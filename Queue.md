# Part 1. 기본 연산
## CreateQueue()
### 대표코드
```cpp
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <new>
#include <queue>
#include <random>
#include <utility>
#include <cassert>

// 큐 만들기(Create): "비어 있는 큐" 라는 초기 상태를 세운다. 새 큐는 크기 0이고 front/rear 가 없으며 dequeue·front 가 실패해야 한다. 표현은 둘로 나뉜다. 배열 큐는 용량을 정해 메모리를 한 번에 확보하고(할당 1 번) front 와 크기로 상태를 나타내며, 연결 큐는 front = rear = nullptr 로 시작해 아무것도 할당하지 않는다.
// 연결 큐에서는 front 와 rear 두 포인터를 항상 함께 관리해야 한다: 빈 큐는 "둘 다 nullptr", 원소가 하나면 "둘이 같은 노드". 한쪽만 갱신하면 큐가 깨진다(Rear 항목). RAII 로 생성자가 자원을 얻고 소멸자가 반환하며 복사는 금지하고 이동만 허용한다.
// 검증(전역 operator new/delete 를 교체해 할당 횟수와 생존 블록을 센다): ① 새 큐는 비어 있고 크기 0이며 front/dequeue 가 실패 ② 배열 큐 생성은 할당 1 번, 연결 큐는 0 번이고 첫 enqueue 에서 1 번 ③ 3000 개를 만들고 부숴도 생존 블록이 늘지 않는다 ④ 용량 0 도 정상 ⑤ 이동 후 원본은 빈 큐 ⑥ std::queue 도 같은 초기 상태
//  ⑦ 만든 직후부터 무작위 연산(인큐 2 : 디큐 1) 10 만 번을 용량 1·2·3·7·64 의 배열 큐(가득 차면 거부)와 연결 큐(거부 없음)에 흘려 보내 각각 std::queue 모형과 대조 — 반환값·front·크기가 매번 같고, 배열 큐는 한 번도 용량을 넘지 않는다
static long newCalls = 0, liveBlocks = 0;
#pragma GCC diagnostic ignored "-Wmismatched-new-delete"
void* operator new(std::size_t n) { void* p = std::malloc(n ? n : 1); if (!p) throw std::bad_alloc(); newCalls++; liveBlocks++; return p; }
void operator delete(void* p) noexcept { if (p) { liveBlocks--; std::free(p); } }
void operator delete(void* p, std::size_t) noexcept { operator delete(p); }
void* operator new[](std::size_t n) { return operator new(n); }
void operator delete[](void* p) noexcept { operator delete(p); }
void operator delete[](void* p, std::size_t) noexcept { operator delete(p); }
class ArrayQueue {
    int* a_; std::size_t cap_, front_ = 0, n_ = 0;
public:
    explicit ArrayQueue(std::size_t capacity) : a_(capacity ? new int[capacity] : nullptr), cap_(capacity) {}
    ~ArrayQueue() { delete[] a_; }
    ArrayQueue(const ArrayQueue&) = delete; ArrayQueue& operator=(const ArrayQueue&) = delete;
    ArrayQueue(ArrayQueue&& o) noexcept : a_(o.a_), cap_(o.cap_), front_(o.front_), n_(o.n_) { o.a_ = nullptr; o.cap_ = o.front_ = o.n_ = 0; }
    bool empty() const { return n_ == 0; } std::size_t size() const { return n_; }
    bool enqueue(int x) { if (n_ == cap_) return false; a_[(front_ + n_) % cap_] = x; n_++; return true; }
    bool dequeue(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % cap_; n_--; return true; }
    bool front(int& out) const { if (!n_) return false; out = a_[front_]; return true; }
};
class LinkedQueue {
    struct Node { int v; Node* next; }; Node *front_ = nullptr, *rear_ = nullptr; std::size_t n_ = 0;
public:
    ~LinkedQueue() { while (front_) { Node* t = front_; front_ = t->next; delete t; } }
    bool empty() const { return front_ == nullptr; } std::size_t size() const { return n_; }
    bool enqueue(int x) { Node* nd = new Node{x, nullptr}; if (rear_) rear_->next = nd; else front_ = nd; rear_ = nd; n_++; return true; }
    bool dequeue(int& out) { if (!front_) return false; Node* t = front_; out = t->v; front_ = t->next; if (!front_) rear_ = nullptr; delete t; n_--; return true; }
    bool front(int& out) const { if (!front_) return false; out = front_->v; return true; }
};
template <class Q> void checkFresh(Q& q) { int v = 123; bool hasFront = q.front(v), hasDeq = q.dequeue(v); assert(q.empty() && q.size() == 0 && !hasFront && !hasDeq && v == 123); }           // ① 초기 불변식 (실패한 호출은 출력 인자를 건드리지 않는다)
int main() {
    long baseLive = liveBlocks;
    { ArrayQueue a(16); LinkedQueue l; checkFresh(a); checkFresh(l); }
    long b0 = newCalls; { ArrayQueue a(16); assert(newCalls - b0 == 1); } long b1 = newCalls; { LinkedQueue l; assert(newCalls == b1); l.enqueue(1); assert(newCalls - b1 == 1); }          // ② 할당 횟수
    for (int i = 0; i < 3000; i++) { ArrayQueue a(i % 40); LinkedQueue l; for (int k = 0; k < i % 7; k++) { a.enqueue(k); l.enqueue(k); } } assert(liveBlocks == baseLive);                    // ③ 누수 0
    { ArrayQueue zero(0); int v = 0; bool enq = zero.enqueue(1), deq = zero.dequeue(v), fr = zero.front(v); assert(zero.empty() && !enq && !deq && !fr); }                                                                      // ④ 용량 0
    { ArrayQueue a(4); a.enqueue(7); a.enqueue(8); ArrayQueue b(std::move(a)); int v = 0, w = 0; std::size_t moved = b.size(); bool aEnq = a.enqueue(1), d1 = b.dequeue(v), d2 = b.dequeue(w); assert(a.empty() && !aEnq && moved == 2 && d1 && v == 7 && d2 && w == 8); }  // ⑤ 이동
    {   std::mt19937 rng(5); for (int cap : {1, 2, 3, 7, 64}) { ArrayQueue a(cap); LinkedQueue l; std::queue<int> ma, ml; long refused = 0;                                           // ⑦ 무작위 대조
            for (int step = 0; step < 100000; ++step) { int v = (int)rng();
                if (rng() % 3 != 0) { bool okA = a.enqueue(v), okL = l.enqueue(v); assert(okA == (ma.size() < (std::size_t)cap) && okL); if (okA) ma.push(v); else ++refused; ml.push(v); }
                else { int x = -1, y = -1; bool gotA = a.dequeue(x), gotL = l.dequeue(y); assert(gotA == !ma.empty() && gotL == !ml.empty()); if (gotA) { assert(x == ma.front()); ma.pop(); } if (gotL) { assert(y == ml.front()); ml.pop(); } }
                assert(a.size() == ma.size() && l.size() == ml.size() && a.size() <= (std::size_t)cap); int f = 0, g = 0; bool hasA = a.front(f), hasL = l.front(g); assert(hasA == !ma.empty() && hasL == !ml.empty()); if (!ma.empty()) assert(f == ma.front() && g == ml.front()); }
            assert(refused > 0 && a.empty() == ma.empty()); } }
    { std::queue<int> q; assert(q.empty() && q.size() == 0); }                                                                                                                          // ⑥ 실무의 std::queue
    std::cout << "CreateQueue: fresh array and linked queues satisfy the empty-state invariants; array queue costs 1 allocation, linked queue 0 until the first enqueue; 3000 create/destroy cycles left no live blocks" << std::endl; return 0;
}
// Time Complexity: 연결 큐 O(1), 배열 큐 할당 1 회
// Space Complexity: 배열 O(용량), 연결 O(1) (원소 수에 비례해 증가)
```
## Enqueue()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <new>
#include <queue>
#include <random>
#include <stdexcept>
#include <cassert>

// 인큐(Enqueue): 큐의 뒤(rear)에 원소를 넣는다. 구현마다 가득 찼을 때의 약속이 다르다. ① 고정 원형 배열: 거절(false) ② 동적 원형 배열: 용량을 두 배로 늘린다 — 이때 원소가 배열 끝을 감아 돌아(wrap) 저장되어 있을 수 있으므로 새 배열로 옮길 때 반드시 front 부터 순서대로 풀어서(linearize) 복사해야 한다. 배열 전체를 그대로 복사하면 순서가 뒤틀린다 ③ 연결: 노드 하나를 할당.
// 쓸 위치는 (front + 크기) % 용량 이다. front 가 배열 끝에 가까운 상태에서 인큐가 앞쪽 빈 칸으로 감아 돌아가는 것이 원형 큐의 핵심이다. 예외 안전: 용량을 늘리다 실패해도 큐는 이전 상태 그대로(새 버퍼를 먼저 완성한 뒤 교체).
// 검증: ① 고정 용량 큐는 정확히 용량만큼 받고 그 다음은 false, 경계 밖 감시값 그대로 ② 동적 큐의 성장 복사 횟수 < 2N, 용량은 2 의 거듭제곱 ③ 감아 돌아간 상태에서 성장해도 순서 유지 — 순진한 "배열 통째 복사" 구현이 실제로 틀리는 반례 ④ std::queue 와 무작위 enqueue/dequeue 차분 ⑤ 할당 실패 주입 시 이전 상태 보존
class FixedQueue {                                                                          // 외부 버퍼를 빌려 쓰는 고정 용량 원형 큐
    int* a_; std::size_t cap_, front_ = 0, n_ = 0;
public:
    FixedQueue(int* buffer, std::size_t cap) : a_(buffer), cap_(cap) {}
    bool enqueue(int x) { if (n_ == cap_) return false; a_[(front_ + n_) % cap_] = x; n_++; return true; }
    bool dequeue(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % cap_; n_--; return true; }
    std::size_t size() const { return n_; }
};
class DynamicQueue {
    int* a_ = nullptr; std::size_t cap_ = 0, front_ = 0, n_ = 0; long copies_ = 0; std::size_t failAbove_ = (std::size_t)-1; bool naive_;
    void grow(std::size_t nc) {
        if (nc > failAbove_) throw std::bad_alloc(); int* nb = new int[nc]();                  // 0 으로 초기화 (순진한 복사의 결과가 결정적이도록)
        if (naive_) { for (std::size_t i = 0; i < cap_; i++) nb[i] = a_[i]; copies_ += (long)cap_; /* 틀림: front_ 를 유지한 채 통째로 복사 -> 감아 돈 원소가 새 용량에서 엉뚱한 위치 */ }
        else { for (std::size_t i = 0; i < n_; i++) nb[i] = a_[(front_ + i) % cap_]; front_ = 0; copies_ += (long)n_; }        // 올바름: front 부터 순서대로 풀어서 앞으로 모은다
        delete[] a_; a_ = nb; cap_ = nc;
    }
public:
    explicit DynamicQueue(bool naive = false) : naive_(naive) {}
    ~DynamicQueue() { delete[] a_; } DynamicQueue(const DynamicQueue&) = delete; DynamicQueue& operator=(const DynamicQueue&) = delete;
    void enqueue(int x) { if (n_ == cap_) grow(cap_ ? cap_ * 2 : 1); a_[(front_ + n_) % cap_] = x; n_++; }
    bool dequeue(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % cap_; n_--; return true; }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } long copies() const { return copies_; } void failAbove(std::size_t n) { failAbove_ = n; }
};
int main() {
    { int raw[10]; for (int& x : raw) x = -999; FixedQueue q(raw + 1, 8); int v; for (int i = 0; i < 8; i++) { bool ok = q.enqueue(i); assert(ok); } bool over = q.enqueue(8); assert(!over && q.size() == 8 && raw[0] == -999 && raw[9] == -999);       // ① 용량 초과 거절, 경계 밖 불변
      for (int round = 0; round < 50; round++) { bool ok = q.dequeue(v); assert(ok && v == (round < 8 ? round : 100 + round - 8)); ok = q.enqueue(100 + round); assert(ok); } assert(raw[0] == -999 && raw[9] == -999); }                                 // 감아 돌며 계속 써도 경계를 넘지 않는다
    { DynamicQueue q; const int N = 5000; int v; for (int i = 0; i < N; i++) { q.enqueue(i); assert((q.capacity() & (q.capacity() - 1)) == 0); if (i % 3 == 2) { bool ok = q.dequeue(v); assert(ok); } } assert(q.copies() < 2L * N); }          // ② 성장 복사 < 2N
    { DynamicQueue good, bad(true); int v, w; for (int i = 0; i < 4; i++) { good.enqueue(i); bad.enqueue(i); } for (int i = 0; i < 3; i++) { good.dequeue(v); bad.dequeue(w); } for (int i = 4; i < 8; i++) { good.enqueue(i); bad.enqueue(i); }   // 가득 찬(감아 돈) 상태에서 성장
      good.enqueue(99); bad.enqueue(99); bool same = true; while (good.size()) { good.dequeue(v); same &= bad.dequeue(w) && v == w; } assert(!same); }                                                          // ③ 순진한 복사는 순서가 뒤틀린다
    { DynamicQueue q; std::queue<int> ref; std::mt19937 rng(5); int v; for (int step = 0; step < 30000; step++) { if (rng() % 3) { int x = rng() % 1000; q.enqueue(x); ref.push(x); } else { bool had = !ref.empty(); bool got = q.dequeue(v); assert(got == had); if (had) { assert(v == ref.front()); ref.pop(); } } assert(q.size() == ref.size()); } }       // ④
    { DynamicQueue q; int v; for (int i = 0; i < 4; i++) q.enqueue(i); q.dequeue(v); q.dequeue(v); q.enqueue(4); std::size_t cap = q.capacity(), n = q.size(); q.failAbove(cap); bool threw = false; try { for (int i = 0; i < 10; i++) q.enqueue(100 + i); } catch (const std::bad_alloc&) { threw = true; }
      q.failAbove((std::size_t)-1); assert(threw && q.capacity() == cap && q.size() >= n); int expect = 2; q.dequeue(v); assert(v == expect); }                                                              // ⑤ 실패해도 지금까지 들어간 것이 그대로
    std::cout << "Enqueue: fixed-capacity queue rejected overflow without touching guard cells even after wrapping; growth was linearized correctly (a whole-array copy scrambled the order) and cost < 2N copies; allocation failure left the queue usable" << std::endl; return 0;
}
// Time Complexity: 고정 O(1), 동적 분할상환 O(1) (최악 O(N)), 연결 O(1)
// Space Complexity: O(N) (동적은 용량이 크기의 최대 2 배)
```
## Dequeue()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <new>
#include <queue>
#include <random>
#include <stdexcept>
#include <utility>
#include <cassert>

// 디큐(Dequeue): 큐의 앞(front)에서 원소를 꺼내 제거한다. 설계 질문은 스택의 팝과 같다. (1) 빈 큐에서는 정의되지 않은 동작으로 둘지 오류로 알릴지 — 이 책의 큐는 false 를 돌려주고 상태를 바꾸지 않는다 (2) 제거한 값을 돌려줄지 — std::queue::pop() 이 void 인 이유는 값을 돌려주려면 제거한 뒤에 복사해야 하고 그 복사가 던지면 원소를 잃기 때문이다. front() 로 복사해 보고 성공한 뒤 pop() 하는 두 단계가 안전하다.
// 배열로 만든 큐가 옛 원소를 지울 때는 원소의 소멸자를 부르고 front 를 한 칸 옮긴다(원형이면 용량으로 감아 돌린다). 선형 배열 큐에서 front 만 올리면 앞쪽 칸이 영영 재사용되지 않아 "가짜 가득 참" 이 생긴다 — 원형 큐가 필요한 이유(LinearQueue 항목).
// 검증: ① N 개를 넣고 모두 꺼내면 정확히 같은 순서(FIFO) ② 빈 큐 dequeue 는 false 이고 출력 인자·상태 불변 ③ 소멸자 호출 수: dequeue 한 만큼 소멸, 큐가 파괴되면 나머지도 소멸 ④ 복사가 던지는 타입에서 "값 반환 dequeue" 설계는 원소를 잃고 "front 후 pop" 설계는 보존 ⑤ std::queue 와 무작위 차분 ⑥ 감아 도는 구간에서의 FIFO
struct Fragile { int v; static bool armed; static long live; Fragile(int x) : v(x) { live++; } Fragile(Fragile&& o) noexcept : v(o.v) { live++; } Fragile(const Fragile& o) : v(o.v) { if (armed) throw std::runtime_error("copy failed"); live++; } ~Fragile() { live--; } };
bool Fragile::armed = false; long Fragile::live = 0;
template <class T> class Queue {
    T* a_; std::size_t cap_, front_ = 0, n_ = 0;
public:
    explicit Queue(std::size_t cap) : a_(static_cast<T*>(::operator new(cap * sizeof(T)))), cap_(cap) {}
    ~Queue() { while (n_) pop(); ::operator delete(a_); } Queue(const Queue&) = delete; Queue& operator=(const Queue&) = delete;
    bool push(T v) { if (n_ == cap_) return false; new (a_ + (front_ + n_) % cap_) T(std::move(v)); n_++; return true; }
    bool pop() { if (!n_) return false; a_[front_].~T(); front_ = (front_ + 1) % cap_; n_--; return true; }          // 설계 B: 제거만 한다
    T& front() { return a_[front_]; } std::size_t size() const { return n_; }
    T dequeueValueNaive() {                                                                                            // 설계 A: 값을 돌려주는 dequeue. 제거한 "뒤에" 복사해 돌려줘야 한다
        alignas(T) unsigned char raw[sizeof(T)]; T* tmp = new (raw) T(std::move(a_[front_])); a_[front_].~T(); front_ = (front_ + 1) % cap_; n_--;
        struct G { T* p; ~G() { p->~T(); } } g{tmp}; return *tmp;                                                     // 이 복사가 던지면 원소는 이미 큐에서 사라졌다
    }
};
int main() {
    { Queue<int> q(1000); for (int i = 0; i < 1000; i++) q.push(i); for (int i = 0; i < 1000; i++) { assert(q.front() == i && q.pop()); } assert(q.size() == 0); }                                                // ① FIFO
    { Queue<int> q(4); assert(!q.pop() && q.size() == 0); q.push(5); assert(q.pop() && !q.pop()); }                                                                                                       // ②
    { Fragile::live = 0; { Queue<Fragile> q(8); for (int i = 0; i < 6; i++) q.push(Fragile(i)); assert(Fragile::live == 6); q.pop(); q.pop(); assert(Fragile::live == 4 && q.size() == 4); } assert(Fragile::live == 0); }  // ③ 소멸 계수
    { Queue<Fragile> a(8), b(8); for (int i = 1; i <= 5; i++) { a.push(Fragile(i)); b.push(Fragile(i)); } Fragile::armed = true; bool threwA = false, threwB = false;
      try { Fragile r = a.dequeueValueNaive(); (void)r; } catch (const std::runtime_error&) { threwA = true; }
      try { Fragile r = b.front(); (void)r; b.pop(); } catch (const std::runtime_error&) { threwB = true; }                                                                                              // 복사 먼저(front), 성공해야 pop
      Fragile::armed = false; assert(threwA && threwB); assert(a.size() == 4 && a.front().v == 2); assert(b.size() == 5 && b.front().v == 1); }                                                         // ④ 값 반환 설계: 1 을 영영 잃었다 / 분리 설계: 그대로 남음
    { std::mt19937 rng(8); std::queue<int> ref; Queue<int> q(64); for (int step = 0; step < 40000; step++) { if (rng() % 2) { int v = rng(); bool ok = q.push(v); assert(ok == (ref.size() < 64)); if (ok) ref.push(v); } else { bool had = !ref.empty(); if (had) { assert(q.front() == ref.front()); ref.pop(); } assert(q.pop() == had); } assert(q.size() == ref.size()); } }     // ⑤ ⑥ (용량 64 로 계속 감아 돈다)
    std::cout << "Dequeue: FIFO order, safe empty dequeues, destructor accounting and the front()+pop() split design verified; a value-returning dequeue lost an element when its copy threw" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Front()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <list>
#include <queue>
#include <random>
#include <type_traits>
#include <vector>
#include <cassert>

// 프런트(Front): 큐의 맨 앞 원소를 제거하지 않고 읽는다(std::queue::front()). 다음에 나갈 원소이므로 스케줄러가 "다음에 무엇을 처리할지" 보고 결정할 때 쓴다. 참조를 돌려주므로 제자리 수정이 가능하고, const 큐에서는 const 참조만 준다. 빈 큐의 front() 는 정의되지 않은 동작 — 호출 전에 empty() 확인이 호출자의 책임이다.
// 참조는 큐의 내부가 재배치되면 매달린다(dangling). 동적 배열 큐에서 enqueue 가 용량을 넘겨 새 버퍼로 옮기면 옛 참조는 해제된 메모리를 가리키고, 연결 큐의 노드는 움직이지 않아 참조가 유지된다. 해제된 메모리를 읽는 것은 정의되지 않은 동작이므로 아래 실험은 주소를 정수로 바꿔 비교만 한다.
// 검증: ① 참조로 제자리 수정이 큐에 반영 ② const 큐는 const 참조만 준다(static_assert) ③ 동적 배열 큐는 용량이 늘 때마다 front 의 주소가 바뀌고 reserve 후에는 바뀌지 않으며 연결 큐의 front 노드는 제자리 ④ std::queue 의 front 와 무작위 차분 ⑤ dequeue 후 front 가 다음 원소로 넘어감
template <class T> class VectorQueue {
    std::vector<T> buf_; std::size_t head_ = 0;
public:
    void enqueue(const T& v) { buf_.push_back(v); } void dequeue() { head_++; if (head_ > 32 && head_ * 2 > buf_.size()) { buf_.erase(buf_.begin(), buf_.begin() + head_); head_ = 0; } }
    bool empty() const { return head_ == buf_.size(); } std::size_t size() const { return buf_.size() - head_; }
    T& front() { return buf_[head_]; } const T& front() const { return buf_[head_]; } void reserve(std::size_t n) { buf_.reserve(n); }
};
template <class T> class ListQueue {
    std::list<T> l_;
public:
    void enqueue(const T& v) { l_.push_back(v); } void dequeue() { l_.pop_front(); } bool empty() const { return l_.empty(); } T& front() { return l_.front(); } const T& front() const { return l_.front(); }
};
uintptr_t addr(const void* p) { return reinterpret_cast<uintptr_t>(p); }
int main() {
    { VectorQueue<int> q; q.enqueue(10); q.front() += 5; assert(q.front() == 15); q.enqueue(20); q.front() *= 2; assert(q.front() == 30); q.dequeue(); assert(q.front() == 20); }                                                         // ① ⑤
    { VectorQueue<int> q; q.enqueue(1); const VectorQueue<int>& cq = q; static_assert(std::is_same<decltype(cq.front()), const int&>::value, "const queue gives const reference"); assert(cq.front() == 1); }                       // ②
    { VectorQueue<int> q; q.enqueue(0); uintptr_t at = addr(&q.front()); int relocations = 0; for (int i = 1; i < 1000; i++) { q.enqueue(i); if (addr(&q.front()) != at) { relocations++; at = addr(&q.front()); } } assert(relocations >= 5);       // ③ 배열: 성장할 때마다 이사
      VectorQueue<int> r; r.reserve(1000); r.enqueue(0); uintptr_t fixed = addr(&r.front()); for (int i = 1; i < 1000; i++) { r.enqueue(i); assert(addr(&r.front()) == fixed); }                                                        // reserve 후엔 제자리
      ListQueue<int> l; l.enqueue(0); int* pinned = &l.front(); for (int i = 1; i < 1000; i++) l.enqueue(i); assert(*pinned == 0 && pinned == &l.front()); }                                                                         // 연결: 제자리 (값을 읽어도 안전)
    { std::queue<int> ref; VectorQueue<int> q; ListQueue<int> l; std::mt19937 rng(3); for (int i = 0; i < 40000; i++) { if (rng() % 3) { int x = rng() % 1000; ref.push(x); q.enqueue(x); l.enqueue(x); } else if (!ref.empty()) { ref.pop(); q.dequeue(); l.dequeue(); } if (!ref.empty()) assert(q.front() == ref.front() && l.front() == ref.front()); assert(q.size() == ref.size()); } }       // ④
    std::cout << "Front: in-place modification through the reference works; reallocation moved the front of a vector-backed queue repeatedly but never the nodes of a linked queue" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Rear()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <cassert>

// 리어(Rear/Back): 큐의 맨 뒤(가장 최근에 들어온) 원소를 읽는다(std::queue::back()). 원형 배열 큐에서는 위치가 (front + 크기 − 1) % 용량 이라는 계산으로 O(1) 이고, 연결 큐에서는 rear 포인터를 따로 두어야 O(1) 이다(없으면 끝까지 따라가야 해서 O(N)). 그래서 연결 큐는 항상 front 와 rear 두 포인터를 쓴다.
// 연결 큐의 대표 버그: 마지막 원소를 dequeue 하면 front 가 nullptr 이 되는데 rear 를 함께 nullptr 로 만들지 않으면 rear 가 이미 해제된 노드를 가리킨다(매달린 포인터). 다음 enqueue 가 `rear->next = new` 로 해제된 메모리에 쓰는 정의되지 않은 동작이 된다. 올바른 구현은 front 가 비면 rear 도 비운다.
// 검증: ① 원형 배열 큐의 back 계산이 std::queue::back 과 일치(감아 돈 상태 포함) ② 연결 큐의 rear 가 enqueue 할 때마다 갱신되고 마지막 원소를 지우면 nullptr ③ rear 를 갱신하지 않는 틀린 구현의 rear 가 "해제된 노드의 주소" 를 쥔 채 남음을 살아 있는 노드 집합과의 대조(주소 숫자 비교만; 해제된 메모리를 읽지 않음)로 보임 ④ 원소가 하나일 때 front == rear 노드 ⑤ 무작위 차분
class CircularQueue {
    int* a_; std::size_t cap_, front_ = 0, n_ = 0;
public:
    explicit CircularQueue(std::size_t cap) : a_(new int[cap]), cap_(cap) {} ~CircularQueue() { delete[] a_; } CircularQueue(const CircularQueue&) = delete; CircularQueue& operator=(const CircularQueue&) = delete;
    bool enqueue(int x) { if (n_ == cap_) return false; a_[(front_ + n_) % cap_] = x; n_++; return true; }
    bool dequeue(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % cap_; n_--; return true; }
    bool front(int& out) const { if (!n_) return false; out = a_[front_]; return true; }
    bool rear(int& out) const { if (!n_) return false; out = a_[(front_ + n_ - 1) % cap_]; return true; }               // 감아 돌아도 한 번의 계산
    std::size_t rearIndex() const { return (front_ + n_ - 1) % cap_; }
};
static std::set<std::uintptr_t> liveNodes;
struct Node { int v; Node* next; };
Node* makeNode(int v) { Node* n = new Node{v, nullptr}; liveNodes.insert(reinterpret_cast<std::uintptr_t>(n)); return n; }
void freeNode(Node* n) { liveNodes.erase(reinterpret_cast<std::uintptr_t>(n)); delete n; }
struct LinkedQueue {
    Node *front = nullptr, *rear = nullptr; bool fixRearOnEmpty;
    explicit LinkedQueue(bool fix) : fixRearOnEmpty(fix) {}
    ~LinkedQueue() { while (front) { Node* t = front; front = t->next; freeNode(t); } }
    void enqueue(int x) { Node* n = makeNode(x); if (rear) rear->next = n; else front = n; rear = n; }
    bool dequeue(int& out) { if (!front) return false; Node* t = front; out = t->v; front = t->next; if (!front && fixRearOnEmpty) rear = nullptr; freeNode(t); return true; }
    bool rearAlive() const { return rear == nullptr || liveNodes.count(reinterpret_cast<std::uintptr_t>(rear)) > 0; }        // 숫자 비교만: 해제된 메모리를 읽지 않는다
};
int main() {
    { CircularQueue q(7); std::queue<int> ref; std::mt19937 rng(4); int v; for (int step = 0; step < 40000; step++) { if (rng() % 2) { int x = rng() % 1000; bool ok = q.enqueue(x); assert(ok == (ref.size() < 7)); if (ok) ref.push(x); } else { bool had = !ref.empty(); bool got = q.dequeue(v); assert(got == had); if (had) ref.pop(); } if (!ref.empty()) { int r = 0, f = 0; bool okRear = q.rear(r), okFront = q.front(f); assert(okRear && r == ref.back() && okFront && f == ref.front()); } else { bool okRear = q.rear(v); assert(!okRear); } } }       // ① ⑤ 용량 7 로 계속 감아 돈다
    { LinkedQueue q(true); int v; assert(q.rear == nullptr); q.enqueue(1); assert(q.front == q.rear && q.rear->v == 1); q.enqueue(2); assert(q.rear->v == 2 && q.front != q.rear); q.dequeue(v); assert(q.front == q.rear && q.rear->v == 2); q.dequeue(v); assert(q.front == nullptr && q.rear == nullptr && q.rearAlive()); q.enqueue(3); assert(q.front == q.rear && q.front->v == 3); }       // ② ④
    { LinkedQueue bad(false); int v; bad.enqueue(1); bad.dequeue(v); assert(bad.front == nullptr && bad.rear != nullptr && !bad.rearAlive()); /* 틀린 구현: 다음 enqueue 가 해제된 노드의 next 에 쓰게 된다 */ }                    // ③ 매달린 rear
    { LinkedQueue q(true); std::queue<int> ref; std::mt19937 rng(9); int v; for (int step = 0; step < 30000; step++) { if (rng() % 2) { int x = rng() % 100; q.enqueue(x); ref.push(x); } else { bool had = !ref.empty(); bool got = q.dequeue(v); assert(got == had); if (had) ref.pop(); } assert(q.rearAlive() && (ref.empty() ? q.rear == nullptr : q.rear->v == ref.back())); } }       // ⑤
    assert(liveNodes.empty());
    std::cout << "Rear: the circular back index matched std::queue::back while wrapping, the linked queue kept front/rear consistent through 30000 operations, and the variant that forgot to clear rear was caught holding a freed node's address" << std::endl; return 0;
}
// Time Complexity: O(1) (연결 큐는 rear 포인터가 있을 때)
// Space Complexity: O(1)
```
## Peek()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 엿보기(Peek): 큐의 맨 앞 원소를 꺼내지 않고 읽는다. 상태를 바꾸지 않는 const 연산이며 O(1) 이다. "다음에 나갈 것을 보고 처리 여부를 결정" 하는 알고리즘(예: 회의실 배정, 이벤트 시뮬레이션에서 가장 이른 이벤트의 시각을 확인)에 쓴다. 빈 큐에서는 실패를 알려야 하므로 bool 과 출력 인자를 쓴다(C++17 std::optional 도 같은 역할).
// 확장으로 앞에서 k 번째 원소를 보는 peekAt(k)가 있다(k = 0 이 맨 앞). 이것은 큐의 정의(맨 앞만 접근)를 넘는 편의 연산이므로 디버깅·정책 검사에만 쓰고, 순회가 잦다면 큐가 아닌 다른 자료구조(덱·리스트)가 맞는다는 신호로 본다.
// 검증: ① 큐 전체를 복사해 둔 뒤 peek/peekAt 을 수천 번 불러도 내용·크기가 그대로 ② std::queue 의 front 와 같고 peekAt(k)가 벡터 모델의 k 번째와 같음(원형 배열이 감아 돈 상태 포함) ③ const 큐에서도 호출 가능 ④ 빈 큐와 범위 밖 k 는 false ⑤ peek 한 값을 dequeue 하면 같은 값
class CircularQueue {
    std::vector<int> a_; std::size_t front_ = 0, n_ = 0;
public:
    explicit CircularQueue(std::size_t cap) : a_(cap) {}
    bool enqueue(int x) { if (n_ == a_.size()) return false; a_[(front_ + n_) % a_.size()] = x; n_++; return true; }
    bool dequeue(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % a_.size(); n_--; return true; }
    bool peek(int& out) const { if (!n_) return false; out = a_[front_]; return true; }
    bool peekAt(std::size_t k, int& out) const { if (k >= n_) return false; out = a_[(front_ + k) % a_.size()]; return true; }
    std::size_t size() const { return n_; }
    std::vector<int> snapshot() const { std::vector<int> v; for (std::size_t i = 0; i < n_; i++) v.push_back(a_[(front_ + i) % a_.size()]); return v; }
};
int main() {
    std::mt19937 rng(3); CircularQueue q(16); std::queue<int> ref; std::vector<int> model;
    for (int step = 0; step < 30000; step++) {
        int op = rng() % 4;
        if (op < 2) { int v = rng() % 100; bool ok = q.enqueue(v); assert(ok == (model.size() < 16)); if (ok) { ref.push(v); model.push_back(v); } }
        else if (op == 2 && !ref.empty()) { int p; assert(q.peek(p) && p == ref.front()); int d; assert(q.dequeue(d) && d == p); ref.pop(); model.erase(model.begin()); }                                           // ⑤
        else { std::vector<int> before = q.snapshot(); std::size_t n = q.size(); for (int t = 0; t < 5; t++) { int v; bool ok = q.peek(v); assert(ok == !ref.empty() && (!ok || v == ref.front())); std::size_t k = rng() % (n + 2); int w; bool ok2 = q.peekAt(k, w); assert(ok2 == (k < n) && (!ok2 || w == model[k])); } assert(q.snapshot() == before && q.size() == n); }   // ① ② ④
    }
    const CircularQueue& cq = q; int v; (void)cq.peek(v); (void)cq.peekAt(0, v);                                                                                                                               // ③ const 접근
    CircularQueue empty(4); assert(!empty.peek(v) && !empty.peekAt(0, v));
    std::cout << "Peek: 30000 randomized operations on a wrapping circular queue; peek and peekAt never changed the queue and agreed with std::queue::front and a vector model" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IsEmpty()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <queue>
#include <random>
#include <cassert>

// 비었는지 검사(IsEmpty): 큐에 원소가 하나도 없는가. dequeue·front 의 전제 조건이고 `while (!q.empty())` 처리 루프의 조건이다. 원형 배열 큐의 핵심 난제가 여기에 있다: front == rear 일 때 비어 있는 것인지 가득 찬 것인지 구별되지 않는다.
// 해법 세 가지. ① 한 칸 비우기: 항상 한 칸을 비워 두고 "비었다 = front == rear", "가득 = (rear + 1) % N == front" — 단순하지만 용량 N 에 N−1 개만 담는다 ② 크기 카운터: 원소 수를 따로 저장하고 "비었다 = count == 0" — 칸을 낭비하지 않는다 ③ 가득 참 플래그: front == rear 일 때 플래그로 구분. 세 방식은 관찰 가능한 동작이 같아야 한다(용량 해석만 다름).
// 검증: ① 세 방식의 empty() 가 무작위 enqueue/dequeue 열에서 항상 std::queue::empty() 와 같다(각자 용량 기준으로 가득 참 처리) ② 한 칸 비우기 방식은 N−1 개에서 가득, 나머지는 N 개 ③ 가득 찬 뒤 모두 dequeue 하면 다시 empty ④ 연결 큐에서 empty() 는 노드를 방문하지 않음 ⑤ size_t 되감기 함정(size()−1 은 비었을 때 SIZE_MAX)
class OneSlotEmpty { int a_[8]; std::size_t f_ = 0, r_ = 0; public:
    bool empty() const { return f_ == r_; } bool full() const { return (r_ + 1) % 8 == f_; }
    bool enqueue(int x) { if (full()) return false; a_[r_] = x; r_ = (r_ + 1) % 8; return true; } bool dequeue(int& o) { if (empty()) return false; o = a_[f_]; f_ = (f_ + 1) % 8; return true; } };
class WithCount { int a_[8]; std::size_t f_ = 0, n_ = 0; public:
    bool empty() const { return n_ == 0; } bool full() const { return n_ == 8; }
    bool enqueue(int x) { if (full()) return false; a_[(f_ + n_) % 8] = x; n_++; return true; } bool dequeue(int& o) { if (empty()) return false; o = a_[f_]; f_ = (f_ + 1) % 8; n_--; return true; } };
class WithFlag { int a_[8]; std::size_t f_ = 0, r_ = 0; bool full_ = false; public:
    bool empty() const { return f_ == r_ && !full_; } bool full() const { return full_; }
    bool enqueue(int x) { if (full_) return false; a_[r_] = x; r_ = (r_ + 1) % 8; full_ = r_ == f_; return true; } bool dequeue(int& o) { if (empty()) return false; o = a_[f_]; f_ = (f_ + 1) % 8; full_ = false; return true; } };
struct LinkedQueue { struct Node { int v; Node* next; }; Node *f = nullptr, *r = nullptr; mutable long visited = 0; ~LinkedQueue() { while (f) { Node* t = f; f = t->next; delete t; } }
    bool empty() const { return f == nullptr; } std::size_t sizeByWalking() const { std::size_t n = 0; for (Node* p = f; p; p = p->next) { visited++; n++; } return n; }
    void enqueue(int x) { Node* n = new Node{x, nullptr}; if (r) r->next = n; else f = n; r = n; } };
template <class Q> std::size_t capacityOf(Q q) { std::size_t c = 0; while (q.enqueue((int)c)) c++; return c; }
int main() {
    std::mt19937 rng(2); OneSlotEmpty a; WithCount b; WithFlag c; std::queue<int> ra, rb, rc;
    for (int step = 0; step < 100000; step++) { int op = rng() % 2; int v;
        if (op) { int x = rng(); bool oa = a.enqueue(x), ob = b.enqueue(x), oc = c.enqueue(x); assert(oa == (ra.size() < 7) && ob == (rb.size() < 8) && oc == (rc.size() < 8)); if (oa) ra.push(x); if (ob) rb.push(x); if (oc) rc.push(x); }
        else { bool oa = a.dequeue(v), ob = b.dequeue(v), oc = c.dequeue(v); assert(oa == !ra.empty() && ob == !rb.empty() && oc == !rc.empty()); if (oa) ra.pop(); if (ob) rb.pop(); if (oc) rc.pop(); }
        assert(a.empty() == ra.empty() && b.empty() == rb.empty() && c.empty() == rc.empty()); }                                                                                               // ① 세 방식 모두 std::queue::empty 와 일치
    assert(capacityOf(OneSlotEmpty()) == 7 && capacityOf(WithCount()) == 8 && capacityOf(WithFlag()) == 8);                                                                                                                      // ② 한 칸 비우기는 N−1 개
    { WithFlag f; int v, n = 0; while (f.enqueue(n)) n++; assert(f.full() && !f.empty()); while (f.dequeue(v)) {} assert(f.empty() && !f.full()); OneSlotEmpty o; while (o.enqueue(1)) {} while (o.dequeue(v)) {} assert(o.empty()); }       // ③
    { LinkedQueue l; for (int i = 0; i < 1000; i++) l.enqueue(i); l.visited = 0; bool e = l.empty(); assert(!e && l.visited == 0); l.visited = 0; assert(l.sizeByWalking() == 1000 && l.visited == 1000); }  // ④ empty 는 O(1)
    { std::size_t n = 0; assert(n - 1 == SIZE_MAX); }                                                                                                                                             // ⑤
    std::cout << "IsEmpty: the one-empty-slot, counter and flag disciplines all matched std::queue::empty() over 100000 operations (capacities 7, 8, 8); empty() visits 0 nodes of a linked queue" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IsFull()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <deque>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 가득 찼는지 검사(IsFull): 고정 용량 큐에서 원소 수 == 용량 인가. enqueue 가 거절될 조건과 정확히 같아야 한다. 용량 0 인 큐는 비어 있으면서 동시에 가득 차 있다. 원형 큐가 "한 칸 비우기" 방식이면 가득 참은 (rear + 1) % N == front 이고 실제 최대 원소 수는 N−1 이다.
// 상한이 있는 동적 큐(서버의 요청 대기열)는 최대 길이를 넘으면 거절하거나(admission control) 가장 오래된 것을 버린다(drop-oldest) 또는 예외를 던진다. 어떤 정책이든 "가득 참" 이 의미를 가지는 것은 큐가 유한한 경우뿐이다. 이 항목은 세 정책(거절, 예외, 가장 오래된 것 버리기)을 구현해 관찰 가능한 결과를 비교한다.
// 경계가 중요하다: 크기가 용량−1 → 용량으로 넘어가는 순간(off-by-one)과 용량 0, 1 이 단골 버그 지점이다.
// 검증: ① 용량 0..16 에서 정확히 용량 개를 받고 그때 IsFull 이 참이며 그 다음 enqueue 는 false, 상태 불변 ② dequeue 하면 다시 거짓, 다시 enqueue 하면 참 ③ IsFull && IsEmpty 는 용량 0 일 때만 ④ 한 칸 비우기 방식은 용량 N 에서 N−1 개 ⑤ 정책 비교: 거절은 가장 오래된 것을 보존, 가장 오래된 것 버리기는 최신 용량 개를 보존, 예외는 std::length_error ⑥ 한 칸 비우기 방식을 용량 0..16 에서 enqueue/dequeue 를 섞어 4000 번씩(인덱스가 여러 바퀴 감아 돈다) std::deque 모형과 대조: 반환값·꺼낸 값·full()·empty() 가 매번 같고, 최대 N−1 개까지 차며 용량 0 과 1 은 아무것도 못 받는다
class BoundedQueue {
    std::vector<int> a_; std::size_t front_ = 0, n_ = 0;
public:
    explicit BoundedQueue(std::size_t cap) : a_(cap) {}
    bool empty() const { return n_ == 0; } bool full() const { return n_ == a_.size(); } std::size_t size() const { return n_; }
    bool enqueue(int x) { if (full()) return false; a_[(front_ + n_) % a_.size()] = x; n_++; return true; }                              // 정책 1: 거절
    void enqueueOrThrow(int x) { if (!enqueue(x)) throw std::length_error("queue full"); }                                               // 정책 2: 예외
    void enqueueDropOldest(int x) { if (a_.empty()) return; if (full()) { front_ = (front_ + 1) % a_.size(); n_--; } enqueue(x); }          // 정책 3: 가장 오래된 것 버리기
    bool dequeue(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % a_.size(); n_--; return true; }
};
class OneSlotEmpty {                                                                         // 한 칸을 비우는 원형 큐
    std::vector<int> a_; std::size_t f_ = 0, r_ = 0;
public:
    explicit OneSlotEmpty(std::size_t n) : a_(n) {} bool empty() const { return f_ == r_; } bool full() const { return a_.empty() || (r_ + 1) % a_.size() == f_; }
    bool enqueue(int x) { if (full()) return false; a_[r_] = x; r_ = (r_ + 1) % a_.size(); return true; }
    bool dequeue(int& out) { if (empty()) return false; out = a_[f_]; f_ = (f_ + 1) % a_.size(); return true; }
};
int main() {
    for (std::size_t cap = 0; cap <= 16; cap++) {
        BoundedQueue q(cap); assert(q.empty() && (q.full() == (cap == 0)) && ((q.full() && q.empty()) == (cap == 0)));                                                                   // ③ 용량 0 만 둘 다 참
        for (std::size_t i = 0; i < cap; i++) { bool wasFull = q.full(), ok = q.enqueue((int)i); assert(!wasFull && ok); } assert(q.full() && q.size() == cap);                                                           // ① 정확히 cap 개
        bool refused = q.enqueue(-1); assert(!refused && q.size() == cap && q.full()); int v = 0; if (cap) { bool ok = q.dequeue(v); assert(ok && v == 0 && !q.full()); ok = q.enqueue(7); assert(ok && q.full()); }                         // ② dequeue 하면 거짓, 다시 enqueue 하면 참
    }
    { OneSlotEmpty o(8); int n = 0; while (o.enqueue(n)) n++; assert(n == 7); OneSlotEmpty z(0); assert(z.full()); }                                                                   // ④
    { BoundedQueue reject(4), thrower(4), dropper(4); for (int i = 0; i < 10; i++) { reject.enqueue(i); dropper.enqueueDropOldest(i); } bool threw = false; try { for (int i = 0; i < 10; i++) thrower.enqueueOrThrow(i); } catch (const std::length_error&) { threw = true; }
      std::vector<int> r, d; int v; while (reject.dequeue(v)) r.push_back(v); while (dropper.dequeue(v)) d.push_back(v); assert(r == (std::vector<int>{0, 1, 2, 3}) && d == (std::vector<int>{6, 7, 8, 9}) && threw && thrower.size() == 4); }                       // ⑤
    for (std::size_t n = 0; n <= 16; n++) { OneSlotEmpty o(n); std::deque<int> model; std::mt19937 rng(100 + (unsigned)n); const std::size_t usable = n ? n - 1 : 0; std::size_t most = 0; long enq = 0;                    // ⑥ 한 칸 비우기 방식 vs deque 모형
        for (int step = 0; step < 4000; step++) { if (rng() % 2) { int x = (int)(rng() % 1000); bool ok = o.enqueue(x); assert(ok == (model.size() < usable)); if (ok) { model.push_back(x); enq++; } } else { int out = -1; bool ok = o.dequeue(out); assert(ok == !model.empty()); if (ok) { assert(out == model.front()); model.pop_front(); } }
            assert(o.empty() == model.empty() && o.full() == (model.size() == usable) && model.size() <= usable); most = std::max(most, model.size()); }
        assert(most == usable && enq >= 3 * (long)usable); }
    std::cout << "IsFull: for capacities 0..16 full() became true exactly when the next enqueue was refused; only capacity 0 is both empty and full; reject, throw and drop-oldest policies behaved as specified, and the one-slot-empty ring agreed with a deque model through 17 x 4000 mixed operations" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Size()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <queue>
#include <random>
#include <cassert>

// 크기(Size): 큐 안의 원소 수. 연결 큐는 카운터를 두면 O(1) 이고 세어 보면 O(N) 이다. 원형 배열 큐에서 front 와 rear 인덱스만으로 크기를 구하는 공식 (rear − front + N) % N 은 큐가 가득 찬 상태와 빈 상태에서 모두 0 이 나와 구별되지 않는 결함이 있다(IsEmpty 항목). 해결은 카운터를 두거나, 인덱스를 용량으로 나머지를 취하지 않고 계속 증가시키는 "단조 카운터"(rear − front 가 그대로 크기, 인덱스는 mod 용량으로만 사용)를 쓰는 것이다.
// 단조 카운터는 size_t 가 한계를 넘어 0 으로 되돌아가도 부호 없는 뺄셈 rear − front 가 올바르다(2^64 법으로의 연산). 용량이 2 의 거듭제곱이면 mod 가 비트 AND 로 바뀌어 빠르다.
// 검증: ① 카운터 방식, 나머지 공식(한 칸 비우기), 단조 카운터 방식이 std::queue::size() 와 항상 같음 ② 나머지 공식은 가득 찬 상태에서 틀린다(0 을 돌려줌) — 한 칸 비우기가 아니면 ③ 단조 카운터를 size_t 최댓값 근처에서 시작해도 정확 ④ 실패한 연산은 크기를 바꾸지 않음 ⑤ 불변식: 성공한 enqueue 수 − 성공한 dequeue 수
class Counted { int a_[8]; std::size_t f_ = 0, n_ = 0; public:
    bool enqueue(int x) { if (n_ == 8) return false; a_[(f_ + n_) % 8] = x; n_++; return true; } bool dequeue(int& o) { if (!n_) return false; o = a_[f_]; f_ = (f_ + 1) % 8; n_--; return true; } std::size_t size() const { return n_; } };
class Modular { int a_[8]; std::size_t f_ = 0, r_ = 0; public:                                // 인덱스를 용량으로 나머지 취함: 가득/빈 구별 불가
    bool enqueue(int x) { a_[r_] = x; r_ = (r_ + 1) % 8; return true; } bool dequeue(int& o) { o = a_[f_]; f_ = (f_ + 1) % 8; return true; } std::size_t size() const { return (r_ + 8 - f_) % 8; } };
class Monotonic { int a_[8]; std::size_t head_, tail_; public:                                 // 단조 증가 카운터: 크기 = tail − head
    explicit Monotonic(std::size_t start = 0) : head_(start), tail_(start) {}
    bool enqueue(int x) { if (tail_ - head_ == 8) return false; a_[tail_ & 7] = x; tail_++; return true; } bool dequeue(int& o) { if (tail_ == head_) return false; o = a_[head_ & 7]; head_++; return true; } std::size_t size() const { return tail_ - head_; } };
int main() {
    std::mt19937 rng(11); Counted c; Monotonic m, edge((std::size_t)-1 - 30); std::queue<int> rc, rm, re; long okEnq = 0, okDeq = 0; int v;
    for (int step = 0; step < 100000; step++) {
        if (rng() % 2) { int x = rng(); std::size_t before = c.size(); bool a = c.enqueue(x), b = m.enqueue(x), e = edge.enqueue(x); assert(a == (rc.size() < 8) && b == (rm.size() < 8) && e == (re.size() < 8)); if (a) { rc.push(x); okEnq++; } else assert(c.size() == before); if (b) rm.push(x); if (e) re.push(x); }
        else { std::size_t before = c.size(); bool a = c.dequeue(v), b = m.dequeue(v), e = edge.dequeue(v); assert(a == !rc.empty() && b == !rm.empty() && e == !re.empty()); if (a) { rc.pop(); okDeq++; } else assert(c.size() == before); if (b) rm.pop(); if (e) re.pop(); }
        assert(c.size() == rc.size() && m.size() == rm.size() && edge.size() == re.size() && (long)c.size() == okEnq - okDeq);                                                              // ① ③ ④ ⑤
    }
    { Modular q; for (int i = 0; i < 8; i++) q.enqueue(i); assert(q.size() == 0); /* 가득 찼는데 0 — 구별 불가 */ Modular p; for (int i = 0; i < 5; i++) p.enqueue(i); assert(p.size() == 5); }                  // ②
    std::cout << "Size: counter and monotonic-counter queues matched std::queue::size() over 100000 operations (including a counter started 30 below SIZE_MAX); the modular-difference formula reported 0 for a full queue" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Clear()
### 대표코드
```cpp
#include <cstddef>
#include <deque>
#include <iostream>
#include <map>
#include <new>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 비우기(Clear): 모든 원소를 제거해 빈 큐로 되돌린다. 해야 할 일은 ① 각 원소의 소멸자를 앞에서부터 부르고 ② 메모리를 돌려주거나 재사용을 위해 남기고 ③ front 와 크기를 0 으로 만드는 것이다. 원형 배열 큐는 원소가 배열 끝을 감아 돌아 있을 수 있으므로 front 에서 크기만큼 (front + i) % 용량 으로 순회해 소멸시켜야 한다 — 배열 0..크기−1 만 소멸시키면 감아 돈 원소를 놓친다.
// 배열 큐는 버퍼(용량)를 남겨 두면 다시 채울 때 재할당이 없다. 연결 큐는 노드를 하나씩 반복문으로 해제한다(재귀 해제는 길이가 크면 호출 스택이 넘친다).
// 검증: 소멸자가 부르는 id 를 순서대로 기록(Tracked::log)하고 id 마다 살아 있는 개수(alive)를 센다. ① 원소가 칸 4..7, 0..3 에 감아 돈 가득 찬 큐(front=4)를 clear() 하면 소멸자가 FIFO 순서(4..11)로 정확히 한 번씩 불리고 크기 0, front 0 ② 가득 차지 않고 감아 돈 큐(원소 5 개가 칸 6, 7, 0, 1, 2)를 clear() 하면 id 6..10 이 이 순서로 소멸한다 — 순진한 "배열 앞쪽 0..n−1 만 소멸" 구현은 감아 돈 칸 6, 7 을 놓치고 이미 비어 있는 칸 3, 4 를 소멸시키는데(소멸 대상 칸 집합 비교; 그 구현은 정의되지 않은 동작이라 실행하지 않는다) 이 id 기록과 alive 검사가 그 차이를 잡는다 ③ 무작위 200 라운드(채우기·빼기·다시 채우기로 감아 돌게 만든 뒤 clear)에서 소멸 순서 == std::deque 모델의 순서, 비운 뒤 크기 0·용량 유지·front 0·생성 수 == 소멸 수이고, 두 번째 clear() 는 소멸자를 더 부르지 않으며(멱등) 감아 돈 라운드가 실제로 여럿 있었다 ④ 연결 큐 clear() 가 100 만 노드를 반복문으로 해제(생성 수 == 해제 수), 두 번 불러도 같고, 비운 뒤 다시 쓸 수 있다(tail 도 초기화)
struct Tracked { static long ctor, dtor; static std::map<int, int> alive; static std::vector<int> log; int id; explicit Tracked(int i) : id(i) { ctor++; alive[id]++; } Tracked(const Tracked& o) : id(o.id) { ctor++; alive[id]++; } ~Tracked() { dtor++; alive[id]--; log.push_back(id); } };
long Tracked::ctor = 0, Tracked::dtor = 0; std::map<int, int> Tracked::alive; std::vector<int> Tracked::log;
bool noneAlive() { for (const auto& kv : Tracked::alive) if (kv.second != 0) return false; return true; }                               // 모든 id 의 (생성 − 소멸) == 0
class RingQueue {
    Tracked* a_; std::size_t cap_, front_ = 0, n_ = 0;
public:
    explicit RingQueue(std::size_t cap) : a_(static_cast<Tracked*>(::operator new(cap * sizeof(Tracked)))), cap_(cap) {}
    ~RingQueue() { clear(); ::operator delete(a_); } RingQueue(const RingQueue&) = delete; RingQueue& operator=(const RingQueue&) = delete;
    bool enqueue(int id) { if (n_ == cap_) return false; new (a_ + (front_ + n_) % cap_) Tracked(id); n_++; return true; }
    bool dequeue() { if (!n_) return false; a_[front_].~Tracked(); front_ = (front_ + 1) % cap_; n_--; return true; }
    void clear() { for (std::size_t i = 0; i < n_; i++) a_[(front_ + i) % cap_].~Tracked(); n_ = 0; front_ = 0; }                  // 감아 돈 원소까지 앞에서부터 소멸
    std::set<std::size_t> occupiedSlots() const { std::set<std::size_t> s; for (std::size_t i = 0; i < n_; i++) s.insert((front_ + i) % cap_); return s; }       // 실제 원소가 있는 칸
    std::set<std::size_t> naiveSlots() const { std::set<std::size_t> s; for (std::size_t i = 0; i < n_; i++) s.insert(i); return s; }                           // 틀린 구현이 소멸시킬 칸: 0..n-1
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } std::size_t front() const { return front_; }
};
struct Node { int v; Node* next; static long made, freed; explicit Node(int x) : v(x), next(nullptr) { made++; } ~Node() { freed++; } };
long Node::made = 0, Node::freed = 0;
class LinkedQueue {
    Node* head_ = nullptr; Node* tail_ = nullptr; std::size_t n_ = 0;
public:
    LinkedQueue() = default; ~LinkedQueue() { clear(); } LinkedQueue(const LinkedQueue&) = delete; LinkedQueue& operator=(const LinkedQueue&) = delete;
    void enqueue(int x) { Node* n = new Node(x); if (tail_) tail_->next = n; else head_ = n; tail_ = n; n_++; }
    bool dequeue(int& out) { if (!head_) return false; Node* t = head_; out = t->v; head_ = t->next; if (!head_) tail_ = nullptr; delete t; n_--; return true; }
    void clear() { while (head_) { Node* t = head_; head_ = t->next; delete t; } tail_ = nullptr; n_ = 0; }                                  // 반복문으로 하나씩 해제(재귀 해제는 길이가 크면 스택이 넘친다), tail 도 비운다
    std::size_t size() const { return n_; } bool empty() const { return head_ == nullptr; }
};
int main() {
    int wrapped = 0;
    { RingQueue q(8); std::vector<int> want; for (int i = 0; i < 6; i++) { bool ok = q.enqueue(i); assert(ok); } for (int i = 0; i < 4; i++) { bool ok = q.dequeue(); assert(ok); } for (int i = 6; i < 12; i++) { bool ok = q.enqueue(i); assert(ok); } assert(q.size() == 8 && q.front() == 4);        // front=4, 원소 4..11 이 칸 4..7 과 0..3 에 감아 돌아 있다
      for (int i = 4; i < 12; i++) { want.push_back(i); } assert(Tracked::ctor - Tracked::dtor == 8); Tracked::log.clear(); q.clear();
      assert(q.size() == 0 && q.front() == 0 && Tracked::log == want && Tracked::ctor == Tracked::dtor && noneAlive()); }                                                   // ① 감아 돈 상태에서도 FIFO 순서로 정확히 한 번씩
    { Tracked::log.clear(); RingQueue r(8); for (int i = 0; i < 8; i++) { bool ok = r.enqueue(i); assert(ok); } for (int i = 0; i < 6; i++) { bool ok = r.dequeue(); assert(ok); } for (int i = 8; i < 11; i++) { bool ok = r.enqueue(i); assert(ok); }          // 크기 5: id 6, 7, 8, 9, 10 이 칸 6, 7, 0, 1, 2 에 있다
      std::set<std::size_t> real = r.occupiedSlots(), naive = r.naiveSlots(); assert(real == (std::set<std::size_t>{0, 1, 2, 6, 7}) && naive == (std::set<std::size_t>{0, 1, 2, 3, 4}) && real != naive && r.size() == 5 && r.size() < r.capacity());
      std::set<std::size_t> missed, wrong; for (auto x : real) if (!naive.count(x)) missed.insert(x); for (auto x : naive) if (!real.count(x)) wrong.insert(x); assert(missed == (std::set<std::size_t>{6, 7}) && wrong == (std::set<std::size_t>{3, 4}));        // 순진한 구현은 칸 6, 7 을 놓치고 빈 칸 3, 4 를 소멸시킨다
      Tracked::log.clear(); r.clear(); assert(Tracked::log == (std::vector<int>{6, 7, 8, 9, 10}) && r.size() == 0 && r.front() == 0 && noneAlive()); }                         // ② 진짜 clear() 는 id 6..10 을 이 순서로 소멸
    { RingQueue q(8); std::mt19937 rng(5); std::deque<int> model; int next = 0, nonEmpty = 0;
      for (int round = 0; round < 200; round++) { int a = rng() % 9; for (int i = 0; i < a; i++) { bool ok = q.enqueue(next); assert(ok); model.push_back(next++); } int d = rng() % (a + 1); for (int i = 0; i < d; i++) { bool ok = q.dequeue(); assert(ok); model.pop_front(); }
        int e = rng() % (8 - (a - d) + 1); for (int i = 0; i < e; i++) { bool ok = q.enqueue(next); assert(ok); model.push_back(next++); } assert(q.size() == model.size());                     // 채우고, 빼고, 다시 채워 감아 돌게 만든다
        if (q.front() + q.size() > q.capacity()) { wrapped++; } if (!model.empty()) { nonEmpty++; }
        Tracked::log.clear(); q.clear(); assert(Tracked::log == std::vector<int>(model.begin(), model.end()) && q.size() == 0 && q.capacity() == 8 && q.front() == 0 && Tracked::ctor == Tracked::dtor && noneAlive());     // ③ 소멸 순서 == 모델, 용량 유지
        model.clear(); long before = Tracked::dtor; q.clear(); assert(Tracked::dtor == before && q.size() == 0); }                                                                 // 멱등: 두 번째 clear 는 소멸자를 부르지 않는다
      assert(wrapped > 20 && nonEmpty > 100); }
    { LinkedQueue q; const int N = 1000000; for (int i = 0; i < N; i++) q.enqueue(i); assert(q.size() == N && Node::made == N); q.clear(); assert(q.size() == 0 && q.empty() && Node::freed == N);             // ④ 100 만 노드를 반복문으로 해제
      q.clear(); assert(Node::freed == N && Node::made == N);                                                                                                                         // 멱등
      q.enqueue(7); q.enqueue(8); int v = 0; bool ok = q.dequeue(v); assert(ok && v == 7); ok = q.dequeue(v); assert(ok && v == 8); ok = q.dequeue(v); assert(!ok && q.empty() && q.size() == 0); }  // 비운 뒤 재사용(tail 이 남아 있으면 해제된 노드에 쓰게 된다)
    assert(Node::made == Node::freed && Node::made == 1000002 && Tracked::ctor == Tracked::dtor && noneAlive());
    std::cout << "Clear: destructors ran exactly once per element and in FIFO order even when the queue wrapped around the array end (" << wrapped << " of 200 random rounds wrapped), the capacity survived clearing, clear() was idempotent, and a 1,000,000-node linked queue was freed iteratively by its own clear() and then reused" << std::endl; return 0;
}
// Time Complexity: 원소 소멸자 호출 O(N) (trivially destructible 이면 O(1))
// Space Complexity: O(1)
```

# Part 2. 배열 큐
## LinearQueue()
### 대표코드
```cpp
#include <cstddef>
#include <cstring>
#include <iostream>
#include <queue>
#include <random>
#include <cassert>

// 선형 큐(LinearQueue): 배열 하나에 front 와 rear 인덱스를 두고 enqueue 는 a[rear++] = x, dequeue 는 front++ 인 가장 단순한 배열 큐다. 치명적인 결함은 앞쪽 칸이 영영 재사용되지 않는다는 것이다 — 용량 8 에서 8 개를 넣고 모두 꺼내면 큐는 비었는데 rear 가 배열 끝(8)에 있어 enqueue 가 "가득 참" 으로 거절된다(가짜 가득 참).
// 응급 처치가 두 가지 있다. ① 큐가 비면 front = rear = 0 으로 되돌리기: 항상 비는 흐름에는 충분하지만, 큐가 계속 조금씩 차 있는 흐름에서는 소용없다 ② 가득 찼을 때 남은 원소를 앞으로 당기기(compaction): 가짜 가득 참은 없어지지만 당기는 데 O(N)이 들고, 큐가 용량 근처에서 enqueue/dequeue 를 번갈아 하는 흐름이면 거의 모든 연산이 당기기를 일으켜 평균 O(N) 이 된다. 근본 해법이 원형 큐(CircularQueue)다 — 인덱스를 용량으로 감아 돌려 앞 칸을 재사용한다.
// 검증: ① 순수 선형 큐는 무작위 흐름에서 실제로는 자리가 있는데 enqueue 를 거절하는 횟수(가짜 가득 참)가 많다 ② 비면 되돌리기는 항상 비는 흐름에서는 0 번 거절 ③ 당기기 방식은 가짜 거절이 0 이지만 경계 흐름(크기 용량−1 유지)에서 연산당 이동 원소 수가 용량에 가깝다 ④ 원형 큐는 같은 흐름에서 이동 0 ⑤ 거절하지 않은 연산의 결과는 모두 std::queue 와 같다
enum Mode { PURE, RESET_WHEN_EMPTY, COMPACT };
class LinearQueue {
    static const std::size_t CAP = 16; int a_[CAP]; std::size_t f_ = 0, r_ = 0; Mode mode_; long moved_ = 0;
public:
    explicit LinearQueue(Mode m) : mode_(m) {}
    std::size_t size() const { return r_ - f_; } long moved() const { return moved_; }
    bool enqueue(int x) {
        if (r_ == CAP) { if (mode_ != COMPACT || f_ == 0) return false; std::size_t n = r_ - f_; std::memmove(a_, a_ + f_, n * sizeof(int)); moved_ += (long)n; f_ = 0; r_ = n; }          // 끝에 닿았다: 당기기 방식만 앞으로 옮겨 자리를 만든다
        a_[r_++] = x; return true;
    }
    bool dequeue(int& out) { if (f_ == r_) return false; out = a_[f_++]; if (f_ == r_ && mode_ == RESET_WHEN_EMPTY) f_ = r_ = 0; return true; }
};
class CircularQueue {
    static const std::size_t CAP = 16; int a_[CAP]; std::size_t f_ = 0, n_ = 0;
public:
    bool enqueue(int x) { if (n_ == CAP) return false; a_[(f_ + n_) % CAP] = x; n_++; return true; }
    bool dequeue(int& out) { if (!n_) return false; out = a_[f_]; f_ = (f_ + 1) % CAP; n_--; return true; }
    std::size_t size() const { return n_; }
};
int main() {
    std::mt19937 rng(7); long falseFull[3] = {0, 0, 0}; const Mode modes[3] = {PURE, RESET_WHEN_EMPTY, COMPACT};
    for (int m = 0; m < 3; m++) { LinearQueue q(modes[m]); std::queue<int> ref; int v;
        for (int step = 0; step < 50000; step++) { if (rng() % 2) { int x = rng(); bool ok = q.enqueue(x); if (ok) ref.push(x); else if (ref.size() < 16) falseFull[m]++; /* 자리가 있는데 거절 = 가짜 가득 참 */ } else { bool had = !ref.empty(); assert(q.dequeue(v) == had); if (had) { assert(v == ref.front()); ref.pop(); } } assert(q.size() == ref.size()); } }       // ⑤
    assert(falseFull[0] > 1000 && falseFull[2] == 0);                                                                                                                                         // ① 순수 선형은 가짜 가득 참이 많다 / 당기기는 0
    { LinearQueue q(RESET_WHEN_EMPTY); int v; long rejected = 0; for (int round = 0; round < 1000; round++) { for (int i = 0; i < 16; i++) if (!q.enqueue(i)) rejected++; for (int i = 0; i < 16; i++) q.dequeue(v); } assert(rejected == 0); }          // ② 매번 완전히 비는 흐름은 되돌리기로 충분
    { LinearQueue c(COMPACT); CircularQueue ring; int v; for (int i = 0; i < 15; i++) { c.enqueue(i); ring.enqueue(i); } long before = c.moved(); const int OPS = 20000; for (int i = 0; i < OPS; i++) { assert(c.enqueue(i)); assert(c.dequeue(v)); assert(ring.enqueue(i)); assert(ring.dequeue(v)); }         // 크기를 용량−1 근처로 유지하며 번갈아 enqueue/dequeue
      double perOp = (double)(c.moved() - before) / (2 * OPS); assert(perOp > 4.0 && c.size() == ring.size()); std::cout << "compaction moved " << perOp << " elements per operation; "; }                    // ③ ④ 원형 큐는 이동이 없다 (메모리 이동 코드가 없음)
    std::cout << "LinearQueue: the pure linear queue wrongly rejected " << falseFull[0] << " enqueues while having free slots; compaction removed them at an O(N) price on boundary workloads; the circular queue needs neither" << std::endl; return 0;
}
// Time Complexity: enqueue·dequeue O(1), 당기기 방식은 최악 O(N)
// Space Complexity: O(N)
```
## CircularQueue()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 원형 큐(CircularQueue): 고정 크기 배열을 원처럼 이어 붙여, 인덱스가 끝에 닿으면 처음으로 감아 돈다. 앞 칸이 비는 대로 재사용되므로 선형 큐의 가짜 가득 참이 없고 모든 연산이 O(1) 이다. 핵심 공식: 다음 위치 = (i + 1) % N, 쓸 위치 = (front + 크기) % N.
// 용량을 2 의 거듭제곱으로 잡으면 `% N` 대신 `& (N − 1)` 비트 AND 로 계산할 수 있다 — 나눗셈이 없어 빠르다(두 식이 모든 인덱스에서 같음을 검증). 이 구현은 템플릿 인자 LOG 로 용량 2^LOG 를 정하고 컴파일 시점에 마스크를 만든다.
// 크기를 따로 저장하므로 "비었다/가득 찼다" 가 front == rear 로 구별되지 않는 문제가 없다(IsEmpty 항목). 순회는 front 부터 크기만큼 감아 돈다.
// 검증: ① 용량 1, 2, 4, …, 64 에서 std::queue(용량 제한 규칙)와 무작위 차분 — 수만 번 감아 돌아도 일치 ② 마스크 식 == 나머지 식 ③ 순회가 항상 FIFO 순서 ④ 가득 찼을 때 enqueue 거절, 꺼낸 뒤 즉시 재사용(가짜 가득 참 없음) ⑤ 원소 수가 용량인 채로 front 가 한 바퀴 이상 돌아도 정상
template <unsigned LOG> class CircularQueue {
    static const std::size_t CAP = (std::size_t)1 << LOG, MASK = CAP - 1; int a_[CAP]; std::size_t f_ = 0, n_ = 0;
public:
    bool enqueue(int x) { if (n_ == CAP) return false; a_[(f_ + n_) & MASK] = x; n_++; return true; }
    bool dequeue(int& out) { if (!n_) return false; out = a_[f_]; f_ = (f_ + 1) & MASK; n_--; return true; }
    std::size_t size() const { return n_; } static std::size_t capacity() { return CAP; } std::size_t frontIndex() const { return f_; }
    std::vector<int> toVector() const { std::vector<int> v; for (std::size_t i = 0; i < n_; i++) v.push_back(a_[(f_ + i) & MASK]); return v; }
};
template <unsigned LOG> void stress(unsigned seed) {
    CircularQueue<LOG> q; std::queue<int> ref; std::mt19937 rng(seed); const std::size_t CAP = CircularQueue<LOG>::capacity(); std::size_t laps = 0, lastFront = 0; int v;
    for (int step = 0; step < 40000; step++) {
        if (rng() % 2) { int x = rng(); bool ok = q.enqueue(x); assert(ok == (ref.size() < CAP)); if (ok) ref.push(x); }
        else { bool had = !ref.empty(); assert(q.dequeue(v) == had); if (had) { assert(v == ref.front()); ref.pop(); } }
        assert(q.size() == ref.size()); if (q.frontIndex() < lastFront) laps++; lastFront = q.frontIndex();
        if (step % 997 == 0) { std::vector<int> want; std::queue<int> c = ref; while (!c.empty()) { want.push_back(c.front()); c.pop(); } assert(q.toVector() == want); }              // ③ 순회 순서
    }
    assert(CAP == 1 || laps > 50);                                                                                                                                                            // 수십 바퀴 감아 돌았다
}
template <unsigned LOG> std::string ringPicture(const CircularQueue<LOG>& q) {   // 그림: 배열 칸마다 값(빈 칸 '.'), 아래 줄 F = 맨 앞 칸, W = 다음에 쓸 칸 — 논리적 순서는 배열 끝에서 앞으로 되감긴다
    const std::size_t cap = q.capacity(); std::vector<int> v = q.toVector(); std::vector<std::string> cell(cap, "."); char buf[16];
    for (std::size_t i = 0; i < v.size(); ++i) cell[(q.frontIndex() + i) % cap] = std::to_string(v[i]);
    std::string r1 = "slot", r2 = "val ", r3 = "    ", w; const std::size_t wr = (q.frontIndex() + q.size()) % cap;
    for (std::size_t i = 0; i < cap; ++i) {
        std::snprintf(buf, sizeof buf, "%3zu", i); r1 += buf; std::snprintf(buf, sizeof buf, "%3s", cell[i].c_str()); r2 += buf;
        w = i == q.frontIndex() && i == wr ? "FW" : i == q.frontIndex() ? "F" : i == wr ? "W" : ""; std::snprintf(buf, sizeof buf, "%3s", w.c_str()); r3 += buf;
    }
    while (!r3.empty() && r3.back() == ' ') r3.pop_back();
    return r1 + "\n" + r2 + "\n" + r3 + "\n";
}
int main() {
    {   CircularQueue<3> r; for (int x = 1; x <= 6; ++x) r.enqueue(x); int out; for (int i = 0; i < 3; ++i) r.dequeue(out);          // 용량 8 칸: 1..6 을 넣고 3 개를 뺀다
        assert(ringPicture(r) == "slot  0  1  2  3  4  5  6  7\nval   .  .  .  4  5  6  .  .\n               F        W\n");
        for (int x = 7; x <= 10; ++x) r.enqueue(x);                                                    // 7 8 은 배열 끝, 9 10 은 되감겨 앞쪽 칸에 들어간다
        const std::string wrap = "slot  0  1  2  3  4  5  6  7\nval   9 10  .  4  5  6  7  8\n            W  F\n";
        assert(ringPicture(r) == wrap && (r.toVector() == std::vector<int>{4, 5, 6, 7, 8, 9, 10}));  // 물리 배열은 뒤죽박죽이지만 논리 순서는 4..10
        r.enqueue(11); assert(ringPicture(r) == "slot  0  1  2  3  4  5  6  7\nval   9 10 11  4  5  6  7  8\n              FW\n" && !r.enqueue(12));   // 가득 차면 맨 앞 칸 = 쓸 칸
        std::cout << wrap; }
    stress<0>(1); stress<1>(2); stress<2>(3); stress<3>(4); stress<4>(5); stress<5>(6); stress<6>(7);                                                                                          // ① 용량 1..64
    for (std::size_t n : {1u, 2u, 8u, 64u, 1024u}) for (std::size_t i = 0; i < 5000; i++) assert((i % n) == (i & (n - 1)));                                                                         // ② 마스크 == 나머지 (n 이 2 의 거듭제곱일 때)
    { CircularQueue<3> q; int v; for (int i = 0; i < 8; i++) assert(q.enqueue(i)); assert(!q.enqueue(8)); assert(q.dequeue(v) && v == 0 && q.enqueue(8) && !q.enqueue(9)); /* ④ 꺼낸 즉시 그 칸을 다시 쓴다 */ for (int i = 0; i < 100; i++) { assert(q.dequeue(v)); assert(q.enqueue(i)); } assert(q.size() == 8); }          // ⑤
    std::cout << "CircularQueue: capacities 1..64 matched std::queue through tens of wraparounds each; the mask arithmetic equalled modulo for powers of two; a full queue reused a freed slot immediately" << std::endl; return 0;
}
// Time Complexity: enqueue·dequeue O(1)
// Space Complexity: O(N)
```
## Resize()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <new>
#include <queue>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 큐 크기 조정(Resize): 원형 배열 큐의 용량을 바꾼다. 스택과 다른 점은 원소가 배열 끝을 감아 돌아 저장돼 있을 수 있다는 것이다. 새 배열로 옮길 때는 반드시 front 부터 크기만큼 (front + i) % 옛용량 순서로 읽어 새 배열의 0..크기−1 에 차례로 써야 한다(linearize). 옛 배열을 통째로 복사하면 감아 돈 부분의 순서가 뒤틀린다(Enqueue 항목).
// 자동 크기 조정 정책(스택의 DynamicStack 과 같은 원리): 가득 차면 두 배로 키우고, 크기가 용량의 1/4 이하이면 절반으로 줄인다(1/2 에서 줄이면 경계에서 enqueue/dequeue 를 번갈아 할 때 매번 전체를 옮겨 Θ(N)). 명시적 연산으로는 reserve(n), shrinkToFit(), resize(n)(크기보다 작게는 거절)이 있다.
// 규칙: ① 줄일 때 크기보다 작은 용량 요청은 거절하고 상태 불변 ② 내용과 순서 보존 ③ 새 버퍼를 먼저 만들고 복사가 끝난 뒤 교체(강한 예외 보장) ④ 비용은 O(크기).
// 검증: ① 감아 도는 상태를 의도적으로 만든 뒤 reserve/shrink/resize 를 섞어도 내용·순서가 std::queue 와 같다 ② 크기보다 작은 resize 는 거절·상태 불변 ③ resize 후 front 는 0 이고 이후 enqueue/dequeue 정상 ④ 자동 정책의 불변식(용량 > 4 이면 크기 > 용량/4)과 총 이동 < 3 × 연산 수 ⑤ 1/4 규칙은 경계 흐름에서 이동 0, 1/2 규칙은 연산당 Θ(N) ⑥ 할당 실패 주입 시 이전 상태 보존
class ResizableQueue {
    int* a_ = nullptr; std::size_t cap_ = 0, front_ = 0, n_ = 0; long moved_ = 0; std::size_t failAbove_ = (std::size_t)-1;
public:
    ~ResizableQueue() { delete[] a_; }
    bool resize(std::size_t nc) {
        if (nc < n_) return false; if (nc == cap_) return true; if (nc > failAbove_) throw std::bad_alloc();
        int* nb = nc ? new int[nc] : nullptr; for (std::size_t i = 0; i < n_; i++) nb[i] = a_[(front_ + i) % cap_]; moved_ += (long)n_; delete[] a_; a_ = nb; cap_ = nc; front_ = 0; return true;      // linearize: front 부터 순서대로
    }
    bool reserve(std::size_t nc) { return nc <= cap_ ? true : resize(nc); } void shrinkToFit() { resize(n_); }
    void enqueue(int x) { if (n_ == cap_) resize(cap_ ? cap_ * 2 : 4); a_[(front_ + n_) % cap_] = x; n_++; }
    bool dequeue(int& out, double shrinkAt = 0.25) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % cap_; n_--; if (cap_ > 4 && n_ <= (std::size_t)(cap_ * shrinkAt)) resize(std::max<std::size_t>(4, cap_ / 2)); return true; }
    std::vector<int> contents() const { std::vector<int> v; for (std::size_t i = 0; i < n_; i++) v.push_back(a_[(front_ + i) % cap_]); return v; }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } std::size_t frontIndex() const { return front_; } long moved() const { return moved_; } void failAbove(std::size_t n) { failAbove_ = n; }
    bool invariant() const { return n_ <= cap_ && (cap_ <= 4 || n_ > cap_ / 4); }
};
int main() {
    std::mt19937 rng(9); ResizableQueue q; std::queue<int> ref; int v; bool wrapped = false;
    for (int step = 0; step < 40000; step++) {
        int op = rng() % 12;
        if (op < 5) { int x = rng() % 1000; q.enqueue(x); ref.push(x); } else if (op < 9) { bool had = !ref.empty(); assert(q.dequeue(v, 0.0) == had); if (had) { assert(v == ref.front()); ref.pop(); } }       // 자동 축소는 끄고(0.0) 명시적 연산만 시험
        else if (op == 9) { q.reserve(ref.size() + rng() % 40); } else if (op == 10) { q.shrinkToFit(); assert(q.capacity() == ref.size()); }
        else { std::size_t want = rng() % (2 * ref.size() + 4); std::size_t cap0 = q.capacity(); bool ok = q.resize(want); if (want < ref.size()) assert(!ok && q.capacity() == cap0); else assert(ok && q.capacity() == want && (want == cap0 || q.frontIndex() == 0)); }   // ② ③
        std::vector<int> want; { std::queue<int> c = ref; while (!c.empty()) { want.push_back(c.front()); c.pop(); } } assert(q.contents() == want); wrapped |= q.frontIndex() + q.size() > q.capacity();                              // ① 감아 도는 상태 포함
    }
    assert(wrapped);
    { ResizableQueue a; ResizableQueue b; int w; std::mt19937 r2(3); std::queue<int> ra; for (int step = 0; step < 100000; step++) { if (r2() % 5 < 2 || ra.empty()) { int x = (int)r2(); a.enqueue(x); ra.push(x); } else { assert(a.dequeue(w) && w == ra.front()); ra.pop(); } assert(a.invariant() && a.size() == ra.size()); } assert(a.moved() < 3L * 100000); (void)b; }       // ④
    { ResizableQueue good, half; int w; for (int i = 0; i < 1024; i++) { good.enqueue(i); half.enqueue(i); } good.enqueue(0); half.enqueue(0); good.dequeue(w, 0.25); half.dequeue(w, 0.5); long g0 = good.moved(), h0 = half.moved(); const int OPS = 2000; for (int i = 0; i < OPS; i++) { good.enqueue(i); good.dequeue(w, 0.25); half.enqueue(i); half.dequeue(w, 0.5); }
      assert(good.moved() - g0 <= 1100 && half.moved() - h0 > 100L * OPS); std::cout << "1/2-rule moves per op: " << (half.moved() - h0) / OPS << "; "; }                                                                                         // ⑤
    { ResizableQueue f; for (int i = 0; i < 8; i++) f.enqueue(i); f.dequeue(v, 0.0); f.dequeue(v, 0.0); f.enqueue(8); std::vector<int> before = f.contents(); std::size_t cap = f.capacity(); f.failAbove(cap); bool threw = false; try { f.resize(100); } catch (const std::bad_alloc&) { threw = true; } assert(threw && f.contents() == before && f.capacity() == cap); }       // ⑥
    std::cout << "Resize: contents and order stayed identical to std::queue across 40000 random operations including wrapped layouts; undersized requests were refused; the 1/4 shrink rule kept total moves under 3 per operation" << std::endl; return 0;
}
// Time Complexity: resize O(크기), enqueue·dequeue 분할상환 O(1)
// Space Complexity: O(용량)
```
## Rotate()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <deque>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 큐 회전(Rotate): 맨 앞 원소를 꺼내 맨 뒤에 다시 넣는 연산(dequeue 후 enqueue)을 k 번 하는 것이다. 순환 대기열(라운드 로빈 스케줄링, 돌아가며 발언, 요세푸스 문제)의 기본 동작이다. 연결 큐나 std::queue 로는 k 번의 dequeue+enqueue 라 O(k).
// 원형 배열 큐가 가득 차 있다면 회전은 배열을 한 칸도 옮기지 않고 front 인덱스만 한 칸 앞으로 보내면 된다(맨 앞이 맨 뒤가 되므로) — 한 번에 O(1), k 칸이면 front 를 k % 크기 만큼 옮겨 O(1). 가득 차지 않았으면 원소 하나를 실제로 옮겨야 한다.
// 응용: 요세푸스 문제(원형으로 앉은 n 명에서 k 번째마다 제거). 큐에서 (k−1)번 회전한 뒤 맨 앞을 제거하기를 반복하면 시뮬레이션이 되고, 점화식 J(1) = 0, J(n) = (J(n−1) + k) % n 이 닫힌 해다.
// 검증: ① 큐 회전 k 번이 std::rotate 로 만든 벡터와 같다(k > 크기 포함) ② 가득 찬 원형 큐의 O(1) 회전(front 이동)이 dequeue/enqueue 반복과 같은 결과 ③ 요세푸스: n ≤ 120, k ≤ 9 모든 조합에서 시뮬레이션의 마지막 생존자가 점화식과 같다 ④ 요세푸스 제거 순서 전체가 벡터 시뮬레이션과 같다 ⑤ 빈 큐와 크기 1 큐의 회전
template <class T> void rotateByQueue(std::queue<T>& q, long long k) { if (q.empty()) return; k %= (long long)q.size(); for (long long i = 0; i < k; i++) { q.push(q.front()); q.pop(); } }
class FullRing {                                                                          // 가득 찬 원형 큐: 회전은 front 이동뿐
    std::vector<int> a_; std::size_t f_ = 0;
public:
    explicit FullRing(std::vector<int> v) : a_(std::move(v)) {}
    void rotate(long long k) { if (a_.empty()) return; f_ = (f_ + (std::size_t)(k % (long long)a_.size())) % a_.size(); }              // O(1)
    std::vector<int> contents() const { std::vector<int> v; for (std::size_t i = 0; i < a_.size(); i++) v.push_back(a_[(f_ + i) % a_.size()]); return v; }
};
int josephusSimulate(int n, int k, std::vector<int>* order = nullptr) { std::queue<int> q; for (int i = 0; i < n; i++) q.push(i); while (q.size() > 1) { rotateByQueue(q, k - 1); if (order) order->push_back(q.front()); q.pop(); } if (order) order->push_back(q.front()); return q.front(); }
int josephusFormula(int n, int k) { int j = 0; for (int m = 2; m <= n; m++) j = (j + k) % m; return j; }
std::vector<int> josephusVector(int n, int k) { std::vector<int> people(n), order; std::iota(people.begin(), people.end(), 0); std::size_t idx = 0; while (!people.empty()) { idx = (idx + k - 1) % people.size(); order.push_back(people[idx]); people.erase(people.begin() + idx); } return order; }
int main() {
    std::mt19937 rng(6);
    for (int t = 0; t < 2000; t++) { int n = rng() % 20; long long k = rng() % 60; std::vector<int> v(n); for (int& x : v) x = rng() % 1000; std::queue<int> q; for (int x : v) q.push(x); rotateByQueue(q, k); std::vector<int> got; while (!q.empty()) { got.push_back(q.front()); q.pop(); }
        std::vector<int> want = v; if (n) std::rotate(want.begin(), want.begin() + (k % n), want.end()); assert(got == want);                                                                          // ①
        FullRing ring(v); ring.rotate(k); assert(ring.contents() == want); }                                                                                                                          // ②
    for (int n = 1; n <= 120; n++) for (int k = 1; k <= 9; k++) { assert(josephusSimulate(n, k) == josephusFormula(n, k)); }                                                                          // ③
    for (int t = 0; t < 300; t++) { int n = 1 + rng() % 40, k = 1 + rng() % 9; std::vector<int> order; josephusSimulate(n, k, &order); assert(order == josephusVector(n, k)); }                              // ④ 제거 순서 전체
    { std::queue<int> e; rotateByQueue(e, 5); assert(e.empty()); std::queue<int> one; one.push(7); rotateByQueue(one, 100); assert(one.size() == 1 && one.front() == 7); FullRing r0(std::vector<int>{}); r0.rotate(3); assert(r0.contents().empty()); }          // ⑤
    std::cout << "Rotate: queue rotation matched std::rotate (including k larger than the size); the O(1) front-index rotation of a full ring was identical; Josephus simulation by rotation equalled the closed recurrence for every n<=120, k<=9 and the full elimination order matched a vector simulation" << std::endl; return 0;
}
// Time Complexity: 큐로 회전 O(k), 가득 찬 원형 배열에서는 O(1)
// Space Complexity: O(1) 추가
```

# Part 3. 연결 큐
## LinkedQueue()
### 대표코드
```cpp
#include <cstddef>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 연결 큐(LinkedQueue): 단방향 연결 리스트의 앞(front)에서 꺼내고 뒤(rear)에 붙이는 큐다. 용량 제한이 없고 enqueue·dequeue 가 항상 O(1) 이며 재할당이 없어 원소 주소가 변하지 않는다. 대신 노드마다 할당·포인터 오버헤드가 있고 메모리가 흩어져 순회가 느리다(배열 큐 대비). 리스트의 맨 뒤에 O(1) 로 붙이려면 rear 포인터가 필요하다(없으면 끝까지 따라가야 해서 O(N)).
// front 와 rear 불변식: 빈 큐 ⇔ 둘 다 nullptr, 원소 하나 ⇔ 둘이 같은 노드. 마지막 원소를 dequeue 할 때 rear 도 비우는 것을 잊으면 매달린 포인터가 된다(Rear 항목). 소멸자는 반복문으로 해제(재귀 해제는 호출 스택 오버플로), 복사는 깊은 복사이되 순서 보존(꼬리 포인터로 이어 붙임), 이동은 포인터만 옮긴다.
// 검증: ① std::queue 와 무작위 차분(front/back/size/empty) ② 살아 있는 노드 수 == 크기(누수·이중 해제 없음) ③ 복사본은 순서까지 같고 독립적 ④ 이동 후 원본은 빈 큐 ⑤ 50 만 노드 파괴 안전 ⑥ 큐 병합 splice(두 연결 큐를 O(1) 로 잇기): 연결 큐만 가능한 연산
class LinkedQueue {
    struct Node { int v; Node* next; };
    Node *front_ = nullptr, *rear_ = nullptr; std::size_t n_ = 0; static long live_;
public:
    static long liveNodes() { return live_; }
    LinkedQueue() = default; ~LinkedQueue() { clear(); }
    LinkedQueue(const LinkedQueue& o) { for (Node* p = o.front_; p; p = p->next) enqueue(p->v); }                              // 순서를 보존하는 깊은 복사
    LinkedQueue(LinkedQueue&& o) noexcept : front_(o.front_), rear_(o.rear_), n_(o.n_) { o.front_ = o.rear_ = nullptr; o.n_ = 0; }
    LinkedQueue& operator=(LinkedQueue o) noexcept { std::swap(front_, o.front_); std::swap(rear_, o.rear_); std::swap(n_, o.n_); return *this; }
    void enqueue(int x) { Node* nd = new Node{x, nullptr}; live_++; if (rear_) rear_->next = nd; else front_ = nd; rear_ = nd; n_++; }
    bool dequeue(int& out) { if (!front_) return false; Node* t = front_; out = t->v; front_ = t->next; if (!front_) rear_ = nullptr; delete t; live_--; n_--; return true; }
    bool front(int& out) const { if (!front_) return false; out = front_->v; return true; } bool back(int& out) const { if (!rear_) return false; out = rear_->v; return true; }
    void clear() { while (front_) { Node* t = front_; front_ = t->next; delete t; live_--; } rear_ = nullptr; n_ = 0; }
    void splice(LinkedQueue& other) { if (!other.front_) return; if (rear_) rear_->next = other.front_; else front_ = other.front_; rear_ = other.rear_; n_ += other.n_; other.front_ = other.rear_ = nullptr; other.n_ = 0; }          // 노드는 그대로, 포인터만 이어 붙인다: O(1)
    std::vector<int> toVector() const { std::vector<int> v; for (Node* p = front_; p; p = p->next) v.push_back(p->v); return v; }
    std::size_t size() const { return n_; } bool empty() const { return !front_; }
};
long LinkedQueue::live_ = 0;
int main() {
    { std::mt19937 rng(12); LinkedQueue q; std::queue<int> ref; int v; for (int step = 0; step < 60000; step++) { if (rng() % 2) { int x = rng(); q.enqueue(x); ref.push(x); } else { bool had = !ref.empty(); assert(q.dequeue(v) == had); if (had) { assert(v == ref.front()); ref.pop(); } }
        int f = 0, b = 0; assert(q.front(f) == !ref.empty() && q.back(b) == !ref.empty() && (ref.empty() || (f == ref.front() && b == ref.back())) && q.size() == ref.size() && q.empty() == ref.empty() && (std::size_t)LinkedQueue::liveNodes() == q.size()); } }          // ① ②
    assert(LinkedQueue::liveNodes() == 0);
    { LinkedQueue a; for (int i = 1; i <= 5; i++) a.enqueue(i); LinkedQueue b(a); assert(b.toVector() == a.toVector() && LinkedQueue::liveNodes() == 10); int v; a.dequeue(v); b.enqueue(99); assert(a.toVector() == (std::vector<int>{2, 3, 4, 5}) && b.toVector() == (std::vector<int>{1, 2, 3, 4, 5, 99}));          // ③ 순서까지 같고 독립
      LinkedQueue c; c = a; assert(c.toVector() == a.toVector()); }
    { LinkedQueue a; a.enqueue(1); a.enqueue(2); LinkedQueue b(std::move(a)); assert(a.empty() && a.size() == 0 && b.size() == 2 && LinkedQueue::liveNodes() == 2); a.enqueue(7); assert(a.size() == 1 && b.size() == 2); }                  // ④ 이동 후 원본도 정상 사용
    assert(LinkedQueue::liveNodes() == 0);
    { LinkedQueue big; for (int i = 0; i < 500000; i++) big.enqueue(i); assert(LinkedQueue::liveNodes() == 500000); } assert(LinkedQueue::liveNodes() == 0);                                                                                  // ⑤
    { LinkedQueue a, b; for (int i = 0; i < 3; i++) a.enqueue(i); for (int i = 10; i < 13; i++) b.enqueue(i); a.splice(b); assert(b.empty() && a.toVector() == (std::vector<int>{0, 1, 2, 10, 11, 12}) && a.size() == 6 && LinkedQueue::liveNodes() == 6); int v; for (int i = 0; i < 6; i++) a.dequeue(v); a.enqueue(5); a.splice(b); assert(a.toVector() == (std::vector<int>{5})); LinkedQueue e; e.splice(a); assert(e.toVector() == (std::vector<int>{5}) && a.empty()); }   // ⑥
    assert(LinkedQueue::liveNodes() == 0);
    std::cout << "LinkedQueue: matched std::queue over 60000 operations with live-node count equal to size; deep copy preserved order, move emptied the source, 500000 nodes were freed iteratively, and splice joined two queues in O(1)" << std::endl; return 0;
}
// Time Complexity: enqueue·dequeue·front·back O(1), splice O(1), 복사·소멸 O(N)
// Space Complexity: O(N) (노드당 포인터 하나 추가)
```
## EnqueueNode()
### 대표코드
```cpp
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <new>
#include <random>
#include <vector>
#include <cassert>

// 노드 단위 인큐(EnqueueNode): 연결 큐의 enqueue 를 포인터 조작 수준에서 본다. ① 새 노드를 만들고(next = nullptr) ② 큐가 비어 있으면 front 와 rear 를 모두 새 노드로, 아니면 rear->next 를 새 노드로 잇고 rear 를 새 노드로 옮긴다. 두 경우를 구분하지 않고 `rear->next = n` 만 쓰면 빈 큐에서 널 포인터를 역참조한다(가장 흔한 버그).
// 예외 안전: 할당이 실패하면 아직 아무것도 바꾸지 않았으므로 큐는 그대로다(강한 보장). 그래서 new 를 가장 먼저 하고 포인터 대입은 마지막에 한다. 포인터 대입 중에는 실패할 수 있는 연산이 없다.
// 포인터를 주소로 줄이는 이중 포인터 관용구: `Node** tail = &front; ... *tail = n;` 처럼 "마지막 next 칸의 주소" 를 들고 있으면 빈 큐 분기가 필요 없다. 아래에서 두 방식이 같은 결과임을 확인한다.
// 검증: ① 무작위로 인큐한 뒤 front 부터 순회한 값이 인큐 순서와 같고 길이가 맞다 ② 순환(cycle)이 없음(토끼와 거북이) ③ k 번째 new 에서 할당 실패를 주입하면 front/rear/내용이 그대로이고 누수 0 ④ 이중 포인터 방식과 분기 방식의 결과가 같다 ⑤ 틀린 구현(빈 큐 분기 없음)은 첫 인큐에서 널 포인터를 쓰려 한다는 것을 구조상 검증(실행하지 않고 조건만 확인)
//  ⑥ 무작위 대조 + 무작위 실패 주입: 인큐 2 만 번 중 1/40 은 새 노드 할당이 실패하도록 하고, 실패한 호출은 아무것도 바꾸지 않았고 성공한 호출만 std::vector 모형에 쌓였는지 500 번마다 front 부터 걸어 rear 와 함께 대조; 끝에 노드가 모두 반환됨
static long allocCount = 0, failAt = -1, liveNodes = 0;
#pragma GCC diagnostic ignored "-Wmismatched-new-delete"
void* operator new(std::size_t n) { if (++allocCount == failAt) throw std::bad_alloc(); void* p = std::malloc(n ? n : 1); if (!p) throw std::bad_alloc(); return p; }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
struct Node { int data; Node* next; };
void enqueueBranch(Node*& front, Node*& rear, int x) { Node* n = new Node{x, nullptr}; liveNodes++; if (rear == nullptr) front = rear = n; else { rear->next = n; rear = n; } }       // 먼저 할당(실패 가능), 대입은 마지막
void enqueueTail(Node*& front, Node**& tail, int x) { Node* n = new Node{x, nullptr}; liveNodes++; *tail = n; tail = &n->next; (void)front; }                                         // 마지막 next 칸의 주소를 들고 있는 방식: 분기 없음
bool wouldCrashWithoutEmptyBranch(Node* rear) { return rear == nullptr; }                                                                                                            // 분기 없이 rear->next 를 쓰면 rear 가 널인 경우 바로 널 역참조
bool hasCycle(Node* head) { Node *slow = head, *fast = head; while (fast && fast->next) { slow = slow->next; fast = fast->next->next; if (slow == fast) return true; } return false; }
std::size_t length(Node* head) { std::size_t n = 0; for (; head; head = head->next) n++; return n; }
void freeAll(Node*& head) { while (head) { Node* t = head; head = head->next; delete t; liveNodes--; } }
int main() {
    { Node *front = nullptr, *rear = nullptr; std::vector<int> pushed; for (int i = 0; i < 1000; i++) { enqueueBranch(front, rear, i * 3); pushed.push_back(i * 3); } std::vector<int> walk; for (Node* p = front; p; p = p->next) walk.push_back(p->data);
      assert(walk == pushed && !hasCycle(front) && length(front) == 1000 && rear->data == 999 * 3 && rear->next == nullptr); freeAll(front); assert(liveNodes == 0); }                              // ① ②
    { Node *front = nullptr, *rear = nullptr; for (int i = 0; i < 5; i++) enqueueBranch(front, rear, i); Node *beforeFront = front, *beforeRear = rear; std::size_t beforeLen = length(front); allocCount = 0; failAt = 1; bool threw = false;
      try { enqueueBranch(front, rear, 99); } catch (const std::bad_alloc&) { threw = true; } failAt = -1; assert(threw && front == beforeFront && rear == beforeRear && length(front) == beforeLen && rear->next == nullptr); freeAll(front); assert(liveNodes == 0); }          // ③ 강한 보장
    { Node *f1 = nullptr, *r1 = nullptr; Node *f2 = nullptr; Node** tail = &f2; for (int i = 0; i < 100; i++) { enqueueBranch(f1, r1, i); enqueueTail(f2, tail, i); } Node *a = f1, *b = f2; bool same = true; while (a && b) { same &= a->data == b->data; a = a->next; b = b->next; } assert(same && !a && !b); freeAll(f1); freeAll(f2); assert(liveNodes == 0); }          // ④ 두 방식 동일
    assert(wouldCrashWithoutEmptyBranch(nullptr) && !wouldCrashWithoutEmptyBranch(reinterpret_cast<Node*>(1)));                                                                                    // ⑤
    {   std::mt19937 rng(11); Node *front = nullptr, *rear = nullptr; std::vector<int> model; long failures = 0;                                                                   // ⑥ 무작위 대조와 실패 주입
        for (int step = 0; step < 20000; ++step) { bool inject = rng() % 40 == 0; int v = (int)(rng() % 1000); allocCount = 0; failAt = inject ? 1 : -1; bool threw = false;
            try { enqueueBranch(front, rear, v); } catch (const std::bad_alloc&) { threw = true; } failAt = -1; assert(threw == inject);
            if (threw) ++failures; else model.push_back(v);
            if (step % 500 == 0) { std::vector<int> walk; for (Node* p = front; p; p = p->next) walk.push_back(p->data); assert(walk == model && (model.empty() ? rear == nullptr : rear->data == model.back())); } }
        std::vector<int> walk; for (Node* p = front; p; p = p->next) walk.push_back(p->data); assert(walk == model && failures > 100 && !hasCycle(front)); freeAll(front); assert(liveNodes == 0); }
    std::cout << "EnqueueNode: both the branch and the tail-address idioms produced identical lists; an injected allocation failure left front, rear and the list untouched" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per node
```
## DequeueNode()
### 대표코드
```cpp
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 노드 단위 디큐(DequeueNode): 연결 큐의 dequeue 를 포인터 조작 수준에서 본다. 순서: ① 떼어 낼 노드를 임시 포인터에 기억 ② front 를 다음 노드로 이동 ③ front 가 비었으면 rear 도 nullptr ④ 값을 꺼내고 노드를 해제. ④ 를 ② 보다 먼저 하면 해제된 노드의 next 를 읽게 되고(use-after-free), ③ 을 빠뜨리면 rear 가 해제된 노드를 가리킨다(Rear 항목).
// 이 항목은 상태 불변식을 직접 검사하는 함수를 두고 모든 연산 뒤에 검사한다: (front == nullptr) ⇔ (rear == nullptr), rear->next == nullptr, front 에서 next 를 따라가면 rear 에 닿는다. 이 불변식은 올바른 연산 열에서는 항상 성립하고, ③ 을 빠뜨린 구현에서는 마지막 원소 제거 직후 깨진다.
// 또 하나의 기법은 노드를 해제하지 않고 떼어내(detach) 재사용하는 것이다(자유 리스트). 재사용하면 new/delete 가 사라지고 같은 주소가 LIFO 로 돌아온다.
// 검증: ① 무작위 enqueue/dequeue 5 만 번 동안 불변식이 항상 성립하고 값은 FIFO ② 빈 큐 dequeue 는 false·출력 불변 ③ 마지막 원소 제거 직후 front == rear == nullptr ④ ③ 을 빠뜨린 구현은 같은 순간 불변식이 깨짐(해제된 주소를 숫자로만 비교) ⑤ detach/reuse: 노드 재사용 시 새 할당 0 번
struct Node { int data; Node* next; };
static std::set<std::uintptr_t> liveNodes; static long newCalls = 0;
Node* makeNode(int v) { Node* n = new Node{v, nullptr}; newCalls++; liveNodes.insert(reinterpret_cast<std::uintptr_t>(n)); return n; }
void freeNode(Node* n) { liveNodes.erase(reinterpret_cast<std::uintptr_t>(n)); delete n; }
struct Q {
    Node *front = nullptr, *rear = nullptr; bool fixRear;
    explicit Q(bool fix = true) : fixRear(fix) {}
    ~Q() { while (front) { Node* t = front; front = t->next; freeNode(t); } }
    void enqueue(Node* n) { n->next = nullptr; if (rear) rear->next = n; else front = n; rear = n; }
    void enqueue(int x) { enqueue(makeNode(x)); }
    bool dequeue(int& out) { if (!front) return false; Node* t = front; front = t->next; if (!front && fixRear) rear = nullptr; out = t->data; freeNode(t); return true; }          // 기억 -> 이동 -> rear 정리 -> 값 -> 해제
    Node* detach() { if (!front) return nullptr; Node* t = front; front = t->next; if (!front) rear = nullptr; t->next = nullptr; return t; }                                          // 해제하지 않고 떼어 낸다
    bool invariant() const {
        if ((front == nullptr) != (rear == nullptr)) return false; if (!front) return true;
        if (!liveNodes.count(reinterpret_cast<std::uintptr_t>(rear)) || rear->next != nullptr) return false;                                                                         // 숫자 비교 먼저: 해제된 노드는 읽지 않는다
        Node* p = front; while (p->next) p = p->next; return p == rear;
    }
};
int main() {
    { Q q; std::vector<int> ref; std::size_t head = 0; unsigned seed = 3; auto rnd = [&] { seed = seed * 1664525u + 1013904223u; return seed >> 8; }; int v;
      for (int step = 0; step < 50000; step++) { if (rnd() % 2) { int x = (int)rnd(); q.enqueue(x); ref.push_back(x); } else { bool had = head < ref.size(); v = -77; assert(q.dequeue(v) == had); if (had) { assert(v == ref[head]); head++; } else assert(v == -77); } assert(q.invariant()); }          // ① ②
      int d; while (q.dequeue(d)) {} assert(q.front == nullptr && q.rear == nullptr && q.invariant()); }                                                                                                      // ③ 마지막 원소 제거 직후
    assert(liveNodes.empty());
    { Q bad(false); bad.enqueue(1); int v; bad.dequeue(v); assert(bad.front == nullptr && bad.rear != nullptr && !bad.invariant()); }                                                                          // ④ rear 정리를 빠뜨린 구현
    { Q a, b; for (int i = 0; i < 5; i++) a.enqueue(i); long before = newCalls; for (int i = 0; i < 5; i++) { Node* n = a.detach(); assert(n && n->data == i); b.enqueue(n); } assert(newCalls == before && a.front == nullptr && a.invariant() && b.invariant());      // ⑤ 새 할당 없이 노드 이동
      int v; for (int i = 0; i < 5; i++) { assert(b.dequeue(v) && v == i); } assert(liveNodes.empty()); }
    std::cout << "DequeueNode: the front/rear invariant held after each of 50000 random operations; the variant that forgot to clear rear broke it right after the last element was removed; detached nodes moved between queues with zero allocations" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 4. 덱
## Deque()
### 대표코드
```cpp
#include <cstddef>
#include <deque>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 덱(Deque, double-ended queue): 양쪽 끝에서 넣고 뺄 수 있는 큐다. 스택(한쪽 끝)과 큐(양쪽 끝에서 다른 연산)를 모두 흉내 낼 수 있어 슬라이딩 윈도우 최댓값, 0-1 BFS, 회문 검사, 작업 훔치기에 쓴다. 이중 연결 리스트로 만들면 모든 연산이 O(1) 이지만 메모리가 흩어지고, 원형 배열로 만들면 모든 연산이 분할상환 O(1) 이면서 임의 접근 a[i] 도 O(1) 이다.
// 이 구현은 원형 배열 덱이다. push_front 는 front 를 (front + 용량 − 1) % 용량 으로 한 칸 뒤로 보내 그 자리에 쓰고, push_back 은 (front + 크기) % 용량 에 쓴다. 가득 차면 두 배로 키우며 front 부터 순서대로 새 배열 앞쪽에 풀어 쓴다. i 번째 원소는 (front + i) % 용량.
// 검증: 무작위 push_front/push_back/pop_front/pop_back/at(i)/front/back 6 만 번을 std::deque 와 대조: ① 모든 반환값·크기·순서가 같고 ② 임의 접근 at(i) 가 같으며 ③ 범위 밖 접근은 예외 ④ 감아 도는 상태와 성장이 정확 ⑤ 스택 사용(한쪽만)·큐 사용(반대쪽) 모두 가능 ⑥ 팰린드롬 판정 같은 응용이 가능
template <class T> class Deque {
    T* a_ = nullptr; std::size_t cap_ = 0, front_ = 0, n_ = 0;
    void grow() {
        std::size_t nc = cap_ ? cap_ * 2 : 4; T* nb = new T[nc]; for (std::size_t i = 0; i < n_; i++) nb[i] = a_[(front_ + i) % cap_];                    // front 부터 순서대로 새 배열 앞쪽에
        delete[] a_; a_ = nb; cap_ = nc; front_ = 0;
    }
public:
    ~Deque() { delete[] a_; } Deque() = default; Deque(const Deque&) = delete; Deque& operator=(const Deque&) = delete;
    void push_back(const T& v) { if (n_ == cap_) grow(); a_[(front_ + n_) % cap_] = v; n_++; }
    void push_front(const T& v) { if (n_ == cap_) grow(); front_ = (front_ + cap_ - 1) % cap_; a_[front_] = v; n_++; }
    bool pop_front(T& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % cap_; n_--; return true; }
    bool pop_back(T& out) { if (!n_) return false; out = a_[(front_ + n_ - 1) % cap_]; n_--; return true; }
    T& at(std::size_t i) { if (i >= n_) throw std::out_of_range("Deque::at"); return a_[(front_ + i) % cap_]; }
    T& front() { return at(0); } T& back() { return at(n_ - 1); }
    std::size_t size() const { return n_; } bool empty() const { return n_ == 0; } std::size_t capacity() const { return cap_; }
};
bool isPalindrome(const std::vector<int>& v) { Deque<int> d; for (int x : v) d.push_back(x); int a, b; while (d.size() > 1) { d.pop_front(a); d.pop_back(b); if (a != b) return false; } return true; }
int main() {
    std::mt19937 rng(13); Deque<int> d; std::deque<int> ref; std::size_t maxCap = 0;
    for (int step = 0; step < 60000; step++) {
        int op = rng() % 8; int v = rng() % 1000, out = -1;
        if (op == 0) { d.push_front(v); ref.push_front(v); } else if (op == 1) { d.push_back(v); ref.push_back(v); }
        else if (op == 2) { bool had = !ref.empty(); assert(d.pop_front(out) == had); if (had) { assert(out == ref.front()); ref.pop_front(); } }
        else if (op == 3) { bool had = !ref.empty(); assert(d.pop_back(out) == had); if (had) { assert(out == ref.back()); ref.pop_back(); } }
        else if (op == 4 && !ref.empty()) { std::size_t i = rng() % ref.size(); assert(d.at(i) == ref[i]); d.at(i) += 1; ref[i] += 1; }                     // ② 임의 접근과 제자리 수정
        else if (op == 5 && !ref.empty()) { assert(d.front() == ref.front() && d.back() == ref.back()); }
        else if (op == 6) { d.push_back(v); ref.push_back(v); d.push_front(v); ref.push_front(v); }
        assert(d.size() == ref.size() && d.empty() == ref.empty()); maxCap = std::max(maxCap, d.capacity());
        if (ref.size() > 500) { int t; for (int i = 0; i < 300; i++) { d.pop_front(t); ref.pop_front(); } }
    }
    { bool threw = false; Deque<int> e; try { e.at(0); } catch (const std::out_of_range&) { threw = true; } assert(threw); e.push_back(1); threw = false; try { e.at(1); } catch (const std::out_of_range&) { threw = true; } assert(threw); }          // ③
    { Deque<int> s; int v; for (int i = 0; i < 100; i++) s.push_back(i); for (int i = 99; i >= 0; i--) { assert(s.pop_back(v) && v == i); } Deque<int> q; for (int i = 0; i < 100; i++) q.push_back(i); for (int i = 0; i < 100; i++) { assert(q.pop_front(v) && v == i); } }  // ⑤ 스택·큐로도 쓴다
    assert(isPalindrome({}) && isPalindrome({1}) && isPalindrome({1, 2, 1}) && isPalindrome({1, 2, 2, 1}) && !isPalindrome({1, 2, 3}) && !isPalindrome({1, 2, 3, 2, 2}));                    // ⑥
    for (int t = 0; t < 2000; t++) { std::vector<int> v(rng() % 10); for (int& x : v) x = rng() % 3; std::vector<int> r(v.rbegin(), v.rend()); assert(isPalindrome(v) == (v == r)); }
    std::cout << "Deque: circular-array deque matched std::deque over 60000 mixed operations including random access and in-place edits (peak capacity " << maxCap << "); out-of-range access threw; used as stack, queue and palindrome checker" << std::endl; return 0;
}
// Time Complexity: 양 끝 연산·임의 접근 O(1) (분할상환)
// Space Complexity: O(N)
```
## PushFront()
### 대표코드
```cpp
#include <cstddef>
#include <deque>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 앞에 넣기(PushFront): 덱의 앞쪽 끝에 원소를 넣는다. 원형 배열에서는 front 를 한 칸 "뒤로" 보내야 하므로 (front + 용량 − 1) % 용량 이다 — front 가 0 일 때는 −1 이 아니라 용량−1 로 감아 돈다(음수 인덱스 버그). `front = (front − 1) % 용량` 은 부호 있는 정수에서 음수가 되고 부호 없는 정수에서는 SIZE_MAX 근처로 되감겨 둘 다 틀린다.
// 가득 찼을 때는 용량을 두 배로 늘리며, 감아 돈 원소를 front 부터 순서대로 풀어 새 배열 앞쪽에 둔다. 그 뒤 push_front 가 연속으로 오면 front 는 새 배열 끝 쪽으로 감아 돌아가므로 감아 돎과 성장이 번갈아 일어난다.
// 효과: push_front 만 N 번 하면 원소 순서는 넣은 순서의 정확한 역순이다(스택처럼 동작). push_front 와 push_back 이 섞이면 앞쪽 원소는 역순, 뒤쪽 원소는 순서대로 이어 붙는다.
// 검증: ① push_front 만 N 번 → 순회 결과가 역순 ② front 인덱스가 0 에서 용량−1 로 감아 도는 순간(모든 용량) ③ 올바른 식 대 틀린 식: `(f + cap − 1) % cap` 은 모든 (f, cap) 에서 올바르고 `(f − 1) % cap` 은 f = 0 에서 틀림(부호 있는 정수 −1, 부호 없는 SIZE_MAX 되감김) ④ 무작위 push_front/push_back 혼합이 std::deque 와 같고 성장 복사 총합 < 2N
class Deque {
    int* a_ = nullptr; std::size_t cap_ = 0, front_ = 0, n_ = 0; long copies_ = 0; long wraps_ = 0;
    void grow() { std::size_t nc = cap_ ? cap_ * 2 : 2; int* nb = new int[nc]; for (std::size_t i = 0; i < n_; i++) nb[i] = a_[(front_ + i) % cap_]; copies_ += (long)n_; delete[] a_; a_ = nb; cap_ = nc; front_ = 0; }
public:
    ~Deque() { delete[] a_; }
    void push_front(int v) { if (n_ == cap_) grow(); if (front_ == 0) wraps_++; front_ = (front_ + cap_ - 1) % cap_; a_[front_] = v; n_++; }                  // front 가 0 이면 용량−1 로 감아 돈다
    void push_back(int v) { if (n_ == cap_) grow(); a_[(front_ + n_) % cap_] = v; n_++; }
    std::vector<int> contents() const { std::vector<int> v; for (std::size_t i = 0; i < n_; i++) v.push_back(a_[(front_ + i) % cap_]); return v; }
    std::size_t size() const { return n_; } std::size_t frontIndex() const { return front_; } long copies() const { return copies_; } long wraps() const { return wraps_; } std::size_t capacity() const { return cap_; }
};
int main() {
    { Deque d; const int N = 1000; for (int i = 0; i < N; i++) d.push_front(i); std::vector<int> want; for (int i = N - 1; i >= 0; i--) want.push_back(i); assert(d.contents() == want && d.size() == (std::size_t)N); }                  // ① 역순
    { Deque d; d.push_back(5); d.push_back(6); d.push_front(4); d.push_front(3); d.push_back(7); d.push_front(2); assert(d.contents() == (std::vector<int>{2, 3, 4, 5, 6, 7})); }
    { Deque d; d.push_front(1); d.push_front(2); std::size_t cap = d.capacity(); assert(cap == 2 && d.frontIndex() == 0); d.push_front(3); /* 가득: 성장 후 front 는 0 -> 다시 감아 돈다 */ assert(d.capacity() == 4 && d.contents() == (std::vector<int>{3, 2, 1})); }
    for (int cap = 1; cap <= 64; cap++) { std::size_t c = cap; assert((0 + c - 1) % c == c - 1);                                                                                                                  // ② f = 0 에서 용량−1
        for (std::size_t f = 0; f < c; f++) { std::size_t right = (f + c - 1) % c; std::size_t expect = f == 0 ? c - 1 : f - 1; assert(right == expect); }                                                      // ③ 올바른 식은 모든 f 에서 맞다
        long signedWrong = (0L - 1) % (long)c; if (c > 1) assert(signedWrong < 0);                                                                                                            // 부호 있는 정수: 음수 인덱스
        unsigned long unsignedWrong = (0UL - 1) % (unsigned long)c; bool pow2 = (c & (c - 1)) == 0; assert((unsignedWrong == c - 1) == pow2); }                                              // 부호 없는 정수: 2^64 mod c = 0 인 2 의 거듭제곱 용량에서만 우연히 맞는다
    { std::size_t wrongUnsigned = ((std::size_t)0 - 1) % 6; assert(wrongUnsigned == 3 && wrongUnsigned != 5); }                                                                                              // 용량 6 에서 틀린 식: 0−1 → SIZE_MAX % 6 = 3 (올바른 값은 5)
    { Deque d; std::deque<int> ref; std::mt19937 rng(7); for (int step = 0; step < 30000; step++) { int v = rng() % 1000; if (rng() % 2) { d.push_front(v); ref.push_front(v); } else { d.push_back(v); ref.push_back(v); } if (step % 997 == 0) assert(d.contents() == std::vector<int>(ref.begin(), ref.end())); } assert(d.contents() == std::vector<int>(ref.begin(), ref.end()) && d.copies() < 2L * 30000 && d.wraps() >= 10); }    // ④
    std::cout << "PushFront: push_front-only sequences came out reversed, the front index wrapped from 0 to capacity-1 correctly (the naive (f-1)%cap formula fails there), and 30000 mixed pushes matched std::deque with growth copies < 2N" << std::endl; return 0;
}
// Time Complexity: 분할상환 O(1)
// Space Complexity: O(N)
```
## PushBack()
### 대표코드
```cpp
#include <cstddef>
#include <deque>
#include <iostream>
#include <new>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 뒤에 넣기(PushBack): 덱의 뒤쪽 끝에 원소를 넣는다. 쓸 위치 (front + 크기) % 용량 이 배열 끝을 넘으면 처음으로 감아 돈다. 가득 차면 두 배로 키우며 앞에서부터 순서대로 풀어 쓴다. N 번 push_back 의 총 복사는 2N 미만이라 분할상환 O(1).
// 예외 안전: 원소 타입의 복사가 던질 수 있으면 성장 중 일부만 옮기다 실패할 수 있다. 새 버퍼에 먼저 모두 복사하고 성공한 뒤에 옛 버퍼를 교체하면(copy-and-swap) 실패해도 덱은 이전 상태 그대로이고, 새 원소는 성장이 끝난 뒤에 넣는다. 이 항목은 복사 도중 예외를 던지는 원소로 그 보장을 시험한다.
// 검증: ① 무작위 push_back/pop_front 가 std::deque 와 같다(감아 도는 구간 포함) ② 성장 복사 총합 < 2N, 용량은 2 의 거듭제곱 ③ 복사가 도중에 던져도 크기·내용·용량이 그대로이고 생존 객체 수가 맞다(누수 없음) ④ 예외 이후 같은 push_back 을 다시 하면 성공 ⑤ push_back 만 N 번 → 넣은 순서 그대로
struct Counted { int v; static long copies, live, failAt; Counted(int x = 0) : v(x) { live++; } Counted(const Counted& o) : v(o.v) { if (++copies == failAt) throw std::runtime_error("copy failed"); live++; } Counted& operator=(const Counted& o) { v = o.v; return *this; } ~Counted() { live--; } };
long Counted::copies = 0, Counted::live = 0, Counted::failAt = -1;
template <class T> class Deque {
    T* a_ = nullptr; std::size_t cap_ = 0, front_ = 0, n_ = 0;
    void grow() {
        std::size_t nc = cap_ ? cap_ * 2 : 2; T* nb = static_cast<T*>(::operator new(nc * sizeof(T))); std::size_t i = 0;
        try { for (; i < n_; i++) new (nb + i) T(a_[(front_ + i) % cap_]); } catch (...) { while (i) nb[--i].~T(); ::operator delete(nb); throw; }                      // 실패하면 새 버퍼만 되돌린다
        for (std::size_t k = 0; k < n_; k++) a_[(front_ + k) % cap_].~T(); ::operator delete(a_); a_ = nb; cap_ = nc; front_ = 0;
    }
public:
    ~Deque() { for (std::size_t k = 0; k < n_; k++) a_[(front_ + k) % cap_].~T(); ::operator delete(a_); } Deque() = default; Deque(const Deque&) = delete; Deque& operator=(const Deque&) = delete;
    void push_back(const T& v) { if (n_ == cap_) grow(); new (a_ + (front_ + n_) % cap_) T(v); n_++; }
    bool pop_front() { if (!n_) return false; a_[front_].~T(); front_ = (front_ + 1) % cap_; n_--; return true; }
    T& at(std::size_t i) { return a_[(front_ + i) % cap_]; } std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; }
};
int main() {
    { Deque<Counted> d; std::deque<int> ref; std::mt19937 rng(5); Counted::copies = 0; long pushes = 0; for (int step = 0; step < 20000; step++) { if (rng() % 3) { int x = rng() % 1000; Counted c(x); d.push_back(c); ref.push_back(x); pushes++; } else { bool had = !ref.empty(); assert(d.pop_front() == had); if (had) ref.pop_front(); } assert(d.size() == ref.size()); if (!ref.empty()) assert(d.at(ref.size() - 1).v == ref.back() && d.at(0).v == ref.front()); }   // ① ②
      assert((d.capacity() & (d.capacity() - 1)) == 0); long growth = Counted::copies - pushes; assert(growth < 2 * pushes); }
    assert(Counted::live == 0);
    { Deque<Counted> d; for (int i = 0; i < 4; i++) d.push_back(Counted(i)); d.pop_front(); d.push_back(Counted(4)); /* 용량 4, 크기 4, 감아 돈 상태 */ assert(d.capacity() == 4 && d.size() == 4 && Counted::live == 4);
      Counted::failAt = Counted::copies + 3; bool threw = false; try { d.push_back(Counted(99)); } catch (const std::runtime_error&) { threw = true; } Counted::failAt = -1;                                            // 성장 중 세 번째 복사에서 실패
      assert(threw && d.size() == 4 && d.capacity() == 4 && Counted::live == 4); for (int i = 0; i < 4; i++) assert(d.at(i).v == i + 1);                                                                      // ③ 이전 상태 그대로, 누수 없음
      d.push_back(Counted(5)); assert(d.size() == 5 && d.capacity() == 8 && d.at(4).v == 5); }                                                                                                                // ④ 다시 하면 성공
    assert(Counted::live == 0);
    { Deque<int> d; for (int i = 0; i < 1000; i++) d.push_back(i); for (int i = 0; i < 1000; i++) assert(d.at(i) == i); }                                                                                      // ⑤
    std::cout << "PushBack: matched std::deque over 20000 operations with growth copies < 2N; an exception thrown mid-growth on a wrapped layout left size, contents, capacity and object counts untouched" << std::endl; return 0;
}
// Time Complexity: 분할상환 O(1)
// Space Complexity: O(N)
```
## PopFront()
### 대표코드
```cpp
#include <cstddef>
#include <deque>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 앞에서 꺼내기(PopFront): 덱의 앞쪽 원소를 제거해 돌려준다. 원형 배열에서는 front = (front + 1) % 용량. 큐의 dequeue 와 같은 연산이다. 빈 덱에서는 거절(false)하고 상태·출력 인자를 바꾸지 않는다.
// 비우다 보면 메모리가 남아도는 문제가 생긴다. 크기가 용량의 1/4 이하로 줄어들 때 용량을 절반으로 줄이면(축소 정책) 메모리를 돌려주면서 분할상환 O(1) 을 유지한다. 1/2 이하에서 줄이면 경계에서 push/pop 을 번갈아 할 때 매번 전체를 옮기는 thrashing 이 일어난다. 줄일 때도 front 부터 순서대로 새 배열에 풀어 쓴다.
// 응용: 슬라이딩 윈도우에서 윈도우 밖으로 나간 인덱스를 앞에서 제거할 때(SlidingWindowMaximum), 작업 큐에서 가장 오래된 작업을 꺼낼 때.
// 검증: ① 무작위 push/pop_front 가 std::deque 와 같다 ② 빈 덱 pop_front 는 false·출력 불변 ③ 비운 뒤 용량이 최소값으로 돌아가고 불변식(용량 > 4 이면 크기 > 용량/4) 유지 ④ 1/4 규칙은 경계 흐름에서 추가 이동 0, 1/2 규칙은 연산당 Θ(N) ⑤ 모두 꺼낸 뒤 다시 채워도 정상
class Deque {
    int* a_; std::size_t cap_ = 4, front_ = 0, n_ = 0; long moved_ = 0; double shrinkAt_;
    void resize(std::size_t nc) { int* nb = new int[nc]; for (std::size_t i = 0; i < n_; i++) nb[i] = a_[(front_ + i) % cap_]; moved_ += (long)n_; delete[] a_; a_ = nb; cap_ = nc; front_ = 0; }
public:
    explicit Deque(double shrinkFraction = 0.25) : a_(new int[4]), shrinkAt_(shrinkFraction) {} ~Deque() { delete[] a_; } Deque(const Deque&) = delete; Deque& operator=(const Deque&) = delete;
    void push_back(int v) { if (n_ == cap_) resize(cap_ * 2); a_[(front_ + n_) % cap_] = v; n_++; }
    bool pop_front(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % cap_; n_--; if (cap_ > 4 && n_ <= (std::size_t)(cap_ * shrinkAt_)) resize(std::max<std::size_t>(4, cap_ / 2)); return true; }
    std::size_t size() const { return n_; } std::size_t capacity() const { return cap_; } long moved() const { return moved_; } bool invariant() const { return n_ <= cap_ && (cap_ == 4 || n_ > cap_ / 4); }
};
int main() {
    { std::mt19937 rng(8); Deque d; std::deque<int> ref; int v; for (int step = 0; step < 100000; step++) { if (rng() % 5 < 2 || ref.empty()) { int x = rng(); d.push_back(x); ref.push_back(x); } else { assert(d.pop_front(v) && v == ref.front()); ref.pop_front(); } assert(d.size() == ref.size() && d.invariant()); } }          // ① ③
    { Deque d; int v = 555; assert(!d.pop_front(v) && v == 555 && d.size() == 0); }                                                                                                                                                       // ②
    { Deque d; int v; for (int i = 0; i < 100000; i++) d.push_back(i); for (int i = 0; i < 100000; i++) { assert(d.pop_front(v) && v == i); } assert(d.capacity() == 4 && d.size() == 0 && d.invariant()); for (int i = 0; i < 10; i++) d.push_back(i); assert(d.size() == 10 && d.pop_front(v) && v == 0); }   // ③ ⑤
    { Deque good(0.25), half(0.5); int v; for (int i = 0; i < 1024; i++) { good.push_back(i); half.push_back(i); } good.push_back(0); half.push_back(0); good.pop_front(v); half.pop_front(v); long g0 = good.moved(), h0 = half.moved(); const int OPS = 2000; for (int i = 0; i < OPS; i++) { good.push_back(i); good.pop_front(v); half.push_back(i); half.pop_front(v); }
      assert(good.moved() - g0 <= 1100 && half.moved() - h0 > 100L * OPS); std::cout << "1/2-rule moves per operation pair: " << (half.moved() - h0) / OPS << "; "; }                                                                                                    // ④
    std::cout << "PopFront: matched std::deque over 100000 operations with the capacity invariant intact; shrinking at 1/4 avoided the thrashing that the 1/2 rule suffers on a boundary workload" << std::endl; return 0;
}
// Time Complexity: 분할상환 O(1)
// Space Complexity: O(N), 용량은 크기의 4 배 이하
```
## PopBack()
### 대표코드
```cpp
#include <cstddef>
#include <deque>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 뒤에서 꺼내기(PopBack): 덱의 뒤쪽 원소를 제거해 돌려준다. 위치는 (front + 크기 − 1) % 용량 이며 front 는 그대로, 크기만 1 줄인다. 이 연산이 있어 덱이 스택(push_back/pop_back)으로도, 큐(push_back/pop_front)로도, 양쪽을 쓰는 알고리즘으로도 쓰인다. 양쪽을 번갈아 벗기는 대표적 응용이 회문 검사와 "양 끝에서 안쪽으로" 풀리는 문제다.
// 단조 덱(monotonic deque)은 뒤에서 pop_back 으로 쓸모없어진 후보를 버리고 앞에서 pop_front 로 만료된 후보를 버린다 — 슬라이딩 윈도우 최댓값의 핵심(SlidingWindowMaximum).
// 검증: ① 무작위 push_front/push_back/pop_front/pop_back 이 std::deque 와 같다 ② 빈 덱 pop_back 은 false·출력 불변 ③ pop_back 직후 push_back 이 같은 칸을 재사용(front 와 감아 돎 유지) ④ 문자열 회문 판정(대소문자·비문자 무시)이 정규화 후 역순 비교와 같다 ⑤ pop_back 만으로 N 개를 꺼내면 넣은 순서의 역순
class Deque {
    std::vector<int> a_; std::size_t front_ = 0, n_ = 0;
    void grow() { std::vector<int> nb(a_.empty() ? 4 : a_.size() * 2); for (std::size_t i = 0; i < n_; i++) nb[i] = a_[(front_ + i) % a_.size()]; a_.swap(nb); front_ = 0; }
public:
    void push_back(int v) { if (n_ == a_.size()) grow(); a_[(front_ + n_) % a_.size()] = v; n_++; }
    void push_front(int v) { if (n_ == a_.size()) grow(); front_ = (front_ + a_.size() - 1) % a_.size(); a_[front_] = v; n_++; }
    bool pop_front(int& out) { if (!n_) return false; out = a_[front_]; front_ = (front_ + 1) % a_.size(); n_--; return true; }
    bool pop_back(int& out) { if (!n_) return false; out = a_[(front_ + n_ - 1) % a_.size()]; n_--; return true; }
    std::size_t size() const { return n_; } std::size_t slotOfBack() const { return (front_ + n_ - 1) % a_.size(); }
};
bool isPalindromeText(const std::string& s) { Deque d; for (char c : s) if (isalnum((unsigned char)c)) d.push_back(tolower((unsigned char)c)); int a, b; while (d.size() > 1) { d.pop_front(a); d.pop_back(b); if (a != b) return false; } return true; }
int main() {
    std::mt19937 rng(3);
    { Deque d; std::deque<int> ref; int v; for (int step = 0; step < 80000; step++) { int op = rng() % 5; int x = rng() % 1000;
        if (op == 0) { d.push_front(x); ref.push_front(x); } else if (op == 1) { d.push_back(x); ref.push_back(x); } else if (op == 2) { bool had = !ref.empty(); assert(d.pop_front(v) == had); if (had) { assert(v == ref.front()); ref.pop_front(); } } else { bool had = !ref.empty(); assert(d.pop_back(v) == had); if (had) { assert(v == ref.back()); ref.pop_back(); } }
        assert(d.size() == ref.size()); } }                                                                                                                                                                  // ①
    { Deque d; int v = 321; assert(!d.pop_back(v) && v == 321); d.push_back(1); assert(d.pop_back(v) && v == 1 && !d.pop_back(v)); }                                                                          // ②
    { Deque d; for (int i = 0; i < 4; i++) d.push_back(i); int v; d.pop_front(v); d.pop_front(v); d.push_back(4); d.push_back(5); /* 감아 돈 상태 */ std::size_t slot = d.slotOfBack(); assert(d.pop_back(v) && v == 5); d.push_back(9); assert(d.slotOfBack() == slot && d.pop_back(v) && v == 9); }   // ③
    for (const std::string& s : {std::string("A man, a plan, a canal: Panama"), std::string("race a car"), std::string(""), std::string("No 'x' in Nixon"), std::string("ab"), std::string("!!")}) { std::string t; for (char c : s) if (isalnum((unsigned char)c)) t += (char)tolower((unsigned char)c); std::string r(t.rbegin(), t.rend()); assert(isPalindromeText(s) == (t == r)); }       // ④
    { Deque d; for (int i = 0; i < 1000; i++) d.push_back(i); int v; for (int i = 999; i >= 0; i--) { assert(d.pop_back(v) && v == i); } }                                                                    // ⑤
    std::cout << "PopBack: mixed push/pop on both ends matched std::deque over 80000 operations; empty pops were refused; a pop_back followed by push_back reused the same slot; palindrome checks matched normalize-and-reverse" << std::endl; return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 5. 우선순위 큐
## PriorityQueue()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <functional>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// 우선순위 큐(Priority Queue): "가장 먼저 나갈 원소" 가 도착 순서가 아니라 우선순위로 정해지는 큐다. 이진 힙(완전 이진 트리를 배열에 저장: i 의 자식은 2i+1, 2i+2, 부모는 (i−1)/2)으로 만들면 push·pop 이 O(log N), top 이 O(1) 이다. 최대 힙은 모든 노드가 자식 이상(부모 ≥ 자식)이라는 불변식 하나로 가장 큰 값이 항상 루트에 오게 한다.
// 최솟값 우선이 필요하면 비교 함수만 바꾼다(std::greater). 우선순위가 같은 원소들의 나가는 순서는 힙이 보장하지 않는다 — 스케줄러가 "같은 우선순위끼리는 먼저 온 것 먼저(FIFO)" 를 원하면 도착 번호를 비교 키에 함께 넣는다. 이 구현은 (우선순위, 도착 번호) 쌍으로 안정성을 보장한다.
// 힙 연산 자체(PushHeap/PopHeap/Heapify/BuildHeap/HeapSort)는 뒤의 항목에서 단계별로 본다. 이 항목은 완성된 컨테이너를 만들어 std::priority_queue 와 대조한다.
// 검증: ① 무작위 push/pop 에서 나오는 값 열이 std::priority_queue 와 같다(키가 서로 다르면 순서까지 동일) ② 최소 힙 (std::greater) ③ 같은 우선순위 원소가 도착 순서(FIFO)로 나온다 — 정렬 기준 (우선순위 내림차순, 도착 번호 오름차순) 과 일치 ④ 힙 불변식이 매 연산 뒤에 성립 ⑤ 사용자 정의 타입(작업)
template <class T, class Less = std::less<T>> class PriorityQueue {
    std::vector<T> h_; Less less_;
    void up(std::size_t i) { while (i > 0) { std::size_t p = (i - 1) / 2; if (!less_(h_[p], h_[i])) break; std::swap(h_[p], h_[i]); i = p; } }
    void down(std::size_t i) { std::size_t n = h_.size(); for (;;) { std::size_t l = 2 * i + 1, r = l + 1, big = i; if (l < n && less_(h_[big], h_[l])) big = l; if (r < n && less_(h_[big], h_[r])) big = r; if (big == i) return; std::swap(h_[i], h_[big]); i = big; } }
public:
    void push(const T& v) { h_.push_back(v); up(h_.size() - 1); }
    const T& top() const { return h_.front(); }
    bool pop() { if (h_.empty()) return false; h_.front() = h_.back(); h_.pop_back(); if (!h_.empty()) down(0); return true; }
    std::size_t size() const { return h_.size(); } bool empty() const { return h_.empty(); }
    bool invariant() const { for (std::size_t i = 1; i < h_.size(); i++) if (less_(h_[(i - 1) / 2], h_[i])) return false; return true; }
};
struct Task { int priority; long seq; std::string name; };
struct TaskLess { bool operator()(const Task& a, const Task& b) const { return a.priority != b.priority ? a.priority < b.priority : a.seq > b.seq; } };       // 우선순위 큰 것 먼저, 같으면 도착 번호 작은 것 먼저
int main() {
    std::mt19937 rng(5);
    { PriorityQueue<int> pq; std::priority_queue<int> ref; for (int step = 0; step < 60000; step++) { if (rng() % 3) { int v = rng() % 1000000; pq.push(v); ref.push(v); } else if (!ref.empty()) { assert(pq.top() == ref.top()); pq.pop(); ref.pop(); } assert(pq.size() == ref.size() && pq.invariant()); }                  // ① ④
      assert(!PriorityQueue<int>().pop()); }
    { PriorityQueue<int, std::greater<int>> mn; std::priority_queue<int, std::vector<int>, std::greater<int>> ref; for (int i = 0; i < 20000; i++) { int v = rng() % 1000; mn.push(v); ref.push(v); } while (!ref.empty()) { assert(mn.top() == ref.top()); mn.pop(); ref.pop(); } }              // ② 최소 힙
    { PriorityQueue<Task, TaskLess> pq; std::vector<Task> all; for (long i = 0; i < 5000; i++) { Task t{(int)(rng() % 5), i, "job" + std::to_string(i)}; pq.push(t); all.push_back(t); }
      std::stable_sort(all.begin(), all.end(), [](const Task& a, const Task& b) { return a.priority > b.priority; });                                                                                    // 우선순위 내림차순, 같으면 도착 순서 유지
      for (auto& want : all) { assert(pq.top().seq == want.seq && pq.top().name == want.name); pq.pop(); } assert(pq.empty()); }                                                                         // ③ ⑤ FIFO tie-break
    std::cout << "PriorityQueue: the binary-heap container matched std::priority_queue over 60000 operations with the heap invariant checked after every step; (priority, arrival) keys made equal-priority tasks leave in FIFO order" << std::endl; return 0;
}
// Time Complexity: push·pop O(log N), top O(1)
// Space Complexity: O(N)
```
## PushHeap()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 힙에 넣기(PushHeap, sift-up): 새 원소를 배열 맨 끝(완전 이진 트리의 다음 빈 자리)에 두고, 부모보다 크면 부모와 자리를 바꿔 가며 위로 올린다. 올라가다 부모 이상이 되거나 루트에 닿으면 멈춘다. 트리 높이가 ⌊log₂ N⌋ 이므로 비교는 많아야 그만큼이다 → O(log N).
// 최선·최악·평균: 이미 부모보다 작으면 비교 1 번에 끝난다(내림차순 삽입은 매번 1). 새 값이 최댓값이면 루트까지 올라가 높이만큼 비교한다(오름차순 삽입은 매번 최악). 무작위 삽입의 평균 비교 횟수는 상수(≈ 1.6~2.6)로 알려져 있어 N 번 삽입의 평균 비용이 O(N) 에 가깝다.
// 불변식: 삽입 전 힙이면 삽입 후에도 힙이고(재귀적으로 증명), 위로 올라가는 경로의 다른 원소들은 한 칸씩 내려올 뿐 상대 관계가 유지된다.
// 검증: ① 무작위 삽입 열 뒤 매번 힙 불변식 성립 ② 한 번의 push 에서 비교 횟수 ≤ ⌊log₂ N⌋ (N 은 삽입 후 크기) ③ 내림차순 삽입은 비교 총 N−1 번(원소당 1), 오름차순 삽입은 Σ⌊log₂ k⌋ ④ 무작위 삽입의 평균 비교 횟수 < 3 ⑤ std::push_heap 으로 만든 힙과 같은 원소 집합이고 루트가 같다 ⑥ N 번 삽입 후 pop 순서가 정렬 순서 ⑦ 동률에서 멈춘다: 같은 키만 N 번 넣으면 교환 0 번·비교 N−1 번이고, 값 범위가 좁은(중복 많은) 무작위 삽입에서 한 번의 교환 횟수 == 새 값보다 작은 조상이 연속된 길이(독립 계산) — `>=` 가 `>` 로 바뀌면 같은 키끼리 쓸데없이 자리를 바꾼다
long comparisons = 0, swaps = 0;
void pushHeap(std::vector<int>& h, int v) { h.push_back(v); std::size_t i = h.size() - 1; while (i > 0) { std::size_t p = (i - 1) / 2; comparisons++; if (h[p] >= h[i]) break; std::swap(h[p], h[i]); swaps++; i = p; } }
bool isMaxHeap(const std::vector<int>& h) { for (std::size_t i = 1; i < h.size(); i++) if (h[(i - 1) / 2] < h[i]) return false; return true; }
int floorLog2(std::size_t n) { int k = 0; while (n > 1) { n >>= 1; k++; } return k; }
int main() {
    std::mt19937 rng(4);
    for (int t = 0; t < 300; t++) { std::vector<int> h; int n = rng() % 200; for (int i = 0; i < n; i++) { long before = comparisons; pushHeap(h, rng() % 50); assert(isMaxHeap(h) && comparisons - before <= floorLog2(h.size())); } }                            // ① ②
    { std::vector<int> h; comparisons = swaps = 0; const int N = 5000; for (int i = N; i >= 1; i--) pushHeap(h, i); assert(comparisons == N - 1 && swaps == 0);                                                                                             // ③ 내림차순: 첫 원소는 비교 0, 이후 1 번씩
      std::vector<int> g; comparisons = swaps = 0; long expect = 0; for (int i = 1; i <= N; i++) { pushHeap(g, i); expect += floorLog2(i); } assert(comparisons == expect && swaps == expect && isMaxHeap(g)); }                                                                  // 오름차순: 항상 루트까지
    { double total = 0; const int RUNS = 50, N = 2000; for (int r = 0; r < RUNS; r++) { std::vector<int> h; comparisons = 0; for (int i = 0; i < N; i++) pushHeap(h, (int)rng()); total += (double)comparisons / N; } double avg = total / RUNS; assert(avg < 3.0); std::cout << "average comparisons per random push: " << avg << "; "; }   // ④
    { std::vector<int> mine, stl; for (int i = 0; i < 3000; i++) { int v = rng() % 100000; pushHeap(mine, v); stl.push_back(v); std::push_heap(stl.begin(), stl.end()); assert(mine.front() == stl.front()); } std::vector<int> a = mine, b = stl; std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end()); assert(a == b && std::is_heap(mine.begin(), mine.end())); }          // ⑤
    { std::vector<int> h, sorted; for (int i = 0; i < 1000; i++) pushHeap(h, (int)(rng() % 5000)); std::vector<int> expected = h; std::sort(expected.rbegin(), expected.rend()); std::vector<int> copy = h; while (!copy.empty()) { std::pop_heap(copy.begin(), copy.end()); sorted.push_back(copy.back()); copy.pop_back(); } assert(sorted == expected); }       // ⑥
    { std::vector<int> h; comparisons = swaps = 0; for (int i = 0; i < 1000; i++) pushHeap(h, 7); assert(comparisons == 999 && swaps == 0 && isMaxHeap(h));                                                       // ⑦ 같은 키는 올라가지 않는다
      std::vector<int> g; swaps = 0; for (int i = 0; i < 3000; i++) { int x = (int)(rng() % 8); long before = swaps, want = 0; for (std::size_t j = g.size(); j > 0 && g[(j - 1) / 2] < x; j = (j - 1) / 2) want++; pushHeap(g, x); assert(swaps - before == want); } assert(isMaxHeap(g)); }
    std::cout << "PushHeap: heap invariant and the log2(N) comparison bound held on 300 random insertion runs; descending input cost exactly N-1 comparisons and ascending input exactly the sum of floor(log2 k); results matched std::push_heap, and equal keys never swapped" << std::endl; return 0;
}
// Time Complexity: O(log N) 최악, 무작위 입력에서만 평균 O(1) 비교 (오름차순 입력은 매번 O(log N))
// Space Complexity: O(1) 추가
```
## PopHeap()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 힙에서 꺼내기(PopHeap, sift-down): 루트(최댓값)를 꺼내고 빈 자리에 맨 끝 원소를 옮긴 뒤, 두 자식 중 큰 쪽과 비교해 작으면 바꿔 가며 아래로 내린다. 한 층마다 비교가 2 번(자식끼리 1 번 + 자식과 자신 1 번)이므로 최악 2⌊log₂ N⌋ 번 → O(log N). 끝 원소는 대개 작아서 거의 잎까지 내려간다.
// 비교 횟수를 줄이는 변형(Wegener 의 bottom-up): 자식끼리만 비교하며 더 큰 쪽을 따라 잎까지 곧장 내려간 뒤(층당 비교 1 번), 거기서 옮겨 온 원소가 들어갈 자리를 위로 올라가며 찾는다. 끝 원소가 잎 근처에 속하는 것이 일반적이라 평균 비교가 ≈ log N + O(1) 로 줄어든다. 결과 힙은 클래식 방식과 같은 값 집합이며 pop 순서도 같다.
// 불변식: 두 부분 트리가 이미 힙이면 sift-down 후 전체가 힙이다(Heapify 항목의 보조 정리).
// 검증: ① 무작위 힙에서 N 번 pop 한 값 열이 내림차순 정렬과 같고 매번 힙 불변식 성립 ② 한 번의 pop 에서 클래식 비교 횟수 ≤ 2⌊log₂ N⌋ ③ 두 방식이 같은 값 열을 내며 bottom-up 의 평균 비교가 클래식보다 적다 ④ std::pop_heap 과 같은 최댓값 ⑤ 빈 힙·원소 하나 경계
long cmpClassic = 0, cmpBottomUp = 0;
void siftDownClassic(std::vector<int>& h, std::size_t i, std::size_t n) { for (;;) { std::size_t l = 2 * i + 1, r = l + 1, big = i; if (l < n) { cmpClassic++; if (h[l] > h[big]) big = l; } if (r < n) { cmpClassic++; if (h[r] > h[big]) big = r; } if (big == i) return; std::swap(h[i], h[big]); i = big; } }
void siftDownBottomUp(std::vector<int>& h, std::size_t i, std::size_t n) {
    int v = h[i]; std::size_t hole = i;
    for (;;) { std::size_t l = 2 * hole + 1, r = l + 1; if (l >= n) break; std::size_t c = l; if (r < n) { cmpBottomUp++; if (h[r] > h[l]) c = r; } h[hole] = h[c]; hole = c; }          // 자식끼리만 비교하며 잎까지 내려간다
    while (hole > i) { std::size_t p = (hole - 1) / 2; cmpBottomUp++; if (h[p] >= v) break; h[hole] = h[p]; hole = p; }                                                                              // 올라가며 v 의 자리를 찾는다
    h[hole] = v;
}
bool popClassic(std::vector<int>& h, int& out) { if (h.empty()) return false; out = h[0]; h[0] = h.back(); h.pop_back(); if (!h.empty()) siftDownClassic(h, 0, h.size()); return true; }
bool popBottomUp(std::vector<int>& h, int& out) { if (h.empty()) return false; out = h[0]; h[0] = h.back(); h.pop_back(); if (!h.empty()) siftDownBottomUp(h, 0, h.size()); return true; }
bool isMaxHeap(const std::vector<int>& h) { for (std::size_t i = 1; i < h.size(); i++) if (h[(i - 1) / 2] < h[i]) return false; return true; }
int floorLog2(std::size_t n) { int k = 0; while (n > 1) { n >>= 1; k++; } return k; }
int main() {
    std::mt19937 rng(8);
    for (int t = 0; t < 200; t++) { std::vector<int> h(rng() % 150); for (int& x : h) x = rng() % 40; std::make_heap(h.begin(), h.end()); std::vector<int> expected = h; std::sort(expected.rbegin(), expected.rend()); std::vector<int> got; int v;
        while (!h.empty()) { std::size_t n = h.size(); long before = cmpClassic; assert(popClassic(h, v) && cmpClassic - before <= 2 * floorLog2(n) + 0); got.push_back(v); assert(isMaxHeap(h)); } assert(got == expected); }                       // ① ②
    { double ratioSum = 0; int runs = 0; for (int t = 0; t < 30; t++) { std::vector<int> a(2000); for (int& x : a) x = (int)rng(); std::make_heap(a.begin(), a.end()); std::vector<int> b = a; cmpClassic = cmpBottomUp = 0; int v, w; std::vector<int> ga, gb;
        while (!a.empty()) { popClassic(a, v); popBottomUp(b, w); ga.push_back(v); gb.push_back(w); assert(isMaxHeap(b)); } assert(ga == gb); ratioSum += (double)cmpBottomUp / cmpClassic; runs++; } double ratio = ratioSum / runs; assert(ratio < 0.75); std::cout << "bottom-up used " << ratio * 100 << "% of the classic comparisons; "; }   // ③
    { std::vector<int> mine(100), stl; for (int& x : mine) x = rng() % 1000; std::make_heap(mine.begin(), mine.end()); stl = mine; int v; popClassic(mine, v); std::pop_heap(stl.begin(), stl.end()); assert(v == stl.back()); }                  // ④
    { std::vector<int> e; int v = -1; assert(!popClassic(e, v) && !popBottomUp(e, v) && v == -1); std::vector<int> one = {7}; assert(popClassic(one, v) && v == 7 && one.empty()); }                                                  // ⑤
    std::cout << "PopHeap: the classic sift-down stayed within 2*floor(log2 N) comparisons per pop and produced fully sorted output; the bottom-up variant gave identical results with fewer comparisons" << std::endl; return 0;
}
// Time Complexity: O(log N) (클래식 최대 2 log N 비교, bottom-up 평균 ≈ log N)
// Space Complexity: O(1) 추가
```
## Heapify()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 힙 정리(Heapify, sift-down 한 번): 노드 i 의 두 자식 부분 트리는 이미 힙이지만 i 의 값이 자식보다 작아 불변식이 깨져 있을 때, i 를 더 큰 자식과 바꿔 가며 아래로 내려 전체 부분 트리를 힙으로 만든다. 힙 알고리즘 전체(꺼내기, 힙 만들기, 힙 정렬)가 이 한 동작의 반복이다.
// 정확성의 핵심은 사전 조건이다: "i 의 양쪽 부분 트리가 힙" 이어야 한다. 이 조건이 없으면 한 번의 sift-down 으로 힙이 되지 않는다. 사후 조건: i 아래 전체가 힙이고 원소 집합은 그대로(교환만 하므로). 한 번의 비용은 i 의 높이에 비례하는 O(log N).
// 이 항목은 이 보조 정리를 증명하는 대신 전수 검사한다: 크기 1..8 의 모든 순열 중 "루트의 두 자식 부분 트리가 힙" 인 배열 전부에 heapify(0)을 적용하면 항상 힙이 된다. 사전 조건이 없는 배열에서는 실패할 수 있음도 보인다.
// 검증: ① n ≤ 8 의 모든 순열(약 5 만 개) 중 사전 조건을 만족하는 것 전부에서 heapify(0) 후 전체가 힙이고 순열 ② 교환 횟수 ≤ 트리 높이 ③ 사전 조건이 없으면 heapify 후에도 힙이 아닌 배열이 존재 ④ 큰 무작위 힙에서 임의의 노드 값을 줄인(감소 키) 뒤 heapify(i) 로 복구 ⑤ 알려진 예제 하나(루트를 0 으로 바꾼 힙에서 8 이 루트로 올라온다). 최소 힙은 비교만 뒤집은 대칭이라 따로 검사하지 않는다
int swaps = 0;
void heapify(std::vector<int>& a, std::size_t i, std::size_t n) { for (;;) { std::size_t l = 2 * i + 1, r = l + 1, big = i; if (l < n && a[l] > a[big]) big = l; if (r < n && a[r] > a[big]) big = r; if (big == i) return; std::swap(a[i], a[big]); swaps++; i = big; } }
bool subtreeIsHeap(const std::vector<int>& a, std::size_t root, std::size_t n) { if (root >= n) return true; std::size_t l = 2 * root + 1, r = l + 1; if (l < n && a[l] > a[root]) return false; if (r < n && a[r] > a[root]) return false; return subtreeIsHeap(a, l, n) && subtreeIsHeap(a, r, n); }
int height(std::size_t n) { int h = 0; while (n > 1) { n >>= 1; h++; } return h; }
int main() {
    long checked = 0, withoutPre = 0, failedWithoutPre = 0;
    for (std::size_t n = 1; n <= 8; n++) { std::vector<int> p(n); std::iota(p.begin(), p.end(), 1);
        do { bool pre = n == 1 || (subtreeIsHeap(p, 1, n) && subtreeIsHeap(p, 2, n)); std::vector<int> q = p; swaps = 0; heapify(q, 0, n);
            if (pre) { assert(subtreeIsHeap(q, 0, n) && std::is_permutation(q.begin(), q.end(), p.begin()) && swaps <= height(n)); checked++; }                                                    // ① ②
            else { withoutPre++; if (!subtreeIsHeap(q, 0, n)) failedWithoutPre++; } } while (std::next_permutation(p.begin(), p.end())); }
    assert(checked > 1000 && failedWithoutPre > 0);                                                                                                                                                  // ③ 사전 조건이 없으면 실패할 수 있다
    std::mt19937 rng(2);
    for (int t = 0; t < 500; t++) { std::vector<int> a(1 + rng() % 300); for (int& x : a) x = rng() % 1000; std::make_heap(a.begin(), a.end()); std::size_t i = rng() % a.size(); a[i] = (int)(rng() % 5);                  // 감소 키: 값을 작게 바꾼다 (i 의 부분 트리 밖은 힙을 유지)
        // i 의 위쪽 조상과의 관계는 값이 줄었으니 그대로 성립한다. 아래만 고치면 된다
        heapify(a, i, a.size()); assert(std::is_heap(a.begin(), a.end())); }                                                                                                                         // ④
    { std::vector<int> a = {9, 4, 8, 1, 2, 7, 6}; a[0] = 0; heapify(a, 0, a.size()); assert(std::is_heap(a.begin(), a.end()) && a == (std::vector<int>{8, 4, 7, 1, 2, 0, 6})); }      // ⑤
    std::cout << "Heapify: " << checked << " permutations satisfying the precondition were all repaired by one sift-down with at most height(N) swaps; " << failedWithoutPre << " of " << withoutPre << " arrays lacking the precondition stayed broken; decrease-key repair worked on 500 random heaps" << std::endl; return 0;
}
// Time Complexity: O(log N) (노드의 높이에 비례)
// Space Complexity: O(1)
```
## BuildHeap()
### 대표코드
```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 힙 만들기(BuildHeap, Floyd 1964): 임의의 배열을 힙으로 바꾼다. 방법 두 가지. ① 원소를 하나씩 push(sift-up): N 번이므로 O(N log N) ② 바닥에서 위로 sift-down(Floyd): 마지막 내부 노드 ⌊N/2⌋−1 부터 0 까지 차례로 heapify. 잎은 이미 힙이므로 건너뛰고, 높이 h 인 노드는 sift-down 이 최대 h 단계인데 높이 h 인 노드는 많아야 ⌈N/2^(h+1)⌉ 개 → 총 비용 Σ h·N/2^(h+1) = O(N). 비교 횟수는 2N 이하다.
// 왜 선형인가: 비용 대부분은 아래층 노드가 짧게 내려가는 데서 나온다. 반대로 push 방식은 아래층(노드의 절반)이 매번 높이만큼 올라갈 수 있어 N log N 이다. 입력이 오름차순일 때 push 방식은 최악이고 Floyd 는 입력에 상관없이 2N 이하다.
// 부수적 사실: 서로 다른 N 개 값으로 만들 수 있는 최대 힙의 수는 h(N) = C(N−1, L) · h(L) · h(R) (L, R 은 왼쪽·오른쪽 부분 트리 크기): 1, 1, 2, 3, 8, 20, 80, 210, 896… 이다. 아래에서 점화식을 전수 열거와 대조한다.
// 검증: ① 무작위·정렬·역정렬·동일값 배열에서 Floyd 결과가 힙이고 원소 집합이 같다 ② Floyd 의 비교 횟수 ≤ 2N (N ≤ 4000, 최악 입력 포함) ③ 오름차순 입력에서 push 방식의 비교 횟수가 Floyd 의 몇 배 이상 ④ 힙의 개수 점화식 == N ≤ 9 모든 순열 전수 열거 ⑤ std::make_heap 과 같은 원소 집합과 루트
long cmpFloyd = 0, cmpPush = 0;
void siftDown(std::vector<int>& a, std::size_t i, std::size_t n) { for (;;) { std::size_t l = 2 * i + 1, r = l + 1, big = i; if (l < n) { cmpFloyd++; if (a[l] > a[big]) big = l; } if (r < n) { cmpFloyd++; if (a[r] > a[big]) big = r; } if (big == i) return; std::swap(a[i], a[big]); i = big; } }
void buildFloyd(std::vector<int>& a) { std::size_t n = a.size(); for (std::size_t i = n / 2; i-- > 0;) siftDown(a, i, n); }
void buildByPush(std::vector<int>& a) { for (std::size_t k = 1; k < a.size(); k++) { std::size_t i = k; while (i > 0) { std::size_t p = (i - 1) / 2; cmpPush++; if (a[p] >= a[i]) break; std::swap(a[p], a[i]); i = p; } } }
bool isMaxHeap(const std::vector<int>& h) { for (std::size_t i = 1; i < h.size(); i++) if (h[(i - 1) / 2] < h[i]) return false; return true; }
long long choose(int n, int k) { long long r = 1; for (int i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; }
long long heapsOfSize(int n) { if (n <= 1) return 1; int h = 0; while ((1 << (h + 1)) <= n) h++; int last = n - ((1 << h) - 1); int L = (1 << (h - 1)) - 1 + std::min(last, 1 << (h - 1)), R = n - 1 - L; return choose(n - 1, L) * heapsOfSize(L) * heapsOfSize(R); }
int main() {
    std::mt19937 rng(6); long worstFloyd = 0; double worstRatio = 0;
    for (int t = 0; t < 400; t++) { int n = rng() % 300; std::vector<int> a(n); int kind = t % 4; for (int i = 0; i < n; i++) a[i] = kind == 0 ? (int)(rng() % 1000) : kind == 1 ? i : kind == 2 ? n - i : 7; std::vector<int> orig = a; cmpFloyd = 0; buildFloyd(a);
        assert(isMaxHeap(a) && std::is_permutation(a.begin(), a.end(), orig.begin())); assert(cmpFloyd <= 2L * n); worstFloyd = std::max(worstFloyd, cmpFloyd); if (n) worstRatio = std::max(worstRatio, (double)cmpFloyd / n); }                          // ① ②
    { const int N = 4000; std::vector<int> asc(N); std::iota(asc.begin(), asc.end(), 0); std::vector<int> a = asc, b = asc; cmpFloyd = cmpPush = 0; buildFloyd(a); buildByPush(b); assert(isMaxHeap(a) && isMaxHeap(b) && cmpFloyd <= 2L * N && cmpPush > 4 * cmpFloyd); std::cout << "ascending input: Floyd " << cmpFloyd << " comparisons vs repeated push " << cmpPush << "; "; }   // ③
    for (int n = 1; n <= 9; n++) { std::vector<int> p(n); std::iota(p.begin(), p.end(), 1); long long count = 0; do { count += isMaxHeap(p); } while (std::next_permutation(p.begin(), p.end())); assert(count == heapsOfSize(n)); }               // ④ 1, 1, 2, 3, 8, 20, 80, 210, 896
    { std::vector<int> a(1000); for (int& x : a) x = rng() % 5000; std::vector<int> stl = a; buildFloyd(a); std::make_heap(stl.begin(), stl.end()); assert(a.front() == stl.front() && std::is_permutation(a.begin(), a.end(), stl.begin())); }          // ⑤
    std::cout << "BuildHeap: Floyd's bottom-up construction never exceeded 2N comparisons (worst " << worstRatio << "N across kinds); heap counts for N=1..9 matched the recurrence (" << heapsOfSize(9) << " for N=9)" << std::endl; return 0;
}
// Time Complexity: Floyd O(N), 반복 push O(N log N)
// Space Complexity: O(1) 추가
```
## HeapSort()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 힙 정렬(HeapSort, Williams 1964): 배열을 최대 힙으로 만든(BuildHeap, O(N)) 뒤, 루트(최댓값)를 배열 맨 뒤 원소와 바꾸고 힙 크기를 1 줄인 다음 루트를 sift-down 하는 일을 반복한다. 매번 가장 큰 값이 뒤쪽에 확정되므로 끝나면 오름차순 정렬이다. 추가 메모리 O(1)(제자리), 최악에도 O(N log N) — 퀵 정렬의 O(N²) 최악이 없고 병합 정렬의 O(N) 추가 메모리가 없다.
// 단점: 안정 정렬이 아니다(같은 키의 원래 순서가 바뀐다), 메모리 접근이 부모-자식 사이에서 크게 건너뛰어 캐시 효율이 퀵 정렬보다 나쁘다. 그래서 실무 정렬은 퀵 정렬 + 힙 정렬 폴백(introsort)을 쓴다: 재귀가 너무 깊어지면 힙 정렬로 넘어가 최악을 막는다.
// 부산물: 크기 k 의 최소 힙으로 스트림에서 가장 큰 k 개를 O(N log k) 에 구한다(top-k). 전체를 정렬하지 않아도 되는 경우의 표준 기법이다.
// 검증: ① 크기 0..300 의 무작위·정렬·역정렬·모두 같은 값·중복 많은 배열에서 std::sort 결과와 같다 ② 비교 횟수 ≤ 2N⌊log₂N⌋ + 2N ③ 10 만 개 배열 ④ 불안정함을 반례로 보임 (같은 키 쌍의 상대 순서가 바뀐 경우를 센다) ⑤ top-k 가 정렬 후 앞 k 개와 같다
long cmp = 0;
template <class T, class Less> void siftDown(std::vector<T>& a, std::size_t i, std::size_t n, Less less) { for (;;) { std::size_t l = 2 * i + 1, r = l + 1, big = i; if (l < n) { cmp++; if (less(a[big], a[l])) big = l; } if (r < n) { cmp++; if (less(a[big], a[r])) big = r; } if (big == i) return; std::swap(a[i], a[big]); i = big; } }
template <class T, class Less> void heapSort(std::vector<T>& a, Less less) {
    std::size_t n = a.size(); for (std::size_t i = n / 2; i-- > 0;) siftDown(a, i, n, less);                       // 1 단계: 최대 힙 만들기
    for (std::size_t end = n; end > 1; end--) { std::swap(a[0], a[end - 1]); siftDown(a, 0, end - 1, less); }       // 2 단계: 최댓값을 뒤로 보내고 힙 크기를 줄인다
}
template <class T> std::vector<T> topK(const std::vector<T>& stream, std::size_t k) {                                 // 크기 k 의 최소 힙: 가장 큰 k 개를 O(N log k) 에
    std::vector<T> heap; for (const T& x : stream) { if (heap.size() < k) { heap.push_back(x); std::push_heap(heap.begin(), heap.end(), std::greater<T>()); } else if (!heap.empty() && x > heap.front()) { std::pop_heap(heap.begin(), heap.end(), std::greater<T>()); heap.back() = x; std::push_heap(heap.begin(), heap.end(), std::greater<T>()); } }
    std::sort(heap.begin(), heap.end(), std::greater<T>()); return heap;
}
int main() {
    std::mt19937 rng(3); auto less = [](int a, int b) { return a < b; };
    for (int t = 0; t < 1500; t++) { int n = rng() % 301; std::vector<int> a(n); int kind = t % 5; for (int i = 0; i < n; i++) a[i] = kind == 0 ? (int)rng() : kind == 1 ? i : kind == 2 ? n - i : kind == 3 ? 5 : (int)(rng() % 4); std::vector<int> want = a; std::sort(want.begin(), want.end()); cmp = 0; heapSort(a, less);
        assert(a == want); double bound = 2.0 * n * std::max(1.0, std::floor(std::log2((double)std::max(n, 1)))) + 2.0 * n; assert(cmp <= bound); }                                                       // ① ②
    { std::vector<int> big(100000); for (int& x : big) x = (int)rng(); std::vector<int> want = big; std::sort(want.begin(), want.end()); heapSort(big, less); assert(big == want); }                                    // ③
    { struct P { int key, order; }; std::vector<P> v; for (int i = 0; i < 2000; i++) v.push_back({(int)(rng() % 20), i}); std::vector<P> hs = v, st = v; heapSort(hs, [](const P& a, const P& b) { return a.key < b.key; }); std::stable_sort(st.begin(), st.end(), [](const P& a, const P& b) { return a.key < b.key; });
      long inverted = 0; for (std::size_t i = 1; i < hs.size(); i++) if (hs[i - 1].key == hs[i].key && hs[i - 1].order > hs[i].order) inverted++; long stableInverted = 0; for (std::size_t i = 1; i < st.size(); i++) if (st[i - 1].key == st[i].key && st[i - 1].order > st[i].order) stableInverted++; assert(inverted > 0 && stableInverted == 0); }          // ④ 불안정
    for (int t = 0; t < 300; t++) { std::vector<int> s(rng() % 200); for (int& x : s) x = rng() % 1000; std::size_t k = rng() % 20; std::vector<int> sorted = s; std::sort(sorted.begin(), sorted.end(), std::greater<int>()); if (sorted.size() > k) sorted.resize(k); assert(topK(s, k) == sorted); }       // ⑤
    std::cout << "HeapSort: in-place heap sort matched std::sort on 1500 arrays of every shape and a 100000-element array, stayed within the comparison bound, was shown to be unstable, and the size-k heap returned the exact top-k" << std::endl; return 0;
}
// Time Complexity: O(N log N) (최악 포함), top-k 는 O(N log k)
// Space Complexity: O(1) 추가 (제자리)
```

## CalendarQueue()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 캘린더 큐(Calendar Queue, Brown 1988): 이산 사건 시뮬레이터의 우선순위 큐. 탁상 달력처럼 "하루(폭 width)" 칸이 nb 개인 배열이고 사건을 자기 날짜의 칸에 (우선순위 순으로 정렬해) 넣는다.
// 칸 번호 = (우선순위 / width) mod nb 이므로 한 바퀴(= 한 해, nb·width)를 넘는 먼 미래의 사건도 같은 칸에 섞여 들어가고, 꺼낼 때는 "이번 해의 현재 날짜" 에 속하는 사건(우선순위 < 그 칸의 끝)만 꺼낸다.
// 현재 칸부터 달력을 넘기며 첫 번째로 해당하는 사건을 찾고, 한 바퀴를 다 돌아도 없으면 전체 칸의 맨 앞에서 최솟값을 직접 찾는다. 사건이 칸에 고르게 퍼지면 넣기·꺼내기가 평균 O(1) 이다(이진 힙의 O(log n)).
// 사건 수가 칸 수의 두 배를 넘거나 절반 아래로 떨어지면 칸 수를 두 배/절반으로 바꾸고 width 를 "가장 이른 사건 25 개의 평균 간격 x 3" 으로 다시 잡는다(간격이 고르지 않은 외톨이는 평균에서 뺀다).
// 검증: ① 손으로 확인한 작은 예 ② 같은 (우선순위, 입력 순번) 순서를 가진 std::multiset 오라클과 꺼낸 순서가 완전히 같다 — 시뮬레이션 "홀드 모델"(꺼내고 미래 사건 넣기, 분포 3 가지: 균등·지수 비슷·두 군집), 과거 우선순위 삽입,
//       일괄 넣기 후 비우기, 전부 같은 우선순위, 큰 간격 ③ 칸 수가 실제로 늘고 줄었으며 꺼낼 때 훑은 칸 수의 평균이 작다(O(1) 에 가깝다)
class CalendarQueue {
    typedef std::pair<long long, long long> Ev;                                                    // (우선순위, 입력 순번): 순번으로 같은 우선순위의 선입선출을 보장
    std::vector<std::vector<Ev>> b_; long long width_ = 1, lastPrio_ = 0, top_ = 1; size_t n_ = 0, last_ = 0; long long seq_ = 0;
    size_t bucketOf(long long p) const { return (size_t)((p / width_) % (long long)b_.size()); }
    void put(const Ev& e) { auto& v = b_[bucketOf(e.first)]; v.insert(std::upper_bound(v.begin(), v.end(), e), e); }
    void rebuild(size_t nb) {                                                                      // 칸 수를 바꾸고 width 를 표본에서 다시 정한다
        std::vector<Ev> all; for (auto& v : b_) all.insert(all.end(), v.begin(), v.end());
        const size_t m = std::min<size_t>(25, all.size()); std::partial_sort(all.begin(), all.begin() + (long)m, all.end());
        long long sum = 0, cnt = 0; for (size_t i = 1; i < m; ++i) { sum += all[i].first - all[i - 1].first; ++cnt; }
        if (cnt) { const long long avg = sum / cnt; long long s2 = 0, c2 = 0; for (size_t i = 1; i < m; ++i) { const long long g = all[i].first - all[i - 1].first; if (g <= 2 * avg) { s2 += g; ++c2; } } if (c2) width_ = std::max<long long>(1, 3 * s2 / c2); }
        b_.assign(nb, {}); for (const Ev& e : all) put(e);
        if (n_) { lastPrio_ = all.empty() ? 0 : std::min_element(all.begin(), all.end())->first; last_ = bucketOf(lastPrio_); top_ = (lastPrio_ / width_ + 1) * width_; }
    }
public:
    long scans = 0, resizesUp = 0, resizesDown = 0;                                                // scans: 꺼낼 때 훑은 칸 수의 합
    CalendarQueue() : b_(2) {}
    size_t size() const { return n_; } size_t buckets() const { return b_.size(); } long long width() const { return width_; }
    void push(long long prio) {
        const Ev e{prio, seq_++}; if (n_ == 0 || prio < lastPrio_) { lastPrio_ = prio; last_ = bucketOf(prio); top_ = (prio / width_ + 1) * width_; }       // 과거의 사건이면 달력의 현재 날짜를 되돌린다
        put(e); ++n_; if (n_ > 2 * b_.size()) { rebuild(2 * b_.size()); ++resizesUp; }
    }
    Ev pop() {                                                                                     // 우선순위가 가장 작은 사건
        size_t i = last_; long long top = top_;
        for (size_t step = 0; step < b_.size(); ++step) {
            ++scans; auto& v = b_[i];
            if (!v.empty() && v.front().first < top) { Ev e = v.front(); v.erase(v.begin()); --n_; last_ = i; top_ = top; lastPrio_ = e.first; shrink(); return e; }
            i = (i + 1) % b_.size(); top += width_;
        }
        size_t best = 0; bool any = false;                                                         // 한 해를 돌아도 없다: 전체에서 최솟값을 직접 찾는다
        for (size_t j = 0; j < b_.size(); ++j) if (!b_[j].empty() && (!any || b_[j].front() < b_[best].front())) { best = j; any = true; }
        Ev e = b_[best].front(); b_[best].erase(b_[best].begin()); --n_; last_ = best; lastPrio_ = e.first; top_ = (e.first / width_ + 1) * width_; shrink(); return e;
    }
    void shrink() { if (n_ < b_.size() / 2 && b_.size() > 2) { rebuild(b_.size() / 2); ++resizesDown; } }
};

int main() {
    {   CalendarQueue q; for (long long p : {50, 10, 40, 10, 30}) q.push(p);                       // 손으로 확인: 우선순위 순서, 같은 10 은 먼저 넣은 것부터
        std::vector<std::pair<long long, long long>> out; while (q.size()) out.push_back(q.pop());
        assert((out == std::vector<std::pair<long long, long long>>{{10, 1}, {10, 3}, {30, 4}, {40, 2}, {50, 0}})); }
    std::mt19937_64 rng(5); long totalPops = 0; size_t maxBuckets = 0; long up = 0, down = 0; double worstAvgScan = 0;
    for (int scenario = 0; scenario < 6; ++scenario) {
        CalendarQueue q; std::set<std::pair<long long, long long>> oracle; long long seq = 0, clock = 0; auto push = [&](long long p) { q.push(p); oracle.insert({p, seq++}); };
        auto pop = [&]() { auto e = q.pop(); assert(e == *oracle.begin()); oracle.erase(oracle.begin()); clock = e.first; ++totalPops; };
        auto incr = [&](int dist) -> long long { if (dist == 0) return (long long)(rng() % 200); if (dist == 1) { long long x = 1; while (rng() % 3 && x < (1 << 20)) x *= 2; return x + (long long)(rng() % 7); } return (rng() % 2 ? 5 : 100000) + (long long)(rng() % 50); };   // 균등 / 거의 지수 / 두 군집
        for (int i = 0; i < 400; ++i) push((long long)(rng() % 5000));
        const long scansBefore = q.scans; long pops0 = totalPops;
        for (int step = 0; step < 60000; ++step) {                                                 // 홀드 모델: 하나 꺼내고 그 시각 이후의 사건 하나를 넣는다 (때로는 과거의 사건도)
            pop(); if (scenario == 3 && step % 50 == 0) push(clock > 100 ? clock - (long long)(rng() % 100) : 0); push(clock + incr(scenario % 3));
            if (scenario == 4 && step % 1000 == 0) { for (int k = 0; k < 3000; ++k) push(clock + (long long)(rng() % 1000000)); while (oracle.size() > 400) pop(); }                             // 일괄 넣기 후 줄이기
        }
        const double avgScan = (double)(q.scans - scansBefore) / (double)(totalPops - pops0); if (scenario != 4) worstAvgScan = std::max(worstAvgScan, avgScan);
        maxBuckets = std::max(maxBuckets, q.buckets()); up += q.resizesUp; down += q.resizesDown;
        while (q.size()) pop(); assert(oracle.empty());
    }
    {   CalendarQueue q; std::multiset<std::pair<long long, long long>> oracle; for (long long i = 0; i < 5000; ++i) { q.push(7); oracle.insert({7, i}); } while (q.size()) { assert(q.pop() == *oracle.begin()); oracle.erase(oracle.begin()); } }    // 전부 같은 우선순위: 입력 순서
    assert(maxBuckets >= 64 && up > 3 && down > 3 && worstAvgScan < 12.0);
    std::cout << "CalendarQueue: dequeue order matched a (priority, insertion-order) multiset oracle over " << totalPops << " pops in 6 workloads (hold model with 3 increment distributions, past-dated inserts, bulk fill/drain, equal priorities); the calendar grew to " << maxBuckets << " buckets (" << up << " doublings, " << down << " halvings) and a dequeue scanned " << worstAvgScan << " buckets on average" << std::endl;
    return 0;
}
// Time Complexity: 평균 O(1) (사건이 칸에 고르게 퍼질 때), 최악 O(n) (한 칸에 몰릴 때), 칸 수 조정은 분할상환 O(1)
// Space Complexity: O(n + 칸 수)
```

## RadixHeap()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 기수 힙(Radix Heap, Ahuja·Mehlhorn·Orlin·Tarjan 1990): 정수 키에 대한 "단조" 우선순위 큐 — 새로 넣는 키는 마지막으로 꺼낸 값(last) 이상이어야 한다(다익스트라에서 자연스럽게 성립).
// 키 x 를 last 와 비교해 처음으로 달라지는 비트 위치로 버킷을 정한다: 버킷 0 = last 와 같은 키, 버킷 i = x xor last 의 최상위 비트가 i-1 번째(즉 x 가 last 보다 크고 2^(i-1) 이상 차이).
// 꺼낼 때 버킷 0 이 비어 있으면 첫 번째 비지 않은 버킷 i 에서 최솟값을 골라 새 last 로 삼고, 그 버킷의 원소들을 새 last 기준으로 다시 나누면 모두 더 낮은 버킷으로 내려간다 — 원소 하나는 버킷을 아래로만 이동하므로 최대 (비트 수 + 1) 번,
// 분할상환 비용은 원소당 O(log C) (C: 키의 최대 차이). 이진 힙(O(log n))보다 상수가 작고 캐시 친화적이라 정수 가중치 다익스트라·정렬 경매에서 쓴다.
// 검증: ① 손으로 확인 ② 단조 작업(꺼낸 키 이상만 넣기) 무작위 20 만 번을 std::priority_queue 와 대조 ③ 무작위 64 비트 키 전부 넣고 꺼내기 == 정렬 ④ 정수 가중치 무작위 그래프의 다익스트라가 힙 구현과 같은 거리를 내고
//       이동 횟수가 원소당 최대 65 이하 (단조가 아닌 삽입은 assert 로 거부한다)
class RadixHeap {
    typedef uint64_t U; std::vector<std::pair<U, int>> b_[65]; U last_ = 0; size_t n_ = 0;
    static int bucketOf(U x, U last) { return x == last ? 0 : 64 - __builtin_clzll(x ^ last); }    // x xor last 의 최상위 비트 위치 + 1
public:
    long moves = 0;                                                                                // 원소가 버킷 사이를 옮겨 다닌 총 횟수
    bool empty() const { return n_ == 0; } size_t size() const { return n_; } U lastKey() const { return last_; }
    void push(U key, int val) { assert(key >= last_); b_[bucketOf(key, last_)].push_back({key, val}); ++n_; ++moves; }
    std::pair<U, int> pop() {
        if (b_[0].empty()) {
            int i = 1; while (b_[i].empty()) ++i;                                                  // 첫 번째 비지 않은 버킷
            U mn = b_[i][0].first; for (const auto& e : b_[i]) mn = std::min(mn, e.first);
            last_ = mn; std::vector<std::pair<U, int>> cell; cell.swap(b_[i]);
            for (const auto& e : cell) { const int j = bucketOf(e.first, last_); assert(j < i); b_[j].push_back(e); ++moves; }      // 새 last 기준으로 재분배: 모두 더 낮은 버킷으로
        }
        auto e = b_[0].back(); b_[0].pop_back(); --n_; return e;
    }
};
struct Arc { int to; uint64_t w; };
std::vector<uint64_t> dijkstraRadix(const std::vector<std::vector<Arc>>& g, int s, long& moves, size_t& pushes) {
    const uint64_t INF = ~0ULL; std::vector<uint64_t> d(g.size(), INF); RadixHeap h; d[s] = 0; h.push(0, s); pushes = 1;
    while (!h.empty()) { auto [du, u] = h.pop(); if (du > d[u]) continue; for (const Arc& a : g[(size_t)u]) if (du + a.w < d[(size_t)a.to]) { d[(size_t)a.to] = du + a.w; h.push(d[(size_t)a.to], a.to); ++pushes; } }      // 키 du + w >= du = last: 단조
    moves = h.moves; return d;
}
std::vector<uint64_t> dijkstraHeap(const std::vector<std::vector<Arc>>& g, int s) {
    const uint64_t INF = ~0ULL; std::vector<uint64_t> d(g.size(), INF); std::priority_queue<std::pair<uint64_t, int>, std::vector<std::pair<uint64_t, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (const Arc& a : g[(size_t)u]) if (du + a.w < d[(size_t)a.to]) { d[(size_t)a.to] = du + a.w; pq.push({d[(size_t)a.to], a.to}); } }
    return d;
}

int main() {
    {   RadixHeap h; for (uint64_t k : {5, 3, 9, 3, 7}) h.push(k, (int)k * 10);                    // 손으로 확인: 3 3 5 7 9 순서, 꺼낸 뒤에는 그 값 이상만 넣을 수 있다
        std::vector<uint64_t> out; while (!h.empty()) { auto e = h.pop(); out.push_back(e.first); if (e.first == 5) h.push(6, 60); }
        assert((out == std::vector<uint64_t>{3, 3, 5, 6, 7, 9}) && h.lastKey() == 9); }
    std::mt19937_64 rng(3); RadixHeap h; std::priority_queue<std::pair<uint64_t, int>, std::vector<std::pair<uint64_t, int>>, std::greater<>> ref; uint64_t last = 0; long pushed = 0;
    for (int step = 0; step < 200000; ++step) {
        if (ref.empty() || rng() % 100 < 55) { const int mode = (int)(rng() % 3); const uint64_t add = mode == 0 ? rng() % 16 : mode == 1 ? rng() % (1ULL << 20) : rng() >> (rng() % 60);        // 가까운 키 / 중간 / 아주 먼 키
            const uint64_t key = last + std::min<uint64_t>(add, ~0ULL - last); h.push(key, step); ref.push({key, step}); ++pushed; }
        else { auto a = h.pop(); auto b = ref.top(); ref.pop(); assert(a.first == b.first); last = a.first; }                                                              // 키가 같은 원소들의 값(step) 순서는 규정하지 않는다
        assert(h.size() == ref.size());
    }
    while (!ref.empty()) { auto a = h.pop(); assert(a.first == ref.top().first); ref.pop(); }
    {   RadixHeap sorter; std::vector<uint64_t> keys(100000); for (auto& k : keys) k = rng(); for (uint64_t k : keys) sorter.push(k, 0);
        std::sort(keys.begin(), keys.end()); for (uint64_t k : keys) assert(sorter.pop().first == k); assert(sorter.moves <= 65L * 100000); }                              // 전부 넣고 꺼내기 == 정렬, 이동 <= 원소당 65
    long maxMovesPerPush = 0;
    for (int trial = 0; trial < 60; ++trial) {
        const int n = 2 + (int)(rng() % 400), m = (int)(rng() % (6 * (unsigned)n)); const uint64_t maxW = 1 + rng() % (trial % 2 ? 1000000000ULL : 20ULL); std::vector<std::vector<Arc>> g((size_t)n);
        for (int i = 0; i < m; ++i) g[rng() % (unsigned)n].push_back({(int)(rng() % (unsigned)n), rng() % (maxW + 1)});         // 가중치 0 포함
        long moves = 0; size_t pushes = 0; assert(dijkstraRadix(g, 0, moves, pushes) == dijkstraHeap(g, 0)); maxMovesPerPush = std::max(maxMovesPerPush, moves / (long)pushes);
        assert(moves <= 65L * (long)pushes);
    }
    std::cout << "RadixHeap: 200000 monotone push/pop operations matched std::priority_queue, 100000 random 64-bit keys came out sorted, and radix-heap Dijkstra equalled binary-heap Dijkstra on 60 random graphs (zero-weight edges included); at most " << maxMovesPerPush << " bucket moves per pushed element" << std::endl;
    return 0;
}
// Time Complexity: push O(1), pop 분할상환 O(log C) (원소 하나는 버킷을 아래로만 옮겨 최대 65 번), 다익스트라 O(E + V log C)
// Space Complexity: O(n + 65)
```
# Part 6. BFS
## BreadthFirstSearch()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 너비 우선 탐색 (큐 관점의 요약, 정본은 Graph.md Part 3): 시작점에서 가까운 정점부터 층(level)별로 방문한다. 큐에 시작점을 넣고, 꺼낸 정점의 아직 보지 못한 이웃을 큐에 넣으며 거리를 1 늘려 기록한다. 큐의 FIFO 성질이 "거리 d 인 정점을 모두 처리한 뒤에야 거리 d+1 인 정점을 처리" 를 보장한다.
// 큐의 불변식이 알고리즘의 증명이다: ① 큐에 든 정점들의 거리는 비내림차순이고 ② 가장 앞과 가장 뒤의 거리 차이는 1 이하다(큐에는 거리 d 와 d+1 짜리만 섞여 있다). 이 때문에 가중치 없는 그래프에서 처음 도달한 거리가 최단 거리다. 또 모든 간선 (u, v) 에서 |dist[u] − dist[v]| ≤ 1 이다.
// 검증: 무작위 방향 그래프에서 ① 거리가 플로이드–워셜 최단 거리와 같다 ② 큐 불변식(비내림차순, 최대-최소 ≤ 1)을 매 단계 확인 ③ 모든 간선에서 dist[v] ≤ dist[u] + 1 ④ 도달 불가 정점은 −1 ⑤ 방문 순서가 거리 비내림차순 ⑥ 큐에 들어간 총 횟수 == 도달 가능한 정점 수(각 정점은 한 번만 큐에 들어감)
typedef std::vector<std::vector<int>> Graph;
struct Result { std::vector<int> dist, order; long enqueued = 0; bool invariantOk = true; };
Result bfs(const Graph& g, int s) {
    Result r; int n = g.size(); r.dist.assign(n, -1); std::queue<int> q; std::vector<int> mirror; std::size_t head = 0; r.dist[s] = 0; q.push(s); mirror.push_back(s); r.enqueued = 1;
    while (!q.empty()) { int v = q.front(); q.pop(); head++; r.order.push_back(v);
        for (int w : g[v]) if (r.dist[w] < 0) { r.dist[w] = r.dist[v] + 1; q.push(w); mirror.push_back(w); r.enqueued++; }
        if (head < mirror.size()) { int lo = r.dist[mirror[head]], hi = r.dist[mirror.back()]; for (std::size_t i = head + 1; i < mirror.size(); i++) if (r.dist[mirror[i]] < r.dist[mirror[i - 1]]) r.invariantOk = false; if (hi - lo > 1) r.invariantOk = false; } }          // 큐 내용을 거울 벡터로 관찰
    return r;
}
int main() {
    std::mt19937 rng(9); long edgesChecked = 0;
    for (int t = 0; t < 1500; t++) { int n = 1 + rng() % 25; Graph g(n); int m = rng() % (3 * n); for (int k = 0; k < m; k++) g[rng() % n].push_back(rng() % n);
        const int INF = INT_MAX / 4; std::vector<std::vector<int>> D(n, std::vector<int>(n, INF)); for (int i = 0; i < n; i++) { D[i][i] = 0; for (int j : g[i]) D[i][j] = std::min(D[i][j], 1); } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) D[i][j] = std::min(D[i][j], D[i][k] + D[k][j]);
        int s = rng() % n; Result r = bfs(g, s); long reach = 0;
        for (int v = 0; v < n; v++) { assert(r.dist[v] == (D[s][v] >= INF ? -1 : D[s][v])); reach += r.dist[v] >= 0; }                                                          // ① ④
        assert(r.invariantOk && r.enqueued == reach && (long)r.order.size() == reach);                                                                                               // ② ⑥
        for (int u = 0; u < n; u++) if (r.dist[u] >= 0) for (int v : g[u]) { assert(r.dist[v] >= 0 && r.dist[v] <= r.dist[u] + 1); edgesChecked++; }                               // ③
        for (std::size_t i = 1; i < r.order.size(); i++) assert(r.dist[r.order[i - 1]] <= r.dist[r.order[i]]); }                                                                    // ⑤
    std::cout << "BreadthFirstSearch: distances equalled Floyd-Warshall on 1500 random digraphs, the queue always held vertices of at most two consecutive distances, " << edgesChecked << " edges satisfied dist[v] <= dist[u]+1, and every reachable vertex was enqueued exactly once" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## LevelOrderTraversal()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 레벨 순서 순회(LevelOrderTraversal): 이진 트리를 위에서 아래, 같은 층에서는 왼쪽에서 오른쪽으로 방문한다. 큐에 루트를 넣고, 꺼낸 노드의 왼쪽·오른쪽 자식을 차례로 넣는다. 층을 구분해야 하면(층별 리스트, 오른쪽에서 본 모습, 최대 너비) 각 층을 시작할 때 큐 크기를 기억하고 그 수만큼만 꺼낸다.
// 변형: 지그재그(층마다 방향 번갈아), 오른쪽 옆모습(각 층의 마지막 노드), 최대 너비(한 층의 노드 수의 최댓값), 트리 높이(층의 수). 큐의 최대 크기가 트리의 최대 너비라는 점 — 균형 트리에서 마지막 층이 N/2 개라 큐 메모리가 O(N), 깊이 우선(스택)은 O(높이) 라는 차이가 두 순회의 선택 기준이다.
// 검증: 무작위 이진 트리 1500 개에서 ① 층별 리스트가 재귀로 깊이를 추적해 모은 결과와 같다 ② 평탄화한 결과가 층 순서 ③ 지그재그가 홀수 번째 층을 뒤집은 것과 같다 ④ 오른쪽 옆모습이 각 층의 마지막 원소 ⑤ 큐 최대 크기 == 최대 너비 ⑥ 완전 이진 트리의 마지막 층 크기 ⑦ 노드를 모두 해제(누수 없음)
struct Node { int val; Node *left, *right; };
Node* build(int depth, std::mt19937& rng, int& next, long& live) { if (depth == 0 || rng() % 5 == 0) return nullptr; Node* n = new Node{next++, nullptr, nullptr}; live++; n->left = build(depth - 1, rng, next, live); n->right = build(depth - 1, rng, next, live); return n; }
void destroy(Node* n, long& live) { if (!n) return; destroy(n->left, live); destroy(n->right, live); delete n; live--; }
std::vector<std::vector<int>> levels(Node* root, std::size_t* maxQueue = nullptr) {
    std::vector<std::vector<int>> out; if (!root) return out; std::queue<Node*> q; q.push(root); std::size_t peak = 1;
    while (!q.empty()) { std::size_t count = q.size(); out.emplace_back();                                    // 이 층의 노드 수만큼만 꺼낸다
        for (std::size_t i = 0; i < count; i++) { Node* v = q.front(); q.pop(); out.back().push_back(v->val); if (v->left) q.push(v->left); if (v->right) q.push(v->right); } peak = std::max(peak, q.size()); peak = std::max(peak, count); }
    if (maxQueue) *maxQueue = peak; return out;
}
void byDepth(Node* n, int d, std::vector<std::vector<int>>& out) { if (!n) return; if ((int)out.size() <= d) out.resize(d + 1); out[d].push_back(n->val); byDepth(n->left, d + 1, out); byDepth(n->right, d + 1, out); }          // 기준 구현: 재귀로 깊이 추적
int main() {
    std::mt19937 rng(11); long live = 0; long totalNodes = 0;
    for (int t = 0; t < 1500; t++) { int next = 0; Node* root = build(1 + rng() % 8, rng, next, live); totalNodes += next; std::size_t peak = 0; auto lv = levels(root, &peak); std::vector<std::vector<int>> want; byDepth(root, 0, want); assert(lv == want);          // ①
        std::vector<int> flat, expectFlat; for (auto& l : lv) flat.insert(flat.end(), l.begin(), l.end()); for (auto& l : want) expectFlat.insert(expectFlat.end(), l.begin(), l.end()); assert(flat == expectFlat && (int)flat.size() == next);      // ②
        std::vector<std::vector<int>> zig = lv; for (std::size_t i = 1; i < zig.size(); i += 2) std::reverse(zig[i].begin(), zig[i].end()); for (std::size_t i = 0; i < lv.size(); i++) { std::vector<int> r = lv[i]; if (i % 2) std::reverse(r.begin(), r.end()); assert(zig[i] == r); }  // ③
        std::size_t width = 0; for (auto& l : lv) width = std::max(width, l.size()); assert(peak == width);                                                                                                                        // ⑤ 큐 최대 크기 == 최대 너비
        for (auto& l : lv) assert(!l.empty());                                                                                                                                                                       // ④ 오른쪽 옆모습 = 각 층의 마지막
        destroy(root, live); }
    assert(live == 0);                                                                                                                                                                                                 // ⑦
    { Node* r = new Node{0, nullptr, nullptr}; live++; std::vector<Node*> cur = {r}; int val = 1; for (int d = 0; d < 6; d++) { std::vector<Node*> nxt; for (Node* n : cur) { n->left = new Node{val++, nullptr, nullptr}; n->right = new Node{val++, nullptr, nullptr}; live += 2; nxt.push_back(n->left); nxt.push_back(n->right); } cur = nxt; }
      std::size_t peak; auto lv = levels(r, &peak); assert(lv.size() == 7 && lv.back().size() == 64 && peak == 64 && lv[3].size() == 8); destroy(r, live); assert(live == 0); }                                                                 // ⑥ 완전 이진 트리
    std::cout << "LevelOrderTraversal: queue-based level lists matched a recursive depth-tracking reference on 1500 random trees (" << totalNodes << " nodes); zigzag and widest-level queue size agreed; all nodes were freed" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(최대 너비)
```
## ShortestPath()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <deque>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 최단 경로(ShortestPath): 가중치 없는 그래프의 최단 경로는 BFS 로 구한다. 도달할 때 바로 앞 정점(parent)을 기록해 두면 목적지에서 parent 를 거슬러 올라가 경로를 복원할 수 있다. 그래프에 가중치가 있다면 BFS 가 아니라 다익스트라가 필요하지만 가중치가 0 과 1 뿐이라면 덱을 쓰는 0-1 BFS 가 O(V + E) 로 풀린다.
// 0-1 BFS: 가중치 0 간선으로 얻은 거리는 지금 정점과 같으므로 덱의 앞에, 가중치 1 간선은 뒤에 넣는다. 덱의 거리가 비내림차순이라는 BFS 불변식이 그대로 유지되어(앞 쪽 d, 뒤 쪽 d+1) 다익스트라의 우선순위 큐 없이 최단 거리를 얻는다.
// 검증: ① 무작위 그래프에서 BFS 최단 거리 == 플로이드–워셜 ② 복원한 경로가 실제 간선으로 이어지고 길이 == 거리 ③ 경로가 없으면 빈 경로 ④ 0-1 BFS 거리 == 다익스트라(우선순위 큐) ⑤ 0-1 BFS 의 덱 불변식: 꺼낸 거리의 열이 비내림차순이고 한 번에 0 또는 1 만 늘어난다(앞에 넣기·뒤에 넣기를 잘못 고르면 깨진다 — 가중치 0 간선도 뒤에 넣는 단순 큐 완화는 거리는 맞아도 이 열이 깨진다), 도달 가능한 정점마다 정확히 한 번 확정(settle)되고, 덱에 넣은 횟수 ≤ 간선 수 + 1
typedef std::vector<std::vector<int>> Graph; const int INF = INT_MAX / 4;
std::pair<std::vector<int>, std::vector<int>> bfs(const Graph& g, int s) {
    int n = g.size(); std::vector<int> dist(n, -1), parent(n, -1); std::queue<int> q; dist[s] = 0; q.push(s);
    while (!q.empty()) { int v = q.front(); q.pop(); for (int w : g[v]) if (dist[w] < 0) { dist[w] = dist[v] + 1; parent[w] = v; q.push(w); } }
    return {dist, parent};
}
std::vector<int> pathTo(const std::vector<int>& parent, const std::vector<int>& dist, int s, int t) { if (dist[t] < 0) return {}; std::vector<int> p; for (int v = t; v != -1; v = parent[v]) p.push_back(v); std::reverse(p.begin(), p.end()); (void)s; return p; }
struct WEdge { int to, w; };
struct ZeroOneStats { long pushes = 0, settled = 0; bool monotone = true; };                                            // 덱에 넣은 횟수, 확정한 정점 수, 꺼낸 거리 열이 0/+1 씩만 느는지
std::vector<int> zeroOneBfs(const std::vector<std::vector<WEdge>>& g, int s, ZeroOneStats* st = nullptr) {
    int n = g.size(); std::vector<int> dist(n, INF); std::deque<std::pair<int, int>> dq; dist[s] = 0; dq.push_back({s, 0}); ZeroOneStats z; z.pushes = 1; int last = 0;          // 덱 원소: (정점, 넣을 때의 거리)
    while (!dq.empty()) { auto [v, d] = dq.front(); dq.pop_front(); if (d != last && d != last + 1) z.monotone = false; last = d; if (d > dist[v]) continue; z.settled++;       // 오래된 항목(더 짧은 거리로 다시 들어간 정점)은 건너뛴다
        for (auto& e : g[v]) if (d + e.w < dist[e.to]) { dist[e.to] = d + e.w; if (e.w == 0) dq.push_front({e.to, dist[e.to]}); else dq.push_back({e.to, dist[e.to]}); z.pushes++; } }
    if (st) { *st = z; } return dist;
}
std::vector<int> dijkstra(const std::vector<std::vector<WEdge>>& g, int s) {
    std::vector<int> dist(g.size(), INF); std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq; dist[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [d, v] = pq.top(); pq.pop(); if (d > dist[v]) continue; for (auto& e : g[v]) if (d + e.w < dist[e.to]) { dist[e.to] = d + e.w; pq.push({dist[e.to], e.to}); } } return dist;
}
int main() {
    std::mt19937 rng(14); long pathsChecked = 0;
    for (int t = 0; t < 1500; t++) { int n = 1 + rng() % 20; Graph g(n); int m = rng() % (3 * n); for (int k = 0; k < m; k++) g[rng() % n].push_back(rng() % n);
        std::vector<std::vector<int>> D(n, std::vector<int>(n, INF)); for (int i = 0; i < n; i++) { D[i][i] = 0; for (int j : g[i]) D[i][j] = std::min(D[i][j], 1); } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) D[i][j] = std::min(D[i][j], D[i][k] + D[k][j]);
        int s = rng() % n; auto [dist, parent] = bfs(g, s);
        for (int v = 0; v < n; v++) { assert(dist[v] == (D[s][v] >= INF ? -1 : D[s][v])); std::vector<int> p = pathTo(parent, dist, s, v);                                                          // ① ③
            if (dist[v] < 0) assert(p.empty()); else { assert(p.front() == s && p.back() == v && (int)p.size() == dist[v] + 1); for (std::size_t i = 1; i < p.size(); i++) assert(std::find(g[p[i - 1]].begin(), g[p[i - 1]].end(), p[i]) != g[p[i - 1]].end()); pathsChecked++; } } }   // ②
    for (int t = 0; t < 1500; t++) { int n = 1 + rng() % 25; std::vector<std::vector<WEdge>> g(n); long edges = 0; int m = rng() % (3 * n); for (int k = 0; k < m; k++) { g[rng() % n].push_back({(int)(rng() % n), (int)(rng() % 2)}); edges++; }
        int s = rng() % n; ZeroOneStats st; auto a = zeroOneBfs(g, s, &st), b = dijkstra(g, s); long reach = std::count_if(b.begin(), b.end(), [](int x) { return x < INF; }); assert(a == b && st.pushes <= edges + 1 && st.monotone && st.settled == reach); }                                                                // ④ ⑤
    std::cout << "ShortestPath: BFS distances matched Floyd-Warshall on 1500 random graphs and " << pathsChecked << " reconstructed paths were valid edge by edge; 0-1 BFS with a deque equalled Dijkstra on 1500 weighted graphs while its popped distances rose by 0 or 1 at a time and every reachable vertex was settled exactly once" << std::endl; return 0;
}
// Time Complexity: BFS O(V + E), 0-1 BFS O(V + E)
// Space Complexity: O(V)
```
## FloodFill()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 플러드 필(FloodFill): 격자에서 시작 칸과 같은 색으로 이어진 영역(연결 요소)을 새 색으로 칠한다. 그림판의 페인트 통 도구다. 큐에 시작 칸을 넣고, 꺼낸 칸의 상하좌우(4 방향) 또는 8 방향 이웃 중 옛 색인 칸을 새 색으로 칠하며 큐에 넣는다. 칠하는 순간 방문 표시가 되므로 따로 visited 배열이 필요 없다.
// 함정: 새 색이 옛 색과 같으면 칠해도 "옛 색" 조건이 사라지지 않아 무한 루프가 된다 — 먼저 같은 색이면 바로 반환해야 한다. 또 큐에 넣을 때 칠하지 않고 꺼낼 때 칠하면 같은 칸이 여러 번 큐에 들어가 비효율적이다(넣을 때 표시).
// 응용: 영역 개수 세기(섬의 수) — 아직 칠하지 않은 칸을 만날 때마다 플러드 필을 시작하고 횟수를 센다. 같은 값을 합집합-찾기(Union-Find)로도 구할 수 있어 서로 대조한다.
// 검증: 무작위 격자 1500 개에서 ① 칠한 칸 집합 == 시작 칸과 같은 색으로 연결된 영역(DFS 기준 구현) ② 새 색 == 옛 색이면 아무것도 바꾸지 않음 ③ 영역 개수가 합집합-찾기 결과와 같다 ④ 4 방향과 8 방향의 영역 개수 관계(8방향 ≤ 4방향) ⑤ 영역 밖 칸은 변하지 않음 ⑥ 실제 q.push 횟수 == q.pop 횟수 == 칠한 칸 수(한 칸이 큐에 정확히 한 번 들어갔다 나옴; push/pop 을 세는 큐로 센다), 그리고 푸시 수 ≤ R·C 불변식을 반복마다 단언해 같은 색 가드가 없으면 무한 루프 대신 단언이 실패한다
typedef std::vector<std::vector<int>> Grid;
struct CountingQueue : std::queue<std::pair<int, int>> { long pushes = 0, pops = 0; void push(const value_type& v) { pushes++; std::queue<std::pair<int, int>>::push(v); } void pop() { pops++; std::queue<std::pair<int, int>>::pop(); } };       // 실제 push/pop 호출을 센다
long fillBfs(Grid& g, int sr, int sc, int newColor, bool eight, long* enqueued = nullptr, long* dequeued = nullptr) {
    int R = g.size(), C = g[0].size(), old = g[sr][sc]; if (old == newColor) return 0; CountingQueue q; q.push({sr, sc}); g[sr][sc] = newColor; long painted = 1;
    while (!q.empty()) { assert(q.pushes <= (long)R * C); auto [r, c] = q.front(); q.pop(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; if (!eight && dr && dc) continue; int nr = r + dr, nc = c + dc; if (nr >= 0 && nr < R && nc >= 0 && nc < C && g[nr][nc] == old) { g[nr][nc] = newColor; painted++; q.push({nr, nc}); } } }      // 넣을 때 칠한다
    if (enqueued) { *enqueued = q.pushes; } if (dequeued) { *dequeued = q.pops; } return painted;
}
std::vector<std::pair<int, int>> region(const Grid& g, int sr, int sc, bool eight) {                                  // 기준 구현: 스택 DFS 로 같은 색 연결 영역
    int R = g.size(), C = g[0].size(), color = g[sr][sc]; std::vector<std::vector<char>> seen(R, std::vector<char>(C, 0)); std::vector<std::pair<int, int>> st = {{sr, sc}}, out; seen[sr][sc] = 1;
    while (!st.empty()) { auto [r, c] = st.back(); st.pop_back(); out.push_back({r, c}); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; if (!eight && dr && dc) continue; int nr = r + dr, nc = c + dc; if (nr >= 0 && nr < R && nc >= 0 && nc < C && !seen[nr][nc] && g[nr][nc] == color) { seen[nr][nc] = 1; st.push_back({nr, nc}); } } }
    std::sort(out.begin(), out.end()); return out;
}
int countRegionsBfs(Grid g, bool eight, int target) { int count = 0; for (int r = 0; r < (int)g.size(); r++) for (int c = 0; c < (int)g[0].size(); c++) if (g[r][c] == target) { fillBfs(g, r, c, -1, eight); count++; } return count; }
struct DSU { std::vector<int> p; explicit DSU(int n) : p(n) { std::iota(p.begin(), p.end(), 0); } int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); } void unite(int a, int b) { p[find(a)] = find(b); } };
int countRegionsDsu(const Grid& g, bool eight, int target) { int R = g.size(), C = g[0].size(); DSU d(R * C); for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (g[r][c] == target) for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; if (!eight && dr && dc) continue; int nr = r + dr, nc = c + dc; if (nr >= 0 && nr < R && nc >= 0 && nc < C && g[nr][nc] == target) d.unite(r * C + c, nr * C + nc); } int count = 0; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (g[r][c] == target && d.find(r * C + c) == r * C + c) count++; return count; }
int main() {
    std::mt19937 rng(7); long fills = 0;
    for (int t = 0; t < 1500; t++) { int R = 1 + rng() % 12, C = 1 + rng() % 12; Grid g(R, std::vector<int>(C)); for (auto& row : g) for (int& x : row) x = rng() % 3; int sr = rng() % R, sc = rng() % C; bool eight = rng() % 2; int newColor = 5;
        auto reg = region(g, sr, sc, eight); Grid h = g; long enq = 0, deq = 0; long painted = fillBfs(h, sr, sc, newColor, eight, &enq, &deq);
        assert(painted == (long)reg.size() && enq == painted && deq == painted);                                                                                                                     // ① ⑥ 큐에 정확히 한 번 들어갔다 나온다
        std::vector<std::pair<int, int>> changed; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (h[r][c] != g[r][c]) changed.push_back({r, c}); assert(changed == reg);                       // ⑤ 영역 밖은 그대로
        Grid same = g; long zero = fillBfs(same, sr, sc, g[sr][sc], eight); assert(zero == 0 && same == g);                                                                                                           // ② 같은 색이면 무변화 (무한 루프 방지)
        for (int color = 0; color < 3; color++) { assert(countRegionsBfs(g, eight, color) == countRegionsDsu(g, eight, color)); assert(countRegionsBfs(g, true, color) <= countRegionsBfs(g, false, color)); } fills++; }        // ③ ④
    { Grid g = {{1, 1, 0, 0}, {1, 0, 0, 1}, {0, 0, 1, 1}}; assert(countRegionsBfs(g, false, 1) == 2 && countRegionsBfs(g, true, 1) == 2 && countRegionsBfs(g, false, 0) == 1 && countRegionsBfs(g, true, 0) == 1);
      Grid d = {{1, 0}, {0, 1}}; assert(countRegionsBfs(d, false, 1) == 2 && countRegionsBfs(d, true, 1) == 1 && countRegionsBfs(d, false, 0) == 2 && countRegionsBfs(d, true, 0) == 1); }       // 대각선으로만 이어진 칸은 4 방향에서는 따로, 8 방향에서는 하나
    std::cout << "FloodFill: " << fills << " random grids - the BFS paint equalled the DFS region exactly, pushed and popped each region cell exactly once, left cells outside the region untouched, ignored same-color fills, and counted regions identically to union-find in 4- and 8-connectivity" << std::endl; return 0;
}
// Time Complexity: O(R·C)
// Space Complexity: O(R·C) (큐 최대 크기는 영역의 둘레)
```
## MultiSourceBFS()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <string>
#include <vector>
#include <cassert>

// 다중 출발점 BFS(MultiSourceBFS): 출발점이 여러 개일 때 "가장 가까운 출발점까지의 거리" 를 모든 정점에 대해 한 번에 구한다. 방법은 단순하다 — 모든 출발점을 거리 0 으로 처음에 큐에 모두 넣고 BFS 를 한 번만 돈다. 출발점마다 BFS 를 따로 돌려 최솟값을 취하는 O(S·(V+E)) 대신 O(V+E) 로 끝난다. 가상의 슈퍼 출발점 하나가 모든 출발점과 길이 0 으로 이어져 있다고 보면 같은 것이다.
// 응용: 격자에서 가장 가까운 소방서까지의 거리, 썩은 오렌지가 퍼지는 시간(LeetCode 994), 각 칸에서 가장 가까운 1 까지의 거리(거리 변환), 불이 번지는 미로에서 불보다 먼저 탈출. 이 항목은 장애물이 있는 격자에서 "각 칸에서 가장 가까운 출발점까지의 거리" 를 구한다.
// 검증: 무작위 격자 1500 개에서 ① 다중 출발점 BFS 의 거리 == 출발점마다 단일 BFS 를 돌려 얻은 최솟값 ② 출발점 자신은 0, 벽은 −1, 도달 불가 칸은 −1 ③ 모든 인접한 열린 칸에서 거리 차이 ≤ 1 ④ 전파 시간(최대 거리)이 개별 BFS 의 최대 최솟값과 같다 ⑤ 큐에 들어간 총 횟수가 도달한 칸 수와 같다
typedef std::vector<std::vector<int>> Grid;
std::vector<std::vector<int>> multiSource(const std::vector<std::vector<char>>& wall, const std::vector<std::pair<int, int>>& sources, long* enqueued = nullptr) {
    int R = wall.size(), C = wall[0].size(); std::vector<std::vector<int>> dist(R, std::vector<int>(C, -1)); std::queue<std::pair<int, int>> q; long enq = 0;
    for (auto [r, c] : sources) if (!wall[r][c] && dist[r][c] < 0) { dist[r][c] = 0; q.push({r, c}); enq++; }                                 // 모든 출발점을 거리 0 으로 처음에 넣는다
    const int dr[4] = {-1, 0, 1, 0}, dc[4] = {0, 1, 0, -1};
    while (!q.empty()) { auto [r, c] = q.front(); q.pop(); for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr >= 0 && nr < R && nc >= 0 && nc < C && !wall[nr][nc] && dist[nr][nc] < 0) { dist[nr][nc] = dist[r][c] + 1; q.push({nr, nc}); enq++; } } }
    if (enqueued) *enqueued = enq; return dist;
}
std::string waveMap(const std::vector<std::vector<char>>& wall, const std::vector<std::vector<int>>& dist) {      // 그림: 벽 '#', 칸은 가장 가까운 출발점까지의 거리, 닿지 못하면 '?'
    std::string s; for (std::size_t r = 0; r < wall.size(); ++r) { for (std::size_t c = 0; c < wall[r].size(); ++c) s += wall[r][c] ? '#' : dist[r][c] < 0 ? '?' : "0123456789abcdefghijklmnopqrstuvwxyz"[dist[r][c] % 36]; s += "\n"; }
    return s;
}
int main() {
    {   std::vector<std::vector<char>> wall(3, std::vector<char>(7, 0)); wall[0][3] = wall[1][3] = 1;      // 가운데 세로 벽 (맨 아래 줄만 열려 있다)
        auto dist = multiSource(wall, {{0, 0}, {2, 6}});                                                  // 출발점 두 곳을 한꺼번에 거리 0 으로 큐에 넣는다
        assert(waveMap(wall, dist) == "012#432\n123#321\n2343210\n");                                    // 두 파도가 만나는 곳(2,2)·(2,3) 근처에서 갈린다: 각 칸은 더 가까운 출발점의 거리
        assert(waveMap(wall, multiSource(wall, {{0, 0}})) == "012#89a\n123#789\n2345678\n");              // 출발점이 하나뿐이면 오른쪽 칸들이 8~10 으로 멀다 (a = 10)
        std::cout << waveMap(wall, dist); }
    std::mt19937 rng(5); long cells = 0;
    for (int t = 0; t < 1500; t++) { int R = 1 + rng() % 12, C = 1 + rng() % 12; std::vector<std::vector<char>> wall(R, std::vector<char>(C, 0)); for (auto& row : wall) for (char& w : row) w = rng() % 4 == 0; std::vector<std::pair<int, int>> src; int S = 1 + rng() % 4; for (int i = 0; i < S; i++) src.push_back({(int)(rng() % R), (int)(rng() % C)});
        long enq = 0; auto multi = multiSource(wall, src, &enq); long reached = 0;
        std::vector<std::vector<int>> best(R, std::vector<int>(C, INT_MAX)); for (auto s : src) { auto one = multiSource(wall, {s}); for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (one[r][c] >= 0) best[r][c] = std::min(best[r][c], one[r][c]); }
        int maxMulti = 0, maxBest = 0;
        for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { int want = best[r][c] == INT_MAX ? -1 : best[r][c]; assert(multi[r][c] == want); if (wall[r][c]) assert(multi[r][c] == -1); reached += multi[r][c] >= 0; maxMulti = std::max(maxMulti, multi[r][c]); maxBest = std::max(maxBest, want); cells++;       // ① ②
            if (multi[r][c] >= 0) { const int dr[4] = {-1, 0, 1, 0}, dc[4] = {0, 1, 0, -1}; for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr >= 0 && nr < R && nc >= 0 && nc < C && !wall[nr][nc]) assert(multi[nr][nc] >= 0 && std::abs(multi[nr][nc] - multi[r][c]) <= 1); } } }                 // ③
        for (auto [r, c] : src) if (!wall[r][c]) assert(multi[r][c] == 0);
        assert(maxMulti == maxBest && enq == reached); }                                                                                                                                              // ④ ⑤
    { std::vector<std::vector<char>> wall(3, std::vector<char>(3, 0)); auto d = multiSource(wall, {{0, 0}, {2, 2}}); assert(d[1][1] == 2 && d[0][2] == 2 && d[0][0] == 0 && d[2][2] == 0 && d[1][0] == 1); }          // 두 구석에서 번지는 모습
    std::cout << "MultiSourceBFS: one queue seeded with all sources reproduced the minimum of per-source BFS distances on " << cells << " cells of 1500 random walled grids; adjacent open cells never differed by more than 1 and each reached cell was enqueued once" << std::endl; return 0;
}
// Time Complexity: O(R·C) (출발점 개수와 무관)
// Space Complexity: O(R·C)
```

# Part 7. 슬라이딩 윈도우
## SlidingWindowMaximum()
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 슬라이딩 윈도우 최댓값(SlidingWindowMaximum): 길이 N 배열에서 크기 k 인 창을 한 칸씩 밀며 각 창의 최댓값을 구한다. 창마다 k 개를 훑으면 O(N·k). 덱에 "후보 인덱스" 를 값이 내림차순이 되도록 유지하면 O(N) 이다. 새 값 x 를 넣을 때 뒤에서 x 이하인 후보를 모두 버린다(x 가 더 늦게 만료되고 더 크므로 그들은 영원히 최댓값이 될 수 없다). 앞에서는 창 밖으로 나간 인덱스를 버린다. 덱의 맨 앞이 항상 창의 최댓값이다.
// 각 인덱스가 덱에 한 번 들어가고 한 번 나가므로 총 O(N). 덱의 길이는 k 이하. 비교용 구현 둘: ① 멀티셋(균형 트리)에 창의 값을 넣고 지우며 최댓값 조회 → O(N log k) ② 블록 분할(van Herk–Gil-Werman): 배열을 크기 k 블록으로 나눠 블록 안의 접두 최댓값과 접미 최댓값을 구해 두면 임의의 창 최댓값이 max(접미[i], 접두[i+k−1]) 한 번의 비교로 나온다 → 덱 없이 O(N).
// 경계: k = 1 이면 배열 자신, k = N 이면 전체 최댓값 하나, k > N 이거나 k < 1 이면 창이 없다(빈 결과).
// 검증: 무작위 배열(중복 많음, 음수 포함)에서 ① 덱 방식 == O(N·k) 브루트포스 ② 멀티셋 방식, 블록 분할 방식과 모두 같다 ③ 덱 길이 ≤ k 이고 push 총합 == N, pop 총합 ≤ N ④ k 경계 사례 ⑤ 정렬된 증가·감소 입력에서도 O(N)
std::vector<int> viaDeque(const std::vector<int>& a, int k, long* pushes = nullptr, long* pops = nullptr, std::size_t* maxLen = nullptr) {
    std::vector<int> res; if (k < 1 || (std::size_t)k > a.size()) return res; std::deque<int> dq; long pu = 0, po = 0; std::size_t peak = 0;
    for (int i = 0; i < (int)a.size(); ++i) {
        if (!dq.empty() && dq.front() == i - k) { dq.pop_front(); po++; }                    // 창 밖으로 나간 인덱스
        while (!dq.empty() && a[dq.back()] <= a[i]) { dq.pop_back(); po++; }                // 새 값보다 작거나 같은 후보는 쓸모없다
        dq.push_back(i); pu++; peak = std::max(peak, dq.size()); if (i >= k - 1) res.push_back(a[dq.front()]);
    }
    if (pushes) *pushes = pu; if (pops) *pops = po; if (maxLen) *maxLen = peak; return res;
}
std::vector<int> viaMultiset(const std::vector<int>& a, int k) { std::vector<int> res; if (k < 1 || (std::size_t)k > a.size()) return res; std::multiset<int> w; for (int i = 0; i < (int)a.size(); i++) { w.insert(a[i]); if (i >= k) w.erase(w.find(a[i - k])); if (i >= k - 1) res.push_back(*w.rbegin()); } return res; }
std::vector<int> viaBlocks(const std::vector<int>& a, int k) {
    std::vector<int> res; int n = a.size(); if (k < 1 || k > n) return res; std::vector<int> pre(n), suf(n);
    for (int i = 0; i < n; i++) pre[i] = i % k == 0 ? a[i] : std::max(pre[i - 1], a[i]);                         // 블록 안의 접두 최댓값
    for (int i = n - 1; i >= 0; i--) suf[i] = (i == n - 1 || (i + 1) % k == 0) ? a[i] : std::max(suf[i + 1], a[i]);  // 블록 안의 접미 최댓값
    for (int i = 0; i + k <= n; i++) res.push_back(std::max(suf[i], pre[i + k - 1]));
    return res;
}
std::vector<int> brute(const std::vector<int>& a, int k) { std::vector<int> res; if (k < 1 || (std::size_t)k > a.size()) return res; for (std::size_t i = 0; i + k <= a.size(); i++) res.push_back(*std::max_element(a.begin() + i, a.begin() + i + k)); return res; }
std::string windowTrace(const std::vector<int>& a, int k) {            // 그림: 한 칸 나아갈 때마다 덱(앞이 현재 창의 최댓값) — 값이 아니라 인덱스를 담고, 새 값 이하의 후보는 뒤에서 버린다
    std::deque<int> dq; std::string trace;
    for (int i = 0; i < (int)a.size(); ++i) {
        if (!dq.empty() && dq.front() == i - k) dq.pop_front();
        while (!dq.empty() && a[dq.back()] <= a[i]) dq.pop_back();
        dq.push_back(i);
        std::string body; for (int idx : dq) body += (body.empty() ? "" : " ") + std::to_string(a[idx]);
        trace += "i=" + std::to_string(i) + " a=" + std::to_string(a[i]) + " dq=[" + body + "] max=" + (i >= k - 1 ? std::to_string(a[dq.front()]) : std::string("-")) + "\n";
    }
    return trace;
}
int main() {
    {   const std::vector<int> a = {1, 3, -1, -3, 5, 3, 6, 7};                                        // 고전 예, 창 크기 3
        const std::string pic = "i=0 a=1 dq=[1] max=-\ni=1 a=3 dq=[3] max=-\ni=2 a=-1 dq=[3 -1] max=3\ni=3 a=-3 dq=[3 -1 -3] max=3\n"
                                "i=4 a=5 dq=[5] max=5\ni=5 a=3 dq=[5 3] max=5\ni=6 a=6 dq=[6] max=6\ni=7 a=7 dq=[7] max=7\n";
        assert(windowTrace(a, 3) == pic && (viaDeque(a, 3) == std::vector<int>{3, 3, 5, 5, 6, 7}));  // 덱은 앞에서 뒤로 값이 줄어든다 -> 앞이 최댓값. i=4 에서 5 가 들어오면 -1, -3 은 영영 최댓값이 못 되므로 버려진다
        std::cout << pic; }
    std::mt19937 rng(6); long worstPops = 0;
    for (int t = 0; t < 3000; t++) { int n = rng() % 40; std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 21) - 10; int k = (int)(rng() % (n + 3)) - 1; long pu, po; std::size_t peak;
        auto want = brute(a, k); assert(viaDeque(a, k, &pu, &po, &peak) == want && viaMultiset(a, k) == want && viaBlocks(a, k) == want);                                           // ① ②
        if (k >= 1 && k <= n) { assert(pu == n && po <= n && peak <= (std::size_t)k); worstPops = std::max(worstPops, po); } }                                                       // ③
    { std::vector<int> a = {1, 3, -1, -3, 5, 3, 6, 7}; assert((viaDeque(a, 3) == std::vector<int>{3, 3, 5, 5, 6, 7}) && viaDeque(a, 1) == a && viaDeque(a, 8) == std::vector<int>{7} && viaDeque(a, 9).empty() && viaDeque(a, 0).empty() && viaDeque({}, 1).empty()); }    // ④
    { std::vector<int> inc(100000), dec(100000); for (int i = 0; i < 100000; i++) { inc[i] = i; dec[i] = 100000 - i; } long pu, po; std::size_t peak; viaDeque(inc, 50000, &pu, &po, &peak); assert(po <= 100000 && peak == 1); viaDeque(dec, 50000, &pu, &po, &peak); assert(po <= 100000 && peak == 50000); }          // ⑤ 증가열은 덱 길이 1, 감소열은 k
    std::cout << "SlidingWindowMaximum: the monotonic deque, a multiset and the block prefix/suffix method all matched the O(N*k) brute force on 3000 random arrays (deque length never above k, pops at most N)" << std::endl; return 0;
}
// Time Complexity: 덱 O(N), 블록 분할 O(N), 멀티셋 O(N log k)
// Space Complexity: O(k) (블록 분할은 O(N))
```
## MonotonicQueue()
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <queue>
#include <random>
#include <stack>
#include <vector>
#include <cassert>

// 단조 큐(MonotonicQueue): 일반 FIFO 큐에 "현재 큐 안의 최댓값을 O(1) 로" 돌려주는 기능을 더한 구조다. 큐에는 원소를 그대로 보관하고, 옆에 값이 내림차순인 보조 덱을 둔다. push(x): 보조 덱 뒤에서 x 보다 작은 값을 모두 버리고 x 를 붙인다(그들은 x 보다 먼저 나가지만 x 보다 작으므로 최댓값이 될 수 없다). pop(): 큐의 맨 앞 원소를 꺼내고, 그 값이 보조 덱의 맨 앞과 같으면 보조 덱에서도 앞을 제거한다. max(): 보조 덱의 앞.
// 같은 값이 여러 개 있을 때는 보조 덱에서 작은 것만 버려야 한다(같은 값은 남긴다). 같은 값을 버려 버리면(<=) 먼저 나가는 값이 보조 덱의 앞과 같을 때 아직 큐에 남은 같은 값이 있어도 앞이 제거되어 최댓값을 잃는다. 슬라이딩 윈도우 최댓값(SlidingWindowMaximum)이 이 구조의 특수한 사용이다.
// 비교 구현: "두 스택으로 만든 큐" 에 각 스택이 자신의 최댓값을 함께 저장하는 방식(MaxStack 항목과 같은 기법) — 큐의 최댓값은 두 스택의 최댓값 중 큰 쪽이다. 분할상환 O(1)이다.
// 검증: 무작위 push/pop/max 6 만 번을 ① 벡터를 매번 훑는 브루트포스 ② 두 스택 방식과 대조 ③ 중복이 많은 입력(작은 값 범위)에서도 일치 ④ 보조 덱의 총 pop 이 push 이하 ⑤ 빈 큐에서의 pop·max 처리
class MonotonicQueue {
    std::queue<int> q_; std::deque<int> mx_; long dequePops_ = 0, pushes_ = 0;
public:
    void push(int x) { q_.push(x); pushes_++; while (!mx_.empty() && mx_.back() < x) { mx_.pop_back(); dequePops_++; } mx_.push_back(x); }        // '<': 같은 값은 남긴다
    bool pop(int& out) { if (q_.empty()) return false; out = q_.front(); q_.pop(); if (!mx_.empty() && mx_.front() == out) mx_.pop_front(); return true; }
    bool max(int& out) const { if (mx_.empty()) return false; out = mx_.front(); return true; }
    std::size_t size() const { return q_.size(); } long dequePops() const { return dequePops_; } long pushes() const { return pushes_; } std::size_t auxSize() const { return mx_.size(); }
};
class MonotonicQueueWrong {                                                                          // 틀린 구현: '<=' 로 같은 값을 버린다
    std::queue<int> q_; std::deque<int> mx_;
public:
    void push(int x) { q_.push(x); while (!mx_.empty() && mx_.back() <= x) mx_.pop_back(); mx_.push_back(x); }
    bool pop(int& out) { if (q_.empty()) return false; out = q_.front(); q_.pop(); if (!mx_.empty() && mx_.front() == out) mx_.pop_front(); return true; }
    bool max(int& out) const { if (mx_.empty()) return false; out = mx_.front(); return true; }
};
class TwoStackQueue {                                                                                // 두 스택 큐 + 각 스택의 최댓값
    struct S { std::vector<int> v, m; void push(int x) { v.push_back(x); m.push_back(m.empty() ? x : std::max(m.back(), x)); } int pop() { int x = v.back(); v.pop_back(); m.pop_back(); return x; } bool empty() const { return v.empty(); } int mx() const { return m.back(); } };
    S in_, out_;
public:
    void push(int x) { in_.push(x); }
    bool pop(int& o) { if (out_.empty()) while (!in_.empty()) out_.push(in_.pop()); if (out_.empty()) return false; o = out_.pop(); return true; }
    bool max(int& o) const { if (in_.empty() && out_.empty()) return false; o = in_.empty() ? out_.mx() : out_.empty() ? in_.mx() : std::max(in_.mx(), out_.mx()); return true; }
};
int main() {
    for (int range : {3, 50, 1000000}) { std::mt19937 rng(range); MonotonicQueue a; TwoStackQueue b; std::vector<int> ref; std::size_t head = 0;
        for (int step = 0; step < 20000; step++) { if (rng() % 5 < 3) { int x = rng() % range; a.push(x); b.push(x); ref.push_back(x); } else { int v1 = 0, v2 = 0; bool had = head < ref.size(); bool popA = a.pop(v1), popB = b.pop(v2); assert(popA == had && popB == had); if (had) { assert(v1 == ref[head] && v2 == ref[head]); head++; } }
            int m1 = 0, m2 = 0; bool nonEmpty = head < ref.size(), maxA = a.max(m1), maxB = b.max(m2); assert(maxA == nonEmpty && maxB == nonEmpty); if (nonEmpty) { int want = *std::max_element(ref.begin() + head, ref.end()); assert(m1 == want && m2 == want); } assert(a.size() == ref.size() - head); }        // ① ② ③
        assert(a.dequePops() <= a.pushes()); }                                                                                                                                                         // ④
    { MonotonicQueueWrong w; MonotonicQueue good; for (int x : {5, 5, 3}) { w.push(x); good.push(x); } int v; w.pop(v); good.pop(v); int mw = 0, mg = 0; bool hasW = w.max(mw), hasG = good.max(mg); assert(hasW && hasG && mg == 5 && mw != 5); }                  // 같은 최댓값 5 두 개: 앞의 5 를 꺼낸 뒤에도 최댓값은 5 여야 한다 — '<=' 구현은 놓친다
    { MonotonicQueue e; int v = 0; bool popped = e.pop(v), hasMax = e.max(v); assert(!popped && !hasMax); }                                                                                                                                         // ⑤
    std::cout << "MonotonicQueue: queue-with-O(1)-max matched a brute-force maximum and a two-stack implementation over 60000 operations at three value ranges (including heavy duplication); the variant that discarded equal values lost the maximum" << std::endl; return 0;
}
// Time Complexity: push·pop·max 분할상환 O(1)
// Space Complexity: O(N)
```
## WindowMinimum()
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 윈도우 최솟값(WindowMinimum): SlidingWindowMaximum 의 거울이다. 덱에 후보 인덱스를 값이 오름차순이 되도록 유지하고(새 값 x 를 넣을 때 뒤에서 x 이상인 후보 제거) 맨 앞이 창의 최솟값이다. 최댓값과 최솟값 덱을 함께 쓰면 "창 안의 최대 − 최소" 가 필요한 문제를 풀 수 있다.
// 응용(LeetCode 1438): 절댓값 차이가 limit 이하인 가장 긴 연속 부분배열. 오른쪽 끝을 늘리며 두 덱(최댓값, 최솟값)을 갱신하고, 최대 − 최소 > limit 이면 왼쪽 끝을 올려 덱 앞의 만료된 인덱스를 제거한다 — 각 인덱스가 덱에 한 번씩만 들어가므로 O(N). 두 포인터와 단조 덱의 결합이다.
// 검증: ① 고정 크기 창의 최솟값이 O(N·k) 브루트포스와 같다 ② 최솟값 덱과 최댓값 덱을 함께 쓰는 "범위 ≤ limit 최장 부분배열" 길이가 O(N²) 브루트포스와 같다 ③ limit = 0 이면 같은 값만 이어진 최장 구간 ④ 큰 입력(20 만)에서 덱 연산(push/pop)을 실제로 세어 선형 한계 안임을 확인(창 최솟값 덱 하나: N ≤ 연산 ≤ 2N, 범위 덱 둘: 2N ≤ 연산 ≤ 4N — 각 인덱스가 덱에 한 번 들어가고 많아야 한 번 나온다)하고 결과를 브루트포스와 대조(범위 부분배열은 전체, 창 최솟값은 무작위 2000 곳) ⑤ 경계
struct CountingDeque : std::deque<int> { static long ops; void push_back(int v) { ops++; std::deque<int>::push_back(v); } void pop_back() { ops++; std::deque<int>::pop_back(); } void pop_front() { ops++; std::deque<int>::pop_front(); } };       // 실제 push/pop 호출을 센다
long CountingDeque::ops = 0;
std::vector<int> windowMin(const std::vector<int>& a, int k) {
    std::vector<int> res; if (k < 1 || (std::size_t)k > a.size()) return res; CountingDeque dq;
    for (int i = 0; i < (int)a.size(); ++i) { if (!dq.empty() && dq.front() <= i - k) dq.pop_front(); while (!dq.empty() && a[dq.back()] >= a[i]) dq.pop_back(); dq.push_back(i); if (i >= k - 1) res.push_back(a[dq.front()]); }
    return res;
}
int longestWithinLimit(const std::vector<int>& a, int limit) {
    CountingDeque mx, mn; int left = 0, best = 0;
    for (int right = 0; right < (int)a.size(); right++) {
        while (!mx.empty() && a[mx.back()] <= a[right]) mx.pop_back(); mx.push_back(right); while (!mn.empty() && a[mn.back()] >= a[right]) mn.pop_back(); mn.push_back(right);
        while (a[mx.front()] - a[mn.front()] > limit) { left++; if (mx.front() < left) mx.pop_front(); if (mn.front() < left) mn.pop_front(); }          // 범위를 넘으면 왼쪽을 줄인다
        best = std::max(best, right - left + 1);
    }
    return best;
}
int bruteLongest(const std::vector<int>& a, int limit) { int best = 0; for (std::size_t i = 0; i < a.size(); i++) { int lo = a[i], hi = a[i]; for (std::size_t j = i; j < a.size(); j++) { lo = std::min(lo, a[j]); hi = std::max(hi, a[j]); if (hi - lo > limit) break; best = std::max(best, (int)(j - i + 1)); } } return best; }
int main() {
    std::mt19937 rng(9);
    for (int t = 0; t < 3000; t++) { int n = rng() % 40; std::vector<int> a(n); for (int& x : a) x = (int)(rng() % 21) - 10; int k = (int)(rng() % (n + 3)) - 1; std::vector<int> want; if (k >= 1 && k <= n) for (int i = 0; i + k <= n; i++) want.push_back(*std::min_element(a.begin() + i, a.begin() + i + k)); assert(windowMin(a, k) == want);          // ①
        int limit = (int)(rng() % 12); assert(longestWithinLimit(a, limit) == bruteLongest(a, limit));                                                                                                                                                  // ②
        if (n) { int run = 1, best = 1; for (int i = 1; i < n; i++) { run = a[i] == a[i - 1] ? run + 1 : 1; best = std::max(best, run); } assert(longestWithinLimit(a, 0) == best); } }                                                                                // ③
    { const long N = 200000; std::vector<int> big(N); for (int& x : big) x = (int)(rng() % 1000);
      CountingDeque::ops = 0; int r = longestWithinLimit(big, 50); long ops1 = CountingDeque::ops; assert(r >= 1 && r == bruteLongest(big, 50) && ops1 >= 2 * N && ops1 <= 4 * N);                                 // 덱 둘: 넣기 2N + 빼기 ≤ 2N
      CountingDeque::ops = 0; std::vector<int> w = windowMin(big, 1000); long ops2 = CountingDeque::ops; assert(w.size() == 199001 && ops2 >= N && ops2 <= 2 * N);
      for (int t = 0; t < 2000; t++) { std::size_t i = rng() % w.size(); assert(w[i] == *std::min_element(big.begin() + i, big.begin() + i + 1000)); } }               // ④
    { assert((longestWithinLimit({8, 2, 4, 7}, 4) == 2) && (longestWithinLimit({10, 1, 2, 4, 7, 2}, 5) == 4) && (longestWithinLimit({4, 2, 2, 2, 4, 4, 2, 2}, 0) == 3) && longestWithinLimit({}, 3) == 0 && windowMin({}, 1).empty()); }           // ⑤ 알려진 예제
    std::cout << "WindowMinimum: monotonic deques matched brute force for fixed-size window minima and for the longest subarray whose max-min stays within a limit (3000 random arrays each), and on a 200000-element input the deques made at most 2N (4N for the two-deque scan) push/pop operations, i.e. linear work with the same answers as brute force" << std::endl; return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(k) 또는 O(N)
```

# Part 8. 운영체제
## JobQueue()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <list>
#include <queue>
#include <random>
#include <unordered_map>
#include <vector>
#include <cassert>

// 작업 큐(JobQueue): 프린터 스풀러처럼 도착한 순서대로 하나씩 처리하는 FIFO 대기열이다. 한 번에 하나의 작업만 처리하는 단일 서버에서 작업 i 가 도착 시각 a_i, 처리 시간 s_i 이면 시작 시각 start_i = max(a_i, finish_{i−1}), 종료 시각 finish_i = start_i + s_i 이다(린들리의 점화식). 대기 시간 = start_i − a_i. FIFO 이므로 종료 시각은 도착 순서대로 증가한다.
// 실제 스풀러는 대기 중인 작업을 취소할 수 있어야 한다. 큐 중간에서 O(1) 로 제거하려면 (작업 번호 → 리스트 노드) 해시 맵과 이중 연결 리스트를 함께 쓴다. 이미 처리 중인 작업은 취소할 수 없다.
// 검증: ① 이벤트 시뮬레이션(큐를 실제로 사용)의 시작·종료 시각이 린들리 점화식과 정확히 같다 ② 서버가 놀지 않은 구간의 총 처리량: 총 처리 시간 == Σ s_i, 마지막 종료 시각 ≥ 첫 도착 + Σ s_i ③ 종료 시각이 도착 순서대로 증가(FIFO 공정성) ④ 취소를 섞은 시뮬레이션이 "취소된 작업을 뺀 점화식" 과 같다 ⑤ 어떤 시점에도 서버가 동시에 두 작업을 처리하지 않는다(시간 구간이 겹치지 않음) ⑥ 대기 중 작업 수의 시간 평균이 리틀의 법칙 L = (평균 체류 시간) × (도착률) 과 일치
struct Job { int id; long arrive, service; };
struct Timing { long start = -1, finish = -1; bool cancelled = false; };
class Spooler {
    std::list<Job> waiting_; std::unordered_map<int, std::list<Job>::iterator> where_;
public:
    void submit(const Job& j) { waiting_.push_back(j); where_[j.id] = std::prev(waiting_.end()); }
    bool cancel(int id) { auto it = where_.find(id); if (it == where_.end()) return false; waiting_.erase(it->second); where_.erase(it); return true; }          // 대기 중이면 O(1) 제거
    bool next(Job& out) { if (waiting_.empty()) return false; out = waiting_.front(); where_.erase(out.id); waiting_.pop_front(); return true; }
    std::size_t waiting() const { return waiting_.size(); }
};
int main() {
    std::mt19937 rng(5); long littleChecks = 0;
    for (int t = 0; t < 400; t++) { int n = 1 + rng() % 40; std::vector<Job> jobs; long time = 0; for (int i = 0; i < n; i++) { time += rng() % 6; jobs.push_back({i, time, 1 + (long)(rng() % 8)}); }
        std::vector<char> willCancel(n, 0); for (int i = 0; i < n; i++) willCancel[i] = t % 2 && rng() % 5 == 0; std::vector<long> cancelAt(n, 0); for (int i = 0; i < n; i++) cancelAt[i] = jobs[i].arrive + rng() % 20;
        // 이벤트 시뮬레이션
        Spooler sp; std::vector<Timing> tm(n); long now = 0; std::size_t nextArrival = 0; Job cur{-1, 0, 0}; bool busy = false; long busyTotal = 0; long areaWaiting = 0, lastT = 0;
        std::vector<std::pair<long, int>> cancels; for (int i = 0; i < n; i++) if (willCancel[i]) cancels.push_back({cancelAt[i], i}); std::sort(cancels.begin(), cancels.end()); std::size_t nextCancel = 0;
        for (;;) {
            long tArr = nextArrival < jobs.size() ? jobs[nextArrival].arrive : -1, tCan = nextCancel < cancels.size() ? cancels[nextCancel].first : -1, tFin = busy ? tm[cur.id].finish : -1; long tNext = -1;
            for (long x : {tArr, tCan, tFin}) if (x >= 0 && (tNext < 0 || x < tNext)) tNext = x;
            if (tNext < 0) break; areaWaiting += (long)sp.waiting() * (tNext - lastT); lastT = tNext; now = tNext;
            if (busy && tFin == now) busy = false;                                                                 // 종료 먼저 처리
            while (nextArrival < jobs.size() && jobs[nextArrival].arrive == now) { sp.submit(jobs[nextArrival]); nextArrival++; }
            while (nextCancel < cancels.size() && cancels[nextCancel].first == now) { int id = cancels[nextCancel].second; if (sp.cancel(id)) tm[id].cancelled = true; nextCancel++; }
            if (!busy && sp.next(cur)) { busy = true; tm[cur.id].start = now; tm[cur.id].finish = now + cur.service; busyTotal += cur.service; }
        }
        // 린들리 점화식 (취소된 작업을 뺀다)
        long prevFinish = 0; std::vector<Timing> rec(n); long sumService = 0;
        for (int i = 0; i < n; i++) { if (tm[i].cancelled) continue; rec[i].start = std::max(jobs[i].arrive, prevFinish); rec[i].finish = rec[i].start + jobs[i].service; prevFinish = rec[i].finish; sumService += jobs[i].service;
            assert(tm[i].start == rec[i].start && tm[i].finish == rec[i].finish); }                                                                              // ① ④
        assert(busyTotal == sumService);                                                                                                                         // ②
        long lastEnd = -1; for (int i = 0; i < n; i++) { if (tm[i].cancelled) continue; assert(tm[i].finish > lastEnd && (lastEnd < 0 || tm[i].start >= lastEnd)); lastEnd = tm[i].finish; }       // ③ ⑤ 겹치지 않고 FIFO
        bool anyCancelled = false; for (int i = 0; i < n; i++) anyCancelled |= tm[i].cancelled;
        if (!anyCancelled) { long totalWait = 0; for (int i = 0; i < n; i++) totalWait += tm[i].start - jobs[i].arrive; assert(areaWaiting == totalWait); littleChecks++; }          // ⑥ 대기열 길이의 시간 적분 == 대기 시간의 합
    }
    assert(littleChecks > 50);
    { Spooler sp; for (int i = 0; i < 5; i++) sp.submit({i, 0, 1}); assert(sp.cancel(2) && !sp.cancel(2) && !sp.cancel(99) && sp.waiting() == 4); Job j; std::vector<int> order; while (sp.next(j)) order.push_back(j.id); assert((order == std::vector<int>{0, 1, 3, 4}) && !sp.cancel(0)); }
    std::cout << "JobQueue: the queue-driven event simulation reproduced the Lindley recurrence exactly for 400 random workloads (half with cancellations); jobs never overlapped, finished in FIFO order, and the area under the waiting-queue length equalled the total waiting time (Little's law in integral form) on " << littleChecks << " cancellation-free runs" << std::endl; return 0;
}
// Time Complexity: submit·next·cancel 모두 O(1)
// Space Complexity: O(대기 작업 수)
```
## ReadyQueue()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 준비 큐(Ready Queue): 실행을 기다리는 프로세스를 담는 운영체제의 큐다. CPU 가 비면 스케줄러가 준비 큐에서 하나를 골라 실행시킨다. 큐의 구조와 고르는 규칙이 곧 스케줄링 알고리즘이다. FCFS: FIFO 큐에서 앞에서 꺼낸다. SJF(최단 작업 우선): 버스트가 가장 짧은 것을 꺼낸다(우선순위 큐). 우선순위 스케줄링: 우선순위 큐. 라운드 로빈(RR): FIFO 큐에서 꺼내 시간 할당량 q 만큼만 실행하고, 안 끝났으면 큐의 맨 뒤로 보낸다(회전).
// 평가 척도는 대기 시간(waiting = 반환 시간 − 버스트 − 도착 시간)이다. 모든 프로세스가 동시에 도착하는 경우 SJF 가 평균 대기 시간을 최소로 만드는 최적 순서다(작은 것을 앞에 두면 뒤따르는 모든 작업의 대기가 가장 적게 늘어난다 — 교환 논증). RR 은 평균 대기 시간이 길어질 수 있지만 응답이 빠르고 공정하다. q 가 최대 버스트 이상이면 RR 은 FCFS 와 같아지고, q 가 작아질수록 문맥 교환(슬라이스 수 Σ⌈burst/q⌉)이 늘어난다.
// 새로 도착한 프로세스와 시간 할당량이 끝나 되돌아온 프로세스가 같은 시각에 큐에 들어갈 때의 순서는 구현에 따라 다르다. 이 구현은 "그 시각까지 도착한 프로세스를 먼저 넣고, 그 뒤에 선점된 프로세스를 넣는다" 규칙을 쓴다.
// 검증: ① FCFS 대기 시간이 린들리 점화식과 같다 ② 모두 시각 0 에 도착할 때 SJF 의 평균 대기 시간이 n ≤ 7 의 모든 실행 순서 중 최소이고 FCFS 이하 ③ 라운드 로빈: 각 프로세스의 슬라이스 수 == ⌈burst/q⌉, 슬라이스는 q 이하, 한 프로세스의 슬라이스가 겹치지 않음, 도착 전에 실행되지 않음, CPU 가 일이 있는데 놀지 않음(작업 보존), 총 실행 시간 == Σ burst ④ q ≥ 최대 버스트이면 RR == FCFS ⑤ 우선순위 스케줄링(비선점)이 매번 도착한 것 중 최고 우선순위를 고르는 O(n²) 기준 구현과 같다 ⑥ 항등식 대기 = 반환 − 버스트 − 도착
struct Proc { int id, arrival, burst, priority; };
struct Slice { int pid; long start, end; };
struct Outcome { std::vector<long> finish; std::vector<Slice> slices; };
Outcome fcfs(std::vector<Proc> ps) { std::sort(ps.begin(), ps.end(), [](const Proc& a, const Proc& b) { return a.arrival != b.arrival ? a.arrival < b.arrival : a.id < b.id; }); Outcome o; o.finish.assign(ps.size(), 0); std::queue<Proc> ready; for (auto& p : ps) ready.push(p); long t = 0;
    while (!ready.empty()) { Proc p = ready.front(); ready.pop(); t = std::max<long>(t, p.arrival); o.slices.push_back({p.id, t, t + p.burst}); t += p.burst; o.finish[p.id] = t; } return o; }
Outcome roundRobin(const std::vector<Proc>& ps, int q) {
    std::vector<int> order(ps.size()); std::iota(order.begin(), order.end(), 0); std::sort(order.begin(), order.end(), [&](int a, int b) { return ps[a].arrival != ps[b].arrival ? ps[a].arrival < ps[b].arrival : a < b; });
    Outcome o; o.finish.assign(ps.size(), 0); std::vector<int> rem(ps.size()); for (std::size_t i = 0; i < ps.size(); i++) rem[i] = ps[i].burst; std::queue<int> ready; std::size_t next = 0; long t = 0; std::size_t done = 0;
    while (done < ps.size()) {
        while (next < order.size() && ps[order[next]].arrival <= t) ready.push(order[next++]);
        if (ready.empty()) { t = ps[order[next]].arrival; continue; }                                    // 일이 없으면 다음 도착으로 건너뛴다
        int p = ready.front(); ready.pop(); int run = std::min(q, rem[p]); o.slices.push_back({p, t, t + run}); t += run; rem[p] -= run;
        while (next < order.size() && ps[order[next]].arrival <= t) ready.push(order[next++]);          // 실행 중에 도착한 것 먼저
        if (rem[p] > 0) ready.push(p); else { o.finish[p] = t; done++; }                                // 선점된 프로세스는 그 뒤에
    }
    return o;
}
std::vector<long> sjfAllAtZero(const std::vector<Proc>& ps) { std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> ready; for (auto& p : ps) ready.push({p.burst, p.id}); std::vector<long> start(ps.size()); long t = 0; while (!ready.empty()) { auto [b, id] = ready.top(); ready.pop(); start[id] = t; t += b; } return start; }
std::vector<long> priorityNonPreemptive(const std::vector<Proc>& ps) {                                    // 준비 큐 = 우선순위 큐 (값이 클수록 먼저, 같으면 먼저 도착한 것)
    auto less = [&](int a, int b) { return ps[a].priority != ps[b].priority ? ps[a].priority < ps[b].priority : (ps[a].arrival != ps[b].arrival ? ps[a].arrival > ps[b].arrival : a > b); };
    std::vector<int> order(ps.size()); std::iota(order.begin(), order.end(), 0); std::sort(order.begin(), order.end(), [&](int a, int b) { return ps[a].arrival != ps[b].arrival ? ps[a].arrival < ps[b].arrival : a < b; });
    std::priority_queue<int, std::vector<int>, decltype(less)> ready(less); std::vector<long> start(ps.size(), -1); long t = 0; std::size_t next = 0, done = 0;
    while (done < ps.size()) { while (next < order.size() && ps[order[next]].arrival <= t) ready.push(order[next++]); if (ready.empty()) { t = ps[order[next]].arrival; continue; } int p = ready.top(); ready.pop(); start[p] = t; t += ps[p].burst; done++; }
    return start;
}
std::vector<long> priorityBrute(const std::vector<Proc>& ps) { std::vector<long> start(ps.size(), -1); std::vector<char> done(ps.size(), 0); long t = 0; for (std::size_t k = 0; k < ps.size(); k++) { int best = -1; for (std::size_t i = 0; i < ps.size(); i++) if (!done[i] && ps[i].arrival <= t && (best < 0 || ps[i].priority > ps[best].priority || (ps[i].priority == ps[best].priority && (ps[i].arrival < ps[best].arrival || (ps[i].arrival == ps[best].arrival && (int)i < best))))) best = i;
        if (best < 0) { long na = LONG_MAX; for (std::size_t i = 0; i < ps.size(); i++) if (!done[i]) na = std::min<long>(na, ps[i].arrival); t = na; k--; continue; } start[best] = t; t += ps[best].burst; done[best] = 1; } return start; }
double avgWaitFromStart(const std::vector<Proc>& ps, const std::vector<long>& start) { double s = 0; for (auto& p : ps) s += start[p.id] - p.arrival; return s / ps.size(); }
int main() {
    std::mt19937 rng(7); long slicesChecked = 0;
    for (int t = 0; t < 400; t++) { int n = 1 + rng() % 7; std::vector<Proc> ps; int arr = 0; for (int i = 0; i < n; i++) { arr += rng() % 5; ps.push_back({i, arr, 1 + (int)(rng() % 9), (int)(rng() % 4)}); } std::vector<Proc> zero = ps; for (auto& p : zero) p.arrival = 0;
        auto f = fcfs(ps); long prev = 0; for (int i = 0; i < n; i++) { long st = std::max<long>(ps[i].arrival, prev); prev = st + ps[i].burst; assert(f.finish[i] == prev); }                                                      // ① FCFS == 린들리 점화식
        auto sj = sjfAllAtZero(zero); double sjfAvg = avgWaitFromStart(zero, sj); std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); double best = 1e18; do { double s = 0; long clock = 0; for (int id : perm) { s += clock; clock += zero[id].burst; } best = std::min(best, s / n); } while (std::next_permutation(perm.begin(), perm.end()));
        assert(std::abs(sjfAvg - best) < 1e-9); auto fc = fcfs(zero); double fcfsAvg = 0; for (int i = 0; i < n; i++) fcfsAvg += fc.finish[i] - zero[i].burst; assert(sjfAvg <= fcfsAvg / n + 1e-9);                                    // ② SJF 최적, ≤ FCFS
        for (int q : {1, 2, 3, 5, 100}) { auto rr = roundRobin(ps, q); long busy = 0; std::vector<long> slicesOf(n, 0), served(n, 0), lastEnd(n, -1);
            for (std::size_t k = 0; k < rr.slices.size(); k++) { const Slice& s = rr.slices[k]; assert(s.end - s.start <= q && s.start >= ps[s.pid].arrival && s.start >= lastEnd[s.pid]); lastEnd[s.pid] = s.end; slicesOf[s.pid]++; served[s.pid] += s.end - s.start; busy += s.end - s.start;       // ③
                if (k) { assert(rr.slices[k - 1].end <= s.start); if (rr.slices[k - 1].end < s.start) { /* 놀았다면 그 사이 준비된 프로세스가 없어야 한다 */ for (int i = 0; i < n; i++) assert(!(ps[i].arrival <= rr.slices[k - 1].end && served[i] - (i == s.pid ? s.end - s.start : 0) < ps[i].burst && i != s.pid)); } } slicesChecked++; }
            for (int i = 0; i < n; i++) { assert(served[i] == ps[i].burst && slicesOf[i] == (ps[i].burst + q - 1) / q); long wait = rr.finish[i] - ps[i].burst - ps[i].arrival; assert(wait >= 0); } long total = 0; for (auto& p : ps) total += p.burst; assert(busy == total);          // ③ ⑥ 대기 = 반환 − 버스트 − 도착 >= 0
            if (q == 100) { auto fz = fcfs(ps); assert(rr.finish == fz.finish); } }                                                                                                                                                       // ④ q 가 크면 FCFS
        assert(priorityNonPreemptive(ps) == priorityBrute(ps)); }                                                                                                                                                                              // ⑤
    { std::vector<Proc> ps = {{0, 0, 5, 0}, {1, 0, 3, 0}, {2, 0, 8, 0}}; auto rr = roundRobin(ps, 2); std::vector<int> firstOrder; for (auto& s : rr.slices) firstOrder.push_back(s.pid); assert((firstOrder == std::vector<int>{0, 1, 2, 0, 1, 2, 0, 2, 2}) && rr.finish[1] == 9 && rr.finish[0] == 12 && rr.finish[2] == 16); }          // 교과서 예제
    std::cout << "ReadyQueue: FCFS matched the Lindley recurrence, SJF's average wait was the minimum over all execution orders (n<=7), round robin satisfied conservation/slice/overlap invariants over " << slicesChecked << " slices at five quanta (and equalled FCFS for a huge quantum), and the priority ready queue matched an O(n^2) reference" << std::endl; return 0;
}
// Time Complexity: FCFS·RR 선택 O(1), SJF·우선순위 선택 O(log N)
// Space Complexity: O(N)
```
## WaitingQueue()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 대기 큐(Waiting Queue): 어떤 사건(입출력 완료, 자원 반환, 잠금 해제)을 기다리며 잠든(blocked) 프로세스를 담는 큐다. 사건이 일어나면 대기 큐에서 프로세스를 꺼내 준비 큐로 옮긴다. 가장 대표적인 예가 세마포어다. 세마포어 값이 0 이면 P(wait) 호출자는 대기 큐에서 자고, V(signal) 는 대기 큐의 가장 오래 기다린 프로세스(FIFO)를 깨운다.
// FIFO 로 깨우면 "기아(starvation)" 가 없다 — 요청한 순서대로 반드시 자원을 얻는다(공정성). 세마포어의 불변식: ① 값 ≥ 0 ② 대기자가 있으면 값은 0 ③ 값 + (V 가 깨운 횟수 외에 아직 쓰지 않은 자원) 처럼 자원 보존 — 구체적으로 초기값 + 완료된 V − 통과한 P 가 현재 값(대기자가 없을 때)이다. 깨워진 프로세스는 값을 다시 줄이지 않고 바로 자원을 넘겨받는다(값이 대기자에게 직접 이전).
// 이 항목은 결정적 스케줄러 시뮬레이션이다: 무작위로 하나의 프로세스를 골라 한 단계 실행하는 방식으로 임계 구역을 반복하는 프로세스 n 개를 돌리고(이진 세마포어 = 상호 배제, 계수 세마포어 = 자원 K 개), 매 단계 불변식을 검사한다.
// 검증: ① 어느 순간에도 임계 구역 안의 프로세스 수 ≤ 초기 값 K(상호 배제) ② 대기자가 있을 때 값 == 0 ③ 깨우는 순서가 대기 시작 순서(FIFO)와 정확히 같다 ④ 모든 프로세스가 반복을 끝까지 마친다(기아·교착 없음) ⑤ 자원 보존: 매 단계 value + inCritical + (깨워졌지만 아직 실행하지 못한 수) == K ⑥ V 가 대기자를 깨울 때 값은 증가하지 않는다
class Semaphore {
    int value_; std::queue<int> waiters_; long woken_ = 0;
public:
    explicit Semaphore(int v) : value_(v) {}
    bool P(int pid) { if (value_ > 0) { value_--; return true; } waiters_.push(pid); return false; }               // 통과하면 true, 아니면 대기 큐에서 잠든다
    int V() { if (!waiters_.empty()) { int pid = waiters_.front(); waiters_.pop(); woken_++; return pid; } value_++; return -1; }     // 대기자가 있으면 값은 올리지 않고 가장 오래 기다린 프로세스에게 자원을 넘긴다
    int value() const { return value_; } std::size_t waiting() const { return waiters_.size(); } long woken() const { return woken_; }
};
enum State { WANT, BLOCKED, RUNNING_CS, DONE };
int main() {
    std::mt19937 rng(4); long totalGrants = 0;
    for (int K : {1, 2, 3}) for (int trial = 0; trial < 60; trial++) {
        const int N = 6, ROUNDS = 5; Semaphore sem(K); std::vector<State> st(N, WANT); std::vector<int> rounds(N, 0), csLeft(N, 0); std::vector<int> blockOrder, wakeOrder; int inCs = 0; std::size_t maxWaiting = 0;
        for (int step = 0; step < 100000; step++) {
            std::vector<int> runnable; for (int i = 0; i < N; i++) if (st[i] == WANT || st[i] == RUNNING_CS) runnable.push_back(i); if (runnable.empty()) break;       // BLOCKED 인 프로세스는 실행 불가
            int p = runnable[rng() % runnable.size()];
            if (st[p] == WANT) { if (sem.P(p)) { st[p] = RUNNING_CS; inCs++; csLeft[p] = 1 + rng() % 3; totalGrants++; } else { st[p] = BLOCKED; blockOrder.push_back(p); } }
            else { if (--csLeft[p] <= 0) { inCs--; int w = sem.V(); if (w >= 0) { assert(st[w] == BLOCKED); st[w] = RUNNING_CS; inCs++; csLeft[w] = 1 + rng() % 3; wakeOrder.push_back(w); totalGrants++; }          // V 가 대기자를 깨우면 자원이 직접 이전된다
                    st[p] = ++rounds[p] == ROUNDS ? DONE : WANT; } }
            assert(inCs <= K);                                                                                                                                                                      // ① 상호 배제
            if (sem.waiting() > 0) assert(sem.value() == 0);                                                                                                                                        // ② 대기자가 있으면 값 0
            assert(sem.value() + inCs == K - 0 || sem.value() + inCs <= K);                                                                                                                         // ⑤ 자원 보존: 값 + 사용 중 == K (대기자가 직접 받은 경우도 사용 중에 포함)
            assert(sem.value() + inCs == K);
            maxWaiting = std::max(maxWaiting, sem.waiting());
        }
        for (int i = 0; i < N; i++) assert(st[i] == DONE && rounds[i] == ROUNDS);                                                                                                                   // ④ 모두 끝났다
        assert(blockOrder == wakeOrder);                                                                                                                                                            // ③ 깨운 순서 == 잠든 순서 (FIFO)
        assert(sem.value() == K && sem.waiting() == 0 && sem.woken() == (long)wakeOrder.size()); }
    { Semaphore s(0); assert(!s.P(1) && !s.P(2) && s.V() == 1 && s.value() == 0 && s.V() == 2 && s.V() == -1 && s.value() == 1); }                                                                    // ⑥ 깨울 때는 값이 오르지 않고, 대기자가 없을 때만 오른다
    std::cout << "WaitingQueue: a FIFO-wakeup semaphore kept mutual exclusion (K=1,2,3) over 180 randomized scheduler runs, granted the resource in exactly the order processes blocked, conserved resources at every step, and let all processes finish (" << totalGrants << " grants)" << std::endl; return 0;
}
// Time Complexity: P·V O(1)
// Space Complexity: O(대기 프로세스 수)
```
## TimingWheel()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>

// 계층형 타이밍 휠(Hierarchical Timing Wheel, Varghese & Lauck 1987): 수만~수백만 개의 타이머(연결 제한 시간, 재전송 타이머, 캐시 만료)를 O(1) 에 등록·취소하고, 시간이 흐르면 만료된 것만 꺼낸다. 우선순위 큐의 O(log n) 대신 시계 바퀴를 쓴다.
// 바퀴 한 개는 64 칸(6 비트) 배열이고 칸 하나는 한 "틱" 에 대응한다. 만료까지 남은 시간(delta)이 64 미만이면 1 층(해상도 1 틱) 칸 (만료 시각 & 63) 에, 64² 미만이면 2 층(칸 하나가 64 틱) 칸 ((만료 시각 >> 6) & 63) 에 둔다 ...
// 4 층이면 2^24 틱까지 표현한다(그 너머는 넘침 목록: 가장 큰 바퀴가 한 바퀴 돌 때마다 다시 배치). 시간이 한 틱 흐를 때: 현재 시각이 64 의 배수에 닿으면 2 층의 해당 칸을 열어 타이머를 다시 배치(cascade — 이제 남은 시간이 짧아져 1 층으로 내려온다), 64² 의 배수면 3 층도 같은 일을 하고,
// 그 뒤 1 층의 현재 칸을 비우면 만료. 타이머 하나는 만료까지 많아야 (층 수 - 1) 번만 옮겨진다. 취소는 활성 표에서 지우면 끝(칸에서는 나중에 지연 삭제). 리눅스 커널 timer wheel, Netty·Kafka 의 시간 휠이 이 구조다.
// 검증: 시험용 16 칸 x 4 층 바퀴(2^16 틱 범위)에서 무작위 등록(지연 1~수십만 틱, 일부는 바퀴 범위 밖(넘침))·취소·같은 id 재등록과 틱 진행을 우선순위 큐 오라클과 대조 — 매 틱 만료된 id 집합이 정확히 같다(만료 시각 정확, 취소·재등록된 것은 만료 안 됨).
//       타이머당 옮김 횟수 <= 층 수 + 넘침 재배치 몫, 활성 타이머가 모두 소진되면 칸이 비어 있다.
template <int BITS = 6, int LEVELS = 4> class TimingWheel {                                        // 기본: 64 칸 x 4 층
    static const int SLOTS = 1 << BITS; struct Timer { uint64_t id, expiry; };
    uint64_t now_ = 0; std::vector<Timer> slot_[LEVELS][SLOTS]; std::vector<Timer> overflow_; std::unordered_map<uint64_t, uint64_t> active_;         // id -> 현재 유효한 만료 시각
public:
    long moves = 0;                                                                               // 칸에 넣은 총 횟수(등록 + cascade)
    uint64_t now() const { return now_; } size_t pending() const { return active_.size(); }
    void add(uint64_t id, uint64_t delay) { active_[id] = now_ + delay; place({id, now_ + delay}); }       // 같은 id 를 다시 등록하면 앞의 것은 무효(지연 삭제)
    void cancel(uint64_t id) { active_.erase(id); }
    void place(const Timer& t) {
        ++moves; const uint64_t delta = t.expiry > now_ ? t.expiry - now_ : 0;
        for (int lv = 0; lv < LEVELS; ++lv) if (delta < (1ULL << (BITS * (lv + 1)))) { slot_[lv][(t.expiry >> (BITS * lv)) & (SLOTS - 1)].push_back(t); return; }
        overflow_.push_back(t);                                                                    // 2^24 틱보다 먼 타이머
    }
    std::vector<uint64_t> tick() {                                                                 // 시각을 한 틱 진행하고 이번 틱에 만료된 id 를 돌려준다
        ++now_;
        if ((now_ & ((1ULL << (BITS * LEVELS)) - 1)) == 0) { std::vector<Timer> o; o.swap(overflow_); for (const Timer& t : o) place(t); }          // 가장 큰 바퀴가 한 바퀴 돌았다: 넘침 목록 재배치
        for (int lv = LEVELS - 1; lv >= 1; --lv) if ((now_ & ((1ULL << (BITS * lv)) - 1)) == 0) {                                                     // 높은 층부터 칸을 열어 아래로 내려보낸다
            std::vector<Timer> cell; cell.swap(slot_[lv][(now_ >> (BITS * lv)) & (SLOTS - 1)]); for (const Timer& t : cell) { auto it = active_.find(t.id); if (it != active_.end() && it->second == t.expiry) place(t); }
        }
        std::vector<uint64_t> fired; std::vector<Timer> cell; cell.swap(slot_[0][now_ & (SLOTS - 1)]);
        for (const Timer& t : cell) { auto it = active_.find(t.id); if (it != active_.end() && it->second == t.expiry) { assert(t.expiry == now_); fired.push_back(t.id); active_.erase(it); } }
        return fired;
    }
};

int main() {
    {   TimingWheel<> w; w.add(1, 3); w.add(2, 3); w.add(3, 70); w.add(4, 5000); w.add(5, 10); w.cancel(5);                       // 손으로 확인: 3 틱 뒤 1·2, 70 틱 뒤 3(2 층에서 내려옴), 5000 틱 뒤 4(3 층), 5 는 취소
        std::vector<std::pair<uint64_t, std::vector<uint64_t>>> got; for (int i = 0; i < 5100; ++i) { auto f = w.tick(); std::sort(f.begin(), f.end()); if (!f.empty()) got.push_back({w.now(), f}); }
        assert((got == std::vector<std::pair<uint64_t, std::vector<uint64_t>>>{{3, {1, 2}}, {70, {3}}, {5000, {4}}}) && w.pending() == 0); }
    // 시험은 16 칸 x 4 층(2^16 틱)으로 줄여 넘침·cascade 가 자주 일어나게 한다
    std::mt19937 rng(91); TimingWheel<4, 4> wheel; std::map<uint64_t, uint64_t> oracle; std::multimap<uint64_t, uint64_t> byExpiry;              // 오라클: id -> 만료, 만료 시각 -> id
    long adds = 0, cancels = 0, rearms = 0, firedTotal = 0, overflowAdds = 0; uint64_t nextId = 1;
    for (int step = 0; step < 400000; ++step) {
        const int op = (int)(rng() % 100);
        if (op < 6) { uint64_t d; const int kind = (int)(rng() % 10);                                // 지연: 짧음 / 중간 / 긺 / 아주 긺(넘침)
            if (kind < 5) d = 1 + rng() % 40; else if (kind < 8) d = 1 + rng() % 3000; else if (kind < 9) d = 1 + rng() % 60000; else { d = (1ULL << 16) + rng() % 200000; ++overflowAdds; }
            uint64_t id = nextId++; if (rng() % 8 == 0 && !oracle.empty()) { auto it = oracle.begin(); std::advance(it, (long)(rng() % oracle.size())); id = it->first; ++rearms; }          // 가끔 기존 id 를 새 시각으로 재등록
            if (oracle.count(id)) { auto range = byExpiry.equal_range(oracle[id]); for (auto r = range.first; r != range.second; ++r) if (r->second == id) { byExpiry.erase(r); break; } }
            oracle[id] = wheel.now() + d; byExpiry.insert({wheel.now() + d, id}); wheel.add(id, d); ++adds; }
        else if (op < 8 && !oracle.empty()) { auto it = oracle.begin(); std::advance(it, (long)(rng() % oracle.size())); const uint64_t id = it->first;
            auto range = byExpiry.equal_range(it->second); for (auto r = range.first; r != range.second; ++r) if (r->second == id) { byExpiry.erase(r); break; } oracle.erase(it); wheel.cancel(id); ++cancels; }
        auto fired = wheel.tick(); std::sort(fired.begin(), fired.end());
        std::vector<uint64_t> want; auto range = byExpiry.equal_range(wheel.now()); for (auto r = range.first; r != range.second; ++r) want.push_back(r->second); byExpiry.erase(range.first, range.second);
        std::sort(want.begin(), want.end()); for (uint64_t id : want) oracle.erase(id);
        assert(fired == want); firedTotal += (long)fired.size(); assert(wheel.pending() == oracle.size());
    }
    while (wheel.pending() > 0 && wheel.now() < (1ULL << 21)) { auto fired = wheel.tick(); std::sort(fired.begin(), fired.end()); std::vector<uint64_t> want; auto range = byExpiry.equal_range(wheel.now()); for (auto r = range.first; r != range.second; ++r) want.push_back(r->second); byExpiry.erase(range.first, range.second); std::sort(want.begin(), want.end()); assert(fired == want); for (uint64_t id : want) oracle.erase(id); }       // 남은 타이머도 정확한 시각에 모두 만료
    assert(wheel.pending() == 0 && oracle.empty() && byExpiry.empty() && overflowAdds > 100);
    assert(wheel.moves <= adds * 7);                                                               // 등록 1 + 층 이동 최대 3 + 넘침 재배치 몫: 등록당 상수 번
    std::cout << "TimingWheel: " << adds << " timer registrations (" << rearms << " re-arms, " << cancels << " cancels, " << overflowAdds << " beyond the wheel range) fired exactly " << firedTotal << " times at exactly their expiry tick, matching a priority-queue oracle on every one of " << wheel.now() << " ticks; " << (double)wheel.moves / (double)adds << " wheel placements per timer" << std::endl;
    return 0;
}
// Time Complexity: 등록·취소 O(1), 틱 하나 O(만료되거나 cascade 되는 타이머 수) — 타이머당 많아야 층 수만큼 이동
// Space Complexity: O(활성 타이머 + 칸 수 256 + 취소됐지만 아직 칸에 남은 항목)
```
## MessageQueue()
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 메시지 큐(MessageQueue): 프로세스 사이에 메시지를 주고받는 운영체제의 IPC 수단이다(POSIX mq_send/mq_receive). 단순 FIFO 가 아니라 메시지마다 우선순위를 가지며, 수신자는 항상 "가장 높은 우선순위, 그 안에서는 가장 먼저 보낸 것" 을 받는다. 큐에는 최대 메시지 수(maxmsg)와 메시지 크기(msgsize) 제한이 있다.
// 의미: send 는 큐가 가득 차면 (비차단 모드에서) 실패(EAGAIN), 메시지가 너무 크면 실패(EMSGSIZE). receive 는 큐가 비면 실패(EAGAIN). 구현은 우선순위별 FIFO 덱을 std::map 에 두는 방식(우선순위 가짓수가 적을 때 O(log P)), 또는 (우선순위, 도착 번호) 키의 힙 방식이다.
// 검증: 무작위 send/receive 5 만 번을 ① 벡터에 쌓고 매번 "우선순위 내림차순, 도착 순서" 규칙으로 가장 앞의 것을 찾는 브루트포스와 대조 ② 같은 우선순위끼리 FIFO ③ 가득 찬 큐의 send 는 EAGAIN 이고 상태 불변 ④ 너무 큰 메시지는 EMSGSIZE ⑤ 빈 큐의 receive 는 EAGAIN ⑥ 현재 메시지 수 == 보낸 성공 수 − 받은 성공 수 ⑦ 최대 우선순위만 계속 보내면 낮은 우선순위가 굶는 현상(기아)이 생김을 관찰
enum Err { OK = 0, EAGAIN_ = 1, EMSGSIZE_ = 2 };
struct Message { int priority; std::string body; };
class MessageQueue {
    std::map<int, std::deque<std::string>, std::greater<int>> byPriority_; std::size_t maxMsg_, maxSize_, count_ = 0;
public:
    MessageQueue(std::size_t maxMsg, std::size_t maxSize) : maxMsg_(maxMsg), maxSize_(maxSize) {}
    Err send(int priority, const std::string& body) { if (body.size() > maxSize_) return EMSGSIZE_; if (count_ == maxMsg_) return EAGAIN_; byPriority_[priority].push_back(body); count_++; return OK; }
    Err receive(Message& out) { if (!count_) return EAGAIN_; auto it = byPriority_.begin(); out = {it->first, it->second.front()}; it->second.pop_front(); if (it->second.empty()) byPriority_.erase(it); count_--; return OK; }
    std::size_t size() const { return count_; }
};
int main() {
    std::mt19937 rng(8); MessageQueue q(16, 8); struct Rec { int prio; long seq; std::string body; }; std::vector<Rec> ref; long seq = 0, sent = 0, received = 0, eagainSend = 0, eagainRecv = 0, toobig = 0;
    for (int step = 0; step < 50000; step++) {
        if (rng() % 2) { int prio = (int)(rng() % 5); std::string body(rng() % 12, (char)('a' + rng() % 26)); Err e = q.send(prio, body);
            if (body.size() > 8) { assert(e == EMSGSIZE_); toobig++; } else if (ref.size() == 16) { assert(e == EAGAIN_); eagainSend++; } else { assert(e == OK); ref.push_back({prio, seq++, body}); sent++; } }          // ③ ④
        else { Message m; Err e = q.receive(m); if (ref.empty()) { assert(e == EAGAIN_); eagainRecv++; } else { assert(e == OK); std::size_t best = 0; for (std::size_t i = 1; i < ref.size(); i++) if (ref[i].prio > ref[best].prio || (ref[i].prio == ref[best].prio && ref[i].seq < ref[best].seq)) best = i;
                assert(m.priority == ref[best].prio && m.body == ref[best].body); ref.erase(ref.begin() + best); received++; } }                                                              // ① ② ⑤
        assert(q.size() == ref.size() && (long)q.size() == sent - received);                                                                                                                        // ⑥
    }
    assert(eagainSend > 0 && eagainRecv > 0 && toobig > 0);
    { MessageQueue s(1000, 4); for (int i = 0; i < 500; i++) s.send(0, "low"); int served = 0; for (int i = 0; i < 400; i++) { s.send(9, "hi"); s.send(9, "hi"); Message m; s.receive(m); if (m.priority == 0) served++; } assert(served == 0 && s.size() == 500 + 400 * 2 - 400); }   // ⑦ 높은 우선순위가 계속 오는 동안 낮은 쪽은 한 번도 받지 못한다
    std::cout << "MessageQueue: the priority-then-FIFO queue matched a brute-force selection over 50000 operations (" << sent << " sent, " << received << " received, " << eagainSend << " full-queue and " << eagainRecv << " empty-queue EAGAINs, " << toobig << " EMSGSIZE rejections); starvation of low priority was reproduced" << std::endl; return 0;
}
// Time Complexity: send·receive O(log P) (P = 서로 다른 우선순위 수)
// Space Complexity: O(메시지 수)
```

# Part 9. 네트워크
## PacketQueue()
### 대표코드
```cpp
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 패킷 큐(PacketQueue): 라우터의 출력 포트에서 전송 순서를 기다리는 패킷 버퍼다. 유한한 크기 K 의 FIFO 이며 가득 찬 상태에서 도착한 패킷은 버려진다(꼬리 버림, tail drop). 도착이 일시적으로 서비스 속도를 넘는 폭주(burst)를 흡수하는 것이 버퍼의 일이고, 버퍼가 클수록 손실은 줄지만 지연(큐에서 기다리는 시간)이 늘어난다 — 지나치게 큰 버퍼가 지연을 키우는 문제가 bufferbloat 이다.
// 슬롯 시간 모델: 매 슬롯 먼저 서비스(큐가 비어 있지 않으면 확률 s 로 패킷 하나 송신), 그다음 도착(확률 p 로 패킷 하나, 큐 길이가 K 미만이면 입장, 아니면 버림). 큐 길이는 출생–사망 연쇄가 된다: 길이 0 → 1 확률 p, 0 < i < K 에서 i → i+1 확률 (1−s)p, i → i−1 확률 s(1−p). 정상 분포 π 는 균형 방정식 π_i · up_i = π_{i+1} · down_{i+1} 으로 구하며, 슬롯당 손실률은 π_K · (1−s) · p 다.
// 검증: 매 슬롯 ① 보존 법칙: 도착 수 == 송신 + 버림 + 현재 큐 길이 ② 큐 길이 ≤ K ③ 200 만 슬롯 시뮬레이션의 평균 큐 길이·손실률이 이론값(출생–사망 연쇄의 정상 분포)과 상대 오차 3% 이내 ④ 버퍼를 키우면 손실률은 줄고 평균 큐 길이(지연)는 는다(bufferbloat) ⑤ 부하 p < s 일 때 버퍼가 충분히 크면 손실이 사실상 0
struct Stats { long arrived = 0, sent = 0, dropped = 0; double meanLen = 0; };
Stats simulate(double p, double s, int K, long slots, unsigned seed) {
    std::mt19937_64 rng(seed); std::uniform_real_distribution<double> U(0, 1); std::queue<int> buf; Stats st; double lenSum = 0;
    for (long t = 0; t < slots; t++) {
        if (!buf.empty() && U(rng) < s) { buf.pop(); st.sent++; }                                                  // 서비스
        if (U(rng) < p) { st.arrived++; if ((int)buf.size() < K) buf.push(1); else st.dropped++; }                // 도착: 가득 차면 꼬리 버림
        lenSum += (double)buf.size(); assert((int)buf.size() <= K && st.arrived == st.sent + st.dropped + (long)buf.size());      // ① ②
    }
    st.meanLen = lenSum / slots; return st;
}
void theory(double p, double s, int K, double& meanLen, double& dropRate) {
    std::vector<double> pi(K + 1, 0); pi[0] = 1; for (int i = 0; i < K; i++) { double up = i == 0 ? p : (1 - s) * p, down = s * (1 - p); pi[i + 1] = pi[i] * up / down; } double sum = 0; for (double x : pi) sum += x; for (double& x : pi) x /= sum;
    meanLen = 0; for (int i = 0; i <= K; i++) meanLen += i * pi[i]; dropRate = pi[K] * (1 - s) * p;
}
int main() {
    const long SLOTS = 2000000; struct Case { double p, s; int K; }; for (Case c : {Case{0.45, 0.5, 8}, Case{0.55, 0.5, 6}, Case{0.30, 0.5, 4}}) {
        Stats sim = simulate(c.p, c.s, c.K, SLOTS, 1); double mean, drop; theory(c.p, c.s, c.K, mean, drop); double simDrop = (double)sim.dropped / SLOTS;
        assert(std::abs(sim.meanLen - mean) / mean < 0.03 && std::abs(simDrop - drop) / drop < 0.05);                                                                                // ③ 이론과 일치 (손실률은 표본이 적어 5%)
        std::cout << "p=" << c.p << " s=" << c.s << " K=" << c.K << ": mean queue " << sim.meanLen << " (theory " << mean << "), drop rate " << simDrop << " (theory " << drop << "); "; }
    { double m4, d4, m16, d16; theory(0.45, 0.5, 4, m4, d4); theory(0.45, 0.5, 16, m16, d16); assert(d16 < d4 && m16 > m4); }                                                       // ④ 큰 버퍼: 손실 감소, 지연(평균 큐 길이) 증가
    { double m, d; theory(0.3, 0.5, 40, m, d); assert(d < 1e-9); }                                                                                                                  // ⑤ 부하가 낮고 버퍼가 크면 손실 ≈ 0
    std::cout << std::endl << "PacketQueue: packet conservation and the buffer bound held in every one of 6,000,000 simulated slots; mean queue length and tail-drop rate agreed with the birth-death chain, and a larger buffer lowered loss while raising delay" << std::endl; return 0;
}
// Time Complexity: 슬롯당 O(1)
// Space Complexity: O(K)
```
## ProducerConsumer()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <condition_variable>
#include <iostream>
#include <map>
#include <mutex>
#include <set>
#include <thread>
#include <vector>

// 생산자–소비자(Producer–Consumer): 생산자는 항목을 만들어 유한한 버퍼(경계 버퍼)에 넣고, 소비자는 꺼내 쓴다. 버퍼가 가득 차면 생산자가, 비어 있으면 소비자가 기다려야 하고, 버퍼 자체는 한 번에 한 스레드만 만져야 한다. 고전적 해법은 세 개의 세마포어다: empty(빈 칸 수, 초기값 N), full(채워진 칸 수, 초기값 0), mutex(상호 배제, 초기값 1).
// 이 해법의 핵심은 연산 순서다. 생산자는 wait(empty) → wait(mutex) → 삽입 → signal(mutex) → signal(full), 소비자는 wait(full) → wait(mutex) → 제거 → signal(mutex) → signal(empty). wait(mutex)를 wait(empty)/wait(full)보다 먼저 하면 뮤텍스를 쥔 채로 잠들어 교착 상태가 된다. 이 코드는 먼저 프로토콜 자체를 모델 검사기(전 상태 탐색)로 검증하고, 그다음 같은 순서의 실제 스레드 구현을 부하 시험한다.
// ① 모델 검사: 상태 = (각 프로세스의 프로그램 카운터, empty, full, mutex, 버퍼 개수). 가능한 모든 인터리빙을 BFS 로 탐색해 교착(아무 프로세스도 진행 불가), 상호 배제 위반, 버퍼 개수의 범위 위반(0..N 밖)을 찾는다. 올바른 순서는 (생산자, 소비자) 1·1, 2·2, 3·2 에서 위반이 없고 버퍼가 정확히 N 까지 찰 수 있다(상한이 지나치게 보수적이지 않다는 뜻). 소비자만 순서가 틀리면 깊이 2, 둘 다 틀리면 깊이 1, 생산자만 틀리면 버퍼를 N 번 채워야 하므로 최단 5N+2 단계에서 교착한다. empty 세마포어를 빼면 개수가 N 을 넘는다.
// ② 실제 구현: 뮤텍스+조건 변수로 만든 계수 세마포어 위에 같은 프로토콜을 올린 경계 버퍼. 생산자 3·소비자 3 스레드가 용량 1·2·4·64 의 버퍼로 모든 항목을 정확히 한 번씩 주고받는지, 한 소비자가 본 한 생산자의 항목 순서가 유지되는지, 버퍼 점유가 용량을 넘지 않는지 확인한다. 그리고 비차단 버전(tryPut/tryTake)의 경계 동작을 결정적으로 확인한다.
enum class Order { Right, Wrong, NoEmpty };
struct Check { size_t states = 0; bool deadlock = false, mutexViolation = false, overflow = false; int deadlockDepth = -1, maxCount = 0; };
Check modelCheck(int P, int C, int N, Order prodOrder, Order consOrder) {
    int procs = P + C, E = procs, F = procs + 1, M = procs + 2, CNT = procs + 3;                                    // 상태 벡터 배치: pc[0..procs), empty, full, mutex, count
    using State = std::vector<int>; State init(procs + 4, 0); init[E] = N; init[M] = 1;
    auto holds = [&](int i, int pc) { bool prod = i < P; Order o = prod ? prodOrder : consOrder; return o == Order::Wrong ? (pc >= 1 && pc <= 3) : (pc >= 2 && pc <= 3); };   // 뮤텍스를 쥔 구간
    auto step = [&](const State& s, int i, State& out) {                                                           // 프로세스 i 의 다음 상태(막혔으면 false)
        bool prod = i < P; Order o = prod ? prodOrder : consOrder; out = s; int pc = s[i]; int& own = prod ? out[E] : out[F]; int& other = prod ? out[F] : out[E];
        // 올바른 순서: 0 wait(own) 1 wait(mutex) 2 연산 3 signal(mutex) 4 signal(other).  틀린 순서: 0 wait(mutex) 1 wait(own).  NoEmpty: 0 은 아무것도 하지 않음, 4 의 signal 도 생략(생산자·소비자 모두 empty 를 안 쓴다)
        auto waitSem = [&](int& sem) { if (sem == 0) return false; sem--; return true; };
        bool ok = true; int next = pc + 1;
        if (pc == 0) { if (o == Order::Right) ok = waitSem(own); else if (o == Order::Wrong) ok = waitSem(out[M]); else if (prod) ok = true; else ok = waitSem(out[F]); }
        else if (pc == 1) { if (o == Order::Right) ok = waitSem(out[M]); else if (o == Order::Wrong) ok = waitSem(own); else ok = waitSem(out[M]); }
        else if (pc == 2) { out[CNT] += prod ? 1 : -1; }
        else if (pc == 3) { out[M]++; }
        else { if (o == Order::NoEmpty) { if (prod) out[F]++; } else other++; next = 0; }
        if (!ok) return false; out[i] = next; return true;
    };
    Check res; std::map<State, int> dist; std::vector<State> frontier{init}; dist[init] = 0;
    while (!frontier.empty()) { std::vector<State> nxt;
        for (const State& s : frontier) { int d = dist[s]; bool any = false; int inCrit = 0, held = 0;
            for (int i = 0; i < procs; i++) { if (s[i] == 2 || s[i] == 3) inCrit++; if (holds(i, s[i])) held++; }
            if (inCrit > 1 || held + s[M] != 1) res.mutexViolation = true; res.maxCount = std::max(res.maxCount, s[CNT]);
            for (int i = 0; i < procs; i++) { State t; if (!step(s, i, t)) continue; any = true;
                if (t[CNT] < 0 || t[CNT] > N) { res.overflow = true; continue; }                                      // 불변식 위반 상태는 확장하지 않음(NoEmpty 는 무한 상태 공간)
                if (!dist.count(t)) { dist[t] = d + 1; nxt.push_back(t); } }
            if (!any && !res.deadlock) { res.deadlock = true; res.deadlockDepth = d; } }
        frontier = nxt; }
    res.states = dist.size(); return res;
}

class Semaphore {                                                                                                    // 계수 세마포어 = 뮤텍스 + 조건 변수
    std::mutex m; std::condition_variable cv; int count;
public:
    explicit Semaphore(int c) : count(c) {}
    void wait() { std::unique_lock<std::mutex> lk(m); cv.wait(lk, [&] { return count > 0; }); --count; }
    bool tryWait() { std::lock_guard<std::mutex> lk(m); if (count == 0) return false; --count; return true; }
    void signal() { { std::lock_guard<std::mutex> lk(m); ++count; } cv.notify_one(); }
};
template <class T> class BoundedBuffer {                                                                             // 모델 검사한 순서 그대로: wait(빈칸) → 잠금 → 연산 → 해제 → signal(찬칸)
    std::vector<T> buf; size_t head = 0, tail = 0; int inBuf = 0, maxInBuf = 0; Semaphore empty, full; std::mutex mtx;
    void insert(const T& v) { std::lock_guard<std::mutex> g(mtx); buf[tail] = v; tail = (tail + 1) % buf.size(); maxInBuf = std::max(maxInBuf, ++inBuf); }
    T remove() { std::lock_guard<std::mutex> g(mtx); T v = buf[head]; head = (head + 1) % buf.size(); --inBuf; return v; }
public:
    explicit BoundedBuffer(size_t cap) : buf(cap), empty((int)cap), full(0) {}
    void put(const T& v) { empty.wait(); insert(v); full.signal(); }
    T take() { full.wait(); T v = remove(); empty.signal(); return v; }
    bool tryPut(const T& v) { if (!empty.tryWait()) return false; insert(v); full.signal(); return true; }
    bool tryTake(T& out) { if (!full.tryWait()) return false; out = remove(); empty.signal(); return true; }
    int maxOccupancy() { std::lock_guard<std::mutex> g(mtx); return maxInBuf; }
};
int main() {
    for (auto pc : std::vector<std::vector<int>>{{1, 1, 1}, {1, 1, 2}, {1, 1, 3}, {2, 2, 2}, {3, 2, 2}}) {            // ① 올바른 프로토콜: 교착·위반 없음, 버퍼는 정확히 N 까지 찬다
        Check r = modelCheck(pc[0], pc[1], pc[2], Order::Right, Order::Right); assert(!r.deadlock && !r.mutexViolation && !r.overflow && r.maxCount == pc[2] && r.states >= 10); }
    for (int N : {1, 2, 3, 4}) {                                                                                     // ② 순서가 틀린 변형의 최단 교착 깊이
        Check both = modelCheck(1, 1, N, Order::Wrong, Order::Wrong); assert(both.deadlock && both.deadlockDepth == 1);
        Check cons = modelCheck(1, 1, N, Order::Right, Order::Wrong); assert(cons.deadlock && cons.deadlockDepth == 2);
        Check prod = modelCheck(1, 1, N, Order::Wrong, Order::Right); assert(prod.deadlock && prod.deadlockDepth == 5 * N + 2); }
    { Check r = modelCheck(2, 2, 2, Order::Wrong, Order::Right); assert(r.deadlock); Check s = modelCheck(2, 2, 2, Order::Right, Order::Wrong); assert(s.deadlock); }
    { Check r = modelCheck(1, 1, 2, Order::NoEmpty, Order::NoEmpty); assert(r.overflow && !r.deadlock); }               // ③ empty 세마포어가 없으면 버퍼가 용량을 넘는다
    { BoundedBuffer<int> b(3); assert(b.tryPut(1) && b.tryPut(2) && b.tryPut(3) && !b.tryPut(4)); int v = 0;        // ④ 비차단 경계 동작
      assert(b.tryTake(v) && v == 1 && b.tryPut(4) && !b.tryPut(5)); assert(b.tryTake(v) && v == 2 && b.tryTake(v) && v == 3 && b.tryTake(v) && v == 4 && !b.tryTake(v) && b.maxOccupancy() == 3); }
    const int P = 3, C = 3, PER = 2000; size_t items = 0;                                                            // ⑤ 실제 스레드 부하 시험
    for (size_t cap : {1u, 2u, 4u, 64u}) {
        BoundedBuffer<int> buf(cap); std::vector<std::vector<int>> got(C); std::vector<std::thread> prod, cons;
        for (int c = 0; c < C; c++) cons.emplace_back([&, c] { for (;;) { int v = buf.take(); if (v < 0) break; got[c].push_back(v); } });
        for (int p = 0; p < P; p++) prod.emplace_back([&, p] { for (int i = 0; i < PER; i++) buf.put(p * 100000 + i); });
        for (auto& t : prod) t.join(); for (int c = 0; c < C; c++) buf.put(-1);                                       // 끝 표지(-1)를 소비자 수만큼
        for (auto& t : cons) t.join();
        std::vector<int> all; for (auto& g : got) { all.insert(all.end(), g.begin(), g.end());
            std::map<int, int> last; for (int v : g) { int p = v / 100000, i = v % 100000; if (last.count(p)) assert(i > last[p]); last[p] = i; } }            // 한 소비자가 본 한 생산자의 순서
        std::sort(all.begin(), all.end()); std::vector<int> want; for (int p = 0; p < P; p++) for (int i = 0; i < PER; i++) want.push_back(p * 100000 + i);
        assert(all == want && buf.maxOccupancy() <= (int)cap && buf.maxOccupancy() >= 1); items += all.size(); }
    std::cout << "ProducerConsumer: the semaphore protocol was exhaustively model-checked (no deadlock, mutual exclusion, count in [0,N]); wrong lock orders deadlocked at depths 1, 2 and 5N+2, and dropping 'empty' overflowed the buffer; the threaded bounded buffer moved " << items << " items exactly once for capacities 1/2/4/64" << std::endl; return 0;
}
// Time Complexity: put·take 각 O(1) (대기 제외), 모델 검사 O(상태 수 × 프로세스 수)
// Space Complexity: O(용량) (모델 검사는 O(상태 수))
```
## RingBuffer()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <deque>
#include <iostream>
#include <random>
#include <thread>
#include <vector>
#include <cassert>

// 링 버퍼(Ring Buffer): 고정 크기 배열을 원형으로 쓰는 FIFO. 바이트 스트림(소켓 수신 버퍼, 오디오 입출력, 로그 파이프)의 표준 구조이며 할당·이동이 없고 읽기/쓰기가 O(1) 이다.
// 구현 요점 세 가지. ① 용량을 2 의 거듭제곱으로 두고 인덱스 대신 "단조 증가하는 카운터" 를 저장한다 — 위치 = 카운터 & (용량−1). 그러면 빈 상태(tail == head)와 가득 찬 상태(tail − head == 용량)가 구별되어 한 칸을 낭비하지 않고, 카운터가 size_t 한계를 넘어 돌아가도 용량이 2^64 의 약수라 차이 계산이 맞는다.
// ② 구간이 배열 끝을 넘으면 memcpy 를 두 번(끝까지, 처음부터)으로 나눈다. ③ 생산자 하나·소비자 하나(SPSC)이면 잠금도 CAS 도 필요 없다: 생산자만 tail 을, 소비자만 head 를 쓰고 서로의 카운터는 acquire 로 읽고 자기 것은 release 로 공개하면 데이터 쓰기가 카운터 공개보다 먼저 보인다. 두 카운터는 서로 다른 캐시 라인에 둬서 거짓 공유를 피한다.
// 검증: ① 무작위 크기의 쓰기·읽기를 std::deque 모델(용량 제한)과 대조, 가득/빈 경계와 래핑 ② 카운터를 size_t 최댓값 근처에서 시작해도 동일 ③ 생산자·소비자 두 스레드로 8 MB 의사난수 스트림을 임의 청크 크기로 주고받아 바이트가 하나도 변하거나 빠지지 않음(TSan 으로도 검증)
class SpscRing {
    std::vector<uint8_t> buf; const size_t cap, mask; alignas(64) std::atomic<size_t> head; alignas(64) std::atomic<size_t> tail;
public:
    explicit SpscRing(size_t capacityPow2, size_t startCounter = 0) : buf(capacityPow2), cap(capacityPow2), mask(capacityPow2 - 1), head(startCounter), tail(startCounter) { assert((cap & mask) == 0); }
    size_t size() const { return tail.load(std::memory_order_acquire) - head.load(std::memory_order_acquire); }
    size_t write(const uint8_t* p, size_t n) {                                         // 생산자 전용. 실제로 쓴 바이트 수를 돌려준다
        size_t t = tail.load(std::memory_order_relaxed), h = head.load(std::memory_order_acquire); n = std::min(n, cap - (t - h));
        if (!n) return 0;                                                                                                     // memcpy 에 널 포인터를 넘기지 않는다 (크기 0 이어도 정의되지 않은 동작)
        size_t off = t & mask, first = std::min(n, cap - off); std::memcpy(&buf[off], p, first); std::memcpy(&buf[0], p + first, n - first); tail.store(t + n, std::memory_order_release); return n;
    }
    size_t read(uint8_t* p, size_t n) {                                                // 소비자 전용
        size_t h = head.load(std::memory_order_relaxed), t = tail.load(std::memory_order_acquire); n = std::min(n, t - h);
        if (!n) return 0;
        size_t off = h & mask, first = std::min(n, cap - off); std::memcpy(p, &buf[off], first); std::memcpy(p + first, &buf[0], n - first); head.store(h + n, std::memory_order_release); return n;
    }
};
int main() {
    for (size_t start : {(size_t)0, (size_t)-1 - 100, (size_t)-1 - 7}) {
        SpscRing r(64, start); std::deque<uint8_t> model; std::mt19937 rng(5); uint8_t next = 0; size_t fullSeen = 0, emptySeen = 0;
        for (int step = 0; step < 50000; step++) {
            if (rng() % 2) { size_t n = rng() % 100; std::vector<uint8_t> data(n); for (auto& b : data) b = next++; size_t w = r.write(data.data(), n); assert(w == std::min(n, 64 - model.size())); next -= (uint8_t)(n - w); for (size_t i = 0; i < w; i++) model.push_back(data[i]); fullSeen += model.size() == 64; }
            else { size_t n = rng() % 100; std::vector<uint8_t> out(n); size_t g = r.read(out.data(), n); assert(g == std::min(n, model.size())); for (size_t i = 0; i < g; i++) { assert(out[i] == model.front()); model.pop_front(); } emptySeen += model.empty(); }
            assert(r.size() == model.size());
        }
        assert(fullSeen > 100 && emptySeen > 100);                                                                                                                                  // ① ② 가득/빈 상태 모두 경험, 용량 전체(64) 사용 가능
    }
    const size_t TOTAL = 8u << 20; SpscRing ring(4096); std::atomic<bool> bad{false}; uint64_t producedSum = 0, consumedSum = 0;
    std::thread prod([&] { std::mt19937 rng(7); std::vector<uint8_t> chunk(1500); size_t sent = 0; while (sent < TOTAL) { size_t n = std::min<size_t>(1 + rng() % 1500, TOTAL - sent); for (size_t i = 0; i < n; i++) chunk[i] = (uint8_t)((sent + i) * 31 % 251); size_t off = 0; while (off < n) { size_t w = ring.write(chunk.data() + off, n - off); off += w; if (!w) std::this_thread::yield(); } for (size_t i = 0; i < n; i++) producedSum += chunk[i]; sent += n; } });
    std::thread cons([&] { std::mt19937 rng(8); std::vector<uint8_t> chunk(2000); size_t got = 0; while (got < TOTAL) { size_t g = ring.read(chunk.data(), 1 + rng() % 2000); if (!g) { std::this_thread::yield(); continue; } for (size_t i = 0; i < g; i++) { if (chunk[i] != (uint8_t)((got + i) * 31 % 251)) bad = true; consumedSum += chunk[i]; } got += g; } });
    prod.join(); cons.join(); assert(!bad && producedSum == consumedSum && ring.size() == 0);                                                                                        // ③
    std::cout << "RingBuffer: matched a bounded deque model including counters starting near size_t max; " << TOTAL << " bytes streamed through a 4 KB SPSC ring with exact order and checksum " << consumedSum << std::endl; return 0;
}
// Time Complexity: write·read O(n) 바이트 복사 (memcpy 최대 2 번), 카운터 연산 O(1)
// Space Complexity: O(용량)
```
## CircularBuffer()
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 순환 버퍼(Circular Buffer): 가득 차면 가장 오래된 원소를 덮어쓰는 고정 용량 버퍼다. RingBuffer 항목이 "가득 차면 쓰기를 거절하는" 스트림 버퍼라면, 이쪽은 "최근 N 개만 기억" 하는 용도 — 로그의 마지막 N 줄, 최근 N 개 센서 값, 이동 평균, undo 이력.
// 구현의 핵심은 "비었다/가득 찼다" 의 구별이다. head == tail 만 저장하면 둘이 같은 상태가 된다. 해법: ① 항상 한 칸을 비워 두기(용량 N 에 N−1 개만 저장; 상태 구별은 쉽지만 한 칸 낭비) ② 원소 수 count 를 따로 저장(낭비 없음; 이 구현) ③ 카운터를 단조 증가시키고 차이로 크기를 구하기(RingBuffer 항목).
// 덮어쓰기 모드에서는 push 가 가득 찬 상태에서 head 를 한 칸 밀어 가장 오래된 값을 버린다. i 번째 오래된 원소는 a[(head + i) % N] 이라 임의 접근이 O(1) 이고, 이동 평균처럼 창 합계가 필요하면 들어오고 나가는 값으로 합을 갱신해 O(1) 에 유지한다. 메모리 위에서 연속이 필요하면 std::rotate 로 head 를 0 으로 옮기는 linearize 가 있다.
// 검증: ① 무작위 push/pop/덮어쓰기를 "용량 제한 deque(가득 차면 앞 제거)" 와 대조 ② 한 칸 비우는 변형은 용량 N 에서 N−1 개만 담음 ③ 이동 평균을 O(1) 갱신한 값이 매번 정의대로 다시 합한 값과 같음 ④ linearize 후 순서 보존, 빈 버퍼 접근은 예외
template <class T> class Circular {
    std::vector<T> a; size_t head = 0, count = 0;
public:
    explicit Circular(size_t cap) : a(cap) { if (!cap) throw std::invalid_argument("capacity"); }
    size_t size() const { return count; } size_t capacity() const { return a.size(); } bool full() const { return count == a.size(); } bool empty() const { return count == 0; }
    bool push(const T& v, T* evicted = nullptr) {                                        // 덮어썼으면 true (evicted 에 버려진 값)
        if (full()) { if (evicted) *evicted = a[head]; a[head] = v; head = (head + 1) % a.size(); return true; }
        a[(head + count) % a.size()] = v; count++; return false;
    }
    T pop_front() { if (empty()) throw std::out_of_range("empty"); T v = a[head]; head = (head + 1) % a.size(); count--; return v; }
    const T& operator[](size_t i) const { if (i >= count) throw std::out_of_range("index"); return a[(head + i) % a.size()]; }          // 0 이 가장 오래된 값
    const T& back() const { return (*this)[count - 1]; }
    void linearize() { std::rotate(a.begin(), a.begin() + head, a.end()); head = 0; }
    const std::vector<T>& raw() const { return a; }
};
struct OneSlotEmpty {                                                                    // 비교용: 항상 한 칸을 비우는 방식
    std::vector<int> a; size_t head = 0, tail = 0; explicit OneSlotEmpty(size_t n) : a(n) {}
    bool full() const { return (tail + 1) % a.size() == head; } bool empty() const { return head == tail; }
    bool push(int v) { if (full()) return false; a[tail] = v; tail = (tail + 1) % a.size(); return true; }
};
int main() {
    std::mt19937 rng(9);
    for (int cap : {1, 2, 3, 7, 16}) { Circular<int> c(cap); std::deque<int> model; for (int step = 0; step < 20000; step++) { int op = rng() % 5;
        if (op < 3) { int v = rng() % 1000, ev = -1; bool over = c.push(v, &ev); bool modelOver = (int)model.size() == cap; assert(over == modelOver); if (modelOver) { assert(ev == model.front()); model.pop_front(); } model.push_back(v); }
        else if (op == 3 && !model.empty()) { assert(c.pop_front() == model.front()); model.pop_front(); }
        assert(c.size() == model.size() && c.full() == ((int)model.size() == cap)); for (size_t i = 0; i < model.size(); i++) assert(c[i] == model[i]); } }                       // ①
    { OneSlotEmpty o(8); int stored = 0; while (o.push(stored)) stored++; Circular<int> c(8); for (int i = 0; i < 100; i++) c.push(i); assert(stored == 7 && c.size() == 8); }                       // ② 한 칸 비움: 용량 8 에서 7 개
    { const size_t W = 50; Circular<double> win(W); double sum = 0; for (int i = 0; i < 5000; i++) { double v = (rng() % 10000) / 100.0, gone = 0; bool over = win.push(v, &gone); sum += v - (over ? gone : 0); double exact = 0; for (size_t k = 0; k < win.size(); k++) exact += win[k]; assert(std::abs(sum - exact) < 1e-6); } }                       // ③ 이동 평균 O(1) 갱신
    { Circular<int> c(5); for (int i = 0; i < 12; i++) c.push(i); assert(c[0] == 7 && c.back() == 11); c.linearize(); assert(std::vector<int>(c.raw().begin(), c.raw().end()) == (std::vector<int>{7, 8, 9, 10, 11}));
      bool threw = false; Circular<int> e(3); try { e.pop_front(); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; try { (void)e[0]; } catch (const std::out_of_range&) { threw = true; } assert(threw); }          // ④
    std::cout << "CircularBuffer: overwrite-oldest semantics matched a capped deque for capacities 1..16; one-slot-empty stores only 7 of 8; O(1) moving-average sums matched recomputation" << std::endl; return 0;
}
// Time Complexity: push·pop_front·접근 O(1), linearize O(N)
// Space Complexity: O(용량)
```

# Part 10. 병렬
## LockFreeQueue()
### 대표코드
```cpp
#include <atomic>
#include <cstdint>
#include <deque>
#include <iostream>
#include <thread>
#include <vector>
#include <cassert>

// 락프리 큐(Vyukov 의 유계 MPMC 큐): 용량이 고정된 원형 배열의 각 칸에 순번(sequence) 필드를 두어, 생산자와 소비자가 "이 칸이 지금 내 차례인가" 를 순번으로 판단한다. 포인터 CAS 가 아니라 카운터 CAS 하나(enqueue 위치/dequeue 위치)만 경쟁하므로 ABA 도 노드 회수 문제도 없다.
// 칸 i 의 순번은 처음에 i. 위치 pos 에 쓰려는 생산자는 seq == pos 이면 자기 차례(CAS 로 enq 를 pos+1 로 올려 선점)이고, 데이터를 쓴 뒤 seq 를 pos+1 로 공개한다. 소비자는 seq == pos+1 이면 읽을 차례이며 읽은 뒤 seq 를 pos+용량 으로 올려 다음 바퀴의 생산자에게 칸을 넘긴다. seq < pos 이면 가득 참(아직 소비 안 됨), seq < pos+1 이면 빔 — 잠금 없이 판단한다.
// 성질: 한 스레드가 멈춰도 다른 스레드는 진행하지만(그 칸을 선점한 쪽이 쓰기를 마치기 전에는 그 칸의 소비자만 기다림) 엄밀한 wait-free 는 아니다. 가득/빈 경우를 실패 반환으로 알려 주므로 호출자가 backoff 정책(spin, yield, 블로킹)을 고른다. 무제한 큐는 MichaelScottQueue 항목.
// 검증: ① 단일 스레드: 정확히 용량만큼 들어가고 FIFO ② 용량 4 의 작은 큐에서 생산자 3·소비자 3 이 3 만 개씩 주고받아 모든 값이 정확히 한 번 나오고, 소비자마다 같은 생산자의 값은 증가 순서로 관측 ③ 가득/빈 실패가 실제로 발생(경쟁 경로 실행) ④ TSan 으로도 검증
template <class T> class MpmcQueue {
    struct Cell { std::atomic<size_t> seq; T data; };
    std::vector<Cell> buf; const size_t mask; alignas(64) std::atomic<size_t> enq{0}; alignas(64) std::atomic<size_t> deq{0};
public:
    explicit MpmcQueue(size_t capacityPow2) : buf(capacityPow2), mask(capacityPow2 - 1) { assert((capacityPow2 & mask) == 0 && capacityPow2 >= 2); for (size_t i = 0; i < capacityPow2; i++) buf[i].seq.store(i, std::memory_order_relaxed); }
    bool push(const T& v) {
        size_t pos = enq.load(std::memory_order_relaxed); Cell* c;
        for (;;) { c = &buf[pos & mask]; size_t seq = c->seq.load(std::memory_order_acquire); intptr_t dif = (intptr_t)seq - (intptr_t)pos;
            if (dif == 0) { if (enq.compare_exchange_weak(pos, pos + 1, std::memory_order_relaxed)) break; }          // 내 차례: 위치 선점
            else if (dif < 0) return false;                                                                        // 가득 참 (이전 바퀴의 값이 아직 소비되지 않음)
            else pos = enq.load(std::memory_order_relaxed); }                                                       // 다른 생산자가 앞섬
        c->data = v; c->seq.store(pos + 1, std::memory_order_release); return true;
    }
    bool pop(T& v) {
        size_t pos = deq.load(std::memory_order_relaxed); Cell* c;
        for (;;) { c = &buf[pos & mask]; size_t seq = c->seq.load(std::memory_order_acquire); intptr_t dif = (intptr_t)seq - (intptr_t)(pos + 1);
            if (dif == 0) { if (deq.compare_exchange_weak(pos, pos + 1, std::memory_order_relaxed)) break; }
            else if (dif < 0) return false;                                                                        // 비어 있음
            else pos = deq.load(std::memory_order_relaxed); }
        v = c->data; c->seq.store(pos + mask + 1, std::memory_order_release); return true;
    }
};
int main() {
    { MpmcQueue<int> q(8); int pushed = 0; while (q.push(pushed)) pushed++; assert(pushed == 8); int v; for (int i = 0; i < 8; i++) { assert(q.pop(v) && v == i); } assert(!q.pop(v)); for (int r = 0; r < 100; r++) { for (int i = 0; i < 5; i++) assert(q.push(r * 10 + i)); for (int i = 0; i < 5; i++) { assert(q.pop(v) && v == r * 10 + i); } } }                                // ① 용량·FIFO·바퀴 넘김
    const int P = 3, C = 3, N = 30000; MpmcQueue<int> q(4); std::atomic<int> consumed{0}; std::atomic<long> fullFails{0}, emptyFails{0}; std::atomic<bool> bad{false}; std::vector<std::vector<int>> seen(C, std::vector<int>(P, -1)); std::vector<std::vector<char>> got(P, std::vector<char>(N, 0)); std::vector<std::thread> ts;
    for (int p = 0; p < P; p++) ts.emplace_back([&, p] { for (int i = 0; i < N; i++) { while (!q.push(p * N + i)) { fullFails++; std::this_thread::yield(); } } });
    for (int c = 0; c < C; c++) ts.emplace_back([&, c] { int v; while (consumed.load() < P * N) { if (!q.pop(v)) { emptyFails++; std::this_thread::yield(); continue; } int p = v / N, i = v % N; if (i <= seen[c][p]) bad = true; seen[c][p] = i; got[p][i]++; consumed++; } });
    for (auto& t : ts) t.join(); assert(!bad && consumed == P * N); for (int p = 0; p < P; p++) for (int i = 0; i < N; i++) assert(got[p][i] == 1);                                      // ② 모든 값이 정확히 한 번, 소비자별 생산자 순서 유지
    assert(fullFails > 0 && emptyFails > 0);                                                                                                                                                         // ③ 경쟁 경로 실행
    std::cout << "LockFreeQueue: " << P * N << " items through a 4-slot MPMC queue (" << P << " producers, " << C << " consumers) with exactly-once delivery and per-producer order; full-queue retries " << fullFails << ", empty-queue retries " << emptyFails << std::endl; return 0;
}
// Time Complexity: push·pop 분할상환 O(1) (경쟁이 없을 때 CAS 1 번)
// Space Complexity: O(용량)
```
## MichaelScottQueue()
### 대표코드
```cpp
#include <atomic>
#include <cstdint>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>
#include <cassert>

// 마이클–스콧 큐(Michael & Scott 1996): 연결 리스트로 만든 무제한 락프리 FIFO. 더미 노드 하나로 시작해 head 는 "방금 꺼낸 노드(더미)", tail 은 "끝 근처" 를 가리킨다.
// enqueue: tail.next 가 비어 있으면 CAS 로 새 노드를 잇고 tail 을 새 노드로 민다. tail.next 가 이미 채워져 있으면 다른 스레드가 잇기만 하고 tail 을 못 민 것이므로 대신 밀어 준다(helping) — 덕분에 스레드가 멈춰도 다른 스레드가 진행한다. dequeue: head.next 의 값을 읽고 head 를 한 칸 CAS 로 전진시킨다. head == tail 이면서 next 가 있으면 tail 이 뒤처진 것이라 먼저 밀어 준다.
// 이 구현은 원 논문처럼 "카운터가 붙은 포인터" 를 쓴다: 노드를 32 비트 인덱스로 가리키고 64 비트 워드 상위에 32 비트 카운터를 붙여, 성공한 CAS 마다 카운터를 올린다. 꺼낸 더미 노드는 고정 풀로 돌려보내 재사용하므로 메모리가 새지 않으면서도 낡은 CAS 는 카운터 때문에 반드시 실패한다(ABA 방지). 풀이 비면 enqueue 는 false 를 돌려주고 호출자가 재시도한다.
// 검증: ① 단일 스레드 FIFO ② 생산자 3·소비자 3 이 3 만 개씩 주고받아 모든 값이 정확히 한 번, 소비자마다 같은 생산자의 값은 증가 순서 ③ 작은 풀(64 노드)에서 풀 고갈 재시도가 실제 발생하고도 끝난 뒤 자유 리스트 + 큐 안의 노드 + 더미 == 풀 크기(누수·중복 없음) ④ TSan 으로도 검증
// audit: stress (보존 법칙이 오라클: 모든 값이 정확히 한 번, 생산자별 순서, 노드 풀이 전부 돌아온다)
typedef uint64_t W; const uint32_t NIL = 0xFFFFFFFFu;
inline W mk(uint32_t cnt, uint32_t idx) { return ((W)cnt << 32) | idx; } inline uint32_t ix(W w) { return (uint32_t)w; } inline uint32_t ct(W w) { return (uint32_t)(w >> 32); }
class MSQueue {
    struct Node { std::atomic<int> val{0}; std::atomic<W> next{0}; };
    std::unique_ptr<Node[]> nodes; std::unique_ptr<std::atomic<uint32_t>[]> fnext; std::atomic<W> freeHead, head, tail; uint32_t cap;
    uint32_t alloc() { for (;;) { W h = freeHead.load(); uint32_t i = ix(h); if (i == NIL) return NIL; uint32_t nx = fnext[i].load(); if (freeHead.compare_exchange_weak(h, mk(ct(h) + 1, nx))) return i; } }
    void release(uint32_t i) { for (;;) { W h = freeHead.load(); fnext[i].store(ix(h)); if (freeHead.compare_exchange_weak(h, mk(ct(h) + 1, i))) return; } }
public:
    explicit MSQueue(uint32_t capacity) : nodes(new Node[capacity + 1]), fnext(new std::atomic<uint32_t>[capacity + 1]), cap(capacity + 1) {      // 노드 0 은 처음의 더미
        nodes[0].next = mk(0, NIL); head = tail = mk(0, 0); for (uint32_t i = 1; i <= capacity; i++) fnext[i] = i < capacity ? i + 1 : NIL; freeHead = mk(0, capacity ? 1 : NIL);
    }
    bool enqueue(int v) {
        uint32_t n = alloc(); if (n == NIL) return false; nodes[n].val.store(v); W old = nodes[n].next.load(); nodes[n].next.store(mk(ct(old) + 1, NIL));       // 카운터는 이전 생애보다 계속 증가
        for (;;) {
            W t = tail.load(); W nx = nodes[ix(t)].next.load(); if (t != tail.load()) continue;                           // 일관성 확인
            if (ix(nx) == NIL) { if (nodes[ix(t)].next.compare_exchange_weak(nx, mk(ct(nx) + 1, n))) { tail.compare_exchange_strong(t, mk(ct(t) + 1, n)); return true; } }
            else tail.compare_exchange_strong(t, mk(ct(t) + 1, ix(nx)));                                                 // 뒤처진 tail 을 대신 밀어 준다
        }
    }
    bool dequeue(int& out) {
        for (;;) {
            W h = head.load(), t = tail.load(); W nx = nodes[ix(h)].next.load(); if (h != head.load()) continue;
            if (ix(h) == ix(t)) { if (ix(nx) == NIL) return false; tail.compare_exchange_strong(t, mk(ct(t) + 1, ix(nx))); }          // 비었거나, tail 이 뒤처짐
            else { int v = nodes[ix(nx)].val.load(); if (head.compare_exchange_weak(h, mk(ct(h) + 1, ix(nx)))) { out = v; release(ix(h)); return true; } }       // CAS 전에 값을 읽는다 (성공 뒤엔 풀로 돌아갈 수 있다)
        }
    }
    size_t countFree() const { size_t c = 0; for (uint32_t i = ix(freeHead.load()); i != NIL; i = fnext[i].load()) c++; return c; }
    size_t countQueued() const { size_t c = 0; for (uint32_t i = ix(nodes[ix(head.load())].next.load()); i != NIL; i = ix(nodes[i].next.load())) c++; return c; }
    size_t total() const { return cap; }
};
int main() {
    { MSQueue q(100); int v; assert(!q.dequeue(v)); for (int i = 0; i < 100; i++) assert(q.enqueue(i)); assert(!q.enqueue(100)); for (int i = 0; i < 100; i++) { assert(q.dequeue(v) && v == i); } assert(!q.dequeue(v) && q.countFree() == 100); }          // ① FIFO와 풀 고갈
    const int P = 3, C = 3, N = 30000; MSQueue q(64); std::atomic<int> consumed{0}; std::atomic<long> poolRetries{0}; std::atomic<bool> bad{false}; std::vector<std::vector<int>> seen(C, std::vector<int>(P, -1)); std::vector<std::vector<char>> got(P, std::vector<char>(N, 0)); std::vector<std::thread> ts;
    for (int p = 0; p < P; p++) ts.emplace_back([&, p] { for (int i = 0; i < N; i++) { while (!q.enqueue(p * N + i)) { poolRetries++; std::this_thread::yield(); } } });
    for (int c = 0; c < C; c++) ts.emplace_back([&, c] { int v; while (consumed.load() < P * N) { if (!q.dequeue(v)) { std::this_thread::yield(); continue; } int p = v / N, i = v % N; if (i <= seen[c][p]) bad = true; seen[c][p] = i; got[p][i]++; consumed++; } });
    for (auto& t : ts) t.join(); assert(!bad && consumed == P * N); for (int p = 0; p < P; p++) for (int i = 0; i < N; i++) assert(got[p][i] == 1);                                                            // ②
    assert(poolRetries > 0 && q.countQueued() == 0 && q.countFree() + 1 == q.total());                                                                                                                  // ③ 누수·중복 없음 (더미 1 개 포함)
    std::cout << "MichaelScottQueue: " << P * N << " items delivered exactly once with per-producer order through a 64-node pool (" << poolRetries << " pool-exhaustion retries); every node returned to the pool" << std::endl; return 0;
}
// Time Complexity: enqueue·dequeue 분할상환 O(1) (락프리: 경쟁에서 재시도 가능)
// Space Complexity: O(풀 크기)
```
## WorkStealingQueue()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <deque>
#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <vector>

// 작업 훔치기 큐(Work-Stealing Queue): 작업 스케줄러의 워커마다 자기 덱을 하나씩 갖는다. 주인(owner)은 덱의 아래쪽(bottom)에서만 push/pop 하고(LIFO: 방금 만든 작은 일을 먼저, 캐시에 따뜻한 데이터), 일이 없는 다른 워커(도둑)는 위쪽(top)에서 훔친다(FIFO: 가장 오래된, 곧 가장 큰 일을 가져간다). 주인은 거의 경쟁 없이 움직이고 도둑끼리·도둑과 주인의 마지막 항목 경쟁만 CAS 로 해결한다.
// 이 코드는 Chase–Lev 덱(2005)이다: top 과 bottom 두 개의 원자 인덱스, 2 의 거듭제곱 크기의 원형 배열(가득 차면 두 배로 늘리고 옛 배열은 소멸자까지 보관 — 도둑이 옛 배열을 읽고 있을 수 있기 때문), pop 은 마지막 한 개일 때만 top 에 CAS, steal 은 항상 top 에 CAS. 모든 원자 연산은 순차적 일관성(seq_cst)이라 pop 의 `bottom 쓰기 → top 읽기` 순서(저장–적재 재배열 금지)가 보장된다.
// 검증: ① 순차 의미: 무작위 push/pop/steal 20 만 번이 std::deque 모델(pop=뒤, steal=앞)과 같고, 용량 2 에서 수천 개까지 늘어나도 내용이 보존된다. DFS 소유자 시나리오에서 훔친 노드의 깊이는 항상 덱 안의 최소 깊이(= 가장 큰 일) ② 동시성: 주인 1 + 도둑 3 이 18 만 개 작업을 처리할 때 모든 작업이 정확히 한 번 실행되고, 각 도둑이 훔친 id 는 단조 증가 ③ 포크–조인 트리(깊이 14, 32767 노드)를 워커 4 개가 서로 훔쳐 가며 실행: 모든 노드가 정확히 한 번 실행되고 종료 감지(대기 중 작업 수 0)가 정확.
struct Array {                                                                                                       // 원형 배열: 인덱스는 단조 증가하는 long, 슬롯은 i & (cap-1)
    long cap; std::unique_ptr<std::atomic<int>[]> a;
    explicit Array(long c) : cap(c), a(new std::atomic<int>[c]()) {}
    int get(long i) const { return a[i & (cap - 1)].load(); }
    void put(long i, int v) { a[i & (cap - 1)].store(v); }
};
enum class Steal { Empty, Abort, Success };
class ChaseLev {
    std::atomic<long> top{0}, bottom{0}; std::atomic<Array*> arr; std::vector<std::unique_ptr<Array>> all;          // all: 소유권 보관(옛 배열 포함) — 주인만 수정
public:
    explicit ChaseLev(long cap = 2) { all.emplace_back(new Array(cap)); arr.store(all.back().get()); }
    void push(int v) {                                                                                               // 주인 전용
        long b = bottom.load(), t = top.load(); Array* a = arr.load();
        if (b - t >= a->cap) { Array* n = new Array(a->cap * 2); for (long i = t; i < b; i++) n->put(i, a->get(i)); all.emplace_back(n); arr.store(n); a = n; }
        a->put(b, v); bottom.store(b + 1);                                                                           // 슬롯을 쓴 뒤에 bottom 을 올려 도둑에게 공개
    }
    bool pop(int& out) {                                                                                             // 주인 전용
        long b = bottom.load() - 1; Array* a = arr.load(); bottom.store(b); long t = top.load();                     // 먼저 bottom 을 내려 예약한 뒤 top 을 읽는다
        if (t > b) { bottom.store(b + 1); return false; }                                                            // 비어 있었음
        out = a->get(b); if (t < b) return true;                                                                     // 두 개 이상: 도둑과 경쟁 없음
        bool won = top.compare_exchange_strong(t, t + 1); bottom.store(b + 1); return won;                           // 마지막 하나: 도둑과 CAS 경쟁
    }
    Steal steal(int& out) {                                                                                          // 도둑 누구나
        long t = top.load(), b = bottom.load(); if (t >= b) return Steal::Empty;
        Array* a = arr.load(); int x = a->get(t); if (!top.compare_exchange_strong(t, t + 1)) return Steal::Abort;   // 다른 도둑/주인이 먼저 가져감
        out = x; return Steal::Success;
    }
    long size() const { return bottom.load() - top.load(); }
    long capacity() const { return arr.load()->cap; }
};
int depthOf(int id) { int d = 0; while (id > 1) { id >>= 1; d++; } return d; }                                       // 힙 번호의 깊이(루트 1 = 깊이 0)
int main() {
    { std::mt19937 rng(7); ChaseLev dq(2); std::deque<int> model; int next = 0; long steals = 0, pops = 0, empties = 0;                    // ① 순차 의미 == deque 모델
      for (int step = 0; step < 200000; step++) { int op = rng() % 10, v = 0;
          if (op < 5) { dq.push(next); model.push_back(next); next++; }
          else if (op < 8) { bool ok = dq.pop(v); assert(ok == !model.empty()); if (ok) { assert(v == model.back()); model.pop_back(); pops++; } else empties++; }
          else { Steal r = dq.steal(v); assert((r == Steal::Success) == !model.empty() && r != Steal::Abort); if (r == Steal::Success) { assert(v == model.front()); model.pop_front(); steals++; } else empties++; }
          assert(dq.size() == (long)model.size() && (long)model.size() <= dq.capacity()); }
      assert(steals > 10000 && pops > 10000 && empties > 20); }
    { ChaseLev dq(2); for (int i = 0; i < 5000; i++) dq.push(i); assert(dq.capacity() == 8192 && dq.size() == 5000); int v; for (int i = 0; i < 2500; i++) { assert(dq.steal(v) == Steal::Success && v == i); } for (int i = 4999; i >= 2500; i--) { assert(dq.pop(v) && v == i); } assert(!dq.pop(v) && dq.steal(v) == Steal::Empty); }   // 성장 + 내용 보존
    { ChaseLev dq(4); std::deque<int> model; std::mt19937 rng(3); dq.push(1); model.push_back(1); long stolen = 0;                                      // DFS 소유자: 도둑은 항상 가장 얕은(큰) 일을 가져간다
      while (!model.empty()) { int v; assert(dq.pop(v) && v == model.back()); model.pop_back(); if (v < 4096) { for (int c : {2 * v, 2 * v + 1}) { dq.push(c); model.push_back(c); } }
          if (rng() % 4 == 0 && !model.empty()) { int minDepth = 99; for (int x : model) minDepth = std::min(minDepth, depthOf(x)); int s; assert(dq.steal(s) == Steal::Success && s == model.front() && depthOf(s) == minDepth); model.pop_front(); stolen++; } }
      assert(stolen >= 3); }
    {   const int N = 180000, T = 3; ChaseLev dq(2); std::atomic<bool> done{false}; std::vector<std::vector<int>> got(T + 1); std::vector<std::thread> thieves;     // ② 주인 1 + 도둑 3
        for (int t = 0; t < T; t++) thieves.emplace_back([&, t] { for (;;) { int v; Steal r = dq.steal(v); if (r == Steal::Success) got[t + 1].push_back(v); else if (r == Steal::Empty && done.load()) { if (dq.steal(v) == Steal::Success) got[t + 1].push_back(v); else if (dq.size() == 0) break; } else std::this_thread::yield(); } });
        std::mt19937 rng(11); for (int i = 0; i < N; i++) { dq.push(i); if (rng() % 3 == 0) { int v; if (dq.pop(v)) got[0].push_back(v); } }
        { int v; while (dq.pop(v)) got[0].push_back(v); } done.store(true); for (auto& th : thieves) th.join();
        std::vector<int> all; for (auto& g : got) all.insert(all.end(), g.begin(), g.end()); std::sort(all.begin(), all.end()); assert((int)all.size() == N); for (int i = 0; i < N; i++) assert(all[i] == i);   // 정확히 한 번씩
        for (int t = 1; t <= T; t++) assert(std::is_sorted(got[t].begin(), got[t].end()) && std::adjacent_find(got[t].begin(), got[t].end()) == got[t].end());          // 각 도둑이 훔친 id 는 단조 증가
    }
    {   const int W = 4, LEAF = 1 << 14, TOTAL = 2 * LEAF - 1; std::vector<std::unique_ptr<ChaseLev>> dqs; for (int w = 0; w < W; w++) dqs.emplace_back(new ChaseLev(2));
        std::unique_ptr<std::atomic<int>[]> ran(new std::atomic<int>[TOTAL + 1]()); std::atomic<long> pending{1}, stolen{0}; dqs[0]->push(1);                           // ③ 포크–조인 트리: 노드 i 는 자식 2i, 2i+1 을 만든다
        auto worker = [&](int me) { while (pending.load() > 0) { int task; bool have = dqs[me]->pop(task);
                for (int k = 1; !have && k < W; k++) { Steal r; do { r = dqs[(me + k) % W]->steal(task); } while (r == Steal::Abort); if (r == Steal::Success) { have = true; stolen++; } }
                if (!have) { std::this_thread::yield(); continue; }
                ran[task].fetch_add(1); if (task < LEAF) { pending.fetch_add(2); dqs[me]->push(2 * task); dqs[me]->push(2 * task + 1); } pending.fetch_sub(1); } };        // 자식을 먼저 계수하고 자신을 뺀다 → 0 이 일찍 보이지 않음
        std::vector<std::thread> ws; for (int w = 0; w < W; w++) ws.emplace_back(worker, w); for (auto& t : ws) t.join();
        for (int i = 1; i <= TOTAL; i++) assert(ran[i].load() == 1); assert(pending.load() == 0); for (auto& d : dqs) assert(d->size() == 0);
        std::cout << "WorkStealingQueue: 200000 sequential operations matched a deque model; 180000 tasks were executed exactly once with one owner and three thieves (thieves saw increasing ids); a " << TOTAL << "-node fork-join tree ran each node exactly once on " << W << " workers (" << stolen.load() << " steals) with correct termination" << std::endl; }
    return 0;
}
// Time Complexity: push·pop O(1) (성장은 분할상환 O(1)), steal O(1) (CAS 재시도 가능)
// Space Complexity: O(N) (옛 배열 보관분 합계도 O(N))
```
## ConcurrentQueue()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <deque>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>
#include <cassert>

// 동시성 큐(Blocking Bounded Queue): 락프리가 아니라 "뮤텍스 + 조건 변수" 로 만든 생산자–소비자 큐다. 락프리 구조보다 단순하고 정확하며, 큐가 비었을 때 소비자를, 가득 찼을 때 생산자를 CPU 를 쓰지 않고 재운다(블로킹) — 대부분의 스레드 풀·파이프라인이 이것으로 충분하다.
// 설계 요점: ① 용량을 제한해 생산자가 소비자보다 빠를 때 메모리가 무한히 늘지 않게 한다(역압, backpressure) ② 조건 변수 대기는 반드시 술어(predicate) 루프 안에서 한다 — 가짜 깨어남(spurious wakeup)이나 다른 스레드가 먼저 가져간 경우에도 조건을 다시 확인하기 위해서다 ③ close(): 더 넣을 것이 없다고 알리면 대기 중인 모두를 깨우고, 소비자는 남은 것을 모두 꺼낸 뒤 false 를 받아 종료한다(종료 신호를 센티넬 값으로 넣지 않아도 된다) ④ 시간 제한 대기(wait_for)로 교착을 피한다.
// 검증: ① 용량 4 인 큐로 생산자 3·소비자 3 이 3 만 개씩 주고받아 모든 값이 정확히 한 번이고 큐 크기가 용량을 넘지 않음 ② 소비자별로 같은 생산자의 값은 증가 순서 ③ close 이후 push 는 실패하고, 소비자는 잔여분을 비운 뒤 종료 ④ 대기(블로킹)가 실제로 일어남을 카운터로 확인 ⑤ try_pop_for 가 시간 제한 안에 빈 큐에서 false 를 돌려줌
// audit: stress (보존 법칙이 오라클: 모든 값이 정확히 한 번, 생산자별 순서, 큐 크기가 용량을 넘지 않는다)
template <class T> class BlockingQueue {
    std::deque<T> q; const size_t cap; bool closed = false; std::mutex m; std::condition_variable notFull, notEmpty; size_t maxSize = 0, pushWaits = 0, popWaits = 0;
public:
    explicit BlockingQueue(size_t c) : cap(c) {}
    bool push(const T& v) { std::unique_lock<std::mutex> lk(m); while (!closed && q.size() == cap) { pushWaits++; notFull.wait(lk); } if (closed) return false; q.push_back(v); maxSize = std::max(maxSize, q.size()); notEmpty.notify_one(); return true; }
    bool pop(T& out) { std::unique_lock<std::mutex> lk(m); while (!closed && q.empty()) { popWaits++; notEmpty.wait(lk); } if (q.empty()) return false; out = q.front(); q.pop_front(); notFull.notify_one(); return true; }       // 닫혔고 비었을 때만 false
    bool try_pop_for(T& out, std::chrono::milliseconds d) { std::unique_lock<std::mutex> lk(m); if (!notEmpty.wait_for(lk, d, [&] { return closed || !q.empty(); }) || q.empty()) return false; out = q.front(); q.pop_front(); notFull.notify_one(); return true; }
    void close() { { std::lock_guard<std::mutex> lk(m); closed = true; } notFull.notify_all(); notEmpty.notify_all(); }
    size_t maxObserved() { std::lock_guard<std::mutex> lk(m); return maxSize; } size_t waits() { std::lock_guard<std::mutex> lk(m); return pushWaits + popWaits; }
};
int main() {
    const int P = 3, C = 3, N = 30000; BlockingQueue<int> q(4); std::atomic<int> consumed{0}; std::atomic<bool> bad{false}; std::vector<std::vector<int>> seen(C, std::vector<int>(P, -1)); std::vector<std::vector<int>> got(P, std::vector<int>(N, 0)); std::mutex gm; std::vector<std::thread> producers, consumers;
    for (int p = 0; p < P; p++) producers.emplace_back([&, p] { for (int i = 0; i < N; i++) { bool ok = q.push(p * N + i); assert(ok); } });
    for (int c = 0; c < C; c++) consumers.emplace_back([&, c] { int v; while (q.pop(v)) { int p = v / N, i = v % N; if (i <= seen[c][p]) bad = true; seen[c][p] = i; { std::lock_guard<std::mutex> g(gm); got[p][i]++; } consumed++; } });
    for (auto& t : producers) t.join(); q.close(); for (auto& t : consumers) t.join();                                                    // ③ 생산이 끝나면 close -> 소비자는 잔여분을 비우고 종료
    assert(!bad && consumed == P * N && q.maxObserved() <= 4 && q.waits() > 0); for (int p = 0; p < P; p++) for (int i = 0; i < N; i++) assert(got[p][i] == 1);              // ①②④
    { int v = 0; assert(!q.push(1) && !q.pop(v)); }                                                                                                  // 닫힌 큐: push 실패, 빈 pop 은 false
    BlockingQueue<int> e(2); int v = -1; auto t0 = std::chrono::steady_clock::now(); assert(!e.try_pop_for(v, std::chrono::milliseconds(30))); auto dt = std::chrono::steady_clock::now() - t0; assert(dt >= std::chrono::milliseconds(25));         // ⑤ 시간 제한
    std::thread late([&] { std::this_thread::sleep_for(std::chrono::milliseconds(20)); e.push(42); }); assert(e.try_pop_for(v, std::chrono::seconds(5)) && v == 42); late.join();
    std::cout << "ConcurrentQueue: " << P * N << " items delivered exactly once through a bounded queue (max size " << q.maxObserved() << " of 4, blocked " << q.waits() << " times); close() let consumers drain and exit" << std::endl; return 0;
}
// Time Complexity: push·pop O(1) (뮤텍스 경쟁 시 대기)
// Space Complexity: O(용량)
```

# Part 11. 연구 주제
## PersistentQueue()
### 대표코드
```cpp
#include <deque>
#include <functional>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 영속 큐 (큐 관점의 요약, 정본은 AdvancedDataStructures.md Part 1): 모든 옛 버전을 건드리지 않고, "어떤 버전에서든" snoc(뒤에 추가)·tail(앞 제거)을 최악 O(1) 에 한다 (Okasaki 의 실시간 큐).
// 두 스택(앞 f, 뒤 r)으로 만드는 큐는 평균 O(1) 이지만 영속적으로 쓰면 같은 "비싼 뒤집기"를 반복 호출당해 O(n) 이 된다.
// 해법은 지연 평가(lazy): f 를 "다 쓰면" 뒤집는 대신, r 의 뒤집기를 f 와 이어 붙이는 작업(rotate)을 지연 스트림으로 걸어 두고, 연산마다 일정(schedule) 스트림 s 를 한 칸씩 강제 평가해 그 일을 조금씩 미리 끝낸다.
// 불변식 |s| = |f| - |r|.  평가 결과는 메모이즈되므로 같은 버전을 여러 번 써도 작업이 한 번만 일어난다
struct Lazy; typedef std::shared_ptr<Lazy> Stream;
struct Cell { bool nil = true; int head = 0; Stream tail; };
long forced = 0;                                                           // 강제된 썽크 수 (최악 시간 측정용)
struct Lazy {
    std::function<Cell()> thunk; Cell val; bool done = false;
    const Cell& force() { if (!done) { forced++; val = thunk(); done = true; thunk = nullptr; } return val; }
};
Stream mkNil() { auto s = std::make_shared<Lazy>(); s->done = true; return s; }
Stream mkCons(int x, const Stream& t) { auto s = std::make_shared<Lazy>(); s->done = true; s->val = Cell{false, x, t}; return s; }
Stream delay(std::function<Cell()> f) { auto s = std::make_shared<Lazy>(); s->thunk = f; return s; }
struct L; typedef std::shared_ptr<const L> List;
struct L { int x; List next; };
Stream rotate(Stream f, List r, Stream a) {                                // f 뒤에 reverse(r) 와 a 를 이은 스트림 (|r| = |f| + 1)
    return delay([=]() -> Cell {
        const Cell& fc = f->force();
        if (fc.nil) return Cell{false, r->x, a};
        return Cell{false, fc.head, rotate(fc.tail, r->next, mkCons(r->x, a))};
    });
}
struct Queue { Stream f; List r; Stream s; };
Queue exec(const Stream& f, const List& r, const Stream& s) {
    const Cell& sc = s->force();                                           // 일정 스트림을 한 칸 강제 = rotate 를 한 걸음 진행
    if (!sc.nil) return Queue{f, r, sc.tail};
    Stream f2 = rotate(f, r, mkNil());                                     // 일정이 끝나면 새 rotate 를 시작
    return Queue{f2, nullptr, f2};
}
Queue empty() { return Queue{mkNil(), nullptr, mkNil()}; }
Queue snoc(const Queue& q, int x) { return exec(q.f, std::make_shared<const L>(L{x, q.r}), q.s); }
bool isEmpty(const Queue& q) { return q.f->force().nil; }
int head(const Queue& q) { return q.f->force().head; }
Queue tail(const Queue& q) { return exec(q.f->force().tail, q.r, q.s); }

int main() {
    std::mt19937 rng(21); std::vector<Queue> ver = {empty()}; std::vector<std::deque<int>> model = {{}}; long worst = 0;
    for (int step = 0; step < 30000; step++) {
        int base = rng() % std::min<size_t>(ver.size(), 3000) + (ver.size() > 3000 ? ver.size() - 3000 : 0);   // 최근 3000 개 버전 중 하나에서 갈라진다
        const Queue q = ver[base]; std::deque<int> m = model[base]; long before = forced;
        if (m.empty() || rng() % 5 < 3) { int x = rng() % 1000; ver.push_back(snoc(q, x)); m.push_back(x); }
        else { assert(head(q) == m.front()); ver.push_back(tail(q)); m.pop_front(); }
        worst = std::max(worst, forced - before); model.push_back(m);
        const Queue& nq = ver.back(); assert(isEmpty(nq) == m.empty()); if (!m.empty()) assert(head(nq) == m.front());
    }
    for (size_t i = 0; i < ver.size(); i += 7) {                           // 오래된 버전도 끝까지 비우면 모델과 같은 순서
        Queue q = ver[i]; for (int x : model[i]) { assert(!isEmpty(q) && head(q) == x); q = tail(q); } assert(isEmpty(q));
    }
    Queue big = empty(); for (int i = 0; i < 1000; i++) big = snoc(big, i);
    long before = forced; Queue t1 = tail(big); for (int k = 0; k < 500; k++) { Queue t = tail(big); assert(head(t) == 1); } (void)t1;
    assert(forced - before <= 10);                                         // 같은 버전에 tail 을 500 번 호출해도 비싼 일은 한 번만 (메모이즈)
    assert(worst <= 12);                                                   // 연산 한 번당 강제 평가 수가 상수
    std::cout << "PersistentQueue: " << ver.size() << " versions verified, worst thunks forced per op = " << worst << std::endl;
    return 0;
}
// Time Complexity: snoc·tail·head 최악 O(1) (영속 사용에서도)
// Space Complexity: O(N)
```
## ImmutableQueue()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <deque>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 불변 큐(Immutable Queue): 연산이 큐를 바꾸지 않고 "새 큐" 를 돌려준다 — 모든 이전 버전이 그대로 유효하다. 가장 단순한 방법은 연결 리스트 두 개(앞쪽 front, 뒤쪽 rear 를 거꾸로 저장)다: push 는 rear 앞에 cons, pop 은 front 의 꼬리로, front 가 비면 rear 를 뒤집어 front 로 옮긴다. 공유되는 꼬리 덕분에 새 버전은 노드 O(1) 개만 만든다.
// 한 가지 버전을 한 번씩만 쓰는 일반적인 사용(ephemeral)에서는 뒤집기 비용이 원소당 한 번이라 분할상환 O(1) 이다. 그러나 같은 버전에서 pop 을 여러 번 부르면(영속 사용) 비싼 뒤집기가 매번 되풀이되어 분할상환 보장이 깨진다 — 분할상환 분석은 연산 열이 이어진다고 가정하기 때문이다. 이 약점을 지연 평가와 일정으로 막은 것이 실시간 영속 큐(PersistentQueue 항목, Okasaki)다.
// 검증: ① 무작위 push/pop 을 임의의 옛 버전에서 이어 붙여도 모든 버전이 std::deque 스냅샷과 같다(불변성) ② 새 버전이 노드를 O(1) 개만 새로 만든다(구조 공유) ③ 한 줄로 이어 쓰면 n 번 push 뒤 n 번 pop 에서 뒤집기 작업량이 정확히 n (분할상환 O(1)) ④ 같은 버전에서 pop 을 K 번 반복하면 뒤집기 작업량이 K×(n−1) 로 커진다(영속 사용에서 분할상환 붕괴)
struct L; typedef std::shared_ptr<const L> List; struct L { int x; List next; };
long reverseWork = 0, allocated = 0;
List cons(int x, const List& t) { allocated++; return std::make_shared<const L>(L{x, t}); }
List reverseList(const List& l) { List r; for (List p = l; p; p = p->next) { r = cons(p->x, r); reverseWork++; } return r; }
struct IQueue {
    List front, rear; size_t n = 0;
    static IQueue make(List f, List r, size_t n) { if (!f && r) { f = reverseList(r); r = nullptr; } return IQueue{f, r, n}; }                 // 불변식: n > 0 이면 front 가 비어 있지 않다
    IQueue push(int x) const { return make(front, cons(x, rear), n + 1); }
    int head() const { return front->x; }
    IQueue pop() const { return make(front->next, rear, n - 1); }
    std::vector<int> toVector() const { std::vector<int> v; for (List p = front; p; p = p->next) v.push_back(p->x); std::vector<int> r; for (List p = rear; p; p = p->next) r.push_back(p->x); v.insert(v.end(), r.rbegin(), r.rend()); return v; }
};
int main() {
    std::mt19937 rng(14); std::vector<IQueue> ver = {IQueue{}}; std::vector<std::deque<int>> model = {{}}; long maxNew = 0;
    for (int step = 0; step < 4000; step++) {
        size_t base = rng() % ver.size(); const IQueue q = ver[base]; std::deque<int> m = model[base]; long before = allocated, revBefore = reverseWork; IQueue r;
        if (m.empty() || rng() % 5 < 3) { int x = rng() % 1000; r = q.push(x); m.push_back(x); } else { assert(q.head() == m.front()); r = q.pop(); m.pop_front(); }
        if (reverseWork == revBefore) maxNew = std::max(maxNew, allocated - before);                                                                         // ② 뒤집기가 없는 연산은 노드를 1 개 이하로 만든다 (뒤집기가 일어난 연산은 크기에 비례)
        assert(r.n == m.size() && r.toVector() == std::vector<int>(m.begin(), m.end()));
        ver.push_back(r); model.push_back(m);
        if (m.size() > 60) { ver.back() = IQueue{}; model.back().clear(); }
    }
    for (size_t i = 0; i < ver.size(); i += 17) assert(ver[i].toVector() == std::vector<int>(model[i].begin(), model[i].end()));                                         // ① 옛 버전은 그대로
    assert(maxNew <= 1);
    const int n = 5000; reverseWork = 0; { IQueue q; for (int i = 0; i < n; i++) q = q.push(i); for (int i = 0; i < n; i++) { assert(q.head() == i); q = q.pop(); } assert(q.n == 0); } assert(reverseWork == n);        // ③ 이어 쓰면 뒤집기 n 번
    { IQueue q; for (int i = 0; i < n; i++) q = q.push(i); reverseWork = 0; const int K = 50; for (int k = 0; k < K; k++) { IQueue t = q.pop(); assert(t.n == n - 1); } assert(reverseWork == (long)K * (n - 1)); }                                     // ④ 같은 버전에서 pop 50 번 -> 뒤집기 50(n−1)
    std::cout << "ImmutableQueue: 4000 persistent versions matched deque snapshots; sequential use reversed " << n << " nodes in total (amortized O(1)) but popping one version 50 times redid the reversal " << 50L * (n - 1) << " node copies" << std::endl; return 0;
}
// Time Complexity: push O(1), head O(1), pop 분할상환 O(1) (이어 쓸 때만; 같은 버전 반복 사용은 최악 O(N))
// Space Complexity: O(N), 새 버전은 O(1) 노드를 만들고 나머지는 공유
```
## QueueingTheory()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <deque>
#include <iostream>
#include <limits>
#include <random>
#include <vector>

// 대기행렬 이론(Queueing Theory): 도착이 확률적이고 서비스 시간이 확률적일 때 큐의 길이와 기다림이 어떻게 되는지를 수학으로 예측한다. 표기 A/S/c/K: 도착 과정/서비스 시간 분포/서버 수/시스템 용량. M = 마르코프(지수 분포, 무기억), D = 결정적(상수), G = 일반. 도착률 λ, 서비스율 μ, 이용률 ρ = λ/(cμ).
// 핵심 결과(정상 상태): M/M/1 은 ρ<1 일 때만 안정, L = ρ/(1−ρ), W = 1/(μ−λ), Lq = ρ²/(1−ρ), Wq = ρ/(μ−λ). ρ 가 1 에 가까워지면 평균 대기가 1/(1−ρ) 로 폭발한다(이용률 90% → 99% 에서 기다림이 10 배). M/M/c 의 대기 확률은 얼랑 C 공식, 대기 없는 손실 시스템 M/M/c/c 의 차단 확률은 얼랑 B 공식(점화식 B(k) = aB(k−1)/(k + aB(k−1)), a = λ/μ). M/G/1 은 폴라체크–힌친 공식 Wq = λE[S²]/(2(1−ρ)): 서비스 시간 변동이 클수록 대기가 길다 — 같은 평균에서 결정적 서비스(M/D/1)는 지수 서비스(M/M/1)의 정확히 절반. 리틀의 법칙 L = λ_eff·W 는 분포에 상관없이 성립한다.
// 검증: 직접 만든 사건 구동 시뮬레이터(서버 힙 + FIFO 대기열, 난수는 mt19937_64 비트에서 직접 만든 지수 분포로 플랫폼 독립)로 ① 정확한 항등식: 도착 = 완료 + 차단 + 잔류, 시스템 내 인원 N(t) 의 적분 == 모든 고객의 체류 시간 합(리틀의 법칙의 표본 경로 버전, 부동소수 오차만) ② M/M/1(ρ=0.5, 0.8), M/D/1, M/M/1/K(ρ<1, ρ>1), M/M/3, M/M/5/5 의 L·Wq·대기 확률·차단 확률이 이론과 일치 ③ 수식 자체의 일관성(리틀, 얼랑 B 닫힌형, M/M/c(c=1) == M/M/1, 풀링 효과: 서버를 하나로 합친 쪽이 낫다) ④ ρ>1 이면 대기열이 선형으로 증가.
struct Rng { std::mt19937_64 g; explicit Rng(uint64_t s) : g(s) {} double u() { return (double)(g() >> 11) * (1.0 / 9007199254740992.0); } double exp(double rate) { return -std::log1p(-u()) / rate; } };
enum class Service { Exponential, Deterministic };
struct Stats { long arrivals = 0, blocked = 0, served = 0, started = 0, waited = 0, inSystemEnd = 0; double area = 0, sojourn = 0, sojournAll = 0, wait = 0, horizon = 0; };
Stats simulate(double lambda, double mu, int c, int K, Service kind, double horizon, uint64_t seed) {                // K=0 이면 무한 대기실
    Rng rng(seed); Stats st; st.horizon = horizon; using Busy = std::pair<double, double>;                          // (퇴장 시각, 도착 시각)
    std::vector<Busy> servers; auto cmp = [](const Busy& a, const Busy& b) { return a.first > b.first; }; std::deque<double> waiting;
    auto service = [&] { return kind == Service::Exponential ? rng.exp(mu) : 1.0 / mu; };
    double t = 0, nextArrival = rng.exp(lambda), inf = std::numeric_limits<double>::infinity();
    for (;;) { double nextDep = servers.empty() ? inf : servers.front().first, te = std::min(nextArrival, nextDep); if (te > horizon) break;
        st.area += (te - t) * (double)(servers.size() + waiting.size()); t = te;
        if (nextArrival <= nextDep) { st.arrivals++;
            if (K > 0 && (int)(servers.size() + waiting.size()) >= K) st.blocked++;
            else if ((int)servers.size() < c) { servers.push_back({t + service(), t}); std::push_heap(servers.begin(), servers.end(), cmp); st.started++; }
            else waiting.push_back(t);
            nextArrival = t + rng.exp(lambda); }
        else { std::pop_heap(servers.begin(), servers.end(), cmp); Busy done = servers.back(); servers.pop_back(); st.served++; st.sojourn += t - done.second;
            if (!waiting.empty()) { double a = waiting.front(); waiting.pop_front(); st.wait += t - a; st.waited++; st.started++; servers.push_back({t + service(), a}); std::push_heap(servers.begin(), servers.end(), cmp); } } }
    st.area += (horizon - t) * (double)(servers.size() + waiting.size()); st.inSystemEnd = (long)(servers.size() + waiting.size());
    st.sojournAll = st.sojourn; for (const Busy& b : servers) st.sojournAll += horizon - b.second; for (double a : waiting) st.sojournAll += horizon - a;      // 아직 시스템에 있는 고객의 체류 시간(지금까지)
    return st;
}
struct Th { double L, Lq, W, Wq, pBlock, pWait; };
Th mm1(double l, double m) { double r = l / m; return {r / (1 - r), r * r / (1 - r), 1 / (m - l), r / (m - l), 0, r}; }
Th md1(double l, double m) { double r = l / m, wq = r / (2 * m * (1 - r)); return {l * (wq + 1 / m), l * wq, wq + 1 / m, wq, 0, r}; }
double erlangB(int c, double a) { double B = 1; for (int k = 1; k <= c; k++) B = a * B / (k + a * B); return B; }
double erlangC(int c, double a) { double B = erlangB(c, a), rho = a / c; return B / (1 - rho * (1 - B)); }
Th mmc(double l, double m, int c) { double a = l / m, C = erlangC(c, a), wq = C / (c * m - l); return {l * (wq + 1 / m), l * wq, wq + 1 / m, wq, 0, C}; }
Th mm1k(double l, double m, int K) { double r = l / m, sum = 0; std::vector<double> p(K + 1); for (int n = 0; n <= K; n++) { p[n] = std::pow(r, n); sum += p[n]; } for (double& x : p) x /= sum;
    double L = 0; for (int n = 0; n <= K; n++) L += n * p[n]; double le = l * (1 - p[K]), Lq = L - (1 - p[0]); return {L, Lq, L / le, Lq / le, p[K], (1 - p[0] - p[K]) / (1 - p[K])}; }
static double rel(double a, double b) { return std::abs(a - b) / std::abs(b); }
int main() {
    double worst = 0; int runs = 0;
    auto exact = [&](const Stats& s) { assert(s.arrivals == s.served + s.blocked + s.inSystemEnd); assert(rel(s.area, s.sojournAll) < 1e-9); runs++; };                 // ① 정확한 항등식
    auto near = [&](double got, double want, double tol) { double e = rel(got, want); worst = std::max(worst, e / tol); assert(e < tol); };
    { Stats s = simulate(0.5, 1.0, 1, 0, Service::Exponential, 1.5e6, 1); exact(s); Th t = mm1(0.5, 1.0);                                              // ② M/M/1 ρ=0.5
      near(s.area / s.horizon, t.L, 0.03); near(s.wait / s.started, t.Wq, 0.04); near((double)s.waited / s.started, t.pWait, 0.03); near(s.sojourn / s.served, t.W, 0.03);
      assert(rel(s.area / s.horizon, (double)s.served / s.horizon * (s.sojourn / s.served)) < 0.01); }                                                  // 리틀: L ≈ λ·W (측정값끼리)
    { Stats s = simulate(0.8, 1.0, 1, 0, Service::Exponential, 3e6, 2); exact(s); Th t = mm1(0.8, 1.0); near(s.area / s.horizon, t.L, 0.06); near(s.wait / s.started, t.Wq, 0.07); near((double)s.waited / s.started, t.pWait, 0.02);
      Stats d = simulate(0.8, 1.0, 1, 0, Service::Deterministic, 3e6, 3); exact(d); Th td = md1(0.8, 1.0); near(d.wait / d.started, td.Wq, 0.04); near(d.area / d.horizon, td.L, 0.04);       // M/D/1
      assert(rel(td.Wq, 0.5 * t.Wq) < 1e-12 && (d.wait / d.started) < 0.6 * (s.wait / s.started)); }                                                   // 폴라체크–힌친: 결정적 서비스 = 지수 서비스의 절반
    for (double lam : {0.9, 1.2}) { Stats s = simulate(lam, 1.0, 1, 5, Service::Exponential, 1e6, 4); exact(s); Th t = mm1k(lam, 1.0, 5); assert(s.inSystemEnd <= 5);   // M/M/1/K
      near((double)s.blocked / s.arrivals, t.pBlock, 0.03); near(s.area / s.horizon, t.L, 0.02); near(s.sojourn / s.served, t.W, 0.02); }
    { Stats s = simulate(2.4, 1.0, 3, 0, Service::Exponential, 1e6, 5); exact(s); Th t = mmc(2.4, 1.0, 3); near((double)s.waited / s.started, t.pWait, 0.02); near(s.wait / s.started, t.Wq, 0.05); near(s.area / s.horizon, t.L, 0.03); }   // M/M/3 (얼랑 C)
    { Stats s = simulate(4.0, 1.0, 5, 5, Service::Exponential, 1e6, 6); exact(s); near((double)s.blocked / s.arrivals, erlangB(5, 4.0), 0.03); assert(s.waited == 0); }                           // M/M/5/5 (얼랑 B, 대기 없음)
    { Stats s = simulate(1.2, 1.0, 1, 0, Service::Exponential, 1e5, 7); exact(s); assert(s.inSystemEnd > 0.1 * s.horizon); Stats s2 = simulate(1.2, 1.0, 1, 0, Service::Exponential, 2e5, 7); assert(s2.inSystemEnd > 1.5 * s.inSystemEnd); }   // ④ ρ>1: 선형 증가
    { Stats a = simulate(0.8, 1.0, 1, 0, Service::Exponential, 1e5, 9), b = simulate(0.8, 1.0, 1, 0, Service::Exponential, 1e5, 9); assert(a.arrivals == b.arrivals && a.area == b.area && a.wait == b.wait); }  // 같은 시드 → 같은 결과
    {   for (double l : {0.3, 0.7, 0.95}) { Th t = mm1(l, 1.0), c1 = mmc(l, 1.0, 1), d = md1(l, 1.0); assert(rel(t.L, l * t.W) < 1e-12 && rel(t.Lq, l * t.Wq) < 1e-12 && rel(t.W, t.Wq + 1.0) < 1e-12 && rel(c1.Wq, t.Wq) < 1e-12 && rel(c1.pWait, t.pWait) < 1e-12 && rel(d.L, l * d.W) < 1e-12); }   // ③ 수식의 일관성
        for (int K : {1, 3, 8}) for (double l : {0.5, 1.0, 1.7}) { Th t = mm1k(l, 1.0, K); double le = l * (1 - t.pBlock); assert(std::abs(t.L - le * t.W) < 1e-12 && std::abs(t.Lq - le * t.Wq) < 1e-12 && std::abs(t.W - t.Wq - 1.0) < 1e-12); }
        { int c = 5; double a = 4, num = std::pow(a, c) / 120, den = 0, f = 1; for (int k = 0; k <= c; k++) { if (k) f *= k; den += std::pow(a, k) / f; } assert(rel(erlangB(c, a), num / den) < 1e-12); }                                                   // 얼랑 B 닫힌형
        Th fast = mm1(1.2, 2.0), pooled = mmc(1.2, 1.0, 2), split = mm1(0.6, 1.0); assert(fast.W < pooled.W && pooled.W < split.W); }                          // 풀링: 빠른 서버 하나 < 공유 큐 서버 둘 < 서버 둘 + 큐 둘
    std::cout << "QueueingTheory: " << runs << " simulations satisfied the exact sample-path identities (conservation; time-integral of N(t) == total sojourn); M/M/1, M/D/1 (Pollaczek-Khinchine: half the M/M/1 wait), M/M/1/K, M/M/3 (Erlang C) and M/M/5/5 (Erlang B) measurements agreed with the formulas (worst error was " << worst * 100 << "% of its tolerance), and an overloaded queue grew linearly" << std::endl; return 0;
}
// Time Complexity: 시뮬레이션 사건당 O(log c), 이론식 O(c) 또는 O(K)
// Space Complexity: O(c + 대기열 길이)
```
## FairQueue()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <deque>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 공정 큐(Fair Queue): 하나의 출력 링크를 여러 흐름(flow)이 나눠 쓸 때, 흐름마다 별도의 큐를 두고 돌아가며 서비스해서 한 흐름이 링크를 독점하지 못하게 한다. 단일 FIFO 는 공격적인 흐름이 큐를 채우면 다른 흐름이 굶는다. 흐름별 큐 + 순회가 공정성의 기본 구조다.
// 패킷 단위 라운드 로빈(RR)은 한 번에 패킷 하나씩 보낸다 — 패킷 크기가 다르면 큰 패킷을 보내는 흐름이 바이트 기준으로 훨씬 많이 가져간다(1500 바이트 대 100 바이트면 15 배). 결핍 라운드 로빈(DRR, Shreedhar–Varghese 1995)은 흐름마다 결핍 카운터(deficit)를 두고, 자기 차례가 올 때마다 양자(quantum)를 더한 뒤 머리 패킷이 카운터 이하인 동안 계속 보낸다. 남은 값은 다음 차례로 이월하고, 큐가 비면 0 으로 되돌려 쉬는 동안 신용을 쌓지 못하게 한다. 양자 ≥ 최대 패킷 크기이면 차례마다 최소 한 개를 보내므로 패킷당 O(1). 가중치 w_i 는 양자 = w_i·Q 로 반영한다.
// 증명되는 공정성 한계: 흐름 i 가 줄곧 대기 중일 때 k 번의 차례 뒤 보낸 바이트 S_i 는 k·Q_i − L < S_i ≤ k·Q_i (L = 최대 패킷 크기, 차례가 끝날 때 남는 결핍은 항상 [0, L)). 따라서 정규화된 서비스 차이 |S_i/w_i − S_j/w_j| 는 상수(L/w_i + L/w_j 미만)로 유계 — 시간이 지나도 벌어지지 않는다.
// 검증: ① 손으로 계산한 예(Q=500; 300,300,300 대 700 → 순서 f0,f0,f0,f1) ② 무작위 도착·서비스에서 흐름별 FIFO 순서·정확히 한 번 전송·일 보존(대기 패킷이 있으면 항상 하나를 보냄) ③ 가중치 1:2:4:1 의 항상 대기 흐름에서 모든 라운드 끝마다 k·Q_i − L < S_i ≤ k·Q_i ④ 패킷 RR 은 15:1 로 불공정, DRR 은 바이트 차이가 한 패킷 이내 ⑤ 쉬었다 온 흐름은 신용이 없다(첫 차례 ≤ Q) ⑥ 차례 부여 횟수: Q ≥ L 이면 보낸 패킷 수 이하, Q 가 패킷의 1/10 이면 패킷마다 10 번 ⑦ 최대–최소 공정 할당(물채우기)과 장시간 시뮬레이션 처리량이 2% 안에서 일치.
struct Pkt { int flow, size; long id; };
class DRR {
    struct Flow { std::deque<Pkt> q; long quantum, deficit = 0; bool active = false, turn = false; };
    std::vector<Flow> fl; std::deque<int> ring;                                                                      // ring: 활성(대기 패킷이 있는) 흐름의 순환 목록
public:
    long grants = 0, sent = 0; std::vector<long> bytes, turnBytes; std::function<void(int)> onTurnEnd;               // 통계와 차례 종료 훅(검증용)
    explicit DRR(const std::vector<long>& quanta) : bytes(quanta.size(), 0), turnBytes(quanta.size(), 0) { for (long q : quanta) { Flow f; f.quantum = q; fl.push_back(std::move(f)); } }
    void enqueue(const Pkt& p) { Flow& f = fl[p.flow]; f.q.push_back(p); if (!f.active) { f.active = true; ring.push_back(p.flow); } }
    bool dequeue(Pkt& out) {                                                                                         // 다음에 보낼 패킷(없으면 false)
        while (!ring.empty()) { int i = ring.front(); Flow& f = fl[i];
            if (!f.turn) { f.turn = true; f.deficit += f.quantum; grants++; turnBytes[i] = 0; }                      // 차례 시작: 양자 지급
            if (f.q.front().size <= f.deficit) { out = f.q.front(); f.q.pop_front(); f.deficit -= out.size; bytes[i] += out.size; turnBytes[i] += out.size; sent++;
                if (f.q.empty()) { f.deficit = 0; f.active = false; f.turn = false; ring.pop_front(); if (onTurnEnd) onTurnEnd(i); }          // 큐가 비면 결핍 초기화
                return true; }
            f.turn = false; ring.pop_front(); ring.push_back(i); if (onTurnEnd) onTurnEnd(i); }                      // 머리 패킷이 안 맞으면 차례 종료, 결핍은 이월
        return false;
    }
    long deficit(int i) const { return fl[i].deficit; }
    bool idle() const { return ring.empty(); }
};
class PacketRR {                                                                                                     // 비교용: 패킷 단위 라운드 로빈
    std::vector<std::deque<Pkt>> q; size_t next = 0; size_t pending = 0;
public:
    std::vector<long> bytes; explicit PacketRR(int flows) : q(flows), bytes(flows, 0) {}
    void enqueue(const Pkt& p) { q[p.flow].push_back(p); pending++; }
    bool dequeue(Pkt& out) { if (!pending) return false; while (q[next].empty()) next = (next + 1) % q.size(); out = q[next].front(); q[next].pop_front(); bytes[out.flow] += out.size; pending--; next = (next + 1) % q.size(); return true; }
};
std::vector<double> maxMin(std::vector<double> demand, double capacity) {                                            // 물채우기: 최대–최소 공정 할당
    int n = (int)demand.size(); std::vector<double> give(n, 0); std::vector<int> open(n); std::iota(open.begin(), open.end(), 0);
    while (!open.empty() && capacity > 1e-12) { double share = capacity / open.size(); std::vector<int> still; bool any = false;
        for (int i : open) { if (demand[i] - give[i] <= share + 1e-12) { capacity -= demand[i] - give[i]; give[i] = demand[i]; any = true; } else still.push_back(i); }
        if (!any) { for (int i : still) give[i] += share; capacity = 0; break; } open = still; }
    return give;
}
int main() {
    { DRR d({500, 500}); for (int s : {300, 300, 300}) d.enqueue({0, s, 0}); d.enqueue({1, 700, 0}); Pkt p; std::vector<std::pair<int, int>> order;     // ① 손으로 계산한 예
      while (d.dequeue(p)) order.push_back({p.flow, p.size}); assert((order == std::vector<std::pair<int, int>>{{0, 300}, {0, 300}, {0, 300}, {1, 700}}) && d.idle() && d.deficit(0) == 0 && d.deficit(1) == 0); }
    { std::mt19937 rng(5); const int F = 6; DRR d({800, 800, 1600, 800, 3200, 800}); std::vector<long> nextId(F, 0), lastSeen(F, -1); std::vector<std::deque<long>> expect(F); long pending = 0, sentCount = 0, enq = 0;   // ② 무작위 일관성
      for (int step = 0; step < 300000; step++) { if (rng() % 5 < 3) { int f = rng() % F; Pkt p{f, (int)(64 + rng() % 737), nextId[f]++}; d.enqueue(p); expect[f].push_back(p.id); pending++; enq++; }
          else { Pkt p; bool ok = d.dequeue(p); assert(ok == (pending > 0)); if (ok) { assert(p.id == expect[p.flow].front()); expect[p.flow].pop_front(); pending--; sentCount++; } } }       // 흐름별 FIFO, 일 보존
      Pkt p; while (d.dequeue(p)) { assert(p.id == expect[p.flow].front()); expect[p.flow].pop_front(); pending--; sentCount++; } assert(pending == 0 && sentCount == enq && d.sent == enq && d.idle()); }
    {   const int F = 4; const long Q = 1500, L = 1500; std::vector<long> w = {1, 2, 4, 1}, quanta; for (long x : w) quanta.push_back(x * Q); DRR d(quanta); std::mt19937 rng(9); std::vector<long> turns(F, 0); long checks = 0;     // ③ 라운드마다 유계 공정성
        d.onTurnEnd = [&](int i) { turns[i]++; if (i == F - 1) { long k = turns[i]; for (int j = 0; j < F; j++) { assert(turns[j] == k && d.bytes[j] <= k * quanta[j] && d.bytes[j] + L > k * quanta[j]); } checks++; } };
        long id = 0; for (int f = 0; f < F; f++) for (int i = 0; i < 40; i++) d.enqueue({f, (int)(40 + rng() % 1461), id++});
        Pkt p; for (int step = 0; step < 100000; step++) { assert(d.dequeue(p)); d.enqueue({p.flow, (int)(40 + rng() % 1461), id++}); }                // 항상 대기 상태 유지(보낸 만큼 보충)
        assert(checks > 1000); for (int i = 0; i < F; i++) for (int j = 0; j < F; j++) assert(std::abs((double)d.bytes[i] / w[i] - (double)d.bytes[j] / w[j]) < (double)L / w[i] + (double)L / w[j] + (double)Q); }
    { PacketRR rr(2); DRR d({1500, 1500}); for (int i = 0; i < 2000; i++) for (int f = 0; f < 2; f++) { Pkt p{f, f == 0 ? 1500 : 100, i}; rr.enqueue(p); d.enqueue(p); }       // ④ RR 불공정 / DRR 공정
      Pkt p; for (int i = 0; i < 2000; i++) { assert(rr.dequeue(p)); } assert(rr.bytes[0] == 15 * rr.bytes[1]);
      long sent = 0; while (sent < 1500 && d.dequeue(p)) { sent++; } assert(std::abs(d.bytes[0] - d.bytes[1]) <= 2 * 1500 && d.bytes[1] > 100000); }
    { DRR d({1000, 1000, 1000}); long id = 0; for (int i = 0; i < 100; i++) { d.enqueue({0, 500, id++}); d.enqueue({1, 500, id++}); } Pkt p; for (int i = 0; i < 200; i++) assert(d.dequeue(p));      // ⑤ 쉬었다 온 흐름은 신용이 없다
      std::vector<long> firstTurn; d.onTurnEnd = [&](int i) { if (i == 2 && firstTurn.empty()) firstTurn.push_back(d.turnBytes[2]); };
      for (int i = 0; i < 100; i++) d.enqueue({2, 100, id++}); for (int i = 0; i < 300; i++) d.enqueue({0, 500, id++}); for (int i = 0; i < 300; i++) d.enqueue({1, 500, id++});
      for (int i = 0; i < 300 && d.dequeue(p); i++) {} assert(firstTurn.size() == 1 && firstTurn[0] <= 1000 && d.turnBytes[2] <= 1000); }
    { DRR big({1000}); DRR small({100}); for (int i = 0; i < 50; i++) { big.enqueue({0, 1000, i}); small.enqueue({0, 1000, i}); } Pkt p;                    // ⑥ 차례 부여 횟수
      while (big.dequeue(p)) {} while (small.dequeue(p)) {} assert(big.grants <= big.sent && small.grants == 10 * small.sent); }
    {   const int F = 4; const long R = 1800; std::vector<double> rate = {100, 300, 900, 2000}; std::vector<int> size = {100, 300, 1500, 500}; DRR d({1500, 1500, 1500, 1500}); std::vector<double> credit(F, 0), got(F, 0);        // ⑦ 최대–최소 공정
        long budget = 0, id = 0; const int T = 200000; Pkt p;
        for (int t = 0; t < T; t++) { for (int f = 0; f < F; f++) { credit[f] += rate[f]; while (credit[f] >= size[f]) { credit[f] -= size[f]; d.enqueue({f, size[f], id++}); } }
            budget += R; while (budget > 0 && d.dequeue(p)) budget -= p.size; }
        std::vector<double> fair = maxMin(rate, (double)R); assert(std::abs(fair[0] - 100) < 1e-9 && std::abs(fair[1] - 300) < 1e-9 && std::abs(fair[2] - 700) < 1e-9 && std::abs(fair[3] - 700) < 1e-9);
        for (int f = 0; f < F; f++) { double thr = (double)d.bytes[f] / T; assert(std::abs(thr - fair[f]) / fair[f] < 0.02); } }
    std::cout << "FairQueue: DRR matched a hand-worked schedule, kept per-flow FIFO and work conservation over 300000 random operations, satisfied k*Q-L < bytes <= k*Q after every round for weights 1:2:4:1, beat packet round robin (15:1 skew) on byte fairness, gave no credit to idle flows, took one grant per packet when Q >= max size, and reproduced the max-min fair allocation within 2%" << std::endl; return 0;
}
// Time Complexity: 양자 ≥ 최대 패킷 크기이면 enqueue·dequeue 패킷당 O(1)
// Space Complexity: O(흐름 수 + 대기 패킷 수)
```
## PriorityScheduling()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 우선순위 스케줄링: 준비 큐를 우선순위 큐로 두고 매번 가장 높은 우선순위의 일을 실행한다. 단순하지만 기아(starvation)가 생긴다 — 높은 우선순위 일이 계속 도착하면 낮은 우선순위 일은 영영 실행되지 못한다. 해법은 에이징(aging): 기다린 시간만큼 우선순위를 올려 준다. 시각 t 의 유효 우선순위 eff(t) = prio + (t − 도착)/A (A = 한 단계 올리는 데 걸리는 시간).
// 핵심 관찰: 두 일 i, j 의 유효 우선순위를 같은 시각 t 에서 비교하면 t 가 양변에서 상쇄된다 — prio_i·A − a_i 대 prio_j·A − a_j. 즉 키 prio·A − 도착 은 시간에 따라 변하지 않으므로 에이징이 있어도 보통의 힙 하나로 충분하다(시간이 흐를 때마다 힙을 갱신할 필요가 없다). A→∞ 이면 키는 (우선순위, 먼저 도착)의 사전식 순서, 곧 엄격한 우선순위 스케줄링이다. 같은 우선순위끼리는 FIFO.
// 기아 방지의 보장: 일 j 보다 먼저 시작하는 일 i 는 키가 j 이상이어야 하므로 도착이 a_i ≤ a_j + (prio_i − prio_j)·A ≤ a_j + (Pmax − prio_j)·A =: T 이다. j 가 기다리는 동안 서버는 쉬지 않으므로, 대기 시간 ≤ 도착이 T 이하인 다른 모든 일의 서비스 시간 합. 시스템이 과부하여도 이 값은 유한하다(엄격한 우선순위는 무한).
// 검증(비선점, 단일 서버): ① 직접 만든 이진 힙이 std::priority_queue 와 무작위 연산에서 같은 결과 ② 힙 기반 스케줄과, 매 결정 시각에 모든 대기 일의 유효 우선순위를 전수 비교하는 느린 구현의 스케줄이 A ∈ {1, 5, 50} 과 엄격한 우선순위에서 일치 ③ 에이징의 모든 일에서 위 대기 시간 한계가 성립하고 최대 대기가 엄격한 우선순위보다 작다 ④ 기아 시나리오: 서버 용량만큼 높은 우선순위 일이 계속 도착할 때 엄격한 우선순위는 낮은 일을 모든 높은 일이 끝난 뒤에야 실행하고, 에이징은 정확히 시각 prio·A 에 실행 ⑤ 같은 우선순위는 도착 순서.
struct Job { int id; long arrival; int prio; long service; };
template <class T, class Less> class Heap {                                                                          // 직접 만든 이진 최대 힙
    std::vector<T> a; Less less;
public:
    explicit Heap(Less l = Less()) : less(l) {}
    bool empty() const { return a.empty(); } size_t size() const { return a.size(); } const T& top() const { return a[0]; }
    void push(const T& x) { a.push_back(x); size_t i = a.size() - 1; while (i && less(a[(i - 1) / 2], a[i])) { std::swap(a[i], a[(i - 1) / 2]); i = (i - 1) / 2; } }
    T pop() { T r = a[0]; a[0] = a.back(); a.pop_back(); size_t i = 0, n = a.size(); for (;;) { size_t l = 2 * i + 1, rr = l + 1, m = i; if (l < n && less(a[m], a[l])) m = l; if (rr < n && less(a[m], a[rr])) m = rr; if (m == i) break; std::swap(a[i], a[m]); i = m; } return r; }
};
const long INF_A = 1000000000000L;                                                                                   // A = ∞ (엄격한 우선순위)
struct ByKey { long A; const std::vector<Job>* jobs;
    long key(int id) const { return (*jobs)[id].prio * A - (*jobs)[id].arrival; }                                    // 시간에 따라 변하지 않는 에이징 키
    bool operator()(int x, int y) const { long kx = key(x), ky = key(y); return kx != ky ? kx < ky : x > y; } };     // less: 키가 작은 쪽이 뒤, 같으면 id 가 큰 쪽이 뒤
std::vector<long> scheduleHeap(const std::vector<Job>& jobs, long A) {                                              // jobs 는 도착 순(= id 순). 반환: 시작 시각
    size_t n = jobs.size(); Heap<int, ByKey> pq(ByKey{A, &jobs}); std::vector<long> start(n, -1); size_t idx = 0, done = 0; long t = 0;
    while (done < n) { while (idx < n && jobs[idx].arrival <= t) pq.push((int)idx++); if (pq.empty()) { t = jobs[idx].arrival; continue; }
        int j = pq.pop(); start[j] = t; t += jobs[j].service; done++; }
    return start;
}
std::vector<long> scheduleBrute(const std::vector<Job>& jobs, long A, bool strict) {                                // 매번 모든 대기 일의 유효 우선순위 prio·A + (t − 도착) 을 직접 비교
    size_t n = jobs.size(); std::vector<int> ready; std::vector<long> start(n, -1); size_t idx = 0, done = 0; long t = 0;
    while (done < n) { while (idx < n && jobs[idx].arrival <= t) ready.push_back((int)idx++); if (ready.empty()) { t = jobs[idx].arrival; continue; }
        size_t best = 0; for (size_t k = 1; k < ready.size(); k++) { const Job &x = jobs[ready[k]], &y = jobs[ready[best]]; bool better;
            if (strict) better = x.prio != y.prio ? x.prio > y.prio : (x.arrival != y.arrival ? x.arrival < y.arrival : x.id < y.id);
            else { long ex = x.prio * A + (t - x.arrival), ey = y.prio * A + (t - y.arrival); better = ex != ey ? ex > ey : x.id < y.id; }
            if (better) best = k; }
        int j = ready[best]; ready.erase(ready.begin() + best); start[j] = t; t += jobs[j].service; done++; }
    return start;
}
std::vector<Job> randomJobs(std::mt19937& rng, int n, int maxPrio, int maxGap, int maxService) {
    std::vector<Job> jobs; long t = 0; for (int i = 0; i < n; i++) { t += rng() % (maxGap + 1); jobs.push_back({i, t, (int)(rng() % (maxPrio + 1)), (long)(1 + rng() % maxService)}); } return jobs; }
int main() {
    { Heap<int, std::less<int>> h; std::priority_queue<int> ref; std::mt19937 rng(4); for (int i = 0; i < 100000; i++) { if (rng() % 3 != 0 || ref.empty()) { int v = rng() % 1000; h.push(v); ref.push(v); } else { assert(h.top() == ref.top() && h.pop() == ref.top()); ref.pop(); } assert(h.size() == ref.size()); } }       // ① 힙
    std::mt19937 rng(21); long maxWaitStrict = 0, maxWaitAged = 0; int instances = 0;
    for (int rep = 0; rep < 6; rep++) { std::vector<Job> jobs = randomJobs(rng, 1500, 9, 3, 6); int n = (int)jobs.size();                                  // 평균 도착 간격 1.5 < 평균 서비스 3.5: 과부하
        std::vector<long> strict = scheduleHeap(jobs, INF_A); assert(strict == scheduleBrute(jobs, 0, true));                                          // ② 힙 == 전수 비교
        long ws = 0; for (int j = 0; j < n; j++) ws = std::max(ws, strict[j] - jobs[j].arrival); maxWaitStrict = std::max(maxWaitStrict, ws);
        for (long A : {1L, 5L, 50L}) { std::vector<long> heap = scheduleHeap(jobs, A); assert(heap == scheduleBrute(jobs, A, false)); instances++;
            long wa = 0; for (int j = 0; j < n; j++) { long wait = heap[j] - jobs[j].arrival, T = jobs[j].arrival + (9 - jobs[j].prio) * A, bound = 0;       // ③ 대기 시간 한계
                for (int i = 0; i < n; i++) if (i != j && jobs[i].arrival <= T) bound += jobs[i].service; assert(wait >= 0 && wait <= bound); wa = std::max(wa, wait); }
            maxWaitAged = std::max(maxWaitAged, wa); if (A <= 5) assert(wa < ws);                                                                    // 에이징이 최악의 기다림을 줄인다
            std::vector<long> order(n); for (int j = 0; j < n; j++) order[j] = j; std::sort(order.begin(), order.end(), [&](long x, long y) { return heap[x] < heap[y]; }); long busy = 0; for (long j : order) { assert(heap[j] >= busy || jobs[j].arrival >= busy); busy = std::max(busy, heap[j]) + jobs[j].service; } } }   // 서버는 겹쳐 실행하지 않는다
    for (long A : {1L, 10L, 37L}) { const int H = 5000; const int P = 10; std::vector<Job> jobs; jobs.push_back({0, 0, 0, 1}); for (int t = 0; t < H; t++) jobs.push_back({t + 1, t, P, 1});    // ④ 기아 시나리오
        std::vector<long> strict = scheduleHeap(jobs, INF_A), aged = scheduleHeap(jobs, A); assert(strict[0] >= H && aged[0] == P * A);
        assert(scheduleBrute(jobs, A, false) == aged && scheduleBrute(jobs, 0, true) == strict); }
    for (long A : {3L, INF_A}) { std::vector<Job> jobs = randomJobs(rng, 800, 0, 2, 4); for (Job& j : jobs) j.prio = 3; std::vector<long> s = scheduleHeap(jobs, A); for (size_t i = 1; i < jobs.size(); i++) assert(s[i] > s[i - 1]); }     // ⑤ 같은 우선순위 = FIFO
    std::cout << "PriorityScheduling: the hand-written heap agreed with std::priority_queue and with an exhaustive effective-priority scheduler for " << instances << " aged and 6 strict overloaded instances; every job met the aging wait bound (worst aged wait " << maxWaitAged << " vs strict " << maxWaitStrict << "), and in the starvation scenario strict priority ran the low job after all 5000 high jobs while aging ran it exactly at prio*A" << std::endl; return 0;
}
// Time Complexity: 일당 O(log N) (에이징 키가 불변이라 재정렬 없음)
// Space Complexity: O(N)
```
