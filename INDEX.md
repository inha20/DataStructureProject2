# INDEX

> 이 파일은 `python3 -I tools/gen_index.py` 가 만든다. 직접 고치지 말고 책을 고친 뒤 다시 생성한다.

## 책별 요약

| 책 | Part | 항목 | 링크형(정본이 다른 책) | GCC/Clang 확장 | POSIX | Linux 전용 | 스레드 |
|----|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| AdvancedDataStructures | 16 | 136 | 33 | 18 | 0 | 0 | 15 |
| Graph | 17 | 107 | 7 | 13 | 1 | 0 | 0 |
| Hash | 16 | 76 | 2 | 13 | 0 | 0 | 2 |
| List | 11 | 78 | 5 | 1 | 0 | 0 | 4 |
| Memory | 17 | 112 | 2 | 15 | 24 | 23 | 16 |
| PathFinding | 17 | 102 | 11 | 2 | 0 | 0 | 0 |
| Queue | 11 | 56 | 2 | 3 | 0 | 0 | 6 |
| Set | 17 | 105 | 14 | 25 | 0 | 0 | 4 |
| Stack | 10 | 50 | 2 | 4 | 1 | 0 | 4 |
| String | 18 | 68 | 2 | 6 | 0 | 0 | 1 |
| Tree | 17 | 125 | 5 | 9 | 0 | 0 | 0 |
| **합계** | 167 | 1015 | 85 | 109 | 26 | 23 | 52 |

표시: `↗File.md#N` 은 링크형 요약(정본이 File.md Part N), `[gcc]` `[posix]` `[linux]` `[threads]` 는 위 표의 이식성 표지다. POSIX·Linux 코드는 `#if` 가드로 감싸 다른 환경에서도 컴파일되고, GCC/Clang 확장을 쓰는 항목은 MSVC에서 따로 손봐야 한다.

## AdvancedDataStructures

### Part 1. Persistent Data Structures (8)

`PersistentArray`, `PersistentList`, `PersistentStack` ↗Stack#10, `PersistentQueue`, `PersistentSegmentTree`, `PersistentTrie`, `HAMT`, `RRBVector`

### Part 2. Succinct Data Structures (7)

`BitVector` [gcc], `Rank` [gcc], `Select` [gcc], `WaveletTree`, `FMIndex` ↗String#9, `SuccinctTrie`, `BitmapIndex`

### Part 3. 확률적 자료구조 (12)

`BloomFilter` [gcc], `CountingBloomFilter`, `CuckooFilter`, `QuotientFilter`, `XORFilter`, `CountMinSketch`, `HyperLogLog` [gcc], `TDigest`, `MisraGries`, `SpaceSaving`, `CountSketch`, `ReservoirSampling`

### Part 4. 문자열 자료구조 (6)

`Rope` ↗String#4, `PieceTable` ↗String#4, `GapBuffer` ↗String#4, `FingerTree`, `SuffixAutomaton` ↗String#9, `PatriciaTrie` ↗Tree#10

### Part 5. 공간 자료구조 (11)

`KDTree` ↗Tree#11, `QuadTree` ↗Tree#11, `Octree` ↗Tree#11, `RTree` ↗Tree#16, `BallTree`, `BVHTree`, `BKTree`, `VPTree`, `CoverTree`, `DCEL`, `QuadEdge`

### Part 6. 범위 질의 (8)

`SegmentTree`, `LazyPropagation` ↗Tree#12, `FenwickTree`, `SparseTable`, `IntervalTree` ↗Tree#16, `RangeTree`, `DisjointSparseTable` [gcc], `SqrtTree` [gcc]

### Part 7. 균형 트리 (7)

`AVLTree`, `RedBlackTree`, `AA Tree`, `Treap` ↗Tree#13, `SplayTree` ↗Tree#13, `ScapegoatTree` ↗Tree#13, `TangoTree` [gcc]

### Part 8. 외부 메모리 (9)

`BTree` ↗Tree#13, `BPlusTree` ↗Tree#13, `BStarTree`, `FractalTree`, `LSMTree`, `BufferTree`, `CSBPlusTree`, `BwTree` [threads], `Masstree`

### Part 9. 동시성 (11)

`LockFreeQueue` ↗Queue#10 [threads], `LockFreeStack` ↗Stack#9 [threads], `ConcurrentHashMap` ↗Hash#12 [threads], `SkipListSet` ↗List#10, `CompareAndSwap` ↗Memory#11 [threads], `HazardPointer` [threads], `ChaseLevDeque` [threads], `Disruptor` [threads], `RCU` [threads], `Seqlock` [threads], `EpochBasedReclamation` [threads]

### Part 10. 분산 시스템 (7)

`ConsistentHashing` ↗Hash#7, `DistributedHashTable`, `Chord` ↗Hash#7, `Kademlia` ↗Hash#7 [gcc], `MerkleTree` ↗Tree#16, `MerklePatriciaTrie`, `CRDT`

### Part 11. GPU 자료구조 (5)

`GPUBVH` [gcc], `CUDASparseMatrix`, `ParallelPrefixSum` [threads], `ParallelHashTable` [threads], `WarpQueue` [gcc][threads]

### Part 12. AI와 데이터 (8)

`VectorIndex`, `HNSW`, `IVFIndex`, `ProductQuantization`, `KDTreeKNN`, `BallTreeKNN`, `AnnoyIndex`, `FAISSIndex`

### Part 13. 데이터베이스 (6)

`SkipList` ↗List#10, `MemTable`, `SSTable`, `WriteAheadLog`, `BTreeIndex`, `HashIndex` ↗Hash#9

### Part 14. 운영체제 (5)

`BuddyAllocator` ↗Memory#6, `SlabAllocator` ↗Memory#6, `RadixTree`, `XArray` [gcc], `PageTable` ↗Memory#9

### Part 15. 최신 연구 (14)

`LearnedIndex`, `LearnedHash` ↗Hash#15, `AdaptiveRadixTree`, `CacheObliviousBTree` [gcc], `FusionTree` [gcc], `vanEmdeBoasTree` [gcc], `XFastTrie`, `YFastTrie`, `EliasFano` [gcc], `CompressedSuffixArray` [gcc], `DynamicWaveletTree`, `PackedMemoryArray`, `CacheAwareBTree`, `LearnedBloomFilter`

### 부록: 부록 (12)

`Cache-Aware vs Cache-Oblivious`, `Immutable vs Persistent`, `Lock-Free vs Wait-Free` [threads], `Online vs Offline 자료구조`, `Static vs Dynamic 자료구조`, `Internal Memory vs External Memory`, `Exact vs Approximate 자료구조` [gcc], `CPU 자료구조 vs GPU 자료구조`, `LSM Tree가 SSD에 적합한 이유`, `벡터 데이터베이스는 왜 HNSW를 사용하는가?`, `현대 데이터베이스가 B+Tree와 LSMTree를 함께 사용하는 이유`, `생성형 AI 시대의 자료구조`

## Graph

### Part 1. 그래프의 기초 (10)

`CreateGraph`, `AddVertex`, `RemoveVertex`, `AddEdge`, `RemoveEdge`, `VertexCount`, `EdgeCount`, `Degree`, `InDegree`, `OutDegree`

### Part 2. 그래프 표현 (6)

`AdjacencyMatrix` [gcc], `AdjacencyList`, `EdgeList`, `IncidenceMatrix`, `CompressedSparseRow`, `CompressedSparseColumn`

### Part 3. 그래프 탐색 (5)

`BreadthFirstSearch`, `DepthFirstSearch`, `IterativeDFS`, `RecursiveDFS`, `GraphTraversal`

### Part 4. 연결성 (6)

`ConnectedComponents`, `StronglyConnectedComponents`, `WeaklyConnectedComponents`, `IsConnected`, `ArticulationPoint`, `Bridge`

### Part 5. 사이클 (7)

`DetectCycle`, `DetectCycleDFS`, `DetectCycleBFS` [gcc], `DetectCycleUnionFind`, `IsTree` [gcc], `IsForest`, `IsBiconnected`

### Part 6. 위상 구조 (3)

`KahnAlgorithm`, `DFSBasedTopologicalSort`, `LongestPathInDAG`

### Part 7. 최소 신장 트리 (5)

`Kruskal` [gcc], `Prim` [gcc], `Boruvka` [gcc], `ReverseDelete` [gcc], `MinimumSpanningTree`

### Part 8. 서로소 집합 (5)

`MakeSet`, `FindSet`, `UnionSet`, `UnionByRank`, `PathCompression`

### Part 9. 최단 경로 (6)

`Dijkstra`, `BellmanFord`, `FloydWarshall`, `Johnson`, `SPFA`, `DialAlgorithm`

### Part 10. 길찾기 (7)

`AStar` ↗PathFinding#4, `JumpPointSearch` ↗PathFinding#5, `GreedyBestFirstSearch` ↗PathFinding#4, `BidirectionalSearch`, `IDDFS`, `IDAStar`, `ThetaStar` ↗PathFinding#5

### Part 11. 네트워크 플로우 (5)

`FordFulkerson`, `EdmondsKarp`, `Dinic`, `PushRelabel`, `MinCostMaxFlow`

### Part 12. 매칭 (4)

`BipartiteMatching` [gcc], `HungarianAlgorithm`, `HopcroftKarp`, `BlossomAlgorithm` [gcc]

### Part 13. 그래프 분석 (6)

`Tarjan`, `Kosaraju`, `Gabow`, `EulerTour`, `HeavyLightDecomposition` ↗Tree#15, `CentroidDecomposition` ↗Tree#15

### Part 14. 특수 그래프 (11)

`BipartiteGraph`, `DirectedGraph`, `UndirectedGraph`, `WeightedGraph`, `UnweightedGraph`, `CompleteGraph` [gcc], `SparseGraph`, `DenseGraph`, `PlanarGraph`, `Multigraph`, `Hypergraph`

### Part 15. 그래프 모델 (6)

`RandomGraph`, `GridGraph`, `TreeGraph`, `HypercubeGraph` [gcc], `ScaleFreeGraph`, `SmallWorldGraph`

### Part 16. 응용 (10)

`DependencyGraph`, `KnowledgeGraph`, `SocialNetworkGraph`, `CallGraph`, `StateTransitionGraph`, `ControlFlowGraph`, `DataFlowGraph`, `BayesianNetwork` [posix], `NeuralGraph`, `PageRank`

### 부록: 부록 (5)

`BFS vs DFS`, `DAG가 중요한 이유`, `Prim vs Kruskal` [gcc], `Dijkstra vs A*` ↗PathFinding#부록, `Union-Find 시간복잡도` [gcc]

## Hash

### Part 1. 해시의 기초 (7)

`CreateHashTable`, `Insert`, `Search`, `Delete`, `Resize`, `Rehash`, `LoadFactor`

### Part 2. 해시 함수 (7)

`DivisionMethod` [gcc], `MultiplicationMethod`, `UniversalHashing`, `FNV`, `MurmurHash` [gcc], `xxHash`, `SipHash` [gcc]

### Part 3. 충돌 해결 (9)

`Chaining`, `OpenAddressing`, `LinearProbing`, `QuadraticProbing`, `DoubleHashing`, `RobinHoodHashing`, `CuckooHashing`, `HopscotchHashing`, `CoalescedHashing`

### Part 4. 완전 해시 (2)

`PerfectHash`, `MinimalPerfectHash`

### Part 5. 롤링 해시 (3)

`PolynomialRollingHash` [gcc], `RabinFingerprint`, `LongestCommonSubstringHash` [gcc]

### Part 6. 해시 컨테이너 (4)

`HashMap`, `LinkedHashMap`, `Multimap`, `BiMap`

### Part 7. 분산 해시 (6)

`ConsistentHashing`, `VirtualNode`, `RendezvousHash`, `Chord`, `Kademlia` [gcc], `Consistent Hashing이 분산 시스템에서 중요한 이유`

### Part 8. 암호학적 해시 (5)

`MD5`, `SHA256`, `HMAC`, `MerkleDamgard`, `암호학적 해시와 일반 해시의 차이`

### Part 9. DB 해시 (4)

`HashIndex`, `HashJoin`, `ExtendibleHashing`, `LinearHashing`

### Part 10. OS·런타임 구현 (6)

`왜 Java HashMap은 TreeBin으로 바뀌는가?`, `Python dict의 구현 원리`, `C++ unordered_map의 구조`, `Redis Dictionary 구조`, `LRUCache`, `LFUCache`

### Part 11. 보안 (2)

`HashDoS` [gcc], `Salting`

### Part 12. 동시성 (2)

`ConcurrentHashMap` [threads], `LockFreeHashTable` [threads]

### Part 13. 확률적 구조 (3)

`BloomFilter` ↗AdvancedDataStructures#3 [gcc], `CountMinSketch` ↗AdvancedDataStructures#3, `Bloom Filter는 왜 오탐(False Positive)만 발생하는가?`

### Part 14. 유사도 해시 (4)

`LocalitySensitiveHashing`, `SimHash` [gcc], `MinHash` [gcc], `SemanticHashing`

### Part 15. 최신 연구 (2)

`SwissTable` [gcc], `LearnedHash`

### Part 16. 해시 성능 시각화 (10)

`CollisionVisualization`, `BucketDistribution`, `ProbeSequence` [gcc], `ResizeAnimation`, `ChainGrowth`, `ClusterFormation`, `AvalancheEffect`, `HashQualityEvaluation`, `CacheLocality`, `MemoryLayout` [gcc]

## List

### Part 1. 리스트의 기초 (10)

`CreateList`, `Traverse`, `Search`, `Insert`, `Delete`, `Update`, `Reverse`, `Copy`, `Swap`, `Clear`

### Part 2. 배열 리스트 (9)

`DynamicArray`, `Resize`, `ShiftLeft`, `ShiftRight`, `InsertAt`, `DeleteAt`, `BinarySearch`, `LowerBound`, `UpperBound`

### Part 3. 연결 리스트 (11)

`PushFront`, `PushBack`, `PopFront`, `PopBack`, `InsertAfter`, `InsertBefore`, `RemoveNode`, `FindMiddle`, `DetectCycle`, `MergeLists`, `SplitList`

### Part 4. 리스트 알고리즘 (6)

`BubbleSort`, `SelectionSort`, `InsertionSort`, `MergeSort`, `QuickSort`, `StablePartition`

### Part 5. 투 포인터 (4)

`TwoPointers`, `SlidingWindow`, `PrefixSum`, `DifferenceArray`

### Part 6. 연결리스트 심화 (5)

`DummyNode`, `SentinelNode`, `CircularList`, `DoublyLinkedList`, `XORLinkedList`

### Part 7. 반복자 (5)

`Iterator`, `Begin`, `End`, `Next`, `Prev`

### Part 8. 메모리 (6)

`ShallowCopy`, `DeepCopy`, `Move`, `Alloc`, `Free`, `GarbageCollection`

### Part 9. 함수형 리스트 (5)

`Map`, `Filter`, `Reduce`, `Zip`, `Flatten`

### Part 10. 학사과정을 넘어 (8)

`SkipList`, `Rope` ↗String#4, `UnrolledLinkedList`, `GapBuffer` ↗String#4, `PieceTable` ↗String#4, `FingerTree` ↗AdvancedDataStructures#4, `PersistentList` ↗AdvancedDataStructures#1, `ImmutableList`

### 부록: 마지막 부록 (9)

`ArrayList vs LinkedList`, `Cache Locality`, `Amortized Analysis` [gcc], `Iterator Invalidation`, `Memory Fragmentation`, `False Sharing` [threads], `Lock-Free Linked List` [threads], `Concurrent List` [threads], `Copy-on-Write List` [threads]

## Memory

### Part 1. 메모리의 기초 (4)

`CreateMemory` [gcc], `Alignment`, `Padding`, `MemoryDump`

### Part 2. 프로세스 메모리 (4)

`TextSegment` [linux], `DataSegment` [posix][linux][threads], `EnvironmentVariable` [posix][linux], `CommandLineArgument`

### Part 3. 스택 메모리 (8)

`PushFrame`, `PopFrame`, `CallFunction`, `ReturnFunction` [gcc], `LocalVariable`, `StackFrame` ↗Stack#8 [gcc], `StackOverflow` ↗Stack#10 [gcc][posix][linux], `TailCallOptimization` [gcc]

### Part 4. 힙 메모리 (3)

`malloc`, `new`, `PlacementNew`

### Part 5. 포인터와 참조 (4)

`Pointer`, `Reference`, `SmartPointer` [threads], `Aliasing`

### Part 6. 메모리 할당기 (6)

`MemoryPool`, `ObjectPool`, `FreeList`, `SlabAllocator`, `BuddyAllocator`, `ArenaAllocator`

### Part 7. 가비지 컬렉션 (7)

`MarkSweep`, `MarkCompact`, `CopyingGC`, `GenerationalGC`, `ReferenceCountingGC`, `IncrementalGC`, `ConcurrentGC` [threads]

### Part 8. 캐시 (6)

`CacheLine` [gcc][posix][linux], `CacheHit`, `CacheMiss`, `CacheFriendlyTraversal`, `CacheBlocking`, `FalseSharing` [threads]

### Part 9. 가상 메모리 (8)

`VirtualAddress`, `PhysicalAddress` [gcc], `AddressTranslation`, `Paging` [gcc], `PageTable`, `PageFault` [posix][linux], `TLBLookup`, `MemoryMapping` [posix][linux]

### Part 10. 메모리 보호 (6)

`ReadOnlyMemory` [posix][linux], `ExecuteOnlyMemory` [gcc][posix][linux], `MemoryProtection` [posix][linux], `StackCanary`, `ASLR` [posix][linux], `DEP` [posix][linux]

### Part 11. 병렬 메모리 (5)

`AtomicOperation` [threads], `CompareAndSwap` [gcc][threads], `MemoryBarrier` [threads], `AcquireRelease` [threads], `SequentialConsistency` [threads]

### Part 12. 메모리 분석 (7)

`MemoryLeak` [gcc], `DanglingPointer`, `WildPointer`, `DoubleFree` [posix][linux], `UseAfterFree` [posix][linux], `BufferOverflow`, `HeapCorruption` [posix][linux]

### Part 13. 파일과 메모리 (4)

`MemoryMappedFile` [posix], `SharedMemory` [posix][linux], `CopyOnWrite` [posix][threads], `ZeroCopy` [posix][linux][threads]

### Part 14. 운영체제 (5)

`ProcessMemory` [posix][linux], `ThreadLocalStorage` [threads], `KernelMemory` [gcc][posix][linux], `UserMemory` [posix][linux], `NUMAMemory`

### Part 15. 현대 시스템 (6)

`GPUMemory`, `UnifiedMemory`, `PersistentMemory`, `HugePage` [posix][linux], `RDMA`, `MemoryCompression`

### Part 16. 연구 주제 (12)

`GarbageFirstGC`, `ZGC`, `ShenandoahGC` [threads], `RegionBasedMemory`, `EscapeAnalysis`, `OwnershipTypeSystem`, `PersistentHeap` [threads], `TransactionalMemory` [threads], `CapabilityPointer`, `CHERIArchitecture`, `MemoryTagging`, `HardwareMemorySafety`

### 부록: 부록 (17)

`Stack vs Heap` [gcc][posix][linux], `Pointer vs Reference`, `malloc vs new`, `free vs delete`, `Shared Pointer의 순환 참조`, `왜 캐시 미스가 성능을 떨어뜨리는가?`, `페이지 교체 알고리즘(LRU, Clock)`, `Virtual Memory가 필요한 이유`, `메모리 단편화(Fragmentation)`, `False Sharing이란?` [gcc][threads], `NUMA 구조 이해하기` [gcc][posix][linux], `C, C++, Java, Python의 메모리 관리 비교`, `JVM 메모리 구조`, `CPython 객체 모델`, `Rust Ownership와 Borrow Checker`, `CUDA 메모리 계층`, `현대 CPU 캐시 계층(L1/L2/L3)`

## PathFinding

### Part 1. 길찾기의 기초 (8)

`CreateMap`, `CreateGrid`, `CreateNode`, `CreateEdge`, `BuildGraph`, `InitializeSearch`, `IsReachable`, `ReconstructPath`

### Part 2. 기초 탐색 (5)

`BreadthFirstSearch` ↗Graph#3, `DepthFirstSearch` ↗Graph#3, `IterativeDeepeningDFS`, `BidirectionalSearch` ↗Graph#10, `MultiSourceBFS` ↗Queue#6

### Part 3. 가중치 최단 경로 (5)

`Dijkstra` ↗Graph#9, `BellmanFord` ↗Graph#9, `SPFA` ↗Graph#9, `FloydWarshall` ↗Graph#9, `Johnson` ↗Graph#9

### Part 4. 휴리스틱 탐색 (5)

`GreedyBestFirstSearch`, `AStar`, `WeightedAStar`, `IDAStar` ↗Graph#10, `BeamSearch`

### Part 5. 게임 AI (5)

`JumpPointSearch`, `ThetaStar`, `LazyThetaStar`, `AnyAngleSearch`, `HierarchicalPathFinding`

### Part 6. 동적 환경 (4)

`DStar`, `DStarLite`, `LifelongPlanningAStar`, `DynamicReplanning`

### Part 7. 다중 경로 (4)

`KShortestPaths`, `YenAlgorithm`, `EppsteinAlgorithm`, `AlternativeRoute`

### Part 8. 비용 최적화 (4)

`UniformCostSearch`, `MinCostPath`, `ResourceConstrainedPath`, `TimeDependentShortestPath`

### Part 9. 다중 에이전트 (4)

`CooperativeAStar`, `ConflictBasedSearch`, `MultiAgentPathFinding`, `ReservationTable`

### Part 10. 지도와 공간 (5)

`NavigationMesh`, `WaypointGraph`, `VisibilityGraph`, `VoronoiDiagram`, `RoadNetwork`

### Part 11. 로봇공학 (5)

`RapidlyExploringRandomTree`, `RRTStar`, `ProbabilisticRoadMap`, `PotentialField`, `DynamicWindowApproach`

### Part 12. 자율주행 (5)

`HybridAStar`, `FrenetPlanner`, `LatticePlanner`, `MotionPlanning`, `TrajectoryOptimization`

### Part 13. 네트워크 (5)

`DistanceVectorRouting`, `LinkStateRouting`, `OSPF`, `RIP`, `BGPPathSelection`

### Part 14. 응용 (8)

`MazeSolver` ↗Stack#5 [gcc], `PuzzleSolver`, `GPSNavigation`, `RobotVacuumPlanner`, `GameNPCNavigation`, `WarehouseRobotRouting`, `DronePathPlanning`, `EmergencyEvacuation`

### Part 15. 성능 최적화 (7)

`HeuristicFunction`, `PriorityQueueOptimization` [gcc], `LandmarkHeuristic`, `ContractionHierarchy`, `TransitNodeRouting`, `ReachBasedRouting`, `ALTAlgorithm`

### Part 16. 연구 주제 (11)

`AnytimeAStar`, `AnytimeRepairingAStar`, `MonteCarloTreeSearch`, `ReinforcementLearningPathPlanning`, `NeuralPathPlanning`, `DifferentiableAStar`, `SwarmPathPlanning`, `AntColonyOptimization`, `GeneticPathPlanning`, `ParticleSwarmOptimization`, `QuantumPathFinding`

### 부록: 부록 (12)

`BFS vs Dijkstra`, `Dijkstra vs A*`, `A*의 휴리스틱은 왜 최적해를 보장하는가?`, `Manhattan Distance vs Euclidean Distance`, `Chebyshev Distance와 8방향 이동`, `Grid Map vs Navigation Mesh`, `Static Map vs Dynamic Map`, `단일 출발점 vs 다중 출발점`, `경로 계획(Path Planning)과 궤적 계획(Trajectory Planning)의 차이`, `게임 엔진(Unity, Unreal)의 길찾기 구조`, `ROS에서의 경로 계획`, `Google Maps와 차량 내비게이션의 경로 탐색 개요`

## Queue

### Part 1. 기본 연산 (10)

`CreateQueue` [gcc], `Enqueue`, `Dequeue`, `Front`, `Rear`, `Peek`, `IsEmpty`, `IsFull`, `Size`, `Clear`

### Part 2. 배열 큐 (4)

`LinearQueue`, `CircularQueue`, `Resize`, `Rotate`

### Part 3. 연결 큐 (3)

`LinkedQueue`, `EnqueueNode` [gcc], `DequeueNode`

### Part 4. 덱 (5)

`Deque`, `PushFront`, `PushBack`, `PopFront`, `PopBack`

### Part 5. 우선순위 큐 (8)

`PriorityQueue`, `PushHeap`, `PopHeap`, `Heapify`, `BuildHeap`, `HeapSort`, `CalendarQueue`, `RadixHeap` [gcc]

### Part 6. BFS (5)

`BreadthFirstSearch` ↗Graph#3, `LevelOrderTraversal`, `ShortestPath`, `FloodFill`, `MultiSourceBFS`

### Part 7. 슬라이딩 윈도우 (3)

`SlidingWindowMaximum`, `MonotonicQueue`, `WindowMinimum`

### Part 8. 운영체제 (5)

`JobQueue`, `ReadyQueue`, `WaitingQueue`, `TimingWheel`, `MessageQueue`

### Part 9. 네트워크 (4)

`PacketQueue`, `ProducerConsumer` [threads], `RingBuffer` [threads], `CircularBuffer`

### Part 10. 병렬 (4)

`LockFreeQueue` [threads], `MichaelScottQueue` [threads], `WorkStealingQueue` [threads], `ConcurrentQueue` [threads]

### Part 11. 연구 주제 (5)

`PersistentQueue` ↗AdvancedDataStructures#1, `ImmutableQueue`, `QueueingTheory`, `FairQueue`, `PriorityScheduling`

## Set

### Part 1. 집합의 기초 (8)

`CreateSet`, `Add`, `Remove`, `Contains`, `Clear`, `Size`, `IsEmpty`, `Copy`

### Part 2. 집합 연산 (2)

`Union` [gcc], `union() (Python Style)`

### 부록: 파이썬에서는 기본 내장 자료형 set을 통해 소문자 union() 메서드를 제공합니다. (6)

`Intersection` [gcc], `Difference` [gcc], `SymmetricDifference` [gcc], `Complement` [gcc], `CartesianProduct`, `PowerSet`

### Part 3. 관계 판별 (5)

`IsSubset`, `IsProperSubset` [gcc], `IsSuperset`, `IsDisjoint`, `Equals`

### Part 4. 반복과 탐색 (6)

`Iterator`, `ForEach`, `Find`, `Filter`, `Map`, `Reduce`

### Part 5. 구현 (7)

`ArraySet`, `LinkedSet`, `HashSet` [gcc], `TreeSet`, `Multiset`, `BitSet` [gcc], `ImmutableSet`

### Part 6. 비트 집합 (6)

`SetBit` [gcc], `ClearBit` [gcc], `ToggleBit` [gcc], `TestBit` [gcc], `CountBits` [gcc], `EnumerateSubsets` [gcc]

### Part 7. 서로소 집합 (6)

`MakeSet` ↗Graph#8, `FindSet` ↗Graph#8, `UnionSet` ↗Graph#8, `UnionByRank` ↗Graph#8, `PathCompression` ↗Graph#8, `ConnectedComponents` ↗Graph#4

### Part 8. 조합론 (5)

`Combination`, `Permutation`, `CombinationWithReplacement`, `NextPermutation`, `GrayCode` [gcc]

### Part 9. 부분집합 탐색 (6)

`Backtracking`, `BitMaskEnumeration` [gcc], `MeetInTheMiddle` [gcc], `SubsetSum`, `KnapsackSubset`, `DancingLinks`

### Part 10. 수학적 구조 (5)

`BinaryRelation`, `EquivalenceRelation`, `Partition`, `EquivalenceClass`, `QuotientSet`

### Part 11. 데이터베이스 (6)

`Distinct`, `Projection`, `Selection`, `Join`, `GroupBy`, `DuplicateElimination`

### Part 12. 정보검색 (5)

`InvertedIndex` ↗String#15, `PostingList`, `JaccardSimilarity`, `MinHash` ↗Hash#14, `LocalitySensitiveHashing` ↗Hash#14

### Part 13. AI와 데이터 (5)

`LabelSet` [gcc], `FeatureSet` [gcc], `VocabularySet`, `CandidateSet`, `ConstraintSet` [gcc]

### Part 14. 확률적 집합 (4)

`BloomFilter` ↗AdvancedDataStructures#3, `CountingBloomFilter` ↗AdvancedDataStructures#3, `CuckooFilter` ↗AdvancedDataStructures#3, `QuotientFilter` ↗AdvancedDataStructures#3

### Part 15. 병렬 집합 (4)

`ConcurrentSet` [threads], `LockFreeSet` [threads], `SkipListSet` ↗List#10, `ConcurrentHashSet` [threads]

### Part 16. 연구 주제 (7)

`PersistentSet`, `ImmutableBitSet` [gcc][threads], `CompressedBitSet`, `RoaringBitmap` [gcc], `SuccinctSet` [gcc], `LearnedSetIndex`, `DynamicConnectivity`

### 부록: 파이썬에서는 기본 내장 자료형 set을 통해 소문자 union() 메서드를 제공합니다. (12)

`Set vs List`, `Set vs Multiset`, `HashSet vs TreeSet`, `BitSet은 언제 사용하는가?`, `Union-Find가 거의 O(1)인 이유`, `집합과 그래프의 연결`, `집합과 관계(Relation)`, `집합과 함수(Function)`, `SQL은 왜 집합 이론 위에서 동작하는가?`, `AI에서 Label Set과 Vocabulary Set의 의미`, `비트마스크와 집합의 대응 관계` [gcc], `부분집합 열거 최적화` [gcc]

## Stack

### Part 1. 기본 연산 (9)

`CreateStack` [gcc], `Push`, `Pop`, `Peek`, `Top`, `IsEmpty`, `IsFull`, `Size`, `Clear`

### Part 2. 배열 스택 (3)

`ArrayStack`, `Resize`, `DynamicStack`

### Part 3. 연결리스트 스택 (3)

`LinkedStack`, `PushNode` [gcc], `PopNode`

### Part 4. 대표 활용 (9)

`ReverseString`, `BalancedParentheses`, `InfixToPostfix`, `PostfixEvaluation`, `PrefixEvaluation`, `DecimalToBinary`, `BaseConversion`, `Undo`, `BrowserHistory`

### Part 5. DFS (4)

`DepthFirstSearch` ↗Graph#3, `IterativeDFS` ↗Graph#3, `MazeSolver`, `TopologicalSort`

### Part 6. 단조 스택 (6)

`MonotonicStack`, `NextGreaterElement`, `PreviousGreaterElement`, `LargestRectangle`, `DailyTemperatures`, `StockSpan`

### Part 7. 특수 스택 (4)

`MinStack`, `MaxStack`, `TwoStacksInArray`, `MultipleStacks`

### Part 8. 재귀 (4)

`CallStack`, `StackFrame` [gcc], `TailRecursion`, `RecursionSimulation`

### Part 9. 병렬 (3)

`LockFreeStack` [threads], `TreiberStack` [threads], `EliminationBackoffStack` [threads]

### Part 10. 연구 주제 (5)

`PersistentStack`, `ImmutableStack` [threads], `StackAllocator`, `StackOverflow` [gcc][posix], `StackUnwinding`

## String

### Part 1. 문자열의 기초 (9)

`CreateString`, `Length`, `Concat`, `Substring`, `Compare`, `문자열 비교의 시간복잡도`, `Reverse`, `Split`, `Immutable String` [threads]

### Part 2. 기본 연산 응용 (3)

`Palindrome`, `Anagram`, `RunLengthEncoding`

### Part 3. 인코딩 (3)

`ASCII부터 Unicode까지`, `UTF-8과 UTF-16의 차이`, `UTF8Validate`

### Part 4. 동적 문자열 (3)

`Rope`, `GapBuffer`, `PieceTable`

### Part 5. 기본 패턴 검색 (2)

`NaiveSearch`, `KMP`

### Part 6. 패턴 검색 (4)

`RabinKarp` [gcc], `BoyerMoore`, `Horspool`, `SundaySearch`

### Part 7. 선형 시간 문자열 알고리즘 (3)

`ZAlgorithm`, `LongestRepeatedSubstring` [gcc], `Manacher`

### Part 8. 트라이와 다중 패턴 (2)

`Trie`, `AhoCorasick`

### Part 9. 접미사 구조 (6)

`SuffixArray`, `BuildSuffixArray`, `LCPArray`, `SuffixAutomaton`, `FMIndex` [gcc], `PalindromicTree`

### Part 10. 롤링 해시 (4)

`PolynomialRollingHash` ↗Hash#5 [gcc], `RabinFingerprint` ↗Hash#5 [gcc], `SubstringHash`, `LongestCommonSubstring`

### Part 11. 압축·변환 (4)

`LZW`, `BurrowsWheelerTransform`, `MoveToFront`, `Huffman`

### Part 12. 편집 거리 (4)

`Levenshtein`, `DamerauLevenshtein`, `LongestCommonSubstringDP`, `LongestCommonSubsequence` [gcc]

### Part 13. 정규식과 오토마톤 (2)

`FiniteAutomaton`, `RegexNFA`

### Part 14. 컴파일러 (2)

`Lexer`, `RecursiveDescentParser`

### Part 15. 검색엔진 (3)

`InvertedIndex`, `NGramIndex`, `TFIDF`

### Part 16. 생물정보학 (3)

`문자열 알고리즘의 생물정보학 활용`, `NeedlemanWunsch`, `SmithWaterman`

### Part 17. AI와 NLP (7)

`BytePairEncoding`, `WordPiece`, `SentencePiece`, `TokenizeLLM`, `EmbeddingLookup`, `Detokenize`, `LLM 토크나이저는 왜 필요한가?`

### 부록: 부록 (4)

`KMP는 왜 O(n)인가?`, `Boyer-Moore가 빠른 이유`, `Trie vs HashMap`, `Suffix Array vs Suffix Tree`

## Tree

### Part 1. 트리의 기초 (12)

`CreateTree`, `Root`, `Parent`, `Child`, `Sibling`, `Degree`, `Depth`, `Height`, `Level` [gcc], `Size`, `IsLeaf`, `IsRoot`

### Part 2. 이진트리 (7)

`CreateBinaryTree`, `InsertLeft`, `InsertRight`, `DeleteNode`, `CopyTree`, `MirrorTree`, `MergeTree`

### Part 3. 순회 (6)

`Preorder`, `Inorder`, `Postorder`, `LevelOrder`, `MorrisTraversal`, `EulerTour` [gcc]

### Part 4. 탐색 (6)

`TreeSearch`, `FindNode`, `FindParent`, `LowestCommonAncestor` [gcc], `PathToNode`, `DistanceBetweenNodes`

### Part 5. 이진 탐색 트리(BST) (8)

`InsertBST`, `SearchBST`, `DeleteBST`, `FindMin`, `FindMax`, `Successor`, `Predecessor`, `ValidateBST`

### Part 6. AVL 트리 (7)

`AVLInsert`, `AVLDelete`, `BalanceFactor`, `RotateLeft`, `RotateRight`, `RotateLeftRight`, `RotateRightLeft`

### Part 7. Red-Black Tree (8)

`RBInsert`, `RBDelete`, `FixViolation`, `Recolor`, `DoubleBlack`, `TwoThreeTree`, `TwoThreeFourTree`, `LeftLeaningRedBlackTree`

### Part 8. 힙 (15)

`BinaryHeap`, `HeapInsert` [gcc], `HeapDelete` [gcc], `Heapify` ↗Queue#5 [gcc], `BuildHeap` ↗Queue#5, `HeapSort` ↗Queue#5, `FibonacciHeap`, `BinomialHeap` [gcc], `PairingHeap`, `LeftistHeap`, `DAryHeap`, `MinMaxHeap` [gcc], `SkewHeap`, `IntervalHeap`, `LoserTree`

### Part 9. 다중 트리 (5)

`TrieInsert() & TrieSearch`, `TrieDelete`, `RadixTree`, `GeneralTree`, `NaryTree`

### Part 10. 문자열 자료구조 (5)

`SuffixTrie`, `SuffixTree`, `PatriciaTrie` [gcc], `TernarySearchTree`, `SuffixArray` ↗String#9

### Part 11. 공간 분할 트리 (6)

`SegmentTree`, `FenwickTree`, `KDTree`, `QuadTree`, `Octree`, `BSPTree`

### Part 12. 구간 연산 (5)

`RangeQuery`, `LazyPropagation`, `RangeUpdate`, `SqrtDecomposition`, `MergeSortTree`

### Part 13. 고급 트리 (10)

`BTree`, `BPlusTree`, `SplayTree`, `Treap`, `CartesianTree`, `ScapegoatTree`, `OrderStatisticTree`, `WeightBalancedTree`, `ZipTree`, `WAVLTree`

### Part 14. 함수형 자료구조 (3)

`PersistentTree`, `ImmutableTree`, `FingerTree` ↗AdvancedDataStructures#4

### Part 15. 그래프 확장 (9)

`RootingTree`, `TreeDP`, `HeavyLightDecomposition`, `CentroidDecomposition`, `BinaryLifting`, `EulerTourTechnique`, `LinkCutTree`, `TopTree`, `EulerTourTree`

### Part 16. 특수 목적 (9)

`ExpressionTree`, `SyntaxTree`, `ParseTree`, `DecisionTree`, `MerkleTree`, `IntervalTree`, `RopeTree`, `RTree`, `VanEmdeBoasTree`

### 부록: 부록 (4)

`트리 순회의 재귀와 반복 구현`, `Binary Tree vs BST`, `BST vs AVL vs Red-Black`, `Segment Tree vs Fenwick Tree`
