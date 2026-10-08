# Part 1. 문자열의 기초
## CreateString()
### 대표코드
```cpp
#include <iostream>
#include <cstring>
#include <string>
#include <cassert>

// C 문자열은 끝에 '\0' 을 두는 방식(널 종단)이고, std::string 은 길이를 따로 저장한다.
// 그래서 std::string 은 중간에 '\0' 이 들어 있어도 되고, 길이를 O(1)에 안다.
int main() {
    char c[] = "hello";                    // 'h','e','l','l','o','\0' -> 6바이트
    assert(sizeof(c) == 6 && std::strlen(c) == 5);
    std::string s("hello");
    assert(s.size() == 5 && s == c);
    std::string t("a\0b", 3);              // 길이를 명시하면 '\0' 도 문자열의 일부
    assert(t.size() == 3);
    assert(std::strlen(t.c_str()) == 1);   // C 함수는 첫 '\0' 에서 멈춘다
    std::cout << "CreateString: c-string " << sizeof(c) << " bytes, std::string size " << s.size() << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
## Length()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <cassert>

// "길이"는 세 가지가 다를 수 있다: 바이트 수, 코드 포인트 수, (눈에 보이는) 글자 수.
// UTF-8 에서 연속 바이트는 상위 비트가 10xxxxxx 이므로 그것을 제외하고 세면 코드 포인트 수가 된다
size_t byteLength(const char* s) { size_t n = 0; while (s[n]) n++; return n; }         // strlen 과 같은 O(n)
size_t codePointLength(const std::string& s) {
    size_t n = 0;
    for (unsigned char c : s) if ((c & 0xC0) != 0x80) n++;
    return n;
}

int main() {
    std::string ascii = "hello", korean = "한글", emoji = "a😀b";
    assert(byteLength("hello") == 5);
    assert(ascii.size() == 5 && codePointLength(ascii) == 5);
    assert(korean.size() == 6 && codePointLength(korean) == 2);        // 한글 한 글자 = 3바이트
    assert(emoji.size() == 6 && codePointLength(emoji) == 3);          // 😀 = 4바이트
    std::cout << "bytes=" << korean.size() << " code points=" << codePointLength(korean) << std::endl;
    return 0;
}
// Time Complexity: 바이트 길이 O(1)(std::string), 코드 포인트 수 O(n)
// Space Complexity: O(1)
```
## Concat()
### 대표코드
```cpp
#include <iostream>
#include <cstring>
#include <cassert>

// 문자열 이어 붙이기: 매번 새로 할당해 복사하면 k번 붙일 때 O(k^2), 용량을 2배씩 늘리면 분할상환 O(k)
struct Buf {
    char* p = nullptr; size_t n = 0, cap = 0; long copies = 0; bool doubling;
    explicit Buf(bool d) : doubling(d) {}
    ~Buf() { delete[] p; }
    void append(char c) {
        if (n + 1 > cap) {
            size_t ncap = doubling ? (cap ? cap * 2 : 1) : n + 1;      // 정확히 필요한 만큼만 vs 2배 성장
            char* q = new char[ncap];
            if (n) std::memcpy(q, p, n);
            copies += n;
            delete[] p; p = q; cap = ncap;
        }
        p[n++] = c; copies++;
    }
};

int main() {
    const int K = 2000;
    Buf naive(false), amort(true);
    for (int i = 0; i < K; i++) { naive.append('x'); amort.append('x'); }
    assert(naive.n == K && amort.n == K);
    assert(naive.copies > 100 * amort.copies / 4);                    // 복사 횟수: 약 K^2/2 vs 약 3K
    std::cout << "copies: naive=" << naive.copies << " doubling=" << amort.copies << std::endl;
    return 0;
}
// Time Complexity: 2배 성장 시 분할상환 O(1)/문자
// Space Complexity: O(n)
```
## Substring()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <cassert>

// substr 은 새 문자열을 만들어 복사(O(len))하고, string_view 는 원본을 가리키는 (포인터, 길이)라 O(1)이다.
// 대신 view 는 원본 문자열보다 오래 살면 안 된다 (dangling)
int main() {
    std::string s = "the quick brown fox";
    std::string copy = s.substr(4, 5);                  // "quick" 복사
    std::string_view view(s.data() + 4, 5);             // "quick" 을 가리키기만 함
    assert(copy == "quick" && view == "quick");
    assert(copy.data() != s.data() + 4);                // 복사본은 다른 메모리
    assert(view.data() == s.data() + 4);                // 뷰는 원본 메모리를 그대로 공유
    s[4] = 'Q';                                          // 원본을 바꾸면 뷰에는 반영되고 복사본은 그대로
    assert(view == "Quick" && copy == "quick");
    std::cout << "substr copy=" << copy << ", view=" << view << std::endl;
    return 0;
}
// Time Complexity: substr O(len), string_view O(1)
// Space Complexity: substr O(len), string_view O(1)
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
#include <iostream>
#include <string>
#include <utility>
#include <cassert>

// 문자열 비교는 O(1)이 아니다: 공통 접두사의 길이만큼 걸린다 (같은 문자열이면 전체 길이 L).
// 그래서 해시맵의 키 비교, 정렬(비교 O(L) × n log n), 이진 탐색에서 L 이 곱해진다
std::pair<int, long> countingCompare(const std::string& a, const std::string& b) {
    long ops = 0;
    size_t n = std::min(a.size(), b.size());
    for (size_t i = 0; i < n; i++) { ops++; if (a[i] != b[i]) return {a[i] < b[i] ? -1 : 1, ops}; }
    return {a.size() == b.size() ? 0 : (a.size() < b.size() ? -1 : 1), ops};
}

int main() {
    const size_t L = 100000;
    std::string a(L, 'x'), b(L, 'x'), c = "y" + std::string(L - 1, 'x');
    assert(countingCompare(a, b).second == (long)L);      // 같은 문자열: 끝까지 L번
    assert(countingCompare(a, c).second == 1);            // 첫 글자에서 다르면 1번
    // 공통 접두사가 긴 키가 많으면 정렬·탐색이 느려진다: 비교 1회가 O(L)
    std::string d = a; d.back() = 'y';
    assert(countingCompare(a, d).second == (long)L);      // 마지막 글자만 다른 최악의 경우
    // 완화책: 길이를 먼저 비교하거나 해시를 캐시해 두면 서로 다른 문자열은 O(1)에 걸러진다
    assert(a.size() == b.size() && std::hash<std::string>{}(a) == std::hash<std::string>{}(b));
    std::cout << "compare cost: equal=" << countingCompare(a, b).second << " differ-at-0=" << countingCompare(a, c).second << std::endl;
    return 0;
}
// Time Complexity: O(공통 접두사 길이), 최악 O(L)
// Space Complexity: O(1)
```
## Reverse()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <cassert>

// 바이트 단위로 뒤집으면 UTF-8 이 깨진다 -> 코드 포인트 단위로 쪼개서 뒤집어야 한다
void reverseBytes(std::string& s) { for (size_t i = 0, j = s.size(); i + 1 < j; i++, j--) std::swap(s[i], s[j - 1]); }   // 두 포인터, 제자리
std::string reverseCodePoints(const std::string& s) {
    std::vector<std::string> cps;
    for (size_t i = 0; i < s.size();) {
        size_t len = 1;
        unsigned char c = s[i];
        if (c >= 0xF0) len = 4; else if (c >= 0xE0) len = 3; else if (c >= 0xC0) len = 2;
        cps.push_back(s.substr(i, len)); i += len;
    }
    std::string r;
    for (size_t i = cps.size(); i-- > 0;) r += cps[i];
    return r;
}

int main() {
    std::string a = "hello";
    reverseBytes(a);
    assert(a == "olleh");
    assert(reverseCodePoints("가나다") == "다나가");                     // 올바른 결과
    std::string bad = "가나다"; reverseBytes(bad);
    assert(bad != "다나가");                                             // 바이트 뒤집기는 깨진 문자열을 만든다
    std::cout << "Reverse verified." << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: 바이트 뒤집기 O(1), 코드 포인트 뒤집기 O(n)
```
## Split()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <cassert>

// 구분자로 나누기: string_view 를 반환하면 복사 없이 O(n). 빈 토큰("a,,b,")을 버릴지 유지할지가 중요한 설계 선택이다
std::vector<std::string_view> split(std::string_view s, char delim, bool keepEmpty = true) {
    std::vector<std::string_view> out;
    size_t start = 0;
    for (size_t i = 0; i <= s.size(); i++) {
        if (i == s.size() || s[i] == delim) {
            if (keepEmpty || i > start) out.push_back(s.substr(start, i - start));
            start = i + 1;
        }
    }
    return out;
}

int main() {
    auto t = split("a,,b,", ',');
    assert((t == std::vector<std::string_view>{"a", "", "b", ""}));          // 빈 토큰 유지
    auto u = split("a,,b,", ',', false);
    assert((u == std::vector<std::string_view>{"a", "b"}));
    assert(split("", ',').size() == 1 && split("", ',', false).empty());
    assert(split("no-delim", ',').size() == 1);
    std::cout << "Split: " << t.size() << " tokens (keep empty), " << u.size() << " (drop empty)" << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(토큰 수) (문자 복사 없음)
```
## Immutable String
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <unordered_set>
#include <cassert>

// 불변 문자열(Java String, Python str): 한 번 만들면 바뀌지 않는다.
//  + 복사는 포인터 공유로 O(1), 스레드 안전, 해시값을 캐시할 수 있어 해시맵 키로 안전
//  + 같은 내용을 하나만 두는 인터닝(interning)으로 비교를 포인터 비교 O(1)로 줄일 수 있다
//  - 수정마다 새 문자열이 만들어진다 (그래서 StringBuilder 같은 가변 버퍼가 따로 필요)
class IStr {
    std::shared_ptr<const std::string> p;
public:
    explicit IStr(std::string s) : p(std::make_shared<const std::string>(std::move(s))) {}
    const std::string& str() const { return *p; }
    IStr concat(const IStr& o) const { return IStr(*p + *o.p); }                // 새 객체를 반환 (원본은 불변)
    long refs() const { return p.use_count(); }
    bool sameObject(const IStr& o) const { return p == o.p; }
};
class InternPool {
    std::unordered_set<std::string> pool;
public:
    const std::string* intern(const std::string& s) { return &*pool.insert(s).first; }
};

int main() {
    IStr a("hello");
    IStr b = a;                                         // 복사 = 포인터 공유
    assert(a.sameObject(b) && a.refs() == 2);
    IStr c = a.concat(IStr(" world"));
    assert(a.str() == "hello" && c.str() == "hello world");               // 원본은 그대로
    InternPool pool;
    const std::string* x = pool.intern("same"); const std::string* y = pool.intern(std::string("sa") + "me");
    assert(x == y);                                     // 내용이 같으면 같은 객체 -> == 가 포인터 비교
    std::cout << "ImmutableString verified." << std::endl;
    return 0;
}
// Time Complexity: 복사 O(1), 연결 O(n+m), 인터닝 평균 O(len)
// Space Complexity: O(n)
```
# Part 2. 기본 연산 응용
## Palindrome()
### 대표코드
```cpp
#include <iostream>
#include <cctype>
#include <string>
#include <cassert>

// 회문 판별: 양 끝에서 안쪽으로 두 포인터. 알파벳·숫자만 보고 대소문자는 무시
bool isPalindrome(const std::string& s) {
    int i = 0, j = (int)s.size() - 1;
    while (i < j) {
        while (i < j && !std::isalnum((unsigned char)s[i])) i++;
        while (i < j && !std::isalnum((unsigned char)s[j])) j--;
        if (std::tolower((unsigned char)s[i]) != std::tolower((unsigned char)s[j])) return false;
        i++; j--;
    }
    return true;
}

int main() {
    assert(isPalindrome("A man, a plan, a canal: Panama"));
    assert(isPalindrome("racecar") && isPalindrome("") && isPalindrome("a"));
    assert(!isPalindrome("hello"));
    std::cout << "Palindrome verified." << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(1)
```
## Anagram()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 애너그램: 글자 빈도가 같으면 된다.  (1) 빈도 배열 비교 O(n)  (2) 정렬한 문자열을 키로 묶으면 단어 그룹핑
bool isAnagram(const std::string& a, const std::string& b) {
    if (a.size() != b.size()) return false;
    int cnt[256] = {0};
    for (unsigned char c : a) cnt[c]++;
    for (unsigned char c : b) if (--cnt[c] < 0) return false;
    return true;
}
std::vector<std::vector<std::string>> groupAnagrams(const std::vector<std::string>& words) {
    std::map<std::string, std::vector<std::string>> g;
    for (auto& w : words) { std::string key = w; std::sort(key.begin(), key.end()); g[key].push_back(w); }
    std::vector<std::vector<std::string>> out;
    for (auto& kv : g) out.push_back(kv.second);
    return out;
}

int main() {
    assert(isAnagram("listen", "silent") && !isAnagram("hello", "world") && !isAnagram("a", "ab"));
    auto g = groupAnagrams({"eat", "tea", "tan", "ate", "nat", "bat"});
    assert(g.size() == 3);
    size_t biggest = 0; for (auto& v : g) biggest = std::max(biggest, v.size());
    assert(biggest == 3);
    std::cout << "Anagram groups: " << g.size() << std::endl;
    return 0;
}
// Time Complexity: 판별 O(n), 그룹핑 O(총 길이 · log 길이)
// Space Complexity: O(총 길이)
```
## RunLengthEncoding()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <cassert>

// 런 길이 부호화(RLE): 연속된 같은 문자를 (문자, 반복 횟수)로 줄인다. 반복이 많은 데이터(단색 이미지, BWT 결과)에서 효과적
std::string rleEncode(const std::string& s) {
    std::string out;
    for (size_t i = 0; i < s.size();) {
        size_t j = i; while (j < s.size() && s[j] == s[i]) j++;
        out += s[i]; out += std::to_string(j - i);
        i = j;
    }
    return out;
}
std::string rleDecode(const std::string& e) {
    std::string out;
    for (size_t i = 0; i < e.size();) {
        char c = e[i++]; size_t n = 0;
        while (i < e.size() && std::isdigit((unsigned char)e[i])) n = n * 10 + (e[i++] - '0');
        out.append(n, c);
    }
    return out;
}

int main() {
    assert(rleEncode("aaabccdddd") == "a3b1c2d4");
    assert(rleDecode("a3b1c2d4") == "aaabccdddd");
    std::string big(1000, 'z');
    assert(rleEncode(big) == "z1000" && rleDecode(rleEncode(big)) == big);
    assert(rleEncode("abc").size() > std::string("abc").size());          // 반복이 없으면 오히려 커진다
    std::cout << "RLE verified." << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
# Part 3. 인코딩
## ASCII부터 Unicode까지
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <cassert>

// ASCII(7비트, 128자) -> 각국 확장 코드페이지 -> Unicode(코드 포인트 U+0000 ~ U+10FFFF) 와 그 인코딩 UTF-8/16/32.
// UTF-8 은 ASCII 와 바이트가 완전히 같아(상위 호환) 인터넷 표준이 되었다. 코드 포인트를 1~4바이트로 부호화
std::string utf8Encode(uint32_t cp) {
    std::string s;
    if (cp < 0x80)         { s += (char)cp; }
    else if (cp < 0x800)   { s += (char)(0xC0 | cp >> 6); s += (char)(0x80 | (cp & 0x3F)); }
    else if (cp < 0x10000) { s += (char)(0xE0 | cp >> 12); s += (char)(0x80 | (cp >> 6 & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    else                   { s += (char)(0xF0 | cp >> 18); s += (char)(0x80 | (cp >> 12 & 0x3F)); s += (char)(0x80 | (cp >> 6 & 0x3F)); s += (char)(0x80 | (cp & 0x3F)); }
    return s;
}

int main() {
    assert(utf8Encode('A') == "A");                   // ASCII 는 1바이트, 값도 그대로
    assert(utf8Encode(0x00E9).size() == 2);           // é
    assert(utf8Encode(0xD55C).size() == 3 && utf8Encode(0xD55C) == "한");
    assert(utf8Encode(0x1F600).size() == 4 && utf8Encode(0x1F600) == "😀");
    for (unsigned char c : utf8Encode(0x1F600)) std::cout << std::hex << (int)c << " ";
    std::cout << std::endl;
    return 0;
}
// Time Complexity: O(1)
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
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <cassert>

// 로프(Rope): 긴 문자열을 이진 트리로 표현한다. 내부 노드는 "왼쪽 부분 트리의 길이(weight)"를 갖고 리프는 짧은 문자열을 갖는다.
// 연결은 새 루트를 만들 뿐이라 O(1)(복사 없음), 분할·색인은 O(depth).  텍스트 에디터의 거대한 문서 편집에 쓰인다.
// (노드는 불변이라 공유해도 안전하다 = 영속 자료구조. 여기서는 균형 재조정을 생략)
struct Node;
typedef std::shared_ptr<const Node> P;
struct Node { P l, r; size_t w; std::string s; };           // 리프: s 사용, 내부: l/r, w = 왼쪽 길이
size_t len(const P& n) { return !n ? 0 : (n->l || n->r) ? n->w + len(n->r) : n->s.size(); }
P leaf(const std::string& s) { return std::make_shared<const Node>(Node{nullptr, nullptr, s.size(), s}); }
P concat(P a, P b) { if (!a) return b; if (!b) return a; return std::make_shared<const Node>(Node{a, b, len(a), ""}); }
char at(const P& n, size_t i) {
    if (!(n->l || n->r)) return n->s[i];
    return i < n->w ? at(n->l, i) : at(n->r, i - n->w);
}
std::pair<P, P> split(const P& n, size_t i) {                // [0,i) 와 [i,len)
    if (!n) return {nullptr, nullptr};
    if (!(n->l || n->r)) return {i ? leaf(n->s.substr(0, i)) : nullptr, i < n->s.size() ? leaf(n->s.substr(i)) : nullptr};
    if (i < n->w) { auto t = split(n->l, i); return {t.first, concat(t.second, n->r)}; }
    auto t = split(n->r, i - n->w); return {concat(n->l, t.first), t.second};
}
std::string str(const P& n) { return !n ? "" : (n->l || n->r) ? str(n->l) + str(n->r) : n->s; }

int main() {
    P doc = concat(leaf("Hello, "), leaf("world!"));
    assert(len(doc) == 13 && at(doc, 7) == 'w');
    auto parts = split(doc, 7);                                 // "Hello, " | "world!"
    P edited = concat(concat(parts.first, leaf("beautiful ")), parts.second);   // 중간 삽입 = 분할 + 연결
    assert(str(edited) == "Hello, beautiful world!");
    assert(str(doc) == "Hello, world!");                        // 원본은 그대로 (영속성)
    assert(at(edited, 7) == 'b' && len(edited) == 23);
    std::cout << "Rope: " << str(edited) << std::endl;
    return 0;
}
// Time Complexity: 연결 O(1), 분할/색인 O(깊이)
// Space Complexity: O(노드 수), 편집 후에도 원본 공유
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
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 단순 검색: 텍스트의 모든 위치에서 패턴을 처음부터 비교. 최악 O(n·m): "aaaa…a" 에서 "aaa…ab" 찾기
std::vector<size_t> naiveSearch(const std::string& t, const std::string& p, long& comparisons) {
    std::vector<size_t> res; comparisons = 0;
    for (size_t i = 0; i + p.size() <= t.size(); i++) {
        size_t j = 0;
        while (j < p.size()) { comparisons++; if (t[i + j] != p[j]) break; j++; }
        if (j == p.size()) res.push_back(i);
    }
    return res;
}

int main() {
    long c;
    auto r = naiveSearch("abracadabra", "abra", c);
    assert((r == std::vector<size_t>{0, 7}));
    naiveSearch(std::string(1000, 'a'), std::string(50, 'a') + "b", c);
    assert(c > 40000);                                            // 약 (n-m)·m 번 비교: 최악의 경우
    std::cout << "worst case comparisons: " << c << std::endl;
    return 0;
}
// Time Complexity: 평균 O(n + m), 최악 O(n·m)
// Space Complexity: O(1)
```
## KMP()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// KMP: 패턴 자체의 접두사-접미사 일치 정보(실패 함수 π)로, 불일치가 나도 텍스트 포인터를 뒤로 되돌리지 않는다. 항상 O(n + m)
std::vector<int> failure(const std::string& p) {
    std::vector<int> pi(p.size(), 0);
    for (size_t i = 1, k = 0; i < p.size(); i++) {
        while (k > 0 && p[i] != p[k]) k = pi[k - 1];             // 이미 맞춘 부분의 "가장 긴 테두리"로 후퇴
        if (p[i] == p[k]) k++;
        pi[i] = k;
    }
    return pi;
}
std::vector<size_t> kmp(const std::string& t, const std::string& p) {
    std::vector<size_t> res; auto pi = failure(p);
    for (size_t i = 0, k = 0; i < t.size(); i++) {
        while (k > 0 && t[i] != p[k]) k = pi[k - 1];
        if (t[i] == p[k]) k++;
        if (k == p.size()) { res.push_back(i + 1 - k); k = pi[k - 1]; }
    }
    return res;
}

int main() {
    assert((failure("ababaca") == std::vector<int>{0, 0, 1, 2, 3, 0, 1}));
    assert((kmp("abracadabra", "abra") == std::vector<size_t>{0, 7}));
    assert((kmp("aaaaa", "aa") == std::vector<size_t>{0, 1, 2, 3}));                  // 겹치는 일치도 모두 찾는다
    assert(kmp(std::string(100000, 'a'), std::string(500, 'a') + "b").empty());        // 나이브라면 5천만 번 비교하는 입력
    std::cout << "KMP verified." << std::endl;
    return 0;
}
// Time Complexity: O(n + m)
// Space Complexity: O(m)
```
# Part 6. 패턴 검색
## RabinKarp()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// 라빈-카프: 패턴의 해시와 텍스트의 길이 m 윈도우 해시를 비교한다. 윈도우를 한 칸 밀 때 해시를 O(1)로 갱신(롤링 해시).
// 해시가 같을 때만 실제 문자열을 비교하므로 정확하고, 여러 패턴을 동시에 찾을 때 특히 유리하다
std::vector<size_t> rabinKarp(const std::string& t, const std::string& p, size_t& spurious) {
    const uint64_t B = 256, M = 1000000007ULL;
    std::vector<size_t> res; spurious = 0;
    size_t n = t.size(), m = p.size();
    if (m == 0 || m > n) return res;
    uint64_t hp = 0, ht = 0, pw = 1;                           // pw = B^(m-1) mod M
    for (size_t i = 0; i < m; i++) { hp = (hp * B + (unsigned char)p[i]) % M; ht = (ht * B + (unsigned char)t[i]) % M; if (i) pw = pw * B % M; }
    for (size_t i = 0; i + m <= n; i++) {
        if (hp == ht) { if (t.compare(i, m, p) == 0) res.push_back(i); else spurious++; }   // 해시 충돌(가짜 일치) 걸러내기
        if (i + m < n) ht = ((ht + M - (unsigned char)t[i] * pw % M) * B + (unsigned char)t[i + m]) % M;   // 롤링 갱신
    }
    return res;
}

int main() {
    size_t sp;
    assert((rabinKarp("abracadabra", "abra", sp) == std::vector<size_t>{0, 7}));
    assert(rabinKarp("aaaaaa", "aaa", sp).size() == 4);
    assert(rabinKarp("hello", "world", sp).empty() && rabinKarp("abc", "abcd", sp).empty());
    std::cout << "RabinKarp verified (spurious hits: " << sp << ")" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(n + m), 최악 O(n·m)
// Space Complexity: O(1)
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
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// Z 배열: z[i] = s[i..] 와 s 의 최장 공통 접두사 길이. 이미 구한 [l, r) 구간 안에서는 값을 재사용해 O(n).
// 패턴 검색: pattern + '\1' + text 에서 z[i] == |pattern| 인 위치
std::vector<int> zArray(const std::string& s) {
    int n = s.size(); std::vector<int> z(n, 0);
    for (int i = 1, l = 0, r = 0; i < n; i++) {
        if (i < r) z[i] = std::min(r - i, z[i - l]);
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;
        if (i + z[i] > r) { l = i; r = i + z[i]; }
    }
    return z;
}
std::vector<size_t> zSearch(const std::string& t, const std::string& p) {
    std::vector<size_t> res; auto z = zArray(p + '\1' + t);
    for (size_t i = p.size() + 1; i < z.size(); i++) if (z[i] == (int)p.size()) res.push_back(i - p.size() - 1);
    return res;
}

int main() {
    assert((zArray("aabxaab") == std::vector<int>{0, 1, 0, 0, 3, 1, 0}));
    assert((zSearch("abracadabra", "abra") == std::vector<size_t>{0, 7}));
    assert((zSearch("aaaaa", "aa") == std::vector<size_t>{0, 1, 2, 3}));
    std::cout << "ZAlgorithm verified." << std::endl;
    return 0;
}
// Time Complexity: O(n + m)
// Space Complexity: O(n + m)
```
## LongestRepeatedSubstring()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <cassert>

// 가장 긴 반복 부분 문자열(두 번 이상 나타나는 가장 긴 부분 문자열; 겹쳐도 됨).
// "길이 L 짜리 반복이 있다" 는 L 에 대해 단조 -> 이분 탐색 + 롤링 해시(일치 후 실제 비교로 확인)
std::string longestRepeated(const std::string& s) {
    const unsigned long long B = 131;
    size_t n = s.size();
    auto check = [&](size_t L, size_t& pos) {
        std::unordered_map<unsigned long long, size_t> seen;
        unsigned long long h = 0, pw = 1;
        for (size_t i = 0; i < L; i++) { h = h * B + (unsigned char)s[i]; if (i) pw *= B; }   // 2^64 로 자연 오버플로
        for (size_t i = 0;; i++) {
            auto it = seen.find(h);
            if (it != seen.end() && s.compare(it->second, L, s, i, L) == 0) { pos = i; return true; }
            seen[h] = i;
            if (i + L >= n) break;
            h = (h - (unsigned char)s[i] * pw) * B + (unsigned char)s[i + L];
        }
        return false;
    };
    size_t lo = 1, hi = n - 1, best = 0, bestPos = 0;
    while (n > 1 && lo <= hi) {
        size_t mid = (lo + hi) / 2, p;
        if (check(mid, p)) { best = mid; bestPos = p; lo = mid + 1; } else hi = mid - 1;
    }
    return s.substr(bestPos, best);
}

int main() {
    assert(longestRepeated("banana") == "ana");               // 겹치는 반복도 허용
    assert(longestRepeated("abcabcabc") == "abcabc");
    assert(longestRepeated("abcdef").empty());
    std::cout << "LongestRepeatedSubstring(banana) = " << longestRepeated("banana") << std::endl;
    return 0;
}
// Time Complexity: O(n log n)
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
#include <iostream>
#include <array>
#include <memory>
#include <string>
#include <vector>
#include <cassert>

// 트라이(문자열 관점의 요약, 정본은 Tree.md Part 9): 문자열을 한 글자씩 간선에 놓은 트리.
// 검색·접두사 질의가 키 길이에만 비례하고(O(L)) 해시맵과 달리 "접두사로 시작하는 모든 단어"를 바로 구할 수 있다
struct Trie {
    struct Node { std::array<std::unique_ptr<Node>, 26> next; bool end = false; } root;
    void insert(const std::string& w) { Node* n = &root; for (char c : w) { auto& x = n->next[c - 'a']; if (!x) x = std::make_unique<Node>(); n = x.get(); } n->end = true; }
    const Node* find(const std::string& p) const { const Node* n = &root; for (char c : p) { n = n->next[c - 'a'].get(); if (!n) return nullptr; } return n; }
    bool contains(const std::string& w) const { auto n = find(w); return n && n->end; }
    void collect(const Node* n, std::string& cur, std::vector<std::string>& out) const {
        if (n->end) out.push_back(cur);
        for (int i = 0; i < 26; i++) if (n->next[i]) { cur.push_back('a' + i); collect(n->next[i].get(), cur, out); cur.pop_back(); }
    }
    std::vector<std::string> startsWith(const std::string& p) const {          // 자동 완성
        std::vector<std::string> out; auto n = find(p); std::string cur = p;
        if (n) collect(n, cur, out);
        return out;
    }
};

int main() {
    Trie t;
    for (auto w : {"car", "card", "care", "cat", "dog"}) t.insert(w);
    assert(t.contains("car") && !t.contains("ca") && !t.contains("cow"));
    assert((t.startsWith("car") == std::vector<std::string>{"car", "card", "care"}));
    assert(t.startsWith("x").empty());
    std::cout << "Trie autocomplete(car): 3 words" << std::endl;
    return 0;
}
// Time Complexity: 삽입/검색 O(L)
// Space Complexity: O(총 글자 수 · σ)
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
#include <iostream>
#include <algorithm>
#include <numeric>
#include <string>
#include <vector>
#include <cassert>

// 접미사 배열: 모든 접미사를 사전순으로 정렬했을 때 각 접미사의 시작 위치.  이를 이용하면 패턴 검색이 이진 탐색(O(m log n))이 된다
std::vector<int> naiveSuffixArray(const std::string& s) {
    std::vector<int> sa(s.size()); std::iota(sa.begin(), sa.end(), 0);
    std::sort(sa.begin(), sa.end(), [&](int a, int b) { return s.compare(a, std::string::npos, s, b, std::string::npos) < 0; });
    return sa;
}
// 패턴으로 시작하는 접미사들은 SA 에서 연속된 구간을 이룬다
std::vector<int> occurrences(const std::string& s, const std::vector<int>& sa, const std::string& p) {
    auto lo = std::lower_bound(sa.begin(), sa.end(), p, [&](int i, const std::string& x) { return s.compare(i, x.size(), x) < 0; });
    auto hi = std::upper_bound(sa.begin(), sa.end(), p, [&](const std::string& x, int i) { return s.compare(i, x.size(), x) > 0; });
    std::vector<int> r(lo, hi); std::sort(r.begin(), r.end()); return r;
}

int main() {
    std::string s = "banana";
    auto sa = naiveSuffixArray(s);
    assert((sa == std::vector<int>{5, 3, 1, 0, 4, 2}));               // a, ana, anana, banana, na, nana
    assert((occurrences(s, sa, "ana") == std::vector<int>{1, 3}));
    assert((occurrences(s, sa, "na") == std::vector<int>{2, 4}));
    assert(occurrences(s, sa, "x").empty());
    std::cout << "SuffixArray(banana) = 5 3 1 0 4 2" << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n² log n)(순진한 정렬), 검색 O(m log n)
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
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// 다항 롤링 해시(문자열 관점의 요약, 정본은 Hash.md Part 5): H(s[l..r)) = P[r] - P[l]·B^(r-l).
// 접두사 해시 한 번 계산으로 임의 부분 문자열의 해시를 O(1)에 구한다
struct PRH {
    static const uint64_t M = 1000000007ULL, B = 131;
    std::vector<uint64_t> p, pw;
    explicit PRH(const std::string& s) : p(s.size() + 1, 0), pw(s.size() + 1, 1) {
        for (size_t i = 0; i < s.size(); i++) { p[i + 1] = (p[i] * B + (unsigned char)s[i]) % M; pw[i + 1] = pw[i] * B % M; }
    }
    uint64_t get(size_t l, size_t r) const { return (p[r] + M - p[l] * pw[r - l] % M) % M; }
};

int main() {
    PRH h("abcabcabc");
    assert(h.get(0, 3) == h.get(3, 6) && h.get(3, 6) == h.get(6, 9));      // 세 개의 "abc"
    assert(h.get(0, 3) != h.get(1, 4));
    std::cout << "PolynomialRollingHash verified." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(n), 질의 O(1)
// Space Complexity: O(n)
```
## RabinFingerprint()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <cassert>

// 라빈 지문(문자열 관점의 요약, 정본은 Hash.md Part 5): 길이 w 윈도우를 한 글자씩 밀며 지문을 O(1)에 갱신한다.
// 여기서는 소수 모듈러 버전: f' = (f - old·B^(w-1))·B + new  (mod M)
int main() {
    const uint64_t B = 256, M = 1000000007ULL;
    std::string s = "rolling hash fingerprints";
    const size_t w = 6;
    uint64_t pw = 1; for (size_t i = 1; i < w; i++) pw = pw * B % M;
    auto direct = [&](size_t pos) { uint64_t f = 0; for (size_t i = 0; i < w; i++) f = (f * B + (unsigned char)s[pos + i]) % M; return f; };
    uint64_t f = direct(0);
    for (size_t i = 0; i + w < s.size(); i++) {
        f = ((f + M - (unsigned char)s[i] * pw % M) * B + (unsigned char)s[i + w]) % M;
        assert(f == direct(i + 1));                                           // 밀어서 구한 값 == 처음부터 구한 값
    }
    std::cout << "RabinFingerprint sliding window verified." << std::endl;
    return 0;
}
// Time Complexity: 슬라이드 1회 O(1)
// Space Complexity: O(1)
```
## SubstringHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <set>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// 부분 문자열 해시: 모듈러가 둘인 이중 해시로 충돌 확률을 ~10^-18 수준으로 낮추면, 두 부분 문자열이 같은지를 O(1)에 판정할 수 있다
struct DoubleHash {
    static const uint64_t M1 = 1000000007ULL, M2 = 998244353ULL, B1 = 131, B2 = 137;
    std::vector<uint64_t> p1, p2, w1, w2;
    explicit DoubleHash(const std::string& s) : p1(s.size() + 1), p2(s.size() + 1), w1(s.size() + 1, 1), w2(s.size() + 1, 1) {
        for (size_t i = 0; i < s.size(); i++) {
            p1[i + 1] = (p1[i] * B1 + (unsigned char)s[i]) % M1; w1[i + 1] = w1[i] * B1 % M1;
            p2[i + 1] = (p2[i] * B2 + (unsigned char)s[i]) % M2; w2[i + 1] = w2[i] * B2 % M2;
        }
    }
    std::pair<uint64_t, uint64_t> get(size_t l, size_t r) const {
        return {(p1[r] + M1 - p1[l] * w1[r - l] % M1) % M1, (p2[r] + M2 - p2[l] * w2[r - l] % M2) % M2};
    }
};

int main() {
    std::string s = "abababcabababc";
    DoubleHash h(s);
    assert(h.get(0, 7) == h.get(7, 14));                    // "abababc" == "abababc"
    assert(h.get(0, 6) != h.get(1, 7));
    // 응용: 길이 L 인 서로 다른 부분 문자열의 개수를 해시 집합으로 센다
    auto countDistinct = [&](size_t L) { std::set<std::pair<uint64_t, uint64_t>> st; for (size_t i = 0; i + L <= s.size(); i++) st.insert(h.get(i, i + L)); return st.size(); };
    for (size_t L = 1; L <= 8; L++) {
        std::set<std::string> brute; for (size_t i = 0; i + L <= s.size(); i++) brute.insert(s.substr(i, L));
        assert(countDistinct(L) == brute.size());
    }
    std::cout << "SubstringHash distinct substrings of length 3: " << countDistinct(3) << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(n), 비교 O(1)
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
#include <iostream>
#include <algorithm>
#include <numeric>
#include <string>
#include <vector>
#include <cassert>

// MTF: 알파벳을 리스트로 두고, 글자를 만나면 "현재 위치(인덱스)"를 출력한 뒤 맨 앞으로 옮긴다.
// 같은 글자가 가까이 모여 있으면 0, 1 같은 작은 수가 많아져 이후 엔트로피 부호화(허프먼 등)가 잘 된다. BWT 뒤에 쓰는 이유
std::vector<int> mtfEncode(const std::string& s) {
    std::string alpha(256, 0); std::iota(alpha.begin(), alpha.end(), 0);
    std::vector<int> out;
    for (unsigned char c : s) {
        int i = alpha.find((char)c);
        out.push_back(i);
        alpha.erase(i, 1); alpha.insert(alpha.begin(), (char)c);
    }
    return out;
}
std::string mtfDecode(const std::vector<int>& codes) {
    std::string alpha(256, 0); std::iota(alpha.begin(), alpha.end(), 0);
    std::string out;
    for (int i : codes) { char c = alpha[i]; out += c; alpha.erase(i, 1); alpha.insert(alpha.begin(), c); }
    return out;
}

int main() {
    auto e = mtfEncode("bananaaa");
    assert(mtfDecode(e) == "bananaaa");
    assert(e.back() == 0 && e[e.size() - 2] == 0);                // 반복되는 마지막 a 는 0 으로 바뀐다
    std::string clustered = "aaaabbbbccccdddd";
    auto c = mtfEncode(clustered);
    int zeros = std::count(c.begin(), c.end(), 0);
    assert(zeros >= 12);                                          // 16글자 중 12개 이상이 0
    std::cout << "MTF zeros in clustered text: " << zeros << "/16" << std::endl;
    return 0;
}
// Time Complexity: O(n·σ)
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
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <cassert>

// 레벤슈타인 거리: 삽입·삭제·치환 각 1로 한 문자열을 다른 문자열로 바꾸는 최소 횟수.  dp[i][j] = a[0..i) -> b[0..j)
// 표를 거슬러 올라가면 실제 편집 연산열도 얻는다
int levenshtein(const std::string& a, const std::string& b, std::string* script = nullptr) {
    size_t n = a.size(), m = b.size();
    std::vector<std::vector<int>> d(n + 1, std::vector<int>(m + 1));
    for (size_t i = 0; i <= n; i++) d[i][0] = i;
    for (size_t j = 0; j <= m; j++) d[0][j] = j;
    for (size_t i = 1; i <= n; i++)
        for (size_t j = 1; j <= m; j++)
            d[i][j] = std::min({d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] != b[j-1])});
    if (script) {
        script->clear(); size_t i = n, j = m;
        while (i > 0 || j > 0) {
            if (i && j && d[i][j] == d[i-1][j-1] + (a[i-1] != b[j-1])) { *script += (a[i-1] == b[j-1]) ? 'M' : 'S'; i--; j--; }
            else if (i && d[i][j] == d[i-1][j] + 1) { *script += 'D'; i--; }
            else { *script += 'I'; j--; }
        }
        std::reverse(script->begin(), script->end());
    }
    return d[n][m];
}

int main() {
    std::string ops;
    assert(levenshtein("kitten", "sitting", &ops) == 3);
    assert(std::count(ops.begin(), ops.end(), 'M') == 4);          // k→s 치환, e→i 치환, g 삽입; 나머지 4글자는 일치
    assert(levenshtein("", "abc") == 3 && levenshtein("abc", "") == 3 && levenshtein("same", "same") == 0);
    assert(levenshtein("flaw", "lawn") == 2);
    std::cout << "Levenshtein(kitten, sitting) = 3, script = " << ops << std::endl;
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(n·m)  (거리만 필요하면 O(min(n, m)))
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
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <cassert>

// 최장 공통 부분 문자열(연속) DP: dp[i][j] = a[i-1] == b[j-1] 이면 dp[i-1][j-1] + 1, 아니면 0.  최댓값이 답. 행 두 개만 쓰면 O(min) 공간
std::string lcsubstringDP(const std::string& a, const std::string& b) {
    std::vector<int> prev(b.size() + 1, 0), cur(b.size() + 1, 0);
    int best = 0, end = 0;
    for (size_t i = 1; i <= a.size(); i++) {
        for (size_t j = 1; j <= b.size(); j++) {
            cur[j] = (a[i-1] == b[j-1]) ? prev[j-1] + 1 : 0;
            if (cur[j] > best) { best = cur[j]; end = i; }
        }
        std::swap(prev, cur);
    }
    return a.substr(end - best, best);
}

int main() {
    assert(lcsubstringDP("abcdxyz", "xyzabcd") == "abcd");
    assert(lcsubstringDP("OldSite:GeeksforGeeks.org", "NewSite:GeeksQuiz.com") == "Site:Geeks");
    assert(lcsubstringDP("abc", "xyz").empty());
    std::cout << "LongestCommonSubstringDP verified." << std::endl;
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(m)
```
## LongestCommonSubsequence()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <cassert>

// 최장 공통 부분 수열(LCS): 연속이 아니어도 순서만 유지하면 된다. diff, 유전자 정렬의 기초.  dp[i][j] = 접두사 a[0..i), b[0..j) 의 LCS 길이
std::string lcs(const std::string& a, const std::string& b) {
    size_t n = a.size(), m = b.size();
    std::vector<std::vector<int>> d(n + 1, std::vector<int>(m + 1, 0));
    for (size_t i = 1; i <= n; i++)
        for (size_t j = 1; j <= m; j++)
            d[i][j] = a[i-1] == b[j-1] ? d[i-1][j-1] + 1 : std::max(d[i-1][j], d[i][j-1]);
    std::string out;
    for (size_t i = n, j = m; i > 0 && j > 0;) {                    // 역추적
        if (a[i-1] == b[j-1]) { out += a[i-1]; i--; j--; }
        else if (d[i-1][j] >= d[i][j-1]) i--; else j--;
    }
    std::reverse(out.begin(), out.end());
    return out;
}
bool isSubsequence(const std::string& s, const std::string& t) { size_t k = 0; for (char c : t) if (k < s.size() && s[k] == c) k++; return k == s.size(); }

int main() {
    std::string r = lcs("ABCBDAB", "BDCABA");
    assert(r.size() == 4 && isSubsequence(r, "ABCBDAB") && isSubsequence(r, "BDCABA"));
    assert(lcs("AGGTAB", "GXTXAYB") == "GTAB");
    assert(lcs("abc", "xyz").empty());
    std::cout << "LCS(ABCBDAB, BDCABA) length " << r.size() << ": " << r << std::endl;
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(n·m)
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
#include <iostream>
#include <cctype>
#include <string>
#include <vector>
#include <cassert>

// 어휘 분석기(lexer): 문자 스트림을 토큰(숫자, 식별자, 연산자, 괄호)으로 자른다.  컴파일러의 첫 단계이며 정규식(오토마톤)으로 정의된다
enum Type { NUMBER, IDENT, OP, LPAREN, RPAREN, END };
struct Token { Type type; std::string text; };

std::vector<Token> lex(const std::string& s) {
    std::vector<Token> out; size_t i = 0;
    while (i < s.size()) {
        unsigned char c = s[i];
        if (std::isspace(c)) { i++; continue; }
        if (std::isdigit(c) || (c == '.' && i + 1 < s.size() && std::isdigit((unsigned char)s[i + 1]))) {
            size_t j = i; while (j < s.size() && (std::isdigit((unsigned char)s[j]) || s[j] == '.')) j++;
            out.push_back({NUMBER, s.substr(i, j - i)}); i = j;
        } else if (std::isalpha(c) || c == '_') {
            size_t j = i; while (j < s.size() && (std::isalnum((unsigned char)s[j]) || s[j] == '_')) j++;
            out.push_back({IDENT, s.substr(i, j - i)}); i = j;
        } else if (c == '(') { out.push_back({LPAREN, "("}); i++; }
        else if (c == ')') { out.push_back({RPAREN, ")"}); i++; }
        else if (std::string("+-*/=").find(c) != std::string::npos) { out.push_back({OP, std::string(1, c)}); i++; }
        else throw std::runtime_error(std::string("unexpected character: ") + (char)c);
    }
    out.push_back({END, ""});
    return out;
}

int main() {
    auto t = lex("x1 = 3.14 * (y_2 + 2)");
    std::vector<std::string> texts; for (auto& k : t) texts.push_back(k.text);
    assert((texts == std::vector<std::string>{"x1", "=", "3.14", "*", "(", "y_2", "+", "2", ")", ""}));
    assert(t[0].type == IDENT && t[2].type == NUMBER && t[3].type == OP && t[4].type == LPAREN);
    bool threw = false; try { lex("a $ b"); } catch (const std::runtime_error&) { threw = true; }
    assert(threw);
    std::cout << "Lexer produced " << t.size() - 1 << " tokens" << std::endl;
    return 0;
}
// Time Complexity: O(n)
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
#include <iostream>
#include <algorithm>
#include <cmath>
#include <map>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// TF-IDF: 문서 안에서 자주 나오고(TF) 전체 문서에서는 드문(IDF) 단어일수록 그 문서를 잘 대표한다.
//   tf-idf(t, d) = tf(t, d) · log(N / df(t))     N = 문서 수, df = 단어를 포함한 문서 수
std::vector<std::string> split(const std::string& s) { std::istringstream in(s); std::vector<std::string> w; std::string x; while (in >> x) w.push_back(x); return w; }

int main() {
    std::vector<std::string> docs = {
        "the cat sat on the mat",
        "the dog sat on the log",
        "cats and dogs are pets",
        "the quick brown fox jumps over the lazy dog dog dog"};
    int N = docs.size();
    std::map<std::string, int> df;
    std::vector<std::map<std::string, int>> tf(N);
    for (int d = 0; d < N; d++) { for (auto& w : split(docs[d])) tf[d][w]++; for (auto& kv : tf[d]) df[kv.first]++; }
    auto score = [&](int d, const std::string& q) {
        double s = 0;
        for (auto& t : split(q)) if (tf[d].count(t)) s += tf[d][t] * std::log(double(N) / df[t]);
        return s;
    };
    std::vector<int> order = {0, 1, 2, 3};
    std::sort(order.begin(), order.end(), [&](int a, int b) { return score(a, "dog") > score(b, "dog"); });
    assert(order[0] == 3);                                              // "dog" 이 세 번 나오는 문서가 1위
    assert(std::log(double(N) / df["the"]) < std::log(double(N) / df["fox"]));   // 흔한 단어 "the" 는 가중치가 낮다
    assert(score(2, "the") == 0 && score(0, "the") > 0 && score(0, "the") < score(0, "cat"));
    std::cout << "TFIDF ranking for 'dog': best doc = " << order[0] << std::endl;
    return 0;
}
// Time Complexity: 색인 O(총 토큰), 점수 계산 O(|q|)
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
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <cassert>

// 니들만-브니쉬: 두 서열의 "전역" 정렬(처음부터 끝까지).  일치 +1, 불일치 -1, 갭 -1 점수로 점수 합이 최대인 정렬을 DP 로 구한다.
// 편집 거리와 같은 구조에서 최소 대신 최대를 구하는 형태
struct Result { int score; std::string a, b; };
Result needlemanWunsch(const std::string& x, const std::string& y, int match = 1, int mismatch = -1, int gap = -1) {
    size_t n = x.size(), m = y.size();
    std::vector<std::vector<int>> f(n + 1, std::vector<int>(m + 1));
    for (size_t i = 0; i <= n; i++) f[i][0] = i * gap;
    for (size_t j = 0; j <= m; j++) f[0][j] = j * gap;
    for (size_t i = 1; i <= n; i++) for (size_t j = 1; j <= m; j++)
        f[i][j] = std::max({f[i-1][j-1] + (x[i-1] == y[j-1] ? match : mismatch), f[i-1][j] + gap, f[i][j-1] + gap});
    std::string a, b; size_t i = n, j = m;
    while (i > 0 || j > 0) {
        if (i && j && f[i][j] == f[i-1][j-1] + (x[i-1] == y[j-1] ? match : mismatch)) { a += x[--i]; b += y[--j]; }
        else if (i && f[i][j] == f[i-1][j] + gap) { a += x[--i]; b += '-'; }
        else { a += '-'; b += y[--j]; }
    }
    std::reverse(a.begin(), a.end()); std::reverse(b.begin(), b.end());
    return {f[n][m], a, b};
}
int rescore(const Result& r, int match = 1, int mismatch = -1, int gap = -1) {
    int s = 0; for (size_t i = 0; i < r.a.size(); i++) s += (r.a[i] == '-' || r.b[i] == '-') ? gap : (r.a[i] == r.b[i] ? match : mismatch); return s;
}

int main() {
    auto r = needlemanWunsch("GCATGCG", "GATTACA");
    assert(r.score == 0);                                              // 위키피디아의 표준 예제
    assert(rescore(r) == r.score);                                     // 정렬 결과를 다시 채점해도 같다
    std::string ra, rb; for (char c : r.a) if (c != '-') ra += c; for (char c : r.b) if (c != '-') rb += c;
    assert(ra == "GCATGCG" && rb == "GATTACA");                        // 갭을 빼면 원래 서열
    assert(needlemanWunsch("ACGT", "ACGT").score == 4);
    std::cout << "NeedlemanWunsch score " << r.score << "\n" << r.a << "\n" << r.b << std::endl;
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(n·m)  (Hirschberg 알고리즘은 O(n+m))
```
## SmithWaterman()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <cassert>

// 스미스-워터먼: 두 서열의 "지역" 정렬 — 가장 비슷한 부분 구간만 찾는다.  전역 정렬과 달리 점수가 0 아래로 내려가면 0 으로 재시작하고,
// 표 전체의 최댓값 칸에서 0 을 만날 때까지 거슬러 올라간다 (유전자 안의 보존된 도메인 찾기, BLAST 의 기반)
struct Result { int score; std::string a, b; };
Result smithWaterman(const std::string& x, const std::string& y, int match = 3, int mismatch = -3, int gap = -2) {
    size_t n = x.size(), m = y.size();
    std::vector<std::vector<int>> h(n + 1, std::vector<int>(m + 1, 0));
    int best = 0; size_t bi = 0, bj = 0;
    for (size_t i = 1; i <= n; i++) for (size_t j = 1; j <= m; j++) {
        h[i][j] = std::max({0, h[i-1][j-1] + (x[i-1] == y[j-1] ? match : mismatch), h[i-1][j] + gap, h[i][j-1] + gap});
        if (h[i][j] > best) { best = h[i][j]; bi = i; bj = j; }
    }
    std::string a, b; size_t i = bi, j = bj;
    while (i > 0 && j > 0 && h[i][j] > 0) {
        if (h[i][j] == h[i-1][j-1] + (x[i-1] == y[j-1] ? match : mismatch)) { a += x[--i]; b += y[--j]; }
        else if (h[i][j] == h[i-1][j] + gap) { a += x[--i]; b += '-'; }
        else { a += '-'; b += y[--j]; }
    }
    std::reverse(a.begin(), a.end()); std::reverse(b.begin(), b.end());
    return {best, a, b};
}

int main() {
    auto r = smithWaterman("TGTTACGG", "GGTTGACTA");
    assert(r.score == 13);                                           // 위키피디아의 표준 예제: GTT-AC / GTTGAC
    assert(r.a == "GTT-AC" && r.b == "GTTGAC");
    int s = 0; for (size_t i = 0; i < r.a.size(); i++) s += (r.a[i] == '-' || r.b[i] == '-') ? -2 : (r.a[i] == r.b[i] ? 3 : -3);
    assert(s == r.score);
    assert(smithWaterman("AAAA", "TTTT").score == 0);                // 공통점이 없으면 0
    std::cout << "SmithWaterman score " << r.score << "\n" << r.a << "\n" << r.b << std::endl;
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
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 증명의 핵심(분할상환): 포인터 k(매칭된 길이)는 텍스트 글자 하나당 많아야 1 증가한다 -> 총 증가 ≤ n.
// k 는 0 아래로 내려갈 수 없고 `while` 의 한 반복마다 최소 1 감소하므로 총 감소 ≤ 총 증가 ≤ n.
// 따라서 안쪽 while 의 전체 반복 횟수 ≤ n 이고, 텍스트를 훑는 총 연산은 ≤ 2n 이다 (실패 함수 구성도 같은 논리로 O(m))
int main() {
    std::string p(50, 'a'); p += 'b';                       // 나이브라면 최악인 패턴
    std::vector<int> pi(p.size(), 0);
    for (size_t i = 1, k = 0; i < p.size(); i++) { while (k > 0 && p[i] != p[k]) k = pi[k - 1]; if (p[i] == p[k]) k++; pi[i] = k; }

    for (std::string t : {std::string(100000, 'a'), std::string(50000, 'a') + "b" + std::string(50000, 'a'), std::string("ab").append(50000, 'a')}) {
        long whileSteps = 0, forSteps = 0;
        for (size_t i = 0, k = 0; i < t.size(); i++, forSteps++) {
            while (k > 0 && t[i] != p[k]) { k = pi[k - 1]; whileSteps++; }
            if (t[i] == p[k]) k++;
            if (k == p.size()) k = pi[k - 1];
        }
        assert(whileSteps <= (long)t.size());                // 후퇴 횟수의 총합 ≤ n
        assert(forSteps + whileSteps <= 2 * (long)t.size());
        std::cout << "n=" << t.size() << " forward=" << forSteps << " backtracks=" << whileSteps << std::endl;
    }
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
#include <iostream>
#include <array>
#include <memory>
#include <string>
#include <unordered_set>
#include <vector>
#include <cassert>

// 해시맵은 "정확히 일치" 에는 O(L)로 빠르지만 접두사 질의를 지원하지 못해 모든 키를 훑어야 한다 (O(N·L)).
// 트라이는 접두사까지 O(L)만에 내려가 그 아래 단어만 방문한다 -> 자동 완성, 사전식 순회, 최장 접두사 일치에 유리.
// 대신 노드마다 포인터 배열을 가져 메모리를 더 쓴다
struct Trie {
    struct Node { std::array<std::unique_ptr<Node>, 26> next; bool end = false; } root; long nodes = 1;
    void insert(const std::string& w) { Node* n = &root; for (char c : w) { auto& x = n->next[c - 'a']; if (!x) { x = std::make_unique<Node>(); nodes++; } n = x.get(); } n->end = true; }
    long visitedForPrefix(const std::string& p) const {                  // 접두사 아래를 순회하며 방문한 노드 수
        const Node* n = &root; long visited = 0;
        for (char c : p) { n = n->next[c - 'a'].get(); visited++; if (!n) return visited; }
        std::vector<const Node*> st = {n};
        while (!st.empty()) { const Node* x = st.back(); st.pop_back(); visited++; for (auto& c : x->next) if (c) st.push_back(c.get()); }
        return visited;
    }
};

int main() {
    Trie t; std::unordered_set<std::string> h; std::vector<std::string> words;
    for (int i = 0; i < 20000; i++) { std::string w; int x = i * 7919 + 13; for (int k = 0; k < 6; k++) { w += (char)('a' + x % 26); x /= 26; x += k * 31; } words.push_back(w); }
    for (auto& w : words) { t.insert(w); h.insert(w); }
    // 접두사 "ab" 로 시작하는 단어 모으기: 해시맵은 키 전체를 검사, 트라이는 해당 가지만 방문
    long hashChecked = 0, found = 0; for (auto& w : h) { hashChecked++; if (w.compare(0, 2, "ab") == 0) found++; }
    long trieVisited = t.visitedForPrefix("ab");
    assert(found > 0 && trieVisited < hashChecked / 10);
    // 정확한 일치는 둘 다 한 번의 조회
    assert(h.count(words[123]) == 1);
    std::cout << "prefix query: hash map scanned " << hashChecked << " keys, trie visited " << trieVisited << " nodes (trie has " << t.nodes << " nodes)" << std::endl;
    return 0;
}
// Time Complexity: 트라이 접두사 질의 O(L + 결과 크기), 해시맵 O(N·L)
// Space Complexity: 트라이 O(총 글자 수 · σ), 해시맵 O(총 글자 수)
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
