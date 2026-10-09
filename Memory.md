# Part 1. 메모리의 기초
## CreateMemory()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

// 메모리는 "주소로 번호가 매겨진 바이트의 배열" 이다.  시뮬레이션: 범위를 검사하는 바이트 배열 + 1~8 바이트 정수의 리틀/빅 엔디언 읽기·쓰기 + 겹쳐도 안전한 복사(memmove)·채우기.
//  정수를 바이트로 나눌 때 낮은 자리 바이트를 낮은 주소에 놓는 방식이 리틀 엔디언(x86, ARM 기본), 반대가 빅 엔디언(네트워크 바이트 순서).  범위 검사는 `addr + n` 이 *오버플로로 되감겨* 통과하는 일이 없게 `addr > size − n` 으로 한다.
//  ① 호스트 대조: 이 기계의 실제 표현(memcpy)과 readLE/readBE 중 맞는 쪽이 같다  ② LE 로 쓰고 BE 로 읽으면 바이트 순서를 뒤집은 값(__builtin_bswap 오라클)  ③ 부호 확장 읽기가 C 의 정수 변환과 같다
//  ④ 범위 밖: 모든 (addr, n) 경계 — addr + n 이 size_t 를 넘어 되감기는 값 포함 — 에서 정확히 범위 안일 때만 성공  ⑤ 무작위 연산 20 만 번(쓰기·채우기·겹치는 복사·읽기)을 그림자 std::vector + std::memmove 와 대조.
class Memory {
    std::vector<uint8_t> bytes;
    void check(size_t addr, size_t n) const { if (n > bytes.size() || addr > bytes.size() - n) throw std::out_of_range("segfault"); }                  // addr + n 오버플로 없이 검사
public:
    explicit Memory(size_t size) : bytes(size, 0) {}
    size_t size() const { return bytes.size(); }
    uint8_t read8(size_t addr) const { check(addr, 1); return bytes[addr]; }
    void write8(size_t addr, uint8_t v) { check(addr, 1); bytes[addr] = v; }
    void writeLE(size_t addr, uint64_t v, int n) { check(addr, (size_t)n); for (int i = 0; i < n; ++i) bytes[addr + i] = (uint8_t)(v >> (8 * i)); }                                  // 낮은 자리 바이트가 낮은 주소
    void writeBE(size_t addr, uint64_t v, int n) { check(addr, (size_t)n); for (int i = 0; i < n; ++i) bytes[addr + i] = (uint8_t)(v >> (8 * (n - 1 - i))); }
    uint64_t readLE(size_t addr, int n) const { check(addr, (size_t)n); uint64_t v = 0; for (int i = 0; i < n; ++i) v |= (uint64_t)bytes[addr + i] << (8 * i); return v; }
    uint64_t readBE(size_t addr, int n) const { check(addr, (size_t)n); uint64_t v = 0; for (int i = 0; i < n; ++i) v = (v << 8) | bytes[addr + i]; return v; }
    int64_t readSignedLE(size_t addr, int n) const { uint64_t v = readLE(addr, n); if (n < 8 && (v >> (8 * n - 1) & 1)) v |= ~0ULL << (8 * n); return (int64_t)v; }                  // 부호 확장
    void fill(size_t addr, uint8_t b, size_t n) { check(addr, n); std::fill(bytes.begin() + addr, bytes.begin() + addr + n, b); }
    void copy(size_t dst, size_t src, size_t n) { check(dst, n); check(src, n); if (dst < src) for (size_t i = 0; i < n; ++i) bytes[dst + i] = bytes[src + i]; else for (size_t i = n; i-- > 0;) bytes[dst + i] = bytes[src + i]; }          // 겹치면 방향을 골라 memmove 처럼
    const uint8_t* data() const { return bytes.data(); }
};
uint64_t swapBytes(uint64_t v, int n) { uint64_t r = 0; for (int i = 0; i < n; ++i) r = (r << 8) | ((v >> (8 * i)) & 0xff); return r; }

int main() {
    Memory m(64); m.writeLE(8, 0x11223344, 4); assert(m.read8(8) == 0x44 && m.read8(9) == 0x33 && m.read8(11) == 0x11 && m.readLE(8, 4) == 0x11223344 && m.readBE(8, 4) == 0x44332211);
    uint32_t probe = 1; uint8_t first; std::memcpy(&first, &probe, 1); bool hostLittle = first == 1;
    std::mt19937_64 rng(1001);
    for (int it = 0; it < 20000; ++it) { int n = 1 << (rng() % 4); uint64_t v = rng() & (n == 8 ? ~0ULL : ((1ULL << (8 * n)) - 1)); size_t addr = rng() % (64 - 8); m.writeLE(addr, v, n);
        uint64_t host = 0; std::memcpy(&host, m.data() + addr, (size_t)n); if (hostLittle) assert(host == v); else assert(host == swapBytes(v, n));                      // ① 호스트의 실제 표현
        assert(m.readLE(addr, n) == v && m.readBE(addr, n) == swapBytes(v, n));                                                                                                  // ② LE 로 쓰고 BE 로 읽으면 뒤집힌 값
        uint64_t be = swapBytes(v, n), viaBuiltin = n == 8 ? __builtin_bswap64(v) : n == 4 ? __builtin_bswap32((uint32_t)v) : n == 2 ? __builtin_bswap16((uint16_t)v) : v; assert(be == viaBuiltin);
        m.writeBE(addr, v, n); assert(m.readBE(addr, n) == v && m.readLE(addr, n) == swapBytes(v, n));
        int64_t s = m.readSignedLE(addr, n); m.writeLE(addr, v, n); int64_t want = n == 1 ? (int64_t)(int8_t)v : n == 2 ? (int64_t)(int16_t)v : n == 4 ? (int64_t)(int32_t)v : (int64_t)v; assert(m.readSignedLE(addr, n) == want); (void)s; }          // ③ 부호 확장
    {   const size_t SZ = 16; Memory small(SZ); const size_t huge = ~(size_t)0;                                  // ④ 범위 경계 전수
        for (size_t addr : {(size_t)0, (size_t)1, (size_t)8, SZ - 8, SZ - 4, SZ - 1, SZ, SZ + 1, huge - 3, huge - 1, huge}) for (int n = 1; n <= 8; ++n) { bool inside = addr <= SZ && (size_t)n <= SZ - addr; bool ok = true; try { small.readLE(addr, n); } catch (const std::out_of_range&) { ok = false; } assert(ok == inside);
            ok = true; try { small.writeBE(addr, 0xAB, n); } catch (const std::out_of_range&) { ok = false; } assert(ok == inside); }
        bool trapped = false; try { small.fill(SZ - 4, 1, 5); } catch (const std::out_of_range&) { trapped = true; } assert(trapped); trapped = false; try { small.copy(0, huge - 2, 4); } catch (const std::out_of_range&) { trapped = true; } assert(trapped); }
    {   const size_t SZ = 512; Memory mem(SZ); std::vector<uint8_t> shadow(SZ, 0);                                  // ⑤ 그림자 모형
        for (int step = 0; step < 200000; ++step) { int op = (int)(rng() % 5); size_t a = rng() % SZ, b = rng() % SZ, n = rng() % 80;
            if (op == 0) { int w = 1 << (rng() % 4); if (a + w <= SZ) { uint64_t v = rng(); mem.writeLE(a, v, w); for (int i = 0; i < w; ++i) shadow[a + i] = (uint8_t)(v >> (8 * i)); } }
            else if (op == 1) { if (a + n <= SZ) { uint8_t byte = (uint8_t)rng(); mem.fill(a, byte, n); std::memset(shadow.data() + a, byte, n); } }
            else if (op == 2) { if (a + n <= SZ && b + n <= SZ) { mem.copy(a, b, n); std::memmove(shadow.data() + a, shadow.data() + b, n); } }                                    // 겹치는 복사
            else if (op == 3) { assert(mem.read8(a) == shadow[a]); }
            else { int w = 1 << (rng() % 4); if (a + w <= SZ) { uint64_t v = 0; for (int i = 0; i < w; ++i) v |= (uint64_t)shadow[a + i] << (8 * i); assert(mem.readLE(a, w) == v); } } }
        assert(std::memcmp(mem.data(), shadow.data(), SZ) == 0); }
    std::cout << "CreateMemory: this machine is " << (hostLittle ? "little" : "big") << "-endian; the byte-array model matched the host representation, a byte-swap oracle, sign-extension casts, every boundary case (including wrapped addr+n) and 2*10^5 random operations against std::memmove" << std::endl;
    return 0;
}
// Time Complexity: 접근 O(n 바이트)
// Space Complexity: O(size)
```
## Alignment()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <new>
#include <random>
#include <vector>

// 정렬(alignment): 크기 N 인 자료형은 N 의 배수 주소에 놓는 것이 원칙이다 (CPU 가 한 번에 읽는 단위와 캐시 라인에 맞추기 위해).
// alignUp(a, N) = (a + N - 1) & ~(N - 1)   (N 은 2의 거듭제곱 — 그렇지 않으면 이 식은 틀린다)
// 검증: ① 손으로 고른 값  ② 정렬 1~4096(2의 거듭제곱 13 가지)과 주소 0~8191 *전부* 에서 alignUp/alignDown 의 정의(가장 작은/큰 배수)를 만족, 나눗셈 판과 같고 비트 마스크 식은 2의 거듭제곱이 아닌 정렬에서 틀린다
//        ③ std::align 을 직접 구현한 판이 무작위 (정렬, 크기, 버퍼, 남은 공간) 20 000 개에서 표준 구현과 같은 결과(포인터·남은 공간·nullptr)  ④ 과할당으로 직접 만든 정렬 할당기: 정렬 1~4096 으로 할당한 블록이 정렬되고 서로 겹치지 않으며 쓴 값이 보존·해제됨
//        ⑤ 정렬 안 맞는 주소의 읽기는 memcpy 로 — 오프셋 0~3 에서 읽은 32 비트 값이 바이트 조합과 같음, over-aligned 타입의 new, std::atomic 의 정렬
uintptr_t alignUp(uintptr_t addr, size_t a) { return (addr + a - 1) & ~(uintptr_t)(a - 1); }
uintptr_t alignDown(uintptr_t addr, size_t a) { return addr & ~(uintptr_t)(a - 1); }
uintptr_t alignUpAny(uintptr_t addr, size_t a) { return (addr + a - 1) / a * a; }               // 나눗셈 판: 어떤 a 에도 맞다
bool isAligned(const void* p, size_t a) { return (reinterpret_cast<uintptr_t>(p) & (a - 1)) == 0; }
void* myAlign(size_t alignment, size_t size, void*& ptr, size_t& space) {                         // std::align 과 같은 계약: 맞으면 정렬된 포인터를 돌려주고 ptr 를 옮기며 space 를 줄인다, 안 맞으면 nullptr 이고 아무것도 바꾸지 않는다
    uintptr_t p = reinterpret_cast<uintptr_t>(ptr); uintptr_t aligned = alignUp(p, alignment); size_t pad = (size_t)(aligned - p);
    if (space < pad || space - pad < size) return nullptr;
    ptr = reinterpret_cast<void*>(aligned); space -= pad; return ptr;
}
void* alignedAlloc(size_t size, size_t alignment) {                                              // 원래 포인터를 정렬된 블록 바로 앞에 저장해 두고 free 때 꺼낸다
    void* raw = std::malloc(size + alignment + sizeof(void*)); if (!raw) return nullptr;
    uintptr_t aligned = alignUp(reinterpret_cast<uintptr_t>(raw) + sizeof(void*), alignment);
    reinterpret_cast<void**>(aligned)[-1] = raw; return reinterpret_cast<void*>(aligned);
}
void alignedFree(void* p) { if (p) std::free(reinterpret_cast<void**>(p)[-1]); }
struct alignas(64) CacheLine { char bytes[64]; };
struct alignas(32) Vec32 { float v[8]; };

int main() {
    assert(alignUp(13, 8) == 16 && alignUp(16, 8) == 16 && alignUp(0, 64) == 0 && alignUp(65, 64) == 128);
    assert(alignof(int) == 4 && alignof(double) == 8 && alignof(char) == 1);
    alignas(64) char line[64];
    assert(isAligned(line, 64));                                      // alignas 로 캐시 라인 경계에 맞춘다
    int x; assert(isAligned(&x, alignof(int)));
    // std::align: 버퍼 안에서 요구 정렬을 만족하는 첫 주소를 찾는다
    char buf[100]; void* p = buf; size_t space = sizeof(buf);
    void* aligned = std::align(32, 10, p, space);
    assert(aligned && isAligned(aligned, 32) && space <= sizeof(buf));
    // ② 모든 (정렬, 주소) 에서 정의대로
    for (size_t a = 1; a <= 4096; a *= 2) for (uintptr_t addr = 0; addr < 8192; addr++) {
        uintptr_t up = alignUp(addr, a), down = alignDown(addr, a);
        assert(up % a == 0 && up >= addr && up - addr < a);                                      // 가장 작은 배수: 사이에 배수가 더 없다
        assert(down % a == 0 && down <= addr && addr - down < a && (up == down || up == down + a) && up == alignUpAny(addr, a) && alignUp(up, a) == up);
        assert((addr % a == 0) == (up == addr) && ((addr % a == 0) == (down == addr)));
    }
    long maskWrong = 0; for (size_t a : {3u, 5u, 6u, 12u, 24u, 100u}) for (uintptr_t addr = 0; addr < 500; addr++) maskWrong += alignUp(addr, a) != alignUpAny(addr, a);
    assert(maskWrong > 1000);                                                                    // 마스크 식은 2의 거듭제곱이 아닌 정렬에서 틀린다
    // ③ std::align 대조
    std::mt19937_64 rng(5); alignas(64) static char arena[512]; long nulls = 0, oks = 0;
    for (int it = 0; it < 20000; ++it) {
        size_t al = size_t(1) << (rng() % 9), sz = rng() % 200; size_t off = rng() % 300, sp = rng() % 400;
        void* a = arena + off; void* b = arena + off; size_t spA = sp, spB = sp;
        void* ra = std::align(al, sz, a, spA); void* rb = myAlign(al, sz, b, spB);
        assert(ra == rb && a == b && spA == spB);
        if (ra) { assert(isAligned(ra, al) && ra >= arena + off); ++oks; } else { assert(a == arena + off && spA == sp); ++nulls; }                                   // 실패하면 아무것도 바뀌지 않는다
    }
    assert(oks > 3000 && nulls > 3000);
    // ④ 정렬 할당기
    {   std::vector<std::pair<unsigned char*, size_t>> blocks; std::vector<size_t> aligns;
        for (int i = 0; i < 400; i++) { size_t al = size_t(1) << (rng() % 13), sz = 1 + rng() % 300; unsigned char* q = (unsigned char*)alignedAlloc(sz, al); assert(q && isAligned(q, al)); for (size_t k = 0; k < sz; k++) q[k] = (unsigned char)(i + k); blocks.push_back({q, sz}); aligns.push_back(al); }
        std::vector<std::pair<uintptr_t, uintptr_t>> ranges; for (auto& b : blocks) ranges.push_back({(uintptr_t)b.first, (uintptr_t)b.first + b.second}); std::sort(ranges.begin(), ranges.end());
        for (size_t i = 1; i < ranges.size(); i++) assert(ranges[i - 1].second <= ranges[i].first);                                // 겹치지 않는다
        for (size_t i = 0; i < blocks.size(); i++) for (size_t k = 0; k < blocks[i].second; k++) assert(blocks[i].first[k] == (unsigned char)(i + k));          // 쓴 값 보존
        for (auto& b : blocks) alignedFree(b.first); }
    // ⑤ 정렬 안 맞는 읽기, over-aligned new, atomic
    {   unsigned char raw[8] = {0, 1, 2, 3, 4, 5, 6, 7}; const uint16_t probe = 1; bool little = *reinterpret_cast<const unsigned char*>(&probe) == 1;
        for (int off = 0; off < 4; off++) { uint32_t v; std::memcpy(&v, raw + off, 4); uint32_t want = little ? (uint32_t)raw[off] | (uint32_t)raw[off + 1] << 8 | (uint32_t)raw[off + 2] << 16 | (uint32_t)raw[off + 3] << 24
                                                                  : (uint32_t)raw[off] << 24 | (uint32_t)raw[off + 1] << 16 | (uint32_t)raw[off + 2] << 8 | raw[off + 3]; assert(v == want); } }
    {   std::vector<CacheLine*> v; for (int i = 0; i < 200; i++) { CacheLine* c = new CacheLine(); assert(isAligned(c, 64)); v.push_back(c); } for (auto* c : v) delete c;
        Vec32* arr = new Vec32[10]; for (int i = 0; i < 10; i++) assert(isAligned(&arr[i], 32) && (uintptr_t)&arr[i] - (uintptr_t)&arr[0] == (uintptr_t)i * sizeof(Vec32)); delete[] arr;
        static_assert(sizeof(CacheLine) == 64 && alignof(CacheLine) == 64 && sizeof(Vec32) == 32, "alignas 는 크기를 정렬의 배수로 키운다");
        CacheLine two[2]; assert((uintptr_t)&two[1] - (uintptr_t)&two[0] == 64 && alignof(std::atomic<uint64_t>) == 8 && alignof(std::max_align_t) >= alignof(long double)); }
    std::cout << "Alignment verified: alignUp(13,8) = " << alignUp(13, 8) << "; std::align and the hand-written version agreed on " << oks + nulls << " random requests (" << nulls << " rejected)" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Padding()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>

// 패딩: 각 멤버를 자신의 정렬에 맞추려고 컴파일러가 사이에 빈 바이트를 끼운다.  구조체 전체 크기는 가장 큰 정렬의 배수가 된다.  규칙은 두 줄이다 — 멤버 i 의 오프셋 = 앞 멤버 끝을 align_i 의 배수로 올림,  전체 크기 = 마지막 멤버 끝을 max(align) 의 배수로 올림.
//  멤버를 정렬이 큰 것부터 배치하면 패딩이 줄어든다.  #pragma pack 은 패딩을 없애지만 정렬되지 않은 접근 비용을 치른다.
//  이 규칙을 직접 구현한 layout() 이 *실제 컴파일러*와 같은지 확인한다: ① char / short / int / double / char[3] 5 종으로 만든 4 멤버 구조체 전부(5^4 = 625 가지)에서 모든 오프셋·sizeof·alignof 가 컴파일러의 값과 같음
//  ② 모든 순열을 시도한 최소 크기와 "정렬 큰 것부터" 배치의 크기가 항상 같음(최적)  ③ 패딩 합 = sizeof − Σ멤버 크기이고 모든 오프셋이 정렬 배수, #pragma pack(1) 이면 패딩 0 · alignof 1  ④ 예: Bad 24 바이트 → Good 16 바이트.
struct Member { size_t size, align; };
struct Layout { std::vector<size_t> offset; size_t size, align; };
size_t alignUp(size_t x, size_t a) { return (x + a - 1) / a * a; }
Layout layout(const std::vector<Member>& m) { Layout L; size_t off = 0, maxAlign = 1; for (const Member& x : m) { off = alignUp(off, x.align); L.offset.push_back(off); off += x.size; maxAlign = std::max(maxAlign, x.align); } L.size = alignUp(off, maxAlign); L.align = maxAlign; return L; }
size_t bruteMinimum(std::vector<Member> m) { std::vector<size_t> idx(m.size()); std::iota(idx.begin(), idx.end(), 0); size_t best = ~(size_t)0; do { std::vector<Member> p; for (size_t i : idx) p.push_back(m[i]); best = std::min(best, layout(p).size); } while (std::next_permutation(idx.begin(), idx.end())); return best; }
size_t sortedSize(std::vector<Member> m) { std::stable_sort(m.begin(), m.end(), [](const Member& a, const Member& b) { return a.align > b.align; }); return layout(m).size; }

template <class A, class B, class C, class D> void check4() {
    struct S { A a; B b; C c; D d; }; S s; const char* base = reinterpret_cast<const char*>(&s);
    std::vector<Member> m = {{sizeof(A), alignof(A)}, {sizeof(B), alignof(B)}, {sizeof(C), alignof(C)}, {sizeof(D), alignof(D)}}; Layout L = layout(m);
    assert(L.offset[0] == 0 && L.offset[1] == (size_t)(reinterpret_cast<const char*>(&s.b) - base) && L.offset[2] == (size_t)(reinterpret_cast<const char*>(&s.c) - base) && L.offset[3] == (size_t)(reinterpret_cast<const char*>(&s.d) - base));      // ① 오프셋
    assert(L.size == sizeof(S) && L.align == alignof(S) && sizeof(S) % alignof(S) == 0);
    for (size_t i = 0; i < 4; ++i) assert(L.offset[i] % m[i].align == 0);                                                                                                                                                                  // ③ 정렬 배수
    size_t payload = 0; for (auto& x : m) payload += x.size; assert(sizeof(S) >= payload);
    assert(sortedSize(m) == bruteMinimum(m) && sortedSize(m) <= sizeof(S));                                                                                                                                                                // ② 정렬 큰 것부터 = 최소
}
template <class... Ts> struct TypeList {};
template <class... Ts, class F> void forEachType(TypeList<Ts...>, F f) { (f(Ts{}), ...); }
struct Arr3 { char v[3]; };                          // char[3] 처럼 크기 3 · 정렬 1 인 멤버
struct Bad  { char a; int64_t b; char c; };          // a(1) + 7 패딩 + b(8) + c(1) + 7 패딩 = 24
struct Good { int64_t b; char a; char c; };          // b(8) + a(1) + c(1) + 6 패딩 = 16
#pragma pack(push, 1)
struct Packed { char a; int64_t b; char c; };        // 패딩 없음 = 10
#pragma pack(pop)
struct alignas(16) Wide { char a; };                 // 정렬 16 → 크기 16

int main() {
    using Types = TypeList<char, short, int, double, Arr3>; int combos = 0;
    forEachType(Types{}, [&](auto a) { using A = decltype(a);
        forEachType(Types{}, [&](auto b) { using B = decltype(b);
            forEachType(Types{}, [&](auto c) { using C = decltype(c);
                forEachType(Types{}, [&](auto d) { using D = decltype(d); check4<A, B, C, D>(); ++combos; }); }); }); });
    assert(combos == 625);
    assert(offsetof(Bad, b) == 8 && offsetof(Bad, c) == 16 && sizeof(Bad) == 24 && sizeof(Good) == 16 && sizeof(Packed) == 10 && alignof(Packed) == 1 && sizeof(Wide) == 16 && alignof(Wide) == 16);                                // ④ 예
    assert(layout({{1, 1}, {8, 8}, {1, 1}}).size == 24 && layout({{8, 8}, {1, 1}, {1, 1}}).size == 16 && sortedSize({{1, 1}, {8, 8}, {1, 1}}) == 16 && bruteMinimum({{1, 1}, {8, 8}, {1, 1}}) == 16);
    assert(offsetof(Good, a) == 8 && offsetof(Good, c) == 9);
    std::cout << "Padding: the offset/size rule matched the compiler for all " << combos << " four-member structs over five member types, sorting by alignment always reached the brute-force minimum, and reordering Bad (" << sizeof(Bad) << " bytes) into Good (" << sizeof(Good) << " bytes) saved " << sizeof(Bad) - sizeof(Good) << " bytes" << std::endl;
    return 0;
}
// Time Complexity: layout O(멤버 수), 최소 크기 탐색 O(멤버 수!) (검증용), 정렬 배치 O(m log m)
// Space Complexity: O(멤버 수)
```
## MemoryDump()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

// 메모리 덤프: 주소, 16진수 바이트, 오른쪽에 출력 가능한 ASCII 를 보여 주는 hexdump -C 형식.  디버깅과 바이너리 분석의 기본 도구.  실제 hexdump -C 처럼 *바로 앞 줄과 똑같은 줄은 `*` 한 줄로 줄이고*, 마지막에 전체 길이를 주소로 한 줄 더 찍는다.
//  덤프가 정말 정보를 보존하는지 확인하려고 *역파서* undump() 를 함께 만든다 (`*` 는 앞 줄을 다음 주소까지 반복).  ① 형식: 알려진 문자열의 정확한 출력  ② 길이 0..300 의 무작위·영(0)·16 바이트 주기 버퍼에서 undump(hexdump(x)) == x  ③ 영으로 가득한 64 바이트는 `*` 로 압축됨
//  ④ 100 만 바이트 영 버퍼의 덤프는 몇 줄뿐이고 되돌려도 같다  ⑤ 출력 가능 문자(32..126) 외에는 '.' 으로 보이며 ASCII 칸의 글자 수 = 그 줄의 바이트 수  ⑥ 잘못된 덤프(주소 불일치·16진수 아님)는 거부.
std::string hexdump(const void* data, size_t n) {
    const unsigned char* p = (const unsigned char*)data; std::string out; char buf[32]; if (n == 0) return out; bool squeezing = false;
    for (size_t off = 0; off < n; off += 16) {
        if (off > 0 && off + 16 <= n && std::equal(p + off, p + off + 16, p + off - 16)) { if (!squeezing) { out += "*\n"; squeezing = true; } continue; }                          // 앞 줄과 같은 줄은 건너뛴다
        squeezing = false; std::snprintf(buf, sizeof buf, "%08zx  ", off); out += buf;
        for (size_t i = 0; i < 16; ++i) { if (off + i < n) { std::snprintf(buf, sizeof buf, "%02x ", p[off + i]); out += buf; } else out += "   "; if (i == 7) out += " "; }
        out += " |"; for (size_t i = 0; i < 16 && off + i < n; ++i) out += (p[off + i] >= 32 && p[off + i] < 127) ? (char)p[off + i] : '.'; out += "|\n"; }
    std::snprintf(buf, sizeof buf, "%08zx\n", n); out += buf; return out; }
int hexval(char c) { if (c >= '0' && c <= '9') return c - '0'; if (c >= 'a' && c <= 'f') return c - 'a' + 10; return -1; }
std::vector<unsigned char> undump(const std::string& dump) {                                                       // 역파서
    std::vector<unsigned char> out; size_t pos = 0; bool pendingStar = false;
    while (pos < dump.size()) { size_t eol = dump.find('\n', pos); if (eol == std::string::npos) throw std::runtime_error("no newline"); std::string line = dump.substr(pos, eol - pos); pos = eol + 1;
        if (line == "*") { pendingStar = true; continue; }
        if (line.size() < 8) throw std::runtime_error("short line"); size_t off = 0; for (int i = 0; i < 8; ++i) { int h = hexval(line[i]); if (h < 0) throw std::runtime_error("bad address"); off = off * 16 + (size_t)h; }
        if (pendingStar) { if (out.size() < 16 || off < out.size() || (off - out.size()) % 16) throw std::runtime_error("bad squeeze"); std::vector<unsigned char> block(out.end() - 16, out.end()); while (out.size() < off) out.insert(out.end(), block.begin(), block.end()); pendingStar = false; }
        if (off != out.size()) throw std::runtime_error("address mismatch");
        if (line.size() == 8) break;                                                                                // 마지막 줄: 전체 길이
        for (size_t i = 0; i < 16; ++i) { size_t col = 10 + i * 3 + (i >= 8 ? 1 : 0); if (col + 1 >= line.size() || line[col] == ' ') break; int hi = hexval(line[col]), lo = hexval(line[col + 1]); if (hi < 0 || lo < 0) throw std::runtime_error("bad hex"); out.push_back((unsigned char)(hi * 16 + lo)); } }
    return out; }

int main() {
    const char text[] = "Hello, memory!\n"; std::string dump = hexdump(text, sizeof(text) - 1);
    assert(dump == "00000000  48 65 6c 6c 6f 2c 20 6d  65 6d 6f 72 79 21 0a     |Hello, memory!.|\n0000000f\n");               // ① hexdump -C 와 같은 형식
    assert(hexdump(text, 0).empty());
    uint32_t v = 0x11223344; std::string d2 = hexdump(&v, 4); assert(d2.find("44 33 22 11") != std::string::npos || d2.find("11 22 33 44") != std::string::npos);
    std::mt19937 rng(1003);
    for (int n = 0; n <= 300; ++n) for (int kind = 0; kind < 4; ++kind) { std::vector<unsigned char> buf(n); for (int i = 0; i < n; ++i) buf[i] = kind == 0 ? (unsigned char)rng() : kind == 1 ? 0 : kind == 2 ? (unsigned char)(i % 16 * 17) : (unsigned char)(i / 40);           // 무작위 / 영 / 16 바이트 주기 / 긴 반복
        std::string d = hexdump(buf.data(), buf.size()); assert(undump(d) == buf); }                                                                                      // ②
    { std::vector<unsigned char> zeros(64, 0); assert(hexdump(zeros.data(), 64) == "00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|\n*\n00000040\n"); }                      // ③
    { std::vector<unsigned char> big(1000000, 0); std::string d = hexdump(big.data(), big.size()); assert(std::count(d.begin(), d.end(), '\n') == 3 && undump(d) == big); }                                  // ④
    {   std::vector<unsigned char> raw(40); for (int i = 0; i < 40; ++i) raw[i] = (unsigned char)(i * 7); raw[5] = 'A'; raw[6] = 0x7f; raw[7] = 0x1f; std::string d = hexdump(raw.data(), raw.size()); size_t bar = d.find('|'), end = d.find('|', bar + 1); assert(end - bar - 1 == 16);   // ⑤ 첫 줄 ASCII 칸 = 16 글자
        for (size_t i = bar + 1; i < end; ++i) assert(d[i] == '.' || (d[i] >= 32 && d[i] < 127)); assert(d.substr(bar + 1 + 6, 2) == ".." && d[bar + 1 + 5] == 'A'); }
    for (const char* bad : {"00000000  4g 00\n", "00000001  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|\n", "0000\n", "*\n00000040\n"}) { bool threw = false; try { undump(bad); } catch (const std::runtime_error&) { threw = true; } assert(threw); }          // ⑥ 거부
    std::cout << dump;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
# Part 2. 프로세스 메모리
## TextSegment()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

// 텍스트(코드) 세그먼트: 컴파일된 기계어가 들어 있는 읽기+실행 전용 영역.  함수의 주소가 여기에 속하고, 문자열 리터럴은 인접한 읽기 전용 영역(.rodata)에 놓인다.
//  프로세스 주소 공간(낮은 주소 → 높은 주소): 코드 < 읽기 전용 데이터 < 초기화된 전역(.data) < 초기화 안 된 전역(.bss) < 힙(위로 성장) ... 스택(아래로 성장).
//  Linux 에서는 `/proc/self/maps` 가 이 지도를 그대로 보여 준다: 줄마다 `시작-끝 권한 오프셋 장치 inode 이름`.  각 변수·함수의 주소가 어느 영역에 속하는지 *권한까지* 찾아 확인한다.
//  ① 함수 주소는 실행 가능(x)·쓰기 불가(w 없음) 영역, 문자열 리터럴은 쓰기 불가 영역, 초기화된/안 된 전역·힙·스택은 읽기+쓰기 영역이며 실행 불가  ② 스택 변수는 "[stack]" 영역, 작은 new 는 "[heap]" 영역(또는 익명 매핑)
//  ③ 이 프로세스에 *쓰기+실행 동시 허용(rwx) 영역이 없다* (W^X)  ④ 영역이 겹치지 않고 오름차순  ⑤ 코드 주소 < 힙 < 스택 (x86-64 Linux 의 전형적 배치).  Linux 가 아니면 주소 순서만 확인한다.
// audit: no-sanitize (섹션 주소 비교는 새니타이저의 섀도 메모리 배치에서 성립하지 않는다)
struct Map { uintptr_t lo, hi; std::string perms, name; };
std::vector<Map> readMaps() {
    std::vector<Map> maps; std::ifstream f("/proc/self/maps"); std::string line;
    while (std::getline(f, line)) { std::istringstream in(line); std::string range, perms, offset, dev, inode, name; in >> range >> perms >> offset >> dev >> inode; std::getline(in, name); size_t b = name.find_first_not_of(' '); name = b == std::string::npos ? "" : name.substr(b);
        size_t dash = range.find('-'); maps.push_back({(uintptr_t)std::stoull(range.substr(0, dash), nullptr, 16), (uintptr_t)std::stoull(range.substr(dash + 1), nullptr, 16), perms, name}); }
    return maps; }
const Map* findMap(const std::vector<Map>& maps, uintptr_t addr) { for (auto& m : maps) if (addr >= m.lo && addr < m.hi) return &m; return nullptr; }
int initialized = 7;
int uninitialized;
const char rodataArray[] = "constant data in .rodata";
void someFunction() {}

int main() {
    const char* literal = "string literal"; int local = 0; int* heap = new int(1);
    uintptr_t code = (uintptr_t)(void*)&someFunction, ro = (uintptr_t)literal, data = (uintptr_t)&initialized, bss = (uintptr_t)&uninitialized, hp = (uintptr_t)heap, stack = (uintptr_t)&local, roArr = (uintptr_t)rodataArray;
    std::cout << std::hex << "text=" << code << " rodata=" << ro << " data=" << data << " bss=" << bss << " heap=" << hp << " stack=" << stack << std::endl;
    assert(std::strcmp(literal, "string literal") == 0 && initialized == 7 && uninitialized == 0);
#if defined(__linux__)
    std::vector<Map> maps = readMaps(); assert(!maps.empty());
    auto perm = [&](uintptr_t a) { const Map* m = findMap(maps, a); assert(m != nullptr); return m->perms; };
    assert(perm(code)[2] == 'x' && perm(code)[1] == '-');                                                                    // ① 코드: r-x
    assert(perm(ro)[1] == '-' && perm(roArr)[1] == '-' && perm(ro)[2] == '-');                                               //    상수: 쓰기 불가
    for (uintptr_t a : {data, bss, hp, stack}) { std::string p = perm(a); assert(p[0] == 'r' && p[1] == 'w' && p[2] == '-'); }  //    전역·힙·스택: rw-
    const Map* sm = findMap(maps, stack); assert(sm->name == "[stack]");                                                     // ② 스택 영역 이름
    const Map* hm = findMap(maps, hp); assert(hm->name == "[heap]" || hm->name.empty());
    for (auto& m : maps) assert(m.perms.substr(0, 3) != "rwx");                                                              // ③ W^X
    for (size_t i = 1; i < maps.size(); ++i) assert(maps[i - 1].hi <= maps[i].lo);                                           // ④ 겹치지 않고 오름차순
    assert(code < hp && hp < stack);                                                                                          // ⑤
    int executable = 0, writable = 0, readonly = 0; for (auto& m : maps) { executable += m.perms[2] == 'x'; writable += m.perms[1] == 'w'; readonly += m.perms == "r--p"; } assert(executable > 0 && writable > 0 && readonly > 0);
    std::cout << std::dec << "TextSegment: " << maps.size() << " mappings (" << executable << " executable, " << writable << " writable, none rwx); code is " << perm(code) << ", literal " << perm(ro) << ", stack " << perm(stack) << " in " << sm->name << std::endl;
#else
    assert(code != 0 && ro != 0 && stack != 0);
#endif
    delete heap;
    return 0;
}
// Time Complexity: O(매핑 수)
// Space Complexity: O(매핑 수)
```
## DataSegment()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <thread>
#include <vector>
#if defined(__linux__)
#include <sys/stat.h>
#include <unistd.h>
extern "C" char etext, edata, end, __bss_start, __data_start;      // GNU ld / glibc 가 정의하는 구역 경계 기호
#endif

// 데이터 세그먼트: 정적 저장 기간(static storage duration) 변수가 사는 곳.
//  .data = 0 이 아닌 초기값이 있는 전역/static (초기값이 실행 파일에 저장됨)
//  .bss  = 초기값이 없거나 0 인 전역/static (실행 파일에는 크기만 기록되고 로드될 때 0 으로 채워진다)
// 그래서 큰 배열을 전역으로 선언해도 실행 파일 크기는 거의 늘지 않는다.  static 지역 변수도 여기에 있어 호출 사이에 값이 유지된다
// 검증: ① 값과 0 초기화, 호출 사이 유지  ② Linux: 링커 기호로 구역 경계를 얻어 `.data` 변수가 [etext, edata) 에, `.bss` 변수가 [__bss_start, end) 에 있음을 확인 — 문자열 리터럴·스택·힙은 어느 구역에도 속하지 않음
//        ③ 실행 파일 크기가 bss 배열(16 MB)보다 훨씬 작음  ④ 요구 페이징: 0 으로 시작하는 큰 배열은 건드리기 전까지 실제 메모리(RSS)를 거의 쓰지 않고, 전부 건드리면 그 크기만큼 늘어난다  ⑤ 함수 안 static 은 여러 스레드가 동시에 처음 불러도 초기화가 *정확히 한 번* (C++11 보장)
// audit: no-sanitize (새니타이저가 전역을 재배치하고 그림자 메모리를 써서 구역 경계와 상주 메모리 측정이 달라진다)
int withValue = 42;                 // .data
int zeroed[4000000];                // .bss: 16MB 인데 파일에는 저장되지 않음
static int counter;                 // .bss, 이 파일에서만 보임
const char* literal = "text segment string";                      // 포인터 변수는 .data, 가리키는 문자열은 읽기 전용 구역

int nextId() { static int id = 100; return id++; }       // static 지역: 첫 호출 때 한 번 초기화
std::atomic<int> initRuns{0};
int expensiveInit() { initRuns.fetch_add(1); return 7; }
int lazyValue() { static int v = expensiveInit(); return v; }
long residentPages() {                                                                              // /proc/self/statm 의 두 번째 값 = 상주 페이지 수
#if defined(__linux__)
    FILE* f = fopen("/proc/self/statm", "r"); long a = 0, r = 0; if (f) { if (fscanf(f, "%ld %ld", &a, &r) != 2) r = -1; fclose(f); } return r;
#else
    return -1;
#endif
}

int main() {
    assert(withValue == 42);
    for (int i = 0; i < 4000000; i += 99999) assert(zeroed[i] == 0);   // 전부 0 으로 시작 (보장됨)
    assert(counter == 0);
    assert(nextId() == 100 && nextId() == 101 && nextId() == 102);     // 호출 사이에 값 유지
#if defined(__linux__)
    uintptr_t e0 = (uintptr_t)&etext, d0 = (uintptr_t)&__data_start, e1 = (uintptr_t)&edata, b0 = (uintptr_t)&__bss_start, b1 = (uintptr_t)&end;
    assert(e0 <= d0 && d0 <= e1 && e1 <= b0 && b0 <= b1);                                              // 구역 순서: 코드 < 읽기 전용 상수 < 초기화된 데이터 < bss
    assert((uintptr_t)&withValue >= d0 && (uintptr_t)&withValue < e1 && (uintptr_t)&literal >= d0 && (uintptr_t)&literal < e1);       // .data
    assert((uintptr_t)zeroed >= b0 && (uintptr_t)(zeroed + 4000000) <= b1 && (uintptr_t)&counter >= b0 && (uintptr_t)&counter < b1);         // .bss
    int onStack = 0; void* onHeap = ::operator new(16);
    auto inData = [&](uintptr_t a) { return (a >= d0 && a < b1); };
    assert(!inData((uintptr_t)&onStack) && !inData((uintptr_t)onHeap) && !inData((uintptr_t)literal) && (uintptr_t)literal >= e0 && (uintptr_t)literal < d0);    // 스택·힙은 데이터 세그먼트가 아니고, 문자열 리터럴은 코드와 데이터 사이의 읽기 전용 구역(.rodata)
    ::operator delete(onHeap);
    struct stat st; assert(stat("/proc/self/exe", &st) == 0 && (size_t)st.st_size < sizeof(zeroed) / 2);       // ③ 파일이 bss 배열 크기의 절반도 안 된다
    long before = residentPages(); assert(before > 0);                                                   // ④ 요구 페이징
    zeroed[5] = 9; long afterOne = residentPages(); assert(afterOne - before <= 8);                        // 한 칸만 건드리면 페이지 한두 개
    for (size_t i = 0; i < 4000000; i += 1024) zeroed[i] = 1;                                              // 4 KB 마다 하나씩 = 모든 페이지
    long afterAll = residentPages(); long grown = afterAll - afterOne; assert(grown > 3500 && grown < 4600);           // 16 MB = 4096 페이지
#else
    zeroed[5] = 9;
#endif
    counter++;
    assert(zeroed[5] == 9 && counter == 1);
    // ⑤ 스레드가 동시에 처음 부른다
    {   std::atomic<int> go{0}; std::vector<std::thread> ts; std::atomic<int> sum{0};
        for (int t = 0; t < 8; t++) ts.emplace_back([&] { while (!go.load()) {} sum.fetch_add(lazyValue()); });
        go = 1; for (auto& th : ts) th.join(); assert(initRuns == 1 && sum == 8 * 7); }
    std::cout << "DataSegment: zero-initialized bss array of " << sizeof(zeroed) / 1024 << " KB" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: bss 는 실행 파일 크기에 영향 없음
```
## EnvironmentVariable()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <map>
#include <string>
#include <vector>
#if defined(__unix__) || defined(__APPLE__)
#include <sys/wait.h>
#include <unistd.h>
extern char** environ;
static char** initialEnviron = environ;                              // 프로그램 시작 직후의 환경 배열 (setenv 가 배열을 새로 만들면 environ 과 달라진다)
#endif

// 환경 변수: 프로세스가 시작될 때 부모로부터 "NAME=value" 문자열 배열로 복사받는다 (스택의 맨 위쪽에 놓인다).
// getenv/setenv 는 이 배열을 읽고 고친다.  fork 한 자식은 부모의 환경을 그대로 물려받고(복사본이라 자식의 변경은 부모에 보이지 않는다), exec 는 환경을 그대로 넘기거나 envp 로 명시한 환경으로 갈아 끼운다
// 검증(POSIX): ① setenv/getenv/unsetenv 의 기본 동작과 overwrite 규칙  ② environ 의 모든 "NAME=value" 항목을 직접 쪼갠 결과가 getenv 와 일치 (이름에 '=' 가 없고 처음 나온 항목이 우선)
//        ③ 잘못된 이름("", "A=B")은 EINVAL 로 거부, 값에는 '=' 가 들어갈 수 있고, 이름은 대소문자를 구분  ④ 변수 500 개를 넣었다 모두 지우면 환경 배열이 원래 항목 집합으로 돌아오고, 배열이 실제로 새로 만들어졌으며 시작 시 항목은 스택 위쪽 주소에 있음
//        ⑤ fork+exec 로 /bin/sh 를 띄워 자식이 본 환경을 파이프로 읽는다: 상속, envp 로 명시, 빈 envp, unsetenv 후 — 그리고 exec 없는 fork 의 자식이 바꾼 값은 부모에 보이지 않는다
#if defined(__unix__) || defined(__APPLE__)
std::string runShell(const char* script, char* const envp[]) {                                      // envp 가 nullptr 이면 현재 환경을 물려준다
    int fd[2]; int pr = pipe(fd); assert(pr == 0 && access("/bin/sh", X_OK) == 0); (void)pr;
    pid_t pid = fork(); assert(pid >= 0);
    if (pid == 0) { dup2(fd[1], 1); close(fd[0]); close(fd[1]); char* argv[] = {(char*)"sh", (char*)"-c", (char*)script, nullptr}; if (envp) execve("/bin/sh", argv, envp); else execv("/bin/sh", argv); _exit(127); }
    close(fd[1]); std::string out; char buf[256]; ssize_t n; while ((n = read(fd[0], buf, sizeof buf)) > 0) out.append(buf, (size_t)n); close(fd[0]);
    int st = 0; waitpid(pid, &st, 0); assert(WIFEXITED(st) && WEXITSTATUS(st) == 0); return out;
}
std::vector<std::string> snapshot() { std::vector<std::string> v; for (char** e = environ; *e; e++) v.push_back(*e); std::sort(v.begin(), v.end()); return v; }
#endif

int main() {
    assert(std::getenv("DS_PROJECT_DEMO") == nullptr);
#if defined(__unix__) || defined(__APPLE__)
    int local = 0;
    setenv("DS_PROJECT_DEMO", "hello", 1);
    assert(std::string(std::getenv("DS_PROJECT_DEMO")) == "hello");
    bool found = false;
    for (char** e = environ; *e; e++) if (std::strcmp(*e, "DS_PROJECT_DEMO=hello") == 0) found = true;   // 배열에 "NAME=value" 로 들어 있다
    assert(found);
    setenv("DS_PROJECT_DEMO", "world", 0);                          // overwrite=0: 이미 있으면 바꾸지 않는다
    assert(std::string(std::getenv("DS_PROJECT_DEMO")) == "hello");
    setenv("DS_PROJECT_DEMO", "world", 1); assert(std::string(std::getenv("DS_PROJECT_DEMO")) == "world");
    unsetenv("DS_PROJECT_DEMO");
    assert(std::getenv("DS_PROJECT_DEMO") == nullptr && unsetenv("DS_NEVER_SET") == 0);
    // ② environ 을 직접 쪼갠 결과가 getenv 와 같다
    {   std::map<std::string, std::string> first; size_t entries = 0;
        for (char** e = environ; *e; e++) { std::string s = *e; size_t eq = s.find('='); if (eq == std::string::npos || eq == 0) continue; ++entries; first.emplace(s.substr(0, eq), s.substr(eq + 1)); }                // 같은 이름이 또 나와도 처음 것을 유지
        assert(entries > 0 && !first.empty()); for (auto& kv : first) { const char* v = std::getenv(kv.first.c_str()); assert(v && kv.second == v); } }
    // ③ 이름 규칙
    errno = 0; assert(setenv("", "x", 1) == -1 && errno == EINVAL); errno = 0; assert(setenv("A=B", "x", 1) == -1 && errno == EINVAL && std::getenv("A") == nullptr);
    setenv("DS_EQ", "a=b=c", 1); assert(std::string(std::getenv("DS_EQ")) == "a=b=c"); setenv("Ds_Eq", "lower", 1); assert(std::string(std::getenv("DS_EQ")) == "a=b=c" && std::string(std::getenv("Ds_Eq")) == "lower");
    setenv("DS_EMPTY", "", 1); assert(std::getenv("DS_EMPTY") != nullptr && std::string(std::getenv("DS_EMPTY")).empty());                // 값이 비어 있는 것과 없는 것은 다르다
    unsetenv("DS_EQ"); unsetenv("Ds_Eq"); unsetenv("DS_EMPTY");
    // ④ 개수 불변식과 배열 재할당
    {   std::vector<std::string> before = snapshot(); char** arrayBefore = environ;
        for (int i = 0; i < 500; i++) setenv(("DS_VAR_" + std::to_string(i)).c_str(), std::to_string(i * 3).c_str(), 1);
        assert(snapshot().size() == before.size() + 500 && std::string(std::getenv("DS_VAR_77")) == "231" && environ != initialEnviron);       // 항목이 늘어 새 배열이 만들어졌다
        for (int i = 0; i < 500; i++) assert(unsetenv(("DS_VAR_" + std::to_string(i)).c_str()) == 0);
        assert(snapshot() == before); (void)arrayBefore;
#if defined(__linux__)
        assert((uintptr_t)initialEnviron[0] > (uintptr_t)&local);                                                                          // 시작 시 환경 문자열은 main 의 지역 변수보다 위(스택 맨 위쪽)
#endif
    }
    // ⑤ fork + exec
    setenv("DS_A", "from_parent", 1); unsetenv("DS_B");
    assert(runShell("printf '%s|%s' \"$DS_A\" \"$DS_B\"", nullptr) == "from_parent|");                                    // 상속
    { char* only[] = {(char*)"DS_B=explicit", nullptr}; assert(runShell("printf '%s|%s' \"$DS_A\" \"$DS_B\"", only) == "|explicit"); }                  // envp 로 명시하면 부모 환경은 넘어가지 않는다
    { char* none[] = {nullptr}; assert(runShell("printf '%s|%s' \"$DS_A\" \"$DS_B\"", none) == "|"); }                      // 빈 환경
    unsetenv("DS_A"); assert(runShell("printf '%s' \"[$DS_A]\"", nullptr) == "[]");                                         // 부모가 지운 변수는 자식도 못 본다
    {   setenv("DS_COW", "parent", 1); int pfd[2]; int pr = pipe(pfd); assert(pr == 0); (void)pr; pid_t pid = fork();
        if (pid == 0) { setenv("DS_COW", "child_changed", 1); const char* v = std::getenv("DS_COW"); ssize_t w = write(pfd[1], v, std::strlen(v)); (void)w; _exit(0); }       // exec 없는 fork: 자식이 바꾼 값
        close(pfd[1]); char buf[64] = {0}; ssize_t n = read(pfd[0], buf, sizeof buf - 1); (void)n; close(pfd[0]); int st = 0; waitpid(pid, &st, 0);
        assert(std::string(buf) == "child_changed" && std::string(std::getenv("DS_COW")) == "parent"); unsetenv("DS_COW"); }       // 부모는 그대로
#endif
    std::cout << "EnvironmentVariable verified." << std::endl;
    return 0;
}
// Time Complexity: getenv O(환경 변수 수)
// Space Complexity: O(환경 크기)
```
## CommandLineArgument()
### 대표코드
```cpp
#include <cassert>
#include <cerrno>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

// 명령줄 인자: main(int argc, char* argv[]).  argv[0] 은 프로그램 이름, argv[argc] 는 항상 nullptr.  문자열들은 환경 변수와 함께 스택 맨 위쪽에 연속으로 놓여 있다.
//  관례: `--key value`, `--key=value`, `--flag`, 짧은 옵션 `-k value` / `-kvalue`, 짧은 플래그 묶음 `-abc`, 그리고 `--` 뒤는 전부 위치 인자.  모호함(값이 `-5` 처럼 `-` 로 시작할 때)을 없애려고 *옵션 사양을 먼저 선언*한다: 값을 받는 옵션은 다음 토큰을 무조건 값으로 삼는다.
//  ① 실제 argc/argv 구조(argv[argc] == nullptr)  ② 생성 기반 검증: 무작위로 (옵션, 값, 표기 방식, 위치 인자, `--` 위치)를 골라 *인자 열을 만들고*, 파서가 원래 선택을 정확히 복원  ③ 까다로운 값: 빈 값(`--k=`), 값에 `=` 포함(`--k=a=b`), 음수(`--n -5`), 공백 포함
//  ④ 오류: 값 누락, 모르는 옵션, 플래그에 `=값`, 정수가 아닌 값·범위 초과  ⑤ 같은 옵션을 여러 번 주면 마지막 값이 이긴다.
struct Spec { std::set<std::string> flags, valued; std::map<char, std::string> shortName; };       // 긴 이름 목록 + 짧은 이름 → 긴 이름
struct Parsed { std::set<std::string> flags; std::map<std::string, std::string> values; std::vector<std::string> positional; };
Parsed parse(const Spec& spec, const std::vector<std::string>& args) {
    Parsed r; bool dashdash = false;
    for (size_t i = 0; i < args.size(); ++i) { const std::string& a = args[i];
        if (dashdash || a.size() < 2 || a[0] != '-') { r.positional.push_back(a); continue; }
        if (a == "--") { dashdash = true; continue; }
        if (a[1] == '-') { std::string body = a.substr(2), key = body, val; size_t eq = body.find('='); bool hasEq = eq != std::string::npos; if (hasEq) { key = body.substr(0, eq); val = body.substr(eq + 1); }
            if (spec.flags.count(key)) { if (hasEq) throw std::runtime_error("flag takes no value: " + key); r.flags.insert(key); }
            else if (spec.valued.count(key)) { if (!hasEq) { if (i + 1 >= args.size()) throw std::runtime_error("missing value: " + key); val = args[++i]; } r.values[key] = val; }
            else throw std::runtime_error("unknown option: " + key); continue; }
        for (size_t k = 1; k < a.size(); ++k) { auto it = spec.shortName.find(a[k]); if (it == spec.shortName.end()) throw std::runtime_error(std::string("unknown option: -") + a[k]); const std::string& name = it->second;      // -abc 묶음
            if (spec.flags.count(name)) r.flags.insert(name);
            else { std::string val = a.substr(k + 1); if (val.empty()) { if (i + 1 >= args.size()) throw std::runtime_error("missing value: " + name); val = args[++i]; } r.values[name] = val; break; } } }          // 값 옵션은 나머지 글자 또는 다음 토큰을 먹는다
    return r; }
long toInt(const std::string& s, long lo, long hi) { if (s.empty()) throw std::runtime_error("not an integer"); char* end = nullptr; errno = 0; long v = std::strtol(s.c_str(), &end, 10); if (*end != '\0' || errno == ERANGE) throw std::runtime_error("not an integer: " + s); if (v < lo || v > hi) throw std::runtime_error("out of range: " + s); return v; }

int main(int argc, char* argv[]) {
    assert(argc >= 1 && argv[0] != nullptr && argv[argc] == nullptr);                                                  // ① 배열은 널 포인터로 끝난다
    Spec spec; spec.flags = {"verbose", "quiet", "force"}; spec.valued = {"name", "count", "path", "tag"}; spec.shortName = {{'v', "verbose"}, {'q', "quiet"}, {'f', "force"}, {'n', "name"}, {'c', "count"}, {'p', "path"}, {'t', "tag"}};
    { Parsed p = parse(spec, {"--name", "kim", "--verbose", "--count=3", "file.txt", "-vq", "-n5", "--", "--force", "-x"}); assert(p.values["name"] == "5" && p.values["count"] == "3" && p.flags == (std::set<std::string>{"verbose", "quiet"}) && p.positional == (std::vector<std::string>{"file.txt", "--force", "-x"})); }
    std::mt19937 rng(1005); const char* flagLong[] = {"verbose", "quiet", "force"}; const char flagShort[] = {'v', 'q', 'f'}; const char* valLong[] = {"name", "count", "path", "tag"}; const char valShort[] = {'n', 'c', 'p', 't'};
    auto randValue = [&]() { static const char* pool[] = {"x", "", "a=b", "-5", "hello world", "3", "--weird", "-", "0x10", "a b=c d", "한글"}; return std::string(pool[rng() % 11]); };
    for (int it = 0; it < 5000; ++it) {                                                                                // ② 생성 기반 검증
        Parsed want; std::vector<std::string> args; std::vector<std::string> positional; int pieces = (int)(rng() % 8);
        for (int k = 0; k < pieces; ++k) { int kind = (int)(rng() % 4);
            if (kind == 0) { int f = (int)(rng() % 3); want.flags.insert(flagLong[f]); args.push_back(rng() % 2 ? std::string("--") + flagLong[f] : std::string("-") + flagShort[f]); }
            else if (kind == 1) { int f = (int)(rng() % 3), g = (int)(rng() % 3); want.flags.insert(flagLong[f]); want.flags.insert(flagLong[g]); args.push_back(std::string("-") + flagShort[f] + flagShort[g]); }          // 묶음
            else if (kind == 2) { int v = (int)(rng() % 4); std::string val = randValue(); want.values[valLong[v]] = val; int style = (int)(rng() % 4);
                if (style == 0) { args.push_back(std::string("--") + valLong[v]); args.push_back(val); } else if (style == 1) args.push_back(std::string("--") + valLong[v] + "=" + val); else if (style == 2) { args.push_back(std::string("-") + valShort[v]); args.push_back(val); } else if (!val.empty()) args.push_back(std::string("-") + valShort[v] + val); else { want.values[valLong[v]] = ""; args.push_back(std::string("--") + valLong[v] + "="); } }
            else { std::string pos = rng() % 3 ? "file" + std::to_string(rng() % 100) : std::string("-"); want.positional.push_back(pos); args.push_back(pos); } }
        if (rng() % 3 == 0) { args.push_back("--"); int extra = (int)(rng() % 3); for (int e = 0; e < extra; ++e) { std::string pos = rng() % 2 ? "--force" : "-x"; want.positional.push_back(pos); args.push_back(pos); } }
        // 같은 옵션이 여러 번이면 마지막 값 (want.values 는 덮어쓰기로 이미 마지막 값) — 단, 짧은 값 옵션의 -nVAL 는 val 이 빈 문자열이 아닐 때만 생성했으므로 일치
        Parsed got = parse(spec, args); assert(got.flags == want.flags && got.values == want.values && got.positional == want.positional); }                                         // ⑤ 마지막 값 우선도 포함
    for (const std::vector<std::string>& bad : std::vector<std::vector<std::string>>{{"--name"}, {"-n"}, {"--bogus"}, {"-z"}, {"--verbose=1"}, {"-vz"}}) { bool threw = false; try { parse(spec, bad); } catch (const std::runtime_error&) { threw = true; } assert(threw); }          // ④ 오류
    assert(toInt("123", 0, 1000) == 123 && toInt("-5", -10, 10) == -5); for (const char* bad : {"", "12x", "99999999999999999999", "abc", "1.5"}) { bool threw = false; try { toInt(bad, LONG_MIN, LONG_MAX); } catch (const std::runtime_error&) { threw = true; } assert(threw); } { bool threw = false; try { toInt("11", 0, 10); } catch (const std::runtime_error&) { threw = true; } assert(threw); }
    { Parsed a = parse(spec, {"--name", "one", "--name=two", "-nthree"}); assert(a.values["name"] == "three"); }      // 마지막 값
    std::cout << "CommandLineArgument: argc=" << argc << " program=" << argv[0] << "; 5000 generated argument lists (long/short/combined/attached values, --, positionals, tricky values) were parsed back to exactly the chosen options, and error cases were rejected" << std::endl;
    return 0;
}
// Time Complexity: O(인자 수)
// Space Complexity: O(인자 수)
```
# Part 3. 스택 메모리
## PushFrame()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

// 함수 호출 한 번이 스택에 "프레임" 을 쌓는 과정(호출 규약 요약): 인자 -> 복귀 주소 -> 이전 프레임 포인터(BP) -> 지역 변수.
// 스택은 높은 주소에서 낮은 주소로 자란다 (x86).  시뮬레이션: 8바이트 단위 메모리 위에서 SP 를 내리며 프레임을 만든다
// 호출: 호출자가 인자를 오른쪽부터 push → call 이 복귀 주소 push → 피호출자가 BP 를 push 하고 BP ← SP, SP ← SP − 지역 칸 수.   반환: SP ← BP, BP 복원, 복귀 주소 pop, 인자 pop.
// 프레임 포인터 사슬(저장된 BP 들)을 따라가면 호출 스택 전체(복귀 주소들)를 복원할 수 있다 — 디버거의 backtrace 가 하는 일
// 검증: ① 손으로 짠 프레임 배치  ② 무작위 호출/반환 20 000 번(깊이 ≤ 60, 인자 0~4 개, 지역 0~6 칸, 모든 칸에 고유한 값을 써 둠)을 오라클(프레임 벡터)과 대조: 매번 backtrace 가 호출 스택과 같고, 반환 값(복귀 주소)이 맞고,
//        *모든* 프레임의 인자·지역 변수가 다른 호출에 의해 훼손되지 않으며, 프레임 크기의 합 = 스택 사용량(닫힌 식), bp − sp = 맨 위 프레임의 지역 칸 수
//        ③ 균일한 프레임(인자 2, 지역 3 → 7 칸)에서 256 칸 스택은 정확히 36 번째 호출까지 되고 37 번째에서 스택 오버플로  ④ 프레임 k 까지 한꺼번에 풀어(longjmp 처럼) 나머지 프레임의 값이 그대로
struct Machine {
    std::vector<uint64_t> mem; size_t sp, bp; const size_t base;           // 인덱스 = 주소 (낮은 주소 = 작은 인덱스), base = 스택의 맨 위
    explicit Machine(size_t words) : mem(words, 0), sp(words), bp(words), base(words) {}
    void push(uint64_t v) { if (sp == 0) throw std::overflow_error("stack overflow"); mem[--sp] = v; }
    void pushFrame(uint64_t returnAddr, size_t localWords) {
        push(returnAddr);                                              // call 명령이 복귀 주소를 쌓는다
        push(bp); bp = sp;                                             // 이전 BP 저장, 새 BP = 현재 SP
        if (sp < localWords) throw std::overflow_error("stack overflow");
        sp -= localWords;                                              // 지역 변수 공간 확보
    }
    void call(const std::vector<uint64_t>& args, uint64_t returnAddr, size_t localWords) { for (size_t i = args.size(); i-- > 0;) push(args[i]); pushFrame(returnAddr, localWords); }
    uint64_t ret(size_t argc) { sp = bp; bp = mem[sp++]; uint64_t r = mem[sp++]; sp += argc; return r; }      // SP ← BP; BP 복원; 복귀 주소 pop; 인자 pop
    uint64_t& arg(size_t i) { return mem[bp + 2 + i]; }
    uint64_t& local(size_t j) { return mem[bp - 1 - j]; }
    std::vector<uint64_t> backtrace() const { std::vector<uint64_t> r; for (size_t b = bp; b != base; b = mem[b]) r.push_back(mem[b + 1]); return r; }       // 가장 안쪽 호출부터 복귀 주소
};
struct Frame { uint64_t ret; std::vector<uint64_t> args, locals; };

int main() {
    Machine m(64);
    size_t top = m.sp;
    m.push(11); m.push(22);                                            // 인자 두 개 (오른쪽부터)
    size_t argTop = m.sp;
    m.pushFrame(0xDEADBEEF, 3);
    assert(m.sp < argTop && m.sp < top);                              // 스택 포인터는 내려갔다 (스택은 아래로 성장)
    assert(m.mem[m.bp + 1] == 0xDEADBEEF);                            // BP 바로 위에 복귀 주소
    assert(m.mem[m.bp] == 64);                                        // BP 위치에 이전 BP (첫 프레임이라 맨 위)
    assert(m.mem[m.bp + 2] == 22 && m.mem[m.bp + 3] == 11);           // 그 위에 인자
    assert(m.bp - m.sp == 3);                                         // 지역 변수 3칸
    assert((m.backtrace() == std::vector<uint64_t>{0xDEADBEEF}));
    // ② 무작위 호출/반환
    std::mt19937 rng(123); Machine mc(4096); std::vector<Frame> frames; long calls = 0, rets = 0; size_t maxDepth = 0; uint64_t stamp = 1;
    auto verify = [&]() {
        std::vector<uint64_t> want; for (size_t i = frames.size(); i-- > 0;) want.push_back(frames[i].ret);
        assert(mc.backtrace() == want);                                                               // 프레임 포인터 사슬 = 호출 스택
        size_t used = 0; size_t b = mc.bp, sp = mc.sp;
        for (size_t i = frames.size(); i-- > 0;) {                                                     // 위에서부터 (가장 안쪽 프레임부터) 모든 프레임의 내용 확인
            const Frame& f = frames[i]; used += f.args.size() + 2 + f.locals.size();
            for (size_t k = 0; k < f.args.size(); k++) assert(mc.mem[b + 2 + k] == f.args[k]);
            for (size_t k = 0; k < f.locals.size(); k++) assert(mc.mem[b - 1 - k] == f.locals[k]);
            if (i == frames.size() - 1) assert(b - sp == f.locals.size());                             // bp − sp = 맨 위 프레임의 지역 칸 수
            b = mc.mem[b];
        }
        assert(used == mc.base - mc.sp);                                                               // 프레임 크기의 합 = 스택 사용량
    };
    for (int step = 0; step < 20000; ++step) {
        bool doCall = frames.empty() || (frames.size() < 60 && rng() % 100 < 52);
        if (doCall) {
            Frame f; f.ret = 0x1000 + (uint64_t)(rng() % 0xFFFF); size_t argc = rng() % 5, locals = rng() % 7;
            for (size_t i = 0; i < argc; i++) f.args.push_back(stamp++); mc.call(f.args, f.ret, locals);
            for (size_t j = 0; j < locals; j++) { f.locals.push_back(stamp++); mc.local(j) = f.locals.back(); }
            for (size_t i = 0; i < argc; i++) assert(mc.arg(i) == f.args[i]);
            frames.push_back(f); ++calls; maxDepth = std::max(maxDepth, frames.size());
        } else {
            for (size_t j = 0; j < frames.back().locals.size(); j++) { frames.back().locals[j] = stamp++; mc.local(j) = frames.back().locals[j]; }              // 반환 직전에 지역 변수를 고쳐 쓴다
            uint64_t r = mc.ret(frames.back().args.size()); assert(r == frames.back().ret); frames.pop_back(); ++rets;
        }
        if (step % 7 == 0 || frames.size() < 3) verify();
    }
    verify(); assert(calls > 5000 && rets > 4000 && maxDepth >= 30);
    // ④ 프레임 k 까지 한꺼번에 풀기 (longjmp 처럼 저장해 둔 BP 를 따라 올라간다)
    {   while (frames.size() < 25) { Frame f; f.ret = 0x2000 + frames.size(); f.args = {stamp++, stamp++}; mc.call(f.args, f.ret, 2); f.locals = {stamp++, stamp++}; mc.local(0) = f.locals[0]; mc.local(1) = f.locals[1]; frames.push_back(f); }
        size_t k = 10; while (frames.size() > k) { mc.ret(frames.back().args.size()); frames.pop_back(); } verify(); assert(mc.backtrace().size() == k); }
    // ③ 오버플로
    {   Machine small(256); int depth = 0; bool overflow = false;
        try { for (;; ++depth) small.call({1, 2}, 0xAA, 3); } catch (const std::overflow_error&) { overflow = true; }
        assert(overflow && depth == 36 && 36 * 7 <= 256 && 37 * 7 > 256); }
    std::cout << "PushFrame: SP moved down by " << top - m.sp << " words; " << calls << " random calls and " << rets << " returns kept every frame intact and every backtrace exact (max depth " << maxDepth << ")" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(프레임 크기)
```
## PopFrame()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

// 프레임 제거(함수 반환): SP 를 BP 로 올려 지역 변수를 버리고(leave), 이전 BP 를 복원하고, 복귀 주소로 점프한다(ret).
//  지역 변수가 "사라지는" 것은 SP 만 올리면 되기 때문이며 값 자체는 메모리에 남아 있다 (그래서 반환된 지역 변수의 주소는 위험하다).  프레임 배치(높은 주소 → 낮은 주소): [복귀 주소][저장된 BP][지역 변수 …]  ← BP 는 저장된 BP 를 가리킨다.
//  ① 무작위 호출·반환 20 만 번을 모형(프레임 구조체의 벡터)과 대조: 반환 때 복귀 주소가 호출의 역순으로 나오고, BP·SP 가 호출 직전 값으로 정확히 복원되며, 바깥 프레임의 지역 변수는 안쪽 호출이 끝난 뒤에도 그대로
//  ② BP 사슬 걷기: 현재 BP 에서 시작해 "저장된 BP" 를 따라가면 호출 스택의 깊이와 복귀 주소 목록(백트레이스)이 모형과 같다  ③ 반환 뒤에도 지역 변수의 옛 값이 메모리에 남아 있다가 *다음 호출이 덮어쓴다* (댕글링 위험의 실체)
//  ④ 스택 바닥을 넘는 pop 과 가득 찬 push 는 예외(언더플로·오버플로).  ⑤ 깊이 10 만 호출도 정확히 되감긴다.
struct Machine {
    std::vector<uint64_t> mem; size_t sp, bp;
    explicit Machine(size_t words) : mem(words, 0), sp(words), bp(words) {}
    void push(uint64_t v) { if (sp == 0) throw std::overflow_error("stack overflow"); mem[--sp] = v; }
    uint64_t pop() { if (sp >= mem.size()) throw std::underflow_error("stack underflow"); return mem[sp++]; }
    void pushFrame(uint64_t ret, size_t locals) { push(ret); push(bp); bp = sp; if (locals > sp) throw std::overflow_error("stack overflow"); sp -= locals; }          // call + prologue
    uint64_t popFrame() { sp = bp; bp = pop(); return pop(); }                                                      // leave (SP ← BP, BP ← 저장된 BP), ret (복귀 주소)
    uint64_t& local(size_t i) { return mem[bp - 1 - i]; }                                                            // i 번째 지역 변수 (BP 아래)
    std::vector<uint64_t> backtrace() const { std::vector<uint64_t> r; for (size_t b = bp; b < mem.size(); b = mem[b]) { r.push_back(mem[b + 1]); if (mem[b] <= b) break; } return r; }   // BP 사슬을 따라 복귀 주소를 모은다
};
struct Model { uint64_t ret; size_t savedBp, savedSp, locals; std::vector<uint64_t> values; };

int main() {
    { Machine m(64); m.pushFrame(0x1111, 2); m.local(0) = 777; size_t outerBp = m.bp; m.pushFrame(0x2222, 4); assert(m.popFrame() == 0x2222 && m.bp == outerBp && m.local(0) == 777); assert(m.popFrame() == 0x1111 && m.sp == 64 && m.bp == 64); }
    std::mt19937_64 rng(1007); Machine m(4096); std::vector<Model> model; long calls = 0;
    for (int step = 0; step < 200000; ++step) {
        bool doCall = model.empty() || (rng() % 100 < 52 && model.size() < 200);
        if (doCall) { size_t locals = rng() % 6; Model f; f.ret = 0x400000 + rng() % 0x1000; f.savedBp = m.bp; f.savedSp = m.sp; f.locals = locals;
            m.pushFrame(f.ret, locals); for (size_t i = 0; i < locals; ++i) { uint64_t v = rng(); m.local(i) = v; f.values.push_back(v); } model.push_back(f); ++calls; }
        else { Model f = model.back(); model.pop_back(); uint64_t ret = m.popFrame(); assert(ret == f.ret && m.bp == f.savedBp && m.sp == f.savedSp);                         // ① 복귀 주소·BP·SP 복원
            for (size_t i = 0; i < f.locals; ++i) assert(m.mem[f.savedSp - 3 - i] == f.values[i]);                                                                                    // ③ 지역 변수 값은 메모리에 아직 있다
            if (!model.empty()) { const Model& caller = model.back(); for (size_t i = 0; i < caller.locals; ++i) assert(m.local(i) == caller.values[i]); } }                       // 바깥 프레임은 그대로
        if (step % 211 == 0) { std::vector<uint64_t> bt = m.backtrace(); assert(bt.size() == model.size()); for (size_t i = 0; i < bt.size(); ++i) assert(bt[i] == model[model.size() - 1 - i].ret); } }              // ② 백트레이스
    while (!model.empty()) { Model f = model.back(); model.pop_back(); assert(m.popFrame() == f.ret); } assert(m.sp == m.mem.size() && m.bp == m.mem.size());
    {   Machine d(8); d.pushFrame(1, 2); d.local(0) = 0xDEAD; d.popFrame(); assert(d.mem[8 - 3] == 0xDEAD); d.pushFrame(2, 2); d.local(0) = 0xBEEF; assert(d.mem[8 - 3] == 0xBEEF); d.popFrame(); }            // ③ 옛 값이 남아 있다가 다음 호출이 덮어쓴다
    {   Machine tiny(6); bool over = false, under = false; try { tiny.pushFrame(1, 3); tiny.pushFrame(2, 3); } catch (const std::overflow_error&) { over = true; } assert(over);                             // ④
        Machine empty(4); try { empty.popFrame(); } catch (const std::underflow_error&) { under = true; } assert(under); }
    {   Machine deep(1000000); for (int i = 0; i < 100000; ++i) deep.pushFrame((uint64_t)i, 3); for (int i = 99999; i >= 0; --i) assert(deep.popFrame() == (uint64_t)i); assert(deep.sp == deep.mem.size()); }    // ⑤ 깊이 10 만
    std::cout << "PopFrame: " << calls << " random calls and returns matched a frame-model (return addresses in LIFO order, BP/SP restored, outer locals untouched, BP-chain backtraces equal), dead locals stayed in memory until the next call overwrote them, and a 10^5-deep call chain unwound exactly" << std::endl;
    return 0;
}
// Time Complexity: push/pop O(1), 백트레이스 O(깊이)
// Space Complexity: O(스택 크기)
```
## CallFunction()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>

// audit: differential (호출 수·최대 깊이·결과를 반복문 오라클과 닫힌 식 2·fib(n+1)−1 로 대조)
// 호출 과정을 명시적인 스택 기계로 흉내 낸다 — 아주 작은 가상 기계(VM)를 만들어 재귀 함수를 *기계어 수준*으로 실행한다.  호출(CALL)은 "인수를 push → 복귀 주소와 BP 를 push → BP 를 새 프레임에 맞춤 → 점프", 반환(RET)은 "결과를 꺼내 두고 SP ← BP, 저장된 BP·복귀 주소를 복원, 인수를 pop, 결과를 push".
//  재귀 factorial 과 fibonacci 를 손으로 어셈블해 돌린다.  ① fact(0..20), fib(0..25) 의 결과가 반복문 오라클과 같다  ② 호출 횟수: fib(n) 의 CALL 수 = 2·fib(n+1) − 1 (재귀 트리의 노드 수), fact(n) 은 n 번(n ≥ 1)  ③ 최대 스택 깊이(프레임 수) = 재귀 깊이: fact(n) → n, fib(n) → max(n, 1)
//  ④ 깊이 10 만의 fact 도 가상 스택(힙)이라 오버플로 없이 되고(정수는 mod 2^64), 스택 한도를 낮추면 *정확히 한도 깊이에서* 오버플로 예외  ⑤ 프레임 한 개의 크기는 일정(인수 1 + 복귀 주소 + 저장된 BP + 곱셈을 기다리며 쌓아 둔 피연산자 n 하나 = 4 칸)이라 최대 스택 사용량 = 정확히 4 · 깊이 + 1.
enum Op { PUSHI, LOADARG, ADD, SUB, MUL, LT, JZ, CALL, RET, HALT };
struct Ins { Op op; int64_t a = 0; };
struct VM {
    std::vector<Ins> code; std::vector<int64_t> stack; size_t limit; size_t bp = 0; long callCount = 0; size_t maxFrames = 0, frames = 0, maxWords = 0;
    explicit VM(std::vector<Ins> c, size_t stackLimit = 1u << 26) : code(std::move(c)), limit(stackLimit) {}
    void push(int64_t v) { if (stack.size() >= limit) throw std::overflow_error("stack overflow"); stack.push_back(v); maxWords = std::max(maxWords, stack.size()); }
    int64_t pop() { int64_t v = stack.back(); stack.pop_back(); return v; }
    int64_t run(int64_t arg) {                                                                                     // main: push 인수; CALL 0; HALT
        push(arg); size_t pc = 0; int64_t retPc = (int64_t)code.size();                                              // 마지막에 HALT 로 돌아오도록 가짜 복귀 주소
        push(retPc); push((int64_t)bp); bp = stack.size(); ++callCount; ++frames; maxFrames = std::max(maxFrames, frames);                                   // 최초 호출
        for (;;) { const Ins& in = code[pc];
            switch (in.op) {
            case PUSHI: push(in.a); ++pc; break;
            case LOADARG: push(stack[bp - 3]); ++pc; break;                                                          // 인수는 [인수][복귀 주소][저장된 BP] 의 가장 위 (BP − 3)
            case ADD: { int64_t b = pop(), a = pop(); push((int64_t)((uint64_t)a + (uint64_t)b)); ++pc; break; }
            case SUB: { int64_t b = pop(), a = pop(); push((int64_t)((uint64_t)a - (uint64_t)b)); ++pc; break; }
            case MUL: { int64_t b = pop(), a = pop(); push((int64_t)((uint64_t)a * (uint64_t)b)); ++pc; break; }
            case LT: { int64_t b = pop(), a = pop(); push(a < b); ++pc; break; }
            case JZ: { int64_t c = pop(); pc = c == 0 ? (size_t)in.a : pc + 1; break; }
            case CALL: { int64_t savedPc = (int64_t)pc + 1; push(savedPc); push((int64_t)bp); bp = stack.size(); ++callCount; ++frames; maxFrames = std::max(maxFrames, frames); pc = (size_t)in.a; break; }
            case RET: { int64_t result = pop(); stack.resize(bp); bp = (size_t)pop(); int64_t ret = pop(); pop(); push(result); --frames; if (ret == retPc) return pop(); pc = (size_t)ret; break; }          // SP ← BP, BP·복귀 주소 복원, 인수 pop, 결과 push
            case HALT: return pop(); } } }
};
std::vector<Ins> factProgram() { return {{LOADARG}, {PUSHI, 2}, {LT}, {JZ, 6}, {PUSHI, 1}, {RET}, {LOADARG}, {LOADARG}, {PUSHI, 1}, {SUB}, {CALL, 0}, {MUL}, {RET}}; }          // n < 2 ? 1 : n · fact(n − 1)
std::vector<Ins> fibProgram() { return {{LOADARG}, {PUSHI, 2}, {LT}, {JZ, 6}, {LOADARG}, {RET}, {LOADARG}, {PUSHI, 1}, {SUB}, {CALL, 0}, {LOADARG}, {PUSHI, 2}, {SUB}, {CALL, 0}, {ADD}, {RET}}; }      // n < 2 ? n : fib(n−1) + fib(n−2)
uint64_t factIter(int n) { uint64_t r = 1; for (int i = 2; i <= n; ++i) r *= (uint64_t)i; return r; }
uint64_t fibIter(int n) { uint64_t a = 0, b = 1; for (int i = 0; i < n; ++i) { uint64_t t = a + b; a = b; b = t; } return a; }

int main() {
    for (int n = 0; n <= 20; ++n) { VM vm(factProgram()); int64_t r = vm.run(n); assert((uint64_t)r == factIter(n) && vm.callCount == std::max(n, 1) && vm.maxFrames == (size_t)std::max(n, 1) && vm.stack.empty() && vm.frames == 0); }          // ① ② ③ fact
    assert(factIter(20) == 2432902008176640000ULL);
    for (int n = 0; n <= 25; ++n) { VM vm(fibProgram()); int64_t r = vm.run(n); assert((uint64_t)r == fibIter(n) && vm.callCount == (long)(2 * fibIter(n + 1) - 1) && vm.maxFrames == (size_t)std::max(n, 1) && vm.stack.empty()); }                      // fib
    {   VM deep(factProgram()); int64_t r = deep.run(100000); assert((uint64_t)r == factIter(100000) && deep.maxFrames == 100000 && deep.maxWords == 4 * 100000 + 1);                                         // ④ ⑤ 깊이 10 만
        for (size_t lim : {30, 300, 3000}) { VM small(factProgram(), lim); bool overflow = false; try { small.run(100000); } catch (const std::overflow_error&) { overflow = true; } assert(overflow && small.maxFrames <= lim / 4 + 1 && small.maxFrames + 1 >= lim / 4); }                // 한도 깊이에서 오버플로
        VM fits(factProgram(), 4 * 100 + 8); assert((uint64_t)fits.run(100) == factIter(100)); }
    std::cout << "CallFunction: the hand-assembled stack VM computed fact(0..20) and fib(0..25) exactly like loops, made 2*fib(n+1)-1 calls for fib(n), peaked at recursion-depth frames of 4 stack words each, ran fact(100000) 100000 frames deep, and overflowed exactly at the configured stack limit" << std::endl;
    return 0;
}
// Time Complexity: 호출 하나당 상수 개의 명령, 전체는 호출 트리의 크기
// Space Complexity: 4 · 재귀 깊이 칸
```
## ReturnFunction()
### 대표코드
```cpp
#include <cassert>
#include <iostream>
#include <string>
#include <utility>

#pragma GCC diagnostic ignored "-Wpessimizing-move"      // makeMoveReturn 이 일부러 보이는 역효과이므로 컴파일러 경고를 끈다
// 반환 방식: 작은 값은 레지스터(rax)로, 큰 구조체는 호출자가 마련한 공간의 주소를 숨은 인자(sret)로 넘겨 거기에 직접 만든다.  C++17 부터 순수 우측값(prvalue) 반환은 복사·이동이 아예 일어나지 않는다 (보장된 복사 생략).
//  이름 있는 지역 변수 반환은 NRVO(허용, 보장은 아님) — 허용되지 않으면 이동으로 폴백한다.  `return std::move(local)` 은 NRVO 를 막는 *역효과*다.
//  각 반환 방식에서 복사·이동 횟수를 센다.  규칙에서 *보장되는* 값만 정확히 단언하고(보장 생략 0/0, std::move 반환 이동 1, 두 이름 있는 후보 중 하나를 고르는 반환은 이동 ≤ 1, 멤버 반환은 복사 1, 정적 객체 반환은 복사 1, 매개변수 반환은 이동 1), NRVO 는 "복사 0, 이동 ≤ 1" 로 허용 범위를 확인한다.
//  또한 생성자 안에서 `this` 를 기록해, prvalue 가 *호출자의 변수 자리에서 직접 만들어졌는지*(주소 동일) 확인하고, 큰 구조체(4 KB)·작은 구조체(두 레지스터 크기)의 반환 값이 정확한지 본다.
struct Tracked {
    static int copies, moves; static const void* lastCtor;
    int v = 0;
    explicit Tracked(int x) : v(x) { lastCtor = this; }
    Tracked(const Tracked& o) : v(o.v) { ++copies; lastCtor = this; }
    Tracked(Tracked&& o) noexcept : v(o.v) { ++moves; lastCtor = this; }
    Tracked& operator=(const Tracked&) = default;
    static void reset() { copies = moves = 0; }
};
int Tracked::copies = 0, Tracked::moves = 0; const void* Tracked::lastCtor = nullptr;
struct Holder { Tracked t{4}; };
Tracked makePrvalue() { return Tracked(7); }                              // 보장된 생략
Tracked makeNamed() { Tracked t(8); return t; }                           // NRVO
Tracked makeMoveReturn() { Tracked t(9); return std::move(t); }           // 역효과: NRVO 불가 → 이동 1
Tracked makeEither(bool c) { Tracked a(1), b(2); if (c) return a; return b; }      // 서로 다른 이름 있는 후보 둘: NRVO 불가 → 이동
Tracked makeFromParam(Tracked p) { return p; }                            // 매개변수 반환: 복사 생략 불가 → 이동
Tracked makeFromMember() { Holder h; return h.t; }                        // 멤버 반환: 복사
Tracked makeStatic() { static Tracked s(5); return s; }                   // 정적 객체 반환: 복사
Tracked chain3() { return makePrvalue(); }                                // prvalue 를 그대로 돌려줘도 생략이 이어진다
struct Big { char data[4096]; int tag; };
Big makeBig(int tag) { Big b; for (int i = 0; i < 4096; ++i) b.data[i] = (char)(i * 31 + tag); b.tag = tag; return b; }
struct Small { long a, b; };
Small makeSmall(long x) { return {x, x * 2}; }

int main() {
    Tracked::reset(); { Tracked a = makePrvalue(); assert(a.v == 7 && Tracked::copies == 0 && Tracked::moves == 0 && Tracked::lastCtor == &a); }                                     // 보장된 생략 + 호출자 변수 자리에 직접 생성
    Tracked::reset(); { Tracked a = chain3(); assert(a.v == 7 && Tracked::copies == 0 && Tracked::moves == 0 && Tracked::lastCtor == &a); }                                         // 여러 단계도 생략
    Tracked::reset(); { Tracked b = makeNamed(); assert(b.v == 8 && Tracked::copies == 0 && Tracked::moves <= 1); }                                                                   // NRVO 허용 범위
    Tracked::reset(); { Tracked c = makeMoveReturn(); assert(c.v == 9 && Tracked::copies == 0 && Tracked::moves == 1); }                                                              // std::move 반환은 이동 1
    Tracked::reset(); { Tracked d = makeEither(true); Tracked e = makeEither(false); assert(d.v == 1 && e.v == 2 && Tracked::copies == 0 && Tracked::moves == 2); }                 // 두 후보 중 선택: 호출마다 이동 1
    Tracked::reset(); { Tracked f = makeFromParam(Tracked(6)); assert(f.v == 6 && Tracked::copies == 0 && Tracked::moves == 1); }                                                    // 인수는 생략(prvalue → 매개변수), 반환에서 이동 1
    Tracked::reset(); { Tracked g = makeFromMember(); assert(g.v == 4 && Tracked::copies == 1 && Tracked::moves == 0); }
    Tracked::reset(); { Tracked h = makeStatic(); Tracked i = makeStatic(); assert(h.v == 5 && i.v == 5 && Tracked::copies == 2 && Tracked::moves == 0); }
    {   Big b = makeBig(3); for (int i = 0; i < 4096; ++i) assert(b.data[i] == (char)(i * 31 + 3)); assert(b.tag == 3 && sizeof(Big) > 16 /* sret */); Small s = makeSmall(21); assert(s.a == 21 && s.b == 42 && sizeof(Small) == 16); }              // 큰 값과 작은 값 모두 정확
    {   const Tracked& r = makePrvalue(); assert(r.v == 7);  /* const& 에 묶인 임시 객체는 참조의 수명 동안 산다 */ }
    {   std::string s = std::string("tmp") + "val"; assert(s == "tmpval"); }
    std::cout << "ReturnFunction: prvalue returns made 0 copies and 0 moves and were constructed in the caller's own variable (same address), std::move returns cost 1 move, two-candidate returns cost 1 move per call, member and static returns cost 1 copy, and 4 KB and 16-byte results came back intact" << std::endl;
    return 0;
}
// Time Complexity: O(1) (큰 구조체는 O(크기))
// Space Complexity: O(1)
```
## LocalVariable()
### 대표코드
```cpp
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 지역 변수(자동 저장 기간): 선언 시점에 만들어지고 블록을 벗어날 때 "생성의 역순" 으로 소멸한다 → RAII 의 토대.  스택에 있으므로 할당·해제가 SP 이동뿐이라 빠르지만, 블록이 끝나면 그 주소는 더 이상 유효하지 않다.
//  이 규칙은 정상 종료뿐 아니라 *조기 반환과 예외로 인한 되감기(stack unwinding)* 에서도 같다 — 던져진 지점까지 만들어진 지역 객체만, 역순으로, 정확히 한 번씩 소멸한다.
//  ① 생성 기반 검증: 무작위 중첩 블록 프로그램(선언 / 안쪽 블록 / 특정 선언에서 throw) 5000 개를 *실제 C++ 범위로* 실행해 얻은 생성·소멸 추적이, 명시적 스택으로 푼 독립 오라클의 추적과 같고 모든 객체가 정확히 한 번 소멸
//  ② 고정 사례: 임시 객체는 완전 표현식 끝에서 역순 소멸, 배열 원소는 역순, 멤버는 선언 순서로 생성·역순으로 소멸하고 기반 클래스는 먼저 생성·나중에 소멸, 반복문은 반복마다 생성·소멸, 조기 return 도 역순  ③ 블록이 끝나면 포인터는 댕글링(읽지 않고 주소만 보관).
std::vector<std::string> trace;
struct Guard { std::string n; explicit Guard(std::string s) : n(std::move(s)) { trace.push_back("+" + n); } ~Guard() { trace.push_back("-" + n); } };
struct Boom {};
struct Item { bool isBlock = false; bool throwHere = false; std::string name; std::vector<Item> inner; };
void runBlock(const std::vector<Item>& items, size_t i) {                                                       // 선언은 재귀로 "범위 안에 계속 살아 있게" 한다
    if (i == items.size()) return; const Item& it = items[i];
    if (it.isBlock) { runBlock(it.inner, 0); runBlock(items, i + 1); return; }                                // 안쪽 블록이 끝난 뒤 같은 범위에서 계속
    Guard g(it.name); if (it.throwHere) throw Boom(); runBlock(items, i + 1); }
void oracle(const std::vector<Item>& items, std::vector<std::string>& out, std::vector<std::vector<std::string>>& live, bool& thrown) {   // 명시적 스택 모형
    live.emplace_back();
    for (const Item& it : items) { if (thrown) break;
        if (it.isBlock) { oracle(it.inner, out, live, thrown); continue; }
        out.push_back("+" + it.name); live.back().push_back(it.name); if (it.throwHere) { thrown = true; break; } }
    std::vector<std::string>& mine = live.back(); for (size_t k = mine.size(); k-- > 0;) out.push_back("-" + mine[k]); live.pop_back(); }          // 블록을 떠날 때 (또는 되감기 중) 자기 범위의 객체를 역순으로
int counter = 0;
std::vector<Item> randomBlock(std::mt19937& rng, int depth, bool allowThrow) { std::vector<Item> v; int n = (int)(rng() % 6); for (int i = 0; i < n; ++i) { Item it; if (depth < 4 && rng() % 4 == 0) { it.isBlock = true; it.inner = randomBlock(rng, depth + 1, allowThrow); } else { it.name = "v" + std::to_string(counter++); it.throwHere = allowThrow && rng() % 40 == 0; } v.push_back(it); } return v; }
struct Base { Guard b{"base"}; }; struct Derived : Base { Guard m1{"m1"}; Guard m2{"m2"}; Derived() : Base() { trace.push_back("body"); } };
struct Counted { static int idx; Guard g; Counted() : g("e" + std::to_string(idx++)) {} }; int Counted::idx = 0;
std::string firstOrEarly(bool early) { Guard a("a"); if (early) return "early"; Guard b("b"); return "late"; }

int main() {
    std::mt19937 rng(1011); long programs = 0, throws = 0;
    for (int it = 0; it < 5000; ++it) { counter = 0; std::vector<Item> prog = randomBlock(rng, 0, true); trace.clear(); bool thrownReal = false;
        try { runBlock(prog, 0); } catch (const Boom&) { thrownReal = true; }
        std::vector<std::string> want; std::vector<std::vector<std::string>> live; bool thrown = false; oracle(prog, want, live, thrown); assert(trace == want && thrownReal == thrown);                           // ①
        std::vector<int> balance(counter + 1, 0); for (const std::string& e : trace) balance[std::stoi(e.substr(2))] += e[0] == '+' ? 1 : -1; for (int b : balance) assert(b == 0);                         // 정확히 한 번씩 소멸
        ++programs; throws += thrownReal; }
    assert(throws > 100 && throws < programs);
    trace.clear(); { (Guard("t1"), Guard("t2"), 0); trace.push_back("after"); } assert((trace == std::vector<std::string>{"+t1", "+t2", "-t2", "-t1", "after"}));                                   // 임시 객체: 완전 표현식 끝에서 역순
    trace.clear(); { Counted::idx = 0; Counted arr[3]; trace.push_back("body"); } assert((trace == std::vector<std::string>{"+e0", "+e1", "+e2", "body", "-e2", "-e1", "-e0"}));                         // 배열: 역순
    trace.clear(); { Derived d; } assert((trace == std::vector<std::string>{"+base", "+m1", "+m2", "body", "-m2", "-m1", "-base"}));                                                              // 기반 → 멤버 순 생성, 정확히 역순 소멸
    trace.clear(); for (int i = 0; i < 2; ++i) { Guard loop("L" + std::to_string(i)); } assert((trace == std::vector<std::string>{"+L0", "-L0", "+L1", "-L1"}));
    trace.clear(); assert(firstOrEarly(true) == "early"); assert((trace == std::vector<std::string>{"+a", "-a"})); trace.clear(); assert(firstOrEarly(false) == "late"); assert((trace == std::vector<std::string>{"+a", "+b", "-b", "-a"}));          // 조기 return
    int* p = nullptr; uintptr_t addr = 0; { int inner = 2; p = &inner; addr = (uintptr_t)p; assert(*p == 2); } assert(addr != 0); /* 여기서 *p 는 정의되지 않은 동작(댕글링) */
    std::cout << "LocalVariable: " << programs << " random nested-scope programs (" << throws << " of them unwinding through a throw) produced exactly the destruction trace of an explicit-stack oracle, with every object destroyed exactly once; temporaries, arrays, bases/members, loops and early returns followed the reverse-of-construction rule" << std::endl;
    return 0;
}
// Time Complexity: O(1) 할당/해제
// Space Complexity: O(스코프 깊이)
```
## StackFrame()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

// audit: closed-form (재귀 프레임 간격이 일정하고 지역 배열 크기 차이와 일치)
// 스택 프레임(요약, 정본은 Stack.md Part 8): 함수 호출마다 프레임이 하나씩 쌓이고, 호출된 함수의 프레임은 더 낮은 주소에 놓인다.  `__builtin_frame_address(0)` 으로 현재 프레임의 주소를 얻어 확인할 수 있다 (GCC/Clang).
//  같은 함수를 재귀로 부르면 프레임 크기가 같으므로 *깊이가 한 칸 깊어질 때마다 주소가 정확히 같은 간격(stride)으로 줄어든다*.  간격은 지역 변수가 커지면 그만큼 커진다.
//  ① 깊이 60 재귀의 프레임 주소가 엄격히 감소하고 간격이 *모두 같다* (16 바이트 정렬)  ② 지역 배열 64 / 256 / 1024 바이트 함수의 간격 차이가 배열 크기 차이와 ±64 바이트 안에서 일치  ③ 호출된 함수의 `__builtin_frame_address(1)` (= 호출자의 프레임 주소)이 바로 위 깊이의 프레임 주소와 같다
//  ④ 서로 다른 함수 두 개가 번갈아 호출해도(상호 재귀) 프레임 주소가 계속 감소한다.  꼬리 호출 제거를 막으려고 호출 뒤에 컴파일러 장벽을 둔다.
#pragma GCC diagnostic ignored "-Wframe-address"          // __builtin_frame_address(1) 은 호출자 프레임을 보려는 일부러의 사용
template <int N> __attribute__((noinline)) uintptr_t dive(int d, std::vector<uintptr_t>& addrs, std::vector<uintptr_t>& callerAddrs) {
    volatile char buf[N]; asm volatile("" : : "r"(buf) : "memory"); /* 주소를 내보내 컴파일러가 배열을 줄이지 못하게 한다 */ buf[0] = (char)d; addrs.push_back((uintptr_t)__builtin_frame_address(0)); if (d < 59) callerAddrs.push_back((uintptr_t)__builtin_frame_address(1));
    uintptr_t r = d == 0 ? 0 : dive<N>(d - 1, addrs, callerAddrs); asm volatile("" ::: "memory"); buf[N - 1] = (char)r; return r + buf[0]; }
__attribute__((noinline)) uintptr_t pingpong(int d, std::vector<uintptr_t>& addrs);
__attribute__((noinline)) uintptr_t pong(int d, std::vector<uintptr_t>& addrs) { volatile char pad[48]; asm volatile("" : : "r"(pad) : "memory"); pad[0] = 1; addrs.push_back((uintptr_t)__builtin_frame_address(0)); uintptr_t r = d == 0 ? 0 : pingpong(d - 1, addrs); asm volatile("" ::: "memory"); return r + pad[0]; }
__attribute__((noinline)) uintptr_t pingpong(int d, std::vector<uintptr_t>& addrs) { volatile char pad[16]; asm volatile("" : : "r"(pad) : "memory"); pad[0] = 1; addrs.push_back((uintptr_t)__builtin_frame_address(0)); uintptr_t r = d == 0 ? 0 : pong(d - 1, addrs); asm volatile("" ::: "memory"); return r + pad[0]; }
template <int N> long strideOf() { std::vector<uintptr_t> addrs, callers; dive<N>(59, addrs, callers); assert(addrs.size() == 60); long stride = (long)(addrs[0] - addrs[1]);
    for (size_t i = 1; i < addrs.size(); ++i) { assert(addrs[i] < addrs[i - 1] && (long)(addrs[i - 1] - addrs[i]) == stride && addrs[i] % 16 == 0); }                       // ① 엄격히 감소 + 같은 간격 + 16 바이트 정렬
    for (size_t i = 1; i < addrs.size(); ++i) assert(callers[i - 1] == addrs[i - 1]);                                                                                         // ③ 호출자의 프레임 주소 = 바로 위 프레임
    return stride; }

int main() {
    uintptr_t outer = (uintptr_t)__builtin_frame_address(0); std::vector<uintptr_t> a; pingpong(40, a); assert(a.size() == 41 && a[0] < outer); for (size_t i = 1; i < a.size(); ++i) assert(a[i] < a[i - 1]);                  // ④ 번갈아 호출해도 감소
    long s64 = strideOf<64>(), s256 = strideOf<256>(), s1024 = strideOf<1024>();
    assert(s64 >= 64 && s256 >= 256 && s1024 >= 1024 && s64 < s256 && s256 < s1024);
    assert(std::labs((s256 - s64) - (256 - 64)) <= 64 && std::labs((s1024 - s256) - (1024 - 256)) <= 64);                                                                      // ② 간격 차이 = 배열 크기 차이
    std::cout << "StackFrame: recursion frames moved down by a constant stride of " << s64 << " / " << s256 << " / " << s1024 << " bytes for 64 / 256 / 1024-byte locals (differences " << s256 - s64 << " and " << s1024 - s256 << "), and __builtin_frame_address(1) matched the caller's frame" << std::endl;
    return 0;
}
// Time Complexity: O(깊이)
// Space Complexity: O(깊이) 스택
```
## StackOverflow()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
#if defined(__linux__)
#include <csignal>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// audit: closed-form (한도 ÷ 프레임 크기로 예측한 깊이를 자식 프로세스의 실제 도달 깊이와 대조)
// 스택 오버플로(요약, 정본은 Stack.md Part 10): 스택은 크기가 정해져 있다(보통 8MB).  재귀가 너무 깊거나 지역 배열이 너무 크면 한계를 넘어 세그멘테이션 오류.
//  안전하게 보는 법 둘: (1) 한도(getrlimit)와 프레임 한 개의 크기를 재서 "최대 재귀 깊이" 를 예측하고 그 일부만 실제로 재귀해 본다  (2) *자식 프로세스*를 fork 해 스택 한도를 1 MB 로 낮춘 뒤 무한 재귀시키고, 부모가 SIGSEGV 로 죽었음을 확인하고 죽기 전 도달한 깊이를 공유 메모리에서 읽어 예측과 비교한다.
//  ① 프레임 크기 측정(주소 간격)  ② 예측 깊이의 1/4 만큼 재귀한 합이 정확  ③ 자식이 SIGSEGV 로 종료했고(`WIFSIGNALED`), 도달 깊이가 예측(한도 ÷ 프레임 크기)의 85%~102% — 스택 맨 위에 환경 변수·인자가 이미 차지한 몇 KB 때문에 약간 못 미친다
//  ④ 한도를 두 배로 하면 도달 깊이도 거의 두 배.  Linux 가 아니면 ①② 만 한다.
// audit: no-sanitize (새니타이저가 프레임 크기를 바꿔 측정값이 달라진다)
static volatile long* progress = nullptr; static uintptr_t lastAddr = 0;
__attribute__((noinline)) long dive(long d, long stop) {
    volatile char pad[256]; asm volatile("" : : "r"(pad) : "memory"); pad[0] = (char)d; if (progress) *progress = d; if (d == stop) { lastAddr = (uintptr_t)__builtin_frame_address(0); return d; }
    long r = dive(d + 1, stop); asm volatile("" ::: "memory"); return r + pad[0] - pad[0]; }
__attribute__((noinline)) long depthSum(long d) { volatile char pad[64]; asm volatile("" : : "r"(pad) : "memory"); pad[0] = 1; long r = d == 0 ? 0 : d + depthSum(d - 1); asm volatile("" ::: "memory"); return r + pad[0] - 1; }

int main() {
    dive(0, 0); uintptr_t a = lastAddr; dive(0, 200); uintptr_t b = lastAddr; size_t perFrame = (a - b) / 200; assert(perFrame >= 256 && perFrame < 1024 && (a - b) % 200 == 0);                    // ① 프레임 하나가 차지하는 바이트
#if defined(__linux__)
    struct rlimit rl; getrlimit(RLIMIT_STACK, &rl); size_t limit = rl.rlim_cur == RLIM_INFINITY ? (8u << 20) : (size_t)rl.rlim_cur; size_t maxDepth = limit / perFrame; assert(maxDepth > 1000);
    long safe = (long)std::min<size_t>(maxDepth / 4, 20000); assert(depthSum(safe) == safe * (safe + 1) / 2);                                                                              // ② 한도의 일부만 쓰면 안전
    long reached[2] = {0, 0};
    for (int k = 0; k < 2; ++k) { size_t childLimit = (size_t)(1u << 20) << k;                                                                                                              // 1 MB, 2 MB
        void* mem = mmap(nullptr, 4096, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0); assert(mem != MAP_FAILED); progress = (volatile long*)mem; *progress = -1;
        pid_t pid = fork(); assert(pid >= 0);
        if (pid == 0) { struct rlimit lim; lim.rlim_cur = childLimit; lim.rlim_max = rl.rlim_max; setrlimit(RLIMIT_STACK, &lim); dive(0, -1); _exit(0); }                                      // 자식: 한도를 낮추고 끝없이 재귀
        int status = 0; waitpid(pid, &status, 0); assert(WIFSIGNALED(status) && WTERMSIG(status) == SIGSEGV);                                                                               // ③ 세그멘테이션 오류로 죽었다
        reached[k] = *progress; double predicted = (double)childLimit / (double)perFrame; assert((double)reached[k] >= 0.85 * predicted && (double)reached[k] <= 1.02 * predicted); munmap(mem, 4096); progress = nullptr; }
    assert((double)reached[1] > 1.8 * (double)reached[0] && (double)reached[1] < 2.2 * (double)reached[0]);                                                                              // ④
    std::cout << "StackOverflow: " << perFrame << " bytes per frame; a child with a 1 MB stack limit died of SIGSEGV after " << reached[0] << " frames (predicted " << (size_t)(1u << 20) / perFrame << "), and with 2 MB after " << reached[1] << "; this process's own limit " << limit / 1024 << " KB allows ~" << maxDepth << " frames" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(깊이)
// Space Complexity: O(깊이) 스택
```
## TailCallOptimization()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <variant>

// audit: differential (꼬리 재귀·일반 재귀·반복문·트램펄린의 값을 서로 대조하고 스택 주소 범위를 측정)
// 꼬리 호출 최적화(TCO): 함수의 마지막 동작이 다른 (또는 자기 자신의) 호출이면 현재 프레임이 더 이상 필요 없으므로 새 프레임 없이 "점프" 로 바꿀 수 있다 → 재귀가 반복문과 같은 공간 O(1).
//  C++ 표준은 TCO 를 보장하지 않는다 (-O2 에서는 대개 적용되지만 디버그 빌드에서는 안 된다) — 그래서 *적용 여부에 의존하는 코드는 이식성이 없다*.  보장이 필요하면 트램펄린(trampoline)으로 직접 구현한다.
//  트램펄린: 재귀 호출 대신 "다음에 할 일" 을 반환하고, 반복문이 그것을 이어서 실행한다 → 스택이 쌓이지 않는다.  상호 재귀(isEven ↔ isOdd)처럼 컴파일러가 제거하기 힘든 경우에도 된다.
//  ① 꼬리 재귀 / 일반 재귀 / 반복문 / 트램펄린이 같은 값(n ≤ 10^4)  ② 트램펄린은 n = 10^6 단계에서도 *스택 프레임 주소 범위가 상수*다 (단계가 모두 반복문의 같은 깊이에서 실행되므로 범위 ≤ 1 KB)  ③ 컴파일러가 제거할 수 없게 장벽을 둔 일반 재귀는 깊이에 비례해 스택 주소가 내려간다 (n = 1000 에서 ≥ 16 · n 바이트)
//  ④ 상호 재귀 isEven(10^6) / isOdd(10^6+1) 가 트램펄린으로 정확  ⑤ 트램펄린 위에서 누적 인수(accumulator) 변환: 일반 재귀 n + f(n−1) → 꼬리 형태 f(n, acc) 로 바꾸면 같은 값을 O(1) 스택으로.
long long sumTail(long long n, long long acc) { return n == 0 ? acc : sumTail(n - 1, acc + n); }                                    // 꼬리 재귀 (마지막이 자기 호출)
uintptr_t deepest = ~(uintptr_t)0, shallowest = 0;
__attribute__((noinline)) long long sumNonTail(long long n) { uintptr_t here = (uintptr_t)__builtin_frame_address(0); deepest = std::min(deepest, here); shallowest = std::max(shallowest, here);
    if (n == 0) return 0; long long r = n + sumNonTail(n - 1); asm volatile("" ::: "memory"); return r; }                               // 호출 뒤에 덧셈이 남아 꼬리 호출이 아니다 (장벽으로 변환도 막는다)
struct Step; typedef std::function<Step()> Thunk;
struct Step { bool done; long long value; Thunk next; };
uintptr_t tMin = ~(uintptr_t)0, tMax = 0;
Step sumStep(long long n, long long acc) { uintptr_t here = (uintptr_t)__builtin_frame_address(0); tMin = std::min(tMin, here); tMax = std::max(tMax, here); if (n == 0) return {true, acc, nullptr}; return {false, 0, [=] { return sumStep(n - 1, acc + n); }}; }
long long run(Step s) { while (!s.done) s = s.next(); return s.value; }
Step isEvenStep(long long n, bool wantEven);
Step isOddStep(long long n, bool wantEven) { if (n == 0) return {true, wantEven ? 0 : 1, nullptr}; return {false, 0, [=] { return isEvenStep(n - 1, wantEven); }}; }          // isOdd(n) = isEven(n−1)
Step isEvenStep(long long n, bool wantEven) { if (n == 0) return {true, wantEven ? 1 : 0, nullptr}; return {false, 0, [=] { return isOddStep(n - 1, wantEven); }}; }          // isEven(n) = isOdd(n−1)

int main() {
    for (long long n : {0LL, 1LL, 2LL, 10LL, 1000LL, 10000LL}) { long long loop = 0; for (long long i = 1; i <= n; ++i) loop += i; assert(sumTail(n, 0) == loop && sumNonTail(n) == loop && run(sumStep(n, 0)) == loop && loop == n * (n + 1) / 2); }                          // ①
    tMin = ~(uintptr_t)0; tMax = 0; assert(run(sumStep(1000000, 0)) == 500000500000LL); assert(tMax - tMin <= 1024);                                                  // ② 10^6 단계 내내 프레임 주소 범위가 상수(첫 호출만 main 에서 불러 조금 다르다)
    deepest = ~(uintptr_t)0; shallowest = 0; sumNonTail(1000); assert(shallowest - deepest >= 16 * 1000);                                                              // ③ 일반 재귀는 깊이에 비례해 내려간다
    for (long long n : {0LL, 1LL, 2LL, 3LL, 999999LL, 1000000LL, 1000001LL}) { bool even = n % 2 == 0; assert(run(isEvenStep(n, true)) == (even ? 1 : 0)); assert(run(isOddStep(n, true)) == (even ? 0 : 1)); }                          // ④ 상호 재귀
    long long loop = 0; for (long long i = 1; i <= 1000000; ++i) loop += i; assert(loop == 500000500000LL && sumTail(1000, 0) == 500500);
    std::cout << "TailCallOptimization: the trampoline ran 10^6 steps at one constant stack depth (frame address range " << tMax - tMin << " bytes), mutual recursion isEven/isOdd worked at n=10^6, while ordinary recursion of depth 1000 descended " << shallowest - deepest << " bytes" << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: 트램펄린 O(1), 일반 재귀 O(n)
```
# Part 4. 힙 메모리
## malloc()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// malloc 의 핵심 동작을 작은 힙 위에서 단계별로 본다 (분할, 병합, 탐색 정책).
//   1) 할당 가능한 블록 탐색  2) 필요한 만큼 분할  3) 헤더(크기·사용 여부) 기록  4) 사용자 포인터 = 헤더 바로 뒤
//   free: 사용 표시를 지우고 이웃한 빈 블록과 병합해 단편화를 줄인다.  탐색 정책: 처음 맞는 곳(first-fit) / 가장 꼭 맞는 곳(best-fit) / 가장 큰 곳(worst-fit) / 마지막 할당 지점부터(next-fit)
// 검증: ① 손으로 짠 시나리오(분할·구멍 재사용·병합)와 외부 단편화의 닫힌 식  ② 네 정책 모두에서 무작위 할당/해제 20 000 번(크기 1~200): 블록이 힙을 빈틈없이 덮고, 빈 블록끼리 이웃하지 않고(완전 병합), 사용 중 블록의 내용이 보존되고 겹치지 않으며,
//        사용자 포인터가 8 바이트 정렬이고, 회계(사용자 영역 + 헤더 + 빈 영역 = 전체)가 맞는다  ③ 정책 오라클: 할당 직전 블록 목록으로 각 정책이 *어느 블록을 골라야 하는지* 따로 계산해 실제 반환 주소와 대조하고, 실패는 "맞는 빈 블록이 정말 없을 때만"
//        ④ 같은 부하에서 정책별 단편화·실패 횟수를 비교
struct Header { size_t size; size_t used; };                            // 사용자 영역 크기, 사용 중 여부 (16 바이트)
enum Policy { FIRST, BEST, WORST, NEXT };
class Heap {
    std::vector<uint8_t> mem; Policy policy; size_t lastOff = 0;
    Header hdr(size_t off) const { Header h; std::memcpy(&h, &mem[off], sizeof h); return h; }
    void setHdr(size_t off, Header h) { std::memcpy(&mem[off], &h, sizeof h); }
    static size_t round8(size_t n) { return (n + 7) & ~size_t(7); }
    size_t next(size_t off) const { return off + sizeof(Header) + hdr(off).size; }
public:
    explicit Heap(size_t bytes, Policy p = FIRST) : mem(bytes), policy(p) { setHdr(0, Header{bytes - sizeof(Header), 0}); }
    void* alloc(size_t n) {
        n = round8(n); if (n == 0) n = 8; size_t pick = SIZE_MAX;
        if (policy == NEXT) {                                                                  // 마지막 할당 지점부터 한 바퀴
            size_t start = lastOff; for (int pass = 0; pass < 2 && pick == SIZE_MAX; pass++) for (size_t off = pass == 0 ? start : 0; off < (pass == 0 ? mem.size() : start); off = next(off)) { Header h = hdr(off); if (!h.used && h.size >= n) { pick = off; break; } }
        } else for (size_t off = 0; off < mem.size(); off = next(off)) {
            Header h = hdr(off); if (h.used || h.size < n) continue;
            if (pick == SIZE_MAX) { pick = off; if (policy == FIRST) break; continue; }
            Header best = hdr(pick); if ((policy == BEST && h.size < best.size) || (policy == WORST && h.size > best.size)) pick = off;
        }
        if (pick == SIZE_MAX) return nullptr;
        Header h = hdr(pick);
        if (h.size >= n + sizeof(Header) + 8) { setHdr(pick + sizeof(Header) + n, Header{h.size - n - sizeof(Header), 0}); h.size = n; }       // 2) 남는 부분을 새 빈 블록으로 분할
        h.used = 1; setHdr(pick, h); lastOff = pick;                                           // 3) 사용 중으로 표시
        return &mem[pick + sizeof(Header)];                                                   // 4) 사용자 포인터
    }
    void release(void* p) {
        size_t off = (size_t)((uint8_t*)p - &mem[0]) - sizeof(Header); Header h = hdr(off); h.used = 0; setHdr(off, h);
        for (size_t o = 0; o < mem.size();) {                                                   // 인접한 빈 블록 병합
            Header a = hdr(o); size_t nx = next(o);
            if (!a.used && nx < mem.size() && !hdr(nx).used) { a.size += sizeof(Header) + hdr(nx).size; setHdr(o, a); if (lastOff == nx) lastOff = o; } else o = nx;
        }
    }
    size_t blocks() const { size_t c = 0; for (size_t o = 0; o < mem.size(); o = next(o)) c++; return c; }
    size_t largestFree() const { size_t m = 0; for (size_t o = 0; o < mem.size(); o = next(o)) if (!hdr(o).used) m = std::max(m, hdr(o).size); return m; }
    size_t totalFree() const { size_t m = 0; for (size_t o = 0; o < mem.size(); o = next(o)) if (!hdr(o).used) m += hdr(o).size; return m; }
    size_t offsetOf(void* p) const { return (size_t)((uint8_t*)p - &mem[0]) - sizeof(Header); }
    std::vector<std::pair<size_t, Header>> layout() const { std::vector<std::pair<size_t, Header>> v; for (size_t o = 0; o < mem.size(); o = next(o)) v.push_back({o, hdr(o)}); return v; }
    bool validate() const {                                                                    // 불변식: 힙을 빈틈없이 덮고, 빈 블록이 이웃하지 않으며, 회계가 맞는다
        size_t covered = 0, payload = 0, headers = 0, freeBytes = 0; bool prevFree = false;
        for (size_t o = 0; o < mem.size();) { Header h = hdr(o); if (h.size % 8 != 0 || o + sizeof(Header) + h.size > mem.size()) return false; if (!h.used && prevFree) return false; prevFree = !h.used;
            covered += sizeof(Header) + h.size; headers += sizeof(Header); (h.used ? payload : freeBytes) += h.size; o += sizeof(Header) + h.size; }
        return covered == mem.size() && payload + freeBytes + headers == mem.size();
    }
    void* base() { return &mem[0]; }
};

int main() {
    Heap h(1024);
    size_t total = h.largestFree();
    void *a = h.alloc(100), *b = h.alloc(200), *c = h.alloc(50);
    assert(a && b && c && a < b && b < c);                             // 주소가 순서대로 배치
    assert(h.blocks() == 4);                                           // a, b, c, 나머지 빈 블록
    h.release(b);                                                       // 가운데 해제 -> 구멍
    void* d = h.alloc(150);
    assert(d == b);                                                    // 구멍을 재사용 (b 의 자리)
    h.release(a); h.release(d); h.release(c);                          // 전부 해제하면 인접 블록이 병합되어
    assert(h.blocks() == 1 && h.largestFree() == total);               // 처음의 하나짜리 큰 블록으로 돌아온다
    assert(h.alloc(5000) == nullptr && h.validate());                  // 너무 큰 요청은 실패
    // ① 외부 단편화: 32 바이트 블록 20 개(블록당 48 바이트) -> 하나 건너 해제하면 빈 영역은 충분한데 64 바이트가 안 들어간다
    {   Heap f(1024); std::vector<void*> v; for (int i = 0; i < 20; i++) v.push_back(f.alloc(32)); assert(f.blocks() == 21 && f.totalFree() == 1024 - 20 * 48 - 16);
        for (int i = 0; i < 20; i += 2) f.release(v[i]); size_t freeBytes = f.totalFree();                   // 구멍 10 개(각 32) + 꼬리
        assert(freeBytes == 10 * 32 + (1024 - 20 * 48 - 16) && f.largestFree() < 64 && freeBytes >= 64 && f.alloc(64) == nullptr);            // 총량은 충분해도 연속 64 가 없다
        f.release(v[1]); assert(f.largestFree() == 32 + 16 + 32 + 16 + 32 && f.alloc(64) != nullptr && f.validate()); }                           // 이웃 하나를 더 풀면 세 블록이 병합되어 성공
    // ②③ 정책별 무작위 부하
    std::mt19937 rng(77); long placed[4] = {0, 0, 0, 0}, failed[4] = {0, 0, 0, 0}; double fragSum[4] = {0, 0, 0, 0}; long fragSamples[4] = {0, 0, 0, 0};
    for (int pol = 0; pol < 4; pol++) {
        Heap heap(4096, (Policy)pol); struct Live { uint8_t* p; size_t n; uint8_t tag; }; std::vector<Live> live; int tagCounter = 1;
        for (int step = 0; step < 20000; ++step) {
            bool doAlloc = live.empty() || rng() % 100 < 52;
            if (doAlloc) {
                size_t n = 1 + rng() % 200, r = std::max<size_t>(8, (n + 7) & ~size_t(7)); auto before = heap.layout();
                size_t expect = SIZE_MAX;                                                                          // 오라클: 정책이 골라야 할 블록의 오프셋
                if (pol == NEXT) { /* 마지막 할당 지점은 힙 내부 상태라 first-fit 오라클로는 못 구한다: 실패 여부만 대조 */ }
                else for (auto& e : before) { if (e.second.used || e.second.size < r) continue; if (expect == SIZE_MAX) { expect = e.first; continue; }
                    size_t cur = 0; for (auto& q : before) if (q.first == expect) cur = q.second.size;
                    if ((pol == BEST && e.second.size < cur) || (pol == WORST && e.second.size > cur)) expect = e.first; }
                bool anyFits = false; for (auto& e : before) anyFits |= !e.second.used && e.second.size >= r;
                void* p = heap.alloc(n);
                if (!p) { assert(!anyFits); ++failed[pol]; continue; }                                             // 실패는 맞는 블록이 정말 없을 때만
                assert(anyFits && (size_t)((uint8_t*)p - (uint8_t*)heap.base()) % 8 == 0 && (pol == NEXT || heap.offsetOf(p) == expect));
                uint8_t tag = (uint8_t)(tagCounter++); std::memset(p, tag, n); live.push_back({(uint8_t*)p, n, tag}); ++placed[pol];
            } else {
                size_t i = rng() % live.size(); for (size_t k = 0; k < live[i].n; k++) assert(live[i].p[k] == live[i].tag);          // 해제 전에 내용 확인
                heap.release(live[i].p); live.erase(live.begin() + (long)i);
            }
            assert(heap.validate());
            if (step % 50 == 0 && heap.totalFree() > 0) { fragSum[pol] += 1.0 - (double)heap.largestFree() / (double)heap.totalFree(); ++fragSamples[pol]; }
        }
        for (auto& l : live) for (size_t k = 0; k < l.n; k++) assert(l.p[k] == l.tag);                               // 끝날 때 살아 있는 블록 전부 내용 보존
        for (auto& l : live) heap.release(l.p); assert(heap.blocks() == 1 && heap.validate());
    }
    for (int pol = 0; pol < 4; pol++) assert(placed[pol] > 5000);
    double frag[4]; for (int pol = 0; pol < 4; pol++) frag[pol] = fragSum[pol] / (double)fragSamples[pol];
    std::cout << "malloc simulation: split, reuse and coalesce verified; mean external fragmentation first/best/worst/next = " << frag[0] << " / " << frag[1] << " / " << frag[2] << " / " << frag[3] << ", failures " << failed[0] << "/" << failed[1] << "/" << failed[2] << "/" << failed[3] << std::endl;
    return 0;
}
// Time Complexity: 할당 O(블록 수) (first-fit), 해제 O(블록 수) (병합 포함)
// Space Complexity: 블록당 헤더 16B
```
## new()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <new>
#include <stdexcept>
#include <vector>

// new 연산자 = (1) operator new 로 메모리 확보 + (2) 생성자 호출.   delete = (1) 소멸자 호출 + (2) operator delete 로 반환.
// new[] 는 소멸자를 원소마다 불러야 하므로 개수를 메모리 앞쪽에 따로 기록한다(cookie).  할당 실패 시 new 는 (new_handler 를 거듭 부른 뒤) bad_alloc 을 던지고 nothrow new 는 nullptr 를 돌려준다
// 생성자가 예외를 던지면 이미 만든 원소는 거꾸로 소멸되고 메모리는 *대응하는* operator delete 로 반환된다 — placement new 는 대응하는 placement delete 가 불린다
// 전역 operator new/delete 를 교체해(예산·호출 기록) 이런 규칙들을 직접 관찰한다.  교체한 할당기는 크기를 앞 16 바이트에 적어 두어 delete 가 예산을 정확히 돌려받는다
// 검증: ① 원래 확인(호출 수·생성/소멸 수·실패 시 예외/nullptr)  ② 쿠키: 소멸자가 사소한 타입은 쿠키 없음, 아니면 원소 수를 담는 8 바이트(정렬 16 타입은 16 바이트) — Itanium ABI
//        ③ 배열 원소 3 번째 생성자가 예외 → 앞의 2 개가 소멸되고 메모리가 반환됨, 단일 new 의 생성자 예외도 누수 없음  ④ placement new + 대응 placement delete (생성자 예외 시 호출됨), 명시적 소멸자 호출
//        ⑤ 클래스별 operator new/delete 와 가상 소멸자(파생 클래스 크기가 sized delete 로 전달됨)  ⑥ new_handler: 예산을 푸는 핸들러는 한 번 불린 뒤 재시도로 성공하고, 계속 실패하면 핸들러가 던질 때까지 반복  ⑦ 정렬 요구가 큰 타입은 정렬된 operator new
static int allocs = 0, frees = 0, handlerCalls = 0; static size_t budget = (size_t)-1, lastSingle = 0, lastArray = 0, lastAlign = 0, lastFreedSize = 0;
void* rawAlloc(size_t n) {
    for (;;) {                                                      // 표준이 정한 루프: 실패하면 new_handler 를 부르고 다시 시도, 핸들러가 없으면 bad_alloc
        if (n <= budget) { void* raw = std::malloc(n + 16); if (raw) { std::memcpy(raw, &n, sizeof n); budget -= n; ++allocs; return (char*)raw + 16; } }
        std::new_handler h = std::get_new_handler(); if (!h) throw std::bad_alloc(); h();
    }
}
void* operator new(size_t n) { lastSingle = n; return rawAlloc(n); }
void* operator new[](size_t n) { lastArray = n; return rawAlloc(n); }
void rawFree(void* p) noexcept { if (!p) return; char* raw = (char*)p - 16; size_t n; std::memcpy(&n, raw, sizeof n); budget += n; lastFreedSize = n; ++frees; std::free(raw); }
void operator delete(void* p) noexcept { rawFree(p); }
void operator delete(void* p, size_t) noexcept { rawFree(p); }
void operator delete[](void* p) noexcept { rawFree(p); }
void operator delete[](void* p, size_t) noexcept { rawFree(p); }
struct alignas(64) Big { char data[64]; };
void* operator new(size_t n, std::align_val_t al) { lastAlign = (size_t)al; void* p = nullptr; if (posix_memalign(&p, (size_t)al, n) != 0) throw std::bad_alloc(); ++allocs; return p; }
void operator delete(void* p, std::align_val_t) noexcept { ++frees; std::free(p); }
void operator delete(void* p, size_t, std::align_val_t) noexcept { ++frees; std::free(p); }

struct Obj { static int alive; Obj() { alive++; } ~Obj() { alive--; } };
int Obj::alive = 0;
struct Plain { int x; };                                            // 소멸자가 사소하다
struct NonTrivial { int x; ~NonTrivial() {} };                      // 소멸자를 불러야 한다 -> 원소 수를 기억해야 한다
struct alignas(16) Wide { char c; ~Wide() {} };
struct Boom {};                                                     // 메시지 문자열을 할당하는 std::runtime_error 대신, 할당 횟수를 어지럽히지 않는 예외
struct Thrower { static int constructed, destroyed, throwAt; Thrower() { if (constructed == throwAt) throw Boom(); ++constructed; } ~Thrower() { ++destroyed; } };
int Thrower::constructed = 0, Thrower::destroyed = 0, Thrower::throwAt = -1;
struct Arena { alignas(16) char buf[256]; size_t used = 0; };
int placementDeletes = 0;
void* operator new(size_t n, Arena& a) { void* p = a.buf + a.used; a.used += (n + 15) & ~size_t(15); return p; }
void operator delete(void*, Arena&) noexcept { ++placementDeletes; }                       // 생성자가 던질 때만 불리는 대응 delete
struct Fragile { Fragile(bool boom) { if (boom) throw Boom(); } };
struct Pooled { static int newCalls, deleteCalls; static size_t lastDeleteSize; char pad[40];
    static void* operator new(size_t n) { ++newCalls; return ::operator new(n); } static void operator delete(void* p, size_t n) { ++deleteCalls; lastDeleteSize = n; ::operator delete(p); }
    virtual ~Pooled() {} };
struct Derived : Pooled { char more[100]; };
int Pooled::newCalls = 0, Pooled::deleteCalls = 0; size_t Pooled::lastDeleteSize = 0;
std::size_t reserveBytes = 0;
void releaseReserve() { ++handlerCalls; if (reserveBytes) { budget += reserveBytes; reserveBytes = 0; } else throw std::bad_alloc(); }            // 예비 메모리를 풀어 주고, 더 줄 것이 없으면 포기

int main() {
    int baseAllocs = allocs, baseFrees = frees;
    Obj* o = new Obj;                                                  // operator new 1번 + 생성자 1번
    assert(allocs == baseAllocs + 1 && Obj::alive == 1);
    delete o;                                                           // 소멸자 + operator delete
    assert(frees == baseFrees + 1 && Obj::alive == 0);
    Obj* arr = new Obj[5];                                              // operator new[] 1번, 생성자 5번
    assert(Obj::alive == 5);
    delete[] arr;                                                       // 소멸자 5번
    assert(Obj::alive == 0 && allocs == frees);
    bool threw = false; budget = 1 << 20;                              // 예산 1 MB
    try { char* volatile sink = new char[2 << 20]; (void)sink; } catch (const std::bad_alloc&) { threw = true; }       // 실제로 큰 메모리를 요구하지 않고도 실패를 만든다
    assert(threw);                                                      // 실패 -> 예외
    char* volatile probe = new (std::nothrow) char[2 << 20]; assert(probe == nullptr);                  // 실패 -> nullptr
    budget = (size_t)-1;
    // ② 쿠키 (Itanium ABI: GCC·Clang)
#if defined(__GNUC__) || defined(__clang__)
    { Plain* p = new Plain[5]; assert(lastArray == 5 * sizeof(Plain)); delete[] p;                                 // 쿠키 없음
      NonTrivial* q = new NonTrivial[5]; assert(lastArray == 5 * sizeof(NonTrivial) + sizeof(size_t)); delete[] q;  // 원소 수를 담는 쿠키
      Wide* w = new Wide[3]; assert(sizeof(Wide) == 16 && lastArray == 3 * 16 + 16); delete[] w; }                  // 쿠키 크기 = max(size_t 크기, 정렬)
#endif
    // ③ 생성자 예외
    {   int a0 = allocs, f0 = frees; Thrower::constructed = Thrower::destroyed = 0; Thrower::throwAt = 2; bool caught = false;
        try { Thrower* t = new Thrower[5]; (void)t; } catch (const Boom&) { caught = true; }
        assert(caught && Thrower::constructed == 2 && Thrower::destroyed == 2 && allocs - a0 == 1 && frees - f0 == 1);            // 만든 2 개는 소멸, 메모리는 반환
        Thrower::constructed = 0; Thrower::throwAt = 0; caught = false; a0 = allocs; f0 = frees; try { Thrower* t = new Thrower; (void)t; } catch (const Boom&) { caught = true; }
        assert(caught && allocs - a0 == 1 && frees - f0 == 1 && Thrower::destroyed == 2); Thrower::throwAt = -1; }
    // ④ placement new
    {   Arena arena; Obj* p = new (arena) Obj; assert((char*)p == arena.buf && Obj::alive == 1); p->~Obj(); assert(Obj::alive == 0);                // 명시적 소멸자 호출 (메모리는 Arena 가 관리)
        placementDeletes = 0; Fragile* f = new (arena) Fragile(false); assert(placementDeletes == 0 && (char*)f == arena.buf + 16); bool caught = false;
        try { new (arena) Fragile(true); } catch (const Boom&) { caught = true; }
        assert(caught && placementDeletes == 1); }
    // ⑤ 클래스별 operator new/delete
    {   Pooled* p = new Pooled; delete p; assert(Pooled::newCalls == 1 && Pooled::deleteCalls == 1 && Pooled::lastDeleteSize == sizeof(Pooled));
        Pooled* d = new Derived; delete d; assert(Pooled::newCalls == 2 && Pooled::deleteCalls == 2 && Pooled::lastDeleteSize == sizeof(Derived) && sizeof(Derived) > sizeof(Pooled)); }       // 가상 소멸자 → 실제 크기가 전달된다
    // ⑥ new_handler
    {   std::set_new_handler(releaseReserve); budget = 1000; reserveBytes = 5000; handlerCalls = 0;
        char* big = new char[3000]; assert(handlerCalls == 1 && big != nullptr && budget == 1000 + 5000 - 3000); delete[] big;                          // 핸들러가 예산을 풀자 재시도에서 성공
        budget = 100; reserveBytes = 0; handlerCalls = 0; bool caught = false; try { char* x = new char[5000]; (void)x; } catch (const std::bad_alloc&) { caught = true; } assert(caught && handlerCalls == 1);     // 풀어 줄 것이 없으면 핸들러가 던진다
        std::set_new_handler(nullptr); budget = (size_t)-1; }
    // ⑦ 정렬 요구가 큰 타입
    {   int a0 = allocs, f0 = frees; Big* b = new Big; assert(lastAlign == 64 && ((uintptr_t)b % 64) == 0 && allocs == a0 + 1); delete b; assert(frees == f0 + 1);
        Big* arr2 = new Big[3]; assert(((uintptr_t)arr2 % 64) == 0 && ((uintptr_t)&arr2[2] - (uintptr_t)arr2) == 128); delete[] arr2; }
    assert(allocs == frees);
    std::cout << "new/delete: allocs=" << allocs << " frees=" << frees << std::endl;
    return 0;
}
// Time Complexity: 할당기에 따라 다름 (평균 O(1))
// Space Complexity: O(n)
// audit: no-sanitize (전역 operator new/delete 를 교체하고 정렬 할당을 직접 한다)
```
## PlacementNew()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <new>
#include <random>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

// 배치 new: 이미 확보한 메모리 위치에 객체만 생성한다 (new (주소) T(...)).  메모리 풀·아레나·컨테이너(std::vector 의 내부)의 기초.  소멸은 delete 가 아니라 소멸자를 직접 호출해야 하며, 메모리 해제는 별도로 한다.
//  이 원리로 *아레나*(범프 할당기 + 소멸자 목록)와 *고정 크기 풀*(자유 슬롯 목록)을 만든다.  ① 아레나: 무작위 타입(char/short/int/double/long double/alignas(32)/std::string/예외를 던지는 생성자)으로 4000 번 할당해 모든 포인터가 정렬되고 서로 겹치지 않으며 값이 다른 할당에 덮이지 않음
//  ② 소멸자는 reset() 때 *생성의 역순* 으로 정확히 한 번씩 호출(전역 카운터로 확인)되고 reset 뒤 첫 할당은 같은 주소  ③ 용량 초과는 std::bad_alloc 이고 상태가 변하지 않음, 생성자가 던지면 소멸자 등록 없이 할당이 되돌려짐
//  ④ 풀: 무작위 할당/해제 20 만 번을 오라클(슬롯 사용 표시)과 대조, 살아 있는 객체 수 = 생성자 − 소멸자 호출 수  ⑤ 같은 버퍼를 다른 타입으로 재사용할 때 std::launder 로 접근.
int liveObjects = 0, ctorCalls = 0, dtorCalls = 0; std::vector<int> dtorOrder;
struct Widget { int id; explicit Widget(int i) : id(i) { ++liveObjects; ++ctorCalls; } ~Widget() { --liveObjects; ++dtorCalls; dtorOrder.push_back(id); } };
struct Thrower { int id; explicit Thrower(int i, bool boom) : id(i) { if (boom) throw std::runtime_error("ctor failed"); ++liveObjects; ++ctorCalls; } ~Thrower() { --liveObjects; ++dtorCalls; dtorOrder.push_back(id); } };
struct alignas(32) Wide { char c; };
struct Dtor { void* p; void (*fn)(void*); };
struct Big512 { char c[512]; };
class Arena {
    unsigned char* base; size_t cap, used = 0; std::vector<Dtor> dtors;
public:
    explicit Arena(size_t c) : base(static_cast<unsigned char*>(::operator new(c, std::align_val_t(64)))), cap(c) {}
    ~Arena() { reset(); ::operator delete(base, std::align_val_t(64)); }
    Arena(const Arena&) = delete; Arena& operator=(const Arena&) = delete;
    void* allocate(size_t size, size_t align) { size_t off = (used + align - 1) & ~(align - 1); if (off + size > cap) throw std::bad_alloc(); used = off + size; return base + off; }
    template <class T, class... A> T* make(A&&... a) { size_t saved = used; void* p = allocate(sizeof(T), alignof(T)); T* t; try { t = new (p) T(std::forward<A>(a)...); } catch (...) { used = saved; throw; }           // 생성자가 던지면 할당을 되돌린다
        if (!std::is_trivially_destructible<T>::value) dtors.push_back({t, [](void* q) { static_cast<T*>(q)->~T(); }}); return t; }
    void reset() { for (size_t i = dtors.size(); i-- > 0;) dtors[i].fn(dtors[i].p); dtors.clear(); used = 0; }                                                                          // 역순 소멸
    size_t usedBytes() const { return used; } const unsigned char* start() const { return base; }
};
template <class T> class Pool {
    alignas(T) unsigned char storage[64 * sizeof(T)]; std::vector<int> freeSlots; std::vector<char> inUse;
public:
    Pool() : inUse(64, 0) { for (int i = 63; i >= 0; --i) freeSlots.push_back(i); }
    ~Pool() { for (int i = 0; i < 64; ++i) if (inUse[i]) slot(i)->~T(); }
    T* slot(int i) { return std::launder(reinterpret_cast<T*>(storage + (size_t)i * sizeof(T))); }
    template <class... A> int alloc(A&&... a) { if (freeSlots.empty()) return -1; int i = freeSlots.back(); freeSlots.pop_back(); new (storage + (size_t)i * sizeof(T)) T(std::forward<A>(a)...); inUse[i] = 1; return i; }
    bool release(int i) { if (i < 0 || i >= 64 || !inUse[i]) return false; slot(i)->~T(); inUse[i] = 0; freeSlots.push_back(i); return true; }
};

int main() {
    std::mt19937 rng(1013); Arena arena(1 << 20); struct Rec { uintptr_t lo, hi; unsigned char fill; }; std::vector<Rec> recs; long strings = 0;
    for (int i = 0; i < 4000; ++i) { int kind = (int)(rng() % 7); void* p = nullptr; size_t sz = 0, al = 1;
        switch (kind) { case 0: p = arena.make<char>('x'); sz = 1; al = 1; break; case 1: p = arena.make<short>((short)5); sz = 2; al = 2; break; case 2: p = arena.make<int>(7); sz = 4; al = 4; break; case 3: p = arena.make<double>(1.5); sz = 8; al = 8; break;
            case 4: p = arena.make<long double>(2.5L); sz = sizeof(long double); al = alignof(long double); break; case 5: p = arena.make<Wide>(); sz = sizeof(Wide); al = 32; break;
            case 6: p = arena.make<std::string>(std::string(40 + rng() % 100, 'q')); sz = sizeof(std::string); al = alignof(std::string); ++strings; break; }
        assert((uintptr_t)p % al == 0); Rec r{(uintptr_t)p, (uintptr_t)p + sz, (unsigned char)(0x30 + i % 64)}; if (kind != 6) std::fill((unsigned char*)p, (unsigned char*)p + sz, r.fill); recs.push_back(r); }              // ① 정렬
    std::sort(recs.begin(), recs.end(), [](const Rec& a, const Rec& b) { return a.lo < b.lo; }); for (size_t i = 1; i < recs.size(); ++i) assert(recs[i - 1].hi <= recs[i].lo);                                               // 겹치지 않는다
    arena.reset();
    {   Arena a2(4096); const unsigned char* first = nullptr; for (int round = 0; round < 3; ++round) { dtorOrder.clear(); liveObjects = 0; int n = 10 + round; std::vector<Widget*> w; for (int i = 0; i < n; ++i) w.push_back(a2.make<Widget>(i)); if (round == 0) first = (const unsigned char*)w[0]; else assert((const unsigned char*)w[0] == first);          // ② reset 뒤 첫 할당은 같은 주소
            assert(liveObjects == n); a2.reset(); assert(liveObjects == 0 && (int)dtorOrder.size() == n); for (int i = 0; i < n; ++i) assert(dtorOrder[i] == n - 1 - i); } }                                                      // 역순으로 정확히 한 번씩
    {   Arena a3(256); size_t before = a3.usedBytes(); bool threw = false; try { for (int i = 0; i < 100; ++i) a3.make<Widget>(i); } catch (const std::bad_alloc&) { threw = true; } assert(threw);                                             // ③ 용량 초과
        size_t full = a3.usedBytes(); try { a3.make<Big512>(); } catch (const std::bad_alloc&) {} assert(a3.usedBytes() == full && before == 0);
        a3.reset(); dtorOrder.clear(); liveObjects = 0; ctorCalls = dtorCalls = 0; bool boomed = false; Arena a4(1024); a4.make<Thrower>(1, false); size_t u = a4.usedBytes(); try { a4.make<Thrower>(2, true); } catch (const std::runtime_error&) { boomed = true; } assert(boomed && a4.usedBytes() == u);
        a4.make<Thrower>(3, false); a4.reset(); assert(liveObjects == 0 && ctorCalls == 2 && dtorCalls == 2 && dtorOrder == (std::vector<int>{3, 1})); }                                                                               // 던진 객체는 소멸자도 호출되지 않는다
    {   Pool<Widget> pool; std::vector<int> live; std::vector<char> oracle(64, 0); liveObjects = 0; ctorCalls = dtorCalls = 0;
        for (int step = 0; step < 200000; ++step) { if (live.empty() || (rng() % 100 < 50 && live.size() < 64)) { int s = pool.alloc(step); assert(s >= 0 && !oracle[s]); oracle[s] = 1; live.push_back(s); assert(pool.slot(s)->id == step); }
            else { size_t k = rng() % live.size(); int s = live[k]; assert(pool.release(s) && oracle[s]); oracle[s] = 0; live[k] = live.back(); live.pop_back(); assert(!pool.release(s)); }
            assert(liveObjects == (int)live.size() && ctorCalls - dtorCalls == liveObjects); }
        assert(pool.alloc(1) >= 0 || live.size() == 64); }                                                                                                                                                             // ④ 풀
    {   alignas(std::string) unsigned char buffer[sizeof(std::string) + 16]; std::string* s = new (buffer) std::string("reused buffer with a long enough content to need the heap"); assert(*s == "reused buffer with a long enough content to need the heap"); s->~basic_string();                // ⑤ 같은 버퍼를 다른 타입으로
        Widget* w = new (buffer) Widget(99); assert(std::launder(reinterpret_cast<Widget*>(buffer))->id == 99); w->~Widget(); }
    std::cout << "PlacementNew: " << recs.size() << " arena allocations of 7 types (" << strings << " heap-owning strings) were aligned and disjoint, destructors ran once in reverse order, a throwing constructor rolled its allocation back, and a 64-slot pool survived 2*10^5 random operations against an oracle" << std::endl;
    return 0;
}
// Time Complexity: 아레나 할당 O(1), 생성자 비용 별도
// Space Complexity: O(1) 추가 할당 없음 (고정 버퍼)
```
# Part 5. 포인터와 참조
## Pointer()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <random>
#include <type_traits>
#include <vector>

// 포인터: 다른 객체의 주소를 값으로 갖는 변수.  p + 1 은 "다음 바이트" 가 아니라 "다음 원소"(sizeof(T) 바이트 뒤).
// 배열 이름은 첫 원소의 포인터로 변환(decay)된다.  포인터의 포인터, const 의 위치, nullptr 이 핵심 어휘
// 검증: ① 손으로 고른 사실(원래 예)  ② 여러 타입(char·short·int·double·24 바이트 구조체·64 바이트 정렬 구조체)의 배열에서 무작위 인덱스 쌍으로 포인터 연산이 *바이트 주소 계산* 과 일치:
//        &a[i] + k == &a[i+k], 뺄셈 = 원소 수, 바이트 차이 = 원소 수 × sizeof, 대소 비교 = 인덱스 대소, 끝 다음 칸(one past the end)은 비교·뺄셈 가능, p[i] == *(p+i) == i[p]
//        ③ 2차원 배열 a[i][j] 의 주소 = base + (i·열 + j)·4, 배열을 가리키는 포인터와 포인터 배열의 차이  ④ const 의 위치를 타입 특성으로 확인하고, 포인터 크기 = 주소 크기, uintptr_t 왕복, 멤버 포인터의 의미
struct Rec24 { int64_t a, b, c; };
struct alignas(64) Line { char b[64]; };
template <class T> void checkArithmetic(std::mt19937& rng) {
    std::vector<T> storage(64); T* a = storage.data(); const int n = 64;
    for (int it = 0; it < 500; ++it) {
        int i = (int)(rng() % n), j = (int)(rng() % n); T* pi = a + i; T* pj = a + j;
        assert(pi == &a[i] && &*pi == &a[i] && (pi + (j - i)) == pj);                                                     // &a[i] + k == &a[i+k]
        assert(pj - pi == (std::ptrdiff_t)(j - i));                                                                        // 뺄셈 = 원소 수
        assert((uintptr_t)pj - (uintptr_t)pi == (uintptr_t)((std::ptrdiff_t)(j - i) * (std::ptrdiff_t)sizeof(T)));      // 바이트 차이 = 원소 수 × sizeof (부호 있는 차이를 모듈러로)
        assert((pi < pj) == (i < j) && (pi == pj) == (i == j) && (pi <= pj) == (i <= j));                                 // 주소 순서 = 인덱스 순서
        assert(reinterpret_cast<char*>(pi) - reinterpret_cast<char*>(a) == (std::ptrdiff_t)(i * sizeof(T)));
    }
    T* end = a + n; assert(end - a == n && end > a + (n - 1) && end == &a[n - 1] + 1);                                   // 끝 다음 칸: 역참조는 안 되지만 비교·뺄셈은 된다
}

int main() {
    int a[5] = {10, 20, 30, 40, 50};
    int* p = a;                                                       // decay: &a[0]
    assert(*p == 10 && *(p + 2) == 30 && p[3] == 40 && 3[p] == 40);   // p[i] == *(p + i) == i[p]
    assert((char*)(p + 1) - (char*)p == sizeof(int));                // +1 은 sizeof(int) 바이트
    assert(&a[4] - &a[1] == 3);                                       // 포인터 뺄셈 = 원소 개수 차이
    int** pp = &p; **pp = 99; assert(a[0] == 99);                     // 포인터의 포인터로 원본을 바꾼다

    int x = 1, y = 2;
    const int* pc = &x;                                               // 가리키는 값이 const: *pc = 3 불가, pc = &y 가능
    int* const cp = &x;                                               // 포인터 자체가 const: *cp = 3 가능, cp = &y 불가
    pc = &y; *cp = 3;
    assert(*pc == 2 && x == 3);

    int* none = nullptr;                                              // 아무것도 가리키지 않음 (역참조는 정의되지 않은 동작)
    assert(none == nullptr && !none);
    assert(sizeof(int*) == sizeof(void*) && sizeof(char*) == sizeof(void*));    // 64비트에서 모두 8바이트
    // ② 타입별 포인터 연산
    std::mt19937 rng(7);
    checkArithmetic<char>(rng); checkArithmetic<short>(rng); checkArithmetic<int>(rng); checkArithmetic<double>(rng); checkArithmetic<Rec24>(rng); checkArithmetic<Line>(rng);
    static_assert(sizeof(Rec24) == 24 && sizeof(Line) == 64, "크기가 포인터 증가폭을 정한다");
    // ③ 2차원 배열
    int m[3][4]; for (int i = 0; i < 3; i++) for (int j = 0; j < 4; j++) m[i][j] = i * 10 + j;
    for (int i = 0; i < 3; i++) for (int j = 0; j < 4; j++) { assert(&m[i][j] == (int*)m + i * 4 + j && *(*(m + i) + j) == m[i][j]); }              // 행 우선 배치
    int (*row)[4] = m; assert((char*)(row + 1) - (char*)row == 4 * sizeof(int) && (*(row + 2))[3] == 23);                              // 배열을 가리키는 포인터는 한 행씩 건너뛴다
    int* rows[3] = {m[0], m[1], m[2]}; assert(sizeof(rows) == 3 * sizeof(int*) && sizeof(m) == 12 * sizeof(int) && rows[1][2] == 12);   // 포인터 배열은 크기가 다른 별개의 구조
    // ④ const 의 위치와 타입 특성, 주소 크기, 멤버 포인터
    static_assert(std::is_same<decltype(pc), const int*>::value && std::is_same<decltype(cp), int* const>::value, "const 가 어디에 붙는지");
    static_assert(std::is_same<std::remove_pointer<const int*>::type, const int>::value && std::is_same<std::remove_const<int* const>::type, int*>::value, "remove_const 는 최상위 const 만");
    static_assert(sizeof(uintptr_t) == sizeof(void*) && std::is_pointer<int*>::value && !std::is_pointer<int>::value && std::is_null_pointer<std::nullptr_t>::value, "주소를 담는 정수");
    assert(reinterpret_cast<int*>(reinterpret_cast<uintptr_t>(p)) == p && p != none);                                                  // 정수로 바꿨다 되돌려도 같은 포인터
    int Rec24::*member = nullptr; assert(!member); member = nullptr; int64_t Rec24::*mb = &Rec24::b; Rec24 r{1, 2, 3}; assert(r.*mb == 2 && (&r)->*mb == 2); Rec24* pr = &r; pr->*mb = 9; assert(r.b == 9);
    assert((char*)&r.b - (char*)&r == (std::ptrdiff_t)offsetof(Rec24, b));
    std::cout << "Pointer: sizeof(pointer) = " << sizeof(void*) << "; pointer arithmetic matched byte arithmetic for 6 element sizes" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Reference()
### 대표코드
```cpp
#include <iostream>
#include <functional>
#include <string>
#include <vector>
#include <cassert>

// 참조: 이미 있는 객체의 "다른 이름(별칭)".  반드시 초기화해야 하고, 다시 다른 객체에 묶을 수 없고, null 이 될 수 없다.
// 컨테이너에 참조를 넣고 싶으면 std::reference_wrapper.  임시 객체에 const 참조를 묶으면 임시의 수명이 연장된다
void addOne(int& v) { v++; }
std::string make() { return "temporary"; }

int main() {
    int a = 1, b = 2;
    int& r = a;
    assert(&r == &a);                                                  // 별칭: 주소가 같다 (새 객체가 아니다)
    r = b;                                                              // 재바인딩이 아니라 a 에 b 의 값을 대입
    assert(a == 2 && &r == &a);
    addOne(a); assert(a == 3);                                         // 함수 인자로 원본 수정

    std::vector<std::reference_wrapper<int>> refs = {std::ref(a), std::ref(b)};
    for (int& x : refs) x *= 10;
    assert(a == 30 && b == 20);

    const std::string& longLived = make();                             // 임시 객체의 수명이 참조의 수명까지 연장된다
    assert(longLived == "temporary");
    int&& rv = 5 + 5; rv++;                                            // 우측값 참조: 임시를 소유처럼 사용
    assert(rv == 11);
    std::cout << "Reference verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SmartPointer()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <functional>
#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

// 스마트 포인터: 소멸자에서 자동으로 해제하는 포인터 (RAII).
//  unique_ptr: 단독 소유, 복사 불가·이동만 가능, 오버헤드 0.   shared_ptr: 참조 횟수로 공동 소유, 마지막 소유자가 해제.
//  weak_ptr: 소유하지 않는 관찰자 (순환 참조를 끊거나 캐시에 쓴다).  사용자 지정 삭제자도 가능
// 표준 라이브러리를 쓰지 않고 세 가지를 직접 만든다: MyUnique(삭제자를 빈 기반 클래스 최적화로 담아 크기가 포인터 하나), MyShared/MyWeak(제어 블록에 강한/약한 참조 수를 원자적으로 두고,
// 강한 수가 0 이 되면 객체를, 약한 수까지 0 이 되면 제어 블록을 해제 — 모든 강한 참조가 약한 참조 하나를 대표한다. lock() 은 강한 수가 0 이 아닐 때만 CAS 로 올린다)
// 검증: ① 손으로 짠 사용법(원래 예)과 크기 = 포인터 하나  ② 같은 연산열을 MyShared/std::shared_ptr 에 동시에 적용하는 차분 시험 30 000 번(생성·복사·이동·reset·swap·weak 대입·lock·삭제자): 매번 모든 핸들의 use_count·expired·소유 객체의 동치 관계가 같고 살아 있는 객체 수가 같으며 끝나면 0
//        ③ 순환 참조는 shared 만으로는 샌다(약한 참조로 끊으면 해제)  ④ 스레드 8 개가 한 객체를 복사·소멸 20 000 번씩 + weak.lock 경합: 객체는 정확히 한 번 소멸하고, lock 이 성공했다면 객체는 살아 있다(use-after-free 없음)  ⑤ unique: 삭제자는 정확히 한 번, release 후에는 호출 안 됨
template <class T> struct DefaultDelete { void operator()(T* p) const { delete p; } };
template <class D, bool Empty = std::is_class<D>::value && std::is_empty<D>::value> struct DelHolder : private D {   // 빈 클래스 삭제자: 기반 클래스로 두어 공간 0
    DelHolder() = default; explicit DelHolder(D d) : D(std::move(d)) {}
    D& deleter() { return *this; }
};
template <class D> struct DelHolder<D, false> {                                                      // 함수 포인터·상태 있는 삭제자: 멤버로 저장
    D d{}; DelHolder() = default; explicit DelHolder(D dd) : d(std::move(dd)) {}
    D& deleter() { return d; }
};
template <class T, class D = DefaultDelete<T>> class MyUnique : private DelHolder<D> {
    T* p = nullptr;
    D& del() { return this->deleter(); }
public:
    MyUnique() = default; explicit MyUnique(T* q) : p(q) {} MyUnique(T* q, D d) : DelHolder<D>(std::move(d)), p(q) {}
    MyUnique(const MyUnique&) = delete; MyUnique& operator=(const MyUnique&) = delete;
    MyUnique(MyUnique&& o) noexcept : DelHolder<D>(std::move(o.del())), p(o.p) { o.p = nullptr; }
    MyUnique& operator=(MyUnique&& o) noexcept { if (this != &o) { reset(); del() = std::move(o.del()); p = o.p; o.p = nullptr; } return *this; }
    ~MyUnique() { reset(); }
    T* get() const { return p; } T* release() { T* t = p; p = nullptr; return t; }
    void reset(T* q = nullptr) { T* old = p; p = q; if (old) del()(old); }
    T& operator*() const { return *p; } T* operator->() const { return p; } explicit operator bool() const { return p != nullptr; }
};
struct CtrlBase {
    std::atomic<long> strong{1}, weak{1};                                                          // weak 는 "강한 참조 전체 + 약한 참조들" 의 수
    virtual void destroyObject() = 0; virtual void destroySelf() = 0; virtual ~CtrlBase() = default;
    void incStrong() { strong.fetch_add(1, std::memory_order_relaxed); }
    bool incStrongIfNonZero() { long c = strong.load(std::memory_order_relaxed); while (c != 0) if (strong.compare_exchange_weak(c, c + 1, std::memory_order_acq_rel)) return true; return false; }
    void decStrong() { if (strong.fetch_sub(1, std::memory_order_acq_rel) == 1) { destroyObject(); decWeak(); } }
    void incWeak() { weak.fetch_add(1, std::memory_order_relaxed); }
    void decWeak() { if (weak.fetch_sub(1, std::memory_order_acq_rel) == 1) destroySelf(); }
};
template <class T, class D> struct Ctrl : CtrlBase { T* p; D d; Ctrl(T* q, D dd) : p(q), d(std::move(dd)) {} void destroyObject() override { d(p); } void destroySelf() override { delete this; } };
template <class T> class MyWeak;
template <class T> class MyShared {
    T* p = nullptr; CtrlBase* c = nullptr; friend class MyWeak<T>;
public:
    MyShared() = default;
    template <class D = DefaultDelete<T>> explicit MyShared(T* q, D d = D()) : p(q) { try { c = new Ctrl<T, D>(q, std::move(d)); } catch (...) { d(q); throw; } }
    MyShared(const MyShared& o) : p(o.p), c(o.c) { if (c) c->incStrong(); }
    MyShared(MyShared&& o) noexcept : p(o.p), c(o.c) { o.p = nullptr; o.c = nullptr; }
    MyShared& operator=(const MyShared& o) { MyShared tmp(o); swap(tmp); return *this; }
    MyShared& operator=(MyShared&& o) noexcept { MyShared tmp(std::move(o)); swap(tmp); return *this; }
    ~MyShared() { if (c) c->decStrong(); }
    void swap(MyShared& o) noexcept { std::swap(p, o.p); std::swap(c, o.c); }
    void reset() { MyShared().swap(*this); }
    T* get() const { return p; } T& operator*() const { return *p; } T* operator->() const { return p; }
    long use_count() const { return c ? c->strong.load() : 0; }
    explicit operator bool() const { return p != nullptr; }
};
template <class T> class MyWeak {
    T* p = nullptr; CtrlBase* c = nullptr;
public:
    MyWeak() = default;
    MyWeak(const MyShared<T>& s) : p(s.p), c(s.c) { if (c) c->incWeak(); }
    MyWeak(const MyWeak& o) : p(o.p), c(o.c) { if (c) c->incWeak(); }
    MyWeak& operator=(const MyWeak& o) { MyWeak t(o); std::swap(p, t.p); std::swap(c, t.c); return *this; }
    MyWeak& operator=(const MyShared<T>& s) { MyWeak t(s); std::swap(p, t.p); std::swap(c, t.c); return *this; }
    ~MyWeak() { if (c) c->decWeak(); }
    bool expired() const { return !c || c->strong.load() == 0; }
    long use_count() const { return c ? c->strong.load() : 0; }
    MyShared<T> lock() const { MyShared<T> s; if (c && c->incStrongIfNonZero()) { s.p = p; s.c = c; } return s; }
};
int destroyedStd = 0, destroyedMine = 0, createdStd = 0, createdMine = 0;
struct ResStd { int magic = 0x5eed; ResStd() { ++createdStd; } ~ResStd() { magic = 0; ++destroyedStd; } };
struct ResMine { int magic = 0x5eed; ResMine() { ++createdMine; } ~ResMine() { magic = 0; ++destroyedMine; } };
struct Node { MyShared<Node> next; MyWeak<Node> back; static int alive; Node() { ++alive; } ~Node() { --alive; } };
int Node::alive = 0;
int deleterCalls = 0;

int main() {
    int destroyed = 0; struct Res { int* d; ~Res() { ++*d; } };
    {   MyUnique<Res> u(new Res{&destroyed}); MyUnique<Res> v = std::move(u); assert(!u && v); }                  // 소유권 이전
    assert(destroyed == 1);
    static_assert(sizeof(MyUnique<int>) == sizeof(int*) && sizeof(std::unique_ptr<int>) == sizeof(int*), "삭제자가 비어 있으면 오버헤드 0");
    MyShared<Res> s1(new Res{&destroyed}); MyWeak<Res> w = s1;
    { MyShared<Res> s2 = s1; assert(s1.use_count() == 2); }                                                         // 공동 소유
    assert(s1.use_count() == 1 && !w.expired());
    s1.reset();                                                                                                      // 마지막 소유자가 사라지면 해제
    assert(destroyed == 2 && w.expired() && w.lock().get() == nullptr);
    int closed = 0;
    {   MyUnique<int, void (*)(int*)> custom(new int(5), [](int* p) { delete p; });
        MyShared<int> file(new int(1), [&closed](int* p) { delete p; closed++; }); MyShared<int> copy = file; }       // 사용자 지정 삭제자: 복사본이 있어도 한 번
    assert(closed == 1);
    // ⑤ unique 의 삭제자 호출 횟수
    {   deleterCalls = 0; auto counting = [](int* p) { ++deleterCalls; delete p; }; { MyUnique<int, void (*)(int*)> a(new int(1), counting), b(new int(2), counting); a = std::move(b); assert(deleterCalls == 1 && *a == 2 && !b); int* raw = a.release(); assert(!a && deleterCalls == 1); delete raw; a.reset(new int(3)); assert(deleterCalls == 1); a.reset(); assert(deleterCalls == 2); }
        assert(deleterCalls == 2); }
    // ② 차분 시험
    std::mt19937 rng(2025); const int H = 6; MyShared<ResMine> mine[H]; std::shared_ptr<ResStd> std_[H]; MyWeak<ResMine> wm[H]; std::weak_ptr<ResStd> ws[H]; long locks = 0, lockFails = 0;
    auto classes = [&](auto& handles) { std::vector<int> label(H); for (int i = 0; i < H; i++) { label[i] = -1; for (int j = 0; j <= i; j++) if (handles[j].get() == handles[i].get()) { label[i] = j; break; } if (!handles[i]) label[i] = -2; } return label; };      // 같은 객체를 가리키는 핸들끼리 같은 번호
    for (int step = 0; step < 30000; ++step) {
        int i = (int)(rng() % H), j = (int)(rng() % H), op = (int)(rng() % 9);
        switch (op) {
            case 0: mine[i] = MyShared<ResMine>(new ResMine); std_[i] = std::shared_ptr<ResStd>(new ResStd); break;                       // 새 객체 (이전 객체는 필요하면 소멸)
            case 1: mine[i] = mine[j]; std_[i] = std_[j]; break;                                                                         // 복사 대입
            case 2: { MyShared<ResMine> a = std::move(mine[j]); std::shared_ptr<ResStd> b = std::move(std_[j]); mine[i] = std::move(a); std_[i] = std::move(b); break; }   // 이동
            case 3: mine[i].reset(); std_[i].reset(); break;
            case 4: mine[i].swap(mine[j]); std_[i].swap(std_[j]); break;
            case 5: wm[i] = mine[j]; ws[i] = std_[j]; break;                                                                             // weak 대입
            case 6: { MyShared<ResMine> a = wm[j].lock(); std::shared_ptr<ResStd> b = ws[j].lock(); assert((bool)a == (bool)b); ++locks; lockFails += !a; if (a) { assert(a->magic == 0x5eed && b->magic == 0x5eed && a.use_count() == b.use_count()); mine[i] = a; std_[i] = b; } break; }       // lock 이 성공하면 객체는 살아 있다
            case 7: { MyShared<ResMine> copy = mine[j]; std::shared_ptr<ResStd> copy2 = std_[j]; assert(copy.use_count() == copy2.use_count()); break; }             // 임시 복사본은 use_count 를 일시적으로 올린다
            default: wm[i] = MyWeak<ResMine>(); ws[i] = std::weak_ptr<ResStd>(); break;
        }
        for (int k = 0; k < H; k++) assert(mine[k].use_count() == std_[k].use_count() && wm[k].expired() == ws[k].expired() && wm[k].use_count() == ws[k].use_count());
        assert(classes(mine) == classes(std_) && destroyedMine == destroyedStd && createdMine == createdStd);
    }
    for (int k = 0; k < H; k++) { mine[k].reset(); std_[k].reset(); }
    assert(destroyedMine == createdMine && destroyedStd == createdStd && createdMine == createdStd && createdMine > 1000 && locks > 2000 && lockFails > 100);
    // ③ 순환 참조
    {   Node::alive = 0; MyWeak<Node> watcher;
        { MyShared<Node> a(new Node), b(new Node); a->next = b; b->next = a; watcher = a; }                       // 서로를 강하게 가리킨다 → 바깥 핸들이 사라져도 둘 다 산다
        assert(Node::alive == 2 && !watcher.expired() && watcher.use_count() == 1);                                 // 누수 상태 (A 는 B 의 next 가 쥐고 있다)
        { MyShared<Node> t = watcher.lock(); assert(t.use_count() == 2); t->next.reset(); }                         // 한 고리를 끊으면 연쇄로 해제
        assert(Node::alive == 0 && watcher.expired());
        { MyShared<Node> a(new Node), b(new Node); a->next = b; b->back = a; }                                      // 되돌아가는 쪽을 weak 로 두면 처음부터 새지 않는다
        assert(Node::alive == 0); }
    // ④ 스레드 경합
    {   destroyedMine = createdMine = 0; MyShared<ResMine> obj(new ResMine); MyWeak<ResMine> watch = obj; std::atomic<bool> go{false}; std::atomic<long> lockOk{0}, bad{0}; std::vector<std::thread> th;
        for (int t = 0; t < 8; t++) th.emplace_back([&, t] { while (!go.load()) {} for (int i = 0; i < 20000; i++) { MyShared<ResMine> c = obj; MyShared<ResMine> d = c; if (t % 2) { MyShared<ResMine> l = watch.lock(); if (l) { ++lockOk; if (l->magic != 0x5eed) ++bad; } } } });
        go = true; for (auto& x : th) x.join(); assert(obj.use_count() == 1 && bad == 0 && lockOk == 4 * 20000 && destroyedMine == 0);
        obj.reset(); assert(destroyedMine == 1 && watch.expired() && watch.lock().get() == nullptr);
        // 마지막 reset 과 lock 이 동시에: lock 이 성공했다면 객체는 살아 있다
        long ok = 0, fail = 0, corrupt = 0;
        for (int round = 0; round < 300; round++) { MyShared<ResMine> o(new ResMine); MyWeak<ResMine> wk = o; std::atomic<bool> start{false}; std::atomic<long> okR{0}, failR{0}, corruptR{0};
            std::thread locker([&] { while (!start.load()) {} MyShared<ResMine> l = wk.lock(); if (l) { ++okR; if (l->magic != 0x5eed) ++corruptR; } else ++failR; });
            start = true; o.reset(); locker.join(); ok += okR; fail += failR; corrupt += corruptR; }
        assert(corrupt == 0 && ok + fail == 300); }
    std::cout << "SmartPointer verified: MyShared/MyWeak matched std::shared_ptr/weak_ptr over 30000 random operations (" << locks << " lock() calls, " << lockFails << " failed) and survived the thread races." << std::endl;
    return 0;
}
// Time Complexity: unique_ptr O(1), shared_ptr 복사 O(1) (원자적 카운터)
// Space Complexity: shared_ptr 은 제어 블록 추가
```
## Aliasing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <set>
#include <type_traits>
#include <vector>

// 앨리어싱: 서로 다른 이름이 같은 메모리를 가리키는 것.  컴파일러는 "다른 타입의 포인터는 같은 메모리를 가리키지 않는다"(엄격한 앨리어싱 규칙)고
// 가정해 최적화하므로, float 비트를 uint32_t* 로 읽는 reinterpret_cast 는 정의되지 않은 동작이다.  안전한 방법은 memcpy (컴파일러가 한 명령으로 최적화한다)
// 이 예제는 "비트를 안전하게 들여다보는" 도구를 직접 만들고 독립 기준과 맞춰 본다.
//  ① floatBits/bitsFloat/bitCast: memcpy 로 만든 비트 캐스트.  IEEE-754 를 손으로 해석(decodeFloat)한 값이 하드웨어 float 값과 같은지, frexp 가 말하는 지수·가수와 같은지 4 000 000 개 패턴 이상으로 확인
//  ② ULP: 양의 유한 float 에서 비트 패턴 +1 은 nextafter 와 같다 (비트 패턴이 곧 순서)
//  ③ 단조 키: 부호 비트가 1 이면 전체 반전, 0 이면 최상위 비트 설정 -> 부호 없는 정수 순서가 float 순서가 된다.  기수 정렬로 std::sort 와 같은 결과가 나오는지 확인
//  ④ 겹침: overlaps 를 바이트 집합의 교집합과 모든 (a, na, b, nb) 조합에서 대조 (빈 구간은 아무것과도 겹치지 않는다 — 그 검사를 뺀 판본의 오류도 센다)
//  ⑤ memmove: 겹침 방향에 따라 앞/뒤에서 복사하는 직접 구현을 std::memmove 와 모든 (src, dst, n) 조합에서 대조, 앞에서만 복사하면 정확히 "dst 가 src 안쪽에 놓인" 경우만 틀림
//  ⑥ 같은 타입 포인터 앨리어싱은 합법이라, 두 포인터가 같으면 결과가 달라진다 (컴파일러가 *b 를 레지스터에 캐시하지 못하는 이유)
uint32_t floatBits(float f) { uint32_t u; std::memcpy(&u, &f, sizeof u); return u; }
float bitsFloat(uint32_t u) { float f; std::memcpy(&f, &u, sizeof f); return f; }

template <class To, class From> To bitCast(const From& f) {          // C++20 std::bit_cast 와 같은 일을 C++17 에서
    static_assert(sizeof(To) == sizeof(From) && std::is_trivially_copyable<To>::value && std::is_trivially_copyable<From>::value, "크기가 같고 trivially copyable 이어야 한다");
    To t; std::memcpy(&t, &f, sizeof t); return t;
}

bool overlapsNoEmptyCheck(const void* a, size_t na, const void* b, size_t nb) {
    auto x = (uintptr_t)a, y = (uintptr_t)b; return x < y + nb && y < x + na;
}
bool overlaps(const void* a, size_t na, const void* b, size_t nb) { return na && nb && overlapsNoEmptyCheck(a, na, b, nb); }

// IEEE-754 binary32 를 부호·지수·가수 필드로 손수 해석 (정규수 1.m×2^(e-127), 비정규수 0.m×2^-126)
double decodeFloat(uint32_t u) {
    int s = (int)(u >> 31), e = (int)((u >> 23) & 0xff); uint32_t m = u & 0x7fffffu; double v;
    if (e == 0xff) return m ? std::nan("") : (s ? -INFINITY : INFINITY);
    if (e == 0) v = std::ldexp((double)m, -149);                         // m × 2^-149
    else v = std::ldexp((double)(m | 0x800000u), e - 150);              // (2^23 + m) × 2^(e-150)
    return s ? -v : v;
}

uint32_t sortKey(float f) { uint32_t u = floatBits(f); return (u & 0x80000000u) ? ~u : (u | 0x80000000u); }
void radixSortFloats(std::vector<float>& a) {                               // 키를 8 비트씩 4 번 계수 정렬 (안정)
    std::vector<uint32_t> k(a.size()), t(a.size());
    for (size_t i = 0; i < a.size(); ++i) k[i] = sortKey(a[i]);
    for (int pass = 0; pass < 4; ++pass) {
        size_t cnt[257] = {0}; int sh = pass * 8;
        for (uint32_t x : k) ++cnt[((x >> sh) & 0xff) + 1];
        for (int i = 0; i < 256; ++i) cnt[i + 1] += cnt[i];
        for (uint32_t x : k) t[cnt[(x >> sh) & 0xff]++] = x;
        k.swap(t);
    }
    for (size_t i = 0; i < a.size(); ++i) { uint32_t x = k[i]; a[i] = bitsFloat((x & 0x80000000u) ? (x & 0x7fffffffu) : ~x); }
}

void* myMemmove(void* d, const void* s, size_t n) {
    unsigned char* dp = (unsigned char*)d; const unsigned char* sp = (const unsigned char*)s;
    if (n == 0 || dp == sp) return d;
    if (dp < sp || dp >= sp + n) { for (size_t i = 0; i < n; ++i) dp[i] = sp[i]; }          // 앞에서 뒤로: 겹쳐도 아직 안 읽은 바이트를 안 덮는다
    else for (size_t i = n; i-- > 0;) dp[i] = sp[i];                                              // dst 가 src 안쪽: 뒤에서 앞으로
    return d;
}
void forwardCopy(unsigned char* d, const unsigned char* s, size_t n) { for (size_t i = 0; i < n; ++i) d[i] = s[i]; }
void addTwice(int* a, const int* b) { *a += *b; *a += *b; }

int main() {
    // 원래 예: 비트 패턴과 겹침
    assert(floatBits(1.0f) == 0x3f800000u && floatBits(-2.0f) == 0xc0000000u && floatBits(0.0f) == 0u && floatBits(-0.0f) == 0x80000000u);
    assert(bitsFloat(0x40490fdbu) > 3.14159f && bitsFloat(0x40490fdbu) < 3.1416f);
    int v = 5; int* p = &v; int* q = &v; *p = 6; assert(*q == 6);                       // 같은 타입의 앨리어싱은 합법
    char buf[10] = "abcdefghi";
    assert(overlaps(buf, 5, buf + 3, 5) && !overlaps(buf, 3, buf + 5, 3));
    std::memmove(buf + 2, buf, 5);
    assert(std::memcmp(buf, "ababcdeh", 8) == 0);

    // ① 바이트로 본 객체 표현 + 비트 캐스트의 왕복 + 직접 해석
    uint32_t one = 1; unsigned char first; std::memcpy(&first, &one, 1); bool little = (first == 1);
    unsigned char fb[4]; float f1 = 1.0f; std::memcpy(fb, &f1, 4);                       // unsigned char* 는 어떤 객체든 읽을 수 있다 (앨리어싱 규칙의 예외)
    assert(little ? (fb[3] == 0x3f && fb[2] == 0x80 && fb[1] == 0 && fb[0] == 0) : (fb[0] == 0x3f && fb[1] == 0x80));
    struct Pair { int32_t a, b; }; Pair pr{1, 2}; int64_t as64 = bitCast<int64_t>(pr);
    assert(as64 == (little ? (int64_t)1 | ((int64_t)2 << 32) : ((int64_t)1 << 32) | 2) && bitCast<Pair>(as64).b == 2);
    assert(bitCast<uint64_t>(1.0) == 0x3ff0000000000000ull && bitCast<double>(0x4000000000000000ull) == 2.0);
    long checked = 0, normals = 0, denorm = 0, specials = 0;
    auto check = [&](uint32_t u) {
        float f = bitsFloat(u); assert(floatBits(f) == u || std::isnan(f));
        double d = decodeFloat(u); ++checked;
        if (std::isnan(f)) { assert(std::isnan(d)); ++specials; return; }
        assert(d == (double)f && std::signbit(d) == std::signbit(f));                          // 손으로 해석한 값 == 하드웨어 값 (부호 있는 0 포함)
        int e = (int)((u >> 23) & 0xff);
        if (std::isinf(f)) { ++specials; return; }
        if (e == 0) { ++denorm; return; }
        ++normals; int ex; double fr = std::frexp(d, &ex);                                      // d = fr × 2^ex, 0.5 <= |fr| < 1
        assert(ex == e - 126 && std::ldexp(std::fabs(fr) * 2 - 1, 23) == (double)(u & 0x7fffffu));
    };
    for (uint32_t u = 0; u < (1u << 14); ++u) { check(u); check(0x80000000u | u); check(0x7f800000u - 8192 + u); check(0xff800000u - 8192 + u); }    // 0 근방, 무한대 근방 모두 빠짐없이
    for (uint32_t u = 0; u < 0xffffff00u; u += 1021) check(u);                                              // 나머지 전 범위를 소수 간격으로
    std::mt19937 rng(20240601u);
    for (int i = 0; i < 600000; ++i) check((uint32_t)rng());
    assert(normals > 3000000 && denorm > 30000 && specials > 20000);

    // ② 비트 패턴 +1 == 다음 float (양의 유한수)
    for (int i = 0; i < 400000; ++i) {
        uint32_t u = (uint32_t)rng() & 0x7fffffffu; if (u >= 0x7f7fffffu) continue;
        assert(bitsFloat(u + 1) == std::nextafter(bitsFloat(u), INFINITY) && bitsFloat(u + 1) > bitsFloat(u));
    }

    // ③ 정렬 키: 부호 없는 정수 순서 == float 순서
    std::vector<float> a;
    for (int i = 0; i < 100000; ++i) {
        float f = bitsFloat((uint32_t)rng()); if (std::isnan(f)) continue;
        a.push_back(f); if (i % 7 == 0) a.push_back(std::round(f)); if (i % 11 == 0) a.push_back(-0.0f), a.push_back(0.0f);
    }
    for (int i = 0; i < 500000; ++i) {
        float x = a[rng() % a.size()], y = a[rng() % a.size()];
        if (x < y) { assert(sortKey(x) < sortKey(y)); }
        if (x > y) { assert(sortKey(x) > sortKey(y)); }
    }
    std::vector<float> ref = a, rs = a; std::sort(ref.begin(), ref.end()); radixSortFloats(rs);
    assert(rs.size() == ref.size()); for (size_t i = 0; i < rs.size(); ++i) assert(rs[i] == ref[i]);
    assert(floatBits(rs.front()) >= 0x80000000u && std::is_sorted(rs.begin(), rs.end()));

    // ④ 겹침 판정: 모든 (a, na, b, nb) 를 바이트 집합의 교집합과 대조
    const int N = 14; unsigned char arena[N]; long cases = 0, naiveWrong = 0;
    for (int x = 0; x <= N; ++x) for (int nx = 0; x + nx <= N; ++nx) for (int y = 0; y <= N; ++y) for (int ny = 0; y + ny <= N; ++ny) {
        std::set<int> sa, sb; for (int i = 0; i < nx; ++i) sa.insert(x + i); for (int i = 0; i < ny; ++i) sb.insert(y + i);
        bool truth = false; for (int i : sa) if (sb.count(i)) truth = true;
        bool got = overlaps(arena + x, nx, arena + y, ny); assert(got == truth); ++cases;
        if (overlapsNoEmptyCheck(arena + x, nx, arena + y, ny) != truth) { ++naiveWrong; assert(nx == 0 || ny == 0); }
    }
    assert(cases == 14400 && naiveWrong > 0);

    // ⑤ memmove: 모든 (src, dst, n) 조합 (24 바이트 영역)
    const int M = 24; long moves = 0, forwardBroken = 0;
    for (int s = 0; s < M; ++s) for (int d = 0; d < M; ++d) for (int n = 0; s + n <= M && d + n <= M; ++n) {
        unsigned char base[M], expect[M], mine[M], lib[M], fwd[M];
        for (int i = 0; i < M; ++i) base[i] = (unsigned char)(i + 1);
        std::memcpy(expect, base, M); for (int i = 0; i < n; ++i) expect[d + i] = base[s + i];                          // 기준: 원본에서 읽은 값을 쓴다
        std::memcpy(mine, base, M); myMemmove(mine + d, mine + s, n); assert(std::memcmp(mine, expect, M) == 0);
        std::memcpy(lib, base, M); std::memmove(lib + d, lib + s, n); assert(std::memcmp(lib, expect, M) == 0);
        std::memcpy(fwd, base, M); forwardCopy(fwd + d, fwd + s, n);
        bool hazard = n > 0 && s < d && d < s + n;                                                                            // 앞에서 복사하면 덮어쓰는 경우
        assert((std::memcmp(fwd, expect, M) != 0) == hazard); forwardBroken += hazard; ++moves;
    }
    assert(moves == 5476 && forwardBroken > 0);

    // ⑥ 앨리어싱 때문에 컴파일러가 *b 를 캐시하지 못한다
    int x = 3, y = 5; addTwice(&x, &y); assert(x == 13 && y == 5);                      // 서로 다른 객체: 3 + 5 + 5
    int z = 3; addTwice(&z, &z); assert(z == 12);                                          // 같은 객체: 3 -> 6 -> 12
    std::cout << "Aliasing verified: " << checked << " float patterns, " << cases << " overlap cases (" << naiveWrong << " wrong without the empty check), "
              << moves << " memmove cases (" << forwardBroken << " broken by forward copy)" << std::endl;
    return 0;
}
// Time Complexity: 비트 캐스트 O(1) (memcpy 가 한 명령으로 바뀐다), 기수 정렬 O(n), memmove O(n)
// Space Complexity: O(1)
```
# Part 6. 메모리 할당기
## MemoryPool()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 메모리 풀: 같은 크기의 블록을 덩어리(chunk) 단위로 확보해 두고 자유 리스트로 나눠 준다.  빈 블록의 앞부분에 "다음 빈 블록" 포인터를 저장하므로 추가 메모리가 없고,
// 할당·해제가 모두 O(1) 포인터 교환이다.  크기가 같아서 외부 단편화가 없다.  malloc 의 탐색·병합 비용이 없어 게임·네트워크 서버에서 많이 쓴다
// 이 구현의 성질: 풀이 비었을 때만 덩어리를 하나 더 받는다(상한 maxChunks 가 있으면 nullptr).  블록은 16 바이트 단위로 올려 항상 16 바이트 정렬.
//  해제된 블록에는 표식(magic)을 남겨 같은 블록의 이중 해제와 풀 밖/블록 경계가 아닌 포인터를 거절한다(휴리스틱: 사용자가 같은 값을 직접 쓰면 속는다).
// 검증: 무작위 할당/해제 200 000 번을 std::set 으로 대조 — 서로 다른 블록, 정렬, 덩어리 안, 블록마다 다른 무늬를 채워 서로 덮어쓰지 않음, 자유 리스트 길이 == 전체 - 사용 중(순환·외부 포인터 없음),
//        덩어리 수 == ceil(최대 동시 사용 / 덩어리당 블록 수) (풀은 줄지 않는다), 시스템 호출 수 == 덩어리 수
class MemoryPool {
    static const uint64_t FREE_MAGIC = 0xF4EEF4EEF4EEF4EEull;
    struct Node { Node* next; uint64_t magic; };
    std::vector<unsigned char*> chunks; Node* head = nullptr;
    size_t blockSize, perChunk, maxChunks, used = 0, total = 0;
    bool grow() {
        if (chunks.size() >= maxChunks) return false;
        unsigned char* c = new unsigned char[blockSize * perChunk]; chunks.push_back(c); ++systemCalls; total += perChunk;
        for (size_t i = perChunk; i-- > 0;) { Node* n = (Node*)(c + i * blockSize); n->magic = FREE_MAGIC; n->next = head; head = n; }   // 주소 오름차순으로 나눠 주도록 역순으로 연결
        return true;
    }
public:
    long systemCalls = 0;
    MemoryPool(size_t block, size_t per, size_t maxCh = (size_t)-1) : blockSize((std::max(block, sizeof(Node)) + 15) & ~size_t(15)), perChunk(per), maxChunks(maxCh) {}
    MemoryPool(const MemoryPool&) = delete; MemoryPool& operator=(const MemoryPool&) = delete;
    ~MemoryPool() { for (unsigned char* c : chunks) delete[] c; }
    void* alloc() { if (!head && !grow()) return nullptr; Node* n = head; head = n->next; n->magic = 0; ++used; return n; }
    bool owns(const void* p) const {                                                                   // 풀 안이고 블록 경계인가
        for (unsigned char* c : chunks) if ((const unsigned char*)p >= c && (const unsigned char*)p < c + blockSize * perChunk) return ((const unsigned char*)p - c) % blockSize == 0;
        return false;
    }
    bool release(void* p) {
        if (!owns(p)) return false;
        Node* n = (Node*)p; if (n->magic == FREE_MAGIC) return false;                                 // 이미 해제된 블록
        n->magic = FREE_MAGIC; n->next = head; head = n; --used; return true;
    }
    size_t inUse() const { return used; } size_t capacity() const { return total; } size_t chunkCount() const { return chunks.size(); } size_t block() const { return blockSize; }
    size_t freeListLength(std::set<const void*>* seen = nullptr) const {                                // 검증용: 자유 리스트를 끝까지 걷는다
        size_t n = 0; for (Node* x = head; x; x = x->next) { if (++n > total) return n; if (seen && !seen->insert(x).second) return total + 1; if (x->magic != FREE_MAGIC) return total + 1; }
        return n;
    }
};

int main() {
    // 원래 예: 작은 풀
    {   MemoryPool pool(32, 4, 1);
        void* b[4]; std::set<void*> distinct;
        for (int i = 0; i < 4; i++) { b[i] = pool.alloc(); assert(b[i] && pool.owns(b[i])); distinct.insert(b[i]); }
        assert(distinct.size() == 4 && pool.alloc() == nullptr && pool.inUse() == 4);                  // 서로 다른 블록, 가득 차면 nullptr
        pool.release(b[1]); pool.release(b[3]);
        assert(pool.alloc() == b[3] && pool.alloc() == b[1]);                                         // 가장 최근에 반환된 블록이 먼저 (LIFO)
        assert((uintptr_t)b[1] - (uintptr_t)b[0] == 32 && pool.block() == 32);
        assert(!pool.release((char*)b[0] + 8) && !pool.release(&pool) && pool.inUse() == 4);          // 블록 경계가 아닌 포인터, 풀 밖 포인터
        assert(pool.release(b[0]) && !pool.release(b[0]) && pool.inUse() == 3);                       // 이중 해제 거절
    }
    // 크기 올림과 상한
    { MemoryPool tiny(1, 3); assert(tiny.block() == 16); void* p = tiny.alloc(); assert((uintptr_t)p % 16 == 0); MemoryPool odd(40, 3); assert(odd.block() == 48); }
    { MemoryPool cap(24, 4, 2); std::vector<void*> v; void* p; while ((p = cap.alloc())) v.push_back(p); assert(v.size() == 8 && cap.chunkCount() == 2 && cap.capacity() == 8);
      assert(cap.release(v[5]) && cap.alloc() == v[5] && cap.alloc() == nullptr); }

    // 차분 시험: 무작위 할당/해제
    for (int cfg = 0; cfg < 3; ++cfg) {
        size_t blk = cfg == 0 ? 16 : cfg == 1 ? 56 : 200, per = cfg == 0 ? 7 : cfg == 1 ? 16 : 3;
        MemoryPool pool(blk, per); std::mt19937 rng(77 + cfg);
        std::map<unsigned char*, unsigned char> live; size_t peak = 0; long allocs = 0, frees = 0;
        for (int step = 0; step < 70000; ++step) {
            bool doAlloc = live.empty() || (rng() % 100 < (step % 20000 < 10000 ? 60u : 40u));     // 늘었다 줄었다 하는 부하
            if (doAlloc) {
                unsigned char* p = (unsigned char*)pool.alloc(); assert(p && !live.count(p) && (uintptr_t)p % 16 == 0 && pool.owns(p));
                unsigned char tag = (unsigned char)(1 + rng() % 250); std::fill(p, p + pool.block(), tag); live[p] = tag; ++allocs;   // 블록 전체를 무늬로 채운다
                peak = std::max(peak, live.size());
            } else {
                auto it = live.begin(); std::advance(it, rng() % live.size());
                for (size_t i = 0; i < pool.block(); ++i) assert(it->first[i] == it->second);                          // 다른 블록이나 자유 리스트가 이 블록을 덮어쓰지 않았다
                assert(pool.release(it->first)); live.erase(it); ++frees;
            }
            assert(pool.inUse() == live.size());
            if (step % 997 == 0) { std::set<const void*> seen; assert(pool.freeListLength(&seen) == pool.capacity() - pool.inUse()); for (auto& kv : live) assert(!seen.count(kv.first)); }
        }
        for (auto& kv : live) for (size_t i = 0; i < pool.block(); ++i) assert(kv.first[i] == kv.second);
        assert(pool.chunkCount() == (peak + per - 1) / per && pool.capacity() == pool.chunkCount() * per && pool.systemCalls == (long)pool.chunkCount());
        assert(allocs - frees == (long)live.size() && peak > 100);
        std::vector<unsigned char*> rest; for (auto& kv : live) rest.push_back(kv.first); for (auto p : rest) assert(pool.release(p));
        std::set<const void*> seen; assert(pool.inUse() == 0 && pool.freeListLength(&seen) == pool.capacity());           // 전부 돌려주면 자유 리스트가 전체
    }
    std::cout << "MemoryPool verified: 3 pool shapes x 70000 random ops, no overlap, free list intact, chunks = ceil(peak/chunk)." << std::endl;
    return 0;
}
// Time Complexity: 할당 O(1) (덩어리가 필요하면 덩어리 크기), 해제 O(덩어리 수) (owns 검증 포함 — 검증을 빼면 O(1))
// Space Complexity: O(블록 크기 · 개수)
```
## ObjectPool()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <memory>
#include <new>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// 객체 풀: 메모리 풀 위에 "객체 생명주기" 를 얹는다.  acquire 는 배치 new 로 생성자를, release 는 소멸자를 부르고 메모리(슬롯)는 풀에 남겨 재사용한다.
// 생성 비용이 큰 객체(연결, 스레드, 버퍼)를 재사용하는 데 쓰이고, 반환되지 않은 객체의 수로 누수를 바로 알 수 있다
// 이 구현: 슬롯 덩어리의 크기를 1, 2, 4, 8 ... 로 두 배씩 늘리고(주소가 안 바뀐다) 슬롯마다 live 표시를 둔다.  자유 슬롯 스택은 LIFO.
//  ① 생성자가 예외를 던지면 슬롯을 되돌려 놓고 개수가 변하지 않는다  ② 같은 객체를 두 번 release 하거나 풀 밖 포인터를 release 하면 거절한다
//  ③ 풀이 소멸할 때 아직 살아 있는 객체는 소멸자를 호출한다 (누수 없이)  ④ alignas(64) 객체도 정렬이 맞는다
// 검증: 생성/소멸 횟수와 살아 있는 id 집합을 계측 클래스로 추적하며 무작위 acquire/release 100 000 번을 std::map 모형과 대조 — 값 보존, 슬롯 재사용(LIFO), 용량 == 2^덩어리 - 1
template <class T>
class ObjectPool {
    struct Slot { alignas(T) unsigned char buf[sizeof(T)]; bool live; };
    std::vector<std::unique_ptr<Slot[]>> chunks; std::vector<size_t> sizes; std::vector<Slot*> freeStack; size_t live = 0;
    void grow() {
        size_t n = chunks.empty() ? 1 : sizes.back() * 2; chunks.emplace_back(new Slot[n]); sizes.push_back(n);
        for (size_t i = n; i-- > 0;) { chunks.back()[i].live = false; freeStack.push_back(&chunks.back()[i]); }   // 낮은 주소가 먼저 나가도록 역순으로 쌓는다
    }
    Slot* slotOf(T* obj) const {
        for (size_t c = 0; c < chunks.size(); ++c) { Slot* s = chunks[c].get(); if ((unsigned char*)obj >= (unsigned char*)s && (unsigned char*)obj < (unsigned char*)(s + sizes[c]) && (unsigned char*)obj == s[((unsigned char*)obj - (unsigned char*)s) / sizeof(Slot)].buf) return &s[((unsigned char*)obj - (unsigned char*)s) / sizeof(Slot)]; }
        return nullptr;
    }
public:
    ObjectPool() = default; ObjectPool(const ObjectPool&) = delete; ObjectPool& operator=(const ObjectPool&) = delete;
    ~ObjectPool() { for (size_t c = 0; c < chunks.size(); ++c) for (size_t i = 0; i < sizes[c]; ++i) if (chunks[c][i].live) reinterpret_cast<T*>(chunks[c][i].buf)->~T(); }
    template <class... A> T* acquire(A&&... args) {
        if (freeStack.empty()) grow();
        Slot* s = freeStack.back(); freeStack.pop_back();
        try { T* obj = new (s->buf) T(std::forward<A>(args)...); s->live = true; ++live; return obj; }
        catch (...) { freeStack.push_back(s); throw; }                                              // 생성 실패: 슬롯을 돌려놓고 예외를 그대로 전달
    }
    bool release(T* obj) {
        Slot* s = slotOf(obj); if (!s || !s->live) return false;
        obj->~T(); s->live = false; freeStack.push_back(s); --live; return true;
    }
    size_t liveCount() const { return live; } size_t chunkCount() const { return chunks.size(); }
    size_t capacity() const { size_t n = 0; for (size_t s : sizes) n += s; return n; }
};

int constructed = 0, destroyed = 0;
std::map<int, int> alive;                                            // id -> 값 (계측: 살아 있는 객체)
struct Conn { std::string host; explicit Conn(std::string h) : host(std::move(h)) { constructed++; } ~Conn() { destroyed++; } };
struct Tracked {
    int id, value; static int nextId;
    explicit Tracked(int v) : id(nextId++), value(v) { if (v < 0) throw std::invalid_argument("negative"); alive[id] = v; ++constructed; }
    ~Tracked() { assert(alive.count(id) && alive[id] == value); alive.erase(id); ++destroyed; }      // 소멸 시점에 값이 보존돼 있어야 한다
};
int Tracked::nextId = 1;
struct alignas(64) Wide { char c[64]; };

int main() {
    // 원래 예
    {   ObjectPool<Conn> pool; constructed = destroyed = 0;
        Conn* a = pool.acquire("alpha"); Conn* b = pool.acquire("beta");
        assert(a->host == "alpha" && b->host == "beta" && pool.liveCount() == 2 && constructed == 2);
        assert(pool.release(a) && destroyed == 1 && pool.liveCount() == 1);                         // 소멸자는 불리지만 슬롯은 남는다
        Conn* c = pool.acquire("gamma"); assert(c == a && c->host == "gamma");                       // 같은 자리를 재사용
        assert(!pool.release(a + 5) && pool.release(b) && pool.release(c) && !pool.release(c) && pool.liveCount() == 0 && constructed == destroyed);
    }
    // 예외 안전: 생성자가 던지면 슬롯이 새지 않는다
    {   constructed = destroyed = 0; alive.clear(); ObjectPool<Tracked> pool;
        Tracked* ok = pool.acquire(1); assert(pool.capacity() == 1);
        try { pool.acquire(-5); assert(false); } catch (const std::invalid_argument&) {}                // 이 시도가 덩어리를 늘렸지만(1 -> 3) 슬롯은 자유 상태로 돌아왔다
        assert(pool.liveCount() == 1 && pool.capacity() == 3 && constructed == 1 && alive.size() == 1);
        Tracked* again = pool.acquire(2); Tracked* third = pool.acquire(3);                              // 되돌린 슬롯까지 써도 더 늘지 않는다
        assert(again != ok && third != ok && again != third && again->value == 2 && pool.liveCount() == 3 && pool.capacity() == 3 && pool.chunkCount() == 2);
        assert(constructed == 3 && destroyed == 0);
    }
    assert(destroyed == 3 && alive.empty());                                                        // 풀이 소멸하며 살아 있던 세 객체를 소멸
    // 정렬
    {   ObjectPool<Wide> wp; std::vector<Wide*> ws; for (int i = 0; i < 40; ++i) { ws.push_back(wp.acquire()); assert((uintptr_t)ws.back() % 64 == 0); }
        for (Wide* w : ws) assert(wp.release(w)); }
    // 차분 시험
    {   constructed = destroyed = 0; alive.clear(); Tracked::nextId = 1;
        ObjectPool<Tracked> pool; std::mt19937 rng(2024);
        std::map<Tracked*, int> model; size_t peak = 0; long reused = 0; std::vector<Tracked*> lastFreed;
        for (int step = 0; step < 100000; ++step) {
            bool doAcq = model.empty() || rng() % 100 < (step % 30000 < 15000 ? 58u : 42u);
            if (doAcq) {
                int v = (int)(rng() % 100000);
                Tracked* t = pool.acquire(v); assert(t->value == v && !model.count(t)); model[t] = v; peak = std::max(peak, model.size());
                if (!lastFreed.empty() && t == lastFreed.back()) { ++reused; }
                lastFreed.clear();         // 직전에 반환한 슬롯이 바로 재사용되는가 (LIFO)
            } else {
                auto it = model.begin(); std::advance(it, rng() % model.size());
                assert(it->first->value == it->second); Tracked* p = it->first; assert(pool.release(p)); model.erase(it); lastFreed.assign(1, p);
                assert(!pool.release(p));                                                            // 이중 해제 거절
            }
            assert(pool.liveCount() == model.size() && alive.size() == model.size());
        }
        for (auto& kv : model) assert(kv.first->value == kv.second);
        assert(constructed - destroyed == (int)model.size() && pool.capacity() >= peak);
        size_t cap = pool.capacity(); assert(cap == ((size_t)1 << pool.chunkCount()) - 1 && (cap - 1) / 2 < peak);   // 용량은 2^k - 1, 최대 동시 개수를 처음 넘는 값
        assert(reused > 1000);
        for (auto& kv : model) pool.release(kv.first);
        assert(pool.liveCount() == 0 && alive.empty() && constructed == destroyed);
    }
    std::cout << "ObjectPool verified: " << constructed << " constructions all matched by destructions, slots reused LIFO, exception-safe." << std::endl;
    return 0;
}
// Time Complexity: acquire O(1) 평균(덩어리 증설 시 O(덩어리 크기)), release O(덩어리 수) (소유 확인 포함)
// Space Complexity: O(최대 동시 객체 수)
```
## FreeList()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <iterator>
#include <map>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 자유 리스트 할당기: 비어 있는 구멍(hole)을 주소순으로 유지한다.  요청이 오면 어떤 구멍을 쓸지가 정책이다.
//   first-fit: 주소가 가장 낮은 맞는 구멍 (빠름)   best-fit: 가장 작게 맞는 구멍 (남는 조각이 가장 작음, 아주 작은 조각이 많이 생김)   worst-fit: 가장 큰 구멍 (남는 조각이 큼)
// 해제할 때는 인접한 구멍과 병합해 외부 단편화를 줄이고, 구멍과 겹치는 해제(이중 해제)는 거절한다
// 세 가지 구현을 같은 연산열에 적용해 서로 맞춘다:  ① ListFreeList: 주소순 벡터 (선형 탐색, 원래 구현)
//   ② IndexedFreeList: 주소 맵 + (크기, 주소) 집합 -> best/worst-fit 이 O(log n)  ③ BitmapOracle: 바이트마다 사용 여부를 둔 독립 기준 (구멍을 비트맵에서 매번 새로 계산)
// 검증: 크기 1024 의 힙에서 정책마다 무작위 할당/해제/잘못된 해제 20 000 번 — 반환 주소가 세 구현에서 모두 같고, 구멍은 정렬·비어 있지 않음·서로 인접하지 않음(완전 병합), 자유 바이트 합이 같다
enum Policy { FIRST, BEST, WORST };
struct Hole { size_t off, size; };

class ListFreeList {
public:
    std::vector<Hole> holes;
    explicit ListFreeList(size_t total) { holes.push_back({0, total}); }
    explicit ListFreeList(std::vector<Hole> h) : holes(std::move(h)) {}
    long alloc(size_t n, Policy p) {
        if (n == 0) return -1;
        int pick = -1;
        for (size_t i = 0; i < holes.size(); i++) {
            if (holes[i].size < n) continue;
            if (pick < 0 || (p == BEST && holes[i].size < holes[pick].size) || (p == WORST && holes[i].size > holes[pick].size)) pick = (int)i;     // 크기가 같으면 앞의(낮은 주소) 구멍 유지
            if (p == FIRST) break;
        }
        if (pick < 0) return -1;
        size_t off = holes[pick].off; holes[pick].off += n; holes[pick].size -= n;
        if (holes[pick].size == 0) holes.erase(holes.begin() + pick);
        return (long)off;
    }
    bool release(size_t off, size_t n, size_t total) {
        if (n == 0 || off + n > total) return false;
        size_t i = std::lower_bound(holes.begin(), holes.end(), off, [](const Hole& h, size_t o) { return h.off < o; }) - holes.begin();
        if (i > 0 && holes[i - 1].off + holes[i - 1].size > off) return false;                       // 앞 구멍과 겹침
        if (i < holes.size() && off + n > holes[i].off) return false;                                  // 뒤 구멍과 겹침
        bool left = i > 0 && holes[i - 1].off + holes[i - 1].size == off, right = i < holes.size() && off + n == holes[i].off;
        if (left && right) { holes[i - 1].size += n + holes[i].size; holes.erase(holes.begin() + i); }
        else if (left) holes[i - 1].size += n;
        else if (right) { holes[i].off = off; holes[i].size += n; }
        else holes.insert(holes.begin() + i, {off, n});
        return true;
    }
    std::vector<Hole> snapshot() const { return holes; }
    double fragmentation() const { size_t tot = 0, mx = 0; for (auto& h : holes) { tot += h.size; mx = std::max(mx, h.size); } return tot ? 1.0 - double(mx) / tot : 0; }
};

class IndexedFreeList {
    std::map<size_t, size_t> byOff; std::set<std::pair<size_t, size_t>> bySize;
    void put(size_t off, size_t size) { byOff[off] = size; bySize.insert({size, off}); }
    void drop(std::map<size_t, size_t>::iterator it) { bySize.erase({it->second, it->first}); byOff.erase(it); }
public:
    explicit IndexedFreeList(size_t total) { put(0, total); }
    long alloc(size_t n, Policy p) {
        if (n == 0) return -1;
        std::map<size_t, size_t>::iterator it = byOff.end();
        if (p == FIRST) { for (auto j = byOff.begin(); j != byOff.end(); ++j) if (j->second >= n) { it = j; break; } }
        else if (p == BEST) { auto k = bySize.lower_bound({n, 0}); if (k != bySize.end()) it = byOff.find(k->second); }                // 크기 >= n 중 가장 작은 것, 같으면 낮은 주소
        else { if (!bySize.empty() && bySize.rbegin()->first >= n) { auto k = bySize.lower_bound({bySize.rbegin()->first, 0}); it = byOff.find(k->second); } }   // 가장 큰 크기 중 낮은 주소
        if (it == byOff.end()) return -1;
        size_t off = it->first, size = it->second; drop(it); if (size > n) put(off + n, size - n);
        return (long)off;
    }
    bool release(size_t off, size_t n, size_t total) {
        if (n == 0 || off + n > total) return false;
        auto next = byOff.lower_bound(off);
        if (next != byOff.begin()) { auto prev = std::prev(next); if (prev->first + prev->second > off) return false; }
        if (next != byOff.end() && off + n > next->first) return false;
        size_t start = off, size = n;
        if (next != byOff.begin()) { auto prev = std::prev(next); if (prev->first + prev->second == off) { start = prev->first; size += prev->second; drop(prev); } }
        if (next != byOff.end() && off + n == next->first) { size += next->second; drop(next); }
        put(start, size); return true;
    }
    std::vector<Hole> snapshot() const { std::vector<Hole> v; for (auto& kv : byOff) v.push_back({kv.first, kv.second}); return v; }
    bool consistent() const { if (byOff.size() != bySize.size()) return false; for (auto& kv : byOff) if (!bySize.count({kv.second, kv.first})) return false; return true; }
};

class BitmapOracle {
    std::vector<char> used;
public:
    explicit BitmapOracle(size_t total) : used(total, 0) {}
    std::vector<Hole> holes() const {                                                    // 매번 바이트 표에서 극대 빈 구간을 새로 구한다
        std::vector<Hole> v; for (size_t i = 0; i < used.size();) { if (used[i]) { ++i; continue; } size_t j = i; while (j < used.size() && !used[j]) ++j; v.push_back({i, j - i}); i = j; }
        return v;
    }
    long alloc(size_t n, Policy p) {
        if (n == 0) return -1;
        long best = -1; size_t bestLen = 0;
        for (const Hole& h : holes()) {
            if (h.size < n) continue;
            bool better = best < 0 || (p == BEST && h.size < bestLen) || (p == WORST && h.size > bestLen);
            if (better) { best = (long)h.off; bestLen = h.size; if (p == FIRST) break; }
        }
        if (best >= 0) for (size_t i = 0; i < n; ++i) used[best + i] = 1;
        return best;
    }
    bool release(size_t off, size_t n) {                                                // 구간 전체가 사용 중일 때만 유효
        if (n == 0 || off + n > used.size()) return false;
        for (size_t i = 0; i < n; ++i) if (!used[off + i]) return false;
        for (size_t i = 0; i < n; ++i) { used[off + i] = 0; }
        return true;
    }
    size_t freeBytes() const { size_t f = 0; for (char c : used) f += !c; return f; }
};

bool same(const std::vector<Hole>& a, const std::vector<Hole>& b) {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) { if (a[i].off != b[i].off || a[i].size != b[i].size) return false; }
    return true;
}

int main() {
    // 원래 예: 구멍 {0,100} {150,30} {300,60} {500,200}
    auto make = [] { return ListFreeList(std::vector<Hole>{{0, 100}, {150, 30}, {300, 60}, {500, 200}}); };
    { ListFreeList a = make(), b = make(), c = make();
      assert(a.alloc(25, FIRST) == 0 && b.alloc(25, BEST) == 150 && c.alloc(25, WORST) == 500);
      assert(b.holes[1].size == 5 && a.alloc(1000, FIRST) == -1);                                 // best-fit 이 남긴 5 짜리 조각, 총 390 이어도 연속 1000 은 없다
      ListFreeList d(std::vector<Hole>{{0, 10}}); assert(d.release(10, 10, 100) && d.release(30, 10, 100) && d.holes.size() == 2 && d.holes[0].size == 20);
      assert(d.release(20, 10, 100) && d.holes.size() == 1 && d.holes[0].size == 40);
      assert(!d.release(5, 3, 100) && !d.release(35, 10, 100) && !d.release(95, 10, 100) && !d.release(50, 0, 100));   // 겹침, 범위 밖, 크기 0
      assert(make().fragmentation() > 0.4); }

    // 세 구현 차분 시험
    const size_t TOTAL = 1024; long failedWithSpace[3] = {0, 0, 0}, okAllocs[3] = {0, 0, 0}, badRelease = 0;
    for (int pol = 0; pol < 3; ++pol) {
        Policy p = (Policy)pol; ListFreeList L(TOTAL); IndexedFreeList I(TOTAL); BitmapOracle O(TOTAL);
        std::mt19937 rng(900 + pol); std::vector<Hole> live;
        for (int step = 0; step < 20000; ++step) {
            int r = (int)(rng() % 100);
            if (r < 52 || live.empty()) {
                size_t n = (rng() % 4 == 0) ? 1 + rng() % 120 : 1 + rng() % 24;
                long a = L.alloc(n, p), b = I.alloc(n, p), c = O.alloc(n, p); assert(a == b && b == c);
                if (a >= 0) { live.push_back({(size_t)a, n}); ++okAllocs[pol]; }
                else if (O.freeBytes() >= n) ++failedWithSpace[pol];                            // 자유 공간 합은 충분한데 연속 구간이 없어서 실패 (외부 단편화)
            } else if (r < 94) {
                size_t k = rng() % live.size(); Hole h = live[k]; live.erase(live.begin() + k);
                bool a = L.release(h.off, h.size, TOTAL), b = I.release(h.off, h.size, TOTAL), c = O.release(h.off, h.size); assert(a && b && c);
            } else {                                                                              // 잘못된 해제: 아무 구간이나
                size_t off = rng() % TOTAL, n = 1 + rng() % 30;
                bool c = O.release(off, n);
                if (c) {                                                                          // 우연히 사용 중인 구간이었다면 실제 해제가 일어난 것이니 모형을 맞춘다
                    bool a = L.release(off, n, TOTAL), b = I.release(off, n, TOTAL); assert(a && b);
                    std::vector<Hole> rest;                                                       // 살아 있는 블록 목록에서 해당 구간을 도려낸다
                    for (const Hole& h : live) { size_t lo = h.off, hi = h.off + h.size; if (hi <= off || lo >= off + n) { rest.push_back(h); continue; }
                        if (lo < off) { rest.push_back({lo, off - lo}); }
                        if (hi > off + n) { rest.push_back({off + n, hi - off - n}); } }
                    live.swap(rest);
                } else { bool a = L.release(off, n, TOTAL), b = I.release(off, n, TOTAL); assert(!a && !b); ++badRelease; }
            }
            if (step % 50 == 0) {
                std::vector<Hole> hl = L.snapshot(), hi = I.snapshot(), ho = O.holes();
                assert(same(hl, ho) && same(hi, ho) && I.consistent());                           // 세 구현의 구멍 목록이 완전히 같다 (비트맵 기준이면 정의상 병합돼 있다)
                size_t sum = 0; for (size_t i = 0; i < hl.size(); ++i) { assert(hl[i].size > 0); if (i) assert(hl[i - 1].off + hl[i - 1].size < hl[i].off); sum += hl[i].size; }
                assert(sum == O.freeBytes());
            }
        }
        for (const Hole& h : live) assert(L.release(h.off, h.size, TOTAL) && I.release(h.off, h.size, TOTAL));
        assert(L.holes.size() == 1 && L.holes[0].off == 0 && L.holes[0].size == TOTAL && I.snapshot().size() == 1);        // 모두 돌려주면 구멍 하나
    }
    assert(okAllocs[0] > 5000 && failedWithSpace[0] + failedWithSpace[1] + failedWithSpace[2] > 100 && badRelease > 100);
    std::cout << "FreeList verified: list == indexed == bitmap oracle; allocs ok first/best/worst = " << okAllocs[0] << "/" << okAllocs[1] << "/" << okAllocs[2]
              << ", fragmentation failures " << failedWithSpace[0] << "/" << failedWithSpace[1] << "/" << failedWithSpace[2] << std::endl;
    return 0;
}
// Time Complexity: 벡터 구현 할당 O(구멍 수)·해제 O(구멍 수), 인덱스 구현 best/worst-fit 할당 O(log 구멍 수)·해제 O(log 구멍 수) (first-fit 은 선형)
// Space Complexity: O(구멍 수)
```
## SlabAllocator()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <new>
#include <random>
#include <set>
#include <vector>

// 슬랩 할당기(리눅스 커널): 한 종류의 객체만 담는 "슬랩(고정 크기 페이지)" 여러 개를 관리한다.  슬랩은 부분(partial)·가득(full)·빈(empty) 상태로 나뉘고
// 할당은 부분 슬랩에서 우선한다 -> 슬랩을 거의 가득 채워 쓰고 빈 슬랩은 반환하므로 단편화가 적다.  객체를 미리 초기화해 두면 생성 비용도 줄인다
// 이 구현은 커널 방식을 따른다:  ① 슬랩은 4096 바이트로 정렬된 한 덩어리이고 머리말(Slab, 40B) + 빈 객체 번호표(bufctl, 객체 밖에 둔다) + 객체들로 구성
//  ② 해제할 때 포인터의 아래 12 비트를 지우면 슬랩 머리말 주소가 나온다 -> 슬랩을 찾는 탐색이 없어 해제 O(1)  ③ 머리말의 리스트 3 개(partial/full/empty)는 이중 연결 리스트라 상태 이동도 O(1)
//  ④ 슬랩 색칠(cache coloring): 새 슬랩마다 첫 객체의 시작 위치를 16 바이트씩 밀어 서로 다른 슬랩의 같은 번호 객체가 캐시 세트 하나에 몰리지 않게 한다
//  ⑤ 생성자는 슬랩을 만들 때 객체마다 한 번, 소멸자는 슬랩을 반환할 때 한 번 호출 — 객체를 돌려줄 때는 "생성된 상태"로 복원해야 한다  ⑥ 빈 슬랩은 keepEmpty 개까지만 보유
// 검증: 5 가지 객체 크기에서 무작위 할당/해제 40 000 번 — 객체 무늬 격리, 객체 간격·경계 정렬, 슬랩 수 == 모형, 부분 슬랩이 있으면 새 슬랩을 만들지 않음, 불변식(리스트 소속·번호표 사슬 길이·사용 수 합),
//        생성자 호출 수 == 슬랩 수 × 슬랩당 객체 수 (소멸자도 같음), 색깔이 0, 1, 2, ... 순환, 이중 해제·경계 밖·다른 캐시의 포인터 거절
class SlabCache {
public:
    static const size_t SLAB_SIZE = 4096;
private:
    enum { PARTIAL, FULL, EMPTY, NOLIST = 9 };
    static const uint16_t ALLOCATED = 0xFFFE, END = 0xFFFD;
    struct Slab { Slab *prev, *next; SlabCache* owner; uint16_t inuse, freeHead, color, total; uint8_t state; };      // 32 바이트 머리말
    Slab* lists[3] = {nullptr, nullptr, nullptr}; size_t counts[3] = {0, 0, 0};
    size_t objSize, perSlab, baseOff, colors, nextColor = 0, keepEmpty; void (*ctor)(void*); void (*dtor)(void*);
    std::set<Slab*> known;                                               // 검증용: 우리가 만든 슬랩 (해제 시 임의 포인터의 머리말을 읽지 않기 위해)
    static uint16_t* bufctl(Slab* s) { return reinterpret_cast<uint16_t*>(s + 1); }
    unsigned char* objBase(Slab* s) const { return reinterpret_cast<unsigned char*>(s) + baseOff + (size_t)s->color * 16; }
    void unlink(Slab* s) { if (s->prev) s->prev->next = s->next; else lists[s->state] = s->next; if (s->next) s->next->prev = s->prev; --counts[s->state]; s->prev = s->next = nullptr; s->state = NOLIST; }
    void linkTo(Slab* s, int st) { s->state = (uint8_t)st; s->prev = nullptr; s->next = lists[st]; if (lists[st]) lists[st]->prev = s; lists[st] = s; ++counts[st]; }
    Slab* newSlab() {
        void* raw = ::operator new(SLAB_SIZE, std::align_val_t(SLAB_SIZE));
        Slab* s = new (raw) Slab{nullptr, nullptr, this, 0, 0, (uint16_t)nextColor, (uint16_t)perSlab, NOLIST};
        nextColor = (nextColor + 1) % colors;
        for (size_t i = 0; i < perSlab; ++i) bufctl(s)[i] = (uint16_t)(i + 1 == perSlab ? END : i + 1);
        if (ctor) for (size_t i = 0; i < perSlab; ++i) { ctor(objBase(s) + i * objSize); ++ctorCalls; }
        known.insert(s); linkTo(s, EMPTY); ++created; return s;
    }
    void destroySlab(Slab* s) {
        if (s->state != NOLIST) { unlink(s); }
        known.erase(s);
        if (dtor) for (size_t i = 0; i < perSlab; ++i) { dtor(objBase(s) + i * objSize); ++dtorCalls; }
        ::operator delete(s, std::align_val_t(SLAB_SIZE)); ++destroyed;
    }
public:
    long created = 0, destroyed = 0, ctorCalls = 0, dtorCalls = 0;
    SlabCache(size_t size, void (*c)(void*) = nullptr, void (*d)(void*) = nullptr, size_t keep = 1) : objSize((size + 7) & ~size_t(7)), keepEmpty(keep), ctor(c), dtor(d) {
        size_t n = (SLAB_SIZE - sizeof(Slab)) / (objSize + 2);
        for (;; --n) { baseOff = (sizeof(Slab) + 2 * n + 7) & ~size_t(7); if (baseOff + n * objSize <= SLAB_SIZE) break; }
        perSlab = n; colors = (SLAB_SIZE - baseOff - n * objSize) / 16 + 1; assert(perSlab >= 1 && perSlab < END);
    }
    SlabCache(const SlabCache&) = delete; SlabCache& operator=(const SlabCache&) = delete;
    ~SlabCache() { while (!known.empty()) destroySlab(*known.begin()); }
    void* alloc() {
        Slab* s = lists[PARTIAL] ? lists[PARTIAL] : lists[EMPTY] ? lists[EMPTY] : newSlab();                // 부분 -> 빈 -> 새 슬랩 순서
        uint16_t idx = s->freeHead; s->freeHead = bufctl(s)[idx]; bufctl(s)[idx] = ALLOCATED; ++s->inuse;
        unlink(s); linkTo(s, s->inuse == s->total ? FULL : PARTIAL); ++live;
        return objBase(s) + (size_t)idx * objSize;
    }
    bool release(void* p) {
        Slab* s = reinterpret_cast<Slab*>(reinterpret_cast<uintptr_t>(p) & ~(uintptr_t)(SLAB_SIZE - 1));    // 아래 12 비트를 지우면 슬랩
        if (!known.count(s)) return false;
        ptrdiff_t off = (unsigned char*)p - objBase(s); if (off < 0 || (size_t)off % objSize || (size_t)off / objSize >= perSlab) return false;
        size_t idx = (size_t)off / objSize; if (bufctl(s)[idx] != ALLOCATED) return false;                  // 이중 해제
        bufctl(s)[idx] = s->freeHead; s->freeHead = (uint16_t)idx; --s->inuse; --live;
        unlink(s);
        if (s->inuse == 0) { if (counts[EMPTY] >= keepEmpty) destroySlab(s); else linkTo(s, EMPTY); } else linkTo(s, PARTIAL);
        return true;
    }
    void shrink() { while (lists[EMPTY]) destroySlab(lists[EMPTY]); }
    long live = 0;
    size_t slabCount() const { return known.size(); } size_t perSlabObjects() const { return perSlab; } size_t colorCount() const { return colors; } size_t objectSize() const { return objSize; }
    size_t count(int list) const { return counts[list]; }
    size_t slabIdOf(const void* p) const { return reinterpret_cast<uintptr_t>(p) / SLAB_SIZE; }
    unsigned colorOfSlabAt(const void* p) const { Slab* s = reinterpret_cast<Slab*>(reinterpret_cast<uintptr_t>(p) & ~(uintptr_t)(SLAB_SIZE - 1)); return s->color; }
    void checkInvariants() const {                                                                         // 리스트 소속, 번호표 사슬, 사용 수
        size_t seen = 0; long inuseSum = 0;
        for (int st = 0; st < 3; ++st) {
            size_t c = 0; Slab* prev = nullptr;
            for (Slab* s = lists[st]; s; prev = s, s = s->next) {
                ++c; assert(s->prev == prev && s->state == st && s->owner == this && known.count(s) && (uintptr_t)s % SLAB_SIZE == 0);
                assert((st == EMPTY) == (s->inuse == 0) && (st == FULL) == (s->inuse == s->total));
                size_t chain = 0, alloc = 0; for (uint16_t i = s->freeHead; i != END; i = bufctl(s)[i]) { assert(i < s->total && bufctl(s)[i] != ALLOCATED && ++chain <= s->total); }
                for (size_t i = 0; i < s->total; ++i) alloc += bufctl(s)[i] == ALLOCATED;
                assert(chain == (size_t)(s->total - s->inuse) && alloc == s->inuse); inuseSum += s->inuse;
                assert(objBase(s) + perSlab * objSize <= (unsigned char*)s + SLAB_SIZE);                      // 객체들이 슬랩 안에 들어간다
            }
            assert(c == counts[st]); seen += c;
        }
        assert(seen == known.size() && inuseSum == live && counts[EMPTY] <= keepEmpty);
    }
};

static unsigned char CANARY = 0xAB;
void canaryCtor(void* p) { std::memset(p, CANARY, 1); }              // 생성된 상태 = 첫 바이트가 표식 (객체 크기는 캐시가 안다)
long dtorBad = 0; size_t gObjSize = 0;
void canaryDtor(void* p) { if (*(unsigned char*)p != CANARY) ++dtorBad; }

int main() {
    // 원래 예: 128 바이트 객체
    {   SlabCache cache(128); std::vector<void*> objs; assert(cache.perSlabObjects() == 31);
        for (int i = 0; i < 70; i++) objs.push_back(cache.alloc());
        assert(cache.slabCount() == 3 && cache.created == 3);                                            // 70 개 -> 슬랩 3 개 (31 + 31 + 8)
        for (int i = 31; i < 62; i++) assert(cache.release(objs[i]));                                    // 가운데 슬랩을 통째로 반환
        assert(cache.slabCount() == 3 && cache.count(2) == 1);                                           // 빈 슬랩은 keepEmpty = 1 개까지 보유
        void* again = cache.alloc(); assert(cache.slabIdOf(again) == cache.slabIdOf(objs[69]));          // 부분 슬랩(마지막 슬랩)을 먼저 사용
        for (int i = 0; i < 31; i++) { cache.release(objs[i]); }
        for (int i = 62; i < 70; i++) { cache.release(objs[i]); }
        assert(cache.release(again));
        assert(cache.slabCount() == 1 && cache.live == 0);                                               // 전부 반환하면 빈 슬랩 하나만 남는다
        cache.checkInvariants(); }
    // 색칠: 새 슬랩마다 시작 위치가 16 바이트씩 밀린다
    {   SlabCache c(40); assert(c.perSlabObjects() == 96 && c.colorCount() == 2); std::vector<void*> v; for (int i = 0; i < 96 * 7; ++i) v.push_back(c.alloc());
        std::map<size_t, unsigned> seen; for (void* p : v) seen[c.slabIdOf(p)] = c.colorOfSlabAt(p);
        unsigned cnt[2] = {0, 0}; assert(seen.size() == 7); for (auto& kv : seen) ++cnt[kv.second]; assert(cnt[0] == 4 && cnt[1] == 3);       // 슬랩 7 개 -> 색 0,1,0,1,0,1,0 (색이 2 가지: 남는 24 바이트 안에서 16 바이트씩)
        assert((unsigned char*)v[1] - (unsigned char*)v[0] == 40 && ((uintptr_t)v[96] & 4095) - ((uintptr_t)v[0] & 4095) == 16);          // 객체 간격 40, 다음 슬랩의 첫 객체는 16 바이트 뒤
        for (void* p : v) assert(c.release(p)); }
    // 잘못된 해제
    {   SlabCache a(64), b(64); void* p = a.alloc(); void* q = b.alloc(); int local = 0;
        assert(!a.release(q) && !a.release(&local) && !a.release((char*)p + 8) && !a.release((char*)p - 64) && !a.release(nullptr));      // 다른 캐시, 스택, 경계가 아님
        assert(a.release(p) && !a.release(p) && b.release(q)); a.checkInvariants(); }
    // 생성자·소멸자 개수와 무작위 시험
    for (int cfg = 0; cfg < 5; ++cfg) {
        size_t sizes[5] = {8, 24, 128, 600, 2000}; size_t sz = sizes[cfg]; CANARY = (unsigned char)(0xA0 + cfg); dtorBad = 0;
        std::mt19937 rng(5000 + cfg); long lastCtor, lastDtor;
        {   SlabCache cache(sz, canaryCtor, canaryDtor, cfg % 3); std::map<unsigned char*, unsigned char> live; std::set<size_t> slabsNow; long steps = 40000; long newSlabsWhilePartial = 0;
            for (long step = 0; step < steps; ++step) {
                bool doAlloc = live.empty() || rng() % 100 < (step % 16000 < 8000 ? 60u : 40u);
                if (doAlloc) {
                    bool hadPartial = cache.count(0) > 0; size_t slabsBefore = cache.slabCount();
                    unsigned char* p = (unsigned char*)cache.alloc(); assert(p && !live.count(p) && (uintptr_t)p % 8 == 0 && *p == CANARY);       // 생성된 상태로 나온다
                    if (hadPartial && cache.slabCount() != slabsBefore) ++newSlabsWhilePartial;                                                    // 부분 슬랩이 있으면 새 슬랩은 필요 없다
                    unsigned char tag = (unsigned char)(1 + rng() % 90); std::fill(p, p + cache.objectSize(), tag); live[p] = tag;
                } else {
                    auto it = live.begin(); std::advance(it, rng() % live.size()); unsigned char* p = it->first;
                    for (size_t i = 0; i < cache.objectSize(); ++i) assert(p[i] == it->second);                                                    // 다른 객체·번호표가 이 객체를 덮어쓰지 않았다
                    *p = CANARY; for (size_t i = 1; i < cache.objectSize(); ++i) p[i] = 0;                                                         // 생성된 상태로 복원해서 반환
                    assert(cache.release(p)); live.erase(it);
                }
                if (step % 400 == 0) { cache.checkInvariants(); assert(cache.live == (long)live.size()); }
            }
            cache.checkInvariants(); assert(newSlabsWhilePartial == 0);
            size_t per = cache.perSlabObjects(); assert(cache.ctorCalls == cache.created * (long)per && cache.dtorCalls == cache.destroyed * (long)per);
            std::set<size_t> distinctSlabs; for (auto& kv : live) distinctSlabs.insert(cache.slabIdOf(kv.first)); assert(distinctSlabs.size() <= cache.slabCount() && cache.slabCount() <= distinctSlabs.size() + (size_t)(cfg % 3));      // 객체가 있는 슬랩 + 빈 슬랩(keepEmpty 이하)
            for (auto& kv : live) { unsigned char* p = kv.first; for (size_t i = 0; i < cache.objectSize(); ++i) assert(p[i] == kv.second); *p = CANARY; for (size_t i = 1; i < cache.objectSize(); ++i) p[i] = 0; assert(cache.release(p)); }
            cache.checkInvariants(); assert(cache.live == 0 && cache.slabCount() <= (size_t)(cfg % 3) && cache.count(0) == 0 && cache.count(1) == 0);   // 모두 돌려주면 빈 슬랩만 keepEmpty 개
            if (cfg % 3 == 0) assert(cache.slabCount() == 0);
            cache.shrink(); assert(cache.slabCount() == 0); lastCtor = cache.ctorCalls; lastDtor = cache.dtorCalls;
        }
        assert(lastCtor == lastDtor && dtorBad == 0 && lastCtor > 0);
    }
    std::cout << "SlabAllocator verified: header at address & ~4095, O(1) release, invariants hold over 5 object sizes x 40000 ops, ctor/dtor counts match slab counts." << std::endl;
    return 0;
}
// Time Complexity: 할당·해제 O(1) (슬랩 머리말은 주소 마스크로 찾고, 리스트 이동은 이중 연결 리스트)
// Space Complexity: O(슬랩 수 · 4096)
```
## BuddyAllocator()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 버디 할당기(리눅스 페이지 할당기): 메모리를 2의 거듭제곱 크기 블록으로 관리한다.  요청은 가장 가까운 큰 2의 거듭제곱으로 올리고(내부 단편화),
// 큰 블록을 반으로 쪼개 쓰고, 해제할 때 "버디"(같은 부모에서 나온 짝, 주소가 offset ^ size)가 비어 있으면 합친다.  병합이 빠르고 외부 단편화에 강하다
// 검증 ① 작은 힙(최소 16B, 128B 까지, 차수 0..3)에서 할당/해제로 닿을 수 있는 모든 상태를 전수 탐색: 그 수는 "이진 트리의 반사슬 개수" a(h) = 1 + a(h-1)² = 677 이어야 하고,
//        모든 상태에서 (a) 빈 블록들이 빈 공간의 "유일한 극대 분해"와 같고(완전 병합) (b) 모든 차수 k 에 대해 "정렬된 빈 구간이 있으면 할당이 성공하고 없으면 실패" (c) 블록은 자기 크기에 정렬
//      ② 큰 힙(16 B ~ 16 KB) 무작위 시험 40 000 번: 실제 메모리에 무늬를 써서 겹침이 없음을 확인, 내부 단편화 < 50% (최소 블록 초과 요청), 잘못된/이중 해제 거절
class Buddy {
    int maxOrder; size_t minBlock; std::vector<std::set<size_t>> freeLists; std::map<size_t, int> allocated;
public:
    Buddy(size_t minB, int maxO) : maxOrder(maxO), minBlock(minB), freeLists(maxO + 1) { freeLists[maxO].insert(0); }
    size_t sizeOf(int order) const { return minBlock << order; }
    int orderFor(size_t n) const { int k = 0; while (k <= maxOrder && sizeOf(k) < n) k++; return k; }     // maxOrder 보다 크면 불가능
    long alloc(size_t n, int* orderOut = nullptr) {
        if (n == 0) return -1;
        int k = orderFor(n); if (k > maxOrder) return -1;
        int j = k; while (j <= maxOrder && freeLists[j].empty()) j++;                                       // 쓸 수 있는 가장 작은 큰 블록
        if (j > maxOrder) return -1;
        size_t off = *freeLists[j].begin(); freeLists[j].erase(freeLists[j].begin());
        while (j > k) { j--; freeLists[j].insert(off + sizeOf(j)); }                                         // 반으로 쪼개고 오른쪽 절반은 빈 블록으로
        allocated[off] = k; if (orderOut) *orderOut = k; return (long)off;
    }
    bool release(size_t off) {
        auto it = allocated.find(off); if (it == allocated.end()) return false;                             // 할당된 적 없거나 이미 해제됨
        int order = it->second; allocated.erase(it);
        while (order < maxOrder) {
            size_t buddy = off ^ sizeOf(order);                                                             // 버디의 주소는 XOR 한 번
            auto f = freeLists[order].find(buddy); if (f == freeLists[order].end()) break;
            freeLists[order].erase(f); off = std::min(off, buddy); order++;                                  // 합쳐서 한 단계 위로
        }
        freeLists[order].insert(off); return true;
    }
    size_t freeBlocks(int order) const { return freeLists[order].size(); }
    const std::set<size_t>& list(int order) const { return freeLists[order]; }
    const std::map<size_t, int>& blocks() const { return allocated; }
    int orders() const { return maxOrder; } size_t unit() const { return minBlock; } size_t heapSize() const { return sizeOf(maxOrder); }
};

// 독립 기준: 최소 블록 단위 사용표에서 극대 정렬 빈 블록 분해를 재귀로 구한다
void decompose(const std::vector<char>& used, size_t unitOff, int order, std::vector<std::set<size_t>>& out, size_t unit) {
    size_t len = (size_t)1 << order; bool allFree = true; for (size_t i = 0; i < len; ++i) if (used[unitOff + i]) { allFree = false; break; }
    if (allFree) { out[order].insert(unitOff * unit); return; }
    if (order == 0) return;
    decompose(used, unitOff, order - 1, out, unit); decompose(used, unitOff + len / 2, order - 1, out, unit);
}
bool alignedFreeExists(const std::vector<char>& used, int order) {                                      // 크기 2^order 로 정렬된 완전히 빈 구간이 있는가
    size_t len = (size_t)1 << order; for (size_t s = 0; s + len <= used.size(); s += len) { bool f = true; for (size_t i = 0; i < len && f; ++i) f = !used[s + i]; if (f) return true; } return false;
}
void checkInvariants(const Buddy& b) {
    size_t units = (size_t)1 << b.orders(); std::vector<char> used(units, 0);
    for (auto& kv : b.blocks()) {
        size_t sz = b.sizeOf(kv.second); assert(kv.first % sz == 0 && kv.first + sz <= b.heapSize());                  // 크기에 정렬, 힙 안
        for (size_t i = 0; i < sz / b.unit(); ++i) { assert(!used[kv.first / b.unit() + i]); used[kv.first / b.unit() + i] = 1; }
    }
    std::vector<std::set<size_t>> want(b.orders() + 1); decompose(used, 0, b.orders(), want, b.unit());
    for (int k = 0; k <= b.orders(); ++k) assert(b.list(k) == want[k]);                                                // 빈 블록 집합 == 유일한 극대 분해 (곧 완전 병합 + 겹침 없음)
}

int main() {
    // 원래 예
    {   Buddy b(64, 4); int oa, ob, oc;
        long a = b.alloc(100, &oa); assert(a == 0 && oa == 1);                                  // 100B -> 128B 블록
        long c = b.alloc(100, &ob); assert(c == 128 && ob == 1);
        long d = b.alloc(300, &oc); assert(d == 512 && oc == 3);
        assert(b.freeBlocks(2) == 1 && b.freeBlocks(1) == 0);
        assert(b.release(a) && b.release(d) && b.freeBlocks(1) == 1);                            // c 가 남아 있어 a 는 버디와 합쳐지지 못함
        assert(b.release(c) && b.freeBlocks(4) == 1 && b.freeBlocks(0) + b.freeBlocks(1) + b.freeBlocks(2) + b.freeBlocks(3) == 0);
        assert(b.alloc(2000) == -1 && b.alloc(0) == -1 && !b.release(0) && !b.release(12345));
    }
    // ① 도달 가능한 모든 상태 전수 탐색 (최소 16B, 차수 0..3 = 8 칸)
    {   Buddy start(16, 3); std::set<std::vector<std::pair<size_t, int>>> seen; std::vector<Buddy> stack{start}; long transitions = 0;
        while (!stack.empty()) {
            Buddy cur = stack.back(); stack.pop_back();
            std::vector<std::pair<size_t, int>> key(cur.blocks().begin(), cur.blocks().end());
            if (!seen.insert(key).second) continue;
            checkInvariants(cur);
            std::vector<char> used(8, 0); for (auto& kv : cur.blocks()) for (size_t i = 0; i < ((size_t)1 << kv.second); ++i) used[kv.first / 16 + i] = 1;
            for (int k = 0; k <= 3; ++k) {                                                                                // 할당: 성공 <=> 정렬된 빈 구간이 존재
                Buddy nxt = cur; long r = nxt.alloc(16 << k); bool exists = alignedFreeExists(used, k);
                assert((r >= 0) == exists); ++transitions;
                if (r >= 0) { assert((size_t)r % (16 << k) == 0); stack.push_back(nxt); }
            }
            for (auto& kv : cur.blocks()) { Buddy nxt = cur; assert(nxt.release(kv.first)); stack.push_back(nxt); ++transitions; }
        }
        long a = 2; for (int h = 1; h <= 3; ++h) a = 1 + a * a;                                                              // a(3) = 677
        assert((long)seen.size() == a && a == 677 && transitions > 5000);
    }
    // ② 큰 힙 무작위 시험
    {   Buddy b(16, 10); std::vector<unsigned char> mem(b.heapSize(), 0); std::mt19937 rng(31); struct Live { size_t off, req; unsigned char tag; }; std::vector<Live> live;
        long okAllocs = 0, fails = 0, rejected = 0; double internalSum = 0, blockSum = 0;
        for (int step = 0; step < 40000; ++step) {
            int r = (int)(rng() % 100);
            if (r < 52 || live.empty()) {
                size_t n = (rng() % 8 == 0) ? 1 + rng() % 3000 : 1 + rng() % 200; int k;
                long off = b.alloc(n, &k);
                if (off < 0) { ++fails; continue; }
                size_t sz = b.sizeOf(k); assert(sz >= n && (n <= 16 || sz < 2 * n));                                            // 내부 단편화는 절반 미만 (최소 블록 초과 요청)
                unsigned char tag = (unsigned char)(1 + rng() % 250); std::fill(mem.begin() + off, mem.begin() + off + sz, tag);
                live.push_back({(size_t)off, n, tag}); ++okAllocs; internalSum += sz - n; blockSum += sz;
            } else if (r < 95) {
                size_t i = rng() % live.size(); Live l = live[i]; live[i] = live.back(); live.pop_back();
                size_t sz = b.sizeOf(b.blocks().at(l.off)); for (size_t j = 0; j < sz; ++j) assert(mem[l.off + j] == l.tag);     // 다른 블록이 내 블록을 덮어쓰지 않았다
                assert(b.release(l.off)); assert(!b.release(l.off)); ++rejected;                                               // 이중 해제 거절
            } else { size_t bogus = rng() % b.heapSize(); if (!b.blocks().count(bogus)) { assert(!b.release(bogus)); ++rejected; } }
            if (step % 200 == 0) checkInvariants(b);
        }
        checkInvariants(b);
        for (auto& l : live) assert(b.release(l.off));
        assert(b.freeBlocks(10) == 1 && b.blocks().empty() && okAllocs > 8000 && fails > 100 && rejected > 8000);          // 모두 돌려주면 1 개의 최대 블록
        std::cout << "BuddyAllocator verified: 677 reachable states checked, " << okAllocs << " random allocs, mean internal fragmentation " << (internalSum / blockSum) << std::endl;
    }
    return 0;
}
// Time Complexity: 할당·해제 O(차수) = O(log N) (집합 연산 포함 O(log N · log 블록 수))
// Space Complexity: O(블록 수)
```
## ArenaAllocator()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <new>
#include <random>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

// 아레나(범프) 할당기: 포인터 하나를 앞으로 밀기만 한다.  할당이 가장 빠르고(덧셈 한 번), 개별 해제는 없고 아레나 전체를 한 번에 비운다.
// 컴파일러의 AST, 요청 하나를 처리하는 동안의 임시 객체, 게임의 프레임별 메모리에 적합.  mark/rollback 으로 부분 되돌리기도 가능
// 이 구현: 덩어리(chunk)를 이어 붙이며 자라는 아레나 — 덩어리를 넘는 큰 요청은 전용 덩어리를 받고, reserved 상한을 넘으면 nullptr 를 돌려준다.
//  make<T> 는 소멸자가 필요한 타입만 소멸자 목록에 올려 두었다가 rollback/reset/소멸 때 "만든 순서의 역순"으로 호출하고, 생성자가 예외를 던지면 사용량을 되돌려 놓는다
// 검증: ① 한 덩어리 안에서 (크기, 정렬) 수열의 주소가 "직전 끝에서 정렬만큼만 올림"으로 정확히 결정  ② 덩어리 증설·큰 요청이 섞여도 구간이 서로 겹치지 않고 무늬가 보존  ③ 상한  ④ 소멸자 순서와
//        cross-chunk rollback(덩어리는 유지되고 재사용)  ⑤ 예외 시 되돌림  ⑥ 같은 무작위 식 트리를 아레나/힙(unique_ptr)에 각각 만들어 계산 결과와 노드 수가 같음
class Arena {
    struct Chunk { unsigned char* mem; size_t cap, top; };
    struct Dtor { void* obj; void (*fn)(void*); };
    std::vector<Chunk> chunks; std::vector<Dtor> dtors; size_t cur = 0, chunkSize, limit, reservedBytes = 0;
    void runDtors(size_t downTo) { while (dtors.size() > downTo) { Dtor d = dtors.back(); dtors.pop_back(); d.fn(d.obj); } }
public:
    struct Mark { size_t chunk, top, dtorCount; };
    explicit Arena(size_t chunk = 4096, size_t maxReserved = (size_t)-1) : chunkSize(chunk), limit(maxReserved) {}
    Arena(const Arena&) = delete; Arena& operator=(const Arena&) = delete;
    ~Arena() { runDtors(0); for (Chunk& c : chunks) delete[] c.mem; }
    void* alloc(size_t n, size_t align = alignof(std::max_align_t)) {
        assert(align && (align & (align - 1)) == 0); if (n == 0) n = 1;                                      // 크기 0 도 서로 다른 주소
        for (size_t i = cur; i < chunks.size(); ++i) {
            Chunk& c = chunks[i]; uintptr_t base = (uintptr_t)c.mem, a = (base + c.top + align - 1) & ~(uintptr_t)(align - 1);
            if (a - base + n <= c.cap) { c.top = a - base + n; cur = i; return (void*)a; }                     // 덧셈 한 번 + 비교 한 번
        }
        size_t cap = std::max(chunkSize, n + align); if (reservedBytes + cap > limit) return nullptr;
        chunks.push_back({new unsigned char[cap], cap, 0}); reservedBytes += cap; cur = chunks.size() - 1; return alloc(n, align);
    }
    template <class T, class... A> T* make(A&&... a) {
        Mark m = mark(); void* p = alloc(sizeof(T), alignof(T)); if (!p) return nullptr;
        T* obj; try { obj = new (p) T(std::forward<A>(a)...); } catch (...) { rollback(m); throw; }              // 생성 실패: 사용량도 되돌린다
        if (!std::is_trivially_destructible<T>::value) dtors.push_back({obj, [](void* q) { static_cast<T*>(q)->~T(); }});
        return obj;
    }
    char* dup(const std::string& s) { char* p = (char*)alloc(s.size() + 1, 1); if (p) std::memcpy(p, s.c_str(), s.size() + 1); return p; }
    Mark mark() const { return {chunks.empty() ? 0 : cur, chunks.empty() ? 0 : chunks[cur].top, dtors.size()}; }
    void rollback(const Mark& m) {                                                                              // 표시 이후의 모든 객체를 만든 역순으로 소멸
        runDtors(m.dtorCount); if (chunks.empty()) return;
        for (size_t i = m.chunk + 1; i < chunks.size(); ++i) { chunks[i].top = 0; }
        chunks[m.chunk].top = m.top; cur = m.chunk;
    }
    void reset() { rollback({0, 0, 0}); }
    size_t used() const { size_t u = 0; for (const Chunk& c : chunks) u += c.top; return u; }
    size_t reserved() const { return reservedBytes; } size_t chunkCount() const { return chunks.size(); } size_t pendingDtors() const { return dtors.size(); }
};

std::vector<int> dlog;
struct Logged { int id; explicit Logged(int i) : id(i) {} ~Logged() { dlog.push_back(id); } };
struct Boom { Boom() { throw std::runtime_error("boom"); } };
struct Expr { int op; long val; Expr *l, *r; };                       // 0 상수, 1 +, 2 *, 3 -  (소멸자가 필요 없는 평범한 노드)
struct HExpr { int op; long val; std::unique_ptr<HExpr> l, r; };
long evalA(const Expr* e) { if (!e->op) return e->val; long a = evalA(e->l), b = evalA(e->r); return e->op == 1 ? a + b : e->op == 2 ? (a * b) % 1000003 : a - b; }
long evalH(const HExpr* e) { if (!e->op) return e->val; long a = evalH(e->l.get()), b = evalH(e->r.get()); return e->op == 1 ? a + b : e->op == 2 ? (a * b) % 1000003 : a - b; }
Expr* buildA(Arena& ar, std::mt19937& g, int depth, long& n) { ++n; if (depth == 0 || g() % 5 == 0) return ar.make<Expr>(Expr{0, (long)(g() % 100), nullptr, nullptr});
    int op = 1 + (int)(g() % 3); Expr* l = buildA(ar, g, depth - 1, n); Expr* r = buildA(ar, g, depth - 1, n); return ar.make<Expr>(Expr{op, 0, l, r}); }
std::unique_ptr<HExpr> buildH(std::mt19937& g, int depth, long& n) { ++n; if (depth == 0 || g() % 5 == 0) return std::unique_ptr<HExpr>(new HExpr{0, (long)(g() % 100), nullptr, nullptr});
    int op = 1 + (int)(g() % 3); auto l = buildH(g, depth - 1, n); auto r = buildH(g, depth - 1, n); return std::unique_ptr<HExpr>(new HExpr{op, 0, std::move(l), std::move(r)}); }

int main() {
    // 원래 예: 정렬과 rollback
    {   Arena a(1024); char* c = (char*)a.alloc(1, 1); double* d = (double*)a.alloc(sizeof(double), alignof(double));
        assert((uintptr_t)d % alignof(double) == 0 && (char*)d > c);
        Arena::Mark m = a.mark(); size_t u = a.used();
        int* tmp = a.make<int>(42); assert(*tmp == 42); std::string* s = a.make<std::string>("arena string"); assert(*s == "arena string" && a.pendingDtors() == 1);
        a.rollback(m); assert(a.used() == u && a.pendingDtors() == 0);                                       // string 의 소멸자도 호출되고 사용량이 되돌아온다
        a.reset(); assert(a.used() == 0 && a.alloc(1000) != nullptr && a.chunkCount() == 1); }
    // ① 한 덩어리 안: 주소가 "직전 끝에서 정렬만큼만 올림"
    {   Arena a(1 << 22); std::mt19937 rng(1); uintptr_t prevEnd = 0; long checked = 0;
        for (int i = 0; i < 20000; ++i) {
            size_t align = (size_t)1 << (rng() % 8), n = 1 + rng() % 100; uintptr_t p = (uintptr_t)a.alloc(n, align);
            assert(p % align == 0 && a.chunkCount() == 1);
            if (prevEnd) assert(p >= prevEnd && p - prevEnd < align);                                         // 정렬에 필요한 만큼만 띄운다
            prevEnd = p + n; ++checked;
        } }
    // ② 덩어리 증설·큰 요청: 겹침 없음
    {   Arena a(256); std::mt19937 rng(2); struct R { unsigned char* p; size_t n; unsigned char tag; }; std::vector<R> rs;
        for (int i = 0; i < 5000; ++i) { size_t n = (rng() % 20 == 0) ? 300 + rng() % 1500 : 1 + rng() % 90, align = (size_t)1 << (rng() % 7);
            unsigned char* p = (unsigned char*)a.alloc(n, align); assert(p && (uintptr_t)p % align == 0); unsigned char tag = (unsigned char)(1 + i % 250); std::fill(p, p + n, tag); rs.push_back({p, n, tag}); }
        std::vector<R> sorted = rs; std::sort(sorted.begin(), sorted.end(), [](const R& x, const R& y) { return x.p < y.p; });
        for (size_t i = 0; i + 1 < sorted.size(); ++i) assert(sorted[i].p + sorted[i].n <= sorted[i + 1].p);   // 모든 구간이 서로소
        for (const R& r : rs) for (size_t i = 0; i < r.n; ++i) assert(r.p[i] == r.tag);                         // 무늬 보존
        assert(a.chunkCount() > 20 && a.reserved() >= a.used()); }
    // ③ 상한
    {   Arena a(100, 1000); int got = 0; while (a.alloc(60, 1)) ++got; assert(got == 10 && a.reserved() <= 1000 && a.alloc(500) == nullptr); a.reset(); assert(a.alloc(60, 1) != nullptr); }
    // ④ 소멸자 순서와 cross-chunk rollback
    {   dlog.clear(); {   Arena a(24); for (int i = 0; i < 2; ++i) a.make<Logged>(i);
            Arena::Mark m = a.mark(); size_t reservedAtMark = a.reserved();
            for (int i = 2; i < 12; ++i) { a.make<Logged>(i); }
            a.make<int>(5); assert(a.chunkCount() > 1 && a.pendingDtors() == 12);       // 정수는 소멸자 목록에 안 올라간다
            size_t reservedPeak = a.reserved(); a.rollback(m); std::vector<int> want; for (int i = 11; i >= 2; --i) want.push_back(i); assert(dlog == want && a.pendingDtors() == 2);
            assert(a.reserved() == reservedPeak && reservedPeak > reservedAtMark);                                                         // 덩어리는 유지
            for (int i = 20; i < 30; ++i) { a.make<Logged>(i); }
            assert(a.reserved() == reservedPeak);                                          // 유지된 덩어리를 재사용: 새로 받지 않는다
            dlog.clear(); }
        std::vector<int> want; for (int i = 29; i >= 20; --i) want.push_back(i); want.push_back(1); want.push_back(0); assert(dlog == want); }        // 아레나가 사라지며 남은 객체를 역순 소멸
    // ⑤ 예외: 생성 실패하면 사용량이 그대로
    {   Arena a(256); a.make<Logged>(1); size_t u = a.used(), p = a.pendingDtors(); dlog.clear();
        try { a.make<Boom>(); assert(false); } catch (const std::runtime_error&) {}
        assert(a.used() == u && a.pendingDtors() == p && dlog.empty()); a.reset(); assert(dlog.size() == 1); }
    // ⑥ 식 트리: 아레나 vs 힙
    {   long nodesTotal = 0;
        for (int seed = 0; seed < 300; ++seed) {
            std::mt19937 g1(seed), g2(seed); long na = 0, nh = 0; Arena ar(1024);
            Expr* ea = buildA(ar, g1, 9, na); std::unique_ptr<HExpr> eh = buildH(g2, 9, nh);
            assert(na == nh && evalA(ea) == evalH(eh.get()) && ar.used() >= (size_t)na * sizeof(Expr)); nodesTotal += na;
            ar.reset(); assert(ar.used() == 0);                                                                // 전체를 한 번에 비운다
        }
        char buf[16]; Arena sa(64); const char* s1 = sa.dup("hello"); const char* s2 = sa.dup(std::string("arena")); assert(std::string(s1) == "hello" && std::string(s2) == "arena" && s1 + 6 == s2); (void)buf;
        std::cout << "ArenaAllocator verified: bump pointer matches the closed form, chunks never overlap, rollback runs destructors in reverse; " << nodesTotal << " tree nodes matched heap-built trees." << std::endl; }
    return 0;
}
// Time Complexity: 할당 O(1) (덩어리 증설 시 O(덩어리 크기)), rollback/reset O(되돌릴 객체 수 + 덩어리 수)
// Space Complexity: O(용량)
```
# Part 7. 가비지 컬렉션
## MarkSweep()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 마크-스윕: (1) 루트(스택·전역 변수)에서 닿는 객체를 모두 표시(mark)하고, (2) 힙 전체를 훑어 표시되지 않은 객체를 해제(sweep)한다.
// 순환 참조도 올바르게 회수하고, 객체를 옮기지 않아 포인터가 안정적이다.  단점: 힙 전체를 훑고 단편화가 생기며 수집 중 멈춤(stop-the-world)이 있다
// 이 구현은 워드 배열 위에서 진짜 힙처럼 만든다: 객체 = [헤더][참조 칸 n 개][데이터 칸], 헤더에 크기·참조 수·표시/빈 블록 비트.
//  할당은 자유 블록 리스트 first-fit(남는 조각이 2 워드 미만이면 통째로 준다), 스윕은 힙을 선형으로 걸으며 죽은 객체와 빈 블록을 이어 붙여(병합) 자유 리스트를 새로 만든다.
//  표시는 두 가지로 구현해 서로 맞춘다: ① 명시적 스택 (추가 메모리 O(깊이))  ② Schorr–Waite 포인터 역전 (추가 메모리 O(1): 내려갈 때 참조 칸에 부모를 적어 두고 올라올 때 복원)
// 검증: ① 임의 그래프(순환·공유·자기 참조 포함) 300 개에서 스택 표시 == 포인터 역전 표시 == BFS 기준, 역전 후 힙이 표시 비트만 빼고 비트까지 원래대로
//        ② 무작위 변경 프로그램 4 000 번(할당·참조 바꾸기·루트 버리기, 힙이 차면 GC 후 재시도)을 id 모형과 대조: 수집 뒤 살아 있는 id 집합 == 모형의 도달 가능 집합, 주소는 그대로, 참조·데이터 보존
//        ③ 불변식: 블록이 힙을 빈틈없이 덮고, 자유 리스트 == 힙 안의 빈 블록 전부(주소순), 스윕 뒤에는 이웃한 빈 블록이 없음  ④ 단편화: 총 자유 공간은 충분해도 연속 공간이 없어 실패하는 장면
const uint64_t MARK = 1ull << 63, FREE = 1ull << 62;
inline uint32_t sizeOf(uint64_t h) { return (uint32_t)(h & 0xFFFFFF); }
inline uint32_t nrefsOf(uint64_t h) { return (uint32_t)((h >> 24) & 0xFFFF); }
inline uint32_t cursorOf(uint64_t h) { return (uint32_t)((h >> 40) & 0xFFFF); }
const uint64_t CURSOR_MASK = 0xFFFFull << 40;

struct Heap {
    std::vector<uint64_t> mem; std::vector<uint32_t> roots; uint32_t freeHead = 1; long collections = 0;
    explicit Heap(uint32_t words) : mem(words + 1, 0) { mem[1] = FREE | words; mem[2] = 0; }
    void relink(uint32_t prev, uint32_t to) { if (prev) mem[prev + 1] = to; else freeHead = to; }
    uint64_t& ref(uint32_t b, uint32_t i) { return mem[b + 1 + i]; }
    uint64_t& data(uint32_t b, uint32_t j) { return mem[b + 1 + nrefsOf(mem[b]) + j]; }
    uint32_t dataWords(uint32_t b) const { return sizeOf(mem[b]) - 1 - nrefsOf(mem[b]); }
    uint32_t alloc(uint32_t nrefs, uint32_t dataN) {                                           // 실패하면 0
        uint32_t need = std::max<uint32_t>(2, 1 + nrefs + dataN), prev = 0;
        for (uint32_t b = freeHead; b; prev = b, b = (uint32_t)mem[b + 1]) {
            uint32_t sz = sizeOf(mem[b]); if (sz < need) continue;
            uint32_t next = (uint32_t)mem[b + 1], take = (sz - need >= 2) ? need : sz;
            if (take < sz) { uint32_t rest = b + take; mem[rest] = FREE | (sz - take); mem[rest + 1] = next; relink(prev, rest); } else relink(prev, next);
            mem[b] = (uint64_t)take | ((uint64_t)nrefs << 24); for (uint32_t i = 1; i < take; ++i) mem[b + i] = 0;
            return b;
        }
        return 0;
    }
    void markStack(const std::vector<uint32_t>& rs) {
        std::vector<uint32_t> st; for (uint32_t r : rs) { if (r) st.push_back(r); }
        while (!st.empty()) {
            uint32_t b = st.back(); st.pop_back(); if (mem[b] & MARK) continue;
            mem[b] |= MARK; for (uint32_t i = 0; i < nrefsOf(mem[b]); ++i) { uint32_t c = (uint32_t)ref(b, i); if (c && !(mem[c] & MARK)) st.push_back(c); }
        }
    }
    void markReversal(uint32_t root) {                                                           // Schorr–Waite: 스택 없이 참조 칸을 뒤집어 부모를 기억한다
        if (!root || (mem[root] & MARK)) return;
        uint32_t prev = 0, cur = root; mem[cur] |= MARK;
        for (;;) {
            uint32_t i = cursorOf(mem[cur]);
            if (i < nrefsOf(mem[cur])) {
                uint32_t child = (uint32_t)ref(cur, i);
                if (child && !(mem[child] & MARK)) { ref(cur, i) = prev; prev = cur; cur = child; mem[cur] |= MARK; }   // 내려간다: 지나온 칸에 부모를 적는다
                else mem[cur] += (1ull << 40);                                                                       // 다음 칸
            } else {
                mem[cur] &= ~CURSOR_MASK;                                                       // 이 객체 끝
                if (!prev) break;
                uint32_t p = prev, j = cursorOf(mem[p]);
                prev = (uint32_t)ref(p, j); ref(p, j) = cur; mem[p] += (1ull << 40); cur = p;   // 올라간다: 조부모를 복원하고 원래 자식 포인터를 되돌린다
            }
        }
    }
    void mark() { markStack(roots); }
    long sweep() {                                                                               // 죽은 객체와 빈 블록을 이어 붙이며 자유 리스트를 새로 만든다
        uint32_t b = 1, end = (uint32_t)mem.size(), runStart = 0, runLen = 0, lastFree = 0; long freed = 0; freeHead = 0;
        auto flush = [&]() { if (!runStart) return; mem[runStart] = FREE | runLen; mem[runStart + 1] = 0; if (lastFree) mem[lastFree + 1] = runStart; else freeHead = runStart; lastFree = runStart; runStart = 0; };
        while (b < end) {
            uint64_t h = mem[b]; uint32_t sz = sizeOf(h);
            if ((h & FREE) || !(h & MARK)) { if (!(h & FREE)) ++freed; if (!runStart) { runStart = b; runLen = 0; } runLen += sz; }
            else { mem[b] &= ~MARK; flush(); }
            b += sz;
        }
        flush(); return freed;
    }
    long collect() { ++collections; mark(); return sweep(); }
    // 검증용
    std::vector<std::pair<uint32_t, bool>> walk() const {                                       // (블록, 빈 블록인가) — 힙을 빈틈없이 덮어야 한다
        std::vector<std::pair<uint32_t, bool>> v; uint32_t b = 1;
        while (b < mem.size()) { assert(sizeOf(mem[b]) >= 2); v.push_back({b, (mem[b] & FREE) != 0}); b += sizeOf(mem[b]); }
        assert(b == mem.size()); return v;
    }
    void checkInvariants(bool afterSweep) const {
        auto w = walk(); std::vector<uint32_t> freeInHeap; for (auto& p : w) { if (p.second) freeInHeap.push_back(p.first); assert(!(mem[p.first] & MARK) && !(mem[p.first] & CURSOR_MASK)); }
        std::vector<uint32_t> inList; for (uint32_t b = freeHead; b; b = (uint32_t)mem[b + 1]) { assert(mem[b] & FREE); inList.push_back(b); assert(inList.size() <= w.size()); }
        assert(inList == freeInHeap);                                                           // 자유 리스트 == 힙 안의 빈 블록 전부, 주소순
        if (afterSweep) for (size_t i = 0; i + 1 < w.size(); ++i) assert(!(w[i].second && w[i + 1].second));   // 이웃한 빈 블록은 병합돼 있다
    }
    size_t liveObjects() const { size_t n = 0; for (auto& p : walk()) n += !p.second; return n; }
    uint32_t largestFree() const { uint32_t m = 0; for (uint32_t b = freeHead; b; b = (uint32_t)mem[b + 1]) m = std::max(m, sizeOf(mem[b])); return m; }
    uint32_t totalFree() const { uint32_t t = 0; for (uint32_t b = freeHead; b; b = (uint32_t)mem[b + 1]) t += sizeOf(mem[b]); return t; }
};

int main() {
    // 원래 예: a -> b -> c, d <-> e (순환 쓰레기)
    {   Heap h(200); uint32_t a = h.alloc(1, 1), b = h.alloc(1, 1), c = h.alloc(0, 1), d = h.alloc(1, 1), e = h.alloc(1, 1);
        h.roots = {a}; h.ref(a, 0) = b; h.ref(b, 0) = c; h.ref(d, 0) = e; h.ref(e, 0) = d;
        assert(h.liveObjects() == 5 && h.collect() == 2 && h.liveObjects() == 3);               // 순환 참조된 d, e 가 회수
        h.ref(b, 0) = 0; assert(h.collect() == 1 && h.liveObjects() == 2);
        uint32_t reused = h.alloc(0, 1); assert(reused == c || reused == d || reused == e || reused > e); h.checkInvariants(true); }

    // ① 임의 그래프에서 세 가지 표시가 같다
    std::mt19937 rng(11); long graphs = 0, markedTotal = 0;
    for (int g = 0; g < 300; ++g) {
        Heap h(6000); int n = 1 + (int)(rng() % 150); std::vector<uint32_t> objs;
        for (int i = 0; i < n; ++i) { uint32_t o = h.alloc(rng() % 6, 1 + rng() % 3); assert(o); objs.push_back(o); }
        for (uint32_t o : objs) for (uint32_t k = 0; k < nrefsOf(h.mem[o]); ++k) { if (rng() % 4) h.ref(o, k) = objs[rng() % objs.size()]; }   // 순환·공유·자기 참조 모두 가능
        std::vector<uint32_t> roots; int nr = (int)(rng() % 4); for (int i = 0; i < nr; ++i) roots.push_back(objs[rng() % objs.size()]);
        std::set<uint32_t> want; { std::vector<uint32_t> st(roots.begin(), roots.end()); while (!st.empty()) { uint32_t b = st.back(); st.pop_back(); if (!want.insert(b).second) continue;
            for (uint32_t k = 0; k < nrefsOf(h.mem[b]); ++k) { if (h.ref(b, k)) st.push_back((uint32_t)h.ref(b, k)); } } }                     // 독립 BFS 기준
        std::vector<uint64_t> snapshot = h.mem;
        h.markStack(roots); std::set<uint32_t> viaStack; for (auto& p : h.walk()) { if (h.mem[p.first] & MARK) viaStack.insert(p.first); }
        h.mem = snapshot; for (uint32_t r : roots) h.markReversal(r); std::set<uint32_t> viaReversal; for (auto& p : h.walk()) { if (h.mem[p.first] & MARK) viaReversal.insert(p.first); }
        assert(viaStack == want && viaReversal == want);
        std::vector<uint64_t> after = h.mem; for (auto& p : h.walk()) { after[p.first] &= ~MARK; }                    // 역전 표시는 표시 비트 말고는 아무것도 바꾸지 않는다 (비트 단위로 복원)
        assert(after == snapshot);
        ++graphs; markedTotal += (long)want.size();
    }

    // ② 무작위 변경 프로그램과 id 모형
    {   Heap h(1500); std::map<int, std::vector<int>> refs; std::map<int, uint32_t> addr; std::vector<int> roots; int nextId = 1; long ooms = 0, gcs = 0, allocs = 0, frees = 0;
        auto reachable = [&]() { std::set<int> seen; std::vector<int> st(roots.begin(), roots.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (!x || !seen.insert(x).second) continue; for (int c : refs[x]) st.push_back(c); } return seen; };
        auto syncRoots = [&]() { h.roots.clear(); for (int r : roots) h.roots.push_back(addr[r]); };
        auto verify = [&]() {
            std::set<int> reach = reachable(); std::set<int> inHeap;
            for (auto& p : h.walk()) { if (p.second) continue; uint32_t b = p.first; int id = (int)h.data(b, 0); assert(inHeap.insert(id).second && addr.count(id) && addr[id] == b);
                for (uint32_t k = 0; k < nrefsOf(h.mem[b]); ++k) { uint32_t c = (uint32_t)h.ref(b, k); assert((c ? (int)h.data(c, 0) : 0) == refs[id][k]); }
                for (uint32_t j = 1; j < h.dataWords(b); ++j) { assert(h.data(b, j) == (uint64_t)id * 2654435761u + j); } }
            assert(inHeap == reach);                                                              // 수집 뒤 살아 있는 id == 도달 가능 id
            for (auto it = refs.begin(); it != refs.end();) { if (!reach.count(it->first)) { addr.erase(it->first); it = refs.erase(it); } else ++it; }
        };
        for (int step = 0; step < 4000; ++step) {
            int op = (int)(rng() % 100); std::set<int> reach = reachable(); std::vector<int> rl(reach.begin(), reach.end());
            if (op < 45 || rl.empty()) {
                uint32_t nr = rng() % 4, nd = 1 + rng() % 5; uint32_t b = h.alloc(nr, nd);
                if (!b) { syncRoots(); h.collect(); ++gcs; verify(); h.checkInvariants(true); b = h.alloc(nr, nd); }
                if (!b) { ++ooms; continue; }
                ++allocs; int id = nextId++; h.data(b, 0) = (uint64_t)id; for (uint32_t j = 1; j < h.dataWords(b); ++j) { h.data(b, j) = (uint64_t)id * 2654435761u + j; }
                addr[id] = b; refs[id] = std::vector<int>(nr, 0);
                int how = (int)(rng() % 10);
                if (how < 3 && roots.size() < 5) { roots.push_back(id); }
                else if (how < 8 && !rl.empty()) { int host = rl[rng() % rl.size()]; if (!refs[host].empty()) { uint32_t k = rng() % refs[host].size(); refs[host][k] = id; h.ref(addr[host], k) = b; } }   // 아니면 바로 쓰레기
            } else if (op < 85) {
                int host = rl[rng() % rl.size()]; if (refs[host].empty()) continue;
                uint32_t k = rng() % refs[host].size(); int tgt = (rng() % 5 == 0) ? 0 : rl[rng() % rl.size()]; refs[host][k] = tgt; h.ref(addr[host], k) = tgt ? addr[tgt] : 0;
            } else if (op < 92) {
                if (!roots.empty()) { roots.erase(roots.begin() + rng() % roots.size()); }
            } else if (op < 97) {
                if (roots.size() < 5) roots.push_back(rl[rng() % rl.size()]);
            } else { syncRoots(); frees += h.collect(); ++gcs; verify(); h.checkInvariants(true); }
            syncRoots();
        }
        syncRoots(); frees += h.collect(); verify(); h.checkInvariants(true);
        assert(gcs > 50 && allocs > 1500 && frees > 500);
        std::cout << "MarkSweep verified: " << graphs << " random graphs (" << markedTotal << " marked, stack == pointer reversal == BFS), " << gcs << " collections, " << allocs << " allocations, " << frees << " objects swept, " << ooms << " out-of-memory." << std::endl; }

    // ④ 단편화: 총 자유 공간은 충분한데 연속 공간이 없어서 실패
    {   auto filled = [](std::vector<uint32_t>& os) { Heap h(40 * 4); for (int i = 0; i < 40; ++i) { uint32_t o = h.alloc(0, 3); assert(o); os.push_back(o); } assert(h.alloc(0, 3) == 0); return h; };
        std::vector<uint32_t> os; Heap h = filled(os);                                              // 4 워드짜리 40 개로 가득 채운다
        h.roots.clear(); for (int i = 1; i < 40; i += 2) { h.roots.push_back(os[i]); }              // 홀수 번째만 살린다
        h.collect(); h.checkInvariants(true);
        assert(h.totalFree() == 20 * 4 && h.largestFree() == 4 && h.alloc(0, 7) == 0);              // 80 워드가 비었지만 8 워드 연속 공간은 없다 (외부 단편화)
        std::vector<uint32_t> os2; Heap g = filled(os2);
        g.roots.clear(); for (int i = 0; i < 20; ++i) { g.roots.push_back(os2[i]); }                // 앞쪽 절반만 살린다
        g.collect(); g.checkInvariants(true); assert(g.largestFree() == 80 && g.alloc(0, 7) != 0);   // 인접한 죽은 객체가 병합돼 큰 요청이 들어간다
    }
    // GC 가 할당 실패에서 구해 준다: 쓰레기를 계속 만들어도 힙이 안 찬다
    {   Heap h(300); uint32_t keeper = h.alloc(1, 2); h.roots = {keeper}; long made = 0;
        for (int i = 0; i < 2000; ++i) { uint32_t o = h.alloc(0, 4); if (!o) { h.collect(); o = h.alloc(0, 4); } assert(o); ++made; if (i % 100 == 0) h.ref(keeper, 0) = o; }
        assert(made == 2000 && h.collections > 5); h.checkInvariants(false); }
    return 0;
}
// Time Complexity: 마크 O(살아있는 객체와 참조), 스윕 O(힙 전체), 할당 O(자유 블록 수)
// Space Complexity: O(깊이) 마크 스택 (포인터 역전 표시는 O(1))
```
## MarkCompact()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 마크-컴팩트(Lisp2 방식): 표시 후 살아있는 객체를 한쪽으로 밀어 붙여(slide) 단편화를 없앤다.  객체의 상대 순서가 유지된다.
//   (1) mark  (2) 새 주소(forwarding address) 계산 — 헤더의 forwarding 칸에 저장  (3) 모든 참조(루트 포함)를 새 주소로 갱신  (4) 객체 이동 (목적지 <= 원래 위치라 낮은 주소부터 옮기면 안전)
// 힙이 가득 차면 압축한 뒤 범프 포인터로 계속 할당한다 (자유 리스트가 필요 없다).  객체 = [헤더][forwarding][참조 n][데이터 d]
// 이어서 대비를 위해 고정 크기 칸 전용 Edwards 의 "두 손가락" 압축도 만든다: 이동 횟수가 최소(살아 있는 칸 중 경계 L 이상인 것만)이지만 순서를 보존하지 않는다
// 검증: ① 임의 그래프 400 개: 압축 뒤 살아 있는 id 집합 == BFS 기준, 살아남은 객체의 주소 순서 보존, 빈틈 없이 앞쪽에 모임, 참조·데이터 보존, 이동한 객체 수 == "앞에 죽은 워드가 있는 산 객체의 수", 두 번째 압축은 아무것도 안 옮김
//        ② 무작위 변경 프로그램 4 000 번: 힙이 차면 압축 후 재시도, id 모형 대조(루트 갱신 포함)  ③ 두 손가락: 산 칸이 [0,L) 로 모이고 이동 수 == L 이상에 있던 산 칸 수 <= Lisp2 이동 수, 그래프 동형
const uint64_t MARK = 1ull << 63, POISON = 0xDEADDEADDEADDEADull;
inline uint32_t sizeOf(uint64_t h) { return (uint32_t)(h & 0xFFFFFF); }
inline uint32_t nrefsOf(uint64_t h) { return (uint32_t)((h >> 24) & 0xFFFF); }

struct Heap {
    std::vector<uint64_t> mem; uint32_t top = 1; std::vector<uint32_t> roots;
    explicit Heap(uint32_t words) : mem(words + 1, POISON) {}
    uint64_t& ref(uint32_t b, uint32_t i) { return mem[b + 2 + i]; }
    uint64_t& data(uint32_t b, uint32_t j) { return mem[b + 2 + nrefsOf(mem[b]) + j]; }
    uint32_t dataWords(uint32_t b) const { return sizeOf(mem[b]) - 2 - nrefsOf(mem[b]); }
    uint32_t alloc(uint32_t nrefs, uint32_t dataN) {
        uint32_t need = 2 + nrefs + dataN; if (top + need > mem.size()) return 0;
        uint32_t b = top; mem[b] = (uint64_t)need | ((uint64_t)nrefs << 24); for (uint32_t i = 1; i < need; ++i) mem[b + i] = 0; top += need; return b;
    }
    void mark() {
        std::vector<uint32_t> st; for (uint32_t r : roots) { if (r) st.push_back(r); }
        while (!st.empty()) { uint32_t b = st.back(); st.pop_back(); if (mem[b] & MARK) continue; mem[b] |= MARK;
            for (uint32_t i = 0; i < nrefsOf(mem[b]); ++i) { uint32_t c = (uint32_t)ref(b, i); if (c && !(mem[c] & MARK)) st.push_back(c); } }
    }
    long compact(long* liveOut = nullptr) {                                                     // 옮긴 객체 수를 돌려준다
        mark(); uint32_t next = 1, oldTop = top; long live = 0, moved = 0;
        for (uint32_t b = 1; b < top; b += sizeOf(mem[b])) { if (mem[b] & MARK) { mem[b + 1] = next; next += sizeOf(mem[b]); ++live; } }      // (2) 새 주소
        for (uint32_t& r : roots) { if (r) r = (uint32_t)mem[r + 1]; }                                                                       // (3) 루트와 참조 갱신
        for (uint32_t b = 1; b < top; b += sizeOf(mem[b])) { if (mem[b] & MARK) for (uint32_t i = 0; i < nrefsOf(mem[b]); ++i) { if (ref(b, i)) ref(b, i) = mem[ref(b, i) + 1]; } }
        for (uint32_t b = 1; b < top;) {                                                                                                     // (4) 이동
            uint32_t sz = sizeOf(mem[b]);
            if (mem[b] & MARK) { uint32_t dst = (uint32_t)mem[b + 1]; if (dst != b) { std::memmove(&mem[dst], &mem[b], (size_t)sz * 8); ++moved; } mem[dst] &= ~MARK; mem[dst + 1] = 0; }
            b += sz;
        }
        top = next; for (uint32_t i = top; i < oldTop; ++i) mem[i] = POISON;                      // 옛 영역을 오염값으로 채워 낡은 참조를 바로 잡아낸다
        if (liveOut) { *liveOut = live; }
        return moved;
    }
    std::vector<uint32_t> objects() const { std::vector<uint32_t> v; for (uint32_t b = 1; b < top; b += sizeOf(mem[b])) { assert(sizeOf(mem[b]) >= 2); v.push_back(b); } return v; }
};

// Edwards 두 손가락: 고정 크기 칸
struct Cell { int id; int refs[3]; };
struct CellHeap {
    std::vector<Cell> cells; std::vector<char> live; std::vector<int> roots;
    long twoFinger() {
        size_t N = cells.size(), L = 0; for (size_t i = 0; i < N; ++i) { L += live[i]; }
        std::vector<int> fwd(N, -1); long moved = 0; size_t lo = 0, hi = N;
        for (;;) {
            while (lo < L && live[lo]) ++lo;                                                     // 아래 손가락: [0,L) 안의 죽은 칸
            while (hi > L && !live[hi - 1]) --hi;                                                // 위 손가락: [L,N) 안의 산 칸
            if (lo >= L || hi <= L) break;
            cells[lo] = cells[hi - 1]; live[lo] = 1; live[hi - 1] = 0; fwd[hi - 1] = (int)lo; ++moved;     // 산 칸을 빈 자리로, 옛 자리에는 전달 주소
        }
        auto fix = [&](int r) { return (r >= 0 && (size_t)r >= L) ? fwd[r] : r; };
        for (int& r : roots) r = fix(r);
        for (size_t i = 0; i < L; ++i) for (int& r : cells[i].refs) r = fix(r);
        cells.resize(L); live.assign(L, 1); return moved;
    }
};

int main() {
    // 원래 예: 0..6 중 1, 3, 5 가 쓰레기
    {   Heap h(100); uint32_t o[7]; int ids[7] = {100, 111, 102, 113, 104, 115, 106};
        for (int i = 0; i < 7; ++i) { o[i] = h.alloc(1, 1); h.data(o[i], 0) = (uint64_t)ids[i]; }
        h.ref(o[0], 0) = o[2]; h.ref(o[2], 0) = o[4]; h.ref(o[4], 0) = o[2]; h.ref(o[6], 0) = o[0]; h.roots = {o[6]};
        long live; long moved = h.compact(&live);
        assert(live == 4 && moved == 3 && h.top == 1 + 4 * 4);                                   // 산 객체 4 개(0, 2, 4, 6), 앞에 죽은 워드가 있는 3 개가 이동
        std::vector<uint32_t> obs = h.objects(); assert(obs.size() == 4);
        assert(h.data(obs[0], 0) == 100 && h.data(obs[1], 0) == 102 && h.data(obs[2], 0) == 104 && h.data(obs[3], 0) == 106);   // 상대 순서 유지
        assert(h.ref(obs[3], 0) == obs[0] && h.ref(obs[0], 0) == obs[1] && h.ref(obs[1], 0) == obs[2] && h.ref(obs[2], 0) == obs[1] && h.roots[0] == obs[3]);
    }

    // ① 임의 그래프에서 압축의 성질
    std::mt19937 rng(5); long graphs = 0, movedTotal = 0, liveTotal = 0;
    for (int g = 0; g < 400; ++g) {
        Heap h(8000); int n = 1 + (int)(rng() % 120); std::vector<uint32_t> objs;
        for (int i = 0; i < n; ++i) { uint32_t b = h.alloc(rng() % 5, 1 + rng() % 3); assert(b); h.data(b, 0) = (uint64_t)(i + 1); objs.push_back(b); }
        for (uint32_t b : objs) for (uint32_t k = 0; k < nrefsOf(h.mem[b]); ++k) { if (rng() % 3) h.ref(b, k) = objs[rng() % objs.size()]; }
        int nr = 1 + (int)(rng() % 3); for (int i = 0; i < nr; ++i) h.roots.push_back(objs[rng() % objs.size()]);
        std::map<int, std::vector<int>> graph; std::map<int, std::vector<uint64_t>> payload; std::vector<int> order;      // 압축 전 논리 그래프와 주소 순서
        for (uint32_t b : h.objects()) { int id = (int)h.data(b, 0); order.push_back(id); for (uint32_t k = 0; k < nrefsOf(h.mem[b]); ++k) { uint32_t c = (uint32_t)h.ref(b, k); graph[id].push_back(c ? (int)h.data(c, 0) : 0); }
            for (uint32_t j = 0; j < h.dataWords(b); ++j) { payload[id].push_back(h.data(b, j)); } }
        std::vector<int> rootIds; for (uint32_t r : h.roots) rootIds.push_back((int)h.data(r, 0));
        std::set<int> want; { std::vector<int> st(rootIds.begin(), rootIds.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (!x || !want.insert(x).second) continue; for (int c : graph[x]) st.push_back(c); } }
        long expectMoved = 0; { uint32_t deadBefore = 0; for (uint32_t b : h.objects()) { int id = (int)h.data(b, 0); if (want.count(id)) { if (deadBefore) ++expectMoved; } else deadBefore += sizeOf(h.mem[b]); } }   // 독립 계산
        long live; long moved = h.compact(&live);
        std::vector<int> after; uint32_t wordsSum = 1;
        for (uint32_t b : h.objects()) { int id = (int)h.data(b, 0); after.push_back(id); wordsSum += sizeOf(h.mem[b]);
            for (uint32_t k = 0; k < nrefsOf(h.mem[b]); ++k) { uint32_t c = (uint32_t)h.ref(b, k); assert((c ? (int)h.data(c, 0) : 0) == graph[id][k]); }
            for (uint32_t j = 0; j < h.dataWords(b); ++j) { assert(h.data(b, j) == payload[id][j]); } }
        assert(std::set<int>(after.begin(), after.end()) == want && (long)after.size() == live && wordsSum == h.top);       // 살아 있는 집합, 빈틈 없음
        std::vector<int> expectOrder; for (int id : order) { if (want.count(id)) expectOrder.push_back(id); } assert(after == expectOrder);   // 상대 순서 보존
        for (size_t i = 0; i < h.roots.size(); ++i) assert((int)h.data(h.roots[i], 0) == rootIds[i]);
        assert(moved == expectMoved);
        std::vector<uint64_t> snap = h.mem; assert(h.compact() == 0 && h.mem == snap);                                       // 멱등
        ++graphs; movedTotal += moved; liveTotal += live;
    }

    // ② 무작위 변경 프로그램 (힙이 차면 압축)
    long compactions = 0, allocs = 0, ooms = 0;
    {   Heap h(900); std::map<int, std::vector<int>> refs; std::vector<int> roots; int nextId = 1;
        auto where = [&]() { std::map<int, uint32_t> w; for (uint32_t b : h.objects()) w[(int)h.data(b, 0)] = b; return w; };
        auto reachable = [&]() { std::set<int> seen; std::vector<int> st(roots.begin(), roots.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (!x || !seen.insert(x).second) continue; for (int c : refs[x]) st.push_back(c); } return seen; };
        auto compactAndVerify = [&]() {
            h.compact(); ++compactions; auto w = where(); std::set<int> reach = reachable(); std::set<int> got; for (auto& kv : w) got.insert(kv.first);
            assert(got == reach);
            for (auto& kv : w) { uint32_t b = kv.second; for (uint32_t k = 0; k < nrefsOf(h.mem[b]); ++k) { uint32_t c = (uint32_t)h.ref(b, k); assert((c ? (int)h.data(c, 0) : 0) == refs[kv.first][k]); }
                for (uint32_t j = 1; j < h.dataWords(b); ++j) { assert(h.data(b, j) == (uint64_t)kv.first * 7919u + j); } }
            for (size_t i = 0; i < roots.size(); ++i) assert((int)h.data(h.roots[i], 0) == roots[i]);
            for (auto it = refs.begin(); it != refs.end();) { if (!reach.count(it->first)) it = refs.erase(it); else ++it; }
        };
        for (int step = 0; step < 4000; ++step) {
            auto w = where(); std::set<int> reach = reachable(); std::vector<int> rl(reach.begin(), reach.end()); int op = (int)(rng() % 100);
            if (op < 50 || rl.empty()) {
                uint32_t nr = rng() % 4, nd = 1 + rng() % 4; uint32_t b = h.alloc(nr, nd);
                if (!b) { compactAndVerify(); w = where(); b = h.alloc(nr, nd); }
                if (!b) { ++ooms; continue; }
                ++allocs; int id = nextId++; h.data(b, 0) = (uint64_t)id; for (uint32_t j = 1; j < h.dataWords(b); ++j) { h.data(b, j) = (uint64_t)id * 7919u + j; }
                refs[id] = std::vector<int>(nr, 0); w[id] = b; int how = (int)(rng() % 10);
                if (how < 3 && roots.size() < 5) { roots.push_back(id); h.roots.push_back(b); }
                else if (how < 8 && !rl.empty()) { int host = rl[rng() % rl.size()]; if (!refs[host].empty()) { uint32_t k = rng() % refs[host].size(); refs[host][k] = id; h.ref(w[host], k) = b; } }
            } else if (op < 85) {
                int host = rl[rng() % rl.size()]; if (refs[host].empty()) continue;
                uint32_t k = rng() % refs[host].size(); int tgt = (rng() % 5 == 0) ? 0 : rl[rng() % rl.size()]; refs[host][k] = tgt; h.ref(w[host], k) = tgt ? w[tgt] : 0;
            } else if (op < 92) { if (!roots.empty()) { size_t i = rng() % roots.size(); roots.erase(roots.begin() + i); h.roots.erase(h.roots.begin() + i); } }
            else if (op < 97) { if (roots.size() < 5) { int id = rl[rng() % rl.size()]; roots.push_back(id); h.roots.push_back(w[id]); } }
            else compactAndVerify();
        }
        compactAndVerify(); assert(compactions > 30 && allocs > 1500);
    }

    // ③ 두 손가락
    long tfMoved = 0, lispMoved = 0, permuted = 0, cellRuns = 0;
    for (int g = 0; g < 400; ++g) {
        CellHeap c; int N = 2 + (int)(rng() % 80); c.cells.resize(N); c.live.assign(N, 0);
        for (int i = 0; i < N; ++i) { c.cells[i].id = i + 1; for (int& r : c.cells[i].refs) r = (rng() % 3) ? (int)(rng() % N) : -1; }
        int nr = 1 + (int)(rng() % 3); for (int i = 0; i < nr; ++i) c.roots.push_back((int)(rng() % N));
        std::vector<int> st(c.roots.begin(), c.roots.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (c.live[x]) continue; c.live[x] = 1; for (int r : c.cells[x].refs) { if (r >= 0) st.push_back(r); } }
        std::map<int, std::vector<int>> graph; std::vector<int> rootIds, liveOrder;
        for (int i = 0; i < N; ++i) { if (!c.live[i]) continue; liveOrder.push_back(c.cells[i].id); for (int r : c.cells[i].refs) graph[c.cells[i].id].push_back(r >= 0 ? c.cells[r].id : 0); }
        for (int r : c.roots) rootIds.push_back(c.cells[r].id);
        size_t L = liveOrder.size(); long expectMoves = 0, lisp2 = 0; bool seenDead = false;
        for (int i = 0; i < N; ++i) { if (c.live[i]) { if ((size_t)i >= L) ++expectMoves; if (seenDead) ++lisp2; } else seenDead = true; }
        long moved = c.twoFinger();
        assert(moved == expectMoves && moved <= lisp2 && c.cells.size() == L);                                               // 이동 수 == L 이상에 있던 산 칸 수
        std::vector<int> after; for (size_t i = 0; i < L; ++i) { after.push_back(c.cells[i].id); int id = c.cells[i].id; for (int k = 0; k < 3; ++k) { int r = c.cells[i].refs[k]; assert((r >= 0 ? c.cells[r].id : 0) == graph[id][k]); } }
        for (size_t i = 0; i < c.roots.size(); ++i) assert(c.cells[c.roots[i]].id == rootIds[i]);
        std::vector<int> a2 = after, b2 = liveOrder; std::sort(a2.begin(), a2.end()); std::sort(b2.begin(), b2.end()); assert(a2 == b2);   // 같은 집합
        if (after != liveOrder) ++permuted;                                                                                  // 순서는 바뀔 수 있다
        tfMoved += moved; lispMoved += lisp2; ++cellRuns;
    }
    assert(permuted > 20 && tfMoved <= lispMoved && graphs == 400);
    std::cout << "MarkCompact verified: " << graphs << " graphs compacted (" << liveTotal << " live objects, " << movedTotal << " moved, order kept), " << compactions
              << " compactions in the mutator run, two-finger moved " << tfMoved << " cells vs " << lispMoved << " for sliding (order not kept in " << permuted << "/" << cellRuns << " runs)." << std::endl;
    return 0;
}
// Time Complexity: O(힙 크기) · 4 패스 (표시 + 주소 계산 + 갱신 + 이동), 두 손가락은 표시 뒤 O(셀 수) 한 번
// Space Complexity: O(1) 추가 (forwarding 주소는 객체 헤더에 저장), 표시 스택 O(깊이)
```
## CopyingGC()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 복사 수집(Cheney 알고리즘): 힙을 from-space/to-space 로 나눈다.  루트에서 닿는 객체를 to-space 로 "복사" 하며 원본에는 전달 주소(forwarding pointer)를 남겨
// 공유된 객체가 두 번 복사되지 않게 한다.  to-space 의 scan 포인터가 free 포인터를 따라잡으면 끝(BFS).  비용은 살아있는 객체에 비례(쓰레기는 방문조차 안 함),
// 결과가 자동으로 압축된다.  단점: 힙의 절반만 쓸 수 있다
// 이 구현은 워드 배열 두 개 위에서 진짜로 만든다: 객체 = [헤더][참조 n][데이터 d], 복사하고 나면 원본의 헤더를 "전달됨 + 새 주소" 로 덮어쓴다.  할당은 범프 포인터.
// 검증: ① 임의 그래프 400 개(순환·공유·자기 참조): 수집 뒤 to-space 의 객체 순서 == 루트부터의 너비 우선 발견 순서(Cheney 의 정확한 성질), 살아 있는 객체가 정확히 한 번씩 복사(복사 횟수 == 도달 가능 수),
//        공유·순환이 보존, 참조·데이터 보존, 옛 공간은 오염값으로 채워 낡은 참조가 있으면 바로 드러남  ② 비용은 쓰레기 양과 무관: 같은 산 구조에 쓰레기를 0 / 100 / 1000 개 섞어도 복사한 워드 수·스캔 수가 같다
//        ③ 무작위 변경 프로그램 4 000 번(할당 실패 시 수집, 루트 갱신): id 모형 대조  ④ 두 번 연속 수집하면 두 번째는 순서까지 같은 배치(고정점)
const uint64_t FWD = 1ull << 63, POISON = 0xDEADDEADDEADDEADull;
inline uint32_t sizeOf(uint64_t h) { return (uint32_t)(h & 0xFFFFFF); }
inline uint32_t nrefsOf(uint64_t h) { return (uint32_t)((h >> 24) & 0xFFFF); }

struct Heap {
    std::vector<uint64_t> from, to; uint32_t top = 1; std::vector<uint32_t> roots; long copiedObjects = 0, copiedWords = 0, scanned = 0, collections = 0;
    explicit Heap(uint32_t semiWords) : from(semiWords + 1, 0), to(semiWords + 1, 0) {}
    uint64_t& ref(uint32_t b, uint32_t i) { return from[b + 1 + i]; }
    uint64_t& data(uint32_t b, uint32_t j) { return from[b + 1 + nrefsOf(from[b]) + j]; }
    uint32_t dataWords(uint32_t b) const { return sizeOf(from[b]) - 1 - nrefsOf(from[b]); }
    uint32_t alloc(uint32_t nrefs, uint32_t dataN) {
        uint32_t need = std::max<uint32_t>(2, 1 + nrefs + dataN); if (top + need > from.size()) return 0;
        uint32_t b = top; from[b] = (uint64_t)need | ((uint64_t)nrefs << 24); for (uint32_t i = 1; i < need; ++i) from[b + i] = 0; top += need; return b;
    }
    void collect() {
        ++collections; uint32_t freePtr = 1, scan = 1;
        auto copy = [&](uint32_t old) -> uint32_t {
            if (!old) return 0;
            uint64_t h = from[old]; if (h & FWD) return (uint32_t)(h & 0xFFFFFFFFu);                                  // 이미 복사됨: 전달 주소
            uint32_t sz = sizeOf(h), nu = freePtr; std::memcpy(&to[nu], &from[old], (size_t)sz * 8); from[old] = FWD | nu; freePtr += sz; ++copiedObjects; copiedWords += sz; return nu;
        };
        for (uint32_t& r : roots) r = copy(r);
        while (scan < freePtr) {                                                                                  // scan 이 free 를 따라잡을 때까지
            uint32_t sz = sizeOf(to[scan]), n = nrefsOf(to[scan]); ++scanned;
            for (uint32_t i = 0; i < n; ++i) { to[scan + 1 + i] = copy((uint32_t)to[scan + 1 + i]); }
            scan += sz;
        }
        std::fill(from.begin(), from.end(), POISON); from.swap(to); top = freePtr;                              // 역할 교대, 옛 from 은 오염값
    }
    std::vector<uint32_t> objects() const { std::vector<uint32_t> v; for (uint32_t b = 1; b < top; b += sizeOf(from[b])) { assert(sizeOf(from[b]) >= 2); v.push_back(b); } return v; }
};

std::vector<int> bfsOrder(const std::map<int, std::vector<int>>& g, const std::vector<int>& roots) {                // 초기 큐 = 루트(중복 제외), 꺼내서 자식을 슬롯 순서로 붙인다
    std::vector<int> q; std::set<int> seen; for (int r : roots) { if (r && seen.insert(r).second) q.push_back(r); }
    for (size_t i = 0; i < q.size(); ++i) { auto it = g.find(q[i]); if (it == g.end()) continue; for (int c : it->second) { if (c && seen.insert(c).second) q.push_back(c); } }
    return q;
}

int main() {
    // 원래 예: 0->1,2 ; 1->3 ; 2->3 ; 3->0 (순환) ; 4<->5 (쓰레기) ; 6 (쓰레기)
    {   Heap h(100); uint32_t o[7]; for (int i = 0; i < 7; ++i) { o[i] = h.alloc(2, 1); h.data(o[i], 0) = (uint64_t)i; }
        h.ref(o[0], 0) = o[1]; h.ref(o[0], 1) = o[2]; h.ref(o[1], 0) = o[3]; h.ref(o[2], 0) = o[3]; h.ref(o[3], 0) = o[0]; h.ref(o[4], 0) = o[5]; h.ref(o[5], 0) = o[4]; h.roots = {o[0]};
        h.collect(); assert(h.copiedObjects == 4 && h.objects().size() == 4);                                        // 도달 가능한 0,1,2,3 만 복사
        uint32_t r = h.roots[0]; assert(h.data(r, 0) == 0);
        uint32_t c1 = (uint32_t)h.ref(r, 0), c2 = (uint32_t)h.ref(r, 1); uint32_t p1 = (uint32_t)h.ref(c1, 0), p2 = (uint32_t)h.ref(c2, 0);
        assert(p1 == p2 && h.data(p1, 0) == 3 && h.ref(p1, 0) == r);                                                 // 공유된 객체 3 은 하나, 순환 3 -> 0 보존
    }

    // ① 임의 그래프: 너비 우선 순서와 정확히 한 번 복사
    std::mt19937 rng(9); long graphs = 0, liveTotal = 0, garbageTotal = 0;
    auto build = [&](Heap& h, int n, int garbage, std::map<int, std::vector<int>>& graph, std::vector<int>& rootIds, std::map<int, std::vector<uint64_t>>& payload, uint32_t seed) {
        std::mt19937 r(seed), r2(seed + 1), r3(seed + 2); std::vector<uint32_t> objs; int total = n + garbage;       // 모양·간선·루트를 서로 다른 난수열로 뽑아, 쓰레기 양이 산 구조를 바꾸지 않게 한다
        for (int i = 0; i < total; ++i) { uint32_t b = h.alloc(r() % 5, 1 + r() % 3); assert(b); h.data(b, 0) = (uint64_t)(i + 1); for (uint32_t j = 1; j < h.dataWords(b); ++j) { h.data(b, j) = (uint64_t)(i + 1) * 31 + j; } objs.push_back(b); }
        std::vector<uint32_t> liveSet(objs.begin(), objs.begin() + n);                                               // 앞 n 개는 산 구조(자기들끼리만 참조), 뒤는 쓰레기(산 쪽도 참조 가능하지만 산 쪽에서는 못 닿는다)
        for (int i = 0; i < total; ++i) for (uint32_t k = 0; k < nrefsOf(h.from[objs[i]]); ++k) {
            if (r2() % 3) { uint32_t t = (i < n) ? liveSet[r2() % n] : objs[r2() % total]; h.ref(objs[i], k) = t; }
        }
        int nr = 1 + (int)(r3() % 3); h.roots.clear(); for (int i = 0; i < nr; ++i) { h.roots.push_back(liveSet[r3() % n]); }
        graph.clear(); payload.clear(); rootIds.clear();
        for (uint32_t b : objs) { int id = (int)h.data(b, 0); for (uint32_t k = 0; k < nrefsOf(h.from[b]); ++k) { uint32_t c = (uint32_t)h.ref(b, k); graph[id].push_back(c ? (int)h.data(c, 0) : 0); } for (uint32_t j = 0; j < h.dataWords(b); ++j) { payload[id].push_back(h.data(b, j)); } }
        for (uint32_t rr : h.roots) rootIds.push_back((int)h.data(rr, 0));
    };
    for (int g = 0; g < 400; ++g) {
        Heap h(9000); std::map<int, std::vector<int>> graph; std::vector<int> rootIds; std::map<int, std::vector<uint64_t>> payload;
        int n = 1 + (int)(rng() % 100), garbage = (int)(rng() % 60); build(h, n, garbage, graph, rootIds, payload, 1000 + g);
        std::vector<int> order = bfsOrder(graph, rootIds); h.collect();
        std::vector<int> got; for (uint32_t b : h.objects()) { int id = (int)h.data(b, 0); got.push_back(id);
            for (uint32_t k = 0; k < nrefsOf(h.from[b]); ++k) { uint32_t c = (uint32_t)h.ref(b, k); assert((c ? (int)h.data(c, 0) : 0) == graph[id][k]); }
            for (uint32_t j = 0; j < h.dataWords(b); ++j) { assert(h.data(b, j) == payload[id][j]); } }
        assert(got == order && h.copiedObjects == (long)order.size() && h.scanned == (long)order.size());              // 순서 == BFS 발견 순서, 정확히 한 번씩
        for (size_t i = 0; i < h.roots.size(); ++i) assert((int)h.data(h.roots[i], 0) == rootIds[i]);
        for (uint32_t i = h.top; i < h.to.size(); ++i) assert(h.to[i] == POISON);                                       // 옛 공간(to 벡터로 바뀐 것)은 오염값
        std::vector<uint64_t> snap(h.from.begin() + 1, h.from.begin() + h.top); std::vector<uint32_t> r2 = h.roots;
        h.collect(); assert(std::vector<uint64_t>(h.from.begin() + 1, h.from.begin() + h.top) == snap && h.roots == r2);   // 한 번 더 하면 같은 배치 (고정점)
        ++graphs; liveTotal += (long)order.size(); garbageTotal += garbage;
    }

    // ② 비용은 살아있는 객체에만 비례
    {   long words[3], scans[3]; int gs[3] = {0, 100, 1000};
        for (int k = 0; k < 3; ++k) { Heap h(40000); std::map<int, std::vector<int>> graph; std::vector<int> rootIds; std::map<int, std::vector<uint64_t>> payload;
            build(h, 80, gs[k], graph, rootIds, payload, 777); h.collect(); words[k] = (long)h.copiedWords; scans[k] = (long)h.scanned; }
        assert(words[0] > 0 && words[0] == words[1] && words[1] == words[2] && scans[0] == scans[1] && scans[1] == scans[2]); }                     // 쓰레기를 1000 개 섞어도 복사량이 같다

    // ③ 무작위 변경 프로그램
    long gcs = 0, allocs = 0;
    {   Heap h(700); std::map<int, std::vector<int>> refs; std::vector<int> roots; int nextId = 1;
        auto where = [&]() { std::map<int, uint32_t> w; for (uint32_t b : h.objects()) w[(int)h.data(b, 0)] = b; return w; };
        auto reachable = [&]() { std::set<int> seen; std::vector<int> st(roots.begin(), roots.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (!x || !seen.insert(x).second) continue; for (int c : refs[x]) st.push_back(c); } return seen; };
        auto collectAndVerify = [&]() {
            h.collect(); ++gcs; auto w = where(); std::set<int> reach = reachable(); std::set<int> got; for (auto& kv : w) got.insert(kv.first);
            assert(got == reach);
            for (auto& kv : w) { uint32_t b = kv.second; for (uint32_t k = 0; k < nrefsOf(h.from[b]); ++k) { uint32_t c = (uint32_t)h.ref(b, k); assert((c ? (int)h.data(c, 0) : 0) == refs[kv.first][k]); } }
            for (size_t i = 0; i < roots.size(); ++i) assert((int)h.data(h.roots[i], 0) == roots[i]);
            for (auto it = refs.begin(); it != refs.end();) { if (!reach.count(it->first)) it = refs.erase(it); else ++it; }
        };
        for (int step = 0; step < 4000; ++step) {
            auto w = where(); std::set<int> reach = reachable(); std::vector<int> rl(reach.begin(), reach.end()); int op = (int)(rng() % 100);
            if (op < 50 || rl.empty()) {
                uint32_t nr = rng() % 4, nd = 1 + rng() % 4; uint32_t b = h.alloc(nr, nd);
                if (!b) { collectAndVerify(); w = where(); b = h.alloc(nr, nd); }
                if (!b) { continue; }                                                                               // 살아 있는 것만으로 가득 찬 경우
                ++allocs; int id = nextId++; h.data(b, 0) = (uint64_t)id; refs[id] = std::vector<int>(nr, 0); w[id] = b; int how = (int)(rng() % 10);
                if (how < 3 && roots.size() < 5) { roots.push_back(id); h.roots.push_back(b); }
                else if (how < 8 && !rl.empty()) { int host = rl[rng() % rl.size()]; if (!refs[host].empty()) { uint32_t k = rng() % refs[host].size(); refs[host][k] = id; h.ref(w[host], k) = b; } }
            } else if (op < 85) {
                int host = rl[rng() % rl.size()]; if (refs[host].empty()) continue;
                uint32_t k = rng() % refs[host].size(); int tgt = (rng() % 5 == 0) ? 0 : rl[rng() % rl.size()]; refs[host][k] = tgt; h.ref(w[host], k) = tgt ? w[tgt] : 0;
            } else if (op < 92) { if (!roots.empty()) { size_t i = rng() % roots.size(); roots.erase(roots.begin() + i); h.roots.erase(h.roots.begin() + i); } }
            else if (op < 97) { if (roots.size() < 5) { int id = rl[rng() % rl.size()]; roots.push_back(id); h.roots.push_back(w[id]); } }
            else collectAndVerify();
        }
        collectAndVerify(); assert(gcs > 30 && allocs > 1500);
    }
    std::cout << "CopyingGC verified: " << graphs << " graphs (" << liveTotal << " survivors copied exactly once in BFS order, " << garbageTotal << " garbage objects never touched), "
              << gcs << " collections in the mutator run; copy cost independent of garbage." << std::endl;
    return 0;
}
// Time Complexity: O(살아있는 객체) (쓰레기는 방문하지 않는다), 할당 O(1)
// Space Complexity: O(힙) · 2 (두 공간), 큐/스택 없이 scan 포인터 하나로 BFS
```
## GenerationalGC()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 세대별 수집: "대부분의 객체는 금방 죽는다"(약한 세대 가설).  새 객체는 young 에 두고 자주·싸게 수집(minor GC), 두 번 이상 살아남으면 old 로 승급해 드물게 수집한다(major GC).
// 문제: old 객체가 young 객체를 가리키면 minor GC 가 old 전체를 훑지 않고도 알아야 한다 -> 쓰기 장벽(write barrier)이 "old -> young 참조" 를 기억한다.
//  장벽은 두 가지를 구현한다: REMEMBERED(조건부: old 가 young 을 가리킬 때만 기억 집합에 추가)와 CARDS(무조건 카드 표시: 쓴 객체가 속한 8 개 묶음에 dirty 비트를 켠다, 값싼 장벽)
//  minor GC 는 루트 + 기억 집합/더러운 카드의 old 객체에서 출발해 young 만 따라간다.  old 의 쓰레기가 가리키는 young 은 살아남는다(nepotism — 떠도는 쓰레기, major 에서 회수)
// 검증: ① 장벽이 없으면 살아 있는 young 객체를 잘못 회수한다 (원래 장면 + 무작위 40 시드 중 손실이 나는 시드 수)  ② 장벽이 있으면 6 000 번 무작위 변경 × 2 가지 장벽 × 20 시드에서
//        GC 뒤: 도달 가능한 객체는 하나도 안 사라지고 참조·id 보존, major 뒤: 살아 있는 집합 == 도달 가능 집합 정확히 일치  ③ GC 직후 기억 집합/더러운 카드는 "old 이면서 young 을 가리키는 객체"와 정확히 같고
//        (GC 사이에는 그것을 빠짐없이 덮음), 승급 규칙: age >= 2 인 객체만 old  ④ 효율: 짧게 사는 객체가 많은 부하에서 세대별 수집이 훑은 객체 수가 "항상 전체 수집" 의 1/3 미만이고 최종 도달 가능 집합은 같다
enum Barrier { NONE, REMEMBERED, CARDS };
struct Obj { bool alive = false, old = false, marked = false; int age = 0, id = 0; std::vector<int> refs; };

struct GenHeap {
    std::vector<Obj> objs; std::vector<int> freeSlots, youngList, roots; Barrier mode; bool generational; size_t nurseryCap, oldCap, youngCount = 0, oldCount = 0;
    std::set<int> remembered; std::vector<char> dirty; static const int CARD = 8;
    long minors = 0, majors = 0, scannedMinor = 0, scannedMajor = 0;
    GenHeap(Barrier b, size_t nursery, size_t limit, bool gen = true) : mode(b), generational(gen), nurseryCap(nursery), oldCap(limit) {}
    bool wantsGC() const { return generational ? (youngCount >= nurseryCap || oldCount >= oldCap) : (youngCount + oldCount >= oldCap); }
    bool collectAuto() { if (!generational || oldCount >= oldCap) { major(); return true; } minor(); return false; }       // 돌려주는 값: major 였는가
    int alloc(int id, int nrefs) {
        int idx; if (!freeSlots.empty()) { idx = freeSlots.back(); freeSlots.pop_back(); } else { idx = (int)objs.size(); objs.emplace_back(); dirty.resize(objs.size() / CARD + 1, 0); }
        Obj& o = objs[idx]; o = Obj(); o.alive = true; o.id = id; o.refs.assign(nrefs, -1); youngList.push_back(idx); ++youngCount; return idx;
    }
    void write(int from, int slot, int to) {                                                  // 쓰기 장벽
        objs[from].refs[slot] = to;
        if (mode == REMEMBERED) { if (objs[from].old && to >= 0 && !objs[to].old) remembered.insert(from); }
        else if (mode == CARDS) dirty[from / CARD] = 1;
    }
    std::vector<int> oldSources() const {                                                      // minor GC 의 추가 루트: old 객체들
        std::vector<int> v;
        if (mode == REMEMBERED) v.assign(remembered.begin(), remembered.end());
        else if (mode == CARDS) {
            for (size_t c = 0; c < dirty.size(); ++c) {
                if (!dirty[c]) continue;
                for (size_t i = c * CARD; i < std::min(objs.size(), (c + 1) * CARD); ++i) { if (objs[i].alive && objs[i].old) v.push_back((int)i); }
            }
        }
        return v;
    }
    bool pointsToYoung(int o) const { for (int c : objs[o].refs) { if (c >= 0 && objs[c].alive && !objs[c].old) return true; } return false; }
    void rebuild(const std::vector<int>& candidates) {                                         // old 이면서 young 을 가리키는 객체만 다시 기억
        remembered.clear(); std::fill(dirty.begin(), dirty.end(), 0);
        for (int o : candidates) {
            if (!objs[o].alive || !objs[o].old || !pointsToYoung(o)) continue;
            if (mode == REMEMBERED) remembered.insert(o); else if (mode == CARDS) dirty[o / CARD] = 1;
        }
    }
    void minor() {
        ++minors; std::vector<int> st; for (int r : roots) { if (r >= 0 && !objs[r].old) st.push_back(r); }
        std::vector<int> srcs = oldSources();
        for (int o : srcs) { ++scannedMinor; for (int c : objs[o].refs) { if (c >= 0 && !objs[c].old) st.push_back(c); } }
        while (!st.empty()) {
            int i = st.back(); st.pop_back(); if (!objs[i].alive || objs[i].old || objs[i].marked) continue;
            objs[i].marked = true; ++scannedMinor; for (int c : objs[i].refs) { if (c >= 0 && !objs[c].old) st.push_back(c); }
        }
        std::vector<int> keep, promoted;
        for (int i : youngList) {
            if (objs[i].marked) { objs[i].marked = false; if (++objs[i].age >= 2) { objs[i].old = true; --youngCount; ++oldCount; promoted.push_back(i); } else keep.push_back(i); }
            else { objs[i].alive = false; objs[i].refs.clear(); freeSlots.push_back(i); --youngCount; }
        }
        youngList = keep; std::vector<int> cand = srcs; cand.insert(cand.end(), promoted.begin(), promoted.end()); rebuild(cand);
    }
    void major() {
        ++majors; std::vector<int> st; for (int r : roots) { if (r >= 0) st.push_back(r); }
        while (!st.empty()) {
            int i = st.back(); st.pop_back(); if (!objs[i].alive || objs[i].marked) continue;
            objs[i].marked = true; ++scannedMajor; for (int c : objs[i].refs) { if (c >= 0) st.push_back(c); }
        }
        youngList.clear(); youngCount = oldCount = 0; std::vector<int> olds;
        for (size_t i = 0; i < objs.size(); ++i) {
            Obj& o = objs[i]; if (!o.alive) continue;
            if (!o.marked) { o.alive = false; o.refs.clear(); freeSlots.push_back((int)i); continue; }
            o.marked = false;
            if (!generational) o.old = true;                                                    // 비세대 모드(비교용): 전부 한 덩어리
            if (o.old) { ++oldCount; olds.push_back((int)i); } else { ++youngCount; youngList.push_back((int)i); }
        }
        rebuild(olds);
    }
    std::set<int> aliveIds() const { std::set<int> s; for (const Obj& o : objs) { if (o.alive) s.insert(o.id); } return s; }
};

struct Run { long lost = 0, floating = 0, minors = 0, majors = 0, ops = 0; };

// 무작위 변경 프로그램을 id 모형과 함께 돌린다 (손실이 처음 나오면 중단)
Run runProgram(Barrier mode, uint32_t seed, int steps) {
    GenHeap h(mode, 24, 120); std::mt19937 rng(seed); Run run; std::map<int, std::vector<int>> refs; std::vector<int> roots; std::map<int, int> idxOf; int nextId = 1;
    auto reachable = [&]() { std::set<int> seen; std::vector<int> st(roots.begin(), roots.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (x < 0 || !seen.insert(x).second) continue; for (int c : refs[x]) st.push_back(c); } return seen; };
    auto syncRoots = [&]() { h.roots.clear(); for (int r : roots) h.roots.push_back(idxOf[r]); };
    auto check = [&](bool major) -> bool {                                                     // GC 직후 검사: 도달 가능한 것이 하나도 안 사라졌나
        std::set<int> reach = reachable(); long lost = 0;
        for (int id : reach) {
            int ix = idxOf[id]; if (!h.objs[ix].alive || h.objs[ix].id != id) { ++lost; continue; }
            for (size_t k = 0; k < refs[id].size(); ++k) { int c = h.objs[ix].refs[k]; int cid = c < 0 ? -1 : (h.objs[c].alive ? h.objs[c].id : -2); if (cid != refs[id][k]) ++lost; }
        }
        run.lost += lost; if (lost) return false;
        std::set<int> alive = h.aliveIds();
        if (major) assert(alive == reach); else run.floating += (long)(alive.size() - reach.size());      // major 뒤 정확히 일치, minor 뒤에는 떠도는 쓰레기가 남을 수 있다
        for (const Obj& o : h.objs) { if (o.alive) assert((o.age >= 2) == o.old); }                       // 승급 규칙
        if (mode != NONE) {                                                                              // GC 직후 기억 집합/카드는 정확히 "old 이면서 young 을 가리키는 객체"
            std::set<int> want, wantCards; for (size_t i = 0; i < h.objs.size(); ++i) { if (h.objs[i].alive && h.objs[i].old && h.pointsToYoung((int)i)) { want.insert((int)i); wantCards.insert((int)i / GenHeap::CARD); } }
            if (mode == REMEMBERED) assert(h.remembered == want);
            else { std::set<int> got; for (size_t c = 0; c < h.dirty.size(); ++c) { if (h.dirty[c]) got.insert((int)c); } assert(got == wantCards); }
        }
        return true;
    };
    for (int step = 0; step < steps; ++step) {
        ++run.ops;
        if (h.wantsGC()) { syncRoots(); bool major = h.collectAuto(); if (!check(major)) break; }
        std::set<int> reach = reachable(); std::vector<int> rl(reach.begin(), reach.end()); int op = (int)(rng() % 100);
        if (op < 50 || rl.empty()) {
            int id = nextId++, nr = (int)(rng() % 4); int ix = h.alloc(id, nr); idxOf[id] = ix; refs[id] = std::vector<int>(nr, -1); int how = (int)(rng() % 10);
            if (how < 3 && roots.size() < 4) roots.push_back(id);
            else if (how < 9 && !rl.empty()) { int host = rl[rng() % rl.size()]; if (!refs[host].empty()) { size_t k = rng() % refs[host].size(); refs[host][k] = id; h.write(idxOf[host], (int)k, ix); } }
        } else if (op < 90) {
            int host = rl[rng() % rl.size()]; if (refs[host].empty()) continue;
            size_t k = rng() % refs[host].size(); int tgt = (rng() % 6 == 0) ? -1 : rl[rng() % rl.size()]; refs[host][k] = tgt; h.write(idxOf[host], (int)k, tgt < 0 ? -1 : idxOf[tgt]);
        } else if (op < 95) { if (!roots.empty()) roots.erase(roots.begin() + rng() % roots.size()); }
        else if (roots.size() < 4) roots.push_back(rl[rng() % rl.size()]);
        if (step % 97 == 0) { syncRoots(); h.minor(); if (!check(false)) break; }
        if (step % 531 == 0) { syncRoots(); h.major(); if (!check(true)) break; }
        if (mode == REMEMBERED) {                                                                        // GC 사이에도 old -> young 간선은 하나도 빠지면 안 된다
            for (size_t i = 0; i < h.objs.size(); ++i) { if (h.objs[i].alive && h.objs[i].old && h.pointsToYoung((int)i)) assert(h.remembered.count((int)i)); }
        }
    }
    run.minors = h.minors; run.majors = h.majors; return run;
}

// 짧게 사는 객체가 많은 부하: 10 개 중 하나만 표에 넣어 오래 산다
long workload(bool generational, std::set<int>& finalIds) {
    GenHeap h(REMEMBERED, 64, generational ? 1000 : 270, generational); std::map<int, std::vector<int>> refs; std::map<int, int> idxOf; int nextId = 1;
    int tableId = nextId++; int table = h.alloc(tableId, 200); idxOf[tableId] = table; refs[tableId] = std::vector<int>(200, -1); int slot = 0;
    for (int it = 0; it < 6000; ++it) {
        h.roots = {table}; if (h.wantsGC()) h.collectAuto();
        int id = nextId++; int ix = h.alloc(id, 2); idxOf[id] = ix; refs[id] = std::vector<int>(2, -1);
        if (it % 10 == 0) { refs[tableId][slot % 200] = id; h.write(table, slot % 200, ix); ++slot; }
        else if (it % 10 == 1) { int prev = idxOf[id - 1]; if (h.objs[prev].alive && h.objs[prev].id == id - 1) { refs[id][0] = id - 1; h.write(ix, 0, prev); } }
    }
    h.roots = {table}; h.major();
    std::set<int> reach, seen; std::vector<int> st{tableId};
    while (!st.empty()) { int x = st.back(); st.pop_back(); if (x < 0 || !reach.insert(x).second) continue; for (int c : refs[x]) st.push_back(c); }
    finalIds = h.aliveIds(); assert(finalIds == reach);
    return h.scannedMinor + h.scannedMajor;
}

int main() {
    // ① 원래 장면: old -> young 참조
    for (int variant = 0; variant < 3; ++variant) {
        Barrier mode = variant == 0 ? NONE : variant == 1 ? REMEMBERED : CARDS; GenHeap h(mode, 100, 100);
        int oldObj = h.alloc(1, 1); h.roots = {oldObj}; h.minor(); h.minor(); assert(h.objs[oldObj].old);            // 두 번 살아남아 old 로 승급
        int young = h.alloc(2, 1), garbage = h.alloc(3, 1); h.write(oldObj, 0, young);                              // old -> young 참조 (쓰기 장벽 발동)
        h.minor();
        assert(!h.objs[garbage].alive);                                                                              // 쓰레기는 회수
        assert(h.objs[young].alive == (mode != NONE));                                                               // 장벽이 없으면 살아있는 young 을 잘못 회수한다
    }
    // ② 무작위 변경: 장벽이 있는 쪽은 손실 0, 없는 쪽은 손실이 나는 시드가 있다
    long lostSeedsNone = 0, floatingTotal = 0, minors = 0, majors = 0, ops = 0;
    for (uint32_t seed = 1; seed <= 40; ++seed) { Run r = runProgram(NONE, seed, 3000); if (r.lost) ++lostSeedsNone; }
    for (uint32_t seed = 1; seed <= 20; ++seed) {
        for (int m = 1; m <= 2; ++m) {
            Run r = runProgram(m == 1 ? REMEMBERED : CARDS, seed * 7919u, 6000); assert(r.lost == 0);
            floatingTotal += r.floating; minors += r.minors; majors += r.majors; ops += r.ops;
        }
    }
    assert(lostSeedsNone >= 20 && minors > 3000 && majors > 100 && floatingTotal > 0);
    // ③ 효율
    std::set<int> finalGen, finalFull; long scanGen = workload(true, finalGen), scanFull = workload(false, finalFull);
    assert(finalGen == finalFull && scanGen * 3 < scanFull);                                                          // 같은 결과를 3 배 이상 적게 훑어서
    std::cout << "GenerationalGC verified: without a barrier " << lostSeedsNone << "/40 seeds lose live objects, with barriers 0 losses in " << ops << " ops (" << minors << " minor, " << majors
              << " major, " << floatingTotal << " floating garbage seen); generational scanned " << scanGen << " vs " << scanFull << " objects." << std::endl;
    return 0;
}
// Time Complexity: minor GC 는 살아있는 young + 기억 집합(또는 더러운 카드)에 비례, major GC 는 살아있는 전체
// Space Complexity: O(기억 집합) 또는 O(카드 수)
```
## ReferenceCountingGC()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 참조 카운팅: 객체마다 "나를 가리키는 참조의 수" 를 세어 0 이 되면 즉시 해제한다 (즉시성, 예측 가능한 지연).  치명적 약점은 순환 참조 — 서로를 가리키면 카운트가 0 이 되지 않는다.
// CPython 은 참조 카운팅 + 순환 수집기: "내부 참조를 뺀 카운트 gc_refs" 가 0 보다 큰 객체는 외부에서 참조되는 것이므로 거기서 닿는 것만 살리고 나머지를 회수한다
struct Obj { std::vector<int> refs; int rc = 0; bool alive = false; };
struct Heap {
    std::vector<Obj> o; int freedCount = 0;
    int make() { o.push_back(Obj{}); o.back().alive = true; return o.size() - 1; }
    void incref(int i) { o[i].rc++; }
    void decref(int i) { if (--o[i].rc == 0) free(i); }
    void free(int i) { o[i].alive = false; freedCount++; for (int c : o[i].refs) decref(c); o[i].refs.clear(); }
    void link(int from, int to) { o[from].refs.push_back(to); incref(to); }
    int cycleCollect() {                                              // 순환 수집: 내부 참조를 빼고 외부 참조가 없는 덩어리를 회수
        int n = o.size(); std::vector<int> gcRefs(n);
        for (int i = 0; i < n; i++) gcRefs[i] = o[i].alive ? o[i].rc : 0;
        for (int i = 0; i < n; i++) if (o[i].alive) for (int c : o[i].refs) gcRefs[c]--;     // 객체끼리의 참조 제외
        std::vector<bool> reach(n, false); std::vector<int> st;
        for (int i = 0; i < n; i++) if (o[i].alive && gcRefs[i] > 0) st.push_back(i);        // 외부(루트)에서 직접 참조되는 객체
        while (!st.empty()) { int i = st.back(); st.pop_back(); if (reach[i]) continue; reach[i] = true; for (int c : o[i].refs) st.push_back(c); }
        int freed = 0;
        for (int i = 0; i < n; i++) if (o[i].alive && !reach[i]) { o[i].alive = false; o[i].refs.clear(); freed++; }
        return freed;
    }
};

int main() {
    Heap h;
    int a = h.make(), b = h.make(), c = h.make();
    h.incref(a); h.incref(c);                  // 루트(변수)가 a, c 를 참조
    h.link(a, b);                              // a -> b
    h.decref(a);                               // 루트가 a 를 놓음 -> a 해제 -> b 의 카운트도 0 -> 연쇄 해제
    assert(!h.o[a].alive && !h.o[b].alive && h.o[c].alive);             // 즉시 회수 (연쇄)

    int x = h.make(), y = h.make();
    h.incref(x);                               // 루트가 x 를 참조
    h.link(x, y); h.link(y, x);                // x <-> y 순환
    h.decref(x);                               // 루트가 x 를 놓았지만 y -> x 참조가 남아 rc(x) = 1
    assert(h.o[x].alive && h.o[y].alive);      // 누수: 순환이라 카운트가 0 이 되지 않는다
    assert(h.cycleCollect() == 2);             // 순환 수집기가 회수
    assert(!h.o[x].alive && !h.o[y].alive && h.o[c].alive);            // 루트가 쥔 c 는 안전
    std::cout << "ReferenceCountingGC: cycle leaked until the cycle collector ran." << std::endl;
    return 0;
}
// Time Complexity: decref 연쇄 해제 O(해제되는 객체), 순환 수집 O(객체 + 참조)
// Space Complexity: 객체당 카운터 하나
```
## IncrementalGC()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 증분 수집: 마킹을 작은 조각으로 쪼개 프로그램(뮤테이터)과 번갈아 실행해 긴 멈춤을 없앤다.  삼색 표시: 흰색(미방문) / 회색(방문했으나 자식 미처리) / 검정(자식까지 처리).
// 불변식: "검정 객체는 흰 객체를 직접 가리키지 않는다".  뮤테이터가 검정 객체에 흰 객체 참조를 쓰면 그 흰 객체는 영영 처리되지 않아 살아있는데 회수된다.
// 쓰기 장벽(Dijkstra): 검정 객체에 참조를 쓸 때 대상 객체를 회색으로 칠한다
// 이 구현은 세 가지 장벽을 비교한다: NONE(없음), DIJKSTRA(삽입 장벽: 새로 쓰는 대상을 회색으로 — 강한 불변식 "검정 -> 흰 간선 없음", 끝낼 때 루트를 다시 훑어야 한다),
//  YUASA(삭제 장벽, snapshot-at-beginning: 덮어쓰는 옛 값을 회색으로 — 약한 불변식 "검정이 가리키는 흰 객체는 회색에서 흰 길로 닿는다", 루트 재검사 불필요).  마킹 중 새 객체는 검정으로 만든다(allocate-black)
// 검증: ① 고전 장면(검정 객체에 숨은 참조)에서 NONE 만 객체를 잃는다  ② 무작위 변경 4 000 번과 증분 단계(예산 1~3)를 섞어 20 시드 × 장벽마다: 매 단계 불변식을 검사하고,
//        스윕 뒤 (a) 도달 가능한 객체가 하나도 안 사라졌고 (b) 살아 있는 집합 ⊆ (사이클 시작 때 도달 가능한 집합 ∪ 사이클 중 새로 만든 객체)  ③ NONE 은 손실이 나는 시드가 많다
//        ④ 변경이 멈춘 상태의 마지막 사이클은 살아 있는 집합 == 도달 가능 집합 정확히 일치, Dijkstra 만 루트 재검사가 필요
enum Color { WHITE, GRAY, BLACK };
enum Barrier { NONE, DIJKSTRA, YUASA };
struct Obj { bool alive = false; Color color = WHITE; int id = 0; std::vector<int> refs; };

struct IncHeap {
    std::vector<Obj> objs; std::vector<int> freeSlots, gray, roots; Barrier mode; bool marking = false; long barrierShades = 0, rescans = 0, steps = 0;
    explicit IncHeap(Barrier b) : mode(b) {}
    int alloc(int id, int nrefs) {
        int idx; if (!freeSlots.empty()) { idx = freeSlots.back(); freeSlots.pop_back(); } else { idx = (int)objs.size(); objs.emplace_back(); }
        Obj& o = objs[idx]; o = Obj(); o.alive = true; o.id = id; o.refs.assign(nrefs, -1); o.color = marking ? BLACK : WHITE; return idx;       // 마킹 중 할당 = 검정
    }
    void shade(int i) { if (i >= 0 && objs[i].alive && objs[i].color == WHITE) { objs[i].color = GRAY; gray.push_back(i); } }
    void startCycle() { marking = true; for (int r : roots) shade(r); }
    bool step(int budget) {                                                                    // 회색 객체를 budget 개까지 처리
        while (budget-- > 0 && !gray.empty()) { int i = gray.back(); gray.pop_back(); for (int c : objs[i].refs) shade(c); objs[i].color = BLACK; ++steps; }
        return gray.empty();
    }
    void write(int from, int slot, int to) {
        if (marking) {
            if (mode == DIJKSTRA && to >= 0 && objs[to].color == WHITE) { ++barrierShades; shade(to); }
            if (mode == YUASA) { int old = objs[from].refs[slot]; if (old >= 0 && objs[old].color == WHITE) { ++barrierShades; shade(old); } }
        }
        objs[from].refs[slot] = to;
    }
    void finish() {                                                                            // 종료: (Dijkstra) 루트 재검사 -> 스윕
        if (mode == DIJKSTRA) { ++rescans; for (int r : roots) shade(r); while (!gray.empty()) step(1 << 20); }
        assert(gray.empty());
        for (size_t i = 0; i < objs.size(); ++i) { Obj& o = objs[i]; if (!o.alive) continue; if (o.color == WHITE) { o.alive = false; o.refs.clear(); freeSlots.push_back((int)i); } else o.color = WHITE; }
        marking = false;
    }
    void checkInvariant() const {                                                               // 마킹 중 삼색 불변식
        if (!marking) return;
        if (mode == DIJKSTRA) { for (const Obj& o : objs) { if (o.alive && o.color == BLACK) for (int c : o.refs) assert(c < 0 || !objs[c].alive || objs[c].color != WHITE); } }
        if (mode == YUASA) {
            std::set<int> chain; std::vector<int> st; for (int g : gray) st.push_back(g);
            while (!st.empty()) { int i = st.back(); st.pop_back(); for (int c : objs[i].refs) { if (c >= 0 && objs[c].alive && objs[c].color == WHITE && chain.insert(c).second) st.push_back(c); } }   // 회색에서 흰 길로 닿는 흰 객체
            for (const Obj& o : objs) { if (o.alive && o.color == BLACK) for (int c : o.refs) assert(c < 0 || !objs[c].alive || objs[c].color != WHITE || chain.count(c)); }
        }
    }
};

bool classicScenario(Barrier mode) {                                                         // 고전 장면: 검정 객체에 숨은 참조를 쓰고 회색 객체의 참조를 지운다
    IncHeap h(mode); int A = h.alloc(1, 2), B = h.alloc(2, 1), C = h.alloc(3, 0);
    h.write(A, 0, B); h.write(B, 0, C); h.roots = {A};
    h.startCycle(); h.step(1);                                                               // A 는 검정, B 는 회색
    h.roots.push_back(C);                                                                    // 뮤테이터가 B 에서 C 를 읽어 지역 변수에 둔다
    h.write(A, 1, C);                                                                        // 검정 A -> 흰 C
    h.write(B, 0, -1);                                                                       // 회색 B -> C 삭제
    h.roots.pop_back(); h.step(100); h.finish();
    return h.objs[C].alive;                                                                  // A -> C 로 아직 닿으므로 살아 있어야 한다
}

struct Result { long lost = 0, floating = 0, cycles = 0, shades = 0, rescans = 0; };
Result runProgram(Barrier mode, uint32_t seed, int steps) {
    IncHeap h(mode); std::mt19937 rng(seed); Result res; std::map<int, std::vector<int>> refs; std::vector<int> roots; std::map<int, int> idxOf; int nextId = 1;
    std::set<int> s0, allocated;
    auto reachable = [&]() { std::set<int> seen; std::vector<int> st(roots.begin(), roots.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (x < 0 || !seen.insert(x).second) continue; for (int c : refs[x]) st.push_back(c); } return seen; };
    auto sync = [&]() { h.roots.clear(); for (int r : roots) h.roots.push_back(idxOf[r]); };
    auto sweepAndCheck = [&]() -> bool {
        sync(); h.finish(); ++res.cycles; std::set<int> reach = reachable(); long lost = 0;
        for (int id : reach) { int ix = idxOf[id]; if (!h.objs[ix].alive || h.objs[ix].id != id) { ++lost; continue; }
            for (size_t k = 0; k < refs[id].size(); ++k) { int c = h.objs[ix].refs[k]; int cid = c < 0 ? -1 : (h.objs[c].alive ? h.objs[c].id : -2); if (cid != refs[id][k]) ++lost; } }
        res.lost += lost; if (lost) return false;
        std::set<int> alive; for (const Obj& o : h.objs) { if (o.alive) alive.insert(o.id); }
        for (int id : alive) assert(s0.count(id) || allocated.count(id));                                    // 살아 있는 집합 ⊆ 시작 때 도달 가능 ∪ 새로 만든 것
        res.floating += (long)(alive.size() - reach.size());
        for (auto it = refs.begin(); it != refs.end();) { if (!alive.count(it->first)) it = refs.erase(it); else ++it; }
        return true;
    };
    for (int step = 0; step < steps; ++step) {
        std::set<int> reach = reachable(); std::vector<int> rl(reach.begin(), reach.end()); int op = (int)(rng() % 100);
        if (op < 40 || rl.empty()) {
            int id = nextId++, nr = (int)(rng() % 4); int ix = h.alloc(id, nr); idxOf[id] = ix; refs[id] = std::vector<int>(nr, -1); if (h.marking) allocated.insert(id); int how = (int)(rng() % 10);
            if (how < 3 && roots.size() < 4) roots.push_back(id);
            else if (how < 9 && !rl.empty()) { int host = rl[rng() % rl.size()]; if (!refs[host].empty()) { size_t k = rng() % refs[host].size(); refs[host][k] = id; h.write(idxOf[host], (int)k, ix); } }
        } else if (op < 78) {
            int host = rl[rng() % rl.size()]; if (!refs[host].empty()) { size_t k = rng() % refs[host].size(); int tgt = (rng() % 6 == 0) ? -1 : rl[rng() % rl.size()]; refs[host][k] = tgt; h.write(idxOf[host], (int)k, tgt < 0 ? -1 : idxOf[tgt]); }
        } else if (op < 86) { if (!roots.empty()) roots.erase(roots.begin() + rng() % roots.size()); }
        else if (op < 93) { if (roots.size() < 4) roots.push_back(rl[rng() % rl.size()]); }                       // 지역 변수가 힙에서 객체를 읽어 온다 (장벽 없음)
        if (!h.marking && rng() % 100 < 4) { sync(); s0 = reachable(); allocated.clear(); h.startCycle(); }
        else if (h.marking) {
            sync(); bool done = h.step(1 + (int)(rng() % 3)); h.checkInvariant();
            if (done && rng() % 100 < 40) { if (!sweepAndCheck()) break; }
        }
        sync();
    }
    if (res.lost == 0) {                                                                                         // 변경이 멈춘 상태의 마지막 사이클은 정확해야 한다
        if (h.marking) { sync(); while (!h.step(5)) {} if (!sweepAndCheck()) return res; }
        sync(); s0 = reachable(); allocated.clear(); h.startCycle(); while (!h.step(5)) {} sync(); h.finish();
        std::set<int> alive, reach = reachable(); for (const Obj& o : h.objs) { if (o.alive) alive.insert(o.id); }
        assert(alive == reach);
    }
    res.shades = h.barrierShades; res.rescans = h.rescans; return res;
}

int main() {
    assert(!classicScenario(NONE) && classicScenario(DIJKSTRA) && classicScenario(YUASA));                        // 장벽이 없으면 C 를 잃는다
    long lostSeeds = 0, floating[3] = {0, 0, 0}, cycles[3] = {0, 0, 0}, shades[3] = {0, 0, 0}, rescans[3] = {0, 0, 0};
    for (uint32_t seed = 1; seed <= 20; ++seed) for (int m = 0; m < 3; ++m) {
        Result r = runProgram((Barrier)m, seed * 104729u, 4000);
        if (m == NONE) { if (r.lost) ++lostSeeds; } else assert(r.lost == 0);
        floating[m] += r.floating; cycles[m] += r.cycles; shades[m] += r.shades; rescans[m] += r.rescans;
    }
    assert(lostSeeds >= 5 && cycles[DIJKSTRA] > 200 && cycles[YUASA] > 200 && shades[DIJKSTRA] > 0 && shades[YUASA] > 0 && rescans[DIJKSTRA] > 0 && rescans[YUASA] == 0);
    std::cout << "IncrementalGC verified: no barrier loses live objects in " << lostSeeds << "/20 seeds; Dijkstra (" << cycles[DIJKSTRA] << " cycles, " << shades[DIJKSTRA] << " barrier shades, " << rescans[DIJKSTRA]
              << " root rescans) and Yuasa (" << cycles[YUASA] << " cycles, " << shades[YUASA] << " shades, no rescan) lose none; floating garbage " << floating[DIJKSTRA] << " / " << floating[YUASA] << "." << std::endl;
    return 0;
}
// Time Complexity: 조각당 O(예산), 한 사이클 O(힙), 장벽 O(1)
// Space Complexity: O(회색 작업 목록)
```
## ConcurrentGC()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <mutex>
#include <random>
#include <set>
#include <thread>
#include <vector>
#include <cassert>

// 동시 수집: 수집기 스레드가 프로그램(뮤테이터)이 실행되는 동안 병렬로 마킹한다.  이때 뮤테이터가 참조를 지우면 수집기가 그 객체를 영영 못 볼 수 있다.
// SATB(Snapshot-At-The-Beginning, Yuasa 삭제 장벽): 참조를 덮어쓰기 전에 "지워지는 옛 값" 을 마킹 큐에 넣는다 -> 수집 시작 시점에 닿던 모든 객체는 반드시 표시된다.
// 검증: 시작 시점에 도달 가능했던 객체 중 회수 대상(표시 안 됨)이 하나도 없어야 한다
struct Heap {
    std::mutex mu;                                              // 단순화: 각 연산을 짧게 잠근다 (실제 JVM 은 락 없는 장벽 사용)
    std::vector<std::vector<int>> refs; std::vector<bool> marked; std::vector<int> work; std::vector<int> satbQueue;
    explicit Heap(int n) : refs(n), marked(n, false) {}
    void writeRef(int from, int slot, int to) {
        std::lock_guard<std::mutex> g(mu);
        int old = refs[from][slot];
        if (old >= 0) satbQueue.push_back(old);                // 삭제 장벽
        refs[from][slot] = to;
    }
    bool markStep() {                                          // 수집기: 작업 하나 처리
        std::lock_guard<std::mutex> g(mu);
        for (int s : satbQueue) work.push_back(s);
        satbQueue.clear();
        if (work.empty()) return false;
        int i = work.back(); work.pop_back();
        if (marked[i]) return true;
        marked[i] = true;
        for (int c : refs[i]) if (c >= 0) work.push_back(c);
        return true;
    }
};

int main() {
    const int N = 200;
    std::mt19937 rng(7);
    Heap h(N);
    for (int i = 0; i < N; i++) { h.refs[i] = {-1, -1}; }
    for (int i = 1; i < N; i++) h.refs[(i - 1) / 2][i % 2] = i;                 // 루트 0 에서 닿는 이진 트리 형태
    // 시작 시점의 스냅샷: 루트 0 에서 도달 가능한 객체 집합
    std::set<int> snapshot; { std::vector<int> st = {0}; while (!st.empty()) { int i = st.back(); st.pop_back(); if (!snapshot.insert(i).second) continue; for (int c : h.refs[i]) if (c >= 0) st.push_back(c); } }
    h.work.push_back(0);
    std::atomic<bool> done(false);
    std::thread mutator([&] {                                                    // 뮤테이터: 마킹 도중 참조를 마구 끊고 바꾼다 (쓰기 횟수는 유한하게 — 수집기가 반드시 끝나도록)
        std::mt19937 r(99);
        for (int k = 0; k < 100000; k++) { int from = r() % N, slot = r() % 2; int to = (r() % 3 == 0) ? -1 : (int)(r() % N); h.writeRef(from, slot, to); }
        done = true;
    });
    for (;;) { if (h.markStep()) continue; if (done) { while (h.markStep()) {} break; } std::this_thread::yield(); }          // 일이 없으면 양보하고, 뮤테이터가 끝났으면 남은 장벽 기록까지 비운다
    mutator.join();
    int missed = 0; for (int i : snapshot) if (!h.marked[i]) missed++;
    assert(missed == 0);                                                          // 스냅샷에서 닿던 객체는 하나도 놓치지 않았다
    std::cout << "ConcurrentGC (SATB): snapshot of " << snapshot.size() << " objects fully marked despite concurrent mutation" << std::endl;
    return 0;
}
// Time Complexity: O(스냅샷 크기 + 장벽 기록 수)
// Space Complexity: O(SATB 큐)
```
# Part 8. 캐시
## CacheLine()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <stdexcept>
#if defined(__linux__)
#include <unistd.h>
#endif

// 캐시는 바이트가 아니라 "캐시 라인"(보통 64바이트) 단위로 메모리를 옮긴다.  주소를 세 부분으로 나눈다:  [ 태그 | 세트 인덱스 | 라인 내 오프셋(log2 라인 바이트) ].  라인 하나를 읽으면 이웃한 63바이트가 공짜로 따라오므로 순차 접근(공간 지역성)이 빠르다.
//  크기·라인·연관도(ways)로 만든 기하(geometry)가 주소를 (tag, set, offset) 으로 가르고 다시 합친다.  ① 무작위 주소 10 만 개에서 분해-합성 왕복이 항등, 세트 번호 < 세트 수, 같은 라인의 두 주소는 태그·세트가 같고 오프셋만 다르다
//  ② 구간 접근 [addr, addr+len) 이 건드리는 라인 수 = (addr+len−1)/L − addr/L + 1 이 집합으로 센 값과 같다 (8 바이트 객체가 라인 경계에 걸리면 2 라인; alignas(64) 인 64 바이트 구조체는 항상 1 라인)
//  ③ 보폭(stride) 접근: 4096 바이트 배열을 보폭 s 로 읽을 때 건드리는 라인 수 = min(4096/L, ⌈4096/s⌉) — 보폭이 라인 이상이면 접근 하나가 라인 하나를 독점해 가져온 바이트의 대부분을 낭비 (이용률 = 접근 크기 / L)  ④ 잘못된 기하(2 의 거듭제곱이 아님)는 거부.
struct Geometry {
    uint64_t size, line, ways, sets; int offBits, setBits;
    Geometry(uint64_t sizeBytes, uint64_t lineBytes, uint64_t w) : size(sizeBytes), line(lineBytes), ways(w) {
        auto pow2 = [](uint64_t x) { return x != 0 && (x & (x - 1)) == 0; }; if (!pow2(sizeBytes) || !pow2(lineBytes) || !pow2(w) || sizeBytes < lineBytes * w) throw std::invalid_argument("geometry"); sets = sizeBytes / lineBytes / w;
        offBits = __builtin_ctzll(lineBytes); setBits = __builtin_ctzll(sets); }
    uint64_t offset(uint64_t a) const { return a & (line - 1); }
    uint64_t set(uint64_t a) const { return (a >> offBits) & (sets - 1); }
    uint64_t tag(uint64_t a) const { return a >> (offBits + setBits); }
    uint64_t compose(uint64_t tag, uint64_t setIdx, uint64_t off) const { return (tag << (offBits + setBits)) | (setIdx << offBits) | off; }
    uint64_t lineOf(uint64_t a) const { return a >> offBits; }
};
struct alignas(64) Aligned64 { char c[64]; }; struct Unaligned64 { char c[64]; };

int main() {
    Geometry g(32 * 1024, 64, 8); assert(g.sets == 64 && g.offBits == 6 && g.setBits == 6);
    std::mt19937_64 rng(1015);
    for (int i = 0; i < 100000; ++i) { uint64_t a = rng() >> 12; uint64_t t = g.tag(a), s = g.set(a), o = g.offset(a); assert(g.compose(t, s, o) == a && s < g.sets && o < g.line);                                           // ① 왕복
        uint64_t b = (a & ~(g.line - 1)) | (rng() % g.line); assert(g.tag(b) == t && g.set(b) == s && g.lineOf(a) == g.lineOf(b));                                                                         // 같은 라인
        uint64_t c = a + g.line; assert(g.lineOf(c) == g.lineOf(a) + 1); }
    assert(g.lineOf(0) == 0 && g.lineOf(63) == 0 && g.lineOf(64) == 1 && g.offset(200) == 8 && g.lineOf(200) == 3);
    for (int i = 0; i < 20000; ++i) { uint64_t addr = rng() % 100000, len = 1 + rng() % 300; std::set<uint64_t> lines; for (uint64_t b = addr; b < addr + len; ++b) lines.insert(g.lineOf(b)); assert(lines.size() == (addr + len - 1) / 64 - addr / 64 + 1); }          // ② 구간이 걸친 라인 수
    {   int straddling = 0; for (uint64_t addr = 0; addr < 256; ++addr) { uint64_t n = (addr + 7) / 64 - addr / 64 + 1; straddling += n == 2; assert(n == (addr % 64 > 56 ? 2u : 1u)); } assert(straddling == 4 * 7);                  // 8 바이트 객체: 오프셋 57..63 에서 시작하면 두 라인
        for (uint64_t addr = 0; addr < 1024; addr += 64) assert((addr + sizeof(Aligned64) - 1) / 64 == addr / 64); int split = 0; for (uint64_t addr = 1; addr < 1024; addr += 64) split += (addr + sizeof(Unaligned64) - 1) / 64 != addr / 64; assert(split == 16 && sizeof(Aligned64) == 64 && alignof(Aligned64) == 64); }       // 정렬된 64 바이트는 1 라인
    for (uint64_t stride : {1ULL, 2ULL, 4ULL, 8ULL, 16ULL, 32ULL, 64ULL, 128ULL, 256ULL}) { std::set<uint64_t> lines; uint64_t accesses = 0; for (uint64_t a = 0; a < 4096; a += stride) { lines.insert(g.lineOf(a)); ++accesses; }          // ③ 보폭
        uint64_t expect = std::min<uint64_t>(4096 / 64, (4096 + stride - 1) / stride); assert(lines.size() == expect); double utilization = (double)std::min<uint64_t>(4, stride) / (double)std::min<uint64_t>(stride, 64); if (stride >= 64) assert(accesses == lines.size()); (void)utilization; }
    int bad = 0; for (auto sizes : std::vector<std::vector<uint64_t>>{{1000, 64, 8}, {1024, 48, 4}, {4096, 64, 3}, {32, 64, 1}}) { try { Geometry x(sizes[0], sizes[1], sizes[2]); (void)x; } catch (const std::invalid_argument&) { ++bad; } } assert(bad == 4);                    // ④
#if defined(__linux__) && defined(_SC_LEVEL1_DCACHE_LINESIZE)
    long hw = sysconf(_SC_LEVEL1_DCACHE_LINESIZE); if (hw > 0) assert((hw & (hw - 1)) == 0 && hw >= 16 && hw <= 256);
    std::cout << "CacheLine: this machine reports an L1 line size of " << hw << " bytes; ";
#endif
    std::cout << "address decomposition [tag|set|offset] round-tripped for 10^5 random addresses on a 32 KB 8-way geometry, line counts of ranges matched set counting, straddling objects/alignment/stride patterns matched their formulas, and invalid geometries were rejected" << std::endl;
    return 0;
}
// Time Complexity: O(1) 주소 분해
// Space Complexity: O(1)
```
## CacheHit()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 캐시 적중(hit): 요청한 라인이 이미 캐시에 있음.  N-way 세트 연관 캐시를 LRU 로 흉내 낸다.  작업 집합(working set)이 캐시에 들어가면 첫 번째 순회 이후로는 거의 모두 적중한다.
//  미스는 세 가지다 — compulsory(처음 보는 라인), capacity(전체 용량 부족), conflict(용량은 충분한데 같은 세트에 몰려서).  conflict = "같은 크기의 완전 연관 캐시라면 적중했을 미스".
//  ① 시뮬레이터 검증: 극단 설정에서 독립 오라클과 같다 — 직접 사상(ways = 1)은 태그 배열 모형, 완전 연관(sets = 1)은 스택 거리 모형  ② 무작위 설정(크기 1..64 KB, ways 1..8, 라인 16..128)·무작위 주소열 300 개를 세트별 최근성 벡터 오라클과 대조
//  ③ 8 KB 작업 집합을 32 KB 8-way 에서 10 번 순회: 미스는 정확히 128 개(compulsory) 뿐이고 적중률 > 99%  ④ 64 KB 작업 집합 순환 순회: LRU 는 용량보다 큰 순환 접근에서 *100% 미스*(thrashing)  ⑤ 충돌: 같은 세트에 사상되는 9 개 라인(ways = 8)을 순환하면 총 크기가 아주 작아도 100% 미스, 같은 용량 완전 연관이면 100% 적중.
struct Cache {                                                                                                 // N-way 세트 연관 LRU 캐시 시뮬레이터
    size_t sets, ways, line; std::vector<std::vector<uint64_t>> s; long hits = 0, misses = 0, compulsory = 0, conflictOrCapacity = 0; std::unordered_set<uint64_t> seen;
    Cache(size_t sizeBytes, size_t lineBytes, size_t w) : sets(sizeBytes / lineBytes / w), ways(w), line(lineBytes), s(sizeBytes / lineBytes / w) {}
    bool access(uint64_t addr) {
        uint64_t ln = addr / line; auto& set = s[ln % sets];
        for (size_t i = 0; i < set.size(); ++i) if (set[i] == ln) { set.erase(set.begin() + i); set.insert(set.begin(), ln); ++hits; return true; }         // 적중: MRU 로
        set.insert(set.begin(), ln); if (set.size() > ways) set.pop_back(); ++misses; if (seen.insert(ln).second) ++compulsory; else ++conflictOrCapacity; return false; }                       // 미스: 가장 오래 안 쓴 라인 축출
};

long stackDistanceMisses(const std::vector<uint64_t>& addrs, size_t lines, size_t lineBytes) { std::vector<uint64_t> st; long miss = 0; for (uint64_t a : addrs) { uint64_t ln = a / lineBytes; size_t i = 0; while (i < st.size() && st[i] != ln) ++i; if (i == st.size() || i >= lines) ++miss; if (i < st.size()) st.erase(st.begin() + i); st.insert(st.begin(), ln); if (st.size() > lines) st.pop_back(); } return miss; }
long directMappedMisses(const std::vector<uint64_t>& addrs, size_t sets, size_t lineBytes) { std::vector<int64_t> tags(sets, -1); long miss = 0; for (uint64_t a : addrs) { uint64_t ln = a / lineBytes; size_t idx = ln % sets; if (tags[idx] != (int64_t)ln) { ++miss; tags[idx] = (int64_t)ln; } } return miss; }
long recencyOracle(const std::vector<uint64_t>& addrs, size_t sets, size_t ways, size_t lineBytes) { std::vector<std::vector<uint64_t>> recent(sets); long miss = 0; uint64_t clock = 0; std::vector<std::vector<std::pair<uint64_t, uint64_t>>> stamped(sets);        // 마지막 사용 시각이 가장 오래된 것을 축출하는 다른 구현
    for (uint64_t a : addrs) { uint64_t ln = a / lineBytes; auto& set = stamped[ln % sets]; ++clock; bool found = false; for (auto& e : set) if (e.first == ln) { e.second = clock; found = true; } if (found) continue; ++miss;
        if (set.size() < ways) set.push_back({ln, clock}); else { size_t victim = 0; for (size_t i = 1; i < set.size(); ++i) if (set[i].second < set[victim].second) victim = i; set[victim] = {ln, clock}; } } return miss; }

int main() {
    std::mt19937_64 rng(1017);
    for (int it = 0; it < 300; ++it) { size_t line = 16u << (rng() % 4), ways = 1u << (rng() % 4), sizeBytes = line * ways * (1u << (rng() % 7)); size_t span = sizeBytes * (1 + rng() % 4); std::vector<uint64_t> addrs(500 + rng() % 1500); for (auto& a : addrs) a = rng() % span;
        Cache c(sizeBytes, line, ways); for (uint64_t a : addrs) c.access(a); assert(c.misses == recencyOracle(addrs, c.sets, ways, line) && c.hits + c.misses == (long)addrs.size());                                       // ②
        if (ways == 1) assert(c.misses == directMappedMisses(addrs, c.sets, line)); Cache full(sizeBytes, line, sizeBytes / line); for (uint64_t a : addrs) full.access(a); assert(full.misses == stackDistanceMisses(addrs, sizeBytes / line, line));            // ① 극단
        assert(full.misses <= c.misses + (long)addrs.size() && c.compulsory == full.compulsory); }
    {   Cache c(32 * 1024, 64, 8); const int bytes = 8 * 1024; for (int pass = 0; pass < 10; ++pass) for (int a = 0; a < bytes; a += 4) c.access((uint64_t)a); long total = c.hits + c.misses;                // ③
        assert(c.misses == bytes / 64 && c.compulsory == bytes / 64 && c.conflictOrCapacity == 0 && (double)c.hits / total > 0.99); }
    {   Cache c(32 * 1024, 64, 8); const int bytes = 64 * 1024; for (int pass = 0; pass < 5; ++pass) for (int a = 0; a < bytes; a += 64) c.access((uint64_t)a); assert(c.hits == 0 && c.misses == 5 * (bytes / 64)); }                           // ④ 순환 접근이 용량보다 크면 LRU 는 계속 미스
    {   Cache sa(32 * 1024, 64, 8), fa(32 * 1024, 64, 512); const uint64_t stride = 64 * sa.sets;                                                                                                              // ⑤ 같은 세트로 몰리는 보폭 = 라인 × 세트 수
        for (int pass = 0; pass < 20; ++pass) for (int k = 0; k < 9; ++k) { sa.access((uint64_t)k * stride); fa.access((uint64_t)k * stride); }
        assert(sa.hits == 0 && sa.misses == 180 && fa.misses == 9 && fa.hits == 171);                                                                                                                         // 8-way 는 전부 미스(충돌), 완전 연관은 처음 9 개뿐
        assert(sa.conflictOrCapacity == 171 && sa.compulsory == 9); }
    std::cout << "CacheHit: set-associative LRU matched independent oracles on 300 random configurations; an 8 KB working set hit 99%+ with only its 128 compulsory misses, a cyclic 64 KB sweep missed 100% (LRU thrashing), and 9 lines in one 8-way set missed every time while a fully associative cache of the same size hit all but 9" << std::endl;
    return 0;
}
// Time Complexity: 접근 O(ways)
// Space Complexity: O(캐시 라인 수)
```
## CacheMiss()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <set>
#include <vector>

// 캐시 미스의 3C 분류:
//  Compulsory(강제): 처음 접근하는 라인 (캐시가 아무리 커도 발생)
//  Capacity(용량): 작업 집합이 캐시보다 커서 (같은 크기의 완전 연관 캐시도 미스)
//  Conflict(충돌): 여러 라인이 같은 세트에 몰려 (완전 연관 캐시라면 적중했을 것)
// 이 예제는 세트 연관 LRU 캐시 시뮬레이터에 3C 분류를 붙이고, 독립된 방법으로 대조한다:
//  ① Mattson 스택 거리: 완전 연관 LRU 캐시(용량 C 라인)의 미스 수 == (처음 접근 + 스택 거리 > C 인 접근 수).  거리를 O(n²) 정의대로 구한 것과 Fenwick 트리 O(n log n) 로 구한 것이 같고, 시뮬레이터가 모든 C 에서 이 값과 일치
//  ② 분류 항등식: 총 미스 = 강제 + 용량 + 충돌, 강제 = 서로 다른 라인 수, 용량 + 강제 = 같은 크기 완전 연관 캐시의 미스
//  ③ 행렬 순회(256 x 256 int, 캐시 32KB·8방향·64B 라인): 행 우선은 미스가 정확히 N²/16 = 4096 (강제만), 열 우선은 행 간격이 1024B(16 라인)라 세트 4 개에만 몰려 정확히 N² = 65536 번 모두 미스 — 완전 연관이면 들어가는데도 충돌 미스.
//        행에 패딩(+16 int)을 넣으면 세트가 고루 퍼져 다시 강제 미스 4096 만 남는다.  전치 연산은 16 x 16 타일로 쪼개면 N²/16 · 2 = 8192 (강제만)
//  ④ 순차 스캔의 미스 수 == 바이트 수 / 라인 크기, 직접 사상 vs 4방향(원래 예)
struct Cache {
    size_t sets, ways, lineBytes; std::vector<std::list<uint64_t>> s; long misses = 0, accesses = 0;
    Cache(size_t numLines, size_t w, size_t line = 64) : sets(numLines / w), ways(w), lineBytes(line), s(numLines / w) {}
    bool accessLine(uint64_t line) {
        ++accesses; auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); return true; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); ++misses; return false;
    }
    bool access(uint64_t byteAddr) { return accessLine(byteAddr / lineBytes); }
};
struct Result { long compulsory = 0, capacity = 0, conflict = 0; long total() const { return compulsory + capacity + conflict; } };
Result classify(size_t numLines, size_t ways, const std::vector<uint64_t>& lines) {
    Cache real(numLines, ways), full(numLines, numLines); std::set<uint64_t> seen; Result r;       // 실제 캐시 vs 같은 크기의 완전 연관 캐시
    for (uint64_t line : lines) {
        bool hit = real.accessLine(line), fullHit = full.accessLine(line);
        if (!hit) { if (!seen.count(line)) r.compulsory++; else if (!fullHit) r.capacity++; else r.conflict++; }
        seen.insert(line);
    }
    return r;
}
std::vector<long> stackDistancesNaive(const std::vector<uint64_t>& t) {                         // 정의 그대로: 직전 접근 이후 서로 다른 라인의 수 + 1 (처음이면 0 = 무한대)
    std::vector<long> d(t.size(), 0); std::map<uint64_t, size_t> last;
    for (size_t i = 0; i < t.size(); ++i) { auto it = last.find(t[i]); if (it != last.end()) { std::set<uint64_t> distinct(t.begin() + it->second + 1, t.begin() + i); distinct.erase(t[i]); d[i] = (long)distinct.size() + 1; } last[t[i]] = i; }
    return d;
}
struct Fenwick { std::vector<long> f; explicit Fenwick(size_t n) : f(n + 1, 0) {} void add(size_t i, long v) { for (++i; i < f.size(); i += i & -i) f[i] += v; } long sum(size_t i) const { long s = 0; for (++i; i > 0; i -= i & -i) s += f[i]; return s; } };
std::vector<long> stackDistancesFast(const std::vector<uint64_t>& t) {                           // 마지막 접근 위치만 1 로 두는 Fenwick 트리
    std::vector<long> d(t.size(), 0); std::map<uint64_t, size_t> last; Fenwick fw(t.size());
    for (size_t i = 0; i < t.size(); ++i) { auto it = last.find(t[i]); if (it != last.end()) { d[i] = fw.sum(i) - fw.sum(it->second) + 1; fw.add(it->second, -1); } fw.add(i, 1); last[t[i]] = i; }
    return d;
}

// 행렬 접근 시뮬레이션 (원소 4바이트)
long matrixMisses(const char* mode, size_t N, size_t rowStrideInts, size_t tile = 16) {
    Cache c(512, 8); auto addr = [&](size_t base, size_t i, size_t j) { return base + (i * rowStrideInts + j) * 4; };
    if (mode[0] == 'r') { for (size_t i = 0; i < N; ++i) for (size_t j = 0; j < N; ++j) c.access(addr(0, i, j)); }                                   // 행 우선 읽기
    else if (mode[0] == 'c') { for (size_t j = 0; j < N; ++j) for (size_t i = 0; i < N; ++i) c.access(addr(0, i, j)); }                             // 열 우선 읽기
    else if (mode[0] == 'n') { const size_t B = 1 << 24; for (size_t i = 0; i < N; ++i) for (size_t j = 0; j < N; ++j) { c.access(addr(0, i, j)); c.access(addr(B, j, i)); } }                         // 전치(B[j][i] = A[i][j]), 단순
    else { const size_t B = 1 << 24; for (size_t ii = 0; ii < N; ii += tile) for (size_t jj = 0; jj < N; jj += tile) for (size_t i = ii; i < ii + tile; ++i) for (size_t j = jj; j < jj + tile; ++j) { c.access(addr(0, i, j)); c.access(addr(B, j, i)); } }   // 타일
    return c.misses;
}

int main() {
    // 원래 예: 64 라인 캐시에서 직접 사상 vs 4방향
    {   const size_t numLines = 64; std::vector<uint64_t> trace; for (int rep = 0; rep < 50; rep++) for (int k = 0; k < 4; k++) trace.push_back(64ULL * k);        // 라인 0, 64, 128, 192: 직접 사상이면 모두 세트 0
        Result direct = classify(numLines, 1, trace), assoc = classify(numLines, 4, trace);
        assert(direct.compulsory == 4 && direct.capacity == 0 && direct.conflict == 196 && direct.total() == 200);                                         // 라인 4 개뿐인데 전부 충돌 미스
        assert(assoc.conflict == 0 && assoc.compulsory == 4 && assoc.total() == 4);
        std::vector<uint64_t> big; for (int rep = 0; rep < 3; rep++) for (uint64_t l = 0; l < 128; l++) big.push_back(l);                                 // 128 라인 순환: 용량 초과
        Result cap = classify(numLines, 8, big); assert(cap.compulsory == 128 && cap.capacity == 256 && cap.conflict == 0); }
    // ①② 스택 거리와 3C
    std::mt19937 rng(11); long checkedTraces = 0, conflictMisses = 0, capacityMisses = 0;
    for (int it = 0; it < 60; ++it) {
        size_t universe = 8 + rng() % 120, len = 200 + rng() % 600; std::vector<uint64_t> tr(len);
        for (auto& x : tr) x = (rng() % 4 == 0) ? rng() % universe : rng() % std::max<size_t>(2, universe / 6);                                           // 지역성이 있는 무작위 트레이스
        auto dn = stackDistancesNaive(tr), df = stackDistancesFast(tr); assert(dn == df);
        std::set<uint64_t> distinct(tr.begin(), tr.end());
        for (size_t C : {(size_t)1, (size_t)2, (size_t)4, (size_t)8, (size_t)16, (size_t)32, (size_t)64}) {
            long byDistance = 0; for (long d : df) byDistance += (d == 0 || d > (long)C);
            Cache fa(C, C); for (uint64_t l : tr) fa.accessLine(l); assert(fa.misses == byDistance);                                                      // 완전 연관 LRU 미스 == 거리 > C 인 접근 + 처음 접근
        }
        for (size_t ways : {(size_t)1, (size_t)2, (size_t)4}) {
            Result r = classify(32, ways, tr); Cache real(32, ways); for (uint64_t l : tr) real.accessLine(l);
            Cache full(32, 32); for (uint64_t l : tr) full.accessLine(l);
            assert(r.total() == real.misses && r.compulsory == (long)distinct.size());                                                                    // 총 미스 = 강제 + 용량 + 충돌, 강제 = 서로 다른 라인 수
            assert(r.compulsory + r.capacity <= full.misses);                                                                                              // 강제 + 용량 미스는 모두 같은 크기 완전 연관 캐시의 미스이기도 하다
            conflictMisses += r.conflict; capacityMisses += r.capacity;
        }
        ++checkedTraces;
    }
    assert(conflictMisses > 100 && capacityMisses > 100);
    // ③ 행렬 순회
    const size_t N = 256;
    assert(matrixMisses("row", N, N) == (long)(N * N / 16));                                                                                              // 행 우선: 강제 미스만
    assert(matrixMisses("col", N, N) == (long)(N * N));                                                                                                   // 열 우선(행 간격 1024B): 모두 미스
    {   std::vector<uint64_t> lines; for (size_t j = 0; j < N; ++j) for (size_t i = 0; i < N; ++i) lines.push_back((i * N + j) * 4 / 64);                    // 같은 접근열을 3C 로 분류
        Result r = classify(512, 8, lines); assert(r.compulsory == 4096 && r.capacity == 0 && r.conflict == (long)(N * N - 4096)); }                       // 완전 연관이면 256 라인이 512 라인에 다 들어간다 -> 나머지는 전부 충돌 미스
    assert(matrixMisses("col", N, N + 16) == (long)(N * N / 16));                                                                                         // 행 길이에 한 라인(16 int) 패딩 -> 세트가 퍼져 강제 미스만
    long naive = matrixMisses("naive", N, N), tiled = matrixMisses("tiled", N, N);
    assert(tiled == (long)(2 * N * N / 16) && naive > 8 * tiled);                                                                                         // 타일: 읽기·쓰기 각각 강제 미스만
    // ④ 순차 스캔
    for (size_t line : {(size_t)16, (size_t)32, (size_t)64, (size_t)128}) { Cache c(1024, 4, line); const size_t bytes = 1 << 20; for (size_t a = 0; a < bytes; a += 4) c.access(a); assert(c.misses == (long)(bytes / line)); }
    std::cout << "CacheMiss verified: " << checkedTraces << " traces (stack distances naive == Fenwick, fully-associative misses match Mattson), column-major 256x256: " << matrixMisses("col", N, N) << " misses vs "
              << matrixMisses("col", N, N + 16) << " with padding, transpose " << naive << " vs tiled " << tiled << "." << std::endl;
    return 0;
}
// Time Complexity: 시뮬레이션 O(접근 수 · 방향 수), 스택 거리 O(n log n) (Fenwick)
// Space Complexity: O(캐시 라인 수)
```
## CacheFriendlyTraversal()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <unordered_set>
#include <vector>

// audit: closed-form (캐시 시뮬레이터의 미스 수를 N²/16, N² 같은 닫힌 식과 임계 보폭 이론으로 대조)
// 2차원 배열은 메모리에서 행 우선(row-major)으로 놓인다: a[i][j] 의 주소 = base + (i·N + j)·4.  행 순서로 훑으면 연속 주소라 라인당 16 개가 적중하지만, 열 순서로 훑으면 한 번 접근할 때마다 N·4 바이트씩 건너뛰어 매번 다른 라인 → 미스 폭증.
//  열 순회의 미스는 N 에 *매우 민감하다*: 보폭 N·4 바이트가 (라인 × 세트 수)의 약수에 가까우면 열의 원소들이 몇 안 되는 세트로 몰려 용량이 충분해도 서로 쫓아낸다(임계 보폭, critical stride).  행을 한 칸 더 길게(패딩) 잡으면 풀린다.
//  ① 행 순서의 미스 = N²/16 (컴펄서리뿐)  ② 같은 배열을 열 순서로 훑으면 N = 512(보폭 2048 B → 세트 64 개 중 2 개만 사용)에서 미스 N² 개 — 행 순서의 16 배  ③ 행을 한 칸(513)만 늘려도 미스가 줄고, 8 칸(520, 32 바이트)이면 행 순서와 거의 같다
//  ④ 타일(블록) 순회 T = 16 은 행 순서와 같은 N²/16 미스 + 가장자리 약간  ⑤ N = 64 처럼 한 열이 캐시에 들어가면 열 순서도 컴펄서리 미스뿐(N²/16)이다  ⑥ 임계 보폭 이론: N 이 16 의 배수이면 열의 원소 사이 라인 간격 N/16 이 쓰는 세트 수는 64/gcd(N/16, 64) 개뿐이므로, 원소가 가장 적게 몰린 세트도 ways + 1 = 9 개 이상(⌊N / 세트 수⌋ ≥ 9)인 모든 N(16..640)에서 열 순회는 *접근마다* 미스다 — 세트마다 순환 접근이 ways 를 넘어 LRU 가 계속 쫓아낸다.
struct Cache {                                                                                                 // N-way 세트 연관 LRU 캐시 시뮬레이터
    size_t sets, ways, line; std::vector<std::vector<uint64_t>> s; long hits = 0, misses = 0;
    Cache(size_t sizeBytes, size_t lineBytes, size_t w) : sets(sizeBytes / lineBytes / w), ways(w), line(lineBytes), s(sizeBytes / lineBytes / w) {}
    bool access(uint64_t addr) {
        uint64_t ln = addr / line; auto& set = s[ln % sets];
        for (size_t i = 0; i < set.size(); ++i) if (set[i] == ln) { set.erase(set.begin() + i); set.insert(set.begin(), ln); ++hits; return true; }         // 적중: MRU 로
        set.insert(set.begin(), ln); if (set.size() > ways) set.pop_back(); ++misses; return false; }                       // 미스: 가장 오래 안 쓴 라인 축출
};

long rowOrder(int N, size_t pitch) { Cache c(32 * 1024, 64, 8); for (int i = 0; i < N; ++i) for (int j = 0; j < N; ++j) c.access(((uint64_t)i * pitch + j) * 4); return c.misses; }
long colOrder(int N, size_t pitch) { Cache c(32 * 1024, 64, 8); for (int j = 0; j < N; ++j) for (int i = 0; i < N; ++i) c.access(((uint64_t)i * pitch + j) * 4); return c.misses; }
long tiled(int N, size_t pitch, int T) { Cache c(32 * 1024, 64, 8); for (int ii = 0; ii < N; ii += T) for (int jj = 0; jj < N; jj += T) for (int i = ii; i < std::min(N, ii + T); ++i) for (int j = jj; j < std::min(N, jj + T); ++j) c.access(((uint64_t)i * pitch + j) * 4); return c.misses; }

int main() {
    const int N = 512;                                                                                           // 512 × 512 ints = 1 MB (캐시 32 KB 보다 훨씬 큼)
    long row = rowOrder(N, N), col = colOrder(N, N); assert(row == (long)N * N / 16);                            // ① 라인당 16 개 → N²/16
    assert(col == (long)N * N && col == 16 * row);                                                               // ② 열 순회: 모든 접근이 미스
    long col513 = colOrder(N, N + 1), col520 = colOrder(N, N + 8); assert(col513 < col && col520 * 10 < col && col520 <= row + row / 20);                       // ③ 패딩 1 칸은 절반으로, 8 칸(32 바이트)이면 행 순서와 거의 같아진다
    long t16 = tiled(N, N, 16); assert(t16 >= row && t16 <= row + (long)N * 2);                                  // ④ 타일 T = 16 (한 타일 = 16 라인 × 16 행 → 용량 안)
    assert(colOrder(64, 64) == (long)64 * 64 / 16 && rowOrder(64, 64) == (long)64 * 64 / 16);                    // ⑤ 열이 캐시에 들어가면 열 순서도 컴펄서리 미스뿐
    int predicted = 0; for (int n = 16; n <= 640; n += 16) { int stepLines = n / 16, g = stepLines, h = 64; while (h) { int t = g % h; g = h; h = t; } int distinctSets = 64 / g; if (n / distinctSets >= 9) { ++predicted; assert(colOrder(n, n) == (long)n * n); } }          // ⑥ 임계 보폭 이론: 열의 원소가 쓰는 세트 수 × 8 < N 이면 *모든* 접근이 미스
    assert(predicted >= 15);
    std::cout << "CacheFriendlyTraversal (32 KB 8-way, 64 B lines, N=512): row order " << row << " misses (N^2/16), column order " << col << " (every access, " << col / row << "x), padded pitch 513/520: " << col513 << "/" << col520 << ", 16x16 tiles: " << t16 << "; the critical-stride rule (every used set receives at least 9 column lines) predicted all-miss column sweeps for " << predicted << " sizes, and each one missed on every access" << std::endl;
    return 0;
}
// Time Complexity: O(N²) 접근, 미스 수가 다르다
// Space Complexity: O(1)
```
## CacheBlocking()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <list>
#include <vector>
#include <cassert>

// 캐시 블로킹(타일링): 큰 행렬을 캐시에 들어가는 작은 타일로 나눠 타일 안에서 최대한 재사용한다.
// 행렬 곱 C = A·B 를 단순하게 쓰면 B 를 열 방향으로 훑어 캐시를 계속 밀어내지만, B×B 타일로 나누면 타일 하나가 캐시에 머무는 동안 B·B·B 번의 연산을 한다
struct Cache {
    size_t sets, ways; std::vector<std::list<uint64_t>> s; long misses = 0;
    Cache(size_t bytes, size_t w) : sets(bytes / 64 / w), ways(w), s(bytes / 64 / w) {}
    void access(uint64_t addr) {
        uint64_t line = addr / 64; auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); return; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); misses++;
    }
};
const int N = 96;
const uint64_t A_BASE = 0, B_BASE = 1 << 20, C_BASE = 2 << 20;
inline uint64_t at(uint64_t base, int i, int j) { return base + ((uint64_t)i * N + j) * 4; }

int main() {
    std::vector<int> A(N * N), B(N * N), Cn(N * N, 0), Cb(N * N, 0);
    for (int i = 0; i < N * N; i++) { A[i] = i % 7; B[i] = (i * 3) % 5; }
    Cache naive(8 * 1024, 4), blocked(8 * 1024, 4);                  // 작은 캐시(8KB)로 차이를 크게 본다
    for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) for (int k = 0; k < N; k++) {
        naive.access(at(A_BASE, i, k)); naive.access(at(B_BASE, k, j)); naive.access(at(C_BASE, i, j));
        Cn[i * N + j] += A[i * N + k] * B[k * N + j];
    }
    const int T = 16;                                                // 타일 16x16 ints = 1KB, 세 타일이 캐시에 들어감
    for (int ii = 0; ii < N; ii += T) for (int jj = 0; jj < N; jj += T) for (int kk = 0; kk < N; kk += T)
        for (int i = ii; i < std::min(ii + T, N); i++) for (int j = jj; j < std::min(jj + T, N); j++) for (int k = kk; k < std::min(kk + T, N); k++) {
            blocked.access(at(A_BASE, i, k)); blocked.access(at(B_BASE, k, j)); blocked.access(at(C_BASE, i, j));
            Cb[i * N + j] += A[i * N + k] * B[k * N + j];
        }
    assert(Cn == Cb);                                                // 계산 결과는 동일
    assert(blocked.misses * 2 < naive.misses);                       // 블로킹이 미스를 절반 이하로 줄인다
    std::cout << "misses: naive=" << naive.misses << " blocked=" << blocked.misses << std::endl;
    return 0;
}
// Time Complexity: O(N³) 연산은 동일, 캐시 미스는 O(N³/ (B·L)) 로 감소
// Space Complexity: O(1)
```
## FalseSharing()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <new>
#include <random>
#include <thread>
#include <unordered_map>
#include <vector>

// 거짓 공유(false sharing): 서로 다른 스레드가 쓰는 "서로 다른 변수" 가 같은 캐시 라인에 있으면, 한 코어가 쓸 때마다 다른 코어의 라인 사본이 무효화되어 라인이 코어 사이를 왔다 갔다 한다.
//  논리적으로는 공유가 없는데 성능이 몇 배 떨어진다.  해결: 변수를 캐시 라인 경계에 맞춰 띄운다 (alignas(64)).  시간 측정은 기계마다 흔들리므로 *결정적인 계수*로 증명한다: 최소 MESI(Invalid / Shared / Modified) 일관성 시뮬레이터가 코어별 라인 상태를 갱신하며 "일관성 미스"(쓰려는데 내 사본이 M 이 아님)를 센다.
//  ① 코어 둘이 번갈아 자기 카운터를 쓸 때, 두 카운터가 한 라인에 있으면 *쓰기마다* 미스(2N 회), 라인을 나누면 처음 한 번씩(2 회)  ② 코어 8 개가 8 바이트 슬롯 배열(한 라인에 8 개)을 쓰면 슬롯을 라인마다 하나로 띄운 배열에 비해 미스가 N 배 이상  ③ 무작위 쓰기 일정 3000 개: 시뮬레이터의 미스 수 = 독립 오라클(직전에 그 라인을 건드린 코어가 다르면 미스)
//  ④ 읽기가 끼면 M → S 강등으로 다음 쓰기가 다시 미스  ⑤ 실제 스레드 2 개: 두 구조 모두 결과는 정확하고, 주소로 같은 라인/다른 라인임을 확인(시간은 출력만).
struct Coherence {
    int cores; std::vector<std::unordered_map<uint64_t, char>> st; long writeMisses = 0, readMisses = 0, invalidations = 0;
    explicit Coherence(int c) : cores(c), st(c) {}
    char state(int core, uint64_t line) const { auto it = st[core].find(line); return it == st[core].end() ? 'I' : it->second; }
    void write(int core, uint64_t addr) { uint64_t line = addr / 64; if (state(core, line) == 'M') return; ++writeMisses;                                            // M 이 아니면 일관성 미스
        for (int c = 0; c < cores; ++c) if (c != core && state(c, line) != 'I') { st[c][line] = 'I'; ++invalidations; } st[core][line] = 'M'; }                            // 다른 코어의 사본 무효화
    void read(int core, uint64_t addr) { uint64_t line = addr / 64; if (state(core, line) != 'I') return; ++readMisses; for (int c = 0; c < cores; ++c) if (c != core && state(c, line) == 'M') st[c][line] = 'S'; st[core][line] = 'S'; }      // M 을 가진 코어는 S 로 강등
};
struct Packed { std::atomic<long> a{0}; std::atomic<long> b{0}; };                                             // 같은 라인
struct Padded { alignas(64) std::atomic<long> a{0}; alignas(64) std::atomic<long> b{0}; };                    // 다른 라인
template <class T> double run(T& c, long iters) { auto t0 = std::chrono::steady_clock::now();
    std::thread t1([&] { for (long i = 0; i < iters; ++i) c.a.fetch_add(1, std::memory_order_relaxed); }); std::thread t2([&] { for (long i = 0; i < iters; ++i) c.b.fetch_add(1, std::memory_order_relaxed); }); t1.join(); t2.join();
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count(); }
bool sameLine(const void* x, const void* y) { return (uintptr_t)x / 64 == (uintptr_t)y / 64; }

int main() {
    const int N = 5000;
    {   Coherence same(2), apart(2); for (int i = 0; i < N; ++i) for (int core = 0; core < 2; ++core) { same.write(core, 0 + 8 * core); apart.write(core, 0 + 64 * core); }                 // ① 번갈아 쓰기
        assert(same.writeMisses == 2 * N && apart.writeMisses == 2 && same.invalidations == 2 * N - 1 && apart.invalidations == 0); }
    {   const int cores = 8; Coherence packed(cores), spread(cores); for (int i = 0; i < N; ++i) for (int c = 0; c < cores; ++c) { packed.write(c, 8 * (uint64_t)c); spread.write(c, 64 * (uint64_t)c); }                  // ② 슬롯 배열
        assert(packed.writeMisses == (long)cores * N && spread.writeMisses == cores && packed.writeMisses >= N * spread.writeMisses / 2); }
    std::mt19937 rng(1019);
    for (int it = 0; it < 3000; ++it) { int cores = 1 + (int)(rng() % 6); Coherence co(cores); std::unordered_map<uint64_t, int> lastTouch; long expect = 0; int ops = 1 + (int)(rng() % 60);                       // ③ 오라클: 직전 접근 코어가 나와 다르면 미스
        for (int k = 0; k < ops; ++k) { int core = (int)(rng() % cores); uint64_t addr = (rng() % 4) * 64 + (rng() % 8) * 8; uint64_t line = addr / 64; auto prev = lastTouch.find(line); if (prev == lastTouch.end() || prev->second != core) ++expect; lastTouch[line] = core; co.write(core, addr); }
        assert(co.writeMisses == expect); }
    {   Coherence co(2); co.write(0, 0); assert(co.state(0, 0) == 'M'); co.read(1, 8); assert(co.state(0, 0) == 'S' && co.state(1, 0) == 'S' && co.readMisses == 1);                                           // ④ 읽기: M → S
        long before = co.writeMisses; co.write(0, 0); assert(co.writeMisses == before + 1 && co.state(1, 0) == 'I' && co.state(0, 0) == 'M'); co.write(0, 0); assert(co.writeMisses == before + 1); }                                // S → M 은 다시 미스, 이어지는 M 쓰기는 적중
    Packed packed; Padded padded; assert(sameLine(&packed.a, &packed.b) && !sameLine(&padded.a, &padded.b) && alignof(Padded) >= 64);                                                                        // ⑤
    const long iters = 2000000; double tPacked = run(packed, iters), tPadded = run(padded, iters); assert(packed.a == iters && packed.b == iters && padded.a == iters && padded.b == iters);
#ifdef __cpp_lib_hardware_interference_size
    assert(std::hardware_destructive_interference_size >= 32);
#endif
    std::cout << "FalseSharing: a MESI simulator counted " << 2 * N << " coherence misses for two counters on one line versus 2 for separate lines (and 8N versus 8 for eight cores), matched an independent oracle on 3000 random write schedules, and real threads gave exact totals (packed " << tPacked << " ms, padded " << tPadded << " ms; timing varies by machine)" << std::endl;
    return 0;
}
// Time Complexity: O(iters)
// Space Complexity: 패딩으로 캐시 라인 하나씩 낭비
```
# Part 9. 가상 메모리
## VirtualAddress()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>

// 가상 주소(x86-64, 4단계 페이징): 64비트 중 하위 48비트만 쓰고 [47:0] 을 9+9+9+9+12 비트로 나눈다.
//   [47:39] PML4 인덱스  [38:30] PDPT 인덱스  [29:21] PD 인덱스  [20:12] PT 인덱스  [11:0] 페이지 내 오프셋(4KB)
// 상위 16비트는 비트 47 의 복사여야 하는 "정규(canonical) 주소" 만 유효하다: 낮은 절반은 사용자, 높은 절반은 커널
// 이 예제는 위 주장을 서로 다른 방법으로 대조한다:
//  ① 비트 연산으로 쪼갠 필드 == 나눗셈/나머지로 구한 필드, 다시 합치면(부호 확장 포함) 원래 정규 주소, 쪼개기는 정규 주소 위에서 일대일(서로 다른 주소가 같은 (인덱스 4 개, 오프셋) 을 갖지 않는다)
//  ② 정규 주소 판정 == "상위 17비트가 모두 같다" 라는 정의 == 부호 확장 후 같은지 == 구간 판정 [0, 2^47) ∪ [2^64-2^47, 2^64)
//  ③ 축소 모형(워드 16비트, 주소 비트 8~12)에서 전수 조사: 정규 주소의 개수가 정확히 2^(주소 비트), 구멍(비정규)의 크기는 2^16 - 2^(주소 비트)
//  ④ 5단계 페이징(57비트)은 PML5 인덱스 [56:48] 이 추가되고, 48비트 정규 주소는 57비트에서도 정규(포함 관계), 반대는 성립하지 않는다  ⑤ 이 프로세스의 실제 포인터(스택·힙·코드)가 사용자 절반의 정규 주소 (x86-64 에서)
struct Split { unsigned pml4, pdpt, pd, pt, offset; };
Split split(uint64_t va) { return {unsigned(va >> 39 & 0x1ff), unsigned(va >> 30 & 0x1ff), unsigned(va >> 21 & 0x1ff), unsigned(va >> 12 & 0x1ff), unsigned(va & 0xfff)}; }
uint64_t signExtend(uint64_t va, int bits) {                                       // 하위 bits 비트를 부호 확장
    uint64_t mask = (bits == 64) ? ~0ULL : ((1ULL << bits) - 1), low = va & mask;
    return (low >> (bits - 1) & 1) ? (low | ~mask) : low;
}
uint64_t compose(const Split& s) { return signExtend((uint64_t)s.pml4 << 39 | (uint64_t)s.pdpt << 30 | (uint64_t)s.pd << 21 | (uint64_t)s.pt << 12 | s.offset, 48); }
bool canonical(uint64_t va, int bits = 48) { return signExtend(va, bits) == va; }

int main() {
    uint64_t va = 0x00007f1234567abcULL; Split s = split(va);
    assert(s.offset == 0xabc && s.pt == 0x167 && s.pd == 0x1a2 && s.pdpt == 0x48 && s.pml4 == 0xfe);
    assert(compose(s) == va);
    assert(canonical(va) && canonical(0xffff800000000000ULL));                        // 사용자 영역 끝, 커널 영역 시작
    assert(!canonical(0x0000800000000000ULL) && !canonical(0x1234000000000000ULL));
    // ① 두 가지 방법과 일대일
    std::mt19937_64 rng(48); long checked = 0, canon = 0;
    for (int i = 0; i < 2000000; ++i) {
        uint64_t x = rng(); if (i % 3 == 0) x = signExtend(x, 48);                    // 정규 주소를 충분히 섞는다
        Split a = split(x);
        assert(a.offset == x % 4096 && a.pt == (x / 4096) % 512 && a.pd == (x / (4096ULL * 512)) % 512 && a.pdpt == (x / (4096ULL * 512 * 512)) % 512 && a.pml4 == (x / (4096ULL * 512 * 512 * 512)) % 512);
        if (canonical(x)) { assert(compose(a) == x); ++canon; }                         // 정규 주소는 쪼갰다 합치면 원래 주소 -> 쪼개기가 일대일
        else assert(compose(a) != x);                                                  // 비정규 주소는 합쳐도 돌아오지 않는다
        // ② 정규 주소 판정을 세 가지로
        uint64_t top = x >> 47; bool byTop = (top == 0 || top == 0x1ffff);
        bool byRange = (x < (1ULL << 47)) || (x >= (~0ULL - (1ULL << 47) + 1));
        assert(canonical(x) == byTop && byTop == byRange);
        ++checked;
    }
    assert(canon > 600000);
    // ③ 축소 모형 전수 조사: 워드 16비트
    for (int vaBits = 8; vaBits <= 12; ++vaBits) {
        long count = 0, lowHalf = 0, highHalf = 0, hole = 0;
        for (uint32_t x = 0; x < 65536; ++x) {
            uint32_t m = (1u << vaBits) - 1, low = x & m; uint32_t ext = (low >> (vaBits - 1) & 1) ? (low | (0xffffu & ~m)) : low;
            bool ok = (ext == x); count += ok; if (ok && x < (1u << (vaBits - 1))) ++lowHalf; if (ok && x >= 65536 - (1u << (vaBits - 1))) ++highHalf; hole += !ok;
        }
        assert(count == (1L << vaBits) && lowHalf == (1L << (vaBits - 1)) && highHalf == (1L << (vaBits - 1)) && hole == 65536 - (1L << vaBits));
    }
    // ④ 5단계 페이징
    for (int i = 0; i < 200000; ++i) {
        uint64_t x = signExtend(rng(), 48);
        assert(canonical(x, 57) && canonical(x, 48));                                   // 48 비트 정규 주소는 57 비트에서도 정규
        uint64_t y = signExtend(rng(), 57); uint64_t mid = y >> 47 & 0x3ff;                // 57 비트 정규 주소의 비트 [56:47]
        assert(canonical(y, 57) && canonical(y, 48) == (mid == 0 || mid == 0x3ff));          // 48 비트에서도 정규일 조건: 그 10 비트가 모두 같다 (PML5 인덱스 + 비트 47)
    }
    assert(canonical(0x0000800000000000ULL, 57) && !canonical(0x0000800000000000ULL, 48));   // 2^47: 5단계에서는 사용자 영역, 4단계에서는 비정규
    assert(canonical(0xff00000000000000ULL, 57) && !canonical(0xff00000000000000ULL, 48) && !canonical(0x0100000000000000ULL, 57));   // 2^56 은 57비트에서도 비정규
    assert(512ULL * 512 * 512 * 512 * 4096 == (1ULL << 48) && 512ULL * 512 * 512 * 512 * 512 * 4096 == (1ULL << 57));          // 인덱스 4개(5개) × 오프셋 = 주소 공간 크기
#if defined(__x86_64__)
    int local = 0; int* heap = new int(1);                                            // ⑤ 실제 포인터
    uint64_t addrs[3] = {(uint64_t)&local, (uint64_t)heap, (uint64_t)(void*)&main};
    for (uint64_t a : addrs) assert(canonical(a) && a < (1ULL << 47));                // 사용자 포인터는 낮은 절반
    delete heap;
#endif
    std::cout << "VirtualAddress verified on " << checked << " addresses (" << canon << " canonical): 0x" << std::hex << va << " -> pml4=" << s.pml4 << " pdpt=" << s.pdpt << " pd=" << s.pd << " pt=" << s.pt << " off=" << s.offset << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PhysicalAddress()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 물리 주소: 실제 RAM 의 번호.  물리 메모리는 4KB "프레임" 으로 나뉘고, 운영체제는 프레임 비트맵(또는 버디 할당기)으로 빈 프레임을 관리한다.
// 물리 주소 = 프레임 번호 << 12 | 페이지 내 오프셋.  여러 프로세스가 같은 프레임을 공유할 수 있어(공유 라이브러리, CoW) 프레임마다 참조 횟수를 둔다
// 이 구현은 64 비트 워드 비트맵(1 = 사용 중)과 프레임별 참조 횟수를 함께 두고, 빈 프레임 찾기를 워드 단위 `ctz` 로 가속한다(64 프레임을 한 번에 건너뜀).
//  alloc 은 가장 낮은 빈 프레임, allocContiguous(n, align) 는 정렬된 n 개 연속 프레임(DMA·큰 페이지용)의 가장 낮은 시작점을 돌려준다.  release 는 마지막 참조가 사라질 때만 프레임을 비운다
// 검증: 프레임 수 3 가지(200, 1000, 4096) × 무작위 연산 30 000 번(alloc, 연속 할당, share, release) 을 "참조 횟수 배열만 쓰는 느린 기준" 과 결과·상태까지 대조 — 반환 프레임이 같고, 빈 프레임 수가 같고,
//        비트맵 == (참조 횟수 > 0), 모든 공유가 사라지면 정확히 비워짐.  단편화: 512 프레임마다 하나씩만 쓰고 있으면 99.8% 가 비어도 정렬된 512 연속 할당은 실패하다가, 그 점유를 풀어 주면 성공
class FrameAllocator {
    std::vector<uint64_t> bits; std::vector<uint16_t> refs; size_t n, freeCount;
    bool used(size_t f) const { return bits[f >> 6] >> (f & 63) & 1; }
public:
    explicit FrameAllocator(size_t frames) : bits((frames + 63) / 64, 0), refs(frames, 0), n(frames), freeCount(frames) {
        if (frames % 64) bits.back() |= ~0ULL << (frames % 64);                     // 존재하지 않는 프레임은 사용 중으로 막아 둔다
    }
    long alloc() {
        for (size_t w = 0; w < bits.size(); ++w) {
            if (bits[w] == ~0ULL) continue;                                        // 64 프레임이 모두 사용 중이면 한 번에 건너뛴다
            size_t f = w * 64 + (size_t)__builtin_ctzll(~bits[w]); refs[f] = 1; bits[w] |= 1ULL << (f & 63); --freeCount; return (long)f;
        }
        return -1;
    }
    long allocContiguous(size_t count, size_t align) {                             // 정렬된 연속 count 프레임 (처음 맞는 곳)
        for (size_t s = 0; s + count <= n; s += align) {
            bool ok = true; for (size_t i = 0; i < count && ok; ++i) ok = !used(s + i);
            if (!ok) continue;
            for (size_t i = 0; i < count; ++i) { refs[s + i] = 1; bits[(s + i) >> 6] |= 1ULL << ((s + i) & 63); }
            freeCount -= count; return (long)s;
        }
        return -1;
    }
    void share(size_t f) { assert(refs[f] > 0); ++refs[f]; }
    bool release(size_t f) { assert(refs[f] > 0); if (--refs[f] == 0) { bits[f >> 6] &= ~(1ULL << (f & 63)); ++freeCount; return true; } return false; }
    size_t freeFrames() const { return freeCount; } int refCount(size_t f) const { return refs[f]; }
    bool consistent() const { size_t fr = 0; for (size_t f = 0; f < n; ++f) { if (used(f) != (refs[f] > 0)) return false; fr += refs[f] == 0; } return fr == freeCount; }
    static uint64_t physAddr(size_t frame, unsigned offset) { return (uint64_t)frame << 12 | offset; }
    static size_t frameOf(uint64_t pa) { return (size_t)(pa >> 12); } static unsigned offsetOf(uint64_t pa) { return (unsigned)(pa & 0xfff); }
};

struct Reference {                                                                // 참조 횟수 배열만으로 구한 느린 기준
    std::vector<int> ref; explicit Reference(size_t n) : ref(n, 0) {}
    long alloc() { for (size_t f = 0; f < ref.size(); ++f) if (ref[f] == 0) { ref[f] = 1; return (long)f; } return -1; }
    long allocContiguous(size_t c, size_t a) { for (size_t s = 0; s + c <= ref.size(); s += a) { bool ok = true; for (size_t i = 0; i < c; ++i) ok &= ref[s + i] == 0; if (ok) { for (size_t i = 0; i < c; ++i) ref[s + i] = 1; return (long)s; } } return -1; }
    size_t freeFrames() const { size_t c = 0; for (int r : ref) c += r == 0; return c; }
};

int main() {
    // 원래 예: 4 프레임짜리 작은 RAM
    {   FrameAllocator fa(4); long f0 = fa.alloc(), f1 = fa.alloc();
        assert(f0 == 0 && f1 == 1 && fa.freeFrames() == 2 && FrameAllocator::physAddr(f1, 0x234) == 0x1234);
        fa.share(f0); assert(!fa.release(f0) && fa.freeFrames() == 2);              // 아직 한 쪽이 쓰는 중이라 반환되지 않는다
        assert(fa.release(f0) && fa.freeFrames() == 3 && fa.alloc() == 0);          // 마지막 참조가 사라져야 비워지고 재사용
        fa.alloc(); fa.alloc(); assert(fa.alloc() == -1 && fa.consistent()); }      // 물리 메모리 고갈
    // 주소 구성
    std::mt19937_64 rng(1);
    for (int i = 0; i < 100000; ++i) { size_t f = rng() & ((1ULL << 40) - 1); unsigned off = (unsigned)(rng() & 0xfff); uint64_t pa = FrameAllocator::physAddr(f, off); assert(FrameAllocator::frameOf(pa) == f && FrameAllocator::offsetOf(pa) == off && pa < (1ULL << 52)); }
    // 차분 시험
    long ops = 0, contiguousOk = 0, contiguousFail = 0, shares = 0;
    for (size_t frames : {(size_t)200, (size_t)1000, (size_t)4096}) {
        FrameAllocator fa(frames); Reference ref(frames); std::mt19937 r((uint32_t)frames); std::vector<size_t> live;                // live: 참조 하나당 항목 하나 (공유하면 같은 프레임이 여러 번)
        for (int step = 0; step < 30000; ++step) {
            int op = (int)(r() % 100); ++ops;
            if (op < 45) { long a = fa.alloc(), b = ref.alloc(); assert(a == b); if (a >= 0) live.push_back((size_t)a); }
            else if (op < 55) {
                size_t cnt = 1 + r() % 16, align = (size_t)1 << (r() % 5); long a = fa.allocContiguous(cnt, align), b = ref.allocContiguous(cnt, align); assert(a == b);
                if (a >= 0) { ++contiguousOk; assert((size_t)a % align == 0); for (size_t i = 0; i < cnt; ++i) live.push_back((size_t)a + i); } else ++contiguousFail;
            } else if (op < 70 && !live.empty()) { size_t f = live[r() % live.size()]; fa.share(f); ref.ref[f]++; live.push_back(f); ++shares; }
            else if (!live.empty()) { size_t i = r() % live.size(); size_t f = live[i]; live[i] = live.back(); live.pop_back(); bool freed = fa.release(f); ref.ref[f]--; assert(freed == (ref.ref[f] == 0)); }
            assert(fa.freeFrames() == ref.freeFrames());
            if (step % 1500 == 0) { assert(fa.consistent()); for (size_t f = 0; f < frames; ++f) assert((int)fa.refCount(f) == ref.ref[f]); }
        }
        for (size_t f : live) fa.release(f);
        assert(fa.consistent() && fa.freeFrames() == frames);                          // 모든 공유가 사라지면 정확히 비워진다
    }
    assert(contiguousOk > 100 && contiguousFail > 10 && shares > 1000);
    // 단편화: 512 프레임마다 하나만 쓰면 정렬된 512 연속 할당 실패
    {   const size_t BLOCKS = 8, FR = BLOCKS * 512; FrameAllocator g(FR);
        for (size_t b = 0; b < BLOCKS; ++b) { long x = g.allocContiguous(512, 512); assert(x == (long)(b * 512)); }                 // 512 프레임(=2MB) 블록 8 개를 차지했다가
        for (size_t b = 0; b < BLOCKS; ++b) { for (size_t i = 1; i < 512; ++i) g.release(b * 512 + i); }                                    // 각 블록의 첫 프레임만 남기고 모두 해제
        assert(g.freeFrames() == FR - BLOCKS && g.allocContiguous(512, 512) == -1);                                                         // 99.8% 가 비었는데도 큰 할당 실패 (외부 단편화)
        g.release(0); assert(g.allocContiguous(512, 512) == 0); }                                                                           // 점유를 풀면 성공
    std::cout << "PhysicalAddress verified: " << ops << " random ops matched the reference (" << contiguousOk << " contiguous allocations, " << contiguousFail << " refused, " << shares << " shares); bitmap == refcounts." << std::endl;
    return 0;
}
// Time Complexity: alloc O(프레임 수 / 64) (비트맵 워드 단위 건너뛰기), 연속 할당 O(프레임 수 · 크기), 해제 O(1)
// Space Complexity: O(프레임 수)
```
## AddressTranslation()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <vector>

// 주소 변환(MMU): 가상 주소를 (페이지 번호, 오프셋) 으로 나누고, 페이지 테이블 항목(PTE)에서 프레임 번호를 찾아 (프레임 번호 << 12 | 오프셋) 을 만든다.
// PTE 에는 present(메모리에 있음), writable, user 비트가 있고, 위반하면 CPU 가 페이지 폴트(예외)를 일으킨다
// 이 구현은 실제 MMU 처럼 ① 접근 종류(읽기/쓰기/실행)와 NX 비트 ② x86 식 오류 코드(bit0 보호 위반인가, bit1 쓰기, bit2 사용자, bit4 명령어 인출) ③ accessed/dirty 비트 갱신(성공한 접근에서만, 쓰기에서 dirty)
//  ④ TLB(세트 연관, 세트마다 LRU) 를 갖춘다.  OS 가 PTE 를 바꾸면 해당 TLB 항목을 무효화(INVLPG)해야 한다
// 검증: 세 구현을 같은 무작위 연산열(map/unmap/protect/접근 40 000 번)에 적용해 결과를 맞춘다 — A: TLB 를 쓰는 MMU, B: TLB 없이 매번 테이블을 걷는 MMU, C: std::map 으로 짠 독립 기준.
//        모든 접근에서 (상태, 물리 주소, 오류 코드) 가 같고, 마지막에 accessed/dirty 비트까지 같다.  D: INVLPG 를 빼먹은 MMU 는 낡은 변환 때문에 틀린 결과가 나온다(횟수 확인).
//        TLB 닫힌 형태: 완전 연관 LRU 에서 P <= 항목 수인 순환 접근의 미스 = P, P = 항목 수 + 1 이면 전부 미스, 세트 연관에서는 같은 세트로 몰리면 용량이 남아도 전부 미스
struct PTE { bool present = false, writable = false, user = false, nx = false, accessed = false, dirty = false; uint32_t frame = 0; };
enum Access { READ, WRITE, EXEC };
enum Status { OK, NOT_PRESENT, PROTECTION };
struct Result { Status st; uint64_t pa; unsigned err; bool operator==(const Result& o) const { return st == o.st && pa == o.pa && err == o.err; } };

unsigned errCode(bool protection, Access a, bool user) { return (protection ? 1u : 0u) | (a == WRITE ? 2u : 0u) | (user ? 4u : 0u) | (a == EXEC ? 16u : 0u); }
bool allowed(const PTE& e, Access a, bool user) { return !((a == WRITE && !e.writable) || (user && !e.user) || (a == EXEC && e.nx)); }

class Tlb {
    struct Ent { uint64_t vpn; PTE pte; };
    size_t sets, ways; std::vector<std::list<Ent>> s;
public:
    long hits = 0, misses = 0;
    Tlb(size_t nsets, size_t nways) : sets(nsets), ways(nways), s(nsets ? nsets : 1) {}
    bool enabled() const { return sets > 0; }
    PTE* lookup(uint64_t vpn) {
        if (!sets) return nullptr;
        auto& set = s[vpn % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (it->vpn == vpn) { set.splice(set.begin(), set, it); ++hits; return &set.front().pte; }
        ++misses; return nullptr;
    }
    void insert(uint64_t vpn, const PTE& e) { if (!sets) return; auto& set = s[vpn % sets]; set.push_front({vpn, e}); if (set.size() > ways) set.pop_back(); }
    void invalidate(uint64_t vpn) { if (!sets) return; s[vpn % sets].remove_if([&](const Ent& x) { return x.vpn == vpn; }); }
    size_t capacity() const { return sets * ways; }
};

class Mmu {
public:
    std::vector<PTE> table; Tlb tlb; bool invlpg; long walks = 0;
    Mmu(size_t pages, size_t sets, size_t ways, bool doInvlpg = true) : table(pages), tlb(sets, ways), invlpg(doInvlpg) {}
    Result translate(uint64_t va, Access a, bool user) {
        uint64_t page = va >> 12, off = va & 0xfff; PTE* e = tlb.lookup(page);
        if (!e) {                                                                               // TLB 미스: 테이블 걷기
            ++walks;
            if (page >= table.size() || !table[page].present) return {NOT_PRESENT, 0, errCode(false, a, user)};
            if (!allowed(table[page], a, user)) return {PROTECTION, 0, errCode(true, a, user)};
            table[page].accessed = true; tlb.insert(page, table[page]); e = tlb.lookup(page); if (!e) { static PTE copy; copy = table[page]; e = &copy; }   // 성공한 접근만 TLB 에 채운다
            if (a == WRITE && !table[page].dirty) table[page].dirty = true;
            if (tlb.enabled()) { PTE* t = tlb.lookup(page); if (t) { t->accessed = true; t->dirty = table[page].dirty; } --tlb.hits; }
            return {OK, (uint64_t)table[page].frame << 12 | off, 0};
        }
        if (!allowed(*e, a, user)) return {PROTECTION, 0, errCode(true, a, user)};              // 캐시된 권한으로 검사 (낡았으면 틀린다)
        if (a == WRITE && !e->dirty) { e->dirty = true; if (page < table.size() && table[page].present) table[page].dirty = true; }   // 처음 쓰기: 테이블의 dirty 비트도 올린다
        if (page < table.size() && table[page].present) table[page].accessed = true;
        return {OK, (uint64_t)e->frame << 12 | off, 0};
    }
    void map(uint64_t page, uint32_t frame, bool w, bool u, bool nx) { PTE e; e.present = true; e.writable = w; e.user = u; e.nx = nx; e.frame = frame; table[page] = e; if (invlpg) tlb.invalidate(page); }
    void unmap(uint64_t page) { table[page] = PTE(); if (invlpg) tlb.invalidate(page); }
    void protect(uint64_t page, bool w, bool u, bool nx) { if (!table[page].present) return; table[page].writable = w; table[page].user = u; table[page].nx = nx; if (invlpg) tlb.invalidate(page); }
};

struct Oracle {                                                                                  // 독립 기준: 페이지 -> PTE 맵과 직접 쓴 진리표
    std::map<uint64_t, PTE> m;
    Result translate(uint64_t va, Access a, bool user) {
        auto it = m.find(va >> 12); if (it == m.end() || !it->second.present) return {NOT_PRESENT, 0, errCode(false, a, user)};
        PTE& e = it->second;
        if (a == WRITE && !e.writable) return {PROTECTION, 0, errCode(true, a, user)};
        if (user && !e.user) return {PROTECTION, 0, errCode(true, a, user)};
        if (a == EXEC && e.nx) return {PROTECTION, 0, errCode(true, a, user)};
        e.accessed = true; if (a == WRITE) e.dirty = true; return {OK, (uint64_t)e.frame << 12 | (va & 0xfff), 0};
    }
};

int main() {
    // 원래 예
    {   Mmu mmu(16, 0, 0); mmu.map(3, 7, true, true, false); mmu.map(4, 9, false, true, false); mmu.map(5, 2, true, false, false);
        Result r = mmu.translate(3 * 4096 + 0x123, READ, true); assert(r.st == OK && r.pa == 7 * 4096 + 0x123);
        assert(mmu.translate(4 * 4096, WRITE, true).st == PROTECTION && mmu.translate(4 * 4096, READ, true).st == OK);
        assert(mmu.translate(5 * 4096, READ, true).st == PROTECTION && mmu.translate(5 * 4096, READ, false).st == OK);
        Result nf = mmu.translate(9 * 4096, READ, true); assert(nf.st == NOT_PRESENT && nf.err == 4);                       // P=0, U=1
        Result pf = mmu.translate(4 * 4096, WRITE, true); assert(pf.err == (1u | 2u | 4u)); }                              // P=1, W=1, U=1
    // 세 구현 차분 + 낡은 TLB
    const size_t PAGES = 48; long accesses = 0, faultsNP = 0, faultsProt = 0, staleWrong = 0;
    {   Mmu A(PAGES, 4, 4), B(PAGES, 0, 0), D(PAGES, 4, 4, false); Oracle C; std::mt19937 rng(77);
        for (int step = 0; step < 40000; ++step) {
            uint64_t page = rng() % PAGES; int op = (int)(rng() % 100);
            if (op < 8) { uint32_t fr = (uint32_t)(rng() % 1000); bool w = rng() % 2, u = rng() % 2, nx = rng() % 3 == 0; A.map(page, fr, w, u, nx); B.map(page, fr, w, u, nx); D.map(page, fr, w, u, nx); PTE e; e.present = true; e.writable = w; e.user = u; e.nx = nx; e.frame = fr; C.m[page] = e; }
            else if (op < 12) { A.unmap(page); B.unmap(page); D.unmap(page); C.m.erase(page); }
            else if (op < 18) { bool w = rng() % 2, u = rng() % 2, nx = rng() % 3 == 0; A.protect(page, w, u, nx); B.protect(page, w, u, nx); D.protect(page, w, u, nx); auto it = C.m.find(page); if (it != C.m.end()) { it->second.writable = w; it->second.user = u; it->second.nx = nx; } }
            else {
                uint64_t va = (rng() % (PAGES + 4)) * 4096 + rng() % 4096; Access a = (Access)(rng() % 3); bool user = rng() % 2; ++accesses;
                Result ra = A.translate(va, a, user), rb = B.translate(va, a, user), rc = C.translate(va, a, user), rd = D.translate(va, a, user);
                assert(ra == rb && rb == rc); faultsNP += rc.st == NOT_PRESENT; faultsProt += rc.st == PROTECTION; if (!(rd == rc)) ++staleWrong;
            }
        }
        for (uint64_t p = 0; p < PAGES; ++p) {                                                  // accessed/dirty 비트까지 같다 (TLB 가 쓰기 비트를 테이블에 반영)
            const PTE& x = A.table[p]; const PTE& y = B.table[p]; auto it = C.m.find(p);
            assert(x.present == y.present && x.accessed == y.accessed && x.dirty == y.dirty && x.writable == y.writable && x.frame == y.frame);
            if (it != C.m.end()) assert(it->second.accessed == x.accessed && it->second.dirty == x.dirty && it->second.present == x.present);
        }
        assert(A.tlb.hits > 5000 && A.walks < B.walks && staleWrong > 100 && faultsNP > 1000 && faultsProt > 1000);          // TLB 는 걷기를 줄이고, INVLPG 없는 쪽은 틀린다
    }
    // TLB 닫힌 형태
    {   auto misses = [](size_t sets, size_t ways, const std::vector<uint64_t>& pages, int reps) {
            Tlb t(sets, ways); long m = 0; for (int r = 0; r < reps; ++r) for (uint64_t p : pages) { if (!t.lookup(p)) { ++m; t.insert(p, PTE()); } } return m; };
        std::vector<uint64_t> p16, p17, same; for (uint64_t i = 0; i < 16; ++i) p16.push_back(i); for (uint64_t i = 0; i < 17; ++i) p17.push_back(i); for (uint64_t i = 0; i < 3; ++i) same.push_back(i * 4);
        assert(misses(1, 16, p16, 50) == 16);                                                    // 완전 연관: 항목 수만큼의 페이지를 순환 -> 처음 한 번씩만 미스
        assert(misses(1, 16, p17, 50) == 17 * 50);                                               // 한 페이지 더 -> LRU 가 매번 가장 오래된 것을 내쫓아 전부 미스
        assert(misses(4, 2, same, 50) == 3 * 50);                                                // 용량 8 이지만 세 페이지가 같은 세트(번호 % 4 == 0) -> 2 방향을 넘어 전부 미스
        std::vector<uint64_t> spread = {0, 1, 2, 3, 4, 5}; assert(misses(4, 2, spread, 50) == 6);   // 같은 용량에서 고르게 퍼지면 처음 6 번만
        assert(Tlb(16, 4).capacity() * 4096 == 256 * 1024ULL); }                                  // TLB 도달 범위(reach) = 항목 수 x 페이지 크기
    std::cout << "AddressTranslation verified: " << accesses << " accesses (" << faultsNP << " not-present, " << faultsProt << " protection faults) agreed across TLB/no-TLB/oracle; skipping INVLPG gave " << staleWrong << " stale results." << std::endl;
    return 0;
}
// Time Complexity: TLB 적중 O(방향 수), 미스 O(1) (한 단계 테이블)
// Space Complexity: O(페이지 수 + TLB 항목 수)
```
## Paging()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <deque>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>

// 페이징: 메모리를 같은 크기(4KB)의 페이지로 나눠 어디에나 배치할 수 있게 한다 -> 외부 단편화가 없다.  대신 마지막 페이지의 낭비(내부 단편화, 평균 반 페이지)가 생긴다.
// 문제: 32비트 주소 공간의 평면 페이지 테이블은 2^20 항목 x 4B = 4MB — 프로세스마다 이만큼 필요하다.
// 해법: 다단계 테이블 — 실제로 쓰는 영역의 테이블만 만든다 (희소한 주소 공간에 매우 유리)
// 물리 메모리보다 큰 주소 공간을 쓰려면 요구 페이징(demand paging)이 필요하다: 페이지를 처음 만질 때(또는 쫓겨난 뒤 다시 만질 때) 페이지 폴트가 나고, 빈 프레임이 없으면 교체 알고리즘이 희생 페이지를 고른다.
// 이 예제는 산술(원래 예)과 함께 교체 알고리즘 네 가지를 서로 다른 구현으로 만들어 성질로 검증한다:
//  FIFO(들어온 순서), LRU(가장 오래 안 쓴 것; 타임스탬프 구현과 리스트 구현 두 가지), Clock(참조 비트를 가진 원형 큐), OPT(Belady 의 최적: 앞으로 가장 늦게 쓰일 페이지)
// 검증: ① 고전 Belady 변칙: FIFO 는 프레임 3 개일 때 폴트 9 번, 4 개일 때 10 번  ② OPT == 전수 동적계획법으로 구한 최소 폴트(작은 트레이스 3 000 개) 이고 모든 알고리즘의 폴트 >= OPT
//        ③ LRU 는 스택 알고리즘: 프레임을 늘려도 폴트가 늘지 않고, 매 순간 k 프레임의 상주 집합 ⊆ k+1 프레임의 상주 집합.  OPT 도 단조.  FIFO 는 (드물게) 무작위 트레이스에서도 변칙이 나온다
//        ④ LRU 두 구현의 폴트와 상주 집합이 매 단계 같다  ⑤ 순환 접근 닫힌 형태: L 페이지를 K 번 순환, 프레임 F: L <= F 면 폴트 L, L > F 면 LRU·FIFO 는 전부 폴트인데 OPT 는 훨씬 적고 L = F + 1 이면 L + (총접근 - L) / F 번
enum Algo { FIFO, LRU, LRU2, CLOCK, OPT };

long simulate(Algo algo, size_t frames, const std::vector<int>& trace, std::vector<std::set<int>>* history = nullptr) {
    long faults = 0; std::set<int> resident; size_t n = trace.size();
    std::deque<int> fifo; std::map<int, long> lastUse; std::list<int> lruList; std::unordered_map<int, std::list<int>::iterator> where;
    std::vector<int> ring(frames, -1); std::vector<char> refBit(frames, 0); size_t hand = 0;
    std::vector<size_t> nextUse(n); { std::map<int, size_t> nxt; for (size_t i = n; i-- > 0;) { auto it = nxt.find(trace[i]); nextUse[i] = it == nxt.end() ? n + 1 : it->second; nxt[trace[i]] = i; } }
    std::map<int, size_t> nextOf;                                                                  // OPT: 각 상주 페이지의 다음 사용 위치
    for (size_t t = 0; t < n; ++t) {
        int p = trace[t]; bool hit = resident.count(p) > 0;
        if (!hit) {
            ++faults;
            if (resident.size() == frames) {                                                     // 희생 페이지 고르기
                int victim = -1;
                if (algo == FIFO) { victim = fifo.front(); fifo.pop_front(); }
                else if (algo == LRU) { long oldest = 1L << 60; for (int q : resident) { if (lastUse[q] < oldest) { oldest = lastUse[q]; victim = q; } } }
                else if (algo == LRU2) { victim = lruList.back(); lruList.pop_back(); where.erase(victim); }
                else if (algo == CLOCK) { while (refBit[hand]) { refBit[hand] = 0; hand = (hand + 1) % frames; } victim = ring[hand]; ring[hand] = p; refBit[hand] = 1; hand = (hand + 1) % frames; }
                else { size_t far = 0; for (int q : resident) { if (nextOf[q] >= far) { if (nextOf[q] > far || victim < 0) victim = q; far = nextOf[q]; } } }
                resident.erase(victim);
            } else if (algo == CLOCK) { for (size_t i = 0; i < frames; ++i) { if (ring[i] < 0) { ring[i] = p; refBit[i] = 1; break; } } }
            resident.insert(p);
            if (algo == FIFO) fifo.push_back(p);
            if (algo == LRU2) { lruList.push_front(p); where[p] = lruList.begin(); }
        } else {
            if (algo == CLOCK) { for (size_t i = 0; i < frames; ++i) { if (ring[i] == p) refBit[i] = 1; } }
            if (algo == LRU2) { lruList.erase(where[p]); lruList.push_front(p); where[p] = lruList.begin(); }
        }
        lastUse[p] = (long)t; nextOf[p] = nextUse[t];
        if (history) history->push_back(resident);
    }
    return faults;
}

long optimalByDP(size_t frames, const std::vector<int>& trace, int pages) {                          // 모든 희생 선택을 따져 보는 전수 동적계획법 (페이지 <= 8)
    size_t S = (size_t)1 << pages; const long INF = 1L << 40; std::vector<long> cur(S, INF), nxt(S, INF); cur[0] = 0;
    for (int p : trace) {
        std::fill(nxt.begin(), nxt.end(), INF);
        for (size_t m = 0; m < S; ++m) {
            if (cur[m] >= INF) continue;
            if (m >> p & 1) { nxt[m] = std::min(nxt[m], cur[m]); continue; }
            if ((size_t)__builtin_popcountll(m) < frames) { size_t m2 = m | (size_t)1 << p; nxt[m2] = std::min(nxt[m2], cur[m] + 1); }
            else for (int e = 0; e < pages; ++e) { if (m >> e & 1) { size_t m2 = (m & ~((size_t)1 << e)) | (size_t)1 << p; nxt[m2] = std::min(nxt[m2], cur[m] + 1); } }
        }
        cur.swap(nxt);
    }
    return *std::min_element(cur.begin(), cur.end());
}

int main() {
    // 원래 예: 산술
    {   const uint64_t PAGE = 4096; auto pages = [&](uint64_t bytes) { return (bytes + PAGE - 1) / PAGE; };
        assert(pages(1) == 1 && pages(4096) == 1 && pages(4097) == 2);
        uint64_t request = 10000, waste = pages(request) * PAGE - request; assert(waste == 2288);               // 3페이지 = 12288 -> 2288 바이트 낭비
        uint64_t flat = (1ULL << 20) * 4; assert(flat == 4u << 20);                                              // 평면 테이블: 4MB
        uint64_t used[] = {0x08048000, 0x09000000, 0xBFFFF000};                                                  // 코드·힙·스택 주변만 쓰는 프로세스
        std::set<uint64_t> dirs; for (uint64_t va : used) dirs.insert(va >> 22);
        uint64_t twoLevel = (1 + dirs.size()) * PAGE; assert(dirs.size() == 3 && twoLevel == 4 * PAGE && flat / twoLevel == 256); }
    // ① Belady 변칙
    std::vector<int> belady = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    assert(simulate(FIFO, 3, belady) == 9 && simulate(FIFO, 4, belady) == 10);                                  // 프레임을 늘렸더니 폴트가 늘었다
    assert(simulate(LRU, 3, belady) == 10 && simulate(LRU, 4, belady) == 8 && simulate(OPT, 3, belady) == 7 && simulate(OPT, 4, belady) == 6);
    // ② OPT 의 최적성, ③ 스택 성질, ④ 두 LRU 구현
    std::mt19937 rng(2024); long traces = 0, fifoAnomalies = 0, clockBetterThanFifo = 0, clockTotal = 0, fifoTotal = 0;
    for (int it = 0; it < 3000; ++it) {
        int pages = 3 + (int)(rng() % 5), len = 10 + (int)(rng() % 31); std::vector<int> tr(len);
        for (int& x : tr) x = (rng() % 3 == 0) ? (int)(rng() % pages) : (int)(rng() % std::max(2, pages / 2));                                           // 지역성이 약간 있는 트레이스
        for (size_t F = 1; F <= 4; ++F) {
            long opt = simulate(OPT, F, tr); assert(opt == optimalByDP(F, tr, pages));                                                                      // OPT == 전수 최솟값
            for (Algo a : {FIFO, LRU, CLOCK}) assert(simulate(a, F, tr) >= opt);
            assert(simulate(LRU, F, tr) == simulate(LRU2, F, tr));
        }
        ++traces;
    }
    for (int it = 0; it < 2000; ++it) {
        int pages = 8, len = 60; std::vector<int> tr(len); for (int& x : tr) x = (int)(rng() % pages);
        long prevLru = 1L << 40, prevOpt = 1L << 40; bool anomaly = false; long prevFifo = 1L << 40;
        std::vector<std::vector<std::set<int>>> hist(7);
        for (size_t F = 1; F <= 6; ++F) {
            long lru = simulate(LRU, F, tr, &hist[F]), lru2 = simulate(LRU2, F, tr), opt = simulate(OPT, F, tr), fifo = simulate(FIFO, F, tr);
            assert(lru == lru2 && lru <= prevLru && opt <= prevOpt);                                                                                            // LRU·OPT 는 프레임을 늘리면 폴트가 줄거나 같다
            if (fifo > prevFifo) { anomaly = true; }
            prevLru = lru; prevOpt = opt; prevFifo = fifo;
            if (F >= 2) for (int t = 0; t < len; ++t) assert(std::includes(hist[F][t].begin(), hist[F][t].end(), hist[F - 1][t].begin(), hist[F - 1][t].end()));   // 포함 성질
            if (F == 4) { clockTotal += simulate(CLOCK, F, tr); fifoTotal += fifo; clockBetterThanFifo += simulate(CLOCK, F, tr) <= fifo; }
        }
        fifoAnomalies += anomaly;
    }
    assert(fifoAnomalies >= 1);                                                                                           // 드물지만 무작위 트레이스에서도 실제로 나온다
    // LRU 두 구현의 상주 집합이 매 단계 같다
    {   std::vector<int> tr(500); for (int& x : tr) x = (int)(rng() % 12); std::vector<std::set<int>> h1, h2; simulate(LRU, 5, tr, &h1); simulate(LRU2, 5, tr, &h2); assert(h1 == h2); }
    // ⑤ 순환 접근
    for (size_t F : {(size_t)4, (size_t)8}) {
        for (size_t L : {F - 1, F, F + 1, F + 3}) {
            std::vector<int> tr; for (int k = 0; k < 20; ++k) for (size_t i = 0; i < L; ++i) tr.push_back((int)i);
            long lru = simulate(LRU, F, tr), fifo = simulate(FIFO, F, tr), opt = simulate(OPT, F, tr);
            if (L <= F) assert(lru == (long)L && fifo == (long)L && opt == (long)L);                                      // 다 들어가면 처음 한 번씩만
            else {
                assert(lru == (long)tr.size() && fifo == (long)tr.size() && opt < lru * 3 / 4);                              // 하나라도 넘치면 LRU·FIFO 는 매번 폴트, OPT 는 훨씬 적다
                if (L == F + 1) assert(opt == (long)L + ((long)tr.size() - (long)L) / (long)F);                              // L = F + 1 이면 OPT 는 처음 L 번 뒤로 F 번 접근마다 한 번만 폴트
            }
        }
    }
    std::cout << "Paging verified: " << traces << " small traces (OPT == exhaustive optimum), Belady anomaly 9 -> 10 faults for FIFO, FIFO anomalies (rare) in " << fifoAnomalies << "/2000 random traces, LRU stack property held; Clock avg faults "
              << clockTotal / 2000.0 << " vs FIFO " << fifoTotal / 2000.0 << " (4 frames)." << std::endl;
    return 0;
}
// Time Complexity: 시뮬레이션 O(트레이스 길이 · 프레임 수) (LRU 리스트 구현은 O(1)/접근)
// Space Complexity: O(프레임 수)
```
## PageTable()
### 대표코드
```cpp
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 페이지 테이블: 가상 주소를 물리 주소로 옮기는 표.  한 장짜리 배열은 주소 공간(2^36 페이지)에 비례해 너무 크므로 x86-64 는 4단계 기수 트리(PML4 -> PDPT -> PD -> PT)를 쓴다.
// 테이블은 4KB 한 프레임이고 항목(8바이트) 512 개 — 쓰이는 구간에 대해서만 하위 테이블을 만들어 희소한 주소 공간을 싸게 표현한다.  PD/PDPT 단계에서 PS(Page Size) 비트를 켜면 거기가 잎이 되어 2MB/1GB 큰 페이지가 된다
// 이 구현은 시뮬레이션한 물리 메모리(프레임 = 항목 512 개 배열) 위에 실제 x86-64 항목 형식(bit0 P, bit1 RW, bit2 US, bit7 PS, bit63 NX, [51:12] 프레임)으로 만들고
//  map(4KB/2MB/1GB, 정렬·겹침 검사), unmap(비게 된 테이블은 위로 올라가며 회수), protect, walk(메모리 접근 횟수 포함) 를 지원한다
// 검증: ① 무작위 연산 20 000 번(군집한 주소 6 곳)을 std::map 으로 짠 독립 기준(구간 겹침 검사 포함)과 대조 — map 성공 여부, walk 결과(성공 여부·물리 주소·페이지 크기·플래그)가 같고 성공한 walk 의 메모리 접근 수는 정확히 4 - 레벨
//        ② 테이블 프레임 수 == 기준의 매핑에서 직접 센 값(루트 1 + 서로 다른 PML4/PDPT/PD 접두사 수) — 실패한 map 이 빈 테이블을 남기지 않고 unmap 이 회수  ③ 모두 지우면 프레임 1 개(루트)만 남고 루트가 비어 있음
//        ④ 닫힌 형태: 정렬된 1GB 구역을 4KB 페이지로 채우면 테이블 프레임이 정확히 1+1+1+512 = 515, 2MB 페이지로 채우면 3, 1GB 페이지면 2  ⑤ 정렬되지 않은 큰 페이지·겹치는 매핑 거절
const uint64_t P = 1, RW = 2, US = 4, PS = 128, NXBIT = 1ULL << 63, ADDR = 0x000ffffffffff000ULL;
struct Walk { bool ok = false; uint64_t pa = 0, flags = 0; int level = -1, accesses = 0; };
inline uint64_t sizeOfLevel(int level) { return 4096ULL << (9 * level); }
inline unsigned idx(uint64_t va, int level) { return unsigned(va >> (12 + 9 * level) & 0x1ff); }

class PageTable {
    std::vector<std::array<uint64_t, 512>> mem; std::vector<int> count; std::vector<uint32_t> freeList; std::vector<char> inUse; size_t inUseFrames = 0;
    uint32_t allocFrame() {
        uint32_t f; if (!freeList.empty()) { f = freeList.back(); freeList.pop_back(); } else { f = (uint32_t)mem.size(); mem.emplace_back(); count.push_back(0); inUse.push_back(0); }
        mem[f].fill(0); count[f] = 0; inUse[f] = 1; ++inUseFrames; return f;
    }
    void freeFrame(uint32_t f) { assert(count[f] == 0); inUse[f] = 0; freeList.push_back(f); --inUseFrames; }
public:
    PageTable() { allocFrame(); }                                                              // 프레임 0 = PML4 (CR3)
    size_t framesInUse() const { return inUseFrames; }
    bool rootEmpty() const { return count[0] == 0; }
    bool map(uint64_t va, uint64_t pa, uint64_t flags, int level = 0) {
        uint64_t sz = sizeOfLevel(level); if (va % sz || pa % sz) return false;                // 큰 페이지는 크기에 정렬돼야 한다
        uint32_t f = 0;
        for (int l = 3; l > level; --l) {
            uint64_t e = mem[f][idx(va, l)];
            if (!(e & P)) { uint32_t nf = allocFrame(); mem[f][idx(va, l)] = ((uint64_t)nf << 12) | P | RW | US; ++count[f]; f = nf; }   // 없으면 하위 테이블을 만든다 (allocFrame 이 벡터를 키울 수 있어 참조를 쥐고 있으면 안 된다)
            else if (e & PS) return false;                                                       // 위쪽에 큰 페이지가 이미 있다: 겹침
            else f = (uint32_t)((e & ADDR) >> 12);
        }
        uint64_t& leaf = mem[f][idx(va, level)]; if (leaf & P) return false;                    // 이미 매핑됨(작은 페이지들이 있는 하위 테이블 포함)
        leaf = (pa & ADDR) | flags | P | (level > 0 ? PS : 0); ++count[f]; return true;
    }
    Walk walk(uint64_t va) const {
        Walk w; uint32_t f = 0;
        for (int l = 3; l >= 0; --l) {
            uint64_t e = mem[f][idx(va, l)]; ++w.accesses;                                      // 테이블 항목 하나를 읽는 것이 메모리 접근 한 번
            if (!(e & P)) return w;
            if (l == 0 || (e & PS)) { w.ok = true; w.level = l; w.flags = e & ~ADDR & ~(uint64_t)PS; w.pa = ((e & ADDR) & ~(sizeOfLevel(l) - 1)) | (va & (sizeOfLevel(l) - 1)); return w; }
            f = (uint32_t)((e & ADDR) >> 12);
        }
        return w;
    }
    bool unmap(uint64_t va) {
        uint32_t path[4]; int pidx[4]; uint32_t f = 0; int l = 3;
        for (;; --l) {
            path[l] = f; pidx[l] = (int)idx(va, l); uint64_t e = mem[f][pidx[l]]; if (!(e & P)) return false;
            if (l == 0 || (e & PS)) break;
            f = (uint32_t)((e & ADDR) >> 12);
        }
        mem[f][pidx[l]] = 0; --count[f];
        while (l < 3 && count[path[l]] == 0) { freeFrame(path[l]); ++l; mem[path[l]][pidx[l]] = 0; --count[path[l]]; }      // 비게 된 테이블은 위로 올라가며 회수
        return true;
    }
    bool protect(uint64_t va, uint64_t flags) {
        uint32_t f = 0;
        for (int l = 3; l >= 0; --l) { uint64_t& e = mem[f][idx(va, l)]; if (!(e & P)) return false; if (l == 0 || (e & PS)) { e = (e & (ADDR | PS)) | flags | P; return true; } f = (uint32_t)((e & ADDR) >> 12); }
        return false;
    }
};

struct Mapping { uint64_t pa, flags; int level; };
struct Oracle {                                                                                  // 독립 기준: 정렬된 구간의 맵
    std::map<uint64_t, Mapping> m;
    const std::pair<const uint64_t, Mapping>* find(uint64_t va) const { auto it = m.upper_bound(va); if (it == m.begin()) return nullptr; --it; return (va - it->first < sizeOfLevel(it->second.level)) ? &*it : nullptr; }
    bool overlaps(uint64_t base, uint64_t size) const {                                      // 주소 공간 끝에서 덧셈이 넘치지 않도록 뺄셈으로 비교
        auto it = m.lower_bound(base); if (it != m.end() && it->first - base < size) return true;
        if (it != m.begin()) { --it; if (base - it->first < sizeOfLevel(it->second.level)) return true; } return false;
    }
    size_t expectedFrames() const {                                                              // 루트 + 서로 다른 PML4/PDPT/PD 접두사 수 (잎이 있는 만큼)
        std::set<uint64_t> p3, p2, p1; for (auto& kv : m) { uint64_t va = kv.first; p3.insert(va >> 39); if (kv.second.level <= 1) p2.insert(va >> 30); if (kv.second.level == 0) p1.insert(va >> 21); }
        return 1 + p3.size() + p2.size() + p1.size();
    }
};

int main() {
    // 원래 구조 확인: 4KB 한 장
    {   PageTable pt; uint64_t va = 0x00007f1234567000ULL; assert(pt.map(va, 0x1000, RW | US) && pt.framesInUse() == 4);
        Walk w = pt.walk(va + 0xabc); assert(w.ok && w.pa == 0x1abc && w.level == 0 && w.accesses == 4 && (w.flags & RW) && (w.flags & US));
        assert(!pt.walk(va + 0x1000).ok && pt.unmap(va) && pt.framesInUse() == 1 && pt.rootEmpty()); }
    // 닫힌 형태
    {   PageTable a; for (uint64_t i = 0; i < 512 * 512; ++i) assert(a.map((1ULL << 30) + i * 4096, i * 4096, RW));            // 정렬된 1GB 구역을 4KB 페이지로
        assert(a.framesInUse() == 1 + 1 + 1 + 512);
        PageTable b; for (uint64_t i = 0; i < 512; ++i) assert(b.map((1ULL << 30) + i * (2ULL << 20), i * (2ULL << 20), RW, 1)); assert(b.framesInUse() == 3);   // 2MB 페이지
        PageTable c; assert(c.map(1ULL << 30, 0, RW, 2) && c.framesInUse() == 2);                                                                                  // 1GB 페이지
        Walk w = b.walk((1ULL << 30) + 5 * (2ULL << 20) + 0x1234); assert(w.ok && w.level == 1 && w.accesses == 3 && w.pa == 5 * (2ULL << 20) + 0x1234);
        Walk g = c.walk((1ULL << 30) + 0x12345678); assert(g.ok && g.level == 2 && g.accesses == 2 && g.pa == 0x12345678);
        assert(a.walk((1ULL << 30) + 777 * 4096).accesses == 4);
        for (uint64_t i = 0; i < 512 * 512; ++i) { assert(a.unmap((1ULL << 30) + i * 4096)); }
        assert(a.framesInUse() == 1 && a.rootEmpty()); }
    // ⑤ 거절
    {   PageTable pt; assert(!pt.map(0x1000, 0, RW, 1) && !pt.map(0, 0x1000, RW, 1) && !pt.map(0x200000, 0x1000, RW, 1));       // 정렬이 안 맞는 2MB
        assert(pt.map(0x200000, 0x400000, RW, 1) && !pt.map(0x201000, 0x1000, RW, 0) && !pt.map(0x200000, 0, RW, 1) && pt.framesInUse() == 3);   // 큰 페이지 안쪽에 작은 페이지, 같은 곳에 두 번
        assert(pt.map(0x400000, 0x1000, RW, 0) && !pt.map(0x400000, 0x600000, RW, 1) && pt.framesInUse() == 4); }              // 하위 테이블이 있는 곳에 큰 페이지
    // 무작위 차분 시험
    std::mt19937_64 rng(4096); const uint64_t bases[6] = {0x00007f0000000000ULL, 0x0000000000400000ULL, 0x00007ffc00000000ULL, 0xffff800000000000ULL, 0xffffffff80000000ULL, 0x0000123400000000ULL};
    PageTable pt; Oracle ora; long maps = 0, mapRejected = 0, walks = 0, hits = 0, bigPages = 0;
    for (int step = 0; step < 20000; ++step) {
        int op = (int)(rng() % 100); uint64_t base = bases[rng() % 6];
        int lvl = (op < 50) ? 0 : (op < 70 ? 1 : (op < 74 ? 2 : 0)); uint64_t sz = sizeOfLevel(lvl);
        uint64_t va = base + ((rng() % (lvl == 0 ? 2048 : lvl == 1 ? 600 : 3)) * sz);                         // 군집한 주소
        if (op < 74) {
            uint64_t pa = (rng() % 100000) * sz & 0x000fffffffffffffULL & ~(sz - 1), fl = (rng() % 2 ? RW : 0) | (rng() % 2 ? US : 0) | (rng() % 4 == 0 ? NXBIT : 0);
            bool want = va % sz == 0 && !ora.overlaps(va, sz); bool got = pt.map(va, pa, fl, lvl); assert(got == want); ++maps;
            if (got) { ora.m[va] = {pa, fl, lvl}; bigPages += lvl > 0; } else ++mapRejected;
        } else if (op < 84) {
            uint64_t q = va + (rng() % 8) * 4096; auto f = ora.find(q); bool want = f != nullptr; uint64_t target = f ? f->first : q;
            bool got = pt.unmap(target); assert(got == want); if (f) ora.m.erase(target);
        } else if (op < 88) {
            auto f = ora.find(va); uint64_t fl = (rng() % 2 ? RW : 0) | (rng() % 2 ? US : 0); bool got = pt.protect(va, fl); assert(got == (f != nullptr));
            if (f) { ora.m[f->first].flags = fl; }
        } else {
            uint64_t q = va + rng() % sz; Walk w = pt.walk(q); auto f = ora.find(q); ++walks; assert(w.ok == (f != nullptr));
            if (f) { ++hits; uint64_t lsz = sizeOfLevel(f->second.level); assert(w.level == f->second.level && w.accesses == 4 - f->second.level && w.pa == ((f->second.pa & ~(lsz - 1)) | (q & (lsz - 1)))); assert((w.flags & (RW | US | NXBIT)) == (f->second.flags & (RW | US | NXBIT))); }
            else assert(w.accesses >= 1 && w.accesses <= 4);
        }
        if (step % 200 == 0) assert(pt.framesInUse() == ora.expectedFrames());                           // 테이블 프레임 수 == 직접 센 값
    }
    assert(pt.framesInUse() == ora.expectedFrames());
    std::vector<uint64_t> all; for (auto& kv : ora.m) all.push_back(kv.first); for (uint64_t v : all) assert(pt.unmap(v));
    assert(pt.framesInUse() == 1 && pt.rootEmpty() && maps > 8000 && mapRejected > 500 && hits > 500 && bigPages > 500);                 // 모두 지우면 루트만
    std::cout << "PageTable verified: " << maps << " maps (" << mapRejected << " rejected overlaps/alignments, " << bigPages << " huge pages) and " << walks << " walks matched the oracle; 1GB of 4KB pages needs exactly 515 table frames." << std::endl;
    return 0;
}
// Time Complexity: map/unmap/walk 모두 O(4) = O(1) (레벨 수), 메모리 접근은 레벨 수만큼
// Space Complexity: O(사용 중인 구간에 필요한 테이블 수) — 희소한 주소 공간에서 한 장짜리 배열(512GB)보다 훨씬 작다
```
## PageFault()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <set>
#include <vector>
#if defined(__linux__)
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>
#endif

// 페이지 폴트: 매핑되지 않았거나 메모리에 없는 페이지에 접근했을 때 CPU 가 일으키는 예외.  운영체제가 디스크에서 페이지를 읽어 오고(요구 페이징), 프레임이 모자라면 교체 알고리즘으로 희생 페이지를 고른다.
//  FIFO 는 프레임을 늘려도 폴트가 오히려 늘어나는 벨레이디의 모순(Belady's anomaly)이 있고, LRU 는 스택 알고리즘이라 그런 일이 없다.  네 알고리즘(FIFO / LRU / Clock / 최적 OPT)을 구현해 성질을 확인한다.
//  ① 고전 열 1,2,3,4,1,2,5,1,2,3,4,5: FIFO 는 프레임 3 개에서 9 번, 4 개에서 *10 번*(모순), LRU 는 10 → 8 번, OPT 는 7 → 6 번  ② 무작위 열 3000 개(프레임 1..8): LRU·OPT 의 폴트는 프레임이 늘면 *줄거나 같다*(스택 성질), OPT ≤ 다른 모든 알고리즘, 폴트 ≥ 서로 다른 페이지 수이고 프레임 ≥ 페이지 수면 정확히 같다
//  ③ OPT(Belady 의 "가장 나중에 쓸 페이지 축출")가 *전수 탐색한 최소 폴트 수*와 같다 (페이지 ≤ 5, 길이 ≤ 9, 프레임 2~3 의 무작위 열 400 개)  ④ 무작위 열 20000 개를 뒤져 FIFO 의 벨레이디 모순 사례가 존재하고 LRU·OPT 에는 없음  ⑤ 순환 접근(프레임 F, 페이지 F+1): LRU/FIFO 는 *매 접근* 폴트, OPT 는 약 1/F
//  ⑥ 실제 커널(Linux): 새로 mmap 한 익명 메모리의 페이지를 처음 만질 때마다 minor fault 가 한 번씩 늘고(getrusage), 두 번째 순회는 거의 폴트가 없다.
long fifo(const std::vector<int>& refs, int frames) { std::list<int> q; std::set<int> in; long faults = 0; for (int p : refs) { if (in.count(p)) continue; ++faults; if ((int)q.size() == frames) { in.erase(q.front()); q.pop_front(); } q.push_back(p); in.insert(p); } return faults; }
long lru(const std::vector<int>& refs, int frames) { std::vector<int> st; long faults = 0; for (int p : refs) { auto it = std::find(st.begin(), st.end(), p); if (it != st.end()) st.erase(it); else { ++faults; if ((int)st.size() == frames) st.pop_back(); } st.insert(st.begin(), p); } return faults; }
long lruStamps(const std::vector<int>& refs, int frames) { std::map<int, long> last; long faults = 0, t = 0; for (int p : refs) { ++t; if (last.count(p)) { last[p] = t; continue; } ++faults; if ((int)last.size() == frames) { auto victim = last.begin(); for (auto it = last.begin(); it != last.end(); ++it) if (it->second < victim->second) victim = it; last.erase(victim); } last[p] = t; } return faults; }
long clockAlg(const std::vector<int>& refs, int frames) { std::vector<int> page(frames, -1); std::vector<char> ref(frames, 0); int hand = 0; long faults = 0; for (int p : refs) { bool hit = false; for (int i = 0; i < frames; ++i) if (page[i] == p) { ref[i] = 1; hit = true; break; } if (hit) continue; ++faults;
        while (page[hand] != -1 && ref[hand]) { ref[hand] = 0; hand = (hand + 1) % frames; } page[hand] = p; ref[hand] = 1; hand = (hand + 1) % frames; } return faults; }              // 두 번째 기회
long opt(const std::vector<int>& refs, int frames) { std::set<int> in; long faults = 0; for (size_t i = 0; i < refs.size(); ++i) { int p = refs[i]; if (in.count(p)) continue; ++faults; if ((int)in.size() == frames) { int victim = -1; size_t farthest = 0; for (int q : in) { size_t nxt = refs.size(); for (size_t j = i + 1; j < refs.size(); ++j) if (refs[j] == q) { nxt = j; break; } if (victim < 0 || nxt > farthest) { victim = q; farthest = nxt; } } in.erase(victim); } in.insert(p); } return faults; }
long bruteMin(const std::vector<int>& refs, size_t i, std::set<int> in, int frames) { while (i < refs.size() && in.count(refs[i])) ++i; if (i == refs.size()) return 0; long best = 1 << 30; if ((int)in.size() < frames) { std::set<int> n = in; n.insert(refs[i]); return 1 + bruteMin(refs, i + 1, n, frames); }
    for (int victim : in) { std::set<int> n = in; n.erase(victim); n.insert(refs[i]); best = std::min(best, 1 + bruteMin(refs, i + 1, n, frames)); } return best; }                    // 모든 희생 선택을 시도

int main() {
    std::vector<int> classic = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    assert(fifo(classic, 3) == 9 && fifo(classic, 4) == 10 && lru(classic, 3) == 10 && lru(classic, 4) == 8 && opt(classic, 3) == 7 && opt(classic, 4) == 6);                                       // ① 벨레이디의 모순
    std::mt19937 rng(1021); long anomalies = 0, lruAnoms = 0, optAnoms = 0;
    for (int it = 0; it < 3000; ++it) { int pages = 2 + (int)(rng() % 9), len = 20 + (int)(rng() % 120); std::vector<int> refs(len); for (int& r : refs) r = (int)(rng() % pages); std::set<int> distinct(refs.begin(), refs.end()); long prevLru = 1 << 30, prevOpt = 1 << 30;
        for (int f = 1; f <= 8; ++f) { long fi = fifo(refs, f), lr = lru(refs, f), cl = clockAlg(refs, f), op = opt(refs, f); assert(lr == lruStamps(refs, f)); assert(op <= fi && op <= lr && op <= cl && (long)distinct.size() <= op && (long)distinct.size() <= fi && (long)distinct.size() <= lr && (long)distinct.size() <= cl);
            assert(lr <= prevLru && op <= prevOpt); prevLru = lr; prevOpt = op; if (f >= (int)distinct.size()) assert(fi == (long)distinct.size() && lr == (long)distinct.size() && op == (long)distinct.size() && cl == (long)distinct.size()); } }          // ② 스택 성질 + OPT 가 최소
    for (int it = 0; it < 400; ++it) { int pages = 2 + (int)(rng() % 4), len = 3 + (int)(rng() % 7), f = 2 + (int)(rng() % 2); std::vector<int> refs(len); for (int& r : refs) r = (int)(rng() % pages); assert(opt(refs, f) == bruteMin(refs, 0, {}, f)); }              // ③ OPT = 전수 탐색한 최소
    for (int it = 0; it < 20000; ++it) { std::vector<int> refs(30 + rng() % 40); for (int& r : refs) r = (int)(rng() % 7); for (int f = 1; f < 6; ++f) { if (fifo(refs, f + 1) > fifo(refs, f)) ++anomalies; if (lru(refs, f + 1) > lru(refs, f)) ++lruAnoms; if (opt(refs, f + 1) > opt(refs, f)) ++optAnoms; } }
    assert(anomalies > 0 && lruAnoms == 0 && optAnoms == 0);                                                                                                                                          // ④
    {   const int F = 8; std::vector<int> cyc; for (int rep = 0; rep < 200; ++rep) for (int p = 0; p <= F; ++p) cyc.push_back(p); long n = (long)cyc.size(); assert(lru(cyc, F) == n && fifo(cyc, F) == n && opt(cyc, F) <= n / F + F + 1); }                // ⑤
#if defined(__linux__)
    {   long page = sysconf(_SC_PAGESIZE); const int pages = 2000; auto minflt = [] { struct rusage ru; getrusage(RUSAGE_SELF, &ru); return ru.ru_minflt; };
        char* mem = (char*)mmap(nullptr, (size_t)pages * page, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(mem != MAP_FAILED);
        long f0 = minflt(); for (int p = 0; p < pages; ++p) mem[(size_t)p * page] = 1; long f1 = minflt(); for (int p = 0; p < pages; ++p) mem[(size_t)p * page] = 2; long f2 = minflt();                // ⑥ 처음 만질 때마다 폴트
        assert(f1 - f0 >= pages && f1 - f0 <= pages + pages / 8 + 64 && f2 - f1 <= 64); munmap(mem, (size_t)pages * page);
        std::cout << "PageFault: the classic string gave FIFO 9 -> 10 faults when frames grew 3 -> 4 (Belady), LRU/OPT never grew over 3000 random strings, OPT matched exhaustive search, FIFO anomalies found: " << anomalies << ", and the kernel took " << f1 - f0 << " minor faults for the first touch of " << pages << " pages versus " << f2 - f1 << " on the second pass" << std::endl; }
#endif
    return 0;
}
// Time Complexity: FIFO/LRU O(n · 프레임), OPT O(n² · 프레임) (비교용)
// Space Complexity: O(프레임)
```
## TLBLookup()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <list>
#include <random>
#include <unordered_map>
#include <vector>

// TLB(Translation Lookaside Buffer): 최근 변환 결과(페이지 번호 → 프레임 번호)를 저장하는 작은 캐시.  적중하면 4 단계 페이지 테이블을 걷지 않아도 된다.
//  유효 접근 시간 EAT = h·(t_tlb + t_mem) + (1 − h)·(t_tlb + 4·t_mem + t_mem)   (미스 시 테이블 4 단계를 걷는 메모리 접근 4 번 + 실제 접근 1 번).  완전 연관 LRU TLB 를 직접 만들어 확인한다.
//  ① 측정한 적중률 h 를 넣은 공식 EAT 가 접근마다 비용을 더한 평균과 같다(부동소수 오차 1e-9)  ② 순차 훑기: 페이지당 1024 번(4 바이트 보폭) 접근하면 적중률이 정확히 1 − 1/1024  ③ 작업 집합 W 쪽을 무작위로 접근: W ≤ TLB 항목 수면 미스는 컴펄서리 W 번뿐, W ≫ 항목 수면 적중률 ≈ 항목 수 / W
//  ④ 큰 페이지: 64 MB 를 무작위 접근할 때 4 KB 페이지(16384 쪽)는 적중률 < 1%, 2 MB 페이지(32 쪽)는 컴펄서리 32 번뿐  ⑤ 주소 공간 식별자(ASID): 프로세스 둘이 K 번 접근마다 교대할 때, ASID 태그가 있으면 미스는 컴펄서리 합뿐이고 문맥 전환마다 TLB 를 비우면 전환마다 작업 집합 쪽수만큼 미스가 생긴다(정확히).
struct Tlb {
    size_t cap; std::list<std::pair<uint32_t, uint64_t>> lru; std::unordered_map<uint64_t, std::list<std::pair<uint32_t, uint64_t>>::iterator> where; long hits = 0, misses = 0;
    explicit Tlb(size_t c) : cap(c) {}
    static uint64_t key(uint32_t asid, uint64_t vpn) { return ((uint64_t)asid << 48) | vpn; }
    bool lookup(uint32_t asid, uint64_t vpn) { auto it = where.find(key(asid, vpn)); if (it != where.end()) { lru.splice(lru.begin(), lru, it->second); ++hits; return true; } ++misses; if (lru.size() == cap) { where.erase(key(lru.back().first, lru.back().second)); lru.pop_back(); } lru.push_front({asid, vpn}); where[key(asid, vpn)] = lru.begin(); return false; }
    void flush() { lru.clear(); where.clear(); }
};

int main() {
    const double tTlb = 1, tMem = 100;
    {   Tlb t(64); std::mt19937_64 rng(1023); double accum = 0; long n = 200000; for (long i = 0; i < n; ++i) { bool hit = t.lookup(0, rng() % 96); accum += hit ? tTlb + tMem : tTlb + 4 * tMem + tMem; }                            // ① 공식 = 직접 누적
        double h = (double)t.hits / n, eat = h * (tTlb + tMem) + (1 - h) * (tTlb + 4 * tMem + tMem); assert(std::fabs(eat - accum / n) < 1e-9 && h > 0.5 && h < 0.8); }
    {   Tlb t(64); long accesses = 0; for (uint64_t page = 0; page < 5000; ++page) for (int k = 0; k < 1024; ++k) { t.lookup(0, page); ++accesses; } assert(t.misses == 5000 && t.hits == accesses - 5000 && std::fabs((double)t.hits / accesses - (1 - 1.0 / 1024)) < 1e-12); }                // ② 순차
    std::mt19937_64 rng(1025);
    for (uint64_t W : {16ULL, 64ULL, 128ULL, 512ULL, 4096ULL}) { Tlb t(64); long n = 400000; for (long i = 0; i < n; ++i) t.lookup(0, rng() % W); double h = (double)t.hits / n;                                        // ③ 작업 집합
        if (W <= 64) assert(t.misses == (long)W); else assert(std::fabs(h - 64.0 / (double)W) < 0.02 + 0.1 * (64.0 / (double)W)); }
    {   Tlb small4k(64), huge2m(64); const uint64_t bytes = 64ULL << 20; long n = 500000; for (long i = 0; i < n; ++i) { uint64_t addr = rng() % bytes; small4k.lookup(0, addr >> 12); huge2m.lookup(0, addr >> 21); }                  // ④ 큰 페이지
        assert((double)small4k.hits / n < 0.01 && huge2m.misses == 32 && huge2m.hits == n - 32); }
    {   const long K = 100, switches = 400; const uint64_t pagesEach = 16; Tlb withAsid(64), flushed(64); for (long s = 0; s < switches; ++s) { uint32_t proc = (uint32_t)(s % 2); flushed.flush(); for (long k = 0; k < K; ++k) { uint64_t vpn = (uint64_t)k % pagesEach; withAsid.lookup(proc, vpn); flushed.lookup(proc, vpn); } }          // ⑤ ASID
        assert(withAsid.misses == 2 * (long)pagesEach && flushed.misses == switches * (long)pagesEach); }
    double h = 0.98, eat = h * (tTlb + tMem) + (1 - h) * (tTlb + 5 * tMem); double noTlb = 5 * tMem; assert(eat < noTlb / 4);
    std::cout << "TLBLookup: the EAT formula equalled the per-access average, a sequential scan hit 1-1/1024, random access over W pages hit about 64/W (only W compulsory misses when W <= 64), 2 MB pages cut 64 MB of random accesses to 32 misses versus a <1% hit rate with 4 KB pages, and ASID tags avoided the " << 400 * 16 << " refill misses a flush-on-switch TLB suffered; at 98% hit rate EAT is " << eat << " vs " << noTlb << " without a TLB" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(1)
// Space Complexity: O(TLB 항목 수)
```
## MemoryMapping()
### 대표코드
```cpp
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <random>
#include <vector>
#if defined(__linux__)
#include <csignal>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 메모리 매핑: mmap 은 가상 주소 범위만 "예약" 하고, 물리 메모리는 페이지를 처음 만졌을 때(요구 페이징) 비로소 배정된다.  mincore 로 어느 페이지가 실제 메모리에 올라와 있는지(resident) 확인할 수 있다.
//  파일 매핑은 파일 내용을 메모리처럼 읽고 쓰게 해 준다 — MAP_PRIVATE 는 쓰면 그 페이지만 복사(copy-on-write)되어 파일은 그대로, MAP_SHARED 는 쓴 내용이 파일에 반영된다.
//  ① 익명 매핑 1000 쪽: 만지기 전 resident 0 개, 3 쪽마다 하나씩 만지면 정확히 그 쪽들만 resident  ② 파일 매핑(읽기 전용)이 read() 로 읽은 내용과 같고 파일 끝 뒤의 같은 쪽 바이트는 0  ③ MAP_PRIVATE 쓰기는 파일을 바꾸지 않는다  ④ MAP_SHARED 무작위 쓰기 5000 번 뒤 msync/munmap 하면 파일이 그림자 배열과 같다
//  ⑤ madvise(MADV_DONTNEED) 뒤 익명 페이지는 0 으로 되돌아온다  ⑥ munmap 한 주소를 읽으면 SIGSEGV (자식 프로세스에서 확인)  ⑦ 보호 변경: mprotect 로 읽기 전용으로 바꾼 쪽에 쓰면 SIGSEGV.  Linux 가 아니면 건너뛴다.
#if defined(__linux__)
bool diesWithSegv(void (*body)(void*), void* arg) { pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); body(arg); _exit(0); } int status = 0; waitpid(pid, &status, 0); return WIFSIGNALED(status) && WTERMSIG(status) == SIGSEGV; }
void readUnmapped(void* p) { volatile char c = *(volatile char*)p; (void)c; }
void writeReadOnly(void* p) { *(volatile char*)p = 1; }
std::vector<unsigned char> readWhole(int fd, size_t n) { std::vector<unsigned char> v(n); size_t got = 0; while (got < n) { ssize_t r = pread(fd, v.data() + got, n - got, (off_t)got); assert(r > 0); got += (size_t)r; } return v; }
#endif

int main() {
#if defined(__linux__)
    const size_t page = (size_t)sysconf(_SC_PAGESIZE); assert(page >= 4096 && (page & (page - 1)) == 0);
    {   const int pages = 1000; unsigned char* m = (unsigned char*)mmap(nullptr, pages * page, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(m != MAP_FAILED); std::vector<unsigned char> vec(pages);
        assert(mincore(m, pages * page, vec.data()) == 0); for (int i = 0; i < pages; ++i) assert(!(vec[i] & 1));                                                                       // ① 만지기 전
        for (int i = 0; i < pages; i += 3) m[(size_t)i * page] = 1; assert(mincore(m, pages * page, vec.data()) == 0); int resident = 0; for (int i = 0; i < pages; ++i) { bool r = vec[i] & 1; assert(r == (i % 3 == 0)); resident += r; } assert(resident == 334);
        for (int i = 0; i < pages; i += 3) assert(m[(size_t)i * page] == 1); madvise(m, pages * page, MADV_DONTNEED); for (int i = 0; i < pages; i += 3) assert(m[(size_t)i * page] == 0);          // ⑤ DONTNEED → 0 으로 되돌아옴
        munmap(m, pages * page); }
    char path[] = "/tmp/memmapXXXXXX"; int fd = mkstemp(path); assert(fd >= 0); unlink(path);
    const size_t fileSize = 5 * page + 1234; std::vector<unsigned char> content(fileSize); std::mt19937 rng(1027); for (auto& b : content) b = (unsigned char)(rng() | 1); assert(write(fd, content.data(), fileSize) == (ssize_t)fileSize);
    {   size_t mapLen = 6 * page; const unsigned char* ro = (const unsigned char*)mmap(nullptr, mapLen, PROT_READ, MAP_PRIVATE, fd, 0); assert(ro != MAP_FAILED);                                            // ② 읽기 전용 파일 매핑
        assert(std::memcmp(ro, content.data(), fileSize) == 0); for (size_t i = fileSize; i < 6 * page; ++i) assert(ro[i] == 0); munmap((void*)ro, mapLen); }                                              // 파일 끝 뒤 같은 쪽은 0
    {   unsigned char* priv = (unsigned char*)mmap(nullptr, fileSize, PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0); assert(priv != MAP_FAILED); for (size_t i = 0; i < fileSize; i += 97) priv[i] ^= 0xFF;          // ③ MAP_PRIVATE: 쓰기 → 복사
        assert(readWhole(fd, fileSize) == content && priv[0] == (unsigned char)(content[0] ^ 0xFF)); munmap(priv, fileSize); }
    {   unsigned char* shared = (unsigned char*)mmap(nullptr, fileSize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0); assert(shared != MAP_FAILED); std::vector<unsigned char> shadow = content;                      // ④ MAP_SHARED: 파일에 반영
        for (int i = 0; i < 5000; ++i) { size_t pos = rng() % fileSize; unsigned char v = (unsigned char)rng(); shared[pos] = v; shadow[pos] = v; }
        assert(msync(shared, fileSize, MS_SYNC) == 0); assert(readWhole(fd, fileSize) == shadow); munmap(shared, fileSize); assert(readWhole(fd, fileSize) == shadow); content = shadow; }
    {   unsigned char* m = (unsigned char*)mmap(nullptr, 2 * page, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(m != MAP_FAILED); m[0] = 7; assert(mprotect(m, page, PROT_READ) == 0); assert(m[0] == 7);                          // ⑦ 읽기 전용 쪽에 쓰면 SIGSEGV
        assert(diesWithSegv(writeReadOnly, m)); assert(mprotect(m, page, PROT_READ | PROT_WRITE) == 0); m[0] = 8; assert(m[0] == 8);
        munmap(m, 2 * page); assert(diesWithSegv(readUnmapped, m)); }                                                                                                                                  // ⑥ munmap 한 주소
    close(fd);
    std::cout << "MemoryMapping: mincore showed exactly every third page resident after touching them, a read-only file mapping matched read(), MAP_PRIVATE writes left the file untouched while 5000 MAP_SHARED writes reproduced the shadow array in the file, MADV_DONTNEED zeroed anonymous pages, and reading an unmapped or writing a read-only page raised SIGSEGV" << std::endl;
#else
    std::cout << "MemoryMapping: skipped (POSIX mmap required)" << std::endl;
#endif
    return 0;
}
// Time Complexity: 매핑 O(1), 쪽 접근은 처음 만질 때 폴트 한 번
// Space Complexity: 만진 쪽 수만큼 물리 메모리
```
# Part 10. 메모리 보호
## ReadOnlyMemory()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#if defined(__unix__) || defined(__APPLE__)
#include <csignal>
#include <cstdio>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
enum Outcome { OK, SEGV, OTHER };
template <class F> Outcome inChild(F f) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); f(); _exit(0); } int st = 0; waitpid(pid, &st, 0);
    if (WIFEXITED(st) && WEXITSTATUS(st) == 0) return OK; if (WIFSIGNALED(st) && WTERMSIG(st) == SIGSEGV) return SEGV; return OTHER; }       // 자식 프로세스에서 시도해 정상 종료 / SIGSEGV 를 구분
#endif

// 읽기 전용 메모리: 페이지 테이블의 writable 비트를 끄면 쓰기는 하드웨어가 막고 운영체제가 SIGSEGV 를 보낸다.  문자열 리터럴·const 전역은 .rodata(읽기 전용) 페이지에 놓인다.  mprotect 로 직접 보호를 걸고 위반을 *자식 프로세스에서* 안전하게 관찰한다.
//  ① 보호 3 종(PROT_NONE / PROT_READ / PROT_READ|PROT_WRITE) × 접근 2 종(읽기 / 쓰기)의 6 가지 조합 모두에서 결과가 규칙(읽기 허용 ⇔ 보호 ≠ NONE, 쓰기 허용 ⇔ 읽기+쓰기)과 같다  ② 보호를 바꾸면 커널의 지도(/proc/self/maps)에 권한 문자열(`---p` / `r--p` / `rw-p`)이 그대로 나타난다
//  ③ 쓰기 보호 → 쓰기 시도(SIGSEGV 로 거부, 값 불변) → 권한 복구 → 쓰기 성공 을 20 번 반복  ④ 문자열 리터럴에 쓰면 자식이 SIGSEGV 로 죽는다  ⑤ 읽기 전용으로 바꾸는 시점의 내용이 보존된다.
#if defined(__linux__)
std::string permsOf(const void* addr) { std::ifstream f("/proc/self/maps"); std::string line; uintptr_t a = (uintptr_t)addr; while (std::getline(f, line)) { std::istringstream in(line); std::string range, perms; in >> range >> perms; size_t dash = range.find('-'); uintptr_t lo = std::stoull(range.substr(0, dash), nullptr, 16), hi = std::stoull(range.substr(dash + 1), nullptr, 16); if (a >= lo && a < hi) return perms; } return ""; }
#endif
int main() {
#if defined(__unix__) || defined(__APPLE__)
    long ps = sysconf(_SC_PAGESIZE);
    for (int prot : {PROT_NONE, PROT_READ, PROT_READ | PROT_WRITE}) for (int op = 0; op < 2; ++op) {                                    // ① 6 가지 조합
        char* p = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(p != MAP_FAILED); p[0] = 'A';
        Outcome got = inChild([&] { mprotect(p, ps, prot); if (op == 0) { volatile char c = ((volatile char*)p)[0]; (void)c; } else ((volatile char*)p)[0] = 'B'; });
        bool allowed = op == 0 ? prot != PROT_NONE : prot == (PROT_READ | PROT_WRITE); assert(got == (allowed ? OK : SEGV)); assert(p[0] == 'A'); munmap(p, ps); }          // 부모의 값은 자식의 시도에 영향받지 않는다
    char* p = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(p != MAP_FAILED);
    std::memset(p, 'A', 64); assert(mprotect(p, ps, PROT_READ) == 0); for (int i = 0; i < 64; ++i) assert(p[i] == 'A');                                    // ⑤ 읽기 전용이 되어도 내용 보존
#if defined(__linux__)
    assert(permsOf(p) == "r--p"); mprotect(p, ps, PROT_NONE); assert(permsOf(p) == "---p"); mprotect(p, ps, PROT_READ | PROT_WRITE); assert(permsOf(p) == "rw-p");     // ② 커널 지도에 반영
#endif
    for (int round = 0; round < 20; ++round) { assert(mprotect(p, ps, PROT_READ) == 0); assert(inChild([&] { ((volatile char*)p)[round] = 'Z'; }) == SEGV); assert(p[round] == 'A'); assert(mprotect(p, ps, PROT_READ | PROT_WRITE) == 0); p[round] = 'C'; assert(p[round] == 'C'); }          // ③
    munmap(p, ps);
    volatile char* literal = (volatile char*)"a string literal lives in .rodata"; assert(literal[0] == 'a'); assert(inChild([&] { literal[0] = 'X'; }) == SEGV);              // ④ 문자열 리터럴
    std::cout << "ReadOnlyMemory: all 6 protection x access combinations behaved as specified (verified in child processes), /proc/self/maps showed the permission strings, 20 protect-write-unprotect cycles left the data intact, and writing a string literal killed the child with SIGSEGV" << std::endl;
#else
    std::cout << "ReadOnlyMemory: POSIX-only demonstration (mprotect + SIGSEGV)" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ExecuteOnlyMemory()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#if defined(__unix__) || defined(__APPLE__)
#include <csignal>
#include <cstdio>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
enum Outcome { OK, SEGV, OTHER };
template <class F> Outcome inChild(F f) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); f(); _exit(0); } int st = 0; waitpid(pid, &st, 0);
    if (WIFEXITED(st) && WEXITSTATUS(st) == 0) return OK; if (WIFSIGNALED(st) && WTERMSIG(st) == SIGSEGV) return SEGV; return OTHER; }       // 자식 프로세스에서 시도해 정상 종료 / SIGSEGV 를 구분
#endif

// W^X(Write XOR Execute): 한 페이지가 동시에 "쓰기 가능" 이면서 "실행 가능" 해서는 안 된다는 정책.  코드 주입 공격을 막는다.  JIT 컴파일러의 정석 절차: RW 로 매핑 → 기계어 쓰기 → (명령 캐시 비우기) → RX 로 전환 → 실행.  (순수한 실행 전용 X-only 는 CPU 가 PKU/ARM 등을 지원해야 한다)
//  여기서는 두 정수 인자 (a, b) 로 `a·C1 + b·C2 + C3` 을 계산하는 x86-64 기계어를 *실제로 만들어* 실행한다 (SysV: a = edi, b = esi, 결과 = eax): imul eax,edi,C1 (69 C7 imm32) · imul ecx,esi,C2 (69 CE imm32) · add eax,ecx (01 C8) · add eax,C3 (05 imm32) · ret (C3).
//  ① 무작위 계수 300 개로 JIT 한 함수가 모든 입력에서 C++ 32 비트 mod 2^32 산술과 같은 값을 돌려준다  ② 실행 중인 JIT 페이지의 권한은 `r-xp` (`rwx` 가 아니다) — 쓰는 동안만 `rw-p`  ③ RX 로 바꾼 뒤 코드를 고쳐 쓰려 하면 자식이 SIGSEGV
//  ④ RW 상태에서 만든 코드는 실행하려 하면 SIGSEGV (NX)  ⑤ 코드를 *고쳐 쓰는* 올바른 절차: RW 로 되돌려 수정 → RX 로 전환 → 새 결과.  x86-64 Linux 가 아니면 건너뛴다.
#if defined(__linux__) && defined(__x86_64__)
std::string permsOf(const void* addr) { std::ifstream f("/proc/self/maps"); std::string line; uintptr_t a = (uintptr_t)addr; while (std::getline(f, line)) { std::istringstream in(line); std::string range, perms; in >> range >> perms; size_t dash = range.find('-'); uintptr_t lo = std::stoull(range.substr(0, dash), nullptr, 16), hi = std::stoull(range.substr(dash + 1), nullptr, 16); if (a >= lo && a < hi) return perms; } return ""; }
void emit32(std::vector<unsigned char>& c, uint32_t v) { for (int i = 0; i < 4; ++i) c.push_back((unsigned char)(v >> (8 * i))); }
std::vector<unsigned char> compileLinear(int32_t c1, int32_t c2, int32_t c3) { std::vector<unsigned char> c; c.push_back(0x69); c.push_back(0xC7); emit32(c, (uint32_t)c1); c.push_back(0x69); c.push_back(0xCE); emit32(c, (uint32_t)c2); c.push_back(0x01); c.push_back(0xC8); c.push_back(0x05); emit32(c, (uint32_t)c3); c.push_back(0xC3); return c; }
int32_t reference(int32_t a, int32_t b, int32_t c1, int32_t c2, int32_t c3) { return (int32_t)((uint32_t)a * (uint32_t)c1 + (uint32_t)b * (uint32_t)c2 + (uint32_t)c3); }
typedef int32_t (*Fn)(int32_t, int32_t);
#endif

int main() {
#if defined(__linux__) && defined(__x86_64__)
    long ps = sysconf(_SC_PAGESIZE); std::mt19937 rng(1029);
    unsigned char* code = (unsigned char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(code != MAP_FAILED);
    {   std::vector<unsigned char> prog = compileLinear(1, 0, 42); std::memcpy(code, prog.data(), prog.size()); assert(permsOf(code) == "rw-p");                         // 쓰는 동안은 rw-p
        assert(inChild([&] { ((Fn)code)(1, 2); }) == SEGV);                                                                                                                  // ④ NX: RW 페이지는 실행 불가
        __builtin___clear_cache((char*)code, (char*)code + prog.size()); assert(mprotect(code, ps, PROT_READ | PROT_EXEC) == 0); assert(permsOf(code) == "r-xp");              // ② RX 로 전환
        Fn fn = (Fn)code; assert(fn(5, 9) == 47); assert(inChild([&] { code[1] = 0x00; }) == SEGV); }                                                                        // ③ RX 에 쓰면 SIGSEGV
    for (int it = 0; it < 300; ++it) { int32_t c1 = (int32_t)rng(), c2 = (int32_t)rng(), c3 = (int32_t)rng(); assert(mprotect(code, ps, PROT_READ | PROT_WRITE) == 0);                  // ⑤ 고쳐 쓰기: RW → 수정 → RX
        std::vector<unsigned char> prog = compileLinear(c1, c2, c3); std::memcpy(code, prog.data(), prog.size()); __builtin___clear_cache((char*)code, (char*)code + prog.size()); assert(mprotect(code, ps, PROT_READ | PROT_EXEC) == 0); assert(permsOf(code) == "r-xp");
        Fn fn = (Fn)code; for (int k = 0; k < 40; ++k) { int32_t a = (int32_t)rng(), b = (int32_t)rng(); assert(fn(a, b) == reference(a, b, c1, c2, c3)); } assert(fn(0, 0) == c3 && fn(1, 0) == (int32_t)((uint32_t)c1 + (uint32_t)c3)); }                  // ① 모든 입력에서 같다
    munmap(code, ps);
    std::cout << "ExecuteOnlyMemory: JIT-compiled linear functions a*C1+b*C2+C3 matched 32-bit wrap-around arithmetic for 300 random coefficient sets, the code page was rw-p while written and r-xp while executed (never rwx), executing an RW page and writing an RX page both killed the child with SIGSEGV" << std::endl;
#else
    std::cout << "ExecuteOnlyMemory: Linux x86-64 demonstration only" << std::endl;
#endif
    return 0;
}
// Time Complexity: 코드 생성 O(길이), 호출 O(1)
// Space Complexity: O(페이지)
```
## MemoryProtection()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#if defined(__unix__) || defined(__APPLE__)
#include <csignal>
#include <cstdio>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
enum Outcome { OK, SEGV, OTHER };
template <class F> Outcome inChild(F f) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); f(); _exit(0); } int st = 0; waitpid(pid, &st, 0);
    if (WIFEXITED(st) && WEXITSTATUS(st) == 0) return OK; if (WIFSIGNALED(st) && WTERMSIG(st) == SIGSEGV) return SEGV; return OTHER; }       // 자식 프로세스에서 시도해 정상 종료 / SIGSEGV 를 구분
#endif

// 메모리 보호: 페이지마다 R/W/X 권한 비트를 두어 접근 종류가 권한과 맞지 않으면 예외를 낸다.  (1) 권한 모델  (2) 가드 페이지: PROT_NONE 페이지를 경계에 놓아 오버플로를 즉시 잡는다.
//  가드 페이지 할당기(electric fence): n 바이트 버퍼의 *끝*이 페이지 경계에 딱 닿도록 놓고 바로 뒤 페이지를 PROT_NONE 으로 둔다 → 한 바이트만 넘어도 SIGSEGV.  정렬을 맞추려고 끝을 16 바이트 배수로 올리면 그 여유분(< 16 바이트)만큼은 오버플로를 *놓친다* — 정밀도와 정렬의 교환.
//  ① 권한 모델 표: 코드 R|X, 데이터 R|W, 상수 R 의 허용/거부 8 × 3 전수  ② 무작위 크기 n(1..12000)의 정밀 가드 버퍼(정렬 1): 앞의 n 바이트는 모두 읽고 쓸 수 있고 n 번째 바이트(한 바이트 넘김)는 자식에서 SIGSEGV  ③ 정렬 16 버퍼: 끝이 16 의 배수로 올려지므로 n 바이트 뒤 (올림 − n) 바이트까지는 넘어가도 조용하고 그다음 바이트는 SIGSEGV (정확한 임계)
//  ④ 언더플로 가드(앞 페이지 PROT_NONE): 데이터 영역 첫 바이트 바로 앞 바이트를 읽으면 SIGSEGV  ⑤ 가드 페이지가 커널 지도에서 `---p` 로 보임.
enum Perm : unsigned { R = 1, W = 2, X = 4 };
bool allowed(unsigned perm, char access) { return (perm & (access == 'r' ? R : access == 'w' ? W : X)) != 0; }
#if defined(__unix__) || defined(__APPLE__)
struct Guarded { unsigned char* base; size_t pages; unsigned char* ptr; size_t n; };
Guarded guardedAlloc(size_t n, size_t align, bool underflow) { long ps = sysconf(_SC_PAGESIZE); size_t dataPages = (n + ps - 1) / ps; size_t total = dataPages + 1 + (underflow ? 1 : 0);
    unsigned char* base = (unsigned char*)mmap(nullptr, total * ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(base != MAP_FAILED);
    size_t dataStart = underflow ? ps : 0, guardOffset = dataStart + dataPages * ps; mprotect(base + guardOffset, ps, PROT_NONE); if (underflow) mprotect(base, ps, PROT_NONE);
    size_t endAligned = guardOffset; size_t rounded = (n + align - 1) / align * align; unsigned char* ptr = base + endAligned - rounded;                          // 올림한 끝이 가드 바로 앞에 닿는다
    return {base, total, ptr, n}; }
void guardedFree(Guarded g) { munmap(g.base, g.pages * sysconf(_SC_PAGESIZE)); }
#endif

int main() {
    unsigned code = R | X, data = R | W, rodata = R;                                                              // ① 권한 모델
    for (unsigned perm = 0; perm < 8; ++perm) for (char acc : {'r', 'w', 'x'}) { bool want = (perm & (acc == 'r' ? 1u : acc == 'w' ? 2u : 4u)) != 0; assert(allowed(perm, acc) == want); }
    assert(allowed(code, 'x') && !allowed(code, 'w') && allowed(data, 'w') && !allowed(data, 'x') && allowed(rodata, 'r') && !allowed(rodata, 'w') && !allowed(rodata, 'x'));
#if defined(__unix__) || defined(__APPLE__)
    std::mt19937 rng(1031); long ps = sysconf(_SC_PAGESIZE);
    for (int it = 0; it < 40; ++it) { size_t n = 1 + rng() % 12000; Guarded g = guardedAlloc(n, 1, false); for (size_t i = 0; i < n; ++i) g.ptr[i] = (unsigned char)i; for (size_t i = 0; i < n; ++i) assert(g.ptr[i] == (unsigned char)i);                    // ② 정밀 가드
        assert((uintptr_t)(g.ptr + n) % ps == 0); assert(inChild([&] { volatile unsigned char c = g.ptr[n]; (void)c; }) == SEGV); assert(inChild([&] { g.ptr[n - 1] = 1; }) == OK); guardedFree(g); }
    for (int it = 0; it < 40; ++it) { size_t n = 1 + rng() % 5000; Guarded g = guardedAlloc(n, 16, false); size_t rounded = (n + 15) / 16 * 16, slack = rounded - n; assert((uintptr_t)g.ptr % 16 == 0 && (uintptr_t)(g.ptr + rounded) % ps == 0);                    // ③ 정렬 16
        for (size_t i = 0; i < n; ++i) g.ptr[i] = 1; if (slack > 0) assert(inChild([&] { g.ptr[n + slack - 1] = 1; }) == OK);                                                                          // 여유분 안의 오버플로는 놓친다
        assert(inChild([&] { g.ptr[n + slack] = 1; }) == SEGV); guardedFree(g); }
    {   Guarded g = guardedAlloc(100, 1, true); std::memset(g.ptr, 7, 100);
        unsigned char* firstDataByte = g.base + ps; assert(inChild([&] { volatile unsigned char c = *(firstDataByte - 1); (void)c; }) == SEGV); guardedFree(g); }                                                          // ④ 앞 가드 페이지
#if defined(__linux__)
    {   Guarded g = guardedAlloc(100, 1, false); std::string perms; { FILE* f = std::fopen("/proc/self/maps", "r"); char line[512]; uintptr_t a = (uintptr_t)(g.ptr + 100); while (std::fgets(line, sizeof line, f)) { unsigned long lo, hi; char p[8]; if (std::sscanf(line, "%lx-%lx %7s", &lo, &hi, p) == 3 && a >= lo && a < hi) perms = p; } std::fclose(f); } assert(perms == "---p"); guardedFree(g); }                       // ⑤
#endif
    std::cout << "MemoryProtection: the permission table matched all 24 (perm, access) pairs; a page-end guard buffer caught a 1-byte overflow for 40 random sizes, a 16-byte-aligned buffer missed overflows only inside its exact rounding slack, an underflow guard page trapped the byte just before the data region, and the guard showed up as '---p' in /proc/self/maps" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 가드 페이지 1개 (4KB)
```
## StackCanary()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

// 스택 카나리: 지역 버퍼와 복귀 주소 사이에 비밀 난수(카나리)를 둔다.  버퍼 오버플로로 복귀 주소를 덮으려면 반드시 카나리를 먼저 덮게 되므로, 함수가 반환하기 직전에 카나리가 그대로인지 확인해 공격을 탐지한다 (gcc -fstack-protector).
//  스택 프레임 한 칸을 바이트 배열로 흉내 낸 안전한 시뮬레이션이다: [ buf(8) | canary(8) | return address(8) ].  glibc 의 카나리는 *가장 낮은 바이트가 0x00* 인 "종결자 카나리"라 strcpy 류의 복사(NUL 에서 멈춤)로는 카나리를 되살려 쓸 수 없다.
//  ① 겹쳐 쓰는 길이 n = 0..24 전수(memcpy 류): 카나리 훼손 ⇔ n > 8, 복귀 주소 훼손 ⇔ n > 16 이고, 카나리 검사를 켜면 훼손 시 *복귀 주소를 쓰기 전에* 탐지, 끄면 n > 16 에서 제어 흐름 탈취  ② 카나리가 유출된 공격자(정확한 카나리를 되살려 쓰며 복귀 주소만 바꿈): memcpy 류 복사에는 *항상 성공*, strcpy 류 복사는 종결자 카나리에 *단 한 번도 성공하지 못함*(NUL 에서 멈춤), 종결자 없는 카나리에는 strcpy 도 성공(공격 주소의 낮은 두 바이트에 0 이 없을 때 — strcpy 는 어차피 NUL 이 든 주소를 못 쓴다)
//  ③ 바이트 단위 무차별 대입(BROP): 카나리가 자식 프로세스마다 *그대로 재사용*되는 포크 서버에는 요청 ≤ 7 × 256 번으로 7 바이트를 모두 알아내지만, 요청마다 카나리가 새로 정해지면 같은 전략이 실패  ④ 카나리 엔트로피: 7 바이트 = 56 비트.
struct Frame { unsigned char mem[24]; };
enum Result { SAFE, DETECTED, HIJACKED };
uint64_t makeCanary(std::mt19937_64& rng, bool terminator) { uint64_t c = rng(); if (terminator) c &= ~0xFFULL; else { for (int i = 0; i < 8; ++i) if (((c >> (8 * i)) & 0xFF) == 0) c |= 1ULL << (8 * i); } return c; }                     // 종결자 카나리: 가장 낮은 바이트가 0
void enter(Frame& f, uint64_t canary, uint64_t ret) { std::memset(f.mem, 0, sizeof f.mem); std::memcpy(f.mem + 8, &canary, 8); std::memcpy(f.mem + 16, &ret, 8); }
void copyMem(Frame& f, const unsigned char* input, size_t n) { std::memcpy(f.mem, input, std::min<size_t>(n, sizeof f.mem)); }                          // memcpy 류: 길이만큼 (NUL 도 복사)
void copyStr(Frame& f, const unsigned char* input, size_t n) { for (size_t i = 0; i < n && i < sizeof f.mem; ++i) { f.mem[i] = input[i]; if (input[i] == 0) break; } }       // strcpy 류: NUL 을 복사하고 멈춘다
Result leave(const Frame& f, uint64_t canary, uint64_t ret, bool check, uint64_t* usedRet = nullptr) { uint64_t c, r; std::memcpy(&c, f.mem + 8, 8); std::memcpy(&r, f.mem + 16, 8);
    if (check && c != canary) return DETECTED; if (usedRet) *usedRet = r; return r != ret ? HIJACKED : SAFE; }                                                                                                  // 검사를 켜면 복귀 주소를 쓰기 전에 탐지

int main() {
    std::mt19937_64 rng(1033); const uint64_t RET = 0x400123;
    for (size_t n = 0; n <= 24; ++n) { uint64_t canary = makeCanary(rng, true) | 0x0102030405060700ULL; unsigned char attack[24]; std::memset(attack, 'A', sizeof attack);                                      // ① 길이 전수 (카나리 바이트가 'A' 와 다르게)
        Frame f; enter(f, canary, RET); copyMem(f, attack, n); uint64_t c, r; std::memcpy(&c, f.mem + 8, 8); std::memcpy(&r, f.mem + 16, 8);
        assert((c != canary) == (n > 8) && (r != RET) == (n > 16));
        Result on = leave(f, canary, RET, true), off = leave(f, canary, RET, false); assert(on == (n > 8 ? DETECTED : SAFE) && off == (n > 16 ? HIJACKED : SAFE)); if (n > 16) { unsigned char rb[8]; std::memcpy(rb, &r, 8); unsigned char orig[8]; std::memcpy(orig, &RET, 8); for (size_t i = 0; i < 8; ++i) assert(rb[i] == (i < n - 16 ? 0x41 : orig[i])); } }          // 복귀 주소는 (n − 16) 바이트만큼 'A' 로 덮인다
    long memcpySuccess = 0, strcpySuccess = 0, strcpyNoTerminator = 0, evilHasNoZeroLowBytes = 0; const int T = 100000;
    for (int it = 0; it < T; ++it) {                                                                                                                                                              // ② 카나리 유출 공격
        for (int variant = 0; variant < 2; ++variant) { uint64_t canary = makeCanary(rng, variant == 0); uint64_t evil = 0xBADC0DE0ULL + (rng() & 0xFFFF); unsigned char payload[24]; std::memset(payload, 'A', 8); std::memcpy(payload + 8, &canary, 8); std::memcpy(payload + 16, &evil, 8);   // 유출된 카나리를 그대로 되살려 쓴다
            Frame f; enter(f, canary, RET); copyMem(f, payload, 24); uint64_t used = 0; Result r1 = leave(f, canary, RET, true, &used); if (variant == 0) { memcpySuccess += (r1 == HIJACKED && used == evil); }
            Frame g; enter(g, canary, RET); copyStr(g, payload, 24); Result r2 = leave(g, canary, RET, true, &used); if (variant == 0) strcpySuccess += (r2 == HIJACKED); else { strcpyNoTerminator += (r2 == HIJACKED && used == evil); evilHasNoZeroLowBytes += ((evil & 0xFF) && (evil >> 8 & 0xFF)); } } }
    assert(memcpySuccess == T && strcpySuccess == 0 && strcpyNoTerminator == evilHasNoZeroLowBytes && evilHasNoZeroLowBytes > T * 99 / 100);     // 종결자 카나리는 strcpy 류 공격을 완전히 막는다; 종결자 없는 카나리에는 strcpy 도 성공 — 공격 주소에 0 바이트가 없을 때(주소의 NUL 때문에 실패하는 경우를 제외하면 100%)
    {   struct Server { uint64_t canary; bool rerandomize; std::mt19937_64* rng; long requests = 0; bool crashes(const unsigned char* payload, size_t n) { ++requests; if (rerandomize) canary = makeCanary(*rng, true); Frame f; enter(f, canary, RET); copyMem(f, payload, n); uint64_t c; std::memcpy(&c, f.mem + 8, 8); return c != canary; } };          // ③ 포크 서버 vs 재무작위 서버
        for (int world = 0; world < 2; ++world) { int successes = 0; long maxRequests = 0; for (int trial = 0; trial < 20; ++trial) { Server s{makeCanary(rng, true), world == 1, &rng}; unsigned char payload[24]; std::memset(payload, 'A', 8); uint64_t known = 0;       // 하위 바이트(0x00)는 알려져 있다
                for (int k = 1; k < 8; ++k) { int found = -1; for (int g = 0; g < 256; ++g) { uint64_t trialCanary = known | ((uint64_t)g << (8 * k)); std::memcpy(payload + 8, &trialCanary, 8); if (!s.crashes(payload, 8 + k + 1)) { found = g; break; } } if (found < 0) { known = ~0ULL; break; } known |= (uint64_t)found << (8 * k); }
                bool ok = known == s.canary; successes += ok; maxRequests = std::max(maxRequests, s.requests); }
            if (world == 0) assert(successes == 20 && maxRequests <= 7 * 256); else assert(successes == 0); } }                                                                                         // 포크 서버는 ≤ 1792 번에 뚫리고 재무작위 서버는 못 뚫는다
    std::cout << "StackCanary: overwrite lengths 0..24 corrupted the canary exactly beyond 8 bytes and the return address beyond 16 (detected before use when checked), a leaked canary beat memcpy-style overflows " << memcpySuccess << "/" << T << " times but a terminator canary stopped strcpy-style ones " << strcpySuccess << "/" << T << " times, byte-by-byte brute force recovered a fork-server canary in at most " << 7 * 256 << " requests yet failed against re-randomised canaries, and 7 unknown bytes = 56 bits of entropy" << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
// Space Complexity: 프레임당 8바이트
```
## ASLR()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>
#if defined(__linux__)
#include <unistd.h>
#endif

// ASLR(주소 공간 배치 무작위화): 프로세스를 시작할 때마다 스택·힙·라이브러리(·PIE 실행 파일)의 위치를 무작위로 옮겨, 공격자가 목표 주소를 미리 알 수 없게 한다.
// 확인: 자기 자신을 두 번 실행(popen)해 스택 주소를 비교한다.  /proc/sys/kernel/randomize_va_space: 0 = 끔, 1 = 스택·mmap, 2 = 힙 포함 전체
// 이 예제는 무작위화의 "효과"를 수치로 확인한다 (리눅스 x86-64 와 비슷한 엔트로피: 스택 22비트, mmap 28비트, brk 힙 13비트, PIE 실행 파일 28비트 — 모두 4KB 페이지 단위):
//  ① 배치 모형 10 만 개: 모든 영역이 자기 창(window) 안, 4KB 정렬, 정규 주소, 창끼리 겹치지 않음  ② 균일성: 6비트 영역을 64 만 번 뽑아 카이제곱(자유도 63)이 120 미만
//  ③ 맹목적 추측: 10비트 영역에 고정 주소를 2^21 번 찍으면 적중이 2^11 번 근처(5 시그마 안)  ④ 공격 비용: 충돌 후 매번 새로 무작위화하면 평균 2^n 번(기하분포), fork 서버처럼 배치가 안 바뀌면 후보를 차례로 시도해 평균 정확히 (2^n + 1) / 2
//  ⑤ 정보 누출 한 번이면 끝: 영역 안 포인터 하나와 알려진 오프셋으로 기준 주소가 정확히 복원  ⑥ 독립 영역의 엔트로피는 합: 3 + 4 + 2 = 9 비트 설정에서 경험적 엔트로피 ≈ 9 비트이고 512 가지 조합이 고르게 나옴  ⑦ PIE 가 아니면(0 비트) 항상 같은 주소
//  ⑧ (리눅스) 실제 프로세스 두 개의 스택 주소 비교
const uint64_t PAGE = 4096;
struct Window { uint64_t lo, hi; };                                                       // [lo, hi) 안에서만 놓일 수 있다
struct Layout { uint64_t exe, heap, mmapBase, stack; };
struct Config { unsigned exeBits, heapBits, mmapBits, stackBits; };

class Randomizer {
    std::mt19937_64 rng; Config c;
    uint64_t pick(unsigned bits) { return bits ? (rng() & ((1ULL << bits) - 1)) : 0; }
public:
    Randomizer(uint64_t seed, Config cfg) : rng(seed), c(cfg) {}
    Layout next() {
        Layout l; l.exe = 0x555500000000ULL + pick(c.exeBits) * PAGE; l.heap = 0x568000000000ULL + pick(c.heapBits) * PAGE;
        l.mmapBase = 0x7f0000000000ULL - pick(c.mmapBits) * PAGE; l.stack = 0x7ffffffff000ULL - pick(c.stackBits) * PAGE; return l;
    }
    static Window exeWin(const Config& c) { return {0x555500000000ULL, 0x555500000000ULL + ((1ULL << c.exeBits) << 12)}; }
    static Window heapWin(const Config& c) { return {0x568000000000ULL, 0x568000000000ULL + ((1ULL << c.heapBits) << 12)}; }
    static Window mmapWin(const Config& c) { return {0x7f0000000000ULL - (((1ULL << c.mmapBits) - 1) << 12), 0x7f0000000000ULL + 1}; }
    static Window stackWin(const Config& c) { return {0x7ffffffff000ULL - (((1ULL << c.stackBits) - 1) << 12), 0x7ffffffff000ULL + 1}; }
};
bool inWin(uint64_t a, Window w) { return a >= w.lo && a < w.hi; }
bool disjoint(Window a, Window b) { return a.hi <= b.lo || b.hi <= a.lo; }
bool canonicalUser(uint64_t a) { return a < (1ULL << 47); }

int main(int argc, char** argv) {
#if defined(__linux__)
    if (argc == 2 && std::string(argv[1]) == "child") { int local; std::printf("%lx\n", (unsigned long)&local); return 0; }
#else
    (void)argc; (void)argv;
#endif
    const Config linuxLike{28, 13, 28, 22};
    // ① 배치 모형
    {   Randomizer r(1, linuxLike); Window w[4] = {Randomizer::exeWin(linuxLike), Randomizer::heapWin(linuxLike), Randomizer::mmapWin(linuxLike), Randomizer::stackWin(linuxLike)};
        for (int i = 0; i < 4; ++i) for (int j = i + 1; j < 4; ++j) assert(disjoint(w[i], w[j]));                                    // 창이 서로 겹치지 않으므로 어떤 배치에서도 영역이 겹칠 수 없다
        for (int i = 0; i < 100000; ++i) {
            Layout l = r.next(); uint64_t v[4] = {l.exe, l.heap, l.mmapBase, l.stack};
            for (int k = 0; k < 4; ++k) { assert(inWin(v[k], w[k]) && v[k] % PAGE == 0 && canonicalUser(v[k])); }
        } }
    // ② 균일성
    {   Randomizer r(2, {0, 0, 6, 0}); std::vector<long> cnt(64, 0); const long N = 640000; for (long i = 0; i < N; ++i) { uint64_t off = (0x7f0000000000ULL - r.next().mmapBase) / PAGE; ++cnt[off]; }
        double chi = 0, e = N / 64.0; for (long c : cnt) chi += (c - e) * (c - e) / e; assert(chi < 120); }
    // ③ 맹목적 추측
    {   Randomizer r(3, {0, 0, 10, 0}); const uint64_t guess = 0x7f0000000000ULL - 517 * PAGE; const long N = 1L << 21; long hits = 0; for (long i = 0; i < N; ++i) hits += r.next().mmapBase == guess;
        double expect = N / 1024.0, sd = std::sqrt(expect); assert(std::abs(hits - expect) < 5 * sd); }
    // ④ 공격 비용
    {   const unsigned bits = 6; const uint64_t N = 1ULL << bits; Randomizer r(4, {0, 0, bits, 0}); double total = 0; const int TR = 3000;
        for (int t = 0; t < TR; ++t) { long tries = 0; const uint64_t g = 0x7f0000000000ULL - 11 * PAGE; do { ++tries; } while (r.next().mmapBase != g); total += (double)tries; }       // 충돌할 때마다 새 배치
        assert(std::abs(total / TR - (double)N) < 0.1 * (double)N);                                                                   // 기하분포: 평균 2^n
        double sum = 0; for (uint64_t secret = 0; secret < N; ++secret) { uint64_t tries = 0; for (uint64_t cand = 0; cand < N; ++cand) { ++tries; if (cand == secret) break; } sum += (double)tries; }
        assert(sum / (double)N == (double)(N + 1) / 2);                                                                              // 배치가 고정이면 평균 (2^n + 1) / 2 — 새로 무작위화하는 쪽(평균 2^n)의 절반
    }
    // ⑤ 정보 누출 한 번
    {   Randomizer r(5, linuxLike); const uint64_t knownOffsetOfFunction = 0x2a4d0;                                                  // 라이브러리 안의 함수 오프셋은 파일에서 알 수 있다
        for (int i = 0; i < 10000; ++i) { Layout l = r.next(); uint64_t leaked = l.mmapBase + knownOffsetOfFunction; assert(leaked - knownOffsetOfFunction == l.mmapBase); } }
    // ⑥ 엔트로피는 합
    {   Randomizer r(6, {0, 3, 4, 2}); std::map<std::vector<uint64_t>, long> freq; const long N = 200000;
        for (long i = 0; i < N; ++i) { Layout l = r.next(); ++freq[{l.heap, l.mmapBase, l.stack}]; }
        assert(freq.size() == 512); double chi = 0, e = N / 512.0, H = 0; for (auto& kv : freq) { chi += (kv.second - e) * (kv.second - e) / e; double p = (double)kv.second / N; H -= p * std::log2(p); }
        assert(chi < 640 && std::abs(H - 9.0) < 0.01); }
    // ⑦ PIE 가 아니면 항상 같은 주소
    {   Randomizer r(7, {0, 0, 0, 0}); std::set<uint64_t> exes; for (int i = 0; i < 1000; ++i) exes.insert(r.next().exe); assert(exes.size() == 1); }
#if defined(__linux__)
    int mode = -1; { std::ifstream f("/proc/sys/kernel/randomize_va_space"); f >> mode; }
    assert(mode >= 0 && mode <= 2);
    auto runChild = [&]() {
        char self[4096]; ssize_t n = readlink("/proc/self/exe", self, sizeof self - 1); assert(n > 0); self[n] = 0;   // popen 은 sh 를 거치므로 자기 경로를 직접 얻어야 한다
        std::string cmd = std::string(self) + " child";
        FILE* pipe = popen(cmd.c_str(), "r"); char buf[64] = {0}; if (pipe) { if (!fgets(buf, sizeof buf, pipe)) buf[0] = 0; pclose(pipe); }
        return std::string(buf);
    };
    std::string a = runChild(), b = runChild();
    assert(!a.empty() && !b.empty());
    if (mode >= 1) assert(a != b);                                  // ⑧ 실행마다 스택 주소가 달라진다 (우연히 같을 확률은 2^-22 이하)
    else assert(a == b);                                            // 끄면 항상 같다
    std::cout << "ASLR verified (model + real, kernel mode " << mode << "): run1 stack=" << a.substr(0, a.size() - 1) << " run2 stack=" << b.substr(0, b.size() - 1) << "; fixed layout halves the expected brute-force cost, one leak defeats it." << std::endl;
#else
    std::cout << "ASLR verified (model only; the real-process comparison is Linux-only)." << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1) (모형의 한 번 뽑기)
// Space Complexity: O(1)
```
## DEP()
### 대표코드
```cpp
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#if defined(__unix__) || defined(__APPLE__)
#include <csignal>
#include <cstdio>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
enum Outcome { OK, SEGV, OTHER };
template <class F> Outcome inChild(F f) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); f(); _exit(0); } int st = 0; waitpid(pid, &st, 0);
    if (WIFEXITED(st) && WEXITSTATUS(st) == 0) return OK; if (WIFSIGNALED(st) && WTERMSIG(st) == SIGSEGV) return SEGV; return OTHER; }
#endif

// DEP / NX 비트(데이터 실행 방지): 데이터 페이지(스택·힙·전역·익명 매핑)에는 실행 권한이 없다.  공격자가 버퍼에 기계어를 주입해도 그 위치로 점프하면 CPU 가 예외를 낸다.  이를 우회하려는 공격이 ROP(이미 있는 코드 조각 = 가젯을 `ret` 으로 이어 붙이기)이고, 그래서 ASLR(주소 무작위화)과 함께 쓴다.
//  ① (Linux x86-64, 실제 실행) 한 바이트짜리 `ret`(0xC3)을 RW 익명 페이지 / 스택 배열 / malloc 블록 / 전역 배열에서 실행하면 자식이 모두 SIGSEGV, mprotect(PROT_EXEC) 한 뒤에는 정상 종료  ② 지도(/proc/self/maps)에서 [stack]·[heap] 권한에 `x` 가 없다
//  ③ ROP 모형: 가젯 4 개(pop rax;ret / pop rbx;ret / add rax,rbx;ret / out=rax;ret)만 있는 프로그램에서, DEP 가 꺼져 있으면 스택에 주입한 코드가 실행되고, 켜져 있으면 주입 코드는 막히지만 *가젯 연결만으로* 20 + 22 = 42 를 출력할 수 있다
//  ④ ASLR: 기준 주소가 8 비트 무작위면 고정 주소를 쓰는 공격의 성공률 ≈ 1/256 (이항 5σ 이내), 28 비트면 사실상 0  ⑤ 가젯 주소 하나가 유출되면 기준을 알아내 ASLR 이 무력화됨(성공률 100%).
struct Gadgets { enum { POP_RAX = 0x100, POP_RBX = 0x110, ADD = 0x120, OUT = 0x130, EXIT = 0x140 }; };
struct Machine {
    bool dep; uint64_t base; uint64_t stackLow, stackHigh; std::vector<uint64_t> stack; size_t sp = 0; uint64_t rax = 0, rbx = 0, out = 0; bool crashed = false, exited = false, shellcode = false;
    Machine(bool d, uint64_t b) : dep(d), base(b), stackLow(0x7fff0000), stackHigh(0x7fff0000 + 8 * 64) {}
    void run(const std::vector<uint64_t>& image) {                                                            // image: 반환 주소 위치(= 오버플로로 덮인 스택)부터의 내용
        stack = image; sp = 0;
        while (!crashed && !exited && sp < stack.size()) { uint64_t target = stack[sp++];                       // ret
            if (target >= stackLow && target < stackHigh) { if (dep) { crashed = true; break; } shellcode = true; out = 0xDEAD; exited = true; break; }       // 스택(데이터)으로 점프: DEP 면 NX 폴트, 아니면 주입 코드 실행
            uint64_t off = target - base;
            switch (off) { case Gadgets::POP_RAX: rax = sp < stack.size() ? stack[sp++] : 0; break; case Gadgets::POP_RBX: rbx = sp < stack.size() ? stack[sp++] : 0; break; case Gadgets::ADD: rax += rbx; break; case Gadgets::OUT: out = rax; break; case Gadgets::EXIT: exited = true; break; default: crashed = true; } } }
};
std::vector<uint64_t> ropChain(uint64_t base) { using G = Gadgets; return {base + G::POP_RAX, 20, base + G::POP_RBX, 22, base + G::ADD, base + G::OUT, base + G::EXIT}; }

int main() {
#if defined(__linux__) && defined(__x86_64__)
    long ps = sysconf(_SC_PAGESIZE); static unsigned char globalBuf[16];
    unsigned char* page = (unsigned char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(page != MAP_FAILED); page[0] = 0xC3;                                                       // ① 실제 실행
    unsigned char* heapBlock = (unsigned char*)std::malloc(64); heapBlock[0] = 0xC3; globalBuf[0] = 0xC3; unsigned char stackBuf[16] = {0xC3};
    assert(inChild([&] { ((void (*)())page)(); }) == SEGV); assert(inChild([&] { ((void (*)())stackBuf)(); }) == SEGV); assert(inChild([&] { ((void (*)())heapBlock)(); }) == SEGV); assert(inChild([&] { ((void (*)())globalBuf)(); }) == SEGV);
    assert(mprotect(page, ps, PROT_READ | PROT_EXEC) == 0); assert(inChild([&] { ((void (*)())page)(); }) == OK);                                                                                                       // 실행 권한을 주면 실행된다
    { std::ifstream f("/proc/self/maps"); std::string line; int checked = 0; while (std::getline(f, line)) { std::istringstream in(line); std::string range, perms, off, dev, inode, name; in >> range >> perms >> off >> dev >> inode >> name; if (name == "[stack]" || name == "[heap]") { assert(perms[2] != 'x'); ++checked; } } assert(checked >= 1); }                  // ②
    munmap(page, ps); std::free(heapBlock);
#endif
    {   Machine off(false, 0x400000); off.run({0x7fff0010}); assert(off.shellcode && off.out == 0xDEAD);                                                                                                    // ③ DEP 없음: 주입 코드 실행
        Machine on(true, 0x400000); on.run({0x7fff0010}); assert(on.crashed && !on.shellcode);                                                                                                              // DEP: 주입 코드는 막힌다
        Machine rop(true, 0x400000); rop.run(ropChain(0x400000)); assert(!rop.crashed && rop.exited && rop.out == 42 && !rop.shellcode); }                                                                          // 하지만 가젯 연결은 실행된다
    std::mt19937_64 rng(1035); const int trials = 20000; uint64_t fixedGuess = 0x400000 + 0x1000 * 37; int success8 = 0, success28 = 0, leaked = 0;                                                                // ④ ASLR
    for (int i = 0; i < trials; ++i) { uint64_t base8 = 0x400000 + 0x1000 * (rng() % 256), base28 = 0x400000 + 0x1000 * (rng() % (1ULL << 28));
        Machine m8(true, base8); m8.run(ropChain(fixedGuess)); success8 += (!m8.crashed && m8.out == 42); Machine m28(true, base28); m28.run(ropChain(fixedGuess)); success28 += (!m28.crashed && m28.out == 42);
        uint64_t leakedGadget = base8 + Gadgets::POP_RAX; Machine ml(true, base8); ml.run(ropChain(leakedGadget - Gadgets::POP_RAX)); leaked += (!ml.crashed && ml.out == 42); }                                           // ⑤ 가젯 주소 유출 → 기준 계산
    double mean = trials / 256.0, sigma = std::sqrt(trials * (1.0 / 256) * (255.0 / 256)); assert(std::fabs(success8 - mean) < 5 * sigma && success28 <= 1 && leaked == trials);
    std::cout << "DEP: executing an injected `ret` from an RW page, the stack, the heap or a global array killed the child with SIGSEGV but ran after mprotect(PROT_EXEC); in the ROP model DEP blocked injected code while a gadget chain still printed 42; a fixed-address chain succeeded " << success8 << "/" << trials << " with 8-bit ASLR (expected ~" << (int)mean << "), " << success28 << " with 28-bit ASLR, and always once a gadget address leaked" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
# Part 11. 병렬 메모리
## AtomicOperation()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <set>
#include <thread>
#include <vector>

// 원자적 연산: 중간 상태를 다른 스레드가 볼 수 없는 불가분의 읽기-수정-쓰기.  일반 변수의 counter++ 는 (읽기, 더하기, 쓰기) 세 단계라 두 스레드가 겹치면 갱신이 사라진다(경쟁 상태).  std::atomic 의 fetch_add 는 CPU 의 lock 접두 명령(x86: lock xadd)으로 구현되어 정확하다.
//  ① 손실 갱신을 *모든 실행 순서를 열거*해서 증명한다: 스레드 T 개가 각각 K 번 비원자 증가(읽기, 쓰기 한 쌍)를 할 때 가능한 최종 값의 집합 — (T, K) = (2,2) → {2,3,4}, (2,3) → {2,…,6}, (3,2) → {2,…,6}: 최솟값은 항상 2  — 원자적 증가는 모든 순서에서 정확히 T·K
//  ② 실제 스레드 4 개 × 20 만 번의 fetch_add(relaxed) 는 정확히 80 만, 같은 일을 test-and-set(exchange) 스핀락으로 지킨 *일반* 변수도 정확(ThreadSanitizer 무결)  ③ 비트 연산 RMW: 스레드 8 개가 각자 서로 다른 비트를 fetch_or 로 켜면 최종 마스크 = 모든 비트(서로의 비트를 덮어쓰지 않는다), 같은 일을 읽고-쓰기로 하면 비트가 사라질 수 있음을 열거로 확인
//  ④ exchange / fetch_sub / compare_exchange 의 의미(이전 값 반환, 실패 시 expected 갱신)와 is_lock_free() — 크기 1·2·4·8 바이트는 잠금 없음, 64 바이트 구조체는 is_always_lock_free 가 아니다(내부 잠금).
struct Scenario { int threads, increments; };
void walk(const Scenario& sc, bool atomicOps, int shared, std::vector<int> pc, std::vector<int> local, std::set<int>& finals) {                         // pc[t] = 해당 스레드가 끝낸 단계 수 (비원자: 읽기 → 쓰기 반복, 원자: 한 단계)
    bool progressed = false;
    for (int t = 0; t < sc.threads; ++t) { int steps = atomicOps ? sc.increments : 2 * sc.increments; if (pc[t] >= steps) continue; progressed = true; std::vector<int> pc2 = pc, local2 = local; int shared2 = shared;
        if (atomicOps) ++shared2; else if (pc[t] % 2 == 0) local2[t] = shared; else shared2 = local[t] + 1; ++pc2[t]; walk(sc, atomicOps, shared2, pc2, local2, finals); }
    if (!progressed) finals.insert(shared); }
std::set<int> reachable(int threads, int increments, bool atomicOps) { std::set<int> f; walk({threads, increments}, atomicOps, 0, std::vector<int>(threads, 0), std::vector<int>(threads, 0), f); return f; }
struct Big { char bytes[64]; };

int main() {
    assert(reachable(2, 2, false) == (std::set<int>{2, 3, 4}) && reachable(2, 3, false) == (std::set<int>{2, 3, 4, 5, 6}) && reachable(3, 2, false) == (std::set<int>{2, 3, 4, 5, 6}));              // ① 손실 갱신: 최솟값 2
    for (auto sc : {Scenario{2, 2}, Scenario{2, 3}, Scenario{3, 2}, Scenario{4, 1}}) assert(reachable(sc.threads, sc.increments, true) == (std::set<int>{sc.threads * sc.increments}));          // 원자적이면 항상 정확히 T·K
    {   const int T = 4; const long N = 200000; std::atomic<long> counter(0); std::vector<std::thread> th; for (int t = 0; t < T; ++t) th.emplace_back([&] { for (long i = 0; i < N; ++i) counter.fetch_add(1, std::memory_order_relaxed); }); for (auto& x : th) x.join(); assert(counter.load() == T * N);      // ② 실제
        std::atomic_flag lock = ATOMIC_FLAG_INIT; long plain = 0; std::vector<std::thread> th2; for (int t = 0; t < T; ++t) th2.emplace_back([&] { for (long i = 0; i < N / 4; ++i) { while (lock.test_and_set(std::memory_order_acquire)) std::this_thread::yield(); ++plain; lock.clear(std::memory_order_release); } }); for (auto& x : th2) x.join(); assert(plain == T * (N / 4)); }
    {   std::atomic<uint32_t> mask(0); std::vector<std::thread> th; for (int t = 0; t < 8; ++t) th.emplace_back([&, t] { mask.fetch_or(1u << (t * 3), std::memory_order_relaxed); }); for (auto& x : th) x.join(); uint32_t want = 0; for (int t = 0; t < 8; ++t) want |= 1u << (t * 3); assert(mask.load() == want);               // ③ 비트 RMW
        std::set<uint32_t> lostBits; { struct S { int pc[2] = {0, 0}; uint32_t local[2] = {0, 0}; uint32_t shared = 0; }; std::vector<S> stack = {S()}; while (!stack.empty()) { S s = stack.back(); stack.pop_back(); bool moved = false;
            for (int t = 0; t < 2; ++t) { if (s.pc[t] >= 2) continue; moved = true; S n = s; if (s.pc[t] == 0) n.local[t] = s.shared; else n.shared = s.local[t] | (1u << t); ++n.pc[t]; stack.push_back(n); } if (!moved) lostBits.insert(s.shared); } }
        assert(lostBits == (std::set<uint32_t>{1, 2, 3})); }                                                         // 읽고-쓰기면 결과 {비트0 만, 비트1 만, 둘 다} — 한 비트가 사라지는 실행이 존재
    {   std::atomic<int> a(5); assert(a.exchange(9) == 5 && a.load() == 9 && a.fetch_sub(4) == 9 && a.load() == 5 && a.fetch_add(0) == 5);                          // ④ 의미
        int expected = 3; bool ok = a.compare_exchange_strong(expected, 100); assert(!ok && expected == 5 && a.load() == 5); ok = a.compare_exchange_strong(expected, 100); assert(ok && a.load() == 100);
        static_assert(std::atomic<char>::is_always_lock_free && std::atomic<short>::is_always_lock_free && std::atomic<int>::is_always_lock_free && std::atomic<long long>::is_always_lock_free, "1·2·4·8 바이트 원자 변수는 잠금이 없다"); assert(!std::atomic<Big>::is_always_lock_free); }          // 64 바이트 구조체는 항상 잠금 없음이 *아니다* (구현이 내부 잠금을 쓴다)
    std::cout << "AtomicOperation: enumerating every interleaving, non-atomic counters ended anywhere in [2, T*K] (e.g. {2,3,4} for 2 threads x 2 increments) while atomic increments always gave exactly T*K; 4 real threads gave exactly 800000 with fetch_add, a test-and-set lock protected a plain counter, and concurrent fetch_or never lost a bit" << std::endl;
    return 0;
}
// Time Complexity: O(1) 연산 (경합 시 캐시 라인 이동 비용)
// Space Complexity: O(1)
```
## CompareAndSwap()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <set>
#include <thread>
#include <vector>

// audit: exhaustive (ABA 가 일어나는 모든 20 가지 인터리브를 열거하고 락 없는 스택은 보존 법칙으로 확인)
// CAS(compare-and-swap): "현재 값이 expected 와 같으면 desired 로 바꾸고 성공, 아니면 실패하고 현재 값을 알려 준다" 를 한 번에 하는 원자 명령 (x86: cmpxchg).  락 없는 자료구조의 기본 블록: 읽고 → 계산하고 → CAS 로 반영을 시도하고, 실패하면(다른 스레드가 먼저 바꿈) 다시 시도한다.
//  ABA 문제: 값이 A → B → A 로 바뀌어도 CAS 는 "그대로" 라고 판단한다.  해법: 포인터에 버전 번호(태그)를 함께 CAS.
//  ① 의미: 성공하면 값이 바뀌고, 실패하면 expected 가 현재 값으로 갱신된다  ② 락 없는 스택 push 를 CAS 루프로: 4 스레드 × 5000 번, 모든 값이 정확히 한 번씩 들어간다(풀 기반 노드, 누수 없음)  ③ ABA 를 *모든 인터리빙 열거*로 증명: 스레드 1 이 pop(읽기 3 단계), 스레드 2 가 "A, B 를 pop 하고 B 를 해제한 뒤 A 를 다시 push" 하는 3 단계를 가질 때 20 가지 순서 중
//  태그 없는 CAS 는 정확히 3 가지에서 이미 해제된 B 를 스택에 되살려 *손상*시키고, 태그(버전) 있는 CAS 는 20 가지 모두에서 손상이 없다  ④ CAS 루프의 재시도는 다른 스레드의 성공이 있었을 때만 일어난다: 8 스레드 × 5 만 번 카운터에서 (성공 수 = 연산 수) 이고 실패 수는 임의.
struct Cell { int v; std::atomic<int> next; };
struct CasStack { std::vector<Cell> pool; std::atomic<int> head, used; explicit CasStack(size_t cap) : pool(cap), head(-1), used(0) {}
    void push(int v) { int n = used.fetch_add(1); pool[n].v = v; int h = head.load(); do { pool[n].next.store(h); } while (!head.compare_exchange_weak(h, n)); }          // 실패하면 h 가 현재 head 로 갱신된다
};
struct AbaWorld { int next[4]; bool freed[4]; int head; unsigned tag; int popped1; bool corrupted; };       // 노드 1(A) → 2(B) → 3(C), 0 = 없음
AbaWorld fresh() { AbaWorld w; w.next[1] = 2; w.next[2] = 3; w.next[3] = 0; w.next[0] = 0; for (bool& f : w.freed) f = false; w.head = 1; w.tag = 0; w.popped1 = 0; w.corrupted = false; return w; }
int runSchedule(unsigned mask, bool useTag) {                                                                  // mask 의 비트가 1 이면 스레드 2 의 다음 단계, 0 이면 스레드 1 의 다음 단계 (6 비트 중 3 개가 1)
    AbaWorld w = fresh(); int t1pc = 0, t2pc = 0; int seenHead = 0, seenNext = 0; unsigned seenTag = 0;
    for (int bit = 5; bit >= 0; --bit) { bool second = (mask >> bit) & 1;
        if (!second) { if (t1pc == 0) { seenHead = w.head; seenTag = w.tag; ++t1pc; } else if (t1pc == 1) { seenNext = seenHead ? w.next[seenHead] : 0; ++t1pc; }
            else { bool match = w.head == seenHead && (!useTag || w.tag == seenTag); if (match) { w.head = seenNext; ++w.tag; w.popped1 = seenHead; if (w.head && w.freed[w.head]) w.corrupted = true; } ++t1pc; } }              // 스레드 1 의 CAS: head(와 태그)가 그대로면 head ← 읽어 둔 next
        else { if (t2pc == 0) { w.head = w.next[w.head]; ++w.tag; }                                            // 스레드 2: pop A
            else if (t2pc == 1) { int b = w.head; w.head = w.next[b]; ++w.tag; w.freed[b] = true; }              // pop B 후 해제
            else { w.next[1] = w.head; w.head = 1; ++w.tag; }                                                    // A 를 다시 push (next = C)
            ++t2pc; } }
    return w.corrupted; }

int main() {
    {   std::atomic<int> a(5); int expected = 3; bool ok = a.compare_exchange_strong(expected, 9); assert(!ok && expected == 5 && a.load() == 5); ok = a.compare_exchange_strong(expected, 9); assert(ok && a.load() == 9); }          // ① 의미
    {   const int T = 4, K = 5000; CasStack st((size_t)T * K); std::vector<std::thread> th; for (int t = 0; t < T; ++t) th.emplace_back([&, t] { for (int i = 0; i < K; ++i) st.push(t * 10000 + i); }); for (auto& x : th) x.join();
        std::set<int> seen; int count = 0; for (int n = st.head.load(); n >= 0; n = st.pool[n].next.load()) { ++count; assert(seen.insert(st.pool[n].v).second); } assert(count == T * K && (int)seen.size() == T * K); }       // ② 유실·중복 없음
    {   int untaggedBad = 0, taggedBad = 0, schedules = 0; for (unsigned mask = 0; mask < 64; ++mask) { if (__builtin_popcount(mask) != 3) continue; ++schedules; untaggedBad += runSchedule(mask, false); taggedBad += runSchedule(mask, true); }        // ③ 20 가지 인터리빙 전수
        assert(schedules == 20 && untaggedBad == 3 && taggedBad == 0); }
    {   std::atomic<long> counter(0); std::atomic<long> failures(0), successes(0); const int T = 8; const long K = 50000; std::vector<std::thread> th; for (int t = 0; t < T; ++t) th.emplace_back([&] { long f = 0, s = 0; for (long i = 0; i < K; ++i) { long v = counter.load(); while (!counter.compare_exchange_weak(v, v + 1)) ++f; ++s; } failures += f; successes += s; });         // ④ CAS 루프 카운터
        for (auto& x : th) x.join(); assert(counter.load() == T * K && successes.load() == T * K);
        std::cout << "CompareAndSwap: a lock-free CAS push lost nothing across 4 threads, and enumerating all 20 interleavings showed the untagged CAS corrupts the stack in exactly 3 of them (resurrecting the freed node) while the version-tagged CAS never does; an 8-thread CAS counter reached exactly " << T * K << " (" << failures.load() << " failed attempts retried)" << std::endl; }
    return 0;
}
// Time Complexity: 루프당 O(1), 경합 시 재시도
// Space Complexity: O(N) 노드 풀 + O(1) 카운터
```
## MemoryBarrier()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <iostream>
#include <set>
#include <thread>
#include <vector>

// audit: exhaustive (메모리 모형의 모든 실행 순서를 열거해 가능한 결과 집합을 얻는다)
// 메모리 장벽: CPU 와 컴파일러는 성능을 위해 서로 다른 주소에 대한 읽기/쓰기 순서를 바꾼다 (x86 도 "쓰기 뒤 읽기" 는 스토어 버퍼 때문에 순서가 바뀐다).
//  고전 실험(Store Buffering, SB):  스레드 A: x = 1; r0 = y;     스레드 B: y = 1; r1 = x;   순차 일관성이라면 (r0, r1) = (0, 0) 은 불가능하지만, 장벽 없이는 둘 다 0 을 볼 수 있다.   seq_cst(또는 fence) 를 쓰면 절대 일어나지 않는다.
//  운에 맡기는 실제 실행 대신 먼저 *메모리 모델을 모형화*해 가능한 결과 전부를 열거한다 — 각 스레드의 명령을 "앞선 명령이 끝나야 하는 관계(waits)" 로 묶고, 모든 실행 순서(스레드 선택 × 준비된 명령 선택)를 깊이 우선으로 훑는다.
//  ① SB 의 가능한 결과 집합: 순차 일관성 {(0,1),(1,0),(1,1)}, x86(TSO)·약한 모델은 (0,0) 까지 4 개  ② 저장과 적재 사이에 전체 장벽(fence)을 두면 *모든 모델*에서 (0,0) 이 사라진다  ③ 약한 모델에서 seq_cst 저장·적재로 주석을 달면 사라지고, release/acquire 만으로는 사라지지 *않는다*
//  ④ MP(메시지 전달)는 TSO 에서 이미 안전하지만(저장끼리·적재끼리 순서 유지) 약한 모델의 relaxed 에서는 위반 가능  ⑤ 같은 주소 읽기-쓰기 일관성(CoRR: 읽은 값이 뒤로 가지 않음)은 어느 모델에서도 성립  ⑥ 실제 스레드 10 만 시도: fence / seq_cst 면 (0,0) 은 0 번(하드웨어 보장), relaxed 의 횟수는 기계에 따라 다르다(모형이 허용하는 결과 안).
enum Kind { ST, LD, FENCE, RMW, SPIN };                                                                        // 저장 / 적재 / 전체 장벽 / 원자적 읽기-수정-쓰기 / 조건이 참일 때까지 대기(두 주소를 한 번에 읽음)
enum Ord { RLX, ACQ, REL, AR, SC };
enum Model { SEQ, TSO, WEAK };                                                                                  // 순차 일관성 / x86 식(저장→적재만 재배열) / 주석 달린 약한 모델(다중 복사 원자적)
struct Ins { Kind k; int addr = 0; int val = 0; Ord ord = RLX; int reg = -1; int addr2 = -1, val2 = 0; };      // SPIN: mem[addr] == val || mem[addr2] == val2 이면 진행
typedef std::vector<Ins> Thread;
bool isAcq(Ord o) { return o == ACQ || o == AR || o == SC; }
bool isRel(Ord o) { return o == REL || o == AR || o == SC; }
bool waits(Model m, const Ins& a, const Ins& b) {                                                               // 같은 스레드에서 앞선 a 가 끝나야 뒤의 b 를 시작할 수 있는가?
    if (m == SEQ) return true; if (a.k == FENCE || b.k == FENCE) return true;
    if (a.k != SPIN && b.k != SPIN && a.addr == b.addr) return true;                                              // 같은 주소: 일관성(coherence)
    bool aRead = a.k == LD || a.k == RMW || a.k == SPIN, bWrite = b.k == ST || b.k == RMW;
    if (m == TSO) return !(a.k == ST && (b.k == LD || b.k == SPIN));                                              // x86: 서로 다른 주소의 "저장 → 적재" 만 순서가 바뀐다 (RMW·SPIN 앞뒤는 유지)
    if (aRead && isAcq(a.ord)) return true; if (bWrite && isRel(b.ord)) return true; return a.ord == SC && b.ord == SC;      // 약한 모델: acquire 적재는 뒤를, release 저장은 앞을 붙잡는다, SC 끼리는 프로그램 순서
}
struct Outcomes { std::set<std::vector<int>> finals; bool deadlock = false; };                                // 각 결과 = [레지스터들..., 메모리들...]
void dfs(Model m, const std::vector<Thread>& th, int nregs, std::vector<int>& mem, std::vector<std::vector<int>>& regs, std::vector<std::vector<char>>& done, std::set<std::vector<int>>& seen, Outcomes& out) {
    std::vector<int> key = mem; for (size_t t = 0; t < th.size(); ++t) { for (int r : regs[t]) key.push_back(r); for (char d : done[t]) key.push_back(d); } if (!seen.insert(key).second) return;
    bool allDone = true, any = false;
    for (size_t t = 0; t < th.size(); ++t) for (size_t j = 0; j < th[t].size(); ++j) { if (done[t][j]) continue; allDone = false; bool ready = true; for (size_t i = 0; i < j && ready; ++i) if (!done[t][i] && waits(m, th[t][i], th[t][j])) ready = false; if (!ready) continue;
        const Ins& in = th[t][j]; if (in.k == SPIN && !(mem[in.addr] == in.val || (in.addr2 >= 0 && mem[in.addr2] == in.val2))) continue; any = true;
        int saveMem = 0, saveReg = 0; if (in.k == ST || in.k == RMW) saveMem = mem[in.addr]; if (in.reg >= 0) saveReg = regs[t][in.reg];
        if (in.k == ST) mem[in.addr] = in.val; else if (in.k == LD) regs[t][in.reg] = mem[in.addr]; else if (in.k == RMW) { regs[t][in.reg] = mem[in.addr]; mem[in.addr] += in.val; }
        done[t][j] = 1; dfs(m, th, nregs, mem, regs, done, seen, out); done[t][j] = 0;
        if (in.k == ST || in.k == RMW) mem[in.addr] = saveMem; if (in.reg >= 0) regs[t][in.reg] = saveReg; }
    if (allDone) { std::vector<int> o; for (size_t t = 0; t < th.size(); ++t) for (int r : regs[t]) o.push_back(r); for (int v : mem) o.push_back(v); out.finals.insert(o); } else if (!any) out.deadlock = true;           // 아무것도 못 하는데 끝나지 않았다 = 교착
}
Outcomes explore(Model m, const std::vector<Thread>& th, int nregs, int nmem) { std::vector<int> mem(nmem, 0); std::vector<std::vector<int>> regs(th.size(), std::vector<int>(nregs, 0)); std::vector<std::vector<char>> done(th.size()); for (size_t t = 0; t < th.size(); ++t) done[t].assign(th[t].size(), 0); std::set<std::vector<int>> seen; Outcomes out; dfs(m, th, nregs, mem, regs, done, seen, out); return out; }
Ins st(int a, int v, Ord o = RLX) { Ins i; i.k = ST; i.addr = a; i.val = v; i.ord = o; return i; }
Ins ld(int a, int r, Ord o = RLX) { Ins i; i.k = LD; i.addr = a; i.reg = r; i.ord = o; return i; }
Ins fence() { Ins i; i.k = FENCE; return i; }
Ins rmw(int a, int v, int r, Ord o = AR) { Ins i; i.k = RMW; i.addr = a; i.val = v; i.reg = r; i.ord = o; return i; }

const int N = 100000;
std::vector<std::atomic<int>> arrive(N), X(N), Y(N), R0(N), R1(N);
long runTest(std::memory_order storeOrder, std::memory_order loadOrder, bool useFence) {
    for (int i = 0; i < N; i++) { arrive[i] = 0; X[i] = 0; Y[i] = 0; R0[i] = -1; R1[i] = -1; }
    auto sync = [&](int i) { arrive[i].fetch_add(1); while (arrive[i].load() < 2) std::this_thread::yield(); };          // 두 스레드를 같은 순간에 출발시킨다
    std::thread a([&] { for (int i = 0; i < N; i++) { sync(i); X[i].store(1, storeOrder); if (useFence) std::atomic_thread_fence(std::memory_order_seq_cst); R0[i].store(Y[i].load(loadOrder), std::memory_order_relaxed); } });
    std::thread b([&] { for (int i = 0; i < N; i++) { sync(i); Y[i].store(1, storeOrder); if (useFence) std::atomic_thread_fence(std::memory_order_seq_cst); R1[i].store(X[i].load(loadOrder), std::memory_order_relaxed); } });
    a.join(); b.join(); long both0 = 0; for (int i = 0; i < N; i++) both0 += (R0[i] == 0 && R1[i] == 0); return both0; }
std::vector<Thread> storeBuffering(Ord so, Ord lo, bool withFence) { Thread a = {st(0, 1, so)}; if (withFence) a.push_back(fence()); a.push_back(ld(1, 0, lo)); Thread b = {st(1, 1, so)}; if (withFence) b.push_back(fence()); b.push_back(ld(0, 0, lo)); return {a, b}; }
bool has(const Outcomes& o, int r0, int r1) { for (auto& f : o.finals) if (f[0] == r0 && f[1] == r1) return true; return false; }       // 레지스터: 스레드 0 의 r0, 스레드 1 의 r0

int main() {
    for (Model m : {SEQ, TSO, WEAK}) { Outcomes o = explore(m, storeBuffering(RLX, RLX, false), 1, 2); std::set<std::pair<int, int>> got; for (auto& f : o.finals) got.insert({f[0], f[1]});                  // ① 결과 집합
        std::set<std::pair<int, int>> want = {{0, 1}, {1, 0}, {1, 1}}; if (m != SEQ) want.insert({0, 0}); assert(got == want && !o.deadlock); }
    for (Model m : {SEQ, TSO, WEAK}) assert(!has(explore(m, storeBuffering(RLX, RLX, true), 1, 2), 0, 0));                                                          // ② fence 가 있으면 (0,0) 없음
    assert(!has(explore(WEAK, storeBuffering(SC, SC, false), 1, 2), 0, 0) && has(explore(WEAK, storeBuffering(REL, ACQ, false), 1, 2), 0, 0));                         // ③ seq_cst 는 막고 release/acquire 는 못 막는다
    {   Thread t0 = {st(0, 1), st(1, 1)}, t1 = {ld(1, 0), ld(0, 1)}; for (Model m : {SEQ, TSO}) { Outcomes o = explore(m, {t0, t1}, 2, 2); for (auto& f : o.finals) assert(!(f[2] == 1 && f[3] == 0)); }        // ④ MP: TSO 에서는 (flag = 1, data = 0) 없음
        Outcomes weak = explore(WEAK, {t0, t1}, 2, 2); bool seen = false; for (auto& f : weak.finals) seen |= (f[2] == 1 && f[3] == 0); assert(seen); }
    {   Thread w = {st(0, 1)}, r = {ld(0, 0), ld(0, 1)}; for (Model m : {SEQ, TSO, WEAK}) { Outcomes o = explore(m, {w, r}, 2, 1); for (auto& f : o.finals) assert(!(f[2] == 1 && f[3] == 0)); } }          // ⑤ CoRR
    long relaxed = runTest(std::memory_order_relaxed, std::memory_order_relaxed, false), withFence = runTest(std::memory_order_relaxed, std::memory_order_relaxed, true), seqcst = runTest(std::memory_order_seq_cst, std::memory_order_seq_cst, false);
    assert(withFence == 0 && seqcst == 0);                                                                       // ⑥ 보장: fence 가 있으면, seq_cst 면 절대 (0,0) 이 없다
    std::cout << "MemoryBarrier: the exhaustive model gave SB outcome sets {(0,1),(1,0),(1,1)} under sequential consistency and all four under TSO/weak, a fence or seq_cst removed (0,0), release/acquire alone did not; on this machine (0,0) appeared " << relaxed << " times in " << N << " relaxed trials, " << withFence << " with a fence and " << seqcst << " with seq_cst" << std::endl;
    return 0;
}
// Time Complexity: 모형 열거는 상태 수에 비례 (작은 리트머스 테스트), 실제 실행 O(N)
// Space Complexity: O(N + 상태 수)
```
## AcquireRelease()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <iostream>
#include <set>
#include <thread>
#include <vector>

// audit: exhaustive (메모리 모형의 모든 실행 순서를 열거해 가능한 결과 집합을 얻는다)
// acquire/release: seq_cst 보다 약하지만 가장 흔한 "메시지 전달" 패턴에 충분한 순서 보장.  release 저장: 이 저장 "이전의 모든 쓰기" 가 이 저장과 함께 다른 스레드에 보이게 한다.  acquire 적재: release 가 쓴 값을 읽었다면, 그 release 이전의 모든 쓰기를 볼 수 있다.
//  생산자가 data 를 쓰고 flag 를 release 로 올리면, flag 를 acquire 로 본 소비자는 반드시 최신 data 를 읽는다.  *한쪽만으로는 부족하다* — 모형(아래 열거기)으로 모든 조합을 확인한다.
//  ① MP(메시지 전달): 금지하고 싶은 결과 (flag = 1, data = 0) 은 약한 모델에서 (relaxed, relaxed)·(release 저장, relaxed 적재)·(relaxed 저장, acquire 적재) 이면 *가능*하고 (release, acquire)·(acq_rel, acq_rel)·(seq_cst, seq_cst) 이면 불가능  ② 인과성의 전이(WRC): T0 이 x = 1, T1 이 x 를 acquire 로 읽은 뒤 y = 1(release), T2 가 y 를 acquire 로 읽은 뒤 x 를 읽을 때 (x=1 을 본 T1 → y=1 을 본 T2 → x=0) 은 release/acquire 로 금지, relaxed 로는 가능
//  ③ 원자적 RMW 는 어떤 모델에서도 한 번에 하나씩: 두 스레드가 같은 변수에 fetch_add(1) 하면 이전 값은 항상 {0, 1} 한 쌍  ④ 실제 스레드 10 만 개 메시지(일반 변수 data + release/acquire 플래그)에서 오래된 읽기 0 번, 객체 포인터를 release 로 공개하면 소비자는 완성된 필드를 본다  ⑤ ThreadSanitizer 로도 데이터 경쟁이 없다(release/acquire 쌍이 happens-before 를 만든다).
enum Kind { ST, LD, FENCE, RMW, SPIN };                                                                        // 저장 / 적재 / 전체 장벽 / 원자적 읽기-수정-쓰기 / 조건이 참일 때까지 대기(두 주소를 한 번에 읽음)
enum Ord { RLX, ACQ, REL, AR, SC };
enum Model { SEQ, TSO, WEAK };                                                                                  // 순차 일관성 / x86 식(저장→적재만 재배열) / 주석 달린 약한 모델(다중 복사 원자적)
struct Ins { Kind k; int addr = 0; int val = 0; Ord ord = RLX; int reg = -1; int addr2 = -1, val2 = 0; };      // SPIN: mem[addr] == val || mem[addr2] == val2 이면 진행
typedef std::vector<Ins> Thread;
bool isAcq(Ord o) { return o == ACQ || o == AR || o == SC; }
bool isRel(Ord o) { return o == REL || o == AR || o == SC; }
bool waits(Model m, const Ins& a, const Ins& b) {                                                               // 같은 스레드에서 앞선 a 가 끝나야 뒤의 b 를 시작할 수 있는가?
    if (m == SEQ) return true; if (a.k == FENCE || b.k == FENCE) return true;
    if (a.k != SPIN && b.k != SPIN && a.addr == b.addr) return true;                                              // 같은 주소: 일관성(coherence)
    bool aRead = a.k == LD || a.k == RMW || a.k == SPIN, bWrite = b.k == ST || b.k == RMW;
    if (m == TSO) return !(a.k == ST && (b.k == LD || b.k == SPIN));                                              // x86: 서로 다른 주소의 "저장 → 적재" 만 순서가 바뀐다 (RMW·SPIN 앞뒤는 유지)
    if (aRead && isAcq(a.ord)) return true; if (bWrite && isRel(b.ord)) return true; return a.ord == SC && b.ord == SC;      // 약한 모델: acquire 적재는 뒤를, release 저장은 앞을 붙잡는다, SC 끼리는 프로그램 순서
}
struct Outcomes { std::set<std::vector<int>> finals; bool deadlock = false; };                                // 각 결과 = [레지스터들..., 메모리들...]
void dfs(Model m, const std::vector<Thread>& th, int nregs, std::vector<int>& mem, std::vector<std::vector<int>>& regs, std::vector<std::vector<char>>& done, std::set<std::vector<int>>& seen, Outcomes& out) {
    std::vector<int> key = mem; for (size_t t = 0; t < th.size(); ++t) { for (int r : regs[t]) key.push_back(r); for (char d : done[t]) key.push_back(d); } if (!seen.insert(key).second) return;
    bool allDone = true, any = false;
    for (size_t t = 0; t < th.size(); ++t) for (size_t j = 0; j < th[t].size(); ++j) { if (done[t][j]) continue; allDone = false; bool ready = true; for (size_t i = 0; i < j && ready; ++i) if (!done[t][i] && waits(m, th[t][i], th[t][j])) ready = false; if (!ready) continue;
        const Ins& in = th[t][j]; if (in.k == SPIN && !(mem[in.addr] == in.val || (in.addr2 >= 0 && mem[in.addr2] == in.val2))) continue; any = true;
        int saveMem = 0, saveReg = 0; if (in.k == ST || in.k == RMW) saveMem = mem[in.addr]; if (in.reg >= 0) saveReg = regs[t][in.reg];
        if (in.k == ST) mem[in.addr] = in.val; else if (in.k == LD) regs[t][in.reg] = mem[in.addr]; else if (in.k == RMW) { regs[t][in.reg] = mem[in.addr]; mem[in.addr] += in.val; }
        done[t][j] = 1; dfs(m, th, nregs, mem, regs, done, seen, out); done[t][j] = 0;
        if (in.k == ST || in.k == RMW) mem[in.addr] = saveMem; if (in.reg >= 0) regs[t][in.reg] = saveReg; }
    if (allDone) { std::vector<int> o; for (size_t t = 0; t < th.size(); ++t) for (int r : regs[t]) o.push_back(r); for (int v : mem) o.push_back(v); out.finals.insert(o); } else if (!any) out.deadlock = true;           // 아무것도 못 하는데 끝나지 않았다 = 교착
}
Outcomes explore(Model m, const std::vector<Thread>& th, int nregs, int nmem) { std::vector<int> mem(nmem, 0); std::vector<std::vector<int>> regs(th.size(), std::vector<int>(nregs, 0)); std::vector<std::vector<char>> done(th.size()); for (size_t t = 0; t < th.size(); ++t) done[t].assign(th[t].size(), 0); std::set<std::vector<int>> seen; Outcomes out; dfs(m, th, nregs, mem, regs, done, seen, out); return out; }
Ins st(int a, int v, Ord o = RLX) { Ins i; i.k = ST; i.addr = a; i.val = v; i.ord = o; return i; }
Ins ld(int a, int r, Ord o = RLX) { Ins i; i.k = LD; i.addr = a; i.reg = r; i.ord = o; return i; }
Ins fence() { Ins i; i.k = FENCE; return i; }
Ins rmw(int a, int v, int r, Ord o = AR) { Ins i; i.k = RMW; i.addr = a; i.val = v; i.reg = r; i.ord = o; return i; }


const int N = 100000;
std::vector<int> data(N);                                       // 일반 변수 (원자적이지 않음)
std::vector<std::atomic<int>> flag(N);
struct Msg { int a, b, c; };
std::vector<std::atomic<Msg*>> published(2000);
std::vector<Thread> messagePassing(Ord storeOrd, Ord loadOrd) { return {{st(0, 1), st(1, 1, storeOrd)}, {ld(1, 0, loadOrd), ld(0, 1)}}; }          // T0: data = 1; flag = 1.  T1: r0 = flag; r1 = data.   레지스터 인덱스: T0 r0,r1 | T1 r0,r1
bool mpViolation(const Outcomes& o) { for (auto& f : o.finals) if (f[2] == 1 && f[3] == 0) return true; return false; }

int main() {
    struct Case { Ord s, l; bool violationPossible; };
    for (Case c : {Case{RLX, RLX, true}, Case{REL, RLX, true}, Case{RLX, ACQ, true}, Case{REL, ACQ, false}, Case{AR, AR, false}, Case{SC, SC, false}}) assert(mpViolation(explore(WEAK, messagePassing(c.s, c.l), 2, 2)) == c.violationPossible);           // ①
    {   Thread t0 = {st(0, 1)}, t1 = {ld(0, 0, ACQ), st(1, 1, REL)}, t2 = {ld(1, 0, ACQ), ld(0, 1)};                        // ② WRC: 레지스터 T1 r0 = idx 2, T2 r0 = idx 4, T2 r1 = idx 5 (스레드당 레지스터 2 개)
        auto bad = [](const Outcomes& o) { for (auto& f : o.finals) if (f[2] == 1 && f[4] == 1 && f[5] == 0) return true; return false; };
        assert(!bad(explore(WEAK, {t0, t1, t2}, 2, 2)));
        Thread r1 = {ld(0, 0), st(1, 1)}, r2 = {ld(1, 0), ld(0, 1)}; assert(bad(explore(WEAK, {t0, r1, r2}, 2, 2))); }       // 전부 relaxed 면 인과 사슬이 끊긴다
    {   Thread a = {rmw(0, 1, 0)}, b = {rmw(0, 1, 0)}; for (Model m : {SEQ, TSO, WEAK}) { Outcomes o = explore(m, {a, b}, 1, 1); std::set<std::pair<int, int>> pairs; for (auto& f : o.finals) { pairs.insert({f[0], f[1]}); assert(f[2] == 2); } assert(pairs == (std::set<std::pair<int, int>>{{0, 1}, {1, 0}})); } }          // ③ RMW 는 쪼개지지 않는다
    for (auto& f : flag) f = 0;                                                                                  // ④ 실제 스레드
    std::thread producer([] { for (int i = 0; i < N; i++) { data[i] = i * 2 + 1; flag[i].store(1, std::memory_order_release); } });
    long stale = 0; std::thread consumer([&] { for (int i = 0; i < N; i++) { while (flag[i].load(std::memory_order_acquire) == 0) std::this_thread::yield(); if (data[i] != i * 2 + 1) stale++; } });
    producer.join(); consumer.join(); assert(stale == 0);
    for (auto& p : published) p.store(nullptr); long incomplete = 0; std::vector<Msg*> owned; std::thread pub([&] { for (size_t i = 0; i < published.size(); i++) { Msg* m = new Msg{(int)i, (int)i * 2, (int)i * 3}; owned.push_back(m); published[i].store(m, std::memory_order_release); } });
    std::thread sub([&] { for (size_t i = 0; i < published.size(); i++) { Msg* m; while ((m = published[i].load(std::memory_order_acquire)) == nullptr) std::this_thread::yield(); if (m->a != (int)i || m->b != (int)i * 2 || m->c != (int)i * 3) incomplete++; } });
    pub.join(); sub.join(); for (Msg* m : owned) delete m; assert(incomplete == 0);
    std::cout << "AcquireRelease: the exhaustive model showed message passing needs BOTH a release store and an acquire load (one alone still allows flag=1,data=0), release/acquire made the causality chain WRC safe, RMWs never split, and real threads moved " << N << " messages plus 2000 published objects with no stale or half-built reads" << std::endl;
    return 0;
}
// Time Complexity: 모형 열거는 상태 수에 비례, 실제 실행 O(N)
// Space Complexity: O(N)
```
## SequentialConsistency()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <iostream>
#include <set>
#include <thread>
#include <vector>

// 순차 일관성(SC): 모든 스레드의 모든 연산이 "하나의 전체 순서" 로 일어난 것처럼 보이고, 각 스레드의 연산은 프로그램 순서를 따른다.  std::atomic 의 기본(seq_cst)이다.
//  IRIW 실험(Independent Reads of Independent Writes):  A: x=1   B: y=1   C: r1=x; r2=y   D: r3=y; r4=x   C 는 "x 가 먼저" (r1=1, r2=0), D 는 "y 가 먼저" (r3=1, r4=0) 를 볼 수 있다면 두 독자가 쓰기 순서에 대해 서로 다른 세계를 본 것 — SC 에서는 불가능하다.
//  SC 가 *꼭 필요한* 대표 사례가 Peterson/Dekker 상호 배제다: 각 스레드가 "내 깃발을 올리고, 차례를 상대에게 넘기고, 상대 깃발이 내려갔거나 내 차례일 때 들어간다".  모형 열거기로 모든 실행을 훑는다.
//  ① IRIW 금지 결과 (1,0,1,0): 순차 일관성·TSO 에서 불가능, 약한 모델의 relaxed 적재에서 가능, acquire 적재나 seq_cst 로 주석을 달면 불가능  ② Peterson: 순차 일관성에서는 상호 배제가 항상 성립하고 교착이 없다 — TSO 에서 *장벽 없이는 깨진다*(저장이 늦게 보이므로 두 스레드가 동시에 임계 구역에 들어감), 저장과 대기 읽기 사이에 전체 장벽을 두면 TSO 에서도 성립, 약한 모델의 relaxed 에서는 깨지고 seq_cst 주석이면 성립
//  ③ 실제 스레드 IRIW 2 만 번: seq_cst 면 금지 결과 0 번(보장)  ④ 실제 Peterson(seq_cst 원자 변수)으로 두 스레드가 일반 변수 카운터를 10 만 번씩 올려도 합이 정확하다(ThreadSanitizer 무결).
enum Kind { ST, LD, FENCE, RMW, SPIN };                                                                        // 저장 / 적재 / 전체 장벽 / 원자적 읽기-수정-쓰기 / 조건이 참일 때까지 대기(두 주소를 한 번에 읽음)
enum Ord { RLX, ACQ, REL, AR, SC };
enum Model { SEQ, TSO, WEAK };                                                                                  // 순차 일관성 / x86 식(저장→적재만 재배열) / 주석 달린 약한 모델(다중 복사 원자적)
struct Ins { Kind k; int addr = 0; int val = 0; Ord ord = RLX; int reg = -1; int addr2 = -1, val2 = 0; };      // SPIN: mem[addr] == val || mem[addr2] == val2 이면 진행
typedef std::vector<Ins> Thread;
bool isAcq(Ord o) { return o == ACQ || o == AR || o == SC; }
bool isRel(Ord o) { return o == REL || o == AR || o == SC; }
bool waits(Model m, const Ins& a, const Ins& b) {                                                               // 같은 스레드에서 앞선 a 가 끝나야 뒤의 b 를 시작할 수 있는가?
    if (m == SEQ) return true; if (a.k == FENCE || b.k == FENCE) return true;
    if (a.k != SPIN && b.k != SPIN && a.addr == b.addr) return true;                                              // 같은 주소: 일관성(coherence)
    bool aRead = a.k == LD || a.k == RMW || a.k == SPIN, bWrite = b.k == ST || b.k == RMW;
    if (m == TSO) return !(a.k == ST && (b.k == LD || b.k == SPIN));                                              // x86: 서로 다른 주소의 "저장 → 적재" 만 순서가 바뀐다 (RMW·SPIN 앞뒤는 유지)
    if (aRead && isAcq(a.ord)) return true; if (bWrite && isRel(b.ord)) return true; return a.ord == SC && b.ord == SC;      // 약한 모델: acquire 적재는 뒤를, release 저장은 앞을 붙잡는다, SC 끼리는 프로그램 순서
}
struct Outcomes { std::set<std::vector<int>> finals; bool deadlock = false; };                                // 각 결과 = [레지스터들..., 메모리들...]
void dfs(Model m, const std::vector<Thread>& th, int nregs, std::vector<int>& mem, std::vector<std::vector<int>>& regs, std::vector<std::vector<char>>& done, std::set<std::vector<int>>& seen, Outcomes& out) {
    std::vector<int> key = mem; for (size_t t = 0; t < th.size(); ++t) { for (int r : regs[t]) key.push_back(r); for (char d : done[t]) key.push_back(d); } if (!seen.insert(key).second) return;
    bool allDone = true, any = false;
    for (size_t t = 0; t < th.size(); ++t) for (size_t j = 0; j < th[t].size(); ++j) { if (done[t][j]) continue; allDone = false; bool ready = true; for (size_t i = 0; i < j && ready; ++i) if (!done[t][i] && waits(m, th[t][i], th[t][j])) ready = false; if (!ready) continue;
        const Ins& in = th[t][j]; if (in.k == SPIN && !(mem[in.addr] == in.val || (in.addr2 >= 0 && mem[in.addr2] == in.val2))) continue; any = true;
        int saveMem = 0, saveReg = 0; if (in.k == ST || in.k == RMW) saveMem = mem[in.addr]; if (in.reg >= 0) saveReg = regs[t][in.reg];
        if (in.k == ST) mem[in.addr] = in.val; else if (in.k == LD) regs[t][in.reg] = mem[in.addr]; else if (in.k == RMW) { regs[t][in.reg] = mem[in.addr]; mem[in.addr] += in.val; }
        done[t][j] = 1; dfs(m, th, nregs, mem, regs, done, seen, out); done[t][j] = 0;
        if (in.k == ST || in.k == RMW) mem[in.addr] = saveMem; if (in.reg >= 0) regs[t][in.reg] = saveReg; }
    if (allDone) { std::vector<int> o; for (size_t t = 0; t < th.size(); ++t) for (int r : regs[t]) o.push_back(r); for (int v : mem) o.push_back(v); out.finals.insert(o); } else if (!any) out.deadlock = true;           // 아무것도 못 하는데 끝나지 않았다 = 교착
}
Outcomes explore(Model m, const std::vector<Thread>& th, int nregs, int nmem) { std::vector<int> mem(nmem, 0); std::vector<std::vector<int>> regs(th.size(), std::vector<int>(nregs, 0)); std::vector<std::vector<char>> done(th.size()); for (size_t t = 0; t < th.size(); ++t) done[t].assign(th[t].size(), 0); std::set<std::vector<int>> seen; Outcomes out; dfs(m, th, nregs, mem, regs, done, seen, out); return out; }
Ins st(int a, int v, Ord o = RLX) { Ins i; i.k = ST; i.addr = a; i.val = v; i.ord = o; return i; }
Ins ld(int a, int r, Ord o = RLX) { Ins i; i.k = LD; i.addr = a; i.reg = r; i.ord = o; return i; }
Ins fence() { Ins i; i.k = FENCE; return i; }
Ins rmw(int a, int v, int r, Ord o = AR) { Ins i; i.k = RMW; i.addr = a; i.val = v; i.reg = r; i.ord = o; return i; }


const int NI = 20000;
std::vector<std::atomic<int>> arrive(NI), X(NI), Y(NI), R1(NI), R2(NI), R3(NI), R4(NI);
std::vector<Thread> iriw(Ord so, Ord lo) { return {{st(0, 1, so)}, {st(1, 1, so)}, {ld(0, 0, lo), ld(1, 1, lo)}, {ld(1, 0, lo), ld(0, 1, lo)}}; }       // 레지스터: T2 r0,r1 = idx 4,5   T3 r0,r1 = idx 6,7 (스레드당 2 개)
bool iriwForbidden(const Outcomes& o) { for (auto& f : o.finals) if (f[4] == 1 && f[5] == 0 && f[6] == 1 && f[7] == 0) return true; return false; }
std::vector<Thread> peterson(Ord o, bool withFence) { std::vector<Thread> th(2); for (int i = 0; i < 2; ++i) { int other = 1 - i; Ins spin; spin.k = SPIN; spin.addr = other; spin.val = 0; spin.addr2 = 2; spin.val2 = i; spin.ord = o;       // 깃발[상대] == 0 || 차례 == 나
        th[i] = {st(i, 1, o), st(2, other, o)}; if (withFence) th[i].push_back(fence()); th[i].push_back(spin); th[i].push_back(rmw(3, 1, 0, o == RLX ? RLX : AR)); th[i].push_back(rmw(3, -1, 1, o == RLX ? RLX : AR)); th[i].push_back(st(i, 0, o)); } return th; }
bool mutexViolated(const Outcomes& o) { for (auto& f : o.finals) if (f[0] == 1 || f[2] == 1) return true; return false; }       // 임계 구역에 들어갈 때 이미 상대가 안에 있었다 (cs 카운터 읽은 값 1)

int main() {
    assert(!iriwForbidden(explore(SEQ, iriw(RLX, RLX), 2, 2)) && !iriwForbidden(explore(TSO, iriw(RLX, RLX), 2, 2)) && iriwForbidden(explore(WEAK, iriw(RLX, RLX), 2, 2)));                      // ① 
    assert(!iriwForbidden(explore(WEAK, iriw(RLX, ACQ), 2, 2)) && !iriwForbidden(explore(WEAK, iriw(SC, SC), 2, 2)));
    {   Outcomes seq = explore(SEQ, peterson(RLX, false), 2, 4); assert(!mutexViolated(seq) && !seq.deadlock && !seq.finals.empty());                                                      // ② Peterson
        Outcomes tso = explore(TSO, peterson(RLX, false), 2, 4); assert(mutexViolated(tso));                                                                                               // 장벽이 없으면 TSO 에서 깨진다
        Outcomes tsoFence = explore(TSO, peterson(RLX, true), 2, 4); assert(!mutexViolated(tsoFence) && !tsoFence.deadlock);                                                               // 전체 장벽을 두면 성립
        Outcomes weakRlx = explore(WEAK, peterson(RLX, false), 2, 4); assert(mutexViolated(weakRlx));
        Outcomes weakSc = explore(WEAK, peterson(SC, false), 2, 4); assert(!mutexViolated(weakSc) && !weakSc.deadlock); }
    for (int i = 0; i < NI; i++) { arrive[i] = 0; X[i] = 0; Y[i] = 0; }                                         // ③ 실제 IRIW
    auto sync = [&](int i) { arrive[i].fetch_add(1); while (arrive[i].load() < 4) std::this_thread::yield(); };
    std::thread a([&] { for (int i = 0; i < NI; i++) { sync(i); X[i].store(1); } }), b([&] { for (int i = 0; i < NI; i++) { sync(i); Y[i].store(1); } });
    std::thread c([&] { for (int i = 0; i < NI; i++) { sync(i); R1[i] = X[i].load(); R2[i] = Y[i].load(); } }), d([&] { for (int i = 0; i < NI; i++) { sync(i); R3[i] = Y[i].load(); R4[i] = X[i].load(); } });
    a.join(); b.join(); c.join(); d.join(); long forbidden = 0; for (int i = 0; i < NI; i++) forbidden += (R1[i] == 1 && R2[i] == 0 && R3[i] == 1 && R4[i] == 0); assert(forbidden == 0);
    {   std::atomic<int> flag0(0), flag1(0), turn(0); long counter = 0; auto worker = [&](int me) { std::atomic<int>& mine = me == 0 ? flag0 : flag1; std::atomic<int>& theirs = me == 0 ? flag1 : flag0;               // ④ 실제 Peterson
            for (int i = 0; i < 100000; ++i) { mine.store(1); turn.store(1 - me); while (theirs.load() == 1 && turn.load() == 1 - me) std::this_thread::yield(); ++counter; mine.store(0); } };
        std::thread t0(worker, 0), t1(worker, 1); t0.join(); t1.join(); assert(counter == 200000); }
    std::cout << "SequentialConsistency: the exhaustive model showed IRIW's split-world outcome is impossible under SC/TSO and with acquire or seq_cst loads but possible with relaxed loads, Peterson's lock kept mutual exclusion under SC, broke under TSO without a store-load fence (and under relaxed ordering) and held again with a fence or seq_cst; real seq_cst threads never showed the IRIW outcome in " << NI << " trials and a real Peterson lock protected a plain counter to exactly 200000" << std::endl;
    return 0;
}
// Time Complexity: 모형 열거는 상태 수에 비례, 실제 실행 O(N)
// Space Complexity: O(N)
```
# Part 12. 메모리 분석
## MemoryLeak()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <memory>
#include <new>
#include <random>
#include <set>
#include <vector>

// 메모리 누수: 할당한 메모리를 더 이상 가리키는 포인터가 없는데 해제하지 않은 상태.  프로그램이 오래 살수록 쌓여 결국 메모리가 고갈된다.  탐지의 기본: new/delete 를 가로채 "아직 살아있는 할당 수" 를 센다 (Valgrind·ASan 의 LeakSanitizer 도 같은 원리).
//  근본 해결은 RAII: 소유권을 객체에 맡겨 해제를 잊을 수 없게 한다.  여기서는 두 층으로 확인한다 — (1) 전역 operator new/delete 를 가로채 *살아 있는 할당 수*를 세고, (2) 호출 위치(사이트 번호)·크기를 기록하는 추적기로 *누수 목록*을 만든다.
//  ① 오류 경로의 누수: 누수 함수 / 조기 반환 / RAII 버전을 실행했을 때 카운터가 정확히 예상만큼 늘어난다(여기서 일부러 샌 블록은 마지막에 모두 해제해 프로그램 자체는 누수가 없다)
//  ② 순환 shared_ptr 은 스코프를 떠나도 객체 2 개가 *살아 있고*(weak_ptr 이 만료되지 않음), 순환을 끊으면 0 이 되며, weak_ptr 로 만든 구조는 처음부터 새지 않는다
//  ③ 추적기 대조: 무작위 할당/해제 프로그램 20 만 번(사이트 16 곳, 크기 1..4096)에서 *해제하지 않은 블록의 목록·사이트별 개수·총 바이트*가 오라클과 같고 이중/잘못된 해제는 거부  ④ 100 만 번 할당·해제에서 1000 번에 한 번씩 일부러 빠뜨리면 보고된 누수가 정확히 1000 건.
static volatile long liveAllocs = 0;                                      // volatile: 컴파일러는 new 호출이 전역 변수를 바꾸지 않는다고 가정하고 읽기를 앞당길 수 있다
void* operator new(size_t n) { void* p = std::malloc(n ? n : 1); if (!p) throw std::bad_alloc(); liveAllocs = liveAllocs + 1; return p; }
void operator delete(void* p) noexcept { if (p) liveAllocs = liveAllocs - 1; std::free(p); }
void operator delete(void* p, size_t) noexcept { if (p) liveAllocs = liveAllocs - 1; std::free(p); }
void* operator new[](size_t n) { return operator new(n); }                // 배열 형태도 같은 계수기를 지나가게 한다 (새니타이저는 자기 new[] 를 쓴다)
void operator delete[](void* p) noexcept { operator delete(p); }
void operator delete[](void* p, size_t) noexcept { operator delete(p); }
static void* volatile sink;                                             // 포인터를 "사용" 한 것처럼 보이게 해 컴파일러가 할당을 통째로 제거하지 못하게 한다
__attribute__((noinline)) void touch(void* p) { sink = p; }
static int* leakedArrays[8]; static int* leakedSingles[8]; static int nArrays = 0, nSingles = 0;                      // 일부러 샌 블록을 마지막에 정리하려는 기록 (할당 없이 고정 배열)
void leaky() { int* p = new int[100]; p[0] = 1; touch(p); leakedArrays[nArrays++] = p; }                                // 해제하지 않고 반환: 마지막 포인터가 사라진다 → 누수
void early(bool fail) { int* p = new int(5); touch(p); if (fail) { leakedSingles[nSingles++] = p; return; } delete p; }  // 오류 경로에서 해제를 빠뜨린 전형적인 누수
void safe(bool fail) { auto p = std::make_unique<int>(5); touch(p.get()); if (fail) return; }                           // RAII: 어느 경로로 나가도 해제
struct Node { static int live; std::shared_ptr<Node> peer; std::weak_ptr<Node> weakPeer; Node() { ++live; } ~Node() { --live; } }; int Node::live = 0;
struct Tracker {                                                                                                  // 사이트·크기를 기록하는 추적기
    struct Info { size_t size; int site; }; std::map<void*, Info> live; size_t bytes = 0;
    void* alloc(size_t n, int site) { void* p = std::malloc(n); live[p] = {n, site}; bytes += n; return p; }
    bool release(void* p) { auto it = live.find(p); if (it == live.end()) return false; bytes -= it->second.size; std::free(p); live.erase(it); return true; }               // 모르는/이미 해제한 포인터는 거부
    std::map<int, size_t> bySite() const { std::map<int, size_t> m; for (auto& kv : live) ++m[kv.second.site]; return m; }
    void cleanup() { for (auto& kv : live) std::free(kv.first); live.clear(); bytes = 0; }
};

int main() {
    long base = liveAllocs;
    leaky(); assert(liveAllocs == base + 1);                                                                     // ① 누수 1 건
    early(false); assert(liveAllocs == base + 1); early(true); assert(liveAllocs == base + 2);
    safe(true); safe(false); assert(liveAllocs == base + 2);                                                     // RAII 는 어느 경로에서도 늘지 않는다
    for (int i = 0; i < nArrays; ++i) delete[] leakedArrays[i]; for (int i = 0; i < nSingles; ++i) delete leakedSingles[i]; assert(liveAllocs == base);        // 일부러 샌 블록 정리
    {   std::weak_ptr<Node> wa, wb; { auto a = std::make_shared<Node>(), b = std::make_shared<Node>(); a->peer = b; b->peer = a; wa = a; wb = b; assert(a.use_count() == 2 && Node::live == 2); }          // ② 순환: 소유 변수가 사라져도
        assert(Node::live == 2 && !wa.expired() && !wb.expired());                                               // 객체 2 개가 *그대로 살아 있다* = 누수 (아무도 접근할 수 없다)
        { std::shared_ptr<Node> rescue = wa.lock(); rescue->peer.reset(); } assert(Node::live == 0 && wa.expired() && wb.expired()); }                      // 순환을 끊으면 연쇄 해제
    {   auto a = std::make_shared<Node>(), b = std::make_shared<Node>(); a->weakPeer = b; b->weakPeer = a; assert(Node::live == 2 && a.use_count() == 1); } assert(Node::live == 0);               // weak_ptr 구조는 처음부터 새지 않는다
    std::mt19937 rng(1037); Tracker tr; std::vector<void*> blocks; std::map<void*, std::pair<size_t, int>> oracle; long invalidRejected = 0;                                           // ③ 추적기 대조
    for (int step = 0; step < 200000; ++step) { int op = (int)(rng() % 10);
        if (op < 6 || blocks.empty()) { size_t n = 1 + rng() % 4096; int site = (int)(rng() % 16); void* p = tr.alloc(n, site); blocks.push_back(p); oracle[p] = {n, site}; }
        else if (op < 9) { size_t k = rng() % blocks.size(); void* p = blocks[k]; assert(tr.release(p)); assert(!tr.release(p)); oracle.erase(p); blocks[k] = blocks.back(); blocks.pop_back(); ++invalidRejected; }          // 이중 해제는 거부
        else { void* foreign = std::malloc(8); assert(!tr.release(foreign)); std::free(foreign); ++invalidRejected; } }
    std::map<int, size_t> expectSites; size_t expectBytes = 0; for (auto& kv : oracle) { ++expectSites[kv.second.second]; expectBytes += kv.second.first; }
    assert(tr.live.size() == oracle.size() && tr.bySite() == expectSites && tr.bytes == expectBytes && invalidRejected > 1000); tr.cleanup();
    {   Tracker t2; std::set<void*> leaked; for (int i = 0; i < 1000000; ++i) { void* p = t2.alloc(8, i % 16); if (i % 1000 == 999) leaked.insert(p); else assert(t2.release(p)); } assert(t2.live.size() == 1000 && t2.bytes == 8000);          // ④ 정확히 1000 건
        for (auto& kv : t2.live) assert(leaked.count(kv.first)); t2.cleanup(); }
    std::cout << "MemoryLeak: counting operator new/delete exposed each deliberate leak exactly, RAII paths never leaked, a shared_ptr cycle kept both Node objects alive after its owners vanished until the cycle was cut while weak_ptr structures never leaked, and the site-tracking allocator reported exactly the blocks a random program forgot (1000 of 10^6)" << std::endl;
    return 0;
}
// Time Complexity: O(1) 추적 (목록 보고는 O(할당 수))
// Space Complexity: O(1) 카운터, 상세 추적은 O(할당 수)
```
## DanglingPointer()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <stdexcept>
#include <vector>

// 댕글링 포인터: 이미 해제된 메모리를 가리키는 포인터.  원시 포인터는 자신이 유효한지 알 수 없다.  해법 중 하나: 포인터 대신 (슬롯 번호, 세대) 핸들을 쓴다.  해제하면 슬롯의 세대가 올라가 옛 핸들은 세대 불일치로 거부된다 (게임 엔진의 엔티티 ID, Rust 의 slotmap).
//  세대 카운터에는 비트 수가 있다: b 비트 세대는 같은 슬롯이 2^b 번 재사용되면 *한 바퀴 돌아* 옛 핸들이 다시 유효해 보인다(세대 되감김 = ABA).  ① 무작위 생성·삭제·조회 40 만 번(32 비트 세대)을 오라클(핸들 → 기대 값/무효)과 대조: 살아 있는 핸들은 정확한 값, 죽은 핸들은 *항상* 거부
//  ② 8 비트 세대의 정확한 되감김: 슬롯 하나를 반복해 재사용하면 옛 핸들이 255 번째 재사용까지는 거부되고 *정확히 256 번째에서* 다시 유효해진다  ③ 32 비트 세대는 슬롯 재사용 10^6 번 동안 오탐이 없다  ④ weak_ptr: 소유자가 사라지면 expired(), lock() 은 nullptr — 만료 확인과 사용이 원자적이다
//  ⑤ 범위 밖 인덱스·기본값 핸들도 거부.
template <class T, class Gen> class SlotMap {
public:
    struct Handle { uint32_t index; Gen gen; };
    Handle create(const T& v) { uint32_t i; if (freeList.empty()) { slots.push_back(Slot()); i = (uint32_t)slots.size() - 1; } else { i = freeList.back(); freeList.pop_back(); } slots[i].value = v; slots[i].used = true; return {i, slots[i].gen}; }
    bool destroy(Handle h) { if (!valid(h)) return false; slots[h.index].used = false; slots[h.index].gen = (Gen)(slots[h.index].gen + 1); freeList.push_back(h.index); return true; }
    T* get(Handle h) { return valid(h) ? &slots[h.index].value : nullptr; }
    bool valid(Handle h) const { return h.index < slots.size() && slots[h.index].used && slots[h.index].gen == h.gen; }
    size_t size() const { return slots.size(); }
private:
    struct Slot { T value{}; Gen gen = 0; bool used = false; };
    std::vector<Slot> slots; std::vector<uint32_t> freeList;
};
struct Tracked { static int live; int id; explicit Tracked(int i) : id(i) { ++live; } ~Tracked() { --live; } }; int Tracked::live = 0;

int main() {
    std::mt19937 rng(1039); typedef SlotMap<int, uint32_t> Map; Map m; struct Rec { Map::Handle h; int value; bool alive; }; std::vector<Rec> recs; long staleAccesses = 0;
    for (int step = 0; step < 400000; ++step) { int op = (int)(rng() % 10);                                                                                    // ① 오라클 대조
        if (op < 4 || recs.empty()) { int v = (int)rng(); Map::Handle h = m.create(v); recs.push_back({h, v, true}); }
        else if (op < 7) { Rec& r = recs[rng() % recs.size()]; bool ok = m.destroy(r.h); assert(ok == r.alive); r.alive = false; }
        else { Rec& r = recs[rng() % recs.size()]; int* p = m.get(r.h); if (r.alive) { assert(p && *p == r.value); } else { assert(p == nullptr); ++staleAccesses; } } }
    for (auto& r : recs) { int* p = m.get(r.h); assert((p != nullptr) == r.alive && (!p || *p == r.value)); } assert(staleAccesses > 10000);
    {   SlotMap<int, uint8_t> small; auto first = small.create(1); assert(small.get(first) && small.destroy(first) && !small.get(first));                                       // ② 8 비트 되감김
        for (int reuse = 1; reuse <= 300; ++reuse) { auto h = small.create(reuse); assert(h.index == first.index); bool stale = small.get(first) != nullptr; if (reuse < 255) assert(!stale); if (reuse == 255) assert(!stale); small.destroy(h);
            if (reuse == 255) { auto h256 = small.create(256); assert(h256.index == first.index && small.get(first) != nullptr && *small.get(first) == 256); small.destroy(h256); break; } } }                // 256 번째 재사용에서 옛 핸들이 되살아난다
    {   SlotMap<int, uint8_t> small; auto first = small.create(0); small.destroy(first); int revived = -1; for (int reuse = 1; reuse <= 600; ++reuse) { auto h = small.create(reuse); if (small.get(first) && revived < 0) revived = reuse; small.destroy(h); } assert(revived == 256); }        // 처음 되살아나는 재사용 횟수 = 256
    {   Map one; auto h0 = one.create(0); one.destroy(h0); for (int i = 1; i <= 1000000; ++i) { auto h = one.create(i); assert(!one.get(h0) && one.get(h) && *one.get(h) == i); one.destroy(h); } }                            // ③ 32 비트 세대는 오탐 없음
    {   std::weak_ptr<Tracked> w; { auto owner = std::make_shared<Tracked>(7); w = owner; assert(!w.expired() && w.lock()->id == 7 && Tracked::live == 1); } assert(w.expired() && w.lock() == nullptr && Tracked::live == 0);             // ④
        auto owner2 = std::make_shared<Tracked>(8); std::weak_ptr<Tracked> w2 = owner2; auto pinned = w2.lock(); owner2.reset(); assert(!w2.expired() && pinned->id == 8); pinned.reset(); assert(w2.expired()); }                   // lock() 으로 얻은 사본이 수명을 붙잡는다
    {   Map empty; Map::Handle none{0, 0}, far{999999, 0}; assert(empty.get(none) == nullptr && empty.get(far) == nullptr && !empty.destroy(far)); }                                                                               // ⑤
    std::cout << "DanglingPointer: slot-map handles matched an oracle over 4*10^5 operations (" << staleAccesses << " stale lookups all rejected), an 8-bit generation let a stale handle come back to life at exactly the 256th reuse while a 32-bit generation stayed safe over 10^6 reuses, and weak_ptr turned expiry into an atomic check" << std::endl;
    return 0;
}
// Time Complexity: 접근 O(1) + 세대 검사
// Space Complexity: 슬롯당 세대 카운터
```
## WildPointer()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <map>
#include <stdexcept>
#include <cassert>

// 와일드 포인터: 초기화되지 않은 포인터 (쓰레기 값을 주소로 간주).  어디를 가리키는지 알 수 없어 어떤 메모리든 망가뜨릴 수 있다.
// 대책: (1) 항상 초기화 (nullptr)  (2) 해제 후 nullptr 대입  (3) 할당 목록에 등록된 범위만 유효하다고 인정하는 검사기(Registry)
class Registry {
    std::map<uintptr_t, size_t> live;                                    // 시작 주소 -> 크기
public:
    void add(const void* p, size_t n) { live[(uintptr_t)p] = n; }
    void remove(const void* p) { live.erase((uintptr_t)p); }
    bool valid(const void* p, size_t n = 1) const {
        uintptr_t a = (uintptr_t)p; auto it = live.upper_bound(a);
        if (it == live.begin()) return false;
        --it; return a >= it->first && a + n <= it->first + it->second;
    }
};
template <class T> T& checkedDeref(const Registry& r, T* p) {
    if (!p) throw std::runtime_error("null dereference");
    if (!r.valid(p, sizeof(T))) throw std::runtime_error("wild pointer: not inside any live allocation");
    return *p;
}

int main() {
    Registry reg;
    int* heap = new int(7); reg.add(heap, sizeof(int));
    int* init = nullptr;                                                  // 초기화된 포인터: 안전하게 검사 가능
    int* wild = reinterpret_cast<int*>(0x12345678);                       // 초기화되지 않은 포인터가 가질 수 있는 쓰레기 값 (역참조하지 않는다)
    assert(checkedDeref(reg, heap) == 7);
    bool nullCaught = false, wildCaught = false;
    try { checkedDeref(reg, init); } catch (const std::runtime_error&) { nullCaught = true; }
    try { checkedDeref(reg, wild); } catch (const std::runtime_error&) { wildCaught = true; }
    assert(nullCaught && wildCaught);
    reg.remove(heap); delete heap; heap = nullptr;                        // 해제 후 nullptr 대입 습관
    bool afterFree = false; try { checkedDeref(reg, heap); } catch (const std::runtime_error&) { afterFree = true; }
    assert(afterFree);
    std::cout << "WildPointer: null and wild dereferences rejected." << std::endl;
    return 0;
}
// Time Complexity: 검사 O(log N)
// Space Complexity: O(할당 수)
```
## DoubleFree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <csignal>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <vector>
#if defined(__linux__) && defined(__GLIBC__)
#include <sys/wait.h>
#include <unistd.h>
#endif

// 이중 해제: 이미 free 한 포인터를 다시 free.  할당기의 자유 리스트가 망가져 같은 블록이 두 번 할당되는 등 공격에 악용된다.  glibc 는 "free(): double free detected in tcache 2" 로 abort.  검사기는 블록 상태(할당됨/해제됨)를 기록해 두 번째 해제를 거부한다.  nullptr free 는 무해하다.
//  ① 검사 힙(주소별 상태)을 무작위 프로그램 30 만 번으로 대조: 정상 해제 / 이중 해제 / *블록 안쪽 주소 해제* / 모르는 주소 해제 / null 해제의 판정이 오라클과 같고 거부된 해제는 상태를 바꾸지 않음
//  ② 해제된 주소가 *재할당되기 전*에는 이중 해제로, 재할당된 뒤의 옛 포인터 해제는 새 블록을 망가뜨린다(검사기는 "정상 해제" 로 오인) — 그래서 해제 직후 격리(quarantine)가 필요함을 수로 보인다  ③ unique_ptr: 이동 뒤 원본은 nullptr, 컨테이너 안에서 섞고 옮겨도 생성자·소멸자 호출 수가 같고 각 객체는 정확히 한 번 소멸
//  ④ (glibc 에서만, 실제 실행) 자식 프로세스에서 같은 포인터를 두 번 free 하면 SIGABRT 로 종료.
// audit: no-sanitize (실제 이중 해제를 일으킨다 — 새니타이저는 자신의 보고로 종료한다)
class CheckedHeap {
public:
    enum Result { OK, DOUBLE_FREE, INVALID_FREE, NULL_FREE };
    size_t alloc(size_t n) { size_t addr = next; next += n + 16; blocks[addr] = {n, true}; ++liveCnt; return addr; }                                      // 주소를 재사용하지 않는 범프 할당
    Result release(size_t addr) { if (addr == 0) return NULL_FREE; auto it = blocks.upper_bound(addr); if (it == blocks.begin()) return INVALID_FREE; --it;
        if (it->first != addr) return INVALID_FREE; if (!it->second.second) return DOUBLE_FREE; it->second.second = false; --liveCnt; return OK; }                                                     // 블록 시작이 아니면 잘못된 해제
    size_t live() const { return liveCnt; }                                                                                                          // 살아 있는 블록 수(증분 유지)
    size_t recount() const { size_t c = 0; for (auto& kv : blocks) c += kv.second.second; return c; }                                            // 전수 재계산(검증용)
private:
    std::map<size_t, std::pair<size_t, bool>> blocks; size_t next = 4096, liveCnt = 0;
};
struct Counted { static int ctors, dtors; static std::map<int, int> destroyedOnce; int id; explicit Counted(int i) : id(i) { ++ctors; } ~Counted() { ++dtors; ++destroyedOnce[id]; } }; int Counted::ctors = 0, Counted::dtors = 0; std::map<int, int> Counted::destroyedOnce;
void (*volatile freeFn)(void*) = std::free;                                   // 함수 포인터를 거치면 컴파일러가 두 번째 free 를 분석·삭제하지 못한다
void freeTwice(volatile char* p) { freeFn((void*)p); freeFn((void*)p); }

int main() {
    std::mt19937 rng(1041); CheckedHeap h; std::vector<std::pair<size_t, size_t>> ever; std::map<size_t, bool> alive; long counts[4] = {0, 0, 0, 0};                                  // ① 무작위 프로그램
    for (int step = 0; step < 300000; ++step) { int op = (int)(rng() % 10);
        if (op < 4 || ever.empty()) { size_t n = 1 + rng() % 200; size_t a = h.alloc(n); ever.push_back({a, n}); alive[a] = true; }
        else { auto& e = ever[rng() % ever.size()]; size_t addr = e.first; CheckedHeap::Result want; size_t target = addr;
            if (op == 9) { target = 0; want = CheckedHeap::NULL_FREE; } else if (op == 8 && e.second > 1) { target = addr + 1 + rng() % (e.second - 1); want = CheckedHeap::INVALID_FREE; } else if (op == 7) { target = 1 + rng() % 2000; want = CheckedHeap::INVALID_FREE; }       // 안쪽 주소 / 할당된 적 없는 주소
            else want = alive[addr] ? CheckedHeap::OK : CheckedHeap::DOUBLE_FREE;
            size_t liveBefore = h.live(); CheckedHeap::Result got = h.release(target); assert(got == want); ++counts[got]; if (got == CheckedHeap::OK) alive[addr] = false; else assert(h.live() == liveBefore); } }        // 거부된 해제는 상태를 바꾸지 않는다
    assert(h.live() == h.recount()); assert(counts[CheckedHeap::OK] > 1000 && counts[CheckedHeap::DOUBLE_FREE] > 100 && counts[CheckedHeap::INVALID_FREE] > 100 && counts[CheckedHeap::NULL_FREE] > 100);
    {   int heapSize = 4; std::vector<size_t> freedAddr; size_t reused = 0, reusedAndFreedAgainBlindly = 0; (void)heapSize;                                                      // ② 주소를 재사용하는 단순 할당기: 해제 후 곧바로 같은 주소를 돌려준다
        std::map<size_t, bool> allocated; std::vector<size_t> freeStack; size_t nextAddr = 100; auto alloc = [&]() { size_t a; if (!freeStack.empty()) { a = freeStack.back(); freeStack.pop_back(); ++reused; } else { a = nextAddr; nextAddr += 32; } allocated[a] = true; return a; };
        auto freeIt = [&](size_t a) { if (!allocated[a]) return false; allocated[a] = false; freeStack.push_back(a); return true; };
        size_t p = alloc(); assert(freeIt(p) && !freeIt(p));                                                      // 재할당 전의 이중 해제는 잡힌다
        size_t q = alloc(); assert(q == p); bool oldStillFrees = freeIt(p); assert(oldStillFrees); ++reusedAndFreedAgainBlindly;                                      // 재할당 뒤 옛 포인터 p 의 free 는 *성공한다*: 새 소유자 q 의 블록을 망가뜨림
        assert(!allocated[q] && reused == 1 && reusedAndFreedAgainBlindly == 1); }
    {   std::vector<std::unique_ptr<Counted>> v; for (int i = 0; i < 1000; ++i) v.push_back(std::make_unique<Counted>(i)); std::shuffle(v.begin(), v.end(), rng); std::vector<std::unique_ptr<Counted>> moved = std::move(v); assert(v.empty() && moved.size() == 1000);          // ③ unique_ptr
        auto a = std::make_unique<Counted>(5000); auto b = std::move(a); assert(a == nullptr && b != nullptr && Counted::ctors - Counted::dtors == 1001);
        moved.erase(moved.begin() + 10, moved.begin() + 510); assert(Counted::ctors - Counted::dtors == 501); moved.clear(); b.reset(); assert(Counted::ctors == Counted::dtors);
        for (auto& kv : Counted::destroyedOnce) assert(kv.second == 1); assert(Counted::destroyedOnce.size() == 1001); }
#if defined(__linux__) && defined(__GLIBC__)
    {   std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { char* p = (char*)std::malloc(32); p[0] = 1; freeTwice(p); _exit(0); } int st = 0; waitpid(pid, &st, 0); assert(WIFSIGNALED(st) && WTERMSIG(st) == SIGABRT); }              // ④ 실제 glibc
#endif
    std::cout << "DoubleFree: the checked heap classified " << counts[CheckedHeap::OK] << " good frees, " << counts[CheckedHeap::DOUBLE_FREE] << " double frees, " << counts[CheckedHeap::INVALID_FREE] << " invalid frees and " << counts[CheckedHeap::NULL_FREE] << " null frees exactly like the oracle without ever changing state on a rejection; address reuse showed why a stale free after reallocation cannot be caught, unique_ptr destroyed all 1001 objects exactly once, and glibc aborted a real double free with SIGABRT" << std::endl;
    return 0;
}
// Time Complexity: O(log 블록 수)
// Space Complexity: O(블록 수)
```
## UseAfterFree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <deque>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <vector>
#if defined(__linux__)
#include <csignal>
#include <cstdio>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 해제 후 사용(use-after-free): 해제된 메모리를 읽거나 쓴다.  그 사이 같은 메모리가 다른 객체에 재할당되면 두 객체가 서로의 데이터를 덮어쓰는 심각한 취약점이 된다.
// 탐지 기법: (1) 해제된 칸에 독 패턴(0xDD)을 칠하고 (2) 곧바로 재사용하지 않고 격리 구역(quarantine)에 둔다 → 격리 중에 접근하면 즉시 잡힌다 (ASan 의 방식).  격리가 끝난 뒤 *재할당되면* 옛 포인터는 *조용히* 새 소유자의 데이터를 읽는다(별칭).
//  ① 독 칠하기: 해제 뒤 읽으면 0xDD, 쓰기는 거부되어 값이 안 바뀜  ② 재사용 거리: 격리 용량 Q 이면 해제 뒤 *정확히 Q 번* 더 해제해야 그 칸이 재사용 목록에 오른다 (Q = 0,1,2,3,8,64,500 전수)
//  ③ 무작위 프로그램 4 만 단계를 Q = 0, 3, 32 에 같은 논리 순서로 돌려, 옛 포인터 접근의 판정을 *사건 기록을 되감는 독립 오라클* 과 대조 (칸의 마지막 사건이 해제 → UAF, 할당 → 다른 객체이므로 조용한 별칭) — 별칭 수는 Q 가 클수록 줄어든다
//  ④ vector 재할당: 용량이 바뀐 횟수 == 데이터 주소가 바뀐 횟수, reserve 를 먼저 하면 0 번, deque/list 는 push 해도 옛 참조가 유효  ⑤ (Linux, 실제 실행) 해제 = mprotect(PROT_NONE) 인 페이지 격리 할당기: 해제된 페이지를 읽거나 쓰면 자식 프로세스가 SIGSEGV
// audit: no-sanitize (실제 접근 위반을 일으킨다 — 새니타이저는 자신의 보고로 종료한다)
class QuarantineHeap {
public:
    enum Access { OK, USE_AFTER_FREE, WILD };
    static const size_t SLOT = 16;
    QuarantineHeap(size_t slots, size_t quarantine) : mem(slots * SLOT, 0), shadow(slots, UNUSED), Q(quarantine) {}
    size_t alloc() { size_t s; if (!freelist.empty()) { s = freelist.back(); freelist.pop_back(); } else { assert(top < shadow.size()); s = top++; }
        shadow[s] = LIVE; std::fill(&mem[s * SLOT], &mem[s * SLOT] + SLOT, (uint8_t)0); return s * SLOT; }                                                     // 가장 최근에 격리를 마친 칸부터 재사용(LIFO)
    bool release(size_t addr) { size_t s = addr / SLOT; if (addr % SLOT != 0 || s >= top || shadow[s] != LIVE) return false;                       // 이중 해제·잘못된 주소는 거부
        shadow[s] = QUARANTINED; std::fill(&mem[s * SLOT], &mem[s * SLOT] + SLOT, (uint8_t)0xDD); quarantine.push_back(s);                                  // 독 칠하고 격리 구역 맨 뒤에 넣음
        while (quarantine.size() > Q) { size_t old = quarantine.front(); quarantine.pop_front(); shadow[old] = FREE; freelist.push_back(old); } return true; }        // 용량을 넘으면 가장 오래된 칸이 재사용 목록으로
    Access read(size_t addr, uint8_t& out) const { size_t s = addr / SLOT; if (s >= top) return WILD; out = mem[addr]; return shadow[s] == LIVE ? OK : USE_AFTER_FREE; }    // 값은 읽히지만(0xDD) 판정은 UAF
    Access write(size_t addr, uint8_t v) { size_t s = addr / SLOT; if (s >= top) return WILD; if (shadow[s] != LIVE) return USE_AFTER_FREE; mem[addr] = v; return OK; }    // 해제된 칸 쓰기는 막는다
    size_t used() const { return top; }
private:
    enum State { UNUSED, LIVE, QUARANTINED, FREE };
    std::vector<uint8_t> mem; std::vector<State> shadow; std::deque<size_t> quarantine; std::vector<size_t> freelist; size_t top = 0, Q;
};
struct Event { bool isAlloc; int object; };
#if defined(__linux__)
enum Outcome { CLEAN, SEGV, OTHER };
template <class F> Outcome inChild(F f) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); f(); _exit(0); } int st = 0; waitpid(pid, &st, 0);
    if (WIFEXITED(st) && WEXITSTATUS(st) == 0) return CLEAN; if (WIFSIGNALED(st) && WTERMSIG(st) == SIGSEGV) return SEGV; return OTHER; }
#endif

int main() {
    {   QuarantineHeap h(8, 4); size_t p = h.alloc(); uint8_t b = 0;                                                                                                // ① 독 칠하기
        assert(h.write(p, 42) == QuarantineHeap::OK && h.read(p, b) == QuarantineHeap::OK && b == 42);
        bool freed = h.release(p); assert(freed); bool again = h.release(p); assert(!again);
        assert(h.read(p, b) == QuarantineHeap::USE_AFTER_FREE && b == 0xDD); assert(h.write(p, 7) == QuarantineHeap::USE_AFTER_FREE); assert(h.read(p, b) == QuarantineHeap::USE_AFTER_FREE && b == 0xDD);   // 거부된 쓰기는 값을 바꾸지 않음
        assert(h.read(8 * 16, b) == QuarantineHeap::WILD); }
    for (size_t Q : {0, 1, 2, 3, 8, 64, 500}) {                                                                                                                     // ② 재사용 거리 = 정확히 Q
        for (size_t d = 0; d <= Q + 2; ++d) { QuarantineHeap h(Q + 8, Q); size_t p = h.alloc(); std::vector<size_t> filler; for (size_t i = 0; i < Q + 4; ++i) filler.push_back(h.alloc());
            bool ok = h.release(p); assert(ok); for (size_t i = 0; i < d; ++i) { ok = h.release(filler[i]); assert(ok); }
            size_t q = h.alloc(); size_t want = d < Q ? (Q + 5) * 16 : d == Q ? p : filler[d - Q - 1]; assert(q == want); } }                                                         // d<Q: 새 칸, d==Q: 바로 p, d>Q: 가장 최근에 격리를 마친 칸(LIFO)
    long aliasByQ[3] = {0, 0, 0}, uafByQ[3] = {0, 0, 0}; const size_t Qs[3] = {0, 3, 32};
    for (int qi = 0; qi < 3; ++qi) {                                                                                                                                  // ③ 무작위 프로그램 대 사건 기록 오라클
        std::mt19937 rng(2024); QuarantineHeap h(128, Qs[qi]); std::vector<std::vector<Event>> log(128); std::map<int, size_t> addrOf; std::vector<int> live, dead; int nextObj = 0;
        for (int step = 0; step < 40000; ++step) { int op = (int)(rng() % 10);
            if (op < 3 && live.size() < 40) { size_t a = h.alloc(); int o = nextObj++; addrOf[o] = a; live.push_back(o); log[a / 16].push_back({true, o}); h.write(a, (uint8_t)(o & 0x7F)); }               // 새 소유자는 자기 표식을 씀
            else if (op < 6 && !live.empty()) { size_t i = rng() % live.size(); int o = live[i]; live[i] = live.back(); live.pop_back(); bool ok = h.release(addrOf[o]); assert(ok); log[addrOf[o] / 16].push_back({false, o}); dead.push_back(o); }
            else if (!dead.empty()) { int o = dead[rng() % dead.size()]; size_t a = addrOf[o]; uint8_t v = 0; QuarantineHeap::Access got = h.read(a, v);
                const Event& last = log[a / 16].back(); QuarantineHeap::Access want = last.isAlloc ? QuarantineHeap::OK : QuarantineHeap::USE_AFTER_FREE;          // 칸의 마지막 사건이 할당이면 (옛 포인터는 남의 객체를 보므로) 조용히 통과, 해제면 UAF
                assert(got == want); if (got == QuarantineHeap::USE_AFTER_FREE) { assert(v == 0xDD); ++uafByQ[qi]; } else { assert(last.isAlloc && last.object != o && v == (uint8_t)(last.object & 0x7F)); ++aliasByQ[qi]; } } }          // 별칭: 남의 표식이 읽힌다
        assert(h.used() <= 128); }
    assert(aliasByQ[0] > aliasByQ[1] && aliasByQ[1] > aliasByQ[2] && uafByQ[0] < uafByQ[1] && uafByQ[1] < uafByQ[2] && aliasByQ[2] > 0);                                      // 격리가 길수록 잡히는 비율이 높아지지만 0 은 아니다(있는 슬롯 수가 유한)
    {   std::vector<int> v; int changes = 0, moves = 0; const int* last = nullptr; size_t cap = 0; for (int i = 0; i < 5000; ++i) { v.push_back(i); if (v.capacity() != cap) { ++changes; cap = v.capacity(); } if (v.data() != last) { ++moves; last = v.data(); } }   // ④ vector 재할당
        assert(changes == moves && changes >= 2 && changes <= 20);
        std::vector<int> r; r.reserve(5000); const int* first = r.data(); for (int i = 0; i < 5000; ++i) r.push_back(i); assert(r.data() == first);
        std::deque<int> dq(1, 0); int* dp = &dq.front(); for (int i = 1; i < 5000; ++i) dq.push_back(i); assert(dp == &dq.front() && *dp == 0);                                    // deque: push_back 은 참조를 보존
        std::list<int> ls(1, 0); int* lp = &ls.front(); for (int i = 1; i < 5000; ++i) ls.push_back(i); assert(lp == &ls.front() && *lp == 0); }
#if defined(__linux__)
    {   const size_t ps = (size_t)sysconf(_SC_PAGESIZE); char* page = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(page != MAP_FAILED);                  // ⑤ 실제 페이지 격리
        std::strcpy(page, "secret"); assert(inChild([&] { volatile char c = page[0]; (void)c; page[1] = 'x'; }) == CLEAN);                                              // 살아 있는 동안은 정상 접근
        int rc = mprotect(page, ps, PROT_NONE); assert(rc == 0);                                                                                                       // "해제" = 매핑은 두고 권한만 회수(격리)
        assert(inChild([&] { volatile char c = page[0]; (void)c; }) == SEGV); assert(inChild([&] { page[0] = 'x'; }) == SEGV);
        rc = mprotect(page, ps, PROT_READ | PROT_WRITE); assert(rc == 0); assert(std::strcmp(page, "secret") == 0);                                                    // 부모는 영향받지 않았고 데이터도 그대로
        rc = munmap(page, ps); assert(rc == 0); }
#endif
    std::cout << "UseAfterFree: quarantine delayed reuse by exactly Q frees for 7 capacities; the random program matched the event-log oracle (aliasing reads " << aliasByQ[0] << " / " << aliasByQ[1] << " / " << aliasByQ[2] << " for Q=0/3/32); vector moved exactly when capacity changed; a revoked page faulted with SIGSEGV" << std::endl;
    return 0;
}
// Time Complexity: 할당·해제·접근 O(1)
// Space Complexity: O(힙 크기 + Q)
```
## BufferOverflow()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

// 버퍼 오버플로: 버퍼 크기를 넘겨 인접한 메모리를 덮어쓴다.  탐지: 할당 앞뒤에 "레드존" 을 두고 특정 값을 채워 두었다가 해제할 때(또는 접근할 때) 값이 바뀌었는지 본다.
// 안전한 C++: std::array::at / vector::at 의 범위 검사, 길이를 지정하는 복사 함수
// 이 예제는 AddressSanitizer 의 핵심을 직접 만든다 — 그림자 메모리(shadow memory): 메모리 8바이트마다 상태 1바이트 {0: 전부 접근 가능, 1~7: 앞 k 바이트만 접근 가능, 음수: 왼쪽/오른쪽 레드존, 해제됨, 미할당}.
//  모든 접근 앞에서 그림자만 검사하므로 바이트 정밀도로 off-by-one 을 잡고, 해제된 블록은 격리(quarantine)에 한동안 두어 해제 후 사용(UAF)을 잡는다(격리를 벗어나 재사용되면 별칭이 되어 못 잡는다).
// 검증: ① 그림자 검사 == 바이트별 기준(할당 기록에서 바이트마다 분류를 따로 유지) — 무작위 할당/해제/이중 해제/잘못된 해제/접근(1·2·4·8 바이트, 정렬 안 된 것 포함) 60 000 번에서 오류 종류까지 일치
//        ② 격리 닫힌 형태: 격리 용량이 블록 16 개일 때 해제 뒤 15 번 더 해제해도 낡은 포인터는 UAF 로 잡히고, 16 번 더 해제하면 그 블록이 재사용되어 못 잡는다
//        ③ 스택 카나리 모형: 연속 덮어쓰기는 길이 > 버퍼일 때만 탐지(카나리 변경), 카나리 바이트를 알면 memcpy 로는 우회되지만 낮은 바이트가 0 인 카나리는 문자열 복사로는 못 넘는다, 색인으로 반환 주소를 직접 쓰면 카나리가 못 막는다
//        ④ 안전한 복사: 직접 만든 copyBounded 가 snprintf 와 모든 (원본 길이, 대상 크기) 조합에서 같고, strncpy 는 가득 차면 널로 끝나지 않고 짧으면 0 으로 채운다
enum Err { NONE, OVERFLOW, UNDERFLOW, USE_AFTER_FREE, WILD, DOUBLE_FREE, INVALID_FREE };

class ShadowHeap {
    static constexpr int8_t LEFT = -1, RIGHT = -2, FREED = -3, UNALLOC = -4;
    struct Chunk { size_t addr, size, rounded; bool freed; };
    std::vector<int8_t> shadow; std::map<size_t, Chunk> chunks; std::vector<size_t> quarantine; size_t qBytes = 0, qLimit, top; std::map<size_t, std::vector<size_t>> freeLists; size_t heapSize;
    void setUser(const Chunk& c, bool live) {
        for (size_t g = 0; g < c.rounded / 8; ++g) shadow[c.addr / 8 + g] = live ? 0 : FREED;
        if (live && c.size % 8) shadow[c.addr / 8 + c.rounded / 8 - 1] = (int8_t)(c.size % 8);                      // 마지막 8 바이트 묶음은 앞 k 바이트만 사용
    }
public:
    static constexpr size_t RZ = 16;
    ShadowHeap(size_t size, size_t quarantineBytes) : shadow(size / 8, UNALLOC), qLimit(quarantineBytes), top(RZ), heapSize(size) {}
    size_t alloc(size_t n) {                                                                                       // 실패하면 0
        size_t rounded = (n + 7) & ~size_t(7); if (rounded == 0) rounded = 8; size_t addr;
        auto fl = freeLists.find(rounded);
        if (fl != freeLists.end() && !fl->second.empty()) { addr = fl->second.back(); fl->second.pop_back(); }        // 격리를 벗어난 같은 크기 블록을 재사용
        else { if (top + rounded + 2 * RZ > heapSize) return 0; addr = top; top += rounded + 2 * RZ; for (size_t g = 0; g < RZ / 8; ++g) { shadow[(addr - RZ) / 8 + g] = LEFT; shadow[(addr + rounded) / 8 + g] = RIGHT; } }
        Chunk c{addr, n, rounded, false}; chunks[addr] = c; setUser(c, true); return addr;
    }
    Err release(size_t addr) {
        auto it = chunks.find(addr); if (it == chunks.end()) return INVALID_FREE; if (it->second.freed) return DOUBLE_FREE;
        it->second.freed = true; setUser(it->second, false); quarantine.push_back(addr); qBytes += it->second.rounded;
        while (qBytes > qLimit && !quarantine.empty()) { size_t old = quarantine.front(); quarantine.erase(quarantine.begin()); qBytes -= chunks[old].rounded; freeLists[chunks[old].rounded].push_back(old); }   // 격리 용량을 넘으면 가장 오래된 것부터 재사용 가능
        return NONE;
    }
    Err check(size_t addr, size_t n) const {                                                                       // 접근 [addr, addr + n) 검사
        for (size_t b = addr; b < addr + n; ++b) {
            if (b / 8 >= shadow.size()) return WILD;
            int8_t k = shadow[b / 8]; if (k == 0 || (k > 0 && b % 8 < (size_t)k)) continue;
            return k == LEFT ? UNDERFLOW : (k == RIGHT || k > 0) ? OVERFLOW : k == FREED ? USE_AFTER_FREE : WILD;
        }
        return NONE;
    }
};

// 스택 카나리 모형: [버퍼 16][카나리 8][반환 주소 8]
struct Frame {
    uint8_t mem[32]; uint64_t canary; uint64_t evil = 0xDEADBEEFDEADBEEFULL;
    explicit Frame(uint64_t c) : canary(c) { std::memset(mem, 0, sizeof mem); std::memcpy(mem + 16, &c, 8); uint64_t ret = 0x400123; std::memcpy(mem + 24, &ret, 8); }
    uint64_t savedCanary() const { uint64_t c; std::memcpy(&c, mem + 16, 8); return c; }
    uint64_t returnAddress() const { uint64_t r; std::memcpy(&r, mem + 24, 8); return r; }
    bool canaryIntact() const { return savedCanary() == canary; }
};
void strcpyLike(uint8_t* dst, const uint8_t* src) { while (*src) *dst++ = *src++; *dst = 0; }                   // 널에서 멈추는 복사 (strcpy)

size_t copyBounded(char* dst, size_t dstSize, const char* src) {                                                // snprintf 처럼: 항상 널 종단, 원본 전체 길이를 돌려준다
    size_t n = std::strlen(src); if (dstSize) { size_t k = std::min(n, dstSize - 1); std::memcpy(dst, src, k); dst[k] = 0; } return n;
}

int main() {
    // 원래 예
    {   ShadowHeap h(4096, 1024); size_t p = h.alloc(16);
        assert(h.check(p, 16) == NONE && h.check(p, 1) == NONE);                                                  // 정확히 16 바이트: 정상
        assert(h.check(p + 16, 1) == OVERFLOW && h.check(p - 1, 1) == UNDERFLOW);                                 // off-by-one 과 언더플로
        std::array<int, 4> arr = {1, 2, 3, 4}; bool caught = false; try { arr.at(4) = 0; } catch (const std::out_of_range&) { caught = true; } assert(caught); }
    // ① 그림자 검사 == 바이트별 기준
    std::mt19937 rng(77); long accesses = 0, byKind[7] = {0, 0, 0, 0, 0, 0, 0};
    {   const size_t SIZE = 1 << 16; ShadowHeap h(SIZE, 2048); std::vector<Err> truth(SIZE, WILD); struct Rec { size_t addr, n, rounded; bool freed; }; std::vector<Rec> recs;
        auto fill = [&](size_t a, size_t len, Err e) { for (size_t i = 0; i < len; ++i) truth[a + i] = e; };
        for (int step = 0; step < 60000; ++step) {
            int op = (int)(rng() % 100);
            if (op < 30) {
                size_t n = 1 + rng() % 100; size_t a = h.alloc(n); if (!a) continue; size_t r = (n + 7) & ~size_t(7);
                fill(a - ShadowHeap::RZ, ShadowHeap::RZ, UNDERFLOW); fill(a, n, NONE); fill(a + n, r - n + ShadowHeap::RZ, OVERFLOW);                       // 바이트마다 분류를 따로 유지 (왼쪽 레드존, 사용자, 오른쪽 슬랙 + 레드존)
                bool reused = false; for (auto& rec : recs) { if (rec.addr == a) { rec = {a, n, r, false}; reused = true; } } if (!reused) recs.push_back({a, n, r, false});
            } else if (op < 48 && !recs.empty()) {
                Rec& rec = recs[rng() % recs.size()]; Err e = h.release(rec.addr);
                if (rec.freed) assert(e == DOUBLE_FREE); else { assert(e == NONE); rec.freed = true; fill(rec.addr, rec.rounded, USE_AFTER_FREE); }                         // 해제된 구간은 반올림한 크기 전체가 UAF
            } else if (op < 50) { size_t bogus = 8 * (1 + rng() % 8000); bool known = false; for (auto& rec : recs) known |= rec.addr == bogus; if (!known) assert(h.release(bogus) == INVALID_FREE); }
            else {
                size_t a, w = (size_t)1 << (rng() % 4);
                if (!recs.empty() && rng() % 10) { Rec& rec = recs[rng() % recs.size()]; long off = (long)(rng() % (rec.n + 48)) - 24; if ((long)rec.addr + off < 0) off = 0; a = (size_t)((long)rec.addr + off); } else a = rng() % (SIZE + 64);
                Err want = NONE; for (size_t b = a; b < a + w; ++b) { Err e = b < SIZE ? truth[b] : WILD; if (e != NONE) { want = e; break; } }
                assert(h.check(a, w) == want); ++accesses; ++byKind[want];
            }
        }
        assert(byKind[NONE] > 5000 && byKind[OVERFLOW] > 500 && byKind[UNDERFLOW] > 500 && byKind[USE_AFTER_FREE] > 500 && byKind[WILD] > 100); }
    // ② 격리
    {   const size_t Q = 16 * 64; auto scenario = [&](int extraFrees) {
            ShadowHeap h(1 << 16, Q); std::vector<size_t> others; size_t victim = h.alloc(64); for (int i = 0; i < 20; ++i) others.push_back(h.alloc(64));
            assert(h.release(victim) == NONE); for (int i = 0; i < extraFrees; ++i) assert(h.release(others[i]) == NONE);
            if (extraFrees >= 16) { size_t again = h.alloc(64); assert(again == victim); }                                                                         // 격리를 벗어난 블록이 재사용된다
            return h.check(victim, 4); };
        assert(scenario(15) == USE_AFTER_FREE);                                                                      // 격리에 16 개: 아직 격리 안 -> 낡은 포인터를 잡는다
        assert(scenario(16) == NONE); }                                                                              // 17 개째가 들어와 victim 이 밀려나 재사용 -> 별칭이라 못 잡는다 (격리의 한계)
    // ③ 스택 카나리 모형
    {   const uint64_t canary = 0x5a3c9e1d7b2f4a00ULL;                                                                // 낮은 바이트가 0 인 "터미네이터" 카나리
        for (int len = 0; len <= 32; ++len) { Frame f(canary); std::memset(f.mem, 'A', (size_t)len); assert(f.canaryIntact() == (len <= 16)); assert((f.returnAddress() == 0x400123) == (len <= 24)); }   // 연속 덮어쓰기: 길이 > 16 이면 카나리가 먼저 깨진다
        Frame leaked(canary); uint8_t payload[32]; std::memset(payload, 'A', 16); std::memcpy(payload + 16, &canary, 8); std::memcpy(payload + 24, &leaked.evil, 8); std::memcpy(leaked.mem, payload, 32);
        assert(leaked.canaryIntact() && leaked.returnAddress() == leaked.evil);                                      // 카나리 값이 새면 memcpy 로 우회: 카나리는 반환 주소를 못 지킨다
        Frame str(canary); uint8_t sp[33]; std::memcpy(sp, payload, 32); sp[32] = 0; strcpyLike(str.mem, sp);
        assert(str.canaryIntact() && str.returnAddress() == 0x400123);                                               // 문자열 복사는 카나리의 0 바이트에서 멈춘다 -> 반환 주소에 못 닿는다
        Frame idx(canary); idx.mem[24] = 0x99; assert(idx.canaryIntact() && idx.returnAddress() != 0x400123); }      // 색인이 건너뛰는 쓰기는 카나리를 건드리지 않고 반환 주소를 바꾼다
    // ④ 안전한 복사
    {   long cases = 0;
        for (size_t srcLen = 0; srcLen <= 20; ++srcLen) for (size_t dstSize = 0; dstSize <= 24; ++dstSize) {
            std::string src(srcLen, 'x'); for (size_t i = 0; i < srcLen; ++i) src[i] = (char)('a' + i % 26);
            std::vector<char> mine(dstSize + 4, '#'), ref(dstSize + 4, '#');
            size_t r1 = copyBounded(mine.data(), dstSize, src.c_str()); int r2 = std::snprintf(ref.data(), dstSize, "%s", src.c_str());
            assert(r1 == (size_t)r2 && mine == ref);                                                                  // 반환값(원본 길이)과 대상 버퍼의 모든 바이트가 snprintf 와 같다 (경계 밖 4 바이트도 건드리지 않음)
            for (size_t i = dstSize; i < mine.size(); ++i) assert(mine[i] == '#');
            if (dstSize) assert(std::strlen(mine.data()) == std::min(srcLen, dstSize - 1));
            ++cases;
        }
        const char* volatile longSrc = "0123456789"; char d1[8]; std::memset(d1, '#', sizeof d1); std::strncpy(d1, longSrc, sizeof d1); assert(d1[7] == '7' && std::memchr(d1, 0, sizeof d1) == nullptr);        // strncpy: 가득 차면 널로 끝나지 않는다
        char d2[8]; std::memset(d2, '#', sizeof d2); std::strncpy(d2, "ab", sizeof d2); assert(d2[2] == 0 && d2[7] == 0);                                              // 짧으면 나머지를 전부 0 으로 채운다
        assert(cases == 21 * 25); }
    std::cout << "BufferOverflow verified: shadow memory matched the per-byte oracle on " << accesses << " accesses (" << byKind[OVERFLOW] << " overflows, " << byKind[UNDERFLOW] << " underflows, "
              << byKind[USE_AFTER_FREE] << " use-after-free); quarantine boundary, canary limits and snprintf equivalence confirmed." << std::endl;
    return 0;
}
// Time Complexity: 접근 검사 O(접근 크기), 할당·해제 O(1) (격리 큐 제외)
// Space Complexity: 힙 크기 / 8 (그림자) + 할당당 2 · 레드존
```
## HeapCorruption()
### 대표코드
```cpp
#include <cassert>
#include <csignal>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <stdexcept>
#include <vector>
#if defined(__linux__) && defined(__GLIBC__)
#include <sys/wait.h>
#include <unistd.h>
#endif

// 힙 손상: 할당기의 메타데이터(블록 헤더, 자유 리스트 포인터)가 오버플로나 UAF 로 망가진 상태.  이후의 malloc/free 가 엉뚱한 곳에 쓰게 되어 공격에 악용된다.
// 방어: 헤더에 마법 값(magic)과 비밀 키가 섞인 체크섬을 두고, 페이로드 뒤에 카나리 푸터를 붙이며, 힙 전체를 걷는 verify() 로 검증한다 (glibc 의 "free(): invalid size", mcheck, safe-linking 이 그것).
//  블록 배치: [헤더 12B: magic | size | check][페이로드 size B][푸터 카나리 4B] 를 16B 로 올림.  magic 은 LIVE/FREE 두 값이라 이중 해제도 헤더만으로 판별된다.
//  ① 페이로드 크기 {1,4,7,16,33} 마다 블록 안의 모든 바이트를 255 가지 XOR 로 바꾼 경우를 전수(헤더 12B + 푸터 4B 변경 20 400 가지, 페이로드 변경 15 555 가지) — verify() 는 메타데이터 변경을 *전부* 그 블록에서 찾고, 페이로드 변경은 *하나도* 못 찾는다(정상 데이터)
//  ② 푸터 카나리 겹쳐쓰기: 오버플로 1 바이트는 값이 카나리 바이트와 같을 때만(256 중 정확히 1) 놓친다 — 4 바이트 위치 × 256 값 전수에서 못 잡는 경우가 정확히 4  ③ 이웃 헤더까지 넘친 'A' 문자열 오버플로·언더플로는 verify 와 해제에서 모두 잡힘
//  ④ 키 없는 위조: 올바른 키로 만든 헤더 위조는 통과하고 틀린 키로 만든 것은 거부 — 체크섬이 MAC 이 아니라 키에 의존함  ⑤ 무작위 프로그램 3 만 단계는 정상 동작에서 verify() 가 늘 통과하고 페이로드 내용이 std::map 오라클과 같음
//  ⑥ safe-linking: 자유 리스트 다음 포인터를 (위치 >> 12) ^ 포인터 로 저장하면 키를 모르는 덮어쓰기가 16 바이트 정렬 검사를 통과하는 것은 정확히 16 분의 1  ⑦ (glibc, 실제 실행) 청크 크기 필드를 덮고 free 하면 abort
// audit: no-sanitize (실제 힙 손상을 일으킨다 — 새니타이저는 자신의 보고로 종료한다)
class GuardedHeap {
public:
    static const uint32_t LIVE = 0xA110CA7E, FREED = 0xF4EE0000;
    enum Verdict { FINE, BAD_HEADER, BAD_FOOTER };
    explicit GuardedHeap(size_t n, uint32_t k) : mem(n, 0), key(k) {}
    size_t alloc(uint32_t size) { size_t total = blockBytes(size); if (top + total > mem.size()) throw std::bad_alloc(); size_t b = top; top += total; writeHeader(b, LIVE, size); writeFooter(b, size); return b + 12; }
    void release(size_t user) { size_t b = user - 12; Verdict v = check(b); if (v == BAD_HEADER) throw std::runtime_error("free(): invalid pointer / corrupted header"); if (v == BAD_FOOTER) throw std::runtime_error("free(): buffer overflow detected");
        if (get(b) == FREED) throw std::runtime_error("free(): double free"); uint32_t size = get(b + 4); writeHeader(b, FREED, size); std::memset(&mem[user], 0xDD, size); }
    Verdict verifyAll(size_t& badBlock) const { size_t b = 0; while (b < top) { Verdict v = check(b); if (v != FINE) { badBlock = b; return v; } b += blockBytes(get(b + 4)); } return FINE; }   // 힙을 걷는다: 크기를 믿기 전에 헤더부터 검증
    uint8_t* at(size_t pos) { return &mem[pos]; }
    size_t top = 0;
    static size_t blockBytes(uint32_t size) { return (12 + (size_t)size + 4 + 15) / 16 * 16; }
    uint32_t headerCheck(uint32_t magic, uint32_t size) const { return (magic ^ size ^ key) * 2654435761u; }                                                                  // 키가 섞인 체크섬
    uint32_t canary(size_t b) const { return (uint32_t)(b * 2246822519u) ^ key ^ 0x5bd1e995u; }                                                                              // 블록 위치와 키에서 정해지는 카나리
    void writeHeader(size_t b, uint32_t magic, uint32_t size) { put(b, magic); put(b + 4, size); put(b + 8, headerCheck(magic, size)); }
    void writeFooter(size_t b, uint32_t size) { put(b + 12 + size, canary(b)); }
    Verdict check(size_t b) const { uint32_t magic = get(b), size = get(b + 4); if ((magic != LIVE && magic != FREED) || get(b + 8) != headerCheck(magic, size) || b + blockBytes(size) > mem.size()) return BAD_HEADER;
        if (get(b + 12 + size) != canary(b)) return BAD_FOOTER; return FINE; }
    uint32_t get(size_t p) const { uint32_t v; std::memcpy(&v, &mem[p], 4); return v; }
    void put(size_t p, uint32_t v) { std::memcpy(&mem[p], &v, 4); }
    std::vector<uint8_t> mem; uint32_t key;
};
uint64_t protectLink(uint64_t where, uint64_t ptr) { return (where >> 12) ^ ptr; }                                                                                              // glibc 2.32 safe-linking
bool alignedAfterUnprotect(uint64_t where, uint64_t stored) { return (((where >> 12) ^ stored) & 0xF) == 0; }

int main() {
    {   // ① 메타데이터 구역 전수
        long headerFlips = 0, footerFlips = 0, payloadFlips = 0, detected = 0;
        for (uint32_t size : {1u, 4u, 7u, 16u, 33u}) for (int where = 0; where < 12 + (int)size + 4; ++where) for (int x = 1; x < 256; ++x) {
            GuardedHeap h(512, 0x9E3779B9u); size_t a = h.alloc(size); size_t b = h.alloc(20); (void)b; for (uint32_t i = 0; i < size; ++i) h.at(a)[i] = (uint8_t)(i * 3 + 1);
            bool inMeta = where < 12 || where >= 12 + (int)size; h.at(0)[where] ^= (uint8_t)x; size_t bad = 99; GuardedHeap::Verdict v = h.verifyAll(bad);
            if (where < 12) ++headerFlips; else if (where >= 12 + (int)size) ++footerFlips; else ++payloadFlips;
            if (inMeta) { assert(v != GuardedHeap::FINE && bad == 0); ++detected; assert(v == (where < 12 ? GuardedHeap::BAD_HEADER : GuardedHeap::BAD_FOOTER)); } else assert(v == GuardedHeap::FINE); }   // 페이로드는 그냥 데이터
        assert(detected == headerFlips + footerFlips && headerFlips == 5 * 12 * 255 && footerFlips == 5 * 4 * 255 && payloadFlips == (1 + 4 + 7 + 16 + 33) * 255); }
    {   // ② 푸터 카나리: 1 바이트 오버플로
        long missed = 0; for (int j = 0; j < 4; ++j) for (int v = 0; v < 256; ++v) { GuardedHeap h(256, 0x1234567u); size_t a = h.alloc(8); uint8_t want = h.at(a + 8)[j]; h.at(a)[8 + j] = (uint8_t)v; size_t bad; GuardedHeap::Verdict r = h.verifyAll(bad); if (r == GuardedHeap::FINE) { ++missed; assert((uint8_t)v == want); } else assert(r == GuardedHeap::BAD_FOOTER); }
        assert(missed == 4); }                                                                                                                                         // 위치마다 카나리와 같은 값 하나만 통과
    {   // ③ 이웃 헤더까지 넘친 오버플로·언더플로
        GuardedHeap h(256, 77); size_t a = h.alloc(16), b = h.alloc(16); std::memset(h.at(a), 'A', 16 + 4 + 12); size_t bad = 0;                                           // 푸터 4B + 이웃 헤더 12B 를 모두 덮음
        assert(h.verifyAll(bad) == GuardedHeap::BAD_FOOTER && bad == 0); bool threw = false; try { h.release(a); } catch (const std::runtime_error& e) { threw = std::string(e.what()).find("overflow") != std::string::npos; } assert(threw);
        threw = false; try { h.release(b); } catch (const std::runtime_error& e) { threw = std::string(e.what()).find("header") != std::string::npos; } assert(threw);        // 이웃은 자기 헤더가 깨져서 거부
        GuardedHeap g(256, 77); size_t c = g.alloc(16); g.at(c)[-1] ^= 0x40; threw = false; try { g.release(c); } catch (const std::runtime_error&) { threw = true; } assert(threw); }   // 언더플로: 헤더 마지막 바이트
    {   // ④ 위조
        uint32_t key = 0xC0FFEE11u; GuardedHeap h(256, key); size_t a = h.alloc(16); (void)h.alloc(16);
        h.writeHeader(0, GuardedHeap::LIVE, 200); size_t bad; GuardedHeap::Verdict v = h.verifyAll(bad); assert(v == GuardedHeap::BAD_FOOTER || v == GuardedHeap::BAD_HEADER);           // 크기만 바꾸면 푸터 위치가 어긋나 발각(헤더 체크섬도 갱신했으므로 푸터에서)
        GuardedHeap g(512, key); size_t c = g.alloc(16); (void)c; (void)g.alloc(16); uint32_t forgedSize = 16;                                                              // 키를 아는 공격자의 "일관된" 위조 = 원래 값 그대로 → 구별 불가
        g.put(8, (GuardedHeap(0, key)).headerCheck(GuardedHeap::LIVE, forgedSize)); assert(g.verifyAll(bad) == GuardedHeap::FINE);
        GuardedHeap wrongKey(0, key ^ 1); g.put(8, wrongKey.headerCheck(GuardedHeap::LIVE, forgedSize)); assert(g.verifyAll(bad) == GuardedHeap::BAD_HEADER && bad == 0); (void)a; }   // 틀린 키로 만든 체크섬은 거부
    {   // ⑤ 정상 프로그램은 늘 통과
        std::mt19937 rng(77); GuardedHeap h(1 << 22, 0xDEADBEEFu); std::map<size_t, std::vector<uint8_t>> liveData; std::vector<size_t> freedUsers;
        for (int step = 0; step < 30000; ++step) { int op = (int)(rng() % 10);
            if (op < 5 && h.top < (1u << 22) - 4096) { uint32_t n = 1 + rng() % 200; size_t u = h.alloc(n); std::vector<uint8_t> data(n); for (auto& x : data) x = (uint8_t)rng(); std::memcpy(h.at(u), data.data(), n); liveData[u] = data; }
            else if (op < 8 && !liveData.empty()) { auto it = liveData.begin(); std::advance(it, rng() % liveData.size()); assert(std::memcmp(h.at(it->first), it->second.data(), it->second.size()) == 0); h.release(it->first); freedUsers.push_back(it->first); liveData.erase(it); }
            else if (!freedUsers.empty()) { bool threw = false; try { h.release(freedUsers[rng() % freedUsers.size()]); } catch (const std::runtime_error& e) { threw = std::string(e.what()).find("double free") != std::string::npos; } assert(threw); }                // 이중 해제는 헤더의 FREED 로 판별
            if (step % 1000 == 0) { size_t bad; assert(h.verifyAll(bad) == GuardedHeap::FINE); } }
        size_t bad; assert(h.verifyAll(bad) == GuardedHeap::FINE); for (auto& kv : liveData) assert(std::memcmp(h.at(kv.first), kv.second.data(), kv.second.size()) == 0); }
    {   // ⑥ safe-linking
        const uint64_t where = 0x55555555a2c0ULL; uint64_t real = 0x55555555a300ULL; assert(real % 16 == 0 && alignedAfterUnprotect(where, protectLink(where, real)) && (protectLink(where, real) ^ (where >> 12)) == real);   // 정상 저장·복원
        int pass = 0; for (uint64_t rawLow = 0; rawLow < 16; ++rawLow) for (uint64_t high = 0; high < 64; ++high) { uint64_t raw = (high << 4) | rawLow; if (alignedAfterUnprotect(where, raw)) ++pass; }      // 공격자가 날것의 값을 덮어쓴다
        assert(pass == 64 && pass * 16 == 16 * 64);                                                                                                                     // 1024 가지 중 정확히 1/16
        uint64_t leaked = where >> 12; uint64_t target = 0x7ffff7e0a000ULL; uint64_t forged = leaked ^ target; assert(alignedAfterUnprotect(where, forged) && ((where >> 12) ^ forged) == target); }   // 힙 주소를 누출한 공격자는 통과(그래서 누출이 선행 조건)
#if defined(__linux__) && defined(__GLIBC__)
    {   std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { char* p = (char*)std::malloc(40); volatile uint64_t* chunkSize = (volatile uint64_t*)(p - 8); *chunkSize = 0x4141414141414141ULL; std::free(p); _exit(0); }   // ⑦ 실제 glibc (volatile: 해제 직전의 죽은 저장으로 지워지지 않게)
        int st = 0; waitpid(pid, &st, 0); assert(WIFSIGNALED(st) && WTERMSIG(st) == SIGABRT); }
#endif
    std::cout << "HeapCorruption: every single-byte change of the metadata bytes was caught in all 20400 enumerated cases while 15555 payload changes were never flagged; footer-canary misses were exactly 4 of 1024; a 12-byte header smash, underflow and double free were rejected; safe-linking passed 1/16 of raw overwrites; glibc aborted on a smashed chunk size" << std::endl;
    return 0;
}
// Time Complexity: 할당 O(1), 검증 O(블록 수)
// Space Complexity: 블록당 헤더 12B + 푸터 4B (16B 정렬)
```
# Part 13. 파일과 메모리
## MemoryMappedFile()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

// 메모리 맵 파일: mmap 으로 파일을 프로세스 주소 공간에 붙이면 read/write 시스템 호출 없이 포인터로 파일 내용을 읽고 쓴다.
// 페이지를 처음 만질 때 커널이 파일에서 읽어 오고(페이지 캐시와 공유 -> 복사 1회 절약), MAP_SHARED 로 수정하면 파일에 반영된다
// 이 예제는 의미를 하나씩 확인하고, 마지막에 mmap 위에 영속 로그를 만들어 닫았다 다시 열어도 내용이 보존되는지 대조한다:
//  ① MAP_SHARED 쓰기는 pread 로 보이고, MAP_PRIVATE 쓰기는 파일에 안 간다(쓰기 시 복사)  ② 같은 파일의 두 MAP_SHARED 매핑은 msync 없이도 서로의 쓰기를 즉시 본다(같은 페이지 캐시)
//  ③ 파일 끝이 페이지 중간이면 그 페이지의 나머지는 0 으로 읽히고 거기 쓴 것은 파일에 반영되지 않는다(파일 크기 불변)  ④ 오프셋은 페이지 크기의 배수여야 한다(아니면 EINVAL)
//  ⑤ 읽는 세 방법 — read, pread, mmap — 이 무작위 위치·길이 3 000 번에서 같은 바이트  ⑥ 영속 로그(머리 + 항목 배열): 항목을 쓰고 커밋(개수 갱신)한 뒤 msync·munmap·재매핑, 파일을 ftruncate 로 늘려 다시 매핑해도 이전 항목이 보존 —
//        std::vector 모형과 5 번의 열기/닫기·증설을 거쳐 일치, 커밋하지 않은 항목은 다시 열면 보이지 않음(찢어진 쓰기 모형)
#if defined(__unix__) || defined(__APPLE__)
struct LogHeader { uint64_t magic, count, capacity; };
class MappedLog {                                                                              // [LogHeader][uint64_t 항목 capacity 개]
    int fd = -1; char* base = nullptr; size_t bytes = 0; std::string path;
    static size_t sizeFor(uint64_t capacity) { return sizeof(LogHeader) + capacity * sizeof(uint64_t); }
    void mapAll(size_t n) { base = (char*)mmap(nullptr, n, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0); assert(base != MAP_FAILED); bytes = n; }
public:
    explicit MappedLog(const std::string& p) : path(p) {
        fd = open(path.c_str(), O_RDWR | O_CREAT, 0600); assert(fd >= 0); struct stat st; fstat(fd, &st);
        if (st.st_size == 0) { assert(ftruncate(fd, (off_t)sizeFor(4)) == 0); mapAll(sizeFor(4)); *hdr() = {0x4c4f4721, 0, 4}; }
        else { mapAll((size_t)st.st_size); assert(hdr()->magic == 0x4c4f4721); }
    }
    ~MappedLog() { if (base) { msync(base, bytes, MS_SYNC); munmap(base, bytes); } if (fd >= 0) close(fd); }
    LogHeader* hdr() { return reinterpret_cast<LogHeader*>(base); }
    uint64_t* items() { return reinterpret_cast<uint64_t*>(base + sizeof(LogHeader)); }
    uint64_t count() { return hdr()->count; }
    void stage(uint64_t v) {                                                                    // 항목만 쓰고 개수는 올리지 않는다 (아직 커밋 전)
        if (hdr()->count == hdr()->capacity) { grow(); }
        items()[hdr()->count] = v;
    }
    void commit() { hdr()->count++; msync(base, bytes, MS_SYNC); }                              // 개수를 올리는 것이 커밋 지점
    void append(uint64_t v) { stage(v); commit(); }
    void grow() {                                                                               // ftruncate 로 파일을 두 배로 늘리고 다시 매핑 (주소가 바뀔 수 있다)
        uint64_t newCap = hdr()->capacity * 2; msync(base, bytes, MS_SYNC); munmap(base, bytes); assert(ftruncate(fd, (off_t)sizeFor(newCap)) == 0); mapAll(sizeFor(newCap)); hdr()->capacity = newCap;
    }
};
#endif

int main() {
#if defined(__unix__) || defined(__APPLE__)
    char path[] = "/tmp/ds_mmap_XXXXXX"; int fd = mkstemp(path); assert(fd >= 0); const long ps = sysconf(_SC_PAGESIZE);
    std::string content(2 * ps, 'a'); content.replace(ps, 5, "HELLO");                                  // 두 페이지짜리 파일, 둘째 페이지 앞에 HELLO
    assert(write(fd, content.data(), content.size()) == (ssize_t)content.size());
    char* m = (char*)mmap(nullptr, content.size(), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0); assert(m != MAP_FAILED);
    assert(m[0] == 'a' && std::memcmp(m + ps, "HELLO", 5) == 0);                                        // 포인터로 파일 내용을 읽는다
    std::memcpy(m + 10, "WORLD", 5); msync(m, content.size(), MS_SYNC);
    char check[6] = {0}; assert(pread(fd, check, 5, 10) == 5 && std::strcmp(check, "WORLD") == 0);       // ① 공유 매핑의 쓰기는 read 로 보인다
    // ① 비공개 매핑: 쓰기 시 복사
    char* priv = (char*)mmap(nullptr, content.size(), PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0); assert(priv != MAP_FAILED);
    std::memcpy(priv + 20, "PRIVATE", 7); char c2[8] = {0}; assert(pread(fd, c2, 7, 20) == 7 && std::memcmp(c2, "aaaaaaa", 7) == 0 && std::memcmp(priv + 20, "PRIVATE", 7) == 0 && std::memcmp(m + 20, "aaaaaaa", 7) == 0);   // 파일과 공유 매핑은 그대로
    // ② 두 공유 매핑은 msync 없이도 서로의 쓰기를 본다
    char* m2 = (char*)mmap(nullptr, content.size(), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0); assert(m2 != MAP_FAILED && m2 != m);
    m[100] = 'X'; assert(m2[100] == 'X'); m2[101] = 'Y'; assert(m[101] == 'Y');
    munmap(m2, content.size()); munmap(priv, content.size()); munmap(m, content.size());
    // ④ 정렬되지 않은 오프셋
    assert(mmap(nullptr, ps, PROT_READ, MAP_SHARED, fd, 1) == MAP_FAILED);
    close(fd); unlink(path);
    // ③ 파일 끝이 페이지 중간
    {   char p2[] = "/tmp/ds_mmap2_XXXXXX"; int f2 = mkstemp(p2); assert(f2 >= 0); std::string small(5000, 'z'); assert(write(f2, small.data(), small.size()) == 5000);
        char* mm = (char*)mmap(nullptr, 2 * ps, PROT_READ | PROT_WRITE, MAP_SHARED, f2, 0); assert(mm != MAP_FAILED);
        for (long i = 5000; i < 2 * ps && i < 8192; ++i) assert(mm[i] == 0);                                // 파일 끝 뒤 같은 페이지의 나머지는 0
        mm[5100] = 'Q'; msync(mm, ps * 2, MS_SYNC); struct stat st; fstat(f2, &st); assert(st.st_size == 5000);                                  // 쓰기는 파일 크기를 늘리지 않는다
        char tail[1] = {0}; assert(pread(f2, tail, 1, 5100) == 0);                                          // 읽어도 파일 끝이라 아무것도 없다
        munmap(mm, 2 * ps); close(f2); unlink(p2); }
    // ⑤ 세 가지 읽기 방법
    {   char p3[] = "/tmp/ds_mmap3_XXXXXX"; int f3 = mkstemp(p3); assert(f3 >= 0); std::mt19937 rng(5); std::vector<unsigned char> data(1 << 20); for (auto& b : data) b = (unsigned char)rng();
        assert(write(f3, data.data(), data.size()) == (ssize_t)data.size());
        unsigned char* mm = (unsigned char*)mmap(nullptr, data.size(), PROT_READ, MAP_SHARED, f3, 0); assert(mm != MAP_FAILED);
        long agree = 0; for (int i = 0; i < 3000; ++i) {
            size_t off = rng() % data.size(), len = 1 + rng() % std::min<size_t>(5000, data.size() - off); std::vector<unsigned char> viaPread(len), viaRead(len);
            assert(pread(f3, viaPread.data(), len, (off_t)off) == (ssize_t)len); assert(lseek(f3, (off_t)off, SEEK_SET) == (off_t)off); assert(read(f3, viaRead.data(), len) == (ssize_t)len);
            assert(viaPread == viaRead && std::memcmp(mm + off, viaRead.data(), len) == 0 && std::memcmp(data.data() + off, mm + off, len) == 0); ++agree; }
        assert(agree == 3000); munmap(mm, data.size()); close(f3); unlink(p3); }
    // ⑥ 영속 로그
    {   char p4[] = "/tmp/ds_maplog_XXXXXX"; int f4 = mkstemp(p4); assert(f4 >= 0); close(f4); unlink(p4); std::string lp = p4; std::vector<uint64_t> model; std::mt19937_64 rng(6); int sessions = 5; long total = 0;
        for (int s = 0; s < sessions; ++s) {
            MappedLog log(lp); assert(log.count() == model.size());                                       // 다시 열었더니 이전 항목이 그대로
            for (uint64_t i = 0; i < log.count(); ++i) assert(log.items()[i] == model[i]);
            int n = 50 + (int)(rng() % 400); for (int i = 0; i < n; ++i) { uint64_t v = rng(); log.append(v); model.push_back(v); ++total; }
            if (s % 2 == 1) { log.stage(0xDEADBEEF); }                                                    // 커밋하지 않은 항목: 개수를 올리지 않았으므로 다시 열면 보이지 않는다
            assert(log.count() == model.size());
        }
        { MappedLog log(lp); assert(log.count() == model.size() && log.hdr()->capacity >= log.count()); for (size_t i = 0; i < model.size(); ++i) assert(log.items()[i] == model[i]); }
        unlink(lp.c_str()); assert(total > 500); }
    std::cout << "MemoryMappedFile verified: shared/private semantics, EOF-page zero fill, three read paths agree on 3000 random reads, and a persistent log survived 5 close/reopen/grow cycles." << std::endl;
#else
    std::cout << "MemoryMappedFile: POSIX-only demonstration (mmap)" << std::endl;
#endif
    return 0;
}
// Time Complexity: 접근 시 페이지 폴트 O(1) (캐시에 있으면 복사 없음), 증설은 재매핑 O(1) + 새 페이지만 폴트
// Space Complexity: 페이지 캐시 공유
```
## SharedMemory()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <new>
#include <vector>
#if defined(__linux__)
#include <sys/mman.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 공유 메모리: 서로 다른 프로세스(혹은 같은 프로세스의 서로 다른 가상 주소)가 *같은 물리 페이지* 를 가리키게 한다 → 복사 없는 가장 빠른 프로세스 간 통신.  동기화는 직접 해야 한다: 락 프리 원자 변수를 공유 영역에 두면 프로세스 사이에서도 원자적이다.
//  ① MAP_SHARED 와 MAP_PRIVATE 의 차이: 자식의 쓰기가 부모에게 보이는지(공유) / 안 보이는지(사유, COW) / 힙 변수는 안 보이는지  ② memfd 로 만든 한 페이지를 *두 개의 서로 다른 가상 주소* 에 매핑 — 한쪽에 쓰면 다른 쪽에 즉시 보인다
//  ③ 자식 4 개 × 5 만 번 fetch_add → 합이 정확히 20 만 (원자성은 프로세스 경계를 넘는다)  ④ 공유 영역의 스핀락으로 보호한 *평범한* 두 정수 불변식(a + b == 상수) — 자식 4 개가 3 만 번씩 이동시켜도 항상 합이 같고 마지막 합 계산도 일치
//  ⑤ 공유 메모리 SPSC 링 버퍼: 자식(생산자)이 1..N 을 acquire/release 원자 인덱스로 넘기고 부모(소비자)가 순서·합을 검증  ⑥ 모든 자식은 정상 종료(상태 0)
// audit: no-sanitize (프로세스 분기 + 공유 매핑 — 새니타이저와 함께 쓰지 않는다)
struct Shared { std::atomic<int> counter; std::atomic<int> lock; long a, b; };
struct Ring { static const int CAP = 1024; std::atomic<uint32_t> head, tail; uint32_t slot[CAP]; };
static_assert(std::atomic<int>::is_always_lock_free && std::atomic<uint32_t>::is_always_lock_free, "프로세스 간 공유에는 락 없는 원자 연산이 필요");

#if defined(__linux__)
int runChild(void (*body)()) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { body(); _exit(0); } return pid; }
template <class F> int runChildLambda(F f) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { f(); _exit(0); } return pid; }
void waitOk(pid_t pid) { int st = 0; waitpid(pid, &st, 0); assert(WIFEXITED(st) && WEXITSTATUS(st) == 0); }
#endif

int main() {
#if defined(__linux__)
    const size_t ps = (size_t)sysconf(_SC_PAGESIZE);
    {   char* sh = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0); char* pr = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(sh != MAP_FAILED && pr != MAP_FAILED);   // ① 공유 / 사유
        int* heapVar = new int(1); sh[0] = 'p'; pr[0] = 'p';
        pid_t pid = runChildLambda([&] { sh[0] = 'c'; pr[0] = 'c'; *heapVar = 2; }); waitOk(pid);
        assert(sh[0] == 'c' && pr[0] == 'p' && *heapVar == 1);                                                                                                       // 공유만 보인다, 사유·힙은 fork 시점의 복사본
        delete heapVar; munmap(sh, ps); munmap(pr, ps); }
    {   int fd = (int)syscall(SYS_memfd_create, "shm", 0); assert(fd >= 0); int rc = ftruncate(fd, (off_t)ps); assert(rc == 0);                                                   // ② 한 물리 페이지, 두 가상 주소
        char* a = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0); char* b = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0); assert(a != MAP_FAILED && b != MAP_FAILED && a != b);
        for (size_t i = 0; i < ps; i += 97) { a[i] = (char)(i / 97 + 1); assert(b[i] == a[i]); } b[5] = 'Z'; assert(a[5] == 'Z');                                           // 양방향으로 즉시 보임
        pid_t pid = runChildLambda([&] { a[100] = 'K'; }); waitOk(pid); assert(b[100] == 'K'); munmap(a, ps); assert(b[5] == 'Z'); munmap(b, ps); close(fd); }                   // 한쪽을 해제해도 다른 쪽은 유효
    Shared* s = (Shared*)mmap(nullptr, sizeof(Shared), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0); assert(s != MAP_FAILED); new (&s->counter) std::atomic<int>(0); new (&s->lock) std::atomic<int>(0); s->a = 1000; s->b = 0;
    const int KIDS = 4, N = 50000; std::vector<pid_t> kids;
    for (int k = 0; k < KIDS; ++k) kids.push_back(runChildLambda([&] { for (int i = 0; i < N; ++i) s->counter.fetch_add(1, std::memory_order_relaxed); }));                      // ③ 원자 증가
    for (pid_t p : kids) waitOk(p); assert(s->counter.load() == KIDS * N);
    kids.clear(); const int MOVES = 30000;
    for (int k = 0; k < KIDS; ++k) kids.push_back(runChildLambda([&] { for (int i = 0; i < MOVES; ++i) { int expected = 0; while (!s->lock.compare_exchange_weak(expected, 1, std::memory_order_acquire)) expected = 0;            // ④ 공유 스핀락
        s->a -= 1; s->b += 1; assert(s->a + s->b == 1000); s->lock.store(0, std::memory_order_release); } }));                                                                       // 임계구역 안에서 합이 늘 1000
    for (pid_t p : kids) waitOk(p); assert(s->a + s->b == 1000 && s->b == (long)KIDS * MOVES && s->a == 1000 - (long)KIDS * MOVES);
    munmap(s, sizeof(Shared));
    Ring* ring = (Ring*)mmap(nullptr, sizeof(Ring), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0); assert(ring != MAP_FAILED); new (&ring->head) std::atomic<uint32_t>(0); new (&ring->tail) std::atomic<uint32_t>(0); const uint32_t TOTAL = 200000;       // ⑤ SPSC 링
    pid_t producer = runChildLambda([&] { for (uint32_t i = 1; i <= TOTAL; ++i) { uint32_t t = ring->tail.load(std::memory_order_relaxed); while (t - ring->head.load(std::memory_order_acquire) == Ring::CAP) {}   // 가득 차면 대기
        ring->slot[t % Ring::CAP] = i; ring->tail.store(t + 1, std::memory_order_release); } });                                                                              // 데이터를 쓴 뒤 release 로 공개
    uint64_t sum = 0; for (uint32_t expect = 1; expect <= TOTAL; ++expect) { uint32_t h = ring->head.load(std::memory_order_relaxed); while (ring->tail.load(std::memory_order_acquire) == h) {}
        uint32_t v = ring->slot[h % Ring::CAP]; assert(v == expect); sum += v; ring->head.store(h + 1, std::memory_order_release); }
    waitOk(producer); assert(sum == (uint64_t)TOTAL * (TOTAL + 1) / 2); munmap(ring, sizeof(Ring));
    std::cout << "SharedMemory: MAP_SHARED writes crossed the process boundary while MAP_PRIVATE and heap writes did not; one memfd page mapped at two addresses stayed coherent; 4 processes made " << KIDS * N << " atomic increments and " << (long)KIDS * MOVES << " lock-protected moves exactly; a shared ring delivered " << TOTAL << " values in order" << std::endl;
#else
    std::cout << "SharedMemory: Linux-only demonstration (mmap + fork + memfd)" << std::endl;
#endif
    return 0;
}
// Time Complexity: 접근 O(1), 동기화는 프로세스 수에 비례한 경쟁
// Space Complexity: 공유 영역 1벌 (프로세스 수와 무관)
```
## CopyOnWrite()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <thread>
#include <vector>
#if defined(__unix__) || defined(__APPLE__)
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 쓰기 시 복사(CoW): 복사본을 만든다고 해 놓고 실제 복사는 "쓰는 순간" 까지 미룬다.  fork 직후 부모와 자식은 같은 물리 페이지를 읽기 전용으로 공유하다가,
// 어느 쪽이 쓰면 그 페이지만 복제한다 -> fork 가 빠르고 메모리를 아낀다.  사용자 공간에서도 문자열·버퍼에 같은 기법을 쓴다
// 사용자 공간 CoW 문자열을 직접 만든다: 공유 블록 + 원자적 참조 횟수, 쓰기 직전 참조가 둘 이상이면 분리(detach).
// 검증: ① 무작위 연산(복사·대입·쓰기·읽기·소멸) 20 000 번을 "핸들마다 독립된 std::string" 모형과 대조 — 모든 핸들의 내용이 같고, owners() 가 "같은 블록을 공유하는 핸들 수" 와 같고(모형이 공유 그룹을 따로 추적),
//        분리 횟수와 살아 있는 블록 수가 모형과 같다  ② 스레드 8 개가 각자 복사본을 쓰기: 원본 핸들이 살아 있는 동안은 모두가 정확히 한 번씩 분리하고(8 번), 원본은 안 바뀌고, 소멸 뒤 블록이 하나도 안 남는다
//        ③ (POSIX) 진짜 fork: 자식이 쓴 값은 부모에게 안 보이고, 부모가 먼저 써도 자식은 옛 값을 보며, MAP_SHARED 는 대조적으로 서로 보인다.  페이지 폴트 수: 쓰면 페이지마다 CoW 폴트가 난다
class CowString {
    struct Block { std::atomic<long> refs{1}; std::string data; explicit Block(std::string s) : data(std::move(s)) { ++alive; } ~Block() { --alive; } };
    Block* b;
    void release() { if (b->refs.fetch_sub(1, std::memory_order_acq_rel) == 1) delete b; }
public:
    static std::atomic<long> alive, detaches;
    explicit CowString(std::string s) : b(new Block(std::move(s))) {}
    CowString(const CowString& o) : b(o.b) { b->refs.fetch_add(1, std::memory_order_relaxed); }       // 복사는 포인터 공유 O(1)
    CowString& operator=(const CowString& o) { if (this != &o) { o.b->refs.fetch_add(1, std::memory_order_relaxed); release(); b = o.b; } return *this; }
    ~CowString() { release(); }
    const std::string& str() const { return b->data; }
    long owners() const { return b->refs.load(std::memory_order_acquire); }
    void set(size_t i, char c) {
        if (b->refs.load(std::memory_order_acquire) > 1) { Block* nb = new Block(b->data); ++detaches; release(); b = nb; }      // 공유 중이면 쓰기 직전에 분리(detach)
        b->data[i] = c;
    }
};
std::atomic<long> CowString::alive{0};
std::atomic<long> CowString::detaches{0};

int main() {
    {   CowString a("hello"); CowString b = a;
        assert(a.owners() == 2 && &a.str() == &b.str());                       // 복사 후에도 같은 버퍼 공유
        b.set(0, 'J'); assert(a.str() == "hello" && b.str() == "Jello" && a.owners() == 1 && b.owners() == 1 && &a.str() != &b.str()); }
    assert(CowString::alive == 0);
    // ① 모형과 대조
    {   std::mt19937 rng(41); CowString::detaches = 0; std::vector<CowString> handles; std::vector<std::string> model; std::vector<int> group; int nextGroup = 0; long expectedDetaches = 0, writes = 0, shared = 0;
        auto groupSize = [&](int g) { return (long)std::count(group.begin(), group.end(), g); };
        handles.emplace_back(std::string("abcdefgh")); model.push_back("abcdefgh"); group.push_back(nextGroup++);
        for (int step = 0; step < 20000; ++step) {
            int op = (int)(rng() % 100); size_t i = rng() % handles.size();
            if (op < 22 && handles.size() < 40) { handles.push_back(handles[i]); model.push_back(model[i]); group.push_back(group[i]); }              // 복사
            else if (op < 30 && handles.size() > 1) { size_t j = rng() % handles.size(); handles[i] = handles[j]; model[i] = model[j]; group[i] = group[j]; }  // 대입
            else if (op < 70) { size_t pos = rng() % model[i].size(); char c = (char)('A' + rng() % 26); if (groupSize(group[i]) > 1) { ++expectedDetaches; group[i] = nextGroup++; ++shared; } handles[i].set(pos, c); model[i][pos] = c; ++writes; }   // 쓰기
            else if (op < 78 && handles.size() > 1) { handles.erase(handles.begin() + (long)i); model.erase(model.begin() + (long)i); group.erase(group.begin() + (long)i); }              // 소멸
            else { assert(handles[i].str() == model[i]); }                                                                                                                                 // 읽기
            if (step % 25 == 0) {
                std::set<int> groups(group.begin(), group.end());
                for (size_t k = 0; k < handles.size(); ++k) { assert(handles[k].str() == model[k] && handles[k].owners() == groupSize(group[k])); }
                assert(CowString::alive == (long)groups.size() && CowString::detaches == expectedDetaches);
            }
        }
        assert(shared > 300 && writes > 5000); }
    assert(CowString::alive == 0);                                                                              // 모든 핸들이 사라지면 블록도 없다
    // ② 스레드 8 개
    {   CowString::detaches = 0; const int T = 8; CowString base(std::string(64, 'o')); std::vector<CowString> copies(T, base); std::vector<std::string> results(T); std::vector<std::thread> ts;
        for (int t = 0; t < T; ++t) ts.emplace_back([&, t] { std::mt19937 r(t); std::string mine(64, 'o'); for (int i = 0; i < 2000; ++i) { size_t pos = r() % 64; char c = (char)('a' + r() % 26); copies[t].set(pos, c); mine[pos] = c; } results[t] = mine; });
        for (auto& th : ts) th.join();
        assert(CowString::detaches == T && base.str() == std::string(64, 'o') && base.owners() == 1);           // 원본 핸들이 살아 있어서 첫 쓰기마다 정확히 한 번씩 분리
        for (int t = 0; t < T; ++t) { assert(copies[t].str() == results[t] && copies[t].owners() == 1); } }
    assert(CowString::alive == 0);
#if defined(__unix__) || defined(__APPLE__)
    // ③ 진짜 fork (스레드가 모두 끝난 뒤)
    {   const long ps = sysconf(_SC_PAGESIZE); const int PAGES = 64;
        char* priv = (char*)mmap(nullptr, PAGES * ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); char* shr = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        assert(priv != MAP_FAILED && shr != MAP_FAILED); for (int i = 0; i < PAGES; ++i) priv[i * ps] = 100; shr[0] = 1;
        int toChild[2], fromChild[2]; assert(pipe(toChild) == 0 && pipe(fromChild) == 0);
        pid_t pid = fork();
        if (pid == 0) {                                                                                         // 자식
            struct rusage r0, r1, r2; getrusage(RUSAGE_SELF, &r0); long sum = 0; for (int i = 0; i < PAGES; ++i) sum += priv[i * ps]; getrusage(RUSAGE_SELF, &r1);       // 읽기: 페이지를 공유
            for (int i = 0; i < PAGES; ++i) { priv[i * ps] = 7; }
            getrusage(RUSAGE_SELF, &r2);                                                                                  // 쓰기: 페이지마다 복제
            long readFaults = r1.ru_minflt - r0.ru_minflt, writeFaults = r2.ru_minflt - r1.ru_minflt; (void)sum;
            char go; (void)!read(toChild[0], &go, 1);                                                           // 부모가 자기 쓰기를 마칠 때까지 기다린다
            long report[4] = {priv[0], shr[0], readFaults, writeFaults}; (void)!write(fromChild[1], report, sizeof report); _exit(0);
        }
        priv[0] = 55; shr[0] = 2;                                                                               // 부모가 자식의 쓰기 뒤에 쓴다 (자식이 읽기 전에)
        char go = 1; (void)!write(toChild[1], &go, 1);
        long report[4]; assert(read(fromChild[0], report, sizeof report) == (ssize_t)sizeof report); int status; waitpid(pid, &status, 0);
        assert(report[0] == 7 && priv[0] == 55);                                                                // 비공개 매핑: 서로 상대의 쓰기가 안 보인다 (자식 7, 부모 55)
        assert(report[1] == 2 && shr[0] == 2);                                                                  // 공유 매핑: 부모의 쓰기가 자식에게도 보인다
        assert(report[3] >= PAGES && report[2] < PAGES / 2);                                                    // 쓰기는 페이지마다 CoW 폴트, 읽기는 거의 폴트 없음
        munmap(priv, PAGES * ps); munmap(shr, ps); close(toChild[0]); close(toChild[1]); close(fromChild[0]); close(fromChild[1]);
        std::cout << "CopyOnWrite verified: user-space CoW matched the value-semantics model (" << CowString::detaches << " detaches in the last phase), kernel CoW faulted " << report[3] << " times for " << PAGES << " written pages vs " << report[2] << " for reads." << std::endl; }
#else
    std::cout << "CopyOnWrite verified (user-space part)." << std::endl;
#endif
    return 0;
}
// Time Complexity: 복사 O(1), 첫 쓰기 O(크기)
// Space Complexity: 쓰기가 일어나기 전까지 공유
```
## ZeroCopy()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <string_view>
#include <thread>
#include <vector>
#if defined(__linux__)
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/sendfile.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/uio.h>
#include <unistd.h>
#endif

// 제로 카피: 데이터를 사용자 공간 버퍼로 옮기지 않고 커널 안에서 파일 -> 소켓/파일로 직접 전달한다.
//  read+write: 디스크 -> 커널 버퍼 -> (복사) 사용자 버퍼 -> (복사) 커널 버퍼 -> 목적지 : 사용자 공간 복사 2번, 문맥 전환 4번
//  sendfile  : 디스크 -> 커널 버퍼 -> 목적지                                          : 사용자 공간 복사 0번 (웹 서버가 정적 파일을 보내는 방식)
// 같은 아이디어를 사용자 공간에서도 쓴다: string_view 로 부분 문자열을 복사 없이 가리킨다
// 이 예제는 방법별로 (1) 결과가 같은지(체크섬) (2) 사용자 공간을 거친 바이트 수 (3) 시스템 호출 수를 센다:
//  read/write 루프, mmap + write, sendfile(파일 -> 파일, 파일 -> 소켓), copy_file_range, splice(파일 -> 파이프 -> 파일); 이어서 writev(머리 + 본문을 이어 붙이지 않고 보내기) 와 string_view 토크나이저(복사 없음)
uint64_t fnv(const std::string& s) { uint64_t h = 1469598103934665603ULL; for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; } return h; }
std::string slurp(const std::string& p) { std::ifstream f(p, std::ios::binary); std::ostringstream ss; ss << f.rdbuf(); return ss.str(); }
std::vector<std::string_view> splitViews(std::string_view s, char sep) { std::vector<std::string_view> v; size_t i = 0; while (i <= s.size()) { size_t j = s.find(sep, i); if (j == std::string_view::npos) j = s.size(); v.push_back(s.substr(i, j - i)); i = j + 1; } return v; }
std::vector<std::string> splitCopies(const std::string& s, char sep) { std::vector<std::string> v; size_t i = 0; while (i <= s.size()) { size_t j = s.find(sep, i); if (j == std::string::npos) j = s.size(); v.push_back(s.substr(i, j - i)); i = j + 1; } return v; }

int main() {
    std::string src = "/tmp/ds_zc_src.bin"; std::string payload(300000, 'x'); for (size_t i = 0; i < payload.size(); i += 97) payload[i] = char('a' + i % 26);
    { std::ofstream f(src, std::ios::binary); f << payload; }
#if defined(__linux__)
    const size_t N = payload.size(); const uint64_t want = fnv(payload); const size_t BUF = 16384; struct Stat { long userBytes = 0, calls = 0; }; Stat st[6]; const char* dst[6] = {"/tmp/ds_zc_d0", "/tmp/ds_zc_d1", "/tmp/ds_zc_d2", "/tmp/ds_zc_d3", "/tmp/ds_zc_d4", "/tmp/ds_zc_d5"};
    auto openIn = [&] { return open(src.c_str(), O_RDONLY); }; auto openOut = [&](const char* p) { return open(p, O_WRONLY | O_CREAT | O_TRUNC, 0644); };
    {   int in = openIn(), out = openOut(dst[0]); std::vector<char> buf(BUF); ssize_t n;                                       // 0: read + write 루프
        while ((n = read(in, buf.data(), buf.size())) > 0) { ++st[0].calls; st[0].userBytes += n; (void)!write(out, buf.data(), (size_t)n); ++st[0].calls; } ++st[0].calls; close(in); close(out); }
    {   int in = openIn(), out = openOut(dst[1]); void* m = mmap(nullptr, N, PROT_READ, MAP_PRIVATE, in, 0); assert(m != MAP_FAILED);                      // 1: mmap + write (사용자 공간에 복사하지 않는다)
        size_t off = 0; while (off < N) { ssize_t n = write(out, (char*)m + off, N - off); ++st[1].calls; assert(n > 0); off += (size_t)n; } munmap(m, N); close(in); close(out); }
    {   int in = openIn(), out = openOut(dst[2]); off_t off = 0; while ((size_t)off < N) { ssize_t n = sendfile(out, in, &off, N - (size_t)off); ++st[2].calls; if (n <= 0) break; } close(in); close(out); }   // 2: sendfile (파일 -> 파일)
    {   int in = openIn(), out = openOut(dst[3]); size_t left = N; while (left > 0) { ssize_t n = copy_file_range(in, nullptr, out, nullptr, left, 0); ++st[3].calls; if (n <= 0) break; left -= (size_t)n; } close(in); close(out); }   // 3: copy_file_range
    {   int in = openIn(), out = openOut(dst[4]); int p[2]; assert(pipe(p) == 0); size_t done = 0;                                                      // 4: splice (파일 -> 파이프 -> 파일)
        while (done < N) { ssize_t a = splice(in, nullptr, p[1], nullptr, std::min<size_t>(N - done, 65536), 0); ++st[4].calls; assert(a > 0); ssize_t left = a; while (left > 0) { ssize_t b = splice(p[0], nullptr, out, nullptr, (size_t)left, 0); ++st[4].calls; assert(b > 0); left -= b; } done += (size_t)a; }
        close(p[0]); close(p[1]); close(in); close(out); }
    {   int sv[2]; assert(socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == 0); std::string got; got.reserve(N);                                              // 5: sendfile (파일 -> 소켓), 다른 스레드가 받는다
        std::thread reader([&] { char b[8192]; ssize_t n; while ((n = recv(sv[1], b, sizeof b, 0)) > 0) got.append(b, (size_t)n); });
        int in = openIn(); off_t off = 0; while ((size_t)off < N) { ssize_t n = sendfile(sv[0], in, &off, N - (size_t)off); ++st[5].calls; if (n <= 0) break; } close(in); shutdown(sv[0], SHUT_WR); reader.join();
        assert(got.size() == N && fnv(got) == want); close(sv[0]); close(sv[1]); }
    for (int i = 0; i < 5; ++i) { assert(fnv(slurp(dst[i])) == want); }                                                                              // 모든 방법의 결과가 같다
    assert(st[0].userBytes == (long)N && st[0].calls == 2 * (long)((N + BUF - 1) / BUF) + 1);                                                          // read/write: 사용자 버퍼를 거친 바이트 N, 호출 2·ceil(N/16K)+1
    assert(st[1].userBytes == 0 && st[2].userBytes == 0 && st[3].userBytes == 0 && st[4].userBytes == 0 && st[5].userBytes == 0);                      // 나머지: 사용자 공간 복사 0
    assert(st[2].calls <= 3 && st[3].calls <= 3 && st[5].calls <= 3 && st[0].calls > 30);                                                              // 시스템 호출 수도 크게 줄어든다
    for (int i = 0; i < 5; ++i) std::remove(dst[i]);
    // writev: 머리와 본문을 이어 붙이지 않고 한 번에
    {   std::string head = "HTTP/1.1 200 OK\r\nContent-Length: 300000\r\n\r\n"; int fd = open("/tmp/ds_zc_wv", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        struct iovec iov[2] = {{(void*)head.data(), head.size()}, {(void*)payload.data(), payload.size()}}; ssize_t n = writev(fd, iov, 2); close(fd); assert(n == (ssize_t)(head.size() + payload.size()));
        std::string joined = head + payload; long concatCopies = (long)joined.size();                                                                   // 이어 붙이는 쪽은 사용자 공간 복사 head + body 바이트
        assert(slurp("/tmp/ds_zc_wv") == joined && concatCopies == (long)(head.size() + payload.size())); std::remove("/tmp/ds_zc_wv"); }
    std::cout << "ZeroCopy verified: 6 transfer methods produced identical bytes; read/write used " << st[0].calls << " syscalls and " << st[0].userBytes << " user-space bytes, sendfile used " << st[2].calls << " call(s) and 0." << std::endl;
#endif
    std::remove(src.c_str());
    // 사용자 공간 제로 카피: string_view
    std::string line = "key=value;other=thing;third=3"; std::string_view v(line); auto parts = splitViews(v, ';'); auto copies = splitCopies(line, ';');
    assert(parts.size() == 3 && copies.size() == 3);
    for (size_t i = 0; i < parts.size(); ++i) {
        assert(parts[i] == copies[i] && parts[i].data() >= line.data() && parts[i].data() + parts[i].size() <= line.data() + line.size());                // 보기는 원래 버퍼 안을 가리킨다
        assert(copies[i].data() < line.data() || copies[i].data() >= line.data() + line.size() || copies[i].empty());                                 // 복사본은 따로 할당된 메모리 (짧은 문자열 최적화로 객체 안에 있어도 line 버퍼 밖)
    }
    line[0] = 'K'; assert(parts[0] == "Key=value" && copies[0] == "key=value");                                                                      // 원본이 바뀌면 보기에는 보이고 복사본에는 안 보인다 (보기의 수명 위험)
    std::mt19937 rng(8); std::string big; for (int i = 0; i < 2000; ++i) { big += std::to_string(rng() % 1000); big += (i % 7 == 0 ? ';' : ','); }
    auto va = splitViews(big, ','); auto vb = splitCopies(big, ','); assert(va.size() == vb.size());
    for (size_t i = 0; i < va.size(); ++i) { assert(va[i] == vb[i]); }   // 둘이 같은 토큰열
    std::cout << "ZeroCopy verified (user-space views): " << va.size() << " tokens identical to the copying tokenizer, all views point into the original buffer." << std::endl;
    return 0;
}
// Time Complexity: O(n) 이동, 사용자 공간 복사 0
// Space Complexity: O(1) 사용자 버퍼
```
# Part 14. 운영체제
## ProcessMemory()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#if defined(__linux__)
#include <sys/mman.h>
#include <unistd.h>
#endif

// 프로세스 메모리 지도: 리눅스의 /proc/self/maps 는 프로세스의 가상 주소 영역(VMA)을 한 줄씩 보여 준다.
//   시작-끝  권한(rwxp)  오프셋  장치  inode  경로      예) 55d0c8a00000-55d0c8a21000 r-xp ... /path/a.out   ...  [heap]   ...  [stack]
// 코드는 r-xp, 읽기 전용 데이터는 r--p, 전역 변수는 rw-p, 스택은 [stack].  자기 변수의 주소가 어느 영역에 속하는지 확인할 수 있다
// 이 예제는 지도를 읽는 것에 그치지 않고, 메모리 시스템 호출이 지도를 바꾸는 방식을 확인한다:
//  ① 지도 불변식: 시작 < 끝, 주소 오름차순, 겹치지 않음, 권한 4 글자  ② mmap 한 8 페이지가 지도에 나타남(rw-p), 가운데 한 페이지를 mprotect(PROT_NONE) 하면 영역이 정확히 3 개로 쪼개지고(+2) 가운데만 ---p,
//  munmap 하면 사라짐  ③ mincore: 만진 페이지만 상주(resident)  ④ 가상 크기는 mmap 즉시 늘지만 상주 크기(VmRSS)는 만져야 는다  ⑤ sbrk 가 [heap] 의 끝(brk)을 움직임  ⑥ 스택은 깊이 들어가면 아래로 자란다
struct Region { uint64_t start, end; std::string perms, name; };
std::vector<Region> readMaps() {
    std::ifstream f("/proc/self/maps"); std::vector<Region> out; std::string line;
    while (std::getline(f, line)) {
        std::istringstream ss(line); std::string range, perms, off, dev, inode, name;
        ss >> range >> perms >> off >> dev >> inode; std::getline(ss, name);
        size_t dash = range.find('-'); size_t b = name.find_first_not_of(' ');
        out.push_back({std::stoull(range.substr(0, dash), nullptr, 16), std::stoull(range.substr(dash + 1), nullptr, 16), perms, b == std::string::npos ? "" : name.substr(b)});
    }
    return out;
}
const Region* find(const std::vector<Region>& maps, const void* p) { uint64_t a = (uint64_t)p; for (auto& r : maps) if (a >= r.start && a < r.end) return &r; return nullptr; }
long statusKb(const char* key) { std::ifstream f("/proc/self/status"); std::string line; size_t n = std::strlen(key); while (std::getline(f, line)) { if (line.compare(0, n, key) == 0) return std::stol(line.substr(n + 1)); } return -1; }
int global = 5;
void code() {}
uint64_t deepestAddress = 0; uint64_t stackStartBefore = 0, stackStartDeep = 0;
void recurse(int depth) {
    volatile char frame[64 * 1024]; frame[0] = (char)depth; frame[sizeof frame - 1] = 1;                // 페이지를 실제로 만지는 큰 스택 프레임
    if (depth > 0) recurse(depth - 1);
    else { deepestAddress = (uint64_t)&frame[0]; auto maps = readMaps(); const Region* s = find(maps, (const void*)deepestAddress); assert(s && s->name == "[stack]"); stackStartDeep = s->start; }
}

int main() {
#if defined(__linux__)
    auto maps = readMaps(); assert(!maps.empty());
    for (size_t i = 0; i < maps.size(); ++i) { assert(maps[i].start < maps[i].end && maps[i].perms.size() == 4); if (i) assert(maps[i - 1].end <= maps[i].start); }          // ① 지도 불변식
    int local = 0; int* heap = new int(1);
    const Region *stack = find(maps, &local), *text = find(maps, (void*)&code), *data = find(maps, &global), *hp = find(maps, heap);
    assert(stack && stack->name == "[stack]" && stack->perms[0] == 'r' && stack->perms[1] == 'w' && stack->perms[2] == '-');   // 스택: 읽기+쓰기, 실행 불가
    assert(text && text->perms[2] == 'x' && text->perms[1] == '-');                   // 코드: 실행 가능, 쓰기 불가 (W^X)
    assert(data && data->perms[1] == 'w' && data->perms[2] == '-');                   // 전역 변수: 쓰기 가능, 실행 불가
    assert(hp && hp->perms[1] == 'w');                                                // 힙(brk 또는 mmap 영역)
    stackStartBefore = stack->start;
    const std::string stackName = stack->name, textPerms = text->perms, dataPerms = data->perms, heapName = hp->name.empty() ? "[anon]" : hp->name;       // maps 를 다시 읽으면 위 포인터들이 무효가 되므로 필요한 값은 미리 복사
    const long ps = sysconf(_SC_PAGESIZE); const int NP = 8;
    // ② mmap -> mprotect 로 쪼개기 -> munmap
    char* p = (char*)mmap(nullptr, NP * ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(p != MAP_FAILED);
    maps = readMaps(); const Region* r = find(maps, p); assert(r && r->start <= (uint64_t)p && r->end >= (uint64_t)p + NP * ps && r->perms == "rw-p"); size_t countBefore = maps.size();
    assert(mprotect(p + 3 * ps, ps, PROT_NONE) == 0);
    maps = readMaps(); assert(maps.size() == countBefore + 2);                                                          // 영역이 3 개로 쪼개졌다
    const Region *a = find(maps, p + 2 * ps), *mid = find(maps, p + 3 * ps), *c = find(maps, p + 4 * ps);
    assert(a != mid && mid != c && a->perms == "rw-p" && mid->perms == "---p" && c->perms == "rw-p" && mid->start == (uint64_t)p + 3 * ps && mid->end == (uint64_t)p + 4 * ps);   // 가운데 한 페이지만 접근 금지
    assert(munmap(p, NP * ps) == 0); maps = readMaps(); assert(find(maps, p) == nullptr && maps.size() <= countBefore - 1 + 1);
    // ③ mincore: 만진 페이지만 상주
    {   const int M = 16; char* q = (char*)mmap(nullptr, M * ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(q != MAP_FAILED);
        int touched[] = {0, 2, 3, 7, 12}; for (int t : touched) q[t * ps] = 1;
        unsigned char vec[M]; assert(mincore(q, M * ps, vec) == 0);
        for (int i = 0; i < M; ++i) { bool want = std::find(std::begin(touched), std::end(touched), i) != std::end(touched); assert(((vec[i] & 1) != 0) == want); }
        munmap(q, M * ps); }
    // ④ 가상 크기 vs 상주 크기
    {   long vm0 = statusKb("VmSize:"), rss0 = statusKb("VmRSS:"); const size_t BIG = 64u << 20;
        char* big = (char*)mmap(nullptr, BIG, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0); assert(big != MAP_FAILED);
        long vm1 = statusKb("VmSize:"), rss1 = statusKb("VmRSS:"); assert(vm1 - vm0 >= (long)(BIG >> 10) - 64 && rss1 - rss0 < 8 * 1024);                       // 만지기 전: 가상 크기만 +64MB
        for (size_t i = 0; i < BIG; i += (size_t)ps) big[i] = 1;
        long rss2 = statusKb("VmRSS:"); assert(rss2 - rss1 >= (long)(BIG >> 10) - 2048); munmap(big, BIG); }                                                         // 만진 뒤: 상주 크기 +64MB
    // ⑤ sbrk
    {   void* b0 = sbrk(0); void* old = sbrk((intptr_t)ps); if (old != (void*)-1) { void* b1 = sbrk(0); assert((uint64_t)b1 >= (uint64_t)old + (uint64_t)ps); maps = readMaps(); bool inHeap = false; for (auto& rg : maps) { if (rg.name == "[heap]" && rg.end >= (uint64_t)b1) inHeap = true; } assert(inHeap); sbrk(-(intptr_t)ps); } (void)b0; }
    // ⑥ 스택은 깊이 들어가면 아래로 자란다
    recurse(12); assert(stackStartDeep < stackStartBefore && stackStartBefore - stackStartDeep >= 12 * 64 * 1024 / 2);
    std::cout << "ProcessMemory verified: stack=" << stackName << " text perms=" << textPerms << " data perms=" << dataPerms << " heap region=" << heapName
              << "; mprotect split a VMA in 3, mincore matched touched pages, stack grew " << (stackStartBefore - stackStartDeep) / 1024 << " KB." << std::endl;
    delete heap;
#else
    std::cout << "ProcessMemory: Linux-only demonstration (/proc/self/maps)" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(영역 수)
// Space Complexity: O(영역 수)
// audit: no-sanitize (/proc/self/maps 의 스택 영역 권한 표시가 새니타이저에서 다르다)
```
## ThreadLocalStorage()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <mutex>
#include <random>
#include <set>
#include <thread>
#include <vector>

// 스레드 지역 저장소(TLS): thread_local 변수는 스레드마다 별도의 복사본이 있다 -> 락 없이 스레드별 상태(errno, 난수 생성기 상태, 캐시)를 유지한다.
// 스레드가 시작할 때 초기화되고 끝날 때 소멸자가 불린다.  공유 변수와 달리 경쟁 상태가 없다
// 이 예제는 의미를 확인하고, TLS 위에 pthread_key 같은 "동적 키" 계층을 직접 만들어 본다(키 생성 시 소멸자 등록, 스레드가 끝날 때 값이 있는 키마다 소멸자 한 번):
//  ① 기본 의미(스레드별 사본·초기값·주소·소멸자 호출 횟수)  ② 함수 안의 thread_local 은 스레드마다 정확히 한 번 초기화  ③ TlsRegistry 를 네이티브 thread_local 과 비교: 스레드 8 개가 무작위 set/get 4 000 번,
//  스레드별 모형(std::map)과 항상 일치하고, 끝날 때 소멸자 호출 수 == 값이 남아 있던 (스레드, 키) 쌍의 수, 누수 없음  ④ 샤딩된 카운터: 스레드별 조각을 락 없이 늘리고 스레드가 끝날 때 전역 합계에 합침 — 총합이 정확하고
//  원자 카운터·뮤텍스 카운터와 같음  ⑤ 스레드마다 시드가 고정된 난수열은 스케줄과 무관하게 재현 가능  ⑥ 스레드 풀의 작업은 같은 워커의 thread_local 상태를 이어받는다(상태 누수의 원인): 워커별로 본 값이 정확히 1, 2, 3 ... 연속
thread_local int counter = 100;
std::mutex mu; std::set<const void*> addresses; int ctors = 0, dtors = 0;
struct PerThread { PerThread() { std::lock_guard<std::mutex> g(mu); ctors++; } ~PerThread() { std::lock_guard<std::mutex> g(mu); dtors++; } };
thread_local PerThread tls;
struct alignas(64) Padded { char c[64]; };
thread_local Padded padded;

// pthread_key 와 같은 동적 키 계층
class TlsRegistry {
    struct Slots { std::vector<void*> v; ~Slots(); };
    std::mutex m; std::vector<void (*)(void*)> dtorOf; std::vector<char> live;
    static Slots& slots() { thread_local Slots s; return s; }
public:
    std::atomic<long> destructorRuns{0};
    int create(void (*dtor)(void*)) { std::lock_guard<std::mutex> g(m); dtorOf.push_back(dtor); live.push_back(1); return (int)dtorOf.size() - 1; }
    void remove(int key) { std::lock_guard<std::mutex> g(m); live[(size_t)key] = 0; }                        // 키를 지운 뒤에는 소멸자도 호출되지 않는다 (pthread_key_delete 와 같다)
    void* get(int key) { auto& v = slots().v; return (size_t)key < v.size() ? v[(size_t)key] : nullptr; }
    void set(int key, void* p) { auto& v = slots().v; if ((size_t)key >= v.size()) v.resize((size_t)key + 1, nullptr); v[(size_t)key] = p; }
    void runDestructors(std::vector<void*>& v) {                                                            // 스레드 종료 시: 값이 있는 키마다 소멸자 (소멸자가 새 값을 넣으면 최대 4 번 반복)
        for (int round = 0; round < 4; ++round) {
            bool any = false;
            for (size_t k = 0; k < v.size(); ++k) {
                void* p = v[k]; if (!p) continue; void (*d)(void*); bool alive; { std::lock_guard<std::mutex> g(m); d = dtorOf[k]; alive = live[k]; }
                v[k] = nullptr; if (alive && d) { d(p); ++destructorRuns; any = true; }
            }
            if (!any) break;
        }
    }
};
TlsRegistry registry;
TlsRegistry::Slots::~Slots() { registry.runDestructors(v); }
std::atomic<long> liveBoxes{0};
struct Box { long v; Box(long x) : v(x) { ++liveBoxes; } ~Box() { --liveBoxes; } };
void boxDtor(void* p) { delete static_cast<Box*>(p); }

// 샤딩된 카운터: 스레드별 조각 + 종료 시 합류
std::atomic<long> shardedTotal{0};
struct Shard { long n = 0; ~Shard() { shardedTotal += n; } };
thread_local Shard shard;
int initCount = 0;
int perThreadInit() { std::lock_guard<std::mutex> g(mu); return ++initCount; }
int callsInThisThread() { thread_local int calls = perThreadInit() * 0; return ++calls; }                    // 처음 호출될 때 스레드마다 한 번 초기화

int main() {
    // ① 기본 의미 (원래 예)
    counter = 1;                                                       // 메인 스레드의 사본만 바뀐다
    {   std::vector<std::thread> th; int results[4];
        for (int t = 0; t < 4; t++) th.emplace_back([&, t] { (void)tls; assert(counter == 100); for (int i = 0; i < 1000; i++) counter++; results[t] = counter; std::lock_guard<std::mutex> g(mu); addresses.insert(&counter); });
        for (auto& x : th) x.join();
        for (int t = 0; t < 4; t++) assert(results[t] == 1100);
        assert(counter == 1 && addresses.size() == 4 && ctors == 4 && dtors == 4); }                          // 메인 값은 그대로, 주소 4 개, 스레드 종료 시 소멸자
    {   std::vector<std::thread> th; std::vector<uintptr_t> pa(4); for (int t = 0; t < 4; ++t) th.emplace_back([&, t] { pa[t] = (uintptr_t)&padded; });
        for (auto& x : th) { x.join(); }
        for (int t = 0; t < 4; ++t) { assert(pa[t] % 64 == 0); }                                                                      // alignas(64) 도 스레드마다 지켜진다
        std::set<uintptr_t> lines; for (auto a : pa) lines.insert(a / 64); (void)lines; }
    // ② 함수 안 thread_local: 스레드마다 정확히 한 번
    {   std::vector<std::thread> th; for (int t = 0; t < 6; ++t) th.emplace_back([] { for (int i = 1; i <= 5; ++i) assert(callsInThisThread() == i); });
        for (auto& x : th) { x.join(); }
        assert(initCount == 6); }
    // ③ 동적 키 계층 vs 모형
    {   const int T = 8, KEYS = 4, OPS = 4000; std::vector<int> keys; for (int k = 0; k < KEYS; ++k) keys.push_back(registry.create(boxDtor));
        std::atomic<long> expectedDtor{0}, mismatches{0}; std::vector<std::thread> th;
        for (int t = 0; t < T; ++t) th.emplace_back([&, t] {
            std::mt19937 rng(1000 + t); std::map<int, Box*> model;
            for (int i = 0; i < OPS; ++i) {
                int k = keys[rng() % KEYS]; int op = (int)(rng() % 3);
                if (op == 0) { Box* b = new Box((long)t * 1000000 + i); Box* old = static_cast<Box*>(registry.get(k)); if (old != model[k]) ++mismatches; delete old; registry.set(k, b); model[k] = b; }   // 덮어쓰기: 옛 값은 호출자가 정리
                else if (op == 1) { if (registry.get(k) != model[k]) ++mismatches; }
                else if (model[k]) { Box* old = static_cast<Box*>(registry.get(k)); if (old != model[k]) ++mismatches; delete old; registry.set(k, nullptr); model[k] = nullptr; }
            }
            long left = 0; for (auto& kv : model) left += kv.second != nullptr; expectedDtor += left;
        });
        for (auto& x : th) x.join();
        assert(mismatches == 0 && registry.destructorRuns == expectedDtor && liveBoxes == 0); }                // 스레드 종료 때 값이 남은 쌍마다 소멸자 한 번, 새는 객체 없음
    // ④ 샤딩된 카운터
    {   const int T = 8; const long N = 200000; std::atomic<long> atomicTotal{0}; long mutexTotal = 0; std::mutex mm; shardedTotal = 0; std::vector<std::thread> th;
        for (int t = 0; t < T; ++t) th.emplace_back([&] { for (long i = 0; i < N; ++i) { ++shard.n; atomicTotal.fetch_add(1, std::memory_order_relaxed); if (i % 100 == 0) { std::lock_guard<std::mutex> g(mm); mutexTotal += 100; } } });
        for (auto& x : th) x.join();
        assert(shardedTotal == T * N && atomicTotal == T * N && mutexTotal == (long)T * (N / 100) * 100); }
    // ⑤ 재현 가능한 스레드별 난수열
    {   auto run = [](int delayPattern) { const int T = 6; std::vector<uint64_t> sums(T); std::vector<std::thread> th;
            for (int t = 0; t < T; ++t) th.emplace_back([&, t] { if ((t + delayPattern) % 3 == 0) std::this_thread::sleep_for(std::chrono::milliseconds(2)); thread_local std::mt19937_64 rng(777 + t); uint64_t s = 0; for (int i = 0; i < 1000; ++i) s += rng(); sums[t] = s; });
            for (auto& x : th) { x.join(); }
            return sums; };
        assert(run(0) == run(1) && run(1) == run(2)); }                                                       // 시작 순서가 달라도 스레드별 결과가 같다
    // ⑥ 스레드 풀: 같은 워커의 thread_local 상태 이어받기
    {   const int W = 4, TASKS = 400; std::mutex qm; std::condition_variable cv; std::deque<int> q; bool done = false; std::vector<std::vector<int>> seenByWorker(W); std::vector<std::thread> workers;
        for (int w = 0; w < W; ++w) workers.emplace_back([&, w] {
            thread_local int tasksSoFar = 0;
            for (;;) { { std::unique_lock<std::mutex> lk(qm); cv.wait(lk, [&] { return !q.empty() || done; }); if (q.empty()) return; q.pop_front(); } seenByWorker[w].push_back(++tasksSoFar); }
        });
        { std::lock_guard<std::mutex> lk(qm); for (int i = 0; i < TASKS; ++i) q.push_back(i); } cv.notify_all();
        { std::unique_lock<std::mutex> lk(qm); while (!q.empty()) { lk.unlock(); std::this_thread::yield(); lk.lock(); } done = true; } cv.notify_all();
        for (auto& x : workers) x.join();
        long total = 0; for (int w = 0; w < W; ++w) { for (size_t i = 0; i < seenByWorker[w].size(); ++i) assert(seenByWorker[w][i] == (int)i + 1); total += (long)seenByWorker[w].size(); }   // 워커마다 1, 2, 3 ... 연속: 상태가 작업 사이에 이어진다
        assert(total == TASKS); }
    std::cout << "ThreadLocalStorage verified: native thread_local, a pthread_key-style registry (" << registry.destructorRuns << " destructor runs, 0 leaks), sharded counters, reproducible per-thread RNG, and worker-state carry-over in a pool." << std::endl;
    return 0;
}
// Time Complexity: 접근 O(1) (세그먼트 레지스터 기준 오프셋; 동적 키는 벡터 색인)
// Space Complexity: 스레드 수 · 변수 크기
```
## KernelMemory()
### 대표코드
```cpp
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#if defined(__linux__)
#include <csignal>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 커널 메모리: x86-64(4 단계 페이징) 에서 가상 주소 공간의 위쪽 절반(0xFFFF8000... 이상)은 커널의 것이다.  사용자 모드 코드는 접근할 수 없고, 접근하려 하면 예외가 난다.
// 시스템 호출에서 사용자가 넘긴 포인터를 커널이 그대로 믿으면 안 되므로 항상 검증한다(access_ok, copy_from_user).  검증 식 `ptr + len <= TASK_SIZE` 는 ptr + len 이 2^64 를 넘어 *되감기면* 거짓 통과한다 → `len <= TASK_SIZE && ptr <= TASK_SIZE - len` 로 써야 한다.
//  ① 검증 함수 3 종 — 순진한 식 / 안전한 식 / 128 비트 오라클 — 을 경계값 위주 200 만 쌍에 대조: 안전한 식은 늘 오라클과 같고, 순진한 식은 오직 "되감김" 때문에 거짓 통과하며 거짓 거부는 없다
//  ② 이 프로세스의 실제 `/proc/self/maps` 의 모든 매핑(레거시 [vsyscall] 제외)이 사용자 영역 안에 있고 스택·힙이 있음  ③ (Linux, 실제 시스템 호출) 파이프에 쓰기: 커널 주소 / null / 되감기는 주소 / 해제된 페이지 / PROT_NONE 페이지는 EFAULT — 프로세스는 죽지 않음
//  ④ 두 페이지에 걸친 버퍼(뒤 페이지가 PROT_NONE): 일반 파일(memfd)은 앞 페이지 몫 10 바이트만 부분 성공하고 그 바이트가 정확히 저장·이어서 경계부터 쓰면 EFAULT, 파이프는 전부 아니면 무(EFAULT 이고 한 바이트도 도착 안 함)  ⑤ /dev/zero 를 커널 주소로 읽기도 EFAULT  ⑥ 같은 커널 주소를 *사용자 모드로 직접* 읽으면 SIGSEGV (자식 프로세스)
// audit: no-sanitize (실제 접근 위반과 잘못된 포인터 시스템 호출 — 새니타이저와 함께 쓰지 않는다)
constexpr uint64_t TASK_SIZE = 0x0000800000000000ULL;
bool userSpace(uint64_t va) { return va < TASK_SIZE; }
bool accessOkNaive(uint64_t p, uint64_t n) { return p + n <= TASK_SIZE; }                                                                                              // 되감기면 틀림
bool accessOk(uint64_t p, uint64_t n) { return n <= TASK_SIZE && p <= TASK_SIZE - n; }                                                                                  // 안전한 식
__extension__ typedef unsigned __int128 u128;                                                                                                                              // -pedantic 에서도 경고 없이 128 비트 정수 사용
bool accessOkOracle(uint64_t p, uint64_t n) { return (u128)p + n <= TASK_SIZE; }                                                                          // 폭을 넓혀 되감김이 없는 기준

int main() {
    assert(userSpace(0x00007fffffffffffULL) && !userSpace(0xffff800000000000ULL) && !userSpace(0xffffffff81000000ULL) && !userSpace(TASK_SIZE));
    {   std::mt19937_64 rng(4242); const uint64_t special[] = {0, 1, 4095, 4096, TASK_SIZE - 16, TASK_SIZE - 1, TASK_SIZE, TASK_SIZE + 1, 0x00007ffffffff000ULL, 0xffff800000000000ULL, 0xffffffff81000000ULL, ~0ULL - 7, ~0ULL, ~0ULL / 2, 1ULL << 63};
        long falseAccept = 0, accepted = 0, rejected = 0, total = 0, disagree = 0;
        auto check = [&](uint64_t p, uint64_t n) { bool want = accessOkOracle(p, n), safe = accessOk(p, n), naive = accessOkNaive(p, n); ++total; if (safe != want) ++disagree; want ? ++accepted : ++rejected;
            if (naive != want) { assert(naive && !want && p + n < p); ++falseAccept; } };                                                                              // 순진한 식의 오류는 항상 "거짓 통과" + 되감김
        for (uint64_t p : special) for (uint64_t n : special) check(p, n);
        for (int i = 0; i < 2000000; ++i) { uint64_t p, n; switch (rng() % 4) { case 0: p = rng(); n = rng(); break; case 1: p = TASK_SIZE - (rng() % 64); n = rng() % 128; break; case 2: p = ~0ULL - (rng() % 4096); n = rng() % 8192; break; default: p = rng() % (1ULL << 20); n = (rng() % 2) ? rng() % TASK_SIZE : TASK_SIZE - (rng() % (1ULL << 20)); }
            check(p, n); }
        assert(disagree == 0 && falseAccept > 1000 && accepted > 1000 && rejected > 1000 && total > 2000000); std::cout << "KernelMemory: access_ok variants agreed on " << total << " ranges; the naive sum accepted " << falseAccept << " wrapping ranges wrongly; "; }
#if defined(__linux__)
    {   std::ifstream maps("/proc/self/maps"); std::string line; int count = 0; uint64_t stackStart = 0, heapStart = 0; bool sawStack = false, sawHeap = false;                                   // ② 실제 지도
        while (std::getline(maps, line)) { uint64_t lo = std::strtoull(line.c_str(), nullptr, 16), hi = std::strtoull(line.c_str() + line.find('-') + 1, nullptr, 16); ++count;
            if (line.find("[vsyscall]") != std::string::npos) { assert(!userSpace(lo)); continue; }                                                                         // 레거시 vsyscall 페이지만 커널 쪽에 있다
            assert(lo < hi && userSpace(lo) && hi <= TASK_SIZE); if (line.find("[stack]") != std::string::npos) { sawStack = true; stackStart = lo; } if (line.find("[heap]") != std::string::npos) { sawHeap = true; heapStart = lo; } }
        assert(count > 5 && sawStack && sawHeap && heapStart < stackStart); int local = 0; assert(userSpace((uint64_t)&local) && userSpace((uint64_t)std::malloc(8))); }
    const size_t ps = (size_t)sysconf(_SC_PAGESIZE); int fds[2]; int rc = pipe(fds); assert(rc == 0); const void* kernelPtr = (const void*)0xffffffff81000000ULL;                                // ③ 시스템 호출에 잘못된 포인터
    auto drain = [&](size_t want) { std::string out(want, '\0'); size_t got = 0; while (got < want) { ssize_t r = read(fds[0], &out[got], want - got); assert(r > 0); got += (size_t)r; } return out; };
    auto expectFault = [&](const void* p, size_t n) { errno = 0; ssize_t r = write(fds[1], p, n); assert(r == -1 && errno == EFAULT); };
    expectFault(kernelPtr, 16); expectFault(nullptr, 16); expectFault((const void*)(~0ULL - 7), 16);                                                                       // 커널 영역 / null / ptr+len 이 2^64 를 넘는 주소
    { char* pg = (char*)mmap(nullptr, 2 * ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); assert(pg != MAP_FAILED); std::memset(pg, 'x', 2 * ps);
      rc = mprotect(pg + ps, ps, PROT_NONE); assert(rc == 0); expectFault(pg + ps, 16);                                                                                          // PROT_NONE 페이지
      int file = (int)syscall(SYS_memfd_create, "kfile", 0); assert(file >= 0); errno = 0; ssize_t part = write(file, pg + ps - 10, 20); assert(part == 10);                                  // ④ 일반 파일: 앞 페이지 몫 10 바이트만 부분 성공
      char got[16] = {0}; assert(pread(file, got, 16, 0) == 10 && std::string(got, 10) == std::string(10, 'x')); errno = 0; assert(write(file, pg + ps, 4) == -1 && errno == EFAULT); close(file);   // 정확히 10 바이트가 저장, 경계부터는 EFAULT
      int fl = fcntl(fds[0], F_GETFL); fcntl(fds[0], F_SETFL, fl | O_NONBLOCK); errno = 0; assert(write(fds[1], pg + ps - 10, 20) == -1 && errno == EFAULT);                          // 파이프는 달라서 전부 아니면 무: EFAULT
      char nothing[8]; errno = 0; assert(read(fds[0], nothing, sizeof nothing) == -1 && errno == EAGAIN); fcntl(fds[0], F_SETFL, fl);                                                        // 한 바이트도 도착하지 않았다
      rc = munmap(pg, 2 * ps); assert(rc == 0); expectFault(pg, 16); }                                                                                                            // 해제된 페이지
    char ok[16]; std::memset(ok, 'k', sizeof ok); assert(write(fds[1], ok, sizeof ok) == (ssize_t)sizeof ok && drain(16) == std::string(16, 'k'));                           // 정상 포인터는 통과
    int zero = open("/dev/zero", O_RDONLY); assert(zero >= 0); errno = 0; ssize_t zr = read(zero, (void*)kernelPtr, 16); assert(zr == -1 && errno == EFAULT);                    // ⑤ 읽기 방향도 거부
    char buf[16]; std::memset(buf, 9, sizeof buf); zr = read(zero, buf, sizeof buf); assert(zr == 16 && buf[0] == 0 && buf[15] == 0); close(zero);
    std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); volatile char c = *(volatile const char*)kernelPtr; (void)c; _exit(0); }                      // ⑥ 직접 접근은 SIGSEGV
    int st = 0; waitpid(pid, &st, 0); assert(WIFSIGNALED(st) && WTERMSIG(st) == SIGSEGV); close(fds[0]); close(fds[1]);
    std::cout << "real syscalls with kernel, null, wrapping, unmapped and PROT_NONE pointers returned EFAULT, a straddling buffer was stored partially in a file (10 bytes) but not at all in a pipe, and a direct user-mode read of a kernel address died with SIGSEGV" << std::endl;
#else
    std::cout << "(Linux-only syscall checks skipped)" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1) 주소 검증
// Space Complexity: O(1)
```
## UserMemory()
### 대표코드
```cpp
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#if defined(__linux__)
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 사용자 메모리: 프로세스가 쓰는 가상 주소 공간.  *가상 크기*(주소 공간 예약)와 *실제 사용량*(RSS, 물리 메모리)은 다르다.  운영체제는 보통 과다 할당(overcommit)을 허용해 예약만 해 두고 실제로 *만질 때* 물리 메모리를 준다.  한도는 getrlimit(RLIMIT_AS / RLIMIT_STACK ...) 로 본다.
//  ① 1 GiB 를 매핑하면 가상 크기가 정확히 1 GiB 만큼(페이지 수 단위) 늘고 RSS 는 거의 안 는다  ② 앞 64 페이지를 하나씩 만지면 RSS 가 정확히 64 페이지(+소량)만 늘고 가상 크기는 그대로  ③ madvise(DONTNEED) 로 돌려주면 RSS 는 줄고 가상 크기는 그대로  ④ munmap 하면 가상 크기도 원위치
//  ⑤ 1 TiB 를 PROT_NONE 으로 예약만 하고 한 페이지만 열어 쓰기: 가상 크기는 1 TiB 늘지만 RSS 는 1 페이지  ⑥ 자식에서 RLIMIT_AS 를 (현재 크기 + 192 MiB) 로 낮추면 64 MiB 매핑은 성공하고 256 MiB 매핑은 ENOMEM
//  ⑦ 지도에서 주소 순서: 코드 < 힙 < mmap 영역 < 스택  ⑧ overcommit 정책(/proc/sys/vm/overcommit_memory)은 0,1,2 중 하나
// audit: no-sanitize (/proc/self/statm 의 가상·상주 크기와 RLIMIT_AS 를 직접 재므로 새니타이저의 섀도 메모리가 결과를 바꾼다)
#if defined(__linux__)
struct Usage { long sizePages, residentPages; };
Usage usage() { std::ifstream f("/proc/self/statm"); Usage u{0, 0}; f >> u.sizePages >> u.residentPages; return u; }
#endif

int main() {
#if defined(__linux__)
    const long ps = sysconf(_SC_PAGESIZE); struct rlimit stack, as; int rc = getrlimit(RLIMIT_STACK, &stack); assert(rc == 0); rc = getrlimit(RLIMIT_AS, &as); assert(rc == 0); assert(stack.rlim_cur > 0 && stack.rlim_cur <= stack.rlim_max);
    const size_t GiB = 1ULL << 30; const long slack = 16; Usage u0 = usage();
    char* p = (char*)mmap(nullptr, GiB, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0); assert(p != MAP_FAILED); madvise(p, GiB, MADV_NOHUGEPAGE);          // ① 매핑만 한 상태
    Usage u1 = usage(); assert(u1.sizePages - u0.sizePages == (long)(GiB / ps) && u1.residentPages - u0.residentPages <= slack);
    for (long i = 0; i < 64; ++i) p[i * ps] = (char)i;                                                                                                                       // ② 만진 페이지만 물리 메모리
    Usage u2 = usage(); assert(u2.sizePages == u1.sizePages && u2.residentPages - u1.residentPages >= 64 && u2.residentPages - u1.residentPages <= 64 + slack);
    rc = madvise(p, 64 * ps, MADV_DONTNEED); assert(rc == 0); Usage u3 = usage(); assert(u3.sizePages == u1.sizePages && u2.residentPages - u3.residentPages >= 64 - slack && u3.residentPages - u1.residentPages <= slack);   // ③ 돌려줘도 주소 공간은 그대로
    for (long i = 0; i < 64; ++i) assert(p[i * ps] == 0);                                                                                                                     // DONTNEED 뒤에는 0 으로 채워진 새 페이지
    rc = munmap(p, GiB); assert(rc == 0); Usage u4 = usage(); assert(u1.sizePages - u4.sizePages == (long)(GiB / ps) && std::labs(u4.sizePages - u0.sizePages) <= slack);          // ④ 반환
    const size_t TiB = 1ULL << 40; void* big = mmap(nullptr, TiB, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0); bool reserved = big != MAP_FAILED;                 // ⑤ 1 TiB 예약
    if (reserved) { Usage b0 = usage(); rc = mprotect(big, (size_t)ps, PROT_READ | PROT_WRITE); assert(rc == 0); ((char*)big)[0] = 1; assert(((char*)big)[0] == 1); Usage b1 = usage();
        assert(b1.sizePages - u4.sizePages >= (long)(TiB / ps) - slack && b1.residentPages - b0.residentPages <= 1 + slack); munmap(big, TiB); }
    Usage base = usage(); const rlim_t limit = (rlim_t)base.sizePages * (rlim_t)ps + (192ULL << 20);                                                                           // ⑥ RLIMIT_AS
    std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { struct rlimit lim = {limit, as.rlim_max}; if (setrlimit(RLIMIT_AS, &lim) != 0) _exit(10);
        void* a = mmap(nullptr, 64ULL << 20, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); if (a == MAP_FAILED) _exit(11);
        errno = 0; void* b = mmap(nullptr, 256ULL << 20, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); if (b != MAP_FAILED) _exit(12); if (errno != ENOMEM) _exit(13); _exit(0); }
    int st = 0; waitpid(pid, &st, 0); assert(WIFEXITED(st) && WEXITSTATUS(st) == 0);
    { std::ifstream maps("/proc/self/maps"); std::string line; uint64_t heapLo = 0, stackLo = 0; while (std::getline(maps, line)) { uint64_t lo = std::strtoull(line.c_str(), nullptr, 16); if (line.find("[heap]") != std::string::npos) heapLo = lo; if (line.find("[stack]") != std::string::npos) stackLo = lo; }
      void* anon = mmap(nullptr, 1 << 20, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0); uint64_t text = (uint64_t)(void*)&usage, mm = (uint64_t)anon;                           // ⑦ 주소 순서
      assert(heapLo != 0 && stackLo != 0 && text < heapLo && heapLo < mm && mm < stackLo); munmap(anon, 1 << 20); }
    { std::ifstream f("/proc/sys/vm/overcommit_memory"); int mode = -1; if (f >> mode) assert(mode >= 0 && mode <= 2); }                                                              // ⑧ overcommit 정책
    std::cout << "UserMemory: a 1 GiB mapping raised the virtual size by exactly " << GiB / ps << " pages but the resident size by at most " << slack << "; touching 64 pages raised RSS by 64 and MADV_DONTNEED gave them back; " << (reserved ? "1 TiB was reserved with one page committed; " : "(1 TiB reservation refused here); ") << "RLIMIT_AS made a 256 MiB mapping fail with ENOMEM" << std::endl;
#else
    std::cout << "UserMemory: Linux-only demonstration" << std::endl;
#endif
    return 0;
}
// Time Complexity: 매핑·해제 O(1), 만진 페이지는 페이지당 O(1) 결함
// Space Complexity: 예약은 무료, 만진 페이지(RSS)만 비용
```
## NUMAMemory()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// NUMA(Non-Uniform Memory Access): 멀티 소켓 서버에서 CPU 마다 가까운 메모리(로컬 노드)가 있고, 다른 소켓의 메모리(원격 노드)는 접근이 느리다.  운영체제의 기본 정책은 first-touch: 페이지를 "처음 만진 스레드가 있는 노드" 에 둔다.  초기화를 한 스레드가 도맡으면 모든 페이지가 한 노드에 몰려 다른 노드의 스레드는 전부 원격 접근을 하고, 그 노드의 메모리 컨트롤러는 모든 요청을 혼자 받는다.
// 페이지 배치 정책 5 가지(직렬 초기화 / first-touch / 인터리브 / 최적 / 최악)를 접근 기록을 한 건씩 흘리는 시뮬레이터로 평가한다: 지연 합 = Σ 횟수 × 거리(스레드 노드, 페이지 노드), 대역폭 압력 = 노드별 처리 요청 수의 최댓값.
//  ① 손으로 계산한 닫힌 형태: 4 노드 링, 스레드당 4 페이지 × 1000 회 — first-touch 160 000 (모든 접근이 로컬), 직렬 초기화 332 000 (노드 0 에 하루 16 000 요청), 인터리브 332 000 이지만 부하가 노드마다 4 000 으로 균등;  공유 배열(모든 스레드가 모든 페이지) 1 328 000 은 직렬/인터리브가 같고 부하만 64 000 대 16 000
//  ② 무작위 토폴로지·기록 300 건에서 시뮬레이터 == (페이지 × 노드) 행렬로 따로 계산한 비용  ③ 배치 최적성: 작은 경우(페이지 5, 노드 3, 243 가지 전수)에서 페이지별 argmin 배치가 전체 최소·argmax 가 전체 최대 — 비용이 페이지별로 분리되기 때문
//  ④ first-touch 의 약점: 한 번 만진 노드와 주 사용 노드가 다르면 손해, 이주(migration)는 절약량이 이주 비용보다 클 때만 이득 — 이 규칙은 모든 부분집합 중 총비용 최소
double rowAverage(const std::vector<int>& row) { double s = 0; for (int x : row) s += x; return s / row.size(); }
typedef std::vector<std::vector<int>> Matrix;
struct Access { int thread, page; long count; };
enum Policy { SERIAL_INIT, FIRST_TOUCH, INTERLEAVE, OPTIMAL, WORST, POLICIES };
struct Outcome { long latency; std::vector<long> nodeLoad; };

std::vector<int> place(Policy pol, int pages, const std::vector<Access>& tr, const std::vector<int>& tnode, const Matrix& d) {
    int nodes = (int)d.size(); std::vector<int> where(pages, -1);
    if (pol == SERIAL_INIT) std::fill(where.begin(), where.end(), tnode[tr.front().thread]);                                             // 첫 스레드가 모두 초기화
    else if (pol == FIRST_TOUCH) { for (auto& a : tr) if (where[a.page] < 0) where[a.page] = tnode[a.thread]; for (auto& w : where) if (w < 0) w = 0; }
    else if (pol == INTERLEAVE) for (int p = 0; p < pages; ++p) where[p] = p % nodes;
    else { std::vector<std::vector<long>> cnt(pages, std::vector<long>(nodes, 0)); for (auto& a : tr) cnt[a.page][tnode[a.thread]] += a.count;
        for (int p = 0; p < pages; ++p) { long best = -1; for (int m = 0; m < nodes; ++m) { long c = 0; for (int n = 0; n < nodes; ++n) c += cnt[p][n] * d[n][m]; if (best < 0 || (pol == OPTIMAL ? c < best : c > best)) { best = c; where[p] = m; } } } }
    return where;
}
Outcome simulate(const std::vector<int>& where, const std::vector<Access>& tr, const std::vector<int>& tnode, const Matrix& d) {
    Outcome o{0, std::vector<long>(d.size(), 0)}; for (auto& a : tr) { int node = where[a.page]; o.latency += a.count * d[tnode[a.thread]][node]; o.nodeLoad[node] += a.count; } return o; }
long matrixCost(const std::vector<int>& where, int pages, const std::vector<Access>& tr, const std::vector<int>& tnode, const Matrix& d) {                    // 독립 오라클: 페이지 × 노드 횟수 행렬
    int nodes = (int)d.size(); std::vector<std::vector<long>> cnt(pages, std::vector<long>(nodes, 0)); for (auto& a : tr) cnt[a.page][tnode[a.thread]] += a.count;
    long total = 0; for (int p = 0; p < pages; ++p) for (int n = 0; n < nodes; ++n) total += cnt[p][n] * d[n][where[p]]; return total; }
long maxOf(const std::vector<long>& v) { return *std::max_element(v.begin(), v.end()); }

int main() {
    Matrix ring = {{10, 21, 21, 31}, {21, 10, 31, 21}, {21, 31, 10, 21}, {31, 21, 21, 10}}; std::vector<int> tnode = {0, 1, 2, 3};
    {   std::vector<Access> own; for (int t = 0; t < 4; ++t) for (int p = 4 * t; p < 4 * t + 4; ++p) own.push_back({t, p, 1000});                                                  // ① 각자 자기 몫
        Outcome ft = simulate(place(FIRST_TOUCH, 16, own, tnode, ring), own, tnode, ring), ser = simulate(place(SERIAL_INIT, 16, own, tnode, ring), own, tnode, ring), il = simulate(place(INTERLEAVE, 16, own, tnode, ring), own, tnode, ring);
        // first-touch 는 스레드 순서대로 만지므로 스레드 t 가 자기 4 페이지를 가진다 → 모든 접근이 로컬
        assert(ft.latency == 16 * 1000 * 10 && maxOf(ft.nodeLoad) == 4000); assert(ser.latency == 4000L * (10 + 21 + 21 + 31) && maxOf(ser.nodeLoad) == 16000 && ser.nodeLoad[0] == 16000);
        assert(il.latency == 1000L * 4 * (10 + 21 + 21 + 31) && maxOf(il.nodeLoad) == 4000 && il.latency == ser.latency);                                                         // 지연은 같고 대역폭 압력만 다르다
        std::vector<Access> shared; for (int t = 0; t < 4; ++t) for (int p = 0; p < 16; ++p) shared.push_back({t, p, 1000});
        Outcome s2 = simulate(place(SERIAL_INIT, 16, shared, tnode, ring), shared, tnode, ring), i2 = simulate(place(INTERLEAVE, 16, shared, tnode, ring), shared, tnode, ring), o2 = simulate(place(OPTIMAL, 16, shared, tnode, ring), shared, tnode, ring);
        assert(s2.latency == 16000L * 83 && i2.latency == 16000L * 83 && maxOf(s2.nodeLoad) == 64000 && maxOf(i2.nodeLoad) == 16000 && o2.latency == 16000L * 83 && rowAverage(ring[0]) == 83 / 4.0); }   // 링은 대칭이라 어느 단일 노드도 같다
    std::mt19937 rng(515);
    for (int trial = 0; trial < 300; ++trial) {                                                                                                                              // ② 시뮬레이터 대 행렬
        int nodes = 2 + (int)(rng() % 5), pages = 8 + (int)(rng() % 57), threads = 1 + (int)(rng() % 8); Matrix d(nodes, std::vector<int>(nodes, 10)); for (int i = 0; i < nodes; ++i) for (int j = i + 1; j < nodes; ++j) d[i][j] = d[j][i] = 11 + (int)(rng() % 30);
        std::vector<int> tn(threads); for (auto& x : tn) x = (int)(rng() % nodes); std::vector<Access> tr; for (int i = 0; i < 200; ++i) tr.push_back({(int)(rng() % threads), (int)(rng() % pages), 1 + (long)(rng() % 100)});
        long cost[POLICIES]; for (int pol = 0; pol < POLICIES; ++pol) { auto w = place((Policy)pol, pages, tr, tn, d); Outcome o = simulate(w, tr, tn, d); cost[pol] = matrixCost(w, pages, tr, tn, d); assert(o.latency == cost[pol]); long total = 0; for (long x : o.nodeLoad) total += x; long all = 0; for (auto& a : tr) all += a.count; assert(total == all); }
        for (int pol = 0; pol < POLICIES; ++pol) assert(cost[OPTIMAL] <= cost[pol] && cost[pol] <= cost[WORST]); }
    for (int trial = 0; trial < 40; ++trial) {                                                                                                                              // ③ 전수 대조
        int nodes = 3, pages = 5; Matrix d(nodes, std::vector<int>(nodes, 10)); for (int i = 0; i < nodes; ++i) for (int j = i + 1; j < nodes; ++j) d[i][j] = d[j][i] = 11 + (int)(rng() % 30);
        std::vector<int> tn = {0, 1, 2, 1}; std::vector<Access> tr; for (int i = 0; i < 30; ++i) tr.push_back({(int)(rng() % 4), (int)(rng() % pages), 1 + (long)(rng() % 50)});
        long mn = -1, mx = -1; for (int code = 0; code < 243; ++code) { std::vector<int> w(pages); int c = code; for (int p = 0; p < pages; ++p) { w[p] = c % 3; c /= 3; } long cost = matrixCost(w, pages, tr, tn, d); if (mn < 0 || cost < mn) mn = cost; if (cost > mx) mx = cost; }
        assert(matrixCost(place(OPTIMAL, pages, tr, tn, d), pages, tr, tn, d) == mn && matrixCost(place(WORST, pages, tr, tn, d), pages, tr, tn, d) == mx); }
    {   const long MIGRATE = 4000; long exampleGap = 0; int wins = 0;                                                                                                        // ④ first-touch 의 약점과 이주 규칙
        for (int trial = 0; trial < 200; ++trial) { int pages = 12; std::vector<int> tn = {0, 1, 2, 3}; std::vector<Access> tr; for (int p = 0; p < pages; ++p) tr.push_back({(int)(rng() % 4), p, 1});   // 처음 만진 스레드는 무작위, 이후 주 사용자는 따로
            std::vector<int> mainUser(pages); for (int p = 0; p < pages; ++p) { mainUser[p] = (int)(rng() % 4); tr.push_back({mainUser[p], p, (long)(rng() % 600)}); }
            auto first = place(FIRST_TOUCH, pages, tr, tn, ring), best = place(OPTIMAL, pages, tr, tn, ring); long noMigrate = matrixCost(first, pages, tr, tn, ring); long naive = matrixCost(best, pages, tr, tn, ring), naiveMoves = 0, smart = 0, smartMoves = 0;
            for (int p = 0; p < pages; ++p) if (first[p] != best[p]) ++naiveMoves;
            std::vector<int> chosen = first; for (int p = 0; p < pages; ++p) { std::vector<Access> one; for (auto& a : tr) if (a.page == p) one.push_back(a); std::vector<int> w1(pages, first[p]), w2(pages, best[p]); long keep = matrixCost(w1, pages, one, tn, ring), move = matrixCost(w2, pages, one, tn, ring); if (keep - move > MIGRATE) { chosen[p] = best[p]; ++smartMoves; } }
            smart = matrixCost(chosen, pages, tr, tn, ring) + MIGRATE * smartMoves; naive += MIGRATE * naiveMoves;
            assert(smart <= noMigrate && smart <= naive); if (smart < noMigrate) ++wins; exampleGap = std::max(exampleGap, noMigrate - matrixCost(best, pages, tr, tn, ring)); }
        assert(wins > 100 && exampleGap > 0); }                                                                                                                              // 이주는 대부분의 경우 이득이고, 무조건 이주도 never-migrate 도 아닌 규칙이 가장 싸다
    std::cout << "NUMA cost: closed-form placement costs (first-touch 160000, serial/interleave 332000 with load 16000 vs 4000) matched the simulator; 300 random topologies agreed with the matrix oracle; argmin placement equalled the minimum of all 243 placements; the break-even migration rule never lost to never- or always-migrate" << std::endl;
    return 0;
}
// Time Complexity: O(접근 기록 + 페이지 × 노드²)
// Space Complexity: O(페이지 × 노드)
```
# Part 15. 현대 시스템
## GPUMemory()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// GPU 메모리: 32 스레드(워프)가 한 명령을 동시에 실행한다.
//  전역 메모리 병합(coalescing): 워프의 접근이 연속된 128바이트 구간에 모이면 메모리 트랜잭션이 1번, 흩어지면 구간 수만큼 늘어난다.
//  공유 메모리 뱅크 충돌: 32개 뱅크(4바이트 단위 주소 % 32) 중 같은 뱅크의 서로 다른 주소를 여러 스레드가 동시에 접근하면 직렬화된다(같은 주소는 방송이라 충돌이 아니다).
// 이 예제는 두 규칙을 임의의 접근 패턴에 대해 계산하는 함수로 만들고 알려진 닫힌 형태와 맞춘다:
//  ① 간격 s 로 float 을 읽을 때 트랜잭션 수 == min(s, 32), 기준 주소가 128B 에 정렬되지 않으면 간격 1 이 2 트랜잭션  ② AoS(구조체 12B/16B 배열) 에서 한 필드만 읽으면 3/4 트랜잭션, SoA 는 1, float4 로 구조체 전체를 읽으면 4
//  ③ 뱅크 충돌 정도 == gcd(간격, 32), 같은 단어를 모두가 읽으면(방송) 1  ④ 32x32 타일 열 접근: 폭 32 면 32 방향 충돌, 폭 33 이면 없음 — 패딩 한 칸
//  ⑤ 행렬 전치의 전역 메모리 트랜잭션: 단순 전치 (N²/32)·(1 + 32) 대 공유 메모리 타일 (N²/32)·2 — 시뮬레이션이 닫힌 형태와 같고 16.5 배 차이, 결과 행렬도 같다
//  ⑥ 병렬 합: 인터리브 주소 지정(thread t 가 2·s·t 를 읽음)은 단계마다 충돌이 커지고, 순차 주소 지정(t 와 t+s)은 충돌이 없다 — 두 방식의 합계가 같고 직렬화 횟수 비교
const int WARP = 32;
int transactions(const std::vector<uint64_t>& byteAddr, unsigned width, unsigned segment = 128) {     // 워프의 접근이 건드리는 서로 다른 구간 수
    std::set<uint64_t> segs; for (uint64_t a : byteAddr) for (unsigned b = 0; b < width; ++b) segs.insert((a + b) / segment); return (int)segs.size();
}
int bankConflictDegree(const std::vector<uint32_t>& wordAddr) {                                      // 같은 뱅크의 서로 다른 단어 수의 최댓값 (같은 단어는 방송)
    std::vector<std::set<uint32_t>> perBank(32); for (uint32_t w : wordAddr) perBank[w % 32].insert(w); size_t mx = 0; for (auto& s : perBank) mx = std::max(mx, s.size()); return (int)mx;
}
int stridedTransactions(int stride, int baseOffsetFloats = 0) { std::vector<uint64_t> a; for (int t = 0; t < WARP; ++t) a.push_back(((uint64_t)baseOffsetFloats + (uint64_t)t * stride) * 4); return transactions(a, 4); }
int stridedConflict(int stride) { std::vector<uint32_t> w; for (int t = 0; t < WARP; ++t) w.push_back((uint32_t)(t * stride)); return bankConflictDegree(w); }

int main() {
    // 원래 예
    assert(stridedTransactions(1) == 1 && stridedTransactions(2) == 2 && stridedTransactions(4) == 4 && stridedTransactions(32) == 32);
    assert(stridedConflict(1) == 1 && stridedConflict(2) == 2 && stridedConflict(32) == 32 && stridedConflict(33) == 1);
    for (int s = 1; s <= 64; s++) assert(stridedConflict(s) == std::gcd(s, 32));                                  // ③ 충돌 정도 = gcd(stride, 32)
    // ① 병합 닫힌 형태
    for (int s = 1; s <= 64; ++s) assert(stridedTransactions(s) == std::min(s, 32));
    for (int k = 0; k < 32; ++k) assert(stridedTransactions(1, k) == (k == 0 ? 1 : 2));                          // 정렬이 안 맞으면 연속 접근도 2 구간
    { std::vector<uint64_t> a; for (int t = 0; t < WARP; ++t) a.push_back((uint64_t)t * 4); assert(transactions(a, 4, 32) == 4); }       // 32B 섹터 단위로 세면 128B 연속 = 4 섹터
    // ② AoS / SoA
    { std::vector<uint64_t> aos12, aos16, soa, vec4; for (int t = 0; t < WARP; ++t) { aos12.push_back((uint64_t)t * 12); aos16.push_back((uint64_t)t * 16); soa.push_back((uint64_t)t * 4); vec4.push_back((uint64_t)t * 16); }
      assert(transactions(aos12, 4) == 3 && transactions(aos16, 4) == 4 && transactions(soa, 4) == 1 && transactions(vec4, 16) == 4); }               // x 만 읽을 때 3/4 구간, SoA 1, float4 로 통째로 읽으면 512B = 4 구간 (전부 쓸모 있음)
    // ③ 방송
    { std::vector<uint32_t> same(WARP, 7); assert(bankConflictDegree(same) == 1); std::vector<uint32_t> pairs; for (int t = 0; t < WARP; ++t) pairs.push_back((uint32_t)(t / 2)); assert(bankConflictDegree(pairs) == 1); }
    // ④ 타일 열 접근과 패딩
    for (int width = 32; width <= 40; ++width) { std::vector<uint32_t> col; for (int row = 0; row < WARP; ++row) col.push_back((uint32_t)(row * width)); assert(bankConflictDegree(col) == std::gcd(width, 32)); }
    // ⑤ 전치
    {   const int N = 256; auto globalTransactions = [&](bool tiled) { long total = 0;
            for (int y = 0; y < N; ++y) for (int x0 = 0; x0 < N; x0 += WARP) {                                   // 워프 하나 = 같은 행의 32 개 연속 원소
                std::vector<uint64_t> rd, wr; for (int l = 0; l < WARP; ++l) { rd.push_back(((uint64_t)y * N + (x0 + l)) * 4); wr.push_back(((uint64_t)(x0 + l) * N + y) * 4); }
                total += transactions(rd, 4);
                if (!tiled) total += transactions(wr, 4);                                                         // 단순 전치: 열 방향 쓰기 = 간격 N 개 float
                else total += 1;                                                                                   // 타일 전치: 공유 메모리를 거쳐 출력 행을 연속으로 쓴다 (타일 안에서 이미 전치됨)
            } return total; };
        long naive = globalTransactions(false), tiled = globalTransactions(true); long warps = (long)N * N / WARP;
        assert(naive == warps * (1 + 32) && tiled == warps * 2 && naive * 2 == tiled * 33);                          // 16.5 배
        std::mt19937 rng(3); std::vector<int> A(N * N), B(N * N, 0), C(N * N, 0); for (int& v : A) v = (int)rng();
        for (int i = 0; i < N; ++i) for (int j = 0; j < N; ++j) B[j * N + i] = A[i * N + j];                         // 단순 전치
        const int T = 32; std::vector<int> tile(T * (T + 1));                                                         // 타일 전치: 폭 33 의 공유 메모리 타일
        for (int bi = 0; bi < N; bi += T) for (int bj = 0; bj < N; bj += T) { for (int i = 0; i < T; ++i) for (int j = 0; j < T; ++j) tile[i * (T + 1) + j] = A[(bi + i) * N + bj + j]; for (int i = 0; i < T; ++i) for (int j = 0; j < T; ++j) C[(bj + i) * N + bi + j] = tile[j * (T + 1) + i]; }
        assert(B == C); }
    // ⑥ 병렬 합의 뱅크 충돌
    {   const int BLOCK = 256; std::mt19937 rng(5); std::vector<long> data(BLOCK); for (long& v : data) v = (long)(rng() % 1000); long want = std::accumulate(data.begin(), data.end(), 0L);
        auto reduce = [&](bool interleaved, long& serialized) {
            std::vector<long> sh = data; serialized = 0;
            for (int s = interleaved ? 1 : BLOCK / 2; interleaved ? s < BLOCK : s > 0; s = interleaved ? s * 2 : s / 2) {
                for (int w = 0; w < BLOCK / WARP; ++w) {                                                          // 워프마다 읽기 접근을 모아 충돌 정도를 더한다
                    std::vector<uint32_t> rd1, rd2;
                    for (int l = 0; l < WARP; ++l) { int t = w * WARP + l; int idx = interleaved ? 2 * s * t : t; if (interleaved ? idx + s < BLOCK : t < s) { rd1.push_back((uint32_t)idx); rd2.push_back((uint32_t)(idx + s)); } }
                    if (!rd1.empty()) serialized += bankConflictDegree(rd1) + bankConflictDegree(rd2);
                }
                for (int t = 0; t < BLOCK; ++t) { int idx = interleaved ? 2 * s * t : t; if (interleaved ? idx + s < BLOCK : t < s) sh[idx] += sh[idx + s]; }
            }
            return sh[0]; };
        long ser1 = 0, ser2 = 0; assert(reduce(true, ser1) == want && reduce(false, ser2) == want); assert(ser1 > 3 * ser2);                    // 같은 합, 인터리브 방식이 훨씬 많이 직렬화
        std::cout << "GPUMemory verified: coalescing = min(stride,32) transactions, bank conflicts = gcd(stride,32), tile padding 33 removes the 32-way conflict, transpose uses 16.5x fewer transactions with tiles, reduction serialization " << ser1 << " vs " << ser2 << "." << std::endl; }
    return 0;
}
// Time Complexity: O(32) (워프 한 번)
// Space Complexity: O(1)
```
## UnifiedMemory()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <list>
#include <random>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// 통합 메모리(CUDA Unified Memory): CPU 와 GPU 가 같은 포인터를 쓰고, 페이지가 필요한 쪽으로 자동 이동(migration)한다.  편리하지만 상대편이 페이지를 만지는 순간마다 페이지 폴트와 이동 비용이 든다.  prefetch 로 미리 옮기면 폴트가 사라지고, read-mostly 힌트로 읽기 전용 복제본을 두면 읽기 핑퐁이 사라진다.
// 시뮬레이터: 페이지마다 "유효한 사본이 있는 쪽" 비트(호스트=1, 디바이스=2).  ON_DEMAND = 사본이 없는 쪽이 접근하면 폴트하고 사본이 *이동*.  READ_MOSTLY = 읽기 폴트는 *복제*, 쓰기는 다른 쪽 사본을 무효화.
//  ① 손 계산: CPU 초기화 → GPU 처리 → CPU 읽기 (N 페이지) — on-demand 는 정확히 2N 폴트, prefetch 두 번이면 폴트 0 + 대량 이동 2 번  ② 비용 모형(폴트 F=25, 페이지당 이동 M=1, 묶음 지연 L=60) — N=1,2 에서는 on-demand 가 싸고 N≥3 부터 prefetch 가 이긴다(교차점 L/(F−M)=2.5)
//  ③ 무작위 접근 기록 300 개(페이지 8, 길이 3 000): ON_DEMAND 폴트 수 == "페이지별로 접근 쪽이 바뀐 횟수"(호스트 시작) 라는 독립 공식, READ_MOSTLY 폴트 수 == "마지막 내 접근 뒤 상대 쓰기가 있었는가" 라는 독립 공식, 그리고 READ_MOSTLY ≤ ON_DEMAND
//  ④ 핑퐁: 읽기만 번갈아 k 번 하면 ON_DEMAND 는 k−1 폴트, READ_MOSTLY 는 정확히 1 폴트; 쓰기를 번갈아 하면 두 정책이 같다(k−1)  ⑤ 디바이스 메모리 과구독(용량 C 페이지, LRU 퇴출): 작업 집합 W ≤ C 면 폴트 W, W = C+1 이고 순환 접근이면 *모든* 접근이 폴트 — 임의 기록에서 LRU 시뮬레이터 == 재사용 거리 공식
enum Side { HOST = 0, DEVICE = 1 };
struct Access { int page; Side who; bool write; };
enum Policy { ON_DEMAND, READ_MOSTLY };
class UnifiedMemory {
public:
    UnifiedMemory(int pages, Policy p) : pol(p), valid(pages, 1) {}                                                                                                     // 처음엔 호스트에만 사본
    void access(const Access& a) { unsigned me = 1u << a.who; unsigned& v = valid[a.page];
        if (!(v & me)) { ++faults; v = (pol == READ_MOSTLY && !a.write) ? (v | me) : me; }                                                                               // 폴트: 이동(또는 읽기 복제)
        else if (a.write) { if (v != me) ++invalidations; v = me; } }                                                                                                     // 쓰기는 다른 사본을 무효화
    void prefetch(int first, int count, Side to) { bool any = false; for (int i = first; i < first + count; ++i) if (valid[i] != (1u << to)) { valid[i] = 1u << to; any = true; ++bulkPages; } if (any) ++bulkBatches; }   // 묶음 이동
    long faults = 0, invalidations = 0, bulkBatches = 0, bulkPages = 0;
private:
    Policy pol; std::vector<unsigned> valid;
};
class DeviceLRU {                                                                                                                                                       // 디바이스 용량 C 페이지, 가장 오래 안 쓴 것부터 퇴출
public:
    explicit DeviceLRU(int c) : cap(c) {}
    void touch(int page) { auto it = pos.find(page); if (it != pos.end()) { order.erase(it->second); } else { ++faults; if ((int)order.size() == cap) { pos.erase(order.back()); order.pop_back(); ++evictions; } } order.push_front(page); pos[page] = order.begin(); }
    long faults = 0, evictions = 0;
private:
    int cap; std::list<int> order; std::unordered_map<int, std::list<int>::iterator> pos;
};
long cost(const UnifiedMemory& u, long F, long M, long L) { return u.faults * F + u.bulkPages * M + u.bulkBatches * L; }
long onDemandOracle(const std::vector<Access>& tr, int pages) { std::vector<int> last(pages, HOST); long f = 0; for (auto& a : tr) { if (last[a.page] != a.who) ++f; last[a.page] = a.who; } return f; }          // 접근 쪽이 바뀐 횟수
long readMostlyOracle(const std::vector<Access>& tr, int pages) { long f = 0; for (size_t i = 0; i < tr.size(); ++i) { const Access& a = tr[i]; long j = -1; bool has = false;                                           // 독립 공식
        for (long k = (long)i - 1; k >= 0; --k) if (tr[k].page == a.page && tr[k].who == a.who) { j = k; has = true; break; }
        if (!has && a.who == DEVICE) { ++f; continue; }                                                                                                                    // 디바이스는 처음 접근이면 사본이 없다
        bool otherWrite = false; for (long k = j + 1; k < (long)i; ++k) if (tr[k].page == a.page && tr[k].who != a.who && tr[k].write) { otherWrite = true; break; } if (otherWrite) ++f; } (void)pages; return f; }
long lruOracle(const std::vector<int>& tr, int cap) { long f = 0; for (size_t i = 0; i < tr.size(); ++i) { long j = -1; for (long k = (long)i - 1; k >= 0; --k) if (tr[k] == tr[i]) { j = k; break; }
        if (j < 0) { ++f; continue; } std::unordered_set<int> distinct(tr.begin() + j + 1, tr.begin() + i); if ((int)distinct.size() >= cap) ++f; } return f; }                // 재사용 거리 ≥ C 이면 폴트

int main() {
    const int N = 256; UnifiedMemory onDemand(N, ON_DEMAND), hinted(N, ON_DEMAND);
    for (int p = 0; p < N; ++p) onDemand.access({p, HOST, true}); for (int p = 0; p < N; ++p) onDemand.access({p, DEVICE, true}); for (int p = 0; p < N; ++p) onDemand.access({p, HOST, false});                      // ①
    for (int p = 0; p < N; ++p) hinted.access({p, HOST, true}); hinted.prefetch(0, N, DEVICE); for (int p = 0; p < N; ++p) hinted.access({p, DEVICE, true}); hinted.prefetch(0, N, HOST); for (int p = 0; p < N; ++p) hinted.access({p, HOST, false});
    assert(onDemand.faults == 2 * N && hinted.faults == 0 && hinted.bulkBatches == 2 && hinted.bulkPages == 2 * N);
    int firstWin = -1; for (int n = 1; n <= 12; ++n) { UnifiedMemory a(n, ON_DEMAND), b(n, ON_DEMAND); for (int p = 0; p < n; ++p) a.access({p, HOST, true}), b.access({p, HOST, true});                      // ② 교차점
        for (int p = 0; p < n; ++p) a.access({p, DEVICE, true}); for (int p = 0; p < n; ++p) a.access({p, HOST, false}); b.prefetch(0, n, DEVICE); for (int p = 0; p < n; ++p) b.access({p, DEVICE, true}); b.prefetch(0, n, HOST); for (int p = 0; p < n; ++p) b.access({p, HOST, false});
        bool prefetchWins = cost(b, 25, 1, 60) < cost(a, 25, 1, 60); if (n < 3) assert(!prefetchWins); else assert(prefetchWins); if (prefetchWins && firstWin < 0) firstWin = n; }
    assert(firstWin == 3);
    std::mt19937 rng(77); long strictlyBetter = 0, totalOnDemand = 0, totalReadMostly = 0;
    for (int trial = 0; trial < 300; ++trial) { const int pages = 8; std::vector<Access> tr; int writePct = (int)(rng() % 60); for (int i = 0; i < 3000; ++i) tr.push_back({(int)(rng() % pages), (rng() % 2) ? DEVICE : HOST, (int)(rng() % 100) < writePct});          // ③
        UnifiedMemory a(pages, ON_DEMAND), b(pages, READ_MOSTLY); for (auto& x : tr) { a.access(x); b.access(x); }
        assert(a.faults == onDemandOracle(tr, pages) && b.faults == readMostlyOracle(tr, pages) && b.faults <= a.faults); if (b.faults < a.faults) ++strictlyBetter; totalOnDemand += a.faults; totalReadMostly += b.faults; }
    assert(strictlyBetter > 200 && totalReadMostly < totalOnDemand);
    for (int k : {2, 3, 10, 51}) { UnifiedMemory r1(1, ON_DEMAND), r2(1, READ_MOSTLY), w1(1, ON_DEMAND), w2(1, READ_MOSTLY);                                                                             // ④ 핑퐁
        for (int i = 0; i < k; ++i) { Side s = (i % 2 == 0) ? HOST : DEVICE; r1.access({0, s, false}); r2.access({0, s, false}); w1.access({0, s, true}); w2.access({0, s, true}); }
        assert(r1.faults == k - 1 && r2.faults == 1 && w1.faults == k - 1 && w2.faults == k - 1); }
    {   for (int W : {3, 8, 20}) for (int C : {1, 4, 8, 19, 20, 25}) { DeviceLRU d(C); for (int pass = 0; pass < 10; ++pass) for (int p = 0; p < W; ++p) d.touch(p);                                          // ⑤ 순환 접근
            long expect = (W <= C) ? W : 10L * W; assert(d.faults == expect); assert(d.evictions == (W <= C ? 0 : expect - C)); }
        for (int trial = 0; trial < 100; ++trial) { int W = 5 + (int)(rng() % 30), C = 1 + (int)(rng() % 25); std::vector<int> tr; for (int i = 0; i < 1500; ++i) tr.push_back(rng() % 3 == 0 ? (int)(rng() % 4) : (int)(rng() % W)); DeviceLRU d(C); for (int p : tr) d.touch(p); assert(d.faults == lruOracle(tr, C)); } }
    std::cout << "UnifiedMemory: on-demand migration faulted " << onDemand.faults << " times where two prefetches faulted 0; prefetch became cheaper exactly from N=" << firstWin << "; 300 random traces matched both independent fault formulas (read-mostly cut faults from " << totalOnDemand << " to " << totalReadMostly << "); LRU oversubscription thrashed every access once W exceeded C" << std::endl;
    return 0;
}
// Time Complexity: 접근당 O(1) (검증 오라클은 O(n²))
// Space Complexity: O(페이지 수)
```
## PersistentMemory()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <functional>
#include <vector>
#include <cassert>

// 영속 메모리(Intel Optane 등): 바이트 주소 접근이 되면서 전원이 꺼져도 남는다.  단 CPU 캐시는 휘발성이라, 저장 후 캐시 라인을 NVM 으로 내리는(clwb + sfence) 순서를 직접 지켜야 한다.
// 캐시는 아무 때나 줄을 내보낼 수 있어서 "저장 순서" 가 곧 "영속 순서" 가 아니다 -> 원자성은 로그로 확보: (1) 옛 값을 로그에 영속시키고 (2) 유효 표시 (3) 데이터 수정 (4) 로그 무효화.
// 시뮬레이터가 가능한 모든 충돌 시점 × 아직 내려가지 않은 줄의 모든 영속 조합을 열거하며 복구 후 불변식(A+B == 100)을 검사한다
const int A = 0, B = 1, LOG_A = 2, LOG_B = 3, VALID = 4, WORDS = 5;
struct Nvm {
    uint64_t persisted[WORDS] = {50, 50, 0, 0, 0}; uint64_t cache[WORDS] = {50, 50, 0, 0, 0}; bool dirty[WORDS] = {};
    void store(int i, uint64_t v) { cache[i] = v; dirty[i] = true; }
    void persist(int i) { persisted[i] = cache[i]; dirty[i] = false; }          // clwb + sfence: 이 줄은 확실히 NVM 에
};
typedef std::vector<std::function<void(Nvm&)>> Program;

void recover(uint64_t p[WORDS]) { if (p[VALID]) { p[A] = p[LOG_A]; p[B] = p[LOG_B]; p[VALID] = 0; } }   // 로그가 유효하면 옛 값으로 되돌린다

// 프로그램의 모든 접두 지점에서 충돌시키고, 남은 dirty 줄이 임의의 부분집합만 영속되었다고 가정해 복구 결과를 검사한다
bool crashConsistent(const Program& prog, bool useRecovery) {
    for (size_t k = 0; k <= prog.size(); k++) {
        Nvm m; for (size_t i = 0; i < k; i++) prog[i](m);
        std::vector<int> dirty; for (int i = 0; i < WORDS; i++) if (m.dirty[i]) dirty.push_back(i);
        for (unsigned mask = 0; mask < (1u << dirty.size()); mask++) {
            uint64_t state[WORDS]; for (int i = 0; i < WORDS; i++) state[i] = m.persisted[i];
            for (size_t d = 0; d < dirty.size(); d++) if (mask >> d & 1) state[dirty[d]] = m.cache[dirty[d]];
            if (useRecovery) recover(state);
            bool ok = (state[A] == 50 && state[B] == 50) || (state[A] == 40 && state[B] == 60);   // 이체 전 또는 이체 후만 허용
            if (!ok) return false;
        }
    }
    return true;
}

int main() {
    Program naive = {                                                   // 로그 없이 두 값을 차례로 수정
        [](Nvm& m) { m.store(A, 40); m.persist(A); },
        [](Nvm& m) { m.store(B, 60); m.persist(B); }};
    assert(!crashConsistent(naive, true));                             // A 만 반영되고 충돌하면 합계가 깨진다 (A=40, B=50)

    Program undoLog = {                                                 // 실행 취소(undo) 로그 프로토콜
        [](Nvm& m) { m.store(LOG_A, m.cache[A]); m.store(LOG_B, m.cache[B]); },
        [](Nvm& m) { m.persist(LOG_A); m.persist(LOG_B); },            // 옛 값을 먼저 영속
        [](Nvm& m) { m.store(VALID, 1); m.persist(VALID); },           // 그 다음에 로그 유효 표시
        [](Nvm& m) { m.store(A, 40); m.store(B, 60); },                // 데이터 수정 (캐시에서 임의 순서로 내려갈 수 있다)
        [](Nvm& m) { m.persist(A); m.persist(B); },
        [](Nvm& m) { m.store(VALID, 0); m.persist(VALID); }};          // 마지막으로 로그 무효화
    assert(crashConsistent(undoLog, true));                            // 모든 충돌 시점·영속 조합에서 복구 후 불변식 유지
    assert(!crashConsistent(undoLog, false));                          // 복구 단계를 빼면 중간 상태가 그대로 노출된다
    std::cout << "PersistentMemory: undo-log protocol is crash-consistent for every crash point and eviction subset." << std::endl;
    return 0;
}
// Time Complexity: 검증 O(단계 · 2^dirty)
// Space Complexity: O(1) 로그
```
## HugePage()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <set>
#include <vector>
#if defined(__linux__)
#include <sys/mman.h>
#endif

// 대형 페이지(2MB / 1GB): 페이지가 클수록 TLB 항목 하나가 덮는 범위(TLB reach)가 커져 TLB 미스와 페이지 테이블 크기가 줄어든다.
//   TLB reach = 항목 수 x 페이지 크기.   데이터베이스·JVM·HPC 처럼 큰 메모리를 쓰는 프로그램에서 수 %~수십 % 성능 향상.
// 단점: 페이지 단위 보호/스왑이 거칠어지고, 큰 연속 물리 메모리가 필요하며 내부 단편화가 커진다.  리눅스는 Transparent Huge Pages(THP)와 madvise(MADV_HUGEPAGE)를 제공
// 이 예제는 장단점을 숫자로 확인한다:
//  ① TLB 시뮬레이션: 완전 연관 LRU TLB 64 항목에서 균일 무작위 접근의 미스율은 1 - 항목/페이지 수 (4KB: 작업 집합 64MB 는 거의 100% 미스, 2MB: 작업 집합 128MB 는 전부 TLB 에 들어가 0%, 512MB 는 87.5%)  — 이론값과 시뮬레이션 일치
//  ② 페이지 테이블 메모리: 밀집 매핑 N 바이트에 필요한 테이블 프레임 수를 직접 센 값 == 올림 공식, 4KB 페이지는 매핑 크기의 0.2%, 2MB 페이지는 그 1/512
//  ③ 메모리 부풀림: 2MB 구역마다 1 바이트만 건드리면 대형 페이지는 구역마다 2MB(512배)를 쓰고, "채운 비율이 임계값을 넘으면 합친다" 는 정책은 닫힌 형태와 일치
//  ④ 물리 단편화: 프레임을 확률 f 로 점유했을 때 비어 있는 정렬된 2MB 블록 수의 기댓값 32 · (1-f)^512 와 시뮬레이션 평균이 일치(f = 0.001), 압축(compaction) 후엔 floor(빈 프레임 / 512) 개이고 옮긴 프레임 수는 정확히 계산한 값
struct Tlb {
    size_t cap; std::list<uint64_t> lru; std::map<uint64_t, std::list<uint64_t>::iterator> pos; long misses = 0, accesses = 0;
    explicit Tlb(size_t c) : cap(c) {}
    void access(uint64_t page) {
        ++accesses; auto it = pos.find(page);
        if (it != pos.end()) { lru.splice(lru.begin(), lru, it->second); return; }
        ++misses; lru.push_front(page); pos[page] = lru.begin(); if (lru.size() > cap) { pos.erase(lru.back()); lru.pop_back(); }
    }
    double missRate() const { return accesses ? (double)misses / accesses : 0; }
};

size_t tableFramesDense(uint64_t pageCount) {                                                  // 연속 매핑 pageCount 개 4KB 페이지에 필요한 테이블 프레임을 직접 센다
    std::set<uint64_t> pt, pd, pdpt; for (uint64_t i = 0; i < pageCount; ++i) { pt.insert(i >> 9); pd.insert(i >> 18); pdpt.insert(i >> 27); } return 1 + pdpt.size() + pd.size() + pt.size();
}

int main() {
    const uint64_t KB = 1024, MB = KB * 1024, GB = MB * 1024;
    // 원래 예: 산술
    {   const uint64_t entries = 64;
        assert(entries * 4 * KB == 256 * KB && entries * 2 * MB == 128 * MB && entries * 1 * GB == 64 * GB);
        assert(GB / (4 * KB) == 262144 && GB / (2 * MB) == 512);
        assert(GB / (4 * KB) * 8 == 2 * MB && GB / (2 * MB) * 8 == 4 * KB); }
    // ① TLB 미스율: 균일 무작위 접근
    {   std::mt19937_64 rng(2); auto rate = [&](uint64_t workingSet, uint64_t pageSize, size_t entries) {
            Tlb t(entries); uint64_t pages = workingSet / pageSize; for (uint64_t i = 0; i < pages * 2; ++i) t.access(i % pages);                       // 워밍업
            t.misses = t.accesses = 0; for (int i = 0; i < 300000; ++i) t.access(rng() % pages); return t.missRate(); };
        double r4k = rate(64 * MB, 4 * KB, 64), r2m = rate(64 * MB, 2 * MB, 64), r2mBig = rate(512 * MB, 2 * MB, 32);
        assert(std::abs(r4k - (1.0 - 64.0 / 16384)) < 0.005);                                                            // 4KB 페이지: 항목 64 / 페이지 16384 -> 적중 0.4%
        assert(r2m == 0.0);                                                                                              // 2MB 페이지: 페이지 32 개가 64 항목에 다 들어간다
        assert(std::abs(r2mBig - (1.0 - 32.0 / 256)) < 0.005);                                                           // 512MB 는 256 개 -> 적중 12.5%
        assert(rate(128 * MB, 4 * KB, 64) > 0.99 && rate(128 * KB, 4 * KB, 64) == 0.0); }
    // ② 페이지 테이블 메모리
    for (uint64_t mb : {(uint64_t)1, (uint64_t)2, (uint64_t)64, (uint64_t)1024, (uint64_t)3000}) {
        uint64_t pagesN = mb * MB / (4 * KB), c512 = 512; auto ceilDiv = [](uint64_t a, uint64_t b) { return (a + b - 1) / b; };
        assert(tableFramesDense(pagesN) == 1 + ceilDiv(pagesN, c512 * c512 * c512) + ceilDiv(pagesN, c512 * c512) + ceilDiv(pagesN, c512));            // 올림 공식
        if (mb >= 64) { double overhead = (double)tableFramesDense(pagesN) * 4 * KB / (mb * MB); assert(overhead > 0.0019 && overhead < 0.0022); }                // 4KB 페이지: 약 0.2%
        uint64_t hugeN = ceilDiv(mb * MB, 2 * MB); uint64_t frames2m = 1 + ceilDiv(hugeN, c512 * c512) + ceilDiv(hugeN, c512);                           // 2MB 페이지: PT 단계가 없다
        assert(frames2m <= tableFramesDense(pagesN));
        if (mb >= 1024) assert(ceilDiv(pagesN, c512) >= 500 * ceilDiv(hugeN, c512)); }                                    // 잎 단계 테이블: 4KB 페이지는 PT 프레임 hugeN 개, 2MB 페이지는 PD 프레임 hugeN/512 개 -> 약 512 배 차이
    // ③ 메모리 부풀림 정책: 2MB 구역(= 4KB 페이지 512 개)마다 건드린 페이지 수 c 가 need 이상이 되면 대형 페이지 하나로 합친다
    {   const uint64_t REGIONS = 64; std::mt19937 rng(9); const size_t NEED[4] = {(size_t)-1, 256, 512, 1};                                 // 합치지 않음 / 절반 / 전부 / 처음 만질 때부터
        const char* names[4] = {"never", "half", "full", "always"}; (void)names;
        uint64_t committedSparse[4], committedDense[4];
        for (int workload = 0; workload < 2; ++workload) {
            for (int p = 0; p < 4; ++p) {
                std::mt19937 r(100 + workload); std::vector<std::set<unsigned>> touched(REGIONS); std::vector<char> promoted(REGIONS, 0); uint64_t committed = 0; int touches = workload == 0 ? 20000 : 400000;
                for (int i = 0; i < touches; ++i) {
                    uint64_t region = r() % REGIONS; unsigned pg = (unsigned)(r() % (workload == 0 ? 4 : 512));                          // 희소: 구역당 페이지 4 개만, 밀집: 전부
                    if (promoted[region]) continue;
                    if (touched[region].insert(pg).second) committed += 4 * KB;
                    if (touched[region].size() >= NEED[p]) { promoted[region] = 1; committed += 2 * MB - touched[region].size() * 4 * KB; }   // 작은 페이지들을 큰 페이지 하나로 교체
                }
                uint64_t expect = 0; for (uint64_t g = 0; g < REGIONS; ++g) { size_t c = touched[g].size(); expect += (c >= NEED[p]) ? 2 * MB : c * 4 * KB; }
                assert(committed == expect);                                                                                  // 순서와 무관하게 구역별 닫힌 형태
                (workload == 0 ? committedSparse : committedDense)[p] = committed;
            }
        }
        assert(committedSparse[3] == 128 * committedSparse[0] && committedSparse[1] == committedSparse[0] && committedSparse[2] == committedSparse[0]);                  // 희소하면 항상 합치는 정책이 128 배(512/4) 부풀린다
        for (int p = 1; p < 4; ++p) assert(committedDense[p] == committedDense[0] && committedDense[0] == REGIONS * 2 * MB);                                                // 밀집하면 합쳐도 메모리가 늘지 않는다
        uint64_t sparseSmall = 100 * 4 * KB, sparseHuge = 100 * 2 * MB; assert(sparseHuge == 512 * sparseSmall); (void)rng; }                                         // 구역마다 1 바이트: 512 배
    // ④ 물리 단편화와 압축
    {   const uint64_t FR = 16384, BLK = 512; std::mt19937_64 rng(5); const double f = 0.001; double sum = 0; const int TR = 2000;
        auto freeBlocksOf = [&](const std::vector<char>& used) { long n = 0; for (uint64_t b = 0; b < FR / BLK; ++b) { bool ok = true; for (uint64_t i = 0; i < BLK && ok; ++i) ok = !used[b * BLK + i]; n += ok; } return n; };
        for (int t = 0; t < TR; ++t) { std::vector<char> used(FR, 0); for (uint64_t i = 0; i < FR; ++i) used[i] = (double)(rng() % 1000000) / 1000000.0 < f; sum += (double)freeBlocksOf(used); }
        double expect = (double)(FR / BLK) * std::pow(1.0 - f, 512); assert(std::abs(sum / TR - expect) < 0.5);                                                          // 기댓값 32 * 0.999^512 = 19.2
        for (int t = 0; t < 50; ++t) {
            std::vector<char> used(FR, 0); uint64_t usedCount = 0; double dens = 0.05 + 0.5 * (double)(rng() % 100) / 100.0;
            for (uint64_t i = 0; i < FR; ++i) { used[i] = (double)(rng() % 1000000) / 1000000.0 < dens; usedCount += used[i]; }
            long expectMoves = 0; for (uint64_t i = usedCount; i < FR; ++i) expectMoves += used[i];                                                                       // 윗부분에 있는 점유 프레임 수 = 옮겨야 할 프레임 수
            long moves = 0; uint64_t lo = 0, hi = FR;
            for (;;) {                                                                                                                                                    // 두 손가락 압축: 아래쪽 빈 칸에 위쪽 점유 프레임을 채운다
                while (lo < usedCount && used[lo]) ++lo;
                while (hi > usedCount && !used[hi - 1]) --hi;
                if (lo >= usedCount || hi <= usedCount) break;
                used[lo] = 1; used[hi - 1] = 0; ++moves;
            }
            assert(moves == expectMoves && freeBlocksOf(used) == (long)((FR - usedCount) / BLK));                                                                         // 압축 뒤 빈 정렬 블록 = floor(빈 프레임 / 512)
            for (uint64_t i = 0; i < usedCount; ++i) assert(used[i]);                                                                                                     // 점유가 앞쪽에 모였다
        } }
#if defined(__linux__)
    {   size_t len = 4 * MB; void* p = mmap(nullptr, len + 2 * MB, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (p != MAP_FAILED) {
            uintptr_t aligned = ((uintptr_t)p + 2 * MB - 1) & ~(uintptr_t)(2 * MB - 1);                  // 2MB 경계로 정렬 (대형 페이지의 조건)
            int rc = madvise((void*)aligned, len, MADV_HUGEPAGE); (void)rc;                              // 커널에 "대형 페이지를 써도 좋다" 고 알린다 (시스템 설정에 따라 무시될 수 있음)
            *(volatile char*)aligned = 1; munmap(p, len + 2 * MB);
        } }
#endif
    std::cout << "HugePage verified: TLB miss rates match 1 - entries/pages, page-table overhead 0.2% vs 1/512 of that, sparse touching bloats memory 512x, and compaction restores floor(free/512) aligned 2MB blocks." << std::endl;
    return 0;
}
// Time Complexity: TLB 적중 O(log 항목) (시뮬레이션), 압축 O(프레임 수)
// Space Complexity: O(항목 수), 페이지 테이블 O(매핑 크기 / 4KB · 8B)
```
## RDMA()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <vector>

// RDMA(원격 직접 메모리 접근): 네트워크 카드(NIC)가 원격 노드의 메모리를 상대 CPU 와 운영체제의 개입 없이 직접 읽고 쓴다 (InfiniBand, RoCE).  커널 우회·제로 카피로 지연이 마이크로초 수준.
// 흐름: (1) 메모리 영역을 NIC 에 등록(고정, pinned) -> rkey 발급 (2) rkey 와 원격 주소를 상대에게 전달 (3) RDMA_WRITE/READ 를 보내면 상대의 NIC 가 rkey·범위·권한을 검사하고 처리
// 이 구현은 verbs 의 핵심 의미를 사건 구동 시뮬레이션으로 만든다 (실제 API: ibv_reg_mr, ibv_post_send, ibv_poll_cq):
//  메모리 영역(MR): 접근 권한 {LOCAL_WRITE, REMOTE_READ, REMOTE_WRITE, REMOTE_ATOMIC}, 등록 해제 가능.  작업 요청(WR): SEND, RDMA_WRITE, RDMA_READ, 원자 CAS, 원자 FETCH_ADD.  큐 페어(QP)마다 순서가 지켜지고(무작위 지연이 있어도)
//  완료(CQ)는 요청 순서대로 상태 코드와 함께 돌아온다.  단방향 연산은 상대 CPU 를 쓰지 않고(cpuTouches 불변), SEND 는 상대가 미리 받기 버퍼를 올려 둬야 한다(없으면 RNR, 너무 작으면 길이 오류)
// 검증: ① 권한·범위·rkey·등록 해제 오류가 올바른 상태 코드  ② 같은 QP 의 RDMA_WRITE 1 000 개는 지연이 무작위라도 마지막 값이 남고 완료가 요청 순서  ③ 클라이언트 4 개가 서버 카운터에 FETCH_ADD 를 1 000 번씩 —
//        최종 4 000, 돌려받은 옛 값이 0..3999 를 정확히 한 번씩 (원자성)  ④ 원격 스핀락(CAS)으로 읽기-수정-쓰기를 감싸면 갱신을 하나도 잃지 않고(4 x 50), 락 없이 하면 갱신을 잃는다
//        ⑤ SEND/RECV: 받기 버퍼 R 개만 올려 두면 앞의 R 개만 성공하고 나머지는 RNR, 길이 초과는 길이 오류, 받는 쪽 CPU 가 관여한 횟수 == 올린 수 + 처리한 수
enum Access : unsigned { LOCAL_WRITE = 1, REMOTE_READ = 2, REMOTE_WRITE = 4, REMOTE_ATOMIC = 8 };
enum Opcode { SEND, RDMA_WRITE, RDMA_READ, ATOMIC_CAS, ATOMIC_FADD };
enum Status { SUCCESS, REM_ACCESS_ERR, LOC_PROT_ERR, LOC_LEN_ERR, RNR_ERR };
struct MR { std::vector<uint8_t> mem; unsigned access; bool valid; };
struct WR { Opcode op; uint64_t id; uint32_t lkey; size_t loff, len; uint32_t rkey; size_t roff; uint64_t cmp, val; };
struct Completion { uint64_t id; Status st; uint64_t old; int qp; };
struct RecvWR { uint32_t lkey; size_t off, len; };

class Node {
public:
    std::map<uint32_t, MR> mrs; std::deque<RecvWR> recvQ; uint32_t nextKey; long cpuTouches = 0; explicit Node(uint32_t base) : nextKey(base) {}
    uint32_t reg(size_t bytes, unsigned access) { mrs[nextKey] = MR{std::vector<uint8_t>(bytes, 0), access, true}; return nextKey++; }
    void dereg(uint32_t key) { mrs.at(key).valid = false; }
    uint8_t* mem(uint32_t key) { return mrs.at(key).mem.data(); }
    uint64_t load64(uint32_t key, size_t off) { uint64_t v; std::memcpy(&v, mem(key) + off, 8); return v; }
    void store64(uint32_t key, size_t off, uint64_t v) { std::memcpy(mem(key) + off, &v, 8); }
    void postRecv(const RecvWR& r) { recvQ.push_back(r); ++cpuTouches; }                           // 받는 쪽 CPU 가 버퍼를 올린다
    MR* find(uint32_t key, unsigned need, size_t off, size_t len) {                                  // NIC 의 검사: 존재·유효·권한·범위
        auto it = mrs.find(key); if (it == mrs.end() || !it->second.valid || (it->second.access & need) != need || off + len > it->second.mem.size()) return nullptr; return &it->second;
    }
};

class Fabric {
    struct Ev { long time, seq; bool complete; int qp; WR wr; Completion c; bool operator>(const Ev& o) const { return time != o.time ? time > o.time : seq > o.seq; } };
    std::priority_queue<Ev, std::vector<Ev>, std::greater<Ev>> pq; long now = 0, seq = 0; std::mt19937 rng; std::map<int, long> lastDeliver, lastComplete; struct Qp { int from, to; }; std::vector<Qp> qps;
public:
    std::vector<Node> nodes; std::function<void(const Completion&)> onComplete; std::map<int, std::vector<Completion>> cq; long executed = 0;
    explicit Fabric(int n, uint32_t seed) : rng(seed) { for (int i = 0; i < n; ++i) nodes.emplace_back(0x100u * (uint32_t)(i + 1)); }
    int connect(int from, int to) { qps.push_back({from, to}); return (int)qps.size() - 1; }
    void post(int qp, const WR& wr) { long t = std::max(now + 1 + (long)(rng() % 20), lastDeliver[qp] + 1); lastDeliver[qp] = t; pq.push({t, seq++, false, qp, wr, {}}); }   // 지연은 무작위지만 QP 안의 순서는 보존
    void run() {
        while (!pq.empty()) {
            Ev e = pq.top(); pq.pop(); now = e.time;
            if (!e.complete) { Completion c = execute(e.qp, e.wr); long t = std::max(now + 1 + (long)(rng() % 20), lastComplete[e.qp] + 1); lastComplete[e.qp] = t; pq.push({t, seq++, true, e.qp, e.wr, c}); }
            else { cq[e.qp].push_back(e.c); if (onComplete) onComplete(e.c); }
        }
    }
    Completion execute(int qp, const WR& w) {                                                         // 응답 노드의 NIC 가 하는 일
        ++executed; Node& src = nodes[qps[qp].from]; Node& dst = nodes[qps[qp].to]; Completion c{w.id, SUCCESS, 0, qp};
        bool writesLocal = w.op == RDMA_READ || w.op == ATOMIC_CAS || w.op == ATOMIC_FADD;
        MR* loc = src.find(w.lkey, writesLocal ? (unsigned)LOCAL_WRITE : 0u, w.loff, w.op == ATOMIC_CAS || w.op == ATOMIC_FADD ? 8 : w.len);
        if (!loc) { c.st = LOC_PROT_ERR; return c; }                                                    // 보내는 쪽 지역 버퍼 검사
        if (w.op == SEND) {
            if (dst.recvQ.empty()) { c.st = RNR_ERR; return c; } RecvWR r = dst.recvQ.front(); dst.recvQ.pop_front(); ++dst.cpuTouches;        // 받는 쪽 CPU 가 완료를 처리
            MR* buf = dst.find(r.lkey, LOCAL_WRITE, r.off, w.len); if (w.len > r.len || !buf) { c.st = LOC_LEN_ERR; return c; }
            std::memcpy(&buf->mem[r.off], &loc->mem[w.loff], w.len); return c;
        }
        unsigned need = w.op == RDMA_WRITE ? REMOTE_WRITE : w.op == RDMA_READ ? REMOTE_READ : REMOTE_ATOMIC; size_t len = (w.op == ATOMIC_CAS || w.op == ATOMIC_FADD) ? 8 : w.len;
        MR* rem = dst.find(w.rkey, need, w.roff, len); if (!rem || ((w.op == ATOMIC_CAS || w.op == ATOMIC_FADD) && w.roff % 8)) { c.st = REM_ACCESS_ERR; return c; }   // 상대 CPU 는 쓰이지 않는다
        if (w.op == RDMA_WRITE) std::memcpy(&rem->mem[w.roff], &loc->mem[w.loff], w.len);
        else if (w.op == RDMA_READ) std::memcpy(&loc->mem[w.loff], &rem->mem[w.roff], w.len);
        else { uint64_t old; std::memcpy(&old, &rem->mem[w.roff], 8); uint64_t nv = (w.op == ATOMIC_CAS) ? (old == w.cmp ? w.val : old) : old + w.val; std::memcpy(&rem->mem[w.roff], &nv, 8); std::memcpy(&loc->mem[w.loff], &old, 8); c.old = old; }
        return c;
    }
};

int main() {
    // ① 상태 코드
    {   Fabric f(2, 1); int qp = f.connect(0, 1); Node& cli = f.nodes[0]; Node& srv = f.nodes[1];
        uint32_t l = cli.reg(64, LOCAL_WRITE), rw = srv.reg(64, REMOTE_READ | REMOTE_WRITE | REMOTE_ATOMIC), ro = srv.reg(64, REMOTE_READ), dead = srv.reg(64, REMOTE_READ | REMOTE_WRITE); srv.dereg(dead);
        const char msg[] = "hello rdma"; std::memcpy(cli.mem(l), msg, sizeof msg);
        f.post(qp, {RDMA_WRITE, 1, l, 0, sizeof msg, rw, 8, 0, 0}); f.post(qp, {RDMA_READ, 2, l, 32, sizeof msg, rw, 8, 0, 0});
        f.post(qp, {RDMA_WRITE, 3, l, 0, 4, ro, 0, 0, 0}); f.post(qp, {RDMA_READ, 4, l, 0, 8, rw, 60, 0, 0}); f.post(qp, {RDMA_READ, 5, l, 0, 8, 0xdead, 0, 0, 0}); f.post(qp, {RDMA_WRITE, 6, l, 0, 4, dead, 0, 0, 0});
        f.post(qp, {ATOMIC_FADD, 7, l, 48, 0, rw, 3, 0, 1}); f.post(qp, {ATOMIC_FADD, 8, l, 48, 0, ro, 0, 0, 1}); f.post(qp, {RDMA_READ, 9, 0xbeef, 0, 4, rw, 0, 0, 0});
        f.run(); auto& c = f.cq[qp];
        assert(c.size() == 9 && c[0].st == SUCCESS && c[1].st == SUCCESS && std::strcmp((char*)cli.mem(l) + 32, "hello rdma") == 0 && srv.cpuTouches == 0);   // 직접 쓰기·읽기, 서버 CPU 불관여
        assert(c[2].st == REM_ACCESS_ERR && c[3].st == REM_ACCESS_ERR && c[4].st == REM_ACCESS_ERR && c[5].st == REM_ACCESS_ERR);                        // 쓰기 권한 없음, 범위 초과, 잘못된 rkey, 등록 해제됨
        assert(c[6].st == REM_ACCESS_ERR && c[7].st == REM_ACCESS_ERR && c[8].st == LOC_PROT_ERR);                                                         // 정렬 안 된 원자 연산, 원자 권한 없음, 잘못된 lkey
        for (size_t i = 0; i < c.size(); ++i) assert(c[i].id == i + 1); }                                                                                  // 완료는 요청 순서
    // ② 순서 보존
    {   Fabric f(2, 2); int qp = f.connect(0, 1); uint32_t rw = f.nodes[1].reg(8, REMOTE_WRITE);
        uint32_t src = f.nodes[0].reg(8 * 1000, LOCAL_WRITE);                                                       // 요청마다 별도의 지역 버퍼 칸 (전송은 나중에 일어나므로)
        for (uint64_t i = 1; i <= 1000; ++i) f.nodes[0].store64(src, (i - 1) * 8, i * 7);
        for (uint64_t i = 1; i <= 1000; ++i) f.post(qp, {RDMA_WRITE, i, src, (i - 1) * 8, 8, rw, 0, 0, 0});
        f.run(); assert(f.nodes[1].load64(rw, 0) == 7000); auto& c = f.cq[qp]; assert(c.size() == 1000); for (size_t i = 0; i < c.size(); ++i) { assert(c[i].id == i + 1 && c[i].st == SUCCESS); } }       // 마지막 값이 남고 완료는 순서대로
    // ③ 원자 FETCH_ADD
    {   const int C = 4, N = 1000; Fabric f(1 + C, 3); uint32_t counter = f.nodes[0].reg(8, REMOTE_ATOMIC); std::vector<int> qp(C); std::vector<uint32_t> loc(C);
        for (int c = 0; c < C; ++c) { qp[c] = f.connect(1 + c, 0); loc[c] = f.nodes[1 + c].reg(8 * N, LOCAL_WRITE); }
        for (int i = 0; i < N; ++i) for (int c = 0; c < C; ++c) f.post(qp[c], {ATOMIC_FADD, (uint64_t)i, loc[c], (size_t)i * 8, 0, counter, 0, 0, 1});
        f.run(); assert(f.nodes[0].load64(counter, 0) == (uint64_t)C * N && f.nodes[0].cpuTouches == 0);
        std::set<uint64_t> olds; for (int c = 0; c < C; ++c) for (int i = 0; i < N; ++i) olds.insert(f.nodes[1 + c].load64(loc[c], (size_t)i * 8));
        assert(olds.size() == (size_t)C * N && *olds.begin() == 0 && *olds.rbegin() == (uint64_t)C * N - 1); }                                         // 옛 값이 0..3999 를 정확히 한 번씩: 원자성
    // ④ 원격 스핀락
    long lostWithLock = 0, lostWithout = 0;
    for (int useLock = 1; useLock >= 0; --useLock) {
        const int C = 4, ITER = 50; Fabric f(1 + C, useLock ? 4 : 5); uint32_t lockWord = f.nodes[0].reg(16, REMOTE_ATOMIC | REMOTE_READ | REMOTE_WRITE);       // [0] 락, [8] 공유 카운터
        std::vector<int> qp(C); std::vector<uint32_t> loc(C); std::vector<int> state(C, 0), done(C, 0);                                                      // state: 0 락 시도, 1 읽는 중, 2 쓰는 중, 3 해제 중
        for (int c = 0; c < C; ++c) { qp[c] = f.connect(1 + c, 0); loc[c] = f.nodes[1 + c].reg(32, LOCAL_WRITE); }
        auto step = [&](int c) {
            if (done[c] == ITER) return;
            if (state[c] == 0) { if (useLock) { f.post(qp[c], {ATOMIC_CAS, 0, loc[c], 0, 0, lockWord, 0, 0, (uint64_t)c + 1}); } else { state[c] = 1; f.post(qp[c], {RDMA_READ, 1, loc[c], 8, 8, lockWord, 8, 0, 0}); } }
            else if (state[c] == 1) f.post(qp[c], {RDMA_READ, 1, loc[c], 8, 8, lockWord, 8, 0, 0});
            else if (state[c] == 2) { uint64_t v = f.nodes[1 + c].load64(loc[c], 8) + 1; f.nodes[1 + c].store64(loc[c], 16, v); f.post(qp[c], {RDMA_WRITE, 2, loc[c], 16, 8, lockWord, 8, 0, 0}); }
            else { f.nodes[1 + c].store64(loc[c], 24, 0); f.post(qp[c], {RDMA_WRITE, 3, loc[c], 24, 8, lockWord, 0, 0, 0}); }
        };
        f.onComplete = [&](const Completion& cp) {
            int c = cp.qp; assert(cp.st == SUCCESS);
            if (state[c] == 0) { if (cp.old == 0) { state[c] = 1; } step(c); }                                  // CAS: 옛 값이 0 이면 락을 얻었다, 아니면 다시 시도(스핀)
            else if (state[c] == 1) { state[c] = 2; step(c); }
            else if (state[c] == 2) { if (useLock) { state[c] = 3; } else { ++done[c]; state[c] = 0; } step(c); }
            else { ++done[c]; state[c] = 0; step(c); }
        };
        for (int c = 0; c < C; ++c) step(c);
        f.run(); long total = (long)f.nodes[0].load64(lockWord, 8), want = (long)C * ITER; (useLock ? lostWithLock : lostWithout) = want - total;
        if (useLock) assert(f.nodes[0].load64(lockWord, 0) == 0);                                              // 끝나면 락이 풀려 있다
    }
    assert(lostWithLock == 0 && lostWithout > 0);                                                              // 락이 있으면 한 번도 안 잃고, 없으면 읽기-수정-쓰기가 서로 덮어쓴다
    // ⑤ SEND / RECV
    {   Fabric f(2, 6); int qp = f.connect(0, 1); Node& cli = f.nodes[0]; Node& srv = f.nodes[1]; uint32_t l = cli.reg(128, LOCAL_WRITE), rb = srv.reg(256, LOCAL_WRITE);
        const int R = 5, M = 8; for (int i = 0; i < R; ++i) srv.postRecv({rb, (size_t)i * 32, 32});
        for (int i = 0; i < M; ++i) { std::memset(cli.mem(l) + i * 16, 'a' + i, 16); f.post(qp, {SEND, (uint64_t)i, l, (size_t)i * 16, 16, 0, 0, 0, 0}); }       // 메시지마다 다른 칸 (전송은 나중에 일어난다)
        f.run(); auto& c = f.cq[qp]; int ok = 0, rnr = 0; for (auto& x : c) { ok += x.st == SUCCESS; rnr += x.st == RNR_ERR; }
        assert(ok == R && rnr == M - R && srv.cpuTouches == 2 * R);                                            // 받기 버퍼 5 개 -> 앞의 5 개만 성공, CPU 관여 == 올린 수 + 처리한 수
        for (int i = 0; i < R; ++i) assert(srv.mem(rb)[i * 32] == 'a' + i);                                      // 각자 다음 받기 버퍼에 순서대로
        Fabric g(2, 7); int q2 = g.connect(0, 1); uint32_t l2 = g.nodes[0].reg(64, LOCAL_WRITE), rb2 = g.nodes[1].reg(64, LOCAL_WRITE); g.nodes[1].postRecv({rb2, 0, 8});
        g.post(q2, {SEND, 1, l2, 0, 16, 0, 0, 0, 0}); g.run(); assert(g.cq[q2][0].st == LOC_LEN_ERR); }          // 받기 버퍼보다 큰 메시지
    std::cout << "RDMA verified: error codes, per-QP ordering with random delays, atomic FETCH_ADD uniqueness over 4000 operations, remote CAS lock (0 lost updates vs " << lostWithout << " without), SEND/RNR accounting." << std::endl;
    return 0;
}
// Time Complexity: 연산당 O(1) 검사 (NIC 가 처리), 시뮬레이션은 사건 수 · log
// Space Complexity: 등록한 영역 크기
```
## MemoryCompression()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <random>
#include <vector>
#include <cassert>

// 메모리 압축(zram, macOS 압축 메모리): 쫓겨날 페이지를 디스크 스왑 대신 RAM 안의 압축 풀에 저장한다.  디스크보다 수백 배 빠르고 RAM 을 아낀다.
// 0 으로 찬 페이지는 매우 흔해 특수 처리하고, 압축이 안 되는 페이지(난수, 이미 압축된 데이터)는 압축본이 더 크므로 원본 그대로 저장한다.
// 압축기는 간단한 LZ77: 이전에 나온 바이트열과 같으면 (거리, 길이) 로 대체한다
typedef std::vector<uint8_t> Bytes;
Bytes compress(const Bytes& in) {
    Bytes out; size_t i = 0;
    while (i < in.size()) {
        size_t bestLen = 0, bestDist = 0;
        for (size_t d = 1; d <= std::min<size_t>(i, 255); d++) {          // 뒤로 최대 255 바이트 내에서 가장 긴 일치를 찾는다
            size_t l = 0; while (i + l < in.size() && l < 255 && in[i + l] == in[i + l - d]) l++;
            if (l > bestLen) { bestLen = l; bestDist = d; }
        }
        if (bestLen >= 4) { out.push_back(1); out.push_back((uint8_t)bestDist); out.push_back((uint8_t)bestLen); i += bestLen; }   // 일치 토큰
        else { out.push_back(0); out.push_back(in[i]); i++; }                                                                      // 리터럴 토큰
    }
    return out;
}
Bytes decompress(const Bytes& c) {
    Bytes out;
    for (size_t i = 0; i < c.size();) {
        if (c[i] == 0) { out.push_back(c[i + 1]); i += 2; }
        else { size_t d = c[i + 1], l = c[i + 2]; for (size_t k = 0; k < l; k++) out.push_back(out[out.size() - d]); i += 3; }
    }
    return out;
}
struct Slot { bool raw; bool zero; Bytes data; };
Slot swapOut(const Bytes& page) {
    bool allZero = true; for (uint8_t b : page) if (b) { allZero = false; break; }
    if (allZero) return {false, true, {}};                                 // 0 페이지: 저장 공간 0 바이트
    Bytes c = compress(page);
    if (c.size() >= page.size()) return {true, false, page};              // 압축 이득이 없으면 원본 보관
    return {false, false, c};
}
Bytes swapIn(const Slot& s, size_t pageSize) { return s.zero ? Bytes(pageSize, 0) : s.raw ? s.data : decompress(s.data); }

int main() {
    const size_t PAGE = 4096; std::mt19937 rng(3);
    Bytes zero(PAGE, 0), text(PAGE), random(PAGE);
    for (size_t i = 0; i < PAGE; i++) { text[i] = "the quick brown fox "[i % 20]; random[i] = rng(); }
    Slot z = swapOut(zero), t = swapOut(text), r = swapOut(random);
    assert(z.zero && z.data.empty());                                      // 0 페이지는 공간 0
    assert(!t.raw && t.data.size() < PAGE / 10);                           // 반복되는 텍스트는 10배 이상 줄어든다
    assert(r.raw && r.data.size() == PAGE);                                // 난수 페이지는 압축 불가 -> 원본
    assert(swapIn(z, PAGE) == zero && swapIn(t, PAGE) == text && swapIn(r, PAGE) == random);   // 복원은 항상 정확
    std::cout << "MemoryCompression: text page " << PAGE << " -> " << t.data.size() << " bytes, zero page -> 0, random page stored raw" << std::endl;
    return 0;
}
// Time Complexity: 압축 O(n · 창 크기), 복원 O(n)
// Space Complexity: O(n)
```
# Part 16. 연구 주제
## GarbageFirstGC()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <vector>

// G1(Garbage-First): 힙을 같은 크기의 영역(region) 여러 개로 나누고, 영역별로 "얼마나 쓰레기인지" 를 추적한다.  수집할 때는 전체가 아니라 *회수 이득 / 복사 비용* 이 큰 영역부터 정지 시간 목표 안에 처리할 만큼만 골라(수집 집합, CSet) 살아 있는 객체를 새 영역으로 복사(evacuation)하고 옛 영역을 통째로 비운다.
// 전체 힙을 훑지 않고 CSet 만 옮기려면 "CSet 안의 객체를 가리키는 바깥 참조" 를 알아야 한다 — 영역마다 *기억 집합(remembered set)* 을 두고, 참조를 저장할 때마다(쓰기 배리어) 영역 경계를 넘는 참조를 기록한다.
//  ① 수집 집합 선택: 복사 예산 안에서 회수량 최대(0/1 배낭).  손으로 만든 예 {1,2,3} → 1 250KB 대 "쓰레기 양 우선" 650KB.  무작위 12 영역 1 500 개에서 DP 최적 == 2^12 부분집합 전수, 최적 ≥ 효율순 욕심쟁이(예산이 남으면 계속) ≥ 효율순 접두, 그리고 max(접두, 최고 단일) × 2 ≥ 최적(고전적 1/2 근사); 욕심쟁이가 최적이 *아닌* 사례 존재
//  ② 실제로 움직이는 미니 G1(영역 24 개, 영역당 512B, 객체 16~64B, 참조 2 칸): 무작위 변이 프로그램이 객체를 할당·연결·교체·루트 해제하다가 빈 영역이 모자라면 수집 — 수집 직전/직후의 *루트에서 도달 가능한 그래프의 정규 직렬화* 가 정확히 같고(내용·모양·공유·순환 보존), 루트에서 닿는 모든 참조가 살아 있는 칸을 가리키며 (죽은 객체의 낡은 참조는 정상: 표시 단계가 죽었다고 한 출처는 기억 집합에서도 무시), 비워진 영역에는 객체가 남지 않고, 회수량이 영역 사용량 − 복사량과 같음
//  ③ 음성 대조: 쓰기 배리어를 끄면 기억 집합이 비어 영역 밖 참조가 갱신되지 않아 같은 프로그램에서 *반드시* 깨진 참조·직렬화 불일치가 관찰됨
struct RegionStat { int id, liveKB, garbageKB; };
std::vector<int> pickCollectionSet(std::vector<RegionStat> regions, int budgetKB, bool skipAndContinue) {                                                                  // 효율순 욕심쟁이
    std::sort(regions.begin(), regions.end(), [](const RegionStat& a, const RegionStat& b) { return (double)a.garbageKB / (a.liveKB + 1) > (double)b.garbageKB / (b.liveKB + 1); });
    std::vector<int> chosen; int spent = 0;
    for (auto& r : regions) { if (r.garbageKB <= 0) continue; if (spent + r.liveKB <= budgetKB) { chosen.push_back(r.id); spent += r.liveKB; } else if (!skipAndContinue) break; }
    return chosen;
}
int reclaimed(const std::vector<RegionStat>& regions, const std::vector<int>& ids) { int s = 0; for (int id : ids) s += regions[id].garbageKB; return s; }
int optimalReclaim(const std::vector<RegionStat>& r, int budget) { std::vector<int> dp(budget + 1, 0); for (auto& x : r) for (int b = budget; b >= x.liveKB; --b) dp[b] = std::max(dp[b], dp[b - x.liveKB] + x.garbageKB); return dp[budget]; }   // 0/1 배낭 DP
int bruteReclaim(const std::vector<RegionStat>& r, int budget) { int best = 0; for (int mask = 0; mask < (1 << r.size()); ++mask) { int cost = 0, gain = 0; for (size_t i = 0; i < r.size(); ++i) if (mask >> i & 1) { cost += r[i].liveKB; gain += r[i].garbageKB; } if (cost <= budget) best = std::max(best, gain); } return best; }

struct Ref { int region = -1, slot = -1; bool null() const { return region < 0; } bool operator==(const Ref& o) const { return region == o.region && slot == o.slot; } };
struct Obj { int payload = 0, size = 0; Ref refs[2]; Ref fwd; };
struct Region { std::vector<Obj> objs; int used = 0; bool inUse = false; std::set<std::pair<int, int>> remset; };                                                     // remset: 이 영역을 가리키는 참조를 가진 (영역, 칸)
class MiniG1 {
public:
    static const int REGIONS = 24, CAP = 512, RESERVE = 6; bool barrier = true; std::vector<Ref> roots; long regionsFreed = 0, bytesReclaimed = 0, collections = 0;
    MiniG1() : reg(REGIONS) {}
    int freeCount() const { int c = 0; for (auto& r : reg) c += !r.inUse; return c; }
    Ref alloc(int payload, int size) { if (cur < 0 || reg[cur].used + size > CAP) { if (freeCount() <= RESERVE) return Ref(); cur = takeFree(); }
        Region& r = reg[cur]; Obj o; o.payload = payload; o.size = size; r.objs.push_back(o); r.used += size; return Ref{cur, (int)r.objs.size() - 1}; }
    Obj& at(Ref r) { return reg[r.region].objs[r.slot]; }
    void setRef(Ref src, int i, Ref dst) { at(src).refs[i] = dst; if (barrier && !dst.null() && dst.region != src.region) reg[dst.region].remset.insert({src.region, src.slot}); }   // 쓰기 배리어
    std::string serialize() { std::map<std::pair<int, int>, int> label; std::vector<Ref> queue; std::ostringstream out; auto visit = [&](Ref r) { if (r.null()) return -1; auto key = std::make_pair(r.region, r.slot); auto it = label.find(key); if (it != label.end()) return it->second; int id = (int)label.size(); label[key] = id; queue.push_back(r); return id; };
        for (Ref r : roots) out << 'R' << visit(r) << ' '; for (size_t i = 0; i < queue.size(); ++i) { Obj& o = at(queue[i]); out << '[' << o.payload << ',' << o.size << ',' << visit(o.refs[0]) << ',' << visit(o.refs[1]) << ']'; } return out.str(); }             // 방문 순서로 이름을 붙인 정규형
    bool validReachable() { std::set<std::pair<int, int>> seen; std::vector<Ref> work(roots); auto ok = [&](Ref x) { return x.null() || (x.region >= 0 && x.region < REGIONS && reg[x.region].inUse && x.slot >= 0 && x.slot < (int)reg[x.region].objs.size()); };   // 루트에서 닿는 모든 참조가 살아 있는 칸을 가리키는가
        while (!work.empty()) { Ref r = work.back(); work.pop_back(); if (!ok(r)) return false; if (r.null() || !seen.insert({r.region, r.slot}).second) continue; work.push_back(at(r).refs[0]); work.push_back(at(r).refs[1]); } return true; }
    bool emptyFreed() { for (auto& r : reg) if (!r.inUse && (!r.objs.empty() || r.used != 0 || !r.remset.empty())) return false; return true; }
    void collect(int budgetBytes) {
        std::vector<int> live(REGIONS, 0); std::set<std::pair<int, int>> seen; { std::vector<Ref> work(roots); while (!work.empty()) { Ref r = work.back(); work.pop_back(); if (r.null() || !seen.insert({r.region, r.slot}).second) continue; live[r.region] += at(r).size; work.push_back(at(r).refs[0]); work.push_back(at(r).refs[1]); } }   // 표시 단계: 영역별 생존 바이트
        std::vector<char> inCS(REGIONS, 0); std::vector<RegionStat> stats; for (int r = 0; r < REGIONS; ++r) if (reg[r].inUse && r != cur) stats.push_back({r, live[r], reg[r].used - live[r]});
        std::vector<int> others = pickCollectionSet(stats, budgetBytes, true); if (others.size() > 2) others.resize(2); for (int r : others) inCS[r] = 1; if (cur >= 0) inCS[cur] = 1;                    // 수집 집합 = 현재 할당 영역 + 효율 높은 영역(최대 2)
        int csetSize = 0; long usedInCSet = 0; for (int r = 0; r < REGIONS; ++r) if (inCS[r]) { ++csetSize; usedInCSet += reg[r].used; }
        int dest = -1; std::vector<int> toSpace; std::vector<Ref> scan;
        auto process = [&](Ref& r) { if (r.null() || !inCS[r.region]) return; Obj& o = at(r); if (o.fwd.null()) { Obj c = o; c.fwd = Ref(); if (dest < 0 || reg[dest].used + c.size > CAP) { dest = takeFree(); assert(dest >= 0); toSpace.push_back(dest); }
                reg[dest].objs.push_back(c); reg[dest].used += c.size; o.fwd = Ref{dest, (int)reg[dest].objs.size() - 1}; scan.push_back(o.fwd); } r = o.fwd; };                                       // 복사하고 옛 칸에 전달 주소를 남긴다
        for (Ref& r : roots) process(r);
        std::vector<std::pair<int, int>> sources; for (int c = 0; c < REGIONS; ++c) if (inCS[c]) for (auto& e : reg[c].remset) if (!inCS[e.first] && reg[e.first].inUse && e.second < (int)reg[e.first].objs.size() && seen.count(e)) sources.push_back(e);   // 기억 집합: 표시된(살아 있는) 출처의 바깥 참조만 — 죽은 출처는 무시
        for (auto& e : sources) for (Ref& x : reg[e.first].objs[e.second].refs) process(x);
        for (size_t i = 0; i < scan.size(); ++i) for (Ref& x : at(scan[i]).refs) process(x);
        long copied = 0; for (int d : toSpace) copied += reg[d].used;
        for (int r = 0; r < REGIONS; ++r) if (inCS[r]) { reg[r].objs.clear(); reg[r].used = 0; reg[r].inUse = false; reg[r].remset.clear(); ++regionsFreed; }                                       // 옛 영역을 통째로 비움
        for (auto& r : reg) for (auto it = r.remset.begin(); it != r.remset.end();) it = inCS[it->first] ? r.remset.erase(it) : std::next(it);                                      // 옮겨진 출처의 기록 제거
        for (auto& e : sources) for (Ref x : reg[e.first].objs[e.second].refs) if (!x.null() && x.region != e.first) reg[x.region].remset.insert(e);                                      // 갱신된 바깥 참조를 새 영역의 기억 집합에
        for (int d : toSpace) for (int s = 0; s < (int)reg[d].objs.size(); ++s) for (Ref x : reg[d].objs[s].refs) if (!x.null() && x.region != d) reg[x.region].remset.insert({d, s});          // 복사본이 가진 경계 참조
        bytesReclaimed += usedInCSet - copied; ++collections; cur = -1; (void)csetSize; lastCopied = copied; lastUsed = usedInCSet; }
    long lastCopied = 0, lastUsed = 0;
private:
    int takeFree() { for (int r = 0; r < REGIONS; ++r) if (!reg[r].inUse) { reg[r].inUse = true; reg[r].objs.clear(); reg[r].objs.reserve(CAP / 16 + 1); reg[r].used = 0; reg[r].remset.clear(); return r; } return -1; }     // reserve: 복사 중 참조가 무효화되지 않게
    std::vector<Region> reg; int cur = -1;
};
Ref walk(MiniG1& g, std::mt19937& rng) { if (g.roots.empty()) return Ref(); Ref r = g.roots[rng() % g.roots.size()]; for (int d = 0; d < 3; ++d) { if (rng() % 3 == 0) break; Ref n = g.at(r).refs[rng() % 2]; if (n.null()) break; r = n; } return r; }
struct RunResult { long collections = 0, regionsFreed = 0, reclaimed = 0; int brokenRuns = 0; bool ok = true; };
RunResult runProgram(unsigned seed, bool barrier, int steps) {
    std::mt19937 rng(seed); MiniG1 g; g.barrier = barrier; RunResult res; int payload = 0; const int sizes[4] = {16, 32, 48, 64};
    auto collectChecked = [&]() { std::string before = g.serialize(); g.collect(300); bool fine = g.validReachable() && g.emptyFreed() && g.lastCopied <= g.lastUsed && before == g.serialize(); if (!fine) res.ok = false; };           // 깨진 참조가 있으면 직렬화는 시도하지 않는다(&& 단락)
    for (int step = 0; step < steps && res.ok; ++step) { int op = (int)(rng() % 10);
        if (op < 6 || g.roots.empty()) { int sz = sizes[rng() % 4]; Ref n = g.alloc(payload++, sz); for (int tries = 0; n.null() && tries < 8 && res.ok; ++tries) { collectChecked(); if (res.ok) n = g.alloc(payload - 1, sz); } if (n.null()) { res.ok = false; break; }
            if (g.roots.size() < 4 && rng() % 4 == 0) g.roots.push_back(n); else if (g.roots.empty()) g.roots.push_back(n); else { Ref p = walk(g, rng); if (rng() % 8 == 0) g.roots[rng() % g.roots.size()] = n; else g.setRef(p, (int)(rng() % 2), n); } }       // 새 객체를 연결(옛 자식은 쓰레기)
        else if (op < 9) { Ref a = walk(g, rng), b = walk(g, rng); if (!a.null()) g.setRef(a, (int)(rng() % 2), b); }                                                         // 교차 연결(순환·공유 포함)
        else if (g.roots.size() > 1) g.roots.erase(g.roots.begin() + rng() % g.roots.size()); }
    res.collections = g.collections; res.regionsFreed = g.regionsFreed; res.reclaimed = g.bytesReclaimed; return res;
}

int main() {
    std::vector<RegionStat> heap = {{0, 350, 650}, {1, 100, 400}, {2, 100, 500}, {3, 150, 350}, {4, 900, 100}};                                                               // ① 손 계산 예
    auto g1 = pickCollectionSet(heap, 400, true); std::sort(g1.begin(), g1.end()); assert((g1 == std::vector<int>{1, 2, 3}));
    std::vector<RegionStat> byAmount = heap; std::sort(byAmount.begin(), byAmount.end(), [](const RegionStat& a, const RegionStat& b) { return a.garbageKB > b.garbageKB; }); std::vector<int> naive; int spent = 0; for (auto& r : byAmount) if (spent + r.liveKB <= 400) { naive.push_back(r.id); spent += r.liveKB; }
    assert((naive == std::vector<int>{0}) && reclaimed(heap, g1) == 1250 && reclaimed(heap, naive) == 650 && optimalReclaim(heap, 400) == 1250);
    std::mt19937 rng(8801); int greedyNotOptimal = 0;
    for (int trial = 0; trial < 1500; ++trial) { int R = 3 + (int)(rng() % 10), budget = 50 + (int)(rng() % 600); std::vector<RegionStat> rs; for (int i = 0; i < R; ++i) rs.push_back({i, 10 + (int)(rng() % 300), (int)(rng() % 500)});
        int opt = optimalReclaim(rs, budget); assert(opt == bruteReclaim(rs, budget)); int skip = reclaimed(rs, pickCollectionSet(rs, budget, true)), prefix = reclaimed(rs, pickCollectionSet(rs, budget, false)); int bestSingle = 0; for (auto& r : rs) if (r.liveKB <= budget) bestSingle = std::max(bestSingle, r.garbageKB);
        assert(opt >= skip && skip >= prefix && 2 * std::max(prefix, bestSingle) >= opt); if (skip < opt) ++greedyNotOptimal; }
    assert(greedyNotOptimal > 0);
    long collections = 0, freed = 0, reclaimedBytes = 0;
    for (unsigned seed = 1; seed <= 40; ++seed) { RunResult r = runProgram(seed, true, 6000); assert(r.ok && r.collections > 10); collections += r.collections; freed += r.regionsFreed; reclaimedBytes += r.reclaimed; }         // ② 올바른 G1
    int broken = 0; for (unsigned seed = 1; seed <= 20; ++seed) { RunResult r = runProgram(seed, false, 6000); if (!r.ok) ++broken; }                                           // ③ 배리어 없음
    assert(broken == 20);
    std::cout << "G1: collection set {1,2,3} reclaims 1250 KB vs 650 KB for garbage-amount-first (DP optimum equals brute force on 1500 instances; greedy missed the optimum in " << greedyNotOptimal << "); the evacuating mini-G1 survived 40 programs with " << collections << " collections, freeing " << freed << " regions and " << reclaimedBytes << " bytes, always preserving the rooted graph; without the write barrier all 20 programs corrupted" << std::endl;
    return 0;
}
// Time Complexity: 수집 O(CSet 생존 객체 + 기억 집합 항목), 선택 O(R log R)
// Space Complexity: O(영역 수 + 기억 집합)
```
## ZGC()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <vector>

// ZGC: 포인터 자체에 "색(color)" 메타데이터 비트를 넣고(colored pointers), 객체를 읽을 때마다 로드 장벽(load barrier)이 색을 검사한다.
// 객체를 이동(재배치)하는 동안에도 프로그램이 돌아가며, 오래된 포인터를 읽는 순간 장벽이 새 주소를 찾아 그 필드를 고쳐 쓴다(self-healing) -> 정지 시간이 힙 크기와 무관(밀리초 미만).
// 색 비트 하나(good color)를 전역으로 바꾸면 "모든 포인터가 낡은 것" 이 되고, 이후 각 포인터는 처음 읽힐 때 한 번씩만 느린 경로를 탄다
// 이 구현은 한 사이클 전체를 시뮬레이션한다 (스레드 없이, 뮤테이터 연산과 GC 단계를 무작위로 번갈아 실행):
//  페이지(8 칸) 단위 힙, 포인터 = (주소 << 4) | 색 {M0, M1, REMAP}.  사이클: ① 표시 시작(정지): good color 를 M0/M1 로 번갈아 바꾸고 루트를 표시  ② 동시 표시: GC 가 객체의 필드를 장벽으로 읽어 표시·치유,
//  뮤테이터도 읽을 때 표시  ③ 표시 끝(정지): 살아 있는 객체가 없는 페이지는 즉시 해제, 살아 있는 비율이 절반 미만인 페이지를 "재배치 집합" 으로 고르고 good color 를 REMAP 으로 바꿔 루트를 갱신
//  ④ 동시 재배치: GC 가 객체를 새 페이지로 옮기며 페이지별 전달 표에 기록, 뮤테이터도 낡은 포인터를 읽다가 아직 안 옮겨진 객체를 만나면 그 자리에서 옮긴다.  옛 페이지는 비워지지만 전달 표는 다음 표시가 끝날 때까지 유지
//  (다음 표시 단계가 모든 도달 가능한 필드를 치유하므로 그 뒤에는 낡은 포인터가 없다)
// 검증: 무작위 변경 6 000 번 × 8 시드: 뮤테이터는 루트에서 장벽을 거쳐 길을 따라가며 읽고 쓴다 — 매번 도착한 객체의 id 가 모형과 같다.  표시 끝마다 (a) 모형에서 도달 가능한 객체는 모두 표시됨 (b) 표시된 객체 ⊆ 시작 때 도달 가능 ∪ 사이클 중 새로 만든 것
//  (c) 도달 가능한 모든 필드가 good color 이고 해제된 페이지를 가리키지 않음 (치유 완료).  느린 경로 횟수 > 0, 빠른 경로가 훨씬 많음, 재배치로 페이지가 실제로 해제됨, GC 와 뮤테이터가 모두 객체를 옮겨 봄
typedef uint64_t Ptr;
const int SLOTS = 8;
enum { M0 = 1, M1 = 2, REMAP = 4 };
inline Ptr mk(uint32_t addr, int color) { return ((Ptr)(addr + 1) << 4) | (Ptr)color; }
inline uint32_t addrOf(Ptr p) { return (uint32_t)(p >> 4) - 1; }
inline int colorOf(Ptr p) { return (int)(p & 15); }

struct Obj { bool used = false, relocated = false; int id = 0, markEpoch = -1; Ptr refs[2] = {0, 0}; };
struct Page { Obj slots[SLOTS]; int top = 0, live = 0, pendingLive = 0; bool target = false, relocSet = false, retired = false, freed = false; std::map<int, uint32_t> fwd; };

struct ZHeap {
    std::vector<std::unique_ptr<Page>> pages; std::vector<Ptr> roots; std::vector<uint32_t> markStack; int goodColor = REMAP, epoch = 0, allocPage = -1, relocPage = -1;
    enum Phase { IDLE, MARKING, RELOCATING } phase = IDLE;
    long slow = 0, fast = 0, relocByGC = 0, relocByMutator = 0, pagesFreed = 0;
    Obj& at(uint32_t addr) { Page& p = *pages[addr / SLOTS]; assert(!p.freed); return p.slots[addr % SLOTS]; }
    uint32_t newSlot(bool forReloc) {
        int& cur = forReloc ? relocPage : allocPage;
        if (cur < 0 || pages[cur]->top == SLOTS) { if (cur >= 0) pages[cur]->target = false; pages.emplace_back(new Page()); cur = (int)pages.size() - 1; pages[cur]->target = true; }
        return (uint32_t)(cur * SLOTS + pages[cur]->top++);
    }
    void markObj(uint32_t addr) { Obj& o = at(addr); if (o.markEpoch != epoch) { o.markEpoch = epoch; ++pages[addr / SLOTS]->live; markStack.push_back(addr); } }
    uint32_t relocate(uint32_t addr, bool byMutator) {
        Page& p = *pages[addr / SLOTS]; uint32_t na = newSlot(true); Obj& o = at(addr); Obj& n = at(na);
        n = o; n.relocated = false; o.relocated = true; p.fwd[addr % SLOTS] = na; (byMutator ? relocByMutator : relocByGC)++;
        if (--p.pendingLive == 0) { p.retired = true; p.relocSet = false; }                // 다 옮겼다: 비워진 페이지 (전달 표는 유지)
        return na;
    }
    uint32_t forward(uint32_t addr) {
        Page& p = *pages[addr / SLOTS]; assert(!p.freed);
        if (!p.relocSet && !p.retired) return addr;
        auto it = p.fwd.find(addr % SLOTS); if (it != p.fwd.end()) return it->second;
        assert(p.relocSet); return relocate(addr, true);                                       // 아직 안 옮겨진 객체를 읽다가 만났다: 뮤테이터가 직접 옮긴다
    }
    Ptr heal(Ptr p) { uint32_t a = forward(addrOf(p)); if (phase == MARKING) markObj(a); return mk(a, goodColor); }
    Ptr load(Ptr* field) {                                                                      // 로드 장벽
        Ptr p = *field; if (!p) return 0;
        if (colorOf(p) == goodColor) { ++fast; return p; }
        ++slow; Ptr q = heal(p); *field = q; return q;                                           // 느린 경로 + 자기 치유
    }
    Ptr alloc(int id) {
        uint32_t a = newSlot(false); Obj& o = at(a); o = Obj(); o.used = true; o.id = id;
        if (phase == MARKING) { o.markEpoch = epoch; ++pages[a / SLOTS]->live; }               // 표시 중 할당 = 이미 표시됨
        return mk(a, goodColor);
    }
    void startMark() {
        assert(phase == IDLE); ++epoch; goodColor = (epoch % 2) ? M0 : M1; phase = MARKING;                    // 색을 바꾸는 순간 모든 기존 포인터가 낡은 것이 된다
        for (auto& p : pages) p->live = 0;                                                                      // 이전 사이클의 표시는 epoch 가 달라 자동으로 무효
        for (Ptr& r : roots) r = heal(r);                                                                       // 루트를 치유하며 표시
    }
    bool markStep(int budget) {                                                                 // 표시 스택을 budget 개 처리, 비었으면 true
        while (budget-- > 0 && !markStack.empty()) { uint32_t a = markStack.back(); markStack.pop_back(); Obj& o = at(a); for (int i = 0; i < 2; ++i) load(&o.refs[i]); }
        return markStack.empty();
    }
    template <class F> void forEachLive(F f) { for (size_t pi = 0; pi < pages.size(); ++pi) { Page& p = *pages[pi]; if (p.freed) continue; for (int s = 0; s < p.top; ++s) { Obj& o = p.slots[s]; if (o.used && !o.relocated && o.markEpoch == epoch) f((uint32_t)(pi * SLOTS + s), o); } } }
    void checkHealed() {                                                                        // 표시 끝: 도달 가능한 모든 필드는 good color 이고 해제된 페이지를 가리키지 않는다
        forEachLive([&](uint32_t, Obj& o) { for (int i = 0; i < 2; ++i) { Ptr p = o.refs[i]; if (!p) continue; assert(colorOf(p) == goodColor); Page& t = *pages[addrOf(p) / SLOTS]; assert(!t.freed && !t.retired && !t.relocSet); assert(at(addrOf(p)).used && at(addrOf(p)).markEpoch == epoch); } });
        for (Ptr r : roots) { assert(colorOf(r) == goodColor); }
    }
    void finishMark() {
        assert(phase == MARKING && markStack.empty()); checkHealed();
        for (auto& p : pages) {                                                                 // 이전 사이클에서 비워진 페이지와 산 객체가 없는 페이지를 해제
            if (p->freed) continue;
            if (p->retired || (p->live == 0 && !p->target)) { p->freed = true; p->fwd.clear(); ++pagesFreed; }
        }
        for (auto& p : pages) { if (!p->freed && !p->target && p->live > 0 && p->live < SLOTS / 2) { p->relocSet = true; p->pendingLive = p->live; p->fwd.clear(); } }   // 절반 미만만 산 페이지 = 재배치 집합
        goodColor = REMAP; phase = RELOCATING;
        for (Ptr& r : roots) r = heal(r);                                                       // 루트 갱신 (필요하면 그 자리에서 옮긴다)
        bool any = false; for (auto& p : pages) any |= (!p->freed && p->relocSet); if (!any) phase = IDLE;
    }
    bool relocStep(int budget) {                                                                // 재배치 집합에서 객체를 budget 개 옮긴다, 끝나면 true
        for (size_t pi = 0; pi < pages.size() && budget > 0; ++pi) {
            Page& p = *pages[pi]; if (!p.relocSet) continue;
            for (int s = 0; s < p.top && budget > 0 && p.relocSet; ++s) { Obj& o = p.slots[s]; if (o.used && !o.relocated && o.markEpoch == epoch && !p.fwd.count(s)) { relocate((uint32_t)(pi * SLOTS + s), false); --budget; } }
        }
        for (auto& p : pages) { if (!p->freed && p->relocSet) return false; }
        phase = IDLE; return true;
    }
};

struct Sim {
    ZHeap h; std::mt19937 rng; std::map<int, std::array<int, 2>> refs; std::vector<int> roots; int nextId = 1;
    long cycles = 0, loads = 0; std::set<int> s0, allocated;
    explicit Sim(uint32_t seed) : rng(seed) {}
    std::set<int> reachable() { std::set<int> seen; std::vector<int> st(roots.begin(), roots.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (x <= 0 || !seen.insert(x).second) continue; for (int c : refs[x]) st.push_back(c); } return seen; }
    bool pathTo(int target, int& root, std::vector<int>& path) {                                // 모형에서 루트부터 target 까지의 슬롯 열
        for (size_t r = 0; r < roots.size(); ++r) {
            std::map<int, std::pair<int, int>> parent; std::vector<int> q{roots[r]}; parent[roots[r]] = {0, -1};
            for (size_t i = 0; i < q.size(); ++i) { int x = q[i]; if (x == target) { path.clear(); for (int y = x; parent[y].first != 0; y = parent[y].first) path.push_back(parent[y].second); std::reverse(path.begin(), path.end()); root = (int)r; return true; }
                for (int k = 0; k < 2; ++k) { int c = refs[x][k]; if (c > 0 && !parent.count(c)) { parent[c] = {x, k}; q.push_back(c); } } }
        }
        return false;
    }
    Ptr fetch(int target) {                                                                      // 루트에서 장벽을 거쳐 길을 따라가 target 의 포인터를 얻는다
        int r; std::vector<int> path; bool ok = pathTo(target, r, path); assert(ok);
        Ptr p = h.load(&h.roots[r]); assert(h.at(addrOf(p)).id == roots[r]); int cur = roots[r]; ++loads;
        for (int k : path) { Ptr q = h.load(&h.at(addrOf(p)).refs[k]); cur = refs[cur][k]; assert(q && h.at(addrOf(q)).id == cur); p = q; ++loads; }
        assert(cur == target && colorOf(p) == h.goodColor); return p;
    }
    void verifyAll() {                                                                           // 모형 전체를 장벽으로 순회해 대조
        std::set<int> reach = reachable(); std::set<int> seen;
        for (int id : reach) { Ptr p = fetch(id); Obj& o = h.at(addrOf(p)); assert(o.id == id); for (int k = 0; k < 2; ++k) { Ptr c = h.load(&o.refs[k]); int cid = c ? h.at(addrOf(c)).id : 0; assert(cid == refs[id][k]); } seen.insert(id); }
        assert(seen == reach);
    }
    void endMark() {
        std::set<int> reach = reachable(); std::set<int> marked; h.forEachLive([&](uint32_t, Obj& o) { marked.insert(o.id); });
        for (int id : reach) assert(marked.count(id));                                            // (a) 도달 가능한 객체는 모두 표시
        for (int id : marked) assert(s0.count(id) || allocated.count(id));                         // (b) 표시된 객체 ⊆ 시작 때 도달 가능 ∪ 새로 만든 것
        h.finishMark(); ++cycles; verifyAll();                                                      // (c) finishMark 안에서 치유 완료도 검사
    }
    void drain() {
        if (h.phase == ZHeap::MARKING) { while (!h.markStep(100)) {} endMark(); }
        while (h.phase == ZHeap::RELOCATING) h.relocStep(100);
    }
    void gcStep() {
        int g = (int)(rng() % 100);
        if (h.phase == ZHeap::IDLE) { if (g < 6) { s0 = reachable(); allocated.clear(); h.startMark(); } }
        else if (h.phase == ZHeap::MARKING) {
            bool done = h.markStep(1 + (int)(rng() % 3));
            if (done && g < 50) endMark();
        } else { if (g < 70) h.relocStep(1 + (int)(rng() % 2)); }
    }
    void mutate() {
        std::set<int> reach = reachable(); std::vector<int> rl(reach.begin(), reach.end()); int op = (int)(rng() % 100);
        if (op < 40 || rl.empty()) {
            int id = nextId++; Ptr np = h.alloc(id); refs[id] = {0, 0}; if (h.phase == ZHeap::MARKING) allocated.insert(id);
            if ((rng() % 10 < 3 && roots.size() < 5) || rl.empty()) { if (roots.size() < 5) { roots.push_back(id); h.roots.push_back(np); } }
            else { int host = rl[rng() % rl.size()]; Ptr hp = fetch(host); int k = (int)(rng() % 2); h.at(addrOf(hp)).refs[k] = np; refs[host][k] = id; }
        } else if (op < 75) {
            int host = rl[rng() % rl.size()], tgt = rl[rng() % rl.size()]; int k = (int)(rng() % 2);
            Ptr hp = fetch(host); Ptr tp = (rng() % 6 == 0) ? 0 : fetch(tgt);
            h.at(addrOf(hp)).refs[k] = tp; refs[host][k] = tp ? tgt : 0;                         // 두 포인터 모두 방금 장벽을 거쳐 good color
        } else if (op < 85) { if (!roots.empty()) { size_t i = rng() % roots.size(); roots.erase(roots.begin() + i); h.roots.erase(h.roots.begin() + i); } }
        else if (op < 93) { if (roots.size() < 5) { int id = rl[rng() % rl.size()]; Ptr p = fetch(id); roots.push_back(id); h.roots.push_back(p); } }
        else { int id = rl[rng() % rl.size()]; Ptr p = fetch(id); assert(h.at(addrOf(p)).id == id); }
    }
};

int main() {
    // 원래 예: 낡은 포인터 두 개가 한 객체를 가리킨다 -> 재배치 -> 각각 처음 읽을 때 한 번씩만 느린 경로
    {   ZHeap h; Ptr h1 = h.alloc(1), h2 = h.alloc(2), a = h.alloc(3);
        for (int i = 0; i < 6; ++i) h.alloc(100 + i);                                              // 쓰레기 6 개: 첫 페이지(8 칸)에서 산 객체는 3 개뿐
        h.at(addrOf(h1)).refs[0] = a; h.at(addrOf(h2)).refs[0] = a; h.roots = {h1, h2};
        uint32_t oldAddr = addrOf(a); Ptr direct = h.alloc(9); assert(h.load(&direct) == direct && h.slow == 0 && h.fast == 1);   // 색이 맞으면 빠른 경로
        h.startMark(); while (!h.markStep(10)) {} h.finishMark();                                  // 표시 -> 첫 페이지가 재배치 집합이 되고 루트가 새 주소로
        assert(h.phase == ZHeap::RELOCATING && h.pages[0]->relocSet);
        Obj& n1 = h.at(addrOf(h.roots[0])); Obj& n2 = h.at(addrOf(h.roots[1])); long slow0 = h.slow;
        Ptr p1 = h.load(&n1.refs[0]);                                                              // 낡은 포인터(옛 주소 + 옛 색) -> 느린 경로: 새 주소를 얻고 필드를 고친다
        assert(h.slow == slow0 + 1 && h.at(addrOf(p1)).id == 3 && addrOf(p1) != oldAddr && colorOf(n1.refs[0]) == REMAP);
        assert(h.load(&n1.refs[0]) == p1 && h.slow == slow0 + 1);                                  // 다음부터는 빠른 경로
        assert(h.load(&n2.refs[0]) == p1 && h.slow == slow0 + 2);                                  // 다른 낡은 포인터도 처음 읽을 때 한 번만 느린 경로, 같은 새 객체
        assert(h.relocStep(1) && h.phase == ZHeap::IDLE);
    }
    // 무작위 시뮬레이션
    long cycles = 0, slow = 0, fast = 0, byGC = 0, byMut = 0, freed = 0, loads = 0, pagesMax = 0;
    for (uint32_t seed = 1; seed <= 8; ++seed) {
        Sim s(seed * 6151u);
        for (int step = 0; step < 6000; ++step) { s.mutate(); s.gcStep(); }
        s.drain();
        s.verifyAll();
        cycles += s.cycles; slow += s.h.slow; fast += s.h.fast; byGC += s.h.relocByGC; byMut += s.h.relocByMutator; freed += s.h.pagesFreed; loads += s.loads; pagesMax = std::max<long>(pagesMax, (long)s.h.pages.size());
    }
    assert(cycles > 40 && slow > 100 && fast > 4 * slow && byGC > 50 && byMut > 50 && freed > 50);
    std::cout << "ZGC verified: " << cycles << " cycles, " << loads << " barrier-checked loads (" << fast << " fast, " << slow << " slow/self-healing), " << byGC << " objects relocated by the GC and " << byMut
              << " by the mutator's barrier, " << freed << " pages freed." << std::endl;
    return 0;
}
// Time Complexity: 로드 장벽 빠른 경로 O(1) 비교, 느린 경로 O(1) 조회(+재배치 시 객체 복사), 정지 시간은 루트 수에 비례
// Space Complexity: 포인터 상위 비트 + 페이지별 전달 표 (다음 표시가 끝나면 해제)
```
## ShenandoahGC()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <thread>
#include <vector>

// Shenandoah: 모든 객체 앞에 Brooks 전달 포인터(forwarding pointer)를 둔다.  평소에는 자기 자신을 가리키고, 객체가 이동하면 새 사본을 가리킨다.
// 프로그램은 항상 "전달 포인터를 한 번 따라간 뒤" 읽고 쓰므로, GC 가 동시에 객체를 옮겨도 읽는 쪽과 쓰는 쪽이 같은 사본을 보게 된다.
// 이동은 CAS 로 전달 포인터를 바꾸는 쪽이 이기게 하여 여러 스레드가 동시에 같은 객체를 옮기려 해도 사본이 하나만 유효하다
// 이 구현의 쓰기 장벽: 수집 집합에 있고 아직 안 옮겨진 객체에 쓰려면 먼저 그 자리에서 옮긴다(evacuate-on-write) -> 옛 사본에는 쓰기가 일어나지 않으므로 GC 가 복사하는 동안 쓰기를 잃지 않는다.
//  사이클: 표시(정지) -> 수집 집합 선택 -> 동시 이동(GC 와 뮤테이터가 함께) -> 동시 참조 갱신(update-refs: 힙의 참조 칸을 전달 포인터를 따라 새 사본으로 고침) -> 루트 갱신(정지) -> 옛 사본 해제
// 검증: ① 잃어버린 쓰기의 결정적 재현: GC 가 사본을 뜬 직후 장벽 없는 쓰기가 들어오면 사라지고, 장벽이 있으면 살아남는다  ② 단일 스레드 시뮬레이션(무작위 변경 5 000 번 × 8 시드, GC 단계와 번갈아):
//        뮤테이터는 루트에서 전달 포인터를 따라 길을 걷고 값을 읽고 쓴다 — 도착한 객체의 id·값이 모형과 같고, 사이클이 끝나면 해제된 옛 사본을 가리키는 참조가 없음  ③ 진짜 스레드: 이동 스레드 4 개가 같은 2 000 개 객체를 서로 다른 순서로
//        동시에 옮기고 쓰기 스레드 4 개가 장벽을 거쳐 값을 증가 — CAS 에서 진 쪽은 사본을 버림: 객체마다 유효한 사본이 정확히 하나, 모든 스레드가 같은 사본을 보고, 증가분을 하나도 잃지 않으며, 사본 수 회계가 맞다(해제 후 0)
std::atomic<long> liveObjs{0};
struct Obj {
    std::atomic<Obj*> fwd; int id; std::atomic<int> value; Obj* refs[2]; bool inCset = false;
    explicit Obj(int i) : fwd(this), id(i), value(0) { refs[0] = refs[1] = nullptr; ++liveObjs; }
    Obj(const Obj& o) : fwd(this), id(o.id), value(o.value.load()) { refs[0] = o.refs[0]; refs[1] = o.refs[1]; ++liveObjs; }       // 사본: 전달 포인터는 자기 자신, 수집 집합에서는 빠진다
    ~Obj() { --liveObjs; }
};
inline Obj* resolve(Obj* o) { return o->fwd.load(); }                              // 읽기 장벽: 전달 포인터를 한 번 따라간다
Obj* evacuate(Obj* o) {                                                            // 사본을 만들고, 전달 포인터 CAS 에 성공한 쪽만 채택
    Obj* cur = o->fwd.load(); if (cur != o) return cur;                              // 이미 옮겨졌다
    Obj* copy = new Obj(*o); Obj* expected = o;
    if (o->fwd.compare_exchange_strong(expected, copy)) return copy;                 // 내가 이겼다
    delete copy; return expected;                                                    // 다른 스레드가 먼저 옮겼다: 그 사본을 쓰고 내 사본은 버린다
}
Obj* writeBarrier(Obj* o) { Obj* c = resolve(o); if (c->inCset && c->fwd.load() == c) c = evacuate(c); return c; }       // 수집 집합의 안 옮겨진 객체에 쓰려면 먼저 옮긴다

struct Heap {
    std::vector<Obj*> all, roots; enum Phase { IDLE, EVAC, UPDATE } phase = IDLE; std::vector<Obj*> cset, toUpdate; size_t evacPos = 0, updPos = 0; long evacByGC = 0, evacByMut = 0, stalePointerReads = 0, cycles = 0;
    Obj* alloc(int id) { Obj* o = new Obj(id); all.push_back(o); if (phase == UPDATE) toUpdate.push_back(o); return o; }       // 갱신 중 새 객체도 갱신 대상
    Obj* load(Obj* p) { Obj* r = resolve(p); if (r != p) ++stalePointerReads; return r; }       // 필드에서 읽은 포인터를 전달 포인터로 정규화
    Obj* wb(Obj* o) { Obj* before = resolve(o); Obj* c = writeBarrier(o); if (c != before) { all.push_back(c); ++evacByMut; } return c; }                 // 쓰기 장벽 (뮤테이터가 옮긴 사본도 힙에 등록)
    void store(Obj* host, int k, Obj* v) { Obj* h = wb(host); h->refs[k] = v ? resolve(v) : nullptr; }                                                      // 저장하는 값은 새 사본으로 정규화
    void startCycle(std::mt19937& rng) {                                                          // 표시(정지) + 수집 집합 선택
        std::set<Obj*> live; std::vector<Obj*> st; for (Obj* r : roots) st.push_back(resolve(r));
        while (!st.empty()) { Obj* o = st.back(); st.pop_back(); if (!live.insert(o).second) continue; for (Obj* c : o->refs) { if (c) st.push_back(resolve(c)); } }
        cset.clear();
        for (Obj* o : live) { if (rng() % 2) { o->inCset = true; cset.push_back(o); } }
        evacPos = updPos = 0; phase = EVAC; if (cset.empty()) beginUpdate();
    }
    void beginUpdate() { toUpdate.clear(); for (Obj* o : all) { if (o->fwd.load() == o) toUpdate.push_back(o); } phase = UPDATE; }      // 이동이 끝난 시점의 모든 유효 사본을 갱신 대상으로
    void finishCycle() {                                                                           // 루트 갱신(정지) -> 옛 사본 해제
        for (Obj*& r : roots) r = resolve(r);
        std::vector<Obj*> keep; for (Obj* o : all) { if (o->fwd.load() != o) delete o; else keep.push_back(o); }
        all.swap(keep); phase = IDLE; ++cycles;
    }
    void gcStep(int budget) {
        if (phase == EVAC) {
            while (budget-- > 0 && evacPos < cset.size()) { Obj* o = cset[evacPos++]; if (o->fwd.load() == o) { all.push_back(evacuate(o)); ++evacByGC; } }
            if (evacPos == cset.size()) beginUpdate();
        } else if (phase == UPDATE) {
            while (budget-- > 0 && updPos < toUpdate.size()) {
                Obj* o = resolve(toUpdate[updPos++]);                                              // 이 객체의 최신 사본의 참조 칸을 새 사본으로 갱신
                for (Obj*& c : o->refs) { if (c) c = resolve(c); }
            }
            if (updPos == toUpdate.size()) finishCycle();
        }
    }
};

int main() {
    // ① 잃어버린 쓰기의 결정적 재현
    {   Obj* o = new Obj(1); o->value = 10; o->inCset = true;
        Obj* c = new Obj(*o); o->value.store(99);                                    // GC 가 사본을 떴는데 (전달 포인터 설치 전) 장벽 없는 뮤테이터가 옛 객체에 쓴다
        Obj* e = o; assert(o->fwd.compare_exchange_strong(e, c)); assert(resolve(o)->value == 10);   // GC 가 설치: 쓰기 99 를 잃었다
        Obj* o2 = new Obj(2); o2->value = 10; o2->inCset = true;
        Obj* c2 = new Obj(*o2);                                                      // 같은 상황이지만 이번에는 장벽을 쓴다
        Obj* w = writeBarrier(o2); w->value.store(99);                               // 뮤테이터가 먼저 자기가 옮기고(CAS 성공) 새 사본에 쓴다
        Obj* e2 = o2; assert(!o2->fwd.compare_exchange_strong(e2, c2) && e2 == w);     // GC 의 CAS 는 실패
        delete c2; assert(resolve(o2)->value == 99 && resolve(o2) == w);
        delete o; delete c; delete o2; delete w;
    }
    // ② 단일 스레드 시뮬레이션
    long cycles = 0, evacGC = 0, evacMut = 0, stale = 0, ops = 0;
    for (uint32_t seed = 1; seed <= 8; ++seed) {
        Heap h; std::mt19937 rng(seed * 2711u); struct M { int value = 0; std::array<int, 2> refs{{0, 0}}; }; std::map<int, M> model; std::map<int, Obj*> handle; std::vector<int> rootIds; int nextId = 1;
        auto reachable = [&]() { std::set<int> seen; std::vector<int> st(rootIds.begin(), rootIds.end()); while (!st.empty()) { int x = st.back(); st.pop_back(); if (x <= 0 || !seen.insert(x).second) continue; for (int c : model[x].refs) st.push_back(c); } return seen; };
        auto fetch = [&](int target) -> Obj* {                                                  // 루트에서 전달 포인터를 따라 target 까지 걷는다 (모형의 BFS 경로)
            for (size_t r = 0; r < rootIds.size(); ++r) {
                std::map<int, std::pair<int, int>> parent; std::vector<int> q{rootIds[r]}; parent[rootIds[r]] = {0, -1};
                for (size_t i = 0; i < q.size(); ++i) {
                    int x = q[i];
                    if (x == target) {
                        std::vector<int> path; for (int y = x; parent[y].first != 0; y = parent[y].first) path.push_back(parent[y].second); std::reverse(path.begin(), path.end());
                        Obj* p = h.load(h.roots[r]); assert(p->id == rootIds[r]); int cur = rootIds[r];
                        for (int k : path) { p = h.load(p->refs[k]); cur = model[cur].refs[k]; assert(p && p->id == cur); }
                        return p;
                    }
                    for (int k = 0; k < 2; ++k) { int c = model[x].refs[k]; if (c > 0 && !parent.count(c)) { parent[c] = {x, k}; q.push_back(c); } }
                }
            }
            assert(false); return nullptr;
        };
        auto verifyAll = [&]() {
            std::set<int> reach = reachable(); std::set<Obj*> exist(h.all.begin(), h.all.end());
            for (int id : reach) { Obj* p = fetch(id); assert(p->id == id && p->value == model[id].value); for (int k = 0; k < 2; ++k) { Obj* c = p->refs[k]; assert((c ? resolve(c)->id : 0) == model[id].refs[k]); } }
            if (h.phase == Heap::IDLE) {                                                          // 사이클 밖: 해제된 옛 사본을 가리키는 참조가 없고 전달 포인터는 모두 자기 자신
                for (Obj* o : h.all) { assert(o->fwd.load() == o); for (Obj* c : o->refs) assert(!c || exist.count(c)); }
                for (Obj* r : h.roots) assert(exist.count(r));
            }
        };
        for (int step = 0; step < 5000; ++step) {
            ++ops; std::set<int> reach; std::vector<int> rl; { reach = reachable(); rl.assign(reach.begin(), reach.end()); } int op = (int)(rng() % 100);
            if (op < 35 || rl.empty()) {
                int id = nextId++; Obj* o = h.alloc(id); o->value = (int)(rng() % 1000); model[id].value = o->value;
                if ((rng() % 10 < 3 && rootIds.size() < 5) || rl.empty()) { if (rootIds.size() < 5) { rootIds.push_back(id); h.roots.push_back(o); } }
                else { int host = rl[rng() % rl.size()]; int k = (int)(rng() % 2); h.store(fetch(host), k, o); model[host].refs[k] = id; }
            } else if (op < 55) {
                int id = rl[rng() % rl.size()]; Obj* w = h.wb(fetch(id)); int v = (int)(rng() % 1000); w->value = v; model[id].value = v;          // 값 쓰기
            } else if (op < 75) {
                int id = rl[rng() % rl.size()]; Obj* p = fetch(id); assert(p->value == model[id].value);                                                 // 값 읽기
            } else if (op < 88) {
                int host = rl[rng() % rl.size()], tgt = rl[rng() % rl.size()]; int k = (int)(rng() % 2); Obj* hp = fetch(host); Obj* tp = (rng() % 6 == 0) ? nullptr : fetch(tgt);
                h.store(hp, k, tp); model[host].refs[k] = tp ? tgt : 0;
            } else if (op < 94) { if (!rootIds.empty()) { size_t i = rng() % rootIds.size(); rootIds.erase(rootIds.begin() + i); h.roots.erase(h.roots.begin() + i); } }
            else if (rootIds.size() < 5) { int id = rl[rng() % rl.size()]; Obj* p = fetch(id); rootIds.push_back(id); h.roots.push_back(p); }
            int g = (int)(rng() % 100);
            if (h.phase == Heap::IDLE) { if (g < 5) h.startCycle(rng); } else if (g < 60) { h.gcStep(1 + (int)(rng() % 3)); if (h.phase == Heap::IDLE) verifyAll(); }
            if (step % 250 == 0) verifyAll();
        }
        while (h.phase != Heap::IDLE) { h.gcStep(50); }
        verifyAll();
        cycles += h.cycles; evacGC += h.evacByGC; evacMut += h.evacByMut; stale += h.stalePointerReads;
        for (Obj* o : h.all) { delete o; }
        h.all.clear();
    }
    assert(cycles > 40 && evacGC > 200 && evacMut > 50 && stale > 100);
    // ③ 진짜 스레드: 같은 객체를 동시에 옮기는 경쟁
    {   const int N = 2000, TE = 4, TW = 4, ITER = 100000; std::vector<Obj*> heap(N); for (int i = 0; i < N; ++i) { heap[i] = new Obj(i); heap[i]->value = i; heap[i]->inCset = true; }
        std::vector<std::vector<Obj*>> seen(TE, std::vector<Obj*>(N, nullptr)); std::vector<std::vector<int>> counts(TW, std::vector<int>(N, 0)); std::vector<std::thread> ts;
        for (int t = 0; t < TE; ++t) ts.emplace_back([&, t] { std::vector<int> perm(N); for (int i = 0; i < N; ++i) perm[i] = i; std::mt19937 rng(100 + t); std::shuffle(perm.begin(), perm.end(), rng); for (int i : perm) seen[t][i] = evacuate(heap[i]); });
        for (int t = 0; t < TW; ++t) ts.emplace_back([&, t] { std::mt19937 rng(200 + t); for (int it = 0; it < ITER; ++it) { int i = (int)(rng() % N); writeBarrier(heap[i])->value.fetch_add(1); ++counts[t][i]; } });
        for (auto& th : ts) th.join();
        long totalInc = 0, winners = 0;
        for (int i = 0; i < N; ++i) {
            Obj* canon = resolve(heap[i]); assert(canon != heap[i] && canon->fwd.load() == canon && canon->id == i);   // 유효한 사본은 정확히 하나
            for (int t = 0; t < TE; ++t) assert(seen[t][i] == canon);                                                // 경쟁한 모든 스레드가 같은 사본을 본다
            long inc = 0; for (int t = 0; t < TW; ++t) inc += counts[t][i]; assert(canon->value.load() == i + inc);  // 증가분을 하나도 잃지 않았다
            totalInc += inc; ++winners;
        }
        assert(totalInc == (long)TW * ITER && winners == N && liveObjs.load() == 2 * N);                              // 졌던 사본은 모두 버려져 N 개의 원본 + N 개의 유효 사본만 남는다
        for (int i = 0; i < N; ++i) { delete resolve(heap[i]); delete heap[i]; }
        assert(liveObjs.load() == 0);
    }
    std::cout << "ShenandoahGC verified: lost-write interleaving reproduced and fixed; " << cycles << " simulated cycles over " << ops << " ops (" << evacGC << " evacuations by the GC, " << evacMut << " by write barriers, " << stale
              << " stale pointers resolved); 4 racing evacuators + 4 writers lost no update and kept exactly one copy per object." << std::endl;
    return 0;
}
// Time Complexity: 접근마다 포인터 한 번 더 (간접 참조 비용), 쓰기는 수집 집합 객체에 처음 쓸 때 복사 O(객체 크기)
// Space Complexity: 객체당 포인터 하나 (+ 이동 중에는 옛 사본과 새 사본)
```
## RegionBasedMemory()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <map>
#include <memory>
#include <new>
#include <random>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

// 리전 기반 메모리 관리(Tofte–Talpin): 객체를 개별로 해제하지 않고 "리전" 에 모아 두었다가 리전이 끝나는 순간 한꺼번에 해제한다.  리전은 스택처럼 중첩되어 만들어지고 역순으로 사라진다 → 개별 free 없음, 단편화 없음, GC 불필요.
// 구현: 리전은 4 KiB 덩어리(chunk)를 범프 포인터로 쪼개 주고(정렬 맞춤), 소멸자가 필요한 객체는 등록해 두었다가 리전이 닫힐 때 *만든 역순* 으로 부른다.  덩어리는 전역 풀(최대 64 개)에서 빌리고 돌려준다.  너무 큰 요청(2 KiB 초과)은 전용 덩어리.
//  ① 16 바이트 객체 10 만 개: 덩어리 요청은 정확히 ⌈100000/256⌉ = 391 번(객체마다 new 하는 쪽은 10 만 번)이고 리전을 닫으면 모두 돌아와 두 번째 리전은 풀 64 개를 재사용  ② 무작위 (크기, 정렬 1..64) 5 만 개: 포인터는 항상 정렬되고 서로 겹치지 않으며(주소순 정렬 후 인접 검사) 중첩 리전을 닫은 뒤에도 바깥 리전 데이터는 그대로
//  ③ 소멸자 호출 순서 = 생성 역순이고 정확히 한 번씩, 생성자가 예외를 던져도 리전은 일관됨  ④ 안쪽보다 먼저 바깥을 닫으려는 시도는 거부되고 아무것도 바꾸지 않음  ⑤ "참조가 리전보다 오래 살지 않는다" 판정을, 무작위 중첩 프로그램의 *실제 소멸 시각* 순서와 대조  ⑥ 요청마다 50 KB 를 쓰는 서버 루프 2 000 회: 덩어리 할당 횟수가 늘지 않음(누수 없음)
struct ChunkPool {
    static const size_t CHUNK = 4096; static std::vector<char*> freeList; static long mallocs, frees, live;
    static char* get() { ++live; if (!freeList.empty()) { char* c = freeList.back(); freeList.pop_back(); return c; } ++mallocs; return (char*)std::malloc(CHUNK); }
    static void put(char* c) { --live; if (freeList.size() < 64) freeList.push_back(c); else { ++frees; std::free(c); } }
    static void trim() { for (char* c : freeList) { ++frees; std::free(c); } freeList.clear(); }
};
std::vector<char*> ChunkPool::freeList; long ChunkPool::mallocs = 0, ChunkPool::frees = 0, ChunkPool::live = 0;

class Region {
public:
    static Region* top;
    Region() : parent_(top), depth_(top ? top->depth_ + 1 : 0) { top = this; }
    ~Region() { bool ok = close(); assert(ok); }
    Region(const Region&) = delete; Region& operator=(const Region&) = delete;
    void* allocate(size_t n, size_t align) { assert(!closed_ && (align & (align - 1)) == 0);
        if (n + align > ChunkPool::CHUNK / 2) { char* b = (char*)std::malloc(n + align); bigs_.push_back(b); return (void*)(((uintptr_t)b + align - 1) & ~(uintptr_t)(align - 1)); }      // 큰 요청은 전용 덩어리
        uintptr_t p = ((uintptr_t)cur_ + align - 1) & ~(uintptr_t)(align - 1);
        if (cur_ == nullptr || p + n > (uintptr_t)end_) { cur_ = ChunkPool::get(); end_ = cur_ + ChunkPool::CHUNK; chunks_.push_back(cur_); p = ((uintptr_t)cur_ + align - 1) & ~(uintptr_t)(align - 1); }   // 현재 덩어리가 모자라면 새 덩어리
        cur_ = (char*)(p + n); return (void*)p; }
    template <class T, class... A> T* make(A&&... a) { void* p = allocate(sizeof(T), alignof(T)); T* o = new (p) T(std::forward<A>(a)...);                                    // 생성자가 던지면 등록하지 않는다
        if (!std::is_trivially_destructible<T>::value) dtors_.push_back({o, [](void* q) { static_cast<T*>(q)->~T(); }}); return o; }
    bool close() { if (closed_) return true; if (top != this) return false;                                                                                                       // 안쪽이 살아 있으면 거부
        for (size_t i = dtors_.size(); i-- > 0;) dtors_[i].fn(dtors_[i].obj); dtors_.clear(); for (char* c : chunks_) ChunkPool::put(c); for (char* b : bigs_) std::free(b); chunks_.clear(); bigs_.clear(); top = parent_; closed_ = true; return true; }
    static bool outlives(const Region& longer, const Region& shorter) { for (const Region* r = &shorter; r; r = r->parent_) if (r == &longer) return true; return false; }              // longer 가 shorter 의 조상(또는 자신)인가
    size_t chunkCount() const { return chunks_.size(); }
private:
    struct Dtor { void* obj; void (*fn)(void*); };
    Region* parent_; int depth_; bool closed_ = false; char* cur_ = nullptr; char* end_ = nullptr; std::vector<char*> chunks_, bigs_; std::vector<Dtor> dtors_;
};
Region* Region::top = nullptr;
struct Log { static std::vector<int> destroyed; int id; explicit Log(int i) : id(i) {} ~Log() { destroyed.push_back(id); } }; std::vector<int> Log::destroyed;
struct Thrower { explicit Thrower(int x) { if (x < 0) throw std::runtime_error("ctor failed"); } };
struct Item16 { uint64_t a, b; };

int main() {
    {   long m0 = ChunkPool::mallocs; { Region r; for (int i = 0; i < 100000; ++i) r.make<Item16>(Item16{(uint64_t)i, 0}); assert(r.chunkCount() == 391 && ChunkPool::mallocs - m0 == 391 && ChunkPool::live == 391); }              // ① 덩어리 요청 횟수
        assert(ChunkPool::live == 0 && ChunkPool::freeList.size() == 64 && ChunkPool::frees == 391 - 64);
        long m1 = ChunkPool::mallocs; { Region r; for (int i = 0; i < 64 * 256; ++i) r.make<Item16>(Item16{1, 2}); } assert(ChunkPool::mallocs == m1); }                                                    // 풀 64 개 재사용: 새 할당 0
    {   std::mt19937 rng(606); Region outer; struct Rec { uintptr_t p; size_t n; uint8_t fill; }; std::vector<Rec> recs, innerRecs;                                                          // ②
        for (int i = 0; i < 25000; ++i) { size_t align = (size_t)1 << (rng() % 7), n = 1 + rng() % 200; if (rng() % 500 == 0) n = 2000 + rng() % 5000; void* p = outer.allocate(n, align); assert((uintptr_t)p % align == 0); std::memset(p, (int)(i & 0xFF), n); recs.push_back({(uintptr_t)p, n, (uint8_t)(i & 0xFF)}); }
        { Region inner; for (int i = 0; i < 25000; ++i) { size_t align = (size_t)1 << (rng() % 7), n = 1 + rng() % 200; void* p = inner.allocate(n, align); assert((uintptr_t)p % align == 0); std::memset(p, (int)((i + 7) & 0xFF), n); innerRecs.push_back({(uintptr_t)p, n, (uint8_t)((i + 7) & 0xFF)}); }
          std::vector<Rec> all = recs; all.insert(all.end(), innerRecs.begin(), innerRecs.end()); std::sort(all.begin(), all.end(), [](const Rec& a, const Rec& b) { return a.p < b.p; }); for (size_t i = 1; i < all.size(); ++i) assert(all[i - 1].p + all[i - 1].n <= all[i].p);     // 겹침 없음
          for (auto& r : innerRecs) for (size_t k = 0; k < r.n; ++k) assert(((uint8_t*)r.p)[k] == r.fill); }
        for (auto& r : recs) for (size_t k = 0; k < r.n; ++k) assert(((uint8_t*)r.p)[k] == r.fill); }                                                                                              // 안쪽을 닫아도 바깥은 그대로
    {   Log::destroyed.clear(); { Region r; for (int i = 0; i < 100; ++i) { r.make<Log>(i); r.make<int>(i); } bool threw = false; try { r.make<Thrower>(-1); } catch (const std::runtime_error&) { threw = true; } assert(threw); r.make<Log>(100); assert(Log::destroyed.empty()); }   // ③
        assert(Log::destroyed.size() == 101); for (int i = 0; i < 101; ++i) assert(Log::destroyed[i] == 100 - i); }
    {   Region outer; Region* innerPtr = new Region; int* inner = innerPtr->make<int>(5); assert(!outer.close() && *inner == 5); assert(Region::top == innerPtr);                                         // ④ 거꾸로 닫기 거부
        assert(innerPtr->close() && outer.close() && outer.close()); delete innerPtr; assert(Region::top == nullptr); }
    for (unsigned seed = 1; seed <= 30; ++seed) {                                                                                                                                              // ⑤ 수명 순서 오라클
        std::mt19937 rng(seed); std::vector<std::unique_ptr<Region>> stack; std::vector<int> ids; int nextId = 0, clock = 0; std::map<int, int> death; struct Pair { int holder, target; bool predicted; }; std::vector<Pair> checks;
        for (int step = 0; step < 400; ++step) { if (stack.empty() || (stack.size() < 12 && rng() % 2)) { stack.emplace_back(new Region); ids.push_back(nextId++); } else { death[ids.back()] = clock++; bool ok = stack.back()->close(); assert(ok); stack.pop_back(); ids.pop_back(); }
            if (stack.size() >= 2 && rng() % 3 == 0) { size_t h = rng() % stack.size(), t = rng() % stack.size(); checks.push_back({ids[h], ids[t], Region::outlives(*stack[t], *stack[h])}); } }
        while (!stack.empty()) { death[ids.back()] = clock++; stack.pop_back(); ids.pop_back(); }
        for (auto& c : checks) assert(c.predicted == (c.holder == c.target || death[c.target] > death[c.holder])); }                                                                            // 오래 사는 쪽이 나중에 죽는다
    {   long before = ChunkPool::mallocs; Region longLived; longLived.make<int>(1); for (int req = 0; req < 2000; ++req) { Region request; for (int i = 0; i < 50; ++i) request.allocate(1000, 8); } assert(ChunkPool::mallocs - before <= 13 && ChunkPool::live == 1); }   // ⑥ 서버 루프
    assert(ChunkPool::live == 0); ChunkPool::trim(); assert(ChunkPool::mallocs == ChunkPool::frees);                                                                                          // 풀을 비우면 짝이 맞는다(누수 0)
    std::cout << "RegionBasedMemory: 100000 objects needed 391 chunk requests instead of 100000 allocations; 50000 random aligned allocations never overlapped; destructors ran exactly once in reverse order; out-of-order close was refused; the outlives check matched real destruction order in 30 random programs; a 2000-request loop reused its chunks" << std::endl;
    return 0;
}
// Time Complexity: 할당 O(1), 닫기 O(등록된 소멸자 + 덩어리 수)
// Space Complexity: O(요청 합 + 덩어리 내부 조각)
```
## EscapeAnalysis()
### 대표코드
```cpp
#include <array>
#include <cassert>
#include <deque>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// 탈출 분석(escape analysis): 객체가 만들어진 함수 밖으로 "빠져나가는가" 를 컴파일 시점에 분석한다.  빠져나가지 않으면 힙 대신 스택에 두거나(스택 할당),
// 필드를 지역 변수로 쪼개 객체 자체를 없앨 수 있다(스칼라 치환) -> GC 부담 제거.  JVM(HotSpot), Go, V8 이 사용
// 작은 중간 표현(변수 5 개, 전역 2 개, 객체마다 참조 필드 2 개와 정수 값 1 개, 반복문)에서 분석을 직접 구현한다.  탈출 조건: (1) 반환됨 (2) 전역에 저장됨 (3) 이미 탈출하는 객체의 필드에 저장됨(전이적으로)
//  분석은 흐름 무관(flow-insensitive) 포인트-투 분석: 변수·필드·전역이 가리킬 수 있는 "할당 위치(site)" 의 집합을 고정점까지 전파하고, 전역·반환값이 가리키는 site 에서 필드를 따라 닫는다
// 검증: 무작위 프로그램 20 000 개를 두 가지 방식으로 실행해 분석을 정확성으로 대조한다 —
//  ① 동적 기준: 실행하면서 "실제로 탈출한 객체" 를 추적(전역 저장·반환 시 도달 가능한 객체 전부, 탈출한 객체의 필드에 저장될 때) -> 분석이 NoEscape 라 한 site 에서 실제 탈출이 한 번도 없어야 한다(건전성)
//  ② 최적화 실행: NoEscape site 의 객체는 "스택"(함수가 끝나면 사라지는 영역)에 만들고 힙 할당 횟수를 센다 -> 출력(값 합계, 반환값·전역이 가리키는 객체 그래프)이 일반 실행과 같고, 끝났을 때 전역·반환값에서 스택 객체로 가는 참조(댕글링)가 0
//  ③ 필드 폐포 규칙을 뺀 틀린 분석은 이 시험에서 건전성 위반이 나온다(규칙의 필요성), ④ 손으로 짠 6 개 프로그램의 판정
enum Op { NEW, MOVE, STORE, LOAD, GSTORE, GLOAD, SETVAL, ADDVAL, RET, LOOP, ENDLOOP };
struct Stmt { Op op; int a = 0, b = 0, c = 0; };      // NEW a / MOVE a,b / STORE a.f(c)=b / LOAD a=b.f(c) / GSTORE G[a]=v[b] / GLOAD v[a]=G[b] / SETVAL v[a].val=c / ADDVAL acc+=v[b].val / RET v[a] / LOOP c 번 / ENDLOOP
typedef std::vector<Stmt> Prog;
const int NV = 5, NG = 2;

struct Analysis { std::vector<std::set<int>> pts, gpts; std::map<int, std::array<std::set<int>, 2>> fld; std::set<int> esc, sites; };
bool addAll(std::set<int>& dst, const std::set<int>& src) { size_t n = dst.size(); dst.insert(src.begin(), src.end()); return dst.size() != n; }
Analysis analyze(const Prog& p, bool closure = true) {
    Analysis A; A.pts.assign(NV, {}); A.gpts.assign(NG, {}); int retVar = -1;
    for (size_t i = 0; i < p.size(); ++i) { if (p[i].op == NEW) { A.sites.insert((int)i); A.fld[(int)i]; } if (p[i].op == RET) retVar = p[i].a; }
    for (bool changed = true; changed;) {                                                    // 고정점 반복
        changed = false;
        for (size_t i = 0; i < p.size(); ++i) {
            const Stmt& s = p[i];
            switch (s.op) {
                case NEW: changed |= A.pts[s.a].insert((int)i).second; break;
                case MOVE: changed |= addAll(A.pts[s.a], A.pts[s.b]); break;
                case STORE: for (int site : A.pts[s.a]) changed |= addAll(A.fld[site][s.c], A.pts[s.b]); break;
                case LOAD: for (int site : A.pts[s.b]) changed |= addAll(A.pts[s.a], A.fld[site][s.c]); break;
                case GSTORE: changed |= addAll(A.gpts[s.a], A.pts[s.b]); break;
                case GLOAD: changed |= addAll(A.pts[s.a], A.gpts[s.b]); break;
                default: break;
            }
        }
    }
    for (int g = 0; g < NG; ++g) A.esc.insert(A.gpts[g].begin(), A.gpts[g].end());           // 전역에 저장된 것
    if (retVar >= 0) A.esc.insert(A.pts[retVar].begin(), A.pts[retVar].end());                // 반환되는 것
    if (closure) { for (bool changed = true; changed;) { changed = false; for (int s : std::set<int>(A.esc)) for (int f = 0; f < 2; ++f) changed |= addAll(A.esc, A.fld[s][f]); } }   // 탈출하는 객체의 필드가 가리키는 것도 탈출
    return A;
}

struct Inst { int site; int val = 0; Inst* f[2] = {nullptr, nullptr}; bool onStack = false, escaped = false; };
struct Result { long heapAllocs = 0, stackAllocs = 0, dangling = 0; std::string out; std::set<int> dynEsc; };
std::string serialize(Inst* o, std::map<Inst*, int>& num) {                                  // 도달 가능한 그래프를 방문 순서로 번호 매겨 직렬화
    if (!o) return "-";
    auto it = num.find(o); if (it != num.end()) return "#" + std::to_string(it->second);
    int id = (int)num.size(); num[o] = id; return "(" + std::to_string(o->val) + " " + serialize(o->f[0], num) + " " + serialize(o->f[1], num) + ")";
}
Result execute(const Prog& p, const std::set<int>* stackSites) {                              // stackSites 가 있으면 그 site 의 객체는 스택에 만든다
    Result R; std::deque<Inst> pool; Inst* v[NV] = {}; Inst* G[NG] = {}; Inst* ret = nullptr; long acc = 0; std::vector<std::pair<size_t, int>> loops;
    auto markEscaped = [&](Inst* o) { std::vector<Inst*> st{o}; while (!st.empty()) { Inst* x = st.back(); st.pop_back(); if (!x || x->escaped) continue; x->escaped = true; R.dynEsc.insert(x->site); st.push_back(x->f[0]); st.push_back(x->f[1]); } };
    for (size_t pc = 0; pc < p.size(); ++pc) {
        const Stmt& s = p[pc];
        switch (s.op) {
            case NEW: { pool.emplace_back(); Inst* o = &pool.back(); o->site = (int)pc; if (stackSites && stackSites->count((int)pc)) { o->onStack = true; ++R.stackAllocs; } else ++R.heapAllocs; v[s.a] = o; break; }
            case MOVE: v[s.a] = v[s.b]; break;
            case STORE: if (v[s.a]) { v[s.a]->f[s.c] = v[s.b]; if (v[s.a]->escaped) markEscaped(v[s.b]); } break;
            case LOAD: v[s.a] = v[s.b] ? v[s.b]->f[s.c] : nullptr; break;
            case GSTORE: G[s.a] = v[s.b]; markEscaped(v[s.b]); break;
            case GLOAD: v[s.a] = G[s.b]; break;
            case SETVAL: if (v[s.a]) v[s.a]->val = s.c; break;
            case ADDVAL: if (v[s.b]) acc += v[s.b]->val; break;
            case RET: ret = v[s.a]; markEscaped(ret); pc = p.size(); break;
            case LOOP: loops.push_back({pc, s.c}); break;
            case ENDLOOP: if (--loops.back().second > 0) pc = loops.back().first; else loops.pop_back(); break;
        }
    }
    std::map<Inst*, int> num; R.out = std::to_string(acc) + "|" + serialize(ret, num) + "|" + serialize(G[0], num) + "|" + serialize(G[1], num);
    std::set<Inst*> seen; std::vector<Inst*> st{ret, G[0], G[1]};                            // 끝났을 때 전역·반환값에서 스택 객체로 가는 참조 = 댕글링
    while (!st.empty()) { Inst* x = st.back(); st.pop_back(); if (!x || !seen.insert(x).second) continue; if (x->onStack) ++R.dangling; st.push_back(x->f[0]); st.push_back(x->f[1]); }
    return R;
}

Prog randomProgram(std::mt19937& rng) {
    Prog p; int n = 6 + (int)(rng() % 18);
    for (int i = 0; i < n; ++i) {
        int r = (int)(rng() % 100); Stmt s;
        if (r < 22) s = {NEW, (int)(rng() % NV)}; else if (r < 34) s = {MOVE, (int)(rng() % NV), (int)(rng() % NV)}; else if (r < 50) s = {STORE, (int)(rng() % NV), (int)(rng() % NV), (int)(rng() % 2)};
        else if (r < 62) s = {LOAD, (int)(rng() % NV), (int)(rng() % NV), (int)(rng() % 2)}; else if (r < 68) s = {GSTORE, (int)(rng() % NG), (int)(rng() % NV)}; else if (r < 74) s = {GLOAD, (int)(rng() % NV), (int)(rng() % NG)};
        else if (r < 86) s = {SETVAL, (int)(rng() % NV), 0, 1 + (int)(rng() % 9)}; else s = {ADDVAL, 0, (int)(rng() % NV)};
        p.push_back(s);
    }
    if (rng() % 100 < 40) { size_t i = rng() % p.size(), j = i + 1 + rng() % (p.size() - i); p.insert(p.begin() + j, Stmt{ENDLOOP}); p.insert(p.begin() + i, Stmt{LOOP, 0, 0, 2 + (int)(rng() % 3)}); }
    p.push_back({RET, (int)(rng() % NV)}); return p;
}

int main() {
    // ④ 손으로 짠 프로그램 (v0 = p, v1 = q, v2 = r)
    {   auto esc = [](const Prog& p) { return analyze(p).esc; };
        Prog a = {{NEW, 0}, {STORE, 0, 0, 0}, {RET, 4}};                                                 // p = new; p.f = p; (아무것도 반환 안 함)
        assert(esc(a).empty());
        assert((esc({{NEW, 0}, {RET, 0}}) == std::set<int>{0}));                                          // 반환되는 객체는 탈출
        assert((esc({{NEW, 1}, {NEW, 0}, {STORE, 0, 1, 0}, {RET, 0}}) == std::set<int>{0, 1}));            // q 를 탈출하는 p 의 필드에 저장 -> q 도 탈출
        assert(esc({{NEW, 1}, {NEW, 0}, {STORE, 0, 1, 0}, {RET, 4}}).empty());                             // 둘 다 지역에서만 연결되면 탈출 없음
        assert((esc({{NEW, 0}, {MOVE, 2, 0}, {RET, 2}}) == std::set<int>{0}));                             // 별칭을 통한 탈출: r = p; return r
        assert((esc({{NEW, 0}, {GSTORE, 0, 0}, {RET, 4}}) == std::set<int>{0}));                           // 전역에 저장하면 탈출
        assert((esc({{NEW, 0}, {NEW, 1}, {STORE, 0, 1, 1}, {GSTORE, 1, 0}, {RET, 4}}) == std::set<int>{0, 1}));   // 전역에 간 객체의 필드에 있는 것도 탈출
    }
    // ①②③ 무작위 프로그램
    std::mt19937 rng(20240501); long programs = 0, sites = 0, noEscSites = 0, heapBefore = 0, heapAfter = 0, stackAllocs = 0, wrongClosureViolations = 0, loopPrograms = 0;
    for (int it = 0; it < 20000; ++it) {
        Prog p = randomProgram(rng); Analysis A = analyze(p), B = analyze(p, false);
        std::set<int> noEsc; for (int s : A.sites) { if (!A.esc.count(s)) noEsc.insert(s); }
        Result plain = execute(p, nullptr), opt = execute(p, &noEsc);
        for (int s : plain.dynEsc) assert(A.esc.count(s));                                                  // ① 건전성: 실제로 탈출한 site 는 모두 분석이 탈출이라 했다
        assert(plain.out == opt.out && opt.dangling == 0);                                                   // ② 최적화해도 결과가 같고 댕글링이 없다
        assert(opt.heapAllocs + opt.stackAllocs == plain.heapAllocs && opt.heapAllocs <= plain.heapAllocs);
        bool wrong = false; for (int s : plain.dynEsc) { if (!B.esc.count(s)) wrong = true; } if (wrong) ++wrongClosureViolations;     // ③ 폐포 규칙이 없으면 위반
        ++programs; sites += (long)A.sites.size(); noEscSites += (long)noEsc.size(); heapBefore += plain.heapAllocs; heapAfter += opt.heapAllocs; stackAllocs += opt.stackAllocs;
        for (const Stmt& s : p) { if (s.op == LOOP) { ++loopPrograms; break; } }
    }
    assert(wrongClosureViolations > 50 && noEscSites * 4 > sites && stackAllocs > 10000 && loopPrograms > 5000);
    std::cout << "EscapeAnalysis verified: " << programs << " random programs sound (0 escapes missed), outputs identical after moving " << stackAllocs << "/" << heapBefore << " allocations to the stack ("
              << noEscSites << "/" << sites << " sites proven non-escaping); without the field-closure rule " << wrongClosureViolations << " programs break." << std::endl;
    return 0;
}
// Time Complexity: 고정점 반복 O(반복 · 문장 수 · site 수)
// Space Complexity: O(변수 · site 수)
```
## OwnershipTypeSystem()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

// 소유권 타입 시스템(Rust): (1) 값의 소유자는 하나  (2) 소유권이 이동(move)하면 원래 변수는 사용 불가  (3) 빌림(borrow) 규칙: 읽기 참조는 여러 개 OR 쓰기 참조는 정확히 한 개 (동시에는 불가)
// -> 데이터 경쟁과 댕글링 참조를 컴파일 시점에 막는다.  Rust 는 컴파일러가 하지만, 여기서는 같은 규칙을 두 가지로 구현한다:
//  (A) 런타임 검사 Owned<T> (RefCell 과 비슷): 위반하는 순간 예외  (B) 작은 언어의 "빌림 검사기": 정적 분석(참조의 마지막 사용까지만 빌림이 살아 있다는 NLL 방식의 생존 구간 + 접근과 충돌 검사)
//  (C) 같은 프로그램을 앞에서부터 실행하며 "소유자에 접근하면 충돌하는 참조를 무효화하고, 무효화된 참조를 쓰면 오류" 로 판정하는 동적 검사기 (Stacked Borrows 와 비슷한 발상)
// 검증: 무작위 프로그램 30 000 개에서 정적 검사기(B)와 동적 검사기(C)가 (1) 통과/거부가 항상 같고 (2) 거부할 때 첫 오류가 일어나는 문장 번호까지 같다 — 서로 다른 알고리즘이 같은 규칙을 구현함을 보인다.
//        손으로 짠 대표 예 6 개: 읽기 참조 여러 개 OK / 쓰기 참조 하나 / 읽기와 쓰기 동시 거부 / NLL(마지막 사용 뒤 쓰기 OK, 어휘적 범위였다면 거부) / 이동 후 사용 거부 / 빌린 채 이동 거부
template <class T> class Owned {
    std::unique_ptr<T> v; int shared = 0; bool mut = false;
public:
    explicit Owned(T x) : v(new T(std::move(x))) {}
    Owned(Owned&& o) noexcept : v(std::move(o.v)) {}                       // 이동: 원본은 비워진다
    bool moved() const { return !v; }
    struct Ref { Owned& o; bool isMut; Ref(Owned& x, bool m) : o(x), isMut(m) {} ~Ref() { if (isMut) o.mut = false; else o.shared--; } const T& get() const { return *o.v; } T& getMut() { return *o.v; } };
    Ref borrow() { if (!v) throw std::logic_error("use after move"); if (mut) throw std::logic_error("cannot borrow as immutable: mutably borrowed"); shared++; return Ref(*this, false); }
    Ref borrowMut() { if (!v) throw std::logic_error("use after move"); if (mut || shared) throw std::logic_error("cannot borrow as mutable: already borrowed"); mut = true; return Ref(*this, true); }
};
template <class F> bool throws(F f) { try { f(); } catch (const std::logic_error&) { return true; } return false; }

// 작은 언어: 변수 번호는 한 번만 정의된다 (SSA 비슷)
enum Kind { LET, BORROW, BORROW_MUT, USE, USE_MUT, READ, WRITE, MOVE };      // LET a: 소유자 a / BORROW a = &b / BORROW_MUT a = &mut b / USE a: 참조 a 로 읽기 / USE_MUT a: 참조 a 로 쓰기 / READ a, WRITE a: 소유자 직접 접근 / MOVE a -> b
struct Stmt { Kind k; int a, b; };
typedef std::vector<Stmt> Prog;

int staticFirstError(const Prog& p) {                                           // (B) 생존 구간 + 충돌: 첫 오류 문장 번호, 없으면 -1
    int n = (int)p.size(); std::map<int, int> def, lastUse, owner, movedAt; std::map<int, bool> isMut;
    for (int i = 0; i < n; ++i) {
        const Stmt& s = p[i];
        if (s.k == BORROW || s.k == BORROW_MUT) { def[s.a] = i; lastUse[s.a] = i; owner[s.a] = s.b; isMut[s.a] = s.k == BORROW_MUT; }
        if (s.k == USE || s.k == USE_MUT) lastUse[s.a] = i;
        if (s.k == MOVE && !movedAt.count(s.a)) movedAt[s.a] = i;
    }
    int best = n + 1;
    for (int i = 0; i < n; ++i) {
        const Stmt& s = p[i]; int x = -1; bool write = false;                     // 이 문장이 소유자 x 에 하는 접근
        if (s.k == BORROW) x = s.b; else if (s.k == BORROW_MUT) { x = s.b; write = true; } else if (s.k == READ) x = s.a; else if (s.k == WRITE) { x = s.a; write = true; } else if (s.k == MOVE) { x = s.a; write = true; }
        if (x < 0) continue;
        if (movedAt.count(x) && movedAt[x] < i) best = std::min(best, i);       // 이동한 소유자에 접근
        for (auto& kv : owner) {                                                // 이 접근에서 아직 살아 있는(나중에 쓰이는) 참조와의 충돌
            int r = kv.first; if (kv.second != x || def[r] >= i || lastUse[r] <= i) continue;
            if (write || isMut[r]) { for (int j = i + 1; j <= lastUse[r]; ++j) if ((p[j].k == USE || p[j].k == USE_MUT) && p[j].a == r) { best = std::min(best, j); break; } }   // 오류는 충돌 뒤 처음 그 참조를 쓰는 곳에서 드러난다
        }
    }
    return best == n + 1 ? -1 : best;
}

int dynamicFirstError(const Prog& p) {                                          // (C) 실행하며 무효화: 첫 오류 문장 번호, 없으면 -1
    std::map<int, bool> moved, valid; std::map<int, int> owner; std::map<int, bool> isMut;
    auto invalidate = [&](int x, bool onlyMut) { for (auto& kv : owner) if (kv.second == x && (!onlyMut || isMut[kv.first])) valid[kv.first] = false; };
    for (int i = 0; i < (int)p.size(); ++i) {
        const Stmt& s = p[i];
        switch (s.k) {
            case LET: break;
            case BORROW: if (moved[s.b]) return i; invalidate(s.b, true); owner[s.a] = s.b; isMut[s.a] = false; valid[s.a] = true; break;
            case BORROW_MUT: if (moved[s.b]) return i; invalidate(s.b, false); owner[s.a] = s.b; isMut[s.a] = true; valid[s.a] = true; break;
            case USE: case USE_MUT: if (!valid[s.a]) return i; break;
            case READ: if (moved[s.a]) return i; invalidate(s.a, true); break;
            case WRITE: if (moved[s.a]) return i; invalidate(s.a, false); break;
            case MOVE: if (moved[s.a]) return i; invalidate(s.a, false); moved[s.a] = true; break;
        }
    }
    return -1;
}

Prog randomProgram(std::mt19937& rng) {
    Prog p; int next = 0; std::vector<int> owners; std::vector<std::pair<int, bool>> refs;                  // 참조 (번호, 쓰기 가능?)
    int n = 5 + (int)(rng() % 14);
    for (int i = 0; i < n; ++i) {
        int r = (int)(rng() % 100);
        if (owners.empty() || r < 12) { owners.push_back(next); p.push_back({LET, next++, 0}); }
        else if (r < 32) { int x = owners[rng() % owners.size()]; refs.push_back({next, false}); p.push_back({BORROW, next++, x}); }
        else if (r < 44) { int x = owners[rng() % owners.size()]; refs.push_back({next, true}); p.push_back({BORROW_MUT, next++, x}); }
        else if (r < 64 && !refs.empty()) p.push_back({USE, refs[rng() % refs.size()].first, 0});
        else if (r < 72) { std::vector<int> mr; for (auto& q : refs) if (q.second) mr.push_back(q.first); if (!mr.empty()) p.push_back({USE_MUT, mr[rng() % mr.size()], 0}); }
        else if (r < 80) p.push_back({READ, owners[rng() % owners.size()], 0});
        else if (r < 87) p.push_back({WRITE, owners[rng() % owners.size()], 0});
        else if (r < 93) { int x = owners[rng() % owners.size()]; owners.push_back(next); p.push_back({MOVE, x, next++}); }
    }
    return p;
}

int main() {
    // (A) 런타임 검사 (원래 예)
    {   Owned<std::string> a(std::string("data"));
        { auto r1 = a.borrow(); auto r2 = a.borrow(); assert(r1.get() == "data" && r2.get() == "data"); }
        { auto w = a.borrowMut(); w.getMut() += "!"; }
        assert(a.borrow().get() == "data!");
        { auto r = a.borrow(); assert(throws([&] { a.borrowMut(); })); }
        { auto w = a.borrowMut(); assert(throws([&] { a.borrow(); })); assert(throws([&] { a.borrowMut(); })); }
        assert(!throws([&] { a.borrowMut(); }));
        Owned<std::string> b = std::move(a); assert(a.moved() && !b.moved() && throws([&] { a.borrow(); })); }
    // 손으로 짠 예: 변수 0 = x (소유자), 1.. = 참조/새 소유자
    {   Prog sharedOk = {{LET, 0, 0}, {BORROW, 1, 0}, {BORROW, 2, 0}, {USE, 1, 0}, {USE, 2, 0}};                             // 읽기 참조 여러 개
        Prog mutOk = {{LET, 0, 0}, {BORROW_MUT, 1, 0}, {USE_MUT, 1, 0}, {USE_MUT, 1, 0}};                                       // 쓰기 참조 하나
        Prog both = {{LET, 0, 0}, {BORROW, 1, 0}, {BORROW_MUT, 2, 0}, {USE, 1, 0}};                                             // 읽기 참조가 살아 있는 동안 쓰기 참조
        Prog nll = {{LET, 0, 0}, {BORROW, 1, 0}, {USE, 1, 0}, {WRITE, 0, 0}};                                                   // 마지막 사용 뒤의 쓰기는 OK (어휘적 범위였다면 거부될 것)
        Prog nllBad = {{LET, 0, 0}, {BORROW, 1, 0}, {WRITE, 0, 0}, {USE, 1, 0}};                                                // 쓰기 뒤에 참조를 다시 쓰면 거부
        Prog useAfterMove = {{LET, 0, 0}, {MOVE, 0, 1}, {READ, 0, 0}};                                                          // 이동 후 사용
        Prog moveWhileBorrowed = {{LET, 0, 0}, {BORROW, 1, 0}, {MOVE, 0, 2}, {USE, 1, 0}};                                      // 빌린 채 이동
        assert(staticFirstError(sharedOk) == -1 && staticFirstError(mutOk) == -1 && staticFirstError(nll) == -1);
        assert(staticFirstError(both) == 3 && staticFirstError(nllBad) == 3 && staticFirstError(useAfterMove) == 2 && staticFirstError(moveWhileBorrowed) == 3);
        for (const Prog* q : {&sharedOk, &mutOk, &both, &nll, &nllBad, &useAfterMove, &moveWhileBorrowed}) assert(staticFirstError(*q) == dynamicFirstError(*q)); }
    // 무작위 프로그램: 정적 == 동적
    std::mt19937 rng(2025); long accepted = 0, rejected = 0, useAfterMoveErrors = 0, conflictErrors = 0;
    for (int it = 0; it < 30000; ++it) {
        Prog p = randomProgram(rng); int s = staticFirstError(p), d = dynamicFirstError(p);
        assert(s == d);                                                                                                         // 통과/거부와 첫 오류 문장이 같다
        if (s < 0) ++accepted; else { ++rejected; if (p[s].k == USE || p[s].k == USE_MUT) ++conflictErrors; else ++useAfterMoveErrors; }
    }
    assert(accepted > 3000 && rejected > 3000 && useAfterMoveErrors > 100 && conflictErrors > 1000);
    std::cout << "OwnershipTypeSystem verified: static (liveness + conflicts) and dynamic (invalidate on access) borrow checkers agreed on all 30000 random programs (" << accepted << " accepted, " << rejected << " rejected: "
              << conflictErrors << " reference-invalidated, " << useAfterMoveErrors << " use-after-move/borrow-after-move)." << std::endl;
    return 0;
}
// Time Complexity: O(1) 런타임 검사, 정적 검사기 O(문장 수² · 참조 수) (설명용)
// Space Complexity: O(1) / O(변수 수)
```
## PersistentHeap()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <thread>
#include <unordered_set>
#include <vector>

// 영속 자료구조(persistent): 수정해도 이전 버전이 그대로 남는다.  비결은 "구조 공유(structural sharing)" — 바뀌는 경로(루트 → 변경 지점)의 노드만 복사하고 나머지는 이전 버전과 공유한다.  불변성 덕분에 락 없이 여러 스레드가 안전하게 읽고, 스냅샷·되돌리기(undo)·분기가 공짜다 (Clojure, Git 의 객체 저장소, 영속 메모리 힙).
// 여기서는 키 해시를 우선순위로 쓰는 *영속 트립*(split/merge 로 삽입·삭제)을 쓴다 — 균형이 깨지지 않고, 우선순위가 키로 결정되므로 같은 키 집합이면 *삽입 순서와 상관없이 트리 모양이 똑같다*(유일 표현).
//  ① 무작위 삽입·삭제 3 000 번의 모든 버전(3 001 개)을 std::set 스냅샷과 대조(저장한 100 번째마다 전수, 나머지는 크기)  ② 연산당 새 노드 ≤ 4·(높이+1), 버전 전체의 서로 다른 노드 수 ≪ 버전마다 통째로 복사했을 때(Σ 크기) — 공유 비율  ③ 같은 키 집합을 서로 다른 무작위 순서로 6 번 넣으면 모양이 *완전히 같다*(직렬화 비교)
//  ④ 일부 버전만 남기고 나머지를 놓으면 살아 있는 노드 수가 "남긴 버전들이 도달하는 서로 다른 노드 수" 와 정확히 같다(shared_ptr 회수의 정확성)  ⑤ 한 버전에서 두 갈래로 분기해도 서로 독립(분기 두 개 vs std::set 두 복사본)  ⑥ 쓰기 스레드가 버전을 늘리는 동안 읽기 스레드 4 개가 고정된 옛 스냅샷을 반복해서 읽어도 체크섬이 변하지 않음
struct Node; typedef std::shared_ptr<const Node> P;
struct Node { int key; uint32_t pri; int size; P l, r; static std::atomic<long> created, alive;
    Node(int k, uint32_t p, P a, P b) : key(k), pri(p), size(1 + (a ? a->size : 0) + (b ? b->size : 0)), l(std::move(a)), r(std::move(b)) { ++created; ++alive; } ~Node() { --alive; } };
std::atomic<long> Node::created(0), Node::alive(0);
uint32_t priorityOf(int k) { uint32_t x = (uint32_t)k * 2654435761u; x ^= x >> 15; x *= 2246822519u; x ^= x >> 13; return x; }
int sizeOf(const P& t) { return t ? t->size : 0; }
P mk(int k, uint32_t pri, P l, P r) { return std::make_shared<const Node>(k, pri, std::move(l), std::move(r)); }
void split(const P& t, int k, P& a, P& b) { if (!t) { a = b = nullptr; return; }                                                                                                       // a: 키 < k, b: 키 ≥ k
    if (t->key < k) { P ra, rb; split(t->r, k, ra, rb); a = mk(t->key, t->pri, t->l, ra); b = rb; } else { P la, lb; split(t->l, k, la, lb); a = la; b = mk(t->key, t->pri, lb, t->r); } }   // 경로의 노드만 새로 만든다
P merge(const P& a, const P& b) { if (!a) return b; if (!b) return a; if (a->pri > b->pri || (a->pri == b->pri && a->key < b->key)) return mk(a->key, a->pri, a->l, merge(a->r, b)); return mk(b->key, b->pri, merge(a, b->l), b->r); }
bool contains(P t, int k) { while (t) { if (k == t->key) return true; t = k < t->key ? t->l : t->r; } return false; }
P insert(const P& t, int k) { if (contains(t, k)) return t; P a, b; split(t, k, a, b); return merge(merge(a, mk(k, priorityOf(k), nullptr, nullptr)), b); }
P erase(const P& t, int k) { if (!contains(t, k)) return t; P a, b, m, c; split(t, k, a, b); split(b, k + 1, m, c); return merge(a, c); }
int height(const P& t) { return t ? 1 + std::max(height(t->l), height(t->r)) : 0; }
void inorder(const P& t, std::vector<int>& out) { if (!t) return; inorder(t->l, out); out.push_back(t->key); inorder(t->r, out); }
std::string shape(const P& t) { return t ? "(" + shape(t->l) + std::to_string(t->key) + shape(t->r) + ")" : "."; }
void collect(const P& t, std::unordered_set<const Node*>& seen) { if (!t || !seen.insert(t.get()).second) return; collect(t->l, seen); collect(t->r, seen); }                          // 이미 센 노드 아래는 다시 안 간다(공유)

int main() {
    std::mt19937 rng(2718); std::vector<P> versions = {nullptr}; std::vector<std::vector<int>> snapshots = {{}}; std::set<int> model; long maxNewNodes = 0, sumSizes = 0; bool shapeOk = true;
    for (int step = 0; step < 3000; ++step) { int k = (int)(rng() % 600); bool ins = rng() % 100 < 60; long c0 = Node::created.load(); P next = ins ? insert(versions.back(), k) : erase(versions.back(), k); long made = Node::created.load() - c0;
        if (ins) model.insert(k); else model.erase(k); assert(sizeOf(next) == (int)model.size() && contains(next, k) == ins); assert(made <= 4L * (height(next) + 1)); maxNewNodes = std::max(maxNewNodes, made); sumSizes += (long)model.size();
        versions.push_back(next); if (step % 100 == 99) { std::vector<int> v; inorder(next, v); snapshots.push_back(std::vector<int>(model.begin(), model.end())); assert(v == snapshots.back()); } else snapshots.push_back({}); }                          // ①
    for (size_t i = 0; i < versions.size(); ++i) if (!snapshots[i].empty() || i == 0) { std::vector<int> v; inorder(versions[i], v); assert(v == snapshots[i]); }                         // 과거 버전도 그대로
    std::unordered_set<const Node*> distinct; for (auto& v : versions) collect(v, distinct); assert((long)distinct.size() <= Node::created.load() && (long)distinct.size() * 10 < sumSizes);                          // ② 구조 공유: 통째 복사의 10 분의 1 미만
    assert(Node::alive.load() == (long)distinct.size());
    {   std::vector<int> keys; for (int i = 0; i < 300; ++i) keys.push_back(i * 7 % 1000); std::string first; for (int t = 0; t < 6; ++t) { std::shuffle(keys.begin(), keys.end(), rng); P tr; for (int k : keys) tr = insert(tr, k); std::string s = shape(tr); if (t == 0) first = s; else if (s != first) shapeOk = false; } assert(shapeOk); }       // ③ 유일 표현
    std::vector<P> kept = {versions[500], versions[1500], versions.back()};                                                                                                         // ④ 회수의 정확성
    versions.clear(); { std::unordered_set<const Node*> reach; for (auto& v : kept) collect(v, reach); assert(Node::alive.load() == (long)reach.size()); }
    {   P base = kept[1]; std::vector<int> original; inorder(base, original); std::set<int> sa(original.begin(), original.end()), sb = sa; P a = base, b = base;                                // ⑤ 분기
        for (int i = 0; i < 500; ++i) { int ka = (int)(rng() % 600), kb = (int)(rng() % 600); if (rng() % 2) { a = insert(a, ka); sa.insert(ka); } else { a = erase(a, ka); sa.erase(ka); } if (rng() % 3) { b = insert(b, kb); sb.insert(kb); } else { b = erase(b, kb); sb.erase(kb); } assert(sizeOf(a) == (int)sa.size() && sizeOf(b) == (int)sb.size()); }
        std::vector<int> va, vb, vbase; inorder(a, va); inorder(b, vb); inorder(base, vbase); assert(va == std::vector<int>(sa.begin(), sa.end()) && vb == std::vector<int>(sb.begin(), sb.end()) && vbase == original); }       // 두 갈래도 뿌리 버전도 서로 영향 없음
    {   P snap = kept[2]; std::vector<int> v0; inorder(snap, v0); long expected = 0; for (int x : v0) expected += x; std::atomic<bool> stop(false); std::atomic<long> bad(0), rounds(0); std::vector<std::thread> readers;                      // ⑥ 읽기 스레드와 쓰기 스레드
        for (int t = 0; t < 4; ++t) readers.emplace_back([&] { P local = snap; do { std::vector<int> v; inorder(local, v); long s = 0; for (int x : v) s += x; if (s != expected || v != v0) ++bad; ++rounds; } while (!stop.load()); });
        P w = snap; std::mt19937 wr(99); for (int i = 0; i < 2000; ++i) w = (i % 3) ? insert(w, (int)(wr() % 600)) : erase(w, (int)(wr() % 600)); stop.store(true); for (auto& th : readers) th.join(); assert(bad.load() == 0 && rounds.load() >= 4); }
    kept.clear(); assert(Node::alive.load() == 0);                                                                                                                                       // 모든 버전을 놓으면 노드 0 개
    std::cout << "PersistentHeap: 3000 updates produced 3001 readable versions sharing " << distinct.size() << " nodes (a full copy per version would hold " << sumSizes << "); at most " << maxNewNodes << " nodes were created per update, any insertion order gave the identical tree, branches stayed independent, 4 readers saw a frozen snapshot while a writer built 2000 newer versions, and dropping every version freed every node" << std::endl;
    return 0;
}
// Time Complexity: 삽입·삭제·조회 기대 O(log N) 시간과 O(log N) 새 노드
// Space Complexity: 버전마다 O(log N) 추가 (공유)
```
## TransactionalMemory()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <thread>
#include <vector>

// 소프트웨어 트랜잭셔널 메모리(STM, TL2 방식): 락 대신 트랜잭션으로 공유 변수를 다룬다.  읽기는 낙관적으로(락 없이) 하고 쓰기는 버퍼에 모았다가,
// 커밋할 때 "내가 읽은 변수들이 시작 이후 바뀌지 않았는가"(버전 검증)를 확인한다.  충돌했으면 버리고 처음부터 재시도 — 교착 상태가 없고 조합이 쉽다
// TL2 의 구성: 전역 시계 gclock, 변수마다 "버전 + 잠금 비트" 한 워드.  트랜잭션은 시작할 때 rv = gclock 을 읽고, 읽을 때마다 (잠겨 있지 않고, 읽는 동안 안 바뀌고, 버전 <= rv) 를 확인해 일관된 스냅샷만 본다(opacity:
// 나중에 중단될 트랜잭션도 모순된 상태를 보지 않는다).  커밋: ① 쓰기 집합을 주소 순서로 잠금(실패하면 중단) ② wv = gclock 증가 ③ 읽기 집합 재검증(버전 > rv 이거나 남이 잠갔으면 중단) ④ 값 쓰기 ⑤ 버전 wv 로 풀기
// 검증: ① 모든 가능한 끼어들기(interleaving)를 전수 탐색 — 트랜잭션 2 개(연산 4 개 + 커밋) 252 가지, 3 개(연산 2 개 + 커밋) 1 680 가지, 쓰기 편향 시나리오: 각 일정에서 커밋된 트랜잭션들이 "어떤 순차 순서"로 실행한 것과
//        읽은 값·최종 상태가 같고(직렬화 가능성), 중단된 트랜잭션이 읽은 값도 그 순서의 어떤 시점의 일관된 상태에 해당(opacity), 끼어들지 않은 순차 일정에서는 중단이 없다
//        ② 진짜 스레드: x == y 불변식을 지키는 쓰기 스레드 4 개와 둘을 읽는 스레드 4 개 — 읽는 쪽이 트랜잭션 안에서(중단될 시도 포함) 불변식이 깨진 값을 본 횟수 0  ③ 계좌 16 개 이체 스레드 4 개 × 5 000 번 + 감사 스레드 2 개의 전체 합(읽기 전용 트랜잭션):
//        감사가 본 합은 항상 16 000, 최종 합 보존, 중단(재시도) 횟수 > 0
struct Abort {};
struct TVar { std::atomic<uint64_t> vlock{0}; std::atomic<int64_t> value{0}; };                  // vlock = (버전 << 1) | 잠금 비트
std::atomic<uint64_t> gclock{0};
std::atomic<long> commits{0}, aborts{0};

struct Tx {
    uint64_t rv; std::map<TVar*, int64_t> wset; std::vector<TVar*> rset;
    Tx() : rv(gclock.load()) {}
    int64_t read(TVar& v) {
        auto w = wset.find(&v); if (w != wset.end()) return w->second;                           // 자기 쓰기 우선
        uint64_t l1 = v.vlock.load(); int64_t val = v.value.load(); uint64_t l2 = v.vlock.load();
        if ((l1 & 1) || l1 != l2 || (l1 >> 1) > rv) throw Abort();                              // 잠겨 있거나, 읽는 도중 바뀌었거나, 내 시작 뒤에 커밋된 값
        rset.push_back(&v); return val;
    }
    void write(TVar& v, int64_t x) { wset[&v] = x; }
    void commit() {
        if (wset.empty()) return;                                                               // 읽기 전용: 읽을 때마다 일관성을 확인했으므로 커밋 작업이 없다
        std::vector<TVar*> locked;
        auto unlockAll = [&] { for (TVar* v : locked) v->vlock.fetch_and(~1ULL); };
        for (auto& kv : wset) {                                                                  // 주소 순서대로 잠금 (교착 방지)
            TVar* v = kv.first; uint64_t l = v->vlock.load();
            if ((l & 1) || !v->vlock.compare_exchange_strong(l, l | 1)) { unlockAll(); throw Abort(); }
            locked.push_back(v);
        }
        uint64_t wv = gclock.fetch_add(1) + 1;
        for (TVar* r : rset) { uint64_t l = r->vlock.load(); bool mine = wset.count(r) > 0; if ((l >> 1) > rv || ((l & 1) && !mine)) { unlockAll(); throw Abort(); } }   // 읽기 집합 재검증
        for (auto& kv : wset) kv.first->value.store(kv.second);
        for (TVar* v : locked) v->vlock.store(wv << 1);                                          // 새 버전으로 풀기
    }
};
template <class F> void atomically(F f) { for (;;) { Tx tx; try { f(tx); tx.commit(); ++commits; return; } catch (const Abort&) { ++aborts; } } }

// 전수 탐색용 프로그램: 연산 R(읽기), W(쓰기: 변수 = reg[a] + reg[b] + c), 마지막은 항상 커밋
struct Op { char k; int var, reg, a, b; int64_t c; };
typedef std::vector<Op> Program;
struct Observed { bool committed = false, aborted = false; std::vector<std::pair<int, int64_t>> reads; std::vector<int64_t> regs = std::vector<int64_t>(4, 0); };
const int NV = 3;
TVar tv[NV];
void resetVars(const std::vector<int64_t>& init) { gclock = 0; for (int i = 0; i < NV; ++i) { tv[i].vlock = 0; tv[i].value = init[(size_t)i]; } }

std::vector<Observed> runSchedule(const std::vector<Program>& progs, const std::vector<int>& schedule, const std::vector<int64_t>& init, std::vector<int64_t>& finalState) {
    resetVars(init); size_t n = progs.size(); std::vector<Observed> obs(n); std::vector<size_t> pc(n, 0); std::vector<Tx*> txs(n, nullptr);
    for (int t : schedule) {
        size_t i = (size_t)t; if (obs[i].aborted) continue;
        if (!txs[i]) txs[i] = new Tx();                                                           // 트랜잭션은 첫 연산 때 시작 (rv 를 읽는다)
        const Op& op = progs[i][pc[i]++];
        try {
            if (op.k == 'R') { int64_t v = txs[i]->read(tv[op.var]); obs[i].regs[(size_t)op.reg] = v; obs[i].reads.push_back({op.var, v}); }
            else if (op.k == 'W') txs[i]->write(tv[op.var], (op.a >= 0 ? obs[i].regs[(size_t)op.a] : 0) + (op.b >= 0 ? obs[i].regs[(size_t)op.b] : 0) + op.c);
            else { txs[i]->commit(); obs[i].committed = true; }
        } catch (const Abort&) { obs[i].aborted = true; }
    }
    for (Tx* t : txs) delete t;
    finalState.assign((size_t)NV, 0); for (int i = 0; i < NV; ++i) finalState[(size_t)i] = tv[i].value.load(); return obs;
}

// 직렬화 가능성 + opacity 검사: 커밋된 트랜잭션들의 어떤 순서 π 가 모든 읽기와 최종 상태를 설명하고, 중단된 트랜잭션이 읽은 값은 π 의 어떤 접두 상태와 일치
bool explains(const std::vector<Program>& progs, const std::vector<Observed>& obs, const std::vector<int64_t>& init, const std::vector<int64_t>& finalState) {
    std::vector<int> committed, abortedTx; for (size_t i = 0; i < obs.size(); ++i) (obs[i].committed ? committed : abortedTx).push_back((int)i);
    std::sort(committed.begin(), committed.end());
    do {
        std::vector<std::vector<int64_t>> states{init}; bool ok = true;
        for (int t : committed) {
            std::vector<int64_t> s = states.back(), regs(4, 0);
            for (const Op& op : progs[(size_t)t]) {
                if (op.k == 'R') { regs[(size_t)op.reg] = states.back()[(size_t)op.var]; }
                else if (op.k == 'W') s[(size_t)op.var] = (op.a >= 0 ? regs[(size_t)op.a] : 0) + (op.b >= 0 ? regs[(size_t)op.b] : 0) + op.c;
            }
            for (const auto& r : obs[(size_t)t].reads) { if (states.back()[(size_t)r.first] != r.second) ok = false; }          // 이 트랜잭션이 본 값 == 순서상 바로 앞 상태
            states.push_back(s);
        }
        if (!ok || states.back() != finalState) continue;
        for (int t : abortedTx) {                                                                  // opacity: 중단된 트랜잭션도 어떤 시점의 일관된 스냅샷을 봤다
            bool any = false; for (const auto& st : states) { bool match = true; for (const auto& r : obs[(size_t)t].reads) { if (st[(size_t)r.first] != r.second) match = false; } any |= match; }
            if (!any) { ok = false; break; }
        }
        if (ok) return true;
    } while (std::next_permutation(committed.begin(), committed.end()));
    return false;
}

void allSchedules(std::vector<int> remaining, std::vector<int>& cur, std::vector<std::vector<int>>& out) {
    bool any = false;
    for (size_t t = 0; t < remaining.size(); ++t) { if (remaining[t] == 0) continue; any = true; --remaining[t]; cur.push_back((int)t); allSchedules(remaining, cur, out); cur.pop_back(); ++remaining[t]; }
    if (!any) out.push_back(cur);
}
bool isSerial(const std::vector<int>& sch) { std::set<int> done; int prev = -1; for (int t : sch) { if (t != prev) { if (done.count(t)) return false; if (prev >= 0) done.insert(prev); prev = t; } } return true; }

struct Scenario { std::vector<Program> progs; std::vector<int64_t> init; };
struct Totals { long schedules = 0, withAbort = 0, allCommit = 0, serial = 0; };
Totals exploreAll(const Scenario& sc) {
    std::vector<int> lens; for (const auto& p : sc.progs) lens.push_back((int)p.size()); std::vector<std::vector<int>> all; std::vector<int> cur; allSchedules(lens, cur, all); Totals t;
    for (const auto& sch : all) {
        std::vector<int64_t> fin; auto obs = runSchedule(sc.progs, sch, sc.init, fin); assert(explains(sc.progs, obs, sc.init, fin));
        bool anyAbort = false; for (const auto& o : obs) anyAbort |= o.aborted; ++t.schedules; t.withAbort += anyAbort; t.allCommit += !anyAbort;
        if (isSerial(sch)) { ++t.serial; assert(!anyAbort); }                                       // 끼어들지 않은 일정에서는 중단이 없다
    }
    return t;
}

int main() {
    // 결정적 충돌: tx1 이 x 를 읽은 뒤 tx2 가 x 를 바꿔 커밋하면 tx1 의 커밋은 실패해야 한다 (원래 예)
    {   resetVars({5, 0, 0}); Tx t1; int64_t seen = t1.read(tv[0]); atomically([&](Tx& t) { t.write(tv[0], t.read(tv[0]) + 1); });
        t1.write(tv[0], seen + 100); bool conflicted = false; try { t1.commit(); } catch (const Abort&) { conflicted = true; }
        assert(conflicted && tv[0].value == 6); }                                                       // tx1 의 쓰기는 반영되지 않았다 (낡은 읽기에 기반한 갱신 차단)
    // ① 전수 탐색
    Totals tA, tB, tC;
    {   Scenario a; a.init = {0, 0, 0};                                                                   // 서로의 변수를 읽고 쓰는 두 트랜잭션
        a.progs.push_back({{'R', 0, 0, 0, 0, 0}, {'R', 1, 1, 0, 0, 0}, {'W', 0, 0, 0, 1, 1}, {'W', 1, 0, 1, -1, 1}, {'C', 0, 0, 0, 0, 0}});
        a.progs.push_back({{'R', 1, 0, 0, 0, 0}, {'R', 0, 1, 0, 0, 0}, {'W', 1, 0, 0, 1, 10}, {'W', 0, 0, 1, -1, 10}, {'C', 0, 0, 0, 0, 0}});
        tA = exploreAll(a); assert(tA.schedules == 252 && tA.serial == 2 && tA.withAbort > 100); }
    {   Scenario b; b.init = {0, 0, 0};                                                                   // 고리 모양 의존: x -> y -> z -> x
        b.progs.push_back({{'R', 0, 0, 0, 0, 0}, {'W', 1, 0, 0, -1, 1}, {'C', 0, 0, 0, 0, 0}});
        b.progs.push_back({{'R', 1, 0, 0, 0, 0}, {'W', 2, 0, 0, -1, 1}, {'C', 0, 0, 0, 0, 0}});
        b.progs.push_back({{'R', 2, 0, 0, 0, 0}, {'W', 0, 0, 0, -1, 1}, {'C', 0, 0, 0, 0, 0}});
        tB = exploreAll(b); assert(tB.schedules == 1680 && tB.serial == 6); }
    {   Scenario c; c.init = {1, 1, 0};                                                                   // 쓰기 편향(write skew): 둘 다 x, y 를 읽고 서로 다른 변수만 갱신
        c.progs.push_back({{'R', 0, 0, 0, 0, 0}, {'R', 1, 1, 0, 0, 0}, {'W', 0, 0, 0, 1, -2}, {'C', 0, 0, 0, 0, 0}});
        c.progs.push_back({{'R', 0, 0, 0, 0, 0}, {'R', 1, 1, 0, 0, 0}, {'W', 1, 0, 0, 1, -2}, {'C', 0, 0, 0, 0, 0}});
        tC = exploreAll(c); assert(tC.schedules == 70 && tC.withAbort > 20 && tC.allCommit > 0); }          // 직렬화 불가능한 결과는 어떤 일정에서도 나오지 않는다 (exploreAll 안의 assert)
    // ② 진짜 스레드: opacity
    {   TVar x, y; std::atomic<long> bad{0}, reads{0}; std::atomic<bool> stop{false}; std::vector<std::thread> ts;
        for (int w = 0; w < 4; ++w) ts.emplace_back([&] { for (int i = 0; i < 5000; ++i) atomically([&](Tx& tx) { int64_t v = tx.read(x); tx.write(x, v + 1); tx.write(y, v + 1); }); });
        std::vector<std::thread> rs;
        for (int r = 0; r < 4; ++r) rs.emplace_back([&] { while (!stop) { atomically([&](Tx& tx) { int64_t a = tx.read(x), b = tx.read(y); if (a != b) ++bad; ++reads; }); } });         // 중단될 시도 안에서도 검사
        for (auto& t : ts) { t.join(); }
        stop = true; for (auto& t : rs) { t.join(); }
        assert(bad == 0 && x.value == 20000 && y.value == 20000 && reads > 100); }
    // ③ 은행 계좌
    {   const int A = 16; std::vector<TVar> acct(A); for (auto& a : acct) a.value = 1000; std::atomic<long> badSum{0}, audits{0}; std::atomic<bool> stop{false}; commits = aborts = 0; std::vector<std::thread> ts, auditors;
        for (int t = 0; t < 4; ++t) ts.emplace_back([&, t] { std::mt19937 rng(t + 1); for (int i = 0; i < 5000; ++i) { int from = (int)(rng() % A), to = (int)(rng() % A); int64_t amount = 1 + (int64_t)(rng() % 50);
            atomically([&](Tx& tx) { int64_t f = tx.read(acct[from]); if (from == to) return; int64_t g = tx.read(acct[to]); tx.write(acct[from], f - amount); tx.write(acct[to], g + amount); }); } });
        for (int a = 0; a < 2; ++a) auditors.emplace_back([&] { for (int i = 0; i < 5000 && !stop; ++i) { atomically([&](Tx& tx) { int64_t s = 0; for (auto& v : acct) s += tx.read(v); if (s != 16000) ++badSum; ++audits; }); } });
        for (auto& t : ts) { t.join(); }
        stop = true; for (auto& t : auditors) { t.join(); }
        int64_t total = 0; for (auto& a : acct) total += a.value; assert(total == 16000 && badSum == 0 && audits > 10 && aborts > 0); }
    std::cout << "TransactionalMemory verified: all " << tA.schedules + tB.schedules + tC.schedules << " interleavings serializable and opaque (" << tA.withAbort + tB.withAbort + tC.withAbort << " with aborts), no torn snapshot seen by 4 readers, 20000 concurrent transfers kept the total at 16000 with " << aborts << " retries." << std::endl;
    return 0;
}
// Time Complexity: 읽기 O(1) (+ 쓰기 집합 조회), 커밋 O(쓰기 집합 · log + 읽기 집합)
// Space Complexity: 트랜잭션당 O(읽기 집합 + 쓰기 집합), 변수당 한 워드(버전 + 잠금 비트)
```
## CapabilityPointer()
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 케이퍼빌리티 포인터(CHERI): 포인터를 "주소" 만이 아니라 (기준 주소 base, 길이 length, 권한 perms) 를 함께 담은 불변 토큰으로 만든다.
// 접근할 때 하드웨어가 범위와 권한을 검사한다.  케이퍼빌리티는 "축소만" 가능하다(단조성): 더 좁은 범위·더 적은 권한은 만들 수 있지만 넓히거나 권한을 추가할 수는 없다 -> 최소 권한 원칙을 하드웨어가 강제
// 이 구현은 CHERI 의 규칙을 순서대로 갖춘다: 유효 비트(tag), 커서(cursor, 현재 주소), 권한 비트 7 개, 봉인(sealed, 객체 유형 otype),  연산은 위반 시 예외가 아니라 "유효 비트를 끈 케이퍼빌리티"를 돌려주고
//  (사용하는 순간 트랩), 접근 검사 순서는 유효 비트 -> 봉인 -> 권한 -> 범위.  경계 압축: 가수 8 비트 모형이라 긴 객체는 정렬된 경계로 올림되는데, 올림 결과가 부모 범위를 벗어나면 유효 비트를 끈다(올림으로 권한이 커지지 않는다)
// 검증: ① 무작위 파생 연쇄 200 000 번(setBounds, andPerms, setAddr, seal, unseal): 모든 파생물의 권한(권한 x 주소 집합)이 부모의 권한 부분집합 — 단조성  ② 경계 올림: 결과가 요청을 포함하고, 정렬되고, 최소(더 작은 표현 가능한 경계가 없음, 전수 비교),
//        길이 <= 256 이면 정확  ③ 접근 오류 종류가 바이트별 기준과 같음  ④ 봉인된 케이퍼빌리티는 호출(invoke) 쌍으로만 열린다 — 호출자는 데이터를 직접 못 읽는다
enum Perm : unsigned { LOAD = 1, STORE = 2, EXEC = 4, SEAL = 8, UNSEAL = 16, LOAD_CAP = 32, STORE_CAP = 64, ALL = 127 };
enum Fault { NONE, TAG_FAULT, SEAL_FAULT, PERM_FAULT, BOUNDS_FAULT };
struct Cap {
    uint64_t base = 0, length = 0, cursor = 0; unsigned perms = 0; bool tag = false; int otype = -1;      // otype -1 = 봉인 안 됨
    uint64_t top() const { return base + length; } bool sealed() const { return otype >= 0; }
    bool operator==(const Cap& o) const { return base == o.base && length == o.length && cursor == o.cursor && perms == o.perms && tag == o.tag && otype == o.otype; }
};
const unsigned MW = 8;                                                                                     // 가수(mantissa) 폭: 길이 <= 2^MW 는 정확, 그보다 크면 2^e 정렬
Cap untagged(Cap c) { c.tag = false; return c; }
Fault check(const Cap& c, uint64_t addr, uint64_t n, unsigned need) {
    if (!c.tag) return TAG_FAULT;
    if (c.sealed()) return SEAL_FAULT;
    if ((c.perms & need) != need) return PERM_FAULT;
    if (addr < c.base || addr + n > c.top()) return BOUNDS_FAULT;
    return NONE;
}
// 경계 올림: 요청 [b, b + len) 을 덮는 표현 가능한 가장 작은 정렬 경계
void representable(uint64_t b, uint64_t len, uint64_t& rb, uint64_t& rt, unsigned& e) {
    e = 0; while (len > (1ULL << (e + MW))) ++e;                                                            // len <= 2^(e + MW) 인 가장 작은 e
    for (;; ++e) {
        uint64_t a = 1ULL << e; rb = b / a * a; rt = (b + len + a - 1) / a * a;
        if (rt - rb <= (1ULL << (e + MW))) return;                                                          // 올림 결과가 가수에 들어가면 끝
    }
}
Cap setBounds(const Cap& c, uint64_t b, uint64_t len, bool exact = false) {
    Cap r = c; uint64_t rb, rt; unsigned e; representable(b, len, rb, rt, e);
    if (!c.tag || c.sealed() || b < c.base || b + len > c.top() || (exact && (rb != b || rt != b + len))) return untagged(c);   // 요청 자체가 부모 밖이거나 정확하게 표현이 안 되면 무효
    if (rb < c.base || rt > c.top()) return untagged(c);                                                    // 올림 결과가 부모를 벗어나도 무효
    r.base = rb; r.length = rt - rb; r.cursor = b; return r;
}
Cap andPerms(const Cap& c, unsigned mask) { if (!c.tag || c.sealed()) return untagged(c); Cap r = c; r.perms &= mask; return r; }
Cap setAddr(const Cap& c, uint64_t a) { if (c.sealed()) return untagged(c); Cap r = c; r.cursor = a; return r; }                // 커서는 범위 밖으로 가도 되지만 접근할 때 검사
Cap seal(const Cap& c, const Cap& sealer) {
    if (!c.tag || c.sealed() || !sealer.tag || sealer.sealed() || !(sealer.perms & SEAL) || sealer.cursor < sealer.base || sealer.cursor >= sealer.top()) return untagged(c);
    Cap r = c; r.otype = (int)sealer.cursor; return r;
}
Cap unseal(const Cap& c, const Cap& unsealer) {
    if (!c.tag || !c.sealed() || !unsealer.tag || unsealer.sealed() || !(unsealer.perms & UNSEAL) || unsealer.cursor != (uint64_t)c.otype || unsealer.cursor < unsealer.base || unsealer.cursor >= unsealer.top()) return untagged(c);
    Cap r = c; r.otype = -1; return r;
}
bool invoke(const Cap& code, const Cap& data, Cap& codeOut, Cap& dataOut) {                              // CInvoke: 같은 유형으로 봉인된 (코드, 데이터) 쌍을 열어 준다
    if (!code.tag || !data.tag || !code.sealed() || !data.sealed() || code.otype != data.otype || !(code.perms & EXEC)) return false;
    codeOut = code; codeOut.otype = -1; dataOut = data; dataOut.otype = -1; return true;
}
const uint64_t SPACE = 512;
std::bitset<SPACE * 3> authority(Cap c) {                                                                   // 봉인을 풀었을 때 접근 가능한 (주소, 권한 비트) 집합 — 권한의 크기
    std::bitset<SPACE * 3> s; if (!c.tag) return s; c.otype = -1;
    for (uint64_t a = 0; a < SPACE; ++a) { if (check(c, a, 1, LOAD) == NONE) s.set(a * 3); if (check(c, a, 1, STORE) == NONE) s.set(a * 3 + 1); if (check(c, a, 1, EXEC) == NONE) s.set(a * 3 + 2); }
    return s;
}
bool subset(const std::bitset<SPACE * 3>& a, const std::bitset<SPACE * 3>& b) { return (a & ~b).none(); }

int main() {
    // 원래 예
    {   Cap whole{0, 1024, 0, ALL, true, -1}; Cap buf = setBounds(whole, 100, 16); buf = andPerms(buf, LOAD | STORE); assert(buf.tag && buf.base == 100 && buf.length == 16);
        assert(check(buf, 115, 1, STORE) == NONE && check(buf, 116, 1, STORE) == BOUNDS_FAULT);                // 버퍼 오버플로: 1바이트만 넘어도 하드웨어가 거부
        Cap ro = andPerms(setBounds(buf, 100, 8), LOAD); assert(ro.tag && check(ro, 100, 1, LOAD) == NONE && check(ro, 100, 1, STORE) == PERM_FAULT);          // 더 좁고 약한 케이퍼빌리티
        Cap again = andPerms(ro, LOAD | STORE); assert(again.tag && (again.perms & STORE) == 0);                                                                  // 권한 마스크는 AND 이므로 권한을 되살릴 수 없다
        assert(!setBounds(buf, 100, 32).tag && !setBounds(buf, 90, 8).tag);                                       // 범위를 넓히거나 밖으로 이동할 수 없다
        assert(check(untagged(buf), 100, 1, LOAD) == TAG_FAULT); }
    // ① 단조성: 무작위 파생 연쇄
    std::mt19937_64 rng(2024); long derivations = 0, tagCleared = 0;
    for (int chain = 0; chain < 2000; ++chain) {
        Cap root{0, SPACE, 0, ALL, true, -1}; Cap cur = root; Cap sealer{0, 16, 7, SEAL | UNSEAL, true, -1}; std::bitset<SPACE * 3> prev = authority(cur);
        for (int step = 0; step < 100; ++step) {
            Cap next; int op = (int)(rng() % 6);
            if (op == 0) { uint64_t b = rng() % (SPACE + 20), len = rng() % 200; next = setBounds(cur, b, len); }
            else if (op == 1) next = andPerms(cur, (unsigned)(rng() & ALL)); else if (op == 2) next = setAddr(cur, rng() % (SPACE + 20));
            else if (op == 3) next = seal(cur, sealer); else if (op == 4) next = cur.sealed() ? unseal(cur, sealer) : cur; else next = setBounds(cur, cur.base + rng() % (cur.length + 1), rng() % (cur.length + 1), true);
            std::bitset<SPACE * 3> now = authority(next); assert(subset(now, prev)); ++derivations; tagCleared += !next.tag;      // 어떤 연산으로도 권한이 커지지 않는다
            if (!next.tag) { assert(!seal(next, sealer).tag && !setBounds(next, 0, 1).tag && !andPerms(next, ALL).tag && !setAddr(next, 3).tag && !unseal(next, sealer).tag); cur = root; prev = authority(cur); }   // 유효 비트가 꺼진 것은 어떤 연산으로도 되살릴 수 없다 — 새 연쇄를 루트에서 다시 시작
            else { cur = next; prev = now; }
        }
    }
    assert(derivations == 200000 && tagCleared > 10000 && tagCleared < 150000);
    // ② 경계 올림
    long exactSmall = 0, rounded = 0;
    for (uint64_t b = 0; b < 1200; b += 7) for (uint64_t len = 1; len < 1500; len += 5) {
        uint64_t rb, rt; unsigned e; representable(b, len, rb, rt, e);
        assert(rb <= b && rt >= b + len && rb % (1ULL << e) == 0 && rt % (1ULL << e) == 0 && rt - rb <= (1ULL << (e + MW)));                // 요청을 포함, 정렬, 가수에 들어간다
        for (unsigned e2 = 0; e2 < e; ++e2) { uint64_t a = 1ULL << e2, lo = b / a * a, hi = (b + len + a - 1) / a * a; assert(hi - lo > (1ULL << (e2 + MW))); }       // 더 작은 지수로는 표현 불가 -> 최소
        if (len <= (1ULL << MW)) { assert(e == 0 && rb == b && rt == b + len); ++exactSmall; } if (rb != b || rt != b + len) ++rounded;       // 짧은 객체는 정확
    }
    assert(exactSmall > 3000 && rounded > 3000);
    { Cap whole{0, 4096, 0, ALL, true, -1}; assert(!setBounds(whole, 1, 1000, true).tag && setBounds(whole, 1, 1000, false).tag && setBounds(whole, 256, 1024, true).tag);     // 정확히 표현할 수 없으면 정확 모드는 무효, 올림 모드는 성공
      Cap tight{3, 700, 3, ALL, true, -1}; assert(!setBounds(tight, 3, 700).tag && !setBounds(tight, 3, 700, true).tag); }                                         // 부모 자체가 정렬 안 된 경계: 올림 결과가 부모를 벗어나면 무효
    // ③ 접근 오류 종류 (바이트 기준과 비교)
    long faults[5] = {0, 0, 0, 0, 0};
    for (int i = 0; i < 60000; ++i) {
        Cap c{rng() % 300, rng() % 200, 0, (unsigned)(rng() & ALL), rng() % 8 != 0, rng() % 5 == 0 ? (int)(rng() % 16) : -1}; uint64_t a = rng() % 520, n = 1 + rng() % 8; unsigned need = 1u << (rng() % 3);
        Fault want = !c.tag ? TAG_FAULT : c.sealed() ? SEAL_FAULT : ((c.perms & need) != need) ? PERM_FAULT : NONE;
        if (want == NONE) { for (uint64_t b = a; b < a + n; ++b) { if (b < c.base || b >= c.base + c.length) { want = BOUNDS_FAULT; break; } } }       // 접근하는 바이트가 하나라도 범위 밖이면
        assert(check(c, a, n, need) == want); ++faults[want];
    }
    for (int k = 0; k < 5; ++k) assert(faults[k] > 500);
    // ④ 봉인과 호출
    {   Cap data{100, 64, 100, LOAD | STORE, true, -1}, code{200, 32, 200, LOAD | EXEC, true, -1}; Cap sealerCap{0, 16, 7, SEAL | UNSEAL, true, -1}, otherSealer{0, 16, 9, SEAL | UNSEAL, true, -1};
        Cap sd = seal(data, sealerCap), sc = seal(code, sealerCap); assert(sd.tag && sd.sealed() && sc.sealed() && check(sd, 100, 1, LOAD) == SEAL_FAULT);        // 봉인된 데이터는 호출자가 직접 못 읽는다
        assert(!unseal(sd, otherSealer).tag && unseal(sd, sealerCap).tag && check(unseal(sd, sealerCap), 100, 1, STORE) == NONE);                              // 맞는 유형으로만 열린다
        Cap c2, d2; assert(invoke(sc, sd, c2, d2) && check(d2, 163, 1, STORE) == NONE && check(d2, 164, 1, STORE) == BOUNDS_FAULT && check(c2, 200, 4, EXEC) == NONE);   // 호출하면 피호출자만 데이터를 쓴다
        Cap wrongType = seal(data, otherSealer); assert(!invoke(sc, wrongType, c2, d2));                           // 서로 다른 유형은 호출 불가
        assert(!seal(sd, sealerCap).tag && !setBounds(sd, 100, 8).tag && !andPerms(sd, LOAD).tag); }               // 봉인된 것은 다시 봉인·축소할 수 없다
    std::cout << "CapabilityPointer verified: " << derivations << " random derivations never increased authority (" << tagCleared << " invalidated), bounds rounding is minimal and never widens past the parent, fault precedence matched on 60000 accesses, sealed invoke pairs work." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사 (하드웨어)
// Space Complexity: 포인터당 base·length·perms 추가 (CHERI 는 128비트 포인터 + 태그 1비트)
```
## CHERIArchitecture()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <set>
#include <stdexcept>
#include <vector>

// CHERI 의 핵심 아이디어 두 가지: (1) 케이퍼빌리티는 16바이트로 정렬된 메모리에 저장되고, 메모리 16바이트마다 숨은 "태그 비트" 가 붙는다.
// (2) 케이퍼빌리티를 저장하면 태그가 1 이 되지만, 같은 16바이트에 일반 데이터를 쓰면 태그가 자동으로 0 이 된다 -> 바이트를 조작해 케이퍼빌리티를 위조할 수 없다.
// 태그가 꺼진 케이퍼빌리티는 사용하려 하면 예외.  이 두 가지로 "포인터 위조 불가" 가 하드웨어 수준에서 성립한다
// 이 구현은 케이퍼빌리티를 진짜 128비트(축소된 32비트 주소 공간: base 32 + length 32 + cursor 32 + perms 16 + otype 16)로 인코딩해 메모리 바이트에 쓰고, 태그는 바이트와 별도의 비트 배열에 둔다.
//  연산: 데이터 저장(1/2/4/8 바이트; 겹치는 16바이트 칸의 태그를 지움), 케이퍼빌리티 저장(16 바이트 정렬; 태그는 값의 태그), 케이퍼빌리티 읽기, 데이터 memcpy(태그를 버림), 케이퍼빌리티 인식 memcpy(정렬되어 있으면 태그째 복사),
//  해제 영역을 가리키는 케이퍼빌리티의 태그를 지우는 회수(revocation) 훑기
// 검증: ① 인코딩 왕복 200 000 개  ② 무작위 연산 30 000 번을 "칸마다 값/무효 표시를 따로 둔 모형" 과 대조 — 모든 칸의 태그가 같고, 태그가 켜진 칸을 읽으면 모형의 케이퍼빌리티와 같음
//        ③ 위조 불가: 데이터 연산(저장·memcpy)만 가진 공격자가 메모리를 10 만 번 만져도 태그가 켜진 케이퍼빌리티는 처음에 신뢰된 코드가 넣어 둔 값들뿐이고, 케이퍼빌리티 인식 복사로는 복제만 될 뿐 새 값은 안 생김
//        ④ 회수: 훑은 뒤 해제 영역을 가리키는 유효한 케이퍼빌리티가 하나도 없고(use-after-free 차단), 그 외 케이퍼빌리티는 그대로
const size_t GRANULE = 16;
struct Cap { uint32_t base = 0, length = 0, cursor = 0; uint16_t perms = 0, otype = 0xFFFF; bool tag = false;
    bool sameValue(const Cap& o) const { return base == o.base && length == o.length && cursor == o.cursor && perms == o.perms && otype == o.otype; } };
void encode(const Cap& c, uint8_t out[16]) { uint64_t lo = (uint64_t)c.base | ((uint64_t)c.length << 32), hi = (uint64_t)c.cursor | ((uint64_t)c.perms << 32) | ((uint64_t)c.otype << 48); std::memcpy(out, &lo, 8); std::memcpy(out + 8, &hi, 8); }
Cap decode(const uint8_t in[16]) { uint64_t lo, hi; std::memcpy(&lo, in, 8); std::memcpy(&hi, in + 8, 8); Cap c; c.base = (uint32_t)lo; c.length = (uint32_t)(lo >> 32); c.cursor = (uint32_t)hi; c.perms = (uint16_t)(hi >> 32); c.otype = (uint16_t)(hi >> 48); return c; }

class TaggedMemory {
    std::vector<uint8_t> bytes; std::vector<bool> tags;
public:
    explicit TaggedMemory(size_t n) : bytes(n, 0), tags(n / GRANULE, false) {}
    size_t granules() const { return tags.size(); }
    bool tagAt(size_t addr) const { return tags[addr / GRANULE]; }
    void storeData(size_t addr, unsigned size, uint64_t value) { std::memcpy(&bytes[addr], &value, size); for (size_t g = addr / GRANULE; g <= (addr + size - 1) / GRANULE; ++g) tags[g] = false; }   // 일반 저장은 겹치는 칸의 태그를 지운다
    void storeCap(size_t addr, const Cap& c) { assert(addr % GRANULE == 0); encode(c, &bytes[addr]); tags[addr / GRANULE] = c.tag; }
    Cap loadCap(size_t addr) const { assert(addr % GRANULE == 0); Cap c = decode(&bytes[addr]); c.tag = tags[addr / GRANULE]; return c; }
    void memcpyData(size_t dst, size_t src, size_t n) { std::vector<uint8_t> tmp(bytes.begin() + (long)src, bytes.begin() + (long)(src + n)); std::copy(tmp.begin(), tmp.end(), bytes.begin() + (long)dst); for (size_t g = dst / GRANULE; g <= (dst + n - 1) / GRANULE; ++g) tags[g] = false; }   // 태그 없이 바이트만
    void memcpyCap(size_t dst, size_t src, size_t n) {                                              // 케이퍼빌리티 인식: 둘 다 16 바이트 정렬이고 길이가 16 의 배수면 태그째 복사
        if (dst % GRANULE || src % GRANULE || n % GRANULE) { memcpyData(dst, src, n); return; }
        std::vector<uint8_t> tmp(bytes.begin() + (long)src, bytes.begin() + (long)(src + n)); std::vector<bool> tt; for (size_t g = 0; g < n / GRANULE; ++g) tt.push_back(tags[src / GRANULE + g]);
        std::copy(tmp.begin(), tmp.end(), bytes.begin() + (long)dst); for (size_t g = 0; g < n / GRANULE; ++g) tags[dst / GRANULE + g] = tt[g];
    }
    size_t revoke(uint32_t lo, uint32_t hi) {                                                       // 회수 훑기: [lo, hi) 와 겹치는 영역을 가리키는 케이퍼빌리티의 태그를 끈다
        size_t cleared = 0; for (size_t g = 0; g < tags.size(); ++g) { if (!tags[g]) continue; Cap c = decode(&bytes[g * GRANULE]); if ((uint64_t)c.base < hi && lo < (uint64_t)c.base + c.length) { tags[g] = false; ++cleared; } } return cleared;
    }
};
uint8_t use(const Cap& c) { if (!c.tag) throw std::runtime_error("tag violation: invalid capability"); return 1; }

int main() {
    // 원래 예: 덮어쓰면 태그가 꺼진다
    {   TaggedMemory mem(256); Cap k; k.base = 100; k.length = 16; k.tag = true; mem.storeCap(32, k);
        assert(mem.tagAt(32) && use(mem.loadCap(32)) == 1);
        mem.storeData(40, 1, 0xFF); assert(!mem.tagAt(32));                                                       // 같은 16바이트 칸의 일부를 덮어쓰면 태그가 자동으로 꺼진다
        bool trapped = false; try { use(mem.loadCap(32)); } catch (const std::runtime_error&) { trapped = true; } assert(trapped);
        for (size_t i = 64; i < 80; i++) { mem.storeData(i, 1, 0x41); }
        assert(!mem.tagAt(64) && !mem.loadCap(64).tag); }                    // 그럴듯한 비트 패턴을 써도 태그가 없어 무효
    // ① 인코딩 왕복
    std::mt19937_64 rng(77);
    for (int i = 0; i < 200000; ++i) { Cap c; c.base = (uint32_t)rng(); c.length = (uint32_t)rng(); c.cursor = (uint32_t)rng(); c.perms = (uint16_t)rng(); c.otype = (uint16_t)rng(); uint8_t buf[16]; encode(c, buf); assert(decode(buf).sameValue(c)); }
    // ② 모형과 대조
    {   const size_t N = 4096, G = N / GRANULE; TaggedMemory mem(N); std::vector<bool> isCap(G, false); std::vector<Cap> val(G); long capStores = 0, strips = 0, copies = 0;
        auto randomCap = [&](bool tag) { Cap c; c.base = (uint32_t)(rng() % 3000); c.length = (uint32_t)(rng() % 1000); c.cursor = c.base; c.perms = (uint16_t)(rng() & 127); c.otype = 0xFFFF; c.tag = tag; return c; };
        for (int step = 0; step < 30000; ++step) {
            int op = (int)(rng() % 100);
            if (op < 40) { unsigned sz = 1u << (rng() % 4); size_t addr = rng() % (N - 8); addr &= ~(size_t)(sz - 1); mem.storeData(addr, sz, rng()); for (size_t g = addr / GRANULE; g <= (addr + sz - 1) / GRANULE; ++g) isCap[g] = false; ++strips; }
            else if (op < 65) { size_t g = rng() % G; Cap c = randomCap(true); mem.storeCap(g * GRANULE, c); isCap[g] = true; val[g] = c; ++capStores; }
            else if (op < 72) { size_t g = rng() % G; Cap c = randomCap(false); mem.storeCap(g * GRANULE, c); isCap[g] = false; }
            else if (op < 90) { size_t n = (1 + rng() % 8) * GRANULE, dst = (rng() % (G - 8)) * GRANULE, src = (rng() % (G - 8)) * GRANULE; if (dst < src + n && src < dst + n) continue;
                mem.memcpyCap(dst, src, n); for (size_t k = 0; k < n / GRANULE; ++k) { isCap[dst / GRANULE + k] = isCap[src / GRANULE + k]; val[dst / GRANULE + k] = val[src / GRANULE + k]; } ++copies; }
            else if (op < 97) { size_t n = 1 + rng() % 64, dst = rng() % (N - 80), src = rng() % (N - 80); if (dst < src + n && src < dst + n) continue; mem.memcpyData(dst, src, n); for (size_t g = dst / GRANULE; g <= (dst + n - 1) / GRANULE; ++g) isCap[g] = false; }
            else { uint32_t lo = (uint32_t)(rng() % 3000), hi = lo + (uint32_t)(rng() % 400); mem.revoke(lo, hi); for (size_t g = 0; g < G; ++g) { if (isCap[g] && (uint64_t)val[g].base < hi && lo < (uint64_t)val[g].base + val[g].length) isCap[g] = false; } }
            if (step % 7 == 0) for (size_t g = 0; g < G; ++g) { assert(mem.tagAt(g * GRANULE) == isCap[g]); if (isCap[g]) { Cap c = mem.loadCap(g * GRANULE); assert(c.tag && c.sameValue(val[g])); } }
        }
        assert(capStores > 5000 && strips > 8000 && copies > 3000); }
    // ③ 위조 불가
    {   const size_t N = 4096, G = N / GRANULE; TaggedMemory mem(N); std::vector<Cap> original; std::set<std::vector<uint32_t>> originalValues;
        for (size_t g = 0; g < G; g += 3) { Cap c; c.base = (uint32_t)(g * 100); c.length = (uint32_t)(16 + g); c.cursor = c.base; c.perms = 7; c.tag = true; mem.storeCap(g * GRANULE, c); originalValues.insert({c.base, c.length, c.cursor, c.perms}); }
        for (int step = 0; step < 100000; ++step) {                                                          // 공격자: 데이터 저장과 memcpy 와 케이퍼빌리티 인식 복사만 쓴다 (새 값을 만들 수단이 없다)
            int op = (int)(rng() % 3);
            if (op == 0) { unsigned sz = 1u << (rng() % 4); size_t addr = (rng() % (N - 8)) & ~(size_t)(sz - 1); mem.storeData(addr, sz, rng()); }
            else if (op == 1) { size_t n = 1 + rng() % 40, dst = rng() % (N - 64), src = rng() % (N - 64); if (!(dst < src + n && src < dst + n)) mem.memcpyData(dst, src, n); }
            else { size_t n = (1 + rng() % 4) * GRANULE, dst = (rng() % (G - 4)) * GRANULE, src = (rng() % (G - 4)) * GRANULE; if (!(dst < src + n && src < dst + n)) mem.memcpyCap(dst, src, n); }
            if (step % 500 == 0) for (size_t g = 0; g < G; ++g) { if (!mem.tagAt(g * GRANULE)) continue; Cap c = mem.loadCap(g * GRANULE); assert(originalValues.count({c.base, c.length, c.cursor, c.perms})); }   // 태그가 켜진 것은 모두 처음 값의 복제
        }
        size_t tagged = 0; for (size_t g = 0; g < G; ++g) tagged += mem.tagAt(g * GRANULE); assert(tagged <= G / 3 + 1 + G); }
    // ④ 회수
    {   const size_t N = 4096, G = N / GRANULE; TaggedMemory mem(N); std::vector<Cap> caps(G); long toFree = 0, keep = 0;
        for (size_t g = 0; g < G; ++g) { Cap c; c.base = (uint32_t)(rng() % 3500); c.length = (uint32_t)(1 + rng() % 200); c.cursor = c.base; c.perms = 3; c.tag = true; caps[g] = c; mem.storeCap(g * GRANULE, c); }
        const uint32_t lo = 1000, hi = 1600; size_t cleared = mem.revoke(lo, hi);
        for (size_t g = 0; g < G; ++g) { bool refers = (uint64_t)caps[g].base < hi && lo < (uint64_t)caps[g].base + caps[g].length; assert(mem.tagAt(g * GRANULE) == !refers); toFree += refers; keep += !refers; }   // 해제 영역을 가리키는 것만 꺼졌다
        assert(cleared == (size_t)toFree && toFree > 30 && keep > 30 && mem.revoke(lo, hi) == 0); }                  // 두 번째 훑기에는 더 지울 것이 없다
    std::cout << "CHERIArchitecture verified: 128-bit encoding round-trips, tag semantics match the per-granule model over 30000 operations, a data-only attacker forged nothing in 100000 operations, and revocation cleared exactly the capabilities that referred to freed memory." << std::endl;
    return 0;
}
// Time Complexity: 저장·읽기 O(1), 회수 훑기 O(메모리 / 16)
// Space Complexity: 16바이트당 태그 1비트 (약 0.8%)
```
## MemoryTagging()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 메모리 태깅(ARM MTE): 메모리를 16바이트 단위(granule)로 나눠 각각에 4비트 "태그" 를 붙이고, 포인터의 상위 비트에도 같은 4비트 태그를 넣는다.
// 접근할 때 하드웨어가 포인터 태그 == 메모리 태그 인지 검사한다.  할당할 때 임의 태그를 붙이고, 해제하면 다른 태그로 바꾸면 해제 후 사용(UAF)이 대부분(15/16) 잡히고,
// 이웃한 할당끼리 태그를 달리하면 오버플로도 잡힌다.  CHERI 와 달리 포인터 크기가 그대로이고 확률적 보호
// 이 구현은 포인터 상위 비트(56~59)에 실제로 태그를 넣고, 태그 1~15 를 쓴다(0 은 태그 없는 메모리). 태그 정책 두 가지를 비교한다: RANDOM(독립 균등 무작위)과 AVOID(옛 태그·이웃 태그를 제외하고 무작위).
//  동기(sync) 모드는 불일치 접근을 막고, 비동기(async) 모드는 접근을 허용하되 불일치를 기록해 두었다가 sync() 에서 한꺼번에 알린다
// 검증: ① 원래 장면(이웃 오버플로, 해제 후 사용)  ② 접근 [off, off + w) 의 판정을 바이트별 태그 배열을 쓴 독립 기준과 전수 대조 — 할당 크기 1..80, 오프셋 -20..100, 폭 1/2/4/8/16 모든 조합
//        (16 바이트 올림 안의 "조각" 은 못 잡는다는 한계 포함)  ③ 몬테카를로 200 000 번: 해제 후 사용 탐지율이 RANDOM 은 14/15, AVOID 는 1 세대 전 낡은 포인터를 100%, 2 세대 전은 13/14 (옛 태그만 제외하므로 후보 14 개 중 하나가 2 세대 전 태그, 5 시그마 안)
//        이웃 오버플로: AVOID 100%, RANDOM 14/15  ④ 비동기 모드: 불일치한 접근 수 == sync() 가 알린 수, 접근은 실제로 실행됨(메모리 변경) / 동기 모드는 실행 안 됨  ⑤ 무작위 할당·해제·접근 50 000 번이 바이트 기준과 일치
const uint64_t TAG_SHIFT = 56;
inline unsigned tagOf(uint64_t p) { return (unsigned)(p >> TAG_SHIFT & 0xf); }
inline uint64_t addrOf(uint64_t p) { return p & ((1ULL << TAG_SHIFT) - 1); }
inline uint64_t withTag(uint64_t addr, unsigned t) { return addr | ((uint64_t)t << TAG_SHIFT); }
enum Policy { RANDOM, AVOID };

struct SplitMix { uint64_t s; explicit SplitMix(uint64_t seed) : s(seed) {} uint32_t operator()() { uint64_t z = (s += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return (uint32_t)((z ^ (z >> 31)) >> 16); } };      // 시드 비용이 작은 난수 발생기
class TaggedHeap {
    std::vector<uint8_t> mem, tags; uint64_t top = 16; SplitMix rng; Policy policy; std::vector<uint64_t> pendingFaults; bool async;
    unsigned pick(unsigned avoid1, unsigned avoid2) {
        for (;;) { unsigned t = 1 + (unsigned)(rng() % 15); if (policy == RANDOM || (t != avoid1 && t != avoid2)) return t; }
    }
public:
    long writes = 0;
    TaggedHeap(size_t n, Policy p, uint32_t seed, bool asyncMode = false) : mem(n, 0), tags(n / 16, 0), rng(seed), policy(p), async(asyncMode) {}
    uint64_t alloc(size_t n) {                                                                          // 이웃(왼쪽) 할당의 태그를 피한다
        size_t g = (n + 15) / 16; unsigned left = top >= 32 ? tags[top / 16 - 1] : 0; unsigned t = pick(left, 0);
        uint64_t addr = top; for (size_t i = 0; i < g; ++i) tags[addr / 16 + i] = (uint8_t)t; top += g * 16; return withTag(addr, t);
    }
    void release(uint64_t p, size_t n) { unsigned old = tagOf(p); unsigned t = pick(old, old); for (size_t i = 0; i < (n + 15) / 16; ++i) tags[addrOf(p) / 16 + i] = (uint8_t)t; }   // 해제: 메모리 태그를 옛 태그와 다른 값으로
    bool matches(uint64_t p, size_t off, size_t w) const { for (uint64_t g = (addrOf(p) + off) / 16; g <= (addrOf(p) + off + w - 1) / 16; ++g) { if (g >= tags.size() || tags[g] != tagOf(p)) return false; } return true; }   // 걸친 모든 칸을 검사
    bool access(uint64_t p, size_t off, size_t w, bool isWrite) {                                         // 성공하면 true
        if (!matches(p, off, w)) { if (!async) return false; pendingFaults.push_back(addrOf(p) + off); }   // 동기: 막는다, 비동기: 기록하고 계속
        if (isWrite) { for (size_t i = 0; i < w; ++i) mem[addrOf(p) + off + i] = 0xAB; ++writes; } return true;
    }
    size_t sync() { size_t n = pendingFaults.size(); pendingFaults.clear(); return n; }
    uint8_t byteAt(uint64_t addr) const { return mem[addr]; }
    uint8_t memTag(uint64_t addr) const { return tags[addr / 16]; }
};

int main() {
    // ① 원래 장면
    {   TaggedHeap h(1024, AVOID, 1); uint64_t a = h.alloc(32), b = h.alloc(32); assert(tagOf(a) != tagOf(b) && tagOf(a) >= 1);
        assert(h.access(a, 31, 1, true) && !h.access(a, 32, 1, true));                                    // 오버플로: a 의 끝을 넘어 b 의 영역(다른 태그)에 쓰기 -> 탐지
        h.release(a, 32); assert(!h.access(a, 0, 1, false));                                              // 해제 후 사용: 메모리 태그가 바뀌어 탐지
        assert(h.access(b, 0, 1, false)); }
    // ② 바이트 기준과 전수 대조
    long cells = 0, intraGranuleMisses = 0;
    for (size_t n = 1; n <= 80; ++n) {
        TaggedHeap h(512, AVOID, (uint32_t)n); h.alloc(16); uint64_t p = h.alloc(n); h.alloc(48); size_t rounded = (n + 15) / 16 * 16; uint64_t base = addrOf(p);
        std::vector<int> byteTag(512, -1); for (size_t i = 0; i < 512; ++i) byteTag[i] = h.memTag(i);                // 바이트마다 태그를 따로 펼친 기준
        for (long off = -20; off <= 100; ++off) for (unsigned w : {1u, 2u, 4u, 8u, 16u}) {
            if ((long)base + off < 0 || (long)base + off + (long)w > 512) continue;
            bool want = true; for (unsigned i = 0; i < w; ++i) { if (byteTag[(size_t)((long)base + off + (long)i)] != (int)tagOf(p)) want = false; }
            if (off >= 0) { assert(h.matches(p, (size_t)off, w) == want); }
            if (off >= (long)n && (size_t)off + w <= rounded && off >= 0) { assert(want); ++intraGranuleMisses; }   // 올림 안의 조각(n 이상 16 의 배수 미만)은 태그가 같아 통과 — MTE 의 한계
            ++cells;
        }
    }
    assert(cells > 40000 && intraGranuleMisses > 1000);
    // ③ 몬테카를로
    {   const int TR = 200000; auto detectRate = [&](Policy pol, int generations, bool neighbor) {
            long caught = 0; std::mt19937 r(5 + generations + (neighbor ? 1000 : 0));
            for (int t = 0; t < TR; ++t) {
                TaggedHeap g(256, pol, (uint32_t)r()); uint64_t a = g.alloc(32), b = g.alloc(32); (void)b;
                if (neighbor) { caught += !g.access(a, 32, 1, false); continue; }                              // 이웃 오버플로: a 의 끝 다음 칸은 b
                uint64_t stale = a; for (int k = 0; k < generations; ++k) { g.release(a, 32); a = withTag(addrOf(a), g.memTag(addrOf(a))); }                     // 해제할 때마다 메모리 태그가 바뀌고, 새 소유자의 포인터는 새 태그를 받는다
                caught += !g.access(stale, 0, 1, false);
            } return (double)caught / TR; };
        auto within = [&](double got, double p) { double sd = std::sqrt(p * (1 - p) / TR); return std::abs(got - p) <= 5 * sd + 1e-9; };
        assert(within(detectRate(RANDOM, 1, false), 14.0 / 15) && detectRate(AVOID, 1, false) == 1.0 && within(detectRate(AVOID, 2, false), 13.0 / 14));   // 낡은 포인터: 1 세대 전은 AVOID 가 100%
        assert(detectRate(AVOID, 1, true) == 1.0 && within(detectRate(RANDOM, 1, true), 14.0 / 15)); }          // 이웃 오버플로: 이웃과 태그를 다르게 하면 100%
    // ④ 비동기 vs 동기
    {   for (int mode = 0; mode < 2; ++mode) {
            TaggedHeap h(1024, AVOID, 7, mode == 1); uint64_t a = h.alloc(16), b = h.alloc(16); (void)b;
            for (int i = 0; i < 10; ++i) { h.access(a, 16 + (size_t)i, 1, true); }                                                   // 이웃 영역에 10 번 쓰기
            if (mode == 0) { assert(h.writes == 0 && h.byteAt(addrOf(a) + 16) == 0 && h.sync() == 0); }            // 동기: 접근이 막혀 메모리가 안 바뀌고 기록할 것도 없다
            else { assert(h.writes == 10 && h.byteAt(addrOf(a) + 16) == 0xAB && h.sync() == 10); }                 // 비동기: 실행되어 메모리가 바뀌었고 sync() 가 10 번을 한꺼번에 알린다
            } }
    // ⑤ 무작위 할당·해제·접근
    {   TaggedHeap h(1 << 16, AVOID, 31); std::mt19937 rng(8); struct Blk { uint64_t p; size_t n; bool freed; unsigned memTagNow; }; std::vector<Blk> blks; long checks = 0, caught = 0;
        for (int step = 0; step < 50000; ++step) {
            int op = (int)(rng() % 100);
            if (op < 25 && blks.size() < 800) { size_t n = 1 + rng() % 70; uint64_t p = h.alloc(n); blks.push_back({p, n, false, tagOf(p)}); }
            else if (op < 40 && !blks.empty()) { Blk& b = blks[rng() % blks.size()]; if (!b.freed) { h.release(b.p, b.n); b.freed = true; b.memTagNow = h.memTag(addrOf(b.p)); } }
            else if (!blks.empty()) {
                Blk& b = blks[rng() % blks.size()]; long off = (long)(rng() % (b.n + 40)) - 8; unsigned w = 1u << (rng() % 4); if ((long)addrOf(b.p) + off < 0 || addrOf(b.p) + (uint64_t)off + w > (1 << 16)) continue;
                size_t o = off < 0 ? 0 : (size_t)off; bool want = true;
                for (uint64_t byte = addrOf(b.p) + o; byte < addrOf(b.p) + o + w; ++byte) { if (h.memTag(byte) != tagOf(b.p)) want = false; }           // 바이트 기준: 걸친 바이트의 칸 태그가 모두 같은가
                assert(h.access(b.p, o, w, false) == want); ++checks; caught += !want;
            }
        }
        assert(checks > 10000 && caught > 500); }
    std::cout << "MemoryTagging verified: granule-exact tag checks over " << cells << " (size, offset, width) cases incl. the 16-byte-rounding blind spot, detection rates match 14/15 (random) and 100% (avoid old/neighbour tags), async mode logs without blocking." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사 (걸친 칸 수)
// Space Complexity: 16바이트당 4비트 (3%)
```
## HardwareMemorySafety()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 하드웨어/런타임 메모리 안전 기법을 같은 버그 4가지에 적용해 무엇을 잡는지 비교한다.  하나의 기법이 모든 버그를 잡지는 못한다.
//  버그 A: 바로 옆으로 넘치는 오버플로          버그 B: 멀리(다른 객체 한가운데로) 건너뛰는 오버플로
//  버그 C: 해제 직후 사용                        버그 D: 해제 후 같은 메모리가 새 객체에 재할당된 뒤의 사용
// 기법: 레드존+격리(ASan 식), 태그(MTE 식), 케이퍼빌리티(CHERI, 해제 회수 없음)
struct Obj { int start, size; unsigned tag; bool live; };
struct World {
    std::vector<Obj> objs;      // 할당 목록 (주소순). 객체 사이에는 16바이트 레드존
    World() {                   // 객체 0: [16,48)  객체 1: [64,96)  객체 2: [112,144)
        objs.push_back({16, 32, 1, true}); objs.push_back({64, 32, 2, true}); objs.push_back({112, 32, 3, true});
    }
    int ownerOf(int addr) const { for (size_t i = 0; i < objs.size(); i++) if (objs[i].live && addr >= objs[i].start && addr < objs[i].start + objs[i].size) return i; return -1; }
    bool inRedzone(int addr) const { return ownerOf(addr) < 0; }
};

// 접근 (포인터는 객체 id 의 것, addr 에 접근) 에 대해 각 기법이 탐지하는지
bool redzoneDetects(const World& w, int /*ptrObj*/, int addr, bool freedQuarantined) {
    if (freedQuarantined) return true;                        // 격리 중인 해제 메모리는 독 처리되어 접근 시 탐지
    return w.inRedzone(addr) && addr >= 0;                    // 유효 객체 밖(레드존)에 닿으면 탐지. 다른 객체 한가운데면 탐지 못 함
}
bool tagDetects(const World& w, const Obj& ptrObjSnapshot, int addr, unsigned memTagAtAddr) { (void)w; (void)addr; return memTagAtAddr != ptrObjSnapshot.tag; }
bool capDetects(const Obj& cap, int addr, bool revoked) { if (revoked) return true; return addr < cap.start || addr >= cap.start + cap.size; }

int main() {
    World w;
    const Obj o0 = w.objs[0];                                  // 객체 0 의 포인터를 들고 있다
    // 버그 A: 객체 0 의 끝(48)에 쓰기 -> 레드존
    assert(redzoneDetects(w, 0, 48, false) && tagDetects(w, o0, 48, 0) && capDetects(o0, 48, false));
    // 버그 B: 객체 0 의 포인터로 객체 1 한가운데(80)에 쓰기
    assert(!redzoneDetects(w, 0, 80, false));                 // 레드존은 놓친다 (다른 객체의 유효한 메모리)
    assert(tagDetects(w, o0, 80, w.objs[1].tag) && capDetects(o0, 80, false));    // 태그·케이퍼빌리티는 잡는다
    // 버그 C: 객체 0 을 해제하고 곧바로 옛 포인터로 읽기 (재할당 전)
    w.objs[0].live = false;
    assert(redzoneDetects(w, 0, 20, true) && tagDetects(w, o0, 20, 9));             // 격리 + 해제 시 태그 변경으로 탐지
    assert(!capDetects(o0, 20, false));                       // 회수(revocation) 없는 케이퍼빌리티는 범위가 여전히 유효해 놓친다
    // 버그 D: 같은 주소에 새 객체(태그 4)가 할당된 뒤 옛 포인터로 접근
    w.objs[0] = {16, 32, 4, true};
    assert(!redzoneDetects(w, 0, 20, false));                 // 새 객체의 유효한 메모리라 놓친다
    assert(tagDetects(w, o0, 20, 4));                         // 태그가 달라(1 != 4) 잡는다
    assert(!capDetects(o0, 20, false) && capDetects(o0, 20, true));      // 회수를 하면 잡는다 (CHERI 의 revocation sweep)
    // 요약 행렬 (O = 탐지, X = 놓침)
    std::map<std::string, std::string> matrix = {{"redzone+quarantine", "OXOX"}, {"memory tagging", "OOOO"}, {"capability (no revocation)", "OOXX"}, {"capability + revocation", "OOOO"}};
    for (auto& kv : matrix) std::cout << kv.first << ": A..D = " << kv.second << "\n";
    assert(matrix["memory tagging"] == "OOOO" && matrix["redzone+quarantine"] == "OXOX");
    return 0;
}
// Time Complexity: O(1) 판정
// Space Complexity: O(1)
```
# 부록
## Stack vs Heap
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <new>
#include <random>
#include <vector>
#if defined(__linux__)
#include <csignal>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 스택: 함수 호출과 함께 자동으로 생기고 사라지는 LIFO 영역 (할당 = SP 이동, 해제 = SP 복원).  힙: 프로그래머가 수명을 정하는 영역 (할당기가 알맞은 빈 블록을 찾아야 하므로 느리고 단편화가 생긴다).
//  ① 전역 operator new 를 세어 보면 스택 객체 1000 개는 할당기 호출 0 번, 힙 객체는 호출마다 1 번  ② *같은 연산 열*(중첩 수명 / 무작위 수명)을 스택 할당기(범프+LIFO 해제)와 first-fit 힙(분할·병합)에 흘려 보내 비교: 스택은 연산마다 1 단계(힙은 깊이 d 에서 정확히 d+1 단계)·단편화 0 이고 LIFO 가 아닌 해제를 *거부* 하며,
//  스택은 거부된 해제가 쌓여 결국 공간이 바닥나고(남는 할당 실패), 힙은 무작위 수명에서 탐색 단계가 늘고 외부 단편화가 생기지만 모든 해제를 받아 준다 — 힙의 불변식(블록이 영역을 빈틈없이 덮음, 인접한 빈 블록 없음, 바이트 소유 배열과 일치)을 매 단계 점검
//  ③ 실제 주소: 중첩 호출의 지역 변수 주소는 한 방향으로 단조(스택은 한 방향으로 자란다)이고, 같은 깊이에서 호출하면 *같은 주소* 가 재사용되는 반면 힙 블록은 해제 전까지 겹치지 않음  ④ (Linux) 8 MiB 스택 한도: 자식 프로세스에서 64 MiB 지역 배열을 만지면 SIGSEGV, 같은 크기의 힙은 성공
// audit: no-sanitize (스택 한도 초과를 일부러 일으킨다)
static volatile long newCalls = 0;                             // volatile: new 호출이 전역을 바꾸지 않는다는 컴파일러의 가정을 막는다
static void* volatile escapeSink;                              // 객체 주소를 밖으로 내보내 new/delete 쌍 전체가 제거되지 않게 한다
#pragma GCC diagnostic ignored "-Wmismatched-new-delete"      // 전역 new/delete 를 malloc/free 로 바꿔 치우는 것이 이 실험의 목적
void* operator new(size_t n) { newCalls = newCalls + 1; void* p = std::malloc(n); if (!p) throw std::bad_alloc(); return p; }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, size_t) noexcept { std::free(p); }
struct Point { int x, y; };

class StackAllocator {                                                                                                                                                  // 범프 포인터 + LIFO 해제
public:
    explicit StackAllocator(size_t cap) : cap_(cap) {}
    long alloc(size_t n) { ++steps; if (top_ + n > cap_) return -1; long off = (long)top_; top_ += n; live_.push_back({(size_t)off, n}); return off; }
    bool release(size_t off) { ++steps; if (live_.empty() || live_.back().first != off) { ++refused; return false; } top_ = off; live_.pop_back(); return true; }              // 가장 최근 것만 해제할 수 있다
    long steps = 0, refused = 0; size_t used() const { return top_; }
private:
    size_t cap_, top_ = 0; std::vector<std::pair<size_t, size_t>> live_;
};
class FirstFitHeap {                                                                                                                                                    // 주소순 블록 목록 + 분할/병합
public:
    explicit FirstFitHeap(size_t cap) : cap_(cap), blocks_{{0, cap, true}} {}
    long alloc(size_t n) { ++allocs; for (size_t i = 0; i < blocks_.size(); ++i) { ++scans; Blk& b = blocks_[i]; if (b.free && b.size >= n) { size_t off = b.off; if (b.size > n) { Blk rest{off + n, b.size - n, true}; b.size = n; blocks_.insert(blocks_.begin() + i + 1, rest); } blocks_[i].free = false; return (long)off; } } return -1; }
    bool release(size_t off) { for (size_t i = 0; i < blocks_.size(); ++i) if (blocks_[i].off == off) { if (blocks_[i].free) return false; blocks_[i].free = true;
            if (i + 1 < blocks_.size() && blocks_[i + 1].free) { blocks_[i].size += blocks_[i + 1].size; blocks_.erase(blocks_.begin() + i + 1); } if (i > 0 && blocks_[i - 1].free) { blocks_[i - 1].size += blocks_[i].size; blocks_.erase(blocks_.begin() + i); } return true; } return false; }
    double fragmentation() const { size_t total = 0, largest = 0; for (auto& b : blocks_) if (b.free) { total += b.size; largest = std::max(largest, b.size); } return total == 0 ? 0.0 : 1.0 - (double)largest / (double)total; }
    bool consistent(const std::vector<int>& owner) const { size_t pos = 0; for (size_t i = 0; i < blocks_.size(); ++i) { const Blk& b = blocks_[i]; if (b.off != pos || b.size == 0) return false; if (i > 0 && b.free && blocks_[i - 1].free) return false;      // 빈틈·겹침·인접 빈 블록 금지
            for (size_t k = b.off; k < b.off + b.size; ++k) if ((owner[k] == 0) != b.free) return false; pos += b.size; } return pos == cap_; }                                // 소유 배열과 일치
    long scans = 0, allocs = 0;
private:
    struct Blk { size_t off, size; bool free; }; size_t cap_; std::vector<Blk> blocks_;
};
__attribute__((noinline)) uintptr_t frameAddress(int depth, std::vector<uintptr_t>* trail) { volatile int local = depth; uintptr_t a = (uintptr_t)&local; if (trail) trail->push_back(a); if (depth > 0) a = frameAddress(depth - 1, trail) + 0 * a; return trail ? a : (uintptr_t)&local; }
__attribute__((noinline)) void touchBigStack() { volatile char big[64 << 20]; for (size_t i = 0; i < sizeof big; i += 4096) big[i] = 1; }              // 별도 함수여야 main 의 프레임이 커지지 않는다
__attribute__((noinline)) uintptr_t addressOfLocal() { volatile int local = 0; return (uintptr_t)&local; }
__attribute__((noinline)) uintptr_t callTwiceNested() { return addressOfLocal(); }

int main() {
    long before = newCalls;
    for (int i = 0; i < 1000; i++) { volatile Point p{i, i}; (void)p.x; }                                                                                                       // ① 스택 객체
    assert(newCalls == before);
    for (int i = 0; i < 1000; i++) { Point* p = new Point{i, i}; escapeSink = p; delete p; }
    assert(newCalls == before + 1000);
    Point* escaped = new Point{3, 4}; assert(escaped->y == 4); delete escaped;                                                                                                    // 힙 객체는 함수가 끝나도 살아남을 수 있다
    std::mt19937 rng(909); const size_t CAP = 1 << 15;
    {   StackAllocator st(CAP); FirstFitHeap hp(CAP); std::vector<int> owner(CAP, 0); std::vector<std::pair<size_t, size_t>> nested; int id = 1; long expectedScans = 0;                                        // ② 중첩 수명: 호출 깊이처럼 쌓고 거꾸로 해제
        for (int round = 0; round < 200; ++round) { int depth = 1 + (int)(rng() % 12); std::vector<std::pair<long, long>> frames; for (int d = 0; d < depth; ++d) { expectedScans += d + 1; size_t n = 16 + rng() % 200; long a = st.alloc(n), b = hp.alloc(n); assert(a >= 0 && b >= 0); for (size_t k = 0; k < n; ++k) owner[b + k] = id; frames.push_back({b, (long)n}); ++id; assert(hp.consistent(owner)); frames.back().second = (long)n; nested.push_back({(size_t)a, n}); }
            for (int d = depth - 1; d >= 0; --d) { bool ok = st.release(nested.back().first); assert(ok); nested.pop_back(); ok = hp.release((size_t)frames[d].first); assert(ok); for (long k = 0; k < frames[d].second; ++k) owner[frames[d].first + k] = 0; assert(hp.consistent(owner)); } }
        assert(st.refused == 0 && st.used() == 0 && hp.fragmentation() == 0.0);                                                               // LIFO 일 때는 둘 다 깔끔, 스택은 연산마다 1 단계
        assert(hp.scans == expectedScans && st.steps == 2 * hp.allocs); }                                                                                                         // 힙의 탐색 수: 깊이 d 에서 할당하면 앞의 d 개 사용 블록을 지나 꼬리 빈 블록에서 멈춤 = d+1 (정확한 닫힌 식)
    {   StackAllocator st(CAP); FirstFitHeap hp(CAP); std::vector<int> owner(CAP, 0); struct Live { long stackOff, heapOff; size_t n; int id; }; std::vector<Live> live; int id = 1; double worstFrag = 0, fragSum = 0; long fragSamples = 0, heapFails = 0, stackFails = 0;          // ③ 무작위 수명
        for (int step = 0; step < 6000; ++step) { if (live.size() < 40 || (live.size() < 120 && rng() % 2)) { size_t n = 8 + rng() % 400; long b = hp.alloc(n); long a = st.alloc(n); if (a < 0) ++stackFails; if (b < 0) { ++heapFails; if (a >= 0) { st.release((size_t)a); } continue; } for (size_t k = 0; k < n; ++k) owner[b + k] = id; live.push_back({a, b, n, id++}); }
            else { size_t i = rng() % live.size(); Live v = live[i]; live[i] = live.back(); live.pop_back(); bool ok = hp.release((size_t)v.heapOff); assert(ok); for (size_t k = 0; k < v.n; ++k) { assert(owner[v.heapOff + k] == v.id); owner[v.heapOff + k] = 0; } if (v.stackOff >= 0) st.release((size_t)v.stackOff); }              // 스택은 순서가 안 맞으면 거부
            assert(hp.consistent(owner)); double f = hp.fragmentation(); worstFrag = std::max(worstFrag, f); fragSum += f; ++fragSamples; }
        double avgScan = (double)hp.scans / (double)hp.allocs; assert(st.refused > 100 && stackFails > 100 && heapFails == 0 && avgScan > 10.0 && worstFrag > 0.4 && fragSum / fragSamples > 0.1); }                                       // 힙: 탐색 단계 증가·단편화 발생, 스택: LIFO 가 아니면 거부
    {   std::vector<uintptr_t> trail; frameAddress(10, &trail); assert(trail.size() == 11); bool down = trail[1] < trail[0]; for (size_t i = 1; i < trail.size(); ++i) assert((trail[i] < trail[i - 1]) == down);        // ③ 실제 주소는 한 방향으로 단조
#if !defined(__SANITIZE_ADDRESS__)
        uintptr_t a1 = callTwiceNested(), a2 = callTwiceNested(); assert(a1 == a2);                                                                                                 // 같은 깊이 호출은 같은 주소를 재사용
#endif
        std::vector<char*> blocks; for (int i = 0; i < 100; ++i) blocks.push_back(new char[64 + i]); for (int i = 0; i < 100; ++i) for (int j = i + 1; j < 100; ++j) assert(blocks[i] + 64 + i <= blocks[j] || blocks[j] + 64 + j <= blocks[i]); for (char* b : blocks) delete[] b; }   // 살아 있는 힙 블록은 서로 겹치지 않는다
#if defined(__linux__)
    {   struct rlimit rl; int rc = getrlimit(RLIMIT_STACK, &rl); assert(rc == 0);                                                                                                  // ④ 스택 한도
        if (rl.rlim_cur != RLIM_INFINITY && rl.rlim_cur <= (rlim_t)(16 << 20)) { std::fflush(stdout); pid_t pid = fork(); if (pid == 0) { signal(SIGSEGV, SIG_DFL); touchBigStack(); _exit(0); }
            int st = 0; waitpid(pid, &st, 0); assert(WIFSIGNALED(st) && WTERMSIG(st) == SIGSEGV); }
        std::vector<char> heapBig(64 << 20); for (size_t i = 0; i < heapBig.size(); i += 4096) heapBig[i] = 1; assert(heapBig[4096] == 1); }                                              // 같은 크기의 힙은 성공
#endif
    std::cout << "Stack vs Heap: 1000 stack objects used 0 allocator calls, 1000 heap objects used 1000; on identical nested lifetimes the stack never refused and both stayed unfragmented, on random lifetimes the stack refused out-of-order frees while the first-fit heap scanned more and fragmented" << std::endl;
    return 0;
}
// Time Complexity: 스택 할당·해제 O(1), 힙 first-fit 은 블록 수에 비례
// Space Complexity: 스택은 제한적(MB), 힙은 큼
```
## Pointer vs Reference
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <functional>
#include <iostream>
#include <memory>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

// 포인터: 주소를 담는 *객체* — null 가능, 다른 대상으로 재지정 가능, 산술 연산 가능, 자기 크기(8B)를 가진다.   참조: 기존 객체의 *별칭* — 반드시 초기화, 재바인딩 불가, null 불가, 항상 유효한 객체를 가리켜야 한다.  참조는 보통 컴파일러가 포인터로 구현하지만 언어 규칙이 안전한 사용법을 강제한다.
//  ① 컴파일 시간 사실(static_assert): 역참조는 lvalue 참조, const 변환 방향, 참조 멤버가 있으면 대입 불가, reference_wrapper 는 포인터 크기이고 재바인딩·기본 생성 불가  ② 별칭 의미: 참조에 대입은 재바인딩이 아니라 값 변경, 포인터는 옮겨 다닌다; 무작위 배열로 swap 을 포인터·참조·std::swap 세 가지로 해 같은 결과, 그리고 별칭끼리 swap (XOR 교환은 자기 자신과 바꾸면 0 이 됨)
//  ③ null 표현: 포인터를 돌려주는 find 는 없으면 nullptr, 참조를 돌려주는 find 는 예외 — std::find 와 대조(500 회)하고 돌려받은 포인터·참조로 컨테이너를 고침  ④ 수명 연장: const& / && 에 임시 객체를 묶으면 참조가 사는 동안 소멸하지 않고, 임시 객체의 멤버 함수가 돌려준 참조는 연장되지 않아 문장이 끝나면 소멸한다(역참조는 하지 않고 소멸 횟수만 센다)
//  ⑤ 다형성: 참조·포인터로는 가상 호출이 파생 클래스로 가고, 값으로 받으면 잘려서(slicing) 기반 클래스  ⑥ reference_wrapper: 참조의 벡터를 값으로 정렬해도 원본 배열의 순서는 그대로이고, 참조를 통해 대입하면 원본이 바뀐다 — 정렬 순위를 독립 계산한 순위와 대조; 대입은 *재바인딩*
//  ⑦ 포인터 산술: 포인터 합 == 인덱스 합 == 범위 for 합 (무작위 벡터), 포인터 차 == 인덱스 차, 끝 다음 포인터 비교
static_assert(std::is_same<decltype(*std::declval<int*>()), int&>::value, "포인터 역참조는 lvalue 참조");
static_assert(std::is_same<std::remove_reference<int&>::type, int>::value && std::is_reference<int&>::value && !std::is_reference<int*>::value, "참조 형식과 포인터 형식은 다르다");
static_assert(std::is_convertible<int*, const int*>::value && !std::is_convertible<const int*, int*>::value, "const 는 더할 수만 있고 버릴 수 없다");
static_assert(!std::is_assignable<const int&, int>::value && std::is_assignable<int*&, int*>::value, "const 참조에는 대입할 수 없고 포인터 변수에는 할 수 있다");
static_assert(sizeof(std::reference_wrapper<int>) == sizeof(int*) && !std::is_default_constructible<std::reference_wrapper<int>>::value && std::is_copy_assignable<std::reference_wrapper<int>>::value, "reference_wrapper 는 재바인딩 가능한 참조");
struct HoldsRef { int& r; }; struct HoldsPtr { int* p; };
static_assert(!std::is_copy_assignable<HoldsRef>::value && std::is_copy_assignable<HoldsPtr>::value && !std::is_default_constructible<HoldsRef>::value && std::is_default_constructible<HoldsPtr>::value, "참조 멤버는 대입과 기본 생성을 막는다");
static_assert(sizeof(HoldsPtr) == sizeof(void*) && sizeof(HoldsRef) >= sizeof(void*) / 2, "참조 멤버는 대개 포인터 하나 크기");

void swapPtr(int* a, int* b) { int t = *a; *a = *b; *b = t; }
void swapRef(int& a, int& b) { int t = a; a = b; b = t; }
void xorSwap(int& a, int& b) { a ^= b; b ^= a; a ^= b; }                                                                                                                         // 별칭이면 깨진다
int* findPtr(std::vector<int>& v, int x) { for (int& e : v) if (e == x) return &e; return nullptr; }
int& findRef(std::vector<int>& v, int x) { for (int& e : v) if (e == x) return e; throw std::out_of_range("not found"); }
struct Counted { static int made, destroyed; int v; explicit Counted(int x) : v(x) { ++made; } Counted(const Counted& o) : v(o.v) { ++made; } ~Counted() { ++destroyed; } const Counted& self() const { return *this; } };
int Counted::made = 0, Counted::destroyed = 0;
Counted makeCounted(int v) { return Counted(v); }
struct Animal { virtual ~Animal() {} virtual std::string name() const { return "Animal"; } };
struct Dog : Animal { std::string name() const override { return "Dog"; } };
std::string byValue(Animal a) { return a.name(); } std::string byRef(const Animal& a) { return a.name(); } std::string byPtr(const Animal* a) { return a->name(); }

int main() {
    int a = 1, b = 2; int* p = &a; int& r = a;                                                                                                                                         // ② 별칭 의미
    assert(*p == r && &r == p); p = &b; r = b; assert(*p == 2 && a == 2 && &r == &a); p = nullptr; assert(p == nullptr);
    int arr[3] = {10, 20, 30}; int* q = arr; q += 2; assert(*q == 30 && q - arr == 2 && sizeof(r) == sizeof(int) && sizeof(p) == sizeof(void*));
    std::mt19937 rng(131);
    for (int trial = 0; trial < 200; ++trial) { int x = (int)(rng() % 1000), y = (int)(rng() % 1000); int x1 = x, y1 = y, x2 = x, y2 = y, x3 = x, y3 = y; swapPtr(&x1, &y1); swapRef(x2, y2); std::swap(x3, y3); assert(x1 == x3 && y1 == y3 && x2 == x3 && y2 == y3);   // 세 가지 swap 이 같다
        int v = x; swapRef(v, v); assert(v == x); int z = x; xorSwap(z, z); assert(z == 0); int u = x, w = y; xorSwap(u, w); assert(u == y && w == x); }                                          // 별칭 swap 은 안전하지만 XOR 교환은 자기 자신과 바꾸면 0
    for (int trial = 0; trial < 500; ++trial) { std::vector<int> v(1 + rng() % 30); for (auto& e : v) e = (int)(rng() % 40); int x = (int)(rng() % 45); std::vector<int> copy = v; auto it = std::find(copy.begin(), copy.end(), x);          // ③ null 표현
        int* fp = findPtr(v, x); if (it == copy.end()) { assert(fp == nullptr); bool threw = false; try { findRef(v, x); } catch (const std::out_of_range&) { threw = true; } assert(threw); }
        else { assert(fp != nullptr && fp - v.data() == it - copy.begin() && &findRef(v, x) == fp); *fp = -1; assert(v[it - copy.begin()] == -1); findRef(v, -1) = -2; assert(v[it - copy.begin()] == -2); } }
    {   int made0 = Counted::made, dead0 = Counted::destroyed; { const Counted& r1 = makeCounted(1); Counted&& r2 = makeCounted(2); assert(Counted::made - made0 == 2 && Counted::destroyed - dead0 == 0 && r1.v == 1 && r2.v == 2); }                // ④ 수명 연장
        assert(Counted::destroyed - dead0 == 2); int dead1 = Counted::destroyed; const Counted* dangling = &makeCounted(3).self(); (void)dangling; assert(Counted::destroyed - dead1 == 1); }              // 멤버 함수가 돌려준 참조는 연장 안 됨: 문장이 끝나자 소멸
    {   Dog dog; assert(byRef(dog) == "Dog" && byPtr(&dog) == "Dog" && byValue(dog) == "Animal"); std::vector<Animal> sliced{dog}; std::vector<std::unique_ptr<Animal>> kept; kept.push_back(std::make_unique<Dog>()); std::vector<std::reference_wrapper<Animal>> refs{dog};     // ⑤ 다형성
        assert(sliced[0].name() == "Animal" && kept[0]->name() == "Dog" && refs[0].get().name() == "Dog"); }
    for (int trial = 0; trial < 50; ++trial) { int n = 2 + (int)(rng() % 200); std::vector<int> data(n); std::iota(data.begin(), data.end(), 0); std::shuffle(data.begin(), data.end(), rng); std::vector<int> original = data;               // ⑥ reference_wrapper
        std::vector<std::reference_wrapper<int>> refs(data.begin(), data.end()); std::sort(refs.begin(), refs.end(), [](int x, int y) { return x < y; }); assert(data == original); for (int i = 0; i < n; ++i) assert(refs[i].get() == i);   // 원본은 그대로, 참조만 정렬
        std::vector<int> rank(n); for (int i = 0; i < n; ++i) rank[original[i]] = i; int k = 0; for (auto& ref : refs) ref.get() = k++; for (int i = 0; i < n; ++i) assert(data[i] == original[i]); }                           // 순열이면 순위 대입 결과가 원본과 같다
    { int x0 = 1, x1 = 2; std::reference_wrapper<int> w = x0; w = x1; assert(&w.get() == &x1 && x0 == 1); int& plain = x0; plain = x1; assert(x0 == 2 && &plain == &x0); }                                                 // 대입: wrapper 는 재바인딩, 순수 참조는 값 변경
    for (int trial = 0; trial < 100; ++trial) { std::vector<int> v(1 + rng() % 300); for (auto& e : v) e = (int)(rng() % 1000) - 500; long viaIndex = 0, viaPtr = 0, viaRange = 0; for (size_t i = 0; i < v.size(); ++i) viaIndex += v[i];     // ⑦ 포인터 산술
        for (const int* it = v.data(); it != v.data() + v.size(); ++it) viaPtr += *it; for (const int& e : v) viaRange += e; assert(viaIndex == viaPtr && viaPtr == viaRange); size_t i = rng() % v.size(); assert((v.data() + i) - v.data() == (std::ptrdiff_t)i && v.data() + v.size() > &v.back()); }
    std::cout << "Pointer vs Reference: compile-time rules held; reference assignment changed values while reference_wrapper rebound; three swaps agreed (and XOR swap of an alias gave 0); pointer and reference finders matched std::find in 500 trials; temporaries lived as long as the bound reference but not past the end of a member-returned one; slicing was visible by value only" << std::endl;
    return 0;
}
// Time Complexity: O(1) 접근, 포인터 산술 O(1)
// Space Complexity: 포인터 8B, 참조는 구현 의존(보통 포인터 하나)
```
## malloc vs new
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <new>
#include <random>
#include <stdexcept>
#include <vector>

// malloc: C 함수, 크기(바이트)를 받아 void* 반환, 초기화 없음(생성자 호출 X), 실패 시 NULL.   new: C++ 연산자, 타입을 받아 해당 타입 포인터 반환, 생성자 호출, 실패 시 bad_alloc 예외.
// new 로 만든 것은 delete, malloc 으로 만든 것은 free 로 해제해야 한다 (섞어 쓰면 정의되지 않은 동작)
// 이 예제는 차이를 전역 operator new/delete 를 계측용으로 교체해 눈으로 확인한다 (교체한 함수는 malloc/free 를 부른다):
//  ① 생성자: new 만 호출, 생성자가 예외를 던지면 new 가 자동으로 메모리를 되돌린다(할당 수 == 해제 수), 배열은 이미 만든 원소를 소멸  ② 실패: malloc 은 NULL, new 는 bad_alloc, new(nothrow) 는 nullptr, new_handler 가 있으면 실패할 때마다 호출한 뒤 재시도
//  ③ 크기: new T[n] 이 실제로 요청하는 바이트 = n·sizeof(T) + (소멸자가 필요한 타입이면 원소 수를 적는 8바이트 "쿠키")  ④ 정렬: malloc 은 max_align_t 까지, 과정렬 타입(alignas 64)도 new 는 C++17 부터 맞춰 준다  ⑤ 크기 0: new char[0] 은 항상 서로 다른 널 아닌 포인터
//  ⑥ 클래스별 operator new 를 정의할 수 있다(malloc 은 불가능): 객체 풀·계측에 쓰인다
static long newCalls = 0, deleteCalls = 0; static size_t lastNewSize = 0; static long failCount = 0; static long handlerCalls = 0;
void* operator new(std::size_t n) {
    ++newCalls; lastNewSize = n;
    for (;;) {
        void* p = nullptr; if (failCount > 0) --failCount; else p = std::malloc(n ? n : 1);                 // failCount 만큼은 실패한 것으로 취급 (메모리 부족 흉내)
        if (p) return p;
        std::new_handler h = std::get_new_handler(); if (!h) throw std::bad_alloc(); h();                    // 표준 규칙: 핸들러를 부르고 다시 시도
    }
}
void* operator new[](std::size_t n) { return operator new(n); }
void rawFree(void* p) noexcept { if (p) ++deleteCalls; std::free(p); }
void operator delete(void* p) noexcept { rawFree(p); }
void operator delete[](void* p) noexcept { rawFree(p); }
void operator delete(void* p, std::size_t) noexcept { rawFree(p); }
void operator delete[](void* p, std::size_t) noexcept { rawFree(p); }

struct Widget { static int ctors, dtors; int v = 7; Widget() { ctors++; } ~Widget() { dtors++; } };
int Widget::ctors = 0, Widget::dtors = 0;
struct Plain { int a, b; };                                                    // 소멸자 불필요 (trivially destructible)
struct Thrower { static int built, destroyed; Thrower() { if (built == 2) throw 7; ++built; } ~Thrower() { ++destroyed; } };       // 예외 객체가 operator new 를 쓰지 않도록 int 를 던진다
int Thrower::built = 0, Thrower::destroyed = 0;
struct alignas(64) Big { char c[64]; };
struct Pooled {                                                                // 클래스별 operator new/delete
    static long allocs, frees; char payload[24];
    static void* operator new(std::size_t n) { ++allocs; return ::operator new(n); }
    static void operator delete(void* p) { ++frees; ::operator delete(p); }
};
long Pooled::allocs = 0, Pooled::frees = 0;
void countingHandler() { ++handlerCalls; }

int main() {
    // ① 생성자
    Widget* viaMalloc = (Widget*)std::malloc(sizeof(Widget));        // 메모리만 확보, 객체는 아직 없다
    assert(Widget::ctors == 0);                                       // 생성자 호출 없음 (v 는 쓰레기 값)
    Widget* viaNew = new Widget;
    assert(Widget::ctors == 1 && viaNew->v == 7);                     // 생성자가 호출되고 멤버가 초기화됨
    new (viaMalloc) Widget;                                           // malloc 메모리에 객체를 만들려면 배치 new 가 필요
    assert(Widget::ctors == 2 && viaMalloc->v == 7);
    viaMalloc->~Widget(); std::free(viaMalloc);                       // malloc 짝은 소멸자 직접 호출 + free
    delete viaNew; assert(Widget::dtors == 2);                        // new 짝은 delete
    {   long n0 = newCalls, d0 = deleteCalls; Thrower::built = Thrower::destroyed = 0;
        try { Thrower* t = new Thrower[5]; delete[] t; assert(false); } catch (int) {}                            // 세 번째 생성자에서 예외
        assert(Thrower::built == 2 && Thrower::destroyed == 2);                                                    // 이미 만든 두 원소는 소멸되고
        assert(newCalls - n0 == 1 && deleteCalls - d0 == 1); }                                                      // 메모리도 자동으로 반환 (할당 1, 해제 1)
    // ② 실패
    {   volatile size_t hugeVolatile = std::numeric_limits<size_t>::max() / 4; const size_t HUGE_SIZE = hugeVolatile;       // 컴파일 시간 상수가 아니게 해서 컴파일러가 거부하지 못하게 한다
        assert(std::malloc(HUGE_SIZE) == nullptr);                                                                 // malloc: NULL
        bool threw = false; try { char* p = new char[HUGE_SIZE]; (void)p; } catch (const std::bad_alloc&) { threw = true; } assert(threw);   // new: 예외
        char* np = new (std::nothrow) char[HUGE_SIZE]; assert(np == nullptr);                                      // nothrow new: nullptr
        std::new_handler old = std::set_new_handler(countingHandler); handlerCalls = 0; failCount = 2;           // 두 번 실패하는 상황
        char* ok = new char[16]; assert(ok != nullptr && handlerCalls == 2 && failCount == 0); delete[] ok;       // 핸들러가 실패마다 호출되고 세 번째 시도에서 성공
        std::set_new_handler(old); }
    // ③ 배열 쿠키
    {
#if defined(__GNUC__)
        Widget* w = new Widget[10]; assert(lastNewSize == 10 * sizeof(Widget) + sizeof(size_t)); delete[] w;          // 소멸자가 필요: 원소 수를 적는 쿠키 8바이트가 앞에 붙는다 (Itanium ABI)
        Plain* p = new Plain[10]; assert(lastNewSize == 10 * sizeof(Plain)); delete[] p;                              // 소멸자가 필요 없으면 쿠키도 없다
#endif
        Widget::ctors = Widget::dtors = 0; Widget* w2 = new Widget[4]; assert(Widget::ctors == 4); delete[] w2; assert(Widget::dtors == 4); }   // 배열은 원소마다 생성자·소멸자
    // ④ 정렬
    {   std::mt19937 rng(3); for (int i = 0; i < 2000; ++i) { void* p = std::malloc(1 + rng() % 500); assert((uintptr_t)p % alignof(std::max_align_t) == 0); std::free(p); }   // malloc: max_align_t 정렬
        std::vector<Big*> bigs; for (int i = 0; i < 100; ++i) { Big* b = new Big; assert((uintptr_t)b % 64 == 0); bigs.push_back(b); }                                  // new: 과정렬 타입도 정렬 (C++17)
        for (Big* b : bigs) delete b;
        void* m = std::malloc(sizeof(Big)); bool aligned64 = (uintptr_t)m % 64 == 0; (void)aligned64; std::free(m); }                                                    // malloc 은 64 정렬을 보장하지 않는다 (posix_memalign/aligned_alloc 필요)
    // ⑤ 크기 0
    {   char* a = new char[0]; char* b = new char[0]; assert(a && b && a != b); delete[] a; delete[] b; }
    // ⑥ 클래스별 operator new
    {   Pooled* p = new Pooled; Pooled* q = new Pooled; assert(Pooled::allocs == 2); delete p; delete q; assert(Pooled::frees == 2);
        int* other = new int(5); assert(Pooled::allocs == 2); delete other; }                                                                                              // 다른 타입의 new 에는 영향이 없다
    int* arr = (int*)std::malloc(10 * sizeof(int));                   // 크기를 직접 계산해야 한다 (new int[10] 은 타입이 계산)
    assert(arr); std::free(arr);
    std::cout << "malloc vs new: constructors, exception safety, failure modes, array cookies, alignment and per-class operator new verified with instrumented allocation functions (" << newCalls << " allocations, " << deleteCalls << " frees)." << std::endl;
    return 0;
}
// Time Complexity: 할당기에 따라 다름
// Space Complexity: O(n)
// audit: no-sanitize (전역 operator new/delete 를 교체하므로 새니타이저의 할당 추적과 겹친다)
```
## free vs delete
### 대표코드
```cpp
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <new>
#include <random>
#include <string>
#include <vector>

// free: 메모리만 반환한다 — 소멸자를 부르지 않는다.   delete: 소멸자를 먼저 호출(자원 해제)한 뒤 메모리를 반환한다.
// 소멸자가 파일을 닫거나 락을 푸는 객체에 free 를 쓰면 그 자원이 새어 나간다.   delete[] 는 배열의 모든 원소에 소멸자를 호출한다
// 이 예제는 delete 가 하는 일을 계측해서 보인다:
//  ① free 는 소멸자를 건너뛰어 자원이 샌다  ② 소멸 순서: 파생 소멸자 본문 -> 멤버(선언의 역순) -> 기반 소멸자,  delete[] 는 원소를 역순(n-1 ... 0)으로 소멸  ③ 가상 소멸자가 있으면 기반 포인터로 delete 해도 실제 타입의 소멸자가 불리고
//  크기 있는 해제 함수에 넘어오는 크기도 "실제 타입"의 크기  ④ delete nullptr / free(nullptr) 는 아무 일도 안 한다  ⑤ 무작위 다형 객체 2 000 개를 기반 포인터로 delete: 생성 수 == 소멸 수, 소멸 순서가 생성의 역순(LIFO)일 때 로그가 정확히 거울상
//  ⑥ unique_ptr<T[]> 는 delete[] 를, unique_ptr<T> 는 delete 를 부른다
static std::vector<std::string> logv; static size_t lastDeleteSize = 0; static long allocs = 0, frees = 0;
void* operator new(std::size_t n) { ++allocs; void* p = std::malloc(n ? n : 1); if (!p) throw std::bad_alloc(); return p; }
void rawFree(void* p) noexcept { if (p) ++frees; std::free(p); }
void operator delete(void* p) noexcept { rawFree(p); }
void operator delete(void* p, std::size_t n) noexcept { lastDeleteSize = n; rawFree(p); }
void operator delete[](void* p) noexcept { rawFree(p); }
void operator delete[](void* p, std::size_t) noexcept { rawFree(p); }

struct Resource { static int open; Resource() { open++; } ~Resource() { open--; } };
int Resource::open = 0;
struct Member { std::string name; explicit Member(std::string n) : name(std::move(n)) { logv.push_back("+" + name); } ~Member() { logv.push_back("-" + name); } };
struct Base { Member m; Base() : m("base.m") { logv.push_back("+Base"); } virtual ~Base() { logv.push_back("-Base"); } virtual int tag() const { return 1; } };
struct Derived : Base { Member a, b; char padding[100]; Derived() : a("a"), b("b") { logv.push_back("+Derived"); } ~Derived() override { logv.push_back("-Derived"); } int tag() const override { return 2; } };
struct Leaf : Base { double d[8]; Leaf() { logv.push_back("+Leaf"); } ~Leaf() override { logv.push_back("-Leaf"); } int tag() const override { return 3; } };
struct Counted { static int alive; int id; explicit Counted(int i = 0) : id(i) { ++alive; } ~Counted() { --alive; logv.push_back("~" + std::to_string(id)); } };
int Counted::alive = 0;
struct Numbered { static int next; int id; Numbered() : id(next++) { logv.push_back("n+" + std::to_string(id)); } ~Numbered() { logv.push_back("n-" + std::to_string(id)); } };
int Numbered::next = 0;

int main() {
    logv.reserve(1 << 16);                                            // 로그 벡터가 자라면서 operator new/delete 를 부르지 않도록 미리 확보
    // ① free 는 소멸자를 건너뛴다 (원래 예)
    Resource* a = new Resource; assert(Resource::open == 1);
    delete a; assert(Resource::open == 0);                             // delete: 소멸자 호출 -> 자원 닫힘
    void* raw = std::malloc(sizeof(Resource));
    Resource* b = new (raw) Resource; assert(Resource::open == 1);
    std::free(b);                                                      // free 만 호출: 메모리는 돌려주지만 소멸자는 호출되지 않는다
    assert(Resource::open == 1);                                       // 자원이 닫히지 않은 채 남았다 (누수)
    Resource::open = 0;
    Resource* arr = new Resource[3]; assert(Resource::open == 3);
    delete[] arr; assert(Resource::open == 0);                         // 배열은 delete[] 로: 소멸자 3번
    // ② 소멸 순서
    {   logv.clear(); Derived* d = new Derived;
        assert((logv == std::vector<std::string>{"+base.m", "+Base", "+a", "+b", "+Derived"}));                  // 기반 -> 멤버(선언 순) -> 파생 본문
        logv.clear(); delete d;
        assert((logv == std::vector<std::string>{"-Derived", "-b", "-a", "-Base", "-base.m"}));                  // 정확히 거울상
        logv.clear(); Numbered::next = 0; Numbered* many = new Numbered[4]; delete[] many;
        assert((logv == std::vector<std::string>{"n+0", "n+1", "n+2", "n+3", "n-3", "n-2", "n-1", "n-0"})); }   // 배열 원소는 역순으로 소멸
    // ③ 가상 소멸자와 크기 있는 해제
    {   logv.clear(); Base* p = new Derived; assert(p->tag() == 2); delete p;
        assert(logv.back() == "-base.m" && logv[logv.size() - 5] == "-Derived" && lastDeleteSize == sizeof(Derived));            // 기반 포인터로 지워도 파생 소멸자가 불리고, 크기도 sizeof(Derived)
        Base* q = new Leaf; delete q; assert(lastDeleteSize == sizeof(Leaf) && sizeof(Leaf) != sizeof(Derived));                  // 타입마다 실제 크기가 전달된다
        Base* plain = new Base; delete plain; assert(lastDeleteSize == sizeof(Base)); }
    // ④ 널
    {   long f0 = frees; logv.clear(); Base* nothing = nullptr; delete nothing; std::free(nullptr); assert(frees == f0 && logv.empty()); }
    // ⑤ 무작위 다형 객체
    {   std::mt19937 rng(1); logv.clear(); std::vector<Base*> objs; objs.reserve(2000); long a0 = allocs, f0 = frees; int made = 0;
        for (int i = 0; i < 2000; ++i) { Base* o = (rng() % 3 == 0) ? static_cast<Base*>(new Derived) : (rng() % 2 ? static_cast<Base*>(new Leaf) : new Base); objs.push_back(o); ++made; }
        size_t constructed = logv.size(); assert(constructed > 6000); logv.clear();
        for (size_t i = objs.size(); i-- > 0;) delete objs[i];                                                         // 생성의 역순으로 파괴
        assert(logv.size() == constructed && allocs - a0 == made && frees - f0 == made);                                // 소멸 로그 수 == 생성 로그 수, 할당 수 == 해제 수
        long plus = 0, minus = 0; for (auto& s : logv) { plus += s[0] == '+'; minus += s[0] == '-'; } assert(plus == 0 && minus == (long)constructed); }
    // ⑥ 스마트 포인터가 부르는 해제
    {   logv.clear(); Counted::alive = 0; { std::unique_ptr<Counted[]> arrp(new Counted[3]); assert(Counted::alive == 3); } assert(Counted::alive == 0 && logv.size() == 3);
        { std::unique_ptr<Counted> one(new Counted(9)); assert(Counted::alive == 1); } assert(Counted::alive == 0); }
    std::cout << "free vs delete: free skipped the destructor; delete ran base/member/derived destructors in exact mirror order, delete[] in reverse, and passed the dynamic type's size (2000 random polymorphic objects)." << std::endl;
    return 0;
}
// Time Complexity: delete 는 소멸자 비용 포함
// Space Complexity: O(1)
// audit: no-sanitize (전역 operator new/delete 를 교체하므로 새니타이저의 할당 추적과 겹친다)
```
## Shared Pointer의 순환 참조
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <cassert>

// shared_ptr 은 참조 카운트가 0 이 되어야 해제한다.  두 객체가 서로를 shared_ptr 로 가리키면 카운트가 영원히 1 이상이라 둘 다 해제되지 않는다(누수).
// 해법: 한쪽(보통 자식 -> 부모, 관찰자 방향)을 weak_ptr 로 바꿔 카운트에 포함시키지 않는다
int destroyed = 0;
struct Node { std::shared_ptr<Node> next; ~Node() { destroyed++; } };
struct Parent; struct Child;
struct Parent { std::shared_ptr<Child> child; ~Parent() { destroyed++; } };
struct Child { std::weak_ptr<Parent> parent; ~Child() { destroyed++; } };     // 역방향은 weak

int main() {
    std::shared_ptr<Node> keep;                                              // 순환을 나중에 끊기 위한 손잡이
    {
        auto a = std::make_shared<Node>(), b = std::make_shared<Node>();
        a->next = b; b->next = a;                                            // 순환
        assert(a.use_count() == 2 && b.use_count() == 2);
        keep = b;
    }                                                                        // 지역 변수가 사라져도 서로가 붙들고 있어 해제되지 않는다
    assert(destroyed == 0);                                                  // 누수!
    keep->next.reset(); keep.reset();                                         // 순환을 끊으면 비로소 둘 다 해제된다 (이 실험이 끝난 뒤 누수가 남지 않게)
    assert(destroyed == 2);

    {
        auto p = std::make_shared<Parent>(); auto c = std::make_shared<Child>();
        p->child = c; c->parent = p;                                         // 부모 -> 자식은 shared, 자식 -> 부모는 weak
        assert(p.use_count() == 1 && c.use_count() == 2);                    // 부모의 카운트가 올라가지 않았다
        assert(c->parent.lock() == p);                                       // 필요하면 lock() 으로 잠시 소유권을 얻는다
    }
    assert(destroyed == 4);                                                  // 정상적으로 둘 다 해제 (순환 2 개 + 부모/자식 2 개)
    std::cout << "Cycle of shared_ptr leaked (destroyed=0); weak_ptr back-reference freed both." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 누수 시 영구 점유
```
## 왜 캐시 미스가 성능을 떨어뜨리는가?
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <list>
#include <numeric>
#include <random>
#include <vector>

// 평균 메모리 접근 시간 AMAT = 적중 시간 + 미스율 × 미스 비용.  L1 적중은 약 4사이클이지만 DRAM 접근은 약 200사이클로 50배 느리다.
// 그래서 미스율이 작아 보여도 평균이 크게 나빠진다: 미스율 5% 만 돼도 AMAT 이 3.5 배가 된다.  캐시 지역성이 곧 성능이다
// 이 예제는 공식을 3 단계 캐시 시뮬레이터(L1 32KB 8방향 4사이클, L2 256KB 8방향 12, L3 8MB 16방향 40, DRAM 200)로 실제 접근열에 적용한다:
//  ① 시뮬레이터가 센 총 사이클 / 접근 수 == 공식 l1 + m1(l2 + m2(l3 + m3·mem)) (측정한 조건부 미스율로, 오차 1e-9)  ② 균일 무작위 접근의 적중 확률은 용량/작업 집합 크기: 작업 집합을 16KB ... 64MB 로 키우며
//  측정 AMAT 가 이론값의 3% 안, 8 배 커질 때마다 계단식으로 나빠짐  ③ 구조체 배열(AoS)에서 필드 하나만 합산하면 배열의 배열(SoA)보다 정확히 16 배 많은 라인을 읽는다(64B 구조체, 4B 필드)
//  ④ 다음 줄 미리 가져오기(프리페치) 깊이 d 이면 순차 스캔의 미스가 정확히 1/(d+1) 로 줄지만 포인터 따라가기(무작위 순서)에는 효과가 없다  ⑤ 같은 줄을 반복 접근하는 코드와 줄마다 한 번만 쓰는 코드의 사이클 차이
double amat(double hit, double missRate, double penalty) { return hit + missRate * penalty; }
double amat3(double l1, double l2, double l3, double mem, double m1, double m2, double m3) { return l1 + m1 * (l2 + m2 * (l3 + m3 * mem)); }

struct Level {
    size_t sets, ways; std::vector<std::list<uint64_t>> s; long hits = 0, misses = 0;
    Level(size_t lines, size_t w) : sets(lines / w), ways(w), s(lines / w) {}
    bool access(uint64_t line) {
        auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); ++hits; return true; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); ++misses; return false;
    }
    void install(uint64_t line) { auto& set = s[line % sets]; for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); return; } set.push_front(line); if (set.size() > ways) set.pop_back(); }
};
struct Hierarchy {
    Level l1{512, 8}, l2{4096, 8}, l3{131072, 16}; const double c1 = 4, c2 = 12, c3 = 40, cm = 200; double cycles = 0; long accesses = 0, dram = 0; int prefetchDepth = 0;
    void access(uint64_t addr) {
        uint64_t line = addr / 64; ++accesses; cycles += c1;
        if (l1.access(line)) return;
        cycles += c2;
        if (!l2.access(line)) { cycles += c3; if (!l3.access(line)) { cycles += cm; ++dram; } }
        for (int d = 1; d <= prefetchDepth; ++d) l1.install(line + (uint64_t)d);                         // 미리 가져오기: 다음 줄들을 L1 에 채운다 (사이클 비용 없이)
    }
    double measured() const { return cycles / (double)accesses; }
    double formula() const {                                                                              // 측정한 조건부 미스율로 계산한 공식
        double m1 = (double)l1.misses / (double)(l1.hits + l1.misses), m2 = l2.hits + l2.misses ? (double)l2.misses / (double)(l2.hits + l2.misses) : 0, m3 = l3.hits + l3.misses ? (double)l3.misses / (double)(l3.hits + l3.misses) : 0;
        return amat3(c1, c2, c3, cm, m1, m2, m3);
    }
};

int main() {
    const double L1 = 4, DRAM = 200;
    assert(amat(L1, 0.00, DRAM) == 4 && amat(L1, 0.01, DRAM) == 6);                  // 원래 공식: 1% 미스면 평균 50% 증가
    assert(std::fabs(amat(L1, 0.05, DRAM) - 14) < 1e-9 && amat(L1, 0.20, DRAM) / amat(L1, 0.0, DRAM) == 11);
    assert(amat3(4, 12, 40, 200, 0.10, 0.20, 0.30) < amat(4, 0.10, 200));            // 다단계 캐시는 같은 L1 미스율에서 훨씬 낫다
    // ①② 균일 무작위 접근: 작업 집합 크기에 따른 AMAT
    std::mt19937_64 rng(1); double prev = 0; int stepsUp = 0;
    for (uint64_t W : {16ULL << 10, 128ULL << 10, 2ULL << 20, 64ULL << 20}) {
        uint64_t lines = W / 64; Hierarchy g; for (uint64_t i = 0; i < 700000; ++i) g.access((rng() % lines) * 64);                  // 워밍업
        g.cycles = 0; g.accesses = 0; g.l1.hits = g.l1.misses = g.l2.hits = g.l2.misses = g.l3.hits = g.l3.misses = 0;
        for (int i = 0; i < 400000; ++i) g.access((rng() % lines) * 64);
        assert(std::fabs(g.measured() - g.formula()) < 1e-9);                                                   // ① 시뮬레이터 == 공식
        auto miss = [&](double capacityLines) { return 1.0 - std::min(1.0, capacityLines / (double)lines); };  // 균일 무작위: 단계마다 적중 확률 = 용량 / 작업 집합 (그 단계가 보는 접근열에서)
        double theory = amat3(4, 12, 40, 200, miss(512), miss(4096), miss(131072));
        assert(std::fabs(g.measured() - theory) / theory < 0.06);                                               // ② 이론값의 6% 안
        if (prev > 0 && g.measured() > prev * 1.05) ++stepsUp;
        prev = g.measured();
    }
    assert(stepsUp >= 3);                                                                                        // 작업 집합이 한 단계 커질 때마다 평균이 계단식으로 나빠진다
    // ③ AoS vs SoA
    {   const uint64_t N = 100000; Hierarchy aos, soa; for (uint64_t i = 0; i < N; ++i) aos.access(i * 64);              // 64B 구조체의 첫 필드만 합산
        for (uint64_t i = 0; i < N; ++i) soa.access(i * 4);                                                              // 같은 필드만 모은 4B 배열
        assert(aos.l1.misses == 100000 && soa.l1.misses == 6250 && aos.l1.misses == 16 * soa.l1.misses && aos.cycles > 4 * soa.cycles); }
    // ④ 프리페치
    {   const uint64_t lines = 20000; for (int depth : {0, 1, 3, 7}) {
            Hierarchy seq; seq.prefetchDepth = depth; for (uint64_t i = 0; i < lines; ++i) seq.access(i * 64);              // 순차 스캔: 줄마다 한 번
            assert(seq.l1.misses == (long)((lines + (uint64_t)depth) / (uint64_t)(depth + 1)));                              // 미스가 정확히 1/(d+1)
            Hierarchy chase; chase.prefetchDepth = depth; std::vector<uint64_t> perm(lines); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
            for (uint64_t i : perm) chase.access(i * 64 * 8);                                                                 // 포인터 따라가기: 이웃하지 않는 줄 (여덟 줄 간격)
            assert(chase.l1.misses == (long)lines);                                                                          // 프리페치로 줄지 않는다
        } }
    // ⑤ 같은 줄 재사용
    {   Hierarchy reuse, once; const int N = 200000; for (int i = 0; i < N; ++i) reuse.access((uint64_t)(i / 16) * 64 + (uint64_t)(i % 16) * 4); for (int i = 0; i < N; ++i) once.access((uint64_t)i * 64);
        assert(reuse.l1.misses == N / 16 && once.l1.misses == N && once.cycles / reuse.cycles > 5); }                         // 줄 안의 16 개 값을 모두 쓰면 미스는 1/16
    std::cout << "Cache misses: simulated 3-level AMAT matched the closed form to 1e-9, tracks capacity/working-set (random access), AoS touches exactly 16x the lines of SoA, prefetch depth d cuts sequential misses to 1/(d+1) but not pointer chasing." << std::endl;
    return 0;
}
// Time Complexity: O(1) 공식, 시뮬레이션 O(접근 수 · 방향 수)
// Space Complexity: O(캐시 라인 수)
```
## 페이지 교체 알고리즘(LRU, Clock)
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <deque>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <set>
#include <vector>

// 프레임이 가득 찼을 때 어느 페이지를 내보낼까?  OPT(앞으로 가장 늦게 쓸 페이지, 미래를 알아야 하므로 이론적 하한)  /  LRU(가장 오래 안 쓴 페이지, 정확하지만 매 접근마다 갱신이 필요해 비싸다)
// Clock(Second Chance): LRU 를 싸게 근사한다 — 프레임을 원형으로 놓고 참조 비트를 보며 시계바늘이 돈다.  비트가 1 이면 0 으로 내리고 한 번 더 기회를 주고, 0 이면 쫓아낸다.  FIFO 는 구현이 가장 단순하지만 성능이 나쁘다
// 이 예제는 LRU 를 근사하는 방법들을 같은 접근열에 적용해 비교한다 — FIFO, LRU(정확), Clock, Aging(8 비트 카운터를 주기적으로 오른쪽 이동하고 참조 비트를 맨 앞에 넣음), LRU-2(최근 두 번째 참조가 가장 오래된 페이지를 내보냄, 한 번만 쓰인 페이지가 먼저 나감), OPT
// 검증: ① 교과서 참조열(프레임 3 개): FIFO 15, LRU 12, OPT 9, Clock 은 OPT 이상 FIFO 이하  ② 지역성이 있는 Zipf 접근 20 000 번(200 페이지, 프레임 16): OPT <= 모든 알고리즘, Clock 은 LRU 의 ±10% 안, Aging 은 ±15% 안, 둘 다 FIFO 보다 좋음
//        ③ 새 페이지만 계속 나오는 접근열에서는 Clock 이 FIFO 와 정확히 같은 상주 집합을 매 단계 유지  ④ 한 번만 훑는 큰 스캔이 섞인 작업(핫 페이지 8 개 + 페이지 50 개 스캔 반복, 프레임 12 개): LRU 는 스캔에 핫 페이지를 빼앗기지만 LRU-2 는 지킨다(스캔의 피할 수 없는 폴트 2 000 번을 뺀 추가 폴트가 10 배 이상 적음)
//        ⑤ 프레임보다 한 페이지 더 큰 순환: LRU·FIFO·Clock 모두 매번 폴트(최악), OPT 는 훨씬 적음  ⑥ 접근마다 하는 일: LRU 는 적중마다 순서 갱신(리스트 이동), Clock 은 비트 하나만 켬 — 적중 때의 "순서 변경 횟수" 를 센다
enum Algo { FIFO, LRU, CLOCK, AGING, LRU2, OPT };
struct Stats { long faults = 0, reorders = 0; std::vector<std::set<int>> resident; };

Stats simulate(Algo algo, size_t F, const std::vector<int>& tr, bool keepHistory = false) {
    Stats st; std::set<int> res; size_t n = tr.size();
    std::deque<int> fifo; std::map<int, long> lastUse; std::list<int> lruList; std::map<int, std::list<int>::iterator> pos;
    std::vector<int> ring(F, -1); std::vector<char> ref(F, 0); size_t hand = 0;
    std::map<int, unsigned> counter; std::map<int, char> refBit; std::map<int, long> loadedAt;
    std::map<int, std::pair<long, long>> hist;                                            // LRU-2: (가장 최근 참조, 그 직전 참조), 없으면 -1
    std::vector<size_t> nextUse(n); { std::map<int, size_t> nxt; for (size_t i = n; i-- > 0;) { auto it = nxt.find(tr[i]); nextUse[i] = it == nxt.end() ? n + 1 : it->second; nxt[tr[i]] = i; } }
    std::map<int, size_t> nextOf;
    for (size_t t = 0; t < n; ++t) {
        int p = tr[t]; bool hit = res.count(p) > 0;
        if (algo == AGING && t % 8 == 0) { for (int q : res) { counter[q] = (counter[q] >> 1) | (refBit[q] ? 0x80u : 0u); refBit[q] = 0; } }       // 주기적으로 카운터 갱신
        if (!hit) {
            ++st.faults;
            if (res.size() == F) {
                int victim = -1;
                if (algo == FIFO) { victim = fifo.front(); fifo.pop_front(); }
                else if (algo == LRU) { long old = 1L << 60; for (int q : res) if (lastUse[q] < old) { old = lastUse[q]; victim = q; } }
                else if (algo == CLOCK) { while (ref[hand]) { ref[hand] = 0; hand = (hand + 1) % F; } victim = ring[hand]; ring[hand] = p; ref[hand] = 1; hand = (hand + 1) % F; }
                else if (algo == AGING) { unsigned best = ~0u; long oldest = 1L << 60; for (int q : res) { if (counter[q] < best || (counter[q] == best && loadedAt[q] < oldest)) { best = counter[q]; oldest = loadedAt[q]; victim = q; } } }
                else if (algo == LRU2) { long bestKey = 1L << 60, bestTie = 1L << 60; for (int q : res) { long k = hist[q].second, tie = hist[q].first; if (k < bestKey || (k == bestKey && tie < bestTie)) { bestKey = k; bestTie = tie; victim = q; } } }      // 직전 참조가 없으면(-1) 가장 먼저 나간다
                else { size_t far = 0; for (int q : res) if (nextOf[q] >= far) { if (nextOf[q] > far || victim < 0) victim = q; far = nextOf[q]; } }
                res.erase(victim);
                if (algo == AGING) { counter.erase(victim); refBit.erase(victim); loadedAt.erase(victim); } if (algo == LRU2) hist.erase(victim);
            } else if (algo == CLOCK) { for (size_t i = 0; i < F; ++i) if (ring[i] < 0) { ring[i] = p; ref[i] = 1; break; } }
            res.insert(p);
            if (algo == FIFO) fifo.push_back(p);
            if (algo == LRU) { lruList.push_front(p); pos[p] = lruList.begin(); }
            if (algo == AGING) { counter[p] = 0; refBit[p] = 1; loadedAt[p] = (long)t; }
            if (algo == LRU2) hist[p] = {(long)t, -1};
        } else {
            if (algo == CLOCK) { for (size_t i = 0; i < F; ++i) if (ring[i] == p) ref[i] = 1; }                      // 적중: 비트 하나만 켠다 (순서는 안 바뀐다)
            if (algo == LRU) { lruList.erase(pos[p]); lruList.push_front(p); pos[p] = lruList.begin(); ++st.reorders; }
            if (algo == AGING) refBit[p] = 1;
            if (algo == LRU2) { hist[p] = {(long)t, hist[p].first}; }
        }
        lastUse[p] = (long)t; nextOf[p] = nextUse[t];
        if (keepHistory) st.resident.push_back(res);
    }
    return st;
}

std::vector<int> zipfTrace(int pages, int len, uint32_t seed) {
    std::mt19937 rng(seed); std::vector<double> cdf(pages); double sum = 0; for (int i = 0; i < pages; ++i) { sum += 1.0 / (i + 1); cdf[i] = sum; }
    std::vector<int> t(len); for (int& x : t) { double u = (double)(rng() % 1000000) / 1000000.0 * sum; x = (int)(std::lower_bound(cdf.begin(), cdf.end(), u) - cdf.begin()); } return t;
}

int main() {
    // ① 교과서 참조열
    std::vector<int> refs = {7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1};
    assert(simulate(FIFO, 3, refs).faults == 15 && simulate(LRU, 3, refs).faults == 12 && simulate(OPT, 3, refs).faults == 9);
    long c = simulate(CLOCK, 3, refs).faults; assert(c >= 9 && c <= 15);
    // ② Zipf 접근
    long totals[6] = {0, 0, 0, 0, 0, 0};
    for (uint32_t seed = 1; seed <= 5; ++seed) {
        auto tr = zipfTrace(200, 20000, seed); long f[6]; for (int a = 0; a < 6; ++a) { f[a] = simulate((Algo)a, 16, tr).faults; totals[a] += f[a]; }
        for (int a = 0; a < 5; ++a) assert(f[OPT] <= f[a]);
        assert(std::abs((double)f[CLOCK] - (double)f[LRU]) / (double)f[LRU] < 0.10);                          // Clock 은 LRU 의 ±10%
        assert(std::abs((double)f[AGING] - (double)f[LRU]) / (double)f[LRU] < 0.15 && f[LRU] < f[FIFO] && f[CLOCK] < f[FIFO] && f[AGING] < f[FIFO]);
    }
    // ③ 새 페이지만 나오면 Clock == FIFO
    {   std::vector<int> fresh(300); for (int i = 0; i < 300; ++i) fresh[(size_t)i] = i; auto a = simulate(CLOCK, 8, fresh, true), b = simulate(FIFO, 8, fresh, true); assert(a.resident == b.resident && a.faults == 300 && b.faults == 300); }
    // ④ 스캔 저항성
    {   std::mt19937 rng(9); std::vector<int> tr; int nextScan = 1000;
        for (int round = 0; round < 40; ++round) { for (int i = 0; i < 100; ++i) tr.push_back((int)(rng() % 8)); for (int i = 0; i < 50; ++i) tr.push_back(nextScan++); }       // 핫 페이지 8 개 + 한 번만 훑는 페이지 50 개
        long lru = simulate(LRU, 12, tr).faults, lru2 = simulate(LRU2, 12, tr).faults, clock = simulate(CLOCK, 12, tr).faults, opt = simulate(OPT, 12, tr).faults;
        const long coldScan = 40 * 50;                                                                              // 스캔 페이지 2 000 개는 처음 보는 페이지라 어떤 알고리즘이든 폴트
        assert(lru > coldScan && lru2 >= coldScan && (lru - coldScan) > 10 * (lru2 - coldScan) + 1 && opt <= lru2 && opt <= clock); }                // 핫 페이지가 스캔에 쫓겨나 겪는 추가 폴트: LRU 는 수백 번, LRU-2 는 거의 0
    // ⑤ 순환
    for (size_t F : {(size_t)4, (size_t)10}) {
        std::vector<int> cyc; for (int k = 0; k < 30; ++k) for (size_t i = 0; i < F + 1; ++i) cyc.push_back((int)i);
        long lru = simulate(LRU, F, cyc).faults, fifo = simulate(FIFO, F, cyc).faults, clk = simulate(CLOCK, F, cyc).faults, opt = simulate(OPT, F, cyc).faults;
        assert(lru == (long)cyc.size() && fifo == (long)cyc.size() && clk == (long)cyc.size() && opt < lru / 2); }
    // ⑥ 적중 때 하는 일
    {   auto tr = zipfTrace(200, 20000, 3); auto l = simulate(LRU, 16, tr), k = simulate(CLOCK, 16, tr); assert(l.reorders == (long)tr.size() - l.faults && k.reorders == 0); }
    std::cout << "Page replacement: textbook trace OPT=9 LRU=12 FIFO=15; on Zipf traces Clock/Aging stay within 10%/15% of exact LRU (faults " << totals[LRU] << " / " << totals[CLOCK] << " / " << totals[AGING] << " vs FIFO " << totals[FIFO]
              << ", OPT " << totals[OPT] << "); LRU-2 resists scans." << std::endl;
    return 0;
}
// Time Complexity: LRU 접근당 O(1) (리스트 + 해시), Clock 은 분할상환 O(1) 이고 적중 때 순서 변경이 없다
// Space Complexity: O(프레임 수)
```
## Virtual Memory가 필요한 이유
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 가상 메모리가 주는 것: (1) 격리 — 프로세스마다 독립된 주소 공간이라 서로의 메모리를 볼 수 없다  (2) 단순한 프로그래밍 모델 — 모든 프로세스가 같은 가상 주소(예: 0x1000)를 쓸 수 있다
// (3) 공유 — 읽기 전용 라이브러리 페이지를 한 프레임에 매핑해 여러 프로세스가 함께 쓴다  (4) 물리 메모리보다 큰 주소 공간(요구 페이징·스왑)  (5) 보호 — 페이지별 권한
// 이 구현은 작은 운영체제를 만든다: 물리 프레임 8 개, 프로세스 3 개, 프로세스마다 익명 페이지 24 개(요구 영(零) 페이지, 스왑 가능) + 공유 라이브러리 페이지 2 개(읽기 전용, 파일에서 다시 읽을 수 있어 그냥 버릴 수 있음).
//  첫 접근은 마이너 폴트(프레임 배정, 0 으로 채움), 쫓겨난 페이지의 재접근은 메이저 폴트(스왑에서 읽음), 프레임이 없으면 Clock 으로 희생 페이지를 골라 더러우면 스왑에 쓴다(안 썼으면 그냥 버림), 라이브러리 쓰기는 보호 폴트, 범위 밖은 세그폴트
// 검증: ① 무작위 연산 40 000 번(읽기/쓰기, 세 프로세스가 번갈아)을 "프로세스마다 독립된 배열" 모형과 대조 — 읽은 값이 항상 같고(격리), 같은 가상 주소를 써도 서로 영향이 없으며, 스왑을 오가도 값이 보존된다
//        ② 가상 페이지 합 78 개가 프레임 8 개를 크게 넘는데도 동작(과예약)  ③ 불변식: 사용 중 프레임 <= 8, 프레임의 참조 수 == 그 프레임을 가리키는 현재 PTE 수, 라이브러리 프레임은 최대 3 프로세스가 공유(프레임은 한 벌)
//        ④ 지역성: 작업 집합이 프레임보다 작으면 워밍업 뒤 메이저 폴트가 거의 없고, 세 프로세스의 작업 집합 합이 프레임보다 크면 폴트가 폭증(스래싱)
const int FRAMES = 8, ANON = 24, LIBPAGES = 2, VPAGES = ANON + LIBPAGES, PROCS = 3;
const int libContent[LIBPAGES] = {1111, 2222};
enum Result { OK, SEGV, PROT };
struct PTE { enum State { UNTOUCHED, PRESENT, SWAPPED } st = UNTOUCHED; int frame = -1, swapSlot = -1; };
struct Frame { bool used = false, referenced = false, dirty = false, isLib = false; int value = 0, libIndex = -1; std::vector<std::pair<int, int>> maps; };

class Os {
    Frame frames[FRAMES]; PTE pt[PROCS][VPAGES]; std::map<int, int> swap; int nextSlot = 0, hand = 0;
    int allocFrame() {
        for (int i = 0; i < FRAMES; ++i) if (!frames[i].used) return i;
        for (;;) {                                                                       // Clock: 참조 비트가 있으면 한 번 기회를 준다
            Frame& f = frames[hand]; int idx = hand; hand = (hand + 1) % FRAMES;
            if (f.referenced) { f.referenced = false; continue; }
            if (f.isLib) { for (auto& m : f.maps) pt[m.first][m.second] = PTE(); }          // 라이브러리: 파일에서 다시 읽을 수 있으니 그냥 버린다
            else {
                auto m = f.maps[0]; PTE& e = pt[m.first][m.second];
                if (f.dirty) { if (e.swapSlot < 0) e.swapSlot = nextSlot++; swap[e.swapSlot] = f.value; e.st = PTE::SWAPPED; ++swapOuts; }          // 더러우면 스왑에 쓴다
                else if (e.swapSlot >= 0) e.st = PTE::SWAPPED;                           // 스왑에 같은 내용이 이미 있다
                else e = PTE();                                                          // 쓴 적이 없으면 0 으로 되돌아가므로 버려도 된다
                e.frame = -1;
            }
            f = Frame(); return idx;
        }
    }
    int ensure(int pid, int v) {                                                         // 페이지를 메모리에 올리고 프레임 번호를 돌려준다
        PTE& e = pt[pid][v];
        if (e.st == PTE::PRESENT) { frames[e.frame].referenced = true; return e.frame; }
        if (v >= ANON) {                                                                 // 공유 라이브러리: 이미 올라와 있으면 같은 프레임에 매핑
            int li = v - ANON; for (int i = 0; i < FRAMES; ++i) if (frames[i].used && frames[i].isLib && frames[i].libIndex == li) { frames[i].maps.push_back({pid, v}); e.st = PTE::PRESENT; e.frame = i; frames[i].referenced = true; ++minor; return i; }
            int fi = allocFrame(); Frame& f = frames[fi]; f = Frame(); f.used = true; f.isLib = true; f.libIndex = li; f.value = libContent[li]; f.referenced = true; f.maps.push_back({pid, v}); pt[pid][v].st = PTE::PRESENT; pt[pid][v].frame = fi; ++minor; return fi;
        }
        bool swappedIn = e.st == PTE::SWAPPED; int slot = e.swapSlot; int fi = allocFrame(); Frame& f = frames[fi]; f = Frame(); f.used = true; f.referenced = true; f.maps.push_back({pid, v});
        PTE& e2 = pt[pid][v]; e2.st = PTE::PRESENT; e2.frame = fi; e2.swapSlot = slot;
        if (swappedIn) { f.value = swap[slot]; ++major; ++swapIns; } else { f.value = 0; ++minor; }
        return fi;
    }
public:
    long minor = 0, major = 0, swapOuts = 0, swapIns = 0, protFaults = 0, segvs = 0;
    Result read(int pid, int v, int& out) { if (v < 0 || v >= VPAGES) { ++segvs; return SEGV; } int fi = ensure(pid, v); out = frames[fi].value; return OK; }
    Result write(int pid, int v, int val) {
        if (v < 0 || v >= VPAGES) { ++segvs; return SEGV; } if (v >= ANON) { ++protFaults; return PROT; }
        int fi = ensure(pid, v); frames[fi].value = val; frames[fi].dirty = true; return OK;
    }
    void check() const {
        int used = 0; for (int i = 0; i < FRAMES; ++i) {
            const Frame& f = frames[i]; if (!f.used) { assert(f.maps.empty()); continue; } ++used;
            int present = 0; for (int p = 0; p < PROCS; ++p) for (int v = 0; v < VPAGES; ++v) if (pt[p][v].st == PTE::PRESENT && pt[p][v].frame == i) ++present;
            assert(present == (int)f.maps.size() && present >= 1 && (f.isLib ? present <= PROCS : present == 1));       // 참조 수 == 그 프레임을 가리키는 PTE 수, 익명 페이지는 한 프로세스 전용
            for (auto& m : f.maps) assert(pt[m.first][m.second].st == PTE::PRESENT && pt[m.first][m.second].frame == i);
        }
        assert(used <= FRAMES);
        for (int p = 0; p < PROCS; ++p) for (int v = 0; v < VPAGES; ++v) { const PTE& e = pt[p][v]; if (e.st == PTE::SWAPPED) assert(e.swapSlot >= 0 && swap.count(e.swapSlot)); if (e.st == PTE::PRESENT) assert(e.frame >= 0 && frames[e.frame].used); }
    }
    int framesUsed() const { int u = 0; for (auto& f : frames) u += f.used; return u; }
};

int main() {
    // 원래 예: 격리와 공유
    {   Os os; int out; assert(os.write(0, 1, 111) == OK && os.write(1, 1, 222) == OK);
        assert(os.read(0, 1, out) == OK && out == 111 && os.read(1, 1, out) == OK && out == 222);                   // 같은 주소를 읽어도 각자 자기 데이터 (격리)
        assert(os.read(0, 2, out) == OK && out == 0 && os.read(0, VPAGES, out) == SEGV && os.read(0, -1, out) == SEGV);   // 첫 접근은 0, 범위 밖은 세그폴트
        assert(os.read(0, ANON, out) == OK && out == 1111 && os.read(1, ANON, out) == OK && out == 1111 && os.read(2, ANON, out) == OK && out == 1111);   // 라이브러리 값 공유
        assert(os.write(0, ANON, 5) == PROT);                                                                        // 쓰기 보호
        os.check(); }
    // ① 무작위 연산과 모형
    {   Os os; std::mt19937 rng(7); std::vector<std::vector<int>> model(PROCS, std::vector<int>(ANON, 0)); long reads = 0, writes = 0, prot = 0, segv = 0, maxUsed = 0;
        for (int step = 0; step < 40000; ++step) {
            int pid = (int)(rng() % PROCS), op = (int)(rng() % 100); int v = (rng() % 20 == 0) ? (int)(rng() % (VPAGES + 6)) - 2 : (int)(rng() % VPAGES); int out = -99;
            if (op < 55) { Result r = os.read(pid, v, out); ++reads;
                if (v < 0 || v >= VPAGES) { assert(r == SEGV); ++segv; } else { assert(r == OK && out == (v < ANON ? model[(size_t)pid][(size_t)v] : libContent[v - ANON])); } }
            else { int val = (int)(rng() % 100000) + 1; Result r = os.write(pid, v, val); ++writes;
                if (v < 0 || v >= VPAGES) { assert(r == SEGV); ++segv; } else if (v >= ANON) { assert(r == PROT); ++prot; } else { assert(r == OK); model[(size_t)pid][(size_t)v] = val; } }
            maxUsed = std::max<long>(maxUsed, os.framesUsed());
            if (step % 50 == 0) os.check();
        }
        for (int p = 0; p < PROCS; ++p) for (int v = 0; v < ANON; ++v) { int out; assert(os.read(p, v, out) == OK && out == model[(size_t)p][(size_t)v]); }       // 끝까지 모든 값이 보존
        assert(maxUsed <= FRAMES && os.major > 1000 && os.swapOuts > 1000 && os.swapIns == os.major && os.protFaults == prot && os.segvs == segv && PROCS * VPAGES > 9 * FRAMES);      // 가상 페이지 78 개 vs 프레임 8 개
    }
    // ④ 지역성과 스래싱
    {   auto majorFaults = [&](int procs, int workingSet) {
            Os os; std::mt19937 rng(5); int out;
            for (int step = 0; step < 4000; ++step) { int pid = step % procs; os.read(pid, (int)(rng() % (unsigned)workingSet), out); }                                      // 워밍업
            long m0 = os.major; for (int step = 0; step < 20000; ++step) { int pid = step % procs; os.write(pid, (int)(rng() % (unsigned)workingSet), step); } return os.major - m0; };
        long fits = majorFaults(1, 7), thrash = majorFaults(3, 7);                                                // 한 프로세스의 작업 집합 7 <= 프레임 8, 세 프로세스는 합 21 > 8
        assert(fits == 0 && thrash > 5000);
        std::cout << "Virtual memory: 3 processes x 26 virtual pages ran correctly on 8 frames (isolation, shared library frame, demand-zero, swap); steady-state major faults " << fits << " when the working set fits vs " << thrash << " when it does not." << std::endl; }
    return 0;
}
// Time Complexity: 접근 O(1) (적중), 폴트 O(프레임 수) (Clock)
// Space Complexity: O(프로세스 수 · 가상 페이지 수 + 스왑 크기)
```
## 메모리 단편화(Fragmentation)
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// 내부 단편화: 블록 안에서 요청보다 크게 줘서 낭비 (크기 클래스 올림, 페이지 올림).   외부 단편화: 빈 공간의 합은 충분하지만 연속된 큰 조각이 없어 할당 실패.
// 해결: 외부 -> 압축(compaction, 이동), 페이징(연속일 필요 없음), 버디/슬랩;  내부 -> 크기 클래스 세분화
// 이 예제는 두 종류의 낭비를 숫자로 확인한다:
//  ① 내부 단편화: 요청 크기 1..4096 전부에 대해 2의 거듭제곱 크기 클래스는 낭비 비율이 최악 50% 에 가깝고(평균은 계산식과 일치), 한 옥타브를 k 칸으로 나눈 세분화 클래스는 최악 1/(k+1) 미만.  페이지 올림의 평균 낭비는 정확히 (P-1)/2 바이트
//  ② 외부 단편화: 4 096 단위 힙에서 first-fit + 병합으로 무작위 할당·해제를 돌리면 정상 상태에서 빈 구멍 수가 할당된 블록 수의 약 절반 — Knuth 의 "50% 규칙" (0.3 ~ 0.7 안) — 이고, 빈 공간의 합이 충분한데 실패하는 요청이 실제로 생긴다
//  ③ 압축하면 외부 단편화 지수가 0 이 되고 옮긴 블록 수는 첫 구멍 뒤에 있는 블록 수  ④ 크기가 같은 블록만 쓰는 풀은 외부 단편화가 없다: 가득 찰 때만 실패
int sizeClass(int n) { int c = 16; while (c < n) c *= 2; return c; }       // 16, 32, 64, 128 ...
int fineClass(int n, int k) {                                                // 옥타브(2^j .. 2^(j+1))를 k 칸으로 나눈 크기 클래스, 최소 16
    if (n <= 16) return 16; int base = 16; while (base * 2 < n) base *= 2; int step = base / k; return base + ((n - base + step - 1) / step) * step;
}
struct Heap {                                                                // first-fit + 인접 병합
    struct Hole { int off, size; }; std::vector<Hole> holes; std::map<int, int> live; int total;                 // live: 오프셋 -> 크기
    explicit Heap(int n) : total(n) { holes.push_back({0, n}); }
    int alloc(int n) { for (size_t i = 0; i < holes.size(); ++i) if (holes[i].size >= n) { int off = holes[i].off; holes[i].off += n; holes[i].size -= n; if (!holes[i].size) holes.erase(holes.begin() + (long)i); live[off] = n; return off; } return -1; }
    void release(int off) {
        int n = live[off]; live.erase(off); size_t i = 0; while (i < holes.size() && holes[i].off < off) ++i; holes.insert(holes.begin() + (long)i, {off, n});
        if (i + 1 < holes.size() && holes[i].off + holes[i].size == holes[i + 1].off) { holes[i].size += holes[i + 1].size; holes.erase(holes.begin() + (long)i + 1); }
        if (i > 0 && holes[i - 1].off + holes[i - 1].size == holes[i].off) { holes[i - 1].size += holes[i].size; holes.erase(holes.begin() + (long)i); }
    }
    int freeTotal() const { int t = 0; for (auto& h : holes) t += h.size; return t; }
    int largest() const { int m = 0; for (auto& h : holes) m = std::max(m, h.size); return m; }
    double index() const { int t = freeTotal(); return t ? 1.0 - (double)largest() / t : 0.0; }
    long compact() { long moved = 0; int w = 0; std::map<int, int> out; bool seenHole = false; int prevEnd = 0;           // 사용 중 블록을 앞쪽으로 밀어 모은다
        for (auto& kv : live) { if (kv.first != prevEnd) seenHole = true; if (seenHole) ++moved; out[w] = kv.second; w += kv.second; prevEnd = kv.first + kv.second; }
        live = out; holes.clear(); if (w < total) holes.push_back({w, total - w}); return moved; }
};

int main() {
    // 원래 예
    assert(sizeClass(17) == 32 && sizeClass(17) - 17 == 15 && sizeClass(64) == 64);
    {   const int B = 64, N = 100; std::vector<bool> used(N, true); for (int i = 0; i < N; i += 2) used[i] = false;
        auto largestFree = [&]() { int best = 0, run = 0; for (bool u : used) { run = u ? 0 : run + 1; best = std::max(best, run); } return best * B; };
        int totalFree = 0; for (bool u : used) totalFree += u ? 0 : B; assert(totalFree == 3200 && largestFree() == 64 && largestFree() < 128);
        double fragmentation = 1.0 - double(largestFree()) / totalFree; assert(fragmentation > 0.97);
        int w = 0; std::vector<bool> compacted(N, false); for (int i = 0; i < N; i++) if (used[i]) compacted[(size_t)w++] = true; used = compacted; assert(largestFree() == 3200); }
    // ① 내부 단편화
    {   double wasteSum[3] = {0, 0, 0}, classSum[3] = {0, 0, 0}, worst[3] = {0, 0, 0}; const int M = 4096;
        for (int n = 1; n <= M; ++n) {
            int c0 = sizeClass(n), c4 = fineClass(n, 4), c8 = fineClass(n, 8); int cs[3] = {c0, c4, c8};
            for (int j = 0; j < 3; ++j) { assert(cs[j] >= n); wasteSum[j] += cs[j] - n; classSum[j] += cs[j]; if (n > 16) worst[j] = std::max(worst[j], (double)(cs[j] - n) / cs[j]); }
        }
        // 2 의 거듭제곱 클래스의 총 낭비를 옥타브별 등차수열 합으로 따로 계산: 옥타브 (2^(j-1), 2^j] 의 낭비 합 = 2^(j-1)(2^(j-1) - 1) / 2,  16 이하 구간은 클래스 16
        double closed = 0; for (int n = 1; n <= 16; ++n) closed += 16 - n; for (int j = 5; (1 << j) <= M; ++j) { double h = 1 << (j - 1); closed += h * (h - 1) / 2; }
        assert(wasteSum[0] == closed);                                                                              // 계산식과 정확히 일치
        assert(worst[0] > 0.48 && worst[0] < 0.5 && worst[1] < 1.0 / 5 && worst[2] < 1.0 / 9);                      // 최악: 2 의 거듭제곱 ~50%, k = 4 는 20% 미만, k = 8 은 약 11% 미만
        assert(wasteSum[1] < wasteSum[0] / 2 && wasteSum[2] < wasteSum[1] * 0.6);                                   // 세분화할수록 평균 낭비도 크게 준다
        const int P = 4096; double pageWaste = 0; for (int n = 1; n <= 10 * P; ++n) pageWaste += (n + P - 1) / P * P - n; assert(pageWaste / (10 * P) == (P - 1) / 2.0);       // 페이지 올림: 평균 정확히 (P - 1) / 2
        std::cout << "Internal fragmentation (sizes 1..4096): power-of-two classes waste " << 100 * wasteSum[0] / classSum[0] << "% of the memory handed out, 4 sub-classes " << 100 * wasteSum[1] / classSum[1] << "%, 8 sub-classes " << 100 * wasteSum[2] / classSum[2] << "%; page rounding wastes " << pageWaste / (10 * P) << " bytes on average." << std::endl; }
    // ② 외부 단편화와 50% 규칙
    {   Heap h(4096); std::mt19937 rng(14); std::vector<int> offs; double holeRatioSum = 0; long samples = 0, failedWithSpace = 0, requests = 0;
        for (int step = 0; step < 200000; ++step) {
            bool doAlloc = offs.empty() || (h.freeTotal() > 4096 / 10 ? rng() % 2 == 0 : rng() % 100 < 40);                // 사용률이 약 90% 가 되도록 균형을 잡는다
            if (doAlloc) { int n = 1 + (int)(rng() % 64); ++requests; int off = h.alloc(n); if (off >= 0) offs.push_back(off); else if (h.freeTotal() >= n) ++failedWithSpace; }
            else { size_t i = rng() % offs.size(); h.release(offs[i]); offs[i] = offs.back(); offs.pop_back(); }
            if (step > 50000 && step % 100 == 0 && !offs.empty()) { holeRatioSum += (double)h.holes.size() / (double)offs.size(); ++samples; }
            if (step % 5000 == 0) { int sum = h.freeTotal(); for (auto& kv : h.live) sum += kv.second; assert(sum == 4096); for (size_t i = 0; i + 1 < h.holes.size(); ++i) assert(h.holes[i].off + h.holes[i].size < h.holes[i + 1].off); }   // 병합이 끝나 있고 합이 맞다
        }
        double ratio = holeRatioSum / (double)samples; assert(ratio > 0.3 && ratio < 0.7 && failedWithSpace > 50);                                       // 구멍 수 ≈ 할당 블록 수의 절반
        double before = h.index(); int freeBefore = h.freeTotal(); long moved = h.compact();
        assert(before > 0.5 && h.index() == 0.0 && h.freeTotal() == freeBefore && h.holes.size() == 1 && moved > 0 && moved <= (long)h.live.size());     // ③ 압축 후 지수 0, 옮긴 블록은 첫 구멍 뒤의 블록들
        std::cout << "External fragmentation: steady-state holes/allocated = " << ratio << " (Knuth's 50% rule), " << failedWithSpace << " of " << requests << " requests failed although enough total space was free; compaction moved " << moved << " blocks." << std::endl; }
    // ④ 같은 크기 블록만: 외부 단편화 없음
    {   const int SLOTS = 100; std::vector<char> used(SLOTS, 0); std::mt19937 rng(2); long failures = 0, allocs = 0;
        for (int step = 0; step < 100000; ++step) {
            int usedCount = 0; for (char c : used) usedCount += c;
            if (rng() % 2) { int slot = -1; for (int i = 0; i < SLOTS; ++i) if (!used[(size_t)i]) { slot = i; break; } if (slot < 0) { ++failures; assert(usedCount == SLOTS); } else { used[(size_t)slot] = 1; ++allocs; } }       // 실패는 정말 가득 찼을 때만
            else { int i = (int)(rng() % SLOTS); used[(size_t)i] = 0; }
        }
        assert(allocs > 10000); }
    return 0;
}
// Time Complexity: 압축 O(N), 할당 O(구멍 수)
// Space Complexity: O(N)
```
## False Sharing이란?
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <thread>
#include <vector>

// 서로 다른 코어가 서로 다른 변수를 쓰는데도, 두 변수가 같은 캐시 라인(64B)에 있으면 한 코어가 쓸 때마다 다른 코어의 라인 사본이 무효화되어 라인이 코어 사이를 오간다.  데이터는 공유하지 않는데 캐시 일관성 프로토콜(MESI) 때문에 느려지므로 "거짓" 공유라 부른다.
// 이 항목은 그것을 *찾아내는 분석기*(perf c2c 와 같은 발상)를 만든다: 스레드별 접근 기록(스레드, 주소, 크기, 쓰기 여부)을 라인 단위로 모아 PRIVATE(한 스레드만) / READ_SHARED(쓰기 없음) / TRUE_SHARED(서로 다른 스레드가 *같은 바이트* 를 건드리고 쓰기가 있음) / FALSE_SHARED(여럿이 건드리고 쓰기가 있지만 바이트는 겹치지 않음)로 분류한다.
//  ① 같은 기록을 구간 겹침 판정 구현 A 와 바이트별 비트마스크 구현 B 로 분류해 대조: 무작위 3 000 세트(스레드 ≤ 6, 라인 4 개, 라인 경계를 가로지르는 접근 포함)에서 모든 라인의 분류가 일치  ② 손으로 만든 사례: 공유 카운터 하나(TRUE) / 슬롯 배열 보폭 8·16·32·64·128 / 읽기 전용 설정 옆의 핫 카운터(FALSE) / 카운터를 다른 라인으로 옮김 / 8바이트 슬롯이 라인 경계에 걸침
//  ③ 8 스레드 슬롯 배열에서 FALSE_SHARED 라인 수는 보폭이 64 의 약수일 때 ⌊T/k⌋ + (T mod k ≥ 2 ? 1 : 0) (k = 64/보폭) 이고 64 이상이면 0; 패딩의 메모리 비용은 T·(올림(보폭) − 보폭)  ④ 실제 객체: alignas(64) 배열 속 원자 카운터 8 개(8바이트 보폭) 와 alignas(64) 슬롯 8 개의 *실제 주소* 를 분석기에 넣어 판정하고, 실제 스레드로 증가시켜 두 배치 모두 합계가 정확함을 확인(속도 차이는 단언하지 않는다)
const uintptr_t LINE = 64;
struct Event { int thread; uintptr_t addr; int size; bool write; };
enum Class { PRIVATE, READ_SHARED, TRUE_SHARED, FALSE_SHARED };
struct Piece { int thread; int lo, hi; bool write; };                                                                                                                    // 한 라인 안의 [lo, hi) 바이트 구간
std::map<uintptr_t, std::vector<Piece>> byLine(const std::vector<Event>& ev) { std::map<uintptr_t, std::vector<Piece>> lines;
    for (auto& e : ev) { uintptr_t a = e.addr, end = e.addr + e.size; while (a < end) { uintptr_t line = a / LINE, stop = std::min<uintptr_t>(end, (line + 1) * LINE); lines[line].push_back({e.thread, (int)(a - line * LINE), (int)(stop - line * LINE), e.write}); a = stop; } } return lines; }   // 경계를 넘는 접근은 쪼갠다
Class classifyA(const std::vector<Piece>& ps) { std::set<int> threads; bool anyWrite = false; for (auto& p : ps) { threads.insert(p.thread); anyWrite |= p.write; } if (threads.size() < 2) return PRIVATE; if (!anyWrite) return READ_SHARED;
    for (size_t i = 0; i < ps.size(); ++i) for (size_t j = i + 1; j < ps.size(); ++j) if (ps[i].thread != ps[j].thread && (ps[i].write || ps[j].write) && ps[i].lo < ps[j].hi && ps[j].lo < ps[i].hi) return TRUE_SHARED; return FALSE_SHARED; }          // 구현 A: 다른 스레드의 구간이 겹치고 한쪽이 쓰기
Class classifyB(const std::vector<Piece>& ps) { uint32_t touchers[LINE] = {0}, writers[LINE] = {0}, all = 0; bool anyWrite = false; for (auto& p : ps) { for (int b = p.lo; b < p.hi; ++b) { touchers[b] |= 1u << p.thread; if (p.write) writers[b] |= 1u << p.thread; } all |= 1u << p.thread; anyWrite |= p.write; }
    if (__builtin_popcount(all) < 2) return PRIVATE; if (!anyWrite) return READ_SHARED; for (uintptr_t b = 0; b < LINE; ++b) if (writers[b] != 0 && __builtin_popcount(touchers[b]) >= 2) return TRUE_SHARED; return FALSE_SHARED; }   // 구현 B: 바이트마다 건드린 스레드 집합
std::map<uintptr_t, Class> classify(const std::vector<Event>& ev, bool useA = true) { std::map<uintptr_t, Class> out; for (auto& kv : byLine(ev)) out[kv.first] = useA ? classifyA(kv.second) : classifyB(kv.second); return out; }
int countClass(const std::map<uintptr_t, Class>& m, Class c) { int n = 0; for (auto& kv : m) n += kv.second == c; return n; }
std::vector<Event> slotArray(uintptr_t base, int threads, int stride) { std::vector<Event> ev; for (int t = 0; t < threads; ++t) ev.push_back({t, base + (uintptr_t)t * stride, 8, true}); return ev; }
struct PackedCounters { alignas(64) std::atomic<long> c[8]; };
struct alignas(64) PaddedSlot { std::atomic<long> v; };
struct PaddedCounters { PaddedSlot s[8]; };
static_assert(sizeof(PackedCounters) == 64 && sizeof(PaddedCounters) == 512 && alignof(PaddedSlot) == 64, "패딩은 슬롯 크기를 64B 로 만든다");

int main() {
    std::mt19937 rng(64);
    for (int trial = 0; trial < 3000; ++trial) { std::vector<Event> ev; int n = 1 + (int)(rng() % 30); for (int i = 0; i < n; ++i) ev.push_back({(int)(rng() % 6), 4096 + rng() % (4 * LINE - 16), 1 + (int)(rng() % 16), rng() % 2 == 0});                          // ① 두 구현 대조
        auto a = classify(ev, true), b = classify(ev, false); assert(a == b); }
    {   const uintptr_t base = 8192; std::vector<Event> counter; for (int t = 0; t < 4; ++t) counter.push_back({t, base, 8, true}); auto m = classify(counter); assert(m.size() == 1 && m[base / LINE] == TRUE_SHARED);                         // ② 공유 카운터 하나
        for (int stride : {8, 16, 24, 32, 48, 64, 72, 128}) { auto ev = slotArray(base, 8, stride); auto cls = classify(ev); int falseLines = countClass(cls, FALSE_SHARED);
            int expect = 0; if (stride >= 64) { expect = 0; } else if (64 % stride == 0) { int k = 64 / stride; expect = 8 / k + (8 % k >= 2 ? 1 : 0); } else { std::map<uintptr_t, int> sharers; for (int t = 0; t < 8; ++t) { uintptr_t lo = base + (uintptr_t)t * stride, hi = lo + 8; for (uintptr_t l = lo / LINE; l <= (hi - 1) / LINE; ++l) ++sharers[l]; } for (auto& kv : sharers) expect += kv.second >= 2; }   // 약수가 아니면 라인별로 직접 센다
            assert(falseLines == expect); assert(countClass(cls, TRUE_SHARED) == 0); if (stride >= 64 && stride % 64 == 0) assert(falseLines == 0 && countClass(cls, PRIVATE) == 8);
            if (stride < 64) { size_t padded = (stride + 63) / 64 * 64; auto fixedLayout = slotArray(base, 8, (int)padded); assert(countClass(classify(fixedLayout), FALSE_SHARED) == 0); assert(8 * ((int)padded - stride) == 8 * (64 - stride) || stride % 64 != 0); } }              // ③ 패딩이 고친다
        std::vector<Event> cfg; for (int t = 0; t < 4; ++t) cfg.push_back({t, base + 0, 8, false}); cfg.push_back({0, base + 8, 8, true}); assert(classify(cfg)[base / LINE] == FALSE_SHARED);                         // 읽기 전용 설정 옆의 카운터: 바이트는 안 겹치지만 거짓 공유
        std::vector<Event> moved; for (int t = 0; t < 4; ++t) moved.push_back({t, base + 0, 8, false}); moved.push_back({0, base + 64, 8, true}); auto mm = classify(moved); assert(mm[base / LINE] == READ_SHARED && mm[base / LINE + 1] == PRIVATE);  // 카운터를 옮기면 읽기 공유 + 비공유
        std::vector<Event> cross = {{0, base + 60, 8, true}, {1, base + 68, 8, true}}; auto cc = classify(cross); assert(cc[base / LINE] == PRIVATE && cc[base / LINE + 1] == FALSE_SHARED); }                          // 라인 경계에 걸친 슬롯
    {   PackedCounters packed; PaddedCounters padded; for (auto& c : packed.c) c.store(0); for (auto& s : padded.s) s.v.store(0);                                                                        // ④ 실제 객체
        std::vector<Event> evPacked, evPadded; for (int t = 0; t < 8; ++t) { evPacked.push_back({t, (uintptr_t)&packed.c[t], 8, true}); evPadded.push_back({t, (uintptr_t)&padded.s[t].v, 8, true}); }
        auto cp = classify(evPacked), cq = classify(evPadded); assert(cp.size() == 1 && countClass(cp, FALSE_SHARED) == 1 && cq.size() == 8 && countClass(cq, PRIVATE) == 8);
        const long ITER = 50000; std::vector<std::thread> pool; for (int t = 0; t < 8; ++t) pool.emplace_back([&, t] { for (long i = 0; i < ITER; ++i) { packed.c[t].fetch_add(1, std::memory_order_relaxed); padded.s[t].v.fetch_add(1, std::memory_order_relaxed); } }); for (auto& th : pool) th.join();
        for (int t = 0; t < 8; ++t) assert(packed.c[t].load() == ITER && padded.s[t].v.load() == ITER); }
    std::cout << "False sharing: the interval and byte-mask classifiers agreed on every line of 3000 random access sets; 8 slots at stride 8 shared 1 line, stride 16 shared 2 lines, stride 32 shared 4, stride >= 64 shared none; padding removed every false-shared line at the predicted memory cost; real packed counters were flagged and padded ones were not, with exact totals from 8 threads" << std::endl;
    return 0;
}
// Time Complexity: 분석 O(이벤트 수 × 라인당 조각 수)
// Space Complexity: 패딩만큼 증가
```
## NUMA 구조 이해하기
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <queue>
#include <sstream>
#include <string>
#include <vector>
#if defined(__linux__)
#include <dirent.h>
#endif

// NUMA 서버의 노드 간 상대 거리(numactl --hardware 의 distance 표): 자기 노드 10, 한 홉 이웃 21, 두 홉 31 처럼 거리가 *홉 수* 로 정해진다 (이 책의 모형: 로컬 10, 원격은 11 + 10 × 홉 — 실제 SLIT 표는 펌웨어가 정하는 상대값이며 제조사마다 다르다).  소켓을 잇는 링크 그래프에서 BFS 로 홉 수를 구하면 거리 표가 나온다.
//  ① 4 소켓 링크(0-1-3-2-0) 의 BFS 거리표가 옛 책의 표 {10,21,21,31 ...} 와 일치  ② 링(n=2..10)·완전 연결(n=2..8)·초입방체(차원 1..4)·일렬(n=2..8)의 거리표가 대칭, 대각 10, 홉 삼각부등식 성립(전수)
//  ③ 평균 홉 수의 닫힌 식: 링 Σ min(k,n−k)/(n−1), 초입방체 k·2^(k−1)/(2^k−1) 이 BFS 결과와 같고 지름은 링 ⌊n/2⌋·초입방체 k  ④ 할당 대체 순서(zonelist): 거리 오름차순·자기 노드가 맨 앞, 용량이 모자라면 가까운 노드부터 채움 — 스레드 하나일 때는 최적(분배 전수 대조)
//  ⑤ 스레드가 *경쟁* 하면 먼저 온 순서대로 가까운 곳을 채우는 욕심쟁이는 최적이 아니다: 작은 경우 전수로 최적과 비교해 욕심쟁이가 *항상 ≥ 최적* 이며 *더 나쁜 사례가 존재*  ⑥ (Linux) 이 기계의 /sys 노드 수·거리표가 같은 성질(대각 10 이 행의 최솟값, 대칭)을 만족
typedef std::vector<std::vector<int>> Matrix;
typedef std::vector<std::pair<int, int>> Links;
Matrix hopTable(int n, const Links& links) { std::vector<std::vector<int>> adj(n); for (auto& e : links) { adj[e.first].push_back(e.second); adj[e.second].push_back(e.first); }
    Matrix hops(n, std::vector<int>(n, -1)); for (int s = 0; s < n; ++s) { std::queue<int> q; q.push(s); hops[s][s] = 0; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (hops[s][v] < 0) { hops[s][v] = hops[s][u] + 1; q.push(v); } } } return hops; }
Matrix distances(const Matrix& hops) { Matrix d = hops; for (auto& row : d) for (auto& x : row) x = x == 0 ? 10 : 11 + 10 * x; return d; }
double averageHops(const Matrix& hops) { double s = 0; int n = (int)hops.size(); for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (i != j) s += hops[i][j]; return s / ((double)n * (n - 1)); }
int diameter(const Matrix& hops) { int m = 0; for (auto& r : hops) for (int x : r) m = std::max(m, x); return m; }
void checkTable(const Matrix& hops) { int n = (int)hops.size(); for (int i = 0; i < n; ++i) { assert(hops[i][i] == 0); for (int j = 0; j < n; ++j) { assert(hops[i][j] >= 0 && hops[i][j] == hops[j][i]); for (int k = 0; k < n; ++k) assert(hops[i][k] <= hops[i][j] + hops[j][k]); } } }
std::vector<int> zonelist(const Matrix& d, int from) { std::vector<int> order(d.size()); for (size_t i = 0; i < d.size(); ++i) order[i] = (int)i; std::stable_sort(order.begin(), order.end(), [&](int a, int b) { return d[from][a] < d[from][b]; }); return order; }
long fillNearestFirst(const Matrix& d, int from, int need, std::vector<int>& cap) { long cost = 0; for (int m : zonelist(d, from)) { int take = std::min(need, cap[m]); cap[m] -= take; need -= take; cost += (long)take * d[from][m]; } assert(need == 0); return cost; }
void best2(const Matrix& d, int a, int na, int b, int nb, const std::vector<int>& cap, long& bestCost) {                                                                    // 두 스레드의 모든 분배를 전수
    int n = (int)d.size(); std::vector<int> x(n, 0), y(n, 0);
    for (int code = 0; code < 1 << 12; ++code) { int c = code; int sa = 0, sb = 0; bool ok = true; for (int m = 0; m < n; ++m) { x[m] = c % 5; c /= 5; sa += x[m]; if (x[m] > 4) ok = false; } if (sa != na) continue; (void)ok;
        for (int code2 = 0; code2 < 625; ++code2) { int c2 = code2; sb = 0; for (int m = 0; m < n; ++m) { y[m] = c2 % 5; c2 /= 5; sb += y[m]; } if (sb != nb) continue; bool fit = true; long cost = 0; for (int m = 0; m < n; ++m) { if (x[m] + y[m] > cap[m]) fit = false; cost += (long)x[m] * d[a][m] + (long)y[m] * d[b][m]; } if (fit && cost < bestCost) bestCost = cost; } } }

int main() {
    Links ring4 = {{0, 1}, {1, 3}, {3, 2}, {2, 0}}; Matrix expected = {{10, 21, 21, 31}, {21, 10, 31, 21}, {21, 31, 10, 21}, {31, 21, 21, 10}}; assert(distances(hopTable(4, ring4)) == expected);                // ①
    for (int n = 2; n <= 10; ++n) { Links ring; for (int i = 0; i < n; ++i) if (n > 2 || i == 0) ring.push_back({i, (i + 1) % n}); Matrix hops = hopTable(n, ring); checkTable(hops);                         // ②③ 링
        double closed = 0; for (int k = 1; k < n; ++k) closed += std::min(k, n - k); closed /= (n - 1); assert(std::abs(averageHops(hops) - closed) < 1e-12 && diameter(hops) == n / 2); }
    for (int n = 2; n <= 8; ++n) { Links mesh, line; for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) mesh.push_back({i, j}); for (int i = 0; i + 1 < n; ++i) line.push_back({i, i + 1}); Matrix m = hopTable(n, mesh), l = hopTable(n, line); checkTable(m); checkTable(l); assert(diameter(m) == 1 && averageHops(m) == 1.0 && diameter(l) == n - 1); }
    for (int k = 1; k <= 4; ++k) { int n = 1 << k; Links cube; for (int i = 0; i < n; ++i) for (int b = 0; b < k; ++b) if (i < (i ^ (1 << b))) cube.push_back({i, i ^ (1 << b)}); Matrix hops = hopTable(n, cube); checkTable(hops);
        for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) assert(hops[i][j] == __builtin_popcount(i ^ j));                                                          // 해밍 거리
        assert(std::abs(averageHops(hops) - (double)k * (1 << (k - 1)) / (n - 1)) < 1e-12 && diameter(hops) == k); }
    {   Matrix d = distances(hopTable(4, ring4)); for (int from = 0; from < 4; ++from) { auto z = zonelist(d, from); assert(z[0] == from); for (size_t i = 1; i < z.size(); ++i) assert(d[from][z[i - 1]] <= d[from][z[i]]); }       // ④ zonelist
        for (int need = 0; need <= 8; ++need) for (int c0 = 0; c0 <= 4; ++c0) for (int c1 = 0; c1 <= 3; ++c1) { std::vector<int> cap = {c0, c1, 2, 3}; if (c0 + c1 + 5 < need) continue; std::vector<int> cap2 = cap; long greedy = fillNearestFirst(d, 0, need, cap2);
            long best = -1; for (int a = 0; a <= need; ++a) for (int b = 0; a + b <= need; ++b) for (int c = 0; a + b + c <= need; ++c) { int e = need - a - b - c; if (a > cap[0] || b > cap[1] || c > cap[2] || e > cap[3]) continue; long cost = (long)a * d[0][0] + (long)b * d[0][1] + (long)c * d[0][2] + (long)e * d[0][3]; if (best < 0 || cost < best) best = cost; }
            assert(greedy == best); }                                                                                                                                         // 스레드 하나: 가까운 곳부터가 최적
        long worse = 0, total = 0; for (int na = 0; na <= 4; ++na) for (int nb = 0; nb <= 4; ++nb) for (int cap0 = 0; cap0 <= 4; ++cap0) for (int a = 0; a < 4; ++a) for (int b = 0; b < 4; ++b) { std::vector<int> cap = {cap0, 4, 4, 4}; if (cap0 + 12 < na + nb) continue; std::vector<int> g = cap; long greedy = fillNearestFirst(d, a, na, g) + fillNearestFirst(d, b, nb, g);
            long best = 1 << 30; best2(d, a, na, b, nb, cap, best); assert(greedy >= best); ++total; if (greedy > best) ++worse; }                                                      // ⑤ 경쟁: 욕심쟁이 ≥ 최적, 더 나쁜 사례 존재
        assert(worse > 0 && worse < total); std::cout << "NUMA structure: link-graph BFS reproduced the 4-socket distance table, ring/mesh/line/hypercube tables obeyed the metric axioms and closed-form averages; greedy first-come allocation was beaten by the optimum in " << worse << " of " << total << " competing-thread cases; "; }
    int nodes = 0;
#if defined(__linux__)
    if (DIR* dir = opendir("/sys/devices/system/node")) { while (dirent* e = readdir(dir)) { std::string name = e->d_name; if (name.rfind("node", 0) == 0 && name.size() > 4 && std::isdigit((unsigned char)name[4])) ++nodes; } closedir(dir); }   // ⑥ 이 기계
    std::vector<std::vector<int>> real; for (int i = 0; i < nodes; ++i) { std::ifstream f("/sys/devices/system/node/node" + std::to_string(i) + "/distance"); std::vector<int> row; int x; while (f >> x) row.push_back(x); if (!row.empty()) real.push_back(row); }
    if ((int)real.size() == nodes && nodes > 0) for (int i = 0; i < nodes; ++i) { assert((int)real[i].size() == nodes && real[i][i] == 10 && *std::min_element(real[i].begin(), real[i].end()) == 10); for (int j = 0; j < nodes; ++j) assert(real[i][j] == real[j][i]); }
#endif
    std::cout << "this machine reports " << nodes << " NUMA node(s)" << std::endl;
    return 0;
}
// Time Complexity: BFS O(n(n+간선)), 분배 전수 O(5^n)
// Space Complexity: O(n²)
```
## C, C++, Java, Python의 메모리 관리 비교
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 같은 객체 그래프를 네 가지 방식으로 정리하면 무엇이 회수되는가?  그래프: root -> a -> b,  c <-> d (서로만 가리키는 순환, root 에서 닿지 않음),  e (아무도 안 가리킴).  root 변수를 놓은 뒤:
//  C(수동)            : 프로그래머가 free 를 안 하면 전부 누수.
//  C++ RAII(shared_ptr): 참조 카운트 -> a, b, e 는 회수, 순환 c/d 는 누수.
//  Java(추적 GC)      : root 에서 닿지 않는 것을 전부 회수 (순환 포함).
//  Python             : 참조 카운트(즉시) + 순환 수집기(나중에) -> 즉시는 a, b, e / 순환 GC 실행 후 c, d 도.
// 이 예제는 네 가지를 실제로 구현해 임의의 그래프 400 개에서 대조한다:
//  Java: 루트에서 DFS 로 도달 가능한 집합을 구해 나머지를 회수  /  Python: 참조 카운트를 직접 세어 0 이 된 것을 연쇄 해제한 뒤, CPython 의 순환 수집 알고리즘(내부 참조를 빼서 "바깥에서 가리키는 수" 가 0 보다 큰 것에서 닿는 것만 살리는 시험 삭제)으로 남은 순환을 회수
//  C++: 진짜 std::shared_ptr 그래프를 만들어 루트를 놓고 남은 객체 수를 센다  /  C: 프로그래머가 일부를 해제하면 가리키는 쪽에 댕글링이 생기는 정도를 센다
// 검증: 회수된 집합 — Java == 도달 불가능 집합 U,  Python(순환 수집 뒤) == U,  Python(즉시 카운트만) == C++ 가 회수한 집합 F ⊆ U,  C++ 누수 개수(진짜 shared_ptr) == |U \ F|,  순환이 없는 그래프에서는 F == U.  또 약한 참조 하나로 순환을 끊으면 회수된다
struct Graph { int n; std::vector<std::vector<int>> out; std::vector<int> roots; };
std::set<int> reachableFrom(const Graph& g) { std::set<int> seen; std::vector<int> st(g.roots.begin(), g.roots.end()); while (!st.empty()) { int u = st.back(); st.pop_back(); if (!seen.insert(u).second) continue; for (int v : g.out[(size_t)u]) st.push_back(v); } return seen; }
std::set<int> javaFreed(const Graph& g) { auto live = reachableFrom(g); std::set<int> f; for (int i = 0; i < g.n; ++i) if (!live.count(i)) f.insert(i); return f; }
std::set<int> refcountFreed(const Graph& g) {                                      // 루트가 각각 참조 하나를 쥔 상태에서 카운트가 0 인 것을 연쇄 해제하되 루트는 해제하지 않는다
    std::vector<long> rc((size_t)g.n, 0); for (int u = 0; u < g.n; ++u) for (int v : g.out[(size_t)u]) ++rc[(size_t)v]; for (int r : g.roots) ++rc[(size_t)r];       // 루트 변수도 참조 하나
    std::set<int> freed; std::queue<int> q; std::set<int> rootSet(g.roots.begin(), g.roots.end());
    for (int i = 0; i < g.n; ++i) if (rc[(size_t)i] == 0) q.push(i);
    while (!q.empty()) { int u = q.front(); q.pop(); if (!freed.insert(u).second) continue; for (int v : g.out[(size_t)u]) if (--rc[(size_t)v] == 0) q.push(v); }
    return freed;
}
std::set<int> pythonCycleCollect(const Graph& g, std::set<int> freedByRc) {        // CPython: update_refs -> subtract_refs -> move_unreachable
    std::vector<long> rc((size_t)g.n, 0); for (int u = 0; u < g.n; ++u) if (!freedByRc.count(u)) for (int v : g.out[(size_t)u]) ++rc[(size_t)v]; for (int r : g.roots) ++rc[(size_t)r];
    std::vector<long> gcRefs = rc; for (int u = 0; u < g.n; ++u) if (!freedByRc.count(u)) for (int v : g.out[(size_t)u]) --gcRefs[(size_t)v];                  // 컨테이너 안의 참조를 뺀다
    std::set<int> reachable; std::vector<int> st; for (int u = 0; u < g.n; ++u) if (!freedByRc.count(u) && gcRefs[(size_t)u] > 0) st.push_back(u);            // 바깥(루트)에서 가리키는 것
    while (!st.empty()) { int u = st.back(); st.pop_back(); if (!reachable.insert(u).second) continue; for (int v : g.out[(size_t)u]) st.push_back(v); }
    std::set<int> freed = freedByRc; for (int u = 0; u < g.n; ++u) if (!freedByRc.count(u) && !reachable.count(u)) freed.insert(u); return freed;
}
struct Node { static int alive; std::vector<std::shared_ptr<Node>> out; Node() { ++alive; } ~Node() { --alive; } };
int Node::alive = 0;
int sharedPtrLeaks(const Graph& g) {                                                // 진짜 shared_ptr 그래프: 작업용 목록을 놓은 뒤 남은 객체 수 - 루트에서 닿는 수 = 순환에 매달린 누수
    Node::alive = 0; int leaks;
    {   std::vector<std::shared_ptr<Node>> nodes; for (int i = 0; i < g.n; ++i) nodes.push_back(std::make_shared<Node>());
        for (int u = 0; u < g.n; ++u) for (int v : g.out[(size_t)u]) nodes[(size_t)u]->out.push_back(nodes[(size_t)v]);
        std::vector<std::shared_ptr<Node>> rootHolders; for (int r : g.roots) rootHolders.push_back(nodes[(size_t)r]);
        std::vector<std::weak_ptr<Node>> all(nodes.begin(), nodes.end());
        nodes.clear();                                                               // 작업용 목록을 놓는다: 남는 참조는 그래프 안의 간선과 루트 변수뿐
        leaks = Node::alive - (int)reachableFrom(g).size();                          // 루트에서 닿는 것은 정상, 나머지 중 아직 살아 있는 것이 누수
        for (auto& w : all) if (auto p = w.lock()) p->out.clear();                   // (검증이 끝났으니 순환을 손으로 끊어 진짜 누수는 남기지 않는다)
        rootHolders.clear();
    }
    assert(Node::alive == 0); return leaks;
}
struct WeakNode { static int alive; std::shared_ptr<WeakNode> strong; std::weak_ptr<WeakNode> weak; WeakNode() { ++alive; } ~WeakNode() { --alive; } };
int WeakNode::alive = 0;
Graph randomGraph(std::mt19937& rng, bool acyclic) {
    Graph g; g.n = 3 + (int)(rng() % 12); g.out.assign((size_t)g.n, {});
    for (int u = 0; u < g.n; ++u) { int deg = (int)(rng() % 3); for (int k = 0; k < deg; ++k) { int v = (int)(rng() % (unsigned)g.n); if (acyclic && v <= u) continue; g.out[(size_t)u].push_back(v); } }
    int nr = (int)(rng() % 3); for (int i = 0; i < nr; ++i) g.roots.push_back((int)(rng() % (unsigned)g.n)); return g;
}

int main() {
    // 원래 예: 0=root 1=a 2=b 3=c 4=d 5=e,  root 변수를 놓은 뒤 (루트 집합이 비었다)
    {   Graph g; g.n = 6; g.out = {{1}, {2}, {}, {4}, {3}, {}}; g.roots = {};
        std::set<int> all = {0, 1, 2, 3, 4, 5}; auto rc = refcountFreed(g); assert((rc == std::set<int>{0, 1, 2, 5}));                           // 참조 카운트만: root, a, b, e 가 회수, 순환 c/d 만 남는다
        auto py = pythonCycleCollect(g, rc); assert(py == all && javaFreed(g) == all);                                                         // 순환 수집기를 돌리면 c/d 도, 추적 GC 는 전부
        assert(sharedPtrLeaks(g) == 2); }                                                                                                       // 진짜 shared_ptr: 2 개 누수
    std::mt19937 rng(2025); long graphs = 0, cyclicLeaks = 0, totalFreedRc = 0, totalU = 0, danglingTotal = 0, leaksManual = 0;
    for (int it = 0; it < 400; ++it) {
        Graph g = randomGraph(rng, it % 4 == 0); auto U = javaFreed(g); auto F = refcountFreed(g); auto P = pythonCycleCollect(g, F);
        assert(U == P);                                                                                                // Java == Python(순환 수집 뒤) == 도달 불가능 집합
        for (int f : F) assert(U.count(f));                                                                            // 카운트가 회수한 것은 모두 진짜 쓰레기 (살아 있는 것을 지우지 않는다)
        int leak = sharedPtrLeaks(g); assert(leak == (int)(U.size() - F.size()));                                      // C++ 누수 개수 == |U \ F|
        if (it % 4 == 0) assert(F == U);                                                                               // 순환이 없는 그래프에서는 참조 카운트로 충분
        cyclicLeaks += leak; totalFreedRc += (long)F.size(); totalU += (long)U.size();
        // C: 프로그래머가 도달 불가능한 것 중 70% 만 해제한다고 하고, 살아 있는 것 중 일부(10%)를 실수로 해제한다
        std::set<int> freedByHand; for (int u : U) if (rng() % 10 < 7) freedByHand.insert(u); auto live = reachableFrom(g); for (int u : live) if (rng() % 10 == 0) freedByHand.insert(u);
        long dangling = 0; for (int u = 0; u < g.n; ++u) if (!freedByHand.count(u)) for (int v : g.out[(size_t)u]) dangling += freedByHand.count(v) > 0;       // 해제되지 않은 객체가 해제된 객체를 가리킨다
        for (int u : U) if (!freedByHand.count(u)) ++leaksManual; danglingTotal += dangling; ++graphs;
    }
    assert(cyclicLeaks > 100 && totalFreedRc < totalU && danglingTotal > 100 && leaksManual > 100);
    // 약한 참조 하나로 순환 끊기
    {   WeakNode::alive = 0;
        { auto a = std::make_shared<WeakNode>(); auto b = std::make_shared<WeakNode>(); a->strong = b; b->weak = a; } assert(WeakNode::alive == 0);                    // a -> b 강한, b -> a 약한: 순환이 아니므로 회수
        { auto a = std::make_shared<WeakNode>(); auto b = std::make_shared<WeakNode>(); a->strong = b; b->strong = a; assert(WeakNode::alive == 2); a->strong.reset(); } assert(WeakNode::alive == 0); }       // 둘 다 강한 참조면 새고(손으로 끊어야 한다)
    std::cout << "Memory management comparison over " << graphs << " random graphs: tracing GC and Python (refcount + cycle collector) freed exactly the unreachable set (" << totalU << " objects); plain reference counting (C++ shared_ptr) freed "
              << totalFreedRc << " and leaked " << cyclicLeaks << " in cycles; hand-managed C left " << leaksManual << " leaks and " << danglingTotal << " dangling references." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## JVM 메모리 구조
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// JVM 런타임 영역: 힙(Young: Eden + Survivor S0/S1, Old), 메타스페이스(클래스 메타데이터), 스레드별 스택(프레임), PC 레지스터, 네이티브 스택.
// 객체는 Eden 에서 태어나고, minor GC 때 살아있으면 Survivor 로 복사되며 나이(age)가 1 증가한다.  나이가 임계값(tenuring threshold, 기본 최대 15)에 이르면 Old 로 승급한다.
// 기본 비율 Eden : S0 : S1 = 8 : 1 : 1.  아래는 임계값 3 인 단순 모델
enum Space { EDEN, SURVIVOR, OLD, DEAD };
struct Obj { std::string name; Space where = EDEN; int age = 0; bool referenced = true; };
const int THRESHOLD = 3;

void minorGC(std::vector<Obj>& heap) {
    for (auto& o : heap) {
        if (o.where == DEAD || o.where == OLD) continue;               // minor GC 는 Young 영역만 처리
        if (!o.referenced) { o.where = DEAD; continue; }                // 쓰레기는 회수
        o.age++;
        o.where = (o.age >= THRESHOLD) ? OLD : SURVIVOR;                // 승급 조건
    }
}

int main() {
    std::vector<Obj> heap = {{"session"}, {"temp1"}, {"temp2"}, {"cache"}};
    heap[1].referenced = false; heap[2].referenced = false;             // 임시 객체는 금방 죽는다 (약한 세대 가설)
    minorGC(heap);
    assert(heap[1].where == DEAD && heap[2].where == DEAD);             // 대부분의 객체는 첫 minor GC 에서 사라진다
    assert(heap[0].where == SURVIVOR && heap[0].age == 1);
    minorGC(heap); assert(heap[0].where == SURVIVOR && heap[0].age == 2);
    minorGC(heap); assert(heap[0].where == OLD && heap[3].where == OLD);   // 세 번 살아남으면 Old 로 승급
    heap.push_back({"new"}); minorGC(heap);
    assert(heap.back().where == SURVIVOR && heap[0].where == OLD);        // Old 는 minor GC 에서 건드리지 않는다
    std::cout << "JVM generational model: long-lived objects tenured to Old after " << THRESHOLD << " survivals." << std::endl;
    return 0;
}
// Time Complexity: minor GC 는 Young 크기에 비례
// Space Complexity: O(힙)
```
## CPython 객체 모델
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// CPython 의 모든 값은 PyObject 이고, 머리말은 (참조 횟수 ob_refcnt, 타입 포인터 ob_type) = 64비트에서 16바이트.  그래서 파이썬 int 하나가 최소 28~32바이트다.
// -5..256 의 작은 정수는 미리 만들어 둔 객체를 공유하므로 `a is b` 가 True.   list 는 append 가 O(1) 분할상환이 되도록 필요한 것보다 더 크게 용량을 잡는다 (over-allocation):
//   new_allocated = (newsize + (newsize >> 3) + 6) & ~3     -> 용량 변화 0, 4, 8, 16, 24, 32, 40, 52, 64, 76 ...
// 이 구현은 작은 파이썬 런타임을 만든다: 정수/리스트 객체, 이름 표(변수), 참조 횟수 규칙(이름에 묶거나 리스트에 넣으면 +1, 이름을 지우거나 리스트에서 빼면 -1, 0 이 되면 즉시 해제하며 담고 있던 것들의 횟수도 -1),
//  작은 정수 캐시, list 의 over-allocation(CPython 의 list_resize 와 같은 식), 크기 계산(sys.getsizeof), 그리고 순환 수집기(CPython 방식: 컨테이너마다 "바깥에서 가리키는 수 = 참조 횟수 - 컨테이너 안의 참조" 를 구해 0 보다 큰 것에서 닿는 것만 살리고 나머지를 비운다)
// 검증: ① 알려진 값: 용량 변화 4 8 16 24 32 40 52 64 76,  getsizeof([]) = 56, 1 개 = 88, 5 개 = 120, 9 개 = 184,  int: 1 -> 28, 2^30 -> 32, 2^60 -> 36  ② `is`: 100 은 같은 객체, 256 까지만 캐시(257 은 다른 객체)
//        ③ 무작위 프로그램 30 000 번(정수 만들기·리스트 만들기·append(자기 자신·서로 포함하는 순환 포함)·이름 지우기·pop·GC): 매 연산 뒤 "모든 살아 있는 객체의 참조 횟수 == 이름에서 오는 수 + 리스트 칸에서 오는 수 (+ 캐시 1)" 를 독립적으로 세어 대조,
//        순환은 GC 전에는 남고(누수), GC 뒤에는 이름에서 닿는 객체만 살아 있음  ④ 순환 수집기가 해제한 객체 수 == 도달 불가능한 컨테이너와 그것만 가리키던 정수
struct PyObjectHead { long ob_refcnt; void* ob_type; };
size_t growListAllocation(size_t allocated, size_t newsize) {                       // CPython list_resize: 늘릴 때 / 절반 아래로 줄어들 때만 재할당
    if (allocated >= newsize && newsize >= (allocated >> 1)) return allocated;
    size_t n = (newsize + (newsize >> 3) + 6) & ~(size_t)3; if (newsize == 0) n = 0; return n;
}
enum Kind { INT, LIST };
struct Obj { Kind kind = INT; long value = 0; std::vector<int> items; size_t allocated = 0; long refcnt = 0; bool alive = false; };

class Interp {
public:
    std::vector<Obj> heap; std::map<std::string, int> names; std::map<long, int> smallInts; long freed = 0;
    int alloc(Kind k) { heap.emplace_back(); Obj& o = heap.back(); o.kind = k; o.alive = true; o.refcnt = 1; return (int)heap.size() - 1; }          // 새 참조 하나를 가진 새 객체
    int newInt(long v) {                                                              // "새 참조" 를 돌려준다
        if (v >= -5 && v <= 256) { auto it = smallInts.find(v); if (it != smallInts.end()) { ++heap[(size_t)it->second].refcnt; return it->second; } int h = alloc(INT); heap[(size_t)h].value = v; smallInts[v] = h; ++heap[(size_t)h].refcnt; return h; }   // 캐시가 참조 하나를 영구히 쥔다
        int h = alloc(INT); heap[(size_t)h].value = v; return h;
    }
    int newList() { return alloc(LIST); }
    void incref(int h) { ++heap[(size_t)h].refcnt; }
    void decref(int h) { Obj& o = heap[(size_t)h]; assert(o.alive && o.refcnt > 0); if (--o.refcnt == 0) { o.alive = false; ++freed; std::vector<int> kids; kids.swap(o.items); o.allocated = 0; for (int c : kids) decref(c); } }
    void store(const std::string& name, int h) { incref(h); auto it = names.find(name); int old = it == names.end() ? -1 : it->second; names[name] = h; if (old >= 0) decref(old); }
    void bind(const std::string& name, int tempRef) { store(name, tempRef); decref(tempRef); }                    // 임시 참조를 이름에 묶고 임시를 놓는다
    void del(const std::string& name) { auto it = names.find(name); if (it == names.end()) return; int h = it->second; names.erase(it); decref(h); }
    void append(int list, int item) { Obj& l = heap[(size_t)list]; incref(item); l.items.push_back(item); l.allocated = growListAllocation(l.allocated, l.items.size()); }
    void pop(int list) { Obj& l = heap[(size_t)list]; if (l.items.empty()) return; int item = l.items.back(); l.items.pop_back(); l.allocated = growListAllocation(l.allocated, l.items.size()); decref(item); }
    size_t sizeOf(int h) const {                                                      // sys.getsizeof
        const Obj& o = heap[(size_t)h]; if (o.kind == LIST) return 56 + 8 * o.allocated;
        unsigned long long a = (unsigned long long)(o.value < 0 ? -o.value : o.value); size_t digits = 0; while (a) { ++digits; a >>= 30; } return 24 + 4 * digits;
    }
    long collect() {                                                                  // 순환 수집: 시험 삭제
        long before = freed; std::vector<int> conts; for (size_t i = 0; i < heap.size(); ++i) if (heap[i].alive && heap[i].kind == LIST) conts.push_back((int)i);
        std::map<int, long> gcRefs; for (int c : conts) gcRefs[c] = heap[(size_t)c].refcnt;
        for (int c : conts) for (int it : heap[(size_t)c].items) if (heap[(size_t)it].kind == LIST) --gcRefs[it];            // 컨테이너 안에서 오는 참조를 뺀다
        std::set<int> reachable; std::vector<int> st; for (int c : conts) if (gcRefs[c] > 0) st.push_back(c);                  // 바깥(이름·캐시)에서 가리키는 것
        while (!st.empty()) { int c = st.back(); st.pop_back(); if (!reachable.insert(c).second) continue; for (int it : heap[(size_t)c].items) if (heap[(size_t)it].kind == LIST) st.push_back(it); }
        for (int c : conts) if (!reachable.count(c) && heap[(size_t)c].alive) { std::vector<int> kids; kids.swap(heap[(size_t)c].items); heap[(size_t)c].allocated = 0; for (int k : kids) decref(k); }         // 도달 불가능한 컨테이너를 비운다 (tp_clear)
        return freed - before;
    }
    void check() const {                                                              // 불변식: 참조 횟수 == 이름에서 오는 수 + 리스트 칸에서 오는 수 + 작은 정수 캐시
        std::vector<long> incoming(heap.size(), 0);
        for (auto& kv : names) { assert(heap[(size_t)kv.second].alive); ++incoming[(size_t)kv.second]; }
        for (size_t i = 0; i < heap.size(); ++i) if (heap[i].alive) for (int it : heap[i].items) { assert(heap[(size_t)it].alive); ++incoming[(size_t)it]; }
        for (auto& kv : smallInts) ++incoming[(size_t)kv.second];
        for (size_t i = 0; i < heap.size(); ++i) { if (heap[i].alive) assert(heap[i].refcnt == incoming[i] && heap[i].refcnt > 0); else assert(heap[i].items.empty()); }
    }
    std::set<int> reachableFromNames() const { std::set<int> seen; std::vector<int> st; for (auto& kv : names) st.push_back(kv.second); for (auto& kv : smallInts) st.push_back(kv.second); while (!st.empty()) { int h = st.back(); st.pop_back(); if (!seen.insert(h).second) continue; for (int it : heap[(size_t)h].items) st.push_back(it); } return seen; }
    std::set<int> aliveSet() const { std::set<int> s; for (size_t i = 0; i < heap.size(); ++i) if (heap[i].alive) s.insert((int)i); return s; }
};

int main() {
    assert(sizeof(PyObjectHead) == 16);
    // ① 알려진 값
    {   std::vector<size_t> caps; size_t allocated = 0;
        for (size_t n = 1; n <= 76; n++) { size_t next = growListAllocation(allocated, n); if (next != allocated) { allocated = next; caps.push_back(allocated); } }
        assert((caps == std::vector<size_t>{4, 8, 16, 24, 32, 40, 52, 64, 76}));                                          // 실제 CPython 의 list 용량 변화와 같다 (76번 append 에 재할당은 9번뿐: 분할상환 O(1))
        Interp py; int l = py.newList(); assert(py.sizeOf(l) == 56);
        std::vector<std::pair<int, size_t>> expectSize = {{1, 88}, {5, 120}, {9, 184}, {17, 248}}; int appended = 0;
        for (auto& e : expectSize) { while (appended < e.first) { py.append(l, py.newInt(0)); py.decref(py.heap[(size_t)l].items.back()); ++appended; } assert(py.sizeOf(l) == e.second); }               // [] = 56, 1 개 88, 5 개 120, 9 개 184, 17 개 248
        assert(py.sizeOf(py.newInt(1)) == 28 && py.sizeOf(py.newInt((1L << 30) - 1)) == 28 && py.sizeOf(py.newInt(1L << 30)) == 32 && py.sizeOf(py.newInt(1L << 60)) == 36 && py.sizeOf(py.newInt(-(1L << 30))) == 32);      // 30 비트 자릿수마다 4 바이트
        // 줄어들 때: 길이가 용량의 절반 아래로 내려가면 재할당
        Interp q; int m = q.newList(); for (int i = 0; i < 40; ++i) { int t = q.newInt(i + 1000); q.append(m, t); q.decref(t); } size_t cap40 = q.heap[(size_t)m].allocated; for (int i = 0; i < 30; ++i) q.pop(m);
        assert(cap40 == 40 && q.heap[(size_t)m].items.size() == 10 && q.heap[(size_t)m].allocated < cap40 && q.heap[(size_t)m].allocated >= 10); }
    // ② `is` 와 작은 정수 캐시
    {   Interp py; int a = py.newInt(100), b = py.newInt(100), c = py.newInt(256), d = py.newInt(256), e = py.newInt(257), f = py.newInt(257), g = py.newInt(-5), h = py.newInt(-5), i = py.newInt(-6), j = py.newInt(-6);
        assert(a == b && c == d && g == h);                                         // 캐시 안: 같은 객체
        assert(e != f && i != j);                                                   // 캐시 밖: 서로 다른 객체 (`257 is 257` 는 False)
        long rc = py.heap[(size_t)a].refcnt; assert(rc == 3);                       // 캐시 1 + 임시 참조 2
        py.decref(a); py.decref(b); assert(py.heap[(size_t)a].refcnt == 1 && py.heap[(size_t)a].alive); }
    // ③④ 무작위 프로그램
    std::mt19937 rng(5); long ops = 0, gcFreed = 0, cyclesCreated = 0, leakedBeforeGc = 0; Interp py; const char* nm[] = {"a", "b", "c", "d", "e", "f"};
    for (int step = 0; step < 30000; ++step) {
        int op = (int)(rng() % 100); std::string n1 = nm[rng() % 6], n2 = nm[rng() % 6]; ++ops;
        auto has = [&](const std::string& n) { return py.names.count(n) > 0; };
        if (op < 22) py.bind(n1, py.newInt((long)(rng() % 600) - 20));
        else if (op < 36) py.bind(n1, py.newList());
        else if (op < 62) { if (has(n1) && py.heap[(size_t)py.names[n1]].kind == LIST) { int item; if (rng() % 3 == 0 && has(n2)) { item = py.names[n2]; if (item == py.names[n1] || py.heap[(size_t)item].kind == LIST) ++cyclesCreated; py.append(py.names[n1], item); } else { int t = py.newInt((long)(rng() % 600)); py.append(py.names[n1], t); py.decref(t); } } }
        else if (op < 78) py.del(n1);
        else if (op < 90) { if (has(n1) && py.heap[(size_t)py.names[n1]].kind == LIST) py.pop(py.names[n1]); }
        else if (op < 95) { auto reach = py.reachableFromNames(); auto alive = py.aliveSet(); leakedBeforeGc += (long)(alive.size() - reach.size()); gcFreed += py.collect(); assert(py.aliveSet() == py.reachableFromNames()); }       // GC 뒤에는 이름에서 닿는 객체만
        py.check();                                                                                      // 매 연산 뒤 참조 횟수 불변식
    }
    assert(cyclesCreated > 200 && gcFreed > 100 && leakedBeforeGc > 100);                               // 컨테이너가 서로를 담는 일이 실제로 생겼고 GC 가 회수했다
    // 순환의 누수와 회수 (결정적 예)
    {   Interp q; int l = q.newList(); q.bind("x", l); int again = q.names["x"]; q.append(again, again);          // 자기 자신을 담는 리스트
        assert(q.heap[(size_t)again].refcnt == 2); q.del("x"); assert(q.heap[(size_t)again].alive && q.heap[(size_t)again].refcnt == 1);            // 이름을 지워도 자기 참조 때문에 살아 있다 (누수)
        assert(q.collect() == 1 && !q.heap[(size_t)again].alive); }                                                                                    // 순환 수집기가 회수
    std::cout << "CPython object model: refcount == incoming references after each of " << ops << " random operations; list capacities 4 8 16 24 32 40 52 64 76, getsizeof 56/88/120/184; the cycle collector freed " << gcFreed << " objects that refcounting alone leaked." << std::endl;
    return 0;
}
// Time Complexity: append 분할상환 O(1), 참조 횟수 갱신 O(1), 순환 수집 O(컨테이너 수 + 참조 수)
// Space Complexity: 용량이 길이보다 약 12.5% 크다, 객체당 머리말 16바이트
```
## Rust Ownership와 Borrow Checker
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// Rust 의 빌림 검사기(borrow checker)가 컴파일 시점에 하는 일을 간단한 프로그램 표현 위에서 구현한다.
//  규칙: (1) 이동된 값은 사용할 수 없다 (E0382)  (2) 빌려준 동안 이동할 수 없다 (E0505)  (3) 가변 참조가 있는 동안 다른 참조·사용은 금지 (E0502/E0499/E0503)
//  (4) 불변 참조는 여러 개 가능하지만 가변 참조는 하나뿐 — "별칭 XOR 변경"
// 이 구현은 분기(if/else)가 있는 프로그램을 제어 흐름 그래프(CFG)로 만들어 데이터 흐름 분석으로 검사한다 (Rust 의 NLL 처럼 "참조가 마지막으로 쓰이는 곳까지만" 빌림이 살아 있다):
//  앞으로 향한 분석 3 개 — 확실히 선언된 변수(모든 경로의 교집합), 이동되었을 수 있는 소유자(합집합), 만들어졌을 수 있는 빌림(합집합) — 와 뒤로 향한 분석 1 개 — 이후 어떤 경로에서 쓰일 참조(합집합).
//  오류 = (a) 확실히 선언되지 않은 변수 사용 (E0381)  (b) 이동되었을 수 있는 소유자 접근 (E0382/E0505)  (c) 소유자에 대한 접근이 "이후에 쓰이는" 충돌 빌림과 겹침 (읽기는 가변 빌림과, 쓰기·이동·가변 빌림 생성은 모든 빌림과 충돌)
// 검증: 무작위 프로그램 20 000 개(if/else 최대 3 개)에서 이 정적 검사의 통과/거부가, 프로그램의 모든 실행 경로(분기 선택마다 한 경로)를 하나씩 앞에서부터 실행하며
//        "소유자에 접근하면 충돌하는 참조를 무효화하고, 무효화된·정의되지 않은 참조를 쓰면 오류" 로 판정하는 동적 검사와 항상 같다 — 서로 다른 알고리즘(데이터 흐름 vs 경로 열거)이 같은 규칙을 구현함을 보인다.
//        손으로 짠 대표 예: 분기마다 다른 빌림은 통과, 한 분기에서 쓰고 합류 뒤에 참조를 쓰면 거부, 한 분기에서만 이동해도 합류 뒤 사용은 거부
enum Kind { NOP, LET, BORROW, BORROW_MUT, USE, USE_MUT, READ, WRITE, MOVE };       // LET a / BORROW a = &b / BORROW_MUT a = &mut b / USE a (참조로 읽기) / USE_MUT a (참조로 쓰기) / READ a, WRITE a (소유자 직접) / MOVE a -> b
struct Stmt { Kind k = NOP; int a = 0, b = 0; };
struct Item { bool isIf = false; Stmt s; std::vector<Item> thenB, elseB; };
typedef std::vector<Item> Block;

struct Cfg { std::vector<Stmt> st; std::vector<std::vector<int>> succ, pred; };
int newNode(Cfg& g, const Stmt& s) { g.st.push_back(s); g.succ.emplace_back(); g.pred.emplace_back(); return (int)g.st.size() - 1; }
void addEdge(Cfg& g, int a, int b) { g.succ[(size_t)a].push_back(b); g.pred[(size_t)b].push_back(a); }
std::vector<int> build(Cfg& g, const Block& items, std::vector<int> ends) {
    for (const Item& it : items) {
        if (!it.isIf) { int id = newNode(g, it.s); for (int e : ends) addEdge(g, e, id); ends = {id}; }
        else {
            int br = newNode(g, Stmt()); for (int e : ends) addEdge(g, e, br);                    // 분기 지점
            std::vector<int> t = build(g, it.thenB, {br}), e = build(g, it.elseB, {br}); std::set<int> u(t.begin(), t.end()); u.insert(e.begin(), e.end()); ends.assign(u.begin(), u.end());   // 두 갈래의 끝이 다음 문장으로 합류
        }
    }
    return ends;
}
// 접근 분류: 소유자 x 에 대한 접근이면 true (write 는 쓰기/이동/가변 빌림)
bool accessOf(const Stmt& s, int& x, bool& write) {
    switch (s.k) { case BORROW: x = s.b; write = false; return true; case BORROW_MUT: x = s.b; write = true; return true; case READ: x = s.a; write = false; return true;
                   case WRITE: x = s.a; write = true; return true; case MOVE: x = s.a; write = true; return true; default: return false; }
}
bool staticReject(const Cfg& g) {
    size_t n = g.st.size(); std::vector<std::set<int>> defIn(n), movedIn(n), loansIn(n), usedLater(n), defOut(n), movedOut(n), loansOut(n); std::map<int, int> ownerOf; std::map<int, bool> isMut;
    for (size_t i = 0; i < n; ++i) if (g.st[i].k == BORROW || g.st[i].k == BORROW_MUT) { ownerOf[g.st[i].a] = g.st[i].b; isMut[g.st[i].a] = g.st[i].k == BORROW_MUT; }
    for (size_t i = 0; i < n; ++i) {                                                                     // 앞으로: 노드 번호가 위상 순서
        if (!g.pred[i].empty()) {
            defIn[i] = defOut[(size_t)g.pred[i][0]]; for (int p : g.pred[i]) { std::set<int> inter; std::set_intersection(defIn[i].begin(), defIn[i].end(), defOut[(size_t)p].begin(), defOut[(size_t)p].end(), std::inserter(inter, inter.begin())); defIn[i] = inter; }
            for (int p : g.pred[i]) { movedIn[i].insert(movedOut[(size_t)p].begin(), movedOut[(size_t)p].end()); loansIn[i].insert(loansOut[(size_t)p].begin(), loansOut[(size_t)p].end()); }
        }
        defOut[i] = defIn[i]; movedOut[i] = movedIn[i]; loansOut[i] = loansIn[i]; const Stmt& s = g.st[i];
        if (s.k == LET) defOut[i].insert(s.a); if (s.k == BORROW || s.k == BORROW_MUT) { defOut[i].insert(s.a); loansOut[i].insert(s.a); } if (s.k == MOVE) { defOut[i].insert(s.b); movedOut[i].insert(s.a); }
    }
    for (size_t i = n; i-- > 0;) for (int s : g.succ[i]) { usedLater[i].insert(usedLater[(size_t)s].begin(), usedLater[(size_t)s].end()); if (g.st[(size_t)s].k == USE || g.st[(size_t)s].k == USE_MUT) usedLater[i].insert(g.st[(size_t)s].a); }   // 뒤로
    for (size_t i = 0; i < n; ++i) {
        const Stmt& s = g.st[i]; int x; bool write;
        if (s.k == USE || s.k == USE_MUT) { if (!defIn[i].count(s.a)) return true; }                      // 정의되지 않은 참조 (E0381)
        if (!accessOf(s, x, write)) continue;
        if (!defIn[i].count(x) || movedIn[i].count(x)) return true;                                      // 선언 안 됨 / 이동되었을 수 있음 (E0381 / E0382 / E0505)
        for (int r : loansIn[i]) { if (ownerOf[r] != x || !usedLater[i].count(r)) continue; if (write || isMut[r]) return true; }          // 이후에 쓰이는 빌림과의 충돌 (E0502 / E0499 / E0503 / E0505)
    }
    return false;
}

bool dynamicPathHasError(const std::vector<Stmt>& path) {                                                // 한 경로를 앞에서부터 실행
    std::set<int> declared, moved; std::map<int, bool> valid; std::map<int, int> owner; std::map<int, bool> isMut;
    auto invalidate = [&](int x, bool onlyMut) { for (auto& kv : owner) if (kv.second == x && (!onlyMut || isMut[kv.first])) valid[kv.first] = false; };
    for (const Stmt& s : path) {
        switch (s.k) {
            case NOP: break;
            case LET: declared.insert(s.a); break;
            case BORROW: if (!declared.count(s.b) || moved.count(s.b)) return true; invalidate(s.b, true); owner[s.a] = s.b; isMut[s.a] = false; valid[s.a] = true; break;
            case BORROW_MUT: if (!declared.count(s.b) || moved.count(s.b)) return true; invalidate(s.b, false); owner[s.a] = s.b; isMut[s.a] = true; valid[s.a] = true; break;
            case USE: case USE_MUT: if (!valid[s.a]) return true; break;
            case READ: if (!declared.count(s.a) || moved.count(s.a)) return true; invalidate(s.a, true); break;
            case WRITE: if (!declared.count(s.a) || moved.count(s.a)) return true; invalidate(s.a, false); break;
            case MOVE: if (!declared.count(s.a) || moved.count(s.a)) return true; invalidate(s.a, false); moved.insert(s.a); declared.insert(s.b); break;
        }
    }
    return false;
}
void allPaths(const Block& items, size_t idx, std::vector<Stmt> prefix, std::vector<std::vector<Stmt>>& out, const Block* continuation = nullptr, size_t contIdx = 0) {
    // 블록을 앞에서부터 따라가며 if 를 만나면 두 갈래로 나눈다. 갈래가 끝나면 바깥 블록의 나머지를 이어서 실행한다
    if (idx == items.size()) { if (continuation) allPaths(*continuation, contIdx, prefix, out); else out.push_back(prefix); return; }
    const Item& it = items[idx];
    if (!it.isIf) { prefix.push_back(it.s); allPaths(items, idx + 1, prefix, out, continuation, contIdx); return; }
    Block restThen = it.thenB, restElse = it.elseB; Block rest(items.begin() + (long)idx + 1, items.end());
    for (const Block* arm : {&it.thenB, &it.elseB}) { Block seq = *arm; seq.insert(seq.end(), rest.begin(), rest.end()); allPaths(seq, 0, prefix, out, continuation, contIdx); }
}

struct Gen {
    std::mt19937& rng; int next = 0, ifs = 0; std::vector<int> allOwners, allRefs; std::map<int, bool> refMut;
    explicit Gen(std::mt19937& r) : rng(r) {}
    Block block(int len, std::vector<int> owners, std::vector<int> refs, int depth) {
        Block b;
        for (int i = 0; i < len; ++i) {
            int r = (int)(rng() % 100); Item it;
            auto pickOwner = [&]() { return (rng() % 8 == 0 && !allOwners.empty()) ? allOwners[rng() % allOwners.size()] : owners[rng() % owners.size()]; };      // 가끔은 안 보이는(다른 갈래에서 선언된) 변수를 고른다
            auto pickRef = [&]() { return (rng() % 8 == 0 && !allRefs.empty()) ? allRefs[rng() % allRefs.size()] : refs[rng() % refs.size()]; };
            if (owners.empty() || r < 10) { it.s = {LET, next, 0}; owners.push_back(next); allOwners.push_back(next); ++next; }
            else if (r < 28) { it.s = {BORROW, next, pickOwner()}; refs.push_back(next); allRefs.push_back(next); refMut[next] = false; ++next; }
            else if (r < 38) { it.s = {BORROW_MUT, next, pickOwner()}; refs.push_back(next); allRefs.push_back(next); refMut[next] = true; ++next; }
            else if (r < 56 && !refs.empty()) it.s = {USE, pickRef(), 0};
            else if (r < 62) { std::vector<int> mr; for (int q : refs) if (refMut[q]) mr.push_back(q); if (mr.empty()) continue; it.s = {USE_MUT, mr[rng() % mr.size()], 0}; }
            else if (r < 70) it.s = {READ, pickOwner(), 0};
            else if (r < 77) it.s = {WRITE, pickOwner(), 0};
            else if (r < 82) { it.s = {MOVE, pickOwner(), next}; owners.push_back(next); allOwners.push_back(next); ++next; }
            else if (depth < 2 && ifs < 3) { ++ifs; it.isIf = true; it.thenB = block(1 + (int)(rng() % 3), owners, refs, depth + 1); it.elseB = block((int)(rng() % 3), owners, refs, depth + 1); }       // 갈래 안에서 선언한 변수는 밖에서 안 보인다
            else continue;
            b.push_back(it);
        }
        return b;
    }
};
Item stmtItem(Kind k, int a, int b = 0) { Item i; i.s = {k, a, b}; return i; }
Item ifItem(Block t, Block e) { Item i; i.isIf = true; i.thenB = std::move(t); i.elseB = std::move(e); return i; }
bool verdictStatic(const Block& p) { Cfg g; int entry = newNode(g, Stmt()); build(g, p, {entry}); return staticReject(g); }
bool verdictDynamic(const Block& p) { std::vector<std::vector<Stmt>> paths; allPaths(p, 0, {}, paths); for (auto& path : paths) if (dynamicPathHasError(path)) return true; return false; }

int main() {
    // 손으로 짠 예: 0 = x (소유자), 1.. = 참조/새 소유자
    {   Block sepBorrow = {stmtItem(LET, 0), ifItem({stmtItem(BORROW_MUT, 1, 0), stmtItem(USE_MUT, 1)}, {stmtItem(BORROW, 2, 0), stmtItem(USE, 2)}), stmtItem(WRITE, 0)};           // 갈래마다 따로 빌렸다 반납
        Block otherArm = {stmtItem(LET, 0), stmtItem(BORROW, 1, 0), ifItem({stmtItem(USE, 1)}, {stmtItem(WRITE, 0)})};                                                           // 쓰는 갈래에서는 이후 참조를 안 쓴다
        Block joinUse = {stmtItem(LET, 0), stmtItem(BORROW, 1, 0), ifItem({stmtItem(WRITE, 0)}, {}), stmtItem(USE, 1)};                                                           // 한 갈래에서 쓰고 합류 뒤 참조를 쓴다
        Block movedMaybe = {stmtItem(LET, 0), ifItem({stmtItem(MOVE, 0, 1)}, {}), stmtItem(READ, 0)};                                                                              // 한 갈래에서만 이동해도 합류 뒤 사용은 거부
        Block declMaybe = {ifItem({stmtItem(LET, 0)}, {}), stmtItem(READ, 0)};                                                                                                      // 한 갈래에서만 선언
        Block nll = {stmtItem(LET, 0), stmtItem(BORROW, 1, 0), stmtItem(USE, 1), ifItem({stmtItem(WRITE, 0)}, {stmtItem(WRITE, 0)})};                                                // 마지막 사용 뒤라 통과
        for (const Block* b : {&sepBorrow, &otherArm, &nll}) { assert(!verdictStatic(*b) && !verdictDynamic(*b)); }
        for (const Block* b : {&joinUse, &movedMaybe, &declMaybe}) { assert(verdictStatic(*b) && verdictDynamic(*b)); } }
    // 무작위 프로그램
    std::mt19937 rng(1859); long accepted = 0, rejected = 0, withIf = 0, multiPath = 0; 
    for (int it = 0; it < 20000; ++it) {
        Gen gen(rng); Block p = gen.block(5 + (int)(rng() % 10), {}, {}, 0);
        bool s = verdictStatic(p), d = verdictDynamic(p); assert(s == d);                                  // 데이터 흐름 분석 == 모든 경로 실행
        (s ? rejected : accepted)++; bool hasIf = false; for (auto& item : p) hasIf |= item.isIf; withIf += hasIf;
        std::vector<std::vector<Stmt>> paths; allPaths(p, 0, {}, paths); multiPath += paths.size() > 1;
    }
    assert(accepted > 2000 && rejected > 2000 && withIf > 3000 && multiPath > 3000);
    std::cout << "Borrow checker: dataflow (maybe-moved, maybe-loans, definite-init, later-use) agreed with all-paths execution on 20000 random branching programs (" << accepted << " accepted, " << rejected << " rejected, " << withIf << " with branches)." << std::endl;
    return 0;
}
// Time Complexity: 데이터 흐름 O(노드 수 · 변수 수), 경로 열거는 O(2^분기 수 · 문장 수)
// Space Complexity: O(노드 수 · 변수 수)
```
## CUDA 메모리 계층
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// GPU 메모리 계층(대략적인 값, 세대마다 다름): 레지스터(~1 사이클, 스레드 전용) > 공유 메모리(~30, 블록 내 공유, 프로그래머가 관리) > L1(~30) > L2(~200, GPU 전체) > 전역 메모리/HBM(~400~800, 대용량).  빠른 곳일수록 작다.
// 성능을 가르는 것은 이 표 자체보다 접근 *방식* 이다.  CPU 로 규칙을 시뮬레이션해 닫힌 식과 대조한다.
//  ① 코얼레싱: 워프(32 스레드)가 4바이트 값을 읽을 때 필요한 128B 전역 메모리 트랜잭션 수 — 정렬된 연속 접근 1, 보폭 s(≤32) 는 s, 보폭 ≥ 32 는 32, 한 칸 어긋난 연속 접근은 2, 같은 세그먼트 안의 임의 순열은 1 (보폭 1..64 × 시작 오프셋 0..31 전수)
//  ② 공유 메모리 뱅크 충돌: 32 개 뱅크(워드 주소 mod 32), 같은 주소는 방송이라 충돌 아님 — 보폭 s 접근의 충돌 차수 == gcd(s, 32) (s = 1..128 전수), 32×32 타일의 열 접근은 32-way, 폭 33 으로 패딩하면 충돌 없음 (폭 1..64 전수: 차수 == gcd(폭, 32))
//  ③ 타일링: N×N 정수 행렬 곱 세 가지 구현(순진한 / 공유 메모리 타일 T / CPU 기준) 결과가 같고, 전역 메모리 읽기 횟수는 순진한 쪽 정확히 2N³, 타일 쪽 정확히 2N³/T — 평균 지연 모형으로 속도 향상  ④ 점유율(occupancy): SM 당 레지스터·공유 메모리·스레드·블록 한도의 최솟값 공식 == 블록을 하나씩 늘려 가며 한도를 검사하는 전수 계산 (무작위 3 000 조합)
//  ⑤ 지연 숨기기: 워프가 c 사이클 계산 → L 사이클 대기를 반복하고 SM 이 사이클당 한 번 발행할 때 상주 워프 n 개의 이용률 ≈ min(1, n·c/(c+L)) — 사이클 단위 시뮬레이션과 2% 이내 일치하고, 레지스터를 많이 쓰면 상주 워프가 줄어 이용률이 떨어짐
struct Level { const char* name; double latency; double capacityKB; };
int transactions(const std::vector<uint64_t>& byteAddr, int segment = 128) { std::set<uint64_t> segs; for (uint64_t a : byteAddr) segs.insert(a / segment); return (int)segs.size(); }
int bankConflictDegree(const std::vector<uint64_t>& words) { std::vector<std::set<uint64_t>> bank(32); for (uint64_t w : words) bank[w % 32].insert(w); size_t worst = 1; for (auto& b : bank) worst = std::max(worst, b.size()); return (int)worst; }   // 같은 주소는 한 번만 센다(방송)
struct Traffic { long globalLoads = 0, sharedLoads = 0; };
typedef std::vector<int> Mat;
Mat multiplyReference(const Mat& A, const Mat& B, int N) { Mat C(N * N, 0); for (int i = 0; i < N; ++i) for (int j = 0; j < N; ++j) { long s = 0; for (int k = 0; k < N; ++k) s += (long)A[i * N + k] * B[k * N + j]; C[i * N + j] = (int)s; } return C; }
Mat multiplyNaive(const Mat& A, const Mat& B, int N, Traffic& t) { Mat C(N * N, 0); for (int i = 0; i < N; ++i) for (int j = 0; j < N; ++j) { long s = 0; for (int k = 0; k < N; ++k) { s += (long)A[i * N + k] * B[k * N + j]; t.globalLoads += 2; } C[i * N + j] = (int)s; } return C; }       // 곱셈마다 전역 읽기 2 번
Mat multiplyTiled(const Mat& A, const Mat& B, int N, int T, Traffic& t) { Mat C(N * N, 0); std::vector<int> sa(T * T), sb(T * T);                                                                                       // sa, sb: 공유 메모리 타일
    for (int bi = 0; bi < N; bi += T) for (int bj = 0; bj < N; bj += T) { std::vector<long> acc(T * T, 0);
        for (int bk = 0; bk < N; bk += T) { for (int i = 0; i < T; ++i) for (int j = 0; j < T; ++j) { sa[i * T + j] = A[(bi + i) * N + bk + j]; sb[i * T + j] = B[(bk + i) * N + bj + j]; t.globalLoads += 2; }   // 타일 하나를 전역에서 한 번 읽어 온다
            for (int i = 0; i < T; ++i) for (int j = 0; j < T; ++j) for (int k = 0; k < T; ++k) { acc[i * T + j] += (long)sa[i * T + k] * sb[k * T + j]; t.sharedLoads += 2; } }
        for (int i = 0; i < T; ++i) for (int j = 0; j < T; ++j) C[(bi + i) * N + bj + j] = (int)acc[i * T + j]; }
    return C; }
struct SM { int regs, smemBytes, maxThreads, maxBlocks; };
int blocksFormula(const SM& sm, int threadsPerBlock, int regsPerThread, int smemPerBlock) { int b = std::min(sm.maxBlocks, sm.maxThreads / threadsPerBlock); b = std::min(b, sm.regs / (regsPerThread * threadsPerBlock)); if (smemPerBlock > 0) b = std::min(b, sm.smemBytes / smemPerBlock); return b; }
int blocksBrute(const SM& sm, int threadsPerBlock, int regsPerThread, int smemPerBlock) { int b = 0; while (true) { int n = b + 1; if (n > sm.maxBlocks || n * threadsPerBlock > sm.maxThreads || (long)n * regsPerThread * threadsPerBlock > sm.regs || (long)n * smemPerBlock > sm.smemBytes) return b; b = n; } }
double simulateUtilization(int warps, int c, int L, int cycles) { std::vector<int> remaining(warps, c); std::vector<long> readyAt(warps, 0); long issued = 0; int last = 0;                                // GTO(greedy-then-oldest): 직전 워프가 준비돼 있으면 계속, 아니면 가장 오래된 준비 워프
    for (long cyc = 0; cyc < cycles; ++cyc) { int pick = -1; if (readyAt[last] <= cyc) pick = last; else for (int w = 0; w < warps; ++w) if (readyAt[w] <= cyc) { pick = w; break; }
        if (pick < 0) continue; last = pick; --remaining[pick]; ++issued; if (remaining[pick] == 0) { remaining[pick] = c; readyAt[pick] = cyc + 1 + L; } }
    return (double)issued / cycles; }
int main() {
    Level levels[] = {{"register", 1, 256}, {"shared", 30, 100}, {"L2", 200, 40960}, {"global", 600, 40000000}};
    for (int i = 0; i + 1 < 4; i++) assert(levels[i].latency < levels[i + 1].latency); for (int i = 1; i + 1 < 4; i++) assert(levels[i].capacityKB < levels[i + 1].capacityKB);
    for (int s = 1; s <= 64; ++s) for (int off = 0; off < 32; ++off) { std::vector<uint64_t> a; for (int i = 0; i < 32; ++i) a.push_back(((uint64_t)off + (uint64_t)i * s) * 4); int tr = transactions(a);               // ① 코얼레싱
        if (off == 0) assert(tr == std::min(s, 32)); if (s == 1) assert(tr == (off == 0 ? 1 : 2)); assert(tr >= 1 && tr <= 32); }
    { std::mt19937 rng(11); std::vector<uint64_t> perm(32); std::iota(perm.begin(), perm.end(), 0); for (int t = 0; t < 100; ++t) { std::shuffle(perm.begin(), perm.end(), rng); std::vector<uint64_t> a; for (auto p : perm) a.push_back(p * 4); assert(transactions(a) == 1); }
      std::vector<uint64_t> scattered; for (int i = 0; i < 32; ++i) scattered.push_back((uint64_t)i * 4096 + 4 * (rng() % 32)); assert(transactions(scattered) == 32); }
    for (int s = 1; s <= 128; ++s) { std::vector<uint64_t> w; for (int i = 0; i < 32; ++i) w.push_back((uint64_t)i * s); assert(bankConflictDegree(w) == std::gcd(s, 32)); }                         // ② 뱅크 충돌
    { std::vector<uint64_t> same(32, 77); assert(bankConflictDegree(same) == 1);
      for (int W = 1; W <= 64; ++W) { std::vector<uint64_t> col; for (int i = 0; i < 32; ++i) col.push_back((uint64_t)i * W + 5); assert(bankConflictDegree(col) == std::gcd(W, 32)); }
      std::vector<uint64_t> col32, col33; for (int i = 0; i < 32; ++i) { col32.push_back((uint64_t)i * 32 + 7); col33.push_back((uint64_t)i * 33 + 7); } assert(bankConflictDegree(col32) == 32 && bankConflictDegree(col33) == 1); }
    { std::mt19937 rng(5); for (auto cfg : {std::make_pair(16, 4), std::make_pair(32, 8), std::make_pair(48, 16), std::make_pair(64, 16)}) { int N = cfg.first, T = cfg.second; Mat A(N * N), B(N * N); for (auto& x : A) x = (int)(rng() % 21) - 10; for (auto& x : B) x = (int)(rng() % 21) - 10;       // ③ 타일링
        Traffic tn, tt; Mat ref = multiplyReference(A, B, N), naive = multiplyNaive(A, B, N, tn), tiled = multiplyTiled(A, B, N, T, tt); assert(naive == ref && tiled == ref);
        long N3 = (long)N * N * N; assert(tn.globalLoads == 2 * N3 && tt.globalLoads == 2 * N3 / T && tt.sharedLoads == 2 * N3);
        double naiveCost = tn.globalLoads * levels[3].latency, tiledCost = tt.globalLoads * levels[3].latency + tt.sharedLoads * levels[1].latency; assert(tiledCost < naiveCost);
        double ratio = naiveCost / tiledCost; assert(ratio > 1.0 && ratio < T * 1.0); } }                                                                                              // 향상은 T 배보다 작다(공유 메모리 읽기 비용)
    { SM sm = {65536, 100 * 1024, 2048, 32}; assert(blocksFormula(sm, 256, 32, 0) == 8 && blocksFormula(sm, 256, 64, 0) == 4 && blocksFormula(sm, 256, 128, 0) == 2 && blocksFormula(sm, 256, 255, 0) == 1 && blocksFormula(sm, 256, 255, 0) * 256 == 256);   // ④ 점유율
      std::mt19937 rng(21); for (int i = 0; i < 3000; ++i) { SM s = {1 << (14 + rng() % 4), (int)(1024 * (16 + rng() % 200)), 512 * (1 + (int)(rng() % 4)), 8 << (rng() % 3)}; int tpb = 32 * (1 + (int)(rng() % 32)), regs = 8 + (int)(rng() % 248), smem = (int)(rng() % 4) ? (int)(rng() % 60000) : 0; if (tpb > s.maxThreads) continue; assert(blocksFormula(s, tpb, regs, smem) == blocksBrute(s, tpb, regs, smem)); } }
    { const int c = 20, L = 400; for (int warps : {1, 2, 4, 8, 16, 21, 32, 64}) { double sim = simulateUtilization(warps, c, L, 60000), model = std::min(1.0, (double)warps * c / (c + L)); assert(std::abs(sim - model) < 0.02); }      // ⑤ 지연 숨기기
      SM sm = {65536, 100 * 1024, 2048, 32}; auto residentWarps = [&](int regs) { return blocksFormula(sm, 256, regs, 0) * 256 / 32; }; double lowRegs = simulateUtilization(residentWarps(32), c, L, 60000), highRegs = simulateUtilization(residentWarps(255), c, L, 60000);
      assert(residentWarps(32) == 64 && residentWarps(255) == 8 && lowRegs > 0.99 && highRegs < 0.4 && highRegs > 0.35); }                                                        // 레지스터 255개 → 상주 워프 8개 → 이용률 약 38%
    std::cout << "CUDA hierarchy: coalescing, bank-conflict and occupancy formulas matched exhaustive or brute-force computation; tiling cut global loads to exactly 2N^3/T with identical results; at 255 registers per thread only 8 warps stay resident and the SM idles about 62% of cycles" << std::endl;
    return 0;
}
// Time Complexity: 시뮬레이션 O(사이클 × 워프)
// Space Complexity: O(워프 수 + 타일)
```
## 현대 CPU 캐시 계층(L1/L2/L3)
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <list>
#include <random>
#include <vector>
#include <cassert>

// 전형적인 계층: L1 32KB(8-way, ~4사이클, 코어 전용) -> L2 256KB~1MB(~12, 코어 전용) -> L3 수 MB~수십 MB(~40, 코어 간 공유) -> DRAM(~200).
// 작업 집합(working set)의 크기가 어느 단계에 들어가느냐가 성능을 결정한다.  무작위 접근에서 단계별 적중률을 시뮬레이션으로 확인한다
struct Level {
    size_t sets, ways; std::vector<std::list<uint64_t>> s; long hits = 0;
    Level(size_t bytes, size_t w) : sets(bytes / 64 / w), ways(w), s(bytes / 64 / w) {}
    bool lookup(uint64_t line) { auto& set = s[line % sets]; for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); hits++; return true; } return false; }
    void fill(uint64_t line) { auto& set = s[line % sets]; set.push_front(line); if (set.size() > ways) set.pop_back(); }
};
struct Hierarchy {
    Level l1{32 * 1024, 8}, l2{256 * 1024, 8}, l3{8 * 1024 * 1024, 16}; long mem = 0, total = 0;
    void access(uint64_t addr) {
        uint64_t line = addr / 64; total++;
        if (l1.lookup(line)) return;
        if (l2.lookup(line)) { l1.fill(line); return; }
        if (l3.lookup(line)) { l2.fill(line); l1.fill(line); return; }
        mem++; l3.fill(line); l2.fill(line); l1.fill(line);
    }
};
Hierarchy run(size_t workingSetBytes) {
    Hierarchy h; std::mt19937_64 rng(1);
    for (long i = 0; i < 1000000; i++) h.access((rng() % (workingSetBytes / 64)) * 64);       // 작업 집합 안에서 균등 무작위
    return h;
}

int main() {
    auto small = run(16 * 1024);                      // L1 에 들어감
    auto medium = run(128 * 1024);                    // L2 에 들어감
    auto large = run(4 * 1024 * 1024);                // L3 에 들어감
    auto huge = run(64 * 1024 * 1024);                // L3 보다 큼 -> DRAM
    assert(double(small.l1.hits) / small.total > 0.99);                                  // 16KB: 거의 전부 L1
    assert(double(medium.l1.hits) / medium.total < 0.35 && double(medium.l2.hits) / medium.total > 0.60);   // 128KB: L1 은 약 25%, 나머지는 L2
    assert(double(large.l3.hits) / large.total > 0.80 && double(large.mem) / large.total < 0.12);           // 4MB: 대부분 L3
    assert(double(huge.mem) / huge.total > 0.80);                                        // 64MB: 대부분 DRAM 까지 간다
    double amat = 4 + (1 - double(huge.l1.hits) / huge.total) * 12 + (double(huge.mem) / huge.total) * 200;
    std::cout << "hit rates — 16KB: L1 " << 100.0 * small.l1.hits / small.total << "%; 4MB: L3 " << 100.0 * large.l3.hits / large.total << "%; 64MB: DRAM " << 100.0 * huge.mem / huge.total << "% (rough AMAT " << amat << " cycles)" << std::endl;
    return 0;
}
// Time Complexity: O(접근 수 · 단계 수 · ways)
// Space Complexity: O(캐시 크기)
```
