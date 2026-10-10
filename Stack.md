# Part 1. 기본 연산
## CreateStack()
### 대표코드
```cpp
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <new>
#include <random>
#include <stack>
#include <utility>
#include <cassert>

// 스택 만들기(Create): "비어 있는 스택" 이라는 초기 상태를 세우는 일이다. 새 스택은 크기 0, top 없음, 어떤 pop/peek 도 실패해야 하며, 이 불변식이 이후 모든 연산의 출발점이 된다.
// 표현 방식에 따라 만드는 비용이 다르다. 배열 스택은 용량을 정해 메모리를 한 번에 확보하고(할당 1 번), 연결 스택은 top = nullptr 하나로 시작해 아무것도 할당하지 않는다(할당 0 번; 메모리는 push 마다 노드 하나씩).
// 자원을 쥐는 클래스는 RAII 를 지킨다: 생성자가 얻고 소멸자가 돌려주며, 얕은 복사로 이중 해제가 나지 않도록 복사는 금지하고 이동(소유권 이전)만 허용한다.
// 검증(전역 operator new/delete 를 교체해 할당 횟수와 생존 블록을 센다): ① 새 스택은 비어 있고 크기 0이며 peek/pop 이 실패한다 ② 배열 스택 생성은 할당 1 번, 연결 스택은 0 번이고 첫 push 에서 1 번 ③ 3000 개를 만들고 부숴도 생존 블록이 늘지 않는다(누수 0) ④ 용량 0 도 정상 ⑤ 이동 후 원본은 빈 스택이고 내용은 새 스택으로 넘어간다 ⑥ 실무의 std::stack 도 같은 초기 상태를 가진다
//  ⑦ 만든 직후부터 무작위 연산(푸시 2 : 팝 1) 10 만 번을 용량 1·2·3·7·64 의 배열 스택(가득 차면 거부)과 연결 스택(거부 없음)에 흘려 보내 각각 std::stack 모형과 대조 — 반환값·top·크기가 매번 같고, 배열 스택은 한 번도 용량을 넘지 않는다
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
template <class S> void checkFresh(S& s) { int v = 123; bool pk = s.peek(v), po = s.pop(v); assert(s.empty() && s.size() == 0 && !pk && !po && v == 123); }                // ① 초기 불변식 (실패한 호출은 출력 인자를 건드리지 않는다)
int main() {
    long baseLive = liveBlocks;
    { ArrayStack a(16); LinkedStack l; checkFresh(a); checkFresh(l); }
    long b0 = newCalls; { ArrayStack a(16); assert(newCalls - b0 == 1); } long b1 = newCalls; { LinkedStack l; assert(newCalls == b1); l.push(1); assert(newCalls - b1 == 1); }          // ② 할당 횟수
    for (int i = 0; i < 3000; i++) { ArrayStack a(i % 40); LinkedStack l; for (int k = 0; k < i % 7; k++) { a.push(k); l.push(k); } } assert(liveBlocks == baseLive);                    // ③ 누수 0
    { ArrayStack zero(0); int v = 0; bool r1 = zero.push(1), r2 = zero.pop(v), r3 = zero.peek(v); assert(zero.empty() && !r1 && !r2 && !r3); }                                                                            // ④ 용량 0
    { ArrayStack a(4); a.push(7); a.push(8); ArrayStack b(std::move(a)); int v1 = 0, v2 = 0; bool r1 = a.push(1); std::size_t bs = b.size(); bool g1 = b.pop(v1), g2 = b.pop(v2); assert(a.empty() && a.size() == 0 && !r1 && bs == 2 && g1 && v1 == 8 && g2 && v2 == 7); }        // ⑤ 이동
    {   std::mt19937 rng(5); for (int cap : {1, 2, 3, 7, 64}) { ArrayStack a(cap); LinkedStack l; std::stack<int> ma, ml; long refused = 0;                                         // ⑦ 무작위 대조
            for (int step = 0; step < 100000; ++step) { int v = (int)rng();
                if (rng() % 3 != 0) { bool okA = a.push(v), okL = l.push(v); assert(okA == (ma.size() < (std::size_t)cap) && okL); if (okA) ma.push(v); else ++refused; ml.push(v); }
                else { int x = -1, y = -1; bool gotA = a.pop(x), gotL = l.pop(y); assert(gotA == !ma.empty() && gotL == !ml.empty()); if (gotA) { assert(x == ma.top()); ma.pop(); } if (gotL) { assert(y == ml.top()); ml.pop(); } }
                assert(a.size() == ma.size() && l.size() == ml.size() && a.size() <= (std::size_t)cap); int f = 0, g = 0; bool pa = a.peek(f), pl = l.peek(g); assert(pa == !ma.empty() && pl == !ml.empty()); if (!ma.empty()) assert(f == ma.top() && g == ml.top()); }
            assert(refused > 0 && a.empty() == ma.empty()); } }
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
    { int raw[10]; for (int& x : raw) x = -999; FixedStack s(raw + 1, 8); for (int i = 0; i < 8; i++) { bool ok = s.push(i); assert(ok); } bool r8 = s.push(8), r9 = s.push(9); assert(!r8 && !r9 && s.size() == 8 && raw[0] == -999 && raw[9] == -999); int v = 0; for (int i = 7; i >= 0; i--) { bool ok = s.pop(v); assert(ok && v == i); } }          // ①
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
// 검증: ① N 개를 올리고 모두 꺼내면 정확히 역순(LIFO) ② 빈 스택 pop 은 false 이고 상태 불변(그 뒤 push·pop 이 정상) ③ 소멸자 호출 수: pop 한 만큼 소멸하고 스택이 파괴되면 나머지도 소멸 ④ 복사가 던지는 타입에서 "값 반환 pop" 설계는 원소를 잃고 "top 후 pop" 설계는 보존 ⑤ std::stack 과 무작위 차분
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
    { Stack<int> s; for (int i = 0; i < 1000; i++) s.push(i); for (int i = 999; i >= 0; i--) { int t = s.top(); bool ok = s.pop(); assert(t == i && ok); } assert(s.size() == 0); }                                                             // ① LIFO
    { Stack<int> s; bool e1 = s.pop(); assert(!e1 && s.size() == 0); s.push(5); bool g1 = s.pop(), g2 = s.pop(); assert(g1 && !g2); }                                                                                                                  // ②
    { Fragile::live = 0; { Stack<Fragile> s; for (int i = 0; i < 6; i++) s.push(Fragile(i)); assert(Fragile::live == 6); s.pop(); s.pop(); assert(Fragile::live == 4 && s.size() == 4); } assert(Fragile::live == 0); }  // ③ 소멸 계수
    { Stack<Fragile> a, b; for (int i = 1; i <= 5; i++) { a.push(Fragile(i)); b.push(Fragile(i)); }
      Fragile::armed = true; bool threwA = false, threwB = false;
      try { Fragile r = a.popValueNaive(); (void)r; } catch (const std::runtime_error&) { threwA = true; }
      try { Fragile r = b.top(); (void)r; b.pop(); } catch (const std::runtime_error&) { threwB = true; }                                                                                                          // 복사 먼저(top), 성공해야 pop
      Fragile::armed = false; assert(threwA && threwB); assert(a.size() == 4 && a.top().v == 4);                                                                                                                  // ④ 값 반환 설계: 5 를 영영 잃었다
      assert(b.size() == 5 && b.top().v == 5); }                                                                                                                                                                      // 분리 설계: 5 가 그대로 남아 재시도 가능
    { std::mt19937 rng(8); std::stack<int> ref; Stack<int> s; for (int step = 0; step < 30000; step++) { if (rng() % 2) { int v = rng(); ref.push(v); s.push(v); } else { bool had = !ref.empty(); if (had) { assert(s.top() == ref.top()); ref.pop(); } bool got = s.pop(); assert(got == had); } assert(s.size() == ref.size()); } }       // ⑤
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
        else if (op == 2 && !ref.empty()) { int p = 0; bool okp = s.peek(p); assert(okp && p == ref.top()); int q = 0; bool okq = s.pop(q); assert(okq && q == p); ref.pop(); model.pop_back(); }                      // ⑤ peek 한 값이 pop 된다
        else { std::vector<int> before = s.snapshotTopFirst(); std::size_t n = s.size(); for (int t = 0; t < 5; t++) { int v; bool ok = s.peek(v); assert(ok == !ref.empty() && (!ok || v == ref.top())); std::size_t k = rng() % (n + 2); int w; bool ok2 = s.peekAt(k, w); assert(ok2 == (k < n) && (!ok2 || w == model[n - 1 - k])); } assert(s.snapshotTopFirst() == before && s.size() == n); }   // ① ② ④
        if (s.size() > 300) { int d; for (int i = 0; i < 150; i++) { s.pop(d); ref.pop(); model.pop_back(); } }
    }
    const ArrayStack& cs = s; int v; (void)cs.peek(v); (void)cs.peekAt(0, v);                                                                                                         // ③ const 접근
    ArrayStack empty; bool e1 = empty.peek(v), e2 = empty.peekAt(0, v); assert(!e1 && !e2);
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
// 검증: ① 참조로 제자리 수정이 스택에 반영된다 ② const 스택은 const 참조만 주고 원소가 여러 개여도 맨 위를 돌려준다 ③ 동적 배열 스택은 용량이 늘 때마다 원소 주소가 바뀌지만(바닥 원소의 주소 변화를 센다) 연결 스택의 첫 노드는 제자리이고 끝까지 pop 하면 모든 값이 역순으로 나온다(사슬 온전) ④ reserve 로 용량을 미리 잡으면 주소가 바뀌지 않음 ⑤ std::stack 의 top 과 일치(차분)
template <class T> class VectorStack {
    std::vector<T> a_;
public:
    void push(const T& v) { a_.push_back(v); } void pop() { a_.pop_back(); } bool empty() const { return a_.empty(); } std::size_t size() const { return a_.size(); }
    T& top() { return a_.back(); } const T& top() const { return a_.back(); } T& bottom() { return a_.front(); } void reserve(std::size_t n) { a_.reserve(n); }
};
template <class T> class LinkedStack {
    struct Node { T v; Node* next; }; Node* top_ = nullptr; std::size_t n_ = 0;
public:
    ~LinkedStack() { while (top_) { Node* t = top_; top_ = t->next; delete t; } }
    void push(const T& v) { top_ = new Node{v, top_}; ++n_; } void pop() { Node* t = top_; top_ = t->next; delete t; --n_; } bool empty() const { return top_ == nullptr; } std::size_t size() const { return n_; }
    T& top() { return top_->v; } const T& top() const { return top_->v; }
};
uintptr_t addr(const void* p) { return reinterpret_cast<uintptr_t>(p); }
int main() {
    { VectorStack<int> s; s.push(10); s.top() += 5; assert(s.top() == 15); s.push(20); s.top() *= 2; assert(s.top() == 40); s.pop(); assert(s.top() == 15); }                                      // ① 제자리 수정
    { VectorStack<int> s; s.push(1); s.push(2); s.push(3); const VectorStack<int>& cs = s; static_assert(std::is_same<decltype(cs.top()), const int&>::value, "const stack gives const reference"); assert(cs.top() == 3 && &cs.top() == &s.top()); }       // ② const 정확성
    { VectorStack<int> s; s.push(0); uintptr_t at = addr(&s.bottom()); int relocations = 0; for (int i = 1; i < 1000; i++) { s.push(i); if (addr(&s.bottom()) != at) { relocations++; at = addr(&s.bottom()); } } assert(relocations >= 5);       // ③ 배열 스택: 용량이 늘 때마다 모든 원소가 이사한다
      VectorStack<int> r; r.reserve(1000); r.push(0); uintptr_t fixed = addr(&r.bottom()); for (int i = 1; i < 1000; i++) { r.push(i); assert(addr(&r.bottom()) == fixed); }                                // ④ reserve 로 용량을 미리 잡으면 이사하지 않는다
      LinkedStack<int> l; l.push(0); int* pinned = &l.top(); for (int i = 1; i < 1000; i++) l.push(i); assert(*pinned == 0 && pinned != &l.top() && l.size() == 1000);
      const LinkedStack<int>& cl = l; static_assert(std::is_same<decltype(cl.top()), const int&>::value, "const linked stack gives const reference"); for (int i = 999; i >= 0; i--) { assert(!l.empty() && l.size() == (std::size_t)i + 1 && cl.top() == i && l.top() == i); l.pop(); } assert(l.empty() && l.size() == 0); }                                                    // 연결 스택: 첫 노드는 제자리, 참조가 계속 유효 (값을 읽어도 안전); 끝까지 pop 하며 999..0 이 차례로 나와야 사슬이 온전하다
    { std::stack<int> ref; VectorStack<int> s; for (int i = 0; i < 5000; i++) { int x = (i * 37) % 101; ref.push(x); s.push(x); assert(s.top() == ref.top()); if (i % 3 == 2) { ref.pop(); s.pop(); assert(s.top() == ref.top()); } } }          // ⑤
    std::cout << "Top: in-place modification through the reference works; reallocation moved the bottom of an array stack repeatedly but never the nodes of a linked stack, whose chain was popped back node by node in exact reverse order" << std::endl; return 0;
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
    { LinkedStack m; for (int i = 0; i < 1000; i++) m.push(i); m.visited = 0; bool e = m.empty(); assert(!e && m.visited == 0); m.visited = 0; std::size_t w = m.sizeByWalking(); assert(w == 1000 && m.visited == 1000); }               // ② empty 는 O(1), 카운터 없는 size 는 O(N)
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
        for (std::size_t i = 0; i < cap; i++) { bool nf = !s.full(), ok = s.push((int)i); assert(nf && ok); } assert(s.full() && s.size() == cap);                                                          // ① 정확히 cap 개
        bool over = s.push(-1); assert(!over && s.size() == cap && s.full()); int v = 0; if (cap) { bool got = s.pop(v); assert(got && v == (int)cap - 1 && !s.full()); bool again = s.push(7); assert(again && s.full()); }                       // ② pop 하면 거짓, 다시 push 하면 참
    }
    { LimitedStack s(100); for (int i = 0; i < 100; i++) s.push(i); assert(s.full()); bool threw = false; try { s.push(100); } catch (const std::length_error&) { threw = true; } assert(threw && s.size() == 100); }       // ④
    { TwoStacks t(10); int pushed = 0; for (int i = 0; i < 100 && !t.full(); i++) { if (i % 3) t.push1(i); else t.push2(i); pushed++; } bool x1 = t.push1(0), x2 = t.push2(0); assert(pushed == 10 && t.size1() + t.size2() == 10 && !x1 && !x2);          // ⑤ 합이 용량이 되는 순간만 가득
      TwoStacks u(10); for (int i = 0; i < 10; i++) { bool ok = u.push1(i); assert(ok); } assert(u.size1() == 10 && u.size2() == 0 && u.full()); }                                                               // 한쪽이 전부 써도 된다
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
// 검증: ① 카운터형 연결 스택의 size() 가 무작위 push/pop 에서 항상 std::stack::size() 와 같고 방문 노드가 0 개 ② 세는 방식은 size() 마다 N 개를 방문 ③ 실패한 연산(상한 500 에서 거절된 push, 빈 스택의 pop)은 크기를 바꾸지 않고 거절 여부는 상한을 아는 std::stack 오라클과 일치하며 두 경우가 실제로 일어난다(오르막·내리막 걸음을 번갈아 상한과 빈 상태에 닿는다) ④ clear 후 0 ⑤ 불변식(성공 push − 성공 pop)이 항상 성립
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
    std::mt19937 rng(11); LinkedStack s(500); std::stack<int> ref; long okPush = 0, okPop = 0, refusedPush = 0, refusedPop = 0; int sink = 0;
    for (int step = 0; step < 100000; step++) {
        std::size_t before = s.size(); bool up = ((step / 2500) % 2 == 1) ? rng() % 10 < 7 : rng() % 10 < 3;                                                      // 2500 걸음마다 오르막(push 70%)과 내리막(30%)을 번갈아 상한 500 과 빈 상태에 모두 닿는다
        if (up) { bool ok = s.push(step); assert(ok == (ref.size() < 500)); if (ok) { ref.push(step); okPush++; } else { refusedPush++; assert(s.size() == before && before == 500); } }                                              // ③ 가득 찬 push 는 크기 불변
        else { bool ok = s.pop(sink); assert(ok == !ref.empty()); if (ok) { assert(sink == ref.top()); ref.pop(); okPop++; } else { refusedPop++; assert(s.size() == before && before == 0); } }                                                                  // ③ 빈 pop 도 크기 불변
        assert(s.size() == ref.size() && (long)s.size() == okPush - okPop);                                                                                                                // ① ⑤
    }
    assert(refusedPush > 0 && refusedPop > 0);
    s.resetWalked(); for (int i = 0; i < 1000; i++) (void)s.size(); assert(s.walked() == 0);                                                                                               // O(1): 노드 방문 0
    s.resetWalked(); std::size_t n = s.size(); for (int i = 0; i < 10; i++) { std::size_t c = s.sizeByCounting(); assert(c == n); } assert(s.walked() == (long)(10 * n));                                          // ② 세는 방식은 호출마다 N
    s.clear(); std::size_t c0 = s.sizeByCounting(); assert(s.size() == 0 && c0 == 0);                                                                                                                         // ④
    std::cout << "Size: counter-based size() matched std::stack::size() and the push-minus-pop invariant over 100000 operations (" << refusedPush << " pushes refused at the cap of 500, " << refusedPop << " pops refused when empty); counting by walking cost " << 10 * n << " node visits for 10 calls versus 0" << std::endl; return 0;
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
//  ⑥ 무작위 연산 2 만 번(푸시 95% / 비우기 5%)에서 매 단계 크기가 모형과 같고 *살아 있는 객체 수 = 크기 + 원본 하나* 가 늘 성립(생성 − 소멸), 마지막에 모두 소멸
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
    {   std::mt19937 rng(9); Tracked::ctor = Tracked::dtor = 0;                                                                                                                         // ⑥ 무작위 대조
        { ArrayStack<Tracked> s; Tracked proto; std::size_t model = 0; long clears = 0;
            for (int step = 0; step < 20000; ++step) { if (rng() % 20 == 0) { s.clear(); model = 0; ++clears; } else { s.push(proto); ++model; } assert(s.size() == model && Tracked::ctor - Tracked::dtor == (long)model + 1); }
            assert(clears > 500); }
        assert(Tracked::ctor == Tracked::dtor); }
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
// 검증: ① 무작위 push/pop 을 std::vector 모델과 대조(내용·크기·가득/빈·peek 이 돌려주는 값) ② 복사본은 독립적(원본을 바꿔도 복사본 불변, 복사본을 바꿔도 원본 불변) ③ 자기 대입 안전 ④ 이동 후 원본이 빈 스택 ⑤ at 의 범위 검사와 순회 순서 ⑥ swap
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
        int p = 0; bool pk = s.peek(p); assert(pk == !model.empty() && (!pk || p == model.back()) && s.size() == model.size() && s.empty() == model.empty() && s.full() == (model.size() == 64));                               // ①
        if (step % 5000 == 0) assert(std::vector<int>(s.begin(), s.end()) == model);                                                                                                   // ⑤ 바닥 -> 위 순서
    }
    { ArrayStack a(8); for (int i = 0; i < 5; i++) a.push(i); ArrayStack b(a); int v; a.pop(v); a.push(100); assert(std::vector<int>(b.begin(), b.end()) == (std::vector<int>{0, 1, 2, 3, 4}) && a.at(4) == 100);          // ② 복사본은 독립
      b.push(7); assert(a.size() == 5 && b.size() == 6 && a.at(4) == 100);
      ArrayStack c(2); c = a; assert(std::vector<int>(c.begin(), c.end()) == std::vector<int>(a.begin(), a.end()) && c.capacity() == 8);                                         // 복사 대입
      c = c; assert(c.size() == 5); }                                                                                                                                                      // ③ 자기 대입
    { ArrayStack a(4); a.push(1); a.push(2); ArrayStack b(std::move(a)); bool r9 = a.push(9); assert(a.empty() && a.capacity() == 0 && !r9 && b.size() == 2); ArrayStack c(1); c = std::move(b); assert(b.empty() && c.size() == 2 && c.capacity() == 4); }     // ④ 이동
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
// 검증: ① std::stack 과 무작위 차분 ② 불변식이 매 연산 뒤에 성립 ③ 적대적 열(가득 찬 경계에서 push/pop 교대)에서 성장 한 번의 이동(1024)뿐 더는 이동하지 않음 ④ 1/2 규칙으로 줄이는 변형은 같은 열에서 연산당 Θ(N) ⑤ N 번 push 의 총 이동 < 2N, 비운 뒤 용량이 최소값으로 돌아감 ⑥ 2000 개까지 키웠다가 모두 꺼내며 매 값과 용량(원소 수에 맞는 2 의 거듭제곱이고, 줄어드는 것은 크기 ≤ 용량/4 가 되는 pop 에서만)을 확인 ⑦ 최소 용량 4 에서는 push·pop 을 반복해도 이동이 0
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
    { std::mt19937 rng(6); DynamicStack s; std::stack<int> ref; int v; for (int step = 0; step < 100000; step++) { if (rng() % 5 < 2 || ref.empty()) { int x = rng(); s.push(x); ref.push(x); } else { assert(s.top() == ref.top()); bool ok = s.pop(v); assert(ok && v == ref.top()); ref.pop(); } assert(s.size() == ref.size() && s.invariant()); } }          // ① ②
    { DynamicStack s; int v; for (int i = 0; i < 1024; i++) s.push(i); long before = s.moved(); const int OPS = 20000; for (int i = 0; i < OPS; i++) { s.push(i); bool ok = s.pop(v); assert(ok && v == i); } assert(s.moved() - before == 1024 && s.capacity() == 2048); }        // ③ 적대적 열: 경계에서 push/pop 교대 (1/4 규칙은 이동 0)
    { DynamicStack half(0.5); int v; for (int i = 0; i < 1024; i++) half.push(i); half.push(0); half.pop(v); long before = half.moved(); const int OPS = 2000; for (int i = 0; i < OPS; i++) { half.push(i); half.pop(v); } assert(half.moved() - before > 100L * OPS); std::cout << "1/2-rule moves per push+pop pair: " << (half.moved() - before) / OPS << "; "; }       // ④ 1/2 규칙은 push+pop 한 쌍마다 천 번 넘게 이동
    { DynamicStack s; const int N = 100000; for (int i = 0; i < N; i++) s.push(i); assert(s.moved() < 2L * N); int v; while (s.size()) s.pop(v); assert(s.capacity() == 4 && s.invariant()); }                                                         // ⑤ 총 이동 < 2N, 비우면 최소 용량
    {   DynamicStack s; std::stack<int> ref; std::size_t expCap = 4; int v = 0; const int N = 2000;                                                                              // ⑥ 2000 개까지 키웠다가 모두 꺼낸다 (용량 4 -> 2048 -> 4)
        for (int i = 0; i < N; i++) { int x = i * 7 + 3; s.push(x); ref.push(x); if (ref.size() > expCap) expCap *= 2; assert(s.top() == ref.top() && s.size() == ref.size() && s.capacity() == expCap && s.invariant()); }
        assert(expCap == 2048 && s.capacity() == 2048);
        while (!ref.empty()) { std::size_t capBefore = s.capacity(); int want = ref.top(); bool ok = s.pop(v); assert(ok && v == want); ref.pop(); bool shrink = capBefore > 4 && ref.size() <= capBefore / 4;
            assert(s.capacity() == (shrink ? capBefore / 2 : capBefore) && s.size() == ref.size() && s.invariant()); if (!ref.empty()) assert(s.top() == ref.top()); }
        assert(s.capacity() == 4 && s.size() == 0); }
    { DynamicStack s; int v = 0; for (int round = 0; round < 50; round++) { for (int i = 0; i < 4; i++) s.push(i); for (int i = 0; i < 4; i++) { bool ok = s.pop(v); assert(ok && v == 3 - i); } } assert(s.moved() == 0 && s.capacity() == 4 && s.size() == 0); }          // ⑦ 최소 용량에서는 키우지도 줄이지도 않아 이동 0
    std::cout << "DynamicStack: matched std::stack over 100000 operations and a 2000-element grow-and-drain with the capacity invariant and the exact shrink moments intact; after one growth the 1/4 shrink rule moved no further elements on the adversarial boundary sequence" << std::endl; return 0;
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
    { std::mt19937 rng(12); LinkedStack s; std::stack<int> ref; int v; for (int step = 0; step < 60000; step++) { if (rng() % 2) { int x = rng(); s.push(x); ref.push(x); } else { bool ok = s.pop(v); assert(ok == !ref.empty()); if (ok) { assert(v == ref.top()); ref.pop(); } } int p = 0; bool pk = s.peek(p); assert(pk == !ref.empty() && (!pk || p == ref.top()) && s.size() == ref.size() && s.empty() == ref.empty()); assert((std::size_t)LinkedStack::liveNodes() == s.size()); } }   // ① ②
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
#include <random>
#include <vector>
#include <cassert>

// 노드 단위 푸시(PushNode): 연결 스택의 push 를 포인터 조작 수준에서 본다. 머리 포인터가 가리키는 리스트의 맨 앞에 새 노드를 달려면 ① 새 노드를 만들고 ② 새 노드의 next 를 옛 머리로 ③ 머리를 새 노드로 — 이 순서가 중요하다. ③ 을 먼저 하면 옛 머리를 잃어 리스트 전체를 누수한다.
// 예외 안전: 할당(① )이 실패하면 아직 아무것도 바꾸지 않았으므로 머리는 그대로다 — 강한 보장. 그래서 new 를 가장 먼저 하고 포인터 대입은 마지막에 한다. 노드를 만든 뒤에는 실패할 수 있는 연산이 없다.
// 검증: ① 무작위로 푸시한 뒤 머리부터 순회한 값이 푸시의 역순이고 길이가 맞다 ② 순환(cycle)이 없음 — 토끼와 거북이(Floyd)로 확인 ③ 할당 실패를 k 번째 new 에서 주입하면 머리와 리스트 내용이 그대로이고 누수 노드 0 ④ 올바른 순서와 틀린 순서의 차이: 틀린 순서(③ 먼저)는 옛 리스트를 잃는다는 것을 도달 가능 노드 수로 보임
//  ⑥ 무작위 푸시 2 만 번 중 1/40 은 새 노드 할당이 실패하도록 주입: 실패한 호출은 머리를 바꾸지 않았고 성공한 호출만 std::vector 모형에 쌓였는지(머리부터 걸으면 모형의 역순) 500 번마다 대조, 끝에 노드가 모두 반환됨
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
    {   std::mt19937 rng(12); Node* head = nullptr; std::vector<int> model; long failures = 0;                                                                                          // ⑥ 무작위 대조와 실패 주입
        for (int step = 0; step < 20000; ++step) { bool inject = rng() % 40 == 0; int v = (int)(rng() % 1000); allocCount = 0; failAt = inject ? 1 : -1; bool threw = false;
            try { pushNode(head, v); } catch (const std::bad_alloc&) { threw = true; } failAt = -1; assert(threw == inject);
            if (threw) ++failures; else model.push_back(v);
            if (step % 500 == 0) { std::vector<int> walk; for (Node* p = head; p; p = p->next) walk.push_back(p->data); assert(std::vector<int>(walk.rbegin(), walk.rend()) == model); } }
        std::vector<int> walk; for (Node* p = head; p; p = p->next) walk.push_back(p->data); assert(std::vector<int>(walk.rbegin(), walk.rend()) == model && failures > 100 && !hasCycle(head)); freeAll(head); assert(liveNodes == 0); }
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
#include <random>
#include <vector>
#include <cassert>

// 노드 단위 팝(PopNode): 연결 스택의 pop 을 포인터 조작 수준에서 본다. 순서: ① 떼어 낼 노드를 임시 포인터에 기억 ② 머리를 다음 노드로 이동 ③ 값을 꺼내고 ④ 노드를 해제. ④ 를 ② 보다 먼저 하면 해제된 노드의 next 를 읽게 되어(use-after-free) 정의되지 않은 동작이다 — 해제 직전에 필요한 값(next, data)을 모두 꺼내 두는 것이 규칙이다.
// 빈 리스트(head == nullptr)는 거절해야 한다. 또 하나의 기법은 "떼어 내되 해제하지 않고 돌려주기"(detach): 노드를 자유 리스트에 모아 두었다가 다음 push 에서 재사용하면 new/delete 를 줄인다(메모리 풀의 시작). 자유 리스트도 같은 연결 스택이다.
// 검증: ① 모든 노드를 팝하면 정확히 푸시의 역순이고 마지막에 head == nullptr ② 빈 리스트 팝은 false 이며 출력 인자를 건드리지 않음 ③ 팝마다 노드 하나만 해제(살아 있는 노드 수 −1) ④ detach/reuse: 떼어 낸 노드를 자유 리스트에 넣고 다시 쓰면 같은 주소가 LIFO 로 재사용되고 새 할당이 없음 ⑤ 해제 전에 next 를 읽는 올바른 순서
//  ⑥ 무작위 푸시(60%)/팝(40%) 5 만 번을 std::vector 모형과 대조: 팝은 모형의 마지막 값을 돌려주고 빈 스택의 팝은 출력 인자를 건드리지 않으며, 생존 노드 수는 늘 모형의 크기와 같다
struct Node { int data; Node* next; };
static long liveNodes = 0, newCalls = 0;
Node* makeNode(int x, Node* next) { newCalls++; liveNodes++; return new Node{x, next}; }
bool popNode(Node*& head, int& out) {                                                          // 올바른 순서: 기억 -> 이동 -> 값 -> 해제
    if (!head) return false; Node* t = head; head = t->next; out = t->data; delete t; liveNodes--; return true;
}
Node* detachTop(Node*& head) { if (!head) return nullptr; Node* t = head; head = t->next; t->next = nullptr; return t; }              // 해제하지 않고 돌려준다
void attach(Node*& head, Node* n) { n->next = head; head = n; }
int main() {
    { Node* head = nullptr; for (int i = 0; i < 1000; i++) head = makeNode(i, head); int v = 0; for (int i = 999; i >= 0; i--) { long before = liveNodes; bool ok = popNode(head, v); assert(ok && v == i && liveNodes == before - 1); } assert(head == nullptr && liveNodes == 0); }          // ① ③
    { Node* head = nullptr; int v = 777; bool ok = popNode(head, v); assert(!ok && v == 777 && head == nullptr); }                                                                                                                                                                  // ②
    { Node* used = nullptr; Node* freeList = nullptr; for (int i = 0; i < 5; i++) used = makeNode(i, used); std::vector<Node*> addrs; for (Node* p = used; p; p = p->next) addrs.push_back(p);        // addrs[0] 이 top
      for (int i = 0; i < 3; i++) attach(freeList, detachTop(used));                                                                                                                                                                                              // 노드 3 개를 free list 로 옮김 (해제 없음)
      long newBefore = newCalls; for (int i = 0; i < 3; i++) { Node* n = detachTop(freeList); n->data = 100 + i; attach(used, n); }                                                                                                                              // 재사용: 새 할당 없음
      assert(newCalls == newBefore && used == addrs[0] /* 스택을 두 번 거꾸로 옮기면(used -> free -> used) 원래 주소 순서가 복원된다 */ ); int v; while (popNode(used, v)) {} assert(liveNodes == 0); }                                                                    // ④
    { Node* head = makeNode(1, makeNode(2, nullptr)); Node* t = head; Node* nextBeforeFree = t->next; int dataBeforeFree = t->data; head = nextBeforeFree; delete t; liveNodes--; assert(head->data == 2 && dataBeforeFree == 1); int v; popNode(head, v); assert(liveNodes == 0); }          // ⑤ 해제 전에 next/data 를 먼저 읽어 둔다
    {   std::mt19937 rng(14); Node* head = nullptr; std::vector<int> model; long base = liveNodes, empties = 0;                                                                         // ⑥ 무작위 대조
        for (int step = 0; step < 50000; ++step) {
            if (rng() % 5 < 3) { int v = (int)(rng() % 1000); head = makeNode(v, head); model.push_back(v); }
            else { int out = -7; bool got = popNode(head, out); assert(got == !model.empty()); if (got) { assert(out == model.back()); model.pop_back(); } else { assert(out == -7); ++empties; } }
            assert(liveNodes - base == (long)model.size() && (head == nullptr) == model.empty()); }
        int v; while (popNode(head, v)) model.pop_back(); assert(model.empty() && liveNodes == base && empties > 0); }
    std::cout << "PopNode: pops returned the exact reverse order and released one node each; empty pops were refused; detached nodes were recycled through a free list with zero new allocations" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 4. 대표 활용
## ReverseString()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <sstream>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 문자열 뒤집기(ReverseString): 스택은 넣은 순서의 반대로 꺼내므로 문자를 차례로 push 한 뒤 모두 pop 하면 뒤집힌 문자열이 된다. 그런데 "문자" 가 무엇인가가 실무의 함정이다. std::string 의 원소는 바이트이고, UTF-8 한글은 한 글자가 3 바이트다. 바이트 단위로 뒤집으면 한 글자의 3 바이트 순서가 거꾸로 되어 올바르지 않은 UTF-8(깨진 글자)이 된다.
// 올바른 방법은 코드 포인트(글자) 단위로 스택에 넣는 것이다. UTF-8 은 첫 바이트의 상위 비트로 길이를 알려 주므로(0xxxxxxx = 1, 110xxxxx = 2, 1110xxxx = 3, 11110xxx = 4 바이트) 글자를 잘라 스택에 넣고 거꾸로 이어 붙이면 된다. 같은 기법으로 문장의 단어 순서를 뒤집는 것도 스택 문제다(공백으로 단어를 나눠 push, pop 하며 잇기).
// 검증: ① 무작위 ASCII 문자열에서 스택 방식 == std::reverse ② 한글·혼합 문자열의 글자 단위 뒤집기가 정답과 같다 ③ 바이트 단위 뒤집기는 한글에서 올바르지 않은 UTF-8 을 만들고 글자 단위는 항상 올바름 ④ 두 번 뒤집으면 원본(항등) ⑤ 단어 순서 뒤집기와 그 항등성
std::vector<std::string> splitCodePoints(const std::string& s) {                                   // UTF-8 을 글자 단위로 자른다 (잘못된 바이트는 한 바이트씩)
    std::vector<std::string> out; for (size_t i = 0; i < s.size();) { unsigned char c = s[i]; size_t n = c < 0x80 ? 1 : (c >> 5) == 6 ? 2 : (c >> 4) == 14 ? 3 : (c >> 3) == 30 ? 4 : 1; if (i + n > s.size()) n = 1; out.push_back(s.substr(i, n)); i += n; } return out;
}
bool validUtf8(const std::string& s) {
    for (size_t i = 0; i < s.size();) { unsigned char c = s[i]; size_t n = c < 0x80 ? 1 : (c >> 5) == 6 ? 2 : (c >> 4) == 14 ? 3 : (c >> 3) == 30 ? 4 : 0; if (!n || i + n > s.size()) return false; for (size_t k = 1; k < n; k++) if (((unsigned char)s[i + k] >> 6) != 2) return false; i += n; } return true;
}
std::string reverseBytes(const std::string& s) { std::stack<char> st; for (char c : s) st.push(c); std::string r; while (!st.empty()) { r += st.top(); st.pop(); } return r; }
std::string reverseChars(const std::string& s) { std::stack<std::string> st; for (auto& cp : splitCodePoints(s)) st.push(cp); std::string r; while (!st.empty()) { r += st.top(); st.pop(); } return r; }
std::string reverseWords(const std::string& s) { std::stack<std::string> st; std::istringstream in(s); std::string w; while (in >> w) st.push(w); std::string r; while (!st.empty()) { r += st.top(); st.pop(); if (!st.empty()) r += ' '; } return r; }
int main() {
    std::mt19937 rng(8);
    for (int t = 0; t < 500; t++) { std::string s; int n = rng() % 40; for (int i = 0; i < n; i++) s += (char)(32 + rng() % 95); std::string want = s; std::reverse(want.begin(), want.end()); assert(reverseBytes(s) == want && reverseChars(s) == want); }                  // ①
    assert(reverseChars("안녕하세요") == "요세하녕안" && reverseChars("가나다 abc") == "cba 다나가" && reverseChars("") == "" && reverseChars("a") == "a");                                                               // ②
    assert(validUtf8("안녕") && !validUtf8(reverseBytes("안녕")) && validUtf8(reverseChars("안녕")));                                                                                                              // ③ 바이트 단위는 깨진다
    const std::vector<std::string> alphabet = {"a", "Z", "7", " ", "가", "힣", "é", "😀", "한"}; int broken = 0;
    for (int t = 0; t < 300; t++) { std::string s; int n = rng() % 12; for (int i = 0; i < n; i++) s += alphabet[rng() % alphabet.size()]; std::string r = reverseChars(s); assert(validUtf8(r) && reverseChars(r) == s && splitCodePoints(r).size() == splitCodePoints(s).size()); broken += !validUtf8(reverseBytes(s)); }      // ③ ④
    assert(broken > 50);
    assert(reverseWords("the sky is blue") == "blue is sky the" && reverseWords("  hello   world  ") == "world hello" && reverseWords(reverseWords("a bb ccc dddd")) == "a bb ccc dddd");                                         // ⑤
    std::cout << "ReverseString: stack reversal matched std::reverse on ASCII; byte-wise reversal produced invalid UTF-8 for " << broken << " of 300 mixed Korean/emoji strings while code-point reversal never did" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## BalancedParentheses()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <utility>
#include <cassert>

// 괄호 검사(BalancedParentheses): 괄호가 올바르게 짝지어졌는가. 여는 괄호는 push, 닫는 괄호는 스택 top 의 짝인지 확인하고 pop. 괄호가 아닌 문자는 건너뛴다. 가장 최근에 연 것을 가장 먼저 닫아야 하는 구조 자체가 후입선출이다.
// 단순히 true/false 만 돌려주면 쓸모가 적다. 컴파일러처럼 "어디가, 왜 잘못인가" 를 알려야 한다: ① 닫는 괄호가 남는 경우(UNMATCHED_CLOSER, 위치) ② 종류가 다른 경우 "(]" (MISMATCH, 위치) ③ 끝까지 닫히지 않은 경우(UNCLOSED, 가장 오래된 열린 괄호의 위치). 첫 오류 위치는 앞에서부터 읽을 때 "이 접두사로는 어떤 올바른 문자열도 만들 수 없게 되는 첫 지점" 이다.
// 괄호가 한 종류뿐이면 스택 없이 카운터 하나로 충분하다(깊이). 여러 종류에서는 어느 괄호가 열려 있는지 알아야 하므로 스택이 꼭 필요하다.
// 검증(스택을 쓰지 않는 독립 기준 구현: 재귀 하강 파서): 알파벳 {( ) [ ] { } a} 로 길이 7 이하의 모든 문자열(약 96 만 개)에서 상태와 오류 위치가 기준 구현과 같고, 한 종류 괄호는 카운터 방식과 같으며, 무작위 긴 문자열에서도 일치한다
enum Status { OK, UNMATCHED_CLOSER, MISMATCH, UNCLOSED };
struct Result { Status status; size_t pos; bool operator==(const Result& o) const { return status == o.status && pos == o.pos; } };
char opener(char c) { return c == ')' ? '(' : c == ']' ? '[' : c == '}' ? '{' : 0; }
Result check(const std::string& s) {
    std::stack<std::pair<char, size_t>> st;
    for (size_t i = 0; i < s.size(); i++) { char c = s[i];
        if (c == '(' || c == '[' || c == '{') st.push({c, i});
        else if (opener(c)) { if (st.empty()) return {UNMATCHED_CLOSER, i}; if (st.top().first != opener(c)) return {MISMATCH, i}; st.pop(); } }
    if (st.empty()) return {OK, 0};
    size_t oldest = 0; while (!st.empty()) { oldest = st.top().second; st.pop(); } return {UNCLOSED, oldest};                       // 스택 맨 아래 = 가장 오래된 열린 괄호
}
char closerOf(char c) { return c == '(' ? ')' : c == '[' ? ']' : '}'; }
Result descend(const std::string& s, size_t& i, char need) {                                       // 기준 구현: 재귀 하강 (스택 대신 호출 스택을 쓴다)
    while (i < s.size()) { char c = s[i];
        if (c == '(' || c == '[' || c == '{') { size_t at = i++; Result r = descend(s, i, closerOf(c)); if (r.status == UNCLOSED) r.pos = at; if (r.status != OK) return r; }          // 바깥 프레임이 나중에 덮어쓰므로 가장 오래된 열린 괄호의 위치가 남는다
        else if (opener(c)) { if (!need) return {UNMATCHED_CLOSER, i}; if (c != need) return {MISMATCH, i}; i++; return {OK, 0}; }
        else i++; }
    return need ? Result{UNCLOSED, 0} : Result{OK, 0};
}
Result reference(const std::string& s) { size_t i = 0; return descend(s, i, 0); }
int main() {
    const char alpha[] = {'(', ')', '[', ']', '{', '}', 'a'}; long strings = 0, ok = 0, unclosed = 0, unmatched = 0, mismatch = 0;
    for (int len = 0; len <= 7; len++) { long total = 1; for (int i = 0; i < len; i++) total *= 7;
        for (long code = 0; code < total; code++) { std::string s; long c = code; for (int i = 0; i < len; i++) { s += alpha[c % 7]; c /= 7; }
            Result a = check(s), b = reference(s); strings++; assert(a == b);                                                                                           // 상태와 오류 위치(UNCLOSED 는 가장 오래된 열린 괄호) 모두 일치
            ok += a.status == OK; unclosed += a.status == UNCLOSED; unmatched += a.status == UNMATCHED_CLOSER; mismatch += a.status == MISMATCH; } }
    std::mt19937 rng(3);
    for (int t = 0; t < 3000; t++) { std::string s; int n = rng() % 30; for (int i = 0; i < n; i++) s += alpha[rng() % 7]; assert(check(s) == reference(s));
        std::string one; for (char c : s) if (c == '(' || c == ')' || c == 'a') one += c; int depth = 0; bool never = true; for (char c : one) { if (c == '(') depth++; else if (c == ')') { if (--depth < 0) never = false; } } assert((never && depth == 0) == (check(one).status == OK)); }   // 한 종류는 카운터 하나로 충분
    assert(check("{[()]}").status == OK && check("(]") == (Result{MISMATCH, 1}) && check("())") == (Result{UNMATCHED_CLOSER, 2}) && check("(()") == (Result{UNCLOSED, 0}) && check("a+(b*[c-d])/e").status == OK);
    std::cout << "BalancedParentheses: " << strings << " exhaustive strings (length <= 7) agreed with the recursive-descent reference - OK " << ok << ", unmatched closer " << unmatched << ", mismatch " << mismatch << ", unclosed " << unclosed << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N) (한 종류 괄호는 O(1))
```
## InfixToPostfix()
### 대표코드
```cpp
#include <cctype>
#include <cmath>
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 중위 → 후위 변환(InfixToPostfix, 다익스트라의 션팅 야드 알고리즘): 사람이 쓰는 중위 표기 "1+2*3" 을 괄호와 우선순위가 필요 없는 후위 표기 "1 2 3 * +" 로 바꾼다. 연산자 스택을 쓴다. 규칙: ① 피연산자는 바로 출력 ② 연산자 o 는 스택 top 이 o 보다 우선순위가 높거나(같고 o 가 좌결합이면) 먼저 꺼내 출력한 뒤 o 를 push ③ 여는 괄호는 push, 닫는 괄호는 여는 괄호가 나올 때까지 pop 해 출력 ④ 끝에 스택을 비운다.
// 결합법칙: a-b-c 는 (a-b)-c 로 좌결합, a^b^c 는 a^(b^c) 로 우결합이다. 우결합 연산자는 같은 우선순위의 top 을 꺼내지 않고 쌓는다. 단항 마이너스(−x)는 이항 연산자 바로 뒤나 여는 괄호 뒤, 식의 맨 앞에 오는 '−' 이며 접두 연산자라 아무것도 꺼내지 않고 push 한다. 이 구현의 단항 마이너스 우선순위는 곱셈보다 높고 ^ 보다 낮다(-2^2 = -(2^2)).
// 오류도 알려야 한다: 짝이 맞지 않는 괄호, 피연산자 자리에 연산자가 오는 것(1+*2), 연산자가 모자란 것(1 2), 빈 식. 토큰은 여러 자리 정수를 지원한다.
// 검증: 무작위 식 트리를 만들어 ① 최소 괄호의 중위 문자열로 쓰고(공백·불필요한 괄호도 섞어) 변환한 결과가 트리의 후위 순회와 정확히 같다(좌/우결합·우선순위·단항 포함) ② 여러 자리 정수 ③ 오류 사례들이 모두 거절된다 ④ 변환한 후위식을 계산하면 트리 값과 같고, 우선순위 표와 스택을 전혀 쓰지 않는 재귀 하강 계산기(독립 오라클)가 중위 문자열을 바로 계산한 값·실패 여부와도 같다(표가 틀리면 생성기·변환기가 같이 틀려도 여기서 드러난다) ⑤ 우선순위 표를 손으로 쓴 후위식으로 직접 확인(%·좌결합 + -·^ 와 * 의 단계·단항 마이너스는 곱셈보다 먼저)
struct E { char op; long long v; int l, r; };                                                 // op: '#' 숫자, 'n' 단항 마이너스, 그 외 이항 + - * / % ^
int prec(char o) { return o == '+' || o == '-' ? 1 : o == '*' || o == '/' || o == '%' ? 2 : o == 'n' ? 3 : o == '^' ? 4 : 0; }
bool rightAssoc(char o) { return o == '^'; }
int gen(std::vector<E>& pool, int depth, std::mt19937& rng) {
    if (depth == 0 || rng() % 4 == 0) { pool.push_back({'#', (long long)(rng() % 120), -1, -1}); return (int)pool.size() - 1; }
    if (rng() % 8 == 0) { int c = gen(pool, depth - 1, rng); pool.push_back({'n', 0, c, -1}); return (int)pool.size() - 1; }
    const char ops[] = {'+', '-', '*', '/', '%', '^'}; char o = ops[rng() % 6]; int l = gen(pool, depth - 1, rng); int r;
    if (o == '^') { auto lit = [&]() { pool.push_back({'#', (long long)(rng() % 4), -1, -1}); return (int)pool.size() - 1; }; r = lit(); if (rng() % 3 == 0) { int x = lit(); pool.push_back({'^', 0, r, x}); r = (int)pool.size() - 1; } }          // 지수는 작은 수 또는 a^b (a^b^c 의 우결합 중첩)
    else r = gen(pool, depth - 1, rng);
    pool.push_back({o, 0, l, r}); return (int)pool.size() - 1;
}
std::string infixOf(const std::vector<E>& p, int i, std::mt19937& rng) {                       // 최소 괄호 (가끔 불필요한 괄호·공백 추가)
    const E& e = p[i]; if (e.op == '#') return std::to_string(e.v);
    auto wrap = [&](int c, bool paren) { std::string s = infixOf(p, c, rng); if (paren || rng() % 10 == 0) s = "(" + s + ")"; return s; };
    if (e.op == 'n') return "-" + wrap(e.l, prec(p[e.l].op) < 3 && p[e.l].op != '#');
    bool lp = p[e.l].op != '#' && (prec(p[e.l].op) < prec(e.op) || (prec(p[e.l].op) == prec(e.op) && rightAssoc(e.op)));
    bool rp = p[e.r].op != '#' && (prec(p[e.r].op) < prec(e.op) || (prec(p[e.r].op) == prec(e.op) && !rightAssoc(e.op)));
    std::string sp = rng() % 3 == 0 ? " " : ""; return wrap(e.l, lp) + sp + e.op + sp + wrap(e.r, rp);
}
void postfixOf(const std::vector<E>& p, int i, std::vector<std::string>& out) { const E& e = p[i]; if (e.op == '#') { out.push_back(std::to_string(e.v)); return; } postfixOf(p, e.l, out); if (e.op != 'n') postfixOf(p, e.r, out); out.push_back(e.op == 'n' ? "~" : std::string(1, e.op)); }
bool toPostfix(const std::string& s, std::vector<std::string>& out) {                           // 실패하면 false
    out.clear(); std::stack<char> st; bool expectOperand = true; int open = 0;
    for (size_t i = 0; i < s.size();) { char c = s[i];
        if (c == ' ') { i++; continue; }
        if (isdigit((unsigned char)c)) { if (!expectOperand) return false; size_t j = i; while (j < s.size() && isdigit((unsigned char)s[j])) j++; out.push_back(s.substr(i, j - i)); i = j; expectOperand = false; continue; }
        if (c == '(') { if (!expectOperand) return false; st.push(c); open++; i++; continue; }
        if (c == ')') { if (expectOperand || open == 0) return false; while (st.top() != '(') { out.push_back(std::string(1, st.top() == 'n' ? '~' : st.top())); st.pop(); } st.pop(); open--; i++; continue; }
        if (std::string("+-*/%^").find(c) == std::string::npos) return false;
        if (expectOperand) { if (c != '-') return false; st.push('n'); i++; continue; }                         // 접두 단항 마이너스: 아무것도 꺼내지 않는다
        while (!st.empty() && st.top() != '(' && (prec(st.top()) > prec(c) || (prec(st.top()) == prec(c) && !rightAssoc(c)))) { out.push_back(std::string(1, st.top() == 'n' ? '~' : st.top())); st.pop(); }
        st.push(c); expectOperand = true; i++; }
    if (expectOperand || open != 0) return false;
    while (!st.empty()) { out.push_back(std::string(1, st.top() == 'n' ? '~' : st.top())); st.pop(); } return true;
}
bool applyOp(char o, long long a, long long b, long long& r) {                              // 이항 연산 하나 (0 으로 나누기·음수 지수·넘침은 실패)
    if (o == '+') r = a + b; else if (o == '-') r = a - b; else if (o == '*') { if (std::fabs((long double)a * (long double)b) > 1e15L) return false; r = a * b; } else if (o == '/') { if (!b) return false; r = a / b; } else if (o == '%') { if (!b) return false; r = a % b; } else { if (b < 0) return false; r = 1; for (long long k = 0; k < b; k++) { if (std::fabs((long double)r * (long double)a) > 1e15L) return false; r *= a; } }
    return !(r > (1LL << 50) || r < -(1LL << 50));
}
bool evalPostfix(const std::vector<std::string>& t, long long& result) {
    std::vector<long long> st;
    for (auto& tok : t) { if (isdigit((unsigned char)tok[0])) { st.push_back(std::stoll(tok)); continue; } if (tok == "~") { if (st.empty()) return false; st.back() = -st.back(); continue; } if (st.size() < 2) return false;
        long long b = st.back(); st.pop_back(); long long a = st.back(); long long r = 0;
        if (!applyOp(tok[0], a, b, r)) return false; st.back() = r; }
    if (st.size() != 1) return false; result = st[0]; return true;
}
bool evalTree(const std::vector<E>& p, int i, long long& out) {
    const E& e = p[i]; if (e.op == '#') { out = e.v; return true; } long long a, b = 0; if (!evalTree(p, e.l, a)) return false; if (e.op == 'n') { out = -a; return true; } if (!evalTree(p, e.r, b)) return false;
    long long r = 0; if (!applyOp(e.op, a, b, r)) return false; out = r; return true;
}
struct RD {                                                                                     // 독립 오라클: 우선순위·결합을 문법(재귀 하강)으로 적어 중위 문자열을 바로 계산한다 (연산자 스택·우선순위 표 없음)
    const std::string& s; std::size_t i = 0; bool ok = true; explicit RD(const std::string& str) : s(str) {}
    char peek() { while (i < s.size() && s[i] == ' ') i++; return i < s.size() ? s[i] : '\0'; }
    long long bin(char o, long long a, long long b) { long long r = 0; if (!applyOp(o, a, b, r)) { ok = false; r = 0; } return r; }
    long long expr() { long long v = term(); while (peek() == '+' || peek() == '-') { char o = s[i++]; v = bin(o, v, term()); } return v; }                                   // + - 좌결합
    long long term() { long long v = unary(); while (peek() == '*' || peek() == '/' || peek() == '%') { char o = s[i++]; v = bin(o, v, unary()); } return v; }                  // * / % 좌결합
    long long unary() { if (peek() == '-') { i++; return -unary(); } return power(); }                                                                                        // 단항 마이너스: 곱셈보다 높고 ^ 보다 낮다
    long long power() { long long b = atom(); if (peek() == '^') { i++; return bin('^', b, unary()); } return b; }                                                            // ^ 우결합
    long long atom() { if (peek() == '(') { i++; long long v = expr(); peek(); i++; return v; } long long v = 0; while (i < s.size() && isdigit((unsigned char)s[i])) v = v * 10 + (s[i++] - '0'); return v; }
};
std::string shuntingTrace(const std::string& s) {                      // 그림: 토큰을 하나 읽을 때마다 (출력, 연산자 스택) — 한 자리 숫자·이항 연산자·괄호만 다루는 단순판
    std::string out, st, trace;
    auto row = [&](const std::string& tok) { trace += tok + " | out=" + out + " | stack=" + st + "\n"; };
    for (char c : s) {
        if (c == ' ') continue;
        if (isdigit((unsigned char)c)) out += c;                                                     // 숫자는 곧장 출력
        else if (c == '(') st += c;
        else if (c == ')') { while (st.back() != '(') { out += st.back(); st.pop_back(); } st.pop_back(); }           // 여는 괄호까지 꺼내 출력하고 괄호는 버린다
        else { while (!st.empty() && st.back() != '(' && (prec(st.back()) > prec(c) || (prec(st.back()) == prec(c) && !rightAssoc(c)))) { out += st.back(); st.pop_back(); } st += c; }
        row(std::string(1, c));
    }
    while (!st.empty()) { out += st.back(); st.pop_back(); }
    return trace + "end | out=" + out + " | stack=\n";
}
int main() {
    {   const std::string expr = "3+4*2/(1-5)^2^3";                                                     // 위키백과의 고전 예: 우선순위 + 괄호 + 우결합 ^
        const std::string pic = "3 | out=3 | stack=\n+ | out=3 | stack=+\n4 | out=34 | stack=+\n* | out=34 | stack=+*\n2 | out=342 | stack=+*\n/ | out=342* | stack=+/\n"
                                "( | out=342* | stack=+/(\n1 | out=342*1 | stack=+/(\n- | out=342*1 | stack=+/(-\n5 | out=342*15 | stack=+/(-\n) | out=342*15- | stack=+/\n"
                                "^ | out=342*15- | stack=+/^\n2 | out=342*15-2 | stack=+/^\n^ | out=342*15-2 | stack=+/^^\n3 | out=342*15-23 | stack=+/^^\nend | out=342*15-23^^/+ | stack=\n";
        assert(shuntingTrace(expr) == pic);                                                           // '/' 는 같은 우선순위의 '*' 를 먼저 꺼내고(좌결합), 두 번째 '^' 는 첫 '^' 를 꺼내지 않는다(우결합)
        std::vector<std::string> tokens; bool conv = toPostfix(expr, tokens); assert(conv); std::string joined; for (const auto& t : tokens) joined += t;
        assert(joined == "342*15-23^^/+");                                                            // 본 구현(toPostfix)도 같은 후위식
        std::cout << pic; }
    std::mt19937 rng(11); int checked = 0, evaluated = 0;
    for (int t = 0; t < 4000; t++) { std::vector<E> pool; int root = gen(pool, 1 + rng() % 5, rng); std::string infix = infixOf(pool, root, rng); std::vector<std::string> want, got; postfixOf(pool, root, want);
        bool conv = toPostfix(infix, got); assert(conv && got == want); checked++;                                                                                                                       // ① 트리의 후위 순회와 정확히 같다
        long long a = 0, b = 0; bool okTree = evalTree(pool, root, a), okPost = evalPostfix(got, b); assert(okTree == okPost && (!okTree || a == b)); evaluated += okTree;
        RD rd(infix); long long c = rd.expr(); char tail = rd.peek(); assert(tail == '\0' && rd.ok == okPost && (!okPost || c == b)); }                  // ④ 계산 결과도 같다
    typedef std::vector<std::string> V;
    { std::vector<std::string> out; bool c1 = toPostfix("12+345*6", out); assert(c1 && out == (V{"12", "345", "6", "*", "+"})); bool c2 = toPostfix("2^3^2", out); assert(c2 && out == (V{"2", "3", "2", "^", "^"}));          // ② 여러 자리, 우결합
      bool c3 = toPostfix("8-3-2", out); assert(c3 && out == (V{"8", "3", "-", "2", "-"})); bool c4 = toPostfix("-2^2", out); assert(c4 && out == (V{"2", "2", "^", "~"})); bool c5 = toPostfix("2*-3", out); assert(c5 && out == (V{"2", "3", "~", "*"})); bool c11 = toPostfix("-2*3", out); assert(c11 && out == (V{"2", "~", "3", "*"}));
      bool c6 = toPostfix("1+7%3", out); assert(c6 && out == (V{"1", "7", "3", "%", "+"})); bool c7 = toPostfix("1+2-3", out); assert(c7 && out == (V{"1", "2", "+", "3", "-"})); bool c8 = toPostfix("1-2+3", out); assert(c8 && out == (V{"1", "2", "-", "3", "+"}));
      bool c9 = toPostfix("8/2*3%5", out); assert(c9 && out == (V{"8", "2", "/", "3", "*", "5", "%"})); bool c10 = toPostfix("2*3^2+1", out); assert(c10 && out == (V{"2", "3", "2", "^", "*", "1", "+"})); }                       // ② 우선순위 표를 손으로 확인: % 는 * 와 같은 단계, + 와 - 는 같은 단계(좌결합)
    for (const char* bad : {"", "(1+2", "1+2)", "1+*2", "1 2", "()", "1+", "*3", "(1+2))", "1+(2*)", "a+b", "2^"}) { std::vector<std::string> out; bool accepted = toPostfix(bad, out); assert(!accepted); }                                      // ③ 오류
    std::cout << "InfixToPostfix: " << checked << " random expressions (with associativity, unary minus, redundant parentheses and spaces) converted to exactly the tree's postfix order; " << evaluated << " of them evaluated identically, also by an independent recursive-descent evaluator; 12 malformed inputs were rejected" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PostfixEvaluation()
### 대표코드
```cpp
#include <cctype>
#include <cmath>
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 후위 표기 계산(PostfixEvaluation, RPN): 피연산자를 만나면 push, 연산자를 만나면 필요한 개수만큼 pop 해 계산하고 결과를 push 한다. 이항 연산자는 오른쪽 피연산자가 먼저 나오므로 b = pop(), a = pop() 순서로 꺼내 a ⊕ b 를 계산한다(뺄셈·나눗셈에서 순서를 거꾸로 하면 틀린다). 끝에 스택에 정확히 하나가 남아야 한다.
// 현실적인 계산기는 오류를 돌려줘야 한다: 스택 언더플로(연산자에 피연산자가 모자람), 남는 피연산자(연산자가 모자람), 0 으로 나누기, 허용 범위를 넘는 결과(오버플로), 음수 지수. 이 구현은 모두 false 로 알린다. 토큰은 공백으로 구분된 여러 자리 정수, 이항 + - * / % ^, 단항 마이너스 ~ 이다.
// 유효성은 계산하지 않고도 센 것만으로 판정할 수 있다: 피연산자는 +1, 이항 연산자는 −1(스택이 2 이상이어야 함), 단항은 0(1 이상이어야 함)을 더해 가며 한 번도 모자라지 않고 끝값이 1 이면 올바른 후위식이다.
// 검증: ① 무작위 식 트리의 후위 표기를 이 계산기로 계산한 값이 트리를 직접 계산한 값과 같다(오류가 나는 식은 오류도 같다) ② 임의의 토큰열에서 계산기의 구조 오류 판정이 "센 값" 규칙과 일치 ③ 뺄셈·나눗셈 순서 고정 사례 ④ 오류 사례 ⑤ 여러 자리 수와 음수
struct E { char op; long long v; int l, r; };
int gen(std::vector<E>& pool, int depth, std::mt19937& rng) {
    if (depth == 0 || rng() % 4 == 0) { pool.push_back({'#', (long long)(rng() % 120), -1, -1}); return (int)pool.size() - 1; }
    if (rng() % 8 == 0) { int c = gen(pool, depth - 1, rng); pool.push_back({'n', 0, c, -1}); return (int)pool.size() - 1; }
    const char ops[] = {'+', '-', '*', '/', '%', '^'}; char o = ops[rng() % 6]; int l = gen(pool, depth - 1, rng); int r = o == '^' ? (pool.push_back({'#', (long long)(rng() % 4), -1, -1}), (int)pool.size() - 1) : gen(pool, depth - 1, rng);
    pool.push_back({o, 0, l, r}); return (int)pool.size() - 1;
}
void postfixOf(const std::vector<E>& p, int i, std::vector<std::string>& out) { const E& e = p[i]; if (e.op == '#') { out.push_back(std::to_string(e.v)); return; } postfixOf(p, e.l, out); if (e.op != 'n') postfixOf(p, e.r, out); out.push_back(e.op == 'n' ? "~" : std::string(1, e.op)); }
enum Err { OK, UNDERFLOW, LEFTOVER, DIV0, RANGE, NEGEXP, BADTOKEN };
Err apply(char o, long long a, long long b, long long& r) {
    if (o == '+') r = a + b; else if (o == '-') r = a - b; else if (o == '*') { if (std::fabs((long double)a * (long double)b) > 1e15L) return RANGE; r = a * b; } else if (o == '/') { if (!b) return DIV0; r = a / b; } else if (o == '%') { if (!b) return DIV0; r = a % b; }
    else { if (b < 0) return NEGEXP; r = 1; for (long long k = 0; k < b; k++) { if (std::fabs((long double)r * (long double)a) > 1e15L) return RANGE; r *= a; } }
    return r > (1LL << 50) || r < -(1LL << 50) ? RANGE : OK;
}
Err evaluate(const std::vector<std::string>& tokens, long long& result) {
    std::stack<long long> st;
    for (auto& t : tokens) {
        if (isdigit((unsigned char)t[0])) { st.push(std::stoll(t)); continue; }
        if (t == "~") { if (st.empty()) return UNDERFLOW; long long a = st.top(); st.pop(); st.push(-a); continue; }
        if (t.size() != 1 || std::string("+-*/%^").find(t[0]) == std::string::npos) return BADTOKEN;
        if (st.size() < 2) return UNDERFLOW;
        long long b = st.top(); st.pop(); long long a = st.top(); st.pop();                                    // 오른쪽 피연산자가 먼저 나온다
        long long r; Err e = apply(t[0], a, b, r); if (e != OK) return e; st.push(r);
    }
    if (st.size() != 1) return st.empty() ? UNDERFLOW : LEFTOVER; result = st.top(); return OK;
}
bool treeValue(const std::vector<E>& p, int i, long long& out) { const E& e = p[i]; if (e.op == '#') { out = e.v; return true; } long long a, b = 0; if (!treeValue(p, e.l, a)) return false; if (e.op == 'n') { out = -a; return true; } if (!treeValue(p, e.r, b)) return false; return apply(e.op, a, b, out) == OK; }
bool countRuleValid(const std::vector<std::string>& t) { int d = 0; for (auto& x : t) { if (isdigit((unsigned char)x[0])) d++; else if (x == "~") { if (d < 1) return false; } else { if (d < 2) return false; d--; } } return d == 1; }
int main() {
    std::mt19937 rng(5); int ok = 0, err = 0;
    for (int t = 0; t < 4000; t++) { std::vector<E> pool; int root = gen(pool, 1 + rng() % 5, rng); std::vector<std::string> pf; postfixOf(pool, root, pf); long long want = 0, got = 0; bool treeOk = treeValue(pool, root, want); Err e = evaluate(pf, got);
        assert(treeOk == (e == OK) && (!treeOk || want == got)); ok += treeOk; err += !treeOk; }                                                                                   // ①
    for (int t = 0; t < 20000; t++) { std::vector<std::string> tk; int n = rng() % 9; for (int i = 0; i < n; i++) { int k = rng() % 5; tk.push_back(k < 2 ? std::to_string(1 + rng() % 9) : k == 2 ? "+" : k == 3 ? "*" : "~"); } long long r; Err e = evaluate(tk, r); bool structural = e == UNDERFLOW || e == LEFTOVER; assert(structural == !countRuleValid(tk)); }          // ②
    { long long r; assert(evaluate({"8", "3", "-"}, r) == OK && r == 5 && evaluate({"8", "2", "/"}, r) == OK && r == 4 && evaluate({"2", "3", "^"}, r) == OK && r == 8 && evaluate({"7", "~", "3", "%"}, r) == OK && r == -1); }                      // ③ 순서
    { long long r; assert(evaluate({"+"}, r) == UNDERFLOW && evaluate({"1", "+"}, r) == UNDERFLOW && evaluate({"1", "2"}, r) == LEFTOVER && evaluate({}, r) == UNDERFLOW && evaluate({"1", "0", "/"}, r) == DIV0 && evaluate({"1", "0", "%"}, r) == DIV0 && evaluate({"2", "1", "~", "^"}, r) == NEGEXP && evaluate({"9", "30", "^"}, r) == RANGE && evaluate({"1", "x"}, r) == BADTOKEN); }      // ④
    { long long r; assert(evaluate({"12", "345", "+", "6", "*"}, r) == OK && r == 2142 && evaluate({"5", "~", "3", "+"}, r) == OK && r == -2); }                                                                                             // ⑤
    std::cout << "PostfixEvaluation: " << ok << " random expression trees evaluated exactly like direct tree evaluation and " << err << " erroneous ones (div by zero, range, negative exponent) failed identically; structural errors matched the counting rule on 20000 random token lists" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PrefixEvaluation()
### 대표코드
```cpp
#include <cctype>
#include <cmath>
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 전위 표기 계산(PrefixEvaluation, 폴란드 표기): 연산자가 피연산자 앞에 오는 표기 "+ * 2 3 4". 오른쪽에서 왼쪽으로 스캔하며 피연산자는 push, 연산자는 pop 두 번으로 계산한다. 이때 먼저 꺼낸 것이 왼쪽 피연산자다(후위와 반대): a = pop(), b = pop() 후 a ⊕ b. 한 번의 스캔과 스택 하나로 끝나며, 연산자 우선순위나 괄호가 필요 없다.
// 후위 표기와의 관계: 같은 식 트리를 전위 순회(루트 → 왼쪽 → 오른쪽)하면 전위식, 후위 순회(왼쪽 → 오른쪽 → 루트)하면 후위식이다. 전위식을 뒤집으면 좌우 대칭 트리의 후위식이 된다. 어느 쪽이든 괄호 없이 트리를 복원할 수 있다(Lisp 의 (+ (* 2 3) 4) 가 전위의 변형이다).
// 유효성은 오른쪽에서 왼쪽으로 센 값으로 판정한다: 피연산자 +1, 이항 −1(2 이상 필요), 단항 0(1 이상 필요), 끝값 1.
// 검증: ① 무작위 식 트리의 전위 표기를 이 계산기로 계산한 값이 트리 직접 계산과 같다(오류도 같다) ② 같은 트리의 전위·후위 표기가 같은 값을 준다 ③ 임의의 토큰열에서 구조 오류 판정이 센 값 규칙과 일치 ④ 피연산자 순서 사례(뺄셈·나눗셈은 전위에서 왼쪽이 먼저) ⑤ 오류 사례
struct E { char op; long long v; int l, r; };
int gen(std::vector<E>& pool, int depth, std::mt19937& rng) {
    if (depth == 0 || rng() % 4 == 0) { pool.push_back({'#', (long long)(rng() % 120), -1, -1}); return (int)pool.size() - 1; }
    if (rng() % 8 == 0) { int c = gen(pool, depth - 1, rng); pool.push_back({'n', 0, c, -1}); return (int)pool.size() - 1; }
    const char ops[] = {'+', '-', '*', '/', '%', '^'}; char o = ops[rng() % 6]; int l = gen(pool, depth - 1, rng); int r = o == '^' ? (pool.push_back({'#', (long long)(rng() % 4), -1, -1}), (int)pool.size() - 1) : gen(pool, depth - 1, rng);
    pool.push_back({o, 0, l, r}); return (int)pool.size() - 1;
}
void prefixOf(const std::vector<E>& p, int i, std::vector<std::string>& out) { const E& e = p[i]; if (e.op == '#') { out.push_back(std::to_string(e.v)); return; } out.push_back(e.op == 'n' ? "~" : std::string(1, e.op)); prefixOf(p, e.l, out); if (e.op != 'n') prefixOf(p, e.r, out); }
void postfixOf(const std::vector<E>& p, int i, std::vector<std::string>& out) { const E& e = p[i]; if (e.op == '#') { out.push_back(std::to_string(e.v)); return; } postfixOf(p, e.l, out); if (e.op != 'n') postfixOf(p, e.r, out); out.push_back(e.op == 'n' ? "~" : std::string(1, e.op)); }
enum Err { OK, UNDERFLOW, LEFTOVER, DIV0, RANGE, NEGEXP, BADTOKEN };
Err apply(char o, long long a, long long b, long long& r) {
    if (o == '+') r = a + b; else if (o == '-') r = a - b; else if (o == '*') { if (std::fabs((long double)a * (long double)b) > 1e15L) return RANGE; r = a * b; } else if (o == '/') { if (!b) return DIV0; r = a / b; } else if (o == '%') { if (!b) return DIV0; r = a % b; }
    else { if (b < 0) return NEGEXP; r = 1; for (long long k = 0; k < b; k++) { if (std::fabs((long double)r * (long double)a) > 1e15L) return RANGE; r *= a; } }
    return r > (1LL << 50) || r < -(1LL << 50) ? RANGE : OK;
}
Err evalPrefix(const std::vector<std::string>& tokens, long long& result) {
    std::stack<long long> st;
    for (size_t k = tokens.size(); k-- > 0;) { const std::string& t = tokens[k];                                  // 오른쪽에서 왼쪽으로
        if (isdigit((unsigned char)t[0])) { st.push(std::stoll(t)); continue; }
        if (t == "~") { if (st.empty()) return UNDERFLOW; long long a = st.top(); st.pop(); st.push(-a); continue; }
        if (t.size() != 1 || std::string("+-*/%^").find(t[0]) == std::string::npos) return BADTOKEN;
        if (st.size() < 2) return UNDERFLOW;
        long long a = st.top(); st.pop(); long long b = st.top(); st.pop();                                      // 먼저 꺼낸 것이 왼쪽 피연산자
        long long r; Err e = apply(t[0], a, b, r); if (e != OK) return e; st.push(r); }
    if (st.size() != 1) return st.empty() ? UNDERFLOW : LEFTOVER; result = st.top(); return OK;
}
Err evalPostfix(const std::vector<std::string>& tokens, long long& result) {
    std::stack<long long> st;
    for (auto& t : tokens) { if (isdigit((unsigned char)t[0])) { st.push(std::stoll(t)); continue; } if (t == "~") { if (st.empty()) return UNDERFLOW; long long a = st.top(); st.pop(); st.push(-a); continue; } if (st.size() < 2) return UNDERFLOW;
        long long b = st.top(); st.pop(); long long a = st.top(); st.pop(); long long r; Err e = apply(t[0], a, b, r); if (e != OK) return e; st.push(r); }
    if (st.size() != 1) return st.empty() ? UNDERFLOW : LEFTOVER; result = st.top(); return OK;
}
bool treeValue(const std::vector<E>& p, int i, long long& out) { const E& e = p[i]; if (e.op == '#') { out = e.v; return true; } long long a, b = 0; if (!treeValue(p, e.l, a)) return false; if (e.op == 'n') { out = -a; return true; } if (!treeValue(p, e.r, b)) return false; return apply(e.op, a, b, out) == OK; }
bool countRuleValid(const std::vector<std::string>& t) { int d = 0; for (size_t k = t.size(); k-- > 0;) { const std::string& x = t[k]; if (isdigit((unsigned char)x[0])) d++; else if (x == "~") { if (d < 1) return false; } else { if (d < 2) return false; d--; } } return d == 1; }
int main() {
    std::mt19937 rng(9); int ok = 0, err = 0;
    for (int t = 0; t < 4000; t++) { std::vector<E> pool; int root = gen(pool, 1 + rng() % 5, rng); std::vector<std::string> pre, post; prefixOf(pool, root, pre); postfixOf(pool, root, post); long long want = 0, a = 0, b = 0; bool treeOk = treeValue(pool, root, want); Err e1 = evalPrefix(pre, a), e2 = evalPostfix(post, b);
        assert(treeOk == (e1 == OK) && treeOk == (e2 == OK) && (!treeOk || (want == a && a == b))); ok += treeOk; err += !treeOk; }                                                      // ① ②
    for (int t = 0; t < 20000; t++) { std::vector<std::string> tk; int n = rng() % 9; for (int i = 0; i < n; i++) { int k = rng() % 5; tk.push_back(k < 2 ? std::to_string(1 + rng() % 9) : k == 2 ? "+" : k == 3 ? "*" : "~"); } long long r; Err e = evalPrefix(tk, r); assert((e == UNDERFLOW || e == LEFTOVER) == !countRuleValid(tk)); }       // ③
    { long long r; assert(evalPrefix({"-", "8", "3"}, r) == OK && r == 5 && evalPrefix({"/", "8", "2"}, r) == OK && r == 4 && evalPrefix({"+", "*", "2", "3", "4"}, r) == OK && r == 10 && evalPrefix({"-", "~", "5", "~", "2"}, r) == OK && r == -3); }                // ④
    { long long r; assert(evalPrefix({"+", "1"}, r) == UNDERFLOW && evalPrefix({"1", "2"}, r) == LEFTOVER && evalPrefix({"/", "1", "0"}, r) == DIV0 && evalPrefix({"^", "2", "~", "1"}, r) == NEGEXP && evalPrefix({}, r) == UNDERFLOW); }                         // ⑤
    std::cout << "PrefixEvaluation: " << ok << " random trees gave identical values by prefix scan, postfix scan and direct tree evaluation; " << err << " erroneous ones failed identically; the counting rule matched on 20000 random token lists" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## DecimalToBinary()
### 대표코드
```cpp
#include <bitset>
#include <climits>
#include <cstdint>
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <cassert>

// 십진수 → 이진수(DecimalToBinary): n 을 2 로 나눈 나머지를 구하는 순서는 낮은 자리부터인데 출력은 높은 자리부터여야 한다. 나머지를 차례로 스택에 쌓았다가 꺼내면 순서가 뒤집혀 올바른 이진 표기가 된다 — 스택을 쓰는 가장 기본적인 예다.
// 경계 조건이 함정이다: ① n = 0 은 반복문이 한 번도 돌지 않으므로 "0" 을 따로 돌려줘야 한다 ② 음수: 부호를 따로 붙이거나(−1101) 고정 폭 2 의 보수 표현으로 바꾼다. 2 의 보수는 부호 없는 형으로 바꿔 같은 알고리즘을 적용한다 ③ INT_MIN 은 −n 이 오버플로하므로 부호 없는 64 비트로 먼저 넓혀서 절댓값을 구한다 ④ 폭을 맞추려면 앞을 0 으로 채운다.
// 역변환(이진 → 십진)은 왼쪽부터 읽으며 v = 2v + 비트 로 누적한다 — 스택이 필요 없다(호너의 방법).
// 검증: ① 0..5000 전부와 무작위 32/64 비트 값에서 std::bitset 출력과 같다(앞 0 제거 후) ② 음수의 부호 표기와 32 비트 2 의 보수 표기가 표준(bitset<32>)과 같다 ③ INT_MIN, INT_MAX, LLONG_MIN, 0 ④ 역변환 왕복 ⑤ 고정 폭 채우기
std::string toBinaryMagnitude(unsigned long long n) { if (n == 0) return "0"; std::stack<int> s; while (n > 0) { s.push((int)(n % 2)); n /= 2; } std::string r; while (!s.empty()) { r += (char)('0' + s.top()); s.pop(); } return r; }
std::string toBinarySigned(long long v) { if (v >= 0) return toBinaryMagnitude((unsigned long long)v); return "-" + toBinaryMagnitude(0ULL - (unsigned long long)v); }           // 0 - u: INT64_MIN 에서도 오버플로 없이 절댓값
std::string toBinaryTwosComplement(long long v, int width) { unsigned long long u = (unsigned long long)v; if (width < 64) u &= (1ULL << width) - 1; std::string m = toBinaryMagnitude(u); return std::string(m.size() < (size_t)width ? width - m.size() : 0, '0') + m; }
unsigned long long fromBinary(const std::string& s) { unsigned long long v = 0; for (char c : s) v = v * 2 + (c - '0'); return v; }
std::string stripZeros(std::string s) { size_t i = s.find('1'); return i == std::string::npos ? "0" : s.substr(i); }
int main() {
    for (int n = 0; n <= 5000; n++) assert(toBinarySigned(n) == stripZeros(std::bitset<32>(n).to_string()));                                                                       // ①
    std::mt19937_64 rng(4);
    for (int t = 0; t < 20000; t++) { unsigned long long u = rng() >> (rng() % 64); assert(toBinaryMagnitude(u) == stripZeros(std::bitset<64>(u).to_string()) && fromBinary(toBinaryMagnitude(u)) == u); }                          // ① ④ 64 비트와 왕복
    for (int t = 0; t < 5000; t++) { int v = (int)rng(); assert(toBinaryTwosComplement(v, 32) == std::bitset<32>((unsigned)v).to_string()); long long w = (long long)rng(); assert(toBinaryTwosComplement(w, 64) == std::bitset<64>((unsigned long long)w).to_string()); assert(toBinarySigned(v) == (v < 0 ? "-" : "") + stripZeros(std::bitset<64>((unsigned long long)(v < 0 ? -(long long)v : (long long)v)).to_string())); }       // ②
    assert(toBinarySigned(0) == "0" && toBinarySigned(INT_MAX) == std::string(31, '1') && toBinarySigned(INT_MIN) == "-1" + std::string(31, '0') && toBinarySigned(LLONG_MIN) == "-1" + std::string(63, '0') && toBinaryTwosComplement(-1, 8) == "11111111" && toBinaryTwosComplement(5, 8) == "00000101");        // ③ ⑤
    assert(toBinarySigned(13) == "1101" && toBinarySigned(-13) == "-1101" && toBinaryTwosComplement(-13, 8) == "11110011" && fromBinary("1101") == 13);
    std::cout << "DecimalToBinary: stack-based conversion matched std::bitset for 0..5000, 20000 random 64-bit values and 5000 negative 32/64-bit values; INT_MIN, LLONG_MIN and zero handled; binary->decimal round trips held" << std::endl; return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(log N)
```
## BaseConversion()
### 대표코드
```cpp
#include <cctype>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <cassert>

// 진법 변환(BaseConversion): 십진수를 2~36 진법으로 바꾼다. 나머지를 쌓았다가 거꾸로 꺼내는 스택 알고리즘은 이진수와 같고 자릿수 문자만 "0-9A-Z" 로 늘어난다. 반대 방향(문자열 → 정수)은 왼쪽부터 v = v·base + 자릿값 으로 누적한다(호너의 방법).
// 정확하게 하려면 ① 0 과 음수(부호를 분리하고 부호 없는 형으로 절댓값을 구해 최솟값 오버플로 방지) ② 입력 검증(진법 범위, 자릿값이 진법 이상인 글자, 빈 문자열, 부호만 있는 문자열) ③ 오버플로 검출(누적 전에 v > (LLONG_MAX − digit)/base 이면 오류) ④ 대소문자 허용을 처리해야 한다.
// 검증: ① 2..36 진법과 0·±경계값·무작위 64 비트에서 변환 결과가 C 표준 strtoll 의 해석과 왕복으로 일치(변환 → strtoll(base) == 원래 값) ② 십진은 std::to_string 과 같다 ③ 파싱 오류 입력이 모두 거절 ④ 오버플로 경계 LLONG_MAX/LLONG_MIN 은 허용되고 한 칸 넘으면 거절 ⑤ 대소문자 입력
std::string toBase(long long value, int base) {
    static const char* D = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"; unsigned long long u = value < 0 ? 0ULL - (unsigned long long)value : (unsigned long long)value;
    if (u == 0) return "0"; std::stack<int> s; while (u > 0) { s.push((int)(u % base)); u /= base; } std::string r = value < 0 ? "-" : ""; while (!s.empty()) { r += D[s.top()]; s.pop(); } return r;
}
bool fromBase(const std::string& str, int base, long long& out) {                                    // 실패하면 false
    if (base < 2 || base > 36 || str.empty()) return false; size_t i = 0; bool neg = false; if (str[0] == '-' || str[0] == '+') { neg = str[0] == '-'; i = 1; } if (i == str.size()) return false;
    unsigned long long v = 0, limit = neg ? (unsigned long long)LLONG_MAX + 1 : (unsigned long long)LLONG_MAX;
    for (; i < str.size(); i++) { char c = (char)toupper((unsigned char)str[i]); int d = isdigit((unsigned char)c) ? c - '0' : isalpha((unsigned char)c) ? c - 'A' + 10 : 99; if (d >= base) return false; if (v > (limit - d) / base) return false; v = v * base + d; }
    out = neg ? (long long)(0ULL - v) : (long long)v; return true;
}
int main() {
    std::mt19937_64 rng(6); long long checked = 0;
    for (int base = 2; base <= 36; base++) { for (long long v : {0LL, 1LL, -1LL, (long long)base, (long long)base - 1, (long long)base * base, LLONG_MAX, LLONG_MIN, LLONG_MAX - 1, LLONG_MIN + 1}) { std::string s = toBase(v, base); long long back; assert(fromBase(s, base, back) && back == v && std::strtoll(s.c_str(), nullptr, base) == v); checked++; }
        for (int t = 0; t < 400; t++) { long long v = (long long)(rng() >> (rng() % 64)) * ((rng() & 1) ? 1 : -1); std::string s = toBase(v, base); long long back; assert(fromBase(s, base, back) && back == v && std::strtoll(s.c_str(), nullptr, base) == v); checked++; } }       // ①
    for (int t = 0; t < 2000; t++) { long long v = (long long)rng() >> (rng() % 63); assert(toBase(v, 10) == std::to_string(v)); }                                                                                 // ②
    { long long x; for (const char* bad : {"", "-", "+", "12G", "z", "2"}) assert(!fromBase(bad, bad[0] == 'z' ? 10 : bad[0] == '2' ? 2 : 16, x)); assert(!fromBase("10", 1, x) && !fromBase("10", 37, x) && !fromBase("1 0", 10, x)); }                // ③
    { long long x; assert(fromBase("9223372036854775807", 10, x) && x == LLONG_MAX && !fromBase("9223372036854775808", 10, x) && fromBase("-9223372036854775808", 10, x) && x == LLONG_MIN && !fromBase("-9223372036854775809", 10, x)); }          // ④ 오버플로 경계
    { long long x; assert(fromBase("ff", 16, x) && x == 255 && fromBase("FF", 16, x) && x == 255 && fromBase("zZ", 36, x) && x == 35 * 36 + 35 && toBase(255, 16) == "FF" && toBase(-255, 16) == "-FF" && toBase(35 * 36 + 35, 36) == "ZZ"); }          // ⑤
    std::cout << "BaseConversion: " << checked << " conversions in bases 2..36 (including LLONG_MIN/MAX) round-tripped through strtoll; decimal output equalled std::to_string; malformed inputs and overflow boundaries were rejected" << std::endl; return 0;
}
// Time Complexity: O(log_base N)
// Space Complexity: O(log_base N)
```
## Undo()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 실행 취소(Undo/Redo): 편집기의 되돌리기는 두 스택으로 만든다. undo 스택에는 지금까지 실행한 명령이, redo 스택에는 되돌린 명령이 쌓인다. 새 편집을 하면 redo 스택은 비운다(되돌린 미래는 더 이상 유효하지 않다).
// 두 가지 구현이 있다. ① 스냅샷 방식: 편집할 때마다 문서 전체를 저장 — 단순하지만 메모리가 문서 크기 × 편집 횟수. ② 명령(command) 방식: 편집마다 "무엇을 어디에 넣었다/지웠다" 만 저장하고 되돌릴 때 역연산(넣은 것을 지우고, 지운 것을 다시 넣기)을 적용 — 메모리는 편집의 크기에만 비례한다. 이 항목은 ② 를 구현하고 ① 을 기준 구현으로 삼아 대조한다.
// 명령에는 되돌릴 정보가 모두 있어야 한다: 삽입은 (위치, 넣은 문자열), 삭제는 (위치, 지운 문자열 — 되살려야 하므로 내용을 보관). 
// 검증: 무작위 편집(삽입·삭제)·undo·redo 6 만 번을 스냅샷 기록 배열(현재 위치 포인터)과 대조: ① 모든 단계에서 문서가 같다 ② undo 후 새 편집은 redo 를 무효화 ③ 끝까지 undo 하면 빈 문서, 다시 끝까지 redo 하면 마지막 상태 ④ 명령 방식의 저장 바이트가 스냅샷 방식보다 적다
struct Cmd { bool insert; size_t pos; std::string text; };                                                     // 삽입이면 text 를 pos 에 넣었다, 삭제면 pos 에서 text 를 지웠다
class Editor {
    std::string doc_; std::stack<Cmd> undo_, redo_; size_t stored_ = 0;
    void apply(const Cmd& c) { if (c.insert) doc_.insert(c.pos, c.text); else doc_.erase(c.pos, c.text.size()); }
    static Cmd inverse(const Cmd& c) { return {!c.insert, c.pos, c.text}; }
public:
    void insertText(size_t pos, const std::string& t) { Cmd c{true, std::min(pos, doc_.size()), t}; apply(c); undo_.push(c); stored_ += t.size(); redo_ = std::stack<Cmd>(); }
    void eraseText(size_t pos, size_t len) { if (pos >= doc_.size()) return; len = std::min(len, doc_.size() - pos); Cmd c{false, pos, doc_.substr(pos, len)}; apply(c); undo_.push(c); stored_ += c.text.size(); redo_ = std::stack<Cmd>(); }
    bool undo() { if (undo_.empty()) return false; Cmd c = undo_.top(); undo_.pop(); apply(inverse(c)); redo_.push(c); return true; }
    bool redo() { if (redo_.empty()) return false; Cmd c = redo_.top(); redo_.pop(); apply(c); undo_.push(c); return true; }
    const std::string& text() const { return doc_; } size_t storedBytes() const { return stored_ + (undo_.size() + redo_.size()) * sizeof(Cmd); } size_t undoDepth() const { return undo_.size(); } size_t redoDepth() const { return redo_.size(); }
};
int main() {
    std::mt19937 rng(7); Editor ed; std::vector<std::string> history = {""}; size_t at = 0; size_t snapshotBytes = 0; bool sawRedoCleared = false;
    for (int step = 0; step < 60000; step++) {
        int op = rng() % 10;
        if (op < 4) { std::string t; int n = 1 + rng() % 6; for (int i = 0; i < n; i++) t += (char)('a' + rng() % 26); size_t pos = rng() % (ed.text().size() + 1); size_t redoBefore = ed.redoDepth(); ed.insertText(pos, t); std::string d = history[at]; d.insert(pos, t); history.resize(at + 1); history.push_back(d); at++; if (redoBefore) { assert(ed.redoDepth() == 0); sawRedoCleared = true; } snapshotBytes += d.size(); }
        else if (op < 6 && !ed.text().empty()) { size_t pos = rng() % ed.text().size(), len = 1 + rng() % 5; ed.eraseText(pos, len); std::string d = history[at]; d.erase(pos, std::min(len, d.size() - pos)); history.resize(at + 1); history.push_back(d); at++; snapshotBytes += d.size(); }
        else if (op < 8) { bool ok = ed.undo(); assert(ok == (at > 0)); if (ok) at--; }
        else { bool ok = ed.redo(); assert(ok == (at + 1 < history.size())); if (ok) at++; }
        assert(ed.text() == history[at]);                                                                                                                                                  // ① 매 단계 문서가 같다
        if (ed.text().size() > 200) { size_t cut = ed.text().size() - 100; ed.eraseText(0, cut); std::string d = history[at]; d.erase(0, cut); history.resize(at + 1); history.push_back(d); at++; assert(ed.text() == history[at]); snapshotBytes += d.size(); }          // 문서가 너무 길어지면 앞을 잘라 낸다 (이것도 되돌릴 수 있는 편집)
    }
    assert(sawRedoCleared);                                                                                                                                                                 // ② 새 편집이 redo 를 지웠다
    { Editor e; e.insertText(0, "hello"); e.insertText(5, " world"); e.eraseText(0, 6); assert(e.text() == "world"); while (e.undo()) {} assert(e.text().empty()); while (e.redo()) {} assert(e.text() == "world"); e.undo(); e.insertText(0, "X"); bool again = e.redo(); assert(!again && e.text() == "Xhello world"); }      // ③
    { Editor e; std::string doc; size_t snap = 0; for (int i = 0; i < 2000; i++) { e.insertText(e.text().size(), "word "); doc += "word "; snap += doc.size(); } assert(e.storedBytes() < snap / 20); }                                       // ④ 명령 방식 저장량 << 스냅샷 방식
    std::cout << "Undo: command-based undo/redo matched a snapshot-history model for 60000 randomized edits (command log " << ed.storedBytes() << " bytes vs " << snapshotBytes << " bytes of snapshots written); a new edit invalidated redo; 2000 appends needed far fewer stored bytes than full snapshots" << std::endl; return 0;
}
// Time Complexity: undo·redo·편집 O(편집 크기)
// Space Complexity: O(총 편집 크기) (스냅샷 방식은 O(문서 크기 × 편집 수))
```
## BrowserHistory()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 브라우저 방문 기록(BrowserHistory): 뒤로 가기·앞으로 가기는 스택 두 개와 "현재 페이지" 로 만든다. visit(url) 은 현재 페이지를 back 스택에 쌓고 새 페이지로 이동하며 forward 스택을 비운다(새 길을 열면 되돌아갔던 앞길은 사라진다). back 은 현재를 forward 에 쌓고 back 의 top 으로, forward 는 반대. 
// 여러 칸 이동(back(k), forward(k))은 요청한 만큼 또는 스택이 허락하는 만큼만 이동한다. 같은 동작을 "배열 + 현재 위치 인덱스" 로 구현할 수도 있다(방문 시 인덱스 뒤를 잘라 냄) — 이 항목은 스택 구현을 그 배열 구현과 대조한다.
// 검증: 무작위 visit/back(k)/forward(k) 5 만 번에서 ① 현재 페이지가 배열 모델과 항상 같다 ② 이동한 칸 수가 배열 모델과 같다 ③ visit 후 forward 는 항상 0 칸 ④ back 스택 크기 + forward 스택 크기 + 1 == 배열 모델의 길이(잘라낸 뒤) ⑤ 빈 기록에서의 이동은 제자리
class BrowserHistory {
    std::stack<std::string> back_, forward_; std::string current_;
public:
    explicit BrowserHistory(std::string home) : current_(std::move(home)) {}
    void visit(const std::string& url) { back_.push(current_); current_ = url; forward_ = std::stack<std::string>(); }
    int back(int steps) { int moved = 0; while (moved < steps && !back_.empty()) { forward_.push(current_); current_ = back_.top(); back_.pop(); moved++; } return moved; }
    int forward(int steps) { int moved = 0; while (moved < steps && !forward_.empty()) { back_.push(current_); current_ = forward_.top(); forward_.pop(); moved++; } return moved; }
    const std::string& current() const { return current_; } size_t backSize() const { return back_.size(); } size_t forwardSize() const { return forward_.size(); }
};
class ArrayHistory {                                                                             // 기준 구현: 배열과 현재 인덱스
    std::vector<std::string> pages_; int cur_ = 0;
public:
    explicit ArrayHistory(std::string home) : pages_{std::move(home)} {}
    void visit(const std::string& url) { pages_.resize(cur_ + 1); pages_.push_back(url); cur_++; }
    int back(int steps) { int m = std::min(steps, cur_); cur_ -= m; return m; }
    int forward(int steps) { int m = std::min(steps, (int)pages_.size() - 1 - cur_); cur_ += m; return m; }
    const std::string& current() const { return pages_[cur_]; } size_t length() const { return pages_.size(); }
};
int main() {
    std::mt19937 rng(8); BrowserHistory h("home.com"); ArrayHistory a("home.com"); int visits = 0, backs = 0, forwards = 0;
    for (int step = 0; step < 50000; step++) {
        int op = rng() % 5;
        if (op < 2) { std::string u = "site" + std::to_string(rng() % 1000) + ".com"; h.visit(u); a.visit(u); visits++; assert(h.forwardSize() == 0); }                          // ③
        else if (op < 4) { int k = 1 + rng() % 5; int m1 = h.back(k), m2 = a.back(k); assert(m1 == m2); backs += m1; }
        else { int k = 1 + rng() % 5; int m1 = h.forward(k), m2 = a.forward(k); assert(m1 == m2); forwards += m1; }                                                                // ②
        assert(h.current() == a.current());                                                                                                                                            // ①
        assert(h.backSize() + h.forwardSize() + 1 == a.length());                                                                                                                       // ④ 배열 모델의 길이 = back + 현재 + forward
    }
    { BrowserHistory e("start"); int b0 = e.back(3), f0 = e.forward(3); assert(b0 == 0 && f0 == 0 && e.current() == "start"); e.visit("a"); e.visit("b");
      int b1 = e.back(1); assert(b1 == 1 && e.current() == "a"); int f1 = e.forward(5); assert(f1 == 1 && e.current() == "b"); int b2 = e.back(5); assert(b2 == 2 && e.current() == "start");
      e.visit("c"); int f2 = e.forward(1), b3 = e.back(1); assert(f2 == 0 && b3 == 1 && e.current() == "start"); }          // ⑤
    std::cout << "BrowserHistory: the two-stack history matched an array-plus-index model over 50000 random operations (" << visits << " visits, " << backs << " pages back, " << forwards << " pages forward)" << std::endl; return 0;
}
// Time Complexity: visit O(1) (forward 비우기는 O(forward 크기)), back·forward O(이동한 칸 수)
// Space Complexity: O(방문한 페이지 수)
```

# Part 5. DFS
## DepthFirstSearch()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 깊이 우선 탐색 (스택 관점의 요약, 정본은 Graph.md Part 3): 스택으로 갈 수 있는 데까지 깊이 들어가고, 막히면 되돌아온다. 이 구현은 스택에 (정점, 다음 이웃 위치)를 두어 재귀 DFS 와 같은 순서를 내면서 각 정점의 발견 시각 disc 과 종료 시각 fin 을 기록한다.
// 두 시각이 DFS 의 모든 구조를 알려 준다. 간선 u→v 는 구간 [disc, fin] 의 포함 관계로 분류된다: v 가 u 를 감싸면 역방향(back; 사이클의 증거), u 가 v 를 감싸면 트리/순방향(forward), 두 구간이 겹치지 않고 v 가 먼저 끝났으면 교차(cross). 무방향 그래프에서는 교차 간선이 존재할 수 없다 — 이것이 DFS 트리가 "깊이" 구조라는 정의 그 자체다.
// 정리: 유향 그래프에 사이클이 있다 ⇔ DFS 에서 역방향 간선(자기 루프 포함)이 있다. 아래에서 이를 위상 정렬 기반(Kahn)의 독립 판정과 대조한다.
// 검증: ① 무작위 유향 그래프에서 DFS 가 도달 가능한 모든 정점을 정확히 한 번 방문(BFS 와 같은 집합) ② 구간이 중첩 구조(laminar)를 이룸 ③ "사이클 있음 ⇔ 역방향 간선 있음" 이 Kahn 과 일치 ④ 간선 분류에서 "v 가 나중에 시작해 나중에 끝나는 비포함" 경우는 존재하지 않음 ⑤ 무방향 그래프에서 교차 간선이 없음
typedef std::vector<std::vector<int>> Graph;
struct Dfs { std::vector<int> disc, fin, parent, order; };
Dfs run(const Graph& g, const std::vector<int>& roots) {
    int n = g.size(); Dfs d{std::vector<int>(n, 0), std::vector<int>(n, 0), std::vector<int>(n, -1), {}}; int t = 0; std::vector<std::pair<int, size_t>> st;
    for (int r : roots) { if (d.disc[r]) continue; d.disc[r] = ++t; d.order.push_back(r); st.push_back({r, 0});
        while (!st.empty()) { int v = st.back().first; size_t& i = st.back().second;
            if (i < g[v].size()) { int w = g[v][i++]; if (!d.disc[w]) { d.disc[w] = ++t; d.parent[w] = v; d.order.push_back(w); st.push_back({w, 0}); } }
            else { d.fin[v] = ++t; st.pop_back(); } } }
    return d;
}
bool hasCycleKahn(const Graph& g) { int n = g.size(); std::vector<int> in(n, 0); for (auto& a : g) for (int w : a) in[w]++; std::queue<int> q; for (int v = 0; v < n; v++) if (!in[v]) q.push(v); int seen = 0; while (!q.empty()) { int v = q.front(); q.pop(); seen++; for (int w : g[v]) if (--in[w] == 0) q.push(w); } return seen != n; }
int main() {
    std::mt19937 rng(13); long back = 0, forward = 0, cross = 0, tree = 0;
    for (int t = 0; t < 1500; t++) {
        int n = 1 + rng() % 14; Graph g(n); int m = rng() % (2 * n + 1); for (int k = 0; k < m; k++) g[rng() % n].push_back(rng() % n);
        std::vector<int> roots(n); for (int i = 0; i < n; i++) roots[i] = i; Dfs d = run(g, roots);
        for (int v = 0; v < n; v++) assert(d.disc[v] && d.fin[v] > d.disc[v]);                                                                                                           // 모든 정점 방문
        std::vector<int> one = {0}; Dfs from0 = run(g, one); std::vector<char> reach(n, 0); std::queue<int> q; q.push(0); reach[0] = 1; while (!q.empty()) { int v = q.front(); q.pop(); for (int w : g[v]) if (!reach[w]) { reach[w] = 1; q.push(w); } }
        for (int v = 0; v < n; v++) assert((from0.disc[v] != 0) == (bool)reach[v]);                                                                                                     // ① 도달 가능한 집합과 같다
        for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) { bool disjoint = d.fin[a] < d.disc[b] || d.fin[b] < d.disc[a]; bool nested = (d.disc[a] < d.disc[b] && d.fin[b] < d.fin[a]) || (d.disc[b] < d.disc[a] && d.fin[a] < d.fin[b]); assert(disjoint || nested); }   // ② 구간의 중첩 구조
        bool backEdge = false; std::vector<char> usedTree(n, 0);
        for (int u = 0; u < n; u++) for (int v : g[u]) { bool vContainsU = d.disc[v] <= d.disc[u] && d.fin[u] <= d.fin[v], uContainsV = d.disc[u] < d.disc[v] && d.fin[v] < d.fin[u], vBefore = d.fin[v] < d.disc[u];
            assert(vContainsU || uContainsV || vBefore);                                                                                                                                // ④ 다른 경우는 없다
            if (d.parent[v] == u && !usedTree[v] && uContainsV) { usedTree[v] = 1; tree++; } else if (vContainsU) { backEdge = true; back++; } else if (uContainsV) forward++; else cross++; }
        assert(backEdge == hasCycleKahn(g));                                                                                                                                              // ③ 사이클 ⇔ 역방향 간선
    }
    for (int t = 0; t < 500; t++) { int n = 1 + rng() % 14; Graph g(n); int m = rng() % (2 * n + 1); for (int k = 0; k < m; k++) { int a = rng() % n, b = rng() % n; g[a].push_back(b); g[b].push_back(a); } std::vector<int> roots(n); for (int i = 0; i < n; i++) roots[i] = i; Dfs d = run(g, roots);
        for (int u = 0; u < n; u++) for (int v : g[u]) assert(!(d.fin[v] < d.disc[u]));                                                                                                 // ⑤ 무방향: 교차 간선 없음
    }
    std::cout << "DepthFirstSearch: discovery/finish times classified " << tree << " tree, " << back << " back, " << forward << " forward and " << cross << " cross edges on 1500 random digraphs; cycle <=> back edge matched Kahn's algorithm and undirected graphs had no cross edges" << std::endl; return 0;
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
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 위상 정렬(TopologicalSort): 방향 비순환 그래프(DAG)의 정점을 모든 간선 u→v 에서 u 가 v 앞에 오도록 일렬로 세운다. DFS 로 하면 한 정점의 모든 후손이 끝난 "뒤에" 그 정점이 끝나므로 종료 순서의 역순이 위상 순서다. 종료되는 정점을 스택에 push 해 두었다가 위에서부터 꺼내면 그 순서가 된다. 건설 순서, 빌드 의존성, 과목 선수 관계에 쓴다.
// 사이클이 있으면 위상 순서가 존재하지 않는다. DFS 에서는 "현재 경로(스택) 위에 있는 정점을 다시 만나면" 사이클이다 — 정점을 흰색(미방문)/회색(경로 위)/검정(완료)으로 칠하면 회색 정점으로 가는 간선이 사이클의 증거다. 이 구현은 재귀 없이 명시적 스택으로 해서 정점이 많아도 안전하다.
// 위상 순서는 유일하지 않다(순서가 정해지지 않은 정점끼리는 임의). 유일할 필요충분조건은 모든 연속한 두 정점 사이에 간선이 있는 것(해밀턴 경로)이다.
// 검증: 무작위 DAG(정점 이름을 섞어 만든 것)와 사이클 있는 그래프 합쳐 3000 개에서 ① DAG 는 결과가 유효한 위상 순서(모든 간선에서 위치 증가) ② 사이클 판정이 Kahn 알고리즘과 일치 ③ 사이클이 있을 때 실제 사이클(간선으로 이어진 정점열)을 돌려줌 ④ 해밀턴 경로가 있는 DAG 는 순서가 유일 ⑤ 모든 위상 순서의 개수가 작은 그래프에서 순열 전수 조사와 일치하는 결과 중 하나
typedef std::vector<std::vector<int>> Graph;
struct Result { bool ok; std::vector<int> order, cycle; };
Result topoSort(const Graph& g) {
    int n = g.size(); std::vector<int> color(n, 0), parent(n, -1); std::vector<int> finished; std::vector<std::pair<int, size_t>> st;
    for (int s = 0; s < n; s++) { if (color[s]) continue; color[s] = 1; st.push_back({s, 0});
        while (!st.empty()) { int v = st.back().first; size_t& i = st.back().second;
            if (i < g[v].size()) { int w = g[v][i++];
                if (color[w] == 0) { color[w] = 1; parent[w] = v; st.push_back({w, 0}); }
                else if (color[w] == 1) { std::vector<int> cyc = {w}; for (int x = v; x != w; x = parent[x]) cyc.push_back(x); std::reverse(cyc.begin(), cyc.end()); return {false, {}, cyc}; } }       // 회색 정점으로 가는 간선 = 사이클
            else { color[v] = 2; finished.push_back(v); st.pop_back(); } } }
    std::reverse(finished.begin(), finished.end()); return {true, finished, {}};                                  // 종료 순서의 역순 (스택에서 꺼내는 순서)
}
bool cyclicKahn(const Graph& g) { int n = g.size(); std::vector<int> in(n, 0); for (auto& a : g) for (int w : a) in[w]++; std::queue<int> q; for (int v = 0; v < n; v++) if (!in[v]) q.push(v); int seen = 0; while (!q.empty()) { int v = q.front(); q.pop(); seen++; for (int w : g[v]) if (--in[w] == 0) q.push(w); } return seen != n; }
bool validOrder(const Graph& g, const std::vector<int>& order) { int n = g.size(); if ((int)order.size() != n) return false; std::vector<int> pos(n, -1); for (int i = 0; i < n; i++) { if (pos[order[i]] >= 0) return false; pos[order[i]] = i; } for (int u = 0; u < n; u++) for (int v : g[u]) if (pos[u] >= pos[v]) return false; return true; }
int main() {
    std::mt19937 rng(14); int dags = 0, cyclic = 0;
    for (int t = 0; t < 3000; t++) { int n = 1 + rng() % 12; std::vector<int> label(n); for (int i = 0; i < n; i++) label[i] = i; std::shuffle(label.begin(), label.end(), rng); Graph g(n); int m = rng() % (2 * n + 1);
        for (int k = 0; k < m; k++) { int a = rng() % n, b = rng() % n; if (a == b) continue; if (a > b) std::swap(a, b); g[label[a]].push_back(label[b]); }                       // 번호가 증가하는 간선만 -> DAG
        if (t % 3 == 0 && n >= 2) { int a = rng() % n, b = rng() % n; g[a].push_back(b); }                                                                                       // 가끔 임의 간선(자기 루프 포함)을 더해 사이클을 만든다
        Result r = topoSort(g); bool cyc = cyclicKahn(g); assert(r.ok == !cyc);                                                                                                    // ② Kahn 과 일치
        if (r.ok) { assert(validOrder(g, r.order)); dags++; }                                                                                                                      // ①
        else { assert(!r.cycle.empty()); for (size_t i = 0; i < r.cycle.size(); i++) { int u = r.cycle[i], v = r.cycle[(i + 1) % r.cycle.size()]; assert(std::find(g[u].begin(), g[u].end(), v) != g[u].end()); } cyclic++; } }   // ③ 실제 사이클
    { Graph path(6); std::vector<int> perm = {3, 0, 5, 1, 4, 2}; for (int i = 0; i + 1 < 6; i++) path[perm[i]].push_back(perm[i + 1]); Result r = topoSort(path); assert(r.ok && r.order == perm); }                                          // ④ 해밀턴 경로 -> 유일
    { Graph g(5); g[0] = {2}; g[1] = {2, 3}; g[2] = {4}; g[3] = {4}; Result r = topoSort(g); assert(r.ok && validOrder(g, r.order)); std::vector<int> p = {0, 1, 2, 3, 4}; int valid = 0; do { valid += validOrder(g, p); } while (std::next_permutation(p.begin(), p.end())); assert(valid == 5); }          // ⑤ 이 그래프의 위상 순서는 정확히 5 가지(0 이 1 보다 먼저인 2 가지 + 1 이 먼저인 3 가지), 결과는 그중 하나
    std::cout << "TopologicalSort: " << dags << " random DAGs produced valid orders and " << cyclic << " cyclic graphs were rejected with a verified cycle, matching Kahn's algorithm on all 3000" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```

# Part 6. 단조 스택
## MonotonicStack()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <random>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 단조 스택(Monotonic Stack): 스택의 값이 항상 한 방향(예: 위로 갈수록 작아지는 감소)으로 정렬되도록 유지하는 기법이다. 새 값 x 를 넣기 전에 규칙을 어기는 top 들을 pop 한다. pop 되는 순간이 바로 "그 원소의 다음으로 큰 값이 x" 라는 사실이 확정되는 순간이므로, O(N²) 비교 없이 모든 원소의 "다음/이전 더 큰/작은 값" 을 O(N) 에 구한다.
// 왜 O(N): 각 원소는 한 번 push 되고 많아야 한 번 pop 되므로 반복문 안의 pop 총합이 N 이하다(분할상환).
// 변형 네 가지: 이전/다음 × 더 큰/더 작은. 또 "엄격히(>)" 인지 "같아도(>=)" 인지에 따라 값이 같은 원소 처리가 달라지므로 중복이 있는 입력에서 특히 중요하다. 이 항목은 네 변형 모두를 같은 틀(비교 함수만 교체)로 구현해 브루트포스(O(N²))와 대조한다. 응용: NextGreaterElement, PreviousGreaterElement, LargestRectangle, DailyTemperatures, StockSpan.
// 검증: 무작위 배열(중복 많음)에서 ① 네 변형의 모든 결과가 브루트포스와 같다 ② nearest 안에서 매 push 직전 top 이 새 원소와 비교 규칙을 만족함을 확인(인접한 쌍마다 성립하므로 스택 전체가 단조) ③ nearest 가 직접 센 값으로 push 횟수 == N, pop 횟수 ≤ N, pop + 남은 원소 == push ④ 엄격/비엄격 차이가 중복 입력에서 실제로 다른 결과를 낸다(배열×방향 쌍 기준)
enum Dir { NEXT, PREV };
// 각 i 에 대해 NEXT 는 i 오른쪽에서, PREV 는 왼쪽에서 pred(candidate, value) 를 처음 만족하는 원소의 인덱스(없으면 -1)를 구한다. pred 는 "더 크다/작다(엄격 또는 비엄격)" 판정.
struct Stats { long pushes = 0, pops = 0, left = 0; bool monotone = true; };                               // nearest 가 스스로 센 값
template <class Pred> std::vector<int> nearest(const std::vector<int>& a, Dir dir, Pred pred, Stats* stats = nullptr) {
    int n = a.size(); std::vector<int> res(n, -1); std::stack<int> st; Stats s;
    for (int step = 0; step < n; step++) { int i = dir == NEXT ? n - 1 - step : step;                              // NEXT 는 오른쪽에서 왼쪽으로 훑는다
        while (!st.empty() && !pred(a[st.top()], a[i])) { st.pop(); s.pops++; }                                    // 후보가 되지 못하는(조건을 만족 못 하는) top 은 이후에도 쓸모없다
        s.monotone = s.monotone && (st.empty() || pred(a[st.top()], a[i]));                                      // ② 새 원소를 얹기 전, top 은 규칙을 만족해야 한다
        res[i] = st.empty() ? -1 : st.top(); st.push(i); s.pushes++; }
    s.left = (long)st.size(); if (stats) *stats = s; return res;
}
template <class Pred> std::vector<int> brute(const std::vector<int>& a, Dir dir, Pred pred) {
    int n = a.size(); std::vector<int> res(n, -1); for (int i = 0; i < n; i++) { if (dir == NEXT) { for (int j = i + 1; j < n; j++) if (pred(a[j], a[i])) { res[i] = j; break; } } else { for (int j = i - 1; j >= 0; j--) if (pred(a[j], a[i])) { res[i] = j; break; } } } return res;
}
std::string monoTrace(const std::vector<int>& a) {                     // 그림: 오른쪽에서 왼쪽으로 훑으며 "다음으로 큰 값" 을 찾는 스택의 변화 (스택은 바닥 -> 꼭대기 값)
    std::stack<int> st; std::string trace; std::vector<int> pops;
    for (int i = (int)a.size() - 1; i >= 0; --i) {
        std::string popped;
        while (!st.empty() && !(a[st.top()] > a[i])) { popped += (popped.empty() ? "" : " ") + std::to_string(a[st.top()]); st.pop(); }     // 꼭대기가 이 값보다 크지 않으면 영영 답이 될 수 없다
        std::string next = st.empty() ? "-" : std::to_string(a[st.top()]); st.push(i);
        std::vector<int> vals; for (std::stack<int> c = st; !c.empty(); c.pop()) vals.insert(vals.begin(), a[c.top()]);
        std::string s; for (int v : vals) s += (s.empty() ? "" : " ") + std::to_string(v);
        trace += "a[" + std::to_string(i) + "]=" + std::to_string(a[i]) + " popped=[" + popped + "] next=" + next + " stack=[" + s + "]\n";
    }
    return trace;
}
int main() {
    {   const std::vector<int> a = {2, 1, 2, 4, 3};
        const std::string pic = "a[4]=3 popped=[] next=- stack=[3]\na[3]=4 popped=[3] next=- stack=[4]\na[2]=2 popped=[] next=4 stack=[4 2]\n"
                                "a[1]=1 popped=[] next=2 stack=[4 2 1]\na[0]=2 popped=[1 2] next=4 stack=[4 2]\n";
        assert(monoTrace(a) == pic);                                                                  // 스택은 바닥에서 꼭대기로 갈수록 값이 작아진다(단조). 새 값에 가려진 후보는 한 번 꺼내지면 끝
        std::vector<int> want = nearest(a, NEXT, [](int c, int v) { return c > v; });                  // 같은 알고리즘의 본 구현: 다음으로 큰 값의 위치
        assert((want == std::vector<int>{3, 2, 3, -1, -1}));
        std::cout << pic; }
    std::mt19937 rng(21); long popsMax = 0;
    auto greater = [](int c, int v) { return c > v; }; auto greaterEq = [](int c, int v) { return c >= v; }; auto less = [](int c, int v) { return c < v; }; auto lessEq = [](int c, int v) { return c <= v; };
    int strictDiffers = 0, pairs = 0;
    for (int t = 0; t < 3000; t++) { int n = rng() % 30; std::vector<int> a(n); for (int& x : a) x = rng() % 8;
        for (Dir d : {NEXT, PREV}) {
            auto check = [&](auto pred) { Stats s; std::vector<int> got = nearest(a, d, pred, &s); assert(got == brute(a, d, pred)); assert(s.pushes == n && s.pops <= n && s.pops + s.left == s.pushes && s.monotone); popsMax = std::max(popsMax, s.pops); return got; };   // ① ② ③
            std::vector<int> g = check(greater), ge = check(greaterEq); check(less); check(lessEq);
            strictDiffers += g != ge; pairs++; } }                                                                                                                                                                                                                   // ④
    assert(strictDiffers > 100);
    { std::vector<int> a = {2, 1, 2, 4, 3}; auto ng = nearest(a, NEXT, greater); assert((ng == std::vector<int>{3, 2, 3, -1, -1})); auto nge = nearest(a, NEXT, greaterEq); assert((nge == std::vector<int>{2, 2, 3, -1, -1})); }
    std::cout << "MonotonicStack: all four nearest-greater/smaller variants (strict and non-strict) matched brute force on 3000 random arrays with many duplicates; pops never exceeded N (max " << popsMax << " for N<=29); strict vs non-strict differed on " << strictDiffers << " of " << pairs << " (array, direction) pairs" << std::endl; return 0;
}
// Time Complexity: O(N) (각 원소가 한 번 push, 한 번 pop)
// Space Complexity: O(N)
```
## NextGreaterElement()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <stack>
#include <unordered_map>
#include <vector>
#include <cassert>

// 다음 큰 원소(NextGreaterElement): 각 원소의 오른쪽에서 자신보다 큰 첫 원소(없으면 −1). 왼쪽에서 오른쪽으로 훑으며 아직 답을 못 찾은 원소의 인덱스를 스택에 쌓고, 새 원소 x 가 스택 top 보다 크면 그 top 의 답이 x 라고 확정하고 pop 한다(단조 감소 스택). 각 원소가 한 번씩만 들어가고 나가므로 O(N).
// 변형 둘. ① 원형 배열: 끝 다음에 처음으로 이어진다. 배열을 두 번 훑는다(인덱스 mod N) — 둘째 바퀴는 답이 없는 원소만 처리한다. ② 질의 배열: A 의 부분집합 B 의 각 원소가 A 에서 갖는 다음 큰 원소(LeetCode 496). A 를 한 번 훑어 해시맵에 value → 답 을 저장하고 B 는 조회만 한다(값이 서로 다르다고 가정).
// 검증: 무작위 배열에서 ① 선형 버전이 O(N²) 브루트포스와 같다(중복 포함) ② 원형 버전이 "배열을 두 배로 이어 붙여 브루트포스" 한 것과 같다 ③ 질의 버전이 직접 검색과 같다 ④ 정렬된 증가/감소 배열의 경계 사례 ⑤ pop 횟수가 N 이하
std::vector<int> nextGreater(const std::vector<int>& a, long* pops = nullptr) {
    std::stack<int> st; std::vector<int> res(a.size(), -1); long p = 0;
    for (int i = 0; i < (int)a.size(); ++i) { while (!st.empty() && a[st.top()] < a[i]) { res[st.top()] = a[i]; st.pop(); p++; } st.push(i); }
    if (pops) *pops = p; return res;
}
std::vector<int> nextGreaterCircular(const std::vector<int>& a) {
    int n = a.size(); std::stack<int> st; std::vector<int> res(n, -1);
    for (int i = 0; i < 2 * n; ++i) { int x = a[i % n]; while (!st.empty() && a[st.top()] < x) { res[st.top()] = x; st.pop(); } if (i < n) st.push(i); }          // 첫 바퀴에서만 push, 둘째 바퀴는 남은 원소의 답을 찾는다
    return res;
}
std::vector<int> nextGreaterOfQueries(const std::vector<int>& universe, const std::vector<int>& queries) {
    std::unordered_map<int, int> ans; std::stack<int> st; for (int x : universe) { while (!st.empty() && st.top() < x) { ans[st.top()] = x; st.pop(); } st.push(x); } while (!st.empty()) { ans[st.top()] = -1; st.pop(); }
    std::vector<int> r; for (int q : queries) r.push_back(ans[q]); return r;
}
int main() {
    std::mt19937 rng(7);
    for (int t = 0; t < 3000; t++) { int n = rng() % 25; std::vector<int> a(n); for (int& x : a) x = rng() % 10; long pops = 0;
        std::vector<int> want(n, -1); for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (a[j] > a[i]) { want[i] = a[j]; break; } std::vector<int> got = nextGreater(a, &pops); assert(got == want && pops <= n);                           // ① ⑤
        std::vector<int> dbl = a; dbl.insert(dbl.end(), a.begin(), a.end()); std::vector<int> wc(n, -1); for (int i = 0; i < n; i++) for (int j = i + 1; j < i + n; j++) if (dbl[j] > a[i]) { wc[i] = dbl[j]; break; } assert(nextGreaterCircular(a) == wc); }         // ②
    for (int t = 0; t < 500; t++) { int n = 1 + rng() % 20; std::vector<int> u(n); for (int i = 0; i < n; i++) u[i] = i; std::shuffle(u.begin(), u.end(), rng); std::vector<int> q; for (int i = 0; i < n; i++) if (rng() % 2) q.push_back(u[i]);
        std::vector<int> r = nextGreaterOfQueries(u, q); for (size_t k = 0; k < q.size(); k++) { int pos = std::find(u.begin(), u.end(), q[k]) - u.begin(); int w = -1; for (int j = pos + 1; j < n; j++) if (u[j] > q[k]) { w = u[j]; break; } assert(r[k] == w); } }     // ③
    { std::vector<int> inc = {1, 2, 3, 4}, dec = {4, 3, 2, 1}; assert((nextGreater(inc) == std::vector<int>{2, 3, 4, -1}) && (nextGreater(dec) == std::vector<int>{-1, -1, -1, -1}) && nextGreater({}).empty() && (nextGreaterCircular(dec) == std::vector<int>{-1, 4, 4, 4}) && (nextGreaterCircular(std::vector<int>{1, 2, 1}) == std::vector<int>{2, -1, 2})); }          // ④
    std::cout << "NextGreaterElement: linear, circular and query variants matched brute force on 3000 + 500 random inputs; pops never exceeded N" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PreviousGreaterElement()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 이전 큰 원소(PreviousGreaterElement): 각 원소의 왼쪽에서 자신보다 큰 첫 원소의 인덱스(없으면 −1). 왼쪽부터 훑으며 스택을 "아래에서 위로 값이 줄어드는" 상태로 유지한다: x 를 넣기 전에 x 이하인 top 들을 pop 하면(그들은 이후 어떤 원소에게도 가장 가까운 큰 원소가 될 수 없다) 남은 top 이 x 의 이전 큰 원소다.
// 엄격한 큰(>)과 같아도 되는 큰(>=)의 차이가 중복에서 드러난다. 주식의 스팬(StockSpan)은 "나보다 큰 값이 처음 나타난 날 이후 며칠째" 이므로 이 문제와 같은 구조이고, 합계 구간 문제(모든 부분배열 최솟값의 합)에서는 한쪽은 엄격하게 다른 쪽은 비엄격하게 해야 같은 값을 두 번 세지 않는다 — 대칭의 열쇠다.
// 이 항목은 이전 큰/이전 작은 원소를 구하고, 이를 이용해 "모든 부분배열의 최솟값의 합"(왼쪽은 엄격 이전 작은, 오른쪽은 비엄격 다음 작은)을 O(N) 으로 계산해 O(N³) 브루트포스와 대조한다.
// 검증: ① 엄격/비엄격 이전 큰 원소가 브루트포스와 같다 ② 이전 작은 원소도 같다 ③ 부분배열 최솟값의 합이 O(N³) 브루트포스와 같다(중복 포함) ④ 경계 사례
std::vector<int> prevGreater(const std::vector<int>& a, bool strict) {
    std::stack<int> st; std::vector<int> res(a.size(), -1);
    for (int i = 0; i < (int)a.size(); ++i) { while (!st.empty() && (strict ? a[st.top()] <= a[i] : a[st.top()] < a[i])) st.pop(); res[i] = st.empty() ? -1 : st.top(); st.push(i); }
    return res;
}
std::vector<int> prevSmaller(const std::vector<int>& a, bool strict) {
    std::stack<int> st; std::vector<int> res(a.size(), -1);
    for (int i = 0; i < (int)a.size(); ++i) { while (!st.empty() && (strict ? a[st.top()] >= a[i] : a[st.top()] > a[i])) st.pop(); res[i] = st.empty() ? -1 : st.top(); st.push(i); }
    return res;
}
std::vector<int> nextSmaller(const std::vector<int>& a, bool strict) {
    std::stack<int> st; int n = a.size(); std::vector<int> res(n, n);
    for (int i = n - 1; i >= 0; --i) { while (!st.empty() && (strict ? a[st.top()] >= a[i] : a[st.top()] > a[i])) st.pop(); res[i] = st.empty() ? n : st.top(); st.push(i); }
    return res;
}
long long sumOfSubarrayMins(const std::vector<int>& a) {                                    // 각 원소가 최솟값이 되는 구간 수 = (왼쪽 거리) × (오른쪽 거리)
    int n = a.size(); auto L = prevSmaller(a, true); auto R = nextSmaller(a, false); long long total = 0; for (int i = 0; i < n; i++) total += (long long)a[i] * (i - L[i]) * (R[i] - i); return total;
}
int main() {
    std::mt19937 rng(9);
    for (int t = 0; t < 3000; t++) { int n = rng() % 25; std::vector<int> a(n); for (int& x : a) x = rng() % 8;
        for (bool strict : {true, false}) {
            std::vector<int> g(n, -1), s(n, -1);                                                                                                                                  // 브루트포스: 왼쪽으로 가며 처음 만나는 큰/작은 원소
            for (int i = 0; i < n; i++) for (int j = i - 1; j >= 0 && (g[i] < 0 || s[i] < 0); j--) { if (g[i] < 0 && (strict ? a[j] > a[i] : a[j] >= a[i])) g[i] = j; if (s[i] < 0 && (strict ? a[j] < a[i] : a[j] <= a[i])) s[i] = j; }
            assert(prevGreater(a, strict) == g && prevSmaller(a, strict) == s); }                                                                                                  // ① ② 엄격/비엄격 모두
        long long brute = 0; for (int i = 0; i < n; i++) { int mn = a[i]; for (int j = i; j < n; j++) { mn = std::min(mn, a[j]); brute += mn; } } assert(sumOfSubarrayMins(a) == brute); }                                // ③
    { std::vector<int> a = {3, 1, 2, 4}; assert((prevGreater(a, true) == std::vector<int>{-1, 0, 0, -1}) && (prevGreater({}, true).empty()) && (prevGreater(std::vector<int>{2, 2, 2}, true) == std::vector<int>{-1, -1, -1}) && (prevGreater(std::vector<int>{2, 2, 2}, false) == std::vector<int>{-1, 0, 1})); assert(sumOfSubarrayMins({3, 1, 2, 4}) == 17); }       // ④
    std::cout << "PreviousGreaterElement: strict/non-strict previous greater and smaller matched brute force on 3000 random arrays; the O(N) sum of subarray minimums equalled the O(N^3) brute force" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## LargestRectangle()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 히스토그램에서 가장 큰 직사각형(LargestRectangle): 너비 1 인 막대들의 높이가 주어질 때 막대들 안에 완전히 들어가는 가장 큰 직사각형의 넓이. 단조 증가 스택이 정석이다: 높이가 올라가는 동안 막대 인덱스를 쌓고, 더 낮은 막대 h[i] 를 만나면 top 을 pop 하며 "그 막대 높이로 만들 수 있는 최대 폭" 을 확정한다 — 폭의 왼쪽 끝은 새 top 바로 다음, 오른쪽 끝은 i−1 이다. 끝에 높이 0 짜리 막대를 하나 덧붙여 스택을 모두 비우는 센티넬 기법을 쓴다.
// 이 문제는 다른 문제의 구성 요소가 된다: 0/1 행렬에서 1 로만 이루어진 가장 큰 직사각형(MaximalRectangle)은 각 행을 "아래로 연속한 1 의 개수" 히스토그램으로 보고 행마다 이 알고리즘을 적용한다 → O(행×열).
// 검증: ① 무작위 히스토그램(중복·0 포함)에서 O(N²) 브루트포스(모든 구간의 최소 × 폭)와 같다 ② 입력 벡터를 변경하지 않음(센티넬을 복사본에 붙임) ③ 0/1 행렬에서 MaximalRectangle 이 O(R²C²) 브루트포스와 같다 ④ 경계: 빈 입력, 하나, 단조 증가/감소, 모두 같은 높이
long long largestRectangle(const std::vector<int>& heights) {
    std::vector<int> h = heights; h.push_back(0);                                              // 센티넬: 마지막에 모두 pop 되게 한다
    std::stack<int> st; long long best = 0;
    for (int i = 0; i < (int)h.size(); ++i) {
        while (!st.empty() && h[st.top()] > h[i]) { long long height = h[st.top()]; st.pop(); long long width = st.empty() ? i : i - st.top() - 1; best = std::max(best, height * width); }
        st.push(i);
    }
    return best;
}
long long maximalRectangle(const std::vector<std::vector<int>>& m) {
    if (m.empty()) return 0; std::vector<int> run(m[0].size(), 0); long long best = 0;
    for (auto& row : m) { for (size_t c = 0; c < row.size(); c++) run[c] = row[c] ? run[c] + 1 : 0; best = std::max(best, largestRectangle(run)); } return best;
}
int main() {
    std::mt19937 rng(5);
    for (int t = 0; t < 4000; t++) { int n = rng() % 16; std::vector<int> h(n); for (int& x : h) x = rng() % 7; std::vector<int> copy = h; long long brute = 0;
        for (int i = 0; i < n; i++) { int mn = h[i]; for (int j = i; j < n; j++) { mn = std::min(mn, h[j]); brute = std::max(brute, (long long)mn * (j - i + 1)); } } assert(largestRectangle(h) == brute && h == copy); }                          // ① ②
    for (int t = 0; t < 1500; t++) { int R = 1 + rng() % 6, C = 1 + rng() % 6; std::vector<std::vector<int>> m(R, std::vector<int>(C)); for (auto& row : m) for (int& x : row) x = rng() % 3 != 0; long long brute = 0;
        for (int r1 = 0; r1 < R; r1++) for (int r2 = r1; r2 < R; r2++) for (int c1 = 0; c1 < C; c1++) for (int c2 = c1; c2 < C; c2++) { bool all = true; for (int r = r1; r <= r2 && all; r++) for (int c = c1; c <= c2; c++) if (!m[r][c]) { all = false; break; } if (all) brute = std::max(brute, (long long)(r2 - r1 + 1) * (c2 - c1 + 1)); }
        assert(maximalRectangle(m) == brute); }                                                                                                                                                                            // ③
    assert(largestRectangle({}) == 0 && largestRectangle({5}) == 5 && largestRectangle({1, 2, 3, 4}) == 6 && largestRectangle({4, 3, 2, 1}) == 6 && largestRectangle({3, 3, 3, 3}) == 12 && largestRectangle({2, 1, 5, 6, 2, 3}) == 10);             // ④
    std::cout << "LargestRectangle: the single-pass monotonic-stack solution matched O(N^2) brute force on 4000 random histograms, and the row-by-row maximal rectangle matched an exhaustive search on 1500 random binary matrices" << std::endl; return 0;
}
// Time Complexity: O(N), 행렬 버전 O(R·C)
// Space Complexity: O(N)
```
## DailyTemperatures()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 일일 온도(DailyTemperatures): 각 날짜에 대해 더 따뜻한 날까지 며칠을 기다려야 하는지(없으면 0). 다음 큰 원소의 "값" 대신 "거리(인덱스 차이)" 를 구하는 문제다. 아직 답을 못 찾은 날짜의 인덱스를 스택에 쌓고, 오늘 온도가 top 날의 온도보다 높으면 그 날의 답은 오늘 − 그 날이다.
// 뒤에서부터 훑는 방법도 있다: 오른쪽에서 왼쪽으로 가며 오늘보다 같거나 낮은 날들은 pop 하면 top 이 더 따뜻한 첫날이다(답 = 거리). 두 방향이 같은 결과를 줌을 확인한다. 스택 없이 "이미 구한 답을 건너뛰며 점프" 하는 O(N) 방법(답 배열로 다음 후보를 찾음)도 있다.
// 검증: ① 무작위 온도열에서 앞→뒤 스택, 뒤→앞 스택, 점프 방식이 모두 O(N²) 브루트포스와 같다 ② 답이 0 인 날은 정확히 "그 날 이후 더 따뜻한 날이 없는" 날 — 브루트포스가 아니라 뒤에서 앞으로 한 번 훑은 접미 최댓값과 스택 해답을 대조 ③ 증가열의 답은 마지막 날만 0 이고 나머지는 모두 1, 감소열은 모두 0, 고전 예제 하나
std::vector<int> forwardStack(const std::vector<int>& t) {
    std::vector<int> ans(t.size(), 0); std::stack<int> st;
    for (int i = 0; i < (int)t.size(); ++i) { while (!st.empty() && t[st.top()] < t[i]) { ans[st.top()] = i - st.top(); st.pop(); } st.push(i); }
    return ans;
}
std::vector<int> backwardStack(const std::vector<int>& t) {
    int n = t.size(); std::vector<int> ans(n, 0); std::stack<int> st;
    for (int i = n - 1; i >= 0; --i) { while (!st.empty() && t[st.top()] <= t[i]) st.pop(); ans[i] = st.empty() ? 0 : st.top() - i; st.push(i); }
    return ans;
}
std::vector<int> jumping(const std::vector<int>& t) {                                         // 스택 없이: 이미 구한 답으로 후보를 건너뛴다
    int n = t.size(); std::vector<int> ans(n, 0);
    for (int i = n - 2; i >= 0; --i) { int j = i + 1; while (j < n && t[j] <= t[i]) { if (ans[j] == 0) { j = n; break; } j += ans[j]; } ans[i] = j < n ? j - i : 0; }
    return ans;
}
int main() {
    std::mt19937 rng(8);
    for (int t = 0; t < 4000; t++) { int n = rng() % 30; std::vector<int> a(n); for (int& x : a) x = 30 + rng() % 8; std::vector<int> want(n, 0); for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (a[j] > a[i]) { want[i] = j - i; break; }
        assert(forwardStack(a) == want && backwardStack(a) == want && jumping(a) == want);                                                                                                         // ①
        std::vector<int> f = forwardStack(a), sufMax(n + 1, -1); for (int i = n - 1; i >= 0; i--) sufMax[i] = std::max(sufMax[i + 1], a[i]);
        for (int i = 0; i < n; i++) assert((f[i] == 0) == (a[i] >= sufMax[i + 1])); }                                                                                                             // ② 0 인 날 == 뒤에 더 따뜻한 날이 없는 날 (접미 최댓값은 스택도 이중 반복도 아니다)
    { std::vector<int> inc = {1, 2, 3, 4, 5}, dec = {5, 4, 3, 2, 1}; assert((forwardStack(inc) == std::vector<int>{1, 1, 1, 1, 0}) && (forwardStack(dec) == std::vector<int>{0, 0, 0, 0, 0}) && (forwardStack({73, 74, 75, 71, 69, 72, 76, 73}) == std::vector<int>{1, 1, 4, 2, 1, 1, 0, 0})); }       // ③
    std::cout << "DailyTemperatures: forward-stack, backward-stack and jumping solutions all matched brute force on 4000 random temperature sequences" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## StockSpan()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <stack>
#include <utility>
#include <vector>
#include <cassert>

// 주식 스팬(StockSpan): 오늘 가격 이하였던 연속된 날의 수(오늘 포함). 즉 "오늘보다 가격이 높았던 가장 가까운 과거의 날" 까지의 거리다. 스택에 (가격, 스팬) 쌍을 쌓고 새 가격 p 가 오면 top 의 가격이 p 이하인 동안 pop 하며 그 스팬을 오늘 스팬에 합친다 — 합쳐진 날들은 이미 "p 이하" 라는 사실이 확정되어 다시 볼 필요가 없다. 온라인(데이터가 하나씩 들어옴)으로 동작하며 호출당 분할상환 O(1).
// 오프라인으로 전체 배열이 있을 때는 이전 큰 원소의 인덱스(PreviousGreaterElement)로 span[i] = i − prevGreater[i] 로 구할 수 있다. 두 방식은 같은 결과를 줘야 한다.
// 검증: 무작위 가격열에서 ① 온라인 StockSpanner 결과가 O(N²) 브루트포스와 같다 ② 오프라인(이전 큰 원소) 방식과 같다 ③ 스택 크기 변화: 총 pop 횟수 ≤ 호출 수 ④ LeetCode 예제(100, 80, 60, 70, 60, 75, 85 → 1, 1, 1, 2, 1, 4, 6)
class StockSpanner {
    std::stack<std::pair<int, int>> st_; long pops_ = 0;
public:
    int next(int price) { int span = 1; while (!st_.empty() && st_.top().first <= price) { span += st_.top().second; st_.pop(); pops_++; } st_.push({price, span}); return span; }
    long pops() const { return pops_; } size_t depth() const { return st_.size(); }
};
std::vector<int> offline(const std::vector<int>& p) {
    int n = p.size(); std::vector<int> prevGreater(n, -1), span(n); std::stack<int> st;
    for (int i = 0; i < n; i++) { while (!st.empty() && p[st.top()] <= p[i]) st.pop(); prevGreater[i] = st.empty() ? -1 : st.top(); st.push(i); span[i] = i - prevGreater[i]; }
    return span;
}
int main() {
    std::mt19937 rng(10);
    for (int t = 0; t < 3000; t++) { int n = rng() % 40; std::vector<int> p(n); for (int& x : p) x = 1 + rng() % 12; StockSpanner ss; std::vector<int> online; for (int x : p) online.push_back(ss.next(x));
        std::vector<int> want(n); for (int i = 0; i < n; i++) { int s = 1; for (int j = i - 1; j >= 0 && p[j] <= p[i]; j--) s++; want[i] = s; }
        assert(online == want && offline(p) == want && ss.pops() <= n); }                                                                                                                               // ① ② ③
    { StockSpanner ss; std::vector<int> got; for (int x : {100, 80, 60, 70, 60, 75, 85}) got.push_back(ss.next(x)); assert((got == std::vector<int>{1, 1, 1, 2, 1, 4, 6})); }                                // ④
    { StockSpanner ss; for (int i = 1; i <= 1000; i++) ss.next(i); assert(ss.depth() == 1 && ss.pops() == 999); StockSpanner d; for (int i = 1000; i >= 1; i--) d.next(i); assert(d.depth() == 1000 && d.pops() == 0); }          // 증가열은 매번 모두 합치고, 감소열은 합칠 것이 없다
    std::cout << "StockSpan: the online one-stack spanner matched brute force and the offline previous-greater formula on 3000 random price series; total pops stayed <= the number of calls" << std::endl; return 0;
}
// Time Complexity: next() 분할상환 O(1)
// Space Complexity: O(N)
```

# Part 7. 특수 스택
## MinStack()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 최솟값 스택(MinStack): push, pop, top 에 더해 현재 스택의 최솟값 getMin() 을 O(1) 에 돌려주는 스택이다. 최솟값만 변수로 들고 있으면 최솟값을 pop 했을 때 새 최솟값을 알 수 없으므로 "각 시점의 최솟값 이력" 을 보관해야 한다.
// 두 가지 구현. ① 보조 스택: 값을 push 할 때 현재 최솟값 이하이면 보조 스택에도 push, pop 한 값이 보조 스택의 top 과 같으면 보조에서도 pop. 같은 값이 여러 번 들어오는 경우를 위해 "이하(<=)" 로 비교해야 한다(< 로 하면 같은 최솟값 두 개 중 하나를 pop 할 때 최솟값을 잃는다). ② 차이 부호화: 스택 하나에 (값 − 그 시점 최솟값 이전의 최솟값) 형태로 저장하고 최솟값 변수만 별도로 들어, 보조 스택 없이 O(1) 추가 공간을 쓴다 — 값 범위가 넓어 오버플로할 수 있으므로 long long 으로 저장한다.
// 검증: 무작위 push/pop/top/getMin 6 만 번을 벡터를 매번 훑어 최솟값을 구하는 브루트포스와 대조 ① 보조 스택 방식 ② 차이 부호화 방식 ③ 같은 값이 여러 개일 때 "<" 비교(잘못된 구현)가 실제로 틀린다는 반례 ④ 극단값 INT_MIN/INT_MAX 가 섞여도 정확
class MinStack {
    std::stack<int> s_, mins_;
public:
    void push(int v) { s_.push(v); if (mins_.empty() || v <= mins_.top()) mins_.push(v); }
    void pop() { if (s_.top() == mins_.top()) mins_.pop(); s_.pop(); }
    int top() const { return s_.top(); } int getMin() const { return mins_.top(); } bool empty() const { return s_.empty(); } size_t auxSize() const { return mins_.size(); }
};
class MinStackBuggy {                                                                          // 틀린 구현: '<' 로 비교
    std::stack<int> s_, mins_;
public:
    void push(int v) { s_.push(v); if (mins_.empty() || v < mins_.top()) mins_.push(v); }
    void pop() { if (s_.top() == mins_.top()) mins_.pop(); s_.pop(); }
    int getMin() const { return mins_.empty() ? INT_MAX : mins_.top(); }
};
class MinStackDelta {                                                                          // 보조 스택 없이 차이만 저장
    std::stack<long long> s_; long long min_ = 0;
public:
    void push(int v) { if (s_.empty()) { s_.push(0); min_ = v; } else { s_.push((long long)v - min_); if (v < min_) min_ = v; } }       // 저장값 < 0 이면 v 가 새 최솟값
    void pop() { long long d = s_.top(); s_.pop(); if (d < 0) min_ = min_ - d; }                                                         // 새 최솟값이었다면 이전 최솟값 복원
    int top() const { long long d = s_.top(); return (int)(d < 0 ? min_ : min_ + d); } int getMin() const { return (int)min_; } bool empty() const { return s_.empty(); }
};
int main() {
    std::mt19937 rng(12); MinStack a; MinStackDelta b; std::vector<int> ref; int buggyWrong = 0;
    for (int step = 0; step < 60000; step++) {
        if (rng() % 5 < 3 || ref.empty()) { int v = (rng() % 20 == 0) ? (rng() & 1 ? INT_MIN : INT_MAX) : (int)(rng() % 10); a.push(v); b.push(v); ref.push_back(v); } else { a.pop(); b.pop(); ref.pop_back(); }
        if (!ref.empty()) { int mn = *std::min_element(ref.begin(), ref.end()); assert(a.getMin() == mn && b.getMin() == mn && a.top() == ref.back() && b.top() == ref.back()); } else assert(a.empty() && b.empty());          // ① ② ④
        if (ref.size() > 200) while (ref.size() > 100) { a.pop(); b.pop(); ref.pop_back(); }
    }
    { MinStackBuggy bad; bad.push(2); bad.push(2); bad.push(5); bad.pop(); bad.pop(); /* 스택: [2], 최솟값은 2 여야 한다 */ buggyWrong += bad.getMin() != 2; MinStack good; good.push(2); good.push(2); good.push(5); good.pop(); good.pop(); assert(good.getMin() == 2 && buggyWrong == 1); }       // ③ '<' 비교는 같은 최솟값이 겹치면 틀린다
    { MinStack g; for (int i = 0; i < 100; i++) g.push(5); assert(g.auxSize() == 100); MinStackDelta d; d.push(INT_MAX); d.push(INT_MIN); assert(d.getMin() == INT_MIN); d.pop(); assert(d.getMin() == INT_MAX && d.top() == INT_MAX); }
    std::cout << "MinStack: auxiliary-stack and delta-encoded implementations matched a brute-force minimum over 60000 random operations including INT_MIN/INT_MAX; the strict-comparison variant lost the minimum when equal minima repeated" << std::endl; return 0;
}
// Time Complexity: push·pop·top·getMin 모두 O(1)
// Space Complexity: 보조 스택 방식 O(N), 차이 부호화 O(1) 추가
```
## MaxStack()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 최댓값 스택(MaxStack): push, pop, top, peekMax 를 O(1) 에, 거기에 최댓값 원소를 제거하는 popMax 를 지원하는 스택(LeetCode 716). peekMax 는 MinStack 과 대칭인 보조 스택으로 O(1) 이다. popMax 는 까다롭다: 최댓값이 스택 중간에 있으므로 그 위의 원소를 임시 스택으로 옮겼다가 최댓값을 제거하고 다시 push 해야 한다 — 이 방식은 popMax 가 O(N) 이다. 같은 값이 여럿이면 가장 위(가장 최근)의 것을 제거한다.
// O(log N) 으로 만드는 방법: 이중 연결 리스트에 스택을 저장하고(위치를 가리키는 반복자는 삭제해도 다른 반복자를 무효화하지 않음), 값 → 그 값이 있는 노드들의 반복자 목록을 std::map 에 둔다. 최댓값은 map 의 마지막 키, 그 키의 마지막 반복자가 가장 위의 최댓값 노드다. 어디서든 O(1) 삭제가 가능하고 map 조작이 O(log N).
// 검증: 무작위 push/pop/top/peekMax/popMax 5 만 번을 벡터 브루트포스(popMax 는 가장 위의 최댓값 위치를 직접 찾아 삭제)와 대조: ① 보조 스택 + 임시 스택 방식 ② 연결 리스트 + 맵 방식(둘 다) ③ 같은 값 여러 개에서 가장 최근의 것이 제거됨 ④ 연산 후 스택 순서가 정확히 유지됨(popMax 로 중간 원소가 빠져도 나머지의 상대 순서 불변)
class MaxStackSimple {
    std::stack<int> s_, mx_;
public:
    void push(int v) { s_.push(v); if (mx_.empty() || v >= mx_.top()) mx_.push(v); }
    int pop() { int v = s_.top(); s_.pop(); if (v == mx_.top()) mx_.pop(); return v; }
    int top() const { return s_.top(); } int peekMax() const { return mx_.top(); } bool empty() const { return s_.empty(); }
    int popMax() { int m = mx_.top(); std::stack<int> buf; while (s_.top() != m) { buf.push(pop()); } pop(); while (!buf.empty()) { push(buf.top()); buf.pop(); } return m; }       // 최댓값 위의 원소를 잠시 치웠다 되돌린다: O(N)
};
class MaxStackFast {
    std::list<int> l_; std::map<int, std::vector<std::list<int>::iterator>> where_;
public:
    void push(int v) { l_.push_back(v); where_[v].push_back(std::prev(l_.end())); }
    int pop() { int v = l_.back(); auto& w = where_[v]; w.pop_back(); if (w.empty()) where_.erase(v); l_.pop_back(); return v; }
    int top() const { return l_.back(); } int peekMax() const { return where_.rbegin()->first; } bool empty() const { return l_.empty(); }
    int popMax() { auto it = std::prev(where_.end()); int v = it->first; auto node = it->second.back(); it->second.pop_back(); if (it->second.empty()) where_.erase(it); l_.erase(node); return v; }    // 가장 위의 최댓값 노드를 O(log N) 에 제거
    std::vector<int> contents() const { return std::vector<int>(l_.begin(), l_.end()); }
};
int main() {
    std::mt19937 rng(14); MaxStackSimple a; MaxStackFast b; std::vector<int> ref; long popMaxCalls = 0;
    for (int step = 0; step < 50000; step++) {
        int op = rng() % 10;
        if (op < 5 || ref.empty()) { int v = rng() % 12; a.push(v); b.push(v); ref.push_back(v); }
        else if (op < 7) { int x = a.pop(), y = b.pop(); assert(x == ref.back() && y == ref.back()); ref.pop_back(); }
        else if (op < 9) { int mx = *std::max_element(ref.begin(), ref.end()); size_t at = ref.size() - 1; while (ref[at] != mx) at--; int x = a.popMax(), y = b.popMax(); assert(x == mx && y == mx); ref.erase(ref.begin() + at); popMaxCalls++; }       // 가장 위의 최댓값 제거
        else { assert(a.top() == ref.back() && b.top() == ref.back()); }
        if (!ref.empty()) { assert(a.peekMax() == *std::max_element(ref.begin(), ref.end()) && b.peekMax() == a.peekMax() && b.contents() == ref); } else assert(a.empty() && b.empty());          // ④ 순서 유지
        if (ref.size() > 300) while (ref.size() > 150) { a.pop(); b.pop(); ref.pop_back(); }
    }
    { MaxStackFast s; s.push(5); s.push(1); s.push(5); int m1 = s.popMax(); assert(m1 == 5 && s.contents() == (std::vector<int>{5, 1})); MaxStackSimple t; t.push(5); t.push(1); t.push(5); int m2 = t.popMax(); assert(m2 == 5 && t.top() == 1); }          // ③ 최근의 5 가 먼저 제거
    std::cout << "MaxStack: both the two-stack and the list-plus-map implementations matched a brute-force vector over 50000 random operations (" << popMaxCalls << " popMax calls) with exact element order preserved" << std::endl; return 0;
}
// Time Complexity: 보조 스택 방식 push·pop·top·peekMax O(1), popMax O(N) / 리스트+맵 방식 popMax 포함 O(log N)
// Space Complexity: O(N)
```
## TwoStacksInArray()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 한 배열에 스택 두 개(TwoStacksInArray): 두 스택을 따로 용량 N/2 씩 잡으면 한쪽이 가득 차도 다른 쪽의 빈 칸을 못 쓴다. 한 배열의 양 끝에서 마주 보며 자라게 하면 — 스택 1 은 왼쪽 끝에서 오른쪽으로, 스택 2 는 오른쪽 끝에서 왼쪽으로 — 두 스택의 크기 합이 N 이 될 때까지만 거절되어 공간을 100% 쓸 수 있다.
// 경계: 비었을 때 top1 = −1, top2 = N. 가득 참 조건은 top1 + 1 == top2 (둘이 맞닿음). 한쪽이 전부를 차지할 수도 있다. 비어 있는 쪽 pop 은 거절한다.
// 비교 방식: 짝수 칸은 스택 1, 홀수 칸은 스택 2 로 번갈아 쓰는 인터리브 방식은 한 스택당 최대 N/2 개라 공간을 낭비한다.
// 검증: 무작위 push1/push2/pop1/pop2/peek 6 만 번을 std::stack 두 개(합이 N 을 넘으면 거절하는 규칙)와 대조: ① 모든 결과와 크기 일치 ② 한 스택이 N 개를 독점 가능 ③ 합이 N 일 때 어느 쪽 push 든 거절 ④ 인터리브 방식은 한쪽이 N/2 에서 막힘
class TwoStacks {
    std::vector<int> a_; int top1_, top2_;
public:
    explicit TwoStacks(int n) : a_(n), top1_(-1), top2_(n) {}
    bool full() const { return top1_ + 1 == top2_; }
    bool push1(int x) { if (full()) return false; a_[++top1_] = x; return true; } bool push2(int x) { if (full()) return false; a_[--top2_] = x; return true; }
    bool pop1(int& out) { if (top1_ < 0) return false; out = a_[top1_--]; return true; } bool pop2(int& out) { if (top2_ >= (int)a_.size()) return false; out = a_[top2_++]; return true; }
    bool peek1(int& out) const { if (top1_ < 0) return false; out = a_[top1_]; return true; } bool peek2(int& out) const { if (top2_ >= (int)a_.size()) return false; out = a_[top2_]; return true; }
    int size1() const { return top1_ + 1; } int size2() const { return (int)a_.size() - top2_; }
};
class Interleaved {                                                                             // 비교용: 짝수 칸 / 홀수 칸
    std::vector<int> a_; int n1_ = 0, n2_ = 0;
public:
    explicit Interleaved(int n) : a_(n) {}
    bool push1(int x) { int idx = 2 * n1_; if (idx >= (int)a_.size()) return false; a_[idx] = x; n1_++; return true; } bool push2(int x) { int idx = 2 * n2_ + 1; if (idx >= (int)a_.size()) return false; a_[idx] = x; n2_++; return true; }
};
int main() {
    const int N = 50; std::mt19937 rng(6); TwoStacks t(N); std::stack<int> r1, r2;
    for (int step = 0; step < 60000; step++) {
        int op = rng() % 6; int v = rng() % 1000, out = -1;
        if (op == 0) { bool ok = t.push1(v); assert(ok == (r1.size() + r2.size() < (size_t)N)); if (ok) r1.push(v); }
        else if (op == 1) { bool ok = t.push2(v); assert(ok == (r1.size() + r2.size() < (size_t)N)); if (ok) r2.push(v); }
        else if (op == 2) { bool ok = t.pop1(out); assert(ok == !r1.empty()); if (ok) { assert(out == r1.top()); r1.pop(); } }
        else if (op == 3) { bool ok = t.pop2(out); assert(ok == !r2.empty()); if (ok) { assert(out == r2.top()); r2.pop(); } }
        else { bool ok1 = t.peek1(out); assert(ok1 == !r1.empty() && (!ok1 || out == r1.top())); bool ok2 = t.peek2(out); assert(ok2 == !r2.empty() && (!ok2 || out == r2.top())); }
        assert((size_t)t.size1() == r1.size() && (size_t)t.size2() == r2.size() && t.full() == (r1.size() + r2.size() == (size_t)N));                        // ①
    }
    { TwoStacks one(10); int pushed = 0; while (one.push1(pushed)) pushed++; bool o2 = one.push2(0); assert(pushed == 10 && !o2 && one.size2() == 0); TwoStacks two(10); pushed = 0; while (two.push2(pushed)) pushed++; bool t1 = two.push1(0); assert(pushed == 10 && !t1); }       // ② ③
    { Interleaved il(10); int pushed = 0; while (il.push1(pushed)) pushed++; assert(pushed == 5); }                                                                                                                // ④ 한 스택이 N/2 에서 막힘
    std::cout << "TwoStacksInArray: two stacks growing toward each other matched two std::stack models for 60000 operations; one stack can use all " << N << " cells while the interleaved layout stops at half" << std::endl; return 0;
}
// Time Complexity: push·pop·peek O(1)
// Space Complexity: O(N) — 두 스택이 공간을 공유하므로 낭비 없음
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
        if (step % 1000 == 0) for (int j = 0; j < K; j++) { assert(m.sizeOf(j) == ref[j].size()); int v = 0; bool pk = m.peek(j, v); assert(pk == !ref[j].empty() && (ref[j].empty() || v == ref[j].top())); } } }          // ①
    { MultiStack m(3, 30); int pushed = 0; while (m.push(0, pushed)) pushed++; bool r1 = m.push(1, 0), r2 = m.push(2, 0); assert(pushed == 30 && !r1 && !r2); }                                                  // ③ 한 스택이 전체를 독점
    { PartitionedStacks p(3, 30); int pushed = 0; while (p.push(0, pushed)) pushed++; assert(pushed == 10); }                                                                               // ④ 균등 분할은 10 개에서 거절
    { MultiStack m(2, 4); for (int i = 0; i < 4; i++) { bool ok = m.push(0, i); assert(ok); } bool full = m.push(1, 9); assert(!full); int v = 0; bool g = m.pop(0, v); assert(g && v == 3); bool p9 = m.push(1, 9), pk = m.peek(1, v); assert(p9 && pk && v == 9); }              // ⑤ 돌려받은 칸을 다른 스택이 쓴다
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
#include <random>

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
    // ⑤ 무작위 점화식 f(n) = f(n−a) + f(n−b) (a, b ∈ {1,2,3}, f(n<3) = n) 30 개 × n ≤ 11: 실제 재귀 로그 == 프레임 스택 로그, 호출 수 C(n) = 1 + C(n−a) + C(n−b), 최대 깊이 D(n) = 1 + max(D(n−a), D(n−b))
    std::mt19937 rng(4); long total = 0;
    for (int trial = 0; trial < 30; ++trial) {
        int a = 1 + (int)(rng() % 3), b = 1 + (int)(rng() % 3);
        struct Rec { int a, b; std::vector<std::string>* log; int depth = 0, maxDepth = 0;
            long f(int n) { log->push_back("call " + std::to_string(n)); depth++; maxDepth = std::max(maxDepth, depth); long r = n < 3 ? n : f(n - a) + f(n - b); depth--; log->push_back("ret " + std::to_string(n) + "=" + std::to_string(r)); return r; } };
        struct SimFrame { int n, step; long first; };
        for (int n = 0; n <= 11; ++n) {
            std::vector<std::string> real, sim; Rec rec{a, b, &real}; long want = rec.f(n);
            std::vector<SimFrame> st{{n, 0, 0}}; sim.push_back("call " + std::to_string(n)); long ret = 0; int sdepth = 0;
            while (!st.empty()) {
                sdepth = std::max(sdepth, (int)st.size()); SimFrame& f = st.back();
                if (f.step == 0) { if (f.n < 3) { ret = f.n; sim.push_back("ret " + std::to_string(f.n) + "=" + std::to_string(ret)); st.pop_back(); } else { f.step = 1; int m = f.n - a; st.push_back({m, 0, 0}); sim.push_back("call " + std::to_string(m)); } }
                else if (f.step == 1) { f.first = ret; f.step = 2; int m = f.n - b; st.push_back({m, 0, 0}); sim.push_back("call " + std::to_string(m)); }
                else { ret = f.first + ret; sim.push_back("ret " + std::to_string(f.n) + "=" + std::to_string(ret)); st.pop_back(); }
            }
            assert(ret == want && real == sim && sdepth == rec.maxDepth);
            long calls = 0; for (auto& l : real) calls += l[0] == 'c'; long C[16]; int D[16]; for (int k = 0; k <= n; ++k) { if (k < 3) { C[k] = 1; D[k] = 1; } else { C[k] = 1 + C[k - a] + C[k - b]; D[k] = 1 + std::max(D[k - a], D[k - b]); } }
            assert(calls == C[n] && rec.maxDepth == D[n]); total += calls;
        }
    }
    // ⑥ 하노이 탑: 이동 열 = 재귀 로그, 이동 수 2^n − 1, 호출 스택 깊이 n + 1 — 그리고 깊은 재귀 합계는 명시적 스택이면 호출 스택이 넘치지 않는다(깊이 200 만)
    for (int n = 1; n <= 12; ++n) {
        std::vector<std::string> moves; std::vector<int> depthSeen; int maxD = 0;
        struct H { std::vector<std::string>& m; int& maxD; void go(int k, char from, char to, char via, int d) { maxD = std::max(maxD, d); if (k == 0) return; go(k - 1, from, via, to, d + 1); m.push_back(std::string(1, from) + ">" + to); go(k - 1, via, to, from, d + 1); } } h{moves, maxD};
        h.go(n, 'A', 'C', 'B', 1);
        std::vector<std::string> sim; struct F { int k; char from, to, via; int stage; }; std::vector<F> st{{n, 'A', 'C', 'B', 0}};
        while (!st.empty()) { F f = st.back(); st.pop_back(); if (f.k == 0) continue; if (f.stage == 0) { st.push_back({f.k, f.from, f.to, f.via, 1}); st.push_back({f.k - 1, f.from, f.via, f.to, 0}); } else { sim.push_back(std::string(1, f.from) + ">" + f.to); st.push_back({f.k - 1, f.via, f.to, f.from, 0}); } }
        assert(moves == sim && moves.size() == (1u << n) - 1 && maxD == n + 1);
    }
    { const long N = 2000000; std::vector<long> stack; long acc = 0; for (long k = N; k >= 1; --k) stack.push_back(k); size_t peak = stack.size(); while (!stack.empty()) { acc += stack.back(); stack.pop_back(); } assert(acc == N * (N + 1) / 2 && peak == (size_t)N); }
    realLog.clear(); realDepth = realMax = 0; fibReal(3); std::cout << "CallStack: " << total << " calls of 30 random recurrences matched the frame-stack simulation, Hanoi moves matched for n <= 12, a 2,000,000-deep sum ran on an explicit stack; trace of fib(3): "; for (auto& l : realLog) std::cout << l << "; "; std::cout << std::endl;
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
// audit: closed-form (프레임 간격 차이 = 지역 배열 크기 차이)
//  ⑥ 지역 배열을 32·64·128·256·512·1024 바이트로 바꿔 가며 잰 프레임 간격이 (40 번 재귀 내내 일정하고) 단조 증가하며, 이웃한 두 크기의 간격 차이가 배열 크기 차이와 ±64 바이트 안에서 같다 — 컴파일러가 배열을 줄이지 못하도록 주소를 asm 으로 내보낸다
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
template <int N> NOINLINE long sizedFrame(int depth) { volatile char buf[N]; asm volatile("" : : "r"(buf) : "memory"); buf[0] = (char)depth; addrs.push_back((std::uintptr_t)&buf[0]); if (depth == 0) return buf[0]; long r = sizedFrame<N>(depth - 1); return r + buf[0]; }
template <int N> std::uintptr_t strideFor() { addrs.clear(); sizedFrame<N>(40); auto g = gaps(); for (std::size_t i = 1; i < g.size(); i++) assert(g[i] == g[0]); return g[0]; }     // 40 번 재귀의 프레임 간격은 모두 같다
int main() {
    addrs.clear(); smallFrame(50); auto gs = gaps(); bool descending = true; for (std::size_t i = 1; i < addrs.size(); i++) descending &= addrs[i] < addrs[i - 1]; assert(descending);                                              // ① 스택이 아래로 자란다
    std::uintptr_t smallBytes = gs[10]; assert(smallBytes >= 16 && smallBytes <= 512);                                                                                                                           // ②
    addrs.clear(); bigFrame(50); auto gb = gaps(); std::uintptr_t bigBytes = gb[10]; assert(bigBytes >= smallBytes + 400);                                                                                      // ③ 지역 배열 512 B 만큼 프레임이 커진다
    bool uniform = true; for (std::size_t i = 1; i < gs.size(); i++) uniform &= gs[i] == gs[0]; for (std::size_t i = 1; i < gb.size(); i++) uniform &= gb[i] == gb[0]; assert(uniform);                           // ④ 모든 재귀 단계의 프레임이 같은 크기
    std::size_t predictedSmall = 8u * 1024 * 1024 / smallBytes, predictedBig = 8u * 1024 * 1024 / bigBytes; assert(predictedSmall > 10000 && predictedBig > 1000 && predictedSmall > predictedBig);                  // ⑤ 예측 최대 깊이
    {   std::uintptr_t s32 = strideFor<32>(), s64 = strideFor<64>(), s128 = strideFor<128>(), s256 = strideFor<256>(), s512 = strideFor<512>(), s1024 = strideFor<1024>();            // ⑥ 지역 배열 크기를 바꿔 가며
        auto near = [](std::uintptr_t d, int expect) { return (long)d >= expect - 64 && (long)d <= expect + 64; };
        assert(s32 < s64 && s64 < s128 && s128 < s256 && s256 < s512 && s512 < s1024);
        assert(near(s64 - s32, 32) && near(s128 - s64, 64) && near(s256 - s128, 128) && near(s512 - s256, 256) && near(s1024 - s512, 512)); }                                       // 프레임 크기 차이 = 지역 배열 크기 차이 (±64: 정렬)
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
#include <numeric>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// 재귀의 시뮬레이션: 모든 재귀 함수는 "명시적 스택 + 반복문" 으로 바꿀 수 있다. 방법: 호출 하나를 프레임 구조체(매개변수 + 지금 어디까지 했는지 나타내는 상태 번호)로 만들어 스택에 쌓고, 반복문이 맨 위 프레임을 꺼내 상태에 따라 한 단계 진행한다. 재귀 호출 = 새 프레임 push, 반환 = pop 하고 반환값을 호출한 프레임에 전달.
// 이 기법의 이유: ① 호출 스택 깊이 제한(수십만 단계 재귀)에서 벗어난다 ② 실행을 중간에 멈추고 재개하거나 상태를 저장·검사할 수 있다 ③ 컴파일러가 하는 일을 이해하게 된다.
// 이 항목은 세 가지 재귀 함수를 시뮬레이션해 재귀 구현과 정확히 같은 결과·이동 순서를 내는지 확인한다. 하노이 탑(이동 순서가 같아야 한다), 아커만 함수(A(2,3)=9, A(3,3)=61: 극단적으로 깊은 재귀), 이진 트리의 중위 순회(왼쪽 → 자신 → 오른쪽).
//  ④ N-Queens(n = 1..10) 해의 수가 재귀·명시적 스택·알려진 값(1, 0, 0, 2, 10, 4, 40, 92, 352, 724)과 같다  ⑤ 교환식 순열 생성의 *출력 순서*가 n ≤ 7 의 모든 경우에 재귀와 명시적 스택에서 같고 개수가 n!
// 검증: ① 하노이 n=1..12 의 이동 목록이 재귀와 같고 이동 횟수 = 2ⁿ−1 ② 아커만 (m, n) 작은 값들이 재귀와 같고 최대 스택 크기 기록 ③ 무작위 이진 트리의 중위 순회 결과가 재귀와 같다 ④ 하노이 n=20 의 시뮬레이션이 재귀 없이 완주 (이동 2^20−1 번)
// audit: differential (재귀 구현이 독립 기준: 하노이 이동 목록, 아커만 값, 중위 순서, N-Queens 수와 순열 생성 순서)
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
long queensRec(int n, int row, unsigned cols, unsigned d1, unsigned d2) { if (row == n) return 1; long c = 0; for (int col = 0; col < n; ++col) { unsigned a = 1u << col, b = 1u << (row + col), d = 1u << (row - col + n - 1); if ((cols & a) || (d1 & b) || (d2 & d)) continue; c += queensRec(n, row + 1, cols | a, d1 | b, d2 | d); } return c; }
struct QFrame { int row, col; unsigned cols, d1, d2; };
long queensSim(int n) { long count = 0; std::vector<QFrame> st = {{0, 0, 0, 0, 0}};                                                       // 프레임 = (행, 다음에 시도할 열, 점유 비트들)
    while (!st.empty()) { QFrame f = st.back(); if (f.row == n) { ++count; st.pop_back(); continue; } if (f.col == n) { st.pop_back(); continue; }
        st.back().col++; unsigned a = 1u << f.col, b = 1u << (f.row + f.col), d = 1u << (f.row - f.col + n - 1); if ((f.cols & a) || (f.d1 & b) || (f.d2 & d)) continue; st.push_back({f.row + 1, 0, f.cols | a, f.d1 | b, f.d2 | d}); }
    return count; }
void permRec(std::vector<int>& a, int k, std::vector<std::vector<int>>& out) { if (k == (int)a.size()) { out.push_back(a); return; } for (int i = k; i < (int)a.size(); ++i) { std::swap(a[k], a[i]); permRec(a, k + 1, out); std::swap(a[k], a[i]); } }
struct PFrame { int k, i; bool swapped; };
std::vector<std::vector<int>> permSim(int n) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); std::vector<std::vector<int>> out; std::vector<PFrame> st = {{0, 0, false}};     // 자식에서 돌아오면 교환을 되돌리고 다음 i
    while (!st.empty()) { PFrame& f = st.back(); if (f.k == n) { out.push_back(a); st.pop_back(); continue; } if (f.swapped) { std::swap(a[f.k], a[f.i]); f.swapped = false; ++f.i; } if (f.i >= n) { st.pop_back(); continue; }
        std::swap(a[f.k], a[f.i]); f.swapped = true; int k = f.k; st.push_back({k + 1, k + 1, false}); }
    return out; }
int main() {
    for (int n = 1; n <= 12; n++) { Moves a, b = hanoiSim(n); hanoiRec(n, 1, 3, 2, a); assert(a == b && a.size() == (std::size_t)((1 << n) - 1)); }                              // ①
    for (long m = 0; m <= 3; m++) for (long n = 0; n <= 3; n++) { std::size_t peak = 0; long viaRec = ackRec(m, n), viaSim = ackSim(m, n, &peak); assert(viaRec == viaSim); } std::size_t pk = 0; long a23 = ackSim(2, 3, nullptr), a33 = ackSim(3, 3, &pk); assert(a23 == 9 && a33 == 61 && pk > 3);          // ②
    for (int t = 0; t < 100; t++) { std::vector<T*> pool; unsigned seed = 17u * t + 3u; T* root = build(1, 1 + t * 3, pool, seed); std::vector<int> a, b = inorderSim(root); inorderRec(root, a); assert(a == b); for (T* p : pool) delete p; }          // ③
    { Moves big = hanoiSim(20); assert(big.size() == (1u << 20) - 1); }                                                                                                                                   // ④
    {   const long known[] = {1, 0, 0, 2, 10, 4, 40, 92, 352, 724}; for (int n = 1; n <= 10; ++n) { long rec = queensRec(n, 0, 0, 0, 0), sim = queensSim(n); assert(rec == sim && sim == known[n - 1]); }          // ④ N-Queens: 재귀 == 시뮬레이션 == 알려진 값
        for (int n = 1; n <= 7; ++n) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); std::vector<std::vector<int>> rec, sim = permSim(n); permRec(a, 0, rec); assert(rec == sim); long fact = 1; for (int i = 2; i <= n; ++i) fact *= i; assert((long)sim.size() == fact); } }   // ⑤ 순열 생성 순서까지 같다
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
    { LockFreeStack s(5); int v = 0; for (int i = 0; i < 5; i++) { bool ok = s.push(i); assert(ok); } bool over = s.push(5); assert(!over && s.countData() == 5 && s.countFree() == 0); for (int i = 4; i >= 0; i--) { bool ok = s.pop(v); assert(ok && v == i); } bool under = s.pop(v); assert(!under && s.countFree() == 5); }       // ①
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
// audit: stress (보존 법칙이 오라클: 모든 값이 정확히 한 번 나오고, 폐기 노드 수 == 성공한 pop 수)
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
    { TreiberStack<std::string> s; std::string v; bool e0 = s.pop(v); assert(!e0); for (int i = 0; i < 100; i++) s.push("item" + std::to_string(i)); for (int i = 99; i >= 0; i--) { bool ok = s.pop(v); assert(ok && v == "item" + std::to_string(i)); } bool e1 = s.pop(v); assert(!e1 && s.retired() == 100); }          // ① ③
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
// 검증: ① 교환기 단위 시험: push 쪽과 pop 쪽 스레드가 같은 슬롯에서 값을 정확히 주고받음 ② 스택 수준의 결정적 랑데부(스레드·타이밍 없음): 시험용 스위치로 중앙 스택 CAS 를 실패한 것으로 만들고 슬롯마다 상대를 미리 세워 두면, push 는 기다리던 pop 에게 값을 전달하고(pop 이 먼저 온 역할) pop 은 기다리던 push 의 값을 가져가며(push 가 먼저 온 역할) 둘 다 중앙 스택을 건드리지 않고 제거 횟수가 정확히 오른다
//  ③ 경쟁 없는 단일 스레드 열 2 만 번을 std::vector 모형과 대조(LIFO 순서, 풀 크기 32 에서의 거절, 노드 수 보존, 제거는 0 번) ④ 6 스레드(push 3 · pop 3) 스트레스: 15 만 개의 값이 각각 정확히 한 번씩 꺼내졌는지 값별 표로 확인(중복·누락·범위 밖 0), 꺼낸 수 + 남은 수 == 넣은 수, 풀 무누수; 모든 대기에 횟수 상한이 있어 값이 사라지면 멈추지 않고 단언이 실패한다 ⑤ 스트레스의 제거 횟수는 참고 출력일 뿐 단언하지 않는다(코어 수·부하에 따라 0 일 수 있다) ⑥ TSan 통과
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
    static const int SLOTS = 4; uint32_t cap_;
    std::unique_ptr<std::atomic<uint32_t>[]> nextIdx; std::unique_ptr<std::atomic<uint32_t>[]> value; std::atomic<uint64_t> top{NIL}, freeTop{0}; Exchanger ex[SLOTS]; std::atomic<long> eliminated{0}; std::atomic<int> force{0};
    bool consumeForce() { int f = force.load(); while (f > 0) { if (force.compare_exchange_weak(f, f - 1)) return true; } return false; }                      // 시험용: 앞으로 f 번의 중앙 스택 CAS 를 실패한 것으로 친다
    static bool casPush(std::atomic<uint64_t>& head, std::atomic<uint32_t>* nx, uint32_t i) { uint64_t h = head.load(); nx[i].store((uint32_t)h); return head.compare_exchange_strong(h, (((h >> 32) + 1) << 32) | i); }          // CAS 한 번만 시도
    static uint32_t casPop(std::atomic<uint64_t>& head, std::atomic<uint32_t>* nx, bool& contended) { uint64_t h = head.load(); uint32_t i = (uint32_t)h; if (i == NIL) { contended = false; return NIL; } uint32_t n = nx[i].load(); if (head.compare_exchange_strong(h, (((h >> 32) + 1) << 32) | n)) { contended = false; return i; } contended = true; return NIL; }
    static void pushLoop(std::atomic<uint64_t>& head, std::atomic<uint32_t>* nx, uint32_t i) { while (!casPush(head, nx, i)) {} }
    uint32_t popLoop(std::atomic<uint64_t>& head) { bool c; for (;;) { uint32_t i = casPop(head, nextIdx.get(), c); if (!c) return i; } }
public:
    explicit EliminationStack(uint32_t cap) : cap_(cap), nextIdx(new std::atomic<uint32_t>[cap]), value(new std::atomic<uint32_t>[cap]) { for (uint32_t i = 0; i < cap; i++) { nextIdx[i] = i + 1 < cap ? i + 1 : NIL; value[i] = 0; } freeTop = cap ? 0 : NIL; }
    Exchanger& exchanger(int i) { return ex[i]; } static int slots() { return SLOTS; } void forceContention(int attempts) { force = attempts; }
    bool push(uint32_t v, std::mt19937& rng) {
        uint32_t n = popLoop(freeTop); if (n == NIL) return false; value[n].store(v);
        for (;;) { if (!consumeForce() && casPush(top, nextIdx.get(), n)) return true;                                                          // 중앙 스택: CAS 한 번
            if (ex[rng() % SLOTS].offerPush(v, 20)) { eliminated++; pushLoop(freeTop, nextIdx.get(), n); return true; } }          // 경쟁하면 제거 배열에서 상대를 찾는다 (성공하면 노드는 풀로)
    }
    bool pop(uint32_t& out, std::mt19937& rng) {
        for (;;) { bool contended = true; uint32_t i = NIL; if (!consumeForce()) i = casPop(top, nextIdx.get(), contended);
            if (!contended) { if (i == NIL) return false; out = value[i].load(); pushLoop(freeTop, nextIdx.get(), i); return true; }
            if (ex[rng() % SLOTS].offerPop(out, 20)) { eliminated++; return true; } }
    }
    long eliminatedPairs() const { return eliminated.load(); }
    long countFree() const { long c = 0; for (uint32_t i = (uint32_t)freeTop.load(); i != NIL && c <= (long)cap_; i = nextIdx[i].load()) c++; return c; }                // 사슬이 깨져 고리가 되어도 cap_+1 에서 멈춘다
    long countData() const { long c = 0; for (uint32_t i = (uint32_t)top.load(); i != NIL && c <= (long)cap_; i = nextIdx[i].load()) c++; return c; }
};
int main() {
    { Exchanger e; std::atomic<bool> got{false}; uint32_t received = 0; std::thread popper([&] { uint32_t v; for (long tries = 0; tries < 50000000 && !got; tries++) if (e.offerPop(v, 1000)) { received = v; got = true; } });
      for (long tries = 0; tries < 50000000 && !got; tries++) { if (e.offerPush(4242, 1000)) { while (!got) std::this_thread::yield(); } } popper.join(); assert(got && received == 4242 && st(e.slot.load()) == EMPTY); }       // ① 교환기: 값이 정확히 전달되고 슬롯이 EMPTY 로 복귀
    {   EliminationStack s(8); std::mt19937 rng(7); const int K = EliminationStack::slots();                                                                                                  // ② 결정적 랑데부 (스레드 없음)
        for (int k = 0; k < K; k++) s.exchanger(k).slot.store(pack(1, POP_WAIT, 0));                                                                                              // 역할 1: pop 이 먼저 와서 모든 슬롯에서 기다리는 중
        s.forceContention(8); bool pushed = s.push(555, rng); int delivered = 0; uint32_t sent = 0;
        for (int k = 0; k < K; k++) { uint64_t w = s.exchanger(k).slot.load(); if (st(w) == DELIVERED) { delivered++; sent = val(w); } else assert(st(w) == POP_WAIT); }
        assert(pushed && delivered == 1 && sent == 555 && s.eliminatedPairs() == 1 && s.countData() == 0 && s.countFree() == 8);                                                 // 값은 슬롯으로 갔고 중앙 스택·풀은 그대로
        for (int k = 0; k < K; k++) s.exchanger(k).slot.store(pack(9, PUSH_WAIT, 900 + k));                                                                                       // 역할 2: push 가 먼저 와서 모든 슬롯에서 기다리는 중
        s.forceContention(8); uint32_t out = 0; bool popped = s.pop(out, rng); int taken = 0, which = -1;
        for (int k = 0; k < K; k++) { uint64_t w = s.exchanger(k).slot.load(); if (st(w) == TAKEN) { taken++; which = k; } else assert(st(w) == PUSH_WAIT && val(w) == 900u + k); }
        assert(popped && taken == 1 && which >= 0 && out == 900u + which && s.eliminatedPairs() == 2 && s.countData() == 0 && s.countFree() == 8); }
    {   EliminationStack s(32); std::mt19937 rng(5), gen(9); std::vector<uint32_t> model;                                                                                              // ③ 경쟁 없는 단일 스레드: LIFO + 풀 크기
        for (int step = 0; step < 20000; step++) {
            if (gen() % 5 < 3) { uint32_t v = gen() % 100000; bool ok = s.push(v, rng); assert(ok == (model.size() < 32)); if (ok) model.push_back(v); }
            else { uint32_t v = 0; bool ok = s.pop(v, rng); assert(ok == !model.empty()); if (ok) { assert(v == model.back()); model.pop_back(); } }
            assert(s.countData() == (long)model.size() && s.countFree() == 32 - (long)model.size()); }
        assert(s.eliminatedPairs() == 0); }
    {   const int PUSHERS = 3, POPPERS = 3, OPS = 50000, CAP = 64; const long LIMIT = 5000000; EliminationStack s(CAP);                                                           // ④ 스트레스
        std::atomic<long> pushedCount{0}; std::atomic<bool> producersDone{false}, bail{false}; std::vector<std::vector<uint32_t>> got(POPPERS); std::vector<std::thread> ts;
        for (int t = 0; t < PUSHERS; t++) ts.emplace_back([&, t] { std::mt19937 rng(100 + t); for (int i = 1; i <= OPS && !bail; i++) { uint32_t v = (uint32_t)(t * OPS + i); long spins = 0;
            while (!s.push(v, rng)) { if (++spins > LIMIT) { bail = true; return; } std::this_thread::yield(); } pushedCount++; } });                                         // 풀이 비어 한없이 기다리지 않는다
        for (int t = 0; t < POPPERS; t++) ts.emplace_back([&, t] { std::mt19937 rng(200 + t); uint32_t v;
            for (;;) { bool done = producersDone; if (bail) break; if (s.pop(v, rng)) { got[t].push_back(v); if (got[t].size() > (size_t)PUSHERS * OPS) { bail = true; break; } } else if (done) break; else std::this_thread::yield(); } });                  // 생산이 끝난 뒤 비어 있으면 끝 (개수를 기다리지 않는다)
        for (int t = 0; t < PUSHERS; t++) ts[t].join(); producersDone = true; for (int t = PUSHERS; t < PUSHERS + POPPERS; t++) ts[t].join();
        std::mt19937 rng(1); std::vector<uint32_t> left; uint32_t v; while ((int)left.size() <= CAP && s.pop(v, rng)) left.push_back(v);                                           // 남은 것 (풀 크기를 넘으면 사슬이 망가진 것)
        std::vector<unsigned char> seen(PUSHERS * OPS + 1, 0); long total = 0, dup = 0, bad = 0, poppedCount = 0;
        auto mark = [&](uint32_t x) { if (x < 1 || x >= seen.size()) bad++; else if (seen[x]) dup++; else { seen[x] = 1; total++; } };
        for (auto& g : got) { poppedCount += (long)g.size(); for (uint32_t x : g) mark(x); } for (uint32_t x : left) mark(x);
        assert(!bail && pushedCount == PUSHERS * OPS);
        assert(dup == 0 && bad == 0 && total == pushedCount && poppedCount + (long)left.size() == pushedCount && (int)left.size() <= CAP && s.countFree() == CAP && s.countData() == 0);     // 값마다 정확히 한 번, 풀 무누수
        std::cout << "EliminationBackoffStack: a forced rendezvous eliminated one push and one pop in both roles without touching the central stack; " << pushedCount << " items exchanged by 3 pushers and 3 poppers were each delivered exactly once; pairs eliminated in the stress run (informational): " << s.eliminatedPairs() << std::endl; }
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
#include <random>
#include <thread>
#include <vector>
#include <cassert>

// 불변 스택(Immutable Stack): 객체의 모든 메서드가 const 이고 "변경" 은 새 객체를 돌려주는 값 의미의 스택이다. 영속 스택(PersistentStack)이 "이전 버전을 쓸 수 있다" 는 자료구조의 성질을 강조한다면, 불변 스택은 "객체가 만들어진 뒤 절대 바뀌지 않는다" 는 API 의 약속을 강조한다. 이 약속 덕분에 ① 여러 스레드가 잠금 없이 같은 스택을 읽을 수 있고(데이터 레이스 불가) ② 호출한 쪽이 인자가 몰래 바뀔 걱정을 하지 않으며 ③ 해시·동등 비교가 안정적이다.
// 구현 장치: 노드는 크기를 함께 저장해 size() 가 O(1) 이고, 동등 비교는 같은 노드를 가리키면(꼬리를 공유하면) 나머지를 볼 필요 없이 즉시 같다고 답해 공유 접미사를 O(1) 에 건너뛴다. 빈 스택은 하나의 공유 객체다.
// 검증: ① 모든 메서드가 const (const 객체로 호출 가능, 컴파일이 증명) ② 한 스택을 4 스레드가 동시에 읽으며 각자 자신의 파생 스택을 만들어도 원본이 그대로이고 결과가 맞음(TSan 으로 레이스 없음 확인) ③ size() 는 노드를 따라가지 않아도 정확 ④ 동등 비교: 내용이 같으면 참, 공유 접미사에서 비교한 노드 수가 접두사 길이로 한정 ⑤ 파생 스택들이 원본 접미사를 공유
//  ⑥ 무작위 버전 그래프: 임의의 옛 버전에서 push/pop 으로 새 버전을 계속 만든다(2 만 개, 크기는 200 이하로 유지). 모든 버전은 자기만의 std::vector 모형을 가지고, 나중에 7 개마다 내용·크기·top 이 모형과 같음 — 파생이 옛 버전을 바꾸지 않았다는 증거
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
    {   std::mt19937 rng(30); std::vector<ImmutableStack> versions = {ImmutableStack()}; std::vector<std::vector<int>> models = {{}};                                                  // ⑥ 무작위 버전 그래프
        for (int step = 0; step < 20000; ++step) { std::size_t from = rng() % versions.size(); std::vector<int> m = models[from]; ImmutableStack next;
            if (m.size() >= 200 || (!m.empty() && rng() % 3 == 0)) { next = versions[from].pop(); m.pop_back(); } else { int v = (int)(rng() % 1000); next = versions[from].push(v); m.push_back(v); }
            versions.push_back(next); models.push_back(m); }
        for (std::size_t i = 0; i < versions.size(); i += 7) { std::vector<int> got = versions[i].toVector(), want(models[i].rbegin(), models[i].rend()); assert(got == want && versions[i].size() == models[i].size() && versions[i].empty() == models[i].empty()); if (!models[i].empty()) assert(versions[i].top() == models[i].back()); } }
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
    { StackAllocator a(256); int count = 0; while (a.alloc(40, 8)) count++; void* none = a.alloc(40, 8); void* tiny = a.alloc(16, 1); assert(count == 6 && none == nullptr && tiny != nullptr); a.rewind(0); void* again = a.alloc(40, 8); assert(again != nullptr); }      // ② 소진 후 되감기로 다시 할당
    { StackAllocator a(1024); a.alloc(10, 1); StackAllocator::Marker m = a.mark(); void* p1 = a.alloc(100, 16); void* p2 = a.alloc(7, 1); bool back = a.rewind(m); assert(back); void* q1 = a.alloc(100, 16); void* q2 = a.alloc(7, 1); assert(p1 == q1 && p2 == q2);                  // ③ 되감으면 같은 주소 재현
      StackAllocator::Marker later = a.mark(); a.rewind(m); bool fwd = a.rewind(later); assert(!fwd && a.used() == m); }                                                                                                                            // ④ 앞으로 가는 되감기 거절
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
//  ⑥ 허용 사용량을 32·64·128 KB 로 바꿔 가며 도달 깊이가 두 배씩 늘어남(비례 관계 ±15%)을 확인
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
    {   long depths[3]; const std::size_t limits[3] = {32u * 1024, 64u * 1024, 128u * 1024};                                                                                          // ⑥ 허용 사용량을 바꿔 가며
        for (int k = 0; k < 3; ++k) { Probe q; q.allowed = limits[k]; q.frameBytes = 0; q.at3 = 0; pthread_attr_t at; pthread_attr_init(&at); pthread_attr_setstacksize(&at, 256 * 1024); pthread_t t2; int rc2 = pthread_create(&t2, &at, runProbe, &q); assert(rc2 == 0); pthread_join(t2, nullptr); pthread_attr_destroy(&at); assert(q.hitLimit); depths[k] = q.depthReached; }
        assert(depths[0] < depths[1] && depths[1] < depths[2] && depths[1] > depths[0] * 17 / 10 && depths[1] < depths[0] * 23 / 10 && depths[2] > depths[1] * 17 / 10 && depths[2] < depths[1] * 23 / 10); }    // 도달 깊이는 허용 사용량에 비례(두 배 → 약 두 배)
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
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
#include <cassert>

// 스택 되감기(Stack Unwinding): 예외가 던져지면 C++ 런타임은 호출 스택을 맨 위에서부터 한 프레임씩 풀어 가며 일치하는 catch 를 찾고, 풀리는 프레임마다 그 프레임의 지역 객체들을 "생성의 역순" 으로 소멸시킨다. 이것이 RAII(자원 획득 = 초기화)가 예외 안전의 토대인 이유다 — 잠금·파일·메모리를 객체 소멸자가 돌려주므로 중간에 예외로 빠져나가도 누수가 없다.
// 되감기 동안에는 소멸자에서 새 예외를 밖으로 던지면 안 된다(std::terminate). 소멸자 안에서 std::uncaught_exceptions() 로 "지금 되감기 중인가" 를 알 수 있다(스코프 가드가 커밋/롤백을 정할 때 쓴다). catch 에 닿지 못한 프레임은 풀리지 않을 수도 있어(구현 정의) 반드시 잡는 최상위 try 가 필요하다.
//  ⑥ 무작위 호출 계획 5 000 개(깊이 1~8, 프레임마다 추적자 0~3, 예외를 던질 프레임과 잡을 프레임을 무작위로): 실제 소멸 기록이 장부만으로 계산한 기대 기록(생성은 앞에서, 되감기 중 소멸 `~!` 은 던진 프레임에서 잡는 프레임 바로 아래까지 뒤에서부터, 잡은 뒤 정상 소멸 `~` 은 잡은 프레임부터 뒤에서부터)과 같다
// 이 항목은 소멸 순서를 기록하는 객체를 여러 프레임에 두고 가장 깊은 곳에서 예외를 던져 확인한다: ① 소멸 순서가 정확히 생성의 역순 ② 소멸자가 되감기 중임을 감지 ③ catch 한 프레임보다 위(호출한 쪽)의 객체는 소멸되지 않음 ④ 정상 반환과 예외 반환 모두 같은 소멸 규칙 ⑤ 스코프 가드가 예외 시 롤백
std::vector<std::string> events;
struct Tracer { std::string name; int unwindingAtCtor; explicit Tracer(std::string n) : name(std::move(n)), unwindingAtCtor(std::uncaught_exceptions()) { events.push_back("+" + name); }
    ~Tracer() { events.push_back(std::string(std::uncaught_exceptions() > unwindingAtCtor ? "~!" : "~") + name); } };           // ~! : 예외로 인한 되감기 중에 소멸
struct Rollback { bool& committed; std::vector<int>& data; std::size_t mark; Rollback(std::vector<int>& d, bool& c) : committed(c), data(d), mark(d.size()) {} ~Rollback() { if (!committed) data.resize(mark); } };      // 커밋되지 않으면 되돌린다
void level3(bool fail) { Tracer c("c"); if (fail) throw std::runtime_error("boom"); events.push_back("level3 ok"); }
void level2(bool fail) { Tracer b("b"); Tracer b2("b2"); level3(fail); events.push_back("level2 after call"); }
void level1(bool fail) { Tracer a("a"); try { level2(fail); events.push_back("level1 after call"); } catch (const std::exception& e) { events.push_back(std::string("caught ") + e.what()); } events.push_back("level1 end"); }
void appendAll(std::vector<int>& data, int n, int failAt) { bool committed = false; Rollback rb(data, committed); for (int i = 0; i < n; i++) { if (i == failAt) throw std::runtime_error("append failed"); data.push_back(i); } committed = true; }
struct Plan { std::vector<int> tracers; int throwFrame, catchFrame; };       // 프레임마다 추적자 개수, 예외를 던지는 프레임(-1 = 안 던짐), 잡는 프레임(-1 = 맨 바깥)
void runFrame(const Plan& p, int i, int j) {                                // 프레임 i 에서 추적자 j 번째부터 만든다
    if (j < p.tracers[i]) { Tracer t("f" + std::to_string(i) + "t" + std::to_string(j)); runFrame(p, i, j + 1); return; }
    if (i == p.throwFrame) throw std::runtime_error("planned");
    if (i + 1 < (int)p.tracers.size()) { if (i == p.catchFrame) { try { runFrame(p, i + 1, 0); } catch (const std::runtime_error&) { events.push_back("caught@" + std::to_string(i)); } } else runFrame(p, i + 1, 0); } }
std::vector<std::string> expectedEvents(const Plan& p) {                    // 독립 오라클: 생성은 앞에서부터, 되감기는 뒤에서부터, 장부만 가지고 계산
    std::vector<std::string> ev; int last = p.throwFrame >= 0 ? p.throwFrame : (int)p.tracers.size() - 1; auto name = [](int i, int j) { return "f" + std::to_string(i) + "t" + std::to_string(j); };
    for (int i = 0; i <= last; ++i) for (int j = 0; j < p.tracers[i]; ++j) ev.push_back("+" + name(i, j));
    if (p.throwFrame >= 0) { for (int i = p.throwFrame; i > p.catchFrame; --i) for (int j = p.tracers[i] - 1; j >= 0; --j) ev.push_back("~!" + name(i, j)); ev.push_back("caught@" + std::to_string(p.catchFrame)); for (int i = p.catchFrame; i >= 0; --i) for (int j = p.tracers[i] - 1; j >= 0; --j) ev.push_back("~" + name(i, j)); }
    else for (int i = last; i >= 0; --i) for (int j = p.tracers[i] - 1; j >= 0; --j) ev.push_back("~" + name(i, j));
    return ev; }
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
    {   std::mt19937 rng(8); long thrown = 0, quiet = 0;                                                                                                                            // ⑥ 무작위 호출 계획 5 000 개
        for (int trial = 0; trial < 5000; ++trial) { Plan p; int depth = 1 + (int)(rng() % 8); for (int i = 0; i < depth; ++i) p.tracers.push_back((int)(rng() % 4));
            p.throwFrame = rng() % 4 == 0 ? -1 : (int)(rng() % depth); p.catchFrame = p.throwFrame <= 0 ? -1 : (int)(rng() % (p.throwFrame + 1)) - 1;
            events.clear(); try { runFrame(p, 0, 0); } catch (const std::runtime_error&) { events.push_back("caught@-1"); }
            assert(events == expectedEvents(p)); p.throwFrame >= 0 ? ++thrown : ++quiet; }
        assert(thrown > 3000 && quiet > 500); }
    std::cout << "StackUnwinding: objects were destroyed in reverse order of construction while the exception propagated, destructors detected the unwinding, and a scope guard rolled back on failure" << std::endl; return 0;
}
// Time Complexity: 되감기 O(풀리는 프레임 수 + 소멸시킬 객체 수) — 예외가 던져질 때만 비용 발생
// Space Complexity: O(1) 추가
```
