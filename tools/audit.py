#!/usr/bin/env python3
"""Audit the markdown books: structure, placeholder code, and compile+run checks.

Usage: python3 -I tools/audit.py [--compile] [--only REGEX] [--jobs N] [--list] [FILE ...]

  (default)  structure + placeholder report for every book
  --compile  compile (g++ -std=c++17) and run every ```cpp block, report failures
  --only     restrict --compile to headings matching REGEX
  --list     print the names of placeholder-only entries
"""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ["AdvancedDataStructures", "Graph", "Hash", "List", "Memory", "PathFinding",
         "Queue", "Set", "Stack", "String", "Tree"]
CACHE = Path(os.environ.get("AUDIT_CACHE", Path.home() / ".cache" / "ds-audit.json"))


def read(path):
    raw = Path(path).read_bytes().decode("utf-8")
    return raw.replace("\r\n", "\n"), raw.count("﻿"), raw.startswith("﻿")


def parse(text):
    """return list of entries: dict(part, name, line, code) for each ## heading."""
    entries, part, fence, cur = [], None, False, None
    lines = text.replace("﻿", "").split("\n")
    buf = None
    for n, l in enumerate(lines, 1):
        if l.startswith("```"):
            if not fence:
                fence = True
                buf = []
                if cur is not None and l.startswith("```cpp") and cur["code"] is None:
                    cur["_open"] = True
                elif cur is not None and l.startswith("```python"):
                    cur["code"] = "# python"
                    cur["lang"] = "python"
            else:
                fence = False
                if cur is not None and cur.get("_open"):
                    cur["code"] = "\n".join(buf)
                    cur["_open"] = False
                buf = None
            continue
        if fence:
            buf.append(l)
            continue
        if l.startswith("# "):
            part = l[2:].strip()
            cur = None
        elif l.startswith("## "):
            cur = {"part": part, "name": l[3:].strip(), "line": n, "code": None, "has_rep": False}
            entries.append(cur)
        elif l.startswith("### ") and cur is not None:
            if "대표코드" in l:
                cur["has_rep"] = True
    return entries, lines


def is_placeholder(code):
    if code is None:
        return False
    body = [x for x in code.splitlines()
            if x.strip() and not x.strip().startswith(("#include", "//"))]
    return bool(re.search(r"assert\((true|1 == 1)\)", " ".join(body))) and len(body) <= 8


def structure(book, text, nbom, startbom):
    probs = []
    entries, lines = parse(text)
    parts = [l[2:].strip() for l in lines if l.startswith("# ")]
    dup = sorted({p for p in parts if parts.count(p) > 1})
    if dup:
        probs.append(f"duplicate Part headings: {dup}")
    names = [e["name"] for e in entries]
    dn = sorted({n for n in names if names.count(n) > 1})
    if dn:
        probs.append(f"duplicate ## headings: {dn}")
    mid = nbom - (1 if startbom else 0)
    if mid:
        probs.append(f"{mid} stray BOM(s) inside file")
    if re.search(r"[一-鿿]{2,}", text):
        probs.append("CJK ideograph run (possible mojibake)")
    if "�" in text:
        probs.append("U+FFFD replacement character present")
    nocode = [e["name"] for e in entries if e["code"] is None]
    if nocode:
        probs.append(f"{len(nocode)} entries without a cpp block: {nocode[:6]}")
    norep = [e["name"] for e in entries if not e["has_rep"]]
    if norep:
        probs.append(f"{len(norep)} entries without '### 대표코드': {norep[:6]}")
    return probs, entries


def compile_one(job):
    book, name, code = job
    key = hashlib.sha1(code.encode()).hexdigest()
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "a.cpp"
        exe = Path(d) / "a.out"
        src.write_text(code, encoding="utf-8")
        r = subprocess.run(["g++", "-std=c++17", "-O1", "-w", "-pthread", str(src), "-o", str(exe)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            err = next((x for x in r.stderr.splitlines() if "error" in x), r.stderr[:200])
            return key, ("compile", err[-200:])
        try:
            r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            return key, ("timeout", "")
        if r.returncode != 0:
            return key, ("run", (r.stderr or f"exit {r.returncode}")[-200:])
    return key, ("ok", "")


def main():
    args = sys.argv[1:]
    do_compile = "--compile" in args
    show_list = "--list" in args
    only = None
    jobs = os.cpu_count() or 2
    files = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--only":
            only = re.compile(args[i + 1]); i += 1
        elif a == "--jobs":
            jobs = int(args[i + 1]); i += 1
        elif not a.startswith("--"):
            files.append(a.replace(".md", ""))
        i += 1
    books = files or BOOKS
    cache = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text())
        except Exception:
            cache = {}
    total = {"blocks": 0, "ph": 0, "fail": 0}
    todo = []
    print(f"{'book':26} {'parts':>5} {'entries':>7} {'blocks':>6} {'placeholder':>11}  structure")
    for b in books:
        text, nbom, sb = read(ROOT / f"{b}.md")
        probs, entries = structure(b, text, nbom, sb)
        nparts = len({e["part"] for e in entries})
        blocks = [e for e in entries if e["code"] is not None and e.get("lang") != "python"]
        ph = [e for e in blocks if is_placeholder(e["code"])]
        total["blocks"] += len(blocks)
        total["ph"] += len(ph)
        print(f"{b:26} {nparts:5} {len(entries):7} {len(blocks):6} {len(ph):6} ({100*len(ph)//max(1,len(blocks)):3}%)  "
              + ("OK" if not probs else "; ".join(probs)))
        if show_list and ph:
            print("    placeholders:", ", ".join(e["name"] for e in ph))
        if do_compile:
            for e in blocks:
                if only and not only.search(e["name"]):
                    continue
                todo.append((b, e["name"], e["code"]))
    print(f"TOTAL blocks={total['blocks']} placeholders={total['ph']}")
    if do_compile:
        fails = []
        pending = [j for j in todo if hashlib.sha1(j[2].encode()).hexdigest() not in cache]
        with cf.ThreadPoolExecutor(jobs) as ex:
            for job, (key, res) in zip(pending, ex.map(compile_one, pending)):
                cache[key] = list(res)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache))
        for b, name, code in todo:
            st, msg = cache[hashlib.sha1(code.encode()).hexdigest()]
            if st != "ok":
                fails.append((b, name, st, msg))
        print(f"compiled {len(todo)} blocks ({len(pending)} new), failures: {len(fails)}")
        for b, name, st, msg in fails:
            print(f"  FAIL {b}.md :: {name} [{st}] {msg}")
        sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
