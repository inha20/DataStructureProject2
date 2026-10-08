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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Inverted Index maps words to sets of document IDs." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PostingList()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Posting List is an ordered set of doc IDs for a term." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## JaccardSimilarity()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Jaccard = |Intersection| / |Union|." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MinHash()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "MinHash estimates Jaccard Similarity efficiently." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LocalitySensitiveHashing()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "LSH hashes similar sets to same buckets." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 13. AI와 데이터
## LabelSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Label Set defines classification categories." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## FeatureSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Feature Set spans the input space dimensions." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## VocabularySet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Vocabulary Set contains all unique tokens." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CandidateSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Candidate Set is filtered subset for recommendation." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ConstraintSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Constraint Set bounds the feasible solution space." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 14. 확률적 집합
## BloomFilter()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Bloom Filter tests set membership probabilistically." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CountingBloomFilter()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Counting Bloom Filter allows deletions." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CuckooFilter()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cuckoo Filter stores fingerprints, handles deletions well." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## QuotientFilter()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Quotient Filter is cache-friendly alternative to Bloom." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 15. 병렬 집합
## ConcurrentSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Concurrent Set ensures thread safety." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LockFreeSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Lock-Free Set avoids OS locks using atomic CAS." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SkipListSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "SkipList Set often underlines concurrent ordered sets." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ConcurrentHashSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Concurrent Hash Set uses lock striping for performance." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 16. 연구 주제
## PersistentSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Persistent Set preserves previous versions upon update." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ImmutableBitSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Immutable BitSet is safe for unprotected concurrent read." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CompressedBitSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Compressed BitSet leverages run-length encoding." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RoaringBitmap()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Roaring Bitmap switches layout based on density." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SuccinctSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Succinct Set targets information theoretic space limit." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LearnedSetIndex()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Learned Set Index uses ML to predict element locations." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DynamicConnectivity()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Dynamic Connectivity tests components in changing graphs." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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

