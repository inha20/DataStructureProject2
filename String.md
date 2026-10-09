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
#include <algorithm>
#include <cassert>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 사전식 비교: 처음 다른 문자의 값(부호 없는 바이트)으로 결정하고, 모두 같으면 짧은 쪽이 작다
// 검증: ① 손으로 고른 경우(접두사·대소문자·UTF-8 바이트·내장 NUL)  ② 알파벳 {0x00, 0x7F, 0x80, 0xFF} 위의 길이 ≤ 4 문자열 *전부* (341 개)의 모든 쌍을
//        std::string::compare 와 "바이트를 int 벡터로 바꿔 벡터끼리 비교" 라는 독립 오라클로 대조  ③ 전순서의 성질(반사·반대칭·추이)과 정렬 결과
//        ④ char 를 부호 있는 채로 비교하는 흔한 버그판은 상위 바이트에서 오라클과 달라진다는 음성 대조군
int compare(const std::string& a, const std::string& b) {
    size_t n = std::min(a.size(), b.size());
    for (size_t i = 0; i < n; i++) {
        unsigned char x = a[i], y = b[i];                // 반드시 unsigned: char 가 음수일 수 있다
        if (x != y) return x < y ? -1 : 1;
    }
    return a.size() == b.size() ? 0 : (a.size() < b.size() ? -1 : 1);
}
int compareSignedBug(const std::string& a, const std::string& b) {          // 흔한 실수: char 를 그대로 비교
    size_t n = std::min(a.size(), b.size());
    for (size_t i = 0; i < n; i++) if (a[i] != b[i]) return a[i] < b[i] ? -1 : 1;
    return a.size() == b.size() ? 0 : (a.size() < b.size() ? -1 : 1);
}
int compareIgnoreCase(const std::string& a, const std::string& b) {         // ASCII 대소문자 무시 (A-Z 만 소문자로)
    auto low = [](unsigned char c) { return c >= 'A' && c <= 'Z' ? c + 32 : c; };
    size_t n = std::min(a.size(), b.size());
    for (size_t i = 0; i < n; i++) { int x = low(a[i]), y = low(b[i]); if (x != y) return x < y ? -1 : 1; }
    return a.size() == b.size() ? 0 : (a.size() < b.size() ? -1 : 1);
}
int sign(int v) { return (v > 0) - (v < 0); }
int oracle(const std::string& a, const std::string& b) {                    // 독립 오라클: 바이트를 0..255 정수 벡터로 바꿔 operator< 로 비교
    std::vector<int> x(a.begin(), a.end()), y(b.begin(), b.end());
    for (int& v : x) v &= 0xFF;
    for (int& v : y) v &= 0xFF;
    return x < y ? -1 : y < x ? 1 : 0;
}

int main() {
    assert(compare("apple", "apple") == 0);
    assert(compare("apple", "apricot") < 0);             // 'p' < 'r'
    assert(compare("app", "apple") < 0);                 // 접두사는 더 작다
    assert(compare("Zebra", "apple") < 0);               // 대문자(65~90) < 소문자(97~122)
    assert(compare("é", "z") > 0);                       // UTF-8 바이트 0xC3 > 'z' (바이트 기준 비교)
    assert(compareSignedBug("é", "z") < 0);              // 부호 있는 비교는 0xC3 을 음수로 보아 순서가 뒤집힌다
    assert(compare("", "") == 0 && compare("", "a") < 0 && compare("a", "") > 0);
    assert(compare(std::string("a\0b", 3), std::string("a\0c", 3)) < 0);     // NUL 이 들어 있어도 끝까지 비교 (strcmp 와 다른 점)
    assert(compare(std::string("a\0", 2), "a") > 0);
    assert(std::strcmp("a\0b", "a\0c") == 0);
    for (auto p : {std::pair<const char*, const char*>{"a", "b"}, {"abc", "abd"}, {"", "x"}, {"same", "same"}, {"\xC3\xA9", "z"}})
        assert(sign(compare(p.first, p.second)) == sign(std::strcmp(p.first, p.second)));       // NUL 이 없으면 strcmp(부호 없는 바이트 기준) 와 일치
    assert(compareIgnoreCase("Apple", "aPPLE") == 0 && compareIgnoreCase("apple", "BANANA") < 0 && compareIgnoreCase("Z", "a") > 0 && compareIgnoreCase("a", "A") == 0);

    // ② 경계 바이트 알파벳 위의 모든 문자열 쌍
    const char alpha[] = {'\x00', '\x7F', '\x80', '\xFF'}; std::vector<std::string> all{std::string()};
    for (size_t i = 0; i < all.size(); ++i) if (all[i].size() < 4) for (char c : alpha) all.push_back(all[i] + c);
    assert(all.size() == 341);                           // 1 + 4 + 16 + 64 + 256
    long pairs = 0, bugDiffers = 0, eq = 0;
    for (const std::string& a : all) for (const std::string& b : all) {
        int c = compare(a, b); assert(c == oracle(a, b) && sign(a.compare(b)) == c);
        assert(compare(b, a) == -c);                     // 반대칭
        if (compareSignedBug(a, b) != c) ++bugDiffers;
        eq += c == 0; ++pairs;
    }
    assert(pairs == 341L * 341 && eq == 341 && bugDiffers > 1000);
    // ③ 무작위 문자열: 정렬 결과가 같고, 추이성
    std::mt19937 rng(5); std::vector<std::string> v;
    for (int i = 0; i < 2000; ++i) { std::string s(rng() % 8, 'a'); for (char& ch : s) ch = (char)(rng() % 4 == 0 ? 0x80 + rng() % 128 : 'a' + rng() % 3); v.push_back(s); }
    std::vector<std::string> byCompare = v, byStd = v;
    std::sort(byCompare.begin(), byCompare.end(), [](const std::string& a, const std::string& b) { return compare(a, b) < 0; });
    std::sort(byStd.begin(), byStd.end());
    assert(byCompare == byStd);
    for (int i = 0; i < 20000; ++i) { const std::string &a = v[rng() % v.size()], &b = v[rng() % v.size()], &c = v[rng() % v.size()]; if (compare(a, b) <= 0 && compare(b, c) <= 0) assert(compare(a, c) <= 0); }
    std::cout << "Compare: " << pairs << " boundary-byte pairs matched std::string::compare and the int-vector oracle; the signed-char bug differed on " << bugDiffers << " of them" << std::endl;
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
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

// UTF-8: 1~4바이트 가변, ASCII 호환, 바이트 순서 문제 없음.   UTF-16: 2바이트 단위, U+10000 이상은 서로게이트 쌍(4바이트).
// 같은 글자라도 크기가 다르다: 영어는 UTF-8 이 작고, 한글은 UTF-16(2B)이 UTF-8(3B)보다 작다
// 검증: ① 알려진 값(€ = E2 82 AC, 😀 = F0 9F 98 80 = D83D DE00)  ② 유니코드 스칼라 값 1 112 064 개 *전부* 의 UTF-8/UTF-16 왕복과 상호 변환, 크기 공식(1/2/3/4 바이트 개수 128·1 920·61 440·1 048 576)
//        ③ 정렬 순서: UTF-8 바이트 순서는 코드 포인트 순서와 같지만 UTF-16 코드 단위 순서는 U+E000..U+FFFF 와 U+10000 이상에서 뒤집힌다  ④ 잘못된 UTF-16(짝 없는 서로게이트)은 거부
std::vector<uint16_t> utf16Encode(uint32_t cp) {
    if (cp < 0x10000) return {(uint16_t)cp};
    cp -= 0x10000;
    return {(uint16_t)(0xD800 + (cp >> 10)), (uint16_t)(0xDC00 + (cp & 0x3FF))};    // 상위/하위 서로게이트
}
bool utf16Decode(const std::vector<uint16_t>& u, size_t& pos, uint32_t& cp) {         // pos 에서 한 글자를 읽는다. 짝 없는 서로게이트는 false
    uint16_t a = u[pos];
    if (a < 0xD800 || a > 0xDFFF) { cp = a; pos += 1; return true; }
    if (a >= 0xDC00 || pos + 1 >= u.size() || u[pos + 1] < 0xDC00 || u[pos + 1] > 0xDFFF) return false;
    cp = 0x10000 + (((uint32_t)a - 0xD800) << 10) + (u[pos + 1] - 0xDC00); pos += 2; return true;
}
size_t utf8Size(uint32_t cp) { return cp < 0x80 ? 1 : cp < 0x800 ? 2 : cp < 0x10000 ? 3 : 4; }
std::string utf8Encode(uint32_t cp) {
    std::string s;
    if (cp < 0x80) s += (char)cp;
    else if (cp < 0x800) { s += (char)(0xC0 | cp >> 6); s += (char)(0x80 | (cp & 0x3F)); }
    else if (cp < 0x10000) { s += (char)(0xE0 | cp >> 12); s += (char)(0x80 | ((cp >> 6) & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    else { s += (char)(0xF0 | cp >> 18); s += (char)(0x80 | ((cp >> 12) & 0x3F)); s += (char)(0x80 | ((cp >> 6) & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    return s;
}
uint32_t utf8Decode(const std::string& s, size_t& i) {                                // 올바른 UTF-8 이라고 가정하고 한 글자를 읽는다
    unsigned char c = s[i]; int len = c < 0x80 ? 1 : c < 0xE0 ? 2 : c < 0xF0 ? 3 : 4;
    uint32_t cp = len == 1 ? c : len == 2 ? c & 0x1F : len == 3 ? c & 0x0F : c & 0x07;
    for (int k = 1; k < len; k++) cp = cp << 6 | (s[i + k] & 0x3F);
    i += len; return cp;
}
bool isScalar(uint32_t cp) { return cp <= 0x10FFFF && !(cp >= 0xD800 && cp <= 0xDFFF); }

int main() {
    assert(utf8Size('A') == 1 && utf16Encode('A').size() * 2 == 2);              // 영어: UTF-8 이 작다
    assert(utf8Size(0xD55C) == 3 && utf16Encode(0xD55C).size() * 2 == 2);        // 한글: UTF-16 이 작다
    assert(utf8Size(0x1F600) == 4 && utf16Encode(0x1F600).size() * 2 == 4);      // 이모지: 같다
    assert(utf8Encode(0x20AC) == "\xE2\x82\xAC" && utf8Encode(0x1F600) == "\xF0\x9F\x98\x80" && utf8Encode(0xD55C) == "\xED\x95\x9C");
    auto pair = utf16Encode(0x1F600);
    assert(pair[0] == 0xD83D && pair[1] == 0xDE00);                               // 😀 의 서로게이트 쌍
    assert(utf16Encode(0x10000)[0] == 0xD800 && utf16Encode(0x10000)[1] == 0xDC00 && utf16Encode(0x10FFFF)[0] == 0xDBFF && utf16Encode(0x10FFFF)[1] == 0xDFFF);

    // ② 모든 스칼라 값 왕복
    long count[5] = {0, 0, 0, 0, 0}, units16[3] = {0, 0, 0}; uint32_t prev = 0; std::string prevBytes; bool first = true;
    for (uint32_t cp = 0; cp <= 0x10FFFF; ++cp) {
        if (!isScalar(cp)) continue;
        std::string u8 = utf8Encode(cp); assert(u8.size() == utf8Size(cp)); ++count[u8.size()];
        size_t i = 0; assert(utf8Decode(u8, i) == cp && i == u8.size());          // UTF-8 왕복
        std::vector<uint16_t> u16 = utf16Encode(cp); ++units16[u16.size()];
        size_t pos = 0; uint32_t back = 0; assert(utf16Decode(u16, pos, back) && back == cp && pos == u16.size());     // UTF-16 왕복
        assert((u16.size() == 2) == (cp >= 0x10000));
        if (!first) assert(u8 > prevBytes);                                   // UTF-8 의 바이트 사전식 순서 = 코드 포인트 순서 (std::string 비교는 부호 없는 바이트)
        prev = cp; prevBytes = u8; first = false;
    }
    (void)prev;
    assert(count[1] == 128 && count[2] == 1920 && count[3] == 61440 && count[4] == 1048576);
    assert(count[1] + count[2] + count[3] + count[4] == 1112064 && units16[1] == 63488 && units16[2] == 1048576);
    // 한글 완성형 음절 11 172 자: UTF-8 은 3 바이트, UTF-16 은 2 바이트 -> UTF-16 이 1/3 작다
    long hangul8 = 0, hangul16 = 0; for (uint32_t cp = 0xAC00; cp <= 0xD7A3; ++cp) { hangul8 += (long)utf8Size(cp); hangul16 += 2 * (long)utf16Encode(cp).size(); }
    assert(hangul8 == 3L * 11172 && hangul16 == 2L * 11172);
    // 혼합 문자열 한 줄: 코드 포인트 수, UTF-16 단위 수 = 코드 포인트 수 + 보충 평면 글자 수
    std::string text = utf8Encode('H') + utf8Encode('i') + utf8Encode(0xD55C) + utf8Encode(0xAE00) + utf8Encode(0x1F600) + utf8Encode(0x20AC); size_t cps = 0, supp = 0;
    std::vector<uint16_t> all16; for (size_t i = 0; i < text.size();) { uint32_t cp = utf8Decode(text, i); ++cps; supp += cp >= 0x10000; for (uint16_t w : utf16Encode(cp)) all16.push_back(w); }
    assert(cps == 6 && supp == 1 && all16.size() == cps + supp && text.size() == 1 + 1 + 3 + 3 + 4 + 3);
    size_t pos = 0, decoded = 0; while (pos < all16.size()) { uint32_t cp; assert(utf16Decode(all16, pos, cp)); ++decoded; } assert(decoded == cps);
    // ③ 정렬 순서가 뒤집히는 쌍: U+FF5E 와 U+10000 은 코드 포인트로는 FF5E < 10000 이지만 UTF-16 코드 단위로는 D800 < FF5E 라서 반대다
    assert(0xFF5E < 0x10000 && utf8Encode(0xFF5E) < utf8Encode(0x10000));
    assert(utf16Encode(0x10000)[0] < utf16Encode(0xFF5E)[0]);
    // ④ 짝 없는 서로게이트는 UTF-16 으로 해석할 수 없다
    for (auto bad : {std::vector<uint16_t>{0xD800}, std::vector<uint16_t>{0xDC00}, std::vector<uint16_t>{0xD800, 0x0041}, std::vector<uint16_t>{0xDC00, 0xD800}}) { size_t p = 0; uint32_t cp; assert(!utf16Decode(bad, p, cp)); }
    std::cout << "UTF-8/16: all " << count[1] + count[2] + count[3] + count[4] << " scalar values round-tripped; U+1F600 = " << std::hex << pair[0] << " " << pair[1] << std::dec << ", Hangul syllables take " << hangul8 << " bytes in UTF-8 vs " << hangul16 << " in UTF-16" << std::endl;
    return 0;
}
// Time Complexity: O(1) (글자당)
// Space Complexity: O(1)
```
## UTF8Validate()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// UTF-8 검증: 선행 바이트가 알려 주는 길이만큼 연속 바이트(10xxxxxx)가 와야 하고,
// (1) 과잉 부호화(overlong)  (2) 서로게이트 영역 U+D800~DFFF  (3) U+10FFFF 초과  는 모두 무효다 (보안 취약점의 단골 원인)
// 검증: ① 알려진 무효 입력  ② 길이 1~3 의 바이트열 *전부* (256 + 65 536 + 16 777 216 개)를 독립 오라클(유니코드 표 3-7 의 "잘 형성된 바이트 범위" 표)과 대조하고,
//        유효한 개수가 점화식 c(n) = 128·c(n-1) + 1 920·c(n-2) + 61 440·c(n-3) + 1 048 576·c(n-4) 와 정확히 일치  ③ 경계 바이트 27 종의 길이 4 문자열 전부 + 무작위 긴 문자열
//        ④ 유효한 문자열은 "디코딩 후 다시 인코딩하면 원본" (정규형이 유일), 모든 코드 포인트의 인코딩은 유효하고 서로게이트는 무효
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
bool inR(unsigned char c, int lo, int hi) { return c >= lo && c <= hi; }
bool validTable(const std::string& s) {                          // 오라클: 유니코드 표 3-7 (각 바이트 위치별 허용 범위만 쓰고 코드 포인트 산술은 쓰지 않는다)
    size_t i = 0, n = s.size();
    auto B = [&](size_t k) { return (unsigned char)s[k]; };
    while (i < n) {
        unsigned char c = B(i);
        if (c <= 0x7F) { i += 1; }
        else if (inR(c, 0xC2, 0xDF)) { if (i + 1 < n && inR(B(i + 1), 0x80, 0xBF)) i += 2; else return false; }
        else if (c == 0xE0 || inR(c, 0xE1, 0xEC) || c == 0xED || inR(c, 0xEE, 0xEF)) {
            int lo = c == 0xE0 ? 0xA0 : 0x80, hi = c == 0xED ? 0x9F : 0xBF;
            if (i + 2 < n && inR(B(i + 1), lo, hi) && inR(B(i + 2), 0x80, 0xBF)) i += 3; else return false;
        } else if (c == 0xF0 || inR(c, 0xF1, 0xF3) || c == 0xF4) {
            int lo = c == 0xF0 ? 0x90 : 0x80, hi = c == 0xF4 ? 0x8F : 0xBF;
            if (i + 3 < n && inR(B(i + 1), lo, hi) && inR(B(i + 2), 0x80, 0xBF) && inR(B(i + 3), 0x80, 0xBF)) i += 4; else return false;
        } else return false;                                     // 80..C1, F5..FF
    }
    return true;
}
std::string encode(uint32_t cp) {
    std::string s;
    if (cp < 0x80) s += (char)cp;
    else if (cp < 0x800) { s += (char)(0xC0 | cp >> 6); s += (char)(0x80 | (cp & 0x3F)); }
    else if (cp < 0x10000) { s += (char)(0xE0 | cp >> 12); s += (char)(0x80 | ((cp >> 6) & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    else { s += (char)(0xF0 | cp >> 18); s += (char)(0x80 | ((cp >> 12) & 0x3F)); s += (char)(0x80 | ((cp >> 6) & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    return s;
}
std::string reencode(const std::string& s) {                     // 유효한 문자열을 코드 포인트로 읽어 다시 인코딩
    std::string out;
    for (size_t i = 0; i < s.size();) {
        unsigned char c = s[i]; int len = c < 0x80 ? 1 : c < 0xE0 ? 2 : c < 0xF0 ? 3 : 4; uint32_t cp = len == 1 ? c : len == 2 ? c & 0x1F : len == 3 ? c & 0x0F : c & 0x07;
        for (int k = 1; k < len; k++) cp = cp << 6 | (s[i + k] & 0x3F);
        out += encode(cp); i += len;
    }
    return out;
}

int main() {
    assert(validUtf8("hello") && validUtf8("한글😀") && validUtf8(""));
    assert(!validUtf8(std::string("\xC0\x80", 2)));              // overlong NUL
    assert(!validUtf8(std::string("\xED\xA0\x80", 3)));          // U+D800 서로게이트
    assert(!validUtf8(std::string("\xF4\x90\x80\x80", 4)));      // U+110000 범위 초과
    assert(!validUtf8(std::string("\xE2\x82", 2)));              // 잘린 시퀀스
    assert(!validUtf8(std::string("\x80", 1)));                  // 선행 위치의 연속 바이트
    assert(!validUtf8(std::string("\xE0\x80\x80", 3)) && !validUtf8(std::string("\xF0\x80\x80\x80", 4)) && !validUtf8(std::string("\xC1\xBF", 2)));   // 3·4·2 바이트 과잉 부호화
    assert(validUtf8(std::string("\x00", 1)) && validUtf8(std::string("\xF4\x8F\xBF\xBF", 4)) && validUtf8(std::string("\xED\x9F\xBF", 3)) && validUtf8(std::string("\xEE\x80\x80", 3)));   // 경계의 유효값

    // ② 길이 1~3 전수
    long valid[4] = {1, 0, 0, 0};                                // valid[0] = 빈 문자열 1 개
    std::string s1(1, 0), s2(2, 0), s3(3, 0);
    for (int a = 0; a < 256; ++a) { s1[0] = (char)a; bool v = validUtf8(s1); assert(v == validTable(s1)); valid[1] += v; }
    for (int a = 0; a < 256; ++a) for (int b = 0; b < 256; ++b) { s2[0] = (char)a; s2[1] = (char)b; bool v = validUtf8(s2); assert(v == validTable(s2)); valid[2] += v; }
    for (int a = 0; a < 256; ++a) for (int b = 0; b < 256; ++b) for (int c = 0; c < 256; ++c) {
        s3[0] = (char)a; s3[1] = (char)b; s3[2] = (char)c; bool v = validUtf8(s3); assert(v == validTable(s3)); valid[3] += v;
        if (v && (a | b | c) != 0 && ((a * 7 + b * 13 + c) & 63) == 0) assert(reencode(s3) == s3);      // 표본: 유효하면 정규형 (3 바이트 전수 대신 1/64 표본)
    }
    long rec[5] = {1, 128, 0, 0, 0};                             // c(0) = 1, c(1) = 128
    rec[2] = 128 * rec[1] + 1920 * rec[0]; rec[3] = 128 * rec[2] + 1920 * rec[1] + 61440 * rec[0];
    assert(valid[1] == rec[1] && valid[2] == rec[2] && valid[3] == rec[3] && rec[2] == 18304 && rec[3] == 2650112);

    // ③ 경계 바이트 27 종의 길이 4 문자열 전부 (531 441 개)
    const int edge[] = {0x00, 0x41, 0x7F, 0x80, 0x8F, 0x90, 0x9F, 0xA0, 0xBF, 0xC0, 0xC1, 0xC2, 0xDF, 0xE0, 0xE1, 0xEC, 0xED, 0xEE, 0xEF, 0xF0, 0xF1, 0xF3, 0xF4, 0xF5, 0xF7, 0xF8, 0xFF};
    std::string s4(4, 0); long valid4 = 0, total4 = 0;
    for (int a : edge) for (int b : edge) for (int c : edge) for (int d : edge) {
        s4[0] = (char)a; s4[1] = (char)b; s4[2] = (char)c; s4[3] = (char)d; bool v = validUtf8(s4); assert(v == validTable(s4)); valid4 += v; ++total4;
        if (v) assert(reencode(s4) == s4);
    }
    assert(total4 == 531441 && valid4 == 2277);                // 2277 은 다른 구현(파이썬의 엄격한 UTF-8 디코더)으로 같은 531 441 개를 돌려 얻은 값
    // ④ 모든 코드 포인트: 서로게이트만 무효, 인코딩은 항상 정규형
    for (uint32_t cp = 0; cp <= 0x10FFFF; ++cp) { std::string e = encode(cp); bool ok = !(cp >= 0xD800 && cp <= 0xDFFF); assert(validUtf8(e) == ok && validTable(e) == ok); if (ok) assert(reencode(e) == e); }
    std::mt19937 rng(11); long randomValid = 0;                  // 유효한 글자를 이어 붙인 긴 문자열 / 한 바이트만 바꾼 변형
    for (int it = 0; it < 3000; ++it) {
        std::string s; int n = 1 + (int)(rng() % 12);
        while (n--) { uint32_t cp; do cp = (uint32_t)(rng() % 3 == 0 ? rng() % 0x110000 : rng() % 0x3000); while (cp >= 0xD800 && cp <= 0xDFFF); s += encode(cp); }
        assert(validUtf8(s) && validTable(s)); ++randomValid;
        std::string m = s; m[rng() % m.size()] = (char)(rng() % 256); assert(validUtf8(m) == validTable(m));
        if (validUtf8(m)) assert(reencode(m) == m);
    }
    std::cout << "UTF8Validate: all " << valid[1] + valid[2] + valid[3] << "+ valid byte strings of length 1..3 counted (" << valid[3] << " of length 3) and matched the range-table oracle; " << total4 << " boundary strings of length 4 agreed" << std::endl;
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 갭 버퍼: 커서 위치에 "빈 구간(gap)"을 두고 그 앞뒤에 텍스트를 저장한다. (Emacs 의 편집 버퍼)
// 커서 근처 삽입·삭제는 O(1), 커서를 옮기면 이동 거리만큼 문자를 갭 반대편으로 옮긴다
// 검증: ① 손으로 짠 편집 시나리오  ② 무작위 편집 30 000 회(문자·문자열 삽입, 백스페이스, 앞으로 지우기, 커서 이동, 용량 0~8 에서 시작)를 std::string 모델과 매 단계 대조
//        ③ 비용 모델: 이동 비용 = 커서 이동 거리의 합과 *정확히* 같고, 제자리 타이핑 5 000 자는 문자를 하나도 옮기지 않으며, 용량은 배증해서 재할당이 O(log n) 번
class GapBuffer {
    std::vector<char> buf; size_t gs, ge;                       // 갭 = [gs, ge)
    size_t moved_ = 0, grows_ = 0;                               // 커서 이동으로 옮긴 문자 수 / 용량 확장 횟수 (분석용)
    void ensure(size_t extra) {
        if (ge - gs >= extra) return;
        size_t oldCap = buf.size(), newCap = std::max(oldCap * 2, oldCap + extra);
        buf.resize(newCap); ++grows_;
        size_t tail = oldCap - ge;
        for (size_t i = 0; i < tail; i++) buf[newCap - 1 - i] = buf[oldCap - 1 - i];     // 뒤쪽 텍스트를 끝으로 밀기
        ge = newCap - tail;
    }
public:
    explicit GapBuffer(size_t cap = 8) : buf(cap), gs(0), ge(cap) {}
    size_t size() const { return buf.size() - (ge - gs); }
    size_t capacity() const { return buf.size(); }
    size_t cursor() const { return gs; }
    size_t moved() const { return moved_; }
    size_t grows() const { return grows_; }
    void move(size_t pos) {                                      // 커서를 pos 로 이동 (갭도 함께 이동)
        assert(pos <= size());
        while (gs > pos) { buf[--ge] = buf[--gs]; ++moved_; }
        while (gs < pos) { buf[gs++] = buf[ge++]; ++moved_; }
    }
    void insert(char c) { ensure(1); buf[gs++] = c; }
    void insert(const std::string& s) { ensure(s.size()); for (char c : s) buf[gs++] = c; }
    void erase() { if (gs > 0) gs--; }                           // 백스페이스: 갭을 넓히기만 하면 된다
    void eraseForward() { if (ge < buf.size()) ge++; }           // Delete 키: 갭의 오른쪽 끝을 넓힌다
    char at(size_t i) const { return i < gs ? buf[i] : buf[i + (ge - gs)]; }
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
    g.move(g.size()); g.erase(); g.erase(); assert(g.str() == ">Hello wor");
    g.move(0); g.eraseForward(); assert(g.str() == "Hello wor" && g.at(0) == 'H' && g.at(8) == 'r');
    GapBuffer e(0); assert(e.size() == 0 && e.str().empty()); e.erase(); e.eraseForward(); e.insert("ab"); e.move(1); e.insert('X'); assert(e.str() == "aXb");   // 경계: 용량 0, 빈 버퍼에서 지우기

    // ② 모델 대조
    std::mt19937 rng(2024); long checks = 0, grownTotal = 0;
    for (size_t cap0 : {0u, 1u, 2u, 4u, 8u}) {
        GapBuffer b(cap0); std::string model; size_t cur = 0; size_t expectMoved = 0;
        for (int step = 0; step < 6000; ++step) {
            int op = (int)(rng() % 10);
            if (op < 4) { char c = (char)('a' + rng() % 26); b.insert(c); model.insert(model.begin() + cur, c); ++cur; }
            else if (op == 4) { std::string s; for (int k = 0, n = (int)(rng() % 12); k < n; ++k) s += (char)('A' + rng() % 26); b.insert(s); model.insert(cur, s); cur += s.size(); }
            else if (op == 5) { b.erase(); if (cur > 0) { model.erase(cur - 1, 1); --cur; } }
            else if (op == 6) { b.eraseForward(); if (cur < model.size()) model.erase(cur, 1); }
            else { size_t to = rng() % (model.size() + 1); expectMoved += cur > to ? cur - to : to - cur; b.move(to); cur = to; }
            assert(b.size() == model.size() && b.cursor() == cur && b.str() == model && b.capacity() >= b.size());
            if (!model.empty()) { size_t i = rng() % model.size(); assert(b.at(i) == model[i]); }
            ++checks;
        }
        assert(b.moved() == expectMoved);                        // ③ 이동 비용 = 이동 거리의 합
        grownTotal += (long)b.grows();
    }
    // 제자리 타이핑은 옮기는 문자가 없고, 재할당은 배증이라 log 번
    GapBuffer t(4); for (int i = 0; i < 5000; ++i) t.insert((char)('a' + i % 26));
    assert(t.moved() == 0 && t.size() == 5000 && t.grows() <= 11 && t.grows() >= 10);          // 4 -> 8 -> ... -> 8192: 11 번
    // 커서 근처 편집은 멀리 있는 텍스트를 건드리지 않는다: 가운데에서 1 000 번 지우고 쓰기 -> 옮긴 문자 수 = 처음 가운데로 간 거리뿐
    t.move(2500); size_t before = t.moved(); for (int i = 0; i < 1000; ++i) { t.insert('x'); t.erase(); } assert(t.moved() == before && t.size() == 5000);
    std::cout << "GapBuffer: " << checks << " random edits matched std::string; typing 5000 chars moved " << 0 << " characters in " << t.grows() << " growths" << std::endl;
    (void)grownTotal;
    return 0;
}
// Time Complexity: 커서 근처 삽입/삭제 O(1), 이동 O(거리)
// Space Complexity: O(n + gap)
```
## PieceTable()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 피스 테이블(VS Code, Word): 원본 파일 버퍼(읽기 전용)와 추가 버퍼(append-only)를 두고,
// 문서는 "어느 버퍼의 어디부터 몇 글자"인 조각(piece)들의 목록으로 표현한다. 편집은 조각 목록만 바꾸므로 텍스트 복사가 없고 undo 가 쉽다
// 이 구현의 undo 는 편집 전의 조각 목록(글자가 아니라 (버퍼, 시작, 길이) 세 수의 배열)을 보관한다.  이어서 타이핑하면 직전 추가 조각을 늘려 조각 수가 늘지 않는다
// 검증: ① 손으로 짠 시나리오  ② 무작위 편집 8 000 회(삽입·삭제·undo·redo, 40 개 문서)를 std::string 모델(상태 스택)과 매 단계 대조하고 불변식 확인:
//        빈 조각 없음, 모든 조각이 버퍼 범위 안, 원본 버퍼 불변, 추가 버퍼는 길이가 줄지 않음, 조각 수 ≤ 1 + 2·삽입 + 삭제  ③ 이어 타이핑 5 000 자 -> 조각 2 개
struct Piece { int buf; size_t start, len; };               // buf 0 = original, 1 = added
class PieceTable {
    std::string orig, added, origCopy;
    std::vector<Piece> pieces;
    std::vector<std::vector<Piece>> undoS, redoS;
    void snapshot() { undoS.push_back(pieces); redoS.clear(); }
public:
    explicit PieceTable(const std::string& text) : orig(text), origCopy(text) { if (!text.empty()) pieces.push_back({0, 0, text.size()}); }
    size_t size() const { size_t n = 0; for (auto& p : pieces) n += p.len; return n; }
    void insert(size_t pos, const std::string& text) {
        assert(pos <= size());
        if (text.empty()) return;
        snapshot();
        size_t start = added.size(); added += text;
        size_t off = 0;
        for (size_t i = 0; i <= pieces.size(); i++) {
            if (i == pieces.size()) { pieces.push_back({1, start, text.size()}); return; }
            if (pos <= off + pieces[i].len) {
                Piece p = pieces[i]; size_t inner = pos - off;
                if (inner == p.len && p.buf == 1 && p.start + p.len == start) { pieces[i].len += text.size(); return; }   // 이어 타이핑: 추가 버퍼 끝에서 이어지는 조각
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
        size_t sz = size();
        if (pos >= sz || n == 0) return;
        snapshot();
        std::vector<Piece> out; size_t off = 0, end = std::min(pos + n, sz);
        for (auto p : pieces) {
            size_t a = off, b = off + p.len; off = b;
            if (b <= pos || a >= end) { out.push_back(p); continue; }
            if (a < pos) out.push_back({p.buf, p.start, pos - a});             // 앞 조각 남김
            if (b > end) out.push_back({p.buf, p.start + (end - a), b - end}); // 뒤 조각 남김
        }
        pieces.swap(out);
    }
    bool undo() { if (undoS.empty()) return false; redoS.push_back(pieces); pieces = undoS.back(); undoS.pop_back(); return true; }
    bool redo() { if (redoS.empty()) return false; undoS.push_back(pieces); pieces = redoS.back(); redoS.pop_back(); return true; }
    std::string text() const {
        std::string r;
        for (auto& p : pieces) r += (p.buf ? added : orig).substr(p.start, p.len);
        return r;
    }
    size_t pieceCount() const { return pieces.size(); }
    size_t addedSize() const { return added.size(); }
    bool consistent() const {                                  // 불변식: 빈 조각 없음, 범위 안, 원본 불변
        if (orig != origCopy) return false;
        for (auto& p : pieces) if (p.len == 0 || p.start + p.len > (p.buf ? added : orig).size()) return false;
        return true;
    }
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
    assert(t.undo() && t.text() == "Hello world!" && t.undo() && t.text() == "Hello, world!" && t.redo() && t.text() == "Hello world!");
    t.insert(0, "X"); assert(!t.redo());                                // 새 편집은 redo 기록을 지운다
    PieceTable empty(""); assert(empty.size() == 0 && empty.text().empty() && !empty.undo() && !empty.redo());
    empty.insert(0, "abc"); empty.erase(1, 100); assert(empty.text() == "a" && empty.pieceCount() == 1);       // 경계: 빈 문서에서 시작, 길이를 넘는 삭제
    empty.erase(5, 1); empty.erase(0, 0); empty.insert(0, ""); assert(empty.text() == "a");                      // 범위 밖/빈 편집은 무시

    // ② 모델 대조 (모델은 문자열 상태 스택)
    std::mt19937 rng(99); long ops = 0, undos = 0, redos = 0;
    for (int doc = 0; doc < 40; ++doc) {
        std::string init; for (int i = 0, n = (int)(rng() % 30); i < n; ++i) init += (char)('a' + rng() % 26);
        PieceTable pt(init); std::string cur = init; std::vector<std::string> undoM, redoM; size_t inserts = 0, erases = 0, prevAdded = 0;
        for (int step = 0; step < 200; ++step) {
            int op = (int)(rng() % 10);
            if (op < 4) { size_t pos = rng() % (cur.size() + 1); std::string s; for (int k = 0, n = 1 + (int)(rng() % 5); k < n; ++k) s += (char)('A' + rng() % 26); pt.insert(pos, s); undoM.push_back(cur); redoM.clear(); cur.insert(pos, s); ++inserts; }
            else if (op < 7) { size_t pos = rng() % (cur.size() + 2), n = rng() % 8; pt.erase(pos, n); if (pos < cur.size() && n > 0) { undoM.push_back(cur); redoM.clear(); cur.erase(pos, n); ++erases; } }
            else if (op < 9) { bool r = pt.undo(); assert(r == !undoM.empty()); if (r) { redoM.push_back(cur); cur = undoM.back(); undoM.pop_back(); ++undos; } }
            else { bool r = pt.redo(); assert(r == !redoM.empty()); if (r) { undoM.push_back(cur); cur = redoM.back(); redoM.pop_back(); ++redos; } }
            assert(pt.text() == cur && pt.size() == cur.size() && pt.consistent() && pt.addedSize() >= prevAdded && pt.pieceCount() <= 1 + 2 * inserts + erases);
            prevAdded = pt.addedSize(); ++ops;
        }
    }
    assert(ops == 8000 && undos > 400 && redos > 100);
    // ③ 이어 타이핑: 가운데에 ", dear" 를 한 글자씩 -> 조각 3 개 (원본 앞, 추가, 원본 뒤). 맨 끝에 5 000 자를 한 글자씩 -> 조각 2 개
    PieceTable typing("Hello world"); std::string typed = ", dear"; for (size_t i = 0; i < typed.size(); ++i) typing.insert(5 + i, std::string(1, typed[i]));
    assert(typing.text() == "Hello, dear world" && typing.pieceCount() == 3);
    PieceTable tail("start"); for (int i = 0; i < 5000; ++i) tail.insert(5 + i, std::string(1, (char)('a' + i % 26)));
    assert(tail.size() == 5005 && tail.pieceCount() == 2 && tail.addedSize() == 5000);
    std::cout << "PieceTable: " << ops << " random edits matched the string model (" << undos << " undos, " << redos << " redos); typing 5000 characters kept " << tail.pieceCount() << " pieces" << std::endl;
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// 아호-코라식: 여러 패턴을 트라이로 합치고 KMP 의 실패 함수를 트라이 전체로 확장(실패 링크)해,
// 텍스트를 한 번만 훑어 모든 패턴의 모든 출현을 O(n + 패턴 총 길이 + 출현 수)에 찾는다
// 검증: ① 교과서 예 {he, she, his, hers} / "ushers"  ② 무작위 패턴 집합(알파벳 2~3, 중복 패턴 포함)과 텍스트 3 000 쌍을 나이브 전수 탐색과 대조
//        ③ 구조 불변식: 실패 링크 = "그 노드 문자열의 가장 긴 진 접미사 중 트라이에 있는 것", 노드의 출력 목록 = 그 문자열의 접미사인 패턴(중복 포함) 전부
//        ④ 큰 입력(텍스트 200 000 자, 패턴 40 개)의 패턴별 출현 횟수와 닫힌 식: 패턴 a, aa, …, a^k 와 텍스트 a^n 의 총 출현 수 = Σ(n - j + 1)
class AhoCorasick {
    struct Node { int next[26]; int fail = 0, parent = -1; char ch = 0; std::vector<int> out; Node() { std::fill(next, next + 26, -1); } };
    std::vector<Node> t; std::vector<std::string> pats;
public:
    explicit AhoCorasick(const std::vector<std::string>& patterns) : t(1), pats(patterns) {
        for (int id = 0; id < (int)pats.size(); id++) {
            if (pats[id].empty()) continue;                            // 빈 패턴은 무시
            int cur = 0;
            for (char ch : pats[id]) {
                int c = ch - 'a';
                if (t[cur].next[c] < 0) { int v = (int)t.size(); t.emplace_back(); t[v].parent = cur; t[v].ch = ch; t[cur].next[c] = v; }
                cur = t[cur].next[c];
            }
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
    std::vector<size_t> countPerPattern(const std::string& text) const {   // 문자열을 만들지 않고 패턴별 출현 횟수만 센다
        std::vector<size_t> cnt(pats.size(), 0); int cur = 0;
        for (char ch : text) { cur = t[cur].next[ch - 'a']; for (int id : t[cur].out) ++cnt[id]; }
        return cnt;
    }
    size_t nodes() const { return t.size(); }
    std::string nodeString(int v) const { std::string s; for (; v > 0; v = t[v].parent) s += t[v].ch; std::reverse(s.begin(), s.end()); return s; }
    int failOf(int v) const { return t[v].fail; }
    size_t outCount(int v) const { return t[v].out.size(); }
};
std::vector<std::pair<std::string, size_t>> naive(const std::vector<std::string>& pats, const std::string& text) {
    std::vector<std::pair<std::string, size_t>> r;
    for (const std::string& p : pats) { if (p.empty()) continue; for (size_t i = 0; i + p.size() <= text.size(); ++i) if (text.compare(i, p.size(), p) == 0) r.push_back({p, i}); }
    std::sort(r.begin(), r.end()); return r;
}

int main() {
    AhoCorasick ac({"he", "she", "his", "hers"});
    auto r = ac.search("ushers");
    std::sort(r.begin(), r.end());
    std::vector<std::pair<std::string, size_t>> expect = {{"he", 2}, {"hers", 2}, {"she", 1}};
    assert(r == expect);
    assert(AhoCorasick({"a", "aa"}).search("aaa").size() == 5);       // a×3 + aa×2
    assert(AhoCorasick({}).search("abc").empty() && AhoCorasick({""}).search("abc").empty() && AhoCorasick({"abc"}).search("").empty());   // 경계: 패턴 없음, 빈 패턴, 빈 텍스트
    assert(AhoCorasick({"ab", "ab"}).search("abab").size() == 4);     // 같은 패턴 둘은 각각 보고된다

    // ② 무작위 대조 + ③ 구조 불변식
    std::mt19937 rng(1234); long matches = 0, nodesTotal = 0;
    for (int it = 0; it < 3000; ++it) {
        int sigma = 2 + (int)(rng() % 2), np = 1 + (int)(rng() % 8); std::vector<std::string> pats;
        for (int i = 0; i < np; ++i) { std::string p; for (int k = 0, n = 1 + (int)(rng() % 5); k < n; ++k) p += (char)('a' + rng() % sigma); pats.push_back(p); }
        if (rng() % 4 == 0) pats.push_back(pats[rng() % pats.size()]);          // 중복 패턴
        std::string text; for (int k = 0, n = (int)(rng() % 60); k < n; ++k) text += (char)('a' + rng() % sigma);
        AhoCorasick a(pats); auto got = a.search(text); std::sort(got.begin(), got.end()); auto want = naive(pats, text);
        assert(got == want); matches += (long)got.size(); nodesTotal += (long)a.nodes();
        std::vector<size_t> cnt = a.countPerPattern(text); size_t sum = 0; for (size_t c : cnt) sum += c; assert(sum == got.size());
        std::set<std::string> trie; for (int v = 0; v < (int)a.nodes(); ++v) trie.insert(a.nodeString(v));
        assert(trie.size() == a.nodes());                                       // 노드마다 문자열이 다르다
        for (int v = 1; v < (int)a.nodes(); ++v) {
            std::string s = a.nodeString(v), best;
            for (size_t k = 1; k < s.size(); ++k) if (trie.count(s.substr(k))) { best = s.substr(k); break; }       // 가장 긴 진 접미사부터
            assert(a.nodeString(a.failOf(v)) == best);                          // 실패 링크의 정의
            size_t suffixPatterns = 0; for (const std::string& p : pats) if (!p.empty() && p.size() <= s.size() && s.compare(s.size() - p.size(), p.size(), p) == 0) ++suffixPatterns;
            assert(a.outCount(v) == suffixPatterns);                            // 출력 목록 = 접미사인 패턴 전부
        }
    }
    assert(matches > 20000 && nodesTotal > 15000);
    // ④ 큰 입력
    std::vector<std::string> big; for (int i = 0; i < 40; ++i) { std::string p; for (int k = 0, n = 1 + (int)(rng() % 8); k < n; ++k) p += (char)('a' + rng() % 4); big.push_back(p); }
    std::string bigText(200000, 'a'); for (char& c : bigText) c = (char)('a' + rng() % 4);
    AhoCorasick ab(big); std::vector<size_t> cnt = ab.countPerPattern(bigText);
    for (size_t i = 0; i < big.size(); ++i) { size_t c = 0; for (size_t pos = bigText.find(big[i]); pos != std::string::npos; pos = bigText.find(big[i], pos + 1)) ++c; assert(cnt[i] == c); }
    const int K = 20, N = 1000; std::vector<std::string> as; for (int j = 1; j <= K; ++j) as.push_back(std::string(j, 'a'));
    std::vector<size_t> ac2 = AhoCorasick(as).countPerPattern(std::string(N, 'a')); for (int j = 1; j <= K; ++j) assert(ac2[j - 1] == (size_t)(N - j + 1));
    std::cout << "AhoCorasick: " << matches << " matches in 3000 random pattern sets agreed with naive search; failure links and output lists matched their definitions; 200000-char text checked for 40 patterns" << std::endl;
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// 최장 공통 부분 문자열: a 의 접미사 자동자를 만들고 b 를 한 글자씩 흘려 보내며 "현재 일치 길이"를 추적한다. O(|a| + |b|)
// 검증: ① 손으로 고른 경우(빈 문자열, 전체 일치, 겹치는 반복)  ② 접미사 자동자 자체: 서로 다른 부분 문자열의 수 Σ(len[v] - len[link[v]]) 가 브루트포스 집합 크기와 같고,
//        상태 수 ≤ 2n - 1, 모든 부분 문자열은 받아들이고 아닌 문자열은 거부  ③ 무작위 쌍 4 000 개(알파벳 2~4)를 O(|a||b|) DP 오라클과 대조 — 길이뿐 아니라 *반환 문자열* 도 같다(b 에서 가장 먼저 끝나는 최장 일치)
//        ④ 긴 입력(각 2 000 자) 5 쌍
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
    long long distinctSubstrings() const { long long s = 0; for (size_t v = 1; v < st.size(); ++v) s += st[v].len - st[st[v].link].len; return s; }
    bool contains(const std::string& s) const { int v = 0; for (char c : s) { auto it = st[v].next.find(c); if (it == st[v].next.end()) return false; v = it->second; } return true; }
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
    return best == 0 ? std::string() : b.substr(bestEnd - best + 1, best);        // best == 0 일 때 b 가 비어 있으면 substr(1, 0) 이 예외를 던지므로 따로 처리
}
std::string oracleLcs(const std::string& a, const std::string& b) {                // O(|a||b|) DP: dp[j] = a[..i] 와 b[..j] 가 접미사로 일치하는 길이
    std::vector<int> prev(a.size() + 1, 0), cur(a.size() + 1, 0); int best = 0, bestEnd = 0;
    for (size_t j = 0; j < b.size(); ++j) {
        for (size_t i = 0; i < a.size(); ++i) cur[i + 1] = a[i] == b[j] ? prev[i] + 1 : 0;
        for (size_t i = 1; i <= a.size(); ++i) if (cur[i] > best) { best = cur[i]; bestEnd = (int)j; }     // b 에서 가장 먼저 끝나는 최장 일치
        std::swap(prev, cur);
    }
    return best == 0 ? std::string() : b.substr(bestEnd - best + 1, best);
}

int main() {
    assert(lcsubstr("abcdxyz", "xyzabcd") == "abcd");
    assert(lcsubstr("zxabcdezy", "yzabcdezx") == "abcdez");
    assert(lcsubstr("abc", "xyz").empty());
    assert(lcsubstr("", "abc").empty() && lcsubstr("abc", "").empty() && lcsubstr("", "").empty());       // 경계: 빈 입력 (b 가 비어도 예외 없음)
    assert(lcsubstr("hello", "hello") == "hello" && lcsubstr("aaaa", "aaaaaa") == "aaaa" && lcsubstr("abab", "baba") == "bab");      // "aba" 와 "bab" 이 같은 길이: b 에서 먼저 끝나는 "bab" 을 돌려준다
    // ② 접미사 자동자의 성질
    std::mt19937 rng(8); long samChecks = 0;
    for (int it = 0; it < 2000; ++it) {
        int sigma = 2 + (int)(rng() % 3), n = (int)(rng() % 14); std::string s; for (int i = 0; i < n; ++i) s += (char)('a' + rng() % sigma);
        SAM sam; for (char c : s) sam.extend(c);
        std::set<std::string> subs; for (size_t i = 0; i < s.size(); ++i) for (size_t l = 1; i + l <= s.size(); ++l) subs.insert(s.substr(i, l));
        assert(sam.distinctSubstrings() == (long long)subs.size());
        assert(n < 2 || sam.st.size() <= (size_t)(2 * n - 1) + 1);                      // 상태 수 ≤ 2n - 1 (+ 빈 문자열을 나타내는 시작 상태)
        for (auto& x : subs) assert(sam.contains(x));
        for (int k = 0; k < 20; ++k) { std::string q; for (int i = 0, m = 1 + (int)(rng() % 6); i < m; ++i) q += (char)('a' + rng() % sigma); assert(sam.contains(q) == (subs.count(q) > 0)); ++samChecks; }
    }
    // ③ 무작위 쌍
    long totalLen = 0, empties = 0;
    for (int it = 0; it < 4000; ++it) {
        int sigma = 2 + (int)(rng() % 3); std::string a, b;
        for (int i = 0, n = (int)(rng() % 25); i < n; ++i) a += (char)('a' + rng() % sigma);
        for (int i = 0, n = (int)(rng() % 25); i < n; ++i) b += (char)('a' + rng() % sigma);
        std::string got = lcsubstr(a, b); assert(got == oracleLcs(a, b));
        assert(a.find(got) != std::string::npos && b.find(got) != std::string::npos);   // 실제로 공통 부분 문자열
        totalLen += (long)got.size(); empties += got.empty();
    }
    assert(totalLen > 10000 && empties > 5 && samChecks == 40000);
    // ④ 긴 입력
    for (int it = 0; it < 5; ++it) {
        std::string a, b; for (int i = 0; i < 2000; ++i) { a += (char)('a' + rng() % 4); b += (char)('a' + rng() % 4); }
        std::string common = a.substr(500, 40 + it); b.replace(1200, common.size(), common);          // 길이 40+ 의 공통 구간을 심는다
        std::string got = lcsubstr(a, b); assert(got == oracleLcs(a, b) && got.size() >= common.size());
    }
    std::cout << "LongestCommonSubstring: 4000 random pairs and 5 long pairs matched the DP oracle (including the returned string); the automaton's distinct-substring count matched brute force on 2000 strings" << std::endl;
    return 0;
}
// Time Complexity: O(|a| log σ + |b| log σ)
// Space Complexity: O(|a|)
```
# Part 11. 압축·변환
## LZW()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>

// LZW: 지금까지 본 문자열을 사전에 등록하며 코드로 대체한다. 사전은 부호기와 복호기가 같은 규칙으로 따로 만들기 때문에 사전을 전송하지 않는다 (GIF, 옛 Unix compress)
// 사전 크기를 maxCodes 로 제한하면(GIF 는 4096) 가득 찬 뒤로는 더 등록하지 않는다. 코드를 바이트로 묶을 때는 i 번째 코드의 비트 폭을 *인덱스만으로* 정해 부호기와 복호기가 어긋나지 않게 한다
// 검증: ① 위키백과의 알려진 출력 [84 79 66 69 79 82 78 79 84 256 258 260 265 259 261 263]  ② 닫힌 식: a^n 은 길이 1, 2, 3, … 인 조각들로 나뉜다(1000 자 -> 45 코드)
//        ③ 무작위 입력(알파벳 1·2·4·256, 길이 0~3 000, 상한 260·300·512·4096·무제한) 왕복을 코드열과 비트 포장 두 단계 모두에서 확인 (KwKwK 경우 포함)  ④ 압축률: 반복 텍스트는 30 % 미만, 난수 바이트는 늘어남이 제한적
std::vector<int> lzwEncode(const std::string& in, int maxCodes = 1 << 30) {
    std::map<std::string, int> dict;
    for (int i = 0; i < 256; i++) dict[std::string(1, (char)i)] = i;
    std::vector<int> out; std::string w;
    for (char c : in) {
        std::string wc = w + c;
        if (dict.count(wc)) w = wc;
        else { out.push_back(dict[w]); if ((int)dict.size() < maxCodes) { int id = (int)dict.size(); dict[wc] = id; } w = std::string(1, c); }
    }
    if (!w.empty()) out.push_back(dict[w]);
    return out;
}
std::string lzwDecode(const std::vector<int>& codes, int maxCodes = 1 << 30) {
    if (codes.empty()) return std::string();                           // 빈 입력: codes[0] 을 읽으면 안 된다
    std::vector<std::string> dict(256);
    for (int i = 0; i < 256; i++) dict[i] = std::string(1, (char)i);
    std::string w = dict[codes[0]], out = w;
    for (size_t i = 1; i < codes.size(); i++) {
        int k = codes[i]; std::string entry;
        if (k < (int)dict.size()) entry = dict[k]; else { assert(k == (int)dict.size()); entry = w + w[0]; }     // 아직 등록 전인 코드(KwKwK 경우)
        out += entry;
        if ((int)dict.size() < maxCodes) dict.push_back(w + entry[0]);
        w = entry;
    }
    return out;
}
int widthAt(size_t i, int maxCodes) {                                  // i 번째 코드가 가질 수 있는 최댓값 = min(255 + i, maxCodes - 1)
    long long top = std::min<long long>(255 + (long long)i, maxCodes - 1); int w = 9; while ((1LL << w) <= top) ++w; return w;
}
std::vector<uint8_t> pack(const std::vector<int>& codes, int maxCodes) {       // 헤더 4 바이트(코드 수) + LSB 우선 비트열
    std::vector<uint8_t> out(4); for (int k = 0; k < 4; ++k) out[k] = (uint8_t)((uint32_t)codes.size() >> (8 * k));
    uint64_t acc = 0; int bits = 0;
    for (size_t i = 0; i < codes.size(); ++i) {
        int w = widthAt(i, maxCodes); assert(codes[i] >= 0 && (1LL << w) > codes[i]);
        acc |= (uint64_t)codes[i] << bits; bits += w;
        while (bits >= 8) { out.push_back((uint8_t)acc); acc >>= 8; bits -= 8; }
    }
    if (bits > 0) out.push_back((uint8_t)acc);
    return out;
}
std::vector<int> unpack(const std::vector<uint8_t>& bytes, int maxCodes) {
    size_t n = 0; for (int k = 0; k < 4; ++k) n |= (size_t)bytes[k] << (8 * k);
    std::vector<int> codes; uint64_t acc = 0; int bits = 0; size_t pos = 4;
    for (size_t i = 0; i < n; ++i) {
        int w = widthAt(i, maxCodes);
        while (bits < w) { acc |= (uint64_t)bytes[pos++] << bits; bits += 8; }
        codes.push_back((int)(acc & ((1ULL << w) - 1))); acc >>= w; bits -= w;
    }
    return codes;
}

int main() {
    std::string s = "TOBEORNOTTOBEORTOBEORNOT";
    auto codes = lzwEncode(s);
    assert((codes == std::vector<int>{84, 79, 66, 69, 79, 82, 78, 79, 84, 256, 258, 260, 265, 259, 261, 263}));    // 알려진 출력
    assert(lzwDecode(codes) == s);
    assert(codes.size() < s.size());                                   // 반복 덕분에 코드 수가 줄어든다
    assert(codes[0] == 'T' && codes[9] == 256);                        // 9번째 코드: 처음으로 사전 항목("TO")을 사용
    std::string rep(1000, 'a');
    assert(lzwDecode(lzwEncode(rep)) == rep && lzwEncode(rep).size() == 45);          // a^1000: 길이 1,2,…,44 조각(합 990) + 마지막 10
    assert(lzwEncode("").empty() && lzwDecode({}).empty() && lzwDecode(lzwEncode("x")) == "x");           // 경계: 빈 입력, 한 글자
    assert(lzwDecode(lzwEncode(std::string("\0\xFF\0", 3))) == std::string("\0\xFF\0", 3));              // 바이너리(NUL 포함)
    assert(widthAt(0, 1 << 30) == 9 && widthAt(256, 1 << 30) == 9 && widthAt(257, 1 << 30) == 10 && widthAt(768, 1 << 30) == 10 && widthAt(769, 1 << 30) == 11 && widthAt(100000, 300) == 9);   // 폭이 늘어나는 경계

    std::mt19937 rng(77); long cases = 0, kwkwk = 0, totalIn = 0, totalCodes = 0;
    const int limits[] = {260, 300, 512, 4096, 1 << 30}; const int sigmas[] = {1, 2, 4, 256};
    for (int it = 0; it < 400; ++it) {
        int sigma = sigmas[rng() % 4], limit = limits[rng() % 5], n = (int)(rng() % 3001);
        std::string in; for (int i = 0; i < n; ++i) in += (char)(sigma == 256 ? rng() % 256 : 'a' + rng() % sigma);
        std::vector<int> c = lzwEncode(in, limit); assert(lzwDecode(c, limit) == in);
        std::vector<uint8_t> bytes = pack(c, limit); assert(unpack(bytes, limit) == c && lzwDecode(unpack(bytes, limit), limit) == in);
        for (int code : c) assert(code < std::max(limit, 256));
        { std::map<int, int> firstSeen; for (size_t i = 0; i < c.size(); ++i) if (c[i] >= 256 && !firstSeen.count(c[i])) { firstSeen[c[i]] = (int)i; if (c[i] == 256 + (int)i - 1 && limit > 256 + (int)i - 1) ++kwkwk; } }      // 방금 만든 항목을 바로 쓰는 경우의 수
        ++cases; totalIn += n; totalCodes += (long)c.size();
    }
    assert(cases == 400 && kwkwk > 50 && totalCodes < totalIn);
    // ④ 압축률
    std::string text; for (int i = 0; i < 200; ++i) text += "the quick brown fox ";
    assert(pack(lzwEncode(text), 1 << 30).size() * 10 < text.size() * 3);
    std::string noise(3000, 'x'); for (char& ch : noise) ch = (char)rng();
    size_t packed = pack(lzwEncode(noise, 4096), 4096).size(); assert(packed >= noise.size() && packed <= noise.size() * 3 / 2 + 8);        // 난수 바이트는 압축되지 않고 9~12 비트로 늘어난다
    std::cout << "LZW: " << cases << " round trips (" << totalIn << " bytes -> " << totalCodes << " codes) at every dictionary limit; the textbook vector matched; repeated text packed to " << pack(lzwEncode(text), 1 << 30).size() << " of " << text.size() << " bytes" << std::endl;
    return 0;
}
// Time Complexity: O(n log D)
// Space Complexity: O(D)  (사전 크기)
```
## BurrowsWheelerTransform()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// BWT: 모든 회전을 정렬해 마지막 열만 취한다. 같은 문맥 뒤의 글자들이 모여 반복(run)이 늘어나므로 압축에 유리하다(bzip2).
// 가역 변환: 마지막 열 L 과 정렬된 첫 열 F 사이의 LF 대응으로 원문을 복원한다.  두 가지 표기:
//   ① 끝 표식 '$' (가장 작은 유일한 글자로 취급) — 원문에 '$' 가 없어야 한다.  접미사 배열(배증)로 O(n log² n) 에 만드는 빠른 판과 회전 전수 정렬 판을 둘 다 둔다
//   ② 표식 없는 판: 정렬된 회전 중 *원문이 있는 행 번호* 를 함께 저장한다 (bzip2 방식) — 모든 바이트(NUL, '$' 포함)와 주기 문자열을 처리한다
// 검증: 교과서 값 3 개(banana, abracadabra, mississippi)  ② {a,b} 위의 길이 ≤ 10 문자열 2 047 개 *전부*: 세 구현이 같고 복원이 정확하며 변환이 단사
//        ③ 무작위 바이트 문자열 600 개의 왕복 + 접미사 배열 판과 회전 판 일치  ④ 반복이 모이는 효과: 자연어풍 텍스트의 run 수가 줄어든다
int ord(char c) { return c == '$' ? -1 : (unsigned char)c; }
std::string bwt(const std::string& s) {                          // 느린 정의 그대로: 회전을 모두 비교해 정렬
    assert(s.find('$') == std::string::npos);
    std::string t = s + '$'; size_t n = t.size();
    std::vector<int> idx(n); std::iota(idx.begin(), idx.end(), 0);
    std::sort(idx.begin(), idx.end(), [&](int a, int b) {                       // 회전 비교
        for (size_t k = 0; k < n; k++) { int x = ord(t[(a + k) % n]), y = ord(t[(b + k) % n]); if (x != y) return x < y; }
        return false; });
    std::string L;
    for (int i : idx) L += t[(i + n - 1) % n];
    return L;
}
std::vector<int> suffixArray(const std::string& t) {              // 접미사 배열(배증): 끝 표식이 가장 작고 유일하므로 접미사 순서 = 회전 순서
    int n = (int)t.size(); std::vector<int> sa(n), rk(n), tmp(n);
    for (int i = 0; i < n; i++) { sa[i] = i; rk[i] = ord(t[i]); }
    for (int k = 1;; k <<= 1) {
        auto cmp = [&](int a, int b) { if (rk[a] != rk[b]) return rk[a] < rk[b]; int ra = a + k < n ? rk[a + k] : -2, rb = b + k < n ? rk[b + k] : -2; return ra < rb; };
        std::sort(sa.begin(), sa.end(), cmp);
        tmp[sa[0]] = 0; for (int i = 1; i < n; i++) tmp[sa[i]] = tmp[sa[i - 1]] + (cmp(sa[i - 1], sa[i]) ? 1 : 0);
        rk = tmp; if (rk[sa[n - 1]] == n - 1) break;
    }
    return sa;
}
std::string bwtFast(const std::string& s) {
    assert(s.find('$') == std::string::npos);
    std::string t = s + '$'; std::vector<int> sa = suffixArray(t); std::string L;
    for (int i : sa) L += t[(i + t.size() - 1) % t.size()];
    return L;
}
std::string inverseBwt(const std::string& L) {
    size_t n = L.size();
    std::vector<int> order(n); std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(), [&](int a, int b) { return ord(L[a]) < ord(L[b]); });   // order[i] = F 의 i번째 글자가 L 의 몇 번째인가
    size_t row = std::find(L.begin(), L.end(), '$') - L.begin();
    std::string out;
    for (size_t i = 0; i < n; i++) { row = order[row]; out += L[row]; }
    // 위 루프는 '$' 다음 글자부터 차례로 복원한다 (마지막에 '$' 도달)
    return out.substr(0, n - 1);
}
std::string bwtRot(const std::string& s, size_t& row) {            // ② 표식 없는 판: 정렬된 회전의 마지막 열 + 원문이 놓인 행
    size_t n = s.size(); std::vector<int> idx(n); std::iota(idx.begin(), idx.end(), 0);
    std::sort(idx.begin(), idx.end(), [&](int a, int b) {
        for (size_t k = 0; k < n; k++) { unsigned char x = s[(a + k) % n], y = s[(b + k) % n]; if (x != y) return x < y; }
        return a < b; });                                          // 같은 회전(주기 문자열)은 번호순
    std::string L; row = 0;
    for (size_t i = 0; i < n; i++) { L += s[(idx[i] + n - 1) % n]; if (idx[i] == 0) row = i; }
    return L;
}
std::string inverseRot(const std::string& L, size_t row) {
    size_t n = L.size(); std::vector<int> order(n); std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(), [&](int a, int b) { return (unsigned char)L[a] < (unsigned char)L[b]; });
    std::string out; size_t cur = row;
    for (size_t i = 0; i < n; i++) { out += L[order[cur]]; cur = order[cur]; }                     // F[cur] = L[order[cur]]
    return out;
}
int runs(const std::string& x) { int r = x.empty() ? 0 : 1; for (size_t i = 1; i < x.size(); i++) r += x[i] != x[i - 1]; return r; }

int main() {
    assert(bwt("banana") == "annb$aa");                       // 교과서의 표준 예
    assert(inverseBwt("annb$aa") == "banana");
    assert(bwt("abracadabra") == "ard$rcaaaabb" && bwt("mississippi") == "ipssm$pissii" && bwtFast("mississippi") == "ipssm$pissii");     // 알려진 값 (정의대로 정렬한 결과)
    for (std::string s : {"abracadabra", "mississippi", "aaaa", "a", ""}) assert(inverseBwt(bwt(s)) == s && inverseBwt(bwtFast(s)) == s);
    assert(bwt("") == "$" && inverseBwt("$") == "");           // 경계: 빈 문자열
    // ② {a,b} 위의 길이 ≤ 10 문자열 전부
    std::vector<std::string> all{std::string()};
    for (size_t i = 0; i < all.size(); ++i) if (all[i].size() < 10) { all.push_back(all[i] + 'a'); all.push_back(all[i] + 'b'); }
    assert(all.size() == 2047);
    std::set<std::pair<size_t, std::string>> images;       // 변환이 단사인가
    for (const std::string& s : all) {
        std::string L = bwt(s); assert(L == bwtFast(s) && inverseBwt(L) == s);
        std::string sortedL = L, sortedT = s + '$'; std::sort(sortedL.begin(), sortedL.end()); std::sort(sortedT.begin(), sortedT.end()); assert(sortedL == sortedT);   // 글자의 재배열
        images.insert({s.size(), L});
        size_t row = 0; std::string R = bwtRot(s, row); assert(inverseRot(R, row) == s);
    }
    assert(images.size() == 2047);                              // 길이가 같은 서로 다른 문자열은 다른 BWT
    // ③ 무작위 바이트 문자열
    std::mt19937 rng(3);
    for (int it = 0; it < 600; ++it) {
        int n = (int)(rng() % 120), sigma = it % 3 == 0 ? 256 : it % 3 == 1 ? 3 : 20; std::string s;
        for (int i = 0; i < n; ++i) { char c; do c = (char)(sigma == 256 ? rng() % 256 : 'a' + rng() % sigma); while (c == '$'); s += c; }
        std::string L = bwt(s); assert(L == bwtFast(s) && inverseBwt(L) == s);
        std::string any(n, 'x'); for (char& c : any) c = (char)(sigma == 256 ? rng() % 256 : '$' + rng() % 3);    // '$' 와 NUL 이 섞여도 표식 없는 판은 된다
        size_t row = 0; std::string R = bwtRot(any, row); assert(inverseRot(R, row) == any && R.size() == any.size());
    }
    for (std::string per : std::vector<std::string>{"abab", "aaaa", "abcabc", std::string("\0\0", 2), std::string("$$$", 3)}) { size_t row = 0; std::string R = bwtRot(per, row); assert(inverseRot(R, row) == per); }     // 주기 문자열
    // ④ 반복이 모이는 효과
    std::string text; for (int i = 0; i < 60; ++i) text += (i % 3 == 0 ? "the cat sat on the mat " : i % 3 == 1 ? "the dog sat on the log " : "the bat sat on the hat ");
    std::string tb = bwtFast(text); assert(inverseBwt(tb) == text && runs(tb) * 4 < runs(text));
    std::string rnd(2000, 'a'); for (char& c : rnd) c = (char)('a' + rng() % 26); assert(runs(bwtFast(rnd)) > runs(rnd) * 9 / 10);        // 무작위 텍스트에서는 모이지 않는다 (대조군)
    std::cout << "BWT: banana -> " << bwt("banana") << "; all 2047 binary strings up to length 10 matched across three implementations and were uniquely invertible; natural-like text runs " << runs(text) << " -> " << runs(tb) << std::endl;
    return 0;
}
// Time Complexity: 정의대로 O(n² log n), 접미사 배열(배증) O(n log² n), SA-IS 로 O(n)
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
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 허프먼 부호: 자주 나오는 글자에 짧은 비트열을 준다. 가장 빈도가 낮은 두 노드를 합치는 탐욕 알고리즘으로 최적의 접두사 부호를 만든다.
// 평균 부호 길이 L 은 엔트로피 H 이상, H + 1 미만.  트리 모양이 아니라 *코드 길이* 만 전송하면 복호기가 같은 정규(canonical) 부호를 재구성한다 (DEFLATE, JPEG)
// 검증: ① 예제 문장의 비용(55 비트)과 왕복  ② 최적성 오라클 둘: (가) 글자 2~6 개의 무작위 빈도 1 500 개에서 *모든* 길이 배정을 크래프트 부등식으로 걸러 최솟값을 전수 탐색,
//        (나) 정렬된 빈도에 대한 투 큐 O(n) 알고리즘(글자 최대 200 개) — 비용이 일치  ③ 접두사 부호성(크래프트 합 = 1, 어떤 부호도 다른 부호의 접두사가 아님),
//        정규 복호(길이별 첫 부호값 표)와 트리 복호가 같고 비트 패킹 왕복  ④ H ≤ 평균 < H+1, 2의 거듭제곱 분포는 평균 = H 정확히, 피보나치 빈도는 깊이 σ-1, 글자 하나·빈 입력 경계
struct HNode { long f; int l, r; };
std::vector<int> huffmanLengths(const std::vector<long>& freq) {         // freq[s] == 0 이면 쓰지 않는 글자 (길이 0)
    int n = (int)freq.size(); std::vector<int> len(n, 0); std::vector<HNode> t(n);
    typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq;
    for (int i = 0; i < n; i++) { t[i] = {freq[i], -1, -1}; if (freq[i] > 0) pq.push({freq[i], i}); }
    if (pq.empty()) return len;
    if (pq.size() == 1) { len[pq.top().second] = 1; return len; }      // 글자가 하나뿐이어도 1 비트는 쓴다
    while (pq.size() > 1) {
        Q a = pq.top(); pq.pop(); Q b = pq.top(); pq.pop();
        int id = (int)t.size(); t.push_back({a.first + b.first, a.second, b.second}); pq.push({t[id].f, id});
    }
    std::vector<std::pair<int, int>> st{{pq.top().second, 0}};
    while (!st.empty()) { std::pair<int, int> p = st.back(); st.pop_back(); if (t[p.first].l < 0) len[p.first] = p.second; else { st.push_back({t[p.first].l, p.second + 1}); st.push_back({t[p.first].r, p.second + 1}); } }
    return len;
}
std::vector<std::string> canonicalCodes(const std::vector<int>& len) {   // (길이, 글자) 순으로 번호를 매기며 코드를 1 씩 늘리고, 길이가 늘면 왼쪽으로 민다
    std::vector<int> syms; for (int i = 0; i < (int)len.size(); i++) if (len[i] > 0) syms.push_back(i);
    std::sort(syms.begin(), syms.end(), [&](int a, int b) { return len[a] != len[b] ? len[a] < len[b] : a < b; });
    std::vector<std::string> code(len.size()); unsigned long long c = 0; int prev = 0;
    for (int s : syms) {
        assert(len[s] <= 62); c <<= (len[s] - prev); prev = len[s];
        for (int b = len[s] - 1; b >= 0; b--) code[s] += (char)('0' + ((c >> b) & 1));
        ++c;
    }
    return code;
}
struct CanonicalDecoder {                                                // 트리 없이 복호: 길이별 첫 부호값 / 개수 / 글자 표
    std::vector<int> syms; std::vector<long long> first, count, offset; int maxLen = 0;
    explicit CanonicalDecoder(const std::vector<int>& len) {
        for (int l : len) maxLen = std::max(maxLen, l);
        for (int i = 0; i < (int)len.size(); i++) if (len[i] > 0) syms.push_back(i);
        std::sort(syms.begin(), syms.end(), [&](int a, int b) { return len[a] != len[b] ? len[a] < len[b] : a < b; });
        first.assign(maxLen + 2, 0); count.assign(maxLen + 2, 0); offset.assign(maxLen + 2, 0);
        for (int s : syms) ++count[len[s]];
        long long code = 0, off = 0;
        for (int l = 1; l <= maxLen; l++) { first[l] = code; offset[l] = off; code = (code + count[l]) << 1; off += count[l]; }
    }
    std::vector<int> decode(const std::string& bits, size_t n) const {
        std::vector<int> out; long long code = 0; int l = 0;
        for (char b : bits) {
            code = code << 1 | (b - '0'); ++l; assert(l <= maxLen);
            if (count[l] && code >= first[l] && code - first[l] < count[l]) { out.push_back(syms[offset[l] + code - first[l]]); code = 0; l = 0; if (out.size() == n) break; }
        }
        return out;
    }
};
std::vector<int> treeDecode(const std::vector<std::string>& code, const std::string& bits, size_t n) {   // 오라클: 부호표로 트라이를 만들어 비트를 따라 내려간다
    std::vector<std::array<int, 3>> trie(1, {-1, -1, -1});               // {0 자식, 1 자식, 글자}
    for (int s = 0; s < (int)code.size(); s++) if (!code[s].empty()) { int cur = 0; for (char ch : code[s]) { int b = ch - '0'; if (trie[cur][b] < 0) { trie[cur][b] = (int)trie.size(); trie.push_back({-1, -1, -1}); } cur = trie[cur][b]; } assert(trie[cur][2] < 0); trie[cur][2] = s; }
    std::vector<int> out; int cur = 0;
    for (char ch : bits) { cur = trie[cur][ch - '0']; assert(cur >= 0); if (trie[cur][2] >= 0) { out.push_back(trie[cur][2]); cur = 0; if (out.size() == n) break; } }
    return out;
}
long twoQueueCost(std::vector<long> f) {                                 // 정렬된 빈도에서 O(n): 합쳐진 노드의 가중치 합 = Σ 빈도 × 깊이
    std::sort(f.begin(), f.end()); std::queue<long> q1, q2; for (long x : f) q1.push(x);
    long cost = 0; auto pop = [&]() { long v; if (q2.empty() || (!q1.empty() && q1.front() <= q2.front())) { v = q1.front(); q1.pop(); } else { v = q2.front(); q2.pop(); } return v; };
    while (q1.size() + q2.size() > 1) { long a = pop(), b = pop(); cost += a + b; q2.push(a + b); }
    return cost;
}
long weightedLength(const std::vector<long>& f, const std::vector<int>& len) { long s = 0; for (size_t i = 0; i < f.size(); i++) s += f[i] * len[i]; return s; }
long bruteOptimum(const std::vector<long>& f) {                          // 오라클 (가): 길이 1..σ-1 의 모든 배정 중 Σ 2^-l ≤ 1 인 것의 최소 비용
    int s = (int)f.size(); std::vector<int> len(s, 1); long best = -1;
    for (;;) {
        long kraft = 0; for (int l : len) kraft += 1L << (s - 1 - l);
        if (kraft <= (1L << (s - 1))) { long c = weightedLength(f, len); if (best < 0 || c < best) best = c; }
        int i = 0; while (i < s && len[i] == s - 1) { len[i] = 1; ++i; } if (i == s) break; ++len[i];
    }
    return best;
}
std::string packedBits(const std::string& bits, std::vector<uint8_t>& bytes) { bytes.assign((bits.size() + 7) / 8, 0); for (size_t i = 0; i < bits.size(); i++) if (bits[i] == '1') bytes[i / 8] |= (uint8_t)(0x80 >> (i % 8)); std::string back; for (size_t i = 0; i < bits.size(); i++) back += (char)('0' + ((bytes[i / 8] >> (7 - i % 8)) & 1)); return back; }

int main() {
    // ① 예제 문장
    std::string text = "abracadabra alakazam"; std::vector<long> freq(256, 0); for (unsigned char c : text) freq[c]++;
    std::vector<int> len = huffmanLengths(freq); std::vector<std::string> code = canonicalCodes(len);
    assert(weightedLength(freq, len) == 55 && twoQueueCost(std::vector<long>{9, 2, 2, 1, 1, 1, 1, 1, 1, 1}) == 55);       // 55 는 파이썬 heapq 로 따로 구한 값
    std::string bits; for (unsigned char c : text) bits += code[c];
    assert(bits.size() == 55);
    std::vector<int> dec = CanonicalDecoder(len).decode(bits, text.size()), dec2 = treeDecode(code, bits, text.size());
    assert(dec == dec2 && dec.size() == text.size()); for (size_t i = 0; i < text.size(); i++) assert(dec[i] == (unsigned char)text[i]);
    // ② 최적성: 전수 탐색 + 투 큐
    std::mt19937 rng(21); long checked = 0;
    for (int it = 0; it < 1500; ++it) {
        int s = 2 + (int)(rng() % 5); std::vector<long> f(s); for (long& x : f) x = 1 + (long)(rng() % 20);
        std::vector<int> l = huffmanLengths(f); assert(weightedLength(f, l) == bruteOptimum(f)); ++checked;
    }
    for (int it = 0; it < 300; ++it) {
        int s = 2 + (int)(rng() % 199); std::vector<long> f(s); for (long& x : f) x = 1 + (long)(rng() % 1000000);
        if (it % 3 == 0) for (long& x : f) x = 1 + (long)(rng() % 4);                  // 동점이 많은 경우
        assert(weightedLength(f, huffmanLengths(f)) == twoQueueCost(f)); ++checked;
    }
    // ③ 접두사 부호성과 복호 (무작위 치우친 분포)
    for (int it = 0; it < 300; ++it) {
        int s = 1 + (int)(rng() % 40); std::vector<long> f(s, 0); std::string msg; int n = (int)(rng() % 400);
        for (int i = 0; i < n; ++i) { int sym = (int)std::min<unsigned>(rng() % s, rng() % s); msg += (char)sym; f[sym]++; }     // 작은 번호가 더 자주 나오도록 치우침
        std::vector<int> l = huffmanLengths(f); std::vector<std::string> c = canonicalCodes(l);
        int used = 0, maxL = 0; for (int x : l) { used += x > 0; maxL = std::max(maxL, x); }
        if (used >= 2) { unsigned long long kraft = 0; for (int x : l) if (x > 0) kraft += 1ULL << (maxL - x); assert(kraft == 1ULL << maxL); }           // 크래프트 합 = 1 (가득 찬 트리)
        for (int a = 0; a < s; a++) for (int b = 0; b < s; b++) if (a != b && !c[a].empty() && !c[b].empty()) assert(c[b].compare(0, c[a].size(), c[a]) != 0);   // 접두사 부호
        std::string enc; for (char ch : msg) enc += c[(unsigned char)ch];
        std::vector<uint8_t> bytes; assert(packedBits(enc, bytes) == enc);
        if (n > 0) {
            std::vector<int> d1 = CanonicalDecoder(l).decode(enc, msg.size()), d2 = treeDecode(c, enc, msg.size());
            assert(d1 == d2 && d1.size() == msg.size()); for (size_t i = 0; i < msg.size(); i++) assert(d1[i] == (unsigned char)msg[i]);
        }
        if (n > 0 && used >= 2) { std::map<char, long> cnt; for (char ch : msg) cnt[ch]++; double H = 0; for (auto& kv : cnt) { double p = double(kv.second) / n; H -= p * std::log2(p); } double avg = double(enc.size()) / n; assert(avg >= H - 1e-9 && avg < H + 1); }     // ④ 엔트로피 한계
    }
    // ④ 특수한 분포
    std::vector<long> dyadic = {8, 4, 2, 1, 1}; std::vector<int> dl = huffmanLengths(dyadic);        // 확률 1/2, 1/4, 1/8, 1/16, 1/16 -> 길이 1,2,3,4,4
    assert((dl == std::vector<int>{1, 2, 3, 4, 4}));
    double H = 0, avg = 0; for (size_t i = 0; i < dyadic.size(); i++) { double p = dyadic[i] / 16.0; H -= p * std::log2(p); avg += p * dl[i]; } assert(std::fabs(avg - H) < 1e-12);       // 평균 = 엔트로피
    std::vector<long> fib = {1, 1}; while (fib.size() < 15) fib.push_back(fib[fib.size() - 1] + fib[fib.size() - 2]);
    std::vector<int> fl = huffmanLengths(fib); assert(*std::max_element(fl.begin(), fl.end()) == 14);  // 피보나치 빈도: 가장 깊은 트리 (σ - 1)
    assert((huffmanLengths({0, 5, 0}) == std::vector<int>{0, 1, 0}) && (huffmanLengths({0, 0}) == std::vector<int>{0, 0}) && huffmanLengths({}).empty());                  // 경계: 글자 하나, 빈 빈도
    assert((canonicalCodes({0, 1, 0})[1] == "0") && (huffmanLengths({3, 3}) == std::vector<int>{1, 1}));
    std::cout << "Huffman: " << text.size() * 8 << " bits -> " << bits.size() << " bits; " << checked << " random frequency tables matched the exhaustive / two-queue optimum, canonical and tree decoders agreed" << std::endl;
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 다메라우-레벤슈타인: 인접한 두 글자의 맞바꿈(transposition)도 비용 1.  오타("teh" -> "the") 교정에 적합
// - 제한형(OSA): 한 부분 문자열을 두 번 편집하지 못한다  /  - 완전형: 제한 없음 (Lowrance-Wagner).  예: "CA" -> "ABC" 는 OSA 3, 완전형 2
// 검증: ① 손으로 고른 값  ② {a,b,c} 위의 길이 ≤ 4 문자열 121 개의 *모든 쌍* 에서
//        (가) 완전형 = 삽입·삭제·치환·인접 맞바꿈 4 연산 그래프의 BFS 최단 거리(길이 ≤ 7 의 중간 문자열), (나) OSA = 접미사 쌍에 대한 하향식 재귀(점화식 방향이 다른 독립 구현),
//        (다) |길이 차| ≤ 완전형 ≤ OSA ≤ 레벤슈타인 ≤ max(n, m), 대칭성, 거리 0 <=> 같은 문자열
//        ③ 삼각 부등식: 완전형은 모든 삼중쌍(40³)에서 성립하고, OSA 는 깨지는 삼중쌍이 실제로 있다  ④ 무작위 편집 k 번으로 만든 오타의 거리 ≤ k (알파벳 26, 길이 ≤ 30)
int levenshtein(const std::string& a, const std::string& b) {
    std::vector<std::vector<int>> d(a.size() + 1, std::vector<int>(b.size() + 1));
    for (size_t i = 0; i <= a.size(); i++) d[i][0] = (int)i;
    for (size_t j = 0; j <= b.size(); j++) d[0][j] = (int)j;
    for (size_t i = 1; i <= a.size(); i++) for (size_t j = 1; j <= b.size(); j++) d[i][j] = std::min({d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] != b[j-1])});
    return d[a.size()][b.size()];
}
int osa(const std::string& a, const std::string& b) {
    size_t n = a.size(), m = b.size();
    std::vector<std::vector<int>> d(n + 1, std::vector<int>(m + 1));
    for (size_t i = 0; i <= n; i++) d[i][0] = (int)i;
    for (size_t j = 0; j <= m; j++) d[0][j] = (int)j;
    for (size_t i = 1; i <= n; i++) for (size_t j = 1; j <= m; j++) {
        d[i][j] = std::min({d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] != b[j-1])});
        if (i > 1 && j > 1 && a[i-1] == b[j-2] && a[i-2] == b[j-1]) d[i][j] = std::min(d[i][j], d[i-2][j-2] + 1);
    }
    return d[n][m];
}
int damerau(const std::string& a, const std::string& b) {
    size_t n = a.size(), m = b.size(); int maxd = (int)(n + m);
    std::map<char, int> da;
    std::vector<std::vector<int>> d(n + 2, std::vector<int>(m + 2));
    d[0][0] = maxd;
    for (size_t i = 0; i <= n; i++) { d[i+1][0] = maxd; d[i+1][1] = (int)i; }
    for (size_t j = 0; j <= m; j++) { d[0][j+1] = maxd; d[1][j+1] = (int)j; }
    for (size_t i = 1; i <= n; i++) {
        int db = 0;
        for (size_t j = 1; j <= m; j++) {
            int k = da.count(b[j-1]) ? da[b[j-1]] : 0, l = db, cost = 1;
            if (a[i-1] == b[j-1]) { cost = 0; db = (int)j; }
            d[i+1][j+1] = std::min({d[i][j] + cost, d[i+1][j] + 1, d[i][j+1] + 1, d[k][l] + (int)(i - k - 1) + 1 + (int)(j - l - 1)});
        }
        da[a[i-1]] = (int)i;
    }
    return d[n+1][m+1];
}
int osaTopDown(const std::string& a, size_t i, const std::string& b, size_t j, std::vector<std::vector<int>>& memo) {   // 접미사 a[i..], b[j..] 의 OSA 거리
    if (i == a.size()) return (int)(b.size() - j);
    if (j == b.size()) return (int)(a.size() - i);
    int& r = memo[i][j]; if (r >= 0) return r;
    r = std::min({osaTopDown(a, i + 1, b, j, memo) + 1, osaTopDown(a, i, b, j + 1, memo) + 1, osaTopDown(a, i + 1, b, j + 1, memo) + (a[i] != b[j])});
    if (i + 1 < a.size() && j + 1 < b.size() && a[i] == b[j + 1] && a[i + 1] == b[j]) r = std::min(r, 1 + osaTopDown(a, i + 2, b, j + 2, memo));
    return r;
}
int osaOracle(const std::string& a, const std::string& b) { std::vector<std::vector<int>> memo(a.size() + 1, std::vector<int>(b.size() + 1, -1)); return osaTopDown(a, 0, b, 0, memo); }
std::vector<std::string> neighbours(const std::string& s, int maxLen) {                 // 한 번의 연산으로 닿는 문자열 (알파벳 a,b,c)
    std::vector<std::string> r;
    for (size_t i = 0; i < s.size(); i++) { r.push_back(s.substr(0, i) + s.substr(i + 1)); for (char c = 'a'; c <= 'c'; c++) if (c != s[i]) { std::string t = s; t[i] = c; r.push_back(t); } }
    for (size_t i = 0; i + 1 < s.size(); i++) if (s[i] != s[i + 1]) { std::string t = s; std::swap(t[i], t[i + 1]); r.push_back(t); }
    if ((int)s.size() < maxLen) for (size_t i = 0; i <= s.size(); i++) for (char c = 'a'; c <= 'c'; c++) r.push_back(s.substr(0, i) + c + s.substr(i));
    return r;
}
std::map<std::string, int> bfs(const std::string& src, int maxLen) {
    std::map<std::string, int> dist{{src, 0}}; std::queue<std::string> q; q.push(src);
    while (!q.empty()) { std::string u = q.front(); q.pop(); for (const std::string& v : neighbours(u, maxLen)) if (!dist.count(v)) { dist[v] = dist[u] + 1; q.push(v); } }
    return dist;
}

int main() {
    assert(osa("teh", "the") == 1 && damerau("teh", "the") == 1);   // 맞바꿈은 한 번
    assert(osa("ca", "ac") == 1);
    assert(osa("CA", "ABC") == 3 && damerau("CA", "ABC") == 2);      // 완전형이 더 작다
    assert(damerau("kitten", "sitting") == 3 && damerau("", "ab") == 2);
    assert(damerau("", "") == 0 && osa("", "") == 0 && osa("abc", "") == 3 && damerau("abc", "") == 3 && damerau("abc", "abc") == 0);          // 경계: 빈 문자열
    std::vector<std::string> all{std::string()};
    for (size_t i = 0; i < all.size(); ++i) if (all[i].size() < 4) for (char c = 'a'; c <= 'c'; c++) all.push_back(all[i] + c);
    assert(all.size() == 121);
    long pairs = 0, osaGap = 0, damGap = 0;
    for (const std::string& a : all) {
        std::map<std::string, int> dist = bfs(a, 7);
        for (const std::string& b : all) {
            int dd = damerau(a, b), oo = osa(a, b), ll = levenshtein(a, b), diff = (int)(a.size() > b.size() ? a.size() - b.size() : b.size() - a.size()), mx = (int)std::max(a.size(), b.size());
            assert(dd == dist.at(b));                                 // (가) 완전형 = 4 연산 그래프의 최단 거리
            assert(oo == osaOracle(a, b));                            // (나) 독립 구현
            assert(diff <= dd && dd <= oo && oo <= ll && ll <= mx);   // (다) 순서 관계
            assert(dd == damerau(b, a) && oo == osa(b, a) && (dd == 0) == (a == b));
            osaGap += oo > dd; damGap += ll > dd; ++pairs;
        }
    }
    assert(pairs == 121 * 121 && osaGap > 50 && damGap > 500);       // OSA 가 완전형보다 큰 쌍이 실제로 있다
    // ③ 삼각 부등식 (길이 ≤ 3 인 40 개 문자열의 모든 삼중쌍)
    std::vector<std::string> small; for (const std::string& s : all) if (s.size() <= 3) small.push_back(s);
    assert(small.size() == 40);
    long osaViolations = 0, damViolations = 0;
    for (const std::string& x : small) for (const std::string& y : small) for (const std::string& z : small) { damViolations += damerau(x, z) > damerau(x, y) + damerau(y, z); osaViolations += osa(x, z) > osa(x, y) + osa(y, z); }
    assert(damViolations == 0 && osaViolations > 0);                  // 완전형은 거리 함수, OSA 는 아니다 (CA, AC, ABC)
    assert(osa("ca", "abc") > osa("ca", "ac") + osa("ac", "abc"));
    // ④ 오타: 무작위 편집 k 번으로 만든 문자열과의 거리는 k 이하
    std::mt19937 rng(17); long within = 0;
    for (int it = 0; it < 2000; ++it) {
        std::string w; for (int i = 0, n = 1 + (int)(rng() % 30); i < n; ++i) w += (char)('a' + rng() % 26);
        std::string t = w; int k = (int)(rng() % 6);
        for (int e = 0; e < k; ++e) {
            int op = (int)(rng() % 4); size_t p = t.empty() ? 0 : rng() % t.size();
            if (op == 0 && !t.empty()) t.erase(p, 1); else if (op == 1) t.insert(rng() % (t.size() + 1), 1, (char)('a' + rng() % 26)); else if (op == 2 && !t.empty()) t[p] = (char)('a' + rng() % 26); else if (t.size() > 1) std::swap(t[p % (t.size() - 1)], t[p % (t.size() - 1) + 1]);
        }
        assert(damerau(w, t) <= k && osa(w, t) <= levenshtein(w, t)); ++within;
    }
    std::cout << "OSA(CA,ABC)=" << osa("CA", "ABC") << " Damerau(CA,ABC)=" << damerau("CA", "ABC") << "; all " << pairs << " string pairs matched the BFS and top-down oracles, OSA exceeded the true distance on " << osaGap << " pairs and broke the triangle inequality " << osaViolations << " times" << std::endl;
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
#include <cassert>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <stack>
#include <stdexcept>
#include <string>
#include <vector>

// 톰프슨 구성: 정규식 -> 후위 표기 -> NFA.  연산자: | (선택)  * + ? (반복)  . (임의 한 글자)  ( ) (묶기)  연결은 암묵적
// 시뮬레이션은 "현재 상태 집합"을 글자마다 갱신하므로 백트래킹과 달리 항상 O(n·m) (지수 폭발 없음)
// 잘못된 식(괄호 불균형, 빈 가지, 맨 앞 반복 기호)은 예외로 거부한다
// 검증: ① 손으로 고른 식  ② 무작위 정규식 400 개(식 트리를 만들어 문자열로 찍음: 연산자 우선순위·중첩 반복 포함)를 *브르조조프스키 도함수* — 톰프슨 NFA 와 전혀 다른 알고리즘 — 로 같은 식 트리에서 판정한 결과와
//        {a,b,c} 위의 길이 ≤ 5 문자열 364 개 전부에서 비교  ③ 상태 집합 삽입 횟수 ≤ (n + 1)·상태 수 (선형 시간 증거), 상태 수 ≤ 2·|식| + 2  ④ 지수 폭발 입력과 잘못된 식 거부
const int SPLIT = 256, MATCH = 257, ANY = 258;
struct State { int c; int out = -1, out1 = -1; };
struct Patch { int s; int which; };
struct Frag { int start; std::vector<Patch> outs; };

bool wellFormed(const std::string& re) {
    if (re.empty()) return true;                                // 빈 식은 허용
    int depth = 0; char prev = '|';                                // prev = 직전 글자 ('|' 로 시작해 맨 앞 반복 기호를 거른다)
    for (char c : re) {
        if (c == '(') { ++depth; }
        else if (c == ')') { if (--depth < 0 || prev == '(' || prev == '|') return false; }
        else if (c == '|') { if (prev == '(' || prev == '|') return false; }
        else if (c == '*' || c == '+' || c == '?') { if (prev == '(' || prev == '|') return false; }
        prev = c;
    }
    return depth == 0 && prev != '|';
}
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
    mutable long inserts = 0;                                    // 상태 집합에 실제로 넣은 횟수 (분석용)
    void patch(const std::vector<Patch>& l, int target) { for (auto& p : l) (p.which ? st[p.s].out1 : st[p.s].out) = target; }
    int add(int c) { st.push_back({c}); return (int)st.size() - 1; }
    explicit NFA(const std::string& re) {
        if (!wellFormed(re)) throw std::invalid_argument("malformed regex");
        if (re.empty()) { start = add(MATCH); return; }          // 빈 식은 빈 문자열만 받아들인다
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
        S.insert(s); ++inserts;
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

// ---- 오라클: 식 트리 + 브르조조프스키 도함수 (NFA 와 공유하는 코드가 없다) ----
enum Kind { NONE, EPS, CHR, ANYC, CAT, ALT, STAR, PLUS, OPT };
struct Re; typedef std::shared_ptr<Re> P;
struct Re { Kind k; char c; P a, b; };
P mk(Kind k, char c = 0, P a = nullptr, P b = nullptr) { return std::make_shared<Re>(Re{k, c, a, b}); }
P cat(P a, P b) { if (a->k == NONE || b->k == NONE) return mk(NONE); if (a->k == EPS) return b; if (b->k == EPS) return a; return mk(CAT, 0, a, b); }
P alt(P a, P b) { if (a->k == NONE) return b; if (b->k == NONE) return a; return mk(ALT, 0, a, b); }
bool nullable(const P& r) {
    switch (r->k) { case EPS: case STAR: case OPT: return true; case CAT: return nullable(r->a) && nullable(r->b); case ALT: return nullable(r->a) || nullable(r->b); case PLUS: return nullable(r->a); default: return false; }
}
P deriv(const P& r, char ch) {
    switch (r->k) {
        case CHR: return r->c == ch ? mk(EPS) : mk(NONE);
        case ANYC: return mk(EPS);
        case CAT: { P d = cat(deriv(r->a, ch), r->b); return nullable(r->a) ? alt(d, deriv(r->b, ch)) : d; }
        case ALT: return alt(deriv(r->a, ch), deriv(r->b, ch));
        case STAR: return cat(deriv(r->a, ch), r);
        case PLUS: return cat(deriv(r->a, ch), mk(STAR, 0, r->a));
        case OPT: return deriv(r->a, ch);
        default: return mk(NONE);
    }
}
bool oracleMatch(P r, const std::string& s) { for (char ch : s) r = deriv(r, ch); return nullable(r); }
// 식 트리 -> 문자열: 우선순위(| < 연결 < 반복)에 필요한 곳에만 괄호
std::string show(const P& r, int ctx) {                              // ctx: 0 = 최상위/선택의 가지, 1 = 연결의 항, 2 = 반복의 대상
    std::string s; int mine;
    switch (r->k) {
        case CHR: return std::string(1, r->c);
        case ANYC: return ".";
        case CAT: s = show(r->a, 1) + show(r->b, 1); mine = 1; break;
        case ALT: s = show(r->a, 0) + "|" + show(r->b, 0); mine = 0; break;
        default: { s = show(r->a, 2) + (r->k == STAR ? "*" : r->k == PLUS ? "+" : "?"); mine = 3; }          // 반복 위의 반복 (a*)* 은 괄호로 감싼다
    }
    bool paren = (r->k == ALT && ctx >= 1) || (r->k == CAT && ctx >= 2) || (mine == 3 && ctx >= 2);
    return paren ? "(" + s + ")" : s;
}
P gen(std::mt19937& rng, int depth) {
    int r = (int)(rng() % 10);
    if (depth == 0 || r < 3) return rng() % 6 == 0 ? mk(ANYC) : mk(CHR, (char)('a' + rng() % 3));
    if (r < 5) return mk(CAT, 0, gen(rng, depth - 1), gen(rng, depth - 1));
    if (r < 7) return mk(ALT, 0, gen(rng, depth - 1), gen(rng, depth - 1));
    return mk(r == 7 ? STAR : r == 8 ? PLUS : OPT, 0, gen(rng, depth - 1));
}
int countNodes(const P& r) { return r ? 1 + countNodes(r->a) + countNodes(r->b) : 0; }

int main() {
    assert(NFA("a(b|c)*d").matches("abcbcd") && NFA("a(b|c)*d").matches("ad") && !NFA("a(b|c)*d").matches("abxd"));
    assert(NFA("colou?r").matches("color") && NFA("colou?r").matches("colour") && !NFA("colou?r").matches("colouur"));
    assert(NFA("(ab)+").matches("ababab") && !NFA("(ab)+").matches("") && !NFA("(ab)+").matches("aba"));
    assert(NFA("a.c").matches("abc") && !NFA("a.c").matches("ac"));
    assert(NFA("a*").matches("") && NFA("(a|b)*abb").matches("babaabb"));
    assert(NFA("ab|cd").matches("ab") && NFA("ab|cd").matches("cd") && !NFA("ab|cd").matches("abcd") && !NFA("ab|cd").matches("ad"));    // | 는 연결보다 약하다
    assert(NFA("ab*").matches("abbb") && !NFA("ab*").matches("abab") && NFA("(ab)*").matches("abab"));                                    // 반복은 직전 항에만
    assert(NFA("").matches("") && !NFA("").matches("a"));                                                                                 // 경계: 빈 식
    // 백트래킹 엔진이 지수 시간이 걸리는 (a*)*b 류의 입력도 선형 시간에 끝난다
    assert(!NFA("(a*)*b").matches(std::string(2000, 'a')) && NFA("(a*)*b").matches(std::string(2000, 'a') + "b"));
    NFA expo("(a|aa)+b"); assert(!expo.matches(std::string(3000, 'a')) && expo.inserts <= 3001L * (long)expo.st.size());
    // ④ 잘못된 식은 예외
    for (std::string bad : {"(", ")", "(a", "a)", "*a", "+", "a||b", "|a", "a|", "()", "(|a)", "(a|)", "a(*)"}) { bool threw = false; try { NFA n(bad); } catch (const std::invalid_argument&) { threw = true; } assert(threw); }
    for (std::string good : {"a", "a|b", "(a)", "((a))", "a**", "(a*)*", "a?+", ".", "a.b*"}) assert(wellFormed(good));

    // ② 무작위 식 400 개 × 길이 ≤ 5 문자열 364 개
    std::vector<std::string> strs{std::string()};
    for (size_t i = 0; i < strs.size(); ++i) if (strs[i].size() < 5) for (char c = 'a'; c <= 'c'; c++) strs.push_back(strs[i] + c);
    assert(strs.size() == 364);
    std::mt19937 rng(515); long accepted = 0, rejected = 0, maxStates = 0;
    for (int it = 0; it < 400; ++it) {
        P tree = gen(rng, 1 + (int)(rng() % 4)); std::string re = show(tree, 0); NFA nfa(re);
        assert(nfa.st.size() <= 2 * re.size() + 2); maxStates = std::max<long>(maxStates, (long)nfa.st.size());           // ③ 상태 수는 식 길이에 선형
        for (const std::string& s : strs) {
            nfa.inserts = 0; bool got = nfa.matches(s); assert(got == oracleMatch(tree, s));
            assert(nfa.inserts <= (long)(s.size() + 1) * (long)nfa.st.size());                                          // 글자마다 상태 집합에 상태는 많아야 한 번씩만
            (got ? accepted : rejected)++;
        }
    }
    assert(accepted > 5000 && rejected > 50000 && maxStates > 15);
    std::cout << "RegexNFA: 400 random regexes x 364 strings agreed with the derivative-based oracle (" << accepted << " accepted, " << rejected << " rejected); state-set work stayed within (n+1)*states; 13 malformed patterns rejected" << std::endl;
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
#include <algorithm>
#include <cassert>
#include <cctype>
#include <cmath>
#include <iostream>
#include <map>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

// 재귀 하강 파서: 문법 규칙 하나가 함수 하나.  연산자 우선순위는 문법의 계층(expr > term > factor)으로 표현된다
//   expr   := term   (('+' | '-') term)*
//   term   := factor (('*' | '/') factor)*
//   factor := NUMBER | IDENT | '(' expr ')' | '-' factor          NUMBER := 숫자+ ('.' 숫자+)?
// 반복(*)으로 쓴 expr/term 은 왼쪽 결합을 만든다.  오류는 모두 std::runtime_error 로 알린다 (너무 깊은 중첩, 큰 수, 0 으로 나눔 포함 — 스택 오버플로·다른 예외는 없다)
// 검증: ① 손으로 고른 식과 오류 표  ② 무작위 식 트리 6 000 개를 *우선순위·결합 규칙이 요구하는 최소 괄호* 와 불필요한 괄호·공백을 섞어 문자열로 찍고, 파서 결과를 식 트리를 직접 계산한 값과 비교
//        (0 으로 나누는 식은 둘 다 예외)  ③ 유효한 식을 한 글자씩 망가뜨린 변형 20 000 개: 값을 내거나 runtime_error 를 던질 뿐 다른 일은 일어나지 않는다  ④ 중첩 150 단계는 성공, 5 000 단계는 깔끔히 거부
class Parser {
    std::string s; size_t i = 0; int depth = 0; const std::map<std::string, double>& vars;
    void ws() { while (i < s.size() && std::isspace((unsigned char)s[i])) i++; }
    bool eat(char c) { ws(); if (i < s.size() && s[i] == c) { i++; return true; } return false; }
    struct Guard { int& d; explicit Guard(int& x) : d(x) { if (++d > 200) { --d; throw std::runtime_error("too deep"); } } ~Guard() { --d; } };
    double factor() {
        Guard g(depth); ws();
        if (eat('-')) return -factor();
        if (eat('(')) { double v = expr(); if (!eat(')')) throw std::runtime_error("expected )"); return v; }
        size_t j = i;
        if (j < s.size() && std::isdigit((unsigned char)s[j])) {
            while (j < s.size() && std::isdigit((unsigned char)s[j])) j++;
            if (j < s.size() && s[j] == '.') { j++; if (j >= s.size() || !std::isdigit((unsigned char)s[j])) throw std::runtime_error("bad number"); while (j < s.size() && std::isdigit((unsigned char)s[j])) j++; }
            double v; try { v = std::stod(s.substr(i, j - i)); } catch (const std::out_of_range&) { throw std::runtime_error("number out of range"); }
            i = j; return v;
        }
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

// ---- 오라클: 식 트리 ----
struct Ex { char op; double val; std::string name; int a, b; };            // op: n 수, v 변수, + - * /, ~ 단항 마이너스
std::vector<Ex> pool;
int mkN(const std::string& t) { pool.push_back({'n', std::stod(t), t, -1, -1}); return (int)pool.size() - 1; }
int mkV(const std::string& t) { pool.push_back({'v', 0, t, -1, -1}); return (int)pool.size() - 1; }
int mkB(char op, int a, int b) { pool.push_back({op, 0, "", a, b}); return (int)pool.size() - 1; }
int mkU(int a) { pool.push_back({'~', 0, "", a, -1}); return (int)pool.size() - 1; }
const std::map<std::string, double> VARS = {{"x", 3}, {"y", -2}, {"z", 0.5}, {"w1", 7}};
double evalTree(int e) {
    const Ex& n = pool[e];
    switch (n.op) {
        case 'n': return n.val; case 'v': return VARS.at(n.name); case '~': return -evalTree(n.a);
        case '+': { double l = evalTree(n.a); return l + evalTree(n.b); } case '-': { double l = evalTree(n.a); return l - evalTree(n.b); }
        case '*': { double l = evalTree(n.a); return l * evalTree(n.b); }
        default: { double l = evalTree(n.a), r = evalTree(n.b); if (r == 0) throw std::runtime_error("division by zero"); return l / r; }
    }
}
int prec(const Ex& n) { return n.op == '+' || n.op == '-' ? 1 : n.op == '*' || n.op == '/' ? 2 : n.op == '~' ? 3 : 4; }
std::mt19937 rng(606);
std::string sp() { return rng() % 3 == 0 ? " " : ""; }
std::string show(int e, int need) {                                         // need: 이 자리에서 괄호 없이 쓸 수 있는 최소 우선순위
    const Ex& n = pool[e]; std::string s;
    if (n.op == 'n' || n.op == 'v') s = n.name;
    else if (n.op == '~') s = "-" + sp() + show(n.a, 3);
    else { int p = prec(n); s = show(n.a, p) + sp() + n.op + sp() + show(n.b, p + 1); }      // 왼쪽 결합: 오른쪽 자식은 한 단계 높아야 괄호가 없다
    bool paren = prec(n) < need || (prec(n) >= 4 ? false : rng() % 8 == 0);                  // 필요한 괄호 + 가끔 불필요한 괄호
    return paren ? "(" + sp() + s + sp() + ")" : s;
}
int gen(int depth) {
    int r = (int)(rng() % 10);
    if (depth == 0 || r < 3) { static const char* nums[] = {"0", "1", "2", "3", "7", "9", "0.5", "2.5", "1.75", "12"}; static const char* vs[] = {"x", "y", "z", "w1"}; return rng() % 4 == 0 ? mkV(vs[rng() % 4]) : mkN(nums[rng() % 10]); }
    if (r == 3) return mkU(gen(depth - 1));
    return mkB("+-*/"[rng() % 4], gen(depth - 1), gen(depth - 1));
}

int main() {
    assert(eval("2 + 3 * 4") == 14);                             // 곱셈이 먼저
    assert(eval("(2 + 3) * 4") == 20);
    assert(eval("-(2 + 3)") == -5 && eval("2 * -3") == -6);
    assert(eval("10 / 4") == 2.5 && eval("2*3+4*5") == 26 && eval("8 - 3 - 2") == 3);   // 뺄셈은 왼쪽 결합
    assert(eval("64 / 4 / 2") == 8 && eval("2 - -3") == 5 && eval("---4") == -4 && eval("  7  ") == 7);
    assert(std::fabs(eval("x * (y + 1)", {{"x", 2.5}, {"y", 3}}) - 10) < 1e-12);
    for (std::string bad : {"", "   ", "+", "1 +", "(", ")", "(1 + 2", "1 + 2)", "1 2", "1 + * 2", "2 ** 3", "x", "1 / 0", "1 / (2 - 2)", "1..2", "1.", "2x", "(1)(2)", "-", "- -", "1 +* 3", "3 $ 4"}) {
        bool threw = false; try { eval(bad); } catch (const std::runtime_error&) { threw = true; } assert(threw);
    }
    // ② 무작위 식 트리
    long ok = 0, divZero = 0, parens = 0;
    for (int it = 0; it < 6000; ++it) {
        pool.clear(); int root = gen(1 + (int)(rng() % 5)); std::string text = show(root, 0); parens += (long)std::count(text.begin(), text.end(), '(');
        double want = 0; bool wantThrow = false; try { want = evalTree(root); } catch (const std::runtime_error&) { wantThrow = true; }
        try { double got = eval(text, VARS); assert(!wantThrow && got == want); ++ok; } catch (const std::runtime_error&) { assert(wantThrow); ++divZero; }
    }
    assert(ok > 4000 && divZero > 100 && parens > 5000);
    // ③ 망가뜨린 변형: 어떤 일이 일어나도 값 또는 runtime_error 뿐
    long mutantsOk = 0, mutantsErr = 0; const std::string junk = "+-*/(). x1w";
    for (int it = 0; it < 20000; ++it) {
        pool.clear(); std::string t = show(gen(3), 0); size_t p = rng() % (t.size() + 1);
        switch (rng() % 3) { case 0: if (!t.empty()) t.erase(p % t.size(), 1); break; case 1: t.insert(p, 1, junk[rng() % junk.size()]); break; default: if (t.size() > 1) std::swap(t[p % (t.size() - 1)], t[p % (t.size() - 1) + 1]); }
        try { eval(t, VARS); ++mutantsOk; } catch (const std::runtime_error&) { ++mutantsErr; }
    }
    assert(mutantsOk > 1000 && mutantsErr > 5000);
    // ④ 깊이와 큰 입력
    assert(eval(std::string(150, '(') + "1" + std::string(150, ')')) == 1);
    for (int depth : {5000, 100000}) { bool threw = false; try { eval(std::string(depth, '(') + "1" + std::string(depth, ')')); } catch (const std::runtime_error&) { threw = true; } assert(threw); }
    { bool threw = false; try { eval(std::string(5000, '-') + "1"); } catch (const std::runtime_error&) { threw = true; } assert(threw); }
    { bool threw = false; try { eval(std::string(400, '9')); } catch (const std::runtime_error&) { threw = true; } assert(threw); }          // 수가 너무 크다
    std::string longSum = "1"; for (int i = 0; i < 20000; ++i) longSum += "+1"; assert(eval(longSum) == 20001);                                // 반복은 재귀하지 않는다
    std::cout << "RecursiveDescentParser: 2 + 3 * 4 = " << eval("2 + 3 * 4") << "; " << ok << " random expressions matched direct tree evaluation (" << divZero << " division-by-zero cases threw), " << mutantsOk + mutantsErr << " corrupted inputs never misbehaved" << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(중첩 깊이)
```
# Part 15. 검색엔진
## InvertedIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cctype>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// 역색인(inverted index): 단어 -> 그 단어가 나오는 문서 번호 목록(포스팅 리스트, 정렬됨).  검색엔진의 핵심 자료구조
// AND 질의 = 정렬된 두 리스트의 교집합(병합식 O(a+b), 길이 차이가 크면 짧은 쪽 원소마다 긴 쪽을 *갤로핑* 탐색해 O(a log(b/a))),  OR = 합집합,  NOT = 차집합
// 위치까지 저장하므로 구절(phrase) 질의 "quick brown" 도 된다.  문서를 다시 넣으면 이전 내용을 지우고 갈아 끼운다 (문서 번호가 순서대로 들어오지 않아도 된다)
// 검증: ① 손으로 짠 예  ② 갤로핑 교집합을 std::set_intersection 과 대조(길이 0~300 의 무작위 정렬 리스트 2 000 쌍)하고, 5 개 vs 100 000 개의 비교 횟수가 선형 병합보다 훨씬 적음을 확인
//        ③ 문서 추가·교체·삭제 3 000 번을 섞으며 40 번 점검: 단일 단어·AND(2~3 단어)·OR·NOT·구절 질의를 문서별 토큰 열을 직접 훑는 오라클과 대조
long cmpSteps = 0;                                                    // 갤로핑이 한 비교 횟수 (분석용)
std::vector<int> intersect(const std::vector<int>& x, const std::vector<int>& y) {
    const std::vector<int>& a = x.size() <= y.size() ? x : y; const std::vector<int>& b = x.size() <= y.size() ? y : x;    // a: 짧은 쪽
    std::vector<int> r; size_t lo = 0;
    for (int v : a) {
        size_t step = 1, hi = lo;
        while (hi < b.size() && b[hi] < v) { ++cmpSteps; lo = hi + 1; hi += step; step <<= 1; }                              // 지수적으로 앞서 뛴다
        size_t l = lo, h = std::min(hi + 1, b.size());
        while (l < h) { ++cmpSteps; size_t m = (l + h) / 2; if (b[m] < v) l = m + 1; else h = m; }                           // 구간 안에서 이분 탐색
        lo = l;
        if (lo < b.size() && b[lo] == v) { r.push_back(v); ++lo; }
        if (lo >= b.size()) break;
    }
    return r;
}
class Index {
    std::map<std::string, std::map<int, std::vector<int>>> post;        // 단어 -> 문서 -> 위치 목록(오름차순)
    std::map<int, std::vector<std::string>> docs;                       // 문서 -> 토큰 열 (삭제·교체용)
    static std::vector<std::string> tokenize(const std::string& s) {
        std::vector<std::string> out; std::string w;
        for (unsigned char c : s) { if (std::isalnum(c)) w += (char)std::tolower(c); else if (!w.empty()) { out.push_back(w); w.clear(); } }
        if (!w.empty()) out.push_back(w);
        return out;
    }
public:
    void remove(int doc) {
        auto it = docs.find(doc); if (it == docs.end()) return;
        for (const std::string& w : it->second) { auto p = post.find(w); if (p == post.end()) continue; p->second.erase(doc); if (p->second.empty()) post.erase(p); }
        docs.erase(it);
    }
    void add(int doc, const std::string& text) {
        remove(doc); std::vector<std::string> toks = tokenize(text);
        for (size_t pos = 0; pos < toks.size(); pos++) post[toks[pos]][doc].push_back((int)pos);
        docs[doc] = toks;
    }
    std::vector<int> postings(const std::string& w) const { std::vector<int> r; auto it = post.find(w); if (it != post.end()) for (auto& kv : it->second) r.push_back(kv.first); return r; }
    std::vector<int> andQuery(std::vector<std::string> terms) const {   // 가장 짧은 목록부터 차례로 교집합
        if (terms.empty()) return {};
        std::vector<std::vector<int>> lists; for (auto& t : terms) lists.push_back(postings(t));
        std::sort(lists.begin(), lists.end(), [](const std::vector<int>& p, const std::vector<int>& q) { return p.size() < q.size(); });
        std::vector<int> r = lists[0]; for (size_t k = 1; k < lists.size() && !r.empty(); k++) r = intersect(r, lists[k]);
        return r;
    }
    std::vector<int> andQuery(const std::string& a, const std::string& b) const { return andQuery(std::vector<std::string>{a, b}); }
    std::vector<int> orQuery(const std::string& a, const std::string& b) const {
        std::vector<int> r; const auto x = postings(a), y = postings(b);
        std::set_union(x.begin(), x.end(), y.begin(), y.end(), std::back_inserter(r)); return r;
    }
    std::vector<int> notQuery(const std::string& a, const std::string& b) const {          // a 는 있고 b 는 없는 문서
        std::vector<int> r; const auto x = postings(a), y = postings(b);
        std::set_difference(x.begin(), x.end(), y.begin(), y.end(), std::back_inserter(r)); return r;
    }
    std::vector<int> phrase(const std::vector<std::string>& terms) const {                  // 단어들이 연속해서 나오는 문서
        std::vector<int> r; if (terms.empty()) return r;
        for (int d : andQuery(terms)) {
            const std::vector<int>& first = post.at(terms[0]).at(d);
            for (int p : first) { bool all = true; for (size_t k = 1; k < terms.size() && all; k++) { const std::vector<int>& pk = post.at(terms[k]).at(d); all = std::binary_search(pk.begin(), pk.end(), p + (int)k); } if (all) { r.push_back(d); break; } }
        }
        return r;
    }
    size_t vocabulary() const { return post.size(); }
    size_t docCount() const { return docs.size(); }
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
    assert((ix.notQuery("quick", "fox") == std::vector<int>{3}) && (ix.phrase({"quick", "brown"}) == std::vector<int>{1, 3}) && ix.phrase({"brown", "quick"}).empty() && (ix.phrase({"brown", "fox"}) == std::vector<int>{1}));
    ix.add(3, "Completely different text");                                                      // 문서 교체: 이전 단어의 포스팅에서 사라진다
    assert(ix.postings("barks").empty() && (ix.postings("quick") == std::vector<int>{1}) && ix.docCount() == 4);
    ix.remove(1); ix.remove(99); assert(ix.postings("fox").empty() && ix.docCount() == 3);
    Index emptyIx; assert(emptyIx.andQuery(std::vector<std::string>{}).empty() && emptyIx.postings("a").empty() && emptyIx.phrase({"a"}).empty() && emptyIx.vocabulary() == 0);

    // ② 갤로핑 교집합
    std::mt19937 rng(64); long checked = 0;
    for (int it = 0; it < 2000; ++it) {
        std::set<int> sa, sb; int na = (int)(rng() % 301), nb = (int)(rng() % 301), range = 1 + (int)(rng() % 600);
        for (int i = 0; i < na; ++i) sa.insert((int)(rng() % range)); for (int i = 0; i < nb; ++i) sb.insert((int)(rng() % range));
        std::vector<int> a(sa.begin(), sa.end()), b(sb.begin(), sb.end()), want; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(want));
        assert(intersect(a, b) == want && intersect(b, a) == want); ++checked;
    }
    std::vector<int> small = {7, 40000, 77777, 99998, 100001}, big; for (int i = 0; i < 100000; ++i) big.push_back(i * 2 + 1);          // 큰 쪽은 홀수 100 000 개
    cmpSteps = 0; std::vector<int> r = intersect(small, big);
    long bigSteps = cmpSteps; assert((r == std::vector<int>{7, 77777, 100001}) && bigSteps < 5 * 40);              // 선형 병합이면 약 10 만 번, 갤로핑은 원소당 O(log) 번
    // ③ 모델 대조
    const char* vocab[] = {"apple", "banana", "cherry", "date", "elder", "fig", "grape", "honey", "iris", "jade"}; const char* seps[] = {" ", ", ", ". ", "  ", "-", "! "};
    std::map<int, std::vector<std::string>> model; Index idx; long queries = 0, nonEmpty = 0;
    for (int step = 0; step < 3000; ++step) {
        int doc = (int)(rng() % 40), op = (int)(rng() % 10);
        if (op < 7) { std::vector<std::string> toks; std::string text; for (int k = 0, n = (int)(rng() % 13); k < n; ++k) { std::string w = vocab[rng() % 10]; toks.push_back(w); if (rng() % 3 == 0) w[0] = (char)std::toupper(w[0]); text += w; text += seps[rng() % 6]; } idx.add(doc, text); model[doc] = toks; }
        else { idx.remove(doc); model.erase(doc); }
        if (step % 75 != 0) continue;
        assert(idx.docCount() == model.size());
        for (int q = 0; q < 12; ++q) {
            std::vector<std::string> terms; for (int k = 0, n = 1 + (int)(rng() % 3); k < n; ++k) terms.push_back(vocab[rng() % 10]);
            std::vector<int> wantAnd, wantOr, wantNot, wantPhrase, wantTerm;
            for (auto& kv : model) {
                auto has = [&](const std::string& w) { return std::find(kv.second.begin(), kv.second.end(), w) != kv.second.end(); };
                bool all = true, any = false; for (auto& t : terms) { all = all && has(t); any = any || has(t); }
                if (all) wantAnd.push_back(kv.first); if (any) wantOr.push_back(kv.first);
                if (has(terms[0]) && !has(terms.back())) wantNot.push_back(kv.first); if (has(terms[0])) wantTerm.push_back(kv.first);
                for (size_t p = 0; p + terms.size() <= kv.second.size(); p++) { bool m = true; for (size_t k = 0; k < terms.size(); k++) m = m && kv.second[p + k] == terms[k]; if (m) { wantPhrase.push_back(kv.first); break; } }
            }
            std::vector<int> gotOr; { std::set<int> u; for (auto& t : terms) for (int d : idx.postings(t)) u.insert(d); gotOr.assign(u.begin(), u.end()); }
            assert(idx.postings(terms[0]) == wantTerm && idx.andQuery(terms) == wantAnd && gotOr == wantOr && idx.notQuery(terms[0], terms.back()) == wantNot && idx.phrase(terms) == wantPhrase);
            if (terms.size() == 2) { assert(idx.orQuery(terms[0], terms[1]) == wantOr && idx.andQuery(terms[0], terms[1]) == wantAnd); }
            ++queries; nonEmpty += !wantAnd.empty() + !wantPhrase.empty();
        }
    }
    assert(queries == 480 && nonEmpty > 100 && checked == 2000);
    std::cout << "InvertedIndex: " << checked << " galloping intersections matched set_intersection (5 vs 100000 took " << bigSteps << " comparisons); " << queries << " mixed queries over 3000 adds/replacements/removals matched the brute-force oracle" << std::endl;
    return 0;
}
// Time Complexity: 색인 O(총 토큰 수 log V), AND 질의 O(|짧은 목록| · log(|긴 목록| / |짧은 목록|))
// Space Complexity: O(총 토큰 수)
```
## NGramIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// n-gram 색인(bigram, trigram …): 단어를 글자 n 개 조각으로 나눠 색인하면 철자 오류가 있는 질의도 찾는다 (자동 교정, "이것을 찾으셨나요?").
// 질의와 후보의 n-gram 집합의 자카드 유사도 |A∩B| / |A∪B| 가 높은 단어를 고른다.  앞뒤에 '$' 를 n-1 개씩 붙여 첫·끝 글자도 n 개의 조각에 들어가게 한다
// 색인을 쓰면 질의와 조각을 하나라도 공유하는 후보만 본다 — 사전 전체를 훑을 필요가 없다
// 검증: ① 손으로 고른 예  ② 사전 전체를 훑는 브루트포스(집합 연산으로 자카드를 직접 계산)와 결과 *벡터가 정확히 같음* — n = 2, 3, 단어 중복 추가, 질의 3 000 개
//        ③ 사전 400 단어에서 한 글자 오타(치환·삭제·삽입·맞바꿈) 질의의 1 위가 원래 단어인 비율(n = 2 와 3 비교)과 검사한 후보 수가 사전 크기보다 훨씬 적음
std::set<std::string> grams(const std::string& w, int n) {
    std::string p = std::string(n - 1, '$') + w + std::string(n - 1, '$'); std::set<std::string> g;
    for (size_t i = 0; i + n <= p.size(); i++) g.insert(p.substr(i, n));
    return g;
}
class NGramIndex {
    int n; std::map<std::string, std::vector<int>> idx; std::vector<std::string> words; std::set<std::string> seen;
public:
    mutable size_t candidates = 0;                                     // 마지막 질의에서 검사한 후보 수 (분석용)
    explicit NGramIndex(int n = 2) : n(n) {}
    void add(const std::string& w) {
        if (!seen.insert(w).second) return;                            // 같은 단어를 두 번 넣어도 한 번만
        int id = (int)words.size(); words.push_back(w); for (auto& g : grams(w, n)) idx[g].push_back(id);
    }
    std::vector<std::pair<double, std::string>> search(const std::string& q, double minSim = 0.3) const {
        assert(minSim > 0);                                            // 조각을 하나도 공유하지 않는 단어(유사도 0)는 색인으로 찾을 수 없다
        std::map<int, int> common; auto qg = grams(q, n);
        for (auto& g : qg) { auto it = idx.find(g); if (it != idx.end()) for (int id : it->second) common[id]++; }   // 공통 조각 수만 센다
        candidates = common.size();
        std::vector<std::pair<double, std::string>> r;
        for (auto& kv : common) {
            double sim = double(kv.second) / (qg.size() + grams(words[kv.first], n).size() - kv.second);
            if (sim >= minSim) r.push_back({sim, words[kv.first]});
        }
        std::sort(r.rbegin(), r.rend()); return r;
    }
    size_t size() const { return words.size(); }
};
std::vector<std::pair<double, std::string>> bruteForce(const std::vector<std::string>& dict, const std::string& q, int n, double minSim) {
    std::set<std::string> uniq(dict.begin(), dict.end()); auto qg = grams(q, n); std::vector<std::pair<double, std::string>> r;
    for (const std::string& w : uniq) {
        auto g = grams(w, n); std::vector<std::string> inter, uni; std::set_intersection(qg.begin(), qg.end(), g.begin(), g.end(), std::back_inserter(inter)); std::set_union(qg.begin(), qg.end(), g.begin(), g.end(), std::back_inserter(uni));
        double sim = double(inter.size()) / uni.size(); if (inter.size() > 0 && sim >= minSim) r.push_back({sim, w});
    }
    std::sort(r.rbegin(), r.rend()); return r;
}
std::string typo(const std::string& w, std::mt19937& rng) {              // 한 글자 오타 하나
    std::string t = w; size_t p = rng() % t.size();
    switch (rng() % 4) {
        case 0: { char c; do c = (char)('a' + rng() % 26); while (c == t[p]); t[p] = c; break; }
        case 1: t.erase(p, 1); break;
        case 2: t.insert(rng() % (t.size() + 1), 1, (char)('a' + rng() % 26)); break;
        default: { size_t q = p % (t.size() - 1); if (t[q] != t[q + 1]) std::swap(t[q], t[q + 1]); else t[q] = (char)('a' + (t[q] - 'a' + 1) % 26); }
    }
    return t;
}

int main() {
    NGramIndex ix;
    for (auto w : {"receive", "relative", "achieve", "deceive", "believe", "banana"}) ix.add(w);
    auto r = ix.search("recieve");                                    // 'ie' <-> 'ei' 오타
    assert(!r.empty() && r[0].second == "receive");
    auto none = ix.search("zzzz");
    assert(none.empty());
    assert(grams("ab", 2) == (std::set<std::string>{"$a", "ab", "b$"}) && grams("ab", 3) == (std::set<std::string>{"$$a", "$ab", "ab$", "b$$"}) && grams("", 2) == (std::set<std::string>{"$$"}));      // 경계: 조각 구성, 빈 단어
    ix.add("receive"); assert(ix.size() == 6 && ix.search("receive")[0].first == 1.0);                                       // 중복 추가는 무시, 완전 일치는 유사도 1

    // ② 브루트포스 대조
    std::mt19937 rng(88); std::vector<std::string> dict;
    for (int i = 0; i < 400; ++i) { std::string w; for (int k = 0, len = 4 + (int)(rng() % 7); k < len; ++k) w += (char)('a' + rng() % 26); dict.push_back(w); }
    for (int i = 0; i < 40; ++i) dict.push_back(dict[rng() % 400]);                                                      // 중복 단어
    long compared = 0;
    for (int n : {2, 3}) {
        NGramIndex big(n); for (auto& w : dict) big.add(w);
        for (int q = 0; q < 1500; ++q) {
            std::string query = q % 3 == 0 ? typo(dict[rng() % 400], rng) : q % 3 == 1 ? dict[rng() % 400] : std::string(3 + rng() % 5, 'a') + (char)('a' + rng() % 26);
            double minSim = q % 2 ? 0.2 : 0.35;
            auto got = big.search(query, minSim), want = bruteForce(dict, query, n, minSim); assert(got == want); ++compared;
        }
    }
    // ③ 오타 교정 정확도와 후보 수
    double hits[2] = {0, 0}, cands[2] = {0, 0}; int trials = 1000;
    for (int k = 0; k < 2; ++k) {
        int n = k + 2; NGramIndex big(n); std::vector<std::string> uniq(dict.begin(), dict.begin() + 400); for (auto& w : uniq) big.add(w);
        std::mt19937 trng(5); int counted = 0;
        for (int t = 0; t < trials; ++t) {
            const std::string& w = uniq[trng() % 400]; if (w.size() < 5) continue; std::string q = typo(w, trng);
            auto res = big.search(q, 0.01); ++counted; cands[k] += (double)big.candidates;
            if (!res.empty() && res[0].second == w) hits[k] += 1;
        }
        hits[k] /= counted; cands[k] /= counted;
    }
    assert(hits[0] > 0.85 && hits[1] > 0.85 && cands[0] < 400 / 3.0 && cands[1] < cands[0]);        // 3-gram 은 후보가 더 적다
    std::cout << "NGramIndex: 'recieve' -> " << r[0].second << " (similarity " << r[0].first << "); " << compared << " queries matched brute force; top-1 recovery of one-letter typos " << hits[0] << " (bigram, " << cands[0] << " candidates of 400) vs " << hits[1] << " (trigram, " << cands[1] << ")" << std::endl;
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <utility>
#include <vector>

// DNA 는 알파벳 {A, C, G, T} 의 문자열이다(N 은 미확정 염기). 기본 연산: 역상보 서열, GC 함량, k-mer 개수 세기, 제한효소 인식 부위(모티프) 찾기·절단, 단백질 번역과 ORF 찾기
// 역상보: 반대 가닥은 서열을 뒤집고 A<->T, C<->G 를 바꾼 것.  제한효소 부위는 대개 역상보와 같은 회문형(GAATTC)
// 검증: ① 손으로 고른 값(EcoRI 부위 5·23, 번역 MAIVMGR*KGAR*)  ② 무작위 서열에서 k-mer 세기를 map 판과 2 비트 롤링 판이 일치(k 1~8, N 포함), 정규(canonical) k-mer 개수는 서열과 그 역상보에서 같음
//        ③ 역상보 회문 부위(길이 4~12)를 중심 확장으로 찾은 결과 = 모든 부분 문자열 전수 검사  ④ 효소 절단 조각을 이어 붙이면 원래 서열  ⑤ 코돈 표의 축퇴도(L·S·R 6, 정지 3, M·W 1 …)와 6 개 읽기틀 ORF 찾기를 독립 구현(ATG 마다 거꾸로 훑기)과 대조
std::string reverseComplement(const std::string& dna) {
    std::string r(dna.rbegin(), dna.rend());
    for (char& c : r) switch (c) { case 'A': c = 'T'; break; case 'T': c = 'A'; break; case 'C': c = 'G'; break; case 'G': c = 'C'; break; default: assert(c == 'N'); }
    return r;
}
double gcContent(const std::string& dna) { return dna.empty() ? 0.0 : double(std::count(dna.begin(), dna.end(), 'G') + std::count(dna.begin(), dna.end(), 'C')) / dna.size(); }
bool acgt(const std::string& s) { return s.find_first_not_of("ACGT") == std::string::npos; }
std::map<std::string, int> kmers(const std::string& dna, int k) { std::map<std::string, int> m; for (size_t i = 0; i + k <= dna.size(); i++) { std::string w = dna.substr(i, k); if (acgt(w)) m[w]++; } return m; }
int baseVal(char c) { return c == 'A' ? 0 : c == 'C' ? 1 : c == 'G' ? 2 : c == 'T' ? 3 : -1; }
std::map<std::string, int> kmersRolling(const std::string& dna, int k) {      // 2 비트 롤링: 새 글자를 밀어 넣어 O(1) 갱신, N 을 만나면 창을 비운다
    std::vector<int> cnt(1u << (2 * k), 0); unsigned code = 0, mask = (1u << (2 * k)) - 1; int run = 0;
    for (char c : dna) { int v = baseVal(c); if (v < 0) { run = 0; code = 0; continue; } code = ((code << 2) | (unsigned)v) & mask; if (++run >= k) cnt[code]++; }
    std::map<std::string, int> m;
    for (unsigned c = 0; c < cnt.size(); c++) if (cnt[c]) { std::string w; for (int b = k - 1; b >= 0; b--) w += "ACGT"[(c >> (2 * b)) & 3]; m[w] = cnt[c]; }
    return m;
}
std::map<std::string, int> canonicalKmers(const std::string& dna, int k) { std::map<std::string, int> m; for (auto& kv : kmers(dna, k)) m[std::min(kv.first, reverseComplement(kv.first))] += kv.second; return m; }
std::vector<std::pair<size_t, size_t>> reversePalindromes(const std::string& dna, size_t minLen, size_t maxLen) {    // (시작, 길이): 부분 문자열 = 그 역상보
    std::vector<std::pair<size_t, size_t>> r;
    for (size_t c = 1; c < dna.size(); c++)                                // 중심은 c-1 과 c 사이
        for (size_t t = 0; c >= t + 1 && c + t < dna.size(); t++) {
            char a = dna[c - 1 - t], b = dna[c + t]; int va = baseVal(a), vb = baseVal(b);
            if (va < 0 || vb < 0 || va + vb != 3) break;                   // 서로 상보(A-T, C-G) 가 아니면 더 못 넓힌다
            size_t len = 2 * (t + 1); if (len > maxLen) break; if (len >= minLen) r.push_back({c - 1 - t, len});
        }
    std::sort(r.begin(), r.end()); return r;
}
std::vector<std::string> digest(const std::string& dna, const std::string& site, size_t cutAfter) {   // site 안에서 cutAfter 글자 뒤를 자른다 (EcoRI: G^AATTC -> 1)
    std::vector<size_t> cuts;
    for (size_t p = dna.find(site); p != std::string::npos; p = dna.find(site, p + 1)) cuts.push_back(p + cutAfter);
    std::vector<std::string> frags; size_t prev = 0;
    for (size_t c : cuts) { frags.push_back(dna.substr(prev, c - prev)); prev = c; }
    frags.push_back(dna.substr(prev)); return frags;
}
const char* CODONS = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG";       // 표준 유전 암호, 순서 T C A G
int tcag(char c) { return c == 'T' ? 0 : c == 'C' ? 1 : c == 'A' ? 2 : 3; }
char aminoAcid(const std::string& s, size_t i) { return CODONS[16 * tcag(s[i]) + 4 * tcag(s[i + 1]) + tcag(s[i + 2])]; }
std::string translate(const std::string& dna) { std::string p; for (size_t i = 0; i + 3 <= dna.size(); i += 3) p += acgt(dna.substr(i, 3)) ? aminoAcid(dna, i) : 'X'; return p; }
struct ORF { int strand; size_t start, nt; std::string protein; bool operator<(const ORF& o) const { return std::tie(strand, start, nt) < std::tie(o.strand, o.start, o.nt); } bool operator==(const ORF& o) const { return strand == o.strand && start == o.start && nt == o.nt && protein == o.protein; } };
std::vector<ORF> findOrfs(const std::string& dna) {                          // 6 개 읽기틀: 틀마다 전체를 번역한 뒤 '*' 사이에서 첫 'M' 부터 정지 코돈까지
    std::vector<ORF> r;
    for (int strand : {1, -1}) {
        std::string s = strand == 1 ? dna : reverseComplement(dna);
        for (size_t f = 0; f < 3 && f < s.size(); f++) {
            std::string prot = translate(s.substr(f)); size_t i = 0;
            while (i < prot.size()) {
                size_t m = prot.find('M', i); if (m == std::string::npos) break;
                size_t e = prot.find_first_of("*X", m); if (e == std::string::npos) break;  // 정지 코돈이 없는 미완성 ORF 는 버린다
                if (prot[e] == '*') r.push_back({strand, f + 3 * m, 3 * (e - m + 1), prot.substr(m, e - m)});          // 'X'(N 이 낀 코돈)를 만나면 그 ORF 는 확정할 수 없어 버린다
                i = e + 1;
            }
        }
    }
    std::sort(r.begin(), r.end()); return r;
}
std::vector<ORF> findOrfsBrute(const std::string& dna) {                       // 독립 구현: ATG 위치마다 정지 코돈까지 훑고, 같은 틀에서 그 앞에 ATG 가 없을 때만 보고
    std::vector<ORF> r;
    for (int strand : {1, -1}) {
        std::string s = strand == 1 ? dna : reverseComplement(dna);
        for (size_t p = 0; p + 3 <= s.size(); p++) {
            if (s.compare(p, 3, "ATG") != 0) continue;
            size_t q = p; while (q + 3 <= s.size() && aminoAcid(s, q) != '*' && acgt(s.substr(q, 3))) q += 3;
            if (q + 3 > s.size() || aminoAcid(s, q) != '*' || !acgt(s.substr(q, 3))) continue;
            bool firstInSegment = true;                                            // 거꾸로 올라가며 정지 코돈 전에 ATG 가 있는지 본다
            for (size_t b = p; b >= 3; ) { b -= 3; if (!acgt(s.substr(b, 3)) || aminoAcid(s, b) == '*') break; if (s.compare(b, 3, "ATG") == 0) { firstInSegment = false; break; } }
            if (firstInSegment) r.push_back({strand, p, q + 3 - p, translate(s.substr(p, q - p))});
        }
    }
    std::sort(r.begin(), r.end()); return r;
}
std::string randomDna(std::mt19937& rng, size_t n, bool withN) { std::string s(n, 'A'); for (char& c : s) c = withN && rng() % 20 == 0 ? 'N' : "ACGT"[rng() % 4]; return s; }

int main() {
    std::string dna = "AGCTTGAATTCGGATCCAAGCTTGAATTC";
    assert(reverseComplement("ATGC") == "GCAT");
    assert(reverseComplement(reverseComplement(dna)) == dna);        // 역상보의 역상보는 원래 서열
    assert(reverseComplement("GAATTC") == "GAATTC");                 // 제한효소 EcoRI 부위는 회문형 (역상보와 같다)
    assert(reverseComplement("") == "" && reverseComplement("ANT") == "ANT" && gcContent("") == 0.0);
    assert(std::abs(gcContent("GGCC") - 1.0) < 1e-12 && std::abs(gcContent("ATGC") - 0.5) < 1e-12);
    auto k = kmers(dna, 6);
    assert(k["GAATTC"] == 2);                                        // EcoRI 인식 부위가 두 번
    std::vector<size_t> sites; for (size_t p = dna.find("GAATTC"); p != std::string::npos; p = dna.find("GAATTC", p + 1)) sites.push_back(p);
    assert((sites == std::vector<size_t>{5, 23}));
    std::vector<std::string> frags = digest(dna, "GAATTC", 1); assert((frags == std::vector<std::string>{"AGCTTG", "AATTCGGATCCAAGCTTG", "AATTC"}));          // G^AATTC
    assert(translate("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG") == "MAIVMGR*KGAR*");
    std::map<char, int> degeneracy; for (int i = 0; i < 64; i++) degeneracy[CODONS[i]]++;
    assert(degeneracy['L'] == 6 && degeneracy['S'] == 6 && degeneracy['R'] == 6 && degeneracy['*'] == 3 && degeneracy['I'] == 3 && degeneracy['M'] == 1 && degeneracy['W'] == 1 && degeneracy['A'] == 4 && degeneracy.size() == 21);
    assert(aminoAcid("ATG", 0) == 'M' && aminoAcid("TAA", 0) == '*' && aminoAcid("TAG", 0) == '*' && aminoAcid("TGA", 0) == '*' && aminoAcid("TGG", 0) == 'W' && aminoAcid("GGG", 0) == 'G' && aminoAcid("TTT", 0) == 'F');
    // ② k-mer 세기
    std::mt19937 rng(2025); long kmerChecks = 0;
    for (int it = 0; it < 300; ++it) {
        std::string s = randomDna(rng, rng() % 400, it % 2 == 0); int kk = 1 + (int)(rng() % 8);
        auto a = kmers(s, kk), b = kmersRolling(s, kk); assert(a == b); ++kmerChecks;
        long total = 0; for (auto& kv : a) total += kv.second; long windows = 0; for (size_t i = 0; i + kk <= s.size(); i++) windows += acgt(s.substr(i, kk)); assert(total == windows);
        std::string rc = reverseComplement(s); assert(canonicalKmers(s, kk) == canonicalKmers(rc, kk));          // 두 가닥에서 같은 정규 k-mer 개수
        auto mk = kmers(rc, kk); for (auto& kv : a) { auto it2 = mk.find(reverseComplement(kv.first)); assert(it2 != mk.end() && it2->second == kv.second); }
    }
    // ③ 회문 부위 ④ 절단
    long palTotal = 0, fragChecks = 0;
    for (int it = 0; it < 300; ++it) {
        std::string s = randomDna(rng, 20 + rng() % 120, it % 3 == 0); auto got = reversePalindromes(s, 4, 12); palTotal += (long)got.size();
        std::vector<std::pair<size_t, size_t>> want; for (size_t len = 4; len <= 12; len += 2) for (size_t i = 0; i + len <= s.size(); i++) { std::string w = s.substr(i, len); if (acgt(w) && w == reverseComplement(w)) want.push_back({i, len}); }
        std::sort(want.begin(), want.end()); assert(got == want);
        for (const char* site : {"GAATTC", "GGATCC", "AAGCTT"}) { auto f = digest(s + site + s, site, 1); std::string joined; for (auto& x : f) joined += x; assert(joined == s + site + s && f.size() >= 2); ++fragChecks; }
    }
    assert(palTotal > 300 && reversePalindromes("GAATTC", 4, 12).size() == 2);                              // GAATTC 와 그 안의 AATT
    // ⑤ ORF
    std::string planted = "CC" + std::string("ATGGCCATTGTAATGGGCCGCTGA") + "TT"; auto orfs = findOrfs(planted);
    assert(std::find(orfs.begin(), orfs.end(), ORF{1, 2, 24, "MAIVMGR"}) != orfs.end());                    // 안쪽의 두 번째 ATG 는 같은 ORF 에 포함되어 따로 보고하지 않는다
    long orfTotal = 0;
    for (int it = 0; it < 400; ++it) { std::string s = randomDna(rng, 30 + rng() % 400, it % 4 == 0); auto a = findOrfs(s), b = findOrfsBrute(s); assert(a == b); orfTotal += (long)a.size(); }
    assert(orfTotal > 300 && findOrfs("").empty() && findOrfs("AT").empty());
    std::cout << "EcoRI sites at positions " << sites[0] << " and " << sites[1] << ", GC=" << gcContent(dna) << "; " << kmerChecks << " k-mer tables matched across two counters, " << palTotal << " palindromic sites and " << orfTotal << " ORFs matched their brute-force oracles" << std::endl;
    return 0;
}
// Time Complexity: O(n) (k-mer 세기 O(n·k), 롤링은 O(n))
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
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// BPE: 글자 단위에서 시작해 "가장 자주 붙어 나오는 인접 쌍"을 하나의 새 토큰으로 합치는 일을 반복해 어휘를 학습한다 (GPT 계열).
// 추론은 학습된 병합을 "학습된 순서대로" 적용한다.  단어 끝 표식 </w> 로 단어 경계를 보존.  동률은 사전순으로 앞선 쌍
// 같은 결과를 내는 두 번째 추론: "지금 이웃한 쌍 중 순위(병합 순번)가 가장 낮은 것을 먼저 합친다" (GPT-2 방식, 병합 목록을 한 번씩 다 훑지 않아도 된다)
// 검증: ① Sennrich 외(2016)의 예 12 병합 전체 (파이썬으로 따로 계산한 값)  ② 병합마다 코퍼스의 총 토큰 수가 *엄격히* 줄고 그 감소량은 1 이상 병합된 쌍의 빈도 이하
//        ③ 무작위 코퍼스 300 개: 문자열 기반 학습기와 *정수 ID 기반* 독립 학습기의 병합 목록이 같고, 학습 단어를 다시 인코딩하면 학습 마지막의 분할과 같으며,
//        순서대로 적용한 추론 = 순위 우선 추론, 처음 보는 단어도 이어 붙이면 원문(+</w>)  ④ 경계: 빈 코퍼스, 병합 수 0, 한 글자 단어
typedef std::vector<std::string> Seq;
typedef std::pair<std::string, std::string> Pair;

std::vector<Pair> train(const std::map<std::string, int>& wordFreq, int numMerges, std::vector<long>* totals = nullptr, std::vector<long>* chosen = nullptr, std::map<std::string, Seq>* finalSeg = nullptr) {
    std::map<Seq, int> vocab;
    for (auto& kv : wordFreq) { Seq s; for (char c : kv.first) s.push_back(std::string(1, c)); s.push_back("</w>"); vocab[s] += kv.second; }
    auto total = [&]() { long t = 0; for (auto& kv : vocab) t += (long)kv.first.size() * kv.second; return t; };
    if (totals) totals->push_back(total());
    std::vector<Pair> merges;
    for (int it = 0; it < numMerges; it++) {
        std::map<Pair, int> cnt;
        for (auto& kv : vocab) for (size_t i = 0; i + 1 < kv.first.size(); i++) cnt[{kv.first[i], kv.first[i + 1]}] += kv.second;
        if (cnt.empty()) break;
        Pair best; int bc = 0;
        for (auto& kv : cnt) if (kv.second > bc) { bc = kv.second; best = kv.first; }     // 빈도 최대, 동률이면 사전순 앞쪽
        merges.push_back(best); if (chosen) chosen->push_back(bc);
        std::map<Seq, int> next;
        for (auto& kv : vocab) {
            Seq s; for (size_t i = 0; i < kv.first.size(); i++) {
                if (i + 1 < kv.first.size() && kv.first[i] == best.first && kv.first[i + 1] == best.second) { s.push_back(best.first + best.second); i++; }
                else s.push_back(kv.first[i]);
            }
            next[s] += kv.second;
        }
        vocab.swap(next);
        if (totals) totals->push_back(total());
    }
    if (finalSeg) for (auto& kv : wordFreq) {                                            // 학습 마지막의 분할: 단어를 병합 목록으로 다시 계산하지 않고 vocab 에서 찾기 위해 한 번 더 적용
        Seq s; for (char c : kv.first) s.push_back(std::string(1, c)); s.push_back("</w>");
        for (auto& m : merges) { Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == m.first && s[i + 1] == m.second) { t.push_back(m.first + m.second); i++; } else t.push_back(s[i]); } s.swap(t); }
        (*finalSeg)[kv.first] = s;
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
Seq encodeRank(const std::string& word, const std::map<Pair, int>& rank) {            // 순위가 가장 낮은 이웃 쌍을 (모든 위치에서) 합치기를 더 합칠 것이 없을 때까지
    Seq s; for (char c : word) s.push_back(std::string(1, c)); s.push_back("</w>");
    for (;;) {
        int best = INT_MAX; Pair bp;
        for (size_t i = 0; i + 1 < s.size(); i++) { auto it = rank.find({s[i], s[i + 1]}); if (it != rank.end() && it->second < best) { best = it->second; bp = it->first; } }
        if (best == INT_MAX) return s;
        Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == bp.first && s[i + 1] == bp.second) { t.push_back(bp.first + bp.second); i++; } else t.push_back(s[i]); }
        s.swap(t);
    }
}
std::vector<Pair> trainIds(const std::map<std::string, int>& wf, int numMerges) {     // 독립 구현: 토큰을 정수 ID 로 바꿔 쌍 개수를 센다 (동률 규칙은 ID 가 아니라 *문자열 쌍* 의 사전순)
    std::vector<std::string> tok; std::map<std::string, int> id;
    auto intern = [&](const std::string& s) { auto it = id.find(s); if (it != id.end()) return it->second; tok.push_back(s); return id[s] = (int)tok.size() - 1; };
    std::vector<std::vector<int>> words; std::vector<long> fr;
    for (auto& kv : wf) { std::vector<int> w; for (char c : kv.first) w.push_back(intern(std::string(1, c))); w.push_back(intern("</w>")); words.push_back(w); fr.push_back(kv.second); }
    std::vector<Pair> merges;
    for (int it = 0; it < numMerges; it++) {
        std::map<std::pair<int, int>, long> cnt;
        for (size_t w = 0; w < words.size(); w++) for (size_t i = 0; i + 1 < words[w].size(); i++) cnt[{words[w][i], words[w][i + 1]}] += fr[w];
        if (cnt.empty()) break;
        std::pair<int, int> best{-1, -1}; long bc = 0;
        for (auto& kv : cnt) {
            bool better = kv.second > bc || (kv.second == bc && Pair{tok[kv.first.first], tok[kv.first.second]} < Pair{tok[best.first], tok[best.second]});
            if (better) { bc = kv.second; best = kv.first; }
        }
        merges.push_back({tok[best.first], tok[best.second]});
        int nid = intern(tok[best.first] + tok[best.second]);
        for (auto& w : words) { std::vector<int> t; for (size_t i = 0; i < w.size(); i++) { if (i + 1 < w.size() && w[i] == best.first && w[i + 1] == best.second) { t.push_back(nid); i++; } else t.push_back(w[i]); } w.swap(t); }
    }
    return merges;
}

int main() {
    std::map<std::string, int> corpus = {{"low", 5}, {"lower", 2}, {"newest", 6}, {"widest", 3}};     // Sennrich et al. (2016) 의 예
    std::vector<long> totals, counts; std::map<std::string, Seq> finalSeg;
    auto merges = train(corpus, 12, &totals, &counts, &finalSeg);
    assert((merges[0] == Pair{"e", "s"}) && (merges[1] == Pair{"es", "t"}) && (merges[2] == Pair{"est", "</w>"}));   // 빈도 9 인 쌍부터
    const std::vector<Pair> golden = {{"e", "s"}, {"es", "t"}, {"est", "</w>"}, {"l", "o"}, {"lo", "w"}, {"e", "w"}, {"ew", "est</w>"}, {"n", "ewest</w>"}, {"low", "</w>"}, {"d", "est</w>"}, {"i", "dest</w>"}, {"w", "idest</w>"}};
    assert(merges == golden && trainIds(corpus, 12) == golden);                              // 문자열 기반, ID 기반 학습기, 파이썬 참조값이 모두 같다
    assert((counts == std::vector<long>{9, 9, 9, 7, 7, 6, 6, 6, 5, 3, 3, 3}));
    Seq e = encode("newest", merges);
    auto endsWithEst = [](const std::string& s) { return s.size() >= 7 && s.compare(s.size() - 7, 7, "est</w>") == 0; };
    assert(endsWithEst(e.back()));                                     // "newest" 는 est</w> 로 끝나는 (더 큰) 토큰으로 끝난다
    Seq u = encode("lowest", merges);                                  // 학습에 없던 단어도 학습된 조각으로 분해된다
    assert(endsWithEst(u.back()) && u.size() >= 2);
    std::string joined; for (auto& t : u) joined += t;
    assert(joined == "lowest</w>");                                    // 이어 붙이면 원문 (+ 단어 끝 표식)
    for (auto& kv : corpus) assert(encode(kv.first, merges) == finalSeg[kv.first]);
    // ② 병합마다 총 토큰 수 감소
    for (size_t i = 0; i < counts.size(); i++) { long dec = totals[i] - totals[i + 1]; assert(dec >= 1 && dec <= counts[i]); }

    // ③ 무작위 코퍼스
    std::mt19937 rng(41); long corpora = 0, mergesTotal = 0, strict = 0;
    for (int it = 0; it < 300; ++it) {
        std::map<std::string, int> wf; int sigma = 2 + (int)(rng() % 3);
        for (int w = 0, n = 1 + (int)(rng() % 12); w < n; ++w) { std::string s; for (int k = 0, len = 1 + (int)(rng() % 8); k < len; ++k) s += (char)('a' + rng() % sigma); wf[s] += 1 + (int)(rng() % 5); }
        int M = (int)(rng() % 25); std::vector<long> tot, cnt; std::map<std::string, Seq> fin;
        auto m1 = train(wf, M, &tot, &cnt, &fin), m2 = trainIds(wf, M); assert(m1 == m2);
        std::map<Pair, int> rank; for (size_t i = 0; i < m1.size(); i++) rank.emplace(m1[i], (int)i);          // 같은 쌍이 두 번 나올 수는 없다 (한 번 합치면 그 쌍은 사라진다)
        assert(rank.size() == m1.size());
        for (size_t i = 0; i < cnt.size(); i++) { long dec = tot[i] - tot[i + 1]; assert(dec >= 1 && dec <= cnt[i]); strict += dec == cnt[i]; if (i) assert(cnt[i] <= cnt[i - 1]); }
        for (auto& kv : wf) assert(encode(kv.first, m1) == fin[kv.first] && encodeRank(kv.first, rank) == fin[kv.first]);   // 학습 단어: 학습 마지막의 분할과 같다
        for (int q = 0; q < 10; ++q) {                                                                   // 처음 보는 단어(알파벳 밖 글자 포함)
            std::string w; for (int k = 0, len = 1 + (int)(rng() % 10); k < len; ++k) w += (char)('a' + rng() % (sigma + 1));
            Seq a = encode(w, m1), b = encodeRank(w, rank); assert(a == b);
            std::string j; for (auto& t : a) j += t; assert(j == w + "</w>");
        }
        ++corpora; mergesTotal += (long)m1.size();
    }
    assert(corpora == 300 && mergesTotal > 2000 && strict > 1000);
    // ④ 경계
    assert(train({}, 5).empty() && train(corpus, 0).empty() && trainIds({}, 5).empty());
    auto single = train({{"a", 3}}, 5); assert((single == std::vector<Pair>{{"a", "</w>"}}) && encode("a", single) == Seq{"a</w>"} && encode("", single) == Seq{"</w>"});
    std::cout << "BPE merges: "; for (int i = 0; i < 5; i++) std::cout << merges[i].first << "+" << merges[i].second << " "; std::cout << "(" << corpora << " random corpora, " << mergesTotal << " merges: two independent trainers and two inference orders agreed)" << std::endl;
    return 0;
}
// Time Complexity: 학습 O(병합 수 · 코퍼스 크기), 추론 O(병합 수 · 단어 길이)
// Space Complexity: O(어휘)
```
## WordPiece()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// WordPiece(BERT): 추론은 "가장 긴 일치 우선(MaxMatch)" 탐욕 방식이다. 단어 중간 조각에는 "##" 접두사를 붙인다.
// 학습은 BPE 와 달리 빈도가 아니라 점수 score(a, b) = freq(ab) / (freq(a) · freq(b)) 가 가장 큰 쌍을 합친다
//  -> 서로 자주 같이 나오지만 각자는 드문 쌍을 선호 (우도 기반)
// 탐욕 추론은 되돌아가지 않으므로 분할이 존재해도 [UNK] 를 낼 수 있다: 어휘 {a, ##bc, ab} 에서 "abc" 는 ab 를 먼저 잡아 ##c 가 없어 실패, a + ##bc 는 가능
// 검증: ① 손으로 고른 예와 위 반례  ② 무작위 어휘(알파벳 {a,b,c}, 조각 길이 ≤ 3) 3 000 개 × 단어 20 개를 DP 오라클과 대조: 탐욕이 낸 분할은 항상 유효(조각이 어휘에 있고 이어 붙이면 원문),
//        탐욕이 성공이면 DP 도 가능하고 조각 수 ≥ 최소 조각 수, 탐욕이 [UNK] 인데 DP 로는 가능한 경우가 실제로 있다
//        ③ 학습: 병합마다 고른 쌍이 점수의 최댓값(처음부터 다시 센 double 점수 기준), 점수 동률은 사전순, 학습 후 모든 학습 단어가 [UNK] 없이 분해되어 이어 붙이면 원문이고 조각 수가 글자 수보다 적음
//        ④ 빈도가 아니라 점수를 쓰면 BPE 와 다른 쌍을 고르는 코퍼스가 있다
typedef std::pair<std::string, std::string> Pair;
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
int minPieces(const std::string& word, const std::set<std::string>& vocab) {   // 오라클: 되돌아가는 DP — 가능한 분할의 최소 조각 수, 없으면 -1
    size_t n = word.size(); std::vector<int> best(n + 1, -1); best[0] = 0;
    for (size_t i = 0; i < n; i++) if (best[i] >= 0) for (size_t j = i + 1; j <= n; j++) {
        std::string sub = word.substr(i, j - i); if (i > 0) sub = "##" + sub;
        if (vocab.count(sub) && (best[j] < 0 || best[i] + 1 < best[j])) best[j] = best[i] + 1;
    }
    return best[n];
}
std::string strip(const std::string& piece) { return piece.compare(0, 2, "##") == 0 ? piece.substr(2) : piece; }

// ---- 학습 ----
typedef std::vector<std::string> Seq;
struct Trained { std::set<std::string> vocab; std::vector<Pair> merges; std::vector<std::vector<std::pair<Seq, long>>> history; };   // history[k] = k 번째 병합 직전의 분할
long ipairScoreCompare(long fp, long fa, long fb, long fq, long fc, long fd) { long l = fp * fc * fd, r = fq * fa * fb; return l > r ? 1 : l < r ? -1 : 0; }     // fp/(fa·fb) 와 fq/(fc·fd) 를 정수 교차 곱으로 비교 (빈도 합이 200 만 미만일 때 안전)
Trained trainWordPiece(const std::map<std::string, int>& wordFreq, int numMerges) {
    Trained T; std::vector<std::pair<Seq, long>> words;
    for (auto& kv : wordFreq) { Seq s; for (size_t i = 0; i < kv.first.size(); i++) s.push_back(i == 0 ? std::string(1, kv.first[i]) : "##" + std::string(1, kv.first[i])); words.push_back({s, kv.second}); for (auto& u : s) T.vocab.insert(u); }
    for (int it = 0; it < numMerges; it++) {
        std::map<std::string, long> unit; std::map<Pair, long> pairs;
        for (auto& w : words) { for (auto& u : w.first) unit[u] += w.second; for (size_t i = 0; i + 1 < w.first.size(); i++) pairs[{w.first[i], w.first[i + 1]}] += w.second; }
        if (pairs.empty()) break;
        T.history.push_back(words);
        bool have = false; Pair best; long bf = 0;
        for (auto& kv : pairs) {                                          // 점수가 같으면 사전순으로 앞선 쌍 (map 순회 순서) — 엄격히 클 때만 교체
            if (!have || ipairScoreCompare(kv.second, unit[kv.first.first], unit[kv.first.second], bf, unit[best.first], unit[best.second]) > 0) { have = true; best = kv.first; bf = kv.second; }
        }
        std::string merged = best.first + strip(best.second); T.merges.push_back(best); T.vocab.insert(merged);
        for (auto& w : words) { Seq t; for (size_t i = 0; i < w.first.size(); i++) { if (i + 1 < w.first.size() && w.first[i] == best.first && w.first[i + 1] == best.second) { t.push_back(merged); i++; } else t.push_back(w.first[i]); } w.first.swap(t); }
    }
    return T;
}
std::map<Pair, double> scoresFromScratch(const std::vector<std::pair<Seq, long>>& words) {       // 오라클: 같은 점수를 double 로 처음부터 계산
    std::map<std::string, double> unit; std::map<Pair, double> pairs, score;
    for (auto& w : words) { for (auto& u : w.first) unit[u] += (double)w.second; for (size_t i = 0; i + 1 < w.first.size(); i++) pairs[{w.first[i], w.first[i + 1]}] += (double)w.second; }
    for (auto& kv : pairs) score[kv.first] = kv.second / (unit[kv.first.first] * unit[kv.first.second]);
    return score;
}
std::map<Pair, long> bpeCounts(const std::vector<std::pair<Seq, long>>& words) { std::map<Pair, long> c; for (auto& w : words) for (size_t i = 0; i + 1 < w.first.size(); i++) c[{w.first[i], w.first[i + 1]}] += w.second; return c; }

int main() {
    std::set<std::string> vocab = {"un", "##aff", "##able", "play", "##ing", "##ed", "a", "##b"};
    using V = std::vector<std::string>;
    assert((wordpiece("unaffable", vocab) == V{"un", "##aff", "##able"}));
    assert((wordpiece("playing", vocab) == V{"play", "##ing"}));
    assert((wordpiece("zzz", vocab) == V{"[UNK]"}));
    assert((wordpiece("", vocab).empty()) && minPieces("", vocab) == 0);                       // 경계: 빈 단어
    std::set<std::string> trap = {"a", "##bc", "ab"};                                          // 탐욕이 실패하는 어휘
    assert((wordpiece("abc", trap) == V{"[UNK]"}) && minPieces("abc", trap) == 2);
    // ② 무작위 어휘 대 DP
    std::mt19937 rng(7); long greedyOk = 0, greedyUnkButPossible = 0, greedyLonger = 0, impossible = 0;
    for (int it = 0; it < 3000; ++it) {
        std::set<std::string> vc; std::vector<std::string> all;
        for (int len = 1; len <= 3; ++len) { std::vector<std::string> cur{""}; for (int k = 0; k < len; ++k) { std::vector<std::string> nx; for (auto& s : cur) for (char c = 'a'; c <= 'c'; c++) nx.push_back(s + c); cur = nx; } for (auto& s : cur) all.push_back(s); }
        for (auto& s : all) { if (rng() % 100 < 35) vc.insert(s); if (rng() % 100 < 35) vc.insert("##" + s); }
        for (int q = 0; q < 20; ++q) {
            std::string w; for (int k = 0, len = 1 + (int)(rng() % 7); k < len; ++k) w += (char)('a' + rng() % 3);
            V g = wordpiece(w, vc); int best = minPieces(w, vc);
            if (g == V{"[UNK]"}) { if (best >= 0) ++greedyUnkButPossible; else ++impossible; continue; }
            std::string j; for (size_t i = 0; i < g.size(); i++) { assert(vc.count(g[i]) && (i == 0) == (g[i].compare(0, 2, "##") != 0)); j += strip(g[i]); }
            assert(j == w && best >= 0 && (int)g.size() >= best); ++greedyOk; greedyLonger += (int)g.size() > best;
        }
    }
    assert(greedyOk > 10000 && greedyUnkButPossible > 100 && impossible > 5000 && greedyLonger > 50);
    // ③ 학습
    std::map<std::string, int> corpus = {{"hugging", 10}, {"hug", 12}, {"huge", 3}, {"face", 9}, {"faces", 4}, {"hugs", 5}, {"pug", 8}, {"pugs", 3}, {"bug", 2}, {"bus", 2}, {"quit", 6}, {"quiz", 5}};
    Trained T = trainWordPiece(corpus, 14);
    assert(T.merges.size() == 14 && T.history.size() == 14);
    for (size_t k = 0; k < T.merges.size(); k++) {
        auto sc = scoresFromScratch(T.history[k]); double mx = 0; for (auto& kv : sc) mx = std::max(mx, kv.second);
        assert(sc.at(T.merges[k]) >= mx * (1 - 1e-12));                                          // 고른 쌍은 점수 최댓값
        for (auto& kv : sc) if (std::fabs(kv.second - mx) <= mx * 1e-12) { assert(!(kv.first < T.merges[k]) || kv.first == T.merges[k]); }   // 동률이면 사전순으로 가장 앞선 쌍
    }
    long chars = 0, pieces = 0;
    for (auto& kv : corpus) { V p = wordpiece(kv.first, T.vocab); assert(p != V{"[UNK]"}); std::string j; for (auto& x : p) j += strip(x); assert(j == kv.first); chars += (long)kv.first.size() * kv.second; pieces += (long)p.size() * kv.second; }
    assert(pieces < chars && wordpiece("hugging", T.vocab).size() < 7);
    assert((wordpiece("hugx", T.vocab) == V{"[UNK]"}));                                        // 코퍼스에 없던 글자 x 는 어떤 조각에도 없으므로 단어 전체가 [UNK]
    // ④ 빈도(BPE) 기준 대 점수(WordPiece) 기준
    std::map<std::string, int> differ = {{"quit", 10}, {"quiz", 10}, {"ever", 100}, {"very", 100}, {"here", 100}};
    Trained D = trainWordPiece(differ, 1);
    auto cnt = bpeCounts(D.history[0]); Pair bpeChoice; long bc = 0; for (auto& kv : cnt) if (kv.second > bc) { bc = kv.second; bpeChoice = kv.first; }     // BPE 는 빈도 최대 (동률 사전순)
    assert(D.merges[0] != bpeChoice);
    std::cout << "WordPiece: unaffable -> un ##aff ##able; greedy matching failed on " << greedyUnkButPossible << " words that a backtracking DP could split; trained " << T.merges.size() << " merges (" << chars << " chars -> " << pieces << " pieces); first merge " << D.merges[0].first << "+" << D.merges[0].second << " vs BPE " << bpeChoice.first << "+" << bpeChoice.second << std::endl;
    return 0;
}
// Time Complexity: 추론 O(L²) (L = 단어 길이), 학습 O(병합 수 · 코퍼스)
// Space Complexity: O(어휘)
```
## SentencePiece()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// SentencePiece(LLaMA, T5): 공백을 일반 기호 "▁"(U+2581)로 바꿔 원문을 그대로 토큰화하므로 언어별 전처리(단어 분리)가 필요 없다.
// Unigram 모델은 조각마다 확률을 두고, 문장 확률 = (선택한 조각들의 확률의 곱).  가장 확률이 큰 분할은 Viterbi DP 로, 상위 k 개는 k-최선 DP 로 구한다
// 어휘에 없는 글자는 작은 확률의 <unk> 조각으로 처리하므로 어떤 문장도 분할되고, 조각을 이어 붙이면 항상 원문이다.  학습은 EM: 분할을 숨은 변수로 보고
// 정방향·역방향 DP 로 조각의 기대 횟수를 계산해 확률을 다시 정규화한다 — 로그 우도는 반복마다 줄지 않는다
// 검증: ① 손으로 고른 예(한국어 포함)  ② 무작위 어휘(알파벳 {a,b,c,d}, 어휘 밖 글자 e 포함)와 길이 ≤ 11 의 문자열 3 000 개를 *모든 분할 전수 열거* 와 대조: Viterbi 최적 점수, k-최선(k=6)의 점수열
//        ③ 정방향 알고리즘의 주변 확률 = 전수 열거한 확률의 합  ④ EM 15 회 동안 코퍼스 로그 우도가 단조 비감소하고 확률 합이 1, 학습 후 Viterbi 분할의 조각 수가 글자 수보다 적음
typedef std::map<std::string, double> Vocab;                           // 조각 -> 로그 확률
std::vector<std::string> utf8Chars(const std::string& s) {
    std::vector<std::string> v;
    for (size_t i = 0; i < s.size();) { unsigned char c = s[i]; size_t len = c >= 0xF0 ? 4 : c >= 0xE0 ? 3 : c >= 0xC0 ? 2 : 1; v.push_back(s.substr(i, len)); i += len; }
    return v;
}
const double NEG = -std::numeric_limits<double>::infinity();
double pieceScore(const std::string& piece, size_t nChars, const Vocab& lp, double unk) {          // 어휘에 있으면 로그 확률, 한 글자짜리 미등록 조각은 <unk>
    auto it = lp.find(piece); if (it != lp.end()) return it->second; return nChars == 1 ? unk : NEG;
}
struct Seg { std::vector<std::string> pieces; double logp; };
Seg viterbi(const std::string& text, const Vocab& lp, double unk = -20.0, size_t maxLen = 8) {
    auto ch = utf8Chars(text); size_t n = ch.size();
    std::vector<double> best(n + 1, NEG); std::vector<int> from(n + 1, -1); best[0] = 0;
    for (size_t i = 0; i < n; i++) {
        if (best[i] == NEG) continue;
        std::string piece;
        for (size_t j = i; j < n && j - i < maxLen; j++) {
            piece += ch[j]; double s = pieceScore(piece, j - i + 1, lp, unk);
            if (s != NEG && best[i] + s > best[j + 1]) { best[j + 1] = best[i] + s; from[j + 1] = (int)i; }
        }
    }
    Seg out{{}, n ? best[n] : 0.0};
    for (int j = (int)n; j > 0; j = from[j]) { std::string p; for (int k = from[j]; k < j; k++) p += ch[k]; out.pieces.insert(out.pieces.begin(), p); }
    return out;
}
std::vector<Seg> kBest(const std::string& text, const Vocab& lp, size_t k, double unk = -20.0, size_t maxLen = 8) {     // 위치마다 상위 k 개 (점수, 이전 위치, 그 위치에서의 순위)
    auto ch = utf8Chars(text); size_t n = ch.size();
    struct Cand { double s; int from, rank; };
    std::vector<std::vector<Cand>> L(n + 1); L[0].push_back({0.0, -1, -1});
    for (size_t j = 1; j <= n; j++) {
        std::vector<Cand> c;
        for (size_t i = (j > maxLen ? j - maxLen : 0); i < j; i++) {
            std::string piece; for (size_t t = i; t < j; t++) piece += ch[t];
            double s = pieceScore(piece, j - i, lp, unk); if (s == NEG) continue;
            for (size_t r = 0; r < L[i].size(); r++) c.push_back({L[i][r].s + s, (int)i, (int)r});
        }
        std::sort(c.begin(), c.end(), [](const Cand& a, const Cand& b) { return a.s > b.s; });
        if (c.size() > k) c.resize(k);
        L[j] = c;
    }
    std::vector<Seg> res;
    for (size_t r = 0; r < L[n].size(); r++) {
        Seg sg{{}, L[n][r].s}; int j = (int)n, rr = (int)r;
        while (j > 0) { const Cand& c = L[j][rr]; std::string p; for (int t = c.from; t < j; t++) p += ch[t]; sg.pieces.insert(sg.pieces.begin(), p); rr = c.rank; j = c.from; }
        res.push_back(sg);
    }
    return res;
}
void enumerate(const std::vector<std::string>& ch, size_t pos, std::vector<std::string>& cur, double score, const Vocab& lp, double unk, size_t maxLen, std::vector<Seg>& all) {    // 오라클: 모든 분할
    if (pos == ch.size()) { all.push_back({cur, score}); return; }
    std::string piece;
    for (size_t j = pos; j < ch.size() && j - pos < maxLen; j++) {
        piece += ch[j]; double s = pieceScore(piece, j - pos + 1, lp, unk); if (s == NEG) continue;
        cur.push_back(piece); enumerate(ch, j + 1, cur, score + s, lp, unk, maxLen, all); cur.pop_back();
    }
}
double logMarginal(const std::string& text, const std::map<std::string, double>& p, size_t maxLen, std::vector<double>* alphaOut = nullptr, std::vector<double>* betaOut = nullptr) {      // 정방향 알고리즘: Σ_분할 Π 확률
    auto ch = utf8Chars(text); size_t n = ch.size(); std::vector<double> a(n + 1, 0.0), b(n + 1, 0.0); a[0] = 1;
    for (size_t j = 1; j <= n; j++) { std::string piece; for (size_t i = j; i-- > 0 && j - i <= maxLen;) { piece = ch[i] + piece; auto it = p.find(piece); if (it != p.end()) a[j] += a[i] * it->second; } }
    b[n] = 1;
    for (size_t i = n; i-- > 0;) { std::string piece; for (size_t j = i; j < n && j - i < maxLen; j++) { piece += ch[j]; auto it = p.find(piece); if (it != p.end()) b[i] += it->second * b[j + 1]; } }
    if (alphaOut) *alphaOut = a; if (betaOut) *betaOut = b;
    return a[n] > 0 ? std::log(a[n]) : NEG;
}
std::map<std::string, double> emStep(const std::vector<std::string>& corpus, const std::map<std::string, double>& p, size_t maxLen) {     // E: 기대 횟수, M: 정규화
    std::map<std::string, double> c;
    for (const std::string& s : corpus) {
        std::vector<double> a, b; logMarginal(s, p, maxLen, &a, &b); auto ch = utf8Chars(s); size_t n = ch.size(); double Z = a[n]; if (Z <= 0) continue;
        for (size_t i = 0; i < n; i++) { std::string piece; for (size_t j = i; j < n && j - i < maxLen; j++) { piece += ch[j]; auto it = p.find(piece); if (it != p.end()) c[piece] += a[i] * it->second * b[j + 1] / Z; } }
    }
    double tot = 0; for (auto& kv : c) tot += kv.second;
    std::map<std::string, double> q; for (auto& kv : c) if (kv.second > 1e-12) q[kv.first] = kv.second / tot;
    return q;
}

int main() {
    Vocab lp = {{"▁hello", std::log(0.05)}, {"▁world", std::log(0.04)}, {"▁hell", std::log(0.01)}, {"o", std::log(0.03)},
        {"▁", std::log(0.1)}, {"h", std::log(0.02)}, {"e", std::log(0.05)}, {"l", std::log(0.04)}, {"w", std::log(0.02)},
        {"r", std::log(0.04)}, {"d", std::log(0.03)}, {"▁w", std::log(0.005)}, {"orld", std::log(0.002)}};
    using V = std::vector<std::string>;
    assert((viterbi("▁hello▁world", lp).pieces == V{"▁hello", "▁world"}));         // 긴 조각 하나가 짧은 조각 여러 개의 곱보다 확률이 높다
    assert((viterbi("▁hello", lp).pieces == V{"▁hello"}));
    Vocab chars = {{"▁", std::log(0.1)}, {"w", std::log(0.02)}, {"o", std::log(0.03)}, {"r", std::log(0.04)}, {"l", std::log(0.04)}, {"d", std::log(0.03)}};
    assert((viterbi("▁world", chars).pieces == V{"▁", "w", "o", "r", "l", "d"}));   // 큰 조각이 없으면 글자 단위
    Vocab ko = {{"▁안녕", std::log(0.03)}, {"▁하세요", std::log(0.02)}, {"▁", std::log(0.1)}, {"안", std::log(0.01)}, {"녕", std::log(0.01)}, {"하", std::log(0.02)}, {"세", std::log(0.01)}, {"요", std::log(0.02)}};
    assert((viterbi("▁안녕▁하세요", ko).pieces == V{"▁안녕", "▁하세요"}));                      // 한국어도 같은 방식 (한 글자 = UTF-8 3 바이트)
    Seg unkSeg = viterbi("▁hello🙂", lp); assert(unkSeg.pieces.size() == 2 && unkSeg.pieces[1] == "🙂" && std::fabs(unkSeg.logp - (std::log(0.05) - 20.0)) < 1e-9);       // 어휘 밖 글자는 <unk> 로 한 글자씩
    assert(viterbi("", lp).pieces.empty() && viterbi("", lp).logp == 0.0 && kBest("", lp, 3).size() == 1);                       // 경계: 빈 문장은 빈 분할 하나
    // ② 전수 열거와 대조
    std::mt19937 rng(100); long checked = 0, ties = 0, multi = 0;
    for (int it = 0; it < 3000; ++it) {
        Vocab v; std::vector<std::string> all; const char* al = "abcd";
        for (int len = 1; len <= 3; ++len) { std::vector<std::string> cur{""}; for (int t = 0; t < len; ++t) { std::vector<std::string> nx; for (auto& s : cur) for (int c = 0; c < 4; ++c) nx.push_back(s + al[c]); cur = nx; } for (auto& s : cur) all.push_back(s); }
        for (auto& s : all) if (rng() % 100 < 40) v[s] = std::log((double)(1 + rng() % 100) / 1000.0);
        std::string text; for (int t = 0, n = (int)(rng() % 12); t < n; ++t) text += "abcde"[rng() % 5];          // e 는 어휘 밖 글자
        std::vector<Seg> every; std::vector<std::string> cur; enumerate(utf8Chars(text), 0, cur, 0.0, v, -20.0, 8, every);
        std::sort(every.begin(), every.end(), [](const Seg& a, const Seg& b) { return a.logp > b.logp; });
        Seg vt = viterbi(text, v); std::string j; for (auto& p : vt.pieces) j += p; assert(j == text);              // 이어 붙이면 원문
        assert(!every.empty() && std::fabs(vt.logp - every[0].logp) < 1e-9);                                      // 최적 점수
        double rescored = 0; for (auto& p : vt.pieces) rescored += pieceScore(p, utf8Chars(p).size(), v, -20.0); assert(std::fabs(rescored - vt.logp) < 1e-9);
        std::vector<Seg> kb = kBest(text, v, 6);
        assert(kb.size() == std::min<size_t>(6, every.size()));
        std::set<std::vector<std::string>> distinct;
        for (size_t r = 0; r < kb.size(); r++) { assert(std::fabs(kb[r].logp - every[r].logp) < 1e-9); distinct.insert(kb[r].pieces); std::string jj; for (auto& p : kb[r].pieces) jj += p; assert(jj == text); }
        assert(distinct.size() == kb.size());
        if (every.size() > 1 && std::fabs(every[0].logp - every[1].logp) < 1e-12) ++ties; multi += every.size() > 1; ++checked;
    }
    assert(checked == 3000 && multi > 1500 && ties > 5);
    // ③ 주변 확률 = 전수 열거한 합
    long margChecks = 0;
    for (int it = 0; it < 500; ++it) {
        std::map<std::string, double> p; double tot = 0; std::vector<std::string> pieces;
        for (int len = 1; len <= 3; ++len) { std::vector<std::string> cur{""}; for (int t = 0; t < len; ++t) { std::vector<std::string> nx; for (auto& s : cur) for (char c = 'a'; c <= 'c'; c++) nx.push_back(s + c); cur = nx; } for (auto& s : cur) pieces.push_back(s); }
        for (auto& s : pieces) if (rng() % 100 < 50 || s.size() == 1) { p[s] = 0.001 + (rng() % 100); tot += p[s]; }
        for (auto& kv : p) kv.second /= tot;
        std::string text; for (int t = 0, n = (int)(rng() % 11); t < n; ++t) text += (char)('a' + rng() % 3);
        Vocab asLog; for (auto& kv : p) asLog[kv.first] = std::log(kv.second);
        std::vector<Seg> every; std::vector<std::string> cur; enumerate(utf8Chars(text), 0, cur, 0.0, asLog, NEG, 3, every);
        double sum = 0; for (auto& sg : every) sum += std::exp(sg.logp);
        assert(std::fabs(std::exp(logMarginal(text, p, 3)) - sum) < 1e-12 * std::max(1.0, sum) + 1e-300); ++margChecks;
    }
    // ④ EM
    std::vector<std::string> corpus = {"▁the▁cat▁sat", "▁the▁cat▁ate", "▁the▁rat▁sat", "▁that▁cat▁sat", "▁the▁hat", "▁the▁cat▁the▁rat", "▁that▁is▁that"};
    std::map<std::string, double> p; std::set<std::string> cand;
    for (auto& s : corpus) { auto ch = utf8Chars(s); for (size_t i = 0; i < ch.size(); i++) { std::string piece; for (size_t j = i; j < ch.size() && j - i < 5; j++) { piece += ch[j]; cand.insert(piece); } } }
    for (auto& s : cand) p[s] = 1.0 / (double)cand.size();
    auto loglik = [&](const std::map<std::string, double>& q) { double t = 0; for (auto& s : corpus) t += logMarginal(s, q, 5); return t; };
    double prev = loglik(p), first = prev; long increases = 0;
    for (int iter = 0; iter < 15; ++iter) {
        p = emStep(corpus, p, 5); double cur = loglik(p), sum = 0; for (auto& kv : p) sum += kv.second;
        assert(cur >= prev - 1e-9 && std::fabs(sum - 1.0) < 1e-9); increases += cur > prev + 1e-9; prev = cur;           // EM: 로그 우도 단조 비감소
    }
    assert(increases >= 10 && prev > first + 10);
    Vocab trainedLog; for (auto& kv : p) trainedLog[kv.first] = std::log(kv.second);
    long chs = 0, pcs = 0; for (auto& s : corpus) { Seg sg = viterbi(s, trainedLog, -20.0, 5); std::string j; for (auto& x : sg.pieces) j += x; assert(j == s); chs += (long)utf8Chars(s).size(); pcs += (long)sg.pieces.size(); }
    assert(pcs < chs);
    std::cout << "SentencePiece: " << checked << " random strings matched exhaustive enumeration (" << multi << " with several segmentations); forward-algorithm marginals matched on " << margChecks << " strings; EM raised the corpus log-likelihood from " << first << " to " << prev << " and tokenized " << chs << " chars into " << pcs << " pieces" << std::endl;
    return 0;
}
// Time Complexity: Viterbi O(n · 최대 조각 길이), k-최선 O(n · L · k log k), EM 한 번은 O(코퍼스 · L)
// Space Complexity: O(n)
```
## TokenizeLLM()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <utility>
#include <vector>

// LLM 에 프롬프트가 들어가는 경로: 텍스트 -> (사전 토큰화) -> 바이트 BPE 병합 -> 토큰 -> 정수 ID -> [BOS, ..., EOS]
// GPT-2 계열은 모든 바이트를 보이는 유니코드 글자로 바꿔 BPE 를 돌린다 — 그래서 어떤 바이트열도 <unk> 없이 표현된다.  표의 규칙: 눈에 보이는 바이트(33~126, 161~172, 174~255)는 자기 자신,
// 나머지 68 바이트는 256 + (순번) 번 코드 포인트로 보낸다.  공백(32)은 U+0120 "Ġ", 줄바꿈(10)은 U+010A "Ċ".  병합 순서(순위)가 곧 우선순위
// 사전 토큰화(GPT-2 정규식의 ASCII 판): 축약형('s 't 're 've 'm 'll 'd) | [공백]글자들 | [공백]숫자들 | [공백]기호들 | 뒤에 비공백이 오면 마지막 하나를 남긴 공백 덩어리 | 공백 덩어리 (바이트 ≥ 0x80 은 글자로 취급)
// 검증: ① 바이트 표(전단사, 알려진 값)와 사전 토큰화의 파이썬 정규식 결과 8 개  ② 직접 만든 병합으로 "hello world" -> [BOS, hello, Ġworld, EOS]  ③ 학습한 병합으로 *임의 바이트열* 1 500 개(잘못된 UTF-8, NUL 포함)가
//        왕복 복원되고, 사전 토큰화 조각은 이어 붙이면 원문이며 모양이 규칙대로이고, 토큰 수 ≤ 바이트 수, 병합이 조각 경계를 넘지 않음, 순서대로 적용한 병합 = 순위 우선 병합  ④ 공백 유무로 다른 토큰, 조각 경계 때문에 encode(a)+encode(b) ≠ encode(a+b)
typedef std::vector<std::string> Seq;
typedef std::pair<std::string, std::string> Pair;
std::vector<unsigned> byteToCp() {
    std::vector<unsigned> t(256); std::vector<bool> keep(256, false);
    for (int b = 33; b <= 126; b++) keep[b] = true; for (int b = 161; b <= 172; b++) keep[b] = true; for (int b = 174; b <= 255; b++) keep[b] = true;
    unsigned n = 0; for (int b = 0; b < 256; b++) t[b] = keep[b] ? (unsigned)b : 256 + n++;
    return t;
}
std::string cpToUtf8(unsigned cp) { std::string s; if (cp < 0x80) s += (char)cp; else { s += (char)(0xC0 | (cp >> 6)); s += (char)(0x80 | (cp & 0x3F)); } return s; }       // 표의 코드 포인트는 모두 < 0x800
const std::vector<unsigned> CP = byteToCp();
std::string byteTok(unsigned char b) { return cpToUtf8(CP[b]); }
std::string toMapped(const std::string& bytes) { std::string s; for (unsigned char b : bytes) s += byteTok(b); return s; }
Seq mappedChars(const std::string& mapped) { Seq v; for (size_t i = 0; i < mapped.size();) { size_t len = (unsigned char)mapped[i] >= 0xC0 ? 2 : 1; v.push_back(mapped.substr(i, len)); i += len; }  return v; }
enum Cls { LETTER, DIGIT, SPACE, PUNCT };
Cls cls(unsigned char c) {
    if (c >= 0x80 || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) return LETTER;
    if (c >= '0' && c <= '9') return DIGIT;
    if (c == ' ' || (c >= 9 && c <= 13)) return SPACE;
    return PUNCT;
}
std::vector<std::string> preTokenize(const std::string& s) {
    std::vector<std::string> out; size_t i = 0, n = s.size();
    while (i < n) {
        bool done = false;
        if (s[i] == '\'') for (const char* c : {"s", "t", "re", "ve", "m", "ll", "d"}) { size_t L = std::strlen(c); if (s.compare(i + 1, L, c) == 0) { out.push_back(s.substr(i, 1 + L)); i += 1 + L; done = true; break; } }
        if (done) continue;
        size_t j = i + (s[i] == ' ' && i + 1 < n ? 1 : 0);                                                          // [공백] 접두
        Cls c = cls(s[j]);
        if (c != SPACE) { size_t k = j; while (k < n && cls(s[k]) == c) k++; out.push_back(s.substr(i, k - i)); i = k; continue; }
        size_t k = i; while (k < n && cls(s[k]) == SPACE) k++;                                                      // 공백 덩어리
        if (k < n && k - i >= 2) k--;                                                                              // 뒤에 비공백이 오면 마지막 하나는 다음 조각에 남긴다
        else if (k < n) k = i + 1;
        out.push_back(s.substr(i, k - i)); i = k;
    }
    return out;
}
Seq bpeRank(const std::string& word, const std::map<Pair, int>& rank) {                // 바이트 -> 매핑된 글자 -> 순위 낮은 쌍부터 합치기
    Seq s = mappedChars(toMapped(word));
    for (;;) {
        int best = INT_MAX; Pair bp;
        for (size_t i = 0; i + 1 < s.size(); i++) { auto it = rank.find({s[i], s[i + 1]}); if (it != rank.end() && it->second < best) { best = it->second; bp = it->first; } }
        if (best == INT_MAX) return s;
        Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == bp.first && s[i + 1] == bp.second) { t.push_back(bp.first + bp.second); i++; } else t.push_back(s[i]); }
        s.swap(t);
    }
}
Seq bpeSequential(const std::string& word, const std::vector<Pair>& merges) {
    Seq s = mappedChars(toMapped(word));
    for (auto& m : merges) { Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == m.first && s[i + 1] == m.second) { t.push_back(m.first + m.second); i++; } else t.push_back(s[i]); } s.swap(t); }
    return s;
}
std::vector<Pair> trainMerges(const std::string& corpus, int numMerges) {
    std::map<std::string, long> freq; for (auto& w : preTokenize(corpus)) freq[w]++;
    std::vector<std::pair<Seq, long>> words; for (auto& kv : freq) words.push_back({mappedChars(toMapped(kv.first)), kv.second});
    std::vector<Pair> merges;
    for (int it = 0; it < numMerges; it++) {
        std::map<Pair, long> cnt; for (auto& w : words) for (size_t i = 0; i + 1 < w.first.size(); i++) cnt[{w.first[i], w.first[i + 1]}] += w.second;
        Pair best; long bc = 0; for (auto& kv : cnt) if (kv.second > bc) { bc = kv.second; best = kv.first; }
        if (bc < 2) break; merges.push_back(best);
        for (auto& w : words) { Seq t; for (size_t i = 0; i < w.first.size(); i++) { if (i + 1 < w.first.size() && w.first[i] == best.first && w.first[i + 1] == best.second) { t.push_back(best.first + best.second); i++; } else t.push_back(w.first[i]); } w.first.swap(t); }
    }
    return merges;
}
struct Tokenizer {
    std::vector<Pair> merges; std::map<Pair, int> rank; std::vector<std::string> vocab; std::map<std::string, int> id; int bos, eos;
    explicit Tokenizer(const std::vector<Pair>& m) : merges(m) {
        for (int b = 0; b < 256; b++) vocab.push_back(byteTok((unsigned char)b));                                   // 0..255: 바이트 토큰
        for (size_t i = 0; i < merges.size(); i++) { rank.emplace(merges[i], (int)i); vocab.push_back(merges[i].first + merges[i].second); }
        bos = (int)vocab.size(); vocab.push_back("<bos>"); eos = (int)vocab.size(); vocab.push_back("<eos>");
        for (size_t i = 0; i < vocab.size(); i++) id.emplace(vocab[i], (int)i);                                    // 같은 문자열이 두 병합에서 나오면 앞 ID 를 쓴다
    }
    std::vector<int> encode(const std::string& text, bool special = true) const {
        std::vector<int> ids; if (special) ids.push_back(bos);
        for (auto& w : preTokenize(text)) for (auto& t : bpeRank(w, rank)) ids.push_back(id.at(t));
        if (special) ids.push_back(eos); return ids;
    }
    std::string decode(const std::vector<int>& ids) const {
        std::map<std::string, int> back; for (int b = 0; b < 256; b++) back[byteTok((unsigned char)b)] = b;
        std::string out;
        for (int x : ids) { if (x == bos || x == eos) continue; for (auto& ch : mappedChars(vocab[x])) out += (char)back.at(ch); }
        return out;
    }
};

int main() {
    // ① 바이트 표
    assert(CP[32] == 0x120 && CP[10] == 0x10A && CP['A'] == 'A' && CP[0] == 0x100 && CP[127] == 0x121 && CP[160] == 0x142 && CP[173] == 0x143 && CP[255] == 255);
    { std::map<unsigned, int> seen; for (int b = 0; b < 256; b++) { assert(seen.emplace(CP[b], b).second); assert(CP[b] < 0x144); } assert(seen.size() == 256 && byteTok(32) == "Ġ" && byteTok(10) == "Ċ"); }
    using V = std::vector<std::string>;
    assert((preTokenize("Hello world!  Don't 123") == V{"Hello", " world", "!", " ", " Don", "'t", " 123"}));           // 파이썬 정규식의 결과
    assert((preTokenize("  leading") == V{" ", " leading"}) && (preTokenize("trail  ") == V{"trail", "  "}) && (preTokenize("a\n\nb") == V{"a", "\n", "\n", "b"}));
    assert((preTokenize("x=1+2;") == V{"x", "=", "1", "+", "2", ";"}) && (preTokenize("한글 😀 ok") == V{"한글", " 😀", " ok"}) && (preTokenize("it's we've") == V{"it", "'s", " we", "'ve"}));
    assert((preTokenize("   ") == V{"   "}) && preTokenize("").empty());
    // ② 직접 만든 병합: "hello world" -> [BOS, hello, Ġworld, EOS]
    std::string G = byteTok(' ');
    std::vector<Pair> hand = {{"h", "e"}, {"he", "l"}, {"hel", "l"}, {"hell", "o"}, {G, "w"}, {G + "w", "o"}, {G + "wo", "r"}, {G + "wor", "l"}, {G + "worl", "d"}};
    Tokenizer th(hand); auto ids = th.encode("hello world");
    assert((ids == std::vector<int>{th.bos, th.id.at("hello"), th.id.at(G + "world"), th.eos}));
    assert(ids.size() == 4);                                           // 11글자가 토큰 2개(+특수 토큰 2개)로 줄어든다
    auto ids2 = th.encode("hello hello");
    assert(ids2[1] == th.id.at("hello") && ids2[2] != th.id.at("hello") && ids2[2] == th.id.at(G) && ids2[3] == th.id.at("hello"));   // 같은 단어라도 앞에 공백이 있으면 다른 토큰 (여기서는 Ġ + hello)
    assert(th.decode(ids) == "hello world" && th.decode(th.encode("")) == "" && th.encode("", false).empty());
    assert(th.encode("hell", false).size() == 1 && th.encode("o", false).size() == 1 && th.encode("hello", false).size() == 1 && th.encode("hell", false)[0] != th.encode("hello", false)[0]);   // ④ 조각 경계: encode(a)+encode(b) ≠ encode(a+b)

    // ③ 학습한 병합과 임의 바이트열
    std::string corpus; for (int i = 0; i < 30; ++i) corpus += "The quick brown fox jumps over the lazy dog. It's 2024 and we've tested 123 cases!\n한글 토크나이저 테스트입니다. 😀 hello world, hello there.\n";
    std::vector<Pair> merges = trainMerges(corpus, 100); Tokenizer tk(merges);
    assert(merges.size() == 100 && tk.vocab.size() == 256 + 100 + 2);
    std::mt19937 rng(2024); long bytesTotal = 0, tokensTotal = 0, crossings = 0;
    std::vector<std::string> pieces = {"hello", " world", "한글", "😀", " ", "\n", "'s", "123", "!", "the", " the", "\xFF\xFE", std::string("\0", 1), "\xC3", "\x80", " fox"};
    for (int it = 0; it < 1500; ++it) {
        std::string s; for (int k = 0, n = (int)(rng() % 12); k < n; ++k) { if (rng() % 3 == 0) { int len = 1 + (int)(rng() % 3); for (int q = 0; q < len; ++q) s += (char)rng(); } else s += pieces[rng() % pieces.size()]; }
        auto pre = preTokenize(s); std::string cat; for (auto& p : pre) { cat += p; assert(!p.empty()); } assert(cat == s);                                  // 사전 토큰화는 원문의 분할
        for (auto& p : pre) {                                                                                                  // 조각의 모양
            bool spaces = true, contraction = p[0] == '\'' && p.size() >= 2 && (p == "'s" || p == "'t" || p == "'re" || p == "'ve" || p == "'m" || p == "'ll" || p == "'d");
            for (unsigned char c : p) spaces = spaces && cls(c) == SPACE;
            std::string body = p[0] == ' ' && p.size() > 1 && cls(p[1]) != SPACE ? p.substr(1) : p; bool uniform = true; for (unsigned char c : body) uniform = uniform && cls(c) == cls(body[0]);
            assert(spaces || contraction || uniform);
        }
        auto ids3 = tk.encode(s); assert(tk.decode(ids3) == s);                                                               // 임의 바이트열 왕복
        assert(ids3.front() == tk.bos && ids3.back() == tk.eos && ids3.size() - 2 <= s.size());                                // 토큰은 바이트마다 많아야 하나
        size_t sum = 0; for (auto& p : pre) sum += tk.encode(p, false).size(); assert(sum == ids3.size() - 2);               // 병합이 조각 경계를 넘지 않는다
        for (auto& p : pre) { Seq a = bpeSequential(p, merges), b = bpeRank(p, tk.rank); assert(a == b); }
        bytesTotal += (long)s.size(); tokensTotal += (long)ids3.size() - 2; crossings += pre.size();
        for (int x : ids3) assert(x >= 0 && x < (int)tk.vocab.size());
    }
    std::string sample = "The quick brown fox jumps over the lazy dog. It's 2024!\n"; auto sid = tk.encode(sample, false);
    assert(tk.decode(sid) == sample && sid.size() * 10 < sample.size() * 6);                                                   // 학습한 문장은 바이트 수의 60 % 미만의 토큰으로
    std::cout << "TokenizeLLM: 'hello world' ->"; for (int i : ids) std::cout << " " << i; std::cout << " ; 1500 arbitrary byte strings round-tripped (" << bytesTotal << " bytes -> " << tokensTotal << " tokens, " << crossings << " pre-tokens), trained text compressed to " << sid.size() << " tokens for " << sample.size() << " bytes" << std::endl;
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
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>

// 역토큰화(detokenize): 생성된 토큰 ID -> 문자열.  (1) 토큰을 이어 붙이고 (2) 바이트 BPE 의 글자를 원래 바이트로 되돌리고(Ġ -> 공백) (3) 특수 토큰은 제거한다.
// 바이트 수준 BPE 에서는 한 글자(UTF-8 여러 바이트)가 토큰 여러 개에 걸쳐 나올 수 있으므로,
// 스트리밍 출력은 "아직 완성되지 않은 바이트"를 버퍼에 두었다가 코드 포인트가 완성될 때만 내보내야 한다.  모델이 잘못된 바이트열을 내도 안전하도록 규칙을 둔다:
// 유니코드 권장대로 "잘못된 시퀀스의 가장 긴 부분(maximal subpart)" 하나를 U+FFFD 로 바꾸고 문제의 바이트부터 다시 읽는다.  끝에서 미완성이면 flush() 가 U+FFFD 하나를 낸다
// 검증: ① 손으로 고른 예와 파이썬 bytes.decode('utf-8', 'replace') 의 결과 12 개  ② 짧은 바이트열 111 110 개(경계 바이트 10 종, 길이 ≤ 5)를 *모든 청크 분할 방식* 으로 스트리밍한 결과가
//        한 번에 디코딩한 기준 구현(앞으로 훑어 보는 방식)과 같고, 출력은 항상 올바른 UTF-8 이며, 올바른 입력은 그대로 나온다  ③ 무작위 긴 입력 2 000 개와 토큰 단위 스트리밍
std::vector<unsigned> byteToCp() {
    std::vector<unsigned> t(256); std::vector<bool> keep(256, false);
    for (int b = 33; b <= 126; b++) keep[b] = true; for (int b = 161; b <= 172; b++) keep[b] = true; for (int b = 174; b <= 255; b++) keep[b] = true;
    unsigned n = 0; for (int b = 0; b < 256; b++) t[b] = keep[b] ? (unsigned)b : 256 + n++;
    return t;
}
const std::vector<unsigned> CP = byteToCp();
std::string cpToUtf8(unsigned cp) { std::string s; if (cp < 0x80) s += (char)cp; else { s += (char)(0xC0 | (cp >> 6)); s += (char)(0x80 | (cp & 0x3F)); } return s; }
const std::string G = cpToUtf8(CP[32]);                                // "Ġ"
const std::string FFFD = "\xEF\xBF\xBD";

std::string detokenizeBytes(const std::vector<std::string>& tokens) {  // GPT-2 방식: 매핑된 글자 -> 바이트 (Ġ -> 공백), 특수 토큰 제외
    std::map<unsigned, int> back; for (int b = 0; b < 256; b++) back[CP[b]] = b;
    std::string out;
    for (auto& t : tokens) {
        if (t == "<bos>" || t == "<eos>") continue;
        for (size_t i = 0; i < t.size();) {
            unsigned char c = t[i]; unsigned cp = c < 0x80 ? c : ((c & 0x1F) << 6) | (t[i + 1] & 0x3F); i += c < 0x80 ? 1 : 2;
            out += (char)back.at(cp);
        }
    }
    return out;
}
std::string detokenizeSP(const std::vector<std::string>& tokens) {     // SentencePiece 방식: ▁ -> 공백, 맨 앞 공백 하나 제거
    const std::string U = "\xE2\x96\x81"; std::string out;
    for (auto& t : tokens) { if (t == "<s>" || t == "</s>") continue; std::string s = t; for (size_t p = s.find(U); p != std::string::npos; p = s.find(U, p + 1)) s.replace(p, U.size(), " "); out += s; }
    if (!out.empty() && out[0] == ' ') out.erase(0, 1);
    return out;
}
class StreamDecoder {                                                   // 바이트 단위 상태 기계
    std::string seq; int remaining = 0; unsigned char lo = 0x80, hi = 0xBF;
    void start(unsigned char b, int rem, unsigned char l, unsigned char h, std::string& out) { (void)out; seq.assign(1, (char)b); remaining = rem; lo = l; hi = h; }
    void one(unsigned char b, std::string& out) {
        if (remaining == 0) {
            if (b < 0x80) out += (char)b;
            else if (b >= 0xC2 && b <= 0xDF) start(b, 1, 0x80, 0xBF, out);
            else if (b == 0xE0) start(b, 2, 0xA0, 0xBF, out);
            else if (b == 0xED) start(b, 2, 0x80, 0x9F, out);
            else if (b >= 0xE1 && b <= 0xEF) start(b, 2, 0x80, 0xBF, out);
            else if (b == 0xF0) start(b, 3, 0x90, 0xBF, out);
            else if (b == 0xF4) start(b, 3, 0x80, 0x8F, out);
            else if (b >= 0xF1 && b <= 0xF3) start(b, 3, 0x80, 0xBF, out);
            else out += FFFD;                                           // 80..C1, F5..FF 는 어떤 문자의 시작도 될 수 없다
        } else if (b >= lo && b <= hi) {
            seq += (char)b; if (--remaining == 0) { out += seq; seq.clear(); } lo = 0x80; hi = 0xBF;
        } else { out += FFFD; seq.clear(); remaining = 0; one(b, out); }  // 끊긴 시퀀스는 U+FFFD 하나, 이 바이트는 처음부터 다시
    }
public:
    std::string feed(const std::string& bytes) { std::string out; for (unsigned char b : bytes) one(b, out); return out; }
    std::string flush() { std::string out; if (remaining > 0) out += FFFD; seq.clear(); remaining = 0; lo = 0x80; hi = 0xBF; return out; }
    bool hasPending() const { return remaining > 0; }
};
std::string decodeAll(const std::string& s) {                           // 기준 구현: 한 번에, 앞으로 훑어 보며 "가능한 가장 긴 접두" 길이를 센다
    std::string out; size_t i = 0, n = s.size();
    while (i < n) {
        unsigned char b = s[i]; int need; unsigned char lo1 = 0x80, hi1 = 0xBF;
        if (b < 0x80) { out += s[i++]; continue; }
        else if (b >= 0xC2 && b <= 0xDF) need = 2;
        else if (b >= 0xE0 && b <= 0xEF) { need = 3; if (b == 0xE0) lo1 = 0xA0; if (b == 0xED) hi1 = 0x9F; }
        else if (b >= 0xF0 && b <= 0xF4) { need = 4; if (b == 0xF0) lo1 = 0x90; if (b == 0xF4) hi1 = 0x8F; }
        else { out += FFFD; i++; continue; }
        int k = 1;
        while (k < need && i + k < n) { unsigned char c = s[i + k]; unsigned char l = k == 1 ? lo1 : 0x80, h = k == 1 ? hi1 : 0xBF; if (c < l || c > h) break; k++; }
        if (k == need) out += s.substr(i, need); else out += FFFD;
        i += k;
    }
    return out;
}
bool validUtf8(const std::string& s) {                                   // 출력 검증용 (유니코드 표 3-7)
    size_t i = 0, n = s.size();
    auto in = [&](size_t k, int lo, int hi) { return k < n && (unsigned char)s[k] >= lo && (unsigned char)s[k] <= hi; };
    while (i < n) {
        unsigned char c = s[i];
        if (c < 0x80) i++;
        else if (c >= 0xC2 && c <= 0xDF && in(i + 1, 0x80, 0xBF)) i += 2;
        else if ((c == 0xE0 && in(i + 1, 0xA0, 0xBF) && in(i + 2, 0x80, 0xBF)) || (((c >= 0xE1 && c <= 0xEC) || c == 0xEE || c == 0xEF) && in(i + 1, 0x80, 0xBF) && in(i + 2, 0x80, 0xBF)) || (c == 0xED && in(i + 1, 0x80, 0x9F) && in(i + 2, 0x80, 0xBF))) i += 3;
        else if ((c == 0xF0 && in(i + 1, 0x90, 0xBF) && in(i + 2, 0x80, 0xBF) && in(i + 3, 0x80, 0xBF)) || (c >= 0xF1 && c <= 0xF3 && in(i + 1, 0x80, 0xBF) && in(i + 2, 0x80, 0xBF) && in(i + 3, 0x80, 0xBF)) || (c == 0xF4 && in(i + 1, 0x80, 0x8F) && in(i + 2, 0x80, 0xBF) && in(i + 3, 0x80, 0xBF))) i += 4;
        else return false;
    }
    return true;
}
std::string streamed(const std::string& s, const std::vector<size_t>& cuts) {   // cuts 에서 나눈 조각들을 차례로 feed 하고 마지막에 flush
    StreamDecoder d; std::string out; size_t prev = 0;
    for (size_t c : cuts) { out += d.feed(s.substr(prev, c - prev)); prev = c; }
    out += d.feed(s.substr(prev)); out += d.flush(); return out;
}

int main() {
    assert(detokenizeBytes({"<bos>", "hello", G + "world", "!", "<eos>"}) == "hello world!");
    assert(detokenizeBytes({G + "a", G + "b"}) == " a b" && detokenizeBytes({cpToUtf8(CP[10]), "x"}) == "\nx");        // GPT-2 방식은 맨 앞 공백을 지우지 않는다
    assert(detokenizeSP({"<s>", "\xE2\x96\x81Hello", "\xE2\x96\x81world", "</s>"}) == "Hello world" && detokenizeSP({"a", "b"}) == "ab" && detokenizeSP({}).empty());
    StreamDecoder d;                                                     // "한" = ED 95 9C 이 토큰 셋으로 쪼개져 도착
    assert(d.feed("\xED") == "" && d.hasPending());
    assert(d.feed("\x95") == "" && d.hasPending());
    assert(d.feed("\x9C") == "한" && !d.hasPending());
    assert(d.feed("ab") == "ab" && d.flush().empty());
    // ① 파이썬 bytes.decode('utf-8', 'replace') 의 결과
    struct Gold { std::string in, out; };
    std::vector<Gold> gold = {
        {"\xE2\x82" "A", FFFD + "A"}, {"\xFF\xFE", FFFD + FFFD}, {"\xF0\x9F\x98", FFFD}, {"\xC0\x80", FFFD + FFFD}, {"\xED\xA0\x80", FFFD + FFFD + FFFD}, {"\xF4\x90\x80\x80", FFFD + FFFD + FFFD + FFFD},
        {"A\x80" "B", "A" + FFFD + "B"}, {"\xE2\x82\xAC\xE2", "\xE2\x82\xAC" + FFFD}, {"\xF0\x80\x80\x80", FFFD + FFFD + FFFD + FFFD}, {"\xE0\x80\x80", FFFD + FFFD + FFFD}, {"ok\xC3", "ok" + FFFD}, {"\xC3\xA9\xC3", "\xC3\xA9" + FFFD}};
    for (auto& g : gold) { assert(decodeAll(g.in) == g.out && streamed(g.in, {}) == g.out); for (size_t c = 1; c < g.in.size(); c++) assert(streamed(g.in, {c}) == g.out); }
    // ② 짧은 바이트열 전수 × 모든 청크 분할
    const unsigned char alpha[] = {0x41, 0x80, 0xBF, 0xC2, 0xE0, 0xED, 0xF0, 0xF4, 0xA0, 0x9F};
    std::vector<std::string> all{std::string()};
    for (size_t i = 0; i < all.size(); ++i) if (all[i].size() < 5) for (unsigned char a : alpha) all.push_back(all[i] + (char)a);
    assert(all.size() == 111111);
    long valid = 0, withRepl = 0, splits = 0;
    for (const std::string& s : all) {
        std::string ref = decodeAll(s); assert(validUtf8(ref));                                                       // 출력은 항상 올바른 UTF-8
        if (validUtf8(s)) { assert(ref == s); ++valid; } else { assert(ref.find(FFFD) != std::string::npos); ++withRepl; }          // 올바른 입력은 그대로, 아니면 대체 문자가 있다
        int n = (int)s.size();
        for (int mask = 0; mask < (1 << (n > 0 ? n - 1 : 0)); ++mask) { std::vector<size_t> cuts; for (int b = 0; b + 1 < n; ++b) if (mask >> b & 1) cuts.push_back((size_t)b + 1); assert(streamed(s, cuts) == ref); ++splits; }     // 청크 분할과 무관
    }
    assert(valid > 100 && withRepl > 100000 && splits > 1000000);
    // ③ 무작위 긴 입력과 토큰 단위 스트리밍
    std::mt19937 rng(321); std::vector<std::string> bits = {"hello", " 한글", "😀", "\xFF", "\xC3", "\x80", "é", "\n", "\xF0\x9F", "\xE2\x82\xAC"};
    for (int it = 0; it < 2000; ++it) {
        std::string s; for (int k = 0, n = (int)(rng() % 15); k < n; ++k) s += bits[rng() % bits.size()];
        std::string ref = decodeAll(s); assert(validUtf8(ref));
        std::vector<size_t> cuts; for (size_t p = 1; p < s.size(); p++) if (rng() % 4 == 0) cuts.push_back(p);
        assert(streamed(s, cuts) == ref);
        if (validUtf8(s)) { StreamDecoder sd; std::string acc; size_t prev = 0; for (size_t c : cuts) { std::string part = sd.feed(s.substr(prev, c - prev)); assert(validUtf8(part)); acc += part; prev = c; } acc += sd.feed(s.substr(prev)); assert(!sd.hasPending() && acc == s); }     // 완성된 글자만 나온다
    }
    std::cout << "Detokenize: " << all.size() << " short byte strings x every chunking (" << splits << " streams) matched the one-shot decoder; " << valid << " valid inputs passed through unchanged, " << withRepl << " invalid ones were repaired with U+FFFD and the output was always valid UTF-8" << std::endl;
    return 0;
}
// Time Complexity: O(총 길이)
// Space Complexity: O(총 길이)
```
## LLM 토크나이저는 왜 필요한가?
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// 모델은 정수만 다룬다.  텍스트를 어떤 단위로 쪼갤지는 어휘 크기와 시퀀스 길이의 교환이다:
//   글자 단위: 어휘 작음, 시퀀스 매우 김   /   단어 단위: 시퀀스 짧음, 어휘 거대 + 처음 보는 단어(OOV)를 표현할 수 없음
//   서브워드(BPE): 둘의 중간, OOV 없음 (최악에도 글자 단위로 분해)
// 실험: 24 개 음절로 만든 1 500 단어의 사전(지프 분포로 등장)에서 학습 문장 30 000 단어를 뽑아 BPE 를 학습하고, 새로 뽑은 8 000 단어 + 사전에 없던 합성어 300 개로 시험한다
// 검증: ① 어휘 크기 V 가 커질수록 BPE 의 총 토큰 수가 줄어든다(비증가, 처음에는 엄격히 감소)  ② BPE 는 어떤 시험 단어도 OOV 없이 표현하고 이어 붙이면 원문  ③ 단어 단위는 어휘 V 개로 OOV 가 생기며 V 가 커질수록 줄어듦
//        ④ 같은 어휘 크기에서 BPE 의 토큰 수는 글자 단위보다 훨씬 짧고, 단어 단위(OOV 를 한 토큰으로 칠 때)보다 길지만 OOV 가 없다.  정수 ID 학습기와 단순 학습기의 병합 목록이 일치
typedef std::vector<std::string> Seq;
typedef std::pair<std::string, std::string> Pair;
std::vector<Pair> trainBPE(const std::map<std::string, long>& wordFreq, int merges) {            // 정수 ID 기반: 병합마다 쌍 빈도를 다시 센다 (동률은 문자열 쌍의 사전순)
    std::vector<std::string> tok; std::map<std::string, int> id;
    auto intern = [&](const std::string& s) { auto it = id.find(s); if (it != id.end()) return it->second; tok.push_back(s); return id[s] = (int)tok.size() - 1; };
    std::vector<std::vector<int>> words; std::vector<long> fr;
    for (auto& kv : wordFreq) { std::vector<int> w; for (char c : kv.first) w.push_back(intern(std::string(1, c))); words.push_back(w); fr.push_back(kv.second); }
    std::vector<Pair> out;
    for (int it = 0; it < merges; it++) {
        std::map<std::pair<int, int>, long> cnt; for (size_t w = 0; w < words.size(); w++) for (size_t i = 0; i + 1 < words[w].size(); i++) cnt[{words[w][i], words[w][i + 1]}] += fr[w];
        std::pair<int, int> best{-1, -1}; long bc = 1;
        for (auto& kv : cnt) if (kv.second > bc || (kv.second == bc && best.first >= 0 && Pair{tok[kv.first.first], tok[kv.first.second]} < Pair{tok[best.first], tok[best.second]})) { bc = kv.second; best = kv.first; }
        if (best.first < 0) break;
        out.push_back({tok[best.first], tok[best.second]}); int nid = intern(tok[best.first] + tok[best.second]);
        for (auto& w : words) { std::vector<int> t; for (size_t i = 0; i < w.size(); i++) { if (i + 1 < w.size() && w[i] == best.first && w[i + 1] == best.second) { t.push_back(nid); i++; } else t.push_back(w[i]); } w.swap(t); }
    }
    return out;
}
std::vector<Pair> trainSimple(const std::map<std::string, long>& wordFreq, int merges) {          // 문자열 Seq 로 직접 (느리지만 단순): 독립 구현
    std::vector<std::pair<Seq, long>> seqs; for (auto& kv : wordFreq) { Seq s; for (char c : kv.first) s.push_back(std::string(1, c)); seqs.push_back({s, kv.second}); }
    std::vector<Pair> out;
    for (int it = 0; it < merges; it++) {
        std::map<Pair, long> cnt; for (auto& s : seqs) for (size_t i = 0; i + 1 < s.first.size(); i++) cnt[{s.first[i], s.first[i + 1]}] += s.second;
        Pair best; long bc = 1; bool have = false; for (auto& kv : cnt) if (kv.second > bc) { bc = kv.second; best = kv.first; have = true; }
        if (!have) break; out.push_back(best);
        for (auto& s : seqs) { Seq t; for (size_t i = 0; i < s.first.size(); i++) { if (i + 1 < s.first.size() && s.first[i] == best.first && s.first[i + 1] == best.second) { t.push_back(best.first + best.second); i++; } else t.push_back(s.first[i]); } s.first.swap(t); }
    }
    return out;
}
Seq encode(const std::string& w, const std::map<Pair, int>& rank, size_t maxRank) {                // 순위가 maxRank 미만인 병합만 사용 (작은 어휘 = 병합 목록의 앞부분)
    Seq s; for (char c : w) s.push_back(std::string(1, c));
    for (;;) {
        int best = (int)maxRank; Pair bp; bool have = false;
        for (size_t i = 0; i + 1 < s.size(); i++) { auto it = rank.find({s[i], s[i + 1]}); if (it != rank.end() && it->second < best) { best = it->second; bp = it->first; have = true; } }
        if (!have) return s;
        Seq t; for (size_t i = 0; i < s.size(); i++) { if (i + 1 < s.size() && s[i] == bp.first && s[i + 1] == bp.second) { t.push_back(bp.first + bp.second); i++; } else t.push_back(s[i]); }
        s.swap(t);
    }
}

int main() {
    const char* syl[] = {"ka", "ro", "mi", "ta", "ne", "su", "lo", "pa", "di", "ve", "gu", "ho", "bi", "ra", "nu", "se", "to", "li", "ma", "fo", "ke", "za", "wi", "yu"};
    std::mt19937 rng(12345);
    std::set<std::string> lexSet; std::vector<std::string> lex;
    while (lex.size() < 1500) { std::string w; for (int k = 0, n = 2 + (int)(rng() % 3); k < n; ++k) w += syl[rng() % 24]; if (lexSet.insert(w).second) lex.push_back(w); }
    std::vector<double> cum; { double s = 0; for (size_t r = 0; r < lex.size(); r++) { s += 1.0 / (double)(r + 1); cum.push_back(s); } }          // 지프 분포 (순위 r 의 가중치 1/r)
    auto draw = [&]() { double u = std::uniform_real_distribution<double>(0, cum.back())(rng); return lex[std::lower_bound(cum.begin(), cum.end(), u) - cum.begin()]; };
    std::map<std::string, long> trainFreq; for (int i = 0; i < 30000; ++i) trainFreq[draw()]++;
    std::vector<std::string> test; for (int i = 0; i < 8000; ++i) test.push_back(draw());
    size_t novel = 0; while (novel < 300) { std::string w; for (int k = 0, n = 2 + (int)(rng() % 3); k < n; ++k) w += syl[rng() % 24]; if (!lexSet.count(w)) { test.push_back(w); ++novel; } }       // 사전에 없던 합성어
    std::set<char> alphabet; for (auto& kv : trainFreq) for (char c : kv.first) alphabet.insert(c); int B = (int)alphabet.size();
    const int MAXM = 800; std::vector<Pair> merges = trainBPE(trainFreq, MAXM);
    { std::map<std::string, long> small; int k = 0; for (auto& kv : trainFreq) { if (k++ >= 120) break; small[kv.first] = kv.second; } assert(trainBPE(small, 40) == trainSimple(small, 40)); }       // 독립 구현과 일치
    std::map<Pair, int> rank; for (size_t i = 0; i < merges.size(); i++) rank.emplace(merges[i], (int)i);
    long charTokens = 0; for (auto& w : test) charTokens += (long)w.size();
    std::map<std::string, long> byFreq = trainFreq; std::vector<std::pair<long, std::string>> rankedWords; for (auto& kv : trainFreq) rankedWords.push_back({kv.second, kv.first}); std::sort(rankedWords.rbegin(), rankedWords.rend());
    std::cout << "alphabet " << B << ", " << merges.size() << " merges learned; test words " << test.size() << " (" << charTokens << " characters)" << std::endl;
    std::vector<long> bpeTotals, oovCounts; std::vector<int> sizes = {B, 50, 100, 200, 400, 800};
    for (int V : sizes) {
        size_t m = V <= B ? 0 : std::min<size_t>(merges.size(), (size_t)(V - B)); long total = 0;
        std::map<std::string, Seq> cache;
        for (auto& w : test) {
            auto it = cache.find(w); if (it == cache.end()) it = cache.emplace(w, encode(w, rank, m)).first;
            std::string j; for (auto& t : it->second) j += t; assert(j == w); total += (long)it->second.size();             // ② OOV 없이 원문 복원 (합성어 포함)
        }
        bpeTotals.push_back(total);
        std::set<std::string> wv; for (int i = 0; i < V && i < (int)rankedWords.size(); i++) wv.insert(rankedWords[i].second);          // 단어 단위: 빈도 상위 V 개 단어만 어휘
        long oov = 0; for (auto& w : test) oov += !wv.count(w); oovCounts.push_back(oov);
        std::cout << "V=" << V << ": BPE " << total << " tokens (" << (double)total / test.size() << "/word), word-level OOV " << oov << " (" << 100.0 * oov / test.size() << "%)" << std::endl;
    }
    // ① 토큰 수는 어휘가 커질수록 줄어든다
    assert(bpeTotals[0] == charTokens);                                                                                    // 병합 0 개 = 글자 단위
    for (size_t i = 1; i < bpeTotals.size(); i++) assert(bpeTotals[i] <= bpeTotals[i - 1]);
    assert(bpeTotals[1] < bpeTotals[0] && bpeTotals[2] < bpeTotals[1] && bpeTotals[3] < bpeTotals[2] && bpeTotals[4] < bpeTotals[3]);
    // ③ 단어 단위 OOV 는 V 가 커질수록 줄어든다 (하지만 사전에 없던 합성어 300 개는 영영 OOV)
    for (size_t i = 1; i < oovCounts.size(); i++) assert(oovCounts[i] <= oovCounts[i - 1]);
    assert(oovCounts.back() >= (long)novel && oovCounts[1] > (long)test.size() / 10 && oovCounts[0] > (long)test.size() / 3);       // 어휘 50 개면 시험 단어의 10 % 이상이 OOV, 합성어는 어떤 V 에서도 OOV
    // ④ 길이와 어휘의 교환: 어휘 400 에서 BPE 는 글자 단위의 절반 이하 길이, 단어 단위(어휘 1500 개 전부)보다는 길다
    double bpePerWord = (double)bpeTotals[4] / test.size(), charPerWord = (double)charTokens / test.size();
    assert(bpePerWord < 0.5 * charPerWord && bpePerWord > 1.0 && bpeTotals[4] > (long)test.size() && (int)lex.size() > 3 * 400);
    std::cout << "tokens per word: char=" << charPerWord << " bpe(V=400)=" << bpePerWord << " word=1 (needs " << lex.size() << " vocabulary entries and fails on " << novel << " novel words)" << std::endl;
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
