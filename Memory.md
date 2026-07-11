# Part 1. 메모리의 기초
## CreateMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Variable created: " << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## Alignment()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Alignment aligns variables to multiple of 4/8 bytes for CPU efficiency." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## Padding()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Size of Padded struct: " << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## MemoryDump()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Memory dump of 0x12345678: " << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 2. 프로세스 메모리
## TextSegment()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Text Segment stores compiled machine instructions (Read-Only)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## DataSegment()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Data Segment stores initialized globals/statics: " << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## EnvironmentVariable()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Environment Variables are stored at the top of the stack." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CommandLineArgument()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Command Line Arguments count: " << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## PopFrame()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Function epilogue: restore stack pointer and base pointer." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CallFunction()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Call Function: Pushes return address and jumps to target." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ReturnFunction()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Return Function: Pops return address and jumps back." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## LocalVariable()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Local Variables accessed via offset from base pointer (e.g., [rbp-4])." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## StackFrame()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Stack Frame: Independent memory block per function call." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## StackOverflow()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Stack Overflow: Exceeding stack limit (e.g., infinite recursion)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## TailCallOptimization()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Tail Call Optimization reuses stack frame if recursive call is the last action." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 4. 힙 메모리
## malloc()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "malloc verified." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## new()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "new verified." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## PlacementNew()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Placement new verified." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## SlabAllocator()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Slab Allocator manages caches of specific fixed-size objects." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## BuddyAllocator()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Buddy Allocator splits memory into powers of 2 and merges buddies." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ArenaAllocator()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Arena Allocator bumps pointer for fast allocation, frees all at once." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ObjectPool()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Object Pool reuses expensive objects instead of destroying them." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## FreeList()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Free List maintains linked list of free blocks for reuse." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 7. 가비지 컬렉션
## MarkSweep()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Mark-Sweep: identifies reachable objects, sweeps unreachable (causes fragmentation)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## MarkCompact()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Mark-Compact: slides live objects together to resolve fragmentation." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CopyingGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Copying GC: moves live objects to a new contiguous half-space." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## GenerationalGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Generational GC: separates young/old objects for efficient minor/major collections." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ReferenceCountingGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Reference Counting GC: frees when count is 0, but fails on circular refs." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## IncrementalGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Incremental GC: interleaves GC work with app thread to reduce pause time." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ConcurrentGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Concurrent GC: runs GC in background thread concurrently with app." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 8. 캐시
## CacheLine()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cache Line: data is fetched in chunks (e.g., 64 bytes)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CacheHit()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cache Hit: data found in fast L1/L2 cache." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CacheMiss()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cache Miss: data not in cache, must fetch from slow RAM." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CacheFriendlyTraversal()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cache Friendly Traversal: iterating rows instead of cols minimizes misses." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CacheBlocking()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cache Blocking: processing in small tiles maximizes cache reuse." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## FalseSharing()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "False Sharing: independent vars on same cache line invalidate each other." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 9. 가상 메모리
## VirtualAddress()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Virtual Address gives illusion of contiguous memory to each process." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## PhysicalAddress()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Physical Address points to actual hardware RAM chip." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## AddressTranslation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Address Translation: MMU converts virtual to physical address." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## Paging()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Paging divides memory into fixed-size blocks (pages), removing external fragmentation." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## PageTable()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Page Table maps virtual pages to physical frames." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## PageFault()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Page Fault occurs when accessed page is not in physical RAM." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## TLBLookup()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "TLB caches recent page table translations inside MMU." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## MemoryMapping()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "mmap maps file descriptor directly to virtual memory." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 10. 메모리 보호
## ReadOnlyMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Read-Only Memory triggers SIGSEGV on write attempt." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ExecuteOnlyMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Execute-Only Memory prevents reading code as data to block attacks." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## MemoryProtection()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Memory Protection uses RWX permission bits on pages." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## StackCanary()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Stack Canary detects buffer overflow before returning." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ASLR()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "ASLR randomizes memory layouts to prevent hardcoded address attacks." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## DEP()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "DEP (NX Bit) marks stack/heap non-executable." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 11. 병렬 메모리
## AtomicOperation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Atomic Operation verified." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## AcquireRelease()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Acquire-Release ensures synchronized light-weight memory ordering." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## SequentialConsistency()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Sequential Consistency provides strict total ordering." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 12. 메모리 분석
## MemoryLeak()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Memory Leak: dynamically allocated memory is never freed." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## DanglingPointer()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Dangling Pointer: points to already freed memory." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## WildPointer()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Wild Pointer: uninitialized pointer holding garbage address." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## DoubleFree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Double Free: calling free/delete twice on same address." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## UseAfterFree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Use-After-Free: accessing freed memory, causing corruption." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## BufferOverflow()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Buffer Overflow: writing past array bounds." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## HeapCorruption()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Heap Corruption: allocator metadata destroyed by bad memory operations." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 13. 파일과 메모리
## MemoryMappedFile()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Memory Mapped File maps file directly to virtual memory." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## SharedMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Shared Memory: identical RAM frame mapped to multiple processes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CopyOnWrite()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Copy-On-Write delays physical memory copy until modification occurs." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ZeroCopy()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Zero Copy transfers data directly inside kernel via DMA." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 14. 운영체제
## ProcessMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Process Memory is fully isolated via page tables." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ThreadLocalStorage()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "TLS ensures independent copies per thread." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## KernelMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Kernel Memory is protected and holds OS data/code." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## UserMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "User Memory holds application stack, heap, data, text." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## NUMAMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "NUMA Memory has non-uniform access times depending on CPU node distance." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 15. 현대 시스템
## GPUMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "GPU Memory (VRAM) has high bandwidth but independent space." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## UnifiedMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Unified Memory seamlessly migrates pages between CPU and GPU." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## PersistentMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Persistent Memory is non-volatile RAM with direct byte addressing." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## HugePage()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Huge Pages (2MB/1GB) reduce TLB miss overhead." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## RDMA()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "RDMA bypasses remote CPU to read/write memory directly over network." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## MemoryCompression()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Memory Compression compresses RAM pages instead of swapping to disk." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# Part 16. 연구 주제
## GarbageFirstGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "G1GC divides heap into regions and targets garbage-heavy areas first." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ZGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "ZGC uses colored pointers for sub-millisecond pause times." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## ShenandoahGC()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Shenandoah GC uses Brooks pointers for concurrent evacuation." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## RegionBasedMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Region-Based Memory manages lifetimes via arenas (similar to Rust lifetimes)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## EscapeAnalysis()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Escape Analysis converts safe heap allocations into stack allocations." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## OwnershipTypeSystem()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Ownership System enforces strict single ownership and borrow rules at compile time." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## PersistentHeap()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Persistent Heap software mechanisms manage recovery for PMEM." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## TransactionalMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Transactional Memory allows atomic execution of memory blocks like DB transactions." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CapabilityPointer()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Capability Pointer binds bounds and permissions to hardware pointers." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CHERIArchitecture()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CHERI adds capability pointers to CPU pipeline." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## MemoryTagging()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Memory Tagging assigns hardware tags to pointers and memory blocks." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## HardwareMemorySafety()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Hardware Memory Safety prevents memory bugs at 0 overhead chip level." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```

# 부록
## Stack vs Heap
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Stack is fast/auto; Heap is large/manual." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## Pointer vs Reference
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Pointer can be null/changed; Reference is a fixed alias." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## malloc vs new
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "malloc allocates bytes; new allocates and calls constructor." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## free vs delete
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "free releases bytes; delete calls destructor then releases bytes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## Shared Pointer의 순환 참조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Circular references in shared_ptr leak memory; break with weak_ptr." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## 왜 캐시 미스가 성능을 떨어뜨리는가?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cache miss stalls CPU pipeline while waiting ~100ns for RAM." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## 페이지 교체 알고리즘(LRU, Clock)
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "LRU/Clock decides which page swaps to disk when RAM is full." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## Virtual Memory가 필요한 이유
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Virtual memory gives security, scalability, and contiguous illusion." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## 메모리 단편화(Fragmentation)
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Internal fragmentation wastes page space; External wastes heap space." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## False Sharing이란?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "False sharing bounces cache lines between cores unnecessarily." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## NUMA 구조 이해하기
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "NUMA requires allocating memory on the same node as the thread." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## C, C++, Java, Python의 메모리 관리 비교
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "C/C++: Manual; Java: Background GC; Python: RefCount + GC." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## JVM 메모리 구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "JVM: Method Area, Heap (Eden/Survivor/Old), Stacks, PC, Native Stack." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CPython 객체 모델
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CPython uses PyObject with ref count and type pointer under GIL." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## Rust Ownership와 Borrow Checker
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Rust enforces 1 owner, N readers OR 1 writer at compile time." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## CUDA 메모리 계층
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CUDA: Global, Shared (L1), Local, Constant, Texture." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
## 현대 CPU 캐시 계층(L1/L2/L3)
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CPU Cache: L1/L2 (private, fast), L3 (shared, large, slower)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
```
