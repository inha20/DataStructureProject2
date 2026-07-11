# Data Structure Project 2: Next Iterations Plan (2차 개정판)

이 계획서는 과거 버전(`*(2).md`)과 현재 버전(`*.md`) 간의 전수 감사 결과를 기반으로 **실제 미구현 항목만 정확하게 반영**한 수정판입니다.

우선순위: **Phase A (구현 복구) → Phase B (스텁 실구현) → Phase C (구조/품질 개선)**

---

## 📋 전체 파일 감사 현황

| 파일 | 현재 구현도 | 누락 파트 수 | 긴급도 |
|------|------------|-------------|--------|
| Stack.md | ✅ 양호 | 0 | 낮음 |
| Queue.md | ✅ 양호 | 0 | 낮음 |
| List.md | ✅ 양호 | 0 | 낮음 |
| Memory.md | ⚠️ 스텁 다수 | 0 (파트 존재) | 중간 |
| PathFinding.md | ⚠️ 스텁 다수 | 0 (파트 존재) | 중간 |
| String.md | ⚠️ 스텁 다수 | 0 (파트 존재) | 중간 |
| Hash.md | 🔴 스텁 + 파트 누락 | Part 16 | 높음 |
| Set.md | 🔴 함수 누락 | union() 소문자 | 높음 |
| Graph.md | 🔴 파트 대거 누락 | Part 5~16 | 🚨 최우선 |
| Tree.md | 🔴 파트 대거 누락 | Part 6~16 | 🚨 최우선 |
| AdvancedDataStructures.md | ⚠️ 스텁 다수 | 0 (파트 존재) | 중간 |

---

## 🚨 Phase A: 목차에서 완전히 누락된 파트 복구 (최우선)

아래 항목들은 과거 버전 목차에는 분명히 존재하나 현재 파일에서 해당 파트 자체가 통째로 빠진 경우입니다. 단순 스텁이 아닌 목차 자체의 누락이므로 최우선 복구 대상입니다.

### A-1. Graph.md — 누락 파트 복구 (Part 5 ~ Part 16)

현재 Graph.md에는 Part 1~4(기초, 표현, 탐색, 연결성)만 온전하고, 이후가 모두 없거나 불완전합니다.

- [ ] **Part 5. 사이클:** `DetectCycle()`, `DetectCycleDFS()`, `DetectCycleBFS()`, `DetectCycleUnionFind()`, `IsTree()`, `IsForest()`, `IsBiconnected()`
- [ ] **Part 7. 최소 신장 트리 (보완):** `Boruvka()`, `ReverseDelete()`, `MinimumSpanningTree()` 추가 (Kruskal/Prim 존재)
- [ ] **Part 8. 분리 집합:** `MakeSet()`, `FindSet()`, `UnionSet()`, `UnionByRank()`, `PathCompression()`
- [ ] **Part 9. 최단 경로 (보완):** `Johnson()`, `SPFA()` 추가 (Dijkstra/BellmanFord/Floyd 존재)
- [ ] **Part 10. 길찾기 (보완):** `GreedyBestFirstSearch()`, `BidirectionalSearch()`, `IDDFS()`, `IDAStar()`, `ThetaStar()` 추가 (AStar/JPS 존재)
- [ ] **Part 11. 네트워크 플로우:** `FordFulkerson()`, `EdmondsKarp()`, `Dinic()`, `PushRelabel()`, `MinCostMaxFlow()`
- [ ] **Part 12. 매칭:** `BipartiteMatching()`, `HungarianAlgorithm()`, `HopcroftKarp()`, `BlossomAlgorithm()`
- [ ] **Part 13. 그래프 분석 (보완):** `Kosaraju()`, `Gabow()`, `EulerTour()`, `HeavyLightDecomposition()`, `CentroidDecomposition()` (Tarjan 존재)
- [ ] **Part 14. 특수 그래프:** 이분 그래프, 완전 그래프, 평면 그래프, DAG 개념 및 판별 함수
- [ ] **Part 15. 그래프 모델:** `RandomGraph()`, `GridGraph()`, `ScaleFreeGraph()`, `SmallWorldGraph()` 등
- [ ] **Part 16. 응용:** `PageRank()`, `KnowledgeGraph()`, `DependencyGraph()`, `NeuralGraph()` 등
- [ ] **부록:** BFS vs DFS, Dijkstra vs A*, Prim vs Kruskal 비교 설명

---

### A-2. Tree.md — 누락 파트 복구 (Part 6 ~ Part 16)

현재 Tree.md에는 Part 1~5(기초, 이진트리, 순회, 탐색, BST)와 일부 Part 8(힙)만 온전합니다.

- [ ] **Part 6. AVL 트리:** `AVLDelete()`, `BalanceFactor()`, `RotateLeft()`, `RotateRight()`, `RotateLeftRight()`, `RotateRightLeft()` — 현재 AVLInsert 존재하나 삭제/회전 스텁
- [ ] **Part 7. Red-Black Tree:** `RBInsert()`, `RBDelete()`, `FixViolation()`, `Recolor()`, `DoubleBlack()` — 현재 클래스 선언만 존재, insertFixup/deleteFixup/rotate 전부 빈 함수
- [ ] **Part 9. 특수 트리 (보완):** `TrieDelete()`, `RadixTree()` (TrieInsert/Search 존재)
- [ ] **Part 10. 문자열 자료구조:** `SuffixTree()`, `PatriciaTrie()` (SuffixArray/SuffixTrie 존재)
- [ ] **Part 11. 공간 자료구조:** `KDTree()`, `QuadTree()`, `Octree()`, `BSPTree()` (SegmentTree/FenwickTree 존재)
- [ ] **Part 12. 구간 연산:** `RangeQuery()`, `LazyPropagation()`, `RangeUpdate()`
- [ ] **Part 13. 고급 트리:** `BPlusTree()`, `SplayTree()`, `Treap()`, `CartesianTree()`, `ScapegoatTree()` (BTree 존재)
- [ ] **Part 14. 함수형 자료구조:** `PersistentTree()`, `ImmutableTree()`, `FingerTree()`
- [ ] **Part 15. 그래프 확장:** `RootingTree()`, `TreeDP()`, `HeavyLightDecomposition()`, `CentroidDecomposition()`, `BinaryLifting()`, `EulerTourTechnique()`
- [ ] **Part 16. 특수 목적:** `ExpressionTree()`, `SyntaxTree()`, `ParseTree()`, `DecisionTree()`, `MerkleTree()`, `IntervalTree()`, `RopeTree()`, `RTree()`, `VanEmdeBoasTree()`
- [ ] **부록:** Binary Tree vs BST, BST vs AVL vs Red-Black, Segment Tree vs Fenwick Tree 비교 설명

---

### A-3. Hash.md — Part 16 복구

- [ ] **Part 16. 해시 성능 시각화:** `CollisionVisualization()`, `BucketDistribution()`, `ProbeSequence()`, `ResizeAnimation()`, `ChainGrowth()`, `ClusterFormation()`, `AvalancheEffect()`, `HashQualityEvaluation()`, `CacheLocality()`, `MemoryLayout()`

---

### A-4. Set.md — 소문자 union() 확인

- [ ] Set.md의 `union()` 소문자 버전 — Python set 메서드 스타일 예시 코드 추가 여부 확인

---

## 🔧 Phase B: 스텁 코드 실구현

아래 항목들은 목차에 파트가 존재하지만 내부 구현이 `assert(true);` 또는 의사코드 주석뿐인 스텁 상태입니다.

### B-1. String.md
- [ ] Part 6: `RabinKarp()`, `BoyerMoore()`, `Horspool()`, `SundaySearch()`
- [ ] Part 7: `ZAlgorithm()`, `LongestRepeatedSubstring()`
- [ ] Part 9: `SuffixArray()`, `BuildSuffixArray()`, `LCPArray()`, `SuffixAutomaton()`
- [ ] Part 10 Rolling Hash: `PolynomialRollingHash()`, `RabinFingerprint()`, `SubstringHash()`, `LongestCommonSubstring()`
- [ ] Part 11: `LZW()`, `BurrowsWheelerTransform()`, `MoveToFront()`
- [ ] Part 12: `DamerauLevenshtein()`, `LongestCommonSubstringDP()`
- [ ] Part 17 AI/NLP: `BytePairEncoding()`, `WordPiece()`, `SentencePiece()`, `TokenizeLLM()`, `EmbeddingLookup()`
- [ ] 부록: KMP는 왜 O(n)인가, Trie vs HashMap, Suffix Array vs Suffix Tree

### B-2. Hash.md
- [ ] Part 3: `RobinHoodHashing()`, `CuckooHashing()`, `HopscotchHashing()`, `CoalescedHashing()`
- [ ] Part 4: `PerfectHash()`, `MinimalPerfectHash()`
- [ ] Part 5: `PolynomialRollingHash()`, `RabinFingerprint()`, `LongestCommonSubstringHash()`
- [ ] Part 7: `ConsistentHashing()`, `VirtualNode()`, `RendezvousHash()`, `Chord()`, `Kademlia()`
- [ ] Part 14: `LocalitySensitiveHashing()`, `SimHash()`, `MinHash()`, `SemanticHashing()`

### B-3. Memory.md
- [ ] Part 6: `MemoryPool()`, `SlabAllocator()`, `BuddyAllocator()`, `ArenaAllocator()`
- [ ] Part 7: `MarkSweep()`, `CopyingGC()`, `GenerationalGC()`
- [ ] Part 11: `AtomicOperation()`, `CompareAndSwap()`, `MemoryBarrier()`
- [ ] Part 16: `ZGC()`, `EscapeAnalysis()`, `TransactionalMemory()`

### B-4. PathFinding.md
- [ ] Part 5: `JumpPointSearch()`, `ThetaStar()`, `HierarchicalPathFinding()`
- [ ] Part 6: `DStar()`, `DStarLite()`, `LifelongPlanningAStar()`
- [ ] Part 7: `YenAlgorithm()`, `EppsteinAlgorithm()`
- [ ] Part 11: `RapidlyExploringRandomTree()`, `RRTStar()`, `ProbabilisticRoadMap()`
- [ ] Part 16: `MonteCarloTreeSearch()`, `AntColonyOptimization()`

### B-5. AdvancedDataStructures.md
- [ ] Part 2: `BitVector()`, `Rank()`, `Select()`, `WaveletTree()`, `FMIndex()`
- [ ] Part 5: `BallTree()`, `BVHTree()`
- [ ] Part 12: `HNSW()`, `IVFIndex()`, `FAISSIndex()`, `ProductQuantization()`
- [ ] Part 15: `AdaptiveRadixTree()`, `CacheObliviousBTree()`, `LearnedIndex()`

---

## 🏗️ Phase C: 구조/품질 개선

### C-1. 중복 항목 제거
- [ ] Hash.md: `Kademlia()` x2, `HashIndex()` x2, `LearnedHashIndex()` x2, `HashChain()` x2 → 병합/삭제
- [ ] String.md: `StringLiteral()` x2, `Detokenize()` x2 → 병합/삭제

### C-2. 복잡도 표기 추가
- [ ] AdvancedDataStructures.md: 핵심 알고리즘에 Big-O 복잡도 추가
- [ ] Memory.md: 할당기/GC 함수에 복잡도 추가

### C-3. 문서화 고도화
- [ ] 통합 README.md 구성: 전체 자료구조 카테고리별 Index 페이지 작성
- [ ] 상호 참조: Graph.md ↔ PathFinding.md, Tree.md ↔ AdvancedDataStructures.md 하이퍼링크
- [ ] Mermaid 다이어그램: Red-Black Tree 회전, 해시 충돌 해결, 그래프 BFS/DFS 과정 시각화

---

## 📅 권장 작업 순서

Phase A-1 (Graph 복구) → A-2 (Tree 복구) → A-3 (Hash Part16) → A-4 (Set 확인)
→ B-1 (String) → B-2 (Hash) → B-3 (Memory) → B-4 (PathFinding) → B-5 (ADS)
→ C-1 (중복 제거) → C-2 (복잡도 표기) → C-3 (문서화)

Graph.md와 Tree.md의 누락 파트 복구(Phase A)가 가장 시급합니다. 두 파일 모두 원래 목차의 절반 이상이 없는 상태입니다.
