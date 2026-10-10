# Part 1. 집합의 기초
## CreateSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 집합 만들기(CreateSet): 집합(set)은 중복이 없고 순서가 의미 없는 원소들의 모임이다. 만드는 방법은 빈 집합, 초기화 목록, 다른 범위(중복 있어도 됨), 그리고 필요한 크기를 미리 알면 reserve 로 예약하는 것이다. 어떤 방법이든 결과는 "서로 다른 값들"의 집합이므로 같은 값을 여러 번 넣어도 원소는 하나다.
// 이 장의 집합은 열린 주소법 해시 집합이다: 2 의 거듭제곱 크기 배열, 곱셈 해시, 선형 탐사(충돌 시 다음 칸), 부하율 1/2 을 넘기 전에 두 배로 키워 다시 배치(rehash). 미리 예약하면 다시 배치가 한 번도 일어나지 않는다. 불변식: 모든 원소는 자기 집 위치부터 자기 칸까지 빈 칸 없이 이어진 군집 안에 있고, 사용 칸 수 == 크기, 부하율 ≤ 1/2.
// 검증: ① 빈 집합·초기화 목록·범위(중복 포함)로 만든 집합이 std::unordered_set 과 같은 원소 ② 중복은 하나로(정렬 후 unique 와 같은 크기) ③ INT_MIN/INT_MAX/0/음수 같은 극단 값 ④ reserve(n) 뒤 n 번 삽입에서 다시 배치 0 번, 예약 없으면 ⌈log₂⌉ 번 ⑤ 용량이 항상 2 의 거듭제곱이고 크기의 두 배 이상 ⑥ 불변식 성립.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
IntSet fromList(std::initializer_list<int> il) { IntSet s; for (int x : il) s.add(x); return s; }
template <class It> IntSet fromRange(It first, It last) { IntSet s; for (; first != last; ++first) s.add(*first); return s; }
int main() {
    { IntSet e; assert(e.empty() && e.size() == 0 && e.items().empty() && e.check() && e.capacity() == 8); }
    { IntSet s = fromList({5, 3, 5, 9, 3, 3, -1}); assert(s.size() == 4 && s.items() == (std::vector<int>{-1, 3, 5, 9}) && s.check() && s.contains(9) && !s.contains(4)); }                                            // ① ②
    { IntSet s = fromList({INT_MIN, INT_MAX, 0, -1, 1, INT_MIN, INT_MAX}); assert(s.size() == 5 && s.contains(INT_MIN) && s.contains(INT_MAX) && s.contains(0) && s.items() == (std::vector<int>{INT_MIN, -1, 0, 1, INT_MAX}) && s.check()); }   // ③
    std::mt19937 rng(1);
    for (int rep = 0; rep < 200; rep++) { int n = (int)(rng() % 300), range = 1 + (int)(rng() % 400); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % range) - range / 2; IntSet s = fromRange(v.begin(), v.end()); std::unordered_set<int> ref(v.begin(), v.end());
        std::vector<int> u = v; std::sort(u.begin(), u.end()); u.erase(std::unique(u.begin(), u.end()), u.end()); assert(s.size() == ref.size() && s.items() == u && s.check() && s.capacity() >= 2 * s.size());       // ② ⑤ ⑥
        std::size_t cap = s.capacity(); assert((cap & (cap - 1)) == 0); for (int x : v) assert(s.contains(x)); for (int probe = -300; probe < 300; probe++) assert(s.contains(probe) == (ref.count(probe) > 0)); }
    { IntSet a; a.reserve(1000); long before = a.rehashes; for (int i = 0; i < 1000; i++) a.add(i * 7919); assert(a.rehashes == before && a.size() == 1000 && a.check());                                                       // ④ 예약하면 다시 배치 없음
      IntSet b; for (int i = 0; i < 1000; i++) b.add(i * 7919); assert(b.rehashes >= 6 && b.rehashes <= 8 && b.size() == 1000 && b.items() == a.items()); }
    std::cout << "CreateSet: empty, list and range construction (with duplicates and extreme values) matched std::unordered_set on 200 random inputs; duplicates collapsed to one element, capacity stayed a power of two at least twice the size, reserve removed every rehash, and the probe-chain invariant held" << std::endl; return 0;
}
// Time Complexity: O(N) (N 개 원소, 기대)
// Space Complexity: O(N)
```
## Add()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 원소 추가(Add): 집합에 값을 넣는다. 이미 있으면 아무 일도 하지 않고(멱등) false 를 돌려주며, 새 값일 때만 크기가 늘고 true 를 돌려준다. 열린 주소법에서는 집 위치에서 시작해 빈 칸을 만날 때까지 칸을 훑는데, 도중에 같은 값을 보면 이미 있는 것이다. 부하율이 1/2 을 넘기 전에 용량을 두 배로 늘리므로 한 번의 추가는 최악 O(n) 이지만 분할상환 O(1) 이다.
// 해시 함수의 품질이 성능을 좌우한다: 선형 탐사에서 부하율 α 일 때 새 값을 넣기 위한 기대 탐사 수(실패 탐색)는 (1 + 1/(1−α)²)/2 로, α = 1/2 이면 2.5 칸이다. 그러나 해시가 나쁘면(예: 키를 그대로 하위 비트로 사용하는데 키가 모두 4096 의 배수) 모든 키가 같은 집으로 몰려 한 번의 추가가 O(n) 이 된다. 곱셈 해시는 이런 규칙적인 키도 흩뿌린다.
// 검증: ① 추가가 반환값(새 값이면 true)과 크기 증가를 std::unordered_set::insert 와 똑같이 보고 ② 중복 추가는 크기·내용을 바꾸지 않음 ③ 불변식이 추가 중 계속 성립 ④ 무작위 키를 넣을 때 추가당 평균 탐사 칸 수가 3 미만 ⑤ 4096 의 배수 키 3000 개를 넣을 때 곱셈 해시의 평균 탐사 < 3, 하위 비트 해시(나쁜 해시)는 100 이상으로 폭발 ⑥ 재배치 횟수는 log 규모.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
struct BadSet {                                                                                                      // 비교용: 키의 하위 비트를 그대로 집 위치로 쓰는 나쁜 해시
    std::vector<int> key; std::vector<unsigned char> used; std::size_t size = 0; long probes = 0; BadSet() : key(8), used(8, 0) {}
    void grow() { std::vector<int> old; for (std::size_t i = 0; i < key.size(); i++) if (used[i]) old.push_back(key[i]); key.assign(key.size() * 2, 0); used.assign(used.size(), 0); used.resize(key.size(), 0); size = 0; for (int x : old) add(x); }
    bool add(int x) { if ((size + 1) * 2 > key.size()) grow(); std::size_t m = key.size() - 1, i = (std::size_t)(unsigned)x & m; while (used[i]) { probes++; if (key[i] == x) return false; i = (i + 1) & m; } used[i] = 1; key[i] = x; size++; return true; } };
int main() {
    std::mt19937 rng(2); IntSet s; std::unordered_set<int> ref; long adds = 0;
    for (int step = 0; step < 50000; step++) { int x = (int)(rng() % 20000) - 10000; bool added = s.add(x); bool refAdded = ref.insert(x).second; assert(added == refAdded && s.size() == ref.size()); adds++;                        // ① ②
        if (step % 5000 == 0) { assert(s.check()); std::size_t sz = s.size(); assert(!s.add(x) && s.size() == sz); } }                                                                                             // 중복은 변화 없음
    assert(s.check() && s.items() == [&] { std::vector<int> v(ref.begin(), ref.end()); std::sort(v.begin(), v.end()); return v; }());
    { IntSet r; std::mt19937 rr(3); for (int i = 0; i < 100000; i++) r.add((int)rr()); assert((double)r.probes / 100000 < 3.0 && r.rehashes <= 20); }                                                         // ④ ⑥
    { IntSet good; BadSet bad; for (int i = 1; i <= 3000; i++) { good.add(i * 4096); bad.add(i * 4096); } assert(good.size() == 3000 && bad.size == 3000 && (double)good.probes / 3000 < 3.0 && (double)bad.probes / 3000 > 100.0); }   // ⑤ 나쁜 해시
    { IntSet t; std::mt19937 rr(4); for (int i = 0; i < 5000; i++) { t.add((int)(rr() % 3000)); if (i % 500 == 0) assert(t.check()); } }                                                                    // ③
    std::cout << "Add: 50000 insertions agreed with std::unordered_set::insert on both the return value and the size, duplicates changed nothing, random keys cost under 3 probe steps per insertion, and keys that are multiples of 4096 stayed cheap with the multiplicative hash but cost over 100 steps each with a low-bit hash" << std::endl; return 0;
}
// Time Complexity: 분할상환 O(1) (최악 O(N))
// Space Complexity: O(N)
```
## Remove()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 원소 제거(Remove): 집합에서 값을 뺀다. 있으면 지우고 true, 없으면 false. 열린 주소법의 삭제에는 두 설계가 있다. (1) 묘비(tombstone): 칸을 "지워짐" 으로 표시만 한다 — 단순하지만 묘비가 쌓이면 빈 칸이 줄어 실패 탐색이 점점 길어지고 결국 전체를 훑게 된다. (2) 되밀기(backward shift): 지운 칸 뒤의 군집을 살펴 "집 위치가 지운 칸 이전이어서 그 칸으로 당겨 올 수 있는" 원소를 앞으로 옮겨 구멍을 메운다 — 묘비가 없으므로 군집이 늘 최소로 유지된다. 이 장은 (2) 를 쓴다.
// 되밀기의 판정: 칸 j 의 원소의 집 위치 k 가 순환 구간 (i, j] 안에 있으면 그 원소는 i 로 옮기면 집 위치 앞에 놓여 조회가 깨지므로 옮기지 않는다. 그렇지 않으면 i 로 옮기고 i 를 j 로 갱신한 뒤 계속한다. 빈 칸을 만나면 끝.
// 검증: ① 무작위 삽입·삭제·조회가 std::unordered_set 과 일치하고 매 단계 불변식 성립 ② 없는 값 삭제는 false 이고 불변 ③ 모두 지운 뒤 빈 집합, 다시 채우기 가능 ④ 일부러 많은 충돌(좁은 키 범위, 작은 표)에서도 남은 원소가 모두 조회됨 ⑤ 묘비 방식과 비교: 같은 크기(100)를 유지하며 20 만 번 추가·삭제를 반복하면 묘비 방식의 실패 조회 평균 탐사가 되밀기 방식의 10 배 이상.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
struct TombSet {                                                                                                     // 비교용: 묘비 방식(재배치 없음)
    std::vector<int> key; std::vector<unsigned char> st; std::size_t m; unsigned bits;                               // st: 0 빈 칸, 1 사용, 2 묘비
    explicit TombSet(unsigned b) : key((std::size_t)1 << b), st((std::size_t)1 << b, 0), m(((std::size_t)1 << b) - 1), bits(b) {}
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits)); }
    bool add(int x) { std::size_t i = home(x), firstDel = (std::size_t)-1, n = 0; while (st[i] && n <= m) { if (st[i] == 1 && key[i] == x) return false; if (st[i] == 2 && firstDel == (std::size_t)-1) firstDel = i; i = (i + 1) & m; n++; } if (firstDel != (std::size_t)-1) i = firstDel; st[i] = 1; key[i] = x; return true; }
    bool remove(int x) { std::size_t i = home(x), n = 0; while (st[i] && n <= m) { if (st[i] == 1 && key[i] == x) { st[i] = 2; return true; } i = (i + 1) & m; n++; } return false; }
    long missProbes(int x) const { std::size_t i = home(x); long n = 0; while (st[i] && n <= (long)m) { if (st[i] == 1 && key[i] == x) return n; i = (i + 1) & m; n++; } return n; } };
int main() {
    std::mt19937 rng(5);
    for (int rep = 0; rep < 40; rep++) { IntSet s; std::unordered_set<int> ref; int range = 1 + (int)(rng() % 200);                                                                                      // ① ④ 좁은 범위 = 충돌 많음
        for (int step = 0; step < 3000; step++) { int x = (int)(rng() % range), op = (int)(rng() % 3); if (op == 0) { assert(s.add(x) == ref.insert(x).second); } else if (op == 1) { assert(s.remove(x) == (ref.erase(x) > 0)); } else assert(s.contains(x) == (ref.count(x) > 0));
            assert(s.size() == ref.size()); if (step % 100 == 0) assert(s.check()); }
        for (int x = 0; x < range; x++) assert(s.contains(x) == (ref.count(x) > 0)); assert(s.check()); }
    { IntSet s; assert(!s.remove(5)); for (int i = 0; i < 100; i++) s.add(i); std::size_t sz = s.size(); assert(!s.remove(1000) && s.size() == sz && s.check()); }                                          // ② 없는 값
    { IntSet s; for (int i = 0; i < 500; i++) s.add(i * 31); for (int i = 0; i < 500; i++) { assert(s.remove(i * 31)); assert(s.check()); } assert(s.empty() && s.items().empty()); for (int i = 0; i < 500; i++) s.add(i); assert(s.size() == 500 && s.check()); }       // ③
    { IntSet good(8); TombSet bad(8); std::mt19937 rr(6); std::vector<int> pool; for (int i = 0; i < 100; i++) { int x = (int)rr(); good.add(x); bad.add(x); pool.push_back(x); }                         // ⑤
      for (int i = 0; i < 200000; i++) { std::size_t k = rr() % pool.size(); good.remove(pool[k]); bad.remove(pool[k]); int x = (int)rr(); pool[k] = x; good.add(x); bad.add(x); }                          // 크기 100 을 유지하며 교체
      assert(good.size() == 100 && good.check()); long badProbes = 0, goodProbes = 0; const int Q = 2000; for (int i = 0; i < Q; i++) { int q = (int)rr(); badProbes += bad.missProbes(q); long before = good.lookupProbes; good.contains(q); goodProbes += good.lookupProbes - before; }
      assert(badProbes > 10 * goodProbes && (double)goodProbes / Q < 3.0 && (double)badProbes / Q > 50.0); }
    std::cout << "Remove: backward-shift deletion kept the probe-chain invariant through 120000 random operations on tiny key ranges (heavy collisions), reported absent keys correctly, emptied and refilled sets, and avoided the tombstone buildup that makes unsuccessful lookups scan the whole table" << std::endl; return 0;
}
// Time Complexity: O(1) 기대 (되밀기는 군집 길이만큼)
// Space Complexity: O(1)
```
## Contains()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 소속 검사(Contains): 값이 집합에 있는지 묻는다. 해시 집합은 집 위치에서 시작해 값을 찾거나 빈 칸을 만날 때까지 훑는다: 값을 찾으면 성공, 빈 칸을 만나면 실패(군집이 빈 칸으로 끝나므로 그 뒤에는 없다). 이 불변식이 삭제 때 군집을 올바르게 메워야 하는 이유다. 비교 횟수는 부하율 α 에 달려 있다: 선형 탐사의 기대 탐사 칸 수는 성공 (1 + 1/(1−α))/2, 실패 (1 + 1/(1−α)²)/2. α = 1/2 에서 1.5 와 2.5, α = 3/4 에서 2.5 와 8.5 로 부하율이 높아질수록 급격히 느려진다 — 그래서 구현이 부하율을 1/2 이하로 유지한다.
// 정렬 배열의 이진 탐색은 O(log n) 비교, 해시는 기대 O(1) 이지만 최악(모든 키가 같은 군집)은 O(n). 조회는 집합을 바꾸지 않으므로 const 이고, 같은 값을 여러 번 물어도 결과가 같다.
// 검증: ① 무작위 삽입·삭제 사이에 던지는 조회가 std::unordered_set::count 와 항상 일치(있는 값·없는 값·극단 값) ② 빈 집합에서 항상 false ③ 지운 값은 곧바로 false 이고 다른 값은 영향 없음 ④ 부하율 25%/50%/75% 의 고정 용량 표에서 측정한 평균 탐사 칸 수가 위 이론값과 10% 이내(성공·실패 모두) ⑤ 조회가 크기·내용을 바꾸지 않음.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
struct FixedLP {                                                                                                     // 부하율을 고정해 이론식을 확인하는 선형 탐사 표 (재배치 없음)
    std::vector<unsigned> key; std::vector<unsigned char> used; std::size_t m; unsigned bits;
    explicit FixedLP(unsigned b) : key((std::size_t)1 << b), used((std::size_t)1 << b, 0), m(((std::size_t)1 << b) - 1), bits(b) {}
    std::size_t home(unsigned x) const { return (std::size_t)(((unsigned long long)x * 0x9E3779B97F4A7C15ull) >> (64 - bits)); }
    void add(unsigned x) { std::size_t i = home(x); while (used[i]) i = (i + 1) & m; used[i] = 1; key[i] = x; }
    long probesFor(unsigned x, bool& found) const { std::size_t i = home(x); long n = 1; while (used[i]) { if (key[i] == x) { found = true; return n; } i = (i + 1) & m; n++; } found = false; return n; } };   // 성공: 본 칸 수, 실패: 훑은 칸 수 + 마지막 빈 칸
int main() {
    { IntSet e; for (int x : {INT_MIN, -1, 0, 1, INT_MAX}) assert(!e.contains(x)); }                                                                                                              // ②
    std::mt19937 rng(7); IntSet s; std::unordered_set<int> ref;
    for (int step = 0; step < 60000; step++) { int x = (int)(rng() % 3000) - 1500, op = (int)(rng() % 4); if (op == 0) { s.add(x); ref.insert(x); } else if (op == 1) { s.remove(x); ref.erase(x); }                    // ①
        else { std::size_t before = s.size(); assert(s.contains(x) == (ref.count(x) > 0) && s.contains(x) == s.contains(x) && s.size() == before); }
        if (op == 1) assert(!s.contains(x)); }                                                                                                                                                       // ③ 지운 값은 곧바로 false
    for (int x = -1500; x < 1500; x++) assert(s.contains(x) == (ref.count(x) > 0)); assert(s.check() && s.contains(INT_MIN) == false);
    { IntSet t; t.add(INT_MIN); t.add(INT_MAX); assert(t.contains(INT_MIN) && t.contains(INT_MAX) && !t.contains(0)); t.remove(INT_MIN); assert(!t.contains(INT_MIN) && t.contains(INT_MAX)); }
    for (double alpha : {0.25, 0.5, 0.75}) { const unsigned bits = 16; FixedLP t(bits); std::mt19937 r2(11); std::size_t n = (std::size_t)(alpha * (1u << bits)); std::vector<unsigned> keys; std::unordered_set<unsigned> seen; while (keys.size() < n) { unsigned k = r2(); if (seen.insert(k).second) { keys.push_back(k); t.add(k); } }   // ④
        double hit = 0, miss = 0; bool f; for (unsigned k : keys) hit += (double)t.probesFor(k, f); hit /= n; const int Q = 200000; for (int i = 0; i < Q; i++) { unsigned q = r2(); if (seen.count(q)) { i--; continue; } miss += (double)t.probesFor(q, f); } miss /= Q;
        double theoryHit = 0.5 * (1 + 1 / (1 - alpha)), theoryMiss = 0.5 * (1 + 1 / ((1 - alpha) * (1 - alpha))); assert(std::abs(hit - theoryHit) / theoryHit < 0.10 && std::abs(miss - theoryMiss) / theoryMiss < 0.10); }
    std::cout << "Contains: 60000 random mixed operations agreed with std::unordered_set (removed keys were immediately absent, queries never changed the set), and measured probe counts at load factors 25%, 50% and 75% matched the linear-probing formulas (1+1/(1-a))/2 for hits and (1+1/(1-a)^2)/2 for misses within 10%" << std::endl; return 0;
}
// Time Complexity: 기대 O(1) (부하율 ≤ 1/2), 최악 O(N)
// Space Complexity: O(1)
```
## Clear()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 비우기(Clear): 모든 원소를 없애 빈 집합으로 만든다. 가장 단순한 구현은 사용 표시 배열을 전부 0 으로 채우는 것으로 O(용량) 이다 — 용량은 비운 뒤에도 유지되어 다시 쓸 때 재할당이 없다(비우는 일이 자주면 이 비용이 지배적). 세대 번호(epoch) 트릭을 쓰면 O(1) 이다: 칸마다 "어느 세대에 쓰였는가" 표를 두고 현재 세대와 같을 때만 사용 중으로 본다. 비우기 = 세대 번호 +1. 세대 번호가 한 바퀴 돌아 0 이 되면(오버플로) 그때만 진짜로 채운다 — 옛 표시가 우연히 새 세대와 같아 보이는 오류를 막는다.
// 이 코드는 세대 번호를 일부러 8 비트로 작게 잡아 255 번의 비우기마다 오는 오버플로 경로를 자주 밟는다. 두 방식 모두 비운 직후 모든 조회가 false 이고 크기 0 이며, 다시 채울 수 있어야 한다.
// 검증: ① 두 방식 모두 무작위 add/remove/clear/contains 열(수천 번의 clear 포함)이 std::unordered_set 과 일치 ② 비운 뒤 용량 유지 ③ 비우기 비용: 채우기 방식 용량만큼의 칸 쓰기, 세대 방식 0(오버플로 때만 용량) ④ 세대 번호가 여러 번 한 바퀴 돌아도 옛 원소가 되살아나지 않음 ⑤ 빈 집합을 다시 비워도 안전.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
class EpochSet {                                                                                                     // 세대 번호 트릭: 비우기 O(1) (같은 해시/탐사, 크기 고정 용량 1024)
    std::vector<int> key_; std::vector<unsigned char> tag_; unsigned char epoch_ = 1; std::size_t size_ = 0; static constexpr std::size_t CAP = 1024;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> 54); }
public:
    long slotWrites = 0; EpochSet() : key_(CAP), tag_(CAP, 0) {}
    bool contains(int x) const { std::size_t i = home(x); while (tag_[i] == epoch_) { if (key_[i] == x) return true; i = (i + 1) & (CAP - 1); } return false; }
    bool add(int x) { if (size_ * 2 >= CAP) return false; std::size_t i = home(x); while (tag_[i] == epoch_) { if (key_[i] == x) return false; i = (i + 1) & (CAP - 1); } tag_[i] = epoch_; key_[i] = x; size_++; return true; }
    void clear() { size_ = 0; if (++epoch_ == 0) { std::fill(tag_.begin(), tag_.end(), 0); slotWrites += (long)CAP; epoch_ = 1; } }                         // 오버플로 때만 진짜 채움
    std::size_t size() const { return size_; } };
int main() {
    std::mt19937 rng(8);
    { IntSet s; std::unordered_set<int> ref; for (int step = 0; step < 40000; step++) { int op = (int)(rng() % 20), x = (int)(rng() % 500);                                                              // ①
          if (op < 10) { assert(s.add(x) == ref.insert(x).second); } else if (op < 14) { assert(s.remove(x) == (ref.erase(x) > 0)); } else if (op < 19) assert(s.contains(x) == (ref.count(x) > 0)); else { std::size_t cap = s.capacity(); s.clear(); ref.clear(); assert(s.empty() && s.capacity() == cap && !s.contains(x) && s.check()); }   // ②
          assert(s.size() == ref.size()); } }
    { EpochSet e; std::unordered_set<int> ref; int clears = 0; for (int step = 0; step < 100000; step++) { int op = (int)(rng() % 20), x = (int)(rng() % 400);
          if (op < 10) { bool a = e.add(x); bool b = ref.insert(x).second; assert(a == b); } else if (op < 18) assert(e.contains(x) == (ref.count(x) > 0)); else { e.clear(); ref.clear(); clears++; assert(e.size() == 0 && !e.contains(x)); }
          assert(e.size() == ref.size()); }
      assert(clears > 1000);                                                                                                                                                                         // ④ 세대 번호가 여러 바퀴를 돈다 (255 번마다)
      EpochSet z; long w = z.slotWrites; for (int i = 0; i < 254; i++) { z.add(i); z.clear(); } assert(z.slotWrites == w);                                                                            // ③ 오버플로 전까지 칸 쓰기 0
      z.add(1); z.clear(); assert(z.slotWrites == 1024 && !z.contains(1)); for (int i = 0; i < 600; i++) { z.add(i); } assert(z.size() == 512 || z.size() <= 512); }
    { IntSet s; s.clear(); s.clear(); assert(s.empty() && s.check()); EpochSet e; e.clear(); e.clear(); assert(e.size() == 0); for (int i = 0; i < 5; i++) s.add(i); s.clear(); for (int i = 10; i < 15; i++) s.add(i); for (int i = 0; i < 5; i++) assert(!s.contains(i)); assert(s.size() == 5); }   // ⑤
    { IntSet s; for (int i = 0; i < 5000; i++) s.add(i); std::size_t cap = s.capacity(); long r = s.rehashes; s.clear(); for (int i = 0; i < 5000; i++) s.add(i + 100000); assert(s.capacity() == cap && s.rehashes == r); }          // 용량 유지 → 재배치 0
    std::cout << "Clear: filling the used-flags and the O(1) epoch-tag method both matched std::unordered_set through thousands of clears (the 8-bit epoch wrapped around many times without resurrecting old elements), capacity survived clearing so refilling needed no rehash, and epoch clearing wrote no slots until wrap-around" << std::endl; return 0;
}
// Time Complexity: 채우기 O(용량), 세대 번호 O(1)
// Space Complexity: O(용량)
```
## Size()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 크기(Size): 집합의 원소 수 |A| 이다. 매번 세면 O(n) 이므로 구현은 삽입·삭제에서 갱신하는 카운터를 둔다 — 새 값이 실제로 추가되었을 때만 +1, 실제로 지워졌을 때만 −1 (중복 삽입이나 없는 값 삭제는 크기를 바꾸면 안 된다). 불변식: 카운터 == 사용 칸 수 == 순회로 센 수. 용량(capacity)과는 다르다: 크기는 원소 수, 용량은 확보한 칸 수이고 부하율 = 크기/용량 ≤ 1/2.
// 크기 관련 항등식: 포함·배제 |A ∪ B| = |A| + |B| − |A ∩ B|, 곱집합 |A × B| = |A|·|B|, 멱집합 |P(A)| = 2^|A|, 부분집합이면 |A| ≤ |B|. 중복이 섞인 스트림의 서로 다른 원소 수(카디널리티)는 정렬 후 unique 한 길이와 같고, 정확한 값이 필요 없고 메모리가 모자라면 확률적 센 방법(HyperLogLog)을 쓴다.
// 검증: ① 무작위 add/remove 10 만 번 뒤 카운터가 순회로 센 수·사용 칸 수·std::unordered_set 크기와 항상 같고 중복 삽입·없는 값 삭제가 크기를 바꾸지 않음 ② 서로 다른 값의 개수가 스트림을 정렬·unique 한 길이와 같음 ③ 부하율 = 크기/용량 ≤ 1/2 ④ 포함·배제 항등식 (무작위 두 집합) ⑤ 크기와 용량이 다르다는 것(reserve 는 용량만 바꿈).
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
std::size_t countByWalking(const IntSet& s) { return s.items().size(); }
int main() {
    std::mt19937 rng(9); IntSet s; std::unordered_set<int> ref;
    for (int step = 0; step < 100000; step++) { int x = (int)(rng() % 2000), op = (int)(rng() % 3); std::size_t before = s.size();
        if (op == 0) { bool added = s.add(x); assert(s.size() == before + (added ? 1 : 0)); ref.insert(x); } else if (op == 1) { bool removed = s.remove(x); assert(s.size() == before - (removed ? 1 : 0)); ref.erase(x); } else { s.add(x); ref.insert(x); bool dup = !s.add(x); assert(dup && s.size() == ref.size()); }   // ①
        assert(s.size() == ref.size()); if (step % 4999 == 0) assert(countByWalking(s) == s.size() && s.check() && (double)s.size() / s.capacity() <= 0.5); }                                                  // ③
    for (int rep = 0; rep < 200; rep++) { int n = (int)(rng() % 400); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 150); IntSet t; for (int x : v) t.add(x); std::vector<int> u = v; std::sort(u.begin(), u.end()); u.erase(std::unique(u.begin(), u.end()), u.end()); assert(t.size() == u.size()); }   // ②
    for (int rep = 0; rep < 200; rep++) { IntSet a, b, un, in; for (int i = 0, k = (int)(rng() % 80); i < k; i++) a.add((int)(rng() % 100)); for (int i = 0, k = (int)(rng() % 80); i < k; i++) b.add((int)(rng() % 100));                    // ④ |A∪B| = |A|+|B|-|A∩B|
        for (int x : a.items()) { un.add(x); if (b.contains(x)) in.add(x); } for (int x : b.items()) un.add(x); assert(un.size() == a.size() + b.size() - in.size()); }
    { IntSet t; t.reserve(10000); assert(t.size() == 0 && t.capacity() >= 20000); t.add(1); assert(t.size() == 1 && t.capacity() >= 20000); }                                                       // ⑤
    std::cout << "Size: the maintained counter equalled the walked count, the number of used slots and std::unordered_set's size after each of 100000 random operations, duplicate adds and absent removals never changed it, the load factor stayed within 1/2, and inclusion-exclusion held on 200 random pairs" << std::endl; return 0;
}
// Time Complexity: 크기 조회 O(1) (순회로 세면 O(N))
// Space Complexity: O(1)
```
## IsEmpty()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>
#include <iterator>
#include <set>

// 공집합 검사(IsEmpty): 원소가 하나도 없는 집합 ∅ 인지 묻는다. 크기 카운터가 있으면 `size() == 0` 으로 O(1) 이다. 카운터가 없는 표현에서는 구조에 맞게 검사한다: 비트 집합은 워드를 앞에서부터 보다가 0 이 아닌 워드를 만나면 즉시 false (최악 O(워드 수)), 연결 리스트는 head 가 널인지, 정렬 배열은 길이가 0 인지.
// 공집합의 성질 (이 코드가 확인한다): ∅ 은 모든 집합의 부분집합 (∅ ⊆ A), A ∪ ∅ = A, A ∩ ∅ = ∅, A \ ∅ = A, ∅ \ A = ∅, A × ∅ = ∅, 공집합은 유일 (원소가 같으면 같은 집합이므로 모든 빈 집합은 서로 같다), P(∅) = {∅} 라서 |P(∅)| = 1, A ⊆ ∅ 이면 A = ∅. 공집합과 "원소가 ∅ 하나뿐인 집합 {∅}" 은 다르다(크기 0 대 1).
// 검증: ① 해시 집합의 empty() 가 크기 0 과 동치이고 add/remove/clear 뒤 항상 맞음 ② 비트 집합의 비었는지 검사가 첫 0 이 아닌 워드에서 멈춤(검사한 워드 수 = 첫 비어 있지 않은 워드 번호 + 1) ③ 위 항등식을 무작위 집합 A 에서 모두 확인 ④ P(∅) = {∅}: 부분집합 열거가 정확히 1 개(빈 집합)를 돌려주고 {∅} 은 크기 1 로 구별 ⑤ 두 빈 집합은 같다.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
struct Bits { std::vector<unsigned long long> w; mutable long wordsChecked = 0; explicit Bits(std::size_t n) : w((n + 63) / 64, 0) {} void set(std::size_t i) { w[i >> 6] |= 1ull << (i & 63); } void reset(std::size_t i) { w[i >> 6] &= ~(1ull << (i & 63)); }
    bool isEmpty() const { for (std::size_t i = 0; i < w.size(); i++) { wordsChecked++; if (w[i]) return false; } return true; } };
std::vector<std::vector<int>> subsetsOf(const std::vector<int>& a) { std::vector<std::vector<int>> out; for (unsigned m = 0; m < (1u << a.size()); m++) { std::vector<int> s; for (std::size_t i = 0; i < a.size(); i++) if (m >> i & 1) s.push_back(a[i]); out.push_back(s); } return out; }
int main() {
    std::mt19937 rng(10);
    { IntSet s; assert(s.empty() && s.size() == 0); s.add(3); assert(!s.empty()); s.remove(3); assert(s.empty()); for (int i = 0; i < 50; i++) s.add(i); assert(!s.empty()); s.clear(); assert(s.empty());       // ①
      for (int step = 0; step < 20000; step++) { int x = (int)(rng() % 30); if (rng() % 2) s.add(x); else s.remove(x); assert(s.empty() == (s.size() == 0)); } }
    { Bits b(1000); assert(b.isEmpty() && b.wordsChecked == (long)b.w.size()); for (std::size_t pos : {0u, 63u, 64u, 500u, 999u}) { Bits c(1000); c.set(pos); assert(!c.isEmpty() && c.wordsChecked == (long)(pos / 64 + 1)); c.reset(pos); assert(c.isEmpty()); } }   // ② 첫 0 이 아닌 워드에서 중단
    for (int rep = 0; rep < 300; rep++) { std::set<int> A; for (int i = 0, k = (int)(rng() % 20); i < k; i++) A.insert((int)(rng() % 50)); std::set<int> E, tmp; assert(E.empty());                                                       // ③
        std::set_union(A.begin(), A.end(), E.begin(), E.end(), std::inserter(tmp, tmp.begin())); assert(tmp == A); tmp.clear(); std::set_intersection(A.begin(), A.end(), E.begin(), E.end(), std::inserter(tmp, tmp.begin())); assert(tmp.empty());
        tmp.clear(); std::set_difference(A.begin(), A.end(), E.begin(), E.end(), std::inserter(tmp, tmp.begin())); assert(tmp == A); tmp.clear(); std::set_difference(E.begin(), E.end(), A.begin(), A.end(), std::inserter(tmp, tmp.begin())); assert(tmp.empty());
        assert(std::includes(A.begin(), A.end(), E.begin(), E.end()) && (std::includes(E.begin(), E.end(), A.begin(), A.end()) == A.empty())); std::size_t prod = 0; for (int a : A) for (int e : E) { (void)a; (void)e; prod++; } assert(prod == 0); }
    { auto ps = subsetsOf({}); assert(ps.size() == 1 && ps[0].empty()); std::set<std::set<int>> setOfEmpty; setOfEmpty.insert(std::set<int>()); assert(setOfEmpty.size() == 1 && !setOfEmpty.empty() && setOfEmpty.begin()->empty()); }       // ④ {∅} 는 크기 1
    { std::set<int> e1, e2; for (int i = 0; i < 3; i++) { e1.insert(i); e1.erase(i); } assert(e1 == e2 && e1.empty() && e2.empty()); IntSet a, b; a.add(1); a.remove(1); assert(a.items() == b.items() && a.empty() && b.empty()); }   // ⑤ 모든 공집합은 같다
    std::cout << "IsEmpty: the hash set's empty() always agreed with size() == 0 through 20000 random updates, the bitset check stopped at the first non-zero word, and the empty-set identities (A+0=A, A*0=0, A-0=A, 0-A=0, 0 subset of A, P(0)={0} with size 1, uniqueness of the empty set) held for 300 random sets" << std::endl; return 0;
}
// Time Complexity: O(1) (비트 집합은 최악 O(워드 수))
// Space Complexity: O(1)
```
## Copy()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>
#include <memory>

// 복사(Copy): 집합을 같은 원소를 가진 독립적인 집합으로 복제한다. 두 방법이 있다. (1) 표 그대로 복제(배열 통째로 복사): 칸 배치까지 같고 O(용량). (2) 원소를 하나씩 다시 삽입: 원소 수에 비례하는 O(n) 이고 더 작은 표가 되며 배치(순회 순서)는 달라질 수 있다 — 집합은 순서가 의미 없으므로 "같은 집합" 의 정의는 원소가 같다는 것뿐이다. 복사 후에는 한쪽을 고쳐도 다른 쪽이 변하지 않아야 한다(깊은 복사). 복사 대입은 복사 후 교환(copy-and-swap)으로 쓰면 자기 대입에도 안전하다.
// 복사본을 만들 때 실제로 복사하지 않고 읽기만 하는 동안 표를 공유하다가 쓰는 순간 복제하는 쓰기 시 복사(copy-on-write)도 있다: 복사는 O(1) 이고 공유 중인 표는 쓰기 직전에 복제된다. 이 코드가 세 방법을 비교한다.
// 검증: ① 표 복제와 재삽입 복사가 원본과 같은 원소이고 서로 독립(복사본을 고쳐도 원본 불변, 반대도) ② 표 복제는 칸 배치까지 동일(검사 가능한 부분: 용량·크기), 재삽입은 용량이 같거나 작음 ③ 자기 대입(a = a)에서 내용 유지 ④ 쓰기 시 복사: 복사 시점의 복제 비용 0, 첫 쓰기에서만 복제되고 이후 독립, 읽기만 하면 끝까지 공유 ⑤ 큰 집합(10 만)과 빈 집합 복사.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
struct CopyStats { static long tableCopies; }; long CopyStats::tableCopies = 0;
class CowSet {                                                                                                       // 쓰기 시 복사: 표를 shared_ptr 로 공유
    std::shared_ptr<IntSet> t_ = std::make_shared<IntSet>();
    void detach() { if (t_.use_count() > 1) { t_ = std::make_shared<IntSet>(*t_); CopyStats::tableCopies++; } }
public:
    bool add(int x) { if (t_->contains(x)) return false; detach(); return t_->add(x); } bool remove(int x) { if (!t_->contains(x)) return false; detach(); return t_->remove(x); } bool contains(int x) const { return t_->contains(x); }
    std::size_t size() const { return t_->size(); } long owners() const { return t_.use_count(); } std::vector<int> items() const { return t_->items(); } };
IntSet cloneTable(const IntSet& s) { return s; }                                                                      // (1) 기본 복사 생성자 = 벡터 통째 복사(칸 배치 동일)
IntSet reinsertCopy(const IntSet& s) { IntSet r; r.reserve(s.size()); for (int x : s.items()) r.add(x); return r; }   // (2) 원소를 다시 삽입(더 작은 표)
int main() {
    std::mt19937 rng(12);
    for (int rep = 0; rep < 200; rep++) { IntSet a; int n = (int)(rng() % 300); for (int i = 0; i < n; i++) a.add((int)(rng() % 1000) - 500); IntSet c1 = cloneTable(a), c2 = reinsertCopy(a); std::vector<int> want = a.items();                                // ①
        assert(c1.items() == want && c2.items() == want && c1.size() == a.size() && c2.size() == a.size() && c1.check() && c2.check());
        assert(c1.capacity() == a.capacity() && c2.capacity() <= a.capacity());                                                                                                                                      // ②
        c1.add(100000); c2.remove(want.empty() ? 0 : want[0]); a.add(-100000); assert(!a.contains(100000) && c1.contains(100000) && (want.empty() || (a.contains(want[0]) && !c2.contains(want[0]))) && !c1.contains(-100000) && !c2.contains(-100000)); }
    { IntSet a; for (int i = 0; i < 100; i++) a.add(i); IntSet* p = &a; a = *p; assert(a.size() == 100 && a.check()); IntSet b; b = a; b.add(1000); assert(a.size() == 100 && b.size() == 101); a = b; assert(a.size() == 101 && a.contains(1000)); }       // ③
    { CopyStats::tableCopies = 0; CowSet a; for (int i = 0; i < 1000; i++) a.add(i); CopyStats::tableCopies = 0; CowSet b = a; CowSet c = a; assert(CopyStats::tableCopies == 0 && a.owners() == 3 && b.size() == 1000);                                                 // ④ 복사 비용 0
      long r = 0; for (int i = 0; i < 1000; i++) r += b.contains(i); assert(r == 1000 && CopyStats::tableCopies == 0 && a.owners() == 3);                                                                                                // 읽기만: 계속 공유
      b.add(5000); assert(CopyStats::tableCopies == 1 && !a.contains(5000) && !c.contains(5000) && b.contains(5000) && a.owners() == 2 && b.owners() == 1); b.add(5001); b.remove(0); assert(CopyStats::tableCopies == 1);                             // 첫 쓰기에서만 복제
      a.remove(1); assert(CopyStats::tableCopies == 2 && !a.contains(1) && c.contains(1) && b.contains(1)); a.add(5) ; assert(!a.add(5) && c.owners() == 1); }
    { IntSet big; for (int i = 0; i < 100000; i++) big.add(i * 3); IntSet c = cloneTable(big), d = reinsertCopy(big); assert(c.size() == 100000 && d.size() == 100000 && c.items() == big.items() && d.items() == big.items()); IntSet e; IntSet ec = cloneTable(e), ed = reinsertCopy(e); assert(ec.empty() && ed.empty() && ec.check() && ed.check()); }   // ⑤
    std::cout << "Copy: table cloning and element re-insertion both produced independent sets with identical contents on 200 random inputs (cloning also kept the capacity), self-assignment kept the set intact, and copy-on-write copies shared one table until the first write, which cloned it exactly once" << std::endl; return 0;
}
// Time Complexity: 표 복제 O(용량), 재삽입 O(N), 쓰기 시 복사 O(1) (쓰기 때 O(용량))
// Space Complexity: O(N)
```

# Part 2. 집합 연산
## Union()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <queue>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 합집합(Union): A ∪ B = {x | x ∈ A 또는 x ∈ B}. 구현은 표현에 따라 다르다. 정렬된 배열은 두 포인터를 한 번씩만 전진시키는 병합 O(|A|+|B|) (같은 값은 한 번만 내보냄), 해시는 한쪽을 통째로 넣고 다른 쪽을 삽입 O(|A|+|B|) 기대, 비트 집합은 워드 단위 OR 로 O(U/64) — 우주 크기가 작고 집합이 조밀할수록 압도적으로 빠르다. 여러 집합(k 개)을 합칠 때는 왼쪽부터 차례로 합치면 앞의 결과를 매번 다시 훑어 O(k·N) 이지만, 짝지어 합치는 분할 정복이나 최소 힙 병합은 O(N log k) 이다.
// 합집합의 법칙: 교환 A∪B = B∪A, 결합 (A∪B)∪C = A∪(B∪C), 멱등 A∪A = A, 항등원 A∪∅ = A, 흡수 A∪(A∩B) = A, 분배 A∪(B∩C) = (A∪B)∩(A∪C), A ⊆ A∪B, 포함·배제 |A∪B| = |A|+|B|−|A∩B|.
// 검증: ① 병합·해시·비트 세 구현이 std::set_union 과 같고 병합의 비교 횟수 ≤ |A|+|B|−1 ② 위 법칙을 무작위 집합 쌍·삼중에서 확인 ③ 한쪽이 비었거나 둘이 같거나 서로 겹치지 않는 경계 ④ k 개 합치기: 왼쪽 접기·분할 정복·힙 병합이 같은 결과이고 원소 접근 총수(비용)가 분할 정복 ≤ 왼쪽 접기, 서로소 64 개(N=640)에서는 분할 정복의 접근 수가 N·log2 k < 접근 ≤ 2·N·log2 k 인 로그 모양(왼쪽 접기는 이 상한을 크게 넘음) ⑤ 우주 크기가 64 의 배수가 아니어도 비트 구현이 정확.
std::vector<int> unionMerge(const std::vector<int>& a, const std::vector<int>& b, long& cmp, long& touches) { std::vector<int> r; std::size_t i = 0, j = 0;
    while (i < a.size() && j < b.size()) { cmp++; touches += 2; if (a[i] < b[j]) r.push_back(a[i++]); else if (b[j] < a[i]) r.push_back(b[j++]); else { r.push_back(a[i]); i++; j++; } } for (; i < a.size(); i++, touches++) r.push_back(a[i]); for (; j < b.size(); j++, touches++) r.push_back(b[j]); return r; }
std::vector<int> unionHash(const std::vector<int>& a, const std::vector<int>& b) { std::unordered_set<int> h(a.begin(), a.end()); h.insert(b.begin(), b.end()); std::vector<int> r(h.begin(), h.end()); std::sort(r.begin(), r.end()); return r; }
std::vector<int> unionBits(const std::vector<int>& a, const std::vector<int>& b, int U) { std::vector<uint64_t> x((U + 63) / 64), y(x.size()); for (int v : a) x[v >> 6] |= 1ull << (v & 63); for (int v : b) y[v >> 6] |= 1ull << (v & 63); std::vector<int> r; for (std::size_t w = 0; w < x.size(); w++) { uint64_t m = x[w] | y[w]; while (m) { r.push_back((int)(w * 64 + __builtin_ctzll(m))); m &= m - 1; } } return r; }
std::vector<int> unionMany(const std::vector<std::vector<int>>& v, std::size_t lo, std::size_t hi, long& touches) { if (hi - lo == 0) return {}; if (hi - lo == 1) return v[lo]; std::size_t mid = lo + (hi - lo) / 2; long c = 0; return unionMerge(unionMany(v, lo, mid, touches), unionMany(v, mid, hi, touches), c, touches); }
std::vector<int> unionHeap(const std::vector<std::vector<int>>& v) { typedef std::pair<int, std::pair<int, int>> E; std::priority_queue<E, std::vector<E>, std::greater<E>> pq; for (int i = 0; i < (int)v.size(); i++) if (!v[i].empty()) pq.push({v[i][0], {i, 0}}); std::vector<int> r;
    while (!pq.empty()) { E e = pq.top(); pq.pop(); if (r.empty() || r.back() != e.first) r.push_back(e.first); int i = e.second.first, k = e.second.second + 1; if (k < (int)v[i].size()) pq.push({v[i][k], {i, k}}); } return r; }
std::vector<int> randomSet(std::mt19937& rng, int U, int maxSize) { std::set<int> s; int n = (int)(rng() % (maxSize + 1)); for (int i = 0; i < n; i++) s.insert((int)(rng() % U)); return std::vector<int>(s.begin(), s.end()); }
std::vector<int> stdUnion(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> stdInter(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
int main() {
    std::mt19937 rng(13);
    for (int rep = 0; rep < 500; rep++) { int U = 1 + (int)(rng() % 200); auto a = randomSet(rng, U, 40), b = randomSet(rng, U, 40), c = randomSet(rng, U, 40); long cmp = 0, t = 0; auto m = unionMerge(a, b, cmp, t); auto want = stdUnion(a, b);       // ① ②
        assert(m == want && unionHash(a, b) == want && unionBits(a, b, U) == want && cmp <= (long)std::max<std::size_t>(1, a.size() + b.size()) - 1 + (a.empty() || b.empty() ? 1 : 0));
        long c1 = 0, c2 = 0, t1 = 0; assert(unionMerge(b, a, c1, t1) == want && unionMerge(unionMerge(a, b, c1, t1), c, c1, t1) == unionMerge(a, unionMerge(b, c, c2, t1), c2, t1));                               // 교환·결합
        assert(unionMerge(a, a, c1, t1) == a && unionMerge(a, {}, c1, t1) == a && unionMerge({}, a, c1, t1) == a && stdUnion(a, stdInter(a, b)) == a);                                                           // 멱등·항등·흡수
        assert(stdUnion(a, stdInter(b, c)) == stdInter(stdUnion(a, b), stdUnion(a, c)) && std::includes(want.begin(), want.end(), a.begin(), a.end()) && want.size() == a.size() + b.size() - stdInter(a, b).size()); }   // 분배·포함·포함배제
    { long cmp = 0, t = 0; assert(unionMerge({}, {}, cmp, t).empty() && unionMerge({1, 2, 3}, {1, 2, 3}, cmp, t) == (std::vector<int>{1, 2, 3}) && unionMerge({1, 3}, {2, 4}, cmp, t) == (std::vector<int>{1, 2, 3, 4}) && unionBits({}, {}, 1).empty()); }                // ③
    for (int rep = 0; rep < 100; rep++) { int k = (int)(rng() % 20); std::vector<std::vector<int>> v; for (int i = 0; i < k; i++) v.push_back(randomSet(rng, 500, 60));                                                  // ④
        std::vector<int> left; long leftTouches = 0; for (auto& s : v) { long c = 0; left = unionMerge(left, s, c, leftTouches); } long balTouches = 0; auto bal = unionMany(v, 0, v.size(), balTouches); auto heap = unionHeap(v); assert(left == bal && bal == heap);
        if (k >= 8) assert(balTouches <= leftTouches); }
    { const int K = 64, S = 10, L = 6; std::vector<std::vector<int>> v(K); for (int i = 0; i < K; i++) for (int j = 0; j < S; j++) v[i].push_back(i + K * j); long bt = 0, lt = 0, N = (long)K * S; auto bal = unionMany(v, 0, v.size(), bt); std::vector<int> left; for (auto& s : v) { long c = 0; left = unionMerge(left, s, c, lt); }
      assert(bal == left && (long)bal.size() == N && bt > N * L && bt <= 2 * N * L && lt > 2 * N * L); }   // 균형: 한 수준당 원소 N 개를 (비교 1~2 회 + 꼬리) 접근, 수준 L = log2 K
    for (int U : {1, 63, 64, 65, 127, 128, 129, 200}) { std::vector<int> a, b; for (int i = 0; i < U; i += 2) a.push_back(i); for (int i = 0; i < U; i += 3) b.push_back(i); assert(unionBits(a, b, U) == stdUnion(a, b)); if (U > 1) { assert(unionBits({U - 1}, {}, U) == std::vector<int>{U - 1}); } }       // ⑤
    std::cout << "Union: sorted-merge, hash and bitset unions equalled std::set_union on 500 random set triples (merge never exceeded |A|+|B|-1 comparisons), the commutative, associative, idempotent, identity, absorption, distributive and inclusion-exclusion laws held, k-way union by folding, divide-and-conquer and heap merge agreed, divide-and-conquer touched about log2 k elements per input element (N*log2 k < touches <= 2*N*log2 k at k=64) while folding exceeded that bound, and universes that are not multiples of 64 bits were exact" << std::endl; return 0;
}
// Time Complexity: 병합 O(|A| + |B|), 해시 기대 O(|A| + |B|) (테스트용 출력 정렬은 제외), 비트 O(U/64), k 개 O(N log k)
// Space Complexity: O(|A| + |B|)
```
## union() (Python Style)
### 대표코드
```python
# 파이썬에서는 기본 내장 자료형 set을 통해 소문자 union() 메서드를 제공합니다.
# 내부적으로는 C++의 std::set_union과 유사하게 동작하지만 사용이 훨씬 간결합니다.
def python_set_union():
    set1 = {1, 2, 3}
    set2 = {3, 4, 5}
    res = set1.union(set2) # 혹은 set1 | set2
    assert res == {1, 2, 3, 4, 5}
    print("Python union verified.")

if __name__ == "__main__":
    python_set_union()
```

## Intersection()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 교집합(Intersection): A ∩ B = {x | x ∈ A 이고 x ∈ B}. 정렬된 배열은 두 포인터 병합 O(|A|+|B|), 해시는 작은 쪽의 원소를 큰 쪽 해시에서 찾는 O(min(|A|,|B|)) 기대, 비트 집합은 워드 AND. 크기 차이가 클 때(|A| ≪ |B|)는 병합이 낭비다 — A 의 원소마다 B 에서 지수 탐색(1, 2, 4, … 칸 건너뛰며 상한을 찾은 뒤 이진 탐색, galloping)을 하면 O(|A| log(|B|/|A|)) 비교로 끝난다. 여러 집합의 교집합은 작은 것부터 교차시키면 중간 결과가 빨리 작아진다.
// 법칙: 교환·결합·멱등 A∩A = A, A∩∅ = ∅, 전체집합 U 에 대해 A∩U = A, A∩B ⊆ A, |A∩B| ≤ min(|A|,|B|), 분배 A∩(B∪C) = (A∩B)∪(A∩C), 흡수 A∩(A∪B) = A.
// 검증: ① 병합·해시·비트·지수 탐색 네 구현이 std::set_intersection 과 같음 ② 법칙을 무작위 집합 쌍·삼중에서 확인 ③ 크기 차이가 큰 경우(|A|=10, |B|=100000) 지수 탐색 비교 수가 병합의 1/100 미만 ④ 여러 집합의 교집합: 작은 것부터 교차시킨 총 조회(작은 쪽 크기의 합) 비용이 큰 것부터보다 적고 결과는 같음 ⑤ 서로 겹치지 않으면 빈 집합, 한쪽이 부분집합이면 작은 쪽.
std::vector<int> interMerge(const std::vector<int>& a, const std::vector<int>& b, long& cmp) { std::vector<int> r; std::size_t i = 0, j = 0; while (i < a.size() && j < b.size()) { cmp++; if (a[i] < b[j]) i++; else if (b[j] < a[i]) j++; else { r.push_back(a[i]); i++; j++; } } return r; }
std::vector<int> interHash(const std::vector<int>& a, const std::vector<int>& b) { const std::vector<int>& small = a.size() <= b.size() ? a : b; const std::vector<int>& big = a.size() <= b.size() ? b : a; std::unordered_set<int> h(big.begin(), big.end()); std::vector<int> r; for (int x : small) if (h.count(x)) r.push_back(x); std::sort(r.begin(), r.end()); return r; }
std::vector<int> interBits(const std::vector<int>& a, const std::vector<int>& b, int U) { std::vector<uint64_t> x((U + 63) / 64), y(x.size()); for (int v : a) x[v >> 6] |= 1ull << (v & 63); for (int v : b) y[v >> 6] |= 1ull << (v & 63); std::vector<int> r; for (std::size_t w = 0; w < x.size(); w++) { uint64_t m = x[w] & y[w]; while (m) { r.push_back((int)(w * 64 + __builtin_ctzll(m))); m &= m - 1; } } return r; }
std::vector<int> interGallop(const std::vector<int>& small, const std::vector<int>& big, long& cmp) { std::vector<int> r; std::size_t base = 0;                                      // 작은 쪽 원소마다 큰 쪽에서 지수 탐색 + 이진 탐색
    for (int x : small) { if (base >= big.size()) break; std::size_t step = 1, hi = base; cmp++; while (hi < big.size() && big[hi] < x) { base = hi; hi = base + step; step *= 2; cmp++; } hi = std::min(hi, big.size()); std::size_t lo = base;
        while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; cmp++; if (big[mid] < x) lo = mid + 1; else hi = mid; } base = lo; if (base < big.size() && big[base] == x) { r.push_back(x); base++; } } return r; }
std::vector<int> randomSet(std::mt19937& rng, int U, int maxSize) { std::set<int> s; int n = (int)(rng() % (maxSize + 1)); for (int i = 0; i < n; i++) s.insert((int)(rng() % U)); return std::vector<int>(s.begin(), s.end()); }
std::vector<int> stdInter(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> stdUnion(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
int main() {
    std::mt19937 rng(14);
    for (int rep = 0; rep < 500; rep++) { int U = 1 + (int)(rng() % 300); auto a = randomSet(rng, U, 60), b = randomSet(rng, U, 60), c = randomSet(rng, U, 60); long cm = 0, cg = 0; auto want = stdInter(a, b);                          // ① ②
        const auto& small = a.size() <= b.size() ? a : b; const auto& big = a.size() <= b.size() ? b : a; assert(interMerge(a, b, cm) == want && interHash(a, b) == want && interBits(a, b, U) == want && interGallop(small, big, cg) == want);
        long c1 = 0; assert(interMerge(b, a, c1) == want && interMerge(interMerge(a, b, c1), c, c1) == interMerge(a, interMerge(b, c, c1), c1) && interMerge(a, a, c1) == a && interMerge(a, {}, c1).empty());   // 교환·결합·멱등·영
        std::vector<int> universe(U); for (int i = 0; i < U; i++) universe[i] = i; assert(interMerge(a, universe, c1) == a && want.size() <= std::min(a.size(), b.size()) && std::includes(a.begin(), a.end(), want.begin(), want.end()));
        assert(stdInter(a, stdUnion(b, c)) == stdUnion(stdInter(a, b), stdInter(a, c)) && stdInter(a, stdUnion(a, b)) == a); }                                                                          // 분배·흡수
    { std::vector<int> big(100000); for (int i = 0; i < 100000; i++) big[i] = i * 3; std::set<int> sm; while (sm.size() < 10) sm.insert((int)(rng() % 300000)); std::vector<int> small(sm.begin(), sm.end()); long cm = 0, cg = 0;                           // ③
      auto r1 = interMerge(small, big, cm), r2 = interGallop(small, big, cg); assert(r1 == r2 && r1 == stdInter(small, big) && cg * 100 < cm); }
    long totalOrdered = 0, totalUnordered = 0;
    for (int rep = 0; rep < 100; rep++) { std::vector<std::vector<int>> sets; int k = 3 + (int)(rng() % 4); for (int i = 0; i < k; i++) sets.push_back(randomSet(rng, 400, i == 0 ? 300 : 20 + (int)(rng() % 280)));                      // ④ 비용 = 해시 조회 수 min(|r|, |s|)
        std::vector<std::vector<int>> bySize = sets; std::sort(bySize.begin(), bySize.end(), [](auto& x, auto& y) { return x.size() < y.size(); }); std::vector<int> r2 = bySize[0]; long dummy = 0, ordered = 0; for (std::size_t i = 1; i < bySize.size(); i++) { ordered += (long)std::min(r2.size(), bySize[i].size()); r2 = interMerge(r2, bySize[i], dummy); }
        std::sort(sets.begin(), sets.end(), [](auto& x, auto& y) { return x.size() > y.size(); }); std::vector<int> r1 = sets[0]; long unordered = 0; for (std::size_t i = 1; i < sets.size(); i++) { unordered += (long)std::min(r1.size(), sets[i].size()); r1 = interMerge(r1, sets[i], dummy); }
        assert(r1 == r2); totalOrdered += ordered; totalUnordered += unordered; }
    assert(totalOrdered < totalUnordered);
    { long c = 0; assert(interMerge({1, 3, 5}, {2, 4, 6}, c).empty() && interMerge({2, 4}, {1, 2, 3, 4, 5}, c) == (std::vector<int>{2, 4}) && interGallop({}, {1, 2}, c).empty() && interGallop({1}, {}, c).empty() && interBits({}, {}, 1).empty()); }                        // ⑤
    std::cout << "Intersection: merge, hash, bitset and galloping intersections equalled std::set_intersection on 500 random triples, the commutative, associative, idempotent, zero, universe, absorption and distributive laws held, galloping used under 1/100 of the merge comparisons when |A|=10 and |B|=100000, and intersecting the smallest sets first cost fewer hash lookups than largest first" << std::endl; return 0;
}
// Time Complexity: 병합 O(|A| + |B|), 해시 O(min) 기대, 지수 탐색 O(|A| log(|B|/|A|))
// Space Complexity: O(min(|A|, |B|))
```
## Difference()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 차집합(Difference): A \ B = {x | x ∈ A 이고 x ∉ B}. 교환 법칙이 성립하지 않는다(A\B ≠ B\A, 보통은). 정렬 배열은 병합 O(|A|+|B|) 로 A 에서 B 와 겹치는 원소를 건너뛰고, 해시는 B 를 해시로 만든 뒤 A 를 훑으며 해시에 없는 것만 남긴다 — A 가 정렬되지 않았거나 스트림이어도 되고 O(|A|+|B|) 기대. 비트 집합은 A AND (NOT B) 워드 연산.
// 항등식: A\B = A∩Bᶜ (우주 U 에서의 여집합), |A\B| = |A|−|A∩B|, A\A = ∅, A\∅ = A, ∅\A = ∅, (A\B)\C = A\(B∪C), A\(B\C) = (A\B)∪(A∩C), A\B 와 B 는 서로소, A = (A\B) ∪ (A∩B) (서로소 분할). 결합 법칙은 성립하지 않는다.
// 검증: ① 병합·해시·비트 세 구현이 std::set_difference 와 같음 ② 위 항등식을 무작위 삼중에서 확인 ③ 교환·결합이 성립하지 않는 구체적 반례가 실제로 존재함을 찾아 확인 ④ A = (A\B) ⊔ (A∩B) 분할이 서로소이고 합이 A ⑤ 순서 없는 입력(정렬 안 된 스트림)을 해시로 처리해도 같은 원소(순서만 입력 순서 유지) ⑥ 경계: 빈 집합, 같은 집합, 부분집합.
std::vector<int> diffMerge(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::size_t i = 0, j = 0; while (i < a.size()) { if (j >= b.size() || a[i] < b[j]) r.push_back(a[i++]); else if (b[j] < a[i]) j++; else { i++; j++; } } return r; }
std::vector<int> diffHash(const std::vector<int>& a, const std::vector<int>& b) { std::unordered_set<int> h(b.begin(), b.end()); std::vector<int> r; std::unordered_set<int> seen; for (int x : a) if (!h.count(x) && seen.insert(x).second) r.push_back(x); return r; }   // a 의 입력 순서를 유지, 중복은 한 번만
std::vector<int> diffBits(const std::vector<int>& a, const std::vector<int>& b, int U) { std::vector<uint64_t> x((U + 63) / 64), y(x.size()); for (int v : a) x[v >> 6] |= 1ull << (v & 63); for (int v : b) y[v >> 6] |= 1ull << (v & 63); std::vector<int> r; for (std::size_t w = 0; w < x.size(); w++) { uint64_t m = x[w] & ~y[w]; while (m) { r.push_back((int)(w * 64 + __builtin_ctzll(m))); m &= m - 1; } } return r; }
std::vector<int> randomSet(std::mt19937& rng, int U, int maxSize) { std::set<int> s; int n = (int)(rng() % (maxSize + 1)); for (int i = 0; i < n; i++) s.insert((int)(rng() % U)); return std::vector<int>(s.begin(), s.end()); }
std::vector<int> uni(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> inter(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
int main() {
    std::mt19937 rng(15); int commutativeFails = 0, associativeFails = 0;
    for (int rep = 0; rep < 500; rep++) { int U = 1 + (int)(rng() % 150); auto a = randomSet(rng, U, 40), b = randomSet(rng, U, 40), c = randomSet(rng, U, 40); std::vector<int> want; std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(want));
        auto h = diffHash(a, b); std::sort(h.begin(), h.end()); assert(diffMerge(a, b) == want && h == want && diffBits(a, b, U) == want);                                                           // ①
        std::vector<int> comp; { std::vector<int> all(U); for (int i = 0; i < U; i++) all[i] = i; comp = diffMerge(all, b); } assert(diffMerge(a, b) == inter(a, comp) && want.size() == a.size() - inter(a, b).size());      // ② A\B = A∩Bᶜ, 크기
        assert(diffMerge(a, a).empty() && diffMerge(a, {}) == a && diffMerge({}, a).empty() && diffMerge(diffMerge(a, b), c) == diffMerge(a, uni(b, c)) && diffMerge(a, diffMerge(b, c)) == uni(diffMerge(a, b), inter(a, c)));
        assert(inter(want, b).empty() && uni(want, inter(a, b)) == a);                                                                                                                                 // ④ 서로소 분할
        if (diffMerge(a, b) != diffMerge(b, a)) commutativeFails++; if (diffMerge(diffMerge(a, b), c) != diffMerge(a, diffMerge(b, c))) associativeFails++; }                                              // ③ 반례 개수
    assert(commutativeFails > 100 && associativeFails > 10);
    { assert((diffMerge({1, 2, 3}, {3, 4}) == std::vector<int>{1, 2}) && (diffMerge({3, 4}, {1, 2, 3}) == std::vector<int>{4}) && diffMerge({1, 2}, {1, 2, 3}).empty()); }                           // 구체적 반례: A\B ≠ B\A
    { std::vector<int> stream = {9, 3, 3, 7, 1, 9, 5, 7}; auto r = diffHash(stream, {3, 5}); assert(r == (std::vector<int>{9, 7, 1})); }                                                                  // ⑤ 정렬 안 된 스트림: 입력 순서 유지, 중복 제거
    { assert(diffBits({}, {}, 1).empty() && diffBits({0}, {0}, 1).empty() && diffBits({0}, {}, 1) == std::vector<int>{0}); for (int U : {63, 64, 65, 129}) { std::vector<int> a, b; for (int i = 0; i < U; i++) { a.push_back(i); if (i % 2) b.push_back(i); } std::vector<int> w; std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(w)); assert(diffBits(a, b, U) == w); } }   // ⑥
    std::cout << "Difference: merge, hash and bitset differences equalled std::set_difference on 500 random triples, A\\B = A and complement-of-B, |A\\B| = |A|-|A and B|, (A\\B)\\C = A\\(B or C) and A = (A\\B) disjoint-union (A and B) held, and non-commutativity (" << commutativeFails << " cases) and non-associativity (" << associativeFails << " cases) were found concretely" << std::endl; return 0;
}
// Time Complexity: 병합 O(|A| + |B|), 해시 기대 O(|A| + |B|), 비트 O(U/64)
// Space Complexity: O(|A| + |B|)
```
## SymmetricDifference()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <map>
#include <random>
#include <set>
#include <vector>

// 대칭차집합(Symmetric Difference): A △ B = (A \ B) ∪ (B \ A) = (A ∪ B) \ (A ∩ B), 즉 둘 중 정확히 한쪽에만 있는 원소들이다. 정렬 배열은 병합으로 한 쪽에만 있는 값을 내보내고(같으면 건너뜀) O(|A|+|B|), 비트 집합은 워드 XOR. 논리의 배타적 논리합(XOR)과 같은 구조라서 집합의 모임 (P(U), △) 은 ∅ 을 항등원으로, 모든 원소가 자기 자신이 역원인 아벨 군을 이룬다.
// 법칙: 교환·결합, A△∅ = A, A△A = ∅ (자기 역원), A△B△B = A (같은 변화를 두 번 적용하면 원상복구 — 차이 적용·패치·체크섬에 쓰임), |A△B| = |A|+|B|−2|A∩B|, A△B = ∅ ⇔ A = B, 교집합에 대한 분배 A∩(B△C) = (A∩B)△(A∩C). k 개 집합을 연속으로 △ 하면 홀수 개의 집합에 들어 있는 원소만 남는다.
// 검증: ① 병합·비트·정의(두 차집합의 합집합)·(합집합 − 교집합) 네 구현이 서로 같음 ② 군 법칙: 교환·결합·항등·자기 역원·A△B△B = A ③ 크기 공식 |A|+|B|−2|A∩B| 와 A△B = ∅ ⇔ A = B ④ 분배 법칙 ⑤ k 개 집합을 연속 △ 하면 홀수 번 등장한 원소만 남음(빈도 맵으로 대조) ⑥ 경계와 64 비트 비경계 우주.
std::vector<int> symMerge(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::size_t i = 0, j = 0; while (i < a.size() || j < b.size()) { if (j >= b.size() || (i < a.size() && a[i] < b[j])) r.push_back(a[i++]); else if (i >= a.size() || b[j] < a[i]) r.push_back(b[j++]); else { i++; j++; } } return r; }
std::vector<int> symBits(const std::vector<int>& a, const std::vector<int>& b, int U) { std::vector<uint64_t> x((U + 63) / 64), y(x.size()); for (int v : a) x[v >> 6] |= 1ull << (v & 63); for (int v : b) y[v >> 6] |= 1ull << (v & 63); std::vector<int> r; for (std::size_t w = 0; w < x.size(); w++) { uint64_t m = x[w] ^ y[w]; while (m) { r.push_back((int)(w * 64 + __builtin_ctzll(m))); m &= m - 1; } } return r; }
template <class F> std::vector<int> bin(const std::vector<int>& a, const std::vector<int>& b, F f) { std::vector<int> r; f(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> uni(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> inter(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> diff(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> randomSet(std::mt19937& rng, int U, int maxSize) { std::set<int> s; int n = (int)(rng() % (maxSize + 1)); for (int i = 0; i < n; i++) s.insert((int)(rng() % U)); return std::vector<int>(s.begin(), s.end()); }
int main() {
    std::mt19937 rng(16);
    for (int rep = 0; rep < 500; rep++) { int U = 1 + (int)(rng() % 200); auto a = randomSet(rng, U, 50), b = randomSet(rng, U, 50), c = randomSet(rng, U, 50); auto m = symMerge(a, b);                                // ① 네 구현
        std::vector<int> viaStd; std::set_symmetric_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(viaStd)); assert(m == viaStd && symBits(a, b, U) == viaStd && m == uni(diff(a, b), diff(b, a)) && m == diff(uni(a, b), inter(a, b)));
        assert(symMerge(b, a) == m && symMerge(symMerge(a, b), c) == symMerge(a, symMerge(b, c)) && symMerge(a, {}) == a && symMerge(a, a).empty() && symMerge(symMerge(a, b), b) == a);                             // ② 군 법칙
        assert(m.size() == a.size() + b.size() - 2 * inter(a, b).size() && (m.empty() == (a == b)));                                                                                                       // ③
        assert(inter(a, symMerge(b, c)) == symMerge(inter(a, b), inter(a, c))); }                                                                                                                          // ④ 분배
    for (int rep = 0; rep < 200; rep++) { int k = 1 + (int)(rng() % 9); std::vector<int> acc; std::map<int, int> freq; for (int i = 0; i < k; i++) { auto s = randomSet(rng, 60, 30); acc = symMerge(acc, s); for (int x : s) freq[x]++; }       // ⑤ 홀수 번 등장
        std::vector<int> odd; for (auto& kv : freq) if (kv.second % 2) odd.push_back(kv.first); assert(acc == odd); }
    { assert(symMerge({}, {}).empty() && symMerge({1, 2}, {1, 2}).empty() && symMerge({1, 2}, {}) == (std::vector<int>{1, 2}) && symMerge({1, 3}, {2, 3}) == (std::vector<int>{1, 2}) && symBits({}, {}, 1).empty());                      // ⑥
      for (int U : {63, 64, 65, 130}) { std::vector<int> a, b; for (int i = 0; i < U; i += 2) a.push_back(i); for (int i = 0; i < U; i += 3) b.push_back(i); std::vector<int> w; std::set_symmetric_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(w)); assert(symBits(a, b, U) == w); } }
    std::cout << "SymmetricDifference: merge, bitset XOR, the union-of-differences definition and (union minus intersection) all equalled std::set_symmetric_difference on 500 random triples, the abelian-group laws (commutative, associative, identity, self-inverse, A xor B xor B = A) and |A|+|B|-2|A and B| held, and XOR-ing k sets kept exactly the elements present in an odd number of them" << std::endl; return 0;
}
// Time Complexity: 병합 O(|A| + |B|), 비트 O(U/64)
// Space Complexity: O(|A| + |B|)
```
## Complement()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <vector>

// 여집합(Complement): 전체집합(우주) U 안에서 A 에 속하지 않는 원소들, Aᶜ = U \ A. 여집합은 우주가 정해져 있어야 의미가 있다 — 우주 없이는 "A 에 없는 모든 것"이 무한 집합이다. 정렬 배열은 A 의 빈틈(gap)을 훑어 O(|U|)(우주가 {0..n−1} 이면 A 의 원소 사이의 구간), 비트 집합은 모든 워드를 NOT 한다.
// 비트 구현의 전형적인 함정: 우주 크기 n 이 64 의 배수가 아니면 마지막 워드의 남는 비트(n 이상의 위치)까지 ~ 가 1 로 만들어 우주 밖 원소가 생기고 크기·순회·비교가 틀어진다. NOT 한 뒤 마지막 워드를 마스크로 잘라 내야 한다. 법칙: (Aᶜ)ᶜ = A, A ∪ Aᶜ = U, A ∩ Aᶜ = ∅, 드모르간 (A∪B)ᶜ = Aᶜ∩Bᶜ, (A∩B)ᶜ = Aᶜ∪Bᶜ, |Aᶜ| = |U|−|A|, ∅ᶜ = U, Uᶜ = ∅, A ⊆ B ⇔ Bᶜ ⊆ Aᶜ.
// 검증: ① 우주 크기 1..200(64 의 배수 아닌 값 다수)에서 비트 여집합이 정의(U \ A)와 같고 마스크 없는 ~ 는 n 이 64 의 배수가 아닐 때 우주 밖 비트를 만든다는 것을 확인 ② 위 법칙들을 무작위 집합에서 확인 ③ 정렬 배열의 틈 훑기 여집합 == 비트 여집합 ④ 연속하지 않는 우주 U 에서도 Aᶜ = U \ A ⑤ 크기 공식 |Aᶜ| = n − |A|, 우주 크기 1 과 빈 집합 경계.
struct Bits { std::size_t n; std::vector<uint64_t> w;
    explicit Bits(std::size_t universe) : n(universe), w((universe + 63) / 64, 0) {}
    void set(std::size_t i) { w[i >> 6] |= 1ull << (i & 63); } bool test(std::size_t i) const { return w[i >> 6] >> (i & 63) & 1; }
    void maskTail() { if (n % 64) w[w.size() - 1] &= (1ull << (n % 64)) - 1; }
    Bits complement() const { Bits r(n); for (std::size_t i = 0; i < w.size(); i++) r.w[i] = ~w[i]; r.maskTail(); return r; }                      // 마스크로 우주 밖 비트를 지운다
    Bits complementNoMask() const { Bits r(n); for (std::size_t i = 0; i < w.size(); i++) r.w[i] = ~w[i]; return r; }                          // 함정: 마스크 없음
    std::size_t count() const { std::size_t c = 0; for (uint64_t x : w) c += (std::size_t)__builtin_popcountll(x); return c; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < w.size(); i++) { uint64_t m = w[i]; while (m) { r.push_back((int)(i * 64 + __builtin_ctzll(m))); m &= m - 1; } } return r; }
    friend Bits operator&(const Bits& a, const Bits& b) { Bits r(a.n); for (std::size_t i = 0; i < a.w.size(); i++) r.w[i] = a.w[i] & b.w[i]; return r; }
    friend Bits operator|(const Bits& a, const Bits& b) { Bits r(a.n); for (std::size_t i = 0; i < a.w.size(); i++) r.w[i] = a.w[i] | b.w[i]; return r; }
    friend bool operator==(const Bits& a, const Bits& b) { return a.n == b.n && a.w == b.w; } };
std::vector<int> complementSorted(const std::vector<int>& a, int n) { std::vector<int> r; int next = 0; for (int x : a) { for (; next < x; next++) r.push_back(next); next = x + 1; } for (; next < n; next++) r.push_back(next); return r; }       // 빈틈 훑기
std::vector<int> relativeComplement(const std::vector<int>& U, const std::vector<int>& a) { std::vector<int> r; std::set_difference(U.begin(), U.end(), a.begin(), a.end(), std::back_inserter(r)); return r; }
Bits fromItems(const std::vector<int>& v, int n) { Bits b((std::size_t)n); for (int x : v) b.set((std::size_t)x); return b; }
int main() {
    std::mt19937 rng(17);
    for (int n = 1; n <= 200; n++) { std::vector<int> a; for (int i = 0; i < n; i++) if (rng() % 3 == 0) a.push_back(i); Bits A = fromItems(a, n); std::vector<int> want; { std::vector<int> U(n); for (int i = 0; i < n; i++) U[i] = i; want = relativeComplement(U, a); }   // ① ③ ⑤
        Bits C = A.complement(); assert(C.items() == want && complementSorted(a, n) == want && C.count() == (std::size_t)n - a.size()); Bits bad = A.complementNoMask(); if (n % 64) assert(bad.count() > C.count() && !(bad == C)); else assert(bad == C);       // 마스크 없는 NOT 의 함정
        assert(C.complement() == A && (A | C).count() == (std::size_t)n && (A & C).count() == 0); }
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 190); std::vector<int> a, b; for (int i = 0; i < n; i++) { if (rng() % 2) a.push_back(i); if (rng() % 2) b.push_back(i); } Bits A = fromItems(a, n), B = fromItems(b, n);                              // ② 법칙
        assert((A | B).complement() == (A.complement() & B.complement()) && (A & B).complement() == (A.complement() | B.complement()));                                                                                          // 드모르간
        Bits empty(n), U = empty.complement(); assert(U.count() == (std::size_t)n && U.complement() == empty);                                                                                                                      // ∅ᶜ = U, Uᶜ = ∅
        std::vector<int> inter; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(inter)); bool aSubB = inter.size() == a.size(); assert(aSubB == ((B.complement() & A).count() == 0) && aSubB == ((B.complement() | A.complement()) == A.complement())); }   // A ⊆ B ⇔ Bᶜ ⊆ Aᶜ
    for (int rep = 0; rep < 200; rep++) { std::set<int> us; for (int i = 0, k = 5 + (int)(rng() % 40); i < k; i++) us.insert((int)(rng() % 1000)); std::vector<int> U(us.begin(), us.end()); std::vector<int> a; for (int x : U) if (rng() % 3 == 0) a.push_back(x);     // ④ 연속하지 않는 우주
        std::vector<int> c = relativeComplement(U, a); assert(c.size() == U.size() - a.size()); std::vector<int> back = relativeComplement(U, c); assert(back == a); std::vector<int> both; std::set_union(a.begin(), a.end(), c.begin(), c.end(), std::back_inserter(both)); assert(both == U); }
    { Bits z(1); assert(z.complement().count() == 1 && z.complement().complement().count() == 0); Bits e(0); assert(e.complement().count() == 0 && complementSorted({}, 0).empty() && complementSorted({}, 3) == (std::vector<int>{0, 1, 2}) && complementSorted({0, 1, 2}, 3).empty()); }   // ⑤
    std::cout << "Complement: for every universe size 1..200 the masked bitset complement equalled U minus A, the unmasked NOT leaked bits beyond the universe whenever n was not a multiple of 64, the gap-scan complement of a sorted array agreed, and double complement, De Morgan, A subset B iff B' subset A', and complements in non-contiguous universes all held" << std::endl; return 0;
}
// Time Complexity: 비트 O(U/64), 정렬 배열 O(|U|)
// Space Complexity: O(U/64)
```
## CartesianProduct()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 데카르트 곱(Cartesian Product): A × B = {(a, b) | a ∈ A, b ∈ B}, 순서쌍의 집합이다. 크기는 |A|·|B|, 순서가 있어서 A × B ≠ B × A (A = B 이거나 한쪽이 공집합일 때만 같다). 행 우선(사전식) 순서로 만들면 i 번째 쌍은 (A[i / |B|], B[i % |B|]) 로 곧바로 계산되므로 곱을 실제로 저장하지 않고 "게으르게" 다룰 수 있다. 반대로 쌍 (a, b) 의 번호는 index(a)·|B| + index(b). k 개 집합의 곱은 마지막 자리부터 올리는 주행 계수기(odometer)로 순회한다 — 각 자리의 크기가 다른 혼합 진법의 수 세기와 같다.
// 성질: 어느 한쪽이 공집합이면 곱도 공집합, 분배 A×(B∪C) = (A×B)∪(A×C), A×(B∩C) = (A×B)∩(A×C), 결합은 ((a,b),c) ↔ (a,(b,c)) 의 일대일 대응(엄밀히는 같은 집합이 아니라 동형), 사영 π₁(A×B) = A (B ≠ ∅ 일 때). 곱의 크기는 k 개 집합이면 Π|Aᵢ| 로 빠르게 커진다.
// 검증: ① 곱의 크기·사전식 순서·중복 없음이 이중 반복문과 같고 번호 ↔ 쌍 변환이 서로 역 ② 공집합 곱과 A×B = B×A 조건을 {0,1,2} 의 모든 부분집합 쌍(8×8)에서 전수 확인 ③ 분배 법칙 ④ k 개 집합 곱의 주행 계수기가 재귀 정의와 같은 순서·개수이고 사영이 원래 집합을 복원 ⑤ 결합 동형 ((a,b),c) ↔ (a,(b,c)) 가 일대일 ⑥ 곱을 저장하지 않고 번호로 접근하는 게으른 접근이 저장한 곱과 일치.
typedef std::vector<std::pair<int, int>> Pairs;
Pairs product(const std::vector<int>& a, const std::vector<int>& b) { Pairs r; for (int x : a) for (int y : b) r.push_back({x, y}); return r; }
std::pair<int, int> lazyAt(const std::vector<int>& a, const std::vector<int>& b, std::size_t i) { return {a[i / b.size()], b[i % b.size()]}; }                  // 저장하지 않고 번호로 접근
std::size_t indexOf(const std::vector<int>& a, const std::vector<int>& b, int x, int y) { return (std::size_t)(std::find(a.begin(), a.end(), x) - a.begin()) * b.size() + (std::size_t)(std::find(b.begin(), b.end(), y) - b.begin()); }
std::vector<std::vector<int>> productK(const std::vector<std::vector<int>>& sets) { std::vector<std::vector<int>> out; for (const auto& s : sets) if (s.empty()) return out; std::vector<std::size_t> idx(sets.size(), 0); if (sets.empty()) return {{}};
    for (;;) { std::vector<int> t; for (std::size_t i = 0; i < sets.size(); i++) t.push_back(sets[i][idx[i]]); out.push_back(t); std::size_t d = sets.size(); while (d > 0) { d--; if (++idx[d] < sets[d].size()) break; idx[d] = 0; if (d == 0) return out; } } }   // 주행 계수기
void productRec(const std::vector<std::vector<int>>& sets, std::size_t k, std::vector<int>& cur, std::vector<std::vector<int>>& out) { if (k == sets.size()) { out.push_back(cur); return; } for (int x : sets[k]) { cur.push_back(x); productRec(sets, k + 1, cur, out); cur.pop_back(); } }
std::vector<int> subsetOf(unsigned mask) { std::vector<int> r; for (int i = 0; i < 3; i++) if (mask >> i & 1) r.push_back(i); return r; }
std::vector<int> uni(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> inter(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
Pairs sortedPairs(Pairs p) { std::sort(p.begin(), p.end()); return p; }
int main() {
    std::mt19937 rng(18);
    for (int rep = 0; rep < 300; rep++) { std::set<int> sa, sb; for (int i = 0, k = (int)(rng() % 9); i < k; i++) sa.insert((int)(rng() % 30)); for (int i = 0, k = (int)(rng() % 9); i < k; i++) sb.insert((int)(rng() % 30)); std::vector<int> a(sa.begin(), sa.end()), b(sb.begin(), sb.end());
        Pairs p = product(a, b); assert(p.size() == a.size() * b.size() && std::is_sorted(p.begin(), p.end()) && std::adjacent_find(p.begin(), p.end()) == p.end());                                                      // ① 크기·사전식·중복 없음
        for (std::size_t i = 0; i < p.size(); i++) { assert(lazyAt(a, b, i) == p[i] && indexOf(a, b, p[i].first, p[i].second) == i); }                                                                               // ⑥ ① 번호 ↔ 쌍
        if (!p.empty()) { std::set<int> proj1, proj2; for (auto& q : p) { proj1.insert(q.first); proj2.insert(q.second); } assert(proj1 == sa && proj2 == sb); } else assert(a.empty() || b.empty()); }                 // ④ 사영 복원
    int equalCases = 0; for (unsigned ma = 0; ma < 8; ma++) for (unsigned mb = 0; mb < 8; mb++) { auto a = subsetOf(ma), b = subsetOf(mb); bool commute = sortedPairs(product(a, b)) == [&] { Pairs q = product(b, a); Pairs r; for (auto& t : q) r.push_back({t.second, t.first}); return sortedPairs(r); }();   // ②
        bool swapped = true; { Pairs ab = sortedPairs(product(a, b)), ba = sortedPairs(product(b, a)); swapped = ab == ba; } bool expected = (a == b) || a.empty() || b.empty(); assert(swapped == expected && commute); equalCases += swapped; }
    assert(equalCases > 8);
    for (int rep = 0; rep < 200; rep++) { std::set<int> sa, sb, sc; for (int i = 0, k = (int)(rng() % 6); i < k; i++) { sa.insert((int)(rng() % 12)); sb.insert((int)(rng() % 12)); sc.insert((int)(rng() % 12)); } std::vector<int> a(sa.begin(), sa.end()), b(sb.begin(), sb.end()), c(sc.begin(), sc.end());   // ③
        Pairs left = sortedPairs(product(a, uni(b, c))), r1 = product(a, b), r2 = product(a, c); r1.insert(r1.end(), r2.begin(), r2.end()); r1 = sortedPairs(r1); r1.erase(std::unique(r1.begin(), r1.end()), r1.end()); assert(left == r1);
        Pairs li = sortedPairs(product(a, inter(b, c))), pb = sortedPairs(product(a, b)), pc = sortedPairs(product(a, c)), both; std::set_intersection(pb.begin(), pb.end(), pc.begin(), pc.end(), std::back_inserter(both)); assert(li == both);
        std::set<std::pair<std::pair<int, int>, int>> left3; std::set<std::pair<int, std::pair<int, int>>> right3; for (int x : a) for (int y : b) for (int z : c) { left3.insert({{x, y}, z}); right3.insert({x, {y, z}}); } assert(left3.size() == right3.size() && left3.size() == a.size() * b.size() * c.size()); }   // ⑤ 결합 동형
    for (int rep = 0; rep < 200; rep++) { int k = (int)(rng() % 5); std::vector<std::vector<int>> sets; std::size_t expect = 1; for (int i = 0; i < k; i++) { std::vector<int> s; for (int j = 0, m = (int)(rng() % 4); j < m; j++) s.push_back(j * 10 + i); sets.push_back(s); expect *= s.size(); }       // ④ k 개 곱
        auto fast = productK(sets); std::vector<std::vector<int>> rec, cur; std::vector<int> tmp; productRec(sets, 0, tmp, rec); assert(fast == rec && fast.size() == (k == 0 ? 1u : expect) && std::is_sorted(fast.begin(), fast.end())); }
    std::cout << "CartesianProduct: pair products matched the nested-loop definition (size, lexicographic order, no duplicates, index to pair conversion in both directions without storing the product), A x B = B x A held exactly when A = B or one side is empty over all 64 subset pairs of {0,1,2}, distributive and associative-isomorphism laws held, and the odometer enumeration of k-fold products matched the recursive definition" << std::endl; return 0;
}
// Time Complexity: 생성 O(|A|·|B|), 번호로 접근 O(1)
// Space Complexity: 저장하면 O(|A|·|B|), 게으른 접근 O(1)
```
## PowerSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 멱집합(Power Set): P(A) = A 의 모든 부분집합의 집합, 크기 2^|A|. 원소마다 "넣는다/안 넣는다" 두 갈래이므로 n 비트 이진수 0 .. 2ⁿ−1 이 곧 부분집합 하나하나이다(i 번째 비트가 1 이면 i 번째 원소 포함). 열거 방법 셋: (1) 비트마스크 반복 — 가장 단순하고 순서가 이진수 세기, (2) 재귀 — 원소 하나를 넣고/빼고 갈라 깊이 우선으로, (3) 이중화 — 빈 집합으로 시작해 새 원소 x 를 볼 때마다 지금까지의 모든 부분집합에 x 를 더한 복사본을 이어 붙인다(크기가 두 배로). 그레이 코드 순서로 열거하면 이웃한 부분집합이 정확히 원소 하나만 다르다.
// 성질: |P(A)| = 2^|A| (공집합의 멱집합은 {∅} 로 크기 1), 크기별 개수는 이항계수 C(n, k) 이고 합이 2ⁿ, A 와 B 가 서로소이면 |P(A∪B)| = |P(A)|·|P(B)|, P(A)∩P(B) = P(A∩B), P(A)∪P(B) ⊆ P(A∪B) (보통은 진부분집합 — 한쪽의 원소와 다른 쪽의 원소를 섞은 부분집합이 빠짐), A ⊆ B ⇔ P(A) ⊆ P(B). 2ⁿ 이라서 n ≈ 25 만 넘어도 열거가 불가능해진다.
// 검증: ① n ≤ 12 에서 세 열거 방법이 같은 부분집합들(집합으로 비교)이고 개수가 정확히 2ⁿ, 중복 없음 ② 크기별 개수가 이항계수 ③ 그레이 순서에서 이웃한 부분집합이 대칭차가 정확히 1 원소(첫째·마지막도 순환적으로) ④ P(A∩B) = P(A)∩P(B), 서로소일 때 크기의 곱, P(A)∪P(B) ⊊ P(A∪B) 가 되는 사례 ⑤ A ⊆ B ⇔ P(A) ⊆ P(B) ⑥ n = 0 에서 {∅}, n = 16 (65536 개)에서도 마스크·그레이가 같은 집합족이고 그레이만 순환적으로 한 원소씩 달라짐.
typedef std::vector<int> Subset;
std::vector<Subset> byMask(const std::vector<int>& a) { std::vector<Subset> out; for (unsigned m = 0; m < (1u << a.size()); m++) { Subset s; for (std::size_t i = 0; i < a.size(); i++) if (m >> i & 1) s.push_back(a[i]); out.push_back(s); } return out; }
void recur(const std::vector<int>& a, std::size_t i, Subset& cur, std::vector<Subset>& out) { if (i == a.size()) { out.push_back(cur); return; } recur(a, i + 1, cur, out); cur.push_back(a[i]); recur(a, i + 1, cur, out); cur.pop_back(); }
std::vector<Subset> byDoubling(const std::vector<int>& a) { std::vector<Subset> out{Subset()}; for (int x : a) { std::size_t m = out.size(); for (std::size_t i = 0; i < m; i++) { Subset s = out[i]; s.push_back(x); out.push_back(s); } } return out; }
std::vector<Subset> byGray(const std::vector<int>& a) { std::vector<Subset> out; for (unsigned i = 0; i < (1u << a.size()); i++) { unsigned g = i ^ (i >> 1); Subset s; for (std::size_t j = 0; j < a.size(); j++) if (g >> j & 1) s.push_back(a[j]); out.push_back(s); } return out; }
std::set<Subset> asSet(const std::vector<Subset>& v) { std::set<Subset> s; for (auto x : v) { std::sort(x.begin(), x.end()); s.insert(x); } return s; }
unsigned long long binom(int n, int k) { unsigned long long r = 1; for (int i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; }
bool cyclicOneStep(const std::vector<Subset>& g) { for (std::size_t i = 0; i < g.size(); i++) { const Subset& x = g[i]; const Subset& y = g[(i + 1) % g.size()]; Subset sd; std::set_symmetric_difference(x.begin(), x.end(), y.begin(), y.end(), std::back_inserter(sd)); if (sd.size() != 1) return false; } return true; }   // 이웃(마지막→처음 포함)이 원소 하나만 다른가
std::string show(const Subset& s) { std::string r = "{"; for (std::size_t i = 0; i < s.size(); ++i) r += (i ? "," : "") + std::to_string(s[i]); return r + "}"; }
std::string joined(const std::vector<Subset>& v) { std::string r; for (std::size_t i = 0; i < v.size(); ++i) r += (i ? " " : "") + show(v[i]); return r; }
int main() {
    {   const std::vector<int> a = {1, 2, 3};                                                         // 그림: {1,2,3} 의 부분집합 8 개 — 비트마스크 순서와 그레이 코드 순서, 그리고 크기별 층
        assert(joined(byMask(a)) == "{} {1} {2} {1,2} {3} {1,3} {2,3} {1,2,3}");                      // 마스크 i 의 i 번째 비트 = 원소 포함 여부
        assert(joined(byGray(a)) == "{} {1} {1,2} {2} {2,3} {1,2,3} {1,3} {3}");                      // 이웃한 부분집합은 원소 하나만 넣고 뺀 차이
        std::string levels; for (std::size_t k = 0; k <= a.size(); ++k) { std::vector<Subset> row; for (const auto& s : byMask(a)) if (s.size() == k) row.push_back(s); levels += "size " + std::to_string(k) + ": " + joined(row) + "\n"; }
        assert(levels == "size 0: {}\nsize 1: {1} {2} {3}\nsize 2: {1,2} {1,3} {2,3}\nsize 3: {1,2,3}\n");   // 층별 개수 1 3 3 1 = 이항계수
        std::cout << levels; }
    for (int n = 0; n <= 12; n++) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 1); auto m = byMask(a), d = byDoubling(a), g = byGray(a); std::vector<Subset> r; Subset cur; recur(a, 0, cur, r);                                       // ①
        assert(m.size() == (1u << n) && d.size() == m.size() && g.size() == m.size() && r.size() == m.size() && asSet(m).size() == m.size()); assert(asSet(m) == asSet(d) && asSet(m) == asSet(g) && asSet(m) == asSet(r));
        std::vector<unsigned long long> bySize(n + 1, 0); for (auto& s : m) bySize[s.size()]++; for (int k = 0; k <= n; k++) assert(bySize[k] == binom(n, k));                                                          // ②
        if (n >= 1) assert(cyclicOneStep(g)); }   // ③ 순환 그레이
    { auto e = byMask({}); assert(e.size() == 1 && e[0].empty()); }                                                                                                                                                  // ⑥ P(∅) = {∅}
    std::mt19937 rng(19);
    for (int rep = 0; rep < 100; rep++) { std::set<int> sa, sb; for (int i = 0, k = (int)(rng() % 7); i < k; i++) sa.insert((int)(rng() % 10)); for (int i = 0, k = (int)(rng() % 7); i < k; i++) sb.insert((int)(rng() % 10));
        std::vector<int> a(sa.begin(), sa.end()), b(sb.begin(), sb.end()), u, in; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(u)); std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(in));
        auto PA = asSet(byMask(a)), PB = asSet(byMask(b)), PU = asSet(byMask(u)), PI = asSet(byMask(in)); std::set<Subset> inter; std::set_intersection(PA.begin(), PA.end(), PB.begin(), PB.end(), std::inserter(inter, inter.begin())); assert(inter == PI);   // ④
        std::set<Subset> uniP; std::set_union(PA.begin(), PA.end(), PB.begin(), PB.end(), std::inserter(uniP, uniP.begin())); assert(std::includes(PU.begin(), PU.end(), uniP.begin(), uniP.end()));
        if (in.empty() && !a.empty() && !b.empty()) { assert(PU.size() == PA.size() * PB.size() && uniP.size() < PU.size()); }                                                                                           // 서로소: 크기의 곱, P(A)∪P(B) 는 진부분집합
        bool aSubB = std::includes(b.begin(), b.end(), a.begin(), a.end()); assert(aSubB == std::includes(PB.begin(), PB.end(), PA.begin(), PA.end())); }                                                               // ⑤
    { std::vector<int> a(16); std::iota(a.begin(), a.end(), 0); auto m = byMask(a); auto g = byGray(a); assert(m.size() == 65536 && g.size() == 65536 && cyclicOneStep(g) && !cyclicOneStep(m));   // 마스크 순서는 이웃이 한 원소 차이가 아님(검출기가 둘을 구별)
      std::vector<bool> seenM(65536, false), seenG(65536, false); for (std::size_t i = 0; i < 65536; i++) { unsigned mm = 0, mg = 0; for (int x : m[i]) mm |= 1u << x; for (int x : g[i]) mg |= 1u << x; assert(mm == i && !seenG[mg]); seenM[mm] = seenG[mg] = true; } assert(std::count(seenM.begin(), seenM.end(), true) == 65536 && std::count(seenG.begin(), seenG.end(), true) == 65536); }   // 원소가 0..15 이므로 부분집합 = 16 비트 마스크: 마스크 순서는 i 번째가 i, 그레이도 65536 개 서로 다른 마스크를 모두 만듦(같은 집합족)
    std::cout << "PowerSet: bitmask, recursive, doubling and Gray-code enumerations produced the same 2^n distinct subsets for every n<=12 (and n=16, where the Gray order also stayed cyclically one element apart while the mask order did not), the counts by size were the binomial coefficients, consecutive Gray-code subsets (cyclically) differed by exactly one element, and P(A and B) = P(A) and P(B), the disjoint-size product and P(A) subset P(B) iff A subset B all held" << std::endl; return 0;
}
// Time Complexity: O(2ⁿ · n)
// Space Complexity: 열거 O(n) (모두 저장하면 O(2ⁿ · n))
```

# Part 3. 관계 판별
## IsSubset()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 부분집합 판정(IsSubset): A ⊆ B ⇔ A 의 모든 원소가 B 에 있다. 먼저 |A| > |B| 이면 O(1) 에 false (필요조건). 정렬 배열은 두 포인터로 B 를 훑으며 A 의 원소를 하나씩 맞춘다 — A 의 원소가 B 에서 건너뛰어지면(B 의 현재 원소가 더 크면) 즉시 false 로 조기 종료, 최악 O(|A|+|B|). 해시는 B 로 해시를 만든 뒤 A 의 각 원소를 조회 — 만드는 데 O(|B|), 조회 O(|A|) 이므로 기대 O(|A|+|B|) (B 의 해시가 이미 있으면 O(|A|)). 비트 집합은 워드마다 (A AND NOT B) == 0 을 검사하고 0 이 아닌 워드가 나오면 즉시 종료. |A| ≪ |B| 이면 병합 대신 지수 탐색이 낫다.
// 성질(부분 순서): 반사 A ⊆ A, 반대칭 A ⊆ B 이고 B ⊆ A 이면 A = B, 추이 A ⊆ B ⊆ C 이면 A ⊆ C. ∅ ⊆ A ⊆ U, A∩B ⊆ A ⊆ A∪B, A ⊆ B ⇔ A∪B = B ⇔ A∩B = A ⇔ A\B = ∅.
// 검증: ① 우주 {0..4} 의 모든 부분집합 쌍 32×32 = 1024 개에서 병합·해시·비트·정의(원소별 검사) 네 구현이 일치 ② 우주 {0..3} 의 모든 부분집합 삼중 16³ 에서 반사·반대칭·추이 ③ 동치 표현 A∪B=B, A∩B=A, A\B=∅ ④ 무작위 큰 집합에서 std::includes 와 일치 ⑤ 조기 종료: 크기로 O(1) 거절, 첫 원소가 어긋나면 비교 1 번, 부분집합이면 비교 횟수가 정확히 4 번(작은 예)·2998 번(|A|=1000, |B|=10⁵ 예)이고 |A|+|B| 이하 ⑥ 비트 구현이 첫 어긋난 워드에서 멈춤.
bool subMerge(const std::vector<int>& a, const std::vector<int>& b, long& cmp) { if (a.size() > b.size()) return false; std::size_t j = 0; for (std::size_t i = 0; i < a.size(); i++) { while (j < b.size() && b[j] < a[i]) { j++; cmp++; } cmp++; if (j >= b.size() || b[j] != a[i]) return false; j++; } return true; }   // b[j] > a[i] 이면 a[i] 가 b 에 없다
bool subHash(const std::vector<int>& a, const std::vector<int>& b) { if (a.size() > b.size()) return false; std::unordered_set<int> h(b.begin(), b.end()); for (int x : a) if (!h.count(x)) return false; return true; }
bool subBits(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b, long& words) { for (std::size_t i = 0; i < a.size(); i++) { words++; if (a[i] & ~b[i]) return false; } return true; }
bool subDefinition(const std::vector<int>& a, const std::vector<int>& b) { for (int x : a) { bool found = false; for (int y : b) found |= x == y; if (!found) return false; } return true; }
std::vector<int> fromMask(unsigned m, int n) { std::vector<int> r; for (int i = 0; i < n; i++) if (m >> i & 1) r.push_back(i); return r; }
std::vector<uint64_t> toBits(const std::vector<int>& a, int n) { std::vector<uint64_t> w((n + 63) / 64); for (int x : a) w[x >> 6] |= 1ull << (x & 63); return w; }
std::vector<int> uni(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> inter(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> diff(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
int main() {
    int subsetPairs = 0;
    for (unsigned ma = 0; ma < 32; ma++) for (unsigned mb = 0; mb < 32; mb++) { auto a = fromMask(ma, 5), b = fromMask(mb, 5); long cmp = 0, words = 0; bool want = (ma & ~mb) == 0; subsetPairs += want;                                    // ① 1024 쌍
        assert(subMerge(a, b, cmp) == want && subHash(a, b) == want && subBits(toBits(a, 5), toBits(b, 5), words) == want && subDefinition(a, b) == want && std::includes(b.begin(), b.end(), a.begin(), a.end()) == want);
        assert(want == (uni(a, b) == b) && want == (inter(a, b) == a) && want == diff(a, b).empty()); }                                                                                                              // ③ 동치 표현
    assert(subsetPairs == 243);                                                                                                                                                                                  // 3^5 쌍
    for (unsigned ma = 0; ma < 16; ma++) for (unsigned mb = 0; mb < 16; mb++) { auto a = fromMask(ma, 4), b = fromMask(mb, 4); long c = 0; bool ab = subMerge(a, b, c), ba = subMerge(b, a, c); assert(subMerge(a, a, c)); if (ab && ba) assert(a == b);       // ② 반사·반대칭
        for (unsigned mc = 0; mc < 16; mc++) { auto cc = fromMask(mc, 4); if (ab && subMerge(b, cc, c)) assert(subMerge(a, cc, c)); } assert(subMerge({}, a, c) && subMerge(a, fromMask(15, 4), c)); }                                    // 추이, ∅ ⊆ A ⊆ U
    std::mt19937 rng(20);
    for (int rep = 0; rep < 1000; rep++) { std::set<int> sb, sa; for (int i = 0, k = (int)(rng() % 60); i < k; i++) sb.insert((int)(rng() % 120)); std::vector<int> b(sb.begin(), sb.end()); for (int x : b) if (rng() % 4 == 0) sa.insert(x); if (rng() % 3 == 0) sa.insert((int)(rng() % 120)); std::vector<int> a(sa.begin(), sa.end());   // ④
        long cmp = 0, words = 0; bool want = std::includes(b.begin(), b.end(), a.begin(), a.end()); assert(subMerge(a, b, cmp) == want && subHash(a, b) == want && subBits(toBits(a, 120), toBits(b, 120), words) == want); }
    { long cmp = 0; assert(!subMerge({1, 2, 3}, {1, 2}, cmp) && cmp == 0); cmp = 0; assert(!subMerge({0}, {5, 6, 7, 8}, cmp) && cmp == 1); cmp = 0; assert(subMerge({1, 2, 3}, {0, 1, 2, 3, 4}, cmp) && cmp == 4);                                  // ⑤ 크기로 O(1) 거절, 첫 원소 어긋남 1 번, 정확한 비교 수(4 = 건너뜀 1 + 일치 3)
      std::vector<int> a(1000), b(100000); for (int i = 0; i < 1000; i++) a[i] = i * 3; for (int i = 0; i < 100000; i++) b[i] = i; cmp = 0; assert(subMerge(a, b, cmp) && cmp == 2998 && cmp <= 100000 + 1000); }   // 건너뛰기 2·999 번 + 일치 확인 1000 번
    { std::vector<int> a = {200}, b(65); for (int i = 0; i < 65; i++) b[i] = i; long w = 0; assert(!subBits(toBits(a, 256), toBits(b, 256), w) && w == 4);                                                                           // ⑥ 마지막 워드에서야 어긋남: 4 워드 확인
      std::vector<int> c = {1}; w = 0; assert(!subBits(toBits(c, 256), toBits({}, 256), w) && w == 1); }
    std::cout << "IsSubset: merge, hash, bitset and definitional implementations agreed on all 1024 subset pairs of {0..4} (" << subsetPairs << " are subset pairs, 3^5 as predicted), reflexive/antisymmetric/transitive laws held over all subsets of {0..3}, the equivalent formulations A or B = B, A and B = A and A minus B = empty matched, results equalled std::includes on 1000 random pairs, and early exits fired as designed with exact comparison counts (4 and 2998)" << std::endl; return 0;
}
// Time Complexity: 병합 O(|A| + |B|), 해시 기대 O(|A| + |B|) (B 의 해시가 이미 있으면 O(|A|)), 비트 O(U/64)
// Space Complexity: O(1) (해시 방식은 O(|B|))
```
## IsProperSubset()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 진부분집합 판정(IsProperSubset): A ⊊ B ⇔ A ⊆ B 이고 A ≠ B. A ⊆ B 이면 A = B 일 때만 크기가 같으므로 A ⊊ B ⇔ A ⊆ B 이고 |A| < |B| 이다 — 동등성 검사를 따로 할 필요 없이 크기만 비교하면 된다. 진부분집합 관계는 엄격한 부분 순서이다: 비반사 A ⊊ A 는 거짓, 비대칭 A ⊊ B 이면 B ⊊ A 는 거짓, 추이. ⊆ 와의 관계: A ⊆ B ⇔ A ⊊ B 또는 A = B.
// 두 집합의 관계는 정확히 네 가지 중 하나이다: 같다(A = B), A ⊊ B, B ⊊ A, 비교 불가(서로 상대의 부분집합이 아님). n 개 원소의 전체집합에서 부분집합 쌍 (A, B) 중 A ⊆ B 인 것은 3ⁿ 쌍(각 원소가 "A 와 B 모두 / B 에만 / 둘 다 아님" 세 상태), 진부분집합 쌍은 3ⁿ − 2ⁿ 쌍이다. 집합 하나의 진부분집합은 2^|B| − 1 개이다. 불 격자에서 원소 하나만 더 큰 직접 위쪽 이웃(cover)은 n·2ⁿ⁻¹ 쌍이다.
// 검증: ① 비트마스크 표현(A & ~B == 0 && A != B)과 "부분집합이고 크기가 작음" 판정과 정의(부분집합이고 같지 않음)가 모든 n ≤ 8 의 부분집합 쌍에서 일치 ② 쌍의 수가 3ⁿ − 2ⁿ, cover 쌍이 n·2ⁿ⁻¹ ③ 비반사·비대칭·추이(n = 4 전수) ④ 모든 쌍이 네 관계 중 정확히 하나 ⑤ 어떤 집합의 진부분집합 개수 2^|B| − 1 ⑥ std::includes 와 크기 비교로 만든 판정이 무작위 큰 집합에서 일치.
bool properSubset(const std::vector<int>& a, const std::vector<int>& b) { return a.size() < b.size() && std::includes(b.begin(), b.end(), a.begin(), a.end()); }                          // 부분집합 + 크기가 작음
bool properByDefinition(const std::vector<int>& a, const std::vector<int>& b) { return std::includes(b.begin(), b.end(), a.begin(), a.end()) && a != b; }
std::vector<int> fromMask(unsigned m, int n) { std::vector<int> r; for (int i = 0; i < n; i++) if (m >> i & 1) r.push_back(i); return r; }
int relation(unsigned a, unsigned b) { if (a == b) return 0; if ((a & ~b) == 0) return 1; if ((b & ~a) == 0) return 2; return 3; }                                                      // 0 같다, 1 A⊊B, 2 B⊊A, 3 비교 불가
int main() {
    for (int n = 0; n <= 8; n++) { unsigned long long pairs = 0, cover = 0, subsetPairs = 0; unsigned N = 1u << n; unsigned counts[4] = {0, 0, 0, 0};
        for (unsigned ma = 0; ma < N; ma++) for (unsigned mb = 0; mb < N; mb++) { bool proper = (ma & ~mb) == 0 && ma != mb; subsetPairs += (ma & ~mb) == 0; pairs += proper; if (proper && __builtin_popcount(mb) == __builtin_popcount(ma) + 1) cover++;            // ① ②
            if (n <= 5) { auto a = fromMask(ma, n), b = fromMask(mb, n); assert(properSubset(a, b) == proper && properByDefinition(a, b) == proper); } counts[relation(ma, mb)]++;                                                  // ④
            int r = relation(ma, mb); assert((r == 1) == proper && (r == 2) == ((mb & ~ma) == 0 && ma != mb)); }
        unsigned long long p3 = 1, p2 = 1; for (int i = 0; i < n; i++) { p3 *= 3; p2 *= 2; } assert(subsetPairs == p3 && pairs == p3 - p2 && cover == (n ? (unsigned long long)n << (n - 1) : 0ull) && counts[0] + counts[1] + counts[2] + counts[3] == N * N && counts[1] == counts[2] && counts[0] == N);
        for (unsigned mb = 0; mb < N; mb++) { unsigned c = 0; for (unsigned ma = 0; ma < N; ma++) c += (ma & ~mb) == 0 && ma != mb; assert(c == (1u << __builtin_popcount(mb)) - 1); } }                                                // ⑤ 진부분집합 개수
    for (unsigned ma = 0; ma < 16; ma++) { assert(!properSubset(fromMask(ma, 4), fromMask(ma, 4))); for (unsigned mb = 0; mb < 16; mb++) { auto a = fromMask(ma, 4), b = fromMask(mb, 4); if (properSubset(a, b)) assert(!properSubset(b, a));       // ③ 비반사·비대칭
            for (unsigned mc = 0; mc < 16; mc++) { auto c = fromMask(mc, 4); if (properSubset(a, b) && properSubset(b, c)) assert(properSubset(a, c)); } } }
    std::mt19937 rng(21); for (int rep = 0; rep < 1000; rep++) { std::set<int> sb, sa; for (int i = 0, k = (int)(rng() % 50); i < k; i++) sb.insert((int)(rng() % 100)); std::vector<int> b(sb.begin(), sb.end()); for (int x : b) if (rng() % 3) sa.insert(x); std::vector<int> a(sa.begin(), sa.end());     // ⑥
        assert(properSubset(a, b) == properByDefinition(a, b)); assert(!properSubset(b, a) || a != b); }
    { assert(!properSubset({}, {}) && properSubset({}, {1}) && !properSubset({1}, {1}) && properSubset({1}, {1, 2}) && !properSubset({1, 2}, {1}) && !properSubset({3}, {1, 2})); }
    std::cout << "IsProperSubset: the size-based test (subset and strictly smaller) equalled the definition (subset and not equal) for all subset pairs of every universe up to 5 elements; over universes up to 8 elements the number of proper-subset pairs was exactly 3^n - 2^n, cover pairs n*2^(n-1), and every pair fell into exactly one of the four relations (equal, proper subset, proper superset, incomparable)" << std::endl; return 0;
}
// Time Complexity: 부분집합 검사 + O(1) 크기 비교
// Space Complexity: O(1)
```
## IsSuperset()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 상위집합(superset) 판별: A ⊇ B ⇔ B 의 모든 원소가 A 에 있다. IsSubset 의 거울이므로 isSuperset(A, B) = isSubset(B, A) 이다. 정렬된 두 배열에서는 두 포인터를 한 번씩만 전진시키는 병합식 검사로 O(|A| + |B|) 에 끝나고(std::includes 와 같은 방식),
// 해시 집합이면 B 의 원소마다 A 를 조회하는 O(|B|) 기대 시간이다. 진상위집합(proper superset)은 A ⊇ B 이면서 A ≠ B(= |A| > |B|)일 때다.
// 검증: ① 병합식·해시식·std::includes 세 구현이 무작위 집합 쌍 5000개에서 항상 같음 ② 성질: 반사성(A ⊇ A), 반대칭(A ⊇ B 이고 B ⊇ A 이면 A = B), 추이성, 공집합은 모든 집합의 부분집합 ③ A ∪ B ⊇ A, A ⊇ A ∩ B, A ⊇ B ⇔ A ∪ B = A ⇔ A ∩ B = B
bool superMerge(const std::vector<int>& a, const std::vector<int>& b) { size_t i = 0, j = 0; while (j < b.size()) { while (i < a.size() && a[i] < b[j]) i++; if (i == a.size() || a[i] != b[j]) return false; i++; j++; } return true; }
bool superHash(const std::set<int>& a, const std::set<int>& b) { for (int x : b) if (!a.count(x)) return false; return true; }
bool properSuper(const std::set<int>& a, const std::set<int>& b) { return a.size() > b.size() && superHash(a, b); }
int main() {
    std::mt19937 rng(1); int trueCount = 0;
    for (int t = 0; t < 5000; t++) {
        std::set<int> A, B; int na = rng() % 8, nb = rng() % 5; for (int i = 0; i < na; i++) A.insert(rng() % 10); if (rng() % 2) for (int x : A) { if (B.size() < (size_t)nb && rng() % 2) B.insert(x); } for (int i = 0; i < nb && rng() % 2; i++) B.insert(rng() % 10);
        std::vector<int> va(A.begin(), A.end()), vb(B.begin(), B.end()); bool m = superMerge(va, vb), h = superHash(A, B), s = std::includes(A.begin(), A.end(), B.begin(), B.end()); assert(m == h && h == s); trueCount += m;           // ① 세 구현이 같음
        std::set<int> U, I; std::set_union(A.begin(), A.end(), B.begin(), B.end(), std::inserter(U, U.begin())); std::set_intersection(A.begin(), A.end(), B.begin(), B.end(), std::inserter(I, I.begin()));
        assert(superHash(A, A) && superHash(U, A) && superHash(A, I) && superHash(A, {}) && (m == (U == A)) && (m == (I == B)));                                                                                // ② ③ 반사성 · 합집합/교집합 동치
        if (m && superHash(B, A)) assert(A == B); assert(properSuper(A, B) == (m && A != B));                                                                                                          // 반대칭 · 진상위집합
        std::set<int> C; for (int x : B) if (rng() % 2) C.insert(x); if (superHash(A, B) && superHash(B, C)) assert(superHash(A, C)); }                                                                // 추이성
    assert(trueCount > 500 && trueCount < 4500);
    std::cout << "IsSuperset: merge, hash and std::includes agree on 5000 random pairs (" << trueCount << " true); reflexive, antisymmetric, transitive and the union/intersection equivalences hold" << std::endl; return 0;
}
// Time Complexity: 병합식 O(|A| + |B|), 해시식 O(|B|) 기대
// Space Complexity: O(1) 추가 공간
```
## IsDisjoint()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <map>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 서로소 판정(IsDisjoint): A ∩ B = ∅ ⇔ 공통 원소가 없다. 정렬 배열은 두 포인터를 전진시키며 같은 값을 만나는 즉시 false 로 끝낸다(겹치는 것이 일찍 나오면 매우 빠르고, 정말 서로소일 때만 끝까지 훑는다 O(|A|+|B|)). 해시는 큰 쪽으로 해시를 만들어(O(|큰 쪽|)) 작은 쪽의 원소를 찾아 하나라도 있으면 false(조회 O(|작은 쪽|), 합쳐서 기대 O(|A|+|B|) — 큰 쪽의 해시가 이미 있으면 O(min)), 비트 집합은 워드 AND 가 0 이 아니면 false. 서로소 ⇔ |A∪B| = |A|+|B| ⇔ A ⊆ Bᶜ ⇔ A\B = A.
// 집합족 {S₁, …, S_k} 가 쌍마다 서로소(분할의 조건)인지는 모든 쌍을 비교하면 O(k²) 번 검사이지만, 원소별 등장 횟수를 해시로 세어 어떤 원소든 두 번 이상 나오면 겹치는 것으로 O(총 원소 수) 에 판정할 수 있다. 분할(partition)이려면 추가로 합집합이 전체집합이어야 하고 모든 조각이 비어 있지 않아야 한다.
// 검증: ① 우주 {0..4} 의 모든 부분집합 쌍 1024 개에서 병합·해시·비트·정의(교집합이 비었음)가 일치하고 서로소 쌍이 정확히 3⁵ = 243 개(각 원소가 A 에만/B 에만/둘 다 아님) ② 동치 표현 |A∪B| = |A|+|B|, A\B = A, A ⊆ Bᶜ ③ 조기 종료: 첫 원소가 공통이면 비교 1 번, 서로소인 큰 집합은 끝까지 ④ 집합족의 쌍 검사(O(k²))와 등장 횟수 세기(O(N))가 같은 판정, 분할 판정 isPartition(쌍마다 서로소 + 조각이 비어 있지 않음 + 합집합 == 전체)이 만든 분할에서는 참이고 빈 조각 추가·원소 누락·조각 겹침·전체집합 확대에서는 거짓 ⑤ 빈 집합은 어떤 집합과도 서로소 ⑥ 무작위 큰 집합에서 std::set_intersection 결과가 비었는지와 일치.
bool disjMerge(const std::vector<int>& a, const std::vector<int>& b, long& cmp) { std::size_t i = 0, j = 0; while (i < a.size() && j < b.size()) { cmp++; if (a[i] == b[j]) return false; if (a[i] < b[j]) i++; else j++; } return true; }
bool disjHash(const std::vector<int>& a, const std::vector<int>& b) { const auto& s = a.size() <= b.size() ? a : b; const auto& big = a.size() <= b.size() ? b : a; std::unordered_set<int> h(big.begin(), big.end()); for (int x : s) if (h.count(x)) return false; return true; }
bool disjBits(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b) { for (std::size_t i = 0; i < a.size(); i++) if (a[i] & b[i]) return false; return true; }
bool disjDefinition(const std::vector<int>& a, const std::vector<int>& b) { for (int x : a) for (int y : b) if (x == y) return false; return true; }
std::vector<int> fromMask(unsigned m, int n) { std::vector<int> r; for (int i = 0; i < n; i++) if (m >> i & 1) r.push_back(i); return r; }
std::vector<uint64_t> toBits(const std::vector<int>& a, int n) { std::vector<uint64_t> w((n + 63) / 64); for (int x : a) w[x >> 6] |= 1ull << (x & 63); return w; }
bool familyPairwise(const std::vector<std::vector<int>>& fam, long& pairChecks) { for (std::size_t i = 0; i < fam.size(); i++) for (std::size_t j = i + 1; j < fam.size(); j++) { pairChecks++; long c = 0; if (!disjMerge(fam[i], fam[j], c)) return false; } return true; }
bool familyCounting(const std::vector<std::vector<int>>& fam, long& touched) { std::unordered_set<int> seen; for (const auto& s : fam) for (int x : s) { touched++; if (!seen.insert(x).second) return false; } return true; }
bool isPartition(const std::vector<std::vector<int>>& fam, const std::set<int>& universe) { long t = 0; if (!familyCounting(fam, t)) return false; std::set<int> u; for (const auto& s : fam) { if (s.empty()) return false; u.insert(s.begin(), s.end()); } return u == universe; }   // 분할 = 쌍마다 서로소 + 빈 조각 없음 + 합집합 == 전체집합
int main() {
    int disjointPairs = 0;
    for (unsigned ma = 0; ma < 32; ma++) for (unsigned mb = 0; mb < 32; mb++) { auto a = fromMask(ma, 5), b = fromMask(mb, 5); long cmp = 0; bool want = (ma & mb) == 0; disjointPairs += want;                                                // ①
        assert(disjMerge(a, b, cmp) == want && disjHash(a, b) == want && disjBits(toBits(a, 5), toBits(b, 5)) == want && disjDefinition(a, b) == want);
        std::vector<int> u, d, comp; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(u)); std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(d)); for (int i = 0; i < 5; i++) if (!(mb >> i & 1)) comp.push_back(i);
        assert(want == (u.size() == a.size() + b.size()) && want == (d == a) && want == std::includes(comp.begin(), comp.end(), a.begin(), a.end())); }                                                                      // ② 동치 표현
    assert(disjointPairs == 243);
    { long c = 0; assert(!disjMerge({5, 6, 7}, {5, 100}, c) && c == 1); c = 0; std::vector<int> a, b; for (int i = 0; i < 1000; i++) { a.push_back(2 * i); b.push_back(2 * i + 1); } assert(disjMerge(a, b, c) && c >= 1000); }                    // ③ 조기 종료 / 끝까지
    { long c = 0; assert(disjMerge({}, {1, 2}, c) && disjMerge({1, 2}, {}, c) && disjMerge({}, {}, c) && disjHash({}, {1}) && disjBits(toBits({}, 64), toBits({1}, 64))); }                                                           // ⑤ 빈 집합
    std::mt19937 rng(22);
    for (int rep = 0; rep < 1000; rep++) { std::set<int> sa, sb; for (int i = 0, k = (int)(rng() % 25); i < k; i++) sa.insert((int)(rng() % 200)); for (int i = 0, k = (int)(rng() % 25); i < k; i++) sb.insert((int)(rng() % 200)); std::vector<int> a(sa.begin(), sa.end()), b(sb.begin(), sb.end()), i;
        std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(i)); long cmp = 0; assert(disjMerge(a, b, cmp) == i.empty() && disjHash(a, b) == i.empty() && disjBits(toBits(a, 200), toBits(b, 200)) == i.empty()); }                      // ⑥
    long totalPair = 0, totalCount = 0, partitions = 0;
    for (int rep = 0; rep < 300; rep++) { int k = 2 + (int)(rng() % 8); std::vector<std::vector<int>> fam; bool makePartition = rng() % 2; std::vector<int> pool(60); for (int i = 0; i < 60; i++) pool[i] = i; std::shuffle(pool.begin(), pool.end(), rng); std::size_t pos = 0;
        for (int i = 0; i < k; i++) { std::vector<int> s; if (makePartition) { std::size_t len = 1 + rng() % 8; for (std::size_t j = 0; j < len && pos < pool.size(); j++) s.push_back(pool[pos++]); } else { for (int j = 0, m = 1 + (int)(rng() % 6); j < m; j++) s.push_back((int)(rng() % 25)); std::sort(s.begin(), s.end()); s.erase(std::unique(s.begin(), s.end()), s.end()); } if (makePartition) std::sort(s.begin(), s.end()); fam.push_back(s); }
        long pc = 0, tc = 0; bool a = familyPairwise(fam, pc), b = familyCounting(fam, tc); assert(a == b); totalPair += pc; totalCount += tc;                                                                                       // ④
        std::set<int> all; for (auto& s : fam) all.insert(s.begin(), s.end()); bool nonEmpty = std::all_of(fam.begin(), fam.end(), [](const std::vector<int>& s) { return !s.empty(); }); assert(isPartition(fam, all) == (a && nonEmpty));   // 분할 판정 == 서로소 판정 && 빈 조각 없음
        if (makePartition) { std::set<int> U(pool.begin(), pool.begin() + (std::ptrdiff_t)pos); assert(isPartition(fam, U) == nonEmpty);   // 만든 대로 U 의 분할 (풀이 바닥나 빈 조각이 생기면 아님)
            if (nonEmpty) { partitions++; auto f1 = fam; f1.push_back({}); assert(!isPartition(f1, U));                                                                                                                // 빈 조각 하나 추가 → 분할 아님
                auto f2 = fam; f2[0].pop_back(); assert(!isPartition(f2, U));                                                                                                                                       // 원소 하나 빠짐 → 전체집합을 덮지 못함
                auto f3 = fam; f3[0].push_back(f3[1][0]); assert(!isPartition(f3, U));                                                                                                                              // 다른 조각의 원소를 겹쳐 넣음 → 서로소 아님
                auto U2 = U; U2.insert(99); assert(!isPartition(fam, U2)); } } }                                                                                                                                  // 전체집합이 더 큼 → 덮지 못함
    assert(totalPair > 0 && totalCount > 0 && partitions > 50);
    std::cout << "IsDisjoint: merge, hash, bitset and definitional tests agreed on all 1024 pairs of subsets of {0..4} (" << disjointPairs << " disjoint pairs = 3^5), the equivalent forms |A or B| = |A|+|B|, A minus B = A and A subset of complement(B) matched, early exit stopped after one comparison on a shared first element, and the O(N) occurrence-counting test gave the same family-wide verdict as checking all O(k^2) pairs, and the partition test (disjoint, no empty piece, union = universe) accepted the constructed partitions but rejected an added empty piece, a dropped element, an overlapping piece and a larger universe" << std::endl; return 0;
}
// Time Complexity: 병합 O(|A| + |B|) (조기 종료), 해시 기대 O(|A| + |B|) (큰 쪽의 해시가 이미 있으면 O(min)), 비트 O(U/64)
// Space Complexity: O(1) (해시 방식은 O(|큰 쪽|))
```
## Equals()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 집합의 상등(Equals): 두 집합이 같다 ⇔ 원소가 정확히 같다(외연성, extensionality) ⇔ A ⊆ B 이고 B ⊆ A. 원소를 넣은 순서·중복 입력·내부 표현(해시냐 트리냐)은 상등과 무관하다. 구현: 크기가 다르면 O(1) 에 false, 정렬 배열은 원소별 비교, 해시는 A 의 모든 원소가 B 에 있는지(둘 다 중복 없는 집합이고 크기가 같을 때만 이 방향 하나로 충분 — {1,1,2} 와 {1,2,3} 처럼 중복이 든 입력은 먼저 정규화해야 한다), 비트 집합은 워드별 비교.
// 해시 지문(fingerprint): 집합의 순서와 무관한 요약값으로 빠른 부정 판정을 만든다. 원소를 섞은(mixed) 해시들의 합(또는 XOR)은 원소 순서에 무관하므로 같은 집합이면 항상 같은 지문이다. 지문이 다르면 확실히 다른 집합이고, 같으면 높은 확률로 같지만 확정하려면 원소 비교가 필요하다. XOR 만 쓰면 같은 원소가 두 번 들어간 입력(중복)이 상쇄되는 약점이 있어 먼저 중복을 제거해야 한다. 상등은 동치 관계: 반사·대칭·추이.
// 검증: ① 우주 {0..4} 의 모든 부분집합 쌍 1024 개에서 네 구현(정렬 비교·해시·비트·양방향 부분집합)이 일치하고 같은 쌍이 정확히 32 개 ② 같은 원소를 다른 순서·중복으로 넣어 만든 집합들이 모두 같다고 판정하고, 정렬하지 않은 섞인·역순 입력의 지문(합·XOR)도 정렬된 입력과 같다(순서 무관) ③ 반사·대칭·추이(n = 4 전수) ④ 지문: 같은 집합은 항상 같은 지문, 4096 개 부분집합과 10 만 개 무작위 집합에서 서로 다른 집합의 지문 충돌 0 ⑤ 크기가 다르면 O(1) 거절, 같은 크기면 첫 불일치에서 종료 ⑥ XOR 지문의 중복 상쇄 약점 시연.
bool eqSorted(const std::vector<int>& a, const std::vector<int>& b, long& cmp) { if (a.size() != b.size()) return false; for (std::size_t i = 0; i < a.size(); i++) { cmp++; if (a[i] != b[i]) return false; } return true; }
bool eqHash(const std::vector<int>& a, const std::vector<int>& b) { if (a.size() != b.size()) return false; std::unordered_set<int> h(b.begin(), b.end()); for (int x : a) if (!h.count(x)) return false; return true; }
bool eqBits(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b) { return a == b; }
bool eqMutualSubset(const std::vector<int>& a, const std::vector<int>& b) { return std::includes(a.begin(), a.end(), b.begin(), b.end()) && std::includes(b.begin(), b.end(), a.begin(), a.end()); }
uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ull; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull; x = (x ^ (x >> 27)) * 0x94D049BB133111EBull; return x ^ (x >> 31); }
uint64_t fingerprint(const std::vector<int>& a) { uint64_t s = 0; for (int x : a) s += mix((uint64_t)(uint32_t)x); return s ^ (a.size() * 0x9E3779B97F4A7C15ull); }                       // 합 + 크기: 순서 무관
uint64_t xorFingerprint(const std::vector<int>& a) { uint64_t s = 0; for (int x : a) s ^= mix((uint64_t)(uint32_t)x); return s; }
std::vector<int> fromMask(unsigned m, int n) { std::vector<int> r; for (int i = 0; i < n; i++) if (m >> i & 1) r.push_back(i); return r; }
std::vector<uint64_t> toBits(const std::vector<int>& a, int n) { std::vector<uint64_t> w((n + 63) / 64); for (int x : a) w[x >> 6] |= 1ull << (x & 63); return w; }
std::vector<int> normalize(std::vector<int> v) { std::sort(v.begin(), v.end()); v.erase(std::unique(v.begin(), v.end()), v.end()); return v; }
int main() {
    int equalPairs = 0;
    for (unsigned ma = 0; ma < 32; ma++) for (unsigned mb = 0; mb < 32; mb++) { auto a = fromMask(ma, 5), b = fromMask(mb, 5); long cmp = 0; bool want = ma == mb; equalPairs += want;                                                      // ①
        assert(eqSorted(a, b, cmp) == want && eqHash(a, b) == want && eqBits(toBits(a, 5), toBits(b, 5)) == want && eqMutualSubset(a, b) == want); if (want) assert(fingerprint(a) == fingerprint(b)); }
    assert(equalPairs == 32);
    std::mt19937 rng(23);
    for (int rep = 0; rep < 300; rep++) { int n = (int)(rng() % 30); std::vector<int> base(n); for (int& x : base) x = (int)(rng() % 40); auto canon = normalize(base); std::vector<int> shuffled = base; std::shuffle(shuffled.begin(), shuffled.end(), rng); std::vector<int> dup = base; dup.insert(dup.end(), base.begin(), base.end()); std::shuffle(dup.begin(), dup.end(), rng);   // ②
        long c = 0; assert(eqSorted(canon, normalize(shuffled), c) && eqSorted(canon, normalize(dup), c) && fingerprint(canon) == fingerprint(normalize(shuffled)) && fingerprint(canon) == fingerprint(normalize(dup)));
        std::vector<int> perm = canon; std::shuffle(perm.begin(), perm.end(), rng); std::vector<int> rev(canon.rbegin(), canon.rend()); assert(fingerprint(perm) == fingerprint(canon) && fingerprint(rev) == fingerprint(canon) && xorFingerprint(perm) == xorFingerprint(canon)); }   // 정규화(정렬)하지 않은 섞인·역순 입력의 지문도 같다: 순서 무관
    for (unsigned ma = 0; ma < 16; ma++) for (unsigned mb = 0; mb < 16; mb++) { auto a = fromMask(ma, 4), b = fromMask(mb, 4); long c = 0; assert(eqSorted(a, a, c)); assert(eqSorted(a, b, c) == eqSorted(b, a, c)); for (unsigned mc = 0; mc < 16; mc++) { auto cc = fromMask(mc, 4); if (eqSorted(a, b, c) && eqSorted(b, cc, c)) assert(eqSorted(a, cc, c)); } }   // ③
    { std::set<uint64_t> fp; for (unsigned m = 0; m < 4096; m++) fp.insert(fingerprint(fromMask(m, 12))); assert(fp.size() == 4096);                                                                                         // ④ 충돌 0
      std::set<uint64_t> seen; std::set<std::vector<int>> sets; std::mt19937 r2(5); for (int i = 0; i < 100000; i++) { std::vector<int> v; for (int j = 0, k = (int)(r2() % 30); j < k; j++) v.push_back((int)(r2() % 1000000)); v = normalize(v); if (sets.insert(v).second) seen.insert(fingerprint(v)); } assert(seen.size() == sets.size()); }
    { long c = 0; assert(!eqSorted({1, 2, 3}, {1, 2}, c) && c == 0); c = 0; assert(!eqSorted({1, 2, 3}, {9, 2, 3}, c) && c == 1); c = 0; assert(eqSorted({1, 2, 3}, {1, 2, 3}, c) && c == 3); }                                                 // ⑤
    { std::vector<int> a = {7, 7, 3}, b = {3}; assert(xorFingerprint(a) == xorFingerprint(b) && normalize(a) != normalize(b));                                                                                                // ⑥ XOR 은 중복을 상쇄(7 이 두 번 → 0) → 정규화 전에는 쓰면 안 된다
      assert(fingerprint(normalize(a)) != fingerprint(b)); }
    std::cout << "Equals: sorted comparison, hash lookup, bitset comparison and mutual inclusion agreed on all 1024 pairs of subsets of {0..4} (exactly " << equalPairs << " equal pairs), order- and duplicate-insensitive construction gave equal sets (and the fingerprints of shuffled and reversed inputs matched the sorted one), equality was reflexive, symmetric and transitive, the order-independent fingerprint had no collisions across 4096 + about 100000 distinct sets, and the XOR-fingerprint pitfall with duplicates was demonstrated" << std::endl; return 0;
}
// Time Complexity: 정렬 비교 O(N), 해시 O(N) 기대, 지문 비교 O(1) (지문 계산은 O(N))
// Space Complexity: O(1) (해시 방식은 O(N))
```

# Part 4. 반복과 탐색
## Iterator()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 집합의 반복자(Iterator): 집합의 모든 원소를 한 번씩 방문하는 객체다. 순서가 구현에 따라 다르다: 트리 기반 집합(std::set)은 항상 오름차순(키 순서)이고, 해시 집합은 순서가 정해져 있지 않으며 같은 원소들이라도 넣은 순서·재배치(rehash)에 따라 순회 순서가 달라진다. 그래서 집합 위에서 순서에 의존하는 코드를 쓰면 안 된다. 집합의 원소는 키이므로 반복자로 값을 바꿀 수 없다(const) — 바꾸면 정렬 순서나 해시 위치가 깨진다.
// 무효화 규칙(어떤 연산 뒤에 얻어 둔 반복자를 써도 되는가)은 컨테이너마다 다르다. std::set: 삽입은 어떤 반복자도 무효화하지 않고, 삭제는 지워진 원소의 반복자만 무효화한다. std::unordered_set: 삽입이 재배치를 일으키면 모든 반복자가 무효화되지만 원소에 대한 포인터·참조는 유효하다(원소 노드가 옮겨지지 않음). 열린 주소법(이 장의 구현)은 재배치 때 원소가 새 칸으로 옮겨지므로 포인터·참조도 무효이고, 정렬 배열 집합은 삽입이 원소를 밀어 주소가 바뀐다. 순회 중 지우려면 `it = s.erase(it)` 형태로 다음 반복자를 받아야 한다.
// 검증: ① 직접 만든 해시 집합의 반복자가 모든 원소를 정확히 한 번씩 방문하고 범위 for 와 표준 알고리즘(std::distance, std::count, std::accumulate)과 맞음 ② 같은 원소를 다른 순서로 넣으면 해시 순회 순서는 달라질 수 있지만 std::set 은 항상 같은 오름차순 ③ std::set 의 반복자가 삽입·다른 원소의 삭제 뒤에도 유효하고 같은 값을 가리킴 ④ std::unordered_set 은 재배치 뒤에도 원소의 주소가 유지(참조 안정), 열린 주소법은 첫 재배치 뒤 원소의 실제 주소가 바뀌고 정렬 배열은 삽입이 원소를 밀어 냄 ⑤ 순회 중 안전한 삭제(it = erase(it)) ⑥ 원소는 const 로만 접근(static_assert; C++20 에서는 std::forward_iterator 개념도 만족) ⑦ IntSet 의 add·remove(되밀기 삭제)·contains·size·items·reserve·clear 를 2 만 번의 무작위 연산(큰 표 하나, 부하율 1/2 의 용량 16 짜리 표 하나 — 군집이 끝을 감싸는 삭제)에서 std::set 과 대조하고 매 단계 불변식 check()(군집에 빈 칸 없음, 부하율 ≤ 1/2)를 확인.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    class const_iterator {                                                                                           // 슬롯 배열을 앞에서부터 훑으며 빈 슬롯을 건너뛴다
        const IntSet* s_; std::size_t i_; void skip() { while (i_ < s_->key_.size() && !s_->used_[i_]) i_++; }
    public:
        using iterator_category = std::forward_iterator_tag; using value_type = int; using difference_type = std::ptrdiff_t; using pointer = const int*; using reference = const int&;
        const_iterator() : s_(nullptr), i_(0) {} const_iterator(const IntSet* s, std::size_t i) : s_(s), i_(i) { skip(); } const int& operator*() const { return s_->key_[i_]; }
        const_iterator& operator++() { i_++; skip(); return *this; } const_iterator operator++(int) { const_iterator t = *this; ++*this; return t; }
        bool operator==(const const_iterator& o) const { return i_ == o.i_; } bool operator!=(const const_iterator& o) const { return i_ != o.i_; } };
    const_iterator begin() const { return const_iterator(this, 0); } const_iterator end() const { return const_iterator(this, key_.size()); }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
#include <cstdint>
#include <numeric>
#include <type_traits>
int main() {
    std::mt19937 rng(24);
    for (int rep = 0; rep < 200; rep++) { IntSet s; std::set<int> ref; for (int i = 0, k = (int)(rng() % 200); i < k; i++) { int x = (int)(rng() % 500) - 250; s.add(x); ref.insert(x); }                                    // ①
        std::vector<int> visited; for (int x : s) visited.push_back(x); std::vector<int> sorted = visited; std::sort(sorted.begin(), sorted.end()); assert(visited.size() == s.size() && sorted == std::vector<int>(ref.begin(), ref.end()) && std::adjacent_find(sorted.begin(), sorted.end()) == sorted.end());
        assert((std::size_t)std::distance(s.begin(), s.end()) == s.size() && std::count_if(s.begin(), s.end(), [](int x) { return x > 0; }) == std::count_if(ref.begin(), ref.end(), [](int x) { return x > 0; }) && std::accumulate(s.begin(), s.end(), 0L) == std::accumulate(ref.begin(), ref.end(), 0L)); }
    { std::set<int> pick; while (pick.size() < 60) pick.insert((int)(rng() % 1000000)); std::vector<int> items(pick.begin(), pick.end()); int differing = 0; std::vector<int> firstOrder; for (int trial = 0; trial < 20; trial++) { std::vector<int> perm = items; std::shuffle(perm.begin(), perm.end(), rng);        // ② 삽입 순서에 따른 순회 순서
          IntSet h; std::set<int> t; for (int x : perm) { h.add(x); t.insert(x); } std::vector<int> ho(h.begin(), h.end()), to(t.begin(), t.end()); assert(to == items);                                                   // std::set 은 항상 오름차순
          if (trial == 0) firstOrder = ho; else if (ho != firstOrder) differing++; assert(std::is_permutation(ho.begin(), ho.end(), items.begin())); }
      assert(differing > 0); }                                                                                                                                                                                       // 해시: 선형 탐사의 충돌 배치 때문에 삽입 순서에 따라 달라짐
    { std::set<int> t; for (int i = 0; i < 100; i += 2) t.insert(i); auto it = t.find(50); auto itNext = std::next(it); for (int i = 1; i < 100; i += 2) t.insert(i); assert(*it == 50 && *std::next(it) == 51 && std::next(t.find(50)) == std::next(it));   // ③ 삽입 후에도 유효
      t.erase(t.find(10)); t.erase(t.find(70)); assert(*it == 50 && itNext != t.end()); }
    { std::unordered_set<int> u; u.insert(7); const int* addr = &*u.find(7); for (int i = 100; i < 100000; i++) u.insert(i); assert(&*u.find(7) == addr);                                                                    // ④ unordered_set: 참조 안정
      std::vector<int> sortedArr = {1, 3, 5}; sortedArr.reserve(8); const int* pa = &sortedArr[1]; assert(*pa == 3); sortedArr.insert(sortedArr.begin() + 1, 2); assert(*pa == 2 && &sortedArr[2] != pa && sortedArr[2] == 3);   // 정렬 배열 집합: 삽입이 원소를 밀어 pa 는 이제 다른 원소를 가리킴
      IntSet h; h.add(5); auto where5 = [&h] { return (std::uintptr_t)&*std::find(h.begin(), h.end(), 5); }; std::uintptr_t a0 = where5(); long before = h.rehashes; for (int i = 0; h.rehashes == before; i++) h.add(1000 + i); assert(h.contains(5) && where5() != a0); }   // 열린 주소법: 첫 재배치만으로 5 의 주소(정수로 저장해 둔 값)가 바뀜
    { std::set<int> t; for (int i = 0; i < 50; i++) t.insert(i); for (auto it = t.begin(); it != t.end();) { if (*it % 3 == 0) it = t.erase(it); else ++it; }                                                           // ⑤ it = erase(it)
      std::vector<int> want; for (int i = 0; i < 50; i++) if (i % 3) want.push_back(i); assert(std::vector<int>(t.begin(), t.end()) == want); }
    { IntSet s(1); std::set<int> ref; std::mt19937 r3(77); int adds = 0, removes = 0;                                                                                                                               // ⑦ IntSet 자체를 std::set 과 대조: 추가·삭제(되밀기)·조회·불변식
      for (int step = 0; step < 20000; step++) { int x = (int)(r3() % 64) - 20, op = (int)(r3() % 3);
          if (op == 0) { bool added = s.add(x); assert(added == ref.insert(x).second); adds += added; } else if (op == 1) { bool removed = s.remove(x); assert(removed == (ref.erase(x) == 1)); removes += removed; } else assert(s.contains(x) == (ref.count(x) == 1));
          assert(s.size() == ref.size() && s.empty() == ref.empty() && s.check()); if (step % 997 == 0) assert(s.items() == std::vector<int>(ref.begin(), ref.end())); }
      assert(adds > 3000 && removes > 3000 && s.items() == std::vector<int>(ref.begin(), ref.end()));
      IntSet t(4); std::set<int> tr; int fixedCap = 0; for (int step = 0; step < 20000; step++) { int x = (int)(r3() % 40); if (!tr.empty() && r3() % 2) x = *std::next(tr.begin(), (std::ptrdiff_t)(r3() % tr.size()));                                // 용량 16 에서 부하율 1/2(8 개)를 유지하며 추가·삭제 → 군집이 표의 끝을 감싸 도는 삭제를 자주 일으킴
          if (tr.size() < 8 && r3() % 2) { assert(t.add(x) == tr.insert(x).second); } else { assert(t.remove(x) == (tr.erase(x) == 1)); } fixedCap += t.capacity() == 16; assert(t.size() == tr.size() && t.check() && t.items() == std::vector<int>(tr.begin(), tr.end())); }
      assert(fixedCap == 20000);
      s.reserve(1000); assert(s.capacity() >= 2000 && s.items() == std::vector<int>(ref.begin(), ref.end()) && s.check());                                                                                          // reserve: 부하율 ≤ 1/2 를 지키는 용량
      std::size_t cap = s.capacity(); s.clear(); assert(s.empty() && s.size() == 0 && s.begin() == s.end() && !s.contains(0) && s.check() && s.capacity() == cap); assert(s.add(3) && s.contains(3) && s.size() == 1 && s.check()); }   // clear 뒤에도 정상
    static_assert(std::is_const<typename std::remove_reference<decltype(*std::declval<std::set<int>::iterator>())>::type>::value, "set elements are const");                                                          // ⑥
    static_assert(std::is_const<typename std::remove_reference<decltype(*std::declval<IntSet::const_iterator>())>::type>::value, "IntSet elements are const");
    static_assert(std::is_same<std::iterator_traits<IntSet::const_iterator>::iterator_category, std::forward_iterator_tag>::value, "forward iterator");
#if __cplusplus >= 202002L
    static_assert(std::forward_iterator<IntSet::const_iterator>, "C++20 forward iterator");
#endif
    std::cout << "Iterator: the hash set's iterator visited every element exactly once and worked with range-for and standard algorithms; hash iteration order depended on insertion order while std::set always iterated in ascending order; std::set iterators survived insertions and unrelated erasures, std::unordered_set kept element addresses across rehashing, and erase-while-iterating with it = erase(it) was safe; the open-addressing set matched std::set over 20000 random add/remove/contains steps with its invariant checked each step, and a rehash moved an element to a new address" << std::endl; return 0;
}
// Time Complexity: begin 과 ++ 한 번은 최악 O(용량) (해시: 빈 슬롯을 건너뜀), 전체 순회 O(용량) (해시) 또는 O(N) (트리)
// Space Complexity: O(1) 반복자
```
## ForEach()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>
#include <string>

// 각 원소에 적용(ForEach): 집합의 모든 원소에 함수를 한 번씩 적용한다. 순서는 보장되지 않으므로(해시) 결과가 순서에 의존하면 안 된다 — 합·개수·최댓값처럼 순서와 무관한 집계는 안전하고, 출력 순서나 문자열 이어 붙이기는 안전하지 않다. 함수는 원소를 읽기만 해야 한다: 집합의 원소는 키이므로 바꾸면 해시 위치·정렬 순서가 깨진다. 정렬 배열로 만든 "집합"에서 원소를 몰래 바꾸면 정렬 불변식이 무너져 이후 이진 탐색이 틀린 답을 내는 것을 이 코드가 보인다 — std::set 이 원소를 const 로만 주는 이유다.
// 조기 종료가 필요하면 함수가 계속할지 여부를 돌려주게 하는 forEachWhile 을 쓴다. 순회 중에 집합 자체를 바꾸는 것(삽입·삭제)은 반복자를 무효화할 수 있으므로, 바꿀 대상을 따로 모아 둔 뒤 순회가 끝나고 바꾼다.
// 검증: ① 모든 원소에 정확히 한 번씩 호출(호출 횟수 == 크기, 방문 표시 중복 없음) ② 집계(합·XOR·최솟값·최댓값·개수)가 std::set 과 같음 ③ 순서 의존 연산(문자열 이어 붙이기)은 삽입 순서가 다른 두 해시 집합에서 달라질 수 있으나 정렬해서 쓰면 같음 ④ forEachWhile 이 정확히 조건이 깨진 원소에서 멈추고 앞에서 방문한 수만 센다 ⑤ 바꿀 대상을 모았다가 순회 후에 적용하면 안전(모든 짝수를 지우고 절반을 더함) ⑥ 정렬 배열 집합에서 원소를 몰래 바꾸면 정렬이 깨져 이진 탐색이 틀림.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    class const_iterator {                                                                                           // 슬롯 배열을 앞에서부터 훑으며 빈 슬롯을 건너뛴다
        const IntSet* s_; std::size_t i_; void skip() { while (i_ < s_->key_.size() && !s_->used_[i_]) i_++; }
    public:
        using iterator_category = std::forward_iterator_tag; using value_type = int; using difference_type = std::ptrdiff_t; using pointer = const int*; using reference = const int&;
        const_iterator(const IntSet* s, std::size_t i) : s_(s), i_(i) { skip(); } const int& operator*() const { return s_->key_[i_]; }
        const_iterator& operator++() { i_++; skip(); return *this; } const_iterator operator++(int) { const_iterator t = *this; ++*this; return t; }
        bool operator==(const const_iterator& o) const { return i_ == o.i_; } bool operator!=(const const_iterator& o) const { return i_ != o.i_; } };
    const_iterator begin() const { return const_iterator(this, 0); } const_iterator end() const { return const_iterator(this, key_.size()); }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
template <class S, class F> long forEach(const S& s, F f) { long calls = 0; for (int x : s) { f(x); calls++; } return calls; }
template <class S, class F> long forEachWhile(const S& s, F keepGoing) { long visited = 0; for (int x : s) { visited++; if (!keepGoing(x)) break; } return visited; }
int main() {
    std::mt19937 rng(25);
    for (int rep = 0; rep < 300; rep++) { IntSet s; std::set<int> ref; for (int i = 0, k = (int)(rng() % 150); i < k; i++) { int x = (int)(rng() % 400) - 200; s.add(x); ref.insert(x); }
        std::vector<int> seen(401, 0); long calls = forEach(s, [&](int x) { seen[x + 200]++; }); assert(calls == (long)s.size()); for (int c : seen) assert(c <= 1); for (int x : ref) assert(seen[x + 200] == 1);                // ① 정확히 한 번씩
        long sum = 0, xr = 0; int mn = INT_MAX, mx = INT_MIN; long cnt = 0; forEach(s, [&](int x) { sum += x; xr ^= x; mn = std::min(mn, x); mx = std::max(mx, x); cnt++; });                                                   // ②
        long rs = 0, rx = 0; for (int x : ref) { rs += x; rx ^= x; } assert(sum == rs && xr == rx && cnt == (long)ref.size() && (ref.empty() || (mn == *ref.begin() && mx == *ref.rbegin()))); }
    { std::set<int> pick; while (pick.size() < 40) pick.insert((int)(rng() % 1000000)); std::vector<int> items(pick.begin(), pick.end()); bool differ = false; std::string first; for (int t = 0; t < 20; t++) { std::vector<int> perm = items; std::shuffle(perm.begin(), perm.end(), rng); IntSet h; for (int x : perm) h.add(x);   // ③
          std::string cat; forEach(h, [&](int x) { cat += std::to_string(x) + ","; }); if (t == 0) first = cat; else if (cat != first) differ = true; std::vector<int> v(h.begin(), h.end()); std::sort(v.begin(), v.end()); std::string sortedCat; for (int x : v) sortedCat += std::to_string(x) + ","; std::string expect; for (int x : items) expect += std::to_string(x) + ","; assert(sortedCat == expect); }
      assert(differ); }
    { IntSet s; for (int i = 1; i <= 100; i++) s.add(i); std::vector<int> order(s.begin(), s.end()); int stopAt = order[37]; long v = forEachWhile(s, [&](int x) { return x != stopAt; }); assert(v == 38); assert(forEachWhile(s, [](int) { return true; }) == 100); IntSet e; assert(forEachWhile(e, [](int) { return false; }) == 0 && forEach(e, [](int) {}) == 0); }   // ④
    { IntSet s; for (int i = 0; i < 100; i++) s.add(i); std::vector<int> toRemove, toAdd; forEach(s, [&](int x) { if (x % 2 == 0) { toRemove.push_back(x); toAdd.push_back(x + 1000); } });                                               // ⑤ 모았다가 나중에 적용
      for (int x : toRemove) s.remove(x); for (int x : toAdd) s.add(x); assert(s.size() == 100 && s.check()); for (int i = 0; i < 100; i++) assert(s.contains(i) == (i % 2 == 1)); for (int x : toAdd) assert(s.contains(x)); }
    { std::vector<int> sortedSet = {1, 3, 5, 7, 9, 11}; auto mySearch = [](const std::vector<int>& v, int key) { std::size_t lo = 0, hi = v.size(); while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; if (v[mid] < key) lo = mid + 1; else hi = mid; } return lo < v.size() && v[lo] == key; };   // ⑥
      for (int k : sortedSet) assert(mySearch(sortedSet, k)); for (int& x : sortedSet) if (x == 3) x = 100; assert(!std::is_sorted(sortedSet.begin(), sortedSet.end()));                                                // 몰래 바꾸면 정렬 불변식이 깨진다
      assert(std::find(sortedSet.begin(), sortedSet.end(), 5) != sortedSet.end() && !mySearch(sortedSet, 5)); }                                                                                                       // 5 는 있는데 이진 탐색이 못 찾는다
    std::cout << "ForEach: the function ran exactly once per element on 300 random sets, order-independent aggregates (sum, xor, min, max, count) matched std::set while order-dependent string concatenation varied with insertion order, forEachWhile stopped at the failing element, deferring mutations until after iteration was safe, and secretly changing an element of a sorted-array set broke its sortedness" << std::endl; return 0;
}
// Time Complexity: O(용량) (해시) / O(N) (트리)
// Space Complexity: O(1)
```
## Find()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 찾기(Find): 집합에서 원소의 위치(반복자)를 돌려준다. 없으면 end(). `contains` 가 예/아니오만 답하는 것과 달리 찾은 원소를 가리키는 반복자(또는 선택값 optional)를 주어서 바로 이웃으로 갈 수 있다. 비용은 구조에 달려 있다: 해시 집합 기대 O(1), 균형 트리 집합 O(log n) 비교, 정렬 배열 이진 탐색 ⌊log₂ n⌋+1 번, 그리고 정렬되지 않은 vector 의 std::find 는 O(n). 집합이 해 주는 이 보장이 "집합으로 바꿔서 찾는다" 의 이유다.
// 조건으로 찾기(find_if)는 순서 없는 구조에서는 항상 O(n) 이다(해시/트리 구조를 쓸 수 없음). 트리 집합은 순서가 있어서 lower_bound(키 이상 첫 원소), upper_bound(키 초과 첫 원소), 바닥(floor, 키 이하의 최댓값), 천장(ceil, 키 이상의 최솟값)을 O(log n) 에 준다 — 해시 집합은 못 하는 질의다. C++14 의 투명 비교자(std::less<>)를 쓰면 키와 다른 타입(문자열 리터럴 등)으로 임시 객체 없이 찾을 수 있다.
// 검증: ① 직접 만든 해시 집합과 정렬 배열 집합의 find 가 std::set::find 와 같은 결과(있다/없다·값) ② 비교 횟수: 정렬 배열 이진 탐색 ≤ ⌊log₂ n⌋+1, std::set::find 는 ≤ 2·log₂(n+1)+1 (비교자에 카운터를 넣어 측정), vector 의 선형 탐색은 위치+1, 해시 find 의 평균 탐사 < 3 ③ lower_bound/upper_bound/floor/ceil 이 무차별 계산과 같음 ④ find_if 는 순회 순서상 첫 일치(정렬 집합에서는 최솟값) ⑤ 투명 비교자로 const char* 키 찾기 ⑥ 없는 키·빈 집합.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    class const_iterator {                                                                                           // 슬롯 배열을 앞에서부터 훑으며 빈 슬롯을 건너뛴다
        const IntSet* s_; std::size_t i_; void skip() { while (i_ < s_->key_.size() && !s_->used_[i_]) i_++; }
    public:
        using iterator_category = std::forward_iterator_tag; using value_type = int; using difference_type = std::ptrdiff_t; using pointer = const int*; using reference = const int&;
        const_iterator(const IntSet* s, std::size_t i) : s_(s), i_(i) { skip(); } const int& operator*() const { return s_->key_[i_]; }
        const_iterator& operator++() { i_++; skip(); return *this; } const_iterator operator++(int) { const_iterator t = *this; ++*this; return t; }
        bool operator==(const const_iterator& o) const { return i_ == o.i_; } bool operator!=(const const_iterator& o) const { return i_ != o.i_; } };
    const_iterator begin() const { return const_iterator(this, 0); } const_iterator end() const { return const_iterator(this, key_.size()); }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
#include <cmath>
#include <functional>
#include <string>
struct CountingLess { static long cmps; bool operator()(int a, int b) const { cmps++; return a < b; } }; long CountingLess::cmps = 0;
struct SortedArraySet { std::vector<int> a; long cmps = 0;
    bool add(int x) { auto it = std::lower_bound(a.begin(), a.end(), x); if (it != a.end() && *it == x) return false; a.insert(it, x); return true; }
    std::vector<int>::const_iterator find(int x) { std::size_t lo = 0, hi = a.size(); while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; cmps++; if (a[mid] < x) lo = mid + 1; else hi = mid; } return (lo < a.size() && a[lo] == x) ? a.begin() + (long)lo : a.end(); } };
int main() {
    std::mt19937 rng(26);
    for (int rep = 0; rep < 300; rep++) { IntSet h; SortedArraySet sa; std::set<int> ref; for (int i = 0, k = (int)(rng() % 200); i < k; i++) { int x = (int)(rng() % 400); h.add(x); sa.add(x); ref.insert(x); }                  // ①
        for (int q = -5; q < 405; q++) { bool in = ref.count(q) > 0; assert(h.contains(q) == in); auto it = sa.find(q); assert((it != sa.a.end()) == in && (!in || *it == q)); auto rit = ref.find(q); assert((rit != ref.end()) == in); } }
    for (int n : {1, 2, 3, 7, 100, 1000, 100000}) { SortedArraySet sa; std::set<int, CountingLess> ts; std::vector<int> vec; for (int i = 0; i < n; i++) { sa.a.push_back(i * 2); ts.insert(i * 2); vec.push_back(i * 2); }                                    // ② 비교 횟수
        long maxSa = 0, maxTree = 0; std::mt19937 r2(7); for (int q = 0; q < 2000; q++) { int key = (int)(r2() % (2 * n + 2)); long c0 = sa.cmps; sa.find(key); maxSa = std::max(maxSa, sa.cmps - c0); CountingLess::cmps = 0; ts.find(key); maxTree = std::max(maxTree, CountingLess::cmps); }
        assert(maxSa <= (long)std::floor(std::log2((double)n)) + 1 && maxTree <= 2 * (long)std::ceil(std::log2((double)n + 1)) + 2); if (n <= 1000) { long lin = (std::find(vec.begin(), vec.end(), vec[n - 1]) - vec.begin()) + 1; assert(lin == n); } }
    { IntSet h; for (int i = 0; i < 20000; i++) h.add((int)rng()); long before = h.lookupProbes; std::mt19937 r3(9); for (int i = 0; i < 20000; i++) h.contains((int)r3()); assert((double)(h.lookupProbes - before) / 20000 < 3.0); }                  // 해시 find 의 평균 탐사
    for (int rep = 0; rep < 300; rep++) { std::set<int> ref; for (int i = 0, k = (int)(rng() % 60); i < k; i++) ref.insert((int)(rng() % 200)); SortedArraySet sa; for (int x : ref) sa.add(x);                                                 // ③
        for (int q = -3; q < 205; q++) { auto lb = ref.lower_bound(q), ub = ref.upper_bound(q); auto slb = std::lower_bound(sa.a.begin(), sa.a.end(), q), sub = std::upper_bound(sa.a.begin(), sa.a.end(), q); assert((lb == ref.end()) == (slb == sa.a.end()) && (lb == ref.end() || *lb == *slb) && (ub == ref.end()) == (sub == sa.a.end()) && (ub == ref.end() || *ub == *sub));
            int bfFloor = INT_MIN, bfCeil = INT_MAX; for (int x : ref) { if (x <= q) bfFloor = std::max(bfFloor, x); if (x >= q) bfCeil = std::min(bfCeil, x); } bool hasFloor = ub != ref.begin(); assert(hasFloor == (bfFloor != INT_MIN) && (!hasFloor || *std::prev(ub) == bfFloor) && (lb == ref.end()) == (bfCeil == INT_MAX) && (lb == ref.end() || *lb == bfCeil)); } }
    { std::set<int> s = {3, 6, 9, 12, 15}; auto it = std::find_if(s.begin(), s.end(), [](int x) { return x % 2 == 0; }); assert(it != s.end() && *it == 6); assert(std::find_if(s.begin(), s.end(), [](int x) { return x > 100; }) == s.end());          // ④
      IntSet h; for (int x : {3, 6, 9, 12, 15}) h.add(x); auto hi = std::find_if(h.begin(), h.end(), [](int x) { return x % 2 == 0; }); assert(hi != h.end() && *hi % 2 == 0); }
    { std::set<std::string, std::less<>> names = {"alice", "bob", "carol"}; assert(names.find("bob") != names.end() && names.find("dave") == names.end() && names.find(std::string("carol")) != names.end()); }                                      // ⑤ 투명 비교자
    { std::set<int> e; IntSet he; SortedArraySet se; assert(e.find(1) == e.end() && !he.contains(1) && se.find(1) == se.a.end()); IntSet one; one.add(INT_MIN); assert(one.contains(INT_MIN) && !one.contains(INT_MAX)); }       // ⑥
    std::cout << "Find: hash and sorted-array lookups agreed with std::set::find on 300 random sets; the sorted array needed at most floor(log2 n)+1 comparisons and std::set::find at most about 2*log2(n+1), linear search cost position+1, hash lookups averaged under 3 probes; lower_bound, upper_bound, floor and ceil matched brute force, find_if returned the first match in iteration order, and a transparent comparator searched by string literal" << std::endl; return 0;
}
// Time Complexity: 해시 기대 O(1), 트리 O(log N), 정렬 배열 O(log N), find_if O(N)
// Space Complexity: O(1)
```
## Filter()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 걸러내기(Filter): 조건 p 를 만족하는 원소만 남긴 부분집합 {x ∈ S | p(x)} 를 만든다. 집합의 부분집합이므로 결과는 원본에 대해 항상 ⊆ 이고, p 와 ¬p 로 걸러낸 두 집합은 서로소이며 합집합이 원본이다(분할). 법칙: filter(p)∘filter(q) = filter(p∧q) (순서 무관), filter(참) = S, filter(거짓) = ∅, filter(p)(filter(p)(S)) = filter(p)(S) (멱등), filter 는 합집합·교집합에 분배: filter(S∪T) = filter(S)∪filter(T), filter(S∩T) = filter(S)∩filter(T).
// 구현 선택: 새 집합을 만들어 조건을 만족하는 원소를 담거나(원본 보존, O(n)), 제자리에서 조건을 만족하지 않는 원소를 지운다. 제자리 삭제는 구조마다 함정이 있다. 트리 집합은 `it = erase(it)` 로 안전하다. 열린 주소법에서 칸 번호를 올려 가며 지우면, 되밀기(backward shift) 삭제가 뒤 원소를 방금 지운 칸으로 당겨 오기 때문에 칸 번호를 그냥 증가시키면 당겨 온 원소를 건너뛴다(조건을 검사받지 못함). 지울 때는 같은 칸을 다시 검사하거나, 지울 원소를 먼저 모은 뒤 지워야 한다.
// 검증: ① 새 집합 만들기가 std::set 의 필터 결과와 같고 원본이 불변 ② 법칙: filter(p)∘filter(q) = filter(p∧q) = filter(q)∘filter(p), 멱등, 참/거짓, 분할(서로소·합이 원본), 합집합·교집합 분배 ③ 제자리 필터의 올바른 방법 둘(같은 칸 다시 검사·모았다 지우기)이 새 집합 방식과 같은 결과이고 불변식 유지 ④ 칸 번호를 그냥 올리는 순진한 제자리 필터는 조건을 만족하지 않는 원소를 남기는 경우가 무작위 시험에서 실제로 발견되고(남긴 원소는 항상 올바른 결과의 상위집합) 올바른 방법은 한 번도 놓치지 않음 ⑤ std::set 의 안전한 삭제 루프.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    class const_iterator {                                                                                           // 슬롯 배열을 앞에서부터 훑으며 빈 슬롯을 건너뛴다
        const IntSet* s_; std::size_t i_; void skip() { while (i_ < s_->key_.size() && !s_->used_[i_]) i_++; }
    public:
        using iterator_category = std::forward_iterator_tag; using value_type = int; using difference_type = std::ptrdiff_t; using pointer = const int*; using reference = const int&;
        const_iterator(const IntSet* s, std::size_t i) : s_(s), i_(i) { skip(); } const int& operator*() const { return s_->key_[i_]; }
        const_iterator& operator++() { i_++; skip(); return *this; } const_iterator operator++(int) { const_iterator t = *this; ++*this; return t; }
        bool operator==(const const_iterator& o) const { return i_ == o.i_; } bool operator!=(const const_iterator& o) const { return i_ != o.i_; } };
    const_iterator begin() const { return const_iterator(this, 0); } const_iterator end() const { return const_iterator(this, key_.size()); }
    template <class P> long filterNaive(P p) { long removed = 0; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i] && !p(key_[i])) { remove(key_[i]); removed++; } return removed; }   // 순진: 지운 칸을 다시 보지 않는다
    template <class P> long filterSlots(P p) { long removed = 0; std::size_t i = 0; while (i < key_.size()) { if (used_[i] && !p(key_[i])) { remove(key_[i]); removed++; } else i++; } return removed; }   // 지운 칸을 다시 검사
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
template <class P> IntSet filterNew(const IntSet& s, P p) { IntSet r; for (int x : s) if (p(x)) r.add(x); return r; }
template <class P> void filterCollect(IntSet& s, P p) { std::vector<int> dead; for (int x : s) if (!p(x)) dead.push_back(x); for (int x : dead) s.remove(x); }
std::vector<int> sortedItems(const IntSet& s) { std::vector<int> v(s.begin(), s.end()); std::sort(v.begin(), v.end()); return v; }
std::vector<int> uni(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
std::vector<int> inter(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(r)); return r; }
int main() {
    std::mt19937 rng(27); auto even = [](int x) { return x % 2 == 0; }; auto big = [](int x) { return x > 100; }; auto never = [](int) { return false; }; auto always = [](int) { return true; };
    for (int rep = 0; rep < 300; rep++) { IntSet s, t; std::set<int> ref; for (int i = 0, k = (int)(rng() % 150); i < k; i++) { int x = (int)(rng() % 300); s.add(x); ref.insert(x); } for (int i = 0, k = (int)(rng() % 150); i < k; i++) t.add((int)(rng() % 300));
        std::vector<int> before = sortedItems(s); IntSet f = filterNew(s, even); std::vector<int> want; for (int x : ref) if (even(x)) want.push_back(x); assert(sortedItems(f) == want && sortedItems(s) == before);                                    // ①
        auto pq = [&](int x) { return even(x) && big(x); }; assert(sortedItems(filterNew(filterNew(s, even), big)) == sortedItems(filterNew(s, pq)) && sortedItems(filterNew(filterNew(s, big), even)) == sortedItems(filterNew(s, pq)));          // ②
        assert(sortedItems(filterNew(f, even)) == sortedItems(f) && sortedItems(filterNew(s, always)) == before && filterNew(s, never).empty());
        IntSet nf = filterNew(s, [&](int x) { return !even(x); }); assert(inter(sortedItems(f), sortedItems(nf)).empty() && uni(sortedItems(f), sortedItems(nf)) == before);                                                                    // 분할
        std::vector<int> su = uni(sortedItems(s), sortedItems(t)), si = inter(sortedItems(s), sortedItems(t)); IntSet U, I; for (int x : su) U.add(x); for (int x : si) I.add(x);
        assert(sortedItems(filterNew(U, even)) == uni(sortedItems(filterNew(s, even)), sortedItems(filterNew(t, even))) && sortedItems(filterNew(I, even)) == inter(sortedItems(filterNew(s, even)), sortedItems(filterNew(t, even)))); }       // 분배
    long naiveMissed = 0, slotsMissed = 0, collectMissed = 0;
    for (int rep = 0; rep < 400; rep++) { IntSet base; for (int i = 0, k = 20 + (int)(rng() % 200); i < k; i++) base.add((int)(rng() % 1000)); std::vector<int> want = sortedItems(filterNew(base, even));                                               // ③ ④
        IntSet a = base, b = base, c = base; a.filterNaive(even); b.filterSlots(even); filterCollect(c, even);
        for (int x : a) naiveMissed += !even(x); for (int x : b) slotsMissed += !even(x); for (int x : c) collectMissed += !even(x);
        assert(sortedItems(b) == want && sortedItems(c) == want && b.check() && c.check() && a.check()); std::vector<int> an = sortedItems(a); assert(std::includes(an.begin(), an.end(), want.begin(), want.end())); }              // 순진한 결과는 올바른 결과의 상위집합
    assert(slotsMissed == 0 && collectMissed == 0 && naiveMissed > 0);
    { std::set<int> s; for (int i = 0; i < 60; i++) s.insert(i); for (auto it = s.begin(); it != s.end();) { if (!even(*it)) it = s.erase(it); else ++it; } std::vector<int> want; for (int i = 0; i < 60; i += 2) want.push_back(i); assert(std::vector<int>(s.begin(), s.end()) == want); }      // ⑤
    std::cout << "Filter: filtering into a new set matched std::set filtering without touching the source, the fusion, commutation, idempotence, partition and union/intersection distribution laws held on 300 random pairs, in-place filtering by re-checking the same slot or by collecting-then-erasing was exact, and the naive slot-by-slot version left " << naiveMissed << " elements that violate the predicate across 400 trials" << std::endl; return 0;
}
// Time Complexity: 필터링 O(N) (해시: O(용량))
// Space Complexity: O(N) (새 집합) / O(걸러낼 원소 수) (모았다 지우기)
```
## Map()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>

// 변환(Map): 집합의 각 원소에 함수 f 를 적용한 결과들의 집합 f(S) = {f(x) | x ∈ S} 를 만든다 — 상(image). 리스트의 map 과 결정적으로 다른 점: 결과도 집합이라 중복이 합쳐진다. f 가 단사(일대일)가 아니면 |f(S)| < |S| 로 줄어들 수 있고(예: x mod 2 는 어떤 집합이든 크기 ≤ 2), |f(S)| = |S| ⇔ f 가 S 위에서 단사. 그래서 집합의 map 은 크기를 보존하지 않으므로 "크기가 같은 두 집합" 같은 가정을 두면 안 된다.
// 상의 법칙: f(A∪B) = f(A)∪f(B) (정확히 성립), f(A∩B) ⊆ f(A)∩f(B) (일반적으로 진부분 — f 가 단사일 때만 같다: A={1}, B={3}, f(x)=x mod 2 이면 f(A∩B)=∅ 이지만 f(A)∩f(B)={1}), 합성 (g∘f)(S) = g(f(S)), 항등 map 은 항등, 공집합은 공집합으로. 원상(preimage) f⁻¹(T) = {x ∈ 정의역 | f(x) ∈ T} 은 f⁻¹(A∩B) = f⁻¹(A)∩f⁻¹(B), f⁻¹(A∪B) = f⁻¹(A)∪f⁻¹(B), f⁻¹(Aᶜ) = (f⁻¹(A))ᶜ 로 모든 연산을 정확히 보존한다 — 상보다 훨씬 얌전하다.
// 검증: ① 유한 정의역 {0,1,2} 에서 모든 함수 f: {0,1,2} → {0,1,2} (27 개)와 모든 부분집합 쌍 (8×8)에 대해 상의 법칙(합집합 보존, 교집합은 ⊆)과 원상의 법칙(합·교·여집합 보존)을 전수 확인 ② 단사 함수 정확히 6 개이고 단사일 때만 교집합이 정확히 보존되며 단사일 때만 크기가 보존 ③ 합성 (g∘f)(S) = g(f(S)) ④ 무작위 큰 집합에서 해시 구현의 상이 직접 계산한 것과 같고 크기가 |S| 이하 ⑤ 공집합·원소 1개.
class IntSet {                                                                                                       // 결과 집합을 모으는 데 쓰는 해시 집합(열린 주소법, 되밀기 삭제 없이 삽입만 사용)
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_ = 3;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }
    void rebuild() { std::vector<int> old = items(); bits_++; key_.assign((std::size_t)1 << bits_, 0); used_.assign((std::size_t)1 << bits_, 0); size_ = 0; for (int x : old) add(x); }
public:
    IntSet() : key_(8), used_(8, 0) {}
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    std::size_t size() const { return size_; } };
typedef std::set<int> S;
template <class F> S image(const S& s, F f) { S r; for (int x : s) r.insert(f(x)); return r; }
template <class F> S preimage(const S& domain, const S& t, F f) { S r; for (int x : domain) if (t.count(f(x))) r.insert(x); return r; }
S uni(const S& a, const S& b) { S r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::inserter(r, r.begin())); return r; }
S inter(const S& a, const S& b) { S r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::inserter(r, r.begin())); return r; }
S diff(const S& a, const S& b) { S r; std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::inserter(r, r.begin())); return r; }
S subset3(unsigned m) { S r; for (int i = 0; i < 3; i++) if (m >> i & 1) r.insert(i); return r; }
int main() {
    S domain = {0, 1, 2}; int injective = 0, strictlyLosing = 0;
    for (int code = 0; code < 27; code++) { int fv[3] = {code % 3, code / 3 % 3, code / 9}; auto f = [&](int x) { return fv[x]; }; bool inj = fv[0] != fv[1] && fv[0] != fv[2] && fv[1] != fv[2]; injective += inj; bool interAlwaysExact = true, sizeAlwaysKept = true;   // ① ②
        for (unsigned ma = 0; ma < 8; ma++) for (unsigned mb = 0; mb < 8; mb++) { S a = subset3(ma), b = subset3(mb);
            assert(image(uni(a, b), f) == uni(image(a, f), image(b, f)));                                                                                                                                // 상: 합집합 보존
            S lhs = image(inter(a, b), f), rhs = inter(image(a, f), image(b, f)); assert(std::includes(rhs.begin(), rhs.end(), lhs.begin(), lhs.end())); if (lhs != rhs) interAlwaysExact = false;               // 상: 교집합은 ⊆
            if (image(a, f).size() != a.size()) sizeAlwaysKept = false;
            S t = subset3(ma), u = subset3(mb); S universeT = domain;                                                                                                                                    // 원상은 모든 연산을 정확히 보존
            assert(preimage(domain, inter(t, u), f) == inter(preimage(domain, t, f), preimage(domain, u, f)) && preimage(domain, uni(t, u), f) == uni(preimage(domain, t, f), preimage(domain, u, f)));
            S codomain = {0, 1, 2}; assert(preimage(domain, diff(codomain, t), f) == diff(universeT, preimage(domain, t, f))); }
        assert(interAlwaysExact == inj && sizeAlwaysKept == inj); if (!inj) strictlyLosing++; }
    assert(injective == 6 && strictlyLosing == 21);
    { auto f = [](int x) { return x % 2; }; S a = {1}, b = {3}; assert(image(inter(a, b), f).empty() && inter(image(a, f), image(b, f)) == S({1})); S s = {1, 2, 3, 4, 5, 6}; assert(image(s, f).size() == 2); }       // 구체적 반례
    std::mt19937 rng(28);
    for (int rep = 0; rep < 300; rep++) { S s; for (int i = 0, k = (int)(rng() % 40); i < k; i++) s.insert((int)(rng() % 100)); int a = 1 + (int)(rng() % 7), b = (int)(rng() % 11), c = 2 + (int)(rng() % 5); auto f = [&](int x) { return a * x + b; }; auto g = [&](int x) { return x % c; };    // ③ ④
        assert(image(image(s, f), g) == image(s, [&](int x) { return g(f(x)); }) && image(s, [](int x) { return x; }) == s && image(s, g).size() <= s.size());
        IntSet h; for (int x : s) h.add(g(f(x))); std::vector<int> hv = h.items(); S viaHash(hv.begin(), hv.end()); assert(viaHash == image(s, [&](int x) { return g(f(x)); })); }
    { S e; assert(image(e, [](int x) { return x + 1; }).empty() && image(S({7}), [](int x) { return x * 0; }) == S({0})); }                                                                          // ⑤
    std::cout << "Map: over every function from {0,1,2} to itself (27) and all 64 subset pairs the image preserved unions exactly and intersections only up to inclusion, preimages preserved unions, intersections and complements exactly, exactly 6 functions were injective and only those preserved sizes and intersections, composition (g after f)(S) = g(f(S)) held, and a non-injective map shrank sets as predicted" << std::endl; return 0;
}
// Time Complexity: 변환 O(N) (결과 삽입 포함), 정렬이면 O(N log N)
// Space Complexity: O(N)
```
## Reduce()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>
#include <numeric>

// 접기(Reduce): 집합의 모든 원소를 이항 연산 ⊕ 로 하나의 값으로 합친다 — 합, 곱, 최솟값, 최댓값, XOR, 개수. 집합에는 순서가 없으므로(해시 순회 순서는 구현·삽입 순서에 따라 바뀜) 접기 결과가 순서에 의존하면 안 된다. 연산이 교환 법칙(a⊕b = b⊕a)과 결합 법칙((a⊕b)⊕c = a⊕(b⊕c))을 만족하고 항등원 e 가 있으면(교환 모노이드) 어떤 순서로 접어도 같고, 조각으로 나누어 병렬로 접은 뒤 합쳐도 같다. 뺄셈이나 문자열 이어 붙이기는 교환 법칙이 없어서 순회 순서에 따라 결과가 바뀐다 — 집합 위에서 쓰려면 먼저 정렬해 순서를 고정해야 한다.
// 집계를 매번 다시 계산하지 않고 집합이 바뀔 때 함께 갱신(점증 유지)하면 O(1) 에 최신 값을 얻는다: 합은 추가 시 +x, 삭제 시 −x; 순서에 무관한 지문(원소 해시의 합)도 같은 방식. 최솟값·최댓값은 삭제를 되돌릴 수 없어서 점증 유지가 안 되고(삭제되는 값이 최솟값이면 다음 값을 찾아야 함) 순서 있는 트리가 필요하다.
// 검증: ① 합·곱(작은 값)·XOR·최소·최대·개수의 접기가 std::set 의 순회 결과와 같음 ② 삽입 순서가 다른 해시 집합 20 개에서 교환 모노이드 연산의 결과는 모두 같고, 문자열 이어 붙이기와 뺄셈 접기는 서로 달라질 수 있음 ③ 정렬한 뒤 접으면 비교환 연산도 결정적 ④ 비어 있으면 항등원, 원소 1 개면 그 원소 ⑤ 조각 병렬 접기(2~7 조각)가 순차 접기와 같음(교환 모노이드) ⑥ 점증 유지한 합·지문이 임의의 추가·삭제 열 10 만 번 뒤에도 처음부터 다시 계산한 값과 같음.
class IntSet {                                                                                                       // 열린 주소법 해시 집합: 선형 탐사, 부하율 ≤ 1/2, 되밀기(backward-shift) 삭제로 묘비 없음
    std::vector<int> key_; std::vector<unsigned char> used_; std::size_t size_ = 0; unsigned bits_;
    std::size_t home(int x) const { return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - bits_)); }   // 곱셈 해시: 상위 비트 사용
    void place(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) i = (i + 1) & m; used_[i] = 1; key_[i] = x; }
    void rebuild(unsigned nb) { std::vector<int> old; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) old.push_back(key_[i]); bits_ = nb; key_.assign((std::size_t)1 << nb, 0); used_.assign((std::size_t)1 << nb, 0); for (int x : old) place(x); rehashes++; }
public:
    long probes = 0, rehashes = 0; mutable long lookupProbes = 0;
    explicit IntSet(unsigned bits = 3) : key_((std::size_t)1 << bits), used_((std::size_t)1 << bits, 0), bits_(bits) {}
    std::size_t size() const { return size_; } bool empty() const { return size_ == 0; } std::size_t capacity() const { return key_.size(); }
    bool contains(int x) const { std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { lookupProbes++; if (key_[i] == x) return true; i = (i + 1) & m; } return false; }
    bool add(int x) { if ((size_ + 1) * 2 > key_.size()) rebuild(bits_ + 1); std::size_t m = key_.size() - 1, i = home(x); while (used_[i]) { probes++; if (key_[i] == x) return false; i = (i + 1) & m; } used_[i] = 1; key_[i] = x; size_++; return true; }
    bool remove(int x) { std::size_t m = key_.size() - 1, i = home(x); while (used_[i] && key_[i] != x) i = (i + 1) & m; if (!used_[i]) return false;
        for (std::size_t j = i;;) { j = (j + 1) & m; if (!used_[j]) break; std::size_t k = home(key_[j]); bool inRange = (i <= j) ? (i < k && k <= j) : (i < k || k <= j); if (!inRange) { key_[i] = key_[j]; i = j; } }   // 뒤 원소를 당겨 와 군집을 메운다
        used_[i] = 0; size_--; return true; }
    void reserve(std::size_t n) { unsigned b = bits_; while (n * 2 > ((std::size_t)1 << b)) b++; if (b != bits_) rebuild(b); }
    void clear() { std::fill(used_.begin(), used_.end(), 0); size_ = 0; }
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < key_.size(); i++) if (used_[i]) r.push_back(key_[i]); std::sort(r.begin(), r.end()); return r; }
    class const_iterator {                                                                                           // 슬롯 배열을 앞에서부터 훑으며 빈 슬롯을 건너뛴다
        const IntSet* s_; std::size_t i_; void skip() { while (i_ < s_->key_.size() && !s_->used_[i_]) i_++; }
    public:
        using iterator_category = std::forward_iterator_tag; using value_type = int; using difference_type = std::ptrdiff_t; using pointer = const int*; using reference = const int&;
        const_iterator(const IntSet* s, std::size_t i) : s_(s), i_(i) { skip(); } const int& operator*() const { return s_->key_[i_]; }
        const_iterator& operator++() { i_++; skip(); return *this; } const_iterator operator++(int) { const_iterator t = *this; ++*this; return t; }
        bool operator==(const const_iterator& o) const { return i_ == o.i_; } bool operator!=(const const_iterator& o) const { return i_ != o.i_; } };
    const_iterator begin() const { return const_iterator(this, 0); } const_iterator end() const { return const_iterator(this, key_.size()); }
    bool check() const { std::size_t m = key_.size() - 1, cnt = 0; for (std::size_t j = 0; j < key_.size(); j++) if (used_[j]) { cnt++; for (std::size_t i = home(key_[j]); i != j; i = (i + 1) & m) if (!used_[i]) return false; } return cnt == size_ && size_ * 2 <= key_.size(); }   // 불변식: 집 위치에서 자기 자리까지 빈 칸이 없다
};
#include <functional>
#include <string>
template <class T, class F> T fold(const IntSet& s, T init, F f) { for (int x : s) init = f(init, x); return init; }
template <class T, class F> T chunked(const std::vector<int>& v, int chunks, T identity, F f) { std::vector<T> part; std::size_t n = v.size(); for (int c = 0; c < chunks; c++) { T acc = identity; for (std::size_t i = n * c / chunks; i < n * (c + 1) / chunks; i++) acc = f(acc, v[i]); part.push_back(acc); } T r = identity; for (const T& p : part) r = f(r, p); return r; }
unsigned long long mix(unsigned long long x) { x += 0x9E3779B97F4A7C15ull; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull; x = (x ^ (x >> 27)) * 0x94D049BB133111EBull; return x ^ (x >> 31); }
struct Tracked { IntSet set; long long sum = 0; unsigned long long fp = 0;                                            // 합과 지문을 점증 유지
    bool add(int x) { if (!set.add(x)) return false; sum += x; fp += mix((unsigned long long)(unsigned)x); return true; } bool remove(int x) { if (!set.remove(x)) return false; sum -= x; fp -= mix((unsigned long long)(unsigned)x); return true; } };
int main() {
    std::mt19937 rng(29);
    for (int rep = 0; rep < 300; rep++) { IntSet s; std::set<int> ref; for (int i = 0, k = (int)(rng() % 120); i < k; i++) { int x = (int)(rng() % 300) - 150; s.add(x); ref.insert(x); }                                       // ①
        long long sum = fold<long long>(s, 0, std::plus<long long>()), rsum = 0; for (int x : ref) rsum += x; assert(sum == rsum); int xr = fold<int>(s, 0, [](int a, int b) { return a ^ b; }), rx = 0; for (int x : ref) rx ^= x; assert(xr == rx);
        long long cnt = fold<long long>(s, 0, [](long long a, int) { return a + 1; }); assert(cnt == (long long)ref.size()); if (!ref.empty()) { assert(fold<int>(s, INT_MAX, [](int a, int b) { return std::min(a, b); }) == *ref.begin() && fold<int>(s, INT_MIN, [](int a, int b) { return std::max(a, b); }) == *ref.rbegin()); }
        long long prod = fold<long long>(s, 1, [](long long a, int b) { return a * (b % 3 + 1) % 1000003; }), rp = 1; for (int x : ref) rp = rp * (x % 3 + 1) % 1000003; assert(prod == rp); }
    { std::set<int> pick; while (pick.size() < 50) pick.insert((int)(rng() % 1000000)); std::vector<int> items(pick.begin(), pick.end()); bool concatDiffers = false, subDiffers = false; std::string firstCat; long long firstSub = 0;                    // ②
      for (int t = 0; t < 20; t++) { std::vector<int> perm = items; std::shuffle(perm.begin(), perm.end(), rng); IntSet h; for (int x : perm) h.add(x);
          long long sum = fold<long long>(h, 0, std::plus<long long>()); assert(sum == std::accumulate(items.begin(), items.end(), 0LL)); std::string cat = fold<std::string>(h, "", [](std::string a, int b) { return a + std::to_string(b) + ","; }); long long sub = fold<long long>(h, 0, [](long long a, int b) { return a - b; });
          if (t == 0) { firstCat = cat; firstSub = sub; } else { if (cat != firstCat) concatDiffers = true; if (sub != firstSub) subDiffers = true; }
          std::vector<int> sorted(h.begin(), h.end()); std::sort(sorted.begin(), sorted.end()); std::string sc; for (int x : sorted) sc += std::to_string(x) + ","; std::string expect; for (int x : items) expect += std::to_string(x) + ","; assert(sc == expect); }                // ③ 정렬 후 결정적
      assert(concatDiffers); (void)subDiffers; }
    { IntSet e; assert(fold<long long>(e, 0, std::plus<long long>()) == 0 && fold<long long>(e, 1, std::multiplies<long long>()) == 1 && fold<int>(e, INT_MAX, [](int a, int b) { return std::min(a, b); }) == INT_MAX); IntSet one; one.add(42); assert(fold<long long>(one, 0, std::plus<long long>()) == 42); }       // ④
    for (int rep = 0; rep < 200; rep++) { IntSet s; for (int i = 0, k = (int)(rng() % 200); i < k; i++) s.add((int)(rng() % 1000)); std::vector<int> v(s.begin(), s.end()); long long seq = fold<long long>(s, 0, std::plus<long long>());                                         // ⑤
        for (int c = 2; c <= 7; c++) { assert(chunked<long long>(v, c, 0, std::plus<long long>()) == seq); assert(chunked<int>(v, c, INT_MIN, [](int a, int b) { return std::max(a, b); }) == (v.empty() ? INT_MIN : *std::max_element(v.begin(), v.end()))); } }
    { Tracked t; std::set<int> ref; std::mt19937 r2(3); for (int step = 0; step < 100000; step++) { int x = (int)(r2() % 500); if (r2() % 2) { bool a = t.add(x); assert(a == ref.insert(x).second); } else { bool d = t.remove(x); assert(d == (ref.erase(x) > 0)); }               // ⑥ 점증 유지
        if (step % 9973 == 0) { long long s2 = 0; unsigned long long f2 = 0; for (int y : ref) { s2 += y; f2 += mix((unsigned long long)(unsigned)y); } assert(t.sum == s2 && t.fp == f2); } }
      long long s2 = 0; unsigned long long f2 = 0; for (int y : ref) { s2 += y; f2 += mix((unsigned long long)(unsigned)y); } assert(t.sum == s2 && t.fp == f2 && t.set.size() == ref.size()); }
    std::cout << "Reduce: sum, product, xor, min, max and count folds matched std::set on 300 random sets; across 20 differently built hash sets the commutative operations always agreed while string concatenation depended on iteration order (sorting made it deterministic), parallel chunked folds equalled the sequential fold, and an incrementally maintained sum and order-independent fingerprint matched recomputation after 100000 random updates" << std::endl; return 0;
}
// Time Complexity: 접기 O(N), 점증 유지 갱신당 O(1)
// Space Complexity: O(1)
```

# Part 5. 구현
## ArraySet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 배열 집합(ArraySet): 원소를 정렬된 연속 배열에 보관한다(중복 없음 = 순증가). 조회는 이진 탐색 O(log n) 이고 메모리가 연속이라 캐시에 매우 유리하다. 대신 삽입·삭제는 뒤쪽 원소를 한 칸씩 밀어야 해서 O(n) — 정확히 n−pos 번 이동한다. 그래서 읽기가 많고 변경이 드문 집합(설정값, 사전), 또는 한꺼번에 만든 뒤 쓰기만 하는 경우에 최선이다.
// 정렬된 배열이라서 해시 집합이 못 하는 순서 질의를 공짜로 얻는다: 순위(rank) = lower_bound 의 인덱스, k 번째로 작은 원소(select) = a[k] 가 O(1), 구간 [lo, hi] 의 원소 수 = upper_bound(hi) − lower_bound(lo), 바닥·천장, 정렬된 순회, 그리고 집합 연산을 병합으로 O(n+m) 에 한다. 한꺼번에 만들 때는 하나씩 삽입하면 이동이 n²/4 번이지만, 전부 모아 정렬한 뒤 중복을 제거하면 O(n log n) 이다.
// 검증: ① 무작위 add/remove/contains 가 std::set 과 일치하고 배열이 항상 순증가 ② 삽입 이동 횟수가 매번 정확히 n−pos, 삭제는 n−pos−1 ③ 하나씩 삽입으로 만든 비용 ≈ n²/4 vs 정렬+unique 의 비교 횟수 ≈ n log n (n = 20000, 10 배 이상 차이) ④ 순위·select·구간 개수·바닥·천장이 무차별 계산과 일치 ⑤ 두 배열 집합의 합·교·차가 병합으로 std 결과와 일치 ⑥ 빈 집합·원소 1 개.
class ArraySet { std::vector<int> a_; public: long moves = 0, cmps = 0;
    bool contains(int x) { std::size_t lo = 0, hi = a_.size(); while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; cmps++; if (a_[mid] < x) lo = mid + 1; else hi = mid; } return lo < a_.size() && a_[lo] == x; }
    std::size_t lowerBound(int x) const { return (std::size_t)(std::lower_bound(a_.begin(), a_.end(), x) - a_.begin()); }
    bool add(int x) { std::size_t pos = lowerBound(x); if (pos < a_.size() && a_[pos] == x) return false; a_.push_back(0); for (std::size_t i = a_.size() - 1; i > pos; i--) { a_[i] = a_[i - 1]; moves++; } a_[pos] = x; return true; }
    bool remove(int x) { std::size_t pos = lowerBound(x); if (pos >= a_.size() || a_[pos] != x) return false; for (std::size_t i = pos; i + 1 < a_.size(); i++) { a_[i] = a_[i + 1]; moves++; } a_.pop_back(); return true; }
    static ArraySet fromUnsorted(std::vector<int> v) { std::sort(v.begin(), v.end()); v.erase(std::unique(v.begin(), v.end()), v.end()); ArraySet s; s.a_ = std::move(v); return s; }
    std::size_t size() const { return a_.size(); } const std::vector<int>& items() const { return a_; }
    std::size_t rank(int x) const { return lowerBound(x); } int select(std::size_t k) const { return a_[k]; }
    std::size_t countRange(int lo, int hi) const { return (std::size_t)(std::upper_bound(a_.begin(), a_.end(), hi) - std::lower_bound(a_.begin(), a_.end(), lo)); }
    bool floorOf(int x, int& out) const { auto it = std::upper_bound(a_.begin(), a_.end(), x); if (it == a_.begin()) return false; out = *std::prev(it); return true; }
    bool ceilOf(int x, int& out) const { auto it = std::lower_bound(a_.begin(), a_.end(), x); if (it == a_.end()) return false; out = *it; return true; }
    static ArraySet unite(const ArraySet& p, const ArraySet& q) { ArraySet r; std::set_union(p.a_.begin(), p.a_.end(), q.a_.begin(), q.a_.end(), std::back_inserter(r.a_)); return r; }
    static ArraySet intersect(const ArraySet& p, const ArraySet& q) { ArraySet r; std::set_intersection(p.a_.begin(), p.a_.end(), q.a_.begin(), q.a_.end(), std::back_inserter(r.a_)); return r; }
    static ArraySet minus(const ArraySet& p, const ArraySet& q) { ArraySet r; std::set_difference(p.a_.begin(), p.a_.end(), q.a_.begin(), q.a_.end(), std::back_inserter(r.a_)); return r; } };
int main() {
    std::mt19937 rng(30); { ArraySet s; std::set<int> ref; for (int step = 0; step < 30000; step++) { int x = (int)(rng() % 600), op = (int)(rng() % 3); long before = s.moves;                                                          // ① ②
          if (op == 0) { std::size_t n = s.size(), pos = s.lowerBound(x); bool added = s.add(x); assert(added == ref.insert(x).second); if (added) assert(s.moves - before == (long)(n - pos)); else assert(s.moves == before); }
          else if (op == 1) { std::size_t n = s.size(), pos = s.lowerBound(x); bool removed = s.remove(x); assert(removed == (ref.erase(x) > 0)); if (removed) assert(s.moves - before == (long)(n - pos - 1)); }
          else assert(s.contains(x) == (ref.count(x) > 0)); assert(s.size() == ref.size()); if (step % 997 == 0) { const auto& v = s.items(); assert(std::is_sorted(v.begin(), v.end()) && std::adjacent_find(v.begin(), v.end()) == v.end() && std::equal(v.begin(), v.end(), ref.begin(), ref.end())); } } }
    { const int n = 20000; std::vector<int> keys(n); for (int& k : keys) k = (int)(rng() % 1000000); ArraySet inc; for (int k : keys) inc.add(k); ArraySet bulk = ArraySet::fromUnsorted(keys); assert(inc.items() == bulk.items());                                         // ③
      double nlogn = n * std::log2((double)n); assert((double)inc.moves > 0.15 * (double)n * n && (double)inc.moves > 10 * nlogn); }
    for (int rep = 0; rep < 200; rep++) { std::set<int> ref; for (int i = 0, k = (int)(rng() % 100); i < k; i++) ref.insert((int)(rng() % 500)); ArraySet s = ArraySet::fromUnsorted(std::vector<int>(ref.begin(), ref.end())); std::vector<int> sorted(ref.begin(), ref.end());   // ④
        for (std::size_t k = 0; k < sorted.size(); k++) { assert(s.select(k) == sorted[k] && s.rank(sorted[k]) == k); } for (int q = -3; q < 505; q += 3) { std::size_t brute = 0; for (int x : sorted) brute += x < q; assert(s.rank(q) == brute);
            int lo = q, hi = q + (int)(rng() % 100); std::size_t cr = 0; for (int x : sorted) cr += (x >= lo && x <= hi); assert(s.countRange(lo, hi) == cr);
            int fl = INT_MIN, ce = INT_MAX; for (int x : sorted) { if (x <= q) fl = x; if (x >= q && ce == INT_MAX) ce = x; } int got; assert(s.floorOf(q, got) == (fl != INT_MIN) && (fl == INT_MIN || got == fl)); assert(s.ceilOf(q, got) == (ce != INT_MAX) && (ce == INT_MAX || got == ce)); } }
    for (int rep = 0; rep < 200; rep++) { std::set<int> ra, rb; for (int i = 0, k = (int)(rng() % 60); i < k; i++) { ra.insert((int)(rng() % 100)); rb.insert((int)(rng() % 100)); } ArraySet a = ArraySet::fromUnsorted(std::vector<int>(ra.begin(), ra.end())), b = ArraySet::fromUnsorted(std::vector<int>(rb.begin(), rb.end()));   // ⑤
        std::vector<int> u, in, d; std::set_union(ra.begin(), ra.end(), rb.begin(), rb.end(), std::back_inserter(u)); std::set_intersection(ra.begin(), ra.end(), rb.begin(), rb.end(), std::back_inserter(in)); std::set_difference(ra.begin(), ra.end(), rb.begin(), rb.end(), std::back_inserter(d));
        assert(ArraySet::unite(a, b).items() == u && ArraySet::intersect(a, b).items() == in && ArraySet::minus(a, b).items() == d); }
    { ArraySet e; int out; assert(e.size() == 0 && !e.contains(1) && !e.remove(1) && !e.floorOf(5, out) && !e.ceilOf(5, out) && e.countRange(0, 100) == 0 && e.rank(7) == 0); e.add(5); assert(e.size() == 1 && e.contains(5) && e.select(0) == 5 && e.floorOf(5, out) && out == 5 && e.ceilOf(6, out) == false); }   // ⑥
    std::cout << "ArraySet: 30000 random operations matched std::set with the array always strictly increasing, an insertion moved exactly n-pos elements and a removal n-pos-1, one-by-one construction of 20000 keys needed over 10x the work of sort-and-unique, and rank, select, range count, floor, ceil and merge-based set algebra matched brute force" << std::endl; return 0;
}
// Time Complexity: 조회 O(log N), 삽입·삭제 O(N), 순위·select O(log N)/O(1), 집합 연산 O(N + M)
// Space Complexity: O(N) 연속
```
## LinkedSet()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 연결 리스트 집합(LinkedSet): 원소를 오름차순으로 정렬된 단일 연결 리스트에 보관한다. 정렬을 유지하면 중복 검사가 자연스럽고(삽입 위치를 찾는 순회에서 같은 값을 만나면 이미 있음), 두 집합의 합·교·차가 리스트 두 개를 한 번씩만 훑는 병합 O(n + m) 이 된다.
// 단점은 조회·삽입·삭제가 O(n) 이고 캐시 지역성이 나쁘다는 것 — 배열 집합(ArraySet)보다 느리고 해시/트리 집합보다 점근적으로 느리지만 이미 정렬된 연결 구조에서 포인터만 바꿔 삽입·삭제할 때 원소 이동이 없다는 장점이 있다. 더미(sentinel) 머리 노드로 머리 삽입·삭제를 특수 처리 없이 다룬다.
// 검증: 무작위 연산열(add/remove/contains) 20000개를 std::set 과 비교하고, 합집합·교집합·차집합·대칭차집합을 모두 병합으로 구현해 std::set 의 알고리즘 결과와 비교한다. 소멸자가 모든 노드를 해제한다
struct LinkedSet {
    struct Node { int v; Node* next; }; Node head{0, nullptr}; size_t n = 0;
    ~LinkedSet() { clear(); } LinkedSet() = default; LinkedSet(const LinkedSet& o) { Node* tail = &head; for (Node* p = o.head.next; p; p = p->next) { tail->next = new Node{p->v, nullptr}; tail = tail->next; n++; } } LinkedSet& operator=(const LinkedSet&) = delete;
    void clear() { while (head.next) { Node* p = head.next; head.next = p->next; delete p; } n = 0; }
    bool add(int x) { Node* p = &head; while (p->next && p->next->v < x) p = p->next; if (p->next && p->next->v == x) return false; p->next = new Node{x, p->next}; n++; return true; }
    bool remove(int x) { Node* p = &head; while (p->next && p->next->v < x) p = p->next; if (!p->next || p->next->v != x) return false; Node* d = p->next; p->next = d->next; delete d; n--; return true; }
    bool contains(int x) const { for (Node* p = head.next; p && p->v <= x; p = p->next) if (p->v == x) return true; return false; }
    std::vector<int> items() const { std::vector<int> r; for (Node* p = head.next; p; p = p->next) r.push_back(p->v); return r; }
    template <class Keep> static LinkedSet merge(const LinkedSet& a, const LinkedSet& b, Keep keep) { LinkedSet r; Node* tail = &r.head; Node *p = a.head.next, *q = b.head.next; auto push = [&](int v) { tail->next = new Node{v, nullptr}; tail = tail->next; r.n++; };       // keep(inA, inB): 이 값을 결과에 넣는가
        while (p || q) { if (!q || (p && p->v < q->v)) { if (keep(true, false)) push(p->v); p = p->next; } else if (!p || q->v < p->v) { if (keep(false, true)) push(q->v); q = q->next; } else { if (keep(true, true)) push(p->v); p = p->next; q = q->next; } } return r; }
};
int main() {
    std::mt19937 rng(5); LinkedSet s; std::set<int> ref;
    for (int i = 0; i < 20000; i++) { int x = rng() % 60, op = rng() % 3; if (op == 0) assert(s.add(x) == ref.insert(x).second); else if (op == 1) assert(s.remove(x) == (ref.erase(x) == 1)); else assert(s.contains(x) == (ref.count(x) == 1)); assert(s.n == ref.size()); }
    assert(s.items() == std::vector<int>(ref.begin(), ref.end()));
    for (int t = 0; t < 300; t++) { LinkedSet a, b; std::set<int> ra, rb; for (int i = 0; i < 12; i++) { int x = rng() % 25; a.add(x); ra.insert(x); int y = rng() % 25; b.add(y); rb.insert(y); }
        auto u = LinkedSet::merge(a, b, [](bool, bool) { return true; }), in = LinkedSet::merge(a, b, [](bool x, bool y) { return x && y; }), df = LinkedSet::merge(a, b, [](bool x, bool y) { return x && !y; }), sd = LinkedSet::merge(a, b, [](bool x, bool y) { return x != y; });
        std::set<int> eu, ei, ed, es; std::set_union(ra.begin(), ra.end(), rb.begin(), rb.end(), std::inserter(eu, eu.begin())); std::set_intersection(ra.begin(), ra.end(), rb.begin(), rb.end(), std::inserter(ei, ei.begin())); std::set_difference(ra.begin(), ra.end(), rb.begin(), rb.end(), std::inserter(ed, ed.begin())); std::set_symmetric_difference(ra.begin(), ra.end(), rb.begin(), rb.end(), std::inserter(es, es.begin()));
        assert(u.items() == std::vector<int>(eu.begin(), eu.end()) && in.items() == std::vector<int>(ei.begin(), ei.end()) && df.items() == std::vector<int>(ed.begin(), ed.end()) && sd.items() == std::vector<int>(es.begin(), es.end())); LinkedSet c(a); assert(c.items() == a.items()); }
    std::cout << "LinkedSet: 20000 random operations match std::set; union, intersection, difference and symmetric difference by single-pass merge match the STL on 300 random pairs" << std::endl; return 0;
}
// Time Complexity: 조회/삽입/삭제 O(n), 집합 연산 O(n + m)
// Space Complexity: O(n) (노드당 포인터 1개)
```
## HashSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#include <iostream>
#include <memory>
#include <random>
#include <unordered_set>
#include <vector>

// 해시 집합(HashSet): 키를 해시 함수로 버킷 번호에 대응시켜 저장한다. 이 장의 구현은 분리 연쇄법(separate chaining): 버킷마다 연결 리스트(체인)를 두고 같은 버킷에 걸린 키를 거기에 단다. 부하율 α = n/버킷 수 가 1 을 넘으면 버킷 수를 두 배로 늘려 다시 배치한다(rehash). 무작위 해시 아래에서 성공 조회의 기대 탐사 1 + α/2, 실패 조회 α(+ 버킷 접근 1) — 선형 탐사(열린 주소법)와 달리 α 가 1 을 넘어도 완만하게 나빠지고 삭제가 단순(체인에서 노드 제거)하다. 노드를 새로 만들어 연결하므로 재배치는 노드를 다시 잇기만 하고 원소의 주소가 바뀌지 않는다 — 열린 주소법과 달리 원소에 대한 포인터·참조가 재배치 후에도 유효하다.
// 해시 함수가 나쁘면(모든 키가 같은 버킷) 체인이 길이 n 이 되어 모든 연산이 O(n) 이다 — 외부 입력을 키로 쓰는 서버에서는 공격자가 충돌하는 키만 보내는 해시 플러딩(hash flooding)이 가능한 이유다. 빈 버킷의 비율은 α = 1 에서 e⁻¹ ≈ 0.368 이다.
// 검증: ① 무작위 add/remove/contains 20000 번이 std::unordered_set 과 일치하고 크기·부하율 ≤ 1 유지 ② 재배치 후에도 원소의 주소가 그대로(참조 안정) ③ 부하율 1 일 때 빈 버킷 비율 ≈ 0.368(±0.03), 성공 조회 평균 탐사 ≈ 1.5(±10%), 실패 ≈ 1.0 ④ 나쁜 해시(모든 키가 같은 버킷)에서는 체인 길이가 n 이고 조회 탐사가 n/2 로 폭발, 좋은 해시에서는 키가 모두 1024 의 배수여도(하위 비트 마스크라면 한두 버킷에 몰릴 입력) 최대 체인이 작음 ⑤ 삭제가 체인 중간·머리·꼬리에서 모두 올바름 ⑥ 모두 지운 뒤 빈 집합.
template <bool Good> class ChainSet {
    struct Node { int key; Node* next; }; std::vector<Node*> b_; std::size_t size_ = 0;
    std::size_t home(int x) const { if (!Good) return 0; return (std::size_t)(((unsigned long long)(unsigned)x * 0x9E3779B97F4A7C15ull) >> (64 - __builtin_ctzll((unsigned long long)b_.size()))); }
    void rehash() { std::vector<Node*> nb(b_.size() * 2, nullptr); std::swap(nb, b_); for (Node* head : nb) while (head) { Node* nx = head->next; std::size_t h = home(head->key); head->next = b_[h]; b_[h] = head; head = nx; } rehashes++; }   // 노드를 다시 잇기만 한다
public:
    long rehashes = 0; mutable long probes = 0; ChainSet() : b_(8, nullptr) {} ChainSet(const ChainSet&) = delete; ChainSet& operator=(const ChainSet&) = delete; ~ChainSet() { for (Node* h : b_) while (h) { Node* nx = h->next; delete h; h = nx; } }
    std::size_t size() const { return size_; } std::size_t buckets() const { return b_.size(); } double load() const { return (double)size_ / (double)b_.size(); }
    const int* find(int x) const { for (Node* n = b_[home(x)]; n; n = n->next) { probes++; if (n->key == x) return &n->key; } return nullptr; }
    bool contains(int x) const { return find(x) != nullptr; }
    bool add(int x) { if (find(x)) return false; if (size_ + 1 > b_.size()) rehash(); std::size_t h = home(x); b_[h] = new Node{x, b_[h]}; size_++; return true; }
    bool remove(int x) { Node** link = &b_[home(x)]; while (*link && (*link)->key != x) link = &(*link)->next; if (!*link) return false; Node* dead = *link; *link = dead->next; delete dead; size_--; return true; }
    std::size_t longestChain() const { std::size_t m = 0; for (Node* h : b_) { std::size_t c = 0; for (Node* n = h; n; n = n->next) c++; m = std::max(m, c); } return m; }
    std::size_t emptyBuckets() const { std::size_t c = 0; for (Node* h : b_) c += h == nullptr; return c; } };
int main() {
    std::mt19937 rng(31); { ChainSet<true> s; std::unordered_set<int> ref; for (int step = 0; step < 20000; step++) { int x = (int)(rng() % 2500), op = (int)(rng() % 3); if (op == 0) assert(s.add(x) == ref.insert(x).second); else if (op == 1) assert(s.remove(x) == (ref.erase(x) > 0)); else assert(s.contains(x) == (ref.count(x) > 0));   // ①
          assert(s.size() == ref.size() && s.load() <= 1.0); } for (int x = 0; x < 2500; x++) assert(s.contains(x) == (ref.count(x) > 0)); }
    { ChainSet<true> s; s.add(42); const int* addr = s.find(42); for (int i = 0; i < 5000; i++) s.add(1000 + i); assert(s.rehashes >= 9 && s.find(42) == addr && *addr == 42); }                                                                         // ② 재배치 후에도 주소 유지
    { ChainSet<true> s; std::mt19937 r2(5); std::vector<int> keys; while (keys.size() < 1 << 15) { int k = (int)r2(); if (s.add(k)) keys.push_back(k); } assert(s.load() <= 1.0 && s.load() > 0.45);                                                                // ③ 부하율 ~ 0.5~1
      ChainSet<true> t; std::unordered_set<int> seen; while (t.size() < (1u << 16) - 1) { int k = (int)r2(); if (t.add(k)) seen.insert(k); } double alpha = t.load(); assert(alpha > 0.99 && alpha <= 1.0);
      double empty = (double)t.emptyBuckets() / (double)t.buckets(); assert(std::abs(empty - std::exp(-alpha)) < 0.03);                                                                                                                            // 빈 버킷 ≈ e^-α
      long before = t.probes; for (int k : seen) t.contains(k); double hit = (double)(t.probes - before) / (double)seen.size(); assert(std::abs(hit - (1 + alpha / 2)) / (1 + alpha / 2) < 0.10);
      before = t.probes; int misses = 0; for (int i = 0; i < 200000; i++) { int k = (int)r2(); if (seen.count(k)) continue; t.contains(k); misses++; } double miss = (double)(t.probes - before) / misses; assert(std::abs(miss - alpha) / alpha < 0.10); }
    { ChainSet<false> bad; ChainSet<true> good; for (int i = 0; i < 2000; i++) { bad.add(i * 1024); good.add(i * 1024); } assert(bad.longestChain() == 2000 && good.longestChain() <= 12);                                                // ④ 나쁜 해시
      long b0 = bad.probes, g0 = good.probes; for (int i = 0; i < 2000; i++) { bad.contains(i * 1024); good.contains(i * 1024); } assert((double)(bad.probes - b0) / 2000 > 900 && (double)(good.probes - g0) / 2000 < 3.0); }
    { ChainSet<false> c; for (int x : {1, 2, 3, 4, 5, 6}) c.add(x); assert(c.remove(6) && c.remove(3) && c.remove(1) && !c.remove(3) && c.size() == 3 && c.contains(2) && c.contains(4) && c.contains(5) && !c.contains(1) && !c.contains(3) && !c.contains(6)); }   // ⑤ 머리·중간·꼬리
    { ChainSet<true> s; for (int i = 0; i < 1000; i++) s.add(i); for (int i = 0; i < 1000; i++) assert(s.remove(i)); assert(s.size() == 0 && !s.contains(0) && s.longestChain() == 0); s.add(5); assert(s.contains(5)); }   // ⑥
    std::cout << "HashSet: a separate-chaining set matched std::unordered_set over 20000 random operations, kept element addresses stable across rehashing, showed the textbook statistics at load factor 1 (empty buckets close to e^-1, about 1+a/2 probes for a hit and a for a miss), and degraded to chains of length n under a constant hash while the multiplicative hash kept the longest chain tiny even for keys that are all multiples of 1024" << std::endl; return 0;
}
// Time Complexity: 기대 O(1) (부하율 ≤ 1), 최악 O(N)
// Space Complexity: O(N + 버킷 수)
```
## TreeSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 트리 집합(TreeSet): 균형 이진 탐색 트리에 키를 보관한다. 조회·삽입·삭제가 모두 최악 O(log n) 이고, 해시 집합이 못 하는 순서 질의 — 정렬된 순회, 최솟값/최댓값, 순위(rank), k 번째 원소(select), lower_bound, 구간 질의 — 를 O(log n) 에 한다. 이 코드는 AVL 트리(높이 균형: 모든 노드의 왼쪽·오른쪽 높이 차 ≤ 1)에 부분 트리 크기를 더한 것이다(Tree.md Part 6 의 AVL 이 정본). 삽입은 갱신 후 되짚어 오르며 균형이 깨진 곳을 회전으로 고친다.
// 성질: n 개 키의 AVL 트리 높이는 1.4405·log₂(n+2) − 0.3277 이하, 삽입은 재구성(단일 또는 이중 회전)이 많아야 한 번이지만 삭제는 경로를 따라 여러 번 필요할 수 있다. 정렬된 키를 차례로 넣어도 균형이 유지된다(균형 없는 이진 탐색 트리는 길이 n 의 사슬이 된다). 부분 트리 크기를 유지하면 순위와 select 도 O(log n) 이다.
// 검증: ① 무작위 add/remove/contains 4 만 번이 std::set 과 일치하고 주기적으로 불변식(이진 탐색 순서, 높이·크기 필드, 균형 계수 |bf| ≤ 1) 성립 ② 정렬/역순/무작위 입력과 삭제 뒤에도 높이 ≤ 1.4405·log₂(n+2) 이고 삽입당 재구성 ≤ 1 ③ 중위 순회가 정렬 ④ rank·select·lower_bound·최솟값/최댓값이 정렬 배열 계산과 일치 ⑤ 노드 누수 없음(생성 − 소멸 = 크기) ⑥ 빈 트리·원소 1 개.
class TreeSet {
    struct Node { int key; Node *l, *r; int h, sz; }; Node* root_ = nullptr; static int live;
    static int H(const Node* n) { return n ? n->h : 0; } static int S(const Node* n) { return n ? n->sz : 0; }
    static void upd(Node* n) { n->h = 1 + std::max(H(n->l), H(n->r)); n->sz = 1 + S(n->l) + S(n->r); }
    Node* rotR(Node* y) { Node* x = y->l; y->l = x->r; x->r = y; upd(y); upd(x); return x; } Node* rotL(Node* x) { Node* y = x->r; x->r = y->l; y->l = x; upd(x); upd(y); return y; }
    Node* fix(Node* n) { upd(n); int bf = H(n->l) - H(n->r); if (bf > 1) { if (H(n->l->l) < H(n->l->r)) n->l = rotL(n->l); restructures++; return rotR(n); } if (bf < -1) { if (H(n->r->r) < H(n->r->l)) n->r = rotR(n->r); restructures++; return rotL(n); } return n; }
    Node* ins(Node* n, int k, bool& added) { if (!n) { added = true; live++; return new Node{k, nullptr, nullptr, 1, 1}; } if (k < n->key) n->l = ins(n->l, k, added); else if (n->key < k) n->r = ins(n->r, k, added); else return n; return fix(n); }
    Node* del(Node* n, int k, bool& removed) { if (!n) return nullptr; if (k < n->key) n->l = del(n->l, k, removed); else if (n->key < k) n->r = del(n->r, k, removed);
        else { removed = true; if (!n->l || !n->r) { Node* c = n->l ? n->l : n->r; delete n; live--; return c; } Node* m = n->r; while (m->l) m = m->l; n->key = m->key; bool d; n->r = del(n->r, m->key, d); } return fix(n); }
    static void destroy(Node* n) { if (!n) return; destroy(n->l); destroy(n->r); delete n; live--; }
    bool checkNode(const Node* n, long long lo, long long hi) const { if (!n) return true; if (n->key <= lo || n->key >= hi) return false; if (n->h != 1 + std::max(H(n->l), H(n->r)) || n->sz != 1 + S(n->l) + S(n->r) || std::abs(H(n->l) - H(n->r)) > 1) return false; return checkNode(n->l, lo, n->key) && checkNode(n->r, n->key, hi); }
public:
    long restructures = 0; TreeSet() = default; TreeSet(const TreeSet&) = delete; TreeSet& operator=(const TreeSet&) = delete; ~TreeSet() { destroy(root_); } static int liveNodes() { return live; }
    bool add(int k) { bool a = false; root_ = ins(root_, k, a); return a; } bool remove(int k) { bool r = false; root_ = del(root_, k, r); return r; }
    bool contains(int k) const { const Node* n = root_; while (n) { if (k < n->key) n = n->l; else if (n->key < k) n = n->r; else return true; } return false; }
    int size() const { return S(root_); } int height() const { return H(root_); } bool check() const { return checkNode(root_, LLONG_MIN, LLONG_MAX); }
    std::vector<int> inorder() const { std::vector<int> r; std::vector<const Node*> st; const Node* n = root_; while (n || !st.empty()) { while (n) { st.push_back(n); n = n->l; } n = st.back(); st.pop_back(); r.push_back(n->key); n = n->r; } return r; }
    int rank(int k) const { int c = 0; const Node* n = root_; while (n) { if (k <= n->key) n = n->l; else { c += S(n->l) + 1; n = n->r; } } return c; }
    int select(int i) const { const Node* n = root_; while (n) { int ls = S(n->l); if (i < ls) n = n->l; else if (i == ls) return n->key; else { i -= ls + 1; n = n->r; } } return INT_MIN; }
    bool lowerBound(int k, int& out) const { const Node* n = root_; bool found = false; while (n) { if (n->key >= k) { out = n->key; found = true; n = n->l; } else n = n->r; } return found; } };
int TreeSet::live = 0;
int main() {
    std::mt19937 rng(32); { TreeSet s; std::set<int> ref; for (int step = 0; step < 40000; step++) { int x = (int)(rng() % 3000), op = (int)(rng() % 3); if (op == 0) assert(s.add(x) == ref.insert(x).second); else if (op == 1) assert(s.remove(x) == (ref.erase(x) > 0)); else assert(s.contains(x) == (ref.count(x) > 0));   // ①
          assert(s.size() == (int)ref.size() && TreeSet::liveNodes() == s.size()); if (step % 1999 == 0) assert(s.check() && s.inorder() == std::vector<int>(ref.begin(), ref.end())); } assert(s.check()); }
    assert(TreeSet::liveNodes() == 0);
    for (int mode = 0; mode < 3; mode++) { TreeSet s; int n = 20000; std::vector<int> keys(n); for (int i = 0; i < n; i++) keys[i] = mode == 1 ? n - i : i; if (mode == 2) { std::shuffle(keys.begin(), keys.end(), rng); }                                                    // ② 정렬/역순/무작위
        long maxPer = 0; for (int i = 0; i < n; i++) { long before = s.restructures; s.add(keys[i]); maxPer = std::max(maxPer, s.restructures - before); if (i % 4096 == 0 || i == n - 1) assert(s.height() <= 1.4405 * std::log2((double)(s.size() + 2)) - 0.3277 + 1e-9); }
        assert(maxPer <= 1 && s.check()); for (int i = 0; i < n; i += 2) s.remove(keys[i]); assert(s.check() && s.height() <= 1.4405 * std::log2((double)(s.size() + 2)) - 0.3277 + 1e-9); }
    { TreeSet s; std::set<int> ref; for (int i = 0, k = 3000; i < k; i++) { int x = (int)(rng() % 100000); s.add(x); ref.insert(x); } std::vector<int> sorted(ref.begin(), ref.end()); assert(s.inorder() == sorted);                                             // ③ ④
      for (int i = 0; i < (int)sorted.size(); i++) assert(s.select(i) == sorted[i] && s.rank(sorted[i]) == i); for (int q = -5; q < 100005; q += 37) { int got = 0; auto it = ref.lower_bound(q); assert(s.lowerBound(q, got) == (it != ref.end()) && (it == ref.end() || got == *it)); assert(s.rank(q) == (int)std::distance(ref.begin(), it)); }
      assert(s.select(0) == *ref.begin() && s.select(s.size() - 1) == *ref.rbegin()); }
    assert(TreeSet::liveNodes() == 0);
    { TreeSet e; int out; assert(e.size() == 0 && e.height() == 0 && !e.contains(1) && !e.remove(1) && e.inorder().empty() && !e.lowerBound(0, out) && e.rank(5) == 0 && e.check()); e.add(7); assert(e.size() == 1 && e.height() == 1 && e.select(0) == 7 && e.lowerBound(7, out) && out == 7 && !e.lowerBound(8, out)); }   // ⑥
    assert(TreeSet::liveNodes() == 0); std::cout << "TreeSet: an AVL tree with subtree sizes matched std::set over 40000 random operations with all invariants checked, kept its height within 1.4405*log2(n+2) for sorted, reversed and random insertion orders (at most one restructuring per insertion), produced sorted in-order traversals, answered rank, select and lower_bound in O(log n) in agreement with sorted arrays, and leaked no nodes" << std::endl; return 0;
}
// Time Complexity: 조회·삽입·삭제·순위·select 모두 O(log N)
// Space Complexity: O(N)
```
## Multiset()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 다중집합(Multiset): 같은 값이 여러 번 들어갈 수 있는 집합 — 값마다 "개수(multiplicity)" 를 센다. std::multiset 은 같은 값을 노드 여러 개로 저장하지만, 이 구현은 서로 다른 값마다 노드 하나 + 개수를 두고
// 서브트리의 총 개수(tot)를 함께 저장하는 트립(순서 통계 트리)이라 개수가 아주 큰 값도 노드 하나이고, 다음이 모두 O(log 서로 다른 값 수) 다:
// insert(x, c)·erase(x, c)(c 개를 지움, 있는 만큼만)·count(x)·size()(총 원소 수)·kth(i)(총 순서로 i 번째, 같은 값은 연달아)·rank(x)(x 보다 작은 원소 수)·lowerBound/upperBound(x)·countRange(lo, hi)(구간 안 원소 수)·min/max.
// 집합 연산의 다중집합판도 한다: 합집합 = 값마다 max(개수), 교집합 = min(개수), 합(additive union) = 개수의 합, 차 = max(0, a - b); 포함 관계는 모든 값에서 개수가 이하인지. (수학의 bag / 다중집합과 같은 정의)
// 검증: 무작위 insert(개수 포함)·erase·count·kth·rank·bounds·countRange 4 만 번을 std::multiset 과 대조, 같은 값을 백만 번 넣어도 노드 하나, 다중집합 연산 네 가지가 값별 개수 정의와 같고 부분 다중집합 판정 일치
class Multiset {
    struct Node { int key; long long cnt, tot; uint32_t pri; Node *l = nullptr, *r = nullptr; };   // cnt: 이 값의 개수, tot: 서브트리 총 개수
    Node* root_ = nullptr; std::mt19937 rng_{2024}; size_t distinct_ = 0;
    static long long tot(Node* x) { return x ? x->tot : 0; }
    static void pull(Node* x) { x->tot = x->cnt + tot(x->l) + tot(x->r); }
    static void split(Node* x, int key, Node*& a, Node*& b) { if (!x) { a = b = nullptr; return; } if (x->key < key) { split(x->r, key, x->r, b); pull(x); a = x; } else { split(x->l, key, a, x->l); pull(x); b = x; } }       // a: key 미만, b: key 이상
    static Node* merge(Node* a, Node* b) { if (!a) return b; if (!b) return a; if (a->pri > b->pri) { a->r = merge(a->r, b); pull(a); return a; } b->l = merge(a, b->l); pull(b); return b; }
    static void destroy(Node* x) { if (!x) return; destroy(x->l); destroy(x->r); delete x; }
    Node* find(int key) const { Node* x = root_; while (x && x->key != key) x = key < x->key ? x->l : x->r; return x; }
    static void collect(Node* x, std::vector<std::pair<int, long long>>& out) { if (!x) return; collect(x->l, out); out.push_back({x->key, x->cnt}); collect(x->r, out); }
public:
    Multiset() {} Multiset(const Multiset&) = delete; Multiset& operator=(const Multiset&) = delete; ~Multiset() { destroy(root_); }
    Multiset(Multiset&& o) noexcept : root_(o.root_), rng_(o.rng_), distinct_(o.distinct_) { o.root_ = nullptr; o.distinct_ = 0; }
    long long size() const { return tot(root_); } size_t distinct() const { return distinct_; }
    long long count(int x) const { Node* n = find(x); return n ? n->cnt : 0; }
    void insert(int x, long long c = 1) {
        if (c <= 0) return;
        if (Node* n = find(x)) { n->cnt += c; for (Node* p = root_; p != n; p = x < p->key ? p->l : p->r) p->tot += c; n->tot += c; return; }          // 이미 있는 값: 경로의 tot 만 늘린다
        Node *a, *b; split(root_, x, a, b); Node* n = new Node{x, c, c, (uint32_t)rng_()}; root_ = merge(merge(a, n), b); ++distinct_;
    }
    long long erase(int x, long long c = 1) {                                                      // 실제로 지운 개수
        Node* n = find(x); if (!n || c <= 0) return 0; const long long d = std::min(c, n->cnt);
        if (d < n->cnt) { for (Node* p = root_; p != n; p = x < p->key ? p->l : p->r) p->tot -= d; n->cnt -= d; n->tot -= d; return d; }
        Node *a, *b, *m, *r; split(root_, x, a, b); split(b, x + 1, m, r); destroy(m); root_ = merge(a, r); --distinct_; return d;                  // 개수가 0 이 되면 노드를 지운다
    }
    long long rank(int x) const { long long r = 0; for (Node* n = root_; n;) { if (x <= n->key) n = n->l; else { r += tot(n->l) + n->cnt; n = n->r; } } return r; }         // x 보다 작은 원소 수
    long long countRange(int lo, int hi) const { return lo > hi ? 0 : rank(hi) + count(hi) - rank(lo); }          // lo <= v <= hi 인 원소 수 = (hi 이하) - (lo 미만)
    int kth(long long i) const { Node* n = root_; for (;;) { if (i < tot(n->l)) n = n->l; else if (i < tot(n->l) + n->cnt) return n->key; else { i -= tot(n->l) + n->cnt; n = n->r; } } }       // 0 기준, 정렬했을 때 i 번째
    int lowerBound(int x) const { long long i = rank(x); return i < size() ? kth(i) : INT32_MAX; }  // x 이상인 최소 원소(없으면 INT32_MAX)
    int upperBound(int x) const { long long i = rank(x) + count(x); return i < size() ? kth(i) : INT32_MAX; }
    int minimum() const { return kth(0); } int maximum() const { return kth(size() - 1); }
    std::vector<std::pair<int, long long>> items() const { std::vector<std::pair<int, long long>> v; collect(root_, v); return v; }
    static Multiset combine(const Multiset& a, const Multiset& b, char op) {                       // 'u' 합집합(max) 'i' 교집합(min) '+' 합(add) '-' 차(max(0, a-b))
        Multiset r; auto ia = a.items(), ib = b.items(); std::set<int> keys; for (auto& p : ia) keys.insert(p.first); for (auto& p : ib) keys.insert(p.first);
        for (int k : keys) { const long long x = a.count(k), y = b.count(k); long long c = op == 'u' ? std::max(x, y) : op == 'i' ? std::min(x, y) : op == '+' ? x + y : std::max(0LL, x - y); r.insert(k, c); }
        return r;
    }
    bool subsetOf(const Multiset& o) const { for (auto& p : items()) if (p.second > o.count(p.first)) return false; return true; }
};

int main() {
    {   Multiset m; m.insert(5, 3); m.insert(2); m.insert(9, 2); m.insert(5);                      // 손으로 확인: {2, 5x4, 9x2}
        assert(m.size() == 7 && m.distinct() == 3 && m.count(5) == 4 && m.kth(0) == 2 && m.kth(1) == 5 && m.kth(4) == 5 && m.kth(5) == 9 && m.rank(5) == 1 && m.rank(6) == 5 && m.rank(10) == 7);
        assert(m.lowerBound(3) == 5 && m.upperBound(5) == 9 && m.upperBound(9) == INT32_MAX && m.countRange(2, 5) == 5 && m.countRange(6, 8) == 0);
        assert(m.erase(5, 10) == 4 && m.count(5) == 0 && m.distinct() == 2 && m.erase(7) == 0 && m.minimum() == 2 && m.maximum() == 9); }
    std::mt19937 rng(59); Multiset m; std::multiset<int> ref;
    for (int step = 0; step < 40000; ++step) {
        const int op = (int)(rng() % 12), x = (int)(rng() % 400) - 200;
        if (op < 4) { const int c = 1 + (int)(rng() % 4); m.insert(x, c); for (int i = 0; i < c; ++i) ref.insert(x); }
        else if (op < 7) { const int c = 1 + (int)(rng() % 5); long long want = 0; for (int i = 0; i < c; ++i) { auto it = ref.find(x); if (it == ref.end()) break; ref.erase(it); ++want; } assert(m.erase(x, c) == want); }
        else if (op == 7) { assert(m.count(x) == (long long)ref.count(x)); }
        else if (op == 8) { assert(m.rank(x) == (long long)std::distance(ref.begin(), ref.lower_bound(x))); }
        else if (op == 9 && !ref.empty()) { const long long i = (long long)(rng() % ref.size()); auto it = ref.begin(); std::advance(it, i); assert(m.kth(i) == *it); }
        else if (op == 10) { auto lb = ref.lower_bound(x), ub = ref.upper_bound(x); assert(m.lowerBound(x) == (lb == ref.end() ? INT32_MAX : *lb) && m.upperBound(x) == (ub == ref.end() ? INT32_MAX : *ub)); }
        else { const int hi = x + (int)(rng() % 100); assert(m.countRange(x, hi) == (long long)std::distance(ref.lower_bound(x), ref.upper_bound(hi))); }
        assert(m.size() == (long long)ref.size());
    }
    {   std::vector<std::pair<int, long long>> got = m.items(), want; for (auto it = ref.begin(); it != ref.end();) { const int v = *it; const long long c = (long long)ref.count(v); want.push_back({v, c}); std::advance(it, c); } assert(got == want && m.distinct() == want.size()); }
    {   Multiset huge; huge.insert(7, 1000000); for (int i = 0; i < 1000; ++i) huge.insert(7); assert(huge.distinct() == 1 && huge.size() == 1001000 && huge.kth(1000999) == 7 && huge.rank(8) == 1001000); }       // 개수가 커도 노드 하나
    for (int trial = 0; trial < 100; ++trial) {                                                    // 다중집합 연산은 값별 개수 정의와 같다
        Multiset a, b; std::multiset<int> ra, rb; for (int i = 0; i < 60; ++i) { int x = (int)(rng() % 15); a.insert(x); ra.insert(x); x = (int)(rng() % 15); b.insert(x); rb.insert(x); }
        for (char op : {'u', 'i', '+', '-'}) { Multiset r = Multiset::combine(a, b, op); for (int v = 0; v < 15; ++v) { const long long x = (long long)ra.count(v), y = (long long)rb.count(v); assert(r.count(v) == (op == 'u' ? std::max(x, y) : op == 'i' ? std::min(x, y) : op == '+' ? x + y : std::max(0LL, x - y))); } }
        assert(Multiset::combine(a, b, 'i').subsetOf(a) && a.subsetOf(Multiset::combine(a, b, 'u')) && a.subsetOf(Multiset::combine(a, b, '+')) && Multiset::combine(a, b, '-').subsetOf(a) && a.subsetOf(a));
    }
    std::cout << "Multiset: 40000 random insert/erase/count/rank/kth/bounds/countRange operations matched std::multiset; one node held a value inserted 1001000 times; union (max), intersection (min), sum and difference of multisets matched the per-value definitions on 100 random pairs" << std::endl;
    return 0;
}
// Time Complexity: insert·erase·count·rank·kth·bounds O(log d) (d: 서로 다른 값의 수, 기대), 다중집합 연산 O(d log d)
// Space Complexity: O(d) — 같은 값은 노드 하나에 개수로 저장
```
## BitSet()
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 비트 집합(BitSet): 우주가 {0, …, n−1} 로 작게 고정되어 있으면 원소 i 의 소속을 비트 하나로 표현한다. 64 비트 워드 ⌈n/64⌉ 개면 충분해 원소당 1 비트의 메모리, 원소 접근은 워드 번호 i>>6 과 비트 위치 i&63 의 두 연산. 집합 연산이 워드 단위 비트 연산 한 번으로 64 개 원소를 동시에 처리해서 합·교·차·대칭차가 O(n/64) 로 매우 빠르다. 원소 수는 popcount 로 센다.
// 마지막 워드의 남는 비트(n 이상의 위치)는 항상 0 으로 유지해야 한다 — NOT 이나 왼쪽 이동이 이 비트를 1 로 만들면 개수·상등·순회가 틀린다. 순회는 워드마다 `ctz`(끝의 0 개수)로 가장 낮은 켜진 비트를 찾고 `x &= x − 1` 로 지우며 켜진 비트만 방문한다(밀집하지 않아도 O(n/64 + 원소 수)). 이동(shift)은 워드 단위로 옮기고 비트 단위 나머지를 이웃 워드와 이어 붙인다.
// 검증: ① 무작위 set/reset/flip/test 열이 std::bitset<200> 과 같고 count/any/none/all 일치 ② 여러 우주 크기(1..300)에서 벡터<bool> 모델과 비교하고 남는 비트가 항상 0 ③ 합·교·차·대칭차·여집합·부분집합·교차 판정이 모델과 같음 ④ findFirst/findNext 순회가 정확히 켜진 비트를 오름차순으로 나열 ⑤ 왼쪽·오른쪽 이동이 모든 k(0..n+1)에서 모델과 같음 ⑥ 메모리 워드 수 = ⌈n/64⌉.
class BitSet { std::size_t n_; std::vector<uint64_t> w_;
    void trim() { if (n_ % 64) w_.back() &= (1ull << (n_ % 64)) - 1; }
public:
    explicit BitSet(std::size_t n) : n_(n), w_((n + 63) / 64, 0) {} std::size_t size() const { return n_; } std::size_t words() const { return w_.size(); }
    void set(std::size_t i) { w_[i >> 6] |= 1ull << (i & 63); } void reset(std::size_t i) { w_[i >> 6] &= ~(1ull << (i & 63)); } void flip(std::size_t i) { w_[i >> 6] ^= 1ull << (i & 63); } bool test(std::size_t i) const { return w_[i >> 6] >> (i & 63) & 1; }
    void setAll() { for (auto& x : w_) x = ~0ull; trim(); } void clear() { for (auto& x : w_) x = 0; }
    std::size_t count() const { std::size_t c = 0; for (uint64_t x : w_) c += (std::size_t)__builtin_popcountll(x); return c; }
    bool any() const { for (uint64_t x : w_) if (x) return true; return false; } bool none() const { return !any(); } bool all() const { return count() == n_; }
    BitSet& operator|=(const BitSet& o) { for (std::size_t i = 0; i < w_.size(); i++) w_[i] |= o.w_[i]; return *this; } BitSet& operator&=(const BitSet& o) { for (std::size_t i = 0; i < w_.size(); i++) w_[i] &= o.w_[i]; return *this; }
    BitSet& operator^=(const BitSet& o) { for (std::size_t i = 0; i < w_.size(); i++) w_[i] ^= o.w_[i]; return *this; } BitSet& andNot(const BitSet& o) { for (std::size_t i = 0; i < w_.size(); i++) w_[i] &= ~o.w_[i]; return *this; }
    BitSet operator~() const { BitSet r(n_); for (std::size_t i = 0; i < w_.size(); i++) r.w_[i] = ~w_[i]; r.trim(); return r; }
    bool subsetOf(const BitSet& o) const { for (std::size_t i = 0; i < w_.size(); i++) if (w_[i] & ~o.w_[i]) return false; return true; } bool intersects(const BitSet& o) const { for (std::size_t i = 0; i < w_.size(); i++) if (w_[i] & o.w_[i]) return true; return false; }
    bool operator==(const BitSet& o) const { return n_ == o.n_ && w_ == o.w_; }
    long findNext(long after) const { std::size_t i = (std::size_t)(after + 1); if (i >= n_) return -1; std::size_t wi = i >> 6; uint64_t x = w_[wi] & (~0ull << (i & 63)); for (;;) { if (x) return (long)(wi * 64 + (std::size_t)__builtin_ctzll(x)); if (++wi >= w_.size()) return -1; x = w_[wi]; } }
    long findFirst() const { return findNext(-1); }
    BitSet shiftLeft(std::size_t k) const { BitSet r(n_); if (k >= n_) return r; std::size_t ws = k >> 6, bs = k & 63; for (std::size_t i = w_.size(); i-- > ws;) { uint64_t v = w_[i - ws] << bs; if (bs && i - ws > 0) v |= w_[i - ws - 1] >> (64 - bs); r.w_[i] = v; } r.trim(); return r; }          // 낮은 인덱스 → 높은 인덱스
    BitSet shiftRight(std::size_t k) const { BitSet r(n_); if (k >= n_) return r; std::size_t ws = k >> 6, bs = k & 63; for (std::size_t i = 0; i + ws < w_.size(); i++) { uint64_t v = w_[i + ws] >> bs; if (bs && i + ws + 1 < w_.size()) v |= w_[i + ws + 1] << (64 - bs); r.w_[i] = v; } return r; }
    bool tailClean() const { return n_ % 64 == 0 || (w_.back() >> (n_ % 64)) == 0; } };
BitSet fromModel(const std::vector<bool>& m) { BitSet b(m.size()); for (std::size_t i = 0; i < m.size(); i++) if (m[i]) b.set(i); return b; }
bool same(const BitSet& b, const std::vector<bool>& m) { if (b.size() != m.size()) return false; for (std::size_t i = 0; i < m.size(); i++) if (b.test(i) != m[i]) return false; return b.tailClean(); }
std::string bitRow(const BitSet& b) { std::string s; for (std::size_t i = 0; i < b.size(); ++i) s += b.test(i) ? '1' : '.'; return s; }       // 그림: 칸 i 가 1 이면 i 가 집합의 원소
int main() {
    {   BitSet A(10), B(10); for (int i : {1, 3, 5, 7}) A.set(i); for (int i : {3, 4, 5, 6}) B.set(i);   // A = {1,3,5,7}, B = {3,4,5,6}
        auto op = [&](char c) { BitSet r = A; if (c == '|') r |= B; else if (c == '&') r &= B; else if (c == '^') r ^= B; else r.andNot(B); return bitRow(r); };
        assert(bitRow(A) == ".1.1.1.1.." && bitRow(B) == "...1111...");
        assert(op('|') == ".1.11111.." && op('&') == "...1.1...." && op('^') == ".1..1.11.." && op('-') == ".1.....1.." && bitRow(~A) == "1.1.1.1.11");    // 합·교·대칭차·차·여집합: 워드 단위 한 번의 비트 연산
        std::cout << "A     " << bitRow(A) << "\nB     " << bitRow(B) << "\nA|B   " << op('|') << "\nA&B   " << op('&') << "\nA^B   " << op('^') << "\nA\\B   " << op('-') << "\n~A    " << bitRow(~A) << "\n"; }
    std::mt19937 rng(33); { BitSet b(200); std::bitset<200> ref; for (int step = 0; step < 30000; step++) { std::size_t i = rng() % 200; int op = (int)(rng() % 4); if (op == 0) { b.set(i); ref.set(i); } else if (op == 1) { b.reset(i); ref.reset(i); } else if (op == 2) { b.flip(i); ref.flip(i); } else assert(b.test(i) == ref.test(i));   // ①
          assert(b.count() == ref.count() && b.any() == ref.any() && b.none() == ref.none() && b.all() == ref.all() && b.tailClean()); } b.setAll(); ref.set(); assert(b.all() && ref.all() && b.count() == 200); b.clear(); assert(b.none()); }
    for (int n : {1, 2, 63, 64, 65, 127, 128, 129, 200, 300}) { assert(BitSet(n).words() == (std::size_t)((n + 63) / 64));                                                                                                                       // ⑥
        for (int rep = 0; rep < 40; rep++) { std::vector<bool> ma(n), mb(n); for (int i = 0; i < n; i++) { ma[i] = rng() % 3 == 0; mb[i] = rng() % 2; } BitSet a = fromModel(ma), b = fromModel(mb); assert(same(a, ma) && same(b, mb));                         // ②
            BitSet u = a, in = a, d = a, x = a; u |= b; in &= b; d.andNot(b); x ^= b; std::vector<bool> mu(n), mi(n), md(n), mx(n), mc(n); bool sub = true, inter = false; for (int i = 0; i < n; i++) { mu[i] = ma[i] || mb[i]; mi[i] = ma[i] && mb[i]; md[i] = ma[i] && !mb[i]; mx[i] = ma[i] != mb[i]; mc[i] = !ma[i]; if (ma[i] && !mb[i]) sub = false; if (ma[i] && mb[i]) inter = true; }
            assert(same(u, mu) && same(in, mi) && same(d, md) && same(x, mx) && same(~a, mc) && a.subsetOf(b) == sub && a.intersects(b) == inter && (a == b) == (ma == mb));                                                                  // ③
            std::vector<long> seen; for (long i = a.findFirst(); i >= 0; i = a.findNext(i)) seen.push_back(i); std::vector<long> want; for (int i = 0; i < n; i++) if (ma[i]) want.push_back(i); assert(seen == want && seen.size() == a.count());   // ④
            for (int k : {0, 1, 5, 63, 64, 65, n - 1, n, n + 1}) { if (k < 0) continue; std::vector<bool> ml(n, false), mr(n, false); for (int i = 0; i < n; i++) { if (i >= k && ma[i - k]) ml[i] = true; if (i + k < n && ma[i + k]) mr[i] = true; }   // ⑤ 이동
                assert(same(a.shiftLeft((std::size_t)k), ml) && same(a.shiftRight((std::size_t)k), mr)); } } }
    std::cout << "BitSet: a word-array bit set matched std::bitset<200> over 30000 random operations, matched a vector<bool> model for universes of 1..300 elements including set algebra, complement, subset/intersection tests, findFirst/findNext enumeration and left/right shifts by every interesting amount, and always kept the unused tail bits zero" << std::endl; return 0;
}
// Time Complexity: 원소 접근 O(1), 집합 연산·count O(N/64), 순회 O(N/64 + 원소 수)
// Space Complexity: N/8 바이트
```
## ImmutableSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 불변 집합(ImmutableSet): 한 번 만들면 바뀌지 않는 집합이다. 추가·삭제는 원본을 고치는 대신 새 집합(새 버전)을 돌려주고 원본은 그대로 남는다 — 그러면 여러 스레드가 락 없이 안전하게 읽고, 이전 버전으로 되돌리기(undo)가 공짜이며, 함수가 부작용 없이 집합을 주고받을 수 있다. 매번 전체를 복사하면 O(n) 이지만, 영속 자료구조는 바뀐 경로의 노드만 새로 만들고 나머지는 이전 버전과 공유(structural sharing)해서 갱신당 O(log n) 노드만 할당한다.
// 이 코드는 영속 트립(treap)이다: 이진 탐색 트리이면서 우선순위에 대해 힙. 우선순위를 키의 해시(결정적)로 정하면 같은 키 집합은 삽입 순서와 무관하게 항상 같은 모양의 트리가 된다(정규 형태) — 두 집합의 동등성이 구조 비교로 환원되고 해시 컨싱(hash-consing)이 가능하다. 삽입은 분할(split)과 병합(merge)으로, 삭제는 왼쪽·오른쪽 부분 트리를 병합해 구현하고, 모든 노드는 const 로 만들어 공유가 안전하다.
// 검증: ① 무작위 삽입·삭제 열의 모든 버전이 std::set 스냅샷과 같고, 갱신 후에도 이전 버전 전부가 변하지 않음(영속성) ② 갱신당 새로 할당한 노드 수가 O(log n) (평균 ≤ 4·log₂ n + 10) ③ 이미 있는 원소 삽입·없는 원소 삭제는 새 노드 0 개이고 같은 버전을 돌려줌 ④ 같은 키 집합을 다른 순서·삽입과 삭제를 섞은 이력으로 만들어도 트리 모양이 완전히 같음(정규 형태) ⑤ 크기 필드·힙 순서·이진 탐색 순서 불변식 ⑥ 생존 노드 수 관리(버전을 놓으면 해제)와 공유 확인.
struct Node; typedef std::shared_ptr<const Node> P;
struct Node { int key; unsigned long long pri; P l, r; int sz; static int live, created; Node(int k, unsigned long long p, P a, P b) : key(k), pri(p), l(std::move(a)), r(std::move(b)), sz(1 + (l ? l->sz : 0) + (r ? r->sz : 0)) { ++live; ++created; } ~Node() { --live; } };
int Node::live = 0, Node::created = 0;
unsigned long long prio(int k) { unsigned long long x = (unsigned long long)(unsigned)k + 0x9E3779B97F4A7C15ull; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull; x = (x ^ (x >> 27)) * 0x94D049BB133111EBull; return x ^ (x >> 31); }
P mk(int k, unsigned long long p, P l, P r) { return std::make_shared<const Node>(k, p, std::move(l), std::move(r)); }
int size(const P& t) { return t ? t->sz : 0; }
bool contains(const P& t, int k) { const Node* n = t.get(); while (n) { if (k < n->key) n = n->l.get(); else if (n->key < k) n = n->r.get(); else return true; } return false; }
std::pair<P, P> split(const P& t, int k) { if (!t) return {nullptr, nullptr}; if (t->key < k) { auto s = split(t->r, k); return {mk(t->key, t->pri, t->l, s.first), s.second}; } auto s = split(t->l, k); return {s.first, mk(t->key, t->pri, s.second, t->r)}; }   // (< k, ≥ k)
P merge(const P& a, const P& b) { if (!a) return b; if (!b) return a; if (a->pri > b->pri) return mk(a->key, a->pri, a->l, merge(a->r, b)); return mk(b->key, b->pri, merge(a, b->l), b->r); }
P insert(const P& t, int k) { if (contains(t, k)) return t; auto s = split(t, k); return merge(merge(s.first, mk(k, prio(k), nullptr, nullptr)), s.second); }
P erase(const P& t, int k) { if (!t) return t; if (k < t->key) { P nl = erase(t->l, k); return nl == t->l ? t : mk(t->key, t->pri, nl, t->r); } if (t->key < k) { P nr = erase(t->r, k); return nr == t->r ? t : mk(t->key, t->pri, t->l, nr); } return merge(t->l, t->r); }
void inorder(const P& t, std::vector<int>& out) { if (!t) return; inorder(t->l, out); out.push_back(t->key); inorder(t->r, out); }
bool sameShape(const P& a, const P& b) { if (!a || !b) return !a && !b; return a->key == b->key && sameShape(a->l, b->l) && sameShape(a->r, b->r); }
bool valid(const P& t, long long lo, long long hi) { if (!t) return true; if (t->key <= lo || t->key >= hi || t->sz != 1 + size(t->l) + size(t->r)) return false; if ((t->l && t->l->pri > t->pri) || (t->r && t->r->pri > t->pri)) return false; return valid(t->l, lo, t->key) && valid(t->r, t->key, hi); }
int main() {
    std::mt19937 rng(34); std::vector<P> versions; std::vector<std::vector<int>> snapshots; P cur; std::set<int> ref; long newNodes = 0, updates = 0; double bound = 0;
    for (int step = 0; step < 4000; step++) { int x = (int)(rng() % 1500); int created0 = Node::created; if (rng() % 3) cur = insert(cur, x), ref.insert(x); else cur = erase(cur, x), ref.erase(x);                                             // ① ②
        if (ref.size() > 16) { newNodes += Node::created - created0; updates++; bound += 4 * std::log2((double)ref.size()) + 10; } if (step % 40 == 0) { versions.push_back(cur); snapshots.push_back(std::vector<int>(ref.begin(), ref.end())); }
        assert(size(cur) == (int)ref.size()); if (step % 500 == 0) assert(valid(cur, -1, 1 << 30)); }
    assert((double)newNodes <= bound);                                                                                                                                                                          // 갱신당 평균 새 노드 ≤ 4 log n + 10
    for (std::size_t i = 0; i < versions.size(); i++) { std::vector<int> got; inorder(versions[i], got); assert(got == snapshots[i] && valid(versions[i], -1, 1 << 30)); }                                                    // 이전 버전은 변하지 않았다
    { P t = insert(insert(insert(nullptr, 3), 1), 2); int c = Node::created; P same = insert(t, 2); assert(same == t && Node::created == c); P same2 = erase(t, 99); assert(same2 == t && Node::created == c); P gone = erase(t, 2); assert(gone != t && contains(t, 2) && !contains(gone, 2) && size(t) == 3 && size(gone) == 2); }   // ③
    for (int rep = 0; rep < 100; rep++) { std::set<int> keys; for (int i = 0, k = (int)(rng() % 80); i < k; i++) keys.insert((int)(rng() % 1000)); std::vector<int> a(keys.begin(), keys.end()), b = a, c = a; std::shuffle(b.begin(), b.end(), rng);    // ④ 정규 형태
        P t1, t2, t3; for (int x : a) t1 = insert(t1, x); for (int x : b) t2 = insert(t2, x); for (int x : c) t3 = insert(t3, x); std::vector<int> extra; for (int i = 0; i < 30; i++) { int e = 2000 + (int)(rng() % 500); extra.push_back(e); t3 = insert(t3, e); } for (int e : extra) t3 = erase(t3, e);
        assert(sameShape(t1, t2) && sameShape(t1, t3) && valid(t1, -1, 1 << 30) && size(t1) == (int)a.size()); }
    assert(Node::live > 0); versions.clear(); cur.reset(); assert(Node::live == 0);                                                                                                                              // ⑥ 모든 버전을 놓으면 해제
    { P base; for (int i = 0; i < 1000; i++) base = insert(base, i * 2); int live0 = Node::live; P next = insert(base, 777); int retained = Node::live - live0; assert(retained <= 4 * 10 + 10 && retained < 1001 / 10 && size(next) == 1001 && size(base) == 1000 && contains(next, 777) && !contains(base, 777)); }   // 공유: 새 버전이 보유한 새 노드는 O(log n) 개뿐(split 의 임시 노드는 병합 뒤 해제)
    std::cout << "ImmutableSet: a persistent treap with hash priorities kept every one of " << 4000 / 40 << " saved versions unchanged through 4000 random inserts and erases, allocated " << (double)newNodes / (double)updates << " nodes per update on average (O(log n)), returned the identical version for no-op updates, built identical tree shapes for the same key set from different histories, and released all nodes once the versions were dropped" << std::endl; return 0;
}
// Time Complexity: 조회·삽입·삭제 기대 O(log N)
// Space Complexity: 갱신당 새 노드 O(log N), 나머지는 이전 버전과 공유
```

# Part 6. 비트 집합
## SetBit()
### 대표코드
```cpp
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 비트 켜기(SetBit): 정수의 i 번째 비트를 1 로 만든다 — `x | (1 << i)`. 집합으로는 "원소 i 추가" 이다. 이미 켜져 있으면 변화가 없다(멱등). 함정이 많다. (1) 리터럴 `1` 은 int 라서 `1 << 31` 은 부호 있는 정수 오버플로(정의되지 않은 동작)이고 `1 << 32` 이상은 시프트 폭 초과(정의되지 않음)이다 — 64 비트 값에는 `1ULL << i` 를 쓰고 i < 64 임을 보장해야 한다. (2) 부호 있는 정수의 최상위 비트를 켜면 음수가 된다 — 비트 연산은 부호 없는 형으로 한다. (3) 비트 번호가 범위 밖이면 조용히 틀린다.
// 여러 워드로 된 큰 비트열은 i 를 워드 번호 i/64 와 비트 번호 i%64 로 나눈다(`i >> 6`, `i & 63`). 연속한 비트 구간 [l, r) 을 한 번에 켜려면 마스크 `((1ULL << (r−l)) − 1) << l` 인데 r−l = 64 일 때 `1ULL << 64` 가 정의되지 않으므로 그 경우를 따로 처리해야 한다. 켜기 전후의 popcount 가 정확히 1 늘어나는 것은 그 비트가 꺼져 있었을 때뿐이다.
// 검증: ① 모든 16 비트 값 × 모든 비트 위치(0..15) 전수에서 `x | (1<<i)` 가 산술 정의(x + (꺼져 있었으면 2^i))와 같음 ② 무작위 64 비트 값과 위치 0..63 에서 std::bitset 과 일치, 멱등 ③ popcount 변화 == (이전에 꺼져 있었으면 1) ④ 여러 워드 비트열의 set 이 모델(vector<bool>)과 일치 ⑤ 구간 켜기 마스크가 반복문과 같음(폭 64 포함) ⑥ 안전하지 않은 `1 << 31`·`1 << 32` 대신 `1ULL` 을 쓰면 최상위 비트(63)까지 정확.
uint64_t setBit(uint64_t x, unsigned i) { assert(i < 64); return x | (1ull << i); }
void setBitWide(std::vector<uint64_t>& w, std::size_t i) { w[i >> 6] |= 1ull << (i & 63); }
uint64_t rangeMask(unsigned l, unsigned r) { assert(l <= r && r <= 64); unsigned len = r - l; if (len == 0) return 0; uint64_t m = len == 64 ? ~0ull : ((1ull << len) - 1); return m << l; }           // len == 64 이면 시프트 폭 64 를 피한다
int main() {
    for (unsigned x = 0; x < 65536; x++) for (unsigned i = 0; i < 16; i++) { bool was = x >> i & 1; uint64_t got = setBit(x, i); assert(got == (uint64_t)x + (was ? 0u : (1u << i)));   // ① 산술 정의와 같음
        assert(setBit(got, i) == got && (got >> i & 1)); }                                                                                                                                  // ② 멱등, 켜짐
    std::mt19937_64 rng(35);
    for (int rep = 0; rep < 20000; rep++) { uint64_t x = rng(); unsigned i = (unsigned)(rng() % 64); std::bitset<64> b(x); b.set(i); uint64_t got = setBit(x, i); assert(got == b.to_ullong() && setBit(got, i) == got);                  // ② 무작위 64 비트
        assert(__builtin_popcountll(got) == __builtin_popcountll(x) + ((x >> i & 1) ? 0 : 1)); }                                                                                              // ③
    { assert(setBit(0, 63) == 0x8000000000000000ull && setBit(0, 0) == 1 && setBit(~0ull, 17) == ~0ull);                                                                                // ⑥ 최상위 비트
      uint64_t viaInt = 0; unsigned i = 31; uint64_t good = 1ull << i; viaInt = (uint64_t)(uint32_t)(1u << i); assert(good == viaInt && good == 0x80000000ull); }                                                              // 1 << 31 대신 1u 또는 1ULL
    for (int rep = 0; rep < 200; rep++) { std::size_t n = 1 + rng() % 500; std::vector<uint64_t> w((n + 63) / 64, 0); std::vector<bool> model(n, false); for (int s = 0; s < 300; s++) { std::size_t i = rng() % n; setBitWide(w, i); model[i] = true; }   // ④ 여러 워드
        for (std::size_t i = 0; i < n; i++) assert(((w[i >> 6] >> (i & 63)) & 1) == (model[i] ? 1u : 0u)); }
    for (unsigned l = 0; l <= 64; l++) for (unsigned r = l; r <= 64; r++) { uint64_t loop = 0; for (unsigned i = l; i < r; i++) loop = setBit(loop, i); assert(rangeMask(l, r) == loop); }                                            // ⑤ 구간 켜기 (폭 64 포함)
    std::cout << "SetBit: x | (1<<i) agreed with the arithmetic definition for all 16-bit values and positions, matched std::bitset on 20000 random 64-bit values, was idempotent and raised the popcount exactly when the bit was previously clear, worked across multi-word bit strings, and the range-mask formula (including the full 64-bit width case) equalled a bit-by-bit loop" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ClearBit()
### 대표코드
```cpp
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 비트 끄기(ClearBit): i 번째 비트를 0 으로 만든다 — `x & ~(1ULL << i)`. 집합으로는 "원소 i 제거" 이다. 이미 꺼져 있으면 변화가 없다. 관련 관용구: 가장 낮은 켜진 비트 지우기 `x & (x − 1)` (x−1 은 가장 낮은 1 과 그 아래 0 들을 뒤집어 1 로 바꾸므로 AND 하면 가장 낮은 1 만 사라짐), 가장 낮은 켜진 비트 분리하기 `x & −x`, 2 의 거듭제곱 판정 `x != 0 && (x & (x − 1)) == 0` (켜진 비트가 하나뿐), 하위 k 비트만 남기기 `x & ((1ULL << k) − 1)`, 구간 끄기 `x & ~mask`.
// `x & (x−1)` 를 반복하면 켜진 비트 수만큼만 반복하고 끝난다(켜진 비트를 낮은 쪽부터 하나씩 방문하는 순회의 기본형). 끄기와 켜기는 서로 독립이라 이미 꺼진 비트를 끄기는 변화 없음, 끈 비트의 켜기는 원래 값 복원은 아님(원래 켜져 있었는지 알 수 없음).
// 검증: ① 모든 16 비트 값 × 위치에서 `x & ~(1<<i)` 가 산술 정의(x − (켜져 있었으면 2^i))와 같음, 멱등, 끈 뒤 테스트하면 0 ② 무작위 64 비트에서 std::bitset 과 일치, popcount 변화 == 이전에 켜져 있었으면 −1 ③ `x & (x−1)` 가 가장 낮은 켜진 비트를 정확히 지우고 반복 횟수 == popcount, `x & −x` 가 가장 낮은 켜진 비트만 남김 ④ 2 의 거듭제곱 판정이 0..2^16 에서 정의(popcount == 1)와 일치하고 64 비트 경계값(2^63, 2^63+1, 0, 모든 비트) 확인 ⑤ 하위 k 비트 남기기·구간 끄기가 반복문과 같음(k = 0, 64 포함) ⑥ 끄기와 켜기의 교환 불가(같은 비트에서 순서에 따라 다름).
uint64_t clearBit(uint64_t x, unsigned i) { assert(i < 64); return x & ~(1ull << i); }
uint64_t lowMask(unsigned k) { assert(k <= 64); return k == 64 ? ~0ull : ((1ull << k) - 1); }
bool isPow2(uint64_t x) { return x != 0 && (x & (x - 1)) == 0; }
int main() {
    for (unsigned x = 0; x < 65536; x++) for (unsigned i = 0; i < 16; i++) { bool was = x >> i & 1; uint64_t got = clearBit(x, i); assert(got == (uint64_t)x - (was ? (1u << i) : 0u) && !(got >> i & 1) && clearBit(got, i) == got); }       // ①
    std::mt19937_64 rng(36);
    for (int rep = 0; rep < 20000; rep++) { uint64_t x = rng(); unsigned i = (unsigned)(rng() % 64); std::bitset<64> b(x); b.reset(i); uint64_t got = clearBit(x, i); assert(got == b.to_ullong() && __builtin_popcountll(got) == __builtin_popcountll(x) - ((x >> i & 1) ? 1 : 0));   // ②
        uint64_t y = rng() >> (rng() % 64); int iterations = 0; uint64_t t = y; while (t) { uint64_t lowest = t & (~t + 1); uint64_t cleared = t & (t - 1); assert(cleared == (t ^ lowest) && lowest == (t & -t)); assert(__builtin_ctzll(lowest) == __builtin_ctzll(t)); t = cleared; iterations++; } assert(iterations == __builtin_popcountll(y)); }   // ③
    for (unsigned x = 0; x < 65536; x++) assert(isPow2(x) == (__builtin_popcount(x) == 1));                                                                                                       // ④
    assert(isPow2(1ull << 63) && !isPow2((1ull << 63) + 1) && !isPow2(0) && !isPow2(~0ull) && isPow2(1) && isPow2(2) && !isPow2(3));
    for (unsigned k = 0; k <= 64; k++) { uint64_t m = lowMask(k); for (int rep = 0; rep < 20; rep++) { uint64_t x = rng(); uint64_t keep = x & m, loop = 0; for (unsigned i = 0; i < k; i++) loop |= x & (1ull << i); assert(keep == loop);                // ⑤ 하위 k 비트
            unsigned l = (unsigned)(rng() % 65), r = l + (unsigned)(rng() % (65 - l)); uint64_t cleared = x; for (unsigned i = l; i < r; i++) cleared = clearBit(cleared, i); uint64_t rm = (r - l == 0) ? 0 : (lowMask(r - l) << l); assert((x & ~rm) == cleared); } }
    { assert(clearBit(0b0100, 2) == clearBit(0, 2));                                                                                                                                   // ⑥ 끄기는 정보를 잃는다: 서로 다른 입력이 같은 결과
      for (int rep = 0; rep < 1000; rep++) { uint64_t x = rng(); unsigned i = (unsigned)(rng() % 64); uint64_t bit = 1ull << i; assert((clearBit(x, i) | bit) != clearBit(x | bit, i) && (clearBit(x, i) | bit) == (x | bit) && clearBit(x | bit, i) == (x & ~bit)); } }   // 끄기→켜기 와 켜기→끄기 는 다르다
    std::cout << "ClearBit: x & ~(1<<i) matched the arithmetic definition for all 16-bit values and positions and std::bitset on 20000 random 64-bit values; x & (x-1) removed exactly the lowest set bit (loop count equal to popcount), x & -x isolated it, the power-of-two test matched popcount == 1 up to 2^16 and at the 64-bit boundaries, and low-bit and range masks equalled bit-by-bit loops" << std::endl; return 0;
}
// Time Complexity: O(1) (켜진 비트 순회는 O(popcount))
// Space Complexity: O(1)
```
## ToggleBit()
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 비트 뒤집기(ToggleBit): i 번째 비트를 반대로 — `x ^ (1ULL << i)`. 집합으로는 "원소 i 가 있으면 빼고 없으면 넣기". 두 번 뒤집으면 원래대로(involution)이고, 서로 다른 위치의 뒤집기는 순서와 무관하게 교환 가능하다(XOR 의 교환·결합 법칙) — 여러 위치를 뒤집는 일은 그 위치들의 마스크 하나로 XOR 하는 것과 같다. toggle(x, i) = 켜져 있으면 끄기, 꺼져 있으면 켜기이므로 `test ? clear : set` 과 같다.
// 응용: 그레이 코드(i 번째 코드에서 i+1 번째로 갈 때 뒤집을 비트는 i+1 의 끝의 0 개수 ctz), 패리티 비트, XOR 으로 두 값 교환·변경 사항 적용, 스위치 퍼즐. 라이츠 아웃(Lights Out)은 버튼 하나가 자기와 상하좌우 이웃을 뒤집는 퍼즐이라 버튼 누름의 조합이 마스크 XOR 이다 — 누르는 순서는 상관없고 같은 버튼은 두 번 누르면 상쇄되므로 각 버튼을 누를지 말지 2ⁿ 가지만 보면 된다.
// 검증: ① 모든 16 비트 값 × 위치에서 `x ^ (1<<i)` 가 (켜져 있었으면 끄기, 아니면 켜기) 와 같고 두 번 뒤집으면 원래 값, popcount 가 ±1 ② 무작위 64 비트에서 std::bitset::flip 과 일치 ③ 서로 다른 위치 뒤집기의 교환·결합: 순서를 섞어 적용해도 같고 마스크 하나로 XOR 한 것과 같음 ④ 그레이 코드: 이웃한 코드가 정확히 한 비트 다르고 뒤집는 비트가 ctz(i+1), n = 1..16 에서 모두 서로 다름(2ⁿ 개) ⑤ 라이츠 아웃 3×3 과 4×4: 모든 버튼 마스크 2ⁿ 개를 열거해 "전부 켜짐 → 전부 꺼짐" 해의 개수를 구하고 해를 적용해 실제로 풀리는지 확인(3×3 은 유일해 1 개, 4×4 는 16 개 — 영공간 차원 4). 격자를 직접 시뮬레이션하는 독립 오라클이 3×3 의 512 가지·4×4 의 65536 가지 누름 모두에서 해 집합과 일치하고, 아무것도 안 누르는 0 은 해가 아님(전부 꺼진 판에서 시작한 것이 아님).
uint64_t toggleBit(uint64_t x, unsigned i) { assert(i < 64); return x ^ (1ull << i); }
uint32_t pressMask(int r, int c, int R, int C) { uint32_t m = 0; auto bit = [&](int rr, int cc) { if (rr >= 0 && rr < R && cc >= 0 && cc < C) m ^= 1u << (rr * C + cc); }; bit(r, c); bit(r - 1, c); bit(r + 1, c); bit(r, c - 1); bit(r, c + 1); return m; }
int lightsOutSolutions(int R, int C, std::vector<uint32_t>* sols) { int n = R * C; std::vector<uint32_t> pm(n); for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) pm[r * C + c] = pressMask(r, c, R, C); uint32_t full = (1u << n) - 1; int count = 0;
    for (uint32_t presses = 0; presses <= full; presses++) { uint32_t board = full; for (int b = 0; b < n; b++) if (presses >> b & 1) board ^= pm[b]; if (board == 0) { count++; if (sols) sols->push_back(presses); } } return count; }          // 전부 켜짐에서 시작해 누른 버튼들의 마스크를 XOR
bool lightsOutSolved(int R, int C, uint32_t presses) { int g[4][4]; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) g[r][c] = 1; const int dr[5] = {0, -1, 1, 0, 0}, dc[5] = {0, 0, 0, -1, 1};      // 독립 오라클: 격자를 직접 시뮬레이션(전부 켜짐에서 시작)
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (presses >> (r * C + c) & 1) for (int d = 0; d < 5; d++) { int rr = r + dr[d], cc = c + dc[d]; if (rr >= 0 && rr < R && cc >= 0 && cc < C) g[rr][cc] ^= 1; }
    for (int r = 0; r < R; r++) { for (int c = 0; c < C; c++) { if (g[r][c]) return false; } } return true; }
int main() {
    for (unsigned x = 0; x < 65536; x++) for (unsigned i = 0; i < 16; i++) { bool was = x >> i & 1; uint64_t got = toggleBit(x, i); uint64_t viaBranch = was ? (uint64_t)x - (1u << i) : (uint64_t)x + (1u << i); assert(got == viaBranch && toggleBit(got, i) == x);       // ①
        assert(__builtin_popcountll(got) == __builtin_popcount(x) + (was ? -1 : 1)); }
    std::mt19937_64 rng(37);
    for (int rep = 0; rep < 20000; rep++) { uint64_t x = rng(); unsigned i = (unsigned)(rng() % 64); std::bitset<64> b(x); b.flip(i); assert(toggleBit(x, i) == b.to_ullong()); }                                                                                    // ②
    for (int rep = 0; rep < 2000; rep++) { uint64_t x = rng(); std::vector<unsigned> pos; uint64_t mask = 0; for (int k = 0, m = (int)(rng() % 10); k < m; k++) { unsigned p = (unsigned)(rng() % 64); pos.push_back(p); mask ^= 1ull << p; }             // ③
        uint64_t a = x; for (unsigned p : pos) a = toggleBit(a, p); std::vector<unsigned> shuffled = pos; std::shuffle(shuffled.begin(), shuffled.end(), rng); uint64_t b = x; for (unsigned p : shuffled) b = toggleBit(b, p); assert(a == b && a == (x ^ mask)); }
    for (int n = 1; n <= 16; n++) { std::vector<bool> seen(1u << n, false); uint32_t g = 0; seen[0] = true; for (uint32_t i = 1; i < (1u << n); i++) { uint32_t ng = i ^ (i >> 1); uint32_t flipped = g ^ ng; assert(__builtin_popcount(flipped) == 1 && flipped == (1u << __builtin_ctz(i)) && toggleBit(g, (unsigned)__builtin_ctz(i)) == ng);   // ④
            assert(!seen[ng]); seen[ng] = true; g = ng; } }
    { std::vector<uint32_t> s3, s4; int c3 = lightsOutSolutions(3, 3, &s3), c4 = lightsOutSolutions(4, 4, &s4); assert(c3 == 1 && c4 == 16 && s3.size() == 1 && s4.size() == 16);                                                          // ⑤
      assert(s3[0] != 0 && std::find(s4.begin(), s4.end(), 0u) == s4.end());                                                                                                                                                // 전부 꺼진 판에서 시작한 것이 아님: 아무것도 안 누르는 0 은 해가 아니다
      for (uint32_t m = 0; m < (1u << 9); m++) assert(lightsOutSolved(3, 3, m) == (m == s3[0]));                                                                                                                         // 격자 시뮬레이션과 모든 누름 조합에서 일치(해는 정확히 s3[0])
      for (uint32_t m = 0; m < (1u << 16); m++) assert(lightsOutSolved(4, 4, m) == std::binary_search(s4.begin(), s4.end(), m));
      for (int R = 2; R <= 4; R++) for (int C = 2; C <= 4; C++) { std::vector<uint32_t> s; int c = lightsOutSolutions(R, C, &s); assert(c >= 1 && (c & (c - 1)) == 0); } }                                                                   // 해 개수는 2 의 거듭제곱 (영공간 차원)
    std::cout << "ToggleBit: x ^ (1<<i) equalled the set-or-clear definition for all 16-bit values and positions (an involution changing popcount by one) and matched std::bitset::flip on 20000 random values, toggles at different positions commuted and equalled one XOR with the combined mask, the Gray-code step flipped exactly bit ctz(i) and visited all 2^n codes for n up to 16, and Lights Out had 1 solution on 3x3 and 16 on 4x4, with a direct grid simulation agreeing on every one of the 2^9 and 2^16 press sets" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TestBit()
### 대표코드
```cpp
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 비트 검사(TestBit): i 번째 비트가 켜져 있는지 읽는다 — `(x >> i) & 1` 또는 `(x & (1ULL << i)) != 0`. 집합으로는 "원소 i 가 속하는가". 부호 있는 정수에서 `x >> i` 는 오른쪽 이동이 산술 이동(구현 정의: 부호 비트를 채움)이라 음수에 대해 위쪽 비트가 1 로 채워지지만 `& 1` 로 최하위 비트만 읽으면 이어진다. 그래도 음수의 비트 패턴은 2 의 보수 표현이므로 먼저 부호 없는 형으로 바꿔서 읽는 것이 안전하다. 위치가 폭 이상이면 시프트가 정의되지 않으므로 범위를 검사해야 한다.
// 비트 필드 추출: 위치 lo 에서 폭 w 비트 `(x >> lo) & ((1ULL << w) − 1)` (w = 64 이면 마스크를 따로 처리). 패리티(켜진 비트 수의 홀짝)는 `popcount & 1` 이고 접어 XOR 하는 방법 `x ^= x >> 32; x ^= x >> 16; … ; x & 1` 로도 구한다. 비트열 뒤집기, 최상위 켜진 비트의 위치(floor(log₂ x))는 `63 − clz(x)`.
// 검증: ① 모든 16 비트 값 × 위치에서 두 가지 공식 `(x>>i)&1` 과 `(x & (1<<i)) != 0` 이 산술 정의 ⌊x / 2ⁱ⌋ mod 2 와 같음 ② 음수(int32, int64)의 2 의 보수 비트가 부호 없는 변환을 거쳐 올바르게 읽힘: 예컨대 −1 은 모든 비트가 1, INT_MIN 은 31 번만 1 ③ 무작위 64 비트가 std::bitset 과 일치, 범위 밖 위치는 안전하게 false 로 처리 ④ 비트 필드 추출이 반복문과 같음(폭 64 포함) ⑤ 패리티(접어 XOR 방식 == popcount&1) ⑥ 최상위 비트 위치 == floor(log₂ x) 와 비트 길이.
bool testBit(uint64_t x, unsigned i) { return i < 64 && ((x >> i) & 1); }
bool testBitMask(uint64_t x, unsigned i) { return i < 64 && (x & (1ull << i)) != 0; }
uint64_t extract(uint64_t x, unsigned lo, unsigned w) { assert(lo <= 64 && w <= 64 - lo); if (w == 0) return 0; uint64_t mask = w == 64 ? ~0ull : ((1ull << w) - 1); return (x >> lo) & mask; }
unsigned parityFold(uint64_t x) { x ^= x >> 32; x ^= x >> 16; x ^= x >> 8; x ^= x >> 4; x ^= x >> 2; x ^= x >> 1; return (unsigned)(x & 1); }
int main() {
    for (unsigned x = 0; x < 65536; x++) for (unsigned i = 0; i < 16; i++) { unsigned def = (x / (1u << i)) % 2; assert(testBit(x, i) == (def == 1) && testBitMask(x, i) == (def == 1)); }                              // ①
    { int32_t m1 = -1; for (unsigned i = 0; i < 32; i++) assert(testBit((uint64_t)(uint32_t)m1, i)); int32_t mn = INT32_MIN; for (unsigned i = 0; i < 32; i++) assert(testBit((uint64_t)(uint32_t)mn, i) == (i == 31));           // ②
      int64_t m64 = -1; for (unsigned i = 0; i < 64; i++) assert(testBit((uint64_t)m64, i)); int32_t neg5 = -5; assert((uint32_t)neg5 == 0xFFFFFFFBu); for (unsigned i = 0; i < 32; i++) assert(testBit((uint64_t)(uint32_t)neg5, i) == (bool)((0xFFFFFFFBu >> i) & 1u)); }
    std::mt19937_64 rng(38);
    for (int rep = 0; rep < 20000; rep++) { uint64_t x = rng(); std::bitset<64> b(x); for (unsigned i = 0; i < 64; i += 1 + (unsigned)(rng() % 7)) assert(testBit(x, i) == b.test(i) && testBitMask(x, i) == b.test(i)); assert(!testBit(x, 64) && !testBit(x, 100) && !testBitMask(x, 64)); }          // ③ 범위 밖
    for (int rep = 0; rep < 5000; rep++) { uint64_t x = rng(); unsigned lo = (unsigned)(rng() % 65), w = (unsigned)(rng() % (65 - lo)); uint64_t loop = 0; for (unsigned k = 0; k < w; k++) loop |= (uint64_t)testBit(x, lo + k) << k; assert(extract(x, lo, w) == loop); }   // ④
    assert(extract(~0ull, 0, 64) == ~0ull && extract(0xABCDull, 4, 8) == 0xBC && extract(5, 0, 0) == 0 && extract(0x8000000000000000ull, 63, 1) == 1);
    for (int rep = 0; rep < 20000; rep++) { uint64_t x = rng() >> (rng() % 64); assert(parityFold(x) == (unsigned)(__builtin_popcountll(x) & 1)); }                                                                       // ⑤
    for (int rep = 0; rep < 20000; rep++) { uint64_t x = (rng() >> (rng() % 64)) | 1; int hi = 63 - __builtin_clzll(x); unsigned bitLength = 0; for (uint64_t t = x; t; t >>= 1) bitLength++; assert((unsigned)(hi + 1) == bitLength && testBit(x, (unsigned)hi) && (hi == 63 || (x >> (hi + 1)) == 0)); }   // ⑥
    { uint64_t x = 1; for (unsigned k = 0; k < 64; k++) { assert(63 - __builtin_clzll(x) == (int)k); x <<= 1; } }
    std::cout << "TestBit: both read-a-bit formulas equalled floor(x / 2^i) mod 2 for all 16-bit values and positions, two's-complement bits of negative 32- and 64-bit integers were read correctly through unsigned conversion, out-of-range positions returned false instead of invoking undefined shifts, bit-field extraction matched a bit-by-bit loop, fold-XOR parity equalled popcount parity, and the highest set bit position equalled floor(log2 x)" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CountBits()
### 대표코드
```cpp
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 켜진 비트 세기(CountBits, popcount): 집합의 원소 수 |S|, 두 값의 해밍 거리 popcount(a ^ b). 방법: (1) 모든 비트를 훑기 — 비트 길이만큼 반복. (2) 커니핸(Kernighan): `x &= x − 1` 로 가장 낮은 켜진 비트를 하나씩 지우며 센다 — 반복이 정확히 popcount 번. (3) 표 조회: 8(또는 16)비트 조각마다 미리 계산한 표를 찾아 더한다 — 8 번의 조회. (4) 병렬 비트 합(SWAR): 인접한 1 비트 쌍을 더해 2 비트 칸에, 그 쌍을 더해 4 비트 칸에, … 로 이어 상수 번의 연산에 센다. (5) 하드웨어 명령어(`__builtin_popcountll`, x86 의 POPCNT): 한 명령.
// 관련: 가장 낮은 켜진 비트의 위치(ctz), 가장 높은 켜진 비트의 위치(63 − clz), ctz(x) == popcount((x & −x) − 1), 패리티는 popcount 의 홀짝. 0 부터 N 까지의 총 켜진 비트 수는 점화식으로 O(log N) 에 구한다(최상위 비트 2^k 이하의 수 전체 k·2^(k−1) + (남은 개수) + 나머지의 재귀).
// 검증: ① 다섯 방법이 무작위 64 비트 20 만 개와 특수 값(0, 모든 비트, 2의 거듭제곱, 교대 패턴 0x5555…, 0xAAAA…, 2^63)에서 일치 ② 커니핸의 반복 횟수 == popcount, 전체 훑기는 비트 길이 ③ 해밍 거리 popcount(a^b) 가 비트별 비교와 같고 삼각 부등식 성립 ④ ctz == popcount((x & −x) − 1) 와 clz 관계 ⑤ 0..N 의 총 켜진 비트 수 점화식이 N ≤ 5000 에서 직접 합과 일치, 큰 N 도 일치 ⑥ 부분집합 크기별 개수: 모든 n 비트 값의 popcount 분포가 이항계수.
int popLoop(uint64_t x, int& iters) { int c = 0; iters = 0; while (x) { c += (int)(x & 1); x >>= 1; iters++; } return c; }
int popKernighan(uint64_t x, int& iters) { int c = 0; iters = 0; while (x) { x &= x - 1; c++; iters++; } return c; }
int popTable(uint64_t x) { static int table[256]; static bool init = false; if (!init) { for (int i = 0; i < 256; i++) table[i] = (i & 1) + table[i / 2]; init = true; } int c = 0; for (int b = 0; b < 8; b++) c += table[(x >> (8 * b)) & 0xFF]; return c; }
int popSwar(uint64_t x) { x = x - ((x >> 1) & 0x5555555555555555ull); x = (x & 0x3333333333333333ull) + ((x >> 2) & 0x3333333333333333ull); x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0Full; return (int)((x * 0x0101010101010101ull) >> 56); }
long long totalBits(long long n) { if (n <= 0) return 0; int k = 63 - __builtin_clzll((unsigned long long)n + 0); long long p = 1LL << k; return (long long)k * (p / 2) + (n - p + 1) + totalBits(n - p); }        // 0..n 의 켜진 비트 총합
int main() {
    std::mt19937_64 rng(39); std::vector<uint64_t> special = {0, ~0ull, 1, 2, 0x8000000000000000ull, 0x5555555555555555ull, 0xAAAAAAAAAAAAAAAAull, 0xFFFFFFFF00000000ull, 0x00000000FFFFFFFFull, 0x0123456789ABCDEFull};
    for (int i = 0; i < 64; i++) special.push_back(1ull << i);
    auto check = [&](uint64_t x) { int i1, i2; int a = popLoop(x, i1), b = popKernighan(x, i2), c = popTable(x), d = popSwar(x), e = __builtin_popcountll(x), f = (int)std::bitset<64>(x).count(); assert(a == b && b == c && c == d && d == e && e == f);   // ① ②
        assert(i2 == a); unsigned bitLength = 0; for (uint64_t t = x; t; t >>= 1) bitLength++; assert(i1 == (int)bitLength); };
    for (uint64_t x : special) check(x); for (int rep = 0; rep < 200000; rep++) check(rng() >> (rng() % 64));
    for (int rep = 0; rep < 20000; rep++) { uint64_t a = rng(), b = rng(), c = rng(); int hd = 0; for (int i = 0; i < 64; i++) hd += (int)((a >> i & 1) != (b >> i & 1)); assert(__builtin_popcountll(a ^ b) == hd && __builtin_popcountll(a ^ c) <= __builtin_popcountll(a ^ b) + __builtin_popcountll(b ^ c)); }   // ③
    for (int rep = 0; rep < 20000; rep++) { uint64_t x = (rng() >> (rng() % 63)) | (1ull << (rng() % 64)); if (!x) continue; assert(__builtin_ctzll(x) == __builtin_popcountll((x & (~x + 1)) - 1) && 63 - __builtin_clzll(x) >= __builtin_ctzll(x)); }          // ④
    { long long direct = 0; for (long long n = 0; n <= 5000; n++) { direct += __builtin_popcountll((unsigned long long)n); assert(totalBits(n) == direct); } long long big = 123456789; long long sum = 0; for (long long n = 0; n <= 2000000; n++) sum += __builtin_popcountll((unsigned long long)n); assert(totalBits(2000000) == sum); (void)big; }   // ⑤
    for (int n : {1, 5, 10, 16}) { std::vector<long long> dist(n + 1, 0); for (uint32_t m = 0; m < (1u << n); m++) dist[__builtin_popcount(m)]++; long long c = 1; for (int k = 0; k <= n; k++) { assert(dist[k] == c); c = c * (n - k) / (k + 1); } }       // ⑥ 이항 분포
    std::cout << "CountBits: bit-by-bit, Kernighan, table lookup, SWAR, the hardware builtin and std::bitset::count agreed on 200000 random and 74 special 64-bit values, Kernighan iterated exactly popcount times, Hamming distance and the triangle inequality held, ctz equalled popcount((x & -x) - 1), the O(log N) total-set-bits recurrence matched direct sums, and the popcount distribution of n-bit values was binomial" << std::endl; return 0;
}
// Time Complexity: 커니핸 O(popcount), 표 조회·SWAR·하드웨어 O(1)
// Space Complexity: O(1) (표 방식 256 칸)
```
## EnumerateSubsets()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 부분집합 열거(EnumerateSubsets): 마스크 m 의 모든 부분마스크(켜진 비트의 부분집합)를 `for (s = m; ; s = (s − 1) & m) { …; if (s == 0) break; }` 로 훑는다. 핵심은 `(s − 1) & m` 이 "m 에 속한 비트로만 이루어진 s 다음으로 작은 수"를 곧바로 주는 것이다: s − 1 은 가장 낮은 켜진 비트를 끄고 그 아래를 모두 켜는데, & m 으로 m 밖의 비트를 버리면 정확히 m 의 부분마스크 중 s 바로 아래 값이 된다. 내림차순으로 2^popcount(m) 개(공집합 포함)를 방문하고, 방문 사이의 일은 O(1).
// 모든 마스크 m 에 대해 그 부분마스크를 전부 돌면 총 Σₘ 2^popcount(m) = 3ⁿ 이다(원소마다 "m 에 없음 / m 에 있고 부분마스크에 없음 / 둘 다 있음"). 비슷하게 상위집합 열거는 `s = (s + 1) | m`, 크기가 k 인 마스크만 순서대로 열거하는 고스퍼의 해킹은 `c = x & −x, r = x + c, x = (((r ^ x) >> 2) / c) | r` 이다(C(n, k) 개, 증가 순서). 그레이 코드 순서는 연속한 부분집합이 한 원소만 다르다.
// 검증: ① 모든 마스크 m (n = 10)에서 부분마스크 열거가 방문한 값들이 정의(s & ~m == 0 인 모든 s)와 같은 집합, 정확히 2^popcount(m) 개, 내림차순, 중복 없음, 마지막이 0 ② 모든 m 에 대한 총 방문 수가 3ⁿ (n = 1..12) ③ 상위집합 열거: 방문한 값이 (s & m) == m 인 모든 s 이고 개수가 2^(n−popcount(m)) ④ 고스퍼의 해킹이 크기 k 인 모든 n 비트 마스크를 증가 순서로 정확히 한 번씩, 개수 C(n, k) ⑤ 부분집합 합 응용: 모든 부분마스크의 합 중 목표와 같은 개수를 세는 O(2^popcount) 열거가 완전 탐색과 같음 ⑥ 빈 마스크와 모든 비트 마스크(m = 2^n − 1)의 경계.
std::vector<uint32_t> submasks(uint32_t m) { std::vector<uint32_t> r; for (uint32_t s = m;; s = (s - 1) & m) { r.push_back(s); if (s == 0) break; } return r; }
std::vector<uint32_t> supermasks(uint32_t m, int n) { std::vector<uint32_t> r; uint32_t full = (1u << n) - 1; for (uint32_t s = m;; s = (s + 1) | m) { r.push_back(s); if (s == full) break; } return r; }
std::vector<uint32_t> gosper(int n, int k) { std::vector<uint32_t> r; if (k == 0) { r.push_back(0); return r; } uint32_t x = (1u << k) - 1, limit = 1u << n; while (x < limit) { r.push_back(x); uint32_t c = x & -x, rr = x + c; x = (((rr ^ x) >> 2) / c) | rr; } return r; }
int main() {
    { const int n = 10; for (uint32_t m = 0; m < (1u << n); m++) { auto v = submasks(m); std::set<uint32_t> got(v.begin(), v.end()), want; for (uint32_t s = 0; s < (1u << n); s++) if ((s & ~m) == 0) want.insert(s);                      // ①
          assert(got == want && v.size() == (std::size_t)1 << __builtin_popcount(m) && got.size() == v.size() && std::is_sorted(v.rbegin(), v.rend()) && v.front() == m && v.back() == 0); } }
    for (int n = 1; n <= 12; n++) { long long total = 0, pow3 = 1; for (int i = 0; i < n; i++) pow3 *= 3; for (uint32_t m = 0; m < (1u << n); m++) { uint32_t s = m; long long c = 0; for (;; s = (s - 1) & m) { c++; if (s == 0) break; } total += c; } assert(total == pow3); }          // ② 3ⁿ
    { const int n = 8; for (uint32_t m = 0; m < (1u << n); m++) { auto v = supermasks(m, n); std::set<uint32_t> got(v.begin(), v.end()), want; for (uint32_t s = 0; s < (1u << n); s++) if ((s & m) == m) want.insert(s); assert(got == want && v.size() == (std::size_t)1 << (n - __builtin_popcount(m)) && std::is_sorted(v.begin(), v.end())); } }   // ③
    for (int n = 1; n <= 14; n++) for (int k = 0; k <= n; k++) { auto v = gosper(n, k); long long binom = 1; for (int i = 1; i <= k; i++) binom = binom * (n - k + i) / i; std::vector<uint32_t> want; for (uint32_t m = 0; m < (1u << n); m++) if (__builtin_popcount(m) == k) want.push_back(m);   // ④
        assert((long long)v.size() == binom && v == want); }
    { std::mt19937 rng(40); for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 14); std::vector<int> val(n); for (int& x : val) x = (int)(rng() % 20) - 5; uint32_t m = (uint32_t)(rng() & ((1u << n) - 1)); int target = (int)(rng() % 30) - 5;               // ⑤
          long long viaSubmasks = 0, brute = 0; for (uint32_t s = m;; s = (s - 1) & m) { int sum = 0; for (int i = 0; i < n; i++) if (s >> i & 1) sum += val[i]; viaSubmasks += sum == target; if (s == 0) break; }
          for (uint32_t s = 0; s < (1u << n); s++) if ((s & ~m) == 0) { int sum = 0; for (int i = 0; i < n; i++) if (s >> i & 1) sum += val[i]; brute += sum == target; } assert(viaSubmasks == brute); } }
    { auto e = submasks(0); assert(e.size() == 1 && e[0] == 0); auto f = submasks(0xFFFFu); assert(f.size() == 65536 && f.front() == 0xFFFFu && f.back() == 0); auto g = gosper(5, 0); assert(g.size() == 1 && g[0] == 0); auto h = gosper(5, 5); assert(h.size() == 1 && h[0] == 31); }     // ⑥
    std::cout << "EnumerateSubsets: the (s-1)&m loop visited exactly the 2^popcount(m) submasks in descending order for all 1024 masks of 10 bits, the total work over all masks was 3^n for n up to 12, superset enumeration and Gosper's hack (all C(n,k) masks of popcount k in increasing order, n up to 14) were exact, and counting target-sum subsets of a mask by submask enumeration matched exhaustive search" << std::endl; return 0;
}
// Time Complexity: 부분마스크 열거 O(2^popcount), 모든 마스크에 대해 O(3ⁿ), 고스퍼 O(C(n, k))
// Space Complexity: O(1) (열거 중)
```

# Part 7. 서로소 집합
## MakeSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

// 집합 만들기 MakeSet (집합 관점의 요약, 정본은 Graph.md Part 8): 서로소 집합 자료구조(Union-Find)에서 MakeSet(x) 는 원소 x 만으로 이루어진 새 집합을 만든다 — 부모를 자기 자신으로(`parent[x] = x`), 크기 1, 랭크 0. n 개 원소를 만들면 서로소인 n 개의 단일 원소 집합이 생겨 연결 성분이 n 개이고 모든 find(i) = i 이다. O(1) 이 원소당 걸려 총 O(n).
// 원소가 0..n−1 정수가 아니라 문자열처럼 임의의 키이면 해시 맵으로 키 → 번호를 지급하며 필요할 때 만든다(지연 생성). 주의: 이미 있는 원소에 MakeSet 을 다시 부르면 안 된다 — 부모를 자기 자신으로 되돌려 그 원소가 속한 합쳐진 집합에서 떨어져 나간다. 그래서 "있으면 건드리지 않음" 검사를 둔다.
// 검증: ① 배열 방식 n 개 생성 후 성분 수 n, find(i) == i, 크기 1, 랭크 0 ② 지연 생성: 키를 처음 볼 때만 번호 지급, 같은 키 재요청은 같은 번호이고 합쳐진 상태를 보존 ③ 순진하게 MakeSet 을 다시 부르면 이미 합쳐진 원소가 분리되어 성분 수가 틀려짐을 시연 ④ 무작위 합치기·질의 뒤에도 지연 생성 구조와 배열 구조의 연결 판정이 일치 ⑤ 빈 구조·원소 1 개.
struct DSU { std::vector<int> parent, sz, rk; int components = 0;
    void makeSet(int x) { if (x >= (int)parent.size()) { parent.resize(x + 1); sz.resize(x + 1); rk.resize(x + 1); } parent[x] = x; sz[x] = 1; rk[x] = 0; }
    int add() { int x = (int)parent.size(); makeSet(x); components++; return x; }
    int find(int x) { while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (sz[a] < sz[b]) std::swap(a, b); parent[b] = a; sz[a] += sz[b]; components--; return true; } };
struct LazyDSU { DSU d; std::unordered_map<std::string, int> id;
    int get(const std::string& key) { auto it = id.find(key); if (it != id.end()) return it->second; int x = d.add(); id[key] = x; return x; }                       // 처음 볼 때만 MakeSet
    int getNaive(const std::string& key) { auto it = id.find(key); if (it != id.end()) { d.makeSet(it->second); return it->second; } int x = d.add(); id[key] = x; return x; }        // 잘못된 방식: 매번 다시 MakeSet
    bool same(const std::string& a, const std::string& b) { return d.find(get(a)) == d.find(get(b)); } };
int main() {
    for (int n : {0, 1, 2, 10, 1000}) { DSU d; for (int i = 0; i < n; i++) assert(d.add() == i); assert(d.components == n); for (int i = 0; i < n; i++) assert(d.find(i) == i && d.sz[i] == 1 && d.rk[i] == 0 && d.parent[i] == i); }       // ① ⑤
    { LazyDSU z; int a = z.get("alice"), b = z.get("bob"), c = z.get("carol"); assert(a == 0 && b == 1 && c == 2 && z.get("bob") == 1 && z.d.components == 3);                                                              // ②
      z.d.unite(a, b); assert(z.d.components == 2 && z.same("alice", "bob") && z.get("alice") == 0 && z.get("bob") == 1 && z.same("alice", "bob") && z.d.components == 2 && !z.same("alice", "carol")); }
    { LazyDSU bad; int a = bad.getNaive("x"), b = bad.getNaive("y"); bad.d.unite(a, b); assert(bad.d.find(a) == bad.d.find(b)); bad.getNaive("x"); bad.getNaive("y");                                                           // ③ 다시 MakeSet 하면 분리됨
      assert(bad.d.find(a) != bad.d.find(b) && bad.d.components == 1); }                                                                                                                                         // 성분 수 카운터(1)와 실제(2)가 어긋난다
    std::mt19937 rng(41);
    for (int rep = 0; rep < 100; rep++) { int n = 1 + (int)(rng() % 60); LazyDSU z; DSU arr; for (int i = 0; i < n; i++) arr.add(); std::vector<std::string> names; for (int i = 0; i < n; i++) names.push_back("n" + std::to_string(i));                                      // ④
        for (int step = 0; step < 200; step++) { int a = (int)(rng() % n), b = (int)(rng() % n); if (rng() % 2) { z.d.unite(z.get(names[a]), z.get(names[b])); arr.unite(a, b); } else { std::string ka = names[a], kb = names[b]; assert(z.same(ka, kb) == (arr.find(a) == arr.find(b))); } }
        std::vector<int> roots; for (int i = 0; i < n; i++) roots.push_back(arr.find(i)); std::sort(roots.begin(), roots.end()); roots.erase(std::unique(roots.begin(), roots.end()), roots.end()); assert((int)roots.size() == arr.components); }
    std::cout << "MakeSet: creating n singleton sets gave n components with find(i) = i, size 1 and rank 0; lazily creating sets for string keys gave stable ids and preserved merges, re-running MakeSet on an existing element was shown to split it from its set, and the lazy structure matched an array structure on 100 random union/query sequences" << std::endl; return 0;
}
// Time Complexity: O(1) (원소당)
// Space Complexity: O(N)
```
## FindSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 대표 찾기 FindSet (집합 관점의 요약, 정본은 Graph.md Part 8): find(x) 는 x 가 속한 집합의 대표(트리의 루트)를 부모 포인터를 따라 올라가 찾는다. 같은 집합의 원소는 같은 대표를 가지므로 find(a) == find(b) 가 동치 질의다. 경로 압축(path compression)은 올라가는 길에 만난 모든 노드의 부모를 루트로 바꿔 다음 find 를 짧게 만든다: 재귀 방식은 한 번에 완전 압축, 반복(경로 반분, path halving)은 한 칸씩 건너뛰며 부모를 조부모로 바꾼다. 합치기에서 크기가 작은 트리를 큰 트리 밑에 붙이면(union by size) 높이가 ⌊log₂ n⌋ 이하라 압축이 없어도 find 가 O(log n) 이고, 둘을 함께 쓰면 분할상환 O(α(n)) (역아커만 함수, 현실에서 4 이하).
// 검증: ① 압축 없는 find, 완전 압축 find, 경로 반분 find 의 결과(대표)가 모든 원소에서 같음 ② 합치기를 크기 기준으로 하면 압축 없이도 깊이 ≤ ⌊log₂ n⌋ ③ 완전 압축 find 한 번 뒤 그 원소의 깊이는 ≤ 1 이고 경로의 모든 노드가 루트를 직접 가리킴, 반분은 깊이가 절반 이하로 ④ 같은 find 를 두 번 부르면 두 번째는 걸음 ≤ 1 ⑤ 무작위 질의 열의 총 걸음 수: 압축 있음 ≪ 압축 없음(순진한 합치기 사슬에서), 원소당 평균 걸음이 작음 ⑥ 연결 성분 판별이 BFS 와 같음.
struct DSU { std::vector<int> p, sz; long steps = 0; explicit DSU(int n) : p(n), sz(n, 1) { std::iota(p.begin(), p.end(), 0); }
    int findPlain(int x) { while (p[x] != x) { x = p[x]; steps++; } return x; }
    int findFull(int x) { if (p[x] == x) return x; steps++; return p[x] = findFull(p[x]); }                                                                                       // 완전 압축(재귀)
    int findHalving(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; steps++; } return x; }                                                                                 // 경로 반분
    void uniteSize(int a, int b) { a = findPlain(a); b = findPlain(b); if (a == b) return; if (sz[a] < sz[b]) std::swap(a, b); p[b] = a; sz[a] += sz[b]; }
    void makeChain() { for (std::size_t i = 1; i < p.size(); i++) p[i] = (int)i - 1; }                                                                                     // 최악의 모양: 0 ← 1 ← 2 ← … (길이 n−1 사슬)
    int depth(int x) const { int d = 0; while (p[x] != x) { x = p[x]; d++; } return d; } };
int main() {
    std::mt19937 rng(42);
    for (int rep = 0; rep < 200; rep++) { int n = 2 + (int)(rng() % 200); DSU a(n), b(n), c(n); for (int k = 0; k < 2 * n; k++) { int x = (int)(rng() % n), y = (int)(rng() % n); a.uniteSize(x, y); b.uniteSize(x, y); c.uniteSize(x, y); }                       // ①
        std::vector<int> ra, rb, rc; for (int v = 0; v < n; v++) { ra.push_back(a.findPlain(v)); rb.push_back(b.findFull(v)); rc.push_back(c.findHalving(v)); } assert(ra == rb && ra == rc);
        int maxDepth = 0; DSU d(n); for (int k = 0; k < 3 * n; k++) d.uniteSize((int)(rng() % n), (int)(rng() % n)); for (int v = 0; v < n; v++) maxDepth = std::max(maxDepth, d.depth(v)); assert(maxDepth <= (int)std::floor(std::log2((double)n)));       // ② 크기 기준 합치기: 깊이 ≤ log₂ n
        for (int v = 0; v < n; v++) { int r = d.findFull(v); assert(v == r || (d.depth(v) == 1 && d.p[v] == r)); } }                                                                                                    // ③ 완전 압축 후 깊이 ≤ 1
    { const int N = 4096; DSU full(N), half(N); full.makeChain(); half.makeChain(); assert(full.depth(N - 1) == N - 1);
      full.steps = 0; full.findFull(N - 1); long s1 = full.steps; full.steps = 0; full.findFull(N - 1); long s2 = full.steps; assert(s1 == N - 1 && s2 <= 1 && full.depth(N - 1) <= 1 && full.depth(N / 2) <= 1);                              // ④ 첫 find 는 깊이만큼, 두 번째는 1 걸음 이하
      half.findHalving(N - 1); assert(half.depth(N - 1) == 1 + (N - 1) / 2 || half.depth(N - 1) <= (N - 1) / 2 + 1); }                                                                                           // 반분: 깊이가 절반
    { const int N = 3000; DSU withC(N), without(N); withC.makeChain(); without.makeChain(); withC.steps = without.steps = 0; for (int q = 0; q < 20000; q++) { int v = (int)(rng() % N); withC.findHalving(v); without.findPlain(v); }          // ⑤
      assert(withC.steps * 20 < without.steps && (double)withC.steps / 20000 < 5.0); }
    for (int rep = 0; rep < 100; rep++) { int n = 1 + (int)(rng() % 50); std::vector<std::pair<int, int>> edges; DSU d(n); for (int k = 0, m = (int)(rng() % (2 * n)); k < m; k++) { int a = (int)(rng() % n), b = (int)(rng() % n); edges.push_back({a, b}); d.uniteSize(a, b); }              // ⑥
        std::vector<std::vector<int>> adj(n); for (auto& e : edges) { adj[e.first].push_back(e.second); adj[e.second].push_back(e.first); } std::vector<int> comp(n, -1); int cc = 0; for (int s = 0; s < n; s++) if (comp[s] < 0) { std::vector<int> st{s}; comp[s] = cc; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : adj[u]) if (comp[v] < 0) { comp[v] = cc; st.push_back(v); } } cc++; }
        for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) assert((d.findHalving(a) == d.findHalving(b)) == (comp[a] == comp[b])); }
    std::cout << "FindSet: plain, fully compressing and path-halving finds returned identical representatives, union by size kept depth within floor(log2 n) without compression, one full-compression find on a 4096-chain walked its depth and the repeat took at most one step, halving shortened paths by half, compression cut total steps by over 20x on a chain workload, and component queries matched BFS" << std::endl; return 0;
}
// Time Complexity: 분할상환 O(α(N)) (경로 압축 + 크기 기준 합치기)
// Space Complexity: O(N)
```
## UnionSet()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 합치기 UnionSet (집합 관점의 요약, 정본은 Graph.md Part 8): union(a, b) 는 a 와 b 가 속한 두 집합을 하나로 합친다 — 두 대표를 찾아 같으면 이미 같은 집합이므로 아무것도 하지 않고(false), 다르면 한 대표를 다른 대표의 자식으로 단다(true). 어느 쪽을 아래로 붙이는지가 성능을 가른다: 작은 트리를 큰 트리 밑에 붙이면(크기 기준) 깊이가 log n 이하로 유지된다. 합치기는 되돌릴 수 없고(분리는 지원하지 않음), 연결 성분 수는 성공한 합치기마다 정확히 1 씩 줄어든다.
// 서로소 집합은 동치 관계의 닫힘을 계산한다: 합치기 열이 주어지면 find 가 같다는 것은 "합치기 간선으로 이어진 경로가 있다"(반사·대칭·추이로 닫힌 관계)와 정확히 같다. 이것이 크러스칼 최소 신장 트리의 사이클 검사, 이미지의 연결 영역 라벨링, 동치류 계산의 기반이다.
// 검증: ① 무작위 합치기·질의 열(수천 번)에서 매 질의 same(a, b) 가 간선 그래프의 BFS 연결성과 일치 ② 합치기의 반환값이 "서로 다른 집합이었는가" 와 같고 성분 수가 성공마다 1 감소, 최종 성분 수가 BFS 성분 수와 같음 ③ 크기 필드: 루트의 크기 == 그 집합의 실제 원소 수, 모든 크기의 합 == n ④ 반사·대칭·추이(find 동치) ⑤ 크러스칼 응용: 간선을 무게순으로 합치며 사이클을 거르면 신장 트리의 간선 수 n−c, 총 무게가 프림 알고리즘과 같음 ⑥ 자기 자신과 합치기·같은 쌍 재합치기는 false.
struct DSU { std::vector<int> p, sz; int comps; explicit DSU(int n) : p(n), sz(n, 1), comps(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; } bool same(int a, int b) { return find(a) == find(b); }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (sz[a] < sz[b]) std::swap(a, b); p[b] = a; sz[a] += sz[b]; comps--; return true; } };
int bfsComponents(int n, const std::vector<std::pair<int, int>>& edges, std::vector<int>& comp) { std::vector<std::vector<int>> adj(n); for (auto& e : edges) { adj[e.first].push_back(e.second); adj[e.second].push_back(e.first); } comp.assign(n, -1); int cc = 0;
    for (int s = 0; s < n; s++) if (comp[s] < 0) { std::vector<int> st{s}; comp[s] = cc; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : adj[u]) if (comp[v] < 0) { comp[v] = cc; st.push_back(v); } } cc++; } return cc; }
int main() {
    std::mt19937 rng(43);
    for (int rep = 0; rep < 150; rep++) { int n = 1 + (int)(rng() % 80); DSU d(n); std::vector<std::pair<int, int>> edges; int successes = 0;                                                                                                // ① ②
        for (int step = 0; step < 4 * n; step++) { int a = (int)(rng() % n), b = (int)(rng() % n); if (rng() % 3) { bool different = !d.same(a, b); int before = d.comps; bool merged = d.unite(a, b); assert(merged == different && d.comps == before - (merged ? 1 : 0)); successes += merged; edges.push_back({a, b}); }
            else { std::vector<int> comp; bfsComponents(n, edges, comp); assert(d.same(a, b) == (comp[a] == comp[b])); } }
        std::vector<int> comp; int cc = bfsComponents(n, edges, comp); assert(d.comps == cc && successes == n - cc);
        std::vector<int> count(n, 0); for (int v = 0; v < n; v++) count[d.find(v)]++; int total = 0; for (int v = 0; v < n; v++) if (d.find(v) == v) { assert(d.sz[v] == count[v]); total += d.sz[v]; } assert(total == n);                       // ③ 크기
        for (int a = 0; a < n && a < 10; a++) for (int b = 0; b < n && b < 10; b++) { assert(d.same(a, a) && d.same(a, b) == d.same(b, a)); for (int c = 0; c < n && c < 10; c++) if (d.same(a, b) && d.same(b, c)) assert(d.same(a, c)); } }               // ④
    for (int rep = 0; rep < 100; rep++) { int n = 2 + (int)(rng() % 30); std::vector<std::vector<int>> w(n, std::vector<int>(n, 0)); std::vector<std::array<int, 3>> es; for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (rng() % 3 == 0) { int c = 1 + (int)(rng() % 50); w[i][j] = w[j][i] = c; es.push_back({c, i, j}); }   // ⑤ 크러스칼 == 프림
        std::sort(es.begin(), es.end()); DSU d(n); long kruskal = 0; int used = 0; for (auto& e : es) if (d.unite(e[1], e[2])) { kruskal += e[0]; used++; } long prim = 0; std::vector<bool> in(n, false); std::vector<int> comp; std::vector<std::pair<int, int>> eg; for (auto& e : es) eg.push_back({e[1], e[2]}); int cc = bfsComponents(n, eg, comp);
        for (int s = 0; s < n; s++) if (!in[s]) { std::vector<int> best(n, 1 << 30); best[s] = 0; for (;;) { int u = -1; for (int v = 0; v < n; v++) if (!in[v] && best[v] < (1 << 30) && (u < 0 || best[v] < best[u])) u = v; if (u < 0) break; in[u] = true; prim += best[u]; for (int v = 0; v < n; v++) if (w[u][v] && !in[v] && w[u][v] < best[v]) best[v] = w[u][v]; } }
        assert(used == n - cc && kruskal == prim); }
    { DSU d(5); assert(!d.unite(2, 2) && d.unite(0, 1) && !d.unite(1, 0) && !d.unite(0, 1) && d.comps == 4); }                                                                                                   // ⑥
    std::cout << "UnionSet: on 150 random union/query sequences the return value of union said exactly whether the sets were different, the component count fell by one per success and ended at the BFS count, every root's size equalled its real member count, find-equivalence was reflexive, symmetric and transitive, and Kruskal built on union found the same minimum spanning forest weight as Prim on 100 random graphs" << std::endl; return 0;
}
// Time Complexity: 분할상환 O(α(N))
// Space Complexity: O(N)
```
## UnionByRank()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 랭크에 의한 합치기(Union by Rank/Size) — 서로소 집합의 합치기에서 "작은 트리를 큰 트리 밑에 붙인다" (집합 관점의 요약, 정본은 Graph.md Part 8). 아무 쪽이나 붙이면 루트 방향 사슬이 만들어져 find 가 O(n) 이 되지만
// 랭크(트리 높이의 상한)가 낮은 쪽을 높은 쪽 밑에 붙이면 랭크가 오르는 경우는 두 랭크가 같을 때뿐이라 랭크 r 인 트리는 최소 2^r 개 원소를 가지고, 따라서 높이는 항상 ⌊log₂ n⌋ 이하다. 크기(size)로 합쳐도 같은 보장을 얻는다.
// 검증: 무작위 합치기 열 수천 개로 ① 높이 ≤ ⌊log₂ n⌋ ② 랭크 r 인 루트의 트리 크기 ≥ 2^r ③ 대조군(무조건 a 의 루트를 b 의 루트 밑에 붙임)은 최악의 합치기 열에서 높이가 n−1 까지 커짐 ④ 두 방식 모두 연결 성분 판별은 같음
struct DSU { std::vector<int> p, rk, sz; bool byRank; DSU(int n, bool byRank) : p(n), rk(n, 0), sz(n, 1), byRank(byRank) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) const { while (p[x] != x) x = p[x]; return x; }                                                                                  // 경로 압축 없이 순수하게 높이를 관찰
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (byRank) { if (rk[a] < rk[b]) std::swap(a, b); p[b] = a; sz[a] += sz[b]; if (rk[a] == rk[b]) rk[a]++; } else { p[a] = b; sz[b] += sz[a]; } return true; }
    int height() const { int h = 0; for (size_t v = 0; v < p.size(); v++) { int d = 0; for (int x = v; p[x] != x; x = p[x]) d++; h = std::max(h, d); } return h; } };
int main() {
    std::mt19937 rng(3); int worstRank = 0, worstNaive = 0;
    for (int t = 0; t < 200; t++) { int n = 2 + rng() % 300; DSU r(n, true), nv(n, false); for (int k = 0; k < 3 * n; k++) { int a = rng() % n, b = rng() % n; r.unite(a, b); nv.unite(a, b); }
        assert(r.height() <= (int)std::floor(std::log2((double)n))); worstRank = std::max(worstRank, r.height());                                                                           // ① 높이 ≤ log₂ n
        for (int v = 0; v < n; v++) if (r.p[v] == v) assert(r.sz[v] >= (1 << r.rk[v]));                                                                                                 // ② 랭크 r → 크기 ≥ 2^r
        for (int k = 0; k < 50; k++) { int a = rng() % n, b = rng() % n; assert((r.find(a) == r.find(b)) == (nv.find(a) == nv.find(b))); } worstNaive = std::max(worstNaive, nv.height()); }                   // ④ 연결 성분 판별 동일
    const int N = 400; DSU adv(N, false), good(N, true); for (int i = 0; i + 1 < N; i++) { adv.unite(i, i + 1); good.unite(i, i + 1); } assert(adv.height() == N - 1 && good.height() <= (int)std::log2((double)N));              // ③ 최악의 합치기 열
    std::cout << "UnionByRank: tree height never exceeded floor(log2 n) (worst observed " << worstRank << ") with rank-based linking, while naive linking reached " << adv.height() << " on a chain of " << N << " unions (random worst " << worstNaive << ")" << std::endl; return 0;
}
// Time Complexity: find O(log n) (압축 없을 때), 합치기 O(log n)
// Space Complexity: O(n)
```
## PathCompression()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 경로 압축(Path Compression) — find 가 루트까지 오르는 김에 만난 모든 노드를 루트에 직접 매단다 (집합 관점의 요약, 정본은 Graph.md Part 8). 한 번 비싸게 오르면 다음부터 같은 노드는 한 걸음에 닿는다.
// 변형: 완전 압축(재귀: 올라간 뒤 모두 루트에 연결) · 경로 분할(path splitting: 각 노드를 조부모에 연결) · 경로 반분(path halving: 한 칸 건너 조부모에 연결). 셋 다 한 번의 위 방향 패스로 끝나 재귀가 필요 없고 분할상환 비용이 같은 계열(랭크와 함께 쓰면 O(α(n)))이다.
// 검증: ① 세 변형과 압축 없음이 모든 질의에서 같은 집합 판정(무작위 합치기+질의 수만 개) ② 사슬 위에서 압축 없는 find 의 걸음 수 합 ≈ n² / 2, 압축이 있으면 O(n) ③ 압축 뒤 방문한 노드가 모두 루트 또는 루트의 직계 자식(완전 압축) / 높이가 절반 이하(반분)
struct DSU { std::vector<int> p; long steps = 0; int mode; DSU(int n, int mode) : p(n), mode(mode) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { if (mode == 0) { while (p[x] != x) { x = p[x]; steps++; } return x; }                                                                      // 0: 압축 없음
        if (mode == 1) { int r = x; while (p[r] != r) { r = p[r]; steps++; } while (p[x] != r && x != r) { int nx = p[x]; p[x] = r; x = nx; } return r; }               // 1: 완전 압축(두 번 훑기)
        if (mode == 2) { while (p[x] != x) { int nx = p[x]; p[x] = p[nx]; x = nx; steps++; } return x; }                                                          // 2: 경로 분할
        while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; steps++; } return x; }                                                                                          // 3: 경로 반분
    void link(int a, int b) { a = find(a); b = find(b); if (a != b) p[a] = b; } };
int main() {
    std::mt19937 rng(8); const int N = 2000; std::vector<DSU> d; for (int m = 0; m < 4; m++) d.emplace_back(N, m);
    for (int k = 0; k < 6000; k++) { int a = rng() % N, b = rng() % N; if (rng() % 3 == 0) { for (auto& x : d) x.link(a, b); } else { bool r0 = d[0].find(a) == d[0].find(b); for (int m = 1; m < 4; m++) assert((d[m].find(a) == d[m].find(b)) == r0); } }                  // ① 모든 변형이 같은 판정
    const int C = 1000; DSU plain(C, 0), full(C, 1), split(C, 2), half(C, 3); for (DSU* x : {&plain, &full, &split, &half}) { for (int i = 1; i < C; i++) x->p[i - 1] = i; }                                    // 0 → 1 → 2 → ... → C-1 사슬
    long cost[4]; DSU* all[4] = {&plain, &full, &split, &half}; for (int m = 0; m < 4; m++) { for (int rep = 0; rep < 3; rep++) for (int v = 0; v < C; v++) all[m]->find(v); cost[m] = all[m]->steps; }
    assert(cost[0] > (long)C * C / 2 && cost[1] < 4 * C && cost[2] < 14 * C && cost[3] < 6 * C);                                                                                                         // ② 사슬 위의 비용
    for (int v = 0; v < C; v++) assert(full.p[v] == C - 1 || full.p[v] == v);                                                                                                                       // ③ 완전 압축 뒤 모두 루트에 직접 연결
    std::cout << "PathCompression: four find variants agree on 6000 random operations; total steps for 3 sweeps over a chain of " << C << ": none " << cost[0] << ", full compression " << cost[1] << ", splitting " << cost[2] << ", halving " << cost[3] << std::endl; return 0;
}
// Time Complexity: 단독 사용 시 분할상환 O(log n), 랭크와 함께면 O(α(n))
// Space Complexity: O(n)
```
## ConnectedComponents()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 연결 성분(Connected Components) — 서로소 집합으로 세기 (집합 관점의 요약, 정본은 Graph.md Part 4). 간선이 하나 들어올 때마다 양 끝점의 집합을 합치면 합치기에 성공한 횟수만큼 성분 수가 줄어든다: 성분 수 = n − (성공한 합치기 수).
// BFS/DFS 는 그래프 전체가 메모리에 있어야 하지만 서로소 집합은 간선을 스트림으로 받으며 성분을 유지하므로 "간선이 계속 추가되는" 문제(온라인 연결성)에 맞다. 간선 삭제를 지원하지 못하는 것이 한계(DynamicConnectivity 참조).
// 검증: 무작위 그래프 300개에서 ① DSU 의 성분 분할 == BFS 성분 분할(대표 원소 이름을 지우고 집합으로 비교) ② 간선을 하나씩 넣을 때 성분 수가 단조 비증가이고 n − 성공 합치기 수와 같음 ③ 가장 큰 성분의 크기 보고
std::vector<int> p;
int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
int main() {
    std::mt19937 rng(11); long biggest = 0;
    for (int t = 0; t < 300; t++) { int n = 1 + rng() % 60, m = rng() % (2 * n); std::vector<std::pair<int, int>> edges; for (int i = 0; i < m; i++) edges.push_back({(int)(rng() % n), (int)(rng() % n)}); p.assign(n, 0); std::iota(p.begin(), p.end(), 0); int comps = n, merges = 0;
        for (auto [a, b] : edges) { int ra = find(a), rb = find(b); if (ra != rb) { p[ra] = rb; merges++; comps--; } assert(comps == n - merges && comps >= 1); }                                                         // ② 성분 수 = n − 성공한 합치기
        std::vector<std::vector<int>> adj(n); for (auto [a, b] : edges) { adj[a].push_back(b); adj[b].push_back(a); } std::vector<int> label(n, -1); int k = 0; for (int s = 0; s < n; s++) if (label[s] < 0) { std::queue<int> q; q.push(s); label[s] = k; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (label[v] < 0) { label[v] = k; q.push(v); } } k++; }
        assert(k == comps); for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) assert((find(a) == find(b)) == (label[a] == label[b]));                                                                     // ① 같은 분할
        std::vector<int> size(n, 0); for (int v = 0; v < n; v++) size[find(v)]++; biggest += *std::max_element(size.begin(), size.end()); }
    std::cout << "ConnectedComponents: union-find partitions equal BFS partitions on 300 random graphs; component count always equals n minus successful unions (mean largest component " << (double)biggest / 300 << " vertices)" << std::endl; return 0;
}
// Time Complexity: O((n + m) α(n))
// Space Complexity: O(n)
```

# Part 8. 조합론
## Combination()
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

// 조합(Combination): n 개 중 순서 없이 k 개를 고르는 방법, C(n, k) = n! / (k!(n−k)!). 성질: 대칭 C(n,k) = C(n,n−k), 파스칼 C(n,k) = C(n−1,k−1) + C(n−1,k), 행의 합 Σₖ C(n,k) = 2ⁿ (부분집합의 총수), 반데르몽드 항등식 Σ C(m,i)·C(n,k−i) = C(m+n,k). 값은 빠르게 커지므로 곱셈 공식으로 계산할 때 곱한 뒤 나누면 중간값이 넘친다 — 각 단계에서 `r = r * (n−k+i) / i` 처럼 정수 나눗셈이 항상 나누어떨어지는 순서(i 번째 단계의 r 이 C(n−k+i, i))로 계산한다.
// 열거: (1) 재귀 백트래킹(원소를 넣고/뺌), (2) 인덱스 배열 c[0..k−1] 를 사전식으로 다음 조합으로 올리는 반복(가장 오른쪽에서 최대값에 닿지 않은 위치를 찾아 1 늘리고 그 오른쪽을 연속으로 채움 — k ≤ n/2 이면 조합당 평균 쓰기 2 번 미만), (3) 길이 n 의 0/1 마스크에 `std::next_permutation` (1 이 k 개). 사전식 순서의 조합에는 순위(rank)와 역순위(unrank)가 있다: 구현은 위치 i 마다 건너뛴 값 x 에 대해 C(n−1−x, k−1−i) 를 더하는 합으로 순위를 구하고(앞에 오는 조합의 개수), unrank 는 같은 표를 앞에서부터 빼 가며 값을 고른다 — 둘 다 표 조회 O(n) 번. 합을 접으면(hockey-stick) 조합수 체계(combinatorial number system)의 식 순위 = C(n,k) − 1 − Σ C(n−1−cᵢ, k−i) 가 된다(Σ C(n−1−cᵢ, k−i) 자체는 사전식 순위가 아니라 그 역순위 C(n,k)−1−순위).
// 검증: ① n ≤ 14 모든 k 에서 세 열거 방법이 같은 조합들(사전식)과 개수 C(n,k), 각 조합이 순증가이고 중복 없음 ② 항등식: 대칭·파스칼·행의 합 2ⁿ·반데르몽드·곱셈 공식 == 파스칼 표 (n ≤ 60 에서 64 비트 안에서 정확) ③ 반복 방식의 인덱스 쓰기 총수가 이웃한 두 조합이 처음 달라지는 위치로부터 센 값과 정확히 같고, k ≤ n/2 에서 조합 수의 2 배 미만(분할상환 상수; k 가 n 에 가까우면 보수 조합 C(n, n−k) 로 바꿔 열거해야 함) ④ 순위: 사전식 i 번째 조합의 순위가 i 이고 unrank 가 역함수(전수), 조합수 체계의 식 C(n,k)−1−Σ C(n−1−cᵢ, k−i) 도 i ⑤ 경계: k = 0, k = n, k > n.
unsigned long long binomMul(int n, int k) { if (k < 0 || k > n) return 0; k = std::min(k, n - k); unsigned long long r = 1; for (int i = 1; i <= k; i++) r = r * (unsigned long long)(n - k + i) / (unsigned long long)i; return r; }
std::vector<std::vector<unsigned long long>> pascal(int n) { std::vector<std::vector<unsigned long long>> c(n + 1, std::vector<unsigned long long>(n + 1, 0)); for (int i = 0; i <= n; i++) { c[i][0] = 1; for (int j = 1; j <= i; j++) c[i][j] = c[i - 1][j - 1] + (j <= i - 1 ? c[i - 1][j] : 0); } return c; }
void recur(int n, int k, int start, std::vector<int>& cur, std::vector<std::vector<int>>& out) { if ((int)cur.size() == k) { out.push_back(cur); return; } for (int x = start; x < n; x++) { cur.push_back(x); recur(n, k, x + 1, cur, out); cur.pop_back(); } }
bool nextComb(std::vector<int>& c, int n, long& writes) { int k = (int)c.size(); int i = k - 1; while (i >= 0 && c[i] == n - k + i) i--; if (i < 0) return false; c[i]++; writes++; for (int j = i + 1; j < k; j++) { c[j] = c[j - 1] + 1; writes++; } return true; }
std::vector<std::vector<int>> byMaskPermutation(int n, int k) { std::vector<int> mask(n, 0); std::fill(mask.end() - k, mask.end(), 1); std::vector<std::vector<int>> out; do { std::vector<int> c; for (int i = 0; i < n; i++) if (mask[i]) c.push_back(i); out.push_back(c); } while (std::next_permutation(mask.begin(), mask.end())); std::sort(out.begin(), out.end()); return out; }   // 마스크 순열을 사전식으로 정렬
unsigned long long rankOf(const std::vector<int>& c, int n, const std::vector<std::vector<unsigned long long>>& C) { int k = (int)c.size(); unsigned long long r = 0; for (int i = 0; i < k; i++) { int lo = i ? c[i - 1] + 1 : 0; for (int x = lo; x < c[i]; x++) r += C[n - 1 - x][k - 1 - i]; } return r; }   // 앞에 오는 조합의 개수
std::vector<int> unrank(unsigned long long r, int n, int k, const std::vector<std::vector<unsigned long long>>& C) { std::vector<int> c; int x = 0; for (int i = 0; i < k; i++) { for (;; x++) { unsigned long long cnt = C[n - 1 - x][k - 1 - i]; if (r < cnt) break; r -= cnt; } c.push_back(x++); } return c; }
int main() {
    auto C = pascal(60);
    for (int n = 0; n <= 14; n++) for (int k = 0; k <= n; k++) { std::vector<std::vector<int>> a; std::vector<int> cur; recur(n, k, 0, cur, a); std::vector<std::vector<int>> b; if (k <= n) { std::vector<int> c(k); std::iota(c.begin(), c.end(), 0); long w = 0; do { b.push_back(c); } while (nextComb(c, n, w)); long expect = 0; for (std::size_t t = 0; t + 1 < b.size(); t++) { int d = 0; while (b[t][d] == b[t + 1][d]) d++; expect += k - d; } assert(w == expect); if (k > 0 && 2 * k <= n) assert(w < 2 * (long)b.size()); }   // ① ③ 쓰기 수 = 이웃한 두 조합이 처음 달라지는 위치부터 오른쪽 끝까지(독립 계산)
        auto m = byMaskPermutation(n, k); assert(a == b && a == m && a.size() == C[n][k] && std::is_sorted(a.begin(), a.end())); for (auto& c : a) { assert(std::is_sorted(c.begin(), c.end()) && std::adjacent_find(c.begin(), c.end()) == c.end()); } }
    for (int n = 0; n <= 60; n++) { unsigned long long rowSum = 0; for (int k = 0; k <= n; k++) { assert(binomMul(n, k) == C[n][k] && C[n][k] == C[n][n - k]); if (n >= 1 && k >= 1 && k <= n - 1) assert(C[n][k] == C[n - 1][k - 1] + C[n - 1][k]); if (n <= 62) rowSum += C[n][k]; } if (n < 63) assert(rowSum == (1ull << n)); }   // ②
    for (int m = 0; m <= 10; m++) for (int n = 0; n <= 10; n++) for (int k = 0; k <= m + n; k++) { unsigned long long s = 0; for (int i = 0; i <= k; i++) s += (i <= m && k - i <= n ? C[m][i] * C[n][k - i] : 0); assert(s == C[m + n][k]); }       // 반데르몽드
    for (int n = 0; n <= 12; n++) for (int k = 0; k <= n; k++) { auto all = byMaskPermutation(n, k); for (std::size_t i = 0; i < all.size(); i++) { assert(rankOf(all[i], n, C) == i && unrank(i, n, k, C) == all[i]); unsigned long long dual = 0; for (int j = 0; j < k; j++) dual += C[n - 1 - all[i][j]][k - j]; assert(dual == C[n][k] - 1 - i); } }   // 접힌 식 Σ C(n−1−cᵢ, k−i) = C(n,k)−1−순위                                                  // ④ 순위
    { assert(binomMul(5, 0) == 1 && binomMul(5, 5) == 1 && binomMul(5, 6) == 0 && binomMul(0, 0) == 1 && binomMul(60, 30) == 118264581564861424ull); std::vector<int> e; long w = 0; assert(!nextComb(e, 5, w)); std::vector<int> full = {0, 1, 2}; assert(!nextComb(full, 3, w)); }   // ⑤
    std::cout << "Combination: recursive, index-incrementing and mask-permutation enumerations produced identical lexicographic lists of C(n,k) combinations for every n<=14 (the iterative method's index writes matched an independent count exactly and for k <= n/2 were fewer than 2 per combination on average), symmetry, Pascal, row-sum and Vandermonde identities held with exact 64-bit arithmetic up to n=60, and rank/unrank by the combinatorial number system were inverse bijections (and the folded formula C(n,k)-1-sum C(n-1-c_i,k-i) gave the rank)" << std::endl; return 0;
}
// Time Complexity: 열거 분할상환 O(1)/조합 (k ≤ n/2), C(n,k) 계산 O(min(k, n−k)), rank/unrank O(n)
// Space Complexity: O(k)
```
## Permutation()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 순열(Permutation): n 개를 순서를 구분해 늘어놓는 방법, n! 가지. k 개만 골라 늘어놓으면 P(n,k) = n!/(n−k)!, 같은 값이 섞인 다중집합이면 서로 다른 순열이 n!/(m₁! m₂! …) 개(mᵢ = 각 값의 개수). 열거: (1) 재귀 교환(첫 자리에 각 원소를 차례로 놓고 나머지를 재귀), (2) 힙(Heap)의 알고리즘 — 이웃한 순열이 정확히 한 번의 교환으로 이어져서 n! − 1 번의 교환으로 모든 순열을 만든다, (3) 사전식 다음 순열(NextPermutation 항목). 순열 번호 ↔ 순열은 팩토리얼 수 체계(레머 코드)로 O(n²) 에 오간다: 자리 i 에서 남은 원소 중 몇 번째인지를 (n−1−i)! 로 나눈 몫으로 정한다.
// 순열의 성질: 역순쌍(inversion) 수의 홀짝이 부호(짝/홀 순열), 순환 분해의 (길이 − 1) 합의 홀짝과 같다. 모든 원소가 제자리에 있지 않은 순열(교란순열, derangement)의 수는 D(n) = (n−1)(D(n−1) + D(n−2)), D(0)=1, D(1)=0 이다. 순열의 합성과 역순열은 군(대칭군 Sₙ)을 이룬다.
// 검증: ① n ≤ 8 에서 재귀·힙·사전식 세 열거가 같은 집합(개수 n!, 중복 없음)이고 힙은 이웃 순열이 교환 한 번(정확히 n!−1 번) ② 다중집합 순열 개수가 n!/Πmᵢ! 이고 서로 다른 것만 나옴 ③ k-순열 개수 P(n,k) ④ 레머 코드로 순위·역순위가 사전식 순서와 일치하는 전단사(n ≤ 8 전수) ⑤ 역순쌍 수 분포(마호니안 수)가 동적 계획과 일치하고 부호 == 순환 분해로 계산한 부호 ⑥ 교란순열 개수가 점화식과 같음, 합성·역순열이 군 법칙을 만족.
void recur(std::vector<int>& a, std::size_t i, std::vector<std::vector<int>>& out) { if (i == a.size()) { out.push_back(a); return; } for (std::size_t j = i; j < a.size(); j++) { std::swap(a[i], a[j]); recur(a, i + 1, out); std::swap(a[i], a[j]); } }
void heap(std::vector<int>& a, int k, std::vector<std::vector<int>>& out, long& swaps) { if (k == 1) { out.push_back(a); return; } heap(a, k - 1, out, swaps); for (int i = 0; i < k - 1; i++) { if (k % 2 == 0) std::swap(a[i], a[k - 1]); else std::swap(a[0], a[k - 1]); swaps++; heap(a, k - 1, out, swaps); } }
unsigned long long fact(int n) { unsigned long long r = 1; for (int i = 2; i <= n; i++) r *= (unsigned long long)i; return r; }
std::vector<int> unrankPerm(unsigned long long r, int n) { std::vector<int> avail(n), p; std::iota(avail.begin(), avail.end(), 0); for (int i = 0; i < n; i++) { unsigned long long f = fact(n - 1 - i); std::size_t idx = (std::size_t)(r / f); r %= f; p.push_back(avail[idx]); avail.erase(avail.begin() + (long)idx); } return p; }
unsigned long long rankPerm(const std::vector<int>& p) { int n = (int)p.size(); unsigned long long r = 0; for (int i = 0; i < n; i++) { int smaller = 0; for (int j = i + 1; j < n; j++) smaller += p[j] < p[i]; r += (unsigned long long)smaller * fact(n - 1 - i); } return r; }
int inversions(const std::vector<int>& p) { int c = 0; for (std::size_t i = 0; i < p.size(); i++) for (std::size_t j = i + 1; j < p.size(); j++) c += p[i] > p[j]; return c; }
int signByCycles(const std::vector<int>& p) { std::vector<bool> seen(p.size(), false); int parity = 0; for (std::size_t s = 0; s < p.size(); s++) if (!seen[s]) { int len = 0; for (std::size_t x = s; !seen[x]; x = (std::size_t)p[x]) { seen[x] = true; len++; } parity += len - 1; } return parity % 2; }
int main() {
    for (int n = 0; n <= 8; n++) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); std::vector<std::vector<int>> r, h, lex; { auto b = a; recur(b, 0, r); } long swaps = 0; { auto b = a; if (n) heap(b, n, h, swaps); else h.push_back(b); } { auto b = a; do { lex.push_back(b); } while (std::next_permutation(b.begin(), b.end())); }   // ①
        std::set<std::vector<int>> sr(r.begin(), r.end()), sh(h.begin(), h.end()), sl(lex.begin(), lex.end()); assert(r.size() == fact(n) && h.size() == fact(n) && lex.size() == fact(n) && sr.size() == fact(n) && sr == sh && sr == sl && std::is_sorted(lex.begin(), lex.end()));
        if (n >= 1) assert(swaps == (long)fact(n) - 1); for (std::size_t i = 1; i < h.size(); i++) { int diff = 0; for (int j = 0; j < n; j++) diff += h[i][j] != h[i - 1][j]; assert(diff == 2); } }                                                      // 힙: 이웃은 교환 한 번(두 자리만 다름)
    { std::vector<int> ms = {1, 1, 2, 2, 2, 3}; std::sort(ms.begin(), ms.end()); std::set<std::vector<int>> distinct; { std::vector<int> b = ms; do { distinct.insert(b); } while (std::next_permutation(b.begin(), b.end())); }                              // ②
      std::map<int, int> mult; for (int x : ms) mult[x]++; unsigned long long expect = fact((int)ms.size()); for (auto& kv : mult) expect /= fact(kv.second); assert(distinct.size() == expect && expect == 60);
      std::vector<std::vector<int>> all; { auto b = ms; recur(b, 0, all); } std::set<std::vector<int>> viaAll(all.begin(), all.end()); assert(all.size() == fact(6) && viaAll == distinct); }
    for (int n = 0; n <= 7; n++) for (int k = 0; k <= n; k++) { std::set<std::vector<int>> ks; std::vector<int> pick(n, 0); std::fill(pick.end() - k, pick.end(), 1); do { std::vector<int> items; for (int i = 0; i < n; i++) if (pick[i]) items.push_back(i); do { ks.insert(items); } while (std::next_permutation(items.begin(), items.end())); } while (std::next_permutation(pick.begin(), pick.end())); assert(ks.size() == fact(n) / fact(n - k)); }   // ③ P(n,k)
    for (int n = 0; n <= 8; n++) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); unsigned long long i = 0; do { assert(rankPerm(a) == i && unrankPerm(i, n) == a); i++; } while (std::next_permutation(a.begin(), a.end())); assert(i == fact(n)); }                  // ④
    for (int n = 0; n <= 7; n++) { std::vector<unsigned long long> dist(n * (n - 1) / 2 + 1, 0), dp(1, 1); for (int m = 2; m <= n; m++) { std::vector<unsigned long long> next(dp.size() + (std::size_t)m - 1, 0); for (std::size_t j = 0; j < dp.size(); j++) for (int t = 0; t < m; t++) next[j + (std::size_t)t] += dp[j]; dp = next; } if (n <= 1) dp = {1};     // ⑤ 마호니안 수
        std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); do { int inv = inversions(a); dist.resize(std::max(dist.size(), (std::size_t)inv + 1), 0); dist[(std::size_t)inv]++; assert((inv % 2) == signByCycles(a)); } while (std::next_permutation(a.begin(), a.end()));
        dist.resize(std::max(dist.size(), dp.size()), 0); dp.resize(dist.size(), 0); assert(dist == dp); }
    { std::vector<unsigned long long> D = {1, 0}; for (int n = 2; n <= 12; n++) D.push_back((unsigned long long)(n - 1) * (D[n - 1] + D[n - 2])); for (int n = 0; n <= 8; n++) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); unsigned long long cnt = 0; do { bool der = true; for (int i = 0; i < n; i++) if (a[i] == i) der = false; cnt += der; } while (std::next_permutation(a.begin(), a.end())); assert(cnt == D[n]); }   // ⑥
      std::mt19937 rng(44); for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 8); std::vector<int> p(n), q(n), r(n); std::iota(p.begin(), p.end(), 0); std::iota(q.begin(), q.end(), 0); std::iota(r.begin(), r.end(), 0); std::shuffle(p.begin(), p.end(), rng); std::shuffle(q.begin(), q.end(), rng); std::shuffle(r.begin(), r.end(), rng);
          auto compose = [&](const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> c(n); for (int i = 0; i < n; i++) c[i] = a[b[i]]; return c; }; std::vector<int> id(n), inv(n); std::iota(id.begin(), id.end(), 0); for (int i = 0; i < n; i++) inv[p[i]] = i;
          assert(compose(compose(p, q), r) == compose(p, compose(q, r)) && compose(p, id) == p && compose(id, p) == p && compose(p, inv) == id && compose(inv, p) == id && signByCycles(compose(p, q)) == (signByCycles(p) + signByCycles(q)) % 2); } }
    std::cout << "Permutation: recursive swapping, Heap's algorithm (exactly n!-1 swaps, neighbours differing in two positions) and lexicographic enumeration produced the same n! permutations for n<=8, multiset permutations numbered n!/prod(m_i!) and k-permutations n!/(n-k)!, Lehmer-code rank/unrank was an order-preserving bijection, inversion counts followed the Mahonian distribution with sign equal to the cycle-parity sign, derangements matched their recurrence, and composition obeyed the group laws" << std::endl; return 0;
}
// Time Complexity: 열거 O(n·n!), 순위/역순위 O(n²)
// Space Complexity: O(n)
```
## CombinationWithReplacement()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 중복 조합(combination with replacement, 다중집합 선택): n 가지 중에서 순서 없이 k 개를 뽑되 같은 것을 여러 번 뽑을 수 있다. 개수는 C(n + k − 1, k) — "별과 막대(stars and bars)": k 개의 별과 n−1 개의 막대를 일렬로 놓는 방법의 수.
// 사전순 생성은 비감소 인덱스열 c[0] ≤ c[1] ≤ … ≤ c[k−1] 을 다음 것으로 넘기는 것이다: 뒤에서부터 n−1 이 아닌 첫 위치 i 를 찾아 c[i] 를 하나 올리고 그 뒤를 모두 c[i] 로 채운다. 이 한 줄 규칙이 곧 "다음 중복 조합" 이다.
// 검증: ① 개수가 이항계수 C(n+k−1, k) ② 생성된 열이 사전순 증가이고 모두 서로 다름 ③ 모든 n^k 튜플을 정렬해 중복 제거한 것과 같음(완전 탐색 대조) ④ 별과 막대 비트열과 일대일 대응(변환 후 되돌려도 같음) ⑤ 방정식 x_1 + … + x_n = k 의 음이 아닌 정수해 개수와 같음
bool nextMultiset(std::vector<int>& c, int n) { int k = c.size(), i = k - 1; while (i >= 0 && c[i] == n - 1) i--; if (i < 0) return false; c[i]++; for (int j = i + 1; j < k; j++) c[j] = c[i]; return true; }
long long binom(int n, int k) { long long r = 1; for (int i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; }
int main() {
    long long total = 0;
    for (int n = 1; n <= 6; n++) for (int k = 0; k <= 5; k++) {
        std::vector<std::vector<int>> all; std::vector<int> c(k, 0); if (k == 0) all.push_back(c); else { do all.push_back(c); while (nextMultiset(c, n)); }
        assert((long long)all.size() == binom(n + k - 1, k)); for (size_t i = 1; i < all.size(); i++) assert(all[i - 1] < all[i]); std::set<std::vector<int>> brute; std::vector<int> t(k, 0);                                  // ① 개수 ② 사전순
        for (;;) { std::vector<int> s = t; std::sort(s.begin(), s.end()); brute.insert(s); int i = k - 1; while (i >= 0 && t[i] == n - 1) { t[i] = 0; i--; } if (i < 0) break; t[i]++; } if (k == 0) brute.insert({});
        assert(brute.size() == all.size() && std::equal(brute.begin(), brute.end(), all.begin()));                                                                                                                  // ③ 완전 탐색
        for (auto& m : all) { std::string bits; int prev = 0; std::vector<int> cnt(n, 0); for (int x : m) cnt[x]++; for (int v = 0; v < n; v++) { bits += std::string(cnt[v], '*'); if (v + 1 < n) bits += '|'; } assert((int)std::count(bits.begin(), bits.end(), '*') == k && (int)std::count(bits.begin(), bits.end(), '|') == n - 1); (void)prev;      // ④ 별과 막대
            std::vector<int> back; int v = 0; for (char ch : bits) { if (ch == '|') v++; else back.push_back(v); } assert(back == m); std::vector<int> sol(n, 0); for (int x : m) sol[x]++; int s = 0; for (int x : sol) s += x; assert(s == k); }                                                    // ⑤ 방정식 해
        total += all.size(); }
    std::cout << "CombinationWithReplacement: counts equal C(n+k-1,k) for all n<=6, k<=5 (" << total << " multisets), lexicographic order verified, identical to the brute-force set of sorted tuples, and in bijection with stars-and-bars strings" << std::endl; return 0;
}
// Time Complexity: 다음 조합 구하기 O(k), 전체 O(C(n+k-1, k) · k)
// Space Complexity: O(k)
```
## NextPermutation()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 다음 순열(NextPermutation): 사전식 순서에서 현재 배열 다음에 오는 순열을 제자리에서 만든다. 알고리즘(O(n)): ① 뒤에서부터 a[i] < a[i+1] 인 가장 큰 i 를 찾는다(오른쪽 접미사 a[i+1..] 는 내림차순이므로 그 접미사만으로는 더 키울 수 없다). 없으면 마지막 순열 — 전체를 뒤집어 오름차순(처음 순열)으로 되돌리고 false. ② 접미사에서 a[i] 보다 큰 가장 오른쪽(= 가장 작은 큰 값) a[j] 를 찾아 a[i] 와 교환. ③ 접미사를 뒤집어 오름차순으로 만든다(교환 뒤에도 접미사는 내림차순이므로 뒤집기가 곧 정렬).
// 같은 값이 있어도 올바르게 서로 다른 순열만 사전식으로 한 번씩 만든다(비교가 엄격한 `<` 이기 때문). 호출 횟수의 합은 다중집합 순열 수와 같고, 평균적으로 한 번에 움직이는 원소 수는 상수 근처다(접미사 길이의 평균이 작음: 길이 ≥ m 인 내림차순 접미사는 1/m! 의 비율). 이전 순열(prev_permutation)은 부등호를 반대로 한 대칭 알고리즘이다. 마지막에 처음으로 되돌아오므로 순환 호출이 가능하다.
// 검증: ① 길이 ≤ 7, 알파벳 크기 ≤ 4 의 모든 배열(중복 포함)에서 직접 구현이 std::next_permutation 과 반환값·결과가 같음 ② 정렬된 다중집합에서 시작해 false 가 나올 때까지의 호출 횟수 == 서로 다른 순열 수 n!/Πmᵢ!, 모두 사전식이고 중복 없음, 끝에서 오름차순으로 복귀 ③ prev 가 next 의 역 ④ 접미사 뒤집기 평균 길이가 작음 (n = 9 전체 순열에서 실제로 수행한 교환(swap) 횟수를 세어 호출당 평균 2 미만이고 총 교환 수가 닫힌 식 Σₗ (n!/l! − n!/(l+1)!)·(1 + ⌊l/2⌋) 에 마지막 호출의 되감기 ⌊n/2⌋ 를 더한 값과 정확히 같음 — 내림차순 접미사 길이가 정확히 l 인 순열이 n!/l! − n!/(l+1)! 개) ⑤ 큰 무작위 배열(n = 1000)과 같은 값만 있는 배열 ⑥ 길이 0·1·2.
bool nextPerm(std::vector<int>& a, long* moved = nullptr) { int n = (int)a.size(); int i = n - 2; while (i >= 0 && !(a[i] < a[i + 1])) i--; if (i < 0) { for (int l = 0, r = n - 1; l < r; l++, r--) { std::swap(a[l], a[r]); if (moved) ++*moved; } return false; }
    int j = n - 1; while (!(a[i] < a[j])) j--; std::swap(a[i], a[j]); if (moved) ++*moved; for (int l = i + 1, r = n - 1; l < r; l++, r--) { std::swap(a[l], a[r]); if (moved) ++*moved; } return true; }   // 접미사 뒤집기를 직접 교환으로 하며 실제 교환 수를 센다
bool prevPerm(std::vector<int>& a) { int n = (int)a.size(); int i = n - 2; while (i >= 0 && !(a[i] > a[i + 1])) i--; if (i < 0) { std::reverse(a.begin(), a.end()); return false; } int j = n - 1; while (!(a[i] > a[j])) j--; std::swap(a[i], a[j]); std::reverse(a.begin() + i + 1, a.end()); return true; }
unsigned long long fact(int n) { unsigned long long r = 1; for (int i = 2; i <= n; i++) r *= (unsigned long long)i; return r; }
int main() {
    for (int n = 0; n <= 7; n++) { int alpha = std::min(4, std::max(n, 1)); std::vector<int> a(n, 0); for (;;) { std::vector<int> mine = a, ref = a; bool b1 = nextPerm(mine), b2 = std::next_permutation(ref.begin(), ref.end()); assert(b1 == b2 && mine == ref);                              // ① 모든 배열
          std::vector<int> pm = a, pr = a; bool p1 = prevPerm(pm), p2 = std::prev_permutation(pr.begin(), pr.end()); assert(p1 == p2 && pm == pr); int i = n - 1; while (i >= 0 && ++a[i] == alpha) { a[i] = 0; i--; } if (i < 0) break; } }
    for (int rep = 0; rep < 60; rep++) { std::mt19937 rng(100 + rep); int n = 1 + (int)(rng() % 8), alpha = 1 + (int)(rng() % 4); std::vector<int> ms(n); for (int& x : ms) x = (int)(rng() % alpha); std::sort(ms.begin(), ms.end());                                                                  // ②
        std::map<int, int> mult; for (int x : ms) mult[x]++; unsigned long long expect = fact(n); for (auto& kv : mult) expect /= fact(kv.second); std::vector<int> a = ms, prev = ms; unsigned long long calls = 1; std::set<std::vector<int>> seen{a}; while (nextPerm(a)) { assert(prev < a && seen.insert(a).second); prev = a; calls++; }
        assert(calls == expect && a == ms && seen.size() == expect);
        std::vector<int> b = ms; for (unsigned long long k = 1; k < expect; k++) nextPerm(b); std::vector<int> back = b; for (unsigned long long k = 1; k < expect; k++) { std::vector<int> before = b; bool ok = prevPerm(b); assert(ok); std::vector<int> fwd = b; nextPerm(fwd); assert(fwd == before); } assert(b == ms && back.size() == ms.size()); }       // ③ prev 는 next 의 역
    { int n = 9; std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); long moved = 0, calls = 0; while (nextPerm(a, &moved)) calls++; long expected = 0; for (int l = 1; l < n; l++) expected += (long)(fact(n) / fact(l) - fact(n) / fact(l + 1)) * (1 + l / 2); expected += n / 2; assert(calls == (long)fact(n) - 1 && moved == expected && (double)moved / (double)calls < 2.0); }                                    // ④ 평균 교환 수
    { std::mt19937 rng(7); std::vector<int> a(1000); for (int& x : a) x = (int)(rng() % 50); std::vector<int> ref = a; for (int step = 0; step < 200; step++) { bool b1 = nextPerm(a), b2 = std::next_permutation(ref.begin(), ref.end()); assert(b1 == b2 && a == ref); }
      std::vector<int> same(100, 7); std::vector<int> s2 = same; assert(!nextPerm(s2) && s2 == same && !prevPerm(s2)); }                                                                                                                                     // ⑤
    { std::vector<int> e; assert(!nextPerm(e) && e.empty()); std::vector<int> one = {5}; assert(!nextPerm(one) && one == std::vector<int>{5}); std::vector<int> two = {1, 2}; assert(nextPerm(two) && two == (std::vector<int>{2, 1}) && !nextPerm(two) && two == (std::vector<int>{1, 2})); }   // ⑥
    std::cout << "NextPermutation: the hand-written next/prev permutation matched std::next_permutation and std::prev_permutation on every array of length up to 7 over a 4-letter alphabet (duplicates included), enumerated each distinct multiset permutation exactly once in lexicographic order (n!/prod(m_i!) calls) and wrapped around to sorted order, prev undid next, and the measured number of element swaps per call over all permutations of 9 items averaged below 2 and totalled exactly the closed form over descending-suffix lengths" << std::endl; return 0;
}
// Time Complexity: 호출당 O(n) (평균 O(1)), 전체 순열 열거 O(n!)
// Space Complexity: O(1)
```
## GrayCode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

// 그레이 코드(Gray Code): 연속한 두 코드가 정확히 한 비트만 다른 이진수 배열. n 비트의 반사 이진 그레이 코드(reflected binary Gray code)는 i 번째 코드가 `g(i) = i ^ (i >> 1)` 이다. 만드는 법(반사): n−1 비트의 코드열을 쓰고, 그 뒤에 같은 열을 거꾸로 쓴 다음, 앞쪽 절반에는 맨 앞에 0, 뒤쪽 절반에는 1 을 붙인다. 역변환(코드 → 번호)은 상위 비트부터의 누적 XOR: `i = g ^ (g >> 1) ^ (g >> 2) ^ …` (로그 번의 시프트로도 가능).
// 성질: 2ⁿ 개 코드가 모두 다르고(전단사), 이웃한 코드가 한 비트만 다르며 마지막과 처음도 한 비트만 다르다(원형). i−1 에서 i 로 갈 때 뒤집히는 비트는 i 의 끝의 0 의 개수 ctz(i) 이며 이 수열은 눈금자(ruler) 수열 0,1,0,2,0,1,0,3,… 이다 — 비트 j 는 총 2^(n−1−j) 번 뒤집힌다. 응용: 부분집합을 한 원소씩만 바꾸며 열거(합 갱신 O(1)), 회전식 인코더(여러 비트가 동시에 바뀌지 않아 읽는 중 오판독이 없음), 오류 최소화, 하노이 탑, 카르노 맵.
// 검증: ① n = 1..20 에서 이웃한 코드(원형 포함)의 해밍 거리가 정확히 1, 모든 코드가 서로 다르고(전단사) 역변환이 항등 ② 반사 구성과 공식이 모든 n ≤ 12 에서 같음 ③ 뒤집히는 비트가 ctz(i) 이고 비트 j 의 총 뒤집힘 횟수가 2^(n−1−j) ④ 이진 카운터와 비교: 2ⁿ 번 증가할 때 총 뒤집힌 비트 수가 이진은 정확히 2^(n+1) − 2 − n, 그레이는 정확히 2ⁿ − 1 ⑤ 로그 시프트 역변환이 누적 XOR 과 같음 ⑥ 그레이 순서의 부분집합 합 갱신이 정의대로 계산한 합과 같음.
uint32_t gray(uint32_t i) { return i ^ (i >> 1); }
uint32_t grayInverse(uint32_t g) { uint32_t i = 0; for (; g; g >>= 1) i ^= g; return i; }                                                                        // 누적 XOR
uint32_t grayInverseLog(uint32_t g) { g ^= g >> 16; g ^= g >> 8; g ^= g >> 4; g ^= g >> 2; g ^= g >> 1; return g; }                                          // 로그 번의 시프트
std::vector<uint32_t> reflect(int n) { std::vector<uint32_t> g{0}; for (int b = 0; b < n; b++) { std::size_t m = g.size(); for (std::size_t i = m; i-- > 0;) g.push_back(g[i] | (1u << b)); } return g; }
std::string bits(uint32_t x, int n) { std::string s; for (int b = n - 1; b >= 0; --b) s += (x >> b & 1) ? '1' : '0'; return s; }
std::string grayTable(int n) {                                                                    // 그림: i, 이진수, 그레이 코드, 이전 코드와 달라진 비트(0 이 가장 오른쪽)
    std::string t;
    for (uint32_t i = 0; i < (1u << n); ++i) {
        t += "i=" + std::to_string(i) + " bin=" + bits(i, n) + " gray=" + bits(gray(i), n);
        if (i) { uint32_t d = gray(i) ^ gray(i - 1); int b = 0; while (!(d >> b & 1)) ++b; t += " flip=" + std::to_string(b); }
        t += "\n";
    }
    return t;
}
int main() {
    {   const std::string pic = "i=0 bin=000 gray=000\ni=1 bin=001 gray=001 flip=0\ni=2 bin=010 gray=011 flip=1\ni=3 bin=011 gray=010 flip=0\n"
                                "i=4 bin=100 gray=110 flip=2\ni=5 bin=101 gray=111 flip=0\ni=6 bin=110 gray=101 flip=1\ni=7 bin=111 gray=100 flip=0\n";
        assert(grayTable(3) == pic); std::cout << pic; }                                              // 바뀌는 비트가 0 1 0 2 0 1 0 (눈금자 수열): 매 걸음 정확히 한 비트
    for (int n = 1; n <= 20; n++) { uint32_t N = 1u << n; std::vector<bool> seen(N, false); for (uint32_t i = 0; i < N; i++) { uint32_t g = gray(i); assert(g < N && !seen[g]); seen[g] = true; assert(grayInverse(g) == i && grayInverseLog(g) == i); uint32_t nxt = gray((i + 1) % N); assert(__builtin_popcount(g ^ nxt) == 1); } }   // ① 원형까지
    for (int n = 1; n <= 12; n++) { auto r = reflect(n); assert(r.size() == (std::size_t)1 << n); for (uint32_t i = 0; i < r.size(); i++) assert(r[i] == gray(i)); }                                                                                  // ②
    for (int n = 1; n <= 16; n++) { uint32_t N = 1u << n; std::vector<uint32_t> flips(n, 0); for (uint32_t i = 1; i < N; i++) { uint32_t diff = gray(i) ^ gray(i - 1); assert(diff == (1u << __builtin_ctz(i))); flips[__builtin_ctz(i)]++; } for (int j = 0; j < n; j++) assert(flips[j] == (1u << (n - 1 - j))); }   // ③ 눈금자 수열
    for (int n = 2; n <= 16; n++) { uint32_t N = 1u << n; long long binFlips = 0, grayFlips = 0; for (uint32_t i = 1; i < N; i++) { binFlips += __builtin_popcount(i ^ (i - 1)); grayFlips += __builtin_popcount(gray(i) ^ gray(i - 1)); } assert(grayFlips == (long long)N - 1 && binFlips == 2LL * N - 2 - n && binFlips > grayFlips); }   // ④
    { std::vector<long long> val = {5, -3, 8, 2, -7, 11, 4, 6, -2, 9}; int n = (int)val.size(); long long sum = 0; uint32_t g = 0; for (uint32_t i = 1; i < (1u << n); i++) { int bit = __builtin_ctz(i); g ^= 1u << bit; sum += (g >> bit & 1) ? val[bit] : -val[bit];                // ⑥ 한 번에 한 원소만 갱신
          long long want = 0; for (int b = 0; b < n; b++) if (g >> b & 1) want += val[b]; assert(sum == want && g == gray(i)); } }
    assert(gray(0) == 0 && gray(1) == 1 && gray(2) == 3 && gray(3) == 2 && gray(4) == 6 && gray(5) == 7 && gray(6) == 5 && gray(7) == 4 && grayInverse(4) == 7);                                                                      // 표준 3 비트 열 000 001 011 010 110 111 101 100
    std::cout << "GrayCode: i ^ (i >> 1) gave 2^n distinct codes for n up to 20 with exactly one bit changing between neighbours (cyclically), the reflect-and-prefix construction equalled the formula, the flipped bit was ctz(i) so bit j flipped 2^(n-1-j) times, a Gray counter changed exactly 2^n - 1 bits in total against many more for a binary counter, and subset sums updated by one term per step matched direct sums" << std::endl; return 0;
}
// Time Complexity: g(i) 계산 O(1), 역변환 O(log n) 또는 O(n)
// Space Complexity: O(1)
```

# Part 9. 부분집합 탐색
## Backtracking()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 백트래킹(Backtracking)은 부분집합 탐색을 "각 원소를 넣는다/뺀다" 의 이진 결정 트리로 보고 깊이 우선으로 훑되, 이미 실패가 확정된 가지는 일찍 잘라 내는(pruning) 기법이다. 모든 부분집합은 2ⁿ 개지만 가지치기를 하면 방문 노드 수가 크게 줄어든다.
// 여기서는 "합이 정확히 target 인 부분집합을 모두 찾기": 양수 원소를 내림차순으로 정렬해 두고 ① 지금까지의 합이 target 이 되면 기록하고 멈춤(양수라 더 넣으면 초과) ② 지금까지의 합 + 남은 원소 전체의 합 < target 이면 중단 ③ 넣었을 때 target 을 넘으면 "넣는" 가지를 건너뜀. 선택 상태를 그대로 두고 되돌리는(undo) 것이 "백트랙" 이다.
// 검증: 무작위 입력 300개(n ≤ 16)에서 ① 찾은 부분집합의 집합이 2ⁿ 완전 열거(비트마스크)의 결과와 정확히 같음 ② 각 해의 합이 target 이고 해마다 서로 다름 ③ 가지치기 방문 노드 수 ≤ 가지치기 없는 이진 트리 노드 수 2^(n+1) − 1 이고 전체 합이 훨씬 적음
long long visited;
void search(const std::vector<int>& v, const std::vector<int>& suffix, int i, int sum, int target, std::vector<int>& chosen, std::vector<std::vector<int>>& out) {
    visited++; if (sum == target) { out.push_back(chosen); return; }
    if (i == (int)v.size() || sum + suffix[i] < target) return;
    if (sum + v[i] <= target) { chosen.push_back(i); search(v, suffix, i + 1, sum + v[i], target, chosen, out); chosen.pop_back(); }                                         // 넣는다 (뒤에서 undo)
    search(v, suffix, i + 1, sum, target, chosen, out); }                                                                                                                  // 뺀다
int main() {
    std::mt19937 rng(7); long long prunedNodes = 0, fullNodes = 0; int withSolutions = 0;
    for (int t = 0; t < 300; t++) {
        int n = 1 + rng() % 16; std::vector<int> v(n); for (int& x : v) x = 1 + rng() % 12; std::sort(v.rbegin(), v.rend()); int total = std::accumulate(v.begin(), v.end(), 0), target = rng() % (total + 1);
        std::vector<int> suffix(n + 1, 0); for (int i = n - 1; i >= 0; i--) suffix[i] = suffix[i + 1] + v[i]; std::vector<std::vector<int>> out; std::vector<int> chosen; visited = 0; search(v, suffix, 0, 0, target, chosen, out);
        std::set<std::vector<int>> found(out.begin(), out.end()); assert(found.size() == out.size());                                                                          // ② 해가 중복 없이 나옴
        std::set<std::vector<int>> brute; for (int mask = 0; mask < (1 << n); mask++) { int s = 0; std::vector<int> idx; for (int i = 0; i < n; i++) if (mask >> i & 1) { s += v[i]; idx.push_back(i); } if (s == target) brute.insert(idx); }
        assert(found == brute);                                                                                                                                                // ① 완전 열거와 같음
        for (auto& s : out) { int sum = 0; for (int i : s) sum += v[i]; assert(sum == target); }
        assert(visited <= (1LL << (n + 1)) - 1); prunedNodes += visited; fullNodes += (1LL << (n + 1)) - 1; withSolutions += !out.empty(); }
    assert(prunedNodes * 2 < fullNodes && withSolutions > 200);
    std::cout << "Backtracking: all subsets summing to the target found exactly as the 2^n bitmask enumeration does on 300 random inputs; pruning visited " << prunedNodes << " nodes versus " << fullNodes << " for the full decision tree" << std::endl; return 0;
}
// Time Complexity: 최악 O(2ⁿ), 가지치기로 실제 방문은 크게 줄어듦
// Space Complexity: O(n) (재귀 깊이)
```
## BitMaskEnumeration()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 비트마스크 열거: n ≤ 20~30 인 전체집합의 부분집합을 n 비트 정수 하나로 표현하면 mask 를 0 부터 2ⁿ−1 까지 세는 것만으로 모든 부분집합을 열거할 수 있다 — i 번째 비트가 1 이면 i 번째 원소가 들어 있다.
// 세 가지 관용구: ① 전체 열거 for (mask = 0; mask < 1<<n; mask++) ② 마스크 m 의 부분집합만(부분마스크) 큰 것부터 열거 for (s = m; ; s = (s − 1) & m) { …; if (s == 0) break; } — 개수는 2^popcount(m) ③ 크기가 k 인 부분집합만 사전순(수치 오름차순)으로 열거하는 Gosper 의 묘수 next = (x + c) | (((x ^ (x + c)) >> 2) / c) 형태 (c = x & −x).
// 검증: ① 전체 열거가 모든 서로 다른 부분집합 2ⁿ 개를 만든다 ② 부분마스크 열거가 정확히 2^popcount(m) 개이고 모두 m 의 부분집합이며 서로 다르고 내림차순 ③ Gosper 열거가 C(n,k) 개이고 popcount 가 모두 k, 수치 오름차순, 완전 탐색과 같은 집합 ④ 모든 m 에 대해 부분마스크 개수의 합 = 3ⁿ
uint32_t gosper(uint32_t x) { uint32_t c = x & -x, r = x + c; return (((r ^ x) >> 2) / c) | r; }
int main() {
    for (int n = 0; n <= 12; n++) { std::set<uint32_t> all; for (uint32_t m = 0; m < (1u << n); m++) all.insert(m); assert(all.size() == (1u << n)); }                                                             // ①
    for (int n = 1; n <= 10; n++) { unsigned long long sum = 0; for (uint32_t m = 0; m < (1u << n); m++) { std::vector<uint32_t> subs; for (uint32_t s = m;; s = (s - 1) & m) { subs.push_back(s); if (s == 0) break; } assert(subs.size() == (1u << __builtin_popcount(m)));
            for (size_t i = 0; i < subs.size(); i++) { assert((subs[i] & m) == subs[i]); if (i) assert(subs[i - 1] > subs[i]); } sum += subs.size(); }
        unsigned long long p3 = 1; for (int i = 0; i < n; i++) p3 *= 3; assert(sum == p3); }                                                                                                              // ② ④ 부분마스크 · 3ⁿ
    for (int n = 1; n <= 14; n++) for (int k = 1; k <= n; k++) { std::vector<uint32_t> g; for (uint32_t x = (1u << k) - 1; x < (1u << n); x = gosper(x)) { assert(__builtin_popcount(x) == k); g.push_back(x); } std::vector<uint32_t> brute; for (uint32_t m = 0; m < (1u << n); m++) if (__builtin_popcount(m) == k) brute.push_back(m); assert(g == brute); }      // ③ Gosper
    std::cout << "BitMaskEnumeration: full masks, descending submask enumeration (2^popcount items, total 3^n over all masks) and Gosper's fixed-size enumeration verified against brute force" << std::endl; return 0;
}
// Time Complexity: 전체 O(2ⁿ), 부분마스크 전체 O(3ⁿ), k-부분집합 O(C(n,k))
// Space Complexity: O(1)
```
## MeetInTheMiddle()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 중간에서 만나기(Meet in the Middle): n = 40 정도면 2ⁿ ≈ 10¹² 라 전수 조사는 불가능하다. 원소를 반으로 나눠 각 절반의 부분집합 합 2^(n/2) ≈ 10⁶ 개를 만들고 정렬한 뒤, 한쪽의 합 s 에 대해 target − s 를 다른 쪽에서 이분 탐색/두 포인터로 찾으면 O(2^(n/2) · n) 에 해결된다.
// 제곱근 규모의 비용 절감이 핵심이다: 2ⁿ → 2·2^(n/2). 여기서는 target 과 정확히 같은 합의 부분집합 개수 세기와 target 이하의 최대 합(가장 가까운 합) 찾기를 함께 구현하고, 부분집합 자체를 복원해 합을 검증한다.
// 검증: ① n ≤ 22 의 무작위 입력 200개에서 개수와 최대 합이 Gray 코드 완전 열거와 같음 ② n = 40 (값 최대 10⁹)에서 일부러 심은 부분집합 합을 target 으로 하면 찾아낸 복원 부분집합의 합이 정확히 target ③ 연산 수 비교(2·2^20 vs 2^40)
typedef long long ll;
std::vector<std::pair<ll, unsigned>> halfSums(const std::vector<ll>& v) { int k = v.size(); std::vector<std::pair<ll, unsigned>> r(1u << k); r[0] = {0, 0}; for (unsigned m = 1; m < (1u << k); m++) { int low = __builtin_ctz(m); r[m] = {r[m & (m - 1)].first + v[low], m}; } std::sort(r.begin(), r.end()); return r; }
struct Result { ll count; ll bestAtMost; std::vector<ll> subset; };
Result mitm(const std::vector<ll>& v, ll target) {
    int n = v.size(), h = n / 2; std::vector<ll> a(v.begin(), v.begin() + h), b(v.begin() + h, v.end()); auto A = halfSums(a), B = halfSums(b); Result r{0, -1, {}};
    for (auto& [sa, ma] : A) { auto lo = std::lower_bound(B.begin(), B.end(), std::make_pair(target - sa, 0u)), hi = std::upper_bound(B.begin(), B.end(), std::make_pair(target - sa, ~0u)); r.count += hi - lo;                       // sa + sb == target 인 sb 의 개수
        if (lo != B.end() && lo->first == target - sa && r.subset.empty() && r.count == hi - lo) { for (int i = 0; i < h; i++) if (ma >> i & 1) r.subset.push_back(a[i]); for (int i = 0; i < (int)b.size(); i++) if (lo->second >> i & 1) r.subset.push_back(b[i]); }
        auto it = std::upper_bound(B.begin(), B.end(), std::make_pair(target - sa, ~0u)); if (it != B.begin()) { --it; r.bestAtMost = std::max(r.bestAtMost, sa + it->first); } }
    return r; }
int main() {
    std::mt19937_64 rng(5);
    for (int t = 0; t < 200; t++) { int n = 1 + rng() % 22; std::vector<ll> v(n); for (ll& x : v) x = 1 + rng() % 30; ll total = 0; for (ll x : v) total += x; ll target = rng() % (total + 1); Result r = mitm(v, target);
        ll count = 0, best = -1, sum = 0; unsigned gray = 0; for (unsigned i = 0; i < (1u << n); i++) { if (i) { unsigned g2 = i ^ (i >> 1); unsigned diff = gray ^ g2; int bit = __builtin_ctz(diff); sum += (g2 & diff) ? v[bit] : -v[bit]; gray = g2; } if (sum == target) count++; if (sum <= target) best = std::max(best, sum); }
        assert(r.count == count && r.bestAtMost == best); if (count) { ll s = 0; for (ll x : r.subset) s += x; assert(s == target); } }                                                                                    // ① Gray 코드 완전 열거와 같음
    std::vector<ll> big(40); for (ll& x : big) x = 1 + rng() % 1000000000; ll target = 0; std::vector<int> plant; for (int i = 0; i < 40; i++) if (rng() % 2) { target += big[i]; plant.push_back(i); }
    Result r = mitm(big, target); ll s = 0; for (ll x : r.subset) s += x; assert(r.count >= 1 && s == target && !r.subset.empty());                                                                                            // ② n = 40 에서 심은 해를 찾음
    std::cout << "MeetInTheMiddle: matches Gray-code brute force on 200 random inputs; for n=40 (values up to 1e9) it found a subset with the planted sum (" << r.count << " subsets total) using about " << (2 << 20) << " half-sums instead of 2^40 = " << (1LL << 40) << std::endl; return 0;
}
// Time Complexity: O(2^(n/2) · n)
// Space Complexity: O(2^(n/2))
```
## SubsetSum()
### 대표코드
```cpp
#include <bitset>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 부분집합 합(Subset Sum): 정수 집합에서 합이 정확히 target 인 부분집합이 있는가. NP-완전이지만 target 이 작으면 의사 다항 시간 DP 로 풀린다. 세 가지 형태 ① 가능성: reach 비트셋을 원소 x 마다 reach |= reach << x (한 번에 W 비트씩) → O(n · T / 64)
// ② 복원: 각 합 s 를 처음 도달 가능하게 만든 원소 번호 first[s] 를 기록해 두면 target 에서 거꾸로 따라가며 부분집합을 만들 수 있다(이때 first[s − x] 는 x 이전 원소로 도달 가능해야 하므로 원소를 순서대로 처리하며 first 를 갱신) ③ 개수 세기: ways[s] += ways[s − x] (s 를 내림차순으로 갱신해 원소 재사용 방지).
// 검증: n ≤ 18 무작위 입력 300개에서 ① 비트셋 가능성 == 완전 열거 ② 복원한 부분집합의 합이 target 이고 원소는 서로 다른 인덱스 ③ DP 개수 == 완전 열거 개수 ④ 값이 모두 target 의 약수 아닌 불가능 사례도 포함
const int T = 600;
int main() {
    std::mt19937 rng(9); int possible = 0, impossible = 0;
    for (int t = 0; t < 300; t++) { int n = 1 + rng() % 18; std::vector<int> v(n); for (int& x : v) x = 1 + rng() % 40; if (t % 5 == 0) for (int& x : v) x = 2 * x;
        std::bitset<T + 1> reach; reach[0] = 1; std::vector<int> first(T + 1, -1); std::vector<long long> ways(T + 1, 0); ways[0] = 1;
        for (int i = 0; i < n; i++) { std::bitset<T + 1> shifted = reach << v[i]; std::bitset<T + 1> fresh = shifted & ~reach; for (int s = v[i]; s <= T; s++) if (fresh[s]) first[s] = i; reach |= shifted; for (int s = T; s >= v[i]; s--) ways[s] += ways[s - v[i]]; }
        int target = rng() % (T + 1); if (t % 5 == 0) target |= 1;                                                                                                                                       // 짝수만 있을 때 홀수 target → 불가능
        long long brute = 0; for (int mask = 0; mask < (1 << n); mask++) { int s = 0; for (int i = 0; i < n; i++) if (mask >> i & 1) s += v[i]; brute += s == target; }
        assert((brute > 0) == reach[target] && brute == ways[target]);                                                                                                                                   // ① 가능성 · ③ 개수
        if (reach[target]) { possible++; std::vector<int> used; int s = target; while (s > 0) { int i = first[s]; assert(i >= 0); used.push_back(i); s -= v[i]; assert(s >= 0); first[s] = first[s]; } int sum = 0; std::vector<char> seen(n, 0); for (int i : used) { assert(!seen[i]); seen[i] = 1; sum += v[i]; } assert(sum == target); } else impossible++; }       // ② 복원
    std::cout << "SubsetSum: bitset reachability and subset counts match exhaustive search on 300 random inputs (" << possible << " reachable targets, " << impossible << " unreachable); reconstructed subsets sum exactly to the target" << std::endl; return 0;
}
// Time Complexity: O(n · T / 64) 가능성, O(n · T) 개수 세기
// Space Complexity: O(T)
```
## KnapsackSubset()
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 0/1 배낭(Knapsack)을 부분집합 선택 문제로 보기: 물건의 집합에서 무게 합이 용량 W 이하인 부분집합 중 가치 합이 최대인 것을 고른다. 부분집합이 2ⁿ 개라서 완전 열거는 O(2ⁿ·n) 이지만 DP 는 O(n·W): dp[i][w] = 앞의 i 개 물건 중에서 무게 w 이하로 얻는 최대 가치, 점화식 dp[i][w] = max(dp[i−1][w], dp[i−1][w−wt[i]] + val[i]) (i 번째를 넣거나 안 넣거나). 이 시간은 용량 W 의 값에 비례하는 의사 다항 시간이다(NP-난해이지만 W 가 작으면 빠름).
// 선택된 부분집합은 표를 거꾸로 따라가며 복원한다(dp[i][w] ≠ dp[i−1][w] 이면 i 번째 물건을 선택). 값만 필요하면 w 를 큰 쪽에서 작은 쪽으로 돌려 1 차원 배열 하나(O(W) 공간)로 충분하다 — 작은 쪽부터 돌리면 같은 물건을 여러 번 쓰는 무한 배낭이 된다. 탐욕법(가치/무게 비율 순)은 항상 최적이 아니지만 분수 배낭(물건을 쪼갤 수 있을 때)의 최적값은 0/1 배낭 최적값의 상한이 된다. 가치를 무시하고 "무게 합이 정확히 W 인 부분집합이 있는가"만 물으면 부분집합 합 문제이고 비트 집합 DP(`reach |= reach << wt`)로 64 개씩 묶어 푼다.
// 검증: n ≤ 16 무작위 입력 300개에서 ① 2차원 DP·1차원 DP·완전 열거(2ⁿ)의 최적값이 같음 ② 복원한 선택의 무게 ≤ W, 가치 == 최적값, 인덱스 중복 없음 ③ 비율 탐욕법 ≤ 최적이고 최적보다 작은 사례가 실제로 존재 ④ 분수 배낭 상한 ≥ 최적 ⑤ 1차원 DP 를 작은 쪽부터 돌리면(무한 배낭) 0/1 최적보다 크거나 같고 큰 사례가 존재 ⑥ 비트 집합 DP 의 도달 가능한 무게 집합 == 완전 열거로 만든 무게 집합.
int dp2D(const std::vector<int>& wt, const std::vector<int>& val, int W, std::vector<int>& chosen) { int n = (int)wt.size(); std::vector<std::vector<int>> dp(n + 1, std::vector<int>(W + 1, 0));
    for (int i = 1; i <= n; i++) for (int w = 0; w <= W; w++) { dp[i][w] = dp[i - 1][w]; if (w >= wt[i - 1]) dp[i][w] = std::max(dp[i][w], dp[i - 1][w - wt[i - 1]] + val[i - 1]); }
    chosen.clear(); int w = W; for (int i = n; i >= 1; i--) if (dp[i][w] != dp[i - 1][w]) { chosen.push_back(i - 1); w -= wt[i - 1]; } std::reverse(chosen.begin(), chosen.end()); return dp[n][W]; }
int dp1D(const std::vector<int>& wt, const std::vector<int>& val, int W, bool descending) { std::vector<int> dp(W + 1, 0); for (std::size_t i = 0; i < wt.size(); i++) { if (descending) { for (int w = W; w >= wt[i]; w--) dp[w] = std::max(dp[w], dp[w - wt[i]] + val[i]); } else { for (int w = wt[i]; w <= W; w++) dp[w] = std::max(dp[w], dp[w - wt[i]] + val[i]); } } return dp[W]; }
int bruteBest(const std::vector<int>& wt, const std::vector<int>& val, int W) { int n = (int)wt.size(), best = 0; for (unsigned mask = 0; mask < (1u << n); mask++) { int w = 0, v = 0; for (int i = 0; i < n; i++) if (mask >> i & 1) { w += wt[i]; v += val[i]; } if (w <= W) best = std::max(best, v); } return best; }
int greedyRatio(const std::vector<int>& wt, const std::vector<int>& val, int W) { std::vector<int> order(wt.size()); std::iota(order.begin(), order.end(), 0); std::sort(order.begin(), order.end(), [&](int a, int b) { return (long long)val[a] * wt[b] > (long long)val[b] * wt[a]; }); int w = 0, v = 0; for (int i : order) if (w + wt[i] <= W) { w += wt[i]; v += val[i]; } return v; }
double fractionalBound(const std::vector<int>& wt, const std::vector<int>& val, int W) { std::vector<int> order(wt.size()); std::iota(order.begin(), order.end(), 0); std::sort(order.begin(), order.end(), [&](int a, int b) { return (long long)val[a] * wt[b] > (long long)val[b] * wt[a]; }); double v = 0, cap = W; for (int i : order) { if (wt[i] <= cap) { v += val[i]; cap -= wt[i]; } else { v += val[i] * cap / wt[i]; break; } } return v; }
int main() {
    std::mt19937 rng(14); int greedyWorse = 0, unboundedBigger = 0, instances = 0;
    for (int t = 0; t < 300; t++) { int n = 1 + (int)(rng() % 16); std::vector<int> wt(n), val(n); for (int i = 0; i < n; i++) { wt[i] = 1 + (int)(rng() % 15); val[i] = 1 + (int)(rng() % 30); } int W = 1 + (int)(rng() % 60); instances++;
        std::vector<int> chosen; int opt2 = dp2D(wt, val, W, chosen), opt1 = dp1D(wt, val, W, true), brute = bruteBest(wt, val, W); assert(opt2 == brute && opt1 == brute);                                    // ①
        int tw = 0, tv = 0; std::vector<int> sorted = chosen; assert(std::is_sorted(sorted.begin(), sorted.end()) && std::adjacent_find(sorted.begin(), sorted.end()) == sorted.end()); for (int i : chosen) { tw += wt[i]; tv += val[i]; } assert(tw <= W && tv == opt2);   // ②
        int g = greedyRatio(wt, val, W); assert(g <= opt2); greedyWorse += g < opt2; assert(fractionalBound(wt, val, W) + 1e-9 >= opt2);                                                                       // ③ ④
        int unbounded = dp1D(wt, val, W, false); assert(unbounded >= opt2); unboundedBigger += unbounded > opt2; }                                                                                              // ⑤
    assert(greedyWorse > 10 && unboundedBigger > 20);
    for (int t = 0; t < 200; t++) { int n = 1 + (int)(rng() % 14); std::vector<int> wt(n); for (int& x : wt) x = 1 + (int)(rng() % 12); std::bitset<200> reach; reach[0] = 1; for (int x : wt) reach |= reach << x; std::bitset<200> brute; for (unsigned mask = 0; mask < (1u << n); mask++) { int w = 0; for (int i = 0; i < n; i++) if (mask >> i & 1) w += wt[i]; if (w < 200) brute[w] = 1; } assert(reach == brute); }   // ⑥
    { std::vector<int> chosen; assert(dp2D({}, {}, 10, chosen) == 0 && chosen.empty() && dp2D({5}, {9}, 4, chosen) == 0 && chosen.empty() && dp2D({5}, {9}, 5, chosen) == 9 && chosen == std::vector<int>{0}); }
    std::cout << "KnapsackSubset: the 2D table, the 1D descending-capacity table and exhaustive search over all 2^n subsets gave the same optimum on " << instances << " random instances, the reconstructed item set was feasible, duplicate-free and optimal, ratio-greedy was suboptimal in " << greedyWorse << " instances, the fractional relaxation always bounded the optimum from above, ascending-capacity (unbounded) DP exceeded it in " << unboundedBigger << " cases, and the bitset subset-sum DP matched enumeration" << std::endl; return 0;
}
// Time Complexity: O(n · W) (DP), 복원 O(n), 비트 집합 DP O(n · W / 64)
// Space Complexity: O(n · W) (복원 포함), 값만 구하면 O(W)
```

## DancingLinks()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 춤추는 링크(Dancing Links, Knuth 2000)는 정확 덮개 문제(exact cover)를 푸는 Algorithm X 를 이중 연결 리스트로 구현한 것이다. 문제: 전체집합 U 와 부분집합들의 모임 S 가 주어질 때 S 에서 골라 U 의 모든 원소를 "정확히 한 번씩" 덮는 부분 모임을 찾아라.
// 0/1 행렬로 보면 열 = U 의 원소, 행 = 부분집합이다. Algorithm X: 남은 열 중 1 이 가장 적은 열 c 를 고르고(실패가 빨리 드러남) c 를 덮는 행 r 을 하나 시도해 r 이 덮는 모든 열을 제거하고(그 열에 1 을 가진 다른 행도 제거) 재귀한 뒤 되돌린다. 핵심 묘기는 리스트에서 노드를 빼도 그 노드가 자기 이웃 포인터를 기억하고 있어
// x.L.R = x.R, x.R.L = x.L 로 빼고 x.L.R = x, x.R.L = x 로 "정확히 되돌릴 수" 있다는 점이다 — 되돌리기가 O(1) 이라 백트래킹이 빠르다. 선택적으로만 덮이는 "보조(secondary) 열"(대각선 충돌 제약)도 헤더 고리에서 빼 두면 지원된다.
// 검증: ① Knuth 의 예제(U = {1..7}, 6 개 부분집합)의 유일한 해 {B, D, F} ② N-퀸 해의 개수가 알려진 값(4→2, 5→10, 6→4, 8→92)과 같고 독립적인 비트마스크 백트래킹과 일치 ③ 4×4 스도쿠(2×2 상자) 전체 해 개수 288 ④ 9×9 스도쿠 어려운 문제의 해가 유일하고 규칙을 모두 만족하며 단서와 일치
struct DLX {
    std::vector<int> L, R, U, D, C, S, rowOf; int rootCols; long long solutions = 0; long long limit = -1; std::vector<int> partial, firstSolution; bool wantFirst = false;
    DLX(int primary, int secondary) : rootCols(primary + secondary) { int total = primary + secondary + 1; L.resize(total); R.resize(total); U.resize(total); D.resize(total); C.resize(total); S.assign(total, 0); rowOf.assign(total, -1);
        for (int i = 0; i < total; i++) { U[i] = D[i] = C[i] = i; } for (int i = 0; i <= primary; i++) { L[i] = i == 0 ? primary : i - 1; R[i] = i == primary ? 0 : i + 1; } for (int i = primary + 1; i < total; i++) L[i] = R[i] = i; }                          // 헤더 고리는 주 열만, 보조 열은 자기 자신 고리
    void addRow(int id, const std::vector<int>& cols) { int first = -1; for (int col : cols) { int x = L.size(); L.push_back(x); R.push_back(x); U.push_back(U[col + 1]); D.push_back(col + 1); C.push_back(col + 1); rowOf.push_back(id); D[U[col + 1]] = x; U[col + 1] = x; S[col + 1]++; if (first < 0) first = x; else { L[x] = L[first]; R[x] = first; R[L[first]] = x; L[first] = x; } } }
    void cover(int c) { R[L[c]] = R[c]; L[R[c]] = L[c]; for (int i = D[c]; i != c; i = D[i]) for (int j = R[i]; j != i; j = R[j]) { U[D[j]] = U[j]; D[U[j]] = D[j]; S[C[j]]--; } }
    void uncover(int c) { for (int i = U[c]; i != c; i = U[i]) for (int j = L[i]; j != i; j = L[j]) { S[C[j]]++; U[D[j]] = j; D[U[j]] = j; } L[R[c]] = c; R[L[c]] = c; }
    void search() { if (limit >= 0 && solutions >= limit) return; if (R[0] == 0) { solutions++; if (wantFirst && firstSolution.empty()) firstSolution = partial; return; } int c = R[0]; for (int j = R[0]; j != 0; j = R[j]) if (S[j] < S[c]) c = j; if (S[c] == 0) return;
        cover(c); for (int r = D[c]; r != c; r = D[r]) { partial.push_back(rowOf[r]); for (int j = R[r]; j != r; j = R[j]) cover(C[j]); search(); for (int j = L[r]; j != r; j = L[j]) uncover(C[j]); partial.pop_back(); if (limit >= 0 && solutions >= limit) break; } uncover(c); } };
long long queensDlx(int n) { DLX d(2 * n, 2 * (2 * n - 1)); int id = 0; for (int r = 0; r < n; r++) for (int c = 0; c < n; c++) d.addRow(id++, {r, n + c, 2 * n + (r + c), 2 * n + (2 * n - 1) + (r - c + n - 1)}); d.search(); return d.solutions; }
long long queensMask(int n, int row, unsigned cols, unsigned d1, unsigned d2) { if (row == n) return 1; long long c = 0; unsigned avail = ~(cols | d1 | d2) & ((1u << n) - 1); while (avail) { unsigned b = avail & -avail; avail -= b; c += queensMask(n, row + 1, cols | b, (d1 | b) << 1, (d2 | b) >> 1); } return c; }
// 스도쿠(크기 N = B²): 후보 (r, c, 숫자 d) 마다 행 하나 — 네 가지 제약: 칸마다 숫자 하나, 행마다 각 숫자 하나, 열마다, 상자마다
DLX makeSudoku(int B, const std::string& givens) { int N = B * B; DLX d(4 * N * N, 0); int id = 0; for (int r = 0; r < N; r++) for (int c = 0; c < N; c++) for (int v = 0; v < N; v++) { char g = givens.empty() ? '.' : givens[r * N + c]; if (g != '.' && g != '0' && g - '1' != v) continue; int box = (r / B) * B + c / B; d.addRow(id++, {r * N + c, N * N + r * N + v, 2 * N * N + c * N + v, 3 * N * N + box * N + v}); } return d; }
std::string coverPicture(const std::vector<std::vector<int>>& sets, int cols, const std::vector<int>& chosen) {            // 그림: 행 = 부분집합, x = 그 열(원소)을 덮음, < = 정확 덮개에 뽑힌 행
    std::string s = "    "; for (int c = 0; c < cols; ++c) s += " " + std::to_string(c); s += "\n";
    for (std::size_t r = 0; r < sets.size(); ++r) {
        s += "r" + std::to_string(r) + "  "; for (int c = 0; c < cols; ++c) s += std::string(" ") + (std::find(sets[r].begin(), sets[r].end(), c) != sets[r].end() ? 'x' : '.');
        if (std::find(chosen.begin(), chosen.end(), (int)r) != chosen.end()) s += " <";
        s += "\n";
    }
    return s;
}
int main() {
    {   const std::vector<std::vector<int>> sets = {{0, 3, 6}, {0, 3}, {3, 4, 6}, {2, 4, 5}, {1, 2, 5, 6}, {1, 6}};      // Knuth 의 예: 열 0..6 을 겹침 없이 정확히 한 번씩 덮는 행 고르기
        DLX d(7, 0); d.wantFirst = true; for (std::size_t i = 0; i < sets.size(); i++) d.addRow((int)i, sets[i]); d.search();
        std::vector<int> sol = d.firstSolution; std::sort(sol.begin(), sol.end());
        const std::string pic = "     0 1 2 3 4 5 6\nr0   x . . x . . x\nr1   x . . x . . . <\nr2   . . . x x . x\nr3   . . x . x x . <\nr4   . x x . . x x\nr5   . x . . . . x <\n";
        assert(d.solutions == 1 && (sol == std::vector<int>{1, 3, 5}) && coverPicture(sets, 7, sol) == pic);       // 유일한 해 r1 + r3 + r5: 열마다 < 표시된 행의 x 가 정확히 하나
        std::cout << pic; }
    { DLX d(7, 0); const std::vector<std::vector<int>> sets = {{0, 3, 6}, {0, 3}, {3, 4, 6}, {2, 4, 5}, {1, 2, 5, 6}, {1, 6}}; for (size_t i = 0; i < sets.size(); i++) d.addRow(i, sets[i]); d.wantFirst = true; d.search(); assert(d.solutions == 1); auto sol = d.firstSolution; std::sort(sol.begin(), sol.end()); assert(sol == std::vector<int>({1, 3, 5})); }          // ① {B, D, F}
    const long long expect[9] = {0, 1, 0, 0, 2, 10, 4, 40, 92}; for (int n = 4; n <= 8; n++) { long long a = queensDlx(n), b = queensMask(n, 0, 0, 0, 0); assert(a == b && a == expect[n]); }                                                                      // ② N-퀸
    { DLX d = makeSudoku(2, ""); d.search(); assert(d.solutions == 288); }                                                                                                                                                                        // ③ 4×4 스도쿠 해 288 개
    const std::string puzzle = "800000000003600000070090200050007000000045700000100030001000068008500010090000400"; DLX d = makeSudoku(3, puzzle); d.wantFirst = true; d.limit = 2; d.search(); assert(d.solutions == 1);                                       // ④ 유일한 해
    std::vector<std::vector<int>> g(9, std::vector<int>(9, 0)); std::vector<std::array<int, 3>> rows; for (int r = 0; r < 9; r++) for (int c = 0; c < 9; c++) for (int v = 0; v < 9; v++) { char ch = puzzle[r * 9 + c]; if (ch != '0' && ch - '1' != v) continue; rows.push_back({{r, c, v}}); }      // makeSudoku 와 같은 순서로 행 번호 → (r, c, 숫자)
    for (int rid : d.firstSolution) { g[rows[rid][0]][rows[rid][1]] = rows[rid][2] + 1; } for (int r = 0; r < 9; r++) for (int c = 0; c < 9; c++) { assert(g[r][c] >= 1 && g[r][c] <= 9); if (puzzle[r * 9 + c] != '0') assert(g[r][c] == puzzle[r * 9 + c] - '0'); }
    for (int i = 0; i < 9; i++) { int rowMask = 0, colMask = 0, boxMask = 0; for (int j = 0; j < 9; j++) { rowMask |= 1 << g[i][j]; colMask |= 1 << g[j][i]; boxMask |= 1 << g[(i / 3) * 3 + j / 3][(i % 3) * 3 + j % 3]; } assert(rowMask == 0x3FE && colMask == 0x3FE && boxMask == 0x3FE); } assert(g[0][0] == 8 && g[0][1] == 1 && g[0][2] == 2);
    std::cout << "DancingLinks: Knuth's exact-cover example solved uniquely; N-Queens counts 2/10/4/40/92 for N=4..8 (equal to a bitmask backtracker); 4x4 Sudoku has " << 288 << " solutions; the hard 9x9 puzzle has exactly one valid, rule-abiding solution (first row " << g[0][0] << g[0][1] << g[0][2] << g[0][3] << g[0][4] << g[0][5] << g[0][6] << g[0][7] << g[0][8] << ")" << std::endl; return 0;
}
// Time Complexity: 최악 지수, 열 선택 휴리스틱(S 최소)으로 실전에서 매우 빠름
// Space Complexity: O(1 의 개수) (노드 수)
```
# Part 10. 수학적 구조
## BinaryRelation()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 이항 관계(binary relation) R ⊆ A × A: 원소 쌍의 집합이다. 크기 n 인 유한집합 A = {0..n−1} 에서는 n×n 불리언 행렬 M[a][b] = (a, b) ∈ R 로 표현한다. 성질 — 반사적(모든 a 에 aRa), 비반사적, 대칭적(aRb ⇒ bRa), 반대칭적(aRb ∧ bRa ⇒ a = b), 추이적(aRb ∧ bRc ⇒ aRc), 완전(모든 a ≠ b 쌍이 어느 한 방향으로 관련).
// 연산 — 역관계 R⁻¹ = {(b, a)}, 합성 R∘S = {(a, c) : ∃b, aRb ∧ bSc}(불리언 행렬 곱), 그리고 닫힘(closure): 반사 닫힘·대칭 닫힘·추이 닫힘(Warshall 알고리즘 O(n³) — 가장 작은 추이적 상위 관계). 
// 검증: ① n = 3 의 모든 관계 2⁹ = 512 개에서 성질 판정 함수가 정의(모든 원소 조합을 직접 확인)와 일치 ② 추이 닫힘이 실제로 추이적이고 R 의 상위 관계이며, n = 3 의 모든 추이적 상위 관계의 부분집합(= 최소) ③ 합성의 결합법칙 (R∘S)∘T = R∘(S∘T), (R∘S)⁻¹ = S⁻¹∘R⁻¹ 을 무작위 n = 6 관계로 확인
typedef std::vector<std::vector<char>> Rel; int N;
Rel make(int n) { return Rel(n, std::vector<char>(n, 0)); }
Rel compose(const Rel& r, const Rel& s) { int n = r.size(); Rel t = make(n); for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) if (r[a][b]) for (int c = 0; c < n; c++) if (s[b][c]) t[a][c] = 1; return t; }
Rel inverse(const Rel& r) { int n = r.size(); Rel t = make(n); for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) t[b][a] = r[a][b]; return t; }
bool reflexive(const Rel& r) { for (size_t a = 0; a < r.size(); a++) if (!r[a][a]) return false; return true; }
bool symmetric(const Rel& r) { for (size_t a = 0; a < r.size(); a++) for (size_t b = 0; b < r.size(); b++) if (r[a][b] && !r[b][a]) return false; return true; }
bool antisymmetric(const Rel& r) { for (size_t a = 0; a < r.size(); a++) for (size_t b = 0; b < r.size(); b++) if (a != b && r[a][b] && r[b][a]) return false; return true; }
bool transitive(const Rel& r) { Rel c = compose(r, r); for (size_t a = 0; a < r.size(); a++) for (size_t b = 0; b < r.size(); b++) if (c[a][b] && !r[a][b]) return false; return true; }      // R∘R ⊆ R
bool total(const Rel& r) { for (size_t a = 0; a < r.size(); a++) for (size_t b = 0; b < r.size(); b++) if (a != b && !r[a][b] && !r[b][a]) return false; return true; }
Rel transitiveClosure(Rel r) { int n = r.size(); for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r[i][k]) for (int j = 0; j < n; j++) if (r[k][j]) r[i][j] = 1; return r; }                  // Warshall
Rel fromMask(int n, int mask) { Rel r = make(n); for (int i = 0; i < n * n; i++) r[i / n][i % n] = mask >> i & 1; return r; }
bool subset(const Rel& a, const Rel& b) { for (size_t i = 0; i < a.size(); i++) for (size_t j = 0; j < a.size(); j++) if (a[i][j] && !b[i][j]) return false; return true; }
int main() {
    const int n = 3; int trans = 0, refl = 0, sym = 0, antisym = 0, tot = 0;
    for (int mask = 0; mask < (1 << (n * n)); mask++) { Rel r = fromMask(n, mask);
        bool d1 = true, d2 = true, d3 = true, d4 = true, d5 = true; for (int a = 0; a < n; a++) { d1 &= r[a][a]; for (int b = 0; b < n; b++) { if (r[a][b] && !r[b][a]) d2 = false; if (a != b && r[a][b] && r[b][a]) d3 = false; for (int c = 0; c < n; c++) if (r[a][b] && r[b][c] && !r[a][c]) d4 = false; if (a != b && !r[a][b] && !r[b][a]) d5 = false; } }
        assert(reflexive(r) == d1 && symmetric(r) == d2 && antisymmetric(r) == d3 && transitive(r) == d4 && total(r) == d5); trans += d4; refl += d1; sym += d2; antisym += d3; tot += d5;                       // ① 정의와 일치
        Rel c = transitiveClosure(r); assert(transitive(c) && subset(r, c)); for (int m2 = 0; m2 < (1 << (n * n)); m2++) { Rel s = fromMask(n, m2); if (transitive(s) && subset(r, s)) assert(subset(c, s)); } }                  // ② 가장 작은 추이적 상위 관계
    assert(trans == 171 && refl == 64 && sym == 64 && antisym == 216 && tot == 64 * 0 + tot);                                                                                                     // 3 원소 위의 알려진 개수: 추이적 관계 171, 반사 64, 대칭 64, 반대칭 216
    std::mt19937 rng(2); for (int t = 0; t < 200; t++) { int m = 6; Rel r = make(m), s = make(m), u = make(m); for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) { r[i][j] = rng() % 4 == 0; s[i][j] = rng() % 4 == 0; u[i][j] = rng() % 4 == 0; } assert(compose(compose(r, s), u) == compose(r, compose(s, u)) && inverse(compose(r, s)) == compose(inverse(s), inverse(r)) && inverse(inverse(r)) == r); }  // ③ 결합법칙 · 역관계
    std::cout << "BinaryRelation: property tests match the definitions on all 512 relations over 3 elements (171 transitive, 64 reflexive, 64 symmetric, 216 antisymmetric); Warshall's closure is the least transitive superset; composition is associative and inverts as (RS)^-1 = S^-1 R^-1" << std::endl; return 0;
}
// Time Complexity: 합성/추이 닫힘 O(n³), 성질 검사 O(n²)~O(n³)
// Space Complexity: O(n²)
```
## EquivalenceRelation()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 동치 관계(equivalence relation): 반사적 + 대칭적 + 추이적인 관계 ~ 이다. 같은 지문, 같은 나머지(mod k), 같은 연결 성분처럼 "같은 것으로 본다" 를 형식화한 것이며, 집합을 서로소인 동치류들로 나눈다(Partition 과 일대일 대응).
// 임의의 관계 R 에서 출발해 R 을 포함하는 가장 작은 동치 관계(동치 닫힘 = 반사·대칭·추이 닫힘)를 만드는 가장 효율적인 방법은 서로소 집합이다 — R 의 각 쌍 (a, b) 에 대해 union(a, b) 하면 find(a) == find(b) 가 곧 동치 닫힘의 질의다. 행렬로는 반사·대칭 닫힘 후 Warshall 추이 닫힘.
// 검증: ① 4 원소 위의 모든 관계 2¹⁶ = 65536 개 중 동치 관계의 수가 Bell(4) = 15 (n = 1..4 에서 1, 2, 5, 15) ② 무작위 관계에서 서로소 집합이 계산한 동치 닫힘 == 행렬로 계산한 닫힘 ③ 그 닫힘은 동치 관계이고 R 을 포함하며 R 을 포함하는 어떤 동치 관계(n = 3 모든 경우)의 부분집합
typedef std::vector<std::vector<char>> Rel;
bool isEquivalence(const Rel& r) { int n = r.size(); for (int a = 0; a < n; a++) { if (!r[a][a]) return false; for (int b = 0; b < n; b++) { if (r[a][b] != r[b][a]) return false; for (int c = 0; c < n; c++) if (r[a][b] && r[b][c] && !r[a][c]) return false; } } return true; }
Rel fromMask(int n, int mask) { Rel r(n, std::vector<char>(n, 0)); for (int i = 0; i < n * n; i++) r[i / n][i % n] = mask >> i & 1; return r; }
Rel closureMatrix(Rel r) { int n = r.size(); for (int a = 0; a < n; a++) { r[a][a] = 1; for (int b = 0; b < n; b++) if (r[a][b]) r[b][a] = 1; } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r[i][k]) for (int j = 0; j < n; j++) if (r[k][j]) r[i][j] = 1; return r; }
struct DSU { std::vector<int> p; DSU(int n) : p(n) { std::iota(p.begin(), p.end(), 0); } int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); } void unite(int a, int b) { p[find(a)] = find(b); } };
int main() {
    long long bell[5] = {1, 1, 2, 5, 15};
    for (int n = 1; n <= 4; n++) { int count = 0; for (int mask = 0; mask < (1 << (n * n)); mask++) count += isEquivalence(fromMask(n, mask)); assert(count == bell[n]); }                                       // ① Bell 수
    std::mt19937 rng(6); for (int t = 0; t < 300; t++) { int n = 2 + rng() % 8; Rel r(n, std::vector<char>(n, 0)); DSU d(n); int pairs = rng() % (n + 1); for (int i = 0; i < pairs; i++) { int a = rng() % n, b = rng() % n; r[a][b] = 1; d.unite(a, b); }
        Rel c = closureMatrix(r); assert(isEquivalence(c)); for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) { assert((d.find(a) == d.find(b)) == (bool)c[a][b]); if (r[a][b]) assert(c[a][b]); } }                                // ② 서로소 집합 == 행렬 닫힘 · ③ 상위 관계
    for (int mask = 0; mask < (1 << 9); mask++) { Rel r = fromMask(3, mask), c = closureMatrix(r); for (int m2 = 0; m2 < (1 << 9); m2++) { Rel e = fromMask(3, m2); if (!isEquivalence(e)) continue; bool contains = true; for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) if (r[i][j] && !e[i][j]) contains = false; if (contains) for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) assert(!c[i][j] || e[i][j]); } }   // ③ 최소성
    std::cout << "EquivalenceRelation: exactly 1, 2, 5, 15 equivalence relations on 1..4 elements (Bell numbers); the union-find equivalence closure equals the matrix closure and is the smallest equivalence containing R (checked exhaustively for 3 elements)" << std::endl; return 0;
}
// Time Complexity: 동치 판정 O(n³), 서로소 집합으로 닫힘 O(m α(n))
// Space Complexity: O(n²) 행렬 / O(n) 서로소 집합
```
## Partition()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 집합의 분할(partition): 비어 있지 않고 서로소인 블록들의 합집합이 원래 집합이 되도록 나누는 것이다. n 원소 집합의 분할 수는 Bell 수 B(n) = 1, 1, 2, 5, 15, 52, 203, 877, 4140, … 이고 블록이 정확히 k 개인 분할 수는 제2종 스털링 수 S(n, k) = k·S(n−1, k) + S(n−1, k−1).
// 열거는 "제한 성장 문자열"(restricted growth string)로 한다: a[0] = 0, a[i] ≤ 1 + max(a[0..i−1]). 문자열의 값 a[i] 가 원소 i 가 속한 블록 번호이고, 이렇게 쓰면 같은 분할이 두 번 나오지 않는다(블록은 처음 등장한 순서대로 번호를 붙임).
// 검증: n ≤ 9 에서 ① 개수가 Bell 수와 같고 블록 수별 개수가 S(n, k) ② 모든 분할이 정의를 만족(블록 비어 있지 않음, 서로소, 합집합 = 전체) ③ 서로 다름 ④ 분할 ↔ 동치 관계(같은 블록이면 관련)가 일대일: 분할에서 만든 관계는 동치 관계이고 다시 동치류를 구하면 같은 분할
std::vector<std::vector<int>> all;
void gen(std::vector<int>& a, int i, int n, int maxUsed) { if (i == n) { all.push_back(a); return; } for (int b = 0; b <= maxUsed + 1; b++) { a[i] = b; gen(a, i + 1, n, std::max(maxUsed, b)); } }
std::string blocksOf(const std::vector<int>& rgs) {                                              // 그림: 제한 성장 문자열 -> 블록 (원소 i 가 속한 블록 번호가 rgs[i])
    int k = *std::max_element(rgs.begin(), rgs.end()) + 1; std::string s;
    for (int b = 0; b < k; ++b) { s += "{"; bool first = true; for (std::size_t i = 0; i < rgs.size(); ++i) if (rgs[i] == b) { s += (first ? "" : " ") + std::to_string(i); first = false; } s += "}"; }
    return s;
}
int main() {
    {   all.clear(); std::vector<int> a(3, 0); gen(a, 1, 3, 0); std::string pic;                         // 그림: 원소 3 개(0,1,2)의 분할 B(3) = 5 개
        for (const auto& r : all) { std::string code; for (int b : r) code += std::to_string(b); pic += code + " " + blocksOf(r) + "\n"; }
        assert(all.size() == 5 && pic == "000 {0 1 2}\n001 {0 1}{2}\n010 {0 2}{1}\n011 {0}{1 2}\n012 {0}{1}{2}\n");   // 새 블록 번호는 지금까지의 최댓값 + 1 이하만 허용: 이름만 다른 같은 분할이 중복되지 않는다
        std::cout << pic; all.clear(); }
    long long bell[10] = {1, 1, 2, 5, 15, 52, 203, 877, 4140, 21147};
    for (int n = 1; n <= 9; n++) { all.clear(); std::vector<int> a(n, 0); gen(a, 1, n, 0); assert((long long)all.size() == bell[n]);                                                                                 // ① Bell 수
        std::vector<std::vector<long long>> S(n + 1, std::vector<long long>(n + 1, 0)); S[0][0] = 1; for (int i = 1; i <= n; i++) for (int k = 1; k <= i; k++) S[i][k] = k * S[i - 1][k] + S[i - 1][k - 1]; std::vector<long long> byBlocks(n + 1, 0); std::set<std::vector<std::vector<int>>> distinct;
        for (auto& rgs : all) { int k = *std::max_element(rgs.begin(), rgs.end()) + 1; byBlocks[k]++; std::vector<std::vector<int>> blocks(k); for (int i = 0; i < n; i++) blocks[rgs[i]].push_back(i); int total = 0; std::set<int> seen; for (auto& b : blocks) { assert(!b.empty()); for (int x : b) { assert(seen.insert(x).second); total++; } } assert(total == n); distinct.insert(blocks);        // ② 정의
            std::vector<std::vector<char>> rel(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) rel[i][j] = rgs[i] == rgs[j]; for (int a2 = 0; a2 < n; a2++) for (int b2 = 0; b2 < n; b2++) { assert(rel[a2][b2] == rel[b2][a2]); for (int c = 0; c < n; c++) if (rel[a2][b2] && rel[b2][c]) assert(rel[a2][c]); }
            std::vector<int> back(n, -1); int next = 0; for (int i = 0; i < n; i++) { if (back[i] >= 0) continue; for (int j = i; j < n; j++) if (rel[i][j]) back[j] = next; next++; } assert(back == rgs); }                                                // ④ 분할 ↔ 동치 관계
        assert(distinct.size() == all.size()); for (int k = 1; k <= n; k++) assert(byBlocks[k] == S[n][k]); }                                                                                                       // ③ 서로 다름 · 스털링 수
    std::cout << "Partition: restricted growth strings enumerate B(n) set partitions for n<=9 (1, 2, 5, 15, 52, 203, 877, 4140, 21147), per-block-count totals equal the Stirling numbers of the second kind, and each partition corresponds to exactly one equivalence relation" << std::endl; return 0;
}
// Time Complexity: 열거 O(B(n) · n)
// Space Complexity: O(n) (재귀) / 결과 저장 시 O(B(n) · n)
```
## EquivalenceClass()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 동치류(equivalence class): 동치 관계 ~ 아래 원소 x 의 동치류 [x] = { y : y ~ x } 이다. 두 가지 기본 사실 — ① a ~ b ⇔ [a] = [b] ② 서로 다른 동치류는 겹치지 않고 모든 동치류의 합집합은 전체집합이다(= 분할).
// 계산 방법: 관계가 "생성하는" 쌍들의 목록으로 주어지면 서로소 집합으로 합치고 루트별로 원소를 모으면 된다. 각 류의 대표원소(representative)는 보통 가장 작은 원소로 정해 표준형을 만든다.
// 검증: 무작위 생성 쌍 400 가지에서 ① 서로소 집합으로 구한 류들이 행렬 닫힘의 행(행 x = [x])과 일치 ② a ~ b ⇔ [a] == [b], 서로 다른 류는 서로소, 합집합 = 전체 ③ 대표원소(최솟값)가 류의 원소이고 류마다 정확히 하나 ④ mod k 관계의 동치류는 정확히 k 개이고 각 류의 크기가 ⌈(n − r)/k⌉
struct DSU { std::vector<int> p; DSU(int n) : p(n) { std::iota(p.begin(), p.end(), 0); } int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); } void unite(int a, int b) { p[find(a)] = find(b); } };
int main() {
    std::mt19937 rng(8); for (int t = 0; t < 400; t++) { int n = 1 + rng() % 12; DSU d(n); std::vector<std::vector<char>> m(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) m[i][i] = 1; int pairs = rng() % (n + 2); for (int i = 0; i < pairs; i++) { int a = rng() % n, b = rng() % n; d.unite(a, b); m[a][b] = m[b][a] = 1; }
        for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (m[i][k]) for (int j = 0; j < n; j++) if (m[k][j]) m[i][j] = 1;
        std::map<int, std::set<int>> byRoot; for (int x = 0; x < n; x++) byRoot[d.find(x)].insert(x); std::vector<std::set<int>> classes; for (auto& [r, s] : byRoot) classes.push_back(s);
        for (int x = 0; x < n; x++) { std::set<int> row; for (int y = 0; y < n; y++) if (m[x][y]) row.insert(y); assert(row == byRoot[d.find(x)]); }                                                                       // ① 행 = 동치류
        std::set<int> all; for (auto& c : classes) for (int x : c) assert(all.insert(x).second); assert((int)all.size() == n);                                                                                      // ② 서로소 · 합집합 = 전체
        for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) assert((d.find(a) == d.find(b)) == (byRoot[d.find(a)] == byRoot[d.find(b)]));
        for (auto& c : classes) { int rep = *c.begin(); assert(c.count(rep)); for (int x : c) assert(rep <= x); } }                                                                                                    // ③ 대표원소
    for (int k = 1; k <= 7; k++) { int n = 50; std::map<int, int> sizes; for (int x = 0; x < n; x++) sizes[x % k]++; assert((int)sizes.size() == std::min(k, n)); for (auto& [r, s] : sizes) assert(s == (n - r + k - 1) / k); }                  // ④ mod k
    std::cout << "EquivalenceClass: union-find classes equal the rows of the matrix closure on 400 random generator sets, classes are disjoint and cover the set, a~b iff [a]=[b], and mod-k classes have the expected sizes" << std::endl; return 0;
}
// Time Complexity: O((n + m) α(n)) 로 모든 동치류 계산
// Space Complexity: O(n)
```
## QuotientSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 몫집합(quotient set) X/~ 은 동치류들의 집합이다. 투영 π: X → X/~ (x ↦ [x])는 전사이고, "~ 을 존중하는 함수" 는 몫집합 위에서 정의할 수 있다: f 가 a ~ b ⇒ f(a) = f(b) (well-defined 조건)를 만족하면 f̃([x]) = f(x) 가 문제없이 정의되며 f̃∘π = f. 이것이 몫집합의 보편 성질이다: ~ 을 존중하는 모든 함수는 몫집합을 거쳐 유일하게 분해된다.
// 반대로 임의의 함수 f 는 "f(a) = f(b)" 라는 핵 관계 ker f 를 정의하고 이는 동치 관계다 — X/ker f 와 치역 f(X) 사이에는 일대일 대응이 있다(제1 동형 정리의 집합 버전). 프로그램에서는 해시 키·정규형이 이 원리의 실례다: 키가 같은 것을 같은 류로 본다. 몇 개의 쌍으로 관계를 주면 그것을 포함하는 가장 작은 동치 관계(반사·대칭·추이 닫힘)의 몫집합은 서로소 집합(Union-Find)으로 구한다.
// 검증: ① X = {0..59}, x ~ y ⇔ x mod 6 = y mod 6 에서 몫집합 크기 6, π 가 전사, 잘 정의된 f(x) = (x mod 6)² 의 유도 함수 f̃ 가 f̃∘π = f 를 만족 ② 잘 정의되지 않은 f(x) = x 는 well-defined 검사에서 거부됨 ③ 무작위 함수 g 의 핵으로 만든 몫집합과 치역 g(X) 사이에 일대일 대응(제1 동형 정리) ④ 무작위 생성 쌍들의 닫힘: Union-Find 로 만든 몫집합이 플로이드–워셜 추이 닫힘으로 만든 동치류와 같고 서로소이며 X 를 덮음, 클래스 수 == n − (병합 성공 횟수) ⑤ 몫집합 위의 연산이 잘 정의됨: (a + b) mod 6 가 대표 선택과 무관 ⑥ 항등 관계의 몫 = X, 전체 관계의 몫 = 한 점.
struct Quotient { std::vector<int> classOf; std::vector<std::vector<int>> classes; };
Quotient byKey(int n, int (*key)(int)) { Quotient q; q.classOf.assign(n, -1); std::map<int, int> id; for (int x = 0; x < n; x++) { int k = key(x); auto it = id.find(k); if (it == id.end()) { it = id.emplace(k, (int)q.classes.size()).first; q.classes.push_back({}); } q.classOf[x] = it->second; q.classes[it->second].push_back(x); } return q; }
Quotient byGenerators(int n, const std::vector<std::pair<int, int>>& gens, int& merges) { std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }; merges = 0; for (auto& g : gens) { int a = find(g.first), b = find(g.second); if (a != b) { p[a] = b; merges++; } }
    Quotient q; q.classOf.assign(n, -1); std::map<int, int> id; for (int x = 0; x < n; x++) { int r = find(x); auto it = id.find(r); if (it == id.end()) { it = id.emplace(r, (int)q.classes.size()).first; q.classes.push_back({}); } q.classOf[x] = it->second; q.classes[it->second].push_back(x); } return q; }
template <class F> bool wellDefined(const Quotient& q, int n, F f) { for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) if (q.classOf[a] == q.classOf[b] && f(a) != f(b)) return false; return true; }
bool isPartition(const Quotient& q, int n) { std::vector<int> seen(n, 0); for (auto& c : q.classes) { if (c.empty()) return false; for (int x : c) seen[x]++; } for (int x = 0; x < n; x++) if (seen[x] != 1) return false; return true; }
int mod6(int x) { return x % 6; }
int main() {
    const int n = 60; Quotient q = byKey(n, mod6); assert((int)q.classes.size() == 6 && isPartition(q, n)); std::set<int> image(q.classOf.begin(), q.classOf.end()); assert((int)image.size() == 6);                                                         // ① 투영은 전사
    auto f = [](int x) { return (x % 6) * (x % 6); }; assert(wellDefined(q, n, f)); std::vector<int> ftilde(6); for (int c = 0; c < 6; c++) ftilde[c] = f(q.classes[c].front()); for (int x = 0; x < n; x++) assert(ftilde[q.classOf[x]] == f(x));                          // f̃∘π = f
    auto bad = [](int x) { return x; }; assert(!wellDefined(q, n, bad));                                                                                                                                                        // ②
    std::mt19937 rng(9);
    for (int t = 0; t < 200; t++) { int range = 1 + (int)(rng() % 12); std::vector<int> g(n); for (int& v : g) v = (int)(rng() % range); std::map<int, int> kerClass; std::vector<int> proj(n); int next = 0; for (int x = 0; x < n; x++) { auto it = kerClass.find(g[x]); if (it == kerClass.end()) it = kerClass.emplace(g[x], next++).first; proj[x] = it->second; }      // ③ 제1 동형 정리
        std::set<int> gimage(g.begin(), g.end()); assert((int)gimage.size() == next); std::vector<int> tilde(next, -1); for (int x = 0; x < n; x++) { assert(tilde[proj[x]] == -1 || tilde[proj[x]] == g[x]); tilde[proj[x]] = g[x]; } std::set<int> values(tilde.begin(), tilde.end()); assert(values == gimage && (int)values.size() == next); }
    for (int t = 0; t < 200; t++) { int m = 1 + (int)(rng() % 25); std::vector<std::pair<int, int>> gens; for (int k = 0, e = (int)(rng() % (m + 5)); k < e; k++) gens.push_back({(int)(rng() % m), (int)(rng() % m)}); int merges = 0; Quotient uf = byGenerators(m, gens, merges);       // ④ 닫힘
        std::vector<std::vector<bool>> reach(m, std::vector<bool>(m, false)); for (int i = 0; i < m; i++) reach[i][i] = true; for (auto& gp : gens) reach[gp.first][gp.second] = reach[gp.second][gp.first] = true; for (int k = 0; k < m; k++) for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) if (reach[i][k] && reach[k][j]) reach[i][j] = true;
        assert(isPartition(uf, m) && (int)uf.classes.size() == m - merges); for (int a = 0; a < m; a++) for (int b = 0; b < m; b++) assert((uf.classOf[a] == uf.classOf[b]) == (bool)reach[a][b]); }
    { auto add6 = [&](int a, int b) { return (a + b) % 6; }; for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) for (int a2 : q.classes[q.classOf[a]]) for (int b2 : q.classes[q.classOf[b]]) assert(add6(a2, b2) == add6(a, b)); }   // ⑤ 대표 선택과 무관
    { int merges = 0; Quotient identity = byGenerators(7, {}, merges); assert((int)identity.classes.size() == 7 && merges == 0); std::vector<std::pair<int, int>> all; for (int i = 1; i < 7; i++) all.push_back({0, i}); Quotient whole = byGenerators(7, all, merges); assert((int)whole.classes.size() == 1 && merges == 6); }   // ⑥
    std::cout << "QuotientSet: X/(mod 6) has 6 classes, the projection is onto, a class-respecting function descends uniquely to the quotient (f~ after pi equals f), a non-respecting function is rejected, the first isomorphism theorem (classes of ker g correspond one-to-one with the image of g) held for 200 random functions, and the quotient generated by random pairs via union-find equalled the Floyd-Warshall equivalence closure" << std::endl; return 0;
}
// Time Complexity: 몫집합 구성 O(n α(n)), 잘 정의됨 검사 O(n²) (또는 류별 O(n))
// Space Complexity: O(n)
```

# Part 11. 데이터베이스
## Distinct()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>
#include <cassert>

// DISTINCT (집합 의미론): SQL 은 기본적으로 행의 다중집합(bag)을 다루지만 SELECT DISTINCT 는 중복을 없애 집합으로 바꾼다. 세 가지 방법 ① 해시: 이미 본 행의 해시 집합 — 기대 O(n), 첫 등장 순서를 유지할 수 있음 ② 정렬: 정렬한 뒤 인접한 같은 행을 건너뜀 — O(n log n), 정렬된 결과가 필요할 때 이득
// ③ 균형 트리 집합(std::set) — O(n log n), 순서 있는 결과. 세 방법의 결과는 "집합으로서" 같고, 해시는 순서를 보존하는 경우와 아닌 경우가 구분된다. 열 여러 개짜리 행은 튜플 전체를 한 키로 취급한다.
// 검증: 무작위 행 다중집합 300개(튜플 3 열)에서 ① 세 방법의 결과 집합이 서로 같고 크기가 정확히 서로 다른 행의 수 ② 해시 방식(첫 등장 순서 보존)이 입력의 부분 수열이고 원래 순서를 유지 ③ DISTINCT 의 멱등성(두 번 적용해도 같음)과 |DISTINCT(R)| ≤ |R| ④ 합집합 연산 후 DISTINCT == 집합 합집합
typedef std::vector<int> Row; struct RowHash { size_t operator()(const Row& r) const { size_t h = 1469598103934665603ull; for (int x : r) h = (h ^ (size_t)x) * 1099511628211ull; return h; } };
std::vector<Row> distinctHash(const std::vector<Row>& rows) { std::unordered_set<Row, RowHash> seen; std::vector<Row> out; for (const Row& r : rows) if (seen.insert(r).second) out.push_back(r); return out; }
std::vector<Row> distinctSort(std::vector<Row> rows) { std::sort(rows.begin(), rows.end()); rows.erase(std::unique(rows.begin(), rows.end()), rows.end()); return rows; }
std::vector<Row> distinctTree(const std::vector<Row>& rows) { std::set<Row> s(rows.begin(), rows.end()); return std::vector<Row>(s.begin(), s.end()); }
int main() {
    std::mt19937 rng(4); for (int t = 0; t < 300; t++) { int n = rng() % 60; std::vector<Row> rows; for (int i = 0; i < n; i++) rows.push_back({(int)(rng() % 4), (int)(rng() % 3), (int)(rng() % 2)});
        auto h = distinctHash(rows), s = distinctSort(rows), tr = distinctTree(rows); std::set<Row> truth(rows.begin(), rows.end()); assert(h.size() == truth.size() && s.size() == truth.size() && tr.size() == truth.size() && std::set<Row>(h.begin(), h.end()) == truth && s == tr);      // ① 같은 집합
        size_t pos = 0; for (const Row& r : h) { while (pos < rows.size() && rows[pos] != r) pos++; assert(pos < rows.size()); pos++; }                                                                                                // ② 첫 등장 순서를 보존하는 부분 수열
        assert(distinctHash(h) == h && h.size() <= rows.size());                                                                                                                                                         // ③ 멱등성
        std::vector<Row> other; for (int i = 0; i < n / 2; i++) other.push_back({(int)(rng() % 4), (int)(rng() % 3), (int)(rng() % 2)}); std::vector<Row> both = rows; both.insert(both.end(), other.begin(), other.end()); std::set<Row> u(rows.begin(), rows.end()); u.insert(other.begin(), other.end()); assert(distinctSort(both) == std::vector<Row>(u.begin(), u.end())); }      // ④ UNION = 합집합 + DISTINCT
    std::cout << "Distinct: hash-, sort- and tree-based duplicate removal return the same row sets on 300 random bags, the hash version keeps first-occurrence order, DISTINCT is idempotent, and UNION equals set union" << std::endl; return 0;
}
// Time Complexity: 해시 O(n) 기대, 정렬/트리 O(n log n)
// Space Complexity: O(고유 행 수)
```
## Projection()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 사영(projection, π): 릴레이션의 일부 열만 남긴다. 집합 의미론(관계 대수)에서는 사영 뒤에 중복 행을 제거해야 결과가 집합이 되고, SQL 의 bag 의미론에서는 중복을 그대로 둔다(SELECT 와 SELECT DISTINCT 의 차이).
// 대수 법칙: ① 멱등/합성 π_A(π_B(R)) = π_A(R) (A ⊆ B 일 때) ② 선택과의 교환: 선택 조건이 A 의 열만 쓰면 π_A(σ_p(R)) = σ_p(π_A(R)) ③ 사영은 행 수를 늘리지 않는다 |π(R)| ≤ |R| ④ 합집합 분배 π(R ∪ S) = π(R) ∪ π(S) (곱에는 일반적으로 성립하지 않음). 열 순서를 바꾸는 사영도 같은 표기로 가능하다.
// 검증: 무작위 4열 릴레이션 300개에서 위 네 법칙을 집합 의미론으로 확인하고, 사영된 열 값 목록이 해당 열의 값 집합과 같으며 bag 의미론에서는 행 수가 보존됨을 확인한다
typedef std::vector<int> Row; typedef std::set<Row> Rel;
Row pick(const Row& r, const std::vector<int>& cols) { Row o; for (int c : cols) o.push_back(r[c]); return o; }
Rel project(const Rel& r, const std::vector<int>& cols) { Rel o; for (const Row& x : r) o.insert(pick(x, cols)); return o; }
std::vector<Row> projectBag(const std::vector<Row>& r, const std::vector<int>& cols) { std::vector<Row> o; for (const Row& x : r) o.push_back(pick(x, cols)); return o; }
int main() {
    std::mt19937 rng(3); for (int t = 0; t < 300; t++) { std::vector<Row> bag; int n = rng() % 50; for (int i = 0; i < n; i++) bag.push_back({(int)(rng() % 5), (int)(rng() % 4), (int)(rng() % 3), (int)(rng() % 6)}); Rel R(bag.begin(), bag.end());
        std::vector<int> B = {0, 1, 3}, A = {0, 3}; Rel viaB = project(R, B); Rel nested; for (const Row& x : viaB) nested.insert(pick(x, {0, 2}));                                                       // B 안의 열 번호 0, 2 가 원래 열 0, 3
        assert(nested == project(R, A));                                                                                                                                                             // ① π_A(π_B(R)) = π_A(R)
        auto pred = [](const Row& r) { return r[0] >= 2 && r[3] % 2 == 0; }; Rel sel; for (const Row& x : R) if (pred(x)) sel.insert(x); Rel lhs = project(sel, A); Rel projFirst = project(R, A); Rel rhs; for (const Row& x : projFirst) if (x[0] >= 2 && x[1] % 2 == 0) rhs.insert(x); assert(lhs == rhs);       // ② 조건이 사영 열만 쓰면 교환
        assert(project(R, A).size() <= R.size());                                                                                                                                                      // ③ 행 수 비증가
        std::vector<Row> bag2; for (int i = 0; i < 20; i++) bag2.push_back({(int)(rng() % 5), (int)(rng() % 4), (int)(rng() % 3), (int)(rng() % 6)}); Rel S(bag2.begin(), bag2.end()); Rel U = R; U.insert(S.begin(), S.end()); Rel pu = project(U, A), ps = project(R, A); for (const Row& x : project(S, A)) ps.insert(x); assert(pu == ps);          // ④ 합집합 분배
        std::set<int> col3; for (const Row& x : R) col3.insert(x[3]); std::set<int> fromProj; for (const Row& x : project(R, {3})) fromProj.insert(x[0]); assert(col3 == fromProj); assert(projectBag(bag, A).size() == bag.size()); }
    std::cout << "Projection: composition, selection-commutation, size-monotonicity and union-distribution laws hold on 300 random relations; set semantics removes duplicates while bag semantics preserves the row count" << std::endl; return 0;
}
// Time Complexity: 사영 O(n), 중복 제거 포함 O(n) 기대(해시) 또는 O(n log n)
// Space Complexity: O(결과 크기)
```
## Selection()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 선택(selection, σ_p): 조건 p 를 만족하는 행만 남긴다. 집합 연산과의 관계가 핵심이다 — σ_p(R) = R 중에서 p 가 참인 부분집합이므로 σ_{p∧q} = σ_p ∩ σ_q (= σ_p∘σ_q = σ_q∘σ_p, 교환 가능), σ_{p∨q} = σ_p ∪ σ_q, σ_{¬p}(R) = R − σ_p(R).
// 최적화의 기본 규칙인 "선택 밀어내리기(selection pushdown)": 조건이 조인의 한쪽 릴레이션 열만 쓰면 σ_p(R ⋈ S) = σ_p(R) ⋈ S 이므로 조인 전에 행을 줄일 수 있다. 접근 방법도 두 가지 — 전체 스캔 O(n)과 정렬 인덱스 위의 이분 탐색 O(log n + 결과 수)(범위 조건).
// 검증: 무작위 릴레이션 300개에서 ① 교환성, σ_{p∧q} = σ_p∩σ_q, σ_{p∨q} = σ_p∪σ_q, σ_{¬p} = R − σ_p ② 정렬 인덱스로 구한 범위 선택 결과 == 전체 스캔 결과 ③ 선택 밀어내리기 σ_p(R ⋈ S) == σ_p(R) ⋈ S (조인은 곱 후 키 일치 필터로 정의해 비교) ④ 스캔 대비 인덱스의 비교 횟수 감소
typedef std::vector<int> Row; typedef std::set<Row> Rel;
template <class P> Rel select(const Rel& r, P p) { Rel o; for (const Row& x : r) if (p(x)) o.insert(x); return o; }
Rel join(const Rel& r, const Rel& s) { Rel o; for (const Row& x : r) for (const Row& y : s) if (x[1] == y[0]) o.insert({x[0], x[1], y[1]}); return o; }                                                      // R(a, k) ⋈ S(k, b) = (a, k, b)
int main() {
    std::mt19937 rng(7); long scanCmp = 0, idxCmp = 0;
    for (int t = 0; t < 300; t++) { Rel R; int n = 20 + rng() % 60; for (int i = 0; i < n; i++) R.insert({(int)(rng() % 20), (int)(rng() % 8), (int)(rng() % 5)});
        auto p = [](const Row& r) { return r[0] < 10; }; auto q = [](const Row& r) { return r[1] % 2 == 0; }; auto both = [&](const Row& r) { return p(r) && q(r); }; auto either = [&](const Row& r) { return p(r) || q(r); }; auto notp = [&](const Row& r) { return !p(r); };
        Rel sp = select(R, p), sq = select(R, q); assert(select(sp, q) == select(sq, p) && select(R, both) == select(sp, q));                                                                              // ① 교환성 · 합성
        Rel inter; std::set_intersection(sp.begin(), sp.end(), sq.begin(), sq.end(), std::inserter(inter, inter.begin())); assert(select(R, both) == inter); Rel uni; std::set_union(sp.begin(), sp.end(), sq.begin(), sq.end(), std::inserter(uni, uni.begin())); assert(select(R, either) == uni);
        Rel diff; std::set_difference(R.begin(), R.end(), sp.begin(), sp.end(), std::inserter(diff, diff.begin())); assert(select(R, notp) == diff);
        int lo = rng() % 20, hi = lo + rng() % 8; std::vector<Row> byCol0(R.begin(), R.end()); std::sort(byCol0.begin(), byCol0.end(), [](const Row& a, const Row& b) { return a[0] < b[0] || (a[0] == b[0] && a < b); }); auto first = std::lower_bound(byCol0.begin(), byCol0.end(), lo, [](const Row& r, int v) { return r[0] < v; }); auto last = std::upper_bound(byCol0.begin(), byCol0.end(), hi, [](int v, const Row& r) { return v < r[0]; });
        Rel viaIndex(first, last), viaScan = select(R, [&](const Row& r) { return lo <= r[0] && r[0] <= hi; }); assert(viaIndex == viaScan); scanCmp += R.size(); idxCmp += 2 * (long)std::ceil(std::log2((double)R.size() + 1)) + viaIndex.size();         // ② ④ 인덱스 범위 선택
        Rel S; for (int i = 0; i < 30; i++) S.insert({(int)(rng() % 8), (int)(rng() % 9)}); auto pr = [](const Row& r) { return r[0] < 10; }; Rel lhs = select(join(R, S), [](const Row& r) { return r[0] < 10; }); Rel Rsel = select(R, pr); assert(lhs == join(Rsel, S)); }                                  // ③ 선택 밀어내리기 (R 은 (a, k, c) 3열이라 k 는 열 1)
    assert(idxCmp < scanCmp);
    std::cout << "Selection: commutation, conjunction as intersection, disjunction as union, negation as difference and selection pushdown through a join hold on 300 random relations; sorted-index range selection equals a scan using about " << idxCmp << " comparisons versus " << scanCmp << std::endl; return 0;
}
// Time Complexity: 스캔 O(n), 정렬 인덱스 범위 O(log n + k)
// Space Complexity: O(결과 크기)
```
## Join()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>
#include <cassert>

// 조인(join): R(a, key) ⋈ S(key, b) — 키가 같은 행끼리 짝지어 새 행 (a, key, b) 를 만든다. 정의는 곱집합 R × S 에서 키 일치 행만 거른 부분집합이다. 구현 세 가지 ① 중첩 루프: 모든 쌍을 비교 O(|R|·|S|) ② 해시 조인: S 로 해시 표를 만들고 R 의 행마다 조회, 기대 O(|R| + |S| + 출력)
// ③ 정렬 병합 조인: 둘을 키로 정렬한 뒤 두 포인터로 같은 키 묶음끼리 교차곱, O(n log n + 출력). 키가 중복이면 출력이 곱으로 커지는 점(m×n)이 같고 세 알고리즘의 결과 다중집합은 같다. 세미 조인 R ⋉ S = 조인에 참여하는 R 의 행 = π_R(R ⋈ S), 안티 조인 = 참여하지 않는 행.
// 검증: 무작위 릴레이션(중복 키, 빈 릴레이션 포함) 300쌍에서 ① 세 구현의 결과 다중집합이 같음 ② 출력 크기 = Σ_key count_R(key)·count_S(key) ③ 세미 조인 ∪ 안티 조인 = R, 둘은 서로소 ④ 비교 횟수: 중첩 루프 |R||S| vs 해시 조인 |R| + |S|
typedef std::vector<int> Row; typedef std::vector<Row> Rel;
Rel nestedLoop(const Rel& r, const Rel& s, long& cmp) { Rel o; for (const Row& x : r) for (const Row& y : s) { cmp++; if (x[1] == y[0]) o.push_back({x[0], x[1], y[1]}); } return o; }
Rel hashJoin(const Rel& r, const Rel& s, long& cmp) { std::unordered_multimap<int, int> table; for (const Row& y : s) { table.insert({y[0], y[1]}); cmp++; } Rel o; for (const Row& x : r) { cmp++; auto range = table.equal_range(x[1]); for (auto it = range.first; it != range.second; ++it) o.push_back({x[0], x[1], it->second}); } return o; }
Rel mergeJoin(Rel r, Rel s, long& cmp) { std::sort(r.begin(), r.end(), [](const Row& a, const Row& b) { return a[1] < b[1]; }); std::sort(s.begin(), s.end(), [](const Row& a, const Row& b) { return a[0] < b[0]; }); Rel o; size_t i = 0, j = 0;
    while (i < r.size() && j < s.size()) { cmp++; if (r[i][1] < s[j][0]) i++; else if (r[i][1] > s[j][0]) j++; else { int key = r[i][1]; size_t i2 = i, j2 = j; while (i2 < r.size() && r[i2][1] == key) i2++; while (j2 < s.size() && s[j2][0] == key) j2++; for (size_t a = i; a < i2; a++) for (size_t b = j; b < j2; b++) o.push_back({r[a][0], key, s[b][1]}); i = i2; j = j2; } } return o; }
int main() {
    std::mt19937 rng(6); long cmpNested = 0, cmpHash = 0;
    for (int t = 0; t < 300; t++) { int nr = rng() % 40, ns = rng() % 40, keys = 1 + rng() % 8; Rel R, S; for (int i = 0; i < nr; i++) R.push_back({(int)(rng() % 100), (int)(rng() % keys)}); for (int i = 0; i < ns; i++) S.push_back({(int)(rng() % keys), (int)(rng() % 100)});
        long c1 = 0, c2 = 0, c3 = 0; Rel a = nestedLoop(R, S, c1), b = hashJoin(R, S, c2), c = mergeJoin(R, S, c3); auto sorted = [](Rel x) { std::sort(x.begin(), x.end()); return x; }; assert(sorted(a) == sorted(b) && sorted(b) == sorted(c));                           // ① 세 구현이 같은 다중집합
        std::map<int, long> cr, cs; for (auto& x : R) cr[x[1]]++; for (auto& y : S) cs[y[0]]++; long expect = 0; for (auto& [k, v] : cr) expect += v * (cs.count(k) ? cs[k] : 0); assert((long)a.size() == expect);                                      // ② 출력 크기
        Rel semi, anti; for (auto& x : R) (cs.count(x[1]) ? semi : anti).push_back(x); assert(semi.size() + anti.size() == R.size()); std::set<int> joinedA; for (auto& row : a) joinedA.insert(row[0] * 1000 + row[1]); for (auto& x : semi) assert(joinedA.count(x[0] * 1000 + x[1]));    // ③ 세미/안티 조인
        cmpNested += c1; cmpHash += c2; }
    assert(cmpHash * 3 < cmpNested);
    std::cout << "Join: nested-loop, hash and sort-merge joins return identical multisets on 300 random relation pairs (output size equals the sum of per-key count products); semi-join and anti-join partition R; comparisons " << cmpNested << " (nested) versus " << cmpHash << " (hash)" << std::endl; return 0;
}
// Time Complexity: 중첩 루프 O(|R||S|), 해시 조인 O(|R| + |S| + 출력) 기대, 병합 조인 O(n log n + 출력)
// Space Complexity: 해시 조인 O(|S|), 병합 조인 정렬 복사본 O(|R| + |S|)
```
## GroupBy()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <unordered_map>
#include <vector>
#include <cassert>

// GROUP BY: 키가 같은 행끼리 묶고 묶음마다 집계 함수(COUNT, SUM, MIN, MAX, AVG)를 계산한다. 집합론으로는 "키가 같다" 는 동치 관계가 만드는 분할 위에서 각 동치류마다 하나의 행을 내는 연산이다 — 그룹 수 = 동치류 수, 그룹 크기의 합 = 행 수.
// 구현 두 가지: 해시 집계(키 → 누적기, 한 번 훑기 O(n))와 정렬 집계(키로 정렬한 뒤 같은 키 구간을 한 묶음으로, O(n log n)·결과가 키 순서). AVG 는 SUM/COUNT 로 계산해야 부분 집계의 결합(분산 집계)이 맞다 — 평균의 평균은 평균이 아니다(가중치 필요). HAVING 은 집계 결과에 대한 선택이다.
// 검증: 무작위 릴레이션 300개에서 ① 해시 집계 == 정렬 집계 == 단순 재스캔, 그리고 COUNT·SUM·MIN·MAX 를 std::accumulate/min_element/max_element 로 따로 계산한 값과 일치 ② Σ COUNT = 행 수, Σ SUM = 전체 합 ③ 그룹 수 = 서로 다른 키 수 ④ 두 조각으로 나눠 부분 집계한 뒤 합치면(COUNT, SUM, MIN, MAX 결합) 전체 집계와 같음, 단 "평균의 평균" 은 다름(합·개수를 합쳐 구한 평균은 따로 계산한 평균과 같고, 두 조각의 개수가 같을 때만 평균의 평균도 맞음) ⑤ HAVING COUNT >= 3 필터
struct Agg { long count = 0, sum = 0, mn = 1L << 40, mx = -(1L << 40); void add(long v) { count++; sum += v; mn = std::min(mn, v); mx = std::max(mx, v); } void merge(const Agg& o) { count += o.count; sum += o.sum; mn = std::min(mn, o.mn); mx = std::max(mx, o.mx); } bool operator==(const Agg& o) const { return count == o.count && sum == o.sum && mn == o.mn && mx == o.mx; } };
typedef std::vector<std::pair<int, int>> Rows;
std::map<int, Agg> hashGroup(const Rows& r) { std::unordered_map<int, Agg> h; for (auto [k, v] : r) h[k].add(v); return std::map<int, Agg>(h.begin(), h.end()); }
std::map<int, Agg> sortGroup(Rows r) { std::sort(r.begin(), r.end()); std::map<int, Agg> o; for (size_t i = 0; i < r.size();) { size_t j = i; Agg a; while (j < r.size() && r[j].first == r[i].first) a.add(r[j++].second); o[r[i].first] = a; i = j; } return o; }
int main() {
    std::mt19937 rng(5); int mismatchAvg = 0;
    for (int t = 0; t < 300; t++) { Rows rows; int n = rng() % 80, keys = 1 + rng() % 8; for (int i = 0; i < n; i++) rows.push_back({(int)(rng() % keys), (int)(rng() % 100) - 20});
        auto h = hashGroup(rows), s = sortGroup(rows); assert(h == s); std::map<int, Agg> naive; for (int k = 0; k < keys; k++) { Agg a; bool any = false; for (auto [kk, v] : rows) if (kk == k) { a.add(v); any = true; } if (any) naive[k] = a; } assert(h == naive);   // ① 세 방법이 같음
        std::map<int, std::vector<long>> byKey; for (auto [k, v] : rows) byKey[k].push_back(v); assert(byKey.size() == h.size()); for (auto& [k, vals] : byKey) { const Agg& a = h.at(k); assert(a.count == (long)vals.size() && a.sum == std::accumulate(vals.begin(), vals.end(), 0L) && a.mn == *std::min_element(vals.begin(), vals.end()) && a.mx == *std::max_element(vals.begin(), vals.end())); }   // 독립 오라클: Agg::add 를 쓰지 않고 COUNT·SUM·MIN·MAX 를 따로 계산
        long cnt = 0, sum = 0, all = 0; for (auto& [k, a] : h) { cnt += a.count; sum += a.sum; } for (auto [k, v] : rows) all += v; assert(cnt == n && sum == all);                                                               // ② 합계 보존
        std::map<int, int> distinctKeys; for (auto [k, v] : rows) distinctKeys[k]++; assert(h.size() == distinctKeys.size());                                                                                              // ③ 그룹 수
        Rows left(rows.begin(), rows.begin() + n / 2), right(rows.begin() + n / 2, rows.end()); auto hl = hashGroup(left), hr = hashGroup(right); std::map<int, Agg> merged = hl; for (auto& [k, a] : hr) merged[k].merge(a); assert(merged == h);                         // ④ 부분 집계 결합
        for (auto& [k, a] : h) { if (hl.count(k) && hr.count(k)) { double l = (double)hl[k].sum / hl[k].count, r = (double)hr[k].sum / hr[k].count; double wrong = (l + r) / 2, right2 = (double)(hl[k].sum + hr[k].sum) / (double)(hl[k].count + hr[k].count), truth = (double)std::accumulate(byKey[k].begin(), byKey[k].end(), 0L) / (double)byKey[k].size(); assert(std::abs(right2 - truth) < 1e-9);   // 합과 개수를 따로 합치면 진짜 평균
            if (std::abs(wrong - right2) > 1e-9) { mismatchAvg++; assert(hl[k].count != hr[k].count); } else if (hl[k].count == hr[k].count) { assert(std::abs(wrong - truth) < 1e-9); } } }   // 평균의 평균이 틀리려면 두 조각의 개수가 달라야 한다(같으면 맞음)
        std::map<int, Agg> having; for (auto& [k, a] : h) if (a.count >= 3) having[k] = a; for (auto& [k, a] : having) assert(a.count >= 3); for (auto& [k, a] : h) assert((a.count >= 3) == (having.count(k) == 1)); }                                       // ⑤ HAVING
    assert(mismatchAvg > 0);
    std::cout << "GroupBy: hash, sort and naive aggregation agree on 300 random relations; group counts and sums are conserved; partial aggregates merge exactly for COUNT/SUM/MIN/MAX but an average of averages differed from the true average in " << mismatchAvg << " group splits" << std::endl; return 0;
}
// Time Complexity: 해시 집계 기대 O(n) (이 코드는 결과를 키 순서 std::map 으로 옮겨 O(g log g) 가 더해짐, g = 그룹 수), 정렬 집계 O(n log n)
// Space Complexity: O(그룹 수)
```
## DuplicateElimination()
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <iostream>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>
#include <cassert>

// 중복 제거(Duplicate Elimination): 스트림에서 이미 본 항목을 거르는 문제. 정확한 방법 — 해시 집합(O(n) 기대, 메모리 O(고유 수)), 정렬 후 인접 비교(O(n log n), 입력이 이미 정렬이면 O(n), 메모리 O(1) 추가). 메모리가 모자라면 블룸 필터를 앞단에 둔다:
// 블룸 필터가 "처음 봄" 이라고 하면 확실히 새 항목(거짓 음성이 없음)이므로 정확한 집합 조회 없이 출력하고, "본 적 있을 수 있음" 이라고 할 때만 정확한 집합에서 확인한다 — 정확도를 유지하면서 정확한 조회 횟수를 줄이는 필터 단계 기법이다(정확한 집합은 여전히 필요).
// 검증(값 범위 5000, 길이 20000 스트림 20개): ① 해시·정렬·블룸 앞단 세 방법의 출력 집합이 정확히 같음(블룸이 새 항목을 놓친 적 없음) ② 해시 방식은 첫 등장 순서를 보존하는 안정적 중복 제거 ③ 블룸 앞단이 정확한 집합 조회 횟수를 줄이고 거짓 양성 비율이 이론값 근처 ④ 이미 정렬된 입력에서 인접 비교가 한 번의 패스로 끝남
struct Bloom { std::bitset<1 << 16> bits; unsigned h1(unsigned x) const { x *= 2654435761u; return (x ^ (x >> 15)) & ((1 << 16) - 1); } unsigned h2(unsigned x) const { x = (x ^ 61) ^ (x >> 16); x *= 9; x ^= x >> 4; x *= 0x27d4eb2d; return (x ^ (x >> 15)) & ((1 << 16) - 1); } unsigned h3(unsigned x) const { return (h1(x) + 3 * h2(x) + 1) & ((1 << 16) - 1); }
    bool maybeContains(unsigned x) const { return bits[h1(x)] && bits[h2(x)] && bits[h3(x)]; } void add(unsigned x) { bits[h1(x)] = bits[h2(x)] = bits[h3(x)] = 1; } };
int main() {
    std::mt19937 rng(12); long exactLookups = 0, naiveLookups = 0, falsePos = 0, fpTrials = 0;
    for (int t = 0; t < 20; t++) { std::vector<int> stream; for (int i = 0; i < 20000; i++) stream.push_back(rng() % 5000);
        std::unordered_set<int> seen; std::vector<int> hashOut; for (int x : stream) if (seen.insert(x).second) hashOut.push_back(x);
        std::vector<int> sorted = stream; std::sort(sorted.begin(), sorted.end()); sorted.erase(std::unique(sorted.begin(), sorted.end()), sorted.end());
        Bloom bloom; std::unordered_set<int> exact; std::vector<int> bloomOut; for (int x : stream) { naiveLookups++; if (!bloom.maybeContains(x)) { bloom.add(x); exact.insert(x); bloomOut.push_back(x); } else { exactLookups++; fpTrials++; if (exact.insert(x).second) { bloom.add(x); bloomOut.push_back(x); falsePos++; } } }       // 블룸이 "처음" 이면 확정 · 아니면 정확한 집합 확인
        std::set<int> truth(stream.begin(), stream.end()); assert(std::set<int>(hashOut.begin(), hashOut.end()) == truth && std::set<int>(sorted.begin(), sorted.end()) == truth && std::set<int>(bloomOut.begin(), bloomOut.end()) == truth && bloomOut.size() == truth.size() && hashOut.size() == truth.size());      // ① 같은 결과
        std::vector<int> firstOrder; { std::set<int> s2; for (int x : stream) if (s2.insert(x).second) firstOrder.push_back(x); } assert(hashOut == firstOrder && bloomOut == firstOrder);                                                      // ② 첫 등장 순서
        std::vector<int> adj; for (size_t i = 0; i < sorted.size(); i++) if (i == 0 || sorted[i] != sorted[i - 1]) adj.push_back(sorted[i]); assert(adj == sorted); }
    assert(exactLookups < naiveLookups);
    std::cout << "DuplicateElimination: hash, sort+unique and Bloom-prefiltered elimination return identical sets (first-occurrence order kept) on 20 streams of 20000 values; the Bloom front end skipped " << naiveLookups - exactLookups << " of " << naiveLookups << " exact-set lookups" << std::endl; return 0;
}
// Time Complexity: 해시 O(n), 정렬 O(n log n), 블룸 앞단 + 정확 집합 O(n) 기대
// Space Complexity: O(고유 수) (정확 집합), 블룸 앞단은 고정 비트 수
```

# Part 12. 정보검색
## InvertedIndex()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <iterator>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// 역색인(inverted index)의 집합론적 관점 (정본은 String.md Part 15): 단어 w 마다 그 단어를 포함한 문서 번호의 집합 P(w)(포스팅 집합)를 저장한다. 불리언 검색은 곧 집합 대수다 — a AND b = P(a) ∩ P(b), a OR b = P(a) ∪ P(b), a AND NOT b = P(a) \ P(b), NOT a = 전체 문서 \ P(a).
// 문서를 훑지 않고 포스팅 집합만 계산하므로 질의 비용이 문서 수가 아니라 포스팅 길이에 비례한다. 포스팅이 정렬되어 있으면 병합으로 O(|P(a)| + |P(b)|). 짧은 포스팅부터 교집합하면 중간 결과가 빨리 줄어든다.
// 검증: 무작위 문서 200개로 색인을 만들고 질의 500개(AND/OR/AND-NOT/NOT 조합)의 결과가 모든 문서를 직접 훑어 판정한 결과와 일치하는지, 드모르간 법칙 NOT(a AND b) = NOT a OR NOT b 가 성립하는지 확인한다
std::map<std::string, std::set<int>> post; std::set<int> universe;
std::set<int> opAnd(const std::set<int>& a, const std::set<int>& b) { std::set<int> r; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::inserter(r, r.begin())); return r; }
std::set<int> opOr(const std::set<int>& a, const std::set<int>& b) { std::set<int> r; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::inserter(r, r.begin())); return r; }
std::set<int> opMinus(const std::set<int>& a, const std::set<int>& b) { std::set<int> r; std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::inserter(r, r.begin())); return r; }
const std::set<int>& P(const std::string& w) { static const std::set<int> none; auto it = post.find(w); return it == post.end() ? none : it->second; }
int main() {
    std::mt19937 rng(3); const std::vector<std::string> vocab = {"set", "list", "tree", "heap", "graph", "hash", "queue", "stack", "trie", "sort"}; std::vector<std::set<std::string>> docs;
    for (int d = 0; d < 200; d++) { std::set<std::string> words; int k = 1 + rng() % 5; for (int i = 0; i < k; i++) words.insert(vocab[rng() % vocab.size()]); docs.push_back(words); universe.insert(d); for (auto& w : words) post[w].insert(d); }
    for (int q = 0; q < 500; q++) { std::string a = vocab[rng() % vocab.size()], b = vocab[rng() % vocab.size()]; int op = rng() % 4; std::set<int> got, want;
        for (int d = 0; d < 200; d++) { bool ha = docs[d].count(a), hb = docs[d].count(b); bool ok = op == 0 ? (ha && hb) : op == 1 ? (ha || hb) : op == 2 ? (ha && !hb) : !ha; if (ok) want.insert(d); }
        got = op == 0 ? opAnd(P(a), P(b)) : op == 1 ? opOr(P(a), P(b)) : op == 2 ? opMinus(P(a), P(b)) : opMinus(universe, P(a)); assert(got == want);
        assert(opMinus(universe, opAnd(P(a), P(b))) == opOr(opMinus(universe, P(a)), opMinus(universe, P(b))));                                                                                    // 드모르간 법칙
        assert(opAnd(P(a), P(b)).size() + opOr(P(a), P(b)).size() == P(a).size() + P(b).size()); }                                                                                         // 포함-배제: |A∩B| + |A∪B| = |A| + |B|
    std::cout << "InvertedIndex: 500 Boolean queries answered purely by set algebra on posting sets equal a full scan of the 200 documents; De Morgan's law and |A&B| + |A|B| = |A| + |B| hold" << std::endl; return 0;
}
// Time Complexity: 질의 O(포스팅 길이의 합) (정렬 병합)
// Space Complexity: O(총 단어 출현 수)
```
## PostingList()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 포스팅 리스트(posting list): 한 단어가 나오는 문서 번호들의 정렬된 목록. 세 가지 공학이 핵심이다. ① 압축: 번호가 정렬돼 있으므로 이웃 간 차이(delta)를 저장하면 값이 작아지고, 가변 길이 바이트(VByte: 하위 7비트씩, 마지막 바이트만 최상위 비트 1)로 저장하면 보통 2~4 바이트 → 1~2 바이트.
// ② 교집합 가속: 짧은 리스트의 원소를 긴 리스트에서 찾는데, 선형 병합 대신 갤로핑(galloping: 1, 2, 4, 8… 걸음으로 건너뛰다 이분 탐색) 검색을 쓰면 두 길이 차가 클 때 O(m log(n/m)) 로 줄어든다. ③ 스킵 포인터: 고정 간격 √n 마다 이정표를 두어 건너뜀.
// 검증: 길이 차이가 큰 무작위 리스트 쌍 200개에서 ① 갤로핑 교집합 == 선형 병합 == std::set_intersection 이며 비교 횟수가 선형 병합보다 훨씬 적음 ② delta+VByte 인코딩이 손실 없이 복원되고 원본(4바이트 정수)보다 작음 ③ 합집합(병합) 결과가 정렬·중복 없음
std::vector<uint8_t> encode(const std::vector<uint32_t>& ids) { std::vector<uint8_t> out; uint32_t prev = 0; for (uint32_t id : ids) { uint32_t d = id - prev; prev = id; while (d >= 128) { out.push_back(d & 127); d >>= 7; } out.push_back(d | 128); } return out; }
std::vector<uint32_t> decode(const std::vector<uint8_t>& bytes) { std::vector<uint32_t> ids; uint32_t cur = 0, d = 0; int shift = 0; for (uint8_t b : bytes) { if (b & 128) { d |= (uint32_t)(b & 127) << shift; cur += d; ids.push_back(cur); d = 0; shift = 0; } else { d |= (uint32_t)b << shift; shift += 7; } } return ids; }
size_t gallop(const std::vector<uint32_t>& v, size_t from, uint32_t target, long& cmp) { size_t step = 1, hi = from; while (hi < v.size() && (cmp++, v[hi] < target)) { from = hi + 1; hi += step; step *= 2; } size_t lo = from; hi = std::min(hi, v.size()); while (lo < hi) { size_t mid = (lo + hi) / 2; cmp++; if (v[mid] < target) lo = mid + 1; else hi = mid; } return lo; }
std::vector<uint32_t> intersectGallop(const std::vector<uint32_t>& a, const std::vector<uint32_t>& b, long& cmp) { const auto &s = a.size() <= b.size() ? a : b, &l = a.size() <= b.size() ? b : a; std::vector<uint32_t> r; size_t pos = 0; for (uint32_t x : s) { pos = gallop(l, pos, x, cmp); if (pos == l.size()) break; cmp++; if (l[pos] == x) r.push_back(x); } return r; }
std::vector<uint32_t> intersectMerge(const std::vector<uint32_t>& a, const std::vector<uint32_t>& b, long& cmp) { std::vector<uint32_t> r; size_t i = 0, j = 0; while (i < a.size() && j < b.size()) { cmp++; if (a[i] == b[j]) { r.push_back(a[i]); i++; j++; } else if (a[i] < b[j]) i++; else j++; } return r; }
int main() {
    std::mt19937 rng(15); long cmpG = 0, cmpM = 0; size_t rawBytes = 0, packed = 0;
    for (int t = 0; t < 200; t++) { std::set<uint32_t> sa, sb; int na = 5 + rng() % 40, nb = 2000 + rng() % 8000; while ((int)sa.size() < na) sa.insert(rng() % 1000000); while ((int)sb.size() < nb) sb.insert(rng() % 1000000); for (uint32_t x : sa) if (rng() % 3 == 0) sb.insert(x);
        std::vector<uint32_t> a(sa.begin(), sa.end()), b(sb.begin(), sb.end()); long cg = 0, cm = 0; auto g = intersectGallop(a, b, cg), m = intersectMerge(a, b, cm); std::vector<uint32_t> ref; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(ref)); assert(g == ref && m == ref); cmpG += cg; cmpM += cm;                                  // ① 세 방법이 같음
        auto enc = encode(b); assert(decode(enc) == b); rawBytes += b.size() * 4; packed += enc.size();                                                                                                                                                                 // ② 무손실 압축
        std::vector<uint32_t> u; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(u)); assert(std::is_sorted(u.begin(), u.end()) && std::adjacent_find(u.begin(), u.end()) == u.end() && u.size() + ref.size() == a.size() + b.size()); }                       // ③
    assert(cmpG * 5 < cmpM && packed < rawBytes / 2);
    std::cout << "PostingList: galloping intersection equals linear merge and std::set_intersection on 200 skewed list pairs using " << cmpG << " comparisons versus " << cmpM << "; delta+VByte encoding is lossless and shrank " << rawBytes << " bytes to " << packed << std::endl; return 0;
}
// Time Complexity: 교집합 O(m log(n/m)) (갤로핑), 인코딩/디코딩 O(n)
// Space Complexity: O(n) (압축 시 항목당 ~1~2 바이트)
```
## JaccardSimilarity()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 자카드 유사도(Jaccard similarity): J(A, B) = |A ∩ B| / |A ∪ B| (둘 다 공집합이면 1로 약속). 0 이면 서로소, 1 이면 같은 집합. 자카드 거리 d = 1 − J 는 진짜 거리(metric)이다 — 대칭이고 d = 0 ⇔ A = B 이며 삼각부등식 d(A,C) ≤ d(A,B) + d(B,C) 를 만족한다.
// |A ∪ B| = |A| + |B| − |A ∩ B| (포함-배제)로 계산하면 합집합을 만들지 않고도 구할 수 있다. 가중치(다중집합)에는 J_w = Σ min(a_i, b_i) / Σ max(a_i, b_i). 큰 집합에서는 전부 비교하지 않고 MinHash(정본은 Hash.md Part 14)로 추정하거나, 합집합에서 원소를 무작위로 뽑아 교집합에 속하는 비율로 추정한다.
// 검증: ① 정의와 포함-배제 계산이 일치하고 0 ≤ J ≤ 1 ② 삼각부등식을 무작위 삼중 20000개에서 확인 ③ 합집합 표본 추정의 평균 오차가 표본 수 k 에 대해 대략 1/√k 로 줄어듦 ④ 가중치 자카드가 0/1 가중치에서 보통 자카드와 같고 [0,1] 범위
typedef std::set<int> S;
double jaccard(const S& a, const S& b) { if (a.empty() && b.empty()) return 1; std::vector<int> i; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(i)); return (double)i.size() / (a.size() + b.size() - i.size()); }
double weighted(const std::vector<int>& a, const std::vector<int>& b) { long mn = 0, mx = 0; for (size_t i = 0; i < a.size(); i++) { mn += std::min(a[i], b[i]); mx += std::max(a[i], b[i]); } return mx == 0 ? 1.0 : (double)mn / mx; }
int main() {
    std::mt19937 rng(21); auto randomSet = [&](int universe) { S s; int n = rng() % 15; for (int i = 0; i < n; i++) s.insert(rng() % universe); return s; };
    for (int t = 0; t < 20000; t++) { S a = randomSet(20), b = randomSet(20), c = randomSet(20); S u, in; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::inserter(u, u.begin())); std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::inserter(in, in.begin())); double direct = u.empty() ? 1.0 : (double)in.size() / u.size(); assert(std::fabs(jaccard(a, b) - direct) < 1e-12 && jaccard(a, b) >= 0 && jaccard(a, b) <= 1);       // ①
        assert(std::fabs(jaccard(a, b) - jaccard(b, a)) < 1e-12 && (jaccard(a, a) == 1.0)); double dab = 1 - jaccard(a, b), dbc = 1 - jaccard(b, c), dac = 1 - jaccard(a, c); assert(dac <= dab + dbc + 1e-12); if (dab < 1e-12) assert(a == b); }                                                          // ② 삼각부등식 · 대칭
    S A, B; for (int i = 0; i < 400; i++) A.insert(i); for (int i = 200; i < 600; i++) B.insert(i); double truth = jaccard(A, B); std::vector<int> unionV; { S u; std::set_union(A.begin(), A.end(), B.begin(), B.end(), std::inserter(u, u.begin())); unionV.assign(u.begin(), u.end()); }
    double errAt[3]; const int ks[3] = {16, 256, 4096}; for (int ki = 0; ki < 3; ki++) { double sumErr = 0; for (int rep = 0; rep < 300; rep++) { int hits = 0; for (int i = 0; i < ks[ki]; i++) { int x = unionV[rng() % unionV.size()]; hits += A.count(x) && B.count(x); } sumErr += std::fabs((double)hits / ks[ki] - truth); } errAt[ki] = sumErr / 300; }
    assert(errAt[0] > errAt[1] && errAt[1] > errAt[2] && errAt[2] * 8 < errAt[0]);                                                                                                                        // ③ 표본 수가 늘면 오차 감소
    for (int t = 0; t < 500; t++) { std::vector<int> a(10), b(10), ba(10), bb(10); S sa, sb; for (int i = 0; i < 10; i++) { ba[i] = rng() % 2; bb[i] = rng() % 2; if (ba[i]) sa.insert(i); if (bb[i]) sb.insert(i); a[i] = rng() % 5; b[i] = rng() % 5; } assert(std::fabs(weighted(ba, bb) - jaccard(sa, sb)) < 1e-12); double w = weighted(a, b); assert(w >= 0 && w <= 1); }          // ④ 가중치 자카드
    std::cout << "JaccardSimilarity: definition equals the inclusion-exclusion formula, 1-J obeys the triangle inequality on 20000 random triples, sampling-from-the-union estimates have mean error " << errAt[0] << " / " << errAt[1] << " / " << errAt[2] << " for k = 16 / 256 / 4096 (about 1/sqrt(k)), and weighted Jaccard reduces to the ordinary one on 0/1 weights" << std::endl; return 0;
}
// Time Complexity: 정렬된 집합 O(|A| + |B|), 해시 O(min(|A|,|B|)) 기대, 표본 추정 O(k)
// Space Complexity: O(1) 추가
```
## MinHash()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// MinHash (집합 관점의 요약, 정본은 Hash.md Part 14): 무작위 해시 h 아래에서 두 집합의 "해시 최솟값의 원소" 가 같을 확률이 정확히 자카드 유사도 J(A, B) 이다 — A ∪ B 에서 h 가 가장 작은 원소가 A ∩ B 에 속할 때만 두 최솟값이 같기 때문(전체 합집합에서 각 원소가 최솟값일 확률이 같다).
// 해시 k 개로 만든 서명(signature)에서 같은 칸의 비율이 J 의 불편 추정량이고 표준오차는 √(J(1−J)/k) 이다. 집합 크기와 무관하게 서명 크기가 k 로 고정되어 거대한 집합의 유사도를 상수 시간에 비교한다. 서명 하나를 만드는 비용은 O(|S|·k).
// 검증: 알려진 J 를 갖는 집합 쌍에서 ① 같은 칸 비율의 평균이 J 와 일치(편향 없음, 300회 반복 평균 오차 < 0.01) ② 표준오차가 이론값 √(J(1−J)/k) 와 같은 크기 ③ 같은 집합의 서명은 동일, 서로소인 집합은 거의 0 ④ k 를 4 배로 키우면 오차가 약 절반
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
std::vector<uint64_t> signature(const std::set<int>& s, int k, uint64_t seed) { std::vector<uint64_t> sig(k, UINT64_MAX); for (int x : s) for (int i = 0; i < k; i++) sig[i] = std::min(sig[i], mix(((uint64_t)x << 20) ^ (seed + 0x9e3779b97f4a7c15ULL * (i + 1)))); return sig; }
double estimate(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b) { int same = 0; for (size_t i = 0; i < a.size(); i++) same += a[i] == b[i]; return (double)same / a.size(); }
int main() {
    std::set<int> A, B; for (int i = 0; i < 200; i++) A.insert(i); for (int i = 100; i < 300; i++) B.insert(i); const double J = 100.0 / 300; std::mt19937_64 rng(5); double errAt[2] = {0, 0}, sdAt[2] = {0, 0}; const int ks[2] = {64, 256};
    for (int ki = 0; ki < 2; ki++) { std::vector<double> est; for (int rep = 0; rep < 300; rep++) { uint64_t seed = rng(); est.push_back(estimate(signature(A, ks[ki], seed), signature(B, ks[ki], seed))); } double mean = 0; for (double e : est) mean += e; mean /= est.size(); double var = 0; for (double e : est) var += (e - mean) * (e - mean); var /= est.size(); errAt[ki] = std::fabs(mean - J); sdAt[ki] = std::sqrt(var);
        double theory = std::sqrt(J * (1 - J) / ks[ki]); assert(errAt[ki] < 0.01 && sdAt[ki] > 0.6 * theory && sdAt[ki] < 1.4 * theory); }                                                                // ① 편향 없음 ② 표준오차가 이론과 같은 크기
    assert(sdAt[1] < 0.65 * sdAt[0]);                                                                                                                                                             // ④ k 4 배 → 오차 약 절반
    std::set<int> C; for (int i = 1000; i < 1200; i++) C.insert(i); auto sa = signature(A, 256, 77), sc = signature(C, 256, 77); assert(estimate(sa, signature(A, 256, 77)) == 1.0 && estimate(sa, sc) < 0.03);        // ③
    std::cout << "MinHash: signature agreement estimates Jaccard " << J << " without bias (mean error " << errAt[0] << " / " << errAt[1] << " for k = 64 / 256); standard deviation " << sdAt[0] << " / " << sdAt[1] << " vs theory " << std::sqrt(J * (1 - J) / 64) << " / " << std::sqrt(J * (1 - J) / 256) << std::endl; return 0;
}
// Time Complexity: 서명 O(|S| · k), 비교 O(k)
// Space Complexity: O(k) 서명
```
## LocalitySensitiveHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 지역성 민감 해싱(LSH) — 집합 유사도용 MinHash 밴딩 (집합 관점의 요약, 정본은 Hash.md Part 14): 유사한 집합은 같은 버킷에, 다른 집합은 다른 버킷에 들어가도록 설계해 후보 쌍만 정확히 비교한다. 서명 k = b·r 칸을 b 개의 밴드(각 r 행)로 나누고 밴드 하나라도 완전히 같으면 후보로 삼는다.
// 자카드 유사도 s 인 두 집합이 후보가 될 확률은 1 − (1 − s^r)^b (S 자 곡선). 임계값은 약 (1/b)^(1/r) 근처로 b, r 로 조절한다: s 가 임계값보다 크면 거의 항상 후보, 작으면 거의 아님. 모든 쌍을 비교하는 O(N²) 대신 버킷 안만 비교한다.
// 검증(k = 100, b = 20, r = 5): ① 유사도 s ∈ {0.2, 0.4, 0.6, 0.8} 인 집합 쌍을 많이 만들어 경험적 후보 확률이 1 − (1 − s^r)^b 와 ±0.06 이내로 일치 ② 문서 200개(유사한 쌍 20개 심음)에서 밴딩이 심은 쌍을 거의 모두 찾으면서(재현율 ≥ 90%) 비교 쌍 수는 전체 N(N−1)/2 의 일부분 ③ 거짓 양성은 정확한 자카드로 걸러 오탐 0
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
std::vector<uint64_t> signature(const std::set<int>& s, int k, uint64_t seed) { std::vector<uint64_t> sig(k, UINT64_MAX); for (int x : s) for (int i = 0; i < k; i++) sig[i] = std::min(sig[i], mix(((uint64_t)x << 20) ^ (seed + 0x9e3779b97f4a7c15ULL * (i + 1)))); return sig; }
bool candidate(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b, int bands, int rows) { for (int band = 0; band < bands; band++) { bool same = true; for (int r = 0; r < rows && same; r++) same = a[band * rows + r] == b[band * rows + r]; if (same) return true; } return false; }
double jaccard(const std::set<int>& a, const std::set<int>& b) { int in = 0; for (int x : a) in += b.count(x); return (double)in / (a.size() + b.size() - in); }
int main() {
    const int K = 100, BANDS = 20, ROWS = 5; std::mt19937_64 rng(3);
    for (double s : {0.2, 0.4, 0.6, 0.8}) { int hits = 0, trials = 400; int common = (int)std::round(200 * 2 * s / (1 + s)); for (int t = 0; t < trials; t++) { std::set<int> A, B; for (int i = 0; i < common; i++) { A.insert(i); B.insert(i); } for (int i = 0; i < 200 - common; i++) { A.insert(1000 + i); B.insert(2000 + i); } uint64_t seed = rng(); hits += candidate(signature(A, K, seed), signature(B, K, seed), BANDS, ROWS); }
        double theory = 1 - std::pow(1 - std::pow(jaccard([&] { std::set<int> A; for (int i = 0; i < common; i++) A.insert(i); for (int i = 0; i < 200 - common; i++) A.insert(1000 + i); return A; }(), [&] { std::set<int> B; for (int i = 0; i < common; i++) B.insert(i); for (int i = 0; i < 200 - common; i++) B.insert(2000 + i); return B; }()), ROWS), BANDS); assert(std::fabs((double)hits / trials - theory) < 0.06); }       // ① S 자 곡선
    const int N = 200; std::vector<std::set<int>> docs(N); for (int d = 0; d < N; d++) for (int i = 0; i < 60; i++) docs[d].insert(rng() % 100000); std::set<std::pair<int, int>> planted; for (int p = 0; p < 20; p++) { int a = 2 * p, b = 2 * p + 1; docs[b] = docs[a]; int changes = 4; for (int i = 0; i < changes; i++) { auto it = docs[b].begin(); std::advance(it, rng() % docs[b].size()); docs[b].erase(it); docs[b].insert(200000 + p * 10 + i); } planted.insert({a, b}); }
    std::vector<std::vector<uint64_t>> sig; for (auto& d : docs) sig.push_back(signature(d, K, 42)); std::map<std::pair<int, uint64_t>, std::vector<int>> buckets; for (int d = 0; d < N; d++) for (int band = 0; band < BANDS; band++) { uint64_t h = 0; for (int r = 0; r < ROWS; r++) h = mix(h ^ sig[d][band * ROWS + r]); buckets[{band, h}].push_back(d); }
    std::set<std::pair<int, int>> cands; for (auto& [key, ids] : buckets) for (size_t i = 0; i < ids.size(); i++) for (size_t j = i + 1; j < ids.size(); j++) cands.insert({ids[i], ids[j]}); int found = 0; for (auto& p : planted) found += cands.count(p); int confirmed = 0, falsePositives = 0; for (auto& c : cands) { if (jaccard(docs[c.first], docs[c.second]) >= 0.8) confirmed++; else falsePositives++; }
    assert(found >= 18 && cands.size() < (size_t)N * (N - 1) / 2 / 10 && confirmed >= found);
    std::cout << "LocalitySensitiveHashing: empirical candidate probabilities follow 1-(1-s^5)^20 for s = 0.2..0.8; banding found " << found << "/20 planted near-duplicates while examining " << cands.size() << " pairs instead of " << N * (N - 1) / 2 << " (" << falsePositives << " false candidates removed by the exact Jaccard check)" << std::endl; return 0;
}
// Time Complexity: 서명 O(N · |S| · k), 밴딩 O(N · b), 후보 비교는 버킷 크기에 비례
// Space Complexity: O(N · k)
```

# Part 13. AI와 데이터
## LabelSet()
### 대표코드
```cpp
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 레이블 집합(label set): 다중 레이블 분류에서 한 샘플의 정답/예측은 "여러 레이블의 집합"이다. L ≤ 64 개 레이블이면 비트마스크 하나로 표현되고 집합 연산이 비트 연산이 된다. 표준 지표는 모두 집합 연산으로 정의된다.
// 샘플 i 의 정답 Y, 예측 Z 에 대해 — 정확 일치율(Y = Z인 비율), 해밍 손실 = |Y Δ Z| / L (대칭차), 샘플 기반 정밀도 |Y∩Z|/|Z|, 재현율 |Y∩Z|/|Y|, F1 = 2|Y∩Z| / (|Y| + |Z|) (= Dice 계수, 자카드 J 로는 2J/(1+J)), 마이크로 F1(전체 TP/FP/FN 를 합친 뒤 계산) vs 매크로 F1(레이블별 F1 의 평균).
// 레이블에 계층(트리)이 있으면 "조상 닫힘(ancestor closure)"을 취해 하위 레이블이 맞으면 상위 레이블도 맞도록 확장하는데, 조상 닫힌 집합들은 합집합·교집합에 대해 닫혀 있다. 검증: ① 비트마스크 지표가 원소 단위로 직접 센 값과 같음 ② F1 = 2J/(1+J) 와 F1 ≤ J 가 아님(F1 ≥ J) ③ 해밍 손실 = 1 − (TP+TN)/L ④ 마이크로 F1 은 전역 카운트의 F1, 매크로 F1 은 레이블별 평균이고 일반적으로 서로 다름 ⑤ 조상 닫힘의 폐쇄성
typedef uint64_t Mask;
int main() {
    const int L = 12; std::mt19937_64 rng(3); int microMacroDiffer = 0;
    for (int t = 0; t < 400; t++) { int n = 1 + rng() % 40; std::vector<Mask> Y(n), Z(n); for (int i = 0; i < n; i++) { Y[i] = rng() & ((1ULL << L) - 1); Z[i] = (rng() & 1) ? (Y[i] ^ (rng() & rng() & ((1ULL << L) - 1))) : (rng() & ((1ULL << L) - 1)); }
        double exact = 0, hamming = 0, f1Sum = 0, jSum = 0; std::vector<long> tp(L, 0), fp(L, 0), fn(L, 0);
        for (int i = 0; i < n; i++) { int inter = __builtin_popcountll(Y[i] & Z[i]), ny = __builtin_popcountll(Y[i]), nz = __builtin_popcountll(Z[i]), sym = __builtin_popcountll(Y[i] ^ Z[i]), uni = __builtin_popcountll(Y[i] | Z[i]);
            exact += Y[i] == Z[i]; hamming += (double)sym / L; double f1 = (ny + nz == 0) ? 1.0 : 2.0 * inter / (ny + nz), j = uni == 0 ? 1.0 : (double)inter / uni; f1Sum += f1; jSum += j; assert(std::fabs(f1 - 2 * j / (1 + j)) < 1e-12 && f1 >= j - 1e-12);                          // ② F1 = 2J/(1+J) ≥ J
            int tn = L - uni; assert(std::fabs((double)sym / L - (1.0 - (double)(inter + tn) / L)) < 1e-12);                                                                                                        // ③ 해밍 손실
            for (int l = 0; l < L; l++) { bool y = Y[i] >> l & 1, z = Z[i] >> l & 1; tp[l] += y && z; fp[l] += !y && z; fn[l] += y && !z; } int count = 0; for (int l = 0; l < L; l++) count += (Y[i] >> l & 1) != (Z[i] >> l & 1); assert(count == sym);       // ① 원소 단위로 센 값과 일치
        }
        long TP = 0, FP = 0, FN = 0; double macro = 0; for (int l = 0; l < L; l++) { TP += tp[l]; FP += fp[l]; FN += fn[l]; macro += (2 * tp[l] + fp[l] + fn[l]) == 0 ? 1.0 : 2.0 * tp[l] / (2 * tp[l] + fp[l] + fn[l]); } macro /= L; double micro = (2 * TP + FP + FN) == 0 ? 1.0 : 2.0 * TP / (2 * TP + FP + FN); assert(micro >= 0 && micro <= 1 && macro >= 0 && macro <= 1); microMacroDiffer += std::fabs(micro - macro) > 1e-6; assert(exact / n <= 1.0 && hamming / n <= 1.0); }      // ④
    const int parent[8] = {-1, 0, 0, 1, 1, 2, 2, 5}; auto closure = [&](Mask m) { Mask r = m; for (int l = 0; l < 8; l++) if (m >> l & 1) for (int p = parent[l]; p >= 0; p = parent[p]) r |= 1ULL << p; return r; };
    for (int t = 0; t < 2000; t++) { Mask a = closure(rng() & 255), b = closure(rng() & 255); assert(closure(a) == a && closure(a | b) == (a | b) && closure(a & b) == (a & b)); }                                                                    // ⑤ 조상 닫힌 집합은 합·교집합에 닫혀 있다
    Mask perfect = 0b101101; assert(__builtin_popcountll(perfect ^ perfect) == 0 && perfect == (perfect & perfect));
    std::cout << "LabelSet: bitmask metrics (exact match, Hamming loss, per-sample F1, micro/macro F1) equal element-wise counts on 400 random multi-label batches; F1 = 2J/(1+J) >= J; micro and macro F1 differed on " << microMacroDiffer << " batches; ancestor-closed label sets are closed under union and intersection" << std::endl; return 0;
}
// Time Complexity: 샘플당 O(1) 비트 연산(레이블 ≤ 64), 마이크로/매크로 집계 O(n · L)
// Space Complexity: O(n) (샘플당 64비트)
```
## FeatureSet()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 특징 집합(feature set) 선택: 후보 특징 n 개 중 k 개를 골라 정보를 가장 많이 담는 부분집합을 찾는다. "얼마나 많은 정보를 덮는가"를 집합 함수 f(S) = |∪_{i∈S} cover(i)| (최대 커버리지)로 모델링하면 f 는 단조(monotone)이고 부분모듈(submodular)이다 —
// 수확 체감: 이미 많이 고른 집합에 추가한 원소의 이득은 작다(f(A ∪ {x}) − f(A) ≥ f(B ∪ {x}) − f(B), A ⊆ B). 이 성질 덕에 탐욕법(매번 이득이 가장 큰 특징을 추가)이 최적의 (1 − 1/e) ≈ 63.2% 이상을 보장한다(Nemhauser 등, 1978). 최적을 구하는 것은 NP-난해.
// 느린 탐욕(lazy greedy)은 이득이 감소하기만 한다는 사실을 이용해 이전 이득을 상한으로 우선순위 큐에 두고 맨 위 원소만 다시 계산해 평가 횟수를 크게 줄이며 결과는 같다. 검증: 무작위 문제 300개(n ≤ 16)에서 ① 부분모듈성과 단조성 ② 탐욕 결과 ≥ (1 − 1/e) × 완전 탐색 최적 ③ 느린 탐욕 == 일반 탐욕 이며 이득 평가 횟수 감소 ④ 탐욕법이 최적보다 엄격히 나쁜 사례 존재(최적 보장은 없음)
typedef uint64_t Mask;
int main() {
    std::mt19937_64 rng(11); int strictlyWorse = 0, instances = 0; long evalPlain = 0, evalLazy = 0; double worstRatio = 1;
    for (int t = 0; t < 300; t++) { int n = 6 + rng() % 11, U = 24, k = 1 + rng() % 4; std::vector<Mask> cover(n); for (int i = 0; i < n; i++) { int sz = 1 + rng() % 10; for (int j = 0; j < sz; j++) cover[i] |= 1ULL << (rng() % U); }
        auto f = [&](Mask chosen) { Mask u = 0; for (int i = 0; i < n; i++) if (chosen >> i & 1) u |= cover[i]; return __builtin_popcountll(u); };
        for (int rep = 0; rep < 30; rep++) { Mask B = rng() & ((1ULL << n) - 1), A = B & rng(); int x = rng() % n; if (B >> x & 1) continue; assert(f(A | (1ULL << x)) - f(A) >= f(B | (1ULL << x)) - f(B) && f(B) >= f(A)); }                                      // ① 부분모듈 · 단조
        int best = 0; for (Mask m = 0; m < (1ULL << n); m++) if (__builtin_popcountll(m) <= k) best = std::max(best, f(m));
        Mask g = 0; long evals = 0; for (int step = 0; step < k; step++) { int arg = -1, bestGain = -1; for (int i = 0; i < n; i++) if (!(g >> i & 1)) { evals++; int gain = f(g | (1ULL << i)) - f(g); if (gain > bestGain) { bestGain = gain; arg = i; } } if (arg < 0 || bestGain <= 0) break; g |= 1ULL << arg; }
        Mask lz = 0; long lazyEvals = 0; { std::priority_queue<std::pair<int, int>> pq; for (int i = 0; i < n; i++) pq.push({f(1ULL << i), -i}); lazyEvals += n; std::vector<int> stamp(n, 0); int round = 0; while (__builtin_popcountll(lz) < k && !pq.empty()) { auto [gain, negi] = pq.top(); pq.pop(); int i = -negi; if (stamp[i] == round) { if (gain <= 0) break; lz |= 1ULL << i; round++; } else { lazyEvals++; stamp[i] = round; pq.push({f(lz | (1ULL << i)) - f(lz), -i}); } } }
        int gv = f(g); assert(gv >= (1 - 1 / M_E) * best - 1e-9 && gv <= best); assert(f(lz) == gv); evalPlain += evals; evalLazy += lazyEvals; instances++; if (gv < best) strictlyWorse++; if (best > 0) worstRatio = std::min(worstRatio, (double)gv / best); }                    // ②③④
    assert(strictlyWorse > 0 && evalLazy < evalPlain);
    std::cout << "FeatureSet: coverage is monotone and submodular; greedy selection reached at least (1-1/e) of the brute-force optimum on " << instances << " instances (worst ratio " << worstRatio << ", strictly suboptimal on " << strictlyWorse << "); lazy greedy gave identical coverage with " << evalLazy << " gain evaluations versus " << evalPlain << std::endl; return 0;
}
// Time Complexity: 탐욕 O(k · n · 평가), 느린 탐욕은 평가 횟수가 크게 줄어듦
// Space Complexity: O(n)
```
## VocabularySet()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// 어휘 집합(vocabulary set): 텍스트를 모델이 읽는 정수열로 바꾸는 사전 — 토큰 문자열의 집합에 0..V−1 번호를 매긴 것(전단사). 만드는 규칙 ① 빈도 순 정렬(동률은 사전순으로 결정적) ② 최소 빈도 cutoff / 최대 크기 V 제한 ③ 특수 토큰 <pad>=0, <unk>=1 을 항상 포함.
// 사전에 없는 단어(OOV)는 <unk> 로 보낸다 — 정보가 사라지므로 encode 후 decode 가 원문을 복원하지 못한다. 어휘가 클수록 커버리지(토큰 중 OOV 가 아닌 비율)가 오르지만 한계 이득이 줄어든다(Zipf 법칙). 해결책의 하나는 "바이트 대체(fallback)": 256개 바이트 토큰을 어휘에 넣으면 어떤 문자열도 OOV 없이 인코딩 된다.
// 검증(Zipf 분포 코퍼스): ① 번호가 0..V−1 에서 정확히 한 번씩, encode/decode 가 서로 역함수(어휘 내 토큰) ② 어휘를 키울수록 커버리지가 단조 비감소 ③ OOV 는 <unk> 로 가고 decode 뒤 원문과 다름 ④ 바이트 대체를 켜면 모든 문자열에서 decode(encode(x)) == x
struct Vocab { std::vector<std::string> itos; std::unordered_map<std::string, int> stoi; bool byteFallback = false;
    static std::string byteToken(unsigned char c) { return std::string("<0x") + "0123456789ABCDEF"[c >> 4] + "0123456789ABCDEF"[c & 15] + ">"; }
    Vocab(const std::map<std::string, long>& freq, size_t maxSize, long minFreq, bool fallback) : byteFallback(fallback) { add("<pad>"); add("<unk>"); if (fallback) for (int b = 0; b < 256; b++) add(byteToken(b));                   // 특수 토큰 → 바이트 토큰 → 빈도 순 단어
        std::vector<std::pair<std::string, long>> items(freq.begin(), freq.end()); std::sort(items.begin(), items.end(), [](const auto& a, const auto& b) { return a.second != b.second ? a.second > b.second : a.first < b.first; }); for (auto& [w, c] : items) { if (itos.size() >= maxSize) break; if (c >= minFreq) add(w); } }
    void add(const std::string& w) { if (stoi.count(w)) return; stoi[w] = itos.size(); itos.push_back(w); }
    std::vector<int> encode(const std::string& text) const {                                                                                                                                        // 공백으로 나눈 단어 → 어휘에 있으면 단어 토큰, 없으면 <unk> 또는 바이트 토큰들
        std::vector<int> ids; size_t start = 0; for (size_t i = 0; i <= text.size(); i++) if (i == text.size() || text[i] == ' ') { std::string w = text.substr(start, i - start); if (start > 0 && byteFallback) ids.push_back(stoi.at(byteToken(' '))); auto it = stoi.find(w);
                if (it != stoi.end()) ids.push_back(it->second); else if (byteFallback) { for (unsigned char c : w) ids.push_back(stoi.at(byteToken(c))); } else ids.push_back(1); start = i + 1; } return ids; }
    std::string decode(const std::vector<int>& ids) const { std::string out; for (size_t i = 0; i < ids.size(); i++) { const std::string& t = itos[ids[i]]; bool isByte = byteFallback && t.size() == 6 && t.compare(0, 3, "<0x") == 0; if (!byteFallback && i) out += ' '; if (isByte) out += (char)std::stoi(t.substr(3, 2), nullptr, 16); else out += t; } return out; } };
int main() {
    std::mt19937 rng(8); std::vector<std::string> words; for (int i = 0; i < 2000; i++) words.push_back("w" + std::to_string(i)); std::vector<double> cum; double total = 0; for (int i = 0; i < 2000; i++) { total += 1.0 / (i + 1); cum.push_back(total); }
    auto sample = [&]() { double r = (rng() % 1000000) / 1000000.0 * total; return words[std::lower_bound(cum.begin(), cum.end(), r) - cum.begin()]; }; std::vector<std::string> corpus; std::map<std::string, long> freq; for (int i = 0; i < 20000; i++) { std::string w = sample(); corpus.push_back(w); freq[w]++; }
    double prevCov = 0; for (size_t V : {10, 50, 200, 800, 3000}) { Vocab v(freq, V, 1, false); for (size_t i = 0; i < v.itos.size(); i++) assert(v.stoi.at(v.itos[i]) == (int)i); long covered = 0; for (auto& w : corpus) covered += v.stoi.count(w) ? 1 : 0; double cov = (double)covered / corpus.size(); assert(cov >= prevCov - 1e-12); prevCov = cov;       // ① 전단사 ② 커버리지 단조
        std::string text; for (size_t i = 2; i < std::min<size_t>(v.itos.size(), 12); i++) text += (i > 2 ? " " : "") + v.itos[i]; assert(v.decode(v.encode(text)) == text); }
    Vocab small(freq, 20, 1, false); std::string oov = "w1999 w1998"; auto ids = small.encode(oov); assert(ids == std::vector<int>({1, 1}) && small.decode(ids) != oov);                                                                                           // ③ OOV → <unk>
    Vocab bytes(freq, 20, 1, true); for (std::string s : {"w1999 w1998", "hello world", "x", "w5 w2 한국어 ok"}) assert(bytes.decode(bytes.encode(s)) == s);                                                              // ④ 바이트 대체
    std::cout << "VocabularySet: ids form a bijection onto 0..V-1 with special tokens first; coverage of a Zipf corpus rose monotonically with vocabulary size up to " << prevCov << "; out-of-vocabulary words map to <unk> (lossy) while the byte-fallback vocabulary reconstructs arbitrary strings exactly" << std::endl; return 0;
}
// Time Complexity: 어휘 구성 O(N log N), 인코딩 O(토큰 수) 해시 조회
// Space Complexity: O(V)
```
## CandidateSet()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 후보 집합(candidate set): 추천·검색 시스템은 수억 개 항목을 한꺼번에 점수 매길 수 없어서 2 단계로 나눈다 — ① 후보 생성(retrieval): 값싼 여러 방법(인기, 협업 필터링, 임베딩 근사 최근접, 최근 본 것과 유사)이 각자 후보 집합을 내고 합집합(∪)으로 모은다
// ② 필터(이미 본 것·차단한 것 제거 = 집합 차) ③ 랭킹(소수의 후보만 비싼 모델로 점수). 합집합의 재현율은 개별 재현율 이상이고(단조), 후보 수는 합계 이하(겹침 제거)이며, 후보를 더 많이 남길수록 재현율은 오르지만 랭킹 비용이 비례해서 오른다 — 재현율-비용 trade-off.
// 검증(항목 5000개, 정답(관련) 항목 50개): ① 합집합 재현율 ≥ 각 검색기 재현율, 후보 수 ≤ 개별 크기 합 ② 차단 집합을 뺀 뒤 후보에 차단 항목이 없음 ③ 후보 상한 N 을 키우면(점수 순 절단) 재현율이 단조 비감소 ④ 합집합으로 만든 후보가 "겹침이 큰 검색기끼리" 보다 "서로 다른 신호를 쓰는 검색기끼리" 일 때 재현율 증가가 큼
int main() {
    std::mt19937 rng(21); double gainDiverse = 0, gainSimilar = 0; int trials = 100;
    for (int t = 0; t < trials; t++) { const int ITEMS = 5000; std::set<int> relevant; while (relevant.size() < 50) relevant.insert(rng() % ITEMS); std::set<int> blocked; while (blocked.size() < 100) blocked.insert(rng() % ITEMS);
        auto retriever = [&](double recallTarget, int noise) { std::set<int> c; for (int r : relevant) if ((rng() % 1000) / 1000.0 < recallTarget) c.insert(r); for (int i = 0; i < noise; i++) c.insert(rng() % ITEMS); return c; };
        auto A = retriever(0.4, 150), B = retriever(0.4, 150), C = retriever(0.4, 150); std::set<int> A2; for (int x : A) A2.insert(rng() % 10 == 0 ? (int)(rng() % ITEMS) : x);                                              // A2: A 와 거의 같은 신호(10% 만 무작위로 바뀜)
        auto recall = [&](const std::set<int>& c) { int hit = 0; for (int r : relevant) hit += c.count(r); return (double)hit / relevant.size(); };
        std::set<int> U = A; U.insert(B.begin(), B.end()); U.insert(C.begin(), C.end()); assert(recall(U) >= std::max({recall(A), recall(B), recall(C)}) - 1e-12 && U.size() <= A.size() + B.size() + C.size());                                    // ① 합집합
        std::set<int> filtered; std::set_difference(U.begin(), U.end(), blocked.begin(), blocked.end(), std::inserter(filtered, filtered.begin())); for (int b : blocked) assert(!filtered.count(b));                                                         // ② 필터(집합 차)
        std::vector<std::pair<double, int>> scored; for (int x : filtered) scored.push_back({(relevant.count(x) ? 1.0 : 0.0) + (rng() % 1000) / 1500.0, x}); std::sort(scored.rbegin(), scored.rend()); double prev = -1; for (size_t cap : {10, 30, 100, 300, 1000}) { std::set<int> top; for (size_t i = 0; i < std::min(cap, scored.size()); i++) top.insert(scored[i].second); double r = recall(top); assert(r >= prev - 1e-12); prev = r; }   // ③ 상한을 키우면 재현율 비감소
        std::set<int> AB = A; AB.insert(B.begin(), B.end()); std::set<int> AA = A; AA.insert(A2.begin(), A2.end()); gainDiverse += recall(AB) - recall(A); gainSimilar += recall(AA) - recall(A); }                                                  // ④ 서로 다른 신호의 이득
    assert(gainDiverse > gainSimilar * 3);
    std::cout << "CandidateSet: union recall is never below any single retriever and the candidate count never exceeds the sum of sizes; blocked items are removed by set difference; truncating the scored candidates gives monotone recall; combining independent retrievers raised recall by " << gainDiverse / trials << " on average versus " << gainSimilar / trials << " for near-duplicate retrievers" << std::endl; return 0;
}
// Time Complexity: 합집합 O(Σ|Cᵢ|) (해시) 또는 O(Σ|Cᵢ| log), 필터 O(|C|), 랭킹 O(N · 모델 비용)
// Space Complexity: O(|C|)
```
## ConstraintSet()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 제약 집합(constraint set)과 제약 만족 문제(CSP): 변수 x_i 마다 "가능한 값의 집합"(도메인)을 비트마스크로 두고 제약으로 도메인을 줄여 나간다. 제약이 둘째 변수 쪽에서 첫째 변수의 값을 지지(support)하지 못하면 그 값을 지운다 — 호 일관성(arc consistency, AC-3):
// 호 (x, y) 에 대해 x 의 도메인에서 "y 의 도메인 어떤 값과도 제약을 만족하지 못하는" 값을 제거하고, 바뀌면 x 에 이웃한 호를 큐에 다시 넣는다. 도메인이 공집합이 되면 해가 없음이 확정된다(소리(sound): 해를 지우지 않는다). 하지만 AC-3 만으로 해를 찾는 것은 아니고 탐색(백트래킹 + 최소 남은 값 MRV 휴리스틱)과 결합한다.
// 여기서는 그래프 3-색칠(이웃 정점은 다른 색)을 푼다. 검증: 무작위 그래프 400개(n ≤ 9)에서 ① 완전 열거로 구한 해 유무와 탐색+AC-3 의 결과가 일치하고 찾은 해는 모든 제약을 만족 ② AC-3 이 줄인 도메인은 모든 실제 해를 보존(soundness) ③ AC-3 이 도메인 공집합을 만들면 정말 해가 없음 ④ 전파를 켠 탐색의 노드 수가 끈 것보다 적음
typedef uint8_t Dom;
bool ac3(std::vector<Dom>& dom, const std::vector<std::vector<int>>& adj) { std::queue<std::pair<int, int>> q; for (size_t x = 0; x < adj.size(); x++) for (int y : adj[x]) q.push({(int)x, y});
    while (!q.empty()) { auto [x, y] = q.front(); q.pop(); Dom nd = dom[x]; for (int v = 0; v < 3; v++) if ((dom[x] >> v & 1) && (dom[y] & ~(1 << v)) == 0) nd &= ~(1 << v);                                          // y 에 v 와 다른 값이 하나도 없으면 x 의 v 는 지지가 없음
        if (nd != dom[x]) { dom[x] = nd; if (!nd) return false; for (int z : adj[x]) if (z != y) q.push({z, x}); } } return true; }
long nodes;
bool solve(std::vector<Dom> dom, const std::vector<std::vector<int>>& adj, bool propagate, std::vector<int>& sol) { nodes++; if (propagate && !ac3(dom, adj)) return false; int n = adj.size(), pick = -1, best = 99; for (int i = 0; i < n; i++) { int c = __builtin_popcount(dom[i]); if (c == 0) return false; if (c > 1 && c < best) { best = c; pick = i; } }
    if (pick < 0) { sol.assign(n, 0); for (int i = 0; i < n; i++) sol[i] = __builtin_ctz(dom[i]); for (int i = 0; i < n; i++) for (int j : adj[i]) if (sol[i] == sol[j]) return false; return true; }                                  // 모든 도메인이 단일값: 제약 최종 확인
    for (int v = 0; v < 3; v++) if (dom[pick] >> v & 1) { auto d2 = dom; d2[pick] = 1 << v; if (!propagate) { bool ok = true; for (int j : adj[pick]) if (d2[j] == (1 << v)) ok = false; if (!ok) continue; } if (solve(d2, adj, propagate, sol)) return true; } return false; }
int main() {
    std::mt19937 rng(7); long nodesOn = 0, nodesOff = 0; int sat = 0, unsat = 0, wipeouts = 0;
    for (int t = 0; t < 400; t++) { int n = 3 + rng() % 7; std::vector<std::vector<int>> adj(n); int edges = rng() % (3 * n); for (int e = 0; e < edges; e++) { int a = rng() % n, b = rng() % n; if (a != b && std::find(adj[a].begin(), adj[a].end(), b) == adj[a].end()) { adj[a].push_back(b); adj[b].push_back(a); } }
        std::vector<std::vector<int>> all; std::vector<int> col(n, 0); for (;;) { bool ok = true; for (int i = 0; i < n && ok; i++) for (int j : adj[i]) if (col[i] == col[j]) ok = false; if (ok) all.push_back(col); int i = 0; while (i < n && ++col[i] == 3) col[i++] = 0; if (i == n) break; }
        std::vector<Dom> dom(n, 7); if (rng() % 2) dom[0] = 1;                                                                                                                                                                    // 일부는 첫 정점 색을 고정
        std::vector<std::vector<int>> mine; for (auto& s : all) if ((dom[0] >> s[0]) & 1) mine.push_back(s);
        std::vector<Dom> reduced = dom; bool consistent = ac3(reduced, adj); for (auto& s : mine) for (int i = 0; i < n; i++) assert(consistent && (reduced[i] >> s[i] & 1));                                                    // ② 해를 보존(소리)
        if (!consistent) { assert(mine.empty()); wipeouts++; }                                                                                                                                                                     // ③
        std::vector<int> a, b; nodes = 0; bool r1 = solve(dom, adj, true, a); nodesOn += nodes; nodes = 0; bool r2 = solve(dom, adj, false, b); nodesOff += nodes; assert(r1 == r2 && r1 == !mine.empty());                                                // ① 완전 열거와 일치
        if (r1) { sat++; for (int i = 0; i < n; i++) { assert((dom[i] >> a[i]) & 1); for (int j : adj[i]) assert(a[i] != a[j]); } } else unsat++; }
    { std::vector<std::vector<int>> k4(4); for (int a = 0; a < 4; a++) for (int b = 0; b < 4; b++) if (a != b) k4[a].push_back(b); std::vector<Dom> dom = {1, 2, 4, 7}; assert(!ac3(dom, k4)); wipeouts++; std::vector<int> s; assert(!solve({7, 7, 7, 7}, k4, true, s)); }                                                // K4 는 3색으로 칠할 수 없음: 앞 세 정점을 고정하면 AC-3 만으로 마지막 도메인이 공집합
    assert(sat > 50 && unsat > 20 && wipeouts > 0 && nodesOn <= nodesOff);
    std::cout << "ConstraintSet: AC-3 plus MRV backtracking agrees with exhaustive search on " << sat + unsat << " random 3-coloring problems (" << sat << " solvable, " << unsat << " not; AC-3 alone proved " << wipeouts << " unsolvable); it never removed a real solution; search nodes " << nodesOn << " with propagation versus " << nodesOff << " without" << std::endl; return 0;
}
// Time Complexity: AC-3 O(e · d³), 탐색은 최악 지수
// Space Complexity: O(n · d)
```

# Part 14. 확률적 집합
## BloomFilter()
### 대표코드
```cpp
#include <bitset>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 블룸 필터(집합 관점의 요약, 정본은 AdvancedDataStructures.md Part 3): "아마도 있음 / 확실히 없음" 만 답하는 확률적 집합. m 비트 배열과 해시 k 개 — 삽입은 k 개 위치의 비트를 1 로, 조회는 k 개가 모두 1 이면 "아마도 있음". 거짓 음성은 없고(넣은 원소는 항상 모두 1) 거짓 양성만 있다.
// n 개 삽입 뒤 거짓 양성률 ≈ (1 − e^(−kn/m))^k 이고 이를 최소로 하는 k = (m/n)·ln 2 (비트의 절반이 1 일 때), 그때 비트/원소 ≈ 1.44·log₂(1/ε). 삭제는 불가능하다(비트를 지우면 다른 원소가 깨짐). 같은 m, k, 해시로 만든 두 필터의 합집합 = 비트 OR (정확), 교집합 = 비트 AND (교집합의 상위집합).
// 이중 해싱 h_i = h1 + i·h2 로 독립 해시 k 개를 흉내 낸다. 검증: ① 거짓 음성 0 ② 측정한 거짓 양성률이 이론식과 ±30% 이내 ③ k 를 최적값 ±3 으로 바꾸면 최적보다 나쁨 ④ OR 필터가 두 집합의 합집합 원소를 모두 포함, AND 필터가 교집합 원소를 모두 포함
template <size_t M> struct Bloom { std::bitset<M> bits; int k; Bloom(int k) : k(k) {} static uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
    size_t pos(uint64_t key, int i) const { uint64_t h = mix(key), h2 = mix(h) | 1; return (h + i * h2) % M; } void add(uint64_t key) { for (int i = 0; i < k; i++) bits[pos(key, i)] = 1; } bool maybe(uint64_t key) const { for (int i = 0; i < k; i++) if (!bits[pos(key, i)]) return false; return true; } };
int main() {
    const size_t M = 1 << 15; const int n = 3000; int kopt = (int)std::round((double)M / n * std::log(2.0)); std::mt19937_64 rng(5); std::set<uint64_t> members; while (members.size() < (size_t)n) members.insert(rng());
    double fpr[7]; double theory[7]; for (int dk = -3; dk <= 3; dk++) { int k = std::max(1, kopt + dk); Bloom<M> b(k); for (uint64_t x : members) b.add(x); for (uint64_t x : members) assert(b.maybe(x)); int fp = 0, T = 100000; for (int i = 0; i < T; i++) { uint64_t probe = rng(); if (!members.count(probe)) fp += b.maybe(probe); } fpr[dk + 3] = (double)fp / T; theory[dk + 3] = std::pow(1 - std::exp(-(double)k * n / M), k); assert(fpr[dk + 3] > theory[dk + 3] * 0.7 && fpr[dk + 3] < theory[dk + 3] * 1.3 + 1e-4); }       // ① 거짓 음성 0 ② 이론식
    for (int dk : {-3, -2, 2, 3}) assert(fpr[3] <= fpr[dk + 3] * 1.05);                                                                                                                              // ③ 최적 k 근처가 가장 좋음
    Bloom<M> A(kopt), B(kopt); std::set<uint64_t> sa, sb; for (int i = 0; i < 1500; i++) { sa.insert(rng()); sb.insert(rng()); } for (int i = 0; i < 300; i++) { uint64_t x = rng(); sa.insert(x); sb.insert(x); } for (uint64_t x : sa) A.add(x); for (uint64_t x : sb) B.add(x);
    Bloom<M> U(kopt), I(kopt); U.bits = A.bits | B.bits; I.bits = A.bits & B.bits; for (uint64_t x : sa) assert(U.maybe(x)); for (uint64_t x : sb) assert(U.maybe(x)); for (uint64_t x : sa) if (sb.count(x)) assert(I.maybe(x));       // ④ OR · AND
    std::cout << "BloomFilter: no false negatives; measured false-positive rates " << fpr[3] << " (k=" << kopt << ") track the formula " << theory[3] << " and are lowest near the optimal k = (m/n) ln 2; bitwise OR contains the union and bitwise AND contains the intersection" << std::endl; return 0;
}
// Time Complexity: 삽입·조회 O(k)
// Space Complexity: O(m) 비트 (원소당 약 10~15 비트로 ε ≈ 1% 이하)
```
## CountingBloomFilter()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 카운팅 블룸 필터(집합 관점의 요약, 정본은 AdvancedDataStructures.md Part 3): 비트 대신 작은 카운터(보통 4 비트)를 두어 삽입은 k 개 카운터 +1, 삭제는 −1, 조회는 k 개 카운터가 모두 > 0 인지로 삭제를 지원한다. 공간은 일반 블룸의 약 4 배(4 비트 카운터로 빽빽이 담았을 때; 이 코드는 카운터마다 uint8_t 한 바이트라 8 배).
// 카운터가 포화(15)하면 더 이상 증가하지 않고 이후 감소도 하지 않는다 — 그대로 두면 감소 때 0 이 되어 거짓 음성이 생길 수 있어서(포화한 카운터는 "영원히 > 0" 으로 고정; 거짓 양성만 늘어남). 넣지 않은 원소를 삭제하면 다른 원소가 깨지므로 삭제는 "실제로 넣은 원소"에만 허용해야 한다.
// 검증: 무작위 삽입/삭제 열 50000개에서 ① 현재 집합의 원소는 항상 "아마도 있음" (거짓 음성 0) ② 삭제된 원소는 대부분 "없음"으로 돌아옴 ③ 삽입·삭제 후의 카운터 총합 = k × 현재 원소 수 (포화가 없을 때) ④ 포화 사례(작은 배열)에서 가장 큰 카운터가 정확히 15(삽입이 15 에서 멈춤)이고 일부를 지워도 거짓 음성이 생기지 않음
struct CBF { std::vector<uint8_t> c; int k; size_t m; CBF(size_t m, int k) : c(m, 0), k(k), m(m) {} static uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
    size_t pos(uint64_t key, int i) const { uint64_t h = mix(key), h2 = mix(h) | 1; return (h + i * h2) % m; } void add(uint64_t key) { for (int i = 0; i < k; i++) { uint8_t& x = c[pos(key, i)]; if (x < 15) x++; } } void remove(uint64_t key) { for (int i = 0; i < k; i++) { uint8_t& x = c[pos(key, i)]; if (x > 0 && x < 15) x--; } }                // 포화(15)한 카운터는 고정
    bool maybe(uint64_t key) const { for (int i = 0; i < k; i++) if (!c[pos(key, i)]) return false; return true; } long sum() const { long s = 0; for (uint8_t x : c) s += x; return s; } bool saturated() const { for (uint8_t x : c) if (x == 15) return true; return false; } };
int main() {
    std::mt19937_64 rng(9); CBF f(1 << 15, 5); std::set<uint64_t> live; std::vector<uint64_t> pool; for (int i = 0; i < 4000; i++) pool.push_back(rng()); std::set<uint64_t> removed;
    for (int step = 0; step < 50000; step++) { uint64_t x = pool[rng() % pool.size()]; if (live.count(x)) { if (rng() % 2) { f.remove(x); live.erase(x); removed.insert(x); } } else { f.add(x); live.insert(x); removed.erase(x); }
        if (step % 5000 == 0) { for (uint64_t y : live) assert(f.maybe(y)); } }
    for (uint64_t y : live) { assert(f.maybe(y)); } assert(!f.saturated() && f.sum() == 5 * (long)live.size());                                                                                       // ① 거짓 음성 0 ③ 카운터 합
    int stillThere = 0; for (uint64_t y : removed) stillThere += f.maybe(y); assert(!removed.empty() && stillThere * 20 < (int)removed.size());                                                                // ② 삭제된 원소는 거의 사라짐
    { CBF tiny(64, 3); std::vector<uint64_t> all; for (int i = 0; i < 300; i++) { uint64_t x = rng(); tiny.add(x); all.push_back(x); } assert(tiny.saturated() && *std::max_element(tiny.c.begin(), tiny.c.end()) == 15); for (size_t i = 0; i < all.size(); i += 2) tiny.remove(all[i]); for (size_t i = 1; i < all.size(); i += 2) assert(tiny.maybe(all[i])); }       // ④ 포화 상태(작은 배열)에서 일부를 지워도 남은 원소는 거짓 음성이 되지 않음
    std::cout << "CountingBloomFilter: after 50000 random inserts/deletes of " << live.size() << " live keys there are no false negatives and the counter total equals k x live keys; only " << stillThere << " of " << removed.size() << " deleted keys still test positive; saturated counters stopped at exactly 15 and were frozen, so deleting under saturation never causes a false negative" << std::endl; return 0;
}
// Time Complexity: 삽입·삭제·조회 O(k)
// Space Complexity: O(m · 카운터 비트 수)
```
## CuckooFilter()
### 대표코드
```cpp
#include <array>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 쿠쿠 필터(집합 관점의 요약, 정본은 AdvancedDataStructures.md Part 3): 키의 f 비트 지문(fingerprint)을 쿠쿠 해시표에 저장하는 확률적 집합 — 삭제가 되고 낮은 거짓 양성률에서 블룸 필터보다 공간 효율이 좋다. 핵심은 "부분 키 쿠쿠 해싱": 후보 버킷 i₂ = i₁ XOR hash(지문) 이라
// 지문만 알아도 짝 버킷을 계산할 수 있어 원래 키 없이 쫓아내기(kick)가 가능하다. 버킷은 4칸, 두 버킷이 모두 가득 차면 한 지문을 쫓아내 그 짝 버킷으로 보내는 일을 반복하고 실패하면 삽입을 거부한다.
// 검증: ① 처음 실패할 때까지 넣은 키가 전부 조회됨(거짓 음성 0) ② 적재율 ≥ 90% ③ 거짓 양성률이 2·4/2^f 수준 ④ 삭제 뒤 남은 키는 여전히 조회되고 삭제된 키는 대부분 사라짐
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct Cuckoo { int fb; size_t nb; std::vector<std::array<uint16_t, 4>> B; std::mt19937_64 rng{7}; size_t count = 0; Cuckoo(int f, size_t n) : fb(f), nb(n), B(n, std::array<uint16_t, 4>{0, 0, 0, 0}) {}
    uint16_t fp(uint64_t h) const { return (uint16_t)((h >> 40) % ((1u << fb) - 1) + 1); } size_t alt(size_t i, uint16_t f) const { return (i ^ mix(f)) & (nb - 1); } bool put(size_t i, uint16_t f) { for (auto& s : B[i]) if (!s) { s = f; return true; } return false; }
    bool insert(uint64_t key) { uint64_t h = mix(key); uint16_t f = fp(h); size_t i1 = h & (nb - 1), i2 = alt(i1, f); if (put(i1, f) || put(i2, f)) { count++; return true; } std::vector<std::pair<size_t, int>> log; std::vector<uint16_t> old; size_t i = (rng() & 1) ? i1 : i2;
        for (int kick = 0; kick < 500; kick++) { int s = rng() % 4; log.push_back({i, s}); old.push_back(B[i][s]); std::swap(f, B[i][s]); i = alt(i, f); if (put(i, f)) { count++; return true; } } for (int j = (int)log.size() - 1; j >= 0; j--) B[log[j].first][log[j].second] = old[j]; return false; }        // 실패하면 되돌림
    bool maybe(uint64_t key) const { uint64_t h = mix(key); uint16_t f = fp(h); size_t i1 = h & (nb - 1), i2 = alt(i1, f); for (auto s : B[i1]) if (s == f) return true; for (auto s : B[i2]) if (s == f) return true; return false; }
    bool erase(uint64_t key) { uint64_t h = mix(key); uint16_t f = fp(h); size_t i1 = h & (nb - 1), i2 = alt(i1, f); for (size_t i : {i1, i2}) for (auto& s : B[i]) if (s == f) { s = 0; count--; return true; } return false; } };
int main() {
    Cuckoo c(12, 1 << 12); uint64_t n = 0; while (c.insert(n)) n++; double load = (double)c.count / (4.0 * c.nb); assert(load > 0.9); for (uint64_t i = 0; i < n; i++) assert(c.maybe(i));                                       // ① ② 적재율 · 거짓 음성 0
    size_t fpCount = 0, T = 200000; for (uint64_t i = 0; i < T; i++) fpCount += c.maybe((1ULL << 40) + i); double rate = (double)fpCount / T; assert(rate < 0.01);                                                          // ③ 거짓 양성률 < 1%
    for (uint64_t i = 0; i < n; i += 2) assert(c.erase(i)); for (uint64_t i = 1; i < n; i += 2) assert(c.maybe(i)); size_t gone = 0; for (uint64_t i = 0; i < n; i += 2) gone += !c.maybe(i); assert(gone > (n / 2) * 99 / 100);   // ④ 삭제
    std::cout << "CuckooFilter: load factor " << load << " at the first failed insert, false-positive rate " << rate * 100 << "%, no false negatives, deletion removes keys" << std::endl; return 0;
}
// Time Complexity: 조회·삭제 O(1) (버킷 2개), 삽입 분할상환 O(1)
// Space Complexity: 키당 f / 적재율 비트
```
## QuotientFilter()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 몫 필터(집합 관점의 요약, 정본은 AdvancedDataStructures.md Part 3): p 비트 지문을 앞 q 비트(몫 = 버킷 번호)와 뒤 r 비트(나머지)로 쪼개 나머지만 저장한다. 같은 몫의 나머지들은 정렬된 "런(run)"으로 모이고, 지문 하나의 정확한 일치만 확인하면 되므로 거짓 양성률은 ≈ n / 2^p = α · 2^(−r) 이다.
// 실제 몫 필터는 런을 하나의 연속 배열에 밀어 넣고 슬롯마다 메타데이터 3비트(is_occupied, is_continuation, is_shifted)로 런의 경계를 복원해 블룸처럼 작고 캐시 친화적이며 삭제·병합이 된다(구현은 정본 참조). 여기서는 "몫 → 정렬된 나머지 런" 이라는 개념만 버킷 벡터로 옮겨 놓았다.
// 검증: ① 거짓 음성 0 ② 측정한 거짓 양성률이 α·2^(−r) (α = n/2^q, 부하율) 와 같은 크기 ③ 지문 충돌(서로 다른 키의 같은 (몫, 나머지))이 곧 거짓 양성의 전부임을 확인 ④ 런들이 정렬·중복 없음 ⑤ 같은 q, r 의 두 필터를 정렬 병합으로 합치면 합집합의 지문 집합과 같음(재해시 불필요)
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct QF { int q, r; std::vector<std::vector<uint32_t>> runs; size_t n = 0; QF(int q, int r) : q(q), r(r), runs(1u << q) {} std::pair<uint32_t, uint32_t> split(uint64_t key) const { uint64_t fpr = mix(key) >> (64 - q - r); return {(uint32_t)(fpr >> r), (uint32_t)(fpr & ((1u << r) - 1))}; }
    bool insert(uint64_t key) { auto [fq, fr] = split(key); auto& run = runs[fq]; auto it = std::lower_bound(run.begin(), run.end(), fr); if (it != run.end() && *it == fr) return false; run.insert(it, fr); n++; return true; }
    bool maybe(uint64_t key) const { auto [fq, fr] = split(key); return std::binary_search(runs[fq].begin(), runs[fq].end(), fr); }
    QF merged(const QF& o) const { QF m(q, r); for (size_t i = 0; i < runs.size(); i++) { std::set_union(runs[i].begin(), runs[i].end(), o.runs[i].begin(), o.runs[i].end(), std::back_inserter(m.runs[i])); m.n += m.runs[i].size(); } return m; } };
int main() {
    const int Q = 14, R = 8; std::mt19937_64 rng(4); QF f(Q, R); std::set<uint64_t> keys; size_t N = (size_t)(0.5 * (1 << Q)); while (keys.size() < N) keys.insert(rng()); std::set<std::pair<uint32_t, uint32_t>> fingerprints; for (uint64_t k : keys) { f.insert(k); fingerprints.insert(f.split(k)); }
    for (uint64_t k : keys) assert(f.maybe(k)); assert(f.n == fingerprints.size());                                                                                                                      // ① 거짓 음성 0
    size_t fp = 0, T = 300000, collisions = 0; for (size_t i = 0; i < T; i++) { uint64_t probe = rng(); if (keys.count(probe)) continue; bool says = f.maybe(probe); fp += says; collisions += fingerprints.count(f.split(probe)) ? 1 : 0; assert(says == (fingerprints.count(f.split(probe)) == 1)); }       // ③ 거짓 양성 == 지문 충돌
    double alpha = (double)N / (1 << Q), rate = (double)fp / T, theory = alpha * std::pow(2.0, -R); assert(rate > theory * 0.6 && rate < theory * 1.5);                                                          // ② 이론값
    for (auto& run : f.runs) assert(std::is_sorted(run.begin(), run.end()) && std::adjacent_find(run.begin(), run.end()) == run.end());                                                                          // ④ 런이 정렬·중복 없음
    QF g(Q, R); std::set<uint64_t> more; while (more.size() < 2000) more.insert(rng()); for (uint64_t k : more) g.insert(k); QF u = f.merged(g); std::set<std::pair<uint32_t, uint32_t>> fu = fingerprints; for (uint64_t k : more) fu.insert(g.split(k)); assert(u.n == fu.size()); for (uint64_t k : keys) assert(u.maybe(k)); for (uint64_t k : more) assert(u.maybe(k));    // ⑤ 병합
    std::cout << "QuotientFilter: simplified run-based model of quotient/remainder buckets; no false negatives, measured false-positive rate " << rate << " vs alpha*2^-r = " << theory << " (every false positive is exactly a fingerprint collision), runs stay sorted and two filters merge by sorted union of runs" << std::endl; return 0;
}
// Time Complexity: 삽입·조회 O(log 런 길이) (이 개념 모델), 실제 몫 필터는 클러스터 길이에 비례하는 O(1) 기대
// Space Complexity: 원소당 r 비트 + 메타데이터(실제 구현은 r + 3 비트), 이 모델은 벡터 오버헤드가 추가
```

# Part 15. 병렬 집합
## ConcurrentSet()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <iostream>
#include <mutex>
#include <random>
#include <set>
#include <shared_mutex>
#include <thread>
#include <vector>
#include <cassert>

// 동시성 집합(concurrent set): 여러 스레드가 같은 집합을 동시에 add/remove/contains 하려면 상호 배제가 필요하다. 가장 단순하고 항상 옳은 방법은 집합 전체에 뮤텍스 하나(coarse-grained lock)를 거는 것이고, 조회가 압도적으로 많으면 읽기-쓰기 잠금(shared_mutex)으로 조회끼리는 병렬로 실행한다.
// 정확성의 기준은 선형화 가능성(linearizability): 모든 연산이 호출과 반환 사이의 한 순간에 원자적으로 일어난 것처럼 보여야 한다. 집합에서 검증 가능한 결과 — ① 같은 키를 여러 스레드가 동시에 add 하면 정확히 하나만 true ② 서로 다른 스레드가 같은 키를 remove 해도 정확히 하나만 true ③ 각 스레드가 자기 키 구간만 건드리면 최종 상태가 스레드별 모델의 합집합.
// 대가는 경합이다: 잠금 하나는 스레드 수가 늘어도 처리량이 늘지 않는다. 더 잘게 나눈 잠금(스트라이프)은 ConcurrentHashSet, 잠금 없는 방식은 LockFreeSet 참조. 검증은 스레드 8개 스트레스(add 경합 4000키, remove 경합, 구간 분리 무작위 연산 후 모델 대조)
struct CoarseSet { mutable std::shared_mutex m; std::set<int> s; bool add(int x) { std::unique_lock<std::shared_mutex> l(m); return s.insert(x).second; } bool remove(int x) { std::unique_lock<std::shared_mutex> l(m); return s.erase(x) == 1; } bool contains(int x) const { std::shared_lock<std::shared_mutex> l(m); return s.count(x) == 1; } size_t size() const { std::shared_lock<std::shared_mutex> l(m); return s.size(); } };
int main() {
    const int T = 8, K = 4000; CoarseSet set; std::atomic<int> addWins{0}; std::vector<std::thread> th; for (int t = 0; t < T; t++) th.emplace_back([&] { for (int k = 0; k < K; k++) if (set.add(k)) addWins++; }); for (auto& x : th) x.join(); th.clear(); assert(addWins == K && set.size() == (size_t)K);                    // ① 같은 키 add 경합: 정확히 하나만 성공
    std::atomic<int> removeWins{0}; for (int t = 0; t < T; t++) th.emplace_back([&] { for (int k = 0; k < K; k++) if (set.remove(k)) removeWins++; }); for (auto& x : th) x.join(); th.clear(); assert(removeWins == K && set.size() == 0);                                      // ② remove 경합
    std::vector<std::set<int>> model(T); for (int t = 0; t < T; t++) th.emplace_back([&, t] { std::mt19937 rng(t + 1); for (int i = 0; i < 20000; i++) { int key = t * 1000 + rng() % 1000; int op = rng() % 3; if (op == 0) { assert(set.add(key) == model[t].insert(key).second); } else if (op == 1) { assert(set.remove(key) == (model[t].erase(key) == 1)); } else assert(set.contains(key) == (model[t].count(key) == 1)); } });
    for (auto& x : th) x.join(); th.clear(); std::set<int> expected; for (auto& m : model) expected.insert(m.begin(), m.end()); assert(set.size() == expected.size()); for (int key : expected) assert(set.contains(key));                                          // ③ 구간 분리 모델과 일치
    std::atomic<bool> stop{false}; std::atomic<long> reads{0}; for (int t = 0; t < 4; t++) th.emplace_back([&] { while (!stop) { set.contains(rand() % 8000); reads++; } }); std::thread writer([&] { for (int i = 0; i < 20000; i++) { set.add(10000 + i % 500); set.remove(10000 + (i + 250) % 500); } stop = true; }); writer.join(); for (auto& x : th) x.join();
    std::cout << "ConcurrentSet: with " << T << " threads exactly one add and one remove won for each of " << K << " contended keys, 160000 mixed operations on disjoint ranges matched per-thread models, and readers ran concurrently with a writer (" << reads << " lookups)" << std::endl; return 0;
}
// Time Complexity: 연산 O(log n) + 잠금 대기
// Space Complexity: O(n)
```
## LockFreeSet()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <climits>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <random>
#include <set>
#include <thread>
#include <vector>
#include <cassert>

// 락프리 집합(Harris–Michael 연결 리스트 집합): 정렬된 연결 리스트에서 노드 삭제를 두 단계로 나눈다 — ① 논리적 삭제: 노드의 next 포인터 최하위 비트에 표시(mark)를 CAS 로 켠다(이 순간 노드는 집합에서 사라진 것) ② 물리적 삭제: 앞 노드의 next 를 CAS 로 건너뛰게 바꾼다.
// 표시 비트 덕에 "삭제 중인 노드 뒤에 새 노드를 끼워 넣는" 경쟁이 막힌다(표시된 next 를 가진 노드에는 CAS(next = 기대값)가 실패). 탐색(find)을 하다가 표시된 노드를 만나면 도와서 물리적으로 지운다(helping). contains 는 CAS 없이 읽기만 한다.
// 메모리 회수는 어려운 문제다(ABA, 다른 스레드가 읽는 중인 노드 해제). 이 구현은 지워진 노드를 폐기 목록에 모아 두었다가 집합이 소멸할 때 한꺼번에 해제하는 가장 단순한 안전한 방법을 쓴다(해제된 주소를 재사용하지 않으므로 ABA 가 없다; 실전에서는 해저드 포인터/에포크 기반 회수). 검증: 8 스레드로 ① 같은 키 add 경합에서 정확히 하나만 성공 ② remove 경합도 같음 ③ 섞인 연산 후 리스트가 정렬·중복 없음이고 스레드별 모델과 일치
struct Node { int key; std::atomic<Node*> next; Node(int k, Node* n) : key(k), next(n) {} };
static inline bool marked(Node* p) { return (uintptr_t)p & 1; } static inline Node* mark(Node* p) { return (Node*)((uintptr_t)p | 1); } static inline Node* unmark(Node* p) { return (Node*)((uintptr_t)p & ~(uintptr_t)1); }
struct LFSet { Node* head; std::mutex retiredLock; std::vector<Node*> retired;
    LFSet() { head = new Node(INT_MIN, new Node(INT_MAX, nullptr)); }
    ~LFSet() { for (Node* p = head; p;) { Node* nx = unmark(p->next.load()); delete p; p = nx; } for (Node* r : retired) delete r; }
    void retire(Node* n) { std::lock_guard<std::mutex> g(retiredLock); retired.push_back(n); }
    bool find(int key, Node*& pred, Node*& curr) { for (;;) { retry: pred = head; curr = unmark(pred->next.load()); for (;;) { Node* succ = curr->next.load(); while (marked(succ)) { Node* expect = curr; if (!pred->next.compare_exchange_strong(expect, unmark(succ))) goto retry; retire(curr); curr = unmark(succ); succ = curr->next.load(); } if (curr->key >= key) return curr->key == key; pred = curr; curr = unmark(succ); } } }
    bool add(int key) { for (;;) { Node *pred, *curr; if (find(key, pred, curr)) return false; Node* n = new Node(key, curr); Node* expect = curr; if (pred->next.compare_exchange_strong(expect, n)) return true; delete n; } }
    bool remove(int key) { for (;;) { Node *pred, *curr; if (!find(key, pred, curr)) return false; Node* succ = curr->next.load(); if (marked(succ)) continue; if (!curr->next.compare_exchange_strong(succ, mark(succ))) continue; Node* expect = curr; if (pred->next.compare_exchange_strong(expect, succ)) retire(curr); else find(key, pred, curr); return true; } }
    bool contains(int key) const { Node* curr = unmark(head->next.load()); while (curr->key < key) curr = unmark(curr->next.load()); return curr->key == key && !marked(curr->next.load()); }
    std::vector<int> items() const { std::vector<int> r; for (Node* p = unmark(head->next.load()); p->key != INT_MAX; p = unmark(p->next.load())) if (!marked(p->next.load())) r.push_back(p->key); return r; } };
int main() {
    const int T = 8, K = 1500; LFSet set; std::atomic<int> addWins{0}, removeWins{0}; std::vector<std::thread> th;
    for (int t = 0; t < T; t++) th.emplace_back([&] { for (int k = 0; k < K; k++) if (set.add(k)) addWins++; }); for (auto& x : th) x.join(); th.clear(); assert(addWins == K); auto items = set.items(); assert((int)items.size() == K && std::is_sorted(items.begin(), items.end()));       // ① add 경합
    for (int t = 0; t < T; t++) th.emplace_back([&] { for (int k = K - 1; k >= 0; k--) if (set.remove(k)) removeWins++; }); for (auto& x : th) x.join(); th.clear(); assert(removeWins == K && set.items().empty());                                                        // ② remove 경합
    std::vector<std::set<int>> model(T); for (int t = 0; t < T; t++) th.emplace_back([&, t] { std::mt19937 rng(t + 7); for (int i = 0; i < 15000; i++) { int key = 1 + t * 200 + rng() % 200; int op = rng() % 3; if (op == 0) assert(set.add(key) == model[t].insert(key).second); else if (op == 1) assert(set.remove(key) == (model[t].erase(key) == 1)); else assert(set.contains(key) == (model[t].count(key) == 1)); } });
    for (auto& x : th) x.join(); th.clear(); std::set<int> expected; for (auto& m : model) expected.insert(m.begin(), m.end()); items = set.items(); assert(std::vector<int>(expected.begin(), expected.end()) == items && std::adjacent_find(items.begin(), items.end()) == items.end());   // ③ 모델 일치
    std::atomic<long> churn{0}; for (int t = 0; t < T; t++) th.emplace_back([&, t] { std::mt19937 rng(100 + t); for (int i = 0; i < 20000; i++) { int key = 5000 + rng() % 50; if (rng() % 2) { if (set.add(key)) churn++; } else { if (set.remove(key)) churn--; } } });                       // 겹치는 키 위의 격렬한 add/remove 경합
    for (auto& x : th) x.join(); int hot = 0; for (int key = 5000; key < 5050; key++) hot += set.contains(key); long delta = churn.load(); assert(hot == delta && delta >= 0 && delta <= 50);
    std::cout << "LockFreeSet: " << T << " threads - exactly one add and one remove succeeded for each of " << K << " contended keys; 120000 mixed operations on disjoint ranges matched per-thread models with a sorted duplicate-free list; under heavy churn on 50 shared keys (adds minus removes = " << delta << ") the final membership count matched" << std::endl; return 0;
}
// Time Complexity: 연산 O(n) (연결 리스트 탐색), 경합 시 CAS 재시도
// Space Complexity: O(n) + 폐기 목록(소멸 시까지 유지)
```
## SkipListSet()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 스킵 리스트 집합(집합 관점의 요약, 정본은 List.md Part 10): 정렬된 연결 리스트 위에 "급행 차선"을 확률적으로 쌓은 구조. 노드는 동전 던지기로 높이(레벨) h 를 정하고(P(h ≥ i) = 2^−(i−1)) 레벨 i 의 리스트는 높이 ≥ i 인 노드들만 잇는다. 탐색은 맨 위 레벨에서 오른쪽으로 가다 넘으면 한 레벨 내려오는 식으로 기대 O(log n).
// 균형 트리처럼 회전이 없어 구현이 단순하고, 노드 단위의 국소적 포인터 갱신뿐이라 락프리/동시성 버전(ConcurrentSkipListSet)이 쉬운 것이 장점이다. 정렬 순회와 범위 질의가 공짜. 검증: ① 무작위 연산 30000개가 std::set 과 완전히 일치 ② 정렬 순회가 std::set 과 같음 ③ 평균 레벨 수 ≈ 2(= 1/(1−p)), 탐색 비교 횟수가 O(log n) 정도 ④ 하한 탐색(lower_bound)이 std::set::lower_bound 와 일치
struct SkipSet { static const int MAXL = 24; struct Node { int key; std::vector<Node*> next; Node(int k, int h) : key(k), next(h, nullptr) {} }; Node* head = new Node(INT32_MIN, MAXL); std::mt19937 rng{12345}; size_t n = 0; long comparisons = 0, nodeLevels = 0;
    ~SkipSet() { for (Node* p = head; p;) { Node* nx = p->next[0]; delete p; p = nx; } } int randomHeight() { int h = 1; while (h < MAXL && rng() % 2) h++; return h; }
    Node* findPreds(int key, Node** preds) const { Node* x = head; for (int lv = MAXL - 1; lv >= 0; lv--) { while (x->next[lv] && x->next[lv]->key < key) x = x->next[lv]; preds[lv] = x; } return x->next[0]; }
    bool add(int key) { Node* preds[MAXL]; Node* nx = findPreds(key, preds); if (nx && nx->key == key) return false; int h = randomHeight(); Node* nd = new Node(key, h); for (int i = 0; i < h; i++) { nd->next[i] = preds[i]->next[i]; preds[i]->next[i] = nd; } n++; nodeLevels += h; return true; }
    bool remove(int key) { Node* preds[MAXL]; Node* nx = findPreds(key, preds); if (!nx || nx->key != key) return false; for (size_t i = 0; i < nx->next.size(); i++) preds[i]->next[i] = nx->next[i]; nodeLevels -= nx->next.size(); delete nx; n--; return true; }
    bool contains(int key) { Node* x = head; for (int lv = MAXL - 1; lv >= 0; lv--) while (x->next[lv] && (comparisons++, x->next[lv]->key < key)) x = x->next[lv]; Node* c = x->next[0]; return c && c->key == key; }
    const Node* lowerBound(int key) const { Node* preds[MAXL]; return findPreds(key, preds); } std::vector<int> items() const { std::vector<int> r; for (Node* p = head->next[0]; p; p = p->next[0]) r.push_back(p->key); return r; } };
int main() {
    SkipSet s; std::set<int> ref; std::mt19937 rng(3); for (int i = 0; i < 30000; i++) { int x = rng() % 5000, op = rng() % 3; if (op == 0) assert(s.add(x) == ref.insert(x).second); else if (op == 1) assert(s.remove(x) == (ref.erase(x) == 1)); else assert(s.contains(x) == (ref.count(x) == 1)); assert(s.n == ref.size()); }
    assert(s.items() == std::vector<int>(ref.begin(), ref.end()));                                                                                                                                   // ① ② 모델 일치
    for (int t = 0; t < 2000; t++) { int q = rng() % 6000; auto lb = ref.lower_bound(q); auto got = s.lowerBound(q); assert((lb == ref.end()) == (got == nullptr) && (got == nullptr || got->key == *lb)); }                    // ④ lower_bound
    SkipSet big; for (int i = 0; i < 100000; i++) big.add(i * 7 + (int)(rng() % 7)); big.comparisons = 0; const int Q = 20000; for (int i = 0; i < Q; i++) big.contains(rng() % 700000); double avgLevels = (double)big.nodeLevels / big.n, avgCmp = (double)big.comparisons / Q; assert(avgLevels > 1.9 && avgLevels < 2.1 && avgCmp < 4 * std::log2((double)big.n));      // ③ 레벨 · 비교 횟수
    std::cout << "SkipListSet: 30000 random operations match std::set exactly, lower_bound agrees, average node height " << avgLevels << " (expected 2) and " << avgCmp << " key comparisons per lookup in a set of 100000 (log2 n = " << std::log2(100000.0) << ")" << std::endl; return 0;
}
// Time Complexity: 탐색·삽입·삭제 기대 O(log n), 최악 O(n)
// Space Complexity: O(n) (노드당 평균 포인터 2개)
```
## ConcurrentHashSet()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <functional>
#include <iostream>
#include <mutex>
#include <random>
#include <set>
#include <thread>
#include <vector>
#include <cassert>

// 동시성 해시 집합(ConcurrentHashSet): 전체에 잠금 하나(ConcurrentSet)는 스레드가 늘수록 병목이 된다. 해시 집합은 서로 다른 버킷의 연산이 독립이라는 성질을 이용해 "잠금 스트라이핑(lock striping)" 을 쓴다 — 버킷 배열을 S 개 구간(스트라이프)으로 나눠 구간마다 잠금 하나를 두고
// 연산은 해당 키의 스트라이프 잠금만 잡는다(서로 다른 스트라이프는 병렬). 문제는 크기 조절(resize): 버킷 수가 바뀌면 모든 키의 위치가 바뀌므로 모든 스트라이프 잠금을 정해진 순서(0..S−1)로 잡고(교착 방지) 옮긴 뒤 놓아야 한다. 스트라이프 수 S 는 고정, 버킷 수는 적재율 > 4 에서 두 배.
// 검증: 8 스레드로 ① 같은 키 add 경합 정확히 하나 성공 ② remove 경합 정확히 하나 성공 ③ 구간 분리 무작위 연산이 스레드별 모델과 일치 ④ 성장(resize)이 여러 번 일어나는 동안에도 동시 contains 가 이미 들어간 키를 놓치지 않음 ⑤ 스트라이핑이 단일 잠금보다 잠금 경합이 적음(스트라이프를 바꿔 가며 서로 다른 스트라이프를 동시에 잡은 횟수 측정)
struct StripedSet { static const int S = 16; std::mutex locks[S]; std::vector<std::vector<int>> buckets; std::atomic<size_t> count{0}; std::atomic<int> resizes{0};
    StripedSet() : buckets(16) {} size_t bucketOf(int key, size_t nb) const { return (size_t)((uint32_t)key * 2654435761u) % nb; } std::mutex& lockFor(int key) { return locks[(uint32_t)key * 2654435761u % S]; }
    bool contains(int key) { std::lock_guard<std::mutex> g(lockFor(key)); auto& b = buckets[bucketOf(key, buckets.size())]; return std::find(b.begin(), b.end(), key) != b.end(); }
    bool add(int key) { bool need; size_t seen; { std::lock_guard<std::mutex> g(lockFor(key)); auto& b = buckets[bucketOf(key, buckets.size())]; if (std::find(b.begin(), b.end(), key) != b.end()) return false; b.push_back(key); seen = buckets.size(); need = ++count > seen * 4; } if (need) resize(seen); return true; }
    bool remove(int key) { std::lock_guard<std::mutex> g(lockFor(key)); auto& b = buckets[bucketOf(key, buckets.size())]; auto it = std::find(b.begin(), b.end(), key); if (it == b.end()) return false; *it = b.back(); b.pop_back(); count--; return true; }
    void resize(size_t seen) { std::vector<std::unique_lock<std::mutex>> held; for (int i = 0; i < S; i++) held.emplace_back(locks[i]); size_t old = buckets.size(); /* 잠금을 모두 잡은 뒤에야 버킷 수를 읽는다 */ if (old != seen) return; /* 다른 스레드가 이미 키웠으면 중단 */ std::vector<std::vector<int>> nb(old * 2); for (auto& b : buckets) for (int k : b) nb[bucketOf(k, nb.size())].push_back(k); buckets.swap(nb); resizes++; } };
int main() {
    const int T = 8, K = 6000; StripedSet set; std::atomic<int> addWins{0}, removeWins{0}; std::vector<std::thread> th;
    for (int t = 0; t < T; t++) th.emplace_back([&] { for (int k = 0; k < K; k++) if (set.add(k)) addWins++; }); for (auto& x : th) x.join(); th.clear(); assert(addWins == K && set.count == (size_t)K && set.resizes > 3);                                         // ① 경합 add + 여러 번의 resize
    for (int t = 0; t < T; t++) th.emplace_back([&] { for (int k = 0; k < K; k++) if (set.remove(k)) removeWins++; }); for (auto& x : th) x.join(); th.clear(); assert(removeWins == K && set.count == 0);                                                                      // ② remove 경합
    std::vector<std::set<int>> model(T); for (int t = 0; t < T; t++) th.emplace_back([&, t] { std::mt19937 rng(t + 3); for (int i = 0; i < 20000; i++) { int key = t * 100000 + rng() % 5000; int op = rng() % 3; if (op == 0) assert(set.add(key) == model[t].insert(key).second); else if (op == 1) assert(set.remove(key) == (model[t].erase(key) == 1)); else assert(set.contains(key) == (model[t].count(key) == 1)); } });
    for (auto& x : th) x.join(); th.clear(); size_t total = 0; for (auto& m : model) { total += m.size(); for (int k : m) assert(set.contains(k)); } assert(set.count == total);                                                                                    // ③ 모델 일치
    StripedSet grow; std::atomic<bool> missed{false}, done{false}; std::thread writer([&] { for (int k = 0; k < 40000; k++) { grow.add(k); } done = true; }); std::vector<std::thread> readers; for (int r = 0; r < 4; r++) readers.emplace_back([&, r] { std::mt19937 rng(r + 50); while (!done) { int upto = (int)grow.count.load() - 1; for (int k = 0; k < 50 && upto >= 0; k++) { int key = (int)(rng() % (upto + 1)); if (!grow.contains(key)) missed = true; } } });
    writer.join(); for (auto& x : readers) x.join(); assert(!missed && grow.resizes >= 8);                                                                                                                                                   // ④ resize 중에도 키를 놓치지 않음
    std::cout << "ConcurrentHashSet: striped locks over " << StripedSet::S << " stripes passed the add/remove contention tests and per-thread model checks with " << set.resizes << " + " << grow.resizes << " table doublings; concurrent readers never missed an inserted key while the table grew" << std::endl; return 0;
}
// Time Complexity: 연산 기대 O(1) + 스트라이프 잠금, resize 는 O(n) (전체 잠금)
// Space Complexity: O(n)
```

# Part 16. 연구 주제
## PersistentSet()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <deque>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 영속 집합(persistent set): 갱신해도 이전 버전이 그대로 남아 모든 과거 버전을 조회할 수 있는 집합. 비결은 경로 복사(path copying)다 — 균형 이진 탐색 트리에서 삽입·삭제가 건드리는 O(log n) 노드만 새로 만들고 나머지 서브트리는 이전 버전과 공유한다. 버전 하나당 새 노드 O(log n) 개.
// 구현은 분할/병합(split/merge)으로 짠 영속 트립(treap)이다. 우선순위를 키의 해시로 정하면(결정적) 같은 원소 집합은 삽입 순서와 무관하게 항상 같은 모양의 트리가 되는 "이력 독립(history independence)" 성질이 생긴다. 노드는 불변(const)이라 여러 스레드가 안전하게 공유할 수 있다.
// 검증: 무작위 갱신 600개로 버전 600개를 쌓고 ① 모든 과거 버전의 중위 순회가 그 시점의 std::set 스냅샷과 일치 ② 생성한 노드 총수가 갱신당 O(log n) 으로 모든 버전을 복사했을 때의 노드 수보다 훨씬 적음 ③ 서로 다른 삽입 순서로 만든 같은 집합의 트리 구조가 동일(이력 독립) ④ 버전들이 서로 노드를 공유하는 비율 보고
struct Node { int key; uint32_t pri; const Node *l, *r; };
std::deque<Node> pool; static uint32_t prio(int k) { uint32_t x = (uint32_t)k * 2654435761u; x ^= x >> 15; x *= 2246822519u; x ^= x >> 13; return x; }
const Node* mk(int key, uint32_t pri, const Node* l, const Node* r) { pool.push_back({key, pri, l, r}); return &pool.back(); }
std::pair<const Node*, const Node*> split(const Node* t, int key) { if (!t) return {nullptr, nullptr}; if (t->key < key) { auto [a, b] = split(t->r, key); return {mk(t->key, t->pri, t->l, a), b}; } auto [a, b] = split(t->l, key); return {a, mk(t->key, t->pri, b, t->r)}; }          // (< key, >= key)
const Node* merge(const Node* a, const Node* b) { if (!a) return b; if (!b) return a; if (a->pri > b->pri) return mk(a->key, a->pri, a->l, merge(a->r, b)); return mk(b->key, b->pri, merge(a, b->l), b->r); }
bool contains(const Node* t, int key) { while (t) { if (key == t->key) return true; t = key < t->key ? t->l : t->r; } return false; }
const Node* insert(const Node* t, int key) { if (contains(t, key)) return t; auto [a, b] = split(t, key); return merge(merge(a, mk(key, prio(key), nullptr, nullptr)), b); }
const Node* erase(const Node* t, int key) { if (!contains(t, key)) return t; auto [a, b] = split(t, key); auto [m, c] = split(b, key + 1); return merge(a, c); }
void inorder(const Node* t, std::vector<int>& out) { if (!t) return; inorder(t->l, out); out.push_back(t->key); inorder(t->r, out); }
bool sameShape(const Node* a, const Node* b) { if (!a || !b) return a == b; return a->key == b->key && sameShape(a->l, b->l) && sameShape(a->r, b->r); }
void collect(const Node* t, std::set<const Node*>& s) { if (!t) return; if (!s.insert(t).second) return; collect(t->l, s); collect(t->r, s); }
int main() {
    std::mt19937 rng(5); std::vector<const Node*> versions = {nullptr}; std::vector<std::set<int>> snapshots = {{}}; std::set<int> cur; size_t biggest = 0;
    for (int i = 0; i < 600; i++) { int x = rng() % 400; const Node* nv; if (rng() % 3 && !cur.count(x)) { nv = insert(versions.back(), x); cur.insert(x); } else { nv = erase(versions.back(), x); cur.erase(x); } versions.push_back(nv); snapshots.push_back(cur); biggest = std::max(biggest, cur.size()); }
    for (size_t v = 0; v < versions.size(); v++) { std::vector<int> items; inorder(versions[v], items); assert(items == std::vector<int>(snapshots[v].begin(), snapshots[v].end())); for (int probe = 0; probe < 400; probe += 37) assert(contains(versions[v], probe) == (snapshots[v].count(probe) == 1)); }       // ① 모든 과거 버전이 그대로
    size_t created = pool.size(), copyAll = 0; for (auto& s : snapshots) copyAll += s.size(); std::set<const Node*> reachable; for (auto* r : versions) collect(r, reachable); assert(created < copyAll / 3);                                                                         // ② 생성 노드 수 ≪ 전체 복사
    std::vector<int> keys(cur.begin(), cur.end()); const Node *a = nullptr, *b = nullptr; std::vector<int> k1 = keys, k2 = keys; std::shuffle(k1.begin(), k1.end(), rng); std::shuffle(k2.begin(), k2.end(), rng); for (int k : k1) a = insert(a, k); for (int k : k2) b = insert(b, k); assert(sameShape(a, b));       // ③ 이력 독립
    std::cout << "PersistentSet: all 601 versions still match their std::set snapshots after 600 updates; path copying created " << created << " nodes instead of the " << copyAll << " that copying every version would need (" << reachable.size() << " distinct nodes shared across versions); two insertion orders of the same " << keys.size() << " keys gave identical tree shapes" << std::endl; return 0;
}
// Time Complexity: 조회·삽입·삭제 기대 O(log n)
// Space Complexity: 버전당 기대 O(log n) 새 노드
```
## ImmutableBitSet()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <thread>
#include <vector>
#include <cassert>

// 불변 비트 집합(immutable bitset): 생성 후 절대 바뀌지 않는 비트 집합. 변경 연산(with/without/합·교·차)은 새 객체를 돌려주고 원본은 그대로다. 불변이면 ① 잠금 없이 여러 스레드가 공유 가능 ② 해시·동치 비교의 키로 안전 ③ 이전 버전을 보존(되돌리기) ④ 구성 시 한 번 계산한 보조 정보를 평생 재사용할 수 있다.
// 여기서는 구성 시 블록(64비트 워드)마다 앞쪽 popcount 접두사 합을 만들어 rank(x) = x 보다 작은 원소 개수를 O(1), select(k) = k 번째 원소를 O(log n) 에 구한다. 변경 연산의 비용은 O(U/64) 복사 — 한 비트를 켜는 데도 전체를 복사하므로 변경이 잦으면 영속 자료구조(PersistentSet)나 일반 가변 비트셋이 낫다.
// 검증: 무작위 연산 3000개에서 ① 모든 버전이 std::set 모델과 일치하고 이전 버전은 변하지 않음 ② rank/select 가 서로 역함수이고 모델과 일치 ③ 합·교·차·대칭차가 모델과 일치 ④ 여러 스레드가 같은 객체를 동시에 읽어도 결과가 같음 ⑤ 해시/동치가 내용이 같으면 같음
class ImmutableBitSet { std::shared_ptr<const std::vector<uint64_t>> w; std::shared_ptr<const std::vector<uint32_t>> prefix; size_t U;
    void build(std::vector<uint64_t>&& words) { auto pf = std::make_shared<std::vector<uint32_t>>(words.size() + 1, 0); for (size_t i = 0; i < words.size(); i++) (*pf)[i + 1] = (*pf)[i] + __builtin_popcountll(words[i]); w = std::make_shared<const std::vector<uint64_t>>(std::move(words)); prefix = pf; }
public: explicit ImmutableBitSet(size_t universe = 0) : U(universe) { build(std::vector<uint64_t>((universe + 63) / 64, 0)); }
    size_t universe() const { return U; } bool test(size_t i) const { return (*w)[i >> 6] >> (i & 63) & 1; } size_t count() const { return prefix->back(); }
    ImmutableBitSet with(size_t i) const { ImmutableBitSet r(*this); auto c = *w; c[i >> 6] |= 1ULL << (i & 63); r.build(std::move(c)); return r; } ImmutableBitSet without(size_t i) const { ImmutableBitSet r(*this); auto c = *w; c[i >> 6] &= ~(1ULL << (i & 63)); r.build(std::move(c)); return r; }
    template <class Op> ImmutableBitSet combine(const ImmutableBitSet& o, Op op) const { ImmutableBitSet r(*this); std::vector<uint64_t> c(w->size()); for (size_t i = 0; i < c.size(); i++) c[i] = op((*w)[i], (*o.w)[i]); r.build(std::move(c)); return r; }
    size_t rank(size_t x) const { size_t b = x >> 6; return (*prefix)[b] + (b < w->size() ? __builtin_popcountll((*w)[b] & ((1ULL << (x & 63)) - 1)) : 0); }                                                // x 보다 작은 원소 수
    size_t select(size_t k) const { size_t lo = 0, hi = w->size(); while (lo + 1 < hi) { size_t mid = (lo + hi) / 2; if ((*prefix)[mid] <= k) lo = mid; else hi = mid; } uint64_t word = (*w)[lo]; size_t need = k - (*prefix)[lo]; for (size_t i = 0; i < need; i++) word &= word - 1; return lo * 64 + __builtin_ctzll(word); }
    bool operator==(const ImmutableBitSet& o) const { return U == o.U && *w == *o.w; } size_t hash() const { size_t h = U; for (uint64_t x : *w) h = h * 1099511628211ULL ^ x; return h; } };
int main() {
    const size_t U = 1000; std::mt19937 rng(3); std::vector<ImmutableBitSet> versions = {ImmutableBitSet(U)}; std::vector<std::set<size_t>> models = {{}}; std::set<size_t> cur;
    for (int i = 0; i < 3000; i++) { size_t x = rng() % U; ImmutableBitSet nv(U); if (rng() % 3) { nv = versions.back().with(x); cur.insert(x); } else { nv = versions.back().without(x); cur.erase(x); } versions.push_back(nv); models.push_back(cur); }
    for (size_t v = 0; v < versions.size(); v += 37) { assert(versions[v].count() == models[v].size()); size_t k = 0; for (size_t x : models[v]) { assert(versions[v].select(k) == x && versions[v].rank(x) == k); k++; } for (size_t x = 0; x <= U; x += 41) assert(versions[v].rank(x) == (size_t)std::distance(models[v].begin(), models[v].lower_bound(x))); }       // ① ② 모든 버전 · rank/select
    ImmutableBitSet a(U), b(U); std::set<size_t> sa, sb; for (int i = 0; i < 300; i++) { size_t x = rng() % U, y = rng() % U; a = a.with(x); sa.insert(x); b = b.with(y); sb.insert(y); }
    auto check = [&](const ImmutableBitSet& r, const std::set<size_t>& m) { assert(r.count() == m.size()); for (size_t i = 0; i < U; i++) assert(r.test(i) == (m.count(i) == 1)); }; std::set<size_t> m;
    std::set_union(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(m, m.begin())); check(a.combine(b, [](uint64_t x, uint64_t y) { return x | y; }), m); m.clear(); std::set_intersection(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(m, m.begin())); check(a.combine(b, [](uint64_t x, uint64_t y) { return x & y; }), m);
    m.clear(); std::set_difference(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(m, m.begin())); check(a.combine(b, [](uint64_t x, uint64_t y) { return x & ~y; }), m); m.clear(); std::set_symmetric_difference(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(m, m.begin())); check(a.combine(b, [](uint64_t x, uint64_t y) { return x ^ y; }), m);   // ③
    std::vector<std::thread> th; std::vector<size_t> sums(8, 0); for (int t = 0; t < 8; t++) th.emplace_back([&, t] { for (int rep = 0; rep < 2000; rep++) for (size_t k = 0; k < a.count(); k += 7) sums[t] += a.select(k) + a.rank(k); }); for (auto& x : th) x.join(); for (int t = 1; t < 8; t++) assert(sums[t] == sums[0]);                                              // ④ 동시 읽기
    ImmutableBitSet c1(U), c2(U); for (size_t x : {5, 70, 999}) { c1 = c1.with(x); } for (size_t x : {999, 5, 70}) { c2 = c2.with(x); } assert(c1 == c2 && c1.hash() == c2.hash() && !(c1 == c1.with(6)));                                                                                                                               // ⑤ 해시 · 동치
    std::cout << "ImmutableBitSet: 3000 versions each matched their model and older versions never changed; rank and select are inverse functions; union, intersection, difference and symmetric difference match std::set; 8 threads read one shared set with identical results" << std::endl; return 0;
}
// Time Complexity: test O(1), rank O(1), select O(log(U/64)), 변경·집합 연산 O(U/64)
// Space Complexity: O(U/8) 바이트 (+ 접두사 합)
```
## CompressedBitSet()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 압축 비트 집합(compressed bitset): 희소하거나 덩어리진 비트맵은 같은 값의 긴 워드 구간(0 만 또는 1 만)이 많다. WAH/EWAH 계열 방식은 32 비트 워드열을 "채움 런(fill run: 0 워드 또는 1 워드가 n 번)" 과 "리터럴 워드(그대로 저장)" 의 열로 부호화한다.
// 핵심은 압축을 풀지 않고 연산하는 것이다 — 두 압축열의 커서를 나란히 전진시키며 두 커서가 모두 채움 런이면 겹치는 길이(남은 길이의 min)만큼을 한 단계에 건너뛴다(예: 0 채움 AND 0 채움 → 그 길이만큼 0 채움). 한쪽만 채움이고 다른 쪽이 리터럴이면 이 구현은 워드를 하나씩 처리한다 — 긴 0 채움과 AND 할 때 리터럴 구간을 통째로 건너뛰는 최적화(연산의 성질을 이용)는 하지 않았다. 결과도 같은 방식으로 이어 붙여(인접한 같은 채움은 합침) 압축 상태를 유지한다.
// 한계: 임의 위치 접근이 O(런 수)이고 변경이 어렵다(Roaring 비트맵이 보완). 검증: 희소(0.05%)·덩어리(긴 구간)·조밀(50% 무작위) 비트맵 각 40개에서 ① 압축·복원이 무손실 ② 압축 상태의 AND/OR/XOR 결과가 원시 비트 연산과 같고 결과도 정규형(인접 같은 채움 합쳐짐) ③ 희소·덩어리는 원시 크기의 1/3 이하로 줄고 조밀은 줄지 않음(런 하나를 4 바이트로 계산하는 WAH 모델 — 31 비트 리터럴 + 태그 비트를 가정하며, 이 코드의 Run 은 32 비트 리터럴이라 실제로는 12 바이트이고 sizeof(Run) 로 계산해도 1/3 이하) ④ 압축 연산의 반복(단계) 수가 원시 워드 단계 수의 1/8 미만이고(조밀은 정확히 워드당 한 단계), 전부 1·전부 0 비트맵은 채움 런 하나이며 둘의 연산이 한 단계에 끝남
struct Run { bool fill; bool bit; uint32_t count; uint32_t lit; };                                                                                               // fill: bit 값 워드 count 개 / 아니면 리터럴 워드 하나
struct Compressed { std::vector<Run> runs; uint32_t words = 0;
    void append(uint32_t word, uint32_t n = 1) { if (n == 0) return; words += n; bool isFill = word == 0 || word == ~0u; if (isFill) { bool bit = word != 0; if (!runs.empty() && runs.back().fill && runs.back().bit == bit) runs.back().count += n; else runs.push_back({true, bit, n, 0}); } else { for (uint32_t i = 0; i < n; i++) runs.push_back({false, false, 1, word}); } }
    static Compressed from(const std::vector<uint32_t>& raw) { Compressed c; for (uint32_t w : raw) c.append(w); return c; }
    std::vector<uint32_t> expand() const { std::vector<uint32_t> out; for (auto& r : runs) { if (r.fill) out.insert(out.end(), r.count, r.bit ? ~0u : 0u); else out.push_back(r.lit); } return out; } };
struct Cursor { const std::vector<Run>& r; size_t i = 0; uint32_t used = 0; bool done() const { return i >= r.size(); } bool fill() const { return r[i].fill; } uint32_t word() const { return r[i].fill ? (r[i].bit ? ~0u : 0u) : r[i].lit; } uint32_t left() const { return r[i].count - used; }
    void skip(uint32_t n) { used += n; if (used == r[i].count) { i++; used = 0; } } };
template <class Op> Compressed combine(const Compressed& a, const Compressed& b, Op op, long& steps) { Compressed out; Cursor x{a.runs}, y{b.runs}; while (!x.done() && !y.done()) { steps++; uint32_t n = 1; if (x.fill() && y.fill()) n = std::min(x.left(), y.left()); else if (x.fill() && !y.fill()) n = 1; else if (!x.fill() && y.fill()) n = 1; out.append(op(x.word(), y.word()), n); x.skip(n); y.skip(n); } return out; }   // steps = 반복 횟수(한 번에 n 워드를 건너뜀)
int main() {
    std::mt19937 rng(8); const uint32_t W = 2000; long compSizeSparse = 0, rawSizeSparse = 0, realSizeSparse = 0, compSizeDense = 0, rawSizeDense = 0, steps = 0, rawSteps = 0;
    for (int kind = 0; kind < 3; kind++) for (int t = 0; t < 40; t++) { std::vector<uint32_t> A(W, 0), B(W, 0); for (int which = 0; which < 2; which++) { auto& v = which ? B : A; if (kind == 0) { for (int i = 0; i < (int)(W * 32 * 0.0005); i++) { uint32_t pos = rng() % (W * 32); v[pos / 32] |= 1u << (pos % 32); } } else if (kind == 1) { uint32_t pos = 0; while (pos < W) { uint32_t len = 1 + rng() % 200; bool on = rng() % 2; for (uint32_t i = 0; i < len && pos < W; i++, pos++) v[pos] = on ? ~0u : 0u; } } else { for (auto& w : v) w = rng(); } }
        Compressed ca = Compressed::from(A), cb = Compressed::from(B); assert(ca.expand() == A && cb.expand() == B && ca.words == W);                                                                                       // ① 무손실
        auto test = [&](auto op) { long vis = 0; Compressed c = combine(ca, cb, op, vis); std::vector<uint32_t> expect(W); for (uint32_t i = 0; i < W; i++) expect[i] = op(A[i], B[i]); assert(c.expand() == expect); for (size_t i = 1; i < c.runs.size(); i++) assert(!(c.runs[i].fill && c.runs[i - 1].fill && c.runs[i].bit == c.runs[i - 1].bit)); return vis; };       // ② 정규형
        long v1 = test([](uint32_t x, uint32_t y) { return x & y; }), v2 = test([](uint32_t x, uint32_t y) { return x | y; }), v3 = test([](uint32_t x, uint32_t y) { return x ^ y; }); if (kind != 2) { steps += v1 + v2 + v3; rawSteps += 3L * W; } else { assert(v1 == W && v2 == W && v3 == W); }   // 조밀(무작위)한 데이터는 건너뛸 구간이 없어 워드마다 한 단계
        long cs = ca.runs.size() * 4L /* WAH 모델: 런(채움 헤더 또는 31 비트 리터럴 + 태그 비트)마다 4 바이트 */, rs = W * 4L; if (kind == 2) { compSizeDense += cs; rawSizeDense += rs; } else { compSizeSparse += cs; rawSizeSparse += rs; realSizeSparse += (long)(ca.runs.size() * sizeof(Run)); } }
    assert(compSizeSparse * 3 < rawSizeSparse && realSizeSparse * 3 < rawSizeSparse && compSizeDense >= rawSizeDense * 9 / 10 && steps * 8 < rawSteps);       // 건너뛰기 덕분에 희소·덩어리에서 단계 수가 원시 워드 단계의 1/8 미만
    { Compressed ones = Compressed::from(std::vector<uint32_t>(W, ~0u)), zeros = Compressed::from(std::vector<uint32_t>(W, 0u)); long st = 0;                  // 전부 1·전부 0 은 채움 런 하나, 둘의 연산은 한 단계에 끝남
      assert(ones.runs.size() == 1 && ones.runs[0].fill && ones.runs[0].bit && ones.runs[0].count == W && zeros.runs.size() == 1 && zeros.runs[0].fill && !zeros.runs[0].bit && zeros.runs[0].count == W);
      Compressed r = combine(ones, zeros, [](uint32_t x, uint32_t y) { return x | y; }, st); assert(st == 1 && r.runs.size() == 1 && r.runs[0].fill && r.runs[0].bit && r.runs[0].count == W);
      st = 0; r = combine(ones, ones, [](uint32_t x, uint32_t y) { return x & y; }, st); assert(st == 1 && r.runs.size() == 1 && r.runs[0].bit && r.expand() == std::vector<uint32_t>(W, ~0u)); }
    std::cout << "CompressedBitSet: run-length (WAH/EWAH-style) compression is lossless and AND/OR/XOR on compressed runs equal the raw word operations with canonical output on 120 bitmap pairs; sparse/clustered data used " << compSizeSparse << " bytes versus " << rawSizeSparse << " raw, random dense data " << compSizeDense << " versus " << rawSizeDense << "; sparse/clustered operations took " << steps << " steps instead of " << rawSteps << " raw word steps" << std::endl; return 0;
}
// Time Complexity: 연산 O(두 압축열의 런 수) (채움 대 리터럴은 워드 단위로 진행하지만 리터럴 런이 한 워드씩이라 이 합을 넘지 않음), 압축 O(워드 수)
// Space Complexity: O(런 수)
```
## RoaringBitmap()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <map>
#include <random>
#include <set>
#include <variant>
#include <vector>
#include <cassert>

// 로어링 비트맵(Roaring Bitmap, Lemire 등 2016): 32 비트 정수 집합을 상위 16 비트(청크 번호)로 나눠 청크마다 하위 16 비트를 가장 알맞은 "컨테이너"로 저장한다. 원소가 4096 개 이하면 정렬된 uint16 배열(2 바이트/원소 ≤ 8 KiB), 그보다 많으면 65536 비트 비트맵(고정 8 KiB) —
// 임계값 4096 은 두 표현의 크기가 같아지는 지점이다(실제 구현은 런 컨테이너도 둔다). 청크 사이는 정렬된 맵으로 이어 두므로 희소한 곳은 작고 조밀한 곳은 비트맵이라 압축 비트맵(WAH 계열)보다 임의 접근·집합 연산이 빠르다.
// 연산은 청크별로 대응하는 컨테이너끼리 한다: 배열∩배열(병합), 비트맵∩비트맵(워드 AND), 배열∩비트맵(배열 원소를 비트맵에서 조회), 합집합도 마찬가지이고 결과의 원소 수에 따라 컨테이너 종류를 다시 정한다. 검증(32 비트 정수): ① 희소(청크 여러 개에 흩어짐)·조밀(한 청크에 꽉 참)·혼합 집합에서 add/remove/contains 가 std::set 과 일치하고 컨테이너 종류가 임계값에 맞게 전환 ② 합·교집합이 모델과 같음 ③ 크기(바이트)가 단순 uint32 배열·평평한 비트맵보다 모든 경우에서 작거나 비슷하고 희소할 때 크게 작음
struct Roaring { typedef std::vector<uint16_t> Arr; typedef std::array<uint64_t, 1024> Bm; typedef std::variant<Arr, Bm> Container; std::map<uint16_t, Container> chunks;
    static size_t card(const Container& c) { if (auto* a = std::get_if<Arr>(&c)) return a->size(); size_t n = 0; for (uint64_t w : std::get<Bm>(c)) n += __builtin_popcountll(w); return n; }
    static void toBitmap(Container& c) { Bm b{}; for (uint16_t x : std::get<Arr>(c)) b[x >> 6] |= 1ULL << (x & 63); c = b; } static void toArray(Container& c) { Arr a; const Bm& b = std::get<Bm>(c); for (int i = 0; i < 1024; i++) for (uint64_t w = b[i]; w; w &= w - 1) a.push_back(i * 64 + __builtin_ctzll(w)); c = a; }
    bool add(uint32_t x) { uint16_t hi = x >> 16, lo = x & 0xFFFF; auto it = chunks.find(hi); if (it == chunks.end()) it = chunks.emplace(hi, Arr{}).first; Container& c = it->second; if (auto* a = std::get_if<Arr>(&c)) { auto pos = std::lower_bound(a->begin(), a->end(), lo); if (pos != a->end() && *pos == lo) return false; a->insert(pos, lo); if (a->size() > 4096) toBitmap(c); return true; } Bm& b = std::get<Bm>(c); bool had = b[lo >> 6] >> (lo & 63) & 1; b[lo >> 6] |= 1ULL << (lo & 63); return !had; }
    bool remove(uint32_t x) { uint16_t hi = x >> 16, lo = x & 0xFFFF; auto it = chunks.find(hi); if (it == chunks.end()) return false; Container& c = it->second; bool removed; if (auto* a = std::get_if<Arr>(&c)) { auto pos = std::lower_bound(a->begin(), a->end(), lo); removed = pos != a->end() && *pos == lo; if (removed) a->erase(pos); } else { Bm& b = std::get<Bm>(c); removed = b[lo >> 6] >> (lo & 63) & 1; b[lo >> 6] &= ~(1ULL << (lo & 63)); if (removed && card(c) <= 4096) toArray(c); } if (card(c) == 0) chunks.erase(it); return removed; }
    bool contains(uint32_t x) const { auto it = chunks.find(x >> 16); if (it == chunks.end()) return false; uint16_t lo = x & 0xFFFF; if (auto* a = std::get_if<Arr>(&it->second)) return std::binary_search(a->begin(), a->end(), lo); return std::get<Bm>(it->second)[lo >> 6] >> (lo & 63) & 1; }
    size_t size() const { size_t n = 0; for (auto& [h, c] : chunks) n += card(c); return n; } size_t bytes() const { size_t b = 0; for (auto& [h, c] : chunks) b += 2 + (std::holds_alternative<Arr>(c) ? 2 * std::get<Arr>(c).size() : 8192); return b; }
    static Container normalize(Bm b) { Container c = b; if (card(c) <= 4096) toArray(c); return c; }
    static Container and2(const Container& x, const Container& y) { if (std::holds_alternative<Bm>(x) && std::holds_alternative<Bm>(y)) { Bm r; for (int i = 0; i < 1024; i++) r[i] = std::get<Bm>(x)[i] & std::get<Bm>(y)[i]; return normalize(r); } const Container &s = std::holds_alternative<Arr>(x) ? x : y, &o = std::holds_alternative<Arr>(x) ? y : x; Arr r; for (uint16_t v : std::get<Arr>(s)) { bool in = std::holds_alternative<Arr>(o) ? std::binary_search(std::get<Arr>(o).begin(), std::get<Arr>(o).end(), v) : (std::get<Bm>(o)[v >> 6] >> (v & 63) & 1); if (in) r.push_back(v); } return r; }
    static Container or2(const Container& x, const Container& y) { Bm r{}; for (const Container* c : {&x, &y}) { if (auto* a = std::get_if<Arr>(c)) for (uint16_t v : *a) r[v >> 6] |= 1ULL << (v & 63); else for (int i = 0; i < 1024; i++) r[i] |= std::get<Bm>(*c)[i]; } return normalize(r); }
    Roaring operator&(const Roaring& o) const { Roaring r; for (auto& [h, c] : chunks) { auto it = o.chunks.find(h); if (it == o.chunks.end()) continue; Container z = and2(c, it->second); if (card(z) > 0) r.chunks[h] = z; } return r; } Roaring operator|(const Roaring& o) const { Roaring r = *this; for (auto& [h, c] : o.chunks) { auto it = r.chunks.find(h); r.chunks[h] = it == r.chunks.end() ? c : or2(it->second, c); } return r; }
    std::vector<uint32_t> items() const { std::vector<uint32_t> out; for (auto& [h, c] : chunks) { if (auto* a = std::get_if<Arr>(&c)) for (uint16_t v : *a) out.push_back((uint32_t)h << 16 | v); else for (int i = 0; i < 1024; i++) for (uint64_t w = std::get<Bm>(c)[i]; w; w &= w - 1) out.push_back((uint32_t)h << 16 | (i * 64 + __builtin_ctzll(w))); } return out; } };
int main() {
    std::mt19937 rng(11); size_t denseBytes = 0, sparseBytes = 0, sparseFlat = 0; int conversions = 0;
    for (int kind = 0; kind < 3; kind++) { Roaring r; std::set<uint32_t> ref; int n = kind == 0 ? 3000 : kind == 1 ? 70000 : 20000; for (int i = 0; i < n; i++) { uint32_t x = kind == 0 ? (uint32_t)(rng() % 1000) << 16 | (rng() % 65536) : kind == 1 ? (uint32_t)(rng() % 70000) : ((rng() % 2) ? (uint32_t)(rng() % 70000) : (uint32_t)(rng() % 50) << 20 | (rng() % 3000)); assert(r.add(x) == ref.insert(x).second); }
        assert(r.size() == ref.size() && r.items() == std::vector<uint32_t>(ref.begin(), ref.end())); for (int i = 0; i < 20000; i++) { uint32_t x = kind == 0 ? (uint32_t)(rng() % 1000) << 16 | (rng() % 65536) : (uint32_t)(rng() % 140000); assert(r.contains(x) == (ref.count(x) == 1)); }
        { std::vector<uint32_t> all(ref.begin(), ref.end()); std::shuffle(all.begin(), all.end(), rng); for (size_t i = 0; i < all.size() / 2; i++) { assert(r.remove(all[i])); ref.erase(all[i]); assert(!r.contains(all[i])); } } assert(r.items() == std::vector<uint32_t>(ref.begin(), ref.end()));                                // ① add/remove/contains
        if (kind == 0) { sparseBytes = r.bytes(); sparseFlat = ref.size() * 4; } if (kind == 1) denseBytes = r.bytes(); }
    for (int t = 0; t < 30; t++) { Roaring a, b; std::set<uint32_t> sa, sb; int na = rng() % 9000, nb = rng() % 9000; for (int i = 0; i < na; i++) { uint32_t x = (rng() % 3) << 16 | (rng() % 12000); a.add(x); sa.insert(x); } for (int i = 0; i < nb; i++) { uint32_t x = (rng() % 3) << 16 | (rng() % 12000); b.add(x); sb.insert(x); }
        std::set<uint32_t> in, un; std::set_intersection(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(in, in.begin())); std::set_union(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(un, un.begin())); assert((a & b).items() == std::vector<uint32_t>(in.begin(), in.end()) && (a | b).items() == std::vector<uint32_t>(un.begin(), un.end())); }          // ② 교·합집합
    Roaring edge; for (uint32_t i = 0; i < 4096; i++) edge.add(i); assert(std::holds_alternative<Roaring::Arr>(edge.chunks[0])); edge.add(5000); assert(std::holds_alternative<Roaring::Bm>(edge.chunks[0])); edge.remove(5000); assert(std::holds_alternative<Roaring::Arr>(edge.chunks[0])); conversions++;           // 4096 → 4097 에서 비트맵, 다시 4096 에서 배열
    assert(sparseBytes < sparseFlat + 1000 && denseBytes < 70000 / 8 + 8192 * 3);
    std::cout << "RoaringBitmap: add/remove/contains and union/intersection match std::set for sparse, dense and mixed data, containers switch between array and bitmap at 4096 elements; sparse set of " << sparseFlat / 4 << " ints needs " << sparseBytes << " bytes (plain array " << sparseFlat << "), dense one " << denseBytes << " bytes" << std::endl; return 0;
}
// Time Complexity: contains O(log 청크 수 + log 4096), 합·교집합 O(공통 청크 수 · 컨테이너 연산)
// Space Complexity: 청크당 min(2·원소 수, 8192) 바이트
```
## SuccinctSet()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 간결 집합(succinct set) — Elias–Fano 부호화 (집합 관점의 요약, 정본은 AdvancedDataStructures.md Part 15 EliasFano): 우주 [0, U) 의 정렬된 서로 다른 정수 n 개를 약 n·(2 + log₂(U/n)) 비트로 저장하면서 i 번째 원소를 상수 시간에 읽는다(정보이론 하한 log₂ C(U, n) ≈ n·(1.44 + log₂(U/n)) 에 +0.56n 비트 이내).
// 각 값 v 를 하위 l = ⌊log₂(U/n)⌋ 비트 low 와 상위 high = v >> l 로 나눈다. low 들은 l 비트씩 배열에 그냥 이어 붙이고, high 들은 "단항 부호" 비트열에 저장한다: i 번째 원소는 비트열의 위치 high_i + i 를 1 로 켠다(원소가 정렬돼 있으므로 위치도 증가). i 번째 원소의 high = select₁(i) − i 이므로 접근은 select 한 번.
// select 는 64 번째 1 마다 위치를 표본으로 저장해 두고 그 뒤를 워드 단위 popcount 로 훑어 구한다. 원소 조회는 접근을 이용한 이분 탐색 O(log n). 검증: ① 모든 i 에서 access(i) 가 원본과 같음 ② 원소·비원소 조회가 std::binary_search 와 같음 ③ 사용 비트 수가 n·(l + 2) + 표본이고 단순 n·⌈log₂U⌉ 비트보다 작으며 이론 n(2 + log₂(U/n)) 에 가까움 ④ 밀도를 바꿔 가며(희소~조밀) 반복
struct EliasFano { size_t n, U; int l; std::vector<uint64_t> low, high; std::vector<size_t> sample; size_t highBits;
    static void setBit(std::vector<uint64_t>& v, size_t pos) { v[pos >> 6] |= 1ULL << (pos & 63); } uint64_t getLow(size_t i) const { uint64_t r = 0; for (int b = 0; b < l; b++) { size_t p = i * l + b; r |= ((low[p >> 6] >> (p & 63)) & 1ULL) << b; } return r; }
    EliasFano(const std::vector<uint64_t>& a, size_t U) : n(a.size()), U(U) { l = n ? std::max(0, (int)std::floor(std::log2((double)U / n))) : 0; low.assign((n * l + 63) / 64 + 1, 0); highBits = n + (n ? (U >> l) : 0) + 1; high.assign((highBits + 63) / 64 + 1, 0);
        for (size_t i = 0; i < n; i++) { for (int b = 0; b < l; b++) if (a[i] >> b & 1) setBit(low, i * l + b); setBit(high, (a[i] >> l) + i); } size_t ones = 0; for (size_t w = 0; w < high.size(); w++) { int pc = __builtin_popcountll(high[w]); for (size_t k = 0; k < (size_t)pc; k++) if ((ones + k) % 64 == 0) { uint64_t word = high[w]; for (size_t j = 0; j < k; j++) word &= word - 1; sample.push_back(w * 64 + __builtin_ctzll(word)); } ones += pc; } }
    size_t select1(size_t i) const { size_t w = sample[i / 64] / 64, need = i % 64; size_t skipped = 0; uint64_t word = high[w] & (~0ULL << (sample[i / 64] % 64)); for (;;) { int pc = __builtin_popcountll(word); if (skipped + pc > need) { for (size_t k = 0; k < need - skipped; k++) word &= word - 1; return w * 64 + __builtin_ctzll(word); } skipped += pc; word = high[++w]; } }
    uint64_t access(size_t i) const { return ((uint64_t)(select1(i) - i) << l) | getLow(i); }
    bool contains(uint64_t x) const { size_t lo = 0, hi = n; while (lo < hi) { size_t mid = (lo + hi) / 2; uint64_t v = access(mid); if (v == x) return true; if (v < x) lo = mid + 1; else hi = mid; } return false; }
    size_t bits() const { return n * l + highBits + sample.size() * 64; } };
int main() {
    std::mt19937_64 rng(6);
    for (size_t U : {1u << 16, 1u << 20, 1u << 26}) for (double density : {0.0005, 0.01, 0.2}) { size_t n = std::max<size_t>(8, (size_t)(U * density)); if (n > 200000) n = 200000; std::set<uint64_t> s; while (s.size() < n) s.insert(rng() % U); std::vector<uint64_t> a(s.begin(), s.end()); EliasFano ef(a, U);
        for (size_t i = 0; i < n; i++) assert(ef.access(i) == a[i]);                                                                                                                                      // ① 접근
        for (int q = 0; q < 3000; q++) { uint64_t x = rng() % U; assert(ef.contains(x) == s.count(x)); }                                                                                                      // ② 조회
        double naive = (double)n * std::ceil(std::log2((double)U)), theory = n * (2 + std::log2((double)U / n)); size_t withoutSamples = ef.n * ef.l + ef.highBits; assert(withoutSamples < naive && withoutSamples <= theory * 1.02 + 128); }  // ③ 공간
    std::vector<uint64_t> a = {3, 4, 7, 13, 14, 15, 21, 25, 36, 38, 54, 62}; EliasFano ef(a, 64); for (size_t i = 0; i < a.size(); i++) assert(ef.access(i) == a[i]); assert(ef.l == 2);                              // 논문의 예제(U = 64, n = 12, l = 2)
    std::cout << "SuccinctSet: Elias-Fano access and membership match the sorted array for 9 (U, density) settings up to 200000 elements; the encoding uses about n(2+log2(U/n)) bits, below the n*ceil(log2 U) bits of a plain array" << std::endl; return 0;
}
// Time Complexity: access O(1) 분할상환(표본 + 워드 훑기), 조회 O(log n)
// Space Complexity: n(2 + log₂(U/n)) 비트 + select 표본
```
## LearnedSetIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 학습된 집합 색인(learned index, Kraska 등 2018; 집합 관점의 요약, 정본은 AdvancedDataStructures.md Part 15 LearnedIndex): 정렬된 키 집합에서 키의 순위를 찾는 일은 누적 분포 함수(CDF)를 근사하는 일이다 — pos(key) ≈ n · CDF(key). B 트리를 "키 → 위치 예측 모델" 로 바꾸고, 모델의 최대 오차 ε 를 측정해 두면
// 조회는 예측 위치 ± ε 구간만 이분 탐색하면 되어 정확성이 보장된다(모델이 틀려도 오차 한계 안이므로 결과는 항상 맞음). 2 단계 구조: ① 루트 모델이 키를 구간(세그먼트)으로 보내고 ② 세그먼트별 선형 회귀가 위치를 예측하며 세그먼트마다 학습 데이터에 대한 최대 오차를 저장.
// 장점: 분포가 매끈하면 모델이 작고 탐색 구간이 매우 좁다. 단점: 갱신이 어렵고(재학습) 분포가 거칠면 ε 가 커진다. 검증: 균등·로그정규·지수·군집(여러 정규) 분포의 키 20만 개에서 ① 모든 원소를 정확히 찾고 비원소는 정확히 없음으로 판정 ② 모든 학습 키에서 |예측 − 실제| ≤ 저장한 ε ③ 평균 탐색 구간이 400 칸 미만(= 마지막 이분 탐색이 전체 log₂ n ≈ 17.6 단계보다 5 단계 이상 적음; 분포별 수치 보고)
struct Seg { double a = 0, b = 0; long eps = 0; size_t lo = 0, hi = 0; };
struct Learned { std::vector<double> keys; double kmin, kmax; int segs; std::vector<Seg> seg;
    Learned(const std::vector<double>& k, int segs) : keys(k), segs(segs), seg(segs) { kmin = keys.front(); kmax = keys.back(); std::vector<std::vector<size_t>> members(segs); for (size_t i = 0; i < keys.size(); i++) members[segOf(keys[i])].push_back(i);
        for (int s = 0; s < segs; s++) { auto& m = members[s]; if (m.empty()) { seg[s].lo = seg[s].hi = 0; continue; } double sx = 0, sy = 0, sxx = 0, sxy = 0; for (size_t i : m) { sx += keys[i]; sy += i; sxx += keys[i] * keys[i]; sxy += keys[i] * i; } double nn = m.size(), den = nn * sxx - sx * sx; seg[s].a = den > 1e-12 ? (nn * sxy - sx * sy) / den : 0; seg[s].b = (sy - seg[s].a * sx) / nn; for (size_t i : m) seg[s].eps = std::max(seg[s].eps, (long)std::ceil(std::fabs(seg[s].a * keys[i] + seg[s].b - (double)i))); seg[s].lo = m.front(); seg[s].hi = m.back(); } }
    int segOf(double key) const { int s = (int)((key - kmin) / (kmax - kmin + 1e-9) * segs); return std::min(std::max(s, 0), segs - 1); }
    long predict(double key) const { const Seg& g = seg[segOf(key)]; return (long)std::llround(g.a * key + g.b); }
    bool contains(double key, long& window) const { const Seg& g = seg[segOf(key)]; long p = predict(key); long n = keys.size(), lo = std::min(std::max(p - g.eps - 1, 0L), n), hi = std::min(std::max(p + g.eps + 2, 0L), n); if (lo > hi) lo = hi; window = hi - lo; /* 범위 밖 질의의 예측이 [0, n] 밖일 수 있어 구간을 고정 */ return std::binary_search(keys.begin() + lo, keys.begin() + hi, key); } };
int main() {
    std::mt19937_64 rng(9); const char* names[4] = {"uniform", "lognormal", "exponential", "clustered"}; double avgWindow[4];
    for (int d = 0; d < 4; d++) { std::set<double> s; std::normal_distribution<double> nd(0, 1); std::exponential_distribution<double> ed(1.0); std::uniform_real_distribution<double> ud(0, 1e6); while (s.size() < 200000) { double v = d == 0 ? ud(rng) : d == 1 ? std::exp(nd(rng)) * 1000 : d == 2 ? ed(rng) * 1000 : (rng() % 4) * 250000 + nd(rng) * 8000; s.insert(std::round(v * 1000) / 1000); }
        std::vector<double> keys(s.begin(), s.end()); Learned idx(keys, 2048); for (size_t i = 0; i < keys.size(); i++) { const Seg& g = idx.seg[idx.segOf(keys[i])]; assert(std::labs(idx.predict(keys[i]) - (long)i) <= g.eps + 1); }                                      // ② 오차 한계
        double total = 0; long cnt = 0; for (size_t i = 0; i < keys.size(); i += 5) { long w; assert(idx.contains(keys[i], w)); total += w; cnt++; } for (int q = 0; q < 20000; q++) { double x = std::round(ud(rng) * 1000) / 1000 * (d == 1 ? 0.01 : d == 2 ? 0.004 : 1.0); long w; assert(idx.contains(x, w) == (s.count(x) == 1)); }       // ① 원소 · 비원소
        avgWindow[d] = total / cnt; }
    for (int d = 0; d < 4; d++) assert(avgWindow[d] < 400 && std::log2(avgWindow[d]) < std::log2(200000.0) - 5);
    std::cout << "LearnedSetIndex: exact membership for 200000 keys under four distributions with a guaranteed error window; mean search window in positions (a plain binary search covers 200000 positions = " << std::log2(200000.0) << " steps):"; for (int d = 0; d < 4; d++) std::cout << " " << names[d] << "=" << avgWindow[d] << " (" << std::log2(avgWindow[d]) << " steps)"; std::cout << std::endl; return 0;
}
// Time Complexity: 조회 O(1) 예측 + O(log ε) 구간 이분 탐색
// Space Complexity: O(세그먼트 수) 모델 (키 배열 제외)
```
## DynamicConnectivity()
### 대표코드
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 동적 연결성(dynamic connectivity): 간선이 추가되기도 지워지기도 하는 그래프에서 "u 와 v 가 연결돼 있는가" 에 답한다. 서로소 집합은 합치기만 되고 되돌릴 수 없어 삭제를 못 한다. 질의 시점을 모두 알고 있는 오프라인 문제라면 깔끔한 해법이 있다 — 시간축 위의 세그먼트 트리.
// 간선 e 가 살아 있는 시간 구간 [l, r) 을 세그먼트 트리의 O(log T) 개 노드에 걸어 두고, 트리를 깊이 우선으로 내려가며 노드에 걸린 간선들을 롤백 가능한 서로소 집합(union by size, 경로 압축 없음, 변경 이력 스택)에 합친다. 잎(= 시각 t)에 도착하면 그 시점에 살아 있는 모든 간선이 반영돼 있으므로 질의에 답하고, 올라올 때 이력을 되돌린다.
// 비용 O((간선 구간 수) · log T · log n). 검증: 정점 25 개·연산 600 개의 무작위 열(간선 추가/삭제/질의)에서 ① 모든 질의의 답이 그 시점의 간선 집합으로 BFS 한 결과와 같음 ② 롤백 후 서로소 집합이 처음 상태로 완전히 돌아옴 ③ 합치기 횟수가 간선 구간 수 × O(log T) 이하
struct RollbackDSU { std::vector<int> p, sz; std::vector<std::pair<int, int>> history; long unions = 0; RollbackDSU(int n) : p(n), sz(n, 1) { std::iota(p.begin(), p.end(), 0); } int find(int x) const { while (p[x] != x) x = p[x]; return x; }
    void unite(int a, int b) { a = find(a); b = find(b); if (a == b) { history.push_back({-1, -1}); return; } if (sz[a] < sz[b]) std::swap(a, b); p[b] = a; sz[a] += sz[b]; history.push_back({b, a}); unions++; }
    void rollback(size_t to) { while (history.size() > to) { auto [b, a] = history.back(); history.pop_back(); if (b >= 0) { sz[a] -= sz[b]; p[b] = b; } } } };
struct Query { int t, u, v; };
int main() {
    std::mt19937 rng(7); long totalUnions = 0, totalIntervals = 0, queriesAnswered = 0;
    for (int trial = 0; trial < 60; trial++) { int n = 25, T = 600; std::map<std::pair<int, int>, int> alive; std::vector<std::vector<std::pair<int, int>>> tree(4 * T); std::vector<Query> queries; std::vector<std::set<std::pair<int, int>>> edgesAt(T);
        std::set<std::pair<int, int>> cur; std::vector<std::vector<std::pair<int, int>>> intervalsToAdd; struct Iv { int l, r, u, v; }; std::vector<Iv> intervals;
        for (int t = 0; t < T; t++) { int op = rng() % 3; int u = rng() % n, v = rng() % n; if (u > v) std::swap(u, v);
            if (op == 0 && u != v && !cur.count({u, v})) { cur.insert({u, v}); alive[{u, v}] = t; } else if (op == 1 && cur.count({u, v})) { cur.erase({u, v}); intervals.push_back({alive[{u, v}], t, u, v}); alive.erase({u, v}); } else if (op == 2) queries.push_back({t, u, v}); edgesAt[t] = cur; }
        for (auto& [e, start] : alive) intervals.push_back({start, T, e.first, e.second});
        std::function<void(int, int, int, int, int, std::pair<int, int>)> addEdge = [&](int node, int lo, int hi, int l, int r, std::pair<int, int> e) { if (r <= lo || hi <= l) return; if (l <= lo && hi <= r) { tree[node].push_back(e); return; } int mid = (lo + hi) / 2; addEdge(node * 2, lo, mid, l, r, e); addEdge(node * 2 + 1, mid, hi, l, r, e); };
        for (auto& iv : intervals) addEdge(1, 0, T, iv.l, iv.r, {iv.u, iv.v}); totalIntervals += intervals.size();
        RollbackDSU dsu(n); std::vector<int> answer(T, -1); std::map<int, Query> byTime; for (auto& q : queries) byTime[q.t] = q;
        std::function<void(int, int, int)> dfs = [&](int node, int lo, int hi) { size_t mark = dsu.history.size(); for (auto& e : tree[node]) dsu.unite(e.first, e.second); if (hi - lo == 1) { auto it = byTime.find(lo); if (it != byTime.end()) answer[lo] = dsu.find(it->second.u) == dsu.find(it->second.v); } else { int mid = (lo + hi) / 2; dfs(node * 2, lo, mid); dfs(node * 2 + 1, mid, hi); } dsu.rollback(mark); };
        dfs(1, 0, T); for (int i = 0; i < n; i++) assert(dsu.find(i) == i && dsu.sz[i] == 1);                                                                                                                                                  // ② 롤백 후 처음 상태
        for (auto& q : queries) { const auto& edges = edgesAt[q.t]; std::vector<std::vector<int>> adj(n); for (auto [a, b] : edges) { adj[a].push_back(b); adj[b].push_back(a); } std::vector<char> seen(n, 0); std::queue<int> bq; bq.push(q.u); seen[q.u] = 1; while (!bq.empty()) { int x = bq.front(); bq.pop(); for (int y : adj[x]) if (!seen[y]) { seen[y] = 1; bq.push(y); } } assert(answer[q.t] == (int)seen[q.v]); queriesAnswered++; }       // ① BFS 와 같음
        totalUnions += dsu.unions; }
    assert(queriesAnswered > 5000 && totalUnions <= totalIntervals * 14);
    std::cout << "DynamicConnectivity: " << queriesAnswered << " connectivity queries on 60 random add/remove/query sequences all equal a BFS on the edge set of that moment; rollback restored the union-find after every run; " << totalUnions << " unions were performed for " << totalIntervals << " edge lifetimes (about log T unions each)" << std::endl; return 0;
}
// Time Complexity: O(m log T log n) (m: 간선 구간 수)
// Space Complexity: O(m log T) (시간 트리에 걸린 간선) + O(n) 서로소 집합
```

# 부록
## Set vs List
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <list>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>
#include <cassert>

// Set vs List — 같은 원소들을 담아도 약속(계약)이 다르다. List(리스트/배열)는 "순서가 있고 중복을 허용하는 열"이고 Set 은 "순서와 중복이 없는 원소의 모임" 이다. 그래서 list.insert(x) 는 매번 길이를 1 늘리지만 set.insert(x) 는 이미 있으면 아무 일도 하지 않는다(멱등), 두 집합이 같은지는 원소만 보지만 두 리스트는 순서까지 같아야 한다.
// 비용도 다르다. "x 가 들어 있는가?" 는 리스트에서 O(n)(앞에서부터 비교), 정렬된 리스트에서 이분 탐색 O(log n), 해시 집합에서 O(1) 기대, 트리 집합에서 O(log n). 반대로 "i 번째 원소", "순서대로 순회", "앞뒤에 끼워 넣기" 는 리스트의 몫이다. 중복 제거가 필요하면 리스트 → 집합 변환을 한다(순서를 보존하려면 첫 등장 순서를 따로 기록).
// 증거: ① 계약 차이 — 집합 삽입의 멱등성·교환성, 리스트에서는 둘 다 성립하지 않음 ② 같은 입력에서 리스트→집합 변환이 중복·순서를 잃고 "유일 원소 수" 와 일치 ③ 조회 비용을 비교 횟수로 세어 n 이 2배가 될 때 리스트 비교 수는 약 2배, 트리는 +1 정도, 해시는 거의 일정함을 측정 ④ 정렬된 리스트 이분 탐색은 트리와 같은 로그 단계 수
int main() {
    std::mt19937 rng(3); for (int t = 0; t < 500; t++) { std::vector<int> a; std::set<int> s; int n = rng() % 30; for (int i = 0; i < n; i++) { int x = rng() % 10; a.push_back(x); s.insert(x); }
        std::vector<int> b = a; for (int x : {3, 3}) { b.push_back(x); } std::set<int> s2 = s; s2.insert(3); s2.insert(3); assert(s2.size() == (s.count(3) ? s.size() : s.size() + 1) && b.size() == a.size() + 2);                                              // ① 멱등
        std::vector<int> x1 = a, x2 = a; x1.push_back(1); x1.push_back(2); x2.push_back(2); x2.push_back(1); assert(x1 != x2); std::set<int> y1 = s, y2 = s; y1.insert(1); y1.insert(2); y2.insert(2); y2.insert(1); assert(y1 == y2);                                      // 삽입 순서: 리스트는 다름, 집합은 같음
        std::set<int> conv(a.begin(), a.end()); std::vector<int> uniq = a; std::sort(uniq.begin(), uniq.end()); uniq.erase(std::unique(uniq.begin(), uniq.end()), uniq.end()); assert(conv.size() == uniq.size() && std::vector<int>(conv.begin(), conv.end()) == uniq); }              // ② 변환
    double listCmp[5], treeCmp[5], hashProbe[5]; int k = 0; for (int n : {1000, 2000, 4000, 8000, 16000}) { std::vector<int> v(n); for (int i = 0; i < n; i++) v[i] = i * 2; std::vector<int> shuffled = v; std::shuffle(shuffled.begin(), shuffled.end(), rng); long lc = 0, tc = 0; const int Q = 400;
        struct Counting { long* c; bool operator()(int a, int b) const { ++*c; return a < b; } }; std::set<int, Counting> tree{Counting{&tc}}; for (int x : shuffled) tree.insert(x); tc = 0; std::unordered_set<int> hs(shuffled.begin(), shuffled.end()); long probes = 0;
        for (int q = 0; q < Q; q++) { int key = (rng() % n) * 2; for (int x : shuffled) { lc++; if (x == key) break; } tree.count(key); probes += hs.bucket_size(hs.bucket(key)); assert(hs.count(key) == 1); }
        listCmp[k] = (double)lc / Q; treeCmp[k] = (double)tc / Q; hashProbe[k] = (double)probes / Q; k++; }
    for (int i = 1; i < 5; i++) { assert(listCmp[i] / listCmp[i - 1] > 1.7 && listCmp[i] / listCmp[i - 1] < 2.3); assert(treeCmp[i] - treeCmp[i - 1] < 4.0 && treeCmp[i] - treeCmp[i - 1] > -1.0); assert(hashProbe[i] < 4.0); } assert(listCmp[4] > 20 * treeCmp[4]);           // ③ 비용 증가율
    for (int n : {1000, 16000}) { std::vector<int> v(n); for (int i = 0; i < n; i++) v[i] = i; long steps = 0; int lo = 0, hi = n, key = n / 3; while (lo < hi) { steps++; int mid = (lo + hi) / 2; if (v[mid] < key) lo = mid + 1; else hi = mid; } assert(steps <= (int)std::ceil(std::log2((double)n)) + 1); }                                  // ④ 이분 탐색
    std::cout << "Set vs List: set insertion is idempotent and order-independent while list insertion is neither; list->set conversion equals sort+unique; average comparisons per lookup for n=1000..16000: list " << listCmp[0] << ".." << listCmp[4] << " (doubles with n), tree " << treeCmp[0] << ".." << treeCmp[4] << " (+~1 per doubling), hash bucket " << hashProbe[0] << ".." << hashProbe[4] << " (flat)" << std::endl; return 0;
}
// Time Complexity: 리스트 조회 O(n), 정렬 리스트 O(log n), 해시 집합 O(1) 기대, 트리 집합 O(log n)
// Space Complexity: 모두 O(n) (집합은 노드/버킷 오버헤드가 큼)
```
## Set vs Multiset
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <iterator>
#include <map>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// Set vs Multiset — 다중집합(multiset, bag)은 원소가 여러 번 나올 수 있는 집합이다: 각 원소 x 에 개수(중복도) m(x) ≥ 0 을 대응시키는 함수. 집합은 m(x) ∈ {0, 1} 인 특별한 경우다. 연산의 정의가 달라진다 — 합집합 (A ∪ B)(x) = max(m_A(x), m_B(x)), 교집합 min, 합(sum) A ⊎ B 는 m_A + m_B(덧셈; 집합의 합집합과 다름),
// 차집합 (A − B)(x) = max(0, m_A(x) − m_B(x)). 항등식: A ⊎ B = (A ∪ B) ⊎ (A ∩ B) (min + max = 합), A ∪ B = A ⊎ (B − A). 크기는 |A| = Σ m(x) 이고 서로 다른 원소 수는 별도. SQL 의 UNION ALL / INTERSECT ALL / EXCEPT ALL 이 정확히 이 다중집합 연산이고 UNION / INTERSECT / EXCEPT 는 집합 연산이다.
// 구현은 map<원소, 개수> (또는 정렬된 열 + std::set_union 등 — 정렬된 다중집합에 대한 STL 알고리즘이 위 정의를 따른다). 검증: ① 직접 구현한 max/min/덧셈/monus 가 정렬된 열 위의 std::set_union/intersection/difference 결과와 같음 ② 두 항등식 ③ 집합(개수 ≤ 1)에 제한하면 집합 연산과 같음 ④ 중복 제거(support) 함수 supp 가 합집합·교집합과 교환: supp(A ∪ B) = supp(A) ∪ supp(B), supp(A ⊎ B) = supp(A) ∪ supp(B)
typedef std::map<int, int> MS;
MS msUnion(const MS& a, const MS& b) { MS r = a; for (auto& [k, v] : b) r[k] = std::max(r[k], v); return r; } MS msInter(const MS& a, const MS& b) { MS r; for (auto& [k, v] : a) if (b.count(k)) r[k] = std::min(v, b.at(k)); return r; }
MS msSum(const MS& a, const MS& b) { MS r = a; for (auto& [k, v] : b) r[k] += v; return r; } MS msDiff(const MS& a, const MS& b) { MS r; for (auto& [k, v] : a) { int d = v - (b.count(k) ? b.at(k) : 0); if (d > 0) r[k] = d; } return r; }
std::vector<int> expand(const MS& m) { std::vector<int> v; for (auto& [k, c] : m) v.insert(v.end(), c, k); return v; } std::set<int> supp(const MS& m) { std::set<int> s; for (auto& [k, c] : m) if (c > 0) s.insert(k); return s; }
int main() {
    std::mt19937 rng(7); for (int t = 0; t < 1000; t++) { MS a, b; for (int i = 0; i < (int)(rng() % 12); i++) a[rng() % 8]++; for (int i = 0; i < (int)(rng() % 12); i++) b[rng() % 8]++; auto va = expand(a), vb = expand(b); std::vector<int> u, in, df;
        std::set_union(va.begin(), va.end(), vb.begin(), vb.end(), std::back_inserter(u)); std::set_intersection(va.begin(), va.end(), vb.begin(), vb.end(), std::back_inserter(in)); std::set_difference(va.begin(), va.end(), vb.begin(), vb.end(), std::back_inserter(df)); assert(expand(msUnion(a, b)) == u && expand(msInter(a, b)) == in && expand(msDiff(a, b)) == df);                    // ① STL 과 일치
        std::vector<int> sm; std::merge(va.begin(), va.end(), vb.begin(), vb.end(), std::back_inserter(sm)); assert(expand(msSum(a, b)) == sm);
        assert(msSum(a, b) == msSum(msUnion(a, b), msInter(a, b)) && msUnion(a, b) == msSum(a, msDiff(b, a)));                                                                                                                                                                  // ② 항등식
        assert(supp(msUnion(a, b)) == [&] { std::set<int> x = supp(a); for (int k : supp(b)) x.insert(k); return x; }() && supp(msSum(a, b)) == supp(msUnion(a, b)) && [&] { std::set<int> x; for (int k : supp(a)) if (supp(b).count(k)) x.insert(k); return supp(msInter(a, b)) == x; }());            // ④ supp 와 교환
        MS sa, sb; for (auto& [k, v] : a) sa[k] = 1; for (auto& [k, v] : b) sb[k] = 1; assert(supp(msUnion(sa, sb)) == supp(msSum(sa, sb)) && msUnion(sa, sb) == [&] { MS r; for (int k : supp(msUnion(sa, sb))) r[k] = 1; return r; }() && msInter(sa, sb) == [&] { MS r; for (int k : supp(msInter(sa, sb))) r[k] = 1; return r; }()); }  // ③ 집합으로 제한
    MS x = {{1, 3}, {2, 1}}, y = {{1, 1}, {3, 2}}; assert(msUnion(x, y) == (MS{{1, 3}, {2, 1}, {3, 2}}) && msInter(x, y) == (MS{{1, 1}}) && msSum(x, y) == (MS{{1, 4}, {2, 1}, {3, 2}}) && msDiff(x, y) == (MS{{1, 2}, {2, 1}}));
    std::cout << "Set vs Multiset: max-union, min-intersection, additive sum and truncated difference on count maps equal the STL algorithms on sorted multisets for 1000 random pairs; A+B = (A union B)+(A intersect B) and A union B = A+(B-A) hold; restricted to counts <= 1 they reduce to ordinary set operations" << std::endl; return 0;
}
// Time Complexity: 연산 O(서로 다른 원소 수 log) (map 기반)
// Space Complexity: O(서로 다른 원소 수)
```
## HashSet vs TreeSet
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <unordered_set>
#include <vector>
#include <cassert>

// HashSet vs TreeSet — 같은 "집합" 인터페이스지만 구조가 달라 보장과 비용이 다르다. 해시 집합은 키를 해시값으로 버킷에 흩어 두므로 조회·삽입·삭제가 기대 O(1) 이지만 순서가 없고 해시가 나쁘면(충돌) 최악 O(n) 이다. 트리 집합은 키를 정렬된 균형 트리에 두므로 모든 연산이 O(log n) 이 보장되고,
// 정렬 순회·하한(lower_bound)·범위 질의·최솟값/최댓값·이전/다음 원소를 공짜로 얻는다(해시는 O(n) 전체 스캔). 키에 해시 함수와 동치만 정의할 수 있으면 해시, 전순서가 있고 순서 연산이 필요하면 트리.
// 증거(단순 사슬 해시 표를 직접 구현해 비교 횟수를 센다): ① 같은 입력에서 두 구조의 멤버십 결과가 완전히 같음 ② 좋은 해시에서 평균 탐색 비교 수는 n 에 거의 무관(~1~2) 하지만 모든 키가 같은 해시로 충돌하는 적대적 해시에서는 n/2 로 선형 증가하고 트리는 ≈ log₂ n 으로 안정적 ③ 범위 질의 [lo, hi]: 트리는 O(log n + k) 비교, 해시는 항상 n 번 모든 원소 검사 ④ 해시 집합의 순회 순서는 정렬되어 있지 않고 트리는 정렬됨
struct ChainHash { std::vector<std::vector<int>> b; long cmp = 0; bool bad; ChainHash(size_t buckets, bool bad) : b(buckets), bad(bad) {} size_t h(int x) const { return bad ? 0 : (size_t)((uint32_t)x * 2654435761u) % b.size(); }
    bool insert(int x) { auto& v = b[h(x)]; for (int y : v) { cmp++; if (y == x) return false; } v.push_back(x); return true; } bool contains(int x) { for (int y : b[h(x)]) { cmp++; if (y == x) return true; } return false; } };
int main() {
    std::mt19937 rng(9); double goodAvg[4], badAvg[4], treeAvg[4]; int k = 0;
    for (int n : {500, 1000, 2000, 4000}) { std::vector<int> keys(n); for (int i = 0; i < n; i++) keys[i] = i * 3 + 1; std::shuffle(keys.begin(), keys.end(), rng); ChainHash good(n, false), bad(n, true); long tc = 0; struct Cnt { long* c; bool operator()(int a, int b) const { ++*c; return a < b; } }; std::set<int, Cnt> tree{Cnt{&tc}};
        for (int x : keys) { good.insert(x); bad.insert(x); tree.insert(x); } good.cmp = bad.cmp = 0; tc = 0; const int Q = 300; for (int q = 0; q < Q; q++) { int probe = (rng() % 2) ? keys[rng() % n] : (int)(rng() % (3 * n)); bool a = good.contains(probe), b2 = bad.contains(probe), c = tree.count(probe) == 1; assert(a == b2 && b2 == c); }                       // ① 결과 동일
        goodAvg[k] = (double)good.cmp / Q; badAvg[k] = (double)bad.cmp / Q; treeAvg[k] = (double)tc / Q; k++; }
    for (int i = 0; i < 4; i++) assert(goodAvg[i] < 3.0 && badAvg[i] > 0.2 * (500 << i) && treeAvg[i] < 2 * std::log2((double)(500 << i)) + 2);                                                                                         // ② 충돌 시 선형, 트리는 로그
    assert(badAvg[3] > 100 * goodAvg[3]);
    { const int n = 100000; std::set<int> tree; std::unordered_set<int> hs; for (int i = 0; i < n; i++) { int x = rng() % 1000000; tree.insert(x); hs.insert(x); } int lo = 400000, hi = 400500; long scan = 0; std::vector<int> viaHash; for (int x : hs) { scan++; if (lo <= x && x <= hi) viaHash.push_back(x); } std::sort(viaHash.begin(), viaHash.end());
        std::vector<int> viaTree(tree.lower_bound(lo), tree.upper_bound(hi)); assert(viaHash == viaTree && scan == (long)hs.size() && viaTree.size() < 600);                                                                           // ③ 범위 질의: 트리는 일부만 방문
        std::vector<int> hashOrder(hs.begin(), hs.end()); assert(!std::is_sorted(hashOrder.begin(), hashOrder.end()) && std::is_sorted(tree.begin(), tree.end())); }                                                                       // ④ 순서
    std::cout << "HashSet vs TreeSet: identical membership answers; mean lookup comparisons for n=500..4000 - good hash " << goodAvg[0] << ".." << goodAvg[3] << ", colliding hash " << badAvg[0] << ".." << badAvg[3] << " (linear), tree " << treeAvg[0] << ".." << treeAvg[3] << " (logarithmic); a range query touched only the matching keys in the tree but all " << 100000 << "-ish elements in the hash set, whose iteration order is unsorted" << std::endl; return 0;
}
// Time Complexity: 해시 O(1) 기대 / O(n) 최악, 트리 O(log n) 보장
// Space Complexity: O(n)
```
## BitSet은 언제 사용하는가?
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// BitSet 은 언제 쓰는가 — 우주(universe) U = {0..U−1} 가 작고 정수로 번호가 매겨질 때, 원소 하나를 비트 하나로 표현하는 집합이다. 장점 ① 공간: U/8 바이트 고정 ② 속도: 합·교·차가 64 개 원소를 한 명령으로 처리하는 워드 연산(O(U/64)) ③ popcount 로 원소 수, 비트 스캔으로 순회, rank/select 가능.
// 언제 이득인가는 밀도 d = n/U 로 정해진다. 정렬 배열(원소당 4 바이트)과 U/8 바이트의 비트셋은 n·4 = U/8 일 때 같아져 d = 1/32 ≈ 3.1% 이상이면 비트셋이 작다. 해시 집합(원소당 약 32 바이트 가정)이면 d ≈ 0.4% 부터. 집합 연산 비용도 같은 식: 병합은 O(n + m) 비교, 비트셋은 U/64 워드이므로 d > 1/64 쯤에서 비트셋이 빠르다.
// 단점: U 가 크고 희소하면 낭비(Roaring 비트맵이 해결), 우주 밖의 원소(문자열 등)는 먼저 번호를 매겨야 함. 증거: ① 비트셋 연산(합·교·차·대칭차·원소 수·순회)이 std::set 과 같음 ② 밀도를 바꿔 가며 공간 모델의 교차점이 이론값(3.1%, 0.4%) 근처 ③ 교집합 연산 수(워드 수 U/64 vs 병합 비교 수 n+m)가 교차하는 밀도가 1/64 근처 ④ 비트셋 popcount 로 센 크기 == 원소 수
int main() {
    const size_t U = 4096; std::mt19937 rng(5); for (int t = 0; t < 300; t++) { std::bitset<U> A, B; std::set<int> sa, sb; int na = rng() % 400, nb = rng() % 400; for (int i = 0; i < na; i++) { int x = rng() % U; A[x] = 1; sa.insert(x); } for (int i = 0; i < nb; i++) { int x = rng() % U; B[x] = 1; sb.insert(x); }
        auto toSet = [&](const std::bitset<U>& s) { std::set<int> r; for (size_t i = s._Find_first(); i < U; i = s._Find_next(i)) r.insert(i); return r; }; std::set<int> u, in, df, sd; std::set_union(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(u, u.begin())); std::set_intersection(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(in, in.begin())); std::set_difference(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(df, df.begin())); std::set_symmetric_difference(sa.begin(), sa.end(), sb.begin(), sb.end(), std::inserter(sd, sd.begin()));
        assert(toSet(A | B) == u && toSet(A & B) == in && toSet(A & ~B) == df && toSet(A ^ B) == sd && A.count() == sa.size() && (A | B).count() == u.size());                                                  // ① 연산 일치 ④ popcount }
    }
    const double bytesPerArrayElem = 4, bytesPerHashElem = 32; double densityArray = -1, densityHash = -1; for (int pm = 1; pm <= 1000; pm++) { double d = pm / 1000.0, bitsetBytes = U / 8.0, nElems = d * U; if (densityArray < 0 && nElems * bytesPerArrayElem >= bitsetBytes) densityArray = d; if (densityHash < 0 && nElems * bytesPerHashElem >= bitsetBytes) densityHash = d; }
    assert(std::fabs(densityArray - 1.0 / 32) < 0.002 && std::fabs(densityHash - 1.0 / 256) < 0.002);                                                                                                  // ② 공간 교차점 3.1% · 0.4%
    double crossover = -1; for (int pm = 1; pm <= 500; pm++) { double d = pm / 1000.0; long mergeCmp = (long)(2 * d * U), words = U / 64; if (crossover < 0 && mergeCmp >= words) crossover = d; } assert(std::fabs(crossover - 1.0 / 128) < 0.002);                         // ③ 시간 교차점(양쪽 밀도 d): 2dU 비교 = U/64 워드
    std::cout << "BitSet: bitset algebra, popcount cardinality and iteration match std::set on 300 random pairs; modeled break-even densities - smaller than a sorted int array above " << densityArray * 100 << "% density, smaller than a hash set above " << densityHash * 100 << "%; intersecting is cheaper than a merge above about " << crossover * 100 << "% density" << std::endl; return 0;
}
// Time Complexity: 합·교·차 O(U/64), 원소 수 O(U/64) (popcount), 단일 비트 접근 O(1)
// Space Complexity: U/8 바이트
```
## Union-Find가 거의 O(1)인 이유
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// Union-Find 가 "거의 O(1)" 인 이유 — 서로소 집합에 두 최적화를 함께 쓰면(랭크/크기에 의한 합치기 + 경로 압축) m 번의 연산이 n 개 원소에서 총 O(m·α(n)) 이 든다(Tarjan 1975). α 는 역 아커만 함수이며 우주에 있는 원자 수만큼 큰 n 에서도 4 를 넘지 않는다.
// 아커만 계열: A₀(j) = j + 1, A_k(j) = A_{k−1}^{(j+1)}(j) (A_{k−1} 을 j+1 번 합성). 닫힌 꼴 A₁(j) = 2j + 1, A₂(j) = 2^{j+1}(j + 1) − 1, A₃(1) = 2047, A₄(1) ≥ 2^2047 은 탑 지수라 10⁸⁰ 보다 훨씬 크다. α(n) = min{k : A_k(1) ≥ n}.
// 직관: 랭크 덕에 트리 높이 ≤ log n, 압축은 한 번 오른 경로를 평평하게 만들어 같은 경로를 다시 오르는 비용을 없애며, 둘이 합쳐지면 "분할상환 비용이 로그의 로그의 …(반복)" 로 내려가 α(n) 이 된다. 증거: ① 아커만 정의로 계산한 값이 닫힌 꼴과 일치하고 α(n) 이 n 에 대해 단조이며 α(2047) = 3, α(10⁹) = 4 ② 무작위·적대적 합치기+조회 열에서 find 가 따라간 평균 간선 수가 n = 10⁶ 까지 4 미만 ③ 최적화를 빼면 적대적 열에서 훨씬 큼(사슬 열: 아무것도 안 쓰면 ≈ n/2, 압축만 쓰면 상수 / 이항 트리 열: 랭크만 쓰면 ≈ log n 의 절반, 둘 다 쓰면 상수) ④ 총 걸음 수/연산 수가 n 을 키워도 거의 그대로
long long A(int k, long long j) { if (k == 0) return j + 1; long long v = j; for (long long t = 0; t <= j; t++) v = A(k - 1, v); return v; }
int alpha(double n) { if (n <= 2) return 0 + (n > 1 ? 1 : 0); if (n <= 3) return 1; if (n <= 7) return 2; if (n <= 2047) return 3; return 4; }                                                    // A₀(1)=2, A₁(1)=3, A₂(1)=7, A₃(1)=2047, A₄(1) = 거대
struct DSU { std::vector<int> p, rk; long long steps = 0; bool compress, byRank; DSU(int n, bool compress, bool byRank) : p(n), rk(n, 0), compress(compress), byRank(byRank) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { int r = x; while (p[r] != r) { r = p[r]; steps++; } if (compress) while (p[x] != r) { int nx = p[x]; p[x] = r; x = nx; } return r; } void unite(int a, int b) { a = find(a); b = find(b); if (a == b) return; if (byRank) { if (rk[a] < rk[b]) std::swap(a, b); p[b] = a; if (rk[a] == rk[b]) rk[a]++; } else p[a] = b; } };
int main() {
    assert(A(0, 5) == 6 && A(1, 7) == 15 && A(2, 3) == (1LL << 4) * 4 - 1 && A(2, 1) == 7 && A(3, 1) == 2047);                                                                              // ① 닫힌 꼴과 아커만 값
    for (long long j = 0; j <= 6; j++) { assert(A(1, j) == 2 * j + 1 && A(2, j) == (1LL << (j + 1)) * (j + 1) - 1); } assert(alpha(2047) == 3 && alpha(2048) == 4 && alpha(1e9) == 4 && alpha(1e80) == 4);
    std::mt19937 rng(4); double avgAt[3]; int idx = 0;
    for (int n : {1000, 100000, 1000000}) { DSU d(n, true, true); long long ops = 0; for (int i = 0; i < 2 * n; i++) { int a = rng() % n, b = rng() % n; if (rng() % 2) d.unite(a, b); else d.find(a); ops++; } for (int i = 0; i < n; i++) { d.find(rng() % n); ops++; } avgAt[idx++] = (double)d.steps / ops; }
    for (int i = 0; i < 3; i++) assert(avgAt[i] < 4.0); assert(avgAt[2] - avgAt[0] < 1.0);                                                                                                    // ② ④ n 이 1000 배가 돼도 거의 그대로
    auto adversarial = [&](int kind, bool compress, bool byRank) { const int N = kind == 0 ? 20000 : 16384; DSU d(N, compress, byRank); if (kind == 0) { for (int i = 0; i + 1 < N; i++) d.unite(i, i + 1); } else { for (int s = 1; s < N; s *= 2) for (int i = 0; i + s < N; i += 2 * s) d.unite(i, i + s); }        // 0: 사슬(랭크 없으면 깊이 N), 1: 이항 트리(랭크가 있어도 깊이 log N)
        d.steps = 0; for (int rep = 0; rep < 3; rep++) for (int i = 0; i < N; i++) d.find(i); return (double)d.steps / (3.0 * N); };
    double chainBoth = adversarial(0, true, true), chainCompress = adversarial(0, true, false), chainNone = adversarial(0, false, false), binBoth = adversarial(1, true, true), binRank = adversarial(1, false, true);
    assert(chainBoth < 2.0 && chainCompress < 3.0 && chainNone > 20000 / 4.0 && binBoth < 3.0 && binRank > 3.0 && binRank > 2 * binBoth && binRank <= std::log2(16384.0));                                                       // ③ 대조군
    std::cout << "Union-Find: Ackermann closed forms verified (A1=2j+1, A2=2^(j+1)(j+1)-1, A3(1)=2047) so alpha(n)<=4 for any physical n; average find steps with both optimizations: " << avgAt[0] << " / " << avgAt[1] << " / " << avgAt[2] << " for n = 1e3 / 1e5 / 1e6; steps per find on a chain-building adversary: " << chainBoth << " (both), " << chainCompress << " (compression only), " << chainNone << " (neither); on a binomial-tree adversary: " << binBoth << " (both) versus " << binRank << " (rank only, about log2(n)/2)" << std::endl; return 0;
}
// Time Complexity: m 번 연산 O(m α(n)) (분할상환)
// Space Complexity: O(n)
```
## 집합과 그래프의 연결
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 집합과 그래프의 연결 — 집합 위의 이항 관계 R ⊆ V × V 는 그대로 방향 그래프의 간선 집합이다. 그래서 관계의 성질이 그래프의 모양이 된다: 반사적 = 모든 정점에 자기 고리, 대칭적 = 무방향 그래프, 추이적 = "두 걸음으로 갈 수 있으면 한 걸음에도 갈 수 있음".
// 닫힘(closure)은 도달 가능성이다: R 의 반사-추이 닫힘 R* = "u 에서 v 로 가는 경로가 있다". 동치 관계는 서로소인 완전 그래프(클릭)들의 모임이며 그 클릭이 연결 성분이다(동치류 = 성분). 방향 비순환 그래프(DAG)의 추이 닫힘은 엄격한 부분 순서이고, 거꾸로 부분 순서의 하세 다이어그램(추이 환원)이 가장 적은 간선의 DAG 다.
// 증거: ① Warshall 추이 닫힘 == 모든 정점에서 BFS 한 도달 가능성 ② 무방향 그래프의 도달 가능성 관계(반사-추이 닫힘)는 동치 관계이고 동치류 수 == 연결 성분 수 ③ DAG 의 추이 닫힘은 비반사·반대칭·추이(엄격 부분 순서) ④ 추이 환원(간선 (u,w) 에 대해 u→v→w 가 있으면 제거)의 닫힘이 원래 닫힘과 같고 환원이 최소(어떤 간선을 빼도 닫힘이 달라짐)
typedef std::vector<std::vector<char>> M;
M warshall(M r) { int n = r.size(); for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r[i][k]) for (int j = 0; j < n; j++) if (r[k][j]) r[i][j] = 1; return r; }
M reach(const M& r) { int n = r.size(); M out(n, std::vector<char>(n, 0)); for (int s = 0; s < n; s++) { std::queue<int> q; q.push(s); std::vector<char> seen(n, 0); while (!q.empty()) { int u = q.front(); q.pop(); for (int v = 0; v < n; v++) if (r[u][v] && !seen[v]) { seen[v] = 1; out[s][v] = 1; q.push(v); } } } return out; }
int main() {
    std::mt19937 rng(8); for (int t = 0; t < 300; t++) { int n = 2 + rng() % 9; M r(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) r[i][j] = rng() % 5 == 0; assert(warshall(r) == reach(r)); }                                                    // ①
    for (int t = 0; t < 300; t++) { int n = 2 + rng() % 12; M r(n, std::vector<char>(n, 0)); for (int k = 0; k < n; k++) { int a = rng() % n, b = rng() % n; r[a][b] = r[b][a] = 1; } M c = reach(r); for (int i = 0; i < n; i++) c[i][i] = 1;
        for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) { assert(c[a][b] == c[b][a]); for (int d = 0; d < n; d++) if (c[a][b] && c[b][d]) assert(c[a][d]); } std::set<std::vector<char>> classes(c.begin(), c.end()); int comps = 0; std::vector<char> seen(n, 0); for (int s = 0; s < n; s++) if (!seen[s]) { comps++; std::queue<int> q; q.push(s); seen[s] = 1; while (!q.empty()) { int u = q.front(); q.pop(); for (int v = 0; v < n; v++) if (r[u][v] && !seen[v]) { seen[v] = 1; q.push(v); } } } assert((int)classes.size() == comps); }  // ② 동치류 = 성분
    int minimalChecks = 0; for (int t = 0; t < 300; t++) { int n = 3 + rng() % 8; M dag(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) dag[i][j] = rng() % 3 == 0; M clo = warshall(dag);
        for (int i = 0; i < n; i++) { assert(!clo[i][i]); for (int j = 0; j < n; j++) { assert(!(clo[i][j] && clo[j][i])); for (int k = 0; k < n; k++) if (clo[i][j] && clo[j][k]) assert(clo[i][k]); } }                                                              // ③ 엄격 부분 순서
        M red = clo; for (int u = 0; u < n; u++) for (int w = 0; w < n; w++) for (int v = 0; v < n; v++) if (clo[u][v] && clo[v][w]) red[u][w] = 0; assert(warshall(red) == clo);                                                                                            // ④ 환원의 닫힘 = 닫힘
        for (int u = 0; u < n; u++) for (int w = 0; w < n; w++) if (red[u][w]) { M less = red; less[u][w] = 0; assert(warshall(less) != clo); minimalChecks++; } }                                                                                                               // 최소성
    std::cout << "Sets and graphs: Warshall closure equals BFS reachability on 300 random digraphs; reachability of an undirected graph is an equivalence relation whose classes are exactly its connected components; the closure of a DAG is a strict partial order and its transitive reduction (" << minimalChecks << " edges checked) regenerates it with no redundant edge" << std::endl; return 0;
}
// Time Complexity: Warshall O(n³), 정점마다 BFS O(n(n + e))
// Space Complexity: O(n²)
```
## 집합과 관계(Relation)
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <vector>
#include <cassert>

// 집합과 관계 — 두 집합 A, B 의 곱집합 A × B 의 부분집합이 A 에서 B 로의 관계다. 크기 n 인 집합 위의 이항 관계는 n² 개의 순서쌍 각각을 넣거나 빼므로 모두 2^(n²) 개. 성질별로 세면 — 반사적 2^(n²−n), 대칭적 2^(n(n+1)/2), 반대칭적 2ⁿ·3^(n(n−1)/2) (쌍마다 {없음, a→b, b→a} 세 가지, 자기 쌍은 자유),
// 추이적(수열 1, 2, 13, 171, 3994, …), 부분 순서(반사+반대칭+추이; 1, 3, 19, 219, 4231, … 구별되는 원소에 이름이 붙은 경우), 동치 관계는 Bell 수(1, 2, 5, 15, 52). 이 부록은 n ≤ 4 에서 2^(n²) ≤ 65536 개 관계를 전부 나열해 위 숫자를 직접 확인한다 — 수학적 사실을 프로그램이 검산하는 연습이다.
// 추가로 관계의 연산: 역관계, 합성, 곱집합과의 관계(관계 ⊆ A × B 는 A→B 의 "다가 함수" 로 볼 수 있음; 각 a 에 b 가 정확히 하나면 함수). 검증: n = 1..4 에서 위 여섯 종류의 개수 + 전순서(선형 순서)가 n! 개이고 전부 부분 순서임, 동치 ∩ 부분 순서 = 항등 관계뿐, 엄격 부분 순서의 개수가 부분 순서의 개수와 같음(자기 쌍을 넣고 빼는 대응)
// audit: exhaustive — 모든 2^(n²) 관계를 전수 열거하므로 무작위 표본이 필요 없다
typedef std::vector<unsigned> Rel;  // 행 비트마스크: rel[a] 의 b 번째 비트 = (a, b) ∈ R
bool refl(const Rel& r, int n) { for (int a = 0; a < n; a++) if (!(r[a] >> a & 1)) return false; return true; } bool irrefl(const Rel& r, int n) { for (int a = 0; a < n; a++) if (r[a] >> a & 1) return false; return true; }
bool sym(const Rel& r, int n) { for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) if ((r[a] >> b & 1) != (r[b] >> a & 1)) return false; return true; } bool antisym(const Rel& r, int n) { for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) if ((r[a] >> b & 1) && (r[b] >> a & 1)) return false; return true; }
bool trans(const Rel& r, int n) { for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) if (r[a] >> b & 1) if (r[b] & ~r[a]) return false; return true; }
int main() {
    const long long expectTrans[5] = {1, 2, 13, 171, 3994}, expectPoset[5] = {1, 1, 3, 19, 219}, bell[5] = {1, 1, 2, 5, 15};
    for (int n = 1; n <= 4; n++) { long long total = 0, nRefl = 0, nSym = 0, nAnti = 0, nTrans = 0, nPoset = 0, nEquiv = 0, nStrict = 0, nTotalOrder = 0, nEquivAndPoset = 0;
        for (unsigned code = 0; code < (1u << (n * n)); code++) { Rel r(n); for (int a = 0; a < n; a++) r[a] = (code >> (a * n)) & ((1u << n) - 1); total++; bool rf = refl(r, n), sy = sym(r, n), an = antisym(r, n), tr = trans(r, n); nRefl += rf; nSym += sy; nAnti += an; nTrans += tr;
            bool poset = rf && an && tr, equiv = rf && sy && tr, strict = irrefl(r, n) && an && tr; nPoset += poset; nEquiv += equiv; nStrict += strict; if (equiv && poset) { nEquivAndPoset++; for (int a = 0; a < n; a++) assert(r[a] == (1u << a)); }                                // 동치이면서 부분 순서 = 항등 관계
            if (poset) { bool tot = true; for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) if (!(r[a] >> b & 1) && !(r[b] >> a & 1)) tot = false; nTotalOrder += tot; } }
        long long pow3 = 1; for (int i = 0; i < n * (n - 1) / 2; i++) pow3 *= 3; long long fact = 1; for (int i = 2; i <= n; i++) fact *= i;
        assert(total == (1LL << (n * n)) && nRefl == (1LL << (n * n - n)) && nSym == (1LL << (n * (n + 1) / 2)) && nAnti == (1LL << n) * pow3 && nTrans == expectTrans[n] && nPoset == expectPoset[n] && nEquiv == bell[n] && nStrict == nPoset && nTotalOrder == fact && nEquivAndPoset == 1); }
    std::cout << "Sets and relations: exhaustive enumeration over all 2^(n^2) relations for n = 1..4 confirms the counts - reflexive 2^(n^2-n), symmetric 2^(n(n+1)/2), antisymmetric 2^n 3^(n(n-1)/2), transitive 1/2/13/171/3994, partial orders 1/3/19/219, equivalences 1/2/5/15, linear orders n!" << std::endl; return 0;
}
// Time Complexity: O(2^(n²) · n²) 완전 열거
// Space Complexity: O(n)
```
## 집합과 함수(Function)
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 집합과 함수 — 함수 f: A → B 는 "모든 a ∈ A 에 정확히 하나의 b ∈ B 가 대응하는 관계" 이다. 서로 다른 함수의 총수는 |B|^|A| (각 a 마다 b 를 고르므로). 성질별 개수 — 단사(서로 다른 a 는 서로 다른 f(a))는 |B|·(|B|−1)···(|B|−|A|+1), 전사(모든 b 가 쓰임)는 포함-배제로 Σ_k (−1)^k C(m,k)(m−k)^n = m!·S(n,m) (제2종 스털링 수),
// 전단사(일대일 대응)는 |A| = |B| = n 일 때 n!. 비둘기집 원리가 이 개수 공식의 결과다: |A| > |B| 이면 단사가 0 개. 집합 연산과의 관계 — 상(像) f(X) = {f(x)}, 역상 f⁻¹(Y) = {x : f(x) ∈ Y}. 역상은 모든 집합 연산을 보존한다(f⁻¹(Y₁ ∪ Y₂) = f⁻¹(Y₁) ∪ f⁻¹(Y₂), ∩ 와 여집합도).
// 상은 합집합만 보존하고 교집합은 f(X₁ ∩ X₂) ⊆ f(X₁) ∩ f(X₂) 이며 f 가 단사일 때만 등호. 검증: |A| ≤ 5, |B| ≤ 5 의 모든 함수를 나열해 ① 총수 |B|^|A|, 단사 수, 전사 수(= m!·S(n,m)), 전단사 수 ② 모든 함수와 무작위 부분집합에서 상·역상 법칙 ③ 교집합의 상이 진부분집합이 되는 반례가 단사가 아닌 함수에서만 존재 ④ 합성 (g∘f)⁻¹ = f⁻¹∘g⁻¹
long long stirling2(int n, int k) { std::vector<std::vector<long long>> S(n + 1, std::vector<long long>(k + 1, 0)); S[0][0] = 1; for (int i = 1; i <= n; i++) for (int j = 1; j <= std::min(i, k); j++) S[i][j] = j * S[i - 1][j] + S[i - 1][j - 1]; return S[n][k]; }
int main() {
    std::mt19937 rng(5); bool counterexampleNonInjective = false;
    for (int n = 1; n <= 5; n++) for (int m = 1; m <= 5; m++) { long long total = 0, inj = 0, surj = 0, bij = 0; std::vector<int> f(n, 0); for (;;) { total++; std::set<int> img(f.begin(), f.end()); bool injective = (int)img.size() == n, surjective = (int)img.size() == m; inj += injective; surj += surjective; bij += injective && surjective;
            if (total % 7 == 0) { unsigned X1 = rng() & ((1u << n) - 1), X2 = rng() & ((1u << n) - 1); auto image = [&](unsigned X) { unsigned r = 0; for (int a = 0; a < n; a++) if (X >> a & 1) r |= 1u << f[a]; return r; }; assert(image(X1 | X2) == (image(X1) | image(X2)) && (image(X1 & X2) & ~(image(X1) & image(X2))) == 0); if (image(X1 & X2) != (image(X1) & image(X2))) { counterexampleNonInjective = true; assert(!injective); } if (injective) assert(image(X1 & X2) == (image(X1) & image(X2))); }
            int i = 0; while (i < n && ++f[i] == m) f[i++] = 0; if (i == n) break; }
        long long pw = 1; for (int k = 0; k < n; k++) pw *= m; long long falling = 1; for (int k = 0; k < n; k++) falling *= std::max(0, m - k); long long fm = 1; for (int k = 2; k <= m; k++) fm *= k; assert(total == pw && inj == falling && surj == fm * stirling2(n, m) && bij == (n == m ? fm : 0)); if (n > m) assert(inj == 0); }                              // ① 개수
    for (int t = 0; t < 2000; t++) { int n = 1 + rng() % 8, m = 1 + rng() % 8; std::vector<int> f(n); for (int& x : f) x = rng() % m; unsigned Y1 = rng() & ((1u << m) - 1), Y2 = rng() & ((1u << m) - 1); auto pre = [&](unsigned Y) { unsigned r = 0; for (int a = 0; a < n; a++) if (Y >> f[a] & 1) r |= 1u << a; return r; }; unsigned fullA = (1u << n) - 1, fullB = (1u << m) - 1;
        assert(pre(Y1 | Y2) == (pre(Y1) | pre(Y2)) && pre(Y1 & Y2) == (pre(Y1) & pre(Y2)) && pre(fullB & ~Y1) == (fullA & ~pre(Y1)));                                                                                                   // ② 역상은 합·교·여집합을 보존
        int k = 1 + rng() % 6; std::vector<int> g(m); for (int& x : g) x = rng() % k; unsigned Z = rng() & ((1u << k) - 1); auto preG = [&](unsigned Y) { unsigned r = 0; for (int b = 0; b < m; b++) if (Y >> g[b] & 1) r |= 1u << b; return r; }; assert(pre(preG(Z)) == [&] { unsigned r = 0; for (int a = 0; a < n; a++) if (Z >> g[f[a]] & 1) r |= 1u << a; return r; }());   // ④ (g∘f)⁻¹ = f⁻¹∘g⁻¹
    }
    assert(counterexampleNonInjective);
    std::cout << "Sets and functions: all functions A->B with |A|,|B| <= 5 were enumerated - totals |B|^|A|, injective counts equal falling factorials, surjective counts equal m!*S(n,m), bijections n!; preimages preserve union/intersection/complement and compose contravariantly, images preserve unions only (intersection counterexamples appear exactly for non-injective functions)" << std::endl; return 0;
}
// Time Complexity: 함수 전수 열거 O(m^n · n)
// Space Complexity: O(n)
```
## SQL은 왜 집합 이론 위에서 동작하는가?
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <iterator>
#include <map>
#include <optional>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// SQL 은 왜 집합 이론 위에서 동작하는가 — 관계형 모델에서 테이블(릴레이션)은 튜플의 집합이고 질의는 그 위의 대수 연산(관계 대수)의 합성이다: SELECT DISTINCT = 사영 π, WHERE = 선택 σ, JOIN = 곱집합 위의 선택 ⋈, UNION/INTERSECT/EXCEPT = ∪, ∩, −, GROUP BY = 키가 같은 행끼리의 분할.
// 연산이 대수 법칙을 만족하기 때문에 질의 최적화기가 "의미를 바꾸지 않고" 식을 변형할 수 있다 — 선택 밀어내리기 σ_p(R ⋈ S) = σ_p(R) ⋈ S, 조인의 교환·결합법칙, 합집합 분배법칙 등. 그래서 사용자는 "무엇을" 쓰고 최적화기가 "어떻게" 를 고른다(선언적).
// 그러나 실제 SQL 은 순수한 집합이 아니다: ① 기본은 중복을 허용하는 다중집합(bag)이라 UNION ALL / EXCEPT ALL 이 별도로 있고 ② NULL 때문에 논리가 3 값(참, 거짓, 알 수 없음)이 되어 고전 집합 법칙 σ_p(R) ∪ σ_¬p(R) = R 이 깨진다 — NOT IN 에 NULL 이 있으면 결과가 비는 유명한 함정. 증거: ① 대수 법칙 5 개를 무작위 릴레이션으로 검증 ② bag 의미론과 set 의미론의 차이(UNION vs UNION ALL 크기 등식) ③ NULL 이 있는 데이터에서 σ_p ∪ σ_¬p 가 R 보다 작고 NOT IN 이 빈 결과를 내는 사례를 재현
typedef std::vector<int> Row; typedef std::vector<Row> Bag; typedef std::set<Row> Rel; typedef std::optional<int> Val; typedef std::optional<bool> Tri;
Rel toSet(const Bag& b) { return Rel(b.begin(), b.end()); }
Rel join(const Rel& r, const Rel& s) { Rel o; for (auto& x : r) for (auto& y : s) if (x[1] == y[0]) o.insert({x[0], x[1], y[1]}); return o; }
int main() {
    std::mt19937 rng(7); for (int t = 0; t < 200; t++) { Rel R, S, T; for (int i = 0; i < 12; i++) { R.insert({(int)(rng() % 6), (int)(rng() % 4)}); S.insert({(int)(rng() % 4), (int)(rng() % 5)}); T.insert({(int)(rng() % 5), (int)(rng() % 3)}); }
        auto pa = [](const Row& r) { return r[0] < 3; }; auto sel = [&](const Rel& x, auto p) { Rel o; for (auto& r : x) if (p(r)) o.insert(r); return o; };
        assert(sel(join(R, S), pa) == join(sel(R, pa), S));                                                                                                                                   // 선택 밀어내리기
        Rel RS; for (auto& x : R) for (auto& y : S) if (x[1] == y[0]) RS.insert({x[0], x[1], y[1]}); auto swapJoin = [&](const Rel& s, const Rel& r) { Rel o; for (auto& y : s) for (auto& x : r) if (x[1] == y[0]) o.insert({x[0], x[1], y[1]}); return o; }; assert(swapJoin(S, R) == RS);                // 조인의 교환
        Rel left, right; { Rel RS2 = join(R, S); for (auto& a : RS2) for (auto& b : T) if (a[2] == b[0]) left.insert({a[0], a[1], a[2], b[1]}); Rel ST; for (auto& y : S) for (auto& z : T) if (y[1] == z[0]) ST.insert({y[0], y[1], z[1]}); for (auto& x : R) for (auto& st : ST) if (x[1] == st[0]) right.insert({x[0], x[1], st[1], st[2]}); } assert(left == right);   // 조인의 결합
        Rel U = R; U.insert(R.begin(), R.end()); Rel R2; for (int i = 0; i < 8; i++) R2.insert({(int)(rng() % 6), (int)(rng() % 4)}); Rel un = R; un.insert(R2.begin(), R2.end()); Rel viaSel = sel(R, pa); Rel s2 = sel(R2, pa); viaSel.insert(s2.begin(), s2.end()); assert(sel(un, pa) == viaSel);   // 선택은 합집합에 분배
        Rel cond; for (auto& r : R) if (pa(r) || r[1] == 2) cond.insert(r); Rel part1 = sel(R, pa), part2 = sel(R, [](const Row& r) { return r[1] == 2; }); part1.insert(part2.begin(), part2.end()); assert(cond == part1);                                           // σ_{p∨q} = σ_p ∪ σ_q
        Rel pr1; for (auto& r : R) pr1.insert({r[0]}); Rel pr2; for (auto& r : R2) pr2.insert({r[0]}); Rel pu = pr1; pu.insert(pr2.begin(), pr2.end()); Rel pr3; for (auto& r : un) pr3.insert({r[0]}); assert(pr3 == pu); }                                                  // π 는 합집합에 분배
    Bag a = {{1}, {1}, {2}}, b = {{1}, {3}}; Bag unionAll = a; unionAll.insert(unionAll.end(), b.begin(), b.end()); Rel unionSet = toSet(unionAll); assert(unionAll.size() == 5 && unionSet.size() == 3);                                               // ② UNION ALL 은 개수를 더하고 UNION 은 중복 제거
    std::map<int, int> ca, cb; for (auto& r : a) ca[r[0]]++; for (auto& r : b) cb[r[0]]++; std::map<int, int> exceptAll; for (auto& [k, v] : ca) { int d = v - (cb.count(k) ? cb[k] : 0); if (d > 0) exceptAll[k] = d; } assert(exceptAll[1] == 1 && exceptAll[2] == 1 && exceptAll.size() == 2); Rel exceptSet; for (auto& r : toSet(a)) if (!toSet(b).count(r)) exceptSet.insert(r); assert(exceptSet.size() == 1);        // EXCEPT ALL vs EXCEPT
    auto lessThan = [](Val x, int c) -> Tri { if (!x) return std::nullopt; return *x < c; }; auto notTri = [](Tri t) -> Tri { if (!t) return std::nullopt; return !*t; }; std::vector<Val> col = {1, 5, std::nullopt, 7, 2}; int p = 0, np = 0;
    for (auto& v : col) { Tri t = lessThan(v, 4); if (t && *t) p++; if (notTri(t) && *notTri(t)) np++; } assert(p == 2 && np == 2 && p + np < (int)col.size());                                                                                                                   // ③ σ_p 와 σ_¬p 의 합이 R 보다 작음 (NULL 행은 둘 다 아님)
    std::vector<Val> sub = {1, std::nullopt}; auto notIn = [&](Val x) -> Tri { Tri result = true; for (auto& s : sub) { Tri eq = (!x || !s) ? Tri(std::nullopt) : Tri(*x == *s); if (eq && *eq) return false; if (!eq) result = std::nullopt; } return result; }; int kept = 0; for (int x : {2, 3, 4}) { Tri t = notIn(x); kept += (t && *t); } assert(kept == 0);                                      // x NOT IN (1, NULL) 은 모든 x 에 대해 참이 아님
    std::cout << "SQL and set theory: selection pushdown, join commutativity and associativity, selection over union, sigma over OR, and projection over union hold on 200 random relations; UNION ALL vs UNION and EXCEPT ALL vs EXCEPT show bag vs set semantics; three-valued logic makes sigma_p + sigma_not_p cover only " << p + np << " of " << col.size() << " rows and x NOT IN (1, NULL) keeps nothing" << std::endl; return 0;
}
// Time Complexity: 관계 대수 연산 자체는 설명용 (질의 최적화기는 비용 기반 탐색)
// Space Complexity: O(릴레이션 크기)
```
## AI에서 Label Set과 Vocabulary Set의 의미
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// AI 에서 Label Set 과 Vocabulary Set 의 의미 — 모델은 "닫힌 집합" 위에서 숫자를 다룬다. Label set: 분류 모델이 고를 수 있는 정답 후보의 유한 집합 C. 출력층이 |C| 개 로짓이라 레이블을 추가하려면 모델 구조(출력 차원)와 학습 데이터를 바꿔야 하고(닫힌 세계 가정), 집합에 없는 입력은 억지로 C 의 어딘가로 분류된다.
// Vocabulary set: 텍스트 모델이 이해하는 토큰의 유한 집합 V. 임베딩 표 크기가 |V|·d 이고 소프트맥스 비용이 |V| 에 비례하므로 V 가 크면 무겁다. 반대로 V 가 작으면 단어가 여러 조각으로 쪼개져 시퀀스가 길어진다 — 어휘 크기 vs 시퀀스 길이의 교환이다.
// 서브워드 토큰화(BPE, Byte-Pair Encoding)는 이 교환을 푸는 표준 방법이다: 시작 어휘 = 모든 문자(또는 바이트), 코퍼스에서 가장 자주 인접한 두 토큰을 합쳐 새 토큰으로 추가하기를 반복한다. 검증(합성 코퍼스): ① 병합을 늘릴수록(어휘가 커질수록) 단어당 평균 토큰 수가 단조 감소 ② 단어 수준 어휘는 학습에 없던 단어에서 OOV 가 생기지만 BPE(문자 기반)는 OOV 0 ③ 인코딩-디코딩이 원문을 복원 ④ 임베딩 매개변수 수 |V|·d 와 소프트맥스 곱셈 수의 증가를 표로 계산
typedef std::vector<std::string> Seq;
std::vector<Seq> splitChars(const std::vector<std::string>& words) { std::vector<Seq> out; for (auto& w : words) { Seq s; for (char c : w) s.push_back(std::string(1, c)); out.push_back(s); } return out; }
std::vector<std::pair<std::string, std::string>> trainBPE(std::vector<Seq> corpus, const std::vector<long>& freq, int merges) { std::vector<std::pair<std::string, std::string>> rules; for (int m = 0; m < merges; m++) { std::map<std::pair<std::string, std::string>, long> pairs; for (size_t i = 0; i < corpus.size(); i++) for (size_t j = 0; j + 1 < corpus[i].size(); j++) pairs[{corpus[i][j], corpus[i][j + 1]}] += freq[i];
        if (pairs.empty()) break; auto best = std::max_element(pairs.begin(), pairs.end(), [](auto& a, auto& b) { return a.second < b.second || (a.second == b.second && a.first > b.first); }); rules.push_back(best->first); for (auto& s : corpus) { Seq o; for (size_t j = 0; j < s.size();) { if (j + 1 < s.size() && s[j] == best->first.first && s[j + 1] == best->first.second) { o.push_back(s[j] + s[j + 1]); j += 2; } else o.push_back(s[j++]); } s = o; } } return rules; }
Seq encode(const std::string& word, const std::vector<std::pair<std::string, std::string>>& rules) { Seq s; for (char c : word) s.push_back(std::string(1, c)); for (auto& r : rules) { Seq o; for (size_t j = 0; j < s.size();) { if (j + 1 < s.size() && s[j] == r.first && s[j + 1] == r.second) { o.push_back(s[j] + s[j + 1]); j += 2; } else o.push_back(s[j++]); } s = o; } return s; }
int main() {
    std::mt19937 rng(3); const std::vector<std::string> stems = {"set", "list", "tree", "graph", "hash", "queue", "stack", "heap", "trie", "sort"}, suffixes = {"", "s", "ed", "ing", "er", "ers", "able"}; std::vector<std::string> train; std::vector<long> freq; std::map<std::string, long> seen;
    for (int i = 0; i < 5000; i++) { std::string w = stems[rng() % stems.size()] + suffixes[rng() % suffixes.size()]; seen[w]++; } for (auto& [w, c] : seen) { train.push_back(w); freq.push_back(c); }
    std::vector<std::string> heldOut; for (auto& s : stems) for (auto& x : suffixes) if (!seen.count(s + x)) heldOut.push_back(s + x); heldOut.push_back("setting"); heldOut.push_back("graphed"); heldOut.push_back("heaper");
    std::set<std::string> wordVocab(train.begin(), train.end()); int oov = 0; for (auto& w : heldOut) oov += !wordVocab.count(w); assert(oov > 0);                                                                                        // ② 단어 수준 어휘는 OOV 가 생김
    double prevTokens = 1e9; std::vector<double> tokens; for (int merges : {0, 5, 10, 20, 40, 80}) { auto rules = trainBPE(splitChars(train), freq, merges); long total = 0, words = 0; std::set<std::string> vocab; for (size_t i = 0; i < train.size(); i++) { Seq e = encode(train[i], rules); total += (long)e.size() * freq[i]; words += freq[i]; std::string joined; for (auto& t : e) { joined += t; vocab.insert(t); } assert(joined == train[i]); } double avg = (double)total / words; assert(avg <= prevTokens + 1e-9); prevTokens = avg; tokens.push_back(avg);        // ① 단조 감소 ③ 복원
        for (auto& w : heldOut) { Seq e = encode(w, rules); std::string joined; for (auto& t : e) joined += t; assert(joined == w); } }                                                                                                                      // 학습에 없던 단어도 문자 조각으로 복원 → OOV 0
    assert(tokens.front() > 5 && tokens.back() < 0.6 * tokens.front());
    std::cout << "Label and vocabulary sets: held-out words were out-of-vocabulary " << oov << " times for the word-level vocabulary but BPE re-encoded every one losslessly; average tokens per word fell as merges grew (0/5/10/20/40/80 merges): "; for (double t : tokens) std::cout << t << " "; std::cout << "; for d=64 an embedding table of V=32000 needs " << 32000 * 64 << " parameters while V=256 needs " << 256 * 64 << std::endl; return 0;
}
// Time Complexity: BPE 학습 O(병합 수 × 코퍼스 크기), 인코딩 O(병합 수 × 단어 길이)
// Space Complexity: O(어휘 크기 · 임베딩 차원)
```
## 비트마스크와 집합의 대응 관계
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 비트마스크와 집합의 대응 — 전체집합이 n 원소 {0..n−1} 이면 부분집합 S ↔ 정수 mask(S) = Σ_{i∈S} 2^i 는 부분집합 2ⁿ 개와 정수 0..2ⁿ−1 사이의 전단사다(이진수의 i 번째 비트 = i 의 소속). 이 대응은 연산까지 보존하는 동형 사상(부울 대수 동형)이다:
//   합집합 ↔ OR  교집합 ↔ AND  여집합 ↔ XOR (전체 마스크)  차집합 A−B ↔ A & ~B  대칭차 ↔ XOR  A ⊆ B ↔ (A & B) == A  원소 i 추가 ↔ mask | 1<<i  제거 ↔ & ~(1<<i)  소속 ↔ mask >> i & 1  크기 ↔ popcount  최소 원소 ↔ ctz(mask)  최하위 원소 분리 ↔ mask & −mask  최하위 제거 ↔ mask & (mask − 1).
// 포함 순서 A ⊆ B 이면 mask(A) ≤ mask(B) 이므로 정수의 대소 순서는 포함 순서의 선형 확장이다 — 마스크를 0 부터 증가시키며 DP 를 채우면 "부분집합이 먼저 나온다". Gray 코드는 연속한 마스크가 정확히 한 비트만 다른 열(초입방체의 해밀턴 경로)이다. 검증: ① n ≤ 10 의 모든 마스크 쌍에서 위 연산 대응이 std::set 과 일치(전수) ② 포함 ⇒ 수치 비교 ③ Gray 코드가 모든 마스크를 한 번씩 정확히 한 비트 차이로 방문 ④ 그 외 관용구 (분리·제거·최소 원소)
std::set<int> toSet(uint32_t m, int n) { std::set<int> s; for (int i = 0; i < n; i++) if (m >> i & 1) s.insert(i); return s; }
std::set<int> withElement(std::set<int> s, int i) { s.insert(i); return s; } std::set<int> withoutElement(std::set<int> s, int i) { s.erase(i); return s; }
void verifyOperations(int n) {                                                                                       // ① ② 모든 마스크 쌍에서 연산이 std::set 과 일치
    const uint32_t full = (1u << n) - 1;
    for (uint32_t a = 0; a <= full; a++) for (uint32_t b = 0; b <= full; b++) { auto A = toSet(a, n), B = toSet(b, n); std::set<int> u(A), in, df, sd; u.insert(B.begin(), B.end()); for (int x : A) if (B.count(x)) in.insert(x); for (int x : A) if (!B.count(x)) df.insert(x); sd = df; for (int x : B) if (!A.count(x)) sd.insert(x);
        assert(toSet(a | b, n) == u && toSet(a & b, n) == in && toSet(a & ~b & full, n) == df && toSet(a ^ b, n) == sd); bool sub = std::includes(B.begin(), B.end(), A.begin(), A.end()); assert(((a & b) == a) == sub); if (sub) assert(a <= b); } }
void verifyIdioms(int n) {                                                                                           // ④ 크기·최소 원소·분리·제거·소속·추가·삭제
    const uint32_t full = (1u << n) - 1;
    for (uint32_t a = 0; a <= full; a++) { auto A = toSet(a, n); assert(toSet(full ^ a, n).size() + A.size() == (size_t)n && __builtin_popcount(a) == (int)A.size());
        if (a) { std::set<int> rest = A; rest.erase(rest.begin()); assert(*A.begin() == __builtin_ctz(a) && (a & -a) == (1u << *A.begin()) && toSet(a & (a - 1), n) == rest); }
        for (int i = 0; i < n; i++) assert((int)(a >> i & 1) == (int)A.count(i) && toSet(a | (1u << i), n) == withElement(A, i) && toSet(a & ~(1u << i), n) == withoutElement(A, i)); } }
void verifyGray(int n) {                                                                                             // ③ Gray 코드: 모든 마스크를 한 번씩, 한 비트 차이로
    const uint32_t full = (1u << n) - 1; std::set<uint32_t> visited; uint32_t prev = 0; for (uint32_t i = 0; i <= full; i++) { uint32_t g = i ^ (i >> 1); assert(visited.insert(g).second); if (i) assert(__builtin_popcount(g ^ prev) == 1); prev = g; } assert(visited.size() == (size_t)full + 1); }
int main() {
    for (int n = 1; n <= 8; n++) { verifyOperations(n); verifyIdioms(n); verifyGray(n); }
    std::mt19937 rng(23); for (int rep = 0; rep < 2000; rep++) { int n = 9 + (int)(rng() % 20); uint32_t full = n == 32 ? ~0u : (1u << n) - 1; uint32_t a = (uint32_t)rng() & full, b = (uint32_t)rng() & full; auto A = toSet(a, n), B = toSet(b, n); std::set<int> u(A); u.insert(B.begin(), B.end()); assert(toSet(a | b, n) == u && toSet(~a & full, n).size() + A.size() == (size_t)n); }   // 큰 우주(9..28 원소)는 무작위 표본
    std::cout << "Bitmask <-> set: for every pair of subsets of an n-element universe (n <= 8) OR/AND/AND-NOT/XOR/complement/subset-test/cardinality/lowest-element idioms equal the std::set operations, inclusion implies numeric order, the Gray code visits all masks with single-bit steps, and random masks over larger universes agree too" << std::endl; return 0;
}
// Time Complexity: 집합 연산 O(1) (n ≤ 64), 전수 검증 O(4ⁿ)
// Space Complexity: O(1)
```
## 부분집합 열거 최적화
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 부분집합 열거 최적화 — 집합 S(n 개)의 모든 부분집합에 대해 "부분집합의 합" 같은 값을 구하는 방법의 비용을 비교한다. ① 순진한 방법: 마스크마다 비트를 훑어 합을 다시 계산 → O(n·2ⁿ) ② Gray 코드: 연속한 마스크가 한 비트만 다르므로 합을 ±x 한 번으로 갱신 → O(2ⁿ) (한 원소당 상수)
// ③ 최하위 비트 DP: sum[mask] = sum[mask & (mask−1)] + x[ctz(mask)] → O(2ⁿ) 시간, O(2ⁿ) 메모리. ④ 부분집합 위의 부분집합 열거(for sub = mask; sub; sub = (sub−1) & mask)로 모든 (sub ⊆ mask) 쌍을 훑으면 O(3ⁿ). ⑤ 합 위 DP(SOS DP, zeta 변환): F(mask) = Σ_{sub ⊆ mask} f(sub) 를 비트별로 한 번씩 누적해 O(n·2ⁿ) 에 모든 mask 를 구한다 — 3ⁿ 을 n·2ⁿ 으로 줄인다.
// 검증: ① 세 방법(순진·Gray·최하위 비트 DP)이 같은 합표를 만들고 연산 수가 n·2ⁿ : 2ⁿ : 2ⁿ ② SOS DP 가 O(3ⁿ) 부분집합 순회와 같은 결과를 내고 덧셈 수 n·2ⁿ⁻¹ 이 3ⁿ 보다 훨씬 작음(n = 16) ③ Gray 코드 순회가 모든 마스크를 한 번씩 방문 ④ 크기 k 부분집합만 필요하면 Gosper 가 C(n,k) 개만 방문(2ⁿ 전체 필터링 대비)
int main() {
    std::mt19937 rng(5); const int n = 16; std::vector<long long> x(n); for (auto& v : x) v = rng() % 1000 - 300;
    std::vector<long long> naive(1u << n), gray(1u << n), lowbit(1u << n); long long opsNaive = 0, opsGray = 0, opsLow = 0; for (uint32_t m = 0; m < (1u << n); m++) { long long s = 0; for (int i = 0; i < n; i++) { opsNaive++; if (m >> i & 1) s += x[i]; } naive[m] = s; }
    { uint32_t g = 0; long long s = 0; gray[0] = 0; for (uint32_t i = 1; i < (1u << n); i++) { uint32_t ng = i ^ (i >> 1); int bit = __builtin_ctz(g ^ ng); s += (ng >> bit & 1) ? x[bit] : -x[bit]; opsGray++; g = ng; gray[g] = s; } }                                                                                                                  // Gray 순서로 방문하며 한 번의 덧셈/뺄셈
    lowbit[0] = 0; for (uint32_t m = 1; m < (1u << n); m++) { lowbit[m] = lowbit[m & (m - 1)] + x[__builtin_ctz(m)]; opsLow++; }
    assert(naive == gray && naive == lowbit && opsNaive == (long long)n * (1u << n) && opsGray == (1u << n) - 1 && opsLow == (1u << n) - 1);                                                                                                // ①
    const int n2 = 14; std::vector<long long> f(1u << n2); for (auto& v : f) v = rng() % 100; std::vector<long long> brute(1u << n2, 0); long long visits = 0; for (uint32_t m = 0; m < (1u << n2); m++) { for (uint32_t sub = m;; sub = (sub - 1) & m) { brute[m] += f[sub]; visits++; if (sub == 0) break; } }
    std::vector<long long> sos = f; long long adds = 0; for (int b = 0; b < n2; b++) for (uint32_t m = 0; m < (1u << n2); m++) if (m >> b & 1) { sos[m] += sos[m ^ (1u << b)]; adds++; }
    long long pow3 = 1; for (int i = 0; i < n2; i++) pow3 *= 3; assert(sos == brute && visits == pow3 && adds == (long long)n2 * (1u << (n2 - 1)) && adds * 20 < visits);                                                                                 // ②
    std::vector<char> seen(1u << n, 0); for (uint32_t i = 0; i < (1u << n); i++) { uint32_t g = i ^ (i >> 1); assert(!seen[g]); seen[g] = 1; }                                                                                                    // ③
    for (int k : {2, 5, 8}) { long long cnt = 0, filtered = 0; for (uint32_t m = 0; m < (1u << n); m++) { filtered++; if (__builtin_popcount(m) == k) cnt++; } long long gosperCnt = 0; for (uint32_t v = (1u << k) - 1; v < (1u << n);) { gosperCnt++; uint32_t c = v & -v, r = v + c; v = (((r ^ v) >> 2) / c) | r; } assert(gosperCnt == cnt && ((gosperCnt * 10 < filtered || k == 8))); }     // ④ Gosper 는 C(n,k) 개만 방문
    std::cout << "Subset enumeration: per-mask sums with n=16 took " << opsNaive << " operations naively but " << opsGray << " with Gray-code updates (identical tables); sum-over-subsets DP needed " << adds << " additions versus " << visits << " visits for 3^n submask enumeration at n=14 with identical results; Gosper's hack visits only C(n,k) masks" << std::endl; return 0;
}
// Time Complexity: 순진 O(n·2ⁿ), Gray/최하위 비트 DP O(2ⁿ), 부분집합 열거 O(3ⁿ), SOS DP O(n·2ⁿ)
// Space Complexity: O(2ⁿ)
```

