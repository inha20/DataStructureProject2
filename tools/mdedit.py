#!/usr/bin/env python3
"""Batch editor for the data-structure markdown books.

Usage: python3 -I tools/mdedit.py BATCH_FILE [--dry]

A batch file is a list of directives; each directive starts with a line
`@@ KIND file :: heading` and its body is every following line up to the next
`@@ ` line.  Headings are written as full lines (`## Kruskal()`,
`# Part 7. 최소 신장 트리`).  Append ` @2` to pick the 2nd heading with the
same text.

KINDs
  CODE     replace the first ```cpp block under the `##` heading (body = bare code)
  SECTION  replace the whole section (heading line included) with the body
  AFTER    insert the body after the section of that heading
  BEFORE   insert the body before that heading line
  DELETE   delete the section of that heading
  RENAME   body = new full heading line
  APPEND   (no heading) append the body to the end of the file
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    raw = Path(path).read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("﻿", "").replace("\r\n", "\n")
    return text.split("\n"), crlf


def save(path, lines, crlf):
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    if crlf:
        text = text.replace("\n", "\r\n")
    Path(path).write_bytes(text.encode("utf-8"))


def level(line):
    m = re.match(r"^(#{1,6}) ", line)
    return len(m.group(1)) if m else 0


def scan(lines):
    """yield (index, line) for lines that are real headings (outside fences)."""
    fence = False
    for i, l in enumerate(lines):
        if l.startswith("```"):
            fence = not fence
            continue
        if not fence and level(l):
            yield i, l


def find(lines, heading):
    occ = 1
    m = re.match(r"^(.*?) @(\d+)$", heading)
    if m:
        heading, occ = m.group(1), int(m.group(2))
    heading = heading.strip()
    n = 0
    for i, l in scan(lines):
        if l.rstrip() == heading:
            n += 1
            if n == occ:
                return i
    raise SystemExit(f"heading not found: {heading!r} (occurrence {occ})")


def section_end(lines, start):
    lv = level(lines[start])
    for i, l in scan(lines):
        if i > start and level(l) <= lv:
            return i
    return len(lines)


def body_lines(body):
    ls = body.split("\n")
    while ls and ls[-1] == "":
        ls.pop()
    return ls


def apply(kind, lines, heading, body):
    b = body_lines(body)
    if kind == "APPEND":
        if lines and lines[-1] == "":
            lines.pop()
        lines += b
    elif kind == "CODE":
        s = find(lines, heading)
        e = section_end(lines, s)
        fence = [i for i in range(s, e) if lines[i].startswith("```")]
        code = ["```cpp"] + b + ["```"]
        if len(fence) >= 2:
            lines[fence[0]:fence[1] + 1] = code
        else:
            lines[s + 1:e] = ["### 대표코드"] + code
    elif kind == "SECTION":
        s = find(lines, heading)
        e = section_end(lines, s)
        lines[s:e] = b
    elif kind == "AFTER":
        s = find(lines, heading)
        e = section_end(lines, s)
        lines[e:e] = b
    elif kind == "BEFORE":
        s = find(lines, heading)
        lines[s:s] = b
    elif kind == "DELETE":
        s = find(lines, heading)
        e = section_end(lines, s)
        del lines[s:e]
    elif kind == "RENAME":
        s = find(lines, heading)
        lines[s] = b[0]
    else:
        raise SystemExit(f"unknown kind {kind}")
    return lines


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    text = Path(args[0]).read_text(encoding="utf-8")
    directives = []
    cur = None
    for l in text.split("\n"):
        if l.startswith("@@ "):
            m = re.match(r"^@@ (\w+)\s+(\S+)(?:\s+::\s+(.*))?$", l.rstrip())
            if not m:
                raise SystemExit(f"bad directive: {l}")
            cur = [m.group(1), m.group(2), (m.group(3) or "").strip(), []]
            directives.append(cur)
        elif cur is not None:
            cur[3].append(l)
    state = {}
    for kind, file, heading, body in directives:
        if file not in state:
            path = ROOT / file
            state[file] = load(path) if path.exists() else ([], True)
        lines, crlf = state[file]
        state[file] = (apply(kind, lines, heading, "\n".join(body)), crlf)
    if not dry:
        for file, (lines, crlf) in state.items():
            save(ROOT / file, lines, crlf)
    print(f"applied {len(directives)} directives to {len(state)} files" + (" (dry)" if dry else ""))


if __name__ == "__main__":
    main()
