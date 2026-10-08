# Part 1. 해시의 기초
## CreateHashTable()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <string>
#include <vector>
#include <cassert>

class HashTable {
    std::vector<std::list<std::pair<std::string, int>>> buckets;
    size_t count = 0;
public:
    explicit HashTable(size_t bucketCount = 8) : buckets(bucketCount) {}
    size_t bucketCount() const { return buckets.size(); }
    size_t size() const { return count; }
    bool empty() const { return count == 0; }
};

int main() {
    HashTable table(8);                 // 빈 버킷 8개로 시작한다
    assert(table.bucketCount() == 8);
    assert(table.empty());
    std::cout << "CreateHashTable: " << table.bucketCount() << " buckets, size " << table.size() << std::endl;
    return 0;
}
// Time Complexity: O(m)  (버킷 m개 초기화)
// Space Complexity: O(m)
```
## Insert()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <string>
#include <vector>
#include <cassert>

class HashTable {
    std::vector<std::list<std::pair<std::string, int>>> b;
    size_t n = 0;
    size_t idx(const std::string& k) const { return std::hash<std::string>{}(k) % b.size(); }
public:
    explicit HashTable(size_t m = 8) : b(m) {}
    // 새 키면 true, 기존 키의 값을 갱신하면 false
    bool insert(const std::string& k, int v) {
        for (auto& kv : b[idx(k)]) if (kv.first == k) { kv.second = v; return false; }
        b[idx(k)].emplace_back(k, v);
        ++n;
        return true;
    }
    size_t size() const { return n; }
    int get(const std::string& k) const {
        for (auto& kv : b[idx(k)]) if (kv.first == k) return kv.second;
        return -1;
    }
};

int main() {
    HashTable t;
    assert(t.insert("apple", 1));
    assert(t.insert("banana", 2));
    assert(!t.insert("apple", 10));     // 같은 키는 갱신: 크기는 그대로
    assert(t.size() == 2 && t.get("apple") == 10);
    std::cout << "Insert: size=" << t.size() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1 + α), 최악 O(n)
// Space Complexity: O(n)
```
## Search()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <string>
#include <vector>
#include <cassert>

class HashTable {
    std::vector<std::list<std::pair<std::string, int>>> b;
    size_t idx(const std::string& k) const { return std::hash<std::string>{}(k) % b.size(); }
public:
    explicit HashTable(size_t m = 8) : b(m) {}
    void insert(const std::string& k, int v) { b[idx(k)].emplace_back(k, v); }
    // 찾으면 값의 주소, 없으면 nullptr
    const int* search(const std::string& k) const {
        for (auto& kv : b[idx(k)]) if (kv.first == k) return &kv.second;
        return nullptr;
    }
};

int main() {
    HashTable t;
    t.insert("one", 1); t.insert("two", 2); t.insert("three", 3);
    assert(t.search("two") && *t.search("two") == 2);
    assert(t.search("four") == nullptr);
    std::cout << "Search: two -> " << *t.search("two") << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1 + α), 최악 O(n)
// Space Complexity: O(1)
```
## Delete()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <string>
#include <vector>
#include <cassert>

class HashTable {
    std::vector<std::list<std::pair<std::string, int>>> b;
    size_t n = 0;
    size_t idx(const std::string& k) const { return std::hash<std::string>{}(k) % b.size(); }
public:
    explicit HashTable(size_t m = 8) : b(m) {}
    void insert(const std::string& k, int v) { b[idx(k)].emplace_back(k, v); ++n; }
    bool contains(const std::string& k) const {
        for (auto& kv : b[idx(k)]) if (kv.first == k) return true;
        return false;
    }
    // 체이닝에서는 해당 노드만 리스트에서 떼어내면 된다
    bool erase(const std::string& k) {
        auto& chain = b[idx(k)];
        for (auto it = chain.begin(); it != chain.end(); ++it)
            if (it->first == k) { chain.erase(it); --n; return true; }
        return false;
    }
    size_t size() const { return n; }
};

int main() {
    HashTable t;
    t.insert("a", 1); t.insert("b", 2); t.insert("c", 3);
    assert(t.erase("b"));
    assert(!t.contains("b") && t.contains("a") && t.contains("c"));
    assert(!t.erase("zzz"));
    assert(t.size() == 2);
    std::cout << "Delete: size=" << t.size() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1 + α), 최악 O(n)
// Space Complexity: O(1)
```
## Resize()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <string>
#include <vector>
#include <cassert>

class HashTable {
    std::vector<std::list<std::pair<std::string, int>>> b;
    size_t n = 0;
    size_t idx(const std::string& k) const { return std::hash<std::string>{}(k) % b.size(); }
    void grow() {                         // 버킷 수를 2배로 늘리고 모든 노드를 재배치
        std::vector<std::list<std::pair<std::string, int>>> nb(b.size() * 2);
        for (auto& chain : b)
            for (auto& kv : chain) nb[std::hash<std::string>{}(kv.first) % nb.size()].push_back(kv);
        b.swap(nb);
    }
public:
    explicit HashTable(size_t m = 4) : b(m) {}
    void insert(const std::string& k, int v) {
        if (double(n + 1) / b.size() > 0.75) grow();   // 적재율이 0.75를 넘으면 확장
        b[idx(k)].emplace_back(k, v);
        ++n;
    }
    size_t buckets() const { return b.size(); }
    bool contains(const std::string& k) const {
        for (auto& kv : b[idx(k)]) if (kv.first == k) return true;
        return false;
    }
};

int main() {
    HashTable t(4);
    for (int i = 0; i < 100; i++) t.insert("key" + std::to_string(i), i);
    assert(t.buckets() == 256);            // 4 -> 8 -> ... -> 256 (적재율 <= 0.75 유지)
    for (int i = 0; i < 100; i++) assert(t.contains("key" + std::to_string(i)));
    std::cout << "Resize: buckets=" << t.buckets() << std::endl;
    return 0;
}
// Time Complexity: 삽입 분할상환 O(1), 확장 1회는 O(n)
// Space Complexity: O(n)
```
## Rehash()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <string>
#include <vector>
#include <cassert>

// 해시 함수(시드)를 바꾸면 모든 키의 위치가 달라지므로 전부 다시 계산해야 한다
class HashTable {
    std::vector<std::list<std::pair<std::string, int>>> b;
    unsigned seed;
    size_t h(const std::string& k) const {
        unsigned x = 2166136261u ^ seed;               // FNV-1a에 시드를 섞은 해시
        for (unsigned char c : k) { x ^= c; x *= 16777619u; }
        return x % b.size();
    }
public:
    HashTable(size_t m, unsigned s) : b(m), seed(s) {}
    void insert(const std::string& k, int v) { b[h(k)].emplace_back(k, v); }
    void rehash(size_t newBuckets, unsigned newSeed) {
        std::vector<std::pair<std::string, int>> all;
        for (auto& chain : b) for (auto& kv : chain) all.push_back(kv);
        b.assign(newBuckets, {});
        seed = newSeed;
        for (auto& kv : all) b[h(kv.first)].push_back(kv);
    }
    size_t maxChain() const { size_t m = 0; for (auto& c : b) m = std::max(m, c.size()); return m; }
    bool contains(const std::string& k) const {
        for (auto& kv : b[h(k)]) if (kv.first == k) return true;
        return false;
    }
};

int main() {
    HashTable t(4, 1);
    for (int i = 0; i < 40; i++) t.insert("k" + std::to_string(i), i);
    size_t before = t.maxChain();
    t.rehash(64, 99);                                  // 버킷 수와 해시 함수를 동시에 교체
    for (int i = 0; i < 40; i++) assert(t.contains("k" + std::to_string(i)));
    assert(t.maxChain() <= before);
    std::cout << "Rehash: maxChain " << before << " -> " << t.maxChain() << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
## LoadFactor()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cassert>

// 적재율 α = n / m 에 따른 평균 탐색 횟수(이론값)
double chainingHit(double a)  { return 1 + a / 2; }                 // 체이닝, 성공 탐색
double chainingMiss(double a) { return 1 + a; }                     // 체이닝, 실패 탐색
double linearHit(double a)    { return 0.5 * (1 + 1 / (1 - a)); }   // 선형 탐사, 성공 탐색
double linearMiss(double a)   { return 0.5 * (1 + 1 / ((1 - a) * (1 - a))); }  // 선형 탐사, 실패 탐색

int main() {
    // α가 커질수록 개방 주소법의 비용은 급격히 커지고, 체이닝은 완만하게 커진다
    assert(std::fabs(linearMiss(0.5) - 2.5) < 1e-9);
    assert(std::fabs(linearMiss(0.9) - 50.5) < 1e-9);
    assert(chainingMiss(0.9) < 2);
    assert(linearMiss(0.9) > 20 * chainingMiss(0.9));
    for (double a : {0.25, 0.5, 0.75, 0.9})
        std::cout << "alpha=" << a << " chain(hit/miss)=" << chainingHit(a) << "/" << chainingMiss(a)
                  << " linear(hit/miss)=" << linearHit(a) << "/" << linearMiss(a) << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
# Part 2. 해시 함수
## DivisionMethod()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// h(k) = k mod m : m 선택이 분포를 좌우한다
size_t spread(unsigned m, const std::vector<unsigned>& keys) {
    std::set<unsigned> used;
    for (unsigned k : keys) used.insert(k % m);
    return used.size();
}

int main() {
    std::vector<unsigned> keys;
    for (unsigned i = 0; i < 64; i++) keys.push_back(i * 16);   // 16의 배수들
    assert(spread(16, keys) == 1);        // m이 2의 거듭제곱이면 하위 비트만 쓰여 전부 한 버킷
    assert(spread(17, keys) == 17);       // m이 소수이면 모든 버킷이 고르게 쓰인다
    std::cout << "m=16 buckets used: " << spread(16, keys) << ", m=17 buckets used: " << spread(17, keys) << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MultiplicationMethod()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <set>
#include <cassert>

// h(k) = floor(m * frac(k * A)),  A = (sqrt(5) - 1) / 2   (Knuth)
// m = 2^p 이면 32비트 정수 곱셈과 시프트만으로 계산된다: (k * 2654435769) >> (32 - p)
uint32_t mulHash(uint32_t k, int p) { return (uint32_t)(k * 2654435769u) >> (32 - p); }

int main() {
    const int p = 4;                       // 버킷 16개
    std::set<uint32_t> used;
    for (uint32_t i = 0; i < 64; i++) {
        uint32_t h = mulHash(i * 16, p);   // 16의 배수도 나눗셈법과 달리 잘 퍼진다
        assert(h < (1u << p));
        used.insert(h);
    }
    assert(used.size() >= 12);
    std::cout << "MultiplicationMethod: used " << used.size() << "/16 buckets" << std::endl;
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
#include <iostream>
#include <cstdint>
#include <string>
#include <cassert>

// FNV-1a: XOR 한 뒤 곱한다 (FNV-1은 곱한 뒤 XOR)
uint32_t fnv1a32(const std::string& s) {
    uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    return h;
}
uint64_t fnv1a64(const std::string& s) {
    uint64_t h = 14695981039346656037ULL;
    for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; }
    return h;
}

int main() {
    assert(fnv1a32("") == 0x811c9dc5u);
    assert(fnv1a32("a") == 0xe40c292cu);
    assert(fnv1a32("foobar") == 0xbf9cf968u);
    assert(fnv1a64("a") == 0xaf63dc4c8601ec8cULL);
    assert(fnv1a64("foobar") == 0x85944171f73967e8ULL);
    std::cout << std::hex << "fnv1a32(foobar)=" << fnv1a32("foobar") << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)
```
## MurmurHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <string>
#include <cassert>

// MurmurHash3 (x86, 32bit)
static inline uint32_t rotl32(uint32_t x, int r) { return (x << r) | (x >> (32 - r)); }
uint32_t murmur3_32(const uint8_t* data, size_t len, uint32_t seed) {
    const uint32_t c1 = 0xcc9e2d51, c2 = 0x1b873593;
    uint32_t h = seed;
    size_t nblocks = len / 4;
    for (size_t i = 0; i < nblocks; i++) {
        uint32_t k; std::memcpy(&k, data + i * 4, 4);
        k *= c1; k = rotl32(k, 15); k *= c2;
        h ^= k; h = rotl32(h, 13); h = h * 5 + 0xe6546b64;
    }
    const uint8_t* tail = data + nblocks * 4;
    uint32_t k1 = 0;
    switch (len & 3) {
        case 3: k1 ^= tail[2] << 16; [[fallthrough]];
        case 2: k1 ^= tail[1] << 8;  [[fallthrough]];
        case 1: k1 ^= tail[0]; k1 *= c1; k1 = rotl32(k1, 15); k1 *= c2; h ^= k1;
    }
    h ^= (uint32_t)len;
    h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16;   // fmix32
    return h;
}
uint32_t murmur(const std::string& s, uint32_t seed = 0) { return murmur3_32((const uint8_t*)s.data(), s.size(), seed); }

int main() {
    assert(murmur("", 0) == 0u);
    assert(murmur("", 1) == 0x514E28B7u);
    assert(murmur("hello", 0) == 0x248bfa47u);
    assert(murmur("test", 0) == 0xba6bd213u);
    std::cout << std::hex << "murmur3(hello)=" << murmur("hello") << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)
```
## xxHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <string>
#include <cassert>

// xxHash32
static const uint32_t P1 = 2654435761u, P2 = 2246822519u, P3 = 3266489917u, P4 = 668265263u, P5 = 374761393u;
static inline uint32_t rotl(uint32_t x, int r) { return (x << r) | (x >> (32 - r)); }
static inline uint32_t rd32(const uint8_t* p) { uint32_t v; std::memcpy(&v, p, 4); return v; }
static inline uint32_t round1(uint32_t acc, uint32_t in) { return rotl(acc + in * P2, 13) * P1; }

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
    while (p + 4 <= end) { h += rd32(p) * P3; h = rotl(h, 17) * P4; p += 4; }
    while (p < end) { h += (*p++) * P5; h = rotl(h, 11) * P1; }
    h ^= h >> 15; h *= P2; h ^= h >> 13; h *= P3; h ^= h >> 16;
    return h;
}
uint32_t xxh(const std::string& s, uint32_t seed = 0) { return xxh32((const uint8_t*)s.data(), s.size(), seed); }

int main() {
    assert(xxh("", 0) == 0x02CC5D05u);
    assert(xxh("a", 0) == 0x550D7456u);
    assert(xxh("abc", 0) == 0x32D153FFu);
    std::cout << std::hex << "xxh32(abc)=" << xxh("abc") << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(1)
```
## SipHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <cassert>

// SipHash-2-4: 키 있는 해시. 해시 플러딩(HashDoS) 방어용으로 Python, Rust, Ruby 등이 사용한다
static inline uint64_t rotl(uint64_t x, int b) { return (x << b) | (x >> (64 - b)); }
#define SIPROUND do { \
    v0 += v1; v1 = rotl(v1, 13); v1 ^= v0; v0 = rotl(v0, 32); \
    v2 += v3; v3 = rotl(v3, 16); v3 ^= v2; \
    v0 += v3; v3 = rotl(v3, 21); v3 ^= v0; \
    v2 += v1; v1 = rotl(v1, 17); v1 ^= v2; v2 = rotl(v2, 32); } while (0)

uint64_t siphash24(const uint8_t* in, size_t len, uint64_t k0, uint64_t k1) {
    uint64_t v0 = k0 ^ 0x736f6d6570736575ULL, v1 = k1 ^ 0x646f72616e646f6dULL;
    uint64_t v2 = k0 ^ 0x6c7967656e657261ULL, v3 = k1 ^ 0x7465646279746573ULL;
    const uint8_t* end = in + (len - len % 8);
    for (; in != end; in += 8) {
        uint64_t m; std::memcpy(&m, in, 8);
        v3 ^= m; SIPROUND; SIPROUND; v0 ^= m;
    }
    uint64_t b = (uint64_t)len << 56;
    for (size_t i = 0; i < len % 8; i++) b |= (uint64_t)in[i] << (8 * i);
    v3 ^= b; SIPROUND; SIPROUND; v0 ^= b;
    v2 ^= 0xff; SIPROUND; SIPROUND; SIPROUND; SIPROUND;
    return v0 ^ v1 ^ v2 ^ v3;
}

int main() {
    uint8_t msg[16];
    for (int i = 0; i < 16; i++) msg[i] = (uint8_t)i;
    const uint64_t k0 = 0x0706050403020100ULL, k1 = 0x0f0e0d0c0b0a0908ULL;   // 키 = 00 01 .. 0f
    assert(siphash24(msg, 0, k0, k1) == 0x726fdb47dd0e0e31ULL);               // 공식 테스트 벡터
    assert(siphash24(msg, 15, k0, k1) == 0xa129ca6149be45e5ULL);
    assert(siphash24(msg, 15, k0 + 1, k1) != siphash24(msg, 15, k0, k1));      // 키가 다르면 결과가 다르다
    std::cout << std::hex << "siphash24(15 bytes)=" << siphash24(msg, 15, k0, k1) << std::endl;
    return 0;
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
#include <iostream>
#include <vector>
#include <cassert>

// 개방 주소법: 모든 원소를 테이블 안에 저장하고 충돌하면 다음 후보 칸을 탐사한다.
// 삭제는 비우지 않고 묘비(DELETED)를 남겨야 뒤쪽 키의 탐사 경로가 끊기지 않는다.
class OpenTable {
    enum State { EMPTY, FULL, DELETED };
    struct Slot { int key = 0; State st = EMPTY; };
    std::vector<Slot> t;
    size_t home(int k) const { return (size_t)k % t.size(); }
public:
    explicit OpenTable(size_t m) : t(m) {}
    bool insert(int k) {
        long firstFree = -1;
        for (size_t i = 0; i < t.size(); i++) {
            size_t j = (home(k) + i) % t.size();             // 선형 탐사
            if (t[j].st == FULL && t[j].key == k) return false;
            if (t[j].st != FULL && firstFree < 0) firstFree = j;   // 묘비 자리는 재사용
            if (t[j].st == EMPTY) break;
        }
        if (firstFree < 0) return false;
        t[firstFree] = {k, FULL};
        return true;
    }
    bool find(int k) const {
        for (size_t i = 0; i < t.size(); i++) {
            size_t j = (home(k) + i) % t.size();
            if (t[j].st == EMPTY) return false;               // 진짜 빈 칸을 만나야 종료
            if (t[j].st == FULL && t[j].key == k) return true;
        }
        return false;
    }
    bool erase(int k) {
        for (size_t i = 0; i < t.size(); i++) {
            size_t j = (home(k) + i) % t.size();
            if (t[j].st == EMPTY) return false;
            if (t[j].st == FULL && t[j].key == k) { t[j].st = DELETED; return true; }
        }
        return false;
    }
};

int main() {
    OpenTable t(8);
    t.insert(1); t.insert(9); t.insert(17);                    // 모두 홈 버킷이 1
    assert(t.erase(9));                                        // 가운데 키 삭제 -> 묘비
    assert(t.find(17));                                        // 묘비를 지나서 17을 찾아야 한다
    assert(!t.find(9));
    assert(t.insert(25) && t.find(25));                        // 묘비 자리 재사용
    std::cout << "OpenAddressing verified." << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1/(1-α)), 최악 O(m)
// Space Complexity: O(m)
```
## LinearProbing()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

// 선형 탐사: h(k, i) = (h(k) + i) mod m.  연속된 점유 구간(클러스터)이 스스로 커지는 1차 군집이 생긴다
int longestCluster(const std::vector<bool>& used) {
    int best = 0, cur = 0;
    for (size_t i = 0; i < 2 * used.size(); i++) {         // 원형이므로 두 바퀴를 본다
        cur = used[i % used.size()] ? cur + 1 : 0;
        best = std::max(best, std::min<int>(cur, used.size()));
    }
    return best;
}

int main() {
    const int m = 32;
    std::vector<bool> spread(m, false), clump(m, false);
    // 흩어진 키: 홈 버킷이 4칸 간격
    for (int i = 0; i < 8; i++) spread[(i * 4) % m] = true;
    // 같은 홈 버킷(5)에 몰린 키 8개: 5, 6, 7, ... 로 이어 붙는다
    for (int i = 0; i < 8; i++) { int j = 5; while (clump[j % m]) j++; clump[j % m] = true; }
    assert(longestCluster(spread) == 1);
    assert(longestCluster(clump) == 8);                    // 8개가 하나의 긴 클러스터가 된다
    std::cout << "cluster length: spread=" << longestCluster(spread) << " clump=" << longestCluster(clump) << std::endl;
    return 0;
}
// Time Complexity: 성공 탐색 ≈ ½(1 + 1/(1-α)), 실패 탐색 ≈ ½(1 + 1/(1-α)²)
// Space Complexity: O(m)
```
## QuadraticProbing()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

// 이차 탐사: h(k, i) = (h(k) + i(i+1)/2) mod m.  m이 2의 거듭제곱이면 처음 m번의 탐사가 모든 칸을 정확히 한 번씩 방문한다
int main() {
    const unsigned m = 16;
    for (unsigned home = 0; home < m; home++) {
        std::set<unsigned> seen;
        for (unsigned i = 0; i < m; i++) seen.insert((home + i * (i + 1) / 2) % m);
        assert(seen.size() == m);                          // 순열 -> 빈 칸이 있으면 반드시 찾는다
    }
    // 비교: c1=c2=1 이 아닌 i^2 만 쓰면 일부 칸을 놓친다
    std::set<unsigned> sq;
    for (unsigned i = 0; i < m; i++) sq.insert((i * i) % m);
    assert(sq.size() < m);
    std::cout << "triangular probes cover all " << m << " slots; i^2 covers only " << sq.size() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1/(1-α)), 군집은 선형 탐사보다 완화
// Space Complexity: O(m)
```
## DoubleHashing()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

// 이중 해싱: h(k, i) = (h1(k) + i * h2(k)) mod m.
// m이 소수이고 h2(k) in [1, m-1] 이면 gcd(h2, m) = 1 이라 탐사열이 모든 칸을 지난다
int main() {
    const unsigned m = 13;
    auto h1 = [&](unsigned k) { return k % m; };
    auto h2 = [&](unsigned k) { return 1 + k % (m - 1); };
    for (unsigned k = 0; k < 200; k++) {
        std::set<unsigned> seen;
        for (unsigned i = 0; i < m; i++) seen.insert((h1(k) + i * h2(k)) % m);
        assert(seen.size() == m);
    }
    // 같은 홈 버킷이어도 간격이 달라 탐사열이 갈라진다 (군집 억제)
    unsigned a = 1, b = 14;                                 // h1이 같다
    assert(h1(a) == h1(b) && h2(a) != h2(b));
    assert((h1(a) + h2(a)) % m != (h1(b) + h2(b)) % m);
    std::cout << "double hashing probe sequences are permutations of Z_" << m << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1/(1-α)) (1차·2차 군집 없음)
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
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 홉스카치 해싱: 모든 키가 홈 버킷에서 H칸 이내(이웃 영역)에 있도록 유지한다.
// 홈 버킷마다 H비트 비트맵을 두어 이웃 영역 안의 점유 위치만 확인하면 되므로 탐색이 캐시 친화적이다.
class Hopscotch {
    static const int H = 8;
    std::vector<int64_t> key;
    std::vector<uint8_t> used;
    std::vector<uint32_t> hop;                                   // hop[b]의 비트 d = (b+d)번 칸이 b가 홈인 원소를 담음
    size_t m;
    size_t home(int64_t k) const { return (((uint64_t)k * 11400714819323198485ULL) >> 40) % m; }
    size_t dist(size_t from, size_t to) const { return (to + m - from) % m; }
public:
    explicit Hopscotch(size_t size) : key(size), used(size, 0), hop(size, 0), m(size) {}
    bool contains(int64_t k) const {
        size_t b = home(k);
        for (int d = 0; d < H; d++) if ((hop[b] >> d & 1) && key[(b + d) % m] == k) return true;
        return false;
    }
    bool insert(int64_t k) {
        if (contains(k)) return true;
        size_t b = home(k), j = b;
        size_t steps = 0;
        while (used[j] && steps < m) { j = (j + 1) % m; steps++; }          // 가장 가까운 빈 칸
        if (used[j]) return false;
        while (dist(b, j) >= H) {                                           // 너무 멀면 이웃 안으로 끌어온다
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
        key[j] = k; used[j] = 1;
        hop[b] |= (1u << dist(b, j));
        return true;
    }
    bool erase(int64_t k) {
        size_t b = home(k);
        for (int d = 0; d < H; d++)
            if ((hop[b] >> d & 1) && key[(b + d) % m] == k) { used[(b + d) % m] = 0; hop[b] &= ~(1u << d); return true; }
        return false;
    }
};

int main() {
    Hopscotch t(128);
    int inserted = 0;
    for (int64_t k = 1; k <= 90; k++) if (t.insert(k * 1000003)) inserted++;     // 적재율 약 0.7
    assert(inserted >= 85);
    int found = 0;
    for (int64_t k = 1; k <= 90; k++) if (t.contains(k * 1000003)) found++;
    assert(found == inserted);
    assert(t.erase(1000003) && !t.contains(1000003));
    std::cout << "Hopscotch inserted " << inserted << "/90, all found" << std::endl;
    return 0;
}
// Time Complexity: 탐색 O(H), 삽입 평균 O(1)
// Space Complexity: O(m)
```
## CoalescedHashing()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 병합 해싱: 개방 주소법처럼 테이블 안에 저장하되 충돌 원소를 next 인덱스로 연결한다.
// 주소 영역(앞쪽)과 cellar(뒤쪽)를 나누고, 충돌 시 비어 있는 칸을 뒤에서부터 찾아 쓴다.
class Coalesced {
    struct Slot { int key = 0; int next = -1; bool used = false; };
    std::vector<Slot> t;
    size_t addr;                                                  // 주소 영역 크기
    long freePtr;
    size_t h(int k) const { return (size_t)k % addr; }
public:
    Coalesced(size_t total, size_t addressRegion) : t(total), addr(addressRegion), freePtr((long)total - 1) {}
    bool insert(int k) {
        size_t i = h(k);
        if (!t[i].used) { t[i] = {k, -1, true}; return true; }
        for (;;) {
            if (t[i].key == k) return true;
            if (t[i].next < 0) break;
            i = t[i].next;
        }
        while (freePtr >= 0 && t[freePtr].used) freePtr--;
        if (freePtr < 0) return false;                            // 가득 참
        t[freePtr] = {k, -1, true};
        t[i].next = (int)freePtr;
        return true;
    }
    bool find(int k) const {
        size_t i = h(k);
        if (!t[i].used) return false;
        for (;;) {
            if (t[i].key == k) return true;
            if (t[i].next < 0) return false;
            i = t[i].next;
        }
    }
};

int main() {
    Coalesced t(11, 9);                                           // 주소 영역 0..8, cellar 9..10
    int keys[] = {5, 14, 23, 32, 1, 10, 7};                       // 5, 14, 23, 32 는 모두 홈 버킷 5
    for (int k : keys) assert(t.insert(k));
    for (int k : keys) assert(t.find(k));
    assert(!t.find(41) && !t.find(2));
    std::cout << "CoalescedHashing verified." << std::endl;
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
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 최소 완전 해시: n개 키를 [0, n) 에 빈틈없이 일대일로 대응시킨다 (hash-and-displace, CHD 방식).
// 키를 r개 버킷으로 나누고, 큰 버킷부터 "변위 d" 를 골라 버킷 안 키들이 모두 빈 칸에 떨어지게 한다.
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
        std::vector<std::vector<const std::string*>> buckets(r);
        for (auto& k : keys) buckets[hseed(k, 0) % r].push_back(&k);
        std::vector<size_t> order(r);
        for (size_t i = 0; i < r; i++) order[i] = i;
        std::sort(order.begin(), order.end(), [&](size_t a, size_t b) { return buckets[a].size() > buckets[b].size(); });
        std::vector<bool> taken(n, false);
        for (size_t b : order) {
            if (buckets[b].empty()) continue;
            for (uint32_t d = 1;; d++) {
                std::set<size_t> pos; bool ok = true;
                for (auto* k : buckets[b]) {
                    size_t p = hseed(*k, d) % n;
                    if (taken[p] || !pos.insert(p).second) { ok = false; break; }
                }
                if (ok) { for (size_t p : pos) taken[p] = true; disp[b] = d; break; }
            }
        }
    }
    size_t operator()(const std::string& k) const { return hseed(k, disp[hseed(k, 0) % r]) % n; }
};

int main() {
    std::vector<std::string> keys;
    for (int i = 0; i < 100; i++) keys.push_back("word" + std::to_string(i * 37));
    MPH f(keys);
    std::set<size_t> image;
    for (auto& k : keys) image.insert(f(k));
    assert(image.size() == keys.size());                         // 충돌 없음
    assert(*image.begin() == 0 && *image.rbegin() == keys.size() - 1);   // 정확히 [0, n) 을 채움 (최소)
    std::cout << "MinimalPerfectHash: " << keys.size() << " keys -> [0," << keys.size() << ")" << std::endl;
    return 0;
}
// Time Complexity: 탐색 O(len), 구성 기대 O(n)
// Space Complexity: O(n)  (키당 약 수 비트의 변위 배열)
```
# Part 5. 롤링 해시
## PolynomialRollingHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// H(s[l..r)) = (P[r] - P[l] * B^(r-l)) mod M  : 접두사 해시로 임의 부분 문자열의 해시를 O(1)에 구한다
struct Rolling {
    static const uint64_t M = 1000000007ULL, B = 911382323ULL;
    std::vector<uint64_t> pre, pw;
    explicit Rolling(const std::string& s) : pre(s.size() + 1, 0), pw(s.size() + 1, 1) {
        for (size_t i = 0; i < s.size(); i++) {
            pre[i + 1] = (pre[i] * B + (unsigned char)s[i]) % M;
            pw[i + 1] = pw[i] * B % M;
        }
    }
    uint64_t get(size_t l, size_t r) const { return (pre[r] + M - pre[l] * pw[r - l] % M) % M; }
};

std::vector<size_t> findAll(const std::string& text, const std::string& pat) {
    std::vector<size_t> res;
    Rolling t(text), p(pat);
    uint64_t hp = p.get(0, pat.size());
    for (size_t i = 0; i + pat.size() <= text.size(); i++)
        if (t.get(i, i + pat.size()) == hp && text.compare(i, pat.size(), pat) == 0) res.push_back(i);   // 해시 일치 후 실제 비교
    return res;
}

int main() {
    Rolling r("abracadabra");
    assert(r.get(0, 4) == r.get(7, 11));                           // "abra" == "abra"
    assert(r.get(0, 4) != r.get(1, 5));
    auto pos = findAll("abracadabra", "abra");
    assert((pos == std::vector<size_t>{0, 7}));
    std::cout << "PolynomialRollingHash matches at 0 and 7" << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(n), 부분 문자열 해시 O(1)
// Space Complexity: O(n)
```
## RabinFingerprint()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// 라빈 지문: GF(2)[x] 위의 다항식을 기약다항식 P(x) = x^32 + x^22 + x^2 + x + 1 로 나눈 나머지.
// 윈도우를 한 바이트 밀 때 가장 오래된 바이트의 기여를 XOR 로 지우고 x^8 을 곱한 뒤 새 바이트를 더한다.
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
    std::cout << "RabinFingerprint sliding window verified." << std::endl;
    return 0;
}
// Time Complexity: 슬라이드 1회 O(1)
// Space Complexity: O(256)
```
## LongestCommonSubstringHash()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// 두 문자열의 최장 공통 부분 문자열: 길이 L 에 대해 "공통 부분 문자열이 있는가" 는 단조 -> 이분 탐색 + 롤링 해시
typedef unsigned __int128 u128;
const uint64_t MOD = (1ULL << 61) - 1;
uint64_t mulmod(uint64_t a, uint64_t b) { return (uint64_t)((u128)a * b % MOD); }

struct Rolling {
    std::vector<uint64_t> pre, pw;
    Rolling(const std::string& s, uint64_t B) : pre(s.size() + 1, 0), pw(s.size() + 1, 1) {
        for (size_t i = 0; i < s.size(); i++) {
            pre[i + 1] = (mulmod(pre[i], B) + (unsigned char)s[i]) % MOD;
            pw[i + 1] = mulmod(pw[i], B);
        }
    }
    uint64_t get(size_t l, size_t r) const { return (pre[r] + MOD - mulmod(pre[l], pw[r - l])) % MOD; }
};

std::string lcs(const std::string& a, const std::string& b) {
    const uint64_t B = 1000003;
    Rolling ra(a, B), rb(b, B);
    auto check = [&](size_t L, size_t& posA) {
        std::unordered_map<uint64_t, size_t> seen;
        for (size_t i = 0; i + L <= a.size(); i++) seen[ra.get(i, i + L)] = i;
        for (size_t j = 0; j + L <= b.size(); j++) {
            auto it = seen.find(rb.get(j, j + L));
            if (it != seen.end() && a.compare(it->second, L, b, j, L) == 0) { posA = it->second; return true; }   // 충돌 방지용 실제 비교
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

int main() {
    assert(lcs("abcdxyz", "xyzabcd") == "abcd");
    assert(lcs("zxabcdezy", "yzabcdezx") == "abcdez");
    assert(lcs("abc", "xyz").empty());
    std::cout << "LongestCommonSubstringHash: " << lcs("abcdxyz", "xyzabcd") << std::endl;
    return 0;
}
// Time Complexity: O((n + m) log min(n, m))
// Space Complexity: O(n + m)
```
# Part 6. 해시 컨테이너
## HashMap()
### 대표코드
```cpp
#include <iostream>
#include <functional>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// 체이닝 해시맵: operator[], find, erase, 적재율 1.0 초과 시 2배 확장
template <class K, class V, class Hash = std::hash<K>>
class HashMap {
    std::vector<std::vector<std::pair<K, V>>> b;
    size_t n = 0;
    size_t idx(const K& k, size_t m) const { return Hash{}(k) % m; }
    void grow() {
        std::vector<std::vector<std::pair<K, V>>> nb(b.size() * 2);
        for (auto& chain : b) for (auto& kv : chain) nb[idx(kv.first, nb.size())].push_back(std::move(kv));
        b.swap(nb);
    }
public:
    HashMap() : b(8) {}
    V& operator[](const K& k) {
        for (auto& kv : b[idx(k, b.size())]) if (kv.first == k) return kv.second;
        if (n + 1 > b.size()) grow();
        b[idx(k, b.size())].emplace_back(k, V{});
        ++n;
        return b[idx(k, b.size())].back().second;
    }
    V* find(const K& k) {
        for (auto& kv : b[idx(k, b.size())]) if (kv.first == k) return &kv.second;
        return nullptr;
    }
    bool erase(const K& k) {
        auto& chain = b[idx(k, b.size())];
        for (size_t i = 0; i < chain.size(); i++)
            if (chain[i].first == k) { chain[i] = std::move(chain.back()); chain.pop_back(); --n; return true; }
        return false;
    }
    size_t size() const { return n; }
    double loadFactor() const { return double(n) / b.size(); }
};

int main() {
    HashMap<std::string, int> m;
    for (int i = 0; i < 1000; i++) m["k" + std::to_string(i)] = i;
    m["k5"] += 100;
    assert(m.size() == 1000 && *m.find("k5") == 105);
    assert(m.erase("k7") && m.find("k7") == nullptr && m.size() == 999);
    assert(m.loadFactor() <= 1.0);
    std::cout << "HashMap size=" << m.size() << " load=" << m.loadFactor() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 확장은 분할상환
// Space Complexity: O(n)
```
## LinkedHashMap()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// LinkedHashMap: 해시맵 + 이중 연결 리스트. 순회 순서가 삽입 순서(또는 접근 순서)로 고정된다.
template <class K, class V>
class LinkedHashMap {
    std::list<std::pair<K, V>> order;
    std::unordered_map<K, typename std::list<std::pair<K, V>>::iterator> index;
    bool accessOrder;
public:
    explicit LinkedHashMap(bool access = false) : accessOrder(access) {}
    void put(const K& k, const V& v) {
        auto it = index.find(k);
        if (it != index.end()) { it->second->second = v; if (accessOrder) order.splice(order.end(), order, it->second); return; }
        order.emplace_back(k, v);
        index[k] = std::prev(order.end());
    }
    V* get(const K& k) {
        auto it = index.find(k);
        if (it == index.end()) return nullptr;
        if (accessOrder) order.splice(order.end(), order, it->second);    // 접근하면 맨 뒤로
        return &it->second->second;
    }
    bool erase(const K& k) {
        auto it = index.find(k);
        if (it == index.end()) return false;
        order.erase(it->second); index.erase(it);
        return true;
    }
    std::vector<K> keys() const { std::vector<K> r; for (auto& kv : order) r.push_back(kv.first); return r; }
};

int main() {
    LinkedHashMap<std::string, int> ins;                                  // 삽입 순서
    ins.put("c", 3); ins.put("a", 1); ins.put("b", 2); ins.put("a", 10);   // 갱신은 순서를 바꾸지 않는다
    assert((ins.keys() == std::vector<std::string>{"c", "a", "b"}));
    LinkedHashMap<std::string, int> acc(true);                            // 접근 순서 (LRU 캐시의 기초)
    acc.put("x", 1); acc.put("y", 2); acc.put("z", 3);
    acc.get("x");
    assert((acc.keys() == std::vector<std::string>{"y", "z", "x"}));
    assert(acc.erase("z") && (acc.keys() == std::vector<std::string>{"y", "x"}));
    std::cout << "LinkedHashMap verified." << std::endl;
    return 0;
}
// Time Complexity: put/get/erase 평균 O(1)
// Space Complexity: O(n)
```
## Multimap()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// 멀티맵: 하나의 키에 여러 값을 허용한다. 해시 버전은 key -> 값 목록으로 구현한다
template <class K, class V>
class Multimap {
    std::unordered_map<K, std::vector<V>> m;
    size_t total = 0;
public:
    void insert(const K& k, const V& v) { m[k].push_back(v); ++total; }
    size_t count(const K& k) const { auto it = m.find(k); return it == m.end() ? 0 : it->second.size(); }
    const std::vector<V>& equalRange(const K& k) const {
        static const std::vector<V> empty;
        auto it = m.find(k); return it == m.end() ? empty : it->second;
    }
    size_t erase(const K& k) {                                           // 키 하나의 모든 값을 지운다
        auto it = m.find(k); if (it == m.end()) return 0;
        size_t c = it->second.size(); total -= c; m.erase(it); return c;
    }
    size_t size() const { return total; }
};

int main() {
    Multimap<std::string, int> mm;
    mm.insert("fruit", 1); mm.insert("fruit", 2); mm.insert("veg", 3); mm.insert("fruit", 4);
    assert(mm.size() == 4 && mm.count("fruit") == 3 && mm.count("none") == 0);
    assert((mm.equalRange("fruit") == std::vector<int>{1, 2, 4}));
    assert(mm.erase("fruit") == 3 && mm.size() == 1);
    std::cout << "Multimap verified." << std::endl;
    return 0;
}
// Time Complexity: insert 분할상환 O(1), erase(key) O(값 개수)
// Space Complexity: O(n)
```
# Part 7. 분산 해시
## ConsistentHashing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 일관된 해싱: 노드와 키를 같은 해시 링(2^32)에 놓고, 키는 시계 방향으로 처음 만나는 노드가 맡는다.
// 노드가 늘거나 줄어도 이웃 구간의 키만 이동한다.
uint32_t h32(const std::string& s) {
    uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16;
    return h;
}

class Ring {
    std::map<uint32_t, std::string> ring;
public:
    void add(const std::string& node) { ring[h32(node)] = node; }
    void remove(const std::string& node) { ring.erase(h32(node)); }
    const std::string& owner(const std::string& key) const {
        auto it = ring.lower_bound(h32(key));
        if (it == ring.end()) it = ring.begin();             // 링이므로 끝에서 처음으로 돌아간다
        return it->second;
    }
};

int main() {
    Ring r;
    for (int i = 0; i < 5; i++) r.add("node" + std::to_string(i));
    const int K = 10000;
    std::vector<std::string> before(K);
    for (int i = 0; i < K; i++) before[i] = r.owner("key" + std::to_string(i));
    r.add("node5");                                          // 노드 추가
    int moved = 0;
    for (int i = 0; i < K; i++) {
        const std::string& now = r.owner("key" + std::to_string(i));
        if (now != before[i]) { moved++; assert(now == "node5"); }   // 이동한 키는 전부 새 노드로만 간다
    }
    assert(moved < K / 2);
    std::cout << "moved " << moved << " of " << K << " keys after adding a node" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(log N)
// Space Complexity: O(N)
```
## VirtualNode()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 가상 노드: 물리 노드 하나를 링 위의 여러 지점(node#0, node#1, ...)에 배치해 부하를 고르게 만든다
uint32_t h32(const std::string& s) {
    uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16;
    return h;
}

double imbalance(int vnodes) {                               // 최대 부하 / 평균 부하
    std::map<uint32_t, int> ring;
    const int N = 5;
    for (int n = 0; n < N; n++)
        for (int v = 0; v < vnodes; v++) ring[h32("node" + std::to_string(n) + "#" + std::to_string(v))] = n;
    std::vector<int> load(N, 0);
    const int K = 20000;
    for (int i = 0; i < K; i++) {
        auto it = ring.lower_bound(h32("key" + std::to_string(i)));
        if (it == ring.end()) it = ring.begin();
        load[it->second]++;
    }
    return double(*std::max_element(load.begin(), load.end())) / (double(K) / N);
}

int main() {
    double one = imbalance(1), many = imbalance(200);
    assert(many < one);                                      // 가상 노드가 많을수록 균형이 좋다
    assert(many < 1.25);
    std::cout << "imbalance (max/mean): 1 vnode = " << one << ", 200 vnodes = " << many << std::endl;
    return 0;
}
// Time Complexity: 조회 O(log(N·V))
// Space Complexity: O(N·V)
```
## RendezvousHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// 랑데부(HRW) 해싱: 키마다 모든 노드의 점수 hash(key, node) 를 계산해 가장 높은 노드를 고른다.
// 링 구조 없이도 노드 제거 시 그 노드의 키만 이동한다 (조회는 O(N))
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
uint64_t score(const std::string& key, const std::string& node) {
    uint64_t h = 1469598103934665603ULL;
    for (unsigned char c : key + "|" + node) { h ^= c; h *= 1099511628211ULL; }
    return mix(h);
}
std::string pick(const std::string& key, const std::vector<std::string>& nodes) {
    std::string best; uint64_t bs = 0;
    for (auto& n : nodes) { uint64_t s = score(key, n); if (best.empty() || s > bs) { bs = s; best = n; } }
    return best;
}

int main() {
    std::vector<std::string> nodes = {"A", "B", "C", "D", "E"};
    const int K = 5000;
    std::vector<std::string> before(K);
    for (int i = 0; i < K; i++) before[i] = pick("key" + std::to_string(i), nodes);
    std::vector<std::string> fewer = {"A", "B", "C", "E"};          // D 제거
    int moved = 0;
    for (int i = 0; i < K; i++) {
        std::string now = pick("key" + std::to_string(i), fewer);
        if (now != before[i]) { moved++; assert(before[i] == "D"); }  // 이동한 키는 전부 D 가 갖고 있던 키
    }
    assert(moved > 0 && moved < K / 3);
    std::cout << "removed D: moved " << moved << " keys, all previously owned by D" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(N)
// Space Complexity: O(N)
```
## Chord()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <vector>
#include <cassert>

// Chord: m비트 식별자 링. 노드 n 의 i번째 finger 는 successor(n + 2^i).
// 조회마다 목표 거리가 최소 절반으로 줄어 O(log N) 홉에 끝난다
const int M = 6, SZ = 1 << M;                                   // 식별자 0..63
std::vector<int> nodes = {1, 8, 14, 21, 32, 38, 42, 48, 51, 56};

int successor(int id) {                                         // 전역 정답 (검증용)
    for (int n : nodes) if (n >= id % SZ) return n;
    return nodes[0];
}
bool inRange(int x, int a, int b, bool inclusiveB) {            // x in (a, b] 또는 (a, b)  (원형)
    if (a < b) return x > a && (inclusiveB ? x <= b : x < b);
    return x > a || (inclusiveB ? x <= b : x < b);
}
int finger(int n, int i) { return successor((n + (1 << i)) % SZ); }
int nextNode(int n) { return successor((n + 1) % SZ); }

int closestPrecedingFinger(int n, int id) {
    for (int i = M - 1; i >= 0; i--) {
        int f = finger(n, i);
        if (inRange(f, n, id, false)) return f;
    }
    return n;
}

int findSuccessor(int start, int id, int& hops) {
    int n = start;
    hops = 0;
    while (!inRange(id, n, nextNode(n), true)) {                // id 가 (n, successor(n)] 에 들 때까지 점프
        int nn = closestPrecedingFinger(n, id);
        if (nn == n) break;
        n = nn; hops++;
    }
    return nextNode(n);
}

int main() {
    int maxHops = 0;
    for (int start : nodes)
        for (int id = 0; id < SZ; id++) {
            int hops;
            int got = findSuccessor(start, id, hops);
            assert(got == successor(id));                       // 모든 시작 노드·모든 키에서 정답과 일치
            maxHops = std::max(maxHops, hops);
        }
    assert(maxHops <= M);
    std::cout << "Chord: all lookups correct, max hops = " << maxHops << " (m = " << M << ")" << std::endl;
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
#include <iostream>
#include <cstdint>
#include <map>
#include <string>
#include <cassert>

// 단순 모듈러 분배(hash % N)는 N 이 바뀌면 거의 모든 키가 이동한다 -> 캐시 서버 한 대만 늘려도 캐시가 통째로 무효화된다
uint32_t h32(const std::string& s) {
    uint32_t h = 2166136261u;
    for (unsigned char c : s) { h ^= c; h *= 16777619u; }
    h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16;
    return h;
}

int main() {
    const int K = 20000;
    int modMoved = 0, ringMoved = 0;
    std::map<uint32_t, int> ring4, ring5;
    for (int n = 0; n < 5; n++) {
        for (int v = 0; v < 100; v++) {
            uint32_t p = h32("n" + std::to_string(n) + "#" + std::to_string(v));
            if (n < 4) ring4[p] = n;
            ring5[p] = n;
        }
    }
    auto own = [](std::map<uint32_t, int>& r, uint32_t h) { auto it = r.lower_bound(h); return (it == r.end() ? r.begin() : it)->second; };
    for (int i = 0; i < K; i++) {
        uint32_t h = h32("k" + std::to_string(i));
        if (h % 4 != h % 5) modMoved++;
        if (own(ring4, h) != own(ring5, h)) ringMoved++;
    }
    double modFrac = double(modMoved) / K, ringFrac = double(ringMoved) / K;
    assert(modFrac > 0.7);                                      // 이론값 1 - 1/5 에 가깝다 (N 이 4 -> 5)
    assert(ringFrac < 0.3);                                     // 이론값 1/5
    std::cout << "servers 4 -> 5: hash%N moves " << modFrac * 100 << "%, consistent hashing moves " << ringFrac * 100 << "%" << std::endl;
    return 0;
}
// Time Complexity: O(K log N)
// Space Complexity: O(N·V)
```
# Part 8. 암호학적 해시
## MD5()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <cassert>

// MD5 (RFC 1321). 충돌이 구성되어 보안 용도로는 쓸 수 없지만 체크섬으로는 여전히 쓰인다.
// 상수 K[i] = floor(2^32 * |sin(i+1)|) 는 코드로 직접 계산한다 ("nothing up my sleeve" 수)
static inline uint32_t rotl(uint32_t x, int c) { return (x << c) | (x >> (32 - c)); }
std::string md5(const std::string& msg) {
    static const int S[64] = {7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22, 5,9,14,20,5,9,14,20,5,9,14,20,5,9,14,20,
                              4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23, 6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21};
    uint32_t K[64];
    for (int i = 0; i < 64; i++) K[i] = (uint32_t)(std::fabs(std::sin((long double)(i + 1))) * 4294967296.0L);
    uint32_t a0 = 0x67452301, b0 = 0xefcdab89, c0 = 0x98badcfe, d0 = 0x10325476;
    std::vector<uint8_t> m(msg.begin(), msg.end());
    uint64_t bits = (uint64_t)msg.size() * 8;
    m.push_back(0x80);
    while (m.size() % 64 != 56) m.push_back(0);
    for (int i = 0; i < 8; i++) m.push_back((bits >> (8 * i)) & 0xff);          // 길이: 리틀엔디언
    for (size_t off = 0; off < m.size(); off += 64) {
        uint32_t w[16];
        for (int i = 0; i < 16; i++) std::memcpy(&w[i], &m[off + 4 * i], 4);   // 리틀엔디언 호스트 가정
        uint32_t A = a0, B = b0, C = c0, D = d0;
        for (int i = 0; i < 64; i++) {
            uint32_t F; int g;
            if (i < 16)      { F = (B & C) | (~B & D); g = i; }
            else if (i < 32) { F = (D & B) | (~D & C); g = (5 * i + 1) % 16; }
            else if (i < 48) { F = B ^ C ^ D;          g = (3 * i + 5) % 16; }
            else             { F = C ^ (B | ~D);       g = (7 * i) % 16; }
            F = F + A + K[i] + w[g];
            A = D; D = C; C = B; B = B + rotl(F, S[i]);
        }
        a0 += A; b0 += B; c0 += C; d0 += D;
    }
    char out[33];
    uint32_t r[4] = {a0, b0, c0, d0};
    for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) std::snprintf(out + 8 * i + 2 * j, 3, "%02x", (r[i] >> (8 * j)) & 0xff);
    return out;
}

int main() {
    assert(md5("") == "d41d8cd98f00b204e9800998ecf8427e");
    assert(md5("abc") == "900150983cd24fb0d6963f7d28e17f72");
    assert(md5("The quick brown fox jumps over the lazy dog") == "9e107d9d372bb6826bd81d3542a419d6");
    std::cout << "md5(abc) = " << md5("abc") << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(len)  (구현의 편의상 패딩 사본을 만든다)
```
## SHA256()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// SHA-256 (FIPS 180-4). 초기값은 처음 8개 소수의 제곱근, 라운드 상수는 처음 64개 소수의 세제곱근의 소수부 상위 32비트
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
std::string sha256(const std::string& msg) {
    std::vector<uint32_t> primes;
    for (uint32_t p = 2; primes.size() < 64; p++) {
        bool ok = true; for (uint32_t q : primes) if (p % q == 0) { ok = false; break; }
        if (ok) primes.push_back(p);
    }
    uint32_t K[64], H[8];
    for (int i = 0; i < 64; i++) { long double c = cbrtl((long double)primes[i]); K[i] = (uint32_t)((c - floorl(c)) * 4294967296.0L); }
    for (int i = 0; i < 8; i++)  { long double s = sqrtl((long double)primes[i]); H[i] = (uint32_t)((s - floorl(s)) * 4294967296.0L); }
    std::vector<uint8_t> m(msg.begin(), msg.end());
    uint64_t bits = (uint64_t)msg.size() * 8;
    m.push_back(0x80);
    while (m.size() % 64 != 56) m.push_back(0);
    for (int i = 7; i >= 0; i--) m.push_back((bits >> (8 * i)) & 0xff);          // 길이: 빅엔디언
    for (size_t off = 0; off < m.size(); off += 64) {
        uint32_t w[64];
        for (int i = 0; i < 16; i++) w[i] = m[off + 4*i] << 24 | m[off + 4*i + 1] << 16 | m[off + 4*i + 2] << 8 | m[off + 4*i + 3];
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
    char out[65];
    for (int i = 0; i < 8; i++) std::snprintf(out + 8 * i, 9, "%08x", H[i]);
    return out;
}

int main() {
    assert(sha256("") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    assert(sha256("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    assert(sha256("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq") ==
           "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");     // 두 블록짜리 표준 시험값
    std::cout << "sha256(abc) = " << sha256("abc") << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(len)
```
## HMAC()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// HMAC(K, m) = H((K' ⊕ opad) || H((K' ⊕ ipad) || m)).  단순히 H(K || m) 을 쓰면 길이 확장 공격에 취약하다 (MerkleDamgard 항목 참고)
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
std::string sha256raw(const std::string& msg) {
    std::vector<uint32_t> primes;
    for (uint32_t p = 2; primes.size() < 64; p++) { bool ok = true; for (uint32_t q : primes) if (p % q == 0) { ok = false; break; } if (ok) primes.push_back(p); }
    uint32_t K[64], H[8];
    for (int i = 0; i < 64; i++) { long double c = cbrtl((long double)primes[i]); K[i] = (uint32_t)((c - floorl(c)) * 4294967296.0L); }
    for (int i = 0; i < 8; i++)  { long double s = sqrtl((long double)primes[i]); H[i] = (uint32_t)((s - floorl(s)) * 4294967296.0L); }
    std::vector<uint8_t> m(msg.begin(), msg.end());
    uint64_t bits = (uint64_t)msg.size() * 8;
    m.push_back(0x80); while (m.size() % 64 != 56) m.push_back(0);
    for (int i = 7; i >= 0; i--) m.push_back((bits >> (8 * i)) & 0xff);
    for (size_t off = 0; off < m.size(); off += 64) {
        uint32_t w[64];
        for (int i = 0; i < 16; i++) w[i] = m[off+4*i] << 24 | m[off+4*i+1] << 16 | m[off+4*i+2] << 8 | m[off+4*i+3];
        for (int i = 16; i < 64; i++) {
            uint32_t s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >> 3), s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >> 10);
            w[i] = w[i-16] + s0 + w[i-7] + s1;
        }
        uint32_t a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
        for (int i = 0; i < 64; i++) {
            uint32_t t1 = h + (rotr(e,6)^rotr(e,11)^rotr(e,25)) + ((e&f)^(~e&g)) + K[i] + w[i];
            uint32_t t2 = (rotr(a,2)^rotr(a,13)^rotr(a,22)) + ((a&b)^(a&c)^(b&c));
            h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
        }
        H[0]+=a; H[1]+=b; H[2]+=c; H[3]+=d; H[4]+=e; H[5]+=f; H[6]+=g; H[7]+=h;
    }
    std::string out;
    for (int i = 0; i < 8; i++) for (int j = 3; j >= 0; j--) out.push_back((char)((H[i] >> (8 * j)) & 0xff));
    return out;
}
std::string hex(const std::string& s) { static const char* d = "0123456789abcdef"; std::string r; for (unsigned char c : s) { r += d[c >> 4]; r += d[c & 15]; } return r; }

std::string hmacSha256(std::string key, const std::string& msg) {
    const size_t block = 64;
    if (key.size() > block) key = sha256raw(key);
    key.resize(block, '\0');
    std::string ipad(block, 0), opad(block, 0);
    for (size_t i = 0; i < block; i++) { ipad[i] = key[i] ^ 0x36; opad[i] = key[i] ^ 0x5c; }
    return sha256raw(opad + sha256raw(ipad + msg));
}

int main() {
    assert(hex(hmacSha256("key", "The quick brown fox jumps over the lazy dog")) ==
           "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8");     // 위키피디아의 표준 시험값
    assert(hmacSha256("key", "a") != hmacSha256("kex", "a"));
    std::cout << "hmac = " << hex(hmacSha256("key", "The quick brown fox jumps over the lazy dog")) << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(len)
```
## MerkleDamgard()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <cassert>

// 머클-담고르 구성: IV 에서 시작해 메시지를 블록 단위로 압축함수에 먹이고, 마지막에 길이를 포함한 패딩을 붙인다.
// 최종 해시가 곧 내부 상태이므로, 해시값과 길이만 알면 이어서 계속 압축할 수 있다 -> 길이 확장 공격.
// (여기서는 구조를 보이려고 32비트 장난감 압축함수를 쓴다. 실제 해시의 압축함수는 SHA-256 항목 참고)
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
    std::cout << "length-extension forgery accepted: tag=" << std::hex << forged << std::endl;
    return 0;
}
// Time Complexity: O(len)
// Space Complexity: O(len)
```
## 암호학적 해시와 일반 해시의 차이
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// 일반 해시(해시 테이블용)는 빠르고 분포가 좋으면 충분하지만 "되돌릴 수 있다".
// 예) MurmurHash3 의 마지막 섞기 fmix32 는 전단사이며, 역함수를 바로 구성할 수 있다 -> 원상(preimage)을 즉시 계산
uint32_t fmix32(uint32_t h) { h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16; return h; }
uint32_t modInverse(uint32_t a) { uint32_t x = a; for (int i = 0; i < 5; i++) x *= 2 - a * x; return x; }   // 홀수 a 의 2^32 역원 (뉴턴 반복)
uint32_t unxorshift(uint32_t y, int s) { uint32_t x = y; for (int i = 0; i < 32 / s + 1; i++) x = y ^ (x >> s); return x; }
uint32_t unfmix32(uint32_t h) {
    h = unxorshift(h, 16); h *= modInverse(0xc2b2ae35); h = unxorshift(h, 13); h *= modInverse(0x85ebca6b); h = unxorshift(h, 16);
    return h;
}

int main() {
    for (uint32_t x : {0u, 1u, 12345u, 0xdeadbeefu, 0xffffffffu}) {
        uint32_t h = fmix32(x);
        assert(unfmix32(h) == x);                                  // 해시값만 보고 입력을 그대로 복원
    }
    // 암호학적 해시는 원상 저항성(preimage resistance)·충돌 저항성·눈사태 효과(입력 1비트 -> 출력 절반이 뒤집힘)를 요구한다.
    // 일반 해시도 눈사태는 좋을 수 있으나, 위 예처럼 역산·충돌 구성이 쉬워 보안 용도로는 부적합하다.
    int flipped = 0, total = 0;
    for (uint32_t x = 0; x < 2000; x++) for (int b = 0; b < 32; b++) { flipped += __builtin_popcount(fmix32(x) ^ fmix32(x ^ (1u << b))); total += 32; }
    double ratio = double(flipped) / total;
    assert(ratio > 0.45 && ratio < 0.55);                          // 눈사태는 좋지만...
    std::cout << "fmix32 avalanche ratio " << ratio << " but invertible; a cryptographic hash must not be." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
# Part 9. DB 해시
## HashIndex()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// 해시 인덱스: 열 값 -> 행 번호 목록. 등치(=) 조회는 O(1)이지만 범위(<, BETWEEN)·정렬에는 쓸 수 없다 (그때는 B+Tree)
struct Row { int id; std::string city; };
class HashIndex {
    std::unordered_map<std::string, std::vector<size_t>> idx;
public:
    void build(const std::vector<Row>& rows) { for (size_t i = 0; i < rows.size(); i++) idx[rows[i].city].push_back(i); }
    const std::vector<size_t>& equal(const std::string& city) const {
        static const std::vector<size_t> none;
        auto it = idx.find(city); return it == idx.end() ? none : it->second;
    }
};

int main() {
    std::vector<Row> rows = {{1, "Seoul"}, {2, "Busan"}, {3, "Seoul"}, {4, "Daegu"}, {5, "Seoul"}};
    HashIndex ix; ix.build(rows);
    assert((ix.equal("Seoul") == std::vector<size_t>{0, 2, 4}));
    assert(ix.equal("Jeju").empty());
    // 범위 조건은 인덱스를 못 쓰고 전체 스캔이 필요하다: city BETWEEN 'B' AND 'D'
    int scanned = 0, hit = 0;
    for (auto& r : rows) { scanned++; if (r.city >= "B" && r.city < "E") hit++; }
    assert(scanned == 5 && hit == 2);
    std::cout << "HashIndex: equality O(1); range query scanned " << scanned << " rows" << std::endl;
    return 0;
}
// Time Complexity: 등치 조회 O(1), 범위 조회 O(n)
// Space Complexity: O(n)
```
## HashJoin()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// 해시 조인: (1) 작은 테이블로 해시 테이블을 만들고(build) (2) 큰 테이블을 훑으며 탐색(probe). 중첩 루프 O(n·m) -> O(n+m)
struct R { int id; std::string name; };
struct S { int id; int score; };
typedef std::pair<std::string, int> Out;

std::vector<Out> hashJoin(const std::vector<R>& r, const std::vector<S>& s) {
    std::unordered_multimap<int, const R*> build;
    for (auto& x : r) build.emplace(x.id, &x);                       // build 단계
    std::vector<Out> out;
    for (auto& y : s) {                                              // probe 단계
        auto range = build.equal_range(y.id);
        for (auto it = range.first; it != range.second; ++it) out.push_back({it->second->name, y.score});
    }
    return out;
}
std::vector<Out> nestedLoop(const std::vector<R>& r, const std::vector<S>& s) {
    std::vector<Out> out;
    for (auto& y : s) for (auto& x : r) if (x.id == y.id) out.push_back({x.name, y.score});
    return out;
}

int main() {
    std::vector<R> r = {{1, "kim"}, {2, "lee"}, {3, "park"}, {3, "park2"}};
    std::vector<S> s = {{3, 90}, {1, 70}, {4, 50}, {3, 85}};
    auto a = hashJoin(r, s), b = nestedLoop(r, s);
    std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end());
    assert(a == b && a.size() == 5);                                 // 두 방식의 결과가 같다 (id=3 은 2x2 중 매칭)
    std::cout << "HashJoin produced " << a.size() << " rows" << std::endl;
    return 0;
}
// Time Complexity: O(n + m + 결과)
// Space Complexity: O(작은 쪽 테이블)
```
## ExtendibleHashing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <memory>
#include <vector>
#include <cassert>

// 확장 해싱: 디렉터리(2^전역깊이)가 해시의 하위 비트로 버킷을 가리킨다.
// 버킷이 넘치면 그 버킷만 쪼개고, 지역 깊이가 전역 깊이와 같을 때만 디렉터리를 2배로 늘린다 (전체 재해시 없음)
uint32_t mix(uint32_t x) { x ^= x >> 16; x *= 0x7feb352d; x ^= x >> 15; x *= 0x846ca68b; x ^= x >> 16; return x; }
struct Bucket { int depth; std::vector<uint32_t> keys; };

class Extendible {
    static const size_t CAP = 2;
    int gd = 1;
    std::vector<std::shared_ptr<Bucket>> dir;
public:
    Extendible() : dir(2) { dir[0] = std::make_shared<Bucket>(Bucket{1, {}}); dir[1] = std::make_shared<Bucket>(Bucket{1, {}}); }
    size_t dirIndex(uint32_t k) const { return mix(k) & ((1u << gd) - 1); }
    bool contains(uint32_t k) const { for (auto x : dir[dirIndex(k)]->keys) if (x == k) return true; return false; }
    void insert(uint32_t k) {
        if (contains(k)) return;
        auto b = dir[dirIndex(k)];
        if (b->keys.size() < CAP) { b->keys.push_back(k); return; }
        if (b->depth == gd) {                                       // 디렉터리 배가
            dir.resize(dir.size() * 2);
            for (size_t i = 0; i < dir.size() / 2; i++) dir[i + dir.size() / 2] = dir[i];
            gd++;
        }
        auto nb = std::make_shared<Bucket>(Bucket{b->depth + 1, {}});
        b->depth++;
        uint32_t bit = 1u << (b->depth - 1);
        for (size_t i = 0; i < dir.size(); i++) if (dir[i] == b && (i & bit)) dir[i] = nb;   // 절반을 새 버킷으로 연결
        std::vector<uint32_t> old; old.swap(b->keys);
        for (auto x : old) insert(x);
        insert(k);
    }
    int globalDepth() const { return gd; }
    size_t dirSize() const { return dir.size(); }
    bool consistent() const { for (auto& b : dir) if (b->depth > gd) return false; return true; }
};

int main() {
    Extendible t;
    for (uint32_t k = 1; k <= 200; k++) t.insert(k * 2654435761u);
    for (uint32_t k = 1; k <= 200; k++) assert(t.contains(k * 2654435761u));
    assert(!t.contains(3));
    assert(t.dirSize() == (1u << t.globalDepth()) && t.consistent());
    std::cout << "ExtendibleHashing: 200 keys, global depth " << t.globalDepth() << ", directory " << t.dirSize() << std::endl;
    return 0;
}
// Time Complexity: 조회 O(1) (디렉터리 1회 + 버킷 1회)
// Space Complexity: O(n + 2^전역깊이)
```
## LinearHashing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 선형 해싱: 디렉터리 없이 "분할 포인터" p 순서대로 버킷을 하나씩 쪼갠다.
// 주소 = h mod (N0·2^L), 이미 쪼갠 구간(주소 < p)이면 h mod (N0·2^(L+1)).  넘친 버킷이 아니라 p 가 가리키는 버킷이 쪼개진다
uint32_t mix(uint32_t x) { x ^= x >> 16; x *= 0x7feb352d; x ^= x >> 15; x *= 0x846ca68b; x ^= x >> 16; return x; }

class LinearHash {
    static const size_t N0 = 4;
    int level = 0; size_t p = 0, count = 0;
    std::vector<std::vector<uint32_t>> b;
    size_t addr(uint32_t k) const {
        size_t a = mix(k) % (N0 << level);
        return a < p ? mix(k) % (N0 << (level + 1)) : a;
    }
    void split() {                                                  // 버킷 p 하나만 둘로 나눈다
        b.emplace_back();
        std::vector<uint32_t> old; old.swap(b[p]);
        for (auto k : old) b[mix(k) % (N0 << (level + 1))].push_back(k);
        if (++p == (N0 << level)) { level++; p = 0; }
    }
public:
    LinearHash() : b(N0) {}
    void insert(uint32_t k) {
        if (contains(k)) return;
        b[addr(k)].push_back(k); ++count;
        if (double(count) / b.size() > 2.0) split();               // 버킷당 평균 2개를 넘으면 분할
    }
    bool contains(uint32_t k) const { for (auto x : b[addr(k)]) if (x == k) return true; return false; }
    size_t buckets() const { return b.size(); }
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
    std::cout << "LinearHashing: 500 keys in " << t.buckets() << " buckets" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(1) 평균, 분할 1회 O(버킷 크기)
// Space Complexity: O(n)
```
# Part 10. OS·런타임 구현
## 왜 Java HashMap은 TreeBin으로 바뀌는가?
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// Java 8 HashMap: 한 버킷(bin)의 연결 리스트가 8개 이상이고 테이블 크기가 64 이상이면 레드-블랙 트리(TreeBin)로 바꾼다.
// 해시가 몰려도 (또는 공격당해도) 한 bin 의 탐색이 O(n) -> O(log n) 이 된다. 6개 이하로 줄면 다시 리스트로 되돌린다.
const int TREEIFY_THRESHOLD = 8, UNTREEIFY_THRESHOLD = 6, MIN_TREEIFY_CAPACITY = 64;
std::string binKind(int binSize, int tableCapacity, bool wasTree) {
    if (wasTree) return binSize <= UNTREEIFY_THRESHOLD ? "list" : "tree";
    if (binSize >= TREEIFY_THRESHOLD) return tableCapacity >= MIN_TREEIFY_CAPACITY ? "tree" : "resize";   // 용량이 작으면 트리 대신 테이블 확장
    return "list";
}

struct CountingLess {
    static long calls;
    bool operator()(const std::string& a, const std::string& b) const { ++calls; return a < b; }
};
long CountingLess::calls = 0;

int main() {
    assert(binKind(7, 64, false) == "list");
    assert(binKind(8, 64, false) == "tree");
    assert(binKind(8, 32, false) == "resize");
    assert(binKind(6, 64, true) == "list" && binKind(7, 64, true) == "tree");

    // 같은 bin 에 N 개의 키가 몰린 최악의 경우: 리스트 탐색 vs 트리 탐색의 비교 횟수
    const int N = 1024;
    std::vector<std::string> list;
    std::map<std::string, int, CountingLess> tree;
    for (int i = 0; i < N; i++) { std::string k = "key" + std::to_string(i * 7919 % 100003); list.push_back(k); tree[k] = i; }
    long listCmp = 0;
    for (auto& k : list) { for (auto& x : list) { ++listCmp; if (x == k) break; } }
    CountingLess::calls = 0;
    for (auto& k : list) tree.find(k);
    double avgList = double(listCmp) / N, avgTree = double(CountingLess::calls) / N;
    assert(avgTree < avgList / 10);
    std::cout << "average comparisons in one bin of " << N << ": list " << avgList << ", tree " << avgTree << std::endl;
    return 0;
}
// Time Complexity: 리스트 bin O(n), 트리 bin O(log n)
// Space Complexity: O(n)
```
## Python dict의 구현 원리
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// CPython 3.6+ 의 compact dict: 해시 테이블(indices)은 "entries 배열의 번호"만 갖고,
// 실제 (hash, key, value) 는 삽입 순서대로 entries 에 쌓인다 -> 삽입 순서 보존 + 메모리 절약.
// 충돌은 개방 주소법: i = (5*i + perturb + 1) mod size,  perturb 는 매번 5비트씩 오른쪽 시프트 (해시의 상위 비트도 쓰도록)
class PyDict {
    static constexpr int EMPTY = -1, DUMMY = -2;
    struct Entry { long key; long value; bool live; };
    std::vector<int> indices = std::vector<int>(8, EMPTY);
    std::vector<Entry> entries;
    size_t used = 0;
    size_t mask() const { return indices.size() - 1; }
    int lookup(long key, size_t& slot) const {
        size_t perturb = (size_t)key, i = perturb & mask();
        long firstDummy = -1;
        for (;;) {
            int ix = indices[i];
            if (ix == EMPTY) { slot = firstDummy >= 0 ? (size_t)firstDummy : i; return -1; }
            if (ix == DUMMY) { if (firstDummy < 0) firstDummy = i; }
            else if (entries[ix].live && entries[ix].key == key) { slot = i; return ix; }
            perturb >>= 5;
            i = (i * 5 + perturb + 1) & mask();
        }
    }
    void resize() {                                              // 살아있는 entries 만 모아 indices 를 새로 만든다
        std::vector<Entry> live;
        for (auto& e : entries) if (e.live) live.push_back(e);
        entries = live;
        indices.assign(indices.size() * 2, EMPTY);
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
        if (entries.size() >= indices.size() * 2 / 3) { resize(); lookup(key, slot); }   // 사용률 2/3 에서 확장
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
    assert(d.tableSize() >= 128);
    std::cout << "PyDict size=" << d.size() << " table=" << d.tableSize() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1)
// Space Complexity: O(n)  (indices 는 int 배열이라 entries 대비 작다)
```
## C++ unordered_map의 구조
### 대표코드
```cpp
#include <iostream>
#include <unordered_map>
#include <cassert>

// std::unordered_map: 분리 연쇄법(노드 기반). 표준이 "bucket 인터페이스"와 "참조 안정성"을 요구한다.
//  - rehash 가 일어나도 요소(노드)는 이동하지 않으므로 요소에 대한 포인터/참조는 유효하다 (반복자는 무효화될 수 있다)
//  - 그래서 개방 주소법 기반의 빠른 해시맵(SwissTable 등)은 표준 인터페이스를 그대로 구현할 수 없다
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
    std::cout << "buckets " << buckets0 << " -> " << m.bucket_count() << ", load " << m.load_factor() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1)
// Space Complexity: O(n)  (요소마다 노드 할당)
```
## Redis Dictionary 구조
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// Redis dict: 해시 테이블 2개(ht[0], ht[1]) + 점진적 재해시(incremental rehashing).
// 한 번에 전부 옮기면 큰 테이블에서 서버가 멈추므로, 명령을 처리할 때마다 버킷 1개씩 옮긴다.
// 재해시 중에는 조회가 두 테이블을 모두 보고, 새 키는 ht[1] 에만 넣는다.
class Dict {
    struct Entry { std::string key; int val; Entry* next; };
    struct Table { std::vector<Entry*> t; size_t used = 0; };
    Table ht[2];
    long rehashidx = -1;
    static size_t hash(const std::string& k) { size_t h = 1469598103934665603ULL; for (unsigned char c : k) { h ^= c; h *= 1099511628211ULL; } return h; }
    bool rehashing() const { return rehashidx != -1; }
    void rehashStep() {
        if (!rehashing()) return;
        int emptyVisits = 10;
        while (ht[0].used > 0 && !ht[0].t[rehashidx]) { rehashidx++; if (--emptyVisits == 0) return; }
        if (ht[0].used > 0) {
            Entry* e = ht[0].t[rehashidx];
            while (e) {
                Entry* nx = e->next;
                size_t i = hash(e->key) % ht[1].t.size();
                e->next = ht[1].t[i]; ht[1].t[i] = e;
                ht[0].used--; ht[1].used++;
                e = nx;
            }
            ht[0].t[rehashidx++] = nullptr;
        }
        if (ht[0].used == 0) { ht[0] = std::move(ht[1]); ht[1] = Table(); rehashidx = -1; }   // 재해시 완료: 테이블 교체
    }
    Entry* findIn(int which, const std::string& k) const {
        if (ht[which].t.empty()) return nullptr;
        for (Entry* e = ht[which].t[hash(k) % ht[which].t.size()]; e; e = e->next) if (e->key == k) return e;
        return nullptr;
    }
public:
    Dict() { ht[0].t.assign(4, nullptr); }
    bool wasRehashing = false;
    void set(const std::string& k, int v) {
        rehashStep();
        if (Entry* e = findIn(0, k)) { e->val = v; return; }
        if (Entry* e = findIn(1, k)) { e->val = v; return; }
        if (!rehashing() && ht[0].used >= ht[0].t.size()) {         // 적재율 1 이상이면 2배 이상으로 확장 시작
            size_t n = 4; while (n < ht[0].used * 2) n <<= 1;
            ht[1].t.assign(n, nullptr); rehashidx = 0;
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
    bool isRehashing() const { return rehashing(); }
    size_t size() const { return ht[0].used + ht[1].used; }
    ~Dict() { for (auto& tb : ht) for (Entry* e : tb.t) while (e) { Entry* n = e->next; delete e; e = n; } }
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
    std::cout << "Redis-style dict: incremental rehash finished, size=" << d.size() << std::endl;
    return 0;
}
// Time Complexity: 연산당 O(1) + 재해시 1버킷 분할상환
// Space Complexity: 재해시 중 최대 두 테이블
```
## LRUCache()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <unordered_map>
#include <cassert>

// LRU 캐시: 해시맵(키 -> 리스트 노드) + 이중 연결 리스트(최근 사용 순). get/put 모두 O(1)
class LRUCache {
    size_t cap;
    std::list<std::pair<int, int>> order;                          // 앞 = 가장 최근
    std::unordered_map<int, std::list<std::pair<int, int>>::iterator> pos;
public:
    explicit LRUCache(size_t c) : cap(c) {}
    int get(int k) {
        auto it = pos.find(k);
        if (it == pos.end()) return -1;
        order.splice(order.begin(), order, it->second);            // 맨 앞으로 이동
        return it->second->second;
    }
    void put(int k, int v) {
        auto it = pos.find(k);
        if (it != pos.end()) { it->second->second = v; order.splice(order.begin(), order, it->second); return; }
        if (order.size() == cap) { pos.erase(order.back().first); order.pop_back(); }   // 가장 오래 쓰이지 않은 항목 제거
        order.emplace_front(k, v);
        pos[k] = order.begin();
    }
};

int main() {
    LRUCache c(2);
    c.put(1, 1); c.put(2, 2);
    assert(c.get(1) == 1);
    c.put(3, 3);                                                   // 2 가 퇴출된다
    assert(c.get(2) == -1);
    c.put(4, 4);                                                   // 1 이 퇴출된다
    assert(c.get(1) == -1 && c.get(3) == 3 && c.get(4) == 4);
    std::cout << "LRUCache verified." << std::endl;
    return 0;
}
// Time Complexity: get/put O(1)
// Space Complexity: O(capacity)
```
## LFUCache()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <unordered_map>
#include <cassert>

// LFU 캐시: 가장 적게 사용된 항목을 퇴출하고, 사용 횟수가 같으면 가장 오래된 것을 퇴출한다. 모든 연산 O(1)
// 키 -> (값, 빈도, 리스트 위치),  빈도 -> 키 리스트(최근이 앞),  minFreq 로 퇴출 후보 빈도를 유지
class LFUCache {
    struct Info { int val, freq; std::list<int>::iterator it; };
    size_t cap; int minFreq = 0;
    std::unordered_map<int, Info> kv;
    std::unordered_map<int, std::list<int>> byFreq;
    void touch(int k) {
        Info& in = kv[k];
        byFreq[in.freq].erase(in.it);
        if (byFreq[in.freq].empty()) { byFreq.erase(in.freq); if (minFreq == in.freq) minFreq++; }
        in.freq++;
        byFreq[in.freq].push_front(k);
        in.it = byFreq[in.freq].begin();
    }
public:
    explicit LFUCache(size_t c) : cap(c) {}
    int get(int k) { if (!kv.count(k)) return -1; touch(k); return kv[k].val; }
    void put(int k, int v) {
        if (cap == 0) return;
        if (kv.count(k)) { kv[k].val = v; touch(k); return; }
        if (kv.size() == cap) {                                    // minFreq 리스트의 맨 뒤(가장 오래된 것) 퇴출
            int victim = byFreq[minFreq].back();
            byFreq[minFreq].pop_back();
            if (byFreq[minFreq].empty()) byFreq.erase(minFreq);
            kv.erase(victim);
        }
        minFreq = 1;
        byFreq[1].push_front(k);
        kv[k] = {v, 1, byFreq[1].begin()};
    }
};

int main() {
    LFUCache c(2);
    c.put(1, 1); c.put(2, 2);
    assert(c.get(1) == 1);              // 1 의 빈도 2, 2 의 빈도 1
    c.put(3, 3);                        // 빈도가 낮은 2 퇴출
    assert(c.get(2) == -1 && c.get(3) == 3);
    c.put(4, 4);                        // 1(빈도 2), 3(빈도 2) 중 더 오래된 1 퇴출
    assert(c.get(1) == -1 && c.get(3) == 3 && c.get(4) == 4);
    std::cout << "LFUCache verified." << std::endl;
    return 0;
}
// Time Complexity: get/put O(1)
// Space Complexity: O(capacity)
```
# Part 11. 보안
## HashDoS()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <list>
#include <string>
#include <vector>
#include <cassert>

// 해시 플러딩(HashDoS): 해시 함수와 테이블 크기를 아는 공격자가 같은 버킷에 몰리는 키만 보내 O(1)을 O(n)으로 만든다.
// Java 의 String.hashCode 에서 "Aa" 와 "BB" 는 해시가 같다 (65*31+97 == 66*31+66) -> 두 블록을 이어 붙이면 2^k 개의 충돌 문자열
uint32_t weak(const std::string& s) { uint32_t h = 0; for (unsigned char c : s) h = h * 31 + c; return h; }
uint32_t keyed(const std::string& s, uint64_t secret) {            // 비밀 키가 섞인 해시: 공격자는 충돌을 미리 만들 수 없다
    uint64_t h = secret ^ 1469598103934665603ULL;
    for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; h ^= h >> 29; }
    h *= 0x9e3779b97f4a7c15ULL; return (uint32_t)(h >> 32);
}

template <class H>
size_t maxChain(const std::vector<std::string>& keys, H h, size_t m) {
    std::vector<size_t> len(m, 0);
    for (auto& k : keys) len[h(k) % m]++;
    return *std::max_element(len.begin(), len.end());
}

int main() {
    std::vector<std::string> keys = {""};
    for (int block = 0; block < 10; block++) {                      // 2^10 = 1024 개의 충돌 문자열
        std::vector<std::string> next;
        for (auto& s : keys) { next.push_back(s + "Aa"); next.push_back(s + "BB"); }
        keys.swap(next);
    }
    assert(keys.size() == 1024);
    for (auto& k : keys) assert(weak(k) == weak(keys[0]));           // 전부 같은 해시값
    size_t attacked = maxChain(keys, weak, 1024);
    size_t defended = maxChain(keys, [](const std::string& s) { return keyed(s, 0x1234abcdULL); }, 1024);
    assert(attacked == 1024);                                       // 한 체인에 전부 -> 삽입 n개에 비교 O(n^2)
    assert(defended < 16);                                          // 키 있는 해시는 고르게 퍼진다
    std::cout << "longest chain: weak hash " << attacked << ", keyed hash " << defended << std::endl;
    return 0;
}
// Time Complexity: 공격 시 삽입 n개 O(n^2), 방어 시 O(n)
// Space Complexity: O(n)
```
## Salting()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <cassert>

// 솔트(salt): 사용자마다 다른 무작위 값을 비밀번호와 함께 해시한다.
//  - 솔트가 없으면 같은 비밀번호 = 같은 해시 -> 미리 계산한 표(레인보우 테이블)로 한 번에 깨진다
//  - 솔트가 있으면 사용자별로 표를 따로 만들어야 하므로 사전 계산이 무의미해진다
// (여기서는 구조를 보이려고 장난감 해시를 쓴다. 실제로는 bcrypt/scrypt/Argon2 처럼 느리고 메모리를 쓰는 KDF 를 사용할 것)
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
uint64_t toyHash(const std::string& pw, const std::string& salt, int rounds = 5000) {
    uint64_t h = 0;
    for (unsigned char c : salt + pw) h = mix(h ^ c);
    for (int i = 0; i < rounds; i++) h = mix(h + i);               // 반복으로 계산 비용을 키운다 (key stretching)
    return h;
}
bool constantTimeEq(uint64_t a, uint64_t b) { uint64_t d = a ^ b; uint64_t acc = 0; for (int i = 0; i < 64; i++) acc |= (d >> i) & 1; return acc == 0; }   // 비교 시간이 값에 의존하지 않게

int main() {
    const char* dictionary[] = {"123456", "password", "qwerty", "letmein", "dragon"};
    std::unordered_map<uint64_t, std::string> rainbow;              // 솔트 없는 해시 -> 비밀번호 사전 계산 표
    for (auto pw : dictionary) rainbow[toyHash(pw, "")] = pw;

    // 솔트 없는 저장: 두 사용자의 해시가 같아 사전 표 한 번으로 둘 다 노출
    uint64_t aliceNoSalt = toyHash("letmein", ""), bobNoSalt = toyHash("letmein", "");
    assert(aliceNoSalt == bobNoSalt && rainbow.count(aliceNoSalt) && rainbow[aliceNoSalt] == "letmein");

    // 솔트 있는 저장: 같은 비밀번호라도 해시가 다르고, 사전 계산 표로는 찾을 수 없다
    uint64_t aliceSalted = toyHash("letmein", "k3Fq9aZ1"), bobSalted = toyHash("letmein", "x8Lm2PqW");
    assert(aliceSalted != bobSalted);
    assert(!rainbow.count(aliceSalted) && !rainbow.count(bobSalted));
    assert(constantTimeEq(aliceSalted, toyHash("letmein", "k3Fq9aZ1")));      // 검증은 같은 솔트로 다시 계산
    assert(!constantTimeEq(aliceSalted, toyHash("wrong", "k3Fq9aZ1")));
    std::cout << "salted hashes differ: " << std::hex << aliceSalted << " vs " << bobSalted << std::endl;
    return 0;
}
// Time Complexity: O(rounds)  (비용을 의도적으로 키움)
// Space Complexity: O(1)
```
# Part 12. 동시성
## ConcurrentHashMap()
### 대표코드
```cpp
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>
#include <cassert>

// 락 스트라이핑: 테이블 전체에 락 하나를 두면 직렬화되므로 해시로 나눈 구역(shard)마다 락을 둔다.
// 서로 다른 구역에 접근하는 스레드는 서로 기다리지 않는다
class ConcurrentMap {
    static const int SHARDS = 16;
    struct Shard { std::mutex mu; std::unordered_map<std::string, long> m; };
    Shard shard[SHARDS];
    Shard& pick(const std::string& k) { return shard[std::hash<std::string>{}(k) % SHARDS]; }
public:
    void add(const std::string& k, long delta) { Shard& s = pick(k); std::lock_guard<std::mutex> g(s.mu); s.m[k] += delta; }   // 원자적 갱신
    long get(const std::string& k) { Shard& s = pick(k); std::lock_guard<std::mutex> g(s.mu); auto it = s.m.find(k); return it == s.m.end() ? 0 : it->second; }
    size_t size() { size_t n = 0; for (auto& s : shard) { std::lock_guard<std::mutex> g(s.mu); n += s.m.size(); } return n; }
};

int main() {
    ConcurrentMap cm;
    const int T = 8, N = 5000;
    std::vector<std::thread> th;
    for (int t = 0; t < T; t++)
        th.emplace_back([&, t] {
            for (int i = 0; i < N; i++) {
                cm.add("shared", 1);                                // 모든 스레드가 같은 키를 갱신
                cm.add("own" + std::to_string(t) + "_" + std::to_string(i), 1);
            }
        });
    for (auto& x : th) x.join();
    assert(cm.get("shared") == (long)T * N);                        // 갱신 손실 없음
    assert(cm.size() == (size_t)T * N + 1);
    std::cout << "ConcurrentMap shared=" << cm.get("shared") << " size=" << cm.size() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1) (구역 간 병렬)
// Space Complexity: O(n)
```
## LockFreeHashTable()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <cstdint>
#include <thread>
#include <vector>
#include <cassert>

// 고정 크기 락프리 해시 테이블(삽입·조회): 키 칸을 CAS 로 차지한다. 0 은 빈 칸 표식이므로 키·값은 0 이 아니어야 한다.
// 삭제와 크기 조정은 어렵다 (실제 구현은 묘비 + 협력적 마이그레이션, Cliff Click 의 설계 참고)
class LockFreeTable {
    static const size_t CAP = 1 << 16;
    std::atomic<uint64_t> keys[CAP], vals[CAP];
    static size_t slot(uint64_t k) { k ^= k >> 33; k *= 0xff51afd7ed558ccdULL; k ^= k >> 33; return k % CAP; }
public:
    LockFreeTable() { for (size_t i = 0; i < CAP; i++) { keys[i] = 0; vals[i] = 0; } }
    bool put(uint64_t k, uint64_t v) {
        for (size_t i = slot(k), n = 0; n < CAP; i = (i + 1) % CAP, n++) {
            uint64_t cur = keys[i].load(std::memory_order_acquire);
            if (cur == 0 && keys[i].compare_exchange_strong(cur, k)) { vals[i].store(v, std::memory_order_release); return true; }
            if (cur == k) { vals[i].store(v, std::memory_order_release); return true; }   // 다른 스레드가 같은 키를 먼저 차지한 경우 포함
        }
        return false;                                                // 가득 참
    }
    bool get(uint64_t k, uint64_t& v) const {
        for (size_t i = slot(k), n = 0; n < CAP; i = (i + 1) % CAP, n++) {
            uint64_t cur = keys[i].load(std::memory_order_acquire);
            if (cur == 0) return false;
            if (cur == k) { v = vals[i].load(std::memory_order_acquire); return v != 0; }
        }
        return false;
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
    assert(!t.get(999999999, v));
    std::cout << "LockFreeTable: " << T * N << " concurrent inserts verified" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 락 없이 진행 보장(lock-free)
// Space Complexity: O(고정 용량)
```
# Part 13. 확률적 구조
## BloomFilter()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// 블룸 필터(해시 관점의 요약, 정본은 AdvancedDataStructures.md Part 3): 비트 배열 m 개와 해시 k 개.
// 이중 해싱 h_i = h1 + i·h2 로 k 개의 위치를 만든다.  "없다"는 확실하고 "있다"는 틀릴 수 있다 (거짓 양성)
class Bloom {
    std::vector<bool> bits; int k;
    static uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
    static uint64_t base(const std::string& s) { uint64_t h = 1469598103934665603ULL; for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; } return h; }
public:
    Bloom(size_t m, int hashes) : bits(m), k(hashes) {}
    void add(const std::string& s) { uint64_t h1 = mix(base(s)), h2 = mix(h1) | 1; for (int i = 0; i < k; i++) bits[(h1 + i * h2) % bits.size()] = true; }
    bool mayContain(const std::string& s) const {
        uint64_t h1 = mix(base(s)), h2 = mix(h1) | 1;
        for (int i = 0; i < k; i++) if (!bits[(h1 + i * h2) % bits.size()]) return false;
        return true;
    }
};

int main() {
    const int n = 10000;
    Bloom f(10 * n, 7);                                           // 원소당 10비트, 해시 7개 -> 이론 오탐률 약 0.8%
    for (int i = 0; i < n; i++) f.add("member" + std::to_string(i));
    for (int i = 0; i < n; i++) assert(f.mayContain("member" + std::to_string(i)));     // 거짓 음성은 없다
    int fp = 0;
    for (int i = 0; i < n; i++) if (f.mayContain("other" + std::to_string(i))) fp++;
    assert(fp < n * 3 / 100);
    std::cout << "false positive rate: " << 100.0 * fp / n << "% (theory ~0.8%)" << std::endl;
    return 0;
}
// Time Complexity: add / mayContain O(k)
// Space Complexity: O(m) 비트
```
## CountMinSketch()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// Count-Min Sketch(정본은 AdvancedDataStructures.md Part 3): 빈도 추정. d 행 × w 열의 카운터, 행마다 다른 해시.
// 추정값 = 행별 카운터의 최솟값 -> 항상 실제 이상 (과대 추정만 한다).  w = ceil(e/ε), d = ceil(ln(1/δ)) 이면
// 확률 1-δ 로 오차가 ε·N 이하
class CMS {
    size_t w, d; std::vector<std::vector<uint32_t>> c;
    static uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
    size_t idx(uint64_t key, size_t row) const { return mix(key + 0x9e3779b97f4a7c15ULL * (row + 1)) % w; }
public:
    CMS(double eps, double delta) : w((size_t)std::ceil(std::exp(1.0) / eps)), d((size_t)std::ceil(std::log(1.0 / delta))), c(d, std::vector<uint32_t>(w, 0)) {}
    void add(uint64_t key, uint32_t n = 1) { for (size_t r = 0; r < d; r++) c[r][idx(key, r)] += n; }
    uint32_t estimate(uint64_t key) const { uint32_t m = UINT32_MAX; for (size_t r = 0; r < d; r++) m = std::min(m, c[r][idx(key, r)]); return m; }
};

int main() {
    CMS cms(0.01, 0.01);
    std::unordered_map<uint64_t, uint32_t> truth;
    uint64_t N = 0;
    for (uint64_t k = 1; k <= 2000; k++) {                         // 빈도가 1/k 에 비례하는 치우친 분포
        uint32_t freq = 20000 / k + 1;
        cms.add(k, freq); truth[k] = freq; N += freq;
    }
    int within = 0;
    for (auto& kv : truth) {
        uint32_t est = cms.estimate(kv.first);
        assert(est >= kv.second);                                  // 과소 추정은 없다
        if (est - kv.second <= 0.01 * N) within++;
    }
    assert(within >= 0.99 * truth.size());                         // 99% 이상이 오차 ε·N 이내
    std::cout << "CountMinSketch: " << within << "/" << truth.size() << " estimates within eps*N" << std::endl;
    return 0;
}
// Time Complexity: add / estimate O(d)
// Space Complexity: O(d·w)
```
## Bloom Filter는 왜 오탐(False Positive)만 발생하는가?
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <cassert>

// 이유: 비트는 0 -> 1 로만 바뀐다. 한 원소를 넣으면 그 원소의 k 개 비트가 반드시 1 이 되고 이후 아무도 0 으로 되돌리지 않으므로
//       "넣은 원소는 항상 있다고 답한다" (거짓 음성 없음).  반면 다른 원소들이 우연히 모든 k 개 비트를 1 로 만들어 놓았다면 오탐이 생긴다.
// 삭제하려고 비트를 0 으로 내리면 이 불변식이 깨져 다른 원소가 거짓 음성이 된다 -> 카운팅 블룸 필터(비트 대신 카운터)가 필요한 이유
struct Filter {
    std::vector<uint8_t> cnt; int k; bool counting;
    Filter(size_t m, int hashes, bool c) : cnt(m, 0), k(hashes), counting(c) {}
    size_t pos(const std::string& s, int i) const { uint64_t h = 1469598103934665603ULL ^ (i * 0x9e3779b97f4a7c15ULL); for (unsigned char ch : s) { h ^= ch; h *= 1099511628211ULL; h ^= h >> 29; } return h % cnt.size(); }
    void add(const std::string& s) { for (int i = 0; i < k; i++) { size_t p = pos(s, i); if (counting) cnt[p]++; else cnt[p] = 1; } }
    bool has(const std::string& s) const { for (int i = 0; i < k; i++) if (!cnt[pos(s, i)]) return false; return true; }
    void remove(const std::string& s) { for (int i = 0; i < k; i++) { size_t p = pos(s, i); if (counting) cnt[p]--; else cnt[p] = 0; } }
};

int main() {
    const int n = 300;
    // (1) 일반 블룸 필터: 삭제 없이 쓰면 거짓 음성이 절대 없다
    Filter plain(2000, 4, false);
    for (int i = 0; i < n; i++) plain.add("m" + std::to_string(i));
    for (int i = 0; i < n; i++) assert(plain.has("m" + std::to_string(i)));
    // (2) 일반 필터에서 비트를 내려 삭제하면 다른 원소가 거짓 음성으로 바뀐다
    Filter broken(200, 4, false);                                   // 작게 만들어 비트 공유를 늘린다
    for (int i = 0; i < 60; i++) broken.add("m" + std::to_string(i));
    for (int i = 0; i < 30; i++) broken.remove("m" + std::to_string(i));
    int falseNeg = 0;
    for (int i = 30; i < 60; i++) if (!broken.has("m" + std::to_string(i))) falseNeg++;
    assert(falseNeg > 0);
    // (3) 카운팅 필터: 같은 상황에서도 남은 원소는 모두 보존된다
    Filter counting(200, 4, true);
    for (int i = 0; i < 60; i++) counting.add("m" + std::to_string(i));
    for (int i = 0; i < 30; i++) counting.remove("m" + std::to_string(i));
    for (int i = 30; i < 60; i++) assert(counting.has("m" + std::to_string(i)));
    std::cout << "plain delete created " << falseNeg << " false negatives; counting filter created 0" << std::endl;
    return 0;
}
// Time Complexity: add / has / remove O(k)
// Space Complexity: O(m)
```
# Part 14. 유사도 해시
## LocalitySensitiveHashing()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>
#include <cassert>

// LSH(Jaccard 용): 문서를 3-gram 집합으로 보고 MinHash 서명을 만든 뒤, 서명을 b 개의 밴드(r 행씩)로 나눈다.
// 한 밴드라도 완전히 같으면 "후보 쌍".  유사도 s 인 쌍이 후보가 될 확률 = 1 - (1 - s^r)^b  (S자 곡선)
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
std::set<uint64_t> shingles(const std::string& s) {
    std::set<uint64_t> r;
    for (size_t i = 0; i + 3 <= s.size(); i++) { uint64_t h = 0; for (int j = 0; j < 3; j++) h = h * 257 + (unsigned char)s[i + j]; r.insert(h); }
    return r;
}
const int BANDS = 20, ROWS = 5;
std::vector<uint64_t> signature(const std::set<uint64_t>& sh) {
    std::vector<uint64_t> sig(BANDS * ROWS, UINT64_MAX);
    for (uint64_t x : sh) for (int i = 0; i < BANDS * ROWS; i++) sig[i] = std::min(sig[i], mix(x ^ (0x9e3779b97f4a7c15ULL * (i + 1))));
    return sig;
}
bool candidate(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b) {
    for (int band = 0; band < BANDS; band++) {
        bool same = true;
        for (int r = 0; r < ROWS; r++) if (a[band * ROWS + r] != b[band * ROWS + r]) { same = false; break; }
        if (same) return true;                                     // 실제 구현은 밴드 키를 해시 테이블 버킷으로 써서 O(n) 에 후보를 모은다
    }
    return false;
}

int main() {
    auto A  = signature(shingles("the quick brown fox jumps over the lazy dog near the river bank"));
    auto A2 = signature(shingles("the quick brown fox jumps over the lazy dog near the river side"));
    auto B  = signature(shingles("completely unrelated text about quantum chromodynamics and gluon fields"));
    assert(candidate(A, A2));                                      // 유사한 문서는 후보가 된다
    assert(!candidate(A, B));                                      // 무관한 문서는 후보가 되지 않는다
    std::cout << "LSH candidates: (A,A') yes, (A,B) no" << std::endl;
    return 0;
}
// Time Complexity: 서명 O(|문서|·H), 후보 탐색 평균 O(n)
// Space Complexity: O(n·H)
```
## SimHash()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <sstream>
#include <string>
#include <cassert>

// SimHash: 단어마다 64비트 해시를 만들어 비트별로 +1/-1 을 누적하고 부호로 64비트 지문을 만든다.
// 비슷한 문서는 지문의 해밍 거리가 작다 (구글의 중복 웹페이지 탐지에 쓰인 방식)
uint64_t fnv64(const std::string& s) {
    uint64_t h = 14695981039346656037ULL;
    for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; }
    h ^= h >> 32; h *= 0x9e3779b97f4a7c15ULL; h ^= h >> 29;        // 비트가 고르게 섞이도록 마무리
    return h;
}
uint64_t simhash(const std::string& doc) {
    int v[64] = {0};
    std::istringstream in(doc); std::string w;
    while (in >> w) { uint64_t h = fnv64(w); for (int i = 0; i < 64; i++) v[i] += (h >> i & 1) ? 1 : -1; }
    uint64_t f = 0;
    for (int i = 0; i < 64; i++) if (v[i] > 0) f |= 1ULL << i;
    return f;
}
int hamming(uint64_t a, uint64_t b) { return __builtin_popcountll(a ^ b); }

int main() {
    uint64_t d1 = simhash("the quick brown fox jumps over the lazy dog and runs into the forest near the old river");
    uint64_t d2 = simhash("the quick brown fox jumped over the lazy dog and runs into the forest near the old river");
    uint64_t d3 = simhash("stock markets rallied sharply after the central bank unexpectedly cut interest rates on friday");
    int near = hamming(d1, d2), far = hamming(d1, d3);
    assert(near < far);
    assert(near <= 20);
    std::cout << "hamming(similar)=" << near << " hamming(different)=" << far << std::endl;
    return 0;
}
// Time Complexity: O(단어 수 · 64)
// Space Complexity: O(1)
```
## MinHash()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <set>
#include <vector>
#include <cassert>

// MinHash: 무작위 순열(해시) h 아래에서 두 집합의 최소 원소가 같을 확률 = Jaccard(A, B).
// 해시 K 개의 서명에서 "같은 칸의 비율"이 Jaccard 의 불편 추정량이다 (표준오차 ≈ sqrt(J(1-J)/K))
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
std::vector<uint64_t> minhash(const std::set<int>& s, int K) {
    std::vector<uint64_t> sig(K, UINT64_MAX);
    for (int x : s) for (int i = 0; i < K; i++) sig[i] = std::min(sig[i], mix((uint64_t)x * 0x9e3779b97f4a7c15ULL + i * 0xbf58476d1ce4e5b9ULL));
    return sig;
}
double estimate(const std::vector<uint64_t>& a, const std::vector<uint64_t>& b) {
    int same = 0; for (size_t i = 0; i < a.size(); i++) same += (a[i] == b[i]);
    return double(same) / a.size();
}

int main() {
    std::set<int> A, B;
    for (int i = 0; i < 100; i++) A.insert(i);
    for (int i = 50; i < 150; i++) B.insert(i);                    // 교집합 50, 합집합 150 -> J = 1/3
    double truth = 50.0 / 150.0;
    double est = estimate(minhash(A, 256), minhash(B, 256));
    assert(std::fabs(est - truth) < 0.1);
    assert(estimate(minhash(A, 256), minhash(A, 256)) == 1.0);     // 같은 집합은 서명도 같다
    std::cout << "true Jaccard " << truth << ", MinHash estimate " << est << std::endl;
    return 0;
}
// Time Complexity: O(|S|·K)
// Space Complexity: O(K)
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
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// SwissTable(Abseil flat_hash_map, Rust hashbrown): 개방 주소법 + 제어 바이트.
// 슬롯 16개를 한 그룹으로 묶고, 그룹마다 제어 바이트 16개(빈 칸/삭제/해시 하위 7비트 H2)를 둔다.
// 조회는 H2 가 같은 칸만 키를 비교하므로 캐시 미스와 키 비교가 크게 줄고, 실제 구현은 SSE2/NEON 한 명령으로 16칸을 동시에 검사한다.
// (여기서는 이식성을 위해 스칼라 루프로 같은 로직을 구현)
class Swiss {
    static constexpr uint8_t EMPTY = 0x80, DELETED = 0xFE;
    static constexpr size_t G = 16;
    std::vector<uint8_t> ctrl; std::vector<uint64_t> key, val;
    size_t groups, count = 0, tomb = 0;
    static uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
    void init(size_t g) { groups = g; ctrl.assign(g * G, EMPTY); key.assign(g * G, 0); val.assign(g * G, 0); count = tomb = 0; }
    long findSlot(uint64_t k) const {
        uint64_t h = mix(k); uint8_t h2 = h & 0x7f;
        size_t g = (h >> 7) % groups;
        for (size_t step = 1; step <= groups; step++) {
            bool sawEmpty = false;
            for (size_t j = 0; j < G; j++) {
                size_t s = g * G + j;
                if (ctrl[s] == h2 && key[s] == k) return (long)s;   // H2 가 같을 때만 실제 키를 비교
                if (ctrl[s] == EMPTY) sawEmpty = true;
            }
            if (sawEmpty) return -1;                                // 빈 칸이 있는 그룹에서 끝난다
            g = (g + step) % groups;                                 // 삼각수 간격으로 그룹 이동
        }
        return -1;
    }
    void grow() {
        std::vector<uint64_t> k2, v2;
        for (size_t s = 0; s < ctrl.size(); s++) if (!(ctrl[s] & 0x80)) { k2.push_back(key[s]); v2.push_back(val[s]); }
        init(groups * 2);
        for (size_t i = 0; i < k2.size(); i++) put(k2[i], v2[i]);
    }
public:
    Swiss() { init(1); }
    void put(uint64_t k, uint64_t v) {
        long f = findSlot(k);
        if (f >= 0) { val[f] = v; return; }
        if ((count + tomb + 1) * 8 > ctrl.size() * 7) grow();     // 적재율 7/8 초과 시 확장
        uint64_t h = mix(k); size_t g = (h >> 7) % groups;
        for (size_t step = 1;; step++) {
            for (size_t j = 0; j < G; j++) {
                size_t s = g * G + j;
                if (ctrl[s] == EMPTY || ctrl[s] == DELETED) {
                    if (ctrl[s] == DELETED) tomb--;
                    ctrl[s] = h & 0x7f; key[s] = k; val[s] = v; count++; return;
                }
            }
            g = (g + step) % groups;
        }
    }
    bool get(uint64_t k, uint64_t& v) const { long s = findSlot(k); if (s < 0) return false; v = val[s]; return true; }
    bool erase(uint64_t k) { long s = findSlot(k); if (s < 0) return false; ctrl[s] = DELETED; count--; tomb++; return true; }
    size_t size() const { return count; }
    size_t capacity() const { return ctrl.size(); }
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
    assert(double(t.size()) / t.capacity() <= 7.0 / 8.0);
    std::cout << "SwissTable size=" << t.size() << " capacity=" << t.capacity() << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1), 그룹 단위 병렬 비교
// Space Complexity: O(n)  (슬롯당 제어 바이트 1개)
```
## LearnedHash()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <set>
#include <vector>
#include <cassert>

// 학습된 해시(Learned Index 의 아이디어): 키의 누적분포(CDF)를 모델로 학습하면 h(k) = CDF(k) · m 이
// 키를 슬롯에 거의 균등·단조하게 펼쳐 놓는다 -> 무작위 해시의 충돌(약 37%)보다 훨씬 적게 충돌한다.
// 여기서는 정렬된 키에서 32개마다 표본을 뽑아 구간별 선형 보간으로 CDF 를 근사한다.
struct Model {
    std::vector<double> sx, sy; size_t n;
    Model(const std::vector<double>& sorted) : n(sorted.size()) {
        for (size_t i = 0; i < sorted.size(); i += 32) { sx.push_back(sorted[i]); sy.push_back((double)i); }
        sx.push_back(sorted.back()); sy.push_back((double)sorted.size() - 1);
    }
    size_t slot(double k, size_t m) const {
        size_t j = std::upper_bound(sx.begin(), sx.end(), k) - sx.begin();
        if (j == 0) return 0;
        if (j >= sx.size()) return m - 1;
        double t = (k - sx[j - 1]) / (sx[j] - sx[j - 1]);
        double rank = sy[j - 1] + t * (sy[j] - sy[j - 1]);
        return std::min<size_t>(m - 1, (size_t)(rank / n * m));
    }
};
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }

int main() {
    const size_t n = 10000, m = n;                                  // 적재율 1
    std::vector<double> keys;
    for (size_t i = 1; i <= n; i++) keys.push_back(std::floor(1000.0 * std::pow((double)i, 1.5)));   // 간격이 점점 벌어지는 치우친 분포
    Model model(keys);
    std::set<size_t> learnedSlots, randomSlots;
    for (double k : keys) { learnedSlots.insert(model.slot(k, m)); randomSlots.insert(mix((uint64_t)k) % m); }
    size_t learnedCollisions = n - learnedSlots.size(), randomCollisions = n - randomSlots.size();
    assert(learnedCollisions * 3 < randomCollisions);               // 학습된 해시가 충돌이 훨씬 적다
    std::cout << "collisions: learned " << learnedCollisions << ", random " << randomCollisions << " (of " << n << ")" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(log S) (S = 표본 수), 상수 시간 모델로 대체 가능
// Space Complexity: O(n/32)
```
# Part 16. 해시 성능 시각화
## CollisionVisualization()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 12개의 키를 버킷 8개에 넣고 충돌을 그림으로 본다. ■ 가 첫 원소, ▲ 는 충돌한 추가 원소
size_t fnv(const std::string& s) { size_t h = 1469598103934665603ULL; for (unsigned char c : s) { h ^= c; h *= 1099511628211ULL; } return h; }

int main() {
    const char* words[] = {"apple", "banana", "cherry", "date", "elder", "fig", "grape", "honey", "iris", "jade", "kiwi", "lemon"};
    std::vector<std::vector<std::string>> bucket(8);
    for (auto w : words) bucket[fnv(w) % 8].push_back(w);
    size_t collisions = 0, used = 0;
    for (size_t i = 0; i < bucket.size(); i++) {
        std::cout << "[" << i << "] ";
        for (size_t j = 0; j < bucket[i].size(); j++) std::cout << (j == 0 ? "■ " : "▲ ") << bucket[i][j] << "  ";
        std::cout << "\n";
        if (!bucket[i].empty()) { used++; collisions += bucket[i].size() - 1; }
    }
    assert(collisions == 12 - used);                               // 충돌 수 = 키 수 - 사용된 버킷 수
    assert(collisions >= 4);                                       // 12개를 8칸에 넣으면 비둘기집 원리로 최소 4번 충돌
    std::cout << "keys=12 buckets=8 used=" << used << " collisions=" << collisions << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
## BucketDistribution()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cstdint>
#include <cassert>

// 좋은 해시와 나쁜 해시의 버킷 분포를 히스토그램과 카이제곱 통계로 비교한다.
// 균등하면 χ² ≈ 자유도(m-1) 근처, 치우치면 훨씬 커진다
uint64_t mix(uint64_t x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; return x ^ (x >> 33); }
double chiSquare(const std::vector<int>& c, int n) {
    double e = double(n) / c.size(), s = 0;
    for (int x : c) s += (x - e) * (x - e) / e;
    return s;
}
void bars(const char* name, const std::vector<int>& c) {
    std::cout << name << "\n";
    for (size_t i = 0; i < c.size(); i += 8) { int sum = 0; for (size_t j = i; j < i + 8; j++) sum += c[j]; std::cout << "  [" << i << ".." << i + 7 << "] " << std::string(sum / 40, '#') << " " << sum << "\n"; }
}

int main() {
    const int m = 64, n = 10000;
    std::vector<int> good(m, 0), bad(m, 0);
    for (int i = 0; i < n; i++) {
        uint64_t key = (uint64_t)i * 8;                            // 8의 배수 키
        good[mix(key) % m]++;
        bad[key % m]++;                                            // 단순 나머지: m=64 와 8의 배수가 겹쳐 8개 버킷만 쓰인다
    }
    bars("good hash", good); bars("bad hash (k mod 64, keys multiple of 8)", bad);
    double cg = chiSquare(good, n), cb = chiSquare(bad, n);
    assert(cg < 110);                                              // 자유도 63 의 99.9% 분위수 근처 이내
    assert(cb > 1000);
    std::cout << "chi-square: good=" << cg << " bad=" << cb << std::endl;
    return 0;
}
// Time Complexity: O(n + m)
// Space Complexity: O(m)
```
## ProbeSequence()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 같은 키(홈=3, m=11)의 탐사 순서를 세 방식으로 나란히 본다.
typedef std::vector<unsigned> Seq;
Seq linear(unsigned h, unsigned m)    { Seq s; for (unsigned i = 0; i < m; i++) s.push_back((h + i) % m); return s; }
Seq quadratic(unsigned h, unsigned m) { Seq s; for (unsigned i = 0; i < m; i++) s.push_back((h + i * i) % m); return s; }
Seq doubleHash(unsigned h, unsigned h2, unsigned m) { Seq s; for (unsigned i = 0; i < m; i++) s.push_back((h + i * h2) % m); return s; }
void show(const char* name, const Seq& s) { std::cout << name << ": "; for (size_t i = 0; i < s.size(); i++) std::cout << s[i] << (i + 1 < s.size() ? " -> " : "\n"); }

int main() {
    const unsigned m = 11, home = 3, step = 4;                     // 이중 해싱의 보폭 h2 = 4
    Seq a = linear(home, m), b = quadratic(home, m), c = doubleHash(home, step, m);
    show("linear   ", a); show("quadratic", b); show("double   ", c);
    assert(a[0] == home && b[0] == home && c[0] == home);          // 모두 홈에서 출발
    assert(std::set<unsigned>(a.begin(), a.end()).size() == m);     // 선형은 전 칸 방문
    assert(std::set<unsigned>(c.begin(), c.end()).size() == m);     // m 이 소수면 이중 해싱도 전 칸 방문
    assert(std::set<unsigned>(b.begin(), b.end()).size() < m);      // i^2 는 일부 칸을 놓친다 (m=11 -> 6칸만)
    std::cout << "distinct slots: linear=" << m << " quadratic=" << std::set<unsigned>(b.begin(), b.end()).size() << " double=" << m << std::endl;
    return 0;
}
// Time Complexity: O(m)
// Space Complexity: O(m)
```
## ResizeAnimation()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 체이닝 테이블이 확장되는 순간을 프레임별로 출력한다 (적재율 0.75 초과 시 버킷 2배)
int main() {
    std::vector<std::vector<int>> b(2);
    size_t n = 0, frame = 0, resizes = 0;
    auto draw = [&](const char* why) {
        std::cout << "frame " << frame++ << " (" << why << ", n=" << n << ", m=" << b.size() << ")\n";
        for (size_t i = 0; i < b.size(); i++) { std::cout << "  [" << i << "]"; for (int k : b[i]) std::cout << " " << k; std::cout << "\n"; }
    };
    draw("empty");
    for (int k : {10, 21, 32, 43, 54, 65}) {
        if (double(n + 1) / b.size() > 0.75) {                    // 확장: 모든 키를 새 크기로 재배치
            std::vector<std::vector<int>> nb(b.size() * 2);
            for (auto& chain : b) for (int x : chain) nb[x % nb.size()].push_back(x);
            b.swap(nb); resizes++;
            draw("resized");
        }
        b[k % b.size()].push_back(k); n++;
        draw(("insert " + std::to_string(k)).c_str());
    }
    assert(b.size() == 8 && resizes == 2);                         // 2 -> 4 -> 8
    size_t total = 0; for (auto& c : b) total += c.size();
    assert(total == 6 && double(n) / b.size() <= 0.75);
    return 0;
}
// Time Complexity: 확장 1회 O(n), 삽입당 분할상환 O(1)
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
#include <iostream>
#include <cstdint>
#include <iomanip>
#include <string>
#include <cassert>

// 눈사태 효과: 입력 1비트를 뒤집으면 출력 비트의 절반(50%)이 뒤집혀야 좋은 해시다. 입력 비트 × 출력 비트 격자로 본다
uint32_t fnvInt(uint32_t x) { uint32_t h = 2166136261u; for (int i = 0; i < 4; i++) { h ^= (x >> (8 * i)) & 0xff; h *= 16777619u; } return h; }
uint32_t fmix(uint32_t h) { h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16; return h; }
uint32_t identity(uint32_t x) { return x; }

template <class F>
double avalanche(F f, const char* name) {
    double flipsTotal = 0; int samples = 0;
    std::cout << name << " : 입력 비트 i 를 뒤집을 때 출력 비트가 바뀐 평균 비율 (행: 입력 비트 0..31, 8개씩 묶음)\n  ";
    for (int bit = 0; bit < 32; bit++) {
        double flips = 0;
        for (uint32_t x = 1; x <= 400; x++) { flips += __builtin_popcount(f(x * 2654435761u) ^ f((x * 2654435761u) ^ (1u << bit))); samples++; }
        flipsTotal += flips;
        std::cout << std::fixed << std::setprecision(2) << flips / 400 / 32 << (bit % 8 == 7 ? "\n  " : " ");
    }
    std::cout << "\n";
    return flipsTotal / samples / 32;
}

int main() {
    double a_id = avalanche(identity, "identity"), a_fnv = avalanche(fnvInt, "fnv1a(4byte)"), a_mur = avalanche(fmix, "murmur fmix32");
    assert(a_id < 0.05);                                           // 항등 함수: 정확히 1비트만 바뀜 (1/32)
    assert(a_mur > 0.45 && a_mur < 0.55);                          // 이상적인 50%
    assert(a_mur > a_fnv);                                         // FNV 는 눈사태가 약하다
    std::cout << "avalanche ratio: identity=" << a_id << " fnv=" << a_fnv << " murmur=" << a_mur << std::endl;
    return 0;
}
// Time Complexity: O(입력비트 · 표본)
// Space Complexity: O(1)
```
## HashQualityEvaluation()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <iomanip>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 해시 함수 품질을 한 표로 평가한다: (1) 균등도 χ²/자유도  (2) 충돌 수  (3) 눈사태 비율
// 두 개의 키 집합 — 연속 정수, 64씩 증가하는 정수 — 에서 비교
uint32_t fnvInt(uint32_t x) { uint32_t h = 2166136261u; for (int i = 0; i < 4; i++) { h ^= (x >> (8 * i)) & 0xff; h *= 16777619u; } return h; }
uint32_t fmix(uint32_t h) { h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16; return h; }
uint32_t mulShift(uint32_t x) { return x * 2654435769u; }          // Knuth 곱셈법 (상위 비트가 좋다)
uint32_t modOnly(uint32_t x) { return x; }                         // h(k) = k, 이후 % m

struct Result { double chi; size_t collisions; double aval; };
template <class F> Result evaluate(F f, uint32_t stride, uint32_t m = 1024, uint32_t n = 20000) {
    std::vector<int> c(m, 0); std::set<uint32_t> distinct;   // 버킷 = h % m (가장 단순한 선택, 하위 비트 사용)
    for (uint32_t i = 0; i < n; i++) { uint32_t h = f(i * stride); c[h % m]++; distinct.insert(h); }
    double e = double(n) / m, chi = 0; for (int x : c) chi += (x - e) * (x - e) / e;
    double flips = 0; int s = 0;
    for (uint32_t x = 1; x <= 300; x++) for (int b = 0; b < 32; b++) { flips += __builtin_popcount(f(x * stride) ^ f((x * stride) ^ (1u << b))); s++; }
    return {chi / (m - 1), n - distinct.size(), flips / s / 32};
}

int main() {
    struct { const char* name; Result r1, r64; } rows[] = {
        {"identity", evaluate(modOnly, 1), evaluate(modOnly, 64)},
        {"mul-shift", evaluate(mulShift, 1), evaluate(mulShift, 64)},
        {"fnv1a", evaluate(fnvInt, 1), evaluate(fnvInt, 64)},
        {"murmur-fmix", evaluate(fmix, 1), evaluate(fmix, 64)},
    };
    std::cout << std::left << std::setw(12) << "hash" << "  chi2/df(stride1) chi2/df(stride64) avalanche\n";
    for (auto& r : rows)
        std::cout << std::setw(12) << r.name << "  " << std::setw(16) << std::setprecision(3) << r.r1.chi << " " << std::setw(16) << r.r64.chi << " " << r.r1.aval << "\n";
    assert(rows[0].r64.chi > 10);                                  // 항등 해시 + 64 간격 키는 버킷 몇 개에 몰린다
    assert(rows[1].r64.chi > 10);                                  // 곱셈 해시도 하위 비트만 쓰면 같은 문제 -> 상위 비트를 써야 한다
    assert(rows[3].r1.chi < 1.5 && rows[3].r64.chi < 1.5);         // 마무리 섞기를 거친 해시는 어떤 키 패턴에도 균등
    assert(rows[3].r1.aval > 0.45 && rows[3].r1.aval < 0.55);
    return 0;
}
// Time Complexity: O(n + 표본)
// Space Complexity: O(m + n)
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
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <cassert>

// 해시 테이블 구조별 메모리 배치: 체이닝 노드, 개방 주소 슬롯, 패딩이 낭비되는 순서, SwissTable 그룹
struct ChainNode { int32_t key; int32_t val; ChainNode* next; };  // 8 + 포인터 8 = 16B (+ 할당기 헤더는 별도)
struct OpenSlot  { int32_t key; int32_t val; };                    // 8B: 라인당 8개
struct BadOrder  { char flag; int64_t value; char tag; };          // 정렬 때문에 패딩이 끼어 24B
struct GoodOrder { int64_t value; char flag; char tag; };          // 큰 멤버부터 두면 16B
struct SwissGroup { uint8_t ctrl[16]; int32_t keys[16]; int32_t vals[16]; };   // 제어 바이트 16B + 키·값

void dump(const char* name, size_t size, size_t align) { std::cout << name << ": size=" << size << " align=" << align << "\n"; }

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
    std::cout << "padding wasted by BadOrder: " << sizeof(BadOrder) - sizeof(GoodOrder) << " bytes per object" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
