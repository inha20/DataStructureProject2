#!/usr/bin/env python3
"""test_tools.py -- self-tests for the tooling, so that a tool bug cannot silently damage the books.

  python3 -I tools/test_tools.py

Covers mdedit (every directive, CRLF/LF round trip, fenced headings, @N occurrences), audit (parse, placeholder
and thin/shallow heuristics, structure problems), linkcheck/drift/gen_index on a miniature repository built in a
temporary directory, and a read-only sanity check that the real books still satisfy the structural contract.
"""
import contextlib, io, json, os, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit, drift, gen_index, linkcheck, mdedit

BOOK = """# Part 1. First
## Alpha()
### 대표코드
```cpp
#include <cassert>
// ## not a heading inside a fence
int main() { assert(1 + 1 == 2); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Beta()
### 대표코드
```cpp
int main() { return 0; }
```
# Part 2. Second
## Alpha()
### 대표코드
```cpp
int main() { return 0; }
```
"""

class MdeditTests(unittest.TestCase):
    def lines(self): return BOOK.split('\n')
    def test_find_ignores_fenced_headings(self):
        ls = self.lines()
        self.assertEqual(ls[mdedit.find(ls, '## Alpha()')], '## Alpha()')
        with self.assertRaises(SystemExit): mdedit.find(ls, '## not a heading inside a fence')
    def test_occurrence_suffix(self):
        ls = self.lines()
        first, second = mdedit.find(ls, '## Alpha()'), mdedit.find(ls, '## Alpha() @2')
        self.assertLess(first, second)
        self.assertGreater(second, mdedit.find(ls, '# Part 2. Second'))
    def test_code_replaces_only_the_fence(self):
        ls = mdedit.apply('CODE', self.lines(), '## Beta()', 'int main() { return 7; }\n')
        text = '\n'.join(ls)
        self.assertIn('int main() { return 7; }', text); self.assertIn('### 대표코드', text)
        self.assertEqual(text.count('```cpp'), 3)
    def test_code_adds_missing_fence(self):
        ls = ['## X()', 'prose only', '## Y()']
        ls = mdedit.apply('CODE', ls, '## X()', 'int main(){}')
        self.assertEqual(ls, ['## X()', '### 대표코드', '```cpp', 'int main(){}', '```', '## Y()'])
    def test_section_after_before_delete_rename_append(self):
        ls = mdedit.apply('AFTER', self.lines(), '## Beta()', '## Gamma()\n### 대표코드\n```cpp\nint main(){}\n```\n')
        self.assertLess(mdedit.find(ls, '## Beta()'), mdedit.find(ls, '## Gamma()'))
        self.assertLess(mdedit.find(ls, '## Gamma()'), mdedit.find(ls, '# Part 2. Second'))
        ls = mdedit.apply('BEFORE', ls, '## Gamma()', '## Pre()')
        self.assertEqual(ls[mdedit.find(ls, '## Pre()') + 1], '## Gamma()')
        ls = mdedit.apply('DELETE', ls, '## Gamma()', '')
        with self.assertRaises(SystemExit): mdedit.find(ls, '## Gamma()')
        ls = mdedit.apply('RENAME', ls, '## Beta()', '## Beta2()')
        self.assertIn('## Beta2()', ls)
        ls = mdedit.apply('SECTION', ls, '## Beta2()', '## Beta3()\ntext')
        self.assertIn('## Beta3()', ls)
        ls = mdedit.apply('APPEND', ls, '', '# Part 3. Third')
        self.assertEqual(ls[-1], '# Part 3. Third')
    def test_dsl_wraps_code(self):
        out = mdedit.dsl('# Part 9. T\n## F()\nint main(){}\n\n## G()\nint main(){}').split('\n')
        self.assertEqual(out.count('### 대표코드'), 2); self.assertEqual(out.count('```cpp'), 2)
    def test_crlf_round_trip_and_bom(self):
        with tempfile.TemporaryDirectory() as d:
            for crlf in (True, False):
                p = os.path.join(d, 'b.md')
                raw = ('﻿' + BOOK).replace('\n', '\r\n' if crlf else '\n')
                with open(p, 'wb') as fh: fh.write(raw.encode('utf-8'))
                ls, was = mdedit.load(p); self.assertEqual(was, crlf); self.assertNotIn('﻿', '\n'.join(ls))
                mdedit.save(p, ls, was)
                with open(p, 'rb') as fh: back = fh.read().decode('utf-8')
                self.assertEqual('\r\n' in back, crlf); self.assertEqual(back.replace('\r\n', '\n').strip(), BOOK.strip())

class AuditTests(unittest.TestCase):
    def test_parse_and_structure(self):
        entries, _ = audit.parse(BOOK)
        self.assertEqual([e['name'] for e in entries], ['Alpha()', 'Beta()', 'Alpha()'])
        self.assertTrue(all(e['has_rep'] and e['code'] for e in entries))
        probs, _ = audit.structure('T', BOOK, 0, False)
        self.assertTrue(any('duplicate ## headings' in p for p in probs))
        probs, _ = audit.structure('T', '﻿' + BOOK, 2, True)
        self.assertTrue(any('stray BOM' in p for p in probs))
    def test_posix_guard_detection(self):
        self.assertTrue(audit.unguarded_posix('#include <unistd.h>\nint main() {}'))
        self.assertTrue(audit.unguarded_posix('#include <sys/mman.h>\nint main() {}'))
        self.assertFalse(audit.unguarded_posix('#if defined(__linux__)\n#include <unistd.h>\n#endif\nint main() {}'))
        self.assertFalse(audit.unguarded_posix('#ifdef __unix__\n#include <sys/mman.h>\n#else\n#endif\n#include <vector>\nint main() {}'))
        self.assertTrue(audit.unguarded_posix('#if 0\n#endif\n#include <fcntl.h>\nint main() {}'))
        self.assertFalse(audit.unguarded_posix('#include <csignal>\n#include <thread>\nint main() {}'))
    def test_nondeterminism_detection(self):
        self.assertTrue(audit.nondeterministic('std::random_device rd; std::mt19937 g(rd());'))
        self.assertTrue(audit.nondeterministic('srand(time(nullptr));'))
        self.assertTrue(audit.nondeterministic('std::mt19937 g((unsigned)time(NULL));'))
        self.assertFalse(audit.nondeterministic('std::mt19937 g(12345); // not random_device'))
        self.assertFalse(audit.nondeterministic('auto t0 = std::chrono::steady_clock::now();'))
    def test_placeholder_detection(self):
        self.assertTrue(audit.is_placeholder('#include <cassert>\nint main() {\n assert(true);\n return 0;\n}'))
        self.assertFalse(audit.is_placeholder('int main() { assert(1 + 1 == 2); }'))
    def test_thin_and_shallow(self):
        wrapper = '#include <stack>\n#include <cassert>\nint main() {\n std::stack<int> s; s.push(1); assert(s.top() == 1);\n}'
        self.assertEqual(audit.thin_reason(wrapper), 'stl-wrapper')
        self.assertIsNone(audit.thin_reason('// audit: stl-demo\n' + wrapper))
        self.assertIsNotNone(audit.shallow_reason('int main() { assert(1); }'))
        self.assertIsNone(audit.shallow_reason('#include <random>\nint main() { std::mt19937 r(1); assert(r() >= 0); }'))
        self.assertIsNone(audit.shallow_reason('// audit: exhaustive\nint main() { assert(1); }'))
    def test_weak(self):
        thin = '#include <cassert>\nint main() { assert(1); assert(2); }'
        self.assertIsNotNone(audit.weak_reason(thin))
        for mark in ('exhaustive', 'known-answer', 'stress', 'closed-form', 'differential', 'stl-demo'): self.assertIsNone(audit.weak_reason('// audit: ' + mark + '\n' + thin))
        self.assertIsNone(audit.weak_reason('#include <random>\nint main() { std::mt19937 r(1); assert(r() >= 0); }'))
        self.assertIsNone(audit.weak_reason('int naiveSum(){return 0;} int main() { assert(naiveSum() == 0); }'))
        many = 'int main() {' + ' assert(1);' * 9 + ' }'
        self.assertIsNone(audit.weak_reason(many))
    def test_marks(self):
        self.assertEqual(audit.marks('// audit: no-sanitize (why)\n// audit: gcc-only'), {'no-sanitize', 'gcc-only'})
        self.assertFalse(audit.applicable('san', '// audit: no-sanitize\nint main(){}'))
        self.assertTrue(audit.applicable('strict', '// audit: no-sanitize\nint main(){}'))
    def test_host_dependent_mark(self):
        host, plain = '// audit: host-dependent (THP)\nint main(){}', 'int main(){}'
        saved = audit.SKIP_HOST, audit.HOST_ONLY
        try:
            audit.SKIP_HOST, audit.HOST_ONLY = False, False
            self.assertTrue(audit.applicable('strict', host) and audit.applicable('strict', plain))
            audit.SKIP_HOST = True          # the blocking CI job: machine-probing entries are left out
            self.assertFalse(audit.applicable('strict', host)); self.assertTrue(audit.applicable('strict', plain))
            audit.SKIP_HOST, audit.HOST_ONLY = False, True       # `--host`: only those entries
            self.assertTrue(audit.applicable('strict', host)); self.assertFalse(audit.applicable('strict', plain))
        finally: audit.SKIP_HOST, audit.HOST_ONLY = saved
    def test_settle_reruns_only_timeouts_alone(self):
        calls = []
        def run(job): calls.append(job); return 'k2', ('ok', '', 1.5) if job == 'slow' else ('timeout', '>10s', 10.0)
        res = audit.settle(['slow', 'hang', 'fine', 'broken'], [('k1', ('timeout', '>10s', 10.0)), ('k3', ('timeout', '>10s', 10.0)),
                                                                ('k5', ('ok', '', 0.1)), ('k6', ('run', 'Assertion', 0.1))], run)
        self.assertEqual(calls, ['slow', 'hang'])                                       # ok and failed-by-assertion results are not retried
        self.assertEqual(res[0], ('k2', ('ok', '', 1.5, 'alone'))); self.assertEqual(res[1][1][0], 'timeout')
        self.assertEqual(res[2], ('k5', ('ok', '', 0.1))); self.assertEqual(res[3], ('k6', ('run', 'Assertion', 0.1)))
    def test_time_scale_is_part_of_the_cache_key(self):
        saved = audit.TIME_SCALE
        try:
            audit.TIME_SCALE = 1.0; a = audit.job_key('strict', 'int main(){}', 1)
            audit.TIME_SCALE = 3.0; b = audit.job_key('strict', 'int main(){}', 1)
        finally: audit.TIME_SCALE = saved
        self.assertNotEqual(a, b)

def miniature(canon, books):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, 'tools'))
    with open(os.path.join(d, 'tools', 'canonical.json'), 'w', encoding='utf-8') as fh: json.dump(canon, fh)
    for name, text in books.items():
        with open(os.path.join(d, name), 'w', encoding='utf-8', newline='') as fh: fh.write(text)
    return d

def entry(name, body):
    return f'## {name}()\n### 대표코드\n```cpp\n{body}\n```\n'

class RepoToolTests(unittest.TestCase):
    CANON = {'generic': ['Size'], 'homonym': {}, 'variant': {}, 'link': {'Dijkstra': ['A.md', 2]}, 'drift_ok': {}}
    def run_tool(self, root, fn, *argv):
        old_root, old_argv = linkcheck.ROOT, sys.argv
        linkcheck.ROOT = root; gen_index.ROOT = root; sys.argv = ['x'] + list(argv)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf): rc = fn()
        finally:
            linkcheck.ROOT = old_root; gen_index.ROOT = old_root; sys.argv = old_argv
        return rc, buf.getvalue()
    def good_books(self):
        a = '# Part 1. One\n' + entry('Size', 'int main(){}') + '# Part 2. Two\n' + entry('Dijkstra', 'int main(){}\n// Time Complexity: O(E log V)\n// Space Complexity: O(V)')
        b = '# Part 1. One\n' + entry('Dijkstra', '// (요약, 정본은 A.md Part 2)\nint main(){}\n// Time Complexity: O(E log V)\n// Space Complexity: O(V)') + entry('Size', 'int main(){}')
        return {'A.md': a, 'B.md': b}
    def test_linkcheck_accepts_a_consistent_repo(self):
        d = miniature(self.CANON, self.good_books())
        rc, out = self.run_tool(d, linkcheck.main); self.assertEqual(rc, 0, out)
    def test_linkcheck_flags_missing_link_comment_wrong_part_and_unclassified(self):
        books = self.good_books(); books['B.md'] = books['B.md'].replace('정본은 A.md Part 2', '정본은 A.md Part 1')
        rc, out = self.run_tool(miniature(self.CANON, books), linkcheck.main)
        self.assertEqual(rc, 1); self.assertIn('mentions A.md Part [1] but its "Dijkstra" is in Part 2', out)
        books = self.good_books(); books['B.md'] = books['B.md'].replace('// (요약, 정본은 A.md Part 2)\n', '')
        rc, out = self.run_tool(miniature(self.CANON, books), linkcheck.main); self.assertEqual(rc, 1); self.assertIn('missing "정본은 A.md Part 2"', out)
        canon = dict(self.CANON, link={})
        rc, out = self.run_tool(miniature(canon, self.good_books()), linkcheck.main); self.assertEqual(rc, 1); self.assertIn('not classified', out)
        books = self.good_books(); books['B.md'] += '# Part 2. Two\n' + entry('Ghost', '// see C.md Part 9\nint main(){}')
        rc, out = self.run_tool(miniature(self.CANON, books), linkcheck.main); self.assertEqual(rc, 1); self.assertIn('unknown book C.md', out)
    def test_linkcheck_appendix_reference(self):
        books = {'A.md': '# Part 1. One\n# 부록\n' + entry('Essay', 'int main(){}'), 'B.md': '# Part 1. One\n' + entry('Essay', '// 정본은 A.md 부록\nint main(){}')}
        canon = dict(self.CANON, generic=[], link={'Essay': ['A.md', 0]})
        rc, out = self.run_tool(miniature(canon, books), linkcheck.main); self.assertEqual(rc, 0, out)
    def test_drift_reports_and_accepts_reviewed_differences(self):
        books = self.good_books(); books['B.md'] = books['B.md'].replace('O(E log V)', 'O(V^2)')
        old = linkcheck.ROOT
        try:
            d = miniature(self.CANON, books); linkcheck.ROOT = d
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf): rc = drift.main()
            self.assertEqual(rc, 1); self.assertIn('Dijkstra|B.md', buf.getvalue())
            canon = dict(self.CANON, drift_ok={'Dijkstra|B.md': '다른 구현'}); d = miniature(canon, books); linkcheck.ROOT = d
            with contextlib.redirect_stdout(io.StringIO()): rc = drift.main()
            self.assertEqual(rc, 0)
        finally: linkcheck.ROOT = old
    def test_gen_index_check_and_status_block(self):
        d = miniature(self.CANON, self.good_books())
        with open(os.path.join(d, 'README.md'), 'w', encoding='utf-8', newline='') as fh: fh.write('# T\r\n\r\nauthor text\r\n')
        rc, out = self.run_tool(d, gen_index.main, '--check'); self.assertEqual(rc, 1)
        rc, out = self.run_tool(d, gen_index.main); self.assertEqual(rc, 0)
        rc, out = self.run_tool(d, gen_index.main, '--check'); self.assertEqual(rc, 0, out)
        with open(os.path.join(d, 'README.md'), 'rb') as fh: readme = fh.read().decode('utf-8')
        self.assertIn('author text', readme); self.assertIn('<!-- status:begin -->', readme); self.assertNotIn('\n<!--', readme.replace('\r\n', ''))   # CRLF preserved
        with open(os.path.join(d, 'INDEX.md'), encoding='utf-8') as fh: self.assertIn('Dijkstra', fh.read())
        with open(os.path.join(d, 'COMPLEXITY.md'), encoding='utf-8') as fh: self.assertIn('O(E log V)', fh.read())

class RealBooksTests(unittest.TestCase):
    def test_books_parse_without_structural_problems(self):
        for b in audit.BOOKS:
            text, nbom, sb = audit.read(os.path.join(audit.ROOT, b + '.md'))
            probs, entries = audit.structure(b, text, nbom, sb)
            self.assertEqual(probs, [], f'{b}: {probs}'); self.assertGreater(len(entries), 40)

if __name__ == '__main__':
    unittest.main(verbosity=1)
