#!/usr/bin/env python3
"""drift.py -- do a canonical entry and its link-type copies still tell the same story?

  python3 -I tools/drift.py [--all]

For every `link` and `variant` concept in tools/canonical.json, compares the asymptotic bounds quoted in the
trailing `// Time Complexity:` / `// Space Complexity:` comments of the canonical entry and of each copy.
The leading O(...) expression of each comment is normalised (spaces, unicode superscripts, log bases) and a pair
is reported when the two normalised expressions differ.  Differences are *not* automatically wrong -- a link-type
summary may quote one operation while the canonical entry quotes another -- so a reviewed difference is recorded in
`drift_ok` of tools/canonical.json as "Name|File.md" and silenced.  Exit status 1 if an unreviewed difference remains.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linkcheck

def bound(code, kind):
    m = re.search(r'^//\s*' + kind + r' Complexity:\s*(.*)$', code, re.M)
    if not m: return None
    text = m.group(1)
    # nested parentheses: take from 'O(' to the matching ')'
    i = text.find('O(')
    if i < 0: return text.strip()
    depth = 0
    for j in range(i + 1, len(text)):
        if text[j] == '(': depth += 1
        elif text[j] == ')':
            depth -= 1
            if depth == 0: return norm(text[i:j + 1])
    return norm(text[i:])

def norm(s):
    s = s.replace(' ', '').replace('·', '').replace('*', '').replace('×', '').lower()
    for a, b in {'²': '^2', '³': '^3', 'log₂': 'log', 'log2': 'log', 'ln': 'log', '√': 'sqrt', 'α': 'alpha'}.items(): s = s.replace(a, b)
    return s

def main():
    books, parts, entries = linkcheck.load()
    with open(os.path.join(linkcheck.ROOT, 'tools', 'canonical.json'), encoding='utf-8') as fh: canon = json.load(fh)
    ok = set(canon.get('drift_ok', []))
    where = {(e['file'], e['name']): e for e in entries}
    byname = {}
    for e in entries: byname.setdefault(e['name'], []).append(e)
    problems, compared = [], 0
    for n, spec in canon['link'].items():
        target = spec[2] if len(spec) > 2 else n
        base = where.get((spec[0], target))
        if not base: continue
        for e in byname.get(n, []):
            if e is base: continue
            compared += 1
            for kind in ('Time', 'Space'):
                a, b = bound(base['code'], kind), bound(e['code'], kind)
                if a is None or b is None or a == b: continue
                key = f'{n}|{e["file"]}'
                if key in ok: continue
                problems.append(f'{n}: {spec[0]} {kind} {a}  vs  {e["file"]} {kind} {b}   [{key}]')
    for p in problems: print('DRIFT', p)
    print(f'drift: compared {compared} pairs, {len(problems)} unreviewed difference(s)')
    return 1 if problems else 0

if __name__ == '__main__':
    sys.exit(main())
