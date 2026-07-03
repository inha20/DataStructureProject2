Part 1. 집합의 기초
CreateSet()
Add()
Remove()
Contains()
Clear()
Size()
IsEmpty()
Copy()
Part 2. 집합 연산
Union()
Intersection()
Difference()
SymmetricDifference()
Complement()
CartesianProduct()
PowerSet()
Part 3. 관계 판별
IsSubset()
IsProperSubset()
IsSuperset()
IsDisjoint()
Equals()
Part 4. 반복과 탐색
Iterator()
ForEach()
Find()
Filter()
Map()
Reduce()
Part 5. 구현
ArraySet()
LinkedSet()
HashSet()
TreeSet()
BitSet()
ImmutableSet()
Part 6. 비트 집합
SetBit()
ClearBit()
ToggleBit()
TestBit()
CountBits()
EnumerateSubsets()
Part 7. 서로소 집합
MakeSet()
FindSet()
UnionSet()
UnionByRank()
PathCompression()
ConnectedComponents()
Part 8. 조합론
Combination()
Permutation()
CombinationWithReplacement()
NextPermutation()
GrayCode()
Part 9. 부분집합 탐색
Backtracking()
BitMaskEnumeration()
MeetInTheMiddle()
SubsetSum()
KnapsackSubset()
Part 10. 수학적 구조
BinaryRelation()
EquivalenceRelation()
Partition()
EquivalenceClass()
QuotientSet()
Part 11. 데이터베이스
Distinct()
Projection()
Selection()
Join()
GroupBy()
DuplicateElimination()
Part 12. 정보검색
InvertedIndex()
PostingList()
JaccardSimilarity()
MinHash()
LocalitySensitiveHashing()
Part 13. AI와 데이터
LabelSet()
FeatureSet()
VocabularySet()
CandidateSet()
ConstraintSet()
Part 14. 확률적 집합
BloomFilter()
CountingBloomFilter()
CuckooFilter()
QuotientFilter()
Part 15. 병렬 집합
ConcurrentSet()
LockFreeSet()
SkipListSet()
ConcurrentHashSet()
Part 16. 연구 주제
PersistentSet()
ImmutableBitSet()
CompressedBitSet()
RoaringBitmap()
SuccinctSet()
LearnedSetIndex()
DynamicConnectivity()
부록
Set vs List
Set vs Multiset
HashSet vs TreeSet
BitSet은 언제 사용하는가?
Union-Find가 거의 O(1)인 이유
집합과 그래프의 연결
집합과 관계(Relation)
집합과 함수(Function)
SQL은 왜 집합 이론 위에서 동작하는가?
AI에서 Label Set과 Vocabulary Set의 의미
비트마스크와 집합의 대응 관계
부분집합 열거 최적화
이 책에서 특히 강조하면 좋은 주제

이 시리즈는 단순히 자료구조를 설명하는 것을 넘어서, 집합이라는 추상 개념이 여러 분야에서 어떻게 구현되는지를 보여주면 차별화될 거야.

예를 들어 하나의 Union() 함수도 다음과 같이 확장할 수 있어.

수학: 합집합
C++ STL: std::set_union
Python: set.union()
데이터베이스: UNION
그래프: Union-Find
비트마스크: OR 연산
AI: 후보(Label) 집합 병합

이처럼 하나의 연산을 여러 분야의 구현과 연결해서 설명하면, 네 리포지토리의 "대표 코드 중심"이라는 철학과도 잘 맞고, 독자도 같은 개념이 다양한 분야에서 재사용되는 구조를 자연스럽게 이해할 수 있을 거야.
