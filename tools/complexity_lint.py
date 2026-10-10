#!/usr/bin/env python3
"""complexity_lint.py -- heuristic review aid for the trailing `// Time Complexity:` / `// Space Complexity:` comments.

  python3 -I tools/complexity_lint.py [Book ...] [--all]

It never edits a book.  It prints entries whose quoted bound looks inconsistent with the code that implements the
structure (everything *outside* `main`, which only holds the tests):

  L1 a Time and a Space comment exist and say something (prose such as "해당 없음 (비용 모델)" is fine)
  L2 Time says O(1) but a non-main function contains a loop whose bound is a size/count variable (n, size, len, ...)
  L3 Time never mentions a log/sort/n log n factor although a non-main function calls std::sort / stable_sort / priority_queue / map
  L4 Space says O(1) but a non-main function builds a container or array sized by an input (vector<T>(n), new T[n], resize(n))
  L5 Time says O(n) / O(V+E) only, but a non-main function nests two loops over size-like bounds

A reviewed warning is silenced by listing "File.md|Name|Rule" in `lint_ok` of tools/canonical.json together with a reason.
L1 is mandatory; L2-L5 are heuristics that need a human decision, so by default only L1 fails and
`--advisory` prints the others (and fails on them).  Test scaffolding is excluded from L2-L5: `main` and
top-level helpers named like naive/oracle/check/verify/random/simulate/... are removed before analysis.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linkcheck

SIZE = r'(?:n|N|m|M|size|len|length|count|cnt|k|K|V|E|rows|cols|R|C|nodes|edges|num\w*|\w*_?size\(\)|\w*\.size\(\)|\w*\.length\(\))'

HELPER = re.compile(r'naive|oracle|brute|check|verif|reference|expect|slow|exhaust|enumerat|cert|valid|test|compare|random|gen\w*|dump|print|show|render|simulate|model|bench', re.I)

def strip_main(code):
    """Remove `main` and the top-level helper functions that only exist to test the structure (naive oracles, checkers, ...)."""
    out, i, n = [], 0, len(code)
    sig = re.compile(r'(?m)^[A-Za-z_][\w:<>,\*&\s]*?\b(\w+)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?\{')
    pos = 0
    for m in sig.finditer(code):
        if m.start() < pos: continue
        name = m.group(1)
        if name != 'main' and not HELPER.search(name): continue
        j = m.end() - 1; depth = 0
        for k in range(j, n):
            if code[k] == '{': depth += 1
            elif code[k] == '}':
                depth -= 1
                if depth == 0: break
        out.append(code[pos:m.start()]); pos = k + 1
    out.append(code[pos:])
    return ''.join(out)

def comment_lines(code, kind):
    return [l for l in code.split('\n') if re.match(r'\s*//\s*' + kind + r' Complexity', l)]

def nest_depth(code):
    best = 0
    for m in re.finditer(r'\b(for|while)\s*\(', code):
        pass
    # crude: scan with a stack of brace depths that open loops
    stack, depth, i = [], 0, 0
    for m in re.finditer(r'\b(?:for|while)\s*\(.*?\)\s*(\{)?|\{|\}', code):
        t = m.group(0)
        if t == '{': stack.append(False)
        elif t == '}':
            if stack and stack.pop(): depth -= 1
        else:
            depth += 1; best = max(best, depth)
            if m.group(1): stack.append(True)
            else: depth -= 1        # single-statement loop: counts only for the statement itself
    return best

def lint(e):
    code = e['code']; body = strip_main(code); issues = []
    tl, sl = comment_lines(code, 'Time'), comment_lines(code, 'Space')
    if not tl or not sl:
        issues.append(('L1', 'missing ' + ('Time' if not tl else 'Space') + ' Complexity comment')); return issues
    time_txt = ' '.join(tl); space_txt = ' '.join(sl)
    for kind, txt in (('Time', time_txt), ('Space', space_txt)):
        if len(re.sub(r'.*Complexity:', '', txt).strip()) < 3: issues.append(('L1', kind + ' comment is empty'))
    first_time = re.sub(r'\s', '', time_txt)
    no_log = not re.search(r'log|sort|정렬|ln|lg|α|alpha|힙|heap|map|tree|트리', time_txt, re.I)
    funcs = body
    loop_on_size = re.search(r'\b(?:for|while)\s*\([^)]*[<>!=]=?\s*' + SIZE + r'\b', funcs)
    if re.search(r'Time Complexity:\s*O\(1\)\s*$', time_txt.strip()) and loop_on_size:
        issues.append(('L2', 'Time O(1) but a loop runs to a size-like bound: ' + loop_on_size.group(0)[:60]))
    if no_log and re.search(r'\bstd::(?:stable_)?sort\s*\(|\bpriority_queue\b|\bstd::map\b|\bstd::set\b|\bmultiset\b', funcs) and re.search(r'O\(\s*(?:n|N|V|E|V\s*\+\s*E|n\s*\+\s*m)\s*\)', time_txt):
        issues.append(('L3', 'Time quotes a linear bound without a log factor but code uses sort/heap/ordered container'))
    if re.search(r'Space Complexity:\s*O\(1\)\s*$', space_txt.strip()) and re.search(r'std::vector<[^;>]*>\s*\w*\s*\(\s*' + SIZE + r'\b|\bnew\s+\w+(?:\s*<[^>]*>)?\s*\[\s*' + SIZE + r'\b|\.resize\(\s*' + SIZE + r'\b', funcs):
        issues.append(('L4', 'Space O(1) but a container/array sized by an input is allocated'))
    if re.search(r'Time Complexity:\s*O\(\s*(?:n|N|V|E|V\s*\+\s*E|n\s*\+\s*m)\s*\)\s*$', time_txt.strip()) and nest_depth(funcs) >= 2:
        issues.append(('L5', 'Time quoted linear but loops nest to depth ' + str(nest_depth(funcs))))
    return issues

def main():
    books, parts, entries = linkcheck.load()
    with open(os.path.join(linkcheck.ROOT, 'tools', 'canonical.json'), encoding='utf-8') as fh: canon = json.load(fh)
    ok = canon.get('lint_ok', {})
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    shown = unrev = total = 0
    for e in entries:
        if want and e['file'][:-3] not in want: continue
        if not e['code'].lstrip().startswith(('#', '//', 'using', 'struct', 'class', 'template', 'int', 'static', 'namespace', 'const', 'typedef', 'enum')): continue
        total += 1
        for rule, msg in lint(e):
            key = f'{e["file"]}|{e["name"]}|{rule}'
            if key in ok: continue
            if rule != 'L1' and '--advisory' not in sys.argv: continue
            unrev += 1; print(f'WARN {key}: {msg}')
    print(f'complexity_lint: {total} entries checked, {unrev} unreviewed warning(s)')
    return 1 if unrev and '--report' not in sys.argv else 0

if __name__ == '__main__':
    sys.exit(main())
