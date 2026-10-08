# Part 1. 리스트의 기초
## CreateList()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst;
    std::cout << "List created." << std::endl;
    assert(lst.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Traverse()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3};
    std::cout << "Traverse: ";
    for (int x : lst) {
        std::cout << x << " ";
    }
    std::cout << std::endl;
    assert(lst.size() == 3);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## Search()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <algorithm>
#include <cassert>

int main() {
    std::list<int> lst = {10, 20, 30};
    int target = 20;
    auto it = std::find(lst.begin(), lst.end(), target);
    bool found = (it != lst.end());
    std::cout << "Search(20) -> " << found << std::endl;
    assert(found == true);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## Insert()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {10, 30};
    auto it = lst.begin();
    std::advance(it, 1); 
    lst.insert(it, 20);  
    std::cout << "Insert(20) executed." << std::endl;
    assert(lst.size() == 3);
    return 0;
}
// Time Complexity: O(N) to advance, O(1) to insert
// Space Complexity: O(1)
```
## Delete()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {10, 20, 30, 20};
    lst.remove(20); 
    std::cout << "Delete(20) executed." << std::endl;
    assert(lst.size() == 2);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## Update()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <algorithm>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3};
    auto it = std::find(lst.begin(), lst.end(), 2);
    if (it != lst.end()) *it = 20;
    std::cout << "Update executed." << std::endl;
    assert(*std::find(lst.begin(), lst.end(), 20) == 20);
    return 0;
}
// Time Complexity: O(N) to find, O(1) to update
// Space Complexity: O(1)
```
## Reverse()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3};
    lst.reverse(); 
    std::cout << "Reverse executed." << std::endl;
    assert(lst.front() == 3);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## Copy()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3};
    std::list<int> lst2 = lst; 
    std::cout << "Copy executed." << std::endl;
    assert(lst2.size() == 3 && lst2.front() == 1);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## Swap()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst1 = {1, 2};
    std::list<int> lst2 = {3, 4, 5};
    lst1.swap(lst2); 
    std::cout << "Swap executed." << std::endl;
    assert(lst1.size() == 3 && lst2.size() == 2);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Clear()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3};
    lst.clear(); 
    std::cout << "Clear executed." << std::endl;
    assert(lst.empty());
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```

# Part 2. 배열 리스트
## DynamicArray()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr;
    arr.push_back(10);
    std::cout << "DynamicArray created." << std::endl;
    assert(!arr.empty());
    return 0;
}
// Time Complexity: Amortized O(1) push
// Space Complexity: O(N)
```
## Resize()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr;
    arr.resize(100); 
    std::cout << "Resize to 100 executed." << std::endl;
    assert(arr.size() == 100);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## ShiftLeft()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {1, 2, 3, 4};
    for (int i = 1; i < (int)arr.size(); ++i) {
        arr[i - 1] = arr[i];
    }
    arr.pop_back();
    std::cout << "ShiftLeft executed." << std::endl;
    assert(arr[0] == 2 && arr.size() == 3);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## ShiftRight()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {1, 2, 3};
    arr.push_back(0); // Make space
    for (int i = arr.size() - 1; i > 0; --i) {
        arr[i] = arr[i - 1];
    }
    arr[0] = 99;
    std::cout << "ShiftRight executed." << std::endl;
    assert(arr[1] == 1);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## InsertAt()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {1, 3};
    arr.insert(arr.begin() + 1, 2);
    std::cout << "InsertAt executed." << std::endl;
    assert(arr[1] == 2);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N) if reallocation occurs
```
## DeleteAt()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {1, 2, 3};
    arr.erase(arr.begin() + 1);
    std::cout << "DeleteAt executed." << std::endl;
    assert(arr[1] == 3);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## BinarySearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {1, 3, 5, 7};
    bool exists = std::binary_search(arr.begin(), arr.end(), 5);
    std::cout << "BinarySearch(5) -> " << exists << std::endl;
    assert(exists == true);
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## LowerBound()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {10, 20, 20, 30};
    auto it = std::lower_bound(arr.begin(), arr.end(), 20);
    std::cout << "LowerBound(20) Index -> " << std::distance(arr.begin(), it) << std::endl;
    assert(*it == 20 && std::distance(arr.begin(), it) == 1);
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## UpperBound()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {10, 20, 20, 30};
    auto it = std::upper_bound(arr.begin(), arr.end(), 20);
    std::cout << "UpperBound(20) Index -> " << std::distance(arr.begin(), it) << std::endl;
    assert(*it == 30 && std::distance(arr.begin(), it) == 3);
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```

# Part 3. 연결 리스트
## PushFront()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {20};
    lst.push_front(10); 
    std::cout << "PushFront(10)" << std::endl;
    assert(lst.front() == 10);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PushBack()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {10};
    lst.push_back(20); 
    std::cout << "PushBack(20)" << std::endl;
    assert(lst.back() == 20);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PopFront()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {10, 20};
    lst.pop_front(); 
    std::cout << "PopFront executed." << std::endl;
    assert(lst.front() == 20);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PopBack()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {10, 20};
    lst.pop_back(); 
    std::cout << "PopBack executed." << std::endl;
    assert(lst.back() == 10);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## InsertAfter()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* head = new Node{10, nullptr};
    Node* newNode = new Node{20, head->next};
    head->next = newNode;
    std::cout << "InsertAfter executed." << std::endl;
    assert(head->next->data == 20);
    delete newNode; delete head;
    return 0;
}
// Time Complexity: O(1) given pointer
// Space Complexity: O(1)
```
## InsertBefore()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* prev; Node* next; };

int main() {
    Node* tail = new Node{30, nullptr, nullptr};
    Node* head = new Node{10, nullptr, tail};
    tail->prev = head;

    // Insert 20 before tail
    Node* newNode = new Node{20, tail->prev, tail};
    tail->prev->next = newNode;
    tail->prev = newNode;

    std::cout << "InsertBefore executed." << std::endl;
    assert(head->next->data == 20);
    delete head; delete newNode; delete tail;
    return 0;
}
// Time Complexity: O(1) given pointer in DLL
// Space Complexity: O(1)
```
## RemoveNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* curr = new Node{20, nullptr};
    Node* prev = new Node{10, curr};
    prev->next = curr->next;
    delete curr;
    std::cout << "RemoveNode executed." << std::endl;
    assert(prev->next == nullptr);
    delete prev;
    return 0;
}
// Time Complexity: O(1) given previous pointer
// Space Complexity: O(1)
```
## FindMiddle()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* n3 = new Node{30, nullptr};
    Node* n2 = new Node{20, n3};
    Node* head = new Node{10, n2};

    Node *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    
    std::cout << "Middle node data: " << slow->data << std::endl;
    assert(slow->data == 20);
    delete head; delete n2; delete n3;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## DetectCycle()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* n3 = new Node{30, nullptr};
    Node* n2 = new Node{20, n3};
    Node* head = new Node{10, n2};
    n3->next = n2; // Creates cycle

    bool hasCycle = false;
    Node *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) { hasCycle = true; break; }
    }
    
    std::cout << "Cycle detected: " << hasCycle << std::endl;
    assert(hasCycle == true);
    // memory leak here due to cycle, but illustrative
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## MergeLists()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

Node* merge(Node* l1, Node* l2) {
    if (!l1) return l2;
    if (!l2) return l1;
    if (l1->data < l2->data) {
        l1->next = merge(l1->next, l2);
        return l1;
    } else {
        l2->next = merge(l1, l2->next);
        return l2;
    }
}

int main() {
    Node* l1 = new Node{1, new Node{3, nullptr}};
    Node* l2 = new Node{2, new Node{4, nullptr}};
    Node* merged = merge(l1, l2);
    assert(merged->next->data == 2);
    std::cout << "MergeLists executed." << std::endl;
    return 0;
}
// Time Complexity: O(N + M)
// Space Complexity: O(N + M) due to call stack
```
## SplitList()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* n4 = new Node{40, nullptr};
    Node* n3 = new Node{30, n4};
    Node* n2 = new Node{20, n3};
    Node* head = new Node{10, n2};

    Node *slow = head, *fast = head->next;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    Node* secondHalf = slow->next;
    slow->next = nullptr;
    
    assert(head->next->next == nullptr && secondHalf->data == 30);
    std::cout << "SplitList executed." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```

# Part 4. 리스트 알고리즘
## BubbleSort()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {5, 2, 9, 1};
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        for (int j = 0; j < n - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) std::swap(arr[j], arr[j + 1]);
        }
    }
    assert(arr[0] == 1 && arr[3] == 9);
    std::cout << "BubbleSort executed." << std::endl;
    return 0;
}
// Time Complexity: O(N^2)
// Space Complexity: O(1)
```
## SelectionSort()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {4, 1, 3, 2};
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        int min_idx = i;
        for (int j = i + 1; j < n; ++j) {
            if (arr[j] < arr[min_idx]) min_idx = j;
        }
        std::swap(arr[i], arr[min_idx]);
    }
    assert(arr[0] == 1 && arr[3] == 4);
    std::cout << "SelectionSort executed." << std::endl;
    return 0;
}
// Time Complexity: O(N^2)
// Space Complexity: O(1)
```
## InsertionSort()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {4, 3, 2, 1};
    int n = arr.size();
    for (int i = 1; i < n; ++i) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        arr[j + 1] = key;
    }
    assert(arr[0] == 1 && arr[3] == 4);
    std::cout << "InsertionSort executed." << std::endl;
    return 0;
}
// Time Complexity: O(N^2)
// Space Complexity: O(1)
```
## MergeSort()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {3, 1, 4, 2};
    lst.sort(); 
    std::cout << "MergeSort (list::sort) executed." << std::endl;
    assert(lst.front() == 1);
    return 0;
}
// Time Complexity: O(N log N)
// Space Complexity: O(log N) for internal list nodes overhead
```
## QuickSort()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {5, 2, 8, 1};
    std::sort(arr.begin(), arr.end()); 
    std::cout << "QuickSort (std::sort) executed." << std::endl;
    assert(arr[0] == 1 && arr[3] == 8);
    return 0;
}
// Time Complexity: O(N log N)
// Space Complexity: O(log N) Call stack
```
## StablePartition()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {1, 2, 3, 4, 5};
    std::stable_partition(arr.begin(), arr.end(), [](int x) { return x % 2 == 0; });
    std::cout << "StablePartition executed." << std::endl;
    assert(arr[0] == 2 && arr[1] == 4);
    return 0;
}
// Time Complexity: O(N log N) or O(N) if memory available
// Space Complexity: O(N)
```

# Part 5. 투 포인터
## TwoPointers()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {1, 2, 3, 4, 5};
    int target = 6;
    int left = 0, right = arr.size() - 1;
    bool found = false;
    while (left < right) {
        int sum = arr[left] + arr[right];
        if (sum == target) { found = true; break; }
        else if (sum < target) left++;
        else right--;
    }
    assert(found == true);
    std::cout << "TwoPointers found target." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## SlidingWindow()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    std::vector<int> arr = {2, 1, 5, 1, 3, 2};
    int target = 7;
    int windowSum = 0, start = 0, minLen = 1e9;
    for (int end = 0; end < (int)arr.size(); ++end) {
        windowSum += arr[end];
        while (windowSum >= target) {
            minLen = std::min(minLen, end - start + 1);
            windowSum -= arr[start];
            start++;
        }
    }
    assert(minLen == 3); // [2,1,5] 등 길이 3이 최소;
    std::cout << "SlidingWindow Min Length: " << minLen << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## PrefixSum()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {10, 20, 30, 40};
    std::vector<int> prefixSum(arr.size() + 1, 0);
    for (int i = 0; i < (int)arr.size(); ++i) {
        prefixSum[i + 1] = prefixSum[i] + arr[i];
    }
    int sum1to2 = prefixSum[3] - prefixSum[1];
    assert(sum1to2 == 50); // 20 + 30
    std::cout << "PrefixSum computed." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## DifferenceArray()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {0, 0, 0, 0};
    std::vector<int> diff(arr.size() + 1, 0);
    
    // Add 10 to range [1, 2]
    int start = 1, end = 2, value = 10;
    diff[start] += value;
    diff[end + 1] -= value;
    
    int current = 0;
    for (int i = 0; i < (int)arr.size(); ++i) {
        current += diff[i];
        arr[i] += current;
    }
    assert(arr[1] == 10 && arr[2] == 10 && arr[3] == 0);
    std::cout << "DifferenceArray applied." << std::endl;
    return 0;
}
// Time Complexity: O(1) update, O(N) build
// Space Complexity: O(N)
```

# Part 6. 연결리스트 심화
## DummyNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* head = new Node{10, nullptr};
    Node* dummy = new Node{0, head};
    Node* curr = dummy;
    curr->next = curr->next->next; // Removes head safely
    delete head;
    
    assert(dummy->next == nullptr);
    std::cout << "DummyNode used safely." << std::endl;
    delete dummy;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SentinelNode()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <list>
#include <random>
#include <vector>
#include <cassert>

// 센티넬 노드(Sentinel Node): 경계 조건을 처리하는 특수 코드를 없애려고 데이터가 아닌 "경계 표지" 노드를 리스트 양 끝(또는 원형으로 하나)에 두는 기법이다.
// 널 검사 방식의 이중 연결 리스트는 삽입·삭제마다 "앞 노드가 없나? 뒤 노드가 없나? 리스트가 비었나?" 를 따져 head/tail 을 고쳐야 한다(특수 경우 4 가지 이상). 센티넬 하나를 가진 원형 리스트에서는 모든 노드가 항상 prev 와 next 를 가지므로 삽입은 4 줄, 삭제는 2 줄로 분기가 없다.
// 같은 발상이 탐색에도 쓰인다: 배열 끝에 찾는 값 자체를 센티넬로 심어 두면 반복마다 "범위를 벗어났나?" 비교가 필요 없어져 비교 횟수가 (2k+1) 에서 (k+1) 로 줄어든다(찾으면 인덱스가 n 미만인지만 검사).
// 검증: ① 무작위 앞/뒤/가운데 삽입·삭제에서 널 검사 방식, 센티넬 방식, std::list 의 내용이 항상 같다 ② 널 검사 방식에서 실제로 실행된 특수 경우 분기 횟수를 센다(센티넬 방식은 분기 자체가 없다) ③ 센티넬 선형 탐색의 비교 횟수가 일반 탐색의 절반 정도
struct Node { int val; Node *prev, *next; };
struct NullList {                                                          // 센티넬 없음: head/tail 이 널일 수 있다
    Node *head = nullptr, *tail = nullptr; size_t n = 0; long specialCases = 0;
    Node* insertBefore(Node* pos, int v) {                                  // pos == nullptr 이면 맨 뒤
        Node* x = new Node{v, pos ? pos->prev : tail, pos}; n++;
        if (x->prev) x->prev->next = x; else { head = x; specialCases++; }
        if (x->next) x->next->prev = x; else { tail = x; specialCases++; }
        return x;
    }
    void erase(Node* x) { if (x->prev) x->prev->next = x->next; else { head = x->next; specialCases++; } if (x->next) x->next->prev = x->prev; else { tail = x->prev; specialCases++; } delete x; n--; }
    ~NullList() { while (head) { Node* x = head->next; delete head; head = x; } }
};
struct SentinelList {                                                      // 센티넬 하나가 head 이자 tail 이다 (원형)
    Node* s; size_t n = 0;
    SentinelList() { s = new Node{0, nullptr, nullptr}; s->prev = s->next = s; }
    Node* insertBefore(Node* pos, int v) { Node* x = new Node{v, pos->prev, pos}; pos->prev->next = x; pos->prev = x; n++; return x; }          // 분기 없음. pos == s 이면 맨 뒤
    void erase(Node* x) { x->prev->next = x->next; x->next->prev = x->prev; delete x; n--; }
    ~SentinelList() { Node* x = s->next; while (x != s) { Node* nx = x->next; delete x; x = nx; } delete s; }
};
long plainCompares = 0, sentinelCompares = 0;
int searchPlain(const std::vector<int>& a, int x) { for (size_t i = 0; i < a.size(); i++) { plainCompares += 2; if (a[i] == x) return (int)i; } plainCompares++; return -1; }              // 반복마다 "범위" 와 "값" 두 번 비교
int searchSentinel(std::vector<int>& a, int x) { int last = a.back(); a.back() = x; size_t i = 0; while (a[i] != x) { sentinelCompares++; i++; } sentinelCompares++; a.back() = last; if (i + 1 < a.size() || last == x) return (int)i; return -1; }  // 끝에 x 를 심어 범위 비교 생략
int main() {
    std::mt19937 rng(2); NullList a; SentinelList b; std::list<int> ref; std::vector<Node*> na, nb;
    for (int step = 0; step < 20000; step++) {
        int op = rng() % 4; size_t n = ref.size();
        if (op < 2 || n == 0) { size_t i = rng() % (n + 1); int v = rng() % 1000; Node* pa = i == n ? nullptr : na[i]; Node* pb = i == n ? b.s : nb[i]; na.insert(na.begin() + i, a.insertBefore(pa, v)); nb.insert(nb.begin() + i, b.insertBefore(pb, v)); auto it = ref.begin(); std::advance(it, i); ref.insert(it, v); }
        else { size_t i = rng() % n; a.erase(na[i]); b.erase(nb[i]); na.erase(na.begin() + i); nb.erase(nb.begin() + i); auto it = ref.begin(); std::advance(it, i); ref.erase(it); }
        if (step % 500 == 0) { std::vector<int> va, vb, vr(ref.begin(), ref.end()); for (Node* x = a.head; x; x = x->next) va.push_back(x->val); for (Node* x = b.s->next; x != b.s; x = x->next) vb.push_back(x->val); assert(va == vr && vb == vr && a.n == vr.size() && b.n == vr.size());
            std::vector<int> back; for (Node* x = b.s->prev; x != b.s; x = x->prev) back.push_back(x->val); std::reverse(back.begin(), back.end()); assert(back == vr); }                            // 거꾸로 순회도 일관적
    }
    assert(a.specialCases > 1000);                                         // ② 널 검사 방식은 경계 분기를 많이 탔다
    std::vector<int> data(1000); for (int& x : data) x = rng() % 5000; long found = 0;
    for (int q = 0; q < 2000; q++) { int x = rng() % 5000; std::vector<int> copy = data; int p1 = searchPlain(data, x), p2 = searchSentinel(copy, x); assert(p1 == p2 && copy == data); found += p1 >= 0; }                           // ③
    assert(sentinelCompares * 10 < plainCompares * 6);
    std::cout << "SentinelNode: three lists agreed after 20000 mixed operations; the null-checking list took " << a.specialCases << " boundary branches, the sentinel list none; linear search needed " << sentinelCompares << " comparisons with a sentinel vs " << plainCompares << " without (" << found << " hits)" << std::endl; return 0;
}
// Time Complexity: 삽입·삭제 O(1) (분기 없음), 센티넬 탐색 O(N) (비교 횟수 절반)
// Space Complexity: 센티넬 노드 1 개 추가
```
## CircularList()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* tail = new Node{10, nullptr};
    tail->next = tail; // Circular link
    assert(tail->next == tail);
    std::cout << "CircularList created." << std::endl;
    delete tail;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DoublyLinkedList()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* prev; Node* next; };

int main() {
    Node* n1 = new Node{10, nullptr, nullptr};
    Node* n2 = new Node{20, n1, nullptr};
    n1->next = n2;
    assert(n2->prev->data == 10);
    std::cout << "DoublyLinkedList connected." << std::endl;
    delete n1; delete n2;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## XORLinkedList()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <deque>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// XOR 연결 리스트: 이중 연결 리스트에서 prev 와 next 포인터 두 개를 저장하는 대신 두 주소의 XOR 하나만 저장한다 — link = prev ^ next. 한쪽 이웃의 주소를 알고 있으면 다른 쪽을 복원할 수 있다(next = link ^ prev, prev = link ^ next).
// 그래서 순회는 "(방금 지나온 노드, 현재 노드)" 쌍을 들고 다니며, 앞으로도 뒤로도 같은 코드로 갈 수 있다. 덕분에 리스트 뒤집기가 head 와 tail 을 맞바꾸는 O(1) 이다.
// 대가: 메모리는 노드당 포인터 하나를 아끼지만(여기서는 24 바이트 -> 16 바이트) 디버깅이 어렵고, 가비지 컬렉터·누수 검사기·스마트 포인터가 숨겨진 포인터를 못 보며, 이웃을 알려면 항상 어느 쪽에서 왔는지를 알아야 하므로 노드 하나만 가리키는 반복자로는 이웃으로 갈 수 없다(커서가 두 주소를 들어야 한다).
// 검증: ① 무작위 앞/뒤 삽입, 위치 삽입, 위치 삭제, O(1) 뒤집기를 std::deque 모델과 대조 ② 앞→뒤, 뒤→앞 순회가 서로 정확한 역순 ③ 노드 크기가 이중 연결 노드의 2/3 ④ 뒤집기 뒤 같은 코드로 순회한 결과가 역순
struct XNode { long long val; uintptr_t link; };
struct DNode { long long val; DNode *prev, *next; };
inline uintptr_t U(const XNode* p) { return reinterpret_cast<uintptr_t>(p); }
inline XNode* P(uintptr_t a) { return reinterpret_cast<XNode*>(a); }
struct Cursor { XNode *prev, *cur; };                                         // 순회 위치: (지나온 노드, 현재 노드)
struct XList {
    XNode *head = nullptr, *tail = nullptr; size_t n = 0;
    void pushBack(long long v) { XNode* x = new XNode{v, U(tail)}; if (tail) tail->link ^= U(x); else head = x; tail = x; n++; }             // tail 의 next 는 0 이었으므로 XOR 하면 next = x 가 된다
    void pushFront(long long v) { XNode* x = new XNode{v, U(head)}; if (head) head->link ^= U(x); else tail = x; head = x; n++; }
    Cursor begin() const { return {nullptr, head}; } Cursor rbegin() const { return {nullptr, tail}; }
    static Cursor advance(Cursor c) { XNode* next = P(U(c.prev) ^ c.cur->link); return {c.cur, next}; }                                             // 앞으로든 뒤로든 같은 코드
    Cursor at(size_t i) const { Cursor c = begin(); while (i--) c = advance(c); return c; }
    void insertAfter(Cursor c, long long v) {                                  // c.cur 바로 뒤에 삽입
        XNode* next = P(U(c.prev) ^ c.cur->link); XNode* x = new XNode{v, U(c.cur) ^ U(next)}; c.cur->link ^= U(next) ^ U(x); if (next) next->link ^= U(c.cur) ^ U(x); else tail = x; n++;
    }
    void erase(Cursor c) {                                                     // c.cur 삭제
        XNode *prev = c.prev, *next = P(U(c.prev) ^ c.cur->link);
        if (prev) prev->link ^= U(c.cur) ^ U(next); else head = next;
        if (next) next->link ^= U(c.cur) ^ U(prev); else tail = prev;
        delete c.cur; n--;
    }
    void reverse() { std::swap(head, tail); }                                  // O(1): 링크는 방향이 없다
    std::vector<long long> toVector(bool backward = false) const { std::vector<long long> v; for (Cursor c = backward ? rbegin() : begin(); c.cur; c = advance(c)) v.push_back(c.cur->val); return v; }
    ~XList() { Cursor c = begin(); while (c.cur) { Cursor nx = advance(c); delete c.cur; c = nx; } }
};
int main() {
    std::mt19937 rng(6); XList l; std::deque<long long> model; int reversals = 0;
    for (int step = 0; step < 30000; step++) {
        int op = rng() % 6; size_t n = model.size(); long long v = rng() % 100000;
        if (op == 0) { l.pushBack(v); model.push_back(v); }
        else if (op == 1) { l.pushFront(v); model.push_front(v); }
        else if (op == 2 && n) { size_t i = rng() % n; l.insertAfter(l.at(i), v); model.insert(model.begin() + i + 1, v); }
        else if (op == 3 && n) { size_t i = rng() % n; l.erase(l.at(i)); model.erase(model.begin() + i); }
        else if (op == 4 && step % 50 == 0) { l.reverse(); std::reverse(model.begin(), model.end()); reversals++; }
        if (l.n > 400 && n) { l.erase(l.at(0)); model.pop_front(); }
        if (step % 200 == 0) { std::vector<long long> fw = l.toVector(), bw = l.toVector(true), m(model.begin(), model.end()); assert(fw == m && l.n == m.size()); std::reverse(bw.begin(), bw.end()); assert(bw == m); }              // ① ②
    }
    std::vector<long long> before = l.toVector(); l.reverse(); std::vector<long long> after = l.toVector(); std::reverse(after.begin(), after.end()); assert(before == after);                                           // ④
    assert(sizeof(XNode) * 3 == sizeof(DNode) * 2);                                                                                                                                                          // ③ 16 바이트 vs 24 바이트
    std::cout << "XORLinkedList: " << model.size() << " elements matched the deque model after 30000 operations (" << reversals << " O(1) reversals); node size " << sizeof(XNode) << " bytes vs " << sizeof(DNode) << " for a doubly linked node" << std::endl; return 0;
}
// Time Complexity: 순회 O(1)/단계, 위치 삽입·삭제 O(1) (커서가 있을 때), 뒤집기 O(1)
// Space Complexity: 노드당 포인터 크기 1 개
```

# Part 7. 반복자
## Iterator()
### 대표코드
```cpp
#include <algorithm>
#include <forward_list>
#include <iostream>
#include <iterator>
#include <list>
#include <numeric>
#include <random>
#include <sstream>
#include <type_traits>
#include <vector>
#include <cassert>

// 반복자(Iterator): 컨테이너의 내부 구조를 숨긴 채 "다음 원소로 가라, 값을 읽어라" 만 노출하는 추상화다. 알고리즘(std::find, std::reverse …)이 컨테이너 종류에 상관없이 반복자 쌍 [first, last) 하나로 일하게 만드는 접착제다.
// 반복자는 할 수 있는 일의 범위에 따라 계층을 이룬다: 입력(한 번 읽기) ⊂ 순방향(여러 번 순회) ⊂ 양방향(-- 가능, 연결 리스트) ⊂ 임의 접근(+n, 거리 O(1), 배열). 알고리즘은 요구하는 범주를 명시한다 — std::reverse 는 양방향이면 되지만 std::sort 는 임의 접근이 필요하다.
// 직접 만든 이중 연결 리스트의 반복자가 이 요구(5 개 타입 정의 + 증감·비교·역참조)를 채우면 표준 알고리즘을 그대로 쓸 수 있고, const 반복자는 비const 반복자에서 암묵 변환된다.
// 검증: ① 표준 컨테이너별 반복자 범주 ② 직접 만든 리스트에서 find/count_if/accumulate/reverse/rotate/unique/partition/stable_partition/inplace_merge/is_sorted/lower_bound/distance/next/prev/copy/역방향 반복자/범위 for 가 vector 결과와 같다 ③ 삽입이 다른 반복자를 무효화하지 않음 ④ 삭제는 지운 원소의 반복자만 무효화
template <class T> struct DList {
    struct Node { T val; Node *prev, *next; };
    Node* s; size_t n = 0;
    template <bool Const> struct Iter {
        typedef std::bidirectional_iterator_tag iterator_category; typedef T value_type; typedef std::ptrdiff_t difference_type;
        typedef typename std::conditional<Const, const T*, T*>::type pointer; typedef typename std::conditional<Const, const T&, T&>::type reference;
        Node* p = nullptr; Iter() {} explicit Iter(Node* q) : p(q) {}
        template <bool C2, class = typename std::enable_if<Const && !C2>::type> Iter(const Iter<C2>& o) : p(o.p) {}              // iterator -> const_iterator 변환
        reference operator*() const { return p->val; } pointer operator->() const { return &p->val; }
        Iter& operator++() { p = p->next; return *this; } Iter operator++(int) { Iter t = *this; p = p->next; return t; }
        Iter& operator--() { p = p->prev; return *this; } Iter operator--(int) { Iter t = *this; p = p->prev; return t; }
        friend bool operator==(const Iter& a, const Iter& b) { return a.p == b.p; } friend bool operator!=(const Iter& a, const Iter& b) { return a.p != b.p; }
    };
    typedef Iter<false> iterator; typedef Iter<true> const_iterator;
    DList() { s = new Node{T(), nullptr, nullptr}; s->prev = s->next = s; }
    DList(const DList&) = delete; DList& operator=(const DList&) = delete;
    ~DList() { Node* x = s->next; while (x != s) { Node* nx = x->next; delete x; x = nx; } delete s; }
    iterator begin() { return iterator(s->next); } iterator end() { return iterator(s); } const_iterator begin() const { return const_iterator(s->next); } const_iterator end() const { return const_iterator(s); }
    iterator insert(const_iterator pos, const T& v) { Node* nx = pos.p; Node* x = new Node{v, nx->prev, nx}; nx->prev->next = x; nx->prev = x; n++; return iterator(x); }
    iterator erase(const_iterator pos) { Node* x = pos.p; Node* nx = x->next; x->prev->next = nx; nx->prev = x->prev; delete x; n--; return iterator(nx); }
    void push_back(const T& v) { insert(end(), v); }
    size_t size() const { return n; }
};
template <class It> const char* category() { typedef typename std::iterator_traits<It>::iterator_category C; return std::is_base_of<std::random_access_iterator_tag, C>::value ? "random" : std::is_base_of<std::bidirectional_iterator_tag, C>::value ? "bidirectional" : std::is_base_of<std::forward_iterator_tag, C>::value ? "forward" : std::is_base_of<std::input_iterator_tag, C>::value ? "input" : "output"; }
template <class C> std::vector<int> toVec(const C& c) { return std::vector<int>(c.begin(), c.end()); }
int main() {
    std::string cats = std::string(category<std::vector<int>::iterator>()) + "," + category<std::list<int>::iterator>() + "," + category<std::forward_list<int>::iterator>() + "," + category<std::istream_iterator<int>>() + "," + category<DList<int>::iterator>();
    assert(cats == "random,bidirectional,forward,input,bidirectional");                                                                                       // ①
    std::mt19937 rng(8);
    for (int t = 0; t < 300; t++) {
        int n = rng() % 40; std::vector<int> v(n); for (int& x : v) x = rng() % 10; DList<int> l; for (int x : v) l.push_back(x); assert(toVec(l) == v && (int)std::distance(l.begin(), l.end()) == n);
        int key = rng() % 10; assert((std::find(l.begin(), l.end(), key) == l.end()) == (std::find(v.begin(), v.end(), key) == v.end()));
        assert(std::count_if(l.begin(), l.end(), [](int x) { return x % 2 == 0; }) == std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; }) && std::accumulate(l.begin(), l.end(), 0) == std::accumulate(v.begin(), v.end(), 0));
        const DList<int>& cl = l; std::vector<int> viaConst(cl.begin(), cl.end()); assert(viaConst == v); DList<int>::const_iterator ci = l.begin(); assert(ci == cl.begin());                       // const 변환
        std::vector<int> rv(l.begin(), l.end()); std::reverse(rv.begin(), rv.end()); std::reverse(l.begin(), l.end()); assert(toVec(l) == rv); std::vector<int> rev2(std::reverse_iterator<DList<int>::iterator>(l.end()), std::reverse_iterator<DList<int>::iterator>(l.begin())); std::reverse(rev2.begin(), rev2.end()); assert(rev2 == rv);
        v = rv; if (n) { int k = rng() % n; std::rotate(l.begin(), std::next(l.begin(), k), l.end()); std::rotate(v.begin(), v.begin() + k, v.end()); assert(toVec(l) == v); }
        auto lu = std::unique(l.begin(), l.end()); auto vu = std::unique(v.begin(), v.end()); assert(std::distance(l.begin(), lu) == std::distance(v.begin(), vu) && std::equal(l.begin(), lu, v.begin()));
        v.assign(l.begin(), l.end()); auto pred = [](int x) { return x < 5; }; auto lp = std::stable_partition(l.begin(), l.end(), pred); auto vp = std::stable_partition(v.begin(), v.end(), pred); assert(toVec(l) == v && std::distance(l.begin(), lp) == std::distance(v.begin(), vp));
        std::sort(v.begin(), v.end()); DList<int> sorted; for (int x : v) sorted.push_back(x); assert(std::is_sorted(sorted.begin(), sorted.end())); int target = rng() % 10; assert(std::distance(sorted.begin(), std::lower_bound(sorted.begin(), sorted.end(), target)) == std::lower_bound(v.begin(), v.end(), target) - v.begin());         // ②
        std::vector<int> copied; std::copy(sorted.begin(), sorted.end(), std::back_inserter(copied)); assert(copied == v); std::vector<int> viaFor; for (int x : sorted) viaFor.push_back(x); assert(viaFor == v);
    }
    DList<int> l; for (int i = 0; i < 6; i++) l.push_back(i * 10); auto it1 = std::next(l.begin(), 1), it4 = std::next(l.begin(), 4); auto ins = l.insert(it4, 35); assert(*it1 == 10 && *it4 == 40 && *ins == 35 && *std::prev(it4) == 35);          // ③ 삽입은 다른 반복자를 유지
    auto after = l.erase(it1); assert(*after == 20 && *it4 == 40 && toVec(l) == (std::vector<int>{0, 20, 30, 35, 40, 50}));                                                                             // ④ 삭제는 지운 것만 무효화
    std::cout << "Iterator: categories " << cats << "; a hand-written bidirectional iterator worked with 20+ standard algorithms on 300 random lists and matched vector results" << std::endl; return 0;
}
// Time Complexity: 증감·역참조 O(1), std::distance 는 양방향에서 O(N)
// Space Complexity: O(1) 반복자
```
## Begin()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {10, 20};
    auto it = lst.begin();
    assert(*it == 10);
    std::cout << "Begin() tested." << std::endl;
    return 0;
}
// Time Complexity: O(1)
```
## End()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <cassert>

int main() {
    std::list<int> lst = {10};
    auto it = lst.end();
    assert(it != lst.begin());
    std::cout << "End() tested." << std::endl;
    return 0;
}
// Time Complexity: O(1)
```
## Next()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <iterator>
#include <cassert>

int main() {
    std::list<int> lst = {10, 20, 30};
    auto next_it = std::next(lst.begin(), 1);
    assert(*next_it == 20);
    std::cout << "std::next() tested." << std::endl;
    return 0;
}
// Time Complexity: O(1) for random access, O(N) for list
```
## Prev()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <iterator>
#include <cassert>

int main() {
    std::list<int> lst = {10, 20, 30};
    auto prev_it = std::prev(lst.end(), 1);
    assert(*prev_it == 30);
    std::cout << "std::prev() tested." << std::endl;
    return 0;
}
// Time Complexity: O(1) or O(N)
```

# Part 8. 메모리
## ShallowCopy()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; };

int main() {
    Node* lst1 = new Node{10};
    Node* lst2 = lst1; // Shallow copy
    lst2->data = 20;
    assert(lst1->data == 20);
    std::cout << "Shallow Copy observed." << std::endl;
    delete lst1;
    return 0;
}
// Time/Space: O(1)
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## DeepCopy()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

int main() {
    Node* lst1 = new Node{10, nullptr};
    Node* lst2 = new Node{lst1->data, nullptr}; // Deep Copy
    lst2->data = 20;
    assert(lst1->data == 10);
    std::cout << "Deep Copy observed." << std::endl;
    delete lst1; delete lst2;
    return 0;
}
// Time/Space: O(N)
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## Move()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <utility>
#include <cassert>

int main() {
    std::list<int> lst1 = {1, 2, 3};
    std::list<int> lst2 = std::move(lst1);
    assert(lst1.empty() && lst2.size() == 3);
    std::cout << "Move Semantics observed." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Alloc()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    int* arr = new int[5];
    arr[0] = 10;
    assert(arr[0] == 10);
    std::cout << "Alloc new[] verified." << std::endl;
    delete[] arr;
    return 0;
}
// Time Complexity: O(1)
```
## Free()
### 대표코드
```cpp
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// Free(): 빌린 메모리를 돌려주는 연산. 잘못 쓰면 이중 해제(double free), 해제 뒤 사용(use-after-free), 해제 안 함(누수)이 생기고 모두 정의되지 않은 동작이거나 보안 취약점이다.
// 고정 크기 블록 풀(pool)은 해제를 O(1) 로 만든다: 해제된 블록을 자유 리스트(free list)의 맨 앞에 끼우기만 하면 되고 다음 할당이 그 블록을 그대로 재사용한다(LIFO — 캐시에 데운 블록이 먼저 쓰인다).
// 풀이 오류를 잡는 법: 핸들을 (인덱스, 세대 번호) 로 만들고, 해제할 때마다 슬롯의 세대 번호를 올리면 ① 같은 핸들을 두 번 해제하면 세대가 달라 이중 해제로 탐지되고 ② 해제된 핸들로 접근하면 포인터를 주지 않고 ③ 슬롯이 이미 다른 용도로 재할당된 뒤의 옛 핸들(ABA)도 구별된다. 해제할 때 내용을 0xDD 로 덮어 쓰면 해제 뒤 읽기가 눈에 띈다. 끝에 남은 생존 블록 수가 곧 누수 보고다.
// 검증: ① 무작위 할당·해제를 기준 모델(map)과 대조 ② 이중 해제·가짜 핸들·옛 핸들 접근이 모두 탐지 ③ 해제 순서의 역순으로 재할당(LIFO) ④ 해제 시 독약 값 ⑤ 생존 블록 수 == 모델 크기(누수 보고)
class Pool {
public:
    struct Handle { uint32_t index, gen; };
    enum Result { OK, DOUBLE_FREE, INVALID };
    explicit Pool(size_t n) : slots_(n) { for (size_t i = 0; i < n; i++) { slots_[i].next = (int)i + 1 < (int)n ? (int)i + 1 : -1; } freeHead_ = n ? 0 : -1; }
    bool alloc(Handle& h) { if (freeHead_ < 0) return false; Slot& s = slots_[freeHead_]; h = {(uint32_t)freeHead_, s.gen}; freeHead_ = s.next; s.used = true; std::memset(s.data, 0, sizeof s.data); live_++; return true; }
    Result free(Handle h) {
        if (h.index >= slots_.size()) return INVALID; Slot& s = slots_[h.index]; if (!s.used || s.gen != h.gen) return DOUBLE_FREE;      // 이미 해제된 블록(또는 옛 핸들)
        std::memset(s.data, 0xDD, sizeof s.data); s.used = false; s.gen++; s.next = freeHead_; freeHead_ = (int)h.index; live_--; return OK;
    }
    void* get(Handle h) { if (h.index >= slots_.size()) return nullptr; Slot& s = slots_[h.index]; return s.used && s.gen == h.gen ? s.data : nullptr; }              // 옛 핸들은 nullptr
    const unsigned char* rawPeek(uint32_t index) const { return reinterpret_cast<const unsigned char*>(slots_[index].data); }                                                // 디버거 역할
    size_t live() const { return live_; }
private:
    struct Slot { alignas(8) char data[24]; uint32_t gen = 0; bool used = false; int next = -1; };
    std::vector<Slot> slots_; int freeHead_; size_t live_ = 0;
};
int main() {
    Pool pool(64); std::mt19937 rng(9); std::map<std::pair<uint32_t, uint32_t>, int> model; auto key = [](Pool::Handle h) { return std::make_pair(h.index, h.gen); }; std::vector<Pool::Handle> handles, stale; long doubleFrees = 0, staleReads = 0;
    for (int step = 0; step < 20000; step++) {
        if (rng() % 2 || handles.empty()) { Pool::Handle h; if (pool.alloc(h)) { int tag = rng(); *(int*)pool.get(h) = tag; model[key(h)] = tag; handles.push_back(h); } else assert(model.size() == 64); }
        else { size_t i = rng() % handles.size(); Pool::Handle h = handles[i]; assert(*(int*)pool.get(h) == model[key(h)]); Pool::Result r = pool.free(h); assert(r == Pool::OK); model.erase(key(h)); handles.erase(handles.begin() + i); stale.push_back(h); if (stale.size() > 50) stale.erase(stale.begin());          // ①
            Pool::Result again = pool.free(h); assert(pool.get(h) == nullptr && again == Pool::DOUBLE_FREE); doubleFrees++; }                                                                                                                                       // ② 해제 직후 접근·재해제 탐지
        if (step % 100 == 0) for (auto& h : stale) { if (pool.get(h) != nullptr) assert(false); staleReads++; }                                                                                                                        // 재할당된 슬롯의 옛 핸들도 구별
        assert(pool.live() == model.size());
    }
    Pool::Result bogus = pool.free({9999, 0}); assert(bogus == Pool::INVALID);
    Pool p2(8); std::vector<Pool::Handle> hs(8); for (auto& h : hs) { bool ok = p2.alloc(h); assert(ok); } std::vector<int> order = {5, 2, 7, 0, 3}; for (int i : order) { Pool::Result r = p2.free(hs[i]); assert(r == Pool::OK); }
    for (size_t k = 0; k < order.size(); k++) { Pool::Handle h; bool ok = p2.alloc(h); assert(ok && (int)h.index == order[order.size() - 1 - k]); }                                                                                              // ③ LIFO 재사용
    Pool p3(4); Pool::Handle h; bool ok3 = p3.alloc(h); assert(ok3); uint32_t idx = h.index; Pool::Result r3 = p3.free(h); assert(r3 == Pool::OK); for (int i = 0; i < 24; i++) assert(p3.rawPeek(idx)[i] == 0xDD);                                                           // ④ 독약 값
    assert(p3.live() == 0); Pool::Handle a, b; p3.alloc(a); p3.alloc(b); assert(p3.live() == 2);                                                                                                                                       // ⑤ 누수 보고 = 생존 블록 수
    std::cout << "Free: pool matched the model for 20000 operations; " << doubleFrees << " double frees and " << staleReads << " stale-handle reads were all detected; reallocation was LIFO; " << pool.live() << " blocks still live at the end (leak report)" << std::endl; return 0;
}
// Time Complexity: alloc·free 모두 O(1)
// Space Complexity: O(블록 수), 블록당 세대 번호·플래그 오버헤드
```
## GarbageCollection()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <cassert>

struct Node { int data; };

int main() {
    std::shared_ptr<Node> head = std::make_shared<Node>();
    head->data = 100;
    assert(head.use_count() == 1);
    std::cout << "Shared Ptr Garbage Collection verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) overhead
```

# Part 9. 함수형 리스트
## Map()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <algorithm>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3};
    std::transform(lst.begin(), lst.end(), lst.begin(), [](int x) { return x * 2; });
    assert(lst.front() == 2);
    std::cout << "Map / Transform verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
```
## Filter()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <algorithm>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3, 4};
    auto it = std::remove_if(lst.begin(), lst.end(), [](int x) { return x % 2 != 0; });
    lst.erase(it, lst.end());
    assert(lst.size() == 2 && lst.front() == 2);
    std::cout << "Filter verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
```
## Reduce()
### 대표코드
```cpp
#include <iostream>
#include <list>
#include <numeric>
#include <cassert>

int main() {
    std::list<int> lst = {1, 2, 3, 4};
    int sum = std::accumulate(lst.begin(), lst.end(), 0);
    assert(sum == 10);
    std::cout << "Reduce / Accumulate verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
```
## Zip()
### 대표코드
```cpp
#include <iostream>
#include <iterator>
#include <list>
#include <random>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// Zip: 두 리스트를 나란히 놓고 같은 위치끼리 짝지어 하나의 (쌍)리스트로 만든다 — zip([1,2,3],[a,b,c]) = [(1,a),(2,b),(3,c)]. 길이가 다르면 짧은 쪽에서 끝낸다. 두 시퀀스를 동시에 훑는 루프(내적, 인접 차분, 인덱스 붙이기)를 인덱스 없이 쓰게 해 준다.
// 변종: zipWith(f) 는 짝을 바로 함수에 넣고, zip3 는 세 리스트, unzip 은 쌍리스트를 두 리스트로 되돌리며, zipLongest 는 짧은 쪽을 기본값으로 채워 긴 쪽 길이까지 간다. "게으른 zip" 은 쌍을 만들어 저장하지 않고 두 반복자를 함께 전진시키는 뷰로 O(1) 메모리다.
// 성질: |zip(a,b)| = min(|a|,|b|), unzip(zip(a,b)) = (a 의 앞 k 개, b 의 앞 k 개) (k = min 길이), zip(a, tail(a)) 의 각 쌍이 인접 원소 쌍이다.
// 검증: ① 길이·내용·unzip 항등식 ② 게으른 뷰 == 즉시 zip, std::list 와 vector 를 섞어도 동작 ③ zipWith 로 내적·인접 차분·enumerate ④ zipLongest 의 길이와 채움값 ⑤ 세 리스트 zip3
template <class A, class B> auto zip(const A& a, const B& b) { std::vector<std::pair<typename A::value_type, typename B::value_type>> out; auto i = a.begin(); auto j = b.begin(); for (; i != a.end() && j != b.end(); ++i, ++j) out.push_back({*i, *j}); return out; }
template <class A, class B, class F> auto zipWith(const A& a, const B& b, F f) { std::vector<decltype(f(*a.begin(), *b.begin()))> out; auto i = a.begin(); auto j = b.begin(); for (; i != a.end() && j != b.end(); ++i, ++j) out.push_back(f(*i, *j)); return out; }
template <class A, class B> auto zipLongest(const A& a, const B& b, typename A::value_type da, typename B::value_type db) { std::vector<std::pair<typename A::value_type, typename B::value_type>> out; auto i = a.begin(); auto j = b.begin(); while (i != a.end() || j != b.end()) { out.push_back({i != a.end() ? *i : da, j != b.end() ? *j : db}); if (i != a.end()) ++i; if (j != b.end()) ++j; } return out; }
template <class A, class B, class C> auto zip3(const A& a, const B& b, const C& c) { std::vector<std::tuple<typename A::value_type, typename B::value_type, typename C::value_type>> out; auto i = a.begin(); auto j = b.begin(); auto k = c.begin(); for (; i != a.end() && j != b.end() && k != c.end(); ++i, ++j, ++k) out.push_back(std::make_tuple(*i, *j, *k)); return out; }
template <class P> auto unzip(const std::vector<P>& ps) { std::vector<typename P::first_type> xs; std::vector<typename P::second_type> ys; for (auto& p : ps) { xs.push_back(p.first); ys.push_back(p.second); } return std::make_pair(xs, ys); }
template <class A, class B> struct ZipView {                                   // 게으른 zip: 복사 없이 두 반복자를 함께 전진
    const A& a; const B& b;
    struct It { typename A::const_iterator i; typename B::const_iterator j; std::pair<typename A::value_type, typename B::value_type> operator*() const { return {*i, *j}; } It& operator++() { ++i; ++j; return *this; } bool operator!=(const It& o) const { return i != o.i && j != o.j; } };    // 어느 한쪽이 끝나면 종료
    It begin() const { return {a.begin(), b.begin()}; } It end() const { return {a.end(), b.end()}; }
};
template <class A, class B> ZipView<A, B> lazyZip(const A& a, const B& b) { return {a, b}; }
int main() {
    std::mt19937 rng(4);
    for (int t = 0; t < 500; t++) {
        std::vector<int> a(rng() % 12); std::list<std::string> b; for (int& x : a) x = rng() % 100; int nb = rng() % 12; for (int i = 0; i < nb; i++) b.push_back(std::string(1, 'a' + rng() % 26)); size_t k = std::min(a.size(), b.size());
        auto z = zip(a, b); assert(z.size() == k); auto bi = b.begin(); for (size_t i = 0; i < k; i++, ++bi) assert(z[i].first == a[i] && z[i].second == *bi);                       // ① 길이·내용
        auto u = unzip(z); assert(u.first == std::vector<int>(a.begin(), a.begin() + k) && u.second == std::vector<std::string>(b.begin(), std::next(b.begin(), k)));       // unzip(zip) 항등
        std::vector<std::pair<int, std::string>> lazy; for (auto p : lazyZip(a, b)) lazy.push_back(p); assert(lazy == z);                                                           // ② 게으른 뷰 == 즉시 zip
        auto zl = zipLongest(a, b, -1, std::string("?")); assert(zl.size() == std::max(a.size(), b.size())); for (size_t i = k; i < zl.size(); i++) assert(i >= a.size() ? zl[i].first == -1 : zl[i].second == "?");        // ④
        auto z3 = zip3(a, a, b); assert(z3.size() == k);                                                                                                                           // ⑤
        if (a.size() >= 2) { std::vector<int> tail(a.begin() + 1, a.end()); auto diffs = zipWith(a, tail, [](int x, int y) { return y - x; }); assert(diffs.size() == a.size() - 1); for (size_t i = 0; i < diffs.size(); i++) assert(diffs[i] == a[i + 1] - a[i]); }     // ③ 인접 차분
        auto dot = zipWith(a, a, [](int x, int y) { return x * y; }); long long d1 = 0, d2 = 0; for (int v : dot) d1 += v; for (int v : a) d2 += (long long)v * v; assert(d1 == d2);
        std::vector<int> idx(a.size()); for (size_t i = 0; i < idx.size(); i++) idx[i] = (int)i; auto en = zip(idx, a); for (size_t i = 0; i < en.size(); i++) assert(en[i].first == (int)i && en[i].second == a[i]);                   // enumerate = zip(0.., a)
    }
    std::cout << "Zip: eager, lazy, zipLongest, zip3, zipWith and unzip agreed on 500 random list pairs of unequal length" << std::endl; return 0;
}
// Time Complexity: O(min(N, M)) (zipLongest 는 O(max(N, M)))
// Space Complexity: 즉시 zip O(min(N, M)), 게으른 zip O(1)
```
## Flatten()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<std::vector<int>> nested = {{1,2}, {3,4}};
    std::vector<int> flat;
    for (auto& v : nested) flat.insert(flat.end(), v.begin(), v.end());
    assert(flat.size() == 4);
    std::cout << "Flatten verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
```

# Part 10. 학사과정을 넘어
## SkipList()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 스킵 리스트(Pugh 1990): 정렬된 연결 리스트 위에 "급행 노선" 을 확률적으로 쌓아 탐색을 기대 O(log N) 으로 만든다. 모든 노드는 최하층(전 구간)에 있고, 동전을 던져 앞면이 나오는 만큼(확률 1/2) 위층에도 올라간다 — 층 k 는 층 k−1 의 원소를 대략 절반만 가진 부분열이다.
// 탐색은 맨 위층에서 오른쪽으로 가다가 다음 값이 목표보다 크면 한 층 내려오기를 반복한다. 균형 이진 트리처럼 회전·재균형이 없고 삽입·삭제는 지나온 각 층의 앞 노드만 고치면 되어 구현이 간단하며, 락프리/동시성 확장이 쉬워 LevelDB·RocksDB 의 memtable, Redis 의 정렬 집합에 쓰인다.
// 이 구현은 각 간격(span; 층 i 의 링크가 건너뛰는 최하층 칸 수)을 함께 저장해 순위(rank)와 k 번째 원소(select)도 O(log N) 에 답한다 — Redis zset 과 같은 방식이다.
// 검증: ① std::set 과 삽입·삭제·검색·lower_bound·순위·k 번째가 같음 ② 구조 불변식: 모든 층이 정렬된 부분열이고 아래층의 부분집합이며 모든 링크의 span 이 실제 칸 수 ③ 정렬된 입력(ascending)에서도 평균 비교 수가 O(log N) ④ 층 높이 분포가 기하분포(높이 ≥ k 인 노드 비율 ≈ 2^−(k−1))이고 평균 포인터 수 ≈ 2
struct SkipList {
    static const int MAXL = 24;
    struct Node { int key; std::vector<Node*> next; std::vector<int> span; Node(int k, int h) : key(k), next(h, nullptr), span(h, 0) {} };
    Node* head; int level = 1; size_t n = 0; std::mt19937 rng; long comparisons = 0;
    explicit SkipList(unsigned seed = 1) : head(new Node(INT_MIN, MAXL)), rng(seed) {}
    SkipList(const SkipList&) = delete; SkipList& operator=(const SkipList&) = delete;
    ~SkipList() { Node* x = head; while (x) { Node* nx = x->next[0]; delete x; x = nx; } }
    int randomLevel() { int h = 1; while (h < MAXL && (rng() & 1)) h++; return h; }
    bool insert(int key) {
        Node* update[MAXL]; int rank[MAXL]; Node* x = head;
        for (int i = level - 1; i >= 0; i--) { rank[i] = i == level - 1 ? 0 : rank[i + 1]; while (x->next[i] && x->next[i]->key < key) { rank[i] += x->span[i]; x = x->next[i]; } update[i] = x; }
        if (x->next[0] && x->next[0]->key == key) return false;
        int h = randomLevel(); if (h > level) { for (int i = level; i < h; i++) { rank[i] = 0; update[i] = head; head->span[i] = (int)n; } level = h; }
        Node* node = new Node(key, h);
        for (int i = 0; i < h; i++) { node->next[i] = update[i]->next[i]; update[i]->next[i] = node; node->span[i] = update[i]->span[i] - (rank[0] - rank[i]); update[i]->span[i] = (rank[0] - rank[i]) + 1; }
        for (int i = h; i < level; i++) update[i]->span[i]++;                    // 새 노드 위를 건너뛰는 링크는 칸 수가 하나 늘어난다
        n++; return true;
    }
    bool erase(int key) {
        Node* update[MAXL]; Node* x = head; for (int i = level - 1; i >= 0; i--) { while (x->next[i] && x->next[i]->key < key) x = x->next[i]; update[i] = x; }
        Node* t = x->next[0]; if (!t || t->key != key) return false;
        for (int i = 0; i < level; i++) { if (update[i]->next[i] == t) { update[i]->span[i] += t->span[i] - 1; update[i]->next[i] = t->next[i]; } else update[i]->span[i]--; }
        delete t; while (level > 1 && !head->next[level - 1]) level--; n--; return true;
    }
    const Node* lowerBound(int key) {                                           // key 이상인 첫 노드
        Node* x = head; for (int i = level - 1; i >= 0; i--) while (x->next[i] && (comparisons++, x->next[i]->key < key)) x = x->next[i]; return x->next[0];
    }
    bool contains(int key) { const Node* t = lowerBound(key); return t && t->key == key; }
    size_t rankOf(int key) const { Node* x = head; size_t r = 0; for (int i = level - 1; i >= 0; i--) while (x->next[i] && x->next[i]->key < key) { r += x->span[i]; x = x->next[i]; } return r; }      // key 보다 작은 원소 수
    int kth(size_t k) const { Node* x = head; size_t pos = 0, target = k + 1; for (int i = level - 1; i >= 0; i--) while (x->next[i] && pos + x->span[i] <= target) { pos += x->span[i]; x = x->next[i]; } assert(pos == target); return x->key; }          // 0 부터
    bool checkInvariants() const {
        for (int i = 0; i < level; i++) { int steps = 0; const Node* x = head; const Node* cur = head; (void)cur;
            for (const Node* y = head; y->next[i]; y = y->next[i]) { const Node* z = y->next[i]; if (y != head && y->key >= z->key) return false; int cnt = 0; const Node* w = y; while (w != z) { w = w->next[0]; cnt++; } if (cnt != y->span[i]) return false; steps++; (void)x; }          // 정렬 + 칸 수
            if (i > 0) for (const Node* y = head->next[i]; y; y = y->next[i]) if ((int)y->next.size() <= i - 1) return false; }
        for (const Node* y = head->next[0]; y; y = y->next[0]) if ((int)y->next.size() > level) return false; return true;
    }
};
int main() {
    SkipList sl(7); std::set<int> ref; std::mt19937 rng(3);
    for (int step = 0; step < 40000; step++) {
        int key = rng() % 5000, op = rng() % 3;
        if (op < 2) assert(sl.insert(key) == ref.insert(key).second); else assert(sl.erase(key) == (ref.erase(key) == 1));
        if (step % 5 == 0) { int q = rng() % 5200 - 100; auto it = ref.lower_bound(q); const SkipList::Node* lb = sl.lowerBound(q); assert((lb == nullptr) == (it == ref.end()) && (!lb || lb->key == *it)); assert(sl.contains(q) == (ref.count(q) == 1)); assert(sl.rankOf(q) == (size_t)std::distance(ref.begin(), ref.lower_bound(q))); }
        if (!ref.empty() && step % 7 == 0) { size_t k = rng() % ref.size(); assert(sl.kth(k) == *std::next(ref.begin(), k)); }
        if (step % 2000 == 0) assert(sl.checkInvariants() && sl.n == ref.size());
    }
    assert(sl.checkInvariants());
    SkipList asc(11); const int N = 100000; for (int i = 0; i < N; i++) asc.insert(i); asc.comparisons = 0; std::mt19937 q(5); const int Q = 20000; for (int t = 0; t < Q; t++) assert(asc.contains(q() % N));
    double perSearch = (double)asc.comparisons / Q, lg = std::log2((double)N); assert(perSearch < 3.0 * lg);                                                                             // ③ 정렬 입력에서도 O(log N)
    std::vector<long> byHeight(SkipList::MAXL + 1, 0); long ptrs = 0; for (const SkipList::Node* x = asc.head->next[0]; x; x = x->next[0]) { byHeight[x->next.size()]++; ptrs += x->next.size(); }
    long atLeast2 = N - byHeight[1], atLeast3 = atLeast2 - byHeight[2]; assert(std::abs((double)atLeast2 / N - 0.5) < 0.02 && std::abs((double)atLeast3 / N - 0.25) < 0.02 && std::abs((double)ptrs / N - 2.0) < 0.05);       // ④ 기하분포
    std::cout << "SkipList: matched std::set (insert/erase/lower_bound/rank/select) over 40000 operations with all invariants intact; on " << N << " ascending keys a search took " << perSearch << " comparisons (log2 N = " << lg << "), levels " << asc.level << ", average pointers per node " << (double)ptrs / N << std::endl; return 0;
}
// Time Complexity: 탐색·삽입·삭제·순위·k 번째 기대 O(log N)
// Space Complexity: O(N) (노드당 평균 포인터 2 개)
```
## Rope()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <cassert>

// 로프(리스트 관점의 요약, 정본은 String.md Part 4): 긴 문자열을 이진 트리로 나타내고 연결은 새 루트 하나, 분할·색인은 O(깊이).  노드가 불변이라 편집 전 버전과 구조를 공유한다
struct Node; typedef std::shared_ptr<const Node> P;
struct Node { P l, r; std::string s; size_t n; };                          // 잎: s, 내부: l/r, n = 전체 길이
P leaf(const std::string& s) { return std::make_shared<const Node>(Node{nullptr, nullptr, s, s.size()}); }
size_t len(const P& p) { return p ? p->n : 0; }
P cat(P a, P b) { return !a ? b : !b ? a : std::make_shared<const Node>(Node{a, b, "", a->n + b->n}); }
std::pair<P, P> split(const P& p, size_t i) {
    if (!p) return {nullptr, nullptr};
    if (!p->l) return {i ? leaf(p->s.substr(0, i)) : nullptr, i < p->n ? leaf(p->s.substr(i)) : nullptr};
    if (i < len(p->l)) { auto t = split(p->l, i); return {t.first, cat(t.second, p->r)}; }
    auto t = split(p->r, i - len(p->l)); return {cat(p->l, t.first), t.second};
}
std::string str(const P& p) { return !p ? "" : !p->l ? p->s : str(p->l) + str(p->r); }
int main() {
    P doc = cat(leaf("Hello, "), leaf("world!")); auto [a, b] = split(doc, 7);
    P edited = cat(cat(a, leaf("rope ")), b);                              // 중간 삽입 = 분할 + 연결
    assert(str(edited) == "Hello, rope world!" && str(doc) == "Hello, world!");
    std::cout << "Rope: " << str(edited) << std::endl; return 0;
}
// Time Complexity: 연결 O(1), 분할 O(깊이)
// Space Complexity: O(노드 수), 편집 후에도 원본 공유
```
## UnrolledLinkedList()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 언롤드 연결 리스트: 노드 하나에 원소를 하나가 아니라 최대 B 개 담는 배열을 두고 그 노드들을 연결한다. 연결 리스트의 O(1) 삽입(노드 단위)과 배열의 캐시 지역성·낮은 포인터 오버헤드를 절충한 구조다.
// 노드가 가득 찬 곳에 삽입하면 반으로 쪼개고(원소 B/2 + 1 개와 B/2 개), 삭제로 노드가 B/2 미만이 되면 이웃에서 하나 빌리거나 이웃과 합친다. 이 규칙으로 노드가 하나뿐인 경우를 빼면 모든 노드가 B/2 개 이상 채워져 있다는 불변식이 유지되어 노드 수는 ⌈2N/B⌉ 이하, 포인터 오버헤드는 N/(B/2) 개 이하다.
// 인덱스 접근은 노드를 건너뛰며 세므로 O(N/B) — 연결 리스트의 O(N) 보다 B 배 빠르다. 노드 안의 이동은 최대 B 칸이라 상수다.
// 검증: ① 무작위 위치 삽입·삭제·접근을 std::vector 와 대조 ② 불변식: 단일 노드가 아니면 모든 노드 크기가 [B/2, B], 합이 N ③ 노드 수 ≤ ⌈2N/B⌉ + 1 ④ 접근 시 방문한 노드 수가 연결 리스트(N/2)보다 약 B 배 적음
template <int B> struct Unrolled {
    static_assert(B >= 4 && B % 2 == 0, "B must be even and >= 4");
    struct Node { int n = 0; int a[B]; Node* next = nullptr; };
    Node* head = nullptr; size_t total = 0, nodes = 0; mutable long visits = 0;
    ~Unrolled() { while (head) { Node* nx = head->next; delete head; head = nx; } }
    void insert(size_t idx, int v) {                                             // 0 <= idx <= total
        if (!head) { head = new Node; nodes = 1; }
        Node* node = head; while (idx > (size_t)node->n && node->next) { idx -= node->n; node = node->next; }
        if (node->n == B) { Node* nn = new Node; nodes++; int h = B / 2; for (int i = h; i < B; i++) nn->a[i - h] = node->a[i]; nn->n = B - h; node->n = h; nn->next = node->next; node->next = nn; if (idx > (size_t)h) { idx -= h; node = nn; } }
        for (int i = node->n; i > (int)idx; i--) node->a[i] = node->a[i - 1]; node->a[idx] = v; node->n++; total++;
    }
    int at(size_t idx) const { for (Node* node = head; node; node = node->next) { visits++; if (idx < (size_t)node->n) return node->a[idx]; idx -= node->n; } assert(false); return -1; }
    void erase(size_t idx) {
        Node *prev = nullptr, *node = head; while (idx >= (size_t)node->n) { idx -= node->n; prev = node; node = node->next; }
        for (int i = idx; i + 1 < node->n; i++) node->a[i] = node->a[i + 1]; node->n--; total--;
        if (node->n == 0 && !node->next && !prev) { delete node; head = nullptr; nodes = 0; return; }                         // 마지막 남은 노드가 비면 제거
        if (node->n >= B / 2) return;
        Node* nx = node->next;
        if (nx) { if (nx->n + node->n <= B) { for (int i = 0; i < nx->n; i++) node->a[node->n + i] = nx->a[i]; node->n += nx->n; node->next = nx->next; delete nx; nodes--; }
                  else { node->a[node->n++] = nx->a[0]; for (int i = 0; i + 1 < nx->n; i++) nx->a[i] = nx->a[i + 1]; nx->n--; } }                          // 이웃에서 하나 빌린다
        else if (prev) { if (prev->n + node->n <= B) { for (int i = 0; i < node->n; i++) prev->a[prev->n + i] = node->a[i]; prev->n += node->n; prev->next = nullptr; delete node; nodes--; }
                         else { for (int i = node->n; i > 0; i--) node->a[i] = node->a[i - 1]; node->a[0] = prev->a[--prev->n]; node->n++; } }
    }
    bool check() const { size_t sum = 0, cnt = 0; for (Node* x = head; x; x = x->next) { cnt++; sum += x->n; if (x->n > B || x->n < 1) return false; if ((head->next) && x->n < B / 2) return false; } return sum == total && cnt == nodes; }
};
int main() {
    const int B = 16; Unrolled<B> u; std::vector<int> ref; std::mt19937 rng(5); size_t maxNodes = 0;
    for (int step = 0; step < 40000; step++) {
        int op = rng() % 5; if (op < 3 || ref.empty()) { size_t i = rng() % (ref.size() + 1); int v = rng(); u.insert(i, v); ref.insert(ref.begin() + i, v); } else { size_t i = rng() % ref.size(); u.erase(i); ref.erase(ref.begin() + i); }
        if (ref.size() > 3000) { for (int k = 0; k < 500; k++) { size_t i = rng() % ref.size(); u.erase(i); ref.erase(ref.begin() + i); } }
        if (!ref.empty() && step % 3 == 0) { size_t i = rng() % ref.size(); assert(u.at(i) == ref[i]); }
        if (step % 500 == 0) { assert(u.check() && u.total == ref.size()); std::vector<int> all; for (auto* x = u.head; x; x = x->next) for (int i = 0; i < x->n; i++) all.push_back(x->a[i]); assert(all == ref); }
        maxNodes = std::max(maxNodes, u.nodes); assert(u.nodes <= (2 * ref.size() + B - 1) / B + 1);                                        // ③
    }
    while (!ref.empty()) { size_t i = rng() % ref.size(); u.erase(i); ref.erase(ref.begin() + i); } assert(u.total == 0 && u.head == nullptr && u.check());
    Unrolled<B> big; const int N = 20000; for (int i = 0; i < N; i++) big.insert(i, i); big.visits = 0; for (int t = 0; t < 2000; t++) assert(big.at(rng() % N) < N); double perAccess = (double)big.visits / 2000; assert(perAccess < (N / 2.0) / (B / 2) + 3 && perAccess * (B / 2) > N / 8.0);   // ④ N/(2·B_eff) 개 노드만 방문
    std::cout << "UnrolledLinkedList: matched vector over 40000 mixed operations with all nodes filled to at least B/2; with B=" << B << " a random access visited " << perAccess << " nodes on average versus " << N / 2 << " for a plain linked list; peak node count " << maxNodes << std::endl; return 0;
}
// Time Complexity: 접근·삽입·삭제 O(N/B + B)
// Space Complexity: O(N), 노드 오버헤드 ≤ 2N/B 개 포인터
```
## GapBuffer()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <cassert>

// 갭 버퍼(리스트 관점의 요약, 정본은 String.md Part 4): 글자 배열 가운데에 "빈 틈(gap)"을 두고 커서가 있는 곳에 틈을 놓는다. 커서 위치에서의 삽입·삭제는 O(1),
// 커서를 옮기면 틈을 따라 옮기는 데 이동 거리만큼의 복사가 든다. 편집은 지역적이라는 관찰에 기대는 Emacs 의 버퍼 구조
struct GapBuffer {
    std::string b; size_t gs, ge;                                          // 틈 [gs, ge)
    GapBuffer() : b(8, '_'), gs(0), ge(8) {}
    void moveTo(size_t pos) { while (gs > pos) b[--ge] = b[--gs]; while (gs < pos) b[gs++] = b[ge++]; }
    void insert(char c) { if (gs == ge) { size_t add = b.size(); b.insert(ge, add, '_'); ge += add; } b[gs++] = c; }
    void erase() { if (gs) gs--; }                                         // 커서 앞 글자 삭제
    std::string text() const { return b.substr(0, gs) + b.substr(ge); }
};
int main() {
    GapBuffer g; for (char c : std::string("Hello world")) g.insert(c);
    g.moveTo(5); g.insert(','); g.moveTo(g.text().size()); g.insert('!');
    assert(g.text() == "Hello, world!"); g.moveTo(5); g.erase(); assert(g.text() == "Hell, world!");
    std::cout << "GapBuffer: " << g.text() << std::endl; return 0;
}
// Time Complexity: 커서 위치 삽입·삭제 O(1), 이동 O(거리)
// Space Complexity: O(N + 틈)
```
## PieceTable()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 피스 테이블(리스트 관점의 요약, 정본은 String.md Part 4): 원본 파일은 수정하지 않고 "추가 전용" 버퍼에 새 글자를 덧붙이며, 문서 = (버퍼, 시작, 길이) 조각들의 목록.
// 삽입은 조각을 둘로 쪼개고 새 조각 하나를 끼우는 일이고, 조각 목록의 복사본이 곧 실행 취소(undo) 기록이다 (VS Code 의 텍스트 버퍼가 이 계열)
struct Piece { bool add; size_t start, len; };
struct PT {
    std::string orig, added; std::vector<Piece> pieces;
    explicit PT(const std::string& s) : orig(s), pieces{{false, 0, s.size()}} {}
    void insert(size_t pos, const std::string& t) {
        size_t off = 0, i = 0; while (i < pieces.size() && off + pieces[i].len <= pos) off += pieces[i++].len;
        Piece n{true, added.size(), t.size()}; added += t;
        if (i < pieces.size() && pos > off) { Piece p = pieces[i]; size_t k = pos - off; pieces[i] = {p.add, p.start, k}; pieces.insert(pieces.begin() + i + 1, {p.add, p.start + k, p.len - k}); i++; }
        pieces.insert(pieces.begin() + i, n);
    }
    std::string text() const { std::string r; for (auto& p : pieces) r += (p.add ? added : orig).substr(p.start, p.len); return r; }
};
int main() {
    PT d("Hello world"); auto undo = d.pieces;                             // 조각 목록의 복사본 = 문서의 한 시점
    d.insert(5, ","); d.insert(0, ">> ");
    assert(d.text() == ">> Hello, world" && d.orig == "Hello world");        // 원본은 그대로
    d.pieces = undo; assert(d.text() == "Hello world");                    // 실행 취소 = 조각 목록 복원
    std::cout << "PieceTable: undo restores \"" << d.text() << "\"" << std::endl; return 0;
}
// Time Complexity: 삽입 O(조각 수), 텍스트 조립 O(길이)
// Space Complexity: 원본 + 추가 버퍼 + 조각 목록
```
## FingerTree()
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 핑거 트리 (리스트 관점의 요약, 정본은 AdvancedDataStructures.md Part 4): 양 끝에 길이 1~4 의 "손가락" 을 두고 가운데에는 2-3 노드를 원소로 하는 같은 구조를 재귀적으로 단 불변 시퀀스. 아래는 정본에서 양 끝 연산(pushFront/pushBack/viewFront/viewBack)만 떼어 낸 영속 덱이다.
// 리스트와 비교하면 양 끝 연산이 분할상환 O(1) 이라 연결 리스트의 맨 앞과 배열의 맨 뒤 장점을 합치면서 모든 버전이 구조를 공유하고, 정본의 concat O(log N) · split/index O(log N) 이 더해지면 영속 시퀀스의 만능 도구가 된다.
// 검증: 임의의 옛 버전에서 이어 붙이는 무작위 양 끝 연산 5000 번이 std::deque 모델과 같고, 옛 버전들이 변하지 않으며, 20 만 원소의 나선(spine) 깊이가 log 규모

struct Node; typedef std::shared_ptr<const Node> NP;
struct Node { int val; int size; std::vector<NP> k; };
NP leaf(int v) { return std::make_shared<const Node>(Node{v, 1, {}}); }
NP node(std::vector<NP> k) { int s = 0; for (auto& x : k) s += x->size; return std::make_shared<const Node>(Node{0, s, std::move(k)}); }
struct FT; typedef std::shared_ptr<const FT> F;
struct FT { int kind; NP one; std::vector<NP> pre, suf; F mid; int size; };          // kind: 0 빈 트리, 1 단일 원소, 2 Deep(앞 손가락, 가운데 트리, 뒤 손가락)
int sz(const std::vector<NP>& d) { int s = 0; for (auto& x : d) s += x->size; return s; }
F Empty() { static F e = std::make_shared<const FT>(FT{0, nullptr, {}, {}, nullptr, 0}); return e; }
F Single(NP a) { return std::make_shared<const FT>(FT{1, a, {}, {}, nullptr, a->size}); }
F Deep(std::vector<NP> pre, F mid, std::vector<NP> suf) { int s = sz(pre) + mid->size + sz(suf); return std::make_shared<const FT>(FT{2, nullptr, std::move(pre), std::move(suf), std::move(mid), s}); }
F digitToTree(const std::vector<NP>& d) {
    switch (d.size()) {
        case 0: return Empty(); case 1: return Single(d[0]); case 2: return Deep({d[0]}, Empty(), {d[1]});
        case 3: return Deep({d[0], d[1]}, Empty(), {d[2]}); default: return Deep({d[0], d[1]}, Empty(), {d[2], d[3]});
    }
}
F pushFront(const F& t, NP a) {
    if (t->kind == 0) return Single(a);
    if (t->kind == 1) return Deep({a}, Empty(), {t->one});
    if (t->pre.size() < 4) { auto p = t->pre; p.insert(p.begin(), a); return Deep(p, t->mid, t->suf); }
    return Deep({a, t->pre[0]}, pushFront(t->mid, node({t->pre[1], t->pre[2], t->pre[3]})), t->suf);           // 손가락이 넘치면 3개를 노드로 묶어 가운데로
}
F pushBack(const F& t, NP a) {
    if (t->kind == 0) return Single(a);
    if (t->kind == 1) return Deep({t->one}, Empty(), {a});
    if (t->suf.size() < 4) { auto s = t->suf; s.push_back(a); return Deep(t->pre, t->mid, s); }
    return Deep(t->pre, pushBack(t->mid, node({t->suf[0], t->suf[1], t->suf[2]})), {t->suf[3], a});
}
F deepL(std::vector<NP> pre, const F& mid, std::vector<NP> suf);
F deepR(std::vector<NP> pre, const F& mid, std::vector<NP> suf);
std::pair<NP, F> viewFront(const F& t) {                                   // 비어 있지 않은 트리의 첫 원소와 나머지
    if (t->kind == 1) return {t->one, Empty()};
    NP h = t->pre[0]; std::vector<NP> rest(t->pre.begin() + 1, t->pre.end());
    return {h, deepL(rest, t->mid, t->suf)};
}
std::pair<F, NP> viewBack(const F& t) {
    if (t->kind == 1) return {Empty(), t->one};
    NP h = t->suf.back(); std::vector<NP> rest(t->suf.begin(), t->suf.end() - 1);
    return {deepR(t->pre, t->mid, rest), h};
}
F deepL(std::vector<NP> pre, const F& mid, std::vector<NP> suf) {          // 앞 손가락이 비었을 수 있을 때 Deep 을 안전하게 만든다
    if (!pre.empty()) return Deep(pre, mid, suf);
    if (mid->kind == 0) return digitToTree(suf);
    auto v = viewFront(mid); return Deep(v.first->k, v.second, suf);       // 가운데에서 노드 하나를 꺼내 그 자식들을 앞 손가락으로
}
F deepR(std::vector<NP> pre, const F& mid, std::vector<NP> suf) {
    if (!suf.empty()) return Deep(pre, mid, suf);
    if (mid->kind == 0) return digitToTree(pre);
    auto v = viewBack(mid); return Deep(pre, v.first, v.second->k);
}
void flat(const NP& n, std::vector<int>& out) { if (n->k.empty()) out.push_back(n->val); else for (auto& c : n->k) flat(c, out); }
void collect(const F& t, std::vector<int>& out) {
    if (t->kind == 0) return; if (t->kind == 1) { flat(t->one, out); return; }
    for (auto& x : t->pre) flat(x, out); collect(t->mid, out); for (auto& x : t->suf) flat(x, out);
}
std::vector<int> toVec(const F& t) { std::vector<int> v; collect(t, v); return v; }
int depth(const F& t) { return t->kind == 2 ? 1 + depth(t->mid) : 0; }
int main() {
    std::mt19937 rng(21); std::vector<F> ver = {Empty()}; std::vector<std::deque<int>> model = {{}};
    for (int step = 0; step < 5000; step++) {
        int base = rng() % ver.size(); F t = ver[base]; std::deque<int> m = model[base]; int op = rng() % 4;
        if (op == 0 || m.empty()) { int x = rng() % 1000; t = pushFront(t, leaf(x)); m.push_front(x); }
        else if (op == 1) { int x = rng() % 1000; t = pushBack(t, leaf(x)); m.push_back(x); }
        else if (op == 2) { auto v = viewFront(t); assert(v.first->val == m.front()); t = v.second; m.pop_front(); }
        else { auto v = viewBack(t); assert(v.second->val == m.back()); t = v.first; m.pop_back(); }
        assert(t->size == (int)m.size() && toVec(t) == std::vector<int>(m.begin(), m.end()));
        ver.push_back(t); model.push_back(m);
    }
    for (size_t i = 0; i < ver.size(); i += 13) assert(toVec(ver[i]) == std::vector<int>(model[i].begin(), model[i].end()));          // 옛 버전은 그대로
    F big = Empty(); for (int i = 0; i < 200000; i++) big = (i % 2) ? pushBack(big, leaf(i)) : pushFront(big, leaf(i)); assert(big->size == 200000 && depth(big) < 25);
    std::cout << "FingerTree: 5000 persistent deque operations matched std::deque; 200000 elements -> spine depth " << depth(big) << std::endl; return 0;
}
// Time Complexity: 양 끝 push/pop 분할상환 O(1) (concat·split 은 정본 참고)
// Space Complexity: O(N), 버전 사이에 구조 공유
```
## PersistentList()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 영속 리스트 (리스트 관점의 요약, 정본은 AdvancedDataStructures.md Part 1): 불변 단방향 연결 리스트. cons(맨 앞에 붙이기)는 새 노드 하나만 만들고 나머지 꼬리는 그대로 공유한다.
// 가운데를 바꾸는 setAt 은 앞부분(i 개)만 복사하고 뒤쪽은 공유, concat(a, b) 는 a 만 복사하고 b 를 공유한다. 모든 옛 버전이 변하지 않으므로 스레드 사이에 잠금 없이 공유할 수 있고, 가운데 접근이 필요하면 ImmutableList(영속 벡터)를 쓴다.
struct Node; typedef std::shared_ptr<const Node> List;
struct Node { int head; List tail; };
List cons(int x, const List& t) { return std::make_shared<const Node>(Node{x, t}); }
int size(List l) { int n = 0; for (; l; l = l->tail) n++; return n; }
int at(List l, int i) { while (i--) l = l->tail; return l->head; }
List setAt(const List& l, int i, int v) { return i == 0 ? cons(v, l->tail) : cons(l->head, setAt(l->tail, i - 1, v)); }
List concat(const List& a, const List& b) { return !a ? b : cons(a->head, concat(a->tail, b)); }
std::vector<int> toVec(List l) { std::vector<int> v; for (; l; l = l->tail) v.push_back(l->head); return v; }
List fromVec(const std::vector<int>& v) { List l; for (int i = (int)v.size() - 1; i >= 0; i--) l = cons(v[i], l); return l; }

int main() {
    List a = fromVec({1, 2, 3, 4, 5});
    List b = setAt(a, 1, 99);                                              // a 는 그대로, b = 1 99 3 4 5
    assert((toVec(a) == std::vector<int>{1, 2, 3, 4, 5}) && (toVec(b) == std::vector<int>{1, 99, 3, 4, 5}));
    assert(a->tail->tail == b->tail->tail);                                // 인덱스 2 부터의 꼬리는 같은 노드를 가리킨다 (구조 공유)
    List c = cons(0, a), d = cons(-1, a);                                  // 같은 꼬리를 공유하는 두 리스트
    assert(c->tail == d->tail && a.use_count() >= 3);
    List e = concat(fromVec({7, 8}), a); assert(toVec(e) == (std::vector<int>{7, 8, 1, 2, 3, 4, 5}) && e->tail->tail == a);
    std::mt19937 rng(9); std::vector<List> ver = {nullptr}; std::vector<std::vector<int>> model = {{}};
    for (int step = 0; step < 4000; step++) {
        int base = rng() % ver.size(); int op = rng() % 3;
        if (op == 0 || model[base].empty()) { int x = rng() % 1000; ver.push_back(cons(x, ver[base])); model.push_back(model[base]); model.back().insert(model.back().begin(), x); }
        else if (op == 1) { int i = rng() % model[base].size(), v = rng() % 1000; ver.push_back(setAt(ver[base], i, v)); model.push_back(model[base]); model.back()[i] = v; }
        else { ver.push_back(ver[base]->tail); model.push_back(model[base]); model.back().erase(model.back().begin()); }
        if (model.back().size() > 40) { ver.back() = ver.back()->tail; model.back().erase(model.back().begin()); }
    }
    for (size_t i = 0; i < ver.size(); i++) assert(toVec(ver[i]) == model[i]);          // 4000 개 버전 모두 자기 내용을 유지
    std::cout << "PersistentList: " << ver.size() << " versions verified, tail sharing confirmed" << std::endl;
    return 0;
}
// Time Complexity: cons·tail O(1), setAt·at O(i), concat O(|a|)
// Space Complexity: 변경마다 새 노드 O(i) 만 추가
```
## ImmutableList()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <memory>
#include <random>
#include <unordered_set>
#include <vector>
#include <cassert>

// 불변 리스트(Immutable List): 한번 만든 리스트는 절대 바뀌지 않고, 수정은 "새 버전" 을 돌려준다. 스레드 사이에 잠금 없이 공유할 수 있고 옛 버전이 그대로 남아 되돌리기(undo)가 공짜다.
// 단순하게 전체를 복사하면 수정마다 O(N) 이다. 그래서 영속 벡터(Clojure/Scala 의 Vector, Bagwell 의 HAMT 계열)는 원소를 W 개씩 담는 노드의 트리(W-진 기수 트라이)로 저장한다: i 번째 원소는 인덱스를 log₂W 비트씩 끊어 루트에서 잎까지 내려가 찾고, 수정은 그 길 위의 노드(깊이 log_W N 개)만 복사하며 나머지 서브트리는 이전 버전과 공유한다.
// W = 32 면 N = 10 억에서도 깊이가 6 이라 접근·수정·끝에 추가가 "실질적 O(1)" 이다. 이 구현은 이해하기 쉽게 잎 꼬리(tail) 최적화 없이 비트 수 BITS 를 템플릿 인자로 받는다(테스트에서는 W=4 로 깊은 트리를, 크기 시험에서는 W=32).
// 검증: ① 무작위 push_back/set/pop_back 을 임의의 옛 버전에서 이어 붙여도 모든 버전이 각자의 스냅샷 vector 와 같다(영속성) ② 한 번의 수정이 새로 만드는 노드 수 ≤ 깊이 + 2 ③ N = 100000, W = 32 에서 set 한 번이 만든 노드는 4~5 개이고 두 버전이 공유하는 노드가 나머지 전부 ④ 옛 버전은 변하지 않음
template <int BITS> struct PVec {
    static const int W = 1 << BITS, MASK = W - 1;
    struct Node; typedef std::shared_ptr<const Node> NP;
    struct Node { std::vector<NP> kid; std::vector<int> val; };
    NP root; int shift = 0; size_t n = 0; static long allocs;
    int get(size_t i) const { const Node* x = root.get(); for (int s = shift; s > 0; s -= BITS) x = x->kid[(i >> s) & MASK].get(); return x->val[i & MASK]; }
    static NP assoc(const NP& node, int s, size_t i, int v) {
        std::shared_ptr<Node> c = node ? std::make_shared<Node>(*node) : std::make_shared<Node>(); allocs++;
        if (s == 0) { if (c->val.size() <= (i & MASK)) c->val.resize((i & MASK) + 1); c->val[i & MASK] = v; }
        else { size_t k = (i >> s) & MASK; if (c->kid.size() <= k) c->kid.resize(k + 1); c->kid[k] = assoc(c->kid[k], s - BITS, i, v); }
        return c;
    }
    static NP trim(const NP& node, int s, size_t count) {                          // 앞의 count 개만 남긴 노드 (count >= 1)
        std::shared_ptr<Node> c = std::make_shared<Node>(*node); allocs++;
        if (s == 0) c->val.resize(count); else { size_t last = (count - 1) >> s & MASK; c->kid.resize(last + 1); c->kid[last] = trim(c->kid[last], s - BITS, count - (last << s)); }
        return c;
    }
    PVec set(size_t i, int v) const { PVec r = *this; r.root = assoc(root, shift, i, v); return r; }
    PVec pushBack(int v) const {
        PVec r = *this;
        if (n > 0 && n == ((size_t)1 << (shift + BITS))) { std::shared_ptr<Node> nr = std::make_shared<Node>(); nr->kid.push_back(root); allocs++; r.root = nr; r.shift = shift + BITS; }          // 가득 찼으면 루트를 한 층 올린다
        r.root = assoc(r.root, r.shift, n, v); r.n = n + 1; return r;
    }
    PVec popBack() const {
        PVec r = *this; r.n = n - 1; if (r.n == 0) { r.root = nullptr; r.shift = 0; return r; }
        r.root = trim(root, shift, r.n); while (r.shift > 0 && r.root->kid.size() == 1) { r.root = r.root->kid[0]; r.shift -= BITS; } return r;
    }
    void collect(std::unordered_set<const Node*>& out) const { std::vector<const Node*> st; if (root) st.push_back(root.get()); while (!st.empty()) { const Node* x = st.back(); st.pop_back(); out.insert(x); for (auto& k : x->kid) st.push_back(k.get()); } }
    int depth() const { return shift / BITS + 1; }
};
template <int BITS> long PVec<BITS>::allocs = 0;
int main() {
    typedef PVec<2> V; std::vector<V> versions = {V()}; std::vector<std::vector<int>> snaps = {{}}; std::mt19937 rng(13); long maxAllocs = 0;
    for (int step = 0; step < 6000; step++) {
        size_t base = rng() % versions.size(); const V& v = versions[base]; std::vector<int> s = snaps[base]; int op = rng() % 4; V r; V::allocs = 0;
        if (op < 2 || s.empty()) { int x = rng() % 1000; r = v.pushBack(x); s.push_back(x); }
        else if (op == 2) { size_t i = rng() % s.size(); int x = rng() % 1000; r = v.set(i, x); s[i] = x; }
        else { r = v.popBack(); s.pop_back(); }
        maxAllocs = std::max(maxAllocs, V::allocs); assert(V::allocs <= r.depth() + 2 || V::allocs <= v.depth() + 2);                                                                         // ②
        assert(r.n == s.size()); for (size_t i = 0; i < s.size(); i++) assert(r.get(i) == s[i]);
        if (s.size() > 120) { r = V(); s.clear(); }                                                                                                                                                  // 크기를 억제
        versions.push_back(r); snaps.push_back(s);
        if (step % 600 == 0) for (size_t k = 0; k < versions.size(); k += 7) { assert(versions[k].n == snaps[k].size()); for (size_t i = 0; i < snaps[k].size(); i++) assert(versions[k].get(i) == snaps[k][i]); }  // ①④ 옛 버전은 그대로
    }
    typedef PVec<5> W32; W32 big; const int N = 100000; for (int i = 0; i < N; i++) big = big.pushBack(i);
    W32::allocs = 0; W32 big2 = big.set(5000, -1); long created = W32::allocs; std::unordered_set<const W32::Node*> a, b; big.collect(a); big2.collect(b); long shared = 0; for (auto* x : b) shared += a.count(x);
    assert(big.get(5000) == 5000 && big2.get(5000) == -1 && big2.get(7) == 7 && big.depth() == 4 && created == big.depth() && (long)b.size() - shared == created && (long)a.size() - shared == created);        // ③ 길 위 노드만 새로 만들고 나머지는 공유
    std::cout << "ImmutableList: " << versions.size() << " persistent versions of a W=4 trie all matched their snapshots (max " << maxAllocs << " nodes created per operation); with W=32 and N=" << N << " one set() created " << created << " nodes (depth " << big.depth() << ") and shared the other " << shared << " of " << b.size() << std::endl; return 0;
}
// Time Complexity: 접근·set·끝 추가·끝 삭제 O(log_W N) (W=32 에서 실질적 상수)
// Space Complexity: 수정당 새 노드 O(log_W N), 나머지는 이전 버전과 공유
```

# 마지막 부록
## ArrayList vs LinkedList
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <iterator>
#include <list>
#include <random>
#include <vector>
#include <cassert>

// ArrayList vs LinkedList — 배열 리스트는 원소를 연속된 메모리에, 연결 리스트는 노드를 포인터로 잇는다. 교과서의 표(배열: 접근 O(1)·중간 삽입 O(N), 연결: 접근 O(N)·삽입 O(1))는 반만 맞다 — "삽입 O(1)" 은 삽입할 위치를 이미 알 때뿐이고, 위치를 찾는 데 O(N) 이 들어가면 두 구조 모두 중간 삽입이 O(N) 이다.
// 이 실험은 원소 이동 횟수(moves)와 노드 건너뛴 횟수(hops)를 직접 센다. ① 앞에 N 번 삽입: 배열 N(N−1)/2 번 이동, 연결 0 ② 인덱스로 가운데 삽입: 배열은 N/2 번 이동, 연결은 N/2 번 건너뛰기 — 같은 차수 ③ 위치(반복자)를 쥐고 있을 때 삽입: 배열 N/2 이동, 연결 0 ④ 임의 접근: 배열 0, 연결 평균 N/2 ⑤ 끝에 추가: 두 배 증가 배열의 총 복사 < 2N (원소당 평균 2 번 미만) ⑥ 조건 삭제: 연결 리스트의 개별 삭제 O(1)·전체 O(N) vs 배열의 erase 반복 O(N²) vs erase–remove 관용구 O(N).
// 메모리 모델도 다르다: int 하나를 담는 데 배열은 4 바이트, 이중 연결 노드는 (int + 포인터 2 개 + 패딩) = 24 바이트라 6 배다. 실제 속도는 캐시 지역성(다음 항목 Cache Locality)이 결정하며, 대부분의 현실 부하에서 배열이 이긴다. 연결 리스트가 이기는 곳은 반복자를 유지한 채 중간 삽입·삭제가 잦거나, 원소 이동이 비싸거나, 원소의 주소가 고정되어야 할 때(참조 안정성)뿐이다
struct ArrayListM {                                                           // 원소 이동 횟수를 세는 배열 리스트
    std::vector<int> a; long moves = 0;
    void insertAt(size_t i, int v) { a.push_back(0); for (size_t k = a.size() - 1; k > i; k--) { a[k] = a[k - 1]; moves++; } a[i] = v; }
    void eraseAt(size_t i) { for (size_t k = i; k + 1 < a.size(); k++) { a[k] = a[k + 1]; moves++; } a.pop_back(); }
};
struct LinkedListM {                                                          // 노드 건너뛴 횟수를 세는 이중 연결 리스트
    struct Node { int v; Node *prev, *next; }; Node* s; size_t n = 0; long hops = 0;
    LinkedListM() { s = new Node{0, nullptr, nullptr}; s->prev = s->next = s; }
    ~LinkedListM() { Node* x = s->next; while (x != s) { Node* nx = x->next; delete x; x = nx; } delete s; }
    Node* nodeAt(size_t i) { Node* x = s->next; while (i--) { x = x->next; hops++; } return x; }
    Node* insertBefore(Node* pos, int v) { Node* x = new Node{v, pos->prev, pos}; pos->prev->next = x; pos->prev = x; n++; return x; }
    void erase(Node* x) { x->prev->next = x->next; x->next->prev = x->prev; delete x; n--; }
    std::vector<int> toVector() const { std::vector<int> v; for (Node* x = s->next; x != s; x = x->next) v.push_back(x->v); return v; }
};
int main() {
    const int N = 2000; std::mt19937 rng(1);
    { ArrayListM a; LinkedListM l; for (int i = 0; i < N; i++) { a.insertAt(0, i); l.insertBefore(l.s->next, i); } assert(a.moves == (long)N * (N - 1) / 2 && l.hops == 0 && a.a == l.toVector()); }                          // ① 앞에 N 번 삽입
    long arrMid = 0, lstMid = 0; { ArrayListM a; LinkedListM l; for (int i = 0; i < N; i++) { a.insertAt(a.a.size() / 2, i); l.insertBefore(l.nodeAt(l.n / 2), i); } arrMid = a.moves; lstMid = l.hops; assert(a.a == l.toVector()); assert(arrMid > N * N / 5 && lstMid > N * N / 5 && arrMid < N * N / 2 && lstMid < N * N / 2); }    // ② 같은 차수 Θ(N²)
    { ArrayListM a; LinkedListM l; for (int i = 0; i < N; i++) { a.a.push_back(i); l.insertBefore(l.s, i); } a.moves = l.hops = 0; LinkedListM::Node* held = l.nodeAt(N / 2); l.hops = 0; for (int i = 0; i < N; i++) { a.insertAt(N / 2, -1 - i); l.insertBefore(held, -1 - i); } assert(l.hops == 0 && a.moves > (long)N * N / 4 * 0 + (long)N * (N / 2 - 1) / 2); }            // ③ 위치를 쥐고 있으면 연결 리스트는 이동 0
    { LinkedListM l; std::vector<int> v; for (int i = 0; i < N; i++) { l.insertBefore(l.s, i); v.push_back(i); } long total = 0; for (int q = 0; q < 1000; q++) { size_t i = rng() % N; l.hops = 0; assert(l.nodeAt(i)->v == v[i]); total += l.hops; } double avg = (double)total / 1000; assert(avg > N * 0.35 && avg < N * 0.65); }                                  // ④ 임의 접근
    { std::vector<int> a; long copies = 0; size_t cap = 0; for (int i = 0; i < 100000; i++) { if (a.size() == cap) { copies += a.size(); cap = cap ? cap * 2 : 1; a.reserve(cap); } a.push_back(i); } assert(copies < 2 * 100000); }                                                                                       // ⑤ 두 배 증가의 총 복사 < 2N
    ArrayListM a; LinkedListM l; std::vector<int> ref; for (int i = 0; i < N; i++) { int v = rng() % 100; a.a.push_back(v); l.insertBefore(l.s, v); ref.push_back(v); }
    { auto pred = [](int x) { return x % 2 == 0; }; for (size_t i = 0; i < a.a.size();) { if (pred(a.a[i])) a.eraseAt(i); else i++; } long lh = 0; for (auto* x = l.s->next; x != l.s;) { auto* nx = x->next; if (pred(x->v)) l.erase(x); x = nx; lh++; } std::vector<int> er; long eraseRemoveMoves = 0; for (int v : ref) if (!pred(v)) { er.push_back(v); eraseRemoveMoves++; } ref.erase(std::remove_if(ref.begin(), ref.end(), pred), ref.end()); assert(a.a == ref && l.toVector() == ref && er == ref && lh == N && eraseRemoveMoves <= N && a.moves > 20 * eraseRemoveMoves); }            // ⑥
    assert(sizeof(LinkedListM::Node) == 24 && sizeof(int) == 4);
    std::cout << "ArrayList vs LinkedList: front inserts " << (long)N * (N - 1) / 2 << " moves vs 0; middle insert by index moves " << arrMid << " vs hops " << lstMid << " (same Theta(N^2)); with a held position the list needs 0; naive erase loop moved " << a.moves << " elements vs <= " << N << " for erase-remove; memory per int 4 vs " << sizeof(LinkedListM::Node) << " bytes" << std::endl; return 0;
}
// Time Complexity: 위치를 아는 삽입 — 배열 O(N), 연결 O(1) / 인덱스로 찾는 삽입 — 둘 다 O(N) / 임의 접근 — 배열 O(1), 연결 O(N)
// Space Complexity: 배열 O(N) (원소 크기), 연결 O(N) (원소 + 포인터 2 개)
```
## Cache Locality
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 캐시 지역성(Cache Locality): CPU 는 메모리를 64 바이트 캐시 라인 단위로 가져온다. 라인 하나를 읽으면 그 안의 이웃 원소들은 공짜가 되므로(공간 지역성) 연속 메모리를 순서대로 훑는 코드가 빠르고, 최근에 쓴 라인이 캐시에 남아 있으면 다시 읽어도 공짜다(시간 지역성).
// 실제 시간은 기계마다 달라 단언문에 쓸 수 없으므로, 결정적인 캐시 시뮬레이터(32 KB, 8-way, 64 B 라인, LRU)에 "주소 열" 을 흘려 미스 횟수를 센다. 실험 ① 행 우선 vs 열 우선 행렬 합: 행 우선은 라인당 16 개 int 를 쓰므로 미스가 N²/16, 열 우선은 보폭이 라인 크기보다 커서 거의 매 접근이 미스 ② 순차 배열 vs 노드가 흩어진 연결 리스트 순회: 배열 n/16 미스, 섞인 리스트는 거의 n ③ AoS(구조체 배열) vs SoA(배열 구조체)로 한 필드만 합산: AoS 는 원소마다 라인을 하나씩, SoA 는 16 개당 하나 ④ 블록(타일) 전치: 순진한 전치는 목적지 쓰기가 열 방향이라 미스가 크지만 16×16 타일이면 타일이 캐시에 들어가 미스가 1/4 이하
// 이 때문에 점근 복잡도가 같아도 배열이 연결 리스트를 대부분 이기고, 알고리즘을 "캐시에 맞게" 재배열(블로킹, SoA 변환)하는 것이 최적화의 큰 몫이다
struct Cache {
    int sets, ways; std::vector<std::vector<uint64_t>> lru; long hits = 0, misses = 0;
    Cache(int kb = 32, int w = 8) : sets(kb * 1024 / 64 / w), ways(w), lru(sets) {}
    void access(uint64_t addr) { uint64_t line = addr >> 6; auto& s = lru[line % sets]; for (size_t i = 0; i < s.size(); i++) if (s[i] == line) { s.erase(s.begin() + i); s.insert(s.begin(), line); hits++; return; } misses++; s.insert(s.begin(), line); if ((int)s.size() > ways) s.pop_back(); }
};
int main() {
    const int N = 512;
    { Cache row, col; for (int r = 0; r < N; r++) for (int c = 0; c < N; c++) row.access(((uint64_t)r * N + c) * 4); for (int c = 0; c < N; c++) for (int r = 0; r < N; r++) col.access(((uint64_t)r * N + c) * 4); assert(row.misses == (long)N * N / 16 && col.misses > (long)N * N * 9 / 10); std::cout << "matrix sum misses: row-major " << row.misses << " vs column-major " << col.misses << "; "; }          // ①
    const int n = 100000; std::mt19937 rng(2);
    { Cache arr, seq, shuf; for (int i = 0; i < n; i++) arr.access((uint64_t)i * 4); std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0);
      for (int i = 0; i < n; i++) seq.access((uint64_t)i * 16);                                   // 순차 배치 노드(16 B): 라인당 4 개
      for (int i = n - 1; i > 0; i--) std::swap(perm[i], perm[rng() % (i + 1)]); for (int i = 0; i < n; i++) shuf.access((uint64_t)perm[i] * 16);                      // 섞인 배치 노드
      assert(arr.misses == n / 16 && seq.misses == n / 4 && shuf.misses > (long)n * 8 / 10 && shuf.misses > 12 * arr.misses); std::cout << "traversal misses: array " << arr.misses << ", sequential nodes " << seq.misses << ", scattered nodes " << shuf.misses << "; "; }               // ②
    { Cache aos, soa; for (int i = 0; i < n; i++) aos.access((uint64_t)i * 64); for (int i = 0; i < n; i++) soa.access((uint64_t)i * 4); assert(aos.misses == n && soa.misses == n / 16); std::cout << "one-field sum misses: AoS " << aos.misses << " vs SoA " << soa.misses << "; "; }                                                       // ③
    { const int M = 512; Cache naive, tiled; uint64_t src = 0, dst = (uint64_t)M * M * 4 + 4096;
      for (int i = 0; i < M; i++) for (int j = 0; j < M; j++) { naive.access(src + ((uint64_t)i * M + j) * 4); naive.access(dst + ((uint64_t)j * M + i) * 4); }
      const int T = 16; for (int bi = 0; bi < M; bi += T) for (int bj = 0; bj < M; bj += T) for (int i = bi; i < bi + T; i++) for (int j = bj; j < bj + T; j++) { tiled.access(src + ((uint64_t)i * M + j) * 4); tiled.access(dst + ((uint64_t)j * M + i) * 4); }
      assert(tiled.misses * 4 < naive.misses); std::cout << "transpose misses: naive " << naive.misses << " vs 16x16 tiles " << tiled.misses << std::endl; }                                                                                                           // ④
    return 0;
}
// Time Complexity: 시뮬레이션은 접근당 O(ways); 실제 순회의 점근 복잡도는 같아도 미스 수가 수십 배 차이
// Space Complexity: O(캐시 크기)
```
## Amortized Analysis
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 분할상환 분석(Amortized Analysis): 연산 하나가 가끔 비싸더라도 연산 열 전체의 평균 비용이 작다면 그 평균을 연산의 비용으로 본다. 평균 사례 분석(입력 분포 가정)이나 확률적 분석과 다르게 최악의 연산 열에 대해서도 성립하는 결정론적 보장이다.
// 세 가지 기법: ① 총합법(aggregate): n 번 연산의 총 비용을 직접 세어 n 으로 나눈다 ② 회계법(banker's): 값싼 연산이 "신용(토큰)" 을 저축해 두었다가 비싼 연산에서 쓴다 ③ 퍼텐셜법(potential): 자료구조 상태의 퍼텐셜 Φ ≥ 0 를 정하고 분할상환 비용 = 실제 비용 + ΔΦ.
// 동적 배열의 push_back: 가득 차면 용량을 두 배로 늘려 전부 복사한다. Φ = 2·size − capacity 를 쓰면 일반 push 는 실제 1 + ΔΦ 2 = 3, 용량 확장 push 는 실제 1 + c 에 ΔΦ = 2 − c 라서 역시 3 — 모든 push 의 분할상환 비용이 3 이다. 반대로 용량을 일정량(+16)씩만 늘리면 복사가 Θ(N²/16) 로 폭발한다. 증가 배수가 1.5 여도 상수만 달라질 뿐 O(1) 이다.
// 축소 정책의 함정: 크기가 용량의 1/2 이하일 때 반으로 줄이면, 가득 찬 경계에서 push·pop 을 번갈아 하는 열이 매번 전체 복사를 일으킨다(thrashing). 1/4 이하일 때 반으로 줄이면 확장 직후 용량의 절반이 비어 있어 다음 확장·축소까지 최소 c/2 번의 연산이 필요하므로 분할상환 O(1) 이다.
// 이진 카운터: n 번 증가에서 비트 뒤집기 총 횟수는 정확히 2n − popcount(n) (< 2n) 이라 증가당 분할상환 2 다.
// 검증: ① 두 배 증가 총 복사 < 2N, 모든 push 의 퍼텐셜 분할상환 비용 ≤ 3 ② 배수 1.5 도 상수, +16 증가는 Θ(N²) ③ 축소 정책: 1/2 정책의 적대적 열은 연산당 Θ(N), 1/4 정책은 총 비용 ≤ 3·연산 수 + 초기 ④ 이진 카운터 총 뒤집기 == 2n − popcount(n) ⑤ 다중 pop 스택의 총 비용 ≤ 2n
struct DynArray {
    double growth; int add; long copies = 0, writes = 0; size_t size = 0, cap = 0;
    DynArray(double g, int a = 0) : growth(g), add(a) {}
    long push() { long cost = 1; if (size == cap) { size_t nc = add ? cap + add : (size_t)std::max<double>(cap * growth, cap + 1); copies += size; cost += size; cap = nc; } size++; writes++; return cost; }
};
struct Shrinking {                                                             // 확장은 두 배, 축소 정책을 선택
    size_t size = 0, cap = 1; double shrinkFraction; long cost = 0; explicit Shrinking(double f) : shrinkFraction(f) {}
    void push() { cost++; if (size == cap) { cost += size; cap *= 2; } size++; }
    void pop() { cost++; size--; if (cap > 1 && size <= cap * shrinkFraction) { cost += size; cap = std::max<size_t>(1, cap / 2); } }
};
int main() {
    { DynArray d(2.0); long phi = 0; long maxAmortized = 0; for (int i = 0; i < 100000; i++) { size_t capBefore = d.cap, sizeBefore = d.size; long actual = d.push(); long phiNew = 2 * (long)d.size - (long)d.cap, phiOld = 2 * (long)sizeBefore - (long)capBefore; if (sizeBefore == 0 && capBefore == 0) phiOld = 0; long amortized = actual + phiNew - phiOld; maxAmortized = std::max(maxAmortized, amortized); phi = phiNew; assert(phi >= 0); }       // ① 퍼텐셜법
      assert(maxAmortized <= 3 && d.copies < 2 * 100000); std::cout << "doubling: copies " << d.copies << " for 100000 pushes, max amortized cost " << maxAmortized << "; "; }
    { DynArray g(1.5), a(1.0, 16); for (int i = 0; i < 100000; i++) { g.push(); a.push(); } assert(g.copies < 3 * 100000 && a.copies > 100000L * 100000 / (2 * 16) / 2); std::cout << "x1.5 copies " << g.copies << ", +16 copies " << a.copies << "; "; }                                                   // ②
    { Shrinking half(0.5), quarter(0.25); for (int i = 0; i < 1024; i++) { half.push(); quarter.push(); } half.cost = quarter.cost = 0; long ops = 0; for (int r = 0; r < 2000; r++) { half.push(); half.pop(); quarter.push(); quarter.pop(); ops += 2; }               // 가득 찬 경계에서 push/pop 번갈아
      assert(half.cost > 100 * ops && quarter.cost <= 3 * ops + 2000); std::cout << "shrink at 1/2: " << half.cost / ops << " per op, at 1/4: " << (double)quarter.cost / ops << " per op; ";
      Shrinking q2(0.25); std::mt19937 rng(3); long total = 0, o = 0; for (int i = 0; i < 200000; i++) { if (rng() % 2 || q2.size == 0) q2.push(); else q2.pop(); o++; } total = q2.cost; assert(total <= 4 * o); }                                                                                    // ③ 무작위 열도 상수
    { unsigned long long counter = 0, flips = 0; const int n = 100000; for (int i = 1; i <= n; i++) { unsigned long long before = counter; counter++; flips += __builtin_popcountll(before ^ counter); assert(flips == 2ULL * i - __builtin_popcountll(counter)); } std::cout << "binary counter flips " << flips << " = 2n - popcount(n); "; }                                         // ④
    { std::mt19937 rng(4); long cost = 0, stack = 0, ops = 0; for (int i = 0; i < 100000; i++) { if (rng() % 3) { stack++; cost++; } else { long k = rng() % (stack + 1); stack -= k; cost += k + 1; } ops++; } assert(cost <= 2 * ops); std::cout << "multipop total cost " << cost << " <= 2 * ops " << 2 * ops << std::endl; }                                    // ⑤
    return 0;
}
// Time Complexity: push_back 분할상환 O(1) (최악 한 번은 O(N)), 이진 카운터 증가 분할상환 O(1)
// Space Complexity: O(N) (용량은 크기의 최대 2 배)
```
## Iterator Invalidation
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <list>
#include <map>
#include <stdexcept>
#include <unordered_map>
#include <vector>
#include <cassert>

// 반복자 무효화(Iterator Invalidation): 컨테이너를 수정하면 이미 얻어 둔 반복자·포인터·참조가 더는 유효하지 않을 수 있고, 그것을 쓰면 정의되지 않은 동작이다. 무효화 규칙은 컨테이너마다 다르다 —
//   vector: 재할당이 일어나면(용량 초과 push_back/insert/resize) 모든 반복자·참조·포인터 무효, 재할당이 없어도 삽입·삭제 지점 이후는 무효.  deque: 양 끝 삽입은 반복자만 무효(참조·포인터는 유효), 가운데 삽입·삭제는 모두 무효.
//   list/forward_list: 삽입은 아무것도 무효화하지 않고, 삭제는 지운 원소의 것만 무효.  map/set: 삽입은 무효화 없음, 삭제는 지운 원소만.  unordered_*: 재해시가 일어나면 반복자는 무효지만 원소 자체에 대한 참조·포인터는 유효.
// 이 항목은 정의되지 않은 동작을 건드리지 않고 규칙을 확인한다: 반복자를 역참조하지 않고 주소 비교, 용량 변화, 참조 안정성(원소의 주소가 그대로인지)만 본다. 또 실수를 런타임에 잡는 검사 반복자(버전 번호 방식; MSVC 디버그 반복자·_GLIBCXX_DEBUG 와 같은 아이디어)를 직접 만들어, 무효화된 반복자의 사용이 예외로 드러나는 것을 보인다.
// 올바른 관용구: ① 삭제하는 루프는 it = c.erase(it) 로 다음 위치를 받는다(아니면 ++it) ② 인덱스 루프에서 erase 하면 i 를 올리지 않거나 뒤에서 앞으로 ③ 조건 삭제는 erase–remove ④ 삽입이 잦으면 reserve 로 재할당 방지 ⑤ 주소가 고정되어야 하면 list/map/unique_ptr 를 쓴다.
// 검증: ① vector 재할당 시 data() 가 바뀌고 reserve 후에는 안 바뀜 ② list 삽입·삭제에서 다른 원소의 주소 불변 ③ deque push_back/push_front 후에도 기존 원소 참조 유효 ④ unordered_map 재해시(버킷 수 증가) 뒤에도 원소 참조 유효 ⑤ 검사 반복자가 stale 사용을 탐지 ⑥ 삭제 루프의 잘못된 인덱스 방식은 원소를 건너뛰고, 올바른 방식은 erase–remove 와 같은 결과
template <class T> class CheckedVector {
    std::vector<T> v; unsigned version = 0;
public:
    struct Iter { CheckedVector* owner; size_t index; unsigned version;
        T& operator*() const { if (version != owner->version) throw std::runtime_error("use of invalidated iterator"); return owner->v[index]; }
        Iter& operator++() { ++index; return *this; } bool operator!=(const Iter& o) const { return index != o.index; } };
    Iter begin() { return {this, 0, version}; } Iter end() { return {this, v.size(), version}; }
    void push_back(const T& x) { v.push_back(x); version++; }                    // 보수적으로 모든 구조 변경이 무효화
    Iter erase(Iter it) { v.erase(v.begin() + it.index); version++; return {this, it.index, version}; }       // 새 반복자를 돌려준다 -> 올바른 사용
    size_t size() const { return v.size(); }
};
int main() {
    { std::vector<int> v; v.push_back(1); const int* p = v.data(); size_t cap = v.capacity(); int changes = 0; for (int i = 0; i < 1000; i++) { v.push_back(i); if (v.capacity() != cap) { assert(v.data() != p); changes++; p = v.data(); cap = v.capacity(); } else assert(v.data() == p); } assert(changes >= 5);       // ① 재할당 <-> 주소 변경
      std::vector<int> w; w.reserve(5000); const int* q = w.data(); for (int i = 0; i < 5000; i++) w.push_back(i); assert(w.data() == q); }                                                                                                   // reserve 로 재할당 방지
    { std::list<int> l = {1, 2, 3, 4, 5}; std::vector<const int*> addr; for (auto& x : l) addr.push_back(&x); auto it = l.begin(); std::advance(it, 2); l.insert(it, 99); l.erase(std::next(l.begin(), 4)); std::vector<const int*> now; for (auto& x : l) now.push_back(&x);
      assert(now[0] == addr[0] && now[1] == addr[1] && now[3] == addr[2] && now[4] == addr[4]); }                                                                                                                        // ② 삭제한 원소(addr[3])를 뺀 나머지 주소 불변
    { std::deque<int> d = {1, 2, 3}; const int* first = &d[0]; const int* last = &d[2]; for (int i = 0; i < 10000; i++) { d.push_back(i); d.push_front(-i); } assert(first == &d[10000] && last == &d[10002]); }                                       // ③ 참조는 유효 (반복자는 무효)
    { std::unordered_map<int, int> m; m[1] = 10; int* ref = &m[1]; size_t buckets = m.bucket_count(); for (int i = 2; i < 5000; i++) m[i] = i; assert(m.bucket_count() > buckets && ref == &m[1] && *ref == 10); }                                  // ④ 재해시 후에도 원소 참조 유효
    { CheckedVector<int> cv; for (int i = 0; i < 5; i++) cv.push_back(i); auto it = cv.begin(); cv.push_back(5); bool threw = false; try { (void)*it; } catch (const std::runtime_error&) { threw = true; } assert(threw);                                       // ⑤ 수정 뒤 낡은 반복자 사용
      auto fresh = cv.begin(); assert(*fresh == 0);
      int removed = 0; for (auto j = cv.begin(); j != cv.end();) { if (*j % 2 == 0) { j = cv.erase(j); removed++; } else ++j; } assert(removed == 3 && cv.size() == 3); }                                                                                 // 올바른 삭제 루프
    { std::vector<int> run = {0, 0, 0, 1, 0, 0, 2}, wrong = run, right = run, idiom = run;
      for (size_t i = 0; i < wrong.size(); i++) if (wrong[i] == 0) wrong.erase(wrong.begin() + i);                                                        // 틀림: erase 뒤에도 i 를 올려 다음 원소를 건너뜀
      for (size_t i = 0; i < right.size();) { if (right[i] == 0) right.erase(right.begin() + i); else i++; }                                                 // 맞음: 지운 자리에서는 i 를 올리지 않는다
      idiom.erase(std::remove(idiom.begin(), idiom.end(), 0), idiom.end());
      long leftover = std::count(wrong.begin(), wrong.end(), 0); assert(leftover > 0 && right == idiom && std::count(right.begin(), right.end(), 0) == 0);                                                           // ⑥
      std::cout << "Iterator Invalidation: vector reallocation changed data() and never after reserve; list/deque/unordered_map kept element addresses; the checked iterator caught stale use; the buggy erase loop left " << leftover << " zeros behind while the correct loop and erase-remove removed all" << std::endl; }
    return 0;
}
// Time Complexity: 검사 반복자 역참조 O(1) (버전 비교 한 번)
// Space Complexity: 반복자당 추가 정수 하나
```
## Memory Fragmentation
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 메모리 단편화(Fragmentation): 전체 빈 메모리는 충분한데도 큰 요청이 실패하는 현상. 두 종류가 있다. 외부 단편화 — 빈 공간이 여러 조각으로 쪼개져 가장 큰 조각이 요청보다 작다. 내부 단편화 — 할당 단위(크기 등급)로 올림해서 블록 안쪽이 낭비된다.
// 크기가 제각각인 블록을 섞어 할당·해제하면 외부 단편화가 쌓인다. 대책: ① 같은 크기끼리 모으는 풀/슬랩 할당자는 어떤 빈 칸이든 어떤 요청이든 맞아 외부 단편화가 없다(내부는 크기 등급 선택에 달림) ② 인접한 빈 조각을 합치는 병합(coalescing) ③ 살아 있는 블록을 한쪽으로 몰아 큰 빈 조각을 만드는 압축(compaction, 이동 가능한 핸들이 있을 때) ④ 크기 등급을 촘촘히(1.25 배) 두면 2 의 거듭제곱 등급보다 내부 낭비가 줄지만 등급 수가 늘어난다.
// 이 항목은 아레나(1 MB) 위의 첫 적합(first-fit) 할당자를 직접 만들어 실험한다: 외부 단편화 지표 = 1 − (가장 큰 빈 조각 / 전체 빈 공간). ① 할당자 불변식(블록이 겹치지 않음, 빈 조각은 인접하면 합쳐져 있음, 총합 일치) ② 1 KB 블록을 꽉 채우고 하나 걸러 해제하면 단편화 지표가 0.99 를 넘고 큰 요청(64 KB)이 전체 빈 공간(512 KB)이 충분한데도 실패 ③ 압축 뒤에는 같은 요청 성공 ④ 같은 크기 부하(풀)에서는 요청이 실패하는 일이 없음 ⑤ 내부 단편화: 2 의 거듭제곱 등급의 평균 낭비가 1.25 배 등급보다 크다
struct Heap {
    size_t cap; std::map<size_t, size_t> freeList, live;                         // 오프셋 -> 크기
    explicit Heap(size_t c) : cap(c) { freeList[0] = c; }
    long alloc(size_t n) { for (auto it = freeList.begin(); it != freeList.end(); ++it) if (it->second >= n) { size_t off = it->first, sz = it->second; freeList.erase(it); if (sz > n) freeList[off + n] = sz - n; live[off] = n; return (long)off; } return -1; }
    void release(size_t off) { size_t n = live[off]; live.erase(off); auto it = freeList.emplace(off, n).first; auto nx = std::next(it); if (nx != freeList.end() && it->first + it->second == nx->first) { it->second += nx->second; freeList.erase(nx); } if (it != freeList.begin()) { auto pv = std::prev(it); if (pv->first + pv->second == it->first) { pv->second += it->second; freeList.erase(it); } } }
    size_t totalFree() const { size_t s = 0; for (auto& f : freeList) s += f.second; return s; }
    size_t largestFree() const { size_t m = 0; for (auto& f : freeList) m = std::max(m, f.second); return m; }
    double fragmentation() const { size_t t = totalFree(); return t ? 1.0 - (double)largestFree() / t : 0.0; }
    bool check() const { std::map<size_t, size_t> all; for (auto& f : freeList) all[f.first] = f.second; for (auto& l : live) all[l.first] = l.second; size_t pos = 0, sum = 0; for (auto& b : all) { if (b.first != pos) return false; pos += b.second; } for (auto it = freeList.begin(); it != freeList.end(); ++it) { sum += it->second; auto nx = std::next(it); if (nx != freeList.end() && it->first + it->second == nx->first) return false; } size_t liveSum = 0; for (auto& l : live) liveSum += l.second; return pos == cap && sum + liveSum == cap; }
    size_t compact() { size_t pos = 0; std::map<size_t, size_t> moved; for (auto& l : live) { moved[pos] = l.second; pos += l.second; } live = moved; freeList.clear(); if (pos < cap) freeList[pos] = cap - pos; return pos; }          // 살아 있는 블록을 앞으로 몰기
};
int main() {
    std::mt19937 rng(8); const size_t CAP = 1 << 20; Heap h(CAP); std::vector<size_t> offs;
    for (;;) { size_t n = 16 + rng() % 1009; long o = h.alloc(n); if (o < 0 || h.cap - h.totalFree() > CAP * 85 / 100) break; offs.push_back((size_t)o); }
    for (int round = 0; round < 40; round++) { for (size_t k = 0; k < offs.size() / 2; k++) { size_t i = rng() % offs.size(); h.release(offs[i]); offs[i] = offs.back(); offs.pop_back(); } for (;;) { size_t n = 16 + rng() % 1009; if (h.cap - h.totalFree() + n > CAP * 85 / 100) break; long o = h.alloc(n); if (o < 0) break; offs.push_back((size_t)o); } assert(h.check()); }          // ① 불변식 유지
    double churnFrag = h.fragmentation(); assert(h.check() && churnFrag >= 0.0);                                                                                                                      // ① 무작위 교체 뒤에도 불변식 유지
    Heap cb(CAP); std::vector<size_t> blocks; for (int i = 0; i < 1024; i++) blocks.push_back((size_t)cb.alloc(1024)); for (size_t i = 1; i < blocks.size(); i += 2) cb.release(blocks[i]);        // 1 KB 블록을 꽉 채우고 하나 걸러 해제
    size_t big = 64 * 1024, freeBefore = cb.totalFree(), largestBefore = cb.largestFree(); double frag = cb.fragmentation(); assert(cb.check() && freeBefore == CAP / 2 && largestBefore == 1024 && frag > 0.99);                         // ② 절반이 비었는데 가장 큰 조각은 1 KB
    assert(cb.alloc(big) < 0); cb.compact(); assert(cb.check() && cb.largestFree() == freeBefore && cb.alloc(big) >= 0);                                                                                    // ③ 압축 후 같은 요청 성공
    { Heap pool(CAP); std::vector<size_t> pv; const size_t B = 64; for (size_t i = 0; i < CAP / B; i++) pv.push_back((size_t)pool.alloc(B)); long failures = 0;
      for (int round = 0; round < 20000; round++) { size_t i = rng() % pv.size(); pool.release(pv[i]); long o = pool.alloc(B); if (o < 0) failures++; else pv[i] = (size_t)o; } assert(failures == 0 && pool.check()); }                                       // ④ 같은 크기 부하는 실패하지 않는다
    double wastePow2 = 0, wasteGeo = 0; const int T = 100000; for (int t = 0; t < T; t++) { size_t n = 17 + rng() % 4000; size_t p2 = 1; while (p2 < n) p2 <<= 1; double c = 16; while (c < n) c = std::ceil(c * 1.25); wastePow2 += (double)(p2 - n) / p2; wasteGeo += (c - n) / c; }
    wastePow2 /= T; wasteGeo /= T; assert(wastePow2 > wasteGeo * 1.4 && wastePow2 > 0.2 && wasteGeo < 0.15);                                                                                                                                                                                      // ⑤ 내부 단편화
    std::cout << "Memory Fragmentation: random churn left fragmentation index " << churnFrag << "; a checkerboard of 1 KB blocks had " << freeBefore << " bytes free but the largest hole was only " << largestBefore << " (index " << frag << "), so a " << big << "-byte request failed until compaction; fixed-size pool never failed; internal waste: power-of-two classes " << wastePow2 << " vs 1.25x classes " << wasteGeo << std::endl; return 0;
}
// Time Complexity: 첫 적합 할당 O(빈 조각 수), 해제 O(log N), 압축 O(살아 있는 블록 수)
// Space Complexity: O(블록 수) 메타데이터
```
## False Sharing
### 대표코드
```cpp
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <map>
#include <thread>
#include <vector>
#include <cassert>

// 거짓 공유(False Sharing): 서로 다른 스레드가 서로 다른 변수를 쓰는데도, 그 변수들이 같은 캐시 라인(64 B)에 있으면 코어들이 라인의 소유권을 두고 핑퐁한다. 캐시 일관성 프로토콜(MESI)에서 한 코어가 라인에 쓰려면 다른 코어의 복사본을 무효화해야 하고, 무효화된 코어가 다시 읽거나 쓸 때 라인을 새로 가져와야 하기 때문이다.
// 논리적으로는 공유가 없는데 성능은 공유한 것처럼 떨어진다: 스레드별 카운터를 배열에 붙여 두면 (8 바이트 × 8 개 = 한 라인) 코어가 늘수록 오히려 느려질 수 있다. 해결은 변수마다 라인 크기로 정렬·패딩(alignas(64))하거나, 스레드 지역 변수에 누적하다가 마지막에 합치는 것이다.
// 실제 시간은 기계마다 달라 단언에 쓸 수 없으므로 두 가지로 확인한다. ① 결정적 시뮬레이터: 코어별 라인 소유 상태(M)를 추적하는 일관성 모델에 쓰기 열을 흘려 "무효화 횟수" 를 센다 — 두 코어가 같은 라인의 다른 주소를 번갈아 쓰면 쓰기마다 무효화가 일어나고(N−1 회), 주소가 64 B 떨어져 있으면 최초 소유 이후 0 회다 ② 실제 스레드: 패딩한 카운터와 붙은 카운터를 모두 정확히 증가시켜 결과가 같음을 검증하고(원자 연산이라 정확성은 같다) 걸린 시간은 참고용으로만 출력한다 — 주소가 같은 라인에 있는지는 결정적으로 단언한다
struct Coherence {                                                              // 단순화한 쓰기 무효화 모델: 라인당 현재 소유 코어 하나
    std::map<uint64_t, int> owner; long invalidations = 0, coldMisses = 0;
    void write(int core, uint64_t addr) { uint64_t line = addr >> 6; auto it = owner.find(line); if (it == owner.end()) { coldMisses++; owner[line] = core; } else if (it->second != core) { invalidations++; it->second = core; } }
};
struct Packed { std::atomic<long> v; };                                         // 8 바이트 -> 한 라인에 8 개
struct alignas(64) Padded { std::atomic<long> v; };                              // 라인 하나를 독점
int main() {
    static_assert(sizeof(Padded) == 64 && alignof(Padded) == 64, "one counter per cache line");
    const int N = 100000;
    { Coherence same, apart; for (int i = 0; i < N; i++) for (int core = 0; core < 2; core++) { same.write(core, 0x1000 + core * 8); apart.write(core, 0x1000 + core * 64); } assert(same.invalidations == 2 * N - 1 && same.coldMisses == 1 && apart.invalidations == 0 && apart.coldMisses == 2); }          // ① 같은 라인: 쓰기마다 무효화
    { Coherence four; for (int i = 0; i < N; i++) for (int core = 0; core < 4; core++) four.write(core, 0x2000 + core * 8); assert(four.invalidations == 4 * N - 1); Coherence local; for (int core = 0; core < 4; core++) { long sum = 0; for (int i = 0; i < N; i++) sum++; local.write(core, 0x3000 + core * 64); assert(sum == N); } assert(local.invalidations == 0); }               // 4 코어, 그리고 지역 누적 후 한 번 쓰기
    alignas(64) static Packed packed[8]; alignas(64) static Padded padded[8];
    assert(((uintptr_t)&packed[0] >> 6) == ((uintptr_t)&packed[7] >> 6) && ((uintptr_t)&padded[0] >> 6) != ((uintptr_t)&padded[1] >> 6));                                                                 // 붙은 카운터는 같은 라인, 패딩한 것은 서로 다른 라인
    long packedMs = 0, paddedMs = 0; const long ITER = 2000000;
    for (int variant = 0; variant < 2; variant++) { auto t0 = std::chrono::steady_clock::now(); std::vector<std::thread> ts; for (int t = 0; t < 4; t++) ts.emplace_back([&, t, variant] { std::atomic<long>& c = variant ? padded[t].v : packed[t].v; for (long i = 0; i < ITER; i++) c.fetch_add(1, std::memory_order_relaxed); }); for (auto& t : ts) t.join(); auto t1 = std::chrono::steady_clock::now(); (variant ? paddedMs : packedMs) = std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count(); }
    for (int t = 0; t < 4; t++) assert(packed[t].v.load() == ITER && padded[t].v.load() == ITER);                                                                                                           // ② 정확성은 같다
    std::cout << "False Sharing: simulated coherence invalidations " << 2 * N - 1 << " for two writers in one cache line vs 0 when 64 bytes apart; real threads counted exactly in both layouts (packed " << packedMs << " ms, padded " << paddedMs << " ms - timing is informational only)" << std::endl; return 0;
}
// Time Complexity: 해당 없음 (캐시 일관성 비용 모델)
// Space Complexity: 변수당 캐시 라인 하나 (64 B) — 메모리를 써서 시간을 산다
```
## Lock-Free Linked List
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <climits>
#include <cstdint>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <thread>
#include <vector>
#include <cassert>

// 락프리 연결 리스트(Harris 2001, Michael 2002): 잠금 없이 CAS(compare-and-swap)만으로 정렬 연결 리스트의 삽입·삭제·검색을 한다. 한 스레드가 멈춰도 다른 스레드가 계속 진행한다.
// 삭제가 까다롭다: 노드 x 를 지우는 CAS(pred.next: x -> x.next)와 x 바로 뒤에 y 를 넣는 CAS(x.next: z -> y)가 동시에 성공하면 y 가 사라진다. 해법은 두 단계 삭제 — ① 논리 삭제: x.next 의 표시(mark) 비트를 CAS 로 켠다(이후 x.next 는 아무도 바꿀 수 없음) ② 물리 삭제: pred.next 를 건너뛰게 CAS. 탐색 중 표시된 노드를 만난 스레드가 대신 물리 삭제를 도와준다(helping).
// 또 하나의 함정은 ABA 와 메모리 회수다. 노드를 풀에 돌려주고 재사용하면, 낡은 값 (x, 같은 포인터)을 쥔 스레드의 CAS 가 "주소가 같다" 는 이유만으로 성공해 구조가 깨진다. 이 구현은 링크 워드 = [31비트 태그 | 표시 1비트 | 32비트 인덱스] 로 두고 모든 성공한 CAS 가 태그를 올리게 해서 낡은 CAS 는 반드시 실패한다. 노드는 고정 풀에서 인덱스로 가리키며(형 안정 메모리) 탐색은 읽은 뒤 pred 링크가 그대로인지 재확인한다(Michael 의 검증).
// Set.md Part 15 의 LockFreeSet 은 같은 알고리즘을 포인터와 지연 해제로 쓴다. 여기서는 ABA 를 결정적으로 재현하고(태그 없음: 파괴, 태그 있음: 안전한 실패), 태그 풀 위에서 4 스레드 스트레스를 돌린다.
// 검증: ① 단일 스레드: std::set 과 연산 결과·내용 동일 ② ABA 시나리오(스크립트로 교차 실행): 태그 없는 스택은 이미 팝된 노드가 다시 스택에 올라가고, 태그 있는 스택은 CAS 가 실패 ③ 4 스레드 × 20만 연산, 키 64 개: 키별 (성공한 삽입 − 성공한 삭제) 가 최종 존재 여부와 같고(0 또는 1) 리스트가 순증가이며 풀의 노드가 하나도 새거나 중복되지 않음
typedef uint64_t W; const uint32_t NIL = 0xFFFFFFFFu;
inline W mk(uint64_t tag, bool mark, uint32_t idx) { return (tag << 33) | ((W)mark << 32) | idx; }
inline uint32_t ix(W w) { return (uint32_t)w; } inline bool isMarked(W w) { return (w >> 32) & 1; } inline uint64_t tg(W w) { return w >> 33; }
class LFList {
    struct Node { std::atomic<int> key{0}; std::atomic<W> next{0}; };
    std::unique_ptr<Node[]> nodes; std::unique_ptr<std::atomic<uint32_t>[]> fnext; std::atomic<W> freeHead; uint32_t cap;
    uint32_t alloc() { for (;;) { W h = freeHead.load(); uint32_t i = ix(h); if (i == NIL) return NIL; uint32_t nx = fnext[i].load(); if (freeHead.compare_exchange_weak(h, mk(tg(h) + 1, false, nx))) return i; } }
    void release(uint32_t i) { for (;;) { W h = freeHead.load(); fnext[i].store(ix(h)); if (freeHead.compare_exchange_weak(h, mk(tg(h) + 1, false, i))) return; } }
    bool find(int key, uint32_t& pred, W& predW, uint32_t& curr, W& currW) {             // key 이상인 첫 노드 curr 와 그 앞 pred 를 돌려준다. 표시된 노드는 지나가며 물리 삭제
    retry:
        pred = 0; predW = nodes[0].next.load(); curr = ix(predW);
        for (;;) {
            currW = nodes[curr].next.load(); int ck = nodes[curr].key.load();
            if (nodes[pred].next.load() != predW) goto retry;                                  // pred 링크가 그대로여야 curr 가 아직 연결되어 있고 재사용되지 않았다
            if (isMarked(currW)) { W repl = mk(tg(predW) + 1, false, ix(currW)); if (!nodes[pred].next.compare_exchange_strong(predW, repl)) goto retry; release(curr); predW = repl; curr = ix(repl); continue; }          // 도와서 물리 삭제 (성공한 쪽만 풀로 반환)
            if (ck >= key) return ck == key;
            pred = curr; predW = currW; curr = ix(currW);
        }
    }
public:
    explicit LFList(uint32_t capacity) : nodes(new Node[capacity + 2]), fnext(new std::atomic<uint32_t>[capacity + 2]), cap(capacity) {
        nodes[0].key = INT_MIN; nodes[1].key = INT_MAX; nodes[0].next = mk(0, false, 1); nodes[1].next = mk(0, false, NIL);
        for (uint32_t i = 2; i < capacity + 2; i++) fnext[i] = i + 1 < capacity + 2 ? i + 1 : NIL; freeHead = mk(0, false, capacity ? 2 : NIL);
    }
    bool insert(int key) {
        uint32_t n = NIL; uint32_t pred, curr; W predW, currW;
        for (;;) {
            if (find(key, pred, predW, curr, currW)) { if (n != NIL) release(n); return false; }
            if (n == NIL) { n = alloc(); assert(n != NIL); nodes[n].key.store(key); }
            W old = nodes[n].next.load(); nodes[n].next.store(mk(tg(old) + 1, false, curr));                                // 새 노드의 태그는 이전 생애보다 계속 증가
            if (nodes[pred].next.compare_exchange_strong(predW, mk(tg(predW) + 1, false, n))) return true;
        }
    }
    bool remove(int key) {
        uint32_t pred, curr; W predW, currW;
        for (;;) {
            if (!find(key, pred, predW, curr, currW)) return false;
            if (!nodes[curr].next.compare_exchange_strong(currW, mk(tg(currW) + 1, true, ix(currW)))) continue;                  // 논리 삭제: 표시 비트 켜기
            W repl = mk(tg(predW) + 1, false, ix(currW)); if (nodes[pred].next.compare_exchange_strong(predW, repl)) release(curr); else find(key, pred, predW, curr, currW);   // 물리 삭제 (실패하면 탐색이 대신 처리)
            return true;
        }
    }
    bool contains(int key) { uint32_t p, c; W pw, cw; return find(key, p, pw, c, cw); }
    std::vector<int> toVector(size_t* markedLeft = nullptr) const { std::vector<int> v; size_t marked = 0; for (uint32_t i = ix(nodes[0].next.load()); i != 1 && i != NIL; i = ix(nodes[i].next.load())) { if (isMarked(nodes[i].next.load())) marked++; else v.push_back(nodes[i].key.load()); } if (markedLeft) *markedLeft = marked; return v; }
    size_t freeCount() const { size_t c = 0; for (uint32_t i = ix(freeHead.load()); i != NIL; i = fnext[i].load()) c++; return c; }
    size_t capacity() const { return cap; }
};
struct Stack {                                                                           // ABA 시연용: 인덱스 풀 위의 Treiber 스택. tagged 면 헤드 워드에 태그를 붙인다
    bool tagged; uint64_t head; uint32_t next[8]; explicit Stack(bool t) : tagged(t), head(mk(0, false, NIL)) { for (auto& n : next) n = NIL; }
    void push(uint32_t i) { next[i] = ix(head); head = mk(tagged ? tg(head) + 1 : 0, false, i); }
    uint32_t pop() { uint32_t i = ix(head); if (i == NIL) return NIL; head = mk(tagged ? tg(head) + 1 : 0, false, next[i]); return i; }
    bool cas(uint64_t expected, uint64_t desired) { if (head != expected) return false; head = desired; return true; }
};
int main() {
    { std::mt19937 rng(3); LFList l(400); std::set<int> ref; for (int step = 0; step < 100000; step++) { int k = rng() % 300, op = rng() % 3; if (op == 0) assert(l.insert(k) == ref.insert(k).second); else if (op == 1) assert(l.remove(k) == (ref.erase(k) == 1)); else assert(l.contains(k) == (ref.count(k) == 1)); }
      size_t marked = 0; auto v = l.toVector(&marked); assert(marked == 0 && v == std::vector<int>(ref.begin(), ref.end()) && l.freeCount() + ref.size() == l.capacity()); }                                       // ① 단일 스레드
    for (int tagged = 0; tagged < 2; tagged++) {                                         // ② ABA: 스택 X -> Y -> Z. A 는 pop 을 시작(top=X, next=Y 읽음)하고 멈춘다. B 가 X, Y 를 pop 하고 X 를 다시 push.
        Stack s(tagged); s.push(2); s.push(1); s.push(0); uint64_t seenHead = s.head; uint32_t seenTop = ix(seenHead), seenNext = s.next[seenTop]; assert(seenTop == 0 && seenNext == 1);
        uint32_t b1 = s.pop(), b2 = s.pop(); s.push(b1); assert(b1 == 0 && b2 == 1 && ix(s.head) == 0);                       // B: 0 과 1 을 가져가고 0 을 되돌림 (스택: 0 -> 2)
        bool ok = s.cas(seenHead, mk(tagged ? tg(seenHead) + 1 : 0, false, seenNext));                                     // A 가 깨어나 CAS 시도
        if (!tagged) { assert(ok && ix(s.head) == 1);  /* 이미 B 가 소유한 노드 1 이 스택 맨 위에 다시 올라가고 노드 0 은 사라졌다 */ } else { assert(!ok && ix(s.head) == 0); }
    }
    const int KEYS = 64, THREADS = 4, OPS = 200000; LFList list(KEYS + THREADS * 8); std::vector<std::vector<int>> net(THREADS, std::vector<int>(KEYS, 0)); std::vector<std::thread> ts;
    for (int t = 0; t < THREADS; t++) ts.emplace_back([&, t] { std::mt19937 rng(100 + t); for (int i = 0; i < OPS; i++) { int k = rng() % KEYS, op = rng() % 3; if (op == 0) { if (list.insert(k)) net[t][k]++; } else if (op == 1) { if (list.remove(k)) net[t][k]--; } else list.contains(k); } });
    for (auto& th : ts) th.join();
    size_t marked = 0; std::vector<int> fin = list.toVector(&marked); std::set<int> present(fin.begin(), fin.end()); assert(present.size() == fin.size() && std::is_sorted(fin.begin(), fin.end()));                                    // 순증가
    for (int k = 0; k < KEYS; k++) { int sum = 0; for (int t = 0; t < THREADS; t++) sum += net[t][k]; assert(sum == (present.count(k) ? 1 : 0)); }                                                                                      // ③ 키별 순합 == 존재 여부
    assert(list.freeCount() + fin.size() + marked == list.capacity());                                                                                                                                                       // 노드가 새거나 중복되지 않음
    std::cout << "Lock-Free Linked List: single-thread run matched std::set; the scripted ABA corrupted the untagged stack but failed safely with tags; " << THREADS << " threads x " << OPS << " operations left " << fin.size() << " keys with per-key insert/remove balance exact and no leaked pool nodes" << std::endl; return 0;
}
// Time Complexity: 검색·삽입·삭제 O(N) (CAS 재시도는 경쟁에 비례)
// Space Complexity: O(고정 풀 크기)
```
## Concurrent List
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <climits>
#include <iostream>
#include <mutex>
#include <random>
#include <set>
#include <thread>
#include <vector>
#include <cassert>

// 동시성 리스트(Concurrent List): 여러 스레드가 공유하는 정렬 연결 리스트를 안전하게 만드는 방법은 잠금의 단위에 따라 단계가 나뉜다(Herlihy–Shavit 의 분류).
//   ① 조대 잠금(coarse-grained): 리스트 전체에 뮤텍스 하나. 정확하지만 모든 연산이 직렬화된다.  ② 손잡이 교대 잠금(hand-over-hand / lock coupling): 노드마다 뮤텍스를 두고 pred 를 잠근 채 curr 를 잠근 뒤 pred 를 풀며 전진 — 서로 다른 구간은 동시에 일하지만 매 노드마다 잠금이 필요하고 앞에서 느린 연산이 뒤를 막는다.
//   ③ 게으른 동기화(lazy synchronization): 탐색은 잠금 없이 하고, 수정할 pred·curr 두 노드만 잠근 뒤 검증(둘 다 삭제 표시가 없고 pred.next == curr)한다. 삭제는 먼저 marked 를 켜서(논리) 연결에서 뗀다(물리). contains 는 잠금이 없다(wait-free).
// 삭제된 노드는 다른 스레드가 아직 읽고 있을 수 있으므로 바로 해제하지 않고 폐기 목록에 모았다가 리스트가 사라질 때 해제한다(안전한 메모리 회수는 hazard pointer / epoch 방식이 필요 — 락프리 항목 참고).
// 검증: ① 세 구현이 단일 스레드에서 std::set 과 완전히 같다 ② 4 스레드 스트레스(키 32 개): 키별 (성공한 삽입 − 성공한 삭제) 합이 최종 존재 여부와 같고 리스트는 순증가 ③ 게으른 리스트에서는 contains 가 잠금을 전혀 잡지 않음(잠금 획득 횟수 카운터로 확인)
struct CoarseList {
    struct Node { int key; Node* next; }; Node* head; std::mutex m; std::atomic<long> locks{0};
    CoarseList() { head = new Node{INT_MIN, new Node{INT_MAX, nullptr}}; }
    ~CoarseList() { while (head) { Node* n = head->next; delete head; head = n; } }
    bool add(int k) { std::lock_guard<std::mutex> g(m); locks++; Node* p = head; while (p->next->key < k) p = p->next; if (p->next->key == k) return false; p->next = new Node{k, p->next}; return true; }
    bool remove(int k) { std::lock_guard<std::mutex> g(m); locks++; Node* p = head; while (p->next->key < k) p = p->next; if (p->next->key != k) return false; Node* d = p->next; p->next = d->next; delete d; return true; }
    bool contains(int k) { std::lock_guard<std::mutex> g(m); locks++; Node* p = head; while (p->key < k) p = p->next; return p->key == k; }
    std::vector<int> toVector() const { std::vector<int> v; for (Node* p = head->next; p->next; p = p->next) v.push_back(p->key); return v; }
};
struct HandOverHandList {
    struct Node { int key; Node* next; std::mutex m; Node(int k, Node* n) : key(k), next(n) {} }; Node* head; std::atomic<long> locks{0};
    HandOverHandList() { head = new Node(INT_MIN, new Node(INT_MAX, nullptr)); }
    ~HandOverHandList() { while (head) { Node* n = head->next; delete head; head = n; } }
    template <class F> bool walk(int k, F f) { head->m.lock(); locks++; Node* pred = head; Node* curr = pred->next; curr->m.lock(); locks++; while (curr->key < k) { pred->m.unlock(); pred = curr; curr = curr->next; curr->m.lock(); locks++; } bool r = f(pred, curr); curr->m.unlock(); pred->m.unlock(); return r; }
    bool add(int k) { return walk(k, [&](Node* p, Node* c) { if (c->key == k) return false; p->next = new Node(k, c); return true; }); }
    bool remove(int k) { Node* dead = nullptr; bool r = walk(k, [&](Node* p, Node* c) { if (c->key != k) return false; p->next = c->next; dead = c; return true; }); delete dead; return r; }          // 두 잠금을 모두 푼 뒤에 해제 (이 노드에 접근할 수 있는 다른 스레드는 없다)
    bool contains(int k) { return walk(k, [&](Node*, Node* c) { return c->key == k; }); }
    std::vector<int> toVector() const { std::vector<int> v; for (Node* p = head->next; p->next; p = p->next) v.push_back(p->key); return v; }
};
struct LazyList {
    struct Node { int key; std::atomic<Node*> next; std::atomic<bool> marked{false}; std::mutex m; Node(int k, Node* n) : key(k), next(n) {} };
    Node* head; std::atomic<long> locks{0}; std::mutex retireM; std::vector<Node*> retired;
    LazyList() { head = new Node(INT_MIN, new Node(INT_MAX, nullptr)); }
    ~LazyList() { for (Node* n : retired) delete n; while (head) { Node* n = head->next; delete head; head = n; } }
    bool validate(Node* p, Node* c) { return !p->marked && !c->marked && p->next.load() == c; }
    bool add(int k) { for (;;) { Node* p = head; Node* c = p->next; while (c->key < k) { p = c; c = c->next; } std::lock_guard<std::mutex> g1(p->m), g2(c->m); locks += 2; if (!validate(p, c)) continue; if (c->key == k) return false; p->next.store(new Node(k, c)); return true; } }
    bool remove(int k) { for (;;) { Node* p = head; Node* c = p->next; while (c->key < k) { p = c; c = c->next; } std::lock_guard<std::mutex> g1(p->m), g2(c->m); locks += 2; if (!validate(p, c)) continue; if (c->key != k) return false; c->marked.store(true); p->next.store(c->next.load()); { std::lock_guard<std::mutex> rg(retireM); retired.push_back(c); } return true; } }
    bool contains(int k) { Node* c = head; while (c->key < k) c = c->next; return c->key == k && !c->marked; }                                // 잠금 없음
    std::vector<int> toVector() const { std::vector<int> v; for (Node* p = head->next; p->next.load(); p = p->next) v.push_back(p->key); return v; }
};
template <class L> void verify(const char* name, long& lockAcquisitions) {
    { L l; std::set<int> ref; std::mt19937 rng(1); for (int i = 0; i < 20000; i++) { int k = rng() % 200, op = rng() % 3; if (op == 0) assert(l.add(k) == ref.insert(k).second); else if (op == 1) assert(l.remove(k) == (ref.erase(k) == 1)); else assert(l.contains(k) == (ref.count(k) == 1)); } assert(l.toVector() == std::vector<int>(ref.begin(), ref.end())); }          // ①
    const int KEYS = 32, THREADS = 4, OPS = 30000; L l; std::vector<std::vector<int>> net(THREADS, std::vector<int>(KEYS, 0)); std::vector<std::thread> ts;
    for (int t = 0; t < THREADS; t++) ts.emplace_back([&, t] { std::mt19937 rng(50 + t); for (int i = 0; i < OPS; i++) { int k = rng() % KEYS, op = rng() % 3; if (op == 0) { if (l.add(k)) net[t][k]++; } else if (op == 1) { if (l.remove(k)) net[t][k]--; } else l.contains(k); } });
    for (auto& th : ts) th.join(); std::vector<int> fin = l.toVector(); std::set<int> present(fin.begin(), fin.end()); assert(present.size() == fin.size() && std::is_sorted(fin.begin(), fin.end()));
    for (int k = 0; k < KEYS; k++) { int sum = 0; for (int t = 0; t < THREADS; t++) sum += net[t][k]; assert(sum == (present.count(k) ? 1 : 0)); }                                                            // ②
    lockAcquisitions = l.locks.load(); std::cout << name << ": " << fin.size() << " keys left, " << lockAcquisitions << " lock acquisitions; ";
}
int main() {
    long coarse = 0, hoh = 0, lazy = 0; verify<CoarseList>("coarse", coarse); verify<HandOverHandList>("hand-over-hand", hoh); verify<LazyList>("lazy", lazy);
    { LazyList l; for (int i = 0; i < 100; i++) l.add(i); long before = l.locks.load(); for (int i = 0; i < 1000; i++) l.contains(i % 150); assert(l.locks.load() == before); }                                               // ③ contains 는 잠금을 잡지 않는다
    assert(hoh > coarse && lazy < hoh);
    std::cout << "\nConcurrent List: all three strategies matched std::set and kept per-key balance under 4 threads; lazy contains took no locks" << std::endl; return 0;
}
// Time Complexity: 조대 O(N) 직렬, 손잡이 교대 O(N) (노드마다 잠금), 게으른 O(N) 탐색 + 잠금 2 개
// Space Complexity: O(N) (+ 폐기 목록)
```
## Copy-on-Write List
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <iostream>
#include <memory>
#include <mutex>
#include <thread>
#include <vector>
#include <cassert>

// 쓰기 시 복사(Copy-on-Write) 리스트: 읽기는 아주 많고 쓰기는 드문 곳(이벤트 리스너 목록, 설정 스냅샷)을 위한 구조다. 데이터는 불변 벡터 하나를 가리키는 공유 포인터이고, 읽는 쪽은 그 포인터를 한 번 복사해 쥐기만 하면(스냅샷) 이후 쓰기와 상관없이 일관된 내용을 잠금 없이 순회한다.
// 쓰는 쪽은 현재 벡터를 통째로 복사해 수정하고 포인터를 새것으로 바꿔 끼운다(RCU 와 같은 발상; Java 의 CopyOnWriteArrayList). 쓰기 한 번이 O(N) 이므로 N 번 연속 쓰기는 Θ(N²) 복사이고, 그래서 쓰기가 잦은 곳에는 맞지 않다. 여러 변경을 한 번의 복사로 묶는 일괄 수정(modify)으로 줄일 수 있다.
// 쓰기 스레드가 여럿이면 두 가지 방식이 있다: 뮤텍스로 쓰기를 직렬화하거나, 복사한 벡터를 만든 뒤 CAS 로 교체해 보고 실패하면 새 스냅샷에서 다시 하는 낙관적 방식. 또 하나의 변종은 "복사 지연": 참조 계수가 1 이면(나만 쥐고 있으면) 제자리에서 수정하고 공유 중일 때만 복사한다.
// 검증: ① 쓰기 하나가 1..K 를 순서대로 추가하는 동안 읽기 세 스레드가 얻은 모든 스냅샷은 정확히 [1..k] 이다(찢어진 내용 없음) 이고 읽기 스레드마다 크기가 단조 증가 ② 총 복사 원소 수 == N(N−1)/2 ③ 이미 얻은 스냅샷은 이후 1000 번의 수정에도 변하지 않음 ④ CAS 방식 다중 쓰기: 네 스레드가 서로 다른 값 2000 개씩 추가해도 하나도 잃지 않음 ⑤ 복사 지연: 공유 중일 때 첫 쓰기만 복사
template <class T> class CowList {
    typedef std::shared_ptr<const std::vector<T>> Ptr; Ptr data_; std::mutex writers_; std::atomic<long> copied_{0}, retries_{0};
public:
    CowList() : data_(std::make_shared<const std::vector<T>>()) {}
    Ptr snapshot() const { return std::atomic_load(&data_); }                              // 읽기: 잠금 없이 포인터 하나 복사
    void push_back(const T& v) { std::lock_guard<std::mutex> g(writers_); Ptr cur = std::atomic_load(&data_); auto nu = std::make_shared<std::vector<T>>(*cur); copied_ += (long)cur->size(); nu->push_back(v); std::atomic_store(&data_, Ptr(nu)); }
    template <class F> void modify(F f) { std::lock_guard<std::mutex> g(writers_); Ptr cur = std::atomic_load(&data_); auto nu = std::make_shared<std::vector<T>>(*cur); copied_ += (long)cur->size(); f(*nu); std::atomic_store(&data_, Ptr(nu)); }       // 일괄 수정: 복사 한 번
    void pushBackOptimistic(const T& v) { for (;;) { Ptr cur = std::atomic_load(&data_); auto nu = std::make_shared<std::vector<T>>(*cur); nu->push_back(v); Ptr expected = cur; if (std::atomic_compare_exchange_strong(&data_, &expected, Ptr(nu))) return; retries_++; } }          // CAS: 실패하면 새 스냅샷에서 다시
    long copied() const { return copied_.load(); } long retries() const { return retries_.load(); }
};
struct LazyCowVec {                                                                     // 복사 지연: 공유 중일 때만 복사
    std::shared_ptr<std::vector<int>> d = std::make_shared<std::vector<int>>(); static long copies;
    void set(size_t i, int v) { if (d.use_count() > 1) { d = std::make_shared<std::vector<int>>(*d); copies++; } (*d)[i] = v; }
};
long LazyCowVec::copies = 0;
int main() {
    const int N = 2000; CowList<int> list; std::atomic<bool> done{false}; std::atomic<long> checked{0}; std::vector<std::thread> readers;
    for (int r = 0; r < 3; r++) readers.emplace_back([&] { size_t last = 0; while (!done.load() || true) { auto snap = list.snapshot(); size_t k = snap->size(); assert(k >= last); last = k; for (size_t i = 0; i < k; i++) assert((*snap)[i] == (int)i + 1); checked++; if (done.load() && k == (size_t)N) break; } });        // ① 모든 스냅샷은 [1..k]
    for (int i = 1; i <= N; i++) list.push_back(i); done = true; for (auto& t : readers) t.join();
    assert(list.copied() == (long)N * (N - 1) / 2);                                                                                                                                                                                                       // ② 총 복사 = N(N−1)/2
    { CowList<int> l; for (int i = 0; i < 10; i++) l.push_back(i); auto snap = l.snapshot(); for (int i = 0; i < 1000; i++) l.push_back(100 + i); assert(snap->size() == 10 && (*snap)[9] == 9 && l.snapshot()->size() == 1010); }                                            // ③ 옛 스냅샷 불변
    { CowList<int> a, b; for (int i = 0; i < 1000; i++) a.push_back(i); b.modify([](std::vector<int>& v) { for (int i = 0; i < 1000; i++) v.push_back(i); }); assert(a.copied() == 1000L * 999 / 2 && b.copied() == 0 && *a.snapshot() == *b.snapshot()); }                    // 일괄 수정: 복사 0 번 (빈 벡터 한 번)
    { CowList<int> l; std::vector<std::thread> ts; for (int t = 0; t < 4; t++) ts.emplace_back([&, t] { for (int i = 0; i < 500; i++) l.pushBackOptimistic(t * 1000 + i); }); for (auto& t : ts) t.join(); auto snap = l.snapshot(); assert(snap->size() == 2000); std::vector<int> sorted(snap->begin(), snap->end()); std::sort(sorted.begin(), sorted.end()); for (int t = 0; t < 4; t++) for (int i = 0; i < 500; i++) assert(std::binary_search(sorted.begin(), sorted.end(), t * 1000 + i)); std::cout << "optimistic writers retried " << l.retries() << " times; "; }      // ④
    { LazyCowVec a; a.d->assign(8, 0); LazyCowVec b = a; b.set(0, 1); b.set(1, 2); b.set(2, 3); assert(LazyCowVec::copies == 1 && (*a.d)[0] == 0 && (*b.d)[2] == 3); a.set(0, 9); assert(LazyCowVec::copies == 1 && (*a.d)[0] == 9); }                                          // ⑤ 첫 쓰기만 복사, 이후는 제자리
    std::cout << "Copy-on-Write List: " << checked.load() << " reader snapshots were all exact prefixes [1..k]; " << N << " sequential writes copied " << list.copied() << " elements in total (N(N-1)/2)" << std::endl; return 0;
}
// Time Complexity: 읽기(스냅샷) O(1), 쓰기 O(N) (전체 복사), 일괄 수정 O(N) / 변경 묶음
// Space Complexity: O(N) × (동시에 살아 있는 스냅샷 수)
```
