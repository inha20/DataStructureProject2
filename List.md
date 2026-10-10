# Part 1. 리스트의 기초
## CreateList()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <functional>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <list>
#include <new>
#include <random>
#include <vector>

// 리스트 만들기: 리스트(list)는 순서가 있는 항목의 열이다. 만드는 방법은 크게 두 가지다. 배열 리스트는 연속된 메모리 한 덩어리를 할당해 항목을 순서대로 채우고, 연결 리스트는 노드를 하나씩 할당해 next 포인터로 잇는다. 어느 쪽이든 "빈 리스트", "n 개를 같은 값으로", "초기화 목록으로", "다른 범위로부터", "생성 함수로부터" 만드는 경우를 다룬다.
// 연결 리스트를 순서대로 만들 때는 꼬리 포인터(포인터의 포인터)를 유지해 O(1) 에 덧붙인다. 매번 처음부터 끝까지 걷고 덧붙이면 (n−1)(n−2)/2 걸음(≈ n²/2)이 든다. 맨 앞에 끼워 넣기만 하면 O(1) 이지만 순서가 뒤집힌다. 또 노드를 만드는 도중 할당이 실패(예외)하면 이미 만든 노드를 모두 지워 누수가 없어야 한다(예외 안전성).
// 검증: ① 배열 리스트의 다섯 가지 생성 방식이 std::vector 와 같은 내용 ② 연결 리스트의 순서대로/앞에 끼우기/덧붙이며 걷기 세 방식이 기대한 순서·걸음 수(0, 0, (n−1)(n−2)/2) ③ k 번째 노드 생성에서 예외를 던져도 모든 k 에서 살아 있는 노드가 0 개(누수 없음) ④ 빈 입력과 크기 0 경계.
struct Node { int val; Node* next; static int live, failAt;
    Node(int v, Node* n) : val(v), next(n) { if (failAt >= 0 && live >= failAt) throw std::bad_alloc(); ++live; } ~Node() { --live; } };
int Node::live = 0, Node::failAt = -1;
class IntArray {                                                                                                     // 배열 리스트: 연속 메모리 + 길이
    int* a_; std::size_t n_; explicit IntArray(std::size_t n) : a_(n ? new int[n] : nullptr), n_(n) {}
public:
    IntArray() : a_(nullptr), n_(0) {} ~IntArray() { delete[] a_; } IntArray(const IntArray&) = delete; IntArray& operator=(const IntArray&) = delete;
    IntArray(IntArray&& o) noexcept : a_(o.a_), n_(o.n_) { o.a_ = nullptr; o.n_ = 0; }
    static IntArray filled(std::size_t n, int v) { IntArray r(n); std::fill_n(r.a_, n, v); return r; }
    static IntArray of(std::initializer_list<int> il) { IntArray r(il.size()); std::copy(il.begin(), il.end(), r.a_); return r; }
    template <class It> static IntArray range(It f, It l) { IntArray r((std::size_t)std::distance(f, l)); std::copy(f, l, r.a_); return r; }
    static IntArray generate(std::size_t n, const std::function<int(std::size_t)>& g) { IntArray r(n); for (std::size_t i = 0; i < n; i++) r.a_[i] = g(i); return r; }
    std::size_t size() const { return n_; } std::vector<int> toVector() const { return std::vector<int>(a_, a_ + n_); }
};
void destroy(Node* h) { while (h) { Node* nx = h->next; delete h; h = nx; } }
Node* buildInOrder(const std::vector<int>& v) {                                                                      // 꼬리 포인터(포인터의 포인터): 매번 O(1) 덧붙임
    Node* head = nullptr; Node** tail = &head;
    try { for (int x : v) { *tail = new Node(x, nullptr); tail = &(*tail)->next; } } catch (...) { destroy(head); throw; }
    return head; }
Node* buildByPrepend(const std::vector<int>& v) {                                                                    // 앞에 끼우기: O(1) 이지만 순서가 뒤집힌다
    Node* head = nullptr; try { for (int x : v) head = new Node(x, head); } catch (...) { destroy(head); throw; } return head; }
Node* buildByWalking(const std::vector<int>& v, long& steps) {                                                       // 매번 끝까지 걸어서 덧붙임: O(n²)
    Node* head = nullptr; try { for (int x : v) { Node* n = new Node(x, nullptr); if (!head) head = n; else { Node* c = head; while (c->next) { c = c->next; steps++; } c->next = n; } } } catch (...) { destroy(head); throw; } return head; }
std::vector<int> toVector(const Node* h) { std::vector<int> r; for (; h; h = h->next) r.push_back(h->val); return r; }
int main() {
    std::mt19937 rng(1); std::vector<int> v(37); for (int& x : v) x = (int)(rng() % 1000);
    assert(IntArray().size() == 0 && IntArray::filled(0, 5).size() == 0 && IntArray::filled(4, 9).toVector() == (std::vector<int>{9, 9, 9, 9}));              // ① 배열 리스트의 생성 방식
    assert(IntArray::of({3, 1, 4, 1, 5}).toVector() == (std::vector<int>{3, 1, 4, 1, 5}) && IntArray::of({}).size() == 0);
    assert(IntArray::range(v.begin(), v.end()).toVector() == v); std::list<int> l(v.begin(), v.end()); assert(IntArray::range(l.begin(), l.end()).toVector() == v); int raw[5] = {5, 6, 7, 8, 9}; assert(IntArray::range(raw + 1, raw + 4).toVector() == (std::vector<int>{6, 7, 8}));
    assert(IntArray::generate(6, [](std::size_t i) { return (int)(i * i); }).toVector() == (std::vector<int>{0, 1, 4, 9, 16, 25}) && IntArray::range(v.begin(), v.begin()).size() == 0);
    { Node* a = buildInOrder(v); Node* b = buildByPrepend(v); std::vector<int> rev(v.rbegin(), v.rend()); assert(toVector(a) == v && toVector(b) == rev && Node::live == 2 * (int)v.size()); destroy(a); destroy(b); assert(Node::live == 0); }  // ② 세 방식
    { std::vector<int> big(1000, 7); long steps = 0; Node* a = buildByWalking(big, steps); assert(steps == 999L * 998 / 2 && toVector(a) == big); destroy(a); assert(Node::live == 0); }
    for (int k = 0; k < (int)v.size(); k++) { Node::failAt = k; bool threw = false;                                                                // ③ k 번째 할당에서 예외 → 누수 없음
        try { destroy(buildInOrder(v)); } catch (const std::bad_alloc&) { threw = true; } assert(threw && Node::live == 0);
        threw = false; try { destroy(buildByPrepend(v)); } catch (const std::bad_alloc&) { threw = true; } assert(threw && Node::live == 0); }
    Node::failAt = -1; assert(buildInOrder({}) == nullptr && buildByPrepend({}) == nullptr && Node::live == 0);                                       // ④ 빈 입력
    { long steps = 0; assert(buildByWalking({}, steps) == nullptr && steps == 0); Node* one = buildByWalking({42}, steps); assert(one->next == nullptr && one->val == 42 && steps == 0); destroy(one); }
    std::cout << "CreateList: five array-list constructions matched std::vector; linked lists built in order (tail pointer: 0 extra steps), reversed by prepending, and by walking ((n-1)(n-2)/2 = 498501 steps for n=1000); allocation failure at each of " << v.size() << " positions leaked no nodes" << std::endl; return 0;
}
// Time Complexity: 배열 생성 O(N), 연결 리스트 꼬리 포인터 O(N) (끝까지 걷기는 O(N²))
// Space Complexity: O(N)
```
## Traverse()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <list>
#include <numeric>
#include <random>
#include <vector>

// 순회(Traverse): 리스트의 모든 항목을 한 번씩 정해진 순서로 방문한다. 배열은 인덱스나 포인터로, 연결 리스트는 head 에서 next 를 따라간다. 단방향 연결 리스트는 뒤로 갈 수 없으므로 역순 순회는 재귀(호출 스택에 쌓기)나 명시적 스택이 필요하다 — 재귀는 노드 수만큼 스택 깊이를 쓰므로 긴 리스트에서는 명시적 스택을 써야 한다.
// 순회 중 일찍 멈추기(조건을 만족하면 중단)와 방문 횟수 세기도 같은 골격이다. 순환이 있는 리스트를 순회하면 끝나지 않으므로 상한이나 플로이드(토끼와 거북이) 판정으로 보호한다.
// 검증: ① 전방 순회(반복·재귀)와 후방 순회(재귀·명시적 스택)가 std::vector 와 같은 순서, 방문 횟수 == 길이 ② 조건부 조기 종료가 정확히 첫 일치까지만 방문 ③ 1,000,000 노드 리스트를 명시적 스택으로 역순 순회(재귀였다면 스택 오버플로) ④ 순환 리스트에서 상한 있는 순회는 정확히 상한만큼만 방문하고 플로이드 판정이 순환 여부를 맞힌다 ⑤ 빈 리스트·노드 1개 경계에서 네 가지 순회(반복 전방·재귀 전방·재귀 후방·스택 후방)가 모두 벡터와 같고 방문 횟수가 길이와 같음.
struct Node { int val; Node* next; Node(int v, Node* n) : val(v), next(n) {} };
Node* build(const std::vector<int>& v) { Node* head = nullptr; Node** t = &head; for (int x : v) { *t = new Node(x, nullptr); t = &(*t)->next; } return head; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
template <class F> long forEach(const Node* h, F f) { long visited = 0; for (; h; h = h->next) { f(h->val); visited++; } return visited; }                    // 반복 전방
void forwardRec(const Node* h, std::vector<int>& out) { if (!h) return; out.push_back(h->val); forwardRec(h->next, out); }                                       // 재귀 전방
void backwardRec(const Node* h, std::vector<int>& out) { if (!h) return; backwardRec(h->next, out); out.push_back(h->val); }                                    // 재귀 후방: 돌아오는 길에 방문
void backwardStack(const Node* h, std::vector<int>& out) { std::vector<const Node*> st; for (; h; h = h->next) st.push_back(h); while (!st.empty()) { out.push_back(st.back()->val); st.pop_back(); } }   // 명시적 스택 후방
long forEachWhile(const Node* h, const std::function<bool(int)>& keepGoing) { long visited = 0; for (; h; h = h->next) { visited++; if (!keepGoing(h->val)) break; } return visited; }   // 조기 종료
long boundedWalk(const Node* h, long limit) { long visited = 0; for (; h && visited < limit; h = h->next) visited++; return visited; }
bool hasCycle(const Node* h) { const Node *slow = h, *fast = h; while (fast && fast->next) { slow = slow->next; fast = fast->next->next; if (slow == fast) return true; } return false; }
int main() {
    std::mt19937 rng(2); std::vector<int> v(500); for (int& x : v) x = (int)(rng() % 100); Node* head = build(v);
    { std::vector<int> a, f; long n = forEach(head, [&](int x) { a.push_back(x); }); assert(n == (long)v.size() && a == v); forwardRec(head, f); assert(f == v);   // ① 전방
      std::vector<int> rev(v.rbegin(), v.rend()), b1, b2; backwardRec(head, b1); backwardStack(head, b2); assert(b1 == rev && b2 == rev);
      long sum = 0; forEach(head, [&](int x) { sum += x; }); assert(sum == std::accumulate(v.begin(), v.end(), 0L)); }
    { int target = v[200]; long first = std::find(v.begin(), v.end(), target) - v.begin(); long visited = forEachWhile(head, [&](int x) { return x != target; }); assert(visited == first + 1);   // ② 조기 종료
      assert(forEachWhile(head, [](int) { return true; }) == (long)v.size() && forEachWhile(nullptr, [](int) { return false; }) == 0 && forEachWhile(head, [](int) { return false; }) == 1); }
    destroy(head);
    { std::vector<int> big(1000000); std::iota(big.begin(), big.end(), 0); Node* h = build(big); std::vector<int> out; out.reserve(big.size()); backwardStack(h, out);   // ③ 100 만 노드 역순 순회
      assert(out.size() == big.size() && out.front() == 999999 && out.back() == 0 && std::is_sorted(out.rbegin(), out.rend())); destroy(h); }
    { Node* h = build({1, 2, 3, 4, 5}); assert(!hasCycle(h)); Node* last = h; while (last->next) last = last->next; last->next = h->next->next;                           // ④ 순환: 5 -> 3
      assert(hasCycle(h) && boundedWalk(h, 100) == 100 && boundedWalk(h, 3) == 3); last->next = nullptr; assert(!hasCycle(h) && boundedWalk(h, 100) == 5); destroy(h); }
    { assert(!hasCycle(nullptr) && boundedWalk(nullptr, 5) == 0);   // ⑤ 빈 리스트와 노드 1개: 모든 순회를 nullptr·단일 노드에서 실행
      for (const std::vector<int>& w : {std::vector<int>{}, std::vector<int>{7}}) { Node* h = build(w); std::vector<int> r(w.rbegin(), w.rend()), a, f, b1, b2; long n = forEach(h, [&](int x) { a.push_back(x); }); forwardRec(h, f); backwardRec(h, b1); backwardStack(h, b2);
        assert(n == (long)w.size() && a == w && f == w && b1 == r && b2 == r && !hasCycle(h) && boundedWalk(h, 5) == (long)w.size() && forEachWhile(h, [](int) { return true; }) == (long)w.size()); destroy(h); }
      Node* one = build({7}); one->next = one; assert(hasCycle(one) && boundedWalk(one, 5) == 5); one->next = nullptr; destroy(one); }
    std::cout << "Traverse: forward (iterative and recursive) and backward (recursive and explicit stack) traversals matched std::vector order, early exit stopped at the first match, a 1,000,000-node list was walked backwards with an explicit stack, and cycles were detected without looping" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: 전방 O(1), 재귀·스택 후방 O(N)
```
## Search()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 탐색(Search): 리스트에서 값이 있는 위치를 찾는다. 정렬되지 않은 리스트에서는 처음부터 하나씩 비교하는 선형 탐색뿐이다. 찾으면 비교 횟수는 (위치+1), 못 찾으면 n 번 — 서로 다른 값 n 개에서 모든 값을 한 번씩 찾으면 총 비교는 n(n+1)/2 이므로 평균 (n+1)/2 이다.
// 보초(sentinel): 루프에서 "끝까지 갔는가"와 "같은가" 두 비교를 매번 하는 대신, 마지막에 찾는 값을 심어 두면 "같은가" 한 번만 비교해도 된다(범위 검사 제거). 끝에 도달했는지는 찾은 위치가 원래 끝인지로 판단한다. 자기 조직 리스트: 접근 빈도가 치우친 환경에서는 찾은 항목을 맨 앞으로 옮기면(move-to-front) 자주 찾는 항목이 앞쪽에 모여 평균 비교 횟수가 줄어든다.
// 검증: ① 첫/마지막/모든 위치 찾기가 std::find 계열과 같음 ② 서로 다른 값 n 개에서 모든 값을 찾을 때 비교 총합 == n(n+1)/2, 실패 탐색은 n 번 ③ 보초 탐색이 선형 탐색과 같은 결과를 내고(원소 대 키 비교 수 = 위치+1, 실패 시 n, 루프당 범위 검사 없음) 심었던 값이 원래대로 복원됨 ④ 치우친 접근(지프 분포)에서 move-to-front 가 총 비교 수를 줄인다.
struct Counted { long cmp = 0; };
long linearFirst(const std::vector<int>& a, int key, Counted& c) { for (std::size_t i = 0; i < a.size(); i++) { c.cmp++; if (a[i] == key) return (long)i; } return -1; }
long linearLast(const std::vector<int>& a, int key, Counted& c) { for (long i = (long)a.size() - 1; i >= 0; i--) { c.cmp++; if (a[i] == key) return i; } return -1; }
std::vector<long> linearAll(const std::vector<int>& a, int key) { std::vector<long> r; for (std::size_t i = 0; i < a.size(); i++) if (a[i] == key) r.push_back((long)i); return r; }
long sentinelSearch(std::vector<int>& a, int key, long& elementCompares) {                                           // 보초: 마지막 칸에 key 를 심고 "같은가" 만 비교
    if (a.empty()) return -1; int last = a.back(); a.back() = key; std::size_t i = 0; while (true) { elementCompares++; if (a[i] == key) break; i++; }
    a.back() = last; return (i < a.size() - 1 || last == key) ? (long)i : -1; }
long mtfSearch(std::vector<int>& a, int key, Counted& c) {                                                           // 찾으면 맨 앞으로(리스트 앞쪽 이동은 선형 시간이 들지만 비교 수만 센다)
    for (std::size_t i = 0; i < a.size(); i++) { c.cmp++; if (a[i] == key) { std::rotate(a.begin(), a.begin() + i, a.begin() + i + 1); return (long)i; } } return -1; }
int main() {
    std::mt19937 rng(3); { std::vector<int> a(300); for (int& x : a) x = (int)(rng() % 20); for (int key = -1; key <= 21; key++) { Counted c; long f = linearFirst(a, key, c), l = linearLast(a, key, c);   // ①
        auto it = std::find(a.begin(), a.end(), key); auto rit = std::find(a.rbegin(), a.rend(), key); assert(f == (it == a.end() ? -1 : it - a.begin()) && l == (rit == a.rend() ? -1 : (long)a.size() - 1 - (rit - a.rbegin())));
        std::vector<long> all = linearAll(a, key); assert((long)all.size() == std::count(a.begin(), a.end(), key) && (all.empty() || (all.front() == f && all.back() == l))); } }
    { const int n = 200; std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); std::shuffle(a.begin(), a.end(), rng); long total = 0; for (int key = 0; key < n; key++) { Counted c; long pos = linearFirst(a, key, c); assert(c.cmp == pos + 1); total += c.cmp; }   // ②
      assert(total == (long)n * (n + 1) / 2); Counted miss; assert(linearFirst(a, -5, miss) == -1 && miss.cmp == n); }
    { std::vector<int> a(100); for (int& x : a) x = (int)(rng() % 150); for (int key = -1; key < 151; key++) { std::vector<int> copy = a; long ec = 0; long s = sentinelSearch(copy, key, ec); Counted c; long ref = linearFirst(a, key, c);   // ③ 보초
        assert(s == ref && copy == a); assert(ec == (ref >= 0 ? ref + 1 : (long)a.size())); } std::vector<int> e; long ec = 0; assert(sentinelSearch(e, 1, ec) == -1);
      std::vector<int> t = {5}; ec = 0; assert(sentinelSearch(t, 5, ec) == 0 && sentinelSearch(t, 6, ec) == -1 && t == std::vector<int>{5}); }
    {   const int n = 100; std::vector<int> plain(n); std::iota(plain.begin(), plain.end(), 0); std::shuffle(plain.begin(), plain.end(), rng); std::vector<int> mtf = plain; std::vector<double> w(n); for (int i = 0; i < n; i++) w[i] = 1.0 / (i + 1);   // ④ 지프 분포 접근
        std::discrete_distribution<int> dist(w.begin(), w.end()); std::vector<int> queries(20000); for (int& q : queries) q = dist(rng);
        Counted cp, cm; for (int q : queries) { assert(linearFirst(plain, q, cp) >= 0); assert(mtfSearch(mtf, q, cm) >= 0); } std::vector<int> sorted = mtf; std::sort(sorted.begin(), sorted.end()); assert(sorted == [&] { std::vector<int> s(n); std::iota(s.begin(), s.end(), 0); return s; }());
        assert(cm.cmp < cp.cmp * 7 / 10); std::cout << "Search: first/last/all positions matched the standard algorithms, successful searches over n distinct keys cost exactly n(n+1)/2 comparisons, the sentinel search agreed with linear search, and move-to-front cut comparisons from " << cp.cmp << " to " << cm.cmp << " under a Zipf-like access pattern" << std::endl; }
    return 0;
}
// Time Complexity: O(N) (평균 (N+1)/2 번 비교)
// Space Complexity: O(1)
```
## Insert()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <list>
#include <random>
#include <stdexcept>
#include <vector>

// 삽입(Insert): 위치 pos 에 새 항목을 끼워 넣는다. 배열 리스트는 pos 이후의 항목을 한 칸씩 뒤로 밀어야 하므로 n−pos 번 이동하고(맨 뒤는 0 번, 맨 앞은 n 번), 연결 리스트는 pos−1 번째 노드까지 걸어간 뒤 포인터 두 개만 바꾼다(걷기 O(pos), 연결은 O(1)). 이동은 반드시 뒤에서부터 해야 덮어쓰지 않는다.
// 정렬된 리스트에 정렬을 유지하며 넣을 때는 같은 값들의 뒤에 넣어야 안정적(먼저 들어온 것이 앞)이다. pos 가 [0, n] 밖이면 오류다 — pos == n 은 맨 뒤 덧붙임으로 유효하다.
// 검증: ① 배열 삽입이 std::vector::insert 와 같은 결과이고 이동 횟수가 정확히 n−pos ② 연결 리스트 삽입이 같은 결과이고 걸은 횟수가 정확히 pos, 머리·꼬리·빈 리스트 경계 ③ 범위 밖 위치는 예외이고 리스트는 변하지 않음 ④ 정렬 유지 삽입이 안정적(같은 키는 도착 순서)이고 결과가 std::upper_bound 삽입과 같음 ⑤ 연결 리스트 노드 누수 없음.
struct ArrayList { int a[256]; int n = 0; long moves = 0;
    void insert(int pos, int v) { if (pos < 0 || pos > n || n == 256) throw std::out_of_range("insert"); for (int i = n; i > pos; i--) { a[i] = a[i - 1]; moves++; } a[pos] = v; n++; }   // 뒤에서부터 밀기
    std::vector<int> items() const { return std::vector<int>(a, a + n); } };
struct Node { int val; Node* next; static int live; Node(int v, Node* nx) : val(v), next(nx) { ++live; } ~Node() { --live; } }; int Node::live = 0;
struct LinkedList { Node* head = nullptr; int n = 0; long steps = 0;
    ~LinkedList() { while (head) { Node* nx = head->next; delete head; head = nx; } }
    void insert(int pos, int v) { if (pos < 0 || pos > n) throw std::out_of_range("insert"); Node** link = &head; for (int i = 0; i < pos; i++) { link = &(*link)->next; steps++; } *link = new Node(v, *link); n++; }   // 포인터의 포인터: 머리도 같은 코드
    std::vector<int> items() const { std::vector<int> r; for (Node* c = head; c; c = c->next) r.push_back(c->val); return r; } };
struct Item { int key, order; };
void insertSortedStable(std::vector<Item>& v, Item x) { std::size_t i = v.size(); while (i > 0 && v[i - 1].key > x.key) i--; v.insert(v.begin() + i, x); }      // 같은 키들의 뒤에
int main() {
    std::mt19937 rng(4);
    { ArrayList a; std::vector<int> ref; for (int step = 0; step < 200; step++) { int pos = (int)(rng() % (ref.size() + 1)), v = (int)(rng() % 1000); long before = a.moves; a.insert(pos, v); ref.insert(ref.begin() + pos, v);        // ①
        assert(a.items() == ref && a.moves - before == (long)ref.size() - 1 - pos); } }
    { LinkedList l; std::vector<int> ref; for (int step = 0; step < 300; step++) { int pos = (int)(rng() % (ref.size() + 1)), v = (int)(rng() % 1000); long before = l.steps; l.insert(pos, v); ref.insert(ref.begin() + pos, v);        // ②
        assert(l.items() == ref && l.steps - before == pos && l.n == (int)ref.size()); } assert(Node::live == 300); }
    assert(Node::live == 0);
    { LinkedList l; l.insert(0, 5); l.insert(0, 3); l.insert(2, 9); l.insert(1, 4); assert(l.items() == (std::vector<int>{3, 4, 5, 9}) && l.head->val == 3); }                     // 빈 리스트·머리·꼬리·중간
    { LinkedList l; for (int v : {1, 2, 3}) l.insert(l.n, v); bool threw = false; for (int bad : {-1, 4, 100}) { try { l.insert(bad, 0); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; }   // ③
      assert(l.items() == (std::vector<int>{1, 2, 3}) && l.n == 3); ArrayList a; a.insert(0, 1); try { a.insert(2, 0); } catch (const std::out_of_range&) { threw = true; } assert(threw && a.items() == std::vector<int>{1}); }
    { std::vector<Item> v, ref; for (int i = 0; i < 400; i++) { Item x{(int)(rng() % 10), i}; insertSortedStable(v, x); auto it = std::upper_bound(ref.begin(), ref.end(), x, [](const Item& p, const Item& q) { return p.key < q.key; }); ref.insert(it, x); }   // ④ 안정적 정렬 삽입
      for (std::size_t i = 0; i < v.size(); i++) assert(v[i].key == ref[i].key && v[i].order == ref[i].order); for (std::size_t i = 1; i < v.size(); i++) assert(v[i - 1].key < v[i].key || (v[i - 1].key == v[i].key && v[i - 1].order < v[i].order)); }
    assert(Node::live == 0); std::cout << "Insert: array insertion shifted exactly n-pos elements, linked insertion walked exactly pos nodes (head, tail and empty cases through one pointer-to-pointer code path), invalid positions threw without modifying the list, and sorted insertion was stable" << std::endl; return 0;
}
// Time Complexity: 배열 O(N) (이동), 연결 리스트 O(pos) (걷기) + O(1) (연결)
// Space Complexity: O(1)
```
## Delete()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

// 삭제(Delete): 위치로 지우기와 값으로 지우기가 있다. 배열 리스트는 지운 칸 뒤의 항목을 한 칸씩 앞으로 당기므로 n−pos−1 번 이동하고, 연결 리스트는 앞 노드의 next 를 건너뛰게 바꾸고 노드를 해제한다(걷기 O(pos)). 포인터의 포인터를 쓰면 머리 노드를 지우는 경우에도 별도 분기가 없다.
// 값이 일치하는 항목을 모두 지울 때 항목마다 한 칸씩 당기면 O(n²) 이지만, 읽기 포인터와 쓰기 포인터를 두고 지워지지 않을 항목만 앞으로 복사하면 단 한 번의 순회(비교 n 번, 이동 ≤ n 번)로 끝난다(안정적: 남은 항목의 순서 유지). 연결 리스트에서는 걷다가 일치하는 노드를 바로 해제한다.
// 검증: ① 위치 삭제가 std::vector::erase 와 같고 이동 횟수가 정확히 n−pos−1 ② 연결 리스트 위치 삭제(머리·꼬리·중간·1 노드)와 노드 해제(누수·이중 해제 없음) ③ 값 삭제(첫 번째)와 전부 삭제가 std::erase-remove 와 같고 한 번의 순회(비교 n 번)이며 이동 횟수가 독립 계산(첫 삭제 항목 뒤에 남는 항목 수)과 정확히 같고 남은 항목의 순서 유지 ④ 범위 밖 위치 예외 ⑤ 없는 값 삭제는 false 이고 리스트 불변.
struct ArrayList { std::vector<int> a; long moves = 0, compares = 0;
    void eraseAt(int pos) { if (pos < 0 || pos >= (int)a.size()) throw std::out_of_range("erase"); for (std::size_t i = pos; i + 1 < a.size(); i++) { a[i] = a[i + 1]; moves++; } a.pop_back(); }
    int removeAll(int key) { std::size_t w = 0; for (std::size_t r = 0; r < a.size(); r++) { compares++; if (a[r] != key) { if (w != r) moves++; a[w++] = a[r]; } } int removed = (int)(a.size() - w); a.resize(w); return removed; } };   // 읽기/쓰기 포인터
struct Node { int val; Node* next; static int live; Node(int v, Node* nx) : val(v), next(nx) { ++live; } ~Node() { --live; } }; int Node::live = 0;
struct LinkedList { Node* head = nullptr; int n = 0; long steps = 0;
    ~LinkedList() { while (head) { Node* nx = head->next; delete head; head = nx; } }
    void pushBack(int v) { Node** l = &head; while (*l) l = &(*l)->next; *l = new Node(v, nullptr); n++; }
    void eraseAt(int pos) { if (pos < 0 || pos >= n) throw std::out_of_range("erase"); Node** l = &head; for (int i = 0; i < pos; i++) { l = &(*l)->next; steps++; } Node* dead = *l; *l = dead->next; delete dead; n--; }
    bool removeFirst(int key) { for (Node** l = &head; *l; l = &(*l)->next) if ((*l)->val == key) { Node* dead = *l; *l = dead->next; delete dead; n--; return true; } return false; }
    int removeAll(int key) { int removed = 0; Node** l = &head; while (*l) { if ((*l)->val == key) { Node* dead = *l; *l = dead->next; delete dead; n--; removed++; } else l = &(*l)->next; } return removed; }
    std::vector<int> items() const { std::vector<int> r; for (Node* c = head; c; c = c->next) r.push_back(c->val); return r; } };
int main() {
    std::mt19937 rng(5);
    { ArrayList a; for (int i = 0; i < 100; i++) a.a.push_back((int)(rng() % 50)); std::vector<int> ref = a.a; while (!ref.empty()) { int pos = (int)(rng() % ref.size()); long before = a.moves; a.eraseAt(pos); ref.erase(ref.begin() + pos); assert(a.a == ref && a.moves - before == (long)ref.size() - pos); } }   // ①
    { LinkedList l; std::vector<int> ref; for (int i = 0; i < 120; i++) { int v = (int)(rng() % 50); l.pushBack(v); ref.push_back(v); } assert(Node::live == 120);                                       // ②
      while (!ref.empty()) { int pos = (int)(rng() % ref.size()); long before = l.steps; l.eraseAt(pos); ref.erase(ref.begin() + pos); assert(l.items() == ref && l.steps - before == pos && Node::live == (int)ref.size() && l.n == (int)ref.size()); } assert(l.head == nullptr); }
    { LinkedList l; l.pushBack(7); l.eraseAt(0); assert(l.head == nullptr && l.n == 0 && Node::live == 0); for (int v : {1, 2, 3}) l.pushBack(v); l.eraseAt(2); l.eraseAt(0); assert(l.items() == std::vector<int>{2}); }
    for (int rep = 0; rep < 200; rep++) { std::vector<int> v((std::size_t)(rng() % 60)); for (int& x : v) x = (int)(rng() % 6); int key = (int)(rng() % 7);                                 // ③ 값 삭제
        ArrayList a; a.a = v; int removed = a.removeAll(key); std::vector<int> ref = v; ref.erase(std::remove(ref.begin(), ref.end(), key), ref.end()); assert(a.a == ref && removed == (int)(v.size() - ref.size()) && a.compares == (long)v.size());
        std::size_t firstHit = (std::size_t)(std::find(v.begin(), v.end(), key) - v.begin()); long behind = 0; for (std::size_t i = firstHit + 1; i < v.size(); i++) if (v[i] != key) behind++; assert(a.moves == behind);   // 이동 = 첫 삭제 항목 뒤에 남는 항목 수(앞쪽 항목은 제자리)
        LinkedList l; for (int x : v) l.pushBack(x); assert(l.removeAll(key) == removed && l.items() == ref && l.n == (int)ref.size() && Node::live == (int)ref.size());
        LinkedList f; for (int x : v) f.pushBack(x); bool had = std::find(v.begin(), v.end(), key) != v.end(); std::vector<int> r1 = v; if (had) r1.erase(std::find(r1.begin(), r1.end(), key)); assert(f.removeFirst(key) == had && f.items() == r1); }   // ⑤
    assert(Node::live == 0); { LinkedList l; for (int v : {1, 2, 3}) l.pushBack(v); bool threw = false; for (int bad : {-1, 3, 10}) { try { l.eraseAt(bad); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; } assert(l.items() == (std::vector<int>{1, 2, 3}) && !l.removeFirst(9) && l.removeAll(9) == 0); }   // ④
    { ArrayList a; a.a = {1, 1, 1, 1}; assert(a.removeAll(1) == 4 && a.a.empty() && a.moves == 0); }
    std::cout << "Delete: positional erase moved exactly n-pos-1 elements, linked erase freed exactly one node per deletion with no leaks, and delete-all used a single pass (n comparisons, exactly one move per kept item behind the first removed one) producing the same stable result as erase-remove" << std::endl; return 0;
}
// Time Complexity: 위치 삭제 배열 O(N)·연결 리스트 O(pos), 값 전부 삭제 O(N)
// Space Complexity: O(1)
```
## Update()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

// 갱신(Update): 구조(길이·노드·메모리 위치)는 그대로 두고 항목의 값만 바꾼다. 위치로 바꾸기(배열 O(1), 연결 리스트 O(pos)), 값으로 찾아 바꾸기, 조건에 맞는 항목 모두 바꾸기, 모든 항목에 함수 적용(제자리 변환)이 있다. 삽입·삭제와 달리 이동이나 노드 할당이 없고 반복자·포인터도 무효가 되지 않는다.
// 주의: 정렬된 리스트에서 값을 바꾸면 정렬이 깨질 수 있다(갱신 뒤 다시 위치를 잡아야 함). 이 코드의 갱신은 정렬 불변식을 지키지 않으며 호출자가 책임진다.
// 검증: ① 위치 갱신이 모델(std::vector) 과 같고 갱신 후에도 각 항목의 주소가 변하지 않음 ② 연결 리스트 노드 주소 순서가 갱신 전후 동일 ③ 값/조건/함수 일괄 갱신이 std::replace, std::replace_if, std::transform 과 같고 갱신된 개수가 정확 ④ 범위 밖 위치 예외, 빈 리스트 경계 ⑤ 갱신이 길이·메모리·노드 수를 바꾸지 않음.
struct Node { int val; Node* next; static int live; Node(int v, Node* nx) : val(v), next(nx) { ++live; } ~Node() { --live; } }; int Node::live = 0;
struct LinkedList { Node* head = nullptr; int n = 0;
    ~LinkedList() { while (head) { Node* nx = head->next; delete head; head = nx; } }
    void pushBack(int v) { Node** l = &head; while (*l) l = &(*l)->next; *l = new Node(v, nullptr); n++; }
    void set(int pos, int v) { if (pos < 0 || pos >= n) throw std::out_of_range("set"); Node* c = head; for (int i = 0; i < pos; i++) c = c->next; c->val = v; }
    int replaceValue(int from, int to) { int cnt = 0; for (Node* c = head; c; c = c->next) if (c->val == from) { c->val = to; cnt++; } return cnt; }
    int replaceIf(const std::function<bool(int)>& pred, int to) { int cnt = 0; for (Node* c = head; c; c = c->next) if (pred(c->val)) { c->val = to; cnt++; } return cnt; }
    void transform(const std::function<int(int)>& f) { for (Node* c = head; c; c = c->next) c->val = f(c->val); }
    std::vector<int> items() const { std::vector<int> r; for (Node* c = head; c; c = c->next) r.push_back(c->val); return r; }
    std::vector<const Node*> addresses() const { std::vector<const Node*> r; for (Node* c = head; c; c = c->next) r.push_back(c); return r; } };
struct ArrayList { std::vector<int> a;
    void set(int pos, int v) { if (pos < 0 || pos >= (int)a.size()) throw std::out_of_range("set"); a[pos] = v; } };
int main() {
    std::mt19937 rng(6);
    { ArrayList al; for (int i = 0; i < 80; i++) al.a.push_back((int)(rng() % 100)); std::vector<int> ref = al.a; const int* base = al.a.data(); std::size_t cap = al.a.capacity();     // ①
      for (int step = 0; step < 500; step++) { int pos = (int)(rng() % ref.size()), v = (int)(rng() % 1000); al.set(pos, v); ref[pos] = v; assert(al.a == ref && al.a.data() == base && al.a.capacity() == cap && &al.a[pos] == base + pos); } }
    { LinkedList l; std::vector<int> ref; for (int i = 0; i < 90; i++) { int v = (int)(rng() % 100); l.pushBack(v); ref.push_back(v); } std::vector<const Node*> addr = l.addresses(); int liveBefore = Node::live;   // ②
      for (int step = 0; step < 300; step++) { int pos = (int)(rng() % ref.size()), v = (int)(rng() % 1000); l.set(pos, v); ref[pos] = v; assert(l.items() == ref && l.addresses() == addr && Node::live == liveBefore); }
      int c1 = l.replaceValue(ref[3], -1); int want1 = (int)std::count(ref.begin(), ref.end(), ref[3]); std::replace(ref.begin(), ref.end(), ref[3], -1); assert(c1 == want1 && l.items() == ref);     // ③
      int c2 = l.replaceIf([](int x) { return x % 2 != 0; }, 0); int want2 = (int)std::count_if(ref.begin(), ref.end(), [](int x) { return x % 2 != 0; }); std::replace_if(ref.begin(), ref.end(), [](int x) { return x % 2 != 0; }, 0); assert(c2 == want2 && l.items() == ref);
      l.transform([](int x) { return x * 3 + 1; }); std::transform(ref.begin(), ref.end(), ref.begin(), [](int x) { return x * 3 + 1; }); assert(l.items() == ref && l.addresses() == addr && l.n == 90 && Node::live == liveBefore); }   // ⑤
    { LinkedList e; bool threw = false; try { e.set(0, 1); } catch (const std::out_of_range&) { threw = true; } assert(threw && e.replaceValue(1, 2) == 0 && e.items().empty()); e.transform([](int x) { return x; }); ArrayList a; threw = false; try { a.set(0, 1); } catch (const std::out_of_range&) { threw = true; } assert(threw);   // ④
      LinkedList l; l.pushBack(1); threw = false; for (int bad : {-1, 1}) { try { l.set(bad, 0); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; } assert(l.items() == std::vector<int>{1}); }
    assert(Node::live == 0); std::cout << "Update: 500 in-place array updates and 300 linked updates matched the model without moving any element or node, bulk replace/replace_if/transform matched the standard algorithms, and invalid positions threw" << std::endl; return 0;
}
// Time Complexity: 배열 O(1), 연결 리스트 O(pos), 일괄 갱신 O(N)
// Space Complexity: O(1)
```
## Reverse()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 뒤집기(Reverse): 배열은 양 끝에서 좁혀 오며 서로 교환한다(교환 ⌊n/2⌋ 번, 추가 공간 O(1)). 단방향 연결 리스트는 값을 옮기지 않고 포인터 방향만 반대로 돌린다: prev, cur, next 세 포인터로 한 노드씩 `cur->next = prev` 로 돌리며 전진하면 O(n) 시간, O(1) 공간이다. 재귀 버전은 같은 일을 호출 스택으로 하므로 O(n) 공간이다.
// 응용: 구간 [l, r] 만 뒤집기(앞뒤 연결을 다시 이어야 함), k 개씩 묶어 뒤집기. 어떤 것이든 노드 자체를 옮기므로 노드 주소는 보존되고 head 가 바뀐다 — 값을 복사해 뒤집는 구현과 구별된다. 두 번 뒤집으면 원래대로다.
// 검증: ① 배열 뒤집기가 std::reverse 와 같고 교환 횟수 == ⌊n/2⌋ ② 연결 리스트 반복·재귀 뒤집기가 같은 결과이고 노드 집합·주소가 보존(값 복사 아님)되며 두 번 뒤집으면 원래 ③ 구간 뒤집기·k 묶음 뒤집기가 std::reverse 로 만든 기대 결과와 같음(모든 l, r, k) ④ 길이 0·1·2 경계 ⑤ 노드 누수 없음.
struct Node { int val; Node* next; static int live; Node(int v, Node* nx) : val(v), next(nx) { ++live; } ~Node() { --live; } }; int Node::live = 0;
Node* build(const std::vector<int>& v) { Node* head = nullptr; Node** t = &head; for (int x : v) { *t = new Node(x, nullptr); t = &(*t)->next; } return head; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
std::vector<int> items(const Node* h) { std::vector<int> r; for (; h; h = h->next) r.push_back(h->val); return r; }
std::vector<const Node*> addrs(const Node* h) { std::vector<const Node*> r; for (; h; h = h->next) r.push_back(h); return r; }
long reverseArray(std::vector<int>& a) { long swaps = 0; if (a.size() < 2) return 0; for (std::size_t i = 0, j = a.size() - 1; i < j; i++, j--) { std::swap(a[i], a[j]); swaps++; } return swaps; }
Node* reverseIter(Node* head) { Node *prev = nullptr, *cur = head; while (cur) { Node* next = cur->next; cur->next = prev; prev = cur; cur = next; } return prev; }
Node* reverseRec(Node* head) { if (!head || !head->next) return head; Node* newHead = reverseRec(head->next); head->next->next = head; head->next = nullptr; return newHead; }
Node* reverseBetween(Node* head, int l, int r) {                                                                     // 1 기반 구간 [l, r]
    Node dummy(0, head); Node* before = &dummy; for (int i = 1; i < l; i++) before = before->next; Node *cur = before->next, *prev = nullptr; Node* first = cur;
    for (int i = l; i <= r; i++) { Node* nx = cur->next; cur->next = prev; prev = cur; cur = nx; } before->next = prev; first->next = cur; Node* res = dummy.next; dummy.next = nullptr; return res; }
Node* reverseKGroup(Node* head, int k) {                                                                             // k 개씩 묶어 뒤집기, 남은 꼬리(< k)는 그대로
    int len = 0; for (Node* c = head; c; c = c->next) len++; Node dummy(0, head); Node* tail = &dummy;
    for (int g = 0; g + k <= len; g += k) { Node *first = tail->next, *prev = nullptr, *cur = first; for (int i = 0; i < k; i++) { Node* nx = cur->next; cur->next = prev; prev = cur; cur = nx; } tail->next = prev; first->next = cur; tail = first; }
    Node* res = dummy.next; dummy.next = nullptr; return res; }
std::string reverseTrace(const std::vector<int>& v) {                  // 그림: 뒤집은 부분(prev) | 아직 안 본 부분(cur) — 화살표를 하나씩 되돌리며 정점이 prev 쪽으로 넘어간다
    Node* cur = build(v); Node* prev = nullptr; std::string s; int step = 0;
    auto line = [&]() {
        s += "step " + std::to_string(step++) + ": [";
        for (const Node* p = prev; p; p = p->next) s += (p == prev ? "" : " ") + std::to_string(p->val);
        s += "] | [";
        for (const Node* p = cur; p; p = p->next) s += (p == cur ? "" : " ") + std::to_string(p->val);
        s += "]\n";
    };
    line();
    while (cur) { Node* next = cur->next; cur->next = prev; prev = cur; cur = next; line(); }
    destroy(prev); return s;
}
int main() {
    {   const std::string pic = "step 0: [] | [1 2 3 4]\nstep 1: [1] | [2 3 4]\nstep 2: [2 1] | [3 4]\nstep 3: [3 2 1] | [4]\nstep 4: [4 3 2 1] | []\n";
        assert(reverseTrace({1, 2, 3, 4}) == pic && Node::live == 0); std::cout << pic; }              // 매 단계 prev 는 이미 뒤집힌 접두사, cur 는 남은 접미사: 노드는 하나도 새로 만들지 않는다
    std::mt19937 rng(7);
    for (int n = 0; n <= 40; n++) { std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 100); std::vector<int> ref = a; std::reverse(ref.begin(), ref.end()); long sw = reverseArray(a); assert(a == ref && sw == n / 2); }   // ①
    for (int n = 0; n <= 30; n++) { std::vector<int> v(n); std::iota(v.begin(), v.end(), 1); std::vector<int> rv(v.rbegin(), v.rend());                                                // ②
        Node* h = build(v); std::vector<const Node*> ad = addrs(h); Node* r1 = reverseIter(h); assert(items(r1) == rv); std::vector<const Node*> ad2 = addrs(r1); std::reverse(ad2.begin(), ad2.end()); assert(ad2 == ad);   // 같은 노드, 거꾸로 이어짐
        Node* r2 = reverseIter(r1); assert(items(r2) == v && addrs(r2) == ad); Node* r3 = reverseRec(r2); assert(items(r3) == rv); Node* r4 = reverseRec(r3); assert(items(r4) == v); destroy(r4); assert(Node::live == 0); }
    for (int n = 1; n <= 12; n++) for (int l = 1; l <= n; l++) for (int r = l; r <= n; r++) { std::vector<int> v(n); std::iota(v.begin(), v.end(), 1); std::vector<int> ref = v; std::reverse(ref.begin() + (l - 1), ref.begin() + r);   // ③
        Node* h = reverseBetween(build(v), l, r); assert(items(h) == ref); destroy(h); }
    for (int n = 0; n <= 14; n++) for (int k = 1; k <= n + 2; k++) { std::vector<int> v(n); std::iota(v.begin(), v.end(), 1); std::vector<int> ref = v; for (int g = 0; g + k <= n; g += k) std::reverse(ref.begin() + g, ref.begin() + g + k);
        Node* h = reverseKGroup(build(v), k); assert(items(h) == ref); destroy(h); }
    assert(Node::live == 0 && reverseIter(nullptr) == nullptr && reverseRec(nullptr) == nullptr); { Node* one = build({9}); assert(reverseIter(one) == one && one->next == nullptr); destroy(one); }   // ④
    std::cout << "Reverse: array reversal used exactly floor(n/2) swaps; iterative and recursive pointer reversal kept every node (same addresses, opposite order) and was an involution; sublist and k-group reversal matched std::reverse for all ranges and group sizes" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: 배열·반복 O(1), 재귀 O(N)
```
## Copy()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <new>
#include <random>
#include <unordered_map>
#include <vector>

// 복사(Copy): 얕은 복사(shallow)는 포인터만 복사해 두 변수가 같은 노드를 가리키게 하고, 깊은 복사(deep)는 노드를 새로 할당해 값과 구조를 그대로 옮긴다. 얕은 복사는 O(1) 이지만 한쪽을 고치면 다른 쪽도 변하고, 두 번 해제하면 이중 해제가 된다. 깊은 복사는 O(n) 이고 서로 독립이다.
// 어려운 경우는 노드가 next 외에 임의의 다른 노드를 가리키는 포인터(rnd)를 가질 때다. 해결 방법 둘: (1) 해시 맵: 원본 노드 → 복사본 노드 대응표를 만들고 두 번째 순회에서 next/rnd 를 대응표로 번역한다(O(n) 추가 공간). (2) 끼워 넣기: 각 원본 노드 바로 뒤에 복사본을 끼우면 `원본->rnd->next` 가 곧 복사본의 rnd 이므로 대응표 없이 rnd 를 채울 수 있고, 마지막에 두 리스트로 분리하며 원본을 복원한다(추가 공간 O(1)).
// 배열 리스트의 복사 대입은 복사 후 교환(copy-and-swap) 관용구로 쓰면 자기 대입이 안전하고, 복사 도중 예외가 나도 대상이 바뀌지 않는다(강한 예외 보장).
// 검증: ① 얕은 복사는 노드를 공유(별칭을 고치면 원본이 변함), 깊은 복사는 노드가 하나도 겹치지 않고 독립, 생성 노드 수 n ② 임의 포인터 리스트 복사 두 방식이 구조 동형(값·next·rnd 의 인덱스가 같음)이고 복사본이 원본을 가리키지 않으며 원본이 그대로 복원 ③ k 번째 할당에서 예외가 나도 누수 없음(끼워 넣기 방식은 원본도 복원) ④ 배열 리스트의 복사 대입이 자기 대입에 안전하고 복사 중 예외에서 대상이 변하지 않음.
struct Node { int val; Node *next, *rnd; static int live, failAt; Node(int v) : val(v), next(nullptr), rnd(nullptr) { if (failAt >= 0 && live >= failAt) throw std::bad_alloc(); ++live; } ~Node() { --live; } };
int Node::live = 0, Node::failAt = -1;
Node* build(const std::vector<int>& v) { Node* head = nullptr; Node** t = &head; for (int x : v) { *t = new Node(x); t = &(*t)->next; } return head; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
std::vector<Node*> nodes(Node* h) { std::vector<Node*> r; for (; h; h = h->next) r.push_back(h); return r; }
Node* shallowCopy(Node* h) { return h; }                                                                             // 포인터만 복사: 같은 노드를 공유
Node* deepCopy(const Node* h) { Node* head = nullptr; Node** t = &head; try { for (; h; h = h->next) { *t = new Node(h->val); t = &(*t)->next; } } catch (...) { destroy(head); throw; } return head; }
Node* copyWithMap(const Node* h) {                                                                                   // 대응표 방식
    std::unordered_map<const Node*, Node*> to; Node* head = nullptr; Node** t = &head; try { for (const Node* c = h; c; c = c->next) { *t = new Node(c->val); to[c] = *t; t = &(*t)->next; } } catch (...) { destroy(head); throw; }
    for (const Node* c = h; c; c = c->next) to[c]->rnd = c->rnd ? to[c->rnd] : nullptr; return head; }
Node* copyInterleaved(Node* h) {                                                                                     // 끼워 넣기 방식: 추가 공간 O(1)
    if (!h) return nullptr; Node* c = h;
    try { for (; c; c = c->next->next) { Node* cp = new Node(c->val); cp->next = c->next; c->next = cp; } }
    catch (...) { for (Node* d = h; d != c;) { Node* cp = d->next; d->next = cp->next; delete cp; d = d->next; } throw; }                                              // 이미 끼운 복사본을 빼서 원본 복원
    for (Node* c = h; c; c = c->next->next) c->next->rnd = c->rnd ? c->rnd->next : nullptr;
    Node* copyHead = h->next; for (Node* c = h; c;) { Node* cp = c->next; c->next = cp->next; cp->next = cp->next ? cp->next->next : nullptr; c = c->next; } return copyHead; }
bool isomorphic(Node* a, Node* b) {                                                                                  // 값·next·rnd 의 인덱스가 같은가
    std::vector<Node*> na = nodes(a), nb = nodes(b); if (na.size() != nb.size()) return false; std::unordered_map<Node*, int> ia, ib; for (std::size_t i = 0; i < na.size(); i++) { ia[na[i]] = (int)i; ib[nb[i]] = (int)i; }
    for (std::size_t i = 0; i < na.size(); i++) { if (na[i]->val != nb[i]->val) return false; int ra = na[i]->rnd ? ia[na[i]->rnd] : -1, rb = nb[i]->rnd ? (ib.count(nb[i]->rnd) ? ib[nb[i]->rnd] : -2) : -1; if (ra != rb) return false; } return true; }
struct Tracked { int v; static int live, copiesLeft; Tracked(int x = 0) : v(x) { ++live; } Tracked(const Tracked& o) : v(o.v) { if (copiesLeft == 0) throw std::bad_alloc(); if (copiesLeft > 0) copiesLeft--; ++live; } ~Tracked() { --live; } };
int Tracked::live = 0, Tracked::copiesLeft = -1;
class Arr { Tracked* a_; std::size_t n_; public:
    explicit Arr(std::size_t n = 0) : a_(n ? static_cast<Tracked*>(::operator new(n * sizeof(Tracked))) : nullptr), n_(0) { for (; n_ < n; n_++) new (a_ + n_) Tracked((int)n_); }
    Arr(const Arr& o) : a_(o.n_ ? static_cast<Tracked*>(::operator new(o.n_ * sizeof(Tracked))) : nullptr), n_(0) { try { for (; n_ < o.n_; n_++) new (a_ + n_) Tracked(o.a_[n_]); } catch (...) { clear(); ::operator delete(a_); throw; } }
    ~Arr() { clear(); ::operator delete(a_); } void clear() { while (n_) a_[--n_].~Tracked(); }
    void swap(Arr& o) { std::swap(a_, o.a_); std::swap(n_, o.n_); } Arr& operator=(Arr o) { swap(o); return *this; }                                    // 복사 후 교환
    std::vector<int> items() const { std::vector<int> r; for (std::size_t i = 0; i < n_; i++) r.push_back(a_[i].v); return r; } };
int main() {
    std::mt19937 rng(8);
    { Node* h = build({1, 2, 3, 4}); Node* alias = shallowCopy(h); Node* deep = deepCopy(h); assert(alias == h && Node::live == 8);                                                  // ①
      alias->val = 99; assert(h->val == 99 && deep->val == 1); deep->next->val = 77; assert(h->next->val == 2);
      std::vector<Node*> a = nodes(h), b = nodes(deep); for (Node* x : a) for (Node* y : b) assert(x != y); destroy(h); destroy(deep); assert(Node::live == 0); }
    for (int rep = 0; rep < 200; rep++) { int n = (int)(rng() % 40); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 100); Node* h = build(v); std::vector<Node*> nd = nodes(h);     // ②
        for (Node* c : nd) c->rnd = (n && rng() % 4) ? nd[rng() % n] : nullptr; std::vector<Node*> nextBefore, rndBefore; for (Node* c : nd) { nextBefore.push_back(c->next); rndBefore.push_back(c->rnd); }
        Node* m = copyWithMap(h); Node* il = copyInterleaved(h); assert(Node::live == 3 * n && isomorphic(h, m) && isomorphic(h, il) && isomorphic(m, il));
        for (std::size_t i = 0; i < nd.size(); i++) assert(nd[i]->next == nextBefore[i] && nd[i]->rnd == rndBefore[i]);                                                  // 원본 복원
        std::vector<Node*> nm = nodes(m), ni = nodes(il); for (Node* c : nm) assert(!c->rnd || std::find(nd.begin(), nd.end(), c->rnd) == nd.end()); for (Node* c : ni) assert(!c->rnd || std::find(nd.begin(), nd.end(), c->rnd) == nd.end());
        destroy(h); destroy(m); destroy(il); assert(Node::live == 0); }
    { std::vector<int> v(25); for (int& x : v) x = (int)(rng() % 100); Node* h = build(v); int base = Node::live; for (int k = 0; k < 25; k++) { Node::failAt = base + k; bool threw = false;      // ③
        try { destroy(deepCopy(h)); } catch (const std::bad_alloc&) { threw = true; } assert(threw && Node::live == base); threw = false; try { destroy(copyWithMap(h)); } catch (const std::bad_alloc&) { threw = true; } assert(threw && Node::live == base);
        std::vector<Node*> before = nodes(h); threw = false; try { destroy(copyInterleaved(h)); } catch (const std::bad_alloc&) { threw = true; } assert(threw && Node::live == base && nodes(h) == before); }
      Node::failAt = -1; destroy(h); assert(Node::live == 0); }
    { Arr a(6), b(3); std::vector<int> av = a.items(); a = a; assert(a.items() == av && Tracked::live == 9); b = a; assert(b.items() == av && a.items() == av && Tracked::live == 12);                 // ④
      Arr c(4); std::vector<int> cv = c.items(); for (int k = 0; k < 6; k++) { Tracked::copiesLeft = k; bool threw = false; try { c = a; } catch (const std::bad_alloc&) { threw = true; } assert(threw && c.items() == cv && Tracked::live == 16); }   // 강한 예외 보장
      Tracked::copiesLeft = -1; c = a; assert(c.items() == av); }
    assert(Tracked::live == 0); std::cout << "Copy: shallow copies shared nodes while deep copies were fully independent; the hash-map and O(1)-space interleaving techniques both copied 200 random-pointer lists isomorphically and restored the original; allocation failures leaked nothing; copy-and-swap assignment was self-assignment safe with the strong exception guarantee" << std::endl; return 0;
}
// Time Complexity: 얕은 복사 O(1), 깊은 복사 O(N)
// Space Complexity: 깊은 복사 O(N) (임의 포인터 복사는 대응표 방식 추가 O(N), 끼워 넣기 방식 추가 O(1))
```
## Swap()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <stdexcept>
#include <utility>
#include <vector>

// 교환(Swap): 배열은 두 칸의 값을 맞바꾼다. i == j 일 때도 안전해야 한다 — 임시 변수를 쓰는 교환은 안전하지만 XOR 교환(a^=b; b^=a; a^=b)은 같은 칸을 가리키면 0 이 되어 값이 사라진다. 연결 리스트에서는 값을 맞바꾸는 대신 노드를 다시 연결하는 것이 올바르다(노드가 큰 객체거나 다른 곳에서 노드 포인터를 들고 있을 때 값 교환은 의미가 달라진다).
// 노드 교환의 균일한 방법: 두 노드를 가리키는 연결(포인터의 포인터) pa, pb 를 찾아 `swap(*pa, *pb); swap((*pa)->next, (*pb)->next)` 두 줄이면 떨어져 있든 이웃하든 머리·꼬리든 i == j 든 모두 맞다(이웃한 경우는 중간에 자기를 가리키는 순환이 잠깐 생기지만 두 번째 교환에서 풀린다). 인접한 쌍끼리 교환(swap pairs)도 포인터 재연결로 한다. 리스트 전체의 교환은 머리 포인터와 길이만 맞바꾸면 되어 길이와 무관한 O(1) 이다. 위치 i, j 가 범위 밖이면 걷다가 null 을 역참조하게 되므로 swapNodes 는 먼저 검사해 out_of_range 를 던진다.
// 검증: ① 배열 교환(i == j 포함)이 std::swap 모델과 같고 XOR 교환은 i == j 에서 0 이 되는 함정을 보임 ② 연결 리스트 노드 교환이 모든 (i, j) 쌍(이웃·머리·꼬리·같은 위치)에서 모델(노드 포인터 벡터에 std::swap)과 같은 순서이고 노드 주소와 노드 값이 보존 ③ 무작위 교환 5000 번 뒤에도 순환·유실 없음 ④ 인접 쌍 교환이 기대 결과와 같음 ⑤ 리스트 전체 교환은 머리 포인터와 길이 두 필드만 맞바꾸고 노드 사슬(주소·순서)은 하나도 건드리지 않음(상수 시간은 이 구조에서 나오며 시간·횟수를 재지는 않는다) ⑥ 범위 밖 위치(음수·길이 이상·빈 리스트)는 out_of_range 이고 리스트 불변.
struct Node { int val; Node* next; static int live; Node(int v, Node* nx) : val(v), next(nx) { ++live; } ~Node() { --live; } }; int Node::live = 0;
Node* build(const std::vector<int>& v) { Node* head = nullptr; Node** t = &head; for (int x : v) { *t = new Node(x, nullptr); t = &(*t)->next; } return head; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
std::vector<Node*> nodes(Node* h) { std::vector<Node*> r; for (; h; h = h->next) r.push_back(h); return r; }
void xorSwap(int& a, int& b) { a ^= b; b ^= a; a ^= b; }
void arraySwap(std::vector<int>& a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }                          // 임시 변수 교환(i == j 에서도 안전)
void swapNodes(Node*& head, int i, int j) {                                                                          // 위치 i, j (0 기반) 의 노드를 재연결로 교환, 범위 밖이면 out_of_range
    auto at = [&](int k) { if (k < 0) throw std::out_of_range("swapNodes"); Node** p = &head; for (; k > 0 && *p; k--) p = &(*p)->next; if (!*p) throw std::out_of_range("swapNodes"); return p; };
    Node **pa = at(i), **pb = at(j);
    std::swap(*pa, *pb); std::swap((*pa)->next, (*pb)->next); }
Node* swapPairs(Node* head) { Node** link = &head; while (*link && (*link)->next) { Node *a = *link, *b = a->next; a->next = b->next; b->next = a; *link = b; link = &a->next; } return head; }
struct List { Node* head = nullptr; std::size_t n = 0; };
void swapLists(List& a, List& b) { std::swap(a.head, b.head); std::swap(a.n, b.n); }                              // 필드 두 개만 교환: 노드는 건드리지 않는다
int main() {
    std::mt19937 rng(9);
    { std::vector<int> a = {5, 6, 7}; arraySwap(a, 0, 2); assert(a == (std::vector<int>{7, 6, 5})); arraySwap(a, 1, 1); assert(a == (std::vector<int>{7, 6, 5}));       // ①
      int x = 5, y = 9; xorSwap(x, y); assert(x == 9 && y == 5); int z = 7; xorSwap(z, z); assert(z == 0);                                                               // 함정: 같은 변수를 XOR 교환하면 0
      std::vector<int> v(30); for (int& e : v) e = (int)(rng() % 100); std::vector<int> ref = v; for (int s = 0; s < 1000; s++) { int i = (int)(rng() % 30), j = (int)(rng() % 30); arraySwap(v, i, j); std::swap(ref[i], ref[j]); } assert(v == ref); }
    for (int n = 1; n <= 9; n++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) { std::vector<int> v(n); for (int k = 0; k < n; k++) v[k] = k * 10; Node* h = build(v); std::vector<Node*> model = nodes(h);   // ②
        swapNodes(h, i, j); std::swap(model[i], model[j]); assert(nodes(h) == model); for (Node* c : model) assert(c->val % 10 == 0); assert(model.back()->next == nullptr); destroy(h); assert(Node::live == 0); }
    { std::vector<int> v(50); for (int k = 0; k < 50; k++) v[k] = k; Node* h = build(v); std::vector<Node*> model = nodes(h); for (int s = 0; s < 5000; s++) { int i = (int)(rng() % 50), j = (int)(rng() % 50); swapNodes(h, i, j); std::swap(model[i], model[j]); }   // ③
      assert(nodes(h) == model && Node::live == 50); std::vector<int> vals; for (Node* c : nodes(h)) vals.push_back(c->val); std::sort(vals.begin(), vals.end()); assert(vals == v); destroy(h); }
    for (int n = 0; n <= 11; n++) { std::vector<int> v(n); for (int k = 0; k < n; k++) v[k] = k + 1; std::vector<int> ref = v; for (int k = 0; k + 1 < n; k += 2) std::swap(ref[k], ref[k + 1]);            // ④
        Node* h = swapPairs(build(v)); std::vector<int> got; for (Node* c : nodes(h)) got.push_back(c->val); assert(got == ref); destroy(h); }
    { List a, b; a.head = build(std::vector<int>(10, 1)); a.n = 10; b.head = build(std::vector<int>(100000, 2)); b.n = 100000; std::vector<Node*> na = nodes(a.head), nb = nodes(b.head); swapLists(a, b);   // ⑤ 머리와 길이만 맞바꾼다
      assert(a.n == 100000 && b.n == 10 && a.head->val == 2 && b.head->val == 1 && nodes(a.head) == nb && nodes(b.head) == na);                            // 어느 노드도 건드리지 않았다(주소·순서 그대로)
      List c, d; swapLists(c, d); assert(c.head == nullptr && d.n == 0); destroy(a.head); destroy(b.head); }
    { Node* h = build({1, 2, 3}); std::vector<Node*> before = nodes(h); const int bad[][2] = {{0, 3}, {3, 0}, {5, 1}, {-1, 0}, {0, -1}};                           // ⑥ 범위 밖 위치
      for (const auto& p : bad) { bool threw = false; try { swapNodes(h, p[0], p[1]); } catch (const std::out_of_range&) { threw = true; } assert(threw && nodes(h) == before); }
      Node* none = nullptr; bool threw = false; try { swapNodes(none, 0, 0); } catch (const std::out_of_range&) { threw = true; } assert(threw && none == nullptr); destroy(h); }
    assert(Node::live == 0); std::cout << "Swap: pointer-to-pointer relinking swapped nodes correctly for every pair (adjacent, head, tail, same) up to length 9 and across 5000 random swaps without losing or duplicating nodes; swapping whole lists exchanged only the head pointer and length, leaving every node of a 10-node and a 100000-node list untouched; out-of-range positions threw without changing the list; XOR-swap of a variable with itself zeroed it" << std::endl; return 0;
}
// Time Complexity: 배열 O(1), 연결 리스트 O(max(i, j)) (걷기), 리스트 전체 교환 O(1)
// Space Complexity: O(1)
```
## Clear()
### 대표코드
```cpp
#include <cassert>
#include <iostream>
#include <memory>
#include <new>
#include <numeric>
#include <vector>

// 비우기(Clear): 모든 항목을 없애 길이를 0 으로 만든다. 항목의 소멸자를 정확히 한 번씩 호출해야 하고(누수·이중 소멸 없음), 비운 뒤에도 리스트는 다시 쓸 수 있어야 한다. 배열 리스트는 소멸자만 호출하고 용량(capacity)은 그대로 둔다 — 다음 삽입에서 다시 할당하지 않는다. 연결 리스트는 노드를 하나씩 해제한다.
// 연결 리스트의 소멸을 재귀(`~Node() { delete next; }`)로 쓰면 호출 깊이가 노드 수와 같아 긴 리스트에서 스택이 넘친다. 반복문으로 next 를 미리 저장하고 하나씩 해제해야 한다. 또 머리·꼬리·길이를 모두 초기 상태로 되돌려야 한다 — 꼬리 포인터를 잊으면 비운 뒤 덧붙일 때 해제된 노드를 건드린다.
// 검증: ① 배열 리스트: 소멸자 호출이 정확히 원소 수만큼, 용량·버퍼 주소 유지, 비운 뒤 재사용, 두 번 비워도 안전 ② 연결 리스트(머리·꼬리·길이): 반복 해제로 살아 있는 노드 0 개, 비운 뒤 덧붙이기·앞 삽입이 정상(꼬리 재설정 확인) ③ 재귀 소멸의 호출 깊이는 노드 수와 같음을 작은 리스트로 확인(큰 리스트로는 실행하지 않음), 반복 해제는 1,000,000 노드도 처리.
struct Tracked { int v; static int live; explicit Tracked(int x) : v(x) { ++live; } Tracked(const Tracked& o) : v(o.v) { ++live; } ~Tracked() { --live; } }; int Tracked::live = 0;
class ArrayList { Tracked* buf_ = nullptr; std::size_t size_ = 0, cap_ = 0;
public:
    ~ArrayList() { clear(); ::operator delete(buf_); }
    void push(int v) { if (size_ == cap_) { std::size_t nc = cap_ ? cap_ * 2 : 4; Tracked* nb = static_cast<Tracked*>(::operator new(nc * sizeof(Tracked))); for (std::size_t i = 0; i < size_; i++) { new (nb + i) Tracked(buf_[i]); buf_[i].~Tracked(); } ::operator delete(buf_); buf_ = nb; cap_ = nc; } new (buf_ + size_++) Tracked(v); }
    void clear() { while (size_) buf_[--size_].~Tracked(); }                                                         // 용량은 유지
    std::size_t size() const { return size_; } std::size_t capacity() const { return cap_; } const Tracked* data() const { return buf_; } int at(std::size_t i) const { return buf_[i].v; } };
struct Node { int val; Node* next; static int live; static int depth, maxDepth; Node(int v) : val(v), next(nullptr) { ++live; } ~Node() { --live; } }; int Node::live = 0, Node::depth = 0, Node::maxDepth = 0;
struct RecNode { RecNode* next = nullptr; static int depth, maxDepth; ~RecNode() { ++depth; if (depth > maxDepth) maxDepth = depth; delete next; --depth; } }; int RecNode::depth = 0, RecNode::maxDepth = 0;   // 재귀 소멸자
class LinkedList { Node *head_ = nullptr, *tail_ = nullptr; std::size_t n_ = 0;
public:
    ~LinkedList() { clear(); }
    void pushBack(int v) { Node* x = new Node(v); if (tail_) tail_->next = x; else head_ = x; tail_ = x; n_++; }
    void pushFront(int v) { Node* x = new Node(v); x->next = head_; head_ = x; if (!tail_) tail_ = x; n_++; }
    void clear() { Node* c = head_; while (c) { Node* nx = c->next; delete c; c = nx; } head_ = tail_ = nullptr; n_ = 0; }          // next 를 먼저 저장 → 반복 해제 → 모두 초기화
    std::size_t size() const { return n_; } const Node* head() const { return head_; } const Node* tail() const { return tail_; } };
int main() {
    { ArrayList a; for (int i = 0; i < 100; i++) a.push(i); assert(Tracked::live == 100 && a.size() == 100); std::size_t cap = a.capacity(); const Tracked* buf = a.data();       // ①
      a.clear(); assert(a.size() == 0 && Tracked::live == 0 && a.capacity() == cap && a.data() == buf); a.clear(); assert(Tracked::live == 0);
      for (int i = 0; i < 100; i++) a.push(i * 2); assert(a.capacity() == cap && a.data() == buf && a.at(99) == 198 && Tracked::live == 100); }
    assert(Tracked::live == 0);
    { LinkedList l; for (int i = 0; i < 1000; i++) l.pushBack(i); assert(Node::live == 1000); l.clear(); assert(Node::live == 0 && l.size() == 0 && l.head() == nullptr && l.tail() == nullptr);   // ②
      l.pushBack(1); l.pushBack(2); l.pushFront(0); assert(l.size() == 3 && l.head()->val == 0 && l.tail()->val == 2 && l.tail()->next == nullptr && Node::live == 3); l.clear(); l.clear(); assert(Node::live == 0); }
    { RecNode* head = new RecNode; RecNode* c = head; for (int i = 1; i < 1000; i++) { c->next = new RecNode; c = c->next; } delete head; assert(RecNode::maxDepth == 1000 && RecNode::depth == 0); }   // ③ 재귀 소멸: 깊이 = 노드 수
    { LinkedList big; for (int i = 0; i < 1000000; i++) big.pushBack(i); assert(Node::live == 1000000); big.clear(); assert(Node::live == 0 && big.size() == 0); }
    std::cout << "Clear: array clear ran each destructor exactly once and kept its buffer for reuse; linked clear freed 1,000,000 nodes iteratively and reset head, tail and size; a recursive destructor's depth equalled the node count (1000), which is why it overflows the stack on long lists" << std::endl; return 0;
}
// Time Complexity: O(N) (소멸자·해제 각 한 번)
// Space Complexity: O(1)
```

# Part 2. 배열 리스트
## DynamicArray()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <new>
#include <random>
#include <stdexcept>
#include <utility>
#include <vector>

// 동적 배열(Dynamic Array): 연속된 메모리 블록에 항목을 저장하고, 가득 차면 더 큰 블록을 할당해 옮겨 담는다. 인덱스 접근 O(1), 끝에 덧붙이기 분할상환 O(1) 이 핵심이다. 용량(capacity)은 길이(size)보다 크거나 같다.
// 분할상환이 성립하려면 용량을 곱셈으로 키워야 한다. 인자 2 배: N 번 덧붙이는 동안 복사된 원소 총수 = 1+2+4+… < 2N. 1.5 배: < 3N. 상수 칸만 늘리면(+16) 복사 총수가 N²/32 로 이차 시간이 된다. 한 번의 덧붙이기는 최악 O(n) (용량 n 일 때)이지만 평균은 상수다.
// 재할당하면 모든 원소의 주소가 바뀌므로 이전에 얻은 포인터·참조·반복자는 무효가 된다. 용량 안에서 덧붙이면 주소가 유지된다.
// 검증: ① 무작위 push/pop/접근/clear/shrink 가 std::vector 와 같음 ② 성장 정책별 복사 총수: 2 배 < 2N, 1.5 배 < 3N, +16 > 100N (N=20000), 한 번의 최악 덧붙이기 비용은 그때의 용량과 같음 ③ 원소 수명: 생성자·소멸자 수가 항상 일치(누수·이중 소멸 없음) ④ 범위 밖 at() 는 예외 ⑤ 용량 안에서는 주소 유지, 재할당 시 주소 변경.
enum class Growth { Double, OnePointFive, Plus16 };
template <class T> class DynamicArray {
    T* d_ = nullptr; std::size_t n_ = 0, cap_ = 0; Growth g_;
    std::size_t nextCap() const { switch (g_) { case Growth::Double: return cap_ ? cap_ * 2 : 1; case Growth::OnePointFive: return std::max(cap_ + 1, cap_ + cap_ / 2); default: return cap_ + 16; } }
    void reallocate(std::size_t nc) { T* nd = static_cast<T*>(::operator new(nc * sizeof(T))); for (std::size_t i = 0; i < n_; i++) { new (nd + i) T(std::move(d_[i])); d_[i].~T(); } ::operator delete(d_); d_ = nd; cap_ = nc; }
public:
    long copies = 0, reallocations = 0, lastPushCost = 0;
    explicit DynamicArray(Growth g = Growth::Double) : g_(g) {}
    ~DynamicArray() { clear(); ::operator delete(d_); } DynamicArray(const DynamicArray&) = delete; DynamicArray& operator=(const DynamicArray&) = delete;
    void push_back(const T& v) { lastPushCost = 0; if (n_ == cap_) { lastPushCost = (long)n_; copies += (long)n_; reallocations++; reallocate(nextCap()); } new (d_ + n_) T(v); n_++; }
    void pop_back() { if (!n_) throw std::out_of_range("pop_back"); d_[--n_].~T(); }
    T& at(std::size_t i) { if (i >= n_) throw std::out_of_range("at"); return d_[i]; } T& operator[](std::size_t i) { return d_[i]; }
    void clear() { while (n_) d_[--n_].~T(); }
    void shrink_to_fit() { if (cap_ != n_) { if (n_ == 0) { ::operator delete(d_); d_ = nullptr; cap_ = 0; } else reallocate(n_); } }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } const T* data() const { return d_; }
};
struct Tracked { int v; static int live; explicit Tracked(int x = 0) : v(x) { ++live; } Tracked(const Tracked& o) : v(o.v) { ++live; } Tracked(Tracked&& o) noexcept : v(o.v) { ++live; } ~Tracked() { --live; } }; int Tracked::live = 0;
int main() {
    std::mt19937 rng(10);
    { DynamicArray<int> a; std::vector<int> ref; for (int step = 0; step < 60000; step++) { int op = (int)(rng() % 20);                                           // ①
          if (op < 11) { int v = (int)rng(); a.push_back(v); ref.push_back(v); } else if (op < 16) { if (!ref.empty()) { a.pop_back(); ref.pop_back(); } }
          else if (op < 19) { if (!ref.empty()) { std::size_t i = rng() % ref.size(); assert(a[i] == ref[i] && a.at(i) == ref[i]); } } else if (op == 19 && rng() % 8 == 0) { if (rng() % 2) { a.clear(); ref.clear(); } else a.shrink_to_fit(); }
          assert(a.size() == ref.size() && a.capacity() >= a.size()); }
      for (std::size_t i = 0; i < ref.size(); i++) assert(a[i] == ref[i]); a.shrink_to_fit(); assert(a.capacity() == a.size()); a.clear(); a.shrink_to_fit(); assert(a.capacity() == 0 && a.data() == nullptr); }
    for (int N : {1, 2, 3, 100, 1025, 100000}) { DynamicArray<int> d(Growth::Double), h(Growth::OnePointFive); for (int i = 0; i < N; i++) { d.push_back(i); h.push_back(i); }        // ②
        assert(d.copies < 2L * N && h.copies < 3L * N + 4 && d.capacity() < 2 * (std::size_t)N + 1); }
    { const int N = 20000; DynamicArray<int> c(Growth::Plus16); for (int i = 0; i < N; i++) c.push_back(i); assert(c.copies > 100L * N);
      DynamicArray<int> d; long maxCost = 0; for (int i = 0; i < 5000; i++) { std::size_t capBefore = d.capacity(); d.push_back(i); if (d.lastPushCost) assert(d.lastPushCost == (long)capBefore); maxCost = std::max(maxCost, d.lastPushCost); } assert(maxCost == 4096); }
    { DynamicArray<Tracked> t; for (int i = 0; i < 1000; i++) { t.push_back(Tracked(i)); assert(Tracked::live == (int)t.size()); } for (int i = 0; i < 400; i++) t.pop_back(); assert(Tracked::live == 600); t.shrink_to_fit(); assert(Tracked::live == 600 && t.capacity() == 600); t.clear(); assert(Tracked::live == 0); }   // ③
    { DynamicArray<int> a; a.push_back(1); bool threw = false; try { a.at(1); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; DynamicArray<int> e; try { e.pop_back(); } catch (const std::out_of_range&) { threw = true; } assert(threw); }   // ④
    { DynamicArray<int> a; for (int i = 0; i < 5; i++) a.push_back(i); const int* before = a.data(); assert(a.capacity() == 8); a.push_back(5); a.push_back(6); a.push_back(7); assert(a.data() == before);        // ⑤ 용량 안: 주소 유지
      a.push_back(8); assert(a.capacity() == 16 && a.data() != before); }
    assert(Tracked::live == 0); std::cout << "DynamicArray: 60000 random operations matched std::vector; doubling copied < 2N elements, 1.5x < 3N, and a constant +16 step copied > 100N (quadratic); the worst single push cost equalled the capacity at that moment; element lifetimes balanced and addresses changed only on reallocation" << std::endl; return 0;
}
// Time Complexity: 접근 O(1), push_back 분할상환 O(1) (최악 O(N)), pop_back O(1)
// Space Complexity: O(N) (용량은 길이의 2 배 이내)
```
## Resize()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <new>
#include <random>
#include <type_traits>
#include <utility>
#include <vector>

// 크기 조절(Resize): resize(n) 은 길이를 n 으로 만든다 — 줄이면 뒤쪽 원소를 소멸시키고(용량은 그대로), 늘리면 새 원소를 값 초기화(int 는 0, 또는 지정한 값)한다. reserve(c) 는 길이를 바꾸지 않고 용량만 미리 확보해 이후 재할당을 막는다. shrink_to_fit() 은 남는 용량을 반납한다.
// 재할당 중에는 원소를 새 블록으로 옮기는데, 이동 생성자가 예외를 던지지 않으면(noexcept) 이동하고, 던질 수 있으면 복사한다(std::move_if_noexcept). 복사 중 예외가 나면 이미 만든 새 원소를 모두 소멸시키고 원래 상태를 그대로 둔다 — 강한 예외 보장. 새 원소를 먼저 만든 뒤에 기존 원소를 옮겨야 값 복사 실패 때 기존 원소를 건드리지 않는다.
// 검증: ① 무작위 resize/reserve/shrink 가 std::vector 의 길이·내용과 같고 reserve 는 길이 불변, 줄여도 용량 유지, shrink_to_fit 후 용량 == 길이 ② 늘릴 때 새 원소가 값 초기화(이전에 쓰레기 값이 있던 칸도 0)이고 resize(n, v) 는 v 로 채움 ③ 이동 가능한 타입은 이동(복사 0), 이동이 던질 수 있는 복사 가능 타입은 복사(이동 0) ④ 복사가 k 번째에서 던져도(모든 k, 재할당 경로와 용량이 충분한 제자리 경로 모두) 길이·내용·저장소·생존 객체 수가 변하지 않음 ⑤ 줄이면 소멸자 정확히 한 번 ⑥ 한 칸씩 늘려도 용량이 매번 정확히 두 배가 되어 재할당이 log N 번뿐(분할상환)이고 큰 점프는 요청한 크기까지 한 번에 늘어남.
template <class T> class Vec {
    T* d_ = nullptr; std::size_t n_ = 0, cap_ = 0;
    static T* alloc(std::size_t n) { return n ? static_cast<T*>(::operator new(n * sizeof(T))) : nullptr; }
    void destroyRange(T* p, std::size_t from, std::size_t to) { while (to > from) p[--to].~T(); }
    void relocate(std::size_t newCap, std::size_t newSize, const T* fill) {                                          // 새 블록에서 [n_, newSize) 를 fill 로 먼저 만들고, 그다음 기존 원소를 옮긴다
        T* nd = alloc(newCap); std::size_t made = 0, moved = 0;
        try { for (std::size_t i = n_; i < newSize; i++) { if (fill) new (nd + i) T(*fill); else new (nd + i) T(); made++; }
              for (; moved < n_; moved++) new (nd + moved) T(std::move_if_noexcept(d_[moved])); }
        catch (...) { destroyRange(nd, 0, moved); destroyRange(nd + n_, 0, made); ::operator delete(nd); throw; }
        destroyRange(d_, 0, n_); ::operator delete(d_); d_ = nd; cap_ = newCap; n_ = newSize;
    }
public:
    Vec() = default; ~Vec() { destroyRange(d_, 0, n_); ::operator delete(d_); } Vec(const Vec&) = delete; Vec& operator=(const Vec&) = delete;
    void reserve(std::size_t c) { if (c > cap_) relocate(c, n_, nullptr); }
    void resize(std::size_t n, const T* fill = nullptr) {
        if (n <= n_) { destroyRange(d_, n, n_); n_ = n; return; }
        if (n > cap_) { relocate(std::max(n, cap_ * 2), n, fill); return; }
        std::size_t made = n_; try { for (; made < n; made++) { if (fill) new (d_ + made) T(*fill); else new (d_ + made) T(); } } catch (...) { destroyRange(d_, n_, made); throw; } n_ = n; }
    void shrink_to_fit() { if (cap_ == n_) return; if (n_ == 0) { ::operator delete(d_); d_ = nullptr; cap_ = 0; } else relocate(n_, n_, nullptr); }
    void push_back(const T& v) { if (n_ == cap_) relocate(cap_ ? cap_ * 2 : 1, n_, nullptr); new (d_ + n_) T(v); n_++; }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } T& operator[](std::size_t i) { return d_[i]; } const T* data() const { return d_; }
};
struct Counting { int v; static int live, copies, moves, copyBudget; Counting(int x = 0) : v(x) { ++live; }
    Counting(const Counting& o) : v(o.v) { if (copyBudget == 0) throw std::bad_alloc(); if (copyBudget > 0) copyBudget--; ++live; copies++; }
    Counting(Counting&& o) noexcept : v(o.v) { ++live; moves++; } ~Counting() { --live; } };
struct ThrowMove { int v; static int live, copies, moves; ThrowMove(int x = 0) : v(x) { ++live; } ThrowMove(const ThrowMove& o) : v(o.v) { ++live; copies++; } ThrowMove(ThrowMove&& o) noexcept(false) : v(o.v) { ++live; moves++; } ~ThrowMove() { --live; } };
struct Counting2 { int v; static int live, copies, moves, copyBudget; Counting2(int x = 0) : v(x) { ++live; }
    Counting2(const Counting2& o) : v(o.v) { if (copyBudget == 0) throw std::bad_alloc(); if (copyBudget > 0) copyBudget--; ++live; copies++; } ~Counting2() { --live; } };      // 이동 생성자 없음 → 복사 사용
int Counting::live = 0, Counting::copies = 0, Counting::moves = 0, Counting::copyBudget = -1; int ThrowMove::live = 0, ThrowMove::copies = 0, ThrowMove::moves = 0;
int Counting2::live = 0, Counting2::copies = 0, Counting2::moves = 0, Counting2::copyBudget = -1;
int main() {
    std::mt19937 rng(11);
    { Vec<int> v; std::vector<int> ref; for (int step = 0; step < 4000; step++) { int op = (int)(rng() % 4); std::size_t n = rng() % 200;                                             // ①
          if (op == 0) { std::size_t before = v.size(); v.reserve(n); assert(v.size() == before && v.capacity() >= n); }
          else if (op == 1) { std::size_t capBefore = v.capacity(); std::size_t sz = std::min<std::size_t>(n, v.size()); v.resize(sz); ref.resize(sz); assert(v.capacity() == capBefore); }
          else if (op == 2) { int fill = (int)(rng() % 100); v.resize(n, &fill); ref.resize(n, fill); } else { v.shrink_to_fit(); assert(v.capacity() == v.size()); }
          assert(v.size() == ref.size()); for (std::size_t i = 0; i < ref.size(); i++) assert(v[i] == ref[i]); } }
    { Vec<int> v; for (int i = 0; i < 20; i++) v.push_back(77); v.resize(0); v.resize(10); for (int i = 0; i < 10; i++) assert(v[i] == 0); int nine = 9; v.resize(15, &nine); for (int i = 0; i < 10; i++) assert(v[i] == 0); for (int i = 10; i < 15; i++) assert(v[i] == 9); }       // ② 값 초기화
    { Vec<Counting> v; Counting::copies = Counting::moves = 0; for (int i = 0; i < 100; i++) v.push_back(Counting(i)); assert(Counting::copies == 100 && Counting::moves > 0);                          // ③ push 는 복사 100 번(인자), 재할당은 이동
      int copiesAfterPush = Counting::copies, movesBeforeReserve = Counting::moves; v.reserve(1000); assert(Counting::copies == copiesAfterPush && Counting::moves - movesBeforeReserve == 100); Vec<ThrowMove> t; ThrowMove::copies = ThrowMove::moves = 0; for (int i = 0; i < 50; i++) t.push_back(ThrowMove(i));
      assert(ThrowMove::moves == 0 && ThrowMove::copies > 50); Vec<Counting2> c; Counting2::copies = 0; for (int i = 0; i < 50; i++) c.push_back(Counting2(i)); assert(Counting2::copies > 50); }
    assert(Counting::live == 0 && ThrowMove::live == 0 && Counting2::live == 0);
    { for (int mode = 0; mode < 2; mode++) for (int k = 0; k < 40; k++) { Vec<Counting2> v; for (int i = 0; i < 6; i++) v.push_back(Counting2(i)); if (mode) v.reserve(40); std::size_t cap = v.capacity(), n = v.size(); const Counting2* base = v.data(); int live = Counting2::live;   // ④ 강한 예외 보장: mode 0 은 재할당 경로, mode 1 은 용량이 충분한 제자리 경로
          Counting2::copyBudget = k; bool threw = false; try { Counting2 fill(5); v.resize(30, &fill); } catch (const std::bad_alloc&) { threw = true; }
          if (threw) { assert(v.size() == n && v.capacity() == cap && v.data() == base && Counting2::live == live); for (std::size_t i = 0; i < n; i++) assert(v[i].v == (int)i); } else { assert(v.size() == 30 && (mode == 0 || (v.data() == base && v.capacity() == cap))); }
          Counting2::copyBudget = -1; assert(Counting2::live == (int)v.size()); } }
    assert(Counting2::live == 0);
    { Vec<Counting> v; for (int i = 0; i < 50; i++) v.push_back(Counting(i)); assert(Counting::live == 50); v.resize(20); assert(Counting::live == 20 && v.size() == 20 && v.capacity() >= 50); v.shrink_to_fit(); assert(v.capacity() == 20 && Counting::live == 20); v.resize(0); assert(Counting::live == 0); }   // ⑤
    { Vec<int> v; std::size_t changes = 0, lastCap = 0; for (std::size_t n = 1; n <= 1000; n++) { v.resize(n); if (v.capacity() != lastCap) { if (lastCap) assert(v.capacity() == 2 * lastCap); lastCap = v.capacity(); changes++; } } assert(changes == 11 && v.capacity() == 1024); v.resize(5000); assert(v.capacity() == 5000 && v.size() == 5000); }   // ⑥ 한 칸씩 늘리면 용량 1, 2, 4, …, 1024 (11 번), 큰 점프는 요청 크기까지
    assert(Counting::live == 0); std::cout << "Resize: 4000 random reserve/resize/shrink operations matched std::vector semantics (reserve keeps size, shrinking keeps capacity); growth value-initialized new elements; noexcept-move types were moved while throwing-move types were copied; a copy failing at any position (during reallocation and during in-place growth) left size, contents, storage and live-object count unchanged; growing one element at a time doubled the capacity each time (11 reallocations up to 1000 elements)" << std::endl; return 0;
}
// Time Complexity: resize 줄이기 O(줄인 수), 늘리기 O(N) (재할당 포함, 분할상환 O(추가 수)), reserve O(N)
// Space Complexity: O(용량)
```
## ShiftLeft()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 왼쪽으로 밀기(ShiftLeft): 배열의 원소를 k 칸 앞으로 당긴다. 두 가지 뜻이 있다. (1) 논리 이동: a[i] = a[i+k] (i < n−k), 앞의 k 개는 버려지고 뒤에 빈칸 k 개가 생겨 채움 값으로 메운다 — 삭제 뒤 틈을 메울 때 쓴다. 앞에서 뒤로 복사하면 겹치는 구간도 안전하다(읽는 칸이 쓰는 칸보다 항상 앞이 아니라 뒤이므로 아직 덮어쓰지 않은 값을 읽는다). (2) 회전: 앞의 k 개를 버리지 않고 뒤로 보낸다(원형 이동).
// 회전의 세 가지 방법: 임시 버퍼(앞 k 개를 저장하고 당긴 뒤 뒤에 붙임, 추가 공간 O(k)), 저글링(gcd(n,k) 개의 순환 고리를 따라 한 번씩만 씀, 추가 공간 O(1), 쓰기 정확히 n 번), 세 번 뒤집기(앞 k 개, 나머지, 전체를 각각 뒤집으면 왼쪽 회전 — 교환 ⌊k/2⌋+⌊(n−k)/2⌋+⌊n/2⌋ 번).
// 검증: ① 논리 이동이 모델과 같고 k ≥ n 이면 전부 채움 값 ② 회전 세 방법이 모든 (n ≤ 24, k ≤ 2n) 조합에서 std::rotate 와 같음(k 는 n 으로 나눈 나머지로 처리) ③ 저글링의 쓰기 횟수가 정확히 n, 세 번 뒤집기의 교환 횟수가 위 식과 같음 ④ 큰 배열(10 만)에서도 같음 ⑤ 빈 배열·k = 0 경계.
void shiftLeft(std::vector<int>& a, std::size_t k, int fill) { std::size_t n = a.size(); if (k > n) k = n; for (std::size_t i = 0; i + k < n; i++) a[i] = a[i + k]; for (std::size_t i = n - k; i < n; i++) a[i] = fill; }
void rotateLeftTemp(std::vector<int>& a, std::size_t k) { std::size_t n = a.size(); if (!n) return; k %= n; if (!k) return; std::vector<int> tmp(a.begin(), a.begin() + k); for (std::size_t i = 0; i + k < n; i++) a[i] = a[i + k]; std::copy(tmp.begin(), tmp.end(), a.end() - k); }
long rotateLeftJuggling(std::vector<int>& a, std::size_t k) {                                                       // 반환: 쓰기 횟수
    std::size_t n = a.size(); if (!n) return 0; k %= n; if (!k) return 0; long writes = 0; std::size_t g = std::gcd(n, k);
    for (std::size_t start = 0; start < g; start++) { int tmp = a[start]; std::size_t i = start; for (;;) { std::size_t j = (i + k) % n; if (j == start) break; a[i] = a[j]; writes++; i = j; } a[i] = tmp; writes++; }
    return writes; }
long rotateLeftReversal(std::vector<int>& a, std::size_t k) {                                                       // 반환: 교환 횟수
    std::size_t n = a.size(); if (!n) return 0; k %= n; if (!k) return 0; long swaps = 0; auto rev = [&](std::size_t l, std::size_t r) { while (l + 1 < r) { std::swap(a[l], a[r - 1]); l++; r--; swaps++; } };
    rev(0, k); rev(k, n); rev(0, n); return swaps; }
int main() {
    std::mt19937 rng(12);
    for (std::size_t n = 0; n <= 12; n++) for (std::size_t k = 0; k <= n + 3; k++) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 1); std::vector<int> ref(n, -1); for (std::size_t i = 0; i < n; i++) if (i + k < n) ref[i] = (int)(i + k + 1);   // ①
        shiftLeft(a, k, -1); assert(a == ref); if (k >= n) for (int x : a) assert(x == -1); }
    for (std::size_t n = 0; n <= 24; n++) for (std::size_t k = 0; k <= 2 * n + 1; k++) { std::vector<int> base(n); std::iota(base.begin(), base.end(), 0); std::vector<int> ref = base; if (n) std::rotate(ref.begin(), ref.begin() + (k % n), ref.end());   // ②
        std::vector<int> a = base, b = base, c = base; rotateLeftTemp(a, k); long w = rotateLeftJuggling(b, k); long s = rotateLeftReversal(c, k); assert(a == ref && b == ref && c == ref);
        if (n && k % n) { std::size_t kk = k % n; assert(w == (long)n && s == (long)(kk / 2 + (n - kk) / 2 + n / 2)); } else assert(w == 0 && s == 0); }                                  // ③
    { std::size_t n = 100000; std::vector<int> base(n); for (int& x : base) x = (int)rng(); for (std::size_t k : {1ul, 7ul, 50000ul, 99999ul, 123457ul}) { std::vector<int> ref = base; std::rotate(ref.begin(), ref.begin() + (k % n), ref.end());      // ④
        std::vector<int> a = base, b = base, c = base; rotateLeftTemp(a, k); assert(rotateLeftJuggling(b, k) == (long)n); rotateLeftReversal(c, k); assert(a == ref && b == ref && c == ref); } }
    { std::vector<int> e; shiftLeft(e, 3, 0); rotateLeftTemp(e, 3); assert(rotateLeftJuggling(e, 3) == 0 && rotateLeftReversal(e, 3) == 0 && e.empty()); std::vector<int> a = {1, 2, 3}; shiftLeft(a, 0, 9); assert(a == (std::vector<int>{1, 2, 3})); }   // ⑤
    std::cout << "ShiftLeft: logical shifts matched the definition for every n<=12 and k<=n+3; the temp-buffer, juggling (exactly n writes) and triple-reversal (floor(k/2)+floor((n-k)/2)+floor(n/2) swaps) rotations matched std::rotate for every n<=24 and k<=2n+1 and for 100000-element arrays" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: 논리 이동·저글링·뒤집기 O(1), 임시 버퍼 O(k)
```
## ShiftRight()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 오른쪽으로 밀기(ShiftRight): 배열의 원소를 k 칸 뒤로 민다. 삽입 때 pos 뒤에 k 칸짜리 틈을 열 때 쓴다: a[i+k] = a[i] (i 는 pos 이상). 겹치는 구간을 앞에서부터 복사하면 같은 원소가 반복해서 덮어쓰기 때문에 틀린다 — 오른쪽 이동은 반드시 뒤에서부터(큰 인덱스부터) 복사해야 한다. 이것이 memcpy 와 memmove 의 차이이며 memmove 는 겹침을 알아서 처리한다.
// 오른쪽 회전(원소를 버리지 않고 뒤의 k 개가 앞으로 옴)은 왼쪽 회전 n−k 와 같다. 세 번 뒤집기로도 가능: 전체를 뒤집고 앞 k 개와 나머지를 각각 뒤집는다.
// 검증: ① 앞에서부터 복사하는 순진한 구현이 겹침에서 첫 원소를 반복해 틀린 결과를 내고, 뒤에서부터 복사하는 구현과 memmove 는 모델과 같음(모든 n, k) ② 틈 열기(openGap)가 std::vector::insert(pos, k, x) 와 같은 결과 ③ 오른쪽 회전 세 방법(뒤집기, 왼쪽 n−k, std::rotate)이 모든 (n ≤ 24, k ≤ 2n) 에서 같음 ④ 큰 배열·경계(k = 0, k ≥ n, 빈 배열).
void shiftRightNaive(std::vector<int>& a, std::size_t k) { std::size_t n = a.size(); for (std::size_t i = 0; i + k < n; i++) a[i + k] = a[i]; }              // 틀림: 앞에서부터 복사
void shiftRight(std::vector<int>& a, std::size_t k, int fill) { std::size_t n = a.size(); if (k > n) k = n; for (std::size_t i = n - k; i-- > 0;) a[i + k] = a[i]; for (std::size_t i = 0; i < k; i++) a[i] = fill; }   // 뒤에서부터
void shiftRightMemmove(std::vector<int>& a, std::size_t k, int fill) { std::size_t n = a.size(); if (k > n) k = n; if (n - k) std::memmove(a.data() + k, a.data(), (n - k) * sizeof(int)); for (std::size_t i = 0; i < k; i++) a[i] = fill; }
void openGap(std::vector<int>& a, std::size_t pos, std::size_t k, int fill) {                                       // pos 에 k 칸 틈을 열고 fill 로 채움(길이 n+k)
    std::size_t n = a.size(); a.resize(n + k); for (std::size_t i = n; i-- > pos;) a[i + k] = a[i]; for (std::size_t i = pos; i < pos + k; i++) a[i] = fill; }
void rotateRightReversal(std::vector<int>& a, std::size_t k) { std::size_t n = a.size(); if (!n) return; k %= n; std::reverse(a.begin(), a.end()); std::reverse(a.begin(), a.begin() + k); std::reverse(a.begin() + k, a.end()); }
void rotateRightViaLeft(std::vector<int>& a, std::size_t k) { std::size_t n = a.size(); if (!n) return; k %= n; std::rotate(a.begin(), a.begin() + (n - k) % n, a.end()); }
int main() {
    bool naiveWrongSeen = false;
    for (std::size_t n = 0; n <= 12; n++) for (std::size_t k = 0; k <= n + 3; k++) { std::vector<int> base(n); std::iota(base.begin(), base.end(), 1); std::vector<int> ref(n, -1); for (std::size_t i = 0; i + k < n; i++) ref[i + k] = base[i];   // ①
        std::vector<int> a = base, b = base, c = base; shiftRight(a, k, -1); shiftRightMemmove(b, k, -1); assert(a == ref && b == ref);
        shiftRightNaive(c, k); for (std::size_t i = 0; i < k && i < n; i++) c[i] = -1; if (c != ref) naiveWrongSeen = true; if (k >= 1 && n > 2 * k) assert(c != ref); }                                          // 순진한 구현은 겹침(n > 2k)에서 틀린다
    assert(naiveWrongSeen);
    { std::mt19937 rng(13); for (int rep = 0; rep < 500; rep++) { std::size_t n = rng() % 40, pos = n ? rng() % (n + 1) : 0, k = rng() % 10; std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 100); std::vector<int> ref = a, got = a;   // ②
          ref.insert(ref.begin() + pos, k, 7); openGap(got, pos, k, 7); assert(got == ref); } }
    for (std::size_t n = 0; n <= 24; n++) for (std::size_t k = 0; k <= 2 * n; k++) { std::vector<int> base(n); std::iota(base.begin(), base.end(), 0); std::vector<int> a = base, b = base, ref = base;                  // ③
        if (n) std::rotate(ref.begin(), ref.begin() + (n - k % n) % n, ref.end()); rotateRightReversal(a, k); rotateRightViaLeft(b, k); assert(a == ref && b == ref); if (n) for (std::size_t i = 0; i < n; i++) assert(ref[(i + k) % n] == base[i]); }   // 원소 i 는 (i+k)%n 로 간다
    { std::size_t n = 100000; std::mt19937 rng(14); std::vector<int> base(n); for (int& x : base) x = (int)rng(); for (std::size_t k : {0ul, 1ul, 5ul, 50000ul, 99999ul, 100000ul, 250001ul}) { std::vector<int> a = base, ref = base; rotateRightReversal(a, k); std::rotate(ref.begin(), ref.begin() + (n - k % n) % n, ref.end()); assert(a == ref);     // ④
        std::vector<int> s = base, m = base; shiftRight(s, k, 0); shiftRightMemmove(m, k, 0); assert(s == m); } }
    { std::vector<int> e; shiftRight(e, 2, 0); shiftRightMemmove(e, 2, 0); rotateRightReversal(e, 2); rotateRightViaLeft(e, 2); openGap(e, 0, 3, 5); assert(e == (std::vector<int>{5, 5, 5})); }
    std::cout << "ShiftRight: the naive forward copy was wrong whenever the ranges overlapped, while backward copy and memmove matched the definition for every n<=12, k<=n+3; gap opening matched vector::insert, and right rotation by reversals equalled rotate-left-by-(n-k) for every n<=24 and k<=2n" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## InsertAt()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <iterator>
#include <list>
#include <new>
#include <random>
#include <stdexcept>
#include <vector>

// 위치 삽입(InsertAt): 배열 리스트에서 pos 위치에 항목을 끼워 넣는 연산이다. 용량이 모자라면 먼저 키우고, pos 이후를 뒤로 민 뒤 값을 쓴다. 여러 개를 넣을 때(범위 삽입)는 항목마다 밀면 m·(n−pos) 번 이동하지만, 틈을 한 번에 m 칸 열고 채우면 (n−pos) + m 번이다 — 같은 결과를 훨씬 적은 이동으로 얻는다.
// 순서가 중요하지 않다면 더 싼 방법이 있다: 끝에 넣고 pos 의 항목과 자리를 바꾸면(unordered insert) O(1) 이다. 입력 범위가 자기 자신(같은 배열의 일부)일 수 있으므로 재할당과 이동 중에 원본이 무효가 되는 일이 없어야 한다.
// 검증: ① 단일 삽입이 std::vector::insert 와 같고 이동 횟수 == n−pos ② 범위 삽입(다양한 반복자: 벡터·리스트·입력 크기 0)이 같은 결과이고 이동 횟수 == (n−pos), 항목별 삽입의 이동은 m·(n−pos) 로 훨씬 큼 ③ 순서 무관 삽입은 새 값이 pos 에 들어가고 옛 pos 항목이 맨 뒤로 가며 원소 집합이 같고 이동 1 회 ④ 범위 밖 pos 는 예외이고 불변 ⑤ 자기 자신의 일부를 삽입해도 정확함.
struct ArrayList { std::vector<int> a; long moves = 0;
    void insertAt(std::size_t pos, int v) { if (pos > a.size()) throw std::out_of_range("insertAt"); a.push_back(0); for (std::size_t i = a.size() - 1; i > pos; i--) { a[i] = a[i - 1]; moves++; } a[pos] = v; }
    template <class It> void insertRange(std::size_t pos, It first, It last) {                                       // 틈을 한 번에 열고 채운다
        if (pos > a.size()) throw std::out_of_range("insertRange"); std::vector<int> items(first, last); std::size_t m = items.size(), n = a.size(); a.resize(n + m);   // items 로 먼저 복사 → 자기 범위여도 안전
        for (std::size_t i = n; i-- > pos;) { a[i + m] = a[i]; moves++; } std::copy(items.begin(), items.end(), a.begin() + pos); }
    void insertUnordered(std::size_t pos, int v) { if (pos > a.size()) throw std::out_of_range("insertUnordered"); a.push_back(v); if (pos != a.size() - 1) std::swap(a[pos], a.back()); moves++; } };   // 끝에 넣고 자리 교환
int main() {
    std::mt19937 rng(15);
    { ArrayList al; std::vector<int> ref; for (int step = 0; step < 300; step++) { std::size_t pos = rng() % (ref.size() + 1); int v = (int)(rng() % 1000); long before = al.moves; al.insertAt(pos, v); ref.insert(ref.begin() + pos, v);   // ①
        assert(al.a == ref && al.moves - before == (long)(ref.size() - 1 - pos)); } }
    for (int rep = 0; rep < 300; rep++) { ArrayList bulk, single; std::size_t n = rng() % 60; for (std::size_t i = 0; i < n; i++) { int x = (int)(rng() % 100); bulk.a.push_back(x); single.a.push_back(x); } std::vector<int> ref = bulk.a;   // ②
        std::size_t pos = rng() % (n + 1), m = rng() % 12; std::vector<int> items(m); for (int& x : items) x = (int)(rng() % 100 + 1000); ref.insert(ref.begin() + pos, items.begin(), items.end());
        bulk.insertRange(pos, items.begin(), items.end()); assert(bulk.a == ref && bulk.moves == (long)(n - pos)); for (std::size_t j = 0; j < m; j++) single.insertAt(pos + j, items[j]); assert(single.a == ref && single.moves == (long)(m * (n - pos)));
        std::list<int> lst(items.begin(), items.end()); ArrayList fromList; fromList.a.assign(bulk.a.begin(), bulk.a.begin() + std::min<std::size_t>(n, 3)); std::vector<int> r2 = fromList.a; std::size_t p2 = rng() % (r2.size() + 1); r2.insert(r2.begin() + p2, lst.begin(), lst.end()); fromList.insertRange(p2, lst.begin(), lst.end()); assert(fromList.a == r2); }
    { ArrayList u; std::vector<int> ref; for (int i = 0; i < 100; i++) { std::size_t pos = rng() % (u.a.size() + 1); long before = u.moves; int displaced = pos < u.a.size() ? u.a[pos] : i; u.insertUnordered(pos, i); ref.push_back(i); assert(u.moves - before == 1 && u.a.size() == ref.size() && u.a[pos] == i && u.a.back() == displaced); }   // 새 값은 pos 에, 밀려난 옛 항목은 맨 뒤에   // ③
      std::vector<int> a = u.a, b = ref; std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end()); assert(a == b); }
    { ArrayList al; al.a = {1, 2, 3}; bool threw = false; for (std::size_t bad : {4ul, 100ul}) { try { al.insertAt(bad, 0); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; try { std::vector<int> x{1}; al.insertRange(bad, x.begin(), x.end()); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; }
      assert(al.a == (std::vector<int>{1, 2, 3})); al.insertAt(3, 4); al.insertAt(0, 0); assert(al.a == (std::vector<int>{0, 1, 2, 3, 4})); }                                              // ④ 경계: 맨 뒤·맨 앞
    { ArrayList al; al.a = {1, 2, 3, 4, 5}; al.insertRange(2, al.a.begin() + 1, al.a.begin() + 4); assert(al.a == (std::vector<int>{1, 2, 2, 3, 4, 3, 4, 5})); }   // ⑤ 자기 범위
    std::cout << "InsertAt: single insertion moved exactly n-pos elements, bulk insertion moved n-pos once instead of m*(n-pos), unordered insertion cost one move, invalid positions threw, and inserting a range of the array into itself was handled safely" << std::endl; return 0;
}
// Time Complexity: 단일 O(N−pos), 범위 삽입 O(N−pos+m), 순서 무관 삽입 O(1)
// Space Complexity: O(1) (범위 삽입은 임시 O(m))
```
## DeleteAt()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

// 위치 삭제(DeleteAt): 배열 리스트에서 pos 위치의 항목을 지운다. 뒤의 항목을 한 칸씩 앞으로 당기므로 n−pos−1 번 이동한다. 구간 삭제 [first, last) 는 한 번에 (n−last) 번만 이동하면 되고, 하나씩 지우면 k = last−first 일 때 k(n−first) − k(k+1)/2 번(대략 k 배)이다.
// 순서가 필요 없다면 지울 자리에 마지막 항목을 덮어쓰고 길이만 줄이면 O(1) 이다(unordered erase) — 대신 순서가 바뀐다. 조건에 맞는 항목을 모두 지울 때는 읽기/쓰기 두 포인터로 한 번만 훑는다(erase–remove 관용구). 지운 뒤 용량은 줄지 않는다.
// 검증: ① 단일 삭제가 std::vector::erase 와 같고 이동 횟수 == n−pos−1 ② 구간 삭제가 같은 결과이고 이동 횟수 == n−last, 하나씩 삭제는 k(n−first) − k(k+1)/2 ③ 순서 무관 삭제는 이동이 정확히 (pos 가 마지막이 아니면 1, 마지막이면 0) 회이고 지운 자리에 옛 마지막 항목이 들어오며 원소 집합이 맞음 ④ 조건 삭제가 erase–remove(remove_if + erase) 와 같고 한 번의 순회 ⑤ 범위 밖 위치·역전된 구간은 예외이고 불변 ⑥ 용량 유지.
struct ArrayList { std::vector<int> a; long moves = 0;
    void eraseAt(std::size_t pos) { if (pos >= a.size()) throw std::out_of_range("eraseAt"); for (std::size_t i = pos; i + 1 < a.size(); i++) { a[i] = a[i + 1]; moves++; } a.pop_back(); }
    void eraseRange(std::size_t first, std::size_t last) { if (first > last || last > a.size()) throw std::out_of_range("eraseRange"); std::size_t k = last - first; for (std::size_t i = last; i < a.size(); i++) { a[i - k] = a[i]; moves++; } a.resize(a.size() - k); }
    int eraseUnordered(std::size_t pos) { if (pos >= a.size()) throw std::out_of_range("eraseUnordered"); int gone = a[pos]; if (pos != a.size() - 1) { a[pos] = a.back(); moves++; } a.pop_back(); return gone; }
    template <class Pred> long eraseIf(Pred p) { long inspected = 0; std::size_t w = 0; for (std::size_t r = 0; r < a.size(); r++) { inspected++; if (!p(a[r])) { if (w != r) { a[w] = a[r]; moves++; } w++; } } a.resize(w); return inspected; } };
int main() {
    std::mt19937 rng(16);
    { ArrayList al; for (int i = 0; i < 150; i++) al.a.push_back((int)(rng() % 1000)); std::vector<int> ref = al.a; while (!ref.empty()) { std::size_t pos = rng() % ref.size(); long before = al.moves; al.eraseAt(pos); ref.erase(ref.begin() + pos); assert(al.a == ref && al.moves - before == (long)(ref.size() - pos)); } }   // ①
    for (int rep = 0; rep < 300; rep++) { std::size_t n = rng() % 60; ArrayList bulk, single; for (std::size_t i = 0; i < n; i++) { int x = (int)(rng() % 100); bulk.a.push_back(x); single.a.push_back(x); } std::vector<int> ref = bulk.a;       // ②
        std::size_t first = n ? rng() % (n + 1) : 0, last = first + (n - first ? rng() % (n - first + 1) : 0); ref.erase(ref.begin() + first, ref.begin() + last); bulk.eraseRange(first, last); assert(bulk.a == ref && bulk.moves == (long)(n - last));
        long k = (long)(last - first); for (std::size_t j = first; j < last; j++) single.eraseAt(first); assert(single.a == ref && single.moves == (long)(k * (n - first) - k * (k + 1) / 2)); }
    { ArrayList u; for (int i = 0; i < 100; i++) u.a.push_back(i); std::vector<int> ref = u.a; std::mt19937 r2(1); while (!u.a.empty()) { std::size_t pos = r2() % u.a.size(); int val = u.a[pos], oldLast = u.a.back(); std::size_t last = u.a.size() - 1; long before = u.moves; assert(u.eraseUnordered(pos) == val && u.moves - before == (pos != last ? 1 : 0) && u.a.size() == last); if (pos != last) assert(u.a[pos] == oldLast); ref.erase(std::find(ref.begin(), ref.end(), val)); std::vector<int> x = u.a, y = ref; std::sort(x.begin(), x.end()); std::sort(y.begin(), y.end()); assert(x == y); } }   // ③
    for (int rep = 0; rep < 200; rep++) { ArrayList al; std::size_t n = rng() % 80; for (std::size_t i = 0; i < n; i++) al.a.push_back((int)(rng() % 20)); std::vector<int> ref = al.a; int m = (int)(rng() % 5) + 2;      // ④
        long inspected = al.eraseIf([&](int x) { return x % m == 0; }); ref.erase(std::remove_if(ref.begin(), ref.end(), [&](int x) { return x % m == 0; }), ref.end()); assert(al.a == ref && inspected == (long)n && al.moves <= (long)n); }
    { ArrayList al; al.a = {1, 2, 3}; bool threw = false; try { al.eraseAt(3); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; try { al.eraseRange(2, 1); } catch (const std::out_of_range&) { threw = true; } assert(threw);   // ⑤
      threw = false; try { al.eraseRange(0, 4); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; try { al.eraseUnordered(5); } catch (const std::out_of_range&) { threw = true; } assert(threw && al.a == (std::vector<int>{1, 2, 3}));
      al.eraseRange(1, 1); assert(al.a.size() == 3); al.eraseRange(0, 3); assert(al.a.empty()); }
    { ArrayList al; for (int i = 0; i < 1000; i++) al.a.push_back(i); std::size_t cap = al.a.capacity(); al.eraseRange(10, 990); assert(al.a.size() == 20 && al.a.capacity() == cap); }       // ⑥ 용량 유지
    std::cout << "DeleteAt: positional erase moved exactly n-pos-1 elements, range erase moved n-last once instead of k(n-first)-k(k+1)/2 when erasing one at a time, unordered erase moved only the last element into the hole (one move, none when the last element itself was removed), conditional erase inspected each element once, and invalid ranges threw without modifying the array" << std::endl; return 0;
}
// Time Complexity: 단일 O(N−pos), 구간 O(N−last), 순서 무관 O(1), 조건 삭제 O(N)
// Space Complexity: O(1)
```
## BinarySearch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 이진 탐색(Binary Search): 정렬된 배열에서 가운데를 비교해 후보 구간을 절반씩 줄인다. n 개에서 최대 ⌊log₂ n⌋ + 1 번 반복한다(10 억 개도 30 번). 구간은 반열린 [lo, hi) 로 두면 경계 처리가 단순하다. 중간값은 lo + (hi − lo) / 2 로 계산해야 한다 — (lo + hi) / 2 는 lo + hi 가 정수 범위를 넘을 때 음수나 엉뚱한 값이 된다(32 비트에서 인덱스가 10 억을 넘으면 발생).
// 같은 값이 여럿이면 어느 것이 반환될지 정해져 있지 않다(첫 번째가 필요하면 LowerBound). 이진 탐색은 배열 위에서만이 아니라 "참/거짓이 한 번만 바뀌는" 모든 단조 조건 위에서 쓸 수 있다: 정수 제곱근, 해의 범위 찾기 등. 목표가 앞쪽에 가까울 때는 구간을 1, 2, 4, … 로 두 배씩 늘려 상한을 찾은 뒤 이진 탐색하는 지수 탐색(galloping)이 i 번째를 O(log i) 에 찾는다. 회전된 정렬 배열에서도 한쪽 절반은 항상 정렬되어 있다는 성질로 O(log n) 에 찾는다.
// 검증: ① 모든 n ≤ 64 와 모든 키(-1..n+1, 중복 포함)에서 std::binary_search 와 같고 반환 인덱스의 값이 키이며 반복 수 ≤ ⌊log₂ n⌋+1 (재귀 구현도 동일) ② 중간값 오버플로 함정: 32 비트 부호 없는 합이 넘쳐 틀린 값이 되지만 lo+(hi−lo)/2 는 맞음 ③ 단조 조건 위의 탐색: 정수 제곱근이 모든 64 비트 입력에서 정확(완전제곱수 ±1 포함), 반복 ≤ 64 ④ 지수 탐색이 모든 위치에서 비용 ≤ 2⌈log₂(i+2)⌉+2 ⑤ 회전 배열 탐색이 선형 탐색과 같음.
long binarySearch(const std::vector<int>& a, int key, int& iterations) {
    std::size_t lo = 0, hi = a.size(); iterations = 0; while (lo < hi) { iterations++; std::size_t mid = lo + (hi - lo) / 2; if (a[mid] == key) return (long)mid; if (a[mid] < key) lo = mid + 1; else hi = mid; } return -1; }
long binarySearchRec(const std::vector<int>& a, int key, std::size_t lo, std::size_t hi, int& iterations) { if (lo >= hi) return -1; iterations++; std::size_t mid = lo + (hi - lo) / 2;
    if (a[mid] == key) return (long)mid; return a[mid] < key ? binarySearchRec(a, key, mid + 1, hi, iterations) : binarySearchRec(a, key, lo, mid, iterations); }
uint64_t isqrt(uint64_t x) { uint64_t lo = 0, hi = std::min<uint64_t>(x, 4294967295ull) + 1; int iters = 0; while (lo + 1 < hi) { uint64_t mid = lo + (hi - lo) / 2; iters++; if (mid <= x / mid) lo = mid; else hi = mid; } assert(iters <= 64); return lo; }   // 가장 큰 r: r·r ≤ x (곱 대신 나눗셈)
bool isFloorSqrt(uint64_t x, uint64_t r) { return (r == 0 ? x < 1 : r <= x / r) && (r + 1 > x / (r + 1)); }                    // r·r ≤ x < (r+1)² 를 나눗셈으로 검사(오버플로 없음)
long gallop(const std::vector<int>& a, int key, long& cost) { cost = 0; std::size_t bound = 1; if (a.empty()) return -1; cost++; if (a[0] == key) return 0; while (bound < a.size() && a[bound] < key) { cost++; bound *= 2; }
    std::size_t lo = bound / 2, hi = std::min(bound + 1, a.size()); while (lo < hi) { cost++; std::size_t mid = lo + (hi - lo) / 2; if (a[mid] == key) return (long)mid; if (a[mid] < key) lo = mid + 1; else hi = mid; } return -1; }
long searchRotated(const std::vector<int>& a, int key) { long lo = 0, hi = (long)a.size() - 1; while (lo <= hi) { long mid = lo + (hi - lo) / 2; if (a[mid] == key) return mid;
        if (a[lo] <= a[mid]) { if (a[lo] <= key && key < a[mid]) hi = mid - 1; else lo = mid + 1; } else { if (a[mid] < key && key <= a[hi]) lo = mid + 1; else hi = mid - 1; } } return -1; }
int main() {
    std::mt19937 rng(17);
    for (int n = 0; n <= 64; n++) for (int rep = 0; rep < 3; rep++) { std::vector<int> a(n); for (int& x : a) x = (int)(rng() % (n + 2)); std::sort(a.begin(), a.end());                                  // ①
        for (int key = -1; key <= n + 2; key++) { int it = 0, it2 = 0; long p = binarySearch(a, key, it), q = binarySearchRec(a, key, 0, a.size(), it2); bool want = std::binary_search(a.begin(), a.end(), key);
            assert((p >= 0) == want && (q >= 0) == want && it == it2); if (p >= 0) assert(a[p] == key && a[q] == key); int bound = n ? (int)std::floor(std::log2((double)n)) + 1 : 0; assert(it <= bound); } }
    { uint32_t lo = 3000000000u, hi = 3100000000u; uint32_t bad = (lo + hi) / 2, good = lo + (hi - lo) / 2; assert(good == 3050000000u && bad != good && bad < lo); }                       // ② (lo+hi) 가 32 비트를 넘쳐 mid 가 구간 밖
    for (uint64_t x : {0ull, 1ull, 2ull, 3ull, 4ull, 15ull, 16ull, 17ull, 4294967295ull, 4294967296ull, 18446744073709551615ull, 18446744065119617025ull, 18446744065119617024ull}) { assert(isFloorSqrt(x, isqrt(x))); }
    { std::mt19937_64 r64(5); for (int i = 0; i < 20000; i++) { uint64_t x = r64() >> (r64() % 64); assert(isFloorSqrt(x, isqrt(x))); uint64_t s = r64() >> 33; uint64_t sq = s * s; assert(isqrt(sq) == s && isqrt(sq + (s ? 1 : 0)) == s && (s ? isqrt(sq - 1) == s - 1 : true)); } }   // ③
    { std::vector<int> a(5000); std::iota(a.begin(), a.end(), 0); for (int i = 0; i < 5000; i += 7) { long cost; assert(gallop(a, i, cost) == i); assert(cost <= 2 * (long)std::ceil(std::log2((double)(i + 2))) + 2); } long c; assert(gallop(a, -5, c) == -1 && gallop(a, 99999, c) == -1); std::vector<int> e; assert(gallop(e, 1, c) == -1); }   // ④
    for (int n = 0; n <= 30; n++) for (int rot = 0; rot <= n; rot++) { std::vector<int> a(n); for (int i = 0; i < n; i++) a[i] = i * 3; std::rotate(a.begin(), a.begin() + (rot % (n ? n : 1)), a.end());           // ⑤ 회전 배열
        for (int key = -2; key <= 3 * n + 2; key++) { long want = -1; for (int i = 0; i < n; i++) if (a[i] == key) want = i; assert(searchRotated(a, key) == want); } }
    std::cout << "BinarySearch: iterative and recursive searches matched std::binary_search for every n<=64 with duplicates in at most floor(log2 n)+1 iterations; the (lo+hi)/2 overflow was demonstrated, integer sqrt by monotone-predicate search was exact for 20000 random 64-bit inputs and perfect-square neighbours, galloping cost O(log i), and rotated-array search matched linear scan" << std::endl; return 0;
}
// Time Complexity: O(log N)
// Space Complexity: 반복 O(1), 재귀 O(log N)
```
## LowerBound()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <functional>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 하한(LowerBound): 정렬된 배열에서 키 이상인 첫 위치(없으면 n)를 찾는다. 같은 키가 여럿이면 그 중 가장 앞이다. 이 위치는 "키보다 작은 원소의 개수"이기도 하고, 키를 넣어도 정렬이 유지되는 가장 앞쪽 삽입 위치(같은 값들의 앞)다. 구현은 반열린 구간 [lo, hi) 에서 a[mid] < key 면 lo = mid+1, 아니면 hi = mid 로 줄여 가는 한 가지 형태면 충분하다(일치해도 멈추지 않고 왼쪽을 계속 찾는다).
// 분기를 없앤 변형: len 을 절반씩 줄이며 base 를 조건부로 옮기면 키와 데이터에 상관없이 비교 횟수가 항상 ⌈log₂ n⌉ + 1 로 고정되고 분기 예측 실패가 없어 빠르다. 비교자를 바꾸면 내림차순 배열, 구조체의 한 필드 기준 탐색에도 같은 코드를 쓴다 — 핵심은 "false…false true…true" 로 한 번만 바뀌는 술어(partition point)다.
// 검증: ① 모든 n ≤ 40(중복 포함)과 모든 키에서 std::lower_bound 와 같고, 앞은 모두 < 키, 뒤는 모두 ≥ 키, 결과 == 키보다 작은 원소 수 ② 분기 없는 변형이 같은 결과이고 비교 횟수가 항상 ⌈log₂ n⌉+1 (n ≥ 1) ③ 비교자 일반화: 내림차순(std::greater), 구조체 필드, 문자열 ④ 하한 위치에 삽입하면 정렬 유지 ⑤ 반복 수는 ⌊log₂ n⌋ 또는 +1.
template <class T, class Less = std::less<T>> std::size_t lowerBound(const std::vector<T>& a, const T& key, int& iters, Less less = Less()) {
    std::size_t lo = 0, hi = a.size(); iters = 0; while (lo < hi) { iters++; std::size_t mid = lo + (hi - lo) / 2; if (less(a[mid], key)) lo = mid + 1; else hi = mid; } return lo; }
std::size_t lowerBoundBranchless(const std::vector<int>& a, int key, int& compares) {
    compares = 0; if (a.empty()) return 0; const int* base = a.data(); std::size_t len = a.size();
    while (len > 1) { std::size_t half = len / 2; compares++; base = (base[half - 1] < key) ? base + half : base; len -= half; } compares++; return (std::size_t)(base - a.data()) + (*base < key); }
template <class It, class Pred> It partitionPoint(It first, It last, Pred p) { std::size_t len = (std::size_t)(last - first); while (len > 0) { std::size_t half = len / 2; It mid = first + half; if (p(*mid)) { first = mid + 1; len -= half + 1; } else len = half; } return first; }
struct Rec { int key; std::string name; };
int main() {
    std::mt19937 rng(18);
    for (int n = 0; n <= 40; n++) for (int rep = 0; rep < 4; rep++) { std::vector<int> a(n); for (int& x : a) x = (int)(rng() % (n / 2 + 2)); std::sort(a.begin(), a.end());                                        // ①
        for (int key = -1; key <= n / 2 + 3; key++) { int it = 0, cmp = 0; std::size_t p = lowerBound(a, key, it), q = lowerBoundBranchless(a, key, cmp); std::size_t want = std::lower_bound(a.begin(), a.end(), key) - a.begin();
            assert(p == want && q == want); for (std::size_t i = 0; i < p; i++) assert(a[i] < key); for (std::size_t i = p; i < a.size(); i++) assert(a[i] >= key); assert((long)p == std::count_if(a.begin(), a.end(), [&](int x) { return x < key; }));
            if (n) { int fl = (int)std::floor(std::log2((double)n)); assert(it >= fl && it <= fl + 1 && cmp == (int)std::ceil(std::log2((double)n)) + 1); } } }                                // ②⑤
    { std::vector<int> d = {9, 7, 7, 5, 3, 3, 1}; int it; assert(lowerBound(d, 7, it, std::greater<int>()) == 1 && lowerBound(d, 8, it, std::greater<int>()) == 1 && lowerBound(d, 3, it, std::greater<int>()) == 4 && lowerBound(d, 0, it, std::greater<int>()) == 7 && lowerBound(d, 10, it, std::greater<int>()) == 0);   // ③
      std::vector<Rec> recs = {{1, "a"}, {3, "b"}, {3, "c"}, {5, "d"}, {8, "e"}}; auto byKey = [](const Rec& r, const Rec& k) { return r.key < k.key; }; assert(lowerBound(recs, Rec{3, ""}, it, byKey) == 1 && lowerBound(recs, Rec{4, ""}, it, byKey) == 3 && lowerBound(recs, Rec{9, ""}, it, byKey) == 5);
      std::vector<std::string> w = {"apple", "banana", "banana", "cherry"}; assert(lowerBound(w, std::string("banana"), it) == 1 && lowerBound(w, std::string("b"), it) == 1 && lowerBound(w, std::string("d"), it) == 4);
      std::vector<int> a = {1, 2, 4, 4, 6, 9}; assert(partitionPoint(a.begin(), a.end(), [](int x) { return x < 4; }) - a.begin() == 2 && partitionPoint(a.begin(), a.end(), [](int) { return true; }) == a.end() && partitionPoint(a.begin(), a.end(), [](int) { return false; }) == a.begin()); }
    { std::vector<int> a; for (int i = 0; i < 500; i++) { int v = (int)(rng() % 100); int it; a.insert(a.begin() + lowerBound(a, v, it), v); } assert(std::is_sorted(a.begin(), a.end()) && a.size() == 500); }            // ④ 정렬 유지 삽입
    { std::vector<int> e; int it, cmp; assert(lowerBound(e, 5, it) == 0 && it == 0 && lowerBoundBranchless(e, 5, cmp) == 0); std::vector<int> one = {5}; assert(lowerBound(one, 5, it) == 0 && lowerBound(one, 6, it) == 1 && lowerBound(one, 4, it) == 0 && lowerBoundBranchless(one, 6, cmp) == 1 && cmp == 1); }
    std::cout << "LowerBound: results equalled std::lower_bound and the count of smaller elements for every n<=40 with duplicates; the branchless form always used exactly ceil(log2 n)+1 comparisons; descending order, record fields and strings worked through the same predicate; sorted insertion at the lower bound stayed sorted" << std::endl; return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## UpperBound()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <functional>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// 상한(UpperBound): 정렬된 배열에서 키보다 큰 첫 위치(없으면 n)를 찾는다. 키와 같은 원소들의 바로 뒤다. 하한과 한 쌍으로 쓰인다: [lower_bound, upper_bound) 는 키와 같은 원소의 구간(equal_range)이고 그 길이가 개수다 — 같은 값을 세는 것이 O(n) 이 아니라 O(log n) 이 된다. 정수에서는 upper(k) == lower(k+1) 이다.
// 활용: 구간 개수 질의 count(lo ≤ x ≤ hi) = upper(hi) − lower(lo); 바닥(floor, 키 이하의 최댓값) = upper(k) − 1, 천장(ceil, 키 이상의 최솟값) = lower(k); 가장 가까운 값 찾기; 같은 키의 뒤에 넣어 안정적으로 삽입하기(먼저 들어온 같은 키가 앞에 남는다). 구현은 a[mid] ≤ key(= !(key < a[mid])) 이면 lo = mid+1, 아니면 hi = mid 로 줄이는 한 가지 형태다.
// 검증: ① n = 0..40 각각에 대해 무작위 정렬 배열 4 개(중복 포함)와 그 값 범위 주변의 모든 키에서 std::upper_bound 와 같고, 앞은 모두 ≤ 키, 뒤는 모두 > 키 ② equal_range 길이 == std::count, 정수에서 upper(k) == lower(k+1), 하한 ≤ 상한 ③ 구간 개수 질의 2000 번이 무차별 계산과 같음 ④ floor/ceil/최근접이 무차별 계산과 같음 ⑤ 상한 위치 삽입이 안정적(같은 키의 도착 순서 유지) ⑥ 내림차순 비교자.
template <class T, class Less = std::less<T>> std::size_t upperBound(const std::vector<T>& a, const T& key, Less less = Less()) {
    std::size_t lo = 0, hi = a.size(); while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; if (!less(key, a[mid])) lo = mid + 1; else hi = mid; } return lo; }
template <class T, class Less = std::less<T>> std::size_t lowerBound(const std::vector<T>& a, const T& key, Less less = Less()) {
    std::size_t lo = 0, hi = a.size(); while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; if (less(a[mid], key)) lo = mid + 1; else hi = mid; } return lo; }
struct Item { int key, order; };
int main() {
    std::mt19937 rng(19);
    for (int n = 0; n <= 40; n++) for (int rep = 0; rep < 4; rep++) { std::vector<int> a(n); for (int& x : a) x = (int)(rng() % (n / 2 + 2)); std::sort(a.begin(), a.end());                                        // ①②
        for (int key = -1; key <= n / 2 + 3; key++) { std::size_t u = upperBound(a, key), l = lowerBound(a, key); assert(u == (std::size_t)(std::upper_bound(a.begin(), a.end(), key) - a.begin()));
            for (std::size_t i = 0; i < u; i++) assert(a[i] <= key); for (std::size_t i = u; i < a.size(); i++) assert(a[i] > key);
            assert(l <= u && (long)(u - l) == std::count(a.begin(), a.end(), key) && u == lowerBound(a, key + 1)); auto er = std::equal_range(a.begin(), a.end(), key); assert((std::size_t)(er.first - a.begin()) == l && (std::size_t)(er.second - a.begin()) == u); } }
    { std::vector<int> a(3000); for (int& x : a) x = (int)(rng() % 500); std::sort(a.begin(), a.end()); for (int q = 0; q < 2000; q++) { int lo = (int)(rng() % 600) - 50, hi = (int)(rng() % 600) - 50; if (lo > hi) std::swap(lo, hi);   // ③
          long got = (long)upperBound(a, hi) - (long)lowerBound(a, lo), want = 0; for (int x : a) want += (x >= lo && x <= hi); assert(got == want); } }
    { std::vector<int> a(800); for (int& x : a) x = (int)(rng() % 1000) * 2; std::sort(a.begin(), a.end()); for (int q = 0; q < 1500; q++) { int key = (int)(rng() % 2100) - 50;                                       // ④
          std::size_t u = upperBound(a, key), l = lowerBound(a, key); bool hasFloor = u > 0, hasCeil = l < a.size(); int bfFloor = -1, bfCeil = -1; for (int x : a) { if (x <= key && (bfFloor < 0 || x > bfFloor)) bfFloor = x; if (x >= key && (bfCeil < 0 || x < bfCeil)) bfCeil = x; }
          assert(hasFloor == (bfFloor >= 0) && (!hasFloor || a[u - 1] == bfFloor) && hasCeil == (bfCeil >= 0) && (!hasCeil || a[l] == bfCeil));
          if (hasFloor && hasCeil) { int d1 = key - a[u - 1], d2 = a[l] - key; int nearest = d1 <= d2 ? a[u - 1] : a[l]; int best = 1 << 30, bestVal = 0; for (int x : a) { int d = std::abs(x - key); if (d < best || (d == best && x < bestVal)) { best = d; bestVal = x; } } assert(std::abs(nearest - key) == best); } } }
    { std::vector<Item> v; for (int i = 0; i < 600; i++) { Item x{(int)(rng() % 8), i}; std::size_t pos = upperBound(v, x, [](const Item& p, const Item& q) { return p.key < q.key; }); v.insert(v.begin() + pos, x); }  // ⑤ 안정적 삽입
      for (std::size_t i = 1; i < v.size(); i++) assert(v[i - 1].key < v[i].key || (v[i - 1].key == v[i].key && v[i - 1].order < v[i].order)); }
    { std::vector<int> d = {9, 7, 7, 5, 3, 3, 1}; assert(upperBound(d, 7, std::greater<int>()) == 3 && upperBound(d, 8, std::greater<int>()) == 1 && upperBound(d, 3, std::greater<int>()) == 6 && upperBound(d, 0, std::greater<int>()) == 7 && upperBound(d, 10, std::greater<int>()) == 0);   // ⑥
      std::vector<int> e; assert(upperBound(e, 1) == 0 && lowerBound(e, 1) == 0); }
    std::cout << "UpperBound: results equalled std::upper_bound for 4 random sorted arrays with duplicates at every length n<=40 and every key around their value range; [lower, upper) gave the occurrence count in O(log n); range-count, floor, ceil and nearest-value queries matched brute force; insertion at the upper bound was stable" << std::endl; return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```

# Part 3. 연결 리스트
## PushFront()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <iostream>
#include <list>
#include <new>
#include <random>
#include <stack>
#include <vector>

// 앞에 넣기(PushFront): 새 노드를 만들어 next 가 현재 head 를 가리키게 하고 head 를 새 노드로 바꾼다. 포인터 두 개만 건드리므로 리스트 길이와 무관한 O(1) 이다. 순서가 중요하다: 새 노드를 먼저 완성(next = head)하고 나서 head 를 바꿔야 한다. 반대로 하면 기존 노드로 가는 길을 잃는다. 노드 할당이 실패(예외)해도 head 는 아직 바뀌지 않았으므로 리스트는 그대로다(강한 예외 보장).
// 빈 리스트에 처음 넣는 노드는 head 이면서 동시에 tail 이다 — 꼬리 포인터를 유지하는 리스트라면 이 경우만 따로 설정해야 한다. 앞에 계속 넣으면 넣은 순서와 반대 순서로 저장되고, 앞에 넣기 + 앞에서 빼기는 그대로 스택(LIFO)이다.
// 검증: ① 무작위 push_front 가 std::list 와 같음(순서 뒤집힘 포함), 길이·살아 있는 노드 수 일치 ② 첫 삽입에서 head == tail, 이후 tail 불변 ③ 순회 걸음 0 (O(1)) ④ 할당 실패가 어느 시점에 나도 리스트 불변 ⑤ 앞에 넣기 + 앞에서 빼기 == std::stack.
struct Node { int val; Node* next; static int live, failAt; Node(int v, Node* nx) : val(v), next(nx) { if (failAt >= 0 && live >= failAt) throw std::bad_alloc(); ++live; } ~Node() { --live; } };
int Node::live = 0, Node::failAt = -1;
class SList { Node *head_ = nullptr, *tail_ = nullptr; std::size_t n_ = 0;
public:
    long hops = 0; ~SList() { while (head_) { Node* nx = head_->next; delete head_; head_ = nx; } }
    void pushFront(int v) { Node* x = new Node(v, head_); head_ = x; if (!tail_) tail_ = x; n_++; }                  // 할당(예외 가능) → 연결 → head 교체
    bool popFront(int& out) { if (!head_) return false; Node* dead = head_; out = dead->val; head_ = dead->next; if (!head_) tail_ = nullptr; delete dead; n_--; return true; }
    std::size_t size() const { return n_; } const Node* head() const { return head_; } const Node* tail() const { return tail_; }
    std::vector<int> items() const { std::vector<int> r; for (const Node* c = head_; c; c = c->next) r.push_back(c->val); return r; } };
int main() {
    std::mt19937 rng(20);
    { SList l; std::list<int> ref; for (int i = 0; i < 2000; i++) { int v = (int)rng(); l.pushFront(v); ref.push_front(v); assert(l.size() == ref.size() && l.head()->val == ref.front() && (int)l.size() == Node::live); }   // ①
      assert(l.items() == std::vector<int>(ref.begin(), ref.end())); assert(l.hops == 0); }                                                                                                              // ③
    assert(Node::live == 0);
    { SList l; l.pushFront(1); assert(l.head() == l.tail() && l.head()->next == nullptr); const Node* firstNode = l.head(); l.pushFront(2); l.pushFront(3); assert(l.tail() == firstNode && l.head()->val == 3 && l.items() == (std::vector<int>{3, 2, 1})); }   // ②
    for (int n = 0; n <= 6; n++) { SList l; for (int i = 0; i < n; i++) l.pushFront(i); Node::failAt = Node::live; bool threw = false; std::vector<int> before = l.items(); const Node *h = l.head(), *t = l.tail();       // ④ 다음 할당이 실패하도록
        try { l.pushFront(99); } catch (const std::bad_alloc&) { threw = true; } assert(threw && l.items() == before && l.size() == (std::size_t)n && l.head() == h && l.tail() == t); Node::failAt = -1; }
    assert(Node::live == 0);
    { SList l; std::stack<int> st; for (int step = 0; step < 5000; step++) { if (rng() % 3) { int v = (int)(rng() % 100); l.pushFront(v); st.push(v); } else { int out = -1; bool ok = l.popFront(out); assert(ok == !st.empty()); if (ok) { assert(out == st.top()); st.pop(); } } assert(l.size() == st.size()); } }   // ⑤
    assert(Node::live == 0); std::cout << "PushFront: 2000 insertions matched std::list::push_front with zero traversal hops; the first node became head and tail and the tail never moved afterwards; allocation failure left head, size and contents untouched; push-front plus pop-front behaved exactly like std::stack" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) (노드 하나)
```
## PushBack()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <iostream>
#include <new>
#include <queue>
#include <random>
#include <vector>

// 뒤에 넣기(PushBack): 리스트의 끝에 새 노드를 붙인다. 꼬리 포인터(tail)가 없으면 head 부터 끝까지 걸어가야 하므로 O(n) 이고, n 개를 차례로 넣으면 (n−1)(n−2)/2 걸음(≈ n²/2)이 든다. 꼬리 포인터를 유지하면 `tail->next = 새 노드; tail = 새 노드` 로 O(1) 이다.
// 꼬리 포인터는 해야 할 일이 하나 더 있다. 빈 리스트에 넣을 때는 tail 이 없으므로 head 와 tail 을 함께 설정해야 하고, 반대로 앞에서 빼다가 리스트가 비면 tail 도 nullptr 로 되돌려야 한다 — 이것을 잊으면 다음 PushBack 이 해제된 노드에 쓴다(가장 흔한 버그). 뒤에 넣기 + 앞에서 빼기는 큐(FIFO)다.
// 검증: ① 꼬리 포인터 방식은 n 개 삽입에 걸음 0, 꼬리 없는 방식은 정확히 (n−1)(n−2)/2 걸음(첫 삽입은 걷지 않고 둘째는 head 바로 뒤에 붙으므로) ② 무작위 push_back/pop_front 가 std::queue 와 같음(비었다 다시 채우는 경우 포함) ③ 빈 리스트가 될 때마다 head, tail 모두 nullptr ④ 할당 실패 시 리스트 불변 ⑤ 두 방식의 결과 순서가 같음.
struct Node { int val; Node* next; static int live, failAt; Node(int v) : val(v), next(nullptr) { if (failAt >= 0 && live >= failAt) throw std::bad_alloc(); ++live; } ~Node() { --live; } };
int Node::live = 0, Node::failAt = -1;
class SListNoTail { Node* head_ = nullptr; public: long hops = 0; ~SListNoTail() { while (head_) { Node* nx = head_->next; delete head_; head_ = nx; } }
    void pushBack(int v) { Node* x = new Node(v); if (!head_) { head_ = x; return; } Node* c = head_; while (c->next) { c = c->next; hops++; } c->next = x; }
    std::vector<int> items() const { std::vector<int> r; for (Node* c = head_; c; c = c->next) r.push_back(c->val); return r; } };
class SList { Node *head_ = nullptr, *tail_ = nullptr; std::size_t n_ = 0;
public:
    ~SList() { while (head_) { Node* nx = head_->next; delete head_; head_ = nx; } }
    void pushBack(int v) { Node* x = new Node(v); if (tail_) tail_->next = x; else head_ = x; tail_ = x; n_++; }       // 빈 리스트면 head 도 설정
    bool popFront(int& out) { if (!head_) return false; Node* dead = head_; out = dead->val; head_ = dead->next; if (!head_) tail_ = nullptr; delete dead; n_--; return true; }   // 비면 tail 도 초기화
    std::size_t size() const { return n_; } const Node* head() const { return head_; } const Node* tail() const { return tail_; }
    std::vector<int> items() const { std::vector<int> r; for (Node* c = head_; c; c = c->next) r.push_back(c->val); return r; } };
int main() {
    std::mt19937 rng(21);
    for (int n : {0, 1, 2, 3, 10, 200}) { SList a; SListNoTail b; for (int i = 0; i < n; i++) { a.pushBack(i); b.pushBack(i); } long want = n >= 2 ? (long)(n - 1) * (n - 2) / 2 : 0; assert(b.hops == want && a.items() == b.items() && (int)a.size() == n);   // ① ⑤
        if (n) assert(a.tail()->val == n - 1 && a.tail()->next == nullptr); else assert(a.head() == nullptr && a.tail() == nullptr); }
    assert(Node::live == 0);
    { SList l; std::queue<int> q; int emptied = 0; for (int step = 0; step < 20000; step++) { if (rng() % 20 < 9) { int v = (int)(rng() % 1000); l.pushBack(v); q.push(v); } else { int out = -1; bool ok = l.popFront(out); assert(ok == !q.empty()); if (ok) { assert(out == q.front()); q.pop(); } }   // ②
          assert(l.size() == q.size() && (int)l.size() == Node::live); if (q.empty()) { assert(l.head() == nullptr && l.tail() == nullptr); emptied++; } else assert(l.tail()->val == q.back() && l.head()->val == q.front()); } assert(emptied > 100); }                                   // ③
    assert(Node::live == 0);
    for (int n = 0; n <= 6; n++) { SList l; for (int i = 0; i < n; i++) l.pushBack(i); Node::failAt = Node::live; std::vector<int> before = l.items(); const Node *h = l.head(), *t = l.tail(); bool threw = false;      // ④ 다음 할당이 실패하도록
        try { l.pushBack(99); } catch (const std::bad_alloc&) { threw = true; } assert(threw && l.items() == before && l.head() == h && l.tail() == t && l.size() == (std::size_t)n && (!t || t->next == nullptr)); Node::failAt = -1; }
    assert(Node::live == 0); std::cout << "PushBack: with a tail pointer n insertions needed no traversal while the tail-less list walked exactly (n-1)(n-2)/2 hops; 20000 random push_back/pop_front operations matched std::queue including emptying and refilling (head and tail were both reset to null each time); allocation failure left the list untouched" << std::endl; return 0;
}
// Time Complexity: 꼬리 포인터 O(1), 꼬리 없음 O(N)
// Space Complexity: O(1)
```
## PopFront()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 앞에서 빼기(PopFront): head 노드를 떼어 내고 head 를 다음 노드로 옮긴 뒤 노드를 해제한다. O(1) 이다. 해제하기 전에 값과 다음 포인터를 먼저 꺼내 두어야 한다(해제한 노드를 읽으면 안 된다). 리스트가 비어 있으면 뺄 것이 없다 — 오류(예외)로 알리거나, 이 코드처럼 실패를 반환값(false)으로 알린다.
// 마지막 노드를 빼서 리스트가 비면 꼬리 포인터도 nullptr 로 되돌려야 한다. 값이 문자열 같은 무거운 객체이면 복사 대신 이동으로 꺼내야 불필요한 할당을 피한다. 뒤에 넣기 + 앞에서 빼기가 큐(FIFO), 앞에 넣기 + 앞에서 빼기가 스택(LIFO)이다.
// 검증: ① 무작위 pop_front 가 std::queue 와 같은 순서(FIFO) ② 빈 리스트에서는 false 이고 아무것도 변하지 않음 ③ 마지막 하나를 빼면 head, tail 모두 nullptr ④ 모든 빼기에서 노드가 정확히 하나씩 해제(누수·이중 해제 없음) ⑤ 문자열 값은 복사 없이 이동으로 나옴 ⑥ 걸음 0 (O(1)).
template <class T> struct Node { T val; Node* next; Node(T v, Node* nx) : val(std::move(v)), next(nx) { ++live; } ~Node() { --live; } static int live; }; template <class T> int Node<T>::live = 0;
struct Probe { int v; static int copies, moves; Probe(int x = 0) : v(x) {} Probe(const Probe& o) : v(o.v) { copies++; } Probe(Probe&& o) noexcept : v(o.v) { moves++; } Probe& operator=(Probe&&) = default; Probe& operator=(const Probe&) = default; }; int Probe::copies = 0, Probe::moves = 0;
template <class T> class SList { Node<T> *head_ = nullptr, *tail_ = nullptr; std::size_t n_ = 0;
public:
    ~SList() { while (head_) { Node<T>* nx = head_->next; delete head_; head_ = nx; } }
    void pushBack(T v) { Node<T>* x = new Node<T>(std::move(v), nullptr); if (tail_) tail_->next = x; else head_ = x; tail_ = x; n_++; }
    bool popFront(T& out) { if (!head_) return false; Node<T>* dead = head_; out = std::move(dead->val); head_ = dead->next; if (!head_) tail_ = nullptr; delete dead; n_--; return true; }   // 값·다음 포인터를 먼저 꺼낸 뒤 해제
    std::size_t size() const { return n_; } const Node<T>* head() const { return head_; } const Node<T>* tail() const { return tail_; } };
int main() {
    std::mt19937 rng(22);
    { SList<int> l; std::queue<int> q; for (int step = 0; step < 30000; step++) { if (rng() % 5 < 2) { int v = (int)rng(); l.pushBack(v); q.push(v); } else { int out = -7; bool ok = l.popFront(out); assert(ok == !q.empty());   // ①②
          if (ok) { assert(out == q.front()); q.pop(); } else assert(out == -7 && l.head() == nullptr && l.tail() == nullptr); } assert(l.size() == q.size() && (int)l.size() == Node<int>::live); } }
    assert(Node<int>::live == 0);
    { SList<int> l; int out; for (int i = 0; i < 4; i++) l.pushBack(i); for (int i = 0; i < 3; i++) assert(l.popFront(out) && out == i && l.tail() != nullptr); assert(l.head() == l.tail() && l.head()->val == 3);                      // ③
      assert(l.popFront(out) && out == 3 && l.head() == nullptr && l.tail() == nullptr && l.size() == 0 && !l.popFront(out)); l.pushBack(9); assert(l.head() == l.tail() && l.head()->val == 9); }
    assert(Node<int>::live == 0);
    { SList<std::string> l; std::string big(200, 'x'); l.pushBack(big); std::string out; assert(l.popFront(out) && out == big && Node<std::string>::live == 0); }                           // ④ ⑤ 문자열
    { SList<Probe> l; for (int i = 0; i < 10; i++) l.pushBack(Probe(i)); Probe::copies = Probe::moves = 0; Probe out; for (int i = 0; i < 10; i++) { assert(l.popFront(out) && out.v == i); } assert(Probe::copies == 0 && Probe::moves == 0); }          // 복사 0, 이동 대입은 생성자 카운트 없음
    assert(Node<std::string>::live == 0 && Node<Probe>::live == 0); std::cout << "PopFront: 30000 random operations matched std::queue FIFO order; popping from an empty list returned false and changed nothing; removing the last node reset both head and tail; every pop freed exactly one node, and values were moved out without copies" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PopBack()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <deque>
#include <iostream>
#include <random>
#include <vector>

// 뒤에서 빼기(PopBack): 마지막 노드를 떼어 낸다. 단방향 연결 리스트에서는 tail 이 있어도 tail 의 앞 노드를 알 수 없어서 head 부터 걸어 tail 의 앞 노드를 찾아야 하므로 O(n) 이다(걸음 n−2). 새 tail 은 그 앞 노드이고 그 next 를 nullptr 로 만든다. 양방향 연결 리스트는 tail->prev 로 바로 알 수 있어 O(1) 이다.
// 단방향으로 n 개를 뒤에서부터 모두 빼면 걸음이 (n−1)(n−2)/2 로 이차 시간이 되고 양방향은 0 이다 — 뒤에서 빼는 일이 잦다면 양방향을 선택하는 이유다. 노드가 하나뿐일 때(head == tail)는 따로 처리해 head 와 tail 을 모두 nullptr 로 만든다.
// 검증: ① 단방향·양방향 모두 무작위 push_back/pop_back 이 std::deque 와 같음 ② 단방향의 걸음이 정확히 n−2 (n ≥ 2), 하나일 때 0 ③ n 개를 모두 빼는 총 걸음 (n−1)(n−2)/2 vs 양방향 0 ④ 하나 남은 노드를 빼면 head, tail 모두 nullptr ⑤ 빈 리스트에서 실패 반환, 누수 없음.
struct SNode { int val; SNode* next; static int live; SNode(int v) : val(v), next(nullptr) { ++live; } ~SNode() { --live; } }; int SNode::live = 0;
struct DNode { int val; DNode *next, *prev; static int live; DNode(int v) : val(v), next(nullptr), prev(nullptr) { ++live; } ~DNode() { --live; } }; int DNode::live = 0;
class SList { SNode *head_ = nullptr, *tail_ = nullptr; std::size_t n_ = 0;
public:
    long hops = 0; ~SList() { while (head_) { SNode* nx = head_->next; delete head_; head_ = nx; } }
    void pushBack(int v) { SNode* x = new SNode(v); if (tail_) tail_->next = x; else head_ = x; tail_ = x; n_++; }
    bool popBack(int& out) { if (!head_) return false; out = tail_->val;
        if (head_ == tail_) { delete head_; head_ = tail_ = nullptr; } else { SNode* c = head_; while (c->next != tail_) { c = c->next; hops++; } delete tail_; c->next = nullptr; tail_ = c; } n_--; return true; }
    std::size_t size() const { return n_; } const SNode* head() const { return head_; } const SNode* tail() const { return tail_; } };
class DList { DNode *head_ = nullptr, *tail_ = nullptr; std::size_t n_ = 0;
public:
    long hops = 0; ~DList() { while (head_) { DNode* nx = head_->next; delete head_; head_ = nx; } }
    void pushBack(int v) { DNode* x = new DNode(v); x->prev = tail_; if (tail_) tail_->next = x; else head_ = x; tail_ = x; n_++; }
    bool popBack(int& out) { if (!tail_) return false; out = tail_->val; DNode* dead = tail_; tail_ = dead->prev; if (tail_) tail_->next = nullptr; else head_ = nullptr; delete dead; n_--; return true; }   // prev 로 O(1)
    std::size_t size() const { return n_; } const DNode* head() const { return head_; } const DNode* tail() const { return tail_; } };
int main() {
    std::mt19937 rng(23);
    { SList s; DList d; std::deque<int> ref; for (int step = 0; step < 20000; step++) { if (rng() % 5 < 2) { int v = (int)(rng() % 1000); s.pushBack(v); d.pushBack(v); ref.push_back(v); } else { int a = -1, b = -1; bool ok1 = s.popBack(a), ok2 = d.popBack(b); assert(ok1 == !ref.empty() && ok2 == ok1);   // ① ⑤
          if (ok1) { assert(a == ref.back() && b == ref.back()); ref.pop_back(); } }
          assert(s.size() == ref.size() && d.size() == ref.size() && (int)ref.size() == SNode::live && (int)ref.size() == DNode::live); if (ref.empty()) assert(s.head() == nullptr && s.tail() == nullptr && d.head() == nullptr && d.tail() == nullptr); else assert(s.tail()->val == ref.back() && d.tail()->val == ref.back() && s.tail()->next == nullptr && d.tail()->next == nullptr); }
      assert(d.hops == 0); }
    assert(SNode::live == 0 && DNode::live == 0);
    for (int n : {1, 2, 3, 4, 10, 50}) { SList s; for (int i = 0; i < n; i++) s.pushBack(i); long before = s.hops; int out; s.popBack(out); assert(out == n - 1 && s.hops - before == (n >= 2 ? n - 2 : 0)); }               // ②
    { int n = 300; SList s; DList d; for (int i = 0; i < n; i++) { s.pushBack(i); d.pushBack(i); } int out; for (int i = n - 1; i >= 0; i--) { assert(s.popBack(out) && out == i && d.popBack(out) && out == i); }   // ③
      assert(s.hops == (long)(n - 1) * (n - 2) / 2 && d.hops == 0 && s.head() == nullptr && s.tail() == nullptr && d.head() == nullptr && d.tail() == nullptr); }
    { SList s; s.pushBack(5); int out; assert(s.popBack(out) && out == 5 && s.head() == nullptr && s.tail() == nullptr && s.size() == 0); assert(!s.popBack(out)); s.pushBack(6); assert(s.head() == s.tail() && s.head()->val == 6); DList d; assert(!d.popBack(out)); }   // ④
    assert(SNode::live == 0 && DNode::live == 0); std::cout << "PopBack: 20000 random operations matched std::deque for singly and doubly linked lists; the singly linked pop walked exactly n-2 hops (draining 300 nodes cost 44551 hops) while the doubly linked pop took none; popping the only node reset head and tail" << std::endl; return 0;
}
// Time Complexity: 단방향 O(N), 양방향 O(1)
// Space Complexity: O(1)
```
## InsertAfter()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <new>
#include <random>
#include <utility>
#include <vector>

// 뒤에 끼우기(InsertAfter): 노드 p 가 주어졌을 때 그 바로 뒤에 새 노드를 끼운다. `새 노드->next = p->next; p->next = 새 노드` 두 줄이면 끝나므로 리스트 길이와 무관한 O(1) 이다 — 위치를 찾는 일이 이미 끝났다는 전제다. 순서가 중요하다: 새 노드의 next 를 먼저 설정해야 p 의 기존 뒷부분을 잃지 않는다. 새 노드를 먼저 완성한 뒤 연결하므로 할당 실패 시 리스트는 그대로다.
// p 가 꼬리라면 꼬리 포인터도 새 노드로 갱신해야 한다. 다른 노드를 가리키는 외부 포인터(참조)는 끼워 넣기로 무효가 되지 않는다 — 노드가 옮겨지지 않기 때문이다(배열의 삽입과 다른 연결 리스트의 장점).
// 검증: ① 무작위 노드 뒤에 끼우기를 모델(값 벡터 + 노드 포인터 벡터)과 비교: 순서·길이·꼬리가 일치 ② 처음에 잡아 둔 모든 노드의 포인터-값 대응이 수천 번 끼운 뒤에도 그대로(노드 이동 없음) ③ 꼬리 뒤에 끼우면 꼬리 갱신, 이후 push 가 올바른 위치에 붙음 ④ 할당 실패 시 불변 ⑤ 노드 누수 없음.
struct Node { int val; Node* next; static int live, failAt; Node(int v, Node* nx) : val(v), next(nx) { if (failAt >= 0 && live >= failAt) throw std::bad_alloc(); ++live; } ~Node() { --live; } };
int Node::live = 0, Node::failAt = -1;
class SList { Node *head_ = nullptr, *tail_ = nullptr; std::size_t n_ = 0;
public:
    ~SList() { while (head_) { Node* nx = head_->next; delete head_; head_ = nx; } }
    Node* pushBack(int v) { Node* x = new Node(v, nullptr); if (tail_) tail_->next = x; else head_ = x; tail_ = x; n_++; return x; }
    Node* insertAfter(Node* p, int v) { Node* x = new Node(v, p->next); p->next = x; if (p == tail_) tail_ = x; n_++; return x; }               // 새 노드를 완성한 뒤 연결
    std::size_t size() const { return n_; } const Node* head() const { return head_; } const Node* tail() const { return tail_; }
    std::vector<Node*> nodes() const { std::vector<Node*> r; for (Node* c = head_; c; c = c->next) r.push_back(c); return r; } };
int main() {
    std::mt19937 rng(24);
    { SList l; std::vector<int> val; std::vector<Node*> ptr; for (int i = 0; i < 5; i++) { ptr.push_back(l.pushBack(i)); val.push_back(i); }                           // ①
      std::vector<std::pair<Node*, int>> anchors; for (std::size_t i = 0; i < ptr.size(); i++) anchors.push_back({ptr[i], val[i]});
      for (int step = 0; step < 3000; step++) { std::size_t i = rng() % ptr.size(); int v = (int)(rng() % 1000); Node* x = l.insertAfter(ptr[i], v); ptr.insert(ptr.begin() + i + 1, x); val.insert(val.begin() + i + 1, v);
          assert(l.size() == val.size() && (int)l.size() == Node::live && l.tail() == ptr.back()); }
      std::vector<Node*> nodes = l.nodes(); assert(nodes == ptr); for (std::size_t i = 0; i < nodes.size(); i++) assert(nodes[i]->val == val[i]);
      for (auto& a : anchors) assert(a.first->val == a.second); }                                                                                   // ② 처음 노드들은 한 번도 옮겨지지 않았다
    assert(Node::live == 0);
    { SList l; Node* a = l.pushBack(1); Node* b = l.insertAfter(a, 2); assert(l.tail() == b); Node* c = l.insertAfter(b, 3); assert(l.tail() == c && l.tail()->next == nullptr); l.pushBack(4); Node* d = l.nodes().back(); assert(d->val == 4 && c->next == d && l.tail() == d);          // ③
      std::vector<int> got; for (Node* n : l.nodes()) got.push_back(n->val); assert(got == (std::vector<int>{1, 2, 3, 4})); }
    for (int n = 1; n <= 6; n++) { SList l; Node* last = nullptr; for (int i = 0; i < n; i++) last = l.pushBack(i); Node::failAt = Node::live; std::vector<Node*> before = l.nodes(); bool threw = false;          // ④
        try { l.insertAfter(last, 99); } catch (const std::bad_alloc&) { threw = true; } assert(threw && l.nodes() == before && l.tail() == last && last->next == nullptr && l.size() == (std::size_t)n); Node::failAt = -1; }
    assert(Node::live == 0); std::cout << "InsertAfter: 3000 random insertions after known nodes matched the model sequence, no pre-existing node was ever moved (all anchors kept their values), inserting after the tail updated the tail, and allocation failure left the list unchanged" << std::endl; return 0;   // ⑤
}
// Time Complexity: O(1) (노드를 이미 가지고 있을 때)
// Space Complexity: O(1)
```
## InsertBefore()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <random>
#include <utility>
#include <vector>

// 앞에 끼우기(InsertBefore): 노드 p 의 바로 앞에 끼운다. 단방향 연결 리스트에서는 p 의 앞 노드를 알 수 없다. 방법 셋: (A) head 부터 걸어서 p 를 가리키는 연결을 찾는다 — O(n), 포인터의 포인터를 쓰면 p 가 head 인 경우도 같은 코드. (B) 값 바꿔치기 트릭 — p 뒤에 새 노드를 끼우되 p 의 옛 값을 거기에 옮기고 p 에는 새 값을 쓴다. O(1) 이지만 노드의 정체성이 바뀐다: p 를 가리키던 외부 포인터는 이제 새 값을 보게 되고 옛 원소는 다른 노드에 산다. (C) 양방향 리스트: p->prev 로 O(1), 정체성 유지.
// 외부에서 노드 포인터를 보관하는 구조(예: 해시 맵이 노드를 가리키는 LRU 캐시)에서는 (B) 를 쓰면 안 된다. 노드 안의 데이터가 크거나 복사가 비싸거나 복사할 수 없는 타입일 때도 (B) 는 부적절하다.
// 검증: ① 세 방법이 모두 std::vector::insert 와 같은 값 순서 ② (A)·(C) 는 모든 기존 노드의 포인터-값 대응을 보존하고 (B) 는 대상 노드 하나만 값이 바뀌어 정체성이 달라짐 ③ 걸음 수: (A) 정확히 위치 i, (B)·(C) 는 0 ④ head 앞에 끼우기는 head 갱신 ⑤ 누수 없음.
struct SNode { int val; SNode* next; static int live; SNode(int v, SNode* nx) : val(v), next(nx) { ++live; } ~SNode() { --live; } }; int SNode::live = 0;
struct DNode { int val; DNode *next, *prev; static int live; DNode(int v) : val(v), next(nullptr), prev(nullptr) { ++live; } ~DNode() { --live; } }; int DNode::live = 0;
struct SList { SNode* head = nullptr; long hops = 0; ~SList() { while (head) { SNode* nx = head->next; delete head; head = nx; } }
    SNode* pushBack(int v) { SNode** l = &head; while (*l) l = &(*l)->next; *l = new SNode(v, nullptr); return *l; }
    SNode* insertBeforeWalk(SNode* p, int v) { SNode** l = &head; while (*l != p) { l = &(*l)->next; hops++; } *l = new SNode(v, p); return *l; }               // (A) 연결을 찾아 교체
    SNode* insertBeforeTrick(SNode* p, int v) { p->next = new SNode(p->val, p->next); p->val = v; return p; }                                                  // (B) 값 바꿔치기: 새 값이 p 에, 옛 값이 p 뒤의 새 노드에
    std::vector<int> items() const { std::vector<int> r; for (SNode* c = head; c; c = c->next) r.push_back(c->val); return r; }
    std::vector<SNode*> nodes() const { std::vector<SNode*> r; for (SNode* c = head; c; c = c->next) r.push_back(c); return r; } };
struct DList { DNode *head = nullptr, *tail = nullptr; ~DList() { while (head) { DNode* nx = head->next; delete head; head = nx; } }
    DNode* pushBack(int v) { DNode* x = new DNode(v); x->prev = tail; if (tail) tail->next = x; else head = x; tail = x; return x; }
    DNode* insertBefore(DNode* p, int v) { DNode* x = new DNode(v); x->next = p; x->prev = p->prev; if (p->prev) p->prev->next = x; else head = x; p->prev = x; return x; }       // (C) prev 로 O(1)
    std::vector<int> items() const { std::vector<int> r; for (DNode* c = head; c; c = c->next) r.push_back(c->val); return r; } };
int main() {
    std::mt19937 rng(25);
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 30); SList a, b; DList c; std::vector<int> ref; std::vector<SNode*> pa, pb; std::vector<DNode*> pc;
        for (int i = 0; i < n; i++) { int v = (int)(rng() % 100); ref.push_back(v); pa.push_back(a.pushBack(v)); pb.push_back(b.pushBack(v)); pc.push_back(c.pushBack(v)); }
        std::vector<std::pair<SNode*, int>> anchorsA, anchorsB; for (int i = 0; i < n; i++) { anchorsA.push_back({pa[i], ref[i]}); anchorsB.push_back({pb[i], ref[i]}); }
        for (int step = 0; step < 10; step++) { int i = (int)(rng() % ref.size()), v = (int)(rng() % 100 + 1000); long before = a.hops; SNode* na = a.insertBeforeWalk(pa[i], v); b.insertBeforeTrick(pb[i], v); DNode* nc = c.insertBefore(pc[i], v);     // ①
            ref.insert(ref.begin() + i, v); pa.insert(pa.begin() + i, na); pc.insert(pc.begin() + i, nc); assert(a.items() == ref && b.items() == ref && c.items() == ref);
            // (B) 의 노드 목록: 정체성이 이동했으므로 목록을 다시 읽는다
            pb = b.nodes(); assert(a.hops - before == i);                                                                                               // ③ (A) 의 걸음 = 위치 i
            if (i == 0) assert(a.head == na && c.head == nc); }
        for (auto& an : anchorsA) assert(an.first->val == an.second);                                                                                   // ② (A): 기존 노드 모두 같은 값
        int changed = 0; for (auto& an : anchorsB) if (an.first->val != an.second) changed++; assert(changed >= 1); }                                  // (B): 정체성이 바뀐 노드가 있다
    { SList b; SNode* x = b.pushBack(10); SNode* y = b.pushBack(20); b.insertBeforeTrick(y, 15); assert(y->val == 15 && y->next->val == 20 && x->val == 10 && b.items() == (std::vector<int>{10, 15, 20}));     // 외부 포인터 y 는 이제 원소 20 이 아니라 15 를 가리킨다
      SList a; a.pushBack(10); SNode* ay = a.pushBack(20); a.insertBeforeWalk(ay, 15); assert(ay->val == 20 && a.items() == (std::vector<int>{10, 15, 20})); }
    { SList a; SNode* h = a.pushBack(1); a.pushBack(2); SNode* nh = a.insertBeforeWalk(h, 0); assert(a.head == nh && nh->next == h && a.items() == (std::vector<int>{0, 1, 2})); }               // ④
    assert(SNode::live == 0 && DNode::live == 0); std::cout << "InsertBefore: the walk-to-predecessor method (O(i) hops), the O(1) value-swap trick and the doubly linked method all produced vector::insert's sequence; only the value-swap trick changed which element an outside pointer saw, which is why it is unsafe when nodes are referenced elsewhere" << std::endl; return 0;   // ⑤
}
// Time Complexity: 단방향 걷기 O(N), 값 바꿔치기 O(1), 양방향 O(1)
// Space Complexity: O(1)
```
## RemoveNode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 노드 제거(RemoveNode): 노드 p 를 가리키는 포인터가 주어졌을 때 리스트에서 떼어 내고 해제한다. 단방향 리스트에서는 p 의 앞 노드가 필요하다. (A) head 부터 p 를 가리키는 연결을 찾아 건너뛰게 바꾼다 — O(n), 포인터의 포인터로 head 도 같은 코드이며, p 가 이 리스트의 노드가 아니면 끝까지 가서 false 를 돌려줄 수 있다. (B) 다음 노드 복사 트릭: p 에 p->next 의 값을 덮어쓰고 p->next 노드를 해제한다 — O(1) 이지만 꼬리 노드는 못 지우고(다음이 없음), p 가 가리키던 원소가 사실상 다음 원소로 바뀌며 p->next 를 가리키던 외부 포인터는 매달린다(dangling). (C) 양방향 리스트: prev/next 로 O(1), 정체성 유지.
// 외부에서 노드 포인터를 들고 있는 구조(LRU 캐시의 해시 맵 등)에서는 (B) 를 쓰면 다른 원소의 포인터가 무효가 된다. 지운 뒤에는 그 노드로 가는 포인터를 더 쓰면 안 된다.
// 검증: ① (A)·(C) 가 무작위 노드 제거에서 모델(std::vector::erase)과 같음, (A) 는 리스트에 없는 노드 포인터에 false 를 돌려주고 리스트 불변 ② (B) 는 꼬리가 아닌 노드에서 같은 값 순서를 내고 꼬리에서는 불가능(false)임을 확인, 그리고 제거 후 이전 `p->next` 노드가 더 이상 리스트에 없음(외부 포인터가 매달림)을 확인 ③ (A)·(C) 는 다른 노드의 포인터-값 대응 보존 ④ 걸음: (A) 정확히 위치, (C) 0 ⑤ 머리·꼬리·유일한 노드 경계, 누수 없음.
struct SNode { int val; SNode* next; static int live; SNode(int v, SNode* nx) : val(v), next(nx) { ++live; } ~SNode() { --live; } }; int SNode::live = 0;
struct DNode { int val; DNode *next, *prev; static int live; DNode(int v) : val(v), next(nullptr), prev(nullptr) { ++live; } ~DNode() { --live; } }; int DNode::live = 0;
struct SList { SNode* head = nullptr; long hops = 0; ~SList() { while (head) { SNode* nx = head->next; delete head; head = nx; } }
    SNode* pushBack(int v) { SNode** l = &head; while (*l) l = &(*l)->next; *l = new SNode(v, nullptr); return *l; }
    bool removeWalk(SNode* p) { SNode** l = &head; while (*l && *l != p) { l = &(*l)->next; hops++; } if (!*l) return false; *l = p->next; delete p; return true; }     // (A)
    bool removeCopyNext(SNode* p) { if (!p->next) return false; SNode* dead = p->next; p->val = dead->val; p->next = dead->next; delete dead; return true; }               // (B) 꼬리는 불가
    std::vector<int> items() const { std::vector<int> r; for (SNode* c = head; c; c = c->next) r.push_back(c->val); return r; }
    std::vector<SNode*> nodes() const { std::vector<SNode*> r; for (SNode* c = head; c; c = c->next) r.push_back(c); return r; } };
struct DList { DNode *head = nullptr, *tail = nullptr; ~DList() { while (head) { DNode* nx = head->next; delete head; head = nx; } }
    DNode* pushBack(int v) { DNode* x = new DNode(v); x->prev = tail; if (tail) tail->next = x; else head = x; tail = x; return x; }
    void remove(DNode* p) { if (p->prev) p->prev->next = p->next; else head = p->next; if (p->next) p->next->prev = p->prev; else tail = p->prev; delete p; }                   // (C)
    std::vector<int> items() const { std::vector<int> r; for (DNode* c = head; c; c = c->next) r.push_back(c->val); return r; } };
int main() {
    std::mt19937 rng(26);
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 40); SList a; DList c; std::vector<int> ref; std::vector<SNode*> pa; std::vector<DNode*> pc; for (int i = 0; i < n; i++) { int v = (int)(rng() % 100); ref.push_back(v); pa.push_back(a.pushBack(v)); pc.push_back(c.pushBack(v)); }
        SNode* stranger = new SNode(7, nullptr); while (!ref.empty()) { int i = (int)(rng() % ref.size()); std::vector<std::pair<SNode*, int>> others; for (std::size_t k = 0; k < pa.size(); k++) if ((int)k != i) others.push_back({pa[k], ref[k]});         // ①
            long before = a.hops; assert(!a.removeWalk(stranger)); a.hops = before; assert(a.removeWalk(pa[i]) && a.hops - before == i); c.remove(pc[i]); ref.erase(ref.begin() + i); pa.erase(pa.begin() + i); pc.erase(pc.begin() + i);
            assert(a.items() == ref && c.items() == ref); for (auto& o : others) assert(o.first->val == o.second); assert((int)ref.size() == SNode::live - 1 && (int)ref.size() == DNode::live); }                                                   // ③ ④ (stranger 도 SNode 하나)
        delete stranger; assert(a.head == nullptr && c.head == nullptr && c.tail == nullptr); }
    for (int rep = 0; rep < 100; rep++) { int n = 2 + (int)(rng() % 20); SList b; std::vector<int> ref; std::vector<SNode*> pb; for (int i = 0; i < n; i++) { int v = (int)(rng() % 100); ref.push_back(v); pb.push_back(b.pushBack(v)); }          // ②
        int i = (int)(rng() % (n - 1)); SNode* nextBefore = pb[i]->next; assert(nextBefore == pb[i + 1]); assert(b.removeCopyNext(pb[i])); ref.erase(ref.begin() + i); assert(b.items() == ref);
        std::vector<SNode*> now = b.nodes(); assert(std::find(now.begin(), now.end(), nextBefore) == now.end());                                         // 옛 p->next 는 해제되어 리스트에 없다(매달림)
        assert(!b.removeCopyNext(now.back()) && b.items() == ref); }
    { SList s; SNode* only = s.pushBack(5); assert(s.removeWalk(only) && s.head == nullptr && s.items().empty()); SList t; SNode* x = t.pushBack(1); SNode* y = t.pushBack(2); SNode* z = t.pushBack(3); assert(t.removeWalk(x) && t.head == y && t.removeWalk(z) && t.items() == std::vector<int>{2}); }  // ⑤
    { DList d; DNode* x = d.pushBack(1); d.remove(x); assert(d.head == nullptr && d.tail == nullptr); DNode* a = d.pushBack(1); DNode* b = d.pushBack(2); d.remove(a); assert(d.head == b && d.tail == b && b->prev == nullptr); d.remove(b); assert(d.head == nullptr && d.tail == nullptr); }
    assert(SNode::live == 0 && DNode::live == 0); std::cout << "RemoveNode: walking removal (O(i) hops) and doubly linked removal matched vector::erase for random nodes, left every other node's pointer-value pairing intact and rejected a foreign pointer; the copy-next trick worked except at the tail and left the old next node dangling" << std::endl; return 0;
}
// Time Complexity: 단방향 걷기 O(N), 다음 노드 복사 트릭 O(1), 양방향 O(1)
// Space Complexity: O(1)
```
## FindMiddle()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 가운데 찾기(FindMiddle): 길이를 모르는 단방향 리스트의 가운데 노드를 한 번의 순회로 찾는 고전적인 방법은 느린/빠른 포인터다. slow 는 한 칸, fast 는 두 칸씩 간다. fast 가 끝에 닿았을 때 slow 가 가운데다. 길이를 먼저 세고 다시 걷는 방법은 두 번 순회하지만 같은 O(n) 이고, 느린/빠른 포인터는 한 번의 순회로 끝난다(총 포인터 이동 1.5n).
// 길이가 짝수면 가운데가 둘이다. `while (fast && fast->next)` 는 뒤쪽 가운데(인덱스 n/2), `while (fast->next && fast->next->next)` 는 앞쪽 가운데(인덱스 (n−1)/2)를 준다 — 리스트를 반으로 나눌 때는 앞쪽 가운데가 필요하다. 같은 기법의 응용: 뒤에서 k 번째(두 포인터 사이에 간격 k 를 두고 같이 전진), 가운데 노드 삭제, 회문 판별(뒤쪽 절반을 뒤집어 비교).
// 검증: ① 길이 1..100 에서 뒤쪽 가운데 == 인덱스 n/2, 앞쪽 가운데 == 인덱스 (n−1)/2, 반복 횟수 ⌊n/2⌋ / ⌊(n−1)/2⌋, 빈 리스트는 nullptr ② 가운데 삭제가 vector::erase(n/2) 와 같음 ③ 뒤에서 k 번째가 모든 k 에서 맞고 범위 밖은 nullptr, 뒤에서 k 번째 삭제 ④ 회문 판별이 무작위·회문 리스트에서 vector 판별과 같고 호출 뒤 리스트가 원상 복구 ⑤ 노드 누수 없음.
struct Node { int val; Node* next; static int live; Node(int v, Node* nx) : val(v), next(nx) { ++live; } ~Node() { --live; } }; int Node::live = 0;
Node* build(const std::vector<int>& v) { Node* head = nullptr; Node** t = &head; for (int x : v) { *t = new Node(x, nullptr); t = &(*t)->next; } return head; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
std::vector<int> items(const Node* h) { std::vector<int> r; for (; h; h = h->next) r.push_back(h->val); return r; }
Node* middleUpper(Node* head, int& iters) { iters = 0; Node *slow = head, *fast = head; while (fast && fast->next) { slow = slow->next; fast = fast->next->next; iters++; } return slow; }                  // 뒤쪽 가운데
Node* middleLower(Node* head, int& iters) { iters = 0; if (!head) return nullptr; Node *slow = head, *fast = head; while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; iters++; } return slow; }   // 앞쪽 가운데
Node* deleteMiddle(Node* head) { if (!head) return nullptr; Node** link = &head; Node* fast = head; while (fast && fast->next) { link = &(*link)->next; fast = fast->next->next; } Node* dead = *link; *link = dead->next; delete dead; return head; }
Node* nthFromEnd(Node* head, int k) { Node *lead = head, *trail = head; for (int i = 0; i < k; i++) { if (!lead) return nullptr; lead = lead->next; } if (k <= 0) return nullptr; while (lead) { lead = lead->next; trail = trail->next; } return trail; }   // k = 1 이 마지막
Node* removeNthFromEnd(Node* head, int k) { Node* target = nthFromEnd(head, k); if (!target) return head; Node** l = &head; while (*l != target) l = &(*l)->next; *l = target->next; delete target; return head; }
Node* reverse(Node* h) { Node *prev = nullptr; while (h) { Node* nx = h->next; h->next = prev; prev = h; h = nx; } return prev; }
bool isPalindrome(Node* head) { int it; if (!head || !head->next) return true; Node* mid = middleLower(head, it); Node* second = reverse(mid->next); Node *a = head, *b = second; bool ok = true; while (b) { if (a->val != b->val) { ok = false; break; } a = a->next; b = b->next; } mid->next = reverse(second); return ok; }
int main() {
    std::mt19937 rng(27); { int it; assert(middleUpper(nullptr, it) == nullptr && it == 0 && middleLower(nullptr, it) == nullptr); }
    for (int n = 1; n <= 100; n++) { std::vector<int> v(n); for (int i = 0; i < n; i++) v[i] = i; Node* h = build(v); std::vector<Node*> nodes; for (Node* c = h; c; c = c->next) nodes.push_back(c); int iu, il;                          // ①
        assert(middleUpper(h, iu) == nodes[n / 2] && iu == n / 2 && middleLower(h, il) == nodes[(n - 1) / 2] && il == (n - 1) / 2);
        Node* d = deleteMiddle(build(v)); std::vector<int> ref = v; ref.erase(ref.begin() + n / 2); assert(items(d) == ref); destroy(d);                                                               // ②
        for (int k = 0; k <= n + 1; k++) { Node* t = nthFromEnd(h, k); if (k >= 1 && k <= n) assert(t == nodes[n - k]); else assert(t == nullptr); }                                                      // ③
        for (int k : {1, n / 2 + 1, n}) { Node* r = removeNthFromEnd(build(v), k); std::vector<int> r2 = v; r2.erase(r2.end() - k); assert(items(r) == r2); destroy(r); } destroy(h); }
    for (int rep = 0; rep < 600; rep++) { int n = (int)(rng() % 14); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 3); if (rep % 3 == 0) for (int i = 0; i < n / 2; i++) v[n - 1 - i] = v[i];          // ④
        Node* h = build(v); bool want = std::equal(v.begin(), v.end(), v.rbegin()); assert(isPalindrome(h) == want && items(h) == v); destroy(h); }
    assert(Node::live == 0); std::cout << "FindMiddle: slow/fast pointers found the exact middle (upper index n/2 in floor(n/2) steps, lower index (n-1)/2) for every length up to 100; middle deletion, k-th-from-end lookup/removal and the O(1)-space palindrome check (which restores the list) all matched vector-based answers" << std::endl; return 0;
}
// Time Complexity: O(N) (한 번의 순회)
// Space Complexity: O(1)
```
## DetectCycle()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 순환 탐지(DetectCycle): next 를 따라가다 처음 방문한 노드로 되돌아오는 리스트가 순환 리스트다. 순회하면 영원히 끝나지 않는다. 방문한 노드를 해시 집합에 넣어 두고 재방문을 찾으면 O(n) 시간·O(n) 공간이다. 플로이드의 토끼와 거북이는 O(1) 공간으로 해결한다: slow 는 한 칸, fast 는 두 칸씩 가다가 순환이 있으면 반드시 만난다(순환 안에서 둘 사이의 거리가 매 걸음 1 씩 줄기 때문).
// 꼬리(순환 앞 비순환 구간)의 길이를 μ, 순환의 길이를 λ 라 하자. 두 포인터가 만난 뒤 한 포인터를 head 로 되돌리고 둘을 한 칸씩 같이 움직이면 순환의 시작점에서 만난다(걸음 수가 μ) — slow 가 μ+k 칸 갔을 때 fast 는 2(μ+k) 칸이고 그 차 μ+k 는 λ 의 배수이기 때문이다. 시작점에서 한 바퀴를 돌면 λ 를 얻는다. 브렌트의 방법은 거북이를 2 의 거듭제곱 걸음마다 토끼 위치로 순간이동시켜 같은 결과를 얻는다.
// 순환이 있는 리스트를 소멸시킬 때는 노드가 순환에 걸려 한 번 이상 해제되거나 영영 순회가 끝나지 않을 수 있다 — 소유권을 따로 관리(노드 풀)하거나 순환을 끊고 해제해야 한다. 이 코드는 노드 풀이 모든 노드를 소유한다.
// 검증: ① 길이 0..60 의 리스트 전부에서(순환 없음, 그리고 시작 위치 k = 0..n−1 모든 순환) 플로이드가 있다/없다를 맞히고, 시작 노드·μ(= k)·λ(= n−k) 를 정확히 돌려줌 ② 만날 때까지 걸음이 ≤ μ+λ, 순환 없으면 ≤ n/2+1 ③ 브렌트와 해시 집합 방식이 같은 결과(μ, λ, 시작 노드) ④ 순환 끊기 뒤 순회 길이가 n ⑤ 큰 순환(100 만 노드)도 O(1) 공간으로 처리 ⑥ 빈 리스트·자기 순환 경계.
struct Node { int val; Node* next; };
struct Pool { std::vector<Node*> all; Node* make(int v) { all.push_back(new Node{v, nullptr}); return all.back(); } ~Pool() { for (Node* p : all) delete p; } };            // 모든 노드를 풀이 소유 → 순환이 있어도 누수 없음
struct Info { bool has = false; Node* start = nullptr; long mu = 0, lambda = 0, steps = 0; };
Info floyd(Node* head) {
    Info r; Node *slow = head, *fast = head;
    while (fast && fast->next) { slow = slow->next; fast = fast->next->next; r.steps++;
        if (slow == fast) { Node *p = head, *q = slow; while (p != q) { p = p->next; q = q->next; r.mu++; } r.start = p; r.has = true; r.lambda = 1; for (Node* c = p->next; c != p; c = c->next) r.lambda++; return r; } }
    return r; }
Info brent(Node* head) {
    Info r; if (!head) return r; long power = 1, lam = 1; Node *tortoise = head, *hare = head->next;
    while (hare && tortoise != hare) { if (power == lam) { tortoise = hare; power *= 2; lam = 0; } hare = hare->next; lam++; }
    if (!hare) return r; r.has = true; r.lambda = lam; tortoise = hare = head; for (long i = 0; i < lam; i++) hare = hare->next;
    while (tortoise != hare) { tortoise = tortoise->next; hare = hare->next; r.mu++; } r.start = tortoise; return r; }
Info hashSet(Node* head) { Info r; std::unordered_set<Node*> seen; long idx = 0; std::vector<Node*> order; for (Node* c = head; c; c = c->next) { if (seen.count(c)) { r.has = true; r.start = c; r.mu = std::find(order.begin(), order.end(), c) - order.begin(); r.lambda = (long)order.size() - r.mu; return r; } seen.insert(c); order.push_back(c); idx++; } return r; }
long breakCycle(Node* head) { Info f = floyd(head); if (!f.has) { long n = 0; for (Node* c = head; c; c = c->next) n++; return n; } Node* last = f.start; while (last->next != f.start) last = last->next; last->next = nullptr; long n = 0; for (Node* c = head; c; c = c->next) n++; return n; }
int main() {
    { Info f = floyd(nullptr), b = brent(nullptr), h = hashSet(nullptr); assert(!f.has && !b.has && !h.has && f.steps == 0); }                                                                    // ⑥
    for (int n = 1; n <= 60; n++) for (int k = -1; k < n; k++) { Pool pool; std::vector<Node*> nd; for (int i = 0; i < n; i++) nd.push_back(pool.make(i)); for (int i = 0; i + 1 < n; i++) nd[i]->next = nd[i + 1]; if (k >= 0) nd[n - 1]->next = nd[k];   // k = -1: 순환 없음
        Info f = floyd(nd[0]), b = brent(nd[0]), h = hashSet(nd[0]);
        if (k < 0) { assert(!f.has && !b.has && !h.has && f.steps <= n / 2 + 1); }
        else { assert(f.has && f.start == nd[k] && f.mu == k && f.lambda == n - k && f.steps <= f.mu + f.lambda); assert(b.has && b.start == nd[k] && b.mu == k && b.lambda == n - k); assert(h.has && h.start == nd[k] && h.mu == k && h.lambda == n - k); }   // ① ② ③
        assert(breakCycle(nd[0]) == n); Info after = floyd(nd[0]); assert(!after.has); }                                                                                                       // ④
    { const int N = 1000000; Pool pool; pool.all.reserve(N); Node* head = pool.make(0); Node* cur = head; for (int i = 1; i < N; i++) { Node* x = pool.make(i); cur->next = x; cur = x; } Node* target = pool.all[N / 3]; cur->next = target;   // ⑤
      Info f = floyd(head); assert(f.has && f.start == target && f.mu == N / 3 && f.lambda == N - N / 3 && f.steps <= f.mu + f.lambda); Info b = brent(head); assert(b.has && b.start == target && b.mu == N / 3 && b.lambda == N - N / 3); }
    { Pool pool; Node* a = pool.make(1); a->next = a; Info f = floyd(a); assert(f.has && f.start == a && f.mu == 0 && f.lambda == 1); Node* one = pool.make(2); assert(!floyd(one).has && !brent(one).has && !hashSet(one).has); }
    std::cout << "DetectCycle: Floyd's algorithm, Brent's algorithm and a hash set agreed on presence, start node, tail length (mu) and cycle length (lambda) for every list of up to 60 nodes and every cycle entry point; Floyd's pointers met within mu+lambda steps, breaking the cycle restored a length-n list, and a 1,000,000-node loop was handled in O(1) extra space" << std::endl; return 0;
}
// Time Complexity: O(μ + λ) = O(N)
// Space Complexity: O(1) (해시 집합 방식은 O(N))
```
## MergeLists()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 리스트 병합(MergeLists): 정렬된 두 연결 리스트를 하나의 정렬된 리스트로 합친다. 두 리스트의 머리를 비교해 작은 쪽 노드를 결과 리스트의 꼬리에 붙이고 그쪽 포인터를 전진한다. 한쪽이 바닥나면 남은 쪽을 통째로 붙인다. 노드를 새로 만들지 않고 연결만 바꾸므로 추가 공간 O(1), 시간 O(m+n), 비교는 많아야 m+n−1 번이다. 같은 값이면 첫 번째 리스트의 노드를 먼저 내보내면 안정적이다(동률의 원래 순서 유지).
// 꼬리 포인터의 포인터(`Node** tail`)를 쓰면 결과 리스트가 비었을 때의 특별 처리가 없다. 재귀 구현은 짧지만 깊이가 m+n 이라 긴 리스트에서는 스택이 넘친다. k 개의 정렬 리스트는 두 개씩 짝지어 합치는 분할 정복(O(N log k)) 또는 최소 힙으로 k 개 머리 중 최소를 뽑는 방법(O(N log k))으로 합친다. 한쪽 리스트가 통째로 앞서면 비교는 앞선 리스트의 길이만큼만 든다.
// 검증: ① 무작위 정렬 리스트 병합이 std::merge 와 같고(키와 출처 태그까지: 안정성), 비교 횟수 ≤ m+n−1 ② 결과가 두 입력의 모든 노드를 정확히 한 번씩 포함하고 새 할당이 없음(살아 있는 노드 수 불변) ③ 한쪽이 통째로 앞서면 비교 == 앞선 쪽 길이, 빈 리스트·전부 같은 값 경계 ④ 재귀 구현과 같은 결과(작은 입력) ⑤ k 개 병합(분할 정복·힙)이 정렬된 이어 붙임과 같고 안정적(동률은 리스트 번호순) ⑥ 누수 없음.
struct Node { int key, tag; Node* next; static int live; Node(int k, int t) : key(k), tag(t), next(nullptr) { ++live; } ~Node() { --live; } }; int Node::live = 0;
Node* build(const std::vector<std::pair<int, int>>& v) { Node* head = nullptr; Node** t = &head; for (auto& p : v) { *t = new Node(p.first, p.second); t = &(*t)->next; } return head; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
std::vector<std::pair<int, int>> items(const Node* h) { std::vector<std::pair<int, int>> r; for (; h; h = h->next) r.push_back({h->key, h->tag}); return r; }
Node* mergeLists(Node* a, Node* b, long& compares) { Node* head = nullptr; Node** tail = &head; while (a && b) { compares++; if (b->key < a->key) { *tail = b; b = b->next; } else { *tail = a; a = a->next; } tail = &(*tail)->next; } *tail = a ? a : b; return head; }   // 동률이면 a 먼저
Node* mergeRec(Node* a, Node* b) { if (!a) return b; if (!b) return a; if (b->key < a->key) { b->next = mergeRec(a, b->next); return b; } a->next = mergeRec(a->next, b); return a; }
Node* mergeKDivide(std::vector<Node*> lists, std::size_t lo, std::size_t hi, long& compares) { if (lo >= hi) return nullptr; if (hi - lo == 1) return lists[lo]; std::size_t mid = lo + (hi - lo) / 2; Node* l = mergeKDivide(lists, lo, mid, compares); Node* r = mergeKDivide(lists, mid, hi, compares); return mergeLists(l, r, compares); }
Node* mergeKHeap(const std::vector<Node*>& lists) { auto cmp = [](const std::pair<Node*, int>& x, const std::pair<Node*, int>& y) { return x.first->key != y.first->key ? x.first->key > y.first->key : x.second > y.second; };
    std::priority_queue<std::pair<Node*, int>, std::vector<std::pair<Node*, int>>, decltype(cmp)> pq(cmp); for (int i = 0; i < (int)lists.size(); i++) if (lists[i]) pq.push({lists[i], i});
    Node* head = nullptr; Node** tail = &head; while (!pq.empty()) { auto top = pq.top(); pq.pop(); *tail = top.first; tail = &(*tail)->next; if (top.first->next) pq.push({top.first->next, top.second}); } *tail = nullptr; return head; }
int main() {
    std::mt19937 rng(28);
    auto randomSorted = [&](int n, int range, int tagBase) { std::vector<std::pair<int, int>> v; for (int i = 0; i < n; i++) v.push_back({(int)(rng() % range), tagBase + i}); std::stable_sort(v.begin(), v.end(), [](auto& x, auto& y) { return x.first < y.first; }); return v; };
    for (int rep = 0; rep < 400; rep++) { int m = (int)(rng() % 25), n = (int)(rng() % 25), range = 1 + (int)(rng() % 12); auto va = randomSorted(m, range, 0), vb = randomSorted(n, range, 1000);
        Node *a = build(va), *b = build(vb); std::set<Node*> before; for (Node* c = a; c; c = c->next) before.insert(c); for (Node* c = b; c; c = c->next) before.insert(c); int live = Node::live; long cmp = 0;
        Node* m1 = mergeLists(a, b, cmp); std::vector<std::pair<int, int>> ref(va.size() + vb.size()); std::merge(va.begin(), va.end(), vb.begin(), vb.end(), ref.begin(), [](auto& x, auto& y) { return x.first < y.first; });   // ① std::merge 도 동률은 첫 범위 먼저
        assert(items(m1) == ref && cmp <= (long)std::max(0, m + n - 1) && Node::live == live);                                                                                                       // ② 할당 없음
        std::set<Node*> after; for (Node* c = m1; c; c = c->next) after.insert(c); assert(after == before && (int)after.size() == m + n);
        destroy(m1); assert(Node::live == 0);
        if (m + n <= 30) { Node *a2 = build(va), *b2 = build(vb); Node* m2 = mergeRec(a2, b2); assert(items(m2) == ref); destroy(m2); } }                                                              // ④
    { auto va = std::vector<std::pair<int, int>>{{1, 0}, {2, 1}, {3, 2}, {4, 3}}, vb = std::vector<std::pair<int, int>>{{5, 10}, {6, 11}}; long cmp = 0; Node* m1 = mergeLists(build(va), build(vb), cmp); assert(cmp == 4 && items(m1).size() == 6); destroy(m1);   // ③ 앞선 쪽 길이
      cmp = 0; Node* m2 = mergeLists(build(vb), build(va), cmp); assert(cmp == 4); destroy(m2); cmp = 0; Node* e = mergeLists(nullptr, build(va), cmp); assert(cmp == 0 && items(e).size() == 4); destroy(e); cmp = 0; assert(mergeLists(nullptr, nullptr, cmp) == nullptr);
      std::vector<std::pair<int, int>> same1 = {{7, 0}, {7, 1}, {7, 2}}, same2 = {{7, 10}, {7, 11}}; cmp = 0; Node* s = mergeLists(build(same1), build(same2), cmp); assert((items(s) == std::vector<std::pair<int, int>>{{7, 0}, {7, 1}, {7, 2}, {7, 10}, {7, 11}})); destroy(s); }
    for (int rep = 0; rep < 150; rep++) { int k = (int)(rng() % 9); std::vector<std::vector<std::pair<int, int>>> vs; std::vector<std::pair<int, int>> all; for (int i = 0; i < k; i++) { vs.push_back(randomSorted((int)(rng() % 15), 8, 100 * (i + 1))); all.insert(all.end(), vs.back().begin(), vs.back().end()); }   // ⑤
        std::stable_sort(all.begin(), all.end(), [](auto& x, auto& y) { return x.first < y.first; });
        std::vector<Node*> l1, l2; for (auto& v : vs) { l1.push_back(build(v)); l2.push_back(build(v)); } long cmp = 0; Node* d = mergeKDivide(l1, 0, l1.size(), cmp); Node* h = mergeKHeap(l2); assert(items(d) == all && items(h) == all); destroy(d); destroy(h); }
    assert(Node::live == 0); std::cout << "MergeLists: 400 random merges matched std::merge including tie order, used at most m+n-1 comparisons and no allocation, and kept every node exactly once; a list entirely before the other cost exactly its own length in comparisons; k-way merges by divide-and-conquer and by heap were stable and equal to the sorted concatenation" << std::endl; return 0;
}
// Time Complexity: 두 리스트 O(M+N), k 개 O(N log k)
// Space Complexity: 반복 O(1), 재귀 O(M+N), k 개 힙 O(k)
```
## SplitList()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 리스트 나누기(SplitList): 연결 리스트 하나를 둘 이상으로 쪼갠다. 노드를 복사하지 않고 한 노드의 next 만 끊으면 되므로 걷는 비용 외에는 O(1) 이다. 대표적인 방법: (1) 위치 k 에서 나누기, (2) 반으로 나누기(느린/빠른 포인터로 가운데를 찾아 끊기 — 앞쪽 가운데에서 끊어야 앞 조각이 ⌈n/2⌉ 개가 된다), (3) 홀수/짝수 번째로 번갈아 나누기, (4) 조건에 따라 나누기(안정적 분할: 조건을 만족하는 노드들과 아닌 노드들을 각각 원래 순서대로 모음), (5) k 개 조각으로 최대한 고르게 나누기(앞쪽 조각이 하나 더 큼).
// 반으로 나누기와 병합(MergeLists)을 합치면 연결 리스트 병합 정렬이 된다: 나누고, 각각 재귀로 정렬하고, 합친다. 배열과 달리 임시 배열이 필요 없고 노드를 옮기지 않으며 안정적이다. 비교 횟수는 n⌈log₂ n⌉ 를 넘지 않는다. 안정적 분할은 퀵 정렬의 분할 단계로도 쓴다.
// 검증: ① 위치 나누기가 모든 (n ≤ 20, k ≤ n+2) 에서 앞 k 개/나머지로 나뉘고 노드 합집합·순서가 보존 ② 반으로 나누기: 앞 조각 길이 == ⌈n/2⌉ ③ 번갈아 나누기와 조건 분할이 안정적(각 조각의 원래 순서 유지) ④ k 조각 나누기: 길이 차 ≤ 1 이고 앞쪽이 크며 합이 n, k > n 이면 빈 조각이 생김 ⑤ 병합 정렬이 std::stable_sort 와 같고(키·출처 태그) 비교 ≤ n⌈log₂ n⌉ ⑥ 모든 연산에서 새 할당 없음, 누수 없음.
struct Node { int key, tag; Node* next; static int live; Node(int k, int t) : key(k), tag(t), next(nullptr) { ++live; } ~Node() { --live; } }; int Node::live = 0;
Node* build(const std::vector<std::pair<int, int>>& v) { Node* head = nullptr; Node** t = &head; for (auto& p : v) { *t = new Node(p.first, p.second); t = &(*t)->next; } return head; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
std::vector<std::pair<int, int>> items(const Node* h) { std::vector<std::pair<int, int>> r; for (; h; h = h->next) r.push_back({h->key, h->tag}); return r; }
std::vector<Node*> nodes(Node* h) { std::vector<Node*> r; for (; h; h = h->next) r.push_back(h); return r; }
Node* splitAt(Node*& head, int k) { if (k <= 0) { Node* rest = head; head = nullptr; return rest; } Node* c = head; for (int i = 1; i < k && c; i++) c = c->next; if (!c) return nullptr; Node* rest = c->next; c->next = nullptr; return rest; }   // 앞 k 개는 head, 나머지를 반환
Node* splitHalf(Node* head) { if (!head || !head->next) return nullptr; Node *slow = head, *fast = head; while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; } Node* second = slow->next; slow->next = nullptr; return second; }   // 앞쪽 가운데에서 끊기
void splitAlternate(Node* head, Node*& odd, Node*& even) { Node **to = &odd, **te = &even; bool toggle = true; *to = *te = nullptr; for (Node* c = head; c;) { Node* nx = c->next; c->next = nullptr; if (toggle) { *to = c; to = &c->next; } else { *te = c; te = &c->next; } toggle = !toggle; c = nx; } }
template <class Pred> void partitionStable(Node* head, Pred p, Node*& yes, Node*& no) { Node **ty = &yes, **tn = &no; yes = no = nullptr; for (Node* c = head; c;) { Node* nx = c->next; c->next = nullptr; if (p(c->key)) { *ty = c; ty = &c->next; } else { *tn = c; tn = &c->next; } c = nx; } }
std::vector<Node*> splitIntoParts(Node* head, int k) { int n = 0; for (Node* c = head; c; c = c->next) n++; std::vector<Node*> parts(k, nullptr); int base = n / k, extra = n % k; Node* c = head;
    for (int i = 0; i < k; i++) { parts[i] = c; int len = base + (i < extra ? 1 : 0); for (int j = 1; j < len && c; j++) c = c->next; if (c && len > 0) { Node* nx = c->next; c->next = nullptr; c = nx; } else c = nullptr; } return parts; }
Node* mergeSorted(Node* a, Node* b, long& compares) { Node* head = nullptr; Node** tail = &head; while (a && b) { compares++; if (b->key < a->key) { *tail = b; b = b->next; } else { *tail = a; a = a->next; } tail = &(*tail)->next; } *tail = a ? a : b; return head; }
Node* mergeSort(Node* head, long& compares) { if (!head || !head->next) return head; Node* second = splitHalf(head); return mergeSorted(mergeSort(head, compares), mergeSort(second, compares), compares); }
int main() {
    std::mt19937 rng(29); auto make = [&](int n) { std::vector<std::pair<int, int>> v; for (int i = 0; i < n; i++) v.push_back({(int)(rng() % 6), i}); return v; };
    for (int n = 0; n <= 20; n++) for (int k = -1; k <= n + 2; k++) { auto v = make(n); Node* head = build(v); std::vector<Node*> before = nodes(head); Node* rest = splitAt(head, k); int cut = std::max(0, std::min(k, n));          // ①
        std::vector<std::pair<int, int>> a(v.begin(), v.begin() + cut), b(v.begin() + cut, v.end()); assert(items(head) == a && items(rest) == b); std::vector<Node*> joined = nodes(head); std::vector<Node*> r2 = nodes(rest); joined.insert(joined.end(), r2.begin(), r2.end()); assert(joined == before); destroy(head); destroy(rest); }
    for (int n = 0; n <= 25; n++) { auto v = make(n); Node* head = build(v); Node* second = splitHalf(head); assert((int)nodes(head).size() == (n + 1) / 2 && (int)nodes(second).size() == n / 2); std::vector<std::pair<int, int>> a(v.begin(), v.begin() + (n + 1) / 2), b(v.begin() + (n + 1) / 2, v.end()); assert(items(head) == a && items(second) == b); destroy(head); destroy(second); }   // ②
    for (int rep = 0; rep < 100; rep++) { auto v = make((int)(rng() % 30)); Node *odd, *even; Node* head = build(v); splitAlternate(head, odd, even); std::vector<std::pair<int, int>> o, e; for (std::size_t i = 0; i < v.size(); i++) (i % 2 == 0 ? o : e).push_back(v[i]); assert(items(odd) == o && items(even) == e); destroy(odd); destroy(even);   // ③
        Node *yes, *no; head = build(v); partitionStable(head, [](int key) { return key % 2 == 0; }, yes, no); std::vector<std::pair<int, int>> y, nn; for (auto& p : v) (p.first % 2 == 0 ? y : nn).push_back(p); assert(items(yes) == y && items(no) == nn); destroy(yes); destroy(no); }
    for (int n = 0; n <= 20; n++) for (int k = 1; k <= 25; k++) { auto v = make(n); Node* head = build(v); std::vector<Node*> before = nodes(head); std::vector<Node*> parts = splitIntoParts(head, k); std::vector<Node*> joined; int total = 0, prevLen = 1 << 30;   // ④
        for (Node* p : parts) { std::vector<Node*> ns = nodes(p); joined.insert(joined.end(), ns.begin(), ns.end()); int len = (int)ns.size(); total += len; assert(len <= prevLen && len >= n / k && len <= (n + k - 1) / k); prevLen = len; }
        assert(total == n && joined == before && (int)parts.size() == k); if (k > n) for (int i = n; i < k; i++) assert(parts[i] == nullptr); for (Node* p : parts) destroy(p); }
    for (int rep = 0; rep < 200; rep++) { int n = (int)(rng() % 60); auto v = make(n); Node* head = build(v); int live = Node::live; long cmp = 0; Node* sorted = mergeSort(head, cmp); std::vector<std::pair<int, int>> ref = v; std::stable_sort(ref.begin(), ref.end(), [](auto& x, auto& y) { return x.first < y.first; });   // ⑤ ⑥
        assert(items(sorted) == ref && Node::live == live); if (n > 1) assert(cmp <= (long)n * (long)std::ceil(std::log2((double)n))); destroy(sorted); assert(Node::live == 0); }
    std::cout << "SplitList: splitting at every position, in halves (front half = ceil(n/2)), alternately, by a stable predicate and into k nearly equal parts preserved every node and the original order, and combining splitHalf with a merge gave a stable O(n log n) list merge sort that matched std::stable_sort" << std::endl; return 0;
}
// Time Complexity: 나누기 O(N) (걷기), 병합 정렬 O(N log N)
// Space Complexity: O(1) (병합 정렬은 재귀 O(log N))
```

# Part 4. 리스트 알고리즘
## BubbleSort()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 거품 정렬(Bubble Sort): 이웃한 두 원소를 비교해 순서가 틀리면 맞바꾸는 일을 끝에서 끝까지 반복한다. 한 번 훑으면 가장 큰 원소가 맨 끝으로 "떠오르므로" 다음 훑기는 한 칸 덜 본다. 비교 횟수는 입력과 무관하게 n(n−1)/2, 교환은 엄격히 큰 이웃 쌍(역순쌍, inversion)을 하나씩 없애므로 교환 횟수 == 역순쌍의 개수다 — 이것이 알고리즘의 정확한 비용 모델이다.
// 개선 둘: (1) 한 번 훑어서 교환이 하나도 없으면 이미 정렬됐으므로 멈춘다(정렬된 입력은 n−1 번 비교로 끝), (2) 마지막으로 교환한 위치를 기억해 그 뒤는 다음 훑기에서 보지 않는다. 칵테일 셰이커 정렬은 왼쪽→오른쪽, 오른쪽→왼쪽을 번갈아 훑어 "작은 원소가 앞으로 가는 데 오래 걸리는" 약점을 줄인다. 같은 키끼리는 교환하지 않으므로 안정적이다.
// 검증: ① 네 변형(기본·조기 종료·마지막 교환 위치·칵테일)이 모든 무작위 입력(중복 많음)에서 std::stable_sort 와 같은 결과(키와 출처 태그 포함 → 안정성) ② 모든 변형의 교환 횟수 == 독립적으로 센 역순쌍 수 ③ 기본 변형의 비교 == n(n−1)/2, 조기 종료·마지막 교환은 그 이하 ④ 이미 정렬된 입력은 조기 종료가 정확히 n−1 번 비교·한 번 훑기, 역순 입력은 교환 n(n−1)/2 ⑤ 길이 0·1·전부 같은 값 경계.
struct Rec { int key, tag; };
struct Cost { long cmp = 0, swaps = 0, passes = 0; };
void bubblePlain(std::vector<Rec>& a, Cost& c) { int n = (int)a.size(); for (int i = 0; i + 1 < n; i++) { c.passes++; for (int j = 0; j + 1 < n - i; j++) { c.cmp++; if (a[j].key > a[j + 1].key) { std::swap(a[j], a[j + 1]); c.swaps++; } } } }
void bubbleEarlyExit(std::vector<Rec>& a, Cost& c) { int n = (int)a.size(); for (int i = 0; i + 1 < n; i++) { c.passes++; bool swapped = false; for (int j = 0; j + 1 < n - i; j++) { c.cmp++; if (a[j].key > a[j + 1].key) { std::swap(a[j], a[j + 1]); c.swaps++; swapped = true; } } if (!swapped) break; } }
void bubbleLastSwap(std::vector<Rec>& a, Cost& c) { int bound = (int)a.size(); while (bound > 1) { c.passes++; int last = 0; for (int j = 0; j + 1 < bound; j++) { c.cmp++; if (a[j].key > a[j + 1].key) { std::swap(a[j], a[j + 1]); c.swaps++; last = j + 1; } } bound = last; } }
void cocktail(std::vector<Rec>& a, Cost& c) { int lo = 0, hi = (int)a.size() - 1; bool swapped = true;
    while (swapped && lo < hi) { swapped = false; c.passes++; for (int j = lo; j < hi; j++) { c.cmp++; if (a[j].key > a[j + 1].key) { std::swap(a[j], a[j + 1]); c.swaps++; swapped = true; } } hi--; if (!swapped) break; swapped = false;
        for (int j = hi; j > lo; j--) { c.cmp++; if (a[j - 1].key > a[j].key) { std::swap(a[j - 1], a[j]); c.swaps++; swapped = true; } } lo++; } }
long inversionsMerge(std::vector<int> v) { std::vector<int> tmp(v.size()); long inv = 0; for (std::size_t w = 1; w < v.size(); w *= 2) { for (std::size_t lo = 0; lo < v.size(); lo += 2 * w) { std::size_t mid = std::min(lo + w, v.size()), hi = std::min(lo + 2 * w, v.size()), i = lo, j = mid, k = lo;
        while (i < mid || j < hi) { if (j >= hi || (i < mid && v[i] <= v[j])) tmp[k++] = v[i++]; else { inv += (long)(mid - i); tmp[k++] = v[j++]; } } } v = tmp; } return inv; }   // 독립적인 O(n log n) 역순쌍 계수
int main() {
    std::mt19937 rng(30); void (*variants[])(std::vector<Rec>&, Cost&) = {bubblePlain, bubbleEarlyExit, bubbleLastSwap, cocktail};
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 60), range = 1 + (int)(rng() % 12); std::vector<Rec> base(n); for (int i = 0; i < n; i++) base[i] = {(int)(rng() % range), i};
        std::vector<Rec> ref = base; std::stable_sort(ref.begin(), ref.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; }); std::vector<int> keys; for (const Rec& r : base) keys.push_back(r.key); long inv = inversionsMerge(keys);
        long brute = 0; for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) brute += keys[i] > keys[j]; assert(inv == brute); Cost cs[4];
        for (int v = 0; v < 4; v++) { std::vector<Rec> a = base; variants[v](a, cs[v]); for (int i = 0; i < n; i++) assert(a[i].key == ref[i].key && a[i].tag == ref[i].tag); assert(cs[v].swaps == inv); }   // ① ②
        long full = (long)n * (n - 1) / 2; assert(cs[0].cmp == (n > 0 ? full : 0) && cs[1].cmp <= full && cs[2].cmp <= cs[1].cmp + 0 + full); assert(cs[2].cmp <= full); }                     // ③
    for (int n : {2, 5, 40}) { std::vector<Rec> a(n); for (int i = 0; i < n; i++) a[i] = {i, i}; Cost c; bubbleEarlyExit(a, c); assert(c.cmp == n - 1 && c.passes == 1 && c.swaps == 0);                  // ④
        std::vector<Rec> r(n); for (int i = 0; i < n; i++) r[i] = {n - i, i}; Cost d; bubblePlain(r, d); assert(d.swaps == (long)n * (n - 1) / 2 && std::is_sorted(r.begin(), r.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; })); Cost e; r.assign(n, Rec{0, 0}); bubbleLastSwap(r, e); assert(e.swaps == 0 && e.cmp == n - 1); }
    for (int v = 0; v < 4; v++) { std::vector<Rec> e; Cost c; variants[v](e, c); assert(e.empty() && c.cmp == 0); std::vector<Rec> one = {{5, 0}}; variants[v](one, c); assert(one.size() == 1 && c.cmp == 0); std::vector<Rec> same = {{3, 0}, {3, 1}, {3, 2}}; variants[v](same, c); assert(same[0].tag == 0 && same[1].tag == 1 && same[2].tag == 2); }   // ⑤
    std::cout << "BubbleSort: four variants matched std::stable_sort (keys and tags) on 500 random arrays with many duplicates, every variant's swap count equalled the independently counted number of inversions, the plain version made exactly n(n-1)/2 comparisons, and sorted input needed one pass of n-1 comparisons with early exit" << std::endl; return 0;
}
// Time Complexity: 최악·평균 O(N²), 최선(조기 종료) O(N)
// Space Complexity: O(1)
```
## SelectionSort()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 선택 정렬(Selection Sort): 남은 구간에서 가장 작은 원소를 찾아 구간의 맨 앞과 맞바꾸는 일을 반복한다. 비교 횟수는 입력과 무관하게 항상 n(n−1)/2 이고(정렬된 입력도 마찬가지 — 적응성이 없다), 교환은 많아야 n−1 번이다. 쓰기 비용이 비싼 매체(플래시 메모리 등)에서 쓰기를 최소화하는 정렬이 필요할 때 의미가 있다. 삽입 정렬은 역순 입력에서 n(n−1)/2 번 이동한다.
// 안정적이지 않다: 맨 앞 원소를 멀리 있는 최솟값과 맞바꾸면서 같은 키의 상대 순서가 뒤바뀔 수 있다(예: 2a, 2b, 1 → 1, 2b, 2a). 맞바꾸는 대신 최솟값을 앞으로 끌어오고 그 사이 원소를 한 칸씩 뒤로 밀면 안정적이지만 이동이 늘어난다. 양방향 선택 정렬은 한 번 훑으며 최솟값과 최댓값을 동시에 찾아 양끝에 놓는다.
// 검증: ① 세 변형(기본·안정·양방향)이 모든 무작위 입력에서 키 기준으로 정렬되고 안정 변형은 std::stable_sort 와 완전히 같음 ② 기본 변형의 비교가 항상 n(n−1)/2, 교환 ≤ n−1, 정렬된 입력은 교환 0 ③ 키가 {0,1,2} 인 길이 ≤ 6 의 모든 입력(3⁶ 가지까지)에서 기본 변형이 불안정한 경우가 실제로 존재하고 안정 변형은 한 번도 불안정하지 않음 ④ 쓰기 횟수 비교: 역순 입력에서 선택 정렬은 ≤ 3(n−1) 쓰기, 삽입 정렬은 n(n−1)/2 이동 ⑤ 길이 0·1·전부 같은 값.
struct Rec { int key, tag; };
struct Cost { long cmp = 0, swaps = 0, moves = 0; };
void selection(std::vector<Rec>& a, Cost& c) { int n = (int)a.size(); for (int i = 0; i + 1 < n; i++) { int m = i; for (int j = i + 1; j < n; j++) { c.cmp++; if (a[j].key < a[m].key) m = j; } if (m != i) { std::swap(a[i], a[m]); c.swaps++; } } }
void selectionStable(std::vector<Rec>& a, Cost& c) { int n = (int)a.size(); for (int i = 0; i + 1 < n; i++) { int m = i; for (int j = i + 1; j < n; j++) { c.cmp++; if (a[j].key < a[m].key) m = j; } if (m != i) { Rec x = a[m]; for (int k = m; k > i; k--) { a[k] = a[k - 1]; c.moves++; } a[i] = x; c.moves++; } } }   // 끌어오고 밀기
void selectionDouble(std::vector<Rec>& a, Cost& c) { int lo = 0, hi = (int)a.size() - 1; while (lo < hi) { int mn = lo, mx = lo; for (int j = lo; j <= hi; j++) { c.cmp += 2; if (a[j].key < a[mn].key) mn = j; if (a[j].key > a[mx].key) mx = j; }
        std::swap(a[lo], a[mn]); c.swaps++; if (mx == lo) mx = mn; std::swap(a[hi], a[mx]); c.swaps++; lo++; hi--; } }                                       // 최솟값을 놓은 뒤 최댓값 위치 보정
bool keysSorted(const std::vector<Rec>& a) { return std::is_sorted(a.begin(), a.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; }); }
bool stableOutput(const std::vector<Rec>& a) { for (std::size_t i = 1; i < a.size(); i++) if (a[i - 1].key == a[i].key && a[i - 1].tag > a[i].tag) return false; return true; }
int main() {
    std::mt19937 rng(31);
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 50), range = 1 + (int)(rng() % 10); std::vector<Rec> base(n); for (int i = 0; i < n; i++) base[i] = {(int)(rng() % range), i};
        std::vector<Rec> ref = base; std::stable_sort(ref.begin(), ref.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; });
        std::vector<Rec> a = base, b = base, d = base; Cost ca, cb, cd; selection(a, ca); selectionStable(b, cb); selectionDouble(d, cd); assert(keysSorted(a) && keysSorted(b) && keysSorted(d));                          // ①
        for (int i = 0; i < n; i++) assert(b[i].key == ref[i].key && b[i].tag == ref[i].tag); std::vector<int> ka, kd; for (auto& r : a) ka.push_back(r.key); for (auto& r : d) kd.push_back(r.key); assert(ka == kd);
        assert(ca.cmp == (long)n * (n - 1) / 2 && cb.cmp == ca.cmp && ca.swaps <= std::max(0, n - 1)); if (keysSorted(base) && stableOutput(base)) assert(ca.swaps == 0 && cb.moves == 0); }                         // ②
    int unstableSeen = 0, stableViolations = 0;
    for (int n = 1; n <= 6; n++) { int total = 1; for (int i = 0; i < n; i++) total *= 3; for (int code = 0; code < total; code++) { std::vector<Rec> base(n); int x = code; for (int i = 0; i < n; i++) { base[i] = {x % 3, i}; x /= 3; }   // ③
            std::vector<Rec> a = base, b = base; Cost c; selection(a, c); selectionStable(b, c); if (!stableOutput(a)) unstableSeen++; if (!stableOutput(b)) stableViolations++; } }
    assert(unstableSeen > 0 && stableViolations == 0);
    { std::vector<Rec> twos = {{2, 0}, {2, 1}, {1, 2}}; Cost c; selection(twos, c); assert(twos[0].key == 1 && twos[1].tag == 1 && twos[2].tag == 0); }                                                  // 2a,2b,1 → 1,2b,2a
    { int n = 200; std::vector<Rec> r(n); for (int i = 0; i < n; i++) r[i] = {n - i, i}; std::vector<Rec> s = r; Cost sel, ins; selection(r, sel); assert(sel.swaps == n / 2 && sel.swaps * 3 <= 3L * (n - 1));                        // ④ 역순: 교환 n/2
      long shifts = 0; for (int i = 1; i < n; i++) { Rec x = s[i]; int j = i; while (j > 0 && s[j - 1].key > x.key) { s[j] = s[j - 1]; shifts++; j--; } s[j] = x; } assert(shifts == (long)n * (n - 1) / 2 && sel.swaps < shifts / 50); }
    { std::vector<Rec> e; Cost c; selection(e, c); selectionStable(e, c); selectionDouble(e, c); assert(c.cmp == 0); std::vector<Rec> one = {{9, 0}}; selection(one, c); selectionDouble(one, c); assert(one[0].key == 9); std::vector<Rec> same = {{4, 0}, {4, 1}, {4, 2}}; Cost z; selection(same, z); assert(z.swaps == 0 && z.cmp == 3); }   // ⑤
    std::cout << "SelectionSort: the stable variant equalled std::stable_sort on 500 random arrays; plain selection always made n(n-1)/2 comparisons and at most n-1 swaps (n/2 on reversed input, versus n(n-1)/2 shifts for insertion sort); exhaustively over keys in {0,1,2} it was unstable in " << unstableSeen << " cases while the stable variant never was" << std::endl; return 0;
}
// Time Complexity: 비교 항상 O(N²), 교환 O(N)
// Space Complexity: O(1)
```
## InsertionSort()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <vector>

// 삽입 정렬(Insertion Sort): 앞쪽에 이미 정렬된 부분 [0, i) 이 있다고 보고, 다음 원소를 그 안의 알맞은 위치에 끼워 넣는다. 끼울 위치까지 더 큰 원소를 한 칸씩 뒤로 민다. 정확한 비용: 이동 횟수 == 역순쌍의 개수, 비교 횟수는 이동 횟수 + (끼울 자리를 찾아 멈추는 데 쓴 비교, 많아야 n−1) 이다. 그래서 입력이 거의 정렬되어 있으면 O(n + 역순쌍) 으로 매우 빠르다(적응적), 정렬된 입력은 n−1 번 비교에 이동 0, 역순 입력은 n(n−1)/2.
// 같은 키를 만나면 멈추므로(엄격히 큰 것만 민다) 안정적이다. 이진 삽입 정렬은 끼울 위치를 이진 탐색(상한 위치)으로 찾아 비교를 O(n log n) 으로 줄이지만 이동은 그대로다. 정렬된 부분은 매 단계의 불변식이며, 데이터가 하나씩 도착하는 온라인 상황에서도 매 순간 정렬된 상태를 유지한다. 연결 리스트에서는 이동 대신 노드 연결만 바꾸면 되고 정렬된 결과 리스트에 하나씩 끼운다. 다만 단방향 리스트는 앞에서부터 걸어 위치를 찾으므로 정렬된 입력에서도 비교가 n(n−1)/2 번 든다(배열처럼 뒤에서부터 찾으려면 양방향 리스트와 꼬리 포인터가 필요하다) — 적응성은 탐색 방향에 달려 있다.
// 검증: ① 무작위 입력(중복 많음)에서 std::stable_sort 와 완전히 같고(안정) 매 바깥 반복 뒤 앞부분이 정렬된 부분 순열(불변식) ② 이동 == 독립적으로 센 역순쌍 수, 비교는 이동 ≤ 비교 ≤ 이동 + (n−1) ③ 정렬된 입력 비교 n−1·이동 0, 역순 입력 이동 n(n−1)/2·비교도 같음, 같은 키만 있으면 이동 0 ④ 이진 삽입이 같은 결과이고 비교 ≤ Σ⌈log₂(i+1)⌉ ⑤ 연결 리스트 삽입 정렬이 같은 결과이고 노드 누수·복사 없으며 비교 횟수가 앞에서부터 걷는 비용 Σ(자신 이하의 개수 + 1) 과 정확히 같음.
struct Rec { int key, tag; };
struct Cost { long cmp = 0, shifts = 0; };
template <class Hook> void insertion(std::vector<Rec>& a, Cost& c, Hook hook) { for (std::size_t i = 1; i < a.size(); i++) { Rec x = a[i]; std::size_t j = i; while (j > 0) { c.cmp++; if (a[j - 1].key > x.key) { a[j] = a[j - 1]; c.shifts++; j--; } else break; } a[j] = x; hook(i); } }
void binaryInsertion(std::vector<Rec>& a, Cost& c) { for (std::size_t i = 1; i < a.size(); i++) { Rec x = a[i]; std::size_t lo = 0, hi = i; while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; c.cmp++; if (a[mid].key <= x.key) lo = mid + 1; else hi = mid; }   // 상한 위치 → 안정적
        for (std::size_t j = i; j > lo; j--) { a[j] = a[j - 1]; c.shifts++; } a[lo] = x; } }
struct Node { int key, tag; Node* next; static int live; Node(int k, int t) : key(k), tag(t), next(nullptr) { ++live; } ~Node() { --live; } }; int Node::live = 0;
Node* insertionList(Node* head, long& cmp) { Node* sorted = nullptr; while (head) { Node* cur = head; head = head->next; Node** link = &sorted; while (*link) { cmp++; if ((*link)->key > cur->key) break; link = &(*link)->next; } cur->next = *link; *link = cur; } return sorted; }   // 같은 키의 뒤에 끼움
long inversionsBrute(const std::vector<Rec>& a) { long inv = 0; for (std::size_t i = 0; i < a.size(); i++) for (std::size_t j = i + 1; j < a.size(); j++) inv += a[i].key > a[j].key; return inv; }
int main() {
    std::mt19937 rng(32);
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 60), range = 1 + (int)(rng() % 15); std::vector<Rec> base(n); for (int i = 0; i < n; i++) base[i] = {(int)(rng() % range), i};
        std::vector<Rec> ref = base; std::stable_sort(ref.begin(), ref.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; }); long inv = inversionsBrute(base);
        std::vector<Rec> a = base, b = base; Cost ca, cb; insertion(a, ca, [&](std::size_t i) { for (std::size_t k = 1; k <= i; k++) assert(a[k - 1].key <= a[k].key); });                       // ① 매 반복 뒤 앞부분 정렬
        for (int i = 0; i < n; i++) assert(a[i].key == ref[i].key && a[i].tag == ref[i].tag); assert(ca.shifts == inv && ca.cmp >= ca.shifts && ca.cmp <= ca.shifts + std::max(0, n - 1));     // ②
        binaryInsertion(b, cb); for (int i = 0; i < n; i++) assert(b[i].key == ref[i].key && b[i].tag == ref[i].tag); long bound = 0; for (int i = 1; i < n; i++) bound += (long)std::ceil(std::log2((double)(i + 1))); assert(cb.shifts == inv && cb.cmp <= bound);   // ④
        Node* head = nullptr; Node** t = &head; for (auto& r : base) { *t = new Node(r.key, r.tag); t = &(*t)->next; } int live = Node::live; long cl = 0; Node* s = insertionList(head, cl); std::vector<Rec> got; for (Node* c = s; c; c = c->next) got.push_back({c->key, c->tag});   // ⑤
        for (int i = 0; i < n; i++) assert(got[i].key == ref[i].key && got[i].tag == ref[i].tag); long walk = 0; for (int i = 0; i < n; i++) { long le = 0; for (int j = 0; j < i; j++) le += base[j].key <= base[i].key; walk += le + (le < i ? 1 : 0); } assert((int)got.size() == n && Node::live == live && cl == walk); while (s) { Node* nx = s->next; delete s; s = nx; } assert(Node::live == 0); }
    for (int n : {2, 10, 80}) { std::vector<Rec> a(n); for (int i = 0; i < n; i++) a[i] = {i, i}; Cost c; insertion(a, c, [](std::size_t) {}); assert(c.cmp == n - 1 && c.shifts == 0);                              // ③
        std::vector<Rec> r(n); for (int i = 0; i < n; i++) r[i] = {n - i, i}; Cost d; insertion(r, d, [](std::size_t) {}); assert(d.shifts == (long)n * (n - 1) / 2 && d.cmp == d.shifts); std::vector<Rec> same(n, Rec{7, 0}); for (int i = 0; i < n; i++) same[i].tag = i; Cost e; insertion(same, e, [](std::size_t) {}); assert(e.shifts == 0 && e.cmp == n - 1); }
    { std::vector<Rec> stream; Cost c; std::mt19937 r2(5); for (int i = 0; i < 300; i++) { stream.push_back({(int)(r2() % 50), i}); insertion(stream, c, [](std::size_t) {}); assert(std::is_sorted(stream.begin(), stream.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; })); } }   // 온라인: 도착할 때마다 정렬 유지
    std::cout << "InsertionSort: 500 random arrays matched std::stable_sort with the sorted-prefix invariant holding after every pass; shifts equalled the number of inversions and comparisons stayed within shifts + n - 1; sorted input cost n-1 comparisons, reversed input n(n-1)/2 shifts; binary insertion and linked-list insertion gave identical stable results" << std::endl; return 0;
}
// Time Complexity: 최악·평균 O(N²), 최선 O(N), 일반적으로 O(N + 역순쌍 수)
// Space Complexity: O(1)
```
## MergeSort()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 병합 정렬(Merge Sort): 반으로 나누어 각각 정렬한 뒤 정렬된 두 반쪽을 병합한다. 병합에서 같은 키는 왼쪽 반쪽을 먼저 내보내므로 안정적이다. 임시 배열이 필요해 추가 공간 O(n) 이지만 어떤 입력에서도 O(n log n) 을 보장한다(퀵 정렬의 최악 O(n²) 이 없음). 최악 비교 횟수는 W(n) = n⌈log₂ n⌉ − 2^⌈log₂ n⌉ + 1 이다.
// 변형: 상향식(길이 1, 2, 4, … 의 구간을 차례로 병합 — 재귀 없음), 자연 병합 정렬(입력에 이미 있는 오름차순 구간(run)을 찾아 짝지어 병합 — 이미 정렬된 입력은 구간 판정 n−1 번 비교만 하고 병합은 한 번도 하지 않는다). 병합 도중 왼쪽 원소가 오른쪽 원소보다 클 때 왼쪽에 남은 개수만큼이 역순쌍이므로 정렬하며 역순쌍 수를 O(n log n) 으로 센다.
// 검증: ① 하향식·상향식·자연 병합이 std::stable_sort 와 완전히 같음(키와 출처 태그: 안정성) ② 모든 n ≤ 130 에서 하향식 비교 ≤ W(n), 상향식도 ≤ W(n) + n ③ 병합 정렬 중 센 역순쌍 수가 O(n²) 무차별 계산과 같음 ④ 자연 병합: 정렬된 입력은 병합 비교 0, 두 개의 run 이 이어진 입력은 병합 비교 ≤ n−1, 임의 입력에서도 정확 ⑤ 길이 0·1·전부 같은 값·역순·큰 입력(20 만) 경계.
struct Rec { int key, tag; };
struct Cost { long cmp = 0; long inversions = 0; };
void mergeRange(std::vector<Rec>& a, std::vector<Rec>& tmp, std::size_t lo, std::size_t mid, std::size_t hi, Cost& c) { std::size_t i = lo, j = mid, k = lo;
    while (i < mid && j < hi) { c.cmp++; if (a[j].key < a[i].key) { c.inversions += (long)(mid - i); tmp[k++] = a[j++]; } else tmp[k++] = a[i++]; }                      // 동률이면 왼쪽 먼저(안정)
    while (i < mid) tmp[k++] = a[i++]; while (j < hi) tmp[k++] = a[j++]; for (std::size_t x = lo; x < hi; x++) a[x] = tmp[x]; }
void topDown(std::vector<Rec>& a, std::vector<Rec>& tmp, std::size_t lo, std::size_t hi, Cost& c) { if (hi - lo < 2) return; std::size_t mid = lo + (hi - lo) / 2; topDown(a, tmp, lo, mid, c); topDown(a, tmp, mid, hi, c); mergeRange(a, tmp, lo, mid, hi, c); }
void bottomUp(std::vector<Rec>& a, Cost& c) { std::vector<Rec> tmp(a.size()); for (std::size_t w = 1; w < a.size(); w *= 2) for (std::size_t lo = 0; lo + w < a.size(); lo += 2 * w) mergeRange(a, tmp, lo, lo + w, std::min(lo + 2 * w, a.size()), c); }
void natural(std::vector<Rec>& a, Cost& c) { std::vector<Rec> tmp(a.size()); for (;;) { std::vector<std::size_t> cuts{0}; for (std::size_t i = 1; i < a.size(); i++) if (a[i - 1].key > a[i].key) cuts.push_back(i); cuts.push_back(a.size()); if (cuts.size() <= 2) return;   // 오름차순 구간의 경계
        std::vector<std::size_t> next{0}; for (std::size_t r = 0; r + 1 < cuts.size(); r += 2) { if (r + 2 < cuts.size()) { mergeRange(a, tmp, cuts[r], cuts[r + 1], cuts[r + 2], c); next.push_back(cuts[r + 2]); } else next.push_back(cuts[r + 1]); } } }
long worstCase(long n) { if (n <= 1) return 0; long ceilLog = 0; while ((1L << ceilLog) < n) ceilLog++; return n * ceilLog - (1L << ceilLog) + 1; }
bool sameAsStable(const std::vector<Rec>& a, const std::vector<Rec>& ref) { if (a.size() != ref.size()) return false; for (std::size_t i = 0; i < a.size(); i++) if (a[i].key != ref[i].key || a[i].tag != ref[i].tag) return false; return true; }
int main() {
    std::mt19937 rng(33);
    for (int rep = 0; rep < 300; rep++) { int n = (int)(rng() % 131), range = 1 + (int)(rng() % 20); std::vector<Rec> base(n); for (int i = 0; i < n; i++) base[i] = {(int)(rng() % range), i};
        std::vector<Rec> ref = base; std::stable_sort(ref.begin(), ref.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; });
        std::vector<Rec> a = base, b = base, d = base, tmp(n); Cost ca, cb, cd; topDown(a, tmp, 0, a.size(), ca); bottomUp(b, cb); natural(d, cd); assert(sameAsStable(a, ref) && sameAsStable(b, ref) && sameAsStable(d, ref));            // ①
        assert(ca.cmp <= worstCase(n) && cb.cmp <= worstCase(n) + n); long inv = 0; for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) inv += base[i].key > base[j].key; assert(ca.inversions == inv && cb.inversions == inv && cd.inversions == inv); }   // ② ③
    for (int n = 1; n <= 130; n++) { std::vector<Rec> a(n); for (int i = 0; i < n; i++) a[i] = {i, i}; Cost c; std::vector<Rec> t(n); topDown(a, t, 0, a.size(), c); assert(c.cmp <= worstCase(n) && c.cmp >= (long)(n / 2) * (long)std::floor(std::log2((double)n)) - n);   // 정렬된 입력도 ~ (n/2)log n
        std::vector<Rec> s(n); for (int i = 0; i < n; i++) s[i] = {i, i}; Cost nc; natural(s, nc); assert(nc.cmp == 0); }
    { std::vector<Rec> two(100); for (int i = 0; i < 100; i++) two[i] = {i < 50 ? 2 * i : 2 * (i - 50) + 1, i}; std::vector<Rec> ref = two; std::stable_sort(ref.begin(), ref.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; }); Cost c; natural(two, c); assert(sameAsStable(two, ref) && c.cmp <= 99); }   // ④ 두 run
    { std::vector<Rec> sortedIn(1000); for (int i = 0; i < 1000; i++) sortedIn[i] = {i, i}; Cost c; natural(sortedIn, c); assert(c.cmp == 0);   // run 이 하나면 병합이 없다
      std::vector<Rec> e; Cost z; std::vector<Rec> tt; topDown(e, tt, 0, 0, z); bottomUp(e, z); natural(e, z); assert(z.cmp == 0); std::vector<Rec> one = {{5, 0}}; bottomUp(one, z); natural(one, z); assert(one[0].key == 5 && z.cmp == 0); }
    { int n = 200000; std::vector<Rec> big(n); for (int i = 0; i < n; i++) big[i] = {(int)(rng() % 100000), i}; std::vector<Rec> ref = big; std::stable_sort(ref.begin(), ref.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; }); std::vector<Rec> a = big, tmp(n); Cost c; topDown(a, tmp, 0, a.size(), c); assert(sameAsStable(a, ref) && c.cmp <= worstCase(n));   // ⑤
      std::vector<Rec> rev(5000); for (int i = 0; i < 5000; i++) rev[i] = {5000 - i, i}; Cost r; bottomUp(rev, r); assert(std::is_sorted(rev.begin(), rev.end(), [](const Rec& x, const Rec& y) { return x.key < y.key; }) && r.inversions == 5000L * 4999 / 2); }
    std::cout << "MergeSort: top-down, bottom-up and natural merge sorts matched std::stable_sort on 300 random arrays, stayed within the worst-case comparison bound n*ceil(log2 n) - 2^ceil(log2 n) + 1, and the inversions counted while merging equalled the brute-force count (also n(n-1)/2 for reversed input)" << std::endl; return 0;
}
// Time Complexity: O(N log N) (최선·평균·최악)
// Space Complexity: O(N)
```
## QuickSort()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 퀵 정렬(Quick Sort): 기준 원소(pivot)를 골라 작은 쪽과 큰 쪽으로 분할(partition)하고 양쪽을 재귀로 정렬한다. 제자리(in-place)이고 평균 O(n log n) 이지만 기준이 계속 최솟값·최댓값이면 분할이 n−1 : 0 으로 치우쳐 O(n²) 가 된다 — 첫 원소를 기준으로 삼으면 이미 정렬된 입력이 정확히 n(n−1)/2 번 비교하는 최악이다. 해법: 무작위 기준, 세 값의 중앙값(median of three), 그리고 재귀 깊이가 한계를 넘으면 힙 정렬로 넘기는 인트로 정렬.
// 분할 방식: 로무토(Lomuto, 마지막/첫 원소 기준, 단순) · 호어(Hoare, 양끝에서 조여 오며 교환이 적음) · 3분할(< = > 로 나누는 네덜란드 국기, 같은 키가 많을 때 필수 — 같은 키만 있으면 로무토는 O(n²) 이고 3분할은 O(n)). 재귀 깊이는 작은 쪽만 재귀하고 큰 쪽은 반복으로 처리하면 ⌊log₂ n⌋ 이하로 보장된다. 퀵 셀렉트는 분할 후 k 번째가 있는 쪽 하나만 쫓아가 평균 O(n) 으로 k 번째 원소를 찾는다.
// 검증: ① 로무토(첫 원소)·호어(무작위)·세 값 중앙값·3분할이 모든 무작위 입력(중복 많음)에서 정렬 결과가 std::sort 와 같음 ② 첫 원소 기준 로무토에 정렬된 입력을 주면 비교가 정확히 n(n−1)/2, 무작위·중앙값 기준은 같은 입력에서 ≤ 3n log₂ n ③ 같은 키만 있는 입력에서 로무토는 n(n−1)/2, 3분할은 ≤ 2n ④ 작은 쪽 먼저 재귀하면 병적 입력(첫 원소 기준 + 정렬 입력 5000)에서도 최대 깊이 ≤ log₂ n + 1 ⑤ 인트로 정렬이 정렬된 입력 10 만에서 힙 정렬 폴백이 작동하며 비교 ≤ 80n(깊이 한계 2log₂n 번의 분할 ≈ 32n + 힙 정렬 비교 상한 2m⌈log₂(m+1)⌉ ≈ 34n; 순수 첫 원소 기준이면 n(n−1)/2 ≈ 5·10⁹) ⑥ 퀵 셀렉트 결과가 std::nth_element 와 같고 무작위 10 만 입력에서 비교 ≤ 8n.
struct Counters { long cmp = 0; int depth = 0, maxDepth = 0, fallbacks = 0; };
int lomuto(std::vector<int>& a, int lo, int hi, Counters& c) { int p = a[lo], i = lo; for (int j = lo + 1; j <= hi; j++) { c.cmp++; if (a[j] < p) std::swap(a[++i], a[j]); } std::swap(a[lo], a[i]); return i; }   // 첫 원소 기준
void quickLomuto(std::vector<int>& a, int lo, int hi, Counters& c) { while (lo < hi) { c.depth++; c.maxDepth = std::max(c.maxDepth, c.depth); int p = lomuto(a, lo, hi, c); if (p - lo < hi - p) { quickLomuto(a, lo, p - 1, c); lo = p + 1; } else { quickLomuto(a, p + 1, hi, c); hi = p - 1; } c.depth--; } }   // 작은 쪽 먼저 재귀
int hoare(std::vector<int>& a, int lo, int hi, Counters& c) { int p = a[lo + (hi - lo) / 2], i = lo - 1, j = hi + 1; for (;;) { do { i++; c.cmp++; } while (a[i] < p); do { j--; c.cmp++; } while (a[j] > p); if (i >= j) return j; std::swap(a[i], a[j]); } }
void quickHoareRandom(std::vector<int>& a, int lo, int hi, Counters& c, std::mt19937& rng) { if (lo >= hi) return; std::swap(a[lo + (hi - lo) / 2], a[lo + (int)(rng() % (hi - lo + 1))]); int p = hoare(a, lo, hi, c); quickHoareRandom(a, lo, p, c, rng); quickHoareRandom(a, p + 1, hi, c, rng); }
void quickMedian3(std::vector<int>& a, int lo, int hi, Counters& c) { while (lo < hi) { int mid = lo + (hi - lo) / 2; if (a[mid] < a[lo]) std::swap(a[mid], a[lo]); if (a[hi] < a[lo]) std::swap(a[hi], a[lo]); if (a[hi] < a[mid]) std::swap(a[hi], a[mid]); c.cmp += 3; std::swap(a[lo], a[mid]);   // 중앙값을 맨 앞으로
        int p = lomuto(a, lo, hi, c); if (p - lo < hi - p) { quickMedian3(a, lo, p - 1, c); lo = p + 1; } else { quickMedian3(a, p + 1, hi, c); hi = p - 1; } } }
void quick3way(std::vector<int>& a, int lo, int hi, Counters& c) { while (lo < hi) { int p = a[lo + (hi - lo) / 2], lt = lo, i = lo, gt = hi; while (i <= gt) { c.cmp++; if (a[i] < p) std::swap(a[lt++], a[i++]); else if (a[i] > p) std::swap(a[i], a[gt--]); else i++; }
        if (lt - lo < hi - gt) { quick3way(a, lo, lt - 1, c); lo = gt + 1; } else { quick3way(a, gt + 1, hi, c); hi = lt - 1; } } }
void introsort(std::vector<int>& a, int lo, int hi, int depthLeft, Counters& c) { while (lo < hi) { if (depthLeft-- == 0) { c.fallbacks++; std::make_heap(a.begin() + lo, a.begin() + hi + 1); std::sort_heap(a.begin() + lo, a.begin() + hi + 1); c.cmp += 2L * (hi - lo + 1) * (long)std::ceil(std::log2((double)(hi - lo + 2))); return; }
        int p = lomuto(a, lo, hi, c); if (p - lo < hi - p) { introsort(a, lo, p - 1, depthLeft, c); lo = p + 1; } else { introsort(a, p + 1, hi, depthLeft, c); hi = p - 1; } } }                    // 첫 원소 기준이라도 깊이 한계로 방어
int quickSelect(std::vector<int> a, int k, Counters& c, std::mt19937& rng) { int lo = 0, hi = (int)a.size() - 1; while (lo < hi) { std::swap(a[lo], a[lo + (int)(rng() % (hi - lo + 1))]); int p = lomuto(a, lo, hi, c); if (k == p) return a[p]; if (k < p) hi = p - 1; else lo = p + 1; } return a[lo]; }
int main() {
    std::mt19937 rng(34);
    for (int rep = 0; rep < 400; rep++) { int n = (int)(rng() % 120), range = 1 + (int)(rng() % 15); std::vector<int> base(n); for (int& x : base) x = (int)(rng() % range); std::vector<int> ref = base; std::sort(ref.begin(), ref.end());             // ①
        std::vector<int> a = base, b = base, d = base, e = base; Counters c1, c2, c3, c4; quickLomuto(a, 0, n - 1, c1); quickHoareRandom(b, 0, n - 1, c2, rng); quickMedian3(d, 0, n - 1, c3); quick3way(e, 0, n - 1, c4); assert(a == ref && b == ref && d == ref && e == ref); }
    for (int n : {10, 100, 1000, 3000}) { std::vector<int> sorted(n); std::iota(sorted.begin(), sorted.end(), 0); std::vector<int> a = sorted, d = sorted, e = sorted; Counters c1, c2, c3; quickLomuto(a, 0, n - 1, c1); assert(c1.cmp == (long)n * (n - 1) / 2);           // ② 첫 원소 기준 + 정렬된 입력 = 정확히 n(n-1)/2
        quickMedian3(d, 0, n - 1, c2); quick3way(e, 0, n - 1, c3); double nlogn = n * std::log2((double)n); assert(c2.cmp <= 3 * nlogn && c3.cmp <= 3 * nlogn); std::vector<int> r = sorted; std::shuffle(r.begin(), r.end(), rng); Counters c4; quickHoareRandom(r, 0, n - 1, c4, rng); assert(c4.cmp <= 3 * nlogn && std::is_sorted(r.begin(), r.end())); }
    { int n = 2000; std::vector<int> same(n, 7); Counters c1, c2; std::vector<int> a = same, b = same; quickLomuto(a, 0, n - 1, c1); quick3way(b, 0, n - 1, c2); assert(c1.cmp == (long)n * (n - 1) / 2 && c2.cmp <= 2 * n); }               // ③
    { int n = 5000; std::vector<int> sorted(n); std::iota(sorted.begin(), sorted.end(), 0); Counters c; quickLomuto(sorted, 0, n - 1, c); assert(c.maxDepth <= (int)std::log2((double)n) + 1 && c.cmp == (long)n * (n - 1) / 2); }   // ④ 작은 쪽 먼저: 깊이 ≤ log n
    { int n = 100000; std::vector<int> sorted(n); std::iota(sorted.begin(), sorted.end(), 0); Counters c; introsort(sorted, 0, n - 1, 2 * (int)std::log2((double)n), c); assert(std::is_sorted(sorted.begin(), sorted.end()) && c.fallbacks > 0 && c.cmp <= 80L * n); }   // ⑤
    { int n = 100000; std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 1000000); std::vector<int> sorted = v; std::sort(sorted.begin(), sorted.end()); for (int k : {0, 1, n / 2, n - 2, n - 1}) { Counters c; assert(quickSelect(v, k, c, rng) == sorted[k] && c.cmp <= 8L * n); }     // ⑥
      std::vector<int> small = {5, 1, 4}; Counters c; for (int k = 0; k < 3; k++) assert(quickSelect(small, k, c, rng) == (std::vector<int>{1, 4, 5})[k]); }
    std::cout << "QuickSort: Lomuto, randomized Hoare, median-of-three and three-way variants matched std::sort on 400 random arrays; first-element pivots made exactly n(n-1)/2 comparisons on sorted input while median-of-three stayed within 3n log n, all-equal keys cost n(n-1)/2 for Lomuto but at most 2n for three-way, recursing into the smaller side kept depth <= log2 n + 1, introsort fell back to heapsort on adversarial input, and quickselect agreed with sorting" << std::endl; return 0;
}
// Time Complexity: 평균 O(N log N), 최악 O(N²) (인트로 정렬은 O(N log N) 보장)
// Space Complexity: O(log N) (작은 쪽 먼저 재귀)
```
## StablePartition()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <vector>

// 안정적 분할(Stable Partition): 조건을 만족하는 원소들을 앞으로, 아닌 원소들을 뒤로 모으되 두 그룹 안에서 원래의 상대 순서를 유지한다. 반환값은 경계(조건을 만족하는 개수)다. 안정성이 필요 없다면 호어 방식의 양끝 교환(교환 ≤ min(참 개수, 거짓 개수))이나 로무토 방식이 훨씬 간단하고 빠르며 O(n) 시간·O(1) 공간이다 — 퀵 정렬의 분할 단계가 이것이다.
// 안정적 분할 방법: (A) 임시 버퍼에 거짓 원소를 따로 모아 두고 참 원소를 앞으로 압축한 뒤 버퍼를 뒤에 붙인다 — O(n) 시간·O(n) 공간. (B) 제자리 분할 정복: 왼쪽 반과 오른쪽 반을 각각 분할한 뒤 [왼쪽 거짓 | 오른쪽 참] 을 회전(rotate)으로 맞바꾼다 — O(n log n) 시간·O(log n) 공간. 회전은 세 번 뒤집기로 하며 구간 길이만큼의 이동을 쓴다. 이 구조는 std::stable_partition 이 메모리가 모자랄 때 쓰는 방식이기도 하다.
// 검증: ① (A)·(B) 가 std::stable_partition 과 완전히 같음(값과 출처 태그) 이며 경계 인덱스가 참의 개수 ② 두 그룹이 각각 원래 순서 유지 ③ 불안정한 호어/로무토 분할은 멀티셋이 같고 앞은 모두 참·뒤는 모두 거짓이며 호어 교환 ≤ min(참, 거짓) ④ (B) 의 이동 횟수 ≤ n⌈log₂ n⌉ ⑤ 전부 참·전부 거짓·빈 입력·원소 1개 경계.
struct Rec { int key, tag; };
template <class Pred> std::size_t partitionBuffer(std::vector<Rec>& a, Pred p) { std::vector<Rec> rest; std::size_t w = 0; for (const Rec& r : a) { if (p(r)) a[w++] = r; else rest.push_back(r); } std::copy(rest.begin(), rest.end(), a.begin() + w); return w; }
long rotateMoves = 0;
void rotateRange(std::vector<Rec>& a, std::size_t lo, std::size_t mid, std::size_t hi) { std::reverse(a.begin() + lo, a.begin() + mid); std::reverse(a.begin() + mid, a.begin() + hi); std::reverse(a.begin() + lo, a.begin() + hi); rotateMoves += (long)(hi - lo); }   // 세 번 뒤집기: [mid,hi) 가 앞으로
template <class Pred> std::size_t partitionInPlace(std::vector<Rec>& a, std::size_t lo, std::size_t hi, Pred p) {                                    // 반환: 참의 끝 위치(절대 인덱스)
    if (hi - lo == 0) return lo; if (hi - lo == 1) return p(a[lo]) ? lo + 1 : lo; std::size_t mid = lo + (hi - lo) / 2; std::size_t leftEnd = partitionInPlace(a, lo, mid, p), rightEnd = partitionInPlace(a, mid, hi, p);   // [참 | 거짓] [참 | 거짓]
    std::size_t rightTrueStart = mid; if (leftEnd < mid && rightTrueStart < rightEnd) rotateRange(a, leftEnd, mid, rightEnd); return leftEnd + (rightEnd - mid); }
template <class Pred> std::size_t hoarePartition(std::vector<Rec>& a, Pred p, long& swaps) { std::size_t i = 0, j = a.size(); for (;;) { while (i < j && p(a[i])) i++; while (i < j && !p(a[j - 1])) j--; if (i >= j) return i; std::swap(a[i], a[j - 1]); swaps++; i++; j--; } }
int main() {
    std::mt19937 rng(35);
    for (int rep = 0; rep < 600; rep++) { int n = (int)(rng() % 80), m = 2 + (int)(rng() % 5); std::vector<Rec> base(n); for (int i = 0; i < n; i++) base[i] = {(int)(rng() % 50), i}; auto pred = [m](const Rec& r) { return r.key % m == 0; };
        std::vector<Rec> ref = base; auto bound = std::stable_partition(ref.begin(), ref.end(), pred); std::size_t cut = (std::size_t)(bound - ref.begin()); std::size_t trues = (std::size_t)std::count_if(base.begin(), base.end(), pred); assert(cut == trues);
        std::vector<Rec> a = base, b = base; rotateMoves = 0; std::size_t ca = partitionBuffer(a, pred), cb = partitionInPlace(b, 0, b.size(), pred); assert(ca == cut && cb == cut);                      // ①
        for (int i = 0; i < n; i++) assert(a[i].tag == ref[i].tag && b[i].tag == ref[i].tag); for (int g = 0; g < 2; g++) { int last = -1; for (std::size_t i = g ? cut : 0; i < (g ? (std::size_t)n : cut); i++) { assert(b[i].tag > last); last = b[i].tag; } }   // ②
        if (n > 1) assert(rotateMoves <= (long)n * (long)std::ceil(std::log2((double)n)));                                                                                                       // ④
        std::vector<Rec> h = base; long sw = 0; std::size_t ch = hoarePartition(h, pred, sw); assert(ch == cut); for (std::size_t i = 0; i < ch; i++) assert(pred(h[i])); for (std::size_t i = ch; i < h.size(); i++) assert(!pred(h[i]));
        std::vector<int> t1, t2; for (auto& r : base) t1.push_back(r.tag); for (auto& r : h) t2.push_back(r.tag); std::sort(t1.begin(), t1.end()); std::sort(t2.begin(), t2.end()); assert(t1 == t2 && sw <= (long)std::min(cut, (std::size_t)n - cut)); }   // ③ 멀티셋 + 교환 한계
    for (int pass = 0; pass < 2; pass++) { for (int n : {0, 1, 2, 7}) { std::vector<Rec> a(n); for (int i = 0; i < n; i++) a[i] = {i, i}; auto all = [pass](const Rec&) { return pass == 0; }; std::vector<Rec> b = a; std::size_t c1 = partitionBuffer(a, all), c2 = partitionInPlace(b, 0, b.size(), all); long sw = 0; std::vector<Rec> h = a; std::size_t c3 = hoarePartition(h, all, sw);   // ⑤
            assert(c1 == (pass == 0 ? (std::size_t)n : 0) && c2 == c1 && c3 == c1 && sw == 0); for (int i = 0; i < n; i++) assert(a[i].tag == i && b[i].tag == i); } }
    std::cout << "StablePartition: the buffer-based and in-place rotate-based partitions matched std::stable_partition exactly (values and original order within both groups) on 600 random arrays, rotation work stayed within n*ceil(log2 n), and the unstable Hoare partition preserved the multiset with at most min(true, false) swaps" << std::endl; return 0;
}
// Time Complexity: 버퍼 방식 O(N), 제자리 방식 O(N log N), 호어(불안정) O(N)
// Space Complexity: 버퍼 O(N), 제자리 O(log N), 호어 O(1)
```

# Part 5. 투 포인터
## TwoPointers()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 투 포인터(Two Pointers): 배열 위에 인덱스 두 개를 두고 규칙에 따라 움직이며 O(n²) 후보를 O(n) 으로 줄이는 기법이다. 대표 형태 셋: (1) 양끝에서 안쪽으로 조여 오기(정렬된 배열의 두 수의 합, 가장 많이 담는 물통) — 어느 쪽을 움직여도 되는지 단조성으로 증명되어 버리는 후보에 정답이 없다. (2) 읽기/쓰기 포인터(제자리 중복 제거, 0 을 뒤로 보내기) — 읽는 쪽이 항상 쓰는 쪽보다 앞서거나 같다. (3) 두 배열을 각각 따라가기(정렬된 두 배열의 병합·교집합).
// 정렬 후 세 수의 합(3Sum)은 한 수를 고정하고 나머지에 양끝 조이기를 적용해 O(n²) 이고 중복 조합은 같은 값을 건너뛰어 제거한다. 빗물 받기(trapping rain water)는 양끝에서 더 낮은 쪽을 움직이며 그쪽의 최대 높이로 고인 물을 정한다 — 접두/접미 최댓값 배열 두 개를 쓰는 방법과 같은 답을 O(1) 공간으로 얻는다. 포인터의 총 이동 횟수가 n 이하임을 세어 선형임을 확인한다.
// 검증: ① 두 수의 합(정렬 배열)이 무차별 O(n²) 와 존재 여부·쌍 모두 일치, 포인터 이동 ≤ n ② 가장 많이 담는 물통이 무차별 최댓값과 같음 ③ 3Sum 이 무차별(집합) 결과와 같고 중복 조합 없음 ④ 빗물 받기 투 포인터 == 접두/접미 최댓값 방식 == 무차별 ⑤ 읽기/쓰기 포인터: 중복 제거(std::unique 와 같음), 0 이동(std::stable_partition 과 같음, 상대 순서 유지) ⑥ 정렬된 두 배열의 병합·교집합(std::merge, std::set_intersection 과 같음) ⑦ 빈 입력·원소 1개.
bool twoSumSorted(const std::vector<int>& a, int target, std::pair<int, int>& out, long& moves) { int i = 0, j = (int)a.size() - 1; while (i < j) { long s = (long)a[i] + a[j]; if (s == target) { out = {i, j}; return true; } if (s < target) i++; else j--; moves++; } return false; }
long maxArea(const std::vector<int>& h, long& moves) { int i = 0, j = (int)h.size() - 1; long best = 0; while (i < j) { best = std::max(best, (long)(j - i) * std::min(h[i], h[j])); if (h[i] < h[j]) i++; else j--; moves++; } return best; }
std::set<std::vector<int>> threeSum(std::vector<int> a, std::vector<std::vector<int>>& listed) { std::sort(a.begin(), a.end()); std::set<std::vector<int>> res; for (int i = 0; i + 2 < (int)a.size(); i++) { if (i > 0 && a[i] == a[i - 1]) continue; int l = i + 1, r = (int)a.size() - 1;
        while (l < r) { long s = (long)a[i] + a[l] + a[r]; if (s == 0) { listed.push_back({a[i], a[l], a[r]}); res.insert(listed.back()); int lv = a[l], rv = a[r]; while (l < r && a[l] == lv) l++; while (l < r && a[r] == rv) r--; } else if (s < 0) l++; else r--; } } return res; }
long trapTwoPointers(const std::vector<int>& h) { int i = 0, j = (int)h.size() - 1, lmax = 0, rmax = 0; long water = 0; while (i < j) { if (h[i] < h[j]) { lmax = std::max(lmax, h[i]); water += lmax - h[i]; i++; } else { rmax = std::max(rmax, h[j]); water += rmax - h[j]; j--; } } return water; }
long trapPrefixSuffix(const std::vector<int>& h) { int n = (int)h.size(); std::vector<int> L(n), R(n); long water = 0; for (int i = 0; i < n; i++) L[i] = std::max(i ? L[i - 1] : 0, h[i]); for (int i = n - 1; i >= 0; i--) R[i] = std::max(i + 1 < n ? R[i + 1] : 0, h[i]); for (int i = 0; i < n; i++) water += std::min(L[i], R[i]) - h[i]; return water; }
long trapBrute(const std::vector<int>& h) { long water = 0; for (int i = 0; i < (int)h.size(); i++) { int l = 0, r = 0; for (int j = 0; j <= i; j++) l = std::max(l, h[j]); for (int j = i; j < (int)h.size(); j++) r = std::max(r, h[j]); water += std::min(l, r) - h[i]; } return water; }
int dedupe(std::vector<int>& a) { if (a.empty()) return 0; int w = 1; for (int r = 1; r < (int)a.size(); r++) if (a[r] != a[w - 1]) a[w++] = a[r]; return w; }
int moveZeros(std::vector<int>& a) { int w = 0; for (int r = 0; r < (int)a.size(); r++) if (a[r] != 0) a[w++] = a[r]; int nonzero = w; while (w < (int)a.size()) a[w++] = 0; return nonzero; }
int main() {
    std::mt19937 rng(36);
    for (int rep = 0; rep < 600; rep++) { int n = (int)(rng() % 20); std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 41) - 20; std::sort(a.begin(), a.end()); int target = (int)(rng() % 41) - 20;                           // ①
        std::pair<int, int> p; long moves = 0; bool got = twoSumSorted(a, target, p, moves); bool want = false; for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) want |= a[i] + a[j] == target; assert(got == want && moves <= n); if (got) assert(p.first < p.second && a[p.first] + a[p.second] == target); }
    for (int rep = 0; rep < 600; rep++) { int n = (int)(rng() % 25); std::vector<int> h(n); for (int& x : h) x = (int)(rng() % 15); long moves = 0, best = maxArea(h, moves), want = 0; for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) want = std::max(want, (long)(j - i) * std::min(h[i], h[j])); assert(best == want && moves <= std::max(0, n - 1)); }   // ②
    for (int rep = 0; rep < 400; rep++) { int n = (int)(rng() % 16); std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 9) - 4; std::vector<std::vector<int>> listed; auto got = threeSum(a, listed); std::set<std::vector<int>> want;                  // ③
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) for (int k = j + 1; k < n; k++) if (a[i] + a[j] + a[k] == 0) { std::vector<int> t = {a[i], a[j], a[k]}; std::sort(t.begin(), t.end()); want.insert(t); } assert(got == want && listed.size() == got.size()); }
    for (int rep = 0; rep < 600; rep++) { int n = (int)(rng() % 30); std::vector<int> h(n); for (int& x : h) x = (int)(rng() % 10); long a = trapTwoPointers(h), b = trapPrefixSuffix(h), c = trapBrute(h); assert(a == b && b == c); }                    // ④
    for (int rep = 0; rep < 400; rep++) { int n = (int)(rng() % 30); std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 6); std::sort(a.begin(), a.end()); std::vector<int> r = a; r.erase(std::unique(r.begin(), r.end()), r.end()); std::vector<int> d = a; int k = dedupe(d); assert(k == (int)r.size() && std::equal(r.begin(), r.end(), d.begin()));   // ⑤
        std::vector<int> z(n); for (int& x : z) x = (int)(rng() % 3); std::vector<int> zs = z; std::stable_partition(zs.begin(), zs.end(), [](int x) { return x != 0; }); std::vector<int> zm = z; int nz = moveZeros(zm); assert(zm == zs && nz == (int)std::count_if(z.begin(), z.end(), [](int x) { return x != 0; })); }
    for (int rep = 0; rep < 400; rep++) { std::vector<int> a((std::size_t)(rng() % 15)), b((std::size_t)(rng() % 15)); for (int& x : a) x = (int)(rng() % 12); for (int& x : b) x = (int)(rng() % 12); std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end());   // ⑥
        std::vector<int> m, in; std::size_t i = 0, j = 0; while (i < a.size() || j < b.size()) { if (j >= b.size() || (i < a.size() && a[i] <= b[j])) m.push_back(a[i++]); else m.push_back(b[j++]); }
        i = j = 0; while (i < a.size() && j < b.size()) { if (a[i] < b[j]) i++; else if (b[j] < a[i]) j++; else { in.push_back(a[i]); i++; j++; } }
        std::vector<int> rm(a.size() + b.size()), ri; std::merge(a.begin(), a.end(), b.begin(), b.end(), rm.begin()); std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(ri)); assert(m == rm && in == ri); }
    { std::vector<int> e; std::pair<int, int> p; long mv = 0; assert(!twoSumSorted(e, 0, p, mv) && maxArea(e, mv) == 0 && trapTwoPointers(e) == 0 && dedupe(e) == 0 && moveZeros(e) == 0); std::vector<int> one = {5}; assert(!twoSumSorted(one, 10, p, mv) && maxArea(one, mv) == 0 && dedupe(one) == 1); }   // ⑦
    std::cout << "TwoPointers: opposite-end squeezing (two-sum, container, 3Sum, trapping water) agreed with brute force on thousands of random arrays using at most n pointer moves, read/write pointers matched std::unique and std::stable_partition, and two-array walks matched std::merge and std::set_intersection" << std::endl; return 0;
}
// Time Complexity: O(N) (3Sum 은 O(N²))
// Space Complexity: O(1)
```
## SlidingWindow()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

// 슬라이딩 윈도우(Sliding Window): 연속 구간 [l, r) 을 유지하며 r 을 늘려 원소를 넣고 조건이 깨지거나 충족되면 l 을 늘려 뺀다. 두 포인터가 각각 n 번 이상 움직이지 않으므로 전체 O(n) 이다 — "구간마다 처음부터 다시 계산하는" O(n²)·O(nk) 를 윈도우 내용만 갱신(들어오는 원소 더하기, 나가는 원소 빼기)해 줄인다.
// 두 종류: (1) 고정 크기 k — 구간 합의 최댓값처럼 한 칸 밀 때 하나 넣고 하나 빼서 합을 O(1) 에 갱신, (2) 가변 크기 — 조건을 만족하는 가장 긴/가장 짧은 구간(최대 k 종류의 서로 다른 값을 가진 가장 긴 구간, 합이 목표 이상인 가장 짧은 구간(양수 원소), 중복 없는 가장 긴 부분 문자열, t 의 모든 문자를 포함하는 최소 윈도우). 가변 윈도우가 성립하려면 조건이 단조적이어야 한다(구간을 넓히면 더 쉽게 만족/깨짐). 음수가 섞인 합 조건에는 단조성이 없어 이 기법을 쓸 수 없다(접두사 합 + 해시를 쓴다).
// 검증: ① 고정 크기 최대 합이 무차별 O(nk) 와 같음 ② 서로 다른 값 최대 k 종류의 가장 긴 구간이 무차별 O(n²) 와 같음 ③ 합 ≥ 목표인 가장 짧은 구간(양수)이 무차별과 같음 ④ 중복 없는 가장 긴 부분 문자열과 최소 윈도우 부분 문자열(t 포함)이 무차별과 같음 ⑤ 모든 변형에서 포인터 이동 합이 ≤ 2n ⑥ 빈 입력·k = 0·k > n 경계.
long maxWindowSum(const std::vector<int>& a, int k) { if (k <= 0 || k > (int)a.size()) return LONG_MIN; long cur = 0, best = LONG_MIN; for (int i = 0; i < (int)a.size(); i++) { cur += a[i]; if (i >= k) cur -= a[i - k]; if (i >= k - 1) best = std::max(best, cur); } return best; }
int longestKDistinct(const std::vector<int>& a, int k, long& moves) { if (k <= 0) return 0; std::unordered_map<int, int> cnt; int l = 0, best = 0; for (int r = 0; r < (int)a.size(); r++) { cnt[a[r]]++; moves++; while ((int)cnt.size() > k) { if (--cnt[a[l]] == 0) cnt.erase(a[l]); l++; moves++; } best = std::max(best, r - l + 1); } return best; }
int shortestAtLeast(const std::vector<int>& a, long target, long& moves) { long sum = 0; int l = 0, best = INT_MAX; for (int r = 0; r < (int)a.size(); r++) { sum += a[r]; moves++; while (sum >= target && l <= r) { best = std::min(best, r - l + 1); sum -= a[l++]; moves++; } } return best == INT_MAX ? 0 : best; }
int longestUnique(const std::string& s, long& moves) { std::vector<int> last(256, -1); int l = 0, best = 0; for (int r = 0; r < (int)s.size(); r++) { unsigned char c = (unsigned char)s[r]; if (last[c] >= l) l = last[c] + 1; last[c] = r; moves++; best = std::max(best, r - l + 1); } return best; }
std::string minWindow(const std::string& s, const std::string& t, long& moves) { if (t.empty()) return ""; std::vector<int> need(256, 0); int missing = (int)t.size(); for (unsigned char c : t) need[c]++; int l = 0, bestL = 0, bestLen = INT_MAX;
    for (int r = 0; r < (int)s.size(); r++) { if (need[(unsigned char)s[r]]-- > 0) missing--; moves++; while (missing == 0) { if (r - l + 1 < bestLen) { bestLen = r - l + 1; bestL = l; } if (++need[(unsigned char)s[l]] > 0) missing++; l++; moves++; } } return bestLen == INT_MAX ? "" : s.substr(bestL, bestLen); }
int main() {
    std::mt19937 rng(37);
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 25); std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 41) - 20; int k = (int)(rng() % 8); long want = LONG_MIN; for (int i = 0; k > 0 && i + k <= n; i++) { long s = 0; for (int j = 0; j < k; j++) s += a[i + j]; want = std::max(want, s); } assert(maxWindowSum(a, k) == want); }   // ① ⑥
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 30); std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 6); int k = (int)(rng() % 5); long moves = 0; int got = longestKDistinct(a, k, moves); int want = 0;                         // ②
        for (int i = 0; i < n; i++) { std::map<int, int> seen; for (int j = i; j < n; j++) { seen[a[j]]++; if ((int)seen.size() <= k) want = std::max(want, j - i + 1); } } assert(got == want && moves <= 2L * n); }
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 30); std::vector<int> a(n); for (int& x : a) x = 1 + (int)(rng() % 9); long target = (long)(rng() % 60) + 1; long moves = 0; int got = shortestAtLeast(a, target, moves); int want = 0;             // ③ 양수 원소
        for (int i = 0; i < n; i++) { long s = 0; for (int j = i; j < n; j++) { s += a[j]; if (s >= target) { if (!want || j - i + 1 < want) want = j - i + 1; break; } } } assert(got == want && moves <= 2L * n); }
    for (int rep = 0; rep < 600; rep++) { int n = (int)(rng() % 30); std::string s; for (int i = 0; i < n; i++) s += (char)('a' + rng() % 5); long moves = 0; int got = longestUnique(s, moves); int want = 0; for (int i = 0; i < n; i++) { std::string seen; for (int j = i; j < n; j++) { if (seen.find(s[j]) != std::string::npos) break; seen += s[j]; } want = std::max(want, (int)seen.size()); } assert(got == want && moves == n);       // ④
        std::string t; int tn = (int)(rng() % 4); for (int i = 0; i < tn; i++) t += (char)('a' + rng() % 5); long m2 = 0; std::string w = minWindow(s, t, m2); std::string bestStr; bool found = false;
        auto covers = [&](const std::string& sub) { std::vector<int> need(256, 0); for (unsigned char c : t) need[c]++; for (unsigned char c : sub) need[c]--; for (int x : need) if (x > 0) return false; return true; };
        for (int i = 0; i < n && !t.empty(); i++) for (int j = i; j < n; j++) { std::string sub = s.substr(i, j - i + 1); if (covers(sub) && (!found || sub.size() < bestStr.size())) { bestStr = sub; found = true; } }
        assert(w.size() == bestStr.size() && (w.empty() || covers(w)) && m2 <= 2L * n); }
    { std::vector<int> e; long mv = 0; assert(maxWindowSum(e, 1) == LONG_MIN && longestKDistinct(e, 2, mv) == 0 && shortestAtLeast(e, 5, mv) == 0 && longestUnique("", mv) == 0 && minWindow("", "a", mv).empty() && minWindow("abc", "", mv).empty());     // ⑥
      assert(maxWindowSum(std::vector<int>{1, 2, 3}, 4) == LONG_MIN && maxWindowSum(std::vector<int>{1, 2, 3}, 0) == LONG_MIN && minWindow("ADOBECODEBANC", "ABC", mv) == "BANC" && longestUnique("abcabcbb", mv) == 3); }
    std::cout << "SlidingWindow: fixed windows (max sum), variable windows (at most k distinct values, shortest sum >= target, longest unique substring, minimum window covering t) all matched brute-force searches on thousands of random inputs, and each pointer pair moved at most 2n times in total" << std::endl; return 0;
}
// Time Complexity: O(N) (고정 윈도우는 O(N), 가변 윈도우는 포인터 이동 합 ≤ 2N)
// Space Complexity: O(1) ~ O(윈도우 안 서로 다른 값의 수)
```
## PrefixSum()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <unordered_map>
#include <vector>

// 접두사 합(Prefix Sum): P[i] = a[0] + … + a[i−1] (P[0] = 0) 을 한 번 O(n) 에 만들어 두면 구간 합 sum(l, r) = P[r] − P[l] 이 O(1) 이다(반열린 구간 [l, r)). P[0] = 0 이라는 "빈 접두사"를 두면 l = 0 인 경우의 특별 처리가 사라진다. 변경이 없는 정적 배열에 질의가 많을 때 쓰고, 값이 바뀌면 O(n) 으로 다시 만들어야 하므로 갱신이 잦으면 펜윅 트리·세그먼트 트리를 쓴다.
// 확장: 2차원 접두사 합(합 영역 테이블) S[i][j] = 왼쪽 위 i×j 사각형의 합, 사각형 질의는 포함–배제로 O(1): S[r2][c2] − S[r1][c2] − S[r2][c1] + S[r1][c1]. 접두사 XOR 도 같은 구조다. 합이 정확히 K 인 부분배열의 개수는 음수가 섞여도 "P[r] − P[l] = K ⇔ P[l] = P[r] − K" 를 해시 맵으로 세어 O(n) 에 구한다(윈도우 기법은 음수에 쓸 수 없다). 오버플로를 피하려면 합에 64 비트를 쓴다.
// 검증: ① 1차원 구간 합이 무차별 합과 모든 (l, r) 에서 일치(빈 구간 0 포함) ② 2차원 사각형 합이 무차별과 일치(모든 사각형, 작은 격자 전수) ③ 접두사 XOR 구간 질의 ④ 합이 K 인 부분배열 개수(음수·0 포함)가 무차별과 같음 ⑤ 큰 값(2³¹ 근처)에서도 64 비트라 정확 ⑥ 빈 배열·원소 1개.
struct Prefix { std::vector<long long> P; explicit Prefix(const std::vector<int>& a) : P(a.size() + 1, 0) { for (std::size_t i = 0; i < a.size(); i++) P[i + 1] = P[i] + a[i]; } long long sum(std::size_t l, std::size_t r) const { return P[r] - P[l]; } };
struct Prefix2D { std::vector<std::vector<long long>> S; Prefix2D(const std::vector<std::vector<int>>& g) : S(g.size() + 1, std::vector<long long>(g.empty() ? 1 : g[0].size() + 1, 0)) {
        for (std::size_t i = 0; i < g.size(); i++) for (std::size_t j = 0; j < g[0].size(); j++) S[i + 1][j + 1] = g[i][j] + S[i][j + 1] + S[i + 1][j] - S[i][j]; }
    long long sum(std::size_t r1, std::size_t c1, std::size_t r2, std::size_t c2) const { return S[r2][c2] - S[r1][c2] - S[r2][c1] + S[r1][c1]; } };
long long countSubarraysWithSum(const std::vector<int>& a, long long K) { std::unordered_map<long long, long long> seen; seen[0] = 1; long long cur = 0, count = 0; for (int x : a) { cur += x; auto it = seen.find(cur - K); if (it != seen.end()) count += it->second; seen[cur]++; } return count; }
int main() {
    std::mt19937 rng(38);
    for (int rep = 0; rep < 300; rep++) { int n = (int)(rng() % 30); std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 201) - 100; Prefix p(a); assert(p.P.size() == (std::size_t)n + 1 && p.P[0] == 0);                                 // ①
        for (int l = 0; l <= n; l++) for (int r = l; r <= n; r++) { long long want = 0; for (int i = l; i < r; i++) want += a[i]; assert(p.sum(l, r) == want); }
        std::vector<unsigned> px(n + 1, 0); std::vector<unsigned> u(n); for (int i = 0; i < n; i++) { u[i] = (unsigned)(rng() % 1024); px[i + 1] = px[i] ^ u[i]; }                                              // ③ XOR
        for (int l = 0; l <= n; l++) for (int r = l; r <= n; r++) { unsigned want = 0; for (int i = l; i < r; i++) want ^= u[i]; assert((px[r] ^ px[l]) == want); } }
    for (int rep = 0; rep < 60; rep++) { int R = 1 + (int)(rng() % 6), C = 1 + (int)(rng() % 6); std::vector<std::vector<int>> g(R, std::vector<int>(C)); for (auto& row : g) for (int& x : row) x = (int)(rng() % 41) - 20; Prefix2D s(g);   // ②
        for (int r1 = 0; r1 <= R; r1++) for (int r2 = r1; r2 <= R; r2++) for (int c1 = 0; c1 <= C; c1++) for (int c2 = c1; c2 <= C; c2++) { long long want = 0; for (int i = r1; i < r2; i++) for (int j = c1; j < c2; j++) want += g[i][j]; assert(s.sum(r1, c1, r2, c2) == want); } }
    for (int rep = 0; rep < 800; rep++) { int n = (int)(rng() % 25); std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 7) - 3; long long K = (int)(rng() % 9) - 4; long long want = 0;                                                    // ④ 음수·0 포함
        for (int l = 0; l < n; l++) { long long s = 0; for (int r = l; r < n; r++) { s += a[r]; want += s == K; } } assert(countSubarraysWithSum(a, K) == want); }
    { std::vector<int> big(1000, 2147483647); Prefix p(big); assert(p.sum(0, 1000) == 1000LL * 2147483647 && p.sum(500, 501) == 2147483647LL); std::vector<int> neg(10, -2147483647 - 1); assert(Prefix(neg).sum(0, 10) == 10LL * -2147483648LL); }       // ⑤
    { Prefix p(std::vector<int>{}); assert(p.P.size() == 1 && p.sum(0, 0) == 0); Prefix q(std::vector<int>{7}); assert(q.sum(0, 1) == 7 && q.sum(1, 1) == 0 && q.sum(0, 0) == 0); assert(countSubarraysWithSum({}, 0) == 0 && countSubarraysWithSum({0, 0, 0}, 0) == 6); }   // ⑥
    std::cout << "PrefixSum: 1D range sums matched brute force for every interval (including empty), the 2D summed-area table matched every rectangle of 60 random grids, prefix XOR queries worked, the hash-map method counted subarrays with sum K correctly even with negatives and zeros, and 64-bit sums stayed exact near the 32-bit limit" << std::endl; return 0;
}
// Time Complexity: 구축 O(N), 질의 O(1), K 개수 세기 O(N)
// Space Complexity: O(N)
```
## DifferenceArray()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 차분 배열(Difference Array): 접두사 합의 역연산이다. D[i] = a[i] − a[i−1] (D[0] = a[0]) 로 두면 a 는 D 의 접두사 합이다. 구간 [l, r) 의 모든 원소에 v 를 더하는 일이 D[l] += v, D[r] −= v 두 번의 O(1) 갱신이 된다 — 구간 갱신이 q 번이면 순진한 방법은 O(q·n), 차분 배열은 O(q + n) (모든 갱신을 모은 뒤 한 번 접두사 합을 취해 복원). 오프라인(갱신을 전부 모은 뒤 읽기) 상황에서 쓴다. 갱신과 질의가 섞이면 펜윅 트리·세그먼트 트리가 필요하다.
// 경계: r 이 배열 끝(r == n)이면 D[n] −= v 를 쓸 자리가 필요하다 — 길이 n+1 로 잡거나 r < n 일 때만 쓴다. 2차원은 네 모퉁이 +v, −v, −v, +v 로 갱신하고 2차원 접두사 합으로 복원한다. 차분을 한 번 더 하면(2계 차분) 구간에 등차수열 first, first+d, … 를 더하는 일도 O(1) 이다: 기울기 d 를 한 번 더 누적하는 구조.
// 검증: ① 무작위 구간 가산 q 번 뒤 복원한 배열이 순진한 구현과 같음(경계 l = 0, r = n, 빈 구간 포함) ② 라운드트립: 차분(접두사 합(a)) == a, 접두사 합(차분(a)) == a ③ 초기 배열이 있는 경우 ④ 2차원 사각형 가산 복원이 순진한 구현과 같음 ⑤ 2계 차분으로 등차수열을 구간에 더하는 갱신이 순진한 구현과 같음(공차 음수 포함) ⑥ 비용: 갱신당 접근 2 회(순진: 구간 길이).
std::vector<long long> applyUpdates(const std::vector<long long>& init, const std::vector<std::vector<long long>>& ups, long long& touches) { std::size_t n = init.size(); std::vector<long long> D(n + 1, 0); for (std::size_t i = 0; i < n; i++) D[i] = init[i] - (i ? init[i - 1] : 0);
    for (const auto& u : ups) { std::size_t l = (std::size_t)u[0], r = (std::size_t)u[1]; if (l >= r) continue; D[l] += u[2]; D[r] -= u[2]; touches += 2; }                                        // 빈 구간은 건너뜀
    std::vector<long long> a(n); long long cur = 0; for (std::size_t i = 0; i < n; i++) { cur += D[i]; a[i] = cur; } return a; }
std::vector<long long> naive(std::vector<long long> a, const std::vector<std::vector<long long>>& ups, long long& touches) { for (const auto& u : ups) for (long long i = u[0]; i < u[1]; i++) { a[(std::size_t)i] += u[2]; touches++; } return a; }
std::vector<long long> diffOf(const std::vector<long long>& a) { std::vector<long long> d(a.size()); for (std::size_t i = 0; i < a.size(); i++) d[i] = a[i] - (i ? a[i - 1] : 0); return d; }
std::vector<long long> prefixOf(const std::vector<long long>& d) { std::vector<long long> a(d.size()); long long cur = 0; for (std::size_t i = 0; i < d.size(); i++) { cur += d[i]; a[i] = cur; } return a; }
std::vector<std::vector<long long>> apply2D(int R, int C, const std::vector<std::vector<long long>>& ups) { std::vector<std::vector<long long>> D(R + 1, std::vector<long long>(C + 1, 0)); for (const auto& u : ups) { int r1 = (int)u[0], c1 = (int)u[1], r2 = (int)u[2], c2 = (int)u[3]; long long v = u[4]; D[r1][c1] += v; D[r1][c2] -= v; D[r2][c1] -= v; D[r2][c2] += v; }
    std::vector<std::vector<long long>> a(R, std::vector<long long>(C)); for (int i = 0; i < R; i++) for (int j = 0; j < C; j++) { D[i][j] += (i ? D[i - 1][j] : 0) + (j ? D[i][j - 1] : 0) - (i && j ? D[i - 1][j - 1] : 0); a[i][j] = D[i][j]; } return a; }
std::vector<long long> applyAP(int n, const std::vector<std::vector<long long>>& ups) { std::vector<long long> D2(n + 2, 0); for (const auto& u : ups) { long long l = u[0], r = u[1], first = u[2], d = u[3]; if (l >= r) continue;       // [l, r) 에 first, first+d, … 를 더함
        D2[l] += first; D2[l + 1] += d - first; D2[r] -= first + (r - l) * d; D2[r + 1] += first + (r - l - 1) * d; }
    std::vector<long long> a(n); long long slope = 0, val = 0, cur = 0; for (int i = 0; i < n; i++) { slope += D2[i]; val += slope; cur = val; a[i] = cur; } return a; }
int main() {
    std::mt19937 rng(39);
    for (int rep = 0; rep < 400; rep++) { int n = (int)(rng() % 25); std::vector<long long> init(n); for (auto& x : init) x = (long long)(rng() % 21) - 10; int q = (int)(rng() % 30); std::vector<std::vector<long long>> ups;                              // ① ③
        for (int i = 0; i < q; i++) { long long l = (long long)(rng() % (n + 1)), r = (long long)(rng() % (n + 1)); if (l > r) std::swap(l, r); ups.push_back({l, r, (long long)(rng() % 21) - 10}); }
        long long t1 = 0, t2 = 0; auto fast = applyUpdates(init, ups, t1), slow = naive(init, ups, t2); assert(fast == slow && t1 <= 2LL * q); long long rangeSum = 0; for (auto& u : ups) rangeSum += std::max(0LL, u[1] - u[0]); assert(t2 == rangeSum); }   // ⑥ 비용
    for (int rep = 0; rep < 300; rep++) { int n = (int)(rng() % 25); std::vector<long long> a(n); for (auto& x : a) x = (long long)(rng() % 2001) - 1000; assert(prefixOf(diffOf(a)) == a && diffOf(prefixOf(a)) == a); }          // ②
    for (int rep = 0; rep < 200; rep++) { int R = 1 + (int)(rng() % 7), C = 1 + (int)(rng() % 7); int q = (int)(rng() % 15); std::vector<std::vector<long long>> ups; std::vector<std::vector<long long>> want(R, std::vector<long long>(C, 0));      // ④
        for (int i = 0; i < q; i++) { long long r1 = rng() % (R + 1), r2 = rng() % (R + 1), c1 = rng() % (C + 1), c2 = rng() % (C + 1); if (r1 > r2) std::swap(r1, r2); if (c1 > c2) std::swap(c1, c2); long long v = (long long)(rng() % 21) - 10; ups.push_back({r1, c1, r2, c2, v});
            for (long long x = r1; x < r2; x++) for (long long y = c1; y < c2; y++) want[(std::size_t)x][(std::size_t)y] += v; } assert(apply2D(R, C, ups) == want); }
    for (int rep = 0; rep < 400; rep++) { int n = 1 + (int)(rng() % 25); int q = (int)(rng() % 15); std::vector<std::vector<long long>> ups; std::vector<long long> want(n, 0);                                                // ⑤ 등차수열 가산
        for (int i = 0; i < q; i++) { long long l = (long long)(rng() % (n + 1)), r = (long long)(rng() % (n + 1)); if (l > r) std::swap(l, r); long long first = (long long)(rng() % 21) - 10, d = (long long)(rng() % 9) - 4; ups.push_back({l, r, first, d}); for (long long k = l; k < r; k++) want[(std::size_t)k] += first + (k - l) * d; }
        assert(applyAP(n, ups) == want); }
    { long long t = 0; auto a = applyUpdates({}, {}, t); assert(a.empty() && t == 0); auto b = applyUpdates({5}, {{0, 1, 3}, {0, 0, 100}}, t); assert(b == (std::vector<long long>{8}) && t == 2); }
    std::cout << "DifferenceArray: range additions applied through two O(1) updates each matched the naive implementation (which touched every element of every range), diff and prefix were exact inverses, 2D rectangle additions and second-order arithmetic-progression additions also reproduced the naive results" << std::endl; return 0;
}
// Time Complexity: 갱신 O(1), 복원 O(N)
// Space Complexity: O(N)
```

# Part 6. 연결리스트 심화
## DummyNode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <random>
#include <vector>

// 더미 노드(Dummy Node): 값이 없는 가짜 노드를 리스트 맨 앞에 하나 두는 기법이다. 실제 head 는 dummy->next 가 된다. 이렇게 하면 "첫 노드를 지우거나 앞에 넣을 때만 head 포인터를 고쳐야 하는" 특수 경우가 사라져 모든 노드가 앞 노드를 가진다 — 삭제는 `prev->next = prev->next->next` 하나의 코드로 통일된다. 결과는 dummy->next 를 반환하고 dummy 자신은 반드시 정리한다(스택에 두면 자동).
// 같은 문제를 더미 없이 풀면 head 가 바뀔 수 있는 경우를 따로 처리하는 반복문이 앞에 붙는다. 이 코드는 head 가 지워질 수 있는 대표 문제 넷을 두 방식으로 구현해 결과가 같음을 확인한다: 값이 같은 노드 모두 지우기, 정렬 유지 삽입, 정렬 리스트에서 중복된 값을 가진 노드를 전부 지우기(II: 중복된 값은 하나도 남기지 않음), x 미만/이상으로 안정 분할해 이어 붙이기.
// 검증: ① 네 문제 모두 더미 방식 == 더미 없는 방식 == 벡터 모델(무작위 3000 입력, 빈 리스트·전부 삭제되는 리스트 포함) 정렬 삽입은 같은 값이 있으면 그 뒤에 들어간다(안정적 — 새 노드의 주소로 위치를 확인) ② 모든 노드가 보존/해제되어 누수 없음 ③ 머리 노드가 지워지는 경우(전부 삭제·머리만 삭제)와 빈 리스트 ④ 반환된 리스트의 머리가 dummy 가 아니라 dummy->next 임을 확인.
struct Node { int val; Node* next; static int live; Node(int v, Node* n = nullptr) : val(v), next(n) { ++live; } ~Node() { --live; } }; int Node::live = 0;
Node* build(const std::vector<int>& v) { Node dummy(0); Node* t = &dummy; for (int x : v) { t->next = new Node(x); t = t->next; } Node* h = dummy.next; dummy.next = nullptr; return h; }
void destroy(Node* h) { while (h) { Node* n = h->next; delete h; h = n; } }
std::vector<int> items(const Node* h) { std::vector<int> r; for (; h; h = h->next) r.push_back(h->val); return r; }
std::vector<const Node*> ptrs(const Node* h) { std::vector<const Node*> r; for (; h; h = h->next) r.push_back(h); return r; }
std::size_t newIndex(const Node* h, const std::vector<const Node*>& old) { std::size_t i = 0; for (; h && std::find(old.begin(), old.end(), h) != old.end(); h = h->next) i++; return i; }   // 옛 노드가 아닌 첫 노드의 위치 = 새 노드의 위치
Node* removeAllDummy(Node* head, int key) { Node dummy(0, head); for (Node* p = &dummy; p->next;) { if (p->next->val == key) { Node* dead = p->next; p->next = dead->next; delete dead; } else p = p->next; } Node* h = dummy.next; dummy.next = nullptr; return h; }
Node* removeAllPlain(Node* head, int key) { while (head && head->val == key) { Node* dead = head; head = head->next; delete dead; }          // 머리가 지워지는 경우를 먼저 따로 처리
    for (Node* p = head; p && p->next;) { if (p->next->val == key) { Node* dead = p->next; p->next = dead->next; delete dead; } else p = p->next; } return head; }
Node* insertSortedDummy(Node* head, int v) { Node dummy(0, head); Node* p = &dummy; while (p->next && p->next->val <= v) p = p->next; p->next = new Node(v, p->next); Node* h = dummy.next; dummy.next = nullptr; return h; }
Node* insertSortedPlain(Node* head, int v) { if (!head || v < head->val) return new Node(v, head); Node* p = head; while (p->next && p->next->val <= v) p = p->next; p->next = new Node(v, p->next); return head; }
Node* deleteDuplicatesDummy(Node* head) { Node dummy(0, head); Node* prev = &dummy; while (prev->next) { Node* c = prev->next; if (c->next && c->next->val == c->val) { int v = c->val; while (prev->next && prev->next->val == v) { Node* dead = prev->next; prev->next = dead->next; delete dead; } } else prev = c; } Node* h = dummy.next; dummy.next = nullptr; return h; }
Node* deleteDuplicatesPlain(Node* head) { Node* newHead = nullptr; Node* tail = nullptr; while (head) { if (head->next && head->next->val == head->val) { int v = head->val; while (head && head->val == v) { Node* dead = head; head = head->next; delete dead; } }
        else { Node* keep = head; head = head->next; keep->next = nullptr; if (!tail) newHead = tail = keep; else { tail->next = keep; tail = keep; } } } return newHead; }
Node* partitionDummy(Node* head, int x) { Node lo(0), hi(0); Node *tl = &lo, *th = &hi; while (head) { Node* nx = head->next; head->next = nullptr; if (head->val < x) { tl->next = head; tl = head; } else { th->next = head; th = head; } head = nx; } tl->next = hi.next; Node* h = lo.next; lo.next = nullptr; hi.next = nullptr; return h; }
Node* partitionPlain(Node* head, int x) { Node *lh = nullptr, *lt = nullptr, *hh = nullptr, *ht = nullptr; while (head) { Node* nx = head->next; head->next = nullptr; if (head->val < x) { if (!lt) lh = lt = head; else { lt->next = head; lt = head; } } else { if (!ht) hh = ht = head; else { ht->next = head; ht = head; } } head = nx; } if (!lt) return hh; lt->next = hh; return lh; }
int main() {
    std::mt19937 rng(40);
    for (int rep = 0; rep < 3000; rep++) { int n = (int)(rng() % 14), range = 1 + (int)(rng() % 6); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % range); int key = (int)(rng() % range);
        { std::vector<int> ref = v; ref.erase(std::remove(ref.begin(), ref.end(), key), ref.end()); Node* a = removeAllDummy(build(v), key); Node* b = removeAllPlain(build(v), key); assert(items(a) == ref && items(b) == ref); destroy(a); destroy(b); }   // ①
        { std::vector<int> s = v; std::sort(s.begin(), s.end()); std::vector<int> ref = s; ref.insert(std::upper_bound(ref.begin(), ref.end(), key), key);
          std::size_t slot = (std::size_t)(std::upper_bound(s.begin(), s.end(), key) - s.begin()); Node* a0 = build(s); std::vector<const Node*> oa = ptrs(a0); Node* a = insertSortedDummy(a0, key); Node* b0 = build(s); std::vector<const Node*> ob = ptrs(b0); Node* b = insertSortedPlain(b0, key);
          assert(items(a) == ref && items(b) == ref && newIndex(a, oa) == slot && newIndex(b, ob) == slot); destroy(a); destroy(b); }   // 같은 값이 있으면 그 뒤(upper_bound 위치)에 들어간다
        { std::vector<int> s = v; std::sort(s.begin(), s.end()); std::vector<int> ref; for (std::size_t i = 0; i < s.size();) { std::size_t j = i; while (j < s.size() && s[j] == s[i]) j++; if (j - i == 1) ref.push_back(s[i]); i = j; }
          Node* a = deleteDuplicatesDummy(build(s)); Node* b = deleteDuplicatesPlain(build(s)); assert(items(a) == ref && items(b) == ref); destroy(a); destroy(b); }
        { std::vector<int> ref; for (int x : v) if (x < key) ref.push_back(x); for (int x : v) if (x >= key) ref.push_back(x); Node* a = partitionDummy(build(v), key); Node* b = partitionPlain(build(v), key); assert(items(a) == ref && items(b) == ref); destroy(a); destroy(b); }
        assert(Node::live == 0); }                                                                                                                       // ②
    { Node* h = removeAllDummy(build({7, 7, 7}), 7); assert(h == nullptr && Node::live == 0); h = removeAllDummy(nullptr, 1); assert(h == nullptr); Node* g = build({1, 2}); Node* r = removeAllDummy(g, 1); assert(r->val == 2 && r->next == nullptr); destroy(r); }   // ④ 머리 삭제 뒤 반환값이 새 머리
    std::cout << "DummyNode: removing a value, sorted insertion, deleting all duplicated values and stable partition were each implemented with a dummy head and with head special-cases; both agreed with a vector model on 3000 random lists (including lists that lose their head entirely) and no node leaked" << std::endl; return 0;
}
// Time Complexity: O(N) (더미 노드는 O(1) 추가)
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
#include <algorithm>
#include <cassert>
#include <deque>
#include <iostream>
#include <random>
#include <vector>

// 원형 연결 리스트(Circular Linked List): 마지막 노드의 next 가 첫 노드를 가리켜 고리를 이룬다. 끝(nullptr)이 없으므로 순회는 "시작 노드로 돌아오면 종료"로 한다. 꼬리 포인터 하나만 들고 있으면 head = tail->next 이므로 앞·뒤 삽입이 모두 O(1)이고, 회전(rotate)은 tail 을 한 칸 전진시키는 것만으로 O(1)이다. 두 원형 리스트의 이어 붙이기(splice)도 next 두 개를 교환해 O(1)이다. 라운드 로빈 스케줄링과 조제푸스 문제가 대표 응용이다.
// 조제푸스(Josephus) 문제: n 명이 원으로 앉아 k 번째마다 제거할 때 마지막 생존자. 원형 리스트로 시뮬레이션하면 O(n·k), 점화식 J(1) = 0, J(m) = (J(m−1) + k) mod m 으로 O(n), k = 2 이면 n = 2^a + l 일 때 2l + 1(1 기반) 닫힌 꼴이다.
// 검증: ① 무작위 push_front/push_back/pop_front/rotate 가 std::deque 모델(rotate = 앞을 빼서 뒤에 넣기)과 같음, 빈·한 노드 경계에서 tail->next == tail ② 순회가 정확히 한 바퀴(길이만큼)이고 멈춤 ③ 두 리스트 이어 붙이기가 O(1) 으로 올바름 ④ 조제푸스: 시뮬레이션 == 점화식 (모든 n ≤ 120, k ≤ 10), k=2 닫힌 꼴 ⑤ 노드 누수 없음.
struct Node { int val; Node* next; static int live; Node(int v) : val(v), next(nullptr) { ++live; } ~Node() { --live; } }; int Node::live = 0;
class Circular { Node* tail_ = nullptr; std::size_t n_ = 0;                                                         // 꼬리 포인터만 보관: head = tail_->next
public:
    Circular() = default; Circular(const Circular&) = delete; Circular& operator=(const Circular&) = delete; ~Circular() { clear(); }
    void pushFront(int v) { Node* x = new Node(v); if (!tail_) { x->next = x; tail_ = x; } else { x->next = tail_->next; tail_->next = x; } n_++; }
    void pushBack(int v) { pushFront(v); tail_ = tail_->next; }                                                    // 앞에 넣고 꼬리를 한 칸 전진 → 방금 넣은 노드가 새 꼬리
    bool popFront(int& out) { if (!tail_) return false; Node* head = tail_->next; out = head->val; if (head == tail_) tail_ = nullptr; else tail_->next = head->next; delete head; n_--; return true; }
    void rotate() { if (tail_) tail_ = tail_->next; }                                                              // 앞의 것이 뒤로: O(1)
    void spliceBack(Circular& other) { if (!other.tail_) return; if (!tail_) { tail_ = other.tail_; n_ = other.n_; } else { Node* h1 = tail_->next; tail_->next = other.tail_->next; other.tail_->next = h1; tail_ = other.tail_; n_ += other.n_; } other.tail_ = nullptr; other.n_ = 0; }
    void clear() { if (!tail_) return; Node* h = tail_->next; tail_->next = nullptr; while (h) { Node* nx = h->next; delete h; h = nx; } tail_ = nullptr; n_ = 0; }
    std::size_t size() const { return n_; } const Node* tail() const { return tail_; }
    std::vector<int> items() const { std::vector<int> r; if (!tail_) return r; const Node* c = tail_->next; do { r.push_back(c->val); c = c->next; } while (c != tail_->next); return r; }
    int survivorOfJosephus(int k) {                                                                                  // 소유 리스트를 소모: k 번째마다 제거
        Node* prev = tail_; while (n_ > 1) { for (int i = 1; i < k; i++) prev = prev->next; Node* dead = prev->next; if (dead == tail_) tail_ = prev; prev->next = dead->next; delete dead; n_--; } return tail_->val; } };
int josephusRec(int n, int k) { int r = 0; for (int m = 2; m <= n; m++) r = (r + k) % m; return r; }
int main() {
    std::mt19937 rng(41);
    { Circular c; std::deque<int> ref; for (int step = 0; step < 20000; step++) { int op = (int)(rng() % 5), v = (int)(rng() % 1000), out = -1;                                          // ①
          if (op == 0) { c.pushFront(v); ref.push_front(v); } else if (op == 1) { c.pushBack(v); ref.push_back(v); } else if (op == 2) { bool ok = c.popFront(out); assert(ok == !ref.empty()); if (ok) { assert(out == ref.front()); ref.pop_front(); } }
          else if (op == 3) { c.rotate(); if (!ref.empty()) { ref.push_back(ref.front()); ref.pop_front(); } } else if (rng() % 8 == 0) { assert(c.size() == ref.size()); }
          assert(c.size() == ref.size() && (int)c.size() == Node::live); if (step % 97 == 0) assert(c.items() == std::vector<int>(ref.begin(), ref.end())); if (ref.empty()) assert(c.tail() == nullptr); else assert(c.tail()->next->val == ref.front() && (ref.size() != 1 || c.tail()->next == c.tail())); } }
    assert(Node::live == 0);
    { Circular c; c.pushBack(5); assert(c.tail()->next == c.tail() && c.items() == std::vector<int>{5}); c.rotate(); assert(c.items() == std::vector<int>{5}); int o; assert(c.popFront(o) && o == 5 && c.tail() == nullptr && !c.popFront(o)); }   // 한 노드 경계
    for (int rep = 0; rep < 200; rep++) { Circular a, b; std::vector<int> va, vb; int na = (int)(rng() % 8), nb = (int)(rng() % 8); for (int i = 0; i < na; i++) { a.pushBack(i); va.push_back(i); } for (int i = 0; i < nb; i++) { b.pushBack(100 + i); vb.push_back(100 + i); }                                      // ③
        a.spliceBack(b); va.insert(va.end(), vb.begin(), vb.end()); assert(a.items() == va && b.size() == 0 && b.tail() == nullptr && a.size() == va.size()); if (!va.empty()) assert(a.tail()->val == va.back()); }
    assert(Node::live == 0);
    for (int n = 1; n <= 120; n++) for (int k = 1; k <= 10; k++) { Circular c; for (int i = 1; i <= n; i++) c.pushBack(i); int s = c.survivorOfJosephus(k); assert(s == josephusRec(n, k) + 1); if (k == 2) { int p = 1; while (p * 2 <= n) p *= 2; assert(s == 2 * (n - p) + 1); } }   // ④
    { Circular c; for (int i = 0; i < 1000; i++) c.pushBack(i); assert(c.items().size() == 1000); c.clear(); assert(Node::live == 0 && c.size() == 0); }                                                                             // ②⑤
    assert(Node::live == 0); std::cout << "CircularList: 20000 random push/pop/rotate operations matched a deque model using only a tail pointer, one full lap visited exactly n nodes, O(1) splicing concatenated correctly, and simulating the Josephus problem matched the recurrence (and the 2l+1 closed form for k=2) for every n<=120, k<=10" << std::endl; return 0;
}
// Time Complexity: 삽입·삭제·회전·이어붙이기 O(1), 조제푸스 시뮬레이션 O(N·K)
// Space Complexity: O(1)
```
## DoublyLinkedList()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <list>
#include <random>
#include <vector>

// 이중 연결 리스트(Doubly Linked List): 각 노드가 prev 와 next 를 모두 가진다. 노드를 가리키는 포인터만 있으면 앞뒤 이동, 그 자리에서의 삽입·삭제(O(1))가 모두 가능하다 — 단방향은 앞 노드를 찾으려 O(n) 이 든다. 대가는 노드당 포인터 하나 더. 센티넬 노드 하나를 두고 원형으로 이으면 head/tail 널 검사가 모두 사라진다(모든 노드가 항상 양쪽 이웃을 가짐).
// 이 코드의 불변식(invariant): 모든 노드 x 에 대해 x->next->prev == x 이고 x->prev->next == x, 센티넬에서 next 로 한 바퀴 돌면 size 개를 지나 센티넬로 돌아오며 prev 로 돌아도 같은 개수. 연산이 끝날 때마다 검사한다. 응용: 노드 핸들로 O(1) 삭제(LRU 캐시), 노드를 다른 위치로 옮기기(moveToFront)와 다른 리스트로 옮기기(splice) — 노드를 다시 할당하지 않고 연결만 바꾼다. reverse 는 모든 노드의 prev/next 를 맞바꾸기만 하면 된다.
// 검증: ① 무작위 삽입·삭제(핸들 기반)가 std::list 와 같은 내용이며 매 연산 뒤 불변식 성립 ② 앞으로 읽은 순서와 뒤로 읽은 순서가 서로 역순 ③ moveToFront·splice 가 노드를 재사용(주소 보존, 새 할당 0)하고 결과가 모델과 같음 ④ reverse 가 std::reverse 와 같고 두 번 뒤집으면 원래 ⑤ 노드 수 = 생성자−소멸자(누수 없음).
struct Node { int val; Node *prev, *next; static int live, created; explicit Node(int v) : val(v), prev(nullptr), next(nullptr) { ++live; ++created; } ~Node() { --live; } }; int Node::live = 0, Node::created = 0;
class DList { Node* s_; std::size_t n_ = 0;
public:
    DList() { s_ = new Node(0); s_->prev = s_->next = s_; } DList(const DList&) = delete; DList& operator=(const DList&) = delete; ~DList() { Node* x = s_->next; while (x != s_) { Node* nx = x->next; delete x; x = nx; } delete s_; }
    Node* sentinel() const { return s_; } Node* first() const { return s_->next; } Node* last() const { return s_->prev; } std::size_t size() const { return n_; }
    Node* insertBefore(Node* pos, int v) { Node* x = new Node(v); x->prev = pos->prev; x->next = pos; pos->prev->next = x; pos->prev = x; n_++; return x; }                     // 분기 없음
    Node* pushFront(int v) { return insertBefore(s_->next, v); } Node* pushBack(int v) { return insertBefore(s_, v); }
    void erase(Node* x) { x->prev->next = x->next; x->next->prev = x->prev; delete x; n_--; }
    void unlink(Node* x) { x->prev->next = x->next; x->next->prev = x->prev; n_--; }                                                                                             // 해제하지 않고 떼어 냄
    void linkBefore(Node* pos, Node* x) { x->prev = pos->prev; x->next = pos; pos->prev->next = x; pos->prev = x; n_++; }
    void moveToFront(Node* x) { unlink(x); linkBefore(s_->next, x); }
    void spliceBefore(Node* pos, DList& other, Node* x) { other.unlink(x); linkBefore(pos, x); }
    void reverse() { Node* x = s_; do { std::swap(x->prev, x->next); x = x->prev; } while (x != s_); }                                                                           // 모든 노드의 prev/next 맞바꿈
    bool invariant() const { std::size_t cnt = 0; const Node* x = s_; do { if (x->next->prev != x || x->prev->next != x) return false; x = x->next; if (x != s_) cnt++; } while (x != s_ && cnt <= n_); if (cnt != n_) return false;
        cnt = 0; x = s_->prev; while (x != s_ && cnt <= n_) { cnt++; x = x->prev; } return cnt == n_; }
    std::vector<int> forward() const { std::vector<int> r; for (Node* x = s_->next; x != s_; x = x->next) r.push_back(x->val); return r; }
    std::vector<int> backward() const { std::vector<int> r; for (Node* x = s_->prev; x != s_; x = x->prev) r.push_back(x->val); return r; } };
int main() {
    std::mt19937 rng(42);
    { DList l; std::list<int> ref; std::vector<Node*> h; std::vector<int> hv; for (int step = 0; step < 15000; step++) { int op = (int)(rng() % 5), v = (int)(rng() % 1000);                                         // ①
          if (op <= 1 || h.empty()) { std::size_t i = rng() % (h.size() + 1); Node* pos = i == h.size() ? l.sentinel() : h[i]; Node* x = l.insertBefore(pos, v); h.insert(h.begin() + i, x); hv.insert(hv.begin() + i, v); auto it = ref.begin(); std::advance(it, i); ref.insert(it, v); }
          else if (op == 2) { std::size_t i = rng() % h.size(); l.erase(h[i]); h.erase(h.begin() + i); hv.erase(hv.begin() + i); auto it = ref.begin(); std::advance(it, i); ref.erase(it); }
          else if (op == 3) { std::size_t i = rng() % h.size(); l.moveToFront(h[i]); Node* x = h[i]; int xv = hv[i]; h.erase(h.begin() + i); hv.erase(hv.begin() + i); h.insert(h.begin(), x); hv.insert(hv.begin(), xv); auto it = ref.begin(); std::advance(it, i); ref.splice(ref.begin(), ref, it); }   // ③
          else { if (rng() % 3 == 0) { l.pushFront(v); h.insert(h.begin(), l.first()); hv.insert(hv.begin(), v); ref.push_front(v); } else { l.pushBack(v); h.push_back(l.last()); hv.push_back(v); ref.push_back(v); } }
          assert(l.size() == ref.size() && (int)l.size() == Node::live - 1 && l.invariant()); if (step % 53 == 0) { std::vector<int> f = l.forward(), b = l.backward(), want(ref.begin(), ref.end()); assert(f == want); std::reverse(b.begin(), b.end()); assert(b == want); } } }    // ②
    assert(Node::live == 0);
    { DList a, b; for (int i = 0; i < 6; i++) { a.pushBack(i); b.pushBack(100 + i); } std::vector<Node*> bn; for (Node* x = b.first(); x != b.sentinel(); x = x->next) bn.push_back(x); int created = Node::created; a.spliceBefore(a.first()->next, b, bn[3]); a.spliceBefore(a.sentinel(), b, bn[0]);     // 노드 이동: 새 할당 0
      assert(Node::created == created && a.forward() == (std::vector<int>{0, 103, 1, 2, 3, 4, 5, 100}) && b.forward() == (std::vector<int>{101, 102, 104, 105}) && a.invariant() && b.invariant() && a.first()->next == bn[3]); }
    for (int rep = 0; rep < 300; rep++) { DList l; int n = (int)(rng() % 20); std::vector<int> v(n); for (int& x : v) { x = (int)(rng() % 100); l.pushBack(x); } std::vector<int> rv(v.rbegin(), v.rend()); std::vector<Node*> before; for (Node* x = l.first(); x != l.sentinel(); x = x->next) before.push_back(x);   // ④
        l.reverse(); assert(l.forward() == rv && l.invariant()); std::vector<Node*> after; for (Node* x = l.first(); x != l.sentinel(); x = x->next) after.push_back(x); std::reverse(after.begin(), after.end()); assert(after == before); l.reverse(); assert(l.forward() == v && l.invariant()); }
    assert(Node::live == 0); std::cout << "DoublyLinkedList: 15000 handle-based insertions, erasures and move-to-front operations matched std::list while the prev/next invariant held after every step; splicing and moving reused existing nodes without allocating, and reversal by swapping prev/next kept every node and was an involution" << std::endl; return 0;
}
// Time Complexity: 핸들 기반 삽입·삭제·이동 O(1), 뒤집기 O(N)
// Space Complexity: 노드당 포인터 2 개 + 센티넬 1 개
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
#include <algorithm>
#include <cassert>
#include <forward_list>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <vector>

// begin(): 첫 원소를 가리키는 반복자다. 반열린 범위 [begin, end) 에서 시작 쪽 경계이며, 비어 있으면 begin() == end() 이다. 연결 리스트에서 begin 은 head 노드를 가리키므로 앞에 원소를 넣으면 begin 이 바뀌지만, 이미 얻어 둔 다른 원소의 반복자는 무효가 되지 않는다(노드가 움직이지 않기 때문 — 배열과 다른 점).
// 단방향 리스트의 큰 난점: "맨 앞에 넣기·지우기" 는 head 포인터를 고쳐야 해서 중간 위치와 다른 코드가 된다. 표준의 해법은 before_begin() — 첫 원소 "앞"의 가상 위치를 가리키는 반복자를 두고 insert_after/erase_after 만 제공해서 맨 앞도 같은 코드로 처리하는 것이다(더미 노드와 같은 발상). 이 코드는 헤더 노드를 내장한 단방향 리스트로 이를 직접 구현한다.
// 검증: ① 무작위 insert_after/erase_after/push_front/pop_front 가 std::forward_list 와 같은 내용(수천 번) ② 빈 리스트에서 begin() == end(), begin() == std::next(before_begin()) ③ 앞에 넣은 뒤에도 이미 가진 반복자는 같은 원소를 가리키고 std::next(begin()) 가 이전 begin ④ erase_after(before_begin()) 는 새 begin 을 돌려줌 ⑤ 반복자 범주가 forward 이고 std::find/count/accumulate/distance 가 vector 결과와 같음 ⑥ 노드 누수 없음.
template <class T> class FList {
    struct Node { T val; Node* next; }; Node before_{T(), nullptr}; std::size_t n_ = 0;                                 // 헤더 노드: before_begin() 이 가리키는 가상 위치
public:
    static int live;
    class iterator { Node* p; friend class FList; public:
        using iterator_category = std::forward_iterator_tag; using value_type = T; using difference_type = std::ptrdiff_t; using pointer = T*; using reference = T&;
        iterator() : p(nullptr) {} explicit iterator(Node* q) : p(q) {} T& operator*() const { return p->val; } iterator& operator++() { p = p->next; return *this; } iterator operator++(int) { iterator t = *this; p = p->next; return t; }
        friend bool operator==(const iterator& a, const iterator& b) { return a.p == b.p; } friend bool operator!=(const iterator& a, const iterator& b) { return a.p != b.p; } };
    FList() = default; FList(const FList&) = delete; FList& operator=(const FList&) = delete; ~FList() { while (before_.next) erase_after(before_begin()); }
    iterator before_begin() { return iterator(&before_); } iterator begin() { return iterator(before_.next); } iterator end() { return iterator(nullptr); }
    iterator insert_after(iterator pos, const T& v) { Node* x = new Node{v, pos.p->next}; ++live; pos.p->next = x; n_++; return iterator(x); }
    iterator erase_after(iterator pos) { Node* dead = pos.p->next; pos.p->next = dead->next; iterator nx(dead->next); delete dead; --live; n_--; return nx; }
    void push_front(const T& v) { insert_after(before_begin(), v); } void pop_front() { erase_after(before_begin()); }
    bool empty() const { return n_ == 0; } std::size_t size() const { return n_; } };
template <class T> int FList<T>::live = 0;
int main() {
    std::mt19937 rng(43); FList<int> a; std::forward_list<int> ref; std::size_t n = 0;
    for (int step = 0; step < 20000; step++) { int op = (int)(rng() % 4), v = (int)(rng() % 1000);                                                          // ①
        if (op == 0 || n == 0) { a.push_front(v); ref.push_front(v); n++; }
        else if (op == 1) { std::size_t i = rng() % (n + 1); auto ia = std::next(a.before_begin(), i); auto ir = std::next(ref.before_begin(), i); a.insert_after(ia, v); ref.insert_after(ir, v); n++; }
        else if (op == 2) { std::size_t i = rng() % n; auto ia = std::next(a.before_begin(), i); auto ir = std::next(ref.before_begin(), i); auto na = a.erase_after(ia); auto nr = ref.erase_after(ir); assert((na == a.end()) == (nr == ref.end())); if (nr != ref.end()) assert(*na == *nr); n--; }
        else { a.pop_front(); ref.pop_front(); n--; }
        assert(a.size() == n && (int)n == FList<int>::live); if (step % 101 == 0) assert(std::equal(a.begin(), a.end(), ref.begin(), ref.end())); }
    assert(std::equal(a.begin(), a.end(), ref.begin(), ref.end()) && std::distance(a.begin(), a.end()) == (std::ptrdiff_t)n);
    { FList<int> e; assert(e.begin() == e.end() && e.begin() == std::next(e.before_begin()) && e.empty()); e.push_front(1); assert(e.begin() != e.end() && *e.begin() == 1 && std::next(e.begin()) == e.end()); }                      // ②
    { FList<int> l; for (int i = 3; i >= 1; i--) l.push_front(i); auto second = std::next(l.begin()); auto oldBegin = l.begin(); assert(*second == 2); l.push_front(0); assert(*second == 2 && *oldBegin == 1 && std::next(l.begin()) == oldBegin && *l.begin() == 0);   // ③ 이미 가진 반복자는 그대로
      auto nb = l.erase_after(l.before_begin()); assert(nb == l.begin() && *nb == 1 && *second == 2 && std::distance(l.begin(), l.end()) == 3);                                                                                                            // ④
      assert((std::is_same<std::iterator_traits<FList<int>::iterator>::iterator_category, std::forward_iterator_tag>::value));
      std::vector<int> v(l.begin(), l.end()); assert(v == (std::vector<int>{1, 2, 3}) && *std::find(l.begin(), l.end(), 3) == 3 && std::count(l.begin(), l.end(), 2) == 1 && std::accumulate(l.begin(), l.end(), 0) == 6); }        // ⑤
    assert(FList<int>::live == (int)n); { FList<int>* p = new FList<int>; for (int i = 0; i < 100; i++) p->push_front(i); int before = FList<int>::live; delete p; assert(FList<int>::live == before - 100); }                                  // ⑥
    std::cout << "Begin: a forward list with an embedded header node (before_begin) matched std::forward_list across 20000 random insert_after/erase_after/push_front/pop_front operations; begin() == end() when empty, iterators to existing elements survived insertion at the front, and standard algorithms accepted the forward iterator" << std::endl; return 0;
}
// Time Complexity: begin()·before_begin()·end() O(1), insert_after·erase_after O(1) (위치 반복자를 이미 가진 경우)
// Space Complexity: O(1) 반복자
```
## End()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <list>
#include <random>
#include <stdexcept>
#include <vector>

// end(): 마지막 원소의 "다음" 위치를 가리키는 반복자다. 반열린 범위 [begin, end) 의 끝 경계로, 원소가 아니므로 역참조하면 안 되고 ++ 도 안 된다. 순회는 `for (it = begin; it != end; ++it)`. 이것이 "찾지 못함"을 표현하는 값이기도 하다(std::find 가 end 를 돌려줌). 센티넬 노드로 만든 원형 이중 연결 리스트에서 end() 는 센티넬 자신이고, 항상 같은 노드라서 삽입·삭제 뒤에도 end() 가 변하지 않는다. --end() 는 마지막 원소다(센티넬의 prev).
// 배열(vector)의 end() 는 데이터 끝 주소라서 원소를 하나 넣을 때마다 이동하고, 재할당되면 시작 주소째 바뀌어 모든 반복자가 무효가 된다. 연결 리스트는 삭제된 원소를 가리키는 반복자만 무효가 되고 나머지는 유효하다.
// 이 코드는 잘못된 사용을 잡아내는 "검사하는 반복자"를 만든다: end() 를 역참조하거나 end() 에서 ++ 하거나 begin() 에서 -- 하면 예외를 던진다. 무효 사용은 보통 정의되지 않은 동작이라 조용히 틀리거나 비정상 종료하기 때문에 디버그 빌드에서 이런 검사를 두는 것이 유용하다.
// 검증: ① 유효한 연산(순회, --end(), erase 가 다음 반복자를 돌려줌, insert(end()) 가 맨 뒤에 추가)이 std::list 와 같은 결과 ② 세 가지 잘못된 사용(*end, ++end, --begin)이 항상 예외이고 리스트는 불변 ③ end() 반복자가 수천 번의 삽입·삭제 뒤에도 같은 값(센티넬) ④ 빈 리스트에서 begin() == end(), --end() 는 예외 ⑤ vector 의 end 주소는 push_back 마다 이동 ⑥ 노드 누수 없음.
template <class T> class CList {
    struct Node { T val; Node *prev, *next; }; Node* s_; std::size_t n_ = 0;
public:
    static int live;
    class iterator { const CList* l_; Node* p_; friend class CList; public:
        using iterator_category = std::bidirectional_iterator_tag; using value_type = T; using difference_type = std::ptrdiff_t; using pointer = T*; using reference = T&;
        iterator() : l_(nullptr), p_(nullptr) {} iterator(const CList* l, Node* p) : l_(l), p_(p) {}
        T& operator*() const { if (p_ == l_->s_) throw std::out_of_range("dereference of end()"); return p_->val; }
        iterator& operator++() { if (p_ == l_->s_) throw std::out_of_range("increment of end()"); p_ = p_->next; return *this; }
        iterator& operator--() { if (p_ == l_->s_->next) throw std::out_of_range("decrement of begin()"); p_ = p_->prev; return *this; }       // 빈 리스트에서는 begin() == end() 라 역시 예외
        iterator operator++(int) { iterator t = *this; ++*this; return t; } iterator operator--(int) { iterator t = *this; --*this; return t; }
        friend bool operator==(const iterator& a, const iterator& b) { return a.p_ == b.p_; } friend bool operator!=(const iterator& a, const iterator& b) { return a.p_ != b.p_; } };
    CList() { s_ = new Node{T(), nullptr, nullptr}; s_->prev = s_->next = s_; } CList(const CList&) = delete; CList& operator=(const CList&) = delete;
    ~CList() { Node* x = s_->next; while (x != s_) { Node* nx = x->next; delete x; --live; x = nx; } delete s_; }
    iterator begin() const { return iterator(this, s_->next); } iterator end() const { return iterator(this, s_); }
    iterator insert(iterator pos, const T& v) { Node* nx = pos.p_; Node* x = new Node{v, nx->prev, nx}; ++live; nx->prev->next = x; nx->prev = x; n_++; return iterator(this, x); }
    iterator erase(iterator pos) { if (pos.p_ == s_) throw std::out_of_range("erase of end()"); Node* x = pos.p_; Node* nx = x->next; x->prev->next = nx; nx->prev = x->prev; delete x; --live; n_--; return iterator(this, nx); }
    std::size_t size() const { return n_; } };
template <class T> int CList<T>::live = 0;
template <class F> bool throws(F f) { try { f(); } catch (const std::out_of_range&) { return true; } return false; }
int main() {
    std::mt19937 rng(44);
    { CList<int> a; std::list<int> ref; for (int step = 0; step < 15000; step++) { int op = (int)(rng() % 3), v = (int)(rng() % 1000); std::size_t n = ref.size();                                               // ①
          if (op == 0 || n == 0) { std::size_t i = rng() % (n + 1); auto ia = std::next(a.begin(), i); auto ir = std::next(ref.begin(), i); auto ra = a.insert(ia, v); auto rr = ref.insert(ir, v); assert(*ra == *rr && (i == n ? std::next(ra) == a.end() : true)); }
          else if (op == 1) { std::size_t i = rng() % n; auto ia = std::next(a.begin(), i); auto ir = std::next(ref.begin(), i); auto na = a.erase(ia); auto nr = ref.erase(ir); assert((na == a.end()) == (nr == ref.end()) && (nr == ref.end() || *na == *nr)); }
          else { a.insert(a.end(), v); ref.push_back(v); } assert(a.size() == ref.size() && (int)a.size() == CList<int>::live && std::equal(a.begin(), a.end(), ref.begin(), ref.end())); if (!ref.empty()) assert(*std::prev(a.end()) == ref.back()); } }
    assert(CList<int>::live == 0);
    { CList<int> l; for (int i = 0; i < 3; i++) l.insert(l.end(), i); auto before = l.end(); std::vector<int> snap(l.begin(), l.end());                                                            // ②
      assert(throws([&] { *l.end(); }) && throws([&] { ++l.end(); }) && throws([&] { --l.begin(); }) && throws([&] { l.erase(l.end()); }));
      assert(std::vector<int>(l.begin(), l.end()) == snap && l.size() == 3 && l.end() == before);
      auto it = l.begin(); ++it; ++it; ++it; assert(it == l.end() && throws([&] { *it; })); --it; assert(*it == 2); assert(!throws([&] { --it; --it; }) && *it == 0 && throws([&] { --it; })); }
    { CList<int> l; auto e = l.end(); for (int i = 0; i < 2000; i++) { l.insert(l.end(), i); if (i % 3 == 0) l.erase(l.begin()); } assert(l.end() == e);                                              // ③ end 는 변하지 않음
      for (int k = 0; k < 500; k++) { auto m = std::next(l.begin(), (long)(l.size() / 2)); l.erase(m); l.insert(l.begin(), -k); assert(l.end() == e); } }
    { CList<int> e; assert(e.begin() == e.end() && throws([&] { --e.end(); }) && throws([&] { *e.begin(); }) && std::distance(e.begin(), e.end()) == 0 && e.size() == 0); }                                         // ④
    { std::vector<int> v; v.reserve(4); const int* lastEnd = v.data() + v.size(); int moved = 0; for (int i = 0; i < 100; i++) { v.push_back(i); const int* e = v.data() + v.size(); if (e != lastEnd) moved++; lastEnd = e; } assert(moved == 100); }      // ⑤ vector 의 끝 주소는 매번 이동
    assert(CList<int>::live == 0); std::cout << "End: a sentinel-based list with checked iterators matched std::list on 15000 random operations; dereferencing end(), incrementing end() and decrementing begin() always threw without modifying the list, end() stayed identical across thousands of insertions and erasures, and a vector's end address moved on every push_back" << std::endl; return 0;
}
// Time Complexity: end() O(1), 검사 포함 증감·역참조 O(1)
// Space Complexity: O(1) 반복자 (센티넬 노드 1 개)
```
## Next()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <forward_list>
#include <iostream>
#include <iterator>
#include <list>
#include <random>
#include <vector>

// next / advance: 반복자를 n 칸 전진시키는 연산이다. 비용은 반복자의 범주(iterator category)에 달려 있다: 순방향·양방향 반복자는 ++ 를 n 번 해야 하므로 O(n), 임의 접근 반복자(vector, 배열)는 `it += n` 한 번이라 O(1) 이다. 같은 `std::next(it, n)` 이라는 호출이 범주에 따라 완전히 다른 구현(태그 디스패치)으로 풀린다. 양방향 반복자는 n 이 음수여도 되고(뒤로), 순방향 반복자는 음수가 안 된다. 범위를 넘어 전진하면 정의되지 않은 동작이라, 안전한 코드에서는 남은 거리와 비교해 잘라(clamp) 쓴다.
// 이 코드는 std::advance 가 하는 일을 직접 구현한다: 범주 태그로 오버로드를 고르고, 각 구현이 실제로 몇 번의 기본 연산(증감 또는 덧셈)을 쓰는지 센다. 그 뒤 std::next 와 같은 결과인지 확인하고, 끝을 넘지 않도록 자르는 안전 버전과 이동 거리 계산(distance)도 만든다.
// 검증: ① 리스트(양방향)의 advance 가 정확히 |n| 번의 증감, vector(임의 접근)는 정확히 1 번의 덧셈을 쓰며 둘 다 std::next 와 같은 위치 ② forward_list(순방향)도 같은 위치이고 |n| 번 증가 ③ 양방향의 음수 n(뒤로) ④ 자르는 버전이 min(n, 남은 거리) 만큼만 이동하고 실제 이동 칸 수를 돌려줌 ⑤ distance 도 범주별 비용(O(n) vs O(1)) ⑥ n = 0 은 연산 0 회.
struct Ops { long incs = 0, decs = 0, adds = 0; };
template <class It> void advanceImpl(It& it, long n, Ops& o, std::input_iterator_tag) { while (n-- > 0) { ++it; o.incs++; } }
template <class It> void advanceImpl(It& it, long n, Ops& o, std::bidirectional_iterator_tag) { if (n >= 0) while (n-- > 0) { ++it; o.incs++; } else while (n++ < 0) { --it; o.decs++; } }
template <class It> void advanceImpl(It& it, long n, Ops& o, std::random_access_iterator_tag) { if (n != 0) { it += n; o.adds++; } }
template <class It> void myAdvance(It& it, long n, Ops& o) { advanceImpl(it, n, o, typename std::iterator_traits<It>::iterator_category()); }                   // 범주 태그로 디스패치
template <class It> long advanceClamped(It& it, It last, long n, Ops& o, std::bidirectional_iterator_tag) { long moved = 0; while (moved < n && it != last) { ++it; o.incs++; moved++; } return moved; }
template <class It> long myDistance(It first, It last, Ops& o, std::input_iterator_tag) { long d = 0; while (first != last) { ++first; o.incs++; d++; } return d; }
template <class It> long myDistance(It first, It last, Ops& o, std::random_access_iterator_tag) { o.adds++; return last - first; }
int main() {
    std::mt19937 rng(45);
    for (int rep = 0; rep < 400; rep++) { int n = 1 + (int)(rng() % 60); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 100); std::list<int> l(v.begin(), v.end()); std::forward_list<int> f(v.begin(), v.end());
        long k = (long)(rng() % (n + 1)); Ops ol, ov, of; auto il = l.begin(); auto iv = v.begin(); auto iff = f.begin(); myAdvance(il, k, ol); myAdvance(iv, k, ov); myAdvance(iff, k, of);                // ① ②
        assert(il == std::next(l.begin(), k) && iv == std::next(v.begin(), k) && iff == std::next(f.begin(), k) && std::distance(l.begin(), il) == k && iv - v.begin() == k);
        assert(ol.incs == k && ol.decs == 0 && ol.adds == 0 && ov.adds == (k ? 1 : 0) && ov.incs == 0 && of.incs == k);                                                                  // ⑥ k = 0 이면 연산 0
        long back = (long)(rng() % (k + 1)); Ops ob; myAdvance(il, -back, ob); assert(il == std::next(l.begin(), k - back) && ob.decs == back && ob.incs == 0);                          // ③ 양방향의 음수
        Ops ov2; myAdvance(iv, -back, ov2); assert(iv == std::next(v.begin(), k - back) && ov2.adds == (back ? 1 : 0));
        Ops oc; auto ic = l.begin(); long over = (long)(rng() % (2 * n)); long moved = advanceClamped(ic, l.end(), over, oc, std::bidirectional_iterator_tag()); assert(moved == std::min<long>(over, n) && oc.incs == moved && std::distance(l.begin(), ic) == moved);      // ④
        Ops d1, d2, d3; assert(myDistance(l.begin(), l.end(), d1, std::bidirectional_iterator_tag()) == n && d1.incs == n && myDistance(v.begin(), v.end(), d2, std::random_access_iterator_tag()) == n && d2.adds == 1 && d2.incs == 0);   // ⑤
        assert(myDistance(f.begin(), f.end(), d3, std::forward_iterator_tag()) == n && d3.incs == n); }
    { std::list<int> l = {1, 2, 3}; Ops o; auto e = l.end(); long moved = advanceClamped(e, l.end(), 5, o, std::bidirectional_iterator_tag()); assert(moved == 0 && o.incs == 0 && e == l.end()); std::list<int> empty; auto b = empty.begin(); assert(advanceClamped(b, empty.end(), 3, o, std::bidirectional_iterator_tag()) == 0); }
    { std::vector<int> big(1000000, 1); std::list<int> lbig(big.begin(), big.end()); Ops ov, ol; auto iv = big.begin(); auto il = lbig.begin(); myAdvance(iv, 999999, ov); myAdvance(il, 999999, ol); assert(ov.adds == 1 && ov.incs == 0 && ol.incs == 999999); }                   // 100 만 칸: 1 회 vs 999999 회
    std::cout << "Next: tag-dispatched advance used exactly |n| increments for list and forward_list iterators and a single addition for vector iterators, always landing where std::next lands (including backwards steps on bidirectional iterators); the clamped version never passed end(), and distance cost n steps versus one subtraction" << std::endl; return 0;
}
// Time Complexity: 순방향·양방향 O(n), 임의 접근 O(1)
// Space Complexity: O(1)
```
## Prev()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <list>
#include <random>
#include <vector>

// prev(): 반복자를 한 칸 뒤로 물린다. 양방향 반복자(이중 연결 리스트)는 노드의 prev 포인터 하나를 따라가면 되어 O(1) 이다. 단방향 연결 리스트에는 prev 가 없어서, 노드의 앞 노드를 알려면 head 에서부터 걸어와야 한다 — O(n). 단방향 리스트의 모든 노드를 뒤에서부터 방문하는 데 걸리는 총 걸음은 (n−1)(n−2)/2 (≈ n²/2) 이고 양방향은 0 이다.
// `std::prev(end())` 는 마지막 원소이다(end 는 마지막의 다음이므로). 역방향 반복자 `std::reverse_iterator` 는 정방향 반복자 하나를 감싸 `*rit` 가 `*std::prev(rit.base())` 가 되도록 한 어댑터다: rbegin() 의 base() 는 end() 이고 rend() 의 base() 는 begin() 이다. 한 칸의 어긋남 때문에 역방향 반복자로 원소를 지울 때는 `list.erase(std::next(rit).base())` 로 써야 한다(`rit.base()` 는 다음 원소를 가리킨다).
// 검증: ① 이중 연결 리스트에서 prev 가 O(1)(추가 걸음 0)이며 뒤로 순회가 vector 의 역순과 같음 ② 단방향의 prev(node) 걸음이 정확히 노드의 위치 인덱스, 마지막에서 처음까지 모두 거치는 총 걸음 (n−1)(n−2)/2 vs 양방향 0 ③ std::prev(end()) == 마지막, begin() 앞으로 가려는 시도를 검사 버전이 잡아냄 ④ reverse_iterator 의 base() 관계와 `*rit == *prev(rit.base())` ⑤ 역방향 반복자로 원소 지우기가 모델과 같음 ⑥ 빈 리스트·원소 1개 경계.
struct SNode { int val; SNode* next; }; struct DNode { int val; DNode *prev, *next; };
SNode* prevOf(SNode* head, SNode* node, long& hops) { if (node == head) return nullptr; SNode* c = head; while (c->next != node) { c = c->next; hops++; } return c; }              // 단방향: 앞 노드를 찾아 걷는다
int main() {
    std::mt19937 rng(46);
    for (int rep = 0; rep < 200; rep++) { int n = (int)(rng() % 40); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 1000);
        DNode* dhead = nullptr; DNode* dtail = nullptr; SNode* shead = nullptr; SNode* stail = nullptr; std::vector<DNode*> dn; std::vector<SNode*> sn;
        for (int x : v) { DNode* d = new DNode{x, dtail, nullptr}; if (dtail) dtail->next = d; else dhead = d; dtail = d; dn.push_back(d); SNode* s = new SNode{x, nullptr}; if (stail) stail->next = s; else shead = s; stail = s; sn.push_back(s); }
        std::vector<int> back; long dhops = 0; for (DNode* c = dtail; c; c = c->prev) back.push_back(c->val); std::vector<int> rv(v.rbegin(), v.rend()); assert(back == rv && dhops == 0 && (dhead == nullptr) == (n == 0));                                // ①
        long shops = 0; std::vector<int> sback; for (SNode* c = stail; c; c = prevOf(shead, c, shops)) sback.push_back(c->val); assert(sback == rv);                                                          // ②
        assert(shops == (n >= 2 ? (long)(n - 1) * (n - 2) / 2 : 0)); for (int i = 0; i < n; i++) { long h = 0; SNode* p = prevOf(shead, sn[i], h); assert(i == 0 ? p == nullptr : p == sn[i - 1]); assert(h == (i >= 1 ? i - 1 : 0)); }
        for (DNode* d : dn) delete d; for (SNode* s : sn) delete s; }
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 30); std::list<int> l; for (int i = 0; i < n; i++) l.push_back((int)(rng() % 100)); std::vector<int> v(l.begin(), l.end());                                                       // ③ ④
        assert(*std::prev(l.end()) == v.back() && *std::prev(l.end(), n) == v.front()); auto rb = l.rbegin(); assert(rb.base() == l.end() && l.rend().base() == l.begin() && *rb == v.back());
        int idx = 0; for (auto rit = l.rbegin(); rit != l.rend(); ++rit, ++idx) assert(*rit == *std::prev(rit.base()) && *rit == v[n - 1 - idx]); assert(idx == n);
        std::vector<int> viaRev(l.rbegin(), l.rend()); std::reverse(v.begin(), v.end()); assert(viaRev == v); std::reverse(v.begin(), v.end()); }
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 25); std::list<int> l; std::vector<int> ref; for (int i = 0; i < n; i++) { int x = (int)(rng() % 10); l.push_back(x); ref.push_back(x); } int k = (int)(rng() % n);                          // ⑤ 뒤에서 k 번째 지우기
        auto rit = std::next(l.rbegin(), k); int want = ref[n - 1 - k]; assert(*rit == want); auto nextAfter = l.erase(std::next(rit).base()); ref.erase(ref.begin() + (n - 1 - k)); assert(std::equal(l.begin(), l.end(), ref.begin(), ref.end()));
        assert((nextAfter == l.end()) == (k == 0)); if (k > 0) assert(*nextAfter == ref[n - 1 - k]); }
    { std::list<int> e; assert(e.rbegin() == e.rend() && e.rbegin().base() == e.end()); std::list<int> one = {7}; assert(*std::prev(one.end()) == 7 && std::prev(one.end()) == one.begin() && *one.rbegin() == 7 && std::next(one.rbegin()) == one.rend()); }  // ⑥
    std::cout << "Prev: doubly linked prev pointers walked a list backwards with no extra hops, while finding a node's predecessor in a singly linked list cost exactly its index ((n-1)(n-2)/2 hops to walk the whole list backwards); std::prev(end()), reverse_iterator base() relations and erase-through-reverse-iterator behaved as specified" << std::endl; return 0;
}
// Time Complexity: 이중 연결 O(1), 단방향 O(N)
// Space Complexity: O(1)
```

# Part 8. 메모리
## ShallowCopy()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <iostream>
#include <memory>
#include <vector>

// 얕은 복사(Shallow Copy): 객체의 멤버를 값 그대로 복사한다. 포인터 멤버는 주소만 복사되므로 원본과 복사본이 같은 메모리 블록을 가리킨다(별칭, alias). 장점은 O(1) 이라는 것, 단점은 (1) 한쪽을 고치면 다른 쪽이 바뀌고, (2) 둘 다 소멸자에서 해제하면 같은 블록을 두 번 해제(이중 해제)하며, (3) 한쪽이 먼저 해제하면 다른 쪽은 해제된 메모리를 가리키는 매달린 포인터(dangling)가 된다는 것이다. 컴파일러가 만드는 기본 복사 생성자가 바로 얕은 복사다.
// 실제 이중 해제·해제 후 사용은 정의되지 않은 동작이라 안전하게 보여 줄 수 없으므로, 이 코드는 "메모리 장부(Registry)"로 가짜 힙을 만든다. 블록마다 살아 있는지 기록하고, 이미 해제된 블록을 해제하면 이중 해제 횟수를, 해제된 블록을 읽으면 해제 후 사용 횟수를 센다. 이렇게 하면 세 가지 설계를 같은 시험으로 비교할 수 있다: (A) 기본 얕은 복사, (B) 참조 횟수(shared_ptr)로 안전하게 공유하는 얕은 복사 — 마지막 소유자가 한 번만 해제, (C) 깊은 복사.
// 검증: ① (A) 복사본을 고치면 원본에 보이고(별칭), 둘 다 소멸하면 이중 해제가 정확히 1 번, 원본이 먼저 죽으면 복사본의 읽기가 해제 후 사용으로 기록 ② (B) 같은 블록을 공유하지만 use_count 가 소유자 수를 따라가고 해제는 정확히 1 번, 이중 해제·해제 후 사용 0 ③ (C) 서로 독립이고 해제 각 1 번 ④ 복사 비용: 얕은 복사는 원소 복사 0, 깊은 복사는 정확히 n ⑤ 장부가 새는 블록(누수)을 정확히 보고.
struct Registry { struct Block { std::vector<int> data; bool live; }; std::vector<Block> blocks; int doubleReleases = 0, usesAfterRelease = 0; long elementCopies = 0;
    int alloc(std::size_t n) { blocks.push_back({std::vector<int>(n, 0), true}); return (int)blocks.size() - 1; }
    void release(int id) { if (!blocks[id].live) { doubleReleases++; return; } blocks[id].live = false; }
    int read(int id, std::size_t i) { if (!blocks[id].live) { usesAfterRelease++; return -1; } return blocks[id].data[i]; }
    void write(int id, std::size_t i, int v) { blocks[id].data[i] = v; }
    int leaks() const { int c = 0; for (const Block& b : blocks) c += b.live; return c; } };
struct ShallowBuf { Registry* r; int id; std::size_t n;                                                             // (A) 기본 복사 생성자 = 멤버별 복사(얕은 복사)
    ShallowBuf(Registry& reg, std::size_t size) : r(&reg), id(reg.alloc(size)), n(size) {} ~ShallowBuf() { r->release(id); } int get(std::size_t i) const { return r->read(id, i); } void set(std::size_t i, int v) { r->write(id, i, v); } };
struct DeepBuf { Registry* r; int id; std::size_t n;                                                                // (C) 깊은 복사
    DeepBuf(Registry& reg, std::size_t size) : r(&reg), id(reg.alloc(size)), n(size) {}
    DeepBuf(const DeepBuf& o) : r(o.r), id(o.r->alloc(o.n)), n(o.n) { for (std::size_t i = 0; i < n; i++) { r->write(id, i, r->read(o.id, i)); r->elementCopies++; } }
    DeepBuf& operator=(const DeepBuf&) = delete; ~DeepBuf() { r->release(id); } int get(std::size_t i) const { return r->read(id, i); } void set(std::size_t i, int v) { r->write(id, i, v); } };
struct SharedBlock { Registry* r; int id; SharedBlock(Registry& reg, std::size_t n) : r(&reg), id(reg.alloc(n)) {} ~SharedBlock() { r->release(id); } };   // (B) 마지막 소유자가 해제
int main() {
    { Registry reg; { ShallowBuf a(reg, 4); a.set(0, 7); ShallowBuf b = a; assert(a.id == b.id && b.get(0) == 7); b.set(1, 9); assert(a.get(1) == 9); } assert(reg.doubleReleases == 1 && reg.leaks() == 0 && reg.usesAfterRelease == 0); }   // ① 별칭 + 이중 해제
    { Registry reg; ShallowBuf* a = new ShallowBuf(reg, 4); a->set(2, 5); ShallowBuf b = *a; delete a; assert(reg.blocks[b.id].live == false && b.get(2) == -1 && reg.usesAfterRelease == 1); }                              // 원본이 먼저 죽으면 복사본은 매달림
    { Registry reg; { std::shared_ptr<SharedBlock> a = std::make_shared<SharedBlock>(reg, 4); reg.write(a->id, 0, 3); { std::shared_ptr<SharedBlock> b = a; std::shared_ptr<SharedBlock> c = b; assert(a.use_count() == 3 && a->id == c->id && reg.read(c->id, 0) == 3); reg.write(c->id, 1, 8); }   // ②
          assert(a.use_count() == 1 && reg.read(a->id, 1) == 8 && reg.blocks[a->id].live && reg.doubleReleases == 0); } assert(reg.doubleReleases == 0 && reg.usesAfterRelease == 0 && reg.leaks() == 0 && reg.blocks.size() == 1); }
    { Registry reg; { DeepBuf a(reg, 4); a.set(0, 1); DeepBuf b = a; b.set(0, 99); assert(a.get(0) == 1 && b.get(0) == 99 && a.id != b.id && reg.blocks.size() == 2); } assert(reg.doubleReleases == 0 && reg.leaks() == 0 && reg.usesAfterRelease == 0); }                // ③
    { Registry reg; const std::size_t n = 1000; ShallowBuf s(reg, n); long before = reg.elementCopies; ShallowBuf* alias = new ShallowBuf(s); assert(reg.elementCopies == before);                                                  // ④ 얕은 복사는 원소를 하나도 복사하지 않는다
      DeepBuf d(reg, n); DeepBuf d2 = d; assert(reg.elementCopies == (long)n); delete alias; assert(reg.doubleReleases == 0); }   // (alias 가 먼저 해제하고 s 가 곧 같은 블록을 다시 해제 → 범위를 벗어날 때 이중 해제가 기록된다)
    { Registry reg; ShallowBuf* kept = new ShallowBuf(reg, 3); (void)kept; assert(reg.leaks() == 1); delete kept; assert(reg.leaks() == 0); }                                                                                   // ⑤ 장부의 누수 보고
    std::cout << "ShallowCopy: with a bookkeeping heap the default member-wise copy aliased its block (writes visible through both copies), produced exactly one double release when both died and a use-after-release when the original died first; reference-counted sharing released once and a deep copy cost exactly n element copies versus zero for the shallow copy" << std::endl; return 0;
}
// Time Complexity: 얕은 복사 O(1), 깊은 복사 O(N)
// Space Complexity: 얕은 복사 O(1), 깊은 복사 O(N)
```
## DeepCopy()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <memory>
#include <new>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

// 깊은 복사(Deep Copy): 포인터가 가리키는 대상까지 새로 만들어 복사본이 원본과 완전히 독립이 되게 한다. 자원을 소유하는 클래스는 소멸자·복사 생성자·복사 대입(3 의 규칙), 이동 생성자·이동 대입(5 의 규칙)을 직접 정의해야 한다. 복사 대입은 "복사본을 만들고 교환하기"(copy-and-swap)로 쓰면 자기 대입에 안전하고 중간에 예외가 나도 대상이 바뀌지 않는다(강한 예외 보장).
// 객체의 실제 타입을 모르는 채 복사해야 하면(기반 클래스 포인터) 가상 `clone()` 이 필요하다. 그래프처럼 노드가 서로를 가리키면 단순 재귀 복사는 순환에서 영원히 돌고 공유된 노드를 여러 번 복사한다. 원본 노드 → 복사본 노드 대응표(memo)를 두면 순환이 있어도 끝나고, 공유 구조(두 노드가 같은 노드를 가리킴)가 복사본에서도 그대로 유지되며 노드 수가 늘지 않는다.
// 검증: ① 배열 소유 클래스의 복사 생성·복사 대입이 독립적이고 원소 복사 횟수가 n, 자기 대입 안전, 복사 중 k 번째 원소 복사가 예외를 던져도(모든 k) 대상의 크기·내용·생존 객체 수 불변 ② 이동은 복사 0 회 ③ 가상 clone 이 실제 파생 타입을 보존하고 독립 ④ 무작위 방향 그래프(순환·자기 루프·공유 포함)의 대응표 방식 깊은 복사가 구조 동형이고 노드 수가 같으며 복사본이 원본 노드를 가리키지 않음, 원본 변경이 복사본에 영향 없음 ⑤ 누수 없음.
struct Elem { int v; static int live, copies, failAt; Elem(int x = 0) : v(x) { ++live; } Elem(const Elem& o) : v(o.v) { if (failAt == 0) throw std::bad_alloc(); if (failAt > 0) failAt--; ++live; copies++; } Elem(Elem&& o) noexcept : v(o.v) { ++live; } ~Elem() { --live; } };
int Elem::live = 0, Elem::copies = 0, Elem::failAt = -1;
class Array { Elem* d_; std::size_t n_;
public:
    explicit Array(std::size_t n = 0) : d_(n ? static_cast<Elem*>(::operator new(n * sizeof(Elem))) : nullptr), n_(0) { for (; n_ < n; n_++) new (d_ + n_) Elem((int)n_); }
    Array(const Array& o) : d_(o.n_ ? static_cast<Elem*>(::operator new(o.n_ * sizeof(Elem))) : nullptr), n_(0) { try { for (; n_ < o.n_; n_++) new (d_ + n_) Elem(o.d_[n_]); } catch (...) { destroy(); throw; } }   // 깊은 복사
    Array(Array&& o) noexcept : d_(o.d_), n_(o.n_) { o.d_ = nullptr; o.n_ = 0; }                                       // 이동 = 포인터만 훔침
    Array& operator=(Array o) noexcept { swap(o); return *this; }                                                    // 복사 후 교환(값으로 받음): 복사는 호출 전에 끝나므로 예외가 나도 *this 불변
    ~Array() { destroy(); } void swap(Array& o) noexcept { std::swap(d_, o.d_); std::swap(n_, o.n_); }
    std::size_t size() const { return n_; } int at(std::size_t i) const { return d_[i].v; } void set(std::size_t i, int v) { d_[i].v = v; } const Elem* data() const { return d_; }
private: void destroy() { while (n_) d_[--n_].~Elem(); ::operator delete(d_); d_ = nullptr; } };
struct Shape { virtual ~Shape() { --live; } virtual std::unique_ptr<Shape> clone() const = 0; virtual int area() const = 0; static int live; Shape() { ++live; } Shape(const Shape&) { ++live; } };
int Shape::live = 0;
struct Square : Shape { int s; explicit Square(int x) : s(x) {} std::unique_ptr<Shape> clone() const override { return std::unique_ptr<Shape>(new Square(*this)); } int area() const override { return s * s; } };
struct Rect : Shape { int w, h; Rect(int a, int b) : w(a), h(b) {} std::unique_ptr<Shape> clone() const override { return std::unique_ptr<Shape>(new Rect(*this)); } int area() const override { return w * h; } };
struct GNode { int val; std::vector<GNode*> out; };
struct Graph { std::vector<GNode*> nodes; Graph() = default; Graph(const Graph&) = delete; ~Graph() { for (GNode* n : nodes) delete n; } GNode* add(int v) { nodes.push_back(new GNode{v, {}}); return nodes.back(); } };
GNode* cloneInto(const GNode* n, Graph& g, std::unordered_map<const GNode*, GNode*>& memo) { auto it = memo.find(n); if (it != memo.end()) return it->second; GNode* c = g.add(n->val); memo[n] = c; for (const GNode* m : n->out) c->out.push_back(cloneInto(m, g, memo)); return c; }   // 대응표로 순환·공유 처리
int main() {
    { Array a(8); Array b(a); assert(Elem::live == 16 && Elem::copies == 8); b.set(0, 99); assert(a.at(0) == 0 && b.at(0) == 99 && a.data() != b.data()); Array c; c = a; assert(c.size() == 8 && c.at(7) == 7 && Elem::copies == 16);      // ①
      c.set(3, -1); assert(a.at(3) == 3); a = a; assert(a.size() == 8 && a.at(5) == 5 && Elem::live == 24); }
    assert(Elem::live == 0);
    for (int k = 0; k < 6; k++) { Array src(5), dst(3); Elem::failAt = k; bool threw = false; try { dst = src; } catch (const std::bad_alloc&) { threw = true; } Elem::failAt = -1; if (k < 5) { assert(threw && dst.size() == 3 && dst.at(2) == 2 && Elem::live == 8); } else assert(!threw && dst.size() == 5); }   // 모든 k: 복사 도중 예외 → 대상 불변
    assert(Elem::live == 0);
    { Array a(1000); Elem::copies = 0; Array b(std::move(a)); assert(Elem::copies == 0 && b.size() == 1000 && a.size() == 0); Array c; c = std::move(b); assert(Elem::copies == 0 && c.size() == 1000 && b.size() == 0); }                             // ② 이동 = 복사 0
    assert(Elem::live == 0);
    { std::vector<std::unique_ptr<Shape>> shapes; shapes.emplace_back(new Square(3)); shapes.emplace_back(new Rect(2, 5)); std::vector<std::unique_ptr<Shape>> copy; for (auto& s : shapes) copy.push_back(s->clone());   // ③
      assert(copy[0]->area() == 9 && copy[1]->area() == 10 && copy[0].get() != shapes[0].get() && dynamic_cast<Square*>(copy[0].get()) && dynamic_cast<Rect*>(copy[1].get()) && Shape::live == 4); static_cast<Square*>(shapes[0].get())->s = 10; assert(copy[0]->area() == 9); }
    assert(Shape::live == 0);
    std::mt19937 rng(47);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 12); Graph g; for (int i = 0; i < n; i++) g.add(i * 10); int edges = (int)(rng() % (3 * n)); for (int e = 0; e < edges; e++) g.nodes[rng() % n]->out.push_back(g.nodes[rng() % n]);        // ④ 순환·자기 루프·중복 간선
        Graph h; std::unordered_map<const GNode*, GNode*> memo; for (const GNode* s : g.nodes) cloneInto(s, h, memo); assert(h.nodes.size() == g.nodes.size() && memo.size() == g.nodes.size());
        std::unordered_map<const GNode*, bool> inG, inH; for (GNode* x : g.nodes) inG[x] = true; for (GNode* x : h.nodes) inH[x] = true;
        for (int i = 0; i < n; i++) { const GNode* o = g.nodes[i]; GNode* c = memo.at(o); assert(c->val == o->val && c != o && inH.count(c) && !inG.count(c) && c->out.size() == o->out.size());            // 값·간선 수가 같고 복사본은 원본이 아님
            for (std::size_t j = 0; j < o->out.size(); j++) assert(c->out[j] == memo.at(o->out[j]) && inH.count(c->out[j]) && !inG.count(c->out[j])); }                                                        // 간선이 대응표대로(공유·순환 보존), 원본을 가리키지 않음
        GNode* c0 = memo.at(g.nodes[0]); int v0 = c0->val, e0 = (int)c0->out.size(); g.nodes[0]->val = -5; g.nodes[0]->out.clear(); assert(c0->val == v0 && (int)c0->out.size() == e0); }
    std::cout << "DeepCopy: a Rule-of-Five array class copied independently with exactly n element copies, survived self-assignment and copy failure at every position without changing its target, and moved with zero copies; virtual clone() preserved dynamic types; memoized graph cloning handled cycles, self-loops and shared nodes on 300 random graphs" << std::endl; return 0;
}
// Time Complexity: O(노드 수 + 간선 수)
// Space Complexity: O(노드 수) (대응표)
```
## Move()
### 대표코드
```cpp
#include <cassert>
#include <cstddef>
#include <iostream>
#include <list>
#include <memory>
#include <utility>
#include <vector>

// 이동(Move): 복사 대신 자원의 소유권을 넘긴다. 이동 생성자는 원본의 포인터를 훔치고 원본을 "빈 상태"로 만든다 — 원소를 하나도 복사하지 않으므로 크기와 무관하게 O(1) 이다. 이동된 객체는 "유효하지만 값은 미지정"인 상태로 소멸·대입은 안전해야 한다. `std::move` 자체는 아무것도 옮기지 않는 형변환(rvalue 로)이고, 실제 이동은 이동 생성자/대입이 한다.
// 구현 요령: 이동 연산은 가능하면 noexcept 로 표시한다(std::vector 가 재할당할 때 이동 생성자가 noexcept 가 아니면 강한 예외 보장을 위해 복사를 택한다). 이동 대입은 자기 이동(a = std::move(a))에도 안전해야 하고 기존 자원을 먼저 해제한다. std::exchange(p, nullptr) 로 "가져오고 비우기"를 한 줄에 쓴다. 연결 리스트를 이동하면 노드는 그대로이므로 원소를 가리키던 반복자·포인터가 이동 후에도 유효하며 이제 새 컨테이너의 것이다.
// 검증: ① 직접 만든 소유 클래스의 이동 생성·이동 대입이 복사 0 회, 원본은 빈 상태, 자기 이동 안전 ② 이동된 객체를 다시 대입하고 사용 가능 ③ 이동이 noexcept 면 vector 성장이 이동만 쓰고 noexcept 가 아니면 복사 ④ std::list 이동 뒤 반복자·원소 주소 유지, 크기가 아무리 커도(100 만) 상수 시간(연산 비용 면 복사 0) ⑤ std::swap 이 이동 세 번으로 두 객체를 O(1) 교환 ⑥ 반환값 이동(복사 없음).
struct Probe { static long copies, moves; };
long Probe::copies = 0, Probe::moves = 0;
class Buffer { int* d_; std::size_t n_;
public:
    explicit Buffer(std::size_t n = 0) : d_(n ? new int[n]() : nullptr), n_(n) {}
    Buffer(const Buffer& o) : d_(o.n_ ? new int[o.n_] : nullptr), n_(o.n_) { for (std::size_t i = 0; i < n_; i++) d_[i] = o.d_[i]; Probe::copies += (long)n_; }                                        // 복사: n 개 복사
    Buffer(Buffer&& o) noexcept : d_(std::exchange(o.d_, nullptr)), n_(std::exchange(o.n_, 0)) { Probe::moves++; }                                                                       // 이동: 소유권 이전
    Buffer& operator=(Buffer&& o) noexcept { if (this != &o) { delete[] d_; d_ = std::exchange(o.d_, nullptr); n_ = std::exchange(o.n_, 0); Probe::moves++; } return *this; }                // 자기 이동 안전, 기존 자원 해제
    Buffer& operator=(const Buffer& o) { if (this != &o) { Buffer t(o); *this = std::move(t); } return *this; } ~Buffer() { delete[] d_; }
    std::size_t size() const { return n_; } int* data() { return d_; } int& operator[](std::size_t i) { return d_[i]; } };
struct ThrowingMove { int v = 0; ThrowingMove() = default; ThrowingMove(const ThrowingMove& o) : v(o.v) { Probe::copies++; } ThrowingMove(ThrowingMove&& o) noexcept(false) : v(o.v) { Probe::moves++; } };
struct NoexceptMove { int v = 0; NoexceptMove() = default; NoexceptMove(const NoexceptMove& o) : v(o.v) { Probe::copies++; } NoexceptMove(NoexceptMove&& o) noexcept : v(o.v) { Probe::moves++; } };
Buffer make(std::size_t n) { Buffer b(n); for (std::size_t i = 0; i < n; i++) b[i] = (int)i; return b; }                                                                   // 반환: 복사 생략 또는 이동
int main() {
    { Buffer a(1000); a[5] = 42; Probe::copies = 0; Buffer b(std::move(a)); assert(Probe::copies == 0 && b.size() == 1000 && b[5] == 42 && a.size() == 0 && a.data() == nullptr);                          // ①
      Buffer c(10); c = std::move(b); assert(Probe::copies == 0 && c.size() == 1000 && c[5] == 42 && b.size() == 0); Buffer& self = c; c = std::move(self); assert(c.size() == 1000 && c[5] == 42);                     // 자기 이동 안전
      Buffer d; d = c; assert(Probe::copies == 1000 && d[5] == 42 && d.data() != c.data()); }
    { Buffer a(5); Buffer b(std::move(a)); a = Buffer(3); a[0] = 7; assert(a.size() == 3 && a[0] == 7 && b.size() == 5); Buffer e(std::move(a)); e = std::move(b); assert(e.size() == 5 && a.size() == 0 && b.size() == 0); }                    // ② 이동된 객체의 재사용
    { Probe::copies = Probe::moves = 0; std::vector<NoexceptMove> v; for (int i = 0; i < 100; i++) v.emplace_back(); assert(Probe::copies == 0 && Probe::moves > 0);                                                  // ③
      Probe::copies = Probe::moves = 0; std::vector<ThrowingMove> w; for (int i = 0; i < 100; i++) w.emplace_back(); assert(Probe::moves == 0 && Probe::copies > 0); }
    { std::list<int> a; for (int i = 0; i < 1000000; i++) a.push_back(i); auto it = std::next(a.begin(), 123456); const int* addr = &*it; std::list<int> b = std::move(a); assert(&*it == addr && *it == 123456 && b.size() == 1000000 && a.empty() && std::distance(b.begin(), it) == 123456);  // ④
      a = std::move(b); assert(&*it == addr && a.size() == 1000000 && b.empty()); }
    { Buffer x(3), y(4); x[0] = 1; y[0] = 2; Probe::copies = 0; std::swap(x, y); assert(Probe::copies == 0 && x.size() == 4 && y.size() == 3 && x[0] == 2 && y[0] == 1); }                                     // ⑤
    { Probe::copies = 0; Buffer r = make(100000); assert(Probe::copies == 0 && r.size() == 100000 && r[99999] == 99999); std::unique_ptr<int[]> p(new int[3]{1, 2, 3}); std::unique_ptr<int[]> q = std::move(p); assert(!p && q[2] == 3); }   // ⑥ 소유권 이전
    std::cout << "Move: a hand-written owner class moved with zero element copies (source left empty, safe under self-move and reusable); vector growth moved noexcept types and copied throwing-move types; moving a 1,000,000-node std::list kept every element address and iterator valid; std::swap exchanged two buffers without copying" << std::endl; return 0;
}
// Time Complexity: 이동 O(1), 복사 O(N)
// Space Complexity: O(1)
```
## Alloc()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <list>
#include <memory>
#include <new>
#include <random>
#include <vector>

// 할당(Alloc): 연결 리스트는 노드마다 `new` 를 부르면 할당자 호출이 원소 수만큼이고, 노드가 메모리 여기저기에 흩어지며, 노드마다 할당자의 부가 정보(헤더)가 붙는다. 풀(pool) 할당자는 같은 크기의 노드를 위한 큰 덩어리(chunk)를 한꺼번에 받아 두고 노드를 자유 목록(free list)으로 관리한다: 할당 = 목록 맨 앞을 떼기, 해제 = 목록 맨 앞에 달기, 둘 다 O(1) 이고 시스템 할당은 덩어리당 한 번뿐이다. 방금 해제한 노드를 가장 먼저 재사용(LIFO)해 캐시에 유리하다.
// 요점: 덩어리는 이동하지 않으므로 노드 포인터가 안정적이고, 정렬(alignment)을 지켜야 하며, 풀 자체가 소멸할 때 덩어리를 모두 돌려주어야 누수가 없다. 객체 생성은 `new (슬롯) Node(...)`(배치 new) 로 하고 파괴는 소멸자를 직접 호출한다. 생성자가 예외를 던지면 슬롯을 자유 목록으로 돌려놓는다.
// 검증: ① 풀 위에 만든 연결 리스트가 std::list 와 무작위 삽입·삭제에서 같은 내용이고 모든 노드가 정렬 조건을 만족 ② n 개를 할당하면 시스템 할당이 정확히 ⌈n/덩어리 크기⌉ 번 ③ 해제한 노드가 가장 먼저 재사용(LIFO)되고 해제·재할당을 반복해도 덩어리 수가 늘지 않음 ④ 모든 노드를 반납하면 live == 0 ⑤ 생성자가 던지면 슬롯이 반납(live 불변, 다음 할당이 같은 슬롯 재사용) ⑥ 노드 주소가 덩어리 안에서만 나오고 서로 겹치지 않음.
template <class T, std::size_t ChunkSize = 64> class Pool {
    union Slot { Slot* next; alignas(T) unsigned char storage[sizeof(T)]; }; struct Chunk { std::unique_ptr<Slot[]> slots; };
    std::vector<Chunk> chunks_; Slot* freeList_ = nullptr; std::size_t live_ = 0;
    void grow() { chunks_.push_back({std::unique_ptr<Slot[]>(new Slot[ChunkSize])}); Slot* base = chunks_.back().slots.get(); for (std::size_t i = ChunkSize; i-- > 0;) { base[i].next = freeList_; freeList_ = &base[i]; } }   // 새 덩어리를 자유 목록에 잇는다
public:
    std::size_t systemAllocs = 0;
    Pool() = default; Pool(const Pool&) = delete; Pool& operator=(const Pool&) = delete;
    template <class... A> T* create(A&&... args) { if (!freeList_) { grow(); systemAllocs++; } Slot* s = freeList_; freeList_ = s->next; try { T* p = new (static_cast<void*>(s->storage)) T(std::forward<A>(args)...); live_++; return p; } catch (...) { s->next = freeList_; freeList_ = s; throw; } }
    void destroy(T* p) { p->~T(); Slot* s = reinterpret_cast<Slot*>(p); s->next = freeList_; freeList_ = s; live_--; }
    std::size_t live() const { return live_; } std::size_t chunks() const { return chunks_.size(); }
    bool owns(const void* p) const { for (const Chunk& c : chunks_) { const unsigned char* b = reinterpret_cast<const unsigned char*>(c.slots.get()); if ((const unsigned char*)p >= b && (const unsigned char*)p < b + ChunkSize * sizeof(Slot)) return true; } return false; } };
struct Node { int val; Node* next; static int failAt, created; explicit Node(int v, Node* nx = nullptr) : val(v), next(nx) { if (failAt >= 0 && created++ >= failAt) throw std::bad_alloc(); } };
int Node::failAt = -1, Node::created = 0;
struct PooledList { Pool<Node, 32> pool; Node* head = nullptr; std::size_t n = 0; ~PooledList() { clear(); }
    void insertAt(std::size_t pos, int v) { Node** l = &head; for (std::size_t i = 0; i < pos; i++) l = &(*l)->next; *l = pool.create(v, *l); n++; }
    void eraseAt(std::size_t pos) { Node** l = &head; for (std::size_t i = 0; i < pos; i++) l = &(*l)->next; Node* dead = *l; *l = dead->next; pool.destroy(dead); n--; }
    void clear() { while (head) { Node* nx = head->next; pool.destroy(head); head = nx; } n = 0; }
    std::vector<int> items() const { std::vector<int> r; for (Node* c = head; c; c = c->next) r.push_back(c->val); return r; } };
int main() {
    std::mt19937 rng(48);
    { PooledList a; std::list<int> ref; for (int step = 0; step < 20000; step++) { std::size_t n = ref.size(); if (n == 0 || rng() % 3) { std::size_t pos = rng() % (n + 1); int v = (int)rng(); a.insertAt(pos, v); auto it = ref.begin(); std::advance(it, pos); ref.insert(it, v); }       // ①
          else { std::size_t pos = rng() % n; a.eraseAt(pos); auto it = ref.begin(); std::advance(it, pos); ref.erase(it); } assert(a.n == ref.size() && a.pool.live() == ref.size()); if (step % 997 == 0) assert(a.items() == std::vector<int>(ref.begin(), ref.end())); }
      for (Node* c = a.head; c; c = c->next) { assert(reinterpret_cast<std::uintptr_t>(c) % alignof(Node) == 0 && a.pool.owns(c)); } }                                                     // ⑥ 정렬 + 풀 소유
    for (int n : {1, 31, 32, 33, 64, 1000}) { Pool<Node, 32> p; std::vector<Node*> v; for (int i = 0; i < n; i++) v.push_back(p.create(i)); assert(p.systemAllocs == (std::size_t)((n + 31) / 32) && p.chunks() == p.systemAllocs && p.live() == (std::size_t)n);   // ②
      std::vector<std::uintptr_t> addr; for (Node* x : v) addr.push_back(reinterpret_cast<std::uintptr_t>(x)); std::sort(addr.begin(), addr.end()); for (std::size_t i = 1; i < addr.size(); i++) assert(addr[i] - addr[i - 1] >= sizeof(Node));    // 겹치지 않음
      for (Node* x : v) p.destroy(x); assert(p.live() == 0); }                                                                                                                         // ④
    { Pool<Node, 8> p; Node* a = p.create(1); Node* b = p.create(2); p.destroy(a); Node* c = p.create(3); assert(c == a && p.chunks() == 1); p.destroy(b); p.destroy(c); Node* d = p.create(4); assert(d == c); p.destroy(d);   // ③ LIFO 재사용
      for (int i = 0; i < 100000; i++) { Node* x = p.create(i); p.destroy(x); } assert(p.chunks() == 1 && p.systemAllocs == 1 && p.live() == 0); }
    { Pool<Node, 8> p; Node* a = p.create(1); Node* keep = p.create(2); p.destroy(a); Node::created = 0; Node::failAt = 0; bool threw = false; try { p.create(3); } catch (const std::bad_alloc&) { threw = true; } Node::failAt = -1;                      // ⑤
      assert(threw && p.live() == 1); Node* again = p.create(4); assert(again == a && again->val == 4 && p.live() == 2); p.destroy(again); p.destroy(keep); assert(p.live() == 0); }
    std::cout << "Alloc: a free-list pool allocator backed list matched std::list across 20000 random operations, made exactly ceil(n/chunk) system allocations, reused freed nodes in LIFO order without growing, stayed aligned and non-overlapping, and returned the slot when a constructor threw" << std::endl; return 0;
}
// Time Complexity: 할당·해제 O(1), 덩어리 확보 분할상환 O(1)
// Space Complexity: O(노드 수) (덩어리 단위)
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
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <vector>

// 가비지 컬렉션(Garbage Collection): 쓰이지 않는 메모리를 자동으로 회수한다. 방식 둘. (1) 참조 계수: 객체마다 가리키는 참조 수를 세어 0 이 되면 즉시 해제(C++ 의 shared_ptr). 단순하고 즉시 회수되지만 순환 참조(a 가 b 를, b 가 a 를 소유)는 계수가 0 이 되지 않아 영원히 샌다 — 한쪽을 weak_ptr 로 바꿔 끊어야 한다. (2) 추적(mark–sweep): 루트에서 도달 가능한 객체를 표시(mark)하고 표시되지 않은 것을 모두 해제(sweep). 순환도 문제없다.
// 연결 리스트에서 shared_ptr 의 흔한 함정: 노드 사슬을 shared_ptr 로 이으면 머리를 놓는 순간 소멸자가 다음 노드의 소멸자를 재귀로 부른다 — 깊이가 노드 수라 긴 리스트에서 스택이 넘친다. 반복문으로 하나씩 풀어 해제해야 한다. 이중 연결 리스트의 prev 는 weak_ptr(또는 원시 포인터)로 해야 순환 소유가 생기지 않는다.
// 검증: ① 단방향 shared_ptr 사슬의 소멸 재귀 깊이가 노드 수와 같음(작은 사슬로 측정), 반복 해제는 1,000,000 노드를 스택 없이 처리 ② 순환 shared_ptr 은 누수(생존 노드 수가 외부 참조를 놓은 뒤에도 남음), 한쪽 참조를 reset() 으로 끊으면 연쇄 해제되어 0 ③ 이중 연결 리스트(next 는 shared, prev 는 weak_ptr)는 처음부터 순환 소유가 없어 누수 없음 ④ mark–sweep: 무작위 객체 그래프(순환 포함)에서 해제 후 남은 집합이 루트에서의 도달 가능 집합(독립 BFS)과 같고, 해제 횟수가 도달 불가능 객체 수와 같음 ⑤ 같은 GC 를 반복 실행해도 안정적(두 번째 sweep 은 아무것도 해제 안 함)이고, 루트를 하나씩 빼며 다시 수집할 때마다 남은 집합이 독립 BFS 도달 집합과 같고 해제 수가 줄어든 만큼과 같음(표시 비트를 매번 지워야 맞다).
struct SNode { int val; std::shared_ptr<SNode> next; static int live, depth, maxDepth; explicit SNode(int v) : val(v) { ++live; } ~SNode() { ++depth; if (depth > maxDepth) maxDepth = depth; next.reset(); --depth; --live; } };       // next.reset() 이 재귀 소멸
int SNode::live = 0, SNode::depth = 0, SNode::maxDepth = 0;
void releaseIteratively(std::shared_ptr<SNode>& head) { while (head && head.use_count() == 1) { std::shared_ptr<SNode> nx = std::move(head->next); head = std::move(nx); } head.reset(); }              // 하나씩 풀어 해제(재귀 없음)
struct CNode : std::enable_shared_from_this<CNode> { int id; std::shared_ptr<CNode> peer; static int live; explicit CNode(int i) : id(i) { ++live; } ~CNode() { --live; } }; int CNode::live = 0;
struct DNode { int val; std::shared_ptr<DNode> next; std::weak_ptr<DNode> prev; static int live; explicit DNode(int v) : val(v) { ++live; } ~DNode() { --live; } }; int DNode::live = 0;
struct Obj { std::vector<int> refs; bool marked = false; bool freed = false; };
struct Heap { std::vector<Obj> objs; std::vector<int> roots; long swept = 0;
    void mark(int start) { std::vector<int> st{start}; while (!st.empty()) { int x = st.back(); st.pop_back(); if (objs[x].freed || objs[x].marked) continue; objs[x].marked = true; for (int r : objs[x].refs) st.push_back(r); } }          // 반복 DFS
    long collect() { for (Obj& o : objs) o.marked = false; for (int r : roots) mark(r); long freed = 0; for (Obj& o : objs) if (!o.freed && !o.marked) { o.freed = true; o.refs.clear(); freed++; } swept += freed; return freed; }
    std::set<int> alive() const { std::set<int> s; for (std::size_t i = 0; i < objs.size(); i++) if (!objs[i].freed) s.insert((int)i); return s; } };
int main() {
    { std::shared_ptr<SNode> head; for (int i = 0; i < 1500; i++) { auto n = std::make_shared<SNode>(i); n->next = head; head = n; } assert(SNode::live == 1500); SNode::maxDepth = 0; head.reset(); assert(SNode::live == 0 && SNode::maxDepth == 1500); }   // ① 재귀 소멸 깊이 = 노드 수
    { std::shared_ptr<SNode> head; for (int i = 0; i < 1000000; i++) { auto n = std::make_shared<SNode>(i); n->next = std::move(head); head = std::move(n); } assert(SNode::live == 1000000); releaseIteratively(head); assert(SNode::live == 0 && !head); }
    { CNode* leaked; { std::shared_ptr<CNode> a = std::make_shared<CNode>(1), b = std::make_shared<CNode>(2); a->peer = b; b->peer = a; assert(a.use_count() == 2 && CNode::live == 2); leaked = a.get(); }               // ② 순환: 외부 참조를 모두 놓아도 남는다
      assert(CNode::live == 2);                                                                                                                                                                       // 누수
      { std::shared_ptr<CNode> rescue = leaked->shared_from_this(); rescue->peer.reset(); } assert(CNode::live == 0); }                                                                              // 순환을 끊으면 연쇄 해제
    { std::shared_ptr<DNode> head; std::shared_ptr<DNode> tail; for (int i = 0; i < 100; i++) { auto n = std::make_shared<DNode>(i); if (!head) head = tail = n; else { tail->next = n; n->prev = tail; tail = n; } } assert(DNode::live == 100 && head->next->prev.lock() == head);          // ③ prev 는 weak
      tail.reset(); head.reset(); assert(DNode::live == 0); }
    std::mt19937 rng(49); long laterFreed = 0;
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 30); Heap h; h.objs.resize(n); for (int i = 0; i < n; i++) { int deg = (int)(rng() % 3); for (int d = 0; d < deg; d++) h.objs[i].refs.push_back((int)(rng() % n)); } int nr = (int)(rng() % 3); for (int r = 0; r < nr; r++) h.roots.push_back((int)(rng() % n));    // ④
        auto bfs = [&](const std::vector<int>& roots) { std::set<int> reach(roots.begin(), roots.end()); std::vector<int> q(roots.begin(), roots.end()); for (std::size_t i = 0; i < q.size(); i++) for (int t : h.objs[q[i]].refs) if (reach.insert(t).second) q.push_back(t); return reach; };   // 독립 BFS
        std::set<int> reach = bfs(h.roots); long freed = h.collect(); assert(h.alive() == reach && freed == (long)(n - (int)reach.size()));
        assert(h.collect() == 0 && h.alive() == reach);                                                                                                  // ⑤ 반복 실행해도 안정
        while (!h.roots.empty()) { h.roots.pop_back(); std::set<int> next = bfs(h.roots); long f = h.collect(); assert(h.alive() == next && f == (long)(reach.size() - next.size())); laterFreed += f; reach = next; } }       // 루트를 하나씩 빼며 재수집: 표시 비트를 지워야 맞다
    assert(laterFreed > 0);                                                                                                                                                // 루트를 빼는 단계가 실제로 객체를 해제했다
    std::cout << "GarbageCollection: a shared_ptr chain's destructor recursed to depth n (1500) and an iterative release freed 1,000,000 nodes without recursion; a shared_ptr cycle leaked until one reference was reset(), doubly linked lists with weak prev pointers leaked nothing, and mark-and-sweep on 300 random object graphs freed exactly the unreachable objects (cycles included), again after each root was dropped in turn (" << laterFreed << " more objects freed)" << std::endl; return 0;
}
// Time Complexity: 참조 계수 갱신 O(1), mark–sweep O(전체 객체 + 참조)
// Space Complexity: 참조 계수 O(1) 추가, mark–sweep O(표시 비트 + DFS 스택)
```

# Part 9. 함수형 리스트
## Map()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <iterator>
#include <memory>
#include <random>
#include <vector>

// 맵(Map): 리스트의 모든 원소에 같은 함수를 적용해 같은 길이의 새 리스트를 만든다 — map(f, [a, b, c]) = [f(a), f(b), f(c)]. 원본은 바뀌지 않는다(불변 리스트에서는 새 리스트를 돌려주고, 제자리 버전은 std::transform 으로 덮어씀). 순서와 길이가 보존되고 원소 하나의 결과는 다른 원소에 의존하지 않으므로 병렬화가 자연스럽다.
// 법칙(함수자 법칙): map(항등) = 항등, map(f∘g) = map(f)∘map(g) — 두 번 훑는 대신 합성해서 한 번만 훑어도 같다(융합, fusion). 길이 보존 |map(f, xs)| = |xs|. 게으른 맵은 새 리스트를 만들지 않고 읽는 순간에만 f 를 적용하는 뷰라서, 앞의 k 개만 쓰면 f 호출도 k 번뿐이다(즉시 맵은 n 번).
// 이 코드는 불변 단방향 리스트(cons 셀 + shared_ptr, 꼬리 공유)를 쓴다: 셀은 만들어진 뒤 바뀌지 않으므로 여러 리스트가 같은 꼬리를 안전하게 공유한다.
// 검증: ① 무작위 입력에서 map 이 std::transform 결과와 같고 원본이 불변 ② 함자 법칙: map(id) = id, map(f∘g) = map(f)∘map(g), 길이 보존 ③ 빈 리스트 ④ 게으른 뷰: 앞 k 개만 소비하면 f 가 정확히 k 번 호출, 즉시 맵은 n 번 ⑤ 새 셀 수가 정확히 n(원본 셀 재사용 없음, 원본은 그대로 살아 있음), 모든 셀 해제 후 누수 없음 ⑥ 서로 다른 타입으로의 변환(int → 문자열 길이 등).
struct Cell; typedef std::shared_ptr<const Cell> L;
struct Cell { int head; L tail; static int live; Cell(int h, L t) : head(h), tail(std::move(t)) { ++live; } ~Cell() { --live; } }; int Cell::live = 0;
L cons(int h, L t) { return std::make_shared<const Cell>(h, std::move(t)); }
L fromVector(const std::vector<int>& v) { L r; for (std::size_t i = v.size(); i-- > 0;) r = cons(v[i], r); return r; }
std::vector<int> toVector(L l) { std::vector<int> r; for (const Cell* c = l.get(); c; c = c->tail.get()) r.push_back(c->head); return r; }
template <class F> L mapL(const L& l, F f) { std::vector<int> out; for (const Cell* c = l.get(); c; c = c->tail.get()) out.push_back(f(c->head)); return fromVector(out); }       // 새 리스트: 원본 불변
template <class F> struct MapView { const L& src; F f; mutable long* calls;                                                                        // 게으른 맵: 읽을 때 적용
    struct It { const Cell* c; const MapView* v; int operator*() const { ++*v->calls; return v->f(c->head); } It& operator++() { c = c->tail.get(); return *this; } bool operator!=(const It& o) const { return c != o.c; } };
    It begin() const { return It{src.get(), this}; } It end() const { return It{nullptr, this}; } };
int main() {
    std::mt19937 rng(50);
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 40); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 2001) - 1000; L l = fromVector(v); auto f = [](int x) { return x * 3 - 1; }; auto g = [](int x) { return x / 2 + 7; };
        std::vector<int> want(n); std::transform(v.begin(), v.end(), want.begin(), f); L m = mapL(l, f); assert(toVector(m) == want && toVector(l) == v);                                                   // ① 원본 불변
        assert(toVector(mapL(l, [](int x) { return x; })) == v);                                                                                                                             // ② map(id) = id
        std::vector<int> composed(n); for (int i = 0; i < n; i++) composed[i] = f(g(v[i])); assert(toVector(mapL(mapL(l, g), f)) == composed && toVector(mapL(l, [&](int x) { return f(g(x)); })) == composed);        // map(f∘g) = map f ∘ map g
        assert((int)toVector(m).size() == n); }
    { L e; assert(mapL(e, [](int x) { return x + 1; }) == nullptr && toVector(mapL(e, [](int x) { return x; })).empty()); }                                                                  // ③
    { std::vector<int> v(1000); for (int i = 0; i < 1000; i++) v[i] = i; L l = fromVector(v); long lazyCalls = 0; MapView<std::function<int(int)>> view{l, [](int x) { return x * x; }, &lazyCalls}; int taken = 0; long sum = 0; for (auto it = view.begin(); it != view.end() && taken < 10; ++it, ++taken) sum += *it;   // ④
      assert(lazyCalls == 10 && sum == 285); long eagerCalls = 0; mapL(l, [&](int x) { ++eagerCalls; return x * x; }); assert(eagerCalls == 1000); }
    { std::vector<int> v(200, 5); L l = fromVector(v); assert(Cell::live == 200); L m = mapL(l, [](int x) { return x + 1; }); assert(Cell::live == 400); m.reset(); assert(Cell::live == 200 && toVector(l) == v); l.reset(); assert(Cell::live == 0);       // ⑤
      L shared = fromVector({1, 2, 3}); L a = cons(0, shared), b = cons(9, shared); assert(a->tail == b->tail && a->tail == shared && Cell::live == 5); L ma = mapL(a, [](int x) { return x * 10; }); assert(toVector(ma) == (std::vector<int>{0, 10, 20, 30}) && toVector(b) == (std::vector<int>{9, 1, 2, 3})); }
    { std::vector<int> v = {1, 22, 333}; std::vector<std::size_t> lens; for (int x : v) lens.push_back(std::to_string(x).size()); L l = fromVector(v); auto m = mapL(l, [](int x) { return (int)std::to_string(x).size(); }); assert(toVector(m) == (std::vector<int>{1, 2, 3}) && lens.size() == 3); }    // ⑥
    assert(Cell::live == 0); std::cout << "Map: on an immutable cons list, map matched std::transform without touching its input, satisfied the functor laws (identity and composition) and preserved length, shared tails between lists stayed intact, a lazy view called the function exactly as often as elements were read (10 versus 1000 for the eager map), and no cell leaked" << std::endl; return 0;
}
// Time Complexity: O(N) (게으른 뷰는 읽는 만큼)
// Space Complexity: 즉시 맵 O(N) 새 셀, 게으른 뷰 O(1)
```
## Filter()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <memory>
#include <random>
#include <vector>

// 필터(Filter): 조건(술어)을 만족하는 원소만 남긴다 — filter(p, xs) 는 xs 의 부분열(순서 유지, 안정적)이다. 길이는 줄어들 수 있고, filter(참) = 항등, filter(거짓) = 빈 리스트. 법칙: filter(p)∘filter(q) = filter(p ∧ q) (두 번 훑을 것을 한 번으로 융합), filter(p) 와 filter(¬p) 의 길이 합 = n 이며 둘을 합치면 원래 원소의 다중집합.
// 불변 리스트에서의 최적화: 어떤 위치부터 끝까지 모든 원소가 조건을 통과하면 그 꼬리 셀들을 새로 만들지 않고 원본 꼬리를 그대로 공유한다. 전부 통과하면 원본 리스트를 그대로 돌려줄 수 있고(새 셀 0), 전부 거르면 빈 리스트다. 공유는 불변이기 때문에 안전하다.
// 검증: ① 무작위 입력에서 filter 가 std::copy_if 와 같고 순서 유지(안정) ② 법칙: filter(p)∘filter(q) = filter(p∧q), |filter(p)| + |filter(¬p)| = n, 항등·빈 결과 ③ 꼬리 공유: 새 셀 수가 (마지막으로 걸러진 원소까지의 앞부분 중 통과 개수)이고, 전부 통과하면 같은 포인터를 반환, 공유된 꼬리는 원본 셀의 주소와 같음 ④ 원본 불변·누수 없음 ⑤ 전부 거르기·빈 리스트 ⑥ 연속 적용(체인)이 같은 결과.
struct Cell; typedef std::shared_ptr<const Cell> L;
struct Cell { int head; L tail; static int live; Cell(int h, L t) : head(h), tail(std::move(t)) { ++live; } ~Cell() { --live; } }; int Cell::live = 0;
L cons(int h, L t) { return std::make_shared<const Cell>(h, std::move(t)); }
L fromVector(const std::vector<int>& v) { L r; for (std::size_t i = v.size(); i-- > 0;) r = cons(v[i], r); return r; }
std::vector<int> toVector(const L& l) { std::vector<int> r; for (const Cell* c = l.get(); c; c = c->tail.get()) r.push_back(c->head); return r; }
template <class P> L filterL(const L& l, P p) {                                                                     // 꼬리 공유 최적화 포함
    std::vector<const Cell*> cells; for (const Cell* c = l.get(); c; c = c->tail.get()) cells.push_back(c);
    std::size_t lastDropped = cells.size();                                                                         // 마지막으로 걸러진 위치 (없으면 n)
    for (std::size_t i = cells.size(); i-- > 0;) if (!p(cells[i]->head)) { lastDropped = i; break; }
    if (lastDropped == cells.size()) return l;                                                                      // 전부 통과 → 원본 그대로
    L tail; if (lastDropped + 1 < cells.size()) { const L* cursor = &l; for (std::size_t i = 0; i < lastDropped + 1; i++) cursor = &(*cursor)->tail; tail = *cursor; }   // lastDropped 뒤의 원본 꼬리를 공유
    std::vector<int> kept; for (std::size_t i = 0; i <= lastDropped; i++) if (p(cells[i]->head)) kept.push_back(cells[i]->head);
    L r = tail; for (std::size_t i = kept.size(); i-- > 0;) r = cons(kept[i], r); return r; }
int main() {
    std::mt19937 rng(51);
    for (int rep = 0; rep < 500; rep++) { int n = (int)(rng() % 40); std::vector<int> v(n); for (int& x : v) x = (int)(rng() % 100); L l = fromVector(v); int m = 2 + (int)(rng() % 5);
        auto p = [m](int x) { return x % m == 0; }; auto q = [](int x) { return x > 30; }; auto notp = [m](int x) { return x % m != 0; };
        std::vector<int> want; std::copy_if(v.begin(), v.end(), std::back_inserter(want), p); L f = filterL(l, p); assert(toVector(f) == want && toVector(l) == v);                                         // ①
        std::vector<int> both; std::copy_if(v.begin(), v.end(), std::back_inserter(both), [&](int x) { return p(x) && q(x); }); assert(toVector(filterL(filterL(l, p), q)) == both && toVector(filterL(l, [&](int x) { return p(x) && q(x); })) == both);   // ②
        L neg = filterL(l, notp); assert(toVector(f).size() + toVector(neg).size() == (std::size_t)n); std::vector<int> merged = toVector(f), r2 = toVector(neg); merged.insert(merged.end(), r2.begin(), r2.end()); std::vector<int> sortedV = v; std::sort(sortedV.begin(), sortedV.end()); std::sort(merged.begin(), merged.end()); assert(merged == sortedV);
        assert(toVector(filterL(l, [](int) { return true; })) == v && filterL(l, [](int) { return false; }) == nullptr); }
    { std::vector<int> v = {1, 2, 3, 4, 5, 6, 7, 8}; L l = fromVector(v); int before = Cell::live; L all = filterL(l, [](int) { return true; }); assert(all == l && Cell::live == before);                                                            // ③ 전부 통과
      L f = filterL(l, [](int x) { return x != 3; }); assert(toVector(f) == (std::vector<int>{1, 2, 4, 5, 6, 7, 8}) && Cell::live == before + 2);                                                                              // 3 이 마지막으로 걸러짐 → 앞의 1, 2 만 새 셀
      const Cell* origFour = l->tail->tail->tail.get(); const Cell* c = f.get(); c = c->tail.get(); c = c->tail.get(); assert(c == origFour);                                                                                  // 꼬리 [4..8] 은 원본 셀을 그대로 공유
      L g = filterL(l, [](int x) { return x != 8; }); assert(toVector(g) == (std::vector<int>{1, 2, 3, 4, 5, 6, 7}) && Cell::live == before + 2 + 7); }                                                                         // 마지막 원소가 걸러지면 공유할 꼬리가 없다
    assert(Cell::live == 0);
    { L e; assert(filterL(e, [](int) { return true; }) == nullptr); std::vector<int> v(100, 1); L l = fromVector(v); L none = filterL(l, [](int x) { return x != 1; }); assert(none == nullptr && toVector(l) == v); }                  // ④ ⑤
    { std::vector<int> v(60); for (int i = 0; i < 60; i++) v[i] = i; L l = fromVector(v); L c = filterL(filterL(filterL(l, [](int x) { return x % 2 == 0; }), [](int x) { return x % 3 == 0; }), [](int x) { return x > 10; }); assert(toVector(c) == (std::vector<int>{12, 18, 24, 30, 36, 42, 48, 54})); }   // ⑥
    assert(Cell::live == 0); std::cout << "Filter: on an immutable cons list, filter matched std::copy_if (stable, input untouched), obeyed the fusion and partition laws, returned the original pointer when nothing was removed, and shared the unfiltered tail cells with the source instead of copying them" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: 새 셀 O(통과한 앞부분), 공유 꼬리 O(1)
```
## Reduce()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

// 리듀스(Reduce / fold): 리스트를 이항 연산으로 하나의 값으로 접는다. foldLeft(f, init, [a, b, c]) = f(f(f(init, a), b), c), foldRight(f, [a, b, c], init) = f(a, f(b, f(c, init))). 초기값을 주면 빈 리스트도 처리하고(결과 = init), 초기값 없이는 빈 리스트에서 정의되지 않는다(예외나 optional). 합·곱·최댓값·연결이 모두 fold 이고, 길이·map·filter·reverse 도 fold 로 쓸 수 있다.
// 연산이 결합 법칙(associative)을 만족하면 foldLeft = foldRight 이고, 리스트를 조각으로 나누어 각각 접은 뒤 결과를 접어도 같다 — 병렬 리듀스(트리 리듀스)의 근거다. 뺄셈처럼 결합 법칙이 없으면 접는 방향과 조각 나누기에 따라 결과가 달라진다. 부동소수점 덧셈은 이름만 결합적이고 실제로는 아니다: 단순 누적은 큰 합 앞에서 작은 값을 잃어 오차가 쌓이고, 두 조각씩 짝지어 합치는 쌍대 합(pairwise)은 오차가 O(log n) 이다.
// 검증: ① foldLeft/foldRight 가 std::accumulate 와 같은 결과(합·곱·최댓값·문자열 연결) ② fold 로 쓴 length/map/filter/reverse 가 직접 구현과 같음 ③ 결합 연산(+, max, 연결)에서 foldLeft = foldRight = 조각 병렬 리듀스(2~7 조각), 비결합(−)에서는 서로 다른 결과가 실제로 존재 ④ 초기값 없는 리듀스가 빈 리스트에서 예외, 원소 1개에서는 그 원소 ⑤ float 100 만 개(0.1f)의 단순 누적 오차가 쌍대 합의 100 배 이상 ⑥ 10 만 원소도 재귀 없이 처리.
template <class A, class T, class F> A foldLeft(const std::vector<T>& v, A init, F f) { for (const T& x : v) init = f(init, x); return init; }
template <class A, class T, class F> A foldRight(const std::vector<T>& v, A init, F f) { for (std::size_t i = v.size(); i-- > 0;) init = f(v[i], init); return init; }
template <class T, class F> T reduceNoInit(const std::vector<T>& v, F f) { if (v.empty()) throw std::invalid_argument("reduce of empty list with no initial value"); T acc = v[0]; for (std::size_t i = 1; i < v.size(); i++) acc = f(acc, v[i]); return acc; }
template <class T, class F> T chunkedReduce(const std::vector<T>& v, int chunks, T identity, F f) { std::size_t n = v.size(); std::vector<T> partial; for (int c = 0; c < chunks; c++) { std::size_t lo = n * c / chunks, hi = n * (c + 1) / chunks; T acc = identity; for (std::size_t i = lo; i < hi; i++) acc = f(acc, v[i]); partial.push_back(acc); } T r = identity; for (const T& p : partial) r = f(r, p); return r; }
float pairwiseSum(const float* a, std::size_t n) { if (n <= 8) { float s = 0; for (std::size_t i = 0; i < n; i++) s += a[i]; return s; } std::size_t h = n / 2; return pairwiseSum(a, h) + pairwiseSum(a + h, n - h); }
int main() {
    std::mt19937 rng(52);
    for (int rep = 0; rep < 400; rep++) { int n = (int)(rng() % 30); std::vector<long long> v(n); for (auto& x : v) x = (long long)(rng() % 21) - 10; auto add = [](long long a, long long b) { return a + b; }; auto mx = [](long long a, long long b) { return std::max(a, b); };           // ①
        assert(foldLeft<long long>(v, 0, add) == std::accumulate(v.begin(), v.end(), 0LL) && foldRight<long long>(v, 0, add) == std::accumulate(v.begin(), v.end(), 0LL)); long long prod = 1; for (auto x : v) prod *= (x % 3); assert(foldLeft<long long>(v, 1, [](long long a, long long b) { return a * (b % 3); }) == prod);
        if (n) { assert(foldLeft<long long>(v, v[0], mx) == *std::max_element(v.begin(), v.end()) && reduceNoInit<long long>(v, mx) == *std::max_element(v.begin(), v.end())); }
        std::vector<std::string> s; for (auto x : v) s.push_back(std::to_string(x)); std::string cat; for (auto& t : s) cat += t; assert(foldLeft<std::string>(s, "", [](std::string a, const std::string& b) { return a + b; }) == cat && foldRight<std::string>(s, "", [](const std::string& a, std::string b) { return a + b; }) == cat);
        auto lenFold = foldLeft<long long>(v, 0, [](long long a, long long) { return a + 1; }); assert(lenFold == n);                                                                         // ② fold 로 length/map/filter/reverse
        std::vector<long long> mapped = foldRight<std::vector<long long>>(v, {}, [](long long x, std::vector<long long> acc) { acc.insert(acc.begin(), x * 2); return acc; }); std::vector<long long> wantMap; for (auto x : v) wantMap.push_back(x * 2); assert(mapped == wantMap);
        std::vector<long long> filtered = foldLeft<std::vector<long long>>(v, {}, [](std::vector<long long> acc, long long x) { if (x > 0) acc.push_back(x); return acc; }); std::vector<long long> wantFilt; for (auto x : v) if (x > 0) wantFilt.push_back(x); assert(filtered == wantFilt);
        std::vector<long long> rev = foldLeft<std::vector<long long>>(v, {}, [](std::vector<long long> acc, long long x) { acc.insert(acc.begin(), x); return acc; }); assert(rev == std::vector<long long>(v.rbegin(), v.rend()));
        for (int chunks = 2; chunks <= 7; chunks++) { assert(chunkedReduce<long long>(v, chunks, 0, add) == foldLeft<long long>(v, 0, add)); assert(chunkedReduce<long long>(v, chunks, std::numeric_limits<long long>::min(), mx) == (n ? *std::max_element(v.begin(), v.end()) : std::numeric_limits<long long>::min())); } }   // ③ 결합 연산: 조각 병렬 리듀스 = 순차
    { auto sub = [](long long a, long long b) { return a - b; }; std::vector<long long> v = {10, 3, 2, 1}; assert(foldLeft<long long>(v, 0, sub) == -16 && foldRight<long long>(v, 0, [](long long a, long long b) { return a - b; }) == 10 - (3 - (2 - (1 - 0))) && foldLeft<long long>(v, 0, sub) != foldRight<long long>(v, 0, sub));       // 비결합: 방향마다 다름
      assert(chunkedReduce<long long>(v, 2, 0, sub) != foldLeft<long long>(v, 0, sub)); }
    { bool threw = false; try { reduceNoInit<int>({}, [](int a, int b) { return a + b; }); } catch (const std::invalid_argument&) { threw = true; } assert(threw && reduceNoInit<int>({7}, [](int a, int b) { return a + b; }) == 7 && foldLeft<int>(std::vector<int>{}, 42, [](int a, int b) { return a + b; }) == 42); }       // ④
    { std::size_t n = 1000000; std::vector<float> a(n, 0.1f); float naive = 0; for (float x : a) naive += x; float pair = pairwiseSum(a.data(), n); double exact = (double)0.1f * (double)n; double errNaive = std::abs((double)naive - exact), errPair = std::abs((double)pair - exact); assert(errNaive > 100 * errPair && errPair < 1.0 && errNaive > 100.0); }      // ⑤
    { std::vector<long long> big(100000); std::iota(big.begin(), big.end(), 1); assert(foldLeft<long long>(big, 0, [](long long a, long long b) { return a + b; }) == 100000LL * 100001 / 2 && foldRight<long long>(big, 0, [](long long a, long long b) { return a + b; }) == 100000LL * 100001 / 2); }   // ⑥
    std::cout << "Reduce: foldLeft and foldRight matched std::accumulate for sums, products, maxima and string concatenation; length, map, filter and reverse written as folds matched direct versions; associative operators gave identical results sequentially and as 2-7 parallel chunks while subtraction did not; float summation drifted by a factor over 100 in the naive loop compared with pairwise summation" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1) (쌍대 합은 재귀 O(log N))
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 평탄화(Flatten): 중첩된 구조를 한 줄로 편다. (1) 한 단계: 리스트의 리스트를 이어 붙인 하나의 리스트로 — flatten([[1,2],[3],[],[4,5]]) = [1,2,3,4,5], flatMap(f) = flatten(map(f)). (2) 깊이를 모르는 중첩: 원소가 숫자이거나 다시 리스트인 구조를 깊이 우선 순서의 숫자열로. 재귀가 쉽지만 깊이가 깊으면 호출 스택이 넘치므로 명시적 스택으로 바꾼다. (3) 연결 리스트의 자식 포인터: 노드가 next/prev 외에 child(아래 층 리스트의 머리)를 가질 때 모든 층을 한 줄의 이중 연결 리스트로 편다 — 노드의 자식 리스트를 그 노드 바로 뒤에 끼워 넣는 일이다.
// 다층 연결 리스트 평탄화는 자식이 있는 노드를 만나면 자식 리스트를 그 노드와 그 노드의 next 사이에 잇고 child 를 비운다. 새 노드를 만들지 않고 연결만 바꾸므로 O(n) 시간, 명시적 스택(또는 반복 처리)이면 추가 공간 O(깊이). 결과는 깊이 우선 전위 순서다.
// 검증: ① 한 단계 평탄화·flatMap 이 직접 이어 붙이기와 같고 길이 합이 보존(빈 안쪽 리스트 포함) ② 무작위 중첩 구조(깊이 ≤ 6)에서 반복(명시적 스택) 평탄화 == 재귀 평탄화 == 정의에 따른 전위 열거 ③ 깊이 3000 의 사슬도 반복 평탄화는 스택을 쓰지 않고 처리 ④ 다층 연결 리스트 평탄화: 결과 순서가 전위 순회와 같고 prev/next 가 서로 일치하며 child 가 모두 비워지고 노드가 보존 ⑤ 빈 구조·한 단계도 없는 구조.
struct Nested { bool leaf; int v; std::vector<Nested> kids; static Nested num(int x) { return Nested{true, x, {}}; } static Nested list(std::vector<Nested> k) { return Nested{false, 0, std::move(k)}; } };
void flattenRec(const Nested& n, std::vector<int>& out) { if (n.leaf) { out.push_back(n.v); return; } for (const Nested& k : n.kids) flattenRec(k, out); }
std::vector<int> flattenIter(const Nested& root) { std::vector<int> out; std::vector<std::pair<const Nested*, std::size_t>> st; st.push_back({&root, 0}); if (root.leaf) { out.push_back(root.v); return out; }
    while (!st.empty()) { auto& top = st.back(); if (top.second == top.first->kids.size()) { st.pop_back(); continue; } const Nested* k = &top.first->kids[top.second++]; if (k->leaf) out.push_back(k->v); else st.push_back({k, 0}); } return out; }
Nested randomNested(std::mt19937& rng, int depth) { if (depth == 0 || rng() % 3 == 0) return Nested::num((int)(rng() % 100)); std::vector<Nested> k; int n = (int)(rng() % 4); for (int i = 0; i < n; i++) k.push_back(randomNested(rng, depth - 1)); return Nested::list(std::move(k)); }
std::vector<int> oracle(const Nested& n) { if (n.leaf) return {n.v}; std::vector<int> r; for (const Nested& k : n.kids) { std::vector<int> s = oracle(k); r.insert(r.end(), s.begin(), s.end()); } return r; }
template <class T> std::vector<T> flatten1(const std::vector<std::vector<T>>& vv) { std::vector<T> out; std::size_t total = 0; for (auto& v : vv) total += v.size(); out.reserve(total); for (auto& v : vv) out.insert(out.end(), v.begin(), v.end()); return out; }
struct MNode { int val; MNode *prev, *next, *child; static int live; explicit MNode(int v) : val(v), prev(nullptr), next(nullptr), child(nullptr) { ++live; } ~MNode() { --live; } }; int MNode::live = 0;
MNode* buildLevel(std::mt19937& rng, int depth, int& counter, std::vector<MNode*>& all) { int n = 1 + (int)(rng() % 4); MNode *head = nullptr, *tail = nullptr; for (int i = 0; i < n; i++) { MNode* x = new MNode(counter++); all.push_back(x); x->prev = tail; if (tail) tail->next = x; else head = x; tail = x; if (depth > 0 && rng() % 3 == 0) x->child = buildLevel(rng, depth - 1, counter, all); } return head; }
void preorder(const MNode* h, std::vector<int>& out) { for (; h; h = h->next) { out.push_back(h->val); preorder(h->child, out); } }
MNode* flattenMulti(MNode* head) { std::vector<MNode*> st; MNode* cur = head; while (cur) { if (cur->child) { if (cur->next) st.push_back(cur->next); cur->next = cur->child; cur->child->prev = cur; cur->child = nullptr; }
        if (!cur->next && !st.empty()) { cur->next = st.back(); st.pop_back(); cur->next->prev = cur; } cur = cur->next; } return head; }                                       // 자식 리스트를 노드 뒤에 끼우고, 나중에 원래 next 로 이어 줌
int main() {
    std::mt19937 rng(53);
    for (int rep = 0; rep < 300; rep++) { int k = (int)(rng() % 6); std::vector<std::vector<int>> vv(k); std::size_t total = 0; for (auto& v : vv) { v.resize(rng() % 5); for (int& x : v) x = (int)(rng() % 100); total += v.size(); } std::vector<int> want; for (auto& v : vv) for (int x : v) want.push_back(x);   // ①
        std::vector<int> f = flatten1(vv); assert(f == want && f.size() == total); std::vector<int> fm; for (int i = 0; i < k; i++) { std::vector<int> r = {i, i * 10}; fm.insert(fm.end(), r.begin(), r.end()); } std::vector<std::vector<int>> mapped; for (int i = 0; i < k; i++) mapped.push_back({i, i * 10}); assert(flatten1(mapped) == fm); }
    for (int rep = 0; rep < 800; rep++) { Nested n = randomNested(rng, 6); std::vector<int> a, b = oracle(n); flattenRec(n, a); assert(a == b && flattenIter(n) == b); }                                                                  // ②
    assert(flattenIter(Nested::list({})).empty() && flattenIter(Nested::list({Nested::list({}), Nested::list({Nested::list({})})})).empty() && flattenIter(Nested::num(5)) == std::vector<int>{5});                                  // ⑤
    { Nested chain = Nested::num(7); for (int i = 0; i < 3000; i++) { std::vector<Nested> k; k.push_back(Nested::num(i)); k.push_back(std::move(chain)); chain = Nested::list(std::move(k)); } std::vector<int> r = flattenIter(chain); assert(r.size() == 3001 && r.front() == 2999 && r.back() == 7); }   // ③ 깊이 3000
    for (int rep = 0; rep < 400; rep++) { std::vector<MNode*> all; int counter = 0; MNode* head = buildLevel(rng, 4, counter, all); std::vector<int> want; preorder(head, want); flattenMulti(head);                                    // ④
        std::vector<int> got; MNode* last = nullptr; for (MNode* c = head; c; c = c->next) { assert(c->child == nullptr && (c == head ? c->prev == nullptr : c->prev == last)); got.push_back(c->val); last = c; } assert(got == want && got.size() == all.size() && (int)all.size() == MNode::live);
        for (MNode* x : all) delete x; assert(MNode::live == 0); }
    { MNode* n = nullptr; assert(flattenMulti(n) == nullptr); }
    std::cout << "Flatten: one-level flatten and flatMap matched manual concatenation; iterative flattening with an explicit stack equalled the recursive version and the definition on 800 random nested structures and handled a depth-3000 chain; flattening multilevel doubly linked lists relinked 400 random lists into preorder with consistent prev/next, no child pointers left and no node lost" << std::endl; return 0;
}
// Time Complexity: O(전체 원소 수)
// Space Complexity: 한 단계 O(N), 반복 중첩 평탄화 O(깊이), 다층 연결 리스트 O(깊이)
```

# Part 10. 학사과정을 넘어
## SkipList()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <cmath>
#include <cstdio>
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
std::string levelsPicture(const SkipList& s) {                         // 그림: 맨 아래 줄이 전체, 위 줄일수록 듬성듬성한 "고속도로" (점은 그 줄에 없는 키)
    std::vector<int> keys; for (const SkipList::Node* x = s.head->next[0]; x; x = x->next[0]) keys.push_back(x->key);
    std::string out; char buf[16];
    for (int lv = s.level - 1; lv >= 0; --lv) {
        std::snprintf(buf, sizeof buf, "L%d:", lv + 1); out += buf; const SkipList::Node* x = s.head->next[lv];
        for (int k : keys) { if (x && x->key == k) { std::snprintf(buf, sizeof buf, "%3d", k); x = x->next[lv]; } else std::snprintf(buf, sizeof buf, "%3s", "."); out += buf; }
        out += "\n";
    }
    return out;
}
int main() {
    {   SkipList demo(5); for (int k : {9, 3, 12, 1, 5, 7, 15, 11}) demo.insert(k);                       // 키 8 개, 층 높이는 동전 던지기(시드 고정)
        const std::string pic = levelsPicture(demo);
        assert(pic == "L3:  .  3  .  .  .  .  .  .\nL2:  .  3  5  .  9 11  . 15\nL1:  1  3  5  7  9 11 12 15\n");   // std::mt19937 은 표준이 출력값까지 정하므로 시드가 같으면 어느 플랫폼에서나 같은 그림
        std::vector<int> all; for (const SkipList::Node* x = demo.head->next[0]; x; x = x->next[0]) all.push_back(x->key);
        assert((all == std::vector<int>{1, 3, 5, 7, 9, 11, 12, 15}));                                   // 맨 아래 줄 = 정렬된 전체
        for (int lv = 1; lv < demo.level; ++lv) {                                                      // 위 줄의 키는 모두 바로 아래 줄에도 있다 (부분 수열)
            const SkipList::Node* up = demo.head->next[lv]; const SkipList::Node* lo = demo.head->next[lv - 1];
            for (; up; up = up->next[lv]) { while (lo && lo->key != up->key) lo = lo->next[lv - 1]; assert(lo); }
        }
        std::cout << pic; }
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
#include <cassert>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 로프(리스트 관점의 요약, 정본은 String.md Part 4): 긴 문자열을 이진 트리로 나타내고 연결은 새 루트 하나, 분할·색인은 O(깊이). 노드가 불변이라 편집 전 버전과 구조를 공유한다 — 편집은 분할(split)과 연결(concat)의 조합이다: 삽입 = 분할 + 연결 + 연결, 삭제 = 분할 두 번 + 연결. 문자열(연속 메모리)에서 중간 삽입이 O(n) 이동인 것에 비해 로프는 O(깊이)에 노드 몇 개만 만든다.
// 검증: 무작위 삽입·삭제·연결을 std::string 모델과 비교하고(길이·내용·임의 위치의 문자), 편집 전에 찍어 둔 스냅샷(이전 버전)이 이후 수백 번의 편집이 끝난 뒤에도 그대로임을 확인한다(영속성). 정본의 균형 잡기·병합 최적화는 String.md 참조.
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
char at(const P& p, size_t i) { return !p->l ? p->s[i] : i < len(p->l) ? at(p->l, i) : at(p->r, i - len(p->l)); }
P insertAt(const P& doc, size_t pos, const std::string& text) { auto t = split(doc, pos); return cat(cat(t.first, leaf(text)), t.second); }
P eraseRange(const P& doc, size_t pos, size_t count) { auto a = split(doc, pos); auto b = split(a.second, count); return cat(a.first, b.second); }
int main() {
    P doc = cat(leaf("Hello, "), leaf("world!")); auto [a, b] = split(doc, 7);
    P edited = cat(cat(a, leaf("rope ")), b);                              // 중간 삽입 = 분할 + 연결
    assert(str(edited) == "Hello, rope world!" && str(doc) == "Hello, world!");
    std::mt19937 rng(54); P cur = leaf("seed text"); std::string ref = "seed text"; std::vector<std::pair<P, std::string>> snaps;
    for (int step = 0; step < 600; step++) { int op = (int)(rng() % 4);
        if (step % 25 == 0) snaps.push_back({cur, ref});                                                          // 버전 스냅샷
        if (op <= 1 || ref.empty()) { size_t pos = rng() % (ref.size() + 1); std::string t; for (int i = 0, k = 1 + (int)(rng() % 6); i < k; i++) t += (char)('a' + rng() % 26); cur = insertAt(cur, pos, t); ref.insert(pos, t); }
        else if (op == 2) { size_t pos = rng() % ref.size(), cnt = rng() % (ref.size() - pos + 1); cur = eraseRange(cur, pos, cnt); ref.erase(pos, cnt); }
        else { std::string t = "[" + std::to_string(step) + "]"; cur = cat(cur, leaf(t)); ref += t; }
        assert(len(cur) == ref.size()); if (step % 7 == 0 && !ref.empty()) { size_t i = rng() % ref.size(); assert(at(cur, i) == ref[i]); } if (step % 50 == 0) assert(str(cur) == ref); }
    assert(str(cur) == ref); for (auto& s : snaps) assert(str(s.first) == s.second);                                  // 영속성: 이전 버전은 그대로
    std::cout << "Rope: " << str(edited) << " (600 random edits matched std::string and " << snaps.size() << " earlier versions stayed intact)" << std::endl; return 0;
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
template <int B> std::string shape(const Unrolled<B>& u) {            // 그림: 노드 하나 = [배열], 노드 안은 연속 메모리라 캐시에 유리하고 노드 수는 n/B 쯤
    std::string s; for (const typename Unrolled<B>::Node* x = u.head; x; x = x->next) { s += "["; for (int i = 0; i < x->n; ++i) s += (i ? " " : "") + std::to_string(x->a[i]); s += "]"; }
    return s;
}
int main() {
    {   Unrolled<4> u; for (int v = 1; v <= 4; ++v) u.insert(u.total, v); assert(shape(u) == "[1 2 3 4]");              // 노드가 가득 찰 때까지는 한 노드
        u.insert(u.total, 5); assert(shape(u) == "[1 2][3 4 5]");                                                  // 5 번째: 꽉 찬 노드를 반으로 쪼갠다
        u.insert(u.total, 6); u.insert(u.total, 7); assert(shape(u) == "[1 2][3 4][5 6 7]");
        u.erase(3); assert(shape(u) == "[1 2][3 5 6 7]");                                                          // 4 를 지우니 노드가 B/2 미만 -> 이웃과 합쳐진다
        std::cout << shape(u) << "\n"; }
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
#include <cassert>
#include <iostream>
#include <random>
#include <string>

// 갭 버퍼(리스트 관점의 요약, 정본은 String.md Part 4): 글자 배열 가운데에 "빈 틈(gap)"을 두고 커서가 있는 곳에 틈을 놓는다. 커서 위치에서의 삽입·삭제는 O(1),
// 커서를 옮기면 틈을 따라 옮기는 데 이동 거리만큼의 복사가 든다. 편집은 지역적이라는 관찰에 기대는 Emacs 의 버퍼 구조
// 검증: 무작위 커서 이동·삽입·뒤로 지우기를 std::string 모델과 비교하고(내용·커서 위치·길이), 커서 이동의 복사 비용이 정확히 이동 거리와 같음을 센다. 같은 자리에서 연속 입력하면 이동이 한 번도 없다(지역성).
struct GapBuffer {
    std::string b; size_t gs, ge; long copies = 0;                         // 틈 [gs, ge)
    GapBuffer() : b(8, '_'), gs(0), ge(8) {}
    void moveTo(size_t pos) { while (gs > pos) { b[--ge] = b[--gs]; copies++; } while (gs < pos) { b[gs++] = b[ge++]; copies++; } }
    void insert(char c) { if (gs == ge) { size_t add = b.size(); b.insert(ge, add, '_'); ge += add; } b[gs++] = c; }
    void erase() { if (gs) gs--; }                                         // 커서 앞 글자 삭제
    std::string text() const { return b.substr(0, gs) + b.substr(ge); }
    size_t cursor() const { return gs; } size_t length() const { return b.size() - (ge - gs); }
};
std::string gapPicture(const GapBuffer& g) { return g.b.substr(0, g.gs) + "[" + std::string(g.ge - g.gs, '.') + "]" + g.b.substr(g.ge); }       // 그림: 대괄호 안이 틈(커서 위치), 점 하나가 빈 칸 하나
int main() {
    {   GapBuffer d; for (char c : std::string("Hello world")) d.insert(c);                           // 처음 8 칸이 차면 두 배로 늘어난다
        assert(gapPicture(d) == "Hello world[.....]" && d.b.size() == 16 && d.copies == 0);
        d.moveTo(5); assert(gapPicture(d) == "Hello[.....] world" && d.copies == 6);                  // 커서 이동 = 틈 반대편으로 글자를 옮기는 것 (옮긴 거리만큼만 복사)
        d.insert(','); assert(gapPicture(d) == "Hello,[....] world");                                   // 커서 자리 입력은 틈 한 칸을 쓰는 것뿐 (이동 없음)
        d.moveTo(12); d.insert('!'); assert(gapPicture(d) == "Hello, world![...]" && d.copies == 12);
        GapBuffer e; for (char c : std::string("Hello wo")) e.insert(c); assert(gapPicture(e) == "Hello wo[]");                 // 틈이 0 칸: 다음 입력에서 틈을 새로 연다
        e.insert('r'); assert(gapPicture(e) == "Hello wor[.......]" && e.b.size() == 16);
        std::cout << gapPicture(d) << "\n" << gapPicture(e) << "\n"; }
    GapBuffer g; for (char c : std::string("Hello world")) g.insert(c);
    g.moveTo(5); g.insert(','); g.moveTo(g.text().size()); g.insert('!');
    assert(g.text() == "Hello, world!"); g.moveTo(5); g.erase(); assert(g.text() == "Hell, world!");
    std::mt19937 rng(55); GapBuffer h; std::string ref; size_t cur = 0;
    for (int step = 0; step < 20000; step++) { int op = (int)(rng() % 6);
        if (op <= 2) { char c = (char)('a' + rng() % 26); h.insert(c); ref.insert(cur, 1, c); cur++; }
        else if (op == 3) { h.erase(); if (cur) { ref.erase(cur - 1, 1); cur--; } }
        else { size_t pos = rng() % (ref.size() + 1); long before = h.copies; size_t dist = pos > cur ? pos - cur : cur - pos; h.moveTo(pos); cur = pos; assert(h.copies - before == (long)dist); }   // 이동 비용 = 거리
        assert(h.cursor() == cur && h.length() == ref.size()); if (step % 97 == 0) assert(h.text() == ref); }
    assert(h.text() == ref);
    { GapBuffer t; long moved = t.copies; for (int i = 0; i < 5000; i++) t.insert('x'); assert(t.copies == moved && t.length() == 5000); }       // 같은 자리 연속 입력: 이동 0
    std::cout << "GapBuffer: " << g.text() << " (20000 random edits matched std::string; a cursor move copied exactly its distance, typing in place copied nothing)" << std::endl; return 0;
}
// Time Complexity: 커서 위치 삽입·삭제 O(1), 이동 O(거리)
// Space Complexity: O(N + 틈)
```
## PieceTable()
### 대표코드
```cpp
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 피스 테이블(리스트 관점의 요약, 정본은 String.md Part 4): 원본 파일은 수정하지 않고 "추가 전용" 버퍼에 새 글자를 덧붙이며, 문서 = (버퍼, 시작, 길이) 조각들의 목록.
// 삽입은 조각을 둘로 쪼개고 새 조각 하나를 끼우는 일이고, 삭제는 두 지점에서 조각을 쪼갠 뒤 사이의 조각을 목록에서 빼는 일이다. 글자는 한 번도 옮기거나 지우지 않으므로 조각 목록의 복사본이 곧 실행 취소(undo) 기록이다 (VS Code 의 텍스트 버퍼가 이 계열)
// 검증: 무작위 삽입·삭제를 std::string 모델과 비교하고, 도중에 찍은 조각 목록 스냅샷으로 복원하면 정확히 그 시점의 문서가 되며(원본·추가 버퍼는 그대로), 추가 버퍼는 줄지 않고 삽입한 글자 수만큼만 늘어난다.
struct Piece { bool add; size_t start, len; };
struct PT {
    std::string orig, added; std::vector<Piece> pieces;
    explicit PT(const std::string& s) : orig(s), pieces{{false, 0, s.size()}} {}
    size_t splitAt(size_t pos) {                                           // pos 에서 조각을 쪼개고 pos 직전까지의 조각 수를 돌려줌
        size_t off = 0, i = 0; while (i < pieces.size() && off + pieces[i].len <= pos) off += pieces[i++].len;
        if (i < pieces.size() && pos > off) { Piece p = pieces[i]; size_t k = pos - off; pieces[i] = {p.add, p.start, k}; pieces.insert(pieces.begin() + i + 1, Piece{p.add, p.start + k, p.len - k}); return i + 1; }
        return i; }
    void insert(size_t pos, const std::string& t) { if (t.empty()) return; size_t i = splitAt(pos); Piece n{true, added.size(), t.size()}; added += t; pieces.insert(pieces.begin() + i, n); }
    void erase(size_t pos, size_t count) { if (!count) return; size_t a = splitAt(pos); size_t b = splitAt(pos + count); pieces.erase(pieces.begin() + a, pieces.begin() + b); }
    std::string text() const { std::string r; for (auto& p : pieces) r += (p.add ? added : orig).substr(p.start, p.len); return r; }
    size_t length() const { size_t n = 0; for (auto& p : pieces) n += p.len; return n; }
};
std::string piecePicture(const PT& d) {                                // 그림: 조각 목록 — 문서는 조각을 이어 붙인 것이고, orig 과 added 두 버퍼는 한 번 쓰면 바뀌지 않는다
    std::string s;
    for (std::size_t i = 0; i < d.pieces.size(); ++i) { const Piece& p = d.pieces[i]; s += (i ? " | " : "") + std::string(p.add ? "add" : "orig") + "[" + std::to_string(p.start) + "," + std::to_string(p.start + p.len) + ")=\"" + (p.add ? d.added : d.orig).substr(p.start, p.len) + "\""; }
    return s;
}
int main() {
    {   PT v("Hello world"); assert(piecePicture(v) == "orig[0,11)=\"Hello world\"");
        v.insert(5, ","); assert(piecePicture(v) == "orig[0,5)=\"Hello\" | add[0,1)=\",\" | orig[5,11)=\" world\"");             // 가운데 삽입 = 조각을 둘로 쪼개고 사이에 새 조각
        v.insert(0, ">> "); assert(piecePicture(v) == "add[1,4)=\">> \" | orig[0,5)=\"Hello\" | add[0,1)=\",\" | orig[5,11)=\" world\"");
        v.erase(10, 3); assert(piecePicture(v) == "add[1,4)=\">> \" | orig[0,5)=\"Hello\" | add[0,1)=\",\" | orig[5,6)=\" \" | orig[9,11)=\"ld\"" && v.text() == ">> Hello, ld");   // 삭제 = 조각에서 범위만 빼기: 글자는 지워지지 않는다
        assert(v.orig == "Hello world" && v.added == ",>> ");
        std::cout << piecePicture(v) << "\n"; }
    PT d("Hello world"); auto undo = d.pieces;                             // 조각 목록의 복사본 = 문서의 한 시점
    d.insert(5, ","); d.insert(0, ">> ");
    assert(d.text() == ">> Hello, world" && d.orig == "Hello world");        // 원본은 그대로
    d.pieces = undo; assert(d.text() == "Hello world");                    // 실행 취소 = 조각 목록 복원
    std::mt19937 rng(56); PT p("The quick brown fox jumps over the lazy dog"); std::string ref = p.orig; std::vector<std::pair<std::vector<Piece>, std::string>> snaps; size_t inserted = 0;
    for (int step = 0; step < 2000; step++) { if (step % 100 == 0) snaps.push_back({p.pieces, ref});
        if (ref.empty() || rng() % 3 == 0) { size_t pos = rng() % (ref.size() + 1); std::string t; for (int i = 0, k = 1 + (int)(rng() % 5); i < k; i++) t += (char)('A' + rng() % 26); p.insert(pos, t); ref.insert(pos, t); inserted += t.size(); }
        else { size_t pos = rng() % ref.size(), cnt = rng() % std::min<size_t>(6, ref.size() - pos + 1); p.erase(pos, cnt); ref.erase(pos, cnt); }
        assert(p.length() == ref.size() && p.added.size() == inserted); if (step % 41 == 0) assert(p.text() == ref); }
    assert(p.text() == ref && p.orig == "The quick brown fox jumps over the lazy dog");
    for (auto& s : snaps) { std::vector<Piece> keep = p.pieces; p.pieces = s.first; assert(p.text() == s.second); p.pieces = keep; }       // 모든 시점으로 되돌릴 수 있다(버퍼는 추가 전용)
    assert(p.text() == ref);
    std::cout << "PieceTable: undo restores \"" << d.text() << "\" (2000 random edits matched std::string and all " << snaps.size() << " saved piece lists restored their exact documents)" << std::endl; return 0;
}
// Time Complexity: 삽입·삭제 O(조각 수), 텍스트 조립 O(길이)
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
#include <cmath>
#include <iostream>
#include <iterator>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 메모리 단편화(Fragmentation): 전체 빈 메모리는 충분한데도 큰 요청이 실패하는 현상. 두 종류가 있다. 외부 단편화 — 빈 공간이 여러 조각으로 쪼개져 가장 큰 조각이 요청보다 작다. 내부 단편화 — 할당 단위(크기 등급)로 올림해서 블록 안쪽이 낭비된다.
// 크기가 제각각인 블록을 섞어 할당·해제하면 외부 단편화가 쌓인다. 대책: ① 같은 크기끼리 모으는 풀/슬랩 할당자는 어떤 빈 칸이든 어떤 요청이든 맞아 외부 단편화가 없다(내부는 크기 등급 선택에 달림) ② 인접한 빈 조각을 합치는 병합(coalescing) ③ 살아 있는 블록을 한쪽으로 몰아 큰 빈 조각을 만드는 압축(compaction, 이동 가능한 핸들이 있을 때) ④ 크기 등급을 촘촘히(1.25 배) 두면 2 의 거듭제곱 등급보다 내부 낭비가 줄지만 등급 수가 늘어난다.
// 이 항목은 아레나(1 MB) 위의 첫 적합(first-fit) 할당자를 직접 만들어 실험한다: 외부 단편화 지표 = 1 − (가장 큰 빈 조각 / 전체 빈 공간). ① 할당자 불변식(블록이 겹치지 않음, 빈 조각은 인접하면 합쳐져 있음, 총합 일치) ② 1 KB 블록을 꽉 채우고 하나 걸러 해제하면 단편화 지표가 0.99 를 넘고 큰 요청(64 KB)이 전체 빈 공간(512 KB)이 충분한데도 실패 ③ 압축 뒤에는 같은 요청 성공 ④ 같은 크기 부하(풀): 64 B 블록을 꽉 채우고 한 칸 걸러 비워 빈 조각이 모두 64 B 인 상태(단편화 지표 0.9 초과, 64 KB 요청은 실패)에서 무작위 할당·해제를 점유율 40~60% 로 2 만 번 해도 64 B 요청은 한 번도 실패하지 않음 ⑤ 내부 단편화: 2 의 거듭제곱 등급의 평균 낭비가 1.25 배 등급보다 크다 ⑥ 첫 적합: 구멍 4 개(100·500·200·900 B)를 만들어 놓고 150 B 를 요청하면 주소가 가장 낮은 맞는 구멍(132)을 돌려주고(최적 적합은 664, 최악·마지막 적합은 896) 딱 맞는 구멍은 통째로 쓰이며, 단편화 지표가 빈 조각 목록과 독립적으로(살아 있는 블록 사이의 틈에서) 계산한 값과 같다
struct Heap {
    size_t cap; std::map<size_t, size_t> freeList, live;                         // 오프셋 -> 크기
    explicit Heap(size_t c) : cap(c) { freeList[0] = c; }
    long alloc(size_t n) { for (auto it = freeList.begin(); it != freeList.end(); ++it) if (it->second >= n) { size_t off = it->first, sz = it->second; freeList.erase(it); if (sz > n) freeList[off + n] = sz - n; live[off] = n; return (long)off; } return -1; }
    void release(size_t off) { size_t n = live[off]; live.erase(off); auto it = freeList.emplace(off, n).first; auto nx = std::next(it); if (nx != freeList.end() && it->first + it->second == nx->first) { it->second += nx->second; freeList.erase(nx); } if (it != freeList.begin()) { auto pv = std::prev(it); if (pv->first + pv->second == it->first) { pv->second += it->second; freeList.erase(it); } } }
    size_t totalFree() const { size_t s = 0; for (auto& f : freeList) s += f.second; return s; }
    size_t largestFree() const { size_t m = 0; for (auto& f : freeList) m = std::max(m, f.second); return m; }
    double fragmentation() const { size_t t = totalFree(); return t ? 1.0 - (double)largestFree() / t : 0.0; }
    bool check() const { std::map<size_t, size_t> all; for (auto& f : freeList) all[f.first] = f.second; for (auto& l : live) all[l.first] = l.second; size_t pos = 0, sum = 0; for (auto& b : all) { if (b.first != pos) return false; pos += b.second; } for (auto it = freeList.begin(); it != freeList.end(); ++it) { sum += it->second; auto nx = std::next(it); if (nx != freeList.end() && it->first + it->second == nx->first) return false; } size_t liveSum = 0; for (auto& l : live) liveSum += l.second; return pos == cap && sum + liveSum == cap; }
    size_t compact() { size_t pos = 0; std::map<size_t, size_t> moved; for (auto& l : live) { moved.emplace_hint(moved.end(), pos, l.second); pos += l.second; } live = moved; freeList.clear(); if (pos < cap) freeList[pos] = cap - pos; return pos; }          // 살아 있는 블록을 앞으로 몰기
};
int main() {
    std::mt19937 rng(8); const size_t CAP = 1 << 20; Heap h(CAP); std::vector<size_t> offs;
    for (;;) { size_t n = 16 + rng() % 1009; if (h.cap - h.totalFree() + n > CAP * 85 / 100) break; long o = h.alloc(n); if (o < 0) break; offs.push_back((size_t)o); }
    for (int round = 0; round < 40; round++) { for (size_t k = 0; k < offs.size() / 2; k++) { size_t i = rng() % offs.size(); h.release(offs[i]); offs[i] = offs.back(); offs.pop_back(); } for (;;) { size_t n = 16 + rng() % 1009; if (h.cap - h.totalFree() + n > CAP * 85 / 100) break; long o = h.alloc(n); if (o < 0) break; offs.push_back((size_t)o); } assert(h.check()); }          // ① 불변식 유지
    double churnFrag = h.fragmentation(); assert(h.check()); { size_t pos = 0, total = 0, largest = 0; for (auto& l : h.live) { size_t gap = l.first - pos; total += gap; largest = std::max(largest, gap); pos = l.first + l.second; } total += CAP - pos; largest = std::max(largest, CAP - pos); assert(std::abs(churnFrag - (1.0 - (double)largest / total)) < 1e-12); }   // 지표를 살아 있는 블록 사이의 틈에서 독립적으로 다시 계산
                                                                                                                         // ① 무작위 교체 뒤에도 불변식 유지
    Heap cb(CAP); std::vector<size_t> blocks; for (int i = 0; i < 1024; i++) blocks.push_back((size_t)cb.alloc(1024)); for (size_t i = 1; i < blocks.size(); i += 2) cb.release(blocks[i]);        // 1 KB 블록을 꽉 채우고 하나 걸러 해제
    size_t big = 64 * 1024, freeBefore = cb.totalFree(), largestBefore = cb.largestFree(); double frag = cb.fragmentation(); assert(cb.check() && freeBefore == CAP / 2 && largestBefore == 1024 && frag > 0.99 && churnFrag > 0.1 && churnFrag < frag);                         // ② 절반이 비었는데 가장 큰 조각은 1 KB
    assert(cb.alloc(big) < 0); cb.compact(); assert(cb.check() && cb.largestFree() == freeBefore && cb.alloc(big) >= 0);                                                                                    // ③ 압축 후 같은 요청 성공
    { Heap pool(CAP); std::vector<size_t> pv; const size_t B = 64, MAXB = CAP / B; long failures = 0, requests = 0; for (size_t i = 0; i < MAXB; i++) pv.push_back((size_t)pool.alloc(B));   // 꽉 채운 뒤
      std::vector<size_t> kept; for (size_t i = 0; i < pv.size(); i++) { if (i % 2) pool.release(pv[i]); else kept.push_back(pv[i]); } pv = kept;                                  // 한 칸 걸러 비운다: 빈 조각이 모두 정확히 64 B (최대한 흩어진 상태)
      assert(pool.check() && pool.fragmentation() > 0.9 && pool.alloc(CAP / 16) < 0 && pv.size() > MAXB * 4 / 10 && pv.size() < MAXB * 6 / 10);
      for (int round = 0; round < 20000; round++) { if (rng() % 2 == 0) { if (pv.size() <= MAXB * 4 / 10) continue; size_t i = rng() % pv.size(); pool.release(pv[i]); pv[i] = pv.back(); pv.pop_back(); } else { if (pv.size() >= MAXB * 6 / 10) continue; long o = pool.alloc(B); requests++; if (o < 0) failures++; else pv.push_back((size_t)o); } }
      assert(failures == 0 && requests > 5000 && pool.check() && pool.fragmentation() > 0.9 && pool.alloc(CAP / 16) < 0); }                                       // ④ 같은 크기 부하는 실패하지 않는다
    { Heap t(1828); long a1 = t.alloc(100); t.alloc(32); long a2 = t.alloc(500); t.alloc(32); long a3 = t.alloc(200); t.alloc(32); long a4 = t.alloc(900); t.alloc(32); assert(a1 == 0 && a2 == 132 && a3 == 664 && a4 == 896 && t.freeList.empty());   // ⑥ 첫 적합
      for (long a : {a1, a2, a3, a4}) t.release((size_t)a); assert(t.check() && t.freeList.size() == 4);                                              // 구멍 4 개: 100@0, 500@132, 200@664, 900@896 (사이는 살아 있는 32 B 블록)
      assert(t.alloc(150) == 132 && t.freeList.at(282) == 350 && t.check());                                                                     // 주소가 가장 낮은 맞는 구멍(최적 적합은 664, 최악·마지막 적합은 896)
      assert(t.alloc(100) == 0 && t.freeList.count(0) == 0 && t.check()); }                                                                        // 딱 맞는 구멍은 통째로 쓰고 목록에서 사라진다
    double wastePow2 = 0, wasteGeo = 0; const int T = 100000; for (int t = 0; t < T; t++) { size_t n = 17 + rng() % 4000; size_t p2 = 1; while (p2 < n) p2 <<= 1; double c = 16; while (c < n) c = std::ceil(c * 1.25); wastePow2 += (double)(p2 - n) / p2; wasteGeo += (c - n) / c; }
    wastePow2 /= T; wasteGeo /= T; assert(wastePow2 > wasteGeo * 1.4 && wastePow2 > 0.2 && wasteGeo < 0.15);                                                                                                                                                                                      // ⑤ 내부 단편화
    std::cout << "Memory Fragmentation: random churn left fragmentation index " << churnFrag << "; a checkerboard of 1 KB blocks had " << freeBefore << " bytes free but the largest hole was only " << largestBefore << " (index " << frag << "), so a " << big << "-byte request failed until compaction; an arena whose free space was a checkerboard of single 64-byte slots never failed a 64-byte request across 20000 random allocations and frees even though a 64 KB request could not be served; first-fit returned the lowest-addressed hole that fits; internal waste: power-of-two classes " << wastePow2 << " vs 1.25x classes " << wasteGeo << std::endl; return 0;
}
// Time Complexity: 첫 적합 할당 O(빈 조각 수), 해제 O(log N), 압축 O(살아 있는 블록 수) (빈 조각은 살아 있는 블록 사이에만 있어 L+1 개 이하)
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
// 실제 시간은 기계마다 달라 단언에 쓸 수 없으므로 두 가지로 확인한다. ① 결정적 시뮬레이터: 코어별 라인 소유 상태(M)를 추적하는 일관성 모델에 쓰기 열을 흘려 "무효화 횟수" 를 센다 — 두 코어가 같은 라인의 다른 주소를 번갈아 쓰면 첫 쓰기를 뺀 모든 쓰기에서 무효화가 일어나고(2 코어 2N−1 회, 4 코어 4N−1 회), 주소가 64 B 떨어져 있으면 최초 소유 이후 0 회다. 코어마다 지역 변수에 누적하다가 같은 라인에 한 번씩만 쓰면 (코어 수 − 1) = 3 회뿐이다 ② 실제 스레드: 패딩한 카운터와 붙은 카운터를 모두 정확히 증가시켜 결과가 같음을 검증하고(원자 연산이라 정확성은 같다) 걸린 시간은 참고용으로만 출력한다(코어가 하나뿐인 기계에서는 거짓 공유가 생기지 않아 두 시간이 비슷하며, 속도 향상은 단언도 주장도 하지 않는다) — 주소가 같은 라인에 있는지는 결정적으로 단언한다
// audit: closed-form (무효화 횟수 2N−1, 4N−1, 3, 0 은 쓰기 순서에서 유도한 닫힌 식)
struct Coherence {                                                              // 단순화한 쓰기 무효화 모델: 라인당 현재 소유 코어 하나
    std::map<uint64_t, int> owner; long invalidations = 0, coldMisses = 0;
    void write(int core, uint64_t addr) { uint64_t line = addr >> 6; auto it = owner.find(line); if (it == owner.end()) { coldMisses++; owner[line] = core; } else if (it->second != core) { invalidations++; it->second = core; } }
};
struct Packed { std::atomic<long> v; };                                         // 8 바이트 -> 한 라인에 8 개
struct alignas(64) Padded { std::atomic<long> v; };                              // 라인 하나를 독점
int main() {
    static_assert(sizeof(Padded) == 64 && alignof(Padded) == 64, "one counter per cache line");
    const int N = 100000; long localInv = 0;
    { Coherence same, apart; for (int i = 0; i < N; i++) for (int core = 0; core < 2; core++) { same.write(core, 0x1000 + core * 8); apart.write(core, 0x1000 + core * 64); } assert(same.invalidations == 2 * N - 1 && same.coldMisses == 1 && apart.invalidations == 0 && apart.coldMisses == 2); }          // ① 같은 라인: 쓰기마다 무효화
    { Coherence four; for (int i = 0; i < N; i++) for (int core = 0; core < 4; core++) four.write(core, 0x2000 + core * 8); assert(four.invalidations == 4 * N - 1);                       // 4 코어: 쓰기마다 무효화
      Coherence local; long sums[4] = {0, 0, 0, 0}; for (int i = 0; i < N; i++) for (int core = 0; core < 4; core++) sums[core]++;   // 같은 교대 순서로 증가하지만 지역 변수에만 누적한다(일관성 모델에 쓰기 없음)
      for (int core = 0; core < 4; core++) { assert(sums[core] == N); local.write(core, 0x3000 + core * 8); }                     // 마지막에 코어당 한 번만, 같은 라인에 쓴다
      assert(local.coldMisses == 1 && local.invalidations == 4 - 1 && four.invalidations == 4 * N - 1); localInv = local.invalidations; }   // 증가마다 쓰면 4N−1 회, 누적 후 한 번이면 정확히 코어 수 − 1 회
    alignas(64) static Packed packed[8]; alignas(64) static Padded padded[8];
    assert(((uintptr_t)&packed[0] >> 6) == ((uintptr_t)&packed[7] >> 6) && ((uintptr_t)&padded[0] >> 6) != ((uintptr_t)&padded[1] >> 6));                                                                 // 붙은 카운터는 같은 라인, 패딩한 것은 서로 다른 라인
    long packedMs = 0, paddedMs = 0; const long ITER = 2000000;
    for (int variant = 0; variant < 2; variant++) { auto t0 = std::chrono::steady_clock::now(); std::vector<std::thread> ts; for (int t = 0; t < 4; t++) ts.emplace_back([&, t, variant] { std::atomic<long>& c = variant ? padded[t].v : packed[t].v; for (long i = 0; i < ITER; i++) c.fetch_add(1, std::memory_order_relaxed); }); for (auto& t : ts) t.join(); auto t1 = std::chrono::steady_clock::now(); (variant ? paddedMs : packedMs) = std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count(); }
    for (int t = 0; t < 4; t++) assert(packed[t].v.load() == ITER && padded[t].v.load() == ITER);                                                                                                           // ② 정확성은 같다
    std::cout << "False Sharing: simulated coherence invalidations " << 2 * N - 1 << " for two writers in one cache line vs 0 when 64 bytes apart, and four cores that accumulate locally and write the shared line once each caused only " << localInv << " (vs " << 4 * N - 1 << " writing every increment); real threads counted exactly in both layouts (packed " << packedMs << " ms, padded " << paddedMs << " ms - timing is informational only, depends on the core count, and no speedup is claimed)" << std::endl; return 0;
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
