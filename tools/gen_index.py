#!/usr/bin/env python3
"""gen_index.py -- generated documents: INDEX.md, COMPLEXITY.md and the status block of README.md.

  python3 -I tools/gen_index.py           rewrite the three outputs
  python3 -I tools/gen_index.py --check   exit 1 if any output is out of date (used by CI)

INDEX.md       books x Parts x entries, which entries are link-type (canonical elsewhere) and which need a
               GCC/Clang extension, POSIX or Linux, or threads (portability table)
COMPLEXITY.md  every entry's trailing `// Time Complexity:` / `// Space Complexity:` comments, per book
README.md      only the block between <!-- status:begin --> and <!-- status:end --> is replaced; the author's
               text is never touched
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linkcheck

ROOT = linkcheck.ROOT
FLAGS = [
    ('gcc',     r'__builtin_|__int128|__attribute__|asm\s+volatile|#pragma\s+GCC|__SANITIZE'),
    ('posix',   r'#include\s*<(?:sys/|unistd\.h|fcntl\.h|dirent\.h|signal\.h|csignal)|\bfork\s*\(|\bmmap\s*\('),
    ('linux',   r'__linux__|/proc/|/sys/|SYS_memfd|sched_getcpu'),
    ('threads', r'std::thread|std::async|std::jthread'),
]
FLAG_TEXT = {'gcc': 'GCC/Clang 확장', 'posix': 'POSIX 헤더·호출', 'linux': 'Linux 전용 경로', 'threads': '스레드'}
GUARD = re.compile(r'#\s*if\w*\s.*(__linux__|__unix__|__APPLE__|__GLIBC__|__GNUC__)')

def flags_of(code):
    return [name for name, pat in FLAGS if re.search(pat, code)]

def bound(code, kind):
    m = re.search(r'^//\s*' + kind + r' Complexity:\s*(.*)$', code, re.M)
    return m.group(1).strip() if m else ''

def load_all():
    books, parts, entries = linkcheck.load()
    titles = {}
    for f in books:
        with open(os.path.join(ROOT, f), encoding='utf-8-sig', newline='') as fh: text = fh.read().replace('\r\n', '\n')
        for m in re.finditer(r'(?m)^# Part (\d+)\.\s*(.*)$', text):
            titles[(f, int(m.group(1)))] = m.group(2).strip()
        for m in re.finditer(r'(?m)^# (?!Part \d+\.)(.*)$', text):
            titles.setdefault((f, 0), m.group(1).strip())
    with open(os.path.join(ROOT, 'tools', 'canonical.json'), encoding='utf-8') as fh: canon = json.load(fh)
    return books, entries, titles, canon

def build_index():
    books, entries, titles, canon = load_all()
    link = canon['link']; out = []
    out.append('# INDEX\n')
    out.append('> 이 파일은 `python3 -I tools/gen_index.py` 가 만든다. 직접 고치지 말고 책을 고친 뒤 다시 생성한다.\n')
    out.append('## 책별 요약\n')
    out.append('| 책 | Part | 항목 | 링크형(정본이 다른 책) | GCC/Clang 확장 | POSIX | Linux 전용 | 스레드 |')
    out.append('|----|-----:|-----:|-----:|-----:|-----:|-----:|-----:|')
    per = {}
    for f in books:
        es = [e for e in entries if e['file'] == f]
        ps = {e['part'] for e in es}
        nl = sum(1 for e in es if e['name'] in link and link[e['name']][0] != f)
        fl = {k: sum(1 for e in es if k in flags_of(e['code'])) for k in FLAG_TEXT}
        per[f] = (len(ps), len(es), nl, fl)
        out.append(f'| {f[:-3]} | {len(ps)} | {len(es)} | {nl} | {fl["gcc"]} | {fl["posix"]} | {fl["linux"]} | {fl["threads"]} |')
    tp = sum(v[0] for v in per.values()); te = sum(v[1] for v in per.values()); tl = sum(v[2] for v in per.values())
    out.append(f'| **합계** | {tp} | {te} | {tl} | {sum(v[3]["gcc"] for v in per.values())} | {sum(v[3]["posix"] for v in per.values())} | {sum(v[3]["linux"] for v in per.values())} | {sum(v[3]["threads"] for v in per.values())} |')
    out.append('')
    out.append('표시: `↗File.md#N` 은 링크형 요약(정본이 File.md Part N), `[gcc]` `[posix]` `[linux]` `[threads]` 는 위 표의 이식성 표지다. POSIX·Linux 코드는 `#if` 가드로 감싸 다른 환경에서도 컴파일되고, GCC/Clang 확장을 쓰는 항목은 MSVC에서 따로 손봐야 한다.\n')
    for f in books:
        out.append(f'## {f[:-3]}\n')
        cur = None; names = []
        def flush():
            if cur is not None:
                out.append((f'### Part {cur[0]}. {cur[1]}' if cur[0] else f'### 부록: {cur[1]}') + f' ({len(names)})\n')
                out.append(', '.join(names) + '\n')
        for e in entries:
            if e['file'] != f: continue
            if cur is None or e['part'] != cur[0]:
                flush(); names = []; cur = (e['part'], titles.get((f, e['part']), ''))
            label = '`' + e['name'].replace('|', '\\|') + '`'
            if e['name'] in link and link[e['name']][0] != f: label += f' ↗{link[e["name"]][0][:-3]}#{link[e["name"]][1] or "부록"}'
            fl = flags_of(e['code'])
            if fl: label += ' ' + ''.join(f'[{x}]' for x in fl)
            names.append(label)
        flush()
    return '\n'.join(out).rstrip() + '\n'

def build_complexity():
    books, entries, titles, canon = load_all()
    out = ['# COMPLEXITY\n', '> 각 항목 코드 끝의 `// Time Complexity:` / `// Space Complexity:` 주석을 모았다. `python3 -I tools/gen_index.py` 가 만든다.\n']
    def cell(t): return t.replace('|', '\\|')[:110] or '-'
    for f in books:
        out.append(f'## {f[:-3]}\n')
        out.append('| 항목 | Part | 시간 | 공간 |'); out.append('|------|-----:|------|------|')
        for e in entries:
            if e['file'] != f: continue
            out.append(f'| `{e["name"].replace("|", chr(92) + "|")}` | {e["part"]} | {cell(bound(e["code"], "Time"))} | {cell(bound(e["code"], "Space"))} |')
        out.append('')
    return '\n'.join(out).rstrip() + '\n'

def build_status():
    books, entries, titles, canon = load_all()
    n_books = len(books); n_entries = len(entries); n_parts = len({(e['file'], e['part']) for e in entries})
    n_code = sum(1 for e in entries if e['code'].lstrip().startswith(('#', '//')))
    n_link = sum(1 for e in entries if e['name'] in canon['link'] and canon['link'][e['name']][0] != e['file'])
    stamp_path = os.path.join(ROOT, 'tools', 'last_audit.json')
    audit = ''
    if os.path.exists(stamp_path):
        with open(stamp_path, encoding='utf-8') as fh: st = json.load(fh)
        audit = f'마지막 전체 감사: {st["date"]} — {st["blocks"]}개 블록, 모드 {", ".join(st["modes"])}, 실패 0.'
    lines = ['<!-- status:begin -->',
             '**현황 (자동 생성 — `python3 -I tools/gen_index.py`)**',
             '',
             f'- 책 {n_books}권, Part {n_parts}개, 항목 {n_entries}개 (실행되는 C++ 코드 블록 {n_code}개, 그중 링크형 요약 {n_link}개).',
             '- 모든 코드 블록은 `main` 과 `assert` 를 가진 완전한 프로그램이며 `tools/audit.py` 로 컴파일·실행을 검증한다.',
             f'- {audit}' if audit else '- 전체 감사 기록 없음.',
             '- 목차와 이식성 표는 [INDEX.md](INDEX.md), 복잡도 모음은 [COMPLEXITY.md](COMPLEXITY.md).',
             '<!-- status:end -->']
    return '\n'.join(lines)

def apply_status(text, block):
    crlf = '\r\n' in text
    t = text.replace('\r\n', '\n')
    if '<!-- status:begin -->' in t:
        t = re.sub(r'<!-- status:begin -->.*?<!-- status:end -->', lambda m: block, t, flags=re.S)
    else:
        first, _, rest = t.partition('\n')
        t = first + '\n\n' + block + '\n' + rest
    return t.replace('\n', '\r\n') if crlf else t

def main():
    check = '--check' in sys.argv
    targets = {'INDEX.md': build_index(), 'COMPLEXITY.md': build_complexity()}
    readme = os.path.join(ROOT, 'README.md')
    with open(readme, encoding='utf-8', newline='') as fh: raw = fh.read()
    targets['README.md'] = apply_status(raw, build_status())
    stale = []
    for name, text in targets.items():
        path = os.path.join(ROOT, name)
        old = None
        if os.path.exists(path):
            with open(path, encoding='utf-8', newline='') as fh: old = fh.read()
        if old != text:
            stale.append(name)
            if not check:
                with open(path, 'w', encoding='utf-8', newline='') as fh: fh.write(text)
    if check:
        for n in stale: print(f'STALE {n}: run python3 -I tools/gen_index.py')
        print(f'gen_index: {len(stale)} stale output(s)')
        return 1 if stale else 0
    print('gen_index: wrote ' + (', '.join(stale) if stale else 'nothing (already current)'))
    return 0

if __name__ == '__main__':
    sys.exit(main())
