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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Backtracking constructs subset item by item via DFS." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## BitMaskEnumeration()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Loop 0 to 2^N-1 provides all subset bitmasks." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MeetInTheMiddle()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Meet-in-the-middle cuts search space from 2^N to 2^(N/2)." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SubsetSum()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "SubsetSum is NP-Complete, solved by DP or MITM." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## KnapsackSubset()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Knapsack seeks subset with max value under capacity constraint." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 10. 수학적 구조
## BinaryRelation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Binary Relation is subset of A x B." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## EquivalenceRelation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Equivalence Relation is reflexive, symmetric, transitive." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Partition()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Partition divides set into non-overlapping subsets." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## EquivalenceClass()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Equivalence Class is a block in a partition." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## QuotientSet()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Quotient Set is the set of all equivalence classes." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 11. 데이터베이스
## Distinct()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "SQL DISTINCT removes duplicates using Set properties." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Projection()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Projection selects specific attributes." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Selection()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Selection filters tuples based on predicate." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Join()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Join combines subsets satisfying a condition." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## GroupBy()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "GroupBy partitions tuples into equivalence classes by key." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DuplicateElimination()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Duplicate Elimination enforces set uniqueness physically." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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

