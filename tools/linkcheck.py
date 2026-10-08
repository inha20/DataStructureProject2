#!/usr/bin/env python3
"""linkcheck.py -- cross-reference integrity of the books.

  python3 -I tools/linkcheck.py [--list]

Checks (exit status 1 if any fails):
  1. every `File.md Part N` mentioned in a code block names an existing book and Part; when the mentioning
     entry has a same-named entry in that book, the entry really sits in Part N
  2. every heading that appears in more than one book is classified in tools/canonical.json
     (generic / homonym / variant / link); no heading is classified twice; no classification is stale
  3. link: the canonical entry exists at the stated place, and every other entry with that name carries a
     `정본은 File.md Part N` comment pointing at it (`정본은 File.md 부록` when the canonical entry is in an appendix; Part 0)
  4. variant: every entry names, by `File.md Part N`, each other book that holds the same-named entry
  5. a heading may not repeat inside one book
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('README.md', 'NextPhasePlan.md', 'INDEX.md', 'COMPLEXITY.md')

def load():
    books = sorted(f for f in os.listdir(ROOT) if f.endswith('.md') and f not in SKIP)
    entries, parts = [], {}
    for f in books:
        with open(os.path.join(ROOT, f), encoding='utf-8-sig', newline='') as fh: text = fh.read().replace('\r\n', '\n')
        part = 0; parts[f] = set()
        for chunk in re.split(r'(?m)^(?=# |## )', text):
            m = re.match(r'# Part (\d+)\.', chunk)
            if m: part = int(m.group(1)); parts[f].add(part); continue
            if chunk.startswith('# '): part = 0; parts[f].add(0); continue   # 부록 등 Part 번호가 없는 장 (Part 0)
            if chunk.startswith('## '):
                name = re.sub(r'\(\)$', '', chunk.split('\n')[0][3:].strip())
                cm = re.search(r'```cpp\n(.*?)\n```', chunk, re.S)
                entries.append(dict(file=f, part=part, name=name, code=cm.group(1) if cm else ''))
    return books, parts, entries

def partpat(p):
    return r'Part\s+' + str(p) + r'\b' if p else '부록'

def main():
    books, parts, entries = load()
    with open(os.path.join(ROOT, 'tools', 'canonical.json'), encoding='utf-8') as fh: canon = json.load(fh)
    generic = set(canon['generic']); homonym = canon['homonym']; variant = canon['variant']; link = canon['link']
    errors = []
    byname = {}
    for e in entries: byname.setdefault(e['name'], []).append(e)
    where = {(e['file'], e['name']): e['part'] for e in entries}

    # 5. repeats inside a book
    for n, es in byname.items():
        seen = {}
        for e in es: seen[e['file']] = seen.get(e['file'], 0) + 1
        for f, c in seen.items():
            if c > 1 and n not in generic: errors.append(f'{f}: heading "{n}" appears {c} times')

    # 1. every File.md Part N mention
    ref = re.compile(r'([A-Za-z]+\.md)\s+(?:Part\s+(\d+)|(부록))')
    for e in entries:
        mentioned = {}
        for f, p, app in set(ref.findall(e['code'])):
            p = int(p) if p else 0                                          # 'File.md 부록' 은 Part 0
            if f not in parts: errors.append(f'{e["file"]} Part {e["part"]} {e["name"]}: mentions unknown book {f}'); continue
            if p not in parts[f]: errors.append(f'{e["file"]} Part {e["part"]} {e["name"]}: mentions {f} Part {p}, which does not exist'); continue
            mentioned.setdefault(f, set()).add(p)
        for f, ps in mentioned.items():                                     # same-named entry in the mentioned book: its Part must be among the mentions
            if f != e['file'] and (f, e['name']) in where and where[(f, e['name'])] not in ps and e['name'] not in generic:
                errors.append(f'{e["file"]} Part {e["part"]} {e["name"]}: mentions {f} Part {sorted(ps)} but its "{e["name"]}" is in Part {where[(f, e["name"])]}')

    # 2. classification coverage
    dup = {n for n, es in byname.items() if len({e['file'] for e in es}) > 1}
    cats = [('generic', generic), ('homonym', set(homonym)), ('variant', set(variant)), ('link', set(link))]
    for i in range(len(cats)):
        for j in range(i + 1, len(cats)):
            for n in sorted(cats[i][1] & cats[j][1]): errors.append(f'canonical.json: "{n}" is both {cats[i][0]} and {cats[j][0]}')
    classified = generic | set(homonym) | set(variant) | set(link)
    for n in sorted(dup - classified): errors.append(f'canonical.json: duplicate heading "{n}" ({", ".join(sorted({e["file"] for e in byname[n]}))}) is not classified')
    for n in sorted(classified - dup - set(link)):
        errors.append(f'canonical.json: "{n}" is classified but no longer appears in two books')
    for n in sorted(set(link) - dup):
        # a link target with an alias heading is fine as long as the linking entries exist
        if n not in byname: errors.append(f'canonical.json: link "{n}" matches no entry')

    # 3. link
    for n, spec in sorted(link.items()):
        cfile, cpart = spec[0], spec[1]; target = spec[2] if len(spec) > 2 else n
        if (cfile, target) not in where: errors.append(f'link {n}: canonical entry "{target}" not found in {cfile}'); continue
        if where[(cfile, target)] != cpart: errors.append(f'link {n}: canonical "{target}" is in {cfile} Part {where[(cfile, target)]}, not Part {cpart} (Part 0 = 부록)')
        pat = re.compile(r'정본[은는]?\s+' + re.escape(cfile) + r'\s+' + partpat(cpart))
        for e in byname.get(n, []):
            if e['file'] == cfile and e['name'] == target: continue
            if not pat.search(e['code']): errors.append(f'{e["file"]} Part {e["part"]} {n}: missing "정본은 {cfile} Part {cpart}" comment')

    # 4. variant
    for n, base in sorted(variant.items()):
        es = byname.get(n, [])
        for e in es:
            for o in es:
                if o is e or o['file'] == e['file']: continue
                if not re.search(re.escape(o['file']) + r'\s+' + partpat(o['part']), e['code']):
                    errors.append(f'{e["file"]} Part {e["part"]} {n}: variant does not mention {o["file"]} Part {o["part"]}')

    if '--list' in sys.argv:
        print(f'books={len(books)} entries={len(entries)} duplicated headings={len(dup)} (generic {len(generic)}, homonym {len(homonym)}, variant {len(variant)}, link {len(link)})')
    for m in errors: print('FAIL', m)
    print(f'linkcheck: {len(errors)} problem(s)')
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
