#!/usr/bin/env python3
"""where.py NAME... : print every "File.md Part N" in which an entry heading `## NAME()` occurs."""
import re, sys, glob
def index():
    idx = {}
    for f in sorted(glob.glob('*.md')):
        if f in ('README.md', 'NextPhasePlan.md'): continue
        part = None
        for line in open(f, encoding='utf-8-sig', newline='').read().split('\n'):
            line = line.rstrip('\r')
            m = re.match(r'# Part (\d+)\.', line)
            if m: part = int(m.group(1)); continue
            if line.startswith('# '): part = 0; continue
            if line.startswith('## '):
                name = re.sub(r'\(\)$', '', line[3:].strip())
                idx.setdefault(name, []).append((f, part))
    return idx
if __name__ == '__main__':
    idx = index()
    for n in sys.argv[1:]:
        print(f"{n:24}", ', '.join(f"{f} Part {p}" if p else f"{f} 부록" for f, p in idx.get(n, [])) or '-')
