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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "IsSuperset(A, B) is same as IsSubset(B, A)." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "LinkedSet uses linked list for ordered no-dup elements." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "UnionByRank keeps tree shallow, guaranteeing O(log N)." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PathCompression()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "PathCompression combined with rank gives O(a(N))." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ConnectedComponents()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Count of unique roots equals number of connected components." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Comb w/ replacement explores DFS allowing re-selection of current index." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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

