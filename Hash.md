# Part 1. 해시의 기초
## CreateHashTable()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>
#include <utility>
#include <vector>

// 해시 테이블을 만드는 순간 정해지는 것: 버킷 수 m 과 "해시값 → 버킷 번호" 규칙. m 을 어떻게 고르느냐가 두 갈래다 — ① 소수 m: 번호 = h mod m. 해시값의 모든 비트가 번호에 섞여 들어가므로 키에 규칙적인 패턴(8의 배수 등)이 있어도 잘 퍼진다. ② 2의 거듭제곱 m: 번호 = h & (m − 1) (나눗셈 대신 비트 마스크, 훨씬 빠르다). 대신 해시값의 *낮은 비트* 만 쓰므로 해시 함수가 낮은 비트를 잘 섞어야 한다(항등 해시 + 8의 배수 키 = 버킷의 7/8 이 빈다).
// 그래서 생성자는 요청 크기 n 을 받아 "n 이상인 가장 작은 소수" 또는 "n 이상인 가장 작은 2의 거듭제곱" 으로 올려 잡고, 터무니없이 큰 요청은 거절한다. 모든 버킷은 비어 있고 크기(저장된 원소 수)는 0 이다.
// 검증: ① 1 ≤ n ≤ 100,000 모두에서 nextPrime(n) 이 체로 구한 "n 이상 최소 소수", nextPow2(n) 이 "n 이상 최소 2의 거듭제곱" ② 2의 거듭제곱 m 에서 (h & (m−1)) == h % m (무작위 5 만 개) ③ 어떤 해시값도 번호 < m (소수·2의 거듭제곱 둘 다) ④ 갓 만든 테이블은 버킷이 모두 비어 있고 크기 0, 너무 큰 요청은 예외 ⑤ 규칙적인 키(8의 배수 100 만 개)를 항등 해시로 넣으면 2의 거듭제곱 m 은 버킷의 1/8 만 쓰고 소수 m 은 모두 쓴다.
enum class Mode { Prime, PowerOfTwo };
bool isPrime(std::uint64_t n) { if (n < 2) return false; for (std::uint64_t d = 2; d * d <= n; ++d) if (n % d == 0) return false; return true; }
std::size_t nextPrime(std::size_t n) { if (n < 2) n = 2; while (!isPrime(n)) ++n; return n; }
std::size_t nextPow2(std::size_t n) { std::size_t m = 1; while (m < n) m <<= 1; return m; }
struct HashTable {
    static constexpr std::size_t kMaxBuckets = std::size_t(1) << 28;
    Mode mode; std::size_t m; std::size_t count = 0; std::vector<std::vector<std::pair<std::uint64_t, int>>> buckets;
    HashTable(std::size_t requested, Mode md) : mode(md), m(0) {
        if (requested > kMaxBuckets) throw std::length_error("too many buckets");
        m = md == Mode::Prime ? nextPrime(requested) : nextPow2(requested == 0 ? 1 : requested); buckets.resize(m);
    }
    std::size_t index(std::uint64_t h) const { return mode == Mode::PowerOfTwo ? (std::size_t)(h & (m - 1)) : (std::size_t)(h % m); }
};

int main() {
    // ① 체로 구한 소수 · 비트로 확인하는 2의 거듭제곱
    {   const int N = 100000 + 200; std::vector<char> comp(N + 1, 0); for (int i = 2; (long)i * i <= N; ++i) if (!comp[i]) for (int j = i * i; j <= N; j += i) comp[j] = 1;
        for (std::size_t n = 1; n <= 100000; ++n) {
            std::size_t p = n < 2 ? 2 : n; while (comp[p]) ++p; assert(nextPrime(n) == p && !comp[nextPrime(n)] && nextPrime(n) >= n);
            std::size_t q = nextPow2(n); assert(q >= n && (q & (q - 1)) == 0 && (q == 1 || q / 2 < n));
        }
    }
    // ②③ 비트 마스크 = 나머지, 번호는 항상 m 미만
    std::mt19937_64 rng(5);
    for (std::size_t req : {1u, 2u, 3u, 7u, 8u, 100u, 1000u, 4096u}) {
        HashTable a(req, Mode::PowerOfTwo), b(req, Mode::Prime);
        for (int i = 0; i < 50000; ++i) { std::uint64_t h = rng(); assert(a.index(h) == h % a.m && a.index(h) < a.m && b.index(h) < b.m); }
        assert(a.m >= req && b.m >= req && a.buckets.size() == a.m && b.buckets.size() == b.m);
        for (auto& bucket : a.buckets) assert(bucket.empty()); for (auto& bucket : b.buckets) assert(bucket.empty());       // ④ 모든 버킷이 비어 있다
        assert(a.count == 0 && b.count == 0);
    }
    bool threw = false; try { HashTable huge(HashTable::kMaxBuckets + 1, Mode::Prime); } catch (const std::length_error&) { threw = true; } assert(threw);
    HashTable zero(0, Mode::PowerOfTwo); assert(zero.m == 1 && zero.index(12345) == 0);
    // ⑤ 규칙적인 키: 8 의 배수 100 만 개를 항등 해시로
    {   HashTable p2(1u << 10, Mode::PowerOfTwo), pr(1031, Mode::Prime); std::vector<int> used2(p2.m, 0), usedP(pr.m, 0);
        for (std::uint64_t k = 0; k < 1000000; ++k) { used2[p2.index(k * 8)] = 1; usedP[pr.index(k * 8)] = 1; }
        int u2 = 0, uP = 0; for (int x : used2) u2 += x; for (int x : usedP) uP += x;
        assert(u2 == (int)p2.m / 8 && uP == (int)pr.m);
        std::cout << "CreateHashTable: nextPrime and nextPow2 were exactly the smallest prime / power of two >= n for every n up to 100,000, the mask equalled the remainder for power-of-two sizes, indices stayed below m, fresh tables were empty, an oversized request threw, and 1,000,000 multiples of 8 hashed by the identity function used " << u2 << " of " << p2.m << " power-of-two buckets but all " << uP << " prime buckets" << std::endl; }
    return 0;
}
// Time Complexity: O(m)  (버킷 m개 초기화, 소수 찾기 O(√m) 반복)
// Space Complexity: O(m)
```
## Insert()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

// 체이닝 해시 테이블의 삽입: 키를 해시해 버킷을 정하고, 그 버킷의 연결 리스트(여기서는 벡터)를 훑어 같은 키가 있으면 *값을 갱신*, 없으면 *새 항목을 추가*한다. 반환값은 "새로 추가됐는가". 충돌(서로 다른 키가 같은 버킷)은 같은 리스트에 이어 붙을 뿐이라 정확성에는 영향이 없고 비용만 늘린다 — 모든 키가 한 버킷에 몰려도(최악) 정답은 같고 삽입이 O(n) 이 된다.
// 비용 분석(검증 대상): i 번째 삽입이 훑는 항목 수의 기댓값은 그때의 평균 체인 길이 (i−1)/m 이므로 n 번 삽입의 총 비교 수 ≈ n(n−1)/(2m) = n·α/2 — 평균 삽입 비용 O(1 + α). 또 모든 체인 길이의 합은 항상 원소 수 n 과 같다(손실·중복 없음).
// 검증: ① 무작위 연산 20 만 번(삽입·갱신 섞음)을 std::unordered_map 과 비교 — 반환값(새로움 여부), 크기, 모든 키의 값 ② 모든 키가 같은 버킷에 몰리는 최악(m 의 배수 키)에서도 같은 결과, 체인 길이 = n ③ 서로 다른 무작위 키 n 개의 총 비교 수가 n(n−1)/(2m) 의 ±5% ④ 체인 길이의 합 = n.
struct Table {
    using Entry = std::pair<std::uint64_t, int>;
    std::vector<std::vector<Entry>> b; std::size_t n = 0; long comparisons = 0;
    explicit Table(std::size_t m) : b(m) {}
    static std::uint64_t mix(std::uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
    std::size_t bucket(std::uint64_t k, bool identity) const { return (identity ? k : mix(k)) % b.size(); }
    bool insert(std::uint64_t k, int v, bool identity = false) {                          // true: 새 항목, false: 기존 키의 값 갱신
        auto& chain = b[bucket(k, identity)];
        for (Entry& e : chain) { ++comparisons; if (e.first == k) { e.second = v; return false; } }
        chain.push_back({k, v}); ++n; return true;
    }
    const int* find(std::uint64_t k, bool identity = false) const { for (const Entry& e : b[bucket(k, identity)]) if (e.first == k) return &e.second; return nullptr; }
    std::size_t totalChain() const { std::size_t s = 0; for (auto& c : b) s += c.size(); return s; }
};

int main() {
    std::mt19937_64 rng(2);
    // ① 무작위 연산 20 만 번 (키 범위 5,000 → 많은 갱신): unordered_map 과 같은 동작
    {   Table t(257); std::unordered_map<std::uint64_t, int> ref; long newCount = 0;
        for (int i = 0; i < 200000; ++i) { std::uint64_t k = rng() % 5000; int v = (int)(rng() % 1000); bool fresh = t.insert(k, v); bool refFresh = ref.find(k) == ref.end(); ref[k] = v; assert(fresh == refFresh); newCount += fresh; }
        assert(t.n == ref.size() && (long)t.n == newCount && t.totalChain() == t.n);
        for (auto& [k, v] : ref) { const int* p = t.find(k); assert(p && *p == v); } assert(t.find(99999) == nullptr);
    }
    // ② 최악: 키가 모두 m 의 배수이고 항등 해시 → 한 버킷. 정답은 같고 체인 길이 = n
    {   const std::size_t m = 101; Table t(m); std::unordered_map<std::uint64_t, int> ref;
        for (int i = 0; i < 3000; ++i) { std::uint64_t k = (rng() % 400) * m; int v = (int)(rng() % 100); bool fresh = t.insert(k, v, true); assert(fresh == (ref.find(k) == ref.end())); ref[k] = v; }
        std::size_t longest = 0; for (auto& c : t.b) longest = std::max(longest, c.size()); assert(longest == ref.size() && t.n == ref.size() && t.totalChain() == t.n);
        for (auto& [k, v] : ref) assert(*t.find(k, true) == v);
    }
    // ③ 서로 다른 무작위 키 n 개를 넣을 때의 총 비교 수 ≈ n(n−1)/(2m), 여러 α 에서
    for (std::size_t n : {5000u, 20000u, 80000u}) {
        Table t(10007); std::unordered_map<std::uint64_t, int> seen; while (seen.size() < n) { std::uint64_t k = rng(); if (seen.emplace(k, 0).second) t.insert(k, 0); }
        double expected = (double)n * (double)(n - 1) / (2.0 * 10007); double ratio = (double)t.comparisons / expected; assert(ratio > 0.95 && ratio < 1.05 && t.totalChain() == n);
    }
    std::cout << "Insert: 200,000 random insert/update operations on a chaining table returned the same 'was it new' flags, size and values as std::unordered_map, 3000 operations with every key colliding into one bucket still agreed (chain length = n), the sum of chain lengths always equalled n, and the total comparison count for n distinct random keys stayed within 5% of n(n-1)/(2m) at three load factors" << std::endl; return 0;
}
// Time Complexity: 평균 O(1 + α), 최악 O(n)
// Space Complexity: O(n)
```
## Search()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

// 체이닝 해시 테이블의 검색: 버킷을 정하고 그 리스트를 처음부터 훑는다. *실패한* 검색은 리스트 전체를 훑으므로 평균 비교 수가 정확히 평균 체인 길이 α = n/m 이고, *성공한* 검색은 찾는 항목이 리스트의 몇 번째에 있느냐 만큼 비교하므로 평균 1 + (n − 1)/(2m) ≈ 1 + α/2 이다(리스트 안 위치가 균등하다고 보면). 두 값을 표 전체를 훑어 *정확히* 계산한 값과, 실제 무작위 검색에서 센 값 둘 다 확인한다.
// 정확한 값: 실패 검색의 기댓값(무작위 버킷) = Σ(체인 길이) / m = n/m 정확히. 성공 검색의 기댓값(저장된 키를 균등하게 골랐을 때) = (Σ 체인마다 Σ_{j=1..len} j) / n = (Σ len(len+1)/2) / n.
// 검증: ① 무작위 삽입·검색 20 만 번을 std::unordered_map 과 비교(찾음/못 찾음, 값) ② 표 전체에서 계산한 정확한 평균 비교 수가 위의 공식과 같고, 실제 검색 10 만 번에서 센 평균이 ±3% 이내 ③ 해시 함수 입력에 따라 못 찾는 키가 찾는 키와 같은 버킷일 수 있음 — 그래도 거짓 양성은 없다(비교는 키 전체 값으로) ④ 빈 표와 경계.
struct Table {
    using Entry = std::pair<std::uint64_t, int>;
    std::vector<std::vector<Entry>> b; std::size_t n = 0;
    explicit Table(std::size_t m) : b(m) {}
    static std::uint64_t mix(std::uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
    void put(std::uint64_t k, int v) { auto& c = b[mix(k) % b.size()]; for (Entry& e : c) if (e.first == k) { e.second = v; return; } c.push_back({k, v}); ++n; }
    const int* find(std::uint64_t k, long* comparisons = nullptr) const {
        for (const Entry& e : b[mix(k) % b.size()]) { if (comparisons) ++*comparisons; if (e.first == k) return &e.second; }
        return nullptr;
    }
    double exactUnsuccessful() const { std::size_t s = 0; for (auto& c : b) s += c.size(); return (double)s / (double)b.size(); }              // 무작위 버킷을 훑는 평균 = n/m
    double exactSuccessful() const { double s = 0; for (auto& c : b) s += (double)c.size() * (double)(c.size() + 1) / 2.0; return n ? s / (double)n : 0.0; }   // 저장된 키 하나를 고를 때 평균 비교 수
};

int main() {
    std::mt19937_64 rng(3);
    // ① 빈 표 · 경계 · 무작위 삽입/검색 20 만 번 (unordered_map 과 비교)
    {   Table t(509); assert(t.find(7) == nullptr && t.exactUnsuccessful() == 0.0 && t.exactSuccessful() == 0.0);
        std::unordered_map<std::uint64_t, int> ref;
        for (int i = 0; i < 200000; ++i) {
            std::uint64_t k = rng() % 3000; if (rng() % 2) { int v = (int)(rng() % 100); t.put(k, v); ref[k] = v; } else { const int* p = t.find(k); auto it = ref.find(k); assert((p != nullptr) == (it != ref.end())); if (p) assert(*p == it->second); }
        }
        assert(t.n == ref.size());
    }
    // ② 정확한 평균 비교 수 = 공식, 실제 검색의 평균 ≈ 공식
    for (auto [n, m] : std::vector<std::pair<std::size_t, std::size_t>>{{2000, 4001}, {20000, 20011}, {60000, 20011}}) {
        Table t(m); std::unordered_set<std::uint64_t> keys; while (keys.size() < n) { std::uint64_t k = rng(); if (keys.insert(k).second) t.put(k, 1); }
        double alpha = (double)n / (double)m; assert(std::abs(t.exactUnsuccessful() - alpha) < 1e-12);                                   // 실패 검색의 평균 비교 수는 정확히 α
        double succ = t.exactSuccessful(); assert(succ >= 1.0 && std::abs(succ - (1 + alpha / 2)) < 0.03 * (1 + alpha / 2));            // 성공 검색은 ≈ 1 + α/2
        long cmp = 0; std::vector<std::uint64_t> stored(keys.begin(), keys.end());
        for (int i = 0; i < 100000; ++i) { const int* p = t.find(stored[rng() % stored.size()], &cmp); assert(p); } double avgSucc = (double)cmp / 100000; assert(std::abs(avgSucc - succ) < 0.03 * succ);
        long cmp2 = 0; int misses = 0; for (int i = 0; i < 100000; ++i) { std::uint64_t k = rng(); if (keys.count(k)) continue; ++misses; assert(t.find(k, &cmp2) == nullptr); } assert(std::abs((double)cmp2 / misses - alpha) < 0.03 * alpha + 0.01);
    }
    std::cout << "Search: 200,000 random put/get operations matched std::unordered_map, the exact mean comparison count of an unsuccessful search equalled n/m, a successful one stayed within 3% of 1 + alpha/2, measured averages over 100,000 random searches matched those exact values, and no absent key was ever reported present" << std::endl; return 0;
}
// Time Complexity: 평균 O(1 + α), 최악 O(n)
// Space Complexity: O(1)
```
## Delete()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

// 삭제는 삽입·검색보다 까다롭다. 체이닝은 리스트에서 항목을 빼면 끝이지만, *개방 주소법(선형 탐사)* 에서는 "검색은 빈 칸을 만나면 멈춘다" 는 규칙 때문에 칸을 그냥 비우면 그 칸을 *지나쳐 저장된* 키들이 검색에서 사라진다(아래 시연: 잃어버린 키가 실제로 생긴다). 해법 둘 — ① 묘비(tombstone): 지운 칸에 표시를 남기고 검색은 계속 지나가며 삽입은 재사용한다. 단점: 묘비가 쌓이면 검색이 길어져 주기적인 재구성이 필요. ② *뒤로 당기기(backward shift, Knuth 알고리즘 R)*: 지운 칸 뒤의 군집을 훑으며 "원래 자리(home)가 빈 칸 이전이라 빈 칸을 건너 있어야 하는" 키를 빈 칸으로 끌어와 불변식(모든 키는 home 에서 자기 칸까지 빈 칸 없이 이어진다)을 지킨다 — 묘비가 필요 없다.
// 검증: ① 체이닝 삭제를 무작위 연산 10 만 번으로 std::unordered_map 과 비교(삭제 반환값 포함) ② 선형 탐사 표에서 뒤로 당기기 삭제를 무작위 삽입·삭제·검색 20 만 번으로 비교하고 *매 100 번마다* 불변식(각 키가 home 에서 자기 칸까지 빈 칸 없이 닿음) 검사 ③ 묘비 방식도 같은 결과 ④ 단순히 비우기만 하면 검색이 틀린다는 반례(잃어버린 키 > 0).
struct Open {                                                                  // 선형 탐사, 키 0 은 쓰지 않는다 (빈 칸 = 0)
    std::vector<std::uint64_t> slot; std::size_t n = 0;
    explicit Open(std::size_t m) : slot(m, 0) {}
    std::size_t home(std::uint64_t k) const { k += 0x9e3779b97f4a7c15ULL; k = (k ^ (k >> 30)) * 0xbf58476d1ce4e5b9ULL; k = (k ^ (k >> 27)) * 0x94d049bb133111ebULL; return (std::size_t)((k ^ (k >> 31)) % slot.size()); }
    bool insert(std::uint64_t k) { std::size_t i = home(k); while (slot[i]) { if (slot[i] == k) return false; i = (i + 1) % slot.size(); } slot[i] = k; ++n; return true; }
    bool contains(std::uint64_t k) const { std::size_t i = home(k); while (slot[i]) { if (slot[i] == k) return true; i = (i + 1) % slot.size(); } return false; }
    bool erase(std::uint64_t k) {                                              // 뒤로 당기기 (알고리즘 R)
        std::size_t m = slot.size(), i = home(k); while (slot[i] && slot[i] != k) i = (i + 1) % m; if (!slot[i]) return false;
        slot[i] = 0; --n; std::size_t j = i;
        while (true) {
            j = (j + 1) % m; if (!slot[j]) break; std::size_t h = home(slot[j]);
            bool between = i <= j ? (i < h && h <= j) : (i < h || h <= j);      // h 가 (i, j] 안이면 slot[j] 는 그대로 있어도 도달 가능
            if (!between) { slot[i] = slot[j]; slot[j] = 0; i = j; }
        }
        return true;
    }
    bool eraseNaive(std::uint64_t k) { std::size_t m = slot.size(), i = home(k); while (slot[i] && slot[i] != k) i = (i + 1) % m; if (!slot[i]) return false; slot[i] = 0; --n; return true; }   // 잘못된 삭제
    bool invariant() const { for (std::size_t i = 0; i < slot.size(); ++i) if (slot[i]) { std::size_t j = home(slot[i]); while (j != i) { if (!slot[j]) return false; j = (j + 1) % slot.size(); } } return true; }
};
struct Tomb {                                                                  // 묘비 방식: 0 = 빈 칸, 1 = 묘비(키 값으로 쓰지 않음)
    std::vector<std::uint64_t> slot; std::size_t live = 0;
    explicit Tomb(std::size_t m) : slot(m, 0) {}
    std::size_t home(std::uint64_t k) const { Open o(slot.size()); return o.home(k); }
    bool insert(std::uint64_t k) { if (contains(k)) return false; std::size_t i = home(k); while (slot[i] && slot[i] != 1) i = (i + 1) % slot.size(); slot[i] = k; ++live; return true; }
    bool contains(std::uint64_t k) const { std::size_t i = home(k), steps = 0; while (slot[i] && steps++ < slot.size()) { if (slot[i] == k) return true; i = (i + 1) % slot.size(); } return false; }
    bool erase(std::uint64_t k) { std::size_t i = home(k), steps = 0; while (slot[i] && steps++ < slot.size()) { if (slot[i] == k) { slot[i] = 1; --live; return true; } i = (i + 1) % slot.size(); } return false; }
};
struct Chain {
    std::vector<std::vector<std::uint64_t>> b; explicit Chain(std::size_t m) : b(m) {}
    bool insert(std::uint64_t k) { auto& c = b[k % b.size()]; if (std::find(c.begin(), c.end(), k) != c.end()) return false; c.push_back(k); return true; }
    bool erase(std::uint64_t k) { auto& c = b[k % b.size()]; auto it = std::find(c.begin(), c.end(), k); if (it == c.end()) return false; *it = c.back(); c.pop_back(); return true; }
    bool contains(std::uint64_t k) const { auto& c = b[k % b.size()]; return std::find(c.begin(), c.end(), k) != c.end(); }
};

int main() {
    std::mt19937_64 rng(4);
    // ① 체이닝: 무작위 삽입·삭제·검색 10 만 번
    {   Chain c(53); std::unordered_map<std::uint64_t, int> ref;
        for (int i = 0; i < 100000; ++i) { std::uint64_t k = 1 + rng() % 400; int op = (int)(rng() % 3);
            if (op == 0) { bool r = ref.emplace(k, 1).second; assert(c.insert(k) == r); } else if (op == 1) { bool r = ref.erase(k) > 0; assert(c.erase(k) == r); } else assert(c.contains(k) == (ref.count(k) > 0)); }
    }
    // ② 선형 탐사 + 뒤로 당기기: 표가 꽤 차 있는 상태(α ≈ 0.7)를 유지하며 20 만 번, 매 100 번마다 불변식 검사
    {   Open t(1009); std::unordered_map<std::uint64_t, int> ref; long erased = 0;
        for (int i = 0; i < 200000; ++i) {
            std::uint64_t k = 1 + rng() % 1500; int op = (int)(rng() % 3);
            if (op == 0 && ref.size() < 700) { bool r = ref.emplace(k, 1).second; assert(t.insert(k) == r); } else if (op == 1) { bool r = ref.erase(k) > 0; erased += r; assert(t.erase(k) == r); } else assert(t.contains(k) == (ref.count(k) > 0));
            if (i % 100 == 0) assert(t.invariant() && t.n == ref.size());
        }
        for (auto& kv : ref) assert(t.contains(kv.first)); assert(erased > 20000);
    }
    // ③ 묘비 방식도 같은 결과
    {   Tomb t(1009); std::unordered_map<std::uint64_t, int> ref;
        for (int i = 0; i < 100000; ++i) { std::uint64_t k = 2 + rng() % 1500; int op = (int)(rng() % 3);
            if (op == 0 && ref.size() < 600) { bool r = ref.emplace(k, 1).second; assert(t.insert(k) == r); } else if (op == 1) { bool r = ref.erase(k) > 0; assert(t.erase(k) == r); } else assert(t.contains(k) == (ref.count(k) > 0)); }
    }
    // ④ 반례: 칸을 그냥 비우면 그 칸을 지나쳐 저장된 키가 검색에서 사라진다
    {   long lostTotal = 0;
        for (int trial = 0; trial < 200; ++trial) {
            Open t(101); std::vector<std::uint64_t> keys; while (keys.size() < 80) { std::uint64_t k = 1 + rng() % 100000; if (t.insert(k)) keys.push_back(k); }
            for (int d = 0; d < 20; ++d) { std::size_t idx = rng() % keys.size(); t.eraseNaive(keys[idx]); keys.erase(keys.begin() + (long)idx); }
            for (std::uint64_t k : keys) lostTotal += !t.contains(k);
        }
        assert(lostTotal > 100);
        std::cout << "Delete: chaining deletion and linear-probing backward-shift deletion (Knuth's Algorithm R) matched std::unordered_map over hundreds of thousands of random operations while the cluster invariant held every 100 steps, tombstone deletion agreed too, and simply blanking a slot lost " << lostTotal << " stored keys in 200 trials" << std::endl; }
    return 0;
}
// Time Complexity: 평균 O(1 + α), 최악 O(n)
// Space Complexity: O(1)
```
## Resize()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

// 크기 조정(Resize): 적재율 α = n/m 이 문턱을 넘으면 버킷 수를 늘리고 모든 항목을 새 표에 다시 넣는다(rehash). 한 번의 확장은 O(n) 이지만 *늘리는 비율이 일정(예: 2 배)* 이면 n 번 삽입하는 동안 옮긴 항목의 총합이 2n 미만이라 삽입 하나당 분할상환 O(1) 이다 — 확장 시점의 크기가 n₀·2^k 이므로 합이 등비급수 (1 + 2 + 4 + … ) < 2n. *일정한 크기만큼* 더하는 방식(+16)은 합이 n²/32 라 이차 시간이다.
// 한 번에 O(n) 이 일어나는 꼬리 지연이 문제라면 *점진적 재구성(incremental rehash)* — 옛 표와 새 표를 함께 두고 연산마다 옛 버킷 k 개를 새 표로 옮긴다(Redis 가 이 방식). 검색은 두 표를 모두 보고, 삽입은 새 표에만 한다. 연산당 일이 상수로 묶이면서 최종 내용은 같다.
// 검증: ① 증가 비율별 총 이동 수 — 2 배: 정확히 마지막 확장 전까지의 크기 합 < 2n, 1.5 배: < 3n, +16: n²/32 근처(100 배 이상 큼) ② 확장 중에도 모든 내용 보존(무작위 삽입 10 만 번을 unordered_map 과 비교) ③ 점진적 재구성에서 연산당 이동한 버킷 수가 k 를 넘지 않고 각 시점에 검색이 맞음, 끝나면 옛 표가 비어 있음 ④ 적재율은 확장 직후 문턱의 절반 이하로 떨어졌다가 다시 오른다.
struct Growing {
    using Entry = std::pair<std::uint64_t, int>;
    std::vector<std::vector<Entry>> b; std::size_t n = 0; double threshold; double factor; long add; long moved = 0; int resizes = 0; double minAlphaAfter = 1e9;
    Growing(std::size_t m, double thr, double f, long a) : b(m), threshold(thr), factor(f), add(a) {}
    static std::size_t h(std::uint64_t k, std::size_t m) { k += 0x9e3779b97f4a7c15ULL; k = (k ^ (k >> 30)) * 0xbf58476d1ce4e5b9ULL; k = (k ^ (k >> 27)) * 0x94d049bb133111ebULL; return (std::size_t)((k ^ (k >> 31)) % m); }
    void rehash(std::size_t newM) { std::vector<std::vector<Entry>> nb(newM); for (auto& c : b) for (Entry& e : c) { nb[h(e.first, newM)].push_back(e); ++moved; } b.swap(nb); ++resizes; minAlphaAfter = std::min(minAlphaAfter, (double)n / (double)newM); }
    void put(std::uint64_t k, int v) {
        for (Entry& e : b[h(k, b.size())]) if (e.first == k) { e.second = v; return; }
        b[h(k, b.size())].push_back({k, v}); ++n;
        if ((double)n / (double)b.size() > threshold) rehash(add ? b.size() + (std::size_t)add : (std::size_t)((double)b.size() * factor) + 1);
    }
    const int* get(std::uint64_t k) const { for (const Entry& e : b[h(k, b.size())]) if (e.first == k) return &e.second; return nullptr; }
};
// 점진적 재구성: 옛 표 old 와 새 표 cur 를 함께 둔다
struct Incremental {
    using Entry = std::pair<std::uint64_t, int>;
    std::vector<std::vector<Entry>> cur, old; std::size_t n = 0, nextOld = 0; int stepsPerOp; long maxMovedPerOp = 0;
    explicit Incremental(std::size_t m, int k) : cur(m), stepsPerOp(k) {}
    static std::size_t h(std::uint64_t k, std::size_t m) { return Growing::h(k, m); }
    bool migrating() const { return !old.empty(); }
    void migrateSome() {
        long moved = 0;
        for (int s = 0; s < stepsPerOp && migrating(); ++s) {
            for (Entry& e : old[nextOld]) { cur[h(e.first, cur.size())].push_back(e); ++moved; } old[nextOld].clear();
            if (++nextOld == old.size()) { old.clear(); old.shrink_to_fit(); nextOld = 0; }
        }
        maxMovedPerOp = std::max(maxMovedPerOp, moved);
    }
    const int* get(std::uint64_t k) const {
        for (const Entry& e : cur[h(k, cur.size())]) if (e.first == k) return &e.second;
        if (migrating()) { for (const Entry& e : old[h(k, old.size())]) if (e.first == k) return &e.second; }
        return nullptr;
    }
    void put(std::uint64_t k, int v) {
        migrateSome();
        if (migrating()) { auto& oc = old[h(k, old.size())]; for (Entry& e : oc) if (e.first == k) { e.second = v; return; } }           // 아직 옛 표에 있으면 거기서 갱신
        auto& c = cur[h(k, cur.size())]; for (Entry& e : c) if (e.first == k) { e.second = v; return; }
        c.push_back({k, v}); ++n;
        if (!migrating() && (double)n / (double)cur.size() > 0.75) { old.swap(cur); cur.assign(old.size() * 2, {}); nextOld = 0; }      // 2 배 새 표를 만들고 옛 표를 서서히 비운다
    }
};

int main() {
    const std::size_t N = 8000; std::mt19937_64 rng(7);
    // ① 증가 방식별 총 이동 수 (상수 증가 +16 은 이차라 n = 8,000 으로도 충분히 크게 드러난다)
    auto run = [&](double f, long add) { Growing g(8, 0.75, f, add); for (std::size_t i = 0; i < N; ++i) g.put(i * 7919 + 1, 1); return g; };
    Growing dbl = run(2.0, 0), mid = run(1.5, 0), lin = run(0.0, 16);
    assert(dbl.moved < 2 * (long)N && mid.moved < 3 * (long)N && lin.moved > 100 * dbl.moved);      // 등비 증가는 분할상환 O(1), 상수 증가는 이차
    assert(dbl.n == N && mid.n == N && lin.n == N && dbl.resizes < 20);
    // 2 배의 정확한 합: 확장 시점마다 그때의 원소 수가 이동 → 합은 등비수열
    {   Growing g(8, 0.75, 2.0, 0); long expect = 0; std::size_t m = 8; std::size_t nn = 0; for (std::size_t i = 0; i < N; ++i) { g.put(i + 1, 1); ++nn; if ((double)nn / (double)m > 0.75) { expect += (long)nn; m = (std::size_t)((double)m * 2.0) + 1; } } assert(g.moved == expect); }
    // ② 확장 중에도 내용 보존: 무작위 삽입(갱신 포함) 10 만 번을 unordered_map 과 비교, 확장 직후 적재율은 문턱보다 훨씬 낮다
    {   Growing g(4, 0.75, 2.0, 0); std::unordered_map<std::uint64_t, int> ref;
        for (int i = 0; i < 100000; ++i) { std::uint64_t k = rng() % 60000; int v = (int)(rng() % 1000); g.put(k, v); ref[k] = v; }
        assert(g.n == ref.size()); for (auto& [k, v] : ref) { const int* p = g.get(k); assert(p && *p == v); } assert(g.minAlphaAfter < 0.4 && (double)g.n / (double)g.b.size() <= 0.75 + 1e-9); }
    // ③ 점진적 재구성: 연산당 이동한 버킷은 stepsPerOp 개 이하(→ 한 연산이 훑는 항목 수가 한 번에 O(n) 이 되지 않는다), 모든 시점에서 검색이 맞음
    {   Incremental t(8, 2); std::unordered_map<std::uint64_t, int> ref; int sawMigrating = 0;
        for (int i = 0; i < 100000; ++i) {
            std::uint64_t k = rng() % 40000; int v = (int)(rng() % 1000); t.put(k, v); ref[k] = v; sawMigrating += t.migrating();
            if (i % 997 == 0) for (int probe = 0; probe < 50; ++probe) { std::uint64_t q = rng() % 40000; const int* p = t.get(q); auto it = ref.find(q); assert((p != nullptr) == (it != ref.end())); if (p) assert(*p == it->second); }
        }
        while (t.migrating()) t.migrateSome();
        assert(t.old.empty() && t.n == ref.size() && sawMigrating > 1000);
        for (auto& [k, v] : ref) { const int* p = t.get(k); assert(p && *p == v); }
        assert(t.maxMovedPerOp < 200);                                                                      // 버킷 2 개 분량 (적재율 ≤ 0.75 라 평균 두세 개씩)
        std::cout << "Resize: total moved entries for 8,000 inserts were " << dbl.moved << " when doubling (< 2n), " << mid.moved << " at x1.5 (< 3n) and " << lin.moved << " when growing by a constant 16 (over 100 times worse); growth preserved every entry through " << dbl.resizes << " rehashes, and incremental rehashing kept the per-operation migration to at most " << t.maxMovedPerOp << " entries while lookups stayed correct throughout" << std::endl; }
    return 0;
}
// Time Complexity: 삽입 분할상환 O(1), 확장 1회는 O(n)
// Space Complexity: O(n)
```
## Rehash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 해시 함수(시드)를 바꾸면 모든 키의 위치가 달라지므로 전부 다시 계산해야 한다.  버킷 수만 바꾸는 것(크기 조정)과 시드를 바꾸는 것(해시 플러딩 방어)은 다른 일이다:
// 공격자가 한 버킷에 몰리는 키를 만들었을 때, 테이블을 두 배로 키워도 (같은 시드면) 절반씩 몰려 있고, 시드를 바꿔야 흩어진다
// 한꺼번에 다시 해시하면 한 번의 삽입이 n 개 키를 옮기는 긴 멈춤이 되므로, Redis 의 dict 처럼 두 테이블을 두고 연산마다 버킷 하나씩 옮기는 *점진적 재해시* 도 둔다
// 검증: ① 손으로 짠 예  ② 사슬 테이블을 std::map 과 20 000 번 대조(삽입·갱신·삭제·조회·무작위 재해시)하고 버킷 점유 합 = 키 수  ③ 해시 플러딩: 한 버킷에 300 개를 몰아넣은 뒤 같은 시드로 두 배 확장하면 여전히 100 개 이상이 몰리고,
//        시드를 바꾸면 최대 사슬이 16 이하  ④ 점진적 재해시를 std::map 과 40 000 번 대조: 재해시가 끝난 횟수, 진행 중에도 모든 키가 정확히 한 번씩, 한 연산이 옮긴 키 수의 최댓값이 전체 재해시(n 개)보다 훨씬 작음
typedef std::vector<std::pair<std::string, int>> Chain;
uint32_t mix32(uint32_t x) { x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16; return x; }                    // 비트를 고르게 섞는 가역 함수
uint32_t seededFnv(const std::string& k, uint32_t seed) { uint32_t x = 2166136261u; for (unsigned char c : k) { x ^= c; x *= 16777619u; } return mix32(x ^ seed); }     // FNV-1a 결과에 시드를 섞은 뒤 한 번 더 섞는다
// 주의: 시드를 FNV 의 시작값에 넣는 것만으로는 부족하다 — 2^k 개 버킷이면 하위 k 비트가 키 바이트의 하위 k 비트와 시드의 하위 k 비트에만 의존해, 시드를 바꿔도 충돌이 상당수 남는다.
// 그래도 FNV 의 32 비트 값 *전체* 가 충돌하는 키(찾기 쉽다)는 어떤 시드로도 못 막는다 — 실제 해시 플러딩 방어는 SipHash 같은 키 있는 해시를 쓴다
class ChainedTable {
    std::vector<Chain> b; uint32_t seed; size_t n = 0;
public:
    ChainedTable(size_t m, uint32_t s) : b(m), seed(s) {}
    size_t bucketOf(const std::string& k) const { return seededFnv(k, seed) % b.size(); }
    void insert(const std::string& k, int v) {                               // 있으면 값만 갱신
        Chain& c = b[bucketOf(k)]; for (auto& kv : c) if (kv.first == k) { kv.second = v; return; }
        c.emplace_back(k, v); ++n;
    }
    bool erase(const std::string& k) { Chain& c = b[bucketOf(k)]; for (size_t i = 0; i < c.size(); i++) if (c[i].first == k) { c[i] = c.back(); c.pop_back(); --n; return true; } return false; }
    const int* find(const std::string& k) const { for (auto& kv : b[bucketOf(k)]) if (kv.first == k) return &kv.second; return nullptr; }
    bool contains(const std::string& k) const { return find(k) != nullptr; }
    size_t rehash(size_t newBuckets, uint32_t newSeed) {                      // 옮긴 키 수를 돌려준다
        std::vector<std::pair<std::string, int>> all;
        for (auto& chain : b) for (auto& kv : chain) all.push_back(kv);
        b.assign(newBuckets, {});
        seed = newSeed;
        for (auto& kv : all) b[bucketOf(kv.first)].push_back(kv);
        return all.size();
    }
    size_t maxChain() const { size_t m = 0; for (auto& c : b) m = std::max(m, c.size()); return m; }
    size_t size() const { return n; }
    size_t buckets() const { return b.size(); }
    size_t occupancy() const { size_t s = 0; for (auto& c : b) s += c.size(); return s; }
    std::map<std::string, int> contents() const { std::map<std::string, int> m; for (auto& c : b) for (auto& kv : c) m[kv.first] = kv.second; return m; }
};
class IncrementalTable {                                                  // 두 테이블 + 진행 위치: 연산마다 t0 의 버킷 하나를 t1 으로 옮긴다
    std::vector<Chain> t0, t1; long idx = -1; size_t n = 0; uint32_t seed;
    size_t maxMoved_ = 0, finished_ = 0;
    static size_t at(const std::string& k, uint32_t seed, size_t m) { return seededFnv(k, seed) % m; }
    void step() {
        if (idx < 0) return;
        Chain& c = t0[idx]; maxMoved_ = std::max(maxMoved_, c.size());
        for (auto& kv : c) t1[at(kv.first, seed, t1.size())].push_back(kv);
        c.clear(); ++idx;
        if ((size_t)idx == t0.size()) { t0.swap(t1); t1.clear(); idx = -1; ++finished_; }
    }
    int* locate(const std::string& k) {
        for (auto& kv : t0[at(k, seed, t0.size())]) if (kv.first == k) return &kv.second;
        if (idx >= 0) for (auto& kv : t1[at(k, seed, t1.size())]) if (kv.first == k) return &kv.second;
        return nullptr;
    }
public:
    explicit IncrementalTable(size_t m, uint32_t s) : t0(m), seed(s) {}
    void insert(const std::string& k, int v) {
        step(); if (int* p = locate(k)) { *p = v; return; }
        std::vector<Chain>& target = idx >= 0 ? t1 : t0; target[at(k, seed, target.size())].emplace_back(k, v); ++n;
        if (idx < 0 && n > t0.size()) { t1.assign(t0.size() * 2, {}); idx = 0; }                            // 부하율 1 을 넘으면 두 배로
    }
    bool erase(const std::string& k) {
        step();
        for (std::vector<Chain>* t : {&t0, &t1}) { if (t->empty()) continue; Chain& c = (*t)[at(k, seed, t->size())]; for (size_t i = 0; i < c.size(); i++) if (c[i].first == k) { c[i] = c.back(); c.pop_back(); --n; return true; } }
        return false;
    }
    const int* find(const std::string& k) { return locate(k); }
    size_t size() const { return n; }
    bool rehashing() const { return idx >= 0; }
    size_t maxMoved() const { return maxMoved_; }
    size_t finished() const { return finished_; }
    size_t held() const { size_t s = 0; for (auto& c : t0) s += c.size(); for (auto& c : t1) s += c.size(); return s; }
    std::map<std::string, int> contents() const { std::map<std::string, int> m; for (auto* t : {&t0, &t1}) for (auto& c : *t) for (auto& kv : c) { assert(!m.count(kv.first)); m[kv.first] = kv.second; } return m; }       // 키가 두 테이블에 중복되면 안 된다
};

int main() {
    ChainedTable t(4, 1);
    for (int i = 0; i < 40; i++) t.insert("k" + std::to_string(i), i);
    size_t before = t.maxChain();
    assert(t.rehash(64, 99) == 40);                                    // 버킷 수와 해시 함수를 동시에 교체
    for (int i = 0; i < 40; i++) assert(t.contains("k" + std::to_string(i)) && *t.find("k" + std::to_string(i)) == i);
    assert(t.maxChain() <= before && t.size() == 40 && t.occupancy() == 40);
    ChainedTable one(8, 5); assert(one.rehash(1, 6) == 0 && one.maxChain() == 0 && !one.contains("x")); one.insert("x", 1); one.rehash(1, 7); assert(one.maxChain() == 1 && *one.find("x") == 1);      // 경계: 빈 테이블, 버킷 1 개
    // ② std::map 대조
    std::mt19937 rng(77); ChainedTable ct(8, 3); std::map<std::string, int> model; long rehashes = 0;
    for (int step = 0; step < 20000; ++step) {
        std::string k = "key" + std::to_string(rng() % 300); int op = (int)(rng() % 20);
        if (op < 9) { ct.insert(k, step); model[k] = step; }
        else if (op < 14) { assert(ct.erase(k) == (model.erase(k) > 0)); }
        else if (op < 19) { const int* p = ct.find(k); auto it = model.find(k); assert((p != nullptr) == (it != model.end()) && (!p || *p == it->second)); }
        else { size_t nb = 1 + rng() % 200; assert(ct.rehash(nb, (uint32_t)rng()) == model.size()); ++rehashes; }
        assert(ct.size() == model.size() && ct.occupancy() == model.size());
    }
    assert(ct.contents() == model && rehashes > 500);
    // ③ 해시 플러딩
    const uint32_t S1 = 1, S2 = 987654321; ChainedTable atk(64, S1); std::vector<std::string> evil;
    for (int i = 0; evil.size() < 300; ++i) { std::string k = "user" + std::to_string(i); if (atk.bucketOf(k) == 0) evil.push_back(k); }      // 시드 S1 에서 0 번 버킷에 떨어지는 키만 모은다
    for (auto& k : evil) atk.insert(k, 1);
    assert(atk.maxChain() == 300);                                                                                 // 한 사슬에 300 개: 조회가 O(n)
    ChainedTable grown = atk; grown.rehash(128, S1);                                                               // 같은 시드로 두 배: 절반씩만 갈라진다
    assert(grown.maxChain() >= 100 && grown.maxChain() < 300);
    ChainedTable reseeded = atk; reseeded.rehash(64, S2);                                                          // 시드를 바꾸면 흩어진다
    assert(reseeded.maxChain() <= 16 && reseeded.size() == 300);
    // ④ 점진적 재해시
    IncrementalTable it(4, 11); std::map<std::string, int> m2; long maxHeldDuringRehash = 0; long duringRehashOps = 0;
    for (int step = 0; step < 40000; ++step) {
        std::string k = "key" + std::to_string(rng() % (step < 20000 ? 5000 : 300)); int op = (int)(rng() % 10);               // 앞 절반은 키 5000 종류(계속 커짐), 뒤 절반은 300 종류(지우고 넣기)
        if (op < 6) { it.insert(k, step); m2[k] = step; } else if (op < 8) { assert(it.erase(k) == (m2.erase(k) > 0)); } else { const int* p = it.find(k); auto f = m2.find(k); assert((p != nullptr) == (f != m2.end()) && (!p || *p == f->second)); }
        assert(it.size() == m2.size() && it.held() == m2.size());                                                 // 진행 중에도 키가 하나도 사라지거나 중복되지 않는다
        if (it.rehashing()) { ++duringRehashOps; maxHeldDuringRehash = std::max<long>(maxHeldDuringRehash, (long)it.held()); }
        if (step % 997 == 0) assert(it.contents() == m2);
    }
    assert(it.contents() == m2 && it.finished() >= 5 && duringRehashOps > 1000);
    ChainedTable full(1024, 3); for (int i = 0; i < 20000; i++) full.insert("n" + std::to_string(i), i);
    size_t fullMoved = full.rehash(2048, 4);                           // 한꺼번에: 한 번의 호출이 20 000 개를 옮긴다
    assert(fullMoved == 20000 && it.maxMoved() < 30 && it.maxMoved() * 100 < fullMoved);
    std::cout << "Rehash: maxChain " << before << " -> " << t.maxChain() << "; flooding chain 300 -> " << grown.maxChain() << " (resize only) / " << reseeded.maxChain() << " (new seed); incremental rehash finished " << it.finished() << " times moving at most " << it.maxMoved() << " keys per operation vs " << fullMoved << " at once" << std::endl;
    return 0;
}
// Time Complexity: 한꺼번에 O(n), 점진적이면 연산당 O(최대 사슬 길이)
// Space Complexity: O(n) (점진적일 때 재해시 중에는 두 테이블)
```
## LoadFactor()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 적재율 α = n / m 이 해시 테이블의 성능을 거의 전부 결정한다. 키가 균등하게 흩어진다는 가정에서 평균 탐사(probe) 횟수의 이론값 — 체이닝: 성공 1 + α/2, 실패 α(+1 버킷 확인). 선형 탐사: 성공 ½(1 + 1/(1−α)), 실패 ½(1 + 1/(1−α)²) — α → 1 에서 제곱으로 폭발. 균등 해싱(이중 해싱의 이상형): 성공 (1/α)·ln(1/(1−α)), 실패 1/(1−α).
// 그래서 개방 주소법은 α 를 0.5~0.75 로 묶고 체이닝도 1 안팎에서 확장한다. 아래 시뮬레이션은 소수 크기 m = 100,003 에서 α 를 0.3, 0.5, 0.7, 0.9 로 채워 *실제 평균 탐사 수를 세어* 이론값과 비교한다(결정적 시드). 선형 탐사의 이론값은 m → ∞ 에서의 근사식이라 α = 0.9 에서는 표가 한 번 만들어질 때의 변동이 커서 ±15%, 나머지는 ±4% 이내여야 통과(실측: 0.9 에서 실패 43.95 대 이론 50.5, 성공 5.18 대 5.5).
// 추가로 이론식의 성질도 확인한다: 단조 증가, 선형 탐사의 실패 비용 > 성공 비용, 균등 해싱 < 선형 탐사(군집 때문), α = 0.5 에서 선형 탐사 실패 비용 2.5 번, α = 0.9 에서 50.5 번.
struct Theory {
    static double chainSuccess(double a) { return 1 + a / 2; }
    static double chainFail(double a) { return a; }
    static double linearSuccess(double a) { return 0.5 * (1 + 1 / (1 - a)); }
    static double linearFail(double a) { return 0.5 * (1 + 1 / ((1 - a) * (1 - a))); }
    static double uniformSuccess(double a) { return std::log(1 / (1 - a)) / a; }
    static double uniformFail(double a) { return 1 / (1 - a); }
};
std::uint64_t mix(std::uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }

int main() {
    // ① 이론식의 성질
    assert(std::abs(Theory::linearFail(0.5) - 2.5) < 1e-12 && std::abs(Theory::linearFail(0.9) - 50.5) < 1e-9 && std::abs(Theory::linearSuccess(0.5) - 1.5) < 1e-12);
    for (double a = 0.05; a < 0.95; a += 0.05) {
        assert(Theory::linearFail(a) > Theory::linearSuccess(a) && Theory::linearSuccess(a) > Theory::uniformSuccess(a) && Theory::linearFail(a) > Theory::uniformFail(a));          // 실패가 더 비싸고, 군집 때문에 선형이 균등보다 나쁘다
        assert(Theory::linearFail(a + 0.04) > Theory::linearFail(a) && Theory::uniformFail(a + 0.04) > Theory::uniformFail(a) && Theory::chainSuccess(a + 0.04) > Theory::chainSuccess(a));    // 단조 증가
    }
    // ② 시뮬레이션: 선형 탐사 표를 α 까지 채우고 성공/실패 탐사 수를 센다
    const std::size_t m = 100003; std::mt19937_64 rng(8);
    for (double alpha : {0.3, 0.5, 0.7, 0.9}) {
        std::size_t n = (std::size_t)(alpha * (double)m); std::vector<std::uint64_t> slot(m, 0), stored; stored.reserve(n); std::unordered_set<std::uint64_t> seen;
        while (stored.size() < n) { std::uint64_t k = rng() | 1; if (!seen.insert(k).second) continue; std::size_t i = mix(k) % m; while (slot[i]) i = (i + 1) % m; slot[i] = k; stored.push_back(k); }
        long succProbes = 0; for (std::uint64_t k : stored) { std::size_t i = mix(k) % m; long p = 1; while (slot[i] != k) { i = (i + 1) % m; ++p; } succProbes += p; }
        long failProbes = 0; const int trials = 200000; for (int t = 0; t < trials; ++t) { std::uint64_t k = rng() & ~1ULL; std::size_t i = mix(k) % m; long p = 1; while (slot[i]) { i = (i + 1) % m; ++p; } failProbes += p; }       // 짝수 키는 저장된 적 없음 → 실패 탐색
        double succ = (double)succProbes / (double)n, fail = (double)failProbes / trials; double tol = alpha > 0.85 ? 0.15 : 0.04;
        assert(std::abs(succ - Theory::linearSuccess(alpha)) < tol * Theory::linearSuccess(alpha) && std::abs(fail - Theory::linearFail(alpha)) < tol * Theory::linearFail(alpha));
        // 체이닝: 평균 체인 길이 = α, 성공 검색 평균 비교 수 ≈ 1 + α/2
        std::vector<int> len(m, 0); for (std::uint64_t k : stored) ++len[mix(k) % m]; double totalLen = 0, sumPairs = 0; for (int l : len) { totalLen += l; sumPairs += (double)l * (l + 1) / 2.0; }
        assert(std::abs(totalLen / (double)m - alpha) < 1e-3 && std::abs(sumPairs / (double)n - Theory::chainSuccess(alpha)) < 0.03 * Theory::chainSuccess(alpha));
        std::cout << "LoadFactor alpha=" << alpha << ": linear probing successful " << succ << " (theory " << Theory::linearSuccess(alpha) << "), unsuccessful " << fail << " (theory " << Theory::linearFail(alpha) << ")" << std::endl;
    }
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
# Part 2. 해시 함수
## DivisionMethod()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 나눗셈법: h(k) = k mod m. 가장 단순하지만 *m 을 어떻게 고르느냐* 가 분포를 좌우한다. 정리(아래에서 모든 m ≤ 200, d ≤ 64 로 확인): 키가 모두 d 의 배수이면 사용되는 버킷은 정확히 m / gcd(m, d) 개다 — m 이 2의 거듭제곱이고 키가 8의 배수면 버킷의 7/8 이 비고, m 이 d 와 서로소(특히 소수)면 모든 버킷이 쓰인다. 그래서 소수 m 을 권장한다. 단, 2의 거듭제곱에 *가까운* 수도 피한다: m = 2^p − 1 이면 k mod m 은 k 의 2^p 진 자릿수의 *합* mod m 이라(2^p ≡ 1) 자릿수를 섞은 키(바이트 순서를 바꾼 것)가 전부 충돌한다.
// 음수 키: C++ 의 % 는 부호를 따라가므로 -7 % 5 == -2 → 버킷 번호로 쓰면 범위 밖. ((k % m) + m) % m 로 보정한다(INT_MIN 도 안전하게 64비트로 올려서). 연속한 키는 라운드 로빈으로 퍼져 버킷 수가 정확히 균등(차이 ≤ 1).
// 검증: ① 키가 d 의 배수일 때 사용 버킷 수 = m / gcd(m, d), 모든 m ≤ 200 · d ≤ 64 ② 바이트 쌍 (a, b) 에서 바이트를 바꾼 키와의 충돌: m = 255 는 a ≠ b 인 65,280 쌍이 전부, 소수 m = 251 은 거의 없음 ③ 음수를 포함한 무작위 키의 번호가 [0, m) ④ 연속한 N 개 키의 버킷 부하 차이 ≤ 1 ⑤ 무작위 키에서 소수/2의 거듭제곱 m 모두 균등(카이제곱 통계가 자유도 ± 5σ 이내).
__extension__ typedef __int128 i128;
long long bucket(long long k, long long m) { return ((k % m) + m) % m; }

int main() {
    // ① 사용 버킷 수 = m / gcd(m, d)
    for (int m = 1; m <= 200; ++m) for (int d = 1; d <= 64; ++d) {
        std::vector<char> used(m, 0); for (long long i = 0; i < 2000; ++i) used[bucket(i * d, m)] = 1;
        assert(std::count(used.begin(), used.end(), 1) == m / std::gcd(m, d));
    }
    // ② 바이트를 바꾼 키: m = 255 (= 2^8 − 1) 에서는 (a·256 + b) mod 255 = (a + b) mod 255 라 a ≠ b 인 모든 쌍이 충돌
    long collide255 = 0, collide251 = 0;
    for (int a = 0; a < 256; ++a) for (int b = 0; b < 256; ++b) if (a != b) { long long k1 = a * 256 + b, k2 = b * 256 + a; collide255 += bucket(k1, 255) == bucket(k2, 255); collide251 += bucket(k1, 251) == bucket(k2, 251); }
    assert(collide255 == 65280 && collide251 < 1500);                                  // 소수 251: a ≡ b (mod 251) 일 때만 (4(a−b) ≡ 0 mod 251 → a − b ∈ {0, ±251})
    // ③ 음수 키 · 극단값
    { long long vals[] = {0, 1, -1, -7, 7, LLONG_MIN, LLONG_MAX, -1000003, 1000003}; for (long long m : {1LL, 2LL, 5LL, 64LL, 1009LL, 1000003LL}) for (long long k : vals) { long long b = bucket(k, m); assert(b >= 0 && b < m); assert(((i128)b - (i128)k) % m == 0); } assert(bucket(-7, 5) == 3 && (-7 % 5) == -2); }
    // ④ 연속 키 N 개 → 버킷 부하 차이 ≤ 1
    for (int m : {7, 64, 101, 1000}) for (int N : {1, 50, 1000, 12345}) { std::vector<int> load(m, 0); for (int k = 0; k < N; ++k) ++load[bucket(k, m)]; assert(*std::max_element(load.begin(), load.end()) - *std::min_element(load.begin(), load.end()) <= 1); }
    // ⑤ 무작위 키의 균등성 (카이제곱): 자유도 m−1, 평균 m−1, 표준편차 √(2(m−1)) 의 5σ 안
    {   std::mt19937_64 rng(1); const int n = 400000; for (int m : {1021, 1024}) { std::vector<int> load(m, 0); for (int i = 0; i < n; ++i) ++load[bucket((long long)(rng() >> 1), m)]; double chi = 0, e = (double)n / m; for (int c : load) chi += (c - e) * (c - e) / e; assert(std::abs(chi - (m - 1)) < 5 * std::sqrt(2.0 * (m - 1))); } }
    std::cout << "DivisionMethod: the number of buckets used by keys that are multiples of d was exactly m/gcd(m,d) for all m <= 200 and d <= 64, byte-swapped keys collided for all 65,280 pairs with m = 255 but only " << collide251 << " times with the prime 251, negative and extreme keys were mapped into [0, m), consecutive keys filled buckets with loads differing by at most 1, and random keys were uniform for both a prime and a power-of-two modulus" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MultiplicationMethod()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 곱셈법: h(k) = ⌊m · frac(k · A)⌋, A ≈ (√5 − 1)/2 = 0.6180339887… (Knuth 의 황금비 상수). m 이 2의 거듭제곱 2^p 이면 32비트 고정소수점 곱 한 번과 시프트로 끝난다: h(k) = (k · 2654435769) >> (32 − p) — 2654435769 = ⌊A·2^32⌋ (Fibonacci hashing). 나눗셈법과 달리 m 은 아무 값이나 되고 키의 규칙적인 패턴(8의 배수)도 높은 비트로 고르게 섞인다.
// 왜 황금비인가 — 세 간격 정리(three-distance theorem): 점 {k·A}, k = 1..N 을 원 위에 놓으면 이웃 점 사이 간격은 *최대 세 가지 값* 뿐이고, A 가 황금비일 때 그 값들의 비가 가장 고르게 유지된다(연분수 전개가 모두 1). 그래서 연속한 키가 버킷 전체에 거의 균등하게 흩어진다.
// 검증: ① 정수 구현이 *정확한 유리수 계산* ⌊2^p · frac(k · 2654435769 / 2^32)⌋ 와 모든 k (무작위 100 만 개)·p 에서 같고, 실수 A 로 계산한 값과는 k < 4096, p ≤ 8 에서 99.9% 이상 같음(A32 가 A 를 2^-32 만큼 자른 값이라 k 가 커지면 오차 k·2^-32 가 쌓여 달라지지만, 정수 구현이 *정의* 이므로 문제 없고 부동소수 `k * 0.618…` 보다 정확) ② 세 간격 정리: k = 1..N (N ≤ 3000) 의 고정소수점 점들의 간격 종류 ≤ 3 ③ 연속한 키 N 개를 2^p 버킷에 넣으면 부하 차이가 2 + log₂(N)/4 이하(불일치도는 O(log N), 실측 최대 4) ④ 키가 모두 64 의 배수일 때 나눗셈법(m = 1024) 은 16 개 버킷만 쓰지만 곱셈법은 1024 개를 모두 쓰고 최대 부하가 이상값 97.7 에 가깝다(99) ⑤ 균등성(카이제곱).
const std::uint32_t A32 = 2654435769u;
std::uint32_t fib(std::uint32_t k, int p) { return (std::uint32_t)(k * A32) >> (32 - p); }

int main() {
    std::mt19937 rng(2);
    // ① 정확한 유리수 계산과 일치 / 실수 A 와 거의 일치
    long mismatchReal = 0, smallTrials = 0; const int trials = 1000000;
    for (int t = 0; t < trials; ++t) {
        std::uint32_t k = rng(); int p = 1 + (int)(rng() % 31);
        std::uint64_t num = (std::uint64_t)k * A32; std::uint64_t frac32 = num & 0xffffffffu;                                // k·A32 의 소수부 × 2^32 를 64비트 정수 곱으로 (오버플로 없음)
        std::uint32_t exact = (std::uint32_t)(frac32 >> (32 - p)); assert(fib(k, p) == exact);
    }
    for (int t = 0; t < 200000; ++t) {                                                  // 작은 키 · 작은 p 에서는 실수 황금비 A 로 계산한 값과 거의 같다
        std::uint32_t k = rng() % 4096; int p = 1 + (int)(rng() % 8); long double A = (std::sqrt(5.0L) - 1) / 2; long double fr = k * A - std::floor(k * A);
        std::uint32_t viaReal = (std::uint32_t)std::floor((long double)(1ULL << p) * fr); mismatchReal += viaReal != fib(k, p); ++smallTrials;
    }
    assert(smallTrials > 1000 && mismatchReal * 1000 < smallTrials);                       // k 가 작으면 실수 A 와 거의 같다 (k·2^-32 만큼의 반올림 차이가 버킷 경계를 넘을 때만 다름)
    // ② 세 간격 정리: 점들을 정렬해 인접 간격(원 위, 마지막→처음 포함)의 종류를 센다
    for (int N : {2, 3, 5, 8, 13, 21, 100, 500, 1000, 3000}) {
        std::vector<std::uint32_t> pts; for (int k = 1; k <= N; ++k) pts.push_back(k * A32); std::sort(pts.begin(), pts.end());
        std::set<std::uint32_t> gaps; for (std::size_t i = 0; i < pts.size(); ++i) gaps.insert(pts[(i + 1) % pts.size()] - pts[i]);       // 부호 없는 32비트 뺄셈이 원 위의 거리
        assert(gaps.size() <= 3);
    }
    // ③ 연속한 키 → 2^p 버킷 부하 차이
    for (int p : {4, 8, 10}) for (int N : {100, 1000, 12345, 100000}) { std::vector<int> load(1 << p, 0); for (int k = 0; k < N; ++k) ++load[fib(k, p)]; assert(*std::max_element(load.begin(), load.end()) - *std::min_element(load.begin(), load.end()) <= 2 + (int)std::log2((double)N) / 4); }      // 불일치도(discrepancy) 는 O(log N): 실측 최대 4
    // ④ 규칙적인 키: 64 의 배수 100,000 개를 1024 버킷에
    {   std::vector<int> div(1024, 0), mul(1024, 0); for (std::uint32_t i = 0; i < 100000; ++i) { ++div[(i * 64) % 1024]; ++mul[fib(i * 64, 10)]; }
        int divUsed = 0, mulUsed = 0; for (int c : div) divUsed += c > 0; for (int c : mul) mulUsed += c > 0; int mulMax = *std::max_element(mul.begin(), mul.end());
        assert(divUsed == 16 && mulUsed == 1024 && mulMax <= 100000 / 1024 + 6);     // 이상적인 부하는 97.7, 실측 최대 99
        // ⑤ 균등성: 무작위 키 40 만 개, 카이제곱
        std::vector<int> load(1024, 0); for (int i = 0; i < 400000; ++i) ++load[fib(rng(), 10)]; double chi = 0, e = 400000.0 / 1024; for (int c : load) chi += (c - e) * (c - e) / e; assert(std::abs(chi - 1023) < 5 * std::sqrt(2.0 * 1023));
        std::cout << "MultiplicationMethod: the integer Fibonacci hash equalled the exact rational computation for 1,000,000 random (k, p) pairs and differed from a long-double golden-ratio version for small keys in only " << mismatchReal << " of " << smallTrials << " cases, point gaps took at most three values (three-distance theorem), and for 100,000 multiples of 64 the division method used " << divUsed << " of 1024 buckets while the multiplication method used " << mulUsed << " (largest bucket " << mulMax << ")" << std::endl; }
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## UniversalHashing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <cassert>

// 전역 해시 족: h_{a,b}(k) = ((a*k + b) mod p) mod m,  p는 소수, a in [1,p-1], b in [0,p-1]
// 서로 다른 두 키가 충돌할 확률이 (무작위 a,b에 대해) 1/m 이하로 보장된다
struct Universal {
    static constexpr uint64_t P = 2147483647ULL;      // 2^31 - 1
    uint64_t a, b, m;
    uint64_t operator()(uint64_t k) const { return ((a * k + b) % P) % m; }
};

int main() {
    std::mt19937_64 rng(12345);
    const uint64_t m = 64;
    const int trials = 40000;
    int collide = 0;
    for (int t = 0; t < trials; t++) {
        Universal h{rng() % (Universal::P - 1) + 1, rng() % Universal::P, m};
        if (h(1000003) == h(7000001)) collide++;       // 고정된 두 키
    }
    double rate = double(collide) / trials;
    assert(rate < 2.0 / m);                            // 이론 상한 1/m = 0.0156 의 2배 이내
    std::cout << "collision rate " << rate << " (bound " << 1.0 / m << ")" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## FNV()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

// FNV-1a: XOR 한 뒤 곱한다 (FNV-1은 곱한 뒤 XOR).  시작값(offset basis)과 소수는 32 비트: 2166136261 / 16777619, 64 비트: 14695981039346656037 / 1099511628211
// 공개된 시험 벡터와 파이썬 구현(따로 작성)으로 변형 네 가지(1/1a × 32/64 비트)를 검증하고, 성질을 수치로 확인한다 — 빠르고 단순하지만 암호학적 해시가 아니다
// 검증: ① 표준 벡터 5 개 문자열 × 4 변형  ② 곱셈을 *시프트·덧셈* 으로 푼 구현과 무작위 입력 100 000 개 일치, 이어 해싱(앞 부분의 해시를 시작값으로)이 연결 해시와 같음
//        ③ 눈사태: 마지막 바이트의 한 비트를 뒤집으면 출력 비트가 평균 10 개 미만만 바뀌는 반면(마지막 곱셈 한 번뿐이라 소수 0x01000193 의 모양이 드러남), 첫 바이트는 평균 13 개 이상 — FNV 의 약점
//        ④ 버킷 분포(카이제곱 검정: 무작위 키 대 순차 키)와, 32 비트 해시의 생일 충돌을 실제로 찾아낸다 (예상 약 8 만 개 시도)
uint32_t fnv1a32(const std::string& s) {
    uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    return h;
}
uint32_t fnv1_32(const std::string& s) { uint32_t h = 2166136261u; for (unsigned char c : s) { h *= 16777619u; h ^= c; } return h; }
uint64_t fnv1a64(const std::string& s) {
    uint64_t h = 14695981039346656037ULL;
    for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; }
    return h;
}
uint64_t fnv1_64(const std::string& s) { uint64_t h = 14695981039346656037ULL; for (unsigned char c : s) { h *= 1099511628211ULL; h ^= c; } return h; }
uint32_t fnv1a32Continue(uint32_t h, const std::string& s) { for (unsigned char c : s) { h ^= c; h *= 16777619u; } return h; }      // 이어 해싱
uint32_t fnv1a32Shift(const std::string& s) {                                    // 0x01000193 = 2^24 + 2^8 + 2^7 + 2^4 + 2^1 + 1 : 곱셈 없이 시프트와 덧셈만
    uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24); }
    return h;
}
uint64_t fnv1a64Shift(const std::string& s) {                                    // 0x100000001b3 = 2^40 + 2^8 + 2^7 + 2^5 + 2^4 + 2^1 + 1
    uint64_t h = 14695981039346656037ULL;
    for (unsigned char c : s) { h ^= c; h += (h << 1) + (h << 4) + (h << 5) + (h << 7) + (h << 8) + (h << 40); }
    return h;
}
int popcount32(uint32_t x) { int c = 0; while (x) { c += x & 1; x >>= 1; } return c; }

int main() {
    assert(fnv1a32("") == 0x811c9dc5u);
    assert(fnv1a32("a") == 0xe40c292cu);
    assert(fnv1a32("foobar") == 0xbf9cf968u);
    assert(fnv1a64("a") == 0xaf63dc4c8601ec8cULL);
    assert(fnv1a64("foobar") == 0x85944171f73967e8ULL);
    // ① 파이썬 구현으로 얻은 표준 벡터: {입력, FNV-1a 32, FNV-1 32, FNV-1a 64, FNV-1 64}
    struct V { const char* s; uint32_t a32, f32; uint64_t a64, f64; };
    const V vec[] = {
        {"", 0x811c9dc5u, 0x811c9dc5u, 0xcbf29ce484222325ULL, 0xcbf29ce484222325ULL},
        {"a", 0xe40c292cu, 0x050c5d7eu, 0xaf63dc4c8601ec8cULL, 0xaf63bd4c8601b7beULL},
        {"b", 0xe70c2de5u, 0x050c5d7du, 0xaf63df4c8601f1a5ULL, 0xaf63bd4c8601b7bdULL},
        {"foobar", 0xbf9cf968u, 0x31f0b262u, 0x85944171f73967e8ULL, 0x340d8765a4dda9c2ULL},
        {"hello", 0x4f9f2cabu, 0xb6fa7167u, 0xa430d84680aabd0bULL, 0x7b495389bdbdd4c7ULL},
        {"The quick brown fox jumps over the lazy dog", 0x048fff90u, 0xe9c86c6eu, 0xf3f9b7f5e7e47110ULL, 0xa8b2f3117de37aceULL}};
    for (const V& v : vec) assert(fnv1a32(v.s) == v.a32 && fnv1_32(v.s) == v.f32 && fnv1a64(v.s) == v.a64 && fnv1_64(v.s) == v.f64);
    assert(fnv1a32(std::string("\0", 1)) == 0x050c5d1fu && fnv1a32(std::string(1, '\xFF')) != fnv1a32(std::string(1, '\x7F')));          // 바이트는 부호 없는 값으로 (NUL 도 해시에 기여)
    // ② 시프트 구현, 이어 해싱
    std::mt19937 rng(1234);
    for (int i = 0; i < 100000; ++i) {
        std::string s(rng() % 24, 'x'); for (char& c : s) c = (char)rng();
        assert(fnv1a32Shift(s) == fnv1a32(s) && fnv1a64Shift(s) == fnv1a64(s));
        size_t cut = s.empty() ? 0 : rng() % (s.size() + 1); assert(fnv1a32Continue(fnv1a32(s.substr(0, cut)), s.substr(cut)) == fnv1a32(s));
    }
    // ③ 눈사태
    double sumLast = 0, sumFirst = 0; long cnt = 0;
    for (int i = 0; i < 20000; ++i) {
        std::string s(8, 'x'); for (char& c : s) c = (char)rng();
        int b = (int)(rng() % 8); std::string last = s, first = s; last[7] ^= (char)(1 << b); first[0] ^= (char)(1 << b);
        sumLast += popcount32(fnv1a32(s) ^ fnv1a32(last)); sumFirst += popcount32(fnv1a32(s) ^ fnv1a32(first)); ++cnt;
    }
    double avgLast = sumLast / cnt, avgFirst = sumFirst / cnt;
    assert(avgLast < 10 && avgFirst > 13);                              // 이상적인 해시라면 둘 다 16
    // ④ 버킷 분포: 카이제곱 = Σ (관측 - 기대)² / 기대 , 자유도 m-1 이면 평균 m-1, 표준편차 √(2(m-1)).  무작위 키는 평균 근처, 순차 키 "key0.." 는 구조가 있어 한쪽으로 치우친다(너무 고르거나 약간 몰림)
    double chiRandom[2], chiSeq[2]; const size_t ms[2] = {1009, 1024};
    for (int k = 0; k < 2; ++k) {
        std::vector<long> rb(ms[k], 0), sb(ms[k], 0); const int N = 100000;
        for (int i = 0; i < N; ++i) {
            std::string r; for (int j = 0; j < 12; j++) r += "abcdefghijklmnopqrstuvwxyz0123456789"[rng() % 36];
            rb[fnv1a32(r) % ms[k]]++; sb[fnv1a32("key" + std::to_string(i)) % ms[k]]++;
        }
        double expect = (double)N / ms[k], c1 = 0, c2 = 0; for (long o : rb) c1 += (o - expect) * (o - expect) / expect; for (long o : sb) c2 += (o - expect) * (o - expect) / expect;
        chiRandom[k] = c1; chiSeq[k] = c2; double mean = (double)(ms[k] - 1), sd = std::sqrt(2.0 * mean);
        assert(std::fabs(c1 - mean) < 4 * sd);                          // 무작위 키: 이상적인 해시와 구별되지 않는다
        assert(c2 > 0.5 * mean && c2 < 1.5 * mean);                     // 순차 키: 실용적으로는 쓸 만한 범위 (±50 %)
    }
    // 32 비트 해시의 생일 충돌: 무작위 12 글자 키를 해시하다 처음으로 겹치는 쌍 (기대 시도 횟수 ≈ √(π/2 · 2^32) ≈ 82 000)
    std::unordered_map<uint32_t, std::string> seen; std::string ka, kb; int tries = 0;
    for (; tries < 400000 && ka.empty(); ++tries) {
        std::string r; for (int j = 0; j < 12; j++) r += "abcdefghijklmnopqrstuvwxyz0123456789"[rng() % 36];
        auto it = seen.find(fnv1a32(r)); if (it != seen.end() && it->second != r) { ka = it->second; kb = r; } else seen[fnv1a32(r)] = r;
    }
    assert(!ka.empty() && ka != kb && fnv1a32(ka) == fnv1a32(kb) && tries > 5000 && tries < 400000);
    std::cout << std::hex << "fnv1a32(foobar)=" << fnv1a32("foobar") << std::dec << "; avalanche (flipped output bits of 32): last byte " << avgLast << ", first byte " << avgFirst << "; chi-square (random keys) " << chiRandom[0] << " / " << chiRandom[1] << ", (sequential) " << chiSeq[0] << " / " << chiSeq[1] << "; collision found after " << tries << " random keys: " << ka << " and " << kb << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)
```
## MurmurHash()
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
#include <string>
#include <vector>

// MurmurHash3 (x86, 32비트): 4 바이트 블록마다 k *= c1; k = rotl(k, 15); k *= c2; h ^= k; h = rotl(h, 13); h = h·5 + 0xe6546b64 로 섞고, 남은 1~3 바이트(tail)를 같은 식으로 처리한 뒤 길이를 xor 하고 fmix32(최종 눈사태) 를 적용한다. 빠르고 분포가 좋아 해시 테이블에 널리 쓰이지만 *암호학적이지 않다* — 모든 단계가 가역이라 해시값을 알면 같은 값을 내는 메시지를 O(1) 에 만들 수 있다(아래 검증: 임의의 목표값에 대한 8 바이트 역상). 그래서 공격자가 키를 고르는 환경(HashDoS)에는 SipHash 같은 키 있는 해시를 쓴다.
// 구현 주의: 블록은 memcpy 로 읽는다(정렬되지 않은 주소를 reinterpret_cast 하면 UB). 리틀 엔디언 가정은 호스트 엔디언 변환으로 명시한다. 검증: ① 널리 알려진 테스트 벡터(빈 문자열 seed 0 → 0, seed 1 → 0x514e28b7, seed 0xffffffff → 0x81f16f39, "test" → 0xba6bd213, "Hello, world!" → 0xc0363e43, seed 0x9747b28c 의 "The quick brown fox jumps over the lazy dog" → 0x2fa826cd) ② 주소 정렬 무관(offset 0..7 로 복사해도 같은 값) ③ 눈사태: 입력 한 비트를 뒤집으면 출력이 평균 16 ± 0.5 비트 뒤집히고 출력 비트별 확률이 0.45~0.55 ④ fmix32 가 전단사이고 *4 바이트 키 전체에 대해 전단사*(역함수로 왕복 일치 100 만 개) → 4 바이트 키는 충돌이 없다 ⑤ 역상 공격: 임의의 시드·목표값에 대해 8 바이트 메시지를 만들어 정확히 그 해시값을 얻는다(2000 번 성공).
inline std::uint32_t rotl(std::uint32_t x, int r) { return (x << r) | (x >> (32 - r)); }
inline std::uint32_t rotr(std::uint32_t x, int r) { return (x >> r) | (x << (32 - r)); }
inline std::uint32_t fmix32(std::uint32_t h) { h ^= h >> 16; h *= 0x85ebca6bU; h ^= h >> 13; h *= 0xc2b2ae35U; h ^= h >> 16; return h; }
const std::uint32_t C1 = 0xcc9e2d51U, C2 = 0x1b873593U;
std::uint32_t murmur3(const void* data, std::size_t len, std::uint32_t seed) {
    const std::uint8_t* p = static_cast<const std::uint8_t*>(data); std::uint32_t h = seed; std::size_t nblocks = len / 4;
    for (std::size_t i = 0; i < nblocks; ++i) { std::uint32_t k; std::memcpy(&k, p + 4 * i, 4); k *= C1; k = rotl(k, 15); k *= C2; h ^= k; h = rotl(h, 13); h = h * 5 + 0xe6546b64U; }
    const std::uint8_t* tail = p + nblocks * 4; std::uint32_t k = 0;
    switch (len & 3) { case 3: k ^= (std::uint32_t)tail[2] << 16; [[fallthrough]]; case 2: k ^= (std::uint32_t)tail[1] << 8; [[fallthrough]]; case 1: k ^= tail[0]; k *= C1; k = rotl(k, 15); k *= C2; h ^= k; }
    h ^= (std::uint32_t)len; return fmix32(h);
}
std::uint32_t inv32(std::uint32_t a) { std::uint32_t x = a; for (int i = 0; i < 5; ++i) x *= 2 - a * x; return x; }                   // 홀수 a 의 곱셈 역원 (뉴턴 반복)
std::uint32_t unfmix32(std::uint32_t h) { h ^= h >> 16; h *= inv32(0xc2b2ae35U); h ^= h >> 13; h ^= h >> 26; h *= inv32(0x85ebca6bU); h ^= h >> 16; return h; }

int main() {
    // ① 테스트 벡터
    auto H = [](const std::string& s, std::uint32_t seed) { return murmur3(s.data(), s.size(), seed); };
    assert(H("", 0) == 0 && H("", 1) == 0x514e28b7U && H("", 0xffffffffU) == 0x81f16f39U);
    assert(H("test", 0) == 0xba6bd213U && H("Hello, world!", 0) == 0xc0363e43U && H("The quick brown fox jumps over the lazy dog", 0x9747b28cU) == 0x2fa826cdU);
    // ② 정렬 무관: 같은 바이트를 서로 다른 offset 에 복사해 해시
    std::mt19937 rng(3);
    for (int t = 0; t < 2000; ++t) { std::size_t len = rng() % 40; std::vector<std::uint8_t> msg(len); for (auto& b : msg) b = (std::uint8_t)rng(); std::uint32_t seed = rng(), ref = murmur3(msg.data(), len, seed);
        for (int off = 0; off < 8; ++off) { std::vector<std::uint8_t> buf(len + 8); std::copy(msg.begin(), msg.end(), buf.begin() + off); assert(murmur3(buf.data() + off, len, seed) == ref); } }
    // ③ 눈사태: 16 바이트 키 2000 개 × 128 비트 뒤집기
    {   double flipsSum = 0; long cell[32] = {0}; long total = 0;
        for (int t = 0; t < 2000; ++t) { std::uint8_t key[16]; for (auto& b : key) b = (std::uint8_t)rng(); std::uint32_t base = murmur3(key, 16, 7);
            for (int bit = 0; bit < 128; ++bit) { key[bit / 8] ^= (std::uint8_t)(1u << (bit % 8)); std::uint32_t diff = base ^ murmur3(key, 16, 7); key[bit / 8] ^= (std::uint8_t)(1u << (bit % 8)); flipsSum += __builtin_popcount(diff); for (int o = 0; o < 32; ++o) cell[o] += diff >> o & 1; ++total; } }
        double avg = flipsSum / (double)total; assert(avg > 15.5 && avg < 16.5); for (int o = 0; o < 32; ++o) { double pr = (double)cell[o] / (double)total; assert(pr > 0.45 && pr < 0.55); } }
    // ④ fmix32 전단사, 4 바이트 키 해시의 역함수 왕복 (그러므로 4 바이트 키끼리는 충돌이 없다)
    for (int t = 0; t < 1000000; ++t) {
        std::uint32_t x = rng(); assert(unfmix32(fmix32(x)) == x);
        std::uint32_t seed = rng(), key = rng(); std::uint32_t h = murmur3(&key, 4, seed);
        std::uint32_t u = unfmix32(h) ^ 4; u = (u - 0xe6546b64U) * inv32(5); u = rotr(u, 13); u ^= seed; u *= inv32(C2); u = rotr(u, 15); u *= inv32(C1); assert(u == key);
    }
    // ⑤ 역상 공격: 임의의 시드 s 와 목표값 T 에 대해 8 바이트 메시지 (a, b) 를 만든다 — a 는 아무거나, b 는 T 로부터 거꾸로 계산
    for (int t = 0; t < 2000; ++t) {
        std::uint32_t seed = rng(), target = rng(), a = rng();
        std::uint32_t h1 = seed; { std::uint32_t k = a * C1; k = rotl(k, 15); k *= C2; h1 ^= k; h1 = rotl(h1, 13); h1 = h1 * 5 + 0xe6546b64U; }          // 첫 블록 처리 뒤의 상태
        std::uint32_t u = unfmix32(target) ^ 8; u = (u - 0xe6546b64U) * inv32(5); u = rotr(u, 13); u ^= h1; u *= inv32(C2); u = rotr(u, 15); u *= inv32(C1);   // 두 번째 블록 k 를 거꾸로
        std::uint32_t msg[2] = {a, u}; assert(murmur3(msg, 8, seed) == target);
    }
    std::cout << "MurmurHash: the published test vectors matched, hashing the same bytes at eight different alignments gave identical values, flipping one input bit changed 16 +- 0.5 output bits on average with every output bit between 45% and 55%, the 4-byte-key hash was inverted exactly for 1,000,000 random (seed, key) pairs, and for 2000 random (seed, target) pairs an 8-byte message with exactly that hash was constructed in constant time - which is why it must not protect a table against adversarial keys" << std::endl; return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)
```
## xxHash()
### 대표코드
```cpp
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// xxHash32 / xxHash64: 4(8) 개 레인을 병렬로 돌려 긴 입력에서 빠르고 눈사태가 좋다.  16(32) 바이트 단위 본체 + 남은 꼬리 + 마지막 섞기
// 검증: ① 공개된 시험 벡터(XXH32: "" -> 02CC5D05, 시드 PRIME32_1 -> 36B78AE7, "a", "abc", 긴 문장 / XXH64: "" -> EF46DB3751D8E999 …)
//        ② 파이썬으로 따로 구현해 계산한 체크섬: 1 바이트 입력 256 개의 XOR, 2 바이트 입력 65 536 개의 XOR(시드 12345), 길이 0~300 의 의사난수 버퍼의 누적 합 (32/64 비트) — 꼬리 처리 경로를 전부 지난다
//        ③ 스트리밍 상태(16 바이트 버퍼)가 입력을 어떻게 나눠 넣어도(길이 0~100 의 모든 한 곳 분할 + 무작위 분할) 한 번에 해시한 값과 같고, 정렬되지 않은 주소(오프셋 0~3)에서도 같은 값
//        ④ 눈사태: 입력 한 비트를 뒤집으면 출력 32 비트 중 평균 16 개가 바뀐다 (모든 바이트 위치에서 15~17)
static const uint32_t P1 = 2654435761u, P2 = 2246822519u, P3 = 3266489917u, P4 = 668265263u, P5 = 374761393u;
static const uint64_t Q1 = 11400714785074694791ULL, Q2 = 14029467366897019727ULL, Q3 = 1609587929392839161ULL, Q4 = 9650029242287828579ULL, Q5 = 2870177450012600261ULL;
static inline uint32_t rotl(uint32_t x, int r) { return (x << r) | (x >> (32 - r)); }
static inline uint64_t rotl64(uint64_t x, int r) { return (x << r) | (x >> (64 - r)); }
static inline uint32_t rd32(const uint8_t* p) { uint32_t v; std::memcpy(&v, p, 4); return v; }
static inline uint64_t rd64(const uint8_t* p) { uint64_t v; std::memcpy(&v, p, 8); return v; }
static inline uint32_t round1(uint32_t acc, uint32_t in) { return rotl(acc + in * P2, 13) * P1; }

uint32_t finish32(uint32_t h, const uint8_t* p, const uint8_t* end) {            // 꼬리(4 바이트씩, 그다음 1 바이트씩)와 마지막 섞기
    while (p + 4 <= end) { h += rd32(p) * P3; h = rotl(h, 17) * P4; p += 4; }
    while (p < end) { h += (*p++) * P5; h = rotl(h, 11) * P1; }
    h ^= h >> 15; h *= P2; h ^= h >> 13; h *= P3; h ^= h >> 16;
    return h;
}
uint32_t xxh32(const uint8_t* p, size_t len, uint32_t seed) {
    const uint8_t* end = p + len;
    uint32_t h;
    if (len >= 16) {
        uint32_t v1 = seed + P1 + P2, v2 = seed + P2, v3 = seed, v4 = seed - P1;
        const uint8_t* limit = end - 16;
        do {
            v1 = round1(v1, rd32(p)); v2 = round1(v2, rd32(p + 4));
            v3 = round1(v3, rd32(p + 8)); v4 = round1(v4, rd32(p + 12));
            p += 16;
        } while (p <= limit);
        h = rotl(v1, 1) + rotl(v2, 7) + rotl(v3, 12) + rotl(v4, 18);
    } else {
        h = seed + P5;
    }
    h += (uint32_t)len;
    return finish32(h, p, end);
}
uint32_t xxh(const std::string& s, uint32_t seed = 0) { return xxh32((const uint8_t*)s.data(), s.size(), seed); }

struct XXH32State {                                                              // 스트리밍: 16 바이트가 찰 때까지 버퍼에 모은다
    uint64_t total = 0; uint32_t v[4]; uint8_t mem[16]; uint32_t memsize = 0, seed;
    explicit XXH32State(uint32_t s) : seed(s) { v[0] = s + P1 + P2; v[1] = s + P2; v[2] = s; v[3] = s - P1; }
    void update(const uint8_t* p, size_t len) {
        total += len;
        if (memsize + len < 16) { if (len) std::memcpy(mem + memsize, p, len); memsize += (uint32_t)len; return; }
        if (memsize) { std::memcpy(mem + memsize, p, 16 - memsize); for (int i = 0; i < 4; i++) v[i] = round1(v[i], rd32(mem + 4 * i)); p += 16 - memsize; len -= 16 - memsize; memsize = 0; }
        while (len >= 16) { for (int i = 0; i < 4; i++) v[i] = round1(v[i], rd32(p + 4 * i)); p += 16; len -= 16; }
        if (len) { std::memcpy(mem, p, len); memsize = (uint32_t)len; }
    }
    uint32_t digest() const {
        uint32_t h = total >= 16 ? rotl(v[0], 1) + rotl(v[1], 7) + rotl(v[2], 12) + rotl(v[3], 18) : seed + P5;
        h += (uint32_t)total; return finish32(h, mem, mem + memsize);
    }
};
static inline uint64_t round64(uint64_t acc, uint64_t in) { return rotl64(acc + in * Q2, 31) * Q1; }
static inline uint64_t merge64(uint64_t acc, uint64_t v) { v = round64(0, v); acc ^= v; return acc * Q1 + Q4; }
uint64_t xxh64(const uint8_t* p, size_t len, uint64_t seed) {
    const uint8_t* end = p + len; uint64_t h;
    if (len >= 32) {
        uint64_t v1 = seed + Q1 + Q2, v2 = seed + Q2, v3 = seed, v4 = seed - Q1; const uint8_t* limit = end - 32;
        do { v1 = round64(v1, rd64(p)); v2 = round64(v2, rd64(p + 8)); v3 = round64(v3, rd64(p + 16)); v4 = round64(v4, rd64(p + 24)); p += 32; } while (p <= limit);
        h = rotl64(v1, 1) + rotl64(v2, 7) + rotl64(v3, 12) + rotl64(v4, 18); h = merge64(h, v1); h = merge64(h, v2); h = merge64(h, v3); h = merge64(h, v4);
    } else h = seed + Q5;
    h += (uint64_t)len;
    while (p + 8 <= end) { h ^= round64(0, rd64(p)); h = rotl64(h, 27) * Q1 + Q4; p += 8; }
    if (p + 4 <= end) { h ^= (uint64_t)rd32(p) * Q1; h = rotl64(h, 23) * Q2 + Q3; p += 4; }
    while (p < end) { h ^= (*p++) * Q5; h = rotl64(h, 11) * Q1; }
    h ^= h >> 33; h *= Q2; h ^= h >> 29; h *= Q3; h ^= h >> 32;
    return h;
}
int popcount(uint64_t x) { int c = 0; while (x) { c += (int)(x & 1); x >>= 1; } return c; }

int main() {
    assert(xxh("", 0) == 0x02CC5D05u);
    assert(xxh("a", 0) == 0x550D7456u);
    assert(xxh("abc", 0) == 0x32D153FFu);
    // ① 공개된 시험 벡터
    assert(xxh("", 2654435761u) == 0x36B78AE7u && xxh("Nobody inspects the spammish repetition", 0) == 0xE2293B2Fu);
    auto x64 = [](const std::string& s, uint64_t seed) { return xxh64((const uint8_t*)s.data(), s.size(), seed); };
    assert(x64("", 0) == 0xEF46DB3751D8E999ULL && x64("a", 0) == 0xD24EC4F1A98C6E5BULL && x64("abc", 0) == 0x44BC2CF5AD770999ULL && x64("Nobody inspects the spammish repetition", 0) == 0xFBCEA83C8A378BF1ULL);
    // ② 파이썬 참조 구현이 계산한 체크섬
    uint32_t x1 = 0; for (int a = 0; a < 256; a++) { uint8_t b[1] = {(uint8_t)a}; x1 ^= xxh32(b, 1, 0); }
    uint32_t x2 = 0; for (int a = 0; a < 256; a++) for (int c = 0; c < 256; c++) { uint8_t b[2] = {(uint8_t)a, (uint8_t)c}; x2 ^= xxh32(b, 2, 12345); }
    assert(x1 == 0xda9e5e68u && x2 == 0x83284d3au);
    std::vector<uint8_t> buf; { uint32_t st = 12345; for (int i = 0; i < 400; i++) { st = (st * 1103515245u + 12345u) & 0x7fffffffu; buf.push_back((uint8_t)((st >> 16) & 0xff)); } }
    uint32_t r32 = 0; uint64_t r64 = 0; for (size_t n = 0; n <= 300; n++) { r32 = r32 * 31u + xxh32(buf.data(), n, (uint32_t)n); r64 = r64 * 131u + xxh64(buf.data(), n, n); }
    assert(r32 == 0x37c4d59au && r64 == 0x438caff83db006eeULL);
    // ③ 스트리밍과 정렬
    std::mt19937 rng(5);
    for (size_t n = 0; n <= 100; n++) {
        std::vector<uint8_t> d(buf.begin(), buf.begin() + (long)n); uint32_t want = xxh32(d.data(), n, 777);
        for (size_t cut = 0; cut <= n; cut++) { XXH32State s(777); s.update(d.data(), cut); s.update(d.data() + cut, n - cut); assert(s.digest() == want); }
        XXH32State s(777); size_t pos = 0; while (pos < n) { size_t step = 1 + rng() % 20; if (pos + step > n) step = n - pos; s.update(d.data() + pos, step); pos += step; } assert(s.digest() == want);
        for (int off = 1; off <= 3; off++) { std::vector<uint8_t> shifted(n + 4); if (n) std::memcpy(shifted.data() + off, d.data(), n); assert(xxh32(shifted.data() + off, n, 777) == want); }
    }
    // ④ 눈사태
    for (int pos : {0, 3, 7, 12, 15}) {
        double sum32 = 0, sum64 = 0; const int N = 4000;
        for (int i = 0; i < N; i++) {
            uint8_t in[16]; for (auto& c : in) c = (uint8_t)rng(); uint8_t flip[16]; std::memcpy(flip, in, 16); flip[pos] ^= (uint8_t)(1 << (rng() % 8));
            sum32 += popcount(xxh32(in, 16, 0) ^ xxh32(flip, 16, 0)); sum64 += popcount(xxh64(in, 16, 0) ^ xxh64(flip, 16, 0));
        }
        assert(sum32 / N > 15 && sum32 / N < 17 && sum64 / N > 31 && sum64 / N < 33);     // 이상적이면 32 비트에서 16, 64 비트에서 32
    }
    std::cout << std::hex << "xxh32(abc)=" << xxh("abc") << " xxh64(abc)=" << x64("abc", 0) << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)  (스트리밍 상태 48 바이트)
```
## SipHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <unordered_map>
#include <vector>

// SipHash-2-4: 128비트 비밀 키를 쓰는 짧은 메시지용 의사난수 함수(PRF). 메시지를 8 바이트 단어로 잘라 상태 (v0..v3) 에 넣고 단어마다 SipRound 2 번(c = 2), 마지막에 길이와 남은 바이트로 한 단어를 더 넣고 v2 ^= 0xff 한 뒤 SipRound 4 번(d = 4) 을 돌려 v0 ^ v1 ^ v2 ^ v3 을 낸다. 해시 플러딩(HashDoS) 방어용으로 Python, Rust, Ruby, Linux 커널 등이 해시 테이블 키 해시에 쓴다 — 공격자가 키를 모르면 충돌을 미리 만들 수 없기 때문이다. MurmurHash 와 달리 역상을 O(1) 에 만들 수 없다.
// 검증: ① 논문(Aumasson–Bernstein)의 시험 벡터 — 키 00 01 … 0f, 메시지 00 01 … 0e(15 바이트) → 0xa129ca6149be45e5, 그리고 참조 구현의 길이 0..4 벡터(0x726fdb47dd0e0e31, 0x74f839c593dc67fd, 0x0d6c8009d9a94f5a, 0x85676696d7fb7e2d, 0xcf2794e0277187b7) ② 한 번에 해시한 값 = 임의로 쪼개 넣는 스트리밍 해시(길이 0..80, 무작위 분할 지점) ③ 키 한 비트나 메시지 한 비트가 바뀌면 출력이 평균 32 ± 0.5 비트 뒤집힘 ④ *키 의존성*: 키 A 에서 32비트 접두 충돌을 생일 역설로 찾으면(약 2^16 번) 같은 쌍은 키 B 에서 충돌하지 않는다(우연히 같을 확률 2^-32) ⑤ 모든 길이 0..64 에서 꼬리 처리(남은 바이트) 가 일관: 접두사와 길이가 다른 메시지는 서로 다른 값.
inline std::uint64_t rotl(std::uint64_t x, int b) { return (x << b) | (x >> (64 - b)); }
struct Sip {
    std::uint64_t v0, v1, v2, v3; std::uint8_t buf[8]; int fill = 0; std::uint64_t total = 0;
    Sip(std::uint64_t k0, std::uint64_t k1) : v0(k0 ^ 0x736f6d6570736575ULL), v1(k1 ^ 0x646f72616e646f6dULL), v2(k0 ^ 0x6c7967656e657261ULL), v3(k1 ^ 0x7465646279746573ULL) {}
    void round() { v0 += v1; v1 = rotl(v1, 13); v1 ^= v0; v0 = rotl(v0, 32); v2 += v3; v3 = rotl(v3, 16); v3 ^= v2; v0 += v3; v3 = rotl(v3, 21); v3 ^= v0; v2 += v1; v1 = rotl(v1, 17); v1 ^= v2; v2 = rotl(v2, 32); }
    void word(std::uint64_t m) { v3 ^= m; round(); round(); v0 ^= m; }
    void update(const void* data, std::size_t len) {
        const std::uint8_t* p = static_cast<const std::uint8_t*>(data); total += len;
        while (len) { std::size_t take = std::min<std::size_t>(8 - fill, len); std::memcpy(buf + fill, p, take); fill += (int)take; p += take; len -= take; if (fill == 8) { std::uint64_t m; std::memcpy(&m, buf, 8); word(m); fill = 0; } }      // 리틀 엔디언 호스트 가정
    }
    std::uint64_t finish() {
        std::uint64_t b = total << 56; for (int i = 0; i < fill; ++i) b |= (std::uint64_t)buf[i] << (8 * i);
        v3 ^= b; round(); round(); v0 ^= b; v2 ^= 0xff; round(); round(); round(); round(); return v0 ^ v1 ^ v2 ^ v3;
    }
};
std::uint64_t sip24(const void* data, std::size_t len, std::uint64_t k0, std::uint64_t k1) { Sip s(k0, k1); s.update(data, len); return s.finish(); }

int main() {
    // ① 시험 벡터: 키 = 00..0f (k0 = 0x0706050403020100, k1 = 0x0f0e0d0c0b0a0908), 메시지 = 00, 01, 02, …
    const std::uint64_t K0 = 0x0706050403020100ULL, K1 = 0x0f0e0d0c0b0a0908ULL; std::uint8_t msg[64]; for (int i = 0; i < 64; ++i) msg[i] = (std::uint8_t)i;
    assert(sip24(msg, 15, K0, K1) == 0xa129ca6149be45e5ULL);
    const std::uint64_t ref[5] = {0x726fdb47dd0e0e31ULL, 0x74f839c593dc67fdULL, 0x0d6c8009d9a94f5aULL, 0x85676696d7fb7e2dULL, 0xcf2794e0277187b7ULL}; for (int len = 0; len < 5; ++len) assert(sip24(msg, len, K0, K1) == ref[len]);
    // ② 스트리밍 = 한 번에 (길이 0..80, 무작위 분할)
    std::mt19937_64 rng(11);
    for (int t = 0; t < 3000; ++t) { std::size_t len = rng() % 81; std::vector<std::uint8_t> m(len); for (auto& b : m) b = (std::uint8_t)rng(); std::uint64_t k0 = rng(), k1 = rng(); std::uint64_t one = sip24(m.data(), len, k0, k1);
        Sip s(k0, k1); std::size_t pos = 0; while (pos < len) { std::size_t chunk = 1 + rng() % 13; chunk = std::min(chunk, len - pos); s.update(m.data() + pos, chunk); pos += chunk; } assert(s.finish() == one); }
    // ③ 눈사태: 키 한 비트 · 메시지 한 비트
    {   double sumKey = 0, sumMsg = 0; long nKey = 0, nMsg = 0;
        for (int t = 0; t < 400; ++t) { std::uint8_t m[24]; for (auto& b : m) b = (std::uint8_t)rng(); std::uint64_t k0 = rng(), k1 = rng(), base = sip24(m, 24, k0, k1);
            for (int bit = 0; bit < 64; ++bit) { sumKey += __builtin_popcountll(base ^ sip24(m, 24, k0 ^ (1ULL << bit), k1)); ++nKey; sumKey += __builtin_popcountll(base ^ sip24(m, 24, k0, k1 ^ (1ULL << bit))); ++nKey; }
            for (int bit = 0; bit < 192; ++bit) { m[bit / 8] ^= (std::uint8_t)(1u << (bit % 8)); sumMsg += __builtin_popcountll(base ^ sip24(m, 24, k0, k1)); ++nMsg; m[bit / 8] ^= (std::uint8_t)(1u << (bit % 8)); } }
        assert(std::abs(sumKey / nKey - 32) < 0.5 && std::abs(sumMsg / nMsg - 32) < 0.5); }
    // ④ 키 의존성: 키 A 에서 32비트 접두 충돌을 생일 역설로 찾고(40 만 개 중 약 18 쌍) 같은 쌍을 키 B 에서 검사
    {   const std::uint64_t A0 = rng(), A1 = rng(), B0 = rng(), B1 = rng(); std::unordered_map<std::uint32_t, std::uint32_t> first; int pairs = 0, collisionsOnB = 0;
        for (std::uint32_t x = 1; x < 400000; ++x) {
            std::uint32_t h = (std::uint32_t)sip24(&x, 4, A0, A1); auto it = first.find(h);
            if (it == first.end()) first[h] = x; else { ++pairs; std::uint32_t y = it->second; assert(y != x); collisionsOnB += (std::uint32_t)sip24(&x, 4, B0, B1) == (std::uint32_t)sip24(&y, 4, B0, B1); }
        }
        assert(pairs >= 5 && collisionsOnB == 0); }
    // ⑤ 길이마다 꼬리 처리가 일관: 같은 접두사라도 길이가 다르면 해시가 다르다 (0..64, 서로 다른 값 65 개)
    { std::vector<std::uint64_t> hs; for (int len = 0; len <= 64; ++len) hs.push_back(sip24(msg, len, K0, K1)); std::sort(hs.begin(), hs.end()); assert(std::adjacent_find(hs.begin(), hs.end()) == hs.end()); }
    std::cout << "SipHash: the Aumasson-Bernstein test vectors matched, streaming with random split points gave the same 64-bit value as one-shot hashing for 3000 random messages up to 80 bytes, flipping a key or message bit changed 32 +- 0.5 output bits on average, 32-bit collisions found for one key did not collide under another, and prefixes of every length 0..64 hashed to different values" << std::endl; return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)
```
# Part 3. 충돌 해결
## Chaining()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <vector>
#include <cassert>

// 분리 연쇄법: 버킷마다 연결 리스트(헤드 삽입). 평균 성공 탐색 비교 횟수 ≈ 1 + α/2
struct Node { uint64_t key; Node* next; };
static uint64_t mix(uint64_t x) {                       // splitmix64 마무리 단계
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

int main() {
    const size_t m = 5000, n = 10000;                   // α = 2
    std::vector<Node*> head(m, nullptr);
    std::mt19937_64 rng(7);
    std::vector<uint64_t> keys(n);
    for (auto& k : keys) { k = rng(); size_t b = mix(k) % m; head[b] = new Node{k, head[b]}; }
    double total = 0;
    for (uint64_t k : keys) {
        int steps = 1;
        for (Node* p = head[mix(k) % m]; p->key != k; p = p->next) ++steps;
        total += steps;
    }
    double avg = total / n;
    assert(avg > 1.8 && avg < 2.2);                     // 이론값 1 + α/2 = 2.0
    std::cout << "average comparisons (hit): " << avg << " (theory 2.0)" << std::endl;
    for (Node* h : head) while (h) { Node* t = h->next; delete h; h = t; }
    return 0;
}
// Time Complexity: 평균 O(1 + α), 최악 O(n)
// Space Complexity: O(n + m)
```
## OpenAddressing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 개방 주소법: 모든 원소를 테이블 안에 저장하고 충돌하면 다음 후보 칸을 탐사한다.  탐사열: 선형 h+i, 이차 h+i(i+1)/2, 이중 해싱 h+i·step(k).
// 삭제는 비우지 않고 묘비(DELETED)를 남겨야 뒤쪽 키의 탐사 경로가 끊기지 않는다.  묘비가 쌓이면 빈 칸이 사라져 실패하는 조회도 테이블 전체를 훑으므로 가끔 다시 지어야 한다.
// 선형 탐사에는 묘비 없이 뒤쪽 키를 앞으로 당기는 *뒤로 밀기 삭제* 도 있다.  선형 탐사의 평균 탐사 수(Knuth): 성공 ½(1+1/(1-α)), 실패 ½(1+1/(1-α)²)
// 검증: ① 손으로 짠 묘비 시나리오  ② 세 탐사열이 테이블 전체를 방문하는지 전수 확인(2^k 크기에서 삼각수·홀수 보폭은 순열, 소수 크기에서 i² 는 (m+1)/2 칸만, 짝수 보폭은 일부만)
//        ③ 세 방식을 std::set 과 40 000 번 대조(가득 찬 경우 삽입 실패 포함)하고 불변식(모든 키가 홈에서 빈 칸을 만나지 않고 닿음)  ④ 묘비 누적 실험: 정리하지 않으면 실패 조회가 거의 테이블 전체를 훑고(평균 > 40칸), 정리하면 3칸 이하
//        ⑤ 선형 탐사의 평균 탐사 수가 α = 0.5, 0.8 에서 Knuth 공식과 일치(성공·실패 모두 10~15 % 이내)  ⑥ 뒤로 밀기 삭제를 std::set 과 대조하고 불변식 확인
enum Probe { LINEAR, QUADRATIC, DOUBLE };
uint32_t mix(uint32_t x) { x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16; return x; }
class OpenTable {
    enum State { EMPTY, FULL, DELETED };
    struct Slot { unsigned key = 0; State st = EMPTY; };
    std::vector<Slot> t; Probe mode; bool identity; size_t live = 0, tomb = 0; mutable long probes = 0;
    size_t home(unsigned k) const { return identity ? (size_t)k % t.size() : (size_t)mix(k) % t.size(); }
    size_t step(unsigned k) const { return (size_t)((mix(k ^ 0x9e3779b9u) % (t.size() / 2)) * 2 + 1); }        // 홀수 보폭: 2^k 크기와 서로소
    size_t slotAt(unsigned k, size_t i) const {
        switch (mode) { case LINEAR: return (home(k) + i) % t.size(); case QUADRATIC: return (home(k) + i * (i + 1) / 2) % t.size(); default: return (home(k) + i * step(k)) % t.size(); }
    }
public:
    explicit OpenTable(size_t m, Probe p = LINEAR, bool identityHash = false) : t(m), mode(p), identity(identityHash) {}
    bool insert(unsigned k) {
        long firstFree = -1;
        for (size_t i = 0; i < t.size(); i++) {
            size_t j = slotAt(k, i);
            if (t[j].st == FULL && t[j].key == k) return false;
            if (t[j].st != FULL && firstFree < 0) firstFree = (long)j;   // 묘비 자리는 재사용
            if (t[j].st == EMPTY) break;
        }
        if (firstFree < 0) return false;                                 // 가득 참
        if (t[firstFree].st == DELETED) --tomb;
        t[firstFree] = {k, FULL}; ++live; return true;
    }
    bool find(unsigned k) const {
        for (size_t i = 0; i < t.size(); i++) {
            size_t j = slotAt(k, i); ++probes;
            if (t[j].st == EMPTY) return false;                           // 진짜 빈 칸을 만나야 종료
            if (t[j].st == FULL && t[j].key == k) return true;
        }
        return false;
    }
    bool erase(unsigned k) {
        for (size_t i = 0; i < t.size(); i++) {
            size_t j = slotAt(k, i);
            if (t[j].st == EMPTY) return false;
            if (t[j].st == FULL && t[j].key == k) { t[j].st = DELETED; --live; ++tomb; return true; }
        }
        return false;
    }
    void rebuild() { std::vector<Slot> old; old.swap(t); t.assign(old.size(), Slot()); live = tomb = 0; for (auto& s : old) if (s.st == FULL) insert(s.key); }     // 묘비 정리
    size_t size() const { return live; }
    size_t tombstones() const { return tomb; }
    size_t slots() const { return t.size(); }
    long probeCount() const { return probes; }
    void resetProbes() const { probes = 0; }
    bool valid() const {                                                 // 불변식: 모든 키는 탐사열을 따라가며 빈 칸을 만나기 전에 자기 자리에 닿는다
        size_t f = 0, d = 0;
        for (size_t j = 0; j < t.size(); j++) {
            if (t[j].st == DELETED) ++d;
            if (t[j].st != FULL) continue; ++f;
            bool reached = false; for (size_t i = 0; i < t.size(); i++) { size_t s = slotAt(t[j].key, i); if (s == j) { reached = true; break; } if (t[s].st == EMPTY) break; }
            if (!reached) return false;
        }
        return f == live && d == tomb;
    }
};
class ShiftTable {                                                       // 선형 탐사 + 뒤로 밀기 삭제 (묘비 없음)
    std::vector<long> t; size_t live = 0;                                // -1 = 빈 칸
    size_t home(unsigned k) const { return (size_t)mix(k) % t.size(); }
public:
    explicit ShiftTable(size_t m) : t(m, -1) {}
    bool insert(unsigned k) { if (live == t.size()) return false; size_t j = home(k); while (t[j] >= 0) { if (t[j] == (long)k) return false; j = (j + 1) % t.size(); } t[j] = (long)k; ++live; return true; }
    bool find(unsigned k) const { long steps = 0; size_t j = home(k); while (t[j] >= 0 && steps++ < (long)t.size()) { if (t[j] == (long)k) return true; j = (j + 1) % t.size(); } return false; }
    bool erase(unsigned k) {
        size_t j = home(k), n = t.size(); long steps = 0; while (t[j] >= 0 && t[j] != (long)k && steps++ < (long)n) j = (j + 1) % n;
        if (t[j] != (long)k) return false;
        size_t i = j;                                                    // i = 비워야 할 칸, j 를 앞으로 훑으며 홈이 (i, j] 밖에 있는 키를 i 로 당긴다
        for (;;) {
            j = (j + 1) % n; if (t[j] < 0) break;
            size_t h = home((unsigned)t[j]); bool inRange = i <= j ? (i < h && h <= j) : (i < h || h <= j);
            if (!inRange) { t[i] = t[j]; i = j; }
        }
        t[i] = -1; --live; return true;
    }
    size_t size() const { return live; }
    bool valid() const { size_t f = 0; for (size_t j = 0; j < t.size(); j++) { if (t[j] < 0) continue; ++f; size_t s = home((unsigned)t[j]); while (s != j) { if (t[s] < 0) return false; s = (s + 1) % t.size(); } } return f == live; }
};

int main() {
    OpenTable t(8, LINEAR, true);                                        // 항등 해시: 키 mod 8
    t.insert(1); t.insert(9); t.insert(17);                    // 모두 홈 버킷이 1
    assert(t.erase(9));                                        // 가운데 키 삭제 -> 묘비
    assert(t.find(17));                                        // 묘비를 지나서 17을 찾아야 한다
    assert(!t.find(9));
    assert(t.insert(25) && t.find(25));                        // 묘비 자리 재사용
    assert(t.size() == 3 && t.tombstones() == 0 && t.valid());
    OpenTable full(4, LINEAR, true); for (unsigned k = 0; k < 4; k++) assert(full.insert(k)); assert(!full.insert(4) && !full.find(99) && !full.insert(2) && full.size() == 4);      // 경계: 가득 찬 테이블에서도 조회는 끝난다
    // ② 탐사열이 방문하는 칸
    for (size_t m = 1; m <= 1024; m *= 2) {
        std::set<size_t> tri, dbl; for (size_t i = 0; i < m; i++) { tri.insert((5 + i * (i + 1) / 2) % m); dbl.insert((5 + i * 7) % m); }
        assert(tri.size() == m && dbl.size() == m);                      // 삼각수 탐사와 홀수 보폭은 모든 칸을 정확히 한 번씩
    }
    { std::set<size_t> sq, evenStep; for (size_t i = 0; i < 101; i++) sq.insert((3 + i * i) % 101); assert(sq.size() == 51);        // 소수 101: i² 는 (m+1)/2 = 51 칸만
      for (size_t i = 0; i < 64; i++) evenStep.insert((3 + i * 6) % 64); assert(evenStep.size() == 32); }                            // 짝수 보폭 6 은 2^k 에서 절반만
    // ③ std::set 대조
    std::mt19937 rng(2025); long fails = 0, succ = 0;
    for (Probe mode : {LINEAR, QUADRATIC, DOUBLE}) {
        OpenTable tb(256, mode); std::set<unsigned> model;
        for (int step = 0; step < 40000; ++step) {
            unsigned k = (unsigned)(rng() % 300); int op = (int)(rng() % 10);
            if (op < 5) { bool want = !model.count(k) && model.size() < 256; bool got = tb.insert(k); assert(got == want); if (got) model.insert(k); (got ? succ : fails)++; }
            else if (op < 8) assert(tb.erase(k) == (model.erase(k) > 0));
            else assert(tb.find(k) == (model.count(k) > 0));
            assert(tb.size() == model.size());
            if (tb.tombstones() > 100) tb.rebuild();                    // 가끔 정리
            if (step % 2000 == 0) assert(tb.valid());
        }
        for (unsigned k = 0; k < 300; k++) assert(tb.find(k) == (model.count(k) > 0));
        assert(tb.valid());
    }
    assert(fails > 1000 && succ > 10000);
    // ④ 묘비 누적: 30 개를 유지하며 20 000 번 지우고 새 키 넣기 (m = 64)
    for (int variant = 0; variant < 2; ++variant) {
        OpenTable tb(64); std::vector<unsigned> live; unsigned next = 1000;
        for (int i = 0; i < 30; i++) { tb.insert(next); live.push_back(next++); }
        for (int step = 0; step < 20000; ++step) { size_t at = rng() % live.size(); assert(tb.erase(live[at])); live[at] = next; tb.insert(next++); if (variant == 1 && tb.tombstones() > 16) tb.rebuild(); }
        tb.resetProbes(); const int Q = 2000; for (int q = 0; q < Q; q++) assert(!tb.find(900000u + (unsigned)q));
        double avg = (double)tb.probeCount() / Q;
        if (variant == 0) assert(avg > 40 && tb.tombstones() > 20); else assert(avg < 3.5);
    }
    // ⑤ 선형 탐사의 평균 탐사 수
    for (double alpha : {0.5, 0.8}) {
        const size_t m = 2048; const int trials = 120; double succProbes = 0, failProbes = 0; long succQ = 0, failQ = 0;
        for (int tr = 0; tr < trials; tr++) {
            OpenTable tb(m); std::vector<unsigned> keys; std::set<unsigned> present;
            while (keys.size() < (size_t)(alpha * m)) { unsigned k = (unsigned)rng(); if (present.insert(k).second) { tb.insert(k); keys.push_back(k); } }
            tb.resetProbes(); for (unsigned k : keys) tb.find(k); succProbes += (double)tb.probeCount(); succQ += (long)keys.size();
            tb.resetProbes(); int q = 0; while (q < 1000) { unsigned k = (unsigned)rng(); if (present.count(k)) continue; tb.find(k); ++q; } failProbes += (double)tb.probeCount(); failQ += 1000;
        }
        double s = succProbes / (double)succQ, f = failProbes / (double)failQ, ks = 0.5 * (1 + 1 / (1 - alpha)), kf = 0.5 * (1 + 1 / ((1 - alpha) * (1 - alpha)));
        assert(std::abs(s - ks) < 0.10 * ks && std::abs(f - kf) < 0.15 * kf);
    }
    // ⑥ 뒤로 밀기 삭제
    ShiftTable sh(128); std::set<unsigned> model;
    for (int step = 0; step < 40000; ++step) {
        unsigned k = (unsigned)(rng() % 150); int op = (int)(rng() % 10);
        if (op < 5) { bool want = !model.count(k) && model.size() < 128; bool got = sh.insert(k); assert(got == want); if (got) model.insert(k); }
        else if (op < 8) assert(sh.erase(k) == (model.erase(k) > 0));
        else assert(sh.find(k) == (model.count(k) > 0));
        assert(sh.size() == model.size()); if (step % 1000 == 0) assert(sh.valid());
    }
    assert(sh.valid());
    std::cout << "OpenAddressing verified." << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1/(1-α)), 최악 O(m)
// Space Complexity: O(m)
```
## LinearProbing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>

// 선형 탐사: h(k, i) = (h(k) + i) mod m. 충돌하면 바로 다음 칸을 본다. 캐시 친화적(이웃한 칸) 이고 구현이 가장 단순하지만, 점유된 연속 구간(클러스터)이 스스로 커지는 *1차 군집(primary clustering)* 이 생긴다 — 클러스터 위로 떨어진 키는 클러스터 끝까지 밀려나 그 길이를 늘리기 때문. 삭제는 묘비 없이 *뒤로 당기기(backward shift)* 로 한다.
// 정리 세 가지를 검증한다. (1) 탐사열 (h + i) mod m, i = 0..m−1 은 *모든 칸을 정확히 한 번씩* 방문한다(모든 m ≤ 40, h). (2) 같은 home 에 n 개 키를 넣으면 총 탐사 수가 정확히 n(n+1)/2 — 1차 군집의 이차 비용. (3) *순서 무관성*: 같은 키 집합을 어떤 순서로 넣어도 점유되는 칸의 집합과 변위(home 에서 떨어진 거리) 의 합이 같다(Knuth) — 그래서 삭제 후 다시 넣어도, 병렬로 넣어도 최종 배치의 "총 비용" 이 변하지 않는다.
// 검증: ④ 무작위 삽입·삭제·검색 20 만 번을 std::unordered_map 과 비교하며 200 번마다 불변식(모든 키가 home 에서 자기 칸까지 빈 칸 없이 닿음) 확인 ⑤ 가장 긴 클러스터가 α = 0.7, m = 100,003 에서 O(log m) 안쪽(≤ 18·ln m, 이론상 상수는 1/(α − 1 − ln α) ≈ 17.6; 실측 97) ⑥ 감김(wrap-around): home 이 m − 1 인 키들이 0 번 칸으로 이어진다.
struct Linear {
    std::vector<std::uint64_t> slot; std::size_t n = 0; long probes = 0; bool ident;           // 빈 칸 = 0, 키 0 은 쓰지 않는다. ident: 항등 해시(시연용)
    explicit Linear(std::size_t m, bool identity = false) : slot(m, 0), ident(identity) {}
    std::size_t home(std::uint64_t k) const { if (ident) return (std::size_t)(k % slot.size()); k += 0x9e3779b97f4a7c15ULL; k = (k ^ (k >> 30)) * 0xbf58476d1ce4e5b9ULL; k = (k ^ (k >> 27)) * 0x94d049bb133111ebULL; return (std::size_t)((k ^ (k >> 31)) % slot.size()); }
    bool insert(std::uint64_t k) { std::size_t i = home(k); while (true) { ++probes; if (!slot[i]) { slot[i] = k; ++n; return true; } if (slot[i] == k) return false; i = (i + 1) % slot.size(); } }
    bool contains(std::uint64_t k) const { std::size_t i = home(k); while (slot[i]) { if (slot[i] == k) return true; i = (i + 1) % slot.size(); } return false; }
    bool erase(std::uint64_t k) {                                                            // 뒤로 당기기
        std::size_t m = slot.size(), i = home(k); while (slot[i] && slot[i] != k) i = (i + 1) % m; if (!slot[i]) return false;
        slot[i] = 0; --n; std::size_t j = i;
        while (true) { j = (j + 1) % m; if (!slot[j]) break; std::size_t h = home(slot[j]); bool stays = i <= j ? (i < h && h <= j) : (i < h || h <= j); if (!stays) { slot[i] = slot[j]; slot[j] = 0; i = j; } }
        return true;
    }
    bool invariant() const { for (std::size_t i = 0; i < slot.size(); ++i) if (slot[i]) { std::size_t j = home(slot[i]); while (j != i) { if (!slot[j]) return false; j = (j + 1) % slot.size(); } } return true; }
    long displacement() const { long d = 0; for (std::size_t i = 0; i < slot.size(); ++i) if (slot[i]) d += (long)((i + slot.size() - home(slot[i])) % slot.size()); return d; }
};

int main() {
    // (1) 탐사열은 모든 칸을 정확히 한 번씩
    for (int m = 1; m <= 40; ++m) for (int h = 0; h < m; ++h) { std::set<int> seen; for (int i = 0; i < m; ++i) seen.insert((h + i) % m); assert((int)seen.size() == m); }
    // (2) 같은 home: n 개를 넣으면 총 탐사 n(n+1)/2 (home = 0 이 되도록 m 의 배수 키, 항등 해시)
    for (int n : {1, 2, 10, 100, 500}) { Linear t(1009, true); for (int i = 1; i <= n; ++i) assert(t.insert((std::uint64_t)i * 1009)); assert(t.probes == (long)n * (n + 1) / 2 && t.displacement() == (long)n * (n - 1) / 2); }
    // (3) 순서 무관성: 같은 키 집합을 200 가지 무작위 순서로 → 점유 칸 집합과 변위 합이 같다
    std::mt19937_64 rng(5);
    {   const std::size_t m = 257; std::vector<std::uint64_t> keys; std::set<std::uint64_t> uniq; while (keys.size() < 180) { std::uint64_t k = 1 + rng() % 100000; if (uniq.insert(k).second) keys.push_back(k); }
        Linear base(m); for (auto k : keys) base.insert(k); std::vector<char> occ(m); for (std::size_t i = 0; i < m; ++i) occ[i] = base.slot[i] != 0; long disp = base.displacement();
        for (int t = 0; t < 200; ++t) { std::shuffle(keys.begin(), keys.end(), rng); Linear x(m); for (auto k : keys) x.insert(k); for (std::size_t i = 0; i < m; ++i) assert((x.slot[i] != 0) == (bool)occ[i]); assert(x.displacement() == disp && x.invariant()); } }
    // ④ 무작위 연산 20 만 번 (α ≈ 0.7 근처), 200 번마다 불변식
    {   Linear t(2003); std::unordered_map<std::uint64_t, int> ref; long erased = 0;
        for (int i = 0; i < 200000; ++i) {
            std::uint64_t k = 1 + rng() % 3000; int op = (int)(rng() % 3);
            if (op == 0 && ref.size() < 1400) { bool r = ref.emplace(k, 1).second; assert(t.insert(k) == r); } else if (op == 1) { bool r = ref.erase(k) > 0; erased += r; assert(t.erase(k) == r); } else assert(t.contains(k) == (ref.count(k) > 0));
            if (i % 200 == 0) assert(t.invariant() && t.n == ref.size());
        }
        for (auto& kv : ref) assert(t.contains(kv.first)); assert(erased > 20000); }
    // ⑤ 가장 긴 클러스터: α = 0.7, m = 100,003 에서 O(log m)
    {   const std::size_t m = 100003; Linear t(m); while (t.n < (std::size_t)(0.7 * m)) t.insert(rng() | 1); std::size_t best = 0, run = 0; for (int pass = 0; pass < 2; ++pass) for (std::size_t i = 0; i < m; ++i) { run = t.slot[i] ? run + 1 : 0; best = std::max(best, run); }
        assert(best >= 40 && (double)best <= 18 * std::log((double)m)); std::cout << "LinearProbing: longest cluster at alpha 0.7, m = 100003 was " << best << " slots (18 ln m = " << 18 * std::log((double)m) << ")" << std::endl; }
    // ⑥ 감김: home 이 m − 1 인 키 5 개가 m − 1, 0, 1, 2, 3 번 칸에
    {   Linear t(11, true); for (int i = 1; i <= 5; ++i) t.insert((std::uint64_t)(i - 1) * 11 + 10); for (int s : {10, 0, 1, 2, 3}) assert(t.slot[s] != 0); assert(t.invariant() && t.contains(21) && t.erase(10 + 11 * 3) && t.invariant() && !t.contains(43)); }                // 키 10, 21, 32, 43, 54 가 모두 home = 10
    std::cout << "LinearProbing: the probe sequence visited every slot exactly once for all m <= 40, n keys with one home cost exactly n(n+1)/2 probes, 200 random insertion orders of the same keys produced the same occupied slots and the same total displacement, and 200,000 random insert/erase/find operations with backward-shift deletion matched std::unordered_map while the cluster invariant held" << std::endl; return 0;
}
// Time Complexity: 성공 탐색 ≈ ½(1 + 1/(1−α)), 실패 탐색 ≈ ½(1 + 1/(1−α)²)
// Space Complexity: O(m)
```
## QuadraticProbing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>

// 이차 탐사: h(k, i) = (h(k) + c₁·i + c₂·i²) mod m. 대표 두 가지 — ① m = 2^p 에서 *삼각수* h + i(i+1)/2 : 처음 m 번의 탐사가 모든 칸을 정확히 한 번씩 방문한다(순열). ② m 이 소수일 때 h + i² : 처음 (m+1)/2 번의 탐사는 모두 다르지만 그 이후는 되풀이되므로 *적재율이 ½ 미만이면 삽입이 항상 성공* 하고, ½ 이상이면 빈 칸이 남아 있어도 삽입이 실패할 수 있다. m 이 합성수이면 i² 탐사가 모든 칸을 못 덮는다. 선형 탐사의 1차 군집은 없지만 *같은 home 의 키는 탐사열이 완전히 같아* 2차 군집(secondary clustering) 이 남는다.
// 삭제는 묘비(DEAD)를 쓴다: 검색은 묘비를 지나치고, 삽입은 묘비를 재사용한다(단, 같은 키가 더 뒤에 없는지 확인한 뒤).
// 검증: ① 삼각수 탐사가 m = 2^p (p ≤ 10) 의 모든 home 에서 순열 ② 모든 소수 m ≤ 200, 모든 home 에서 처음 (m+1)/2 개 탐사 h + i² 가 서로 다르고 그 뒤로 (m+1)/2 번째 이후 새 칸을 만들지 않음 ③ 모든 합성수 m (4 ≤ m ≤ 60) 에서 i² 탐사가 방문하는 칸 수 < m ④ 소수 m = 101 에서 키 50 개(α < ½)는 어떤 무작위 순서·충돌 패턴에서도 삽입 성공, m = 7 에서 같은 home 키 5 개(α = 5/7) 중 다섯 번째는 빈 칸이 둘 남았는데도 실패 ⑤ 삼각수 탐사 표를 unordered_map 과 20 만 번 비교(묘비 포함) ⑥ 같은 home 의 두 키는 탐사열이 같다(2차 군집) ⑦ m = 2^17, α = 0.5 에서 평균 탐사 수가 Knuth 근사식(성공 1 − ln(1−α) − α/2 = 1.443, 실패 1/(1−α) − α − ln(1−α) = 2.193)의 ±6%.
std::size_t mix(std::uint64_t k) { k += 0x9e3779b97f4a7c15ULL; k = (k ^ (k >> 30)) * 0xbf58476d1ce4e5b9ULL; k = (k ^ (k >> 27)) * 0x94d049bb133111ebULL; return (std::size_t)(k ^ (k >> 31)); }
struct Quad {                                                                                // m 은 2의 거듭제곱 (삼각수 탐사)
    enum : std::uint8_t { EMPTY, FULL, DEAD }; std::vector<std::uint8_t> st; std::vector<std::uint64_t> key; std::size_t m, live = 0, used = 0; long probes = 0;                // used = FULL + DEAD 칸 수
    explicit Quad(std::size_t mm) : st(mm, EMPTY), key(mm, 0), m(mm) {}
    std::size_t at(std::uint64_t k, std::size_t i) const { return (mix(k) + i * (i + 1) / 2) & (m - 1); }
    bool insert(std::uint64_t k) {
        std::size_t firstFree = m; for (std::size_t i = 0; i < m; ++i) { std::size_t s = at(k, i); ++probes; if (st[s] == FULL) { if (key[s] == k) return false; } else { if (firstFree == m) firstFree = s; if (st[s] == EMPTY) break; } }
        if (firstFree == m) return false; used += st[firstFree] == EMPTY; st[firstFree] = FULL; key[firstFree] = k; ++live; return true;
    }
    bool contains(std::uint64_t k, long* pr = nullptr) const { for (std::size_t i = 0; i < m; ++i) { std::size_t s = at(k, i); if (pr) ++*pr; if (st[s] == EMPTY) return false; if (st[s] == FULL && key[s] == k) return true; } return false; }
    bool erase(std::uint64_t k) { for (std::size_t i = 0; i < m; ++i) { std::size_t s = at(k, i); if (st[s] == EMPTY) return false; if (st[s] == FULL && key[s] == k) { st[s] = DEAD; --live; return true; } } return false; }
    void rebuild() { std::vector<std::uint64_t> keep; for (std::size_t s = 0; s < m; ++s) if (st[s] == FULL) keep.push_back(key[s]); std::fill(st.begin(), st.end(), (std::uint8_t)EMPTY); live = used = 0; for (auto k : keep) insert(k); }       // 묘비가 쌓이면 재구성
};

int main() {
    std::mt19937_64 rng(6);
    // ① 삼각수 탐사 = 순열 (m = 2^p)
    for (int p = 0; p <= 10; ++p) { std::size_t m = (std::size_t)1 << p; for (std::size_t h = 0; h < m; h += (m > 64 ? 17 : 1)) { std::set<std::size_t> seen; for (std::size_t i = 0; i < m; ++i) seen.insert((h + i * (i + 1) / 2) & (m - 1)); assert(seen.size() == m); } }
    // ② 소수 m: h + i² 의 처음 (m+1)/2 개가 서로 다르고 전체 방문 칸 수도 정확히 (m+1)/2
    for (int m = 3; m <= 200; ++m) { bool prime = true; for (int d = 2; d * d <= m; ++d) prime = prime && m % d; if (!prime) continue;
        for (int h = 0; h < m; ++h) { std::set<int> first; for (int i = 0; i <= (m - 1) / 2; ++i) first.insert((h + i * i) % m); assert((int)first.size() == (m + 1) / 2); std::set<int> all; for (int i = 0; i < m; ++i) all.insert((h + i * i) % m); assert(all.size() == first.size()); } }
    // ③ 합성수 m: i² 탐사는 모든 칸을 덮지 못한다
    for (int m = 4; m <= 60; ++m) { bool prime = true; for (int d = 2; d * d <= m; ++d) prime = prime && m % d; if (prime) continue; std::set<int> all; for (int i = 0; i < m; ++i) all.insert(i * i % m); assert((int)all.size() < m); }
    // ④ 소수 m = 101, α < ½: 같은 home 에 몰리는 최악 패턴을 포함해 항상 성공. m = 7 에서 α = 5/7 이면 실패하는 반례
    {   const int m = 101; int fails = 0;
        for (int trial = 0; trial < 3000; ++trial) { std::vector<char> used(m, 0); for (int c = 0; c < 50; ++c) { int h = trial % 3 == 0 ? 17 : (int)(rng() % m); bool ok = false; for (int i = 0; i <= (m - 1) / 2; ++i) { int s = (h + i * i) % m; if (!used[s]) { used[s] = 1; ok = true; break; } } fails += !ok; } }
        assert(fails == 0);
        std::vector<char> used(7, 0); int placed = 0; for (int c = 0; c < 5; ++c) { bool ok = false; for (int i = 0; i <= 3; ++i) { int s = (2 + i * i) % 7; if (!used[s]) { used[s] = 1; ok = true; break; } } placed += ok; }
        assert(placed == 4 && std::count(used.begin(), used.end(), 0) == 3);               // 같은 home 에서 4 개만 들어가고 다섯 번째는 빈 칸이 3 개나 남아 있어도 실패
    }
    // ⑤ 삼각수 탐사 표 vs unordered_map (α ≤ 0.7, 묘비 포함) 20 만 번
    {   Quad t(2048); std::unordered_map<std::uint64_t, int> ref;
        for (int i = 0; i < 200000; ++i) { std::uint64_t k = 1 + rng() % 3000; int op = (int)(rng() % 3);
            if (t.used >= 1400) t.rebuild();                                                                        // 묘비 포함 점유가 α = 0.7 에 닿으면 재구성
            if (op == 0 && t.live < 1100) { bool r = ref.emplace(k, 1).second; assert(t.insert(k) == r); }
            else if (op == 1) { bool r = ref.erase(k) > 0; assert(t.erase(k) == r); } else assert(t.contains(k) == (ref.count(k) > 0)); }
        for (auto& kv : ref) assert(t.contains(kv.first)); assert(t.live == ref.size()); }
    // ⑥ 2차 군집: home 이 같으면 탐사열이 같다
    { Quad t(1024); for (int a = 0; a < 5000; ++a) { std::uint64_t k1 = rng(), k2 = rng(); if (mix(k1) % 1024 != mix(k2) % 1024) continue; for (std::size_t i = 0; i < 20; ++i) assert(t.at(k1, i) == t.at(k2, i)); } }
    // ⑦ m = 2^17, α = 0.5 의 평균 탐사 수
    {   const std::size_t m = 1u << 17; Quad t(m); std::vector<std::uint64_t> keys; while (t.live < m / 2) { std::uint64_t k = rng() | 1; if (t.insert(k)) keys.push_back(k); }
        long ps = 0; for (auto k : keys) { long pr = 0; t.contains(k, &pr); ps += pr; } long pf = 0; for (int i = 0; i < 200000; ++i) { long pr = 0; t.contains(rng() & ~1ULL, &pr); pf += pr; }
        double succ = (double)ps / (double)keys.size(), fail = (double)pf / 200000.0; assert(std::abs(succ - 1.443) < 0.06 * 1.443 && std::abs(fail - 2.193) < 0.06 * 2.193);
        std::cout << "QuadraticProbing: triangular probing visited every slot for all power-of-two sizes up to 1024, h + i^2 probing on every prime up to 200 touched exactly (m+1)/2 distinct slots, composite sizes never covered the table, 3000 trials of 50 inserts into a prime table of size 101 never failed while a 5th same-home key in a table of 7 failed with 3 slots empty, 200,000 random operations with tombstones matched std::unordered_map, same-home keys shared one probe sequence, and at alpha 0.5 the measured probes (successful " << succ << ", unsuccessful " << fail << ") matched Knuth's approximations" << std::endl; }
    return 0;
}
// Time Complexity: 평균 O(1/(1−α)), 군집은 선형 탐사보다 완화
// Space Complexity: O(m)
```
## DoubleHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// 이중 해싱: h(k, i) = (h₁(k) + i·h₂(k)) mod m. 두 번째 해시가 *걸음 폭* 을 키마다 다르게 정해서, 같은 home 의 키도 서로 다른 간격으로 튀므로 1차·2차 군집이 모두 사라진다(균등 해싱의 가장 좋은 근사). 탐사열이 모든 칸을 덮으려면 h₂(k) 와 m 이 서로소여야 한다 — 정리: 방문하는 서로 다른 칸 수는 정확히 m / gcd(h₂, m). 그래서 m 이 소수면 h₂ = 1 + (k mod (m−1)) ∈ [1, m−1] 이면 충분하고, m = 2^p 이면 h₂ 를 홀수로 만든다(h₂ | 1). h₂ 가 0 이 되면 같은 칸만 맴돈다.
// 검증: ① 모든 소수 m ≤ 100 · h₂ ∈ [1, m−1] · h₁ 에서 탐사열이 순열, m = 64 는 모든 홀수 h₂ 에서 순열 ② 합성수 m ≤ 40, h₂ ∈ [1, m−1] 에서 방문 칸 수가 정확히 m / gcd(h₂, m) ③ 묘비를 쓰는 소수 크기 표를 unordered_map 과 20 만 번 비교 ④ 같은 h₁ 인 키 1000 개의 두 번째 탐사 칸이 거의 다 다르다(≥ 90%) — 선형 탐사는 모두 같음 ⑤ 시뮬레이션(m = 100,003): 실패 탐색 평균이 α = 0.5, 0.7 에서 균등 해싱 이론값 1/(1−α) 의 ±5%, 성공 탐색이 (1/α)·ln(1/(1−α)) 의 ±5%, α = 0.9 에서 이중 해싱의 실패 탐사가 선형 탐사의 1/3 미만.
std::uint64_t mix(std::uint64_t k) { k += 0x9e3779b97f4a7c15ULL; k = (k ^ (k >> 30)) * 0xbf58476d1ce4e5b9ULL; k = (k ^ (k >> 27)) * 0x94d049bb133111ebULL; return k ^ (k >> 31); }
struct Dbl {                                                                                  // m 은 소수
    enum : std::uint8_t { EMPTY, FULL, DEAD }; std::vector<std::uint8_t> st; std::vector<std::uint64_t> key; std::size_t m, live = 0;
    explicit Dbl(std::size_t mm) : st(mm, EMPTY), key(mm, 0), m(mm) {}
    std::size_t h1(std::uint64_t k) const { return (std::size_t)(mix(k) % m); }
    std::size_t h2(std::uint64_t k) const { return 1 + (std::size_t)((mix(k ^ 0xabcdefULL) >> 8) % (m - 1)); }
    std::size_t at(std::uint64_t k, std::size_t i) const { return (h1(k) + i * h2(k)) % m; }
    bool insert(std::uint64_t k) {
        std::size_t firstFree = m; for (std::size_t i = 0; i < m; ++i) { std::size_t s = at(k, i); if (st[s] == FULL) { if (key[s] == k) return false; } else { if (firstFree == m) firstFree = s; if (st[s] == EMPTY) break; } }
        if (firstFree == m) return false; st[firstFree] = FULL; key[firstFree] = k; ++live; return true;
    }
    bool contains(std::uint64_t k, long* pr = nullptr) const { for (std::size_t i = 0; i < m; ++i) { std::size_t s = at(k, i); if (pr) ++*pr; if (st[s] == EMPTY) return false; if (st[s] == FULL && key[s] == k) return true; } return false; }
    bool erase(std::uint64_t k) { for (std::size_t i = 0; i < m; ++i) { std::size_t s = at(k, i); if (st[s] == EMPTY) return false; if (st[s] == FULL && key[s] == k) { st[s] = DEAD; --live; return true; } } return false; }
};
struct LinearSim {                                                                            // 비교용 선형 탐사 (삭제 없음)
    std::vector<std::uint64_t> slot; std::size_t n = 0; explicit LinearSim(std::size_t m) : slot(m, 0) {}
    bool insert(std::uint64_t k) { std::size_t i = (std::size_t)(mix(k) % slot.size()); while (slot[i]) { if (slot[i] == k) return false; i = (i + 1) % slot.size(); } slot[i] = k; ++n; return true; }
    long failProbes(std::uint64_t k) const { std::size_t i = (std::size_t)(mix(k) % slot.size()); long p = 1; while (slot[i]) { i = (i + 1) % slot.size(); ++p; } return p; }
};

int main() {
    // ① 소수 m: 모든 (h1, h2) 가 순열. m = 64: 홀수 h2 만 순열
    for (int m = 2; m <= 100; ++m) { bool prime = true; for (int d = 2; d * d <= m; ++d) prime = prime && m % d; if (!prime) continue; for (int h2 = 1; h2 < m; ++h2) for (int h1 = 0; h1 < m; h1 += 7) { std::set<int> seen; for (int i = 0; i < m; ++i) seen.insert((h1 + i * h2) % m); assert((int)seen.size() == m); } }
    for (int h2 = 1; h2 < 64; ++h2) { std::set<int> seen; for (int i = 0; i < 64; ++i) seen.insert((5 + i * h2) % 64); assert((seen.size() == 64) == (h2 % 2 == 1)); }
    // ② 합성수 m: 방문 칸 수 = m / gcd(h2, m)
    for (int m = 4; m <= 40; ++m) for (int h2 = 1; h2 < m; ++h2) { std::set<int> seen; for (int i = 0; i < m; ++i) seen.insert((3 + i * h2) % m); assert((int)seen.size() == m / std::gcd(h2, m)); }
    // ③ 소수 크기 표 vs unordered_map (묘비 포함, 살아 있는 키 ≤ 0.7 m)
    std::mt19937_64 rng(7);
    {   Dbl t(2003); std::unordered_map<std::uint64_t, int> ref;
        for (int i = 0; i < 200000; ++i) { std::uint64_t k = 1 + rng() % 3000; int op = (int)(rng() % 3);
            if (op == 0 && ref.size() < 1400) { bool r = ref.emplace(k, 1).second; assert(t.insert(k) == r); } else if (op == 1) { bool r = ref.erase(k) > 0; assert(t.erase(k) == r); } else assert(t.contains(k) == (ref.count(k) > 0)); }
        for (auto& kv : ref) assert(t.contains(kv.first)); assert(t.live == ref.size()); }
    // ④ 같은 h1 인 키 1000 개: 이중 해싱의 두 번째 탐사 칸이 거의 다 다르다, 선형 탐사는 모두 같다(home + 1)
    {   Dbl t(10007); std::vector<std::uint64_t> same; while (same.size() < 1000) { std::uint64_t k = rng(); if (t.h1(k) == 5) same.push_back(k); }
        std::set<std::size_t> second; for (auto k : same) second.insert(t.at(k, 1)); assert(second.size() >= 900); }
    // ⑤ 시뮬레이션: m = 100,003 (소수)
    const std::size_t m = 100003;
    for (double alpha : {0.5, 0.7}) {
        Dbl t(m); std::vector<std::uint64_t> keys; while (t.live < (std::size_t)(alpha * (double)m)) { std::uint64_t k = rng() | 1; if (t.insert(k)) keys.push_back(k); }
        long ps = 0; for (auto k : keys) { long pr = 0; t.contains(k, &pr); ps += pr; } long pf = 0; const int trials = 200000; for (int i = 0; i < trials; ++i) { long pr = 0; t.contains(rng() & ~1ULL, &pr); pf += pr; }
        double succ = (double)ps / (double)keys.size(), fail = (double)pf / trials, thSucc = std::log(1 / (1 - alpha)) / alpha, thFail = 1 / (1 - alpha);
        assert(std::abs(succ - thSucc) < 0.05 * thSucc && std::abs(fail - thFail) < 0.05 * thFail);
    }
    {   Dbl d(m); LinearSim l(m); std::size_t n = (std::size_t)(0.9 * (double)m); while (d.live < n) { std::uint64_t k = rng() | 1; d.insert(k); l.insert(k); }
        long pd = 0, pl = 0; for (int i = 0; i < 100000; ++i) { std::uint64_t k = rng() & ~1ULL; long pr = 0; d.contains(k, &pr); pd += pr; pl += l.failProbes(k); }
        double dd = (double)pd / 100000, ll = (double)pl / 100000; assert(dd * 3 < ll);
        std::cout << "DoubleHashing: probe sequences were permutations for every prime size up to 100 and every step in [1, m-1] (and for odd steps modulo 64), a composite size visited exactly m/gcd(h2,m) slots, a prime table with tombstones matched std::unordered_map over 200,000 operations, same-home keys fanned out to 900+ different second slots, measured probe counts at alpha 0.5 and 0.7 matched the uniform-hashing formulas within 5%, and at alpha 0.9 an unsuccessful search needed " << dd << " probes against " << ll << " for linear probing" << std::endl; }
    return 0;
}
// Time Complexity: 평균 O(1/(1−α)) (1차·2차 군집 없음)
// Space Complexity: O(m)
```
## RobinHoodHashing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <vector>
#include <cassert>

// 로빈 후드: 홈에서 더 멀리 떨어진 원소(가난한 쪽)가 가까운 원소(부자)의 자리를 빼앗는다 -> 탐사 거리의 분산이 줄어든다.
// 삭제는 뒤 원소들을 한 칸씩 앞으로 당기는 후방 이동(backward shift)이라 묘비가 필요 없다.
struct Slot { uint64_t key = 0; int dist = -1; };                // dist < 0 이면 빈 칸
static uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }

class RobinHood {
    std::vector<Slot> t;
public:
    explicit RobinHood(size_t m) : t(m) {}
    void insert(uint64_t k) {
        size_t i = mix(k) % t.size();
        Slot cur{k, 0};
        while (t[i].dist >= 0) {
            if (t[i].dist < cur.dist) std::swap(t[i], cur);     // 더 가난한 쪽이 자리를 차지한다
            i = (i + 1) % t.size();
            cur.dist++;
        }
        t[i] = cur;
    }
    bool find(uint64_t k) const {
        size_t i = mix(k) % t.size();
        for (int d = 0; ; d++, i = (i + 1) % t.size()) {
            if (t[i].dist < d) return false;                     // 이 키가 있었다면 여기까지 오기 전에 자리 잡았을 것
            if (t[i].key == k) return true;
        }
    }
    bool erase(uint64_t k) {
        size_t i = mix(k) % t.size();
        for (int d = 0; ; d++, i = (i + 1) % t.size()) {
            if (t[i].dist < d) return false;
            if (t[i].key == k) break;
        }
        size_t j = (i + 1) % t.size();
        while (t[j].dist > 0) { t[i] = {t[j].key, t[j].dist - 1}; i = j; j = (j + 1) % t.size(); }
        t[i] = Slot{};
        return true;
    }
    double variance() const {
        double s = 0, s2 = 0; int n = 0;
        for (auto& x : t) if (x.dist >= 0) { s += x.dist; s2 += double(x.dist) * x.dist; n++; }
        double mean = s / n; return s2 / n - mean * mean;
    }
};

// 비교 대상: 같은 키를 선형 탐사로 넣었을 때의 탐사 거리 분산
double linearVariance(const std::vector<uint64_t>& keys, size_t m) {
    std::vector<int> d(m, -1);
    for (uint64_t k : keys) { size_t i = mix(k) % m; int step = 0; while (d[i] >= 0) { i = (i + 1) % m; step++; } d[i] = step; }
    double s = 0, s2 = 0; int n = 0;
    for (int x : d) if (x >= 0) { s += x; s2 += double(x) * x; n++; }
    double mean = s / n; return s2 / n - mean * mean;
}

int main() {
    const size_t m = 1024, n = 870;                             // 적재율 약 0.85
    std::mt19937_64 rng(3);
    std::vector<uint64_t> keys(n);
    RobinHood rh(m);
    for (auto& k : keys) { k = rng() | 1; rh.insert(k); }
    for (uint64_t k : keys) assert(rh.find(k));
    assert(rh.variance() < linearVariance(keys, m));            // 평균은 같고 분산은 더 작다
    for (size_t i = 0; i < n; i += 2) assert(rh.erase(keys[i]));
    for (size_t i = 0; i < n; i++) assert(rh.find(keys[i]) == (i % 2 == 1));
    std::cout << "variance: robin-hood " << rh.variance() << " vs linear " << linearVariance(keys, m) << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 탐색 실패 시 조기 종료
// Space Complexity: O(m)
```
## CuckooHashing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <random>
#include <cassert>

// 뻐꾸기 해싱: 해시 함수 2개, 테이블 2개. 키는 항상 두 후보 칸 중 하나에만 있으므로 탐색은 최악도 2번 확인
class Cuckoo {
    std::vector<int64_t> t1, t2;                                 // -1 = 빈 칸
    uint64_t s1, s2;
    size_t m;
    std::mt19937_64 rng{42};
    static uint64_t mix(uint64_t x) { x *= 0x9e3779b97f4a7c15ULL; x ^= x >> 32; x *= 0xd6e8feb86659fd93ULL; return x ^ (x >> 32); }
    size_t h1(int64_t k) const { return mix(k ^ s1) % m; }
    size_t h2(int64_t k) const { return mix(k ^ s2) % m; }
    // 밀어내기를 최대 64번. 실패하면 k 에 "집을 잃은 키"가 남아 있다 (테이블의 나머지는 일관됨)
    bool place(int64_t& k) {
        for (int kicks = 0; kicks < 64; kicks++) {
            std::swap(k, t1[h1(k)]);  if (k < 0) return true;
            std::swap(k, t2[h2(k)]);  if (k < 0) return true;
        }
        return false;
    }
    void rehash(int64_t homeless) {                              // 순환 발생: 크기를 키우고 해시 함수를 새로 뽑는다
        std::vector<int64_t> all{homeless};
        for (auto x : t1) if (x >= 0) all.push_back(x);
        for (auto x : t2) if (x >= 0) all.push_back(x);
        m *= 2;
        for (;;) {
            s1 = rng(); s2 = rng();
            t1.assign(m, -1); t2.assign(m, -1);
            bool ok = true;
            for (auto x : all) { int64_t cur = x; if (!place(cur)) { ok = false; break; } }
            if (ok) return;
        }
    }
public:
    explicit Cuckoo(size_t size) : t1(size, -1), t2(size, -1), s1(1), s2(2), m(size) {}
    bool contains(int64_t k) const { return t1[h1(k)] == k || t2[h2(k)] == k; }
    void insert(int64_t k) {
        if (contains(k)) return;
        if (!place(k)) rehash(k);
    }
    size_t capacity() const { return 2 * m; }
};

int main() {
    Cuckoo c(16);
    for (int64_t k = 0; k < 1000; k++) c.insert(k * 7919 + 13);
    for (int64_t k = 0; k < 1000; k++) assert(c.contains(k * 7919 + 13));
    assert(!c.contains(100000000 - 5));
    std::cout << "Cuckoo: 1000 keys in capacity " << c.capacity() << std::endl;
    return 0;
}
// Time Complexity: 탐색 O(1) 최악, 삽입 분할상환 O(1)
// Space Complexity: O(n)  (적재율 약 50% 이하에서 안정)
```
## HopscotchHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 홉스카치 해싱: 모든 키가 홈 버킷에서 H칸 이내(이웃 영역)에 있도록 유지한다.
// 홈 버킷마다 H비트 비트맵을 두어 이웃 영역 안의 점유 위치만 확인하면 되므로 탐색이 캐시 친화적이다.
// 삽입은 가장 가까운 빈 칸을 찾은 뒤, 너무 멀면 앞쪽 원소를 그 빈 칸으로 옮겨(자기 이웃 영역을 지키는 범위에서) 빈 칸을 홈 쪽으로 끌어온다.  끌어올 수 없으면 실패(테이블 확장 필요)
// 검증: ① 손으로 짠 예  ② H = 8 테이블을 std::set 과 대조(삽입 실패 시 테이블 불변, 삭제 후 재삽입)하고 불변식 확인: 비트맵이 가리키는 칸의 키는 홈이 그 버킷이고,
//        점유된 칸은 정확히 하나의 비트가 가리키며 거리 < H, 조회가 비교하는 칸 수 ≤ H   ③ H 가 클수록 더 높은 적재율까지 실패 없이 채워진다 (H = 4, 8, 16, 32 의 첫 실패 때 평균 적재율)
template <int H>
class Hopscotch {
    std::vector<int64_t> key; std::vector<uint8_t> used; std::vector<uint32_t> hop;          // hop[b]의 비트 d = (b+d)번 칸이 b가 홈인 원소를 담음
    size_t m, n = 0;
    size_t home(int64_t k) const { return (((uint64_t)k * 11400714819323198485ULL) >> 40) % m; }
    size_t dist(size_t from, size_t to) const { return (to + m - from) % m; }
public:
    mutable long compared = 0;                                    // 조회가 키를 비교한 횟수 (분석용)
    explicit Hopscotch(size_t size) : key(size), used(size, 0), hop(size, 0), m(size) {}
    bool contains(int64_t k) const {
        size_t b = home(k);
        for (int d = 0; d < H; d++) if ((hop[b] >> d & 1) && (++compared, key[(b + d) % m] == k)) return true;
        return false;
    }
    bool insert(int64_t k) {
        if (contains(k)) return true;
        size_t b = home(k), j = b;
        size_t steps = 0;
        while (used[j] && steps < m) { j = (j + 1) % m; steps++; }          // 가장 가까운 빈 칸
        if (used[j]) return false;
        while (dist(b, j) >= (size_t)H) {                                   // 너무 멀면 이웃 안으로 끌어온다
            bool moved = false;
            for (size_t back = H - 1; back >= 1 && !moved; back--) {
                size_t p = (j + m - back) % m;                              // j 앞쪽 후보 칸
                if (!used[p]) continue;
                size_t hp = home(key[p]);
                if (dist(hp, j) < (size_t)H) {                              // p의 원소를 j로 옮겨도 이웃 규칙을 지킨다
                    hop[hp] &= ~(1u << dist(hp, p));
                    hop[hp] |= (1u << dist(hp, j));
                    key[j] = key[p]; used[j] = 1; used[p] = 0;
                    j = p; moved = true;
                }
            }
            if (!moved) return false;                                       // 재배치 불가 -> 테이블 확장 필요
        }
        key[j] = k; used[j] = 1; ++n;
        hop[b] |= (1u << dist(b, j));
        return true;
    }
    bool erase(int64_t k) {
        size_t b = home(k);
        for (int d = 0; d < H; d++)
            if ((hop[b] >> d & 1) && key[(b + d) % m] == k) { used[(b + d) % m] = 0; hop[b] &= ~(1u << d); --n; return true; }
        return false;
    }
    size_t size() const { return n; }
    size_t capacity() const { return m; }
    bool valid() const {
        std::vector<int> cover(m, 0); size_t usedCount = 0;
        for (size_t b = 0; b < m; b++) for (int d = 0; d < H; d++) if (hop[b] >> d & 1) {
            size_t s = (b + d) % m; if (!used[s] || home(key[s]) != b) return false; ++cover[s];
        }
        for (size_t s = 0; s < m; s++) { if (used[s]) { ++usedCount; if (cover[s] != 1) return false; } else if (cover[s] != 0) return false; }
        return usedCount == n;
    }
};

int main() {
    Hopscotch<8> t(128);
    int inserted = 0;
    for (int64_t k = 1; k <= 90; k++) if (t.insert(k * 1000003)) inserted++;     // 적재율 약 0.7
    assert(inserted >= 85);
    int found = 0;
    for (int64_t k = 1; k <= 90; k++) if (t.contains(k * 1000003)) found++;
    assert(found == inserted);
    assert(t.erase(1000003) && !t.contains(1000003) && t.valid());
    // ② std::set 대조
    std::mt19937_64 rng(17); long fails = 0, ops = 0, maxCompared = 0;
    for (int round = 0; round < 40; ++round) {
        Hopscotch<8> h(256); std::set<int64_t> model;
        for (int step = 0; step < 2000; ++step) {
            int64_t k = (int64_t)(rng() % 400) - 100; int op = (int)(rng() % 10);                                // 음수 키 포함
            if (op < 6) { size_t before = h.size(); bool ok = h.insert(k); if (ok) model.insert(k); else { ++fails; assert(h.size() == before && !model.count(k)); } }
            else if (op < 8) assert(h.erase(k) == (model.erase(k) > 0));
            else { h.compared = 0; assert(h.contains(k) == (model.count(k) > 0)); maxCompared = std::max<long>(maxCompared, h.compared); }
            assert(h.size() == model.size()); ++ops;
        }
        assert(h.valid()); for (int64_t k = -100; k < 300; k++) assert(h.contains(k) == (model.count(k) > 0));
    }
    assert(maxCompared <= 8 && ops == 80000 && fails > 0);
    // ③ H 와 적재율
    double avgLoad[4];
    for (int idx = 0; idx < 4; ++idx) {
        double sum = 0; const int trials = 30;
        for (int tr = 0; tr < trials; ++tr) {
            const size_t m = 1024; size_t count = 0;
            auto fill = [&](auto& table) { for (;;) { int64_t k = (int64_t)(rng() >> 1); if (!table.insert(k)) break; if (++count >= m) break; } };
            if (idx == 0) { Hopscotch<4> tb(m); fill(tb); } else if (idx == 1) { Hopscotch<8> tb(m); fill(tb); } else if (idx == 2) { Hopscotch<16> tb(m); fill(tb); } else { Hopscotch<32> tb(m); fill(tb); }
            sum += (double)count / m;
        }
        avgLoad[idx] = sum / trials;
    }
    assert(avgLoad[0] < avgLoad[1] && avgLoad[1] < avgLoad[2] && avgLoad[2] < avgLoad[3] && avgLoad[3] > 0.9);
    std::cout << "Hopscotch inserted " << inserted << "/90, all found; load at first failure H=4/8/16/32: " << avgLoad[0] << " " << avgLoad[1] << " " << avgLoad[2] << " " << avgLoad[3] << std::endl;
    return 0;
}
// Time Complexity: 탐색 O(H), 삽입 평균 O(1)
// Space Complexity: O(m)
```
## CoalescedHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 병합 해싱: 개방 주소법처럼 테이블 안에 저장하되 충돌 원소를 next 인덱스로 연결한다.
// 주소 영역(앞쪽)과 cellar(뒤쪽)를 나누고, 충돌 시 비어 있는 칸을 뒤에서부터 찾아 쓴다 → 충돌한 키들은 먼저 cellar 로 들어가 주소 영역의 자리를 빼앗지 않는다.
// 서로 다른 홈의 사슬이 한 칸에서 합쳐질 수 있다(coalesce) — 그래서 이름이 병합.  삭제는 사슬을 끊으면 다른 사슬이 잘려 복잡하므로(Vitter 의 알고리즘) 여기서는 삽입·조회만 다룬다
// 검증: ① 손으로 짠 예  ② 무작위 삽입을 std::set 과 대조(가득 차면 실패)하고 불변식: 모든 키가 홈에서 next 를 따라가면 닿고, 사슬에 순환이 없고, 칸 수 = 키 수, 충돌로 밀려난 첫 키들은 cellar(뒤쪽)에 놓인다
//        ③ 적재율 0.9 에서 성공 조회의 평균 탐사 수가 같은 크기의 선형 탐사보다 적다  ④ 모든 키가 같은 홈에 몰려도(최악) 사슬이 하나로 이어져 모두 찾을 수 있다
class Coalesced {
    struct Slot { int key = 0; int next = -1; bool used = false; };
    std::vector<Slot> t;
    size_t addr;                                                  // 주소 영역 크기
    long freePtr;
    size_t n = 0;
    size_t h(int k) const { return (size_t)(unsigned)k % addr; }
public:
    mutable long visited = 0;                                     // 조회가 방문한 칸 수 (분석용)
    Coalesced(size_t total, size_t addressRegion) : t(total), addr(addressRegion), freePtr((long)total - 1) {}
    bool insert(int k) {
        size_t i = h(k);
        if (!t[i].used) { t[i] = {k, -1, true}; ++n; return true; }
        for (;;) {
            if (t[i].key == k) return true;
            if (t[i].next < 0) break;
            i = t[i].next;
        }
        while (freePtr >= 0 && t[freePtr].used) freePtr--;
        if (freePtr < 0) return false;                            // 가득 참
        t[freePtr] = {k, -1, true}; ++n;
        t[i].next = (int)freePtr;
        return true;
    }
    bool find(int k) const {
        size_t i = h(k);
        if (!t[i].used) return false;
        for (;;) {
            ++visited;
            if (t[i].key == k) return true;
            if (t[i].next < 0) return false;
            i = t[i].next;
        }
    }
    size_t size() const { return n; }
    long placeOf(int k) const { size_t i = h(k); if (!t[i].used) return -1; for (;;) { if (t[i].key == k) return (long)i; if (t[i].next < 0) return -1; i = t[i].next; } }
    bool valid() const {
        size_t usedCount = 0; for (auto& s : t) usedCount += s.used;
        if (usedCount != n) return false;
        std::vector<int> indeg(t.size(), 0);
        for (size_t i = 0; i < t.size(); i++) if (t[i].used && t[i].next >= 0) { if (!t[t[i].next].used) return false; ++indeg[t[i].next]; }
        for (size_t i = 0; i < t.size(); i++) if (indeg[i] > 1) return false;       // 한 칸을 가리키는 next 는 많아야 하나
        for (size_t i = 0; i < t.size(); i++) if (t[i].used) {                       // 각 키는 자기 홈의 사슬에서 찾아진다, 사슬은 순환하지 않는다
            size_t c = h(t[i].key), steps = 0; bool reached = false;
            while (true) { if (c == i) { reached = true; break; } if (t[c].next < 0 || ++steps > t.size()) break; c = (size_t)t[c].next; }
            if (!reached) return false;
        }
        return true;
    }
};

int main() {
    Coalesced t(11, 9);                                           // 주소 영역 0..8, cellar 9..10
    int keys[] = {5, 14, 23, 32, 1, 10, 7};                       // 5, 14, 23, 32 는 모두 홈 버킷 5
    for (int k : keys) assert(t.insert(k));
    for (int k : keys) assert(t.find(k));
    assert(!t.find(41) && !t.find(2));
    assert(t.placeOf(5) == 5 && t.placeOf(14) == 10 && t.placeOf(23) == 9 && t.valid());   // 충돌한 첫 두 키는 cellar 의 뒤쪽부터 (10, 9)
    long late = t.placeOf(32); assert(late >= 0 && late < 9);                              // 세 번째 충돌부터는 주소 영역의 빈 칸 (cellar 가 찼다)
    // ② std::set 대조
    std::mt19937 rng(123); long fullFails = 0;
    for (int round = 0; round < 200; ++round) {
        size_t total = 5 + rng() % 60, addr = std::max<size_t>(1, total * (70 + rng() % 25) / 100); Coalesced c(total, addr); std::set<int> model;
        for (int step = 0; step < 150; ++step) {
            int k = (int)(rng() % 120); if (rng() % 3) { bool ok = c.insert(k); if (ok) model.insert(k); else { ++fullFails; assert(model.size() == total && !model.count(k)); } } else assert(c.find(k) == (model.count(k) > 0));
            assert(c.size() == model.size());
        }
        for (int k = 0; k < 120; k++) assert(c.find(k) == (model.count(k) > 0));
        assert(c.valid());
    }
    assert(fullFails > 100);
    // ③ 적재율 0.9 에서 평균 탐사 수: 병합 해싱(cellar 14 %) 대 선형 탐사
    const size_t total = 1000, nk = 900; double coalProbes = 0, linProbes = 0; const int trials = 60;
    for (int tr = 0; tr < trials; ++tr) {
        Coalesced c(total, total * 86 / 100); std::vector<int> lin(total, -1); std::set<int> keysSet; std::vector<int> keyList;
        while (keyList.size() < nk) { int k = (int)(rng() % 1000000); if (keysSet.insert(k).second) { keyList.push_back(k); c.insert(k); size_t j = (size_t)(unsigned)k * 2654435761u % total; while (lin[j] >= 0) j = (j + 1) % total; lin[j] = k; } }
        c.visited = 0; for (int k : keyList) assert(c.find(k)); coalProbes += (double)c.visited / nk;
        long steps = 0; for (int k : keyList) { size_t j = (size_t)(unsigned)k * 2654435761u % total; ++steps; while (lin[j] != k) { j = (j + 1) % total; ++steps; } } linProbes += (double)steps / nk;
    }
    coalProbes /= trials; linProbes /= trials;
    assert(coalProbes < linProbes && coalProbes < 2.0 && linProbes > 3.0);
    // ④ 전부 같은 홈
    Coalesced worst(40, 30); for (int i = 0; i < 40; i++) assert(worst.insert(i * 30)); for (int i = 0; i < 40; i++) assert(worst.find(i * 30)); assert(!worst.insert(7) && worst.valid());
    std::cout << "CoalescedHashing verified: at load 0.9 a successful search visits " << coalProbes << " slots on average vs " << linProbes << " for linear probing." << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 병합된 체인 길이에 비례
// Space Complexity: O(m)
```
# Part 4. 완전 해시
## PerfectHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// FKS 완전 해시: 고정된 키 집합에 대해 충돌 0, 탐색 최악 O(1).
// 1단계: 전역 해시로 n개 버킷에 나누고 sum(n_i^2) < 4n 이 될 때까지 재시도.
// 2단계: 버킷 i는 n_i^2 칸의 표를 만들고 충돌이 없을 때까지 해시 함수를 다시 뽑는다.
struct UH {
    static constexpr uint64_t P = 4294967311ULL;                 // 2^32 보다 큰 소수
    uint64_t a = 1, b = 0;
    size_t operator()(uint32_t k, size_t m) const { return ((a * k + b) % P) % m; }
};

class FKS {
    struct Bucket { UH h; std::vector<int64_t> slot; };
    UH top; std::vector<Bucket> bucket; size_t n;
public:
    explicit FKS(const std::vector<uint32_t>& keys) : n(keys.size()) {
        std::mt19937_64 rng(2024);
        auto draw = [&]() { UH u; u.a = rng() % (UH::P - 1) + 1; u.b = rng() % UH::P; return u; };
        std::vector<std::vector<uint32_t>> groups;
        for (;;) {
            top = draw();
            groups.assign(n, {});
            for (uint32_t k : keys) groups[top(k, n)].push_back(k);
            size_t sum = 0; for (auto& g : groups) sum += g.size() * g.size();
            if (sum < 4 * n) break;
        }
        bucket.resize(n);
        for (size_t i = 0; i < n; i++) {
            size_t sz = groups[i].size() * groups[i].size();
            if (sz == 0) continue;
            for (;;) {
                bucket[i].h = draw();
                bucket[i].slot.assign(sz, -1);
                bool ok = true;
                for (uint32_t k : groups[i]) {
                    size_t j = bucket[i].h(k, sz);
                    if (bucket[i].slot[j] >= 0) { ok = false; break; }
                    bucket[i].slot[j] = k;
                }
                if (ok) break;
            }
        }
    }
    bool contains(uint32_t k) const {
        const Bucket& bk = bucket[top(k, n)];
        return !bk.slot.empty() && bk.slot[bk.h(k, bk.slot.size())] == (int64_t)k;
    }
    size_t totalSlots() const { size_t s = 0; for (auto& b : bucket) s += b.slot.size(); return s; }
};

int main() {
    std::vector<uint32_t> keys;
    for (uint32_t i = 0; i < 200; i++) keys.push_back(i * 7919u + 17u);
    FKS f(keys);
    for (uint32_t k : keys) assert(f.contains(k));
    assert(!f.contains(3) && !f.contains(123456789));
    assert(f.totalSlots() < 4 * keys.size());                    // 공간은 O(n)
    std::cout << "PerfectHash: " << keys.size() << " keys, " << f.totalSlots() << " slots" << std::endl;
    return 0;
}
// Time Complexity: 탐색 O(1) 최악, 구성 기대 O(n)
// Space Complexity: O(n)
```
## MinimalPerfectHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

// 최소 완전 해시: n개 키를 [0, n) 에 빈틈없이 일대일로 대응시킨다 (hash-and-displace, CHD 방식).
// 키를 r개 버킷으로 나누고, 큰 버킷부터 "변위 d" 를 골라 버킷 안 키들이 모두 빈 칸에 떨어지게 한다.  키 집합이 *고정* 이고 서로 달라야 한다. 집합 밖의 문자열에는 아무 칸이나 돌려준다(멤버십 검사가 아니다)
// 검증: ① 손으로 짠 예  ② 크기 1~300 의 무작위 키 집합 300 개와 5 000 개 하나에서 이미지가 정확히 [0, n) (일대일·전사), 재구성이 결정적, 중복 키는 거부
//        ③ 변위 배열의 크기: 키당 비트 수를 계산해 작음을 확인 (CHD 의 장점)  ④ 집합 밖 문자열도 [0, n) 안의 값을 돌려준다(그래서 따로 키를 저장해 비교해야 멤버십을 안다)
uint32_t hseed(const std::string& s, uint32_t seed) {
    uint32_t h = 2166136261u ^ (seed * 2654435761u);
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16;
    return h;
}

struct MPH {
    size_t n, r;
    std::vector<uint32_t> disp;
    explicit MPH(const std::vector<std::string>& keys) : n(keys.size()), r(keys.size() / 4 + 1), disp(r, 0) {
        if (std::set<std::string>(keys.begin(), keys.end()).size() != keys.size()) throw std::invalid_argument("duplicate keys");      // 같은 키는 어떤 변위로도 갈라놓을 수 없다
        std::vector<std::vector<const std::string*>> buckets(r);
        for (auto& k : keys) buckets[hseed(k, 0) % r].push_back(&k);
        std::vector<size_t> order(r);
        for (size_t i = 0; i < r; i++) order[i] = i;
        std::stable_sort(order.begin(), order.end(), [&](size_t a, size_t b) { return buckets[a].size() > buckets[b].size(); });
        std::vector<bool> taken(n, false);
        for (size_t b : order) {
            if (buckets[b].empty()) continue;
            for (uint32_t d = 1;; d++) {
                std::vector<size_t> pos; bool ok = true;
                for (auto* k : buckets[b]) {
                    size_t p = hseed(*k, d) % n;
                    if (taken[p] || std::find(pos.begin(), pos.end(), p) != pos.end()) { ok = false; break; }
                    pos.push_back(p);
                }
                if (ok) { for (size_t p : pos) taken[p] = true; disp[b] = d; break; }
            }
        }
    }
    size_t operator()(const std::string& k) const { return hseed(k, disp[hseed(k, 0) % r]) % n; }
    double bitsPerKey() const { uint32_t mx = 0; for (uint32_t d : disp) mx = std::max(mx, d); int bits = 1; while ((1u << bits) <= mx) bits++; return (double)r * bits / (double)n; }
};

int main() {
    std::vector<std::string> keys;
    for (int i = 0; i < 100; i++) keys.push_back("word" + std::to_string(i * 37));
    MPH f(keys);
    std::set<size_t> image;
    for (auto& k : keys) image.insert(f(k));
    assert(image.size() == keys.size());                         // 충돌 없음
    assert(*image.begin() == 0 && *image.rbegin() == keys.size() - 1);   // 정확히 [0, n) 을 채움 (최소)
    // ② 무작위 키 집합
    std::mt19937 rng(3); long sets = 0, totalKeys = 0; double worstBits = 0;
    auto randomKeys = [&](size_t n) { std::set<std::string> s; while (s.size() < n) { std::string k; for (int j = 0, len = 1 + (int)(rng() % 14); j < len; j++) k += (char)('a' + rng() % 26); s.insert(k); } return std::vector<std::string>(s.begin(), s.end()); };
    for (int it = 0; it < 300; ++it) {
        size_t n = 1 + rng() % 300; auto ks = randomKeys(n); MPH g(ks);
        std::vector<bool> hit(n, false); for (auto& k : ks) { size_t p = g(k); assert(p < n && !hit[p]); hit[p] = true; }
        assert(std::count(hit.begin(), hit.end(), true) == (long)n);                      // 전사: [0, n) 의 모든 칸이 쓰인다
        MPH g2(ks); assert(g2.disp == g.disp);                                            // 결정적
        ++sets; totalKeys += (long)n; if (n >= 50) worstBits = std::max(worstBits, g.bitsPerKey());
    }
    { auto big = randomKeys(5000); MPH g(big); std::vector<bool> hit(5000, false); for (auto& k : big) { size_t p = g(k); assert(p < 5000 && !hit[p]); hit[p] = true; } assert(std::count(hit.begin(), hit.end(), true) == 5000); worstBits = std::max(worstBits, g.bitsPerKey()); }
    bool threw = false; try { MPH bad({"a", "b", "a"}); } catch (const std::invalid_argument&) { threw = true; } assert(threw);        // 중복 키는 거부
    MPH one({"only"}); assert(one("only") == 0 && one("other") == 0);                    // 경계: 키 하나는 칸 하나
    // ③ 작은 변위 배열 ④ 집합 밖
    assert(worstBits < 8.0);                                                              // 키당 8 비트 미만 (원본 문자열을 저장하지 않는다)
    MPH g(keys); for (int i = 0; i < 1000; i++) assert(g("not-a-key-" + std::to_string(i)) < keys.size());
    std::cout << "MinimalPerfectHash: " << keys.size() << " keys -> [0," << keys.size() << "); " << sets << " random sets (" << totalKeys << " keys) mapped bijectively; displacement table uses at most " << worstBits << " bits per key" << std::endl;
    return 0;
}
// Time Complexity: 탐색 O(len), 구성 기대 O(n)
// Space Complexity: O(n)  (키당 약 수 비트의 변위 배열)
```
# Part 5. 롤링 해시
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

// 다항 롤링 해시: 문자열 s 의 해시 H(s) = Σ s[i]·B^(n−1−i) mod p. 접두사 해시 P[i+1] = P[i]·B + s[i] 를 미리 만들면 임의의 부분 문자열의 해시를 O(1) 에 H(s[l..r)) = P[r] − P[l]·B^(r−l) (mod p) 로 구하고, 창을 한 칸 밀 때는 h ← (h − s[out]·B^(w−1))·B + s[in] 로 O(1) 에 갱신한다(라빈–카프 문자열 검색의 핵심). 이 책에서 롤링 해시의 정본은 이 항목이다(String.md 의 라빈–카프는 이것을 쓴다).
// 파라미터 선택이 전부다. p = 2^61 − 1 (메르센 소수; 곱은 128비트로 한 뒤 비트 연산으로 줄인다) 와 *실행 시 무작위로 고른* 밑 B 를 쓴다. 두 서로 다른 길이 ≤ L 문자열이 충돌하려면 B 가 차수 ≤ L − 1 인 다항식(두 해시의 차)의 근이어야 하므로 확률 ≤ (L − 1)/p — 아래에서 작은 소수로 *모든 밑을 시도해* 이 정리를 정확히 확인한다. 나쁜 선택: ① 2^64 로 자연 오버플로(mod 2^64) — Thue–Morse 문자열 쌍이 *어떤 밑에서도* 충돌(아래 시연), ② 고정 밑 + 작은 p(~10^9) — 생일 역설로 20 만 개 문자열 안에서 충돌이 나온다.
// 검증: ① 이진 알파벳 문자열 2000 개에서 모든 부분 문자열 쌍의 해시 동치 ⇔ 실제 동치 ② 롤링 갱신 = 재계산, 롤링으로 센 패턴 등장 횟수 = 순진한 검색 ③ 소수 p = 10007 에서 서로 다른 길이 8 문자열 쌍 500 개: 충돌하는 밑의 수 ≤ 7 (= L − 1) ④ Thue–Morse (길이 2^11, 2^12) 는 mod 2^64 해시가 *무작위 밑 50 개 모두* 에서 충돌하지만 mod 2^61 − 1 에서는 안 함 ⑤ mod ~10^9 는 무작위 12 글자 문자열 20 만 개에서 충돌이 나오고 mod 2^61 − 1 은 안 나옴 ⑥ 해시 이분 탐색으로 구한 가장 긴 반복 부분 문자열 길이 = 완전 탐색.
__extension__ typedef unsigned __int128 u128;
typedef std::uint64_t u64;
const u64 MOD61 = (1ULL << 61) - 1;
u64 mulmod61(u64 a, u64 b) { u128 t = (u128)a * b; u64 r = (u64)(t & MOD61) + (u64)(t >> 61); if (r >= MOD61) r -= MOD61; return r >= MOD61 ? r - MOD61 : r; }
struct Roll {
    u64 B; std::vector<u64> P, pw;
    Roll(const std::string& s, u64 base) : B(base), P(s.size() + 1, 0), pw(s.size() + 1, 1) {
        for (std::size_t i = 0; i < s.size(); ++i) { P[i + 1] = mulmod61(P[i], B) + (u64)(unsigned char)s[i]; if (P[i + 1] >= MOD61) P[i + 1] -= MOD61; pw[i + 1] = mulmod61(pw[i], B); }
    }
    u64 sub(std::size_t l, std::size_t r) const { u64 x = mulmod61(P[l], pw[r - l]); return P[r] >= x ? P[r] - x : P[r] + MOD61 - x; }
};
u64 roll(u64 h, unsigned char out, unsigned char in, u64 B, u64 powWm1) { u64 x = mulmod61(out, powWm1); h = h >= x ? h - x : h + MOD61 - x; h = mulmod61(h, B) + in; return h >= MOD61 ? h - MOD61 : h; }
u64 hashPlain(const std::string& s, u64 B, u64 mod) { u64 h = 0; for (unsigned char c : s) h = (u64)(((u128)h * B + c) % mod); return h; }

int main() {
    std::mt19937_64 rng(12);
    // ① 부분 문자열 해시 동치 ⇔ 실제 동치 (이진 알파벳이라 같은 부분 문자열이 많다)
    long equalPairs = 0;
    for (int it = 0; it < 2000; ++it) {
        std::size_t n = 1 + rng() % 40; std::string s(n, 'a'); for (char& c : s) c = "ab"[rng() % 2]; Roll r(s, 256 + rng() % (MOD61 - 256));
        for (int q = 0; q < 40; ++q) { std::size_t len = 1 + rng() % n, l1 = rng() % (n - len + 1), l2 = rng() % (n - len + 1); bool same = s.compare(l1, len, s, l2, len) == 0; assert((r.sub(l1, l1 + len) == r.sub(l2, l2 + len)) == same); equalPairs += same; }
    }
    assert(equalPairs > 5000);
    // ② 롤링 갱신 = 재계산, 패턴 등장 횟수 = 순진한 검색
    for (int it = 0; it < 500; ++it) {
        std::size_t n = 10 + rng() % 200, w = 1 + rng() % 6; std::string s(n, 'a'); for (char& c : s) c = "abc"[rng() % 3]; std::string pat(w, 'a'); for (char& c : pat) c = "abc"[rng() % 3]; u64 B = 300 + rng() % 1000000;
        std::vector<u64> pw(w, 1); for (std::size_t i = 1; i < w; ++i) pw[i] = mulmod61(pw[i - 1], B); u64 hp = 0; for (unsigned char c : pat) { hp = mulmod61(hp, B) + c; if (hp >= MOD61) hp -= MOD61; }
        u64 h = 0; for (std::size_t i = 0; i < w; ++i) { h = mulmod61(h, B) + (unsigned char)s[i]; if (h >= MOD61) h -= MOD61; } long found = 0, naive = 0;
        for (std::size_t i = 0; i + w <= n; ++i) { if (i) h = roll(h, (unsigned char)s[i - 1], (unsigned char)s[i + w - 1], B, pw[w - 1]); assert(h == Roll(s.substr(i, w), B).sub(0, w)); found += h == hp && s.compare(i, w, pat) == 0; naive += s.compare(i, w, pat) == 0; }
        assert(found == naive);
    }
    // ③ 정리: 서로 다른 길이 L 문자열이 충돌하는 밑은 L − 1 개 이하 (p = 10007 의 모든 밑을 시도)
    {   const u64 p = 10007; int worst = 0;
        for (int it = 0; it < 500; ++it) { std::string a(8, 'a'), b(8, 'a'); for (char& c : a) c = (char)('a' + rng() % 26); b = a; b[rng() % 8] = (char)('a' + rng() % 26); if (a == b) continue; int roots = 0; for (u64 B = 0; B < p; ++B) roots += hashPlain(a, B, p) == hashPlain(b, B, p); worst = std::max(worst, roots); assert(roots <= 7); }
        assert(worst >= 1); }
    // ④ Thue–Morse: mod 2^64 (자연 오버플로) 는 어떤 홀수 밑에서도 충돌 (짝수 밑은 B^64 = 0 이라 마지막 64 글자만 본다), mod 2^61 − 1 은 충돌 안 함
    for (int k : {11, 12}) {
        std::string a(1u << k, 'a'), b(1u << k, 'b'); for (std::size_t i = 0; i < a.size(); ++i) { bool bit = __builtin_popcountll(i) & 1; a[i] = bit ? 'b' : 'a'; b[i] = bit ? 'a' : 'b'; }
        int collide64 = 0, collide61 = 0;
        for (int t = 0; t < 50; ++t) { u64 B = rng() | 1; u64 ha = 0, hb = 0; for (unsigned char c : a) ha = ha * B + c; for (unsigned char c : b) hb = hb * B + c; collide64 += ha == hb; collide61 += Roll(a, 256 + rng() % (MOD61 - 256)).sub(0, a.size()) == Roll(b, 256 + rng() % (MOD61 - 256)).sub(0, b.size()); }
        assert(a != b && collide64 == 50 && collide61 == 0);
    }
    // ⑤ 작은 모듈러스는 생일 역설로 깨진다: 무작위 12 글자 문자열 20 만 개 (p = 10^9+7, 고정 밑 31)
    {   std::unordered_set<u64> seen32, seen61; std::set<std::string> distinct; long coll32 = 0, coll61 = 0; Roll dummy("a", 12345);
        for (int i = 0; i < 200000; ++i) { std::string s(12, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); if (!distinct.insert(s).second) continue; if (!seen32.insert(hashPlain(s, 31, 1000000007ULL)).second) ++coll32; if (!seen61.insert(Roll(s, 987654321987ULL).sub(0, 12)).second) ++coll61; }
        assert(coll32 >= 5 && coll61 == 0); std::cout << "PolynomialRollingHash: distinct 12-letter strings colliding under p = 10^9+7: " << coll32 << ", under 2^61-1: " << coll61 << std::endl; }
    // ⑥ 가장 긴 반복 부분 문자열: 길이 L 이 가능한지 해시 집합으로 판정 (단조) + 이분 탐색 vs 완전 탐색
    for (int it = 0; it < 300; ++it) {
        std::size_t n = 2 + rng() % 40; std::string s(n, 'a'); for (char& c : s) c = "ab"[rng() % 2]; Roll r(s, 1000 + rng() % 100000);
        auto has = [&](std::size_t L) { std::unordered_set<u64> seen; for (std::size_t i = 0; i + L <= n; ++i) if (!seen.insert(r.sub(i, i + L)).second) return true; return false; };
        std::size_t lo = 0, hi = n - 1; while (lo < hi) { std::size_t mid = (lo + hi + 1) / 2; if (has(mid)) lo = mid; else hi = mid - 1; }
        std::size_t brute = 0; for (std::size_t L = 1; L < n; ++L) { std::set<std::string> seen; bool dup = false; for (std::size_t i = 0; i + L <= n && !dup; ++i) dup = !seen.insert(s.substr(i, L)).second; if (dup) brute = L; }
        assert(lo == brute);
    }
    // 큰 입력: 길이 100 만 문자열에서 무작위 부분 문자열 쌍 2000 개
    {   std::string s(1000000, 'a'); for (char& c : s) c = "ab"[rng() % 2]; Roll r(s, 1234567891011ULL);
        for (int q = 0; q < 2000; ++q) { std::size_t len = 1 + rng() % 40; std::size_t l1 = rng() % (s.size() - len), l2 = rng() % (s.size() - len); if (q % 2) l2 = (l1 + len * 3) % (s.size() - len); assert((r.sub(l1, l1 + len) == r.sub(l2, l2 + len)) == (s.compare(l1, len, s, l2, len) == 0)); } }
    std::cout << "PolynomialRollingHash: substring hashes (mod 2^61-1, random base) were equal exactly when the substrings were on " << equalPairs << " equal pairs, rolling updates equalled recomputation and pattern counts equalled naive search, the number of bases colliding for two distinct length-8 strings never exceeded L-1 = 7 over all bases of a 10007 modulus, Thue-Morse strings of length 2048 and 4096 collided for all 50 random bases modulo 2^64 but never modulo 2^61-1, and hash-based binary search found the longest repeated substring of 300 random binary strings" << std::endl; return 0;
}
// Time Complexity: 전처리 O(n), 부분 문자열 해시 O(1)
// Space Complexity: O(n)
```
## RabinFingerprint()
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

// 라빈 지문: GF(2)[x] 위의 다항식을 기약다항식 P(x) = x^32 + x^22 + x^2 + x + 1 로 나눈 나머지.
// 윈도우를 한 바이트 밀 때 가장 오래된 바이트의 기여를 XOR 로 지우고 x^8 을 곱한 뒤 새 바이트를 더한다.
// 지문은 GF(2) 위에서 *선형* (fp(a⊕b) = fp(a)⊕fp(b)) 이고, 고정된 P 에서는 P 의 배수가 모두 지문 0 이라 의도적인 충돌을 만들 수 있다 — 그래서 원래는 P 를 무작위로 고른다
// 응용: 라빈-카프 문자열 검색, 내용 기반 청크 분할(지문의 하위 비트가 0 이면 경계 — 앞쪽에 바이트를 끼워 넣어도 뒤쪽 경계가 그대로여서 중복 제거·rsync 가 가능)
// 검증: ① P 가 정말 기약인가: Rabin 검사(x^(2^32) ≡ x, gcd(x^(2^16) - x, P) = 1)  ② 슬라이딩 값 = 정의대로의 합 Σ 바이트_i · x^(8(w-1-i)) mod P (캐리 없는 곱셈과 거듭제곱으로 따로 계산), 길이 1~500 문자열 × 윈도우 1~64
//        ③ 선형성과 P 자체(5 바이트)의 지문 0 → 서로 다른 두 문자열이 충돌  ④ 라빈-카프 검색이 나이브 검색과 같은 위치를 내고 거짓 양성이 드물다  ⑤ 내용 기반 청크 경계가 앞쪽 삽입에 불변이고 평균 청크 길이 ≈ 2^k
const uint32_t POLY = 0x00400007u;                                  // P(x) 의 낮은 32비트 (최고차항 x^32 는 암묵적)

uint32_t mulx8(uint32_t f) {                                        // f * x^8 mod P
    for (int i = 0; i < 8; i++) f = (f & 0x80000000u) ? (f << 1) ^ POLY : (f << 1);
    return f;
}

struct Window {
    size_t w; uint32_t f = 0; uint32_t out[256];
    explicit Window(size_t width) : w(width) {
        for (int b = 0; b < 256; b++) {                              // out[b] = b * x^(8(w-1)) mod P
            uint32_t v = b; for (size_t i = 0; i + 1 < w; i++) v = mulx8(v);
            out[b] = v;
        }
    }
    void push(uint8_t in) { f = mulx8(f) ^ in; }                     // 윈도우를 채우는 단계
    void slide(uint8_t old, uint8_t in) { f = mulx8(f ^ out[old]) ^ in; }
};

uint32_t direct(const std::string& s, size_t pos, size_t w) {      // 매번 처음부터 계산한 기준값
    uint32_t f = 0; for (size_t i = 0; i < w; i++) f = mulx8(f) ^ (uint8_t)s[pos + i]; return f;
}
// ---- 독립 참조: 캐리 없는 곱셈 ----
const uint64_t PFULL = (1ULL << 32) | POLY;                          // P(x) 전체 (33 비트)
int degree(uint64_t a) { int d = -1; while (a) { ++d; a >>= 1; } return d; }
uint64_t polyMod(uint64_t a, uint64_t p) { int dp = degree(p); while (degree(a) >= dp) a ^= p << (degree(a) - dp); return a; }
uint64_t mulMod(uint64_t a, uint64_t b) { uint64_t r = 0; a = polyMod(a, PFULL); for (; b; b >>= 1) { if (b & 1) r ^= a; a <<= 1; if (degree(a) >= 32) a ^= PFULL; } return r; }
uint64_t powX(uint64_t e) { uint64_t r = 1, base = 2; for (; e; e >>= 1) { if (e & 1) r = mulMod(r, base); base = mulMod(base, base); } return r; }      // x^e mod P
uint64_t polyGcd(uint64_t a, uint64_t b) { while (b) { uint64_t r = polyMod(a, b); a = b; b = r; } return a; }
uint32_t reference(const std::string& s, size_t pos, size_t w) {    // Σ 바이트_i(x) · x^(8(w-1-i)) mod P
    uint64_t r = 0; for (size_t i = 0; i < w; i++) r ^= mulMod((uint8_t)s[pos + i], powX(8 * (w - 1 - i))); return (uint32_t)r;
}
std::vector<size_t> chunkEnds(const std::string& d, size_t w, uint32_t mask) {       // 윈도우(마지막 w 바이트)의 지문이 mask 와 겹치는 비트가 모두 0 이면 그 윈도우의 끝이 경계
    std::vector<size_t> ends; if (d.size() < w) return ends;
    Window win(w); for (size_t i = 0; i < w; i++) win.push((uint8_t)d[i]);
    if ((win.f & mask) == 0) ends.push_back(w - 1);
    for (size_t i = w; i < d.size(); i++) { win.slide((uint8_t)d[i - w], (uint8_t)d[i]); if ((win.f & mask) == 0) ends.push_back(i); }
    return ends;
}

int main() {
    std::string s = "the quick brown fox jumps over the lazy dog";
    const size_t w = 5;
    Window win(w);
    for (size_t i = 0; i < w; i++) win.push((uint8_t)s[i]);
    assert(win.f == direct(s, 0, w));
    for (size_t i = w; i < s.size(); i++) {
        win.slide((uint8_t)s[i - w], (uint8_t)s[i]);
        assert(win.f == direct(s, i - w + 1, w));                    // 밀어서 구한 값 == 처음부터 구한 값
    }
    // ① P 가 기약인가
    { uint64_t v = 2; for (int i = 0; i < 32; i++) v = mulMod(v, v); assert(v == 2); }                       // x^(2^32) ≡ x (mod P)
    { uint64_t v = 2; for (int i = 0; i < 16; i++) v = mulMod(v, v); assert(v != 2 && polyGcd(PFULL, v ^ 2) == 1); }   // 16 = 32/2 : gcd(x^(2^16) - x, P) = 1  => 기약
    // ② 정의 그대로의 합과 일치
    std::mt19937 rng(9); long windows = 0;
    for (int it = 0; it < 60; ++it) {
        std::string t(1 + rng() % 500, 'x'); for (char& c : t) c = (char)rng(); size_t ww = 1 + rng() % std::min<size_t>(64, t.size());
        Window wn(ww); for (size_t i = 0; i < ww; i++) wn.push((uint8_t)t[i]);
        assert(wn.f == direct(t, 0, ww) && wn.f == reference(t, 0, ww)); ++windows;
        for (size_t i = ww; i < t.size(); i++) { wn.slide((uint8_t)t[i - ww], (uint8_t)t[i]); if ((i & 7) == 0 || i + 1 == t.size()) assert(wn.f == reference(t, i - ww + 1, ww)); assert(wn.f == direct(t, i - ww + 1, ww)); ++windows; }
    }
    // ③ 선형성과 P 의 배수
    for (int it = 0; it < 2000; ++it) {
        size_t len = 1 + rng() % 40; std::string a(len, 'x'), b(len, 'x'), c(len, 'x'); for (size_t i = 0; i < len; i++) { a[i] = (char)rng(); b[i] = (char)rng(); c[i] = (char)(a[i] ^ b[i]); }
        assert(direct(c, 0, len) == (direct(a, 0, len) ^ direct(b, 0, len)));
    }
    std::string multiple("\x01\x00\x40\x00\x07", 5), zeros(5, '\0');                       // P(x) 자신 = x^32 + x^22 + x^2 + x + 1 (비트 32, 22, 2, 1, 0)
    assert(multiple != zeros && direct(multiple, 0, 5) == 0 && direct(zeros, 0, 5) == 0);   // 서로 다른 문자열이 같은 지문 0
    std::string longMultiple = multiple + std::string("\x00\x00\x00", 3);                   // P(x)·x^24 도 P 의 배수 (8 바이트)
    assert(direct(longMultiple, 0, 8) == 0);
    // ④ 라빈-카프 검색
    long found = 0, falsePositives = 0, checks = 0;
    for (int it = 0; it < 400; ++it) {
        int sigma = 2 + (int)(rng() % 3); std::string text(rng() % 400, 'a'); for (char& c : text) c = (char)('a' + rng() % sigma);
        size_t m = 1 + rng() % 12; std::string pat(m, 'a'); for (char& c : pat) c = (char)('a' + rng() % sigma);
        std::vector<size_t> want; for (size_t i = 0; i + m <= text.size(); i++) if (text.compare(i, m, pat) == 0) want.push_back(i);
        std::vector<size_t> got; uint32_t pf = direct(pat, 0, m);
        if (text.size() >= m) {
            Window wn(m); for (size_t i = 0; i < m; i++) wn.push((uint8_t)text[i]);
            for (size_t i = 0;; i++) { ++checks; if (wn.f == pf) { if (text.compare(i, m, pat) == 0) got.push_back(i); else ++falsePositives; } if (i + m >= text.size()) break; wn.slide((uint8_t)text[i], (uint8_t)text[i + m]); }
        }
        assert(got == want); found += (long)got.size();
    }
    assert(found > 500 && falsePositives == 0);
    // ⑤ 내용 기반 청크 분할
    std::string data(20000, 'x'); for (char& c : data) c = (char)rng();
    const size_t cw = 16; const uint32_t mask = 63;                                          // 하위 6 비트 = 0 -> 평균 64 바이트
    std::vector<size_t> ends = chunkEnds(data, cw, mask);
    double avg = (double)data.size() / (double)ends.size(); assert(avg > 40 && avg < 100);
    std::string edited = data.substr(0, 100) + "INSERTED" + data.substr(100);               // 앞쪽(100 바이트 지점)에 8 바이트를 끼워 넣는다
    std::vector<size_t> ends2 = chunkEnds(edited, cw, mask);
    std::set<size_t> a, b; for (size_t e : ends) if (e >= 100 + cw) a.insert(e + 8); for (size_t e : ends2) if (e >= 100 + 8 + cw) b.insert(e);
    assert(a == b && a.size() > 200);                                                        // 삽입 지점에서 윈도우 하나 이상 떨어진 경계는 모두 그대로 (8 바이트 밀려난 자리)
    std::cout << "RabinFingerprint sliding window verified (" << windows << " windows vs the definition); content-defined chunks average " << avg << " bytes and " << a.size() << " boundaries survived an insertion" << std::endl;
    return 0;
}
// Time Complexity: 슬라이드 1회 O(1)
// Space Complexity: O(256)
```
## LongestCommonSubstringHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

// 두 문자열의 최장 공통 부분 문자열: 길이 L 에 대해 "공통 부분 문자열이 있는가" 는 단조 -> 이분 탐색 + 롤링 해시
// 주의: 해시가 같다고 같은 문자열은 아니다.  한 해시값에 여러 위치가 있을 수 있으므로 *모든* 후보 위치를 실제로 비교해야 한다 (마지막 위치만 기억하면 충돌 때 진짜 일치를 놓친다)
// 검증: ① 손으로 고른 예와 경계(빈 문자열, 전체 일치, 반복)  ② 무작위 문자열 쌍 3 000 개(알파벳 2~4, 길이 ≤ 40)를 O(nm) DP 오라클과 대조 (길이 일치, 반환 문자열은 두 문자열의 실제 부분 문자열)
//        ③ 모듈러를 일부러 7·101 로 줄여 충돌을 폭발시켜도 결과가 같고, "마지막 위치만 기억" 하는 순진한 판은 같은 조건에서 틀리는 경우가 실제로 있다  ④ 단조성: 길이 L 의 공통 부분 문자열 존재 여부가 L ≤ LCS 에서만 참이고 이분 탐색 횟수는 ⌈log2⌉ 수준
//        ⑤ 긴 입력(각 3 000 자, 200 자 공통 구간을 심음)
__extension__ typedef unsigned __int128 u128;
const uint64_t MOD61 = (1ULL << 61) - 1;
uint64_t mulmod(uint64_t a, uint64_t b, uint64_t mod) { return (uint64_t)((u128)a * b % mod); }

struct Rolling {
    std::vector<uint64_t> pre, pw; uint64_t mod;
    Rolling(const std::string& s, uint64_t B, uint64_t m) : pre(s.size() + 1, 0), pw(s.size() + 1, 1), mod(m) {
        for (size_t i = 0; i < s.size(); i++) {
            pre[i + 1] = (mulmod(pre[i], B, mod) + (unsigned char)s[i]) % mod;
            pw[i + 1] = mulmod(pw[i], B, mod);
        }
    }
    uint64_t get(size_t l, size_t r) const { return (pre[r] + mod - mulmod(pre[l], pw[r - l], mod)) % mod; }
};
struct Stats { long checks = 0, falseMatches = 0; };

std::string lcs(const std::string& a, const std::string& b, uint64_t mod = MOD61, uint64_t B = 911382323ULL, Stats* st = nullptr, bool allPositions = true) {
    Rolling ra(a, B % mod, mod), rb(b, B % mod, mod);
    auto check = [&](size_t L, size_t& posA) {
        if (st) st->checks++;
        std::unordered_map<uint64_t, std::vector<size_t>> seen;
        for (size_t i = 0; i + L <= a.size(); i++) { auto& v = seen[ra.get(i, i + L)]; if (!allPositions) v.clear(); v.push_back(i); }     // allPositions == false: 마지막 위치만 기억하는 순진한 판
        for (size_t j = 0; j + L <= b.size(); j++) {
            auto it = seen.find(rb.get(j, j + L));
            if (it == seen.end()) continue;
            for (size_t i : it->second) {
                if (a.compare(i, L, b, j, L) == 0) { posA = i; return true; }                // 충돌 방지용 실제 비교
                if (st) st->falseMatches++;
            }
        }
        return false;
    };
    size_t lo = 0, hi = std::min(a.size(), b.size()), best = 0, bestPos = 0;
    while (lo <= hi) {
        size_t mid = (lo + hi) / 2, p = 0;
        if (mid == 0 || check(mid, p)) { best = mid; bestPos = p; lo = mid + 1; }
        else { if (mid == 0) break; hi = mid - 1; }
    }
    return a.substr(bestPos, best);
}
size_t dpLength(const std::string& a, const std::string& b) {                      // O(nm) DP 오라클
    std::vector<size_t> prev(b.size() + 1, 0), cur(b.size() + 1, 0); size_t best = 0;
    for (size_t i = 0; i < a.size(); i++) { for (size_t j = 0; j < b.size(); j++) { cur[j + 1] = a[i] == b[j] ? prev[j] + 1 : 0; best = std::max(best, cur[j + 1]); } std::swap(prev, cur); }
    return best;
}
bool commonOfLength(const std::string& a, const std::string& b, size_t L) {        // 오라클: 길이 L 인 공통 부분 문자열이 있는가 (전수 비교)
    if (L == 0) return true; for (size_t i = 0; i + L <= a.size(); i++) if (b.find(a.substr(i, L)) != std::string::npos) return true; return false;
}

int main() {
    assert(lcs("abcdxyz", "xyzabcd") == "abcd");
    assert(lcs("zxabcdezy", "yzabcdezx") == "abcdez");
    assert(lcs("abc", "xyz").empty());
    assert(lcs("", "abc").empty() && lcs("abc", "").empty() && lcs("", "").empty() && lcs("hello", "hello") == "hello" && lcs("aaaa", "aaaaaa") == "aaaa" && lcs("a", "a") == "a");
    // ② DP 대조
    std::mt19937 rng(2024); long cases = 0, nonEmpty = 0;
    for (int it = 0; it < 3000; ++it) {
        int sigma = 2 + (int)(rng() % 3); std::string a(rng() % 41, 'a'), b(rng() % 41, 'a');
        for (char& c : a) c = (char)('a' + rng() % sigma); for (char& c : b) c = (char)('a' + rng() % sigma);
        std::string got = lcs(a, b); assert(got.size() == dpLength(a, b) && a.find(got) != std::string::npos && b.find(got) != std::string::npos);
        ++cases; nonEmpty += !got.empty();
    }
    // ③ 충돌을 일부러 폭발시킨다
    long falseMatches = 0, naiveWrong = 0, tinyCases = 0;
    for (int it = 0; it < 1500; ++it) {
        std::string a(1 + rng() % 30, 'a'), b(1 + rng() % 30, 'a'); for (char& c : a) c = (char)('a' + rng() % 3); for (char& c : b) c = (char)('a' + rng() % 3);
        for (uint64_t mod : {7ULL, 101ULL}) {
            Stats st; std::string good = lcs(a, b, mod, 5, &st), bad = lcs(a, b, mod, 5, nullptr, false);
            assert(good.size() == dpLength(a, b) && a.find(good) != std::string::npos && b.find(good) != std::string::npos);        // 충돌이 많아도 정답
            assert(bad.size() <= good.size() && (bad.empty() || (a.find(bad) != std::string::npos && b.find(bad) != std::string::npos)));   // 순진한 판은 틀린 문자열을 내지는 않지만 놓칠 수 있다
            falseMatches += st.falseMatches; naiveWrong += bad.size() < good.size(); ++tinyCases;
        }
    }
    assert(falseMatches > 10000 && naiveWrong > 20 && tinyCases == 3000);
    // ④ 단조성과 이분 탐색 횟수
    for (int it = 0; it < 200; ++it) {
        std::string a(1 + rng() % 25, 'a'), b(1 + rng() % 25, 'a'); for (char& c : a) c = (char)('a' + rng() % 3); for (char& c : b) c = (char)('a' + rng() % 3);
        size_t L = dpLength(a, b); for (size_t len = 0; len <= std::min(a.size(), b.size()) + 1; len++) assert(commonOfLength(a, b, len) == (len <= L));
        Stats st; lcs(a, b, MOD61, 911382323ULL, &st); size_t bound = 1; for (size_t x = std::min(a.size(), b.size()) + 1; x > 1; x = (x + 1) / 2) bound++; assert((size_t)st.checks <= bound + 1);
    }
    // ⑤ 긴 입력
    for (int it = 0; it < 4; ++it) {
        std::string a(3000, 'a'), b(3000, 'a'); for (char& c : a) c = (char)('a' + rng() % 4); for (char& c : b) c = (char)('a' + rng() % 4);
        b.replace(1500, 200, a.substr(700, 200)); std::string got = lcs(a, b); assert(got.size() == dpLength(a, b) && got.size() >= 200);
    }
    std::cout << "LongestCommonSubstringHash: " << lcs("abcdxyz", "xyzabcd") << " (" << cases << " random pairs matched the DP; with modulus 7 / 101 there were " << falseMatches << " hash collisions and the naive last-position variant missed the answer " << naiveWrong << " times)" << std::endl;
    return 0;
}
// Time Complexity: O((n + m) log min(n, m))
// Space Complexity: O(n + m)
```
# Part 6. 해시 컨테이너
## HashMap()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// 체이닝 해시맵: operator[], find, erase, 적재율 1.0 초과 시 2배 확장.  노드를 하나씩 따로 할당(std::unordered_map 과 같은 방식)하므로 확장해도 *값의 주소가 바뀌지 않는다*
// → m[a] = m[b] 처럼 참조를 쥔 채 다른 키를 삽입해도 안전하다 (벡터에 값을 직접 담으면 확장 때 주소가 바뀌어 댕글링 참조가 된다).  확장은 노드를 새 버킷 배열에 다시 연결할 뿐 값을 옮기지 않는다
// 검증: ① 손으로 짠 예  ② std::unordered_map 과 정수·문자열·쌍 키로 각각 60 000 번 대조(삽입·갱신·삭제·조회)하고 적재율 ≤ 1  ③ 모든 키가 같은 해시(최악)여도 정답이고 사슬 길이 = 키 수
//        ④ 참조 안정성: 1 000 개의 값 주소를 쥔 채 10 만 개를 더 넣어도 그대로  ⑤ 이동만 되는 값(unique_ptr)·소멸자의 해제  ⑥ 분할상환: 확장에서 다시 연결한 노드 수 ≤ 2n, reserve 후에는 확장이 없음  ⑦ m[a] = m[b] (확장이 일어나는 순간)
template <class K, class V, class Hash = std::hash<K>>
class HashMap {
    struct Node { K key; V val; Node* next; explicit Node(const K& k) : key(k), val(), next(nullptr) {} };
    std::vector<Node*> b; size_t n = 0, relinked_ = 0, grows_ = 0;
    size_t idx(const K& k, size_t m) const { return Hash{}(k) % m; }
    void grow(size_t newSize) {
        std::vector<Node*> nb(newSize, nullptr);
        for (Node* head : b) for (Node* p = head; p;) { Node* nx = p->next; size_t i = idx(p->key, newSize); p->next = nb[i]; nb[i] = p; p = nx; ++relinked_; }
        b.swap(nb); ++grows_;
    }
public:
    HashMap() : b(8, nullptr) {}
    HashMap(const HashMap&) = delete; HashMap& operator=(const HashMap&) = delete;
    ~HashMap() { clear(); }
    V& operator[](const K& k) {
        for (Node* p = b[idx(k, b.size())]; p; p = p->next) if (p->key == k) return p->val;
        if (n + 1 > b.size()) grow(b.size() * 2);
        Node* nd = new Node(k); size_t i = idx(k, b.size()); nd->next = b[i]; b[i] = nd; ++n;
        return nd->val;
    }
    V* find(const K& k) {
        for (Node* p = b[idx(k, b.size())]; p; p = p->next) if (p->key == k) return &p->val;
        return nullptr;
    }
    bool erase(const K& k) {
        Node** pp = &b[idx(k, b.size())];
        while (*pp) { if ((*pp)->key == k) { Node* d = *pp; *pp = d->next; delete d; --n; return true; } pp = &(*pp)->next; }
        return false;
    }
    void clear() { for (Node*& h : b) while (h) { Node* nx = h->next; delete h; h = nx; } n = 0; }
    void reserve(size_t count) { size_t m = b.size(); while (m < count) m *= 2; if (m != b.size()) grow(m); }
    template <class F> void forEach(F f) const { for (Node* h : b) for (Node* p = h; p; p = p->next) f(p->key, p->val); }
    size_t size() const { return n; }
    size_t buckets() const { return b.size(); }
    double loadFactor() const { return double(n) / b.size(); }
    size_t maxChain() const { size_t m = 0; for (Node* h : b) { size_t c = 0; for (Node* p = h; p; p = p->next) ++c; m = std::max(m, c); } return m; }
    size_t relinked() const { return relinked_; }
    size_t grows() const { return grows_; }
};
struct PairHash { size_t operator()(const std::pair<int, int>& p) const { return std::hash<long long>()((long long)p.first * 1000003LL + p.second); } };
struct ConstHash { size_t operator()(int) const { return 7; } };

int main() {
    HashMap<std::string, int> m;
    for (int i = 0; i < 1000; i++) m["k" + std::to_string(i)] = i;
    m["k5"] += 100;
    assert(m.size() == 1000 && *m.find("k5") == 105);
    assert(m.erase("k7") && m.find("k7") == nullptr && m.size() == 999);
    assert(m.loadFactor() <= 1.0 && !m.erase("nope") && m.find("nope") == nullptr);
    // ② std::unordered_map 대조
    std::mt19937 rng(8);
    {   HashMap<int, int> h; std::unordered_map<int, int> ref; long peak = 0;
        for (int step = 0; step < 60000; ++step) {
            int k = (int)(rng() % (step < 30000 ? 20000 : 500)) - 100; int op = (int)(rng() % 10);
            if (op < 5) { h[k] = step; ref[k] = step; } else if (op < 6) { h[k] += 1; ref[k] += 1; } else if (op < 8) assert(h.erase(k) == (ref.erase(k) > 0));
            else { int* p = h.find(k); auto it = ref.find(k); assert((p != nullptr) == (it != ref.end()) && (!p || *p == it->second)); }
            assert(h.size() == ref.size() && h.loadFactor() <= 1.0); peak = std::max<long>(peak, (long)h.size());
            if (step % 5000 == 0) { std::map<int, int> a, c; h.forEach([&](int key, int v) { a[key] = v; }); for (auto& kv : ref) c[kv.first] = kv.second; assert(a == c); }
        }
        assert(peak > 5000);
    }
    {   HashMap<std::string, int> h; std::map<std::string, int> ref;
        for (int step = 0; step < 60000; ++step) { std::string k = "w" + std::to_string(rng() % 3000); int op = (int)(rng() % 10); if (op < 6) { h[k] = step; ref[k] = step; } else if (op < 8) assert(h.erase(k) == (ref.erase(k) > 0)); else { int* p = h.find(k); auto it = ref.find(k); assert((p != nullptr) == (it != ref.end()) && (!p || *p == it->second)); } assert(h.size() == ref.size()); }
        std::map<std::string, int> a; h.forEach([&](const std::string& key, int v) { a[key] = v; }); assert(a == ref);
    }
    {   HashMap<std::pair<int, int>, int, PairHash> h; std::map<std::pair<int, int>, int> ref;
        for (int step = 0; step < 60000; ++step) { std::pair<int, int> k{(int)(rng() % 60), (int)(rng() % 60)}; int op = (int)(rng() % 10); if (op < 6) { h[k] = step; ref[k] = step; } else if (op < 8) assert(h.erase(k) == (ref.erase(k) > 0)); else { int* p = h.find(k); auto it = ref.find(k); assert((p != nullptr) == (it != ref.end()) && (!p || *p == it->second)); } assert(h.size() == ref.size()); }
    }
    // ③ 모든 키가 같은 해시
    {   HashMap<int, int, ConstHash> h; for (int i = 0; i < 300; i++) h[i] = i * 2; for (int i = 0; i < 300; i++) assert(*h.find(i) == i * 2); assert(h.maxChain() == 300 && h.size() == 300); for (int i = 0; i < 300; i += 2) assert(h.erase(i)); assert(h.size() == 150 && h.find(4) == nullptr && *h.find(5) == 10); }
    // ④ 참조 안정성
    {   HashMap<int, int> h; std::vector<int*> ptrs; for (int i = 0; i < 1000; i++) { h[i] = i + 5; ptrs.push_back(h.find(i)); }
        size_t growsBefore = h.grows(); for (int i = 1000; i < 101000; i++) h[i] = i; assert(h.grows() > growsBefore + 5);
        for (int i = 0; i < 1000; i++) { assert(h.find(i) == ptrs[i] && *ptrs[i] == i + 5); } }
    // ⑤ 이동만 되는 값
    {   HashMap<int, std::unique_ptr<int>> h; for (int i = 0; i < 2000; i++) h[i].reset(new int(i)); for (int i = 0; i < 2000; i += 2) assert(h.erase(i)); for (int i = 1; i < 2000; i += 2) assert(**h.find(i) == i); h.clear(); assert(h.size() == 0); h[5].reset(new int(55)); assert(**h.find(5) == 55); }          // 남은 것은 소멸자가 해제
    // ⑥ 분할상환
    {   HashMap<int, int> h; for (int i = 0; i < 50000; i++) h[i] = i; assert(h.relinked() <= 2 * h.size() && h.grows() >= 12 && h.loadFactor() <= 1.0 && h.maxChain() < 15);
        HashMap<int, int> r; r.reserve(10000); size_t g = r.grows(); for (int i = 0; i < 10000; i++) r[i] = i; assert(r.grows() == g && r.buckets() >= 10000); }
    // ⑦ m[a] = m[b] 를 확장이 일어나는 바로 그 삽입에서 (벡터에 값을 직접 담은 구현이면 댕글링 참조)
    {   HashMap<int, std::string> h; for (int i = 0; i < 8; i++) h[i] = "v" + std::to_string(i); assert(h.size() == h.buckets()); h[100] = h[3]; assert(h[100] == "v3" && h.buckets() == 16); }
    std::cout << "HashMap size=" << m.size() << " load=" << m.loadFactor() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 확장은 분할상환
// Space Complexity: O(n)
```
## LinkedHashMap()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

// LinkedHashMap: 해시맵 + 이중 연결 리스트. 순회 순서가 삽입 순서(또는 접근 순서)로 고정된다.  해시 사슬과 순서 리스트를 *같은 노드* 가 가진다 (Java 의 LinkedHashMap 과 같은 구조).
// 접근 순서 + 용량 제한 = LRU 캐시 (용량을 넘으면 가장 오래 쓰이지 않은 항목 = 리스트 맨 앞을 쫓아낸다).  삽입 순서 모드에서는 값 갱신이 순서를 바꾸지 않고, 접근 순서 모드에서는 get/put 이 맨 뒤로 보낸다
// 검증: ① 손으로 짠 예  ② 단순 모델(벡터에 (키, 값) 을 순서대로 담고 선형 탐색)과 50 000 번씩 대조 — 삽입 순서 / 접근 순서 / 접근 순서 + 용량 8 (LRU, 쫓겨난 키의 기록까지)  ③ 불변식: 앞으로 훑은 개수 = 뒤로 훑은 개수 = 크기,
//        모든 노드가 해시로도 찾아짐, 앞/뒤 포인터가 서로 대칭  ④ 노드 주소 안정성(확장·순서 변경 후에도 값 포인터 유효)과 소멸자 해제
template <class K, class V, class Hash = std::hash<K>>
class LinkedHashMap {
    struct Node { K key; V val; Node* hnext; Node* before; Node* after; };
    std::vector<Node*> b; Node* head = nullptr; Node* tail = nullptr; size_t n = 0, capacity; bool accessOrder;
    std::vector<K> evicted_;
    size_t idx(const K& k, size_t m) const { return Hash{}(k) % m; }
    Node* lookup(const K& k) const { for (Node* p = b[idx(k, b.size())]; p; p = p->hnext) if (p->key == k) return p; return nullptr; }
    void unlink(Node* p) { if (p->before) p->before->after = p->after; else head = p->after; if (p->after) p->after->before = p->before; else tail = p->before; p->before = p->after = nullptr; }
    void linkLast(Node* p) { p->before = tail; p->after = nullptr; if (tail) tail->after = p; else head = p; tail = p; }
    void touch(Node* p) { if (accessOrder && p != tail) { unlink(p); linkLast(p); } }
    void grow() {
        std::vector<Node*> nb(b.size() * 2, nullptr);
        for (Node* h : b) for (Node* p = h; p;) { Node* nx = p->hnext; size_t i = idx(p->key, nb.size()); p->hnext = nb[i]; nb[i] = p; p = nx; }
        b.swap(nb);
    }
    void removeNode(Node* p) {                                           // 해시 사슬과 리스트에서 모두 뗀다
        Node** pp = &b[idx(p->key, b.size())]; while (*pp != p) pp = &(*pp)->hnext; *pp = p->hnext; unlink(p); delete p; --n;
    }
public:
    explicit LinkedHashMap(bool access = false, size_t cap = 0) : b(8, nullptr), capacity(cap), accessOrder(access) {}
    LinkedHashMap(const LinkedHashMap&) = delete; LinkedHashMap& operator=(const LinkedHashMap&) = delete;
    ~LinkedHashMap() { for (Node* p = head; p;) { Node* nx = p->after; delete p; p = nx; } }
    void put(const K& k, const V& v) {
        if (Node* p = lookup(k)) { p->val = v; touch(p); return; }
        if (n + 1 > b.size()) grow();
        Node* nd = new Node{k, v, nullptr, nullptr, nullptr}; size_t i = idx(k, b.size()); nd->hnext = b[i]; b[i] = nd; linkLast(nd); ++n;
        if (capacity && n > capacity) { evicted_.push_back(head->key); removeNode(head); }       // 가장 오래된 항목 제거
    }
    V* get(const K& k) { Node* p = lookup(k); if (!p) return nullptr; touch(p); return &p->val; }       // 접근 순서 모드면 맨 뒤로
    V* peek(const K& k) { Node* p = lookup(k); return p ? &p->val : nullptr; }                         // 순서를 바꾸지 않는 조회
    bool erase(const K& k) { Node* p = lookup(k); if (!p) return false; removeNode(p); return true; }
    std::vector<K> keys() const { std::vector<K> r; for (Node* p = head; p; p = p->after) r.push_back(p->key); return r; }
    std::vector<K> keysReverse() const { std::vector<K> r; for (Node* p = tail; p; p = p->before) r.push_back(p->key); return r; }
    std::vector<K> takeEvicted() { std::vector<K> r; r.swap(evicted_); return r; }
    size_t size() const { return n; }
    bool valid() const {
        size_t f = 0, back = 0, inHash = 0;
        for (Node* p = head; p; p = p->after) { ++f; if (p->after && p->after->before != p) return false; if (!p->after && p != tail) return false; if (lookup(p->key) != p) return false; }
        for (Node* p = tail; p; p = p->before) ++back;
        for (Node* h : b) for (Node* p = h; p; p = p->hnext) ++inHash;
        return f == n && back == n && inHash == n && (n == 0 ? (!head && !tail) : (!head->before && !tail->after));
    }
};
struct Model {                                                           // 모델: 순서대로 담은 벡터
    std::vector<std::pair<int, int>> v; bool access; size_t cap; std::vector<int> evicted;
    Model(bool a, size_t c) : access(a), cap(c) {}
    long find(int k) const { for (size_t i = 0; i < v.size(); i++) if (v[i].first == k) return (long)i; return -1; }
    void toEnd(long i) { auto e = v[i]; v.erase(v.begin() + i); v.push_back(e); }
    void put(int k, int val) { long i = find(k); if (i >= 0) { v[i].second = val; if (access) toEnd(i); return; } v.push_back({k, val}); if (cap && v.size() > cap) { evicted.push_back(v.front().first); v.erase(v.begin()); } }
    int* get(int k) { long i = find(k); if (i < 0) return nullptr; if (access) { toEnd(i); i = (long)v.size() - 1; } return &v[(size_t)i].second; }
    bool erase(int k) { long i = find(k); if (i < 0) return false; v.erase(v.begin() + i); return true; }
    std::vector<int> keys() const { std::vector<int> r; for (auto& e : v) r.push_back(e.first); return r; }
};

int main() {
    LinkedHashMap<std::string, int> ins;                                  // 삽입 순서
    ins.put("c", 3); ins.put("a", 1); ins.put("b", 2); ins.put("a", 10);   // 갱신은 순서를 바꾸지 않는다
    assert((ins.keys() == std::vector<std::string>{"c", "a", "b"}) && *ins.get("a") == 10);
    LinkedHashMap<std::string, int> acc(true);                            // 접근 순서 (LRU 캐시의 기초)
    acc.put("x", 1); acc.put("y", 2); acc.put("z", 3);
    acc.get("x");
    assert((acc.keys() == std::vector<std::string>{"y", "z", "x"}));
    assert(acc.erase("z") && (acc.keys() == std::vector<std::string>{"y", "x"}));
    assert((acc.keysReverse() == std::vector<std::string>{"x", "y"}) && acc.peek("y") != nullptr && (acc.keys() == std::vector<std::string>{"y", "x"}));        // peek 는 순서를 바꾸지 않는다
    LinkedHashMap<int, int> lru(true, 2); lru.put(1, 1); lru.put(2, 2); lru.get(1); lru.put(3, 3);       // 용량 2: 2 가 쫓겨난다
    assert((lru.keys() == std::vector<int>{1, 3}) && (lru.takeEvicted() == std::vector<int>{2}) && lru.get(2) == nullptr && lru.valid());
    LinkedHashMap<int, int> empty; assert(empty.keys().empty() && empty.get(1) == nullptr && !empty.erase(1) && empty.valid());
    // ② 모델 대조
    std::mt19937 rng(11); long hits = 0, evictions = 0;
    for (int config = 0; config < 3; ++config) {
        bool access = config > 0; size_t cap = config == 2 ? 8 : 0; LinkedHashMap<int, int> lh(access, cap); Model md(access, cap);
        for (int step = 0; step < 50000; ++step) {
            int k = (int)(rng() % 30), op = (int)(rng() % 10);
            if (op < 5) { lh.put(k, step); md.put(k, step); }
            else if (op < 8) { int* got = lh.get(k); int* want = md.get(k); assert((got != nullptr) == (want != nullptr) && (!got || *got == *want)); hits += got != nullptr; }
            else if (op < 9) { assert(lh.erase(k) == md.erase(k)); }
            else { int* p = lh.peek(k); long i = md.find(k); assert((p != nullptr) == (i >= 0) && (!p || *p == md.v[i].second)); }
            assert(lh.size() == md.v.size() && lh.keys() == md.keys());
            if (step % 100 == 0) { assert(lh.valid()); std::vector<int> rev = lh.keysReverse(); std::reverse(rev.begin(), rev.end()); assert(rev == lh.keys()); }
        }
        if (config == 2) { std::vector<int> ev = lh.takeEvicted(); assert(ev == md.evicted && ev.size() > 100); evictions = (long)ev.size(); }
    }
    assert(hits > 20000 && evictions > 100);
    // ④ 노드 주소 안정성
    {   LinkedHashMap<int, int> lh(true); std::vector<int*> ptrs; for (int i = 0; i < 100; i++) { lh.put(i, i * 3); ptrs.push_back(lh.peek(i)); }
        for (int i = 100; i < 5000; i++) lh.put(i, i); for (int i = 0; i < 100; i += 3) lh.get(i); for (int i = 0; i < 100; i++) { assert(lh.peek(i) == ptrs[i] && *ptrs[i] == i * 3); } assert(lh.valid()); }
    std::cout << "LinkedHashMap verified: " << hits << " reads matched the ordered model; LRU evicted " << evictions << " keys in the same order." << std::endl;
    return 0;
}
// Time Complexity: put/get/erase 평균 O(1)
// Space Complexity: O(n)
```
## Multimap()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

// 멀티맵: 하나의 키에 여러 값을 허용한다. 해시 버전은 두 가지로 만든다 — ① 키 → 값 목록(여기서는 키마다 벡터): count(k) 와 equal_range(k) 가 O(값 개수), erase(k) 가 O(값 개수) ② 같은 키 항목을 같은 버킷 안에서 이웃하게 두는 방식(std::unordered_multimap). ①로 만들어 std::unordered_multimap 과 비교한다. 값의 *삽입 순서* 는 ①에서 보존되지만 표준 컨테이너는 보장하지 않으므로 비교는 키별 값의 멀티집합으로 한다.
// 연산 의미(검증 대상): insert 는 항상 새 항목을 추가(키 중복 허용), count(k) 는 k 의 값 개수, erase(k) 는 k 의 모든 값을 지우고 개수를 반환, erase(k, v) 는 (k, v) 한 개만 지우고 지웠는지 반환(같은 값이 여럿이면 하나만), size() 는 전체 항목 수, contains(k, v) 는 쌍의 존재. 키가 사라지면 빈 목록을 남기지 않는다(메모리 누수·size 오류 방지).
// 검증: 무작위 연산 20 만 번(삽입·키 삭제·쌍 삭제·조회·개수) 을 unordered_multimap 과 비교 — 반환값, 크기, 키별 값 멀티집합; 같은 쌍을 여러 번 넣고 하나씩 지우기; 100 만 항목 삽입 뒤 크기·키 개수; 키별 삽입 순서 보존.
struct Multimap {
    using Key = std::uint64_t;
    std::vector<std::vector<std::pair<Key, std::vector<int>>>> b; std::size_t total = 0, keys = 0;
    explicit Multimap(std::size_t m = 1024) : b(m) {}
    std::size_t idx(Key k) const { k += 0x9e3779b97f4a7c15ULL; k = (k ^ (k >> 30)) * 0xbf58476d1ce4e5b9ULL; k = (k ^ (k >> 27)) * 0x94d049bb133111ebULL; return (std::size_t)((k ^ (k >> 31)) % b.size()); }
    std::vector<int>* find(Key k) { for (auto& e : b[idx(k)]) if (e.first == k) return &e.second; return nullptr; }
    const std::vector<int>* find(Key k) const { for (auto& e : b[idx(k)]) if (e.first == k) return &e.second; return nullptr; }
    void insert(Key k, int v) { if (auto* l = find(k)) l->push_back(v); else { b[idx(k)].push_back({k, {v}}); ++keys; } ++total; }
    std::size_t count(Key k) const { auto* l = find(k); return l ? l->size() : 0; }
    const std::vector<int>& equalRange(Key k) const { static const std::vector<int> none; auto* l = find(k); return l ? *l : none; }
    std::size_t erase(Key k) { auto& chain = b[idx(k)]; for (std::size_t i = 0; i < chain.size(); ++i) if (chain[i].first == k) { std::size_t n = chain[i].second.size(); chain[i] = chain.back(); chain.pop_back(); total -= n; --keys; return n; } return 0; }
    bool erasePair(Key k, int v) { auto& chain = b[idx(k)]; for (std::size_t i = 0; i < chain.size(); ++i) if (chain[i].first == k) { auto& l = chain[i].second; auto it = std::find(l.begin(), l.end(), v); if (it == l.end()) return false; l.erase(it); --total; if (l.empty()) { chain[i] = chain.back(); chain.pop_back(); --keys; } return true; } return false; }
    bool contains(Key k, int v) const { auto* l = find(k); return l && std::find(l->begin(), l->end(), v) != l->end(); }
};
std::vector<int> sortedValues(const std::unordered_multimap<std::uint64_t, int>& ref, std::uint64_t k) { std::vector<int> v; auto r = ref.equal_range(k); for (auto it = r.first; it != r.second; ++it) v.push_back(it->second); std::sort(v.begin(), v.end()); return v; }

int main() {
    std::mt19937_64 rng(13);
    // ① 무작위 연산 20 만 번 (키 범위 300, 값 범위 6 → 같은 쌍이 자주 겹침)
    {   Multimap mm(97); std::unordered_multimap<std::uint64_t, int> ref; long pairErases = 0;
        for (int i = 0; i < 200000; ++i) {
            std::uint64_t k = rng() % 300; int v = (int)(rng() % 6); int op = (int)(rng() % 10);
            if (op < 4) { mm.insert(k, v); ref.emplace(k, v); }
            else if (op == 4) { std::size_t a = mm.erase(k); std::size_t c = ref.erase(k); assert(a == c); }
            else if (op < 7) { bool had = false; auto r = ref.equal_range(k); for (auto it = r.first; it != r.second; ++it) if (it->second == v) { ref.erase(it); had = true; break; } assert(mm.erasePair(k, v) == had); pairErases += had; }
            else if (op == 7) assert(mm.count(k) == ref.count(k));
            else if (op == 8) { std::vector<int> a = mm.equalRange(k); std::sort(a.begin(), a.end()); assert(a == sortedValues(ref, k)); }
            else assert(mm.contains(k, v) == (std::count_if(ref.equal_range(k).first, ref.equal_range(k).second, [&](const std::pair<const std::uint64_t, int>& e) { return e.second == v; }) > 0));
            assert(mm.total == ref.size());
        }
        std::size_t distinct = 0; for (std::uint64_t k = 0; k < 300; ++k) distinct += ref.count(k) > 0; assert(mm.keys == distinct && pairErases > 10000);
        for (std::uint64_t k = 0; k < 300; ++k) { std::vector<int> a = mm.equalRange(k); std::sort(a.begin(), a.end()); assert(a == sortedValues(ref, k)); }
        for (auto& chain : mm.b) for (auto& e : chain) assert(!e.second.empty()); }                       // 빈 목록이 남지 않는다
    // ② 같은 쌍을 여러 번 넣고 하나씩 지우기, 삽입 순서 보존
    {   Multimap mm; for (int i = 0; i < 5; ++i) mm.insert(7, 42); mm.insert(7, 1); mm.insert(7, 42); assert(mm.count(7) == 7 && mm.keys == 1 && mm.total == 7);
        for (int i = 0; i < 6; ++i) assert(mm.erasePair(7, 42)); assert(!mm.erasePair(7, 42) && mm.count(7) == 1 && mm.equalRange(7) == std::vector<int>({1}));
        assert(mm.erasePair(7, 1) && mm.keys == 0 && mm.total == 0 && mm.equalRange(7).empty() && mm.erase(7) == 0);
        Multimap order; for (int v : {5, 3, 9, 1, 3}) order.insert(8, v); assert(order.equalRange(8) == std::vector<int>({5, 3, 9, 1, 3})); }
    // ③ 100 만 항목: 크기 · 키 개수 · 임의 조회
    {   Multimap mm(1 << 16); std::map<std::uint64_t, long> cnt; for (int i = 0; i < 1000000; ++i) { std::uint64_t k = rng() % 50000; mm.insert(k, i); ++cnt[k]; }
        assert(mm.total == 1000000 && mm.keys == cnt.size()); for (int q = 0; q < 2000; ++q) { std::uint64_t k = rng() % 50000; assert((long)mm.count(k) == (cnt.count(k) ? cnt[k] : 0)); }
        std::cout << "Multimap: 200,000 random insert / erase-key / erase-pair / count / equal-range / contains operations matched std::unordered_multimap (return values, sizes and per-key value multisets), no empty value lists were left behind, duplicates of one pair were removed one at a time, insertion order was preserved per key, and a 1,000,000-entry map reported the right size and key count" << std::endl; }
    return 0;
}
// Time Complexity: insert 분할상환 O(1), erase(key) O(값 개수)
// Space Complexity: O(n)
```
# Part 7. 분산 해시
## ConsistentHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

// 일관된 해싱: 노드와 키를 같은 해시 링(2^32)에 놓고, 키는 시계 방향으로 처음 만나는 노드가 맡는다.
// 노드가 늘거나 줄어도 이웃 구간의 키만 이동한다.  노드마다 가상 노드(여러 점)를 두면 부하가 고르게 퍼지고, 가중치만큼 점을 더 주면 용량이 큰 서버가 더 많이 맡는다.
// 두 노드의 점이 우연히 같은 해시값을 가질 수 있으므로 점의 키를 (해시, 노드 이름) 쌍으로 둔다 — 해시값만 키로 쓰면 뒤에 넣은 노드가 앞의 노드를 조용히 덮어쓴다.  복제는 시계 방향의 서로 다른 노드 r 개
// 검증: ① 손으로 짠 예(노드 하나 추가 시 이동한 키는 전부 새 노드로)  ② 5 000 개 키의 소유자를 *세 가지 독립 구현* (std::map 링, 정렬 벡터 + 이분 탐색, 모든 점을 훑어 시계 방향 최단 거리를 고르는 브루트포스)이 모두 같게 낸다
//        ③ 단조성: 노드를 더하면 이동한 키는 전부 새 노드로만, 빼면 *그 노드가 맡던 키만* 이동 (정확히 일치)  ④ 균형: 가상 노드 1·10·100·1 000 개에서 가장 바쁜 노드의 부하 / 평균이 줄어든다  ⑤ 가중치 3 인 노드가 약 3 배
//        ⑥ 충돌 강제(해시를 8 비트로 줄임): 점이 겹쳐도 노드가 사라지지 않고, 하나를 빼도 같은 점의 다른 노드가 남음  ⑦ 복제 r = 3 의 서로 다른 노드, 빈 링
uint32_t h32(const std::string& s) {
    uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16;
    return h;
}

class Ring {
    typedef std::pair<uint32_t, std::string> Point;                        // (링 위의 위치, 노드 이름)
    std::map<Point, int> ring; int vnodes; uint32_t mask;                  // mask: 해시를 줄여 충돌을 일부러 만들 때 사용
    uint32_t pointHash(const std::string& node, int j) const { return h32(node + "#" + std::to_string(j)) & mask; }
public:
    explicit Ring(int v = 1, uint32_t m = 0xFFFFFFFFu) : vnodes(v), mask(m) {}
    uint32_t keyHash(const std::string& key) const { return h32(key) & mask; }
    void add(const std::string& node, int weight = 1) { for (int j = 0; j < vnodes * weight; j++) ring[{pointHash(node, j), node}] = 1; }
    void remove(const std::string& node, int weight = 1) { for (int j = 0; j < vnodes * weight; j++) ring.erase({pointHash(node, j), node}); }
    std::string owner(const std::string& key) const {
        if (ring.empty()) return "";
        auto it = ring.lower_bound({keyHash(key), std::string()});
        if (it == ring.end()) it = ring.begin();             // 링이므로 끝에서 처음으로 돌아간다
        return it->first.second;
    }
    std::vector<std::string> owners(const std::string& key, size_t r) const {      // 시계 방향으로 만나는 서로 다른 노드 r 개
        std::vector<std::string> out; if (ring.empty()) return out;
        auto it = ring.lower_bound({keyHash(key), std::string()});
        for (size_t seen = 0; seen < ring.size() && out.size() < r; seen++) { if (it == ring.end()) it = ring.begin(); if (std::find(out.begin(), out.end(), it->first.second) == out.end()) out.push_back(it->first.second); ++it; }
        return out;
    }
    std::vector<Point> points() const { std::vector<Point> v; for (auto& kv : ring) v.push_back(kv.first); return v; }
    size_t pointCount() const { return ring.size(); }
    std::set<std::string> nodes() const { std::set<std::string> s; for (auto& kv : ring) s.insert(kv.first.second); return s; }
};
std::string ownerSorted(const std::vector<std::pair<uint32_t, std::string>>& pts, uint32_t h) {            // 구현 2: 정렬된 벡터 + 이분 탐색
    auto it = std::lower_bound(pts.begin(), pts.end(), std::make_pair(h, std::string())); if (it == pts.end()) it = pts.begin(); return it->second;
}
std::string ownerBrute(const std::vector<std::pair<uint32_t, std::string>>& pts, uint32_t h) {              // 구현 3: 모든 점 중 시계 방향 거리 (점 - 키) mod 2^32 가 가장 작은 것 (동률은 이름 순)
    uint64_t bestD = ~0ULL; std::string best; for (auto& p : pts) { uint64_t d = (uint64_t)(uint32_t)(p.first - h); if (d < bestD || (d == bestD && p.second < best)) { bestD = d; best = p.second; } } return best;
}

int main() {
    Ring r;
    for (int i = 0; i < 5; i++) r.add("node" + std::to_string(i));
    const int K = 10000;
    std::vector<std::string> before(K);
    for (int i = 0; i < K; i++) before[i] = r.owner("key" + std::to_string(i));
    r.add("node5");                                          // 노드 추가
    int moved = 0;
    for (int i = 0; i < K; i++) {
        const std::string now = r.owner("key" + std::to_string(i));
        if (now != before[i]) { moved++; assert(now == "node5"); }   // 이동한 키는 전부 새 노드로만 간다
    }
    assert(moved < K / 2);
    // ② 세 구현의 일치
    Ring big(50); for (int i = 0; i < 8; i++) big.add("srv" + std::to_string(i));
    std::vector<std::pair<uint32_t, std::string>> pts = big.points();
    assert(pts.size() == 400 && std::is_sorted(pts.begin(), pts.end()));
    for (int i = 0; i < 5000; i++) { std::string key = "item:" + std::to_string(i * 7919); uint32_t h = big.keyHash(key); std::string a = big.owner(key); assert(a == ownerSorted(pts, h) && a == ownerBrute(pts, h)); }
    // ③ 단조성
    auto owners = [&](Ring& ring, int n) { std::vector<std::string> v(n); for (int i = 0; i < n; i++) v[i] = ring.owner("k" + std::to_string(i)); return v; };
    {   Ring ring(40); for (int i = 0; i < 10; i++) ring.add("n" + std::to_string(i)); auto a = owners(ring, 20000); ring.add("n10"); auto b = owners(ring, 20000);
        int movedAdd = 0; for (int i = 0; i < 20000; i++) if (a[i] != b[i]) { assert(b[i] == "n10"); ++movedAdd; }
        double frac = (double)movedAdd / 20000; assert(frac > 0.5 / 11 && frac < 1.6 / 11);                                   // 이상값 1/11
        ring.remove("n3"); auto c = owners(ring, 20000); int movedRm = 0;
        for (int i = 0; i < 20000; i++) { if (b[i] == "n3") { assert(c[i] != "n3"); ++movedRm; } else assert(c[i] == b[i]); }       // 빼면 그 노드가 맡던 키만 이동
        assert(movedRm > 0); }
    // ④ 균형
    double imbalance[4]; const int vs[4] = {1, 10, 100, 1000};
    for (int t = 0; t < 4; t++) {
        Ring ring(vs[t]); for (int i = 0; i < 20; i++) ring.add("node" + std::to_string(i)); std::map<std::string, int> load; const int KK = 100000;
        for (int i = 0; i < KK; i++) load[ring.owner("obj" + std::to_string(i))]++;
        int mx = 0; for (auto& kv : load) mx = std::max(mx, kv.second); imbalance[t] = (double)mx / ((double)KK / 20);
    }
    assert(imbalance[0] > 1.8 && imbalance[3] < 1.3 && imbalance[1] < imbalance[0] && imbalance[2] < imbalance[1] && imbalance[3] < imbalance[2]);
    // ⑤ 가중치
    {   Ring ring(300); for (int i = 0; i < 4; i++) ring.add("w" + std::to_string(i)); ring.add("heavy", 3); std::map<std::string, int> load; const int KK = 100000;
        for (int i = 0; i < KK; i++) load[ring.owner("x" + std::to_string(i))]++;
        double share = (double)load["heavy"] / KK; assert(share > 0.36 && share < 0.50 && load.size() == 5); }                // 3 / 7 ≈ 0.43
    // ⑥ 충돌 강제: 해시를 8 비트로 줄여 40 노드 × 4 점이 256 칸에 몰린다
    {   Ring tiny(4, 0xFF); for (int i = 0; i < 40; i++) tiny.add("t" + std::to_string(i));
        assert(tiny.pointCount() > 140 && tiny.pointCount() <= 160 && tiny.nodes().size() == 40);                              // (해시, 이름) 쌍이 키라서 40 노드 모두 남는다 (같은 노드의 가상 노드끼리 겹치는 점만 합쳐진다)
        std::set<uint32_t> distinct; size_t t7points = 0; for (auto& p : tiny.points()) { distinct.insert(p.first); t7points += p.second == "t7"; } assert(distinct.size() < tiny.pointCount());    // 서로 다른 노드의 점이 같은 칸에 겹친 경우가 실제로 있다
        size_t beforePoints = tiny.pointCount(); tiny.remove("t7"); assert(tiny.nodes().size() == 39 && tiny.pointCount() == beforePoints - t7points);
        for (int i = 0; i < 2000; i++) { std::string o = tiny.owner("q" + std::to_string(i)); assert(o != "t7" && !o.empty()); } }
    // ⑦ 복제와 빈 링
    {   Ring ring(20); for (int i = 0; i < 6; i++) ring.add("s" + std::to_string(i));
        for (int i = 0; i < 2000; i++) { std::string key = "rep" + std::to_string(i); auto o = ring.owners(key, 3); assert(o.size() == 3 && o[0] == ring.owner(key) && std::set<std::string>(o.begin(), o.end()).size() == 3); }
        Ring two(5); two.add("a"); two.add("b"); assert(two.owners("x", 3).size() == 2);                                      // 노드보다 많이 요청하면 노드 수만큼
        Ring none; assert(none.owner("x").empty() && none.owners("x", 2).empty()); }
    std::cout << "moved " << moved << " of " << K << " keys after adding a node; max load / average with 1, 10, 100, 1000 virtual nodes: " << imbalance[0] << " " << imbalance[1] << " " << imbalance[2] << " " << imbalance[3] << std::endl;
    return 0;
}
// Time Complexity: 조회 O(log N)
// Space Complexity: O(N)
```
## VirtualNode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// 가상 노드(virtual node): 일관된 해싱(consistent hashing) 링에서 물리 노드 하나를 링 위의 여러 지점(node#0, node#1, …)에 배치해 부하를 고르게 만든다. 노드가 링에 1 개 점이면 점 사이 구간 길이가 지수 분포처럼 들쭉날쭉해서 가장 큰 구간의 노드가 평균의 O(log N) 배를 떠안는다; 노드마다 v 개의 점을 두면 부하의 변동계수가 1/√v 로 줄어든다(독립 구간 v 개의 합). 가중치가 다른 노드는 가상 노드 수를 가중치에 비례시킨다.
// 키의 담당 노드 = 링에서 키 해시 이상인 첫 점(시계 방향 후계자, 끝이면 처음으로 감김)의 노드. 노드 추가·제거 시 이동하는 키는 *바로 그 노드의 구간에 속한 키뿐* 이다 — 추가하면 새 노드로만 가고, 제거하면 그 노드의 키만 이웃들로 흩어진다(정확히 검증).
// 검증: ① 링 조회가 정렬 배열 선형 탐색(후계자 정의 그대로) 과 10 만 키에서 일치 ② v = 1, 10, 100, 1000 에서 최대/평균 부하와 변동계수가 단조 감소, cv(v)·√v 가 거의 상수(≈ 1) ③ 노드 추가: 이동한 키가 모두 새 노드로 가고 비율이 1/(N+1) 근처, 제거: 제거된 노드의 키만 이동 ④ 가중 노드: 가상 노드 수 2 배 → 부하 약 2 배 ⑤ 복제본 선택: 시계 방향으로 *서로 다른 물리 노드* R 개 ⑥ 모듈로 해싱(h mod N)은 N → N + 1 에서 N/(N+1) 의 키가 이동.
std::uint64_t mix(std::uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
std::uint64_t pointHash(int node, int replica) { return mix(((std::uint64_t)node << 32) ^ (std::uint64_t)replica ^ 0xfeedfaceULL); }
struct Ring {
    std::map<std::uint64_t, int> ring;                                                         // 해시 → 물리 노드
    void add(int node, int vnodes) { for (int r = 0; r < vnodes; ++r) ring[pointHash(node, r)] = node; }
    void remove(int node, int vnodes) { for (int r = 0; r < vnodes; ++r) ring.erase(pointHash(node, r)); }
    int lookup(std::uint64_t keyHash) const { auto it = ring.lower_bound(keyHash); if (it == ring.end()) it = ring.begin(); return it->second; }
    std::vector<int> replicas(std::uint64_t keyHash, int r) const { std::vector<int> out; auto it = ring.lower_bound(keyHash); for (std::size_t seen = 0; seen < ring.size() && (int)out.size() < r; ++seen) { if (it == ring.end()) it = ring.begin(); if (std::find(out.begin(), out.end(), it->second) == out.end()) out.push_back(it->second); ++it; } return out; }
};
struct Load { double maxOverMean, cv; };
Load loadOf(const Ring& ring, int nodes, int keys, std::uint64_t seed) {
    std::vector<long> load(nodes, 0); for (int i = 0; i < keys; ++i) ++load[ring.lookup(mix(seed + i))]; double mean = (double)keys / nodes, var = 0; long mx = 0; for (long l : load) { var += (l - mean) * (l - mean); mx = std::max(mx, l); } return {(double)mx / mean, std::sqrt(var / nodes) / mean};
}

int main() {
    std::mt19937_64 rng(14);
    // ① 링 조회 = 정렬 배열 선형 탐색 (후계자의 정의 그대로)
    {   Ring r; for (int n = 0; n < 7; ++n) r.add(n, 20); std::vector<std::pair<std::uint64_t, int>> pts(r.ring.begin(), r.ring.end());
        for (int i = 0; i < 100000; ++i) { std::uint64_t h = rng(); int expect = pts.front().second; for (auto& p : pts) if (p.first >= h) { expect = p.second; break; } assert(r.lookup(h) == expect); } }
    // ② 부하 균형: 노드 10 개, 키 20 만 개
    double prevCv = 1e9, prevMax = 1e9; double cvTimesSqrt[4]; int idx = 0;
    for (int v : {1, 10, 100, 1000}) { Ring r; for (int n = 0; n < 10; ++n) r.add(n, v); Load l = loadOf(r, 10, 200000, 99); assert(l.cv < prevCv && l.maxOverMean < prevMax); prevCv = l.cv; prevMax = l.maxOverMean; cvTimesSqrt[idx++] = l.cv * std::sqrt((double)v); if (v == 1000) assert(l.maxOverMean < 1.15); if (v == 1) assert(l.maxOverMean > 1.5); }
    assert(cvTimesSqrt[1] > 0.5 && cvTimesSqrt[1] < 1.6 && cvTimesSqrt[2] > 0.5 && cvTimesSqrt[2] < 1.6 && cvTimesSqrt[3] > 0.4 && cvTimesSqrt[3] < 1.7);                 // 변동계수 ∝ 1/√v
    // ③ 노드 추가 · 제거 시 이동하는 키
    {   const int N = 10, V = 200, K = 100000; Ring r; for (int n = 0; n < N; ++n) r.add(n, V); std::vector<int> before(K); for (int i = 0; i < K; ++i) before[i] = r.lookup(mix(1000 + i));
        r.add(N, V); int moved = 0; for (int i = 0; i < K; ++i) { int now = r.lookup(mix(1000 + i)); if (now != before[i]) { assert(now == N); ++moved; } }                                  // 이동한 키는 모두 새 노드로
        double frac = (double)moved / K; assert(frac > 0.07 && frac < 0.115);                                                                                                       // ≈ 1/11 = 0.0909
        std::vector<int> mid(K); for (int i = 0; i < K; ++i) mid[i] = r.lookup(mix(1000 + i)); r.remove(3, V); int movedOut = 0, owned = 0;
        for (int i = 0; i < K; ++i) { int now = r.lookup(mix(1000 + i)); if (mid[i] == 3) { ++owned; assert(now != 3); } else assert(now == mid[i]); movedOut += now != mid[i]; } assert(movedOut == owned && owned > 0);        // 제거: 그 노드의 키만 이동
        // ⑥ 모듈로 해싱 비교
        int modMoved = 0; for (int i = 0; i < K; ++i) modMoved += mix(1000 + i) % N != mix(1000 + i) % (N + 1); double modFrac = (double)modMoved / K; assert(modFrac > 0.88 && modFrac < 0.93);
        std::cout << "VirtualNode: adding an 11th node moved " << frac << " of the keys (1/11 = 0.0909), all to the new node, whereas modulo hashing moved " << modFrac << " (N/(N+1) = 0.909)" << std::endl; }
    // ④ 가중 노드: 노드 0 은 가상 노드 200 개, 나머지 4 개는 100 개 → 노드 0 의 부하 ≈ 200/600 = 1/3 = 다른 노드 평균(1/6)의 2 배
    {   Ring r; r.add(0, 400); for (int n = 1; n <= 4; ++n) r.add(n, 200); std::vector<long> load(5, 0); const int K = 300000; for (int i = 0; i < K; ++i) ++load[r.lookup(mix(555 + i))];
        double w0 = (double)load[0] / K, expect = 400.0 / 1200.0; assert(std::abs(w0 - expect) < 0.03); }
    // ⑤ 복제본: 시계 방향으로 서로 다른 물리 노드 R 개 (가상 노드가 연속으로 같은 물리 노드여도 건너뜀)
    {   Ring r; for (int n = 0; n < 6; ++n) r.add(n, 50); for (int i = 0; i < 20000; ++i) for (int R : {1, 2, 3, 5, 6}) { auto reps = r.replicas(mix(77 + i), R); assert((int)reps.size() == R && std::set<int>(reps.begin(), reps.end()).size() == (std::size_t)R && reps[0] == r.lookup(mix(77 + i))); } assert(r.replicas(1, 9).size() == 6); }
    return 0;
}
// Time Complexity: 조회 O(log(N·V)), 노드 추가·제거 O(V log(N·V))
// Space Complexity: O(N·V)
```
## RendezvousHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 랑데부 해싱(HRW, Highest Random Weight): 키마다 *모든 노드* 의 점수 score(key, node) = hash(key, node) 를 계산해 가장 높은 노드를 담당으로 정한다. 링 구조·가상 노드가 필요 없고 균형이 자동으로 좋으며, 노드를 제거하면 *그 노드의 키만* 이동하고(점수 순위는 다른 노드끼리 변하지 않는다), 추가하면 *새 노드가 최고가 된 키만* 새 노드로 간다 — 이동 비율 정확히 기대값 1/(N+1). 조회는 O(N) (링은 O(log N)) 이므로 노드 수가 수십 개 이하일 때 단순함이 이점이다.
// 가중치: score = −w / ln(U) (U = hash 를 (0, 1] 로 정규화) 로 하면 노드가 이길 확률이 정확히 w / Σw 다(지수 분포의 최솟값 성질). 상위 R 개 점수의 노드 = 복제본 집합이며 순서도 일관된다(R 개 선택은 최고 점수 선택의 접두사).
// 검증: ① 조회가 결정적이고 점수 최댓값 정의와 같음 ② 노드 제거 → 제거된 노드의 키만 이동(정확), 추가 → 이동한 키는 모두 새 노드로, 이동 비율이 1/(N+1) 의 ±15% ③ 노드 10 개 · 키 20 만 개의 부하가 균등(카이제곱: 자유도 9 ± 5σ) ④ 가중치 1:2:3 → 승률 1/6, 1/3, 1/2 (±0.01) ⑤ 복제본 상위 R 개는 R−1 개의 접두사 확장 ⑥ 노드 수가 달라도 모듈로 해싱(N/(N+1) 이동)보다 훨씬 적게 이동.
std::uint64_t mix(std::uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
std::uint64_t score(std::uint64_t key, int node) { return mix(key * 0x2545f4914f6cdd1dULL ^ mix((std::uint64_t)node + 1)); }
int owner(std::uint64_t key, const std::vector<int>& nodes) { int best = -1; std::uint64_t bs = 0; for (int n : nodes) { std::uint64_t s = score(key, n); if (best < 0 || s > bs || (s == bs && n < best)) { best = n; bs = s; } } return best; }
int weightedOwner(std::uint64_t key, const std::vector<int>& nodes, const std::vector<double>& w) {
    int best = -1; double bs = -1; for (std::size_t i = 0; i < nodes.size(); ++i) { double u = ((double)(score(key, nodes[i]) >> 11) + 1.0) / 9007199254740993.0; double s = -w[i] / std::log(u); if (s > bs) { bs = s; best = nodes[i]; } } return best;
}
std::vector<int> topR(std::uint64_t key, const std::vector<int>& nodes, int R) { std::vector<int> v = nodes; std::sort(v.begin(), v.end(), [&](int a, int b) { std::uint64_t sa = score(key, a), sb = score(key, b); return sa != sb ? sa > sb : a < b; }); v.resize(std::min<std::size_t>(R, v.size())); return v; }

int main() {
    // ①② 결정성 · 제거 · 추가
    const int K = 100000; std::vector<int> nodes; for (int i = 0; i < 10; ++i) nodes.push_back(i);
    std::vector<int> before(K); for (int i = 0; i < K; ++i) { before[i] = owner(mix(i), nodes); assert(before[i] == owner(mix(i), nodes)); }
    {   std::vector<int> fewer; for (int n : nodes) if (n != 4) fewer.push_back(n); int moved = 0, owned = 0;
        for (int i = 0; i < K; ++i) { int now = owner(mix(i), fewer); if (before[i] == 4) { ++owned; assert(now != 4); } else assert(now == before[i]); moved += now != before[i]; } assert(moved == owned && owned > 0);
        std::vector<int> more = nodes; more.push_back(10); int movedIn = 0; for (int i = 0; i < K; ++i) { int now = owner(mix(i), more); if (now != before[i]) { assert(now == 10); ++movedIn; } }
        double frac = (double)movedIn / K; assert(frac > 0.0909 * 0.85 && frac < 0.0909 * 1.15);
        int modMoved = 0; for (int i = 0; i < K; ++i) modMoved += mix(i) % 10 != mix(i) % 11; assert(modMoved > 8 * movedIn);
        std::cout << "RendezvousHash: removing a node moved exactly its own " << owned << " keys; adding an 11th node moved " << frac << " of the keys, all to the new node, against " << (double)modMoved / K << " for modulo hashing" << std::endl; }
    // ③ 균등성: 노드 10 개, 키 20 만 개의 카이제곱
    {   std::vector<long> load(10, 0); const int KK = 200000; for (int i = 0; i < KK; ++i) ++load[owner(mix(5000000 + i), nodes)]; double e = KK / 10.0, chi = 0; for (long l : load) chi += (l - e) * (l - e) / e; assert(std::abs(chi - 9) < 5 * std::sqrt(18.0)); }
    // ④ 가중치 1:2:3 → 승률 1/6, 1/3, 1/2
    {   std::vector<int> ns = {0, 1, 2}; std::vector<double> w = {1, 2, 3}; std::vector<long> win(3, 0); const int KK = 300000; for (int i = 0; i < KK; ++i) ++win[weightedOwner(mix(9000000 + i), ns, w)];
        assert(std::abs((double)win[0] / KK - 1.0 / 6) < 0.01 && std::abs((double)win[1] / KK - 1.0 / 3) < 0.01 && std::abs((double)win[2] / KK - 0.5) < 0.01); }
    // ⑤ 복제본: 상위 R 개는 상위 R−1 개의 접두사 확장, 첫 번째는 owner
    for (int i = 0; i < 20000; ++i) { std::uint64_t key = mix(777 + i); auto t1 = topR(key, nodes, 1), t3 = topR(key, nodes, 3), t5 = topR(key, nodes, 5); assert(t1[0] == owner(key, nodes) && std::equal(t1.begin(), t1.end(), t3.begin()) && std::equal(t3.begin(), t3.end(), t5.begin())); }
    // ⑥ 노드 수 N 이 커지는 경우의 이동 비율: 1/(N+1) (N = 2..30)
    for (int N = 2; N <= 30; N += 4) { std::vector<int> a, b; for (int i = 0; i < N; ++i) a.push_back(i); b = a; b.push_back(N); int moved = 0; const int KK = 40000; for (int i = 0; i < KK; ++i) moved += owner(mix(31337 + i), a) != owner(mix(31337 + i), b); double frac = (double)moved / KK, expect = 1.0 / (N + 1); assert(std::abs(frac - expect) < 0.3 * expect + 0.005); }
    return 0;
}
// Time Complexity: 조회 O(N)
// Space Complexity: O(N)
```
## Chord()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// Chord: m비트 식별자 링. 노드 n 의 i번째 finger 는 successor(n + 2^i).
// 조회마다 목표 거리가 최소 절반으로 줄어 O(log N) 홉에 끝난다.  여기서는 정답표(successor 를 전역에서 계산)에 기대지 않고 실제 프로토콜을 흉내 낸다:
// join(기존 노드를 통해 자기 후계자를 찾음) → 주기적으로 stabilize(후계자의 선행자를 확인해 끼어든 노드를 받아들이고 notify) + fixFingers(핑거 재계산), 후계자 목록 r = 3 으로 죽은 노드를 건너뜀
// 검증: ① 손으로 짠 작은 링(원래 예)의 모든 조회  ② 노드 48 개를 하나씩 join 시킨 뒤 수렴(후계자·선행자·모든 핑거가 전역 정답과 일치)하고, 모든 (시작 노드, 키) 조회가 정답이며 홉 수 ≤ m, 평균 홉 < 4.5
//        ③ 이웃한 두 노드가 동시에 죽어도(r - 1 개까지) 링이 복구되고 새 노드가 join 해도 수렴  ④ 노드 N = 16, 64, 256 에서 평균 홉 수가 ½·log2 N 근처(0.25~0.75 배)  ⑤ 키 이전: 노드가 join 하면 옮겨 가는 키는 새 노드가 맡는 (선행자, 새 노드] 구간뿐
const int M = 10, SZ = 1 << M;                                  // 식별자 0..1023
bool inRange(int x, int a, int b, bool inclusiveB) {            // x in (a, b] 또는 (a, b)  (원형, a == b 이면 링 전체)
    if (a < b) return x > a && (inclusiveB ? x <= b : x < b);
    return x > a || (inclusiveB ? x <= b : x < b);
}
class Chord {
    struct Node { int pred = -1; std::vector<int> finger, succ; bool alive = true; };
    std::map<int, Node> net; static const int R = 3;
    bool up(int id) const { auto it = net.find(id); return it != net.end() && it->second.alive; }
    int successorOf(int n) const { for (int s : net.at(n).succ) if (up(s)) return s; return n; }               // 후계자 목록의 첫 생존 노드
    int closestPrecedingFinger(int n, int id) const {
        for (int i = M - 1; i >= 0; i--) { int f = net.at(n).finger[i]; if (up(f) && inRange(f, n, id, false)) return f; }
        return n;
    }
public:
    int findSuccessor(int start, int id, int& hops) const {
        int n = start; hops = 0;
        for (int guard = 0; guard < 2 * SZ; guard++) {
            int s = successorOf(n);
            if (s == n || inRange(id, n, s, true)) return s;    // id 가 (n, 후계자] 에 들면 후계자가 담당
            int nn = closestPrecedingFinger(n, id);
            if (nn == n) nn = s;                                // 핑거가 도움이 안 되면(수렴 전) 후계자로 한 칸
            n = nn; hops++;
        }
        return -1;
    }
    void create(int id) { Node nd; nd.finger.assign(M, id); nd.succ = {id}; net[id] = nd; }
    void join(int id, int via) { assert(!net.count(id) && up(via)); int h; int s = findSuccessor(via, id, h); Node nd; nd.finger.assign(M, s); nd.succ = {s}; net[id] = nd; }
    void fail(int id) { net.at(id).alive = false; }
    void notify(int s, int n) { Node& t = net.at(s); if (t.pred == -1 || !up(t.pred) || inRange(n, t.pred, s, false)) t.pred = n; }
    void stabilize(int n) {
        Node& me = net.at(n);
        if (me.pred != -1 && !up(me.pred)) me.pred = -1;
        int s = successorOf(n); int x = net.at(s).pred;
        if (x != -1 && up(x) && inRange(x, n, s, false)) s = x;                   // 후계자와 나 사이에 새 노드가 끼어 있다
        std::vector<int> list{s}; for (int t : net.at(s).succ) if (t != n && up(t) && std::find(list.begin(), list.end(), t) == list.end() && (int)list.size() < R) list.push_back(t);
        me.succ = list; notify(s, n);
    }
    void fixFingers(int n) { for (int i = 0; i < M; i++) { int h; int f = findSuccessor(n, (n + (1 << i)) % SZ, h); if (f >= 0) net.at(n).finger[i] = f; } }
    void round() { std::vector<int> ids = alive(); for (int n : ids) stabilize(n); for (int n : ids) fixFingers(n); }
    std::vector<int> alive() const { std::vector<int> v; for (auto& kv : net) if (kv.second.alive) v.push_back(kv.first); return v; }
    // ---- 정답표 (검증 전용) ----
    int truthSuccessor(int id) const { std::vector<int> v = alive(); auto it = std::lower_bound(v.begin(), v.end(), id % SZ); return it == v.end() ? v[0] : *it; }
    int truthNext(int n) const { return truthSuccessor((n + 1) % SZ); }
    int truthPrev(int n) const { std::vector<int> v = alive(); auto it = std::lower_bound(v.begin(), v.end(), n); return it == v.begin() ? v.back() : *(it - 1); }
    bool converged() const {
        for (int n : alive()) {
            if (successorOf(n) != truthNext(n) || net.at(n).pred != truthPrev(n)) return false;
            for (int i = 0; i < M; i++) if (net.at(n).finger[i] != truthSuccessor((n + (1 << i)) % SZ)) return false;
        }
        return true;
    }
    int runUntilConverged(int maxRounds) { for (int r = 0; r <= maxRounds; r++) { if (converged()) return r; round(); } return -1; }
    int predOf(int n) const { return net.at(n).pred; }
};
// 전수 검사: 모든 (시작 노드, 키) 조회가 정답이고 홉 수의 최댓값·평균을 돌려준다
void verifyLookups(const Chord& c, int& maxHops, double& avgHops) {
    long total = 0, count = 0; maxHops = 0;
    for (int start : c.alive()) for (int id = 0; id < SZ; id++) { int hops; int got = c.findSuccessor(start, id, hops); assert(got == c.truthSuccessor(id)); maxHops = std::max(maxHops, hops); total += hops; ++count; }
    avgHops = (double)total / count;
}

int main() {
    // ① 작은 링 (원래 예: 노드 {1, 8, 14, 21, 32, 38, 42, 48, 51, 56})
    {   Chord c; std::vector<int> ids = {1, 8, 14, 21, 32, 38, 42, 48, 51, 56}; c.create(ids[0]); for (size_t i = 1; i < ids.size(); i++) { c.join(ids[i], ids[0]); c.round(); }
        assert(c.runUntilConverged(50) >= 0); int mh; double ah; verifyLookups(c, mh, ah); assert(mh <= M); }
    // ② 노드 48 개
    std::mt19937 rng(77); auto randomIds = [&](size_t n, std::set<int> taken = {}) { std::vector<int> v; while (v.size() < n) { int id = (int)(rng() % SZ); if (taken.insert(id).second) v.push_back(id); } return v; };
    std::vector<int> ids = randomIds(48);
    Chord c; c.create(ids[0]);
    for (size_t i = 1; i < ids.size(); i++) { c.join(ids[i], ids[rng() % i]); if (i % 3 == 0) c.round(); }         // 수렴하기 전에 다음 노드가 들어오기도 한다
    int rounds = c.runUntilConverged(100); assert(rounds >= 0);
    int maxHops; double avgHops; verifyLookups(c, maxHops, avgHops); assert(maxHops <= M && avgHops < 4.5 && avgHops > 1.0);
    // ③ 이웃한 노드 둘이 동시에 죽는다 (후계자 목록 r = 3 이면 복구된다), 그다음 새 노드 join
    {   std::vector<int> alive = c.alive(); size_t at = rng() % alive.size(); int a = alive[at], b = alive[(at + 1) % alive.size()]; c.fail(a); c.fail(b);
        assert(c.runUntilConverged(100) >= 0); verifyLookups(c, maxHops, avgHops); assert(c.alive().size() == 46);
        std::set<int> taken(ids.begin(), ids.end()); std::vector<int> fresh = randomIds(6, taken); for (int id : fresh) { auto al = c.alive(); c.join(id, al[rng() % al.size()]); c.round(); }
        assert(c.runUntilConverged(100) >= 0); verifyLookups(c, maxHops, avgHops); assert(c.alive().size() == 52 && maxHops <= M);
        // 흩어진 노드 5 개가 죽고 3 개가 들어온다
        for (int k = 0; k < 5; k++) { auto al = c.alive(); c.fail(al[rng() % al.size()]); c.round(); }
        std::set<int> taken2(ids.begin(), ids.end()); for (int id : fresh) taken2.insert(id); taken2.insert(a); taken2.insert(b);
        for (int id : randomIds(3, taken2)) { auto al = c.alive(); c.join(id, al[rng() % al.size()]); c.round(); }
        assert(c.runUntilConverged(150) >= 0); verifyLookups(c, maxHops, avgHops); assert(c.alive().size() == 50); }
    // ④ 규모에 따른 평균 홉
    for (int N : {16, 64, 256}) {
        Chord big; std::vector<int> bi = randomIds((size_t)N); big.create(bi[0]); for (size_t i = 1; i < bi.size(); i++) { big.join(bi[i], bi[rng() % i]); if (i % 4 == 0) big.round(); }
        assert(big.runUntilConverged(200) >= 0); int mh; double ah; verifyLookups(big, mh, ah);
        double lg = std::log2((double)N); assert(mh <= M && ah > 0.25 * lg && ah < 0.75 * lg);
    }
    // ⑤ 키 이전: 새 노드 X 가 join 하면 옮겨 가는 키는 모두 X 로
    {   std::vector<int> before(SZ); for (int k = 0; k < SZ; k++) before[k] = c.truthSuccessor(k);
        std::set<int> taken; for (int n : c.alive()) taken.insert(n); int x = randomIds(1, taken)[0]; auto al = c.alive(); c.join(x, al[0]); assert(c.runUntilConverged(100) >= 0);
        int prev = c.predOf(x), moved = 0; for (int k = 0; k < SZ; k++) { int now = c.truthSuccessor(k); if (now != before[k]) { assert(now == x && inRange(k, prev, x, true)); ++moved; } else assert(!inRange(k, prev, x, true) || x == before[k]); }
        assert(moved > 0); }
    // 경계: 노드 하나, 둘
    {   Chord one; one.create(500); assert(one.runUntilConverged(5) >= 0); int h; assert(one.findSuccessor(500, 3, h) == 500 && one.findSuccessor(500, 500, h) == 500);
        Chord two; two.create(10); two.join(900, 10); assert(two.runUntilConverged(20) >= 0); assert(two.findSuccessor(10, 500, h) == 900 && two.findSuccessor(900, 901, h) == 10 && two.findSuccessor(900, 5, h) == 10); }
    std::cout << "Chord: all lookups correct after joins and failures, max hops = " << maxHops << " (m = " << M << "), converged in " << rounds << " rounds" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(log N) 홉
// Space Complexity: 노드당 O(log N) finger
```
## Kademlia()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// Kademlia: 거리 = XOR. 노드는 거리 구간(상위 일치 비트 수)별로 k-bucket 을 유지하고
// 조회는 목표에 더 가까운 노드를 반복해서 물어보며 좁혀 간다.
const int B = 16, K = 8;
struct Node {
    uint16_t id;
    std::vector<std::vector<uint16_t>> bucket;                  // bucket[i]: 거리가 [2^i, 2^(i+1)) 인 노드들
    explicit Node(uint16_t i) : id(i), bucket(B) {}
    void learn(uint16_t other) {
        if (other == id) return;
        int i = 31 - __builtin_clz((unsigned)(id ^ other));
        auto& b = bucket[i];
        if (std::find(b.begin(), b.end(), other) == b.end() && (int)b.size() < K) b.push_back(other);   // 오래된 노드 유지
    }
    std::vector<uint16_t> closest(uint16_t target, int n) const {
        std::vector<uint16_t> all;
        for (auto& b : bucket) all.insert(all.end(), b.begin(), b.end());
        std::sort(all.begin(), all.end(), [&](uint16_t a, uint16_t c) { return (a ^ target) < (c ^ target); });
        if ((int)all.size() > n) all.resize(n);
        return all;
    }
};

int main() {
    std::mt19937 rng(5);
    std::set<uint16_t> ids;
    while (ids.size() < 300) ids.insert(rng());
    std::vector<uint16_t> idv(ids.begin(), ids.end());
    std::vector<Node> net;
    for (auto id : idv) net.emplace_back(id);
    for (auto& n : net) { std::shuffle(idv.begin(), idv.end(), rng); for (auto o : idv) n.learn(o); }
    auto byId = [&](uint16_t id) -> Node& { for (auto& n : net) if (n.id == id) return n; throw 1; };

    int ok = 0, trials = 100;
    for (int t = 0; t < trials; t++) {
        uint16_t target = rng();
        uint16_t truth = *std::min_element(ids.begin(), ids.end(), [&](uint16_t a, uint16_t b) { return (a ^ target) < (b ^ target); });
        std::vector<uint16_t> shortlist = net[rng() % net.size()].closest(target, 3);
        std::set<uint16_t> asked;
        for (bool progress = true; progress;) {                  // 반복 조회: 새로 알게 된 더 가까운 노드에 다시 묻는다
            progress = false;
            for (auto c : std::vector<uint16_t>(shortlist)) {
                if (!asked.insert(c).second) continue;
                for (auto x : byId(c).closest(target, K)) shortlist.push_back(x);
                progress = true;
            }
            std::sort(shortlist.begin(), shortlist.end(), [&](uint16_t a, uint16_t b) { return (a ^ target) < (b ^ target); });
            shortlist.erase(std::unique(shortlist.begin(), shortlist.end()), shortlist.end());
            if ((int)shortlist.size() > K) shortlist.resize(K);
        }
        if (shortlist[0] == truth) ok++;
    }
    assert(ok >= 95);                                           // 거의 항상 진짜 최근접 노드에 수렴
    std::cout << "Kademlia lookup found the true closest node in " << ok << "/" << trials << std::endl;
    return 0;
}
// Time Complexity: 조회 O(log N) 라운드
// Space Complexity: 노드당 O(K log N)
```
## Consistent Hashing이 분산 시스템에서 중요한 이유
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// audit: closed-form (이동한 키의 비율을 모듈로 N/(N+1)·이상적 해싱 1/(N+1)·누적 Σ1/(N+1) 이라는 닫힌 식과 오차 한계 안에서 대조한다)
// 분산 캐시·DB 에서 키를 N 대 서버에 나누는 가장 쉬운 방법은 server = hash(key) mod N 이다. 문제는 N 이 바뀔 때다 — 서버를 한 대 늘리면 *거의 모든 키(N/(N+1))의 담당이 바뀌어* 캐시가 한꺼번에 비는 "캐시 폭풍" 이 일어나고 원본 DB 가 쓰러진다. 일관된 해싱(링)과 랑데부 해싱은 노드 추가·제거 시 *평균 1/(N+1) 의 키만* 옮긴다 — 이동하는 키는 새로 생긴/없어진 서버의 몫뿐이다.
// 이 항목은 세 방식의 차이를 숫자로 보인다: ① N → N + 1 에서 이동한 키 비율 (N = 2..30) ② 서버를 10 대에서 20 대로 한 대씩 늘릴 때 누적 이동 횟수 ③ 캐시 서버 10 대 + 새 서버 투입 직후의 적중률(캐시가 채워진 상태에서 새 서버를 넣을 때 기존 캐시에 계속 적중하는 키의 비율). 모두 결정적 시드로 계산하고 이론값(모듈로 N/(N+1), 이상적 해싱 1/(N+1))과 비교한다.
std::uint64_t mix(std::uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct Ring {                                                                                 // v 개의 가상 노드를 가진 일관된 해싱 링
    std::map<std::uint64_t, int> pts; int v;
    explicit Ring(int vnodes) : v(vnodes) {}
    void add(int node) { for (int r = 0; r < v; ++r) pts[mix(((std::uint64_t)node << 32) ^ (std::uint64_t)r ^ 0xfeedULL)] = node; }
    int lookup(std::uint64_t h) const { auto it = pts.lower_bound(h); if (it == pts.end()) it = pts.begin(); return it->second; }
};
int rendezvous(std::uint64_t key, int N) { int best = 0; std::uint64_t bs = 0; for (int n = 0; n < N; ++n) { std::uint64_t s = mix(key * 0x2545f4914f6cdd1dULL ^ mix((std::uint64_t)n + 1)); if (n == 0 || s > bs) { bs = s; best = n; } } return best; }

int main() {
    const int K = 60000;
    // ① N → N + 1 에서 이동한 키 비율
    double sumMod = 0, sumRing = 0, sumHrw = 0; int cases = 0;
    for (int N = 2; N <= 30; N += 4) {
        Ring ring(150); for (int n = 0; n < N; ++n) ring.add(n); std::vector<int> r0(K), h0(K); for (int i = 0; i < K; ++i) { r0[i] = ring.lookup(mix(i)); h0[i] = rendezvous(mix(i), N); }
        ring.add(N); int mod = 0, rg = 0, hr = 0;
        for (int i = 0; i < K; ++i) { mod += mix(i) % N != mix(i) % (N + 1); rg += ring.lookup(mix(i)) != r0[i]; hr += rendezvous(mix(i), N + 1) != h0[i]; }
        double fm = (double)mod / K, fr = (double)rg / K, fh = (double)hr / K, ideal = 1.0 / (N + 1);
        assert(std::abs(fm - (double)N / (N + 1)) < 0.03);                                           // 모듈로: N/(N+1)
        assert(std::abs(fr - ideal) < 0.45 * ideal + 0.01 && std::abs(fh - ideal) < 0.25 * ideal + 0.005);   // 링·랑데부: ≈ 1/(N+1) (링은 가상 노드가 유한해 변동이 더 크다)
        sumMod += fm; sumRing += fr; sumHrw += fh; ++cases;
    }
    // ② 서버를 10 대에서 20 대로 한 대씩 늘릴 때 (키 3 만 개) 누적 이동 횟수: 모듈로는 키당 거의 10 번 가까이 옮겨 다니고, 링은 키당 평균 Σ 1/(N+1) ≈ 0.69 번
    {   const int KK = 30000; std::vector<int> mod(KK), rg(KK); Ring ring(150); for (int n = 0; n < 10; ++n) ring.add(n); for (int i = 0; i < KK; ++i) { mod[i] = (int)(mix(i) % 10); rg[i] = ring.lookup(mix(i)); }
        long movesMod = 0, movesRing = 0; for (int N = 10; N < 20; ++N) { ring.add(N); for (int i = 0; i < KK; ++i) { int m2 = (int)(mix(i) % (N + 1)), r2 = ring.lookup(mix(i)); movesMod += m2 != mod[i]; movesRing += r2 != rg[i]; mod[i] = m2; rg[i] = r2; } }
        double perKeyMod = (double)movesMod / KK, perKeyRing = (double)movesRing / KK; double idealRing = 0; for (int N = 10; N < 20; ++N) idealRing += 1.0 / (N + 1);
        assert(perKeyMod > 6 && std::abs(perKeyRing - idealRing) < 0.3 * idealRing);
        std::cout << "ConsistentHashing(motivation): across N = 2..30 adding one server moved " << sumMod / cases << " of the keys with modulo hashing, " << sumRing / cases << " with a 150-virtual-node ring and " << sumHrw / cases << " with rendezvous hashing; growing from 10 to 20 servers one at a time remapped each key " << perKeyMod << " times with modulo but only " << perKeyRing << " times (ideal " << idealRing << ") with the ring" << std::endl; }
    // ③ 캐시 적중률: 서버 10 대에 키 10 만 개가 모두 캐시되어 있을 때 새 서버를 넣은 직후 같은 키를 다시 읽으면 → 기존 서버에서 계속 적중하는 비율
    {   const int KK = 100000; Ring ring(150); for (int n = 0; n < 10; ++n) ring.add(n); std::vector<int> owner0(KK), ownerRing(KK); for (int i = 0; i < KK; ++i) ownerRing[i] = ring.lookup(mix(i)); ring.add(10);
        long hitMod = 0, hitRing = 0; for (int i = 0; i < KK; ++i) { hitMod += mix(i) % 10 == mix(i) % 11; hitRing += ring.lookup(mix(i)) == ownerRing[i]; }
        double hm = (double)hitMod / KK, hr = (double)hitRing / KK; assert(hm < 0.15 && hr > 0.8);                                   // 모듈로: 적중률 ≈ 1/11 로 폭락, 링: ≈ 10/11
        std::cout << "ConsistentHashing(motivation): cache hit rate right after adding the 11th server was " << hm << " with modulo hashing and " << hr << " with the ring" << std::endl; }
    return 0;
}
// Time Complexity: 링 조회 O(log(N·V)), 랑데부 O(N), 모듈로 O(1)
// Space Complexity: O(N·V)
```
# Part 8. 암호학적 해시
## MD5()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// MD5 (RFC 1321). 충돌이 구성되어 보안 용도로는 쓸 수 없지만 체크섬으로는 여전히 쓰인다.
// 상수 K[i] = floor(2^32 * |sin(i+1)|) 는 코드로 직접 계산한다 ("nothing up my sleeve" 수)
// 스트리밍 객체(update/digest)로 만들어 입력을 어떻게 나눠 넣어도 같은 값이 나오게 하고, 호스트 바이트 순서에 기대지 않는다
// 검증: ① RFC 1321 의 시험 벡터 7 개 + 백만 개의 'a' + 상수 K 의 알려진 값  ② 패딩 경계 길이(55·56·57·63·64·65·119~129)와 길이 0~200 의 의사난수 버퍼 201 개의 다이제스트를 이어 붙여 다시 해시한 값(파이썬 hashlib 이 따로 계산한 값)
//        ③ 길이 0~130 의 입력을 *모든 한 곳 분할* 과 무작위 분할로 스트리밍한 결과 = 한 번에 계산한 결과, digest() 가 상태를 건드리지 않음  ④ 눈사태: 입력 한 비트를 뒤집으면 출력 128 비트 중 평균 64 개(60~68)가 바뀐다
//        ⑤ 유명한 충돌 쌍(Wang 2004, 128 바이트 두 개)이 같은 다이제스트를 내고, 뒤에 같은 접미사를 붙여도 계속 충돌 — 머클-담고르 구조의 성질
static inline uint32_t rotl(uint32_t x, int c) { return (x << c) | (x >> (32 - c)); }
struct Md5K { uint32_t K[64]; Md5K() { for (int i = 0; i < 64; i++) K[i] = (uint32_t)(std::fabs(std::sin((long double)(i + 1))) * 4294967296.0L); } };
const Md5K& md5k() { static const Md5K k; return k; }
class Md5 {
    uint32_t s[4]; uint64_t total = 0; uint8_t buf[64]; size_t blen = 0;
    void block(const uint8_t* p) {
        static const int S[64] = {7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22, 5,9,14,20,5,9,14,20,5,9,14,20,5,9,14,20,
                                  4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23, 6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21};
        uint32_t w[16]; for (int i = 0; i < 16; i++) w[i] = (uint32_t)p[4 * i] | (uint32_t)p[4 * i + 1] << 8 | (uint32_t)p[4 * i + 2] << 16 | (uint32_t)p[4 * i + 3] << 24;     // 리틀엔디언 (호스트와 무관)
        uint32_t A = s[0], B = s[1], C = s[2], D = s[3];
        for (int i = 0; i < 64; i++) {
            uint32_t F; int g;
            if (i < 16)      { F = (B & C) | (~B & D); g = i; }
            else if (i < 32) { F = (D & B) | (~D & C); g = (5 * i + 1) % 16; }
            else if (i < 48) { F = B ^ C ^ D;          g = (3 * i + 5) % 16; }
            else             { F = C ^ (B | ~D);       g = (7 * i) % 16; }
            F = F + A + md5k().K[i] + w[g];
            A = D; D = C; C = B; B = B + rotl(F, S[i]);
        }
        s[0] += A; s[1] += B; s[2] += C; s[3] += D;
    }
public:
    Md5() { s[0] = 0x67452301; s[1] = 0xefcdab89; s[2] = 0x98badcfe; s[3] = 0x10325476; }
    void update(const uint8_t* p, size_t n) { total += n; while (n) { size_t take = std::min(n, 64 - blen); std::memcpy(buf + blen, p, take); blen += take; p += take; n -= take; if (blen == 64) { block(buf); blen = 0; } } }
    void update(const std::string& m) { update((const uint8_t*)m.data(), m.size()); }
    std::string digest() const {                                       // 상태를 건드리지 않는다 (복사본에서 패딩)
        Md5 t = *this; uint64_t bits = total * 8; uint8_t pad = 0x80, z = 0; t.update(&pad, 1); while (t.blen != 56) t.update(&z, 1);
        for (int i = 0; i < 8; i++) { uint8_t b = (uint8_t)(bits >> (8 * i)); t.update(&b, 1); }                // 길이: 리틀엔디언
        std::string out; for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) out.push_back((char)((t.s[i] >> (8 * j)) & 0xff));
        return out;
    }
};
std::string hex(const std::string& d) { static const char* h = "0123456789abcdef"; std::string r; for (unsigned char c : d) { r += h[c >> 4]; r += h[c & 15]; } return r; }
std::string md5raw(const std::string& msg) { Md5 m; m.update(msg); return m.digest(); }
std::string md5(const std::string& msg) { return hex(md5raw(msg)); }
std::string fromHex(const std::string& h) { std::string r; for (size_t i = 0; i + 1 < h.size(); i += 2) r.push_back((char)std::stoi(h.substr(i, 2), nullptr, 16)); return r; }
int popcount(const std::string& a, const std::string& b) { int c = 0; for (size_t i = 0; i < a.size(); i++) for (int x = (unsigned char)a[i] ^ (unsigned char)b[i]; x; x >>= 1) c += x & 1; return c; }

int main() {
    assert(md5("") == "d41d8cd98f00b204e9800998ecf8427e");
    assert(md5("abc") == "900150983cd24fb0d6963f7d28e17f72");
    assert(md5("The quick brown fox jumps over the lazy dog") == "9e107d9d372bb6826bd81d3542a419d6");
    // ① RFC 1321 시험 벡터
    assert(md5("a") == "0cc175b9c0f1b6a831c399e269772661" && md5("message digest") == "f96b697d7cb7938d525a2f31aaf161d0" && md5("abcdefghijklmnopqrstuvwxyz") == "c3fcd3d76192e4007dfb496cca67e13b");
    assert(md5("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") == "d174ab98d277d9f5a5611c2c9f419d9f");
    assert(md5("12345678901234567890123456789012345678901234567890123456789012345678901234567890") == "57edf4a22be3c955ac49da2e2107b67a");
    { Md5 m; std::string chunk(1000, 'a'); for (int i = 0; i < 1000; i++) m.update(chunk); assert(hex(m.digest()) == "7707d6ae4e027c70eea2a935c2296f21"); }          // 백만 개의 'a'
    assert(md5k().K[0] == 0xd76aa478u && md5k().K[1] == 0xe8c7b756u && md5k().K[63] == 0xeb86d391u);
    // ② 패딩 경계와 길이별 체크섬
    const struct { int n; const char* d; } edge[] = {{55, "ef1772b6dff9a122358552954ad0df65"}, {56, "3b0c8ac703f828b04c6c197006d17218"}, {57, "652b906d60af96844ebd21b674f35e93"}, {63, "b06521f39153d618550606be297466d5"},
        {64, "014842d480b571495a4a0363793f7367"}, {65, "c743a45e0d2e6a95cb859adae0248435"}, {119, "8a7bd0732ed6a28ce75f6dabc90e1613"}, {120, "5f61c0ccad4cac44c75ff505e1f1e537"}, {121, "f6acfca2d47c87f2b14ca038234d3614"},
        {127, "020406e1d05cdc2aa287641f7ae2cc39"}, {128, "e510683b3f5ffe4093d021808bc6ff70"}, {129, "b325dc1c6f5e7a2b7cf465b9feab7948"}};
    for (auto& e : edge) assert(md5(std::string(e.n, 'a')) == e.d);
    std::string buf; { uint32_t st = 12345; for (int i = 0; i < 400; i++) { st = (st * 1103515245u + 12345u) & 0x7fffffffu; buf.push_back((char)((st >> 16) & 0xff)); } }
    { std::string acc; for (int n = 0; n <= 200; n++) acc += md5raw(buf.substr(0, n)); assert(md5(acc) == "e3e6f62d034898a05892e045381af1d7"); }
    // ③ 스트리밍
    std::mt19937 rng(4);
    for (int n = 0; n <= 130; n++) {
        std::string m = buf.substr(0, n), want = md5raw(m);
        for (int cut = 0; cut <= n; cut++) { Md5 s; s.update(m.substr(0, cut)); std::string mid = s.digest(); assert(mid == md5raw(m.substr(0, cut))); s.update(m.substr(cut)); assert(s.digest() == want); }     // digest() 뒤에도 계속 update 가능
        Md5 r; size_t pos = 0; while (pos < m.size()) { size_t step = 1 + rng() % 70; if (pos + step > m.size()) step = m.size() - pos; r.update(m.substr(pos, step)); pos += step; } assert(r.digest() == want);
    }
    // ④ 눈사태
    double sum = 0; const int N = 3000;
    for (int i = 0; i < N; i++) { std::string m(40, 'x'); for (char& c : m) c = (char)rng(); std::string f = m; f[rng() % 40] ^= (char)(1 << (rng() % 8)); sum += popcount(md5raw(m), md5raw(f)); }
    assert(sum / N > 60 && sum / N < 68);
    // ⑤ 알려진 충돌 쌍
    std::string m1 = fromHex("d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f8955ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5bd8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70");
    std::string m2 = fromHex("d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f8955ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5bd8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70");
    assert(m1.size() == 128 && m2.size() == 128 && m1 != m2 && md5(m1) == "79054025255fb1a26e4bc422aef54eb4" && md5(m1) == md5(m2));
    for (int i = 0; i < 20; i++) { std::string suffix(rng() % 100, 'x'); for (char& c : suffix) c = (char)rng(); assert(md5(m1 + suffix) == md5(m2 + suffix)); }          // 충돌은 접미사를 붙여도 유지된다
    std::cout << "md5(abc) = " << md5("abc") << "; known collision pair: " << md5(m1) << " (avalanche " << sum / N << " of 128 bits)" << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)  (스트리밍 상태 64 바이트 버퍼)
```
## SHA256()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// SHA-256 (FIPS 180-4). 초기값은 처음 8개 소수의 제곱근, 라운드 상수는 처음 64개 소수의 세제곱근의 소수부 상위 32비트
// 스트리밍 객체(update/digest)로 만들어 입력을 어떻게 나눠 넣어도 같은 값이 나오게 하고, digest() 는 상태를 건드리지 않으므로 중간 해시를 보며 계속 이어 넣을 수 있다
// 검증: ① NIST 시험 벡터("", "abc", 448 비트·896 비트 메시지, 백만 개의 'a'), 상수 H[0]·K[0]·K[63] 의 알려진 값  ② 패딩 경계 길이와 길이 0~200 의 의사난수 버퍼 다이제스트 체크섬(파이썬 hashlib 이 따로 계산)
//        ③ 길이 0~130 을 모든 한 곳 분할과 무작위 분할로 스트리밍, 중간 digest() 가 접두사의 해시와 같음  ④ 눈사태: 입력 한 비트 반전 시 출력 256 비트 중 평균 128 개(124~132)가 바뀐다
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
struct Consts {
    uint32_t K[64], H0[8];
    Consts() {
        std::vector<uint32_t> primes;
        for (uint32_t p = 2; primes.size() < 64; p++) { bool ok = true; for (uint32_t q : primes) if (p % q == 0) { ok = false; break; } if (ok) primes.push_back(p); }
        for (int i = 0; i < 64; i++) { long double c = cbrtl((long double)primes[i]); K[i] = (uint32_t)((c - floorl(c)) * 4294967296.0L); }
        for (int i = 0; i < 8; i++)  { long double s = sqrtl((long double)primes[i]); H0[i] = (uint32_t)((s - floorl(s)) * 4294967296.0L); }
    }
};
const Consts& consts() { static const Consts c; return c; }
class Sha256 {
    uint32_t H[8]; uint64_t total = 0; uint8_t buf[64]; size_t blen = 0;
    void block(const uint8_t* p) {
        uint32_t w[64], K[64]; std::memcpy(K, consts().K, sizeof K);
        for (int i = 0; i < 16; i++) w[i] = (uint32_t)p[4 * i] << 24 | (uint32_t)p[4 * i + 1] << 16 | (uint32_t)p[4 * i + 2] << 8 | p[4 * i + 3];
        for (int i = 16; i < 64; i++) {
            uint32_t s0 = rotr(w[i-15], 7) ^ rotr(w[i-15], 18) ^ (w[i-15] >> 3);
            uint32_t s1 = rotr(w[i-2], 17) ^ rotr(w[i-2], 19) ^ (w[i-2] >> 10);
            w[i] = w[i-16] + s0 + w[i-7] + s1;
        }
        uint32_t a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
        for (int i = 0; i < 64; i++) {
            uint32_t S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25), ch = (e & f) ^ (~e & g);
            uint32_t t1 = h + S1 + ch + K[i] + w[i];
            uint32_t S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22), maj = (a & b) ^ (a & c) ^ (b & c);
            uint32_t t2 = S0 + maj;
            h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
        }
        H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
public:
    Sha256() { std::memcpy(H, consts().H0, sizeof H); }
    void update(const uint8_t* p, size_t n) { total += n; while (n) { size_t take = std::min(n, 64 - blen); std::memcpy(buf + blen, p, take); blen += take; p += take; n -= take; if (blen == 64) { block(buf); blen = 0; } } }
    void update(const std::string& m) { update((const uint8_t*)m.data(), m.size()); }
    std::string digest() const {                                       // 상태를 건드리지 않는다
        Sha256 t = *this; uint64_t bits = total * 8; uint8_t pad = 0x80, z = 0; t.update(&pad, 1); while (t.blen != 56) t.update(&z, 1);
        for (int i = 7; i >= 0; i--) { uint8_t b = (uint8_t)(bits >> (8 * i)); t.update(&b, 1); }                // 길이: 빅엔디언
        std::string out; for (int i = 0; i < 8; i++) for (int j = 3; j >= 0; j--) out.push_back((char)((t.H[i] >> (8 * j)) & 0xff));
        return out;
    }
    static uint32_t K0() { return consts().K[0]; } static uint32_t K63() { return consts().K[63]; } static uint32_t H00() { return consts().H0[0]; }
};
std::string hex(const std::string& d) { static const char* h = "0123456789abcdef"; std::string r; for (unsigned char c : d) { r += h[c >> 4]; r += h[c & 15]; } return r; }
std::string sha256raw(const std::string& msg) { Sha256 s; s.update(msg); return s.digest(); }
std::string sha256(const std::string& msg) { return hex(sha256raw(msg)); }
int popcount(const std::string& a, const std::string& b) { int c = 0; for (size_t i = 0; i < a.size(); i++) for (int x = (unsigned char)a[i] ^ (unsigned char)b[i]; x; x >>= 1) c += x & 1; return c; }

int main() {
    assert(sha256("") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    assert(sha256("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    assert(sha256("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq") ==
           "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");     // 두 블록짜리 표준 시험값
    // ① NIST 시험 벡터와 상수
    assert(sha256("abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu") == "cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1");
    { Sha256 s; std::string chunk(1000, 'a'); for (int i = 0; i < 1000; i++) s.update(chunk); assert(hex(s.digest()) == "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"); }       // 백만 개의 'a'
    assert(Sha256::H00() == 0x6a09e667u && Sha256::K0() == 0x428a2f98u && Sha256::K63() == 0xc67178f2u);
    assert(sha256("a") == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb" && sha256("message digest") == "f7846f55cf23e14eebeab5b4e1550cad5b509e3348fbc4efa3a1413d393cb650");
    // ② 패딩 경계와 길이별 체크섬
    const struct { int n; const char* d; } edge[] = {{55, "9f4390f8d30c2dd92ec9f095b65e2b9ae9b0a925a5258e241c9f1e910f734318"}, {56, "b35439a4ac6f0948b6d6f9e3c6af0f5f590ce20f1bde7090ef7970686ec6738a"}, {57, "f13b2d724659eb3bf47f2dd6af1accc87b81f09f59f2b75e5c0bed6589dfe8c6"},
        {63, "7d3e74a05d7db15bce4ad9ec0658ea98e3f06eeecf16b4c6fff2da457ddc2f34"}, {64, "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb"}, {65, "635361c48bb9eab14198e76ea8ab7f1a41685d6ad62aa9146d301d4f17eb0ae0"},
        {119, "31eba51c313a5c08226adf18d4a359cfdfd8d2e816b13f4af952f7ea6584dcfb"}, {120, "2f3d335432c70b580af0e8e1b3674a7c020d683aa5f73aaaedfdc55af904c21c"}, {121, "e9615320128cc7a3d6078e9af05603188e5ccbf0d07d8b735d3df5e8e0c1281f"},
        {127, "c57e9278af78fa3cab38667bef4ce29d783787a2f731d4e12200270f0c32320a"}, {128, "6836cf13bac400e9105071cd6af47084dfacad4e5e302c94bfed24e013afb73e"}, {129, "c12cb024a2e5551cca0e08fce8f1c5e314555cc3fef6329ee994a3db752166ae"}};
    for (auto& e : edge) assert(sha256(std::string(e.n, 'a')) == e.d);
    std::string buf; { uint32_t st = 12345; for (int i = 0; i < 400; i++) { st = (st * 1103515245u + 12345u) & 0x7fffffffu; buf.push_back((char)((st >> 16) & 0xff)); } }
    { std::string acc; for (int n = 0; n <= 200; n++) acc += sha256raw(buf.substr(0, n)); assert(sha256(acc) == "ce348b5da30cafbd9806a31cc8b17744740e500089117f16d0f689bbd3966941"); }
    // ③ 스트리밍
    std::mt19937 rng(6);
    for (int n = 0; n <= 130; n++) {
        std::string m = buf.substr(0, n), want = sha256raw(m);
        for (int cut = 0; cut <= n; cut++) { Sha256 s; s.update(m.substr(0, cut)); assert(s.digest() == sha256raw(m.substr(0, cut))); s.update(m.substr(cut)); assert(s.digest() == want); }
        Sha256 r; size_t pos = 0; while (pos < m.size()) { size_t step = 1 + rng() % 70; if (pos + step > m.size()) step = m.size() - pos; r.update(m.substr(pos, step)); pos += step; } assert(r.digest() == want);
    }
    // ④ 눈사태
    double sum = 0; const int N = 2000;
    for (int i = 0; i < N; i++) { std::string m(40, 'x'); for (char& c : m) c = (char)rng(); std::string f = m; f[rng() % 40] ^= (char)(1 << (rng() % 8)); sum += popcount(sha256raw(m), sha256raw(f)); }
    assert(sum / N > 124 && sum / N < 132);
    std::cout << "sha256(abc) = " << sha256("abc") << " (avalanche " << sum / N << " of 256 bits)" << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)  (스트리밍 상태 64 바이트 버퍼)
```
## HMAC()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// HMAC(K, m) = H((K' ⊕ opad) || H((K' ⊕ ipad) || m)).  단순히 H(K || m) 을 쓰면 길이 확장 공격에 취약하다 (MerkleDamgard 항목 참고)
// K' 는 키가 블록(64바이트)보다 길면 먼저 해시하고, 짧으면 0 으로 채운 것 — 그래서 "k" 와 "k\0" 는 같은 HMAC 키다
// 검증: ① RFC 4231 의 시험 벡터(1·2·3·4·6·7번)와 위키백과 값, 키 길이 63·64·65 (해시 후 사용하는 경계), 키 0~130 바이트 × 메시지 격자의 체크섬(파이썬 hmac 이 따로 계산)
//        ② 영 채움 동치와 키·메시지 변조가 값을 바꿈  ③ 실제 SHA-256 의 *길이 확장 공격*: H(비밀 || m) 은 비밀 없이 m || 패딩 || 확장 의 태그를 위조할 수 있고(300 번 모두 성공), HMAC 은 같은 방법이 한 번도 통하지 않는다
//        ④ 상수 시간 비교: 불일치 위치와 무관하게 같은 횟수만큼 훑는다
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
struct Consts {
    uint32_t K[64], H0[8];
    Consts() {
        std::vector<uint32_t> primes;
        for (uint32_t p = 2; primes.size() < 64; p++) { bool ok = true; for (uint32_t q : primes) if (p % q == 0) { ok = false; break; } if (ok) primes.push_back(p); }
        for (int i = 0; i < 64; i++) { long double c = cbrtl((long double)primes[i]); K[i] = (uint32_t)((c - floorl(c)) * 4294967296.0L); }
        for (int i = 0; i < 8; i++)  { long double s = sqrtl((long double)primes[i]); H0[i] = (uint32_t)((s - floorl(s)) * 4294967296.0L); }
    }
};
const Consts& consts() { static const Consts c; return c; }
class Sha256 {
    uint32_t H[8]; uint64_t total = 0; uint8_t buf[64]; size_t blen = 0;
    void block(const uint8_t* p) {
        uint32_t w[64], K[64]; std::memcpy(K, consts().K, sizeof K);
        for (int i = 0; i < 16; i++) w[i] = (uint32_t)p[4 * i] << 24 | (uint32_t)p[4 * i + 1] << 16 | (uint32_t)p[4 * i + 2] << 8 | p[4 * i + 3];
        for (int i = 16; i < 64; i++) { uint32_t s0 = rotr(w[i-15], 7) ^ rotr(w[i-15], 18) ^ (w[i-15] >> 3), s1 = rotr(w[i-2], 17) ^ rotr(w[i-2], 19) ^ (w[i-2] >> 10); w[i] = w[i-16] + s0 + w[i-7] + s1; }
        uint32_t a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
        for (int i = 0; i < 64; i++) {
            uint32_t t1 = h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i];
            uint32_t t2 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
            h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
        }
        H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
public:
    Sha256() { std::memcpy(H, consts().H0, sizeof H); }
    void update(const uint8_t* p, size_t n) { total += n; while (n) { size_t take = std::min(n, 64 - blen); std::memcpy(buf + blen, p, take); blen += take; p += take; n -= take; if (blen == 64) { block(buf); blen = 0; } } }
    void update(const std::string& m) { update((const uint8_t*)m.data(), m.size()); }
    std::string digest() const {
        Sha256 t = *this; uint64_t bits = total * 8; uint8_t pad = 0x80, z = 0; t.update(&pad, 1); while (t.blen != 56) t.update(&z, 1);
        for (int i = 7; i >= 0; i--) { uint8_t b = (uint8_t)(bits >> (8 * i)); t.update(&b, 1); }
        std::string out; for (int i = 0; i < 8; i++) for (int j = 3; j >= 0; j--) out.push_back((char)((t.H[i] >> (8 * j)) & 0xff));
        return out;
    }
    void setState(const std::string& digestBytes, uint64_t processedBytes) {                  // 길이 확장 공격: 다이제스트가 곧 내부 상태이므로 거기서 이어간다 (processedBytes 는 64 의 배수)
        for (int i = 0; i < 8; i++) H[i] = (uint32_t)(uint8_t)digestBytes[4 * i] << 24 | (uint32_t)(uint8_t)digestBytes[4 * i + 1] << 16 | (uint32_t)(uint8_t)digestBytes[4 * i + 2] << 8 | (uint8_t)digestBytes[4 * i + 3];
        total = processedBytes; blen = 0;
    }
    static std::string mdPadding(uint64_t len) { std::string p(1, (char)0x80); while ((len + p.size()) % 64 != 56) p += '\0'; for (int i = 7; i >= 0; i--) p += (char)((len * 8 >> (8 * i)) & 0xff); return p; }
};
std::string hex(const std::string& d) { static const char* h = "0123456789abcdef"; std::string r; for (unsigned char c : d) { r += h[c >> 4]; r += h[c & 15]; } return r; }
std::string sha256raw(const std::string& msg) { Sha256 s; s.update(msg); return s.digest(); }

std::string hmacSha256(std::string key, const std::string& msg) {
    const size_t block = 64;
    if (key.size() > block) key = sha256raw(key);
    key.resize(block, '\0');
    std::string ipad(block, 0), opad(block, 0);
    for (size_t i = 0; i < block; i++) { ipad[i] = key[i] ^ 0x36; opad[i] = key[i] ^ 0x5c; }
    return sha256raw(opad + sha256raw(ipad + msg));
}
bool constantTimeEq(const std::string& a, const std::string& b, long* steps = nullptr) {      // 불일치가 어디서 나든 끝까지 훑는다 (타이밍으로 값을 추측하지 못하게)
    size_t n = std::max(a.size(), b.size()); unsigned diff = (unsigned)(a.size() ^ b.size()); long s = 0;
    for (size_t i = 0; i < n; i++) { unsigned char x = i < a.size() ? (unsigned char)a[i] : 0, y = i < b.size() ? (unsigned char)b[i] : 0; diff |= (unsigned)(x ^ y); ++s; }
    if (steps) *steps = s; return diff == 0;
}
std::string extendSha256(const std::string& tag, uint64_t knownLen, const std::string& ext) {     // 위조: 비밀을 모르고 태그와 (비밀+m) 의 길이만 안다
    std::string pad = Sha256::mdPadding(knownLen); Sha256 s; s.setState(tag, knownLen + pad.size()); s.update(ext); return s.digest();
}

int main() {
    assert(hex(hmacSha256("key", "The quick brown fox jumps over the lazy dog")) ==
           "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8");     // 위키피디아의 표준 시험값
    assert(hmacSha256("key", "a") != hmacSha256("kex", "a"));
    // ① RFC 4231 (SHA-256)
    assert(hex(hmacSha256(std::string(20, '\x0b'), "Hi There")) == "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7");
    assert(hex(hmacSha256("Jefe", "what do ya want for nothing?")) == "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843");
    assert(hex(hmacSha256(std::string(20, '\xaa'), std::string(50, '\xdd'))) == "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe");
    { std::string k; for (int i = 1; i <= 25; i++) k.push_back((char)i); assert(hex(hmacSha256(k, std::string(50, '\xcd'))) == "82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b"); }
    assert(hex(hmacSha256(std::string(131, '\xaa'), "Test Using Larger Than Block-Size Key - Hash Key First")) == "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54");
    assert(hex(hmacSha256(std::string(131, '\xaa'), "This is a test using a larger than block-size key and a larger than block-size data. The key needs to be hashed before being used by the HMAC algorithm.")) ==
           "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2");
    const struct { int kl; const char* d; } kb[] = {{63, "10e769af2d2919c3e45444c20ff5663e1549007f2a19d1c7d78cebdc5c15ff55"}, {64, "78ca3825abdda5c36e64afabc0273c51f909fcb87462a20551d9655d0f6eb292"}, {65, "6a73f99effa292beb8ac7c8eac60b638241e0120373ebbf746c7177bba2b9de2"}};
    for (auto& e : kb) { std::string k; for (int i = 0; i < e.kl; i++) k.push_back((char)((i * 7 + 1) & 0xff)); assert(hex(hmacSha256(k, "msg")) == e.d); }       // 64 바이트 이하는 영 채움, 65 바이트부터는 해시 후 사용
    std::string buf; { uint32_t st = 12345; for (int i = 0; i < 400; i++) { st = (st * 1103515245u + 12345u) & 0x7fffffffu; buf.push_back((char)((st >> 16) & 0xff)); } }
    { std::string acc; for (int kl = 0; kl <= 130; kl++) acc += hmacSha256(buf.substr(0, kl), buf.substr(200, (kl * 7) % 150)); assert(hex(sha256raw(acc)) == "bc6cb51ac5ec2a96ee87ee7a371bb35029ca69d332c4461ad244eed6a864d82f"); }
    // ② 영 채움 동치와 변조
    assert(hmacSha256("k", "x") == hmacSha256(std::string("k\0", 2), "x") && hmacSha256("k", "x") == hmacSha256(std::string("k") + std::string(63, '\0'), "x") && hmacSha256("k", "x") != hmacSha256("K", "x") && hmacSha256("k", "x") != hmacSha256("k", "y"));
    assert(hmacSha256("", "") != hmacSha256("", std::string(1, '\0')));
    // ③ 길이 확장 공격
    std::mt19937 rng(9); int naiveForged = 0, hmacForged = 0;
    for (int it = 0; it < 300; ++it) {
        std::string secret(1 + rng() % 40, 'x'), m(rng() % 60, 'x'), ext(1 + rng() % 30, 'x'); for (char& c : secret) c = (char)rng(); for (char& c : m) c = (char)rng(); for (char& c : ext) c = (char)rng();
        uint64_t L = secret.size() + m.size(); std::string forgedMsg = m + Sha256::mdPadding(L) + ext;
        std::string naiveTag = sha256raw(secret + m), forged = extendSha256(naiveTag, L, ext);
        naiveForged += sha256raw(secret + forgedMsg) == forged;                                  // H(비밀 || m) : 서버가 같은 값을 계산한다 -> 위조 성공
        std::string macTag = hmacSha256(secret, m), forged2 = extendSha256(macTag, L, ext);
        hmacForged += hmacSha256(secret, forgedMsg) == forged2;                                  // HMAC : 통하지 않는다
        assert(forgedMsg != m);
    }
    assert(naiveForged == 300 && hmacForged == 0);
    // ④ 상수 시간 비교
    std::string t = hmacSha256("key", "m"); std::string early = t, late = t; early[0] ^= 1; late[31] ^= 1; long s0, s1, s2, s3;
    assert(constantTimeEq(t, t, &s0) && !constantTimeEq(t, early, &s1) && !constantTimeEq(t, late, &s2) && !constantTimeEq(t, t.substr(0, 31), &s3));
    assert(s0 == 32 && s1 == 32 && s2 == 32 && s3 == 32 && constantTimeEq("", "") && !constantTimeEq("a", ""));
    std::cout << "hmac = " << hex(hmacSha256("key", "The quick brown fox jumps over the lazy dog")) << "; length extension forged " << naiveForged << "/300 naive tags and " << hmacForged << "/300 HMAC tags" << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(len)
```
## MerkleDamgard()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

// 머클-담고르 구성: IV 에서 시작해 메시지를 블록 단위로 압축함수에 먹이고, 마지막에 길이를 포함한 패딩을 붙인다.
// 최종 해시가 곧 내부 상태이므로, 해시값과 길이만 알면 이어서 계속 압축할 수 있다 -> 길이 확장 공격.
// 또 한 단계에서 충돌 두 개를 찾으면 그 단계들을 이어 붙여 2^k 개 메시지가 같은 해시를 갖는다(Joux 의 다중 충돌) — 상태가 작을수록(여기선 32 비트) 눈앞에서 볼 수 있다
// (여기서는 구조를 보이려고 32비트 장난감 압축함수를 쓴다. 실제 해시의 압축함수는 SHA-256 항목 참고)
// 검증: ① 길이 확장 위조(원래 예)  ② 무작위 500 쌍(비밀 길이 0~20, 메시지 길이 0~30)에서 위조가 모두 성공하고, 내부 해시를 한 번 더 감싼 MAC H(비밀 || H(비밀 || m)) 에는 한 번도 통하지 않음
//        ③ 이 압축함수는 고정된 상태에서 블록에 대해 *전단사* 라서 한 블록 메시지는 충돌할 수 없다(무작위 2^18 개 블록에서 충돌 없음) — 충돌은 두 블록부터, 생일 공격으로 단계마다 약 2^16 번의 시도로 찾는다
//        ④ 6 단계를 이어 붙인 64 개의 서로 다른 메시지가 모두 같은 해시  ⑤ 패딩은 길이를 포함하므로 짧은 메시지들에서 "메시지 -> 패딩된 열" 이 단사이고 패딩 뒤 길이가 4 의 배수
static inline uint32_t rotl(uint32_t x, int r) { return (x << r) | (x >> (32 - r)); }
const uint32_t IV = 0x6a09e667u;
uint32_t compress(uint32_t h, uint32_t block) {
    h ^= block; h *= 0x9e3779b1u; h = rotl(h, 13); h += 0x7f4a7c15u; h ^= h >> 15; h *= 0x85ebca6bu;
    return h;
}
// 패딩: 0x80, 0 채움(4의 배수까지), 전체 길이(4바이트)
std::string padding(uint64_t totalLen) {
    std::string p(1, (char)0x80);
    while ((totalLen + p.size()) % 4 != 0) p += '\0';
    for (int i = 0; i < 4; i++) p += (char)((totalLen >> (8 * i)) & 0xff);
    return p;
}
// state 에서 이어서 해시한다. already = 이미 처리된 바이트 수 (패딩 길이 필드에 반영)
uint32_t hashFrom(uint32_t state, const std::string& msg, uint64_t already) {
    std::string data = msg + padding(already + msg.size());
    for (size_t i = 0; i < data.size(); i += 4) {
        uint32_t w = (uint8_t)data[i] | (uint8_t)data[i+1] << 8 | (uint8_t)data[i+2] << 16 | (uint32_t)(uint8_t)data[i+3] << 24;
        state = compress(state, w);
    }
    return state;
}
uint32_t H(const std::string& msg) { return hashFrom(IV, msg, 0); }
std::string bytesOf(uint32_t v) { std::string s; for (int i = 0; i < 4; i++) s += (char)((v >> (8 * i)) & 0xff); return s; }
uint32_t mac2(const std::string& secret, const std::string& m) { return H(secret + bytesOf(H(secret + m))); }          // 안쪽 해시를 한 번 더 감싼 MAC
struct Pair2 { uint32_t a, b; };
bool stageCollision(uint32_t s, std::mt19937& rng, Pair2& x, Pair2& y, uint32_t& next, long& tries) {                    // 상태 s 에서 두 블록 메시지의 생일 충돌
    std::unordered_map<uint32_t, Pair2> seen;
    for (int i = 0; i < 2000000; i++) {
        Pair2 p{(uint32_t)rng(), (uint32_t)rng()}; uint32_t st = compress(compress(s, p.a), p.b); ++tries;
        auto it = seen.find(st); if (it != seen.end() && (it->second.a != p.a || it->second.b != p.b)) { x = it->second; y = p; next = st; return true; }
        seen[st] = p;
    }
    return false;
}
std::string blocks(const Pair2& p) { return bytesOf(p.a) + bytesOf(p.b); }

int main() {
    std::string secret = "s3cr3t!", m = "amount=100&to=alice", ext = "&amount=9999&to=mallory";
    uint32_t tag = H(secret + m);                                 // 서버가 만든 MAC = H(secret || m)
    // 공격자: secret 은 모르고 tag, m, secret 의 길이만 안다
    uint64_t L = secret.size() + m.size();
    std::string glue = padding(L);                                // 서버가 내부적으로 붙였던 패딩
    uint32_t forged = hashFrom(tag, ext, L + glue.size());        // tag 를 내부 상태로 삼아 ext 를 이어서 해시
    std::string forgedMsg = m + glue + ext;
    assert(H(secret + forgedMsg) == forged);                      // 서버가 계산한 값과 일치 -> 위조 성공
    assert(forgedMsg != m);
    // ② 무작위 위조
    std::mt19937 rng(77); int naive = 0, wrapped = 0;
    for (int it = 0; it < 500; ++it) {
        std::string sec(rng() % 21, 'x'), msg(rng() % 31, 'x'), e(1 + rng() % 20, 'x'); for (char& c : sec) c = (char)rng(); for (char& c : msg) c = (char)rng(); for (char& c : e) c = (char)rng();
        uint64_t len = sec.size() + msg.size(); std::string g = padding(len), fm = msg + g + e;
        naive += H(sec + fm) == hashFrom(H(sec + msg), e, len + g.size());
        wrapped += mac2(sec, fm) == hashFrom(mac2(sec, msg), e, len + g.size());
    }
    assert(naive == 500 && wrapped == 0);
    // ③ 압축함수는 블록에 대해 전단사
    for (uint32_t s : {IV, 0u, 0xdeadbeefu}) { std::unordered_map<uint32_t, uint32_t> out; for (int i = 0; i < (1 << 18); i++) { uint32_t b = (uint32_t)rng(); uint32_t r = compress(s, b); auto it = out.find(r); assert(it == out.end() || it->second == b); out[r] = b; } }
    // ④ 다중 충돌
    const int K = 6; uint32_t state = IV; std::vector<std::pair<std::string, std::string>> choices; long tries = 0;
    for (int stage = 0; stage < K; stage++) { Pair2 x, y; uint32_t next; assert(stageCollision(state, rng, x, y, next, tries)); assert(blocks(x) != blocks(y) && compress(compress(state, x.a), x.b) == compress(compress(state, y.a), y.b)); choices.push_back({blocks(x), blocks(y)}); state = next; }
    std::set<std::string> messages; std::set<uint32_t> hashes;
    for (int mask = 0; mask < (1 << K); mask++) { std::string msg; for (int i = 0; i < K; i++) msg += (mask >> i & 1) ? choices[i].second : choices[i].first; messages.insert(msg); hashes.insert(H(msg)); }
    assert(messages.size() == 64 && hashes.size() == 1 && tries > 6 * 5000 && tries < 6 * 400000);                  // 서로 다른 64 개 메시지, 해시는 하나
    // ⑤ 패딩
    std::vector<std::string> small{std::string()}; const char alpha[] = {'\x00', '\x01', '\x80'};
    for (size_t i = 0; i < small.size(); ++i) if (small[i].size() < 3) for (char c : alpha) small.push_back(small[i] + c);
    std::set<std::string> padded; for (auto& s : small) { std::string d = s + padding(s.size()); assert(d.size() % 4 == 0 && (uint8_t)d[s.size()] == 0x80); padded.insert(d); }
    assert(small.size() == 40 && padded.size() == 40);
    std::cout << "length-extension forgery accepted: tag=" << std::hex << forged << std::dec << "; 500/500 forgeries worked on H(secret||m), " << wrapped << "/500 on the wrapped MAC; " << (1 << K) << " messages share one hash after " << tries << " birthday tries" << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(len)
```
## 암호학적 해시와 일반 해시의 차이
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

// 일반 해시(해시 테이블용)와 암호학적 해시의 차이를 실제 코드로 가른다.
//  ① 암호학적 해시 SHA-256 을 스트리밍으로 직접 구현하고 표준 시험값(NIST·RFC 4231·패딩 경계 55/56/63/64/65 바이트·100 만 개의 'a')과 대조한다.
//  ② 일반 해시의 finalizer fmix32 는 전단사라 해시값에서 입력이 한 번에 복원된다. SHA-256 은 잘라 써도 충돌은 2^(n/2), 원상은 2^n 번의 시도가 든다.
//  ③ 눈사태 행렬(입력 비트 i 를 뒤집을 때 출력 비트 j 가 뒤집힐 확률): SHA-256 은 모든 칸이 1/2 근처이지만 FNV-1a 에는 정확히 0 인 칸이 있다.
//  ④ 길이 확장 공격: H(key‖m) 을 MAC 으로 쓰면 key 없이 위조되지만 HMAC 은 막는다.
typedef std::uint8_t u8; typedef std::uint32_t u32; typedef std::uint64_t u64;
static inline u32 rotr(u32 x, int n) { return (x >> n) | (x << (32 - n)); }

struct Sha256 {
    struct Consts {                                                  // 초기값 = 소수 제곱근의 소수부, 라운드 상수 = 소수 세제곱근의 소수부 (상위 32 비트)
        u32 K[64], IV[8];
        Consts() { std::vector<u32> pr; for (u32 p = 2; pr.size() < 64; ++p) { bool ok = true; for (u32 q : pr) if (p % q == 0) { ok = false; break; } if (ok) pr.push_back(p); }
            for (int i = 0; i < 64; ++i) { long double c = cbrtl((long double)pr[i]); K[i] = (u32)((c - floorl(c)) * 4294967296.0L); }
            for (int i = 0; i < 8; ++i) { long double s = sqrtl((long double)pr[i]); IV[i] = (u32)((s - floorl(s)) * 4294967296.0L); } }
    };
    static const Consts& C() { static const Consts c; return c; }
    u32 H[8]; u8 buf[64]; std::size_t blen; u64 total;
    Sha256() : blen(0), total(0) { std::memcpy(H, C().IV, sizeof H); }
    Sha256(const u8* digest, u64 processed) : blen(0), total(processed) {            // 다이제스트 = 내부 상태: 여기서부터 이어서 해시할 수 있다 (길이 확장)
        for (int i = 0; i < 8; ++i) H[i] = (u32)digest[4 * i] << 24 | (u32)digest[4 * i + 1] << 16 | (u32)digest[4 * i + 2] << 8 | digest[4 * i + 3]; }
    void block(const u8* p) {
        u32 w[64]; for (int i = 0; i < 16; ++i) w[i] = (u32)p[4 * i] << 24 | (u32)p[4 * i + 1] << 16 | (u32)p[4 * i + 2] << 8 | p[4 * i + 3];
        for (int i = 16; i < 64; ++i) { u32 s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3), s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10); w[i] = w[i - 16] + s0 + w[i - 7] + s1; }
        u32 a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7]; const u32* K = C().K;
        for (int i = 0; i < 64; ++i) {
            u32 t1 = h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i], t2 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
            h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2; }
        H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
    void update(const void* data, std::size_t n) {
        const u8* p = (const u8*)data; total += n;
        while (n) { std::size_t t = std::min(n, 64 - blen); std::memcpy(buf + blen, p, t); blen += t; p += t; n -= t; if (blen == 64) { block(buf); blen = 0; } }
    }
    std::string finish() {
        u64 bits = total * 8; buf[blen++] = 0x80;
        if (blen > 56) { std::memset(buf + blen, 0, 64 - blen); block(buf); blen = 0; }
        std::memset(buf + blen, 0, 56 - blen); for (int i = 0; i < 8; ++i) buf[56 + i] = (u8)(bits >> (56 - 8 * i)); block(buf);
        std::string out; for (int i = 0; i < 8; ++i) for (int j = 3; j >= 0; --j) out.push_back((char)(H[i] >> (8 * j))); return out;
    }
};
std::string sha256(const std::string& m) { Sha256 s; s.update(m.data(), m.size()); return s.finish(); }
std::string hex(const std::string& s) { static const char* d = "0123456789abcdef"; std::string r; for (unsigned char c : s) { r += d[c >> 4]; r += d[c & 15]; } return r; }
std::string hmac(std::string key, const std::string& msg) {
    if (key.size() > 64) key = sha256(key);
    key.resize(64, '\0'); std::string ip(64, 0), op(64, 0); for (int i = 0; i < 64; ++i) { ip[i] = key[i] ^ 0x36; op[i] = key[i] ^ 0x5c; }
    return sha256(op + sha256(ip + msg));
}
std::string padFor(u64 len) { std::string p(1, (char)0x80); while ((len + p.size()) % 64 != 56) p += '\0'; u64 bits = len * 8; for (int i = 7; i >= 0; --i) p += (char)(bits >> (8 * i)); return p; }

u32 fmix32(u32 h) { h ^= h >> 16; h *= 0x85ebca6bu; h ^= h >> 13; h *= 0xc2b2ae35u; h ^= h >> 16; return h; }          // MurmurHash3 의 마지막 섞기
u32 modInverse(u32 a) { u32 x = a; for (int i = 0; i < 5; ++i) x *= 2 - a * x; return x; }                           // 홀수 a 의 2^32 역원 (뉴턴 반복)
u32 unxorshift(u32 y, int s) { u32 x = y; for (int i = 0; i < 32 / s + 1; ++i) x = y ^ (x >> s); return x; }
u32 unfmix32(u32 h) { h = unxorshift(h, 16); h *= modInverse(0xc2b2ae35u); h = unxorshift(h, 13); h *= modInverse(0x85ebca6bu); return unxorshift(h, 16); }
u32 truncBits(const std::string& d, int bits) { u32 v = (u32)(u8)d[0] << 24 | (u32)(u8)d[1] << 16 | (u32)(u8)d[2] << 8 | (u8)d[3]; return v >> (32 - bits); }

std::vector<u8> shaBytes(const std::string& s) { std::string d = sha256(s); return std::vector<u8>(d.begin(), d.end()); }
std::vector<u8> fnvBytes(const std::string& s) { u32 h = 2166136261u; for (u8 c : s) { h ^= c; h *= 16777619u; } return {(u8)(h >> 24), (u8)(h >> 16), (u8)(h >> 8), (u8)h}; }
std::vector<u8> fmixBytes(const std::string& s) { u32 x; std::memcpy(&x, s.data(), 4); u32 h = fmix32(x); return {(u8)(h >> 24), (u8)(h >> 16), (u8)(h >> 8), (u8)h}; }
struct Av { double lo, hi; int zero; };
Av avalanche(std::vector<u8> (*f)(const std::string&), int trials, std::mt19937_64& rng) {           // 4 바이트 입력의 32 개 비트를 하나씩 뒤집는다
    int outBits = (int)f(std::string(4, 'a')).size() * 8; std::vector<int> cnt(32 * outBits, 0);
    for (int t = 0; t < trials; ++t) {
        std::string x(4, 0); u32 r = (u32)rng(); std::memcpy(&x[0], &r, 4); std::vector<u8> h0 = f(x);
        for (int b = 0; b < 32; ++b) { std::string y = x; y[b / 8] ^= (char)(1 << (b % 8)); std::vector<u8> h1 = f(y); for (int o = 0; o < outBits; ++o) cnt[b * outBits + o] += ((h0[o / 8] ^ h1[o / 8]) >> (o % 8)) & 1; }
    }
    Av a{1, 0, 0}; for (int c : cnt) { double p = (double)c / trials; a.lo = std::min(a.lo, p); a.hi = std::max(a.hi, p); a.zero += c == 0; } return a;
}
u64 collisionTries(int bits, u64 salt) {                                                                // 잘린 다이제스트에서 처음 겹칠 때까지의 해시 횟수
    std::unordered_map<u32, u64> seen; std::string pre = std::to_string(salt) + ":";
    for (u64 i = 0;; ++i) { auto r = seen.emplace(truncBits(sha256(pre + std::to_string(i)), bits), i);
        if (!r.second) { assert(sha256(pre + std::to_string(i)) != sha256(pre + std::to_string(r.first->second))); return i + 1; } }   // 잘린 값만 같고 전체 다이제스트는 다르다
}
u64 preimageTries(int bits, u64 t) {                                                                    // 주어진 잘린 값을 맞히는 입력을 찾을 때까지의 해시 횟수
    u32 target = truncBits(sha256("target:" + std::to_string(t)), bits);
    for (u64 i = 1;; ++i) if (truncBits(sha256("try:" + std::to_string(i)), bits) == target) return i;
}

int main() {
    // ① 표준 시험값 + 패딩 경계 + 100 만 개의 'a'
    assert(hex(sha256("")) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    assert(hex(sha256("abc")) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    assert(hex(sha256("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq")) == "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
    const struct { int n; const char* d; } edge[] = {
        {55, "9f4390f8d30c2dd92ec9f095b65e2b9ae9b0a925a5258e241c9f1e910f734318"}, {56, "b35439a4ac6f0948b6d6f9e3c6af0f5f590ce20f1bde7090ef7970686ec6738a"},
        {63, "7d3e74a05d7db15bce4ad9ec0658ea98e3f06eeecf16b4c6fff2da457ddc2f34"}, {64, "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb"},
        {65, "635361c48bb9eab14198e76ea8ab7f1a41685d6ad62aa9146d301d4f17eb0ae0"}, {119, "31eba51c313a5c08226adf18d4a359cfdfd8d2e816b13f4af952f7ea6584dcfb"},
        {120, "2f3d335432c70b580af0e8e1b3674a7c020d683aa5f73aaaedfdc55af904c21c"}, {1000000, "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"}};
    for (auto& e : edge) assert(hex(sha256(std::string(e.n, 'a'))) == e.d);
    std::mt19937_64 rng(2024);
    for (int it = 0; it < 300; ++it) {                                                                  // 임의 조각으로 나눠 먹여도 한 번에 먹인 것과 같다
        std::string m(rng() % 300, 'x'); for (char& c : m) c = (char)rng(); Sha256 s; std::size_t pos = 0;
        while (pos < m.size()) { std::size_t t = std::min<std::size_t>(1 + rng() % 70, m.size() - pos); s.update(m.data() + pos, t); pos += t; }
        assert(s.finish() == sha256(m));
    }
    // RFC 4231 의 HMAC-SHA-256 시험값 (키가 블록보다 긴 경우 포함)
    assert(hex(hmac(std::string(20, '\x0b'), "Hi There")) == "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7");
    assert(hex(hmac("Jefe", "what do ya want for nothing?")) == "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843");
    assert(hex(hmac(std::string(131, '\xaa'), "Test Using Larger Than Block-Size Key - Hash Key First")) == "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54");
    // ② 일반 해시의 finalizer 는 전단사라 원상이 즉시 복원된다
    for (int it = 0; it < 1000000; ++it) { u32 x = (u32)rng(); assert(unfmix32(fmix32(x)) == x && fmix32(unfmix32(x)) == x); }
    // 암호학적 해시를 n 비트로 자르면: 충돌 ≈ 1.25·2^(n/2) 번, 원상 ≈ 2^n 번의 시도 (생일 역설)
    double col[3], pre[3]; const int cb[3] = {16, 20, 24}, pb[3] = {8, 10, 12};
    for (int k = 0; k < 3; ++k) {
        double sc = 0, sp = 0; for (int r = 0; r < 16; ++r) sc += (double)collisionTries(cb[k], r); for (int r = 0; r < 60; ++r) sp += (double)preimageTries(pb[k], r);
        col[k] = sc / 16; pre[k] = sp / 60;
        double ec = 1.2533 * std::pow(2.0, cb[k] / 2.0), ep = std::pow(2.0, pb[k]);
        assert(col[k] > 0.6 * ec && col[k] < 1.6 * ec && pre[k] > 0.6 * ep && pre[k] < 1.6 * ep);
    }
    assert(col[1] / col[0] > 2.5 && col[1] / col[0] < 6 && col[2] / col[1] > 2.5 && col[2] / col[1] < 6);       // 비트 4 개 늘 때마다 충돌 비용 ×4 (= 2^(4/2))
    assert(pre[1] / pre[0] > 2.5 && pre[2] / pre[1] > 2.5);                                             // 비트 2 개 늘 때마다 원상 비용 ×4
    // ③ 눈사태 행렬
    Av sha = avalanche(shaBytes, 3000, rng), fnv = avalanche(fnvBytes, 3000, rng), fmx = avalanche(fmixBytes, 20000, rng);
    assert(sha.zero == 0 && sha.lo > 0.43 && sha.hi < 0.57);                                            // 256 × 32 칸 모두 1/2 근처
    assert(fmx.zero == 0 && fmx.lo > 0.4 && fmx.hi < 0.6);                                              // fmix32 도 눈사태는 좋다 (다만 역산이 쉽다)
    assert(fnv.zero >= 28 && fnv.lo == 0.0);                                                            // FNV-1a: 출력 0 번 비트는 입력 각 바이트의 0 번 비트의 XOR → 나머지 28 개 입력 비트는 영향 0
    // ④ 길이 확장 공격: key 를 모른 채 H(key‖m) 의 태그에서 이어 붙여 위조
    for (int it = 0; it < 200; ++it) {
        std::string key(1 + rng() % 100, 'k'), m(rng() % 80, 'm'), ext(1 + rng() % 60, 'e'); for (char& c : key) c = (char)rng(); for (char& c : m) c = (char)rng(); for (char& c : ext) c = (char)rng();
        std::string tag = sha256(key + m);                                                              // 서버가 발급한 태그
        std::string glue = padFor(key.size() + m.size());                                               // 공격자는 |key|, m, tag, ext 만 안다
        Sha256 s((const u8*)tag.data(), key.size() + m.size() + glue.size()); s.update(ext.data(), ext.size());
        std::string forged = s.finish(), fm = m + glue + ext;
        assert(sha256(key + fm) == forged && fm != m);                                                  // 서버의 검증을 통과한다
        assert(hmac(key, fm) != forged && hmac(key, m) != tag && hmac(key, m) != hmac(key, fm));        // HMAC 은 같은 수법이 통하지 않는다
    }
    std::cout << "crypto vs general hash: SHA-256 matched all standard vectors (incl. 10^6 'a'); fmix32 inverted on 10^6 inputs; truncated SHA-256 needed " << col[0] << "/" << col[1] << "/" << col[2] << " hashes for a 16/20/24-bit collision but " << pre[0] << "/" << pre[1] << "/" << pre[2] << " for an 8/10/12-bit preimage; avalanche cells SHA-256 [" << sha.lo << "," << sha.hi << "], fmix32 [" << fmx.lo << "," << fmx.hi << "], FNV-1a [" << fnv.lo << ",...] with " << fnv.zero << " dead cells; length-extension forgery worked 200/200 against H(key||m) and 0/200 against HMAC" << std::endl;
    return 0;
}
// Time Complexity: SHA-256 O(n), 충돌 탐색 O(2^(b/2)), 원상 탐색 O(2^b) (b = 자른 비트 수)
// Space Complexity: O(2^(b/2)) (충돌 탐색의 표)
```
# Part 9. DB 해시
## HashIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 해시 인덱스 = "열 값 → 행 번호(RID)". DB 인덱스는 디스크 페이지 단위로 읽으므로 비용은 비교 횟수가 아니라 읽은 페이지 수다.
// 해시 인덱스: 키를 해시한 버킷의 페이지 체인만 읽는다 → 등치(=) 조회는 페이지 약 1 개, 그러나 범위(BETWEEN)·정렬에는 쓸 수 없어 전체 페이지를 읽는다.
// 정렬 인덱스(B+트리의 리프 층을 흉내 낸 정렬 페이지): 등치 1 페이지, 범위는 겹치는 페이지만 읽는다.
const int PAGE = 8;                                                    // 페이지 한 장에 들어가는 항목 수
static inline std::uint64_t mix(std::uint64_t z) { z += 0x9e3779b97f4a7c15ULL; z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }

template <class K> class HashIndex {
    struct Page { std::vector<std::pair<K, int>> e; int next = -1; };
    std::vector<Page> pages; std::vector<int> freePages; std::size_t buckets, n = 0;
    std::size_t bucketOf(const K& k) const { return mix(std::hash<K>()(k)) % buckets; }
    int newPage() { if (!freePages.empty()) { int p = freePages.back(); freePages.pop_back(); return p; } pages.emplace_back(); return (int)pages.size() - 1; }
public:
    mutable long pageReads = 0;                                        // 읽은 페이지 수 (비용 모델)
    explicit HashIndex(std::size_t b = 4) : pages(b), buckets(b) {}
    std::size_t size() const { return n; }
    std::size_t bucketCount() const { return buckets; }
    std::size_t pageCount() const { return pages.size() - freePages.size(); }
    std::size_t chainPages(const K& k) const { std::size_t c = 0; for (int p = (int)bucketOf(k); p != -1; p = pages[p].next) ++c; return c; }
    void insert(const K& k, int rid) {
        if (n + 1 > buckets * PAGE * 3 / 4) grow();                    // 평균 적재율이 0.75 페이지를 넘으면 버킷 수를 두 배로
        int p = (int)bucketOf(k), last = p;
        for (; p != -1; last = p, p = pages[p].next) if ((int)pages[p].e.size() < PAGE) { pages[p].e.emplace_back(k, rid); ++n; return; }
        int q = newPage(); pages[last].next = q; pages[q].e.emplace_back(k, rid); ++n;       // 오버플로 페이지
    }
    std::vector<int> equal(const K& k) const {
        std::vector<int> out; for (int p = (int)bucketOf(k); p != -1; p = pages[p].next) { ++pageReads; for (auto& x : pages[p].e) if (x.first == k) out.push_back(x.second); }
        return out;
    }
    bool erase(const K& k, int rid) {                                  // 체인의 마지막 항목으로 구멍을 메우고, 비어 버린 오버플로 페이지는 반환
        int prev = -1;
        for (int p = (int)bucketOf(k); p != -1; prev = p, p = pages[p].next) for (auto& x : pages[p].e) if (x.first == k && x.second == rid) {
            int lp = p, lprev = prev; while (pages[lp].next != -1) { lprev = lp; lp = pages[lp].next; }
            x = pages[lp].e.back(); pages[lp].e.pop_back(); --n;
            if (pages[lp].e.empty() && lprev != -1) { pages[lprev].next = -1; freePages.push_back(lp); }
            return true;
        }
        return false;
    }
    std::vector<std::pair<K, int>> range(const K& lo, const K& hi) const {   // 해시는 순서를 모른다: 모든 페이지를 읽는다
        std::vector<std::pair<K, int>> out;
        for (std::size_t b = 0; b < buckets; ++b) for (int p = (int)b; p != -1; p = pages[p].next) { ++pageReads; for (auto& x : pages[p].e) if (!(x.first < lo) && x.first < hi) out.push_back(x); }
        return out;
    }
    void grow() { std::vector<std::pair<K, int>> all; for (std::size_t b = 0; b < buckets; ++b) for (int p = (int)b; p != -1; p = pages[p].next) for (auto& x : pages[p].e) all.push_back(x);
        pages.assign(buckets * 2, Page()); freePages.clear(); buckets *= 2; n = 0; for (auto& x : all) insert(x.first, x.second); }
    bool check() const {                                               // 불변식: 체인의 마지막을 뺀 페이지는 가득 차 있고, 마지막 오버플로 페이지는 비어 있지 않다
        std::size_t cnt = 0, used = 0;
        for (std::size_t b = 0; b < buckets; ++b) for (int p = (int)b; p != -1; p = pages[p].next) {
            ++used; cnt += pages[p].e.size(); if ((int)pages[p].e.size() > PAGE) return false;
            if (pages[p].next != -1 && (int)pages[p].e.size() != PAGE) return false;
            if (pages[p].next == -1 && p != (int)b && pages[p].e.empty()) return false;
            for (auto& x : pages[p].e) if (bucketOf(x.first) != b) return false;
        }
        return cnt == n && used == pageCount();
    }
};

template <class K> class OrderedIndex {                                // 정렬된 리프 페이지 (B+트리의 위 층은 메모리에 있다고 본다)
    std::vector<std::pair<K, int>> e;
    std::size_t lowerIdx(const K& k) const { return std::lower_bound(e.begin(), e.end(), k, [](const std::pair<K, int>& x, const K& v) { return x.first < v; }) - e.begin(); }
    std::size_t upperIdx(const K& k) const { return std::upper_bound(e.begin(), e.end(), k, [](const K& v, const std::pair<K, int>& x) { return v < x.first; }) - e.begin(); }
    std::vector<std::pair<K, int>> slice(std::size_t i, std::size_t j) const { pageReads += i < j ? (j - 1) / PAGE - i / PAGE + 1 : 1; return std::vector<std::pair<K, int>>(e.begin() + i, e.begin() + j); }
public:
    mutable long pageReads = 0;
    void build(std::vector<std::pair<K, int>> v) { std::sort(v.begin(), v.end()); e.swap(v); }
    std::size_t pageCount() const { return (e.size() + PAGE - 1) / PAGE; }
    std::vector<std::pair<K, int>> range(const K& lo, const K& hi) const { return slice(lowerIdx(lo), std::max(lowerIdx(lo), lowerIdx(hi))); }   // lo <= key < hi
    std::vector<int> equal(const K& k) const { std::vector<int> r; for (auto& x : slice(lowerIdx(k), upperIdx(k))) r.push_back(x.second); return r; }
};

int main() {
    // ① 원래 예: city 열
    {   std::vector<std::string> city = {"Seoul", "Busan", "Seoul", "Daegu", "Seoul"}; HashIndex<std::string> h; OrderedIndex<std::string> o; std::vector<std::pair<std::string, int>> rows;
        for (std::size_t i = 0; i < city.size(); ++i) { h.insert(city[i], (int)i); rows.emplace_back(city[i], (int)i); } o.build(rows);
        std::vector<int> r = h.equal("Seoul"); std::sort(r.begin(), r.end()); assert((r == std::vector<int>{0, 2, 4}) && h.equal("Jeju").empty());
        assert((o.equal("Seoul") == std::vector<int>{0, 2, 4}) && o.equal("Jeju").empty());
        std::vector<std::pair<std::string, int>> a = h.range("B", "E"), b = o.range("B", "E"); std::sort(a.begin(), a.end());
        assert(a == b && a.size() == 2);                                // Busan, Daegu
    }
    // ② 무작위 작업열 vs std::multimap: 중복 키가 많은 좁은 도메인 (체인·삭제·재해시를 모두 거친다)
    std::mt19937 rng(11);
    {   HashIndex<int> h; std::multimap<int, int> ref; std::vector<std::pair<int, int>> live; int nextRid = 0;
        for (int op = 0; op < 60000; ++op) {
            int t = rng() % 10;
            if (t < 5) { int k = rng() % 300; h.insert(k, nextRid); ref.emplace(k, nextRid); live.emplace_back(k, nextRid); ++nextRid; }
            else if (t < 8 && !live.empty()) { std::size_t i = rng() % live.size(); auto kv = live[i]; live[i] = live.back(); live.pop_back(); bool ok = h.erase(kv.first, kv.second); assert(ok); (void)ok; for (auto it = ref.find(kv.first); ; ++it) if (it->second == kv.second) { ref.erase(it); break; } }
            else if (t == 8) { bool ok = h.erase((int)(rng() % 300), -1); assert(!ok); (void)ok; }                                     // 없는 항목의 삭제는 false
            else { int k = rng() % 320; std::vector<int> got = h.equal(k), want; auto er = ref.equal_range(k); for (auto it = er.first; it != er.second; ++it) want.push_back(it->second); std::sort(got.begin(), got.end()); std::sort(want.begin(), want.end()); assert(got == want); }
            if (op % 1000 == 0) {
                assert(h.size() == ref.size() && h.check());
                OrderedIndex<int> o; o.build(live); int lo = rng() % 300, hi = lo + rng() % 80; std::vector<std::pair<int, int>> a = h.range(lo, hi), b = o.range(lo, hi), c; for (auto it = ref.lower_bound(lo); it != ref.lower_bound(hi); ++it) c.push_back(*it);
                std::sort(a.begin(), a.end()); std::sort(c.begin(), c.end()); assert(a == b && a == c);
            }
        }
    }
    // ③ 비용 모델: 고유 키 10 만 개 — 등치 조회는 두 인덱스 모두 페이지 약 1 장, 범위 조회는 해시가 전 페이지를 읽는다
    {   const int N = 100000; std::vector<int> keys(N); for (int i = 0; i < N; ++i) keys[i] = i * 7 + 3; std::shuffle(keys.begin(), keys.end(), rng);
        HashIndex<int> h; OrderedIndex<int> o; std::vector<std::pair<int, int>> rows; for (int i = 0; i < N; ++i) { h.insert(keys[i], i); rows.emplace_back(keys[i], i); } o.build(rows); assert(h.check());
        for (int q = 0; q < 20000; ++q) { int i = rng() % N; assert(h.equal(keys[i]) == std::vector<int>{i} && o.equal(keys[i]) == std::vector<int>{i}); }
        double hashAvg = h.pageReads / 20000.0, ordAvg = o.pageReads / 20000.0; assert(ordAvg == 1.0 && hashAvg >= 1.0 && hashAvg < 1.6);
        h.pageReads = o.pageReads = 0; std::vector<std::pair<int, int>> a = h.range(70000, 70280), b = o.range(70000, 70280); std::sort(a.begin(), a.end()); assert(a == b && a.size() == 40);   // 키 간격 7 → 40 개
        assert(o.pageReads <= 40 / PAGE + 2 && h.pageReads == (long)h.pageCount() && h.pageReads > 100 * o.pageReads);
        std::cout << "HashIndex: " << N << " unique keys, equality reads " << hashAvg << " pages (hash) vs " << ordAvg << " (ordered); a 40-row range read " << h.pageReads << " pages (hash) vs " << o.pageReads << " (ordered)" << std::endl;
    }
    // ④ 치우친 분포: 한 키에 5000 행 — 그 키의 체인은 길어지고, 같은 버킷의 다른 키도 그 체인을 읽는다
    {   HashIndex<int> h; for (int i = 0; i < 5000; ++i) h.insert(-1, i); for (int k = 0; k < 20000; ++k) h.insert(k, 5000 + k);
        std::size_t hot = h.chainPages(-1); assert(hot >= 5000 / PAGE && h.equal(-1).size() == 5000);
        int victim = -2; for (int k = 0; k < 2000000 && victim == -2; ++k) if (k != -1 && h.chainPages(k) == hot) victim = k;      // 같은 버킷으로 해시되는 다른 키
        assert(victim != -2); long before = h.pageReads; h.equal(victim); assert(h.pageReads - before == (long)hot);               // 엉뚱한 키의 조회도 그 긴 체인을 전부 읽는다
        long total = 0; for (int k = 0; k < 20000; ++k) total += (long)h.chainPages(k);
        assert((double)total / 20000 < 1.6 && h.check());                                                                          // 하지만 나머지 키 대부분은 영향이 없다
    }
    // ⑤ 큰 입력: 행 100 만 개 (고유 키 10 만 개 × 10 회) 를 넣고 표본 조회를 정렬 배열과 대조한 뒤 전부 지운다
    {   const int N = 1000000; HashIndex<int> h; std::vector<std::pair<int, int>> rows(N); for (int i = 0; i < N; ++i) { rows[i] = {(int)(mix(i) % 100000), i}; h.insert(rows[i].first, i); }
        assert(h.size() == (std::size_t)N && h.check()); std::vector<std::pair<int, int>> sorted = rows; std::sort(sorted.begin(), sorted.end());
        for (int q = 0; q < 10000; ++q) { int k = rng() % 100000; std::vector<int> got = h.equal(k), want; auto lo = std::lower_bound(sorted.begin(), sorted.end(), std::make_pair(k, -1)); for (; lo != sorted.end() && lo->first == k; ++lo) want.push_back(lo->second); std::sort(got.begin(), got.end()); assert(got == want && want.size() >= 1); }
        std::shuffle(rows.begin(), rows.end(), rng); for (auto& r : rows) { bool ok = h.erase(r.first, r.second); assert(ok); (void)ok; }
        assert(h.size() == 0 && h.pageCount() == h.bucketCount() && h.check());          // 오버플로 페이지는 모두 반환된다
    }
    return 0;
}
// Time Complexity: 등치 조회 기대 O(1) 페이지, 범위 조회 O(전체 페이지) (정렬 인덱스는 O(log n + 결과/페이지))
// Space Complexity: O(n / PAGE) 페이지
```
## HashJoin()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <tuple>
#include <vector>

// 해시 조인: (1) 작은 쪽으로 해시 테이블을 만들고(build) (2) 큰 쪽을 훑으며 탐색(probe). 중첩 루프 O(n·m) → O(n+m).
// build 쪽이 메모리(M 튜플)에 안 들어가면 Grace 해시 조인: 두 테이블을 같은 해시로 F 조각에 나눠 디스크에 내려쓰고(spill) 같은 번호끼리 조인한다.
// 한 키가 M 보다 많이 중복되면 해시로 쪼갤 수 없으므로 블록 중첩 루프로 후퇴한다. 조인 종류: 내부(INNER)·왼쪽 외부(LEFT)·세미(SEMI)·안티(ANTI).
typedef std::uint64_t u64;
struct Tup { int key, val; };
typedef std::tuple<int, int, int> Out;                                  // (key, 왼쪽 val, 오른쪽 val), 짝이 없으면 오른쪽 = NONE
const int NONE = -1;
enum Kind { INNER, LEFT, SEMI, ANTI };
struct Stats { long probes = 0, spilled = 0, blockLoops = 0; std::size_t maxTable = 0; int maxDepth = 0; };
static inline u64 mix(u64 z) { z += 0x9e3779b97f4a7c15ULL; z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }

struct BuildTable {                                                     // 체인 방식 해시 테이블: head[버킷] → 튜플 번호 → nxt[튜플 번호]
    const std::vector<Tup>& s; std::vector<int> head, nxt; std::size_t mask; u64 seed;
    BuildTable(const std::vector<Tup>& S, u64 sd) : s(S), nxt(S.size(), -1), seed(sd) {
        std::size_t b = 1; while (b < 2 * S.size()) b <<= 1; head.assign(b, -1); mask = b - 1;
        for (std::size_t i = 0; i < S.size(); ++i) { std::size_t h = mix((u64)S[i].key ^ seed) & mask; nxt[i] = head[h]; head[h] = (int)i; }
    }
    int first(int key) const { return head[mix((u64)key ^ seed) & mask]; }
};
// B 로 테이블을 만들고 P 를 훑는다. 키가 같은 짝마다 hit(p, b), p 하나의 탐색이 끝날 때마다 done(p, 짝이 있었는가) 를 부른다.
template <class Hit, class Done> void buildProbe(const std::vector<Tup>& B, const std::vector<Tup>& P, u64 seed, Stats& st, Hit hit, Done done) {
    BuildTable t(B, seed); st.maxTable = std::max(st.maxTable, B.size());
    for (const Tup& p : P) { bool any = false; for (int i = t.first(p.key); i != -1; i = t.nxt[i]) { ++st.probes; if (B[i].key == p.key) { any = true; hit(p, B[i]); } } done(p, any); }
}
void inMemory(const std::vector<Tup>& R, const std::vector<Tup>& S, Kind k, u64 seed, Stats& st, std::vector<Out>& out) {
    if (k == INNER) {                                                   // 내부 조인은 작은 쪽을 build 로 쓴다 (출력의 열 순서는 (R, S) 그대로)
        if (S.size() <= R.size()) buildProbe(S, R, seed, st, [&](const Tup& r, const Tup& s) { out.emplace_back(r.key, r.val, s.val); }, [](const Tup&, bool) {});
        else buildProbe(R, S, seed, st, [&](const Tup& s, const Tup& r) { out.emplace_back(r.key, r.val, s.val); }, [](const Tup&, bool) {});
        return;
    }
    buildProbe(S, R, seed, st, [&](const Tup& r, const Tup& s) { if (k == LEFT) out.emplace_back(r.key, r.val, s.val); },
               [&](const Tup& r, bool any) { if ((k == LEFT && !any) || (k == SEMI && any) || (k == ANTI && !any)) out.emplace_back(r.key, r.val, NONE); });
}
void blockJoin(const std::vector<Tup>& R, const std::vector<Tup>& S, Kind k, std::size_t M, u64 seed, Stats& st, std::vector<Out>& out) {
    ++st.blockLoops; std::vector<char> matched(R.size(), 0);            // S 를 M 개씩 끊어 테이블을 만들고 R 전체를 매번 훑는다
    for (std::size_t lo = 0; lo < S.size(); lo += M) {
        std::vector<Tup> blk(S.begin() + lo, S.begin() + std::min(S.size(), lo + M)); BuildTable t(blk, seed); st.maxTable = std::max(st.maxTable, blk.size());
        for (std::size_t i = 0; i < R.size(); ++i) for (int j = t.first(R[i].key); j != -1; j = t.nxt[j]) { ++st.probes; if (blk[j].key == R[i].key) { matched[i] = 1; if (k == INNER || k == LEFT) out.emplace_back(R[i].key, R[i].val, blk[j].val); } }
    }
    for (std::size_t i = 0; i < R.size(); ++i) if ((k == LEFT && !matched[i]) || (k == SEMI && matched[i]) || (k == ANTI && !matched[i])) out.emplace_back(R[i].key, R[i].val, NONE);
}
void grace(const std::vector<Tup>& R, const std::vector<Tup>& S, Kind k, std::size_t M, int depth, Stats& st, std::vector<Out>& out) {
    st.maxDepth = std::max(st.maxDepth, depth); if (R.empty()) return;
    u64 seed = 0x9e3779b97f4a7c15ULL * (u64)(depth + 1);                // 단계마다 다른 해시 → 조각이 다시 쪼개진다
    if ((k == INNER ? std::min(R.size(), S.size()) : S.size()) <= M) { inMemory(R, S, k, seed, st, out); return; }
    const int F = 8; std::vector<std::vector<Tup>> pr(F), ps(F);
    for (const Tup& t : R) pr[(mix((u64)t.key ^ seed) >> 40) % F].push_back(t);
    for (const Tup& t : S) ps[(mix((u64)t.key ^ seed) >> 40) % F].push_back(t);
    st.spilled += (long)(R.size() + S.size());                          // 조각을 디스크에 내려쓴 튜플 수
    for (int p = 0; p < F; ++p) {
        if ((pr[p].size() + ps[p].size()) * 4 >= 3 * (R.size() + S.size())) blockJoin(pr[p], ps[p], k, M, seed, st, out);   // 거의 안 쪼개졌다: 한 키가 대부분 → 해시로는 못 나눈다
        else grace(pr[p], ps[p], k, M, depth + 1, st, out);
    }
}
std::vector<Out> hashJoin(const std::vector<Tup>& R, const std::vector<Tup>& S, Kind k, std::size_t M, Stats& st) { std::vector<Out> out; grace(R, S, k, std::max<std::size_t>(M, 1), 0, st, out); return out; }
std::vector<Out> nestedLoop(const std::vector<Tup>& R, const std::vector<Tup>& S, Kind k) {
    std::vector<Out> out;
    for (const Tup& r : R) { int m = 0; for (const Tup& s : S) if (r.key == s.key) { ++m; if (k == INNER || k == LEFT) out.emplace_back(r.key, r.val, s.val); }
        if ((k == LEFT && !m) || (k == SEMI && m) || (k == ANTI && !m)) out.emplace_back(r.key, r.val, NONE); }
    return out;
}
std::vector<Out> sorted(std::vector<Out> v) { std::sort(v.begin(), v.end()); return v; }

int main() {
    // ① 원래 예: id=3 은 2×2 중 매칭
    {   std::vector<Tup> R = {{1, 10}, {2, 20}, {3, 30}, {3, 31}}, S = {{3, 90}, {1, 70}, {4, 50}, {3, 85}}; Stats st;
        const std::size_t want[4] = {5, 6, 3, 1};                       // INNER, LEFT, SEMI, ANTI
        for (int k = 0; k < 4; ++k) { std::vector<Out> a = sorted(hashJoin(R, S, (Kind)k, 1000, st)), b = sorted(nestedLoop(R, S, (Kind)k)); assert(a == b && a.size() == want[k]); }
    }
    // ② 무작위 작은 입력 × 키 도메인(중복 많음) × 메모리 한도 × 조인 종류 vs 중첩 루프
    std::mt19937 rng(5);
    for (int it = 0; it < 4000; ++it) {
        int dom[4] = {1, 2, 6, 60}; int d = dom[rng() % 4]; std::vector<Tup> R(rng() % 41), S(rng() % 41);
        for (std::size_t i = 0; i < R.size(); ++i) R[i] = {(int)(rng() % d), (int)i}; for (std::size_t i = 0; i < S.size(); ++i) S[i] = {(int)(rng() % d), 1000 + (int)i};
        std::size_t Ms[5] = {1, 2, 3, 8, 1000}, M = Ms[rng() % 5]; Kind k = (Kind)(rng() % 4); Stats st;
        assert(sorted(hashJoin(R, S, k, M, st)) == sorted(nestedLoop(R, S, k)));
        assert(st.maxTable <= M);                                       // 메모리 한도를 한 번도 넘지 않았다
    }
    // 독립 오라클: 키별 개수·합만으로 결과 크기와 체크섬을 센다
    auto oracle = [](const std::vector<Tup>& R, const std::vector<Tup>& S, int dom, Kind k, long long& cnt, long long& sum) {
        std::vector<long long> cl(dom), cr(dom), sl(dom), sr(dom); for (auto& t : R) { ++cl[t.key]; sl[t.key] += t.val; } for (auto& t : S) { ++cr[t.key]; sr[t.key] += t.val; }
        cnt = sum = 0; for (int x = 0; x < dom; ++x) {
            if (k == INNER) { cnt += cl[x] * cr[x]; sum += sl[x] * cr[x] + sr[x] * cl[x]; }
            else if (k == LEFT) { cnt += cl[x] * std::max(cr[x], 1LL); sum += cr[x] ? sl[x] * cr[x] + sr[x] * cl[x] : sl[x] + cl[x] * NONE; }
            else if (k == SEMI) { if (cr[x]) { cnt += cl[x]; sum += sl[x] + cl[x] * NONE; } }
            else { if (!cr[x]) { cnt += cl[x]; sum += sl[x] + cl[x] * NONE; } }
        }
    };
    auto checksum = [](const std::vector<Out>& v) { long long s = 0; for (auto& o : v) s += std::get<1>(o) + std::get<2>(o); return s; };
    // ③ 메모리 한도를 줄이면 Grace 단계가 늘고 spill 이 늘지만 결과는 같다
    const int N = 20000, DOM = 5000; std::vector<Tup> R(N), S(N); for (int i = 0; i < N; ++i) { R[i] = {(int)(rng() % DOM), i}; S[i] = {(int)(rng() % DOM), 100000 + i}; }
    std::vector<Out> ref; long spill[3]; int depth[3]; std::size_t Ms[3] = {(std::size_t)N, (std::size_t)N / 4, (std::size_t)N / 64};
    for (int j = 0; j < 3; ++j) {
        Stats st; std::vector<Out> out = sorted(hashJoin(R, S, INNER, Ms[j], st)); long long cnt, sum; oracle(R, S, DOM, INNER, cnt, sum);
        assert((long long)out.size() == cnt && checksum(out) == sum && st.maxTable <= Ms[j]); if (j == 0) ref = out; else assert(out == ref);
        spill[j] = st.spilled; depth[j] = st.maxDepth;
    }
    assert(spill[0] == 0 && spill[1] == 2L * N && spill[2] > spill[1] && spill[2] <= 4L * 2 * N && depth[0] == 0 && depth[1] == 1 && depth[2] >= 2);
    // ④ 치우친 분포: S 에 한 키가 3000 번, R 에도 50 번 → 해시로 쪼갤 수 없어 블록 중첩 루프로 후퇴하지만 메모리 한도는 지킨다
    {   std::vector<Tup> R2, S2; for (int i = 0; i < 3000; ++i) S2.push_back({7, i}); for (int i = 0; i < 2000; ++i) S2.push_back({(int)(rng() % DOM), 5000 + i});
        for (int i = 0; i < 50; ++i) R2.push_back({7, i}); for (int i = 0; i < 3000; ++i) R2.push_back({(int)(rng() % DOM), 100 + i}); std::shuffle(S2.begin(), S2.end(), rng);
        for (int k = 0; k < 4; ++k) { Stats st; std::vector<Out> out = hashJoin(R2, S2, (Kind)k, 100, st); long long cnt, sum; oracle(R2, S2, DOM, (Kind)k, cnt, sum);
            assert((long long)out.size() == cnt && checksum(out) == sum && st.maxTable <= 100 && st.blockLoops >= 1); }
    }
    // ⑤ 큰 입력: 각 20 만 행, 키 20 만 종류 — 탐색 비교 횟수는 O(n + m) 이고 중첩 루프라면 n·m = 4·10^10 번
    {   const int n = 200000; std::vector<Tup> A(n), B(n); for (int i = 0; i < n; ++i) { A[i] = {(int)(rng() % n), i}; B[i] = {(int)(rng() % n), i}; }
        long long cnt, sum; Stats st; std::vector<Out> out = hashJoin(A, B, INNER, n, st); oracle(A, B, n, INNER, cnt, sum);
        assert((long long)out.size() == cnt && checksum(out) == sum && st.probes < 2L * (2 * n) && st.spilled == 0);
        for (int k = 1; k < 4; ++k) { Stats s2; std::vector<Out> o2 = hashJoin(A, B, (Kind)k, n, s2); oracle(A, B, n, (Kind)k, cnt, sum); assert((long long)o2.size() == cnt && checksum(o2) == sum); }
        std::cout << "HashJoin: " << out.size() << " result rows from " << n << " x " << n << " tuples with " << st.probes << " chain probes (nested loop: " << (long long)n * n << " comparisons); Grace spilled " << spill[1] << " / " << spill[2] << " tuples with memory N/4 / N/64 and fell back to block nested loop on the heavy key" << std::endl;
    }
    return 0;
}
// Time Complexity: O(n + m + 결과) (Grace: 디스크 I/O 약 3(n + m), 한 키가 M 보다 많으면 블록 중첩 루프로 O(n·m/M))
// Space Complexity: O(작은 쪽 테이블) (Grace 는 O(M) 튜플)
```
## ExtendibleHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <vector>

// 확장 해싱: 디렉터리(2^전역깊이)가 해시의 하위 비트로 버킷을 가리킨다.
// 버킷이 넘치면 그 버킷만 쪼개고, 지역 깊이가 전역 깊이와 같을 때만 디렉터리를 2배로 늘린다 (전체 재해시 없음).  삭제로 짝(buddy) 버킷과 합칠 수 있으면 합치고, 모든 지역 깊이가 전역 깊이보다 작아지면 디렉터리를 절반으로 줄인다
// 조회는 디렉터리 한 번 + 버킷 한 번(디스크라면 입출력 1~2 회)
// 검증: ① 손으로 짠 예  ② 버킷 용량 2·4·8 에서 std::set 과 60 000 번씩 대조(삽입·삭제·조회)하고 불변식: 디렉터리 크기 = 2^전역깊이, 깊이 d 인 버킷은 정확히 2^(전역-d) 개 칸이 가리키며 하위 d 비트가 같은 칸들,
//        버킷의 모든 키는 그 접두사를 가짐, 용량 초과 없음, 전역깊이 = 지역깊이의 최댓값(축소 후)  ③ 분할 한 번이 옮기는 키는 많아야 용량+1 개(전체 재해시 없음)
//        ④ 균일한 키에서 버킷 평균 점유율이 ln 2 ≈ 0.69 근처, 하위 비트를 일부러 맞춘 40 개 키는 디렉터리를 2^10 이상으로 부풀린다(해시가 몰리면 디렉터리가 커지는 약점)
uint32_t mix(uint32_t x) { x ^= x >> 16; x *= 0x7feb352d; x ^= x >> 15; x *= 0x846ca68b; x ^= x >> 16; return x; }     // 전단사: 서로 다른 키는 서로 다른 해시
struct Bucket { int depth; std::vector<uint32_t> keys; };

class Extendible {
    size_t cap;
    int gd = 1;
    std::vector<std::shared_ptr<Bucket>> dir;
    std::vector<size_t> hist;                                       // hist[d] = 지역 깊이가 d 인 서로 다른 버킷의 수 (디렉터리를 훑지 않고 최대 깊이를 알기 위해)
    long moved_ = 0, splits_ = 0; size_t n_ = 0;
    void repoint(size_t index, int depth, const std::shared_ptr<Bucket>& to) {      // 하위 depth 비트가 index 와 같은 모든 칸을 to 로 (보폭 2^depth)
        size_t stride = size_t(1) << depth; for (size_t i = index & (stride - 1); i < dir.size(); i += stride) dir[i] = to;
    }
    void insertNoDup(uint32_t k) {
        size_t idx = dirIndex(k); auto b = dir[idx];
        if (b->keys.size() < cap) { b->keys.push_back(k); return; }
        if (b->depth == gd) {                                       // 디렉터리 배가
            size_t half = dir.size(); dir.resize(half * 2);
            for (size_t i = 0; i < half; i++) dir[i + half] = dir[i];
            gd++; hist.resize(gd + 2, 0);
        }
        auto nb = std::make_shared<Bucket>(Bucket{b->depth + 1, {}});
        --hist[b->depth]; hist[b->depth + 1] += 2;
        b->depth++; ++splits_;
        size_t stride = size_t(1) << b->depth, newIndex = (idx & (stride - 1)) | (size_t(1) << (b->depth - 1));         // 새 접두사: 한 비트 더
        for (size_t i = newIndex; i < dir.size(); i += stride) dir[i] = nb;                                              // 절반을 새 버킷으로 연결
        std::vector<uint32_t> old; old.swap(b->keys); moved_ += (long)old.size();
        for (auto x : old) insertNoDup(x);
        insertNoDup(k);
    }
    void tryMerge(uint32_t k) {                                     // 짝과 합쳐도 용량 이내면 합치고, 합쳐진 버킷에서 반복
        for (;;) {
            size_t i = dirIndex(k); auto b = dir[i]; if (b->depth <= 1) break;
            size_t buddy = i ^ (size_t(1) << (b->depth - 1)); auto o = dir[buddy];
            if (o->depth != b->depth || b->keys.size() + o->keys.size() > cap) break;
            for (auto x : o->keys) b->keys.push_back(x);
            repoint(buddy, b->depth, b);
            hist[b->depth] -= 2; hist[b->depth - 1] += 1; b->depth--;
        }
        while (gd > 1 && hist[gd] == 0) { dir.resize(dir.size() / 2); gd--; }     // 모든 지역 깊이 < 전역 깊이이면 디렉터리 절반
    }
public:
    mutable long accesses = 0;                                      // 조회가 접근한 구조 수 (디렉터리 1 + 버킷 1)
    explicit Extendible(size_t capacity = 2) : cap(capacity), dir(2), hist(4, 0) { dir[0] = std::make_shared<Bucket>(Bucket{1, {}}); dir[1] = std::make_shared<Bucket>(Bucket{1, {}}); hist[1] = 2; }
    size_t dirIndex(uint32_t k) const { return mix(k) & ((1u << gd) - 1); }
    bool contains(uint32_t k) const { accesses += 2; for (auto x : dir[dirIndex(k)]->keys) if (x == k) return true; return false; }
    void insert(uint32_t k) { if (!contains(k)) { insertNoDup(k); ++n_; } }
    size_t size() const { return n_; }
    bool erase(uint32_t k) {
        auto b = dir[dirIndex(k)]; auto it = std::find(b->keys.begin(), b->keys.end(), k); if (it == b->keys.end()) return false;
        b->keys.erase(it); --n_; tryMerge(k); return true;
    }
    int globalDepth() const { return gd; }
    size_t dirSize() const { return dir.size(); }
    long moved() const { return moved_; }
    long splits() const { return splits_; }
    size_t distinctBuckets() const { std::set<Bucket*> s; for (auto& b : dir) s.insert(b.get()); return s.size(); }
    size_t keyCount() const { std::set<Bucket*> s; size_t n = 0; for (auto& b : dir) if (s.insert(b.get()).second) n += b->keys.size(); return n; }
    double occupancy() const { return (double)keyCount() / ((double)distinctBuckets() * (double)cap); }
    bool consistent() const {
        if (dir.size() != (size_t(1) << gd)) return false;
        std::map<Bucket*, std::vector<size_t>> where; for (size_t i = 0; i < dir.size(); i++) where[dir[i].get()].push_back(i);
        int maxDepth = 0; std::vector<size_t> counted(hist.size(), 0);
        for (auto& kv : where) {
            const Bucket& b = *kv.first; const std::vector<size_t>& idx = kv.second;
            if (b.depth > gd || b.depth < 1 || b.keys.size() > cap) return false; maxDepth = std::max(maxDepth, b.depth); ++counted[b.depth];
            size_t mask = (size_t(1) << b.depth) - 1;
            if (idx.size() != (size_t(1) << (gd - b.depth))) return false;                                       // 깊이 d 인 버킷은 정확히 2^(전역-d) 개 칸이 가리킨다
            for (size_t i : idx) if ((i & mask) != (idx[0] & mask)) return false;                                // 가리키는 칸들은 하위 d 비트가 같다
            for (uint32_t k : b.keys) if ((mix(k) & mask) != (idx[0] & mask)) return false;                      // 키는 버킷의 접두사를 가진다
        }
        return (maxDepth == gd || gd == 1) && counted == hist;
    }
};

int main() {
    Extendible t;
    for (uint32_t k = 1; k <= 200; k++) t.insert(k * 2654435761u);
    for (uint32_t k = 1; k <= 200; k++) assert(t.contains(k * 2654435761u));
    assert(!t.contains(3));
    assert(t.dirSize() == (1u << t.globalDepth()) && t.consistent());
    Extendible e; assert(!e.erase(5) && !e.contains(5) && e.dirSize() == 2 && e.consistent()); e.insert(5); assert(e.erase(5) && !e.contains(5) && e.size() == 0 && e.keyCount() == 0);          // 경계: 빈 구조
    // ② std::set 대조
    std::mt19937 rng(31); long totalOps = 0, shrinks = 0;
    for (size_t cap : {2u, 4u, 8u}) {
        Extendible h(cap); std::set<uint32_t> model; int peakDepth = 1;
        for (int step = 0; step < 60000; ++step) {
            uint32_t k = (uint32_t)(rng() % (step < 30000 ? 2000 : 200)) * 2654435761u; int op = (int)(rng() % 10);                           // 앞 절반은 키가 늘고, 뒤 절반은 키 범위가 좁아 지우기가 많다
            if (op < 5) { h.insert(k); model.insert(k); } else if (op < 8) { assert(h.erase(k) == (model.erase(k) > 0)); } else assert(h.contains(k) == (model.count(k) > 0));
            assert(h.size() == model.size()); ++totalOps;
            if (step % 250 == 0) assert(h.consistent());
            if (h.globalDepth() < peakDepth) ++shrinks; peakDepth = h.globalDepth();
        }
        assert(h.consistent() && h.keyCount() == model.size()); for (uint32_t i = 0; i < 2000; i++) assert(h.contains(i * 2654435761u) == (model.count(i * 2654435761u) > 0));
        assert(h.moved() <= h.splits() * (long)(cap + 1));                                      // ③ 분할 한 번이 옮긴 키 ≤ 용량 + 1 (평균은 훨씬 적다)
    }
    assert(totalOps == 180000 && shrinks > 0);
    // ④ 점유율과 몰린 해시
    {   Extendible u(8); for (uint32_t k = 0; k < 50000; k++) u.insert(k * 2654435761u); double occ = u.occupancy(); assert(occ > 0.62 && occ < 0.76 && u.consistent());      // 이론값 ln 2 ≈ 0.693
        u.accesses = 0; for (uint32_t k = 0; k < 1000; k++) u.contains(k * 2654435761u); assert(u.accesses == 2000);                                                             // 조회마다 디렉터리 1 + 버킷 1
        Extendible skew(2); std::vector<uint32_t> bad; for (uint32_t k = 1; bad.size() < 40; k++) if ((mix(k) & 0x3FF) == 0x155) bad.push_back(k);            // 해시의 하위 10 비트가 같은 키 40 개
        for (uint32_t k : bad) skew.insert(k); assert(skew.globalDepth() >= 10 && skew.dirSize() >= 1024 && skew.keyCount() == 40 && skew.consistent());
        std::cout << "ExtendibleHashing: 200 keys, global depth " << t.globalDepth() << ", directory " << t.dirSize() << "; uniform load " << occ << " (ln 2 = 0.693); 40 skewed keys forced a directory of " << skew.dirSize() << std::endl; }
    return 0;
}
// Time Complexity: 조회 O(1) (디렉터리 1회 + 버킷 1회)
// Space Complexity: O(n + 2^전역깊이)
```
## LinearHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 선형 해싱: 디렉터리 없이 "분할 포인터" p 순서대로 버킷을 하나씩 쪼갠다.
// 주소 = h mod (N0·2^L), 이미 쪼갠 구간(주소 < p)이면 h mod (N0·2^(L+1)).  넘친 버킷이 아니라 p 가 가리키는 버킷이 쪼개진다 — 넘친 버킷은 분할 차례가 올 때까지 긴 사슬을 견딘다
// 적재율이 상한(2.0)을 넘으면 분할, 하한(1.0) 아래로 내려가면 마지막 분할을 되돌리는 병합(수축)
// 검증: ① 손으로 짠 성장 확인  ② std::set 과 60 000 번 대조(삽입·삭제·조회)하고 불변식: 버킷 수 = N0·2^L + p, 모든 키가 자기 주소의 버킷에 있음, 키 수 합 = 크기
//        ③ 삽입 한 번에 버킷은 최대 1 개 늘고 삭제 한 번에 최대 1 개 줄며, 분할 한 번이 옮기는 키 수는 그 버킷의 크기 이하(전체 재해시 n 개와 대조)  ④ 균일한 키 5 000 개의 적재율이 (1.9, 2.0], 가장 긴 버킷이 짧음
uint32_t mix(uint32_t x) { x ^= x >> 16; x *= 0x7feb352d; x ^= x >> 15; x *= 0x846ca68b; x ^= x >> 16; return x; }

class LinearHash {
    static const size_t N0 = 4;
    int level = 0; size_t p = 0, count = 0;
    std::vector<std::vector<uint32_t>> b;
    long maxSplitMoved_ = 0;
    size_t addr(uint32_t k) const {
        size_t a = mix(k) % (N0 << level);
        return a < p ? mix(k) % (N0 << (level + 1)) : a;
    }
    void split() {                                                  // 버킷 p 하나만 둘로 나눈다
        b.emplace_back();
        std::vector<uint32_t> old; old.swap(b[p]); maxSplitMoved_ = std::max<long>(maxSplitMoved_, (long)old.size());
        for (auto k : old) b[mix(k) % (N0 << (level + 1))].push_back(k);
        if (++p == (N0 << level)) { level++; p = 0; }
    }
    void merge() {                                                  // 마지막 분할을 되돌린다: 마지막 버킷의 키를 짝에게 돌려준다
        if (b.size() <= N0) return;
        if (p == 0) { --level; p = N0 << level; }
        --p;
        for (auto k : b.back()) b[p].push_back(k);
        b.pop_back();
    }
public:
    LinearHash() : b(N0) {}
    void insert(uint32_t k) {
        if (contains(k)) return;
        b[addr(k)].push_back(k); ++count;
        if (double(count) / b.size() > 2.0) split();               // 버킷당 평균 2개를 넘으면 분할
    }
    bool erase(uint32_t k) {
        auto& v = b[addr(k)]; auto it = std::find(v.begin(), v.end(), k); if (it == v.end()) return false;
        v.erase(it); --count;
        if (b.size() > N0 && double(count) / b.size() < 1.0) merge();            // 하한 아래면 수축
        return true;
    }
    bool contains(uint32_t k) const { for (auto x : b[addr(k)]) if (x == k) return true; return false; }
    size_t buckets() const { return b.size(); }
    size_t size() const { return count; }
    double load() const { return double(count) / b.size(); }
    long maxSplitMoved() const { return maxSplitMoved_; }
    size_t longest() const { size_t m = 0; for (auto& v : b) m = std::max(m, v.size()); return m; }
    bool consistent() const {
        if (b.size() != (N0 << level) + p) return false;
        size_t total = 0; for (size_t i = 0; i < b.size(); i++) { total += b[i].size(); for (auto k : b[i]) if (addr(k) != i) return false; }
        return total == count;
    }
};

int main() {
    LinearHash t;
    size_t prev = t.buckets();
    for (uint32_t k = 1; k <= 500; k++) {
        t.insert(k * 40503u);
        assert(t.buckets() - prev <= 1);                            // 삽입 한 번에 버킷은 최대 1개만 늘어난다 (점진적 성장)
        prev = t.buckets();
    }
    for (uint32_t k = 1; k <= 500; k++) assert(t.contains(k * 40503u));
    assert(t.consistent() && t.size() == 500 && t.buckets() == 250);                                // 500 개가 버킷 250 개: 정확히 평균 2.0
    LinearHash e; assert(!e.erase(1) && !e.contains(1) && e.buckets() == 4 && e.consistent());      // 경계: 빈 구조
    // ② 모델 대조
    std::mt19937 rng(13); std::set<uint32_t> model; LinearHash h; long grew = 0, shrank = 0;
    for (int step = 0; step < 60000; ++step) {
        uint32_t k = (uint32_t)(rng() % (step < 20000 ? 8000 : step < 40000 ? 3000 : 20)) * 40503u; int op = (int)(rng() % 10); size_t before = h.buckets();
        if (op < (step < 20000 ? 7 : 3)) { h.insert(k); model.insert(k); } else if (op < 9) { assert(h.erase(k) == (model.erase(k) > 0)); } else assert(h.contains(k) == (model.count(k) > 0));
        assert(h.size() == model.size() && (h.buckets() > before ? h.buckets() - before <= 1 : before - h.buckets() <= 1));       // ③ 한 번에 최대 한 개
        grew += h.buckets() > before; shrank += h.buckets() < before;
        if (step % 300 == 0) assert(h.consistent());
    }
    assert(h.consistent() && grew > 1000);
    std::vector<uint32_t> drain(model.begin(), model.end()); std::shuffle(drain.begin(), drain.end(), rng);            // 전부 지우면 수축이 이어져 처음 크기로 돌아간다
    for (size_t i = 0; i < drain.size(); i++) {
        size_t before = h.buckets(); assert(h.erase(drain[i])); model.erase(drain[i]); assert(before - h.buckets() <= 1); shrank += h.buckets() < before;
        if (i % 400 == 0) assert(h.consistent());
    }
    assert(h.size() == 0 && h.buckets() == 4 && h.consistent() && shrank > 1000);
    for (uint32_t i = 0; i < 8000; i++) assert(!h.contains(i * 40503u));
    // ④ 균일한 키
    LinearHash u; for (uint32_t k = 0; k < 5000; k++) u.insert(k * 2654435761u);
    assert(u.load() > 1.9 && u.load() <= 2.0 && u.longest() < 20 && u.maxSplitMoved() <= 20 && u.maxSplitMoved() * 100 < 5000);          // 분할 한 번이 옮긴 키 ≪ 전체 5 000
    std::cout << "LinearHashing: 500 keys in " << t.buckets() << " buckets; 5000 keys -> load " << u.load() << ", longest bucket " << u.longest() << ", largest split moved " << u.maxSplitMoved() << " keys" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(1) 평균, 분할 1회 O(버킷 크기)
// Space Complexity: O(n)
```
# Part 10. OS·런타임 구현
## 왜 Java HashMap은 TreeBin으로 바뀌는가?
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>

// Java 8 HashMap: 한 버킷(bin)의 연결 리스트에 이미 8개 이상 들어 있는데 하나를 더 넣을 때, 테이블 크기가 64 이상이면 트리(TreeBin, 레드-블랙 트리)로 바꾸고 64 미만이면 트리 대신 테이블을 두 배로 늘린다.
// 해시가 몰려도 (또는 공격당해도) 한 bin 의 탐색이 O(n) -> O(log n) 이 된다. 크기 조정 때 나눈 조각이 6개 이하이거나 삭제로 6개 이하로 줄면 다시 리스트로 되돌린다.
// 여기서는 그 규칙 전체를 따르는 해시맵 모형을 만든다 (bin 의 트리는 레드-블랙 대신 결정적 우선순위의 트립 — 기대 O(log n) 으로 같은 효과): 인덱스 = (h ^ h>>16) & (용량-1), 적재율 0.75 에서 두 배, 분할은 h & 옛 용량 비트
// 검증: ① 규칙 함수(경계값)  ② 용량 16 에서 모든 키가 같은 해시일 때: 9번째 삽입은 크기 조정(32), 10번째는 크기 조정(64), 11번째에야 트리가 된다  ③ 해시가 몰린 / 고른 두 해시 함수로 std::map 과 40 000 번 대조(삽입·삭제·조회)하고 불변식:
//        트리 bin 은 크기 ≥ 7, 리스트 bin 은 용량 ≥ 64 이면 크기 ≤ 9, 트립의 정렬·힙 성질, 총 개수  ④ 키 1 024 개가 한 bin 에 몰린 최악에서 리스트(treeify 끔) 평균 비교 ≈ N/2, 트리는 그것의 1/20 미만  ⑤ 삭제로 6개 이하가 되면 리스트로 복귀
const int TREEIFY_THRESHOLD = 8, UNTREEIFY_THRESHOLD = 6, MIN_TREEIFY_CAPACITY = 64;
std::string binKind(int binSize, int tableCapacity, bool wasTree) {                // binSize: 새 원소를 넣기 *전* 의 크기 (트리였다면 현재 크기)
    if (wasTree) return binSize <= UNTREEIFY_THRESHOLD ? "list" : "tree";
    if (binSize >= TREEIFY_THRESHOLD) return tableCapacity >= MIN_TREEIFY_CAPACITY ? "tree" : "resize";   // 용량이 작으면 트리 대신 테이블 확장
    return "list";
}

struct TNode { int key, val; uint32_t pri; TNode *l = nullptr, *r = nullptr; };
static uint32_t prio(int key) { uint32_t x = (uint32_t)key * 2654435761u; x ^= x >> 15; x *= 0x2c1b3c6du; x ^= x >> 12; return x; }
static long g_cmp = 0;                                                             // 키 비교(노드 방문) 횟수
TNode* merge(TNode* a, TNode* b) { if (!a) return b; if (!b) return a; if (a->pri > b->pri) { a->r = merge(a->r, b); return a; } b->l = merge(a, b->l); return b; }
void split(TNode* t, int key, TNode*& a, TNode*& b) { if (!t) { a = b = nullptr; return; } if (t->key < key) { a = t; split(t->r, key, a->r, b); } else { b = t; split(t->l, key, a, b->l); } }
TNode* find(TNode* t, int key) { while (t) { ++g_cmp; if (key == t->key) return t; t = key < t->key ? t->l : t->r; } return nullptr; }
TNode* eraseRec(TNode* t, int key, bool& removed) {
    if (!t) return nullptr;
    if (key < t->key) t->l = eraseRec(t->l, key, removed); else if (key > t->key) t->r = eraseRec(t->r, key, removed);
    else { TNode* m = merge(t->l, t->r); delete t; removed = true; return m; }
    return t;
}
void collect(TNode* t, std::vector<std::pair<int, int>>& out) { if (!t) return; collect(t->l, out); out.push_back({t->key, t->val}); collect(t->r, out); }
void destroy(TNode* t) { if (!t) return; destroy(t->l); destroy(t->r); delete t; }
bool treapValid(TNode* t, long lo, long hi, size_t& count) {                        // 정렬 성질 + 힙 성질
    if (!t) return true; if (t->key <= lo || t->key >= hi) return false; ++count;
    if ((t->l && t->l->pri > t->pri) || (t->r && t->r->pri > t->pri)) return false;
    return treapValid(t->l, lo, t->key, count) && treapValid(t->r, t->key, hi, count);
}

struct Bin { std::vector<std::pair<int, int>> list; TNode* root = nullptr; bool tree = false; size_t size = 0; };
class JavaMap {
    std::vector<Bin> table; size_t n = 0; std::function<uint32_t(int)> hashFn; bool allowTree;
    uint32_t spread(int key) const { uint32_t h = hashFn(key); return h ^ (h >> 16); }
    size_t index(int key, size_t cap) const { return spread(key) & (cap - 1); }
    void treeify(Bin& b) { for (auto& e : b.list) { TNode* nd = new TNode{e.first, e.second, prio(e.first)}; TNode *x, *y; split(b.root, e.first, x, y); b.root = merge(merge(x, nd), y); } b.list.clear(); b.tree = true; }
    void untreeify(Bin& b) { b.list.clear(); collect(b.root, b.list); destroy(b.root); b.root = nullptr; b.tree = false; }
    void put(Bin& b, int key, int val) {                                          // 이 bin 에 새 키를 추가 (이미 있는지는 호출 전에 확인)
        if (b.tree) { TNode* nd = new TNode{key, val, prio(key)}; TNode *x, *y; split(b.root, key, x, y); b.root = merge(merge(x, nd), y); ++b.size; return; }
        b.list.push_back({key, val}); ++b.size;
    }
    void resize() {
        size_t oldCap = table.size(); std::vector<Bin> nt(oldCap * 2);
        for (size_t i = 0; i < oldCap; i++) {
            Bin& old = table[i]; std::vector<std::pair<int, int>> items; if (old.tree) collect(old.root, items); else items = old.list; bool wasTree = old.tree; destroy(old.root); old.root = nullptr;
            for (auto& e : items) { Bin& dst = nt[(spread(e.first) & oldCap) ? i + oldCap : i]; dst.list.push_back(e); ++dst.size; }
            for (size_t part : {i, i + oldCap}) { Bin& dst = nt[part]; if (wasTree && allowTree && dst.size > (size_t)UNTREEIFY_THRESHOLD) treeify(dst); }       // 트리였고 조각이 7개 이상이면 트리 유지, 아니면 리스트
        }
        table.swap(nt);
    }
public:
    mutable long probes = 0;
    explicit JavaMap(std::function<uint32_t(int)> h, bool treeEnabled = true) : table(16), hashFn(h), allowTree(treeEnabled) {}
    ~JavaMap() { for (auto& b : table) destroy(b.root); }
    JavaMap(const JavaMap&) = delete; JavaMap& operator=(const JavaMap&) = delete;
    int* get(int key) {
        Bin& b = table[index(key, table.size())];
        if (b.tree) { long before = g_cmp; TNode* t = find(b.root, key); probes += g_cmp - before; return t ? &t->val : nullptr; }
        for (auto& e : b.list) { ++probes; if (e.first == key) return &e.second; }
        return nullptr;
    }
    void put(int key, int val) {
        if (int* p = get(key)) { *p = val; return; }
        Bin& b = table[index(key, table.size())]; size_t before = b.size; bool wasTree = b.tree; put(b, key, val); ++n;
        if (!wasTree && allowTree && before >= (size_t)TREEIFY_THRESHOLD) { if (table.size() >= (size_t)MIN_TREEIFY_CAPACITY) treeify(b); else resize(); }       // 용량이 작으면 트리 대신 크기 조정
        if (n > table.size() * 3 / 4) resize();                                      // 적재율 0.75
    }
    bool remove(int key) {
        Bin& b = table[index(key, table.size())];
        if (b.tree) { bool removed = false; b.root = eraseRec(b.root, key, removed); if (!removed) return false; --b.size; --n; if (b.size <= (size_t)UNTREEIFY_THRESHOLD) untreeify(b); return true; }
        for (size_t i = 0; i < b.list.size(); i++) if (b.list[i].first == key) { b.list.erase(b.list.begin() + i); --b.size; --n; return true; }
        return false;
    }
    size_t size() const { return n; }
    size_t capacity() const { return table.size(); }
    size_t treeBins() const { size_t c = 0; for (auto& b : table) c += b.tree; return c; }
    size_t binSize(int key) const { return table[index(key, table.size())].size; }
    bool binIsTree(int key) const { return table[index(key, table.size())].tree; }
    bool valid() const {
        size_t total = 0;
        for (auto& b : table) {
            total += b.size;
            if (b.tree) { size_t c = 0; if (!treapValid(b.root, -3000000000L, 3000000000L, c) || c != b.size || b.size <= (size_t)UNTREEIFY_THRESHOLD || !b.list.empty()) return false; }
            else if (b.list.size() != b.size || b.root || (allowTree && table.size() >= (size_t)MIN_TREEIFY_CAPACITY && b.size > (size_t)TREEIFY_THRESHOLD + 1)) return false;
        }
        return total == n;
    }
};

int main() {
    assert(binKind(7, 64, false) == "list");
    assert(binKind(8, 64, false) == "tree");
    assert(binKind(8, 32, false) == "resize");
    assert(binKind(6, 64, true) == "list" && binKind(7, 64, true) == "tree");
    // ② 모든 키가 같은 해시 (용량 16 에서 시작)
    {   JavaMap m([](int) { return 7u; }); for (int i = 0; i < 8; i++) m.put(i, i); assert(m.capacity() == 16 && !m.binIsTree(0) && m.binSize(0) == 8);
        m.put(8, 8); assert(m.capacity() == 32 && !m.binIsTree(0));                         // 9번째: 트리 대신 테이블 확장
        m.put(9, 9); assert(m.capacity() == 64 && !m.binIsTree(0));                         // 10번째: 한 번 더 (용량이 아직 64 미만이었다)
        m.put(10, 10); assert(m.capacity() == 64 && m.binIsTree(0) && m.treeBins() == 1 && m.valid());   // 11번째: 용량 64 이므로 드디어 트리
        for (int i = 0; i <= 10; i++) assert(m.get(i) && *m.get(i) == i);
        // ⑤ 삭제로 6개 이하가 되면 리스트로
        for (int i = 10; i >= 6; i--) { assert(m.remove(i)); assert(m.valid()); }
        assert(m.binSize(0) == 6 && !m.binIsTree(0) && m.treeBins() == 0 && m.size() == 6);
        for (int i = 0; i < 6; i++) assert(*m.get(i) == i); }
    // ③ std::map 대조
    std::mt19937 rng(21); long treeSeen = 0;
    for (int variant = 0; variant < 2; variant++) {
        JavaMap m(variant == 0 ? std::function<uint32_t(int)>([](int k) { return (uint32_t)(k % 6) * 0x10001u; })        // 6 개의 해시값에 몰림
                               : std::function<uint32_t(int)>([](int k) { uint32_t x = (uint32_t)k * 2654435761u; return x ^ (x >> 13); }));            // 고른 해시
        std::map<int, int> ref;
        for (int step = 0; step < 40000; ++step) {
            int k = (int)(rng() % (step < 20000 ? 2000 : 150)) - 50; int op = (int)(rng() % 10);
            if (op < 5) { m.put(k, step); ref[k] = step; } else if (op < 8) assert(m.remove(k) == (ref.erase(k) > 0)); else { int* p = m.get(k); auto it = ref.find(k); assert((p != nullptr) == (it != ref.end()) && (!p || *p == it->second)); }
            assert(m.size() == ref.size()); if (step % 100 == 0) { assert(m.valid()); treeSeen += (long)m.treeBins(); }
        }
        assert(m.valid()); for (auto& kv : ref) assert(*m.get(kv.first) == kv.second);
    }
    assert(treeSeen > 500);                                                                // 몰린 해시에서는 트리 bin 이 실제로 생겼다
    // ④ 최악: 키 1 024 개가 한 bin
    const int N = 1024; double avg[2];
    for (int variant = 0; variant < 2; variant++) {
        JavaMap m([](int) { return 12345u; }, variant == 1); for (int i = 0; i < N; i++) m.put(i * 7919 % 100003, i);
        m.probes = 0; for (int i = 0; i < N; i++) assert(m.get(i * 7919 % 100003) != nullptr); avg[variant] = (double)m.probes / N;
        assert(m.size() == (size_t)N && m.valid() && (variant == 1) == (m.treeBins() == 1));
    }
    assert(avg[0] > N / 2 - 50 && avg[1] < avg[0] / 20);
    std::cout << "average comparisons in one bin of " << N << ": list " << avg[0] << ", tree " << avg[1] << std::endl;
    return 0;
}
// Time Complexity: 리스트 bin O(n), 트리 bin O(log n)
// Space Complexity: O(n)
```
## Python dict의 구현 원리
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

// CPython 3.6+ 의 compact dict: 해시 테이블(indices)은 "entries 배열의 번호"만 갖고,
// 실제 (hash, key, value) 는 삽입 순서대로 entries 에 쌓인다 -> 삽입 순서 보존 + 메모리 절약.
// 충돌은 개방 주소법: i = (5*i + perturb + 1) mod size,  perturb 는 매번 5비트씩 오른쪽 시프트 (해시의 상위 비트도 쓰도록).
// 크기가 2의 거듭제곱이면 i -> 5i+1 이 전체 주기를 가지므로 perturb 가 0 이 된 뒤에는 *모든 칸* 을 방문한다 → 빈 칸이 하나라도 있으면 탐사가 끝난다
// 확장은 살아있는 항목만 모아(죽은 항목·묘비 제거) 새 크기를 *살아 있는 개수* 의 3배 이상 2의 거듭제곱으로 잡는다.  삽입 순서는 확장 뒤에도 유지된다
// 검증: ① 손으로 짠 예(삽입 순서, 지웠다 다시 넣으면 맨 뒤)  ② 탐사열 완전성: 크기 8~4096 에서 무작위 64 비트 해시(음수 포함)로 시작한 탐사가 전체 칸을 방문  ③ 모델 대조: std::map(값) + 벡터(순서)와 60 000 번 대조하고
//        키 순서 = 모델의 삽입 순서, 매번 indices 가 가리키는 entries 가 일치  ④ 넣고 지우기를 20 만 번 반복해도 (살아 있는 키 ≤ 10) 표와 entries 가 작게 유지  ⑤ 메모리: compact 구조가 같은 용량의 희소 표(칸마다 24 바이트)보다 25 % 이상 작음
class PyDict {
    static constexpr int EMPTY = -1, DUMMY = -2;
    struct Entry { long key; long value; bool live; };
    std::vector<int> indices = std::vector<int>(8, EMPTY);
    std::vector<Entry> entries;
    size_t used = 0, resizes_ = 0;
    size_t mask() const { return indices.size() - 1; }
    int lookup(long key, size_t& slot) const {
        size_t perturb = (size_t)key, i = perturb & mask();
        long firstDummy = -1;
        for (;;) {
            int ix = indices[i];
            if (ix == EMPTY) { slot = firstDummy >= 0 ? (size_t)firstDummy : i; return -1; }
            if (ix == DUMMY) { if (firstDummy < 0) firstDummy = (long)i; }
            else if (entries[ix].live && entries[ix].key == key) { slot = i; return ix; }
            perturb >>= 5;
            i = (i * 5 + perturb + 1) & mask();
        }
    }
    void resize() {                                              // 살아있는 entries 만 모아 indices 를 새로 만든다
        std::vector<Entry> live;
        for (auto& e : entries) if (e.live) live.push_back(e);
        entries = live;
        size_t want = 8; while (want * 2 / 3 < entries.size() * 3) want *= 2;                 // 살아 있는 개수의 3배 이상 (확장 직후 사용률 ≤ 1/3)
        indices.assign(want, EMPTY); ++resizes_;
        for (size_t n = 0; n < entries.size(); n++) {
            size_t slot; lookup(entries[n].key, slot);
            indices[slot] = (int)n;
        }
    }
public:
    void set(long key, long value) {
        size_t slot;
        int ix = lookup(key, slot);
        if (ix >= 0) { entries[ix].value = value; return; }
        if (entries.size() >= indices.size() * 2 / 3) { resize(); lookup(key, slot); }   // entries(죽은 것 포함)가 사용률 2/3 에 닿으면 확장
        entries.push_back({key, value, true});
        indices[slot] = (int)entries.size() - 1;
        ++used;
    }
    bool get(long key, long& value) const { size_t s; int ix = lookup(key, s); if (ix < 0) return false; value = entries[ix].value; return true; }
    bool erase(long key) {
        size_t slot; int ix = lookup(key, slot);
        if (ix < 0) return false;
        entries[ix].live = false; indices[slot] = DUMMY; --used;     // 묘비(DUMMY) 를 남긴다
        return true;
    }
    std::vector<long> keys() const { std::vector<long> r; for (auto& e : entries) if (e.live) r.push_back(e.key); return r; }
    size_t size() const { return used; }
    size_t tableSize() const { return indices.size(); }
    size_t entryCount() const { return entries.size(); }
    size_t resizes() const { return resizes_; }
    bool valid() const {                                          // indices 가 가리키는 entries 가 살아 있고 키가 일치, 살아 있는 entries 는 정확히 한 칸이 가리킴, EMPTY 가 존재
        std::vector<int> pointed(entries.size(), 0); size_t empties = 0;
        for (size_t i = 0; i < indices.size(); i++) { int ix = indices[i]; if (ix == EMPTY) ++empties; else if (ix >= 0) { if (ix >= (int)entries.size() || !entries[ix].live) return false; ++pointed[ix]; } }
        size_t live = 0; for (size_t n = 0; n < entries.size(); n++) { if (entries[n].live) { ++live; if (pointed[n] != 1) return false; size_t s; if (lookup(entries[n].key, s) != (int)n) return false; } else if (pointed[n] != 0) return false; }
        return live == used && empties > 0;
    }
};

int main() {
    PyDict d;
    long order[] = {42, 7, 99, 3, 1000, 15, 8, 64, 23, 5, 77, 31};
    for (long k : order) d.set(k, k * 2);
    assert((d.keys() == std::vector<long>(order, order + 12)));        // 삽입 순서 그대로
    assert(d.erase(99) && d.erase(5) && !d.erase(12345));
    d.set(99, 1);                                                      // 지웠다 다시 넣으면 맨 뒤로
    std::vector<long> expect = {42, 7, 3, 1000, 15, 8, 64, 23, 77, 31, 99};
    assert(d.keys() == expect);
    for (long k = 0; k < 200; k++) d.set(k + 10000, k);                // 확장 유발
    long v;
    assert(d.get(10150, v) && v == 150 && d.get(42, v) && v == 84 && !d.get(5, v));
    assert(d.tableSize() >= 128 && d.valid());
    PyDict empty; assert(empty.size() == 0 && !empty.get(1, v) && !empty.erase(1) && empty.keys().empty() && empty.valid());
    // ② 탐사열 완전성
    std::mt19937_64 rng(5);
    for (size_t size = 8; size <= 4096; size *= 2) {
        for (int t = 0; t < 40; t++) {
            size_t perturb = (size_t)rng(), i = perturb & (size - 1); std::vector<bool> seen(size, false); size_t visited = 0, steps = 0;
            while (visited < size && steps < 20 * size + 200) { if (!seen[i]) { seen[i] = true; ++visited; } perturb >>= 5; i = (i * 5 + perturb + 1) & (size - 1); ++steps; }
            assert(visited == size);                                                    // perturb 가 0 이 된 뒤에는 i -> 5i+1 이 전체 주기
        }
    }
    // ③ 모델 대조
    std::mt19937 r32(77); PyDict m; std::map<long, long> ref; std::vector<long> order2; long maxTable = 0;
    for (int step = 0; step < 60000; ++step) {
        long k = (long)(r32() % (step < 30000 ? 3000 : 120)) - 40; if (r32() % 11 == 0) k = (long)(rng() >> 3) * (r32() % 2 ? 1 : -1); int op = (int)(r32() % 10);          // 아주 큰 값·음수 키도 섞는다
        if (op < 5) { m.set(k, step); if (!ref.count(k)) order2.push_back(k); ref[k] = step; }
        else if (op < 8) { bool e = m.erase(k); assert(e == (ref.erase(k) > 0)); if (e) order2.erase(std::find(order2.begin(), order2.end(), k)); }
        else { long val; bool f = m.get(k, val); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || val == it->second)); }
        assert(m.size() == ref.size()); maxTable = std::max<long>(maxTable, (long)m.tableSize());
        if (step % 500 == 0) { assert(m.valid() && m.keys() == order2); }
    }
    assert(m.valid() && m.keys() == order2 && maxTable >= 4096);
    // ④ 넣고 지우기를 반복해도 커지지 않는다
    PyDict churn; std::vector<long> alive; long next = 1;
    for (int i = 0; i < 200000; ++i) { churn.set(next, next); alive.push_back(next++); if (alive.size() > 10) { size_t at = r32() % alive.size(); assert(churn.erase(alive[at])); alive.erase(alive.begin() + (long)at); } }
    assert(churn.size() == 10 && churn.tableSize() <= 64 && churn.entryCount() <= churn.tableSize() * 2 / 3 + 1 && churn.resizes() > 1000 && churn.valid());
    // ⑤ 메모리: 희소 표(칸마다 {hash, key, value} 24 바이트) 대 compact(indices + 사용률 2/3 만큼의 entries).  CPython 은 칸 수에 따라 indices 를 1·2·4 바이트로 줄인다 (이 모형은 int 4 바이트로 단순화)
    for (size_t n : {100u, 1000u, 10000u, 100000u}) {
        size_t slots = 8; while (slots * 2 / 3 < n) slots *= 2;
        size_t idxBytes = slots <= 128 ? 1 : slots <= 32768 ? 2 : 4;
        double sparse = (double)slots * 24, compact = (double)slots * (double)idxBytes + (double)(slots * 2 / 3) * 24;
        assert(compact < sparse * (idxBytes <= 2 ? 0.76 : 0.84));                                // 1·2 바이트 색인이면 24~29 % 절약, 4 바이트여도 17 %
    }
    std::cout << "PyDict size=" << d.size() << " table=" << d.tableSize() << "; order and contents matched the model over 60000 operations, churn kept the table at " << churn.tableSize() << " slots" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1)
// Space Complexity: O(n)  (indices 는 int 배열이라 entries 대비 작다)
```
## C++ unordered_map의 구조
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// std::unordered_map: 분리 연쇄법(노드 기반). 표준이 "bucket 인터페이스"와 "참조 안정성"을 요구한다.
//  - rehash 가 일어나도 요소(노드)는 이동하지 않으므로 요소에 대한 포인터/참조는 유효하다 (반복자는 무효화될 수 있다)
//  - 그래서 개방 주소법 기반의 빠른 해시맵(SwissTable 등)은 표준 인터페이스를 그대로 구현할 수 없다
// libstdc++ 의 실제 배치를 직접 만든다: 모든 요소가 *하나의 단일 연결 리스트* 에 있고, 같은 버킷의 요소는 그 안에서 연속해 있다.
// 버킷 배열의 i 번째 칸은 "버킷 i 의 첫 노드 *바로 앞* 노드" 를 가리킨다(비어 있으면 null).  그래서 전체 순회는 빈 버킷을 건너뛰지 않고도 O(n), 삭제는 앞 노드를 바로 안다
// 버킷 수는 소수로 키우고, 요소 수 > 버킷 수 × max_load_factor 가 되면 늘린다
// 검증: ① 원래 예(std::unordered_map 의 표준 보장)  ② 같은 연산열을 표준 컨테이너와 모형에 40 000 번 적용해 내용이 같고 bucket 인터페이스(모든 버킷 크기의 합 = size, 요소의 bucket(k) 가 실제 버킷)
//        ③ 구조 불변식: 버킷마다 요소가 리스트에서 연속, 버킷 칸이 가리키는 앞 노드 다음이 그 버킷의 첫 노드, 적재율 ≤ max_load_factor  ④ 참조 안정성(rehash 후에도 요소 주소 그대로)과 reserve 후 재배치 없음
//        ⑤ max_load_factor 를 바꿔도 지켜지고, 버킷 수가 소수  ⑥ 같은 해시에 모두 몰려도 정답(버킷 하나가 길어질 뿐)
bool isPrime(size_t x) { if (x < 2) return false; for (size_t d = 2; d * d <= x; d++) if (x % d == 0) return false; return true; }
size_t nextPrime(size_t x) { while (!isPrime(x)) ++x; return x; }

template <class K, class V, class Hash = std::hash<K>>
class MiniUnorderedMap {
    struct NodeBase { NodeBase* next = nullptr; };
    struct Node : NodeBase { K key; V val; size_t h; Node(const K& k, size_t hh) : key(k), val(), h(hh) {} };
    NodeBase head;                                              // before_begin
    std::vector<NodeBase*> buckets{nullptr};                    // 버킷 i 의 첫 노드의 앞 노드, 비면 null (처음에는 버킷 1 개)
    size_t n = 0, rehashes_ = 0; float mlf = 1.0f;
    size_t bucketOf(size_t h) const { return h % buckets.size(); }
    static Node* node(NodeBase* p) { return static_cast<Node*>(p); }
    void insertNode(Node* nd) {                                 // 버킷의 맨 앞에, 버킷이 비었으면 리스트 맨 앞에
        size_t b = bucketOf(nd->h);
        if (buckets[b]) { nd->next = buckets[b]->next; buckets[b]->next = nd; }
        else {
            nd->next = head.next; head.next = nd;
            if (nd->next) buckets[bucketOf(node(nd->next)->h)] = nd;      // 예전 첫 노드가 속한 버킷의 "앞 노드" 가 이제 nd
            buckets[b] = &head;
        }
    }
    void rehashTo(size_t bc) {
        std::vector<Node*> all; for (NodeBase* p = head.next; p; p = p->next) all.push_back(node(p));
        head.next = nullptr; buckets.assign(bc, nullptr); for (Node* nd : all) insertNode(nd); ++rehashes_;
    }
    void growIfNeeded() { if ((float)n > (float)buckets.size() * mlf) rehashTo(nextPrime(std::max(buckets.size() * 2 + 1, (size_t)std::ceil((float)n / mlf)))); }
public:
    MiniUnorderedMap() = default;
    MiniUnorderedMap(const MiniUnorderedMap&) = delete; MiniUnorderedMap& operator=(const MiniUnorderedMap&) = delete;
    ~MiniUnorderedMap() { for (NodeBase* p = head.next; p;) { NodeBase* nx = p->next; delete node(p); p = nx; } }
    V* find(const K& k) const {
        size_t h = Hash{}(k), b = bucketOf(h); if (!buckets[b]) return nullptr;
        for (Node* p = node(buckets[b]->next); p && bucketOf(p->h) == b; p = node(p->next)) if (p->key == k) return &p->val;
        return nullptr;
    }
    V& operator[](const K& k) {
        if (V* v = find(k)) return *v;
        size_t h = Hash{}(k); Node* nd = new Node(k, h); ++n; growIfNeeded(); insertNode(nd); return nd->val;       // 확장은 삽입 전에 (새 노드 포함 개수로)
    }
    bool erase(const K& k) {
        size_t h = Hash{}(k), b = bucketOf(h); if (!buckets[b]) return false;
        NodeBase* prev = buckets[b]; Node* cur = node(prev->next);
        for (; cur && bucketOf(cur->h) == b; prev = cur, cur = node(cur->next)) if (cur->key == k) break;
        if (!cur || bucketOf(cur->h) != b) return false;
        Node* nx = node(cur->next); size_t nb = nx ? bucketOf(nx->h) : b;
        if (prev == buckets[b] && (!nx || nb != b)) buckets[b] = nullptr;       // 버킷의 유일한 노드였다
        if (nx && nb != b) buckets[nb] = prev;                                  // 다음 버킷의 "앞 노드" 가 prev 로 바뀐다
        prev->next = nx; delete cur; --n; return true;
    }
    void rehash(size_t count) { size_t need = std::max<size_t>(count, (size_t)std::ceil((float)n / mlf)); rehashTo(nextPrime(std::max<size_t>(need, 1))); }
    void reserve(size_t count) { size_t need = (size_t)std::ceil((float)count / mlf); if (need > buckets.size()) rehashTo(nextPrime(need)); }
    void max_load_factor(float f) { mlf = f; growIfNeeded(); }
    float max_load_factor() const { return mlf; }
    size_t size() const { return n; }
    size_t bucket_count() const { return buckets.size(); }
    float load_factor() const { return (float)n / (float)buckets.size(); }
    size_t bucket(const K& k) const { return bucketOf(Hash{}(k)); }
    size_t bucket_size(size_t b) const { size_t c = 0; if (!buckets[b]) return 0; for (Node* p = node(buckets[b]->next); p && bucketOf(p->h) == b; p = node(p->next)) ++c; return c; }
    size_t rehashes() const { return rehashes_; }
    template <class F> void forEach(F f) const { for (NodeBase* p = head.next; p; p = p->next) f(node(p)->key, node(p)->val); }
    template <class F> void forEachInBucket(size_t b, F f) const { if (!buckets[b]) return; for (Node* p = node(buckets[b]->next); p && bucketOf(p->h) == b; p = node(p->next)) f(p->key, p->val); }
    bool valid() const {
        size_t total = 0; std::vector<size_t> runs(buckets.size(), 0); long prevBucket = -1;
        for (NodeBase* p = head.next; p; p = p->next) { ++total; long b = (long)bucketOf(node(p)->h); if (b != prevBucket) ++runs[(size_t)b]; prevBucket = b; }
        if (total != n) return false;
        for (size_t b = 0; b < buckets.size(); b++) {
            if (runs[b] > 1) return false;                                                                    // 같은 버킷의 요소는 리스트에서 하나의 연속 구간
            if (!buckets[b]) { if (runs[b] != 0) return false; continue; }
            if (runs[b] != 1 || !buckets[b]->next || bucketOf(node(buckets[b]->next)->h) != b) return false;   // 앞 노드의 다음이 그 버킷의 첫 노드
            NodeBase* before = buckets[b]; if (before != &head && bucketOf(node(before)->h) == b) return false; // 앞 노드는 다른 버킷의 노드(또는 head)
        }
        return true;
    }
};
struct ConstHash { size_t operator()(int) const { return 42; } };

int main() {
    std::unordered_map<int, int> m;
    m.max_load_factor(1.0f);
    m[1] = 10;
    int* p = &m[1];
    size_t buckets0 = m.bucket_count();
    for (int i = 2; i <= 5000; i++) m[i] = i * 10;
    assert(m.bucket_count() > buckets0);                    // 적재율이 max_load_factor 를 넘어 rehash 발생
    assert(p == &m[1] && *p == 10);                         // 노드 주소는 그대로
    assert(m.load_factor() <= m.max_load_factor());

    size_t total = 0;                                       // bucket 인터페이스: 모든 버킷 크기의 합 = size
    for (size_t b = 0; b < m.bucket_count(); b++) total += m.bucket_size(b);
    assert(total == m.size());
    assert(m.bucket(1234) < m.bucket_count());
    // ② 같은 연산열을 표준 컨테이너와 모형에 적용
    std::mt19937 rng(3); MiniUnorderedMap<int, int> mine; std::unordered_map<int, int> ref; long rehashSeen = 0;
    for (int step = 0; step < 40000; ++step) {
        int k = (int)(rng() % (step < 25000 ? 6000 : 400)) - 200; int op = (int)(rng() % 10);
        if (op < 5) { mine[k] = step; ref[k] = step; } else if (op < 8) assert(mine.erase(k) == (ref.erase(k) > 0));
        else { int* a = mine.find(k); auto it = ref.find(k); assert((a != nullptr) == (it != ref.end()) && (!a || *a == it->second)); }
        assert(mine.size() == ref.size() && mine.load_factor() <= mine.max_load_factor() + 1e-6f);
        if (step % 400 == 0) {
            assert(mine.valid()); size_t sum = 0; for (size_t b = 0; b < mine.bucket_count(); b++) sum += mine.bucket_size(b); assert(sum == mine.size());
            std::map<int, int> a, c; mine.forEach([&](int key, int v) { a[key] = v; }); for (auto& kv : ref) c[kv.first] = kv.second; assert(a == c);
            for (size_t b = 0; b < mine.bucket_count(); b += 7) mine.forEachInBucket(b, [&](int key, int) { assert(mine.bucket(key) == b); });             // 버킷 b 에서 나온 요소의 bucket(k) 는 b
        }
        rehashSeen = (long)mine.rehashes();
    }
    assert(mine.valid() && rehashSeen > 5);
    // ④ 참조 안정성, reserve
    {   MiniUnorderedMap<int, int> s; s[1] = 10; int* q = &s[1]; for (int i = 2; i <= 5000; i++) s[i] = i * 10; assert(s.rehashes() > 3 && q == s.find(1) && *q == 10 && s.valid());
        std::unordered_map<int, int> stdm; stdm[1] = 10; int* sq = &stdm[1]; for (int i = 2; i <= 5000; i++) stdm[i] = i * 10; assert(sq == &stdm[1]);               // 표준 컨테이너도 마찬가지
        MiniUnorderedMap<int, int> r; r.reserve(3000); size_t before = r.rehashes(); for (int i = 0; i < 3000; i++) r[i] = i; assert(r.rehashes() == before && r.load_factor() <= 1.0f && r.valid()); }
    // ⑤ max_load_factor 와 소수 버킷
    for (float f : {0.5f, 1.0f, 2.0f, 4.0f}) {
        MiniUnorderedMap<int, int> t; t.max_load_factor(f); for (int i = 0; i < 4000; i++) { t[i * 31] = i; assert(t.load_factor() <= f + 1e-6f); }
        assert(isPrime(t.bucket_count()) && t.valid());
        if (f == 4.0f) assert(t.bucket_count() < 2000); else if (f == 0.5f) assert(t.bucket_count() > 6000);                                  // 허용 적재율이 클수록 버킷이 적다
    }
    // ⑥ 모두 같은 해시
    {   MiniUnorderedMap<int, int, ConstHash> w; for (int i = 0; i < 300; i++) w[i] = i * 3; for (int i = 0; i < 300; i++) assert(*w.find(i) == i * 3);
        assert(w.valid() && w.bucket_size(w.bucket(0)) == 300); for (int i = 0; i < 300; i += 3) assert(w.erase(i)); assert(w.size() == 200 && w.find(3) == nullptr && *w.find(4) == 12 && w.valid()); }
    std::cout << "buckets " << buckets0 << " -> " << m.bucket_count() << ", load " << m.load_factor() << "; model: " << mine.size() << " keys in " << mine.bucket_count() << " prime buckets after " << mine.rehashes() << " rehashes" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1)
// Space Complexity: O(n)  (요소마다 노드 할당)
```
## Redis Dictionary 구조
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

// Redis dict: 해시 테이블 2개(ht[0], ht[1]) + 점진적 재해시(incremental rehashing).
// 한 번에 전부 옮기면 큰 테이블에서 서버가 멈추므로, 명령을 처리할 때마다 버킷 1개씩 옮긴다.
// 재해시 중에는 조회가 두 테이블을 모두 보고, 새 키는 ht[1] 에만 넣는다.  채움이 10 % 아래로 떨어지면 줄이는 재해시도 시작한다
// SCAN: 커서를 "마스크 비트를 뒤집은 순서로 1 증가" 시켜 순회한다 — 테이블 크기가 호출 사이에 두 배·절반이 되어도 *처음부터 끝까지 있던 키는 최소 한 번 반환* 된다(중복은 있을 수 있음)
// 검증: ① 원래 예(재해시 중에도 모든 키 조회, 조회만으로 재해시 완료)  ② std::map 과 60 000 번 대조(set/get/del)하고 불변식(모든 항목이 자기 테이블의 올바른 버킷, rehashidx 앞쪽 버킷은 비어 있음, 재해시 중이 아니면 ht[1] 비어 있음),
//        늘리기·줄이기 재해시가 모두 완료됨, 한 단계가 옮긴 항목 수가 작음  ③ 변경 없는 SCAN 은 모든 키를 *정확히 한 번*  ④ SCAN 도중 삽입·삭제·재해시가 일어나도(300 회) 끝까지 살아 있던 키는 모두 반환
class Dict {
    struct Entry { std::string key; int val; Entry* next; };
    struct Table { std::vector<Entry*> t; size_t used = 0; };
    Table ht[2];
    long rehashidx = -1;
    size_t maxMoved_ = 0, finished_ = 0, grows_ = 0, shrinks_ = 0;
    static size_t hash(const std::string& k) { size_t h = 1469598103934665603ULL; for (unsigned char c : k) { h ^= c; h *= 1099511628211ULL; } return h; }
    bool rehashing() const { return rehashidx != -1; }
    void rehashStep() {
        if (!rehashing()) return;
        int emptyVisits = 10;
        while (ht[0].used > 0 && !ht[0].t[rehashidx]) { rehashidx++; if (--emptyVisits == 0) return; }
        if (ht[0].used > 0) {
            Entry* e = ht[0].t[rehashidx]; size_t moved = 0;
            while (e) {
                Entry* nx = e->next;
                size_t i = hash(e->key) % ht[1].t.size();
                e->next = ht[1].t[i]; ht[1].t[i] = e;
                ht[0].used--; ht[1].used++; ++moved;
                e = nx;
            }
            ht[0].t[rehashidx++] = nullptr; maxMoved_ = std::max(maxMoved_, moved);
        }
        if (ht[0].used == 0) { ht[0] = std::move(ht[1]); ht[1] = Table(); rehashidx = -1; ++finished_; }   // 재해시 완료: 테이블 교체
    }
    Entry* findIn(int which, const std::string& k) const {
        if (ht[which].t.empty()) return nullptr;
        for (Entry* e = ht[which].t[hash(k) % ht[which].t.size()]; e; e = e->next) if (e->key == k) return e;
        return nullptr;
    }
    void startRehash(size_t n) { ht[1].t.assign(n, nullptr); rehashidx = 0; }
    static size_t rev(size_t v) { size_t r = 0; for (int i = 0; i < 64; i++) { r = (r << 1) | (v & 1); v >>= 1; } return r; }
    static size_t advance(size_t v, size_t mask) { v |= ~mask; v = rev(v); v++; return rev(v); }         // 마스크 밖의 비트를 모두 1 로 채워, 뒤집어 1 을 더하고 다시 뒤집는다
public:
    Dict() { ht[0].t.assign(4, nullptr); }
    ~Dict() { for (auto& tb : ht) for (Entry* e : tb.t) while (e) { Entry* n = e->next; delete e; e = n; } }
    Dict(const Dict&) = delete; Dict& operator=(const Dict&) = delete;
    bool wasRehashing = false;
    void set(const std::string& k, int v) {
        rehashStep();
        if (Entry* e = findIn(0, k)) { e->val = v; return; }
        if (Entry* e = findIn(1, k)) { e->val = v; return; }
        if (!rehashing() && ht[0].used >= ht[0].t.size()) {         // 적재율 1 이상이면 2배 이상으로 확장 시작
            size_t n = 4; while (n < ht[0].used * 2) n <<= 1;
            startRehash(n); ++grows_;
        }
        wasRehashing = wasRehashing || rehashing();
        Table& t = rehashing() ? ht[1] : ht[0];
        size_t i = hash(k) % t.t.size();
        t.t[i] = new Entry{k, v, t.t[i]};
        t.used++;
    }
    bool get(const std::string& k, int& v) {
        rehashStep();
        Entry* e = findIn(0, k); if (!e) e = findIn(1, k);
        if (!e) return false; v = e->val; return true;
    }
    bool del(const std::string& k) {
        rehashStep();
        for (int which = 0; which < 2; which++) {
            if (ht[which].t.empty()) continue;
            Entry** pp = &ht[which].t[hash(k) % ht[which].t.size()];
            while (*pp) { if ((*pp)->key == k) { Entry* d = *pp; *pp = d->next; delete d; ht[which].used--; if (!rehashing() && ht[0].t.size() > 4 && ht[0].used * 10 < ht[0].t.size()) { size_t n = 4; while (n < ht[0].used) n <<= 1; if (n < ht[0].t.size()) { startRehash(n); ++shrinks_; } } return true; } pp = &(*pp)->next; }
        }
        return false;
    }
    template <class F> size_t scan(size_t cursor, F emit) const {           // 커서 하나로 버킷 하나(재해시 중이면 작은 테이블의 한 버킷과 큰 테이블의 대응 버킷들)
        if (size() == 0) return 0;
        auto visit = [&](const Table& t, size_t idx) { for (Entry* e = t.t[idx]; e; e = e->next) emit(e->key); };
        if (!rehashing()) { size_t m0 = ht[0].t.size() - 1; visit(ht[0], cursor & m0); return advance(cursor, m0); }
        const Table* small = &ht[0]; const Table* big = &ht[1]; if (small->t.size() > big->t.size()) std::swap(small, big);
        size_t m0 = small->t.size() - 1, m1 = big->t.size() - 1; visit(*small, cursor & m0);
        do { visit(*big, cursor & m1); cursor = advance(cursor, m1); } while (cursor & (m0 ^ m1));
        return cursor;
    }
    bool isRehashing() const { return rehashing(); }
    size_t size() const { return ht[0].used + ht[1].used; }
    size_t maxMoved() const { return maxMoved_; }
    size_t finished() const { return finished_; }
    size_t grows() const { return grows_; }
    size_t shrinks() const { return shrinks_; }
    size_t tableSize(int which) const { return ht[which].t.size(); }
    bool valid() const {
        size_t counted[2] = {0, 0};
        for (int w = 0; w < 2; w++) for (size_t b = 0; b < ht[w].t.size(); b++) for (Entry* e = ht[w].t[b]; e; e = e->next) { if (hash(e->key) % ht[w].t.size() != b) return false; ++counted[w]; if (w == 0 && rehashing() && (long)b < rehashidx) return false; }
        if (counted[0] != ht[0].used || counted[1] != ht[1].used) return false;
        if (!rehashing() && (!ht[1].t.empty() || ht[1].used != 0)) return false;
        return true;
    }
};

int main() {
    Dict d;
    for (int i = 0; i < 2000; i++) {
        d.set("key" + std::to_string(i), i);
        int v;
        if (i % 50 == 0) for (int j = 0; j <= i; j += 37) assert(d.get("key" + std::to_string(j), v) && v == j);   // 재해시 도중에도 모든 키 조회 가능
    }
    assert(d.wasRehashing && d.size() == 2000);
    int v;
    for (int i = 0; i < 100 && d.isRehashing(); i++) d.get("key0", v);       // 조회만으로도 재해시가 진행·완료된다
    assert(!d.isRehashing());
    for (int i = 0; i < 2000; i++) assert(d.get("key" + std::to_string(i), v) && v == i);
    // ② std::map 대조
    std::mt19937 rng(8); Dict dd; std::map<std::string, int> ref; long rehashingOps = 0;
    for (int step = 0; step < 60000; ++step) {
        std::string k = "k" + std::to_string(rng() % (step < 20000 ? 5000 : step < 40000 ? 600 : 40)); int op = (int)(rng() % 10);          // 커졌다가(앞 구간) 줄어든다(뒤 구간)
        if (op < (step < 20000 ? 6 : 3)) { dd.set(k, step); ref[k] = step; } else if (op < 8) { assert(dd.del(k) == (ref.erase(k) > 0)); } else { int val; bool f = dd.get(k, val); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || val == it->second)); }
        assert(dd.size() == ref.size()); rehashingOps += dd.isRehashing(); if (step % 200 == 0) assert(dd.valid());
    }
    assert(dd.valid() && dd.finished() >= 8 && dd.grows() >= 4 && rehashingOps > 1000 && dd.maxMoved() < 20);
    {   std::vector<std::string> ks; for (auto& kv : ref) ks.push_back(kv.first); std::shuffle(ks.begin(), ks.end(), rng);          // 전부 지우면 채움이 10 % 아래로 떨어져 줄이는 재해시가 일어난다
        for (size_t i = 0; i < ks.size(); i++) { assert(dd.del(ks[i])); ref.erase(ks[i]); int val; if (i % 3 == 0) dd.get("k0", val); assert(dd.size() == ref.size()); if (i % 200 == 0) assert(dd.valid()); }
        for (int i = 0; i < 100 && dd.isRehashing(); i++) { int val; dd.get("none", val); }
        assert(dd.size() == 0 && dd.shrinks() >= 3 && dd.tableSize(0) == 4 && dd.valid()); }
    // ③ 변경 없는 SCAN: 정확히 한 번씩
    for (int size : {1, 5, 50, 1000}) {
        Dict s; for (int i = 0; i < size; i++) s.set("s" + std::to_string(i), i);
        std::map<std::string, int> seen; size_t cur = 0; int calls = 0; do { cur = s.scan(cur, [&](const std::string& key) { seen[key]++; }); ++calls; } while (cur != 0 && calls < 100000);
        assert(cur == 0 && (int)seen.size() == size); for (auto& kv : seen) assert(kv.second == 1 || s.isRehashing());                 // 재해시 중이면 같은 키가 두 번 나올 수도 있다
    }
    // ④ SCAN 도중에 삽입·삭제·재해시.  방식 0: 삽입 위주(표가 커짐)  1: 섞기  2: 삭제 위주  3: 스캔 전에 95 % 삭제(줄이는 재해시가 진행 중)  4: 스캔 중간에 원래 키의 85 % 를 한꺼번에 삭제
    long scans = 0, stableTotal = 0, duplicates = 0, shrinkDuringScan = 0;
    for (int trial = 0; trial < 300; trial++) {
        Dict s; std::set<std::string> present, fresh; int n0 = 20 + (int)(rng() % 400); int mode = trial % 5;
        std::vector<std::string> originals; for (int i = 0; i < n0; i++) { std::string k = "a" + std::to_string(i); s.set(k, i); present.insert(k); originals.push_back(k); }
        std::set<std::string> stable = present;                                           // 스캔 내내 있었던 키
        auto removeKey = [&](const std::string& k) { s.del(k); present.erase(k); fresh.erase(k); stable.erase(k); };
        if (mode == 3) { std::vector<std::string> v = originals; std::shuffle(v.begin(), v.end(), rng); for (size_t i = 0; i < v.size() * 95 / 100; i++) removeKey(v[i]); }
        std::map<std::string, int> returned; size_t cur = 0; int created = 0, calls = 0, origDeleted = 0;
        do {
            cur = s.scan(cur, [&](const std::string& key) { returned[key]++; }); ++calls;
            if (mode == 4 && calls == 3) { std::vector<std::string> v = originals; std::shuffle(v.begin(), v.end(), rng); for (size_t i = 0; i < v.size() * 85 / 100; i++) removeKey(v[i]); }
            int muts = 1 + (int)(rng() % 12);
            for (int q = 0; q < muts; q++) {
                bool ins = (mode == 0 ? rng() % 10 < 8 : mode == 1 ? rng() % 2 : mode == 2 ? rng() % 10 < 1 : rng() % 10 < 2) && created < 4 * n0 + 20;        // 새 키는 시작 크기의 4 배까지만 (끝없이 커지는 표는 SCAN 이 끝나지 않을 수 있다)
                if (ins) { std::string k = "n" + std::to_string(created++); s.set(k, 0); present.insert(k); fresh.insert(k); }
                else if (rng() % 10 < 7 && !fresh.empty()) { auto it = fresh.begin(); std::advance(it, rng() % fresh.size()); std::string k = *it; removeKey(k); }       // 새로 넣은 키를 지운다
                else if (mode == 2 && origDeleted < n0 / 3 && !stable.empty()) { auto it = stable.begin(); std::advance(it, rng() % stable.size()); std::string k = *it; removeKey(k); ++origDeleted; }      // 원래 키는 일부만 지운다
                if (rng() % 3 == 0) { int val; s.get("a0", val); }                      // 조회로도 재해시가 진행된다
            }
        } while (cur != 0 && calls < 200000);
        assert(cur == 0 && s.valid());
        for (const std::string& k : stable) assert(returned.count(k));                   // 처음부터 끝까지 있던 키는 빠짐없이 반환
        for (auto& kv : returned) duplicates += kv.second > 1; stableTotal += (long)stable.size(); shrinkDuringScan += s.shrinks() > 0; ++scans;
    }
    assert(scans == 300 && stableTotal > 8000 && shrinkDuringScan > 80);
    std::cout << "Redis-style dict: incremental rehash finished, size=" << d.size() << "; " << dd.finished() << " rehashes (" << dd.grows() << " grows, " << dd.shrinks() << " shrinks, at most " << dd.maxMoved() << " entries moved per step); " << scans << " mutating scans (" << shrinkDuringScan << " of them involved a shrinking rehash) never lost a stable key (" << duplicates << " duplicates)" << std::endl;
    return 0;
}
// Time Complexity: 연산당 O(1) + 재해시 1버킷 분할상환
// Space Complexity: 재해시 중 최대 두 테이블
```
## LRUCache()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <deque>
#include <functional>
#include <iostream>
#include <random>
#include <set>
#include <unordered_map>
#include <utility>
#include <vector>

// LRU 캐시: 해시맵(키 → 노드) + 이중 연결 리스트(최근 사용 순). get/put/erase 모두 O(1). 노드는 배열에 두고 인덱스로 잇는다(할당 없는 재사용).
template <class K, class V> class LRUCache {
    struct Node { K key; V val; int prev, next; };
    std::vector<Node> nodes; std::vector<int> freeList; std::unordered_map<K, int> pos; int head = -1, tail = -1; std::size_t cap;   // head = 가장 최근, tail = 가장 오래
    void unlink(int i) { Node& n = nodes[i]; (n.prev == -1 ? head : nodes[n.prev].next) = n.next; (n.next == -1 ? tail : nodes[n.next].prev) = n.prev; }
    void pushFront(int i) { Node& n = nodes[i]; n.prev = -1; n.next = head; if (head != -1) nodes[head].prev = i; head = i; if (tail == -1) tail = i; }
    void evictOne() { int i = tail; if (onEvict) onEvict(nodes[i].key, nodes[i].val); unlink(i); pos.erase(nodes[i].key); freeList.push_back(i); }
public:
    std::function<void(const K&, const V&)> onEvict;                    // 용량 때문에 퇴출될 때만 불린다 (erase 로 지운 항목은 아님)
    explicit LRUCache(std::size_t c) : cap(c) {}
    std::size_t size() const { return pos.size(); }
    V* get(const K& k) { auto it = pos.find(k); if (it == pos.end()) return nullptr; unlink(it->second); pushFront(it->second); return &nodes[it->second].val; }
    const V* peek(const K& k) const { auto it = pos.find(k); return it == pos.end() ? nullptr : &nodes[it->second].val; }     // 순서를 바꾸지 않는 조회
    void put(const K& k, const V& v) {
        if (cap == 0) return;                                           // 용량 0: 아무것도 저장하지 않는다
        auto it = pos.find(k); if (it != pos.end()) { nodes[it->second].val = v; unlink(it->second); pushFront(it->second); return; }
        if (pos.size() == cap) evictOne();
        int i; if (!freeList.empty()) { i = freeList.back(); freeList.pop_back(); nodes[i].key = k; nodes[i].val = v; } else { nodes.push_back({k, v, -1, -1}); i = (int)nodes.size() - 1; }
        pushFront(i); pos[k] = i;
    }
    bool erase(const K& k) { auto it = pos.find(k); if (it == pos.end()) return false; int i = it->second; unlink(i); freeList.push_back(i); pos.erase(it); return true; }
    void resize(std::size_t c) { cap = c; while (pos.size() > cap) evictOne(); }
    std::vector<K> order() const { std::vector<K> r; for (int i = head; i != -1; i = nodes[i].next) r.push_back(nodes[i].key); return r; }     // 최근 → 오래
    bool check() const {
        std::size_t c = 0; int prev = -1; for (int i = head; i != -1; prev = i, i = nodes[i].next) { if (nodes[i].prev != prev) return false; auto it = pos.find(nodes[i].key); if (it == pos.end() || it->second != i) return false; if (++c > pos.size()) return false; }
        return c == pos.size() && prev == tail && pos.size() <= cap && freeList.size() + pos.size() == nodes.size();
    }
};

struct Naive {                                                          // 오라클: 벡터를 통째로 훑는 O(n) LRU
    std::vector<std::pair<int, int>> v; std::size_t cap; std::vector<int> evicted;                // v.front() = 가장 최근
    explicit Naive(std::size_t c) : cap(c) {}
    int idx(int k) const { for (std::size_t i = 0; i < v.size(); ++i) if (v[i].first == k) return (int)i; return -1; }
    int* get(int k) { int i = idx(k); if (i < 0) return nullptr; auto e = v[i]; v.erase(v.begin() + i); v.insert(v.begin(), e); return &v[0].second; }
    void put(int k, int x) { if (cap == 0) return; int i = idx(k); if (i >= 0) v.erase(v.begin() + i); else if (v.size() == cap) { evicted.push_back(v.back().first); v.pop_back(); } v.insert(v.begin(), {k, x}); }
    bool erase(int k) { int i = idx(k); if (i < 0) return false; v.erase(v.begin() + i); return true; }
    void resize(std::size_t c) { cap = c; while (v.size() > cap) { evicted.push_back(v.back().first); v.pop_back(); } }
};

// 정책 비교용: 적중 횟수를 세는 시뮬레이터들
long lruHits(const std::vector<int>& t, std::size_t cap) { LRUCache<int, int> c(cap); long h = 0; for (std::size_t i = 0; i < t.size(); ++i) { if (c.get(t[i])) ++h; else c.put(t[i], (int)i); } return h; }
long fifoHits(const std::vector<int>& t, std::size_t cap) { std::deque<int> q; std::set<int> in; long h = 0; for (int k : t) { if (in.count(k)) { ++h; continue; } if (q.size() == cap) { in.erase(q.front()); q.pop_front(); } q.push_back(k); in.insert(k); } return h; }
long optHits(const std::vector<int>& t, std::size_t cap) {              // Belady: 다음 사용이 가장 먼 것을 퇴출 (오프라인 최적)
    const int n = (int)t.size(); std::vector<int> nxt(n); std::unordered_map<int, int> last; for (int i = n - 1; i >= 0; --i) { auto it = last.find(t[i]); nxt[i] = it == last.end() ? n + i : it->second; last[t[i]] = i; }
    std::set<std::pair<int, int>> byNext; std::unordered_map<int, int> cur; long h = 0;
    for (int i = 0; i < n; ++i) {
        auto it = cur.find(t[i]);
        if (it != cur.end()) { ++h; byNext.erase({it->second, t[i]}); }
        else if (cur.size() == cap) { auto far = std::prev(byNext.end()); cur.erase(far->second); byNext.erase(far); }
        cur[t[i]] = nxt[i]; byNext.insert({nxt[i], t[i]});
    }
    return h;
}
// 마타슨 스택 거리: 한 번의 패스로 모든 용량의 LRU 적중 수를 구한다 (펜윅 트리)
std::vector<long> stackDistanceHist(const std::vector<int>& t) {
    int n = (int)t.size(); std::vector<int> bit(n + 2, 0); auto add = [&](int i, int d) { for (++i; i <= n + 1; i += i & -i) bit[i] += d; }; auto sum = [&](int i) { int s = 0; for (++i; i > 0; i -= i & -i) s += bit[i]; return s; };
    std::unordered_map<int, int> last; std::vector<long> hist(n + 2, 0);
    for (int i = 0; i < n; ++i) { auto it = last.find(t[i]); if (it != last.end()) { ++hist[sum(i) - sum(it->second) + 1]; add(it->second, -1); } add(i, 1); last[t[i]] = i; }
    return hist;                                                         // hist[d] = 스택 거리가 d 인 재접근 수 (d 는 1 이상)
}

int main() {
    // ① 원래 예
    {   LRUCache<int, int> c(2); c.put(1, 1); c.put(2, 2); assert(*c.get(1) == 1); c.put(3, 3); assert(!c.get(2)); c.put(4, 4); assert(!c.get(1) && *c.get(3) == 3 && *c.get(4) == 4); }
    // ② 무작위 작업열 vs 순진한 모델: get / put / erase / peek / resize, 용량 0·1 포함, 퇴출 순서까지 대조
    std::mt19937 rng(21);
    for (int round = 0; round < 40; ++round) {
        std::size_t cap = rng() % 12; LRUCache<int, int> c(cap); Naive m(cap); std::vector<int> ev; c.onEvict = [&](const int& k, const int&) { ev.push_back(k); };
        for (int op = 0; op < 3000; ++op) {
            int k = rng() % 30, t = rng() % 10;
            if (t < 4) { int* a = c.get(k); int* b = m.get(k); assert((a == nullptr) == (b == nullptr) && (!a || *a == *b)); }
            else if (t < 7) { c.put(k, op); m.put(k, op); }
            else if (t == 7) { assert(c.erase(k) == m.erase(k)); }
            else if (t == 8) { const int* a = c.peek(k); int i = m.idx(k); assert((a != nullptr) == (i >= 0) && (!a || *a == m.v[i].second)); }
            else { std::size_t nc = rng() % 14; c.resize(nc); m.resize(nc); }
            std::vector<int> want; for (auto& e : m.v) want.push_back(e.first); assert(c.order() == want && c.check() && ev == m.evicted);
        }
    }
    // ③ 정책 비교: 스택 거리 오라클 = 직접 시뮬레이션, OPT ≥ LRU, FIFO 의 Belady 이상 현상
    auto zipfTrace = [&](int n, int keys) { std::vector<int> t(n); for (int& x : t) x = (int)std::exp(std::uniform_real_distribution<double>(0, std::log((double)keys))(rng)); return t; };   // 순위 r 의 확률 ∝ 1/r
    for (int rep = 0; rep < 6; ++rep) {
        std::vector<int> t = zipfTrace(20000, 300 + 200 * rep); std::vector<long> hist = stackDistanceHist(t); long prefix = 0; std::size_t c = 0;
        for (std::size_t cap : {1u, 2u, 5u, 10u, 40u, 100u, 300u}) { while (c < cap) prefix += hist[++c]; assert(lruHits(t, cap) == prefix); assert(optHits(t, cap) >= lruHits(t, cap)); }
    }
    {   std::vector<int> t = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};                       // 교과서의 FIFO 이상 현상 예
        assert((long)t.size() - fifoHits(t, 3) == 9 && (long)t.size() - fifoHits(t, 4) == 10);            // 프레임을 늘렸더니 오히려 폴트가 늘었다
        assert((long)t.size() - lruHits(t, 3) == 10 && (long)t.size() - lruHits(t, 4) == 8);              // LRU 는 스택 알고리즘이라 이런 일이 없다
        for (int rep = 0; rep < 30; ++rep) { std::vector<int> r(400); for (int& x : r) x = rng() % 12; long prev = -1; for (std::size_t cap = 1; cap <= 12; ++cap) { long h = lruHits(r, cap); assert(h >= prev); prev = h; } }   // 용량이 늘면 적중은 줄지 않는다
    }
    {   const int cap = 100; std::vector<int> loop; for (int i = 0; i < 20000; ++i) loop.push_back(i % (cap + 1));     // 용량보다 1 큰 순환: LRU 는 영원히 직전에 쫓아낸 것을 다시 찾는다
        long lru = lruHits(loop, cap), opt = optHits(loop, cap); assert(lru == 0 && opt > 19000);
        std::vector<int> scan; for (int round = 0; round < 3; ++round) { for (int pass = 0; pass < 20; ++pass) for (int h = 0; h < 50; ++h) scan.push_back(h); for (int x = 0; x < 1000; ++x) scan.push_back(100000 + round * 1000 + x); }   // 핫셋 50 개 20 바퀴 + 일회성 스캔 1000 개
        LRUCache<int, int> c(cap); long firstPass = 0, secondPass = 0, total = 0;
        for (std::size_t i = 0; i < scan.size(); ++i) { bool hit = c.get(scan[i]) != nullptr; if (!hit) c.put(scan[i], 0); total += hit; std::size_t off = i % 2000; if (off < 50) firstPass += hit; else if (off < 100) secondPass += hit; }
        assert(firstPass == 0 && secondPass == 3 * 50 && total == 3 * 950);          // 스캔이 지나가면 핫셋이 통째로 밀려나 첫 바퀴는 전부 미스 (스캔 오염), 이후 바퀴는 전부 적중
        std::cout << "LRUCache: loop of 101 pages with 100 slots: LRU " << lru << " hits vs OPT " << opt << " of " << loop.size() << std::endl;
    }
    // ④ 큰 입력: 100 만 번 접근, 용량 1 만 — 직접 시뮬레이션 적중 수 == 스택 거리 오라클
    {   std::vector<int> t = zipfTrace(1000000, 200000); std::vector<long> hist = stackDistanceHist(t); long expect = 0; for (int d = 1; d <= 10000; ++d) expect += hist[d];
        assert(lruHits(t, 10000) == expect);
    }
    return 0;
}
// Time Complexity: get/put/erase O(1) 기대, 스택 거리 오라클은 O(n log n)
// Space Complexity: O(capacity)
```
## LFUCache()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <vector>

// LFU 캐시: 가장 적게 사용된 항목을 퇴출하고, 사용 횟수가 같으면 가장 오래된 것을 퇴출한다. 모든 연산 O(1)  (Shah–Mitra–Matani 의 구조)
// 빈도 노드의 이중 연결 리스트(빈도 오름차순) × 각 빈도 노드 안에 항목의 이중 연결 리스트(최근이 앞).  접근하면 항목을 다음 빈도 노드로 옮긴다(없으면 새로 끼워 넣음) — 해시, 정렬, 힙이 필요 없다
// 키 -> 항목은 체이닝 해시 표(직접 구현).  빈도 최솟값 = 빈도 리스트의 첫 노드 (별도의 minFreq 변수가 필요 없다)
// 검증: ① 손으로 짠 예  ② 단순 모델(항목마다 {빈도, 마지막 사용 시각}, 퇴출은 선형 탐색)과 용량 0~8 에서 100 000 번씩 대조: get 결과, 퇴출된 키의 순서까지 일치, 불변식(빈도 리스트 순증가·비어 있는 빈도 노드 없음·크기·해시 도달성)
//        ③ 한계: 한때 인기 있던 항목이 영영 남는 "오염"(LFU) — 작업 집합이 바뀌는 부하에서 같은 용량의 LRU 보다 적중률이 낮다  ④ 고정된 지프 분포 부하에서는 LFU 의 적중률이 LRU 보다 높다
class LFUCache {
    struct FreqNode;
    struct Item { int key, val; FreqNode* fl; Item *prev, *next, *hnext; };
    struct FreqNode { long freq; Item *head = nullptr, *tail = nullptr; FreqNode *prev = nullptr, *next = nullptr; };
    size_t cap, n = 0; FreqNode* first = nullptr; std::vector<Item*> table;
    size_t idx(int k) const { return (size_t)((unsigned)k * 2654435761u) % table.size(); }
    Item* lookup(int k) const { for (Item* p = table[idx(k)]; p; p = p->hnext) if (p->key == k) return p; return nullptr; }
    void pushFront(FreqNode* f, Item* it) { it->fl = f; it->prev = nullptr; it->next = f->head; if (f->head) f->head->prev = it; else f->tail = it; f->head = it; }
    void unlinkItem(Item* it) {                                    // 항목을 빈도 노드에서 떼고, 빈도 노드가 비면 빈도 리스트에서도 뗀다
        FreqNode* f = it->fl;
        if (it->prev) it->prev->next = it->next; else f->head = it->next;
        if (it->next) it->next->prev = it->prev; else f->tail = it->prev;
        if (!f->head) { if (f->prev) f->prev->next = f->next; else first = f->next; if (f->next) f->next->prev = f->prev; delete f; }
    }
    FreqNode* freqNodeAfter(FreqNode* f, long freq) {              // f 바로 뒤에 빈도 freq 노드가 있으면 그것을, 없으면 새로 끼운다 (f == nullptr 이면 리스트 맨 앞)
        FreqNode* nxt = f ? f->next : first;
        if (nxt && nxt->freq == freq) return nxt;
        FreqNode* nf = new FreqNode(); nf->freq = freq; nf->prev = f; nf->next = nxt; if (nxt) nxt->prev = nf; if (f) f->next = nf; else first = nf; return nf;
    }
    void touch(Item* it) {
        FreqNode* old = it->fl; long f = old->freq + 1;
        FreqNode* target = freqNodeAfter(old, f);                  // old 가 비어 지워지기 전에 대상 노드를 확보
        unlinkItemKeepFreq(it); pushFront(target, it);
        if (!old->head) { if (old->prev) old->prev->next = old->next; else first = old->next; if (old->next) old->next->prev = old->prev; delete old; }
    }
    void unlinkItemKeepFreq(Item* it) { FreqNode* f = it->fl; if (it->prev) it->prev->next = it->next; else f->head = it->next; if (it->next) it->next->prev = it->prev; else f->tail = it->prev; }
public:
    std::vector<int> evicted;                                      // 퇴출된 키의 기록 (검증용)
    explicit LFUCache(size_t c) : cap(c), table(64, nullptr) {}
    ~LFUCache() { for (FreqNode* f = first; f;) { FreqNode* nf = f->next; for (Item* p = f->head; p;) { Item* nx = p->next; delete p; p = nx; } delete f; f = nf; } }
    LFUCache(const LFUCache&) = delete; LFUCache& operator=(const LFUCache&) = delete;
    int get(int k) { Item* it = lookup(k); if (!it) return -1; touch(it); return it->val; }
    void put(int k, int v) {
        if (cap == 0) return;
        if (Item* it = lookup(k)) { it->val = v; touch(it); return; }
        if (n == cap) {                                            // 첫 빈도 노드(최소 빈도)의 꼬리 = 가장 오래된 항목 퇴출
            Item* victim = first->tail; evicted.push_back(victim->key);
            Item** pp = &table[idx(victim->key)]; while (*pp != victim) pp = &(*pp)->hnext; *pp = victim->hnext;
            unlinkItem(victim); delete victim; --n;
        }
        FreqNode* f = freqNodeAfter(nullptr, 1);
        Item* it = new Item{k, v, f, nullptr, nullptr, nullptr}; pushFront(f, it); it->hnext = table[idx(k)]; table[idx(k)] = it; ++n;
    }
    size_t size() const { return n; }
    bool valid() const {
        size_t counted = 0; long prevFreq = 0;
        for (FreqNode* f = first; f; f = f->next) {
            if (f->freq <= prevFreq || !f->head || (f->prev && f->prev->next != f) || (!f->prev && f != first)) return false; prevFreq = f->freq;
            for (Item* p = f->head; p; p = p->next) { ++counted; if (p->fl != f || (p->next && p->next->prev != p) || lookup(p->key) != p) return false; }
        }
        return counted == n && n <= cap;
    }
};
struct ModelLFU {                                                  // 모델: 선형 탐색
    struct E { int key, val; long freq, last; }; std::vector<E> v; size_t cap; long tick = 0; std::vector<int> evicted;
    explicit ModelLFU(size_t c) : cap(c) {}
    int find(int k) const { for (size_t i = 0; i < v.size(); i++) if (v[i].key == k) return (int)i; return -1; }
    int get(int k) { int i = find(k); if (i < 0) return -1; v[i].freq++; v[i].last = ++tick; return v[i].val; }
    void put(int k, int val) {
        if (cap == 0) return; int i = find(k);
        if (i >= 0) { v[i].val = val; v[i].freq++; v[i].last = ++tick; return; }
        if (v.size() == cap) { size_t w = 0; for (size_t j = 1; j < v.size(); j++) if (v[j].freq < v[w].freq || (v[j].freq == v[w].freq && v[j].last < v[w].last)) w = j; evicted.push_back(v[w].key); v.erase(v.begin() + (long)w); }
        v.push_back({k, val, 1, ++tick});
    }
};
struct SimpleLRU {                                                 // 비교용 LRU (벡터, 맨 뒤가 최근)
    std::vector<int> keys; size_t cap; explicit SimpleLRU(size_t c) : cap(c) {}
    bool access(int k) { auto it = std::find(keys.begin(), keys.end(), k); bool hit = it != keys.end(); if (hit) keys.erase(it); else if (keys.size() == cap) keys.erase(keys.begin()); keys.push_back(k); return hit; }
};

int main() {
    LFUCache c(2);
    c.put(1, 1); c.put(2, 2);
    assert(c.get(1) == 1);              // 1 의 빈도 2, 2 의 빈도 1
    c.put(3, 3);                        // 빈도가 낮은 2 퇴출
    assert(c.get(2) == -1 && c.get(3) == 3);
    c.put(4, 4);                        // 1(빈도 2), 3(빈도 2) 중 더 오래된 1 퇴출
    assert(c.get(1) == -1 && c.get(3) == 3 && c.get(4) == 4);
    assert((c.evicted == std::vector<int>{2, 1}) && c.valid());
    LFUCache zero(0); zero.put(1, 1); assert(zero.get(1) == -1 && zero.size() == 0 && zero.valid());      // 경계: 용량 0
    LFUCache one(1); one.put(1, 10); one.put(2, 20); assert(one.get(1) == -1 && one.get(2) == 20 && one.valid()); one.put(2, 21); assert(one.get(2) == 21);
    // ② 모델 대조
    std::mt19937 rng(17); long gets = 0, hits = 0;
    for (size_t cap = 0; cap <= 8; cap++) {
        LFUCache real(cap); ModelLFU model(cap);
        for (int step = 0; step < 100000 / 9; ++step) {
            int k = (int)(rng() % 20); int op = (int)(rng() % 10);
            if (op < 5) { real.put(k, step); model.put(k, step); } else { int a = real.get(k), b = model.get(k); assert(a == b); ++gets; hits += a >= 0; }
            assert(real.size() == model.v.size()); if (step % 50 == 0) assert(real.valid());
        }
        assert(real.evicted == model.evicted && real.valid());
    }
    assert(gets > 20000 && hits > 5000);
    // ③ 작업 집합이 바뀌는 부하: 오래된 인기 항목이 영영 남는다
    {   const size_t cap = 10; LFUCache lfu(cap); SimpleLRU lru(cap); long lfuHit = 0, lruHit = 0, total = 0;
        for (int i = 0; i < 2000; i++) { lfu.put(i % 10, i); lfu.get(i % 10); lru.access(i % 10); }                       // 1 단계: 키 0~9 를 아주 많이 쓴다 (빈도 2000 안팎)
        for (int round = 0; round < 3000; round++) {                                                                      // 2 단계: 새 작업 집합 100~109 만 쓴다
            int k = 100 + (int)(rng() % 10); bool lruH = lru.access(k); int got = lfu.get(k); if (got < 0) lfu.put(k, k); else lfuHit++;
            lruHit += lruH; ++total;
        }
        assert(lruHit > total * 9 / 10 && lfuHit < total / 2);                                                            // LRU 는 곧 새 집합으로 갈아타지만 LFU 는 옛 항목이 자리를 차지한다
    }
    // ④ 고정된 지프 분포
    {   const int keys = 1000; const size_t cap = 50; std::vector<double> cum; double s = 0; for (int r = 1; r <= keys; r++) { s += 1.0 / r; cum.push_back(s); }
        LFUCache lfu(cap); SimpleLRU lru(cap); long lfuHit = 0, lruHit = 0; const int N = 60000;
        for (int i = 0; i < N; i++) { double u = std::uniform_real_distribution<double>(0, cum.back())(rng); int k = (int)(std::lower_bound(cum.begin(), cum.end(), u) - cum.begin());
            lruHit += lru.access(k); int g = lfu.get(k); if (g < 0) lfu.put(k, k); else lfuHit++; }
        assert(lfuHit > lruHit && (double)lfuHit / N > 0.35);
        std::cout << "LFUCache verified: hit rates on a static Zipf workload LFU " << (double)lfuHit / N << " vs LRU " << (double)lruHit / N << std::endl; }
    return 0;
}
// Time Complexity: get/put O(1)
// Space Complexity: O(capacity)
```
# Part 11. 보안
## HashDoS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <unordered_set>
#include <vector>

// 해시 플러딩(HashDoS): 해시 함수를 아는 공격자가 전부 같은 해시값(또는 같은 버킷)을 갖는 키만 보내 해시 테이블의 O(1) 을 O(n) 으로, n 번 삽입을 O(n²) 으로 만든다.
// 이 항목은 ① 다항 해시(Java String.hashCode 의 31, djb2 의 33 …)의 충돌 문자열 2^k 개를 만드는 법 ② 그 키로 체인 테이블의 비교 횟수가 정확히 n(n−1)/2 가 됨
// ③ 밑(base)만 무작위로 바꾸는 방어가 Thue–Morse 문자열에 뚫림 ④ 비밀 키 PRF(SipHash)·트리화(Java 8 TreeBin)가 어떻게 막는지를 비교 횟수로 보인다.
typedef std::uint32_t u32; typedef std::uint64_t u64;
struct Poly {                                                           // h = h·B + c  (mod 2^32).  B = 31 이 Java 의 String.hashCode, 33 이 djb2
    u32 B; u32 operator()(const std::string& s) const { u32 h = 0; for (unsigned char c : s) h = h * B + c; return h; }
};
struct Sip {                                                            // SipHash-2-4: 비밀 키 (k0, k1) 를 모르면 충돌을 미리 만들 수 없다
    u64 k0, k1;
    static u64 rotl(u64 x, int b) { return (x << b) | (x >> (64 - b)); }
    u64 hash(const unsigned char* p, std::size_t len) const {
        u64 v0 = k0 ^ 0x736f6d6570736575ULL, v1 = k1 ^ 0x646f72616e646f6dULL, v2 = k0 ^ 0x6c7967656e657261ULL, v3 = k1 ^ 0x7465646279746573ULL;
        auto round = [&] { v0 += v1; v1 = rotl(v1, 13); v1 ^= v0; v0 = rotl(v0, 32); v2 += v3; v3 = rotl(v3, 16); v3 ^= v2; v0 += v3; v3 = rotl(v3, 21); v3 ^= v0; v2 += v1; v1 = rotl(v1, 17); v1 ^= v2; v2 = rotl(v2, 32); };
        std::size_t i = 0; for (; i + 8 <= len; i += 8) { u64 m; std::memcpy(&m, p + i, 8); v3 ^= m; round(); round(); v0 ^= m; }       // 리틀 엔디언 호스트 가정
        u64 b = (u64)len << 56; for (std::size_t j = 0; i + j < len; ++j) b |= (u64)p[i + j] << (8 * j);
        v3 ^= b; round(); round(); v0 ^= b; v2 ^= 0xff; round(); round(); round(); round(); return v0 ^ v1 ^ v2 ^ v3;
    }
    u32 operator()(const std::string& s) const { return (u32)hash((const unsigned char*)s.data(), s.size()); }
};
template <class H> class ChainTable {                                   // 체인 방식 해시 집합 (적재율 1 에서 두 배로 확장). 키 비교 횟수를 센다
    std::vector<std::vector<std::string>> b; std::size_t n = 0; H h;
    void grow() { std::vector<std::vector<std::string>> nb(b.size() * 2); for (auto& c : b) for (auto& s : c) nb[h(s) % nb.size()].push_back(std::move(s)); b.swap(nb); }
public:
    long cmps = 0;
    explicit ChainTable(H hh) : b(16), h(hh) {}
    bool insert(const std::string& s) { auto& c = b[h(s) % b.size()]; for (auto& x : c) { ++cmps; if (x == s) return false; } c.push_back(s); if (++n > b.size()) grow(); return true; }
    bool contains(const std::string& s) { for (auto& x : b[h(s) % b.size()]) { ++cmps; if (x == s) return true; } return false; }
    std::size_t size() const { return n; }
    std::size_t maxChain() const { std::size_t m = 0; for (auto& c : b) m = std::max(m, c.size()); return m; }
};
template <class H> class TreeBinTable {                                 // Java 8 의 TreeBin: 체인이 8 을 넘으면 그 버킷만 균형 트리(비교 가능한 키)로 바꾼다
    struct Cmp { long* c; bool operator()(const std::string& a, const std::string& b) const { ++*c; return a < b; } };
    struct Bin { std::vector<std::string> list; std::unique_ptr<std::set<std::string, Cmp>> tree; };
    std::vector<Bin> b; std::size_t n = 0; H h;
    void grow() { std::vector<Bin> nb(b.size() * 2);
        for (auto& bin : b) { auto move = [&](const std::string& s) { Bin& d = nb[h(s) % nb.size()]; if (d.tree) d.tree->insert(s); else d.list.push_back(s); };
            if (bin.tree) for (auto& s : *bin.tree) move(s); else for (auto& s : bin.list) move(s); }
        for (auto& bin : nb) if (!bin.tree && bin.list.size() > 8) { bin.tree.reset(new std::set<std::string, Cmp>(Cmp{&cmps})); for (auto& s : bin.list) bin.tree->insert(s); bin.list.clear(); }
        b.swap(nb); }
public:
    long cmps = 0;
    explicit TreeBinTable(H hh, std::size_t buckets = 16) : b(buckets), h(hh) {}                   // 버킷 수를 미리 정하면 재해시 비용이 섞이지 않는다
    bool insert(const std::string& s) {
        Bin& bin = b[h(s) % b.size()]; bool added;
        if (bin.tree) added = bin.tree->insert(s).second;
        else { added = true; for (auto& x : bin.list) { ++cmps; if (x == s) { added = false; break; } } if (added) { bin.list.push_back(s); if (bin.list.size() > 8) { bin.tree.reset(new std::set<std::string, Cmp>(Cmp{&cmps})); for (auto& x : bin.list) bin.tree->insert(x); bin.list.clear(); } } }
        if (added && ++n > b.size()) grow(); return added;
    }
    std::size_t size() const { return n; }
};

// 같은 길이 두 블록 (c1, c2) 와 (c1+1, c2−B) 는 c1·B + c2 = (c1+1)·B + (c2−B) 라 해시 기여가 같다 → 블록마다 둘 중 하나를 고르면 2^k 개의 문자열이 모두 같은 해시
std::vector<std::string> collisions(u32 B, int k) {
    char c1 = 'A', c2 = (char)(B + 66);                                 // 블록 0 = (65, B+66), 블록 1 = (66, 66)
    std::vector<std::string> keys = {""};
    for (int i = 0; i < k; ++i) { std::vector<std::string> next; next.reserve(keys.size() * 2); for (auto& s : keys) { next.push_back(s + c1 + c2); next.push_back(s + (char)(c1 + 1) + (char)66); } keys.swap(next); }
    return keys;
}
std::string thueMorse(int len, bool flip) { std::string s(len, 'a'); for (int i = 0; i < len; ++i) s[i] = (__builtin_popcount(i) & 1) != flip ? 'b' : 'a'; return s; }

int main() {
    std::mt19937_64 rng(2025);
    // ① 충돌 문자열: 밑 31(Java)·33(djb2)·37·131 모두 2^10 개가 전부 같은 해시값, 서로 다른 문자열
    for (u32 B : {31u, 33u, 37u, 131u}) { std::vector<std::string> keys = collisions(B, 10); Poly h{B}; std::set<std::string> uniq(keys.begin(), keys.end()); assert(keys.size() == 1024 && uniq.size() == 1024); for (auto& s : keys) assert(h(s) == h(keys[0])); }
    assert(collisions(31, 1)[0] == "Aa" && collisions(31, 1)[1] == "BB");                   // 유명한 "Aa" == "BB"
    // ② 복잡도 공격: 같은 개수의 무작위 키는 비교 약 n 번, 충돌 키는 정확히 n(n−1)/2 번 (테이블 크기를 몰라도 된다)
    long lastAttack = 0;
    for (int k = 8; k <= 13; ++k) {
        long n = 1L << k; std::vector<std::string> bad = collisions(31, k); ChainTable<Poly> atk{Poly{31}}, rnd{Poly{31}};
        for (auto& s : bad) atk.insert(s);
        for (long i = 0; i < n; ++i) { std::string s(12, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); rnd.insert(s); }
        assert(atk.cmps == n * (n - 1) / 2 && atk.maxChain() == (std::size_t)n && rnd.cmps < 2 * n && rnd.maxChain() < 12);
        lastAttack = atk.cmps;
    }
    // ③ 밑만 무작위로 고르는 방어: 충돌 쌍은 밑에 의존하므로 B=31 용 키들은 흩어지지만, Thue–Morse 문자열은 홀수 밑 어느 것에서도 (mod 2^32) 충돌한다
    {   std::vector<std::string> keys = collisions(31, 10); int worst = 0;
        for (int t = 0; t < 20; ++t) { u32 B = (u32)rng() | 1; if (B == 31) continue; std::unordered_set<u32> distinct; Poly h{B}; for (auto& s : keys) distinct.insert(h(s)); worst = std::max(worst, (int)(1024 - distinct.size())); }
        assert(worst < 600);                                            // 대부분 흩어진다 (한 밑이 우연히 많이 겹치는 일은 드물다)
        std::string a = thueMorse(128, false), b = thueMorse(128, true); assert(a != b && a.size() == 128);
        for (int t = 0; t < 200; ++t) { u32 B = (u32)rng() | 1; Poly h{B}; assert(h(a) == h(b)); }   // 길이 2^7 이면 ∏(B^(2^j) − 1) 이 2^32 로 나뉜다
        std::vector<std::string> tm = {""}; for (int i = 0; i < 10; ++i) { std::vector<std::string> next; for (auto& s : tm) { next.push_back(s + a); next.push_back(s + b); } tm.swap(next); }   // 128 글자 블록 2^10 개 조합 = 1024 개
        for (int t = 0; t < 20; ++t) { u32 B = (u32)rng() | 1; Poly h{B}; for (auto& s : tm) assert(h(s) == h(tm[0])); }
        // 비밀 키 PRF 는 이 키들을 흩어 놓는다 (서로 다른 문자열 1024 개가 거의 모두 다른 해시값)
        Sip sip{rng(), rng()}; std::unordered_set<u32> distinct; for (auto& s : tm) distinct.insert(sip(s)); assert(distinct.size() > 1000);
        ChainTable<Sip> t1{sip}; for (auto& s : tm) t1.insert(s); assert(t1.maxChain() < 12);
    }
    // ④ 방어 1: 비밀 키 SipHash — 먼저 시험 벡터로 구현을 확인한 뒤, 같은 충돌 키 2^13 개를 넣어 비교 횟수를 잰다
    {   unsigned char msg[15]; for (int i = 0; i < 15; ++i) msg[i] = (unsigned char)i; Sip ref{0x0706050403020100ULL, 0x0f0e0d0c0b0a0908ULL}; assert(ref.hash(msg, 15) == 0xa129ca6149be45e5ULL && ref.hash(msg, 0) == 0x726fdb47dd0e0e31ULL);
        std::vector<std::string> bad = collisions(31, 13); ChainTable<Sip> keyed{Sip{rng(), rng()}}; for (auto& s : bad) keyed.insert(s);
        long n = 1L << 13; assert(keyed.cmps < 2 * n && keyed.maxChain() < 14 && keyed.size() == (std::size_t)n);
        std::cout << "HashDoS: 2^13 colliding keys cost " << lastAttack << " comparisons in a polynomial-hash table (n(n-1)/2) but " << keyed.cmps << " in a SipHash table; ";
    }
    // ⑤ 방어 2: Java 8 식 트리화 — 해시가 뚫려도 최악이 O(n log n): 충돌 키 2^17 개
    {   long n = 1L << 17; std::vector<std::string> bad = collisions(31, 17); TreeBinTable<Poly> tree(Poly{31}, n); for (auto& s : bad) tree.insert(s);
        assert(tree.size() == (std::size_t)n && tree.cmps < 2 * n * 17 && tree.cmps > n * 10);
        TreeBinTable<Sip> sip(Sip{rng(), rng()}, n); for (auto& s : bad) sip.insert(s); assert(sip.cmps < 2 * n);
        std::cout << "with 2^17 colliding keys the treeified Poly31 table needed " << tree.cmps << " comparisons (n log2 n = " << n * 17 << ") and the SipHash table " << sip.cmps << std::endl;
    }
    // 차분 테스트: 충돌 키와 일반 키를 섞은 무작위 삽입·조회가 std::unordered_set 과 같은 답을 낸다 (세 가지 테이블)
    {   std::vector<std::string> pool = collisions(31, 6); for (int i = 0; i < 100; ++i) pool.push_back("key" + std::to_string(i)); pool.push_back(""); pool.push_back("\xff\xfe");
        ChainTable<Poly> a{Poly{31}}; ChainTable<Sip> b{Sip{rng(), rng()}}; TreeBinTable<Poly> c{Poly{31}}; std::unordered_set<std::string> ref;
        for (int op = 0; op < 20000; ++op) { const std::string& s = pool[rng() % pool.size()];
            if (rng() % 3) { bool r = ref.insert(s).second; assert(a.insert(s) == r && b.insert(s) == r && c.insert(s) == r); } else { bool r = ref.count(s) > 0; assert(a.contains(s) == r && b.contains(s) == r); } }
        assert(a.size() == ref.size() && b.size() == ref.size() && c.size() == ref.size());
    }
    // 테이블 크기를 아는 공격 (키가 정수이고 h(k) = k): 크기의 배수만 보내면 전부 한 버킷
    {   const int m = 1024; std::vector<int> byIdent(m), bySpread(m); for (int i = 0; i < m; ++i) { u32 k = (u32)i * m; ++byIdent[k % m]; ++bySpread[(u32)(Sip{7, 9}.hash((const unsigned char*)&k, 4)) % m]; }
        assert(*std::max_element(byIdent.begin(), byIdent.end()) == m && *std::max_element(bySpread.begin(), bySpread.end()) < 12); }
    return 0;
}
// Time Complexity: 공격 시 삽입 n 개 O(n²), 키 있는 해시 O(n) 기대, 트리화 O(n log n)
// Space Complexity: O(n)
```
## Salting()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

// 솔트(salt): 사용자마다 다른 무작위 값을 비밀번호와 함께 해시한다.
//  - 솔트가 없으면 같은 비밀번호 = 같은 해시 -> 미리 계산한 표(레인보우 테이블)로 한 번에 깨진다
//  - 솔트가 있으면 사용자별로 표를 따로 만들어야 하므로 사전 계산이 무의미해진다
// 여기서는 실제 부품으로 만든다: SHA-256 -> HMAC -> PBKDF2(RFC 8018, 반복으로 계산 비용을 키우는 key stretching) -> "pbkdf2-sha256$반복$솔트$해시" 저장 형식과 상수 시간 검증
// (더 나은 선택은 메모리도 쓰는 scrypt/Argon2 이다.)
// 검증: ① PBKDF2-HMAC-SHA256 의 공개 시험 벡터(반복 1·2·4096, 40 바이트 출력, NUL 이 든 입력 — 파이썬 hashlib.pbkdf2_hmac 으로 확인한 값)  ② 사용자 60 명이 사전 100 개 단어에서 비밀번호를 고른 시스템:
//        솔트 없는 SHA-256 은 중복 해시가 생기고 사전 표 하나로 전원이 깨지며, 솔트+PBKDF2 는 해시가 모두 다르고 표가 통하지 않고 사용자별로 사전을 다시 돌려야 해서 압축 호출 수가 수만 배  ③ 반복 횟수에 비례하는 비용(압축 호출 수의 선형성)
//        ④ 저장 형식 왕복과 검증: 맞는 비밀번호만 통과, 반복·솔트·해시를 바꾸거나 형식이 깨지면 거부(예외 없음)  ⑤ 상수 시간 비교의 단계 수가 불일치 위치와 무관
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
long g_compress = 0;                                                  // SHA-256 압축 함수 호출 수 (비용 측정)
struct Consts {
    uint32_t K[64], H0[8];
    Consts() {
        std::vector<uint32_t> primes;
        for (uint32_t p = 2; primes.size() < 64; p++) { bool ok = true; for (uint32_t q : primes) if (p % q == 0) { ok = false; break; } if (ok) primes.push_back(p); }
        for (int i = 0; i < 64; i++) { long double c = cbrtl((long double)primes[i]); K[i] = (uint32_t)((c - floorl(c)) * 4294967296.0L); }
        for (int i = 0; i < 8; i++)  { long double s = sqrtl((long double)primes[i]); H0[i] = (uint32_t)((s - floorl(s)) * 4294967296.0L); }
    }
};
const Consts& consts() { static const Consts c; return c; }
class Sha256 {
    uint32_t H[8]; uint64_t total = 0; uint8_t buf[64]; size_t blen = 0;
    void block(const uint8_t* p) {
        ++g_compress; uint32_t w[64], K[64]; std::memcpy(K, consts().K, sizeof K);
        for (int i = 0; i < 16; i++) w[i] = (uint32_t)p[4 * i] << 24 | (uint32_t)p[4 * i + 1] << 16 | (uint32_t)p[4 * i + 2] << 8 | p[4 * i + 3];
        for (int i = 16; i < 64; i++) { uint32_t s0 = rotr(w[i-15], 7) ^ rotr(w[i-15], 18) ^ (w[i-15] >> 3), s1 = rotr(w[i-2], 17) ^ rotr(w[i-2], 19) ^ (w[i-2] >> 10); w[i] = w[i-16] + s0 + w[i-7] + s1; }
        uint32_t a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
        for (int i = 0; i < 64; i++) {
            uint32_t t1 = h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i];
            uint32_t t2 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
            h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
        }
        H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
public:
    Sha256() { std::memcpy(H, consts().H0, sizeof H); }
    void update(const uint8_t* p, size_t n) { total += n; while (n) { size_t take = std::min(n, 64 - blen); std::memcpy(buf + blen, p, take); blen += take; p += take; n -= take; if (blen == 64) { block(buf); blen = 0; } } }
    void update(const std::string& m) { update((const uint8_t*)m.data(), m.size()); }
    std::string digest() const {
        Sha256 t = *this; uint64_t bits = total * 8; uint8_t pad = 0x80, z = 0; t.update(&pad, 1); while (t.blen != 56) t.update(&z, 1);
        for (int i = 7; i >= 0; i--) { uint8_t b = (uint8_t)(bits >> (8 * i)); t.update(&b, 1); }
        std::string out; for (int i = 0; i < 8; i++) for (int j = 3; j >= 0; j--) out.push_back((char)((t.H[i] >> (8 * j)) & 0xff));
        return out;
    }
};
std::string hex(const std::string& d) { static const char* h = "0123456789abcdef"; std::string r; for (unsigned char c : d) { r += h[c >> 4]; r += h[c & 15]; } return r; }
bool fromHex(const std::string& h, std::string& out) {                   // 잘못된 16 진 문자열은 false
    if (h.size() % 2) return false; out.clear();
    for (size_t i = 0; i < h.size(); i += 2) { int v = 0; for (int k = 0; k < 2; k++) { char c = h[i + k]; int d = c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10 : -1; if (d < 0) return false; v = v * 16 + d; } out.push_back((char)v); }
    return true;
}
std::string sha256raw(const std::string& msg) { Sha256 s; s.update(msg); return s.digest(); }
std::string hmacSha256(std::string key, const std::string& msg) {
    const size_t block = 64; if (key.size() > block) key = sha256raw(key); key.resize(block, '\0');
    std::string ipad(block, 0), opad(block, 0); for (size_t i = 0; i < block; i++) { ipad[i] = key[i] ^ 0x36; opad[i] = key[i] ^ 0x5c; }
    return sha256raw(opad + sha256raw(ipad + msg));
}
std::string be32(uint32_t i) { std::string s(4, 0); for (int k = 0; k < 4; k++) s[k] = (char)((i >> (24 - 8 * k)) & 0xff); return s; }
std::string pbkdf2(const std::string& password, const std::string& salt, uint32_t iterations, size_t dkLen) {          // RFC 8018: T_i = U_1 ⊕ U_2 ⊕ … ⊕ U_c , U_1 = PRF(P, S || INT(i)), U_j = PRF(P, U_{j-1})
    std::string out;
    for (uint32_t i = 1; out.size() < dkLen; i++) {
        std::string u = hmacSha256(password, salt + be32(i)), t = u;
        for (uint32_t j = 1; j < iterations; j++) { u = hmacSha256(password, u); for (size_t k = 0; k < t.size(); k++) t[k] ^= u[k]; }
        out += t;
    }
    out.resize(dkLen); return out;
}
bool constantTimeEq(const std::string& a, const std::string& b, long* steps = nullptr) {
    size_t n = std::max(a.size(), b.size()); unsigned diff = (unsigned)(a.size() ^ b.size()); long s = 0;
    for (size_t i = 0; i < n; i++) { unsigned char x = i < a.size() ? (unsigned char)a[i] : 0, y = i < b.size() ? (unsigned char)b[i] : 0; diff |= (unsigned)(x ^ y); ++s; }
    if (steps) *steps = s; return diff == 0;
}
std::string makeRecord(const std::string& password, const std::string& salt, uint32_t iterations) { return "pbkdf2-sha256$" + std::to_string(iterations) + "$" + hex(salt) + "$" + hex(pbkdf2(password, salt, iterations, 32)); }
bool verify(const std::string& record, const std::string& password) {                // 형식이 깨졌으면 false (예외 없음)
    std::vector<std::string> parts; std::stringstream ss(record); std::string tok; while (std::getline(ss, tok, '$')) parts.push_back(tok);
    if (parts.size() != 4 || parts[0] != "pbkdf2-sha256" || parts[1].empty() || parts[1].size() > 9 || parts[1].find_first_not_of("0123456789") != std::string::npos) return false;
    uint32_t iters = (uint32_t)std::stoul(parts[1]); std::string salt, want; if (iters == 0 || iters > 1000000 || !fromHex(parts[2], salt) || !fromHex(parts[3], want) || want.size() != 32) return false;
    return constantTimeEq(pbkdf2(password, salt, iters, want.size()), want);
}

int main() {
    // ① 공개 시험 벡터
    assert(hex(pbkdf2("password", "salt", 1, 32)) == "120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b");
    assert(hex(pbkdf2("password", "salt", 2, 32)) == "ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43");
    assert(hex(pbkdf2("password", "salt", 4096, 32)) == "c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a");
    assert(hex(pbkdf2("passwordPASSWORDpassword", "saltSALTsaltSALTsaltSALTsaltSALTsalt", 4096, 40)) == "348c89dbcbd32b2f32d814b8116e84cf2b17347ebc1800181c4e2a1fb8dd53e1c635518c7dac47e9");      // 출력이 한 블록(32 바이트)보다 길다
    assert(hex(pbkdf2(std::string("pass\0word", 9), std::string("sa\0lt", 5), 4096, 16)) == "89b69d0516f829893c696226650a8687");
    // ② 레인보우 표 대 솔트
    std::vector<std::string> dictionary; for (int i = 0; i < 100; i++) dictionary.push_back("pw" + std::to_string(i * 37 % 1000));
    std::mt19937 rng(5); const int users = 60; std::vector<std::string> chosen(users), salts(users);
    for (int u = 0; u < users; u++) { chosen[u] = dictionary[rng() % dictionary.size()]; salts[u].resize(16); for (char& c : salts[u]) c = (char)rng(); }
    g_compress = 0; std::unordered_map<std::string, std::string> rainbow; for (auto& pw : dictionary) rainbow[sha256raw(pw)] = pw;       // 솔트 없는 표: 단어 100 개를 한 번씩만 해시
    long tableCost = g_compress;
    std::set<std::string> plainDistinct; int cracked = 0; for (int u = 0; u < users; u++) { std::string h = sha256raw(chosen[u]); plainDistinct.insert(h); auto it = rainbow.find(h); cracked += it != rainbow.end() && it->second == chosen[u]; }
    assert(cracked == users && (int)plainDistinct.size() < users);                       // 전원이 표 한 번 조회로 노출되고, 같은 비밀번호를 쓴 사용자는 해시가 같다 (서로를 드러낸다)
    const uint32_t ITER = 50; std::vector<std::string> salted(users); std::set<std::string> saltedDistinct; int saltedHits = 0;
    for (int u = 0; u < users; u++) { salted[u] = pbkdf2(chosen[u], salts[u], ITER, 32); saltedDistinct.insert(salted[u]); saltedHits += rainbow.count(salted[u]); }
    assert((int)saltedDistinct.size() == users && saltedHits == 0);                      // 같은 비밀번호도 해시가 모두 다르고, 사전 표로는 한 명도 못 찾는다
    g_compress = 0; int found = 0;                                                       // 솔트를 아는 공격자의 비용: 사용자마다 사전 100 개를 PBKDF2 로 다시 돌려야 한다
    for (int u = 0; u < users; u++) for (auto& guess : dictionary) if (pbkdf2(guess, salts[u], ITER, 32) == salted[u]) { ++found; break; }
    long attackCost = g_compress; assert(found == users && attackCost > 5000 * tableCost / 10 && attackCost / tableCost > 1000);       // 표 만들기 대비 수천 배
    // ③ 비용은 반복 횟수에 비례
    long cost[3]; const uint32_t its[3] = {500, 1000, 2000};
    for (int i = 0; i < 3; i++) { g_compress = 0; pbkdf2("pw", "salt", its[i], 32); cost[i] = g_compress; }
    assert(std::fabs((double)cost[1] / cost[0] - 2.0) < 0.05 && std::fabs((double)cost[2] / cost[1] - 2.0) < 0.05);
    // ④ 저장 형식
    std::string salt = "k3Fq9aZ1x8Lm2PqW", rec = makeRecord("letmein", salt, 1000);
    assert(rec.compare(0, 19, "pbkdf2-sha256$1000$") == 0 && verify(rec, "letmein") && !verify(rec, "wrong") && !verify(rec, "") && !verify(rec, "letmein "));
    std::string tampered = rec; tampered[tampered.size() - 1] = tampered.back() == '0' ? '1' : '0'; assert(!verify(tampered, "letmein"));            // 해시 변조
    std::string fewer = rec; fewer.replace(fewer.find("$1000$"), 6, "$999$"); assert(!verify(fewer, "letmein"));                                       // 반복 횟수 변조
    for (std::string bad : std::vector<std::string>{"", "pbkdf2-sha256", "pbkdf2-sha256$1000$zz$00", "pbkdf2-sha256$0$aa$bb", "pbkdf2-sha256$abc$aa$bb", "md5$1000$aa$bb", "pbkdf2-sha256$1000$aa", "pbkdf2-sha256$9999999999$aa$bb", rec + "$extra"}) assert(!verify(bad, "letmein"));
    assert(makeRecord("letmein", "salt-one", 10) != makeRecord("letmein", "salt-two", 10) && makeRecord("a", "s", 10) == makeRecord("a", "s", 10));        // 솔트가 다르면 레코드가 다르고, 같으면 결정적
    // ⑤ 상수 시간 비교
    std::string h = pbkdf2("x", "y", 1, 32), early = h, late = h; early[0] ^= 1; late[31] ^= 1; long s0, s1, s2;
    assert(constantTimeEq(h, h, &s0) && !constantTimeEq(h, early, &s1) && !constantTimeEq(h, late, &s2) && s0 == 32 && s1 == 32 && s2 == 32);
    std::cout << "salted: " << users << " users, " << plainDistinct.size() << " distinct unsalted hashes (all cracked by one table) vs " << saltedDistinct.size() << " distinct salted hashes (attack cost x" << attackCost / tableCost << ")" << std::endl;
    return 0;
}
// Time Complexity: O(반복 횟수)  (비용을 의도적으로 키움)
// Space Complexity: O(1)
```
# Part 12. 동시성
## ConcurrentHashMap()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <functional>
#include <iostream>
#include <memory>
#include <mutex>
#include <random>
#include <shared_mutex>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>

// 락 스트라이핑 동시성 해시맵: 테이블 전체에 락 하나를 두면 모든 스레드가 직렬화되므로 해시로 나눈 구역(shard)마다 읽기-쓰기 락을 둔다.
//  · 서로 다른 구역에 접근하는 스레드는 기다리지 않고, 같은 구역의 읽기(get)는 동시에 진행한다.  구역 안의 테이블은 구역 락 아래에서 직접 확장한다.
//  · 한 키의 갱신은 compute(k, f) 로 락을 쥔 채 읽고-고치고-쓴다 (get 뒤에 put 을 따로 하면 갱신을 잃는다).
//  · 두 키를 함께 바꾸는 transfer(a, b) 는 구역을 번호 순서로 잠가 교착을 피하고, snapshot 은 모든 구역을 번호 순서로 잠가 일관된 순간을 본다.
static inline std::uint64_t mix(std::uint64_t z) { z += 0x9e3779b97f4a7c15ULL; z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }
template <class K, class V> class ConcurrentMap {
    struct Shard {
        mutable std::shared_mutex mu; std::vector<std::vector<std::pair<K, V>>> b; std::size_t n = 0;                 // 구역마다 체인 테이블 (4 칸에서 시작해 적재율 1 에서 두 배)
        Shard() : b(4) {}
        std::pair<K, V>* find(const K& k, std::uint64_t h) { for (auto& e : b[h % b.size()]) if (e.first == k) return &e; return nullptr; }
        const std::pair<K, V>* find(const K& k, std::uint64_t h) const { for (auto& e : b[h % b.size()]) if (e.first == k) return &e; return nullptr; }
        void add(const K& k, const V& v, std::uint64_t h) { b[h % b.size()].emplace_back(k, v); if (++n > b.size()) grow(); }
        void grow() { std::vector<std::vector<std::pair<K, V>>> nb(b.size() * 2); for (auto& c : b) for (auto& e : c) nb[mix(std::hash<K>()(e.first)) % nb.size()].push_back(std::move(e)); b.swap(nb); }
    };
    std::vector<std::unique_ptr<Shard>> shards;
    static std::uint64_t hashOf(const K& k) { return mix(std::hash<K>()(k)); }
public:
    explicit ConcurrentMap(std::size_t S = 16) { for (std::size_t i = 0; i < S; ++i) shards.emplace_back(new Shard); }
    std::size_t shardOf(const K& k) const { return (hashOf(k) >> 40) % shards.size(); }          // 구역은 높은 비트, 구역 안 버킷은 낮은 비트
    bool get(const K& k, V& out) const { std::uint64_t h = hashOf(k); const Shard& s = *shards[(h >> 40) % shards.size()]; std::shared_lock<std::shared_mutex> g(s.mu); auto* e = s.find(k, h); if (!e) return false; out = e->second; return true; }
    void put(const K& k, const V& v) { std::uint64_t h = hashOf(k); Shard& s = *shards[(h >> 40) % shards.size()]; std::unique_lock<std::shared_mutex> g(s.mu); if (auto* e = s.find(k, h)) e->second = v; else s.add(k, v, h); }
    bool putIfAbsent(const K& k, const V& v) { std::uint64_t h = hashOf(k); Shard& s = *shards[(h >> 40) % shards.size()]; std::unique_lock<std::shared_mutex> g(s.mu); if (s.find(k, h)) return false; s.add(k, v, h); return true; }
    bool erase(const K& k) {
        std::uint64_t h = hashOf(k); Shard& s = *shards[(h >> 40) % shards.size()]; std::unique_lock<std::shared_mutex> g(s.mu); auto& c = s.b[h % s.b.size()];
        for (std::size_t i = 0; i < c.size(); ++i) if (c[i].first == k) { c[i] = std::move(c.back()); c.pop_back(); --s.n; return true; }
        return false;
    }
    template <class F> V compute(const K& k, F f) {                       // 없으면 V() 에서 시작해 f(V&) 로 고친다. 읽기·수정·쓰기가 한 덩어리
        std::uint64_t h = hashOf(k); Shard& s = *shards[(h >> 40) % shards.size()]; std::unique_lock<std::shared_mutex> g(s.mu);
        auto* e = s.find(k, h); if (!e) { s.add(k, V(), h); e = s.find(k, h); } f(e->second); return e->second;
    }
    bool transfer(const K& a, const K& b, V amount) {                     // a 의 잔액이 충분하면 a → b 로 옮긴다 (두 키 모두 이미 있어야 한다)
        std::uint64_t ha = hashOf(a), hb = hashOf(b); std::size_t ia = (ha >> 40) % shards.size(), ib = (hb >> 40) % shards.size();
        std::unique_lock<std::shared_mutex> g1(shards[std::min(ia, ib)]->mu), g2; if (ia != ib) g2 = std::unique_lock<std::shared_mutex>(shards[std::max(ia, ib)]->mu);   // 항상 번호가 작은 구역 먼저
        auto* ea = shards[ia]->find(a, ha); auto* eb = shards[ib]->find(b, hb); if (!ea || !eb || a == b || ea->second < amount) return false;
        ea->second -= amount; eb->second += amount; return true;
    }
    std::size_t size() const { std::size_t n = 0; for (auto& s : shards) { std::shared_lock<std::shared_mutex> g(s->mu); n += s->n; } return n; }     // 동시 수정 중에는 근사값
    template <class F> void snapshot(F f) const {                          // 모든 구역을 번호 순서로 잠근 일관된 순간의 전체 항목
        std::vector<std::shared_lock<std::shared_mutex>> locks; for (auto& s : shards) locks.emplace_back(s->mu);
        for (auto& s : shards) for (auto& c : s->b) for (auto& e : c) f(e.first, e.second);
    }
};

int main() {
    std::mt19937_64 rng(77);
    // ① 단일 스레드 차분 테스트 (확장·삭제·putIfAbsent·compute 를 모두 거친다)
    {   ConcurrentMap<int, long> m(5); std::unordered_map<int, long> ref;
        for (int op = 0; op < 100000; ++op) {
            int k = rng() % 500, t = rng() % 5; long v = (long)(rng() % 1000);
            if (t == 0) { m.put(k, v); ref[k] = v; } else if (t == 1) { assert(m.putIfAbsent(k, v) == ref.emplace(k, v).second); }
            else if (t == 2) { assert(m.erase(k) == (ref.erase(k) > 0)); } else if (t == 3) { long r = m.compute(k, [&](long& x) { x += v; }); ref[k] += v; assert(r == ref[k]); }
            else { long out = -1; bool f = m.get(k, out); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || out == it->second)); }
        }
        assert(m.size() == ref.size()); std::size_t seen = 0; m.snapshot([&](const int& k, const long& v) { assert(ref.at(k) == v); ++seen; }); assert(seen == ref.size());
    }
    const int T = 8; auto run = [&](std::function<void(int)> body) { std::vector<std::thread> th; for (int t = 0; t < T; ++t) th.emplace_back(body, t); for (auto& x : th) x.join(); };
    // ② 갱신 손실 없음: 모든 스레드가 같은 64 개 키를 compute 로 증가
    {   ConcurrentMap<int, long> m(16); const int N = 20000; run([&](int t) { for (int i = 0; i < N; ++i) m.compute((i * 7 + t) % 64, [](long& x) { ++x; }); });
        long sum = 0; m.snapshot([&](const int&, const long& v) { sum += v; }); assert(sum == (long)T * N && m.size() == 64);
    }
    // ③ 확장 중에도 안전: 미리 넣은 1000 개 키는 다른 스레드가 20 만 개를 넣어 구역이 계속 커지는 동안에도 항상 읽힌다
    {   ConcurrentMap<int, long> m(8); for (int i = 0; i < 1000; ++i) m.put(-1 - i, i * 3L);
        std::atomic<bool> done{false}; std::atomic<long> reads{0}, misses{0};
        std::vector<std::thread> readers; for (int r = 0; r < 3; ++r) readers.emplace_back([&, r] { std::mt19937 g(r); long n = 0; while (!done) { int i = g() % 1000; long v; if (!m.get(-1 - i, v) || v != i * 3L) ++misses; ++n; } reads += n; });
        const int W = 5, per = 40000; std::vector<std::thread> writers; for (int w = 0; w < W; ++w) writers.emplace_back([&, w] { for (int i = 0; i < per; ++i) m.put(w * per + i, i); });
        for (auto& x : writers) x.join(); done = true; for (auto& x : readers) x.join();
        assert(misses == 0 && reads > 0 && m.size() == 1000 + (std::size_t)W * per);
        for (int w = 0; w < W; ++w) for (int i = 0; i < per; i += 997) { long v; assert(m.get(w * per + i, v) && v == i); }
    }
    // ④ 여러 키를 함께 바꾸는 연산: 계좌 100 개에 1000 씩, 8 스레드가 무작위 이체(같은 계좌·잔액 부족 포함), 감사 스레드는 일관된 스냅샷의 합을 확인
    {   ConcurrentMap<int, long> bank(7); for (int i = 0; i < 100; ++i) bank.put(i, 1000);
        std::atomic<bool> done{false}; std::atomic<long> audits{0}, bad{0}, ok{0}, refused{0};
        std::thread auditor([&] { while (!done) { long total = 0, minBal = 0; bank.snapshot([&](const int&, const long& v) { total += v; minBal = std::min(minBal, v); }); if (total != 100000 || minBal < 0) ++bad; ++audits; } });
        run([&](int t) { std::mt19937 g(t + 1); for (int i = 0; i < 20000; ++i) { if (bank.transfer(g() % 100, g() % 100, 1 + g() % 600)) ++ok; else ++refused; } });
        done = true; auditor.join(); long total = 0; bank.snapshot([&](const int&, const long& v) { total += v; });
        assert(total == 100000 && bad == 0 && audits > 0 && ok > 0 && refused > 0);                 // 교착 없이 끝났고, 어떤 순간에도 합이 보존됐다
    }
    // ⑤ 스트라이핑의 효과: 키마다 느린 콜백(1 ms)을 돌릴 때 동시에 실행 중인 콜백의 최대 개수 — 구역 1 개면 1, 16 개면 여러 개
    auto maxOverlap = [&](std::size_t shards) {
        ConcurrentMap<int, long> m(shards); std::atomic<int> active{0}, peak{0}; std::vector<int> keyOf; std::vector<char> used(shards, 0);
        for (int k = 0; (int)keyOf.size() < T; ++k) { std::size_t sh = m.shardOf(k); if (shards == 1 || !used[sh]) { used[sh] = 1; keyOf.push_back(k); } }        // 스레드마다 서로 다른 구역에 떨어지는 키 (구역이 1 개면 모두 같은 구역)
        run([&](int t) { for (int i = 0; i < 15; ++i) m.compute(keyOf[t], [&](long& x) { int a = ++active; int p = peak.load(); while (a > p && !peak.compare_exchange_weak(p, a)) {} std::this_thread::sleep_for(std::chrono::milliseconds(1)); ++x; --active; }); });
        return peak.load();
    };
    int one = maxOverlap(1), many = maxOverlap(64);
    assert(one == 1 && many >= 2);
    std::cout << "ConcurrentMap: no lost updates, no lost keys while shards resized, bank total conserved across " << T * 20000 << " concurrent transfers; slow callbacks overlapped at most " << one << " at a time with 1 shard but " << many << " with 64 shards" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1) (서로 다른 구역은 병렬, 같은 구역의 읽기도 병렬), snapshot 은 O(n) 에 전 구역 잠금
// Space Complexity: O(n)
```
## LockFreeHashTable()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <thread>
#include <vector>

// 고정 크기 락프리 해시 테이블(삽입·조회·논리적 삭제): 키 칸을 CAS 로 차지한다. 0 은 빈 칸 표식이므로 키·값은 0 이 아니어야 한다.
// 키 칸은 한 번 차지하면 영영 그 키의 것(그래서 탐사 사슬이 끊기지 않는다)이고, 값 칸을 0 으로 만들면 논리적 삭제(같은 키로 다시 넣으면 그 칸을 재사용).
// 삽입은 "키 CAS → 값 저장" 두 단계라 사이에 읽는 쪽은 값 0(= 아직 없음)을 본다 — 키가 보이는 것과 값이 보이는 것의 순서가 갈린다는 점을 get 이 0 을 "없음" 으로 취급해 해결한다.
// 삭제와 크기 조정은 어렵다 (실제 구현은 묘비 + 협력적 마이그레이션, Cliff Click 의 설계 참고)
// 검증(스트레스 시험, 불변식이 오라클): ① 스레드 4 개의 서로 다른 키 삽입 32 000 개가 모두 조회됨  ② 같은 키를 여러 스레드가 동시에 넣어도 칸은 *하나* (키 칸 전수 검사로 중복 없음), 최종 값은 누가 넣었든 그중 하나
//        ③ 용량 64 에 스레드 4 개가 총 200 개의 서로 다른 키를 경쟁 삽입: 정확히 64 개 성공하고 나머지는 실패(가득 참), 성공한 키는 전부 조회됨  ④ 작성자가 자기 키만 넣고(버전 증가)·지우고(논리 삭제) 다시 넣는 동안 읽는 스레드 4 개가 임의 키를 읽음 —
//        읽은 값은 항상 "그 키가 쓴 적 있는 값" (키·버전이 맞는 형식)이고 버전은 거꾸로 가지 않으며, 끝난 뒤 각 키의 상태는 작성자의 마지막 연산과 일치  ⑤ 0 키·0 값 거부
class LockFreeTable {
    size_t cap; std::unique_ptr<std::atomic<uint64_t>[]> keys, vals;
    size_t slot(uint64_t k) const { k ^= k >> 33; k *= 0xff51afd7ed558ccdULL; k ^= k >> 33; return k % cap; }
public:
    explicit LockFreeTable(size_t capacity = 1 << 16) : cap(capacity), keys(new std::atomic<uint64_t>[capacity]), vals(new std::atomic<uint64_t>[capacity]) { for (size_t i = 0; i < cap; i++) { keys[i].store(0); vals[i].store(0); } }
    bool put(uint64_t k, uint64_t v) {
        if (k == 0 || v == 0) return false;
        for (size_t i = slot(k), n = 0; n < cap; i = (i + 1) % cap, n++) {
            uint64_t cur = keys[i].load(std::memory_order_acquire);
            if (cur == 0 && keys[i].compare_exchange_strong(cur, k)) { vals[i].store(v, std::memory_order_release); return true; }
            if (cur == k) { vals[i].store(v, std::memory_order_release); return true; }   // 다른 스레드가 같은 키를 먼저 차지한 경우 포함 (CAS 실패 시 cur 에 그 키가 들어온다)
        }
        return false;                                                // 가득 참
    }
    bool get(uint64_t k, uint64_t& v) const {
        if (k == 0) return false;
        for (size_t i = slot(k), n = 0; n < cap; i = (i + 1) % cap, n++) {
            uint64_t cur = keys[i].load(std::memory_order_acquire);
            if (cur == 0) return false;
            if (cur == k) { v = vals[i].load(std::memory_order_acquire); return v != 0; }
        }
        return false;
    }
    bool erase(uint64_t k) {                                         // 논리적 삭제: 값 칸을 0 으로. 키 칸은 남겨 탐사 사슬을 지킨다
        for (size_t i = slot(k), n = 0; n < cap; i = (i + 1) % cap, n++) {
            uint64_t cur = keys[i].load(std::memory_order_acquire);
            if (cur == 0) return false;
            if (cur == k) return vals[i].exchange(0, std::memory_order_acq_rel) != 0;
        }
        return false;
    }
    size_t capacity() const { return cap; }
    size_t occupied() const { size_t c = 0; for (size_t i = 0; i < cap; i++) c += keys[i].load() != 0; return c; }
    size_t slotsHolding(uint64_t k) const { size_t c = 0; for (size_t i = 0; i < cap; i++) c += keys[i].load() == k; return c; }
    bool chainsIntact() const {                                       // 모든 키가 홈에서 빈 칸을 만나지 않고 닿는다
        for (size_t j = 0; j < cap; j++) { uint64_t k = keys[j].load(); if (k == 0) continue; size_t i = slot(k); while (i != j) { if (keys[i].load() == 0) return false; i = (i + 1) % cap; } }
        return true;
    }
};

int main() {
    static LockFreeTable t;
    const int T = 4, N = 8000;
    std::vector<std::thread> th;
    for (int w = 0; w < T; w++)
        th.emplace_back([w] { for (int i = 1; i <= N; i++) t.put((uint64_t)w * 1000000 + i, (uint64_t)i * 2); });
    for (auto& x : th) x.join();
    uint64_t v;
    for (int w = 0; w < T; w++) for (int i = 1; i <= N; i++) { assert(t.get((uint64_t)w * 1000000 + i, v) && v == (uint64_t)i * 2); }
    assert(!t.get(999999999, v) && t.occupied() == (size_t)T * N && t.chainsIntact());
    // ⑤ 경계
    LockFreeTable small(8); assert(!small.put(0, 5) && !small.put(5, 0) && !small.get(0, v) && !small.erase(3) && small.put(3, 30) && small.get(3, v) && v == 30 && small.erase(3) && !small.get(3, v) && !small.erase(3) && small.put(3, 31) && small.get(3, v) && v == 31 && small.occupied() == 1);
    // ② 같은 키 경쟁
    {   LockFreeTable shared(1 << 10); std::vector<std::thread> ws; const int K = 200;
        for (int w = 0; w < 4; w++) ws.emplace_back([&shared, w] { for (int round = 0; round < 50; round++) for (int k = 1; k <= K; k++) shared.put((uint64_t)k, (uint64_t)(w + 1) * 1000 + (uint64_t)k); });
        for (auto& x : ws) x.join();
        for (int k = 1; k <= K; k++) { assert(shared.slotsHolding((uint64_t)k) == 1); uint64_t val; assert(shared.get((uint64_t)k, val) && val % 1000 == (uint64_t)k && val / 1000 >= 1 && val / 1000 <= 4); }
        assert(shared.occupied() == (size_t)K && shared.chainsIntact()); }
    // ③ 가득 찬 테이블
    {   LockFreeTable tiny(64); std::atomic<int> ok{0}; std::vector<std::thread> ws;
        for (int w = 0; w < 4; w++) ws.emplace_back([&tiny, &ok, w] { for (int i = 0; i < 50; i++) if (tiny.put((uint64_t)(w * 50 + i + 1), 7)) ok++; });
        for (auto& x : ws) x.join();
        assert(ok == 64 && tiny.occupied() == 64 && tiny.chainsIntact()); int found = 0; for (uint64_t k = 1; k <= 200; k++) { uint64_t val; found += tiny.get(k, val); }
        assert(found == 64 && !tiny.put(1000, 1)); }                                         // 이미 있는 키라면 가득 차도 갱신은 되지만 새 키는 실패
    // ④ 작성자 + 독자: 값 = (키 << 20) | 버전
    {   const int KEYS = 64, ROUNDS = 400; LockFreeTable tb(1 << 9); std::atomic<bool> stop{false}; std::atomic<uint64_t> version[KEYS + 1]; for (auto& x : version) x.store(0);
        std::vector<std::thread> writers, readers; std::atomic<long> reads{0}, observed{0};
        for (int w = 0; w < 4; w++) writers.emplace_back([&, w] {
            std::mt19937 rng((unsigned)w);
            for (int r = 0; r < ROUNDS; r++) for (int k = 1 + w; k <= KEYS; k += 4) {                         // 키를 작성자가 나눠 가진다
                uint64_t ver = version[k].fetch_add(1) + 1; tb.put((uint64_t)k, ((uint64_t)k << 20) | ver);
                if (rng() % 3 == 0) tb.erase((uint64_t)k);
            } });
        for (int rd = 0; rd < 4; rd++) readers.emplace_back([&, rd] {
            std::mt19937 rng(100u + (unsigned)rd); uint64_t last[KEYS + 1] = {0};
            while (!stop.load()) { int k = 1 + (int)(rng() % KEYS); uint64_t val; ++reads;
                if (tb.get((uint64_t)k, val)) { ++observed; assert((val >> 20) == (uint64_t)k); uint64_t ver = val & 0xFFFFF; assert(ver >= 1 && ver <= version[k].load()); assert(ver >= last[k]); last[k] = ver; } } });
        for (auto& x : writers) x.join(); stop = true; for (auto& x : readers) x.join();
        for (int k = 1; k <= KEYS; k++) { uint64_t val; if (tb.get((uint64_t)k, val)) { assert((val >> 20) == (uint64_t)k && (val & 0xFFFFF) == version[k].load()); } assert(version[k].load() == (uint64_t)ROUNDS); }     // 남아 있다면 마지막 버전
        assert(tb.chainsIntact() && tb.occupied() == (size_t)KEYS && reads > 1000); }
    std::cout << "LockFreeTable: " << T * N << " concurrent inserts verified; same-key races left one slot per key; capacity race admitted exactly 64 keys" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 락 없이 진행 보장(lock-free)
// Space Complexity: O(고정 용량)
```
# Part 13. 확률적 구조
## BloomFilter()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 블룸 필터(해시 관점의 요약, 정본은 AdvancedDataStructures.md Part 3): 비트 m 개와 해시 k 개. add 는 k 개 비트를 1 로 만들고 mayContain 은 k 개가 모두 1 인지 본다.
// "없다"는 확실하고(거짓 음성 없음) "있다"는 틀릴 수 있다(거짓 양성). 이론 거짓 양성률 (1 − e^(−kn/m))^k 는 k = (m/n)·ln 2 에서 최소(≈ 0.6185^(m/n)).
// 이중 해싱 h_i = h1 + i·h2 (Kirsch–Mitzenmacher) 로 해시 한 번 값만으로 k 개 위치를 만든다.
typedef std::uint64_t u64;
static inline u64 mix(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
static u64 base(const std::string& s) { u64 h = 1469598103934665603ULL; for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; } return h; }
class Bloom {
    std::vector<u64> w; std::size_t m; int k; bool dbl;
    std::size_t pos(u64 h, int i) const { if (dbl) { u64 h1 = mix(h), h2 = mix(h1) | 1; return (h1 + (u64)i * h2) % m; } return mix(h + 0x9e3779b97f4a7c15ULL * (u64)(i + 1)) % m; }     // dbl=false: 서로 다른 k 개의 해시
public:
    Bloom(std::size_t bits, int hashes, bool doubleHashing = true) : w((bits + 63) / 64), m(bits), k(hashes), dbl(doubleHashing) {}
    void add(const std::string& s) { u64 h = base(s); for (int i = 0; i < k; ++i) { std::size_t p = pos(h, i); w[p >> 6] |= 1ULL << (p & 63); } }
    bool mayContain(const std::string& s) const { u64 h = base(s); for (int i = 0; i < k; ++i) { std::size_t p = pos(h, i); if (!(w[p >> 6] >> (p & 63) & 1)) return false; } return true; }
    std::size_t ones() const { std::size_t c = 0; for (u64 x : w) c += (std::size_t)__builtin_popcountll(x); return c; }
    void merge(const Bloom& o) { assert(m == o.m && k == o.k && dbl == o.dbl); for (std::size_t i = 0; i < w.size(); ++i) w[i] |= o.w[i]; }      // 합집합 = 비트 OR
    bool operator==(const Bloom& o) const { return w == o.w; }
    double estimateCount() const { return -(double)m / k * std::log(1.0 - (double)ones() / (double)m); }                                    // 켜진 비트 수로 원소 수를 거꾸로 추정
};
double theoryFp(double m, double n, double k) { return std::pow(1 - std::exp(-k * n / m), k); }
double measuredFp(const Bloom& f, int queries) { int fp = 0; for (int i = 0; i < queries; ++i) fp += f.mayContain("neg" + std::to_string(i)); return (double)fp / queries; }

int main() {
    // ① 원래 예: 원소당 10 비트, 해시 7 개 → 이론 거짓 양성률 ≈ 0.82 %
    {   const int n = 10000; Bloom f(10 * n, 7); for (int i = 0; i < n; ++i) f.add("mem" + std::to_string(i));
        for (int i = 0; i < n; ++i) assert(f.mayContain("mem" + std::to_string(i)));                  // 거짓 음성은 없다
        double fp = measuredFp(f, 200000), th = theoryFp(10 * n, n, 7); assert(std::abs(fp - th) < 4 * std::sqrt(th / 200000) + 0.1 * th);
    }
    // ② 격자 (원소당 비트 수 × k): 측정한 거짓 양성률이 이론식을 따르고, 최소는 k ≈ (m/n)·ln 2 근처
    const int n = 20000; const int Q = 200000; std::size_t cnt = 0; double worstRel = 0;
    for (int c : {4, 8, 12, 16}) {
        double best = 2; int bestK = 0;
        for (int k = 1; k <= 12; ++k) {
            Bloom f((std::size_t)c * n, k); for (int i = 0; i < n; ++i) f.add("mem" + std::to_string(i));
            double fp = measuredFp(f, Q), th = theoryFp((double)c * n, n, k), sd = std::sqrt(th * (1 - th) / Q);
            assert(std::abs(fp - th) <= 5 * sd + 0.06 * th); if (th > 0.005) worstRel = std::max(worstRel, std::abs(fp - th) / th); ++cnt;
            if (fp < best) { best = fp; bestK = k; }
            if (k == (int)std::lround(c * std::log(2.0))) { double dens = (double)f.ones() / ((double)c * n); assert(dens > 0.45 && dens < 0.55); }          // 최적 k 에서 켜진 비트는 절반
        }
        assert(std::abs(bestK - c * std::log(2.0)) <= 2.5);
    }
    // ③ 이중 해싱 ≈ 독립 해시 k 개 (거짓 양성률 차이 작음), ④ 합집합 = OR, ⑤ 켜진 비트 수로 원소 수 추정
    {   Bloom a(10 * n, 7, true), b(10 * n, 7, false); for (int i = 0; i < n; ++i) { a.add("mem" + std::to_string(i)); b.add("mem" + std::to_string(i)); }
        double fa = measuredFp(a, Q), fb = measuredFp(b, Q); assert(fa / fb > 0.8 && fa / fb < 1.25);
        Bloom x(8 * n, 6), y(8 * n, 6), both(8 * n, 6); for (int i = 0; i < n; ++i) { (i % 3 ? x : y).add("mem" + std::to_string(i)); both.add("mem" + std::to_string(i)); }
        x.merge(y); assert(x == both); for (int i = 0; i < n; ++i) assert(x.mayContain("mem" + std::to_string(i)));
        for (int m : {1000, 5000, 20000, 60000}) { Bloom f(10 * 60000, 7); for (int i = 0; i < m; ++i) f.add("mem" + std::to_string(i)); assert(std::abs(f.estimateCount() - m) < 0.03 * m); }
    }
    // ⑥ 큰 입력: 원소 100 만 개, 비트 1000 만 개, k = 7
    {   const int N = 1000000; Bloom f(10 * (std::size_t)N, 7); for (int i = 0; i < N; ++i) f.add("mem" + std::to_string(i));
        for (int i = 0; i < N; i += 7) assert(f.mayContain("mem" + std::to_string(i)));
        double fp = measuredFp(f, Q), th = theoryFp(10.0 * N, N, 7); assert(std::abs(fp - th) < 4 * std::sqrt(th / Q) + 0.1 * th);
        std::cout << "BloomFilter: " << cnt << " (bits/element, k) settings matched (1-e^(-kn/m))^k (worst relative deviation " << 100 * worstRel << "% where the rate exceeds 0.5%); at 10 bits per element and k = 7 the measured false-positive rate was " << 100 * fp << "% (theory " << 100 * th << "%) for 10^6 elements" << std::endl;
    }
    return 0;
}
// Time Complexity: add / mayContain O(k), 합집합 O(m/64)
// Space Complexity: O(m) 비트
```
## CountMinSketch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <unordered_map>
#include <vector>

// Count-Min Sketch(정본은 AdvancedDataStructures.md Part 3): 빈도 추정. d 행 × w 열의 카운터, 행마다 다른 해시. 추정값 = 행별 카운터의 최솟값.
//  · 항상 실제 이상(과대 추정만 한다, 삭제가 있어도 최종 빈도가 0 이상이면 그대로).  w = ⌈e/ε⌉, d = ⌈ln(1/δ)⌉ 이면 확률 1−δ 로 오차 ≤ ε·N.
//  · 합치기: 두 스케치의 카운터를 칸마다 더하면 두 스트림을 이어 붙인 스케치와 같다. 보수적 갱신(conservative update)은 오차를 줄인다.
typedef std::uint64_t u64; typedef std::int64_t i64;
static inline u64 mix(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
class CMS {
    std::size_t w, d; std::vector<i64> c; bool conservative;
    std::size_t idx(u64 key, std::size_t row) const { return row * w + mix(key + 0x9e3779b97f4a7c15ULL * (row + 1)) % w; }
public:
    CMS(double eps, double delta, bool cons = false) : w((std::size_t)std::ceil(std::exp(1.0) / eps)), d((std::size_t)std::ceil(std::log(1.0 / delta))), c(w * d, 0), conservative(cons) {}
    void add(u64 key, i64 n = 1) {
        if (conservative && n > 0) { i64 target = estimate(key) + n; for (std::size_t r = 0; r < d; ++r) c[idx(key, r)] = std::max(c[idx(key, r)], target); }   // 최솟값 칸만 올린다
        else for (std::size_t r = 0; r < d; ++r) c[idx(key, r)] += n;
    }
    i64 estimate(u64 key) const { i64 m = INT64_MAX; for (std::size_t r = 0; r < d; ++r) m = std::min(m, c[idx(key, r)]); return m; }
    void merge(const CMS& o) { assert(w == o.w && d == o.d); for (std::size_t i = 0; i < c.size(); ++i) c[i] += o.c[i]; }
    bool sameCells(const CMS& o) const { return c == o.c; }
    std::size_t cells() const { return c.size(); }
};
std::vector<u64> zipfStream(std::size_t n, double universe, std::mt19937_64& rng) {      // 키 k 의 확률 ∝ 1/k
    std::vector<u64> s(n); std::uniform_real_distribution<double> u(0, std::log(universe)); for (u64& x : s) x = (u64)std::exp(u(rng)); return s;
}

int main() {
    std::mt19937_64 rng(31);
    // ① 보장: 과소 추정 없음, 오차 > ε·N 인 키의 비율 ≤ δ  (여러 (ε, δ))
    double worstViol = 0; int settings = 0;
    for (double eps : {0.02, 0.01, 0.005}) for (double delta : {0.1, 0.01}) {
        std::vector<u64> s = zipfStream(300000, 1e6, rng); CMS cms(eps, delta); std::unordered_map<u64, i64> truth; for (u64 k : s) { cms.add(k); ++truth[k]; }
        std::size_t viol = 0; for (auto& kv : truth) { i64 e = cms.estimate(kv.first); assert(e >= kv.second); viol += (double)(e - kv.second) > eps * (double)s.size(); }
        double frac = (double)viol / truth.size(); assert(frac <= delta); worstViol = std::max(worstViol, frac / delta); ++settings;
    }
    // ② 보수적 갱신: 여전히 과소 추정은 없고 총 오차는 더 작다
    {   std::vector<u64> s = zipfStream(300000, 1e6, rng); CMS plain(0.01, 0.01), cons(0.01, 0.01, true); std::unordered_map<u64, i64> truth;
        for (u64 k : s) { plain.add(k); cons.add(k); ++truth[k]; }
        i64 errPlain = 0, errCons = 0; for (auto& kv : truth) { i64 a = plain.estimate(kv.first) - kv.second, b = cons.estimate(kv.first) - kv.second; assert(a >= 0 && b >= 0 && b <= a); errPlain += a; errCons += b; }
        assert(errCons * 10 < errPlain * 9);                                                    // 총 오차가 10 % 이상 줄었다
    }
    // ③ 합치기: 스트림을 두 조각으로 나눠 만든 스케치를 더하면 통짜 스케치와 칸마다 같다
    {   std::vector<u64> s = zipfStream(200000, 1e5, rng); CMS whole(0.01, 0.01), a(0.01, 0.01), b(0.01, 0.01); for (std::size_t i = 0; i < s.size(); ++i) { whole.add(s[i]); (i < 70000 ? a : b).add(s[i]); }
        a.merge(b); assert(a.sameCells(whole)); }
    // ④ 빈도 높은 항목(heavy hitters): 빈도 ≥ φN 인 키는 하나도 놓치지 않고(재현율 100 %), 보고된 키의 실제 빈도는 (φ−ε)N 이상
    {   const double phi = 0.01, eps = 0.002; std::vector<u64> s = zipfStream(500000, 1e5, rng); CMS cms(eps, 0.001); std::unordered_map<u64, i64> truth, cand;
        for (std::size_t i = 0; i < s.size(); ++i) { cms.add(s[i]); ++truth[s[i]]; i64 e = cms.estimate(s[i]); if ((double)e >= phi * (double)(i + 1)) cand[s[i]] = e; }
        double N = (double)s.size(); std::size_t trueHeavy = 0, found = 0;
        for (auto& kv : truth) if ((double)kv.second >= phi * N) { ++trueHeavy; found += cand.count(kv.first); }
        assert(trueHeavy > 0 && found == trueHeavy);
        std::size_t reported = 0; for (auto& kv : cand) if ((double)cms.estimate(kv.first) >= phi * N) { ++reported; assert((double)truth[kv.first] >= (phi - eps) * N); }     // 보고된 키의 실제 빈도 ≥ (φ − ε)N
        assert(reported >= trueHeavy && reported <= trueHeavy + 5);
    }
    // ⑤ 삭제(터스타일): 음수 갱신 후에도 최종 빈도가 0 이상이면 과소 추정은 없다
    {   CMS cms(0.01, 0.01); std::map<u64, i64> truth; for (int op = 0; op < 200000; ++op) { u64 k = rng() % 500; if (truth[k] > 0 && rng() % 3 == 0) { cms.add(k, -1); --truth[k]; } else { cms.add(k, 1); ++truth[k]; } }
        for (auto& kv : truth) assert(cms.estimate(kv.first) >= kv.second); }
    // ⑥ 크기는 키 종류 수와 무관: 서로 다른 키 약 200 만 개를 넣어도 카운터는 d·w 개 그대로, 큰 빈도 키는 정확하게 잡는다
    {   CMS cms(0.001, 0.01); std::size_t cells = cms.cells(); for (u64 k = 1; k <= 2000000; ++k) cms.add(k); for (int i = 0; i < 100000; ++i) cms.add(7);
        assert(cms.cells() == cells && cms.estimate(7) >= 100001 && cms.estimate(7) <= 100001 + 0.001 * 2100000 + 1);
        std::cout << "CountMinSketch: guarantee held for " << settings << " (eps, delta) settings (worst violation fraction was " << worstViol << " of the allowed delta); the " << cells << "-counter sketch estimated a key seen 100001 times as " << cms.estimate(7) << " after 2.1*10^6 updates" << std::endl; }
    return 0;
}
// Time Complexity: add / estimate O(d), 합치기 O(d·w)
// Space Complexity: O(d·w) = O((1/ε)·ln(1/δ))
```
## Bloom Filter는 왜 오탐(False Positive)만 발생하는가?
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 이유: 비트는 0 → 1 로만 바뀐다. 원소를 넣으면 그 원소의 k 개 비트가 반드시 1 이 되고 아무도 되돌리지 않으므로 "넣은 원소는 항상 있다고 답한다"(거짓 음성 없음).
// 반면 다른 원소들이 우연히 그 k 개 비트를 모두 1 로 만들어 놓았다면 오탐이 생긴다.  이 항목은 이를 작은 필터에서 *모든* 부분집합을 열거해 확인한다.
//  ① 12 개 원소의 모든 부분집합(4096 개): 넣은 원소는 전부 "있음", 넣지 않은 원소의 답은 독립 계산(각 위치를 덮는 원소가 있는가)과 같다.
//  ② 단조성: S ⊆ T 이면 S 에서 "있음"인 원소는 T 에서도 "있음" (모든 쌍 3^12 = 531441 개).
//  ③ 비트를 0 으로 내려 삭제하면 다른 원소가 거짓 음성이 되는 경우의 수, 카운터를 쓰면 삭제 뒤 필터가 "처음부터 그 원소 없이 만든 것"과 정확히 같다.
//  ④ 거짓 양성률의 *정확한* 값은 점유 분포 DP 로 구한 E[ρ^k] 이고, 교과서 식 (E[ρ])^k 는 이보다 약간 작다 (옌센 부등식) — 시뮬레이션으로 확인.
//  ⑤ 카운터 폭: 2 비트 래핑 카운터는 거짓 음성을 만들고, 포화(saturating) 카운터는 거짓 음성은 없지만 삭제 뒤에도 흔적이 남으며, 4 비트면 보통 설계에서 넘치지 않는다.
const int U = 12, M = 20, K = 3;                                         // 원소 12 개, 비트 20 개, 해시 3 개
struct Hashes {
    int pos[U][K]; std::uint32_t bits[U];
    explicit Hashes(std::mt19937& rng) { for (int x = 0; x < U; ++x) { bits[x] = 0; for (int i = 0; i < K; ++i) { pos[x][i] = (int)(rng() % M); bits[x] |= 1u << pos[x][i]; } } }
    std::uint32_t filterOf(unsigned subset) const { std::uint32_t f = 0; for (int x = 0; x < U; ++x) if (subset >> x & 1) f |= bits[x]; return f; }
    bool has(std::uint32_t f, int x) const { return (f & bits[x]) == bits[x]; }
    bool coveredBySet(unsigned subset, int x) const {                    // 독립 오라클: x 의 모든 위치를 덮는 원소가 집합 안에 있는가
        for (int i = 0; i < K; ++i) { bool covered = false; for (int y = 0; y < U && !covered; ++y) if (subset >> y & 1) for (int j = 0; j < K; ++j) if (pos[y][j] == pos[x][i]) covered = true; if (!covered) return false; }
        return true;
    }
};
double exactFp(int m, int n, int k) {                                    // n·k 번 던져 켜진 칸 수 j 의 분포 → E[(j/m)^k]
    std::vector<double> d(m + 1, 0.0); d[0] = 1; for (int t = 0; t < n * k; ++t) { std::vector<double> nd(m + 1, 0.0); for (int j = 0; j <= m; ++j) { nd[j] += d[j] * j / m; if (j < m) nd[j + 1] += d[j] * (m - j) / m; } d.swap(nd); }
    double p = 0; for (int j = 0; j <= m; ++j) p += d[j] * std::pow((double)j / m, k); return p;
}

int main() {
    std::mt19937 rng(9);
    long fpTotal = 0, nonMembers = 0, removalBreaks = 0, removalCases = 0;
    for (int trial = 0; trial < 20; ++trial) {
        Hashes h(rng);
        for (unsigned S = 0; S < (1u << U); ++S) {                      // ① 모든 부분집합
            std::uint32_t f = h.filterOf(S);
            for (int x = 0; x < U; ++x) { if (S >> x & 1) assert(h.has(f, x)); else { assert(h.has(f, x) == h.coveredBySet(S, x)); fpTotal += h.has(f, x); ++nonMembers; } }
            // ③ 비트를 내려 삭제하면 다른 원소가 사라질 수 있다 / 카운터는 정확히 되돌린다
            for (int y = 0; y < U; ++y) if (S >> y & 1) {
                std::uint32_t g = f & ~h.bits[y]; bool broke = false; for (int z = 0; z < U; ++z) if ((S >> z & 1) && z != y && !h.has(g, z)) broke = true; removalBreaks += broke; ++removalCases;
                int cnt[M] = {}, ref[M] = {}; for (int z = 0; z < U; ++z) if (S >> z & 1) for (int i = 0; i < K; ++i) ++cnt[h.pos[z][i]];
                for (int i = 0; i < K; ++i) --cnt[h.pos[y][i]];
                for (int z = 0; z < U; ++z) if ((S >> z & 1) && z != y) for (int i = 0; i < K; ++i) ++ref[h.pos[z][i]];
                for (int p = 0; p < M; ++p) assert(cnt[p] == ref[p]);
            }
        }
        if (trial == 0) for (unsigned T = 0; T < (1u << U); ++T) {       // ② 단조성: 모든 (S ⊆ T) — 3^12 쌍 전체 검사는 첫 필터에서만 (나머지 필터는 ①·③)
            std::uint32_t ft = h.filterOf(T);
            for (unsigned S = T;; S = (S - 1) & T) { std::uint32_t fs = h.filterOf(S); for (int x = 0; x < U; ++x) if (h.has(fs, x)) assert(h.has(ft, x)); if (S == 0) break; }
        }
    }
    assert(removalBreaks > 0 && removalBreaks < removalCases && fpTotal > 0 && fpTotal < nonMembers);
    // ④ 정확한 거짓 양성률 vs 교과서 식 vs 시뮬레이션
    const int m = 64, n = 8, k = 3; double exact = exactFp(m, n, k), textbook = std::pow(1 - std::exp(-(double)k * n / m), k);
    {   std::mt19937_64 g(5); const int R = 600000; long fp = 0;
        for (int r = 0; r < R; ++r) { std::uint64_t f = 0; for (int t = 0; t < n * k; ++t) f |= 1ULL << (g() % m); bool all = true; for (int i = 0; i < k; ++i) all = all && (f >> (g() % m) & 1); fp += all; }
        double sim = (double)fp / R, sd = std::sqrt(exact * (1 - exact) / R);
        assert(std::abs(sim - exact) < 4 * sd && exact > textbook * 1.02 && std::abs(sim - textbook) > 3 * sd);          // 교과서 식은 약 5 % 작다
        std::cout << "BloomFilter(why false positives only): m=" << m << ", n=" << n << ", k=" << k << ": exact " << exact << ", simulated " << sim << ", textbook formula " << textbook << "; zeroing bits on delete broke " << removalBreaks << " of " << removalCases << " (set, deleted element) cases per 20 hash tables";
    }
    // ⑤ 카운터 폭: 과부하 필터(m=32, k=3, 원소 30 개 = 90 번 던짐)에서 2 비트 카운터 세 가지 + 넉넉한 카운터
    long wrapFalseNeg = 0, satFalseNeg = 0, satResidue = 0, wideFalseNeg = 0, wideResidue = 0;
    {   std::mt19937 g(17); const int mm = 32, kk = 3, items = 30;
        for (int trial = 0; trial < 2000; ++trial) {
            std::vector<std::vector<int>> pos(items, std::vector<int>(kk)); for (auto& p : pos) for (int& x : p) x = (int)(g() % mm);
            std::vector<int> wide(mm, 0), wrap(mm, 0), sat(mm, 0);
            for (auto& p : pos) for (int x : p) { ++wide[x]; wrap[x] = (wrap[x] + 1) & 3; if (sat[x] < 3) ++sat[x]; }
            std::vector<int> order(items); for (int i = 0; i < items; ++i) order[i] = i; std::shuffle(order.begin(), order.end(), g);
            auto present = [&](const std::vector<int>& c, int it) { for (int x : pos[it]) if (!c[x]) return false; return true; };
            bool wrapBad = false, satBad = false, wideBad = false;
            for (int step = 0; step <= items; ++step) {
                for (int s = step; s < items; ++s) { int it = order[s]; wrapBad |= !present(wrap, it); satBad |= !present(sat, it); wideBad |= !present(wide, it); }      // 아직 안 지운 원소
                if (step == items) break;
                for (int x : pos[order[step]]) { --wide[x]; wrap[x] = (wrap[x] + 3) & 3; if (sat[x] < 3) --sat[x]; }                   // 포화한 카운터는 내리지 않는다
            }
            wrapFalseNeg += wrapBad; satFalseNeg += satBad; wideFalseNeg += wideBad;
            bool residue = false; for (int c : sat) residue |= c != 0; satResidue += residue; bool wres = false; for (int c : wide) wres |= c != 0; wideResidue += wres;
        }
        assert(wrapFalseNeg > 0 && satFalseNeg == 0 && wideFalseNeg == 0 && satResidue > 0 && wideResidue == 0);
        // 표준 설계(원소당 10 비트, k=7): 칸당 개수는 푸아송(0.7) 이라 4 비트 카운터(최대 15)로 충분하다
        const int N = 100000; std::vector<unsigned char> c(10 * N, 0); std::mt19937_64 g2(3); int mx = 0; for (long t = 0; t < 7L * N; ++t) { int p = (int)(g2() % c.size()); mx = std::max(mx, (int)++c[p]); }
        assert(mx < 15);
        std::cout << "; with 2-bit counters in an overloaded filter: wrapping gave false negatives in " << wrapFalseNeg << "/2000 runs, saturating in " << satFalseNeg << " (but left residue in " << satResidue << "), wide counters in " << wideFalseNeg << "; at 10 bits/element the largest cell count was " << mx << std::endl;
    }
    return 0;
}
// Time Complexity: add / has / remove O(k), 열거 검증 O(3^U · U)
// Space Complexity: O(m)
```
# Part 14. 유사도 해시
## LocalitySensitiveHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

// LSH(Jaccard 용): 문서를 3-gram 집합으로 보고 MinHash 서명을 만든 뒤, 서명을 b 개의 밴드(r 행씩)로 나눈다.
// 한 밴드라도 완전히 같으면 "후보 쌍".  유사도 s 인 쌍이 후보가 될 확률 = 1 - (1 - s^r)^b  (S자 곡선, 곡선이 가파르게 솟는 문턱 ≈ (1/b)^(1/r))
// MinHash 의 성질: 서명의 한 행이 같을 확률 = 두 집합의 Jaccard 유사도 (불편 추정량).  밴드 키를 해시 테이블 버킷으로 쓰면 모든 쌍을 비교하지 않고도 후보를 모은다
// 검증: ① 손으로 고른 문서(원래 예)  ② MinHash: 서명 일치 비율이 참 Jaccard 의 불편 추정량(평균 오차 < 0.01, 표준편차 ≈ √(s(1-s)/n))  ③ S자 곡선: 유사도 0.2~0.9 의 집합 쌍 각 400 개에서 후보가 된 비율이 이론값 1-(1-s^r)^b 와 4σ 이내
//        ④ 버킷 방식(밴드 키 -> 문서 목록)이 모든 쌍을 비교하는 방식과 *정확히 같은* 후보 집합을 내고, 300 개 문서에서 비교한 쌍 수가 전수 비교(44 850 쌍)보다 훨씬 적으며, 참 유사도 ≥ 0.8 인 쌍의 재현율이 높다
//        ⑤ 문턱에 맞는 (b, r) 고르기: b·r ≤ 100 인 모든 쌍 중 오류 면적(거짓 양성 + 거짓 음성)이 최소인 것이 원하는 문턱 근처에서 곡선이 솟는다 (문턱 0.5 의 최적은 이 예제의 20×5)
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
std::set<uint64_t> shingles(const std::string& s) {
    std::set<uint64_t> r;
    for (size_t i = 0; i + 3 <= s.size(); i++) { uint64_t h = 0; for (int j = 0; j < 3; j++) h = h * 257 + (unsigned char)s[i + j]; r.insert(h); }
    return r;
}
const int BANDS = 20, ROWS = 5;
std::vector<uint64_t> signature(const std::set<uint64_t>& sh, int bands = BANDS, int rows = ROWS) {
    std::vector<uint64_t> sig(bands * rows, UINT64_MAX);
    for (uint64_t x : sh) for (int i = 0; i < bands * rows; i++) sig[i] = std::min(sig[i], mix(x ^ (0x9e3779b97f4a7c15ULL * (i + 1))));
    return sig;
}
bool candidate(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b, int bands = BANDS, int rows = ROWS) {
    for (int band = 0; band < bands; band++) {
        bool same = true;
        for (int r = 0; r < rows; r++) if (a[band * rows + r] != b[band * rows + r]) { same = false; break; }
        if (same) return true;                                     // 아래 bucketCandidates 는 밴드 키를 해시 테이블 버킷으로 써서 O(n) 에 후보를 모은다
    }
    return false;
}
double jaccard(const std::set<uint64_t>& a, const std::set<uint64_t>& b) { size_t inter = 0; for (uint64_t x : a) inter += b.count(x); return a.empty() && b.empty() ? 1.0 : (double)inter / (double)(a.size() + b.size() - inter); }
double sCurve(double s, int bands = BANDS, int rows = ROWS) { return 1 - std::pow(1 - std::pow(s, rows), bands); }
std::set<std::pair<int, int>> bucketCandidates(const std::vector<std::vector<uint64_t>>& sigs, long& comparedPairs, int bands = BANDS, int rows = ROWS) {     // 같은 밴드 키를 가진 문서끼리만 쌍을 만든다
    std::set<std::pair<int, int>> out; comparedPairs = 0;
    for (int band = 0; band < bands; band++) {
        std::unordered_map<uint64_t, std::vector<int>> bucket;
        for (size_t d = 0; d < sigs.size(); d++) { uint64_t key = 0; for (int r = 0; r < rows; r++) key = mix(key ^ sigs[d][band * rows + r]); bucket[key].push_back((int)d); }
        for (auto& kv : bucket) for (size_t i = 0; i < kv.second.size(); i++) for (size_t j = i + 1; j < kv.second.size(); j++) { ++comparedPairs; out.insert({kv.second[i], kv.second[j]}); }
    }
    return out;
}
std::pair<std::set<uint64_t>, std::set<uint64_t>> pairWithJaccard(double s, int m, std::mt19937_64& rng) {      // 크기 m 인 두 집합, 교집합 크기 i = 2ms/(1+s) 로 Jaccard ≈ s
    int inter = (int)std::lround(2.0 * m * s / (1.0 + s)); std::set<uint64_t> a, b;
    while ((int)a.size() < inter) { uint64_t x = rng(); a.insert(x); b.insert(x); }
    while ((int)a.size() < m) a.insert(rng()); while ((int)b.size() < m) b.insert(rng());
    return {a, b};
}

int main() {
    auto A  = signature(shingles("the quick brown fox jumps over the lazy dog near the river bank"));
    auto A2 = signature(shingles("the quick brown fox jumps over the lazy dog near the river side"));
    auto B  = signature(shingles("completely unrelated text about quantum chromodynamics and gluon fields"));
    assert(candidate(A, A2));                                      // 유사한 문서는 후보가 된다
    assert(!candidate(A, B));                                      // 무관한 문서는 후보가 되지 않는다
    assert(candidate(A, A) && jaccard(shingles(""), shingles("")) == 1.0 && sCurve(0) == 0 && sCurve(1) == 1 && std::fabs(sCurve(0.2) - 0.0064) < 1e-3 && sCurve(0.8) > 0.999);        // 경계와 곡선의 알려진 값
    // ② MinHash 는 Jaccard 의 불편 추정량
    std::mt19937_64 rng(2024); const int n = BANDS * ROWS;
    for (double s : {0.1, 0.3, 0.5, 0.7, 0.9}) {
        double sumErr = 0, sumSq = 0; const int pairs = 300; double trueMean = 0;
        for (int t = 0; t < pairs; t++) { auto pr = pairWithJaccard(s, 100, rng); double tj = jaccard(pr.first, pr.second); auto sa = signature(pr.first), sb = signature(pr.second);
            int eq = 0; for (int i = 0; i < n; i++) eq += sa[i] == sb[i]; double est = (double)eq / n; sumErr += est - tj; sumSq += (est - tj) * (est - tj); trueMean += tj; }
        double bias = sumErr / pairs, sd = std::sqrt(sumSq / pairs), theory = std::sqrt(s * (1 - s) / n);
        assert(std::fabs(bias) < 0.012 && sd > 0.6 * theory && sd < 1.4 * theory);                                 // 편향 ≈ 0, 표준편차 ≈ √(s(1-s)/n)
    }
    // ③ S자 곡선
    for (double s : {0.2, 0.4, 0.5, 0.6, 0.8, 0.9}) {
        int hits = 0; const int trials = 400;
        for (int t = 0; t < trials; t++) { auto pr = pairWithJaccard(s, 100, rng); hits += candidate(signature(pr.first), signature(pr.second)); }
        int inter = (int)std::lround(2.0 * 100 * s / (1.0 + s)); double p = sCurve((double)inter / (200 - inter));        // 정수로 반올림된 실제 Jaccard 에 대한 이론값
        double frac = (double)hits / trials, sigma = std::sqrt(p * (1 - p) / trials) + 0.005;
        assert(std::fabs(frac - p) < 4 * sigma + 0.02);
    }
    // ④ 버킷 방식 대 전수 비교: 75 개의 클러스터(클러스터당 4 개 문서, 클러스터 안에서는 기준 문서에서 4 개씩 바꿔 Jaccard ≈ 0.85)
    std::vector<std::set<uint64_t>> docs; std::vector<int> cluster;
    for (int c = 0; c < 75; c++) { std::set<uint64_t> base; while (base.size() < 100) base.insert(rng());
        for (int d = 0; d < 4; d++) { std::set<uint64_t> doc = base; std::vector<uint64_t> v(doc.begin(), doc.end()); for (int k = 0; k < 4; k++) { doc.erase(v[rng() % v.size()]); } while (doc.size() < 100) doc.insert(rng()); docs.push_back(doc); cluster.push_back(c); } }
    std::vector<std::vector<uint64_t>> sigs; for (auto& d : docs) sigs.push_back(signature(d));
    long compared; std::set<std::pair<int, int>> viaBuckets = bucketCandidates(sigs, compared), viaAll;
    for (size_t i = 0; i < docs.size(); i++) for (size_t j = i + 1; j < docs.size(); j++) if (candidate(sigs[i], sigs[j])) viaAll.insert({(int)i, (int)j});
    assert(viaBuckets == viaAll);                                                                               // 정확히 같은 후보 집합
    long allPairs = (long)docs.size() * ((long)docs.size() - 1) / 2; assert(allPairs == 44850 && compared < allPairs / 3 && viaBuckets.size() < 1500);
    long close = 0, closeFound = 0, far = 0, farFound = 0;
    for (size_t i = 0; i < docs.size(); i++) for (size_t j = i + 1; j < docs.size(); j++) { double tj = jaccard(docs[i], docs[j]); bool cand = viaAll.count({(int)i, (int)j}) > 0; if (tj >= 0.8) { ++close; closeFound += cand; } else if (tj < 0.3) { ++far; farFound += cand; } }
    assert(close > 150 && (double)closeFound / close > 0.97 && far > 40000 && (double)farFound / far < 0.001);       // 비슷한 쌍은 거의 다 찾고 먼 쌍은 거의 안 낸다
    // ⑤ 문턱에 맞는 (b, r)
    auto choose = [](int total, double threshold) { int bestB = 1, bestR = 1; double bestErr = 1e18;
        for (int r = 1; r <= total; r++) for (int b = 1; b * r <= total; b++) { double err = 0; const int steps = 200;
            for (int i = 0; i < steps; i++) { double s = (i + 0.5) / steps; double p = sCurve(s, b, r); err += s < threshold ? p : 1 - p; }                     // 문턱 아래의 후보 확률(거짓 양성) + 위의 놓칠 확률(거짓 음성)
            if (err < bestErr) { bestErr = err; bestB = b; bestR = r; } }
        return std::make_pair(bestB, bestR); };
    for (double th : {0.3, 0.5, 0.7, 0.9}) { auto br = choose(100, th); double implied = std::pow(1.0 / br.first, 1.0 / br.second); assert(std::fabs(implied - th) < 0.08 && std::fabs(sCurve(th, br.first, br.second) - 0.5) < 0.25 && br.first * br.second <= 100); }
    assert(choose(100, 0.5) == std::make_pair(20, 5));                                                                              // 이 예제의 설정 (20 밴드 × 5 행) 이 문턱 0.5 의 최적
    std::cout << "LSH: candidates (A,A') yes, (A,B) no; the bucket method compared " << compared << " of " << allPairs << " pairs and found " << closeFound << "/" << close << " near-duplicate pairs (false-candidate rate " << (double)farFound / far << ")" << std::endl;
    return 0;
}
// Time Complexity: 서명 O(|문서|·H), 후보 탐색 평균 O(n)
// Space Complexity: O(n·H)
```
## SimHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// SimHash: 문서의 특징(단어)마다 64 비트 해시를 만들고, 비트별로 가중치를 +w / −w 로 누적해 부호로 64 비트 지문을 만든다.
// 두 문서의 비트가 다를 확률 ≈ θ/π (θ = 두 tf 벡터 사이 각) → 해밍 거리 ≈ 64·arccos(cos)/π 이므로 비슷한 문서는 지문이 가깝다 (구글의 중복 웹페이지 탐지).
//  ① 코사인과 해밍 거리의 관계를 여러 유사도에서 측정. ② 해밍 거리 ≤ k 를 모두 찾는 색인: 64 비트를 k+1 조각으로 나누면 비둘기집 원리로 최소 한 조각은 정확히 같다.
//  ③ 그 색인이 거리 ≤ 3 의 모든 변형(C(64,≤3) = 43745 가지)을 놓치지 않는지 전수 확인, 무작위·계획된 중복쌍에서 무차별 탐색과 대조.
//  ④ 가족(원본+약간 고친 변형) 문서 모음에서 가족 내 거리와 가족 간 거리가 분리되는지 확인.
typedef std::uint64_t u64; typedef std::uint32_t u32; typedef std::int64_t i64;
static inline u64 mix(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
typedef std::map<int, int> Doc;                                          // 단어 번호 → 빈도(tf)
u64 simhash(const Doc& d, int stopRanks = 0) {                         // 가중치 = tf. stopRanks > 0 이면 흔한 단어(번호 < stopRanks)는 버리고 나머지는 1 + 2·ln(tf) (부분선형 tf)
    i64 v[64] = {0};
    for (auto& kv : d) { u64 h = mix((u64)kv.first + 0x1234567ULL); i64 w = stopRanks == 0 ? kv.second : kv.first < stopRanks ? 0 : 1 + std::llround(2 * std::log((double)kv.second)); for (int i = 0; i < 64; ++i) v[i] += (h >> i & 1) ? w : -w; }
    u64 f = 0; for (int i = 0; i < 64; ++i) if (v[i] > 0) f |= 1ULL << i; return f; }
int hamming(u64 a, u64 b) { return __builtin_popcountll(a ^ b); }
double cosine(const Doc& a, const Doc& b) { double dot = 0, na = 0, nb = 0; for (auto& kv : a) { na += (double)kv.second * kv.second; auto it = b.find(kv.first); if (it != b.end()) dot += (double)kv.second * it->second; } for (auto& kv : b) nb += (double)kv.second * kv.second; return dot / std::sqrt(na * nb); }

class NearDupIndex {                                                     // 해밍 거리 ≤ k 질의: k+1 개의 비트 조각 각각을 키로 한 정렬 배열
    int k, blocks; std::vector<int> lo, width; std::vector<std::vector<std::pair<u32, u32>>> tab; std::vector<u64> fps;
    u32 blockOf(u64 fp, int b) const { return (u32)((fp >> lo[b]) & ((width[b] == 64 ? ~0ULL : (1ULL << width[b]) - 1))); }
public:
    explicit NearDupIndex(int kk) : k(kk), blocks(kk + 1), lo(kk + 1), width(kk + 1), tab(kk + 1) { int pos = 0; for (int b = 0; b < blocks; ++b) { width[b] = 64 / blocks + (b < 64 % blocks); lo[b] = pos; pos += width[b]; } assert(pos == 64 && k >= 1); }
    void add(u64 fp) { u32 id = (u32)fps.size(); fps.push_back(fp); for (int b = 0; b < blocks; ++b) tab[b].emplace_back(blockOf(fp, b), id); }
    void seal() { for (auto& t : tab) std::sort(t.begin(), t.end()); }
    std::vector<u32> query(u64 fp, std::size_t& scanned) const {          // 후보 = 어떤 조각이 같은 지문들, 그중 실제 거리 ≤ k 인 것만
        std::vector<u32> out; for (int b = 0; b < blocks; ++b) { u32 key = blockOf(fp, b); for (auto it = std::lower_bound(tab[b].begin(), tab[b].end(), std::make_pair(key, 0u)); it != tab[b].end() && it->first == key; ++it) { ++scanned; if (hamming(fps[it->second], fp) <= k) out.push_back(it->second); } }
        std::sort(out.begin(), out.end()); out.erase(std::unique(out.begin(), out.end()), out.end()); return out; }
    std::vector<u32> brute(u64 fp) const { std::vector<u32> out; for (u32 i = 0; i < fps.size(); ++i) if (hamming(fps[i], fp) <= k) out.push_back(i); return out; }
};

int main() {
    std::mt19937_64 rng(6);
    // ① 코사인 ↔ 해밍: 원본에서 단어 일부를 새 단어로 갈아 끼운 변형 (남기는 비율 f)
    double worstGap = 0;
    for (double f : {0.99, 0.95, 0.9, 0.8, 0.6, 0.4, 0.2, 0.0}) {
        double sumH = 0, sumTheta = 0; const int T = 300;
        for (int t = 0; t < T; ++t) {
            Doc a, b; int next = 1000000; for (int i = 0; i < 150; ++i) { int w = (int)(rng() % 20000), tf = 1 + (int)(rng() % 5); a[w] = tf; if ((double)(rng() % 1000) / 1000 < f) b[w] = tf; else b[next++] = tf; }
            sumH += hamming(simhash(a), simhash(b)) / 64.0; sumTheta += std::acos(std::min(1.0, cosine(a, b))) / M_PI;
        }
        double gap = std::abs(sumH - sumTheta) / T; worstGap = std::max(worstGap, gap); assert(gap < 0.03);
    }
    // ② 색인 vs 무차별 탐색: 지문 2 만 개 + 계획된 중복쌍 (거리 0~3 으로 비트 뒤집기), 질의 2000 개
    for (int k : {1, 2, 3, 5}) {
        NearDupIndex ix(k); std::vector<u64> fps; for (int i = 0; i < 20000; ++i) fps.push_back(rng());
        for (int i = 0; i < 300; ++i) { u64 f = fps[rng() % 20000]; int d = (int)(rng() % (k + 2)); for (int j = 0; j < d; ++j) f ^= 1ULL << (rng() % 64); fps.push_back(f); }
        for (u64 f : fps) ix.add(f); ix.seal(); std::size_t scanned = 0, hits = 0;
        for (int q = 0; q < 2000; ++q) { u64 f = fps[rng() % fps.size()]; if (q % 2) f ^= 1ULL << (rng() % 64); std::vector<u32> got = ix.query(f, scanned), want = ix.brute(f); assert(got == want); hits += got.size(); }
        assert(hits >= 2000 && scanned < 2000 * (fps.size() / 10));       // 무차별 탐색(2000 × 20300 번)의 10 % 미만만 훑는다
    }
    // ③ 비둘기집 원리의 전수 확인 (k = 3): 한 지문의 거리 0~3 변형 43745 개 전부가 질의로 원본을 찾는다
    {   NearDupIndex ix(3); u64 target = rng(); ix.add(target); for (int i = 0; i < 3000; ++i) ix.add(rng()); ix.seal(); long checked = 0; std::size_t scanned = 0;
        auto found = [&](u64 f) { std::vector<u32> r = ix.query(f, scanned); ++checked; return std::binary_search(r.begin(), r.end(), 0u); };
        assert(found(target)); for (int a = 0; a < 64; ++a) { assert(found(target ^ (1ULL << a))); for (int b = a + 1; b < 64; ++b) { assert(found(target ^ (1ULL << a) ^ (1ULL << b))); for (int c = b + 1; c < 64; ++c) assert(found(target ^ (1ULL << a) ^ (1ULL << b) ^ (1ULL << c))); } }
        assert(checked == 1 + 64 + 2016 + 41664);
    }
    // ④ 가족 문서: 100 가족 × (원본 + 변형 3 개, 단어 3 % 교체), 빈도는 지프 분포 → 가족 내 거리 vs 가족 간 거리
    {   std::vector<Doc> docs; std::vector<int> family; std::vector<double> w(5000); for (int i = 0; i < 5000; ++i) w[i] = 1.0 / (i + 1);
        std::discrete_distribution<int> zipf(w.begin(), w.end()); std::mt19937 g(2);
        for (int f = 0; f < 100; ++f) {
            Doc base; for (int i = 0; i < 250; ++i) ++base[zipf(g)]; docs.push_back(base); family.push_back(f);
            for (int v = 0; v < 3; ++v) { Doc d = base; int edits = 6; for (int e = 0; e < edits; ++e) { auto it = d.begin(); std::advance(it, g() % d.size()); if (--it->second == 0) d.erase(it); ++d[zipf(g)]; } docs.push_back(d); family.push_back(f); }
        }
        for (int stop : {0, 30}) {
            std::vector<u64> fp; for (auto& d : docs) fp.push_back(simhash(d, stop)); const int T = 10; long within = 0, withinOk = 0, across = 0, acrossBad = 0; double sumWithin = 0, sumAcross = 0;
            for (std::size_t i = 0; i < docs.size(); ++i) for (std::size_t j = i + 1; j < docs.size(); ++j) { int h = hamming(fp[i], fp[j]); if (family[i] == family[j]) { ++within; withinOk += h <= T; sumWithin += h; } else { ++across; acrossBad += h <= T; sumAcross += h; } }
            double recall = (double)withinOk / within, fpr = (double)acrossBad / across;
            if (stop == 0) { assert(sumAcross / across < 14 && fpr > 0.3 && recall > 0.9); std::cout << "SimHash: |measured Hamming/64 - arccos(cos)/pi| stayed below " << worstGap << " at every similarity; the index matched brute force for k=1,2,3,5 and found all 43745 variants within distance 3; in a 400-document Zipf corpus, raw tf weights let stop words dominate (unrelated documents averaged only " << sumAcross / across << " bits apart, so " << 100 * fpr << "% of cross-family pairs fell within 10 bits), "; }
            else { assert(recall > 0.9 && fpr < 0.002 && sumAcross / across > 20); std::cout << "while dropping the 30 most common words and using 1+2ln(tf) put " << 100 * recall << "% of same-family pairs and " << 100 * fpr << "% of cross-family pairs within 10 bits (means " << sumWithin / within << " vs " << sumAcross / across << ")" << std::endl; }
        }
    }
    return 0;
}
// Time Complexity: 지문 O(단어 수 · 64), 색인 질의 기대 O(k · log N + 후보 수)
// Space Complexity: O(N · (k + 1)) (색인), 지문은 문서당 8 바이트
```
## MinHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

// MinHash: 무작위 순열 π 아래에서 두 집합 A, B 의 "최소 원소"가 같을 확률 = Jaccard(A, B) = |A∩B| / |A∪B|.
// 순열 K 개(여기서는 해시 K 개)로 서명을 만들면 "같은 칸의 비율"이 Jaccard 의 불편 추정량이다 (표준오차 √(J(1−J)/K)).
//  ① 작은 전체집합(6 개)에서는 모든 순열 720 개를 세어 확률 = Jaccard 를 *정확히* 확인한다 (모든 쌍 A, B).
//  ② 통계 검증: 편향 없음, 오차가 √(J(1−J)/K) 로 줄어듦. ③ 합집합 서명 = 칸별 최솟값(정확히 같음). ④ b-비트 MinHash(서명 크기를 줄이는 변형), ⑤ bottom-k 스케치(해시 한 번).
typedef std::uint64_t u64;
static inline u64 mix(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
struct MinHash {
    int K; std::vector<u64> seed;
    explicit MinHash(int k, u64 s = 1) : K(k), seed(k) { for (int i = 0; i < k; ++i) seed[i] = mix(s * 0x9e3779b97f4a7c15ULL + (u64)i + 1); }
    std::vector<u64> sign(const std::vector<u64>& set) const {           // 칸 i 의 값 = min_x h_i(x).  원소 하나당 해시 K 번
        std::vector<u64> sig(K, UINT64_MAX); for (u64 x : set) { u64 hx = mix(x); for (int i = 0; i < K; ++i) sig[i] = std::min(sig[i], mix(hx ^ seed[i])); } return sig; }
    static double estimate(const std::vector<u64>& a, const std::vector<u64>& b) { int same = 0; for (std::size_t i = 0; i < a.size(); ++i) same += a[i] == b[i]; return (double)same / a.size(); }
    static std::vector<u64> merge(const std::vector<u64>& a, const std::vector<u64>& b) { std::vector<u64> r(a.size()); for (std::size_t i = 0; i < a.size(); ++i) r[i] = std::min(a[i], b[i]); return r; }
    static double estimateBBit(const std::vector<u64>& a, const std::vector<u64>& b, int bits) {     // 칸마다 하위 b 비트만 저장해도 (m − 2^−b)/(1 − 2^−b) 로 보정하면 불편 추정
        u64 mask = (1ULL << bits) - 1; int same = 0; for (std::size_t i = 0; i < a.size(); ++i) same += (a[i] & mask) == (b[i] & mask);
        double m = (double)same / a.size(), c = std::pow(2.0, -bits); return (m - c) / (1 - c); }
};
std::vector<u64> bottomK(const std::vector<u64>& set, std::size_t k, u64 seed) {      // 해시 하나로 가장 작은 k 개만 남긴다 (정렬된 벡터)
    std::vector<u64> h; for (u64 x : set) h.push_back(mix(mix(x) ^ seed)); std::sort(h.begin(), h.end()); h.erase(std::unique(h.begin(), h.end()), h.end()); if (h.size() > k) h.resize(k); return h; }
double bottomKJaccard(const std::vector<u64>& a, const std::vector<u64>& b, std::size_t k) {   // 합집합의 bottom-k 중 A, B 양쪽에 모두 있는 비율
    std::vector<u64> u; std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(u)); if (u.size() > k) u.resize(k);
    std::size_t both = 0; for (u64 x : u) both += std::binary_search(a.begin(), a.end(), x) && std::binary_search(b.begin(), b.end(), x); return (double)both / u.size(); }
double exactJaccard(std::vector<u64> a, std::vector<u64> b) { std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end()); std::vector<u64> i, u; std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(i)); std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(u)); return (double)i.size() / u.size(); }
void makePair(int n, int inter, u64 base, std::vector<u64>& A, std::vector<u64>& B) { A.clear(); B.clear(); for (int i = 0; i < n; ++i) A.push_back(base + i); for (int i = n - inter; i < 2 * n - inter; ++i) B.push_back(base + i); }

int main() {
    // ① 전체집합 {0..5} 의 모든 순열(720 개)과 모든 비어 있지 않은 쌍 (A, B): P[argmin_A == argmin_B] = |A∩B| / |A∪B| 가 정확히 성립
    {   const int U = 6; std::vector<int> perm(U); std::iota(perm.begin(), perm.end(), 0); std::vector<std::vector<int>> perms; do perms.push_back(perm); while (std::next_permutation(perm.begin(), perm.end())); assert(perms.size() == 720);
        for (int A = 1; A < (1 << U); ++A) for (int B = 1; B < (1 << U); ++B) {
            int match = 0; for (auto& rank : perms) { int ma = -1, mb = -1; for (int x = 0; x < U; ++x) { if ((A >> x & 1) && (ma < 0 || rank[x] < rank[ma])) ma = x; if ((B >> x & 1) && (mb < 0 || rank[x] < rank[mb])) mb = x; } match += ma == mb; }
            int inter = __builtin_popcount(A & B), uni = __builtin_popcount(A | B); assert(match * uni == inter * 720);
        }
    }
    // ② 통계: 편향 없음, 표준오차 = √(J(1−J)/K)
    std::mt19937_64 rng(4); double worstBias = 0, worstRatio = 0, bestRatio = 9;
    for (int inter : {36, 133, 190}) for (int K : {16, 64, 256}) {
        std::vector<u64> A, B; makePair(200, inter, 1000, A, B); double J = (double)inter / (400 - inter), se = std::sqrt(J * (1 - J) / K); double sum = 0, sq = 0; const int T = 400;
        for (int t = 0; t < T; ++t) { MinHash mh(K, 1000 + t); double e = MinHash::estimate(mh.sign(A), mh.sign(B)); sum += e - J; sq += (e - J) * (e - J); }
        double bias = sum / T, rms = std::sqrt(sq / T); assert(std::abs(bias) < 4 * se / std::sqrt((double)T) && rms > 0.8 * se && rms < 1.25 * se);
        worstBias = std::max(worstBias, std::abs(bias) / se); worstRatio = std::max(worstRatio, rms / se); bestRatio = std::min(bestRatio, rms / se);
    }
    // ③ 합집합 서명 = 칸별 최솟값 (정확히 같음), 같은 집합 → 1, 서로소 → 0
    for (int it = 0; it < 100; ++it) {
        std::vector<u64> A(1 + rng() % 50), B(1 + rng() % 50), AB; for (u64& x : A) x = rng() % 200; for (u64& x : B) x = rng() % 200; AB = A; AB.insert(AB.end(), B.begin(), B.end());
        MinHash mh(64, it); assert(mh.sign(AB) == MinHash::merge(mh.sign(A), mh.sign(B)) && MinHash::estimate(mh.sign(A), mh.sign(A)) == 1.0);
    }
    {   std::vector<u64> A, B; for (u64 i = 0; i < 300; ++i) { A.push_back(i); B.push_back(10000 + i); } MinHash mh(512, 5); assert(MinHash::estimate(mh.sign(A), mh.sign(B)) == 0.0); }
    // ④ b-비트 MinHash: 서명 크기를 b/64 로 줄여도 편향은 없고 분산만 커진다
    {   std::vector<u64> A, B; makePair(300, 150, 7, A, B); const double J = 1.0 / 3; const int K = 256, T = 300; double d1 = 0, d8 = 0;
        for (int t = 0; t < T; ++t) { MinHash mh(K, 77 + t); auto sa = mh.sign(A), sb = mh.sign(B); d1 += MinHash::estimateBBit(sa, sb, 1) - J; d8 += MinHash::estimateBBit(sa, sb, 8) - J; }
        double m1 = 0.5 + 0.5 * J, sd1 = std::sqrt(m1 * (1 - m1) / K) / 0.5, sd8 = std::sqrt(J * (1 - J) / K) / (1 - 1.0 / 256);       // 1 비트는 표준편차가 약 2 배
        assert(std::abs(d1 / T) < 4 * sd1 / std::sqrt((double)T) && std::abs(d8 / T) < 4 * sd8 / std::sqrt((double)T) && sd1 > 1.8 * sd8); }
    // ⑤ bottom-k: 해시를 한 번만 쓰고도 비슷한 정확도 (k = 256, 두 집합 각 5000 개)
    {   std::vector<u64> A, B; makePair(5000, 2500, 91, A, B); double J = 2500.0 / 7500, errMax = 0;
        for (int t = 0; t < 100; ++t) { u64 seed = 900 + t; double e = bottomKJaccard(bottomK(A, 256, seed), bottomK(B, 256, seed), 256); errMax = std::max(errMax, std::abs(e - J)); }
        assert(errMax < 4.5 * std::sqrt(J * (1 - J) / 256)); }
    // ⑥ 문서: 3-글자 조각(shingle) 집합의 Jaccard vs MinHash (서명 K = 256)
    {   auto shingles = [](const std::string& s) { std::vector<u64> r; for (std::size_t i = 0; i + 3 <= s.size(); ++i) r.push_back((u64)(unsigned char)s[i] << 16 | (u64)(unsigned char)s[i + 1] << 8 | (unsigned char)s[i + 2]); std::sort(r.begin(), r.end()); r.erase(std::unique(r.begin(), r.end()), r.end()); return r; };
        std::string base; for (int i = 0; i < 400; ++i) base += "abcdefghijklmnopqrstuvwxyz "[rng() % 27]; std::string edited = base; for (int i = 0; i < 20; ++i) edited[rng() % edited.size()] = 'Z'; std::string other; for (int i = 0; i < 400; ++i) other += "abcdefghijklmnopqrstuvwxyz "[rng() % 27];
        MinHash mh(256, 3); auto sb = mh.sign(shingles(base)), se = mh.sign(shingles(edited)), so = mh.sign(shingles(other));
        double j1 = exactJaccard(shingles(base), shingles(edited)), j2 = exactJaccard(shingles(base), shingles(other)); assert(std::abs(MinHash::estimate(sb, se) - j1) < 0.12 && std::abs(MinHash::estimate(sb, so) - j2) < 0.08 && j1 > j2 + 0.3);
    }
    // 큰 입력: 각 20 만 개, 절반 겹침 (J = 1/3), K = 256
    {   std::vector<u64> A, B; makePair(200000, 100000, 123456789, A, B); MinHash mh(256, 8); double e = MinHash::estimate(mh.sign(A), mh.sign(B)), J = 1.0 / 3; assert(std::abs(e - J) < 4 * std::sqrt(J * (1 - J) / 256));
        std::cout << "MinHash: all 720 permutations matched |A∩B|/|A∪B| exactly for every pair of non-empty subsets of 6 elements; over 9 (J, K) settings the largest |bias| was " << worstBias << " x sqrt(J(1-J)/K) and the RMS error stayed within [" << bestRatio << ", " << worstRatio << "] x sqrt(J(1-J)/K); 2*10^5-element sets (J=1/3) gave " << e << std::endl; }
    return 0;
}
// Time Complexity: 서명 O(|S|·K), 비교 O(K), bottom-k 는 O(|S| log k)
// Space Complexity: O(K) (b-비트 MinHash 는 K·b 비트)
```
## SemanticHashing()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <random>
#include <vector>
#include <cassert>

// 의미 해싱(임베딩용): 무작위 초평면 LSH.  벡터를 초평면 B 개의 어느 쪽에 있는지(부호)로 B 비트 코드로 만든다.
// 두 벡터의 비트가 다를 확률 = 각도 θ/π  ->  해밍 거리로 코사인 유사도를 근사하고, 대규모 임베딩 검색에서 후보를 빠르게 줄인다.
// (학습으로 코드를 얻는 "semantic hashing" 의 기준선이 되는 방법)
const int D = 32, BITS = 256;
typedef std::vector<double> Vec;
double dot(const Vec& a, const Vec& b) { double s = 0; for (int i = 0; i < D; i++) s += a[i] * b[i]; return s; }
double norm(const Vec& a) { return std::sqrt(dot(a, a)); }

int main() {
    std::mt19937 rng(11);
    std::normal_distribution<double> N(0, 1);
    std::vector<Vec> planes(BITS, Vec(D));
    for (auto& p : planes) for (auto& x : p) x = N(rng);
    auto encode = [&](const Vec& v) { std::vector<bool> c(BITS); for (int i = 0; i < BITS; i++) c[i] = dot(planes[i], v) > 0; return c; };
    auto ham = [&](const std::vector<bool>& a, const std::vector<bool>& b) { int h = 0; for (int i = 0; i < BITS; i++) h += (a[i] != b[i]); return h; };

    Vec u(D), v(D), w(D);
    for (int i = 0; i < D; i++) { u[i] = N(rng); v[i] = u[i] + 0.4 * N(rng); w[i] = N(rng); }   // v 는 u 와 비슷, w 는 무관
    double angleUV = std::acos(dot(u, v) / (norm(u) * norm(v)));
    int hUV = ham(encode(u), encode(v)), hUW = ham(encode(u), encode(w));
    assert(hUV < hUW);
    double estAngle = M_PI * hUV / BITS;
    assert(std::fabs(estAngle - angleUV) < 0.25);                  // 해밍 거리로 각도를 근사
    std::cout << "angle(u,v)=" << angleUV << " estimated=" << estAngle << " hamming(u,v)=" << hUV << " hamming(u,w)=" << hUW << std::endl;
    return 0;
}
// Time Complexity: 인코딩 O(B·D), 비교 O(B/64) (비트 연산)
// Space Complexity: O(B·D) 초평면
```
# Part 15. 최신 연구
## SwissTable()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <unordered_map>
#include <vector>

// SwissTable(Abseil flat_hash_map, Rust hashbrown): 개방 주소법 + 제어 바이트.
// 슬롯 G 개를 한 그룹으로 묶고, 그룹마다 제어 바이트 G 개(빈 칸 0x80 / 삭제 0xFE / 사용 중이면 해시 하위 7비트 H2)를 둔다.
// 조회는 H2 가 같은 칸만 키를 비교하므로 캐시 미스와 키 비교가 크게 줄고, 실제 구현은 SSE2/NEON 한 명령으로 16칸을 동시에 검사한다.
// 여기서는 이식성을 위해 64 비트 정수 하나에 제어 바이트 8 개를 담고 *SWAR* (한 정수 연산으로 8 바이트를 동시에 비교)로 같은 일을 한다 — 리틀엔디언 호스트·GCC/Clang 가정.
// 그룹 안에 EMPTY 가 하나라도 있으면 그 그룹에서 탐사가 끝나므로, 삭제할 때 그 그룹에 이미 EMPTY 가 있으면 묘비 대신 EMPTY 로 되돌려도 안전하다(묘비가 쌓이지 않는다).
// 묘비 때문에 자리가 모자라면, 살아 있는 항목이 용량의 25/32 이하일 때는 같은 크기로 다시 짓고(묘비 청소), 그렇지 않으면 두 배로 키운다
// 검증: ① 손으로 짠 예  ② SWAR 바이트 일치 마스크가 스칼라 루프와 정확히 같음 (H2 256 가지 × 무작위 워드·심어 둔 일치)  ③ std::unordered_map 과 120 000 번 대조(삽입·덮어쓰기·삭제·조회)하고 불변식:
//        사용 중인 칸 수 = size, 묘비 수, growthLeft = 7/8·용량 - size - 묘비, 사용 중인 칸의 H2 가 키의 해시와 일치, 모든 키가 조회됨, 적재율 ≤ 7/8
//        ④ 삭제-삽입을 반복해도 묘비가 거의 쌓이지 않음(순진하게 항상 묘비를 남기는 규칙과 비교)  ⑤ H2 필터: 적재율 0.8 에서 실패 조회 한 번의 키 비교 횟수가 0.2 미만이고, 그룹의 사용 중인 칸을 다 비교하는 방식의 1/40 이하  ⑥ 방문한 그룹 수가 작음
class Swiss {
    static constexpr uint8_t EMPTY = 0x80, DELETED = 0xFE;
    static constexpr size_t G = 8;
    static constexpr uint64_t LO = 0x0101010101010101ULL, HI = 0x8080808080808080ULL;
    std::vector<uint8_t> ctrl; std::vector<uint64_t> key, val;
    size_t groups = 1, count = 0, growthLeft = 0, tomb = 0, grows_ = 0, inPlace_ = 0;
    static uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
    static size_t maxLoad(size_t cap) { return cap * 7 / 8; }
    void init(size_t g) { groups = g; ctrl.assign(g * G, EMPTY); key.assign(g * G, 0); val.assign(g * G, 0); count = tomb = 0; growthLeft = maxLoad(g * G); }
    uint64_t loadGroup(size_t g) const { uint64_t w; std::memcpy(&w, &ctrl[g * G], 8); return w; }
    static size_t firstSlot(uint64_t mask) { return (size_t)(__builtin_ctzll(mask) >> 3); }          // 마스크의 가장 낮은 비트가 속한 바이트 번호
    long findSlot(uint64_t k) const {
        uint64_t h = mix(k); uint8_t h2 = h & 0x7f; size_t g = (h >> 7) & (groups - 1);
        for (size_t step = 0;; ) {
            uint64_t w = loadGroup(g); ++groupsProbed;
            for (uint64_t m = matchByte(w, h2); m; m &= m - 1) { size_t s = g * G + firstSlot(m); ++keyCompares; if (key[s] == k) return (long)s; }
            if (matchByte(w, EMPTY)) return -1;                       // 빈 칸이 있는 그룹에서 끝난다
            ++step; g = (g + step) & (groups - 1);                    // 그룹 단위 삼각수 간격 (그룹 수가 2의 거듭제곱이면 모든 그룹을 한 번씩 방문)
        }
    }
    void insertNew(uint64_t k, uint64_t v) {                          // 키가 없다고 알고 있을 때: 탐사열의 첫 EMPTY/DELETED 칸에
        uint64_t h = mix(k); size_t g = (h >> 7) & (groups - 1);
        for (size_t step = 0;; ) {
            uint64_t m = loadGroup(g) & HI;                           // 최상위 비트가 켜진 바이트 = EMPTY 또는 DELETED
            if (m) { size_t s = g * G + firstSlot(m); if (ctrl[s] == EMPTY) --growthLeft; else --tomb; ctrl[s] = (uint8_t)(h & 0x7f); key[s] = k; val[s] = v; ++count; return; }
            ++step; g = (g + step) & (groups - 1);
        }
    }
    void rehashTo(size_t newGroups) {
        std::vector<uint64_t> ks, vs; for (size_t s = 0; s < ctrl.size(); s++) if (!(ctrl[s] & 0x80)) { ks.push_back(key[s]); vs.push_back(val[s]); }
        init(newGroups); for (size_t i = 0; i < ks.size(); i++) insertNew(ks[i], vs[i]);
    }
public:
    mutable long keyCompares = 0, groupsProbed = 0;
    static uint64_t matchByte(uint64_t w, uint8_t b) {                // 바이트가 b 인 위치의 최상위 비트를 켠 마스크 (정확: 거짓 양성 없음)
        uint64_t t = w ^ (LO * b);
        return ~(((t & ~HI) + ~HI + 0) | t) & HI;                    // t 의 바이트가 0 인 위치만 켜진다
    }
    Swiss() { init(1); }
    void put(uint64_t k, uint64_t v) {
        long f = findSlot(k);
        if (f >= 0) { val[f] = v; return; }
        if (growthLeft == 0) { if (count * 32 <= ctrl.size() * 25 && tomb > 0) { rehashTo(groups); ++inPlace_; } else { rehashTo(groups * 2); ++grows_; } }     // 묘비가 많으면 청소, 아니면 확장
        insertNew(k, v);
    }
    bool get(uint64_t k, uint64_t& v) const { long s = findSlot(k); if (s < 0) return false; v = val[s]; return true; }
    bool erase(uint64_t k) {
        long s = findSlot(k); if (s < 0) return false;
        size_t g = (size_t)s / G;
        if (matchByte(loadGroup(g), EMPTY)) { ctrl[s] = EMPTY; ++growthLeft; } else { ctrl[s] = DELETED; ++tomb; }       // 그룹에 EMPTY 가 있으면 묘비가 필요 없다
        --count; return true;
    }
    size_t size() const { return count; }
    size_t capacity() const { return ctrl.size(); }
    size_t tombstones() const { return tomb; }
    size_t grows() const { return grows_; }
    size_t inPlaceRehashes() const { return inPlace_; }
    bool valid() const {
        size_t full = 0, del = 0;
        for (size_t s = 0; s < ctrl.size(); s++) { uint8_t c = ctrl[s]; if (c == DELETED) ++del; else if (!(c & 0x80)) { ++full; if (c != (mix(key[s]) & 0x7f)) return false; long f = findSlot(key[s]); if (f != (long)s) return false; } else if (c != EMPTY) return false; }
        return full == count && del == tomb && growthLeft + count + tomb == maxLoad(ctrl.size());
    }
};

int main() {
    Swiss t;
    for (uint64_t k = 1; k <= 10000; k++) t.put(k * 2654435761ULL, k);
    uint64_t v;
    for (uint64_t k = 1; k <= 10000; k++) assert(t.get(k * 2654435761ULL, v) && v == k);
    for (uint64_t k = 1; k <= 10000; k += 2) assert(t.erase(k * 2654435761ULL));
    assert(t.size() == 5000 && !t.get(2654435761ULL, v) && t.get(2 * 2654435761ULL, v));
    for (uint64_t k = 1; k <= 10000; k += 2) t.put(k * 2654435761ULL, k + 1);          // 묘비 재사용
    assert(t.size() == 10000 && t.get(2654435761ULL, v) && v == 2);
    assert(double(t.size()) / t.capacity() <= 7.0 / 8.0 && t.valid());
    Swiss e; assert(!e.get(1, v) && !e.erase(1) && e.size() == 0 && e.valid()); e.put(0, 5); assert(e.get(0, v) && v == 5);        // 경계: 빈 표, 키 0
    // ② SWAR 마스크가 스칼라 루프와 같다
    std::mt19937_64 rng(11);
    for (int b = 0; b < 256; b++) for (int t2 = 0; t2 < 400; t2++) {
        uint64_t w = rng(); if (t2 % 3 == 0) for (int j = 0; j < 8; j++) if (rng() % 3 == 0) w = (w & ~(0xFFULL << (8 * j))) | ((uint64_t)b << (8 * j));      // 일치를 여러 곳에 심는다
        uint64_t want = 0; for (int j = 0; j < 8; j++) if (((w >> (8 * j)) & 0xFF) == (uint64_t)b) want |= 0x80ULL << (8 * j);
        assert(Swiss::matchByte(w, (uint8_t)b) == want);
    }
    // ③ 모델 대조
    Swiss s; std::unordered_map<uint64_t, uint64_t> ref; long inserts = 0;
    for (int step = 0; step < 120000; ++step) {
        uint64_t k = (rng() % (step < 60000 ? 4000 : 150)) * 0x9e3779b97f4a7c15ULL + 1; int op = (int)(rng() % 10);        // 앞 절반은 늘고 뒤 절반은 좁은 범위에서 넣고 지우기를 반복
        if (op < 5) { s.put(k, (uint64_t)step); ref[k] = (uint64_t)step; ++inserts; } else if (op < 8) assert(s.erase(k) == (ref.erase(k) > 0));
        else { uint64_t val; bool f = s.get(k, val); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || val == it->second)); }
        assert(s.size() == ref.size() && s.size() <= s.capacity() * 7 / 8);
        if (step % 600 == 0) assert(s.valid());
    }
    assert(s.valid() && s.grows() >= 5 && inserts > 50000);
    // ④ 묘비: 살아 있는 키 30 개를 유지하며 넣고 지우기 10 만 번 (용량 64 안팎)
    {   Swiss c; std::vector<uint64_t> alive; uint64_t next = 1; size_t maxTomb = 0;
        for (int i = 0; i < 30; i++) { c.put(next * 7919, 1); alive.push_back(next++ * 7919); }
        for (int i = 0; i < 100000; i++) { size_t at = rng() % alive.size(); assert(c.erase(alive[at])); alive[at] = next * 7919; c.put(next * 7919, 1); ++next; maxTomb = std::max(maxTomb, c.tombstones()); }
        assert(c.size() == 30 && c.valid() && c.capacity() <= 128 && maxTomb < c.capacity() / 2);
        // 비교용: 삭제가 항상 묘비를 남기면 EMPTY 가 사라져 같은 부하에서 청소(재구성)가 훨씬 자주 필요하다 — 여기서는 재구성 횟수로 측정
        assert(c.inPlaceRehashes() + c.grows() < 100000 / 20); }
    // ④-2 적재율 0.75 에서 넣고 지우기를 반복하면 가득 찬 그룹에 묘비가 생겨 청소(같은 크기로 재구성)가 일어나고, 그동안 용량은 커지지 않는다
    {   Swiss c; std::vector<uint64_t> alive; uint64_t next = 1; while (c.capacity() < 1024 || c.size() < 768) { c.put(next * 104729, 1); alive.push_back(next++ * 104729); if (c.capacity() > 1024) break; }
        while (c.size() < 768) { c.put(next * 104729, 1); alive.push_back(next++ * 104729); }
        size_t cap0 = c.capacity(), grows0 = c.grows(); size_t maxTomb = 0;
        for (int i = 0; i < 60000; i++) { size_t at = rng() % alive.size(); assert(c.erase(alive[at])); alive[at] = next * 104729; c.put(next * 104729, 1); ++next; maxTomb = std::max(maxTomb, c.tombstones()); }
        assert(c.capacity() == cap0 && c.grows() == grows0 && c.inPlaceRehashes() >= 1 && c.size() == alive.size() && c.valid() && maxTomb > 0); }
    // ⑤ H2 필터와 ⑥ 방문한 그룹 수 (적재율 0.8)
    {   Swiss big; const size_t target = 6553; uint64_t key = 1; while (big.size() < target) big.put(key++ * 0x9e3779b97f4a7c15ULL, 1);
        while ((double)big.size() / big.capacity() > 0.84 || (double)big.size() / big.capacity() < 0.7) { if ((double)big.size() / big.capacity() > 0.84) { big.erase((key - 1) * 0x9e3779b97f4a7c15ULL); --key; } else big.put(key++ * 0x9e3779b97f4a7c15ULL, 1); }
        double load = (double)big.size() / big.capacity(); big.keyCompares = 0; big.groupsProbed = 0; const int Q = 20000;
        for (int i = 0; i < Q; i++) { uint64_t val; bool hit = big.get(rng() | (1ULL << 63) | 1, val); assert(!hit); }         // 없는 키만 조회
        double perLookup = (double)big.keyCompares / Q, groupsPer = (double)big.groupsProbed / Q, naive = groupsPer * 8 * load;                 // 그룹 안의 사용 중인 칸을 전부 비교했다면
        assert(load > 0.7 && load <= 0.875 && perLookup < 0.2 && perLookup * 40 < naive && groupsPer < 3.0); }
    std::cout << "SwissTable size=" << t.size() << " capacity=" << t.capacity() << "; model run: " << s.grows() << " growths and " << s.inPlaceRehashes() << " in-place rehashes" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 그룹 단위 병렬 비교
// Space Complexity: O(n)  (슬롯당 제어 바이트 1개)
```
## LearnedHash()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iostream>
#include <random>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// 학습된 해시(Learned Index 의 아이디어): 키의 누적분포(CDF)를 모델로 학습하면 h(k) = CDF(k)·m 이 키를 슬롯에 균등·단조하게 펼친다.
// 무작위 해시는 적재율 1 에서 약 37 % 의 키가 충돌하지만(빈 슬롯 e^−1), 이미 아는 키 집합에 대해서는 CDF 가 정확할수록 충돌이 줄고 모델 크기가 정확도를 산다.
//  · 모델 = 정렬된 학습 키에서 step 개마다 뽑은 (키, 순위) 표본의 구간별 선형 보간 → 순위 추정 → 슬롯.  step = 1 이면 순위 그대로(완전·최소·단조 해시, 모델 크기 n).
//  · 한계도 같이 확인한다: 새 키(분포 이동)에는 보장이 없고 한 슬롯에 몰리며, 일반 해시와 달리 모델을 다시 학습시켜야 한다. 정확성(조회 결과)은 어떤 모델이든 유지된다.
typedef std::uint64_t u64;
static inline u64 mix(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
class LearnedModel {
    std::vector<double> sx, sy; std::size_t n;
public:
    LearnedModel(const std::vector<u64>& sortedDistinct, std::size_t step) : n(sortedDistinct.size()) {
        for (std::size_t i = 0; i < n; i += step) { sx.push_back((double)sortedDistinct[i]); sy.push_back((double)i); }
        if (sx.back() != (double)sortedDistinct.back()) { sx.push_back((double)sortedDistinct.back()); sy.push_back((double)n - 1); }
    }
    std::size_t modelSize() const { return sx.size(); }
    double rank(u64 key) const {                                         // 추정 순위 ∈ [0, n−1], 키에 대해 단조 비감소
        double k = (double)key; if (k <= sx.front()) return 0; if (k >= sx.back()) return (double)n - 1;
        std::size_t j = std::upper_bound(sx.begin(), sx.end(), k) - sx.begin(); double t = (k - sx[j - 1]) / (sx[j] - sx[j - 1]); return sy[j - 1] + t * (sy[j] - sy[j - 1]);
    }
    std::size_t slot(u64 key, std::size_t m) const { return std::min(m - 1, (std::size_t)(rank(key) * (double)m / (double)n)); }                // (순위 × m) / n 순서: step 1 에서 정수 나눗셈이 정확해진다
};
struct RandomHash { std::size_t m; std::size_t operator()(u64 k) const { return mix(k) % m; } };
struct LearnedHash { const LearnedModel* model; std::size_t m; std::size_t operator()(u64 k) const { return model->slot(k, m); } };
template <class H> struct ChainTable {                                   // 체인 테이블 (슬롯 함수만 바꿔 끼운다). 조회의 비교 횟수를 센다
    std::vector<std::vector<u64>> b; H h; std::size_t n = 0;
    ChainTable(std::size_t m, H hh) : b(m), h(hh) {}
    bool insert(u64 k) { auto& c = b[h(k)]; if (std::find(c.begin(), c.end(), k) != c.end()) return false; c.push_back(k); ++n; return true; }
    bool find(u64 k, long& probes) const { for (u64 x : b[h(k)]) { ++probes; if (x == k) return true; } return false; }
    bool erase(u64 k) { auto& c = b[h(k)]; auto it = std::find(c.begin(), c.end(), k); if (it == c.end()) return false; *it = c.back(); c.pop_back(); --n; return true; }
    std::size_t collisions() const { std::size_t used = 0; for (auto& c : b) used += !c.empty(); return n - used; }              // 키 수 − 쓰인 슬롯 수
    std::size_t maxLoad() const { std::size_t mx = 0; for (auto& c : b) mx = std::max(mx, c.size()); return mx; }
    double avgProbes(const std::vector<u64>& keys) const { long p = 0; for (u64 k : keys) { bool f = find(k, p); assert(f); (void)f; } return (double)p / keys.size(); }
};
std::vector<u64> distinctSorted(std::vector<u64> v) { std::sort(v.begin(), v.end()); v.erase(std::unique(v.begin(), v.end()), v.end()); return v; }

int main() {
    std::mt19937_64 rng(12); const std::size_t n = 20000;
    std::normal_distribution<double> gauss(0, 1);
    struct Dist { const char* name; std::vector<u64> keys; } dists[6];
    dists[0].name = "uniform";    for (std::size_t i = 0; i < n * 2; ++i) dists[0].keys.push_back(rng() >> 24);
    dists[1].name = "power gaps"; for (std::size_t i = 1; i <= n; ++i) dists[1].keys.push_back((u64)std::floor(1000.0 * std::pow((double)i, 1.5)));
    dists[2].name = "bell";       for (std::size_t i = 0; i < n * 2; ++i) dists[2].keys.push_back((u64)((double)(1ULL << 38) * (3 + gauss(rng))));
    dists[3].name = "clustered";  { std::vector<u64> centers; for (int c = 0; c < 20; ++c) centers.push_back(rng() >> 24); for (std::size_t i = 0; i < n * 2; ++i) dists[3].keys.push_back(centers[rng() % 20] + rng() % 100000); }
    dists[4].name = "gapped seq"; for (std::size_t i = 0; i < n; ++i) dists[4].keys.push_back(i * 10 + rng() % 4);
    dists[5].name = "log-normal"; for (std::size_t i = 0; i < n * 2; ++i) dists[5].keys.push_back((u64)std::exp(14 + 2 * gauss(rng)) + 1);
    // ① 여섯 가지 분포에서 (학습 키 자체에 대한) 충돌 수: 무작위 해시 ≈ 0.37 n.  표본 1/32 모델은 *규칙적인* 키 집합(간격이 매끈하게 변하는 것)에서만 크게 이기고,
    //    난수로 뽑은 키는 표본 사이의 무작위 요철을 배울 수 없어 무작위 해시와 비슷하다 (공짜 점심은 없다).  step 1 (모델 크기 n) 은 항상 0.
    double ratio[6]; int di = 0;
    for (auto& d : dists) {
        std::vector<u64> keys = distinctSorted(d.keys); if (keys.size() > n) keys.resize(n); std::size_t nn = keys.size(); assert(nn >= n * 9 / 10);
        LearnedModel coarse(keys, 32), exact(keys, 1); ChainTable<RandomHash> rnd(nn, RandomHash{nn}); ChainTable<LearnedHash> lrn(nn, LearnedHash{&coarse, nn}), perfect(nn, LearnedHash{&exact, nn});
        for (u64 k : keys) { rnd.insert(k); lrn.insert(k); perfect.insert(k); }
        assert(rnd.collisions() > 0.33 * nn && rnd.collisions() < 0.40 * nn);                                    // 푸아송: 빈 칸 비율 e^-1 → 충돌 ≈ 0.368 n
        assert(perfect.collisions() == 0 && perfect.maxLoad() == 1 && exact.modelSize() == nn);                    // step 1: 순위 자체가 완전·최소 해시, 모델 크기는 n
        assert(std::abs(rnd.avgProbes(keys) - 1.5) < 0.05);                                                     // 무작위 해시의 평균 비교 횟수 ≈ 1 + α/2 = 1.5
        ratio[di] = (double)lrn.collisions() / rnd.collisions(); if (di == 1) assert(ratio[di] < 0.15 && lrn.avgProbes(keys) < 1.15); else if (di == 4) assert(ratio[di] < 0.7 && lrn.avgProbes(keys) < 1.3); else assert(ratio[di] > 0.85); ++di;      // 매끈한 거듭제곱 간격 / 격자+잡음 / 나머지(난수 키)
    }
    // ② 모델 크기 대 충돌 (균등 분포): step 이 커질수록 모델은 작아지고 충돌은 늘어난다
    {   std::vector<u64> keys = distinctSorted(dists[0].keys); keys.resize(n); std::size_t prevColl = 0, firstColl = 0, lastColl = 0;
        for (std::size_t step : {1u, 2u, 4u, 16u, 64u, 256u, 1024u, 4096u}) {
            LearnedModel mod(keys, step); ChainTable<LearnedHash> t(n, LearnedHash{&mod, n}); for (u64 k : keys) t.insert(k); std::size_t c = t.collisions(); assert(mod.modelSize() <= n / step + 2);
            if (step == 1) { assert(c == 0); firstColl = c; } else assert(c + n / 50 >= prevColl);              // 거의 단조 증가 (표본 잡음 2 % 허용)
            prevColl = c; lastColl = c;
        }
        assert(lastColl > firstColl + n / 10);
    }
    // ③ 단조성: 모델의 슬롯은 키 순서를 보존 — 범위 질의에 쓸 수 있다 (무작위 해시는 불가).  학습하지 않은 임의 키에도 성립
    for (auto& d : dists) {
        std::vector<u64> keys = distinctSorted(d.keys); LearnedModel mod(keys, 16); std::vector<u64> probes; for (int i = 0; i < 100000; ++i) probes.push_back(rng() >> (rng() % 40)); std::sort(probes.begin(), probes.end());
        std::size_t prev = 0; for (u64 q : probes) { std::size_t s = mod.slot(q, 50000); assert(s >= prev && s < 50000); prev = s; }
    }
    // ④ 분포가 이동하면 보장이 사라진다: 균등 분포로 학습한 모델에 (a) 범위 밖의 새 키, (b) 범위 안의 좁은 구간의 새 키
    {   std::vector<u64> keys = distinctSorted(dists[0].keys); keys.resize(n); LearnedModel mod(keys, 32); u64 lo = keys.front(), hi = keys.back();
        std::vector<u64> outside, narrow; for (std::size_t i = 0; i < n; ++i) { outside.push_back(hi + 1 + rng() % 1000000000ULL); narrow.push_back(lo + (hi - lo) / 2 + rng() % ((hi - lo) / 1000)); }
        for (const std::vector<u64>* fresh : {&outside, &narrow}) {
            ChainTable<RandomHash> rnd(n, RandomHash{n}); ChainTable<LearnedHash> lrn(n, LearnedHash{&mod, n}); for (u64 k : *fresh) { rnd.insert(k); lrn.insert(k); }
            assert(lrn.collisions() > 2 * rnd.collisions() && lrn.maxLoad() > 20 * rnd.maxLoad());               // 몰림: 범위 밖은 마지막 슬롯 하나에 전부
            long p = 0; for (u64 k : *fresh) { bool f = lrn.find(k, p); assert(f); (void)f; }                      // 그래도 조회 결과는 정확하다 (느려질 뿐)
        }
    }
    // ⑤ 동적 사용: 학습 시점의 키 1 만 개 + 같은 분포의 새 키 삽입·삭제·조회를 std::unordered_map 과 대조 (정확성), 새 키에는 이점이 사라진다 (무작위 해시와 비슷한 비교 횟수)
    {   std::vector<u64> all = distinctSorted(dists[0].keys); std::shuffle(all.begin(), all.end(), rng); std::vector<u64> train(all.begin(), all.begin() + 10000), fresh(all.begin() + 10000, all.begin() + 20000);
        std::vector<u64> sortedTrain = distinctSorted(train); LearnedModel mod(sortedTrain, 16); ChainTable<LearnedHash> t(20000, LearnedHash{&mod, 20000}); ChainTable<RandomHash> r(20000, RandomHash{20000}); std::unordered_set<u64> ref;
        for (u64 k : train) { assert(t.insert(k) == r.insert(k)); ref.insert(k); }
        for (int op = 0; op < 60000; ++op) { u64 k = rng() % 3 ? all[rng() % 20000] : rng() >> 24; int t3 = (int)(rng() % 3); long p = 0;
            if (t3 == 0) { bool a = t.insert(k), b = r.insert(k), c = ref.insert(k).second; assert(a == c && b == c); } else if (t3 == 1) { bool a = t.erase(k), b = r.erase(k), c = ref.erase(k) > 0; assert(a == c && b == c); } else { bool a = t.find(k, p), b = r.find(k, p), c = ref.count(k) > 0; assert(a == c && b == c); } }
        assert(t.n == ref.size() && r.n == ref.size());
        ChainTable<LearnedHash> t2(20000, LearnedHash{&mod, 20000}); ChainTable<RandomHash> r2(20000, RandomHash{20000}); for (u64 k : fresh) { t2.insert(k); r2.insert(k); }
        double pl = t2.avgProbes(fresh), pr = r2.avgProbes(fresh); assert(pl > 0.85 * pr && pl < 1.2 * pr);
        std::cout << "LearnedHash: collisions of a 1/32-sized CDF model relative to random hashing (~37% of keys collide): "; for (int i = 0; i < 6; ++i) std::cout << dists[i].name << " " << ratio[i] << (i < 5 ? ", " : "; "); std::cout << "a full-rank model (size n) gave 0 collisions; keys unseen by the model got " << pl << " probes on average vs " << pr << " for random hashing" << std::endl;
    }
    // 큰 입력: 매끈하게 벌어지는 키 100 만 개, 표본 간격 64 (모델 크기 약 1.6 만 = n/64) — 규칙성이 있으면 큰 입력에서도 같은 효과
    {   std::vector<u64> keys; for (u64 i = 1; i <= 1000000; ++i) keys.push_back((u64)std::floor(2000.0 * std::pow((double)i, 1.5))); LearnedModel mod(keys, 64); const std::size_t m = keys.size();
        std::vector<char> usedL(m, 0), usedR(m, 0); std::size_t distL = 0, distR = 0; for (u64 k : keys) { std::size_t a = mod.slot(k, m), b = mix(k) % m; distL += !usedL[a]; usedL[a] = 1; distR += !usedR[b]; usedR[b] = 1; }
        assert(m - distL < 0.25 * (m - distR) && mod.modelSize() < m / 60); }
    return 0;
}
// Time Complexity: 조회 O(log S) (S = 표본 수, 균등 분할 표를 쓰면 O(1)), 학습 O(n)
// Space Complexity: O(n / step)
```
# Part 16. 해시 성능 시각화
## CollisionVisualization()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 충돌을 눈으로 본다. 12 개의 키를 버킷 8 개에 넣으면 ■ 가 버킷의 첫 원소, ▲ 는 충돌한 추가 원소다.
//  ① 그림 + 비둘기집 원리(충돌 수 = 키 수 − 사용된 버킷 수 ≥ n − m).  ② "사용된 버킷 수"의 분포를 점유 DP 로 *정확히* 구해, 시드를 바꿔 가며 만든 20 만 개의 해시 함수 결과와 대조.
//  ③ 생일 역설: 충돌 확률이 처음 1/2 를 넘는 키 수 (m=365 → 23, m=2^32 → 77164 — 흔히 인용되는 77163 은 √(2m ln 2) 근사, 근사 1.1774·√m).  ④ 키 100 만 개를 2^20 칸에 넣은 버킷 적재량 히스토그램 vs 푸아송 분포.
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
uint64_t fnv(const std::string& s, uint64_t seed) { uint64_t h = 1469598103934665603ULL ^ seed; for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; } return mix(h); }       // 시드로 해시 함수 가족을 만든다
std::vector<double> usedDistribution(int n, int m) {                      // P[u] = 키 n 개를 버킷 m 개에 던졌을 때 정확히 u 개 버킷이 쓰일 확률
    std::vector<double> dp(m + 1, 0.0); dp[0] = 1;
    for (int t = 0; t < n; ++t) { std::vector<double> nd(m + 1, 0.0); for (int u = 0; u <= m; ++u) { nd[u] += dp[u] * u / m; if (u < m) nd[u + 1] += dp[u] * (m - u) / m; } dp.swap(nd); }
    return dp;
}
long double collisionProbability(long n, long double m) { long double logNo = 0; for (long i = 1; i < n; ++i) logNo += log1pl(-(long double)i / m); return 1 - expl(logNo); }
long minKeysForHalf(long double m) { long double logNo = 0; for (long n = 1;; ++n) { logNo += log1pl(-(long double)n / m); if (1 - expl(logNo) >= 0.5L) return n + 1; } }       // n 번째 키까지 넣어 처음 ≥ 1/2

int main() {
    const char* words[] = {"apple", "banana", "cherry", "date", "elder", "fig", "grape", "honey", "iris", "jade", "kiwi", "lemon"};
    // ① 그림
    {   std::vector<std::vector<std::string>> bucket(8); for (auto w : words) bucket[fnv(w, 0) % 8].push_back(w); size_t collisions = 0, used = 0;
        for (size_t i = 0; i < bucket.size(); ++i) { std::cout << "[" << i << "] "; for (size_t j = 0; j < bucket[i].size(); ++j) std::cout << (j == 0 ? "■ " : "▲ ") << bucket[i][j] << "  "; std::cout << "\n"; if (!bucket[i].empty()) { ++used; collisions += bucket[i].size() - 1; } }
        assert(collisions == 12 - used && collisions >= 4);                // 충돌 수 = 키 수 − 사용된 버킷 수, 12 개를 8 칸에 넣으면 최소 4 번
    }
    // ② 정확한 분포 vs 20 만 개의 시드별 해시 함수
    {   std::vector<double> exact = usedDistribution(12, 8), mean; double expect = 0; for (int u = 0; u <= 8; ++u) expect += u * exact[u];
        assert(std::abs(expect - 8 * (1 - std::pow(1 - 1.0 / 8, 12))) < 1e-12 && exact[0] == 0 && exact[1] < 1e-9);       // 독립 닫힌 꼴: m(1 − (1 − 1/m)^n)
        const int R = 200000; std::vector<int> cnt(9, 0); for (int seed = 0; seed < R; ++seed) { std::vector<char> hit(8, 0); int u = 0; for (auto w : words) { size_t b = fnv(w, (uint64_t)seed * 0x9e3779b97f4a7c15ULL) % 8; u += !hit[b]; hit[b] = 1; } ++cnt[u]; }
        double worst = 0; for (int u = 0; u <= 8; ++u) { double p = exact[u], sd = std::sqrt(p * (1 - p) / R); worst = std::max(worst, std::abs((double)cnt[u] / R - p) / (sd + 1e-12)); assert(std::abs((double)cnt[u] / R - p) <= 5 * sd + 1e-9); }
        std::cout << "used buckets (exact vs 200000 hash functions):"; for (int u = 4; u <= 8; ++u) std::cout << "  " << u << ": " << exact[u] << " / " << (double)cnt[u] / R; std::cout << "  (largest deviation " << worst << " sd)\n";
    }
    // ③ 생일 역설
    long n365 = minKeysForHalf(365), n32 = minKeysForHalf(4294967296.0L); assert(n365 == 23 && n32 == 77164);                                        // 정확한 값은 77164 (흔히 인용되는 77163 은 √(2m ln 2) 근사)
    for (long double m : {1e3L, 1e4L, 1e5L, 1e6L, 4294967296.0L}) { long n = minKeysForHalf(m); assert(std::abs((double)n / (1.1774 * std::sqrt((double)m)) - 1) < 0.03); }
    {   std::mt19937_64 rng(3); const int m = 1000, R = 100000; long n = minKeysForHalf(m); double p = (double)collisionProbability(n, m); int hits = 0;
        for (int r = 0; r < R; ++r) { std::vector<char> seen(m, 0); for (long i = 0; i < n; ++i) { size_t b = rng() % m; if (seen[b]) { ++hits; break; } seen[b] = 1; } }
        assert(n == 38 && std::abs((double)hits / R - p) < 5 * std::sqrt(p * (1 - p) / R)); }
    // ④ 키 100 만 개를 2^20 칸에: 버킷 적재량 히스토그램 vs 푸아송(λ = n/m)
    {   const uint64_t n = 1000000, m = 1ULL << 20; std::vector<int> load(m, 0); for (uint64_t i = 0; i < n; ++i) ++load[mix(i) % m];
        double lambda = (double)n / m; std::vector<long> hist(6, 0); size_t used = 0; for (int l : load) { ++hist[std::min(l, 5)]; used += l > 0; }
        std::cout << "keys per bucket   (bars = buckets/4000; Poisson prediction in parentheses)\n"; double pk = std::exp(-lambda);
        for (int k = 0; k <= 5; ++k) { double pred = k < 5 ? pk * m : m; if (k == 5) { double cum = 0, q = std::exp(-lambda); for (int j = 0; j < 5; ++j) { cum += q; q *= lambda / (j + 1); } pred = (1 - cum) * m; } std::cout << "  " << k << (k == 5 ? "+" : " ") << " " << std::string(hist[k] / 4000, '#') << " " << hist[k] << " (" << (long)pred << ")\n";
            assert(std::abs(hist[k] - pred) < 6 * std::sqrt(pred) + 2); pk *= lambda / (k + 1); }
        double expectedCollisions = n - m * (1 - std::pow(1 - 1.0 / m, (double)n)); assert(std::abs((double)(n - used) - expectedCollisions) < 0.005 * expectedCollisions);
        std::cout << "keys=" << n << " buckets=" << m << " collisions=" << n - used << " (expected " << expectedCollisions << ")" << std::endl; }
    return 0;
}
// Time Complexity: DP O(n·m), 분포 측정 O(n)
// Space Complexity: O(m)
```
## BucketDistribution()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 버킷 분포를 히스토그램과 카이제곱(χ²) 검정으로 평가한다. 균등하면 χ² ≈ 자유도(m−1) 이고, p-값 P[χ² ≥ 관측] 이 매우 작으면 치우친 해시다.
//  ① 정규화 불완전 감마로 p-값을 직접 구현하고 표준 분위수(df=1: 3.841, 63: 82.529, 100: 124.342 → p=0.05)로 검증.  ② 좋은 해시의 p-값은 [0,1] 에서 균등 (콜모고로프–스미르노프).
//  ③ 해시 6 가지 × 키 패턴 5 가지 표: 항등 해시 % 2^k 는 간격 키에서 몰리고, 소수 나머지는 소수의 배수 키에서 몰리며, 곱셈 해시는 상위 비트를 써야 한다.
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
double gammaQ(double a, double x) {                                      // 정규화 상위 불완전 감마 Q(a, x) = 1 − P(a, x)  (Numerical Recipes 방식: 급수 / 연분수)
    if (x <= 0) return 1;
    if (x < a + 1) { double ap = a, sum = 1 / a, del = sum; for (int n = 0; n < 1000; ++n) { ap += 1; del *= x / ap; sum += del; if (std::abs(del) < std::abs(sum) * 1e-15) break; } return 1 - sum * std::exp(-x + a * std::log(x) - std::lgamma(a)); }
    double b = x + 1 - a, c = 1e300, d = 1 / b, h = d; for (int i = 1; i < 1000; ++i) { double an = -i * (i - a); b += 2; d = an * d + b; if (std::abs(d) < 1e-300) d = 1e-300; c = b + an / c; if (std::abs(c) < 1e-300) c = 1e-300; d = 1 / d; double del = d * c; h *= del; if (std::abs(del - 1) < 1e-15) break; }
    return std::exp(-x + a * std::log(x) - std::lgamma(a)) * h;
}
double chiSquareP(double chi, int df) { return gammaQ(df / 2.0, chi / 2.0); }
double chiSquare(const std::vector<long>& c, long n) { double e = (double)n / c.size(), s = 0; for (long x : c) s += (x - e) * (x - e) / e; return s; }
void bars(const char* name, const std::vector<long>& c, long n) {
    std::cout << name << "\n"; for (size_t i = 0; i < c.size(); i += 8) { long sum = 0; for (size_t j = i; j < i + 8; ++j) sum += c[j]; std::cout << "  [" << i << ".." << i + 7 << "] " << std::string(sum / 40, '#') << " " << sum << "\n"; } (void)n;
}
typedef uint32_t (*Hash32)(uint32_t);
uint32_t hIdentity(uint32_t x) { return x; }
uint32_t hMulLow(uint32_t x) { return x * 2654435769u; }                  // 곱셈 해시, 버킷 = 하위 비트
uint32_t hMulHigh(uint32_t x) { return (x * 2654435769u) >> 26; }         // 곱셈(피보나치) 해시, 버킷 = 상위 6 비트
uint32_t hFmix(uint32_t h) { h ^= h >> 16; h *= 0x85ebca6bu; h ^= h >> 13; h *= 0xc2b2ae35u; h ^= h >> 16; return h; }
uint32_t hFnv(uint32_t x) { uint32_t h = 2166136261u; for (int i = 0; i < 4; ++i) { h ^= (x >> (8 * i)) & 0xff; h *= 16777619u; } return h; }

int main() {
    // ① 구현 검증: 표준 카이제곱 분위수에서 p ≈ 0.05, 그리고 df=2 에서는 닫힌 꼴 p = e^(−x/2)
    assert(std::abs(chiSquareP(3.841, 1) - 0.05) < 2e-4 && std::abs(chiSquareP(82.529, 63) - 0.05) < 2e-4 && std::abs(chiSquareP(124.342, 100) - 0.05) < 2e-4 && std::abs(chiSquareP(18.307, 10) - 0.05) < 2e-4);
    for (double x : {0.5, 2.0, 7.0, 30.0}) assert(std::abs(chiSquareP(x, 2) - std::exp(-x / 2)) < 1e-12);
    // 원래 예: 8 의 배수 키 만 개를 64 칸에 — 좋은 해시 vs 단순 나머지
    const int m = 64; const long n = 10000;
    {   std::vector<long> good(m, 0), bad(m, 0); for (long i = 0; i < n; ++i) { uint64_t key = (uint64_t)i * 8; ++good[mix(key) % m]; ++bad[key % m]; }
        bars("good hash", good, n); bars("bad hash (k mod 64, keys multiple of 8)", bad, n);
        double cg = chiSquare(good, n), cb = chiSquare(bad, n); assert(chiSquareP(cg, m - 1) > 0.001 && chiSquareP(cb, m - 1) < 1e-300 + 1e-100 && std::count(bad.begin(), bad.end(), 0L) == 56);      // 8 개 버킷만 쓰인다
        std::cout << "chi-square: good=" << cg << " (p=" << chiSquareP(cg, m - 1) << ") bad=" << cb << " (p<1e-100)\n"; }
    // ② 좋은 해시의 p-값은 균등 분포: 무작위 키 집합 400 개 → p-값의 KS 통계량
    {   std::mt19937_64 rng(8); std::vector<double> ps; for (int t = 0; t < 400; ++t) { std::vector<long> c(m, 0); for (long i = 0; i < n; ++i) ++c[mix(rng()) % m]; ps.push_back(chiSquareP(chiSquare(c, n), m - 1)); }
        std::sort(ps.begin(), ps.end()); double ks = 0; for (size_t i = 0; i < ps.size(); ++i) ks = std::max({ks, std::abs(ps[i] - (double)(i + 1) / ps.size()), std::abs(ps[i] - (double)i / ps.size())});
        long below = std::count_if(ps.begin(), ps.end(), [](double p) { return p < 0.05; }); assert(ks < 1.63 / std::sqrt(400.0) && below > 5 && below < 40);
        std::cout << "400 random key sets: KS distance of p-values to uniform = " << ks << " (1% critical " << 1.63 / std::sqrt(400.0) << "), " << below << " below 0.05\n"; }
    // ③ 해시 × 키 패턴: χ²/자유도 (균등이면 ≈ 1)
    struct H { const char* name; Hash32 f; int mod; } hs[] = {{"identity % 64", hIdentity, 64}, {"identity % 67 (prime)", hIdentity, 67}, {"mul low bits % 64", hMulLow, 64}, {"mul high bits % 64", hMulHigh, 64}, {"fnv1a % 64", hFnv, 64}, {"fmix32 % 64", hFmix, 64}};
    struct P { const char* name; uint32_t stride; } ps[] = {{"seq", 1}, {"x8", 8}, {"x64", 64}, {"x67", 67}, {"x1000", 1000}};
    double tab[6][5]; std::cout << "chi2/df     "; for (auto& p : ps) std::cout << p.name << "\t"; std::cout << "\n";
    for (int i = 0; i < 6; ++i) { std::cout << hs[i].name << "\t"; for (int j = 0; j < 5; ++j) { std::vector<long> c(hs[i].mod, 0); for (long k = 0; k < n; ++k) ++c[hs[i].f((uint32_t)k * ps[j].stride + 12345u) % hs[i].mod]; tab[i][j] = chiSquare(c, n) / (hs[i].mod - 1); std::cout << tab[i][j] << "\t"; } std::cout << "\n"; }
    assert(tab[0][0] < 0.01 && tab[0][1] > 100 && tab[0][2] > 1000);       // 항등 % 64: 연속 키는 완벽, 8·64 간격은 몰린다
    assert(tab[1][0] < 0.01 && tab[1][1] < 0.02 && tab[1][2] < 0.05 && tab[1][3] > 1000);       // 소수 나머지: 2 의 거듭제곱 간격은 괜찮지만 소수의 배수 키(x67) 는 한 버킷
    assert(tab[2][2] > 100);                                                // 곱셈 해시의 하위 비트: 64 의 배수 키는 하위 6 비트가 상수(홀수 곱이라 변하지 않음)
    for (int j = 0; j < 5; ++j) { assert(tab[3][j] < 5); assert(chiSquareP(tab[5][j] * 63, 63) > 1e-4); }     // 상위 비트·fmix32 는 모든 패턴에서 균등
    return 0;
}
// Time Complexity: O(n + m)
// Space Complexity: O(m)
```
## ProbeSequence()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 같은 키(홈=3, m=11)의 탐사 순서를 세 방식으로 나란히 보고, 어떤 (m, 보폭)에서 모든 칸을 방문하는지를 전수 확인한다.
//  · 선형 h+i: 항상 전 칸.  · 이차 h+i²: 소수 m 에서는 (m+1)/2 칸만 방문 → 적재율 1/2 이하여야 삽입이 보장.  · 삼각수 h+i(i+1)/2: m 이 2 의 거듭제곱일 때만 전 칸.
//  · 이중 해싱 h+i·h2: 방문하는 칸 수 = m/gcd(h2, m) → m 이 소수이거나 h2 가 m 과 서로소여야 전 칸.
typedef std::vector<unsigned> Seq;
Seq linear(unsigned h, unsigned m)    { Seq s; for (unsigned i = 0; i < m; ++i) s.push_back((h + i) % m); return s; }
Seq quadratic(unsigned h, unsigned m) { Seq s; for (unsigned i = 0; i < m; ++i) s.push_back((unsigned)((h + (unsigned long long)i * i) % m)); return s; }
Seq triangular(unsigned h, unsigned m){ Seq s; for (unsigned i = 0; i < m; ++i) s.push_back((unsigned)((h + (unsigned long long)i * (i + 1) / 2) % m)); return s; }
Seq doubleHash(unsigned h, unsigned h2, unsigned m) { Seq s; for (unsigned i = 0; i < m; ++i) s.push_back((unsigned)((h + (unsigned long long)i * h2) % m)); return s; }
size_t distinctCount(const Seq& s) { return std::set<unsigned>(s.begin(), s.end()).size(); }
bool isPrime(unsigned n) { if (n < 2) return false; for (unsigned d = 2; d * d <= n; ++d) if (n % d == 0) return false; return true; }
void show(const char* name, const Seq& s, unsigned m) {
    std::cout << name << ": "; for (size_t i = 0; i < s.size(); ++i) std::cout << s[i] << (i + 1 < s.size() ? " -> " : "\n");
    std::vector<int> order(m, -1); for (size_t i = 0; i < s.size(); ++i) if (order[s[i]] < 0) order[s[i]] = (int)i;         // 칸별 처음 방문한 순번 (빈칸 = 방문 안 함)
    std::cout << "           slot:"; for (unsigned i = 0; i < m; ++i) std::cout << " " << i; std::cout << "\n           step:"; for (unsigned i = 0; i < m; ++i) { if (order[i] < 0) std::cout << " ."; else std::cout << " " << order[i]; } std::cout << "\n";
}

int main() {
    const unsigned m = 11, home = 3, step = 4;                       // 이중 해싱의 보폭 h2 = 4
    Seq a = linear(home, m), b = quadratic(home, m), c = doubleHash(home, step, m);
    show("linear   ", a, m); show("quadratic", b, m); show("double   ", c, m);
    assert(a[0] == home && b[0] == home && c[0] == home && distinctCount(a) == m && distinctCount(c) == m && distinctCount(b) == 6);       // i² 는 m=11 에서 6 칸만
    // ① 이차 탐사: 소수 p 에서 정확히 (p+1)/2 칸, 처음 (p+1)/2 번의 탐사는 서로 다르다.  합성수에서는 제곱수(잉여) 개수와 같다 (독립 계산)
    for (unsigned p = 3; p < 400; ++p) {
        if (isPrime(p)) { for (unsigned h : {0u, 1u, p - 1}) { Seq q = quadratic(h, p); assert(distinctCount(q) == (p + 1) / 2); assert(distinctCount(Seq(q.begin(), q.begin() + (p + 1) / 2)) == (p + 1) / 2); } }
        std::set<unsigned> squares; for (unsigned x = 0; x < p; ++x) squares.insert((x * x) % p); assert(distinctCount(quadratic(0, p)) == squares.size());
    }
    // ② 삼각수 탐사: m ≤ 300 에서 전 칸 방문 ⇔ m 이 2 의 거듭제곱
    for (unsigned mm = 1; mm <= 300; ++mm) assert((distinctCount(triangular(0, mm)) == mm) == ((mm & (mm - 1)) == 0));
    // ③ 이중 해싱: m ≤ 60 의 모든 보폭에서 방문 칸 수 = m / gcd(h2, m)
    for (unsigned mm = 2; mm <= 60; ++mm) for (unsigned h2 = 1; h2 < mm; ++h2) assert(distinctCount(doubleHash(7 % mm, h2, mm)) == mm / std::gcd(h2, mm));
    // ④ 이차 탐사의 삽입 보장: 소수 p, 점유 칸이 (p−1)/2 개 이하면 어떤 점유 상태·홈에서도 (p+1)/2 번 안에 빈 칸을 찾는다 (p=7, 11 전수).  점유가 (p+1)/2 이면 막힐 수 있다 (빈 칸이 남아 있어도)
    for (unsigned p : {7u, 11u}) {
        for (unsigned occ = 0; occ < (1u << p); ++occ) { unsigned cnt = __builtin_popcount(occ); if (cnt > (p - 1) / 2) continue; for (unsigned h = 0; h < p; ++h) { Seq q = quadratic(h, p); bool found = false; for (unsigned i = 0; i < (p + 1) / 2; ++i) if (!(occ >> q[i] & 1)) found = true; assert(found); } }
    }
    for (unsigned p = 5; p < 100; ++p) if (isPrime(p)) { Seq q = quadratic(0, p); std::set<unsigned> block(q.begin(), q.end()); assert(block.size() == (p + 1) / 2 && p - block.size() == (p - 1) / 2); bool blocked = true; for (unsigned s : q) blocked = blocked && block.count(s); assert(blocked); }   // 점유 (p+1)/2 개로 홈 0 의 모든 탐사가 막힌다
    // ⑤ 탐사 횟수: 소수 m=10007 에 무작위 홈으로 αm 개를 넣은 뒤, 새 키가 빈 칸을 찾을 때까지의 평균 탐사 수 (실패 탐색)
    {   const unsigned M = 10007; std::mt19937_64 rng(5);
        auto trial = [&](double alpha, int kind) {                   // 0 = 선형, 1 = 이중 해싱, 2 = 이차.  표 8 개의 평균 (클러스터 요동을 줄인다)
            auto probeAt = [&](unsigned h, unsigned h2, unsigned i) -> unsigned { if (kind == 0) return (h + i) % M; if (kind == 1) return (unsigned)((h + (unsigned long long)i * h2) % M); return (unsigned)((h + (unsigned long long)i * i) % M); };
            double total = 0; const int TABLES = 8, Q = 20000;
            for (int tb = 0; tb < TABLES; ++tb) {
                std::vector<char> used(M, 0); for (unsigned n = 0; n < (unsigned)(alpha * M); ++n) { unsigned h = rng() % M, h2 = 1 + rng() % (M - 1), i = 0; while (used[probeAt(h, h2, i)]) ++i; used[probeAt(h, h2, i)] = 1; }
                double sum = 0; for (int q = 0; q < Q; ++q) { unsigned h = rng() % M, h2 = 1 + rng() % (M - 1), i = 0; while (used[probeAt(h, h2, i)]) ++i; sum += i + 1; } total += sum / Q;
            }
            return total / TABLES; };
        for (double alpha : {0.5, 0.8}) {
            double lin = trial(alpha, 0), dbl = trial(alpha, 1), linTheory = 0.5 * (1 + 1 / ((1 - alpha) * (1 - alpha))), dblTheory = 1 / (1 - alpha);
            std::cout << "alpha=" << alpha << ": unsuccessful probes linear " << lin << " (Knuth " << linTheory << "), double hashing " << dbl << " (1/(1-alpha) = " << dblTheory << ")\n";
            assert(std::abs(lin - linTheory) < 0.08 * linTheory && std::abs(dbl - dblTheory) < 0.06 * dblTheory && lin > dbl);
        }
        double quad = trial(0.5, 2), quadTheory = 1 / (1 - 0.5) - 0.5 - std::log(1 - 0.5); assert(std::abs(quad - quadTheory) < 0.08 * quadTheory);       // 이차 탐사 (α ≤ 1/2): Knuth 근사
        std::cout << "quadratic at alpha=0.5: " << quad << " (approx " << quadTheory << ")" << std::endl; }
    return 0;
}
// Time Complexity: 탐사열 생성 O(m), 평균 탐사 수 선형 ½(1+1/(1−α)²) / 이중 1/(1−α)
// Space Complexity: O(m)
```
## ResizeAnimation()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 체이닝 테이블이 확장되는 순간을 프레임별로 출력한다 (적재율 0.75 초과 시 버킷 2배, h(k) = k mod m).
//  ① 프레임 + 분할 성질: m 이 2 의 거듭제곱이고 m → 2m 으로 키우면 모든 키는 제자리(i)이거나 i+m 으로만 옮겨 간다 (한 버킷이 둘로 갈라진다).
//  ② 소수 크기(7 → 17)로 키우면 거의 모든 키가 다른 버킷으로 이동 (정확히 1 − 7/119 = 94.1 %).  ③ 키우는 정책별 총 재배치 횟수 — ×2: ≤ 2N, ×1.5: ≤ 3N, +k: 이차.
int main() {
    std::vector<std::vector<int>> b(2); size_t n = 0, frame = 0, resizes = 0;
    auto draw = [&](const std::string& why) { std::cout << "frame " << frame++ << " (" << why << ", n=" << n << ", m=" << b.size() << ")\n"; for (size_t i = 0; i < b.size(); ++i) { std::cout << "  [" << i << "]"; for (int k : b[i]) std::cout << " " << k; std::cout << "\n"; } };
    draw("empty");
    for (int k : {10, 21, 32, 43, 54, 65}) {
        if (double(n + 1) / b.size() > 0.75) {                    // 확장: 모든 키를 새 크기로 재배치
            std::vector<std::vector<int>> nb(b.size() * 2); size_t oldM = b.size(), moved = 0, total = 0;
            for (size_t i = 0; i < b.size(); ++i) for (int x : b[i]) { size_t j = (size_t)x % nb.size(); assert(j == i || j == i + oldM); nb[j].push_back(x); moved += j != i; ++total; std::cout << "    key " << x << ": [" << i << "] -> [" << j << "]" << (j == i ? " (stays)" : " (moves)") << "\n"; }
            b.swap(nb); ++resizes; draw("resized, " + std::to_string(moved) + "/" + std::to_string(total) + " keys moved");
        }
        b[(size_t)k % b.size()].push_back(k); ++n; draw("insert " + std::to_string(k));
    }
    assert(b.size() == 8 && resizes == 2);                         // 2 -> 4 -> 8
    size_t total = 0; for (auto& c : b) total += c.size(); assert(total == 6 && double(n) / b.size() <= 0.75);
    // ② 분할 성질과 이동 비율 (무작위 키 10 만 개, 크기 2^k → 2^(k+1)), 소수 크기에서는 거의 전부 이동
    std::mt19937_64 rng(2);
    for (unsigned k = 3; k <= 16; k += 3) {
        size_t m = 1u << k, moved = 0; const int N = 100000; for (int i = 0; i < N; ++i) { uint64_t key = rng(); size_t a = key % m, c = key % (2 * m); assert(c == a || c == a + m); moved += c != a; }
        assert(std::abs((double)moved / N - 0.5) < 5 * std::sqrt(0.25 / N));                   // 정확히 절반이 분할되어 나간다 (이항 오차 내)
    }
    {   size_t stay = 0, all = 119 * 1000; for (size_t key = 0; key < all; ++key) stay += key % 7 == key % 17; assert(stay * 17 == all && (double)(all - stay) / all > 0.94); }     // 7 → 17: 정확히 7/119 만 제자리
    // ③ 정책별 총 재배치: N 번 삽입(적재율 1 에서 확장) 동안 확장 때마다 그 시점의 원소 수만큼 이동
    const long N = 200000; struct Policy { const char* name; double factor; long add; } pol[] = {{"x2", 2.0, 0}, {"x1.5", 1.5, 0}, {"+64", 1.0, 64}};
    long moves[3];
    for (int p = 0; p < 3; ++p) { long cap = 16, mv = 0, rs = 0; for (long i = 1; i <= N; ++i) if (i > cap) { mv += i - 1; ++rs; cap = std::max(cap + 1, pol[p].add ? cap + pol[p].add : (long)(cap * pol[p].factor)); } moves[p] = mv; std::cout << pol[p].name << ": " << rs << " resizes, " << mv << " moves for " << N << " inserts (" << (double)mv / N << " per insert)\n"; }
    assert(moves[0] <= 2 * N && moves[1] <= 3 * N && moves[1] > moves[0] && moves[2] > 50 * moves[0]);     // 곱셈 정책은 분할상환 O(1), 덧셈 정책은 O(N/k) 로 훨씬 크다
    return 0;
}
// Time Complexity: 확장 1회 O(n), 삽입당 분할상환 O(1) (×2 정책)
// Space Complexity: O(n)
```
## ChainGrowth()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 적재율 α 가 커질 때 체인 길이 분포: 평균 길이 = α, 빈 버킷 비율 ≈ e^{-α} (푸아송 분포)
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }

int main() {
    const int m = 2000;
    std::mt19937_64 rng(99);
    for (double alpha : {0.25, 0.5, 1.0, 2.0, 4.0}) {
        int n = (int)(alpha * m);
        std::vector<int> len(m, 0);
        for (int i = 0; i < n; i++) len[mix(rng()) % m]++;
        int empty = 0, longest = 0; double mean = 0;
        std::vector<int> hist(12, 0);
        for (int x : len) { empty += (x == 0); longest = std::max(longest, x); mean += x; hist[std::min(x, 11)]++; }
        mean /= m;
        std::cout << "alpha=" << alpha << " mean=" << mean << " empty=" << 100.0 * empty / m << "% (e^-a=" << 100 * std::exp(-alpha) << "%) longest=" << longest << "\n";
        for (int c = 0; c < 6; c++) std::cout << "   len " << c << ": " << std::string(hist[c] * 40 / m, '#') << "\n";
        assert(std::fabs(mean - alpha) < 1e-9);                    // 평균 체인 길이는 정확히 α
        assert(std::fabs(double(empty) / m - std::exp(-alpha)) < 0.03);
    }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(m)
```
## ClusterFormation()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 선형 탐사의 1차 군집: 적재율이 커질수록 연속 점유 구간(클러스터)이 급격히 길어지고 평균 탐사 횟수가 폭증한다
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }

int main() {
    const int m = 2000;
    int longestAt[3]; double probes[3]; int idx = 0;
    for (double alpha : {0.5, 0.7, 0.9}) {
        std::mt19937_64 rng(123);
        std::vector<bool> used(m, false);
        long totalProbes = 0; int n = (int)(alpha * m);
        for (int i = 0; i < n; i++) {
            size_t p = mix(rng()) % m; int steps = 1;
            while (used[p]) { p = (p + 1) % m; steps++; }
            used[p] = true; totalProbes += steps;
        }
        int longest = 0, cur = 0;
        for (int i = 0; i < 2 * m; i++) { cur = used[i % m] ? cur + 1 : 0; longest = std::max(longest, std::min(cur, m)); }
        longestAt[idx] = longest; probes[idx] = double(totalProbes) / n; idx++;
        std::cout << "alpha=" << alpha << " longest cluster=" << longest << " avg probes/insert=" << double(totalProbes) / n << "\n  ";
        for (int i = 0; i < 64; i++) std::cout << (used[i] ? '#' : '.');
        std::cout << "\n";
    }
    assert(longestAt[2] > 3 * longestAt[0]);                       // 0.5 -> 0.9 에서 클러스터가 몇 배로 길어진다
    assert(probes[2] > 2 * probes[0]);
    return 0;
}
// Time Complexity: O(n · 평균 탐사)
// Space Complexity: O(m)
```
## AvalancheEffect()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>

// 눈사태 효과: 입력 1 비트를 뒤집으면 출력 비트의 *각각* 이 정확히 1/2 의 확률로 뒤집혀야 좋은 해시다 (엄격한 눈사태 기준, SAC).
// 32×32 격자(행 = 뒤집은 입력 비트, 열 = 출력 비트)의 칸마다 뒤집힌 비율을 재서 그림으로 본다:  '#' = 1/2 ± 0.05, '+' ±0.15, ':' ±0.3, '.' ±0.45, ' ' = 0 또는 1 에 가까움.
// 구조적으로 알 수 있는 사실을 전수로 확인한다 — 항등: 대각선만 1.  곱셈 x·C: 입력 비트 i 는 출력 비트 j < i 에 영향이 없고 j = i 는 항상 뒤집힘(삼각형).  CRC32 는 선형이라 모든 칸이 정확히 0 또는 1.
// FNV-1a: 바이트 안의 입력 비트 k 는 출력 비트 < k 에 영향 없음.  MurmurHash3 fmix32·lowbias32 는 모든 칸이 1/2 근처.
typedef std::uint32_t u32;
u32 hIdentity(u32 x) { return x; }
u32 hMul(u32 x) { return x * 2654435769u; }
u32 hFnv(u32 x) { u32 h = 2166136261u; for (int i = 0; i < 4; ++i) { h ^= (x >> (8 * i)) & 0xff; h *= 16777619u; } return h; }
u32 crcTable(int i) { u32 c = (u32)i; for (int k = 0; k < 8; ++k) c = c & 1 ? 0xEDB88320u ^ (c >> 1) : c >> 1; return c; }
u32 crc32(const unsigned char* p, std::size_t n) { static u32 t[256]; static bool init = false; if (!init) { for (int i = 0; i < 256; ++i) t[i] = crcTable(i); init = true; } u32 c = 0xFFFFFFFFu; for (std::size_t i = 0; i < n; ++i) c = t[(c ^ p[i]) & 0xff] ^ (c >> 8); return c ^ 0xFFFFFFFFu; }
u32 hCrc(u32 x) { unsigned char b[4] = {(unsigned char)x, (unsigned char)(x >> 8), (unsigned char)(x >> 16), (unsigned char)(x >> 24)}; return crc32(b, 4); }
u32 hFmix(u32 h) { h ^= h >> 16; h *= 0x85ebca6bu; h ^= h >> 13; h *= 0xc2b2ae35u; h ^= h >> 16; return h; }
u32 hLowbias(u32 x) { x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15; x *= 0x846ca68bu; x ^= x >> 16; return x; }
struct Matrix { double p[32][32]; double worst, rms; int zeros, ones, middle; };
Matrix measure(u32 (*f)(u32), int samples, std::mt19937& rng) {
    static long cnt[32][32]; for (auto& r : cnt) for (long& c : r) c = 0;
    for (int s = 0; s < samples; ++s) { u32 x = (u32)rng(), fx = f(x); for (int i = 0; i < 32; ++i) { u32 d = fx ^ f(x ^ (1u << i)); for (int j = 0; j < 32; ++j) cnt[i][j] += d >> j & 1; } }
    Matrix m{}; double sq = 0; for (int i = 0; i < 32; ++i) for (int j = 0; j < 32; ++j) { double p = (double)cnt[i][j] / samples; m.p[i][j] = p; m.worst = std::max(m.worst, std::abs(p - 0.5)); sq += (p - 0.5) * (p - 0.5); m.zeros += cnt[i][j] == 0; m.ones += cnt[i][j] == samples; m.middle += cnt[i][j] != 0 && cnt[i][j] != samples; }
    m.rms = std::sqrt(sq / 1024); return m;
}
char shade(double p) { double d = std::abs(p - 0.5); return d < 0.05 ? '#' : d < 0.15 ? '+' : d < 0.3 ? ':' : d < 0.45 ? '.' : ' '; }
void draw(const char* name, const Matrix& m) { std::cout << name << "  (worst |p-1/2| = " << m.worst << ", rms = " << m.rms << ")\n"; for (int i = 0; i < 32; ++i) { std::cout << "  in" << (i < 10 ? "0" : "") << i << " "; for (int j = 0; j < 32; ++j) std::cout << shade(m.p[i][j]); std::cout << "\n"; } }

int main() {
    assert(crc32((const unsigned char*)"123456789", 9) == 0xCBF43926u);          // CRC-32(IEEE) 표준 시험값
    std::mt19937 rng(5); const int S = 20000;
    Matrix mi = measure(hIdentity, S, rng), mm = measure(hMul, S, rng), mf = measure(hFnv, S, rng), mc = measure(hCrc, S, rng), mx = measure(hFmix, S, rng), ml = measure(hLowbias, S, rng);
    draw("identity", mi); draw("multiply (x*2654435769)", mm); draw("fnv1a (4 bytes)", mf); draw("crc32", mc); draw("murmur3 fmix32", mx); draw("lowbias32", ml);
    // 구조적 사실 (전수)
    for (int i = 0; i < 32; ++i) for (int j = 0; j < 32; ++j) {
        assert(mi.p[i][j] == (i == j ? 1.0 : 0.0));                                        // 항등: 대각선만
        if (j < i) assert(mm.p[i][j] == 0.0); if (j == i) assert(mm.p[i][j] == 1.0);        // 곱셈: 삼각형, 대각선은 항상 뒤집힘
        if (j < i % 8) assert(mf.p[i][j] == 0.0);                                          // FNV-1a: 바이트 안의 입력 비트 k 는 출력 비트 < k 에 무영향
        assert(mc.p[i][j] == 0.0 || mc.p[i][j] == 1.0);                                    // CRC: 선형이므로 칸은 정확히 0 또는 1
    }
    assert(mi.ones == 32 && mi.zeros == 992 && mc.middle == 0 && mm.zeros >= 496 && mf.zeros >= 4 * (0 + 1 + 2 + 3 + 4 + 5 + 6 + 7));
    // 좋은 믹서: 모든 1024 칸이 1/2 근처 (20000 표본의 표준오차 0.0035 → 최악 편차도 0.02 미만)
    assert(mx.worst < 0.02 && ml.worst < 0.02 && mx.zeros == 0 && ml.zeros == 0 && mx.middle == 1024);
    assert(mf.rms > mx.rms * 5 && mm.rms > mf.rms && mi.rms > mm.rms);                      // 편향 순위: 항등 > 곱셈 > FNV-1a ≫ fmix32
    std::cout << "avalanche rms bias: identity " << mi.rms << ", mul " << mm.rms << ", fnv1a " << mf.rms << ", crc32 " << mc.rms << ", fmix32 " << mx.rms << ", lowbias32 " << ml.rms << std::endl;
    return 0;
}
// Time Complexity: O(표본 · 32 · 32)
// Space Complexity: O(1) (격자 32×32)
```
## HashQualityEvaluation()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 해시 함수 품질을 한 장의 성적표로 평가한다. 네 가지 시험:
//  ① 균등도: 키 패턴(연속·간격 64·간격 1024·간격 4099·무작위) × 버킷 선택(하위 10 비트 / 상위 10 비트)의 χ² z-점수 (z = (χ²−df)/√(2df), 크면 몰림).
//  ② 희소 키 충돌: 켜진 비트가 3 개 이하인 32 비트 키 5489 개의 출력 상위 16 비트 충돌 수 (이상적으로 ≈ n²/2^17 = 230).
//  ③ 눈사태: 1 비트 반전 시 출력 각 비트의 뒤집힘 확률이 1/2 에서 벗어난 최악의 정도.
//  ④ 아핀성: f(x)⊕f(y)⊕f(z)⊕f(x⊕y⊕z) = 0 이 항상 성립하면 f 는 GF(2) 위의 아핀 함수 (키를 알면 충돌·역산이 선형대수로 풀린다).
typedef std::uint32_t u32;
u32 hIdentity(u32 x) { return x; }
u32 hMul(u32 x) { return x * 2654435769u; }
u32 hFnv(u32 x) { u32 h = 2166136261u; for (int i = 0; i < 4; ++i) { h ^= (x >> (8 * i)) & 0xff; h *= 16777619u; } return h; }
u32 hCrc(u32 x) { static u32 t[256]; static bool init = false; if (!init) { for (int i = 0; i < 256; ++i) { u32 c = (u32)i; for (int k = 0; k < 8; ++k) c = c & 1 ? 0xEDB88320u ^ (c >> 1) : c >> 1; t[i] = c; } init = true; } u32 c = 0xFFFFFFFFu; for (int i = 0; i < 4; ++i) c = t[(c ^ (x >> (8 * i))) & 0xff] ^ (c >> 8); return c ^ 0xFFFFFFFFu; }
u32 hFmix(u32 h) { h ^= h >> 16; h *= 0x85ebca6bu; h ^= h >> 13; h *= 0xc2b2ae35u; h ^= h >> 16; return h; }
u32 hLowbias(u32 x) { x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15; x *= 0x846ca68bu; x ^= x >> 16; return x; }
double zScore(const std::vector<long>& c, long n) { double e = (double)n / c.size(), s = 0; for (long x : c) s += (x - e) * (x - e) / e; int df = (int)c.size() - 1; return (s - df) / std::sqrt(2.0 * df); }
struct Report { double zLow, zTop, sparse, aval, affine; };
Report evaluate(u32 (*f)(u32), std::mt19937& rng) {
    Report r{-1e9, -1e9, 0, 0, 0}; const long n = 40000;
    for (u32 stride : {1u, 64u, 1024u, 4099u, 0u}) {                                  // 0 = 무작위 키
        std::vector<long> lo(1024, 0), top(1024, 0); for (long i = 0; i < n; ++i) { u32 h = f(stride ? (u32)i * stride : (u32)rng()); ++lo[h & 1023]; ++top[h >> 22]; }
        r.zLow = std::max(r.zLow, zScore(lo, n)); r.zTop = std::max(r.zTop, zScore(top, n)); }
    { std::vector<u32> keys; keys.push_back(0); for (int a = 0; a < 32; ++a) { keys.push_back(1u << a); for (int b = a + 1; b < 32; ++b) { keys.push_back((1u << a) | (1u << b)); for (int c = b + 1; c < 32; ++c) keys.push_back((1u << a) | (1u << b) | (1u << c)); } }
      assert(keys.size() == 5489); std::vector<long> cnt(65536, 0); long coll = 0; for (u32 k : keys) coll += cnt[f(k) >> 16]++; r.sparse = (double)coll; }
    { const int S = 5000; static long c[32][32]; for (auto& row : c) for (long& x : row) x = 0; for (int s = 0; s < S; ++s) { u32 x = (u32)rng(), fx = f(x); for (int i = 0; i < 32; ++i) { u32 d = fx ^ f(x ^ (1u << i)); for (int j = 0; j < 32; ++j) c[i][j] += d >> j & 1; } }
      for (int i = 0; i < 32; ++i) for (int j = 0; j < 32; ++j) r.aval = std::max(r.aval, std::abs((double)c[i][j] / S - 0.5)); }
    { long hold = 0; const int T = 20000; for (int t = 0; t < T; ++t) { u32 x = (u32)rng(), y = (u32)rng(), z = (u32)rng(); hold += (f(x) ^ f(y) ^ f(z) ^ f(x ^ y ^ z)) == 0; } r.affine = (double)hold / T; }
    return r;
}

int main() {
    std::mt19937 rng(11); struct Row { const char* name; u32 (*f)(u32); Report r; } rows[] = {{"identity", hIdentity, {}}, {"mul (Knuth)", hMul, {}}, {"fnv1a", hFnv, {}}, {"crc32", hCrc, {}}, {"murmur fmix32", hFmix, {}}, {"lowbias32", hLowbias, {}}};
    std::cout << std::left << std::setw(14) << "hash" << std::right << std::setw(10) << "z(low10)" << std::setw(10) << "z(top10)" << std::setw(10) << "sparse" << std::setw(10) << "aval" << std::setw(10) << "affine" << "   verdict\n";
    for (auto& row : rows) {
        row.r = evaluate(row.f, rng); bool ok = row.r.zLow < 6 && row.r.zTop < 6 && row.r.sparse < 460 && row.r.aval < 0.05 && row.r.affine < 0.01;
        std::cout << std::left << std::setw(14) << row.name << std::right << std::setw(10) << std::setprecision(3) << row.r.zLow << std::setw(10) << row.r.zTop << std::setw(10) << row.r.sparse << std::setw(10) << row.r.aval << std::setw(10) << row.r.affine << "   " << (ok ? "PASS" : "FAIL") << "\n";
    }
    const Report &id = rows[0].r, &mul = rows[1].r, &fnv = rows[2].r, &crc = rows[3].r, &fmix = rows[4].r, &low = rows[5].r;
    assert(id.zLow > 100 && id.zTop > 100 && id.sparse > 5000 && id.aval == 0.5 && id.affine == 1.0);                            // 항등: 몰림·충돌·무눈사태·아핀
    assert(mul.zLow > 100 && mul.zTop < 6 && mul.aval == 0.5 && mul.affine < 0.01);                                              // 곱셈 해시: 하위 비트는 몰리고(간격 1024 → 하위 10 비트 상수), 상위 비트는 균등
    assert(fnv.aval > 0.45 && fnv.affine < 0.01);                                                                                // FNV-1a: 입력 비트 7 이 출력 하위 비트에 닿지 않는다
    assert(crc.zLow < 12 && crc.zTop < 12 && crc.sparse < 460 && crc.aval == 0.5 && crc.affine == 1.0);                // CRC32: 균등·충돌은 대체로 문제없지만(간격 키의 선형 구조가 z≈6 으로 비친다) 선형(아핀)이라 보안·SAC 에는 부적합
    for (const Report* r : {&fmix, &low}) assert(r->zLow < 6 && r->zTop < 6 && r->sparse < 460 && r->aval < 0.05 && r->affine < 0.01);
    return 0;
}
// Time Complexity: O(패턴 수 · n + 표본 · 32 · 32)
// Space Complexity: O(2^16)
```
## CacheLocality()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 캐시 지역성 모형: 캐시 라인(64B) 하나를 읽을 때마다 비용이 든다고 보고, 성공 조회 1회가 건드리는 "서로 다른 캐시 라인 수"를 센다.
//  - 체이닝: 버킷 헤드 1회 + 체인의 노드마다 힙의 서로 다른 위치 -> 노드 수만큼 라인
//  - 개방 주소법(선형 탐사): 슬롯이 배열에 연속 -> 16바이트 슬롯 4개가 한 라인을 공유
// (실제 시간은 기계마다 다르므로 결정적인 모형으로 비교한다)
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }

int main() {
    const int m = 4096; const double alpha = 0.7; const int n = (int)(alpha * m);
    std::mt19937_64 rng(5);
    std::vector<uint64_t> keys(n); for (auto& k : keys) k = rng();

    // 체이닝: 각 노드는 별개의 힙 할당이므로 서로 다른 라인으로 취급
    std::vector<std::vector<uint64_t>> chain(m);
    for (auto k : keys) chain[mix(k) % m].push_back(k);
    double chainLines = 0;
    for (auto k : keys) {
        auto& c = chain[mix(k) % m];
        size_t pos = 0; while (c[pos] != k) pos++;
        chainLines += 1 + (pos + 1);                              // 버킷 헤드 + 방문한 노드들
    }

    // 개방 주소법: 슬롯 16B, 라인당 4슬롯
    std::vector<uint64_t> slot(m, 0);
    for (auto k : keys) { size_t p = mix(k) % m; while (slot[p]) p = (p + 1) % m; slot[p] = k; }
    double openLines = 0;
    for (auto k : keys) {
        std::set<size_t> lines; size_t p = mix(k) % m;
        for (;;) { lines.insert(p / 4); if (slot[p] == k) break; p = (p + 1) % m; }
        openLines += lines.size();
    }
    chainLines /= n; openLines /= n;
    std::cout << "cache lines per successful lookup (alpha=" << alpha << "): chaining=" << chainLines << " open addressing=" << openLines << std::endl;
    assert(openLines < chainLines);
    return 0;
}
// Time Complexity: O(n · 평균 탐사)
// Space Complexity: O(m)
```
## MemoryLayout()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 해시 테이블 구조별 메모리 배치: 체이닝 노드, 개방 주소 슬롯, 패딩이 낭비되는 순서, SwissTable 그룹
// 컴파일러가 구조체를 배치하는 규칙(각 멤버를 자기 정렬 배수 위치에, 전체 크기는 최대 정렬의 배수로)을 함수로 옮겨 실제 sizeof/offsetof 와 맞춰 보고,
// 멤버를 정렬이 큰 것부터 두면 패딩이 최소라는 것을 모든 순열로 확인한다. 이어 슬롯 크기·배열 구조(AoS/SoA)에 따라 한 번의 조회가 건드리는 캐시 라인 수를 시뮬레이션하고,
// 구조별 원소당 바이트 수(모형)를 비교한다
// 검증: ① 손으로 짠 구조체의 sizeof/alignof/offsetof (LP64 이면 기대값까지)  ② 배치 계산 함수가 실제 구조체 8 종의 크기·오프셋과 일치  ③ 멤버 7 개 이하의 무작위 크기·정렬 2 000 세트에서 *모든 순열* 중 최소 크기 = 정렬 내림차순 배치의 크기
//        ④ 적재율 0.7 의 선형 탐사에서 슬롯 8·16·32 바이트일 때 조회당 캐시 라인 수가 슬롯이 클수록 늘고, 키와 값을 따로 둔 배열(SoA)은 실패 조회에서 값 배열을 건드리지 않아 더 적은 라인  ⑤ 원소당 바이트: 스위스 < 개방 주소 < compact dict < 체이닝(노드 + 버킷 + 할당기 머리말)
struct ChainNode { int32_t key; int32_t val; ChainNode* next; };  // 8 + 포인터 8 = 16B (+ 할당기 헤더는 별도)
struct OpenSlot  { int32_t key; int32_t val; };                    // 8B: 라인당 8개
struct BadOrder  { char flag; int64_t value; char tag; };          // 정렬 때문에 패딩이 끼어 24B
struct GoodOrder { int64_t value; char flag; char tag; };          // 큰 멤버부터 두면 16B
struct SwissGroup { uint8_t ctrl[16]; int32_t keys[16]; int32_t vals[16]; };   // 제어 바이트 16B + 키·값
struct Mixed1 { char a; int32_t b; char c; int16_t d; double e; };
struct Mixed2 { double e; int32_t b; int16_t d; char a; char c; };
struct Tiny { char a; char b; char c; };
struct Wide { char a; __attribute__((aligned(16))) char b; int32_t c; };     // 정렬이 16 인 멤버

void dump(const char* name, size_t size, size_t align) { std::cout << name << ": size=" << size << " align=" << align << "\n"; }
struct Member { size_t size, align; };
struct LayoutResult { size_t size, align; std::vector<size_t> offsets; size_t padding; };
LayoutResult layout(const std::vector<Member>& ms) {               // 규칙: offset 을 멤버 정렬로 올림, 마지막에 전체 크기를 최대 정렬로 올림
    size_t off = 0, maxAlign = 1, payload = 0; LayoutResult r;
    for (const Member& m : ms) { off = (off + m.align - 1) / m.align * m.align; r.offsets.push_back(off); off += m.size; maxAlign = std::max(maxAlign, m.align); payload += m.size; }
    r.size = (off + maxAlign - 1) / maxAlign * maxAlign; r.align = maxAlign; r.padding = r.size - payload; return r;
}

int main() {
    dump("ChainNode", sizeof(ChainNode), alignof(ChainNode));
    dump("OpenSlot", sizeof(OpenSlot), alignof(OpenSlot));
    dump("BadOrder", sizeof(BadOrder), alignof(BadOrder));
    dump("GoodOrder", sizeof(GoodOrder), alignof(GoodOrder));
    dump("SwissGroup", sizeof(SwissGroup), alignof(SwissGroup));
    assert(sizeof(OpenSlot) == 8 && 64 / sizeof(OpenSlot) == 8);                // 캐시 라인 하나에 슬롯 8개
    assert(sizeof(GoodOrder) < sizeof(BadOrder));                               // 멤버 순서만 바꿔도 메모리가 줄어든다
    assert(offsetof(SwissGroup, keys) == 16);                                   // 제어 바이트가 맨 앞 16B 에 모여 한 번에 검사 가능
    if (sizeof(void*) == 8) {
        assert(sizeof(ChainNode) == 16 && offsetof(ChainNode, next) == 8);
        assert(sizeof(BadOrder) == 24 && sizeof(GoodOrder) == 16);
    }
    assert(sizeof(SwissGroup) == 144 && alignof(SwissGroup) == 4);
    // ② 배치 계산 함수 대 실제 컴파일러
    {   LayoutResult a = layout({{1, 1}, {8, 8}, {1, 1}}); assert(a.size == sizeof(BadOrder) && a.offsets[1] == offsetof(BadOrder, value) && a.offsets[2] == offsetof(BadOrder, tag) && a.padding == 14);
        LayoutResult b = layout({{8, 8}, {1, 1}, {1, 1}}); assert(b.size == sizeof(GoodOrder) && b.offsets[1] == offsetof(GoodOrder, flag) && b.padding == 6);
        LayoutResult c = layout({{4, 4}, {4, 4}, {8, 8}}); assert(c.size == sizeof(ChainNode) && c.offsets[2] == offsetof(ChainNode, next));          // LP64 가정(포인터 8)
        LayoutResult d = layout({{4, 4}, {4, 4}}); assert(d.size == sizeof(OpenSlot) && d.padding == 0);
        LayoutResult e = layout({{1, 1}, {4, 4}, {1, 1}, {2, 2}, {8, 8}}); assert(e.size == sizeof(Mixed1) && e.offsets[1] == offsetof(Mixed1, b) && e.offsets[3] == offsetof(Mixed1, d) && e.offsets[4] == offsetof(Mixed1, e));
        LayoutResult f = layout({{8, 8}, {4, 4}, {2, 2}, {1, 1}, {1, 1}}); assert(f.size == sizeof(Mixed2) && f.padding == 0 && sizeof(Mixed1) > sizeof(Mixed2));        // 같은 멤버, 순서만 다르다
        LayoutResult g = layout({{1, 1}, {1, 1}, {1, 1}}); assert(g.size == sizeof(Tiny) && g.align == 1);
        LayoutResult h = layout({{1, 1}, {1, 16}, {4, 4}}); assert(h.size == sizeof(Wide) && h.offsets[1] == offsetof(Wide, b) && h.align == alignof(Wide)); }
    // ③ 정렬 내림차순이 패딩 최소 (모든 순열로 확인)
    std::mt19937 rng(9); const size_t kinds[5] = {1, 2, 4, 8, 16}; long sets = 0, strictlyBetter = 0;
    for (int it = 0; it < 2000; ++it) {
        int n = 2 + (int)(rng() % 6); std::vector<Member> ms; for (int i = 0; i < n; i++) { size_t sz = kinds[rng() % 5]; ms.push_back({sz, sz}); if (rng() % 4 == 0) ms.back().size = sz * (1 + rng() % 3); }                         // 배열 멤버처럼 크기가 정렬의 배수가 되도록
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); size_t best = SIZE_MAX, original = layout(ms).size;
        do { std::vector<Member> v; for (int i : perm) v.push_back(ms[i]); best = std::min(best, layout(v).size); } while (std::next_permutation(perm.begin(), perm.end()));
        std::vector<Member> sorted = ms; std::stable_sort(sorted.begin(), sorted.end(), [](const Member& a, const Member& b) { return a.align > b.align; });
        assert(layout(sorted).size == best); ++sets; strictlyBetter += best < original;
    }
    assert(sets == 2000 && strictlyBetter > 400);
    // ④ 캐시 라인: 슬롯 크기별로 선형 탐사 한 번이 건드리는 라인 수 (적재율 0.7, 실패 조회)
    {   const size_t cap = 1 << 14; const double load = 0.7; std::vector<bool> used(cap, false); size_t placed = 0;
        while (placed < (size_t)(load * cap)) { size_t h = rng() % cap; while (used[h]) h = (h + 1) % cap; used[h] = true; ++placed; }
        auto linesPerFailedLookup = [&](size_t slotBytes, size_t keyBytes, bool soa) {            // soa 이면 키 배열(keyBytes 씩)만 읽는다
            double lines = 0; const int Q = 20000;
            for (int q = 0; q < Q; q++) { size_t h = rng() % cap; std::set<size_t> touched; size_t stride = soa ? keyBytes : slotBytes; for (size_t i = h;; i = (i + 1) % cap) { touched.insert(i * stride / 64); if (!used[i]) break; } lines += (double)touched.size(); }
            return lines / Q; };
        double l8 = linesPerFailedLookup(8, 4, false), l16 = linesPerFailedLookup(16, 8, false), l32 = linesPerFailedLookup(32, 8, false);
        double aos16 = linesPerFailedLookup(16, 8, false), soa16 = linesPerFailedLookup(16, 8, true);
        assert(l8 < l16 && l16 < l32 && soa16 < aos16); }
    // ⑤ 원소당 바이트 (키 4B + 값 4B 의 8B 페이로드, 모형)
    {   const double alloc = 16;                                             // glibc malloc 의 청크 머리말·정렬 낭비를 노드당 약 16B 로 어림
        double chain = (double)sizeof(ChainNode) + alloc + 8.0 / 1.0;       // 노드 + 할당기 + 버킷 포인터(적재율 1.0 이면 원소당 하나)
        double open = (double)sizeof(OpenSlot) / 0.7;                       // 적재율 0.7
        double swiss = (8.0 + 1.0) / (7.0 / 8.0);                           // 슬롯 8B + 제어 1B, 적재율 7/8
        double compact = 4.0 / (2.0 / 3.0) + 8.0;                           // 색인 4B 는 모든 칸에 있어 사용률 2/3 로 나누면 원소당 6B, 항목 8B 는 원소마다
        std::cout << "bytes per 8-byte entry: chaining " << chain << ", open " << open << ", swiss " << swiss << ", compact " << compact << std::endl;
        assert(swiss < open && open < compact && compact < chain && chain > 3 * open); }                // 원소당 바이트: 스위스 < 개방 주소 < compact dict < 체이닝
    std::cout << "padding wasted by BadOrder: " << sizeof(BadOrder) - sizeof(GoodOrder) << " bytes per object; " << strictlyBetter << " of 2000 random structs shrink when members are sorted by alignment" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
