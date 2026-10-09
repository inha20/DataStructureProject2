#!/usr/bin/env python3
"""Audit the markdown books: structure, placeholder code, and compile+run checks.

Usage: python3 -I tools/audit.py [modes] [--only REGEX] [--jobs N] [--repeat N] [--time] [--list] [FILE ...]

  (default)      structure + placeholder + thin-block report for every book
  --compile      compile (g++ -std=c++17) and run every ```cpp block, report failures
  --strict       -Wall -Wextra; any warning fails (skip a block with `// audit: allow-warn`)
  --san          AddressSanitizer + UBSan + LeakSanitizer (skip with `// audit: no-sanitize`)
  --tsan         ThreadSanitizer, only for blocks that start threads
  --portable     clang++ -std=c++17 and g++ -std=c++20 -pedantic (skip the latter with `// audit: gcc-only`)
  --all          every mode above
  --repeat N     run thread-using blocks N times (flaky-test hunting)
  --time         list blocks slower than 3 s
  --only         restrict checks to headings matching REGEX
  --stamp        after a clean run over every book, record date and modes in tools/last_audit.json (used by gen_index.py)
  --list         print the names of placeholder-only entries
  --list-thin    print STL-wrapper / concept-only / trivial-assert entries (`// audit: stl-demo` exempts)
  --list-shallow print entries with <= 4 asserts, <= 40 lines and no randomized check
                 (`// audit: exhaustive` exempts programs that enumerate their whole input space)
  --list-weak    print entries with <= 8 asserts and no randomized or oracle-based check at all
                 (exempt with `// audit: exhaustive`, `// audit: known-answer` for published test vectors, or
                 `// audit: stress` for concurrent stress tests whose conservation laws -- every value delivered exactly
                 once, per-producer order, pool fully returned -- are the independent oracle), `// audit: closed-form`
                 when the assertions test a derived formula (measured stack-frame sizes vs array sizes, ...) and
                 `// audit: differential` when the program compares against a second, independently written
                 implementation of the same function whose name does not say so)
"""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
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


POSIX_INC = re.compile(r"#\s*include\s*<(?:sys/[\w./]+|unistd\.h|fcntl\.h|dirent\.h|signal\.h|pthread\.h|semaphore\.h|sched\.h|termios\.h|poll\.h|netinet/[\w.]+|arpa/[\w.]+|netdb\.h|dlfcn\.h|spawn\.h)>")


def unguarded_posix(code):
    """True if a POSIX-only header is included outside any #if/#ifdef/#ifndef region (it would not compile on Windows)."""
    depth = 0
    for line in code.split("\n"):
        s = line.strip()
        if re.match(r"#\s*(if|ifdef|ifndef)\b", s):
            depth += 1
        elif re.match(r"#\s*endif\b", s):
            depth -= 1
        elif depth == 0 and POSIX_INC.match(s):
            return True
    return False


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
    posix = [e["name"] for e in entries if e["code"] and unguarded_posix(e["code"])]
    if posix:
        probs.append(f"{len(posix)} entries include POSIX headers outside an #if guard: {posix[:6]}")
    norep = [e["name"] for e in entries if not e["has_rep"]]
    if norep:
        probs.append(f"{len(norep)} entries without '### 대표코드': {norep[:6]}")
    return probs, entries


MODES = {
    # name: (compiler, flags, run timeout seconds)
    "std":     ("g++",     ["-std=c++17", "-O1", "-w", "-pthread"], 10),
    "strict":  ("g++",     ["-std=c++17", "-O1", "-Wall", "-Wextra", "-Wno-misleading-indentation", "-pthread"], 10),   # dense one-line style: see README
    "san":     ("g++",     ["-std=c++17", "-O1", "-g", "-w", "-pthread", "-fsanitize=address,undefined", "-fno-sanitize-recover=undefined"], 60),
    "tsan":    ("g++",     ["-std=c++17", "-O1", "-g", "-w", "-pthread", "-fsanitize=thread"], 120),
    "clang":   ("clang++", ["-std=c++17", "-O1", "-w", "-pthread"], 20),
    "cxx20":   ("g++",     ["-std=c++20", "-O1", "-pedantic", "-pthread"], 10),
}
SKIP_MARK = {"san": "no-sanitize", "tsan": "no-sanitize"}
THREAD_RE = re.compile(r"std::thread|std::async|std::jthread|<thread>")


def marks(code):
    return set(re.findall(r"//\s*audit:\s*([a-z\-]+)", code))


def applicable(mode, code):
    m = marks(code)
    if mode in SKIP_MARK and SKIP_MARK[mode] in m:
        return False
    if mode == "tsan" and not THREAD_RE.search(code):
        return False
    if mode == "strict" and "allow-warn" in m:
        return False
    if mode == "cxx20" and "gcc-only" in m:
        return False
    return True


def job_key(mode, code, repeat):
    return hashlib.sha1(f"{mode}|{MODES[mode]}|{repeat}|{code}".encode()).hexdigest()


def compile_one(job):
    mode, book, name, code, repeat = job
    key = job_key(mode, code, repeat)
    cc, flags, tmo = MODES[mode]
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "a.cpp"
        exe = Path(d) / "a.out"
        src.write_text(code, encoding="utf-8")
        r = subprocess.run([cc] + flags + [str(src), "-o", str(exe)], capture_output=True, text=True)
        if r.returncode != 0:
            err = next((x for x in r.stderr.splitlines() if "error" in x), r.stderr[:200])
            return key, ("compile", err[-200:], 0.0)
        if mode in ("strict", "cxx20") and "warning:" in r.stderr:
            w = [x for x in r.stderr.splitlines() if "warning:" in x]
            return key, ("warn", f"{len(w)} warning(s): {w[0].split('warning:')[1].strip()[:150]}", 0.0)
        times = []
        n = repeat if THREAD_RE.search(code) and mode in ("std", "san", "tsan") else 1
        env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1:abort_on_error=0", UBSAN_OPTIONS="print_stacktrace=1", TSAN_OPTIONS="halt_on_error=1")
        for _ in range(n):
            t0 = time.time()
            try:
                r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=tmo, env=env)
            except subprocess.TimeoutExpired:
                return key, ("timeout", f">{tmo}s", float(tmo))
            times.append(time.time() - t0)
            if r.returncode != 0:
                err = r.stderr.strip().splitlines()
                head = next((x for x in err if "ERROR" in x or "runtime error" in x or "Assertion" in x or "WARNING" in x), (err[0] if err else f"exit {r.returncode}"))
                return key, ("run", head[-200:], max(times))
            if mode in ("san", "tsan") and ("WARNING: ThreadSanitizer" in r.stderr or "runtime error" in r.stderr):
                head = next(x for x in r.stderr.splitlines() if "WARNING" in x or "runtime error" in x)
                return key, ("run", head[-200:], max(times))
    return key, ("ok", "", max(times))


THIN_WORDS = re.compile(r"concept|Placeholder|개념적|conceptually", re.I)


def thin_reason(code):
    """return a reason string if the block looks like an STL wrapper / toy demo, else None."""
    if code is None or "audit: stl-demo" in code:
        return None
    lines = [l for l in code.split("\n") if l.strip()]
    body = "\n".join(lines)
    nocomm = re.sub(r"//.*", "", body)
    has_def = bool(re.search(r"\b(struct|class)\s+\w+\s*[\{:]", nocomm)) or len(re.findall(
        r"^\s*(?:template\s*<[^>]*>\s*)?(?:static\s+|inline\s+)?[\w:<>,\*&\s]+?\s+\w+\s*\([^;]*\)\s*(?:const\s*)?\{", nocomm, re.M)) > 1
    if THIN_WORDS.search(nocomm + "".join(re.findall(r'"[^"]*"', body))):
        return "concept-only"
    if re.search(r"assert\((true|1\s*==\s*1)\)", body):
        return "trivial-assert"
    if not has_def and len(lines) <= 24:
        return "stl-wrapper"
    return None


def shallow_reason(code):
    if code is None or "audit: stl-demo" in code or "audit: exhaustive" in code:
        return None
    lines = [l for l in code.split("\n") if l.strip()]
    asserts = len(re.findall(r"\bassert\(", code))
    rng = bool(re.search(r"mt19937|rand\(|default_random", code))
    if not rng and asserts <= 4 and len(lines) <= 40:
        return f"{len(lines)} lines, {asserts} asserts, no randomized check"
    return None


def weak_reason(code):
    """stricter second-level depth check: few assertions and nothing that compares against an independent oracle."""
    if code is None or re.search(r"//\s*audit:\s*(stl-demo|exhaustive|known-answer|stress|closed-form|differential)", code):
        return None
    nocomm = re.sub(r"//.*", "", code)
    asserts = len(re.findall(r"\bassert\s*\(", nocomm))
    if asserts <= 8 and not re.search(r"mt19937|rand\s*\(|default_random|next_permutation|[Nn]aive|[Oo]racle|[Bb]rute|[Rr]eference", nocomm):
        return f"{asserts} asserts, no randomized or oracle check"
    return None


def main():
    args = sys.argv[1:]
    do_compile = "--compile" in args
    show_list = "--list" in args
    list_thin = "--list-thin" in args
    list_shallow = "--list-shallow" in args
    list_weak = "--list-weak" in args
    modes = ["std"] if do_compile else []
    if "--strict" in args: modes = ["strict"] + [m for m in modes if m != "strict"]; do_compile = True
    if "--san" in args: modes.append("san"); do_compile = True
    if "--tsan" in args: modes.append("tsan"); do_compile = True
    if "--portable" in args: modes += ["clang", "cxx20"]; do_compile = True
    if "--all" in args: modes = ["std", "strict", "san", "tsan", "clang", "cxx20"]; do_compile = True
    modes = list(dict.fromkeys(modes))
    show_time = "--time" in args
    only = None
    repeat = 1
    jobs = os.cpu_count() or 2
    files = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--only":
            only = re.compile(args[i + 1]); i += 1
        elif a == "--jobs":
            jobs = int(args[i + 1]); i += 1
        elif a == "--repeat":
            repeat = int(args[i + 1]); i += 1
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
    total = {"blocks": 0, "ph": 0, "thin": 0, "shallow": 0, "weak": 0}
    todo = []
    print(f"{'book':26} {'parts':>5} {'entries':>7} {'blocks':>6} {'placeholder':>11} {'thin':>5}  structure")
    for b in books:
        text, nbom, sb = read(ROOT / f"{b}.md")
        probs, entries = structure(b, text, nbom, sb)
        nparts = len({e["part"] for e in entries})
        blocks = [e for e in entries if e["code"] is not None and e.get("lang") != "python"]
        ph = [e for e in blocks if is_placeholder(e["code"])]
        thin = [e for e in blocks if thin_reason(e["code"])]
        shallow = [e for e in blocks if shallow_reason(e["code"])]
        weak = [e for e in blocks if weak_reason(e["code"])]
        total["blocks"] += len(blocks); total["ph"] += len(ph); total["thin"] += len(thin); total["shallow"] += len(shallow); total["weak"] += len(weak)
        print(f"{b:26} {nparts:5} {len(entries):7} {len(blocks):6} {len(ph):6} ({100*len(ph)//max(1,len(blocks)):3}%) {len(thin):5}  "
              + ("OK" if not probs else "; ".join(probs)))
        if show_list and ph:
            print("    placeholders:", ", ".join(e["name"] for e in ph))
        if list_thin and thin:
            print("    thin:", ", ".join(f"{e['name']}[{thin_reason(e['code'])}]" for e in thin))
        if list_shallow and shallow:
            print("    shallow:", ", ".join(e["name"] for e in shallow))
        if list_weak and weak:
            print("    weak:", ", ".join(e["name"] for e in weak))
        if do_compile:
            for e in blocks:
                if only and not only.search(e["name"]):
                    continue
                todo.append((b, e["name"], e["code"]))
    print(f"TOTAL blocks={total['blocks']} placeholders={total['ph']} thin={total['thin']} shallow={total['shallow']} weak={total['weak']}")
    if do_compile:
        bad = False
        for mode in modes:
            sel = [(b, n, c) for b, n, c in todo if applicable(mode, c)]
            pending = [(mode, b, n, c, repeat) for b, n, c in sel if job_key(mode, c, repeat) not in cache]
            with cf.ThreadPoolExecutor(jobs if mode not in ("san", "tsan") else max(1, jobs // 2)) as ex:
                for job, (key, res) in zip(pending, ex.map(compile_one, pending)):
                    cache[key] = list(res)
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(cache))
            fails = []
            slow = []
            for b, name, code in sel:
                res = cache[job_key(mode, code, repeat)]
                st, msg = res[0], res[1]
                if st != "ok":
                    fails.append((b, name, st, msg))
                elif len(res) > 2 and res[2] > 3.0:
                    slow.append((res[2], b, name))
            print(f"[{mode}] checked {len(sel)} of {len(todo)} blocks ({len(pending)} new), failures: {len(fails)}")
            for b, name, st, msg in fails:
                print(f"  FAIL {b}.md :: {name} [{st}] {msg}")
            if show_time and slow:
                for t, b, name in sorted(slow, reverse=True)[:15]:
                    print(f"  SLOW {t:5.1f}s {b}.md :: {name}")
            bad |= bool(fails)
        if "--stamp" in args and not bad and not files and not only:
            import datetime
            (ROOT / "tools" / "last_audit.json").write_text(json.dumps(
                {"date": datetime.date.today().isoformat(), "modes": modes, "blocks": total["blocks"], "failures": 0},
                ensure_ascii=False, indent=2) + "\n")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
