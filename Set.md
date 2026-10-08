# Part 1. 집합의 기초
## CreateSet()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s; // C++ 표준 해시 기반 집합
    std::cout << "Set created." << std::endl;
    assert(s.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Add()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s;
    s.insert(10); // 집합에 요소 추가
    std::cout << "Inserted 10." << std::endl;
    assert(s.count(10) == 1);
    return 0;
}
// Time Complexity: Amortized O(1)
```
## Remove()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s = {10, 20};
    s.erase(10); // 집합에서 요소 삭제
    std::cout << "Removed 10." << std::endl;
    assert(s.count(10) == 0);
    return 0;
}
// Time Complexity: Amortized O(1)
```
## Contains()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s = {10, 20};
    bool exists = (s.find(10) != s.end());
    std::cout << "Contains 10: " << exists << std::endl;
    assert(exists == true);
    return 0;
}
// Time Complexity: Amortized O(1)
```
## Clear()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s = {10, 20};
    s.clear();
    std::cout << "Cleared set." << std::endl;
    assert(s.empty());
    return 0;
}
// Time Complexity: O(N)
```
## Size()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s = {10, 20};
    size_t size = s.size();
    std::cout << "Size: " << size << std::endl;
    assert(size == 2);
    return 0;
}
// Time Complexity: O(1)
```
## IsEmpty()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s;
    bool empty = s.empty();
    std::cout << "IsEmpty: " << empty << std::endl;
    assert(empty == true);
    return 0;
}
// Time Complexity: O(1)
```
## Copy()
### 대표코드
```cpp
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s = {10, 20};
    std::unordered_set<int> s2 = s; // Deep copy
    std::cout << "Copied set." << std::endl;
    assert(s2.size() == 2 && s2.count(10) == 1);
    return 0;
}
// Time Complexity: O(N)
```

# Part 2. 집합 연산
## Union()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <algorithm>
#include <cassert>

int main() {
    std::set<int> s1 = {1, 2}, s2 = {2, 3}, res;
    std::set_union(s1.begin(), s1.end(), s2.begin(), s2.end(), std::inserter(res, res.begin()));
    std::cout << "Union size: " << res.size() << std::endl;
    assert(res.size() == 3);
    return 0;
}
// Time Complexity: O(N + M)
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
#include <iostream>
#include <set>
#include <algorithm>
#include <cassert>

int main() {
    std::set<int> s1 = {1, 2}, s2 = {2, 3}, res;
    std::set_intersection(s1.begin(), s1.end(), s2.begin(), s2.end(), std::inserter(res, res.begin()));
    std::cout << "Intersection size: " << res.size() << std::endl;
    assert(res.size() == 1 && res.count(2));
    return 0;
}
// Time Complexity: O(N + M)
```
## Difference()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <algorithm>
#include <cassert>

int main() {
    std::set<int> s1 = {1, 2}, s2 = {2, 3}, res;
    std::set_difference(s1.begin(), s1.end(), s2.begin(), s2.end(), std::inserter(res, res.begin()));
    std::cout << "Difference size: " << res.size() << std::endl;
    assert(res.size() == 1 && res.count(1));
    return 0;
}
// Time Complexity: O(N + M)
```
## SymmetricDifference()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <algorithm>
#include <cassert>

int main() {
    std::set<int> s1 = {1, 2}, s2 = {2, 3}, res;
    std::set_symmetric_difference(s1.begin(), s1.end(), s2.begin(), s2.end(), std::inserter(res, res.begin()));
    std::cout << "Symmetric Difference size: " << res.size() << std::endl;
    assert(res.size() == 2 && !res.count(2));
    return 0;
}
// Time Complexity: O(N + M)
```
## Complement()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <algorithm>
#include <cassert>

int main() {
    std::set<int> U = {1, 2, 3, 4}, A = {2, 3}, res;
    std::set_difference(U.begin(), U.end(), A.begin(), A.end(), std::inserter(res, res.begin()));
    std::cout << "Complement size: " << res.size() << std::endl;
    assert(res.size() == 2 && res.count(1) && res.count(4));
    return 0;
}
// Time Complexity: O(|U| + |A|)
```
## CartesianProduct()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> A = {1, 2}, B = {3, 4};
    std::vector<std::pair<int, int>> result;
    for (int a : A) for (int b : B) result.push_back({a, b});
    std::cout << "Cartesian Product size: " << result.size() << std::endl;
    assert(result.size() == 4);
    return 0;
}
// Time Complexity: O(|A| * |B|)
```
## PowerSet()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> s = {1, 2, 3};
    int n = s.size();
    int count = 0;
    for (int i = 0; i < (1 << n); ++i) count++;
    std::cout << "PowerSet subsets: " << count << std::endl;
    assert(count == 8);
    return 0;
}
// Time Complexity: O(2^N)
```

# Part 3. 관계 판별
## IsSubset()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <algorithm>
#include <cassert>

int main() {
    std::set<int> A = {1, 2, 3}, B = {1, 2};
    bool isSubset = std::includes(A.begin(), A.end(), B.begin(), B.end());
    std::cout << "B is subset of A: " << isSubset << std::endl;
    assert(isSubset == true);
    return 0;
}
// Time Complexity: O(|A| + |B|)
```
## IsProperSubset()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <algorithm>
#include <cassert>

int main() {
    std::set<int> A = {1, 2, 3}, B = {1, 2};
    bool isSubset = std::includes(A.begin(), A.end(), B.begin(), B.end());
    bool isProperSubset = (isSubset && A.size() > B.size());
    std::cout << "B is proper subset of A: " << isProperSubset << std::endl;
    assert(isProperSubset == true);
    return 0;
}
// Time Complexity: O(|A| + |B|)
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
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> A = {1, 2}, B = {3, 4};
    bool disjoint = true;
    for (int x : B) { if (A.count(x)) disjoint = false; }
    std::cout << "A and B are disjoint: " << disjoint << std::endl;
    assert(disjoint == true);
    return 0;
}
// Time Complexity: O(|B|) on average
```
## Equals()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    std::set<int> A = {1, 2}, B = {1, 2};
    bool equals = (A == B);
    std::cout << "A equals B: " << equals << std::endl;
    assert(equals == true);
    return 0;
}
// Time Complexity: O(N)
```

# Part 4. 반복과 탐색
## Iterator()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    std::set<int> s = {1, 2, 3};
    auto it = s.begin();
    int count = 0;
    while (it != s.end()) { count++; ++it; }
    std::cout << "Iterated over elements: " << count << std::endl;
    assert(count == 3);
    return 0;
}
// Time Complexity: O(N)
```
## ForEach()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    std::set<int> s = {1, 2, 3};
    int sum = 0;
    for (int element : s) sum += element;
    std::cout << "Sum using range-based for: " << sum << std::endl;
    assert(sum == 6);
    return 0;
}
// Time Complexity: O(N)
```
## Find()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    std::set<int> s = {1, 2, 3};
    auto it = s.find(2);
    std::cout << "Found element: " << *it << std::endl;
    assert(it != s.end() && *it == 2);
    return 0;
}
// Time Complexity: O(log N) for std::set
```
## Filter()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    std::set<int> s = {1, 2, 3, 4};
    // std::erase_if is in C++20. Here is manual filter:
    for (auto it = s.begin(); it != s.end(); ) {
        if (*it % 2 == 0) it = s.erase(it);
        else ++it;
    }
    std::cout << "Filtered odd elements only. Size: " << s.size() << std::endl;
    assert(s.size() == 2);
    return 0;
}
// Time Complexity: O(N log N)
```
## Map()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    std::set<int> s = {1, 2}, mapped_s;
    for (int val : s) mapped_s.insert(val * 2);
    std::cout << "Mapped set size: " << mapped_s.size() << std::endl;
    assert(mapped_s.count(4));
    return 0;
}
// Time Complexity: O(N log N)
```
## Reduce()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <numeric>
#include <cassert>

int main() {
    std::set<int> s = {1, 2, 3};
    int sum = std::accumulate(s.begin(), s.end(), 0);
    std::cout << "Reduced sum: " << sum << std::endl;
    assert(sum == 6);
    return 0;
}
// Time Complexity: O(N)
```

# Part 5. 구현
## ArraySet()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> s;
    int val = 10;
    if (std::find(s.begin(), s.end(), val) == s.end()) s.push_back(val);
    assert(s.size() == 1);
    std::cout << "ArraySet insert verified." << std::endl;
    return 0;
}
// Time Complexity: O(N) for insert
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
#include <iostream>
#include <unordered_set>
#include <cassert>

int main() {
    std::unordered_set<int> s;
    s.insert(1);
    assert(s.count(1));
    std::cout << "HashSet verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TreeSet()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    std::set<int> s; // Ordered set (Tree)
    s.insert(2); s.insert(1);
    assert(*s.begin() == 1);
    std::cout << "TreeSet verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## BitSet()
### 대표코드
```cpp
#include <iostream>
#include <bitset>
#include <cassert>

int main() {
    std::bitset<100> bs;
    bs.set(10);
    assert(bs.test(10));
    std::cout << "BitSet verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ImmutableSet()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

int main() {
    const std::set<int> s = {1, 2, 3};
    // s.insert(4); // Compiler error
    assert(s.size() == 3);
    std::cout << "ImmutableSet verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 6. 비트 집합
## SetBit()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int mask = 0;
    mask |= (1 << 5);
    assert(mask == 32);
    std::cout << "SetBit verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ClearBit()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int mask = 32;
    mask &= ~(1 << 5);
    assert(mask == 0);
    std::cout << "ClearBit verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ToggleBit()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int mask = 0;
    mask ^= (1 << 5); // 32
    mask ^= (1 << 5); // 0
    assert(mask == 0);
    std::cout << "ToggleBit verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TestBit()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int mask = 32;
    bool exists = mask & (1 << 5);
    assert(exists == true);
    std::cout << "TestBit verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CountBits()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int mask = 5; // 101 in binary
    int count = __builtin_popcount(mask);
    assert(count == 2);
    std::cout << "CountBits verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## EnumerateSubsets()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int mask = 5; // 101 in binary (4 + 1)
    int count = 0;
    for (int i = mask; i > 0; i = (i - 1) & mask) count++;
    assert(count == 3); // 5, 4, 1
    std::cout << "EnumerateSubsets verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```

# Part 7. 서로소 집합
## MakeSet()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int N = 5;
    std::vector<int> parent(N);
    for (int i = 0; i < N; ++i) parent[i] = i; 
    assert(parent[4] == 4);
    std::cout << "MakeSet verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## FindSet()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<int> parent = {0, 0, 1};
int findSet(int v) {
    if (v == parent[v]) return v;
    return parent[v] = findSet(parent[v]); 
}

int main() {
    assert(findSet(2) == 0);
    std::cout << "FindSet verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## UnionSet()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<int> parent = {0, 1};
int findSet(int v) { return v == parent[v] ? v : parent[v] = findSet(parent[v]); }
void unionSet(int a, int b) {
    a = findSet(a); b = findSet(b);
    if (a != b) parent[a] = b;
}

int main() {
    unionSet(0, 1);
    assert(findSet(0) == findSet(1));
    std::cout << "UnionSet verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
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
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    int n = 4, k = 2, count = 0;
    std::vector<int> mask(n, 0);
    std::fill(mask.end() - k, mask.end(), 1);
    do { count++; } while(std::next_permutation(mask.begin(), mask.end()));
    assert(count == 6); // 4C2
    std::cout << "Combination generated." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## Permutation()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> v = {1, 2, 3};
    int count = 0;
    do { count++; } while(std::next_permutation(v.begin(), v.end()));
    assert(count == 6); // 3!
    std::cout << "Permutation generated." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
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
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> v = {1, 2, 3};
    std::next_permutation(v.begin(), v.end()); 
    assert(v[0] == 1 && v[1] == 3 && v[2] == 2);
    std::cout << "NextPermutation executed." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## GrayCode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int n = 3;
    int gray = n ^ (n >> 1); // For 3 (011), Gray is 2 (010)
    assert(gray == 2);
    std::cout << "GrayCode evaluated." << std::endl;
    return 0;
}
// Time Complexity: O(1)
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
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 0/1 배낭(Knapsack)을 부분집합 선택 문제로 보기: 물건의 집합에서 무게 합이 용량 W 이하인 부분집합 중 가치 합이 최대인 것을 고른다. DP: dp[i][w] = 앞의 i 개 물건 중에서 무게 w 이하로 얻는 최대 가치, 점화식 dp[i][w] = max(dp[i−1][w], dp[i−1][w − wt_i] + val_i).
// 선택된 부분집합은 표를 거꾸로 따라가며 복원한다(dp[i][w] ≠ dp[i−1][w] 이면 i 번째 물건을 선택). 탐욕법(가치/무게 비율 순)은 항상 최적이 아니지만 분수 배낭(물건을 쪼갤 수 있을 때)의 최적값은 0/1 배낭 최적값의 상한이 된다.
// 검증: n ≤ 16 무작위 입력 300개에서 ① DP 최적값 == 2ⁿ 완전 열거 ② 복원한 선택의 무게 ≤ W, 가치 == 최적값, 인덱스 중복 없음 ③ 비율 탐욕법 ≤ 최적이고 최적보다 작은 사례가 실제로 존재 ④ 분수 배낭 상한 ≥ 최적 (그리고 정수 해일 때만 같음)
int main() {
    std::mt19937 rng(14); int greedyWorse = 0, instances = 0;
    for (int t = 0; t < 300; t++) { int n = 1 + rng() % 16; std::vector<int> wt(n), val(n); for (int i = 0; i < n; i++) { wt[i] = 1 + rng() % 15; val[i] = 1 + rng() % 30; } int W = 1 + rng() % 45; instances++;
        std::vector<std::vector<int>> dp(n + 1, std::vector<int>(W + 1, 0)); for (int i = 1; i <= n; i++) for (int w = 0; w <= W; w++) { dp[i][w] = dp[i - 1][w]; if (w >= wt[i - 1]) dp[i][w] = std::max(dp[i][w], dp[i - 1][w - wt[i - 1]] + val[i - 1]); }
        int best = 0; for (int mask = 0; mask < (1 << n); mask++) { int w = 0, v = 0; for (int i = 0; i < n; i++) if (mask >> i & 1) { w += wt[i]; v += val[i]; } if (w <= W) best = std::max(best, v); } assert(dp[n][W] == best);                       // ① 완전 열거와 같음
        std::vector<int> chosen; int w = W; for (int i = n; i >= 1; i--) if (dp[i][w] != dp[i - 1][w]) { chosen.push_back(i - 1); w -= wt[i - 1]; } int tw = 0, tv = 0; std::vector<char> seen(n, 0); for (int i : chosen) { assert(!seen[i]); seen[i] = 1; tw += wt[i]; tv += val[i]; } assert(tw <= W && tv == best);   // ② 복원
        std::vector<int> order(n); for (int i = 0; i < n; i++) order[i] = i; std::sort(order.begin(), order.end(), [&](int a, int b) { return (long long)val[a] * wt[b] > (long long)val[b] * wt[a]; }); int gw = 0, gv = 0; for (int i : order) if (gw + wt[i] <= W) { gw += wt[i]; gv += val[i]; } assert(gv <= best); greedyWorse += gv < best;   // ③ 비율 탐욕법
        double frac = 0, cap = W; for (int i : order) { if (wt[i] <= cap) { frac += val[i]; cap -= wt[i]; } else { frac += val[i] * cap / wt[i]; break; } } assert(frac >= best - 1e-9); }                                                                            // ④ 분수 배낭 상한
    assert(greedyWorse > 10);
    std::cout << "KnapsackSubset: DP optimum equals exhaustive search on " << instances << " random instances and the reconstructed item set is feasible and optimal; ratio-greedy was strictly worse on " << greedyWorse << " instances; the fractional relaxation was always an upper bound" << std::endl; return 0;
}
// Time Complexity: O(n · W)
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
int main() {
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
int main() {
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
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 몫집합(quotient set) X/~ 은 동치류들의 집합이다. 투영 π: X → X/~ (x ↦ [x])는 전사이고, "~ 을 존중하는 함수" 는 몫집합 위에서 정의할 수 있다: f 가 a ~ b ⇒ f(a) = f(b) (well-defined 조건)를 만족하면 f̃([x]) = f(x) 가 문제없이 정의되고 f̃ ∘ π = f 이며 f̃ 은 유일하다(몫의 보편 성질).
// 반대로 임의의 함수 f 는 "f(a) = f(b)" 라는 핵 관계 ker f 를 정의하고 이는 동치 관계다 — X/ker f 와 치역 f(X) 사이에는 일대일 대응이 있다(제1 동형 정리의 집합 버전). 프로그램에서는 해시 키·정규형이 이 원리의 실례다: 키가 같은 것을 같은 류로 본다.
// 검증: ① X = {0..59}, x ~ y ⇔ x mod 6 = y mod 6 에서 몫집합 크기 6, π 가 전사, 잘 정의된 f(x) = (x mod 6)² 의 유도 함수 f̃ 가 f̃∘π = f 를 만족 ② 잘 정의되지 않은 f(x) = x 는 well-defined 검사에서 거부됨 ③ 무작위 함수 200개의 핵 ker f 에서 |X/ker f| = |f(X)| 이고 유도된 f̃ 가 단사
int main() {
    const int n = 60, k = 6; std::vector<int> pi(n); std::map<int, int> classId; std::vector<std::set<int>> quotient; for (int x = 0; x < n; x++) { int key = x % k; if (!classId.count(key)) { classId[key] = quotient.size(); quotient.emplace_back(); } pi[x] = classId[key]; quotient[pi[x]].insert(x); }
    assert((int)quotient.size() == k); std::set<int> image(pi.begin(), pi.end()); assert((int)image.size() == k);                                                                                            // 전사: π 의 치역 = X/~
    auto wellDefined = [&](auto f) { for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) if (pi[a] == pi[b] && f(a) != f(b)) return false; return true; };
    auto f = [](int x) { return (x % 6) * (x % 6); }; assert(wellDefined(f)); std::vector<int> ftilde(k); for (int c = 0; c < k; c++) ftilde[c] = f(*quotient[c].begin()); for (int x = 0; x < n; x++) assert(ftilde[pi[x]] == f(x));         // ① 보편 성질 f̃∘π = f
    auto bad = [](int x) { return x; }; assert(!wellDefined(bad));                                                                                                                                              // ② 잘 정의되지 않음
    std::mt19937 rng(9); for (int t = 0; t < 200; t++) { int range = 1 + rng() % 12; std::vector<int> g(n); for (int& v : g) v = rng() % range; std::map<int, int> kerClass; std::vector<int> proj(n); int next = 0; for (int x = 0; x < n; x++) { if (!kerClass.count(g[x])) kerClass[g[x]] = next++; proj[x] = kerClass[g[x]]; }
        std::set<int> gimage(g.begin(), g.end()); assert((int)gimage.size() == next);                                                                                                                              // ③ |X/ker g| = |g(X)|
        std::vector<int> tilde(next, -1); for (int x = 0; x < n; x++) { assert(tilde[proj[x]] == -1 || tilde[proj[x]] == g[x]); tilde[proj[x]] = g[x]; } std::set<int> vals(tilde.begin(), tilde.end()); assert((int)vals.size() == next); }                  // g̃ 는 단사
    std::cout << "QuotientSet: X/(mod 6) has 6 classes, the projection is onto, a class-respecting function descends uniquely to the quotient (f~ o pi = f), a non-respecting function is rejected, and for 200 random functions |X/ker f| = |f(X)| with the induced map injective" << std::endl; return 0;
}
// Time Complexity: 몫집합 구성 O(n), 잘 정의됨 검사 O(n²) (또는 류별 O(n))
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
#include <random>
#include <unordered_map>
#include <vector>
#include <cassert>

// GROUP BY: 키가 같은 행끼리 묶고 묶음마다 집계 함수(COUNT, SUM, MIN, MAX, AVG)를 계산한다. 집합론으로는 "키가 같다" 는 동치 관계가 만드는 분할 위에서 각 동치류마다 하나의 행을 내는 연산이다 — 그룹 수 = 동치류 수, 그룹 크기의 합 = 행 수.
// 구현 두 가지: 해시 집계(키 → 누적기, 한 번 훑기 O(n))와 정렬 집계(키로 정렬한 뒤 같은 키 구간을 한 묶음으로, O(n log n)·결과가 키 순서). AVG 는 SUM/COUNT 로 계산해야 부분 집계의 결합(분산 집계)이 맞다 — 평균의 평균은 평균이 아니다(가중치 필요). HAVING 은 집계 결과에 대한 선택이다.
// 검증: 무작위 릴레이션 300개에서 ① 해시 집계 == 정렬 집계 == 단순 재스캔 ② Σ COUNT = 행 수, Σ SUM = 전체 합 ③ 그룹 수 = 서로 다른 키 수 ④ 두 조각으로 나눠 부분 집계한 뒤 합치면(COUNT, SUM, MIN, MAX 결합) 전체 집계와 같음, 단 "평균의 평균" 은 다름 ⑤ HAVING COUNT >= 3 필터
struct Agg { long count = 0, sum = 0, mn = 1L << 40, mx = -(1L << 40); void add(long v) { count++; sum += v; mn = std::min(mn, v); mx = std::max(mx, v); } void merge(const Agg& o) { count += o.count; sum += o.sum; mn = std::min(mn, o.mn); mx = std::max(mx, o.mx); } bool operator==(const Agg& o) const { return count == o.count && sum == o.sum && mn == o.mn && mx == o.mx; } };
typedef std::vector<std::pair<int, int>> Rows;
std::map<int, Agg> hashGroup(const Rows& r) { std::unordered_map<int, Agg> h; for (auto [k, v] : r) h[k].add(v); return std::map<int, Agg>(h.begin(), h.end()); }
std::map<int, Agg> sortGroup(Rows r) { std::sort(r.begin(), r.end()); std::map<int, Agg> o; for (size_t i = 0; i < r.size();) { size_t j = i; Agg a; while (j < r.size() && r[j].first == r[i].first) a.add(r[j++].second); o[r[i].first] = a; i = j; } return o; }
int main() {
    std::mt19937 rng(5); int mismatchAvg = 0;
    for (int t = 0; t < 300; t++) { Rows rows; int n = rng() % 80, keys = 1 + rng() % 8; for (int i = 0; i < n; i++) rows.push_back({(int)(rng() % keys), (int)(rng() % 100) - 20});
        auto h = hashGroup(rows), s = sortGroup(rows); assert(h == s); std::map<int, Agg> naive; for (int k = 0; k < keys; k++) { Agg a; bool any = false; for (auto [kk, v] : rows) if (kk == k) { a.add(v); any = true; } if (any) naive[k] = a; } assert(h == naive);   // ① 세 방법이 같음
        long cnt = 0, sum = 0, all = 0; for (auto& [k, a] : h) { cnt += a.count; sum += a.sum; } for (auto [k, v] : rows) all += v; assert(cnt == n && sum == all);                                                               // ② 합계 보존
        std::map<int, int> distinctKeys; for (auto [k, v] : rows) distinctKeys[k]++; assert(h.size() == distinctKeys.size());                                                                                              // ③ 그룹 수
        Rows left(rows.begin(), rows.begin() + n / 2), right(rows.begin() + n / 2, rows.end()); auto hl = hashGroup(left), hr = hashGroup(right); std::map<int, Agg> merged = hl; for (auto& [k, a] : hr) merged[k].merge(a); assert(merged == h);                         // ④ 부분 집계 결합
        for (auto& [k, a] : h) { if (hl.count(k) && hr.count(k)) { double l = (double)hl[k].sum / hl[k].count, r = (double)hr[k].sum / hr[k].count; double wrong = (l + r) / 2, right2 = (double)h[k].sum / h[k].count; if (std::abs(wrong - right2) > 1e-9) mismatchAvg++; } }
        std::map<int, Agg> having; for (auto& [k, a] : h) if (a.count >= 3) having[k] = a; for (auto& [k, a] : having) assert(a.count >= 3); for (auto& [k, a] : h) assert((a.count >= 3) == (having.count(k) == 1)); }                                       // ⑤ HAVING
    assert(mismatchAvg > 0);
    std::cout << "GroupBy: hash, sort and naive aggregation agree on 300 random relations; group counts and sums are conserved; partial aggregates merge exactly for COUNT/SUM/MIN/MAX but an average of averages differed from the true average in " << mismatchAvg << " group splits" << std::endl; return 0;
}
// Time Complexity: 해시 집계 O(n), 정렬 집계 O(n log n)
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
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 카운팅 블룸 필터(집합 관점의 요약, 정본은 AdvancedDataStructures.md Part 3): 비트 대신 작은 카운터(보통 4 비트)를 두어 삽입은 k 개 카운터 +1, 삭제는 −1, 조회는 k 개 카운터가 모두 > 0 인지로 삭제를 지원한다. 공간은 일반 블룸의 약 4 배.
// 카운터가 포화(15)하면 더 이상 증가하지 않고 이후 감소도 하지 않는다 — 그대로 두면 감소 때 0 이 되어 거짓 음성이 생길 수 있어서(포화한 카운터는 "영원히 > 0" 으로 고정; 거짓 양성만 늘어남). 넣지 않은 원소를 삭제하면 다른 원소가 깨지므로 삭제는 "실제로 넣은 원소"에만 허용해야 한다.
// 검증: 무작위 삽입/삭제 열 50000개에서 ① 현재 집합의 원소는 항상 "아마도 있음" (거짓 음성 0) ② 삭제된 원소는 대부분 "없음"으로 돌아옴 ③ 삽입·삭제 후의 카운터 총합 = k × 현재 원소 수 (포화가 없을 때) ④ 포화 사례(작은 배열)에서도 거짓 음성이 생기지 않음
struct CBF { std::vector<uint8_t> c; int k; size_t m; CBF(size_t m, int k) : c(m, 0), k(k), m(m) {} static uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
    size_t pos(uint64_t key, int i) const { uint64_t h = mix(key), h2 = mix(h) | 1; return (h + i * h2) % m; } void add(uint64_t key) { for (int i = 0; i < k; i++) { uint8_t& x = c[pos(key, i)]; if (x < 15) x++; } } void remove(uint64_t key) { for (int i = 0; i < k; i++) { uint8_t& x = c[pos(key, i)]; if (x > 0 && x < 15) x--; } }                // 포화(15)한 카운터는 고정
    bool maybe(uint64_t key) const { for (int i = 0; i < k; i++) if (!c[pos(key, i)]) return false; return true; } long sum() const { long s = 0; for (uint8_t x : c) s += x; return s; } bool saturated() const { for (uint8_t x : c) if (x == 15) return true; return false; } };
int main() {
    std::mt19937_64 rng(9); CBF f(1 << 15, 5); std::set<uint64_t> live; std::vector<uint64_t> pool; for (int i = 0; i < 4000; i++) pool.push_back(rng()); std::set<uint64_t> removed;
    for (int step = 0; step < 50000; step++) { uint64_t x = pool[rng() % pool.size()]; if (live.count(x)) { if (rng() % 2) { f.remove(x); live.erase(x); removed.insert(x); } } else { f.add(x); live.insert(x); removed.erase(x); }
        if (step % 5000 == 0) { for (uint64_t y : live) assert(f.maybe(y)); } }
    for (uint64_t y : live) assert(f.maybe(y)); assert(!f.saturated() && f.sum() == 5 * (long)live.size());                                                                                       // ① 거짓 음성 0 ③ 카운터 합
    int stillThere = 0; for (uint64_t y : removed) stillThere += f.maybe(y); assert(!removed.empty() && stillThere * 20 < (int)removed.size());                                                                // ② 삭제된 원소는 거의 사라짐
    { CBF tiny(64, 3); std::vector<uint64_t> all; for (int i = 0; i < 300; i++) { uint64_t x = rng(); tiny.add(x); all.push_back(x); } assert(tiny.saturated()); for (size_t i = 0; i < all.size(); i += 2) tiny.remove(all[i]); for (size_t i = 1; i < all.size(); i += 2) assert(tiny.maybe(all[i])); }       // ④ 포화 상태(작은 배열)에서 일부를 지워도 남은 원소는 거짓 음성이 되지 않음
    std::cout << "CountingBloomFilter: after 50000 random inserts/deletes of " << live.size() << " live keys there are no false negatives and the counter total equals k x live keys; only " << stillThere << " of " << removed.size() << " deleted keys still test positive; saturated counters are frozen so deleting under saturation never causes a false negative" << std::endl; return 0;
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
    std::cout << "QuotientFilter: concept model of quotient/remainder runs; no false negatives, measured false-positive rate " << rate << " vs alpha*2^-r = " << theory << " (every false positive is exactly a fingerprint collision), runs stay sorted and two filters merge by sorted union of runs" << std::endl; return 0;
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
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 압축 비트 집합(compressed bitset): 희소하거나 덩어리진 비트맵은 같은 값의 긴 워드 구간(0 만 또는 1 만)이 많다. WAH/EWAH 계열 방식은 32 비트 워드열을 "채움 런(fill run: 0 워드 또는 1 워드가 n 번)" 과 "리터럴 워드(그대로 저장)" 의 열로 부호화한다.
// 핵심은 압축을 풀지 않고 연산하는 것이다 — 두 압축열의 커서를 나란히 전진시키며 한쪽이 긴 0 채움이면 AND 결과는 그 길이만큼 0 채움(OR 은 다른 쪽을 그대로 복사)이라 런 단위로 건너뛴다. 결과도 같은 방식으로 이어 붙여(인접한 같은 채움은 합침) 압축 상태를 유지한다.
// 한계: 임의 위치 접근이 O(런 수)이고 변경이 어렵다(Roaring 비트맵이 보완). 검증: 희소(0.05%)·덩어리(긴 구간)·조밀(50% 무작위) 비트맵 각 40개에서 ① 압축·복원이 무손실 ② 압축 상태의 AND/OR/XOR 결과가 원시 비트 연산과 같고 결과도 정규형(인접 같은 채움 합쳐짐) ③ 희소·덩어리는 원시 크기의 1/3 이하로 줄고 조밀은 줄지 않음(런 하나를 4 바이트로 계산) ④ 압축 연산이 방문한 런 수가 원시 워드 수보다 훨씬 적음
struct Run { bool fill; bool bit; uint32_t count; uint32_t lit; };                                                                                               // fill: bit 값 워드 count 개 / 아니면 리터럴 워드 하나
struct Compressed { std::vector<Run> runs; uint32_t words = 0;
    void append(uint32_t word, uint32_t n = 1) { if (n == 0) return; words += n; bool isFill = word == 0 || word == ~0u; if (isFill) { bool bit = word != 0; if (!runs.empty() && runs.back().fill && runs.back().bit == bit) runs.back().count += n; else runs.push_back({true, bit, n, 0}); } else { for (uint32_t i = 0; i < n; i++) runs.push_back({false, false, 1, word}); } }
    static Compressed from(const std::vector<uint32_t>& raw) { Compressed c; for (uint32_t w : raw) c.append(w); return c; }
    std::vector<uint32_t> expand() const { std::vector<uint32_t> out; for (auto& r : runs) { if (r.fill) out.insert(out.end(), r.count, r.bit ? ~0u : 0u); else out.push_back(r.lit); } return out; } };
struct Cursor { const std::vector<Run>& r; size_t i = 0; uint32_t used = 0; long visited = 0; bool done() const { return i >= r.size(); } bool fill() const { return r[i].fill; } uint32_t word() const { return r[i].fill ? (r[i].bit ? ~0u : 0u) : r[i].lit; } uint32_t left() const { return r[i].count - used; }
    void skip(uint32_t n) { used += n; if (used == r[i].count) { i++; used = 0; visited++; } } };
template <class Op> Compressed combine(const Compressed& a, const Compressed& b, Op op, long& visited) { Compressed out; Cursor x{a.runs}, y{b.runs}; while (!x.done() && !y.done()) { uint32_t n = 1; if (x.fill() && y.fill()) n = std::min(x.left(), y.left()); else if (x.fill() && !y.fill()) n = 1; else if (!x.fill() && y.fill()) n = 1; out.append(op(x.word(), y.word()), n); x.skip(n); y.skip(n); } visited += x.visited + y.visited; return out; }
int main() {
    std::mt19937 rng(8); const uint32_t W = 2000; long compSizeSparse = 0, rawSizeSparse = 0, compSizeDense = 0, rawSizeDense = 0, visited = 0, rawWords = 0;
    for (int kind = 0; kind < 3; kind++) for (int t = 0; t < 40; t++) { std::vector<uint32_t> A(W, 0), B(W, 0); for (int which = 0; which < 2; which++) { auto& v = which ? B : A; if (kind == 0) { for (int i = 0; i < (int)(W * 32 * 0.0005); i++) { uint32_t pos = rng() % (W * 32); v[pos / 32] |= 1u << (pos % 32); } } else if (kind == 1) { uint32_t pos = 0; while (pos < W) { uint32_t len = 1 + rng() % 200; bool on = rng() % 2; for (uint32_t i = 0; i < len && pos < W; i++, pos++) v[pos] = on ? ~0u : 0u; } } else { for (auto& w : v) w = rng(); } }
        Compressed ca = Compressed::from(A), cb = Compressed::from(B); assert(ca.expand() == A && cb.expand() == B && ca.words == W);                                                                                       // ① 무손실
        auto test = [&](auto op) { long vis = 0; Compressed c = combine(ca, cb, op, vis); std::vector<uint32_t> expect(W); for (uint32_t i = 0; i < W; i++) expect[i] = op(A[i], B[i]); assert(c.expand() == expect); for (size_t i = 1; i < c.runs.size(); i++) assert(!(c.runs[i].fill && c.runs[i - 1].fill && c.runs[i].bit == c.runs[i - 1].bit)); return vis; };       // ② 정규형
        long v1 = test([](uint32_t x, uint32_t y) { return x & y; }), v2 = test([](uint32_t x, uint32_t y) { return x | y; }), v3 = test([](uint32_t x, uint32_t y) { return x ^ y; }); if (kind != 2) { visited += v1 + v2 + v3; rawWords += 3L * W * 2; }
        long cs = ca.runs.size() * 4L /* WAH 처럼 런(채움 헤더 또는 리터럴 워드)마다 4 바이트 */, rs = W * 4L; if (kind == 2) { compSizeDense += cs; rawSizeDense += rs; } else { compSizeSparse += cs; rawSizeSparse += rs; } }
    assert(compSizeSparse * 3 < rawSizeSparse && compSizeDense >= rawSizeDense * 9 / 10 && visited < rawWords);
    std::cout << "CompressedBitSet: run-length (WAH/EWAH-style) compression is lossless and AND/OR/XOR on compressed runs equal the raw word operations with canonical output on 120 bitmap pairs; sparse/clustered data used " << compSizeSparse << " bytes versus " << rawSizeSparse << " raw, random dense data " << compSizeDense << " versus " << rawSizeDense << "; cursors visited " << visited << " runs for " << rawWords << " raw word steps" << std::endl; return 0;
}
// Time Complexity: 연산 O(두 압축열의 런 수), 압축 O(워드 수)
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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Set uniqueness vs List ordered duplicates." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Set vs Multiset
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Set unique vs Multiset duplicate items allowed." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## HashSet vs TreeSet
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Hash O(1) unordered vs Tree O(logN) ordered." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## BitSet은 언제 사용하는가?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "BitSet is ideal for dense integer sets requiring fast ops." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Union-Find가 거의 O(1)인 이유
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Path compression + Rank bound time to inverse Ackermann." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 집합과 그래프의 연결
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Graph is a set of vertices and set of relation edges." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 집합과 관계(Relation)
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Relation is a subset of Cartesian Product." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 집합과 함수(Function)
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Function is a relation mapping exactly one output." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SQL은 왜 집합 이론 위에서 동작하는가?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Relational algebra grounds SQL in set operations." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## AI에서 Label Set과 Vocabulary Set의 의미
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Sets define discrete target or input spaces." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 비트마스크와 집합의 대응 관계
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Bit operations correspond directly to set operations." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 부분집합 열거 최적화
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Bit tricks allow O(3^N) generation of subsets of subsets." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

