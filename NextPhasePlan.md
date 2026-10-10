# Data Structure Project 2: Next Iterations Plan (6차 개정판 · 완료 보고)

이 계획서는 2차 개정판을 **2026-10-08 기준 저장소 실측**(커밋 `2b166e7`)으로 갱신한 것입니다. 2차 개정판의 체크리스트 중 이미 처리된 것은 완료로 옮기고, 이번 점검에서 새로 발견된 문제(파일 손상, 번호 중복, 자리표시 코드 비율)와 추가 후보를 반영했습니다.

표기 규칙: **[실측]** = 파일을 직접 대조해 확인한 사실, **[판단]** = 실측을 바탕으로 한 작성자(AI)의 권고, **[확정]** = 사용자가 답했거나 판단을 위임해 채택된 결정(섹션 3 참조).

> 2026-10-08 4차 개정: 작업 진행 중 실측한 품질 지표를 바탕으로 **Phase E(완성도 향상)** 를 추가했습니다. 진행 현황 스냅샷은 Phase E-0을 보세요.

> 2026-10-08 갱신: 사용자 답변(Set.md 정상본 없음 / 원본 목차 모름 / Phase C는 Tier 2까지 / `process.py`·중복 구현 정책은 작성자 판단 위임)을 반영했습니다.

우선순위: **Phase 0 (손상 복구) → Phase A (누락 복구) → Phase B (자리표시 코드 실구현) → Phase C (추가 후보) → Phase D (품질/문서화) → Phase E (완성도 향상)**

> **2026-10-10 6차 개정 — 이 계획서의 모든 Phase(0 → A → B → C → D → E)가 끝났다.** 아래 "🏁 최종 상태"가 증거와 함께 현재 상태를 요약한다. 그 뒤의 섹션 1~3과 Phase별 상세는 작업 당시의 계획·실측을 **이력으로 보존**한 것이라 수치가 현재와 다를 수 있고, 체크박스는 완료 여부를 반영해 갱신했다.

---

## 🏁 최종 상태 (2026-10-10) [실측]

### 한눈에
| 지표 | 값 | 확인 방법 |
|------|----|-----------|
| 책 / Part / 항목 | 11권 / 167개 / 1015개 | `README.md` 현황 블록 (`tools/gen_index.py` 가 생성) |
| 실행되는 C++ 코드 블록 | 1014개 (그중 링크형 요약 85개) | `tools/audit.py` |
| 자리표시 · STL 래퍼 · 얕은 항목 · 약한 항목 | 0 · 0 · 0 · 0 | `python3 -I tools/audit.py --list-thin --list-shallow --list-weak` |
| 전체 감사 | 2026-10-10 — 1014개 블록, 모드 strict, san, tsan, clang, cxx20, **실패 0** | `python3 -I tools/audit.py --strict --san --tsan --portable --stamp` → `tools/last_audit.json` |
| 스레드 블록 반복 검사 | 3회 반복 통과 (타이밍 의존 단언 제거) | `--repeat 3` |
| 빠른 관문 | 통과 (도구 자체 테스트 23개, 구조·링크·복잡도 표기·드리프트·생성 문서) | `python3 -I tools/check_all.py` |
| 시각화(ASCII 그림 + 골든 단언) | 45개 항목 추가 (Tree 11, Graph 10, List 5, Stack 2, Queue 3, PathFinding 5, Set 5, Memory 3, ADS 1) 외에 Hash·String·Tree 의 기존 그림 | E-9 |
| Tier 3 추가 후보 | 30개 항목 (요약표 11행 전부) | E-10 |

### Phase별 결과
| Phase | 결과 |
|-------|------|
| 0 손상 복구 | Set.md 한글 재작성, Tree BOM 제거, Graph·Hash·Memory 의 Part 번호 정리, `process.py` → `archive/` (실행 차단) |
| A 누락 복구 | Hash Part 2~15, String Part 2~17, Graph Part 14~16, Tree·Memory 누락 항목 전부 |
| B 자리표시 실구현 | 시작 시점의 자리표시 약 420개 → **0개**. 모든 항목이 `main`·`assert` 를 가진 완전한 프로그램 |
| C 추가 후보 | Tier 1·Tier 2 전부 존재 확인 (아래 한계 1: Soft Heap 만 의도적으로 제외), Dancing Links 포함 |
| D 품질·문서 | 복잡도 표기 점검(`complexity_lint.py`), 정본/링크형 요약 점검(`linkcheck.py`, `drift.py`), `INDEX.md`·`COMPLEXITY.md`·README 현황 자동 생성, `audit_result.txt` 폐기 |
| E-1 위생 | `-Wall -Wextra` 경고 0, ASan/UBSan/LSan/TSan 통과 (의도적 메모리 실험은 `// audit: no-sanitize` 표식으로 공개) |
| E-2 깊이 | 래퍼·얕은·약한 항목을 직접 구현 + 차분/불변식 검사로 교체 (`--list-thin`, `--list-shallow`, `--list-weak` 모두 0) |
| E-3 이식성 | `clang++ -std=c++17` 와 `g++ -std=c++20 -pedantic` 통과, 이식성 표(INDEX), POSIX 헤더는 `#if` 가드 밖에 없음을 `audit.py` 가 검사 |
| E-4 결정성 | 난수는 전부 고정 시드(`random_device`·시각 시드 사용을 `audit.py` 가 거부), 단언은 시간이 아니라 횟수·불변식 |
| E-5~E-8, E-11 도구·CI | `.github/workflows/audit.yml`(빠른 관문 · 컴파일 · 호스트 의존 항목 별도 작업 · 주간 심층 검사; 푸시당 실행 1회, 아래 "CI 실패 메일 폭주" 참조), 도구 자체 테스트, 링크·드리프트·복잡도 린트, 생성 문서, `.gitignore`·`tools/README.md` |
| E-9 시각화 | 위 표 참조 (Mermaid 는 만들지 않기로 한 방침 유지: 해설 본문은 사람이 쓴다) |
| E-10 Tier 3 | HAMT, RRBVector, BitmapIndex, MisraGries, SpaceSaving, CountSketch, ReservoirSampling, DCEL, QuadEdge, DisjointSparseTable, SqrtTree, CSBPlusTree, BwTree, Masstree, MerklePatriciaTrie, ChaseLevDeque, Disruptor, RCU, Seqlock, EpochBasedReclamation (이상 ADS), TimingWheel, CalendarQueue, RadixHeap (Queue), DialAlgorithm (Graph), SkewHeap, IntervalHeap, LoserTree, EulerTourTree (Tree), BiMap (Hash), Multiset (Set) |
| E-12 인수 검사 | 전체 감사 통과 · 빠른 관문 통과 · 생성 문서 최신 · 책별 15개 무작위 표본(고정 시드)의 독립 검토와 그 지적의 수정(아래 "독립 검토 결과") · 한계 공개 |

### CI 실패 메일 폭주 — 원인과 조치 (2026-10-09)
**증상**: 푸시할 때마다 실패 메일이 두 통씩, 하루에 수십 통.
**원인** (GitHub Actions 기록 50회 실행 전부 실패로 확인):
1. **이중 실행** — `on: push` 와 `on: pull_request` 가 함께 켜져 있어 열린 PR(#1)이 있는 브랜치에 푸시하면 같은 커밋에 실행이 두 번 돌고 메일도 두 통이었다.
2. **실패 자체** — 초기(실행 21~36)는 `fast` 가 오래된 생성 문서(INDEX/COMPLEXITY)를 잡아 12초 만에 실패, 이후(실행 37~50)는 `compile` 이 Memory.md 의 5개 항목(DataSegment, StackOverflow, PageFault, MemoryMapping, MemoryProtection)에서 실패했다. 이들은 THP·코어 덤프 도우미·스택 한도 처리 같은 **호스트 커널 설정을 직접 재서** 작업 환경에서는 통과해도 러너에서 깨졌다. 부하가 큰 2코어에서는 락스텝 스레드 시험 몇 개(MemoryBarrier, SequentialConsistency, LockFreeQueue 등)가 시간 초과했고, TransactionalMemory 는 "충돌이 한 번이라도 났다"(`aborts > 0`)는 스케줄링 의존 단언 때문에 실패할 수 있었다.
**조치**:
- 워크플로: 푸시당 실행 1회(`pull_request` 는 포크 PR 만), 같은 브랜치의 이전 실행 취소, 작업별 `timeout-minutes`, 최소 권한(`contents: read`).
- 호스트 의존 5개 항목: THP 끄기(`madvise(MADV_NOHUGEPAGE)`), 일부러 죽는 자식의 코어 덤프 차단(`RLIMIT_CORE`·`PR_SET_DUMPABLE`), 스택 시험은 부모가 깊이 재귀하기 전에 자식을 만들도록 순서 변경, 실패 시 실측값을 stderr 로 보고. `// audit: host-dependent` 표지로 막는 `compile` 작업에서는 빼고(`AUDIT_SKIP_HOST=1`), 막지 않는 `host` 작업(`continue-on-error`)이 러너 환경 보고와 함께 따로 돌린다.
- 스케줄링에 기대던 단언 제거: TransactionalMemory 는 두 스레드가 같은 계좌를 읽은 뒤에야 쓰게 하는 핸드셰이크로 충돌을 결정적으로 만들었다. 락스텝 시험의 판 수를 줄였다(보장 검사 `== 0` 의 검증력은 판 수와 무관).
- 느린 러너 대비: `AUDIT_TIME_SCALE=3`(캐시 키에 포함), 병렬 실행 중 시간 초과한 블록은 혼자 한 번 더 실행(`settle`, 결과에 `NOTE` 표시), 가장 무거운 세 항목(BST vs AVL vs Red-Black, EppsteinAlgorithm, DistributedHashTable)의 부하 감축(6.7 s/5.6 s/4.6 s → 1 s 안팎).
- 재현·검증: 2코어(`taskset -c 0,1`) + THP=always + 병렬 4 에서 전체 `--strict` 통과(실패 0, 재시도 필요 0).

### 독립 검토 결과 (E-12, 2026-10-09~10)
11권 × 15개 = **165개 항목**을 무작위(시드 20261009)로 뽑아, 코드를 쓰지 않은 독립 검토자가 각 항목을 (1) 정말 그 자료구조·알고리즘인지, (2) 단언이 틀린 구현을 잡는지 — 구현의 핵심 줄을 일부러 망가뜨린 **변이 시험 약 1,000회**로, (3) 주석·출력·복잡도 주장이 코드가 실제로 하는 일과 맞는지 점검했다. 변이가 살아남으면 약한 시험으로 보고했다.
- **결과**: 항목의 약 85%에서 지적이 나왔다. 대부분은 *약한 오라클*(변이가 살아남음)과 *코드보다 센 주장*이었다. 모두 고쳤고, 새·강화한 단언마다 해당 줄을 다시 망가뜨려 실패하는지 확인했다.
- **실제 버그 7건** (표본 안에서 발견): ConflictBasedSearch(도달 불가 목표에서 미정의 동작), NavigationMesh(`visible()` 이 막힌 외곽선을 따라가는 선분을 허용), Palindrome(`#` 구분자가 입력에 있으면 오답), FiniteAutomaton(빈 패턴 미처리), OpenAddressing(`ShiftTable::erase` 가 가득 찬 표에서 종료하지 않음), Union(`unionMany` 값 전달로 O(k·N)), StackFrame(g++ -O3 에서 클론 때문에 실패).
- **거짓·과장 주장 바로잡음**: 복잡도(CoverTree, GreedyBestFirstSearch, CSR 구성, SuccinctTrie 의 "succinct"), 수치("5000개 질의" → 110개, "수백 배" → 68배, 10^6 → 8·10^5), 모델링 범위(Redis 딕셔너리는 특정 버전의 정책, Java HashMap 의 untreeify 규칙, WAVL 트리는 삽입만이라 AVL 과 같았음 → 삭제를 구현해 std::set 과 대조, CHERI 항목은 태그 무결성만 모델링).
- **같은 유형의 구조적 결함**: `assert(...)` 안의 부작용 호출 — `-DNDEBUG` 로 빌드하면 시험이 사라지거나 멈춘다. Stack·Queue 의 해당 항목을 모두 고쳤다(표본 밖에도 남은 곳은 아래 한계).
- 표본 밖 항목에는 같은 검토를 하지 않았다. 표본에서 나온 결함 유형(약한 오라클, 센 주장)이 다른 항목에도 있을 수 있다.

### 알려진 한계 (정직한 기록)
1. **Soft Heap 은 의도적으로 제외**했다. ε-손상(corruption) 보장을 구현하고 단언으로 검증하기 어려워, 검증되지 않은 주장을 쓰느니 넣지 않기로 했다.
2. **단순화한 구현**은 코드 머리 주석에 밝혀 두었다. 주요한 것: `TangoTree`(보조 트리를 레드-블랙이 아니라 트립으로 만들어 최악이 아니라 기대 O(log log N), 키 집합은 정적), `FusionTree`(스케치 추출을 곱셈 요령 대신 비트 루프로), `BwTree`(내부 노드는 뿌리 한 층, 해제는 에포크 회수 대신 종료 시 일괄), `Masstree`(층 인덱스를 `std::map` 으로, 동시성 제어 생략), `RRBVector`(이음매만 다시 포장 — 탐색 단계 불변식 미적용), `CSBPlusTree`(게으른 삭제, 잎 연결 없음), `MerklePatriciaTrie`(RLP/Keccak 이 아니라 자체 직렬화 + SHA-256, 노드 인라인 없음), `GPU*`·`RDMA`·`NUMAMemory` 류(CPU 에서의 시뮬레이션·모델), PathFinding 의 네트워크 라우팅(OSPF·RIP·BGP)은 축약 시뮬레이션.
3. **검증의 성격**: 단언은 표준 라이브러리·완전 탐색·독립 구현과의 차분 검사와 불변식이며 형식 증명이 아니다. 동시성 항목은 스케줄링에 따라 횟수가 달라지므로 보존 법칙(모든 작업이 정확히 한 번)만 단언하고, 변이(mutation) 시험으로 단언이 실제로 잘못된 구현을 잡는지 일부 확인했다(RCU 의 `synchronize` 제거 → use-after-free, Seqlock 의 재검증 제거 → 찢어진 읽기, EBR 의 시대 검사 제거 → use-after-free, Chase–Lev 의 CAS 제거 → 중복 실행, Disruptor 의 gating 제거 → 소비자 정지).
4. **이식성**: GCC/Clang 가정(`__builtin_*` 등은 INDEX 의 `[gcc]` 표지). **MSVC 는 지원하지 않는다** (Windows 는 MinGW-w64 또는 WSL). 일부 Memory 항목은 Linux 전용 경로(`/proc`)를 `#if` 로 가드했다.
5. **사람의 몫으로 남긴 것**: `###` 해설 본문, README 가 말한 파이썬 대응 코드, `LICENSE`, ADS 의 영어/한글 Part 제목 혼용(현상 유지), 원본 목차가 발견될 경우의 Part 구성 조정.
6. 커밋 `a65ea38` 의 메시지는 Tier 3 항목 수를 33개로 적었으나 실제는 30개다.
7. **표본 검토의 범위**: 독립 검토는 책별 15개(전체의 약 16%)뿐이다. Queue 에서는 표본 밖 `assert` 부작용이 약 60곳(21개 항목) 남아 있다 — `-DNDEBUG` 에서도 종료 코드 0 이지만 시험이 빠진다. 같은 검토를 나머지 항목에도 돌리는 것이 다음 단계다.
8. **호스트 의존 항목 5개**(Memory.md: DataSegment, StackOverflow, PageFault, MemoryMapping, MemoryProtection)는 실행 환경의 커널 설정에 따라 결과가 달라질 수 있어 CI 의 막는 작업에서 제외했다. 작업 환경(THP 끔/켬, 2코어 부하)에서는 모두 통과하며 `host` 작업이 러너에서의 결과를 따로 보고한다.

### 재현 방법
```
python3 -I tools/check_all.py                                          # 몇 초: 구조·링크·복잡도·생성 문서·도구 테스트
python3 -I tools/audit.py --strict --san --tsan --portable --stamp     # 전체 컴파일·실행 검증 (캐시가 있으면 변경분만)
python3 -I tools/audit.py --strict --repeat 3                          # 스레드 블록 반복(간헐 실패 탐지)
```

---

---

## 0. 점검 방법과 한계

- 방법: `audit_result.txt`(117개 항목)와 2차 계획서의 항목을 현재 파일의 `##` 헤딩과 대조, 코드 블록의 자리표시 여부 집계, 저장소 전체 문자열 검색.
- 자리표시 코드의 기준: `assert(true)` 또는 `assert(1 == 1)`와 출력문만 있고 실행 로직이 없는 ` ```cpp ` 블록(코드 8줄 이하).
- 한계 1: 원본 목차 `*(2).md`는 저장소에 없고 사용자도 내용을 기억하지 못합니다. "원래 있어야 했던 항목"은 `audit_result.txt`와 2차 계획서에 적힌 것까지만 확인할 수 있으며, 그 밖의 Part 구성은 이 계획서의 제안 목차를 작업 기준으로 삼습니다.
- 한계 2: 사용자 로컬 폴더 `DataStructureProject2-main`은 비교하지 못했습니다(클라우드 세션에서 접근 불가). Set.md 정상본도 없는 것으로 확인됐습니다.
- 한계 3: 코드가 실제로 컴파일·실행되는지는 확인하지 않았습니다(Phase D-3에서 다룸). → 이후 `tools/audit.py` 로 해소됨(최종 상태 참조).

---

## 1. 전체 파일 현황 [실측, 2026-10-08 시점 — 이력]

| 파일 | 현재 Part | 코드 블록 | 자리표시 코드 | 상태 | 긴급도 |
|------|-----------|-----------|---------------|------|--------|
| Set.md | 1~16 + 부록 | 102 | 59 (57%) | 🔴 **한글 전체 깨짐**, 헤딩 병합 | 🚨 최우선 |
| Hash.md | 1, 16, 16(중복) | 19 | 19 (100%) | 🔴 Part 2~15 전체 없음 | 🚨 최우선 |
| String.md | 1 | 14 | 14 (100%) | 🔴 Part 2~17 전체 없음 | 🚨 최우선 |
| Graph.md | 1~15 (+ "(보완)" 중복 블록) | 78 | 15 (19%) | 🔴 Part 14·15 일부, Part 16 없음, 번호 중복 | 높음 |
| Memory.md | 1,2,4,7~16 | 104 | 104 (100%) | ⚠️ Part 3·5·6 결번, 전부 자리표시 | 높음 |
| Tree.md | 1~16 + 부록 | 91 | 38 (41%) | ⚠️ 항목 일부 누락, BOM 2곳 | 중간 |
| PathFinding.md | 1~16 + 부록 | 102 | 89 (87%) | ⚠️ 헤딩은 완비, 내용은 자리표시 | 중간 |
| AdvancedDataStructures.md | 1~15 + 부록 | 112 | 110 (98%) | ⚠️ 헤딩은 완비, 내용은 자리표시 | 중간 |
| List.md | 1~10 + 부록 | 78 | 22 (28%) | ✅ 양호 | 낮음 |
| Queue.md | 1~11 | 53 | 4 (7%) | ✅ 양호 | 낮음 |
| Stack.md | 1~10 | 50 | 0 (0%) | ✅ 양호 | 낮음 |

---

## 2. 2차 계획서 대비 변경 사항 [실측]

### 완료 처리 (2차 계획서의 미완료 항목 중 현재 존재 확인)
- **Graph.md**: Part 5(`DetectCycleDFS/BFS/UnionFind`, `IsTree`, `IsForest`, `IsBiconnected`), Part 7 보완(`Boruvka`, `ReverseDelete`), Part 8 보완(`PathCompression`), Part 9 보완(`Johnson`, `SPFA`), Part 10 보완 5개, Part 11 전체 5개, Part 12 전체 4개, Part 13 보완 5개, 부록 일부(`BFS vs DFS`, `Prim vs Kruskal`)
- **Tree.md**: Part 6 AVL(`AVLDelete`, `BalanceFactor`, 회전 4종), Part 7 `RBInsert/RBDelete/FixViolation`, Part 9 `TrieDelete/RadixTree`, Part 10 `SuffixTree/PatriciaTrie`, Part 11~16 전 항목
- **Hash.md**: Part 16의 10개 항목 헤딩(단, 아래 Phase 0-3의 번호 중복 및 내용 문제 있음)
- **Set.md**: `union() (Python Style)` 항목 (A-4 종료)
- **Memory.md / PathFinding.md / AdvancedDataStructures.md**: 2차 계획서 B-3~B-5에 적힌 함수는 `MemoryPool`, `CompareAndSwap`, `MemoryBarrier`를 제외하고 모두 헤딩이 존재함 (내용은 자리표시)

### 무효화
- **C-1 중복 항목 제거**(Hash `Kademlia` ×2 등, String `StringLiteral`/`Detokenize` ×2): 해당 Part 자체가 사라져 현재 파일에는 중복이 없음. **재작성할 때 다시 생기지 않도록 주의.**

### 여전히 유효 / 새로 확인
- 아래 Phase 0, A, B의 항목들. 특히 `audit_result.txt`는 이미 오래된 스냅샷이므로 **더 이상 기준으로 쓰지 않음** (Phase D-3에서 스크립트로 대체).

---

## 3. 확정된 결정과 정책 (2026-10-08) [확정]

### 사용자 답변과 반영
| # | 질문 | 답변 | 반영 |
|---|------|------|------|
| 1 | Set.md 정상본 | 없음 | Phase 0-1에서 한글을 **재작성**. ASCII 메서드명·코드는 보존하고, Part 제목은 깨진 문자열을 역변환해 복원 |
| 2 | 원본 목차 | 모름 | A-3, A-4, A-5의 제안 목차를 **작업 기준으로 확정**. 원본을 나중에 찾으면 그때 조정 |
| 3 | Phase C 범위 | Tier 2까지 | Tier 1 + Tier 2 모두 채택. 넣을 위치는 Phase C 표에 확정 |
| 4 | `process.py` 처리 | 작성자 판단 위임 | `archive/process.py`로 이동하고 실행 차단 (아래 근거, 적용 완료) |
| 5 | 중복 구현 정책 | 작성자 판단 위임 | 아래 "중복 구현 정책" 채택 |

### `process.py` 결정 근거 [판단 → 확정]
- 삭제하지 않는 이유: README의 "특색"을 자동 정리한 방법이 남는 유일한 기록이고, 보관에 비용이 들지 않음.
- 루트에 두지 않는 이유: 현재 파일에 재실행하면 모든 줄이 `##` 헤딩 + 빈 코드 블록으로 감싸져 파일이 파손됨.
- 조치: `archive/process.py`로 이동하고 파일 맨 앞에 `raise SystemExit`를 넣어 실수로 실행되지 않게 함.

### 중복 구현 정책 [판단 → 확정]
**근거 [실측]**: 헤딩 이름이 둘 이상의 파일에 나오는 경우가 76개. 그중 `Clear`, `Size`, `IsEmpty`, `PushFront` 같은 일반 연산 16개는 자료구조마다 고유한 연산이라 제외하고, 나머지 **60개가 정책 대상**. 이 60개 중 11개는 이미 양쪽 모두 실구현이 있음(`Dijkstra`, `BellmanFord`, `FloydWarshall`, `BreadthFirstSearch`, `DepthFirstSearch`, `IterativeDFS`, `MakeSet`, `FindSet`, `EulerTour`, `SegmentTree`, `FenwickTree`).

**규칙**
1. 한 개념의 **정본(canonical)은 한 파일**. 이미 실구현이 있는 쪽이 정본이고, 양쪽 모두 자리표시면 개념의 본적지 파일이 정본(원리 → Graph/Tree/Set 등, 응용 → PathFinding/Memory 등, ADS는 ADS 고유 주제만).
2. 비정본 항목은 **삭제하지 않는다.** README 확장계획상 파일 하나가 책 한 권이 되므로 각 파일이 독립적으로 읽혀야 하기 때문(링크만 두면 종이책에서 끊김). 비정본 항목 = 요약 3~5줄 + 정본 구현을 쓰는 15줄 이내 대표코드(README의 `### 대표코드` 규칙 유지) + `→ 정본: X.md Part N`.
3. 이미 양쪽 모두 실구현인 11개는 이번 라운드에서 **병합·삭제하지 않고** 정본만 지정해 상호 링크. 코드가 서로 어긋나는지는 Phase D-3 스크립트로 점검.
4. 신규 작성(Phase A, C)은 항목을 추가하기 전에 아래 표에서 정본 위치를 확인.

| 개념 | 정본 | 링크형 요약을 두는 곳 |
|------|------|----------------------|
| Union-Find (`MakeSet/FindSet/UnionSet/UnionByRank/PathCompression/ConnectedComponents`) | Graph.md Part 8 | Set.md Part 7 |
| 일반 탐색·최단 경로 (`BFS/DFS/IterativeDFS/Dijkstra/BellmanFord/FloydWarshall/SPFA/Johnson/BidirectionalSearch/IDDFS/IDAStar`) | Graph.md Part 3, 9, 10 | PathFinding.md Part 2~4, Stack.md, Queue.md |
| 휴리스틱 탐색 (`AStar/JumpPointSearch/ThetaStar/GreedyBestFirstSearch`) | PathFinding.md Part 4~5 | Graph.md Part 10 |
| 미로·다중 시작점 (`MazeSolver`, `MultiSourceBFS`) | Stack.md Part 5 / Queue.md Part 6 (실구현 있음) | PathFinding.md |
| 트리 순회·분해 (`EulerTour/HeavyLightDecomposition/CentroidDecomposition`) | Tree.md Part 3, 15 | Graph.md Part 13 |
| 힙 (`Heapify/BuildHeap/HeapSort/PushHeap/PopHeap`) | Queue.md Part 5 | Tree.md Part 8 |
| 구간·공간 트리 (`SegmentTree/FenwickTree/IntervalTree/LazyPropagation/KDTree/QuadTree/Octree/RTree`) | Tree.md Part 11~12, 16 | AdvancedDataStructures.md Part 5~6 |
| 균형·고급 트리 (`BPlusTree/SplayTree/Treap/ScapegoatTree/VanEmdeBoasTree/RadixTree/PatriciaTrie/MerkleTree`) | Tree.md Part 9~10, 13, 16 | AdvancedDataStructures.md Part 7~8, 10, 14~15 |
| 문자열 편집 구조 (`Rope/GapBuffer/PieceTable`) | String.md Part 4 (신규) | List.md Part 10, AdvancedDataStructures.md Part 4, Tree.md `RopeTree` |
| 접미사 계열 (`SuffixArray/SuffixAutomaton/FMIndex`) | String.md Part 9 | Tree.md Part 10, AdvancedDataStructures.md Part 2·4·15 (`SuffixTree/SuffixTrie/Trie`는 Tree.md가 정본) |
| `SkipList/SkipListSet` | List.md Part 10 | AdvancedDataStructures.md Part 9·13, Set.md Part 15 |
| `FingerTree`, 영속·불변 구조 (`PersistentList/PersistentQueue/ImmutableX`) | AdvancedDataStructures.md Part 1·4 (`PersistentStack`은 실구현 있는 Stack.md) | List.md, Queue.md, Tree.md |
| 확률적 필터 (`BloomFilter/CountingBloomFilter/CuckooFilter/QuotientFilter`) | AdvancedDataStructures.md Part 3 | Set.md Part 14, Hash.md Part 13 |
| `MinHash/LocalitySensitiveHashing` | Hash.md Part 14 | Set.md Part 12 |
| 분산 해시 (`ConsistentHashing/Chord/Kademlia`) | Hash.md Part 7 | AdvancedDataStructures.md Part 10 |
| 무잠금 구조 (`LockFreeQueue/LockFreeStack`) | Queue.md Part 10 / Stack.md Part 9 (실구현 있음) | AdvancedDataStructures.md Part 9 |
| 할당기·페이지 테이블 (`BuddyAllocator/SlabAllocator/PageTable`) | Memory.md | AdvancedDataStructures.md Part 14 |
| `StackFrame/StackOverflow` | Stack.md Part 8·10 (실구현 있음) | Memory.md Part 2 |

---

## 🧯 Phase 0: 손상 복구 (신규, 최우선)

내용을 더 쓰기 전에 현재 파일이 읽히고 렌더링되는 상태부터 만듭니다.

### 0-1. Set.md 한글 인코딩 복구 [실측]
- 증상: `Part 1. 吏묓빀??湲곗큹`처럼 한글 UTF-8 바이트가 CP949로 잘못 해석된 상태로 다시 저장됨. 일부 글자는 `?`로 치환되어 **파일만으로는 복원 불가**.
- 부가 증상:
  - `### 대표코드`가 ` ```cpp `와 한 줄로 붙음 (코드 블록 파손)
  - Part 8, 12, 13, 부록 헤딩이 뒤의 `## ...` 헤딩과 한 줄로 병합됨 (`Combination()`, `InvertedIndex()`, `LabelSet()`, `Set vs List`)
  - Python `union()` 설명 두 줄이 `#`(Part 헤딩)로 처리됨
  - `##` 헤딩 중 한글 제목이 깨진 항목 9개 (`BitSet은 언제 사용하는가?` 류의 부록 해설 등), 그 외 Part 제목 16개도 깨짐
  - 코드 블록 안의 한글 주석도 깨짐 (예: `// C++ ?쒖? ?댁떆 湲곕컲 吏묓빀`)
- **정상본 없음 [확정]** → 재작성한다.
- [x] ASCII 메서드명과 코드 로직은 그대로 보존하고, 한글 Part 제목·부록 제목·코드 주석·설명만 재작성
- [x] Part 제목은 깨진 문자열을 역변환(CP949 → UTF-8)해 아래와 같이 **추정 복원** [판단]. 손실된 글자는 문맥으로 보완한 것이라 확정 전에 한 번 읽어볼 것.

  | Part | 추정 제목 | Part | 추정 제목 |
  |------|-----------|------|-----------|
  | 1 | 집합의 기초 | 9 | 부분집합 탐색 |
  | 2 | 집합 연산 | 10 | 수학적 구조 |
  | 3 | 관계 판별 | 11 | 데이터베이스 |
  | 4 | 반복과 탐색 | 12 | 정보검색 |
  | 5 | 구현 | 13 | AI와 데이터 |
  | 6 | 비트 집합 | 14 | 확률적 집합 |
  | 7 | 서로소 집합 | 15 | 병렬 집합 |
  | 8 | 조합론 | 16 | 연구 주제 |

- [x] 부록 제목도 같은 방법으로 복원: `BitSet은 언제 사용하는가?`, `Union-Find가 거의 O(1)인 이유`, `집합과 그래프의 연결`, `집합과 관계(Relation)`, `집합과 함수(Function)`, `SQL은 왜 집합 이론 위에서 동작하는가?`, `AI에서 Label Set과 Vocabulary Set의 의미`는 비교적 확실하고, `비트마스크와 집합의 ?? 관계`, `부분집합 ?거 최적화`는 글자 손실이 있어 문맥으로 보완
- [x] 병합된 헤딩 4곳 분리, `### 대표코드`와 ` ```cpp ` 줄 분리
- [x] `union()` 설명 두 줄을 `#`에서 본문으로 변경
- [x] [판단] 복구 후 다른 파일에도 같은 손상이 있는지 검사(깨진 한자 연속, U+FFFD) — 현재 Set.md 외에는 발견되지 않음

### 0-2. Tree.md BOM 제거 [실측]
- Tree.md 1069행(Part 6), 1206행(Part 7) 헤딩 앞에 U+FEFF가 끼어 있어 헤딩이 렌더링되지 않을 수 있음 (여러 파일을 합칠 때 들어간 것으로 추정).
- [x] 두 곳의 BOM 제거 (Set.md, NextPhasePlan.md의 파일 맨 앞 BOM은 정상 범위)

### 0-3. Part 번호·헤딩 구조 정리 [실측 + 판단]
- [x] **Graph.md**: "(보완)" 블록(Part 7~13)을 원래 Part로 병합. Part 11, 12는 접미사 없이 같은 제목이 두 번 나옴. 병합 후 Part 번호 중복이 없어야 함.
- [x] **Graph.md**: 부록에 있는 `IsTree`, `IsForest`, `IsBiconnected`를 Part 5(사이클)로 이동. [판단] 부록은 비교·해설(`BFS vs DFS` 등)만 남김.
- [x] **Hash.md**: "Part 16"이 2개. `Visualizations Placeholder` 항목 삭제 후 하나로 합침.
- [x] **Memory.md**: Part 3, 5, 6 결번. 원본 목차를 알 수 없으므로 다음 구성으로 **확정** [판단 → 확정]:
  - Part 3 스택 메모리: 현재 Part 2에 섞인 `PopFrame/CallFunction/ReturnFunction/LocalVariable/StackFrame/StackOverflow/TailCallOptimization`을 분리하고 `PushFrame()` 추가 (`StackFrame/StackOverflow`는 Stack.md가 정본이므로 링크형 요약)
  - Part 5 포인터와 참조: 신규. `Pointer`, `Reference`, `SmartPointer`(unique/shared/weak), `Aliasing` (현재 부록에 `Pointer vs Reference`, `Shared Pointer의 순환 참조` 해설만 있음)
  - Part 6 메모리 할당기: 2차 계획서의 "Part 6 = 할당기"에 따라 현재 Part 4에 섞인 `SlabAllocator/BuddyAllocator/ArenaAllocator/ObjectPool/FreeList`를 분리하고 `MemoryPool()` 추가
  - Part 4(힙 메모리)에는 `malloc/new/PlacementNew`만 남김

### 0-4. 일회성 변환 스크립트 처리 [실측 + 확정]
- `process.py`는 파일의 **모든 비어있지 않은 줄을 `##` 헤딩 + 빈 코드 블록으로 감싸는** 일회성 변환기이며, 로컬 경로(`C:\Users\cjh3c\...`)가 하드코딩되어 있고 파일을 제자리에서 덮어씀. **현재 파일에 재실행하면 구조가 망가짐.**
- [x] `archive/process.py`로 이동하고 맨 앞에 `raise SystemExit`로 실행 차단 (섹션 3의 근거 참조)

---

## 🚨 Phase A: 목차에서 누락된 항목 복구

### A-1. Graph.md [실측]
- [x] **Part 5**: `DetectCycle()` — 현재 DFS/BFS/UnionFind 3개 변형만 있음. [판단] 래퍼 함수보다 Part 서두 개요 설명 항목으로 대체 권장.
- [x] **Part 7**: `MinimumSpanningTree()` (Kruskal/Prim/Boruvka를 고르는 통합 인터페이스)
- [x] **Part 8**: `UnionSet()`
- [x] **Part 14 특수 그래프** (현재 `BipartiteGraph`, `DirectedGraph`만 있음): `UndirectedGraph()`, `WeightedGraph()`, `UnweightedGraph()`, `CompleteGraph()`, `SparseGraph()`, `DenseGraph()`, `PlanarGraph()`
- [x] **Part 15 그래프 모델** (현재 `PageRank`만 있음): `RandomGraph()`, `GridGraph()`, `TreeGraph()`, `HypercubeGraph()`, `ScaleFreeGraph()`, `SmallWorldGraph()`
- [x] **Part 16 응용 (Part 전체 없음)**: `DependencyGraph()`, `KnowledgeGraph()`, `SocialNetworkGraph()`, `CallGraph()`, `StateTransitionGraph()`, `ControlFlowGraph()`, `DataFlowGraph()`, `BayesianNetwork()`, `NeuralGraph()`
- [x] [판단] `PageRank()`는 모델이 아니라 알고리즘이므로 Part 15에서 Part 16(응용)으로 이동
- [x] **부록**: `Dijkstra vs A*` 비교 설명 (미작성)

### A-2. Tree.md [실측 + 판단]
- [x] **Part 7**: `Recolor()`, `DoubleBlack()` — 독립 항목 없음 (현재 `RBInsert/RBDelete/FixViolation`만 있음, 그나마 `RBDelete`와 `FixViolation`은 자리표시)
- [x] **Part 8 힙**: 현재 `BinaryHeap()` 하나에 `heapifyDown`이 들어 있을 뿐, `HeapInsert()`, `HeapDelete()`, `Heapify()`, `BuildHeap()`, `HeapSort()` 독립 항목 없음. [확정] Queue.md Part 5에 `PushHeap/PopHeap/Heapify/BuildHeap/HeapSort`가 이미 구현돼 있으므로 정본은 Queue.md. Tree.md의 5개 항목은 "완전이진트리의 배열 표현" 관점의 링크형 요약으로 쓴다(섹션 3 정책). 힙 변형(Phase C의 Fibonacci·Binomial·Pairing 등)은 Tree.md Part 8의 정본 항목으로 추가.
- [x] **Part 9**: `GeneralTree()`, `NaryTree()` (Part 9가 Trie 계열만 있음)
- [x] **Part 10**: `SuffixArray()` — 정본은 String.md Part 9이므로 Tree.md에는 링크형 요약으로 추가 (현재 AdvancedDataStructures.md에만 있음)
- [x] **Part 13**: `BTree()` 독립 항목 (현재 `BPlusTree()`만 있음). 2차 계획서는 "BTree 존재"라고 했으나 Tree.md에서는 확인되지 않음.
- [x] **부록**: `BST vs AVL vs Red-Black` 비교 설명

### A-3. Hash.md — Part 2~15 신규 작성 [실측 + 판단]
현재 Part 1(8개 항목)과 Part 16만 존재. 원본 목차를 알 수 없으므로(사용자도 기억하지 못함) **아래 표를 작업 기준으로 확정**하고, 원본을 찾으면 그때 조정합니다. "계획서" 표시는 2차 계획서·audit에 근거가 있는 항목입니다.

| Part | 내용 | 근거 |
|------|------|------|
| 1 해시의 기초 | `CreateHashTable`(유지) + `Insert/Search/Delete/Resize/Rehash/LoadFactor` | [판단] 해시 테이블 핵심 연산이 현재 하나도 없음 |
| 2 해시 함수 | `DivisionMethod`, `MultiplicationMethod`, `UniversalHashing`, `FNV`, `MurmurHash`, `xxHash`, `SipHash` | [판단] |
| 3 충돌 해결 | `Chaining`, `OpenAddressing`, `LinearProbing`, `QuadraticProbing`, `DoubleHashing`, `RobinHoodHashing`, `CuckooHashing`, `HopscotchHashing`, `CoalescedHashing` | 뒤 4개는 계획서, 앞 5개는 [판단] (현재 `Open Addressing`은 이름만 언급) |
| 4 완전 해시 | `PerfectHash`, `MinimalPerfectHash` | 계획서 |
| 5 롤링 해시 | `PolynomialRollingHash`, `RabinFingerprint`, `LongestCommonSubstringHash` | 계획서 |
| 6 해시 컨테이너 | `HashMap`, `LinkedHashMap`, `Multimap` (`HashSet`은 Set.md Part 5가 정본) | [판단] 원본을 몰라 채운 Part |
| 7 분산 해시 | `ConsistentHashing`, `VirtualNode`, `RendezvousHash`, `Chord`, `Kademlia` | 계획서 |
| 8 암호학적 해시 | `MD5`, `SHA256`, `HMAC`, `MerkleDamgard` | [판단] README: "암호학까지 이어지는 분야" |
| 9 DB 해시 | `HashIndex`, `HashJoin`, `ExtendibleHashing`, `LinearHashing` | [판단] README: "데이터베이스" |
| 10 OS·런타임 구현 | Python dict, Java HashMap(TreeBin), C++ `unordered_map`, Redis Dictionary, `LRUCache`, `LFUCache` | [판단] 현재 Part 1에 해설로 들어 있는 항목을 이전. `LRUCache/LFUCache`는 Phase C Tier 1 (`HashMap` + 이중 연결 리스트 조합) |
| 11 보안 | `HashDoS`, `Salting` | [판단] |
| 12 동시성 | `ConcurrentHashMap`, `LockFreeHashTable` | [판단] |
| 13 확률적 구조 | `BloomFilter`, `CountMinSketch` | [판단] 현재 Part 1에 `Bloom Filter` 해설만 있음. 정본은 AdvancedDataStructures.md Part 3이므로 여기는 해시 관점의 링크형 요약 |
| 14 유사도 해시 | `LocalitySensitiveHashing`, `SimHash`, `MinHash`, `SemanticHashing` | 계획서 |
| 15 최신 연구 | `SwissTable`, `LearnedHash` | [판단] |
| 16 시각화 | 현재 10개 보유 (Phase 0-3에서 중복 제거) | 실측 |

- [x] 현재 Part 1의 해설형 항목(`왜 Java HashMap은 TreeBin으로 바뀌는가?` 등)은 구현 항목이 아니므로 [판단] Part 10 또는 부록으로 이전

### A-4. String.md — Part 2~17 신규 작성 [실측 + 판단]
현재 Part 1(14개 항목)만 존재하고 그중 상당수가 해설형 제목입니다.

| Part | 내용 | 근거 |
|------|------|------|
| 1 문자열의 기초 | `CreateString` + `Length/Concat/Substring/Compare/Reverse/Split` | [판단] 기본 연산이 없음 |
| 2~5 | Part 2 기본 연산 응용(`Palindrome`, `Anagram`), Part 3 인코딩(ASCII/UTF-8/UTF-16), Part 4 동적 문자열(`Rope`, `GapBuffer`, `PieceTable` — 이 3개의 **정본**), Part 5 기본 패턴 검색(`NaiveSearch`, `KMP`) | [판단] 원본을 몰라 채운 Part. 현재 Part 1에 해설로 있는 항목을 분리 |
| 6 패턴 검색 | `RabinKarp`, `BoyerMoore`, `Horspool`, `SundaySearch` | 계획서 |
| 7 | `ZAlgorithm`, `LongestRepeatedSubstring`, `Manacher` | `Manacher`는 [판단] (Phase C Tier 1) |
| 8 | `Trie`, `AhoCorasick` | [판단] |
| 9 접미사 구조 | `SuffixArray`, `BuildSuffixArray`, `LCPArray`, `SuffixAutomaton`, `PalindromicTree` | 앞 4개는 계획서 (이 파일이 정본), `PalindromicTree(Eertree)`는 Phase C Tier 2 |
| 10 롤링 해시 | `PolynomialRollingHash`, `RabinFingerprint`, `SubstringHash`, `LongestCommonSubstring` | 계획서 |
| 11 압축·변환 | `LZW`, `BurrowsWheelerTransform`, `MoveToFront`, `Huffman` | `Huffman`은 [판단] |
| 12 편집 거리 | `Levenshtein`, `DamerauLevenshtein`, `LongestCommonSubstringDP` | `Levenshtein`은 [판단] (현재 저장소에 편집 거리 구현 없음) |
| 13~16 | 정규식/오토마톤, 컴파일러(렉서·파서), 검색엔진(`InvertedIndex`, n-gram), 생물정보학 | [판단] README: "컴파일러, 검색엔진, 생물정보학" |
| 17 AI/NLP | `BytePairEncoding`, `WordPiece`, `SentencePiece`, `TokenizeLLM`, `EmbeddingLookup`, `Detokenize` | 계획서 + README 특색 |
| 부록 | `KMP는 왜 O(n)인가?`, `Trie vs HashMap`, `Suffix Array vs Suffix Tree` | 현재 Part 1에 있는 해설을 부록으로 이동 |

### A-5. Memory.md [실측]
- [x] `MemoryPool()` — 저장소 전체에 없음 (2차 계획서 Part 6)
- [x] `PushFrame()` — `PopFrame()`만 있고 짝이 없음 (Part 2)
- [x] `CompareAndSwap()`, `MemoryBarrier()` — Memory.md에 없음 (Part 11, `CompareAndSwap`은 AdvancedDataStructures.md에만 있음)
- [x] Part 3, 5, 6 결번 처리: Part 3 스택 메모리 / Part 5 포인터와 참조 / Part 6 할당기로 확정 (Phase 0-3). `Pointer`, `Reference`, `SmartPointer`, `Aliasing`은 Part 5 신규 항목

---

## 🔧 Phase B: 자리표시 코드 실구현

**원칙 [판단]**: 신규 작성하는 항목(Phase A)은 처음부터 `assert(true)` / `assert(1 == 1)` 자리표시를 쓰지 않고, 실제로 동작하는 코드와 의미 있는 `assert`를 넣는다. 복잡도 주석도 템플릿 복사(`O(1)`)가 아닌 실제 값을 쓴다.

### B-1. Hash.md · String.md (100%)
- Phase A-3, A-4의 신규 작성과 함께 진행. 기존 33개 블록은 전부 자리표시이므로 재작성.

### B-2. Memory.md (104/104, 100%) [판단: 이 저장소에서 우선 구현 가치가 가장 높음]
- README 특색: "메모리 상태 변화를 단계별로 시각화"가 이 파일의 차별점인데 현재는 시각화에 쓸 구현이 전혀 없음.
- [x] 1순위: `malloc()`, `FreeList()`, `SlabAllocator()`, `BuddyAllocator()`, `ArenaAllocator()`, `ObjectPool()`, `MemoryPool()` (할당·해제 후 힙 상태를 출력하는 시뮬레이션)
- [x] 2순위: `MarkSweep()`, `CopyingGC()`, `GenerationalGC()`, `PageTable()`, `TLBLookup()`, `AddressTranslation()`
- [x] 3순위: `AtomicOperation()`, `CompareAndSwap()`, `MemoryBarrier()`, `ZGC()`, `EscapeAnalysis()`, `TransactionalMemory()` (2차 계획서 B-3)

### B-3. AdvancedDataStructures.md (110/112, 98%)
- [x] 1순위 [판단]: README가 "책의 정체성"으로 꼽은 6개 — `HNSW()`, `FAISSIndex()`, `LSMTree()`, `AdaptiveRadixTree()`, `LearnedIndex()`, `CacheObliviousBTree()`
- [x] 2순위 (2차 계획서 B-5): `BitVector()`, `Rank()`, `Select()`, `WaveletTree()`, `FMIndex()`, `BallTree()`, `BVHTree()`, `IVFIndex()`, `ProductQuantization()`
- [x] 3순위 [판단]: 실무 빈도가 높은 `BloomFilter()`, `CountMinSketch()`, `HyperLogLog()`, `SkipList()`, `LockFreeQueue()`

### B-4. PathFinding.md (89/102, 87%)
- [x] Part 5: `JumpPointSearch()`, `ThetaStar()`, `HierarchicalPathFinding()`
- [x] Part 6: `DStar()`, `DStarLite()`, `LifelongPlanningAStar()`
- [x] Part 7: `YenAlgorithm()`, `EppsteinAlgorithm()`
- [x] Part 11: `RapidlyExploringRandomTree()`, `RRTStar()`, `ProbabilisticRoadMap()`
- [x] Part 16: `MonteCarloTreeSearch()`, `AntColonyOptimization()`
- [x] [판단] Part 13(`OSPF`, `RIP`, `BGPPathSelection`) 등 외부 시스템 의존 항목은 실제 구현이 아니라 **축약 시뮬레이션**으로 충분

### B-5. Set.md (59/102, 57%) — Phase 0-1 완료 후 진행
- 자리표시 항목: `IsSuperset`, `LinkedSet`, `UnionByRank`, `PathCompression`, `ConnectedComponents`, `CombinationWithReplacement`, `Backtracking`, `BitMaskEnumeration`, `MeetInTheMiddle`, `SubsetSum`, `KnapsackSubset`, `BinaryRelation`, `EquivalenceRelation`, `Partition`, `EquivalenceClass`, `QuotientSet`, `Distinct`, `Projection`, `Selection`, `Join`, `GroupBy`, `DuplicateElimination`, `PostingList`, `JaccardSimilarity`, `MinHash`, `LocalitySensitiveHashing`, `FeatureSet`, `VocabularySet`, `CandidateSet`, `ConstraintSet`, `BloomFilter`~`QuotientFilter`, `ConcurrentSet`~`LearnedSetIndex`, `DynamicConnectivity`, 부록 해설
- [x] [확정] `UnionByRank/PathCompression/ConnectedComponents`는 Graph.md Part 8이 정본(실구현 있음)이므로 Set.md는 집합 관점의 링크형 요약(15줄 이내 + `→ 정본`). `BloomFilter` 계열은 AdvancedDataStructures.md Part 3이 정본, `MinHash/LocalitySensitiveHashing`은 Hash.md Part 14가 정본, `SkipListSet`은 List.md Part 10이 정본. 나머지 자리표시 항목(`Join`, `GroupBy`, `SubsetSum` 등)은 Set.md에서 직접 구현.

### B-6. Tree.md (38/91, 41%) — 대부분 Part 11~16
- [x] Part 7: `RBDelete()`, `FixViolation()`
- [x] Part 9~10: `RadixTree()`, `SuffixTree()`, `PatriciaTrie()`
- [x] Part 11~12: `KDTree()`, `QuadTree()`, `Octree()`, `BSPTree()`, `RangeQuery()`, `LazyPropagation()`, `RangeUpdate()`
- [x] Part 13: `BPlusTree()`, `SplayTree()`, `Treap()`, `CartesianTree()`, `ScapegoatTree()`
- [x] Part 14~16: `PersistentTree()`, `ImmutableTree()`, `FingerTree()`, `RootingTree()`, `TreeDP()`, `HeavyLightDecomposition()`, `CentroidDecomposition()`, `BinaryLifting()`, `EulerTourTechnique()`, `ExpressionTree()`, `SyntaxTree()`, `ParseTree()`, `DecisionTree()`, `MerkleTree()`, `IntervalTree()`, `RopeTree()`, `RTree()`, `VanEmdeBoasTree()`
- [x] 부록 3개 (`트리 순회의 재귀와 반복 구현`, `Binary Tree vs BST`, `Segment Tree vs Fenwick Tree`)
- [x] [확정] `HeavyLightDecomposition`, `CentroidDecomposition`, `EulerTour`는 Tree.md가 정본이고 Graph.md는 링크형 요약(`EulerTour`는 양쪽 모두 실구현이므로 유지하고 상호 링크). `RopeTree`는 String.md Part 4, `FingerTree/PersistentTree`는 AdvancedDataStructures.md Part 1·4가 정본이므로 Tree.md는 링크형 요약. 구간·공간·균형 트리는 Tree.md가 정본이고 AdvancedDataStructures.md가 링크형 요약(섹션 3 표).

### B-7. Graph.md (15/78), List.md (22/78), Queue.md (4/53)
- [x] **Graph.md**: `AStar()`, `JumpPointSearch()`, `Johnson()`, `GreedyBestFirstSearch()`, `ThetaStar()`, `PushRelabel()`, `MinCostMaxFlow()`, `BlossomAlgorithm()`, `Gabow()`, `HeavyLightDecomposition()`, `CentroidDecomposition()`, 해설 `BFS vs DFS`, `DAG가 중요한 이유`, `Prim vs Kruskal`, `Union-Find 시간복잡도`
- [x] **List.md**: `SentinelNode()`, `XORLinkedList()`, `Iterator()`, `Free()`, `Zip()`, `SkipList()`, `Rope()`, `UnrolledLinkedList()`, `GapBuffer()`, `PieceTable()`, `FingerTree()`, `PersistentList()`, `ImmutableList()`, 부록 해설 9개
- [x] **Queue.md**: `CircularBuffer()`, `MichaelScottQueue()`, `PersistentQueue()`, `ImmutableQueue()`
- [x] [확정] PathFinding.md ↔ Graph.md 겹침은 성격별로 나눔: 휴리스틱 탐색(`AStar/JumpPointSearch/ThetaStar/GreedyBestFirstSearch`)은 PathFinding.md가 정본, 최단 경로·일반 탐색(`Johnson`, `SPFA`, `BidirectionalSearch`, `IDAStar` 등)은 Graph.md가 정본. 비정본 쪽은 링크형 요약.
- [x] [확정] List.md의 `SkipList` 정본, `Rope/GapBuffer/PieceTable`은 String.md Part 4가 정본(List.md는 링크형 요약), `FingerTree/PersistentList/ImmutableList`는 AdvancedDataStructures.md가 정본(List.md는 링크형 요약)

---

## 💡 Phase C: 추가 후보 자료구조 [판단]

저장소 어디에도 독립 항목이 없는 자료구조를 검색으로 확인한 목록입니다. **Tier 1과 Tier 2 모두 채택 [확정]**. 단 Phase A·B가 끝나기 전에 시작하지 않는 것을 권장하며, 정본 위치는 아래 표로 확정합니다(섹션 3의 중복 구현 정책 적용).

### Tier 1: 기존 Part에 자연스럽게 들어가며 추가 가치가 큼 (권장)
| 후보 | 넣을 위치 | 이유 |
|------|-----------|------|
| Fibonacci Heap, Binomial Heap, Pairing Heap, Leftist Heap, d-ary Heap | Tree.md Part 8 (확정) | PathFinding.md가 "Fibonacci Heaps speed up Dijkstra decrease-key"라고 출력만 하고 정작 구현이 없음 |
| 2-3 Tree, 2-3-4 Tree, Left-Leaning Red-Black | Tree.md Part 7 | Red-Black Tree 이해의 다리. 현재 `Recolor/DoubleBlack` 설명이 비어 있어 더 필요 |
| Order-Statistic Tree, Weight-Balanced Tree | Tree.md Part 13 | 범위 질의·순위 질의의 기본 |
| Open Addressing 계열, Load Factor, 해시 함수 | Hash.md Part 2~3 | 해시 편의 핵심인데 현재 전무 (Phase A-3에 이미 포함) |
| Huffman, Aho-Corasick, Edit Distance | String.md | 문자열 편의 대표 알고리즘인데 현재 전무 (Phase A-4에 이미 포함) |
| LRU Cache, LFU Cache | Hash.md Part 10 (확정) | Hash+Linked List 조합의 대표 응용. 현재 Memory.md의 페이지 교체 설명에만 이름이 나옴. Memory.md 부록과 List.md Part 10에서 링크 |
| Manacher | String.md Part 7 (확정) | 회문 탐색의 선형 시간 알고리즘 |

### Tier 2: 채택 [확정], Tier 1 이후 진행
| 후보 | 넣을 위치 | 비고 |
|------|-----------|------|
| Link-Cut Tree, Top Tree | Tree.md Part 15 | 동적 트리. `HeavyLightDecomposition`과 비교 |
| Zip Tree, WAVL Tree | Tree.md Part 13 | `Treap`, `AVL`/`Red-Black`과 비교 |
| Sqrt Decomposition, Merge Sort Tree | Tree.md Part 12 | `SegmentTree`와 비교 |
| Ternary Search Tree | Tree.md Part 9 | Trie 계열 |
| Min-Max Heap, Soft Heap | Tree.md Part 8 | Tier 1의 힙 변형과 함께 작성 |
| Palindromic Tree (Eertree) | String.md Part 9 | `Manacher`와 비교 |
| BK-Tree, VP-Tree, Cover Tree | AdvancedDataStructures.md Part 5 | 거리 공간 인덱스. `BK-Tree`는 String.md의 `Levenshtein`을 사용 |
| Dancing Links (Exact Cover) | Set.md Part 9 | 연결 리스트 기반이므로 List.md Part 10에서 링크 |
| Multigraph, Hypergraph | Graph.md Part 14 | 특수 그래프에 추가 |
| t-digest | AdvancedDataStructures.md Part 3 | 확률적 자료구조 |

### 채택 기준 [판단 → 확정]
- 새 항목은 (1) 어느 파일·Part에 들어가는지 (2) 섹션 3 표에서 정본이 어디인지 (3) 실제 동작하는 대표코드 (4) 실제 복잡도 — 네 가지를 갖춘 뒤에만 추가.
- Tier 1·2 합계 약 30개이므로 한 번에 넣지 않고 Tier 1 → Tier 2 순서로, 같은 Part에 들어가는 항목은 묶어서 작성.

---

## 🏗️ Phase D: 구조/품질 개선

### D-1. 복잡도 표기 [실측]
- Memory.md: 복잡도 표기 **0건**
- AdvancedDataStructures.md(111/112), Hash.md(19/19), String.md(14/14), PathFinding.md(95/102): `// Time Complexity: O(1)` **템플릿 복사**로 보임. 실제 복잡도와 다르므로 오해를 부를 수 있음.
- [x] 실구현(Phase B) 시 실제 복잡도로 교체. 구현 전까지는 [판단] 틀린 값을 두기보다 `TBD`로 표시하는 편이 안전.

### D-2. 문서화
- [x] 통합 README.md 구성: 전체 자료구조 카테고리별 Index 페이지 (현재 README는 저장소 철학과 특색 메모만 있음)
- [x] 상호 참조: 섹션 3의 정본 표에 있는 모든 "링크형 요약" 항목에 `→ 정본: X.md Part N` 문구 추가 (Graph.md ↔ PathFinding.md, Tree.md ↔ AdvancedDataStructures.md, Tree.md ↔ Queue.md(힙), Set.md ↔ Graph.md(Union-Find) ↔ AdvancedDataStructures.md(Bloom Filter) 등)
- [x] (대체) Mermaid 대신 E-9 의 ASCII 그림 + 골든 단언(회전 전후, 해시 버킷, BFS 층, DFS 구간 막대 …)

### D-3. 자동 검증 [판단]
`audit_result.txt`는 수동 스냅샷이라 이미 현재 상태와 어긋났으므로 스크립트로 대체합니다.
- [x] 점검 항목: 헤딩 계층(`#`/`##`/`###`), 빈 코드 블록, 자리표시 코드 비율, 중복 Part·중복 헤딩, 파일 중간 BOM, 인코딩 손상(깨진 한자 연속·U+FFFD)
- [x] 코드 블록을 추출해 `g++ -std=c++17`로 컴파일하고 실행해 `assert` 통과 여부 확인 (이번 점검에서는 하지 않음)
- [x] 양쪽 모두 실구현인 11개 중복(섹션 3)의 코드가 서로 어긋나지 않는지 비교
- [x] `audit_result.txt` 삭제 또는 "과거 스냅샷" 표기

## 🌟 Phase E: 완성도 향상 (4차 개정에서 신규) [실측 + 판단]

Phase B가 "자리표시를 없애는" 일이라면, Phase E는 "남은 코드가 **책의 목적(구조 해설)에 맞게 깊고, 깨끗하고, 어디서나 돌고, 서로 일관된가**"를 끌어올리는 일입니다. 아래 수치는 이번 세션에서 직접 잰 값입니다.

### E-0. 품질 스냅샷 [실측, 2026-10-08 — 4차 개정 시점의 이력]

| 지표 | 값 | 해석 |
|------|----|------|
| 컴파일·실행 통과 | 자리표시를 제외한 모든 블록 통과 (`audit --compile`) | 기준선 확보 |
| 자리표시 0개인 책 | Hash, String, Memory, Tree (Tree 121항목) | ADS는 41/116, PathFinding 13/102, Set 43/103 등이 실구현 |
| 위생 프로브 (`-Wall -Wextra` + ASan/UBSan/LSan, Tree·Hash·String·Memory 375블록) | UB·ASan 오류 0 (Memory의 의도적 메모리 실험 5개 제외), **누수 51 (Tree 49, Memory 2)**, **경고 42건/24블록** (`misleading-indentation` 13, `sign-compare` 3, `missing-field-initializers` 3 …) | 새로 쓴 코드는 깨끗하고, 문제는 **원본 블록**에 집중 |
| 실행 시간 | 위 375블록 합계 약 99초(병렬 전). ASan 하에서 `ConcurrentGC` 60초 초과, `SequentialConsistency` 14초 | 시간 예산 규칙 필요 |
| 깊이(원본 블록) | **STL 래퍼 추정 151개**: List 40, Set 36, Queue 30, Graph 18, Stack 13, PathFinding 8 … (`std::stack`을 쓰고 `push/top`만 호출하는 식) | "구조 해설" 책인데 구조를 구현하지 않고 STL 사용법만 보여 주는 항목 |
| 이식성 | `__builtin_*` 22곳, `M_PI` 2, `__int128` 1, POSIX 헤더(`sys/`·`unistd`) Memory 27곳(대부분 `#if` 가드), 스레드 19곳 | GCC/Clang 가정. 사용자 PC는 Windows(경로 `C:\Users\...`)라 MSVC 여부가 열린 항목 |
| 결정성 | `random_device`·`rand`·`time` 시드 0건 | 좋음. 스레드 코드는 반복 실행 검사 필요 |
| 동명 항목 | 둘 이상의 파일에 실구현이 있는 이름 55개 (일반 연산 `Clear/Size/IsEmpty` 등 제외 시 약 35개) | 링크형 요약이 정본과 어긋나지 않는지 기계 검사 필요 |
| 저장소 인프라 | CI 없음, LICENSE·`.gitignore` 없음, `audit_result.txt`는 낡은 수동 스냅샷 | E-5, E-11 |

### E-1. 위생 패스: 경고 0, 새니타이저 통과 [우선순위 높음]
- [x] `tools/audit.py`에 `--strict` 추가: `-Wall -Wextra`로 컴파일해 경고를 실패로 취급, `--san`: `-fsanitize=address,undefined`(+LeakSanitizer)로 실행. 결과는 기존 해시 캐시에 모드별로 저장.
- [x] 누수 51개(대부분 `new` 후 `delete` 없음)를 **트리 해제 함수 또는 `unique_ptr`** 로 정리. 새로 쓰는 코드는 처음부터 해제까지 포함(이미 그렇게 작성 중).
- [x] 경고 24블록 수정(`misleading-indentation`은 원본 한 줄 `if (...) a; b;` 패턴이라 줄바꿈만으로 해결).
- [x] 메모리 레이아웃을 일부러 들여다보는 Memory 항목(`new()`, `TextSegment`, `StackOverflow`, `MemoryLeak`, `ProcessMemory`)은 새니타이저 하에서 의미가 달라지므로 코드 주석에 `// audit: no-sanitize` 표식을 두고 `--san`에서 제외. `ConcurrentGC`는 일반 실행 시간을 재 보고 필요하면 반복 횟수를 줄임.
- 완료 기준: `audit --strict --san` 전 책 0 실패 (표식 제외 항목은 목록으로 공개).

### E-2. 깊이 보강: STL 래퍼 → 직접 구현 [우선순위 높음, 이번 라운드의 가장 큰 품질 격차]
- 문제: 예를 들어 Stack.md `Peek()`는 `std::stack<int> s; s.push(30); s.top()` 뿐이고, List.md `Reverse()`는 `std::list::reverse()` 호출뿐입니다. 책의 목적이 "구조를 눈으로 이해하는 자료구조"이므로 이런 블록은 **구조를 하나도 보여 주지 못합니다.**
- 정책 [판단]: 래퍼 블록은 **직접 구현한 최소 구조 + 경계 사례(빈 구조·언더플로·용량·중복) 검사 + 같은 연산을 `std::`로 수행한 결과와의 차분 검사(differential test)** 로 교체한다. STL 호출은 "실무에서는 이렇게" 한 줄로만 남긴다.
- 적용 순서(규모 순): Queue 30 → List 40 → Set 36 → Stack 13 → Graph 18 → PathFinding 8. **아직 자리표시인 항목(List 22, Set 59, Queue 4, PathFinding 89)은 처음부터 이 정책으로 직접 구현**해 이중 작업을 피한다.
- 래퍼 판별 휴리스틱(`struct/class` 없음 + 22줄 이하 + STL 컨테이너 사용)을 `tools/audit.py --list-thin`로 노출해 진행률을 추적.
- 완료 기준: 판별 휴리스틱에 걸리는 블록 0개(의도적으로 STL 사용법을 보이는 "STL 대응" 항목은 `// audit: stl-demo` 표식).

### E-3. 이식성 [판단]
- [x] `tools/audit.py --portable`: `clang++ -std=c++17`와 `g++ -std=c++20 -pedantic` 컴파일을 추가로 시도해 비교(실행은 g++ 기준으로 충분).
- [x] GCC 전용 구성요소(`__builtin_popcountll/clzll/ctzll`, `__int128`, `M_PI`, `cbrtl`)를 목록화하고, 이식성 표를 INDEX에 자동 생성. 새 코드에서는 `std::bitset::count`, `<cmath>`의 상수 정의 등 표준 대안이 있는 경우 우선 사용.
- [x] POSIX 전용(Memory)은 가드가 모두 있는지 기계 확인(가드 밖의 `sys/`·`unistd.h`·`fork`·`mmap`을 찾는 검사).
- 결정 필요(열린 항목 3): **MSVC 지원 범위.** 기본안: GCC/Clang(Windows에서는 MinGW-w64/WSL) 지원을 명시하고, MSVC에서 안 되는 항목은 목록으로 공개.

### E-4. 결정성 · 시간 예산 · 플레이키 검사 [판단]
- [x] 블록당 실행 시간 상한 10초(현행) 유지 + `--time` 보고에서 3초 초과 블록 목록화 → 반복 횟수 조정.
- [x] `audit --repeat N`: 스레드를 쓰는 블록(Memory 17, Hash 2)을 N회 반복 실행해 간헐 실패(레이스·타이밍 의존 단언) 탐지. 타이밍 단언은 금지하고 횟수·불변식 단언만 허용.
- [x] 난수는 모두 고정 시드(현재 위반 0건)임을 린트 항목으로 고정.

### E-5. CI와 도구 [판단]
- [x] `.github/workflows/audit.yml`: ubuntu-latest, g++ 설치 상태에서 `python3 -I tools/audit.py --compile --strict`(PR·push), 주 1회 `--san --portable --repeat 3` 스케줄. 해시 캐시를 `actions/cache`로 보존해 변경된 블록만 다시 컴파일.
- [x] 도구 자체 테스트: `tools/test_tools.py`(mdedit의 각 지시어 왕복, audit의 파서·플레이스홀더 판정)로 도구가 책 파일을 망가뜨리지 않음을 보장.
- [x] 생성 문서의 최신성 검사(E-7)를 같은 워크플로에 포함: 책을 고치고 `INDEX.md`를 갱신하지 않으면 실패.

### E-6. 링크·중복 무결성 `tools/linkcheck.py` [판단]
- [x] 링크형 항목의 `정본은 X.md Part N` 주석을 모두 파싱해 **대상 파일·Part·동명 항목이 실제로 존재하는지** 검사(현재 `where.py`가 수동 조회용).
- [x] 섹션 3의 정본 표를 데이터 파일(`tools/canonical.json`)로 옮겨, 비정본 위치에 있는 항목이 링크 주석을 갖추었는지 역방향 검사.
- [x] 동명 실구현 55개 중 일반 연산을 제외한 쌍은 `canonical.json`의 `allow-both`(양쪽 모두 실구현 허용: 예 Dijkstra Graph/PathFinding) 또는 `link`로 분류되도록 강제. 분류되지 않은 쌍이 있으면 실패.
- [x] 양쪽 실구현 쌍은 **같은 테스트 벡터**를 쓰도록 하고(예: Dijkstra 두 구현이 같은 그래프에서 같은 거리), 서로 다른 결과가 나오는지 `tools/drift.py`가 두 블록을 컴파일해 출력의 `assert`가 아닌 **표준 출력 한 줄**로 비교.

### E-7. 생성 문서: 색인과 복잡도 치트시트 [판단]
- [x] `tools/gen_index.py` → `INDEX.md`: 책별 Part 제목과 항목 목록(`##`), 항목 수, 정본/링크형 구분, 이식성 표시, 이 책에 속한 "동명 항목의 정본 위치". 종이책 목차의 기반이 된다.
- [x] 같은 스크립트가 각 블록 끝의 `// Time/Space Complexity` 주석을 모아 `COMPLEXITY.md`(자료구조·연산별 복잡도 표)를 생성.
- [x] README 상단에 짧은 "현황" 블록(책 11권, 항목 수, 자리표시 0, 검증 날짜)을 스크립트가 갱신. README의 기존 철학·특색 메모는 건드리지 않는다.

### E-8. 복잡도 정확성 린트 [판단]
- 배경: 자리표시에서 복사된 `O(1)` 템플릿과 원본 블록의 값이 실제와 다를 수 있다.
- [x] `tools/complexity_lint.py` 휴리스틱: 코드에 이중 반복문·재귀·정렬이 있는데 `Time: O(1)`이면 경고, `std::sort`가 있는데 `O(N)`이면 경고, 공간이 `O(1)`인데 컨테이너를 N개 채우면 경고 → 경고 목록을 사람이 검토해 수정(자동 수정 금지).
- [x] 새로 쓴 항목은 이미 구현 기준으로 적었으므로 우선 원본 블록 약 300개가 대상.

### E-9. 시각화 패스: 이 시리즈의 정체성 [판단]
- 근거: README의 "구조를 눈으로 이해한다"는 방향. 이미 Hash(시각화 10편)·Memory(레이아웃 출력)는 갖췄지만 Tree·Graph·List·Stack·Queue·PathFinding·Set은 거의 숫자 단언뿐입니다.
- [x] 대표 항목 약 40개에 **ASCII 렌더러**를 붙여 단계별 상태를 출력하고, 출력 문자열을 **골든 단언**(`assert(out == "...")`)으로 고정: AVL/레드-블랙 회전 전후, 힙 배열↔트리 대응, B-트리 분할, 스킵 리스트 레벨, 연결 리스트 역방향 회전 단계, 유니온-파인드 숲, BFS 층, A* 격자 경로, 해시 체이닝 버킷 등.
- [x] 출력은 결정적이어야 하고(시드 고정, 포인터 값 금지) 폭 80열 이내.
- [x] (선택) 마크다운 Mermaid 그림은 해설 본문 몫이므로 이 저장소에서는 만들지 않는다 — README가 `###` 해설을 사람이 쓰도록 정해 둠.

### E-10. Tier 3 추가 후보 (선택, Phase B~E 완료 후 예산이 남을 때) [판단]
채택 기준(Phase C와 동일): ① 실무·교재에서 널리 쓰임 ② 기존 Part에 자연스럽게 들어감 ③ 정확성을 단언으로 검증 가능. 작성 직전에 `tools/where.py`로 중복을 확인한다(예: Tarjan·Kosaraju·HopcroftKarp는 이미 Graph에 있음).

| 후보 | 들어갈 곳 | 이유 |
|------|-----------|------|
| HAMT(해시 배열 매핑 트라이), RRB-Vector | ADS Part 1 | Clojure·Scala 영속 컬렉션의 핵심 |
| Roaring Bitmap 상세, Bitmap Index | Set Part 16 → ADS Part 2 | 검색엔진·OLAP |
| Misra–Gries, Space-Saving, Count Sketch, Reservoir Sampling | ADS Part 3 | 스트림 알고리즘 필수 |
| 계층형 Timing Wheel, Radix Heap, Dial(버킷 큐), Calendar Queue | Queue Part 5·11 / Graph | 타이머·최단경로 가속 |
| Chase–Lev 덱, LMAX Disruptor 링 버퍼, RCU, Seqlock, Epoch 기반 회수 | ADS Part 9 / Memory Part 11 | 동시성 실무 |
| Bw-Tree, Masstree, CSB+Tree, Merkle Patricia Trie | ADS Part 8·10·15 | DB·블록체인 |
| Euler Tour Tree, 동적 연결성(오프라인) | Graph / Tree Part 15 | 동적 그래프 |
| Sqrt Tree, Disjoint Sparse Table | ADS Part 6 | 정적 RMQ 변형 |
| DCEL(반변), Quad-Edge | ADS Part 5 | 계산기하 |
| Skew Heap, Interval Heap, Tournament/Loser Tree | Tree Part 8 | 힙 변형·외부 정렬 |
| BiMap, Multiset/Multimap 직접 구현 | Set / Hash | 컨테이너 의미론 |

### E-11. 저장소 위생 [판단]
- [x] `.gitignore`(`*.out`, `a.out`, `__pycache__/`), `tools/README.md`(DSL·감사 사용법), `audit_result.txt`는 삭제하고 `audit` 결과를 `reports/` 대신 CI 아티팩트로 대체.
- [ ] LICENSE는 **사용자가 정할 일**이므로 임의로 추가하지 않는다(열린 항목 2).
- [x] 헤딩 규칙 유지 검사: Part=`# `, 항목=`## `, 첫 `###`=`대표코드`, 언어=C++ (이미 `audit.py`가 검사).

### E-12. 최종 인수 검사 체크리스트
1. `python3 -I tools/audit.py --compile --strict --san --portable` 전 책 통과, 자리표시 0, 래퍼 0(표식 제외), 누수 0.
2. `tools/linkcheck.py`, `tools/drift.py`, `tools/complexity_lint.py` 경고 0 또는 승인된 예외 목록만.
3. `INDEX.md`·`COMPLEXITY.md`·README 현황이 최신(CI 통과).
4. 무작위 표본(책당 15항목)을 사람이 읽듯 검토: 한국어 주석이 코드와 일치하는지, 주장(복잡도·확률·재현율)이 단언 또는 출력으로 뒷받침되는지.
5. 알려진 한계 목록(단순화한 구현: 예 TangoTree의 보조 트리, Soft Heap 제외 등)을 `NextPhasePlan.md`에 정직하게 기록.

### E-13. 권장 순서와 규모 [판단]
```
(진행 중) ADS 나머지 → PathFinding → Set/Graph/List/Queue/Stack   ← 자리표시는 E-2 정책(직접 구현+차분 검사)으로 작성
 → Phase C 잔여(Set Dancing Links)
 → E-1 위생 → E-3 이식성 → E-4 결정성 → E-6 링크·드리프트 → E-8 복잡도 린트
 → E-2 남은 원본 래퍼 보강 (Queue → List → Set → Stack → Graph → PathFinding)
 → E-9 시각화 패스
 → E-5 CI·도구 테스트 → E-7 생성 문서 → E-11 위생
 → Phase D 마감(README 색인은 E-7로 대체)
 → E-10 Tier 3 (예산 잔여 시)
 → E-12 최종 인수 검사 + 계획서 최종 갱신
```
대략적 규모(토큰 기준): 자리표시 구현 약 2.5M, E-2 약 0.6M, E-1·3·4·6·8 약 0.5M, E-9 약 0.3M, 도구·CI·문서 약 0.3M, E-10 약 0.5~1M. 남은 예산 안에 들어가며, 순서상 뒤쪽(E-10)이 먼저 잘린다.

---

---

## 📋 남은 열린 항목

계획서가 다루던 항목은 모두 끝났고, 아래는 **저장소 소유자가 정할 일**이거나 계획 밖의 선택 사항이다.

1. **제안 목차의 검토**: 원본 목차를 모르므로 A-3(Hash), A-4(String), A-5(Memory)의 [판단] 표시 Part 는 작업하면서 읽어 본 구성이다. 원본 `*(2).md` 가 발견되면 그 기준으로 조정.
2. **Set.md 추정 복원 제목**: Phase 0-1 의 Part 제목은 깨진 문자열을 역변환해 추정한 것이므로 한 번 읽어 확인.
3. **MSVC 지원 범위 (E-3)**: 현재 방침은 GCC/Clang(Windows 는 MinGW-w64/WSL). MSVC 까지 지원하려면 `__builtin_*`·`M_PI`·`__int128` 대체 코드를 항목마다 넣어야 한다.
4. **LICENSE**: 소유자가 정할 일이라 추가하지 않았다.
5. **파이썬 대응 코드**: README 의 "파이썬 들여쓰기 부분을 포함하는 마무리 설명" 은 사람이 쓰는 해설 몫(`###`)으로 보고 채우지 않았다. 필요하면 핵심 항목 약 60개에 검증 가능한 ```python 블록을 추가할 수 있다.
6. **Part 제목 언어**: ADS Part 일부가 영어 제목, 나머지는 한글. 현상 유지(번역은 INDEX 에서만 병기).
7. **브랜치 정리**: 작업 브랜치(`claude/busy-mendel-mthsyr`)를 기본 브랜치로 합치는 방법과 오래된 브랜치 정리는 소유자가 정한다(PR 은 요청이 있을 때만 만든다).

---

## 📅 권장 작업 순서 [판단]

```
Phase 0 (Set.md 재작성, Tree BOM, Part 번호 정리; process.py 처리는 완료)
 → A-3 Hash Part 2~15 (+ B-1, 실구현으로 작성)
 → A-4 String Part 2~17 (+ B-1, 실구현으로 작성)
 → A-1 Graph Part 14~16
 → A-2 Tree 누락 항목
 → A-5 Memory 누락 항목
 → B-2 Memory → B-3 AdvancedDS → B-4 PathFinding → B-5 Set → B-6 Tree → B-7 Graph/List/Queue
 → Phase C Tier 1 → Tier 2 (같은 Part에 들어가는 항목은 묶어서)
 → Phase D
 → Phase E (세부 순서는 E-13)
```

순서의 근거:
- Set.md는 지금 읽을 수 없으므로 다른 작업보다 먼저 복구해야 함.
- Hash.md는 Part 16개 중 14개(Part 2~15), String.md는 17개 중 16개(Part 2~17)가 없는 상태로, 2차 계획서의 우선순위(Graph·Tree 먼저)와 달리 **누락 규모가 가장 큼**. Graph·Tree는 남은 누락이 소수의 항목임.
- 신규 작성은 자리표시 없이 실구현으로 해야 Phase B의 작업량이 늘지 않음.
