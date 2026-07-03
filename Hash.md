해시는 학부에서는 보통 "HashMap 구현" 정도에서 끝나지만, 실제로는 데이터베이스, 운영체제, 암호학, 분산 시스템까지 이어지는 아주 큰 분야야. 그래서 "대표 코드" 중심으로 목차를 짜면 다음과 같이 구성할 수 있어.

자료구조 리포지토리 - 해시(Hash) 편
Part 1. 해시의 기초
CreateHashTable()
HashFunction()
HashCode()
IndexOf()
LoadFactor()
Capacity()
Resize()
Rehash()
Part 2. 기본 연산
Put()
Get()
Remove()
ContainsKey()
ContainsValue()
Replace()
Clear()
Size()
Part 3. 충돌 해결
SeparateChaining()
LinearProbing()
QuadraticProbing()
DoubleHashing()
RobinHoodHashing()
CuckooHashing()
HopscotchHashing()
CoalescedHashing()
Part 4. 해시 함수
DivisionHash()
MultiplicationHash()
MidSquareHash()
FoldingHash()
UniversalHash()
PerfectHash()
MinimalPerfectHash()
Part 5. 문자열 해싱
PolynomialRollingHash()
RabinFingerprint()
DoubleHash()
SubstringHash()
LongestCommonSubstringHash()
Part 6. 확률적 자료구조
BloomFilter()
CountingBloomFilter()
CuckooFilter()
CountMinSketch()
HyperLogLog()
Part 7. 분산 해시
ConsistentHashing()
VirtualNode()
RendezvousHash()
DistributedHashTable()
Chord()
Kademlia()
Part 8. 암호학
MD5()
SHA1()
SHA256()
SHA3()
HMAC()
PBKDF2()
BCrypt()
Argon2()
Part 9. 자료구조 응용
HashSet()
HashMap()
LinkedHashMap()
IdentityHashMap()
WeakHashMap()
LRUCache()
Part 10. 병렬 해시
ConcurrentHashMap()
LockStriping()
LockFreeHashTable()
SplitOrderedList()
Part 11. 데이터베이스
ExtendibleHashing()
LinearHashing()
HashJoin()
GraceHashJoin()
HashIndex()
Part 12. 파일 시스템
ContentAddressing()
Deduplication()
MerkleHash()
CASStorage()
Part 13. 블록체인
MerkleTree()
MerkleProof()
BlockHash()
ProofOfWork()
HashChain()
Part 14. AI와 검색
LocalitySensitiveHashing()
SimHash()
MinHash()
FeatureHashing()
SemanticHashing()
Part 15. 연구 주제
PerfectHashGeneration()
DynamicPerfectHash()
QuotientFilter()
XORFilter()
SuccinctHashTable()
LearnedHashIndex()
부록
Array vs Hash Table
BST vs Hash Table
HashMap vs TreeMap
Open Addressing vs Separate Chaining
Robin Hood Hashing의 직관
왜 Java HashMap은 TreeBin으로 바뀌는가?
Python dict의 구현 원리
C++ unordered_map의 구조
Redis Dictionary 구조
Bloom Filter는 왜 오탐(False Positive)만 발생하는가?
Consistent Hashing이 분산 시스템에서 중요한 이유
암호학적 해시와 일반 해시의 차이
개인적으로 추가하고 싶은 장

네 리포지토리는 "구조를 시각적으로 이해한다"는 성격이 강하니까, 마지막에 다음과 같은 장을 넣는 것도 재미있을 것 같아.

Part 16. 해시 구조 시각화
CollisionVisualization()
BucketDistribution()
ProbeSequence()
ResizeAnimation()
ChainGrowth()
ClusterFormation()
AvalancheEffect()
HashQualityEvaluation()
CacheLocality()
MemoryLayout()

이런 장은 일반 자료구조 책에서는 거의 다루지 않지만, 해시 테이블 내부에서 실제로 무슨 일이 일어나는지를 그림과 애니메이션으로 설명할 수 있어서 네 리포지토리의 특징을 잘 살릴 수 있을 거야.
