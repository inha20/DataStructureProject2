# Part 1. 문자열의 기초
## CreateString()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 문자열의 표현 세 가지: ① C 문자열(끝에 '\0'), ② 길이를 따로 저장(std::string 방식 — 중간에 '\0' 이 있어도 되고 길이가 O(1)), ③ 짧은 문자열 최적화(SSO):
// 15 글자 이하는 객체 안의 버퍼에 두어 힙 할당이 아예 없다. 여기서는 ③ 을 직접 구현(MiniString)하고 std::string 과 무작위 연산열로 대조한다.
//  불변식: c_str()[size()] == '\0' · size() ≤ capacity() · 힙을 쓰는 것은 capacity() > 15 일 때뿐 · 이동하면 원본은 비지만 유효 · 자기 자신에 붙이기(s.append(s)) 도 안전 · 할당/해제 횟수가 같다(누수 없음).
static long g_allocs = 0, g_frees = 0;
char* heapAlloc(size_t n) { ++g_allocs; return static_cast<char*>(std::malloc(n)); }
void heapFree(char* p) { ++g_frees; std::free(p); }
class MiniString {
    static const size_t SSO = 15;
    char* p_; size_t n_, cap_; char inl_[SSO + 1];
    bool onHeap() const { return p_ != inl_; }
    void reallocate(size_t newCap) {                                   // 새 버퍼로 옮긴 뒤 옛 버퍼를 해제 (자기 자신을 붙일 때도 안전하도록 복사 후 해제)
        char* q = newCap > SSO ? heapAlloc(newCap + 1) : inl_; if (q != p_) std::memcpy(q, p_, n_ + 1);
        if (onHeap() && q != p_) heapFree(p_); p_ = q; cap_ = newCap > SSO ? newCap : SSO;
    }
    void ensure(size_t need) { if (need > cap_) reallocate(std::max(need, cap_ * 2)); }      // 기하급수 성장 → 분할상환 O(1)
public:
    MiniString() : p_(inl_), n_(0), cap_(SSO) { inl_[0] = 0; }
    MiniString(const char* s, size_t n) : MiniString() { append(s, n); }
    explicit MiniString(const char* s) : MiniString(s, std::strlen(s)) {}
    MiniString(const MiniString& o) : MiniString(o.p_, o.n_) {}
    MiniString(MiniString&& o) noexcept : p_(inl_), n_(0), cap_(SSO) { inl_[0] = 0; steal(o); }
    MiniString& operator=(const MiniString& o) { if (this != &o) { clear(); append(o.p_, o.n_); } return *this; }
    MiniString& operator=(MiniString&& o) noexcept { if (this != &o) { if (onHeap()) heapFree(p_); p_ = inl_; n_ = 0; cap_ = SSO; inl_[0] = 0; steal(o); } return *this; }
    ~MiniString() { if (onHeap()) heapFree(p_); }
    void steal(MiniString& o) {                                        // 이 객체는 비어 있고 인라인 상태여야 한다. 힙 버퍼는 포인터만 훔치고, 인라인 내용은 복사한다
        if (o.onHeap()) { p_ = o.p_; n_ = o.n_; cap_ = o.cap_; o.p_ = o.inl_; o.cap_ = SSO; } else { std::memcpy(inl_, o.inl_, o.n_ + 1); n_ = o.n_; }
        o.n_ = 0; o.inl_[0] = 0;                                       // 원본은 비었지만 유효
    }
    size_t size() const { return n_; }
    size_t capacity() const { return cap_; }
    bool heapAllocated() const { return onHeap(); }
    const char* c_str() const { return p_; }
    char& operator[](size_t i) { return p_[i]; }
    void clear() { n_ = 0; p_[0] = 0; }
    void reserve(size_t c) { ensure(c); }
    void shrink_to_fit() { if (onHeap() && n_ <= SSO) reallocate(n_); else if (onHeap() && cap_ > n_) { char* q = heapAlloc(n_ + 1); std::memcpy(q, p_, n_ + 1); heapFree(p_); p_ = q; cap_ = n_; } }
    void append(const char* s, size_t n) { size_t off = (s >= p_ && s < p_ + n_ + 1) ? (size_t)(s - p_) : (size_t)-1; ensure(n_ + n); if (off != (size_t)-1) s = p_ + off; std::memmove(p_ + n_, s, n); n_ += n; p_[n_] = 0; }   // s 가 자기 버퍼 안이면 재할당 뒤 주소를 다시 계산
    void push_back(char c) { append(&c, 1); }
    void insert(size_t pos, const char* s, size_t n) { std::string keep(s, n); ensure(n_ + n); std::memmove(p_ + pos + n, p_ + pos, n_ - pos + 1); std::memcpy(p_ + pos, keep.data(), n); n_ += n; }
    void erase(size_t pos, size_t len) { len = std::min(len, n_ - pos); std::memmove(p_ + pos, p_ + pos + len, n_ - pos - len + 1); n_ -= len; }
    void resize(size_t n, char fill) { if (n > n_) { ensure(n); std::memset(p_ + n_, fill, n - n_); } n_ = n; p_[n_] = 0; }
    bool equals(const std::string& s) const { return n_ == s.size() && std::memcmp(p_, s.data(), n_) == 0; }
};

int main() {
    // ① C 문자열 vs 길이 저장: 중간 '\0'
    char c[] = "hello"; assert(sizeof(c) == 6 && std::strlen(c) == 5);
    MiniString m("a\0b", 3); std::string t("a\0b", 3); assert(m.size() == 3 && t.size() == 3 && std::strlen(m.c_str()) == 1 && m.equals(t));       // 길이를 알면 '\0' 도 내용, C 함수는 첫 '\0' 에서 멈춘다
    {   // ② 짧은 문자열은 힙을 쓰지 않는다
        long before = g_allocs; for (size_t len = 0; len <= 15; ++len) { MiniString s(std::string(len, 'x').c_str()); assert(!s.heapAllocated() && s.size() == len && s.capacity() == 15); } assert(g_allocs == before);
        MiniString big(std::string(16, 'y').c_str()); assert(big.heapAllocated() && big.capacity() >= 16 && g_allocs == before + 1);
    }
    // ③ 무작위 연산열 vs std::string (대조 + 불변식)
    std::mt19937 rng(14);
    for (int round = 0; round < 300; ++round) {
        MiniString a; std::string b; MiniString other; std::string otherB;
        for (int op = 0; op < 200; ++op) {
            int t3 = rng() % 12; char ch = (char)(rng() % 4 == 0 ? 0 : 'a' + rng() % 26); std::string chunk(rng() % 25, ch);
            switch (t3) {
                case 0: a.push_back(ch); b.push_back(ch); break;
                case 1: a.append(chunk.data(), chunk.size()); b += chunk; break;
                case 2: { size_t pos = b.empty() ? 0 : rng() % (b.size() + 1); a.insert(pos, chunk.data(), chunk.size()); b.insert(pos, chunk); break; }
                case 3: if (!b.empty()) { size_t pos = rng() % b.size(), len = rng() % 20; a.erase(pos, len); b.erase(pos, len); } break;
                case 4: { size_t n = rng() % 60; a.resize(n, ch); b.resize(n, ch); break; }
                case 5: a.append(a.c_str(), a.size()); b += std::string(b); break;                         // 자기 자신 붙이기 (재할당 중 별칭)
                case 6: if (!b.empty()) { size_t pos = rng() % b.size(), len = 1 + rng() % b.size(); a.append(a.c_str() + pos, std::min(len, b.size() - pos)); b += b.substr(pos, len); } break;   // 자기 일부 붙이기
                case 7: other = a; otherB = b; assert(other.equals(otherB)); break;                          // 복사 대입 (깊은 복사)
                case 8: { MiniString moved(std::move(other)); std::string movedB = otherB; otherB.clear(); assert(moved.equals(movedB) && other.size() == 0 && other.c_str()[0] == 0); a = std::move(moved); b = movedB; break; }
                case 9: a.reserve(rng() % 200); break;
                case 10: a.shrink_to_fit(); break;
                case 11: if (rng() % 10 == 0) { a.clear(); b.clear(); } break;
            }
            assert(a.equals(b) && a.c_str()[a.size()] == 0 && a.size() <= a.capacity() && (a.heapAllocated() == (a.capacity() > 15)));
        }
        other = a; assert(other.equals(b)); MiniString& alias = other; other = alias; assert(other.equals(b));                            // 자기 대입
    }
    assert(g_allocs == g_frees);                                                                                // 누수 없음
    // ④ 연산 횟수: strlen 은 O(n) 스캔, 길이 저장은 O(1)
    {   std::string big(1000000, 'x'); MiniString s(big.c_str()); long steps = 0; for (const char* p = s.c_str(); *p; ++p) ++steps; assert(steps == 1000000 && s.size() == 1000000); }
    assert(g_allocs == g_frees);
    std::cout << "CreateString: MiniString matched std::string over 60000 random operations (" << g_allocs << " heap allocations, all freed); strings up to 15 chars never touched the heap" << std::endl;
    return 0;
}
// Time Complexity: append 분할상환 O(1), insert/erase O(n), 길이 O(1)
// Space Complexity: O(n) (15 바이트 이하는 객체 안)
```
## Length()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// "길이"는 단위에 따라 다르다: 바이트 수 ≠ 코드 포인트 수 ≠ UTF-16 코드 유닛 수 ≠ (눈에 보이는) 글자 수(grapheme cluster).
//  · 길이를 저장하면 바이트 길이는 O(1), strlen 은 O(n).  코드 포인트 수는 UTF-8 이 올바를 때 "연속 바이트(10xxxxxx)가 아닌 바이트의 수" — 잘못된 입력에서는 틀릴 수 있으니 먼저 검증한다.
//  · 검증기를 RFC 3629 / Unicode 표 3-7 의 표 구동 방식으로 독립 구현해 모든 코드 포인트(U+0000..U+10FFFF, 서러게이트 제외)의 부호화·복호화를 전수 확인하고, 무작위 바이트열에서 두 검증기가 일치하는지 본다.
//  · 글자 수: 결합 문자(é = e + U+0301)와 한글 자모 조합(한 = ㅎ+ㅏ+ㄴ)은 코드 포인트가 여럿이어도 글자 하나. 한글 음절 11172 개의 분해·조합을 전수 확인한다.
typedef std::uint32_t u32;
void encode(u32 cp, std::string& out) {
    if (cp < 0x80) out += (char)cp;
    else if (cp < 0x800) { out += (char)(0xC0 | cp >> 6); out += (char)(0x80 | (cp & 0x3F)); }
    else if (cp < 0x10000) { out += (char)(0xE0 | cp >> 12); out += (char)(0x80 | (cp >> 6 & 0x3F)); out += (char)(0x80 | (cp & 0x3F)); }
    else { out += (char)(0xF0 | cp >> 18); out += (char)(0x80 | (cp >> 12 & 0x3F)); out += (char)(0x80 | (cp >> 6 & 0x3F)); out += (char)(0x80 | (cp & 0x3F)); }
}
int expectedBytes(u32 cp) { return cp < 0x80 ? 1 : cp < 0x800 ? 2 : cp < 0x10000 ? 3 : 4; }
int decodeAt(const unsigned char* p, size_t n, u32& cp) {               // 엄격한 복호화: 성공 시 소비한 바이트 수, 실패 시 0 (과잉 부호화·서러게이트·범위 초과·잘림·잘못된 연속 바이트)
    if (n == 0) return 0; unsigned char c = p[0];
    if (c < 0x80) { cp = c; return 1; }
    int len = c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 0; if (len == 0 || n < (size_t)len || c > 0xF4) return 0;
    u32 v = c & (0x3F >> (len - 1)); for (int i = 1; i < len; ++i) { if ((p[i] & 0xC0) != 0x80) return 0; v = v << 6 | (p[i] & 0x3F); }
    if (v < (len == 2 ? 0x80u : len == 3 ? 0x800u : 0x10000u) || v > 0x10FFFF || (v >= 0xD800 && v <= 0xDFFF)) return 0; cp = v; return len;
}
bool validateTable(const unsigned char* p, size_t n) {                   // 독립 검증기: Unicode 표 3-7 (허용되는 바이트 범위)
    size_t i = 0; auto in = [&](size_t k, int lo, int hi) { return k < n && p[k] >= lo && p[k] <= hi; };
    while (i < n) { unsigned char c = p[i];
        if (c <= 0x7F) i += 1;
        else if (c >= 0xC2 && c <= 0xDF) { if (!in(i + 1, 0x80, 0xBF)) return false; i += 2; }
        else if (c == 0xE0) { if (!in(i + 1, 0xA0, 0xBF) || !in(i + 2, 0x80, 0xBF)) return false; i += 3; }
        else if ((c >= 0xE1 && c <= 0xEC) || c == 0xEE || c == 0xEF) { if (!in(i + 1, 0x80, 0xBF) || !in(i + 2, 0x80, 0xBF)) return false; i += 3; }
        else if (c == 0xED) { if (!in(i + 1, 0x80, 0x9F) || !in(i + 2, 0x80, 0xBF)) return false; i += 3; }
        else if (c == 0xF0) { if (!in(i + 1, 0x90, 0xBF) || !in(i + 2, 0x80, 0xBF) || !in(i + 3, 0x80, 0xBF)) return false; i += 4; }
        else if (c >= 0xF1 && c <= 0xF3) { if (!in(i + 1, 0x80, 0xBF) || !in(i + 2, 0x80, 0xBF) || !in(i + 3, 0x80, 0xBF)) return false; i += 4; }
        else if (c == 0xF4) { if (!in(i + 1, 0x80, 0x8F) || !in(i + 2, 0x80, 0xBF) || !in(i + 3, 0x80, 0xBF)) return false; i += 4; }
        else return false; }
    return true;
}
bool validate(const std::string& s) { const unsigned char* p = (const unsigned char*)s.data(); size_t i = 0; u32 cp; while (i < s.size()) { int l = decodeAt(p + i, s.size() - i, cp); if (!l) return false; i += l; } return true; }
size_t countByLeadBytes(const std::string& s) { size_t n = 0; for (unsigned char c : s) n += (c & 0xC0) != 0x80; return n; }       // 연속 바이트가 아닌 바이트 수
std::vector<u32> decodeAll(const std::string& s) { std::vector<u32> v; const unsigned char* p = (const unsigned char*)s.data(); size_t i = 0; u32 cp; while (i < s.size()) { int l = decodeAt(p + i, s.size() - i, cp); assert(l); v.push_back(cp); i += l; } return v; }
size_t utf16Units(const std::vector<u32>& cps) { size_t n = 0; for (u32 c : cps) n += c > 0xFFFF ? 2 : 1; return n; }
// 한글: 음절 = 0xAC00 + (L·21 + V)·28 + T.  분해는 산술, 자모 구간은 L 0x1100.., V 0x1161.., T 0x11A7(T 인덱스 1..27)
const u32 SBase = 0xAC00, LBase = 0x1100, VBase = 0x1161, TBase = 0x11A7, VCount = 21, TCount = 28, SCount = 11172;
std::vector<u32> decomposeHangul(u32 s) { u32 idx = s - SBase; std::vector<u32> r = {LBase + idx / (VCount * TCount), VBase + idx % (VCount * TCount) / TCount}; if (idx % TCount) r.push_back(TBase + idx % TCount); return r; }
std::vector<u32> composeHangul(const std::vector<u32>& in) {
    std::vector<u32> out; for (size_t i = 0; i < in.size(); ++i) {
        u32 c = in[i]; if (!out.empty()) { u32 last = out.back();
            if (last >= LBase && last < LBase + 19 && c >= VBase && c < VBase + VCount) { out.back() = SBase + ((last - LBase) * VCount + (c - VBase)) * TCount; continue; }                    // L + V → LV
            if (last >= SBase && last < SBase + SCount && (last - SBase) % TCount == 0 && c > TBase && c < TBase + TCount) { out.back() = last + (c - TBase); continue; } }                         // LV + T → LVT
        out.push_back(c); }
    return out;
}
size_t graphemeCount(const std::vector<u32>& cps) {                      // 단순화한 확장 글자 군집: 결합 표지는 앞 글자에 붙고, 한글 L V* T* 는 한 덩어리
    auto isExtend = [](u32 c) { return (c >= 0x300 && c <= 0x36F) || (c >= 0x1AB0 && c <= 0x1AFF) || (c >= 0x1DC0 && c <= 0x1DFF) || (c >= 0x20D0 && c <= 0x20FF) || (c >= 0xFE20 && c <= 0xFE2F); };
    auto kind = [](u32 c) { if (c >= 0x1100 && c <= 0x115F) return 'L'; if (c >= 0x1160 && c <= 0x11A7) return 'V'; if (c >= 0x11A8 && c <= 0x11FF) return 'T'; if (c >= SBase && c < SBase + SCount) return (c - SBase) % TCount == 0 ? 'v' : 't'; return 'o'; };   // v = LV 음절, t = LVT 음절
    size_t n = 0; char prev = 0; for (size_t i = 0; i < cps.size(); ++i) { char k = kind(cps[i]); bool join = i > 0 && (isExtend(cps[i]) || (prev == 'L' && (k == 'L' || k == 'V' || k == 'v' || k == 't')) || ((prev == 'v' || prev == 'V') && (k == 'V' || k == 'T')) || ((prev == 't' || prev == 'T') && k == 'T')); n += !join; prev = k; }
    return n;
}

int main() {
    // ① 문자열 몇 개: 바이트 / 코드 포인트 / UTF-16 유닛 / 글자
    struct Case { const char* s; size_t bytes, cps, units, graphemes; } cases[] = {{"hello", 5, 5, 5, 5}, {"한글", 6, 2, 2, 2}, {"a😀b", 6, 3, 4, 3}, {"e\xCC\x81", 3, 2, 2, 1}, {"\xE1\x84\x92\xE1\x85\xA1\xE1\x86\xAB", 9, 3, 3, 1}};     // 마지막: ᄒ+ᅡ+ᆫ (한 의 자모)
    for (auto& c : cases) { std::string s = c.s; assert(validate(s) && s.size() == c.bytes && countByLeadBytes(s) == c.cps); std::vector<u32> cps = decodeAll(s); assert(cps.size() == c.cps && utf16Units(cps) == c.units && graphemeCount(cps) == c.graphemes); }
    // ② 모든 코드 포인트 전수: 부호화 길이, 복호화 왕복, 한 개로 센다 (서러게이트 제외 1,112,064 개)
    long total = 0;
    for (u32 cp = 0; cp <= 0x10FFFF; ++cp) {
        if (cp >= 0xD800 && cp <= 0xDFFF) { std::string bad; bad += (char)(0xE0 | cp >> 12); bad += (char)(0x80 | (cp >> 6 & 0x3F)); bad += (char)(0x80 | (cp & 0x3F)); assert(!validate(bad) && !validateTable((const unsigned char*)bad.data(), 3)); continue; }
        std::string s; encode(cp, s); u32 back = 0; assert((int)s.size() == expectedBytes(cp) && decodeAt((const unsigned char*)s.data(), s.size(), back) == (int)s.size() && back == cp && countByLeadBytes(s) == 1 && validateTable((const unsigned char*)s.data(), s.size())); ++total;
    }
    assert(total == 1112064);
    // 과잉 부호화(overlong)와 잘림은 모두 거부: cp < 0x80 을 2 바이트로, cp < 0x800 을 3 바이트로 ...
    for (u32 cp = 0; cp < 0x80; ++cp) { std::string o; o += (char)(0xC0 | cp >> 6); o += (char)(0x80 | (cp & 0x3F)); assert(!validate(o) && !validateTable((const unsigned char*)o.data(), 2)); }
    // ③ 두 검증기(복호화 기반 vs 표 구동)가 무작위 바이트열 3 백만 개에서 일치, 그리고 올바른 문자열에서만 "비연속 바이트 수 = 코드 포인트 수"
    std::mt19937 rng(23); long valid = 0, invalidButCounted = 0;
    for (int it = 0; it < 3000000; ++it) {
        std::string s(1 + rng() % 5, 0); for (char& c : s) { int r = (int)(rng() % 6); c = (char)(r == 0 ? rng() % 0x80 : r == 1 ? 0x80 + rng() % 0x40 : r == 2 ? 0xC0 + rng() % 0x40 : (int)(rng() % 256)); }
        bool a = validate(s), b = validateTable((const unsigned char*)s.data(), s.size()); assert(a == b); valid += a; if (a) assert(countByLeadBytes(s) == decodeAll(s).size()); else invalidButCounted += countByLeadBytes(s) > 0;
    }
    assert(valid > 100000 && validate(std::string("\xE0\x80\x80", 3)) == false && countByLeadBytes(std::string("\xE0\x80\x80", 3)) == 1);       // 잘못된 입력에서는 세어진 값이 의미가 없다 (E0 80 80 → "1 글자"로 센다)
    // ④ 한글 11172 음절: 분해 → 조합 왕복, 분해된 길이는 2 또는 3, 글자 수는 1
    for (u32 s = SBase; s < SBase + SCount; ++s) { std::vector<u32> d = decomposeHangul(s); assert((d.size() == 2 || d.size() == 3) && ((s - SBase) % TCount == 0) == (d.size() == 2)); std::vector<u32> c = composeHangul(d); assert(c.size() == 1 && c[0] == s && graphemeCount(d) == 1 && graphemeCount(c) == 1); }
    // 무작위 한글 문장: 조합형/분해형의 코드 포인트 수는 다르지만 글자 수는 같다
    long precomposed = 0, decomposed = 0;
    for (int it = 0; it < 2000; ++it) { std::vector<u32> sy, dec; size_t n = 1 + rng() % 30; for (size_t i = 0; i < n; ++i) { u32 s = SBase + rng() % SCount; sy.push_back(s); for (u32 x : decomposeHangul(s)) dec.push_back(x); } assert(composeHangul(dec) == sy && graphemeCount(sy) == n && graphemeCount(dec) == n && dec.size() >= sy.size()); precomposed += sy.size(); decomposed += dec.size(); }
    // ⑤ 비용: 저장된 길이는 O(1), strlen 은 100 만 번의 스캔
    { std::string big(1000000, 'x'); long steps = 0; for (const char* p = big.c_str(); *p; ++p) ++steps; assert(steps == 1000000 && big.size() == 1000000); }
    std::cout << "Length: all 1112064 scalar values round-tripped; two UTF-8 validators agreed on 3*10^6 random byte strings (" << valid << " valid, and for " << invalidButCounted << " invalid ones the lead-byte count was meaningless); " << SCount << " Hangul syllables decompose/compose exactly; random Hangul text had " << precomposed << " precomposed vs " << decomposed << " decomposed code points but identical grapheme counts" << std::endl;
    return 0;
}
// Time Complexity: 바이트 길이 O(1) (저장), 코드 포인트·글자 수 O(n)
// Space Complexity: O(1)
```
## Concat()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 문자열 이어 붙이기의 비용은 *복사한 문자 수*로 센다.
//  ① 한 글자씩 N 번 붙일 때 용량 성장 정책: 필요한 만큼만(+1) → Θ(N²), 16 칸씩 → N²/32, ×1.5 → 3N 미만, ×2 → 2N 미만 (재할당 때 옮기는 문자의 합).  독립 산술 계산과 일치해야 한다.
//  ② k 개의 조각(각 L 글자)을 합치는 세 가지: 왼쪽부터 ((a+b)+c)+… = L·(k(k+1)/2 − 1) 복사, 전체 길이를 미리 구해 한 번에(join) = k·L, 분할 정복 = k·L·log₂k.
//  ③ s = s + x 는 매번 새 문자열을 만들어 Θ(N²), s += x 는 분할상환 Θ(N).  모든 결과는 std::string 과 같아야 한다.
long g_copied = 0;                                                       // 복사한 문자 수
typedef size_t (*Growth)(size_t cap, size_t need);
size_t gExact(size_t, size_t need) { return need; }
size_t gChunk(size_t, size_t need) { return (need + 15) / 16 * 16; }
size_t gX15(size_t cap, size_t need) { return std::max(need, cap + cap / 2 + 1); }
size_t gX2(size_t cap, size_t need) { return std::max(need, cap ? cap * 2 : 1); }
struct Buf {
    char* p = nullptr; size_t n = 0, cap = 0; Growth g; long reallocs = 0; long moved = 0;
    explicit Buf(Growth gg) : g(gg) {}
    ~Buf() { delete[] p; }
    Buf(const Buf&) = delete; Buf& operator=(const Buf&) = delete;
    void append(const char* s, size_t len) {
        if (n + len > cap) { size_t nc = g(cap, n + len); char* q = new char[nc]; if (n) { std::memcpy(q, p, n); g_copied += (long)n; moved += (long)n; } delete[] p; p = q; cap = nc; ++reallocs; }
        std::memcpy(p + n, s, len); n += len; g_copied += (long)len;
    }
    std::string str() const { return std::string(p ? p : "", n); }
};
long simulateMoved(Growth g, long N) { long cap = 0, moved = 0; for (long n = 1; n <= N; ++n) if (n > cap) { moved += n - 1; cap = (long)g((size_t)cap, (size_t)n); } return moved; }       // 버퍼 없이 용량만 따라간 독립 계산
std::string concatLeft(const std::vector<std::string>& v) { std::string acc; for (auto& s : v) { std::string t(acc.size() + s.size(), ' '); std::memcpy(&t[0], acc.data(), acc.size()); std::memcpy(&t[acc.size()], s.data(), s.size()); g_copied += (long)t.size(); acc.swap(t); } return acc; }   // 매번 새 문자열
std::string joinOnce(const std::vector<std::string>& v) { size_t total = 0; for (auto& s : v) total += s.size(); std::string r(total, ' '); size_t off = 0; for (auto& s : v) { std::memcpy(&r[off], s.data(), s.size()); off += s.size(); g_copied += (long)s.size(); } return r; }
std::string concatTree(const std::vector<std::string>& v, size_t lo, size_t hi) { if (hi - lo == 1) return v[lo]; size_t mid = (lo + hi) / 2; std::string a = concatTree(v, lo, mid), b = concatTree(v, mid, hi); std::string r(a.size() + b.size(), ' '); std::memcpy(&r[0], a.data(), a.size()); std::memcpy(&r[a.size()], b.data(), b.size()); g_copied += (long)r.size(); return r; }

int main() {
    // ① 성장 정책
    const long N = 20000; struct P { const char* name; Growth g; } pol[] = {{"exact (+1)", gExact}, {"16-chunk", gChunk}, {"x1.5", gX15}, {"x2", gX2}}; long moved[4];
    for (int i = 0; i < 4; ++i) {
        Buf b(pol[i].g); g_copied = 0; for (long k = 0; k < N; ++k) b.append("x", 1); assert(b.str() == std::string(N, 'x') && b.moved == simulateMoved(pol[i].g, N) && g_copied == b.moved + N); moved[i] = b.moved;
        std::cout << pol[i].name << ": " << b.reallocs << " reallocations, " << b.moved << " characters moved for " << N << " appends (" << (double)b.moved / N << " per append)\n";
    }
    assert(moved[0] == N * (N - 1) / 2);                                                  // +1: 1 + 2 + … + (N−1)
    assert(moved[1] > N * N / 40 && moved[1] < N * N / 25);                               // 16 칸씩: ≈ N²/32
    assert(moved[2] < 3 * N && moved[3] < 2 * N && moved[3] < moved[2]);                  // 곱셈 정책: 분할상환 O(1)/문자
    // ② k 개 조각 합치기
    std::mt19937 rng(9);
    for (int k : {2, 7, 16, 64, 250}) {
        const long L = 40; std::vector<std::string> v(k); std::string want; for (auto& s : v) { s.assign(L, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); want += s; }
        g_copied = 0; assert(concatLeft(v) == want); long left = g_copied; g_copied = 0; assert(joinOnce(v) == want); long once = g_copied; g_copied = 0; assert(concatTree(v, 0, v.size()) == want); long tree = g_copied;
        assert(left == L * ((long)k * (k + 1) / 2) && once == (long)k * L);                                         // 왼쪽 결합: 단계 i 에서 i·L 글자를 새로 복사 → L·k(k+1)/2, join: k·L
        assert(tree >= once && tree <= once * std::max(1L, (long)std::ceil(std::log2((double)k))));                    // 분할 정복: 층마다 k·L → 많아야 k·L·⌈log₂k⌉
        if (k >= 64) assert(left > 5 * tree);
    }
    // ③ s = s + x (매번 새 문자열) vs s += x (용량 재사용)
    { const long M = 3000; std::string a; g_copied = 0; for (long i = 0; i < M; ++i) { std::string t(a.size() + 1, 'x'); std::memcpy(&t[0], a.data(), a.size()); g_copied += (long)t.size(); a.swap(t); } assert(g_copied == M * (M + 1) / 2);
      Buf b(gX2); g_copied = 0; for (long i = 0; i < M; ++i) b.append("x", 1); assert(g_copied < 3 * M && b.str() == a); }
    std::cout << "Concat: copy counts matched the closed forms (+1: N(N-1)/2, x2: " << moved[3] << " < 2N); left-fold vs single join vs divide-and-conquer verified for k = 2..250 pieces" << std::endl;
    return 0;
}
// Time Complexity: 분할상환 O(1)/문자(곱셈 성장), 왼쪽 결합 O(k²L), join O(kL)
// Space Complexity: O(n)
```
## Substring()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstring>
#include <iostream>
#include <memory>
#include <random>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

// substr 은 새 문자열을 만들어 복사(O(len))하고, 뷰는 원본을 가리키는 (포인터, 길이) 한 쌍이라 O(1) 이다. 대신 뷰는 원본보다 오래 살거나 원본이 바뀌면 *dangling* 이 된다.
//  ① View: remove_prefix/suffix·substr·find·compare·starts_with 를 직접 구현하고 std::string_view 와 무작위 연산열로 대조.
//  ② 비용: 재귀 회문 검사를 substr(복사)로 하면 복사한 바이트가 n²/4 에 가깝고, 뷰로 하면 0.  100 만 글자를 20 만 토큰으로 쪼갤 때도 복사 바이트가 전체 길이만큼 든다.
//  ③ CheckedView: 원본이 파괴되거나 수정(재할당)되면 접근 시 예외로 감지 — 디버그 빌드의 반복자 검사와 같은 원리. 소유권 있는 복사본(to_string)은 항상 안전.
struct View {
    const char* p; size_t n;
    View(const char* s, size_t len) : p(s), n(len) {}
    explicit View(const std::string& s) : p(s.data()), n(s.size()) {}
    char operator[](size_t i) const { return p[i]; }
    View substr(size_t pos, size_t len = (size_t)-1) const { if (pos > n) throw std::out_of_range("substr"); return View(p + pos, std::min(len, n - pos)); }
    void remove_prefix(size_t k) { p += k; n -= k; }
    void remove_suffix(size_t k) { n -= k; }
    bool starts_with(View o) const { return n >= o.n && std::memcmp(p, o.p, o.n) == 0; }
    bool ends_with(View o) const { return n >= o.n && std::memcmp(p + n - o.n, o.p, o.n) == 0; }
    size_t find(View o, size_t from = 0) const { if (o.n == 0) return from <= n ? from : (size_t)-1; for (size_t i = from; i + o.n <= n; ++i) if (std::memcmp(p + i, o.p, o.n) == 0) return i; return (size_t)-1; }
    int compare(View o) const { int c = std::memcmp(p, o.p, std::min(n, o.n)); return c != 0 ? (c < 0 ? -1 : 1) : (n == o.n ? 0 : n < o.n ? -1 : 1); }
    std::string to_string() const { return std::string(p, n); }          // 소유권 있는 복사본
};
long g_copied = 0;                                                       // 복사한 바이트 수
std::string copySubstr(const std::string& s, size_t pos, size_t len) { std::string r = s.substr(pos, len); g_copied += (long)r.size(); return r; }
bool palindromeCopy(const std::string& s) { if (s.size() < 2) return true; return s.front() == s.back() && palindromeCopy(copySubstr(s, 1, s.size() - 2)); }
bool palindromeView(View v) { while (v.n >= 2) { if (v[0] != v[v.n - 1]) return false; v.remove_prefix(1); v.remove_suffix(1); } return true; }

struct State { bool alive = true; unsigned version = 0; };
class Owner {                                                            // 문자열을 소유하고, 수정할 때마다 version 을 올린다
    std::string s_; std::shared_ptr<State> st_ = std::make_shared<State>();
public:
    explicit Owner(std::string s) : s_(std::move(s)) {}
    ~Owner() { st_->alive = false; }
    void append(const std::string& x) { s_ += x; ++st_->version; }
    const std::string& str() const { return s_; }
    std::shared_ptr<State> state() const { return st_; }
};
class CheckedView {
    const Owner* o_; std::shared_ptr<State> st_; unsigned ver_; size_t pos_, len_;
public:
    CheckedView(const Owner& o, size_t pos, size_t len) : o_(&o), st_(o.state()), ver_(o.state()->version), pos_(pos), len_(len) {}
    bool valid() const { return st_->alive && st_->version == ver_; }
    char at(size_t i) const { if (!valid()) throw std::runtime_error("stale view"); return o_->str()[pos_ + i]; }
    std::string to_string() const { if (!valid()) throw std::runtime_error("stale view"); return o_->str().substr(pos_, len_); }
};

int main() {
    // ① View vs std::string_view: 무작위 연산열 (작은 알파벳이라 find/compare 가 자주 맞는다)
    std::mt19937 rng(31);
    for (int round = 0; round < 2000; ++round) {
        std::string text(rng() % 40, 'a'); for (char& c : text) c = (char)('a' + rng() % 3); View v(text); std::string_view w(text);
        for (int op = 0; op < 12; ++op) {
            switch (rng() % 7) {
                case 0: { size_t k = v.n ? rng() % (v.n + 1) : 0; v.remove_prefix(k); w.remove_prefix(k); break; }
                case 1: { size_t k = v.n ? rng() % (v.n + 1) : 0; v.remove_suffix(k); w.remove_suffix(k); break; }
                case 2: { size_t pos = rng() % (v.n + 2), len = rng() % 10; bool t1 = false, t2 = false; View a(nullptr, 0); std::string_view b; try { a = v.substr(pos, len); } catch (const std::out_of_range&) { t1 = true; } try { b = w.substr(pos, len); } catch (const std::out_of_range&) { t2 = true; } assert(t1 == t2); if (!t1) { v = a; w = b; } break; }
                default: { std::string pat(rng() % 4, 'a'); for (char& c : pat) c = (char)('a' + rng() % 3); size_t from = rng() % (v.n + 1); size_t f1 = v.find(View(pat), from), f2 = w.find(pat, from); assert(f1 == f2 || (f1 == (size_t)-1 && f2 == std::string_view::npos));
                          assert(v.starts_with(View(pat)) == (w.substr(0, pat.size()) == pat && w.size() >= pat.size())); assert(v.ends_with(View(pat)) == (w.size() >= pat.size() && w.substr(w.size() - pat.size()) == pat)); assert(v.compare(View(pat)) == (w.compare(pat) < 0 ? -1 : w.compare(pat) > 0 ? 1 : 0)); break; }
            }
            assert(v.n == w.size() && std::memcmp(v.p, w.data(), v.n) == 0);
        }
    }
    // ② 비용: 재귀 회문 (복사) vs 뷰
    {   const size_t N = 2000; std::string s(N, 'x'); g_copied = 0; assert(palindromeCopy(s)); long expect = 0; for (size_t len = N; len >= 2; len -= 2) expect += (long)(len - 2); assert(g_copied == expect && expect == (long)(N / 2 - 1) * (long)(N / 2));   // Σ (n−2) + (n−4) + … = (n/2)(n/2 − 1)
      assert(palindromeView(View(s)) && !palindromeView(View(s.replace(N / 2, 1, "y"))) );
      std::string text; std::vector<std::pair<size_t, size_t>> toks; for (int i = 0; i < 200000; ++i) { size_t len = 1 + rng() % 8; toks.emplace_back(text.size(), len); text.append(len, (char)('a' + i % 26)); text += ' '; }
      g_copied = 0; size_t viewBytes = 0; for (auto& t : toks) { std::string c = copySubstr(text, t.first, t.second); View v(text.data() + t.first, t.second); assert(v.to_string() == c); viewBytes += v.n; }
      long tokenBytes = 0; for (auto& t : toks) tokenBytes += (long)t.second; assert(g_copied == tokenBytes && viewBytes == (size_t)tokenBytes && text.size() >= 1000000 / 2); std::cout << "Substring: recursive palindrome copied " << expect << " bytes with substr and 0 with views; tokenising " << text.size() << " characters copied " << g_copied << " bytes vs 0, "; }
    // ③ 검사하는 뷰: 수정·파괴를 감지
    {   Owner* o = new Owner("the quick brown fox"); CheckedView v(*o, 4, 5); assert(v.valid() && v.at(0) == 'q' && v.to_string() == "quick"); std::string safe = v.to_string();
        o->append(" jumps"); assert(!v.valid()); bool threw = false; try { v.at(0); } catch (const std::runtime_error&) { threw = true; } assert(threw);       // 수정(재할당 가능) 뒤의 예전 뷰는 접근 불가
        CheckedView v2(*o, 4, 5); assert(v2.valid()); delete o; assert(!v2.valid()); threw = false; try { v2.to_string(); } catch (const std::runtime_error&) { threw = true; } assert(threw);   // 원본이 사라진 뒤
        assert(safe == "quick");                                                                                                                   // 복사본은 그대로 안전
        std::cout << "stale views (after mutation or owner destruction) were detected and owning copies stayed valid" << std::endl; }
    return 0;
}
// Time Complexity: substr 복사 O(len), 뷰 O(1)
// Space Complexity: substr 복사 O(len), 뷰 O(1) (포인터 + 길이)
```
## Compare()
### 대표코드
```cpp
#include <iostream>
#include <cstring>
#include <string>
#include <cassert>

// 사전식 비교: 처음 다른 문자의 값(부호 없는 바이트)으로 결정하고, 모두 같으면 짧은 쪽이 작다
int compare(const std::string& a, const std::string& b) {
    size_t n = std::min(a.size(), b.size());
    for (size_t i = 0; i < n; i++) {
        unsigned char x = a[i], y = b[i];                // 반드시 unsigned: char 가 음수일 수 있다
        if (x != y) return x < y ? -1 : 1;
    }
    return a.size() == b.size() ? 0 : (a.size() < b.size() ? -1 : 1);
}
int sign(int v) { return (v > 0) - (v < 0); }

int main() {
    assert(compare("apple", "apple") == 0);
    assert(compare("apple", "apricot") < 0);             // 'p' < 'r'
    assert(compare("app", "apple") < 0);                 // 접두사는 더 작다
    assert(compare("Zebra", "apple") < 0);               // 대문자(65~90) < 소문자(97~122)
    assert(compare("é", "z") > 0);                       // UTF-8 바이트 0xC3 > 'z' (바이트 기준 비교)
    for (auto p : {std::pair<const char*, const char*>{"a", "b"}, {"abc", "abd"}, {"", "x"}, {"same", "same"}})
        assert(sign(compare(p.first, p.second)) == sign(std::strcmp(p.first, p.second)));
    std::cout << "Compare verified." << std::endl;
    return 0;
}
// Time Complexity: O(min(|a|, |b|))
// Space Complexity: O(1)
```
## 문자열 비교의 시간복잡도
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 문자열 비교는 O(1) 이 아니다: 공통 접두사(LCP)만큼 걸린다 (같은 문자열이면 전체 길이 L).  그래서 정렬은 n log n *번의 비교* × LCP 만큼의 문자 검사가 든다.
//  ① 문자 검사 횟수를 센다: std::sort(비교 기반) vs 멀티키 퀵정렬(Bentley–Sedgewick: 문자 단위 3-분할, 한 번 맞춘 접두사는 다시 안 본다) — 접두사가 긴 데이터에서 차이가 크다.
//  ② 정렬된 이웃과의 LCP 합 D 는 어떤 알고리즘이든 *읽어야 하는* 최소 문자 수(구별 접두사): 멀티키 퀵정렬은 O(n log n + D) 이다.
//  ③ 해시를 캐시해 두면 서로 다른 문자열의 동치 비교는 O(1) 로 걸러진다 (마지막 글자만 다른 최악의 경우도).
long g_chars = 0;                                                       // 검사한 문자 수
int charAt(const std::string& s, size_t d) { ++g_chars; return d < s.size() ? (unsigned char)s[d] : -1; }
bool countingLess(const std::string& a, const std::string& b) { size_t n = std::min(a.size(), b.size()), i = 0; for (; i < n; ++i) { ++g_chars; if (a[i] != b[i]) return (unsigned char)a[i] < (unsigned char)b[i]; } ++g_chars; return a.size() < b.size(); }
void mkqs(std::vector<const std::string*>& a, long lo, long hi, size_t d, std::mt19937& rng) {   // a[lo, hi) 를 d 번째 문자부터 정렬
    while (hi - lo > 1) {
        int v = charAt(*a[lo + (long)(rng() % (hi - lo))], d); long lt = lo, gt = hi, i = lo;               // 피벗 문자 v 로 <v | =v | >v 3-분할
        while (i < gt) { int c = charAt(*a[i], d); if (c < v) std::swap(a[lt++], a[i++]); else if (c > v) std::swap(a[i], a[--gt]); else ++i; }
        mkqs(a, lo, lt, d, rng); mkqs(a, gt, hi, d, rng);
        if (v < 0) return;                                                                                 // 끝에 닿은(같은) 문자열들은 더 볼 문자가 없다
        lo = lt; hi = gt; ++d;                                                                             // 같은 문자 묶음은 다음 문자로
    }
}
size_t lcp(const std::string& a, const std::string& b) { size_t i = 0; while (i < a.size() && i < b.size() && a[i] == b[i]) ++i; return i; }

int main() {
    std::mt19937 rng(17); const int n = 20000;
    auto randomStr = [&](size_t len) { std::string s(len, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); return s; };
    struct Data { const char* name; std::vector<std::string> v; } sets[4];
    sets[0].name = "random 8"; for (int i = 0; i < n; ++i) sets[0].v.push_back(randomStr(8));
    sets[1].name = "common prefix 100"; for (int i = 0; i < n; ++i) sets[1].v.push_back(std::string(100, 'p') + randomStr(8));
    sets[2].name = "url-like"; for (int i = 0; i < n; ++i) sets[2].v.push_back("https://example.com/path/" + std::to_string(rng() % 50) + "/item/" + randomStr(5));
    sets[3].name = "many duplicates"; for (int i = 0; i < n; ++i) sets[3].v.push_back(std::string(60, 'z') + std::to_string(rng() % 20));
    double ratio[4];
    for (int k = 0; k < 4; ++k) {
        std::vector<std::string> a = sets[k].v; g_chars = 0; std::sort(a.begin(), a.end(), countingLess); long stdChars = g_chars;
        std::vector<const std::string*> p; for (auto& s : sets[k].v) p.push_back(&s); g_chars = 0; mkqs(p, 0, (long)p.size(), 0, rng); long mkChars = g_chars;
        for (size_t i = 0; i < a.size(); ++i) assert(*p[i] == a[i]);                                          // 같은 정렬 결과
        long D = 0; for (size_t i = 0; i < a.size(); ++i) { size_t l = std::max(i ? lcp(a[i - 1], a[i]) : 0, i + 1 < a.size() ? lcp(a[i], a[i + 1]) : 0); D += (long)l + 1; }       // 구별 접두사의 합
        assert(mkChars >= D / 2 && mkChars <= 12 * ((long)n * (long)std::ceil(std::log2((double)n)) + D));   // 멀티키 퀵정렬: Θ(n log n + D) 범위
        ratio[k] = (double)stdChars / mkChars; std::cout << sets[k].name << ": std::sort inspected " << stdChars << " chars, multikey quicksort " << mkChars << " (distinguishing prefix D = " << D << ")\n";
    }
    assert(ratio[1] > 8 && ratio[3] > 8 && ratio[0] < 3);                                                      // 긴 공통 접두사에서는 크게 이기고, 짧은 무작위 문자열에서는 비슷하다
    // ③ 해시 캐시 동치 비교: 길이 L 이 같고 마지막 글자만 다른 쌍
    {   const size_t L = 100000; std::string x(L, 'x'), y = x; y.back() = 'y'; size_t hx = std::hash<std::string>()(x), hy = std::hash<std::string>()(y); long cheap = 0, full = 0;
        auto eqCached = [&](const std::string& a, size_t ha, const std::string& b, size_t hb) { ++cheap; if (ha != hb) return false; return a == b; };
        auto eqScan = [&](const std::string& a, const std::string& b) { for (size_t i = 0; i < a.size(); ++i) { ++full; if (a[i] != b[i]) return false; } return true; };
        assert(!eqCached(x, hx, y, hy) && !eqScan(x, y) && cheap == 1 && full == (long)L && eqCached(x, hx, std::string(x), hx));
        std::cout << "equality of two " << L << "-char strings differing in the last char: " << full << " chars scanned vs " << 1 << " hash comparison" << std::endl; }
    return 0;
}
// Time Complexity: 비교 O(LCP), 비교 기반 정렬 O(n log n · LCP), 멀티키 퀵정렬 O(n log n + D)
// Space Complexity: O(n) (포인터 배열), 재귀 깊이 O(log n + 최대 길이)
```
## Reverse()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 바이트 단위로 뒤집으면 UTF-8 이 깨진다 → 코드 포인트(문자) 단위로 뒤집어야 한다. 결합 문자(é = e + U+0301)까지 있다면 *글자(grapheme) 단위*여야 한다.
//  ① 제자리(O(1) 추가 공간) 코드 포인트 뒤집기: 전체 바이트를 뒤집으면 문자마다 [연속 바이트…, 선두 바이트] 순서가 되므로, 문자 하나씩 다시 뒤집어 바로잡는다 — 잘못된 UTF-8 이 와도 경계를 넘지 않는다.
//  ② 성질 검사: 두 번 뒤집으면 원래대로, 결과는 올바른 UTF-8, 비 ASCII 문자가 하나라도 있으면 *바이트* 뒤집기 결과는 항상 올바르지 않다 (첫 바이트가 연속 바이트가 되므로).
//  ③ 글자 단위 뒤집기: 결합 표지는 앞 글자와 한 덩어리로 다뤄야 한다.  ④ 단어 순서 뒤집기(제자리): 전체 뒤집기 후 단어마다 다시 뒤집기.
typedef std::uint32_t u32;
void reverseRange(std::string& s, size_t i, size_t j) { while (i + 1 < j) { std::swap(s[i], s[j - 1]); ++i; --j; } }     // [i, j) 를 두 포인터로
void reverseBytes(std::string& s) { reverseRange(s, 0, s.size()); }
void reverseCodePoints(std::string& s) {
    reverseBytes(s);
    for (size_t i = 0; i < s.size();) { size_t j = i; while (j < s.size() && ((unsigned char)s[j] & 0xC0) == 0x80) ++j; size_t end = j < s.size() ? j + 1 : j; reverseRange(s, i, end); i = end; }       // 연속 바이트들 + 선두 바이트 = 문자 하나
}
void encode(u32 cp, std::string& out) {
    if (cp < 0x80) out += (char)cp; else if (cp < 0x800) { out += (char)(0xC0 | cp >> 6); out += (char)(0x80 | (cp & 0x3F)); }
    else if (cp < 0x10000) { out += (char)(0xE0 | cp >> 12); out += (char)(0x80 | (cp >> 6 & 0x3F)); out += (char)(0x80 | (cp & 0x3F)); }
    else { out += (char)(0xF0 | cp >> 18); out += (char)(0x80 | (cp >> 12 & 0x3F)); out += (char)(0x80 | (cp >> 6 & 0x3F)); out += (char)(0x80 | (cp & 0x3F)); }
}
bool decode(const std::string& s, std::vector<u32>& out) {              // 올바른 UTF-8 이면 코드 포인트 목록, 아니면 false (엄격: 과잉 부호화·서러게이트 거부)
    out.clear(); size_t i = 0; while (i < s.size()) { unsigned char c = s[i]; int len = c < 0x80 ? 1 : c >= 0xF8 ? 0 : c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 0; if (!len || i + len > s.size()) return false;
        u32 v = len == 1 ? c : c & (0x3F >> (len - 1)); for (int k = 1; k < len; ++k) { if (((unsigned char)s[i + k] & 0xC0) != 0x80) return false; v = v << 6 | ((unsigned char)s[i + k] & 0x3F); }
        if (v < (len == 2 ? 0x80u : len == 3 ? 0x800u : len == 4 ? 0x10000u : 0u) || v > 0x10FFFF || (v >= 0xD800 && v <= 0xDFFF)) return false; out.push_back(v); i += len; }
    return true;
}
bool isMark(u32 c) { return (c >= 0x300 && c <= 0x36F) || (c >= 0x1AB0 && c <= 0x1AFF) || (c >= 0x1DC0 && c <= 0x1DFF) || (c >= 0x20D0 && c <= 0x20FF); }
std::string reverseGraphemes(const std::string& s) {                    // 결합 표지는 앞의 글자에 붙어 한 덩어리
    std::vector<u32> cps; bool ok = decode(s, cps); assert(ok); (void)ok; std::vector<std::vector<u32>> clusters;
    for (u32 c : cps) { if (!clusters.empty() && isMark(c)) clusters.back().push_back(c); else clusters.push_back({c}); }
    std::string r; for (size_t i = clusters.size(); i-- > 0;) for (u32 c : clusters[i]) encode(c, r); return r;
}
void reverseWords(std::string& s) { reverseBytes(s); for (size_t i = 0; i < s.size();) { if (s[i] == ' ') { ++i; continue; } size_t j = i; while (j < s.size() && s[j] != ' ') ++j; reverseRange(s, i, j); i = j; } }

int main() {
    std::string a = "hello"; reverseBytes(a); assert(a == "olleh");
    std::string kr = "가나다"; reverseCodePoints(kr); assert(kr == "다나가");
    std::string bad = "가나다"; reverseBytes(bad); std::vector<u32> tmp; assert(bad != "다나가" && !decode(bad, tmp));                 // 바이트 뒤집기는 깨진 문자열
    // ② 무작위 올바른 UTF-8 (1~4 바이트 문자와 결합 표지가 섞임)
    std::mt19937 rng(8);
    auto randomCp = [&]() -> u32 { switch (rng() % 6) { case 0: return 0x20 + rng() % 0x5F; case 1: return 0xA1 + rng() % 0x600; case 2: return 0x300 + rng() % 0x70; case 3: return 0xAC00 + rng() % 11172; case 4: return 0x10000 + rng() % 0x100000; default: { u32 c = 0x800 + rng() % 0xF800; if (c >= 0xD800 && c <= 0xDFFF) c = 0xE000; return c; } } };
    long nonAscii = 0;
    for (int it = 0; it < 20000; ++it) {
        std::vector<u32> cps(rng() % 25); std::string s; bool multi = false; for (u32& c : cps) { c = randomCp(); encode(c, s); multi |= c >= 0x80; }
        std::string t = s; reverseCodePoints(t); std::vector<u32> got, want = cps; std::reverse(want.begin(), want.end()); assert(decode(t, got) && got == want);          // 참조: 복호화 → 뒤집기
        std::string u = t; reverseCodePoints(u); assert(u == s);                                                                                                        // 두 번 뒤집으면 원래대로
        std::string bytes = s; reverseBytes(bytes); std::vector<u32> tmp2; if (multi) { assert(!decode(bytes, tmp2)); ++nonAscii; } else assert(bytes == t);                // 비 ASCII 가 있으면 바이트 뒤집기는 항상 깨진다
        std::string g = reverseGraphemes(s); std::vector<u32> gc; assert(decode(g, gc) && gc.size() == cps.size() && (cps.empty() || isMark(cps[0]) || reverseGraphemes(g) == s));     // 글자 단위도 두 번이면 원래대로 (맨 앞이 결합 표지가 아닐 때)
    }
    assert(nonAscii > 15000);
    // 잘못된 UTF-8 이 와도 경계를 넘지 않는다 (ASan 으로도 확인): 길이는 그대로
    for (int it = 0; it < 20000; ++it) { std::string s(rng() % 12, 'x'); for (char& c : s) c = (char)rng(); size_t n = s.size(); reverseCodePoints(s); assert(s.size() == n); }
    // ③ 글자 단위: e + U+0301 은 한 글자
    { std::string s = "e\xCC\x81x"; std::string cp = s; reverseCodePoints(cp); assert(cp == "x\xCC\x81" "e");                  // 코드 포인트 뒤집기: 표지가 x 에 붙는다 (틀림)
      assert(reverseGraphemes(s) == "xe\xCC\x81"); }                                                                           // 글자 뒤집기: é 가 보존된다
    // ④ 단어 순서 뒤집기 (제자리, 공백 보존)
    for (int it = 0; it < 5000; ++it) { std::string s(rng() % 30, ' '); for (char& c : s) c = rng() % 4 == 0 ? ' ' : (char)('a' + rng() % 3);
        std::vector<std::string> tokens; for (size_t i = 0; i < s.size();) { size_t j = i; bool sp = s[i] == ' '; while (j < s.size() && (s[j] == ' ') == sp) ++j; tokens.push_back(s.substr(i, j - i)); i = j; }
        std::string want; for (size_t i = tokens.size(); i-- > 0;) want += tokens[i]; std::string t = s; reverseWords(t); assert(t == want); }
    // 큰 입력: 100 만 글자 (ASCII 와 한글 섞음)
    { std::string s; for (int i = 0; i < 250000; ++i) { s += "ab"; encode(0xAC00 + rng() % 11172, s); } std::vector<u32> cps; assert(decode(s, cps)); std::string t = s; reverseCodePoints(t); std::vector<u32> back; assert(decode(t, back)); std::reverse(cps.begin(), cps.end()); assert(back == cps && s.size() > 1000000);
      std::cout << "Reverse: in-place code point reversal matched decode-reverse-encode on 20000 random strings and 10^6-byte input; byte reversal broke every string with a non-ASCII character" << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: 바이트·코드 포인트 뒤집기 O(1), 글자 뒤집기 O(n)
```
## Split()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

// 구분자로 나누기. string_view 를 돌려주면 복사 없이 O(n) 이고, 설계 선택(빈 토큰 유지 여부·최대 분할 수·여러 글자 구분자·따옴표)이 의미를 결정한다.
//  성질: keepEmpty 면 join(split(s, d), d) == s 이고 토큰 수 = (d 의 개수) + 1.  Python 의 의미(split(d, maxsplit), 겹치는 구분자는 왼쪽부터 겹치지 않게)를 따른다.
//  마지막에 RFC 4180 CSV: 따옴표 안의 쉼표·줄바꿈·"" 이스케이프를 파싱하고, 쓰기 → 읽기 왕복을 무작위 필드로 확인한다.
typedef std::vector<std::string_view> Views;
Views split(std::string_view s, char d, bool keepEmpty = true) {
    Views out; size_t start = 0;
    for (size_t i = 0; i <= s.size(); ++i) if (i == s.size() || s[i] == d) { if (keepEmpty || i > start) out.push_back(s.substr(start, i - start)); start = i + 1; }
    return out;
}
Views splitN(std::string_view s, char d, size_t maxSplit) {              // 최대 maxSplit 번만 자른다 (토큰 ≤ maxSplit + 1), 나머지는 마지막 토큰에
    Views out; size_t start = 0;
    for (size_t i = 0; i < s.size() && out.size() < maxSplit; ++i) if (s[i] == d) { out.push_back(s.substr(start, i - start)); start = i + 1; }
    out.push_back(s.substr(start)); return out;
}
Views splitStr(std::string_view s, std::string_view delim) {              // 여러 글자 구분자, 왼쪽부터 겹치지 않게
    if (delim.empty()) throw std::invalid_argument("empty delimiter"); Views out; size_t start = 0;
    for (size_t pos; (pos = s.find(delim, start)) != std::string_view::npos; start = pos + delim.size()) out.push_back(s.substr(start, pos - start));
    out.push_back(s.substr(start)); return out;
}
Views splitWhitespace(std::string_view s) {                               // 연속 공백은 하나, 양 끝 공백 무시 (Python 의 s.split())
    Views out; size_t i = 0; while (i < s.size()) { while (i < s.size() && (s[i] == ' ' || s[i] == '\t' || s[i] == '\n')) ++i; size_t j = i; while (j < s.size() && !(s[j] == ' ' || s[j] == '\t' || s[j] == '\n')) ++j; if (j > i) out.push_back(s.substr(i, j - i)); i = j; }
    return out;
}
std::string join(const Views& v, std::string_view d) { std::string r; for (size_t i = 0; i < v.size(); ++i) { if (i) r += d; r += v[i]; } return r; }
typedef std::vector<std::vector<std::string>> Rows;
Rows csvParse(const std::string& t) {                                    // 줄(행)마다 필드 목록. 따옴표 안에서는 , 와 줄바꿈이 그대로 내용이다
    Rows rows; std::vector<std::string> row; std::string f; bool inQ = false, any = false;
    for (size_t i = 0; i < t.size(); ++i) { char c = t[i]; any = true;
        if (inQ) { if (c == '"') { if (i + 1 < t.size() && t[i + 1] == '"') { f += '"'; ++i; } else inQ = false; } else f += c; }
        else if (c == '"' && f.empty()) inQ = true;
        else if (c == ',') { row.push_back(f); f.clear(); }
        else if (c == '\n') { row.push_back(f); f.clear(); rows.push_back(row); row.clear(); any = false; }
        else f += c; }
    if (inQ) throw std::runtime_error("unterminated quote"); if (any) { row.push_back(f); rows.push_back(row); }
    return rows;
}
std::string csvWrite(const Rows& rows) {
    std::string out; for (auto& r : rows) { for (size_t i = 0; i < r.size(); ++i) { if (i) out += ','; const std::string& f = r[i]; bool q = f.find_first_of(",\"\n\r") != std::string::npos;
            if (q) { out += '"'; for (char c : f) { if (c == '"') out += '"'; out += c; } out += '"'; } else out += f; } out += '\n'; }
    return out;
}

int main() {
    Views t = split("a,,b,", ','); assert((t == Views{"a", "", "b", ""})); Views u = split("a,,b,", ',', false); assert((u == Views{"a", "b"}));
    assert(split("", ',').size() == 1 && split("", ',', false).empty() && split("no-delim", ',').size() == 1);
    std::mt19937 rng(41);
    auto randomText = [&](size_t n) { std::string s(n, 'a'); for (char& c : s) c = "ab, \t"[rng() % 5]; return s; };
    for (int it = 0; it < 20000; ++it) {
        std::string s = randomText(rng() % 25); char d = ',';
        Views v = split(s, d); assert(join(v, ",") == s && v.size() == (size_t)std::count(s.begin(), s.end(), d) + 1);                       // join 왕복, 토큰 수
        std::vector<std::string> ref; { size_t st = 0, p; while ((p = s.find(d, st)) != std::string::npos) { ref.push_back(s.substr(st, p - st)); st = p + 1; } ref.push_back(s.substr(st)); }       // 다른 방식(find 루프)의 참조
        assert(v.size() == ref.size()); for (size_t i = 0; i < v.size(); ++i) assert(v[i] == ref[i]);
        size_t maxSplit = rng() % 5; Views n = splitN(s, d, maxSplit); assert(n.size() <= maxSplit + 1 && join(n, ",") == s && (n.size() == maxSplit + 1 || n.size() == v.size()) && (n.size() == v.size() || n.back() == std::string_view(s).substr(n.back().data() - s.data())));
        Views drop = split(s, d, false); for (auto x : drop) assert(!x.empty());
        Views w = splitWhitespace(s); std::istringstream in(s); std::string word; size_t k = 0; while (in >> word) { assert(k < w.size() && w[k] == word); ++k; } assert(k == w.size());       // istringstream 과 같은 토큰
        std::string delim = std::string(1 + rng() % 2, "ab"[rng() % 2]); Views m = splitStr(s, delim); assert(join(m, delim) == s); for (size_t i = 0; i + 1 < m.size(); ++i) assert(m[i].find(delim) == std::string_view::npos);                              // 토큰 안에는 구분자가 없다
        size_t cnt = 0, from = 0; for (size_t p; (p = s.find(delim, from)) != std::string::npos; from = p + delim.size()) ++cnt; assert(m.size() == cnt + 1);
    }
    assert((splitStr("aaaa", "aa") == Views{"", "", ""}) && (splitStr("aaa", "aa") == Views{"", "a"}) && (splitN("a,b,c,d", ',', 2) == Views{"a", "b", "c,d"}));       // 파이썬과 같은 결과
    bool threw = false; try { splitStr("x", ""); } catch (const std::invalid_argument&) { threw = true; } assert(threw);
    // CSV: 알려진 경우
    { Rows r = csvParse("a,\"b,c\",d\n\"he said \"\"hi\"\"\",x,\n\"line1\nline2\",,z\n"); assert(r.size() == 3 && r[0] == (std::vector<std::string>{"a", "b,c", "d"}) && r[1] == (std::vector<std::string>{"he said \"hi\"", "x", ""}) && r[2] == (std::vector<std::string>{"line1\nline2", "", "z"}));
      threw = false; try { csvParse("\"open"); } catch (const std::runtime_error&) { threw = true; } assert(threw); }
    // CSV 쓰기 → 읽기 왕복 (필드에 쉼표·따옴표·줄바꿈·빈 문자열)
    for (int it = 0; it < 20000; ++it) { Rows rows(rng() % 5); for (auto& r : rows) { r.resize(1 + rng() % 4); for (auto& f : r) { f.assign(rng() % 6, 'a'); for (char& c : f) c = ",\"\n\r ab"[rng() % 7]; } } assert(csvParse(csvWrite(rows)) == rows); }
    // 큰 입력: 100 만 글자
    { std::string big; for (int i = 0; i < 200000; ++i) big += "ab,c"; Views v = split(big, ','); assert(v.size() == 200001 && join(v, ",") == big); std::cout << "Split: " << v.size() << " tokens from a 10^6-character string; join round-trip, Python-style maxsplit/multi-character semantics and RFC 4180 CSV round-trips verified" << std::endl; }
    return 0;
}
// Time Complexity: O(n) (string_view 토큰, 복사 없음)
// Space Complexity: O(토큰 수)
```
## Immutable String
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <iostream>
#include <memory>
#include <mutex>
#include <random>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

// 불변 문자열(Java String, Python str): 한 번 만들면 바뀌지 않는다.
//  + 복사는 포인터 공유로 O(1), 여러 스레드가 락 없이 읽어도 안전, 해시를 한 번만 계산해 캐시, 해시맵 키로 안전.   + 인터닝하면 동치 비교가 포인터 비교 O(1).
//  − 수정마다 새 문자열(연결 O(n+m)) → 가변 버퍼(StringBuilder)가 따로 필요.   − 조각(slice)이 버퍼를 공유하면 작은 조각이 큰 원본을 붙잡는다 (Java 6 의 substring 메모리 누수) → compact() 로 복사해 놓아 준다.
//  아래 구현은 ① 공유·불변 확인 ② 인터닝 풀(약한 참조라 쓰이지 않으면 해제) ③ 8 스레드 동시 읽기(TSan) ④ 해시·비교 비용 계수 ⑤ slice 공유와 compact 를 한 번에 확인한다.
static std::atomic<long> g_hashes{0}, g_cmpBytes{0};
class IStr {
    friend class InternPool;
    struct Rep { const std::string s; const size_t hash; explicit Rep(std::string x) : s(std::move(x)), hash(std::hash<std::string>()(s)) { ++g_hashes; } };
    std::shared_ptr<const Rep> p_; size_t off_, len_;
    IStr(std::shared_ptr<const Rep> p, size_t off, size_t len) : p_(std::move(p)), off_(off), len_(len) {}
public:
    IStr() : IStr(std::make_shared<const Rep>(std::string()), 0, 0) {}
    explicit IStr(std::string s) : p_(std::make_shared<const Rep>(std::move(s))), off_(0), len_(p_->s.size()) {}
    size_t size() const { return len_; }
    std::string str() const { return p_->s.substr(off_, len_); }
    char operator[](size_t i) const { return p_->s[off_ + i]; }
    IStr concat(const IStr& o) const { return IStr(str() + o.str()); }                          // 새 객체 (원본은 그대로)
    IStr slice(size_t pos, size_t len) const { assert(pos + len <= len_); return IStr(p_, off_ + pos, len); }      // 버퍼 공유 O(1)
    IStr compact() const { return IStr(str()); }                                                // 조각만 복사해 큰 원본을 놓아 준다
    bool sameObject(const IStr& o) const { return p_ == o.p_ && off_ == o.off_ && len_ == o.len_; }
    long refs() const { return p_.use_count(); }
    size_t retainedBytes() const { return p_->s.size(); }
    std::weak_ptr<const void> observer() const { return p_; }
    size_t hash() const { return off_ == 0 && len_ == p_->s.size() ? p_->hash : std::hash<std::string>()(str()); }        // 전체 문자열은 캐시된 해시
    bool operator==(const IStr& o) const {
        if (sameObject(o)) return true;                                                          // 같은 객체: 비교 0 바이트
        if (len_ != o.len_) return false; if (hash() != o.hash()) return false;                  // 길이·해시로 대부분 걸러진다
        g_cmpBytes += (long)len_; return p_->s.compare(off_, len_, o.p_->s, o.off_, len_) == 0;
    }
};
class InternPool {
    std::unordered_map<std::string, std::weak_ptr<const IStr::Rep>> m; std::mutex mu;
public:
    IStr intern(const std::string& s) {                                  // 같은 내용이면 같은 객체. 풀은 약한 참조만 쥐므로 아무도 안 쓰는 문자열은 해제된다
        std::lock_guard<std::mutex> g(mu); auto it = m.find(s); if (it != m.end()) if (auto sp = it->second.lock()) return IStr(sp, 0, sp->s.size());
        IStr n(s); m[s] = n.p_; return n;
    }
    size_t size() { std::lock_guard<std::mutex> g(mu); for (auto it = m.begin(); it != m.end();) it = it->second.expired() ? m.erase(it) : std::next(it); return m.size(); }     // 살아 있는 항목 수 (만료된 것은 정리)
};

int main() {
    // ① 복사 = 공유, 연결 = 새 객체, 원본 불변
    { IStr a("hello"); IStr b = a; assert(a.sameObject(b) && a.refs() == 2); IStr c = a.concat(IStr(" world")); assert(a.str() == "hello" && c.str() == "hello world" && !c.sameObject(a) && a.refs() == 2); }
    // ② 인터닝: 내용이 같으면 같은 객체 → 동치 비교가 포인터 비교. 무작위 단어 2 만 번, 어휘 300 개
    { InternPool pool; std::mt19937 rng(3); std::vector<IStr> held; std::vector<std::string> words; for (int i = 0; i < 20000; ++i) { std::string w = "w" + std::to_string(rng() % 300); words.push_back(w); held.push_back(pool.intern(w)); }
      g_cmpBytes = 0; for (int it = 0; it < 20000; ++it) { size_t i = rng() % held.size(), j = rng() % held.size(); assert((held[i] == held[j]) == (words[i] == words[j]) && held[i].sameObject(held[j]) == (words[i] == words[j])); }
      assert(g_cmpBytes == 0 && pool.size() == 300);                                                       // 같은 단어는 항상 같은 객체라 문자 비교가 한 번도 필요 없었다
      held.clear(); assert(pool.size() == 0); }                                                            // 아무도 안 쓰면 풀에서도 사라진다
    // 인터닝하지 않으면 같은 내용도 서로 다른 객체 → 길이·해시가 같으면 바이트를 비교한다
    { IStr x(std::string(1000, 'q')), y(std::string(1000, 'q')); g_cmpBytes = 0; assert(x == y && !x.sameObject(y) && g_cmpBytes == 1000); IStr z(std::string(999, 'q') + "r"); g_cmpBytes = 0; assert(!(x == z) && g_cmpBytes == 0); }    // 다르면 해시만 보고 0 바이트
    // ③ 8 스레드가 같은 불변 문자열을 락 없이 읽는다 (TSan 으로 경쟁 없음 확인)
    { IStr shared(std::string(10000, 'k')); std::atomic<long> total{0}; std::vector<std::thread> th; for (int t = 0; t < 8; ++t) th.emplace_back([&] { long s = 0; for (int i = 0; i < 2000; ++i) { IStr copy = shared; IStr piece = copy.slice(i, 50); s += piece[0] == 'k' ? (long)piece.size() : 0; s += copy.hash() == shared.hash(); IStr cat = piece.concat(piece); s += cat.size() == 100; } total += s; });
      for (auto& x : th) x.join(); assert(total == 8L * 2000 * (50 + 1 + 1) && shared.refs() == 1); }
    // ④ 해시 비용: 전체 문자열은 만들 때 한 번만 계산하고 캐시
    { g_hashes = 0; IStr k(std::string(100000, 'h')); for (int i = 0; i < 1000; ++i) (void)k.hash(); assert(g_hashes == 1); }
    // ⑤ 조각이 큰 원본을 붙잡는다: 작은 slice 하나가 1 MB 를 살려 둔다 → compact() 로 놓아 준다
    { std::weak_ptr<const void> watch; IStr small; { IStr big(std::string(1000000, 'B')); watch = big.observer(); small = big.slice(10, 8); assert(small.retainedBytes() == 1000000); }
      assert(!watch.expired() && small.size() == 8);                                                         // 큰 원본은 지역 변수가 사라져도 slice 때문에 살아 있다
      small = small.compact(); assert(watch.expired() && small.retainedBytes() == 8 && small.str() == std::string(8, 'B')); }
    std::cout << "ImmutableString: sharing, interning (300 distinct words -> 300 objects, 0 byte comparisons), 8-thread reads without data races, hash cached once, slice retention and compact() verified" << std::endl;
    return 0;
}
// Time Complexity: 복사 O(1), 연결 O(n+m), 인터닝 평균 O(len), 해시 O(1) (캐시)
// Space Complexity: O(n) (slice 는 원본 버퍼를 공유)
```
# Part 2. 기본 연산 응용
## Palindrome()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cctype>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 회문(palindrome) 여섯 가지를 각각 독립적인 참조 구현과 대조한다.
//  ① 알파벳·숫자만 보고 대소문자를 무시하는 두 포인터 판별  ② 문자 하나를 지워서 회문이 되는가(그리디 한 번 건너뛰기)  ③ 가장 긴 회문 부분 문자열(중심 확장 O(n²)) — 인증서: 회문이고, 더 긴 회문 부분 문자열이 없다
//  ④ 회문 부분 문자열의 개수(중심 확장 vs DP 표)  ⑤ 회문이 되도록 넣어야 하는 최소 글자 수 = n − (가장 긴 회문 부분 수열)  ⑥ 앞에 붙여 만드는 최단 회문(KMP 접두사 함수 한 번, 선형).
bool isPalindrome(const std::string& s) {
    int i = 0, j = (int)s.size() - 1;
    while (i < j) { while (i < j && !std::isalnum((unsigned char)s[i])) ++i; while (i < j && !std::isalnum((unsigned char)s[j])) --j; if (std::tolower((unsigned char)s[i]) != std::tolower((unsigned char)s[j])) return false; ++i; --j; }
    return true;
}
bool refPalindrome(const std::string& s) { std::string f; for (unsigned char c : s) if (std::isalnum(c)) f += (char)std::tolower(c); std::string r(f.rbegin(), f.rend()); return f == r; }
bool plain(const std::string& s, int i, int j) { while (i < j) if (s[i++] != s[j--]) return false; return true; }
bool validPalindromeII(const std::string& s) {                            // 많아야 한 글자를 지워서 회문이 되는가: 처음 어긋난 곳에서 양쪽 중 하나만 건너뛴다
    int i = 0, j = (int)s.size() - 1; while (i < j && s[i] == s[j]) { ++i; --j; } if (i >= j) return true; return plain(s, i + 1, j) || plain(s, i, j - 1);
}
bool bruteII(const std::string& s) { if (plain(s, 0, (int)s.size() - 1)) return true; for (size_t k = 0; k < s.size(); ++k) { std::string t = s; t.erase(k, 1); if (plain(t, 0, (int)t.size() - 1)) return true; } return false; }
std::string longestPalSub(const std::string& s) {
    int n = (int)s.size(), bestL = 0, bestLen = 0; if (n == 0) return "";
    for (int c = 0; c < 2 * n - 1; ++c) { int l = c / 2, r = l + c % 2; while (l >= 0 && r < n && s[l] == s[r]) { --l; ++r; } int len = r - l - 1; if (len > bestLen) { bestLen = len; bestL = l + 1; } }     // 엄격한 > : 가장 왼쪽
    return s.substr(bestL, bestLen);
}
size_t bruteLongest(const std::string& s) { size_t best = s.empty() ? 0 : 1; for (size_t i = 0; i < s.size(); ++i) for (size_t j = i; j < s.size(); ++j) if (plain(s, (int)i, (int)j)) best = std::max(best, j - i + 1); return best; }
long countPal(const std::string& s) { int n = (int)s.size(); long cnt = 0; for (int c = 0; c < 2 * n - 1; ++c) { int l = c / 2, r = l + c % 2; while (l >= 0 && r < n && s[l] == s[r]) { ++cnt; --l; ++r; } } return cnt; }
long countPalDP(const std::string& s) { int n = (int)s.size(); std::vector<std::vector<char>> d(n, std::vector<char>(n, 0)); long cnt = 0; for (int len = 1; len <= n; ++len) for (int i = 0; i + len <= n; ++i) { int j = i + len - 1; d[i][j] = s[i] == s[j] && (len <= 2 || d[i + 1][j - 1]); cnt += d[i][j]; } return cnt; }
int minInsertions(const std::string& s) { int n = (int)s.size(); std::string r(s.rbegin(), s.rend()); std::vector<std::vector<int>> L(n + 1, std::vector<int>(n + 1, 0)); for (int i = 1; i <= n; ++i) for (int j = 1; j <= n; ++j) L[i][j] = s[i - 1] == r[j - 1] ? L[i - 1][j - 1] + 1 : std::max(L[i - 1][j], L[i][j - 1]); return n - L[n][n]; }
int bruteInsertions(const std::string& s) { int n = (int)s.size(), best = 0; for (unsigned m = 1; m < (1u << n); ++m) { std::string t; for (int i = 0; i < n; ++i) if (m >> i & 1) t += s[i]; if (plain(t, 0, (int)t.size() - 1)) best = std::max(best, (int)t.size()); } return n - best; }
std::string shortestPalindrome(const std::string& s) {                   // 앞에 붙여서: 가장 긴 회문 접두사를 찾는다 = (s + '#' + reverse(s)) 의 접두사 함수 마지막 값
    std::string t = s + "#" + std::string(s.rbegin(), s.rend()); std::vector<int> pi(t.size(), 0); for (size_t i = 1; i < t.size(); ++i) { int k = pi[i - 1]; while (k && t[i] != t[k]) k = pi[k - 1]; if (t[i] == t[k]) ++k; pi[i] = k; }
    int keep = pi.back(); std::string r(s.rbegin(), s.rend()); return r.substr(0, s.size() - keep) + s;
}
std::string bruteShortest(const std::string& s) { for (size_t k = s.size() + 1; k-- > 0;) if (plain(s, 0, (int)k - 1)) return std::string(s.rbegin(), s.rend() - k) + s; return s; }

int main() {
    assert(isPalindrome("A man, a plan, a canal: Panama") && isPalindrome("racecar") && isPalindrome("") && isPalindrome("a") && !isPalindrome("hello"));
    std::mt19937 rng(77); const char alpha[] = "aAb1 ,.!B";
    for (int it = 0; it < 200000; ++it) { std::string s(rng() % 13, 'a'); for (char& c : s) c = alpha[rng() % 9]; assert(isPalindrome(s) == refPalindrome(s)); }              // ① 참조: 걸러 낸 뒤 뒤집어 비교
    for (int it = 0; it < 100000; ++it) { std::string s(rng() % 13, 'a'); for (char& c : s) c = (char)('a' + rng() % 3); assert(validPalindromeII(s) == bruteII(s)); }              // ②
    for (int it = 0; it < 30000; ++it) { std::string s(rng() % 31, 'a'); for (char& c : s) c = (char)('a' + rng() % 2); std::string p = longestPalSub(s); assert(p.size() == bruteLongest(s) && plain(p, 0, (int)p.size() - 1) && s.find(p) != std::string::npos); assert(countPal(s) == countPalDP(s)); }          // ③ ④
    { std::string s(1500, 'a'); for (char& c : s) c = (char)('a' + rng() % 2); std::string p = longestPalSub(s); int n = (int)s.size(); std::vector<std::vector<char>> d(n, std::vector<char>(n, 0)); size_t longest = 0;      // 인증서: 표로 모든 부분 문자열을 검사해도 더 긴 회문은 없다
      for (int len = 1; len <= n; ++len) for (int i = 0; i + len <= n; ++i) { int j = i + len - 1; d[i][j] = s[i] == s[j] && (len <= 2 || d[i + 1][j - 1]); if (d[i][j]) longest = len; } assert(p.size() == longest && countPal(s) == countPalDP(s)); }
    for (int it = 0; it < 3000; ++it) { std::string s(rng() % 13, 'a'); for (char& c : s) c = (char)('a' + rng() % 3); assert(minInsertions(s) == bruteInsertions(s)); }                    // ⑤
    for (int it = 0; it < 50000; ++it) { std::string s(rng() % 11, 'a'); for (char& c : s) c = (char)('a' + rng() % 2); std::string r = shortestPalindrome(s); assert(r == bruteShortest(s) && plain(r, 0, (int)r.size() - 1) && r.size() >= s.size() && r.compare(r.size() - s.size(), s.size(), s) == 0); }   // ⑥
    { std::string s(1000000, 'a'); s += 'b'; std::string r = shortestPalindrome(s); assert(r.size() == s.size() + 1 && r.front() == 'b' && r.back() == 'b' && plain(r, 0, (int)r.size() - 1));       // 100 만 글자: 선형 시간
      std::cout << "Palindrome: all six algorithms matched their reference implementations on random inputs; shortest-palindrome on a 10^6-character string is linear" << std::endl; }
    return 0;
}
// Time Complexity: 판별 O(n), 가장 긴 회문 부분 문자열·개수 O(n²), 최소 삽입 O(n²), 최단 회문 O(n)
// Space Complexity: 판별 O(1), 최소 삽입 O(n²), 최단 회문 O(n)
```
## Anagram()
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
#include <unordered_map>
#include <vector>

// 애너그램: 글자 빈도가 같으면 된다. 구현 세 가지(빈도 배열·정렬·다중집합 해시)와 응용을 서로 대조한다.
//  ① 판별 3 가지가 무작위 쌍에서 일치(절반은 섞어서 만든 진짜 애너그램, 절반은 한 글자 바꾼 쌍).  ② 슬라이딩 윈도로 텍스트 안의 모든 애너그램 위치를 O(n) 에 찾는다(무차별과 대조).
//  ③ 그룹핑 키: 정렬한 문자열(정확) / 빈도 서명(정확) / 글자 값의 합(약함 — 'ad' 와 'bc' 가 같다) / Σ mix(c) 64 비트 다중집합 해시(실질적으로 정확) — 거짓 병합 수를 센다.
//  ④ 서로 다른 애너그램의 개수 = n!/Π(빈도!) 를 next_permutation 열거와 대조.
typedef std::uint64_t u64;
static inline u64 mix(u64 x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
bool anagramCount(const std::string& a, const std::string& b) { if (a.size() != b.size()) return false; int cnt[256] = {0}; for (unsigned char c : a) ++cnt[c]; for (unsigned char c : b) if (--cnt[c] < 0) return false; return true; }
bool anagramSort(std::string a, std::string b) { std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end()); return a == b; }
u64 multisetHash(const std::string& s) { u64 h = 0; for (unsigned char c : s) h += mix(c); return h; }                       // 순서와 무관한 합
bool anagramHash(const std::string& a, const std::string& b) { return a.size() == b.size() && multisetHash(a) == multisetHash(b); }   // 확률적 (거짓 양성은 2^-64 수준)
std::vector<size_t> findAnagrams(const std::string& text, const std::string& pat) {   // text 에서 pat 의 애너그램인 모든 윈도 시작 위치, 윈도를 한 칸씩 밀며 불일치 칸 수만 갱신
    std::vector<size_t> res; if (pat.size() > text.size()) return res; int diff[256] = {0}, mismatched = 0; for (unsigned char c : pat) --diff[c];
    for (int c = 0; c < 256; ++c) mismatched += diff[c] != 0;
    auto add = [&](unsigned char c, int d) { mismatched -= diff[c] != 0; diff[c] += d; mismatched += diff[c] != 0; };
    for (size_t i = 0; i < text.size(); ++i) { add((unsigned char)text[i], +1); if (i >= pat.size()) add((unsigned char)text[i - pat.size()], -1); if (i + 1 >= pat.size() && mismatched == 0) res.push_back(i + 1 - pat.size()); }
    return res;
}
std::vector<size_t> bruteFind(const std::string& text, const std::string& pat) { std::vector<size_t> r; for (size_t i = 0; i + pat.size() <= text.size(); ++i) if (anagramSort(text.substr(i, pat.size()), pat)) r.push_back(i); return r; }
std::string signature(const std::string& w) { int cnt[26] = {0}; for (char c : w) ++cnt[c - 'a']; std::string k; for (int i = 0; i < 26; ++i) { k += (char)('a' + cnt[i] % 26); k += '#'; } return k; }
std::string canonical(std::string w) { std::sort(w.begin(), w.end()); return w; }

int main() {
    assert(anagramCount("listen", "silent") && !anagramCount("hello", "world") && !anagramCount("a", "ab"));
    std::mt19937 rng(5); long yes = 0;
    for (int it = 0; it < 300000; ++it) {
        std::string a(1 + rng() % 12, 'a'); for (char& c : a) c = (char)('a' + rng() % 5); std::string b = a; std::shuffle(b.begin(), b.end(), rng); if (rng() % 2) b[rng() % b.size()] = (char)('a' + rng() % 5);
        bool x = anagramCount(a, b), y = anagramSort(a, b), z = anagramHash(a, b); assert(x == y && y == z); yes += x;
    }
    assert(yes > 100000 && yes < 250000);                                                                           // 두 부류가 모두 충분히 섞여 있다
    for (int it = 0; it < 60000; ++it) { std::string t(rng() % 31, 'a'), p(1 + rng() % 5, 'a'); for (char& c : t) c = (char)('a' + rng() % 3); for (char& c : p) c = (char)('a' + rng() % 3); assert(findAnagrams(t, p) == bruteFind(t, p)); }       // ② 슬라이딩 윈도
    { std::string t(1000000, 'a'), p = "ab"; for (size_t i = 0; i < t.size(); i += 3) t[i] = 'b'; std::vector<size_t> r = findAnagrams(t, p); assert(!r.empty()); for (size_t i : r) assert(canonical(t.substr(i, 2)) == "ab"); }
    // ③ 그룹핑: 어휘 5 만 개 (길이 3~6, 글자 8 종 → 애너그램이 많이 생긴다)
    std::vector<std::string> words; for (int i = 0; i < 50000; ++i) { std::string w(3 + rng() % 4, 'a'); for (char& c : w) c = (char)('a' + rng() % 8); words.push_back(w); }
    std::map<std::string, std::vector<int>> exact; for (int i = 0; i < (int)words.size(); ++i) exact[canonical(words[i])].push_back(i);
    std::map<std::string, std::vector<int>> bySig; for (int i = 0; i < (int)words.size(); ++i) bySig[signature(words[i])].push_back(i);
    std::unordered_map<u64, std::vector<int>> byHash; std::map<int, std::vector<int>> byAdd; for (int i = 0; i < (int)words.size(); ++i) { byHash[multisetHash(words[i])].push_back(i); int sum = 0; for (char c : words[i]) sum += c; byAdd[sum * 100 + (int)words[i].size()].push_back(i); }
    auto partition = [](auto& m) { std::set<std::vector<int>> p; for (auto& kv : m) p.insert(kv.second); return p; };
    assert(partition(exact) == partition(bySig) && partition(exact) == partition(byHash));                           // 서명·다중집합 해시는 정렬 키와 같은 분할
    long falseMerges = 0; for (auto& kv : byAdd) { std::set<std::string> distinct; for (int i : kv.second) distinct.insert(canonical(words[i])); falseMerges += (long)distinct.size() - 1; }
    assert(falseMerges > 1000);                                                                                      // 글자 값의 합은 서로 다른 다중집합을 많이 합쳐 버린다
    std::cout << "Anagram: " << words.size() << " words fell into " << exact.size() << " exact groups; the character-sum key merged " << falseMerges << " distinct multisets by mistake while the 64-bit multiset hash produced the identical partition" << std::endl;
    // ④ 서로 다른 애너그램 개수 n!/Π(빈도!) vs next_permutation 열거
    for (int it = 0; it < 2000; ++it) { std::string s(1 + rng() % 8, 'a'); for (char& c : s) c = (char)('a' + rng() % 4); std::sort(s.begin(), s.end()); long brute = 0; std::string t = s; do ++brute; while (std::next_permutation(t.begin(), t.end()));
        long num = 1; for (int i = 2; i <= (int)s.size(); ++i) num *= i; int cnt[256] = {0}; for (unsigned char c : s) ++cnt[c]; for (int c = 0; c < 256; ++c) for (int i = 2; i <= cnt[c]; ++i) num /= i; assert(brute == num); }
    return 0;
}
// Time Complexity: 판별 O(n), 윈도 탐색 O(|text| + |pattern|), 그룹핑 O(총 길이) (서명·해시) / O(총 길이 · log 길이) (정렬)
// Space Complexity: O(알파벳) (판별), O(총 길이) (그룹핑)
```
## RunLengthEncoding()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cctype>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 런 길이 부호화(RLE): 연속된 같은 바이트를 (바이트, 반복 횟수)로 줄인다. 반복이 많은 데이터(단색 이미지, BWT 결과)에서 효과적이지만 반복이 없으면 오히려 커진다.
//  ① 교과서식 텍스트 RLE("a3b1")는 입력에 숫자가 있으면 복원할 수 없다 → 반례를 무작위로 센다.   ② PackBits(TIFF·Apple): 머리 바이트 h — 0..127: 뒤따르는 h+1 바이트를 그대로(literal),
//  129..255: 다음 한 바이트를 257−h (2..128) 번 반복.  어떤 입력이든 정확히 복원되고 최악의 확장은 ⌈n/128⌉ 바이트.   ③ 단순 (개수, 값) 쌍은 반복이 없으면 정확히 2 배.
//  ④ 디코더는 잘린·악의적 입력에도 안전해야 한다(출력 크기 상한, 경계 검사).
std::string textEncode(const std::string& s) { std::string out; for (size_t i = 0; i < s.size();) { size_t j = i; while (j < s.size() && s[j] == s[i]) ++j; out += s[i]; out += std::to_string(j - i); i = j; } return out; }
bool textDecode(const std::string& e, std::string& out, size_t maxOut = 1 << 20) {              // 숫자가 입력에 섞이면 "a111" 처럼 개수가 엄청나게 커질 수 있어 출력 상한이 필요하다
    out.clear(); for (size_t i = 0; i < e.size();) { char c = e[i++]; size_t n = 0; while (i < e.size() && std::isdigit((unsigned char)e[i])) { n = n * 10 + (size_t)(e[i++] - '0'); if (n > maxOut) return false; } if (out.size() + n > maxOut) return false; out.append(n, c); }
    return true; }
typedef std::vector<std::uint8_t> Bytes;
Bytes packEncode(const Bytes& in) {
    Bytes out; size_t i = 0, n = in.size();
    while (i < n) {
        size_t r = 1; while (i + r < n && in[i + r] == in[i] && r < 128) ++r;
        if (r >= 3) { out.push_back((std::uint8_t)(257 - r)); out.push_back(in[i]); i += r; continue; }                  // 반복 3 이상은 반복 블록
        size_t j = i; while (j < n && j - i < 128) { if (j + 2 < n && in[j] == in[j + 1] && in[j] == in[j + 2]) break; ++j; }   // 다음 반복이 시작되기 전까지 literal
        out.push_back((std::uint8_t)(j - i - 1)); out.insert(out.end(), in.begin() + i, in.begin() + j); i = j;
    }
    return out;
}
bool packDecode(const Bytes& in, Bytes& out, size_t maxOut = (size_t)1 << 30) {      // 잘렸거나 출력이 maxOut 을 넘으면 false
    out.clear(); size_t i = 0;
    while (i < in.size()) { std::uint8_t h = in[i++];
        if (h < 128) { size_t len = (size_t)h + 1; if (i + len > in.size() || out.size() + len > maxOut) return false; out.insert(out.end(), in.begin() + i, in.begin() + i + len); i += len; }
        else if (h > 128) { size_t len = 257 - (size_t)h; if (i >= in.size() || out.size() + len > maxOut) return false; out.insert(out.end(), len, in[i++]); }
        /* h == 128: 아무 일도 하지 않음 */ }
    return true;
}
Bytes pairEncode(const Bytes& in) { Bytes out; for (size_t i = 0; i < in.size();) { size_t j = i; while (j < in.size() && in[j] == in[i] && j - i < 255) ++j; out.push_back((std::uint8_t)(j - i)); out.push_back(in[i]); i = j; } return out; }

int main() {
    std::string tmp; assert(textEncode("aaabccdddd") == "a3b1c2d4" && textDecode("a3b1c2d4", tmp) && tmp == "aaabccdddd" && textEncode("abc").size() > 3);
    std::mt19937 rng(21); long textBroken = 0, total = 0;
    for (int it = 0; it < 20000; ++it) { std::string s(1 + rng() % 8, 'a'); for (char& c : s) c = "ab12"[rng() % 4]; std::string back; textBroken += !textDecode(textEncode(s), back) || back != s; ++total; }
    assert(textBroken > total / 4);                                                                                   // 숫자가 들어간 입력은 복원이 깨진다 (예: "a1" → "a111" → 'a' 111 개, "1212…" → 개수가 10^15)
    auto gen = [&](int kind) { Bytes b; size_t n = rng() % 600; if (kind == 0) { b.resize(n); for (auto& x : b) x = (std::uint8_t)rng(); }                                  // 균등 난수 (비압축성)
        else if (kind == 1) { b.resize(n); for (auto& x : b) x = (std::uint8_t)(rng() % 2); }                                                                                   // 저엔트로피
        else { while (b.size() < n) { size_t run = 1 + rng() % (kind == 2 ? 300 : 4); b.insert(b.end(), run, (std::uint8_t)rng()); } } return b; };            // 긴 런 / 짧은 런
    for (int it = 0; it < 100000; ++it) {
        Bytes in = gen(it % 4), enc = packEncode(in), dec; assert(packDecode(enc, dec) && dec == in);                                                      // ② 왕복
        assert(enc.size() <= in.size() + (in.size() + 127) / 128);                                                                                        // 최악의 확장: 128 바이트마다 머리 1 바이트
        Bytes pairs = pairEncode(in); if (it % 4 == 0 && in.size() > 50) assert(pairs.size() > enc.size());
    }
    { Bytes zeros(1 << 20, 0), enc = packEncode(zeros), dec; assert(enc.size() == 2 * (zeros.size() / 128) && packDecode(enc, dec) && dec == zeros);          // 같은 바이트 1 MiB → 16 KiB (1/64)
      Bytes alt(1 << 20); for (size_t i = 0; i < alt.size(); ++i) alt[i] = (std::uint8_t)(i % 2); Bytes e2 = packEncode(alt); assert(e2.size() == alt.size() + alt.size() / 128 && pairEncode(alt).size() == 2 * alt.size()); }      // 교대 패턴: PackBits +0.8 %, (개수,값) 쌍은 +100 %
    // ④ 디코더 안전성: 임의 바이트열을 넣어도 경계를 넘지 않고 출력 상한을 지킨다
    for (int it = 0; it < 100000; ++it) { Bytes junk(rng() % 40); for (auto& x : junk) x = (std::uint8_t)rng(); Bytes out; bool ok = packDecode(junk, out, 4096); assert(!ok || out.size() <= 4096); }
    Bytes trunc = packEncode(Bytes(300, 7)); trunc.pop_back(); Bytes sink; assert(!packDecode(trunc, sink));                                                // 잘린 입력은 거부
    std::cout << "RunLengthEncoding: text RLE failed to round-trip " << textBroken << " of " << total << " random inputs over {a,b,1,2}; PackBits round-tripped 100000 random inputs (worst expansion <= ceil(n/128)), 1 MiB of zeros -> 16 KiB, alternating bytes +0.8% vs +100% for (count,value) pairs" << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
# Part 3. 인코딩
## ASCII부터 Unicode까지
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// ASCII(7비트, 128자) → 각국 확장 코드페이지(Latin-1 은 U+0000..U+00FF 와 일대일) → Unicode(코드 포인트 U+0000 ~ U+10FFFF)와 그 인코딩 UTF-8/16/32.
//  모든 스칼라 값(서러게이트 제외 1,112,064 개)에 대해 세 인코딩을 전수 왕복 검사하고, 다음을 확인한다:
//  · UTF-8 은 ASCII 와 바이트가 같다(상위 호환).  · UTF-8 의 바이트 사전식 순서 = 코드 포인트 순서.  UTF-16 의 코드 유닛 순서는 U+E000..U+FFFF 와 보충 평면(≥ U+10000)에서 *어긋난다*.
//  · BOM(EF BB BF / FE FF / FF FE)으로 인코딩·바이트 순서 판별.  · 모지바케: UTF-8 바이트를 Latin-1 로 읽었다 다시 UTF-8 로 쓰면 글자가 깨지지만 Latin-1 이 무손실이라 정확히 되돌릴 수 있다.
typedef std::uint32_t u32; typedef std::uint16_t u16;
std::string utf8Encode(u32 cp) {
    std::string s; if (cp < 0x80) s += (char)cp; else if (cp < 0x800) { s += (char)(0xC0 | cp >> 6); s += (char)(0x80 | (cp & 0x3F)); }
    else if (cp < 0x10000) { s += (char)(0xE0 | cp >> 12); s += (char)(0x80 | (cp >> 6 & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    else { s += (char)(0xF0 | cp >> 18); s += (char)(0x80 | (cp >> 12 & 0x3F)); s += (char)(0x80 | (cp >> 6 & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    return s;
}
bool utf8Decode(const std::string& s, size_t& i, u32& cp) {
    unsigned char c = s[i]; int len = c < 0x80 ? 1 : c >= 0xF8 ? 0 : c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 0; if (!len || i + len > s.size()) return false;
    u32 v = len == 1 ? c : c & (0x3F >> (len - 1)); for (int k = 1; k < len; ++k) { if (((unsigned char)s[i + k] & 0xC0) != 0x80) return false; v = v << 6 | ((unsigned char)s[i + k] & 0x3F); }
    if (v < (len == 2 ? 0x80u : len == 3 ? 0x800u : len == 4 ? 0x10000u : 0u) || v > 0x10FFFF || (v >= 0xD800 && v <= 0xDFFF)) return false; cp = v; i += len; return true;
}
std::vector<u16> utf16Encode(u32 cp) { if (cp < 0x10000) return {(u16)cp}; u32 v = cp - 0x10000; return {(u16)(0xD800 + (v >> 10)), (u16)(0xDC00 + (v & 0x3FF))}; }          // 서러게이트 쌍
bool utf16Decode(const std::vector<u16>& u, size_t& i, u32& cp) {
    u16 a = u[i]; if (a < 0xD800 || a > 0xDFFF) { cp = a; i += 1; return true; } if (a >= 0xDC00 || i + 1 >= u.size() || u[i + 1] < 0xDC00 || u[i + 1] > 0xDFFF) return false;
    cp = 0x10000 + (((u32)a - 0xD800) << 10) + (u[i + 1] - 0xDC00); i += 2; return true;
}
std::string latin1ToUtf8(const std::string& bytes) { std::string r; for (unsigned char c : bytes) r += utf8Encode(c); return r; }                         // Latin-1 바이트 = 코드 포인트
std::string utf8ToLatin1(const std::string& s) { std::string r; size_t i = 0; u32 cp; while (i < s.size()) { bool ok = utf8Decode(s, i, cp); assert(ok && cp < 256); (void)ok; r += (char)cp; } return r; }

int main() {
    // ① 모든 스칼라 값 전수: UTF-8 / UTF-16 / UTF-32 길이와 왕복
    long scalars = 0, bytes8 = 0, units16 = 0;
    for (u32 cp = 0; cp <= 0x10FFFF; ++cp) {
        if (cp >= 0xD800 && cp <= 0xDFFF) { std::string bad = std::string("\xED") + (char)(0x80 | (cp >> 6 & 0x3F)) + (char)(0x80 | (cp & 0x3F)); size_t i = 0; u32 out; assert(!utf8Decode(bad, i, out)); std::vector<u16> lone = {(u16)cp}; i = 0; assert(!utf16Decode(lone, i, out)); continue; }
        std::string s = utf8Encode(cp); size_t i = 0; u32 back; assert(utf8Decode(s, i, back) && back == cp && i == s.size());
        std::vector<u16> u = utf16Encode(cp); size_t k = 0; assert(utf16Decode(u, k, back) && back == cp && k == u.size() && (u.size() == (cp > 0xFFFF ? 2u : 1u)));
        assert((cp < 0x80) == (s.size() == 1) && (cp < 0x80 ? s[0] == (char)cp : true));                                                      // ASCII: UTF-8 == ASCII
        ++scalars; bytes8 += (long)s.size(); units16 += (long)u.size();
    }
    assert(scalars == 1112064);
    // ② 정렬 순서: UTF-8 바이트 순서 = 코드 포인트 순서, UTF-16 코드 유닛 순서는 일부 쌍에서 어긋난다
    std::mt19937 rng(2); long mismatches16 = 0, pairs = 0;
    auto randScalar = [&]() { u32 c; do { c = rng() % 3 == 0 ? 0xE000 + rng() % 0x2000 : rng() % 3 == 0 ? 0x10000 + rng() % 0x100000 : rng() % 0x110000; } while (c >= 0xD800 && c <= 0xDFFF); return c; };
    for (int it = 0; it < 2000000; ++it) {
        u32 a = randScalar(), b = randScalar(); std::string sa = utf8Encode(a), sb = utf8Encode(b); assert((sa < sb) == (a < b) && (sa == sb) == (a == b));         // std::string 비교는 unsigned 바이트 사전식
        std::vector<u16> ua = utf16Encode(a), ub = utf16Encode(b); bool less16 = std::lexicographical_compare(ua.begin(), ua.end(), ub.begin(), ub.end()); ++pairs;
        if (less16 != (a < b) && a != b) { ++mismatches16; assert((a >= 0xE000 && a <= 0xFFFF && b >= 0x10000) || (b >= 0xE000 && b <= 0xFFFF && a >= 0x10000)); }       // 어긋나는 쌍은 정확히 이 경우뿐
    }
    assert(mismatches16 > 10000);
    { std::vector<u16> x = utf16Encode(0xFFFD), y = utf16Encode(0x10000); assert(std::lexicographical_compare(y.begin(), y.end(), x.begin(), x.end()) && 0x10000 > 0xFFFD); }    // U+10000 이 U+FFFD 보다 "앞"에 정렬된다 (UTF-16)
    // ③ BOM 으로 인코딩 판별
    auto sniff = [](const std::string& b) { if (b.size() >= 3 && b.compare(0, 3, "\xEF\xBB\xBF") == 0) return std::string("UTF-8"); if (b.size() >= 2 && b.compare(0, 2, "\xFE\xFF") == 0) return std::string("UTF-16BE"); if (b.size() >= 2 && b.compare(0, 2, "\xFF\xFE") == 0) return std::string("UTF-16LE"); return std::string("unknown"); };
    assert(sniff("\xEF\xBB\xBFhi") == "UTF-8" && sniff("\xFE\xFF\x00h") == "UTF-16BE" && sniff("\xFF\xFEh\x00") == "UTF-16LE" && sniff("hi") == "unknown");
    // ④ 모지바케: UTF-8 바이트를 Latin-1 로 읽으면 깨지고(é → Ã©), 정확히 되돌릴 수 있다
    { std::string e = utf8Encode(0xE9); assert(e == "\xC3\xA9"); std::string garbled = latin1ToUtf8(e); assert(garbled == utf8Encode(0xC3) + utf8Encode(0xA9) && garbled.size() == 4 && utf8ToLatin1(garbled) == e); }
    for (int it = 0; it < 20000; ++it) { std::string s; for (size_t n = rng() % 12; n > 0; --n) s += utf8Encode(randScalar()); assert(utf8ToLatin1(latin1ToUtf8(s)) == s && latin1ToUtf8(s).size() >= s.size()); }          // 모든 올바른 UTF-8 에서 무손실
    long invalid = 0; for (int it = 0; it < 20000; ++it) { std::string l(1 + rng() % 6, 'a'); for (char& c : l) c = (char)(rng() % 256); size_t i = 0; u32 cp; bool ok = true; while (i < l.size() && ok) ok = utf8Decode(l, i, cp); invalid += !ok; }       // 반대로 Latin-1 텍스트를 UTF-8 로 읽으면 대부분 오류
    assert(invalid > 12000);
    std::cout << "ASCII->Unicode: " << scalars << " scalar values round-tripped in UTF-8/16 (" << (double)bytes8 / scalars << " bytes and " << (double)units16 / scalars << " UTF-16 units on average); UTF-8 byte order matched code point order in all " << pairs << " random pairs while UTF-16 code-unit order disagreed in " << mismatches16 << "; random Latin-1 bytes were invalid UTF-8 " << invalid << "/20000 times" << std::endl;
    return 0;
}
// Time Complexity: 부호화·복호화 O(1)/코드 포인트
// Space Complexity: O(1)
```
## UTF-8과 UTF-16의 차이
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// UTF-8: 1~4바이트 가변, ASCII 호환, 바이트 순서 문제 없음.   UTF-16: 2바이트 단위, U+10000 이상은 서로게이트 쌍(4바이트).
// 같은 글자라도 크기가 다르다: 영어는 UTF-8 이 작고, 한글은 UTF-16(2B)이 UTF-8(3B)보다 작다
std::vector<uint16_t> utf16Encode(uint32_t cp) {
    if (cp < 0x10000) return {(uint16_t)cp};
    cp -= 0x10000;
    return {(uint16_t)(0xD800 + (cp >> 10)), (uint16_t)(0xDC00 + (cp & 0x3FF))};    // 상위/하위 서로게이트
}
uint32_t utf16Decode(const std::vector<uint16_t>& u) {
    if (u.size() == 1) return u[0];
    return 0x10000 + ((u[0] - 0xD800) << 10) + (u[1] - 0xDC00);
}
size_t utf8Size(uint32_t cp) { return cp < 0x80 ? 1 : cp < 0x800 ? 2 : cp < 0x10000 ? 3 : 4; }

int main() {
    assert(utf8Size('A') == 1 && utf16Encode('A').size() * 2 == 2);              // 영어: UTF-8 이 작다
    assert(utf8Size(0xD55C) == 3 && utf16Encode(0xD55C).size() * 2 == 2);        // 한글: UTF-16 이 작다
    assert(utf8Size(0x1F600) == 4 && utf16Encode(0x1F600).size() * 2 == 4);      // 이모지: 같다
    auto pair = utf16Encode(0x1F600);
    assert(pair[0] == 0xD83D && pair[1] == 0xDE00);                               // 😀 의 서로게이트 쌍
    assert(utf16Decode(pair) == 0x1F600);
    for (uint32_t cp : {0x41u, 0xD55Cu, 0x10000u, 0x10FFFFu}) assert(utf16Decode(utf16Encode(cp)) == cp);
    std::cout << "UTF-16 surrogate pair for U+1F600: " << std::hex << pair[0] << " " << pair[1] << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## UTF8Validate()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <cassert>

// UTF-8 검증: 선행 바이트가 알려 주는 길이만큼 연속 바이트(10xxxxxx)가 와야 하고,
// (1) 과잉 부호화(overlong)  (2) 서로게이트 영역 U+D800~DFFF  (3) U+10FFFF 초과  는 모두 무효다 (보안 취약점의 단골 원인)
bool validUtf8(const std::string& s) {
    for (size_t i = 0; i < s.size();) {
        unsigned char c = s[i]; int len; uint32_t cp, minCp;
        if (c < 0x80) { i++; continue; }
        else if ((c & 0xE0) == 0xC0) { len = 2; cp = c & 0x1F; minCp = 0x80; }
        else if ((c & 0xF0) == 0xE0) { len = 3; cp = c & 0x0F; minCp = 0x800; }
        else if ((c & 0xF8) == 0xF0) { len = 4; cp = c & 0x07; minCp = 0x10000; }
        else return false;                                       // 연속 바이트가 선행 위치에 있거나 0xF8 이상
        if (i + len > s.size()) return false;                    // 잘림
        for (int k = 1; k < len; k++) {
            unsigned char d = s[i + k];
            if ((d & 0xC0) != 0x80) return false;
            cp = cp << 6 | (d & 0x3F);
        }
        if (cp < minCp || (cp >= 0xD800 && cp <= 0xDFFF) || cp > 0x10FFFF) return false;
        i += len;
    }
    return true;
}

int main() {
    assert(validUtf8("hello") && validUtf8("한글😀"));
    assert(!validUtf8(std::string("\xC0\x80", 2)));              // overlong NUL
    assert(!validUtf8(std::string("\xED\xA0\x80", 3)));          // U+D800 서로게이트
    assert(!validUtf8(std::string("\xF4\x90\x80\x80", 4)));      // U+110000 범위 초과
    assert(!validUtf8(std::string("\xE2\x82", 2)));              // 잘린 시퀀스
    assert(!validUtf8(std::string("\x80", 1)));                  // 선행 위치의 연속 바이트
    std::cout << "UTF8Validate verified." << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(1)
```
# Part 4. 동적 문자열
## Rope()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 로프(Rope): 긴 문자열을 이진 트리로 표현한다. 리프는 짧은 문자열(≤ LEAF), 내부 노드는 왼쪽 부분 트리의 길이로 색인을 안내한다.
// 노드는 *불변*이라 편집해도 원본이 그대로 남는다(영속, 구조 공유).  연결·분할을 AVL 식 join 으로 하여 높이를 O(log n) 으로 유지 → 색인·분할·삽입·삭제가 모두 O(log n).
//  검증: ① std::string 과 무작위 편집(삽입·삭제·부분 문자열·붙이기·대체)을 매 단계 대조  ② 모든 노드에서 |높이 차| ≤ 1 (AVL 불변식), 높이 ≤ 1.45·log2(리프 수) + 2  ③ 과거 버전 200 개가 끝까지 그대로(영속성)
//  ④ 균형 없이 이어 붙이면 높이가 n 이 되지만 join 은 O(log n)  ⑤ 100 만 글자 문서의 편집.
const size_t LEAF = 32;
struct Node; typedef std::shared_ptr<const Node> P;
struct Node { P l, r; std::string s; size_t size; int height; };           // 리프: l, r 가 비어 있고 s 사용. 내부: s 비어 있음
size_t sizeOf(const P& n) { return n ? n->size : 0; }
int heightOf(const P& n) { return n ? n->height : -1; }
bool isLeaf(const P& n) { return !n->l && !n->r; }
P leaf(std::string s) { size_t n = s.size(); return std::make_shared<const Node>(Node{nullptr, nullptr, std::move(s), n, 0}); }
P node(P l, P r) { size_t n = sizeOf(l) + sizeOf(r); int h = 1 + std::max(heightOf(l), heightOf(r)); return std::make_shared<const Node>(Node{std::move(l), std::move(r), "", n, h}); }
P balance(const P& l, const P& r) {                                           // |h(l) − h(r)| ≤ 2 인 두 트리를 AVL 회전으로 합친다
    if (heightOf(l) > heightOf(r) + 1) { if (heightOf(l->l) >= heightOf(l->r)) return node(l->l, node(l->r, r)); return node(node(l->l, l->r->l), node(l->r->r, r)); }
    if (heightOf(r) > heightOf(l) + 1) { if (heightOf(r->r) >= heightOf(r->l)) return node(node(l, r->l), r->r); return node(node(l, r->l->l), node(r->l->r, r->r)); }
    return node(l, r);
}
P join(const P& a, const P& b) {                                              // a + b, O(|h(a) − h(b)| + 1)
    if (!a) return b; if (!b) return a;
    if (isLeaf(a) && isLeaf(b) && a->size + b->size <= LEAF) return leaf(a->s + b->s);                    // 작은 리프끼리는 합친다
    int ha = heightOf(a), hb = heightOf(b);
    if (ha > hb + 1) return balance(a->l, join(a->r, b));
    if (hb > ha + 1) return balance(join(a, b->l), b->r);
    return node(a, b);
}
std::pair<P, P> split(const P& n, size_t i) {                                 // [0, i) 와 [i, size)
    if (!n || i == 0) return {nullptr, n}; if (i >= n->size) return {n, nullptr};
    if (isLeaf(n)) return {leaf(n->s.substr(0, i)), leaf(n->s.substr(i))};
    size_t w = sizeOf(n->l); if (i < w) { auto t = split(n->l, i); return {t.first, join(t.second, n->r)}; }
    if (i == w) return {n->l, n->r}; auto t = split(n->r, i - w); return {join(n->l, t.first), t.second};
}
P fromString(const std::string& s) { std::vector<P> v; for (size_t i = 0; i < s.size(); i += LEAF) v.push_back(leaf(s.substr(i, LEAF))); if (v.empty()) return nullptr;
    while (v.size() > 1) { std::vector<P> w; for (size_t i = 0; i + 1 < v.size(); i += 2) w.push_back(join(v[i], v[i + 1])); if (v.size() % 2) w.push_back(v.back()); v.swap(w); } return v[0]; }        // 아래에서 위로 쌍으로 join (남는 하나도 join 이 균형을 맞춘다)
char at(const P& n, size_t i) { const Node* c = n.get(); while (c->l || c->r) { size_t w = sizeOf(c->l); if (i < w) c = c->l.get(); else { i -= w; c = c->r.get(); } } return c->s[i]; }
void collect(const P& n, std::string& out) { std::vector<const Node*> st; if (n) st.push_back(n.get()); while (!st.empty()) { const Node* c = st.back(); st.pop_back(); if (!c->l && !c->r) out += c->s; else { if (c->r) st.push_back(c->r.get()); if (c->l) st.push_back(c->l.get()); } } }
std::string str(const P& n) { std::string s; collect(n, s); return s; }
P insert(const P& n, size_t pos, const std::string& s) { auto t = split(n, pos); return join(join(t.first, fromString(s)), t.second); }
P erase(const P& n, size_t pos, size_t len) { auto a = split(n, pos); auto b = split(a.second, len); return join(a.first, b.second); }
P substr(const P& n, size_t pos, size_t len) { auto a = split(n, pos); return split(a.second, len).first; }
bool check(const P& n, size_t& leaves) {                                      // 불변식: 크기·높이 정확, AVL 균형, 리프는 비어 있지 않고 ≤ LEAF
    if (!n) return true; if (isLeaf(n)) { ++leaves; return n->height == 0 && n->size == n->s.size() && n->size >= 1 && n->size <= LEAF; }
    return n->l && n->r && n->size == n->l->size + n->r->size && n->height == 1 + std::max(n->l->height, n->r->height) && std::abs(n->l->height - n->r->height) <= 1 && check(n->l, leaves) && check(n->r, leaves);
}

int main() {
    // 원래 예
    P doc = join(leaf("Hello, "), leaf("world!")); assert(sizeOf(doc) == 13 && at(doc, 7) == 'w');
    P edited = insert(doc, 7, "beautiful "); assert(str(edited) == "Hello, beautiful world!" && str(doc) == "Hello, world!");               // 원본은 그대로 (영속성)
    // ① 무작위 편집 vs std::string (과거 버전 200 개를 보관해 ③ 영속성도 확인)
    std::mt19937 rng(55); std::string ref; P rope = nullptr; std::vector<std::pair<P, std::string>> history;
    auto randStr = [&](size_t n) { std::string s(n, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); return s; };
    for (int op = 0; op < 4000; ++op) {
        int t = (int)(rng() % 6); size_t n = ref.size();
        if (t <= 1 || n < 5) { size_t pos = rng() % (n + 1); std::string x = randStr(rng() % 90); rope = insert(rope, pos, x); ref.insert(pos, x); }
        else if (t == 2) { size_t pos = rng() % n, len = rng() % std::min<size_t>(80, n - pos + 1); rope = erase(rope, pos, len); ref.erase(pos, len); }
        else if (t == 3) { std::string x = randStr(1 + rng() % 40); rope = join(rope, fromString(x)); ref += x; }                                              // 붙이기
        else if (t == 4) { std::string x = randStr(1 + rng() % 40); rope = join(fromString(x), rope); ref = x + ref; }                                          // 앞에 붙이기
        else { size_t pos = rng() % n, len = rng() % (n - pos + 1); assert(str(substr(rope, pos, len)) == ref.substr(pos, len)); }
        size_t leaves = 0; assert(sizeOf(rope) == ref.size() && check(rope, leaves)); if (rope) assert(rope->height <= 1.45 * std::log2((double)std::max<size_t>(leaves, 1)) + 2);   // ② 불변식·높이 상한
        if (ref.size()) { size_t i = rng() % ref.size(); assert(at(rope, i) == ref[i]); }
        if (op % 20 == 0) history.emplace_back(rope, ref);
        if (op % 400 == 0) assert(str(rope) == ref);
    }
    assert(str(rope) == ref);
    for (auto& h : history) assert(str(h.first) == h.second);                                                                                                   // ③ 과거 버전은 전부 그대로
    // ④ 균형 없는 이어 붙이기 vs join: 글자를 하나씩 100000 번 붙인다
    { P chain = nullptr, bal = nullptr; for (int i = 0; i < 20000; ++i) { chain = chain ? node(chain, leaf("x")) : leaf("x"); bal = join(bal, leaf("x")); }
      assert(chain->height == 19999 && bal->height <= 30 && sizeOf(chain) == 20000 && sizeOf(bal) == 20000 && str(bal) == std::string(20000, 'x')); }          // 편향된 트리의 높이는 n−1, 균형 트리는 O(log n)
    // ⑤ 100 만 글자 문서: 편집 2000 번 (std::string 은 매번 O(n) 이동)
    { std::string big = randStr(1000000); P r = fromString(big); size_t leaves = 0; assert(check(r, leaves) && r->height <= 17);
      for (int op = 0; op < 2000; ++op) { size_t pos = rng() % big.size(); if (rng() % 2) { std::string x = randStr(1 + rng() % 200); r = insert(r, pos, x); big.insert(pos, x); } else { size_t len = rng() % std::min<size_t>(300, big.size() - pos + 1); r = erase(r, pos, len); big.erase(pos, len); }
        assert(sizeOf(r) == big.size()); for (int k = 0; k < 20; ++k) { size_t i = rng() % big.size(); assert(at(r, i) == big[i]); } }
      leaves = 0; assert(check(r, leaves) && str(r) == big);
      std::cout << "Rope: " << history.size() << " historical versions stayed intact; AVL invariants held after every edit; 10^6-character document survived 2000 edits (height " << r->height << ", " << leaves << " leaves)" << std::endl; }
    return 0;
}
// Time Complexity: 색인·분할·삽입·삭제·붙이기 O(log n)
// Space Complexity: O(n), 편집마다 O(log n) 새 노드 (나머지는 공유)
```
## GapBuffer()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 갭 버퍼: 커서 위치에 "빈 구간(gap)"을 두고 그 앞뒤에 텍스트를 저장한다. (Emacs 의 편집 버퍼)
// 커서 근처 삽입·삭제는 O(1), 커서를 옮기면 이동 거리만큼 문자를 갭 반대편으로 옮긴다
class GapBuffer {
    std::vector<char> buf; size_t gs, ge;                       // 갭 = [gs, ge)
    void ensure(size_t extra) {
        if (ge - gs >= extra) return;
        size_t oldCap = buf.size(), newCap = std::max(oldCap * 2, oldCap + extra);
        buf.resize(newCap);
        size_t tail = oldCap - ge;
        for (size_t i = 0; i < tail; i++) buf[newCap - 1 - i] = buf[oldCap - 1 - i];     // 뒤쪽 텍스트를 끝으로 밀기
        ge = newCap - tail;
    }
public:
    explicit GapBuffer(size_t cap = 8) : buf(cap), gs(0), ge(cap) {}
    size_t size() const { return buf.size() - (ge - gs); }
    size_t cursor() const { return gs; }
    void move(size_t pos) {                                      // 커서를 pos 로 이동 (갭도 함께 이동)
        while (gs > pos) buf[--ge] = buf[--gs];
        while (gs < pos) buf[gs++] = buf[ge++];
    }
    void insert(char c) { ensure(1); buf[gs++] = c; }
    void erase() { if (gs > 0) gs--; }                           // 백스페이스: 갭을 넓히기만 하면 된다
    std::string str() const { return std::string(buf.begin(), buf.begin() + gs) + std::string(buf.begin() + ge, buf.end()); }
};

int main() {
    GapBuffer g(4);
    for (char c : std::string("Hello world")) g.insert(c);      // 용량 4 -> 자동 확장
    assert(g.str() == "Hello world");
    g.move(5);
    for (char c : std::string(",")) g.insert(c);
    assert(g.str() == "Hello, world");
    g.erase();
    assert(g.str() == "Hello world");
    g.move(0); g.insert('>');
    assert(g.str() == ">Hello world" && g.size() == 12);
    std::cout << "GapBuffer: " << g.str() << std::endl;
    return 0;
}
// Time Complexity: 커서 근처 삽입/삭제 O(1), 이동 O(거리)
// Space Complexity: O(n + gap)
```
## PieceTable()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 피스 테이블(VS Code, Word): 원본 파일 버퍼(읽기 전용)와 추가 버퍼(append-only)를 두고,
// 문서는 "어느 버퍼의 어디부터 몇 글자"인 조각(piece)들의 목록으로 표현한다. 편집은 조각 목록만 바꾸므로 텍스트 복사가 없고 undo 가 쉽다
struct Piece { int buf; size_t start, len; };               // buf 0 = original, 1 = added
class PieceTable {
    std::string orig, added;
    std::vector<Piece> pieces;
public:
    explicit PieceTable(const std::string& text) : orig(text) { if (!text.empty()) pieces.push_back({0, 0, text.size()}); }
    void insert(size_t pos, const std::string& text) {
        size_t start = added.size(); added += text;
        size_t off = 0;
        for (size_t i = 0; i <= pieces.size(); i++) {
            if (i == pieces.size() || pos <= off + pieces[i].len) {
                if (i == pieces.size()) { pieces.push_back({1, start, text.size()}); return; }
                Piece p = pieces[i]; size_t inner = pos - off;
                std::vector<Piece> rep;
                if (inner > 0) rep.push_back({p.buf, p.start, inner});
                rep.push_back({1, start, text.size()});
                if (inner < p.len) rep.push_back({p.buf, p.start + inner, p.len - inner});
                pieces.erase(pieces.begin() + i); pieces.insert(pieces.begin() + i, rep.begin(), rep.end());
                return;
            }
            off += pieces[i].len;
        }
    }
    void erase(size_t pos, size_t n) {
        std::vector<Piece> out; size_t off = 0, end = pos + n;
        for (auto p : pieces) {
            size_t a = off, b = off + p.len; off = b;
            if (b <= pos || a >= end) { out.push_back(p); continue; }
            if (a < pos) out.push_back({p.buf, p.start, pos - a});             // 앞 조각 남김
            if (b > end) out.push_back({p.buf, p.start + (end - a), b - end}); // 뒤 조각 남김
        }
        pieces.swap(out);
    }
    std::string text() const {
        std::string r;
        for (auto& p : pieces) r += (p.buf ? added : orig).substr(p.start, p.len);
        return r;
    }
    size_t pieceCount() const { return pieces.size(); }
};

int main() {
    PieceTable t("Hello world");
    t.insert(5, ",");
    assert(t.text() == "Hello, world" && t.pieceCount() == 3);        // 원본 조각 둘 + 추가 조각 하나
    t.insert(12, "!");
    assert(t.text() == "Hello, world!");
    t.erase(5, 1);
    assert(t.text() == "Hello world!");
    t.erase(0, 6);
    assert(t.text() == "world!");
    std::cout << "PieceTable: " << t.text() << " (" << t.pieceCount() << " pieces)" << std::endl;
    return 0;
}
// Time Complexity: 편집 O(조각 수), 균형 트리로 O(log 조각 수) 개선 가능
// Space Complexity: O(편집 횟수), 원본은 복사하지 않음
```
# Part 5. 기본 패턴 검색
## NaiveSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 단순 검색: 텍스트의 모든 위치에서 패턴을 처음부터 비교한다. 비교 횟수는 입력에 따라 (n−m+1) 에서 (n−m+1)·m 까지.
//  ① 정답: 겹치는 일치를 모두 찾는지 std::string::find 와 대조(빈 패턴·패턴이 더 긴 경우·'\0' 포함).  ② 최악 입력 a^n 에서 a^(m−1)b 찾기 = 정확히 (n−m+1)·m 번, 최선 = (n−m+1) 번.
//  ③ 전수 확인: 이진 텍스트(길이 10) × 이진 패턴(길이 4) 전부에서 비교 횟수의 최대·최소가 위 식과 같다.  ④ 무작위 텍스트의 기대 비교 횟수: 위치당 1/(1 − 1/σ) (σ = 알파벳 크기).
std::vector<size_t> naiveSearch(const std::string& t, const std::string& p, long& comparisons) {
    std::vector<size_t> res; comparisons = 0;
    for (size_t i = 0; i + p.size() <= t.size(); ++i) { size_t j = 0; while (j < p.size()) { ++comparisons; if (t[i + j] != p[j]) break; ++j; } if (j == p.size()) res.push_back(i); }
    return res;
}
std::vector<size_t> findAll(const std::string& t, const std::string& p) { std::vector<size_t> r; if (p.empty()) { for (size_t i = 0; i <= t.size(); ++i) r.push_back(i); return r; } for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) r.push_back(i); return r; }

int main() {
    long c; assert((naiveSearch("abracadabra", "abra", c) == std::vector<size_t>{0, 7}));
    // ① 정답
    std::mt19937 rng(3);
    for (int it = 0; it < 100000; ++it) { std::string t(rng() % 20, 'a'), p(rng() % 5, 'a'); for (char& ch : t) ch = "ab\0"[rng() % 3]; for (char& ch : p) ch = "ab\0"[rng() % 3]; assert(naiveSearch(t, p, c) == findAll(t, p)); }
    assert(naiveSearch("abc", "abcd", c).empty() && c == 0 && naiveSearch("", "", c) == std::vector<size_t>{0});
    // ② 최악·최선 (정확한 식)
    for (size_t n : {100u, 1000u}) for (size_t m : {1u, 5u, 50u}) { if (m > n) continue;
        std::string worstT(n, 'a'), worstP = std::string(m - 1, 'a') + "b"; naiveSearch(worstT, worstP, c); assert(c == (long)((n - m + 1) * m));      // 모든 위치에서 마지막 글자에서 어긋난다
        std::string bestT(n, 'a'), bestP(m, 'b'); naiveSearch(bestT, bestP, c); assert(c == (long)(n - m + 1)); }                                          // 첫 글자에서 어긋난다
    // ③ 전수: 이진 텍스트 길이 10, 패턴 길이 4 (1024 × 16)
    { const int n = 10, m = 4; long mx = 0, mn = 1 << 30; for (int ti = 0; ti < (1 << n); ++ti) { std::string t(n, '0'); for (int k = 0; k < n; ++k) t[k] = '0' + (ti >> k & 1); for (int pi = 0; pi < (1 << m); ++pi) { std::string p(m, '0'); for (int k = 0; k < m; ++k) p[k] = '0' + (pi >> k & 1); naiveSearch(t, p, c); mx = std::max(mx, c); mn = std::min(mn, c); } }
      assert(mx == (n - m + 1) * m && mn == n - m + 1); }
    // ④ 무작위 텍스트의 기대 비교 횟수 (위치당 Σ_{j≥0} σ^−j = 1/(1 − 1/σ)): 알파벳 2, 4, 26
    for (int sigma : {2, 4, 26}) { std::string t(400000, 'a'); for (char& ch : t) ch = (char)('a' + rng() % sigma); std::string p(30, 'a'); for (char& ch : p) ch = (char)('a' + rng() % sigma); naiveSearch(t, p, c); double perPos = (double)c / (double)(t.size() - p.size() + 1), expect = 1.0 / (1.0 - 1.0 / sigma); assert(std::abs(perPos - expect) < 0.03 * expect);
      std::cout << "sigma=" << sigma << ": " << perPos << " comparisons per position (expected " << expect << ")\n"; }
    naiveSearch(std::string(1000, 'a'), std::string(50, 'a') + "b", c); assert(c == (long)(950 * 51));
    std::cout << "worst case comparisons for n=1000, m=51: " << c << " = (n-m+1)*m" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(n) (무작위 텍스트), 최악 O(n·m)
// Space Complexity: O(1)
```
## KMP()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// KMP: 패턴 자체의 접두사-접미사 일치 정보(실패 함수 π)로, 불일치가 나도 텍스트 포인터를 뒤로 되돌리지 않는다. 항상 O(n + m).
//  ① π 를 *정의*대로 (각 접두사의 가장 긴 진 테두리) 무차별로 구한 값과 대조  ② 검색을 std::string::find 로 만든 모든 겹치는 일치와 대조  ③ 응용: 최소 주기 p = m − π[m−1], 모든 테두리는 π 사슬,
//  접두사 등장 횟수  ④ 스트리밍: 텍스트를 임의 조각으로 나눠 넣어도 상태 k 만 이어 가면 결과가 같다  ⑤ 글자마다 실패 간선을 따라가는 횟수의 최대(지연)는 log_φ(m)+1 이하이고 피보나치 문자열이 이를 거의 채운다.
std::vector<int> failure(const std::string& p) {
    std::vector<int> pi(p.size(), 0);
    for (size_t i = 1, k = 0; i < p.size(); ++i) { while (k > 0 && p[i] != p[k]) k = (size_t)pi[k - 1]; if (p[i] == p[k]) ++k; pi[i] = (int)k; }
    return pi;
}
std::vector<int> bruteFailure(const std::string& p) { std::vector<int> pi(p.size(), 0); for (size_t i = 0; i < p.size(); ++i) for (size_t b = i; b >= 1; --b) if (p.compare(0, b, p, i + 1 - b, b) == 0) { pi[i] = (int)b; break; } return pi; }       // 접두사 [0..i] 의 가장 긴 진 테두리
struct Matcher {                                                              // 스트리밍 KMP: 상태 하나(k)만 들고 있다
    std::string p; std::vector<int> pi; size_t k = 0, pos = 0; long maxDelay = 0, steps = 0;
    explicit Matcher(const std::string& pat) : p(pat), pi(failure(pat)) {}
    void feed(char c, std::vector<size_t>& out) {
        long d = 0; while (k > 0 && (k == p.size() || c != p[k])) { k = (size_t)pi[k - 1]; ++d; } if (c == p[k]) ++k; steps += d; maxDelay = std::max(maxDelay, d);
        if (k == p.size()) out.push_back(pos + 1 - k); ++pos;
    }
};
std::vector<size_t> kmp(const std::string& t, const std::string& p) { Matcher m(p); std::vector<size_t> r; for (char c : t) m.feed(c, r); return r; }
std::vector<size_t> findAll(const std::string& t, const std::string& p) { std::vector<size_t> r; for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) r.push_back(i); return r; }
std::string fibWord(int k) { std::string a = "a", b = "ab"; if (k == 0) return a; for (int i = 2; i <= k; ++i) { std::string c = b + a; a = b; b = c; } return b; }

int main() {
    assert((failure("ababaca") == std::vector<int>{0, 0, 1, 2, 3, 0, 1}) && (kmp("abracadabra", "abra") == std::vector<size_t>{0, 7}) && (kmp("aaaaa", "aa") == std::vector<size_t>{0, 1, 2, 3}));
    std::mt19937 rng(12);
    for (int it = 0; it < 100000; ++it) {                                     // ① ②
        std::string p(1 + rng() % 8, 'a'), t(rng() % 40, 'a'); for (char& c : p) c = (char)('a' + rng() % 2); for (char& c : t) c = (char)('a' + rng() % 2);
        assert(failure(p) == bruteFailure(p) && kmp(t, p) == findAll(t, p));
    }
    for (int it = 0; it < 20000; ++it) {                                      // ③ 주기·테두리·접두사 등장 횟수
        std::string p(1 + rng() % 12, 'a'); for (char& c : p) c = (char)('a' + rng() % 2); std::vector<int> pi = failure(p); size_t n = p.size(), per = n - (size_t)pi[n - 1];
        size_t brutePer = n; for (size_t q = 1; q <= n; ++q) { bool ok = true; for (size_t i = q; i < n && ok; ++i) ok = p[i] == p[i - q]; if (ok) { brutePer = q; break; } } assert(per == brutePer);                       // 최소 주기
        std::vector<int> borders; for (int b = pi[n - 1]; b > 0; b = pi[b - 1]) borders.push_back(b); for (int b = 1; b < (int)n; ++b) assert((std::find(borders.begin(), borders.end(), b) != borders.end()) == (p.compare(0, b, p, n - b, b) == 0));    // π 사슬 = 모든 테두리
        }
    // ④ 스트리밍 = 한 번에
    for (int it = 0; it < 5000; ++it) { std::string p(1 + rng() % 5, 'a'), t(rng() % 200, 'a'); for (char& c : p) c = (char)('a' + rng() % 2); for (char& c : t) c = (char)('a' + rng() % 2); Matcher m(p); std::vector<size_t> got; size_t pos = 0; while (pos < t.size()) { size_t chunk = std::min<size_t>(1 + rng() % 17, t.size() - pos); for (size_t i = 0; i < chunk; ++i) m.feed(t[pos + i], got); pos += chunk; } assert(got == findAll(t, p)); }
    // ⑤ 선형성과 지연: 총 후퇴 ≤ n, 한 글자당 후퇴 ≤ log_φ(m) + 1.  피보나치 패턴/텍스트가 거의 최악
    { Matcher m(std::string(500, 'a') + "b"); std::vector<size_t> r; std::string t(100000, 'a'); for (char c : t) m.feed(c, r); assert(r.empty() && m.steps <= (long)t.size()); }               // 나이브라면 5천만 번 비교하는 입력
    double phi = (1 + std::sqrt(5.0)) / 2; long bestDelay = 0;
    for (int k = 6; k <= 20; ++k) { std::string p = fibWord(k), t = fibWord(k + 3) + fibWord(k + 2) + fibWord(k + 4); Matcher m(p); std::vector<size_t> r; for (char c : t) m.feed(c, r); bestDelay = std::max(bestDelay, m.maxDelay); assert(m.steps <= (long)t.size() && (double)m.maxDelay <= std::log((double)p.size()) / std::log(phi) + 1.0 && r == findAll(t, p)); }
    { std::string p = fibWord(22); Matcher m(p); std::vector<size_t> r; std::string t = fibWord(25); for (char c : t) m.feed(c, r); assert(r == findAll(t, p));
      std::cout << "KMP: failure function = brute-force borders and matches = std::string::find on 10^5 random cases; streaming in random chunks agreed; max backtracks on one character was " << bestDelay << " (bound log_phi(m)+1)" << std::endl; }
    return 0;
}
// Time Complexity: O(n + m) (글자당 최악 O(log m) 이지만 총합은 O(n))
// Space Complexity: O(m)
```
# Part 6. 패턴 검색
## RabinKarp()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>

// 라빈-카프(롤링 해시 관점의 요약, 정본은 Hash.md Part 5): 패턴의 해시와 텍스트의 길이 m 윈도 해시를 비교하고, 같을 때만 실제 문자열을 비교한다. 윈도를 밀 때 해시를 O(1) 로 갱신한다.
//  ① 모듈러스 세 가지 — 2^61−1(무작위 밑), 작은 소수 101, 자연 오버플로 2^64 — 에서 가짜 일치(spurious hit) 수를 센다: 101 은 윈도당 1/101, 2^61−1 은 사실상 0, 2^64 는 Thue–Morse 문자열에 속아 대량 발생.
//  ② 검증을 생략하면(해시만 믿으면) 틀린 답을 낸다.  ③ 같은 길이의 패턴 여러 개를 해시 맵 하나로 동시에 찾는다(무차별과 대조).  ④ 2차원 패턴 찾기: 행 해시를 다시 세로로 굴린다.
typedef std::uint64_t u64; __extension__ typedef unsigned __int128 u128;
const u64 P61 = (1ULL << 61) - 1;
struct M61 { static u64 add(u64 a, u64 b) { u64 r = a + b; return r >= P61 ? r - P61 : r; } static u64 sub(u64 a, u64 b) { return a >= b ? a - b : a + P61 - b; }
             static u64 mul(u64 a, u64 b) { u128 t = (u128)a * b; u64 r = (u64)(t & P61) + (u64)(t >> 61); if (r >= P61) r -= P61; if (r >= P61) r -= P61; return r; } };
struct M64 { static u64 add(u64 a, u64 b) { return a + b; } static u64 sub(u64 a, u64 b) { return a - b; } static u64 mul(u64 a, u64 b) { return a * b; } };
struct M101 { static u64 add(u64 a, u64 b) { return (a + b) % 101; } static u64 sub(u64 a, u64 b) { return (a + 101 - b) % 101; } static u64 mul(u64 a, u64 b) { return a * b % 101; } };
struct Stats { long spurious = 0, verifications = 0; };
template <class M> std::vector<size_t> rabinKarp(const std::string& t, const std::string& p, u64 base, bool verify, Stats& st) {
    std::vector<size_t> res; size_t n = t.size(), m = p.size(); if (m == 0 || m > n) return res;
    u64 hp = 0, ht = 0, pw = 1; for (size_t i = 0; i < m; ++i) { hp = M::add(M::mul(hp, base), (unsigned char)p[i]); ht = M::add(M::mul(ht, base), (unsigned char)t[i]); if (i) pw = M::mul(pw, base); }      // pw = base^(m−1)
    for (size_t i = 0; i + m <= n; ++i) {
        if (hp == ht) { if (!verify) res.push_back(i); else { ++st.verifications; if (t.compare(i, m, p) == 0) res.push_back(i); else ++st.spurious; } }
        if (i + m < n) ht = M::add(M::mul(M::sub(ht, M::mul((unsigned char)t[i], pw)), base), (unsigned char)t[i + m]);                                             // 롤링 갱신: 앞 글자 빼고 뒤 글자 더하기
    }
    return res;
}
std::vector<size_t> findAll(const std::string& t, const std::string& p) { std::vector<size_t> r; if (p.empty()) return r; for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) r.push_back(i); return r; }
std::string thueMorse(int len, bool flip) { std::string s(len, 'a'); for (int i = 0; i < len; ++i) s[i] = (__builtin_popcount(i) & 1) != flip ? 'b' : 'a'; return s; }

int main() {
    Stats st; assert((rabinKarp<M61>("abracadabra", "abra", 911382323ULL, true, st) == std::vector<size_t>{0, 7}) && rabinKarp<M61>("hello", "world", 131, true, st).empty() && rabinKarp<M61>("abc", "abcd", 131, true, st).empty());
    std::mt19937_64 rng(99);
    // ① 정답 + 가짜 일치: 2^61−1 (무작위 밑)
    for (int it = 0; it < 50000; ++it) { std::string t(rng() % 40, 'a'), p(1 + rng() % 5, 'a'); for (char& c : t) c = (char)('a' + rng() % 3); for (char& c : p) c = (char)('a' + rng() % 3); Stats s; u64 base = 256 + rng() % (P61 - 256); assert(rabinKarp<M61>(t, p, base, true, s) == findAll(t, p) && s.spurious == 0); }
    // 작은 소수 101: 윈도마다 약 1/101 가짜 일치 (패턴과 다른 윈도 중)
    { std::string t(60000, 'a'), p(8, 'a'); for (char& c : t) c = (char)('a' + rng() % 4); for (char& c : p) c = (char)('a' + rng() % 4); Stats s, s2; std::vector<size_t> good = rabinKarp<M101>(t, p, 7, true, s), unverified = rabinKarp<M101>(t, p, 7, false, s2);
      double windows = (double)(t.size() - p.size() + 1), rate = (double)s.spurious / windows; assert(good == findAll(t, p) && rate > 0.0065 && rate < 0.0135);                     // 1/101 = 0.0099
      assert(unverified.size() == good.size() + (size_t)s.spurious && unverified.size() > good.size() + 300);                                                                          // ② 검증을 생략하면 가짜 일치가 답에 섞인다
      std::cout << "RabinKarp: modulus 101 produced " << s.spurious << " spurious hits in " << (long)windows << " windows (" << 100 * rate << "%, expected ~0.99%), "; }
    // 2^64: Thue–Morse 패턴 a 와 보수 b 는 모든 홀수 밑에서 같은 해시 → b 를 이어 붙인 텍스트의 b 위치마다 가짜 일치
    { std::string a = thueMorse(2048, false), b = thueMorse(2048, true), t; for (int i = 0; i < 16; ++i) t += b; Stats s64, s61; u64 base = (rng() | 1) % (1ULL << 62) | 1;
      std::vector<size_t> r64 = rabinKarp<M64>(t, a, base, true, s64), r61 = rabinKarp<M61>(t, a, 256 + rng() % (P61 - 256), true, s61); assert(r64 == findAll(t, a) && r61 == r64 && s64.spurious >= 16 && s61.spurious == 0);                                      // 검증 덕분에 두 구현 모두 답은 정확 (진짜 일치 위치는 같다)
      std::cout << "mod 2^64 was fooled " << s64.spurious << " times by Thue-Morse blocks (each costs an O(m) verification) while mod 2^61-1 never was; "; }
    // ③ 같은 길이의 패턴 200 개를 한 번에 (텍스트 10 만 글자)
    { const size_t m = 6; std::vector<std::string> pats; for (int i = 0; i < 200; ++i) { std::string p(m, 'a'); for (char& c : p) c = (char)('a' + rng() % 4); pats.push_back(p); }
      std::string t(100000, 'a'); for (char& c : t) c = (char)('a' + rng() % 4); const u64 base = 1000003; std::map<u64, std::vector<int>> byHash; for (int i = 0; i < (int)pats.size(); ++i) { u64 h = 0; for (unsigned char c : pats[i]) h = M61::add(M61::mul(h, base), c); byHash[h].push_back(i); }
      u64 pw = 1; for (size_t i = 1; i < m; ++i) pw = M61::mul(pw, base); u64 h = 0; for (size_t i = 0; i < m; ++i) h = M61::add(M61::mul(h, base), (unsigned char)t[i]);
      std::vector<std::pair<size_t, int>> got; for (size_t i = 0; i + m <= t.size(); ++i) { auto it = byHash.find(h); if (it != byHash.end()) for (int id : it->second) if (t.compare(i, m, pats[id]) == 0) got.emplace_back(i, id); if (i + m < t.size()) h = M61::add(M61::mul(M61::sub(h, M61::mul((unsigned char)t[i], pw)), base), (unsigned char)t[i + m]); }
      std::vector<std::pair<size_t, int>> want; for (int id = 0; id < (int)pats.size(); ++id) for (size_t pos : findAll(t, pats[id])) want.emplace_back(pos, id); std::sort(got.begin(), got.end()); std::sort(want.begin(), want.end()); assert(got == want && got.size() > 1000);
      std::cout << "200 patterns found " << got.size() << " matches in one pass; "; }
    // ④ 2 차원: R×C 격자에서 r×c 패턴. 행 윈도 해시(밑 B1) → 열 방향으로 다시 롤링(밑 B2)
    auto findGrid = [&](const std::vector<std::string>& g, const std::vector<std::string>& pat) {
        size_t R = g.size(), C = g[0].size(), r = pat.size(), c = pat[0].size(); std::vector<std::pair<size_t, size_t>> res; if (r > R || c > C) return res; const u64 B1 = 1000003, B2 = 998244353; u64 pw1 = 1, pw2 = 1; for (size_t i = 1; i < c; ++i) pw1 = M61::mul(pw1, B1); for (size_t i = 1; i < r; ++i) pw2 = M61::mul(pw2, B2);
        auto rowHash = [&](const std::string& s, size_t col) { u64 h = 0; for (size_t k = 0; k < c; ++k) h = M61::add(M61::mul(h, B1), (unsigned char)s[col + k]); return h; };
        u64 hp = 0; for (size_t i = 0; i < r; ++i) hp = M61::add(M61::mul(hp, B2), rowHash(pat[i], 0));
        std::vector<std::vector<u64>> H(R, std::vector<u64>(C - c + 1)); for (size_t i = 0; i < R; ++i) { H[i][0] = rowHash(g[i], 0); for (size_t j = 1; j + c <= C; ++j) H[i][j] = M61::add(M61::mul(M61::sub(H[i][j - 1], M61::mul((unsigned char)g[i][j - 1], pw1)), B1), (unsigned char)g[i][j + c - 1]); }
        for (size_t j = 0; j + c <= C; ++j) { u64 v = 0; for (size_t i = 0; i < r; ++i) v = M61::add(M61::mul(v, B2), H[i][j]);
            for (size_t i = 0; i + r <= R; ++i) { if (v == hp) { bool ok = true; for (size_t k = 0; k < r && ok; ++k) ok = g[i + k].compare(j, c, pat[k]) == 0; if (ok) res.emplace_back(i, j); } if (i + r < R) v = M61::add(M61::mul(M61::sub(v, M61::mul(H[i][j], pw2)), B2), H[i + r][j]); } }
        std::sort(res.begin(), res.end()); return res; };
    for (int it = 0; it < 3000; ++it) { size_t R = 1 + rng() % 8, C = 1 + rng() % 8, r = 1 + rng() % 3, c = 1 + rng() % 3; std::vector<std::string> g(R, std::string(C, 'a')), pat(r, std::string(c, 'a')); for (auto& row : g) for (char& ch : row) ch = (char)('a' + rng() % 2); for (auto& row : pat) for (char& ch : row) ch = (char)('a' + rng() % 2);
        std::vector<std::pair<size_t, size_t>> want; for (size_t i = 0; i + r <= R; ++i) for (size_t j = 0; j + c <= C; ++j) { bool ok = true; for (size_t k = 0; k < r && ok; ++k) ok = g[i + k].compare(j, c, pat[k]) == 0; if (ok) want.emplace_back(i, j); } assert(findGrid(g, pat) == want); }
    { const size_t N = 1000, k = 20; std::vector<std::string> g(N, std::string(N, 'a')); for (auto& row : g) for (char& ch : row) ch = (char)('a' + rng() % 26); std::vector<std::string> pat(k); for (size_t i = 0; i < k; ++i) pat[i] = g[100 + i].substr(300, k);
      std::vector<std::pair<size_t, size_t>> want = {{100, 300}}; for (std::pair<size_t, size_t> at : {std::pair<size_t, size_t>{0, 0}, {500, 500}, {979, 979}, {250, 700}}) { for (size_t i = 0; i < k; ++i) g[at.first + i].replace(at.second, k, pat[i]); want.push_back(at); } std::sort(want.begin(), want.end()); assert(findGrid(g, pat) == want);
      std::cout << "a 20x20 pattern was located at all 5 positions of a 1000x1000 grid" << std::endl; }
    return 0;
}
// Time Complexity: 평균 O(n + m), 가짜 일치가 많으면 최악 O(n·m)
// Space Complexity: O(1) (2 차원은 O(R·C))
```
## BoyerMoore()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 보이어-무어: 패턴을 오른쪽 끝부터 비교하고, 불일치가 나면 두 규칙 중 더 큰 이동량만큼 한 번에 건너뛴다.
//  (1) 나쁜 문자 규칙: 텍스트의 불일치 문자가 패턴에서 마지막으로 나타나는 위치에 맞춘다
//  (2) 좋은 접미사 규칙: 이미 맞춘 접미사가 패턴의 다른 곳에 다시 나타나는 위치에 맞춘다
// 평균적으로 텍스트의 일부만 읽어 서브리니어(sublinear)이다
std::vector<size_t> boyerMoore(const std::string& t, const std::string& p) {
    std::vector<size_t> res;
    int n = t.size(), m = p.size();
    if (m == 0 || m > n) return res;
    int bc[256]; std::fill(bc, bc + 256, -1);
    for (int i = 0; i < m; i++) bc[(unsigned char)p[i]] = i;
    std::vector<int> shift(m + 1, 0), bpos(m + 1);                    // 좋은 접미사 전처리
    int i = m, j = m + 1; bpos[i] = j;
    while (i > 0) {
        while (j <= m && p[i - 1] != p[j - 1]) { if (shift[j] == 0) shift[j] = j - i; j = bpos[j]; }
        i--; j--; bpos[i] = j;
    }
    j = bpos[0];
    for (i = 0; i <= m; i++) { if (shift[i] == 0) shift[i] = j; if (i == j) j = bpos[j]; }
    int s = 0;
    while (s <= n - m) {
        int k = m - 1;
        while (k >= 0 && p[k] == t[s + k]) k--;
        if (k < 0) { res.push_back(s); s += shift[0]; }
        else s += std::max(shift[k + 1], k - bc[(unsigned char)t[s + k]]);
    }
    return res;
}
std::vector<size_t> naive(const std::string& t, const std::string& p) {
    std::vector<size_t> r; for (size_t i = 0; i + p.size() <= t.size(); i++) if (t.compare(i, p.size(), p) == 0) r.push_back(i); return r;
}

int main() {
    assert((boyerMoore("abracadabra", "abra") == std::vector<size_t>{0, 7}));
    assert((boyerMoore("HERE IS A SIMPLE EXAMPLE", "EXAMPLE") == std::vector<size_t>{17}));
    std::mt19937 rng(1);                                              // 무작위 입력에서 나이브와 결과 일치
    for (int iter = 0; iter < 2000; iter++) {
        std::string t, p; int n = rng() % 40 + 1, m = rng() % 6 + 1;
        for (int i = 0; i < n; i++) t += "ab"[rng() % 2]; for (int i = 0; i < m; i++) p += "ab"[rng() % 2];
        assert(boyerMoore(t, p) == naive(t, p));
    }
    std::cout << "BoyerMoore matches naive on 2000 random cases." << std::endl;
    return 0;
}
// Time Complexity: 평균 O(n/m), 최악 O(n·m) (좋은 접미사 규칙과 Galil 규칙을 쓰면 O(n))
// Space Complexity: O(m + σ)
```
## Horspool()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 호스풀: 보이어-무어를 단순화. 윈도우의 "마지막 문자"만 보고 이동량을 정한다 (나쁜 문자 규칙만)
//  shift[c] = 패턴의 마지막 문자를 제외하고 c 가 마지막으로 나오는 위치부터 끝까지의 거리, 없으면 m
std::vector<size_t> horspool(const std::string& t, const std::string& p) {
    std::vector<size_t> res; size_t n = t.size(), m = p.size();
    if (m == 0 || m > n) return res;
    size_t shift[256];
    std::fill(shift, shift + 256, m);
    for (size_t i = 0; i + 1 < m; i++) shift[(unsigned char)p[i]] = m - 1 - i;
    for (size_t s = 0; s + m <= n; s += shift[(unsigned char)t[s + m - 1]]) {
        size_t k = m; while (k > 0 && p[k - 1] == t[s + k - 1]) k--;
        if (k == 0) res.push_back(s);
    }
    return res;
}

int main() {
    assert((horspool("abracadabra", "abra") == std::vector<size_t>{0, 7}));
    assert(horspool("hello", "xyz").empty());
    std::mt19937 rng(2);
    for (int iter = 0; iter < 2000; iter++) {
        std::string t, p; int n = rng() % 40 + 1, m = rng() % 6 + 1;
        for (int i = 0; i < n; i++) t += "abc"[rng() % 3]; for (int i = 0; i < m; i++) p += "abc"[rng() % 3];
        std::vector<size_t> expect; for (size_t i = 0; i + p.size() <= t.size(); i++) if (t.compare(i, p.size(), p) == 0) expect.push_back(i);
        assert(horspool(t, p) == expect);
    }
    std::cout << "Horspool matches naive on 2000 random cases." << std::endl;
    return 0;
}
// Time Complexity: 평균 O(n/m), 최악 O(n·m)
// Space Complexity: O(σ)
```
## SundaySearch()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 선데이(Quick Search): 일치 여부와 상관없이 "윈도우 바로 다음 문자"를 보고 이동한다.
//  shift[c] = 패턴에서 c 가 마지막으로 나타나는 위치로부터 패턴 끝 다음까지의 거리 (m - 마지막 위치), 없으면 m + 1
std::vector<size_t> sunday(const std::string& t, const std::string& p) {
    std::vector<size_t> res; size_t n = t.size(), m = p.size();
    if (m == 0 || m > n) return res;
    size_t shift[256];
    std::fill(shift, shift + 256, m + 1);
    for (size_t i = 0; i < m; i++) shift[(unsigned char)p[i]] = m - i;
    for (size_t s = 0; s + m <= n;) {
        if (t.compare(s, m, p) == 0) res.push_back(s);
        if (s + m >= n) break;                                   // 다음 문자가 없다
        s += shift[(unsigned char)t[s + m]];
    }
    return res;
}

int main() {
    assert((sunday("substring searching algorithm", "search") == std::vector<size_t>{10}));
    assert((sunday("abracadabra", "abra") == std::vector<size_t>{0, 7}));
    std::mt19937 rng(3);
    for (int iter = 0; iter < 2000; iter++) {
        std::string t, p; int n = rng() % 40 + 1, m = rng() % 6 + 1;
        for (int i = 0; i < n; i++) t += "abc"[rng() % 3]; for (int i = 0; i < m; i++) p += "abc"[rng() % 3];
        std::vector<size_t> expect; for (size_t i = 0; i + p.size() <= t.size(); i++) if (t.compare(i, p.size(), p) == 0) expect.push_back(i);
        assert(sunday(t, p) == expect);
    }
    std::cout << "Sunday matches naive on 2000 random cases." << std::endl;
    return 0;
}
// Time Complexity: 평균 O(n/m), 최악 O(n·m)
// Space Complexity: O(σ)
```
# Part 7. 선형 시간 문자열 알고리즘
## ZAlgorithm()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// Z 배열: z[i] = s[i..] 와 s 의 최장 공통 접두사 길이. 이미 구한 [l, r) 구간 안에서는 값을 재사용해 O(n).
//  ① 정의대로의 무차별 계산과 대조, 문자 비교 횟수 ≤ 2n.  ② 패턴 검색: 구분자 방식(p + '\1' + t)은 텍스트에 구분자가 있으면 틀릴 수 있으니 z 를 |p| 로 자르거나, p 의 Z 로 텍스트를 직접 훑는 확장 Z(구분자 불필요)를 쓴다.
//  ③ 응용: 최소 주기(p + z[p] == n 인 가장 작은 p), 가장 긴 테두리, 접두사별 등장 횟수, z → 접두사 함수(π) 변환(KMP 의 π 와 일치).
std::vector<int> zArray(const std::string& s, long* work = nullptr) {
    int n = (int)s.size(); std::vector<int> z(n, 0); long w = 0;
    for (int i = 1, l = 0, r = 0; i < n; ++i) { if (i < r) z[i] = std::min(r - i, z[i - l]); while (i + z[i] < n && s[z[i]] == s[i + z[i]]) { ++z[i]; ++w; } ++w; if (i + z[i] > r) { l = i; r = i + z[i]; } }
    if (work) *work = w; if (n) z[0] = n; return z;                                             // 관례: z[0] = n
}
std::vector<int> bruteZ(const std::string& s) { int n = (int)s.size(); std::vector<int> z(n, 0); for (int i = 0; i < n; ++i) { int k = 0; while (i + k < n && s[k] == s[i + k]) ++k; z[i] = k; } return z; }
std::vector<int> extendedZ(const std::string& p, const std::string& t) {                          // ext[i] = lcp(t[i..], p).  구분자 없이 p 의 z 만 이용
    std::vector<int> z = zArray(p), ext(t.size(), 0); int m = (int)p.size(), n = (int)t.size();
    for (int i = 0, l = 0, r = 0; i < n; ++i) { if (i < r) ext[i] = std::min(r - i, z[i - l]); while (i + ext[i] < n && ext[i] < m && p[ext[i]] == t[i + ext[i]]) ++ext[i]; if (i + ext[i] > r) { l = i; r = i + ext[i]; } }
    return ext;
}
std::vector<size_t> searchExt(const std::string& t, const std::string& p) { std::vector<size_t> r; std::vector<int> e = extendedZ(p, t); for (size_t i = 0; i < t.size(); ++i) if (e[i] == (int)p.size()) r.push_back(i); return r; }
std::vector<size_t> searchSentinelEq(const std::string& t, const std::string& p) { std::vector<size_t> r; std::vector<int> z = zArray(p + '\1' + t); for (size_t i = p.size() + 1; i < z.size(); ++i) if (z[i] == (int)p.size()) r.push_back(i - p.size() - 1); return r; }        // == : 구분자가 텍스트에도 있으면 놓친다
std::vector<size_t> searchSentinelGe(const std::string& t, const std::string& p) { std::vector<size_t> r; std::vector<int> z = zArray(p + '\1' + t); for (size_t i = p.size() + 1; i < z.size(); ++i) if (z[i] >= (int)p.size()) r.push_back(i - p.size() - 1); return r; }        // >= : 방어
std::vector<size_t> findAll(const std::string& t, const std::string& p) { std::vector<size_t> r; for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) r.push_back(i); return r; }
std::vector<int> piFromZ(const std::vector<int>& z) { int n = (int)z.size(); std::vector<int> pi(n, 0); for (int i = 1; i < n; ++i) for (int j = z[i] - 1; j >= 0; --j) { if (pi[i + j] > 0) break; pi[i + j] = j + 1; } return pi; }       // Z 로부터 접두사 함수를 O(n) 에
std::vector<int> failure(const std::string& p) { std::vector<int> pi(p.size(), 0); for (size_t i = 1, k = 0; i < p.size(); ++i) { while (k > 0 && p[i] != p[k]) k = (size_t)pi[k - 1]; if (p[i] == p[k]) ++k; pi[i] = (int)k; } return pi; }

int main() {
    assert((zArray("aabxaab") == std::vector<int>{7, 1, 0, 0, 3, 1, 0}) && (searchExt("abracadabra", "abra") == std::vector<size_t>{0, 7}) && (searchExt("aaaaa", "aa") == std::vector<size_t>{0, 1, 2, 3}));
    std::mt19937 rng(61);
    for (int it = 0; it < 100000; ++it) {                                                          // ① 정의 대조 + 작업량 ≤ 2n
        std::string s(rng() % 30, 'a'); for (char& c : s) c = (char)('a' + rng() % 2); long w; std::vector<int> z = zArray(s, &w); assert(z == bruteZ(s) && w <= 2 * (long)s.size() + 1);
    }
    { std::string s(1000000, 'a'); long w; std::vector<int> z = zArray(s, &w); assert(z[999999] == 1 && w <= 2 * 1000000L); }                                          // a^n 에서도 선형
    for (int it = 0; it < 50000; ++it) {                                                            // ② 검색 세 가지 (텍스트에 구분자 '\1' 이 섞일 수 있다)
        std::string t(rng() % 25, 'a'), p(1 + rng() % 4, 'a'); for (char& c : t) c = "ab\1"[rng() % 3]; for (char& c : p) c = "ab\1"[rng() % 3]; std::vector<size_t> want = findAll(t, p);
        assert(searchExt(t, p) == want && searchSentinelGe(t, p) == want);                                                         // 확장 Z 와 "z ≥ |p|" 방식은 입력에 구분자가 있어도 정확하다 (z ≥ |p| 이면 p 와 정확히 같다)
        if (p.find('\1') == std::string::npos && t.find('\1') == std::string::npos) assert(searchSentinelEq(t, p) == want);        // "z == |p|" 방식은 구분자가 입력에 없을 때만 보장
    }
    { std::string p = "ab", t = "ab\1ab"; assert(searchSentinelEq(t, p) != findAll(t, p) && searchExt(t, p) == findAll(t, p) && searchSentinelGe(t, p) == findAll(t, p)); }       // 구분자가 텍스트에 있으면 == 방식은 일치를 놓친다
    { std::string t("a\0b\0a\0b", 7), p("\0b", 2); assert(searchExt(t, p) == findAll(t, p) && searchExt(t, p).size() == 2); }                                                      // '\0' 같은 임의의 바이트도 안전
    // ③ 응용
    for (int it = 0; it < 30000; ++it) {
        std::string s(1 + rng() % 14, 'a'); for (char& c : s) c = (char)('a' + rng() % 2); int n = (int)s.size(); std::vector<int> z = zArray(s);
        int period = n; for (int q = 1; q < n; ++q) if (q + z[q] == n) { period = q; break; } int piPeriod = n - failure(s)[n - 1]; assert(period == piPeriod);                         // 최소 주기: Z 와 KMP 가 같다
        int border = 0; for (int i = 1; i < n; ++i) if (i + z[i] == n) { border = std::max(border, z[i]); } assert(border == failure(s)[n - 1]);                                               // 가장 긴 테두리
        assert(piFromZ(z) == failure(s));                                                                                                                                              // Z → π
        std::vector<long> occ(n + 2, 0); for (int i = 0; i < n; ++i) ++occ[std::min(z[i], n)]; for (int k = n - 1; k >= 1; --k) occ[k] += occ[k + 1];                                          // occ[k] = z[i] ≥ k 인 i 의 수 = 접두사(길이 k)의 등장 횟수
        for (int k = 1; k <= n; ++k) { long brute = 0; for (int i = 0; i + k <= n; ++i) brute += s.compare(i, k, s, 0, k) == 0; assert(brute == occ[k]); }
    }
    std::cout << "ZAlgorithm: Z array = brute force on 10^5 strings with <= 2n work; extended Z needs no sentinel; Z -> prefix function, period, border and prefix occurrence counts verified" << std::endl;
    return 0;
}
// Time Complexity: O(n + m)
// Space Complexity: O(n + m) (확장 Z 는 O(m))
```
## LongestRepeatedSubstring()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

// 가장 긴 반복 부분 문자열(두 번 이상 나타나는 가장 긴 부분 문자열; 겹쳐도 됨).  "길이 L 짜리 반복이 있다" 는 L 에 대해 단조(L 이면 L−1 도) → 이분 탐색 + 해시(일치 후 실제 비교로 확인).
//  세 가지 구현을 대조한다: ① 접미사 배열 + Kasai LCP 의 최댓값(정확, 오라클)  ② 해시 이분 탐색 — *해시마다 위치를 모두 보관*하고 mod 2^61−1 무작위 밑 사용  ③ 흔한 약식 구현(해시마다 위치 하나만 덮어쓰기 + mod 2^64)
//  ③ 은 Thue–Morse 문자열에서 해시가 대량 충돌해 위치를 덮어쓰는 바람에 실제로 있는 반복을 놓칠 수 있다 — 가짜 일치 수와 정답 여부를 측정한다.
typedef std::uint64_t u64; __extension__ typedef unsigned __int128 u128;
const u64 P61 = (1ULL << 61) - 1;
u64 mul61(u64 a, u64 b) { u128 t = (u128)a * b; u64 r = (u64)(t & P61) + (u64)(t >> 61); if (r >= P61) r -= P61; if (r >= P61) r -= P61; return r; }
std::vector<int> suffixArray(const std::string& s) {                                              // 접두사 배가법 O(n log² n)
    int n = (int)s.size(); std::vector<int> sa(n), rk(n), tmp(n); std::iota(sa.begin(), sa.end(), 0); for (int i = 0; i < n; ++i) rk[i] = (unsigned char)s[i];
    for (int k = 1;; k <<= 1) { auto cmp = [&](int a, int b) { if (rk[a] != rk[b]) return rk[a] < rk[b]; int ra = a + k < n ? rk[a + k] : -1, rb = b + k < n ? rk[b + k] : -1; return ra < rb; };
        std::sort(sa.begin(), sa.end(), cmp); tmp[sa[0]] = 0; for (int i = 1; i < n; ++i) tmp[sa[i]] = tmp[sa[i - 1]] + cmp(sa[i - 1], sa[i]); rk = tmp; if (rk[sa[n - 1]] == n - 1) break; }
    return sa;
}
std::vector<int> kasai(const std::string& s, const std::vector<int>& sa) { int n = (int)s.size(); std::vector<int> rank(n), lcp(n, 0); for (int i = 0; i < n; ++i) rank[sa[i]] = i; for (int i = 0, h = 0; i < n; ++i) { if (rank[i] == 0) { h = 0; continue; } int j = sa[rank[i] - 1]; while (i + h < n && j + h < n && s[i + h] == s[j + h]) ++h; lcp[rank[i]] = h; if (h > 0) --h; } return lcp; }
size_t lrsByLcp(const std::string& s) { if (s.size() < 2) return 0; std::vector<int> lcp = kasai(s, suffixArray(s)); return (size_t)*std::max_element(lcp.begin(), lcp.end()); }
struct Counters { long spurious = 0; };
template <class Hash> size_t lrsHash(const std::string& s, bool keepAll, Counters& cnt, Hash hashWindows) {
    size_t n = s.size(), lo = 1, hi = n ? n - 1 : 0, best = 0;
    auto check = [&](size_t L) {
        std::unordered_map<u64, std::vector<size_t>> seen; std::vector<u64> hs = hashWindows(s, L);
        for (size_t i = 0; i < hs.size(); ++i) { auto& bucket = seen[hs[i]]; for (size_t j : bucket) { if (s.compare(j, L, s, i, L) == 0) return true; ++cnt.spurious; } if (keepAll) bucket.push_back(i); else { bucket.assign(1, i); } }     // keepAll=false: 마지막 위치 하나만 (약식)
        return false; };
    while (n > 1 && lo <= hi) { size_t mid = (lo + hi) / 2; if (check(mid)) { best = mid; lo = mid + 1; } else hi = mid - 1; }
    return best;
}
std::vector<u64> windows61(const std::string& s, size_t L, u64 base) { std::vector<u64> h; if (L > s.size()) return h; u64 cur = 0, pw = 1; for (size_t i = 0; i < L; ++i) { cur = mul61(cur, base) + (unsigned char)s[i]; if (cur >= P61) cur -= P61; if (i) pw = mul61(pw, base); } h.push_back(cur);
    for (size_t i = 0; i + L < s.size(); ++i) { u64 sub = mul61((unsigned char)s[i], pw); cur = cur >= sub ? cur - sub : cur + P61 - sub; cur = mul61(cur, base) + (unsigned char)s[i + L]; if (cur >= P61) cur -= P61; h.push_back(cur); } return h; }
std::vector<u64> windows64(const std::string& s, size_t L) { std::vector<u64> h; if (L > s.size()) return h; u64 cur = 0, pw = 1; for (size_t i = 0; i < L; ++i) { cur = cur * 131 + (unsigned char)s[i]; if (i) pw *= 131; } h.push_back(cur); for (size_t i = 0; i + L < s.size(); ++i) { cur = (cur - (unsigned char)s[i] * pw) * 131 + (unsigned char)s[i + L]; h.push_back(cur); } return h; }
size_t bruteLrs(const std::string& s) { for (size_t L = s.size(); L-- > 1;) { std::set<std::string> seen; for (size_t i = 0; i + L <= s.size(); ++i) if (!seen.insert(s.substr(i, L)).second) return L; } return 0; }
std::string thueMorse(int len) { std::string s(len, 'a'); for (int i = 0; i < len; ++i) s[i] = (__builtin_popcount(i) & 1) ? 'b' : 'a'; return s; }

int main() {
    std::mt19937_64 rng(7); u64 base = 256 + rng() % (P61 - 256); auto h61 = [&](const std::string& s, size_t L) { return windows61(s, L, base); };
    { Counters c; assert(lrsByLcp("banana") == 3 && lrsHash("banana", true, c, h61) == 3 && lrsByLcp("abcabcabc") == 6 && lrsByLcp("abcdef") == 0 && lrsHash("abcdef", true, c, h61) == 0); }
    for (int it = 0; it < 20000; ++it) { std::string s(rng() % 40, 'a'); int sigma = 2 + (int)(rng() % 3); for (char& c : s) c = (char)('a' + rng() % sigma); Counters c61, c64; size_t want = bruteLrs(s);
        assert(lrsByLcp(s) == want && lrsHash(s, true, c61, h61) == want && c61.spurious == 0); /* 약식 구현은 무작위 짧은 문자열에서는 거의 맞는다 */ lrsHash(s, false, c64, windows64); }
    // Thue–Morse 문자열: 해시 충돌이 많은 최악 — 정확한 구현은 그대로 정확하고, 약식 구현은 가짜 일치(검증 실패)가 폭증하며 답이 틀릴 수 있다
    long naiveWrong = 0, naiveSpurious = 0, robustSpurious = 0; size_t worstGap = 0;
    for (int len : {64, 200, 512, 1000, 2048, 4096}) { std::string s = thueMorse(len); size_t want = lrsByLcp(s); Counters cr, cn; size_t robust = lrsHash(s, true, cr, h61), naive = lrsHash(s, false, cn, windows64);
        assert(robust == want && cr.spurious == 0); robustSpurious += cr.spurious; naiveSpurious += cn.spurious; if (naive != want) { ++naiveWrong; worstGap = std::max(worstGap, want - naive); } }
    // 큰 입력: 무작위 10 만 글자 (알파벳 4) 와 반복이 심은 문자열
    { std::string s(100000, 'a'); for (char& c : s) c = (char)('a' + rng() % 4); Counters c; size_t want = lrsByLcp(s); assert(lrsHash(s, true, c, h61) == want && want >= 8 && want <= 30);
      std::string planted(100000, 'a'); for (char& ch : planted) ch = (char)('a' + rng() % 26); std::string block = planted.substr(1234, 500); planted.replace(70000, 500, block); Counters c2; assert(lrsByLcp(planted) >= 500 && lrsHash(planted, true, c2, h61) == lrsByLcp(planted)); }
    std::cout << "LongestRepeatedSubstring: suffix-array/LCP, bucketed 2^61-1 hashing and brute force agreed on 20000 random strings; on Thue-Morse strings the sloppy 2^64 overwrite-map version caused " << naiveSpurious << " failed verifications and gave a wrong answer " << naiveWrong << " times of 6 (largest shortfall " << worstGap << ") while the robust version had " << robustSpurious << std::endl;
    return 0;
}
// Time Complexity: 해시 이분 탐색 O(n log n), 접미사 배열 + LCP O(n log² n)
// Space Complexity: O(n)
```
## Manacher()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 마나커: 가장 긴 회문 부분 문자열을 O(n)에 구한다. 사이사이에 '#'을 끼워 홀수·짝수 길이를 한꺼번에 처리하고,
// 지금까지 구한 가장 오른쪽 회문의 [center, right] 대칭 정보를 재사용한다
std::string longestPalindrome(const std::string& s) {
    std::string t = "#";
    for (char c : s) { t += c; t += '#'; }
    int n = t.size(); std::vector<int> r(n, 0);                  // r[i] = i 를 중심으로 한 회문 반지름
    int c = 0, right = 0, best = 0, center = 0;
    for (int i = 0; i < n; i++) {
        if (i < right) r[i] = std::min(right - i, r[2 * c - i]);
        while (i - r[i] - 1 >= 0 && i + r[i] + 1 < n && t[i - r[i] - 1] == t[i + r[i] + 1]) r[i]++;
        if (i + r[i] > right) { c = i; right = i + r[i]; }
        if (r[i] > best) { best = r[i]; center = i; }
    }
    return s.substr((center - best) / 2, best);
}
std::string brute(const std::string& s) {
    std::string best;
    for (size_t i = 0; i < s.size(); i++) for (size_t j = i; j < s.size(); j++) {
        bool ok = true; for (size_t a = i, b = j; a < b; a++, b--) if (s[a] != s[b]) { ok = false; break; }
        if (ok && j - i + 1 > best.size()) best = s.substr(i, j - i + 1);
    }
    return best;
}

int main() {
    assert(longestPalindrome("babad").size() == 3);
    assert(longestPalindrome("cbbd") == "bb");
    assert(longestPalindrome("forgeeksskeegfor") == "geeksskeeg");
    std::mt19937 rng(4);
    for (int iter = 0; iter < 2000; iter++) {
        std::string s; int n = rng() % 30 + 1; for (int i = 0; i < n; i++) s += "ab"[rng() % 2];
        assert(longestPalindrome(s).size() == brute(s).size());
    }
    std::cout << "Manacher matches brute force on 2000 random strings." << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
# Part 8. 트라이와 다중 패턴
## Trie()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 트라이(문자열 관점의 요약, 정본은 Tree.md Part 9): 문자열을 한 글자씩 간선에 놓은 트리. 검색·접두사 질의가 키 길이에만 비례하고(O(L)), "접두사로 시작하는 모든 단어"를 바로 구할 수 있다.
//  노드를 배열 풀에 두고(인덱스 연결, 재귀 해제 없음) 노드마다 *그 아래 단어 수* cnt 를 둔다 → 접두사 개수 질의 O(L), 삭제 시 단어가 하나도 안 남은 노드는 즉시 회수(가지치기).
//  검증: std::set<string> 과 무작위 연산열 대조 — contains/erase/접두사 개수/자동 완성(사전순)/최장 접두사 일치/공통 접두사/와일드카드('.'), 그리고 노드 수 = 1 + (살아 있는 단어들의 서로 다른 비어 있지 않은 접두사 수).
class Trie {
    struct Node { int next[26]; bool end; int cnt; };
    std::vector<Node> nd; std::vector<int> freeList;
    int newNode() { int i; if (!freeList.empty()) { i = freeList.back(); freeList.pop_back(); } else { nd.emplace_back(); i = (int)nd.size() - 1; } std::fill(nd[i].next, nd[i].next + 26, -1); nd[i].end = false; nd[i].cnt = 0; return i; }
public:
    Trie() { nd.emplace_back(); std::fill(nd[0].next, nd[0].next + 26, -1); nd[0].end = false; nd[0].cnt = 0; }
    size_t nodes() const { return nd.size() - freeList.size(); }
    size_t size() const { return (size_t)nd[0].cnt; }
    bool insert(const std::string& w) {
        if (contains(w)) return false; int n = 0; ++nd[0].cnt;
        for (char c : w) { int& ref = nd[n].next[c - 'a']; if (ref < 0) { int m = newNode(); nd[n].next[c - 'a'] = m; } n = nd[n].next[c - 'a']; ++nd[n].cnt; }
        nd[n].end = true; return true;
    }
    int find(const std::string& p) const { int n = 0; for (char c : p) { n = nd[n].next[c - 'a']; if (n < 0) return -1; } return n; }
    bool contains(const std::string& w) const { int n = find(w); return n >= 0 && nd[n].end; }
    int countPrefix(const std::string& p) const { int n = find(p); return n < 0 ? 0 : nd[n].cnt; }
    bool erase(const std::string& w) {
        if (!contains(w)) return false; std::vector<int> path = {0}; for (char c : w) path.push_back(nd[path.back()].next[c - 'a']); for (int n : path) --nd[n].cnt;
        for (size_t i = 1; i < path.size(); ++i) if (nd[path[i]].cnt == 0) { nd[path[i - 1]].next[w[i - 1] - 'a'] = -1; for (size_t j = i; j < path.size(); ++j) freeList.push_back(path[j]); return true; }      // 처음으로 단어가 0 이 된 노드부터 끝까지 한 가닥을 통째로 회수
        nd[path.back()].end = false; return true;
    }
    std::vector<std::string> list(const std::string& prefix, size_t limit = (size_t)-1) const {      // 사전순 (깊이 우선, 작은 글자부터)
        std::vector<std::string> out; int s = find(prefix); if (s < 0 || limit == 0) return out; std::string cur = prefix; std::vector<std::pair<int, int>> st = {{s, -1}};      // (노드, 마지막으로 내려간 글자 번호)
        if (nd[s].end) out.push_back(cur);
        while (!st.empty() && out.size() < limit) { auto& top = st.back(); int c = top.second + 1; while (c < 26 && nd[top.first].next[c] < 0) ++c;
            if (c == 26) { st.pop_back(); if (!st.empty()) cur.pop_back(); continue; } top.second = c; int ch = nd[top.first].next[c]; cur.push_back((char)('a' + c)); st.push_back({ch, -1}); if (nd[ch].end) out.push_back(cur); }
        return out;
    }
    std::string longestPrefixOf(const std::string& s) const {                                         // s 의 접두사 중 저장된 가장 긴 단어
        int n = 0; int best = nd[0].end ? 0 : -1; for (size_t i = 0; i < s.size(); ++i) { n = nd[n].next[s[i] - 'a']; if (n < 0) break; if (nd[n].end) best = (int)i + 1; } return best < 0 ? std::string("\x01") : s.substr(0, (size_t)best); }   // 없으면 "\x01"
    std::string commonPrefix() const { std::string r; int n = 0; while (!nd[n].end) { int only = -1, k = 0; for (int c = 0; c < 26; ++c) if (nd[n].next[c] >= 0) { ++k; only = c; } if (k != 1) break; r += (char)('a' + only); n = nd[n].next[only]; } return r; }
    bool matches(const std::string& pat, size_t i = 0, int n = 0) const {                             // '.' 은 아무 글자
        if (i == pat.size()) return nd[n].end; if (pat[i] == '.') { for (int c = 0; c < 26; ++c) if (nd[n].next[c] >= 0 && matches(pat, i + 1, nd[n].next[c])) return true; return false; }
        int m = nd[n].next[pat[i] - 'a']; return m >= 0 && matches(pat, i + 1, m);
    }
};
bool wildMatch(const std::string& pat, const std::string& w) { if (pat.size() != w.size()) return false; for (size_t i = 0; i < pat.size(); ++i) if (pat[i] != '.' && pat[i] != w[i]) return false; return true; }

int main() {
    Trie t; for (auto w : {"car", "card", "care", "cat", "dog"}) t.insert(w);
    assert(t.contains("car") && !t.contains("ca") && !t.contains("cow") && (t.list("car") == std::vector<std::string>{"car", "card", "care"}) && t.list("x").empty());
    std::mt19937 rng(18); auto randWord = [&](int maxLen) { std::string w(rng() % (maxLen + 1), 'a'); for (char& c : w) c = (char)('a' + rng() % 4); return w; };
    for (int round = 0; round < 30; ++round) {
        Trie tr; std::set<std::string> S;
        for (int op = 0; op < 3000; ++op) {
            std::string w = randWord(6); int k = (int)(rng() % 10);
            if (k <= 3) assert(tr.insert(w) == S.insert(w).second);
            else if (k <= 5) assert(tr.erase(w) == (S.erase(w) > 0));
            else if (k == 6) assert(tr.contains(w) == (S.count(w) > 0));
            else if (k == 7) { int cnt = 0; for (auto& x : S) cnt += x.compare(0, w.size(), w) == 0; assert(tr.countPrefix(w) == cnt); }
            else if (k == 8) { std::vector<std::string> want; for (auto it = S.lower_bound(w); it != S.end() && it->compare(0, w.size(), w) == 0; ++it) want.push_back(*it); assert(tr.list(w) == want); size_t lim = rng() % 4; std::vector<std::string> head(want.begin(), want.begin() + std::min(lim, want.size())); assert(tr.list(w, lim) == head); }
            else { std::string pat = randWord(5); for (char& c : pat) if (rng() % 3 == 0) c = '.'; bool want = false; for (auto& x : S) want |= wildMatch(pat, x); assert(tr.matches(pat) == want);
                   std::string best = "\x01"; for (auto& x : S) if (x.size() <= w.size() && w.compare(0, x.size(), x) == 0 && (best == "\x01" || x.size() > best.size())) best = x; assert(tr.longestPrefixOf(w) == best); }
            assert(tr.size() == S.size());
            if (op % 150 == 0) {                                                                      // 노드 수 = 1 + 서로 다른 비어 있지 않은 접두사 수, 공통 접두사, 전체 목록
                std::set<std::string> prefixes; for (auto& x : S) for (size_t l = 1; l <= x.size(); ++l) prefixes.insert(x.substr(0, l)); assert(tr.nodes() == 1 + prefixes.size());
                std::string common; if (!S.empty()) { common = *S.begin(); for (auto& x : S) { size_t l = 0; while (l < common.size() && l < x.size() && common[l] == x[l]) ++l; common.resize(l); } } assert(tr.commonPrefix() == (S.empty() ? "" : (S.count("") ? "" : common)));
                assert(tr.list("") == std::vector<std::string>(S.begin(), S.end())); }
        }
        for (auto it = S.begin(); it != S.end();) { assert(tr.erase(*it)); it = S.erase(it); } assert(tr.nodes() == 1 && tr.size() == 0);                  // 전부 지우면 루트만 남는다 (가지치기)
    }
    // 큰 입력: 20 만 개의 무작위 단어 (3~10 글자, 26 글자)
    { Trie big; std::vector<std::string> words; for (int i = 0; i < 200000; ++i) { std::string w(3 + rng() % 8, 'a'); for (char& c : w) c = (char)('a' + rng() % 26); words.push_back(w); big.insert(w); }
      std::vector<std::string> sorted = words; std::sort(sorted.begin(), sorted.end()); sorted.erase(std::unique(sorted.begin(), sorted.end()), sorted.end()); assert(big.size() == sorted.size() && big.list("") == sorted);
      size_t chars = 0; for (auto& w : sorted) chars += w.size(); std::cout << "Trie: matched std::set on 90000 random operations; 200000 words (" << sorted.size() << " distinct, " << chars << " characters) used " << big.nodes() << " nodes, listing in sorted order matched std::sort" << std::endl; }
    return 0;
}
// Time Complexity: 삽입/검색/삭제/접두사 개수 O(L), 자동 완성 O(L + 결과 크기)
// Space Complexity: O(노드 수 · σ)
```
## AhoCorasick()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <queue>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// 아호-코라식: 여러 패턴을 트라이로 합치고 KMP 의 실패 함수를 트라이 전체로 확장(실패 링크)해,
// 텍스트를 한 번만 훑어 모든 패턴의 모든 출현을 O(n + 패턴 총 길이 + 출현 수)에 찾는다
class AhoCorasick {
    struct Node { int next[26]; int fail = 0; std::vector<int> out; Node() { std::fill(next, next + 26, -1); } };
    std::vector<Node> t; std::vector<std::string> pats;
public:
    explicit AhoCorasick(const std::vector<std::string>& patterns) : t(1), pats(patterns) {
        for (int id = 0; id < (int)pats.size(); id++) {
            int cur = 0;
            for (char ch : pats[id]) { int c = ch - 'a'; if (t[cur].next[c] < 0) { t[cur].next[c] = t.size(); t.emplace_back(); } cur = t[cur].next[c]; }
            t[cur].out.push_back(id);
        }
        std::queue<int> q;                                         // BFS 로 실패 링크를 만든다
        for (int c = 0; c < 26; c++) { int v = t[0].next[c]; if (v < 0) t[0].next[c] = 0; else { t[v].fail = 0; q.push(v); } }
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int c = 0; c < 26; c++) {
                int v = t[u].next[c];
                if (v < 0) { t[u].next[c] = t[t[u].fail].next[c]; continue; }
                t[v].fail = t[t[u].fail].next[c];
                for (int id : t[t[v].fail].out) t[v].out.push_back(id);   // 접미사로 끝나는 패턴도 함께 출력
                q.push(v);
            }
        }
    }
    // (패턴, 시작 위치) 목록
    std::vector<std::pair<std::string, size_t>> search(const std::string& text) const {
        std::vector<std::pair<std::string, size_t>> res; int cur = 0;
        for (size_t i = 0; i < text.size(); i++) {
            cur = t[cur].next[text[i] - 'a'];
            for (int id : t[cur].out) res.push_back({pats[id], i + 1 - pats[id].size()});
        }
        return res;
    }
};

int main() {
    AhoCorasick ac({"he", "she", "his", "hers"});
    auto r = ac.search("ushers");
    std::sort(r.begin(), r.end());
    std::vector<std::pair<std::string, size_t>> expect = {{"he", 2}, {"hers", 2}, {"she", 1}};
    assert(r == expect);
    assert(AhoCorasick({"a", "aa"}).search("aaa").size() == 5);       // a×3 + aa×2
    std::cout << "AhoCorasick found " << r.size() << " matches in 'ushers'" << std::endl;
    return 0;
}
// Time Complexity: O(n + Σ|패턴| + z)  (z = 출현 횟수)
// Space Complexity: O(Σ|패턴| · σ)
```
# Part 9. 접미사 구조
## SuffixArray()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 접미사 배열: 모든 접미사를 사전순으로 정렬했을 때 각 접미사의 시작 위치. 이를 이용하면 패턴 검색이 이진 탐색(O(m log n))이 된다.
//  ① 순진한 정렬(접미사 비교 O(n)) vs 접두사 배가법(2^k 글자씩 순위를 두 배로 — O(n log² n)): 비교한 문자 수와 라운드 수를 센다 (a^n 에서 순진한 방식은 n²/2, 배가법은 ⌈log₂n⌉ 라운드).
//  ② Kasai 알고리즘으로 LCP(인접 접미사의 공통 접두사)를 O(n) 에.  ③ 활용: 패턴 등장 위치(연속 구간), 서로 다른 부분 문자열 수 = n(n+1)/2 − ΣLCP, 가장 긴 반복 부분 문자열 = max LCP.
//  모두 독립 계산(모든 접미사 문자열 정렬, 모든 부분 문자열 집합)과 대조하고 20 만 글자 무작위 문자열에서도 확인한다.
long g_chars = 0;
std::vector<int> naiveSuffixArray(const std::string& s) {
    std::vector<int> sa(s.size()); std::iota(sa.begin(), sa.end(), 0);
    std::sort(sa.begin(), sa.end(), [&](int a, int b) { size_t i = (size_t)a, j = (size_t)b; while (i < s.size() && j < s.size() && s[i] == s[j]) { ++i; ++j; ++g_chars; } ++g_chars; if (i == s.size() || j == s.size()) return i == s.size() && j != s.size(); return s[i] < s[j]; });
    return sa;
}
std::vector<int> bruteSuffixArray(const std::string& s) { std::vector<std::pair<std::string, int>> v; for (size_t i = 0; i < s.size(); ++i) v.emplace_back(s.substr(i), (int)i); std::sort(v.begin(), v.end()); std::vector<int> sa; for (auto& x : v) sa.push_back(x.second); return sa; }
std::vector<int> doublingSuffixArray(const std::string& s, int* rounds = nullptr) {
    int n = (int)s.size(), r = 0; std::vector<int> sa(n), rk(n), tmp(n); std::iota(sa.begin(), sa.end(), 0); for (int i = 0; i < n; ++i) rk[i] = (unsigned char)s[i]; if (n <= 1) { if (rounds) *rounds = 0; return sa; }
    for (int k = 1;; k <<= 1) { ++r; auto cmp = [&](int a, int b) { if (rk[a] != rk[b]) return rk[a] < rk[b]; int ra = a + k < n ? rk[a + k] : -1, rb = b + k < n ? rk[b + k] : -1; return ra < rb; };
        std::sort(sa.begin(), sa.end(), cmp); tmp[sa[0]] = 0; for (int i = 1; i < n; ++i) tmp[sa[i]] = tmp[sa[i - 1]] + cmp(sa[i - 1], sa[i]); rk = tmp; if (rk[sa[n - 1]] == n - 1) break; }
    if (rounds) *rounds = r; return sa;
}
std::vector<int> kasai(const std::string& s, const std::vector<int>& sa) {                         // lcp[i] = sa[i−1] 과 sa[i] 접미사의 공통 접두사 길이 (lcp[0] = 0)
    int n = (int)s.size(); std::vector<int> rank(n), lcp(n, 0); for (int i = 0; i < n; ++i) rank[sa[i]] = i;
    for (int i = 0, h = 0; i < n; ++i) { if (rank[i] == 0) { h = 0; continue; } int j = sa[rank[i] - 1]; while (i + h < n && j + h < n && s[i + h] == s[j + h]) ++h; lcp[rank[i]] = h; if (h > 0) --h; }
    return lcp;
}
std::vector<int> occurrences(const std::string& s, const std::vector<int>& sa, const std::string& p) {          // 패턴으로 시작하는 접미사는 SA 에서 연속 구간
    auto lo = std::lower_bound(sa.begin(), sa.end(), p, [&](int i, const std::string& x) { return s.compare((size_t)i, x.size(), x) < 0; });
    auto hi = std::upper_bound(sa.begin(), sa.end(), p, [&](const std::string& x, int i) { return s.compare((size_t)i, x.size(), x) > 0; });
    std::vector<int> r(lo, hi); std::sort(r.begin(), r.end()); return r;
}
std::vector<int> findAll(const std::string& t, const std::string& p) { std::vector<int> r; for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) r.push_back((int)i); return r; }

int main() {
    std::string banana = "banana"; auto sa0 = naiveSuffixArray(banana); assert((sa0 == std::vector<int>{5, 3, 1, 0, 4, 2}) && (occurrences(banana, sa0, "ana") == std::vector<int>{1, 3}) && (occurrences(banana, sa0, "na") == std::vector<int>{2, 4}) && occurrences(banana, sa0, "x").empty());
    { std::vector<int> l = kasai(banana, sa0); assert((l == std::vector<int>{0, 1, 3, 0, 0, 2})); long sum = 0; for (int x : l) sum += x; assert(6 * 7 / 2 - sum == 15); }                              // banana 의 서로 다른 부분 문자열은 15 개
    std::mt19937 rng(19);
    for (int it = 0; it < 30000; ++it) {
        std::string s(rng() % 30, 'a'); int sigma = 1 + (int)(rng() % 3); for (char& c : s) c = (char)('a' + rng() % sigma); std::vector<int> brute = bruteSuffixArray(s), a = naiveSuffixArray(s), b = doublingSuffixArray(s); assert(a == brute && b == brute);
        std::vector<int> lcp = kasai(s, b); for (size_t i = 1; i < s.size(); ++i) { size_t l = 0; while (brute[i] + l < s.size() && brute[i - 1] + l < s.size() && s[brute[i] + l] == s[brute[i - 1] + l]) ++l; assert((size_t)lcp[i] == l); }      // LCP: 인접 접미사를 직접 비교
        std::set<std::string> subs; for (size_t i = 0; i < s.size(); ++i) for (size_t l = 1; i + l <= s.size(); ++l) subs.insert(s.substr(i, l)); long total = (long)s.size() * ((long)s.size() + 1) / 2, sum = 0; for (int x : lcp) sum += x; assert((long)subs.size() == total - sum);    // 서로 다른 부분 문자열 수
        std::string p(1 + rng() % 3, 'a'); for (char& c : p) c = (char)('a' + rng() % sigma); assert(occurrences(s, b, p) == findAll(s, p));
        size_t longestRep = 0; for (int x : lcp) longestRep = std::max<size_t>(longestRep, (size_t)x); size_t bruteRep = 0; for (size_t l = 1; l < s.size(); ++l) { std::set<std::string> seen; bool dup = false; for (size_t i = 0; i + l <= s.size() && !dup; ++i) dup = !seen.insert(s.substr(i, l)).second; if (dup) bruteRep = l; } assert(longestRep == bruteRep);
    }
    // ① 비용: a^n 에서 순진한 정렬은 n²/2 에 가까운 문자 비교, 배가법은 ⌈log₂ n⌉ 라운드
    { const int n = 2000; std::string s(n, 'a'); g_chars = 0; auto a = naiveSuffixArray(s); long naive = g_chars; int rounds; auto b = doublingSuffixArray(s, &rounds); assert(a == b && naive > (long)n * n / 8 && rounds <= 12 && a[0] == n - 1);       // 가장 짧은 접미사 'a' 가 맨 앞
      std::cout << "SuffixArray: on a^" << n << " the naive sort compared " << naive << " characters while doubling needed " << rounds << " rounds; "; }
    // 큰 입력: 무작위 20 만 글자 (알파벳 4) — 순열인지, 인접 접미사가 정렬되어 있는지(직접 비교), LCP 의 합이 다른 식과 맞는지
    { std::string s(200000, 'a'); for (char& c : s) c = (char)('a' + rng() % 4); std::vector<int> sa = doublingSuffixArray(s); std::vector<char> seen(s.size(), 0); for (int x : sa) { assert(!seen[x]); seen[x] = 1; }
      for (size_t i = 1; i < sa.size(); ++i) assert(s.compare((size_t)sa[i - 1], std::string::npos, s, (size_t)sa[i], std::string::npos) < 0);
      std::vector<int> lcp = kasai(s, sa); long sum = 0; int mx = 0; for (int x : lcp) { sum += x; mx = std::max(mx, x); } long total = (long)s.size() * (long)(s.size() + 1) / 2; assert(total - sum > total - 20 * (long)s.size() && mx >= 8);
      std::string p = s.substr(100000, 12); std::vector<int> occ = occurrences(s, sa, p); assert(!occ.empty() && std::binary_search(occ.begin(), occ.end(), 100000));
      std::cout << "a random 200000-character string sorted correctly (longest repeated substring " << mx << ")" << std::endl; }
    return 0;
}
// Time Complexity: 구성 O(n log² n) (배가법) / O(n² log n) 최악 (순진), LCP O(n), 검색 O(m log n)
// Space Complexity: O(n)
```
## BuildSuffixArray()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <numeric>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 접두사 두 배(prefix doubling): 길이 k 로 정렬된 순위를 이용해 (rank[i], rank[i+k]) 쌍으로 길이 2k 순위를 구한다. O(n log² n)
std::vector<int> buildSA(const std::string& s) {
    int n = s.size(); std::vector<int> sa(n), rk(n), tmp(n);
    std::iota(sa.begin(), sa.end(), 0);
    for (int i = 0; i < n; i++) rk[i] = (unsigned char)s[i];
    for (int k = 1;; k <<= 1) {
        auto cmp = [&](int a, int b) {
            if (rk[a] != rk[b]) return rk[a] < rk[b];
            int ra = a + k < n ? rk[a + k] : -1, rb = b + k < n ? rk[b + k] : -1;
            return ra < rb;
        };
        std::sort(sa.begin(), sa.end(), cmp);
        tmp[sa[0]] = 0;
        for (int i = 1; i < n; i++) tmp[sa[i]] = tmp[sa[i - 1]] + cmp(sa[i - 1], sa[i]);
        rk = tmp;
        if (rk[sa[n - 1]] == n - 1) break;                             // 모든 순위가 서로 다르면 끝
    }
    return sa;
}
std::vector<int> naive(const std::string& s) {
    std::vector<int> sa(s.size()); std::iota(sa.begin(), sa.end(), 0);
    std::sort(sa.begin(), sa.end(), [&](int a, int b) { return s.substr(a) < s.substr(b); });
    return sa;
}

int main() {
    assert((buildSA("banana") == std::vector<int>{5, 3, 1, 0, 4, 2}));
    std::mt19937 rng(5);
    for (int iter = 0; iter < 1000; iter++) {
        std::string s; int n = rng() % 40 + 1; for (int i = 0; i < n; i++) s += "abc"[rng() % 3];
        assert(buildSA(s) == naive(s));
    }
    std::string big(20000, 'a'); for (size_t i = 0; i < big.size(); i += 7) big[i] = 'b';
    auto sa = buildSA(big); assert(sa.size() == big.size());
    std::cout << "BuildSuffixArray matches naive on 1000 random strings." << std::endl;
    return 0;
}
// Time Complexity: O(n log² n)  (기수 정렬을 쓰면 O(n log n), SA-IS 는 O(n))
// Space Complexity: O(n)
```
## LCPArray()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <numeric>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// LCP 배열(Kasai): lcp[i] = SA 에서 이웃한 두 접미사 SA[i-1], SA[i] 의 최장 공통 접두사 길이.
// 접미사 i 의 LCP 는 접미사 i+1 의 LCP 보다 1 이상 작지 않다는 성질로 전체를 O(n)에 구한다
std::vector<int> suffixArray(const std::string& s) {
    std::vector<int> sa(s.size()); std::iota(sa.begin(), sa.end(), 0);
    std::sort(sa.begin(), sa.end(), [&](int a, int b) { return s.substr(a) < s.substr(b); });
    return sa;
}
std::vector<int> kasai(const std::string& s, const std::vector<int>& sa) {
    int n = s.size(); std::vector<int> rank(n), lcp(n, 0);
    for (int i = 0; i < n; i++) rank[sa[i]] = i;
    for (int i = 0, h = 0; i < n; i++) {
        if (rank[i] > 0) {
            int j = sa[rank[i] - 1];
            while (i + h < n && j + h < n && s[i + h] == s[j + h]) h++;
            lcp[rank[i]] = h;
            if (h > 0) h--;                                           // 다음 접미사에서는 최소 h-1 은 이미 일치
        } else h = 0;
    }
    return lcp;
}

int main() {
    std::string s = "banana";
    auto sa = suffixArray(s);
    auto lcp = kasai(s, sa);
    assert((lcp == std::vector<int>{0, 1, 3, 0, 0, 2}));
    // 응용: 서로 다른 부분 문자열의 개수 = n(n+1)/2 - Σ lcp
    long distinct = (long)s.size() * (s.size() + 1) / 2 - std::accumulate(lcp.begin(), lcp.end(), 0L);
    std::set<std::string> brute;
    for (size_t i = 0; i < s.size(); i++) for (size_t l = 1; i + l <= s.size(); l++) brute.insert(s.substr(i, l));
    assert(distinct == 15 && distinct == (long)brute.size());
    // 응용: 가장 긴 반복 부분 문자열 = max(lcp)
    assert(*std::max_element(lcp.begin(), lcp.end()) == 3);           // "ana"
    std::cout << "LCP(banana) = 0 1 3 0 0 2, distinct substrings = " << distinct << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
## SuffixAutomaton()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 접미사 자동자(SAM): 문자열의 모든 부분 문자열을 인식하는 가장 작은 DFA. 상태 수 ≤ 2n, 온라인 구성 O(n)
// 상태 v 가 나타내는 문자열 개수 = len[v] - len[link[v]]  ->  서로 다른 부분 문자열 수 = Σ (len[v] - len[link[v]])
struct SAM {
    struct State { int len = 0, link = -1; std::map<char, int> next; };
    std::vector<State> st; int last = 0;
    SAM() : st(1) {}
    void extend(char c) {
        int cur = st.size(); st.push_back({}); st[cur].len = st[last].len + 1;
        int p = last;
        while (p != -1 && !st[p].next.count(c)) { st[p].next[c] = cur; p = st[p].link; }
        if (p == -1) st[cur].link = 0;
        else {
            int q = st[p].next[c];
            if (st[p].len + 1 == st[q].len) st[cur].link = q;
            else {
                int clone = st.size(); st.push_back(st[q]); st[clone].len = st[p].len + 1;
                while (p != -1 && st[p].next[c] == q) { st[p].next[c] = clone; p = st[p].link; }
                st[q].link = st[cur].link = clone;
            }
        }
        last = cur;
    }
    bool contains(const std::string& s) const { int v = 0; for (char c : s) { auto it = st[v].next.find(c); if (it == st[v].next.end()) return false; v = it->second; } return true; }
    long distinctSubstrings() const { long r = 0; for (size_t v = 1; v < st.size(); v++) r += st[v].len - st[st[v].link].len; return r; }
};

int main() {
    SAM sam; for (char c : std::string("banana")) sam.extend(c);
    assert(sam.distinctSubstrings() == 15);
    assert(sam.contains("nan") && sam.contains("anana") && !sam.contains("nab"));
    assert(sam.st.size() <= 2 * 6);                                    // 상태 수 <= 2n
    std::string s = "abracadabra"; SAM b; for (char c : s) b.extend(c);
    std::set<std::string> brute;
    for (size_t i = 0; i < s.size(); i++) for (size_t l = 1; i + l <= s.size(); l++) brute.insert(s.substr(i, l));
    assert(b.distinctSubstrings() == (long)brute.size());
    std::cout << "SuffixAutomaton distinct(banana)=" << sam.distinctSubstrings() << ", states=" << sam.st.size() << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n log σ), 질의 O(m log σ)
// Space Complexity: O(n)
```
## FMIndex()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// FM-인덱스(Ferragina–Manzini 2000): 접미사 배열과 BWT 를 합친 "자기 색인(self-index)". 원문 T 를 버리고도 ① 패턴 개수 세기 ② 출현 위치 찾기 ③ 원문 복원이 모두 되며, BWT 가 압축에 잘 맞아 원문보다 작게 저장된다.
// 재료: BWT 문자열 L (SA 순서로 각 접미사의 바로 앞 글자), C[c] = 원문에서 c 보다 작은 글자의 수, Occ(c, i) = L[0..i) 안의 c 의 개수.  LF 사상 LF(i) = C[L[i]] + Occ(L[i], i) 는 "행 i 의 접미사 앞에 글자를 붙인 접미사의 행".
// 역방향 탐색(backward search): 패턴을 끝에서부터 한 글자씩 붙여 가며 SA 구간 [lo, hi) 를 lo = C[c] + Occ(c, lo), hi = C[c] + Occ(c, hi) 로 줄인다 — 구간 크기가 곧 출현 횟수이고 시간은 |P| 에만 비례(원문 길이 무관).
// 위치(locate): SA 값을 s 칸마다 표본으로 저장하고, 표본이 아닌 행은 LF 를 따라 한 칸씩 이동(걸음 수 t)하다가 표본 행을 만나면 SA[i] = 표본 + t.  Occ 는 32 칸마다 체크포인트를 두고 나머지는 직접 센다(공간-시간 균형)
struct FM {
    std::string L; int n; static const int CP = 32, S = 16; std::array<int, 256> C{}; std::vector<std::array<int, 256>> cp; std::vector<uint64_t> mark; std::vector<int> markRank, sample;
    explicit FM(const std::string& text) {                                  // text 는 마지막에 유일한 가장 작은 문자 '$' 가 붙어 있어야 한다
        n = text.size(); std::vector<int> sa(n); std::iota(sa.begin(), sa.end(), 0); std::sort(sa.begin(), sa.end(), [&](int a, int b) { return text.compare(a, n, text, b, n) < 0; });
        L.resize(n); for (int i = 0; i < n; i++) L[i] = text[(sa[i] + n - 1) % n];
        std::array<int, 256> cnt{}; for (unsigned char ch : text) cnt[ch]++; int acc = 0; for (int c = 0; c < 256; c++) { C[c] = acc; acc += cnt[c]; }
        std::array<int, 256> run{}; for (int i = 0; i < n; i++) { if (i % CP == 0) cp.push_back(run); run[(unsigned char)L[i]]++; } cp.push_back(run);
        mark.assign((n + 63) / 64 + 1, 0); markRank.assign(mark.size() + 1, 0);
        for (int i = 0; i < n; i++) if (sa[i] % S == 0) { mark[i / 64] |= 1ULL << (i % 64); sample.push_back(sa[i]); }
        for (size_t w = 0; w < mark.size(); w++) markRank[w + 1] = markRank[w] + __builtin_popcountll(mark[w]);
    }
    int occ(unsigned char c, int i) const { int b = i / CP, r = cp[b][c]; for (int j = b * CP; j < i; j++) r += (unsigned char)L[j] == c; return r; }
    int lf(int i) const { unsigned char c = L[i]; return C[c] + occ(c, i); }
    std::pair<int, int> range(const std::string& P) const {                // 역방향 탐색
        int lo = 0, hi = n; for (int k = (int)P.size() - 1; k >= 0 && lo < hi; k--) { unsigned char c = P[k]; lo = C[c] + occ(c, lo); hi = C[c] + occ(c, hi); } return {lo, std::max(lo, hi)};
    }
    int count(const std::string& P) const { auto r = range(P); return r.second - r.first; }
    bool marked(int i) const { return (mark[i / 64] >> (i % 64)) & 1; }
    int locate(int i) const { int t = 0; while (!marked(i)) { i = lf(i); t++; } int r = markRank[i / 64] + __builtin_popcountll(mark[i / 64] & ((1ULL << (i % 64)) - 1)); return (sample[r] + t) % n; }
    std::string invert() const { std::string t(n, 0); int i = 0; for (int k = n - 1; k >= 0; k--) { t[k] = L[i]; i = lf(i); } std::rotate(t.begin(), t.begin() + 1, t.end()); return t; }      // 행 0 은 접미사 "$": 거꾸로 따라가며 원문을 복원
    double bits() const { std::array<bool, 256> used{}; for (unsigned char ch : L) used[ch] = true; int sigma = 0; for (bool u : used) sigma += u;
        int lg = 1; while ((1 << lg) < sigma) lg++; return (double)n * lg + cp.size() * (double)sigma * 32 + sample.size() * 32.0 + n; }       // BWT 를 글자당 ⌈log2 σ⌉ 비트로 묶고 + Occ 체크포인트(σ 개 카운터) + SA 표본 + 표시 비트
};
int main() {
    std::mt19937 g(1); int n = 20000; std::string T; for (int i = 0; i < n - 1; i++) T += "ACGT"[g() % 4]; T += '$';
    FM fm(T); assert(fm.invert() == T);                                    // 원문 없이 BWT 만으로 원문 복원
    for (int t = 0; t < 500; t++) {
        std::string P; if (t % 2) { int len = 1 + g() % 10, st = g() % (n - len - 1); P = T.substr(st, len); } else { int len = 1 + g() % 9; for (int i = 0; i < len; i++) P += "ACGT"[g() % 4]; }
        std::vector<int> want; for (size_t p = T.find(P); p != std::string::npos; p = T.find(P, p + 1)) want.push_back(p);
        assert(fm.count(P) == (int)want.size()); auto r = fm.range(P); std::vector<int> got; for (int i = r.first; i < r.second; i++) got.push_back(fm.locate(i)); std::sort(got.begin(), got.end()); assert(got == want);
    }
    std::string W = "the quick brown fox jumps over the lazy dog and the quiet cat sleeps by the door"; std::string big; for (int i = 0; i < 40; i++) big += W; big += '\x01';       // 공백(0x20)이 '$' 보다 작으므로 영어 문장에는 더 작은 종결 문자를 쓴다
    FM text(big); assert(text.count("the ") == 40 * 4 && text.count("quick") == 40 && text.count("zebra") == 0 && text.invert() == big);
    std::cout << "FMIndex: count/locate/invert verified; " << fm.bits() / n << " bits per char for a 4-letter text (plain text 8 + plain suffix array 32 = 40)" << std::endl; return 0;
}
// Time Complexity: count O(|P|·Occ 비용), locate O(s·Occ 비용), 구성 O(n log n) (이 구현의 정렬 기반)
// Space Complexity: BWT n 문자 + Occ 체크포인트 + SA 표본 n/s 개 (BWT 를 압축하면 n H_k 비트)
```
## PalindromicTree()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 회문 트리(Eertree): 문자열의 서로 다른 회문 부분 문자열을 노드로 하는 자료구조. 길이 n 문자열에는 서로 다른 회문이 최대 n개뿐이다.
// 노드 = 회문, next[c] = 양끝에 c 를 붙인 회문, link = 가장 긴 진(proper) 회문 접미사.  O(n)에 온라인 구성
struct Eertree {
    struct Node { int len, link; std::map<char, int> next; };
    std::vector<Node> t; std::string s; int last;
    Eertree() : t{{-1, 0, {}}, {0, 0, {}}}, last(1) {}           // 0 = 길이 -1 인 가상 루트, 1 = 빈 문자열
    int getLink(int v) { while (true) { int pos = (int)s.size() - 1 - t[v].len - 1; if (pos >= 0 && s[pos] == s.back()) return v; v = t[v].link; } }
    void add(char c) {
        s += c;
        int cur = getLink(last);
        if (!t[cur].next.count(c)) {
            int nw = t.size(); t.push_back({t[cur].len + 2, 0, {}});
            if (t[nw].len == 1) t[nw].link = 1;
            else t[nw].link = t[getLink(t[cur].link)].next[c];
            t[cur].next[c] = nw;
        }
        last = t[cur].next[c];
    }
    int distinctPalindromes() const { return (int)t.size() - 2; }
};

int main() {
    for (std::string s : {"eertree", "aaaa", "abacaba", "abcde"}) {
        Eertree e; for (char c : s) e.add(c);
        std::set<std::string> brute;
        for (size_t i = 0; i < s.size(); i++) for (size_t l = 1; i + l <= s.size(); l++) {
            std::string x = s.substr(i, l); if (x == std::string(x.rbegin(), x.rend())) brute.insert(x);
        }
        assert(e.distinctPalindromes() == (int)brute.size());
    }
    Eertree e; for (char c : std::string("eertree")) e.add(c);
    std::cout << "PalindromicTree(eertree): " << e.distinctPalindromes() << " distinct palindromes" << std::endl;
    return 0;
}
// Time Complexity: O(n log σ)
// Space Complexity: O(n)
```
# Part 10. 롤링 해시
## PolynomialRollingHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <unordered_set>
#include <vector>

// 다항 롤링 해시(문자열 관점의 요약, 정본은 Hash.md Part 5): H(s[l..r)) = P[r] − P[l]·B^(r−l).  접두사 해시를 한 번 만들어 두면 임의 부분 문자열의 해시를 O(1) 에 구한다.
//  여기서는 mod 2^61−1 과 무작위 밑을 쓰고 ① 같은 부분 문자열 ↔ 같은 해시를 직접 비교와 대조  ② 해시로 LCP 를 이분 탐색(O(log n))해 두 접미사를 사전순으로 비교 — std::string 비교와 일치
//  ③ 팰린드롬 판정(정방향 해시 = 역방향 해시)  ④ 모듈러가 작으면(10^9+7) 생일 역설로 서로 다른 문자열 20 만 개에서 충돌이 실제로 나타난다.
typedef std::uint64_t u64; __extension__ typedef unsigned __int128 u128;
const u64 P = (1ULL << 61) - 1;
u64 mulmod(u64 a, u64 b) { u128 t = (u128)a * b; u64 r = (u64)(t & P) + (u64)(t >> 61); if (r >= P) r -= P; if (r >= P) r -= P; return r; }
struct PRH {
    std::vector<u64> p, pw; PRH() {}
    PRH(const std::string& s, u64 B) : p(s.size() + 1, 0), pw(s.size() + 1, 1) { for (size_t i = 0; i < s.size(); ++i) { u64 v = mulmod(p[i], B) + (unsigned char)s[i]; p[i + 1] = v >= P ? v - P : v; pw[i + 1] = mulmod(pw[i], B); } }
    u64 get(size_t l, size_t r) const { u64 sub = mulmod(p[l], pw[r - l]); return p[r] >= sub ? p[r] - sub : p[r] + P - sub; }
};
size_t lcpByHash(const PRH& h, size_t n, size_t i, size_t j) { size_t lo = 0, hi = n - std::max(i, j); while (lo < hi) { size_t mid = (lo + hi + 1) / 2; if (h.get(i, i + mid) == h.get(j, j + mid)) lo = mid; else hi = mid - 1; } return lo; }      // 같은 길이 접두사의 해시가 같은 최대 길이
int compareSuffix(const std::string& s, const PRH& h, size_t i, size_t j) { size_t l = lcpByHash(h, s.size(), i, j); if (i + l == s.size() || j + l == s.size()) return i == j ? 0 : (i + l == s.size() ? -1 : 1); return (unsigned char)s[i + l] < (unsigned char)s[j + l] ? -1 : 1; }

int main() {
    std::mt19937_64 rng(13); u64 B = 256 + rng() % (P - 256);
    { PRH h("abcabcabc", B); assert(h.get(0, 3) == h.get(3, 6) && h.get(3, 6) == h.get(6, 9) && h.get(0, 3) != h.get(1, 4) && h.get(2, 2) == 0); }
    for (int it = 0; it < 2000; ++it) {                                                          // ① 모든 부분 문자열 쌍: 같음 ↔ 해시 같음
        std::string s(1 + rng() % 25, 'a'); for (char& c : s) c = (char)('a' + rng() % 2); PRH h(s, B); size_t n = s.size();
        for (size_t l1 = 0; l1 < n; ++l1) for (size_t l2 = 0; l2 < n; ++l2) { size_t len = 1 + rng() % std::min(n - l1, n - l2); assert((h.get(l1, l1 + len) == h.get(l2, l2 + len)) == (s.compare(l1, len, s, l2, len) == 0)); }
        for (size_t i = 0; i < n; ++i) for (size_t j = 0; j < n; ++j) { size_t l = lcpByHash(h, n, i, j), t = 0; while (i + t < n && j + t < n && s[i + t] == s[j + t]) ++t; assert(l == t);          // ② LCP 와 사전순 비교
            int want = s.compare(i, std::string::npos, s, j, std::string::npos); assert(compareSuffix(s, h, i, j) == (want < 0 ? -1 : want > 0 ? 1 : 0)); }
    }
    for (int it = 0; it < 3000; ++it) {                                                          // ③ 팰린드롬: s[l..r) 이 회문 ↔ 정방향 해시 == 역방향 해시
        std::string s(1 + rng() % 30, 'a'); for (char& c : s) c = (char)('a' + rng() % 2); std::string r(s.rbegin(), s.rend()); PRH f(s, B), b(r, B); size_t n = s.size();
        for (size_t l = 0; l < n; ++l) for (size_t e = l + 1; e <= n; ++e) { bool pal = true; for (size_t k = 0; k < (e - l) / 2; ++k) pal = pal && s[l + k] == s[e - 1 - k]; assert((f.get(l, e) == b.get(n - e, n - l)) == pal); }
    }
    // ④ 작은 모듈러(10^9+7) vs 2^61−1: 길이 12 의 서로 다른 무작위 문자열 20 만 개 (생일 역설: 기대 충돌 ≈ n²/2M ≈ 20)
    { std::set<std::string> distinct; while (distinct.size() < 200000) { std::string s(12, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); distinct.insert(s); }
      std::unordered_set<u64> small, big; long collSmall = 0, collBig = 0; for (auto& s : distinct) { u64 hs = 0; for (unsigned char c : s) hs = (hs * 131 + c) % 1000000007ULL; collSmall += !small.insert(hs).second; PRH h(s, B); collBig += !big.insert(h.get(0, s.size())).second; }
      assert(collSmall >= 5 && collBig == 0);
      // 큰 입력: 100 만 글자에서 무작위 부분 문자열 쌍 10 만 개
      std::string text(1000000, 'a'); for (char& c : text) c = "ab"[rng() % 2]; PRH h(text, B); for (int q = 0; q < 100000; ++q) { size_t len = 1 + rng() % 50, l1 = rng() % (text.size() - len), l2 = q % 2 ? (l1 + len * 5) % (text.size() - len) : rng() % (text.size() - len); assert((h.get(l1, l1 + len) == h.get(l2, l2 + len)) == (text.compare(l1, len, text, l2, len) == 0)); }
      std::cout << "PolynomialRollingHash: substring equality, hash-LCP suffix comparison and palindrome tests matched direct comparison; 200000 distinct 12-letter strings collided " << collSmall << " times under mod 10^9+7 and " << collBig << " under 2^61-1" << std::endl; }
    return 0;
}
// Time Complexity: 전처리 O(n), 부분 문자열 해시 O(1), 해시 LCP O(log n)
// Space Complexity: O(n)
```
## RabinFingerprint()
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

// 라빈 지문(문자열 관점의 요약, 정본은 Hash.md Part 5) — 진짜 라빈 지문은 정수 모듈러가 아니라 GF(2) 위의 다항식 나머지다: 바이트열을 계수가 0/1 인 다항식으로 보고 *기약 다항식* P(x) 로 나눈 나머지.
// 윈도 w 바이트를 한 칸 밀 때 표 두 개(새 바이트 밀어 넣기, 낡은 바이트 빼기)로 O(1) 갱신하고, XOR 만 쓰므로 선형이다: f(a ⊕ b) = f(a) ⊕ f(b).  내용 기반 청크 분할(rsync, LBFS, 중복 제거 저장소)에 쓴다.
//  ① 기약성 판정(Rabin 의 시험: x^(2^d) ≡ x 이고 d 의 소인수 q 마다 gcd(x^(2^(d/q)) − x, P) = 1)을 구현하고 차수 ≤ 12 의 모든 다항식에서 기약 다항식의 개수(목걸이 공식)와 일치하는지 확인.
//  ② 기약 31 차 다항식을 찾아 슬라이딩 갱신 = 처음부터 계산(비트 단위 나눗셈)임을 확인, 선형성 확인.  ③ 내용 기반 청크: 지문 하위 13 비트가 0 이면 경계 — 평균 8 KiB, 앞에 한 바이트를 끼워 넣어도 거의 모든 청크가 그대로 (고정 크기 분할은 전부 달라진다).
typedef std::uint64_t u64; typedef std::uint32_t u32;
int degreeOf(u64 p) { return 63 - __builtin_clzll(p); }
u64 pmod(u64 a, u64 m) { int dm = degreeOf(m); while (a && degreeOf(a) >= dm) a ^= m << (degreeOf(a) - dm); return a; }                    // GF(2)[x] 의 나머지
u64 pmulmod(u64 a, u64 b, u64 m) { u64 r = 0; a = pmod(a, m); while (b) { if (b & 1) r ^= a; b >>= 1; a <<= 1; if (a >> degreeOf(m) & 1) a ^= m; } return r; }      // a·b mod m (deg m ≤ 62)
u64 pgcd(u64 a, u64 b) { while (b) { u64 t = pmod(a, b); a = b; b = t; } return a; }
u64 xpow2k(int k, u64 m) { u64 r = 2; for (int i = 0; i < k; ++i) r = pmulmod(r, r, m); return r; }                                           // x^(2^k) mod m
bool irreducible(u64 p) {                                                                                                                 // Rabin 의 시험
    int d = degreeOf(p); if (d < 1) return false; if (pmod(xpow2k(d, p) ^ 2, p) != 0) return false;                                                         // x^(2^d) ≡ x (mod p)
    for (int q = 2; q <= d; ++q) if (d % q == 0) { bool prime = true; for (int r = 2; r * r <= q; ++r) if (q % r == 0) prime = false; if (prime) { u64 g = pgcd(p, xpow2k(d / q, p) ^ 2); if (g != 1) return false; } }
    return true;
}
bool bruteIrreducible(u64 p) { int d = degreeOf(p); for (u64 f = 2; degreeOf(f) <= d / 2; ++f) if (pmod(p, f) == 0) return false; return d >= 1; }                     // 모든 낮은 차수 인수로 나눠 본다 (차수 ≤ 12)
long necklace(int d) { long s = 0; for (int k = 1; k <= d; ++k) if (d % k == 0) { long mu; int m = d / k; mu = 1; int t = m; for (int pr = 2; pr <= t; ++pr) if (t % pr == 0) { int e = 0; while (t % pr == 0) { t /= pr; ++e; } mu = e > 1 ? 0 : -mu; } s += mu * (1L << k); } return s / d; }       // 차수 d 기약 다항식의 수 (1/d)·Σ μ(d/k)·2^k
struct Rabin {
    static const int D = 31; u64 P; int w; u32 push[256], pop[256]; u32 f = 0;                  // 지문은 D 비트
    Rabin(u64 poly, int window) : P(poly), w(window) {
        for (int t = 0; t < 256; ++t) push[t] = (u32)pmod((u64)t << D, P);                    // 위로 밀려난 상위 8 비트의 나머지
        for (int b = 0; b < 256; ++b) { u64 v = (u64)b; for (int i = 0; i < 8 * (w - 1); ++i) { v <<= 1; if (v >> D & 1) v ^= P; } pop[b] = (u32)v; }                         // b·x^(8(w−1)) mod P
    }
    void reset() { f = 0; }
    void slide(unsigned char in, unsigned char out) { u32 g = f ^ pop[out]; u32 top = g >> (D - 8); g = ((g << 8) & ((1u << D) - 1)) | in; f = g ^ push[top]; }              // 낡은 바이트의 기여를 빼고 한 바이트 밀어 넣기
    void feed(unsigned char in) { u32 top = f >> (D - 8); f = (((f << 8) & ((1u << D) - 1)) | in) ^ push[top]; }                                                                    // 윈도가 아직 덜 찼을 때
};
u32 directFingerprint(const unsigned char* p, int w, u64 P) { u64 v = 0; for (int i = 0; i < w; ++i) for (int bit = 7; bit >= 0; --bit) { v = (v << 1) | (p[i] >> bit & 1); if (v >> Rabin::D & 1) v ^= P; } return (u32)v; }       // 비트 단위 긴 나눗셈

int main() {
    // ① 기약성 판정 검증: 차수 d ≤ 12 의 모든 최고차 계수 1 다항식 (2^d 개) — 시험과 무차별(낮은 차수 인수) 판정이 일치하고 개수는 목걸이 공식과 같다
    for (int d = 1; d <= 12; ++d) { long cnt = 0; for (u64 p = 1ULL << d; p < (2ULL << d); ++p) { bool a = irreducible(p), b = bruteIrreducible(p); assert(a == b); cnt += a; } assert(cnt == necklace(d)); }
    assert(necklace(8) == 30 && necklace(12) == 335 && necklace(16) == 4080);
    // ② 31 차 기약 다항식을 찾는다 (결정적 탐색)
    std::mt19937_64 rng(5); u64 poly = 0; for (u64 cand = (1ULL << 31) | 1 | (rng() & 0x7FFFFFFE); ; cand = (1ULL << 31) | 1 | (rng() & 0x7FFFFFFE)) if (irreducible(cand)) { poly = cand; break; }
    assert(degreeOf(poly) == 31 && irreducible(poly) && bruteIrreducible(poly));                                       // 낮은 차수(≤ 15) 인수가 없음을 무차별로도 확인
    const int w = 48; Rabin r(poly, w); std::vector<unsigned char> data(300000); for (auto& b : data) b = (unsigned char)rng();
    r.reset(); for (int i = 0; i < w; ++i) r.feed(data[i]); assert(r.f == directFingerprint(data.data(), w, poly));
    for (size_t i = w; i < data.size(); ++i) { r.slide(data[i], data[i - w]); if (i % 97 == 0 || i < 200) assert(r.f == directFingerprint(&data[i - w + 1], w, poly)); }          // 슬라이딩 == 처음부터
    { unsigned char a[16], b[16], c[16]; for (int i = 0; i < 16; ++i) { a[i] = (unsigned char)rng(); b[i] = (unsigned char)rng(); c[i] = a[i] ^ b[i]; } assert(directFingerprint(c, 16, poly) == (directFingerprint(a, 16, poly) ^ directFingerprint(b, 16, poly))); }   // 선형성
    // ③ 내용 기반 청크 분할: 경계 = 지문 하위 13 비트가 0
    auto chunk = [&](const std::vector<unsigned char>& d) { std::vector<std::vector<unsigned char>> chunks; Rabin rb(poly, w); std::vector<unsigned char> cur; for (size_t i = 0; i < d.size(); ++i) { cur.push_back(d[i]); if (cur.size() > (size_t)w) rb.slide(d[i], d[i - w]); else rb.feed(d[i]); if (cur.size() >= (size_t)w && (rb.f & 8191) == 0) { chunks.push_back(cur); cur.clear(); rb.reset(); /* 경계 뒤에는 새로 시작 */ } } if (!cur.empty()) chunks.push_back(cur); return chunks; };
    std::vector<unsigned char> big(4 << 20); for (auto& b : big) b = (unsigned char)rng(); auto c1 = chunk(big); size_t total = 0; for (auto& c : c1) total += c.size(); assert(total == big.size());
    double mean = (double)big.size() / c1.size(); assert(mean > 6000 && mean < 11000);                                                  // 평균 약 2^13 = 8192 (+ 윈도 길이)
    std::vector<unsigned char> edited = big; edited.insert(edited.begin() + 1000, 0xAB); auto c2 = chunk(edited);
    std::set<std::vector<unsigned char>> s1(c1.begin(), c1.end()); long same = 0; for (auto& c : c2) same += s1.count(c); double sameFrac = (double)same / c2.size();
    // 고정 크기 8 KiB 분할: 한 바이트를 끼워 넣으면 그 뒤의 청크가 전부 어긋난다
    auto fixedChunks = [&](const std::vector<unsigned char>& d) { std::set<std::vector<unsigned char>> s; for (size_t i = 0; i < d.size(); i += 8192) s.insert(std::vector<unsigned char>(d.begin() + i, d.begin() + std::min(d.size(), i + 8192))); return s; };
    std::set<std::vector<unsigned char>> f1 = fixedChunks(big), f2 = fixedChunks(edited); long fixedSame = 0; for (auto& c : f2) fixedSame += f1.count(c); double fixedFrac = (double)fixedSame / f2.size();
    assert(sameFrac > 0.97 && fixedFrac < 0.05);
    std::cout << "RabinFingerprint: irreducibility test agreed with brute force for all polynomials of degree <= 12 (counts 30, 335, 4080 for degrees 8, 12, 16); sliding fingerprint = direct computation; content-defined chunks averaged " << mean << " bytes and " << 100 * sameFrac << "% survived a 1-byte insertion vs " << 100 * fixedFrac << "% for fixed-size chunks" << std::endl;
    return 0;
}
// Time Complexity: 윈도 이동 O(1) (표 조회 2 번), 처음부터 계산 O(w)
// Space Complexity: O(1) (표 2 × 256 개)
```
## SubstringHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

// 부분 문자열 해시: 모듈러가 둘인 이중 해시로 충돌 확률을 ~10^−18 수준으로 낮추면 두 부분 문자열이 같은지를 O(1) 에 판정할 수 있다.
//  ① 길이 L 인 서로 다른 부분 문자열의 개수를 해시 집합으로 세고 std::set<string> 과 대조(모든 L).  ② 두 문자열의 최장 공통 부분 문자열 길이를 *이분 탐색 + 해시 집합* 으로 O(n log n) 에 구해 DP 와 대조.
//  ③ 단일 모듈러는 생일 역설로 충돌(서로 다른 부분 문자열인데 해시가 같음)이 나고, 이중 해시는 나지 않는다.
typedef std::uint64_t u64;
struct DoubleHash {
    static const u64 M1 = 1000000007ULL, M2 = 998244353ULL; u64 B1, B2; std::vector<u64> p1, p2, w1, w2;
    DoubleHash(const std::string& s, u64 b1, u64 b2) : B1(b1), B2(b2), p1(s.size() + 1), p2(s.size() + 1), w1(s.size() + 1, 1), w2(s.size() + 1, 1) {
        for (size_t i = 0; i < s.size(); ++i) { p1[i + 1] = (p1[i] * B1 + (unsigned char)s[i]) % M1; w1[i + 1] = w1[i] * B1 % M1; p2[i + 1] = (p2[i] * B2 + (unsigned char)s[i]) % M2; w2[i + 1] = w2[i] * B2 % M2; }
    }
    u64 get(size_t l, size_t r) const { u64 a = (p1[r] + M1 - p1[l] * w1[r - l] % M1) % M1, b = (p2[r] + M2 - p2[l] * w2[r - l] % M2) % M2; return a << 32 | b; }        // 두 값을 한 64 비트로
};
size_t lcsubstringDP(const std::string& a, const std::string& b) { std::vector<int> prev(b.size() + 1, 0), cur(b.size() + 1, 0); int best = 0; for (size_t i = 1; i <= a.size(); ++i) { for (size_t j = 1; j <= b.size(); ++j) { cur[j] = a[i - 1] == b[j - 1] ? prev[j - 1] + 1 : 0; best = std::max(best, cur[j]); } std::swap(prev, cur); } return (size_t)best; }
size_t lcsubstringHash(const std::string& a, const std::string& b, u64 b1, u64 b2) {
    DoubleHash ha(a, b1, b2), hb(b, b1, b2); size_t lo = 0, hi = std::min(a.size(), b.size());
    auto ok = [&](size_t L) { std::unordered_set<u64> sa; for (size_t i = 0; i + L <= a.size(); ++i) sa.insert(ha.get(i, i + L)); for (size_t j = 0; j + L <= b.size(); ++j) if (sa.count(hb.get(j, j + L))) return true; return false; };      // 길이 L 인 공통 부분 문자열이 있는가 (단조)
    while (lo < hi) { size_t mid = (lo + hi + 1) / 2; if (ok(mid)) lo = mid; else hi = mid - 1; } return lo;
}

int main() {
    std::mt19937_64 rng(29); u64 b1 = 256 + rng() % 1000000, b2 = 256 + rng() % 1000000;
    { std::string s = "abababcabababc"; DoubleHash h(s, 131, 137); assert(h.get(0, 7) == h.get(7, 14) && h.get(0, 6) != h.get(1, 7)); }
    for (int it = 0; it < 3000; ++it) {                                                                              // ① 길이별 서로 다른 부분 문자열 수
        std::string s(1 + rng() % 40, 'a'); int sigma = 2 + (int)(rng() % 3); for (char& c : s) c = (char)('a' + rng() % sigma); DoubleHash h(s, b1, b2);
        for (size_t L = 1; L <= s.size(); ++L) { std::set<std::string> brute; std::unordered_set<u64> hashed; for (size_t i = 0; i + L <= s.size(); ++i) { brute.insert(s.substr(i, L)); hashed.insert(h.get(i, i + L)); } assert(hashed.size() == brute.size()); }
    }
    for (int it = 0; it < 3000; ++it) {                                                                              // ② 최장 공통 부분 문자열: 해시 이분 탐색 == DP
        std::string a(rng() % 40, 'a'), b(rng() % 40, 'a'); int sigma = 2 + (int)(rng() % 3); for (char& c : a) c = (char)('a' + rng() % sigma); for (char& c : b) c = (char)('a' + rng() % sigma); assert(lcsubstringHash(a, b, b1, b2) == lcsubstringDP(a, b));
    }
    { std::string a(3000, 'a'), b(3000, 'a'); for (char& c : a) c = "ab"[rng() % 2]; for (char& c : b) c = "ab"[rng() % 2]; std::string common = a.substr(1000, 200); b.replace(1500, 200, common); assert(lcsubstringHash(a, b, b1, b2) == lcsubstringDP(a, b) && lcsubstringDP(a, b) >= 200); }
    // ③ 단일 모듈러 충돌: 서로 다른 길이 12 문자열 30 만 개 — 기대 충돌 n²/(2M) ≈ 45 (10^9+7), 이중 해시는 0
    { std::set<std::string> distinct; while (distinct.size() < 300000) { std::string s(12, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); distinct.insert(s); }
      std::unordered_set<u64> one, two; long collOne = 0, collTwo = 0; for (auto& s : distinct) { DoubleHash h(s, b1, b2); u64 v = h.get(0, s.size()); collOne += !one.insert(v >> 32).second; collTwo += !two.insert(v).second; }
      assert(collOne >= 10 && collOne <= 120 && collTwo == 0);
      std::cout << "SubstringHash: distinct-substring counts and longest-common-substring (hash binary search vs DP) matched; " << distinct.size() << " distinct strings gave " << collOne << " collisions with one modulus and " << collTwo << " with two" << std::endl; }
    return 0;
}
// Time Complexity: 전처리 O(n), 비교 O(1), 최장 공통 부분 문자열 O((n + m) log min(n, m))
// Space Complexity: O(n)
```
## LongestCommonSubstring()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 최장 공통 부분 문자열: a 의 접미사 자동자를 만들고 b 를 한 글자씩 흘려 보내며 "현재 일치 길이"를 추적한다. O(|a| + |b|)
struct SAM {
    struct State { int len = 0, link = -1; std::map<char, int> next; };
    std::vector<State> st; int last = 0;
    SAM() : st(1) {}
    void extend(char c) {
        int cur = st.size(); st.push_back({}); st[cur].len = st[last].len + 1;
        int p = last;
        while (p != -1 && !st[p].next.count(c)) { st[p].next[c] = cur; p = st[p].link; }
        if (p == -1) st[cur].link = 0;
        else {
            int q = st[p].next[c];
            if (st[p].len + 1 == st[q].len) st[cur].link = q;
            else {
                int cl = st.size(); st.push_back(st[q]); st[cl].len = st[p].len + 1;
                while (p != -1 && st[p].next[c] == q) { st[p].next[c] = cl; p = st[p].link; }
                st[q].link = st[cur].link = cl;
            }
        }
        last = cur;
    }
};
std::string lcsubstr(const std::string& a, const std::string& b) {
    SAM sam; for (char c : a) sam.extend(c);
    int v = 0, l = 0, best = 0, bestEnd = 0;
    for (size_t i = 0; i < b.size(); i++) {
        char c = b[i];
        while (v && !sam.st[v].next.count(c)) { v = sam.st[v].link; l = sam.st[v].len; }   // 실패 시 접미사 링크로 후퇴
        if (sam.st[v].next.count(c)) { v = sam.st[v].next[c]; l++; }
        if (l > best) { best = l; bestEnd = (int)i; }
    }
    return b.substr(bestEnd - best + 1, best);
}

int main() {
    assert(lcsubstr("abcdxyz", "xyzabcd") == "abcd");
    assert(lcsubstr("zxabcdezy", "yzabcdezx") == "abcdez");
    assert(lcsubstr("abc", "xyz").empty());
    std::cout << "LongestCommonSubstring(abcdxyz, xyzabcd) = " << lcsubstr("abcdxyz", "xyzabcd") << std::endl;
    return 0;
}
// Time Complexity: O(|a| log σ + |b| log σ)
// Space Complexity: O(|a|)
```
# Part 11. 압축·변환
## LZW()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// LZW: 지금까지 본 문자열을 사전에 등록하며 코드로 대체한다. 사전은 부호기와 복호기가 같은 규칙으로 따로 만들기 때문에 사전을 전송하지 않는다 (GIF, 옛 Unix compress)
std::vector<int> lzwEncode(const std::string& in) {
    std::map<std::string, int> dict;
    for (int i = 0; i < 256; i++) dict[std::string(1, (char)i)] = i;
    std::vector<int> out; std::string w;
    for (char c : in) {
        std::string wc = w + c;
        if (dict.count(wc)) w = wc;
        else { out.push_back(dict[w]); dict[wc] = dict.size(); w = std::string(1, c); }
    }
    if (!w.empty()) out.push_back(dict[w]);
    return out;
}
std::string lzwDecode(const std::vector<int>& codes) {
    std::map<int, std::string> dict;
    for (int i = 0; i < 256; i++) dict[i] = std::string(1, (char)i);
    std::string w = dict[codes[0]], out = w;
    for (size_t i = 1; i < codes.size(); i++) {
        std::string entry = dict.count(codes[i]) ? dict[codes[i]] : w + w[0];     // 아직 등록 전인 코드(KwKwK 경우)
        out += entry;
        dict[dict.size()] = w + entry[0];
        w = entry;
    }
    return out;
}

int main() {
    std::string s = "TOBEORNOTTOBEORTOBEORNOT";
    auto codes = lzwEncode(s);
    assert(lzwDecode(codes) == s);
    assert(codes.size() < s.size());                                   // 반복 덕분에 코드 수가 줄어든다
    assert(codes[0] == 'T' && codes[9] == 256);                        // 9번째 코드: 처음으로 사전 항목("TO")을 사용
    std::string rep(1000, 'a');
    assert(lzwDecode(lzwEncode(rep)) == rep && lzwEncode(rep).size() < 60);
    std::cout << "LZW: " << s.size() << " chars -> " << codes.size() << " codes" << std::endl;
    return 0;
}
// Time Complexity: O(n log D)
// Space Complexity: O(D)  (사전 크기)
```
## BurrowsWheelerTransform()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <numeric>
#include <string>
#include <vector>
#include <cassert>

// BWT: 모든 회전을 정렬해 마지막 열만 취한다. 같은 문맥 뒤의 글자들이 모여 반복(run)이 늘어나므로 압축에 유리하다(bzip2).
// 가역 변환: 마지막 열 L 과 정렬된 첫 열 F 사이의 LF 대응으로 원문을 복원한다 (끝 표식 '$' 필요)
std::string bwt(std::string s) {
    s += '$';
    std::vector<int> idx(s.size()); std::iota(idx.begin(), idx.end(), 0);
    std::sort(idx.begin(), idx.end(), [&](int a, int b) {                       // 회전 비교
        for (size_t k = 0; k < s.size(); k++) { char x = s[(a + k) % s.size()], y = s[(b + k) % s.size()]; if (x != y) return x < y; }
        return false; });
    std::string L;
    for (int i : idx) L += s[(i + s.size() - 1) % s.size()];
    return L;
}
std::string inverseBwt(const std::string& L) {
    size_t n = L.size();
    std::vector<int> order(n); std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(), [&](int a, int b) { return L[a] < L[b]; });   // order[i] = F 의 i번째 글자가 L 의 몇 번째인가
    size_t row = std::find(L.begin(), L.end(), '$') - L.begin();
    std::string out;
    for (size_t i = 0; i < n; i++) { row = order[row]; out += L[row]; }
    // 위 루프는 '$' 다음 글자부터 차례로 복원한다 (마지막에 '$' 도달)
    return out.substr(0, n - 1);
}

int main() {
    assert(bwt("banana") == "annb$aa");                       // 교과서의 표준 예
    assert(inverseBwt("annb$aa") == "banana");
    for (std::string s : {"abracadabra", "mississippi", "aaaa", "a"}) assert(inverseBwt(bwt(s)) == s);
    // 효과: 같은 글자가 이어진다 -> BWT 결과의 run 개수가 줄어든다
    auto runs = [](const std::string& x) { int r = 1; for (size_t i = 1; i < x.size(); i++) r += x[i] != x[i - 1]; return r; };
    std::string text = "mississippi$mississippi$mississippi";
    assert(runs(bwt("mississippimississippimississippi")) < runs(text));
    std::cout << "BWT(banana) = " << bwt("banana") << std::endl;
    return 0;
}
// Time Complexity: 순진한 구현 O(n² log n), 접미사 배열 기반 O(n log n)
// Space Complexity: O(n)
```
## MoveToFront()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstring>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// MTF: 알파벳을 리스트로 두고, 글자를 만나면 "현재 위치(인덱스)"를 출력한 뒤 맨 앞으로 옮긴다. 같은 글자가 가까이 모여 있으면 0, 1 같은 작은 수가 많아져 이후 엔트로피 부호화(허프먼 등)가 잘 된다 — BWT 뒤에 쓰는 이유.
//  ① 독립 오라클(리스트를 흉내 내지 않고 정의로 계산): 이미 나온 글자의 출력 = "직전 등장 이후 나온 서로 다른 글자의 수"(스택 거리), 처음 나온 글자 c 의 출력 = c + (그때까지 나온 서로 다른 글자 중 c 보다 큰 것의 수).
//  ② 왕복 복원(무작위 바이트 10 만 개 문자열)  ③ 지역성이 있는 데이터에서 출력의 0 비율과 영차 엔트로피가 크게 줄고, 지역성이 없는 순환 데이터(256 글자를 차례로)는 매번 255 라는 최악.
std::vector<int> mtfEncode(const std::string& s) {
    unsigned char alpha[256]; std::iota(alpha, alpha + 256, 0); std::vector<int> out;
    for (unsigned char c : s) { int i = 0; while (alpha[i] != c) ++i; out.push_back(i); std::memmove(alpha + 1, alpha, (size_t)i); alpha[0] = c; }
    return out;
}
std::string mtfDecode(const std::vector<int>& codes) {
    unsigned char alpha[256]; std::iota(alpha, alpha + 256, 0); std::string out;
    for (int i : codes) { unsigned char c = alpha[i]; out += (char)c; std::memmove(alpha + 1, alpha, (size_t)i); alpha[0] = c; }
    return out;
}
std::vector<int> mtfOracle(const std::string& s) {
    std::vector<int> out;
    for (size_t p = 0; p < s.size(); ++p) { unsigned char c = s[p]; int prev = -1; for (int q = (int)p - 1; q >= 0; --q) if ((unsigned char)s[q] == c) { prev = q; break; }
        std::set<unsigned char> seen; if (prev >= 0) { for (size_t q = (size_t)prev + 1; q < p; ++q) seen.insert((unsigned char)s[q]); out.push_back((int)seen.size()); }
        else { for (size_t q = 0; q < p; ++q) if ((unsigned char)s[q] > c) seen.insert((unsigned char)s[q]); out.push_back((int)c + (int)seen.size()); } }
    return out;
}
double entropy(const std::vector<int>& v) { std::map<int, long> h; for (int x : v) ++h[x]; double e = 0; for (auto& kv : h) { double p = (double)kv.second / v.size(); e -= p * std::log2(p); } return e; }

int main() {
    auto e = mtfEncode("bananaaa"); assert(mtfDecode(e) == "bananaaa" && e.back() == 0 && e[e.size() - 2] == 0 && (e == mtfOracle("bananaaa")));
    std::mt19937 rng(14);
    for (int it = 0; it < 20000; ++it) { std::string s(rng() % 40, 'a'); int sigma = 1 + (int)(rng() % 10); for (char& c : s) c = (char)(rng() % 3 == 0 ? rng() % 256 : 'a' + rng() % sigma); assert(mtfEncode(s) == mtfOracle(s) && mtfDecode(mtfEncode(s)) == s); }          // ① ②
    for (int it = 0; it < 100; ++it) { std::string s(100000, 'a'); for (char& c : s) c = (char)rng(); assert(mtfDecode(mtfEncode(s)) == s); }
    // ③ 지역성: 같은 글자가 10~50 번씩 덩어리로 나오는 데이터 (BWT 결과와 비슷)
    { std::string s; while (s.size() < 200000) s.append(10 + rng() % 41, "abcdefgh"[rng() % 8]); std::vector<int> raw(s.begin(), s.end()), m = mtfEncode(s); long zeros = std::count(m.begin(), m.end(), 0); double zeroFrac = (double)zeros / m.size();
      assert(zeroFrac > 0.95 && entropy(m) < 0.5 * entropy(raw) && mtfDecode(m) == s);
      std::string cyc; for (int i = 0; i < 256 * 40; ++i) cyc += (char)i; std::vector<int> c = mtfEncode(cyc); long big = 0; for (size_t i = 256; i < c.size(); ++i) big += c[i] == 255; assert(big == (long)(c.size() - 256));                   // 지역성 없는 순환: 첫 바퀴 뒤에는 매번 255
      std::cout << "MoveToFront: zeros made up " << 100 * zeroFrac << "% of the output for clustered data and entropy fell from " << entropy(raw) << " to " << entropy(m) << " bits/symbol; a cyclic sweep over 256 symbols produced 255 every time" << std::endl; }
    return 0;
}
// Time Complexity: O(n·σ) (σ ≤ 256)
// Space Complexity: O(σ)
```
## Huffman()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <map>
#include <memory>
#include <queue>
#include <string>
#include <vector>
#include <cassert>

// 허프먼 부호: 자주 나오는 글자에 짧은 비트열을 준다. 가장 빈도가 낮은 두 노드를 합치는 탐욕 알고리즘으로 최적의 접두사 부호를 만든다.
// 평균 부호 길이 L 은 엔트로피 H 이상, H + 1 미만
struct Node { char c; long f; std::unique_ptr<Node> l, r; };
struct Cmp { bool operator()(const Node* a, const Node* b) const { return a->f > b->f || (a->f == b->f && a->c > b->c); } };
void assign(const Node* n, const std::string& code, std::map<char, std::string>& out) {
    if (!n->l && !n->r) { out[n->c] = code.empty() ? "0" : code; return; }
    assign(n->l.get(), code + "0", out); assign(n->r.get(), code + "1", out);
}

int main() {
    std::string text = "abracadabra alakazam";
    std::map<char, long> freq; for (char c : text) freq[c]++;
    std::vector<std::unique_ptr<Node>> pool;
    std::priority_queue<Node*, std::vector<Node*>, Cmp> pq;
    for (auto& kv : freq) { pool.push_back(std::make_unique<Node>(Node{kv.first, kv.second, nullptr, nullptr})); pq.push(pool.back().get()); }
    std::unique_ptr<Node> root;
    while (pq.size() > 1) {
        auto a = pq.top(); pq.pop(); auto b = pq.top(); pq.pop();
        auto parent = std::make_unique<Node>(Node{0, a->f + b->f, nullptr, nullptr});
        for (auto& p : pool) { if (p.get() == a) parent->l = std::move(p); }
        for (auto& p : pool) { if (p.get() == b) parent->r = std::move(p); }
        pool.push_back(std::move(parent)); pq.push(pool.back().get());
    }
    const Node* top = pq.top();
    std::map<char, std::string> code; assign(top, "", code);
    std::string bits; for (char c : text) bits += code[c];
    // 복호: 접두사 부호이므로 모호함 없이 비트를 따라 내려가면 된다
    std::string decoded; const Node* cur = top;
    for (char b : bits) { cur = (b == '0') ? cur->l.get() : cur->r.get(); if (!cur->l && !cur->r) { decoded += cur->c; cur = top; } }
    assert(decoded == text);
    for (auto& a : code) for (auto& b : code) if (a.first != b.first) assert(b.second.compare(0, a.second.size(), a.second) != 0);   // 접두사 부호
    double entropy = 0; for (auto& kv : freq) { double p = double(kv.second) / text.size(); entropy -= p * std::log2(p); }
    double avg = double(bits.size()) / text.size();
    assert(avg >= entropy - 1e-9 && avg < entropy + 1);
    assert(bits.size() < text.size() * 8);
    std::cout << "Huffman: " << text.size() * 8 << " bits -> " << bits.size() << " bits (entropy " << entropy << ", avg " << avg << ")" << std::endl;
    return 0;
}
// Time Complexity: O(n + σ log σ)
// Space Complexity: O(σ)
```
# Part 12. 편집 거리
## Levenshtein()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 레벤슈타인 거리: 삽입·삭제·치환 각 1 로 한 문자열을 다른 문자열로 바꾸는 최소 횟수. dp[i][j] = a[0..i) → b[0..j).  표를 거슬러 올라가면 실제 편집 연산열도 얻는다.
//  ① 표 DP · 두 행 DP · 재귀 무차별 · 띠(Ukkonen: 거리 ≤ k 만 필요하면 O(n·k)) · 비트 병렬(Hyyrö: 한쪽이 64 글자 이하면 텍스트 글자당 O(1) 워드 연산)을 서로 대조.
//  ② 성질: 대칭, 삼각부등식, |길이 차| ≤ d ≤ max(길이), 연산열을 a 에 적용하면 정확히 b 가 되고 M 이 아닌 연산 수 = d.
int levenshtein(const std::string& a, const std::string& b, std::string* script = nullptr) {
    size_t n = a.size(), m = b.size(); std::vector<std::vector<int>> d(n + 1, std::vector<int>(m + 1));
    for (size_t i = 0; i <= n; ++i) d[i][0] = (int)i; for (size_t j = 0; j <= m; ++j) d[0][j] = (int)j;
    for (size_t i = 1; i <= n; ++i) for (size_t j = 1; j <= m; ++j) d[i][j] = std::min({d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1])});
    if (script) { script->clear(); size_t i = n, j = m;
        while (i > 0 || j > 0) { if (i && j && d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1])) { *script += (a[i - 1] == b[j - 1]) ? 'M' : 'S'; --i; --j; } else if (i && d[i][j] == d[i - 1][j] + 1) { *script += 'D'; --i; } else { *script += 'I'; --j; } }
        std::reverse(script->begin(), script->end()); }
    return d[n][m];
}
int levTwoRow(const std::string& a, const std::string& b) { std::vector<int> prev(b.size() + 1), cur(b.size() + 1); for (size_t j = 0; j <= b.size(); ++j) prev[j] = (int)j; for (size_t i = 1; i <= a.size(); ++i) { cur[0] = (int)i; for (size_t j = 1; j <= b.size(); ++j) cur[j] = std::min({prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1])}); std::swap(prev, cur); } return prev[b.size()]; }
int levBrute(const std::string& a, const std::string& b, size_t i, size_t j) { if (i == a.size()) return (int)(b.size() - j); if (j == b.size()) return (int)(a.size() - i); if (a[i] == b[j]) return levBrute(a, b, i + 1, j + 1); return 1 + std::min({levBrute(a, b, i + 1, j), levBrute(a, b, i, j + 1), levBrute(a, b, i + 1, j + 1)}); }       // 같으면 그대로 진행해도 최적
int levBanded(const std::string& a, const std::string& b, int k, long* cells = nullptr) {             // 거리 ≤ k 이면 거리, 아니면 k+1
    int n = (int)a.size(), m = (int)b.size(); const int INF = k + 1; if (cells) *cells = 0; if (std::abs(n - m) > k) return INF; std::vector<int> prev(m + 2, INF), cur(m + 2, INF); long c = 0;
    for (int j = 0; j <= std::min(m, k); ++j) prev[j] = j;
    for (int i = 1; i <= n; ++i) { int lo = std::max(0, i - k), hi = std::min(m, i + k); if (lo > 0) cur[lo - 1] = INF; cur[hi + 1 <= m + 1 ? hi + 1 : m + 1] = INF; if (lo == 0) cur[0] = i <= k ? i : INF;
        for (int j = std::max(1, lo); j <= hi; ++j) { ++c; cur[j] = std::min({prev[j - 1] + (a[i - 1] != b[j - 1]), prev[j] + 1, cur[j - 1] + 1}); if (cur[j] > INF) cur[j] = INF; } std::swap(prev, cur); }
    if (cells) *cells = c; return std::min(prev[m], INF);
}
int levBits(const std::string& p, const std::string& t) {                                              // |p| ≤ 64 : 전역 편집 거리 (Hyyrö 2003)
    size_t m = p.size(); assert(m >= 1 && m <= 64); std::uint64_t peq[256] = {0}; for (size_t i = 0; i < m; ++i) peq[(unsigned char)p[i]] |= 1ULL << i;
    const std::uint64_t mask = m == 64 ? ~0ULL : (1ULL << m) - 1, hb = 1ULL << (m - 1); std::uint64_t pv = mask, mv = 0; int score = (int)m;
    for (unsigned char c : t) { std::uint64_t eq = peq[c], xv = eq | mv, xh = (((eq & pv) + pv) ^ pv) | eq, ph = mv | ~(xh | pv), mh = pv & xh;
        if (ph & hb) ++score; else if (mh & hb) --score; ph = ((ph << 1) | 1) & mask; mh = (mh << 1) & mask; pv = (mh | ~(xv | ph)) & mask; mv = ph & xv & mask; }
    return score;
}
std::string applyScript(const std::string& a, const std::string& b, const std::string& script) { std::string out; size_t i = 0, j = 0; for (char op : script) { if (op == 'M') { out += a[i++]; ++j; } else if (op == 'S') { out += b[j++]; ++i; } else if (op == 'D') ++i; else out += b[j++]; } assert(i == a.size() && j == b.size()); return out; }

int main() {
    std::string ops; assert(levenshtein("kitten", "sitting", &ops) == 3 && std::count(ops.begin(), ops.end(), 'M') == 4 && levenshtein("", "abc") == 3 && levenshtein("same", "same") == 0 && levenshtein("flaw", "lawn") == 2);
    std::mt19937 rng(36);
    for (int it = 0; it < 100000; ++it) {
        std::string a(rng() % 8, 'a'), b(rng() % 8, 'a'); int sigma = 1 + (int)(rng() % 3); for (char& c : a) c = (char)('a' + rng() % sigma); for (char& c : b) c = (char)('a' + rng() % sigma);
        std::string sc; int d = levenshtein(a, b, &sc); assert(d == levTwoRow(a, b) && d == levBrute(a, b, 0, 0) && d == levenshtein(b, a));                                      // ① 세 가지 + 대칭
        assert(applyScript(a, b, sc) == b && (int)(sc.size() - std::count(sc.begin(), sc.end(), 'M')) == d && d >= std::abs((int)a.size() - (int)b.size()) && d <= (int)std::max(a.size(), b.size()));    // ② 연산열·경계
        int k = (int)(rng() % 6); long cells; int bd = levBanded(a, b, k, &cells); assert(bd == (d <= k ? d : k + 1) && cells <= (long)a.size() * (2 * k + 1));                       // 띠
        if (!b.empty()) assert(levBits(b, a) == d);                                                                                                                          // 비트 병렬 (패턴 = b)
        std::string c(rng() % 8, 'a'); for (char& ch : c) ch = (char)('a' + rng() % sigma); assert(levenshtein(a, c) <= levenshtein(a, b) + levenshtein(b, c));                      // 삼각부등식
    }
    for (int it = 0; it < 2000; ++it) { std::string p(1 + rng() % 64, 'a'), t(rng() % 200, 'a'); for (char& c : p) c = (char)('a' + rng() % 4); for (char& c : t) c = (char)('a' + rng() % 4); assert(levBits(p, t) == levTwoRow(p, t)); }       // 비트 병렬: 패턴 64 글자까지
    { std::string a(5000, 'a'), b(5000, 'a'); for (char& c : a) c = (char)('a' + rng() % 4); b = a; for (int i = 0; i < 40; ++i) b[rng() % b.size()] = (char)('a' + rng() % 4); b.erase(100, 7); b.insert(3000, "xyz");
      int d = levTwoRow(a, b); long cells; int bd = levBanded(a, b, 80, &cells); assert(bd == d && d <= 60 && cells < 5000L * 161);                                                      // 띠 DP: 25 M 칸 대신 약 0.8 M 칸
      std::string p(64, 'a'), t(1000000, 'a'); for (char& c : p) c = (char)('a' + rng() % 4); for (char& c : t) c = (char)('a' + rng() % 4); int bits = levBits(p, t);
      std::cout << "Levenshtein: table, two-row, brute-force recursion, banded and bit-parallel versions agreed on 10^5 random pairs; banded DP touched " << cells << " cells instead of 25,000,000 (distance " << d << "); a 64-letter pattern against 10^6 text characters gave " << bits << " in 10^6 word operations" << std::endl; }
    return 0;
}
// Time Complexity: O(n·m), 띠 O(n·k), 비트 병렬 O(n·⌈m/64⌉)
// Space Complexity: O(n·m) (연산열 필요 시), 거리만 O(min(n, m))
```
## DamerauLevenshtein()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 다메라우-레벤슈타인: 인접한 두 글자의 맞바꿈(transposition)도 비용 1.  오타("teh" -> "the") 교정에 적합
// - 제한형(OSA): 한 부분 문자열을 두 번 편집하지 못한다  /  - 완전형: 제한 없음 (Lowrance-Wagner).  예: "CA" -> "ABC" 는 OSA 3, 완전형 2
int osa(const std::string& a, const std::string& b) {
    size_t n = a.size(), m = b.size();
    std::vector<std::vector<int>> d(n + 1, std::vector<int>(m + 1));
    for (size_t i = 0; i <= n; i++) d[i][0] = i;
    for (size_t j = 0; j <= m; j++) d[0][j] = j;
    for (size_t i = 1; i <= n; i++) for (size_t j = 1; j <= m; j++) {
        d[i][j] = std::min({d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] != b[j-1])});
        if (i > 1 && j > 1 && a[i-1] == b[j-2] && a[i-2] == b[j-1]) d[i][j] = std::min(d[i][j], d[i-2][j-2] + 1);
    }
    return d[n][m];
}
int damerau(const std::string& a, const std::string& b) {
    size_t n = a.size(), m = b.size(); int maxd = n + m;
    std::map<char, int> da;
    std::vector<std::vector<int>> d(n + 2, std::vector<int>(m + 2));
    d[0][0] = maxd;
    for (size_t i = 0; i <= n; i++) { d[i+1][0] = maxd; d[i+1][1] = i; }
    for (size_t j = 0; j <= m; j++) { d[0][j+1] = maxd; d[1][j+1] = j; }
    for (size_t i = 1; i <= n; i++) {
        int db = 0;
        for (size_t j = 1; j <= m; j++) {
            int k = da.count(b[j-1]) ? da[b[j-1]] : 0, l = db, cost = 1;
            if (a[i-1] == b[j-1]) { cost = 0; db = j; }
            d[i+1][j+1] = std::min({d[i][j] + cost, d[i+1][j] + 1, d[i][j+1] + 1, d[k][l] + (int)(i - k - 1) + 1 + (int)(j - l - 1)});
        }
        da[a[i-1]] = i;
    }
    return d[n+1][m+1];
}

int main() {
    assert(osa("teh", "the") == 1 && damerau("teh", "the") == 1);   // 맞바꿈은 한 번
    assert(osa("ca", "ac") == 1);
    assert(osa("CA", "ABC") == 3 && damerau("CA", "ABC") == 2);      // 완전형이 더 작다
    assert(damerau("kitten", "sitting") == 3 && damerau("", "ab") == 2);
    std::cout << "OSA(CA,ABC)=" << osa("CA", "ABC") << " Damerau(CA,ABC)=" << damerau("CA", "ABC") << std::endl;
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(n·m)
```
## LongestCommonSubstringDP()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 최장 공통 부분 문자열(연속) DP: dp[i][j] = a[i−1] == b[j−1] 이면 dp[i−1][j−1] + 1, 아니면 0.  최댓값이 답. 행 두 개만 쓰면 O(min) 공간.
//  ① 모든 부분 문자열을 모으는 무차별과 대조  ② 전혀 다른 알고리즘(두 문자열을 구분자로 이어 접미사 배열을 만들고, 서로 다른 문자열에서 온 인접 접미사의 LCP 최댓값)과 대조  ③ 칸 수 정확히 n·m, 같은 문자열이면 답은 n.
long g_cells = 0;
std::string lcsubstringDP(const std::string& a, const std::string& b) {
    std::vector<int> prev(b.size() + 1, 0), cur(b.size() + 1, 0); int best = 0, end = 0;
    for (size_t i = 1; i <= a.size(); ++i) { for (size_t j = 1; j <= b.size(); ++j) { ++g_cells; cur[j] = (a[i - 1] == b[j - 1]) ? prev[j - 1] + 1 : 0; if (cur[j] > best) { best = cur[j]; end = (int)i; } } std::swap(prev, cur); }
    return a.substr((size_t)(end - best), (size_t)best);
}
std::string bruteLcsubstring(const std::string& a, const std::string& b) { std::string best; for (size_t i = 0; i < a.size(); ++i) for (size_t l = 1; i + l <= a.size(); ++l) if (l > best.size() && b.find(a.substr(i, l)) != std::string::npos) best = a.substr(i, l); return best; }
size_t lcsubstringBySuffixArray(const std::string& a, const std::string& b) {                           // a + '\1' + b 의 접미사 배열 + Kasai
    std::string s = a + '\1' + b; int n = (int)s.size(), na = (int)a.size(); std::vector<int> sa(n), rk(n), tmp(n); std::iota(sa.begin(), sa.end(), 0); for (int i = 0; i < n; ++i) rk[i] = (unsigned char)s[i]; if (n < 2) return 0;
    for (int k = 1;; k <<= 1) { auto cmp = [&](int x, int y) { if (rk[x] != rk[y]) return rk[x] < rk[y]; int rx = x + k < n ? rk[x + k] : -1, ry = y + k < n ? rk[y + k] : -1; return rx < ry; }; std::sort(sa.begin(), sa.end(), cmp); tmp[sa[0]] = 0; for (int i = 1; i < n; ++i) tmp[sa[i]] = tmp[sa[i - 1]] + cmp(sa[i - 1], sa[i]); rk = tmp; if (rk[sa[n - 1]] == n - 1) break; }
    std::vector<int> rank(n); for (int i = 0; i < n; ++i) rank[sa[i]] = i; size_t best = 0;
    for (int i = 0, h = 0; i < n; ++i) { if (rank[i] == 0) { h = 0; continue; } int j = sa[rank[i] - 1]; while (i + h < n && j + h < n && s[i + h] == s[j + h]) ++h; bool differentSides = (i < na) != (j < na) && i != na && j != na; if (differentSides) best = std::max<size_t>(best, (size_t)h); if (h > 0) --h; }
    return best;
}

int main() {
    assert(lcsubstringDP("abcdxyz", "xyzabcd") == "abcd" && lcsubstringDP("OldSite:GeeksforGeeks.org", "NewSite:GeeksQuiz.com") == "Site:Geeks" && lcsubstringDP("abc", "xyz").empty());
    std::mt19937 rng(64);
    for (int it = 0; it < 30000; ++it) {
        std::string a(rng() % 20, 'a'), b(rng() % 20, 'a'); int sigma = 1 + (int)(rng() % 4); for (char& c : a) c = (char)('a' + rng() % sigma); for (char& c : b) c = (char)('a' + rng() % sigma);
        g_cells = 0; std::string got = lcsubstringDP(a, b); size_t want = bruteLcsubstring(a, b).size(); assert(got.size() == want && g_cells == (long)(a.size() * b.size()) && (got.empty() || (a.find(got) != std::string::npos && b.find(got) != std::string::npos)));
        assert(lcsubstringBySuffixArray(a, b) == want);
    }
    for (int it = 0; it < 30; ++it) { size_t n = 500 + rng() % 2500; std::string a(n, 'a'), b(n / 2 + rng() % n, 'a'); for (char& c : a) c = (char)('a' + rng() % 4); for (char& c : b) c = (char)('a' + rng() % 4); if (it % 3 == 0) { std::string common = a.substr(n / 3, 60); b.replace(b.size() / 2, 60, common); }
        std::string got = lcsubstringDP(a, b); assert(got.size() == lcsubstringBySuffixArray(a, b) && a.find(got) != std::string::npos && b.find(got) != std::string::npos); }
    { std::string a(3000, 'a'); for (char& c : a) c = (char)('a' + rng() % 26); g_cells = 0; assert(lcsubstringDP(a, a) == a && g_cells == 3000L * 3000); std::cout << "LongestCommonSubstringDP: DP = brute force = suffix-array/LCP method on 30000 + 30 random cases, exactly n*m = " << g_cells << " cell updates" << std::endl; }
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(m)
```
## LongestCommonSubsequence()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 최장 공통 부분 수열(LCS): 연속이 아니어도 순서만 유지하면 된다. diff, 유전자 정렬의 기초.  dp[i][j] = 접두사 a[0..i), b[0..j) 의 LCS 길이.
//  ① 표 DP + 역추적  ② Hirschberg 분할 정복(공간 O(n + m)) — 결과는 항상 두 문자열의 부분 수열이고 길이가 표 DP 와 같다  ③ 비트 병렬(한쪽이 64 글자 이하): 텍스트 글자당 O(1) 워드 연산
//  ④ 서로 다른 LCS 문자열 전체를 DP 로 모아 부분 수열을 모두 나열하는 무차별과 대조  ⑤ diff: 삽입·삭제만 허용한 편집 거리 = n + m − 2·LCS, 연산열을 적용하면 b 가 된다.
std::vector<std::vector<int>> table(const std::string& a, const std::string& b) { std::vector<std::vector<int>> d(a.size() + 1, std::vector<int>(b.size() + 1, 0)); for (size_t i = 1; i <= a.size(); ++i) for (size_t j = 1; j <= b.size(); ++j) d[i][j] = a[i - 1] == b[j - 1] ? d[i - 1][j - 1] + 1 : std::max(d[i - 1][j], d[i][j - 1]); return d; }
std::string lcs(const std::string& a, const std::string& b) {
    auto d = table(a, b); std::string out; for (size_t i = a.size(), j = b.size(); i > 0 && j > 0;) { if (a[i - 1] == b[j - 1]) { out += a[i - 1]; --i; --j; } else if (d[i - 1][j] >= d[i][j - 1]) --i; else --j; }
    std::reverse(out.begin(), out.end()); return out;
}
std::vector<int> lastRow(const std::string& a, const std::string& b) { std::vector<int> prev(b.size() + 1, 0), cur(b.size() + 1, 0); for (size_t i = 1; i <= a.size(); ++i) { for (size_t j = 1; j <= b.size(); ++j) cur[j] = a[i - 1] == b[j - 1] ? prev[j - 1] + 1 : std::max(prev[j], cur[j - 1]); std::swap(prev, cur); } return prev; }
std::string hirschberg(const std::string& a, const std::string& b) {
    if (a.empty() || b.empty()) return ""; if (a.size() == 1) return b.find(a[0]) != std::string::npos ? a : "";
    size_t mid = a.size() / 2; std::string a1 = a.substr(0, mid), a2 = a.substr(mid); std::vector<int> l1 = lastRow(a1, b); std::string ra2(a2.rbegin(), a2.rend()), rb(b.rbegin(), b.rend()); std::vector<int> l2 = lastRow(ra2, rb);
    size_t bestK = 0; int best = -1; for (size_t k = 0; k <= b.size(); ++k) if (l1[k] + l2[b.size() - k] > best) { best = l1[k] + l2[b.size() - k]; bestK = k; }
    return hirschberg(a1, b.substr(0, bestK)) + hirschberg(a2, b.substr(bestK));
}
int lcsBits(const std::string& p, const std::string& t) {                                              // |p| ≤ 64
    size_t m = p.size(); assert(m >= 1 && m <= 64); std::uint64_t peq[256] = {0}; for (size_t i = 0; i < m; ++i) peq[(unsigned char)p[i]] |= 1ULL << i; const std::uint64_t mask = m == 64 ? ~0ULL : (1ULL << m) - 1; std::uint64_t v = mask;
    for (unsigned char c : t) { std::uint64_t u = v & peq[c]; v = ((v + u) | (v & ~peq[c])) & mask; }
    return (int)m - __builtin_popcountll(v);                                                            // v 의 0 비트 수 = LCS 길이
}
bool isSubsequence(const std::string& s, const std::string& t) { size_t k = 0; for (char c : t) if (k < s.size() && s[k] == c) ++k; return k == s.size(); }
std::set<std::string> allLcs(const std::string& a, const std::string& b, const std::vector<std::vector<int>>& d, size_t i, size_t j) {          // 서로 다른 모든 LCS
    if (i == 0 || j == 0) return {""}; std::set<std::string> r;
    if (a[i - 1] == b[j - 1]) { for (auto& s : allLcs(a, b, d, i - 1, j - 1)) r.insert(s + a[i - 1]); return r; }
    if (d[i - 1][j] >= d[i][j - 1]) { for (auto& s : allLcs(a, b, d, i - 1, j)) r.insert(s); }
    if (d[i][j - 1] >= d[i - 1][j]) { for (auto& s : allLcs(a, b, d, i, j - 1)) r.insert(s); }
    return r;
}
std::set<std::string> bruteAllLcs(const std::string& a, const std::string& b) { std::set<std::string> best; size_t bl = 0; for (unsigned m = 0; m < (1u << a.size()); ++m) { std::string s; for (size_t i = 0; i < a.size(); ++i) if (m >> i & 1) s += a[i]; if (s.size() >= bl && isSubsequence(s, b)) { if (s.size() > bl) { best.clear(); bl = s.size(); } best.insert(s); } } return best; }
std::string diffScript(const std::string& a, const std::string& b) {                                    // '=' 유지, '-' a 의 글자 삭제, '+' b 의 글자 삽입
    auto d = table(a, b); std::string s; size_t i = a.size(), j = b.size(); while (i > 0 || j > 0) { if (i && j && a[i - 1] == b[j - 1]) { s += '='; --i; --j; } else if (j && (!i || d[i][j - 1] >= d[i - 1][j])) { s += '+'; --j; } else { s += '-'; --i; } } std::reverse(s.begin(), s.end()); return s; }

int main() {
    std::string r = lcs("ABCBDAB", "BDCABA"); assert(r.size() == 4 && isSubsequence(r, "ABCBDAB") && isSubsequence(r, "BDCABA") && lcs("AGGTAB", "GXTXAYB") == "GTAB" && lcs("abc", "xyz").empty());
    std::mt19937 rng(8);
    for (int it = 0; it < 30000; ++it) {
        std::string a(rng() % 9, 'a'), b(rng() % 9, 'a'); int sigma = 1 + (int)(rng() % 3); for (char& c : a) c = (char)('a' + rng() % sigma); for (char& c : b) c = (char)('a' + rng() % sigma); auto d = table(a, b);
        std::string x = lcs(a, b), h = hirschberg(a, b); assert((int)x.size() == d[a.size()][b.size()] && isSubsequence(x, a) && isSubsequence(x, b) && h.size() == x.size() && isSubsequence(h, a) && isSubsequence(h, b));     // ① ②
        assert(allLcs(a, b, d, a.size(), b.size()) == bruteAllLcs(a, b));                                                                                                                                                   // ④ 서로 다른 LCS 전체
        if (!a.empty()) assert(lcsBits(a, b) == d[a.size()][b.size()]);                                                                                                                                                    // ③
        std::string sc = diffScript(a, b); std::string applied; size_t i = 0, j = 0; long ins = 0, del = 0; for (char op : sc) { if (op == '=') { applied += a[i++]; ++j; } else if (op == '-') { ++i; ++del; } else { applied += b[j++]; ++ins; } }
        assert(i == a.size() && j == b.size() && applied == b && ins + del == (long)(a.size() + b.size()) - 2 * d[a.size()][b.size()]);                                                                                         // ⑤
    }
    for (int it = 0; it < 2000; ++it) { std::string p(1 + rng() % 64, 'a'), t(rng() % 300, 'a'); for (char& c : p) c = (char)('a' + rng() % 4); for (char& c : t) c = (char)('a' + rng() % 4); assert(lcsBits(p, t) == table(p, t)[p.size()][t.size()]); }
    { std::string a(3000, 'a'), b(3000, 'a'); for (char& c : a) c = (char)('a' + rng() % 4); for (char& c : b) c = (char)('a' + rng() % 4); std::string h = hirschberg(a, b); assert(lastRow(a, b).back() == (int)h.size() && isSubsequence(h, a) && isSubsequence(h, b) && lcs(a, b).size() == h.size());
      std::cout << "LCS: table DP, Hirschberg (linear space), bit-parallel, all-LCS enumeration and diff scripts agree; two random 3000-letter strings share a subsequence of length " << h.size() << std::endl; }
    return 0;
}
// Time Complexity: O(n·m) (Hirschberg 도 O(n·m)), 비트 병렬 O(n·⌈m/64⌉)
// Space Complexity: 표 O(n·m), Hirschberg·거리만 O(n + m)
```
# Part 13. 정규식과 오토마톤
## FiniteAutomaton()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 문자열 매칭 오토마톤: 패턴의 각 접두사 길이를 상태로 하는 DFA 를 미리 만들면 텍스트를 한 번 훑는 것만으로 매칭이 끝난다.
// 텍스트 글자마다 O(1) 전이 (KMP 의 실패 함수를 완전한 전이표로 펼친 것)
struct Matcher {
    std::vector<std::vector<int>> delta; int m;
    explicit Matcher(const std::string& p) : delta(p.size() + 1, std::vector<int>(256, 0)), m(p.size()) {
        delta[0][(unsigned char)p[0]] = 1;
        for (int state = 1, x = 0; state <= m; state++) {             // x = 상태 state 의 "실패 상태"
            for (int c = 0; c < 256; c++) delta[state][c] = delta[x][c];
            if (state < m) { delta[state][(unsigned char)p[state]] = state + 1; x = delta[x][(unsigned char)p[state]]; }
        }
    }
    std::vector<size_t> search(const std::string& t) const {
        std::vector<size_t> res; int s = 0;
        for (size_t i = 0; i < t.size(); i++) { s = delta[s][(unsigned char)t[i]]; if (s == m) res.push_back(i + 1 - m); }
        return res;
    }
};

int main() {
    Matcher a("abab");
    assert((a.search("ababababc") == std::vector<size_t>{0, 2, 4}));
    assert(Matcher("x").search("abc").empty());
    std::mt19937 rng(6);
    for (int it = 0; it < 1000; it++) {
        std::string t, p; int n = rng() % 40 + 1, m = rng() % 5 + 1;
        for (int i = 0; i < n; i++) t += "ab"[rng() % 2]; for (int i = 0; i < m; i++) p += "ab"[rng() % 2];
        std::vector<size_t> expect; for (size_t i = 0; i + p.size() <= t.size(); i++) if (t.compare(i, p.size(), p) == 0) expect.push_back(i);
        assert(Matcher(p).search(t) == expect);
    }
    std::cout << "FiniteAutomaton matches naive on 1000 random cases." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(m·σ), 검색 O(n)
// Space Complexity: O(m·σ)
```
## RegexNFA()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 톰프슨 구성: 정규식 -> 후위 표기 -> NFA.  연산자: | (선택)  * + ? (반복)  . (임의 한 글자)  ( ) (묶기)  연결은 암묵적
// 시뮬레이션은 "현재 상태 집합"을 글자마다 갱신하므로 백트래킹과 달리 항상 O(n·m) (지수 폭발 없음)
const int SPLIT = 256, MATCH = 257, ANY = 258;
struct State { int c; int out = -1, out1 = -1; };
struct Patch { int s; int which; };
struct Frag { int start; std::vector<Patch> outs; };

std::string toPostfix(const std::string& re) {
    std::string out; std::stack<char> ops;
    auto prec = [](char c) { return c == '|' ? 1 : c == '\x01' ? 2 : 3; };
    std::string expl;                                           // 암묵적 연결을 \x01 로 명시
    for (size_t i = 0; i < re.size(); i++) {
        expl += re[i];
        if (i + 1 < re.size()) {
            char a = re[i], b = re[i + 1];
            bool left = a != '(' && a != '|', right = b != ')' && b != '|' && b != '*' && b != '+' && b != '?';
            if (left && right) expl += '\x01';
        }
    }
    for (char c : expl) {
        if (c == '(') ops.push(c);
        else if (c == ')') { while (ops.top() != '(') { out += ops.top(); ops.pop(); } ops.pop(); }
        else if (c == '|' || c == '\x01' || c == '*' || c == '+' || c == '?') {
            while (!ops.empty() && ops.top() != '(' && prec(ops.top()) >= prec(c) && c != '*' && c != '+' && c != '?') { out += ops.top(); ops.pop(); }
            if (c == '*' || c == '+' || c == '?') out += c; else ops.push(c);
        } else out += c;
    }
    while (!ops.empty()) { out += ops.top(); ops.pop(); }
    return out;
}

struct NFA {
    std::vector<State> st; int start;
    void patch(const std::vector<Patch>& l, int target) { for (auto& p : l) (p.which ? st[p.s].out1 : st[p.s].out) = target; }
    int add(int c) { st.push_back({c}); return st.size() - 1; }
    explicit NFA(const std::string& re) {
        std::string post = toPostfix(re); std::stack<Frag> f;
        for (char ch : post) {
            if (ch == '\x01') { Frag b = f.top(); f.pop(); Frag a = f.top(); f.pop(); patch(a.outs, b.start); f.push({a.start, b.outs}); }
            else if (ch == '|') { Frag b = f.top(); f.pop(); Frag a = f.top(); f.pop(); int s = add(SPLIT); st[s].out = a.start; st[s].out1 = b.start;
                                  auto o = a.outs; o.insert(o.end(), b.outs.begin(), b.outs.end()); f.push({s, o}); }
            else if (ch == '?') { Frag a = f.top(); f.pop(); int s = add(SPLIT); st[s].out = a.start; auto o = a.outs; o.push_back({s, 1}); f.push({s, o}); }
            else if (ch == '*') { Frag a = f.top(); f.pop(); int s = add(SPLIT); st[s].out = a.start; patch(a.outs, s); f.push({s, {{s, 1}}}); }
            else if (ch == '+') { Frag a = f.top(); f.pop(); int s = add(SPLIT); st[s].out = a.start; patch(a.outs, s); f.push({a.start, {{s, 1}}}); }
            else { int s = add(ch == '.' ? ANY : (unsigned char)ch); f.push({s, {{s, 0}}}); }
        }
        Frag e = f.top(); int m = add(MATCH); patch(e.outs, m); start = e.start;
    }
    void addState(std::set<int>& S, int s) const {
        if (s < 0 || S.count(s)) return;
        S.insert(s);
        if (st[s].c == SPLIT) { addState(S, st[s].out); addState(S, st[s].out1); }
    }
    bool matches(const std::string& text) const {
        std::set<int> cur; addState(cur, start);
        for (unsigned char ch : text) {
            std::set<int> next;
            for (int s : cur) if (st[s].c == ch || st[s].c == ANY) addState(next, st[s].out);
            cur.swap(next);
        }
        for (int s : cur) if (st[s].c == MATCH) return true;
        return false;
    }
};

int main() {
    assert(NFA("a(b|c)*d").matches("abcbcd") && NFA("a(b|c)*d").matches("ad") && !NFA("a(b|c)*d").matches("abxd"));
    assert(NFA("colou?r").matches("color") && NFA("colou?r").matches("colour") && !NFA("colou?r").matches("colouur"));
    assert(NFA("(ab)+").matches("ababab") && !NFA("(ab)+").matches("") && !NFA("(ab)+").matches("aba"));
    assert(NFA("a.c").matches("abc") && !NFA("a.c").matches("ac"));
    assert(NFA("a*").matches("") && NFA("(a|b)*abb").matches("babaabb"));
    // 백트래킹 엔진이 지수 시간이 걸리는 (a*)*b 류의 입력도 선형 시간에 끝난다
    assert(!NFA("(a*)*b").matches(std::string(2000, 'a')));
    std::cout << "RegexNFA verified." << std::endl;
    return 0;
}
// Time Complexity: 매칭 O(n·m) (n = 텍스트, m = 정규식 크기)
// Space Complexity: O(m)
```
# Part 14. 컴파일러
## Lexer()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cctype>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 어휘 분석기(lexer): 문자 스트림을 토큰(숫자, 식별자, 키워드, 문자열, 연산자)으로 자른다. 컴파일러의 첫 단계이며 토큰은 정규식(오토마톤)으로 정의된다. 규칙: *최장 일치*(maximal munch).
//  숫자: 12, 3.14, .5, 5., 1e-3, 2.5E+7 ("1e" 는 숫자 1 과 식별자 e, "1.2.3" 은 1.2 와 .3).  연산자: <<= >>= ... -> ++ -- << >> <= >= == != && || += -= *= /= %= &= |= ^= 과 한 글자 연산자·구분자.  주석: // …, /* … */.
//  검증: ① 알려진 입력의 토큰열  ② 최장 일치 표  ③ 무작위 토큰열을 구분자(공백·줄바꿈·주석)로 이어 붙인 뒤 다시 자르면 원래 토큰열  ④ 각 토큰의 (줄, 열, 위치)를 접두사에서 독립적으로 계산한 값과 비교
//  ⑤ 오류의 종류와 위치  ⑥ 무작위 바이트 퍼징: 종료하고, 토큰 구간들이 정렬되어 겹치지 않으며 구간 사이는 공백·주석뿐  ⑦ 2 MB 이상의 입력이 선형 시간.
enum Kind { NUMBER, IDENT, KEYWORD, STRING, CHAR, OP };
struct Token { Kind kind; std::string text; size_t pos, end; int line, col; };
struct LexError { std::string msg; size_t pos; int line, col; };
const std::set<std::string> KEYWORDS = {"if", "else", "while", "for", "return", "int", "float", "void"};
const char* OPS3[] = {"<<=", ">>=", "..."}; const char* OPS2[] = {"->", "++", "--", "<<", ">>", "<=", ">=", "==", "!=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="};
bool isIdentStart(unsigned char c) { return std::isalpha(c) || c == '_'; } bool isIdentChar(unsigned char c) { return std::isalnum(c) || c == '_'; }
struct Lexer {
    const std::string& s; size_t i = 0; int line = 1, col = 1; LexError* err; std::vector<Token> out;
    Lexer(const std::string& src, LexError* e) : s(src), err(e) {}
    void advance(size_t n) { for (size_t k = 0; k < n; ++k) { if (s[i] == '\n') { ++line; col = 1; } else ++col; ++i; } }
    bool fail(const std::string& m, size_t pos, int l, int c) { if (err) *err = {m, pos, l, c}; return false; }
    bool run() {
        while (i < s.size()) {
            unsigned char c = s[i];
            if (std::isspace(c)) { advance(1); continue; }
            if (c == '/' && i + 1 < s.size() && s[i + 1] == '/') { while (i < s.size() && s[i] != '\n') advance(1); continue; }
            if (c == '/' && i + 1 < s.size() && s[i + 1] == '*') { size_t p = i; int l = line, cc = col; advance(2); while (i + 1 < s.size() && !(s[i] == '*' && s[i + 1] == '/')) advance(1); if (i + 1 >= s.size()) return fail("unterminated comment", p, l, cc); advance(2); continue; }
            size_t start = i; int l = line, cc = col; Kind kind;
            if (std::isdigit(c) || (c == '.' && i + 1 < s.size() && std::isdigit((unsigned char)s[i + 1]))) {                    // 숫자: 정수부 [. 소수부] [e[±]지수]  — 지수는 숫자가 뒤따를 때만
                size_t j = i; while (j < s.size() && std::isdigit((unsigned char)s[j])) ++j; if (j < s.size() && s[j] == '.') { ++j; while (j < s.size() && std::isdigit((unsigned char)s[j])) ++j; }
                if (j < s.size() && (s[j] == 'e' || s[j] == 'E')) { size_t k = j + 1; if (k < s.size() && (s[k] == '+' || s[k] == '-')) ++k; if (k < s.size() && std::isdigit((unsigned char)s[k])) { while (k < s.size() && std::isdigit((unsigned char)s[k])) ++k; j = k; } }
                advance(j - i); kind = NUMBER;
            } else if (isIdentStart(c)) { size_t j = i; while (j < s.size() && isIdentChar((unsigned char)s[j])) ++j; advance(j - i); kind = KEYWORDS.count(s.substr(start, i - start)) ? KEYWORD : IDENT; }
            else if (c == '"' || c == '\'') { char q = (char)c; advance(1); while (i < s.size() && s[i] != q && s[i] != '\n') { if (s[i] == '\\' && i + 1 < s.size() && s[i + 1] != '\n') advance(2); else advance(1); } if (i >= s.size() || s[i] != q) return fail("unterminated string", start, l, cc); advance(1); kind = q == '"' ? STRING : CHAR; }
            else {
                size_t n = 0; for (const char* o : OPS3) if (s.compare(i, 3, o) == 0) n = 3; if (!n) for (const char* o : OPS2) if (s.compare(i, 2, o) == 0) n = 2;
                if (!n && std::string("+-*/%=<>!&|^~?:;,.(){}[]").find((char)c) != std::string::npos) n = 1; if (!n) return fail(std::string("unexpected character '") + (char)c + "'", i, line, col);
                advance(n); kind = OP;
            }
            out.push_back({kind, s.substr(start, i - start), start, i, l, cc});
        }
        return true;
    }
};
std::vector<Token> lex(const std::string& s, LexError* err = nullptr) { Lexer lx(s, err); lx.run(); return lx.out; }
bool skippable(const std::string& g) { size_t i = 0; while (i < g.size()) { if (std::isspace((unsigned char)g[i])) ++i; else if (g.compare(i, 2, "//") == 0) { while (i < g.size() && g[i] != '\n') ++i; } else if (g.compare(i, 2, "/*") == 0) { size_t e = g.find("*/", i + 2); if (e == std::string::npos) return false; i = e + 2; } else return false; } return true; }       // 독립 검사: 공백과 주석뿐인가
std::string randomToken(std::mt19937& rng, Kind& kind) {
    static const char* ops[] = {"<<=", ">>=", "...", "->", "++", "--", "<<", ">>", "<=", ">=", "==", "!=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "+", "-", "*", "/", "%", "=", "<", ">", "!", "&", "|", "^", "~", "?", ":", ";", ",", ".", "(", ")", "{", "}", "[", "]"};
    static const char* kws[] = {"if", "else", "while", "for", "return", "int", "float", "void"};
    switch (rng() % 5) {
        case 0: { kind = NUMBER; std::string t; int form = (int)(rng() % 5); auto digits = [&](int n) { std::string d; for (int i = 0; i < n; ++i) d += (char)('0' + rng() % 10); return d; };
                  if (form == 0) t = digits(1 + (int)(rng() % 4)); else if (form == 1) t = digits(1 + (int)(rng() % 3)) + "." + digits(1 + (int)(rng() % 3)); else if (form == 2) t = "." + digits(1 + (int)(rng() % 3)); else if (form == 3) t = digits(1) + "e" + (rng() % 2 ? "-" : "+") + digits(1 + (int)(rng() % 2)); else t = digits(1 + (int)(rng() % 3)) + ".";
                  return t; }
        case 1: { kind = IDENT; std::string t(1, "abcxyz_"[rng() % 7]); for (int n = (int)(rng() % 5); n > 0; --n) t += "ab9_Z"[rng() % 5]; if (KEYWORDS.count(t)) t += "_"; return t; }
        case 2: kind = KEYWORD; return kws[rng() % 8];
        case 3: { kind = rng() % 2 ? STRING : CHAR; char q = kind == STRING ? '"' : '\''; std::string t(1, q); for (int n = (int)(rng() % 5); n > 0; --n) { if (rng() % 4 == 0) { t += '\\'; t += rng() % 2 ? q : 'n'; } else t += "ab c+/"[rng() % 6]; } t += q; return t; }
        default: kind = OP; return ops[rng() % (sizeof(ops) / sizeof(ops[0]))];
    }
}

int main() {
    { auto t = lex("x1 = 3.14 * (y_2 + 2)"); std::vector<std::string> tx; for (auto& k : t) tx.push_back(k.text); assert((tx == std::vector<std::string>{"x1", "=", "3.14", "*", "(", "y_2", "+", "2", ")"}) && t[0].kind == IDENT && t[2].kind == NUMBER && t[3].kind == OP && lex("if x").front().kind == KEYWORD); }
    // ② 최장 일치와 숫자 문법
    struct Case { const char* src; std::vector<std::string> toks; } cases[] = {{"<<=", {"<<="}}, {"<<<", {"<<", "<"}}, {"->>", {"->", ">"}}, {"....", {"...", "."}}, {"a+++b", {"a", "++", "+", "b"}}, {"x<=y", {"x", "<=", "y"}}, {"a>>=b", {"a", ">>=", "b"}},
        {"1e", {"1", "e"}}, {"1e+", {"1", "e", "+"}}, {"1e+5", {"1e+5"}}, {"1.2.3", {"1.2", ".3"}}, {"1..2", {"1.", ".2"}}, {"5.", {"5."}}, {".5", {".5"}}, {"0x1F", {"0", "x1F"}}, {"a//c\nb", {"a", "b"}}, {"a/*c*/b", {"a", "b"}}, {"\"a\\\"b\"", {"\"a\\\"b\""}}, {"'x'", {"'x'"}}};
    for (auto& c : cases) { auto t = lex(c.src); std::vector<std::string> tx; for (auto& k : t) tx.push_back(k.text); assert(tx == c.toks); }
    std::mt19937 rng(77);
    // ③ 토큰열 → 구분자로 이어 붙이기 → 다시 자르기
    for (int it = 0; it < 20000; ++it) {
        std::vector<std::string> toks; std::vector<Kind> kinds; std::string src; int n = (int)(rng() % 12);
        for (int k = 0; k < n; ++k) { Kind kd; std::string t = randomToken(rng, kd); toks.push_back(t); kinds.push_back(kd); static const char* seps[] = {" ", "\n", "  /*c*/ ", " //c\n", "\t", " /* a * / b */ "}; src += seps[rng() % 6]; src += t; }
        src += (rng() % 2 ? "\n" : " "); LexError e; auto got = lex(src, &e); bool ok = got.size() == toks.size(); for (size_t k = 0; ok && k < toks.size(); ++k) ok = got[k].text == toks[k] && got[k].kind == kinds[k]; assert(ok);
        // ④ 위치: 각 토큰의 시작 위치·줄·열을 접두사에서 직접 센 값과 비교
        for (auto& tk : got) { int line = 1, col = 1; for (size_t p = 0; p < tk.pos; ++p) { if (src[p] == '\n') { ++line; col = 1; } else ++col; } assert(src.compare(tk.pos, tk.text.size(), tk.text) == 0 && tk.end == tk.pos + tk.text.size() && tk.line == line && tk.col == col); }
    }
    // ⑤ 오류의 종류·위치
    { LexError e; lex("a $ b", &e); assert(e.pos == 2 && e.line == 1 && e.col == 3 && e.msg.find("unexpected") == 0);
      lex("x = 1;\ny = \"abc\nz", &e); assert(e.msg == "unterminated string" && e.line == 2 && e.col == 5);
      lex("a\n  /* never closed", &e); assert(e.msg == "unterminated comment" && e.line == 2 && e.col == 3 && e.pos == 4);
      lex("ok 'q", &e); assert(e.msg == "unterminated string" && e.col == 4); }
    // ⑥ 무작위 바이트 퍼징: 종료하고, 토큰 구간은 정렬·비중첩, 사이는 공백·주석뿐
    long errors = 0, clean = 0; const char alphabet[] = "ab1.eE+-*/<>=!&|^ \n\t\"'\\(){};_$#@0x/*";
    for (int it = 0; it < 100000; ++it) { std::string s(rng() % 30, 'a'); for (char& c : s) c = alphabet[rng() % (sizeof(alphabet) - 1)]; LexError e; e.pos = 0; auto toks = lex(s, &e); size_t prev = 0; bool ok = true; for (auto& tk : toks) { ok = ok && tk.pos >= prev && tk.end > tk.pos && skippable(s.substr(prev, tk.pos - prev)); prev = tk.end; } assert(ok);
        bool rest = prev == s.size() || skippable(s.substr(prev)); assert(e.msg.empty() == rest && (e.msg.empty() || e.pos >= prev)); if (rest) ++clean; else ++errors; }                 // 오류 없음 ↔ 남은 부분이 공백·주석뿐
    assert(clean > 1000 && errors > 1000);
    // ⑦ 5 MB 입력
    { std::string snippet = "int x1 = 3.14e-2 * (y_2 + .5) >>= 2; // c\nif (a<=b) { return \"s\\\"t\"; } /* k */\n", big; const size_t reps = 30000; big.reserve(snippet.size() * reps); for (size_t r = 0; r < reps; ++r) big += snippet; size_t per = lex(snippet).size(); LexError e; auto t = lex(big, &e); assert(t.size() == per * reps && big.size() > 2000000);
      std::cout << "Lexer: round trip of 20000 random token streams, positions, errors and 10^5 fuzz inputs verified (" << clean << " lexed cleanly, " << errors << " stopped at an error); a " << big.size() << "-byte source produced " << t.size() << " tokens" << std::endl; }
    return 0;
}
// Time Complexity: O(n) (문자마다 상수 번 앞을 본다)
// Space Complexity: O(토큰 수)
```
## RecursiveDescentParser()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cctype>
#include <map>
#include <stdexcept>
#include <string>
#include <cassert>

// 재귀 하강 파서: 문법 규칙 하나가 함수 하나.  연산자 우선순위는 문법의 계층(expr > term > factor)으로 표현된다
//   expr   := term   (('+' | '-') term)*
//   term   := factor (('*' | '/') factor)*
//   factor := NUMBER | IDENT | '(' expr ')' | '-' factor
class Parser {
    std::string s; size_t i = 0; const std::map<std::string, double>& vars;
    void ws() { while (i < s.size() && std::isspace((unsigned char)s[i])) i++; }
    bool eat(char c) { ws(); if (i < s.size() && s[i] == c) { i++; return true; } return false; }
    double factor() {
        ws();
        if (eat('-')) return -factor();
        if (eat('(')) { double v = expr(); if (!eat(')')) throw std::runtime_error("expected )"); return v; }
        size_t j = i;
        if (j < s.size() && std::isdigit((unsigned char)s[j])) { while (j < s.size() && (std::isdigit((unsigned char)s[j]) || s[j] == '.')) j++; double v = std::stod(s.substr(i, j - i)); i = j; return v; }
        if (j < s.size() && std::isalpha((unsigned char)s[j])) { while (j < s.size() && std::isalnum((unsigned char)s[j])) j++; std::string name = s.substr(i, j - i); i = j; auto it = vars.find(name); if (it == vars.end()) throw std::runtime_error("unknown variable " + name); return it->second; }
        throw std::runtime_error("unexpected input");
    }
    double term() { double v = factor(); for (;;) { if (eat('*')) v *= factor(); else if (eat('/')) { double d = factor(); if (d == 0) throw std::runtime_error("division by zero"); v /= d; } else return v; } }
    double expr() { double v = term(); for (;;) { if (eat('+')) v += term(); else if (eat('-')) v -= term(); else return v; } }
public:
    Parser(const std::string& src, const std::map<std::string, double>& v) : s(src), vars(v) {}
    double parse() { double v = expr(); ws(); if (i != s.size()) throw std::runtime_error("trailing input"); return v; }
};
double eval(const std::string& src, const std::map<std::string, double>& v = {}) { return Parser(src, v).parse(); }

int main() {
    assert(eval("2 + 3 * 4") == 14);                             // 곱셈이 먼저
    assert(eval("(2 + 3) * 4") == 20);
    assert(eval("-(2 + 3)") == -5 && eval("2 * -3") == -6);
    assert(eval("10 / 4") == 2.5 && eval("2*3+4*5") == 26 && eval("8 - 3 - 2") == 3);   // 뺄셈은 왼쪽 결합
    assert(std::fabs(eval("x * (y + 1)", {{"x", 2.5}, {"y", 3}}) - 10) < 1e-12);
    bool threw = false; try { eval("1 / 0"); } catch (const std::runtime_error&) { threw = true; } assert(threw);
    threw = false; try { eval("(1 + 2"); } catch (const std::runtime_error&) { threw = true; } assert(threw);
    std::cout << "RecursiveDescentParser: 2 + 3 * 4 = " << eval("2 + 3 * 4") << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(중첩 깊이)
```
# Part 15. 검색엔진
## InvertedIndex()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cctype>
#include <map>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// 역색인(inverted index): 단어 -> 그 단어가 나오는 문서 번호 목록(포스팅 리스트, 정렬됨).  검색엔진의 핵심 자료구조
// AND 질의 = 정렬된 두 리스트의 교집합(병합식 O(a+b)),  OR = 합집합
class Index {
    std::map<std::string, std::vector<int>> post;
    static std::vector<std::string> tokenize(const std::string& s) {
        std::vector<std::string> out; std::string w;
        for (unsigned char c : s) { if (std::isalnum(c)) w += std::tolower(c); else if (!w.empty()) { out.push_back(w); w.clear(); } }
        if (!w.empty()) out.push_back(w);
        return out;
    }
public:
    void add(int doc, const std::string& text) { for (auto& w : tokenize(text)) { auto& v = post[w]; if (v.empty() || v.back() != doc) v.push_back(doc); } }
    const std::vector<int>& postings(const std::string& w) const { static const std::vector<int> none; auto it = post.find(w); return it == post.end() ? none : it->second; }
    std::vector<int> andQuery(const std::string& a, const std::string& b) const {
        const auto &x = postings(a), &y = postings(b); std::vector<int> r;
        for (size_t i = 0, j = 0; i < x.size() && j < y.size();) { if (x[i] == y[j]) { r.push_back(x[i]); i++; j++; } else if (x[i] < y[j]) i++; else j++; }
        return r;
    }
    std::vector<int> orQuery(const std::string& a, const std::string& b) const {
        std::vector<int> r; const auto &x = postings(a), &y = postings(b);
        std::set_union(x.begin(), x.end(), y.begin(), y.end(), std::back_inserter(r)); return r;
    }
};

int main() {
    Index ix;
    ix.add(1, "The quick brown fox");
    ix.add(2, "The lazy dog sleeps");
    ix.add(3, "A quick brown dog barks");
    ix.add(4, "Foxes and dogs are animals");
    assert((ix.postings("the") == std::vector<int>{1, 2}));
    assert((ix.andQuery("quick", "dog") == std::vector<int>{3}));
    assert((ix.orQuery("fox", "dog") == std::vector<int>{1, 2, 3}));
    assert(ix.postings("zebra").empty());
    std::cout << "InvertedIndex verified." << std::endl;
    return 0;
}
// Time Complexity: 색인 O(총 토큰 수 log V), AND 질의 O(|a| + |b|)
// Space Complexity: O(총 토큰 수)
```
## NGramIndex()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// n-gram 색인(여기서는 bigram): 단어를 글자 n 개 조각으로 나눠 색인하면 철자 오류가 있는 질의도 찾는다 (자동 교정, "이것을 찾으셨나요?").
// 질의와 후보의 n-gram 집합의 자카드 유사도 |A∩B| / |A∪B| 가 높은 단어를 고른다
std::set<std::string> grams(const std::string& w, int n = 2) {
    std::string p = "$" + w + "$"; std::set<std::string> g;
    for (size_t i = 0; i + n <= p.size(); i++) g.insert(p.substr(i, n));
    return g;
}
class NGramIndex {
    std::map<std::string, std::vector<std::string>> idx; std::vector<std::string> words;
public:
    void add(const std::string& w) { words.push_back(w); for (auto& g : grams(w)) idx[g].push_back(w); }
    std::vector<std::pair<double, std::string>> search(const std::string& q, double minSim = 0.3) const {
        std::map<std::string, int> common; auto qg = grams(q);
        for (auto& g : qg) { auto it = idx.find(g); if (it != idx.end()) for (auto& w : it->second) common[w]++; }   // 공통 조각 수만 센다
        std::vector<std::pair<double, std::string>> r;
        for (auto& kv : common) {
            double sim = double(kv.second) / (qg.size() + grams(kv.first).size() - kv.second);
            if (sim >= minSim) r.push_back({sim, kv.first});
        }
        std::sort(r.rbegin(), r.rend()); return r;
    }
};

int main() {
    NGramIndex ix;
    for (auto w : {"receive", "relative", "achieve", "deceive", "believe", "banana"}) ix.add(w);
    auto r = ix.search("recieve");                                    // 'ie' <-> 'ei' 오타
    assert(!r.empty() && r[0].second == "receive");
    auto none = ix.search("zzzz");
    assert(none.empty());
    std::cout << "NGramIndex: 'recieve' -> " << r[0].second << " (similarity " << r[0].first << ")" << std::endl;
    return 0;
}
// Time Complexity: 질의 O(|q| · 평균 포스팅 길이)
// Space Complexity: O(총 n-gram 수)
```
## TFIDF()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

// TF-IDF: 문서 안에서 자주 나오고(TF) 전체 문서에서는 드문(IDF) 단어일수록 그 문서를 잘 대표한다.  tf-idf(t, d) = tf(t, d)·log(N / df(t)),  N = 문서 수, df = 단어를 포함한 문서 수.
//  ① 같은 점수를 두 방식으로: 단어 공간의 밀집 벡터로 코사인 유사도를 계산하는 *무차별*과, 단어마다 (문서, tf) 목록을 둔 *역색인*으로 질의 단어의 목록만 훑는 방법 — 점수·순위가 일치해야 한다.
//  ② 성질: 모든 문서에 나오는 단어의 idf = 0, 문서를 같은 내용으로 두 번 이어 붙여도(tf 2 배) 코사인은 불변, 코사인은 [0, 1], 자기 자신과는 1.   ③ BM25: tf 가 커져도 점수는 (k1+1)·idf 로 포화하고 길이 정규화가 있다.
//  ④ 주제별로 단어 분포를 달리한 말뭉치에서 주제 단어 질의의 상위 10 개가 모두 그 주제 문서인지(정밀도).
typedef std::vector<std::string> Doc;
struct Corpus {
    std::vector<std::map<int, int>> tf; std::map<std::string, int> id; std::vector<int> df; std::vector<int> len; int N = 0;
    void add(const Doc& d) { std::map<int, int> t; for (auto& w : d) { auto it = id.find(w); int k; if (it == id.end()) { k = (int)id.size(); id[w] = k; df.push_back(0); } else k = it->second; ++t[k]; } for (auto& kv : t) ++df[kv.first]; tf.push_back(t); len.push_back((int)d.size()); ++N; }
    double idf(int t) const { return std::log((double)N / df[t]); }
    std::map<int, double> vec(int d) const { std::map<int, double> v; for (auto& kv : tf[d]) v[kv.first] = kv.second * idf(kv.first); return v; }
    std::map<int, double> queryVec(const Doc& q) const { std::map<int, double> v; for (auto& w : q) { auto it = id.find(w); if (it != id.end()) v[it->second] += idf(it->second); } return v; }
};
double norm(const std::map<int, double>& v) { double s = 0; for (auto& kv : v) s += kv.second * kv.second; return std::sqrt(s); }
double cosineDense(const Corpus& c, int d, const Doc& q) {                                        // 무차별: 어휘 크기의 밀집 벡터
    size_t V = c.id.size(); std::vector<double> a(V, 0), b(V, 0); for (auto& kv : c.vec(d)) a[kv.first] = kv.second; for (auto& kv : c.queryVec(q)) b[kv.first] = kv.second;
    double dot = 0, na = 0, nb = 0; for (size_t i = 0; i < V; ++i) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; } return na == 0 || nb == 0 ? 0 : dot / std::sqrt(na * nb);
}
struct Index {                                                                                    // 역색인: 단어 → (문서, tf) 목록 + 문서 벡터 노름
    std::vector<std::vector<std::pair<int, int>>> post; std::vector<double> docNorm; const Corpus& c;
    explicit Index(const Corpus& corpus) : post(corpus.id.size()), docNorm(corpus.N), c(corpus) { for (int d = 0; d < c.N; ++d) { for (auto& kv : c.tf[d]) post[kv.first].push_back({d, kv.second}); docNorm[d] = norm(c.vec(d)); } }
    std::vector<double> scores(const Doc& q) const { std::vector<double> acc(c.N, 0); std::map<int, double> qv = c.queryVec(q); double qn = norm(qv); if (qn == 0) return acc; for (auto& kv : qv) for (auto& p : post[kv.first]) acc[p.first] += p.second * c.idf(kv.first) * kv.second; for (int d = 0; d < c.N; ++d) acc[d] = docNorm[d] == 0 ? 0 : acc[d] / (docNorm[d] * qn); return acc; }
};
double bm25(const Corpus& c, int d, const Doc& q, double k1 = 1.2, double b = 0.75) { double avg = 0; for (int l : c.len) avg += l; avg /= c.N; double s = 0; std::set<std::string> seen; for (auto& w : q) { if (!seen.insert(w).second) continue; auto it = c.id.find(w); if (it == c.id.end()) continue; auto f = c.tf[d].find(it->second); if (f == c.tf[d].end()) continue; double tf = f->second, idf = std::log(1 + (c.N - c.df[it->second] + 0.5) / (c.df[it->second] + 0.5)); s += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * c.len[d] / avg)); } return s; }
std::vector<int> topK(const std::vector<double>& s, size_t k) { std::vector<int> o(s.size()); for (size_t i = 0; i < o.size(); ++i) o[i] = (int)i; std::stable_sort(o.begin(), o.end(), [&](int a, int b) { return s[a] > s[b]; }); o.resize(std::min(k, o.size())); return o; }

int main() {
    // 원래 예
    { std::vector<std::string> docs = {"the cat sat on the mat", "the dog sat on the log", "cats and dogs are pets", "the quick brown fox jumps over the lazy dog dog dog"}; Corpus c; for (auto& d : docs) { std::istringstream in(d); Doc w; std::string x; while (in >> x) w.push_back(x); c.add(w); }
      std::vector<double> sc; for (int d = 0; d < c.N; ++d) sc.push_back(cosineDense(c, d, {"dog"})); assert(topK(sc, 1)[0] == 3 && c.idf(c.id["the"]) < c.idf(c.id["fox"]) && cosineDense(c, 2, {"the"}) == 0); }
    std::mt19937 rng(40);
    // ① 무작위 말뭉치(문서 300 개, 어휘 60, 지프 분포): 밀집 코사인 == 역색인, 순위 일치
    { std::vector<double> w(60); for (int i = 0; i < 60; ++i) w[i] = 1.0 / (i + 1); std::discrete_distribution<int> zipf(w.begin(), w.end()); Corpus c; for (int d = 0; d < 300; ++d) { Doc doc; for (int k = 20 + (int)(rng() % 180); k > 0; --k) doc.push_back("w" + std::to_string(zipf(rng))); c.add(doc); }
      Index ix(c); for (int q = 0; q < 100; ++q) { Doc query; for (int k = 1 + (int)(rng() % 4); k > 0; --k) query.push_back("w" + std::to_string(zipf(rng))); std::vector<double> fast = ix.scores(query), slow(c.N); for (int d = 0; d < c.N; ++d) { slow[d] = cosineDense(c, d, query); assert(std::abs(fast[d] - slow[d]) < 1e-9 && slow[d] >= -1e-12 && slow[d] <= 1 + 1e-9); } std::vector<int> a = topK(fast, 10), b = topK(slow, 10); for (size_t i = 0; i < a.size(); ++i) assert(std::abs(fast[a[i]] - slow[b[i]]) < 1e-9); }
      // ② 성질: 모든 문서에 나오는 단어, 자기 자신, 내용 두 번 이어 붙이기
      Corpus all; for (int d = 0; d < 20; ++d) all.add({"common", "w" + std::to_string(d), "w" + std::to_string(d)}); assert(all.idf(all.id["common"]) == 0 && cosineDense(all, 3, {"common"}) == 0);
      Corpus a, b; Doc base = {"x", "y", "y", "z", "q"}, twice = base; twice.insert(twice.end(), base.begin(), base.end()); for (int d = 0; d < 5; ++d) { Doc other = {"x", "k" + std::to_string(d)}; a.add(other); b.add(other); } a.add(base); b.add(twice); assert(std::abs(cosineDense(a, 5, {"x", "y"}) - cosineDense(b, 5, {"x", "y"})) < 1e-12);
      assert(std::abs(cosineDense(a, 5, base) - 1) < 1e-12 && std::abs(cosineDense(b, 5, base) - 1) < 1e-12); }               // 자기 자신(문서 내용 그대로 질의)과의 코사인은 1
    // ③ BM25: tf 포화와 길이 정규화
    { Corpus c; for (int d = 0; d < 50; ++d) c.add({"filler", "pad" + std::to_string(d)}); Doc rare(1, "needle"); double prev = -1, bound = 0; for (int tf : {1, 2, 5, 20, 100, 100000}) { Doc doc(tf, "needle"); Corpus c2 = c; c2.add(doc); double s = bm25(c2, 50, {"needle"}, 1.2, 0.0); assert(s > prev); prev = s; double idf = std::log(1 + (51 - 1 + 0.5) / (1 + 0.5)); bound = idf * (1.2 + 1); assert(s < bound + 1e-9); } assert(prev > 0.99 * bound);          // b=0: 길이 무시, 점수가 (k1+1)·idf 로 수렴
      Corpus L; L.add({"needle", "a", "b"}); Doc longDoc(200, "pad"); longDoc[0] = "needle"; L.add(longDoc); L.add({"x"}); assert(bm25(L, 0, {"needle"}) > bm25(L, 1, {"needle"})); }          // 같은 tf 면 긴 문서의 점수가 낮다
    // ④ 주제별 말뭉치: 주제 5 개 × 문서 40 개, 문서는 주제 단어 80 % + 공통 단어 20 %
    { Corpus c; std::vector<int> topic; for (int t = 0; t < 5; ++t) for (int d = 0; d < 40; ++d) { Doc doc; for (int k = 0; k < 60; ++k) doc.push_back(rng() % 5 == 0 ? "common" + std::to_string(rng() % 30) : "t" + std::to_string(t) + "_" + std::to_string(rng() % 25)); c.add(doc); topic.push_back(t); }
      Index ix(c); double precisionCos = 0, precisionBm = 0; int Q = 100; for (int q = 0; q < Q; ++q) { int t = (int)(rng() % 5); Doc query; for (int k = 0; k < 3; ++k) query.push_back("t" + std::to_string(t) + "_" + std::to_string(rng() % 25)); std::vector<double> s = ix.scores(query); for (int d : topK(s, 10)) precisionCos += topic[d] == t; std::vector<double> bs(c.N); for (int d = 0; d < c.N; ++d) bs[d] = bm25(c, d, query); for (int d : topK(bs, 10)) precisionBm += topic[d] == t; }
      precisionCos /= (10.0 * Q); precisionBm /= (10.0 * Q); assert(precisionCos > 0.9 && precisionBm > 0.9); std::cout << "TFIDF: inverted-index scores matched dense cosine on 100 queries x 300 documents; precision@10 on 5 topics was " << precisionCos << " (tf-idf cosine) and " << precisionBm << " (BM25)" << std::endl; }
    return 0;
}
// Time Complexity: 색인 O(총 토큰), 질의 O(질의 단어의 색인 목록 길이 합)
// Space Complexity: O(고유 (단어, 문서) 쌍)
```
# Part 16. 생물정보학
## 문자열 알고리즘의 생물정보학 활용
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// DNA 는 알파벳 {A, C, G, T} 의 문자열이다. 기본 연산: 역상보 서열, GC 함량, k-mer 개수 세기, 제한효소 인식 부위(모티프) 찾기
std::string reverseComplement(const std::string& dna) {
    std::string r(dna.rbegin(), dna.rend());
    for (char& c : r) c = c == 'A' ? 'T' : c == 'T' ? 'A' : c == 'C' ? 'G' : 'C';
    return r;
}
double gcContent(const std::string& dna) { return double(std::count(dna.begin(), dna.end(), 'G') + std::count(dna.begin(), dna.end(), 'C')) / dna.size(); }
std::map<std::string, int> kmers(const std::string& dna, int k) { std::map<std::string, int> m; for (size_t i = 0; i + k <= dna.size(); i++) m[dna.substr(i, k)]++; return m; }

int main() {
    std::string dna = "AGCTTGAATTCGGATCCAAGCTTGAATTC";
    assert(reverseComplement("ATGC") == "GCAT");
    assert(reverseComplement(reverseComplement(dna)) == dna);        // 역상보의 역상보는 원래 서열
    assert(reverseComplement("GAATTC") == "GAATTC");                 // 제한효소 EcoRI 부위는 회문형 (역상보와 같다)
    assert(std::abs(gcContent("GGCC") - 1.0) < 1e-12 && std::abs(gcContent("ATGC") - 0.5) < 1e-12);
    auto k = kmers(dna, 6);
    assert(k["GAATTC"] == 2);                                        // EcoRI 인식 부위가 두 번
    std::vector<size_t> sites; for (size_t p = dna.find("GAATTC"); p != std::string::npos; p = dna.find("GAATTC", p + 1)) sites.push_back(p);
    assert((sites == std::vector<size_t>{5, 23}));
    std::cout << "EcoRI sites at positions " << sites[0] << " and " << sites[1] << ", GC=" << gcContent(dna) << std::endl;
    return 0;
}
// Time Complexity: O(n) (k-mer 세기 O(n·k))
// Space Complexity: O(고유 k-mer 수)
```
## NeedlemanWunsch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 니들만-브니쉬: 두 서열의 "전역" 정렬(처음부터 끝까지). 일치 +1, 불일치 −1, 갭 −1 같은 점수 합이 최대인 정렬을 DP 로 구한다. 편집 거리와 같은 구조에서 최소 대신 최대.
//  ① 정렬 전수 열거(델라누아 수: 6×6 이면 8989 개)로 최적 점수와 *최적 정렬의 개수*를 독립 계산해 DP 와 대조  ② 정렬 결과를 다시 채점하면 DP 점수와 같고, 갭을 빼면 원래 서열
//  ③ 점수 체계를 바꾸면 이미 아는 문제가 된다: (일치 0, 불일치 −1, 갭 −1) → −Levenshtein, (일치 1, 불일치 −∞, 갭 0) → LCS 길이  ④ 아핀 갭(Gotoh): 갭 길이 k 의 비용 = open + (k−1)·extend 를 상태 3 개의 DP 로, 전수 열거와 대조.
struct Score { int match = 1, mismatch = -1, gap = -1; };
struct Result { int score; std::string a, b; };
std::vector<std::vector<int>> fillTable(const std::string& x, const std::string& y, const Score& sc) {
    size_t n = x.size(), m = y.size(); std::vector<std::vector<int>> f(n + 1, std::vector<int>(m + 1)); for (size_t i = 0; i <= n; ++i) f[i][0] = (int)i * sc.gap; for (size_t j = 0; j <= m; ++j) f[0][j] = (int)j * sc.gap;
    for (size_t i = 1; i <= n; ++i) for (size_t j = 1; j <= m; ++j) f[i][j] = std::max({f[i - 1][j - 1] + (x[i - 1] == y[j - 1] ? sc.match : sc.mismatch), f[i - 1][j] + sc.gap, f[i][j - 1] + sc.gap});
    return f;
}
Result needlemanWunsch(const std::string& x, const std::string& y, const Score& sc = Score()) {
    auto f = fillTable(x, y, sc); size_t i = x.size(), j = y.size(); std::string a, b;
    while (i > 0 || j > 0) { if (i && j && f[i][j] == f[i - 1][j - 1] + (x[i - 1] == y[j - 1] ? sc.match : sc.mismatch)) { a += x[--i]; b += y[--j]; } else if (i && f[i][j] == f[i - 1][j] + sc.gap) { a += x[--i]; b += '-'; } else { a += '-'; b += y[--j]; } }
    std::reverse(a.begin(), a.end()); std::reverse(b.begin(), b.end()); return {f[x.size()][y.size()], a, b};
}
int rescore(const Result& r, const Score& sc = Score()) { int s = 0; for (size_t i = 0; i < r.a.size(); ++i) s += (r.a[i] == '-' || r.b[i] == '-') ? sc.gap : (r.a[i] == r.b[i] ? sc.match : sc.mismatch); return s; }
int scoreOnly(const std::string& x, const std::string& y, const Score& sc) { std::vector<int> prev(y.size() + 1), cur(y.size() + 1); for (size_t j = 0; j <= y.size(); ++j) prev[j] = (int)j * sc.gap; for (size_t i = 1; i <= x.size(); ++i) { cur[0] = (int)i * sc.gap; for (size_t j = 1; j <= y.size(); ++j) cur[j] = std::max({prev[j - 1] + (x[i - 1] == y[j - 1] ? sc.match : sc.mismatch), prev[j] + sc.gap, cur[j - 1] + sc.gap}); std::swap(prev, cur); } return prev[y.size()]; }
void enumerate(const std::string& x, const std::string& y, size_t i, size_t j, int score, const Score& sc, int& best, long& count) {            // 모든 정렬을 무차별로 (메모 없음)
    if (i == x.size() && j == y.size()) { if (score > best) { best = score; count = 1; } else if (score == best) ++count; return; }
    if (i < x.size() && j < y.size()) enumerate(x, y, i + 1, j + 1, score + (x[i] == y[j] ? sc.match : sc.mismatch), sc, best, count);
    if (i < x.size()) { enumerate(x, y, i + 1, j, score + sc.gap, sc, best, count); }
    if (j < y.size()) { enumerate(x, y, i, j + 1, score + sc.gap, sc, best, count); }
}
long countOptimal(const std::string& x, const std::string& y, const Score& sc) { auto f = fillTable(x, y, sc); std::vector<std::vector<long>> c(x.size() + 1, std::vector<long>(y.size() + 1, 0)); c[0][0] = 1;
    for (size_t i = 0; i <= x.size(); ++i) for (size_t j = 0; j <= y.size(); ++j) { if (!i && !j) continue; long t = 0; if (i && j && f[i][j] == f[i - 1][j - 1] + (x[i - 1] == y[j - 1] ? sc.match : sc.mismatch)) t += c[i - 1][j - 1]; if (i && f[i][j] == f[i - 1][j] + sc.gap) t += c[i - 1][j]; if (j && f[i][j] == f[i][j - 1] + sc.gap) t += c[i][j - 1]; c[i][j] = t; } return c[x.size()][y.size()]; }
// 아핀 갭 (Gotoh): M = 끝이 (일치/불일치), X = 끝이 x 의 글자 vs 갭, Y = 끝이 갭 vs y 의 글자
int affine(const std::string& x, const std::string& y, int match, int mismatch, int open, int extend) {
    const int NEG = INT_MIN / 4; size_t n = x.size(), m = y.size(); std::vector<std::vector<int>> M(n + 1, std::vector<int>(m + 1, NEG)), X = M, Y = M; M[0][0] = 0;
    for (size_t i = 0; i <= n; ++i) for (size_t j = 0; j <= m; ++j) { if (i && j) M[i][j] = std::max({M[i - 1][j - 1], X[i - 1][j - 1], Y[i - 1][j - 1]}) + (x[i - 1] == y[j - 1] ? match : mismatch);
        if (i) X[i][j] = std::max({M[i - 1][j] + open, Y[i - 1][j] + open, X[i - 1][j] + extend}); if (j) Y[i][j] = std::max({M[i][j - 1] + open, X[i][j - 1] + open, Y[i][j - 1] + extend}); }
    return std::max({M[n][m], X[n][m], Y[n][m]});
}
void enumAffine(const std::string& x, const std::string& y, size_t i, size_t j, int last, int score, int match, int mismatch, int open, int extend, int& best) {             // last: 0 = 시작/일치, 1 = x 갭..., 2 = y 갭
    if (i == x.size() && j == y.size()) { best = std::max(best, score); return; }
    if (i < x.size() && j < y.size()) enumAffine(x, y, i + 1, j + 1, 0, score + (x[i] == y[j] ? match : mismatch), match, mismatch, open, extend, best);
    if (i < x.size()) { enumAffine(x, y, i + 1, j, 1, score + (last == 1 ? extend : open), match, mismatch, open, extend, best); }
    if (j < y.size()) { enumAffine(x, y, i, j + 1, 2, score + (last == 2 ? extend : open), match, mismatch, open, extend, best); }
}

int main() {
    auto r = needlemanWunsch("GCATGCG", "GATTACA"); assert(r.score == 0 && rescore(r) == r.score && needlemanWunsch("ACGT", "ACGT").score == 4);                   // 위키피디아의 표준 예
    std::mt19937 rng(25);
    for (int it = 0; it < 1200; ++it) {
        std::string x(rng() % 7, 'a'), y(rng() % 7, 'a'); int sigma = 2 + (int)(rng() % 3); for (char& c : x) c = (char)('a' + rng() % sigma); for (char& c : y) c = (char)('a' + rng() % sigma); Score sc; sc.match = 1 + (int)(rng() % 3); sc.mismatch = -(int)(rng() % 4); sc.gap = -1 - (int)(rng() % 3);
        Result res = needlemanWunsch(x, y, sc); int best = INT_MIN; long cnt = 0; enumerate(x, y, 0, 0, 0, sc, best, cnt);
        std::string ra, rb; for (char c : res.a) if (c != '-') ra += c; for (char c : res.b) if (c != '-') rb += c;
        assert(res.score == best && countOptimal(x, y, sc) == cnt && rescore(res, sc) == res.score && ra == x && rb == y && res.a.size() == res.b.size() && scoreOnly(x, y, sc) == res.score && needlemanWunsch(y, x, sc).score == res.score);            // ① ② + 대칭
        Score ed; ed.match = 0; ed.mismatch = -1; ed.gap = -1; int lev = 0; { std::vector<std::vector<int>> d(x.size() + 1, std::vector<int>(y.size() + 1)); for (size_t i = 0; i <= x.size(); ++i) d[i][0] = (int)i; for (size_t j = 0; j <= y.size(); ++j) d[0][j] = (int)j; for (size_t i = 1; i <= x.size(); ++i) for (size_t j = 1; j <= y.size(); ++j) d[i][j] = std::min({d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (x[i - 1] != y[j - 1])}); lev = d[x.size()][y.size()]; }
        assert(scoreOnly(x, y, ed) == -lev);                                                                                                                                  // ③ 편집 거리
        Score lc; lc.match = 1; lc.mismatch = -1000; lc.gap = 0; std::vector<std::vector<int>> L(x.size() + 1, std::vector<int>(y.size() + 1, 0)); for (size_t i = 1; i <= x.size(); ++i) for (size_t j = 1; j <= y.size(); ++j) L[i][j] = x[i - 1] == y[j - 1] ? L[i - 1][j - 1] + 1 : std::max(L[i - 1][j], L[i][j - 1]); assert(scoreOnly(x, y, lc) == L[x.size()][y.size()]);                // ③ LCS
        int open = -(2 + (int)(rng() % 4)), extend = -1 - (int)(rng() % 2), bestAff = INT_MIN; enumAffine(x, y, 0, 0, 0, 0, sc.match, sc.mismatch, open, extend, bestAff); if (x.empty() && y.empty()) bestAff = 0; assert(affine(x, y, sc.match, sc.mismatch, open, extend) == bestAff);     // ④ 아핀 갭
    }
    { std::string x(2000, 'a'), y(2000, 'a'); for (char& c : x) c = (char)('a' + rng() % 4); for (char& c : y) c = (char)('a' + rng() % 4); Result big = needlemanWunsch(x, y); assert(rescore(big) == big.score && big.score == scoreOnly(x, y, Score()));
      std::cout << "NeedlemanWunsch: DP score and optimal-alignment count equal exhaustive enumeration on 1200 random cases; (0,-1,-1) scoring gave -Levenshtein, (1,-inf,0) gave LCS, affine gaps matched enumeration; a 2000x2000 alignment scored " << big.score << std::endl; }
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(n·m) (점수만 O(min(n, m)), Hirschberg 로 정렬도 O(n + m))
```
## SmithWaterman()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 스미스-워터먼: 두 서열의 "지역" 정렬 — 가장 비슷한 부분 구간만 찾는다. 전역 정렬과 달리 점수가 0 아래로 내려가면 0 으로 재시작하고, 표 전체의 최댓값 칸에서 0 을 만날 때까지 거슬러 올라간다 (BLAST 의 기반).
//  ① 독립 오라클: 두 문자열의 *모든 부분 문자열 쌍*에 전역 정렬(니들만-브니쉬) 점수를 구해 최댓값을 취한 값(빈 부분은 0) — 지역 정렬 점수와 같아야 한다.  ② 되돌린 정렬의 점수 재계산, 두 구간이 원본의 부분 문자열
//  ③ 지역 점수 ≥ max(0, 전역 점수).  ④ 무작위 서열에 같은 구간을 심으면 그 구간을 정확한 좌표로 찾고(점수 = 일치 점수 × 길이) 우연한 점수보다 훨씬 높다.
struct Result { int score; std::string a, b; size_t aStart, bStart; };
struct Sc { int match = 3, mismatch = -3, gap = -2; };
Result smithWaterman(const std::string& x, const std::string& y, const Sc& sc = Sc()) {
    size_t n = x.size(), m = y.size(); std::vector<std::vector<int>> h(n + 1, std::vector<int>(m + 1, 0)); int best = 0; size_t bi = 0, bj = 0;
    for (size_t i = 1; i <= n; ++i) for (size_t j = 1; j <= m; ++j) { h[i][j] = std::max({0, h[i - 1][j - 1] + (x[i - 1] == y[j - 1] ? sc.match : sc.mismatch), h[i - 1][j] + sc.gap, h[i][j - 1] + sc.gap}); if (h[i][j] > best) { best = h[i][j]; bi = i; bj = j; } }
    std::string a, b; size_t i = bi, j = bj;
    while (i > 0 && j > 0 && h[i][j] > 0) { if (h[i][j] == h[i - 1][j - 1] + (x[i - 1] == y[j - 1] ? sc.match : sc.mismatch)) { a += x[--i]; b += y[--j]; } else if (h[i][j] == h[i - 1][j] + sc.gap) { a += x[--i]; b += '-'; } else { a += '-'; b += y[--j]; } }
    std::reverse(a.begin(), a.end()); std::reverse(b.begin(), b.end()); return {best, a, b, i, j};
}
int nwScore(const std::string& x, const std::string& y, const Sc& sc) { std::vector<int> prev(y.size() + 1), cur(y.size() + 1); for (size_t j = 0; j <= y.size(); ++j) prev[j] = (int)j * sc.gap; for (size_t i = 1; i <= x.size(); ++i) { cur[0] = (int)i * sc.gap; for (size_t j = 1; j <= y.size(); ++j) cur[j] = std::max({prev[j - 1] + (x[i - 1] == y[j - 1] ? sc.match : sc.mismatch), prev[j] + sc.gap, cur[j - 1] + sc.gap}); std::swap(prev, cur); } return prev[y.size()]; }
int bruteLocal(const std::string& x, const std::string& y, const Sc& sc) { int best = 0; for (size_t i = 0; i < x.size(); ++i) for (size_t li = 1; i + li <= x.size(); ++li) for (size_t j = 0; j < y.size(); ++j) for (size_t lj = 1; j + lj <= y.size(); ++lj) best = std::max(best, nwScore(x.substr(i, li), y.substr(j, lj), sc)); return best; }
int rescore(const Result& r, const Sc& sc) { int s = 0; for (size_t i = 0; i < r.a.size(); ++i) s += (r.a[i] == '-' || r.b[i] == '-') ? sc.gap : (r.a[i] == r.b[i] ? sc.match : sc.mismatch); return s; }

int main() {
    auto r = smithWaterman("TGTTACGG", "GGTTGACTA"); assert(r.score == 13 && r.a == "GTT-AC" && r.b == "GTTGAC" && rescore(r, Sc()) == r.score && smithWaterman("AAAA", "TTTT").score == 0);              // 위키피디아의 표준 예
    std::mt19937 rng(31);
    for (int it = 0; it < 3000; ++it) {
        std::string x(rng() % 8, 'a'), y(rng() % 8, 'a'); int sigma = 2 + (int)(rng() % 3); for (char& c : x) c = (char)('a' + rng() % sigma); for (char& c : y) c = (char)('a' + rng() % sigma); Sc sc; sc.match = 1 + (int)(rng() % 4); sc.mismatch = -1 - (int)(rng() % 3); sc.gap = -1 - (int)(rng() % 3);
        Result res = smithWaterman(x, y, sc); std::string ra, rb; for (char c : res.a) if (c != '-') ra += c; for (char c : res.b) if (c != '-') rb += c;
        assert(res.score == bruteLocal(x, y, sc) && rescore(res, sc) == res.score && x.compare(res.aStart, ra.size(), ra) == 0 && y.compare(res.bStart, rb.size(), rb) == 0 && res.score >= std::max(0, nwScore(x, y, sc)) && res.a.size() == res.b.size());
    }
    // ④ 같은 구간을 심은 무작위 서열.  점수 체계가 "로그 영역"(무작위 서열의 기대 열 점수 < 0, 갭이 비쌈)이어야 유의미하다: 일치 +2, 불일치 −3, 갭 −5
    Sc plant; plant.match = 2; plant.mismatch = -3; plant.gap = -5;
    for (int it = 0; it < 20; ++it) {
        std::string x(800, 'a'), y(700, 'a'); for (char& c : x) c = (char)('a' + rng() % 4); for (char& c : y) c = (char)('a' + rng() % 4); int noise = smithWaterman(x, y, plant).score;           // 심기 전의 우연한 최고 점수
        std::string motif(60, 'a'); for (char& c : motif) c = (char)('a' + rng() % 4); size_t px = 100 + rng() % 600, py = 100 + rng() % 500; x.replace(px, 60, motif); y.replace(py, 60, motif);
        Result res = smithWaterman(x, y, plant); std::string ra; for (char c : res.a) if (c != '-') ra += c;
        assert(res.score >= 2 * 60 && ra.find(motif.substr(10, 40)) != std::string::npos && res.score > 2 * noise && std::abs((long)res.aStart - (long)px) <= 25 && std::abs((long)res.bStart - (long)py) <= 25 && rescore(res, plant) == res.score);          // 점수 ≥ 120, 좌표 일치, 우연 점수의 두 배 이상
    }
    // 점수 체계가 영역을 정한다: (3, −3, −2) 는 무작위 서열에서도 점수가 길이에 비례(선형 영역)해 지역 정렬이 무의미하고, (2, −3, −5) 는 길이의 로그에 가깝게만 자란다
    double linear, logarithmic;
    { std::string x1(400, 'a'), y1(400, 'a'), x2(1600, 'a'), y2(1600, 'a'); for (auto* v : {&x1, &y1, &x2, &y2}) for (char& c : *v) c = (char)('a' + rng() % 4);
      linear = (double)smithWaterman(x2, y2).score / smithWaterman(x1, y1).score; logarithmic = (double)smithWaterman(x2, y2, plant).score / std::max(1, smithWaterman(x1, y1, plant).score); assert(linear > 3 && logarithmic < 2); }
    { std::string x(3000, 'a'), y(3000, 'a'); for (char& c : x) c = (char)('a' + rng() % 4); for (char& c : y) c = (char)('a' + rng() % 4); Result res = smithWaterman(x, y, plant); assert(res.score > 0 && rescore(res, plant) == res.score);
      std::cout << "SmithWaterman: local scores equal the best global alignment over all substring pairs on 3000 random cases; a 60-letter motif planted in two random sequences was found (score >= 120, well above the chance level) with the (2,-3,-5) scheme; quadrupling the length multiplied the random-pair score by " << linear << " under (3,-3,-2) but only " << logarithmic << " under (2,-3,-5); two random 3000-letter sequences scored " << res.score << std::endl; }
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(n·m)
```
# Part 17. AI와 NLP
## BytePairEncoding()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// BPE: 글자 단위에서 시작해 "가장 자주 붙어 나오는 인접 쌍"을 하나의 새 토큰으로 합치는 일을 반복해 어휘를 학습한다 (GPT 계열).
// 추론은 학습된 병합을 "학습된 순서대로" 적용한다.  단어 끝 표식 </w> 로 단어 경계를 보존
typedef std::vector<std::string> Seq;
typedef std::pair<std::string, std::string> Pair;

std::vector<Pair> train(const std::map<std::string, int>& wordFreq, int numMerges) {
    std::map<Seq, int> vocab;
    for (auto& kv : wordFreq) { Seq s; for (char c : kv.first) s.push_back(std::string(1, c)); s.push_back("</w>"); vocab[s] = kv.second; }
    std::vector<Pair> merges;
    for (int it = 0; it < numMerges; it++) {
        std::map<Pair, int> cnt;
        for (auto& kv : vocab) for (size_t i = 0; i + 1 < kv.first.size(); i++) cnt[{kv.first[i], kv.first[i + 1]}] += kv.second;
        if (cnt.empty()) break;
        Pair best; int bc = 0;
        for (auto& kv : cnt) if (kv.second > bc) { bc = kv.second; best = kv.first; }     // 빈도 최대, 동률이면 사전순 앞쪽
        merges.push_back(best);
        std::map<Seq, int> next;
        for (auto& kv : vocab) {
            Seq s; for (size_t i = 0; i < kv.first.size(); i++) {
                if (i + 1 < kv.first.size() && kv.first[i] == best.first && kv.first[i + 1] == best.second) { s.push_back(best.first + best.second); i++; }
                else s.push_back(kv.first[i]);
            }
            next[s] += kv.second;
        }
        vocab.swap(next);
    }
    return merges;
}
Seq encode(const std::string& word, const std::vector<Pair>& merges) {
    Seq s; for (char c : word) s.push_back(std::string(1, c)); s.push_back("</w>");
    for (auto& m : merges) {
        Seq t; for (size_t i = 0; i < s.size(); i++) {
            if (i + 1 < s.size() && s[i] == m.first && s[i + 1] == m.second) { t.push_back(m.first + m.second); i++; } else t.push_back(s[i]);
        }
        s.swap(t);
    }
    return s;
}

int main() {
    std::map<std::string, int> corpus = {{"low", 5}, {"lower", 2}, {"newest", 6}, {"widest", 3}};     // Sennrich et al. (2016) 의 예
    auto merges = train(corpus, 10);
    assert((merges[0] == Pair{"e", "s"}) && (merges[1] == Pair{"es", "t"}) && (merges[2] == Pair{"est", "</w>"}));   // 빈도 9 인 쌍부터
    Seq e = encode("newest", merges);
    auto endsWithEst = [](const std::string& s) { return s.size() >= 7 && s.compare(s.size() - 7, 7, "est</w>") == 0; };
    assert(endsWithEst(e.back()));                                     // "newest" 는 est</w> 로 끝나는 (더 큰) 토큰으로 끝난다
    Seq u = encode("lowest", merges);                                  // 학습에 없던 단어도 학습된 조각으로 분해된다
    assert(endsWithEst(u.back()) && u.size() >= 2);
    std::string joined; for (auto& t : u) joined += t;
    assert(joined == "lowest</w>");                                    // 이어 붙이면 원문 (+ 단어 끝 표식)
    std::cout << "BPE merges: "; for (int i = 0; i < 5; i++) std::cout << merges[i].first << "+" << merges[i].second << " "; std::cout << std::endl;
    return 0;
}
// Time Complexity: 학습 O(병합 수 · 코퍼스 크기), 추론 O(병합 수 · 단어 길이)
// Space Complexity: O(어휘)
```
## WordPiece()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// WordPiece(BERT): 추론은 "가장 긴 일치 우선(MaxMatch)" 탐욕 방식이다. 단어 중간 조각에는 "##" 접두사를 붙인다.
// 학습은 BPE 와 달리 빈도가 아니라 점수 score(a, b) = freq(ab) / (freq(a) · freq(b)) 가 가장 큰 쌍을 합친다
//  -> 서로 자주 같이 나오지만 각자는 드문 쌍을 선호 (우도 기반)
std::vector<std::string> wordpiece(const std::string& word, const std::set<std::string>& vocab) {
    std::vector<std::string> out; size_t start = 0;
    while (start < word.size()) {
        size_t end = word.size(); std::string cur;
        while (start < end) {
            std::string sub = word.substr(start, end - start);
            if (start > 0) sub = "##" + sub;
            if (vocab.count(sub)) { cur = sub; break; }
            end--;
        }
        if (cur.empty()) return {"[UNK]"};                              // 어떤 조각도 맞지 않으면 단어 전체가 [UNK]
        out.push_back(cur); start = end;
    }
    return out;
}
std::pair<std::string, std::string> bestPairByScore(const std::map<std::pair<std::string, std::string>, int>& pairFreq, const std::map<std::string, int>& unitFreq) {
    double best = -1; std::pair<std::string, std::string> arg;
    for (auto& kv : pairFreq) {
        double sc = double(kv.second) / (unitFreq.at(kv.first.first) * double(unitFreq.at(kv.first.second)));
        if (sc > best) { best = sc; arg = kv.first; }
    }
    return arg;
}

int main() {
    std::set<std::string> vocab = {"un", "##aff", "##able", "play", "##ing", "##ed", "a", "##b"};
    using V = std::vector<std::string>;
    assert((wordpiece("unaffable", vocab) == V{"un", "##aff", "##able"}));
    assert((wordpiece("playing", vocab) == V{"play", "##ing"}));
    assert((wordpiece("zzz", vocab) == V{"[UNK]"}));
    // 학습 점수: ("q","u") 는 q 가 항상 u 와 함께 나오므로, 흔한 글자끼리의 쌍보다 점수가 높다
    std::map<std::pair<std::string, std::string>, int> pf = {{{"q", "u"}, 10}, {{"e", "r"}, 30}};
    std::map<std::string, int> uf = {{"q", 10}, {"u", 50}, {"e", 200}, {"r", 100}};
    assert((bestPairByScore(pf, uf) == std::make_pair(std::string("q"), std::string("u"))));
    std::cout << "WordPiece: unaffable -> un ##aff ##able" << std::endl;
    return 0;
}
// Time Complexity: 추론 O(L²) (L = 단어 길이), 학습 O(병합 수 · 코퍼스)
// Space Complexity: O(어휘)
```
## SentencePiece()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// SentencePiece(LLaMA, T5): 공백을 일반 기호 "▁"(U+2581)로 바꿔 원문을 그대로 토큰화하므로 언어별 전처리(단어 분리)가 필요 없다.
// Unigram 모델은 조각마다 로그 확률을 두고, 문장 전체 확률이 최대인 분할을 Viterbi DP 로 찾는다
std::vector<std::string> utf8Chars(const std::string& s) {
    std::vector<std::string> v;
    for (size_t i = 0; i < s.size();) { unsigned char c = s[i]; size_t len = c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 1; v.push_back(s.substr(i, len)); i += len; }
    return v;
}
std::vector<std::string> viterbi(const std::string& text, const std::map<std::string, double>& logp) {
    auto ch = utf8Chars(text); size_t n = ch.size();
    std::vector<double> best(n + 1, -1e18); std::vector<int> from(n + 1, -1);
    best[0] = 0;
    for (size_t i = 0; i < n; i++) {
        if (best[i] <= -1e17) continue;
        std::string piece;
        for (size_t j = i; j < n && j - i < 8; j++) {
            piece += ch[j];
            auto it = logp.find(piece);
            if (it != logp.end() && best[i] + it->second > best[j + 1]) { best[j + 1] = best[i] + it->second; from[j + 1] = i; }
        }
    }
    std::vector<std::string> out;
    for (int j = n; j > 0 && from[j] >= 0; j = from[j]) { std::string p; for (int k = from[j]; k < j; k++) p += ch[k]; out.insert(out.begin(), p); }
    return out;
}

int main() {
    std::map<std::string, double> lp = {
        {"▁hello", std::log(0.05)}, {"▁world", std::log(0.04)}, {"▁hell", std::log(0.01)}, {"o", std::log(0.03)},
        {"▁", std::log(0.1)}, {"h", std::log(0.02)}, {"e", std::log(0.05)}, {"l", std::log(0.04)}, {"w", std::log(0.02)},
        {"r", std::log(0.04)}, {"d", std::log(0.03)}, {"▁w", std::log(0.005)}, {"orld", std::log(0.002)}};
    using V = std::vector<std::string>;
    assert((viterbi("▁hello▁world", lp) == V{"▁hello", "▁world"}));         // 긴 조각 하나가 짧은 조각 여러 개의 곱보다 확률이 높다
    assert((viterbi("▁hello", lp) == V{"▁hello"}));
    assert((viterbi("▁world", {{"▁", std::log(0.1)}, {"w", std::log(0.02)}, {"o", std::log(0.03)}, {"r", std::log(0.04)}, {"l", std::log(0.04)}, {"d", std::log(0.03)}}) == V{"▁", "w", "o", "r", "l", "d"}));   // 큰 조각이 없으면 글자 단위
    std::cout << "SentencePiece unigram segmentation verified." << std::endl;
    return 0;
}
// Time Complexity: O(n · 최대 조각 길이)
// Space Complexity: O(n)
```
## TokenizeLLM()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// LLM 에 프롬프트가 들어가는 경로: 텍스트 -> (사전 토큰화: 공백 앞붙은 단어) -> BPE 병합 -> 토큰 -> 정수 ID -> [BOS, ..., EOS]
// GPT-2 계열은 공백을 "Ġ" 로 표시해 단어 앞에 붙인다.  병합 순서(순위)가 곧 우선순위
typedef std::vector<std::string> Seq;
const std::string G = "Ġ";                                           // U+0120, 공백 대신 쓰는 가시 문자
Seq preTokenize(const std::string& text) {
    Seq words; std::string cur;
    for (size_t i = 0; i < text.size(); i++) {
        if (text[i] == ' ') { if (!cur.empty()) words.push_back(cur); cur = G; }       // 공백은 다음 단어의 접두로
        else cur += text[i];
    }
    if (!cur.empty()) words.push_back(cur);
    return words;
}
Seq bpe(const std::string& word, const std::vector<std::pair<std::string, std::string>>& merges) {
    Seq s; for (size_t i = 0; i < word.size();) { size_t len = (unsigned char)word[i] >= 0xC0 ? 2 : 1; s.push_back(word.substr(i, len)); i += len; }
    for (auto& m : merges) {
        Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == m.first && s[i + 1] == m.second) { t.push_back(m.first + m.second); i++; } else t.push_back(s[i]); }
        s.swap(t);
    }
    return s;
}

int main() {
    std::vector<std::pair<std::string, std::string>> merges = {{"h", "e"}, {"he", "l"}, {"hel", "l"}, {"hell", "o"}, {G, "hello"}, {"w", "o"}, {"wo", "r"}, {"wor", "l"}, {"worl", "d"}, {G, "world"}};
    std::vector<std::string> vocabList = {"<bos>", "<eos>", "h", "e", "l", "o", "w", "r", "d", ",", "!", G};
    for (auto& m : merges) vocabList.push_back(m.first + m.second);
    std::map<std::string, int> id; for (size_t i = 0; i < vocabList.size(); i++) id[vocabList[i]] = i;

    auto encode = [&](const std::string& text) {
        std::vector<int> ids = {id["<bos>"]};
        for (auto& w : preTokenize(text)) for (auto& t : bpe(w, merges)) ids.push_back(id.at(t));
        ids.push_back(id["<eos>"]);
        return ids;
    };
    auto ids = encode("hello world");
    assert((ids == std::vector<int>{id["<bos>"], id["hello"], id[G + "world"], id["<eos>"]}));
    assert(ids.size() == 4);                                           // 11글자가 토큰 2개(+특수 토큰 2개)로 줄어든다
    auto ids2 = encode("hello hello");
    assert(ids2[1] == id["hello"] && ids2[2] == id[G + "hello"]);      // 같은 단어라도 앞에 공백이 있으면 다른 토큰
    std::cout << "TokenizeLLM: 'hello world' ->"; for (int i : ids) std::cout << " " << i; std::cout << std::endl;
    return 0;
}
// Time Complexity: O(병합 수 · 단어 길이) (실제 구현은 우선순위 큐로 O(n log n))
// Space Complexity: O(어휘 + n)
```
## EmbeddingLookup()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 임베딩 조회: 토큰 ID -> 벡터.  (V × d) 행렬의 한 행을 꺼내는 gather 연산이며,
// 원-핫 벡터(길이 V)와 행렬을 곱한 결과와 수학적으로 같지만 O(d) 로 훨씬 싸다 (곱셈은 O(V·d))
typedef std::vector<float> Vec;
int main() {
    const int V = 1000, D = 16;
    std::mt19937 rng(8); std::normal_distribution<float> N(0, 1);
    std::vector<Vec> E(V, Vec(D));
    for (auto& row : E) for (auto& x : row) x = N(rng);

    std::vector<int> ids = {5, 42, 7, 42};
    std::vector<Vec> out; for (int i : ids) out.push_back(E[i]);                 // gather
    assert(out[1] == out[3]);                                                   // 같은 ID 는 같은 벡터

    // 원-핫 × 행렬 == 행 조회
    Vec oneHot(V, 0); oneHot[42] = 1;
    Vec viaMatmul(D, 0);
    for (int v = 0; v < V; v++) for (int d = 0; d < D; d++) viaMatmul[d] += oneHot[v] * E[v][d];
    assert(viaMatmul == E[42]);

    // 문장 벡터: 토큰 임베딩의 평균 풀링
    Vec pooled(D, 0); for (auto& v : out) for (int d = 0; d < D; d++) pooled[d] += v[d] / out.size();
    // 코사인 유사도: 자기 자신은 1
    auto cosine = [&](const Vec& a, const Vec& b) { double s = 0, na = 0, nb = 0; for (int d = 0; d < D; d++) { s += a[d] * b[d]; na += a[d] * a[d]; nb += b[d] * b[d]; } return s / std::sqrt(na * nb); };
    assert(std::fabs(cosine(E[5], E[5]) - 1.0) < 1e-6);
    assert(std::fabs(cosine(E[5], E[7])) < 0.9);                                // 무작위 초기화 벡터끼리는 거의 직교
    std::cout << "EmbeddingLookup: gathered " << out.size() << " rows of dim " << D << std::endl;
    return 0;
}
// Time Complexity: 조회 O(d), 원-핫 행렬곱 O(V·d)
// Space Complexity: O(V·d)
```
## Detokenize()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 역토큰화(detokenize): 생성된 토큰 ID -> 문자열.  (1) 토큰을 이어 붙이고 (2) "Ġ" 를 공백으로 바꾸고 (3) 특수 토큰은 제거한다.
// 바이트 수준 BPE 에서는 한 글자(UTF-8 여러 바이트)가 토큰 여러 개에 걸쳐 나올 수 있으므로,
// 스트리밍 출력은 "아직 완성되지 않은 바이트"를 버퍼에 두었다가 코드 포인트가 완성될 때만 내보내야 한다
const std::string G = "Ġ";
std::string detokenize(const std::vector<std::string>& tokens) {
    std::string out;
    for (auto& t : tokens) {
        if (t == "<bos>" || t == "<eos>") continue;
        std::string s = t;
        for (size_t p = s.find(G); p != std::string::npos; p = s.find(G, p + 1)) s.replace(p, G.size(), " ");
        out += s;
    }
    if (!out.empty() && out[0] == ' ') out.erase(0, 1);                 // 맨 앞 공백 제거
    return out;
}
class StreamDecoder {
    std::string pending;
    static size_t need(unsigned char c) { return c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 1; }
public:
    std::string feed(const std::string& bytes) {
        pending += bytes; std::string out;
        while (!pending.empty()) {
            size_t n = need(pending[0]);
            if (pending.size() < n) break;                               // 아직 덜 도착한 글자
            out += pending.substr(0, n); pending.erase(0, n);
        }
        return out;
    }
    bool hasPending() const { return !pending.empty(); }
};

int main() {
    assert(detokenize({"<bos>", "hello", G + "world", "!", "<eos>"}) == "hello world!");
    assert(detokenize({G + "a", G + "b"}) == "a b");
    StreamDecoder d;                                                     // "한" = ED 95 9C 이 토큰 셋으로 쪼개져 도착
    assert(d.feed("\xED") == "" && d.hasPending());
    assert(d.feed("\x95") == "" && d.hasPending());
    assert(d.feed("\x9C") == "한" && !d.hasPending());
    assert(d.feed("ab") == "ab");
    std::cout << "Detokenize verified." << std::endl;
    return 0;
}
// Time Complexity: O(총 길이)
// Space Complexity: O(총 길이)
```
## LLM 토크나이저는 왜 필요한가?
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// 모델은 정수만 다룬다.  텍스트를 어떤 단위로 쪼갤지는 어휘 크기와 시퀀스 길이의 교환이다:
//   글자 단위: 어휘 작음, 시퀀스 매우 김   /   단어 단위: 시퀀스 짧음, 어휘 거대 + 처음 보는 단어(OOV)를 표현할 수 없음
//   서브워드(BPE): 둘의 중간, OOV 없음 (최악에도 글자 단위로 분해)
typedef std::vector<std::string> Seq;
typedef std::pair<std::string, std::string> Pair;
std::vector<Pair> trainBPE(const std::vector<std::string>& words, int merges) {
    std::vector<Seq> seqs; for (auto& w : words) { Seq s; for (char c : w) s.push_back(std::string(1, c)); seqs.push_back(s); }
    std::vector<Pair> out;
    for (int it = 0; it < merges; it++) {
        std::map<Pair, int> cnt; for (auto& s : seqs) for (size_t i = 0; i + 1 < s.size(); i++) cnt[{s[i], s[i + 1]}]++;
        Pair best; int bc = 1; for (auto& kv : cnt) if (kv.second > bc) { bc = kv.second; best = kv.first; }
        if (bc <= 1) break;
        out.push_back(best);
        for (auto& s : seqs) { Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == best.first && s[i + 1] == best.second) { t.push_back(best.first + best.second); i++; } else t.push_back(s[i]); } s.swap(t); }
    }
    return out;
}
size_t bpeLength(const std::string& w, const std::vector<Pair>& merges) {
    Seq s; for (char c : w) s.push_back(std::string(1, c));
    for (auto& m : merges) { Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == m.first && s[i + 1] == m.second) { t.push_back(m.first + m.second); i++; } else t.push_back(s[i]); } s.swap(t); }
    return s.size();
}

int main() {
    std::string train = "the cat sat on the mat the cat ate the rat the rat sat on the cat that is that";
    std::vector<std::string> trainWords; { std::istringstream in(train); std::string w; while (in >> w) trainWords.push_back(w); }
    auto merges = trainBPE(trainWords, 20);
    std::set<std::string> wordVocab(trainWords.begin(), trainWords.end());
    std::string test = "the cat sat on the hat";                        // "hat" 은 학습에 없던 단어
    std::vector<std::string> testWords; { std::istringstream in(test); std::string w; while (in >> w) testWords.push_back(w); }
    size_t charTokens = 0, bpeTokens = 0, wordTokens = testWords.size(), oov = 0;
    for (auto& w : testWords) { charTokens += w.size(); bpeTokens += bpeLength(w, merges); if (!wordVocab.count(w)) oov++; }
    assert(oov == 1);                                                   // 단어 단위는 "hat" 을 표현하지 못한다
    assert(wordTokens < bpeTokens && bpeTokens < charTokens);           // 길이: 단어 < BPE < 글자
    assert(bpeLength("hat", merges) >= 1);                              // BPE 는 처음 보는 단어도 조각으로 표현한다
    std::cout << "tokens for '" << test << "': word=" << wordTokens << " (OOV " << oov << ") bpe=" << bpeTokens << " char=" << charTokens << std::endl;
    return 0;
}
// Time Complexity: O(병합 수 · 코퍼스)
// Space Complexity: O(어휘)
```
# 부록
## KMP는 왜 O(n)인가?
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 증명의 핵심(분할상환): 포인터 k(매칭된 길이)는 텍스트 글자 하나당 많아야 1 증가한다 → 총 증가 ≤ n.  k 는 0 아래로 내려갈 수 없고 안쪽 while 의 한 반복마다 최소 1 감소하므로 총 감소 ≤ 총 증가 ≤ n.
// 따라서 안쪽 while 의 전체 반복 ≤ n, 텍스트를 훑는 총 연산 ≤ 2n 이다 (실패 함수 구성도 같은 논리로 O(m)).  이를 *매 실행마다* 항등식으로 검사한다: 증가 횟수 − 감소 총량 = 마지막 k.
//  전수 확인: 이진 텍스트(길이 14) × 이진 패턴(길이 1..6) 전부에서 while 반복 합의 최댓값이 n 이하임을 확인하고 최댓값을 보고한다 — 나이브의 비교 횟수와 나란히.
struct Run { long increments = 0, decrements = 0, whileSteps = 0, forSteps = 0; size_t finalK = 0; };
std::vector<int> failure(const std::string& p, Run* r = nullptr) {
    std::vector<int> pi(p.size(), 0); long inc = 0, dec = 0, wh = 0;
    for (size_t i = 1, k = 0; i < p.size(); ++i) { while (k > 0 && p[i] != p[k]) { size_t nk = (size_t)pi[k - 1]; dec += (long)(k - nk); k = nk; ++wh; } if (p[i] == p[k]) { ++k; ++inc; } pi[i] = (int)k; }
    if (r) { r->increments = inc; r->decrements = dec; r->whileSteps = wh; } return pi;
}
Run scan(const std::string& t, const std::string& p, const std::vector<int>& pi) {
    Run r; size_t k = 0;
    for (size_t i = 0; i < t.size(); ++i, ++r.forSteps) { while (k > 0 && t[i] != p[k]) { size_t nk = (size_t)pi[k - 1]; r.decrements += (long)(k - nk); k = nk; ++r.whileSteps; } if (t[i] == p[k]) { ++k; ++r.increments; } if (k == p.size()) { size_t nk = (size_t)pi[k - 1]; r.decrements += (long)(k - nk); k = nk; } }       // 일치 후 후퇴도 감소로 센다
    r.finalK = k; return r;
}
long naiveComparisons(const std::string& t, const std::string& p) { long c = 0; for (size_t i = 0; i + p.size() <= t.size(); ++i) { size_t j = 0; while (j < p.size()) { ++c; if (t[i + j] != p[j]) break; ++j; } } return c; }

int main() {
    std::string p(50, 'a'); p += 'b';
    for (std::string t : {std::string(100000, 'a'), std::string(50000, 'a') + "b" + std::string(50000, 'a'), std::string("ab").append(50000, 'a')}) {
        Run rf; std::vector<int> pi = failure(p, &rf); Run r = scan(t, p, pi);
        assert(r.whileSteps <= (long)t.size() && r.forSteps + r.whileSteps <= 2 * (long)t.size() && rf.whileSteps <= (long)p.size());                // 총 후퇴 ≤ n, 총 연산 ≤ 2n, 구성 비용 ≤ m
        std::cout << "n=" << t.size() << " forward=" << r.forSteps << " backtracks=" << r.whileSteps << " (naive would compare " << naiveComparisons(t, p) << ")\n";
    }
    // 매 실행의 항등식: 증가 − 감소 = 마지막 k (포텐셜 k 의 수지), 증가 ≤ n, 감소 ≤ 증가
    std::mt19937 rng(4);
    for (int it = 0; it < 200000; ++it) {
        std::string pat(1 + rng() % 8, 'a'), t(rng() % 60, 'a'); for (char& c : pat) c = (char)('a' + rng() % 2); for (char& c : t) c = (char)('a' + rng() % 2);
        Run rf; std::vector<int> pi = failure(pat, &rf); assert(rf.increments - rf.decrements == pi.back() && rf.increments <= (long)pat.size() && rf.whileSteps <= rf.decrements);
        Run r = scan(t, pat, pi); assert(r.increments - r.decrements == (long)r.finalK && r.increments <= (long)t.size() && r.decrements <= r.increments && r.whileSteps <= r.decrements);
    }
    // 전수: 모든 이진 텍스트(길이 14) × 모든 이진 패턴(길이 1..6)
    { const int n = 14; long maxWhile = 0, maxNaive = 0; std::string t(n, '0'), pat;
      for (int ti = 0; ti < (1 << n); ++ti) { for (int k = 0; k < n; ++k) t[k] = '0' + (ti >> k & 1);
          for (int m = 1; m <= 6; ++m) for (int pi = 0; pi < (1 << m); ++pi) { pat.assign(m, '0'); for (int k = 0; k < m; ++k) pat[k] = '0' + (pi >> k & 1); Run r = scan(t, pat, failure(pat)); assert(r.whileSteps <= n && r.forSteps + r.whileSteps <= 2 * n); maxWhile = std::max(maxWhile, r.whileSteps); maxNaive = std::max(maxNaive, naiveComparisons(t, pat)); } }
      std::cout << "exhaustive (all binary texts of length " << n << " x all binary patterns of length 1..6): max backtracks " << maxWhile << " <= n = " << n << ", while the naive search needed up to " << maxNaive << " comparisons" << std::endl; }
    return 0;
}
// Time Complexity: O(n + m)
// Space Complexity: O(m)
```
## Boyer-Moore가 빠른 이유
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <string>
#include <cassert>

// 보이어-무어는 패턴을 오른쪽 끝부터 비교하고 불일치 시 최대 m 칸을 한 번에 건너뛰므로, 알파벳이 크고 패턴이 길수록
// 텍스트의 글자 대부분을 "읽지도 않는다" (서브리니어).  비교한 글자 수를 세어 나이브와 비교한다
int main() {
    std::mt19937 rng(9);
    std::string t; for (int i = 0; i < 200000; i++) t += (char)('a' + rng() % 26);        // 알파벳 26자 무작위 텍스트
    std::string p = t.substr(100000, 20); p[19] = '#';                                   // 20글자 패턴 (일치 없음)
    long naiveCmp = 0;
    for (size_t i = 0; i + p.size() <= t.size(); i++) for (size_t j = 0; j < p.size(); j++) { naiveCmp++; if (t[i + j] != p[j]) break; }

    int m = p.size(), n = t.size();
    int bc[256]; std::fill(bc, bc + 256, -1); for (int i = 0; i < m; i++) bc[(unsigned char)p[i]] = i;
    long bmCmp = 0;
    for (int s = 0; s <= n - m;) {
        int j = m - 1; while (j >= 0) { bmCmp++; if (p[j] != t[s + j]) break; j--; }
        if (j < 0) s += 1; else s += std::max(1, j - bc[(unsigned char)t[s + j]]);       // 나쁜 문자 규칙
    }
    assert(bmCmp < naiveCmp / 3);
    assert(bmCmp < n / 4);                                      // 텍스트의 1/4 보다 적게 읽는다
    std::cout << "text " << n << ": naive compared " << naiveCmp << ", Boyer-Moore compared " << bmCmp << std::endl;
    return 0;
}
// Time Complexity: 평균 O(n/m)
// Space Complexity: O(σ)
```
## Trie vs HashMap
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <unordered_set>
#include <vector>

// 해시맵은 "정확히 일치" 에는 O(L) 로 빠르지만 접두사 질의를 지원하지 못해 모든 키를 훑어야 한다 (O(N·L)). 트라이는 접두사까지 O(L) 만에 내려가 그 아래 단어만 방문한다 → 자동 완성, 사전식 순회, 최장 접두사 일치에 유리.
// 대신 노드마다 포인터 배열을 가져 메모리를 더 쓴다 — 단어들이 접두사를 많이 공유할 때만 이득.  여기서는 다음을 *숫자로* 확인한다:
//  ① 접두사 질의 비용: 해시맵은 N 이 커지면 그대로 N 개를 훑고, 트라이는 방문 노드 수가 결과 크기에만 비례 → N 이 10 배 되면 비율도 약 10 배.  ② 사전식 순회는 트라이가 정렬된 순서를 주고 해시 집합은 아니다.
//  ③ 메모리: 트라이 노드 수 vs 전체 글자 수 — 무작위 단어는 거의 공유가 없고(노드 ≈ 글자), 접두사가 겹치는 사전은 크게 줄어든다.  ④ 정확한 일치 조회는 둘 다 한 번 (트라이 L 걸음, 해시 L 글자 해시 + 비교).
struct Trie {
    struct Node { int next[26]; bool end; }; std::vector<Node> nd;
    Trie() { nd.emplace_back(); std::fill(nd[0].next, nd[0].next + 26, -1); nd[0].end = false; }
    void insert(const std::string& w) { int n = 0; for (char c : w) { if (nd[n].next[c - 'a'] < 0) { nd.emplace_back(); std::fill(nd.back().next, nd.back().next + 26, -1); nd.back().end = false; nd[n].next[c - 'a'] = (int)nd.size() - 1; } n = nd[n].next[c - 'a']; } nd[n].end = true; }
    long visitedForPrefix(const std::string& p, std::vector<std::string>* out) const {            // 접두사까지 내려간 걸음 + 그 아래에서 방문한 노드 수
        int n = 0; long visited = 0; for (char c : p) { n = nd[n].next[c - 'a']; ++visited; if (n < 0) return visited; }
        std::vector<std::pair<int, std::string>> st = {{n, p}}; while (!st.empty()) { auto cur = st.back(); st.pop_back(); ++visited; if (nd[cur.first].end && out) out->push_back(cur.second); for (int c = 25; c >= 0; --c) if (nd[cur.first].next[c] >= 0) st.push_back({nd[cur.first].next[c], cur.second + (char)('a' + c)}); }
        return visited;
    }
};
int main() {
    std::mt19937 rng(23);
    // ① N 을 키워 가며 접두사 "ab" 질의: 해시맵은 N 개를 훑고 트라이는 결과 크기에 비례
    double ratio[3]; int idx = 0;
    for (int N : {2000, 20000, 200000}) {
        Trie t; std::unordered_set<std::string> h; for (int i = 0; i < N; ++i) { std::string w(6, 'a'); for (char& c : w) c = (char)('a' + rng() % 26); t.insert(w); h.insert(w); }
        long hashScanned = 0, found = 0; for (auto& w : h) { ++hashScanned; found += w.compare(0, 2, "ab") == 0; }
        std::vector<std::string> res; long trieVisited = t.visitedForPrefix("ab", &res); assert((long)res.size() == found && std::is_sorted(res.begin(), res.end()) && trieVisited <= 2 + (long)res.size() * 5);          // 방문 ≤ 결과 수 × 남은 길이 + 접두사 걸음
        ratio[idx++] = (double)hashScanned / trieVisited;
        std::cout << "N=" << N << ": hash scanned " << hashScanned << " keys, trie visited " << trieVisited << " nodes for " << found << " matches\n";
    }
    assert(ratio[2] > 50);                                                                                                           // N = 20 만: 해시맵은 20 만 개를 훑고 트라이는 수백 노드
    // ② 사전식 순회: 트라이는 정렬된 순서, 해시 집합은 순서 없음
    { Trie t; std::unordered_set<std::string> h; std::vector<std::string> words; for (int i = 0; i < 5000; ++i) { std::string w(1 + rng() % 8, 'a'); for (char& c : w) c = (char)('a' + rng() % 5); t.insert(w); h.insert(w); words.push_back(w); }
      std::vector<std::string> all; t.visitedForPrefix("", &all); std::vector<std::string> sorted(h.begin(), h.end()); std::sort(sorted.begin(), sorted.end()); std::vector<std::string> hv(h.begin(), h.end()); assert(all == sorted && !std::is_sorted(hv.begin(), hv.end())); }
    // ③ 메모리: 노드 수 대 글자 수 — 무작위 단어 vs 접두사를 공유하는 사전(알파벳 3 개, 길이 6 의 모든 단어 729 개)
    { Trie random; size_t chars = 0; std::unordered_set<std::string> seen; for (int i = 0; i < 20000; ++i) { std::string w(6, 'a'); for (char& c : w) c = (char)('a' + rng() % 26); if (seen.insert(w).second) { random.insert(w); chars += w.size(); } }
      Trie dense; size_t denseChars = 0; for (int x = 0; x < 729; ++x) { std::string w(6, 'a'); int v = x; for (char& c : w) { c = (char)('a' + v % 3); v /= 3; } dense.insert(w); denseChars += w.size(); }
      double randomRatio = (double)(random.nd.size() - 1) / chars, denseRatio = (double)(dense.nd.size() - 1) / denseChars; assert(dense.nd.size() == 1 + 3 + 9 + 27 + 81 + 243 + 729 && randomRatio > 0.5 && denseRatio < 0.26 && randomRatio > 2 * denseRatio);
      size_t trieBytes = random.nd.size() * sizeof(Trie::Node), hashBytes = 0; for (auto& w : seen) hashBytes += w.size() + 2 * sizeof(void*) + sizeof(std::string); assert(trieBytes > 4 * hashBytes);         // 공유가 적으면 트라이가 몇 배 더 쓴다
      std::cout << "nodes per character: random words " << randomRatio << ", dense 3-letter dictionary " << denseRatio << "; random-word trie used " << (double)trieBytes / hashBytes << "x the memory of the hash set" << std::endl; }
    return 0;
}
// Time Complexity: 트라이 접두사 질의 O(L + 결과 크기), 해시맵 O(N·L)
// Space Complexity: 트라이 O(노드 수 · σ), 해시맵 O(총 글자 수)
```
## Suffix Array vs Suffix Tree
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 같은 문제(부분 문자열 검색)를 푸는 세 가지 표현의 크기를 비교한다.
//  - 접미사 트라이(압축 안 함): 노드 수 = 서로 다른 부분 문자열 수 + 1 = O(n²)
//  - 접미사 트리/자동자(압축): 노드 ≤ 2n = O(n)  (포인터가 많아 상수가 큼)
//  - 접미사 배열: 정수 n 개 = O(n)  (포인터 없음, 캐시 친화적, 검색은 이진 탐색 O(m log n))
long suffixTrieNodes(const std::string& s) { std::set<std::string> subs; for (size_t i = 0; i < s.size(); i++) for (size_t l = 1; i + l <= s.size(); l++) subs.insert(s.substr(i, l)); return subs.size() + 1; }
long samStates(const std::string& s) {
    struct St { int len, link; std::map<char, int> nx; }; std::vector<St> st(1, {0, -1, {}}); int last = 0;
    for (char c : s) {
        int cur = st.size(); st.push_back({st[last].len + 1, -1, {}}); int p = last;
        while (p != -1 && !st[p].nx.count(c)) { st[p].nx[c] = cur; p = st[p].link; }
        if (p == -1) st[cur].link = 0;
        else { int q = st[p].nx[c]; if (st[p].len + 1 == st[q].len) st[cur].link = q; else { int cl = st.size(); st.push_back(st[q]); st[cl].len = st[p].len + 1; while (p != -1 && st[p].nx[c] == q) { st[p].nx[c] = cl; p = st[p].link; } st[q].link = st[cur].link = cl; } }
        last = cur;
    }
    return st.size();
}

int main() {
    std::mt19937 rng(10); std::string s; for (int i = 0; i < 300; i++) s += "abcd"[rng() % 4];
    long trie = suffixTrieNodes(s), sam = samStates(s), sa = s.size();
    assert(sa < sam && sam <= 2 * (long)s.size() && sam * 10 < trie);        // 배열 < 자동자(≤2n) << 트라이(≈n²/2)
    // 검색 결과는 동일: 접미사 배열로 "abc" 의 출현 위치 구하기 == 직접 찾기
    std::vector<int> idx(s.size()); std::iota(idx.begin(), idx.end(), 0);
    std::sort(idx.begin(), idx.end(), [&](int a, int b) { return s.compare(a, std::string::npos, s, b, std::string::npos) < 0; });
    auto lo = std::lower_bound(idx.begin(), idx.end(), std::string("abc"), [&](int i, const std::string& x) { return s.compare(i, x.size(), x) < 0; });
    auto hi = std::upper_bound(idx.begin(), idx.end(), std::string("abc"), [&](const std::string& x, int i) { return s.compare(i, x.size(), x) > 0; });
    long viaSA = hi - lo, direct = 0; for (size_t p = s.find("abc"); p != std::string::npos; p = s.find("abc", p + 1)) direct++;
    assert(viaSA == direct);
    std::cout << "n=300: suffix trie nodes=" << trie << ", suffix automaton states=" << sam << ", suffix array entries=" << sa << std::endl;
    return 0;
}
// Time Complexity: 접미사 배열 검색 O(m log n), 자동자 검색 O(m)
// Space Complexity: 트라이 O(n²), 자동자 O(n), 배열 O(n)
```
