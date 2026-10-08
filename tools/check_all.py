#!/usr/bin/env python3
"""check_all.py -- the fast, compile-free gate (seconds): run this before every commit.

  python3 -I tools/check_all.py

  1. tools/test_tools.py        the tooling's own tests
  2. audit.py (static)          every book's structure is OK, 0 placeholders, 0 thin, 0 shallow entries
  3. linkcheck.py               cross-references and the duplicate-heading classification
  4. drift.py                   quoted complexity of link-type copies vs their canonical entry
  5. complexity_lint.py         every entry carries Time/Space comments
  6. gen_index.py --check       INDEX.md, COMPLEXITY.md and the README status block are current

Compile/run checks are separate because they take minutes: `python3 -I tools/audit.py --strict` (every PR) and
`--strict --san --tsan --portable` (weekly), see tools/README.md.
"""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def run(label, *argv):
    p = subprocess.run([sys.executable, '-I', os.path.join(HERE, argv[0])] + list(argv[1:]), capture_output=True, text=True)
    ok = p.returncode == 0
    print(f'{"ok  " if ok else "FAIL"} {label}')
    if not ok: print('\n'.join('     ' + l for l in (p.stdout + p.stderr).strip().split('\n')[-15:]))
    return ok, p.stdout

def main():
    results = [run('tools self-tests', 'test_tools.py')[0]]
    ok, out = run('static audit', 'audit.py', '--list-thin', '--list-shallow')
    total = re.search(r'TOTAL blocks=(\d+) placeholders=(\d+) thin=(\d+) shallow=(\d+)', out)
    structure_bad = [l for l in out.split('\n') if re.match(r'^\w+\s+\d+\s+\d+\s+\d+\s+\d+', l) and not l.rstrip().endswith('OK')]
    if not total or total.group(2, 3, 4) != ('0', '0', '0') or structure_bad:
        print('FAIL static audit contract'); print('     ' + (total.group(0) if total else 'no TOTAL line')); [print('     ' + l) for l in structure_bad]
        ok = False
    results.append(ok)
    for label, argv in (('linkcheck', ('linkcheck.py',)), ('drift', ('drift.py',)), ('complexity lint', ('complexity_lint.py',)), ('generated documents', ('gen_index.py', '--check'))):
        results.append(run(label, *argv)[0])
    print('all checks passed' if all(results) else 'SOME CHECKS FAILED')
    return 0 if all(results) else 1

if __name__ == '__main__':
    sys.exit(main())
