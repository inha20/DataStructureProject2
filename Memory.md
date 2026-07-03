Part 1. 메모리의 기초
CreateMemory()
Address()
Pointer()
Reference()
Dereference()
MemoryLayout()
Alignment()
Padding()
Endianness()
MemoryDump()
Part 2. 프로세스 메모리
TextSegment()
DataSegment()
BSSSegment()
HeapMemory()
StackMemory()
EnvironmentVariable()
CommandLineArgument()
Part 3. 스택 메모리
PushFrame()
PopFrame()
CallFunction()
ReturnFunction()
LocalVariable()
StackFrame()
StackOverflow()
TailCallOptimization()
Part 4. 힙 메모리
malloc()
calloc()
realloc()
free()
new()
delete()
PlacementNew()
Part 5. 스마트 포인터
UniquePointer()
SharedPointer()
WeakPointer()
ReferenceCounting()
OwnershipTransfer()
Part 6. 메모리 관리
MemoryPool()
SlabAllocator()
BuddyAllocator()
ArenaAllocator()
ObjectPool()
FreeList()
Part 7. 가비지 컬렉션
MarkSweep()
MarkCompact()
CopyingGC()
GenerationalGC()
ReferenceCountingGC()
IncrementalGC()
ConcurrentGC()
Part 8. 캐시
CacheLine()
CacheHit()
CacheMiss()
CacheFriendlyTraversal()
CacheBlocking()
FalseSharing()
Part 9. 가상 메모리
VirtualAddress()
PhysicalAddress()
AddressTranslation()
Paging()
PageTable()
PageFault()
TLBLookup()
MemoryMapping()
Part 10. 메모리 보호
ReadOnlyMemory()
ExecuteOnlyMemory()
MemoryProtection()
StackCanary()
ASLR()
DEP()
Part 11. 병렬 메모리
AtomicOperation()
CompareAndSwap()
MemoryBarrier()
AcquireRelease()
SequentialConsistency()
Part 12. 메모리 분석
MemoryLeak()
DanglingPointer()
WildPointer()
DoubleFree()
UseAfterFree()
BufferOverflow()
HeapCorruption()
Part 13. 파일과 메모리
MemoryMappedFile()
SharedMemory()
CopyOnWrite()
ZeroCopy()
Part 14. 운영체제
ProcessMemory()
ThreadLocalStorage()
ContextSwitch()
KernelMemory()
UserMemory()
NUMAMemory()
Part 15. 현대 시스템
GPUMemory()
UnifiedMemory()
PersistentMemory()
HugePage()
RDMA()
MemoryCompression()
Part 16. 연구 주제
GarbageFirstGC()
ZGC()
ShenandoahGC()
RegionBasedMemory()
EscapeAnalysis()
OwnershipTypeSystem()
PersistentHeap()
TransactionalMemory()
CapabilityPointer()
CHERIArchitecture()
MemoryTagging()
HardwareMemorySafety()
부록
Stack vs Heap
Pointer vs Reference
malloc vs new
free vs delete
Shared Pointer의 순환 참조
왜 캐시 미스가 성능을 떨어뜨리는가?
페이지 교체 알고리즘(LRU, Clock)
Virtual Memory가 필요한 이유
메모리 단편화(Fragmentation)
False Sharing이란?
NUMA 구조 이해하기
C, C++, Java, Python의 메모리 관리 비교
JVM 메모리 구조
CPython 객체 모델
Rust Ownership와 Borrow Checker
CUDA 메모리 계층
현대 CPU 캐시 계층(L1/L2/L3)
이 책의 차별점

이 책은 단순히 메모리 API를 설명하는 것이 아니라, 프로그램이 실행되는 순간 메모리에서 실제 어떤 일이 일어나는지를 단계별로 시각화하는 데 초점을 맞추면 좋아.

예를 들어 malloc() 하나의 장도 다음처럼 구성할 수 있어.

함수 호출 전 힙 상태
할당 가능한 블록 탐색
메타데이터(Header) 생성
사용자 포인터 반환
할당 후 메모리 레이아웃
free() 호출 시 Free List 변화
단편화가 누적되는 과정
Memory Pool과의 비교

이런 식으로 메모리 상태의 변화를 그림과 애니메이션으로 보여준다면, 기존 자료구조 교재와는 확실히 다른 리포지토리가 될 거야.

개인적으로는 지금까지 이야기한 리스트, 스택, 큐, 트리, 그래프, 문자열, 해시 중에서도 이 메모리 편이 가장 독창적이고, 네가 지향하는 '구조를 눈으로 이해하는 컴퓨터공학'이라는 방향성을 가장 잘 보여줄 수 있는 시리즈가 될 가능성이 크다고 생각해.
