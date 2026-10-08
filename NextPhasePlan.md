# Data Structure Project 2: Next Iterations Plan (3차 개정판)

이 계획서는 2차 개정판을 **2026-10-08 기준 저장소 실측**(커밋 `2b166e7`)으로 갱신한 것입니다. 2차 개정판의 체크리스트 중 이미 처리된 것은 완료로 옮기고, 이번 점검에서 새로 발견된 문제(파일 손상, 번호 중복, 자리표시 코드 비율)와 추가 후보를 반영했습니다.

표기 규칙: **[실측]** = 파일을 직접 대조해 확인한 사실, **[판단]** = 실측을 바탕으로 한 작성자(AI)의 권고, **[확정]** = 사용자가 답했거나 판단을 위임해 채택된 결정(섹션 3 참조).

> 2026-10-08 갱신: 사용자 답변(Set.md 정상본 없음 / 원본 목차 모름 / Phase C는 Tier 2까지 / `process.py`·중복 구현 정책은 작성자 판단 위임)을 반영했습니다.

우선순위: **Phase 0 (손상 복구) → Phase A (누락 복구) → Phase B (자리표시 코드 실구현) → Phase C (추가 후보) → Phase D (품질/문서화)**

---

## 0. 점검 방법과 한계

- 방법: `audit_result.txt`(117개 항목)와 2차 계획서의 항목을 현재 파일의 `##` 헤딩과 대조, 코드 블록의 자리표시 여부 집계, 저장소 전체 문자열 검색.
- 자리표시 코드의 기준: `assert(true)` 또는 `assert(1 == 1)`와 출력문만 있고 실행 로직이 없는 ` ```cpp ` 블록(코드 8줄 이하).
- 한계 1: 원본 목차 `*(2).md`는 저장소에 없고 사용자도 내용을 기억하지 못합니다. "원래 있어야 했던 항목"은 `audit_result.txt`와 2차 계획서에 적힌 것까지만 확인할 수 있으며, 그 밖의 Part 구성은 이 계획서의 제안 목차를 작업 기준으로 삼습니다.
- 한계 2: 사용자 로컬 폴더 `DataStructureProject2-main`은 비교하지 못했습니다(클라우드 세션에서 접근 불가). Set.md 정상본도 없는 것으로 확인됐습니다.
- 한계 3: 코드가 실제로 컴파일·실행되는지는 확인하지 않았습니다(Phase D-3에서 다룸).

---

## 1. 전체 파일 현황 [실측]

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
- [ ] ASCII 메서드명과 코드 로직은 그대로 보존하고, 한글 Part 제목·부록 제목·코드 주석·설명만 재작성
- [ ] Part 제목은 깨진 문자열을 역변환(CP949 → UTF-8)해 아래와 같이 **추정 복원** [판단]. 손실된 글자는 문맥으로 보완한 것이라 확정 전에 한 번 읽어볼 것.

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

- [ ] 부록 제목도 같은 방법으로 복원: `BitSet은 언제 사용하는가?`, `Union-Find가 거의 O(1)인 이유`, `집합과 그래프의 연결`, `집합과 관계(Relation)`, `집합과 함수(Function)`, `SQL은 왜 집합 이론 위에서 동작하는가?`, `AI에서 Label Set과 Vocabulary Set의 의미`는 비교적 확실하고, `비트마스크와 집합의 ?? 관계`, `부분집합 ?거 최적화`는 글자 손실이 있어 문맥으로 보완
- [ ] 병합된 헤딩 4곳 분리, `### 대표코드`와 ` ```cpp ` 줄 분리
- [ ] `union()` 설명 두 줄을 `#`에서 본문으로 변경
- [ ] [판단] 복구 후 다른 파일에도 같은 손상이 있는지 검사(깨진 한자 연속, U+FFFD) — 현재 Set.md 외에는 발견되지 않음

### 0-2. Tree.md BOM 제거 [실측]
- Tree.md 1069행(Part 6), 1206행(Part 7) 헤딩 앞에 U+FEFF가 끼어 있어 헤딩이 렌더링되지 않을 수 있음 (여러 파일을 합칠 때 들어간 것으로 추정).
- [ ] 두 곳의 BOM 제거 (Set.md, NextPhasePlan.md의 파일 맨 앞 BOM은 정상 범위)

### 0-3. Part 번호·헤딩 구조 정리 [실측 + 판단]
- [ ] **Graph.md**: "(보완)" 블록(Part 7~13)을 원래 Part로 병합. Part 11, 12는 접미사 없이 같은 제목이 두 번 나옴. 병합 후 Part 번호 중복이 없어야 함.
- [ ] **Graph.md**: 부록에 있는 `IsTree`, `IsForest`, `IsBiconnected`를 Part 5(사이클)로 이동. [판단] 부록은 비교·해설(`BFS vs DFS` 등)만 남김.
- [ ] **Hash.md**: "Part 16"이 2개. `Visualizations Placeholder` 항목 삭제 후 하나로 합침.
- [ ] **Memory.md**: Part 3, 5, 6 결번. 원본 목차를 알 수 없으므로 다음 구성으로 **확정** [판단 → 확정]:
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
- [ ] **Part 5**: `DetectCycle()` — 현재 DFS/BFS/UnionFind 3개 변형만 있음. [판단] 래퍼 함수보다 Part 서두 개요 설명 항목으로 대체 권장.
- [ ] **Part 7**: `MinimumSpanningTree()` (Kruskal/Prim/Boruvka를 고르는 통합 인터페이스)
- [ ] **Part 8**: `UnionSet()`
- [ ] **Part 14 특수 그래프** (현재 `BipartiteGraph`, `DirectedGraph`만 있음): `UndirectedGraph()`, `WeightedGraph()`, `UnweightedGraph()`, `CompleteGraph()`, `SparseGraph()`, `DenseGraph()`, `PlanarGraph()`
- [ ] **Part 15 그래프 모델** (현재 `PageRank`만 있음): `RandomGraph()`, `GridGraph()`, `TreeGraph()`, `HypercubeGraph()`, `ScaleFreeGraph()`, `SmallWorldGraph()`
- [ ] **Part 16 응용 (Part 전체 없음)**: `DependencyGraph()`, `KnowledgeGraph()`, `SocialNetworkGraph()`, `CallGraph()`, `StateTransitionGraph()`, `ControlFlowGraph()`, `DataFlowGraph()`, `BayesianNetwork()`, `NeuralGraph()`
- [ ] [판단] `PageRank()`는 모델이 아니라 알고리즘이므로 Part 15에서 Part 16(응용)으로 이동
- [ ] **부록**: `Dijkstra vs A*` 비교 설명 (미작성)

### A-2. Tree.md [실측 + 판단]
- [ ] **Part 7**: `Recolor()`, `DoubleBlack()` — 독립 항목 없음 (현재 `RBInsert/RBDelete/FixViolation`만 있음, 그나마 `RBDelete`와 `FixViolation`은 자리표시)
- [ ] **Part 8 힙**: 현재 `BinaryHeap()` 하나에 `heapifyDown`이 들어 있을 뿐, `HeapInsert()`, `HeapDelete()`, `Heapify()`, `BuildHeap()`, `HeapSort()` 독립 항목 없음. [확정] Queue.md Part 5에 `PushHeap/PopHeap/Heapify/BuildHeap/HeapSort`가 이미 구현돼 있으므로 정본은 Queue.md. Tree.md의 5개 항목은 "완전이진트리의 배열 표현" 관점의 링크형 요약으로 쓴다(섹션 3 정책). 힙 변형(Phase C의 Fibonacci·Binomial·Pairing 등)은 Tree.md Part 8의 정본 항목으로 추가.
- [ ] **Part 9**: `GeneralTree()`, `NaryTree()` (Part 9가 Trie 계열만 있음)
- [ ] **Part 10**: `SuffixArray()` — 정본은 String.md Part 9이므로 Tree.md에는 링크형 요약으로 추가 (현재 AdvancedDataStructures.md에만 있음)
- [ ] **Part 13**: `BTree()` 독립 항목 (현재 `BPlusTree()`만 있음). 2차 계획서는 "BTree 존재"라고 했으나 Tree.md에서는 확인되지 않음.
- [ ] **부록**: `BST vs AVL vs Red-Black` 비교 설명

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

- [ ] 현재 Part 1의 해설형 항목(`왜 Java HashMap은 TreeBin으로 바뀌는가?` 등)은 구현 항목이 아니므로 [판단] Part 10 또는 부록으로 이전

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
- [ ] `MemoryPool()` — 저장소 전체에 없음 (2차 계획서 Part 6)
- [ ] `PushFrame()` — `PopFrame()`만 있고 짝이 없음 (Part 2)
- [ ] `CompareAndSwap()`, `MemoryBarrier()` — Memory.md에 없음 (Part 11, `CompareAndSwap`은 AdvancedDataStructures.md에만 있음)
- [ ] Part 3, 5, 6 결번 처리: Part 3 스택 메모리 / Part 5 포인터와 참조 / Part 6 할당기로 확정 (Phase 0-3). `Pointer`, `Reference`, `SmartPointer`, `Aliasing`은 Part 5 신규 항목

---

## 🔧 Phase B: 자리표시 코드 실구현

**원칙 [판단]**: 신규 작성하는 항목(Phase A)은 처음부터 `assert(true)` / `assert(1 == 1)` 자리표시를 쓰지 않고, 실제로 동작하는 코드와 의미 있는 `assert`를 넣는다. 복잡도 주석도 템플릿 복사(`O(1)`)가 아닌 실제 값을 쓴다.

### B-1. Hash.md · String.md (100%)
- Phase A-3, A-4의 신규 작성과 함께 진행. 기존 33개 블록은 전부 자리표시이므로 재작성.

### B-2. Memory.md (104/104, 100%) [판단: 이 저장소에서 우선 구현 가치가 가장 높음]
- README 특색: "메모리 상태 변화를 단계별로 시각화"가 이 파일의 차별점인데 현재는 시각화에 쓸 구현이 전혀 없음.
- [ ] 1순위: `malloc()`, `FreeList()`, `SlabAllocator()`, `BuddyAllocator()`, `ArenaAllocator()`, `ObjectPool()`, `MemoryPool()` (할당·해제 후 힙 상태를 출력하는 시뮬레이션)
- [ ] 2순위: `MarkSweep()`, `CopyingGC()`, `GenerationalGC()`, `PageTable()`, `TLBLookup()`, `AddressTranslation()`
- [ ] 3순위: `AtomicOperation()`, `CompareAndSwap()`, `MemoryBarrier()`, `ZGC()`, `EscapeAnalysis()`, `TransactionalMemory()` (2차 계획서 B-3)

### B-3. AdvancedDataStructures.md (110/112, 98%)
- [ ] 1순위 [판단]: README가 "책의 정체성"으로 꼽은 6개 — `HNSW()`, `FAISSIndex()`, `LSMTree()`, `AdaptiveRadixTree()`, `LearnedIndex()`, `CacheObliviousBTree()`
- [ ] 2순위 (2차 계획서 B-5): `BitVector()`, `Rank()`, `Select()`, `WaveletTree()`, `FMIndex()`, `BallTree()`, `BVHTree()`, `IVFIndex()`, `ProductQuantization()`
- [ ] 3순위 [판단]: 실무 빈도가 높은 `BloomFilter()`, `CountMinSketch()`, `HyperLogLog()`, `SkipList()`, `LockFreeQueue()`

### B-4. PathFinding.md (89/102, 87%)
- [ ] Part 5: `JumpPointSearch()`, `ThetaStar()`, `HierarchicalPathFinding()`
- [ ] Part 6: `DStar()`, `DStarLite()`, `LifelongPlanningAStar()`
- [ ] Part 7: `YenAlgorithm()`, `EppsteinAlgorithm()`
- [ ] Part 11: `RapidlyExploringRandomTree()`, `RRTStar()`, `ProbabilisticRoadMap()`
- [ ] Part 16: `MonteCarloTreeSearch()`, `AntColonyOptimization()`
- [ ] [판단] Part 13(`OSPF`, `RIP`, `BGPPathSelection`) 등 외부 시스템 의존 항목은 실제 구현이 아니라 **축약 시뮬레이션**으로 충분

### B-5. Set.md (59/102, 57%) — Phase 0-1 완료 후 진행
- 자리표시 항목: `IsSuperset`, `LinkedSet`, `UnionByRank`, `PathCompression`, `ConnectedComponents`, `CombinationWithReplacement`, `Backtracking`, `BitMaskEnumeration`, `MeetInTheMiddle`, `SubsetSum`, `KnapsackSubset`, `BinaryRelation`, `EquivalenceRelation`, `Partition`, `EquivalenceClass`, `QuotientSet`, `Distinct`, `Projection`, `Selection`, `Join`, `GroupBy`, `DuplicateElimination`, `PostingList`, `JaccardSimilarity`, `MinHash`, `LocalitySensitiveHashing`, `FeatureSet`, `VocabularySet`, `CandidateSet`, `ConstraintSet`, `BloomFilter`~`QuotientFilter`, `ConcurrentSet`~`LearnedSetIndex`, `DynamicConnectivity`, 부록 해설
- [ ] [확정] `UnionByRank/PathCompression/ConnectedComponents`는 Graph.md Part 8이 정본(실구현 있음)이므로 Set.md는 집합 관점의 링크형 요약(15줄 이내 + `→ 정본`). `BloomFilter` 계열은 AdvancedDataStructures.md Part 3이 정본, `MinHash/LocalitySensitiveHashing`은 Hash.md Part 14가 정본, `SkipListSet`은 List.md Part 10이 정본. 나머지 자리표시 항목(`Join`, `GroupBy`, `SubsetSum` 등)은 Set.md에서 직접 구현.

### B-6. Tree.md (38/91, 41%) — 대부분 Part 11~16
- [ ] Part 7: `RBDelete()`, `FixViolation()`
- [ ] Part 9~10: `RadixTree()`, `SuffixTree()`, `PatriciaTrie()`
- [ ] Part 11~12: `KDTree()`, `QuadTree()`, `Octree()`, `BSPTree()`, `RangeQuery()`, `LazyPropagation()`, `RangeUpdate()`
- [ ] Part 13: `BPlusTree()`, `SplayTree()`, `Treap()`, `CartesianTree()`, `ScapegoatTree()`
- [ ] Part 14~16: `PersistentTree()`, `ImmutableTree()`, `FingerTree()`, `RootingTree()`, `TreeDP()`, `HeavyLightDecomposition()`, `CentroidDecomposition()`, `BinaryLifting()`, `EulerTourTechnique()`, `ExpressionTree()`, `SyntaxTree()`, `ParseTree()`, `DecisionTree()`, `MerkleTree()`, `IntervalTree()`, `RopeTree()`, `RTree()`, `VanEmdeBoasTree()`
- [ ] 부록 3개 (`트리 순회의 재귀와 반복 구현`, `Binary Tree vs BST`, `Segment Tree vs Fenwick Tree`)
- [ ] [확정] `HeavyLightDecomposition`, `CentroidDecomposition`, `EulerTour`는 Tree.md가 정본이고 Graph.md는 링크형 요약(`EulerTour`는 양쪽 모두 실구현이므로 유지하고 상호 링크). `RopeTree`는 String.md Part 4, `FingerTree/PersistentTree`는 AdvancedDataStructures.md Part 1·4가 정본이므로 Tree.md는 링크형 요약. 구간·공간·균형 트리는 Tree.md가 정본이고 AdvancedDataStructures.md가 링크형 요약(섹션 3 표).

### B-7. Graph.md (15/78), List.md (22/78), Queue.md (4/53)
- [ ] **Graph.md**: `AStar()`, `JumpPointSearch()`, `Johnson()`, `GreedyBestFirstSearch()`, `ThetaStar()`, `PushRelabel()`, `MinCostMaxFlow()`, `BlossomAlgorithm()`, `Gabow()`, `HeavyLightDecomposition()`, `CentroidDecomposition()`, 해설 `BFS vs DFS`, `DAG가 중요한 이유`, `Prim vs Kruskal`, `Union-Find 시간복잡도`
- [ ] **List.md**: `SentinelNode()`, `XORLinkedList()`, `Iterator()`, `Free()`, `Zip()`, `SkipList()`, `Rope()`, `UnrolledLinkedList()`, `GapBuffer()`, `PieceTable()`, `FingerTree()`, `PersistentList()`, `ImmutableList()`, 부록 해설 9개
- [ ] **Queue.md**: `CircularBuffer()`, `MichaelScottQueue()`, `PersistentQueue()`, `ImmutableQueue()`
- [ ] [확정] PathFinding.md ↔ Graph.md 겹침은 성격별로 나눔: 휴리스틱 탐색(`AStar/JumpPointSearch/ThetaStar/GreedyBestFirstSearch`)은 PathFinding.md가 정본, 최단 경로·일반 탐색(`Johnson`, `SPFA`, `BidirectionalSearch`, `IDAStar` 등)은 Graph.md가 정본. 비정본 쪽은 링크형 요약.
- [ ] [확정] List.md의 `SkipList` 정본, `Rope/GapBuffer/PieceTable`은 String.md Part 4가 정본(List.md는 링크형 요약), `FingerTree/PersistentList/ImmutableList`는 AdvancedDataStructures.md가 정본(List.md는 링크형 요약)

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
- [ ] 실구현(Phase B) 시 실제 복잡도로 교체. 구현 전까지는 [판단] 틀린 값을 두기보다 `TBD`로 표시하는 편이 안전.

### D-2. 문서화
- [ ] 통합 README.md 구성: 전체 자료구조 카테고리별 Index 페이지 (현재 README는 저장소 철학과 특색 메모만 있음)
- [ ] 상호 참조: 섹션 3의 정본 표에 있는 모든 "링크형 요약" 항목에 `→ 정본: X.md Part N` 문구 추가 (Graph.md ↔ PathFinding.md, Tree.md ↔ AdvancedDataStructures.md, Tree.md ↔ Queue.md(힙), Set.md ↔ Graph.md(Union-Find) ↔ AdvancedDataStructures.md(Bloom Filter) 등)
- [ ] Mermaid 다이어그램: Red-Black Tree 회전, 해시 충돌 해결, 그래프 BFS/DFS 과정

### D-3. 자동 검증 [판단]
`audit_result.txt`는 수동 스냅샷이라 이미 현재 상태와 어긋났으므로 스크립트로 대체합니다.
- [ ] 점검 항목: 헤딩 계층(`#`/`##`/`###`), 빈 코드 블록, 자리표시 코드 비율, 중복 Part·중복 헤딩, 파일 중간 BOM, 인코딩 손상(깨진 한자 연속·U+FFFD)
- [ ] 코드 블록을 추출해 `g++ -std=c++17`로 컴파일하고 실행해 `assert` 통과 여부 확인 (이번 점검에서는 하지 않음)
- [ ] 양쪽 모두 실구현인 11개 중복(섹션 3)의 코드가 서로 어긋나지 않는지 비교
- [ ] `audit_result.txt` 삭제 또는 "과거 스냅샷" 표기

---

## 📋 남은 열린 항목

이전 판의 결정 필요 항목 5개는 모두 섹션 3에서 확정됐습니다. 남은 것은 다음 두 가지입니다.

1. **제안 목차의 검토**: 원본 목차를 모르므로 A-3(Hash), A-4(String), A-5(Memory)의 [판단] 표시 Part는 작업하면서 읽어보고 조정. 원본 `*(2).md`가 발견되면 그 기준으로 교체.
2. **Set.md 추정 복원 제목**: Phase 0-1의 Part 제목은 역변환으로 추정한 것이므로, 복구 후 한 번 확인.

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
```

순서의 근거:
- Set.md는 지금 읽을 수 없으므로 다른 작업보다 먼저 복구해야 함.
- Hash.md는 Part 16개 중 14개(Part 2~15), String.md는 17개 중 16개(Part 2~17)가 없는 상태로, 2차 계획서의 우선순위(Graph·Tree 먼저)와 달리 **누락 규모가 가장 큼**. Graph·Tree는 남은 누락이 소수의 항목임.
- 신규 작성은 자리표시 없이 실구현으로 해야 Phase B의 작업량이 늘지 않음.
