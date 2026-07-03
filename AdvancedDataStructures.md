Part 1. Persistent Data Structures
PersistentArray()
PersistentList()
PersistentStack()
PersistentQueue()
PersistentSegmentTree()
PersistentTrie()
Part 2. Succinct Data Structures
BitVector()
Rank()
Select()
WaveletTree()
FMIndex()
SuccinctTrie()
Part 3. 확률적 자료구조
BloomFilter()
CountingBloomFilter()
CuckooFilter()
QuotientFilter()
XORFilter()
CountMinSketch()
HyperLogLog()
Part 4. 문자열 자료구조
Rope()
PieceTable()
GapBuffer()
FingerTree()
SuffixAutomaton()
PatriciaTrie()
Part 5. 공간 자료구조
KDTree()
QuadTree()
Octree()
RTree()
BallTree()
BVHTree()
Part 6. 범위 질의
SegmentTree()
LazyPropagation()
FenwickTree()
SparseTable()
IntervalTree()
RangeTree()
Part 7. 균형 트리
AVLTree()
RedBlackTree()
AA Tree()
Treap()
SplayTree()
ScapegoatTree()
TangoTree()
Part 8. 외부 메모리
BTree()
BPlusTree()
BStarTree()
FractalTree()
LSMTree()
BufferTree()
Part 9. 동시성
LockFreeQueue()
LockFreeStack()
ConcurrentHashMap()
SkipListSet()
CompareAndSwap()
HazardPointer()
Part 10. 분산 시스템
ConsistentHashing()
DistributedHashTable()
Chord()
Kademlia()
MerkleTree()
CRDT()
Part 11. GPU 자료구조
GPUBVH()
CUDASparseMatrix()
ParallelPrefixSum()
ParallelHashTable()
WarpQueue()
Part 12. AI와 데이터
VectorIndex()
HNSW()
IVFIndex()
ProductQuantization()
KDTreeKNN()
BallTreeKNN()
AnnoyIndex()
FAISSIndex()
Part 13. 데이터베이스
SkipList()
MemTable()
SSTable()
WriteAheadLog()
BTreeIndex()
HashIndex()
Part 14. 운영체제
BuddyAllocator()
SlabAllocator()
RadixTree()
XArray()
PageTable()
Part 15. 최신 연구
LearnedIndex()
LearnedHash()
AdaptiveRadixTree()
CacheObliviousBTree()
FusionTree()
vanEmdeBoasTree()
XFastTrie()
YFastTrie()
EliasFano()
CompressedSuffixArray()
DynamicWaveletTree()
PackedMemoryArray()
CacheAwareBTree()
LearnedBloomFilter()
부록
Cache-Aware vs Cache-Oblivious
Immutable vs Persistent
Lock-Free vs Wait-Free
Online vs Offline 자료구조
Static vs Dynamic 자료구조
Internal Memory vs External Memory
Exact vs Approximate 자료구조
CPU 자료구조 vs GPU 자료구조
LSM Tree가 SSD에 적합한 이유
벡터 데이터베이스는 왜 HNSW를 사용하는가?
현대 데이터베이스가 B+Tree와 LSMTree를 함께 사용하는 이유
생성형 AI 시대의 자료구조
이 책의 역할

이 책은 학부 교재의 연장선이라기보다 컴퓨터과학의 최전선으로 가는 안내서가 되면 좋겠어.

예를 들어 마지막 장에 있는 항목들은 최근 연구와 산업에서 실제로 많이 쓰이는 것들이야.

HNSW → 벡터 검색(LLM, RAG, 임베딩 검색)
FAISSIndex → 대규모 유사도 검색
LSMTree → RocksDB, LevelDB, Cassandra
AdaptiveRadixTree → 메인 메모리 데이터베이스
LearnedIndex → 머신러닝을 이용한 인덱스
CacheObliviousBTree → 메모리 계층을 고려한 자료구조

이렇게 구성하면 시리즈 전체가 입문부터 최신 연구까지 이어지는 계단이 되고, 마지막 권은 "자료구조를 더 배우려면 어떤 주제들이 있는가"를 보여주는 로드맵 역할도 할 수 있을 거야.
