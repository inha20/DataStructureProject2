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
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <cassert>

// 정렬(alignment): 크기 N 인 자료형은 N 의 배수 주소에 놓는 것이 원칙이다 (CPU 가 한 번에 읽는 단위와 캐시 라인에 맞추기 위해).
// alignUp(a, N) = (a + N - 1) & ~(N - 1)   (N 은 2의 거듭제곱)
uintptr_t alignUp(uintptr_t addr, size_t a) { return (addr + a - 1) & ~(uintptr_t)(a - 1); }
bool isAligned(const void* p, size_t a) { return (reinterpret_cast<uintptr_t>(p) & (a - 1)) == 0; }

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
    // 정렬이 맞지 않는 읽기는 memcpy 로 안전하게 (직접 캐스팅하면 일부 CPU 에서 오류, C++ 에서는 정의되지 않은 동작)
    unsigned char raw[8] = {0, 1, 0, 0, 0, 0, 0, 0}; uint32_t v; std::memcpy(&v, raw + 1, 4);
    assert(v == 1 || v == 0x01000000u);                               // 바이트 {1,0,0,0}: 리틀 엔디언이면 1, 빅 엔디언이면 0x01000000
    std::cout << "Alignment verified: alignUp(13,8) = " << alignUp(13, 8) << std::endl;
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
#include <iostream>
#include <cstdint>
#include <cassert>

// 데이터 세그먼트: 정적 저장 기간(static storage duration) 변수가 사는 곳.
//  .data = 0 이 아닌 초기값이 있는 전역/static (초기값이 실행 파일에 저장됨)
//  .bss  = 초기값이 없거나 0 인 전역/static (실행 파일에는 크기만 기록되고 로드될 때 0 으로 채워진다)
// 그래서 큰 배열을 전역으로 선언해도 실행 파일 크기는 거의 늘지 않는다.  static 지역 변수도 여기에 있어 호출 사이에 값이 유지된다
int withValue = 42;                 // .data
int zeroed[1000000];                // .bss: 4MB 인데 파일에는 저장되지 않음
static int counter;                 // .bss, 이 파일에서만 보임

int nextId() { static int id = 100; return id++; }       // static 지역: 첫 호출 때 한 번 초기화

int main() {
    assert(withValue == 42);
    for (int i = 0; i < 1000000; i += 99999) assert(zeroed[i] == 0);   // 전부 0 으로 시작 (보장됨)
    assert(counter == 0);
    assert(nextId() == 100 && nextId() == 101 && nextId() == 102);     // 호출 사이에 값 유지
    zeroed[5] = 9; counter++;
    assert(zeroed[5] == 9 && counter == 1);
    std::cout << "DataSegment: zero-initialized bss array of " << sizeof(zeroed) / 1024 << " KB" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: bss 는 실행 파일 크기에 영향 없음
```
## EnvironmentVariable()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <string>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
extern char** environ;
#endif

// 환경 변수: 프로세스가 시작될 때 부모로부터 "NAME=value" 문자열 배열로 복사받는다 (스택의 맨 위쪽에 놓인다).
// getenv/setenv 는 이 배열을 읽고 고친다.  fork 한 자식은 부모의 환경을 그대로 물려받는다
int main() {
    assert(std::getenv("DS_PROJECT_DEMO") == nullptr);
#if defined(__unix__) || defined(__APPLE__)
    setenv("DS_PROJECT_DEMO", "hello", 1);
    assert(std::string(std::getenv("DS_PROJECT_DEMO")) == "hello");
    bool found = false;
    for (char** e = environ; *e; e++) if (std::strcmp(*e, "DS_PROJECT_DEMO=hello") == 0) found = true;   // 배열에 "NAME=value" 로 들어 있다
    assert(found);
    setenv("DS_PROJECT_DEMO", "world", 0);                          // overwrite=0: 이미 있으면 바꾸지 않는다
    assert(std::string(std::getenv("DS_PROJECT_DEMO")) == "hello");
    unsetenv("DS_PROJECT_DEMO");
    assert(std::getenv("DS_PROJECT_DEMO") == nullptr);
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
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 함수 호출 한 번이 스택에 "프레임" 을 쌓는 과정(호출 규약 요약): 인자 -> 복귀 주소 -> 이전 프레임 포인터(BP) -> 지역 변수.
// 스택은 높은 주소에서 낮은 주소로 자란다 (x86).  시뮬레이션: 8바이트 단위 메모리 위에서 SP 를 내리며 프레임을 만든다
struct Machine {
    std::vector<uint64_t> mem; size_t sp, bp;                          // 인덱스 = 주소 (낮은 주소 = 작은 인덱스)
    explicit Machine(size_t words) : mem(words, 0), sp(words), bp(words) {}
    void push(uint64_t v) { assert(sp > 0); mem[--sp] = v; }
    void pushFrame(uint64_t returnAddr, size_t localWords) {
        push(returnAddr);                                              // call 명령이 복귀 주소를 쌓는다
        push(bp); bp = sp;                                             // 이전 BP 저장, 새 BP = 현재 SP
        sp -= localWords;                                              // 지역 변수 공간 확보
    }
};

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
    std::cout << "PushFrame: SP moved down by " << top - m.sp << " words" << std::endl;
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
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>
#include <cassert>

// malloc 의 핵심 동작을 작은 힙 위에서 단계별로 본다 (first-fit, 분할, 병합).
//   1) 할당 가능한 블록 탐색  2) 필요한 만큼 분할  3) 헤더(크기·사용 여부) 기록  4) 사용자 포인터 = 헤더 바로 뒤
//   free: 사용 표시를 지우고 이웃한 빈 블록과 병합해 단편화를 줄인다
struct Header { size_t size; bool used; };                             // 사용자 영역 크기, 사용 중 여부
class Heap {
    std::vector<uint8_t> mem;
    Header* hdr(size_t off) { return (Header*)&mem[off]; }
    static size_t round8(size_t n) { return (n + 7) & ~size_t(7); }
public:
    explicit Heap(size_t bytes) : mem(bytes) { *hdr(0) = Header{bytes - sizeof(Header), false}; }
    void* alloc(size_t n) {
        n = round8(n);
        for (size_t off = 0; off < mem.size(); off += sizeof(Header) + hdr(off)->size) {       // 1) 첫 번째로 맞는 블록
            Header* h = hdr(off);
            if (h->used || h->size < n) continue;
            if (h->size >= n + sizeof(Header) + 8) {                                           // 2) 남는 부분을 새 빈 블록으로 분할
                *hdr(off + sizeof(Header) + n) = Header{h->size - n - sizeof(Header), false};
                h->size = n;
            }
            h->used = true;                                                                     // 3) 사용 중으로 표시
            return &mem[off + sizeof(Header)];                                                  // 4) 사용자 포인터
        }
        return nullptr;
    }
    void release(void* p) {
        size_t off = (uint8_t*)p - &mem[0] - sizeof(Header);
        hdr(off)->used = false;
        for (size_t o = 0; o < mem.size();) {                                                   // 인접한 빈 블록 병합
            Header* h = hdr(o); size_t next = o + sizeof(Header) + h->size;
            if (!h->used && next < mem.size() && !hdr(next)->used) h->size += sizeof(Header) + hdr(next)->size; else o = next;
        }
    }
    size_t blocks() { size_t c = 0; for (size_t o = 0; o < mem.size(); o += sizeof(Header) + hdr(o)->size) c++; return c; }
    size_t largestFree() { size_t m = 0; for (size_t o = 0; o < mem.size(); o += sizeof(Header) + hdr(o)->size) if (!hdr(o)->used) m = std::max(m, hdr(o)->size); return m; }
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
    assert(h.alloc(5000) == nullptr);                                  // 너무 큰 요청은 실패
    std::cout << "malloc simulation: split, reuse and coalesce verified." << std::endl;
    return 0;
}
// Time Complexity: 할당 O(블록 수) (first-fit), 해제 O(블록 수) (병합 포함)
// Space Complexity: 블록당 헤더 16B
```
## new()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <new>
#include <vector>
#include <cassert>

// new 연산자 = (1) operator new 로 메모리 확보 + (2) 생성자 호출.   delete = (1) 소멸자 호출 + (2) operator delete 로 반환.
// new[] 는 소멸자를 원소마다 불러야 하므로 개수를 메모리 앞쪽에 따로 기록한다(cookie).  할당 실패 시 new 는 bad_alloc 을 던지고 nothrow new 는 nullptr 를 돌려준다
static int allocs = 0, frees = 0;
void* operator new(size_t n) { allocs++; void* p = std::malloc(n); if (!p) throw std::bad_alloc(); return p; }
void operator delete(void* p) noexcept { if (p) frees++; std::free(p); }
void operator delete(void* p, size_t) noexcept { if (p) frees++; std::free(p); }
void* operator new[](size_t n) { allocs++; void* p = std::malloc(n); if (!p) throw std::bad_alloc(); return p; }
void operator delete[](void* p) noexcept { if (p) frees++; std::free(p); }
void operator delete[](void* p, size_t) noexcept { if (p) frees++; std::free(p); }

struct Obj { static int alive; Obj() { alive++; } ~Obj() { alive--; } };
int Obj::alive = 0;

int main() {
    int baseAllocs = allocs, baseFrees = frees;
    Obj* o = new Obj;                                                  // operator new 1번 + 생성자 1번
    assert(allocs == baseAllocs + 1 && Obj::alive == 1);
    delete o;                                                           // 소멸자 + operator delete
    assert(frees == baseFrees + 1 && Obj::alive == 0);
    Obj* arr = new Obj[5];                                              // operator new[] 1번, 생성자 5번
    assert(Obj::alive == 5);
    delete[] arr;                                                       // 소멸자 5번
    assert(Obj::alive == 0);
    bool threw = false;
    volatile size_t huge = (size_t)-1 / 2;                             // 컴파일러가 상수로 판단하지 못하게 volatile
    try { char* volatile sink = new char[huge]; (void)sink; } catch (const std::bad_alloc&) { threw = true; }       // 결과를 volatile 에 담아 컴파일러가 안 쓰는 할당을 지우지 못하게 한다
    assert(threw);                                                      // 실패 -> 예외
    char* volatile probe = new (std::nothrow) char[huge]; assert(probe == nullptr);                  // 실패 -> nullptr
    std::cout << "new/delete: allocs=" << allocs << " frees=" << frees << std::endl;
    return 0;
}
// Time Complexity: 할당기에 따라 다름 (평균 O(1))
// Space Complexity: O(n)
// audit: no-sanitize (터무니없이 큰 할당을 일부러 요청한다)
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
#include <iostream>
#include <cstddef>
#include <cassert>

// 포인터: 다른 객체의 주소를 값으로 갖는 변수.  p + 1 은 "다음 바이트" 가 아니라 "다음 원소"(sizeof(T) 바이트 뒤).
// 배열 이름은 첫 원소의 포인터로 변환(decay)된다.  포인터의 포인터, const 의 위치, nullptr 이 핵심 어휘
int main() {
    int a[5] = {10, 20, 30, 40, 50};
    int* p = a;                                                       // decay: &a[0]
    assert(*p == 10 && *(p + 2) == 30 && p[3] == 40);                 // p[i] == *(p + i)
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
    std::cout << "Pointer: sizeof(pointer) = " << sizeof(void*) << std::endl;
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
#include <iostream>
#include <memory>
#include <vector>
#include <cassert>

// 스마트 포인터: 소멸자에서 자동으로 해제하는 포인터 (RAII).
//  unique_ptr: 단독 소유, 복사 불가·이동만 가능, 오버헤드 0.   shared_ptr: 참조 횟수로 공동 소유, 마지막 소유자가 해제.
//  weak_ptr: 소유하지 않는 관찰자 (순환 참조를 끊거나 캐시에 쓴다).  사용자 지정 삭제자도 가능
int destroyed = 0;
struct Res { ~Res() { destroyed++; } };

int main() {
    {
        std::unique_ptr<Res> u = std::make_unique<Res>();
        std::unique_ptr<Res> v = std::move(u);                         // 소유권 이전
        assert(!u && v);
    }                                                                   // 범위를 벗어나면 자동 소멸
    assert(destroyed == 1);

    std::shared_ptr<Res> s1 = std::make_shared<Res>();
    std::weak_ptr<Res> w = s1;
    {
        std::shared_ptr<Res> s2 = s1;                                  // 공동 소유
        assert(s1.use_count() == 2);
    }
    assert(s1.use_count() == 1 && !w.expired());
    s1.reset();                                                         // 마지막 소유자가 사라지면 해제
    assert(destroyed == 2 && w.expired() && w.lock() == nullptr);

    int closed = 0;
    {
        std::unique_ptr<int, void(*)(int*)> custom(new int(5), [](int* p) { delete p; });     // 사용자 지정 삭제자
        auto file = std::shared_ptr<int>(new int(1), [&closed](int* p) { delete p; closed++; });
    }
    assert(closed == 1);
    std::cout << "SmartPointer verified." << std::endl;
    return 0;
}
// Time Complexity: unique_ptr O(1), shared_ptr 복사 O(1) (원자적 카운터)
// Space Complexity: shared_ptr 은 제어 블록 추가
```
## Aliasing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <cassert>

// 앨리어싱: 서로 다른 이름이 같은 메모리를 가리키는 것.  컴파일러는 "다른 타입의 포인터는 같은 메모리를 가리키지 않는다"(엄격한 앨리어싱 규칙)고
// 가정해 최적화하므로, float 비트를 uint32_t* 로 읽는 reinterpret_cast 는 정의되지 않은 동작이다.  안전한 방법은 memcpy (컴파일러가 한 명령으로 최적화한다)
uint32_t floatBits(float f) { uint32_t u; std::memcpy(&u, &f, sizeof u); return u; }
float bitsFloat(uint32_t u) { float f; std::memcpy(&f, &u, sizeof f); return f; }

bool overlaps(const void* a, size_t na, const void* b, size_t nb) {
    auto x = (uintptr_t)a, y = (uintptr_t)b; return x < y + nb && y < x + na;
}

int main() {
    assert(floatBits(1.0f) == 0x3f800000u);                           // IEEE-754: 1.0f 의 비트 패턴
    assert(floatBits(-2.0f) == 0xc0000000u);
    assert(bitsFloat(0x40490fdbu) > 3.14159f && bitsFloat(0x40490fdbu) < 3.1416f);   // 비트 패턴 -> π
    int v = 5; int* p = &v; int* q = &v;                               // 같은 타입의 앨리어싱은 합법: 한쪽을 바꾸면 다른 쪽에도 보인다
    *p = 6; assert(*q == 6);
    char buf[10] = "abcdefghi";
    assert(overlaps(buf, 5, buf + 3, 5) && !overlaps(buf, 3, buf + 5, 3));
    std::memmove(buf + 2, buf, 5);                                      // 영역이 겹치면 memcpy 가 아니라 memmove
    assert(std::memcmp(buf, "ababcdeh", 8) == 0);
    std::cout << "Aliasing verified: 1.0f bits = " << std::hex << floatBits(1.0f) << std::endl;
    return 0;
}
// Time Complexity: O(1), memmove O(n)
// Space Complexity: O(1)
```
# Part 6. 메모리 할당기
## MemoryPool()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <set>
#include <cassert>

// 메모리 풀: 같은 크기의 블록 N 개를 한 번에 확보해 두고 자유 리스트로 나눠 준다.  빈 블록의 앞부분에 "다음 빈 블록" 포인터를 저장하므로 추가 메모리가 없고,
// 할당·해제가 모두 O(1) 포인터 교환이다.  크기가 같아서 외부 단편화가 없다.  malloc 의 탐색·병합 비용이 없어 게임·네트워크 서버에서 많이 쓴다
class MemoryPool {
    char* mem; void* head = nullptr; size_t blockSize, count, used = 0;
public:
    MemoryPool(size_t block, size_t n) : blockSize(block < sizeof(void*) ? sizeof(void*) : block), count(n) {
        mem = new char[blockSize * count];
        for (size_t i = count; i-- > 0;) { void* b = mem + i * blockSize; *(void**)b = head; head = b; }   // 모든 블록을 리스트로 연결
    }
    ~MemoryPool() { delete[] mem; }
    void* alloc() { if (!head) return nullptr; void* b = head; head = *(void**)b; used++; return b; }
    void release(void* b) { *(void**)b = head; head = b; used--; }
    size_t inUse() const { return used; }
    bool owns(void* p) const { return (char*)p >= mem && (char*)p < mem + blockSize * count; }
};

int main() {
    MemoryPool pool(32, 4);
    void* b[4]; std::set<void*> distinct;
    for (int i = 0; i < 4; i++) { b[i] = pool.alloc(); assert(b[i] && pool.owns(b[i])); distinct.insert(b[i]); }
    assert(distinct.size() == 4);                                  // 서로 다른 블록
    assert(pool.alloc() == nullptr && pool.inUse() == 4);          // 풀이 가득 차면 nullptr
    pool.release(b[1]); pool.release(b[3]);
    assert(pool.alloc() == b[3] && pool.alloc() == b[1]);          // 가장 최근에 반환된 블록이 먼저 재사용 (LIFO, 캐시에 따뜻함)
    assert(((uintptr_t)b[0] - (uintptr_t)b[1]) % 32 == 0);          // 블록 크기 간격
    std::cout << "MemoryPool verified: O(1) alloc/free, LIFO reuse." << std::endl;
    return 0;
}
// Time Complexity: 할당·해제 O(1)
// Space Complexity: O(블록 크기 · 개수)
```
## ObjectPool()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <new>
#include <string>
#include <vector>
#include <cassert>

// 객체 풀: 메모리 풀 위에 "객체 생명주기" 를 얹는다.  acquire 는 배치 new 로 생성자를, release 는 소멸자를 부르고 메모리는 풀에 남겨 재사용한다.
// 생성 비용이 큰 객체(연결, 스레드, 버퍼)를 재사용하는 데 쓰이고, 반환되지 않은 객체의 수로 누수를 바로 알 수 있다
template <class T>
class ObjectPool {
    std::vector<void*> freeList; std::vector<std::unique_ptr<unsigned char[]>> chunks; size_t live = 0;
public:
    template <class... A> T* acquire(A&&... args) {
        if (freeList.empty()) { chunks.emplace_back(new unsigned char[sizeof(T) + alignof(T)]); void* raw = chunks.back().get(); size_t space = sizeof(T) + alignof(T); freeList.push_back(std::align(alignof(T), sizeof(T), raw, space)); }
        void* slot = freeList.back(); freeList.pop_back(); live++;
        return new (slot) T(std::forward<A>(args)...);
    }
    void release(T* obj) { obj->~T(); freeList.push_back(obj); live--; }
    size_t liveCount() const { return live; }
    size_t chunkCount() const { return chunks.size(); }
};

int constructed = 0, destroyed = 0;
struct Conn { std::string host; explicit Conn(std::string h) : host(std::move(h)) { constructed++; } ~Conn() { destroyed++; } };

int main() {
    ObjectPool<Conn> pool;
    Conn* a = pool.acquire("alpha");
    Conn* b = pool.acquire("beta");
    assert(a->host == "alpha" && b->host == "beta" && pool.liveCount() == 2 && constructed == 2);
    pool.release(a);                                               // 소멸자는 호출되지만 메모리는 풀에 남는다
    assert(destroyed == 1 && pool.liveCount() == 1);
    Conn* c = pool.acquire("gamma");
    assert(c == a && c->host == "gamma");                          // 같은 자리를 재사용 -> 새 할당 없음
    assert(pool.chunkCount() == 2);
    pool.release(b); pool.release(c);
    assert(pool.liveCount() == 0 && constructed == destroyed);     // 생성 수 == 소멸 수 -> 누수 없음
    std::cout << "ObjectPool: " << constructed << " constructed, " << pool.chunkCount() << " chunks" << std::endl;
    return 0;
}
// Time Complexity: acquire/release 평균 O(1)
// Space Complexity: O(최대 동시 객체 수)
```
## FreeList()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <vector>
#include <cassert>

// 자유 리스트 할당기: 비어 있는 구멍(hole)을 주소순 리스트로 유지한다.  요청이 오면 어떤 구멍을 쓸지가 정책이다.
//   first-fit: 처음 맞는 구멍 (빠름)   best-fit: 가장 작게 맞는 구멍 (남는 조각이 가장 작음, 아주 작은 조각이 많이 생김)   worst-fit: 가장 큰 구멍 (남는 조각이 큼)
// 해제할 때는 인접한 구멍과 병합해 외부 단편화를 줄인다
struct Hole { size_t off, size; };
enum Policy { FIRST, BEST, WORST };
class FreeList {
public:
    std::vector<Hole> holes;
    long alloc(size_t n, Policy p) {
        int pick = -1;
        for (size_t i = 0; i < holes.size(); i++) {
            if (holes[i].size < n) continue;
            if (pick < 0 || (p == BEST && holes[i].size < holes[pick].size) || (p == WORST && holes[i].size > holes[pick].size)) pick = i;
            if (p == FIRST) break;
        }
        if (pick < 0) return -1;
        size_t off = holes[pick].off;
        holes[pick].off += n; holes[pick].size -= n;
        if (holes[pick].size == 0) holes.erase(holes.begin() + pick);
        return off;
    }
    void release(size_t off, size_t n) {
        holes.push_back({off, n});
        std::sort(holes.begin(), holes.end(), [](const Hole& a, const Hole& b) { return a.off < b.off; });
        for (size_t i = 0; i + 1 < holes.size();) {                 // 인접한 구멍 병합
            if (holes[i].off + holes[i].size == holes[i + 1].off) { holes[i].size += holes[i + 1].size; holes.erase(holes.begin() + i + 1); } else i++;
        }
    }
    double fragmentation() const { size_t tot = 0, mx = 0; for (auto& h : holes) { tot += h.size; mx = std::max(mx, h.size); } return tot ? 1.0 - double(mx) / tot : 0; }
};

int main() {
    auto make = [] { FreeList f; f.holes = {{0, 100}, {150, 30}, {300, 60}, {500, 200}}; return f; };
    FreeList a = make(), b = make(), c = make();
    assert(a.alloc(25, FIRST) == 0);                                 // 첫 구멍(0, 크기 100)
    assert(b.alloc(25, BEST) == 150);                                // 가장 딱 맞는 구멍(150, 크기 30) -> 남는 조각 5
    assert(c.alloc(25, WORST) == 500);                               // 가장 큰 구멍(500, 크기 200)
    assert(b.holes[1].size == 5);                                    // best-fit 이 남긴 아주 작은 조각
    assert(a.alloc(1000, FIRST) == -1);                              // 외부 단편화: 전체 합은 390 이지만 연속 1000 은 없다
    FreeList d; d.holes = {{0, 10}};
    d.release(10, 10); d.release(30, 10);                            // 인접 병합: [0,20) 과 [30,40)
    assert(d.holes.size() == 2 && d.holes[0].size == 20);
    d.release(20, 10);                                               // 가운데를 채우면 세 구멍이 하나로
    assert(d.holes.size() == 1 && d.holes[0].size == 40);
    assert(make().fragmentation() > 0.4);
    std::cout << "FreeList: first-fit=0, best-fit=150, worst-fit=500" << std::endl;
    return 0;
}
// Time Complexity: 할당 O(구멍 수), 해제 O(구멍 수 log 구멍 수)
// Space Complexity: O(구멍 수)
```
## SlabAllocator()
### 대표코드
```cpp
#include <iostream>
#include <bitset>
#include <memory>
#include <vector>
#include <cassert>

// 슬랩 할당기(리눅스 커널): 한 종류의 객체만 담는 "슬랩(고정 크기 페이지)" 여러 개를 관리한다.  슬랩은 부분(partial)·가득(full)·빈(empty) 상태로 나뉘고
// 할당은 부분 슬랩에서 우선한다 -> 슬랩을 거의 가득 채워 쓰고 빈 슬랩은 반환하므로 단편화가 적다.  객체를 미리 초기화해 두면 생성 비용도 줄인다
class SlabCache {
    static const int PER_SLAB = 8;
    struct Slab { std::unique_ptr<char[]> mem; std::bitset<PER_SLAB> used; int count = 0; };
    size_t objSize; std::vector<std::unique_ptr<Slab>> slabs;
public:
    long created = 0, destroyed = 0;
    explicit SlabCache(size_t sz) : objSize(sz) {}
    void* alloc() {
        Slab* s = nullptr;
        for (auto& x : slabs) if (x->count < PER_SLAB && (!s || x->count > s->count)) s = x.get();   // 가장 찬 부분 슬랩 우선
        if (!s) { slabs.emplace_back(new Slab{std::unique_ptr<char[]>(new char[objSize * PER_SLAB]), {}, 0}); s = slabs.back().get(); created++; }
        for (int i = 0; i < PER_SLAB; i++) if (!s->used[i]) { s->used[i] = 1; s->count++; return s->mem.get() + i * objSize; }
        return nullptr;
    }
    void release(void* p) {
        for (size_t k = 0; k < slabs.size(); k++) {
            char* base = slabs[k]->mem.get();
            if ((char*)p >= base && (char*)p < base + objSize * PER_SLAB) {
                slabs[k]->used[((char*)p - base) / objSize] = 0; slabs[k]->count--;
                int empties = 0; for (auto& x : slabs) empties += x->count == 0;
                if (slabs[k]->count == 0 && empties > 1) { slabs.erase(slabs.begin() + k); destroyed++; }     // 빈 슬랩은 하나만 남기고 반환
                return;
            }
        }
    }
    size_t slabCount() const { return slabs.size(); }
};

int main() {
    SlabCache cache(128);
    std::vector<void*> objs;
    for (int i = 0; i < 20; i++) objs.push_back(cache.alloc());
    assert(cache.slabCount() == 3 && cache.created == 3);          // 20개 -> 슬랩 3개 (8 + 8 + 4)
    for (int i = 8; i < 16; i++) cache.release(objs[i]);           // 가운데 슬랩을 전부 반환
    assert(cache.slabCount() == 3 || cache.slabCount() == 2);      // 빈 슬랩은 하나까지만 보유
    void* again = cache.alloc();                                   // 부분 슬랩(가장 찬 슬랩)을 우선 사용
    assert(again != nullptr);
    for (int i = 0; i < 8; i++) cache.release(objs[i]);
    for (int i = 16; i < 20; i++) cache.release(objs[i]);
    cache.release(again);
    assert(cache.slabCount() == 1);                                // 전부 반환하면 빈 슬랩 하나만 남는다
    std::cout << "SlabAllocator: created=" << cache.created << " destroyed=" << cache.destroyed << " remaining=" << cache.slabCount() << std::endl;
    return 0;
}
// Time Complexity: 할당 O(슬랩 수) (구현의 단순화), 실제 커널은 리스트로 O(1)
// Space Complexity: O(슬랩 수 · 슬랩 크기)
```
## BuddyAllocator()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 버디 할당기(리눅스 페이지 할당기): 메모리를 2의 거듭제곱 크기 블록으로 관리한다.  요청은 가장 가까운 큰 2의 거듭제곱으로 올리고(내부 단편화),
// 큰 블록을 반으로 쪼개 쓰고, 해제할 때 "버디"(같은 부모에서 나온 짝, 주소가 offset ^ size)가 비어 있으면 합친다.  병합이 빠르고 외부 단편화에 강하다
class Buddy {
    static const int MAX_ORDER = 4;                                 // 최소 블록 64B ... 최대 1024B (order 4)
    std::set<size_t> freeLists[MAX_ORDER + 1];
    static size_t sizeOf(int order) { return size_t(64) << order; }
public:
    Buddy() { freeLists[MAX_ORDER].insert(0); }
    long alloc(size_t n, int* orderOut = nullptr) {
        int k = 0; while (k <= MAX_ORDER && sizeOf(k) < n) k++;
        if (k > MAX_ORDER) return -1;
        int j = k; while (j <= MAX_ORDER && freeLists[j].empty()) j++;   // 쓸 수 있는 가장 작은 큰 블록
        if (j > MAX_ORDER) return -1;
        size_t off = *freeLists[j].begin(); freeLists[j].erase(freeLists[j].begin());
        while (j > k) { j--; freeLists[j].insert(off + sizeOf(j)); }     // 반으로 쪼개고 오른쪽 절반은 빈 블록으로
        if (orderOut) *orderOut = k;
        return off;
    }
    void release(size_t off, int order) {
        while (order < MAX_ORDER) {
            size_t buddy = off ^ sizeOf(order);                         // 버디의 주소는 XOR 한 번
            auto it = freeLists[order].find(buddy);
            if (it == freeLists[order].end()) break;
            freeLists[order].erase(it); off = std::min(off, buddy); order++;     // 합쳐서 한 단계 위로
        }
        freeLists[order].insert(off);
    }
    size_t freeBlocks(int order) const { return freeLists[order].size(); }
};

int main() {
    Buddy b; int oa, ob, oc;
    long a = b.alloc(100, &oa);                                      // 100B -> 128B 블록 (내부 단편화 28B)
    assert(a == 0 && oa == 1);
    long c = b.alloc(100, &ob);                                      // 이웃한 128B 블록
    assert(c == 128 && ob == 1);
    long d = b.alloc(300, &oc);                                      // 300B -> 512B 블록
    assert(d == 512 && oc == 3);
    assert(b.freeBlocks(2) == 1 && b.freeBlocks(1) == 0);            // 남은 빈 블록: [256, 512)
    b.release(a, oa);
    b.release(d, oc);
    assert(b.freeBlocks(1) == 1);                                    // c 가 남아 있어 a 는 버디와 합쳐지지 못함
    b.release(c, ob);                                                // 마지막 해제 -> 연쇄 병합
    assert(b.freeBlocks(4) == 1 && b.freeBlocks(0) + b.freeBlocks(1) + b.freeBlocks(2) + b.freeBlocks(3) == 0);   // 다시 1024B 하나로
    assert(b.alloc(2000) == -1);
    std::cout << "BuddyAllocator: split on alloc, coalesce on free (buddy = addr XOR size)" << std::endl;
    return 0;
}
// Time Complexity: 할당·해제 O(log N) (order 수)
// Space Complexity: O(블록 수)
```
## ArenaAllocator()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>
#include <string>
#include <cassert>

// 아레나(범프) 할당기: 포인터 하나를 앞으로 밀기만 한다.  할당이 가장 빠르고(덧셈 한 번), 개별 해제는 없고 아레나 전체를 한 번에 비운다.
// 컴파일러의 AST, 요청 하나를 처리하는 동안의 임시 객체, 게임의 프레임별 메모리에 적합.  mark/rollback 으로 부분 되돌리기도 가능
class Arena {
    std::unique_ptr<unsigned char[]> buf; size_t cap, top = 0;
public:
    explicit Arena(size_t n) : buf(new unsigned char[n]), cap(n) {}
    void* alloc(size_t n, size_t align = alignof(std::max_align_t)) {
        uintptr_t cur = (uintptr_t)buf.get() + top;
        uintptr_t aligned = (cur + align - 1) & ~(uintptr_t)(align - 1);
        size_t newTop = aligned - (uintptr_t)buf.get() + n;
        if (newTop > cap) return nullptr;
        top = newTop;
        return (void*)aligned;
    }
    template <class T, class... A> T* make(A&&... a) { void* p = alloc(sizeof(T), alignof(T)); return p ? new (p) T(std::forward<A>(a)...) : nullptr; }
    size_t mark() const { return top; }
    void rollback(size_t m) { top = m; }
    void reset() { top = 0; }
    size_t used() const { return top; }
};

int main() {
    Arena a(1024);
    char* c = (char*)a.alloc(1, 1);
    double* d = (double*)a.alloc(sizeof(double), alignof(double));
    assert((uintptr_t)d % alignof(double) == 0 && (char*)d > c);       // 패딩을 넣어 정렬을 맞춘다
    size_t m = a.mark();
    int* tmp = a.make<int>(42); assert(*tmp == 42);
    std::string* s = a.make<std::string>("arena string"); assert(*s == "arena string");
    s->~basic_string();                                                  // 소멸자가 필요한 객체는 직접 정리해야 한다
    a.rollback(m);                                                       // 임시 객체들을 한꺼번에 버린다
    assert(a.used() == m);
    assert(a.alloc(2000) == nullptr);                                    // 용량 초과
    a.reset();
    assert(a.used() == 0 && a.alloc(1000) != nullptr);
    std::cout << "ArenaAllocator verified: bump pointer, rollback, reset." << std::endl;
    return 0;
}
// Time Complexity: 할당 O(1), 해제 O(1) (전체)
// Space Complexity: O(용량)
```
# Part 7. 가비지 컬렉션
## MarkSweep()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 마크-스윕: (1) 루트(스택·전역 변수)에서 닿는 객체를 모두 표시(mark)하고, (2) 힙 전체를 훑어 표시되지 않은 객체를 해제(sweep)한다.
// 순환 참조도 올바르게 회수하고, 객체를 옮기지 않아 포인터가 안정적이다.  단점: 힙 전체를 훑고 단편화가 생기며 수집 중 멈춤(stop-the-world)이 있다
struct Obj { std::vector<int> refs; bool alive = false, marked = false; };
struct Heap {
    std::vector<Obj> objs; std::vector<int> roots;
    int alloc() { for (size_t i = 0; i < objs.size(); i++) if (!objs[i].alive) { objs[i] = Obj{}; objs[i].alive = true; return i; } objs.push_back(Obj{}); objs.back().alive = true; return objs.size() - 1; }
    void mark() {
        std::vector<int> stack(roots.begin(), roots.end());
        while (!stack.empty()) {
            int i = stack.back(); stack.pop_back();
            if (objs[i].marked) continue;
            objs[i].marked = true;
            for (int r : objs[i].refs) stack.push_back(r);
        }
    }
    int sweep() {
        int freed = 0;
        for (auto& o : objs) { if (o.alive && !o.marked) { o.alive = false; o.refs.clear(); freed++; } o.marked = false; }
        return freed;
    }
    int collect() { mark(); return sweep(); }
    int liveCount() const { int c = 0; for (auto& o : objs) c += o.alive; return c; }
};

int main() {
    Heap h;
    int a = h.alloc(), b = h.alloc(), c = h.alloc(), d = h.alloc(), e = h.alloc();
    h.roots = {a};
    h.objs[a].refs = {b}; h.objs[b].refs = {c};            // a -> b -> c  (루트에서 닿는다)
    h.objs[d].refs = {e}; h.objs[e].refs = {d};            // d <-> e  (서로만 가리키는 순환, 루트에서 닿지 않음)
    assert(h.liveCount() == 5);
    assert(h.collect() == 2);                               // 순환 참조된 d, e 가 회수된다
    assert(h.liveCount() == 3 && h.objs[a].alive && h.objs[b].alive && h.objs[c].alive);
    h.objs[b].refs.clear();                                 // b -> c 끊기
    assert(h.collect() == 1 && !h.objs[c].alive);
    int reused = h.alloc();                                 // 회수된 칸을 재사용
    assert(reused == c || reused == d || reused == e);
    std::cout << "MarkSweep verified: cycle collected, live=" << h.liveCount() << std::endl;
    return 0;
}
// Time Complexity: O(살아있는 객체 + 힙 전체) (마크 + 스윕)
// Space Complexity: O(깊이) 마크 스택
```
## MarkCompact()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 마크-컴팩트(Lisp2 방식): 표시 후 살아있는 객체를 한쪽으로 밀어 붙여(slide) 단편화를 없앤다.  객체의 상대 순서가 유지된다.
//   (1) mark  (2) 새 주소(forwarding address) 계산  (3) 모든 참조를 새 주소로 갱신  (4) 객체 이동
struct Obj { int payload; std::vector<int> refs; bool alive = false, marked = false; int fwd = -1; };

int main() {
    std::vector<Obj> heap(8);
    auto make = [&](int i, int payload, std::vector<int> refs) { heap[i] = Obj{payload, refs, true, false, -1}; };
    make(0, 100, {2}); make(1, 111, {}); make(2, 102, {4}); make(3, 113, {}); make(4, 104, {2}); make(5, 115, {}); make(6, 106, {0}); // 1,3,5 는 쓰레기
    std::vector<int> roots = {6};

    // 1) mark
    std::vector<int> st = roots;
    while (!st.empty()) { int i = st.back(); st.pop_back(); if (heap[i].marked) continue; heap[i].marked = true; for (int r : heap[i].refs) st.push_back(r); }
    // 순회 결과(이동 전) 기록: 루트에서 DFS 로 본 payload 순서
    auto walk = [&](std::vector<int> start) { std::vector<int> out, s = start; std::vector<bool> seen(heap.size(), false);
        while (!s.empty()) { int i = s.back(); s.pop_back(); if (seen[i]) continue; seen[i] = true; out.push_back(heap[i].payload); for (int k = heap[i].refs.size(); k-- > 0;) s.push_back(heap[i].refs[k]); } return out; };
    std::vector<int> before = walk(roots);
    // 2) forwarding address
    int next = 0; for (size_t i = 0; i < heap.size(); i++) if (heap[i].alive && heap[i].marked) heap[i].fwd = next++;
    // 3) 참조 갱신
    for (auto& o : heap) if (o.alive && o.marked) for (int& r : o.refs) r = heap[r].fwd;
    for (int& r : roots) r = heap[r].fwd;
    // 4) 이동 (앞쪽으로 밀기: 목적지 <= 원래 위치이므로 순서대로 옮겨도 안전)
    for (size_t i = 0; i < heap.size(); i++) if (heap[i].alive && heap[i].marked) { int dst = heap[i].fwd; Obj o = heap[i]; o.marked = false; o.fwd = -1; heap[dst] = o; }
    for (int i = next; i < (int)heap.size(); i++) heap[i] = Obj{};
    assert(next == 4);                                                     // 살아남은 객체 4개: 0, 2, 4, 6
    for (int i = 0; i < next; i++) assert(heap[i].alive);                 // 앞쪽에 빈틈 없이 모였다
    for (int i = next; i < (int)heap.size(); i++) assert(!heap[i].alive);
    assert(heap[0].payload == 100 && heap[1].payload == 102 && heap[2].payload == 104 && heap[3].payload == 106);   // 상대 순서 유지
    assert(walk(roots) == before);                                         // 이동 후에도 그래프 구조(참조 관계)가 같다
    std::cout << "MarkCompact: live objects slid to [0," << next << ")" << std::endl;
    return 0;
}
// Time Complexity: O(힙 크기) · 3~4 패스
// Space Complexity: O(1) 추가 (forwarding 주소는 객체 헤더에 저장)
```
## CopyingGC()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 복사 수집(Cheney 알고리즘): 힙을 from-space/to-space 로 나눈다.  루트에서 닿는 객체를 to-space 로 "복사" 하며 원본에는 전달 주소(forwarding pointer)를 남겨
// 공유된 객체가 두 번 복사되지 않게 한다.  to-space 의 scan 포인터가 free 포인터를 따라잡으면 끝(BFS).  비용은 살아있는 객체에 비례(쓰레기는 방문조차 안 함),
// 결과가 자동으로 압축된다.  단점: 힙의 절반만 쓸 수 있다
struct Obj { int payload; std::vector<int> refs; int fwd = -1; };

int main() {
    std::vector<Obj> from = {{0, {1, 2}}, {1, {3}}, {2, {3}}, {3, {0}}, {4, {5}}, {5, {4}}, {6, {}}};   // 0->1,2 ; 1->3 ; 2->3 ; 3->0 (순환) ; 4<->5 (쓰레기) ; 6 (쓰레기)
    std::vector<int> roots = {0};
    std::vector<Obj> to;
    auto copy = [&](int i) -> int {                          // 이미 복사됐으면 전달 주소를 돌려준다
        if (from[i].fwd >= 0) return from[i].fwd;
        to.push_back(Obj{from[i].payload, from[i].refs, -1});
        from[i].fwd = to.size() - 1;
        return from[i].fwd;
    };
    for (int& r : roots) r = copy(r);
    for (size_t scan = 0; scan < to.size(); scan++)          // scan 포인터가 free(to.size()) 를 따라잡을 때까지
        for (int& r : to[scan].refs) r = copy(r);
    assert(to.size() == 4);                                   // 도달 가능한 0,1,2,3 만 복사 (4,5,6 은 방문하지 않음)
    assert(to[roots[0]].payload == 0);
    // 공유된 객체 3 은 하나만 복사되어 1 과 2 가 같은 사본을 가리킨다
    int p1 = to[to[roots[0]].refs[0]].refs[0], p2 = to[to[roots[0]].refs[1]].refs[0];
    assert(p1 == p2 && to[p1].payload == 3);
    assert(to[to[p1].refs[0]].payload == 0 && to[p1].refs[0] == roots[0]);   // 순환 3 -> 0 도 올바르게 보존
    from.swap(to);                                            // 역할 교대: to-space 가 새 from-space
    assert(from.size() == 4);
    std::cout << "CopyingGC: 7 objects -> " << from.size() << " survivors, compacted automatically" << std::endl;
    return 0;
}
// Time Complexity: O(살아있는 객체)
// Space Complexity: O(힙) · 2 (두 공간)
```
## GenerationalGC()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 세대별 수집: "대부분의 객체는 금방 죽는다"(약한 세대 가설).  새 객체는 young 에 두고 자주·싸게 수집(minor GC), 두 번 이상 살아남으면 old 로 승급해 드물게 수집한다.
// 문제: old 객체가 young 객체를 가리키면 minor GC 가 old 전체를 훑지 않고도 알아야 한다 -> 쓰기 장벽(write barrier)이 "old -> young 참조" 를 기억 집합(remembered set)에 기록
struct Obj { int id; std::vector<int> refs; bool old = false; int age = 0; };

struct Heap {
    std::vector<Obj> objs; std::set<int> alive; std::vector<int> roots; std::set<int> remembered;   // old 에 있으면서 young 을 가리키는 객체들
    int make() { objs.push_back(Obj{(int)objs.size(), {}, false, 0}); alive.insert(objs.size() - 1); return objs.size() - 1; }
    void writeRef(int from, int to) {
        objs[from].refs.push_back(to);
        if (objs[from].old && !objs[to].old) remembered.insert(from);          // 쓰기 장벽
    }
    // useRemembered=false 는 장벽을 빼먹은 잘못된 구현을 보여주기 위한 것
    int minorGC(bool useRemembered) {
        std::set<int> live; std::vector<int> st(roots.begin(), roots.end());
        if (useRemembered) for (int r : remembered) for (int c : objs[r].refs) st.push_back(c);
        while (!st.empty()) {
            int i = st.back(); st.pop_back();
            if (objs[i].old || live.count(i)) continue;                         // old 는 minor GC 에서 건드리지 않는다
            live.insert(i);
            for (int c : objs[i].refs) st.push_back(c);
        }
        int freed = 0;
        for (auto it = alive.begin(); it != alive.end();) {
            if (!objs[*it].old && !live.count(*it)) { it = alive.erase(it); freed++; } else ++it;
        }
        for (int i : live) if (++objs[i].age >= 2) objs[i].old = true;          // 두 번 살아남으면 승급
        return freed;
    }
};

int main() {
    auto scenario = [](bool useRemembered) {
        Heap h;
        int oldObj = h.make(); h.roots = {oldObj};
        h.minorGC(true); h.minorGC(true);                 // 두 번 살아남아 oldObj 가 old 세대로 승급
        assert(h.objs[oldObj].old);
        int young = h.make(); int garbage = h.make();      // 새 객체 둘: young 은 old 객체가 참조, garbage 는 아무도 참조 안 함
        h.writeRef(oldObj, young);                         // old -> young 참조 (쓰기 장벽 발동)
        int freed = h.minorGC(useRemembered);
        return std::make_tuple(freed, h.alive.count(young) > 0, h.alive.count(garbage) > 0);
    };
    auto good = scenario(true), bad = scenario(false);
    assert(std::get<0>(good) == 1 && std::get<1>(good) && !std::get<2>(good));    // 쓰레기만 회수, young 은 생존
    assert(!std::get<1>(bad));                                                     // 기억 집합이 없으면 살아있는 young 객체를 잘못 회수한다
    std::cout << "GenerationalGC: remembered set keeps old->young referents alive" << std::endl;
    return 0;
}
// Time Complexity: minor GC 는 young 크기 + 기억 집합에 비례
// Space Complexity: O(기억 집합)
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
#include <iostream>
#include <vector>
#include <cassert>

// 증분 수집: 마킹을 작은 조각으로 쪼개 프로그램(뮤테이터)과 번갈아 실행해 긴 멈춤을 없앤다.  삼색 표시: 흰색(미방문) / 회색(방문했으나 자식 미처리) / 검정(자식까지 처리).
// 불변식: "검정 객체는 흰 객체를 직접 가리키지 않는다".  뮤테이터가 검정 객체에 흰 객체 참조를 쓰면 그 흰 객체는 영영 처리되지 않아 살아있는데 회수된다.
// 쓰기 장벽(Dijkstra): 검정 객체에 참조를 쓸 때 대상 객체를 회색으로 칠한다
enum Color { WHITE, GRAY, BLACK };
struct Obj { std::vector<int> refs; Color c = WHITE; };
struct GC {
    std::vector<Obj> o; std::vector<int> gray; bool barrier;
    explicit GC(bool b) : barrier(b) {}
    void shade(int i) { if (o[i].c == WHITE) { o[i].c = GRAY; gray.push_back(i); } }
    bool step() {                                                   // 회색 객체 하나를 처리하는 작은 작업
        if (gray.empty()) return false;
        int i = gray.back(); gray.pop_back();
        for (int c : o[i].refs) shade(c);
        o[i].c = BLACK; return true;
    }
    void writeRef(int from, int to) {
        o[from].refs.push_back(to);
        if (barrier && o[from].c == BLACK) shade(to);               // 쓰기 장벽
    }
};

bool lostObject(bool barrier) {
    GC gc(barrier);
    gc.o.resize(3);                                                 // 0 = 루트 객체, 1 = A, 2 = B (A 가 B 를 가리킴)
    gc.o[0].refs = {1}; gc.o[1].refs = {2};
    gc.shade(0);
    gc.step();                                                      // 루트 처리: 1 이 회색, 루트는 검정
    // 뮤테이터: 이미 검정인 루트에 B 로 가는 새 참조를 쓰고, A -> B 참조를 지운다 (B 는 여전히 루트에서 닿는다)
    gc.writeRef(0, 2);
    gc.o[1].refs.clear();
    while (gc.step()) {}                                            // 수집 마무리
    return gc.o[2].c == WHITE;                                      // B 가 표시되지 않았다 = 살아있는 객체가 회수 대상이 됨
}

int main() {
    assert(lostObject(false));                                      // 장벽 없음: B 가 흰색으로 남아 잘못 회수된다
    assert(!lostObject(true));                                      // 장벽 있음: B 는 보존된다
    std::cout << "IncrementalGC: write barrier prevents losing a live object during incremental marking." << std::endl;
    return 0;
}
// Time Complexity: 조각당 O(1) 작업, 전체 O(힙)
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
#include <iostream>
#include <cstdint>
#include <list>
#include <set>
#include <vector>
#include <cassert>

// 캐시 미스의 3C 분류:
//  Compulsory(강제): 처음 접근하는 라인 (캐시가 아무리 커도 발생)
//  Capacity(용량): 작업 집합이 캐시보다 커서 (같은 크기의 완전 연관 캐시도 미스)
//  Conflict(충돌): 여러 라인이 같은 세트에 몰려 (완전 연관 캐시라면 적중했을 것)
struct LRU {
    size_t sets, ways; std::vector<std::list<uint64_t>> s;
    LRU(size_t numLines, size_t w) : sets(numLines / w), ways(w), s(numLines / w) {}
    bool access(uint64_t line) {
        auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); return true; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); return false;
    }
};
struct Result { long compulsory = 0, capacity = 0, conflict = 0; };
Result classify(size_t numLines, size_t ways, const std::vector<uint64_t>& trace) {
    LRU real(numLines, ways), full(numLines, numLines);           // 실제 캐시 vs 같은 크기의 완전 연관 캐시
    std::set<uint64_t> seen; Result r;
    for (uint64_t line : trace) {
        bool hit = real.access(line), fullHit = full.access(line);
        if (!hit) { if (!seen.count(line)) r.compulsory++; else if (!fullHit) r.capacity++; else r.conflict++; }
        seen.insert(line);
    }
    return r;
}

int main() {
    const size_t numLines = 64;                                    // 64 라인 캐시
    std::vector<uint64_t> trace;                                   // 라인 0, 64, 128, 192 를 반복: 직접 사상(1-way)이면 모두 같은 세트(번호 % 64 == 0)
    for (int rep = 0; rep < 50; rep++) for (int k = 0; k < 4; k++) trace.push_back(64ULL * k);
    Result direct = classify(numLines, 1, trace), assoc = classify(numLines, 4, trace);
    assert(direct.compulsory == 4 && direct.capacity == 0 && direct.conflict > 150);   // 라인 4개뿐인데 전부 충돌 미스
    assert(assoc.conflict == 0 && assoc.compulsory == 4);          // 4-way 면 충돌이 사라지고 강제 미스만 남는다
    std::vector<uint64_t> big; for (int rep = 0; rep < 3; rep++) for (uint64_t l = 0; l < 128; l++) big.push_back(l);   // 128 라인을 순환: 용량 초과
    Result cap = classify(numLines, 8, big);
    assert(cap.capacity > 0 && cap.compulsory == 128);             // 완전 연관이어도 미스 -> 용량 미스
    std::cout << "direct-mapped: conflict=" << direct.conflict << "; 4-way: conflict=" << assoc.conflict << "; oversized set: capacity=" << cap.capacity << std::endl;
    return 0;
}
// Time Complexity: O(trace · ways)
// Space Complexity: O(라인 수)
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
#include <iostream>
#include <cstdint>
#include <cassert>

// 가상 주소(x86-64, 4단계 페이징): 64비트 중 하위 48비트만 쓰고 [47:0] 을 9+9+9+9+12 비트로 나눈다.
//   [47:39] PML4 인덱스  [38:30] PDPT 인덱스  [29:21] PD 인덱스  [20:12] PT 인덱스  [11:0] 페이지 내 오프셋(4KB)
// 상위 16비트는 비트 47 의 복사여야 하는 "정규(canonical) 주소" 만 유효하다: 낮은 절반은 사용자, 높은 절반은 커널
struct Split { unsigned pml4, pdpt, pd, pt, offset; };
Split split(uint64_t va) { return {unsigned(va >> 39 & 0x1ff), unsigned(va >> 30 & 0x1ff), unsigned(va >> 21 & 0x1ff), unsigned(va >> 12 & 0x1ff), unsigned(va & 0xfff)}; }
uint64_t compose(const Split& s) {
    uint64_t va = (uint64_t)s.pml4 << 39 | (uint64_t)s.pdpt << 30 | (uint64_t)s.pd << 21 | (uint64_t)s.pt << 12 | s.offset;
    if (va >> 47 & 1) va |= 0xffff000000000000ULL;                      // 부호 확장 (정규 주소)
    return va;
}
bool canonical(uint64_t va) { uint64_t top = va >> 47; return top == 0 || top == 0x1ffff; }

int main() {
    uint64_t va = 0x00007f1234567abcULL;
    Split s = split(va);
    assert(s.offset == 0xabc && s.pt == 0x167 && s.pd == 0x1a2 && s.pdpt == 0x48 && s.pml4 == 0xfe);
    assert(compose(s) == va);                                            // 쪼갠 뒤 다시 합치면 원래 주소
    assert(canonical(va) && canonical(0xffff800000000000ULL));           // 사용자 영역 끝, 커널 영역 시작
    assert(!canonical(0x0000800000000000ULL) && !canonical(0x1234000000000000ULL));
    int local; assert(canonical((uint64_t)&local) && (uint64_t)&local < 0x0000800000000000ULL);   // 사용자 포인터는 낮은 절반
    std::cout << "VirtualAddress: 0x" << std::hex << va << " -> pml4=" << s.pml4 << " pdpt=" << s.pdpt << " pd=" << s.pd << " pt=" << s.pt << " off=" << s.offset << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PhysicalAddress()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 물리 주소: 실제 RAM 의 번호.  물리 메모리는 4KB "프레임" 으로 나뉘고, 운영체제는 프레임 비트맵(또는 버디 할당기)으로 빈 프레임을 관리한다.
// 물리 주소 = 프레임 번호 << 12 | 페이지 내 오프셋.  여러 프로세스가 같은 프레임을 공유할 수 있어(공유 라이브러리, CoW) 프레임마다 참조 횟수를 둔다
class FrameAllocator {
    std::vector<int> refs;                                              // 프레임별 참조 횟수 (0 = 비어 있음)
public:
    explicit FrameAllocator(size_t frames) : refs(frames, 0) {}
    long alloc() { for (size_t i = 0; i < refs.size(); i++) if (refs[i] == 0) { refs[i] = 1; return i; } return -1; }
    void share(size_t f) { refs[f]++; }
    void release(size_t f) { assert(refs[f] > 0); refs[f]--; }
    size_t freeFrames() const { size_t c = 0; for (int r : refs) c += r == 0; return c; }
    static uint64_t physAddr(size_t frame, unsigned offset) { return (uint64_t)frame << 12 | offset; }
};

int main() {
    FrameAllocator fa(4);                                                // 16KB 짜리 작은 RAM
    long f0 = fa.alloc(), f1 = fa.alloc();
    assert(f0 == 0 && f1 == 1 && fa.freeFrames() == 2);
    assert(FrameAllocator::physAddr(f1, 0x234) == 0x1234);
    fa.share(f0);                                                        // 두 프로세스가 프레임 0 을 공유 (참조 2)
    fa.release(f0);
    assert(fa.freeFrames() == 2);                                        // 아직 한 쪽이 쓰는 중이라 반환되지 않는다
    fa.release(f0);
    assert(fa.freeFrames() == 3);                                        // 마지막 참조가 사라져야 프레임이 비워진다
    assert(fa.alloc() == 0);                                             // 재사용
    fa.alloc(); fa.alloc();
    assert(fa.alloc() == -1);                                            // 물리 메모리 고갈
    std::cout << "PhysicalAddress: frame accounting verified." << std::endl;
    return 0;
}
// Time Complexity: 할당 O(프레임 수) (비트맵 + 힌트로 O(1) 가능)
// Space Complexity: O(프레임 수)
```
## AddressTranslation()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 주소 변환(MMU): 가상 주소를 (페이지 번호, 오프셋) 으로 나누고, 페이지 테이블 항목(PTE)에서 프레임 번호를 찾아 (프레임 번호 << 12 | 오프셋) 을 만든다.
// PTE 에는 present(메모리에 있음), writable, user 비트가 있고, 위반하면 CPU 가 페이지 폴트(예외)를 일으킨다
struct PTE { bool present = false, writable = false, user = false; uint32_t frame = 0; };
enum Status { OK, NOT_PRESENT, PROTECTION };
struct Result { Status st; uint64_t pa; };

Result translate(const std::vector<PTE>& table, uint64_t va, bool write, bool userMode) {
    uint64_t page = va >> 12, off = va & 0xfff;
    if (page >= table.size() || !table[page].present) return {NOT_PRESENT, 0};
    const PTE& e = table[page];
    if ((write && !e.writable) || (userMode && !e.user)) return {PROTECTION, 0};
    return {OK, (uint64_t)e.frame << 12 | off};
}

int main() {
    std::vector<PTE> pt(16);
    pt[3] = {true, true, true, 7};                                       // 페이지 3 -> 프레임 7 (읽기/쓰기, 사용자)
    pt[4] = {true, false, true, 9};                                      // 페이지 4 -> 프레임 9 (읽기 전용)
    pt[5] = {true, true, false, 2};                                      // 페이지 5 -> 프레임 2 (커널 전용)
    auto r = translate(pt, 3 * 4096 + 0x123, false, true);
    assert(r.st == OK && r.pa == 7 * 4096 + 0x123);                      // 오프셋은 그대로, 페이지 번호만 프레임 번호로 바뀐다
    assert(translate(pt, 4 * 4096, true, true).st == PROTECTION);        // 읽기 전용 페이지에 쓰기
    assert(translate(pt, 4 * 4096, false, true).st == OK);
    assert(translate(pt, 5 * 4096, false, true).st == PROTECTION);       // 사용자 모드에서 커널 페이지 접근
    assert(translate(pt, 5 * 4096, false, false).st == OK);
    assert(translate(pt, 9 * 4096, false, true).st == NOT_PRESENT);      // 매핑되지 않은 페이지 -> 페이지 폴트
    std::cout << "AddressTranslation: 0x" << std::hex << (3 * 4096 + 0x123) << " -> 0x" << r.pa << std::endl;
    return 0;
}
// Time Complexity: O(1) (한 단계 테이블)
// Space Complexity: O(페이지 수)
```
## Paging()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <set>
#include <cassert>

// 페이징: 메모리를 같은 크기(4KB)의 페이지로 나눠 어디에나 배치할 수 있게 한다 -> 외부 단편화가 없다.  대신 마지막 페이지의 낭비(내부 단편화, 평균 반 페이지)가 생긴다.
// 문제: 32비트 주소 공간의 평면 페이지 테이블은 2^20 항목 x 4B = 4MB — 프로세스마다 이만큼 필요하다.
// 해법: 다단계 테이블 — 실제로 쓰는 영역의 테이블만 만든다 (희소한 주소 공간에 매우 유리)
int main() {
    const uint64_t PAGE = 4096;
    auto pages = [&](uint64_t bytes) { return (bytes + PAGE - 1) / PAGE; };
    assert(pages(1) == 1 && pages(4096) == 1 && pages(4097) == 2);
    uint64_t request = 10000, waste = pages(request) * PAGE - request;   // 3페이지 = 12288 -> 2288 바이트 낭비
    assert(waste == 2288);

    uint64_t flat = (1ULL << 20) * 4;                                     // 평면 테이블: 4MB
    assert(flat == 4u << 20);
    // 2단계(디렉터리 1024 x 테이블 1024): 프로세스가 코드(0x08048000), 힙(0x09000000), 스택(0xBFFFF000) 주변만 쓴다
    uint64_t used[] = {0x08048000, 0x09000000, 0xBFFFF000};
    std::set<uint64_t> directoryIndexes; for (uint64_t va : used) directoryIndexes.insert(va >> 22);
    uint64_t twoLevel = (1 + directoryIndexes.size()) * PAGE;             // 디렉터리 1페이지 + 사용 중인 페이지 테이블들
    assert(directoryIndexes.size() == 3 && twoLevel == 4 * PAGE);         // 16KB
    assert(flat / twoLevel == 256);                                       // 평면 테이블의 1/256
    std::cout << "Paging: flat page table " << flat / 1024 << " KB vs two-level " << twoLevel / 1024 << " KB; internal fragmentation of 10000 B request = " << waste << " B" << std::endl;
    return 0;
}
// Time Complexity: O(1) 계산
// Space Complexity: 다단계 테이블 O(사용 영역)
```
## PageTable()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <memory>
#include <cassert>

// 4단계 페이지 테이블: 각 단계는 512 개 항목의 배열이고, 하위 단계 테이블이 필요할 때만 만든다 (기수 트리).
// 변환은 인덱스 4번으로 4개 테이블을 차례로 따라가는 것 (그래서 TLB 가 필요하다).  연속한 페이지들은 상위 테이블을 공유한다
struct Table { std::unique_ptr<Table> next[512]; int64_t frame[512]; Table() { for (auto& f : frame) f = -1; } };
class PageTable {
    Table root; int nodes = 1;
    static unsigned idx(uint64_t va, int level) { return va >> (12 + 9 * level) & 0x1ff; }       // level 3 = PML4 ... 0 = PT
public:
    void map(uint64_t va, int64_t frame) {
        Table* t = &root;
        for (int lv = 3; lv > 0; lv--) { auto& n = t->next[idx(va, lv)]; if (!n) { n.reset(new Table()); nodes++; } t = n.get(); }
        t->frame[idx(va, 0)] = frame;
    }
    int64_t translate(uint64_t va) const {
        const Table* t = &root;
        for (int lv = 3; lv > 0; lv--) { t = t->next[idx(va, lv)].get(); if (!t) return -1; }
        int64_t f = t->frame[idx(va, 0)];
        return f < 0 ? -1 : (f << 12 | (va & 0xfff));
    }
    void unmap(uint64_t va) {
        Table* t = &root;
        for (int lv = 3; lv > 0; lv--) { t = t->next[idx(va, lv)].get(); if (!t) return; }
        t->frame[idx(va, 0)] = -1;
    }
    int nodeCount() const { return nodes; }
};

int main() {
    PageTable pt;
    pt.map(0x0000000000400000ULL, 11);                                   // 코드
    assert(pt.nodeCount() == 4);                                         // 루트 + PDPT + PD + PT
    pt.map(0x0000000000401000ULL, 12);                                   // 바로 다음 페이지: 같은 PT 를 공유 -> 노드 추가 없음
    assert(pt.nodeCount() == 4);
    pt.map(0x00007ffffffff000ULL, 99);                                   // 스택 근처: 완전히 다른 가지 -> 노드 3개 추가
    assert(pt.nodeCount() == 7);
    assert(pt.translate(0x0000000000400123ULL) == (11LL << 12 | 0x123));
    assert(pt.translate(0x00007ffffffff008ULL) == (99LL << 12 | 0x8));
    assert(pt.translate(0x0000000000500000ULL) == -1);                   // 매핑 없음
    pt.unmap(0x0000000000400000ULL);
    assert(pt.translate(0x0000000000400123ULL) == -1 && pt.translate(0x0000000000401000ULL) == (12LL << 12));
    std::cout << "PageTable: 3 mappings use " << pt.nodeCount() << " table pages (flat table would need 2^36 entries)" << std::endl;
    return 0;
}
// Time Complexity: 변환 O(4) = O(1), 매핑 O(4)
// Space Complexity: O(매핑된 영역에 비례하는 테이블 수)
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
#include <iostream>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <cassert>
#if defined(__linux__)
#include <unistd.h>
#endif

// ASLR(주소 공간 배치 무작위화): 프로세스를 시작할 때마다 스택·힙·라이브러리(·PIE 실행 파일)의 위치를 무작위로 옮겨, 공격자가 목표 주소를 미리 알 수 없게 한다.
// 확인: 자기 자신을 두 번 실행(popen)해 스택 주소를 비교한다.  /proc/sys/kernel/randomize_va_space: 0 = 끔, 1 = 스택·mmap, 2 = 힙 포함 전체
int main(int argc, char** argv) {
#if defined(__linux__)
    if (argc == 2 && std::string(argv[1]) == "child") { int local; std::printf("%lx\n", (unsigned long)&local); return 0; }
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
    if (mode >= 1) assert(a != b);                                  // 실행마다 스택 주소가 달라진다 (우연히 같을 확률은 2^-22 이하)
    else assert(a == b);                                            // 끄면 항상 같다
    std::cout << "ASLR (mode " << mode << "): run1 stack=" << a.substr(0, a.size() - 1) << " run2 stack=" << b.substr(0, b.size() - 1) << std::endl;
#else
    (void)argc; (void)argv;
    std::cout << "ASLR: Linux-only demonstration" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
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
#include <iostream>
#include <array>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <cassert>

// 버퍼 오버플로: 버퍼 크기를 넘겨 인접한 메모리를 덮어쓴다.  탐지: 할당 앞뒤에 "레드존" 을 두고 특정 값을 채워 두었다가 해제할 때(또는 접근할 때) 값이 바뀌었는지 본다.
// 안전한 C++: std::array::at / vector::at 의 범위 검사, 길이를 지정하는 복사 함수
class GuardedBuffer {
    static const size_t RZ = 8; std::vector<uint8_t> mem; size_t n;
public:
    explicit GuardedBuffer(size_t size) : mem(size + 2 * RZ, 0xFE), n(size) { std::memset(&mem[RZ], 0, size); }
    uint8_t* data() { return &mem[RZ]; }                                 // 사용자 영역
    bool redzonesIntact() const {
        for (size_t i = 0; i < RZ; i++) if (mem[i] != 0xFE || mem[RZ + n + i] != 0xFE) return false;
        return true;
    }
};

int main() {
    GuardedBuffer b(16);
    std::memset(b.data(), 'A', 16);                                      // 정확히 16바이트: 정상
    assert(b.redzonesIntact());
    b.data()[16] = 'X';                                                  // 1바이트 초과 쓰기(off-by-one)
    assert(!b.redzonesIntact());                                         // 뒤쪽 레드존이 오염되어 탐지된다
    GuardedBuffer under(16); under.data()[-1] = 'Y';
    assert(!under.redzonesIntact());                                     // 앞쪽 언더플로도 탐지
    std::array<int, 4> arr = {1, 2, 3, 4};
    bool caught = false; try { arr.at(4) = 0; } catch (const std::out_of_range&) { caught = true; }
    assert(caught);                                                      // at() 은 범위를 검사한다
    char dst[8]; const char* src = "this string is too long";
    std::strncpy(dst, src, sizeof(dst) - 1); dst[sizeof(dst) - 1] = '\0';   // 길이를 제한한 복사 + 항상 널 종단
    assert(std::strlen(dst) == 7);
    std::cout << "BufferOverflow: off-by-one detected through red zones." << std::endl;
    return 0;
}
// Time Complexity: 검사 O(레드존 크기)
// Space Complexity: 할당당 2 · 레드존
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
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <string>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#endif

// 메모리 맵 파일: mmap 으로 파일을 프로세스 주소 공간에 붙이면 read/write 시스템 호출 없이 포인터로 파일 내용을 읽고 쓴다.
// 페이지를 처음 만질 때 커널이 파일에서 읽어 오고(페이지 캐시와 공유 -> 복사 1회 절약), MAP_SHARED 로 수정하면 파일에 반영된다
int main() {
#if defined(__unix__) || defined(__APPLE__)
    char path[] = "/tmp/ds_mmap_XXXXXX";
    int fd = mkstemp(path); assert(fd >= 0);
    const long ps = sysconf(_SC_PAGESIZE);
    std::string content(2 * ps, 'a'); content.replace(ps, 5, "HELLO");   // 두 페이지짜리 파일, 둘째 페이지 앞에 HELLO
    assert(write(fd, content.data(), content.size()) == (ssize_t)content.size());

    char* m = (char*)mmap(nullptr, content.size(), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    assert(m != MAP_FAILED);
    assert(m[0] == 'a' && std::memcmp(m + ps, "HELLO", 5) == 0);          // 포인터로 파일 내용을 읽는다
    std::memcpy(m + 10, "WORLD", 5);                                       // 메모리에 쓰면
    msync(m, content.size(), MS_SYNC);                                     // 파일에 반영한다
    char check[6] = {0}; assert(pread(fd, check, 5, 10) == 5);
    assert(std::strcmp(check, "WORLD") == 0);                              // read 로 읽은 파일 내용에서도 보인다
    munmap(m, content.size()); close(fd); unlink(path);
    std::cout << "MemoryMappedFile: file edited through a pointer and visible via pread." << std::endl;
#else
    std::cout << "MemoryMappedFile: POSIX-only demonstration (mmap)" << std::endl;
#endif
    return 0;
}
// Time Complexity: 접근 시 페이지 폴트 O(1) (캐시에 있으면 복사 없음)
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
#include <iostream>
#include <memory>
#include <string>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 쓰기 시 복사(CoW): 복사본을 만든다고 해 놓고 실제 복사는 "쓰는 순간" 까지 미룬다.  fork 직후 부모와 자식은 같은 물리 페이지를 읽기 전용으로 공유하다가,
// 어느 쪽이 쓰면 그 페이지만 복제한다 -> fork 가 빠르고 메모리를 아낀다.  사용자 공간에서도 문자열·버퍼에 같은 기법을 쓴다
class CowString {
    std::shared_ptr<std::string> data;
public:
    explicit CowString(std::string s) : data(std::make_shared<std::string>(std::move(s))) {}
    CowString(const CowString&) = default;                               // 복사는 포인터 공유 O(1)
    const std::string& str() const { return *data; }
    long owners() const { return data.use_count(); }
    void set(size_t i, char c) {
        if (data.use_count() > 1) data = std::make_shared<std::string>(*data);   // 공유 중이면 쓰기 직전에 분리(detach)
        (*data)[i] = c;
    }
};

int main() {
    CowString a("hello"); CowString b = a;
    assert(a.owners() == 2 && &a.str() == &b.str());                       // 복사 후에도 같은 버퍼 공유
    b.set(0, 'J');
    assert(a.str() == "hello" && b.str() == "Jello");                      // 쓰는 순간 분리 — 원본은 그대로
    assert(a.owners() == 1 && b.owners() == 1 && &a.str() != &b.str());
#if defined(__unix__) || defined(__APPLE__)
    int* p = (int*)mmap(nullptr, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    *p = 100;
    int fds[2]; assert(pipe(fds) == 0);
    pid_t pid = fork();
    if (pid == 0) {                                                        // 자식: 같은 가상 주소에 쓰면 자기 사본만 바뀐다
        *p = 999; int seen = *p; (void)!write(fds[1], &seen, sizeof seen); _exit(0);
    }
    int childSaw = 0; assert(read(fds[0], &childSaw, sizeof childSaw) == sizeof childSaw);
    wait(nullptr);
    assert(childSaw == 999 && *p == 100);                                  // 부모의 값은 그대로 (페이지가 복제됨)
    munmap(p, 4096);
#endif
    std::cout << "CopyOnWrite: writer got its own copy, original untouched." << std::endl;
    return 0;
}
// Time Complexity: 복사 O(1), 첫 쓰기 O(크기)
// Space Complexity: 쓰기가 일어나기 전까지 공유
```
## ZeroCopy()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <cassert>
#if defined(__linux__)
#include <fcntl.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

// 제로 카피: 데이터를 사용자 공간 버퍼로 옮기지 않고 커널 안에서 파일 -> 소켓/파일로 직접 전달한다.
//  read+write: 디스크 -> 커널 버퍼 -> (복사) 사용자 버퍼 -> (복사) 커널 버퍼 -> 목적지 : 사용자 공간 복사 2번, 문맥 전환 4번
//  sendfile  : 디스크 -> 커널 버퍼 -> 목적지                                          : 사용자 공간 복사 0번 (웹 서버가 정적 파일을 보내는 방식)
// 같은 아이디어를 사용자 공간에서도 쓴다: string_view 로 부분 문자열을 복사 없이 가리킨다
int main() {
    std::string src = "/tmp/ds_zc_src.bin", dst1 = "/tmp/ds_zc_dst1.bin", dst2 = "/tmp/ds_zc_dst2.bin";
    std::string payload(300000, 'x'); for (size_t i = 0; i < payload.size(); i += 97) payload[i] = char('a' + i % 26);
    { std::ofstream f(src, std::ios::binary); f << payload; }
#if defined(__linux__)
    long userCopied = 0;                                             // 사용자 공간 버퍼를 거친 바이트 수
    { int in = open(src.c_str(), O_RDONLY), out = open(dst1.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
      std::vector<char> buf(16384); ssize_t n;
      while ((n = read(in, buf.data(), buf.size())) > 0) { userCopied += n; (void)!write(out, buf.data(), n); }          // 전통적인 방식
      close(in); close(out); }
    long viaSendfile = 0, userCopied2 = 0;
    { int in = open(src.c_str(), O_RDONLY), out = open(dst2.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
      struct stat st; fstat(in, &st); off_t off = 0;
      while (off < st.st_size) { ssize_t n = sendfile(out, in, &off, st.st_size - off); if (n <= 0) break; viaSendfile += n; }   // 커널 안에서만 이동
      close(in); close(out); }
    auto slurp = [](const std::string& p) { std::ifstream f(p, std::ios::binary); std::ostringstream ss; ss << f.rdbuf(); return ss.str(); };
    assert(slurp(dst1) == payload && slurp(dst2) == payload);         // 결과는 동일
    assert(userCopied == (long)payload.size() && userCopied2 == 0 && viaSendfile == (long)payload.size());     // 사용자 공간 복사: 전체 vs 0
    std::remove(dst1.c_str()); std::remove(dst2.c_str());
#endif
    std::remove(src.c_str());
    std::string line = "key=value;other=thing";
    std::string_view v(line); auto eq = v.find('='); auto semi = v.find(';');
    std::string_view key = v.substr(0, eq), val = v.substr(eq + 1, semi - eq - 1);     // 복사 없이 같은 메모리를 가리킨다
    assert(key == "key" && val == "value" && key.data() == line.data());
    std::cout << "ZeroCopy: sendfile moved " << payload.size() << " bytes without a user-space buffer." << std::endl;
    return 0;
}
// Time Complexity: O(n) 이동, 사용자 공간 복사 0
// Space Complexity: O(1) 사용자 버퍼
```
# Part 14. 운영체제
## ProcessMemory()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// 프로세스 메모리 지도: 리눅스의 /proc/self/maps 는 프로세스의 가상 주소 영역(VMA)을 한 줄씩 보여 준다.
//   시작-끝  권한(rwxp)  오프셋  장치  inode  경로      예) 55d0c8a00000-55d0c8a21000 r-xp ... /path/a.out   ...  [heap]   ...  [stack]
// 코드는 r-xp, 읽기 전용 데이터는 r--p, 전역 변수는 rw-p, 스택은 [stack].  자기 변수의 주소가 어느 영역에 속하는지 확인할 수 있다
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
int global = 5;
void code() {}

int main() {
#if defined(__linux__)
    auto maps = readMaps();
    assert(!maps.empty());
    int local = 0; int* heap = new int(1);
    const Region *stack = find(maps, &local), *text = find(maps, (void*)&code), *data = find(maps, &global), *hp = find(maps, heap);
    assert(stack && stack->name == "[stack]" && stack->perms[0] == 'r' && stack->perms[1] == 'w' && stack->perms[2] == '-');   // 스택: 읽기+쓰기, 실행 불가
    assert(text && text->perms[2] == 'x' && text->perms[1] == '-');                   // 코드: 실행 가능, 쓰기 불가 (W^X)
    assert(data && data->perms[1] == 'w' && data->perms[2] == '-');                   // 전역 변수: 쓰기 가능, 실행 불가
    assert(hp && hp->perms[1] == 'w');                                                // 힙(brk 또는 mmap 영역)
    std::cout << "ProcessMemory: stack=" << stack->name << " text perms=" << text->perms << " data perms=" << data->perms << " heap region=" << (hp->name.empty() ? "[anon]" : hp->name) << std::endl;
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
#include <iostream>
#include <set>
#include <thread>
#include <mutex>
#include <vector>
#include <cassert>

// 스레드 지역 저장소(TLS): thread_local 변수는 스레드마다 별도의 복사본이 있다 -> 락 없이 스레드별 상태(errno, 난수 생성기 상태, 캐시)를 유지한다.
// 스레드가 시작할 때 초기화되고 끝날 때 소멸자가 불린다.  공유 변수와 달리 경쟁 상태가 없다
thread_local int counter = 100;
std::mutex mu; std::set<const void*> addresses; int ctors = 0, dtors = 0;
struct PerThread { PerThread() { std::lock_guard<std::mutex> g(mu); ctors++; } ~PerThread() { std::lock_guard<std::mutex> g(mu); dtors++; } };
thread_local PerThread tls;

int main() {
    counter = 1;                                                       // 메인 스레드의 사본만 바뀐다
    std::vector<std::thread> th; int results[4];
    for (int t = 0; t < 4; t++)
        th.emplace_back([&, t] {
            (void)tls;                                                  // 이 스레드의 tls 객체 생성
            assert(counter == 100);                                     // 각 스레드는 초기값 100 으로 시작 (메인의 1 과 무관)
            for (int i = 0; i < 1000; i++) counter++;                   // 락 없이 증가해도 경쟁 없음
            results[t] = counter;
            std::lock_guard<std::mutex> g(mu); addresses.insert(&counter);
        });
    for (auto& x : th) x.join();
    for (int t = 0; t < 4; t++) assert(results[t] == 1100);
    assert(counter == 1);                                               // 메인의 값은 영향 없음
    assert(addresses.size() == 4);                                      // 스레드마다 주소가 다르다
    assert(ctors == 4 && dtors == 4);                                   // 스레드 종료 시 소멸자 호출
    std::cout << "ThreadLocalStorage: 4 threads, 4 distinct copies, no locking." << std::endl;
    return 0;
}
// Time Complexity: 접근 O(1) (세그먼트 레지스터 기준 오프셋)
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
#include <iostream>
#include <numeric>
#include <set>
#include <vector>
#include <cassert>

// GPU 메모리: 32 스레드(워프)가 한 명령을 동시에 실행한다.
//  전역 메모리 병합(coalescing): 워프의 접근이 연속된 128바이트 구간에 모이면 메모리 트랜잭션이 1번, 흩어지면 구간 수만큼 늘어난다.
//  공유 메모리 뱅크 충돌: 32개 뱅크(4바이트 단위 주소 % 32) 중 같은 뱅크의 서로 다른 주소를 여러 스레드가 동시에 접근하면 직렬화된다.
int transactions(int stride) {                                       // 스레드 t 가 float[t * stride] 를 읽을 때 건드리는 128B 구간 수
    std::set<long> segs; for (int t = 0; t < 32; t++) segs.insert((long)t * stride * 4 / 128); return segs.size();
}
int bankConflictDegree(int stride) {                                 // 스레드 t 가 word[t * stride] 에 접근할 때 같은 뱅크에 몰리는 최대 스레드 수
    std::vector<int> perBank(32, 0); for (int t = 0; t < 32; t++) perBank[(t * stride) % 32]++;
    int mx = 0; for (int c : perBank) mx = std::max(mx, c); return mx;
}

int main() {
    assert(transactions(1) == 1 && transactions(2) == 2 && transactions(4) == 4 && transactions(32) == 32);   // 간격이 클수록 병합 실패
    assert(bankConflictDegree(1) == 1);                              // 연속 접근: 충돌 없음
    assert(bankConflictDegree(2) == 2 && bankConflictDegree(32) == 32);   // 2-way, 32-way 충돌
    assert(bankConflictDegree(33) == 1);                             // 32x32 타일의 한 줄에 패딩 1칸(폭 33)을 주면 열 접근도 충돌이 사라진다
    for (int s = 1; s <= 64; s++) assert(bankConflictDegree(s) == std::gcd(s, 32));   // 충돌 정도 = gcd(stride, 32)
    std::cout << "GPUMemory: stride-1 -> " << transactions(1) << " transaction; stride-32 -> " << transactions(32) << "; tile padding 33 removes the 32-way conflict" << std::endl;
    return 0;
}
// Time Complexity: O(32)
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
#include <iostream>
#include <cstdint>
#include <cassert>
#if defined(__linux__)
#include <sys/mman.h>
#endif

// 대형 페이지(2MB / 1GB): 페이지가 클수록 TLB 항목 하나가 덮는 범위(TLB reach)가 커져 TLB 미스와 페이지 테이블 크기가 줄어든다.
//   TLB reach = 항목 수 x 페이지 크기.   데이터베이스·JVM·HPC 처럼 큰 메모리를 쓰는 프로그램에서 수 %~수십 % 성능 향상.
// 단점: 페이지 단위 보호/스왑이 거칠어지고, 큰 연속 물리 메모리가 필요하며 내부 단편화가 커진다.  리눅스는 Transparent Huge Pages(THP)와 madvise(MADV_HUGEPAGE)를 제공
int main() {
    const uint64_t KB = 1024, MB = KB * 1024, GB = MB * 1024;
    const uint64_t entries = 64;
    assert(entries * 4 * KB == 256 * KB);                              // 4KB 페이지: 64 항목이 겨우 256KB 를 덮는다
    assert(entries * 2 * MB == 128 * MB);                              // 2MB 페이지: 512배
    assert(entries * 1 * GB == 64 * GB);
    assert(GB / (4 * KB) == 262144 && GB / (2 * MB) == 512);           // 1GB 를 매핑하는 데 필요한 페이지 항목 수: 262144 vs 512
    assert(GB / (4 * KB) * 8 == 2 * MB && GB / (2 * MB) * 8 == 4 * KB);   // 항목당 8바이트: 말단 테이블 2MB vs 4KB
#if defined(__linux__)
    size_t len = 4 * MB;
    void* p = mmap(nullptr, len + 2 * MB, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p != MAP_FAILED) {
        uintptr_t aligned = ((uintptr_t)p + 2 * MB - 1) & ~(uintptr_t)(2 * MB - 1);   // 2MB 경계로 정렬 (대형 페이지의 조건)
        int rc = madvise((void*)aligned, len, MADV_HUGEPAGE);             // 커널에 "대형 페이지를 써도 좋다" 고 알린다 (시스템 설정에 따라 무시될 수 있음)
        *(volatile char*)aligned = 1;
        std::cout << "HugePage: madvise(MADV_HUGEPAGE) returned " << rc << " (kernel may or may not back it with a huge page)" << std::endl;
        munmap(p, len + 2 * MB);
    }
#endif
    std::cout << "HugePage: TLB reach 4KB=" << entries * 4 * KB / KB << "KB, 2MB=" << entries * 2 * MB / MB << "MB, 1GB=" << entries * GB / GB << "GB" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 페이지 테이블 크기가 1/512 로 감소
```
## RDMA()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <map>
#include <stdexcept>
#include <vector>
#include <cassert>

// RDMA(원격 직접 메모리 접근): 네트워크 카드(NIC)가 원격 노드의 메모리를 상대 CPU 와 운영체제의 개입 없이 직접 읽고 쓴다 (InfiniBand, RoCE).  커널 우회·제로 카피로 지연이 마이크로초 수준.
// 흐름: (1) 메모리 영역을 NIC 에 등록(고정, pinned) -> rkey 발급 (2) rkey 와 원격 주소를 상대에게 전달 (3) RDMA_WRITE/READ 를 보내면 상대의 NIC 가 rkey·범위·권한을 검사하고 처리
// 아래는 verbs 의 핵심 의미만 흉내 낸 모델이다 (실제 API: ibv_reg_mr, ibv_post_send)
enum Access { LOCAL_WRITE = 1, REMOTE_READ = 2, REMOTE_WRITE = 4 };
struct Region { std::vector<uint8_t> mem; unsigned access; };
class Node {
    std::map<uint32_t, Region> mr; uint32_t nextKey = 0x100;
public:
    long cpuInvolvements = 0;                                        // 이 노드의 CPU 가 처리에 관여한 횟수 (RDMA 에서는 0)
    uint32_t registerRegion(size_t bytes, unsigned access) { mr[nextKey] = Region{std::vector<uint8_t>(bytes, 0), access}; return nextKey++; }
    uint8_t* local(uint32_t key) { return mr.at(key).mem.data(); }
    // 상대 NIC 가 수행하는 검사 (수신 노드의 CPU 는 호출되지 않는다)
    void nicWrite(uint32_t rkey, size_t off, const void* src, size_t n) {
        auto it = mr.find(rkey); if (it == mr.end()) throw std::runtime_error("invalid rkey");
        if (!(it->second.access & REMOTE_WRITE)) throw std::runtime_error("remote write not permitted");
        if (off + n > it->second.mem.size()) throw std::runtime_error("out of bounds");
        std::memcpy(&it->second.mem[off], src, n);
    }
    void nicRead(uint32_t rkey, size_t off, void* dst, size_t n) {
        auto it = mr.find(rkey); if (it == mr.end()) throw std::runtime_error("invalid rkey");
        if (!(it->second.access & REMOTE_READ)) throw std::runtime_error("remote read not permitted");
        if (off + n > it->second.mem.size()) throw std::runtime_error("out of bounds");
        std::memcpy(dst, &it->second.mem[off], n);
    }
};
template <class F> bool fails(F f) { try { f(); } catch (const std::runtime_error&) { return true; } return false; }

int main() {
    Node client, server;
    uint32_t rkey = server.registerRegion(64, REMOTE_READ | REMOTE_WRITE);
    uint32_t roKey = server.registerRegion(64, REMOTE_READ);
    const char msg[] = "hello rdma";
    server.nicWrite(rkey, 8, msg, sizeof msg);                        // 클라이언트가 서버 메모리에 직접 쓴다 (서버 CPU 는 코드를 실행하지 않는다)
    char back[16] = {0};
    server.nicRead(rkey, 8, back, sizeof msg);                         // 직접 읽어 온다
    assert(std::strcmp(back, "hello rdma") == 0 && server.cpuInvolvements == 0);
    assert(std::memcmp(server.local(rkey) + 8, msg, sizeof msg) == 0); // 서버의 메모리에 실제로 반영됨
    assert(fails([&] { server.nicWrite(0xdead, 0, msg, 4); }));        // 알 수 없는 rkey
    assert(fails([&] { server.nicWrite(roKey, 0, msg, 4); }));         // 읽기 전용으로 등록된 영역에 쓰기
    assert(fails([&] { server.nicWrite(rkey, 62, msg, 8); }));         // 범위 초과
    (void)client;
    std::cout << "RDMA: remote write/read completed without involving the target CPU; invalid access rejected by the NIC." << std::endl;
    return 0;
}
// Time Complexity: O(n) 복사 (NIC 가 DMA)
// Space Complexity: 등록된 영역(고정 메모리)
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
#include <iostream>
#include <cstdint>
#include <unordered_map>
#include <cassert>

// ZGC: 포인터 자체에 "색(color)" 메타데이터 비트를 넣고(colored pointers), 객체를 읽을 때마다 로드 장벽(load barrier)이 색을 검사한다.
// 객체를 이동(재배치)하는 동안에도 프로그램이 돌아가며, 오래된 포인터를 읽는 순간 장벽이 새 주소를 찾아 그 필드를 고쳐 쓴다(self-healing) -> 정지 시간이 힙 크기와 무관(밀리초 미만).
// 색 비트 하나(good color)를 전역으로 바꾸면 "모든 포인터가 낡은 것" 이 되고, 이후 각 포인터는 처음 읽힐 때 한 번씩만 느린 경로를 탄다
const uint64_t ADDR_MASK = (1ULL << 42) - 1, COLOR_SHIFT = 42;
uint64_t goodColor = 1;                                                     // 현재 유효한 색 (1 = 사이클 A, 2 = 사이클 B)
uint64_t colored(uint64_t addr, uint64_t color) { return addr | color << COLOR_SHIFT; }
uint64_t addrOf(uint64_t p) { return p & ADDR_MASK; }
uint64_t colorOf(uint64_t p) { return p >> COLOR_SHIFT; }

std::unordered_map<uint64_t, uint64_t> forwarding;                          // 재배치된 객체의 옛 주소 -> 새 주소
long slowPaths = 0, fastPaths = 0;
uint64_t loadBarrier(uint64_t* field) {
    uint64_t p = *field;
    if (colorOf(p) == goodColor) { fastPaths++; return addrOf(p); }         // 빠른 경로: 색이 맞으면 그대로
    slowPaths++;                                                             // 느린 경로: 새 주소를 찾아 자기 치유
    uint64_t a = addrOf(p); auto it = forwarding.find(a); if (it != forwarding.end()) a = it->second;
    *field = colored(a, goodColor);                                         // 필드를 올바른 주소·색으로 고쳐 쓴다
    return a;
}

int main() {
    uint64_t fieldA = colored(0x1000, goodColor), fieldB = colored(0x1000, goodColor);   // 같은 객체를 가리키는 포인터 두 개
    assert(loadBarrier(&fieldA) == 0x1000 && slowPaths == 0 && fastPaths == 1);
    // GC 가 0x1000 의 객체를 0x2000 으로 옮기고 전역 색을 바꾼다
    forwarding[0x1000] = 0x2000; goodColor = 2;
    assert(loadBarrier(&fieldA) == 0x2000 && slowPaths == 1);              // 낡은 포인터를 읽는 순간 새 주소를 얻는다
    assert(colorOf(fieldA) == goodColor && addrOf(fieldA) == 0x2000);       // 필드가 고쳐졌다 (self-healing)
    assert(loadBarrier(&fieldA) == 0x2000 && slowPaths == 1);              // 다음부터는 빠른 경로
    assert(loadBarrier(&fieldB) == 0x2000 && slowPaths == 2);              // 다른 낡은 포인터도 처음 읽을 때 한 번만 느린 경로
    std::cout << "ZGC: slow paths=" << slowPaths << ", fast paths=" << fastPaths << " (each stale pointer healed once)" << std::endl;
    return 0;
}
// Time Complexity: 빠른 경로 O(1) 비교, 느린 경로 O(1) 조회
// Space Complexity: 포인터 상위 비트 + 전달 테이블
```
## ShenandoahGC()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <vector>
#include <cassert>

// Shenandoah: 모든 객체 앞에 Brooks 전달 포인터(forwarding pointer)를 둔다.  평소에는 자기 자신을 가리키고, 객체가 이동하면 새 사본을 가리킨다.
// 프로그램은 항상 "전달 포인터를 한 번 따라간 뒤" 읽고 쓰므로, GC 가 동시에 객체를 옮겨도 읽는 쪽과 쓰는 쪽이 같은 사본을 보게 된다.
// 이동은 CAS 로 전달 포인터를 바꾸는 쪽이 이기게 하여 여러 스레드가 동시에 같은 객체를 옮기려 해도 사본이 하나만 유효하다
struct Obj { std::atomic<Obj*> fwd; int value; Obj(int v) : fwd(this), value(v) {} };
Obj* resolve(Obj* o) { return o->fwd.load(); }                              // 모든 접근의 첫 단계
int read(Obj* o) { return resolve(o)->value; }
void write(Obj* o, int v) { resolve(o)->value = v; }
Obj* evacuate(Obj* o, std::vector<Obj*>& heap) {                            // 사본을 만들고, 전달 포인터 CAS 에 성공한 쪽만 채택
    Obj* copy = new Obj(o->value);
    Obj* expected = o;
    if (o->fwd.compare_exchange_strong(expected, copy)) { heap.push_back(copy); return copy; }         // 내가 이겼다
    delete copy; return expected;                                              // 다른 스레드가 먼저 옮겼다: 그 사본을 사용 (내 사본은 버림)
}

int main() {
    std::vector<Obj*> heap; Obj* a = new Obj(10); heap.push_back(a);
    assert(read(a) == 10 && resolve(a) == a);                                 // 이동 전: 전달 포인터는 자기 자신
    Obj* moved = evacuate(a, heap);                                           // GC 가 객체를 이동
    assert(resolve(a) == moved && moved != a);
    write(a, 99);                                                             // 뮤테이터는 옛 주소 a 로 쓰지만 전달 포인터를 따라 새 사본에 쓰인다
    assert(moved->value == 99 && read(a) == 99);                              // 새 사본에 반영되고, 옛 주소로 읽어도 최신 값
    assert(a->value == 10);                                                   // 옛 사본은 더 이상 쓰이지 않는다 (낡은 값)
    Obj* second = evacuate(a, heap);                                          // 두 번째 이동 시도 -> 이미 이동됨: 기존 사본을 돌려준다
    assert(second == moved && resolve(a) == moved);
    for (Obj* o : heap) delete o;                                             // 힙의 모든 사본 해제
    std::cout << "ShenandoahGC: accesses through the forwarding pointer saw the relocated copy; duplicate evacuation lost the CAS." << std::endl;
    return 0;
}
// Time Complexity: 접근마다 포인터 한 번 더 (간접 참조 비용)
// Space Complexity: 객체당 포인터 하나
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
#include <iostream>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 탈출 분석(escape analysis): 객체가 만들어진 함수 밖으로 "빠져나가는가" 를 컴파일 시점에 분석한다.  빠져나가지 않으면 힙 대신 스택에 두거나(스택 할당),
// 필드를 지역 변수로 쪼개 객체 자체를 없앨 수 있다(스칼라 치환) -> GC 부담 제거.  JVM(HotSpot), Go, V8 이 사용
// 단순화한 중간 표현에서 분석을 직접 구현한다.  탈출 조건: (1) 반환됨 (2) 전역/미지의 함수에 전달됨 (3) 이미 탈출하는 객체의 필드에 저장됨
enum Op { NEW, MOVE, STORE, RETURN, PASS };
struct Stmt { Op op; std::string a, b; };     // NEW a: a = new / MOVE a, b: a = b / STORE a, b: a.f = b / RETURN a / PASS a: 미지의 함수에 인자로 전달

std::set<std::string> escaped(const std::vector<Stmt>& prog) {
    std::set<std::string> esc;
    for (auto& s : prog) if (s.op == RETURN || s.op == PASS) esc.insert(s.a);
    for (bool changed = true; changed;) {                                    // 고정점 반복: 탈출이 별칭·필드를 통해 전파된다
        changed = false;
        for (auto& s : prog) {
            if (s.op == MOVE && esc.count(s.a) && esc.insert(s.b).second) changed = true;      // a = b 에서 a 가 탈출하면 b 도 탈출
            if (s.op == MOVE && esc.count(s.b) && esc.insert(s.a).second) changed = true;      // 별칭이므로 양방향
            if (s.op == STORE && esc.count(s.a) && esc.insert(s.b).second) changed = true;      // 탈출하는 객체의 필드에 저장된 값도 탈출
        }
    }
    return esc;
}

int main() {
    using V = std::vector<Stmt>;
    // 1) p 는 함수 안에서만 쓰인다 -> 탈출 없음 -> 스택/스칼라 치환 가능
    assert(escaped(V{{NEW, "p", ""}, {STORE, "p", "p"}}).empty());
    // 2) 반환되는 객체는 탈출
    assert((escaped(V{{NEW, "p", ""}, {RETURN, "p", ""}}) == std::set<std::string>{"p"}));
    // 3) q 를 탈출하는 p 의 필드에 저장 -> q 도 탈출
    assert((escaped(V{{NEW, "q", ""}, {NEW, "p", ""}, {STORE, "p", "q"}, {RETURN, "p", ""}}) == std::set<std::string>{"p", "q"}));
    // 4) 둘 다 지역에서만 연결되면 탈출 없음
    assert(escaped(V{{NEW, "q", ""}, {NEW, "p", ""}, {STORE, "p", "q"}}).empty());
    // 5) 별칭을 통한 탈출: r = p; return r;
    assert((escaped(V{{NEW, "p", ""}, {MOVE, "r", "p"}, {RETURN, "r", ""}}) == std::set<std::string>{"p", "r"}));
    // 6) 미지의 함수에 전달하면 탈출
    assert((escaped(V{{NEW, "p", ""}, {PASS, "p", ""}}) == std::set<std::string>{"p"}));
    std::cout << "EscapeAnalysis: classified 6 programs; non-escaping objects can live on the stack." << std::endl;
    return 0;
}
// Time Complexity: O(문장 수 · 반복)
// Space Complexity: O(변수 수)
```
## OwnershipTypeSystem()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <cassert>

// 소유권 타입 시스템(Rust): (1) 값의 소유자는 하나  (2) 소유권이 이동(move)하면 원래 변수는 사용 불가  (3) 빌림(borrow) 규칙: 읽기 참조는 여러 개 OR 쓰기 참조는 정확히 한 개 (동시에는 불가)
// -> 데이터 경쟁과 댕글링 참조를 컴파일 시점에 막는다.  Rust 는 컴파일러가 하지만, 여기서는 같은 규칙을 런타임 검사로 흉내 내 규칙의 의미를 확인한다 (RefCell 과 비슷)
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

int main() {
    Owned<std::string> a(std::string("data"));
    { auto r1 = a.borrow(); auto r2 = a.borrow(); assert(r1.get() == "data" && r2.get() == "data"); }     // 읽기 참조는 여러 개 가능
    { auto w = a.borrowMut(); w.getMut() += "!"; }                                                            // 쓰기 참조는 하나
    assert(a.borrow().get() == "data!");
    { auto r = a.borrow(); assert(throws([&] { a.borrowMut(); })); }                                         // 읽는 중에 쓰기 참조 -> 위반
    { auto w = a.borrowMut(); assert(throws([&] { a.borrow(); })); assert(throws([&] { a.borrowMut(); })); } // 쓰는 중에는 어떤 참조도 불가
    assert(!throws([&] { a.borrowMut(); }));                                                                  // 참조가 끝나면 다시 가능
    Owned<std::string> b = std::move(a);                                                                      // 소유권 이동
    assert(a.moved() && !b.moved() && throws([&] { a.borrow(); }));                                           // 이동 후 원본 사용은 오류
    std::cout << "OwnershipTypeSystem: aliasing XOR mutation enforced; use after move rejected." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
// Space Complexity: O(1)
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
#include <iostream>
#include <atomic>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <unordered_map>
#include <vector>
#include <cassert>

// 소프트웨어 트랜잭셔널 메모리(STM, TL2 방식): 락 대신 트랜잭션으로 공유 변수를 다룬다.  읽기는 낙관적으로(락 없이) 하고 쓰기는 버퍼에 모았다가,
// 커밋할 때 "내가 읽은 변수들이 시작 이후 바뀌지 않았는가"(버전 검증)를 확인한다.  충돌했으면 버리고 처음부터 재시도 — 교착 상태가 없고 조합이 쉽다
struct TVar { std::atomic<int> value{0}; std::atomic<long> version{0}; };       // 낙관적 읽기와 커밋 쓰기가 겹칠 수 있으므로 값도 원자 변수로 둔다 (겹침은 버전 검사로 걸러낸다)
std::atomic<long> globalClock(0); std::mutex commitLock;

struct Tx {
    long start = globalClock.load();
    std::unordered_map<TVar*, long> readSet;                         // 읽은 변수 -> 읽은 시점의 버전
    std::unordered_map<TVar*, int> writeBuf;
    int read(TVar& v) {
        auto w = writeBuf.find(&v); if (w != writeBuf.end()) return w->second;     // 자기 쓰기 우선
        long ver = v.version.load(); int val = v.value;
        if (v.version.load() != ver || ver > start) throw std::runtime_error("conflict");   // 읽는 도중이거나 시작 후에 바뀐 값
        readSet[&v] = ver; return val;
    }
    void write(TVar& v, int x) { writeBuf[&v] = x; }
    void commit() {
        std::lock_guard<std::mutex> g(commitLock);
        for (auto& r : readSet) if (r.first->version.load() != r.second) throw std::runtime_error("conflict");   // 읽기 집합 검증
        long wv = globalClock.fetch_add(1) + 1;
        for (auto& w : writeBuf) { w.first->value = w.second; w.first->version.store(wv); }                    // 쓰기 반영
    }
};
template <class F> void atomically(F f) { for (;;) { Tx tx; try { f(tx); tx.commit(); return; } catch (const std::runtime_error&) {} } }

int main() {
    // 결정적 충돌: tx1 이 x 를 읽은 뒤 tx2 가 x 를 바꿔 커밋하면 tx1 의 커밋은 실패해야 한다
    TVar x; x.value = 5;
    Tx tx1; int seen = tx1.read(x);
    atomically([&](Tx& t) { t.write(x, t.read(x) + 1); });
    tx1.write(x, seen + 100);
    bool conflicted = false; try { tx1.commit(); } catch (const std::runtime_error&) { conflicted = true; }
    assert(conflicted && x.value == 6);                              // tx1 의 쓰기는 반영되지 않았다 (낡은 읽기에 기반한 갱신 차단)

    // 여러 스레드가 두 계좌 사이에서 동시에 이체: 락 없이도 합계가 보존된다
    TVar a, b; a.value = 1000; b.value = 1000;
    std::vector<std::thread> th;
    for (int t = 0; t < 4; t++) th.emplace_back([&, t] { for (int i = 0; i < 2000; i++) atomically([&](Tx& tx) { int amount = 1 + (i + t) % 5; tx.write(a, tx.read(a) - amount); tx.write(b, tx.read(b) + amount); }); });
    for (auto& s : th) s.join();
    assert(a.value + b.value == 2000);                               // 불변식 유지
    assert(a.value != 1000);                                         // 이체가 실제로 일어났다
    std::cout << "TransactionalMemory: stale transaction aborted; 8000 concurrent transfers kept the total at " << a.value + b.value << std::endl;
    return 0;
}
// Time Complexity: 트랜잭션당 O(읽기 + 쓰기 집합), 충돌 시 재시도
// Space Complexity: O(읽기·쓰기 집합)
```
## CapabilityPointer()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <stdexcept>
#include <vector>
#include <cassert>

// 케이퍼빌리티 포인터(CHERI): 포인터를 "주소" 만이 아니라 (기준 주소 base, 길이 length, 권한 perms) 를 함께 담은 불변 토큰으로 만든다.
// 접근할 때 하드웨어가 범위와 권한을 검사한다.  케이퍼빌리티는 "축소만" 가능하다(단조성): 더 좁은 범위·더 적은 권한은 만들 수 있지만 넓히거나 권한을 추가할 수는 없다 -> 최소 권한 원칙을 하드웨어가 강제
enum Perm : unsigned { LOAD = 1, STORE = 2 };
struct Cap {
    uint64_t base, length, addr; unsigned perms;
    Cap derive(uint64_t newBase, uint64_t newLen, unsigned newPerms) const {
        if (newBase < base || newBase + newLen > base + length) throw std::runtime_error("monotonicity: range would widen");
        if (newPerms & ~perms) throw std::runtime_error("monotonicity: permissions would increase");
        return {newBase, newLen, newBase, newPerms};
    }
};
class Memory {
    std::vector<uint8_t> bytes;
public:
    explicit Memory(size_t n) : bytes(n, 0) {}
    uint8_t load(const Cap& c, uint64_t off) const { check(c, off, LOAD); return bytes[c.base + off]; }
    void store(const Cap& c, uint64_t off, uint8_t v) { check(c, off, STORE); bytes[c.base + off] = v; }
private:
    static void check(const Cap& c, uint64_t off, unsigned need) {
        if (off >= c.length) throw std::runtime_error("bounds violation");
        if (!(c.perms & need)) throw std::runtime_error("permission violation");
    }
};
template <class F> bool traps(F f) { try { f(); } catch (const std::runtime_error&) { return true; } return false; }

int main() {
    Memory mem(1024);
    Cap whole{0, 1024, 0, LOAD | STORE};
    Cap buf = whole.derive(100, 16, LOAD | STORE);                    // 16바이트 버퍼에 대한 케이퍼빌리티
    mem.store(buf, 15, 7); assert(mem.load(buf, 15) == 7);             // 범위 안: 정상
    assert(traps([&] { mem.store(buf, 16, 1); }));                     // 버퍼 오버플로: 1바이트만 넘어도 하드웨어가 거부
    Cap readOnly = buf.derive(100, 8, LOAD);                           // 더 좁고 더 약한 케이퍼빌리티는 만들 수 있다
    assert(mem.load(readOnly, 0) == 0 && traps([&] { mem.store(readOnly, 0, 1); }));   // 읽기 전용: 쓰기 거부
    assert(traps([&] { readOnly.derive(100, 8, LOAD | STORE); }));     // 권한을 되살릴 수 없다
    assert(traps([&] { buf.derive(100, 32, LOAD); }));                 // 범위를 넓힐 수 없다
    assert(traps([&] { buf.derive(90, 8, LOAD); }));                   // 범위 밖으로 이동할 수 없다
    std::cout << "CapabilityPointer: bounds and permissions enforced; derivation can only shrink." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
// Space Complexity: 포인터당 base·length·perms 추가 (CHERI 는 128비트 포인터)
```
## CHERIArchitecture()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <cassert>

// CHERI 의 핵심 아이디어 두 가지: (1) 케이퍼빌리티는 16바이트로 정렬된 메모리에 저장되고, 메모리 16바이트마다 숨은 "태그 비트" 가 붙는다.
// (2) 케이퍼빌리티를 저장하면 태그가 1 이 되지만, 같은 16바이트에 일반 데이터를 쓰면 태그가 자동으로 0 이 된다 -> 바이트를 조작해 케이퍼빌리티를 위조할 수 없다.
// 태그가 꺼진 케이퍼빌리티는 사용하려 하면 예외.  이 두 가지로 "포인터 위조 불가" 가 하드웨어 수준에서 성립한다
const size_t GRANULE = 16;
struct Cap { uint64_t base, length; bool tag; };
class TaggedMemory {
    std::vector<uint8_t> bytes; std::vector<bool> tags; std::vector<Cap> capStore;       // 케이퍼빌리티 값은 별도 저장 (16B 칸마다 하나)
public:
    explicit TaggedMemory(size_t n) : bytes(n, 0), tags(n / GRANULE, false), capStore(n / GRANULE) {}
    void storeCap(size_t addr, const Cap& c) { assert(addr % GRANULE == 0); capStore[addr / GRANULE] = c; tags[addr / GRANULE] = true; }
    Cap loadCap(size_t addr) const { Cap c = capStore[addr / GRANULE]; c.tag = tags[addr / GRANULE]; return c; }
    void storeByte(size_t addr, uint8_t v) { bytes[addr] = v; tags[addr / GRANULE] = false; }      // 일반 저장은 해당 칸의 태그를 지운다
    bool tagAt(size_t addr) const { return tags[addr / GRANULE]; }
};
uint8_t use(const Cap& c) { if (!c.tag) throw std::runtime_error("tag violation: invalid capability"); return 1; }

int main() {
    TaggedMemory mem(256);
    mem.storeCap(32, Cap{100, 16, true});                           // 정상적인 케이퍼빌리티 저장
    assert(mem.tagAt(32) && use(mem.loadCap(32)) == 1);             // 태그가 켜져 있어 사용 가능
    mem.storeByte(40, 0xFF);                                        // 공격자가 같은 16바이트 칸의 일부 바이트를 덮어써 케이퍼빌리티를 변조하려 한다
    assert(!mem.tagAt(32));                                         // 태그가 자동으로 꺼졌다
    bool trapped = false; try { use(mem.loadCap(32)); } catch (const std::runtime_error&) { trapped = true; }
    assert(trapped);                                                // 변조된 케이퍼빌리티는 쓸 수 없다
    // 위조 시도: 일반 데이터로 "그럴듯한 케이퍼빌리티 비트 패턴" 을 써도 태그가 없으므로 무효
    for (size_t i = 64; i < 80; i++) mem.storeByte(i, 0x41);
    assert(!mem.tagAt(64) && !mem.loadCap(64).tag);
    std::cout << "CHERIArchitecture: writing data over a capability cleared its tag; forged capabilities are unusable." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 16바이트당 태그 1비트 (약 0.8%)
```
## MemoryTagging()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 메모리 태깅(ARM MTE): 메모리를 16바이트 단위(granule)로 나눠 각각에 4비트 "태그" 를 붙이고, 포인터의 상위 비트에도 같은 4비트 태그를 넣는다.
// 접근할 때 하드웨어가 포인터 태그 == 메모리 태그 인지 검사한다.  할당할 때 임의 태그를 붙이고, 해제하면 다른 태그로 바꾸면 해제 후 사용(UAF)이 대부분(15/16) 잡히고,
// 이웃한 할당끼리 태그를 달리하면 오버플로도 잡힌다.  CHERI 와 달리 포인터 크기가 그대로이고 확률적 보호
struct TaggedPtr { uint64_t addr; unsigned tag; };
class TaggedHeap {
    std::vector<uint8_t> mem, tags; uint64_t top = 0; unsigned nextTag = 1;
public:
    explicit TaggedHeap(size_t n) : mem(n, 0), tags(n / 16, 0) {}
    TaggedPtr alloc(size_t n) {
        size_t g = (n + 15) / 16; unsigned t = nextTag; nextTag = nextTag % 15 + 1;          // 이웃에 다른 태그가 가도록 순환
        TaggedPtr p{top, t}; for (size_t i = 0; i < g; i++) tags[top / 16 + i] = t; top += g * 16; return p;
    }
    void release(TaggedPtr p, size_t n) { unsigned nt = p.tag % 15 + 1; for (size_t i = 0; i < (n + 15) / 16; i++) tags[p.addr / 16 + i] = nt; }   // 해제: 메모리 태그를 다른 값으로 바꿔 둔다 (옛 포인터의 태그와 달라진다)
    uint8_t read(TaggedPtr p, size_t off) const { if (tags[(p.addr + off) / 16] != p.tag) throw std::runtime_error("tag mismatch"); return mem[p.addr + off]; }
    void write(TaggedPtr p, size_t off, uint8_t v) { if (tags[(p.addr + off) / 16] != p.tag) throw std::runtime_error("tag mismatch"); mem[p.addr + off] = v; }
};
template <class F> bool traps(F f) { try { f(); } catch (const std::runtime_error&) { return true; } return false; }

int main() {
    TaggedHeap h(1024);
    TaggedPtr a = h.alloc(32), b = h.alloc(32);                          // 서로 다른 태그를 가진 이웃 할당
    assert(a.tag != b.tag);
    h.write(a, 31, 9); assert(h.read(a, 31) == 9);                        // 범위 안: 정상
    assert(traps([&] { h.write(a, 32, 1); }));                            // 오버플로: a 의 끝을 넘어 b 의 영역(다른 태그)에 쓰기 -> 탐지
    h.release(a, 32);
    assert(traps([&] { h.read(a, 0); }));                                 // 해제 후 사용: 메모리 태그가 바뀌어 탐지
    TaggedPtr c = h.alloc(32);                                            // 같은 번호의 새 할당 (다른 태그)
    assert(traps([&] { h.read(a, 0); }) || c.tag != a.tag);               // 재할당 후에도 옛 포인터는 (태그가 다르면) 거부
    std::cout << "MemoryTagging: overflow into a neighbour and use-after-free both caught by tag mismatch." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
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
#include <iostream>
#include <cstdlib>
#include <new>
#include <cassert>

// malloc: C 함수, 크기(바이트)를 받아 void* 반환, 초기화 없음(생성자 호출 X), 실패 시 NULL.   new: C++ 연산자, 타입을 받아 해당 타입 포인터 반환, 생성자 호출, 실패 시 bad_alloc 예외.
// new 로 만든 것은 delete, malloc 으로 만든 것은 free 로 해제해야 한다 (섞어 쓰면 정의되지 않은 동작)
struct Widget { static int ctors, dtors; int v = 7; Widget() { ctors++; } ~Widget() { dtors++; } };
int Widget::ctors = 0, Widget::dtors = 0;

int main() {
    Widget* viaMalloc = (Widget*)std::malloc(sizeof(Widget));        // 메모리만 확보, 객체는 아직 없다
    assert(Widget::ctors == 0);                                       // 생성자 호출 없음 (v 는 쓰레기 값)
    Widget* viaNew = new Widget;
    assert(Widget::ctors == 1 && viaNew->v == 7);                     // 생성자가 호출되고 멤버가 초기화됨
    new (viaMalloc) Widget;                                           // malloc 메모리에 객체를 만들려면 배치 new 가 필요
    assert(Widget::ctors == 2 && viaMalloc->v == 7);
    viaMalloc->~Widget(); std::free(viaMalloc);                       // malloc 짝은 소멸자 직접 호출 + free
    delete viaNew;                                                    // new 짝은 delete
    assert(Widget::dtors == 2);
    int* arr = (int*)std::malloc(10 * sizeof(int));                   // 크기를 직접 계산해야 한다 (new int[10] 은 타입이 계산)
    assert(arr); std::free(arr);
    std::cout << "malloc vs new: constructors run only with new (or placement new)." << std::endl;
    return 0;
}
// Time Complexity: 할당기에 따라 다름
// Space Complexity: O(n)
```
## free vs delete
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <new>
#include <cassert>

// free: 메모리만 반환한다 — 소멸자를 부르지 않는다.   delete: 소멸자를 먼저 호출(자원 해제)한 뒤 메모리를 반환한다.
// 소멸자가 파일을 닫거나 락을 푸는 객체에 free 를 쓰면 그 자원이 새어 나간다.   delete[] 는 배열의 모든 원소에 소멸자를 호출한다
struct Resource { static int open; Resource() { open++; } ~Resource() { open--; } };
int Resource::open = 0;

int main() {
    Resource* a = new Resource; assert(Resource::open == 1);
    delete a; assert(Resource::open == 0);                             // delete: 소멸자 호출 -> 자원 닫힘

    void* raw = std::malloc(sizeof(Resource));
    Resource* b = new (raw) Resource; assert(Resource::open == 1);
    std::free(b);                                                      // free 만 호출: 메모리는 돌려주지만 소멸자는 호출되지 않는다
    assert(Resource::open == 1);                                       // 자원이 닫히지 않은 채 남았다 (누수)
    Resource::open = 0;

    Resource* arr = new Resource[3]; assert(Resource::open == 3);
    delete[] arr; assert(Resource::open == 0);                         // 배열은 delete[] 로: 소멸자 3번
    std::cout << "free vs delete: free skipped the destructor; delete[] destroyed all elements." << std::endl;
    return 0;
}
// Time Complexity: delete 는 소멸자 비용 포함
// Space Complexity: O(1)
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
#include <iostream>
#include <cmath>
#include <cassert>

// 평균 메모리 접근 시간 AMAT = 적중 시간 + 미스율 × 미스 비용.  L1 적중은 약 4사이클이지만 DRAM 접근은 약 200사이클로 50배 느리다.
// 그래서 미스율이 작아 보여도 평균이 크게 나빠진다: 미스율 5% 만 돼도 AMAT 이 3.5 배가 된다.  캐시 지역성이 곧 성능이다
double amat(double hit, double missRate, double penalty) { return hit + missRate * penalty; }
double amat3(double l1, double l2, double l3, double mem, double m1, double m2, double m3) {      // 3단계 + DRAM
    return l1 + m1 * (l2 + m2 * (l3 + m3 * mem));
}

int main() {
    const double L1 = 4, DRAM = 200;
    assert(amat(L1, 0.00, DRAM) == 4);                                   // 모두 적중
    assert(amat(L1, 0.01, DRAM) == 6);                                   // 1% 미스: 평균 50% 증가
    assert(std::fabs(amat(L1, 0.05, DRAM) - 14) < 1e-9);                 // 5% 미스: 3.5 배
    assert(amat(L1, 0.20, DRAM) / amat(L1, 0.0, DRAM) == 11);            // 20% 미스: 11 배
    // 다단계 캐시는 미스 비용을 단계별로 완화한다: L1 미스 10%, 그중 L2 미스 20%, 그중 L3 미스 30%
    double hierarchical = amat3(4, 12, 40, 200, 0.10, 0.20, 0.30);
    double flat = amat(4, 0.10 * 0.20 * 0.30, 200) ;                      // 참고: 중간 단계를 무시한 값
    assert(hierarchical < amat(4, 0.10, 200));                            // 같은 L1 미스율이라도 L2/L3 가 있으면 훨씬 낫다
    std::cout << "AMAT: 0% miss=4, 1%=6, 5%=14 cycles; 3-level hierarchy (10%/20%/30% misses) = " << hierarchical << " cycles (flat estimate " << flat << ")" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 페이지 교체 알고리즘(LRU, Clock)
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <list>
#include <vector>
#include <cassert>

// 프레임이 가득 찼을 때 어느 페이지를 내보낼까?  OPT(앞으로 가장 늦게 쓸 페이지, 미래를 알아야 하므로 이론적 하한)  /  LRU(가장 오래 안 쓴 페이지, 정확하지만 매 접근마다 갱신이 필요해 비싸다)
// Clock(Second Chance): LRU 를 싸게 근사한다 — 프레임을 원형으로 놓고 참조 비트를 보며 시계바늘이 돈다.  비트가 1 이면 0 으로 내리고 한 번 더 기회를 주고, 0 이면 쫓아낸다.  FIFO 는 구현이 가장 단순하지만 성능이 나쁘다
int fifo(const std::vector<int>& r, int F) { std::list<int> q; int f = 0; for (int p : r) { if (std::find(q.begin(), q.end(), p) != q.end()) continue; f++; if ((int)q.size() == F) q.pop_front(); q.push_back(p); } return f; }
int lru(const std::vector<int>& r, int F) { std::list<int> q; int f = 0; for (int p : r) { auto it = std::find(q.begin(), q.end(), p); if (it != q.end()) { q.erase(it); q.push_back(p); continue; } f++; if ((int)q.size() == F) q.pop_front(); q.push_back(p); } return f; }
int opt(const std::vector<int>& r, int F) {
    std::vector<int> mem; int f = 0;
    for (size_t i = 0; i < r.size(); i++) {
        if (std::find(mem.begin(), mem.end(), r[i]) != mem.end()) continue;
        f++; if ((int)mem.size() < F) { mem.push_back(r[i]); continue; }
        size_t victim = 0; long farthest = -1;
        for (size_t k = 0; k < mem.size(); k++) { long next = 1e9; for (size_t j = i + 1; j < r.size(); j++) if (r[j] == mem[k]) { next = j; break; } if (next > farthest) { farthest = next; victim = k; } }
        mem[victim] = r[i];
    }
    return f;
}
int clockAlg(const std::vector<int>& r, int F) {
    std::vector<int> page(F, -1); std::vector<bool> ref(F, false); int hand = 0, f = 0;
    for (int p : r) {
        auto it = std::find(page.begin(), page.end(), p);
        if (it != page.end()) { ref[it - page.begin()] = true; continue; }       // 적중: 참조 비트만 켠다 (싸다)
        f++;
        while (page[hand] != -1 && ref[hand]) { ref[hand] = false; hand = (hand + 1) % F; }   // 기회를 한 번 주고 넘어감
        page[hand] = p; ref[hand] = true; hand = (hand + 1) % F;
    }
    return f;
}

int main() {
    std::vector<int> refs = {7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1};      // 운영체제 교과서의 표준 참조열 (프레임 3개)
    assert(fifo(refs, 3) == 15 && lru(refs, 3) == 12 && opt(refs, 3) == 9);
    int c = clockAlg(refs, 3);
    assert(c >= opt(refs, 3) && c <= fifo(refs, 3));                   // Clock 은 OPT 보다 나쁘고 FIFO 보다 나쁘지 않다 (LRU 에 가깝다)
    std::cout << "page faults (3 frames): OPT=" << opt(refs, 3) << " LRU=" << lru(refs, 3) << " Clock=" << c << " FIFO=" << fifo(refs, 3) << std::endl;
    return 0;
}
// Time Complexity: LRU 접근당 O(프레임) (리스트), Clock 은 분할상환 O(1)
// Space Complexity: O(프레임 수)
```
## Virtual Memory가 필요한 이유
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <vector>
#include <cassert>

// 가상 메모리가 주는 것: (1) 격리 — 프로세스마다 독립된 주소 공간이라 서로의 메모리를 볼 수 없다  (2) 단순한 프로그래밍 모델 — 모든 프로세스가 같은 가상 주소(예: 0x1000)를 쓸 수 있다
// (3) 공유 — 읽기 전용 라이브러리 페이지를 한 프레임에 매핑해 여러 프로세스가 함께 쓴다  (4) 물리 메모리보다 큰 주소 공간(요구 페이징·스왑)  (5) 보호 — 페이지별 권한
struct Process { std::map<int, int> pageTable; };            // 가상 페이지 -> 물리 프레임
std::vector<int> physical(8, 0);                              // 물리 메모리 8프레임 (각 프레임의 내용을 정수 하나로 단순화)
int load(const Process& p, int vpage) { auto it = p.pageTable.find(vpage); if (it == p.pageTable.end()) return -1; return physical[it->second]; }

int main() {
    Process a, b;
    a.pageTable[1] = 3; b.pageTable[1] = 5;                    // 같은 가상 페이지 1 이 서로 다른 프레임으로
    physical[3] = 111; physical[5] = 222;
    assert(load(a, 1) == 111 && load(b, 1) == 222);            // 같은 주소를 읽어도 각자 자기 데이터 (격리)
    assert(load(a, 2) == -1);                                  // 매핑이 없으면 접근 불가 (b 의 프레임 5 에 닿을 방법이 없다)
    a.pageTable[7] = 0; b.pageTable[9] = 0; physical[0] = 42;  // 라이브러리 프레임 0 을 두 프로세스가 서로 다른 가상 주소로 공유
    assert(load(a, 7) == 42 && load(b, 9) == 42);
    physical[0] = 43; assert(load(a, 7) == 43 && load(b, 9) == 43);   // 한 프레임이므로 물리 메모리는 한 벌만 쓴다
    // 가상 주소 공간은 물리 메모리보다 크다: 프로세스 2개가 각각 1000 페이지를 "예약" 했지만 실제 프레임은 8개뿐 (쓸 때 배정)
    Process big1, big2; for (int v = 0; v < 1000; v++) { big1.pageTable[v] = -1; big2.pageTable[v] = -1; }
    assert(big1.pageTable.size() + big2.pageTable.size() > physical.size());
    std::cout << "Virtual memory: isolation, sharing and over-reservation demonstrated with page tables." << std::endl;
    return 0;
}
// Time Complexity: O(log 매핑 수)
// Space Complexity: O(매핑 수)
```
## 메모리 단편화(Fragmentation)
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 내부 단편화: 블록 안에서 요청보다 크게 줘서 낭비 (크기 클래스 올림, 페이지 올림).   외부 단편화: 빈 공간의 합은 충분하지만 연속된 큰 조각이 없어 할당 실패.
// 해결: 외부 -> 압축(compaction, 이동), 페이징(연속일 필요 없음), 버디/슬랩;  내부 -> 크기 클래스 세분화
int sizeClass(int n) { int c = 16; while (c < n) c *= 2; return c; }       // 16, 32, 64, 128 ...

int main() {
    // 내부 단편화
    assert(sizeClass(17) == 32 && sizeClass(17) - 17 == 15);               // 17 바이트 요청에 32 바이트 -> 15 바이트 낭비
    assert(sizeClass(64) == 64);                                            // 딱 맞으면 낭비 없음
    // 외부 단편화: 6400 바이트 힙에 64 바이트 블록 100개
    const int B = 64, N = 100;
    std::vector<bool> used(N, true);
    for (int i = 0; i < N; i += 2) used[i] = false;                         // 짝수 번째 블록을 해제 -> 3200 바이트가 비었지만 모두 흩어져 있다
    auto largestFree = [&]() { int best = 0, run = 0; for (bool u : used) { run = u ? 0 : run + 1; best = std::max(best, run); } return best * B; };
    int totalFree = 0; for (bool u : used) totalFree += u ? 0 : B;
    assert(totalFree == 3200 && largestFree() == 64);                       // 합은 3200 인데 연속 최대는 64
    assert(largestFree() < 128);                                            // 128 바이트짜리 요청은 실패 (공간은 충분한데도)
    double fragmentation = 1.0 - double(largestFree()) / totalFree;          // 외부 단편화 지수
    assert(fragmentation > 0.97);
    // 압축: 사용 중인 블록을 앞쪽으로 모으면 빈 공간이 하나로 합쳐진다
    int w = 0; std::vector<bool> compacted(N, false);
    for (int i = 0; i < N; i++) if (used[i]) compacted[w++] = true;
    used = compacted;
    assert(largestFree() == 3200);                                          // 이제 3200 바이트 연속 공간
    std::cout << "Fragmentation index before compaction: " << fragmentation << ", after: 0" << std::endl;
    return 0;
}
// Time Complexity: 압축 O(N)
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
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 같은 객체 그래프를 네 가지 방식으로 정리하면 무엇이 회수되는가?  그래프: root -> a -> b,  c <-> d (서로만 가리키는 순환, root 에서 닿지 않음),  e (아무도 안 가리킴).  root 변수를 놓은 뒤:
//  C(수동)            : 프로그래머가 free 를 안 하면 전부 누수.
//  C++ RAII(shared_ptr): 참조 카운트 -> a, b, e 는 회수, 순환 c/d 는 누수.
//  Java(추적 GC)      : root 에서 닿지 않는 것을 전부 회수 (순환 포함).
//  Python             : 참조 카운트(즉시) + 순환 수집기(나중에) -> 즉시는 a, b, e / 순환 GC 실행 후 c, d 도.
struct Graph { std::vector<std::vector<int>> out; };       // 0=root 1=a 2=b 3=c 4=d 5=e
std::set<int> reachable(const Graph& g, int root) { std::set<int> seen{root}; std::vector<int> st{root}; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : g.out[u]) if (seen.insert(v).second) st.push_back(v); } return seen; }
std::set<int> refcountFreed(const Graph& g, int droppedRoot) {                  // 카운트가 0 이 되는 것만 연쇄 해제
    int n = g.out.size(); std::vector<int> rc(n, 0); for (auto& o : g.out) for (int v : o) rc[v]++;
    rc[droppedRoot] = 0; std::set<int> freed; std::vector<int> st{droppedRoot}; freed.insert(droppedRoot);
    while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : g.out[u]) if (--rc[v] == 0 && freed.insert(v).second) st.push_back(v); }
    for (int v = 1; v < n; v++) if (rc[v] == 0 && !freed.count(v)) freed.insert(v);        // 처음부터 카운트 0 인 객체(e)
    return freed;
}

int main() {
    Graph g; g.out = {{1}, {2}, {}, {4}, {3}, {}};
    std::set<int> all = {1, 2, 3, 4, 5};                      // root 를 제외한 객체
    // C: 아무것도 해제하지 않음
    std::set<int> cLeaked = all;
    // C++ shared_ptr (참조 카운트만)
    auto rc = refcountFreed(g, 0); std::set<int> cppFreed; for (int v : rc) if (v != 0) cppFreed.insert(v);
    std::set<int> cppLeaked; for (int v : all) if (!cppFreed.count(v)) cppLeaked.insert(v);
    // Java: 추적 — root 변수를 놓았으므로 루트 집합이 비었고, 루트에서 닿는 객체가 없으니 전부 회수된다 (순환 포함)
    std::set<int> roots, live;                                   // 루트(스택 변수 등)가 없다
    for (int r : roots) { auto s = reachable(g, r); live.insert(s.begin(), s.end()); }
    std::set<int> javaFreed; for (int v : all) if (!live.count(v)) javaFreed.insert(v);
    // Python: 참조 카운트 + 순환 수집
    std::set<int> pyImmediate = cppFreed, pyAfterGc = all;
    assert((cppFreed == std::set<int>{1, 2, 5}));              // a, b, e 즉시 회수
    assert((cppLeaked == std::set<int>{3, 4}));                // 순환만 누수
    assert(cLeaked.size() == 5 && javaFreed.size() == 5);
    assert(pyImmediate.size() == 3 && pyAfterGc.size() == 5);
    std::cout << "Leaked after dropping root — C: " << cLeaked.size() << ", C++ shared_ptr: " << cppLeaked.size() << ", Java: 0, Python: 0 (after cycle GC)" << std::endl;
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
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// CPython 의 모든 값은 PyObject 이고, 머리말은 (참조 횟수 ob_refcnt, 타입 포인터 ob_type) = 64비트에서 16바이트.  그래서 파이썬 int 하나가 최소 28~32바이트다.
// -5..256 의 작은 정수는 미리 만들어 둔 객체를 공유하므로 `a is b` 가 True.   list 는 append 가 O(1) 분할상환이 되도록 필요한 것보다 더 크게 용량을 잡는다 (over-allocation):
//   new_allocated = (newsize + (newsize >> 3) + 6) & ~3     -> 용량 변화 0, 4, 8, 16, 24, 32, 40, 52, 64, 76 ...
struct PyObjectHead { long ob_refcnt; void* ob_type; };
size_t growListAllocation(size_t allocated, size_t newsize) {
    if (newsize <= allocated) return allocated;
    return (newsize + (newsize >> 3) + 6) & ~(size_t)3;
}
const int SMALL_MIN = -5, SMALL_MAX = 256;
bool sameObject(long a, long b) { return a == b && a >= SMALL_MIN && a <= SMALL_MAX; }      // 작은 정수 캐시: 같은 값이면 같은 객체

int main() {
    assert(sizeof(PyObjectHead) == 16);
    std::vector<size_t> caps; size_t allocated = 0;
    for (size_t n = 1; n <= 76; n++) { size_t next = growListAllocation(allocated, n); if (next != allocated) { allocated = next; caps.push_back(allocated); } }
    assert((caps == std::vector<size_t>{4, 8, 16, 24, 32, 40, 52, 64, 76}));       // 실제 CPython 의 list 용량 변화와 같다
    assert(caps.size() == 9);                                                        // 76번 append 에 재할당은 9번뿐 (분할상환 O(1))
    assert(sameObject(100, 100) && sameObject(-5, -5) && !sameObject(257, 257));      // 256 까지만 캐시
    long refcnt = 1; refcnt++; refcnt--; refcnt--;                                   // 참조 횟수 규칙: 참조가 생기면 +1, 사라지면 -1, 0 이면 즉시 해제
    assert(refcnt == 0);
    std::cout << "CPython list capacities: 4 8 16 24 32 40 52 64 76; PyObject header = " << sizeof(PyObjectHead) << " bytes" << std::endl;
    return 0;
}
// Time Complexity: append 분할상환 O(1)
// Space Complexity: 용량이 길이보다 약 12.5% 크다
```
## Rust Ownership와 Borrow Checker
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// Rust 의 빌림 검사기(borrow checker)가 컴파일 시점에 하는 일을 간단한 프로그램 표현 위에서 구현한다.
//  규칙: (1) 이동된 값은 사용할 수 없다 (E0382)  (2) 빌려준 동안 이동할 수 없다 (E0505)  (3) 가변 참조가 있는 동안 다른 참조·사용은 금지 (E0502/E0499/E0503)
//  (4) 불변 참조는 여러 개 가능하지만 가변 참조는 하나뿐 — "별칭 XOR 변경"
enum Kind { LET, MOVE, BORROW, BORROW_MUT, USE, USE_REF, END_BORROW };
struct Stmt { Kind k; std::string a = {}, b = {}; };           // LET x / MOVE x->y / BORROW x as r / BORROW_MUT x as r / USE x / USE_REF r / END_BORROW r

std::string check(const std::vector<Stmt>& prog) {
    std::set<std::string> moved; std::map<std::string, std::pair<std::string, bool>> refs;    // 참조 이름 -> (대상, 가변 여부)
    auto borrows = [&](const std::string& x, bool& anyMut, int& shared) { anyMut = false; shared = 0; for (auto& r : refs) if (r.second.first == x) { if (r.second.second) anyMut = true; else shared++; } };
    for (auto& s : prog) {
        bool anyMut; int shared;
        switch (s.k) {
            case LET: break;
            case MOVE: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut || shared) return "E0505"; moved.insert(s.a); break;
            case USE: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut) return "E0503"; break;
            case BORROW: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut) return "E0502"; refs[s.b] = {s.a, false}; break;
            case BORROW_MUT: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut) return "E0499"; if (shared) return "E0502"; refs[s.b] = {s.a, true}; break;
            case USE_REF: if (!refs.count(s.a)) return "E0597"; break;
            case END_BORROW: refs.erase(s.a); break;
        }
    }
    return "OK";
}

int main() {
    assert(check({{LET, "x"}, {MOVE, "x", "y"}, {USE, "x"}}) == "E0382");                                    // 이동 후 사용
    assert(check({{LET, "x"}, {BORROW, "x", "r1"}, {BORROW, "x", "r2"}, {USE_REF, "r1"}, {USE_REF, "r2"}}) == "OK");   // 불변 참조는 여러 개
    assert(check({{LET, "x"}, {BORROW, "x", "r"}, {BORROW_MUT, "x", "w"}}) == "E0502");                       // 읽는 중에 가변 참조
    assert(check({{LET, "x"}, {BORROW_MUT, "x", "w1"}, {BORROW_MUT, "x", "w2"}}) == "E0499");                 // 가변 참조 둘
    assert(check({{LET, "x"}, {BORROW_MUT, "x", "w"}, {USE, "x"}}) == "E0503");                               // 가변 참조 중 원본 사용
    assert(check({{LET, "x"}, {BORROW, "x", "r"}, {MOVE, "x", "y"}}) == "E0505");                              // 빌려준 채 이동
    assert(check({{LET, "x"}, {BORROW_MUT, "x", "w"}, {END_BORROW, "w"}, {USE, "x"}}) == "OK");               // 참조가 끝나면 원본 사용 가능
    assert(check({{USE_REF, "ghost"}}) == "E0597");
    std::cout << "Borrow checker model: aliasing XOR mutation, move semantics enforced at 'compile time'." << std::endl;
    return 0;
}
// Time Complexity: O(문장 수 · 참조 수)
// Space Complexity: O(참조 수)
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
