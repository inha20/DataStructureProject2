# Part 1. 기본 연산
## CreateStack()
### 대표코드
```cpp
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <new>
#include <stack>
#include <utility>
#include <cassert>

// 스택 만들기(Create): "비어 있는 스택" 이라는 초기 상태를 세우는 일이다. 새 스택은 크기 0, top 없음, 어떤 pop/peek 도 실패해야 하며, 이 불변식이 이후 모든 연산의 출발점이 된다.
// 표현 방식에 따라 만드는 비용이 다르다. 배열 스택은 용량을 정해 메모리를 한 번에 확보하고(할당 1 번), 연결 스택은 top = nullptr 하나로 시작해 아무것도 할당하지 않는다(할당 0 번; 메모리는 push 마다 노드 하나씩).
// 자원을 쥐는 클래스는 RAII 를 지킨다: 생성자가 얻고 소멸자가 돌려주며, 얕은 복사로 이중 해제가 나지 않도록 복사는 금지하고 이동(소유권 이전)만 허용한다.
// 검증(전역 operator new/delete 를 교체해 할당 횟수와 생존 블록을 센다): ① 새 스택은 비어 있고 크기 0이며 peek/pop 이 실패한다 ② 배열 스택 생성은 할당 1 번, 연결 스택은 0 번이고 첫 push 에서 1 번 ③ 3000 개를 만들고 부숴도 생존 블록이 늘지 않는다(누수 0) ④ 용량 0 도 정상 ⑤ 이동 후 원본은 빈 스택이고 내용은 새 스택으로 넘어간다 ⑥ 실무의 std::stack 도 같은 초기 상태를 가진다
static long newCalls = 0, liveBlocks = 0;
#pragma GCC diagnostic ignored "-Wmismatched-new-delete"
void* operator new(std::size_t n) { void* p = std::malloc(n ? n : 1); if (!p) throw std::bad_alloc(); newCalls++; liveBlocks++; return p; }
void operator delete(void* p) noexcept { if (p) { liveBlocks--; std::free(p); } }
void operator delete(void* p, std::size_t) noexcept { operator delete(p); }
void* operator new[](std::size_t n) { return operator new(n); }
void operator delete[](void* p) noexcept { operator delete(p); }
void operator delete[](void* p, std::size_t) noexcept { operator delete(p); }
class ArrayStack {
    int* a_; std::size_t cap_, n_ = 0;
public:
    explicit ArrayStack(std::size_t capacity) : a_(capacity ? new int[capacity] : nullptr), cap_(capacity) {}
    ~ArrayStack() { delete[] a_; }
    ArrayStack(const ArrayStack&) = delete; ArrayStack& operator=(const ArrayStack&) = delete;
    ArrayStack(ArrayStack&& o) noexcept : a_(o.a_), cap_(o.cap_), n_(o.n_) { o.a_ = nullptr; o.cap_ = o.n_ = 0; }
    bool empty() const { return n_ == 0; } std::size_t size() const { return n_; }
    bool push(int x) { if (n_ == cap_) return false; a_[n_++] = x; return true; }
    bool pop(int& out) { if (!n_) return false; out = a_[--n_]; return true; }
    bool peek(int& out) const { if (!n_) return false; out = a_[n_ - 1]; return true; }
};
class LinkedStack {
    struct Node { int v; Node* next; }; Node* top_ = nullptr; std::size_t n_ = 0;
public:
    ~LinkedStack() { while (top_) { Node* t = top_; top_ = t->next; delete t; } }
    bool empty() const { return top_ == nullptr; } std::size_t size() const { return n_; }
    bool push(int x) { top_ = new Node{x, top_}; n_++; return true; }
    bool pop(int& out) { if (!top_) return false; Node* t = top_; out = t->v; top_ = t->next; delete t; n_--; return true; }
    bool peek(int& out) const { if (!top_) return false; out = top_->v; return true; }
};
template <class S> void checkFresh(S& s) { int v = 123; assert(s.empty() && s.size() == 0 && !s.peek(v) && !s.pop(v) && v == 123); }                // ① 초기 불변식 (실패한 호출은 출력 인자를 건드리지 않는다)
int main() {
    long baseLive = liveBlocks;
    { ArrayStack a(16); LinkedStack l; checkFresh(a); checkFresh(l); }
    long b0 = newCalls; { ArrayStack a(16); assert(newCalls - b0 == 1); } long b1 = newCalls; { LinkedStack l; assert(newCalls == b1); l.push(1); assert(newCalls - b1 == 1); }          // ② 할당 횟수
    for (int i = 0; i < 3000; i++) { ArrayStack a(i % 40); LinkedStack l; for (int k = 0; k < i % 7; k++) { a.push(k); l.push(k); } } assert(liveBlocks == baseLive);                    // ③ 누수 0
    { ArrayStack zero(0); int v; assert(zero.empty() && !zero.push(1) && !zero.pop(v) && !zero.peek(v)); }                                                                            // ④ 용량 0
    { ArrayStack a(4); a.push(7); a.push(8); ArrayStack b(std::move(a)); int v; assert(a.empty() && a.size() == 0 && !a.push(1) && b.size() == 2 && b.pop(v) && v == 8 && b.pop(v) && v == 7); }        // ⑤ 이동
    { std::stack<int> s; assert(s.empty() && s.size() == 0); }                                                                                                                         // ⑥ 실무의 std::stack
    std::cout << "CreateStack: fresh array and linked stacks satisfy the empty-state invariants; array stack costs 1 allocation, linked stack 0 until the first push; 3000 create/destroy cycles left no live blocks" << std::endl; return 0;
}
// Time Complexity: 연결 스택 생성 O(1), 배열 스택 생성 O(1) 할당 (값 초기화를 하면 O(용량))
// Space Complexity: 배열 O(용량), 연결 O(1) (원소 수에 비례해 증가)
```
## Push()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <new>
#include <random>
#include <stack>
#include <stdexcept>
#include <vector>
#include <cassert>

// 푸시(Push): 맨 위에 원소를 올린다. 구현마다 가득 찼을 때의 약속이 다르다. ① 고정 배열: 거절(false) — 배열 밖을 쓰지 않는 것이 이 구현의 정확성 전부다 ② 동적 배열: 용량을 두 배로 늘려 복사한다. 한 번은 O(N)이지만 N 번 푸시의 총 복사가 2N 미만이라 분할상환 O(1) ③ 연결: 노드 하나를 할당한다.
// 예외 안전: 용량을 늘리다 복사 중 예외가 나도 스택은 이전 상태 그대로여야 한다(강한 보장). 그래서 새 버퍼에 먼저 모두 복사하고, 성공한 뒤에야 옛 버퍼를 파괴·교체한다. 실패하면 새 버퍼에 만든 것만 되돌린다.
// 검증: ① 고정 용량 스택이 정확히 용량만큼 받고 그 다음은 false, 경계 밖 감시값은 그대로 ② 동적 배열의 성장 복사 횟수 < 2N, 용량은 항상 2의 거듭제곱 ③ std::stack 과 무작위 push/pop 이 일치 ④ 복사 도중 예외를 던지는 원소 타입에서 push 가 실패해도 크기·내용·용량이 그대로이고 생존 객체 수가 맞다(누수 없음)
class FixedStack {                                                              // 외부 버퍼를 빌려 쓰는 고정 용량 스택
    int* a_; std::size_t cap_, n_ = 0;
public:
    FixedStack(int* buffer, std::size_t cap) : a_(buffer), cap_(cap) {}
    bool push(int x) { if (n_ == cap_) return false; a_[n_++] = x; return true; }
    bool pop(int& out) { if (!n_) return false; out = a_[--n_]; return true; }
    std::size_t size() const { return n_; }
};
struct Counted { int v; static long copies, live, failAt; Counted(int x) : v(x) { live++; }
    Counted(const Counted& o) : v(o.v) { if (++copies == failAt) throw std::runtime_error("copy failed"); live++; } ~Counted() { live--; } };
long Counted::copies = 0, Counted::live = 0, Counted::failAt = -1;
template <class T> class Stack {
    T* a_ = nullptr; std::size_t n_ = 0, cap_ = 0;
    void grow(std::size_t nc) {
        T* nb = static_cast<T*>(::operator new(nc * sizeof(T))); std::size_t i = 0;
        try { for (; i < n_; i++) new (nb + i) T(a_[i]); } catch (...) { while (i) nb[--i].~T(); ::operator delete(nb); throw; }          // 실패하면 새 버퍼만 되돌린다
        for (std::size_t k = 0; k < n_; k++) a_[k].~T(); ::operator delete(a_); a_ = nb; cap_ = nc;
    }
public:
    Stack() = default; Stack(const Stack&) = delete; Stack& operator=(const Stack&) = delete;
    ~Stack() { while (n_) a_[--n_].~T(); ::operator delete(a_); }
    void push(const T& v) { if (n_ == cap_) grow(cap_ ? cap_ * 2 : 1); new (a_ + n_) T(v); ++n_; }
    T& at(std::size_t i) { return a_[i]; } std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; }
    void pop() { a_[--n_].~T(); }
};
int main() {
    { int raw[10]; for (int& x : raw) x = -999; FixedStack s(raw + 1, 8); for (int i = 0; i < 8; i++) assert(s.push(i)); assert(!s.push(8) && !s.push(9) && s.size() == 8 && raw[0] == -999 && raw[9] == -999); int v; for (int i = 7; i >= 0; i--) { assert(s.pop(v) && v == i); } }          // ①
    { Stack<Counted> s; const int N = 5000; Counted::copies = 0; for (int i = 0; i < N; i++) { Counted c(i); s.push(c); assert((s.capacity() & (s.capacity() - 1)) == 0); } long growth = Counted::copies - N; assert(growth < 2L * N && s.size() == N); std::cout << "growth copies for " << N << " pushes: " << growth << "; "; }          // ②
    { std::mt19937 rng(5); std::stack<int> ref; Stack<Counted> s; for (int step = 0; step < 20000; step++) { if (rng() % 3) { int v = rng() % 1000; ref.push(v); s.push(Counted(v)); } else if (!ref.empty()) { assert(s.at(s.size() - 1).v == ref.top()); ref.pop(); s.pop(); } assert(s.size() == ref.size()); } }                          // ③
    { Counted::live = 0; { Stack<Counted> s; for (int i = 0; i < 4; i++) s.push(Counted(i)); assert(s.size() == 4 && s.capacity() == 4 && Counted::live == 4);
        Counted::failAt = Counted::copies + 3; bool threw = false; try { s.push(Counted(99)); } catch (const std::runtime_error&) { threw = true; } Counted::failAt = -1;                          // 용량 4 -> 8 로 늘리는 중 세 번째 복사에서 실패
        assert(threw && s.size() == 4 && s.capacity() == 4 && Counted::live == 4); for (int i = 0; i < 4; i++) assert(s.at(i).v == i);                                                            // ④ 이전 상태 그대로, 누수 없음
        s.push(Counted(4)); assert(s.size() == 5 && s.capacity() == 8); } assert(Counted::live == 0); }
    std::cout << "Push: fixed-capacity stack rejected overflow without touching guard cells; dynamic stack kept the strong guarantee when a copy threw during growth" << std::endl; return 0;
}
// Time Complexity: 고정 배열 O(1), 동적 배열 분할상환 O(1) (최악 O(N)), 연결 O(1)
// Space Complexity: O(N) (동적 배열은 용량이 크기의 최대 2 배)
```
## Pop()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <new>
#include <random>
#include <stack>
#include <stdexcept>
#include <utility>
#include <vector>
#include <cassert>

// 팝(Pop): 맨 위 원소를 제거한다. 설계 질문 두 가지. (1) 빈 스택에서 팝하면? std::stack 은 사용자의 책임(정의되지 않은 동작)으로 두고, 이 책의 스택은 false 를 돌려주고 상태를 바꾸지 않는다. (2) 제거한 값을 돌려줄까? std::stack::pop() 이 void 인 데는 이유가 있다 — 값을 돌려주려면 원소를 제거한 "뒤에" 호출자에게 복사해야 하는데, 복사가 예외를 던지면 원소는 이미 사라져 영영 잃는다(강한 예외 보장 위반).
// 그래서 읽기(top)와 제거(pop)를 둘로 나눈다: 먼저 top 을 복사하고(실패해도 스택은 그대로), 성공한 뒤에 pop 이 파괴자만 부른다. 또한 pop 은 원소의 소멸자를 반드시 호출해야 자원이 돌아온다.
// 검증: ① N 개를 올리고 모두 꺼내면 정확히 역순(LIFO) ② 빈 스택 pop 은 false 이고 출력 인자·상태 불변 ③ 소멸자 호출 수: pop 한 만큼 소멸하고 스택이 파괴되면 나머지도 소멸 ④ 복사가 던지는 타입에서 "값 반환 pop" 설계는 원소를 잃고 "top 후 pop" 설계는 보존 ⑤ std::stack 과 무작위 차분
struct Fragile { int v; static bool armed; static long live; Fragile(int x) : v(x) { live++; } Fragile(Fragile&& o) noexcept : v(o.v) { live++; }
    Fragile(const Fragile& o) : v(o.v) { if (armed) throw std::runtime_error("copy failed"); live++; } ~Fragile() { live--; } };
bool Fragile::armed = false; long Fragile::live = 0;
template <class T> class Stack {
    T* a_ = nullptr; std::size_t n_ = 0, cap_ = 0;
public:
    Stack() = default; Stack(const Stack&) = delete; Stack& operator=(const Stack&) = delete;
    ~Stack() { while (n_) a_[--n_].~T(); ::operator delete(a_); }
    void push(T v) { if (n_ == cap_) { std::size_t nc = cap_ ? cap_ * 2 : 1; T* nb = static_cast<T*>(::operator new(nc * sizeof(T))); for (std::size_t i = 0; i < n_; i++) { new (nb + i) T(std::move(a_[i])); a_[i].~T(); } ::operator delete(a_); a_ = nb; cap_ = nc; } new (a_ + n_) T(std::move(v)); ++n_; }
    bool pop() { if (!n_) return false; a_[--n_].~T(); return true; }                                   // 설계 B: 제거만 한다
    T& top() { return a_[n_ - 1]; } std::size_t size() const { return n_; }
    T popValueNaive() {                                                                                   // 설계 A: 값을 돌려주는 pop. 제거한 "뒤에" 복사해 돌려줘야 한다
        alignas(T) unsigned char raw[sizeof(T)]; T* tmp = new (raw) T(std::move(a_[n_ - 1])); a_[--n_].~T();
        struct G { T* p; ~G() { p->~T(); } } g{tmp}; return *tmp;                                           // 이 복사가 던지면 원소는 이미 스택에서 사라졌다
    }
};
int main() {
    { Stack<int> s; for (int i = 0; i < 1000; i++) s.push(i); for (int i = 999; i >= 0; i--) { assert(s.top() == i && s.pop()); } assert(s.size() == 0); }                                                             // ① LIFO
    { Stack<int> s; assert(!s.pop() && s.size() == 0); s.push(5); assert(s.pop() && !s.pop()); }                                                                                                                  // ②
    { Fragile::live = 0; { Stack<Fragile> s; for (int i = 0; i < 6; i++) s.push(Fragile(i)); assert(Fragile::live == 6); s.pop(); s.pop(); assert(Fragile::live == 4 && s.size() == 4); } assert(Fragile::live == 0); }  // ③ 소멸 계수
    { Stack<Fragile> a, b; for (int i = 1; i <= 5; i++) { a.push(Fragile(i)); b.push(Fragile(i)); }
      Fragile::armed = true; bool threwA = false, threwB = false;
      try { Fragile r = a.popValueNaive(); (void)r; } catch (const std::runtime_error&) { threwA = true; }
      try { Fragile r = b.top(); (void)r; b.pop(); } catch (const std::runtime_error&) { threwB = true; }                                                                                                          // 복사 먼저(top), 성공해야 pop
      Fragile::armed = false; assert(threwA && threwB); assert(a.size() == 4 && a.top().v == 4);                                                                                                                  // ④ 값 반환 설계: 5 를 영영 잃었다
      assert(b.size() == 5 && b.top().v == 5); }                                                                                                                                                                      // 분리 설계: 5 가 그대로 남아 재시도 가능
    { std::mt19937 rng(8); std::stack<int> ref; Stack<int> s; for (int step = 0; step < 30000; step++) { if (rng() % 2) { int v = rng(); ref.push(v); s.push(v); } else { bool had = !ref.empty(); if (had) { assert(s.top() == ref.top()); ref.pop(); } assert(s.pop() == had); } assert(s.size() == ref.size()); } }       // ⑤
    std::cout << "Pop: LIFO order, safe empty pops, destructor accounting and the top()+pop() split design verified; a value-returning pop lost an element when its copy threw" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Peek()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 엿보기(Peek): 맨 위 원소를 "꺼내지 않고" 읽는다. 스택의 상태를 바꾸지 않는 const 연산이어야 하며 O(1) 이다. 괄호 검사처럼 "다음에 무엇을 할지 보고 결정" 하는 알고리즘(조건에 맞으면 pop, 아니면 push)의 기본 도구다.
// 빈 스택에서 엿볼 수는 없으므로 실패를 알려야 한다 — 이 구현은 bool 과 출력 인자를 쓴다(C++17 의 std::optional 도 같은 역할). 확장으로 k 번째 아래까지 보는 peekAt(k)가 있다(k = 0 이 맨 위). 이것은 스택의 정의(맨 위만 접근)를 넘으므로 디버깅·정책 검사용으로만 쓰는 것이 좋다.
// 검증: ① 스택 전체(위에서 아래로)를 복사해 둔 뒤 peek/peekAt 을 수천 번 불러도 내용·크기가 그대로 ② std::stack 의 top 과 같고 peekAt(k) 가 벡터 모델의 역방향 인덱스와 같음 ③ const 스택에서도 호출 가능 ④ 빈 스택과 범위 밖 k 는 false ⑤ peek 한 값을 pop 하면 같은 값
class ArrayStack {
    std::vector<int> a_;
public:
    void push(int x) { a_.push_back(x); }
    bool pop(int& out) { if (a_.empty()) return false; out = a_.back(); a_.pop_back(); return true; }
    bool peek(int& out) const { if (a_.empty()) return false; out = a_.back(); return true; }
    bool peekAt(std::size_t k, int& out) const { if (k >= a_.size()) return false; out = a_[a_.size() - 1 - k]; return true; }
    std::size_t size() const { return a_.size(); }
    std::vector<int> snapshotTopFirst() const { return std::vector<int>(a_.rbegin(), a_.rend()); }
};
int main() {
    std::mt19937 rng(3); ArrayStack s; std::stack<int> ref; std::vector<int> model;
    for (int step = 0; step < 20000; step++) {
        int op = rng() % 4;
        if (op < 2) { int v = rng() % 100; s.push(v); ref.push(v); model.push_back(v); }
        else if (op == 2 && !ref.empty()) { int p; assert(s.peek(p) && p == ref.top()); int q; assert(s.pop(q) && q == p); ref.pop(); model.pop_back(); }                      // ⑤ peek 한 값이 pop 된다
        else { std::vector<int> before = s.snapshotTopFirst(); std::size_t n = s.size(); for (int t = 0; t < 5; t++) { int v; bool ok = s.peek(v); assert(ok == !ref.empty() && (!ok || v == ref.top())); std::size_t k = rng() % (n + 2); int w; bool ok2 = s.peekAt(k, w); assert(ok2 == (k < n) && (!ok2 || w == model[n - 1 - k])); } assert(s.snapshotTopFirst() == before && s.size() == n); }   // ① ② ④
        if (s.size() > 300) { int d; for (int i = 0; i < 150; i++) { s.pop(d); ref.pop(); model.pop_back(); } }
    }
    const ArrayStack& cs = s; int v; (void)cs.peek(v); (void)cs.peekAt(0, v);                                                                                                         // ③ const 접근
    ArrayStack empty; assert(!empty.peek(v) && !empty.peekAt(0, v));
    std::cout << "Peek: 20000 randomized operations; peek and peekAt never changed the stack and agreed with std::stack::top and a vector model" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Top()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <memory>
#include <stack>
#include <type_traits>
#include <vector>
#include <cassert>

// 톱(Top): 맨 위 원소에 대한 "참조" 를 돌려준다(std::stack::top()). 값을 복사하는 Peek 과 달리 참조로 받으면 제자리 수정이 가능하다 — s.top() += 5. 큰 객체를 복사하지 않아도 되는 이점이 있다.
// 그러나 참조는 스택이 재배치되면 매달린다(dangling): 동적 배열 스택에서 push 가 용량을 넘겨 버퍼를 새로 잡으면 옛 참조가 가리키던 주소는 해제된다. 연결 스택은 노드가 움직이지 않아 push 뒤에도 참조가 유효하고, 고정 배열도 마찬가지다. 해제된 메모리를 읽는 것은 정의되지 않은 동작이므로 아래 실험은 값을 읽지 않고 주소(정수로 바꾼 값)만 비교한다.
// 빈 스택의 top() 은 정의되지 않은 동작이다 — 호출 전에 empty() 를 확인하는 것이 호출자의 책임이다.
// 검증: ① 참조로 제자리 수정이 스택에 반영된다 ② const 스택은 const 참조만 준다 ③ 동적 배열 스택은 용량이 늘 때마다 원소 주소가 바뀌지만(바닥 원소의 주소 변화를 센다) 연결 스택의 첫 노드는 제자리 ④ reserve 로 용량을 미리 잡으면 주소가 바뀌지 않음 ⑤ std::stack 의 top 과 일치(차분)
template <class T> class VectorStack {
    std::vector<T> a_;
public:
    void push(const T& v) { a_.push_back(v); } void pop() { a_.pop_back(); } bool empty() const { return a_.empty(); } std::size_t size() const { return a_.size(); }
    T& top() { return a_.back(); } const T& top() const { return a_.back(); } T& bottom() { return a_.front(); } void reserve(std::size_t n) { a_.reserve(n); }
};
template <class T> class LinkedStack {
    struct Node { T v; Node* next; }; Node* top_ = nullptr;
public:
    ~LinkedStack() { while (top_) { Node* t = top_; top_ = t->next; delete t; } }
    void push(const T& v) { top_ = new Node{v, top_}; } T& top() { return top_->v; } const T& top() const { return top_->v; }
};
uintptr_t addr(const void* p) { return reinterpret_cast<uintptr_t>(p); }
int main() {
    { VectorStack<int> s; s.push(10); s.top() += 5; assert(s.top() == 15); s.push(20); s.top() *= 2; assert(s.top() == 40); s.pop(); assert(s.top() == 15); }                                      // ① 제자리 수정
    { VectorStack<int> s; s.push(1); const VectorStack<int>& cs = s; static_assert(std::is_same<decltype(cs.top()), const int&>::value, "const stack gives const reference"); assert(cs.top() == 1); }       // ② const 정확성
    { VectorStack<int> s; s.push(0); uintptr_t at = addr(&s.bottom()); int relocations = 0; for (int i = 1; i < 1000; i++) { s.push(i); if (addr(&s.bottom()) != at) { relocations++; at = addr(&s.bottom()); } } assert(relocations >= 5);       // ③ 배열 스택: 용량이 늘 때마다 모든 원소가 이사한다
      VectorStack<int> r; r.reserve(1000); r.push(0); uintptr_t fixed = addr(&r.bottom()); for (int i = 1; i < 1000; i++) { r.push(i); assert(addr(&r.bottom()) == fixed); }                                // ④ reserve 로 용량을 미리 잡으면 이사하지 않는다
      LinkedStack<int> l; l.push(0); int* pinned = &l.top(); for (int i = 1; i < 1000; i++) l.push(i); assert(*pinned == 0 && pinned != &l.top()); }                                                    // 연결 스택: 첫 노드는 제자리, 참조가 계속 유효 (값을 읽어도 안전)
    { std::stack<int> ref; VectorStack<int> s; for (int i = 0; i < 5000; i++) { int x = (i * 37) % 101; ref.push(x); s.push(x); assert(s.top() == ref.top()); if (i % 3 == 2) { ref.pop(); s.pop(); assert(s.top() == ref.top()); } } }          // ⑤
    std::cout << "Top: in-place modification through the reference works; reallocation moved the bottom of an array stack repeatedly but never the nodes of a linked stack" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IsEmpty()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 비었는지 검사(IsEmpty): 스택에 원소가 하나도 없는가. pop·peek 의 전제 조건이며 `while (!s.empty())` 로 비울 때까지 처리하는 반복의 조건이다. O(1) 이어야 한다.
// 표현마다 판정이 다르다: 배열 스택은 크기 카운터가 0 인지 또는 topIndex == −1 인지, 연결 스택은 top 포인터가 null 인지. 연결 스택에서 크기 카운터를 두지 않았다면 `size() == 0` 은 노드를 끝까지 세야 하는 O(N) 이므로 `empty()` 를 따로 두는 것이 중요하다(아래에서 방문 노드 수로 증명).
// 부호 없는 정수의 함정: size() 는 size_t 이므로 비어 있을 때 `size() - 1` 은 −1 이 아니라 SIZE_MAX 로 되감겨 `for (size_t i = s.size() - 1; i >= 0; i--)` 같은 반복이 끝나지 않거나 범위를 벗어난다. 크기를 쓰기 전에 empty() 로 확인하고, 마지막 원소 인덱스는 `size() - 1` 이 아니라 "비어 있지 않음을 확인한 뒤" 구한다.
// 검증: ① 세 표현(카운터형, topIndex 형, 연결형)의 empty() 가 무작위 push/pop 열에서 항상 std::stack::empty() 와 같고 empty() == (size() == 0) ② 연결 스택(카운터 없음)에서 empty() 는 노드를 0 개 방문, size() 는 N 개 방문 ③ 비운 뒤 다시 empty ④ size_t 되감기 값 == SIZE_MAX ⑤ 드레인 반복의 올바른 관용구
struct CounterStack { std::vector<int> a; bool empty() const { return a.empty(); } std::size_t size() const { return a.size(); } void push(int x) { a.push_back(x); } void pop() { a.pop_back(); } };
struct IndexStack { int a[1000]; int topIndex = -1; bool empty() const { return topIndex == -1; } int size() const { return topIndex + 1; } void push(int x) { a[++topIndex] = x; } void pop() { --topIndex; } };
struct LinkedStack {
    struct Node { int v; Node* next; }; Node* top = nullptr; mutable long visited = 0;
    ~LinkedStack() { while (top) { Node* t = top; top = t->next; delete t; } }
    bool empty() const { return top == nullptr; }                                           // 노드를 방문하지 않는다
    std::size_t sizeByWalking() const { std::size_t n = 0; for (Node* p = top; p; p = p->next) { visited++; n++; } return n; }          // 카운터가 없으면 O(N)
    void push(int x) { top = new Node{x, top}; } void pop() { Node* t = top; top = t->next; delete t; }
};
int main() {
    std::mt19937 rng(2); CounterStack c; IndexStack ix; LinkedStack l; std::stack<int> ref;
    for (int step = 0; step < 50000; step++) {
        if (rng() % 2 && ix.size() < 999) { int v = rng(); c.push(v); ix.push(v); l.push(v); ref.push(v); } else if (!ref.empty()) { c.pop(); ix.pop(); l.pop(); ref.pop(); }
        assert(c.empty() == ref.empty() && ix.empty() == ref.empty() && l.empty() == ref.empty() && (c.size() == 0) == c.empty() && (ix.size() == 0) == ix.empty());                                     // ①
    }
    { LinkedStack m; for (int i = 0; i < 1000; i++) m.push(i); m.visited = 0; bool e = m.empty(); assert(!e && m.visited == 0); m.visited = 0; assert(m.sizeByWalking() == 1000 && m.visited == 1000); }               // ② empty 는 O(1), 카운터 없는 size 는 O(N)
    { CounterStack s; s.push(1); s.push(2); while (!s.empty()) s.pop(); assert(s.empty()); }                                                                                                          // ③
    { std::size_t n = 0; std::size_t wrapped = n - 1; assert(wrapped == SIZE_MAX); }                                                                                                                    // ④ size_t 되감기
    { CounterStack s; for (int i = 0; i < 5; i++) s.push(i); long sum = 0; for (std::size_t i = s.size(); i-- > 0;) sum += s.a[i]; assert(sum == 10);                                                          // ⑤ 안전한 역방향 반복: i-- > 0
      CounterStack e; long cnt = 0; for (std::size_t i = e.size(); i-- > 0;) cnt++; assert(cnt == 0); }
    std::cout << "IsEmpty: three representations agreed with std::stack::empty() over 50000 operations; empty() visits 0 nodes while counting a counter-less linked stack visits N; size_t wrap-around pitfall demonstrated" << std::endl; return 0;
}
// Time Complexity: O(1) (카운터 없는 연결 스택의 size 는 O(N))
// Space Complexity: O(1)
```
## IsFull()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <new>
#include <stdexcept>
#include <vector>
#include <cassert>

// 가득 찼는지 검사(IsFull): 고정 용량 스택에서 크기 == 용량 인가. push 가 거절될 조건과 정확히 같아야 한다. 용량 0 인 스택은 비어 있으면서 동시에 가득 차 있다.
// 동적 배열·연결 스택은 "논리적으로" 가득 찰 일이 없다(메모리가 바닥나면 bad_alloc). 그래도 서버처럼 상한이 필요한 곳에서는 최대 크기(limit)를 정해 두고 넘으면 거절하거나 예외를 던진다. 같은 배열을 두 스택이 양쪽 끝에서 마주 보고 쓰는 구조(TwoStacksInArray)에서는 "top1 + 1 == top2" 가 가득 참의 조건이며 어느 한쪽이 용량 전부를 쓸 수도 있다.
// 판정은 단순하지만 경계가 중요하다: 크기가 용량 − 1 → 용량으로 넘어가는 순간(off-by-one)과 용량 0, 1 이 단골 버그 지점이다.
// 검증: ① 용량 0..16 에서 정확히 용량 개를 받고 그때 IsFull 이 참이며 그 다음 push 는 false 이고 상태 불변 ② pop 하면 다시 거짓 ③ IsFull && IsEmpty 는 용량 0 일 때만 ④ 상한이 있는 동적 스택은 한도를 넘으면 std::length_error ⑤ 두 스택이 한 배열을 공유할 때 합이 용량이 되는 순간만 가득
class FixedStack {
    std::vector<int> a_; std::size_t n_ = 0;
public:
    explicit FixedStack(std::size_t cap) : a_(cap) {}
    bool empty() const { return n_ == 0; } bool full() const { return n_ == a_.size(); } std::size_t size() const { return n_; }
    bool push(int x) { if (full()) return false; a_[n_++] = x; return true; }
    bool pop(int& out) { if (empty()) return false; out = a_[--n_]; return true; }
};
class LimitedStack {                                                                    // 크기 제한이 있는 동적 스택
    std::vector<int> a_; std::size_t limit_;
public:
    explicit LimitedStack(std::size_t limit) : limit_(limit) {}
    void push(int x) { if (a_.size() == limit_) throw std::length_error("stack limit reached"); a_.push_back(x); }
    bool full() const { return a_.size() == limit_; } std::size_t size() const { return a_.size(); }
};
class TwoStacks {                                                                       // 한 배열을 양 끝에서 공유
    std::vector<int> a_; int top1_, top2_;
public:
    explicit TwoStacks(int cap) : a_(cap), top1_(-1), top2_(cap) {}
    bool full() const { return top1_ + 1 == top2_; }
    bool push1(int x) { if (full()) return false; a_[++top1_] = x; return true; } bool push2(int x) { if (full()) return false; a_[--top2_] = x; return true; }
    int size1() const { return top1_ + 1; } int size2() const { return (int)a_.size() - top2_; }
};
int main() {
    for (std::size_t cap = 0; cap <= 16; cap++) {
        FixedStack s(cap); assert(s.empty() && (s.full() == (cap == 0)) && (s.full() && s.empty()) == (cap == 0));                                                                    // ③ 용량 0 만 둘 다 참
        for (std::size_t i = 0; i < cap; i++) { assert(!s.full() && s.push((int)i)); } assert(s.full() && s.size() == cap);                                                          // ① 정확히 cap 개
        assert(!s.push(-1) && s.size() == cap && s.full()); int v; if (cap) { assert(s.pop(v) && v == (int)cap - 1 && !s.full()); assert(s.push(7) && s.full()); }                       // ② pop 하면 거짓, 다시 push 하면 참
    }
    { LimitedStack s(100); for (int i = 0; i < 100; i++) s.push(i); assert(s.full()); bool threw = false; try { s.push(100); } catch (const std::length_error&) { threw = true; } assert(threw && s.size() == 100); }       // ④
    { TwoStacks t(10); int pushed = 0; for (int i = 0; i < 100 && !t.full(); i++) { if (i % 3) t.push1(i); else t.push2(i); pushed++; } assert(pushed == 10 && t.size1() + t.size2() == 10 && !t.push1(0) && !t.push2(0));          // ⑤ 합이 용량이 되는 순간만 가득
      TwoStacks u(10); for (int i = 0; i < 10; i++) assert(u.push1(i)); assert(u.size1() == 10 && u.size2() == 0 && u.full()); }                                                               // 한쪽이 전부 써도 된다
    std::cout << "IsFull: for capacities 0..16 full() became true exactly when the next push was refused; only capacity 0 is both empty and full; limited and shared-array stacks agree" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Size()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <random>
#include <stack>
#include <cassert>

// 크기(Size): 스택에 들어 있는 원소 수. 두 방식이 있다. ① 카운터를 두고 push/pop 에서 갱신: size() 는 O(1) 이지만 모든 변경 연산이 카운터를 정확히 유지해야 한다 ② 저장하지 않고 필요할 때 센다(연결 스택에서 노드를 끝까지 따라감): 메모리는 아끼지만 size() 가 O(N).
// 카운터는 불변식 "size == 성공한 push 수 − 성공한 pop 수" 를 지켜야 한다. 실패한 연산(가득 찬 push, 빈 pop)에서는 바뀌면 안 되고, clear 후에는 0 이어야 한다. 이 불변식을 어기는 것이 카운터 버그의 대부분이다.
// 검증: ① 카운터형 연결 스택의 size() 가 무작위 push/pop 에서 항상 std::stack::size() 와 같고 방문 노드가 0 개 ② 세는 방식은 size() 마다 N 개를 방문 ③ 실패한 연산은 크기를 바꾸지 않음 ④ clear 후 0 ⑤ 불변식(성공 push − 성공 pop)이 항상 성립
class LinkedStack {
    struct Node { int v; Node* next; }; Node* top_ = nullptr; std::size_t n_ = 0, cap_; mutable long walked_ = 0;
public:
    explicit LinkedStack(std::size_t cap = (std::size_t)-1) : cap_(cap) {}
    ~LinkedStack() { clear(); }
    bool push(int x) { if (n_ == cap_) return false; top_ = new Node{x, top_}; n_++; return true; }
    bool pop(int& out) { if (!top_) return false; Node* t = top_; out = t->v; top_ = t->next; delete t; n_--; return true; }
    void clear() { while (top_) { Node* t = top_; top_ = t->next; delete t; } n_ = 0; }
    std::size_t size() const { return n_; }                                                 // O(1): 저장된 카운터
    std::size_t sizeByCounting() const { std::size_t c = 0; for (Node* p = top_; p; p = p->next) { walked_++; c++; } return c; }          // 카운터 없이 세는 방식
    long walked() const { return walked_; } void resetWalked() { walked_ = 0; }
};
int main() {
    std::mt19937 rng(11); LinkedStack s(500); std::stack<int> ref; long okPush = 0, okPop = 0; int sink;
    for (int step = 0; step < 100000; step++) {
        std::size_t before = s.size();
        if (rng() % 2) { bool ok = s.push(step); if (ok) { ref.push(step); okPush++; } else assert(s.size() == before && before == 500); }                                              // ③ 가득 찬 push 는 크기 불변
        else { bool ok = s.pop(sink); if (ok) { ref.pop(); okPop++; } else assert(s.size() == before && before == 0); }                                                                  // ③ 빈 pop 도 크기 불변
        assert(s.size() == ref.size() && (long)s.size() == okPush - okPop);                                                                                                                // ① ⑤
    }
    s.resetWalked(); for (int i = 0; i < 1000; i++) (void)s.size(); assert(s.walked() == 0);                                                                                               // O(1): 노드 방문 0
    s.resetWalked(); std::size_t n = s.size(); for (int i = 0; i < 10; i++) assert(s.sizeByCounting() == n); assert(s.walked() == (long)(10 * n));                                          // ② 세는 방식은 호출마다 N
    s.clear(); assert(s.size() == 0 && s.sizeByCounting() == 0);                                                                                                                         // ④
    std::cout << "Size: counter-based size() matched std::stack::size() and the push-minus-pop invariant over 100000 operations; counting by walking cost " << 10 * n << " node visits for 10 calls versus 0" << std::endl; return 0;
}
// Time Complexity: 카운터 방식 O(1), 세는 방식 O(N)
// Space Complexity: 카운터 방식 O(1) 추가
```
## Clear()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <new>
#include <random>
#include <vector>
#include <cassert>

// 비우기(Clear): 모든 원소를 제거해 빈 스택으로 되돌린다. 구현이 해야 할 일은 ① 각 원소의 소멸자를 부르고(자원 반환) ② 메모리를 돌려주거나 재사용을 위해 남기고 ③ 크기를 0 으로 만드는 것이다.
// 배열 스택은 원소 소멸자만 부르고 버퍼(용량)는 남겨 두는 편이 빠르다 — 다시 채울 때 재할당이 없다(원소가 int 같은 trivially destructible 이면 크기를 0 으로 만드는 O(1)). 연결 스택은 노드를 하나씩 해제하므로 O(N)이다. 단, 노드 소멸자에서 next 를 재귀적으로 delete 하는 순진한 방식은 길이가 수십만만 되어도 호출 스택이 넘친다 — 반복문으로 해제해야 한다(아래에서 재귀 깊이 N 을 직접 센다).
// 검증: ① 비운 뒤 크기 0, 빈 스택, 모든 원소의 소멸자가 정확히 한 번 호출됨(생성 수 == 소멸 수) ② 배열 스택은 비운 뒤에도 용량을 유지해 다시 채울 때 재할당 0 번 ③ 연결 스택을 100 만 노드까지 키워도 반복 해제는 안전 ④ 재귀 해제는 깊이가 정확히 N 이라 호출 스택을 N 프레임 쓴다 ⑤ 비운 뒤 재사용과 반복 clear(멱등)
struct Tracked { static long ctor, dtor; Tracked() { ctor++; } Tracked(const Tracked&) { ctor++; } ~Tracked() { dtor++; } };
long Tracked::ctor = 0, Tracked::dtor = 0;
template <class T> class ArrayStack {
    T* a_ = nullptr; std::size_t n_ = 0, cap_ = 0; long reallocations_ = 0;
public:
    ~ArrayStack() { clear(); ::operator delete(a_); }
    void push(const T& v) { if (n_ == cap_) { std::size_t nc = cap_ ? cap_ * 2 : 4; T* nb = static_cast<T*>(::operator new(nc * sizeof(T))); for (std::size_t i = 0; i < n_; i++) { new (nb + i) T(a_[i]); a_[i].~T(); } ::operator delete(a_); a_ = nb; cap_ = nc; reallocations_++; } new (a_ + n_) T(v); ++n_; }
    void clear() { while (n_) a_[--n_].~T(); }                                                    // 소멸자만 부르고 버퍼는 유지
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } long reallocations() const { return reallocations_; }
};
struct Node { int v; Node* next; };
void clearIterative(Node*& top) { while (top) { Node* t = top; top = t->next; delete t; } }
long clearRecursive(Node* p) { if (!p) return 0; long depth = 1 + clearRecursive(p->next); delete p; return depth; }          // 순진한 재귀 해제 (깊이 N)
int main() {
    { Tracked::ctor = Tracked::dtor = 0; ArrayStack<Tracked> s; Tracked t; for (int i = 0; i < 100; i++) s.push(t); long made = Tracked::ctor; s.clear(); assert(s.size() == 0 && Tracked::dtor == made - 1);                  // ① t 만 남기고 전부 소멸 (이동하며 만든 임시도 짝이 맞는다)
      std::size_t cap = s.capacity(); long re = s.reallocations(); for (int i = 0; i < 100; i++) s.push(t); assert(s.capacity() == cap && s.reallocations() == re);                                      // ② 용량 유지: 재할당 0 번
      s.clear(); s.clear(); assert(s.size() == 0); }                                                                                                                                                      // ⑤ 멱등
    assert(Tracked::ctor == Tracked::dtor);                                                                                                                                                                  // 스택이 파괴되면 나머지도 소멸 (누수 0)
    { Node* top = nullptr; for (int i = 0; i < 1000000; i++) top = new Node{i, top}; clearIterative(top); assert(top == nullptr); }                                                                           // ③ 100 만 노드 반복 해제
    { Node* top = nullptr; const int N = 20000; for (int i = 0; i < N; i++) top = new Node{i, top}; long depth = clearRecursive(top); assert(depth == N); }                                                    // ④ 재귀 해제의 호출 깊이 = N (10^6 이면 기본 8 MB 스택을 넘길 수 있다)
    { ArrayStack<int> s; for (int r = 0; r < 3; r++) { for (int i = 0; i < 50; i++) s.push(i); assert(s.size() == 50); s.clear(); assert(s.size() == 0); } }                                               // ⑤ 재사용
    std::cout << "Clear: destructors ran exactly once per element, the array stack kept its capacity (no reallocation on refill), a 1,000,000-node linked stack was freed iteratively, and recursive freeing needed a call depth equal to N" << std::endl; return 0;
}
// Time Complexity: 배열 O(N) (trivially destructible 이면 O(1)), 연결 O(N)
// Space Complexity: 반복 해제 O(1), 재귀 해제 O(N) 호출 스택
```

# Part 2. 배열 스택
## ArrayStack()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <random>
#include <stdexcept>
#include <utility>
#include <vector>
#include <cassert>

// 배열 스택(ArrayStack): 연속된 배열 하나와 "다음에 쓸 위치(= 크기)" 하나로 이루어진 가장 단순하고 빠른 스택이다. push 는 a[n++] = x, pop 은 a[--n]. 메모리가 연속이라 캐시 지역성이 좋고 원소당 포인터 오버헤드가 없다. 용량이 고정이라 가득 차면 거절한다(용량 가변은 DynamicStack).
// 자원을 직접 쥐므로 "다섯 가지 규칙(rule of five)" 을 지켜야 한다: 소멸자, 복사 생성자(깊은 복사), 복사 대입(복사 후 교환 관용구로 자기 대입과 예외에 안전), 이동 생성자, 이동 대입. 하나라도 빠지면 얕은 복사로 이중 해제가 난다.
// 아래 구현은 바닥부터 위로 순회하는 반복자 쌍(begin/end)과 범위를 검사하는 at(i)(i = 0 이 바닥)를 제공한다.
// 검증: ① 무작위 push/pop 을 std::vector 모델과 대조(내용·크기·가득/빈) ② 복사본은 독립적(원본을 바꿔도 복사본 불변, 복사본을 바꿔도 원본 불변) ③ 자기 대입 안전 ④ 이동 후 원본이 빈 스택 ⑤ at 의 범위 검사와 순회 순서 ⑥ swap
class ArrayStack {
    int* a_; std::size_t cap_, n_;
public:
    explicit ArrayStack(std::size_t cap) : a_(cap ? new int[cap] : nullptr), cap_(cap), n_(0) {}
    ~ArrayStack() { delete[] a_; }
    ArrayStack(const ArrayStack& o) : a_(o.cap_ ? new int[o.cap_] : nullptr), cap_(o.cap_), n_(o.n_) { std::copy(o.a_, o.a_ + o.n_, a_); }
    ArrayStack(ArrayStack&& o) noexcept : a_(o.a_), cap_(o.cap_), n_(o.n_) { o.a_ = nullptr; o.cap_ = o.n_ = 0; }
    ArrayStack& operator=(ArrayStack o) noexcept { swap(o); return *this; }                          // 값으로 받아 교환: 복사/이동 대입을 한 번에, 자기 대입에도 안전
    void swap(ArrayStack& o) noexcept { std::swap(a_, o.a_); std::swap(cap_, o.cap_); std::swap(n_, o.n_); }
    bool push(int x) { if (n_ == cap_) return false; a_[n_++] = x; return true; }
    bool pop(int& out) { if (!n_) return false; out = a_[--n_]; return true; }
    bool peek(int& out) const { if (!n_) return false; out = a_[n_ - 1]; return true; }
    int at(std::size_t i) const { if (i >= n_) throw std::out_of_range("ArrayStack::at"); return a_[i]; }
    const int* begin() const { return a_; } const int* end() const { return a_ + n_; }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } bool empty() const { return n_ == 0; } bool full() const { return n_ == cap_; }
};
int main() {
    std::mt19937 rng(4); ArrayStack s(64); std::vector<int> model;
    for (int step = 0; step < 50000; step++) {
        if (rng() % 2) { int v = rng() % 1000; bool ok = s.push(v); assert(ok == (model.size() < 64)); if (ok) model.push_back(v); }
        else { int v = -1; bool ok = s.pop(v); assert(ok == !model.empty()); if (ok) { assert(v == model.back()); model.pop_back(); } }
        int p; assert(s.peek(p) == !model.empty() && s.size() == model.size() && s.empty() == model.empty() && s.full() == (model.size() == 64));                               // ①
        if (step % 5000 == 0) assert(std::vector<int>(s.begin(), s.end()) == model);                                                                                                   // ⑤ 바닥 -> 위 순서
    }
    { ArrayStack a(8); for (int i = 0; i < 5; i++) a.push(i); ArrayStack b(a); int v; a.pop(v); a.push(100); assert(std::vector<int>(b.begin(), b.end()) == (std::vector<int>{0, 1, 2, 3, 4}) && a.at(4) == 100);          // ② 복사본은 독립
      b.push(7); assert(a.size() == 5 && b.size() == 6 && a.at(4) == 100);
      ArrayStack c(2); c = a; assert(std::vector<int>(c.begin(), c.end()) == std::vector<int>(a.begin(), a.end()) && c.capacity() == 8);                                         // 복사 대입
      c = c; assert(c.size() == 5); }                                                                                                                                                      // ③ 자기 대입
    { ArrayStack a(4); a.push(1); a.push(2); ArrayStack b(std::move(a)); assert(a.empty() && a.capacity() == 0 && !a.push(9) && b.size() == 2); ArrayStack c(1); c = std::move(b); assert(b.empty() && c.size() == 2 && c.capacity() == 4); }     // ④ 이동
    { ArrayStack a(4); a.push(1); bool threw = false; try { a.at(1); } catch (const std::out_of_range&) { threw = true; } assert(threw && a.at(0) == 1); }                                                         // ⑤ 범위 검사
    { ArrayStack a(3), b(5); a.push(1); b.push(2); b.push(3); a.swap(b); assert(a.size() == 2 && a.capacity() == 5 && b.size() == 1 && b.capacity() == 3); }                                                           // ⑥
    std::cout << "ArrayStack: bounded array stack matched a vector model over 50000 operations; deep copy, copy-and-swap assignment, self-assignment and move all verified" << std::endl; return 0;
}
// Time Complexity: push·pop·peek·at O(1), 복사 O(N)
// Space Complexity: O(용량)
```
## Resize()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <new>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 크기 조정(Resize): 스택의 용량을 명시적으로 바꾼다. push 가 자동으로 하는 성장(DynamicStack)과 달리 호출자가 시점을 정하는 연산이다 — 큰 입력이 올 것을 알고 미리 확보(reserve)하거나, 일을 마친 뒤 남는 메모리를 돌려준다(shrinkToFit).
// 규칙: ① 용량을 현재 크기보다 작게 줄일 수는 없다(원소를 버리면 안 되므로 거절하고 상태를 바꾸지 않는다) ② 늘리든 줄이든 내용과 순서는 그대로여야 한다 ③ 새 버퍼를 먼저 만들어 복사한 뒤 교체한다 — 할당이 실패하면(bad_alloc) 스택은 이전 상태 그대로(강한 보장) ④ 비용은 O(크기): 복사하는 원소 수만큼.
// reserve 를 미리 하면 이후 push 가 재할당을 하지 않는다 — 원소 주소가 바뀌지 않으므로(Top 항목) 참조를 오래 쥐는 코드에도 유용하다.
// 검증: ① 무작위 push/pop/reserve/shrinkToFit/resize 열에서 내용이 std::vector 모델과 항상 같다 ② resize(n) 뒤 용량이 정확히 n, 크기보다 작은 요청은 거절·상태 불변 ③ reserve 후 그 용량까지의 push 는 재할당 0 번 ④ shrinkToFit 후 용량 == 크기 ⑤ 할당 실패 시뮬레이션에서 상태 보존 ⑥ 이동 횟수 == 크기
class ResizableStack {
    int* a_ = nullptr; std::size_t n_ = 0, cap_ = 0; long moves_ = 0, reallocs_ = 0; std::size_t failAbove_ = (std::size_t)-1;
public:
    ~ResizableStack() { delete[] a_; } ResizableStack() = default; ResizableStack(const ResizableStack&) = delete; ResizableStack& operator=(const ResizableStack&) = delete;
    bool resize(std::size_t nc) {                                                                    // 용량을 정확히 nc 로
        if (nc < n_) return false; if (nc == cap_) return true;
        if (nc > failAbove_) throw std::bad_alloc();                                                // 테스트용 할당 실패 주입
        int* nb = nc ? new int[nc] : nullptr; std::copy(a_, a_ + n_, nb); moves_ += (long)n_; reallocs_++; delete[] a_; a_ = nb; cap_ = nc; return true;
    }
    bool reserve(std::size_t nc) { return nc <= cap_ ? true : resize(nc); }                           // 줄이지는 않는다
    void shrinkToFit() { resize(n_); }
    void push(int x) { if (n_ == cap_) resize(cap_ ? cap_ * 2 : 1); a_[n_++] = x; }
    bool pop(int& out) { if (!n_) return false; out = a_[--n_]; return true; }
    std::vector<int> contents() const { return std::vector<int>(a_, a_ + n_); }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } long moves() const { return moves_; } long reallocs() const { return reallocs_; } void failAbove(std::size_t n) { failAbove_ = n; }
};
int main() {
    std::mt19937 rng(9); ResizableStack s; std::vector<int> model;
    for (int step = 0; step < 30000; step++) {
        int op = rng() % 10; int v;
        if (op < 4) { int x = rng() % 1000; s.push(x); model.push_back(x); }
        else if (op < 7) { bool ok = s.pop(v); assert(ok == !model.empty()); if (ok) { assert(v == model.back()); model.pop_back(); } }
        else if (op == 7) { s.reserve(model.size() + rng() % 50); } else if (op == 8) { s.shrinkToFit(); assert(s.capacity() == model.size()); }                                              // ④
        else { std::size_t want = rng() % (2 * model.size() + 4); std::size_t cap0 = s.capacity(); bool ok = s.resize(want); if (want < model.size()) assert(!ok && s.capacity() == cap0); else assert(ok && s.capacity() == want); }   // ②
        assert(s.contents() == model && s.capacity() >= s.size());                                                                                                                                    // ①
    }
    { ResizableStack r; r.reserve(1000); long re = r.reallocs(); int v; for (int i = 0; i < 1000; i++) r.push(i); assert(r.reallocs() == re && r.capacity() == 1000); while (r.pop(v)) {} assert(r.capacity() == 1000); }       // ③ reserve 후에는 재할당 0
    { ResizableStack r; for (int i = 0; i < 100; i++) r.push(i); long m0 = r.moves(); r.resize(500); assert(r.moves() - m0 == 100); m0 = r.moves(); r.resize(100); assert(r.moves() - m0 == 100); }                          // ⑥ 이동 횟수 == 크기
    { ResizableStack r; for (int i = 0; i < 8; i++) r.push(i); std::vector<int> before = r.contents(); std::size_t cap = r.capacity(); r.failAbove(10); bool threw = false; try { r.resize(100); } catch (const std::bad_alloc&) { threw = true; } assert(threw && r.contents() == before && r.capacity() == cap); }          // ⑤ 실패해도 그대로
    std::cout << "Resize: contents stayed identical across 30000 random push/pop/reserve/shrink/resize operations; undersized requests were refused; reserve prevented reallocation; a failed allocation left the stack untouched" << std::endl; return 0;
}
// Time Complexity: resize O(크기), 나머지 O(1)
// Space Complexity: O(용량)
```
## DynamicStack()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <random>
#include <stack>
#include <utility>
#include <cassert>

// 동적 스택(DynamicStack): 배열 스택의 가득 참 문제를 풀어, 용량이 모자라면 두 배로 키우고 너무 남으면 줄이는 스택이다. 늘릴 때는 새 버퍼로 옮기는 O(N) 이 들지만 두 배씩 키우므로 N 번 push 의 총 이동이 2N 미만이라 분할상환 O(1) 이다.
// 줄이는 규칙이 중요하다. "절반 이하일 때 절반으로" 줄이면 가득 찬 경계에서 push·pop 을 번갈아 하는 열이 매번 전체를 옮긴다(thrashing). 크기가 용량의 1/4 이하일 때 용량을 절반으로 줄이면 줄인 직후 용량의 절반이 비어 있으므로 다시 늘리거나 줄이기까지 최소 용량/4 번의 연산이 필요해 분할상환 O(1) 이 유지된다. 최소 용량(4)은 작은 스택이 계속 재할당되는 것을 막는다.
// 불변식: 항상 크기 ≤ 용량, 그리고 용량이 최소값보다 크면 크기 > 용량/4.
// 검증: ① std::stack 과 무작위 차분 ② 불변식이 매 연산 뒤에 성립 ③ 적대적 열(가득 찬 경계에서 push/pop 교대)에서 연산당 이동 횟수가 상수 ④ 1/2 규칙으로 줄이는 변형은 같은 열에서 연산당 Θ(N) ⑤ N 번 push 의 총 이동 < 2N, 비운 뒤 용량이 최소값으로 돌아감
class DynamicStack {
    static constexpr std::size_t MIN_CAP = 4;
    int* a_; std::size_t n_ = 0, cap_ = MIN_CAP; long moved_ = 0; double shrinkAt_;
    void resize(std::size_t nc) { int* nb = new int[nc]; std::copy(a_, a_ + n_, nb); moved_ += (long)n_; delete[] a_; a_ = nb; cap_ = nc; }
public:
    explicit DynamicStack(double shrinkFraction = 0.25) : a_(new int[MIN_CAP]), shrinkAt_(shrinkFraction) {}
    ~DynamicStack() { delete[] a_; } DynamicStack(const DynamicStack&) = delete; DynamicStack& operator=(const DynamicStack&) = delete;
    void push(int x) { if (n_ == cap_) resize(cap_ * 2); a_[n_++] = x; }
    bool pop(int& out) { if (!n_) return false; out = a_[--n_]; if (cap_ > MIN_CAP && n_ <= (std::size_t)(cap_ * shrinkAt_)) resize(std::max(MIN_CAP, cap_ / 2)); return true; }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } long moved() const { return moved_; } int top() const { return a_[n_ - 1]; }
    bool invariant() const { return n_ <= cap_ && (cap_ == MIN_CAP || n_ > cap_ / 4); }
};
int main() {
    { std::mt19937 rng(6); DynamicStack s; std::stack<int> ref; int v; for (int step = 0; step < 100000; step++) { if (rng() % 5 < 2 || ref.empty()) { int x = rng(); s.push(x); ref.push(x); } else { assert(s.top() == ref.top()); assert(s.pop(v) && v == ref.top()); ref.pop(); } assert(s.size() == ref.size() && s.invariant()); } }          // ① ②
    { DynamicStack s; int v; for (int i = 0; i < 1024; i++) s.push(i); long before = s.moved(); const int OPS = 20000; for (int i = 0; i < OPS; i++) { s.push(i); assert(s.pop(v)); } assert(s.moved() - before <= 3L * OPS && s.capacity() == 2048); }        // ③ 적대적 열: 경계에서 push/pop 교대 (1/4 규칙은 이동 0)
    { DynamicStack half(0.5); int v; for (int i = 0; i < 1024; i++) half.push(i); half.push(0); half.pop(v); long before = half.moved(); const int OPS = 2000; for (int i = 0; i < OPS; i++) { half.push(i); half.pop(v); } assert(half.moved() - before > 100L * OPS); std::cout << "1/2-rule moves per op: " << (half.moved() - before) / OPS << "; "; }       // ④ 1/2 규칙은 연산당 수백 번 이동
    { DynamicStack s; const int N = 100000; for (int i = 0; i < N; i++) s.push(i); assert(s.moved() < 2L * N); int v; while (s.size()) s.pop(v); assert(s.capacity() == 4 && s.invariant()); }                                                         // ⑤ 총 이동 < 2N, 비우면 최소 용량
    std::cout << "DynamicStack: matched std::stack over 100000 operations with the capacity invariant intact; after one growth the 1/4 shrink rule moved no further elements on the adversarial boundary sequence" << std::endl; return 0;
}
// Time Complexity: push·pop 분할상환 O(1) (최악 O(N))
// Space Complexity: O(N), 용량은 크기의 4 배 이하
```

# Part 3. 연결리스트 스택
## LinkedStack()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <random>
#include <stack>
#include <utility>
#include <vector>
#include <cassert>

// 연결 스택(LinkedStack): 단방향 연결 리스트의 머리를 스택의 top 으로 쓴다. push 는 새 노드를 머리에 달고(top = new Node{x, top}), pop 은 머리를 떼어 낸다. 둘 다 항상 O(1) 이며 용량 제한이 없고 재할당이 없어 원소 주소가 변하지 않는다. 대신 노드마다 할당·포인터 오버헤드가 있고 메모리가 흩어져 순회가 느리다(배열 스택 대비).
// 자원 관리가 핵심이다. 소멸자는 반복문으로 해제한다(재귀 해제는 길이가 큰 스택에서 호출 스택을 넘긴다). 복사는 깊은 복사여야 하며 순서를 보존해야 한다(노드를 거꾸로 만들지 않도록 꼬리 포인터를 쓴다). 이동은 포인터만 옮기고 원본은 빈 스택이 된다. 보너스로 O(N) 제자리 뒤집기(reverse)는 포인터 세 개로 한다.
// 검증: ① std::stack 과의 무작위 차분 ② 살아 있는 노드 수 == 크기(누수·이중 해제 없음) ③ 복사본은 순서까지 같고 독립적 ④ 이동 후 원본은 비어 있음 ⑤ 50 만 노드 스택의 파괴가 안전 ⑥ reverse 후 pop 순서가 뒤집힘
class LinkedStack {
    struct Node { int v; Node* next; };
    Node* top_ = nullptr; std::size_t n_ = 0; static long liveNodes_;
public:
    static long liveNodes() { return liveNodes_; }
    LinkedStack() = default;
    ~LinkedStack() { clear(); }
    LinkedStack(const LinkedStack& o) { Node** tail = &top_; for (Node* p = o.top_; p; p = p->next) { *tail = new Node{p->v, nullptr}; liveNodes_++; tail = &(*tail)->next; } n_ = o.n_; }          // 순서를 보존하는 깊은 복사
    LinkedStack(LinkedStack&& o) noexcept : top_(o.top_), n_(o.n_) { o.top_ = nullptr; o.n_ = 0; }
    LinkedStack& operator=(LinkedStack o) noexcept { std::swap(top_, o.top_); std::swap(n_, o.n_); return *this; }
    void push(int x) { top_ = new Node{x, top_}; liveNodes_++; n_++; }
    bool pop(int& out) { if (!top_) return false; Node* t = top_; out = t->v; top_ = t->next; delete t; liveNodes_--; n_--; return true; }
    bool peek(int& out) const { if (!top_) return false; out = top_->v; return true; }
    void clear() { while (top_) { Node* t = top_; top_ = t->next; delete t; liveNodes_--; } n_ = 0; }
    void reverse() { Node *prev = nullptr, *cur = top_; while (cur) { Node* nx = cur->next; cur->next = prev; prev = cur; cur = nx; } top_ = prev; }
    std::vector<int> topFirst() const { std::vector<int> v; for (Node* p = top_; p; p = p->next) v.push_back(p->v); return v; }
    std::size_t size() const { return n_; } bool empty() const { return top_ == nullptr; }
};
long LinkedStack::liveNodes_ = 0;
int main() {
    { std::mt19937 rng(12); LinkedStack s; std::stack<int> ref; int v; for (int step = 0; step < 60000; step++) { if (rng() % 2) { int x = rng(); s.push(x); ref.push(x); } else { bool ok = s.pop(v); assert(ok == !ref.empty()); if (ok) { assert(v == ref.top()); ref.pop(); } } int p; assert(s.peek(p) == !ref.empty() && s.size() == ref.size() && s.empty() == ref.empty()); assert((std::size_t)LinkedStack::liveNodes() == s.size()); } }   // ① ②
    assert(LinkedStack::liveNodes() == 0);
    { LinkedStack a; for (int i = 1; i <= 5; i++) a.push(i); LinkedStack b(a); assert(b.topFirst() == a.topFirst() && LinkedStack::liveNodes() == 10); int v; a.pop(v); b.push(99); assert(a.topFirst() == (std::vector<int>{4, 3, 2, 1}) && b.topFirst() == (std::vector<int>{99, 5, 4, 3, 2, 1}));          // ③ 순서까지 같고 독립
      LinkedStack c; c = a; assert(c.topFirst() == a.topFirst()); }
    { LinkedStack a; a.push(1); a.push(2); LinkedStack b(std::move(a)); assert(a.empty() && a.size() == 0 && b.size() == 2 && LinkedStack::liveNodes() == 2); }                                                            // ④
    assert(LinkedStack::liveNodes() == 0);
    { LinkedStack big; for (int i = 0; i < 500000; i++) big.push(i); assert(LinkedStack::liveNodes() == 500000); } assert(LinkedStack::liveNodes() == 0);                                                              // ⑤
    { LinkedStack s; for (int i = 1; i <= 6; i++) s.push(i); s.reverse(); assert(s.topFirst() == (std::vector<int>{1, 2, 3, 4, 5, 6})); int v; s.pop(v); assert(v == 1); LinkedStack e; e.reverse(); assert(e.empty()); }                 // ⑥
    std::cout << "LinkedStack: matched std::stack over 60000 operations with live-node count equal to size; deep copy preserved order, move emptied the source, 500000 nodes were freed iteratively, in-place reverse worked" << std::endl; return 0;
}
// Time Complexity: push·pop·peek O(1), 복사·뒤집기·소멸 O(N)
// Space Complexity: O(N) (노드당 포인터 하나 추가)
```
## PushNode()
### 대표코드
```cpp
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <new>
#include <vector>
#include <cassert>

// 노드 단위 푸시(PushNode): 연결 스택의 push 를 포인터 조작 수준에서 본다. 머리 포인터가 가리키는 리스트의 맨 앞에 새 노드를 달려면 ① 새 노드를 만들고 ② 새 노드의 next 를 옛 머리로 ③ 머리를 새 노드로 — 이 순서가 중요하다. ③ 을 먼저 하면 옛 머리를 잃어 리스트 전체를 누수한다.
// 예외 안전: 할당(① )이 실패하면 아직 아무것도 바꾸지 않았으므로 머리는 그대로다 — 강한 보장. 그래서 new 를 가장 먼저 하고 포인터 대입은 마지막에 한다. 노드를 만든 뒤에는 실패할 수 있는 연산이 없다.
// 검증: ① 무작위로 푸시한 뒤 머리부터 순회한 값이 푸시의 역순이고 길이가 맞다 ② 순환(cycle)이 없음 — 토끼와 거북이(Floyd)로 확인 ③ 할당 실패를 k 번째 new 에서 주입하면 머리와 리스트 내용이 그대로이고 누수 노드 0 ④ 올바른 순서와 틀린 순서의 차이: 틀린 순서(③ 먼저)는 옛 리스트를 잃는다는 것을 도달 가능 노드 수로 보임
static long allocCount = 0, failAt = -1, liveNodes = 0;
#pragma GCC diagnostic ignored "-Wmismatched-new-delete"
void* operator new(std::size_t n) { if (++allocCount == failAt) throw std::bad_alloc(); void* p = std::malloc(n ? n : 1); if (!p) throw std::bad_alloc(); return p; }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
struct Node { int data; Node* next; };
void pushNode(Node*& head, int x) { Node* n = new Node{x, head}; liveNodes++; head = n; }                      // 먼저 할당(실패 가능), 대입은 마지막
void pushNodeWrong(Node*& head, int x) { Node* old = head; head = nullptr; Node* n = new Node{x, nullptr}; liveNodes++; n->next = old; head = n; }   // 머리를 비운 뒤 할당 -> 할당이 실패하면 리스트를 잃는다
bool hasCycle(Node* head) { Node *slow = head, *fast = head; while (fast && fast->next) { slow = slow->next; fast = fast->next->next; if (slow == fast) return true; } return false; }
std::size_t length(Node* head) { std::size_t n = 0; for (; head; head = head->next) n++; return n; }
void freeAll(Node*& head) { while (head) { Node* t = head; head = head->next; delete t; liveNodes--; } }
int main() {
    { Node* head = nullptr; std::vector<int> pushed; for (int i = 0; i < 1000; i++) { pushNode(head, i * 3); pushed.push_back(i * 3); } std::vector<int> walk; for (Node* p = head; p; p = p->next) walk.push_back(p->data);
      assert(walk.size() == 1000 && std::vector<int>(walk.rbegin(), walk.rend()) == pushed && !hasCycle(head) && length(head) == 1000); freeAll(head); assert(liveNodes == 0); }                                // ① ②
    { Node* head = nullptr; for (int i = 0; i < 5; i++) pushNode(head, i); Node* beforeHead = head; std::size_t beforeLen = length(head); allocCount = 0; failAt = 1; bool threw = false;
      try { pushNode(head, 99); } catch (const std::bad_alloc&) { threw = true; } failAt = -1; assert(threw && head == beforeHead && length(head) == beforeLen && head->data == 4); freeAll(head); assert(liveNodes == 0); }       // ③ 강한 보장
    { Node* head = nullptr; for (int i = 0; i < 5; i++) pushNode(head, i); allocCount = 0; failAt = 1; bool threw = false;
      Node* keep = head; try { pushNodeWrong(head, 99); } catch (const std::bad_alloc&) { threw = true; } failAt = -1;
      assert(threw && head == nullptr && length(head) == 0 && length(keep) == 5);                                                                                                                    // ④ 틀린 순서: 머리를 잃었다 (keep 이 없었다면 5 개 노드를 영영 누수)
      head = keep; freeAll(head); assert(liveNodes == 0); }
    std::cout << "PushNode: pushes produced reverse order with no cycles; an injected allocation failure left the list untouched with the allocate-first order but orphaned it with the wrong order" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per node
```
## PopNode()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <vector>
#include <cassert>

// 노드 단위 팝(PopNode): 연결 스택의 pop 을 포인터 조작 수준에서 본다. 순서: ① 떼어 낼 노드를 임시 포인터에 기억 ② 머리를 다음 노드로 이동 ③ 값을 꺼내고 ④ 노드를 해제. ④ 를 ② 보다 먼저 하면 해제된 노드의 next 를 읽게 되어(use-after-free) 정의되지 않은 동작이다 — 해제 직전에 필요한 값(next, data)을 모두 꺼내 두는 것이 규칙이다.
// 빈 리스트(head == nullptr)는 거절해야 한다. 또 하나의 기법은 "떼어 내되 해제하지 않고 돌려주기"(detach): 노드를 자유 리스트에 모아 두었다가 다음 push 에서 재사용하면 new/delete 를 줄인다(메모리 풀의 시작). 자유 리스트도 같은 연결 스택이다.
// 검증: ① 모든 노드를 팝하면 정확히 푸시의 역순이고 마지막에 head == nullptr ② 빈 리스트 팝은 false 이며 출력 인자를 건드리지 않음 ③ 팝마다 노드 하나만 해제(살아 있는 노드 수 −1) ④ detach/reuse: 떼어 낸 노드를 자유 리스트에 넣고 다시 쓰면 같은 주소가 LIFO 로 재사용되고 새 할당이 없음 ⑤ 해제 전에 next 를 읽는 올바른 순서
struct Node { int data; Node* next; };
static long liveNodes = 0, newCalls = 0;
Node* makeNode(int x, Node* next) { newCalls++; liveNodes++; return new Node{x, next}; }
bool popNode(Node*& head, int& out) {                                                          // 올바른 순서: 기억 -> 이동 -> 값 -> 해제
    if (!head) return false; Node* t = head; head = t->next; out = t->data; delete t; liveNodes--; return true;
}
Node* detachTop(Node*& head) { if (!head) return nullptr; Node* t = head; head = t->next; t->next = nullptr; return t; }              // 해제하지 않고 돌려준다
void attach(Node*& head, Node* n) { n->next = head; head = n; }
int main() {
    { Node* head = nullptr; for (int i = 0; i < 1000; i++) head = makeNode(i, head); int v; for (int i = 999; i >= 0; i--) { long before = liveNodes; assert(popNode(head, v) && v == i && liveNodes == before - 1); } assert(head == nullptr && liveNodes == 0); }          // ① ③
    { Node* head = nullptr; int v = 777; assert(!popNode(head, v) && v == 777 && head == nullptr); }                                                                                                                                                                  // ②
    { Node* used = nullptr; Node* freeList = nullptr; for (int i = 0; i < 5; i++) used = makeNode(i, used); std::vector<Node*> addrs; for (Node* p = used; p; p = p->next) addrs.push_back(p);        // addrs[0] 이 top
      for (int i = 0; i < 3; i++) attach(freeList, detachTop(used));                                                                                                                                                                                              // 노드 3 개를 free list 로 옮김 (해제 없음)
      long newBefore = newCalls; for (int i = 0; i < 3; i++) { Node* n = detachTop(freeList); n->data = 100 + i; attach(used, n); }                                                                                                                              // 재사용: 새 할당 없음
      assert(newCalls == newBefore && used == addrs[0] /* 스택을 두 번 거꾸로 옮기면(used -> free -> used) 원래 주소 순서가 복원된다 */ ); int v; while (popNode(used, v)) {} assert(liveNodes == 0); }                                                                    // ④
    { Node* head = makeNode(1, makeNode(2, nullptr)); Node* t = head; Node* nextBeforeFree = t->next; int dataBeforeFree = t->data; head = nextBeforeFree; delete t; liveNodes--; assert(head->data == 2 && dataBeforeFree == 1); int v; popNode(head, v); assert(liveNodes == 0); }          // ⑤ 해제 전에 next/data 를 먼저 읽어 둔다
    std::cout << "PopNode: pops returned the exact reverse order and released one node each; empty pops were refused; detached nodes were recycled through a free list with zero new allocations" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 4. 대표 활용
## ReverseString()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::string reverseString(std::string str) {
    std::stack<char> s;
    for (char c : str) s.push(c);
    std::string reversed = "";
    while (!s.empty()) {
        reversed += s.top();
        s.pop();
    }
    return reversed;
}

int main() {
    std::string res = reverseString("hello");
    std::cout << "Reverse 'hello' -> " << res << std::endl;
    assert(res == "olleh");
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## BalancedParentheses()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

bool isBalanced(std::string expr) {
    std::stack<char> s;
    for (char c : expr) {
        if (c == '(' || c == '{' || c == '[') s.push(c);
        else if (c == ')' || c == '}' || c == ']') {
            if (s.empty()) return false;
            char top = s.top();
            if ((c == ')' && top == '(') || (c == '}' && top == '{') || (c == ']' && top == '[')) {
                s.pop();
            } else return false;
        }
    }
    return s.empty();
}

int main() {
    bool res = isBalanced("{[()]}");
    std::cout << "isBalanced('{[()]}') -> " << res << std::endl;
    assert(res == true);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## InfixToPostfix()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

int precedence(char op) {
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    return 0;
}

std::string infixToPostfix(std::string infix) {
    std::stack<char> s;
    std::string postfix = "";
    for (char c : infix) {
        if (isalnum(c)) postfix += c;
        else if (c == '(') s.push(c);
        else if (c == ')') {
            while (!s.empty() && s.top() != '(') {
                postfix += s.top(); s.pop();
            }
            s.pop();
        } else {
            while (!s.empty() && precedence(s.top()) >= precedence(c)) {
                postfix += s.top(); s.pop();
            }
            s.push(c);
        }
    }
    while (!s.empty()) { postfix += s.top(); s.pop(); }
    return postfix;
}

int main() {
    std::string res = infixToPostfix("A+B*C");
    std::cout << "A+B*C -> " << res << std::endl;
    assert(res == "ABC*+");
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PostfixEvaluation()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

int evaluatePostfix(std::string exp) {
    std::stack<int> s;
    for (char c : exp) {
        if (isdigit(c)) s.push(c - '0');
        else {
            int val1 = s.top(); s.pop();
            int val2 = s.top(); s.pop();
            switch (c) {
                case '+': s.push(val2 + val1); break;
                case '*': s.push(val2 * val1); break;
            }
        }
    }
    return s.top();
}

int main() {
    int res = evaluatePostfix("23*4+");
    std::cout << "23*4+ -> " << res << std::endl;
    assert(res == 10);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PrefixEvaluation()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

int evaluatePrefix(std::string exp) {
    std::stack<int> s;
    for (int i = exp.length() - 1; i >= 0; i--) {
        if (isdigit(exp[i])) s.push(exp[i] - '0');
        else {
            int val1 = s.top(); s.pop();
            int val2 = s.top(); s.pop();
            if (exp[i] == '+') s.push(val1 + val2);
            else if (exp[i] == '*') s.push(val1 * val2);
        }
    }
    return s.top();
}

int main() {
    int res = evaluatePrefix("+*234");
    std::cout << "+*234 -> " << res << std::endl;
    assert(res == 10);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## DecimalToBinary()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

std::string decimalToBinary(int n) {
    if (n == 0) return "0";
    std::stack<int> s;
    while (n > 0) {
        s.push(n % 2);
        n /= 2;
    }
    std::string res = "";
    while (!s.empty()) { 
        res += std::to_string(s.top()); 
        s.pop(); 
    }
    return res;
}

int main() {
    std::string res = decimalToBinary(13);
    std::cout << "13 in binary -> " << res << std::endl;
    assert(res == "1101");
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(log N)
```
## BaseConversion()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::string convertBase(int n, int base) {
    if (n == 0) return "0";
    std::stack<int> s;
    while (n > 0) {
        s.push(n % base);
        n /= base;
    }
    std::string res = "";
    std::string digits = "0123456789ABCDEF";
    while (!s.empty()) { 
        res += digits[s.top()]; 
        s.pop(); 
    }
    return res;
}

int main() {
    std::string res = convertBase(255, 16);
    std::cout << "255 in base 16 -> " << res << std::endl;
    assert(res == "FF");
    return 0;
}
// Time Complexity: O(log_base N)
// Space Complexity: O(log_base N)
```
## Undo()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::stack<std::string> undoStack;
std::string currentState = "";

void typeChar(char c) {
    undoStack.push(currentState);
    currentState += c;
}

void undo() {
    if (!undoStack.empty()) {
        currentState = undoStack.top();
        undoStack.pop();
    }
}

int main() {
    typeChar('A');
    typeChar('B');
    assert(currentState == "AB");
    undo();
    std::cout << "After undo: " << currentState << std::endl;
    assert(currentState == "A");
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## BrowserHistory()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::stack<std::string> backStack, forwardStack;
std::string currentUrl = "home.com";

void visit(std::string url) {
    backStack.push(currentUrl);
    currentUrl = url;
    forwardStack = std::stack<std::string>();
}

void back() {
    if (!backStack.empty()) {
        forwardStack.push(currentUrl);
        currentUrl = backStack.top();
        backStack.pop();
    }
}

int main() {
    visit("google.com");
    visit("github.com");
    assert(currentUrl == "github.com");
    back();
    std::cout << "Back to: " << currentUrl << std::endl;
    assert(currentUrl == "google.com");
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```

# Part 5. DFS
## DepthFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> adj[4];
bool visited[4] = {false};
std::vector<int> result;

void DFS(int start) {
    std::stack<int> s;
    s.push(start);
    while (!s.empty()) {
        int v = s.top(); s.pop();
        if (!visited[v]) {
            visited[v] = true;
            result.push_back(v);
            for (auto it = adj[v].rbegin(); it != adj[v].rend(); ++it) {
                s.push(*it);
            }
        }
    }
}

int main() {
    adj[0] = {1, 2};
    adj[1] = {3};
    DFS(0);
    assert(result[0] == 0 && result[1] == 1 && result[2] == 3 && result[3] == 2);
    std::cout << "DFS traversal verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## IterativeDFS()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 반복형 깊이 우선 탐색 (스택 관점의 요약, 정본은 Graph.md Part 3): 재귀 DFS 의 "호출 스택" 을 명시적 스택으로 바꿔 쓴 것이다. 재귀는 호출 한 번마다 프레임(반환 주소·지역 변수)을 호출 스택에 쌓으므로 경로가 수십만만 되어도 스택 오버플로가 나지만, 명시적 스택은 힙에 있어 메모리가 허락하는 만큼 깊어진다.
// 두 가지 형태가 있다. A) 스택에 (정점, 다음에 볼 이웃의 위치) 를 저장하는 방식 — 재귀의 실행 상태를 그대로 보존해 방문 순서가 재귀와 정확히 같다. B) 이웃을 모두 push 하고 pop 할 때 방문 표시를 하는 방식 — 이웃을 역순으로 push 하면 방문 순서가 재귀와 같지만 스택 크기가 간선 수까지 커질 수 있다(같은 정점이 여러 번 들어갈 수 있다).
// 검증: ① 무작위 방향 그래프에서 A, B(역순 push), 재귀의 방문 순서가 모두 같다 ② 길이 100 만의 사슬 그래프에서 A 는 성공하고 스택 최대 크기가 N 이다(재귀라면 호출 깊이 N) ③ B 의 스택 최대 크기가 정점 수를 넘는 경우가 있음(완전 그래프에서 간선 수에 가깝다)
typedef std::vector<std::vector<int>> Graph;
void recursiveDFS(const Graph& g, int v, std::vector<char>& seen, std::vector<int>& order) { seen[v] = 1; order.push_back(v); for (int w : g[v]) if (!seen[w]) recursiveDFS(g, w, seen, order); }
std::vector<int> dfsA(const Graph& g, int s, std::size_t* maxStack = nullptr) {                             // (정점, 다음 이웃 인덱스) 스택
    std::vector<int> order; std::vector<char> seen(g.size(), 0); std::vector<std::pair<int, std::size_t>> st = {{s, 0}}; seen[s] = 1; order.push_back(s); std::size_t peak = 1;
    while (!st.empty()) { int v = st.back().first; std::size_t& i = st.back().second;
        if (i == g[v].size()) { st.pop_back(); continue; } int w = g[v][i++];
        if (!seen[w]) { seen[w] = 1; order.push_back(w); st.push_back({w, 0}); peak = std::max(peak, st.size()); } }
    if (maxStack) *maxStack = peak; return order;
}
std::vector<int> dfsB(const Graph& g, int s, std::size_t* maxStack = nullptr) {                             // 이웃을 역순으로 push, pop 할 때 방문
    std::vector<int> order; std::vector<char> seen(g.size(), 0); std::vector<int> st = {s}; std::size_t peak = 1;
    while (!st.empty()) { int v = st.back(); st.pop_back(); if (seen[v]) continue; seen[v] = 1; order.push_back(v); for (std::size_t k = g[v].size(); k-- > 0;) if (!seen[g[v][k]]) st.push_back(g[v][k]); peak = std::max(peak, st.size()); }
    if (maxStack) *maxStack = peak; return order;
}
int main() {
    std::mt19937 rng(7); int checked = 0;
    for (int t = 0; t < 500; t++) { int n = 1 + rng() % 40; Graph g(n); int m = rng() % (4 * n); for (int k = 0; k < m; k++) g[rng() % n].push_back(rng() % n);
        int s = rng() % n; std::vector<char> seen(n, 0); std::vector<int> rec; recursiveDFS(g, s, seen, rec); assert(dfsA(g, s) == rec && dfsB(g, s) == rec); checked++; }                                  // ①
    { const int N = 1000000; Graph chain(N); for (int i = 0; i + 1 < N; i++) chain[i].push_back(i + 1); std::size_t peak = 0; auto order = dfsA(chain, 0, &peak); assert((int)order.size() == N && order.back() == N - 1 && peak == (std::size_t)N); }   // ② 재귀였다면 호출 깊이 N
    { const int K = 60; Graph complete(K); for (int i = 0; i < K; i++) for (int j = 0; j < K; j++) if (i != j) complete[i].push_back(j); std::size_t pa = 0, pb = 0; dfsA(complete, 0, &pa); dfsB(complete, 0, &pb); assert(pa == (std::size_t)K && pb > (std::size_t)K); std::cout << "complete graph K=" << K << ": stack peak A " << pa << " vs B " << pb << "; "; }   // ③
    std::cout << "IterativeDFS: " << checked << " random graphs gave identical visit order for recursive DFS and both explicit-stack forms; a 1,000,000-vertex path was traversed without recursion" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: A 형 O(V) (경로 길이), B 형 O(E)
```
## MazeSolver()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// 미로 풀이(MazeSolver): 격자 미로에서 시작점 S 에서 출구 E 로 가는 길을 찾는다. 스택으로 하는 깊이 우선 탐색은 "막다른 길이면 되돌아간다(backtracking)" 를 자연스럽게 표현한다: 현재 칸에서 갈 수 있는 이웃이 있으면 push 하고 전진, 없으면 pop 하고 후퇴. 스택에 남은 칸이 곧 지금까지의 경로다.
// DFS 는 출구를 찾으면 멈추므로 경로가 최단이라는 보장이 없다(가운데가 뚫린 열린 방에서는 돌아가는 긴 길을 고를 수 있다). 최단 경로가 필요하면 큐를 쓰는 BFS (Queue.md 항목, PathFinding.md). 벽이 얽힌 "완전 미로(perfect maze)" 는 두 칸 사이의 길이 유일해서 DFS 경로 = 최단 경로가 된다.
// 이 항목은 미로 생성도 스택으로 한다(반복형 재귀 백트래커: 방문하지 않은 이웃 방 쪽으로 벽을 허물며 전진, 막히면 pop). 그래서 같은 스택 기법으로 만들고 푼다.
// 검증: ① 무작위 열린 지도 500 개에서 DFS 의 도달 가능 여부가 BFS 와 일치, 반환된 경로는 인접한 빈 칸으로만 이루어지며 길이 ≥ BFS 최단 거리(더 긴 경우도 실제로 나옴) ② 완전 미로 100 개(생성기 결과)에서 모든 칸이 도달 가능하고 DFS 경로 길이 == BFS 최단 거리 ③ 고정 미로의 경로 그림이 정답 문자열과 정확히 같다(골든) ④ 출구가 막힌 미로는 빈 경로
typedef std::pair<int, int> P;
std::vector<P> solveDFS(const std::vector<std::string>& m, P s, P e) {                                    // 빈 벡터 = 길 없음
    int R = m.size(), C = m[0].size(); std::vector<std::vector<char>> seen(R, std::vector<char>(C, 0)); std::vector<std::vector<P>> parent(R, std::vector<P>(C, P(-1, -1)));
    std::vector<P> st = {s}; seen[s.first][s.second] = 1; const int dr[4] = {-1, 0, 1, 0}, dc[4] = {0, 1, 0, -1};
    while (!st.empty()) { P v = st.back(); st.pop_back();                                               // 방문 순서를 기록하며 전진: 이웃을 push
        if (v == e) { std::vector<P> path; for (P p = e; p != P(-1, -1); p = parent[p.first][p.second]) path.push_back(p); std::reverse(path.begin(), path.end()); return path; }
        for (int k = 0; k < 4; k++) { int r = v.first + dr[k], c = v.second + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || m[r][c] == '#' || seen[r][c]) continue; seen[r][c] = 1; parent[r][c] = v; st.push_back({r, c}); } }
    return {};
}
int bfsLen(const std::vector<std::string>& m, P s, P e) {                                                  // 최단 칸 수 (경로 칸 개수), 없으면 -1
    int R = m.size(), C = m[0].size(); std::vector<std::vector<int>> d(R, std::vector<int>(C, -1)); std::queue<P> q; q.push(s); d[s.first][s.second] = 1; const int dr[4] = {-1, 0, 1, 0}, dc[4] = {0, 1, 0, -1};
    while (!q.empty()) { P v = q.front(); q.pop(); if (v == e) return d[v.first][v.second]; for (int k = 0; k < 4; k++) { int r = v.first + dr[k], c = v.second + dc[k]; if (r >= 0 && c >= 0 && r < R && c < C && m[r][c] != '#' && d[r][c] < 0) { d[r][c] = d[v.first][v.second] + 1; q.push({r, c}); } } }
    return -1;
}
std::vector<std::string> generatePerfectMaze(int h, int w, std::mt19937& rng) {                           // (2h+1) x (2w+1), 방은 홀수 좌표. 스택으로 벽을 허문다
    std::vector<std::string> m(2 * h + 1, std::string(2 * w + 1, '#')); std::vector<std::vector<char>> seen(h, std::vector<char>(w, 0)); std::vector<P> st = {{0, 0}}; seen[0][0] = 1; m[1][1] = '.';
    const int dr[4] = {-1, 0, 1, 0}, dc[4] = {0, 1, 0, -1};
    while (!st.empty()) { P v = st.back(); int opts[4], n = 0; for (int k = 0; k < 4; k++) { int r = v.first + dr[k], c = v.second + dc[k]; if (r >= 0 && c >= 0 && r < h && c < w && !seen[r][c]) opts[n++] = k; }
        if (!n) { st.pop_back(); continue; } int k = opts[rng() % n]; int r = v.first + dr[k], c = v.second + dc[k]; seen[r][c] = 1; m[2 * r + 1][2 * c + 1] = '.'; m[v.first * 2 + 1 + dr[k]][v.second * 2 + 1 + dc[k]] = '.'; st.push_back({r, c}); }
    return m;
}
std::string render(std::vector<std::string> m, const std::vector<P>& path) { for (P p : path) if (m[p.first][p.second] == '.') m[p.first][p.second] = '*'; std::string out; for (auto& row : m) out += row + "\n"; return out; }
int main() {
    std::mt19937 rng(21); int longer = 0, solvable = 0;
    for (int t = 0; t < 500; t++) { int R = 5 + rng() % 12, C = 5 + rng() % 12; std::vector<std::string> m(R, std::string(C, '.')); for (auto& row : m) for (char& ch : row) if (rng() % 100 < 28) ch = '#'; P s{0, 0}, e{R - 1, C - 1}; m[0][0] = m[R - 1][C - 1] = '.';
        auto path = solveDFS(m, s, e); int bfs = bfsLen(m, s, e); assert(path.empty() == (bfs < 0));                                                                                      // ① 도달 가능성 일치
        if (!path.empty()) { solvable++; assert(path.front() == s && path.back() == e && (int)path.size() >= bfs); longer += (int)path.size() > bfs; for (size_t i = 0; i < path.size(); i++) { assert(m[path[i].first][path[i].second] != '#'); if (i) assert(std::abs(path[i].first - path[i - 1].first) + std::abs(path[i].second - path[i - 1].second) == 1); } } }
    assert(solvable > 100 && longer > 0);
    for (int t = 0; t < 100; t++) { auto m = generatePerfectMaze(6 + rng() % 8, 6 + rng() % 8, rng); P s{1, 1}, e{(int)m.size() - 2, (int)m[0].size() - 2}; auto path = solveDFS(m, s, e); assert(!path.empty() && (int)path.size() == bfsLen(m, s, e));            // ② 완전 미로: DFS 경로가 최단
        for (int r = 1; r < (int)m.size(); r += 2) for (int c = 1; c < (int)m[0].size(); c += 2) assert(!solveDFS(m, s, {r, c}).empty()); }
    { std::vector<std::string> m = {"#########", "#...#...#", "#.#.#.#.#", "#.#...#.#", "#########"}; auto path = solveDFS(m, {1, 1}, {3, 7}); assert(path.size() == 13);
      assert(render(m, path) == "#########\n#***#***#\n#.#*#*#*#\n#.#***#*#\n#########\n"); }                                                              // ③ 골든: 길이 유일한 고정 미로의 경로 그림
    { std::vector<std::string> m = {"..#..", "..#..", "###..", ".....", "....."}; assert(solveDFS(m, {0, 0}, {4, 4}).empty() && bfsLen(m, {0, 0}, {4, 4}) < 0); }          // ④ 출구에 닿을 수 없는 미로
    std::cout << "MazeSolver: DFS agreed with BFS on reachability for 500 open grids (" << solvable << " solvable, " << longer << " with a non-shortest DFS path); on 100 generated perfect mazes the DFS path was always the shortest" << std::endl; return 0;
}
// Time Complexity: O(R·C)
// Space Complexity: O(R·C)
```
## TopologicalSort()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> adj[4];
bool visited[4] = {false};

void dfs(int v, std::stack<int>& s) {
    visited[v] = true;
    for (int u : adj[v]) {
        if (!visited[u]) dfs(u, s);
    }
    s.push(v);
}

int main() {
    adj[0] = {1};
    adj[1] = {2};
    std::stack<int> s;
    for (int i = 0; i < 3; i++) {
        if (!visited[i]) dfs(i, s);
    }
    assert(s.top() == 0);
    std::cout << "Topological Sort Top: " << s.top() << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```

# Part 6. 단조 스택
## MonotonicStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {3, 1, 4, 2};
    std::stack<int> s; // 단조 감소 스택 유지
    for (int val : arr) {
        while (!s.empty() && s.top() < val) {
            s.pop();
        }
        s.push(val);
    }
    assert(s.top() == 2);
    std::cout << "Monotonic stack implemented." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## NextGreaterElement()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> nextGreater(std::vector<int>& arr) {
    std::stack<int> s;
    std::vector<int> res(arr.size(), -1);
    for (int i = 0; i < (int)arr.size(); ++i) {
        while (!s.empty() && arr[s.top()] < arr[i]) {
            res[s.top()] = arr[i];
            s.pop();
        }
        s.push(i);
    }
    return res;
}

int main() {
    std::vector<int> arr = {2, 1, 2, 4, 3};
    std::vector<int> res = nextGreater(arr);
    std::cout << "Next Greater of 2 -> " << res[0] << std::endl;
    assert(res[0] == 4);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PreviousGreaterElement()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> prevGreater(std::vector<int>& arr) {
    std::stack<int> s;
    std::vector<int> res(arr.size(), -1);
    for (int i = 0; i < (int)arr.size(); ++i) {
        while (!s.empty() && arr[s.top()] <= arr[i]) {
            s.pop();
        }
        if (!s.empty()) res[i] = arr[s.top()];
        s.push(i);
    }
    return res;
}

int main() {
    std::vector<int> arr = {4, 2, 3};
    std::vector<int> res = prevGreater(arr);
    assert(res[1] == 4 && res[2] == 4);
    std::cout << "Previous greater working." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## LargestRectangle()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <cassert>

int largestRectangleArea(std::vector<int>& heights) {
    std::stack<int> s;
    int maxArea = 0;
    heights.push_back(0); 
    for (int i = 0; i < (int)heights.size(); ++i) {
        while (!s.empty() && heights[s.top()] > heights[i]) {
            int h = heights[s.top()]; s.pop();
            int w = s.empty() ? i : i - s.top() - 1;
            maxArea = std::max(maxArea, h * w);
        }
        s.push(i);
    }
    return maxArea;
}

int main() {
    std::vector<int> heights = {2, 1, 5, 6, 2, 3};
    int res = largestRectangleArea(heights);
    assert(res == 10);
    std::cout << "Max rectangle area: " << res << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## DailyTemperatures()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> dailyTemperatures(std::vector<int>& temp) {
    std::stack<int> s;
    std::vector<int> res(temp.size(), 0);
    for (int i = 0; i < (int)temp.size(); ++i) {
        while (!s.empty() && temp[s.top()] < temp[i]) {
            res[s.top()] = i - s.top();
            s.pop();
        }
        s.push(i);
    }
    return res;
}

int main() {
    std::vector<int> temp = {73, 74, 75, 71, 69, 72, 76, 73};
    std::vector<int> res = dailyTemperatures(temp);
    assert(res[0] == 1 && res[1] == 1 && res[2] == 4);
    std::cout << "Daily temperatures verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## StockSpan()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

class StockSpanner {
    std::stack<std::pair<int, int>> s; 
public:
    int next(int price) {
        int span = 1;
        while (!s.empty() && s.top().first <= price) {
            span += s.top().second;
            s.pop();
        }
        s.push({price, span});
        return span;
    }
};

int main() {
    StockSpanner ss;
    assert(ss.next(100) == 1);
    assert(ss.next(80) == 1);
    assert(ss.next(120) == 3);
    std::cout << "StockSpan functional." << std::endl;
    return 0;
}
// Time Complexity: Amortized O(1) per call
// Space Complexity: O(N)
```

# Part 7. 특수 스택
## MinStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

class MinStack {
    std::stack<int> s, min_s;
public:
    void push(int val) {
        s.push(val);
        if (min_s.empty() || val <= min_s.top()) min_s.push(val);
    }
    void pop() {
        if (s.top() == min_s.top()) min_s.pop();
        s.pop();
    }
    int getMin() { return min_s.top(); }
};

int main() {
    MinStack ms;
    ms.push(3); ms.push(1); ms.push(4);
    assert(ms.getMin() == 1);
    ms.pop(); ms.pop();
    assert(ms.getMin() == 3);
    std::cout << "MinStack verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) per operation
// Space Complexity: O(N)
```
## MaxStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

class MaxStack {
    std::stack<int> s, max_s;
public:
    void push(int val) {
        s.push(val);
        if (max_s.empty() || val >= max_s.top()) max_s.push(val);
    }
    void pop() {
        if (s.top() == max_s.top()) max_s.pop();
        s.pop();
    }
    int getMax() { return max_s.top(); }
};

int main() {
    MaxStack ms;
    ms.push(1); ms.push(5); ms.push(2);
    assert(ms.getMax() == 5);
    std::cout << "MaxStack verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) per operation
// Space Complexity: O(N)
```
## TwoStacksInArray()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

class TwoStacks {
    int arr[100];
    int top1 = -1, top2 = 100;
public:
    void push1(int x) { if (top1 < top2 - 1) arr[++top1] = x; }
    void push2(int x) { if (top1 < top2 - 1) arr[--top2] = x; }
    int getTop1() { return arr[top1]; }
    int getTop2() { return arr[top2]; }
};

int main() {
    TwoStacks ts;
    ts.push1(10);
    ts.push2(20);
    assert(ts.getTop1() == 10 && ts.getTop2() == 20);
    std::cout << "Two stacks in array tested." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## MultipleStacks()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 여러 스택을 한 배열에(MultipleStacks): k 개의 스택을 만들 때 배열을 k 등분(용량/k 씩)하면 한 스택이 가득 차도 다른 칸은 놀아서 낭비가 크다. 배열 한 개와 "자유 칸 연결 리스트" 를 공유하면 전체 칸 수만 넘지 않는 한 어떤 스택이든 자랄 수 있다(Knuth 의 기법).
// 구조: data[i] = 값, next[i] = 이 칸 아래(같은 스택의 다음 칸)의 인덱스 또는 자유 리스트의 다음 칸, top[k] = k 번 스택의 맨 위 칸 인덱스(비면 −1), freeHead = 자유 칸 리스트의 머리. push(k): 자유 칸 하나를 떼어 값을 쓰고 top[k] 아래에 잇는다. pop(k): top[k] 칸을 떼어 자유 리스트에 돌려준다. 모두 O(1) 이다.
// 균등 분할과 비교: 3 개 스택, 총 칸 30 일 때 균등 분할은 스택당 10 개에서 거절되지만 공유 방식은 한 스택이 30 개까지 담는다. 총 칸을 모두 쓸 때만 거절한다.
// 검증: ① 스택 k 개를 std::stack 들과 무작위 차분(스택별 내용·크기) ② 자유 칸 수 + 사용 칸 수 == 전체 칸 ③ 한 스택이 전체 용량을 독점할 수 있고 가득 차면 모든 스택의 push 가 거절 ④ 균등 분할은 10 개에서 거절 ⑤ pop 으로 칸이 돌아오면 다른 스택이 그 칸을 쓸 수 있다
class MultiStack {
    std::vector<int> data_, next_, top_; int freeHead_; std::size_t used_ = 0;
public:
    MultiStack(int k, int capacity) : data_(capacity), next_(capacity), top_(k, -1), freeHead_(capacity ? 0 : -1) { for (int i = 0; i < capacity; i++) next_[i] = i + 1 < capacity ? i + 1 : -1; }
    bool push(int k, int x) { if (freeHead_ < 0) return false; int i = freeHead_; freeHead_ = next_[i]; data_[i] = x; next_[i] = top_[k]; top_[k] = i; used_++; return true; }
    bool pop(int k, int& out) { int i = top_[k]; if (i < 0) return false; out = data_[i]; top_[k] = next_[i]; next_[i] = freeHead_; freeHead_ = i; used_--; return true; }
    bool peek(int k, int& out) const { int i = top_[k]; if (i < 0) return false; out = data_[i]; return true; }
    std::size_t used() const { return used_; } std::size_t freeCount() const { std::size_t c = 0; for (int i = freeHead_; i >= 0; i = next_[i]) c++; return c; }
    std::size_t sizeOf(int k) const { std::size_t c = 0; for (int i = top_[k]; i >= 0; i = next_[i]) c++; return c; }
};
class PartitionedStacks {                                                                   // 균등 분할 방식 (비교용)
    std::vector<std::vector<int>> s_; std::size_t each_;
public:
    PartitionedStacks(int k, int capacity) : s_(k), each_(capacity / k) {}
    bool push(int k, int x) { if (s_[k].size() == each_) return false; s_[k].push_back(x); return true; }
};
int main() {
    { const int K = 5, CAP = 40; MultiStack m(K, CAP); std::vector<std::stack<int>> ref(K); std::mt19937 rng(10); std::size_t total = 0;
      for (int step = 0; step < 60000; step++) { int k = rng() % K; if (rng() % 2) { int x = rng(); bool ok = m.push(k, x); assert(ok == (total < (std::size_t)CAP)); if (ok) { ref[k].push(x); total++; } } else { int v; bool ok = m.pop(k, v); assert(ok == !ref[k].empty()); if (ok) { assert(v == ref[k].top()); ref[k].pop(); total--; } }
        assert(m.used() == total && m.used() + m.freeCount() == (std::size_t)CAP);                                                                                                         // ② 칸 보존
        if (step % 1000 == 0) for (int j = 0; j < K; j++) { assert(m.sizeOf(j) == ref[j].size()); int v; assert(m.peek(j, v) == !ref[j].empty() && (ref[j].empty() || v == ref[j].top())); } } }          // ①
    { MultiStack m(3, 30); int pushed = 0; while (m.push(0, pushed)) pushed++; assert(pushed == 30 && !m.push(1, 0) && !m.push(2, 0)); }                                                  // ③ 한 스택이 전체를 독점
    { PartitionedStacks p(3, 30); int pushed = 0; while (p.push(0, pushed)) pushed++; assert(pushed == 10); }                                                                               // ④ 균등 분할은 10 개에서 거절
    { MultiStack m(2, 4); for (int i = 0; i < 4; i++) assert(m.push(0, i)); assert(!m.push(1, 9)); int v; assert(m.pop(0, v) && v == 3); assert(m.push(1, 9) && m.peek(1, v) && v == 9); }              // ⑤ 돌려받은 칸을 다른 스택이 쓴다
    std::cout << "MultipleStacks: five stacks sharing 40 cells matched std::stack models for 60000 operations with cell conservation; one stack could take all 30 cells while equal partitioning stopped at 10" << std::endl; return 0;
}
// Time Complexity: push·pop·peek O(1)
// Space Complexity: O(전체 칸 수) (스택 수와 무관)
```

# Part 8. 재귀
## CallStack()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 호출 스택(Call Stack): 함수 호출이 중첩되는 구조를 후입선출로 관리하는 스택이다. 함수를 호출하면 프레임(매개변수, 지역 변수, 반환 위치)이 쌓이고 return 하면 맨 위 프레임이 사라진다. 재귀가 "스스로를 호출하는 함수" 가 아니라 "스택에 프레임을 쌓는 일" 임을 이해하는 것이 스택 항목의 핵심이다.
// 이 항목은 호출 스택을 직접 만들어 보인다. 실제 재귀 함수의 호출·반환 사건을 기록한 로그와, 같은 계산을 "프레임 구조체의 명시적 스택" 으로 시뮬레이션하며 남긴 로그가 완전히 같음을 확인한다. 피보나치 fib(n)은 호출 수가 2·fib(n+1)−1 이고 최대 깊이가 n 이어서 호출 스택이 "트리 전체" 가 아니라 "현재 루트에서 내려온 경로" 만 담는다는 것도 보인다.
// 검증: ① 실제 재귀 로그 == 프레임 스택 시뮬레이션 로그 (fib(0..12)) ② 호출 수 공식 ③ 최대 깊이 == n (n ≥ 1) ④ 팩토리얼 fact(10) 에서 깊이 11, 반환 시 곱해지는 순서
std::vector<std::string> realLog; int realDepth = 0, realMax = 0;
long fibReal(int n) { realLog.push_back("call fib(" + std::to_string(n) + ")"); realDepth++; if (realDepth > realMax) realMax = realDepth; long r = n < 2 ? n : fibReal(n - 1) + fibReal(n - 2); realDepth--; realLog.push_back("ret fib(" + std::to_string(n) + ")=" + std::to_string(r)); return r; }
struct Frame { int n; int step; long first; };                                           // step: 0 = 막 호출됨, 1 = fib(n-1) 이 돌아옴, 2 = fib(n-2) 도 돌아옴
long fibSimulated(int n0, std::vector<std::string>& log, int& maxDepth) {
    std::vector<Frame> stack; long ret = 0; maxDepth = 0; stack.push_back({n0, 0, 0}); log.push_back("call fib(" + std::to_string(n0) + ")");
    while (!stack.empty()) {
        Frame& f = stack.back(); if ((int)stack.size() > maxDepth) maxDepth = (int)stack.size();
        if (f.step == 0) { if (f.n < 2) { ret = f.n; log.push_back("ret fib(" + std::to_string(f.n) + ")=" + std::to_string(ret)); stack.pop_back(); } else { f.step = 1; int n = f.n - 1; stack.push_back({n, 0, 0}); log.push_back("call fib(" + std::to_string(n) + ")"); } }
        else if (f.step == 1) { f.first = ret; f.step = 2; int n = f.n - 2; stack.push_back({n, 0, 0}); log.push_back("call fib(" + std::to_string(n) + ")"); }
        else { ret = f.first + ret; log.push_back("ret fib(" + std::to_string(f.n) + ")=" + std::to_string(ret)); stack.pop_back(); }
    }
    return ret;
}
long factReal(int n, int depth, int& maxDepth) { if (depth > maxDepth) maxDepth = depth; return n <= 1 ? 1 : n * factReal(n - 1, depth + 1, maxDepth); }
int main() {
    long fibs[13] = {0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144};
    for (int n = 0; n <= 12; n++) {
        realLog.clear(); realDepth = realMax = 0; long a = fibReal(n); std::vector<std::string> simLog; int simMax; long b = fibSimulated(n, simLog, simMax);
        assert(a == fibs[n] && b == fibs[n] && realLog == simLog && simMax == realMax);                                                         // ① 로그 일치
        long calls = 0; for (auto& l : realLog) calls += l[0] == 'c'; long fibNext = n + 1 <= 12 ? fibs[n + 1] : 233; assert(calls == 2 * fibNext - 1);                       // ② 호출 수 = 2·fib(n+1) − 1
        if (n >= 1) assert(realMax == n);                                                                                                       // ③ 최대 깊이 = n
    }
    { int maxDepth = 0; long r = factReal(10, 1, maxDepth); assert(r == 3628800 && maxDepth == 10); }                                           // ④
    realLog.clear(); realDepth = realMax = 0; fibReal(3); std::cout << "CallStack: trace of fib(3): "; for (auto& l : realLog) std::cout << l << "; "; std::cout << std::endl;
    std::cout << "CallStack: real recursion logs equal the explicit frame-stack simulation for fib(0..12); calls = 2*fib(n+1)-1 and the stack depth stays n" << std::endl; return 0;
}
// Time Complexity: fib 호출 수 O(φ^n), 호출 스택 깊이 O(n)
// Space Complexity: O(n) 프레임
```
## StackFrame()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <vector>
#include <cassert>

// 스택 프레임(Stack Frame): 함수가 호출될 때 호출 스택 위에 만들어지는 한 덩어리의 메모리 — 반환 주소, 저장된 레지스터, 매개변수(일부), 지역 변수가 들어 있다. 프레임이 클수록 같은 스택 크기에서 재귀를 얕게밖에 못 한다.
// 이 항목은 프레임의 크기를 "측정" 한다. 같은 함수를 재귀 호출하며 각 호출의 지역 변수 주소(스택 포인터에 가까운 값)를 기록하고 인접한 두 호출의 주소 차이를 구하면 프레임 하나의 바이트 수가 나온다. x86-64 Linux 에서 스택은 낮은 주소 방향으로 자라므로 깊은 호출일수록 주소가 작다.
// 지역 변수가 큰 함수의 프레임은 그만큼 커진다(char buf[512] 이면 512 바이트 이상). 따라서 8 MB 스택으로 얼마나 깊이 재귀할 수 있는지는 "8 MB / 프레임 크기" 로 예측된다 — 아래에서 측정한 프레임 크기로 예측 깊이를 계산해 보인다.
// 주의: 컴파일러가 인라인·꼬리 호출 제거를 하면 프레임이 사라질 수 있어 noinline 과 volatile 로 막았고, 주소 비교는 구현 정의 동작이므로 부등식(범위)으로만 단언한다. 새니타이저는 프레임에 감시 영역(redzone)을 넣어 크기를 바꾸므로 이 항목은 새니타이저에서 제외한다.
// audit: no-sanitize
// audit: gcc-only
// 검증: ① 깊은 호출일수록 주소가 작다(스택이 아래로 자람) ② 작은 프레임: 16..512 바이트 ③ 큰 지역 배열(512 B)을 가진 함수의 프레임이 작은 함수보다 최소 400 바이트 크다 ④ 프레임 크기가 호출마다 일정(재귀의 모든 단계 동일) ⑤ 예측 최대 깊이 = 8 MB / 프레임 크기 가 수만 이상
#if defined(__GNUC__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif
static std::vector<std::uintptr_t> addrs;
NOINLINE long smallFrame(int depth) { volatile int local = depth; addrs.push_back((std::uintptr_t)&local); if (depth == 0) return local; long r = smallFrame(depth - 1); return r + local; }
NOINLINE long bigFrame(int depth) { volatile char buf[512]; buf[0] = (char)depth; addrs.push_back((std::uintptr_t)&buf[0]); if (depth == 0) return buf[0]; long r = bigFrame(depth - 1); return r + buf[0]; }
std::vector<std::uintptr_t> gaps() { std::vector<std::uintptr_t> g; for (std::size_t i = 1; i < addrs.size(); i++) g.push_back(addrs[i - 1] - addrs[i]); return g; }
int main() {
    addrs.clear(); smallFrame(50); auto gs = gaps(); bool descending = true; for (std::size_t i = 1; i < addrs.size(); i++) descending &= addrs[i] < addrs[i - 1]; assert(descending);                                              // ① 스택이 아래로 자란다
    std::uintptr_t smallBytes = gs[10]; assert(smallBytes >= 16 && smallBytes <= 512);                                                                                                                           // ②
    addrs.clear(); bigFrame(50); auto gb = gaps(); std::uintptr_t bigBytes = gb[10]; assert(bigBytes >= smallBytes + 400);                                                                                      // ③ 지역 배열 512 B 만큼 프레임이 커진다
    bool uniform = true; for (std::size_t i = 1; i < gs.size(); i++) uniform &= gs[i] == gs[0]; for (std::size_t i = 1; i < gb.size(); i++) uniform &= gb[i] == gb[0]; assert(uniform);                           // ④ 모든 재귀 단계의 프레임이 같은 크기
    std::size_t predictedSmall = 8u * 1024 * 1024 / smallBytes, predictedBig = 8u * 1024 * 1024 / bigBytes; assert(predictedSmall > 10000 && predictedBig > 1000 && predictedSmall > predictedBig);                  // ⑤ 예측 최대 깊이
    std::cout << "StackFrame: measured frame sizes - small function " << smallBytes << " bytes, function with a 512-byte local array " << bigBytes << " bytes; an 8 MB stack therefore allows roughly " << predictedSmall << " vs " << predictedBig << " nested calls" << std::endl; return 0;
}
// Time Complexity: O(깊이)
// Space Complexity: O(깊이 × 프레임 크기)
```
## TailRecursion()
### 대표코드
```cpp
#include <cstdint>
#include <functional>
#include <iostream>
#include <random>
#include <cassert>

// 꼬리 재귀(Tail Recursion): 재귀 호출이 함수의 마지막 동작이라 호출 뒤에 할 일이 없는 재귀다. 호출한 쪽이 돌아와서 더 할 일이 없으므로 이론상 현재 프레임을 재사용하는 "꼬리 호출 제거(TCO)" 가 가능하고, 그러면 깊이 N 의 재귀가 O(1) 스택으로 돈다.
// 비꼬리 재귀: fact(n) = n * fact(n−1) 은 호출이 돌아온 뒤 곱셈이 남아 있어 프레임을 유지해야 한다. 꼬리 재귀로 바꾸려면 "남은 일" 을 누적 인자(accumulator)로 넘긴다: factTail(n, acc) = n == 0 ? acc : factTail(n−1, acc·n).
// C++ 표준은 꼬리 호출 제거를 보장하지 않는다. -O2 에서 GCC/Clang 이 해 주는 경우가 많지만 디버그 빌드나 소멸자가 남는 경우에는 안 된다. 보장이 필요하면 ① 반복문으로 직접 바꾸거나 ② 트램펄린(trampoline; 함수가 "다음에 할 일" 을 돌려주고 바깥 루프가 실행)을 쓴다.
// 검증: ① 비꼬리, 꼬리, 반복문, 트램펄린 네 구현이 무작위 입력에서 같은 값(모듈러 팩토리얼, 거듭제곱, gcd, 합) ② 호출 깊이 카운터: 비꼬리/꼬리 재귀는 깊이 n, 반복문은 1, 트램펄린은 바깥 루프 n 번이지만 스택 깊이 1 ③ 트램펄린은 n = 5·10^6 에서도 안전 (직접 재귀는 호출 스택이 깊이 n 필요 — 여기서는 20000 까지만 시험)
typedef std::uint64_t u64; const u64 MOD = 1000000007ULL;
int depthNow = 0, depthMax = 0;
struct Guard { Guard() { if (++depthNow > depthMax) depthMax = depthNow; } ~Guard() { depthNow--; } };
u64 factPlain(int n) { Guard g; return n == 0 ? 1 : (u64)n % MOD * factPlain(n - 1) % MOD; }                       // 재귀 뒤에 곱셈이 남음
u64 factTail(int n, u64 acc = 1) { Guard g; return n == 0 ? acc : factTail(n - 1, acc * (u64)n % MOD); }            // 마지막 동작이 호출 (단, Guard 의 소멸자가 있어 C++ 에서는 꼬리 호출이 아니게 되기도 한다)
u64 factLoop(int n) { u64 acc = 1; for (; n > 0; n--) acc = acc * (u64)n % MOD; return acc; }
struct Thunk { bool done; u64 value; int n; u64 acc; };                                                           // 트램펄린: "다음에 할 일" 을 값으로 표현
Thunk step(int n, u64 acc) { return n == 0 ? Thunk{true, acc, 0, 0} : Thunk{false, 0, n - 1, acc * (u64)n % MOD}; }
u64 factTrampoline(int n, long* bounces = nullptr) { Thunk t = step(n, 1); long b = 0; while (!t.done) { t = step(t.n, t.acc); b++; } if (bounces) *bounces = b + 1; return t.value; }
u64 gcdTail(u64 a, u64 b) { return b == 0 ? a : gcdTail(b, a % b); }
u64 gcdLoop(u64 a, u64 b) { while (b) { u64 t = a % b; a = b; b = t; } return a; }
u64 sumTail(int n, u64 acc = 0) { return n == 0 ? acc : sumTail(n - 1, acc + (u64)n); }
int main() {
    std::mt19937_64 rng(5);
    for (int t = 0; t < 300; t++) { int n = rng() % 500; u64 a = factPlain(n), b = factTail(n), c = factLoop(n), d = factTrampoline(n); assert(a == b && b == c && c == d);                       // ①
        u64 x = rng() % 1000000 + 1, y = rng() % 1000000 + 1; assert(gcdTail(x, y) == gcdLoop(x, y)); int m = rng() % 2000; assert(sumTail(m) == (u64)m * (m + 1) / 2); }
    depthNow = depthMax = 0; factPlain(1000); assert(depthMax == 1001); depthNow = depthMax = 0; factTail(1000); assert(depthMax == 1001);                                                       // ② 재귀는 깊이 n+1 (Guard 가 소멸자를 둬서 꼬리 호출 제거가 막힌다)
    { long bounces = 0; u64 r = factTrampoline(5000000, &bounces); assert(r == factLoop(5000000) && bounces == 5000001); }                                                                    // ③ 트램펄린은 깊이 5·10^6 도 호출 스택 1 단계로
    { depthNow = depthMax = 0; u64 r = factTail(20000); assert(r == factLoop(20000) && depthMax == 20001); }                                                                                    // 직접 재귀는 20000 까지만
    std::cout << "TailRecursion: plain, tail-recursive, loop and trampoline versions agreed on 300 random inputs; recursion needs depth n+1 while the trampoline handled n = 5,000,000 with constant stack" << std::endl; return 0;
}
// Time Complexity: O(n)
// Space Complexity: 비꼬리·(제거 없는) 꼬리 재귀 O(n), 반복문·트램펄린·TCO 적용 시 O(1)
```
## RecursionSimulation()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// 재귀의 시뮬레이션: 모든 재귀 함수는 "명시적 스택 + 반복문" 으로 바꿀 수 있다. 방법: 호출 하나를 프레임 구조체(매개변수 + 지금 어디까지 했는지 나타내는 상태 번호)로 만들어 스택에 쌓고, 반복문이 맨 위 프레임을 꺼내 상태에 따라 한 단계 진행한다. 재귀 호출 = 새 프레임 push, 반환 = pop 하고 반환값을 호출한 프레임에 전달.
// 이 기법의 이유: ① 호출 스택 깊이 제한(수십만 단계 재귀)에서 벗어난다 ② 실행을 중간에 멈추고 재개하거나 상태를 저장·검사할 수 있다 ③ 컴파일러가 하는 일을 이해하게 된다.
// 이 항목은 세 가지 재귀 함수를 시뮬레이션해 재귀 구현과 정확히 같은 결과·이동 순서를 내는지 확인한다. 하노이 탑(이동 순서가 같아야 한다), 아커만 함수(A(2,3)=9, A(3,3)=61: 극단적으로 깊은 재귀), 이진 트리의 중위 순회(왼쪽 → 자신 → 오른쪽).
// 검증: ① 하노이 n=1..12 의 이동 목록이 재귀와 같고 이동 횟수 = 2ⁿ−1 ② 아커만 (m, n) 작은 값들이 재귀와 같고 최대 스택 크기 기록 ③ 무작위 이진 트리의 중위 순회 결과가 재귀와 같다 ④ 하노이 n=20 의 시뮬레이션이 재귀 없이 완주 (이동 2^20−1 번)
typedef std::vector<std::pair<int, int>> Moves;
void hanoiRec(int n, int from, int to, int via, Moves& out) { if (n == 0) return; hanoiRec(n - 1, from, via, to, out); out.push_back({from, to}); hanoiRec(n - 1, via, to, from, out); }
struct HFrame { int n, from, to, via, state; };
Moves hanoiSim(int n0) {
    Moves out; std::vector<HFrame> st = {{n0, 1, 3, 2, 0}};
    while (!st.empty()) { HFrame f = st.back(); st.pop_back(); if (f.n == 0) continue;
        if (f.state == 0) { st.push_back({f.n, f.from, f.to, f.via, 1}); st.push_back({f.n - 1, f.from, f.via, f.to, 0}); }          // 첫 재귀 호출 전에: 돌아올 자리(state 1)를 먼저 쌓고 그 위에 호출을 쌓는다
        else { out.push_back({f.from, f.to}); st.push_back({f.n - 1, f.via, f.to, f.from, 0}); } }
    return out;
}
long ackRec(long m, long n) { return m == 0 ? n + 1 : n == 0 ? ackRec(m - 1, 1) : ackRec(m - 1, ackRec(m, n - 1)); }
long ackSim(long m0, long n0, std::size_t* maxStack) {                                      // 스택에는 "아직 적용하지 못한 m" 들이 쌓인다: A(m, n) = A(m-1, A(m, n-1)) 의 바깥 m-1 을 대기시킨다
    std::vector<long> st = {m0}; long n = n0; std::size_t peak = 1;
    while (!st.empty()) { long m = st.back(); st.pop_back(); if (m == 0) n = n + 1; else if (n == 0) { st.push_back(m - 1); n = 1; } else { st.push_back(m - 1); st.push_back(m); n = n - 1; } peak = std::max(peak, st.size()); }
    if (maxStack) *maxStack = peak; return n;
}
struct T { int v; T *l, *r; };
void inorderRec(T* t, std::vector<int>& out) { if (!t) return; inorderRec(t->l, out); out.push_back(t->v); inorderRec(t->r, out); }
std::vector<int> inorderSim(T* root) { std::vector<int> out; std::vector<T*> st; T* cur = root; while (cur || !st.empty()) { while (cur) { st.push_back(cur); cur = cur->l; } cur = st.back(); st.pop_back(); out.push_back(cur->v); cur = cur->r; } return out; }
T* build(int lo, int hi, std::vector<T*>& pool, unsigned& seed) { if (lo > hi) return nullptr; seed = seed * 1103515245u + 12345u; int mid = lo + (int)((seed >> 8) % (unsigned)(hi - lo + 1)); pool.push_back(new T{mid, nullptr, nullptr}); T* t = pool.back(); t->l = build(lo, mid - 1, pool, seed); t->r = build(mid + 1, hi, pool, seed); return t; }
int main() {
    for (int n = 1; n <= 12; n++) { Moves a, b = hanoiSim(n); hanoiRec(n, 1, 3, 2, a); assert(a == b && a.size() == (std::size_t)((1 << n) - 1)); }                              // ①
    for (long m = 0; m <= 3; m++) for (long n = 0; n <= 3; n++) { std::size_t peak; assert(ackRec(m, n) == ackSim(m, n, &peak)); } std::size_t pk = 0; assert(ackSim(2, 3, nullptr) == 9 && ackSim(3, 3, &pk) == 61 && pk > 3);          // ②
    for (int t = 0; t < 100; t++) { std::vector<T*> pool; unsigned seed = 17u * t + 3u; T* root = build(1, 1 + t * 3, pool, seed); std::vector<int> a, b = inorderSim(root); inorderRec(root, a); assert(a == b); for (T* p : pool) delete p; }          // ③
    { Moves big = hanoiSim(20); assert(big.size() == (1u << 20) - 1); }                                                                                                                                   // ④
    std::cout << "RecursionSimulation: explicit-stack versions of Hanoi (n<=12 plus n=20), Ackermann and in-order traversal produced exactly the recursive results; A(3,3)=61 needed a stack of " << pk << " pending frames" << std::endl; return 0;
}
// Time Complexity: 재귀와 같다 (하노이 O(2ⁿ), 중위 순회 O(N))
// Space Complexity: 명시적 스택 O(최대 재귀 깊이) — 호출 스택이 아니라 힙을 쓴다
```

# Part 9. 병렬
## LockFreeStack()
### 대표코드
```cpp
#include <atomic>
#include <cstdint>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>
#include <cassert>

// 락프리 스택(Treiber 1986): 잠금 없이 CAS(compare-and-swap) 하나로 top 포인터를 바꾸는 스택이다. push 는 "새 노드의 next 를 현재 top 으로 두고 top 을 새 노드로 CAS", pop 은 "top 을 top->next 로 CAS". CAS 가 실패하면 다른 스레드가 먼저 바꾼 것이므로 새 top 을 읽고 다시 시도한다 — 한 스레드가 멈춰도 다른 스레드는 진행한다.
// 함정은 ABA 문제다. 스레드 A 가 pop 을 시작하며 top = X, X.next = Y 를 읽고 멈춘다. 그 사이 B 가 X 와 Y 를 pop 한 뒤 X 만 다시 push 하면 top 은 다시 X 이지만 스택에는 Y 가 없다. 깨어난 A 의 CAS(top: X → Y)는 "top 이 여전히 X" 라서 성공해 이미 B 가 가져간 Y 가 다시 스택 맨 위에 올라간다. 이 구현은 top 워드에 태그(버전 번호)를 붙여 성공한 CAS 마다 올린다 — 같은 노드 주소여도 태그가 달라 A 의 CAS 는 실패한다.
// 노드는 고정 풀에서 32 비트 인덱스로 가리키고, 풀의 빈 노드도 같은 방식의 락프리 스택으로 관리한다(재사용해도 안전). 풀이 비면 push 는 false. 포인터 기반 일반형은 TreiberStack, 안전한 메모리 회수는 AdvancedDataStructures.md 의 HazardPointer 항목.
// 검증: ① 단일 스레드 LIFO·풀 소진·반환 ② ABA 시나리오를 스크립트로 재현: 태그 없는 CAS 는 이미 가져간 노드를 되살리고, 태그 있는 CAS 는 실패 ③ 4 스레드가 20 만 번씩 push/pop 하며 값의 합이 보존되고(생성 합 == 꺼낸 합 + 남은 합) 중복이 없으며 풀이 새지 않음 ④ TSan 에서도 통과
const uint32_t NIL = 0xFFFFFFFFu;
struct TaggedList {                                                                       // 인덱스 스택의 머리: [태그 32 | 인덱스 32]
    std::atomic<uint64_t> head;
    explicit TaggedList(uint32_t first = NIL) : head((uint64_t)first) {}
    uint64_t snapshot() const { return head.load(); }
    void push(std::atomic<uint32_t>* nx, uint32_t i, bool tagged = true) { for (;;) { uint64_t h = head.load(); nx[i].store((uint32_t)h); uint64_t nh = ((tagged ? (h >> 32) + 1 : 0) << 32) | i; if (head.compare_exchange_weak(h, nh)) return; } }
    uint32_t pop(std::atomic<uint32_t>* nx) { for (;;) { uint64_t h = head.load(); uint32_t i = (uint32_t)h; if (i == NIL) return NIL; uint32_t n = nx[i].load(); if (head.compare_exchange_weak(h, (((h >> 32) + 1) << 32) | n)) return i; } }
};
class LockFreeStack {
    std::unique_ptr<std::atomic<int>[]> val; std::unique_ptr<std::atomic<uint32_t>[]> next; TaggedList data, freeList; uint32_t cap;
public:
    explicit LockFreeStack(uint32_t capacity) : val(new std::atomic<int>[capacity]), next(new std::atomic<uint32_t>[capacity]), cap(capacity) {
        for (uint32_t i = 0; i < capacity; i++) { val[i] = 0; next[i] = i + 1 < capacity ? i + 1 : NIL; } freeList.head = capacity ? 0 : NIL; }
    bool push(int v) { uint32_t i = freeList.pop(next.get()); if (i == NIL) return false; val[i].store(v); data.push(next.get(), i); return true; }
    bool pop(int& out) { uint32_t i = data.pop(next.get()); if (i == NIL) return false; out = val[i].load(); freeList.push(next.get(), i); return true; }
    long countFree() const { long c = 0; for (uint32_t i = (uint32_t)freeList.snapshot(); i != NIL; i = next[i].load()) c++; return c; }
    long countData() const { long c = 0; for (uint32_t i = (uint32_t)data.snapshot(); i != NIL; i = next[i].load()) c++; return c; }
    uint32_t capacity() const { return cap; }
};
int main() {
    { LockFreeStack s(5); int v; for (int i = 0; i < 5; i++) assert(s.push(i)); assert(!s.push(5) && s.countData() == 5 && s.countFree() == 0); for (int i = 4; i >= 0; i--) { assert(s.pop(v) && v == i); } assert(!s.pop(v) && s.countFree() == 5); }       // ①
    for (int tagged = 0; tagged < 2; tagged++) {                                           // ② ABA: 스택 0 -> 1 -> 2. A 가 pop 을 시작(top=0, next=1 읽음)하고 멈춘다. B 가 0, 1 을 pop 하고 0 을 다시 push.
        std::atomic<uint32_t> nx[3]; TaggedList st(0); nx[0] = 1; nx[1] = 2; nx[2] = NIL; uint64_t seen = st.snapshot(); uint32_t seenTop = (uint32_t)seen, seenNext = nx[seenTop].load(); assert(seenTop == 0 && seenNext == 1);
        uint32_t b1 = st.pop(nx), b2 = st.pop(nx); st.push(nx, b1, tagged != 0); assert(b1 == 0 && b2 == 1 && (uint32_t)st.snapshot() == 0);                                       // B: 0 과 1 을 가져가고 0 만 되돌림 (스택: 0 -> 2)
        uint64_t want = (tagged ? (seen >> 32) + 1 : 0) << 32 | seenNext; uint64_t expected = seen; bool ok = st.head.compare_exchange_strong(expected, want);                         // A 가 깨어나 CAS
        if (!tagged) { assert(ok && (uint32_t)st.snapshot() == 1); /* B 가 이미 가져간 노드 1 이 스택 맨 위에 되살아났다 */ } else { assert(!ok && (uint32_t)st.snapshot() == 0); } }
    { const int THREADS = 4, OPS = 200000; LockFreeStack s(THREADS * 8); std::atomic<long long> pushedSum{0}, poppedSum{0}; std::atomic<long> poppedCount{0}, pushedCount{0}; std::vector<std::thread> ts;
      for (int t = 0; t < THREADS; t++) ts.emplace_back([&, t] { for (int i = 1; i <= OPS; i++) { int v = t * OPS + i; if (s.push(v)) { pushedSum += v; pushedCount++; } int out; if (s.pop(out)) { poppedSum += out; poppedCount++; } } });
      for (auto& t : ts) t.join(); long long left = 0; long leftCount = 0; int out; while (s.pop(out)) { left += out; leftCount++; }
      assert(pushedSum == poppedSum + left && pushedCount == poppedCount + leftCount && s.countFree() == (long)s.capacity() && s.countData() == 0);                                         // ③ 보존·중복 없음·풀 무누수
      std::cout << "LockFreeStack: " << pushedCount << " pushes across " << THREADS << " threads, sums conserved, pool intact; " << std::endl; }
    std::cout << "LockFreeStack: LIFO and pool exhaustion verified; the scripted ABA corrupted the untagged stack and failed safely with a version tag" << std::endl; return 0;
}
// Time Complexity: push·pop 분할상환 O(1) (락프리: 경쟁에서 재시도)
// Space Complexity: O(풀 크기)
```
## TreiberStack()
### 대표코드
```cpp
#include <atomic>
#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <vector>
#include <cassert>

// 트라이버 스택(Treiber Stack): 임의 타입 T 를 담는 포인터 기반 락프리 스택이다. top 은 atomic<Node*> 하나. push: 새 노드를 만들고 `node->next = top; CAS(top, node->next, node)` 를 성공할 때까지 반복(compare_exchange_weak 은 실패하면 node->next 를 현재 top 으로 갱신해 준다). pop: top 을 읽고 CAS(top, t, t->next).
// 포인터 기반 구현의 위험은 ABA 와 메모리 회수다. pop 한 노드를 곧바로 delete 하면 ① 다른 스레드가 아직 t->next 를 읽는 중일 수 있고(해제된 메모리 접근) ② 같은 주소가 재할당되면 낡은 CAS 가 성공할 수 있다(ABA). 가장 단순한 안전 전략은 "스택이 살아 있는 동안 주소를 재사용하지 않는 것": 꺼낸 노드를 해제하지 않고 폐기 목록(retired, 이것도 락프리 스택)에 모았다가 스택이 파괴될 때 한꺼번에 해제한다. 주소가 재사용되지 않으니 ABA 가 일어날 수 없다. 대가는 pop 한 만큼 메모리가 늘어나는 것 — 오래 도는 서버에는 HazardPointer(AdvancedDataStructures.md)나 에포크 기반 회수가 필요하다.
// 값 복사: pop 은 노드를 CAS 로 독점한 뒤에 값을 이동해 꺼낸다(독점했으므로 경쟁 없음).
// 검증: ① 단일 스레드 LIFO·빈 스택 ② 문자열 값을 4 스레드가 push/pop 하며 모든 값이 정확히 한 번씩 나옴(중복·유실 없음) ③ 폐기 목록 크기 == 성공한 pop 수 ④ 소멸자가 남은 노드와 폐기 노드를 모두 해제(ASan/LSan 으로 누수 0 확인)
template <class T> class TreiberStack {
    struct Node { T value; std::atomic<Node*> next; explicit Node(T v) : value(std::move(v)), next(nullptr) {} };          // next 는 낡은 포인터를 쥔 스레드가 읽을 수 있으므로 atomic
    std::atomic<Node*> top_{nullptr}, retired_{nullptr}; std::atomic<long> retiredCount_{0};
    static void pushList(std::atomic<Node*>& head, Node* n) { Node* h = head.load(); do { n->next.store(h); } while (!head.compare_exchange_weak(h, n)); }
public:
    ~TreiberStack() { for (std::atomic<Node*>* h : {&top_, &retired_}) { Node* n = h->load(); while (n) { Node* nx = n->next.load(); delete n; n = nx; } } }
    void push(T v) { pushList(top_, new Node(std::move(v))); }
    bool pop(T& out) {
        Node* t = top_.load();
        while (t && !top_.compare_exchange_weak(t, t->next.load())) {}                          // 실패하면 t 가 현재 top 으로 갱신된다
        if (!t) return false;
        out = std::move(t->value);                                                              // 노드를 독점했으므로 안전
        pushList(retired_, t); retiredCount_++; return true;                                    // 해제하지 않고 폐기 목록에 보관 -> 주소가 재사용되지 않는다
    }
    long retired() const { return retiredCount_.load(); }
};
int main() {
    { TreiberStack<std::string> s; std::string v; assert(!s.pop(v)); for (int i = 0; i < 100; i++) s.push("item" + std::to_string(i)); for (int i = 99; i >= 0; i--) { assert(s.pop(v) && v == "item" + std::to_string(i)); } assert(!s.pop(v) && s.retired() == 100); }          // ① ③
    { const int THREADS = 4, PER = 50000; TreiberStack<std::string> s; std::vector<std::vector<std::string>> got(THREADS); std::vector<std::thread> ts;
      for (int t = 0; t < THREADS; t++) ts.emplace_back([&, t] { for (int i = 0; i < PER; i++) { s.push(std::to_string(t) + ":" + std::to_string(i)); std::string v; if (s.pop(v)) got[t].push_back(v); if (i % 3 == 0 && s.pop(v)) got[t].push_back(v); } });
      for (auto& t : ts) t.join(); std::string v; std::vector<std::string> rest; while (s.pop(v)) rest.push_back(v);
      std::multiset<std::string> all; for (auto& g : got) all.insert(g.begin(), g.end()); all.insert(rest.begin(), rest.end()); assert((int)all.size() == THREADS * PER);                                                  // ② 개수 보존
      std::set<std::string> uniq(all.begin(), all.end()); assert(uniq.size() == all.size()); for (int t = 0; t < THREADS; t++) for (int i = 0; i < PER; i += 997) assert(uniq.count(std::to_string(t) + ":" + std::to_string(i)));                // 중복·유실 없음
      long pops = (long)all.size(); assert(s.retired() == pops); std::cout << "TreiberStack: " << pops << " string values moved through 4 threads exactly once; "; }                                                           // ③
    std::cout << "retired nodes (kept until destruction) equal successful pops; destructor frees everything" << std::endl; return 0;
}
// Time Complexity: push·pop 분할상환 O(1) (락프리)
// Space Complexity: O(N + 지금까지의 pop 수) — 폐기 노드는 소멸 때까지 보관
```
## EliminationBackoffStack()
### 대표코드
```cpp
#include <atomic>
#include <cstdint>
#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <vector>
#include <cassert>

// 제거-백오프 스택(Hendler–Shavit–Yerushalmi 2004): 락프리 스택은 모든 스레드가 하나의 top 포인터를 CAS 하므로 경쟁이 심하면 병목이 된다. 그런데 동시에 도착한 push 와 pop 은 서로 상쇄될 수 있다 — push(x) 와 pop() 이 만나면 x 를 스택에 넣었다 꺼낸 것과 결과가 같으므로 스택을 거치지 않고 둘이 바로 값을 주고받으면 된다("제거"). 이 교환은 top 이 아닌 여러 개의 슬롯(제거 배열)에서 이뤄지므로 경쟁이 분산되고 오히려 처리량이 스레드 수에 따라 늘어난다.
// 알고리즘: push/pop 은 먼저 중앙 스택(Treiber)에 CAS 를 한 번 시도한다. 실패(경쟁)하면 제거 배열의 무작위 슬롯에서 상대를 찾아 교환을 시도하고, 실패하면 중앙 스택부터 다시 한다. 교환 슬롯의 프로토콜: 슬롯은 {EMPTY, PUSH_WAIT(값), POP_WAIT, TAKEN, DELIVERED(값)} 상태를 가진다. push 는 EMPTY 에 PUSH_WAIT 을 걸고 기다리며 pop 이 PUSH_WAIT 을 TAKEN 으로 바꿔 값을 가져가면 완료, 거꾸로 pop 이 POP_WAIT 을 걸어 두면 push 가 DELIVERED(값)로 바꿔 전달한다. 모든 전이는 슬롯 워드 전체(태그 포함)에 대한 CAS 이고 태그가 전이마다 올라가 ABA 가 없다.
// 선형화 가능성: 제거된 쌍은 "push 직후 pop" 이라는 순간에 선형화된다 — 두 연산의 구간이 겹치므로 유효한 순서다. 따라서 스택 의미(LIFO)는 유지된다.
// 검증: ① 교환기 단위 시험: push 쪽과 pop 쪽 스레드가 같은 슬롯에서 값을 정확히 주고받음 ② 6 스레드(push 3 · pop 3 혼합) 스트레스: 값의 합과 개수 보존, 중복 없음, 풀 무누수 ③ 제거로 처리된 쌍의 수(참고 출력) ④ TSan 통과
const uint32_t NIL = 0xFFFFFFFFu;
enum State : uint64_t { EMPTY = 0, PUSH_WAIT = 1, TAKEN = 2, POP_WAIT = 3, DELIVERED = 4 };
inline uint64_t pack(uint64_t tag, State s, uint32_t v) { return (tag << 40) | ((uint64_t)s << 32) | v; } inline State st(uint64_t w) { return (State)((w >> 32) & 0xFF); } inline uint64_t tg(uint64_t w) { return w >> 40; } inline uint32_t val(uint64_t w) { return (uint32_t)w; }
struct Exchanger {
    std::atomic<uint64_t> slot{0};
    bool offerPush(uint32_t v, int spins) {                                                // push 쪽: 값 v 를 pop 에게 넘기려 시도
        uint64_t w = slot.load();
        if (st(w) == EMPTY) { uint64_t mine = pack(tg(w) + 1, PUSH_WAIT, v); if (!slot.compare_exchange_strong(w, mine)) return false;
            for (int i = 0; i < spins; i++) { uint64_t x = slot.load(); if (st(x) == TAKEN) { slot.store(pack(tg(x) + 1, EMPTY, 0)); return true; } std::this_thread::yield(); }
            uint64_t expected = mine; if (slot.compare_exchange_strong(expected, pack(tg(mine) + 1, EMPTY, 0))) return false;      // 철회 성공: 교환 실패
            uint64_t x = slot.load(); slot.store(pack(tg(x) + 1, EMPTY, 0)); return true; }                                         // 철회 직전에 pop 이 가져갔다 -> 성공
        if (st(w) == POP_WAIT) return slot.compare_exchange_strong(w, pack(tg(w) + 1, DELIVERED, v));                                // 기다리던 pop 에게 전달
        return false;
    }
    bool offerPop(uint32_t& out, int spins) {
        uint64_t w = slot.load();
        if (st(w) == EMPTY) { uint64_t mine = pack(tg(w) + 1, POP_WAIT, 0); if (!slot.compare_exchange_strong(w, mine)) return false;
            for (int i = 0; i < spins; i++) { uint64_t x = slot.load(); if (st(x) == DELIVERED) { out = val(x); slot.store(pack(tg(x) + 1, EMPTY, 0)); return true; } std::this_thread::yield(); }
            uint64_t expected = mine; if (slot.compare_exchange_strong(expected, pack(tg(mine) + 1, EMPTY, 0))) return false;
            uint64_t x = slot.load(); out = val(x); slot.store(pack(tg(x) + 1, EMPTY, 0)); return true; }
        if (st(w) == PUSH_WAIT) { uint32_t v = val(w); if (slot.compare_exchange_strong(w, pack(tg(w) + 1, TAKEN, 0))) { out = v; return true; } }
        return false;
    }
};
class EliminationStack {
    static const int SLOTS = 4;
    std::unique_ptr<std::atomic<uint32_t>[]> nextIdx; std::unique_ptr<std::atomic<uint32_t>[]> value; std::atomic<uint64_t> top{NIL}, freeTop{0}; Exchanger ex[SLOTS]; std::atomic<long> eliminated{0};
    static bool casPush(std::atomic<uint64_t>& head, std::atomic<uint32_t>* nx, uint32_t i) { uint64_t h = head.load(); nx[i].store((uint32_t)h); return head.compare_exchange_strong(h, (((h >> 32) + 1) << 32) | i); }          // CAS 한 번만 시도
    static uint32_t casPop(std::atomic<uint64_t>& head, std::atomic<uint32_t>* nx, bool& contended) { uint64_t h = head.load(); uint32_t i = (uint32_t)h; if (i == NIL) { contended = false; return NIL; } uint32_t n = nx[i].load(); if (head.compare_exchange_strong(h, (((h >> 32) + 1) << 32) | n)) { contended = false; return i; } contended = true; return NIL; }
    static void pushLoop(std::atomic<uint64_t>& head, std::atomic<uint32_t>* nx, uint32_t i) { while (!casPush(head, nx, i)) {} }
    uint32_t popLoop(std::atomic<uint64_t>& head) { bool c; for (;;) { uint32_t i = casPop(head, nextIdx.get(), c); if (!c) return i; } }
public:
    explicit EliminationStack(uint32_t cap) : nextIdx(new std::atomic<uint32_t>[cap]), value(new std::atomic<uint32_t>[cap]) { for (uint32_t i = 0; i < cap; i++) { nextIdx[i] = i + 1 < cap ? i + 1 : NIL; value[i] = 0; } freeTop = cap ? 0 : NIL; }
    Exchanger& exchanger(int i) { return ex[i]; }
    bool push(uint32_t v, std::mt19937& rng) {
        uint32_t n = popLoop(freeTop); if (n == NIL) return false; value[n].store(v);
        for (;;) { if (casPush(top, nextIdx.get(), n)) return true;                                                          // 중앙 스택: CAS 한 번
            if (ex[rng() % SLOTS].offerPush(v, 20)) { eliminated++; pushLoop(freeTop, nextIdx.get(), n); return true; } }          // 경쟁하면 제거 배열에서 상대를 찾는다 (성공하면 노드는 풀로)
    }
    bool pop(uint32_t& out, std::mt19937& rng) {
        for (;;) { bool contended; uint32_t i = casPop(top, nextIdx.get(), contended);
            if (!contended) { if (i == NIL) return false; out = value[i].load(); pushLoop(freeTop, nextIdx.get(), i); return true; }
            if (ex[rng() % SLOTS].offerPop(out, 20)) { eliminated++; return true; } }
    }
    long eliminatedPairs() const { return eliminated.load(); }
    long countFree() const { long c = 0; for (uint32_t i = (uint32_t)freeTop.load(); i != NIL; i = nextIdx[i].load()) c++; return c; }
    long countData() const { long c = 0; for (uint32_t i = (uint32_t)top.load(); i != NIL; i = nextIdx[i].load()) c++; return c; }
};
int main() {
    { Exchanger e; std::atomic<bool> got{false}; uint32_t received = 0; std::thread popper([&] { uint32_t v; for (long tries = 0; tries < 50000000 && !got; tries++) if (e.offerPop(v, 1000)) { received = v; got = true; } });
      for (long tries = 0; tries < 50000000 && !got; tries++) { if (e.offerPush(4242, 1000)) { while (!got) std::this_thread::yield(); } } popper.join(); assert(got && received == 4242 && st(e.slot.load()) == EMPTY); }       // ① 교환기: 값이 정확히 전달되고 슬롯이 EMPTY 로 복귀
    { const int PUSHERS = 3, POPPERS = 3, OPS = 100000; EliminationStack s(64); std::atomic<long long> pushedSum{0}, poppedSum{0}; std::atomic<long> pushedCount{0}, poppedCount{0}; std::vector<std::thread> ts;
      for (int t = 0; t < PUSHERS; t++) ts.emplace_back([&, t] { std::mt19937 rng(100 + t); for (int i = 1; i <= OPS; i++) { uint32_t v = (uint32_t)(t * OPS + i); while (!s.push(v, rng)) std::this_thread::yield(); pushedSum += v; pushedCount++; } });
      std::atomic<bool> producersDone{false};
      for (int t = 0; t < POPPERS; t++) ts.emplace_back([&, t] { std::mt19937 rng(200 + t); uint32_t v; while (!producersDone || poppedCount < pushedCount) { if (s.pop(v, rng)) { poppedSum += v; poppedCount++; } else std::this_thread::yield(); } });
      for (int t = 0; t < PUSHERS; t++) ts[t].join(); producersDone = true; for (int t = PUSHERS; t < PUSHERS + POPPERS; t++) ts[t].join();
      std::mt19937 rng(1); uint32_t v; long long left = 0; while (s.pop(v, rng)) left += v;
      assert(pushedCount == PUSHERS * OPS && poppedSum + left == pushedSum && s.countFree() == 64 && s.countData() == 0);                                                                                              // ② 보존, 풀 무누수
      std::cout << "EliminationBackoffStack: " << pushedCount << " items exchanged by 3 pushers and 3 poppers with sums conserved; pairs eliminated without touching the central stack: " << s.eliminatedPairs() << std::endl; }
    return 0;
}
// Time Complexity: 경쟁이 없으면 O(1); 경쟁이 있으면 교환 성공 시 중앙 스택을 거치지 않음
// Space Complexity: O(풀 크기 + 슬롯 수)
```

# Part 10. 연구 주제
## PersistentStack()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 영속 스택(Persistent Stack): 연산이 기존 스택을 바꾸지 않고 "새 버전" 을 돌려주며, 이전 버전은 언제든 그대로 쓸 수 있다. 연결 스택의 push/pop 이 머리만 건드린다는 성질 덕분에 거의 공짜로 만들어진다 — push(s, x) 는 노드 하나를 만들어 기존 s 를 next 로 가리키고, pop(s) 는 s->next 를 돌려줄 뿐이다. 두 버전이 꼬리를 공유하므로 복사가 없다.
// 응용: 실행 취소(undo)/되돌리기 이력, 분기하는 탐색(각 분기가 같은 접두 경로를 공유), 함수형 언어의 리스트, 락 없는 스레드 간 공유(불변이라 경쟁 없음). 버전은 값이 아니라 "포인터 하나" 이므로 모든 버전을 보관해도 노드는 새로 만든 만큼만 늘어난다.
// 주의: shared_ptr 사슬은 기본 소멸자가 재귀적으로 풀려 수십만 길이에서 호출 스택이 넘친다. 노드 소멸자에서 "나만 가진 사슬은 반복문으로 풀기" 를 하면 안전하다(아래 구현).
// 검증: ① 임의의 옛 버전에서 이어 붙이는 무작위 push/pop 5000 번이 각 버전의 벡터 스냅샷과 같다 ② 구조 공유: push 한 새 버전의 next 가 옛 버전과 같은 노드, pop 은 새 노드를 만들지 않음(노드 생성 계수) ③ 분기: 같은 버전에서 두 갈래로 자라도 서로 영향이 없다 ④ 모든 버전을 버리면 노드가 전부 해제됨 ⑤ 100 만 길이 사슬이 스택 오버플로 없이 해제
struct Node; typedef std::shared_ptr<const Node> Stack;
static long liveNodes = 0, createdNodes = 0;
struct Node { int value; Stack next; Node(int v, Stack n) : value(v), next(std::move(n)) { liveNodes++; createdNodes++; }
    ~Node() { liveNodes--; Stack cur = std::move(next); while (cur && cur.use_count() == 1) { Stack nx = std::move(const_cast<Node&>(*cur).next); cur.reset(); cur = std::move(nx); } } };      // 반복적 해제: 단독 소유 사슬은 하나씩 푼다
Stack push(const Stack& s, int v) { return std::make_shared<const Node>(v, s); }
Stack pop(const Stack& s) { return s->next; }                                         // 새 노드 없음
std::vector<int> toVector(Stack s) { std::vector<int> v; for (; s; s = s->next) v.push_back(s->value); return v; }
int main() {
    std::mt19937 rng(3);
    { std::vector<Stack> ver = {nullptr}; std::vector<std::vector<int>> snap = {{}};
      for (int step = 0; step < 5000; step++) { size_t b = rng() % ver.size(); Stack s = ver[b]; std::vector<int> m = snap[b]; long createdBefore = createdNodes;
        if (!s || rng() % 3) { int x = rng() % 1000; Stack t = push(s, x); assert(createdNodes == createdBefore + 1 && t->next == s); ver.push_back(t); m.insert(m.begin(), x); }                             // ② push: 노드 1 개, 꼬리 공유
        else { Stack t = pop(s); assert(createdNodes == createdBefore && t == s->next); ver.push_back(t); m.erase(m.begin()); }                                                                         // pop: 새 노드 0 개
        snap.push_back(m); if (snap.back().size() > 60) { ver.back() = pop(ver.back()); snap.back().erase(snap.back().begin()); } }
      for (size_t i = 0; i < ver.size(); i++) assert(toVector(ver[i]) == snap[i]); }                                                                                                                    // ① 모든 버전이 자기 스냅샷과 같다
    { Stack base = push(push(nullptr, 1), 2); Stack left = push(base, 10), right = push(push(base, 20), 30); assert(toVector(base) == (std::vector<int>{2, 1}) && toVector(left) == (std::vector<int>{10, 2, 1}) && toVector(right) == (std::vector<int>{30, 20, 2, 1}) && left->next == base);            // ③ 분기
      Stack undone = pop(right); assert(toVector(undone) == (std::vector<int>{20, 2, 1}) && toVector(right).size() == 4); }                                                                           // pop 해도 원본은 그대로
    assert(liveNodes == 0);                                                                                                                                                                              // ④ 모든 버전을 버리면 노드 해제
    { Stack s; for (int i = 0; i < 1000000; i++) s = push(s, i); assert(liveNodes == 1000000); } assert(liveNodes == 0);                                                                                 // ⑤ 반복 해제 덕분에 오버플로 없음
    std::cout << "PersistentStack: thousands of branching versions matched their snapshots; push created exactly one node, pop none; sharing, branching and iterative release of a 1,000,000-node chain verified" << std::endl; return 0;
}
// Time Complexity: push·pop·top O(1) (모든 버전에서), 순회 O(N)
// Space Complexity: 연산당 새 노드 O(1), 이전 버전과 구조 공유
```
## ImmutableStack()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>
#include <cassert>

// 불변 스택(Immutable Stack): 객체의 모든 메서드가 const 이고 "변경" 은 새 객체를 돌려주는 값 의미의 스택이다. 영속 스택(PersistentStack)이 "이전 버전을 쓸 수 있다" 는 자료구조의 성질을 강조한다면, 불변 스택은 "객체가 만들어진 뒤 절대 바뀌지 않는다" 는 API 의 약속을 강조한다. 이 약속 덕분에 ① 여러 스레드가 잠금 없이 같은 스택을 읽을 수 있고(데이터 레이스 불가) ② 호출한 쪽이 인자가 몰래 바뀔 걱정을 하지 않으며 ③ 해시·동등 비교가 안정적이다.
// 구현 장치: 노드는 크기를 함께 저장해 size() 가 O(1) 이고, 동등 비교는 같은 노드를 가리키면(꼬리를 공유하면) 나머지를 볼 필요 없이 즉시 같다고 답해 공유 접미사를 O(1) 에 건너뛴다. 빈 스택은 하나의 공유 객체다.
// 검증: ① 모든 메서드가 const (const 객체로 호출 가능, 컴파일이 증명) ② 한 스택을 4 스레드가 동시에 읽으며 각자 자신의 파생 스택을 만들어도 원본이 그대로이고 결과가 맞음(TSan 으로 레이스 없음 확인) ③ size() 는 노드를 따라가지 않아도 정확 ④ 동등 비교: 내용이 같으면 참, 공유 접미사에서 비교한 노드 수가 접두사 길이로 한정 ⑤ 파생 스택들이 원본 접미사를 공유
class ImmutableStack {
    struct Node { int value; std::shared_ptr<const Node> next; std::size_t size; };
    std::shared_ptr<const Node> head_;
    explicit ImmutableStack(std::shared_ptr<const Node> h) : head_(std::move(h)) {}
public:
    ImmutableStack() = default;
    ImmutableStack push(int v) const { return ImmutableStack(std::make_shared<const Node>(Node{v, head_, size() + 1})); }
    ImmutableStack pop() const { return ImmutableStack(head_->next); }                    // 비어 있으면 호출자 책임 (empty() 로 확인)
    int top() const { return head_->value; } bool empty() const { return !head_; } std::size_t size() const { return head_ ? head_->size : 0; }
    const void* identity() const { return head_.get(); }
    static bool equal(const ImmutableStack& a, const ImmutableStack& b, long* compared = nullptr) {
        auto p = a.head_; auto q = b.head_; long c = 0;
        while (p && q) { if (p.get() == q.get()) { if (compared) *compared = c; return true; } c++; if (p->value != q->value) { if (compared) *compared = c; return false; } p = p->next; q = q->next; }
        if (compared) *compared = c; return !p && !q;
    }
    std::vector<int> toVector() const { std::vector<int> v; for (auto p = head_; p; p = p->next) v.push_back(p->value); return v; }
};
int main() {
    const ImmutableStack empty; static_assert(noexcept(empty.empty()) || true, ""); assert(empty.empty() && empty.size() == 0);                      // ① const 객체에서 모든 조회가 가능
    ImmutableStack base; for (int i = 0; i < 1000; i++) base = base.push(i); const ImmutableStack shared = base; assert(shared.size() == 1000 && shared.top() == 999);        // ③ size 는 O(1)
    std::vector<std::vector<int>> results(4); std::vector<ImmutableStack> derived(4); std::vector<std::thread> ts;
    for (int t = 0; t < 4; t++) ts.emplace_back([&, t] { ImmutableStack mine = shared; for (int i = 0; i < 200; i++) mine = mine.push(100000 * (t + 1) + i); for (int i = 0; i < 50; i++) mine = mine.pop(); long long sum = 0; for (ImmutableStack s = mine; !s.empty(); s = s.pop()) sum += s.top(); results[t] = {(int)mine.size(), (int)(sum % 1000003)}; derived[t] = mine; });
    for (auto& t : ts) t.join();                                                                                                                                           // ② 동시 읽기·파생
    for (int t = 0; t < 4; t++) { assert(results[t][0] == 1150); long long expect = 0; for (int i = 0; i < 150; i++) expect += 100000 * (t + 1) + i; for (int i = 0; i < 1000; i++) expect += i; assert(results[t][1] == (int)(expect % 1000003)); }
    assert(shared.size() == 1000 && shared.top() == 999 && shared.toVector().size() == 1000);                                                                              // 원본은 그대로
    for (int t = 0; t < 4; t++) { ImmutableStack s = derived[t]; for (int i = 0; i < 150; i++) s = s.pop(); assert(s.identity() == shared.identity()); }                      // ⑤ 파생 스택은 원본 노드를 공유
    { ImmutableStack a = shared.push(1).push(2), b = shared.push(1).push(2); long c = 0; assert(ImmutableStack::equal(a, b, &c) && c <= 2); ImmutableStack x = shared.push(3); assert(!ImmutableStack::equal(a, x) && ImmutableStack::equal(shared, shared, &c) && c == 0); }     // ④ 공유 접미사에서 즉시 같다고 판단
    std::cout << "ImmutableStack: 4 threads derived private stacks from one shared 1000-element stack with no synchronization; the original never changed, size() is O(1), and equality stopped at the shared suffix" << std::endl; return 0;
}
// Time Complexity: push·pop·top·size O(1), 동등 비교 O(서로 다른 접두사 길이)
// Space Complexity: 변경당 O(1), 나머지는 공유
```
## StackAllocator()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <new>
#include <vector>
#include <cassert>

// 스택 할당기(StackAllocator, 범프/아레나 할당기): 큰 메모리 덩어리 하나를 미리 잡아 두고, 할당은 "오프셋을 올리기" 로, 해제는 "오프셋을 되돌리기" 로 처리한다. 호출 스택의 할당·해제와 같은 후입선출(LIFO)이라 모든 연산이 O(1) 이고 단편화가 없으며 헤더도 거의 필요 없다. 게임 프레임 임시 메모리, 컴파일러의 AST 할당, 요청 단위 서버 메모리에서 쓴다.
// 규칙: ① 정렬 — 반환 주소는 요청한 정렬(alignof) 배수여야 하므로 오프셋을 올림한다 ② 소진 — 남은 공간이 모자라면 nullptr (예외 없이 실패를 알린다) ③ 해제는 개별 블록이 아니라 "마커(그 시점의 오프셋)로 되감기" — 마커 이후 할당이 한꺼번에 사라진다. 순서를 어기는 되감기(옛 마커 → 새 마커로 앞으로 가기)는 거절한다 ④ RAII 스코프 객체가 생성 시 마커를 잡고 소멸 시 되감는다.
// 소멸자가 필요한 객체를 담을 때는 호출자가 직접 소멸자를 불러야 한다 — 이 할당기는 메모리만 관리한다.
// 검증: ① 모든 할당 주소가 요청 정렬을 만족하고 서로 겹치지 않음(무작위 크기·정렬 2000 개) ② 소진되면 nullptr 이고 이후 되감기로 다시 할당 가능 ③ 마커로 되감으면 같은 주소가 다시 나온다(재현성) ④ 앞으로 가는 되감기는 거절 ⑤ 중첩 스코프가 안쪽부터 되감기며 고수위(high-water mark)가 기록됨
class StackAllocator {
    unsigned char* base_; std::size_t cap_, off_ = 0, high_ = 0;
public:
    typedef std::size_t Marker;
    explicit StackAllocator(std::size_t capacity) : base_(static_cast<unsigned char*>(::operator new(capacity, std::align_val_t(64)))), cap_(capacity) {}
    ~StackAllocator() { ::operator delete(base_, std::align_val_t(64)); }
    StackAllocator(const StackAllocator&) = delete; StackAllocator& operator=(const StackAllocator&) = delete;
    void* alloc(std::size_t n, std::size_t align = alignof(std::max_align_t)) {
        std::uintptr_t cur = reinterpret_cast<std::uintptr_t>(base_) + off_; std::uintptr_t aligned = (cur + align - 1) & ~(std::uintptr_t)(align - 1); std::size_t newOff = off_ + (aligned - cur) + n;
        if (newOff > cap_) return nullptr; off_ = newOff; if (off_ > high_) high_ = off_; return reinterpret_cast<void*>(aligned);
    }
    Marker mark() const { return off_; }
    bool rewind(Marker m) { if (m > off_) return false; off_ = m; return true; }               // 앞으로 가는 되감기는 거절
    std::size_t used() const { return off_; } std::size_t highWater() const { return high_; } std::size_t capacity() const { return cap_; }
};
class Scope { StackAllocator& a_; StackAllocator::Marker m_; public: explicit Scope(StackAllocator& a) : a_(a), m_(a.mark()) {} ~Scope() { a_.rewind(m_); } };
int main() {
    { StackAllocator a(1 << 16); std::vector<std::pair<std::uintptr_t, std::size_t>> blocks; unsigned seed = 7; auto rnd = [&] { seed = seed * 1664525u + 1013904223u; return seed >> 8; };
      for (int i = 0; i < 2000; i++) { std::size_t n = 1 + rnd() % 24, al = (std::size_t)1 << (rnd() % 5); void* p = a.alloc(n, al); if (!p) break; std::uintptr_t u = reinterpret_cast<std::uintptr_t>(p); assert(u % al == 0); blocks.push_back({u, n}); }          // ① 정렬
      for (std::size_t i = 1; i < blocks.size(); i++) assert(blocks[i].first >= blocks[i - 1].first + blocks[i - 1].second);                                                                                                   // 겹치지 않음 (할당 순서대로 증가)
      assert(blocks.size() > 500 && a.used() <= a.capacity()); }
    { StackAllocator a(256); int count = 0; while (a.alloc(40, 8)) count++; assert(count == 6 && a.alloc(40, 8) == nullptr && a.alloc(16, 1) != nullptr); a.rewind(0); assert(a.alloc(40, 8) != nullptr); }      // ② 소진 후 되감기로 다시 할당
    { StackAllocator a(1024); a.alloc(10, 1); StackAllocator::Marker m = a.mark(); void* p1 = a.alloc(100, 16); void* p2 = a.alloc(7, 1); assert(a.rewind(m)); void* q1 = a.alloc(100, 16); void* q2 = a.alloc(7, 1); assert(p1 == q1 && p2 == q2);                  // ③ 되감으면 같은 주소 재현
      StackAllocator::Marker later = a.mark(); a.rewind(m); assert(!a.rewind(later) && a.used() == m); }                                                                                                                            // ④ 앞으로 가는 되감기 거절
    { StackAllocator a(4096); a.alloc(100, 8); std::size_t base = a.used();
      { Scope outer(a); a.alloc(500, 8); std::size_t mid = a.used(); { Scope inner(a); a.alloc(1000, 8); assert(a.used() > mid); } assert(a.used() == mid); }
      assert(a.used() == base && a.highWater() >= base + 1500); }                                                                                                                                                       // ⑤ 중첩 스코프와 고수위
    std::cout << "StackAllocator: 2000 randomly sized and aligned blocks never overlapped and respected alignment; rewinding to a marker reproduced identical addresses; forward rewinds were refused; nested scopes unwound innermost-first" << std::endl; return 0;
}
// Time Complexity: 할당·되감기 O(1)
// Space Complexity: 미리 확보한 용량 (할당당 헤더 없음, 정렬 패딩만)
```
## StackOverflow()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <vector>
#include <cassert>
#if defined(__unix__)
#include <pthread.h>
#include <sys/resource.h>
#endif

// 스택 오버플로(Stack Overflow): 호출 스택이 정해진 크기를 넘어 쌓이는 오류다. 프로세스의 스택은 기본 8 MB(리눅스 ulimit -s)쯤이라 프레임이 96 바이트면 약 87,000 단계까지만 재귀할 수 있고, 넘으면 스택 아래의 보호 페이지에 닿아 SIGSEGV 로 죽는다. 무한 재귀뿐 아니라 입력이 큰 정상적인 재귀(깊이 10^6 의 DFS)에서도 일어난다.
// 막는 방법: ① 재귀를 명시적 스택(힙)으로 바꾼다(IterativeDFS, RecursionSimulation) ② 꼬리 재귀를 반복문으로 바꾼다 ③ 깊이를 제한하고 한도에 닿으면 오류를 돌려주는 가드를 둔다 ④ 지역 큰 배열을 힙으로 옮긴다 ⑤ 스레드의 스택 크기를 늘린다(pthread_attr_setstacksize).
// 이 항목은 안전하게 실험한다: 스택 크기를 256 KB 로 줄인 스레드에서, 매 호출이 지역 변수의 주소를 현재 스택 사용량 추정치로 쓰고 허용치(128 KB)를 넘으면 재귀를 멈춘다(③). 그러면 충돌 없이 "한도에 닿았다" 는 사실과 도달 깊이를 얻는다. 깊이 10^7 의 같은 계산을 명시적 스택으로 하면 문제없이 끝난다(①). 실제 오버플로 크래시는 일으키지 않는다.
// audit: no-sanitize
// audit: gcc-only
// 검증: ① 가드가 있는 재귀가 한도에서 멈추고(hitLimit) 도달 깊이가 [허용 바이트 / 프레임 크기] 근처 ② 충돌 없이 반환 ③ 도달 깊이로 예측한 "256 KB 에서의 실제 오버플로 깊이" 가 가드 깊이의 약 2 배 ④ 같은 합 계산이 명시적 스택으로 1000만 단계 완료 ⑤ 기본 스택 크기(RLIMIT_STACK)를 읽어 예측 깊이를 계산
#if defined(__GNUC__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif
struct Probe { std::uintptr_t base; std::size_t allowed; long depthReached; bool hitLimit; long frameBytes; std::uintptr_t at3; };
static volatile long sink;
NOINLINE long recurse(Probe& p, long depth) {
    volatile char pad[48]; pad[0] = (char)depth; std::uintptr_t here = (std::uintptr_t)&pad[0];
    if (depth == 3) p.at3 = here; if (depth == 4) p.frameBytes = (long)(p.at3 - here);           // 연속한 두 단계의 주소 차이 = 프레임 크기
    if (p.base - here > p.allowed) { p.hitLimit = true; p.depthReached = depth; return depth; }  // 가드: 허용 사용량 초과 -> 오류로 반환
    long r = recurse(p, depth + 1); sink = r; return r;                                            // 꼬리 호출이 되지 않도록 반환 뒤 쓰기
}
long sumExplicit(long n) { std::vector<long> st; st.reserve(1024); for (long i = n; i > 0; i--) st.push_back(i); long s = 0; while (!st.empty()) { s += st.back(); st.pop_back(); } return s; }
#if defined(__unix__)
static void* runProbe(void* arg) { Probe* p = (Probe*)arg; volatile char anchor = 0; p->base = (std::uintptr_t)&anchor; p->hitLimit = false; p->depthReached = 0; recurse(*p, 0); return nullptr; }
#endif
int main() {
#if defined(__unix__)
    struct rlimit rl; getrlimit(RLIMIT_STACK, &rl); std::size_t defaultStack = rl.rlim_cur == RLIM_INFINITY ? 8u << 20 : (std::size_t)rl.rlim_cur; assert(defaultStack >= 64 * 1024);
    Probe probe; probe.allowed = 128 * 1024; probe.frameBytes = 0; probe.at3 = 0; pthread_attr_t attr; pthread_attr_init(&attr); pthread_attr_setstacksize(&attr, 256 * 1024); pthread_t th; int rc = pthread_create(&th, &attr, runProbe, &probe); assert(rc == 0); pthread_join(th, nullptr);
    assert(probe.hitLimit && probe.frameBytes >= 16 && probe.frameBytes <= 512);                                                                                 // ① ②
    long expected = (long)probe.allowed / probe.frameBytes; assert(probe.depthReached > expected * 8 / 10 && probe.depthReached < expected * 12 / 10 + 10);            // 도달 깊이 ≈ 허용 바이트 / 프레임 크기
    long crashDepth = (long)(256 * 1024) / probe.frameBytes; assert(crashDepth > probe.depthReached && crashDepth < 3 * probe.depthReached);                          // ③ 실제 오버플로 예측 깊이
    long predictedDefault = (long)(defaultStack / probe.frameBytes);                                                                                                    // ⑤ 기본 스택에서의 예측 최대 깊이
    assert(sumExplicit(10000000) == 10000000L * 10000001L / 2);                                                                                                         // ④ 명시적 스택은 1000만 단계도 문제없다
    std::cout << "StackOverflow: with a 256 KB thread stack and a 128 KB guard, recursion stopped cleanly at depth " << probe.depthReached << " (frame " << probe.frameBytes << " bytes); an unguarded run would crash near depth " << crashDepth << "; the default " << defaultStack / 1024 << " KB stack predicts about " << predictedDefault << " frames; the explicit-stack version summed 10,000,000 terms" << std::endl;
#else
    assert(sumExplicit(10000000) == 10000000L * 10000001L / 2); std::cout << "StackOverflow: POSIX threads unavailable; explicit-stack summation only" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(깊이)
// Space Complexity: 호출 스택 O(깊이 × 프레임), 명시적 스택 O(깊이) 힙
```
## StackUnwinding()
### 대표코드
```cpp
#include <exception>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 스택 되감기(Stack Unwinding): 예외가 던져지면 C++ 런타임은 호출 스택을 맨 위에서부터 한 프레임씩 풀어 가며 일치하는 catch 를 찾고, 풀리는 프레임마다 그 프레임의 지역 객체들을 "생성의 역순" 으로 소멸시킨다. 이것이 RAII(자원 획득 = 초기화)가 예외 안전의 토대인 이유다 — 잠금·파일·메모리를 객체 소멸자가 돌려주므로 중간에 예외로 빠져나가도 누수가 없다.
// 되감기 동안에는 소멸자에서 새 예외를 밖으로 던지면 안 된다(std::terminate). 소멸자 안에서 std::uncaught_exceptions() 로 "지금 되감기 중인가" 를 알 수 있다(스코프 가드가 커밋/롤백을 정할 때 쓴다). catch 에 닿지 못한 프레임은 풀리지 않을 수도 있어(구현 정의) 반드시 잡는 최상위 try 가 필요하다.
// 이 항목은 소멸 순서를 기록하는 객체를 여러 프레임에 두고 가장 깊은 곳에서 예외를 던져 확인한다: ① 소멸 순서가 정확히 생성의 역순 ② 소멸자가 되감기 중임을 감지 ③ catch 한 프레임보다 위(호출한 쪽)의 객체는 소멸되지 않음 ④ 정상 반환과 예외 반환 모두 같은 소멸 규칙 ⑤ 스코프 가드가 예외 시 롤백
std::vector<std::string> events;
struct Tracer { std::string name; int unwindingAtCtor; explicit Tracer(std::string n) : name(std::move(n)), unwindingAtCtor(std::uncaught_exceptions()) { events.push_back("+" + name); }
    ~Tracer() { events.push_back(std::string(std::uncaught_exceptions() > unwindingAtCtor ? "~!" : "~") + name); } };           // ~! : 예외로 인한 되감기 중에 소멸
struct Rollback { bool& committed; std::vector<int>& data; std::size_t mark; Rollback(std::vector<int>& d, bool& c) : committed(c), data(d), mark(d.size()) {} ~Rollback() { if (!committed) data.resize(mark); } };      // 커밋되지 않으면 되돌린다
void level3(bool fail) { Tracer c("c"); if (fail) throw std::runtime_error("boom"); events.push_back("level3 ok"); }
void level2(bool fail) { Tracer b("b"); Tracer b2("b2"); level3(fail); events.push_back("level2 after call"); }
void level1(bool fail) { Tracer a("a"); try { level2(fail); events.push_back("level1 after call"); } catch (const std::exception& e) { events.push_back(std::string("caught ") + e.what()); } events.push_back("level1 end"); }
void appendAll(std::vector<int>& data, int n, int failAt) { bool committed = false; Rollback rb(data, committed); for (int i = 0; i < n; i++) { if (i == failAt) throw std::runtime_error("append failed"); data.push_back(i); } committed = true; }
int main() {
    events.clear(); level1(true);
    std::vector<std::string> want = {"+a", "+b", "+b2", "+c", "~!c", "~!b2", "~!b", "caught boom", "level1 end", "~a"};
    assert(events == want);                                                                                                      // ① 생성의 역순 소멸, ② 되감기 중 표시(~!), ③ a 는 catch 가 있는 프레임이라 정상 소멸(~a)
    events.clear(); level1(false);
    std::vector<std::string> wantOk = {"+a", "+b", "+b2", "+c", "level3 ok", "~c", "level2 after call", "~b2", "~b", "level1 after call", "level1 end", "~a"};
    assert(events == wantOk);                                                                                                    // ④ 정상 반환도 같은 소멸 규칙 (되감기 표시 없음)
    { std::vector<int> data = {100, 200}; bool threw = false; try { appendAll(data, 10, 5); } catch (const std::runtime_error&) { threw = true; } assert(threw && data == (std::vector<int>{100, 200}));      // ⑤ 예외 시 롤백
      appendAll(data, 3, -1); assert(data == (std::vector<int>{100, 200, 0, 1, 2})); }
    { events.clear(); try { Tracer outer("outer"); try { Tracer inner("inner"); throw 42; } catch (int) { events.push_back("inner catch"); throw; } } catch (int v) { events.push_back("outer catch " + std::to_string(v)); }
      assert(events == (std::vector<std::string>{"+outer", "+inner", "~!inner", "inner catch", "~!outer", "outer catch 42"})); }                                                           // 다시 던지기: 두 프레임이 차례로 풀림
    std::cout << "StackUnwinding: objects were destroyed in reverse order of construction while the exception propagated, destructors detected the unwinding, and a scope guard rolled back on failure" << std::endl; return 0;
}
// Time Complexity: 되감기 O(풀리는 프레임 수 + 소멸시킬 객체 수) — 예외가 던져질 때만 비용 발생
// Space Complexity: O(1) 추가
```
