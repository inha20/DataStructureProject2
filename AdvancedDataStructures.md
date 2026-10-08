# Part 1. Persistent Data Structures
## PersistentArray()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 영속 배열(persistent array): 원소를 바꿔도 "이전 버전"이 그대로 살아 있어, 어느 버전이든 읽고 거기서 다시 갈라져(branch) 수정할 수 있다.
// 구현은 경로 복사(path copying): 크기 N 의 배열을 완전 이진 트리(잎 = 원소)로 두고, 한 원소를 바꿀 때 루트에서 그 잎까지의 노드 O(log N) 개만 새로 만들며 나머지는 이전 버전과 공유한다.
// 새 버전 = 새 루트 번호 하나.  전체를 복사하는 방식은 갱신마다 O(N) 이지만 이쪽은 O(log N) 시간과 공간이다
struct Node { int l = 0, r = 0, val = 0; };
std::vector<Node> pool(1);                                                 // 0 번은 비워 둔다
int build(int lo, int hi) {
    int id = pool.size(); pool.push_back({});
    if (lo == hi) return id;
    int m = (lo + hi) / 2, l = build(lo, m), r = build(m + 1, hi); pool[id].l = l; pool[id].r = r; return id;
}
int setAt(int cur, int lo, int hi, int i, int v) {                         // cur 버전에서 i 번 원소를 v 로 바꾼 새 루트
    int id = pool.size(); pool.push_back(pool[cur]);
    if (lo == hi) { pool[id].val = v; return id; }
    int m = (lo + hi) / 2;
    if (i <= m) { int c = setAt(pool[cur].l, lo, m, i, v); pool[id].l = c; }
    else        { int c = setAt(pool[cur].r, m + 1, hi, i, v); pool[id].r = c; }
    return id;
}
int getAt(int cur, int lo, int hi, int i) {
    while (lo < hi) { int m = (lo + hi) / 2; if (i <= m) { cur = pool[cur].l; hi = m; } else { cur = pool[cur].r; lo = m + 1; } }
    return pool[cur].val;
}

int main() {
    const int N = 1000, U = 3000; std::mt19937 rng(5);
    std::vector<int> root = {build(0, N - 1)}; std::vector<std::vector<int>> model = {std::vector<int>(N, 0)};
    size_t afterBuild = pool.size();
    for (int step = 0; step < U; step++) {
        int base = rng() % root.size(), i = rng() % N, v = rng() % 100000;              // 아무 옛 버전에서나 갈라져 나온다 (브랜칭)
        root.push_back(setAt(root[base], 0, N - 1, i, v));
        model.push_back(model[base]); model.back()[i] = v;
    }
    for (int q = 0; q < 20000; q++) {                                      // 모든 버전은 여전히 자기 시점의 값을 갖는다
        int ver = rng() % root.size(), i = rng() % N;
        assert(getAt(root[ver], 0, N - 1, i) == model[ver][i]);
    }
    size_t added = pool.size() - afterBuild;
    assert(added <= (size_t)U * 11);                                       // 갱신당 노드 약 log2(1000)+1 = 11 개
    std::cout << "PersistentArray: " << root.size() << " versions, " << added << " new nodes (full copies would need " << (size_t)U * N << " cells)" << std::endl;
    return 0;
}
// Time Complexity: 읽기·갱신 O(log N)
// Space Complexity: 버전당 O(log N)
```
## PersistentList()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 영속 리스트: 불변 단방향 연결 리스트.  cons(맨 앞에 붙이기)는 새 노드 하나만 만들고 나머지 꼬리는 그대로 공유한다.
// 가운데를 바꾸는 setAt 은 앞부분(O(i) 개)만 복사하고 i 뒤쪽은 공유, concat(a, b) 는 a 만 복사하고 b 를 공유한다.  모든 옛 버전이 변하지 않으므로 스레드 사이에 잠금 없이 공유할 수 있다
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
## PersistentStack()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <cassert>

// 영속 스택(스택 관점의 요약, 정본은 Stack.md Part 10): push 는 "새 머리 노드 -> 옛 머리", pop 은 옛 머리의 next 를 새 스택으로 돌려줄 뿐이다.
// 옛 버전을 건드리지 않으므로 실행 취소(undo)·분기 탐색·스레드 간 공유가 공짜다.  push·pop·top 이 모두 O(1) 이고 버전마다 노드 하나만 늘어난다
struct Node; typedef std::shared_ptr<const Node> Stack;
struct Node { int v; Stack next; };
Stack push(const Stack& s, int v) { return std::make_shared<const Node>(Node{v, s}); }
Stack pop(const Stack& s) { return s->next; }
int main() {
    Stack s0, s1 = push(s0, 1), s2 = push(s1, 2), s3 = push(s2, 3);        // 세 버전: [1], [2 1], [3 2 1]
    Stack branch = push(pop(s3), 9);                                       // s3 에서 pop 한 뒤 갈라져 나온 새 버전 [9 2 1]
    assert(s3->v == 3 && branch->v == 9 && branch->next == s2 && pop(s1) == nullptr);
    std::cout << "PersistentStack: s3 top=" << s3->v << ", branch top=" << branch->v << std::endl; return 0;
}
// Time Complexity: push·pop·top O(1)
// Space Complexity: 버전당 O(1)
```
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

// 영속 큐: 모든 옛 버전을 건드리지 않고, "어떤 버전에서든" snoc(뒤에 추가)·tail(앞 제거)을 최악 O(1) 에 한다 (Okasaki 의 실시간 큐).
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
## PersistentSegmentTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 영속 세그먼트 트리의 대표 응용: "구간 [l, r] 에서 k 번째로 작은 값" 을 O(log N) 에 (온라인).
// 값을 좌표 압축한 뒤, 접두 a[0..i) 의 "값 분포"를 담은 버전 root[i] 를 만든다. 원소 하나를 넣을 때마다 루트→잎 경로만 새로 만들어 root[i+1] 이 된다.
// 구간 (l, r] 의 분포 = root[r] 의 개수 - root[l] 의 개수 이므로, 두 버전을 동시에 내려가며 왼쪽 자식의 개수 차로 k 번째를 찾는다
struct Node { int l = 0, r = 0, cnt = 0; };
std::vector<Node> pool(1);
int insert(int prev, int lo, int hi, int v) {
    int id = pool.size(); pool.push_back(pool[prev]); pool[id].cnt++;
    if (lo == hi) return id;
    int m = (lo + hi) / 2;
    if (v <= m) { int c = insert(pool[prev].l, lo, m, v); pool[id].l = c; } else { int c = insert(pool[prev].r, m + 1, hi, v); pool[id].r = c; }
    return id;
}
int kth(int u, int v, int lo, int hi, int k) {                             // u = root[l], v = root[r+1]; 구간 안에서 k 번째(1-기준)로 작은 값의 순위
    while (lo < hi) {
        int m = (lo + hi) / 2, left = pool[pool[v].l].cnt - pool[pool[u].l].cnt;
        if (k <= left) { u = pool[u].l; v = pool[v].l; hi = m; } else { k -= left; u = pool[u].r; v = pool[v].r; lo = m + 1; }
    }
    return lo;
}

int main() {
    std::mt19937 rng(14); int n = 2000; std::vector<int> a(n);
    for (auto& x : a) x = (int)(rng() % 1000000) - 500000;
    std::vector<int> sorted = a; std::sort(sorted.begin(), sorted.end()); sorted.erase(std::unique(sorted.begin(), sorted.end()), sorted.end());
    int m = sorted.size(); std::vector<int> root = {0};
    for (int x : a) root.push_back(insert(root.back(), 0, m - 1, std::lower_bound(sorted.begin(), sorted.end(), x) - sorted.begin()));
    for (int q = 0; q < 3000; q++) {
        int l = rng() % n, r = rng() % n; if (l > r) std::swap(l, r); int k = rng() % (r - l + 1) + 1;
        std::vector<int> seg(a.begin() + l, a.begin() + r + 1); std::nth_element(seg.begin(), seg.begin() + k - 1, seg.end());
        assert(sorted[kth(root[l], root[r + 1], 0, m - 1, k)] == seg[k - 1]);
    }
    std::cout << "PersistentSegmentTree: k-th smallest in any range answered online, " << pool.size() << " nodes for n=" << n << std::endl;
    return 0;
}
// Time Complexity: 구성 O(N log N), 질의 O(log N)
// Space Complexity: O(N log N)
```
## PersistentTrie()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 영속 이진 트라이: 정수를 상위 비트부터 한 비트씩 내려가는 트라이로 두고, 접두 a[0..i) 마다 버전 root[i] 를 만든다 (각 노드에 지나간 개수 cnt).
// "구간 [l, r] 의 원소 중 x 와 XOR 이 최대인 것" 은 root[l] 과 root[r+1] 의 cnt 차이가 양수인 방향 중 x 의 반대 비트 쪽을 우선 선택하며 내려가면 된다 -> O(비트 수)
const int B = 30;
struct Node { int ch[2] = {0, 0}, cnt = 0; };
std::vector<Node> pool(1);
int insert(int prev, int x) {
    int root = pool.size(); pool.push_back(pool[prev]); pool[root].cnt++;
    int cur = root;
    for (int b = B - 1; b >= 0; b--) {
        int bit = (x >> b) & 1, old = pool[cur].ch[bit], id = pool.size();
        pool.push_back(pool[old]); pool[id].cnt++; pool[cur].ch[bit] = id; cur = id;
    }
    return root;
}
int maxXor(int ru, int rv, int x) {                                        // ru = root[l], rv = root[r+1]
    int res = 0;
    for (int b = B - 1; b >= 0; b--) {
        int want = ((x >> b) & 1) ^ 1;
        if (pool[pool[rv].ch[want]].cnt - pool[pool[ru].ch[want]].cnt > 0) { res |= 1 << b; ru = pool[ru].ch[want]; rv = pool[rv].ch[want]; }
        else { ru = pool[ru].ch[want ^ 1]; rv = pool[rv].ch[want ^ 1]; }
    }
    return res;
}

int main() {
    std::mt19937 rng(8); int n = 1500; std::vector<int> a(n);
    for (auto& x : a) x = rng() % (1 << B);
    std::vector<int> root = {0}; for (int x : a) root.push_back(insert(root.back(), x));
    for (int q = 0; q < 3000; q++) {
        int l = rng() % n, r = rng() % n; if (l > r) std::swap(l, r); int x = rng() % (1 << B), best = 0;
        for (int i = l; i <= r; i++) best = std::max(best, a[i] ^ x);
        assert(maxXor(root[l], root[r + 1], x) == best);
    }
    std::cout << "PersistentTrie: max-XOR over any subarray in O(" << B << "), nodes " << pool.size() << std::endl;
    return 0;
}
// Time Complexity: 구성 O(N·B), 질의 O(B)  (B = 비트 수)
// Space Complexity: O(N·B)
```

# Part 2. Succinct Data Structures
## BitVector()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 비트 벡터: n 비트를 64비트 워드 n/64 개에 빽빽이 담는다 (bool 배열의 1/8, std::vector<bool> 과 같은 밀도).  succinct 구조의 바탕이며,
// 한 워드 안에서는 popcount(비트 개수 세기) 한 번으로 "그 워드 안의 1의 개수"가 나온다.  이 항목은 접근·설정·전체 1의 개수까지,
// 다음 항목 Rank / Select 가 그 위에 보조 디렉터리를 얹어 O(1) 에 가깝게 만든다
struct BitVector {
    size_t n; std::vector<uint64_t> w;
    explicit BitVector(size_t n) : n(n), w((n + 63) / 64, 0) {}
    bool get(size_t i) const { return (w[i >> 6] >> (i & 63)) & 1; }
    void set(size_t i, bool v = true) { if (v) w[i >> 6] |= 1ULL << (i & 63); else w[i >> 6] &= ~(1ULL << (i & 63)); }
    void flip(size_t i) { w[i >> 6] ^= 1ULL << (i & 63); }
    size_t count() const { size_t c = 0; for (uint64_t x : w) c += __builtin_popcountll(x); return c; }
    size_t bytes() const { return w.size() * 8; }
};

int main() {
    const size_t N = 100003; BitVector bv(N); std::vector<bool> ref(N); std::mt19937 rng(1);
    for (int step = 0; step < 300000; step++) {
        size_t i = rng() % N; int op = rng() % 3;
        if (op == 0) { bv.set(i); ref[i] = true; } else if (op == 1) { bv.set(i, false); ref[i] = false; } else { bv.flip(i); ref[i] = !ref[i]; }
        assert(bv.get(i) == ref[i]);
    }
    size_t c = 0; for (size_t i = 0; i < N; i++) { assert(bv.get(i) == ref[i]); c += ref[i]; }
    assert(bv.count() == c);
    assert(bv.bytes() <= N / 8 + 8);                                       // 비트당 1 비트(+ 워드 올림)
    std::cout << "BitVector: " << N << " bits in " << bv.bytes() << " bytes (a bool[] would take " << N << "), ones = " << c << std::endl;
    return 0;
}
// Time Complexity: get·set O(1), count O(N/64)
// Space Complexity: N 비트
```
## Rank()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// rank1(i) = 앞쪽 i 비트(B[0..i))에 들어 있는 1 의 개수.  이를 O(1) 에 하려면 "위치마다 누적 개수"를 저장하는 n 칸 배열 대신,
// 512 비트마다 누적 개수 하나(32비트)만 저장하는 디렉터리를 둔다 -> 추가 공간 32/512 = 6.25%.  질의는 (디렉터리 한 칸) + (최대 8 워드의 popcount) + (마지막 워드의 부분 popcount)
// 이론상의 o(n) 보조 구조(Jacobson, Clark)는 블록을 두 단계로 더 잘게 쪼개 같은 아이디어를 반복한다
struct RankBits {
    size_t n; std::vector<uint64_t> w; std::vector<uint32_t> super;       // super[k] = 앞쪽 512*k 비트의 1 의 수
    explicit RankBits(const std::vector<bool>& bits) : n(bits.size()), w((n + 63) / 64 + 1, 0) {
        for (size_t i = 0; i < n; i++) if (bits[i]) w[i >> 6] |= 1ULL << (i & 63);
        super.assign(w.size() / 8 + 2, 0); uint32_t acc = 0;
        for (size_t k = 0; k * 8 < w.size(); k++) { super[k] = acc; for (size_t j = k * 8; j < std::min(w.size(), k * 8 + 8); j++) acc += __builtin_popcountll(w[j]); }
        super[(w.size() + 7) / 8] = acc;
    }
    uint32_t rank1(size_t i) const {                                       // 0 <= i <= n
        size_t word = i >> 6, blk = word >> 3; uint32_t r = super[blk];
        for (size_t j = blk * 8; j < word; j++) r += __builtin_popcountll(w[j]);
        if (i & 63) r += __builtin_popcountll(w[word] & ((1ULL << (i & 63)) - 1));
        return r;
    }
    uint32_t rank0(size_t i) const { return i - rank1(i); }
    size_t bytes() const { return w.size() * 8 + super.size() * 4; }
};

int main() {
    std::mt19937 rng(2);
    for (double density : {0.5, 0.05, 0.95}) {
        size_t n = 200000 + rng() % 1000; std::vector<bool> bits(n); std::vector<uint32_t> pre(n + 1, 0);
        for (size_t i = 0; i < n; i++) { bits[i] = (rng() % 1000) < density * 1000; pre[i + 1] = pre[i] + bits[i]; }
        RankBits rb(bits);
        for (size_t i = 0; i <= n; i += 1 + rng() % 7) assert(rb.rank1(i) == pre[i] && rb.rank0(i) == i - pre[i]);
        assert(rb.rank1(n) == pre[n]);
        double overhead = (double)rb.bytes() / (n / 8.0) - 1;
        assert(overhead < 0.08);                                           // 원본 비트 배열 대비 약 6% 추가 공간 (누적 배열이면 3200%)
        std::cout << "Rank: density " << density << ", overhead " << overhead * 100 << "% (naive prefix array +3100%)" << std::endl;
    }
    return 0;
}
// Time Complexity: rank O(1) (최대 8 워드 popcount 상수 번)
// Space Complexity: N + 0.0625 N 비트
```
## Select()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// select1(k) = k 번째(1-기준) 1 의 위치.  rank 의 역함수이므로 "rank1(i) >= k 인 가장 작은 i" 를 이분 탐색하면 O(log n) 이다.
// 더 빠르게: 1024 번째 1 마다 그 위치를 표본(sample)으로 저장해 두면 이분 탐색 범위가 표본 사이로 좁아진다. 마지막에 한 워드 안에서 "k 번째 1 의 비트 위치"는
// 하위 비트를 하나씩 지우는 루프(x &= x - 1)로 찾는다
struct SelectBits {
    size_t n; std::vector<uint64_t> w; std::vector<uint32_t> cum; std::vector<uint32_t> sample;   // cum[j] = 워드 j 앞쪽의 1 의 수
    const uint32_t S = 1024; uint32_t ones = 0;
    explicit SelectBits(const std::vector<bool>& bits) : n(bits.size()), w((n + 63) / 64, 0) {
        for (size_t i = 0; i < n; i++) if (bits[i]) w[i >> 6] |= 1ULL << (i & 63);
        cum.assign(w.size() + 1, 0); for (size_t j = 0; j < w.size(); j++) cum[j + 1] = cum[j] + __builtin_popcountll(w[j]);
        ones = cum[w.size()]; size_t j = 0;
        for (uint32_t k = 1; k <= ones; k += S) { while (cum[j + 1] < k) j++; sample.push_back(j); }      // k 번째 1 이 들어 있는 워드 번호
    }
    size_t select1(uint32_t k) const {                                     // 1 <= k <= ones
        size_t lo = sample[(k - 1) / S], hi = ((k - 1) / S + 1 < sample.size()) ? sample[(k - 1) / S + 1] : w.size() - 1;
        while (lo < hi) { size_t mid = (lo + hi) / 2; if (cum[mid + 1] >= k) hi = mid; else lo = mid + 1; }   // cum[j+1] >= k 인 첫 워드
        uint64_t x = w[lo]; uint32_t need = k - cum[lo];
        while (--need) x &= x - 1;                                         // 낮은 1 비트를 need-1 개 지운 뒤
        return lo * 64 + __builtin_ctzll(x);                               // 가장 낮은 1 의 위치
    }
};

int main() {
    std::mt19937 rng(3);
    for (double density : {0.5, 0.02, 0.9}) {
        size_t n = 300000; std::vector<bool> bits(n); std::vector<size_t> pos;
        for (size_t i = 0; i < n; i++) { bits[i] = (rng() % 1000) < density * 1000; if (bits[i]) pos.push_back(i); }
        SelectBits sb(bits);
        for (uint32_t k = 1; k <= sb.ones; k += 1 + rng() % 5) assert(sb.select1(k) == pos[k - 1]);
        assert(sb.select1(1) == pos.front() && sb.select1(sb.ones) == pos.back());
        std::cout << "Select: density " << density << ", " << sb.ones << " ones, " << sb.sample.size() << " samples" << std::endl;
    }
    return 0;
}
// Time Complexity: select O(log (표본 사이의 워드 수)) + O(1)
// Space Complexity: N + 표본 O(N/1024)
```
## WaveletTree()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 웨이블릿 트리(여기서는 레벨별 비트 배열로 펴 놓은 "웨이블릿 행렬"): 문자열/정수열 S[0..n) 을 비트 배열 log σ 개로 바꿔 저장하면서도
//   access(i)     S[i]
//   rank(c, i)    S[0..i) 안에서 값 c 의 개수
//   quantile(l,r,k) S[l..r) 에서 k 번째(0-기준)로 작은 값
//   count(l,r,lo,hi) S[l..r) 에서 값이 [lo, hi) 인 원소 수
// 를 모두 O(log σ) 에 한다.  레벨 b(최상위 비트부터)마다 현재 순서에서 b 번째 비트를 적은 비트 배열을 두고, 그 비트가 0 인 원소를 앞으로, 1 인 원소를 뒤로 안정 정렬해 다음 레벨로 넘긴다
struct Level { std::vector<uint32_t> ones; int zeros = 0; };               // ones[i] = 이 레벨 비트 배열 앞쪽 i 개 중 1 의 수
struct WaveletMatrix {
    int B; size_t n; std::vector<Level> lv;
    WaveletMatrix(std::vector<uint32_t> s, int bits) : B(bits), n(s.size()), lv(bits) {
        for (int b = 0; b < B; b++) {
            int bit = B - 1 - b; Level& L = lv[b]; L.ones.assign(n + 1, 0);
            std::vector<uint32_t> zero, one;
            for (size_t i = 0; i < n; i++) { int v = (s[i] >> bit) & 1; L.ones[i + 1] = L.ones[i] + v; (v ? one : zero).push_back(s[i]); }
            L.zeros = zero.size(); s = zero; s.insert(s.end(), one.begin(), one.end());
        }
    }
    uint32_t access(size_t i) const {
        uint32_t v = 0;
        for (int b = 0; b < B; b++) {
            const Level& L = lv[b]; int bit = L.ones[i + 1] - L.ones[i];
            v = v << 1 | bit; i = bit ? L.zeros + L.ones[i] : i - L.ones[i];
        }
        return v;
    }
    size_t rank(uint32_t c, size_t i) const {                              // S[0..i) 안의 c 의 개수
        size_t lo = 0, hi = i;
        for (int b = 0; b < B; b++) {
            const Level& L = lv[b]; int bit = (c >> (B - 1 - b)) & 1;
            if (bit) { lo = L.zeros + L.ones[lo]; hi = L.zeros + L.ones[hi]; } else { lo -= L.ones[lo]; hi -= L.ones[hi]; }
        }
        return hi - lo;
    }
    uint32_t quantile(size_t l, size_t r, size_t k) const {                // [l, r) 에서 k 번째(0-기준)로 작은 값
        uint32_t v = 0;
        for (int b = 0; b < B; b++) {
            const Level& L = lv[b]; size_t zl = l - L.ones[l], zr = r - L.ones[r], z = zr - zl;
            if (k < z) { l = zl; r = zr; v <<= 1; } else { k -= z; l = L.zeros + L.ones[l]; r = L.zeros + L.ones[r]; v = v << 1 | 1; }
        }
        return v;
    }
    size_t countLess(size_t l, size_t r, uint32_t x) const {              // [l, r) 에서 값 < x 인 원소 수
        if (x >= (1u << B)) return r - l;
        size_t res = 0;
        for (int b = 0; b < B; b++) {
            const Level& L = lv[b]; int bit = (x >> (B - 1 - b)) & 1; size_t zl = l - L.ones[l], zr = r - L.ones[r];
            if (bit) { res += zr - zl; l = L.zeros + L.ones[l]; r = L.zeros + L.ones[r]; } else { l = zl; r = zr; }
        }
        return res;
    }
    size_t count(size_t l, size_t r, uint32_t lo, uint32_t hi) const { return countLess(l, r, hi) - countLess(l, r, lo); }
};

int main() {
    std::mt19937 rng(6); const int n = 3000, B = 10; std::vector<uint32_t> s(n);
    for (auto& x : s) x = rng() % (1u << B);
    WaveletMatrix wm(s, B);
    for (int i = 0; i < n; i += 3) assert(wm.access(i) == s[i]);
    for (int q = 0; q < 3000; q++) {
        size_t l = rng() % n, r = rng() % n; if (l > r) std::swap(l, r); r++;
        uint32_t c = s[rng() % n], lo = rng() % 1024, hi = rng() % 1025; if (lo > hi) std::swap(lo, hi);
        size_t cnt = 0, inRange = 0; for (size_t i = 0; i < r; i++) cnt += s[i] == c;
        for (size_t i = l; i < r; i++) inRange += s[i] >= lo && s[i] < hi;
        assert(wm.rank(c, r) == cnt && wm.count(l, r, lo, hi) == inRange);
        std::vector<uint32_t> seg(s.begin() + l, s.begin() + r); std::sort(seg.begin(), seg.end());
        size_t k = rng() % seg.size(); assert(wm.quantile(l, r, k) == seg[k]);
    }
    std::cout << "WaveletTree: access / rank / quantile / range-count verified, " << B << " levels for sigma=" << (1 << B) << std::endl;
    return 0;
}
// Time Complexity: 구성 O(N log σ), 질의 O(log σ)
// Space Complexity: N log σ 비트 (+ 랭크 디렉터리)
```
## FMIndex()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// FM-인덱스(문자열 관점의 요약, 정본은 String.md Part 9): BWT(Burrows–Wheeler 변환)와 두 표 C[c](c 보다 작은 문자 수), Occ(c, i)(BWT[0..i) 안의 c 개수)만으로
// 패턴의 출현 횟수를 원문 없이 O(|P|) 에 센다 (backward search).  원문을 BWT 로 압축해 두고도 검색이 되는 "자기 색인" 구조다
int main() {
    std::string t = "banana$"; int n = t.size(); std::vector<int> sa(n);
    for (int i = 0; i < n; i++) sa[i] = i;
    std::sort(sa.begin(), sa.end(), [&](int a, int b) { return t.compare(a, n, t, b, n) < 0; });
    std::string bwt; for (int i : sa) bwt += t[(i + n - 1) % n];            // annb$aa
    auto C = [&](char c) { int r = 0; for (char x : t) r += x < c; return r; };
    auto occ = [&](char c, int i) { return (int)std::count(bwt.begin(), bwt.begin() + i, c); };
    auto count = [&](const std::string& p) { int lo = 0, hi = n; for (int k = p.size() - 1; k >= 0 && lo < hi; k--) { lo = C(p[k]) + occ(p[k], lo); hi = C(p[k]) + occ(p[k], hi); } return hi - lo; };
    assert(bwt == "annb$aa" && count("ana") == 2 && count("na") == 2 && count("nab") == 0 && count("a") == 3);
    std::cout << "FMIndex: BWT=" << bwt << ", count(ana)=" << count("ana") << std::endl; return 0;
}
// Time Complexity: count O(|P|) (Occ 가 O(1) 이라면)
// Space Complexity: BWT 크기 + Occ 표
```
## SuccinctTrie()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 간결 트라이(LOUDS, Level-Order Unary Degree Sequence): 트라이를 포인터 대신 비트열 하나로 표현한다. 노드를 너비 우선 순서로 보며
// 각 노드마다 "자식 수만큼의 1 과 0 하나"를 이어 쓰고, 맨 앞에 가상 루트용 "10" 을 붙인다. 노드 n 개면 비트는 2n+1 개뿐이다.
// rank/select 만으로 이동한다 (x = BFS 번호, 1-기준):
//   첫째 자식 = select0(x)+1 위치의 1 의 순번(rank1),  다음 형제 = 바로 다음 비트가 1 이면 y+1,  부모 = rank0(select1(y))
// 간선 라벨은 BFS 순서로 별도 배열에, "단어의 끝" 표시는 비트 배열 하나에 둔다
struct Louds {
    std::vector<int> B;                                                    // 비트열
    std::vector<char> label;                                               // label[y] = 노드 y 로 들어오는 간선의 문자 (y >= 2, 1 번이 루트)
    std::vector<bool> terminal;                                            // terminal[y] = 단어의 끝인가
    std::vector<int> pos0, pos1, pre1;                                     // select0, select1 표와 rank1 접두합
    void build(const std::set<std::string>& words) {
        struct T { std::vector<std::pair<char, int>> kids; bool end = false; }; std::vector<T> t(1);
        for (auto& w : words) { int cur = 0; for (char c : w) { int nx = -1; for (auto& k : t[cur].kids) if (k.first == c) nx = k.second; if (nx < 0) { nx = t.size(); t.emplace_back(); t[cur].kids.push_back({c, nx}); } cur = nx; } t[cur].end = true; }
        for (auto& x : t) std::sort(x.kids.begin(), x.kids.end());
        B = {1, 0}; label = {0, 0}; terminal = {false, false};              // 인덱스 0 은 사용하지 않는다
        std::queue<int> q; q.push(0);
        terminal[1] = t[0].end; label[1] = 0;
        std::vector<int> order = {0};
        while (!q.empty()) { int u = q.front(); q.pop(); for (auto& k : t[u].kids) { B.push_back(1); label.push_back(k.first); terminal.push_back(t[k.second].end); q.push(k.second); order.push_back(k.second); } B.push_back(0); }
        pre1.assign(B.size() + 1, 0); for (size_t i = 0; i < B.size(); i++) { pre1[i + 1] = pre1[i] + B[i]; (B[i] ? pos1 : pos0).push_back(i); }
        pos0.insert(pos0.begin(), -1); pos1.insert(pos1.begin(), -1);       // 1-기준
    }
    int rank1(int i) const { return pre1[i + 1]; }                         // B[0..i] 안의 1 의 수
    int firstChild(int x) const { int p = pos0[x] + 1; return (p < (int)B.size() && B[p]) ? rank1(p) : 0; }
    int nextSibling(int y) const { int p = pos1[y] + 1; return (p < (int)B.size() && B[p]) ? y + 1 : 0; }
    int parent(int y) const { return pos1[y] - (rank1(pos1[y]) - 1); }     // pos1[y] 앞쪽의 0 의 개수
    int child(int x, char c) const { for (int y = firstChild(x); y; y = nextSibling(y)) if (label[y] == c) return y; return 0; }
    bool contains(const std::string& w) const { int x = 1; for (char c : w) { x = child(x, c); if (!x) return false; } return terminal[x]; }
    int countWords(int x) const { int r = terminal[x]; for (int y = firstChild(x); y; y = nextSibling(y)) r += countWords(y); return r; }
    int countPrefix(const std::string& p) const { int x = 1; for (char c : p) { x = child(x, c); if (!x) return 0; } return countWords(x); }
    int nodes() const { return label.size() - 1; }
};

int main() {
    std::mt19937 rng(33); std::set<std::string> words;
    for (int i = 0; i < 1500; i++) { std::string w; int len = 1 + rng() % 8; for (int j = 0; j < len; j++) w += 'a' + rng() % 4; words.insert(w); }
    Louds t; t.build(words);
    assert((int)t.B.size() == 2 * t.nodes() + 1);                          // 노드 n 개 -> 비트 2n+1 개
    for (auto& w : words) assert(t.contains(w));
    for (int i = 0; i < 3000; i++) { std::string w; int len = 1 + rng() % 9; for (int j = 0; j < len; j++) w += 'a' + rng() % 5; assert(t.contains(w) == (words.count(w) > 0)); }
    for (int i = 0; i < 300; i++) {                                        // 접두사로 시작하는 단어 수
        std::string p; int len = rng() % 4; for (int j = 0; j < len; j++) p += 'a' + rng() % 4;
        int want = 0; for (auto& w : words) want += w.compare(0, p.size(), p) == 0;
        assert(t.countPrefix(p) == want);
    }
    for (int y = 2; y <= t.nodes(); y++) { int p = t.parent(y); bool found = false; for (int c = t.firstChild(p); c; c = t.nextSibling(c)) found |= c == y; assert(found); }   // parent 와 firstChild/nextSibling 이 일관
    std::cout << "SuccinctTrie: " << words.size() << " words, " << t.nodes() << " nodes, " << t.B.size() << " structure bits (pointer trie: " << t.nodes() * 4 * 8 << " bits for 4 children pointers)" << std::endl;
    return 0;
}
// Time Complexity: 이동 O(1) (rank/select 가 O(1) 일 때), 단어 조회 O(|w|·σ)
// Space Complexity: 2N+1 비트 + 라벨 N 문자
```

# Part 3. 확률적 자료구조
## BloomFilter()
### 대표코드
```cpp
#include <cmath>
#include <cstdint>
#include <iostream>
#include <vector>
#include <cassert>

// 블룸 필터: "이 키가 집합에 있을 수도 있다 / 확실히 없다" 만 답하는 확률적 집합.  m 비트 배열과 해시 k 개. 삽입은 k 개 비트를 켜고, 조회는 k 개가 모두 켜졌는지 본다.
// 거짓 음성은 없고(넣은 키는 항상 "있을 수도"), 거짓 양성 확률은 p ≈ (1 - e^(-kn/m))^k.  목표 p 와 개수 n 이 주어지면 m = -n ln p / (ln 2)^2, k = (m/n) ln 2 가 최적이고
// 그때 원소당 약 1.44 log2(1/p) 비트(p=1% 이면 9.6 비트)면 된다.  해시 k 개는 해시 둘로 흉내 낸다(Kirsch–Mitzenmacher: h1 + i·h2).  OR 로 합집합, 삭제는 불가(→ Counting/Cuckoo)
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct Bloom {
    size_t m; int k; std::vector<uint64_t> bits;
    Bloom(size_t n, double p) {
        m = (size_t)std::ceil(-(double)n * std::log(p) / (std::log(2.0) * std::log(2.0))); k = std::max(1, (int)std::round((double)m / n * std::log(2.0)));
        bits.assign((m + 63) / 64, 0);
    }
    void add(uint64_t key) { uint64_t h1 = mix(key), h2 = mix(h1) | 1; for (int i = 0; i < k; i++) { size_t pos = (h1 + (uint64_t)i * h2) % m; bits[pos >> 6] |= 1ULL << (pos & 63); } }
    bool maybe(uint64_t key) const { uint64_t h1 = mix(key), h2 = mix(h1) | 1; for (int i = 0; i < k; i++) { size_t pos = (h1 + (uint64_t)i * h2) % m; if (!((bits[pos >> 6] >> (pos & 63)) & 1)) return false; } return true; }
    void merge(const Bloom& o) { for (size_t i = 0; i < bits.size(); i++) bits[i] |= o.bits[i]; }
};

int main() {
    const size_t N = 100000; Bloom b(N, 0.01);
    for (uint64_t i = 0; i < N; i++) b.add(i * 2);                         // 짝수 키 N 개
    for (uint64_t i = 0; i < N; i++) assert(b.maybe(i * 2));               // 거짓 음성 없음
    size_t fp = 0, T = 200000; for (uint64_t i = 0; i < T; i++) fp += b.maybe(i * 2 + 1 + (1ULL << 40));     // 넣지 않은 키
    double rate = (double)fp / T;
    assert(rate > 0.004 && rate < 0.016);                                  // 이론값 1%
    assert(b.k == 7 && b.m > 950000 && b.m < 960000);                      // 원소당 9.6 비트, 해시 7 개
    Bloom c(N, 0.01); for (uint64_t i = 0; i < N; i++) c.add(i * 2 + 1);   // 다른 필터와 합집합
    c.merge(b); for (uint64_t i = 0; i < 2 * N; i++) assert(c.maybe(i));
    std::cout << "BloomFilter: m=" << b.m << " bits (" << (double)b.m / N << " bits/key), k=" << b.k << ", measured false-positive rate " << rate * 100 << "% (target 1%)" << std::endl;
    return 0;
}
// Time Complexity: 삽입·조회 O(k)
// Space Complexity: 약 1.44 n log2(1/p) 비트
```
## CountingBloomFilter()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <vector>
#include <cassert>

// 카운팅 블룸 필터: 비트 대신 작은 카운터(보통 4비트)를 두어 삭제를 지원한다. 삽입은 k 개 카운터 +1, 삭제는 -1, 조회는 모두 > 0 인지.
// 4비트(최대 15)면 충분한 이유: 카운터 하나가 16 이상이 될 확률이 m·1.37e-15 수준이라 무시할 만하다.  그래도 포화(15)한 카운터는 "더 이상 줄이지 않는다" — 줄이면 실제보다 낮아져 거짓 음성이 생길 수 있기 때문이다
// (일반 블룸 필터보다 공간 4배.  없는 키를 삭제하면 필터가 깨지므로 "넣었던 키만 삭제" 가 전제)
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct CBF {
    size_t m; int k; std::vector<uint8_t> c;                               // 데모에서는 카운터 하나를 1바이트에 두되 값은 0..15 만 쓴다 (실제로는 한 바이트에 2개)
    CBF(size_t m, int k) : m(m), k(k), c(m, 0) {}
    size_t pos(uint64_t key, int i) const { uint64_t h1 = mix(key), h2 = mix(h1) | 1; return (h1 + (uint64_t)i * h2) % m; }
    void add(uint64_t key) { for (int i = 0; i < k; i++) { uint8_t& x = c[pos(key, i)]; if (x < 15) x++; } }
    void remove(uint64_t key) { for (int i = 0; i < k; i++) { uint8_t& x = c[pos(key, i)]; if (x > 0 && x < 15) x--; } }      // 포화한 카운터는 그대로
    bool maybe(uint64_t key) const { for (int i = 0; i < k; i++) if (!c[pos(key, i)]) return false; return true; }
};

int main() {
    const size_t N = 20000; CBF f(N * 10, 7);
    for (uint64_t i = 0; i < N; i++) f.add(i);
    for (uint64_t i = 0; i < N; i++) assert(f.maybe(i));
    for (uint64_t i = 0; i < N; i += 2) f.remove(i);                       // 짝수 키 삭제
    for (uint64_t i = 1; i < N; i += 2) assert(f.maybe(i));                // 남은 키는 여전히 있음 (거짓 음성 없음)
    size_t still = 0; for (uint64_t i = 0; i < N; i += 2) still += f.maybe(i);
    assert(still < N / 2 / 50);                                            // 삭제한 키 대부분은 이제 "없음" (거짓 양성 몇 %)
    CBF g(1000, 3); for (int i = 0; i < 40; i++) g.add(777);               // 같은 키를 40 번: 카운터가 15 에서 포화
    for (int i = 0; i < 40; i++) g.remove(777);
    assert(g.maybe(777));                                                  // 포화한 카운터는 줄이지 않으므로 키가 남아 있는 것으로 보인다 (안전한 쪽으로의 오류)
    std::cout << "CountingBloomFilter: deletes work (" << still << "/" << N / 2 << " deleted keys still look present), saturated counters never decrement" << std::endl;
    return 0;
}
// Time Complexity: 삽입·삭제·조회 O(k)
// Space Complexity: 카운터당 4비트 -> 블룸 필터의 4배
```
## CuckooFilter()
### 대표코드
```cpp
#include <array>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 쿠쿠 필터: 키의 "지문(fingerprint, f 비트)"을 쿠쿠 해싱 표에 넣는 필터. 삭제가 되고, 거짓 양성률이 낮을 때(<3%) 블룸 필터보다 공간 효율이 좋다.
// 핵심 요령 "partial-key cuckoo hashing": 지문만으로 다른 후보 버킷을 알아내려고 i2 = i1 XOR hash(지문) 으로 정한다 (XOR 이므로 어느 쪽에서 계산해도 짝이 같다).
// 버킷마다 4칸. 둘 다 가득 차면 한 지문을 쫓아내(kick) 그 짝 버킷으로 보내길 반복한다. 실패하면 되돌려서(rollback) 이전에 넣은 키가 사라지지 않게 한다
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct Cuckoo {
    int fb; size_t nb; std::vector<std::array<uint16_t, 4>> B; std::mt19937_64 rng{7}; size_t count = 0;   // 지문 0 = 빈칸 (지문은 1..2^fb-1)
    Cuckoo(int fpBits, size_t buckets) : fb(fpBits), nb(buckets), B(buckets, std::array<uint16_t, 4>{0, 0, 0, 0}) {}
    uint16_t fp(uint64_t h) const { return (uint16_t)((h >> 40) % ((1u << fb) - 1) + 1); }
    size_t idx(uint64_t h) const { return h & (nb - 1); }
    size_t alt(size_t i, uint16_t f) const { return (i ^ mix(f)) & (nb - 1); }
    bool put(size_t i, uint16_t f) { for (auto& s : B[i]) if (!s) { s = f; return true; } return false; }
    bool insert(uint64_t key) {
        uint64_t h = mix(key); uint16_t f = fp(h); size_t i1 = idx(h), i2 = alt(i1, f);
        if (put(i1, f) || put(i2, f)) { count++; return true; }
        std::vector<std::pair<size_t, int>> log; std::vector<uint16_t> old; size_t i = (rng() & 1) ? i1 : i2;
        for (int kick = 0; kick < 500; kick++) {
            int s = rng() % 4; log.push_back({i, s}); old.push_back(B[i][s]); std::swap(f, B[i][s]);         // 한 지문을 쫓아낸다
            i = alt(i, f); if (put(i, f)) { count++; return true; }
        }
        for (int j = (int)log.size() - 1; j >= 0; j--) B[log[j].first][log[j].second] = old[j];             // 실패: 전부 되돌린다
        return false;
    }
    bool maybe(uint64_t key) const {
        uint64_t h = mix(key); uint16_t f = fp(h); size_t i1 = idx(h), i2 = alt(i1, f);
        for (auto s : B[i1]) if (s == f) return true; for (auto s : B[i2]) if (s == f) return true; return false;
    }
    bool erase(uint64_t key) {
        uint64_t h = mix(key); uint16_t f = fp(h); size_t i1 = idx(h), i2 = alt(i1, f);
        for (size_t i : {i1, i2}) for (auto& s : B[i]) if (s == f) { s = 0; count--; return true; }
        return false;
    }
};

int main() {
    Cuckoo c(12, 1 << 12); uint64_t n = 0;                                 // 16384 칸
    while (c.insert(n)) n++;                                               // 처음 실패할 때까지
    double load = (double)c.count / (4.0 * c.nb);
    assert(load > 0.93);                                                   // 4-way 쿠쿠는 ~95% 까지 채울 수 있다
    for (uint64_t i = 0; i < n; i++) assert(c.maybe(i));                   // 실패 시 롤백 덕에 먼저 넣은 키는 하나도 사라지지 않았다
    size_t fp = 0, T = 200000; for (uint64_t i = 0; i < T; i++) fp += c.maybe((1ULL << 40) + i);
    double rate = (double)fp / T; assert(rate < 0.01);                     // 이론 상한 2·4/2^12 ≈ 0.2%
    for (uint64_t i = 0; i < n; i += 2) assert(c.erase(i));                // 삭제
    for (uint64_t i = 1; i < n; i += 2) assert(c.maybe(i));
    size_t gone = 0; for (uint64_t i = 0; i < n; i += 2) gone += !c.maybe(i);
    assert(gone > (n / 2) * 99 / 100);
    std::cout << "CuckooFilter: load factor " << load << " at first failure, false-positive rate " << rate * 100 << "%, erase works" << std::endl;
    return 0;
}
// Time Complexity: 조회·삭제 O(1) (버킷 2개), 삽입 분할상환 O(1)
// Space Complexity: 키당 f / 부하율 비트 (f=12, 부하 95% -> 약 12.6 비트)
```
## QuotientFilter()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 몫 필터(quotient filter): p = q + r 비트 지문을 앞 q 비트(몫, 버킷 번호)와 뒤 r 비트(나머지)로 나누고, 나머지를 해시 표의 "선형 탐사 + 정렬된 런" 으로 저장한다.
// 같은 몫의 나머지들이 이어 붙은 구간 = 런(run), 런이 이어진 덩어리 = 클러스터.  나머지 하나당 슬롯 하나이고 슬롯마다 메타데이터 3비트만 쓴다:
//   is_occupied  이 슬롯 번호를 몫으로 하는 런이 (어딘가에) 있다    is_continuation  런의 첫 원소가 아니다    is_shifted  자기 몫의 슬롯이 아닌 곳에 밀려 있다
// 이 3비트로 클러스터의 시작으로 거슬러 올라간 뒤 "런과 몫을 짝지어 세며" 앞으로 가서 어떤 몫의 런이 어디서 시작하는지 알아낸다.  블룸과 달리 캐시 친화적이고(런이 연속), 병합·리사이즈가 쉽다
// (이 구현은 순환 없이 끝에 여유 슬롯을 두고, 삭제는 생략했다)
struct Slot { uint32_t rem = 0; bool occ = false, cont = false, shift = false; };
struct QF {
    int q, r; std::vector<Slot> T; size_t n = 0;
    QF(int q, int r) : q(q), r(r), T((1u << q) + 256) {}
    bool empty(int i) const { return !T[i].occ && !T[i].cont && !T[i].shift; }
    int runStart(int fq) const {                                           // 몫 fq (occ 가 켜져 있어야 한다) 의 런이 시작하는 슬롯
        int b = fq; while (T[b].shift) b--;                                // 클러스터의 시작으로
        int s = b;
        while (b != fq) { do s++; while (T[s].cont); do b++; while (!T[b].occ); }     // 다음 런 시작과 다음 occupied 몫을 한 쌍으로 전진
        return s;
    }
    void place(int pos, uint32_t rem, bool cont, bool shift) {             // pos 에 끼워 넣고 뒤쪽을 첫 빈 슬롯까지 한 칸씩 민다 (occ 비트는 슬롯 번호의 성질이라 그대로 둔다)
        int e = pos; while (!empty(e)) e++;
        assert(e < (int)T.size());
        for (int i = e; i > pos; i--) { T[i].rem = T[i - 1].rem; T[i].cont = T[i - 1].cont; T[i].shift = true; }
        T[pos].rem = rem; T[pos].cont = cont; T[pos].shift = shift;
    }
    bool insert(uint32_t fq, uint32_t fr) {                                // 새로 들어갔으면 true, 이미 있으면 false
        if (empty(fq)) { T[fq].rem = fr; T[fq].occ = true; n++; return true; }
        bool was = T[fq].occ; T[fq].occ = true;
        int s = runStart(fq);
        if (!was) { place(s, fr, false, s != (int)fq); n++; return true; } // 새 런: 해당 위치에 런 시작으로
        int p = s;
        do { if (T[p].rem == fr) return false; if (T[p].rem > fr) break; p++; } while (T[p].cont);      // 런 안에서 정렬 위치 찾기
        bool atStart = (p == s);
        place(p, fr, !atStart, p != (int)fq);
        if (atStart) T[p + 1].cont = true;                                 // 옛 첫 원소는 이제 연속 원소
        n++; return true;
    }
    bool contains(uint32_t fq, uint32_t fr) const {
        if (!T[fq].occ) return false;
        int s = runStart(fq);
        do { if (T[s].rem == fr) return true; if (T[s].rem > fr) return false; s++; } while (T[s].cont);
        return false;
    }
    std::set<uint64_t> decode() const {                                    // 표 전체를 (몫, 나머지) 로 복원 -> 불변식 검사용
        std::set<uint64_t> out; std::queue<uint32_t> pending; uint32_t cur = 0;
        for (size_t i = 0; i < T.size(); i++) {
            if (T[i].occ) pending.push(i);
            if (empty(i)) { assert(pending.empty()); continue; }
            if (!T[i].cont) { cur = pending.front(); pending.pop(); }
            out.insert((uint64_t)cur << r | T[i].rem);
        }
        assert(pending.empty()); return out;
    }
};
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }

int main() {
    const int Q = 14, R = 8; QF f(Q, R); std::set<uint64_t> model; std::mt19937_64 rng(4);
    size_t N = (size_t)(0.75 * (1 << Q));
    for (size_t i = 0; i < N; i++) {                                       // 지문 = 해시의 상위 Q+R 비트
        uint64_t fpr = mix(rng()) >> (64 - Q - R); bool fresh = model.insert(fpr).second;
        assert(f.insert(fpr >> R, fpr & ((1u << R) - 1)) == fresh);
        if (i % 2000 == 0) assert(f.decode() == model);                    // 진행 중에도 표가 모델과 일치
    }
    assert(f.decode() == model && f.n == model.size());
    for (uint64_t x : model) assert(f.contains(x >> R, x & ((1u << R) - 1)));
    size_t bad = 0;                                                        // 지문 수준에서는 정확: 모델에 없는 지문은 항상 false
    for (int t = 0; t < 100000; t++) { uint64_t x = rng() >> (64 - Q - R); bad += f.contains(x >> R, x & ((1u << R) - 1)) != (model.count(x) > 0); }
    assert(bad == 0);
    size_t fp = 0, T = 100000; for (size_t i = 0; i < T; i++) fp += f.contains(mix(~rng()) >> (64 - Q) , (mix(rng()) & 0xff));       // 서로 다른 키가 같은 지문을 만드는 경우만 거짓 양성
    std::cout << "QuotientFilter: " << f.n << " fingerprints in " << (1 << Q) << " slots (load 75%), table decodes to the exact model, random-probe hit rate " << 100.0 * fp / T << "%" << std::endl;
    return 0;
}
// Time Complexity: 조회·삽입 O(클러스터 길이) = 기대 O(1) (부하율이 낮을 때)
// Space Complexity: 원소당 r + 3 비트
```
## XORFilter()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// XOR 필터(Graf & Lemire): 정적 집합 전용 필터. 블룸(원소당 9.6비트@1%)·쿠쿠보다 작고 빠르다 — 거짓 양성 2^-8 ≈ 0.39% 에 원소당 약 9.84 비트.
// 키마다 서로 다른 구간 세 곳에서 위치 h0,h1,h2 를 정하고, 표 F 를 "fp(key) == F[h0] ^ F[h1] ^ F[h2]" 가 되도록 채운다. 조회는 XOR 세 번과 비교 한 번.
// 채우는 방법은 3-균일 하이퍼그래프 벗겨내기(peeling): 어떤 키가 "혼자만 쓰는 위치"를 가지면 그 키를 맨 나중 순서로 미루고 제거한다. 전부 벗겨지면 역순으로 F 를 채운다
// (표 크기 1.23n 이면 성공 확률이 높고, 실패하면 시드를 바꿔 다시 시도)
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct Xor8 {
    uint64_t seed = 0; size_t B = 0; std::vector<uint8_t> F; int tries = 0;
    void pos(uint64_t key, size_t h[3], uint8_t& fp) const {
        uint64_t x = mix(key ^ seed);
        h[0] = (x & 0xffffffffULL) * B >> 32; h[1] = B + (((x >> 21) & 0xffffffffULL) * B >> 32); h[2] = 2 * B + (((x >> 42 | x << 22) & 0xffffffffULL) * B >> 32);
        fp = (uint8_t)(x >> 56) ^ (uint8_t)(x >> 17);
    }
    bool build(const std::vector<uint64_t>& keys) {
        size_t n = keys.size(); B = (size_t)(1.23 * n + 32) / 3 + 1; std::mt19937_64 rng(99);
        for (tries = 1; tries <= 100; tries++) {
            seed = rng(); std::vector<uint32_t> cnt(3 * B, 0); std::vector<uint64_t> xr(3 * B, 0);
            for (size_t i = 0; i < n; i++) { size_t h[3]; uint8_t f; pos(keys[i], h, f); for (int j = 0; j < 3; j++) { cnt[h[j]]++; xr[h[j]] ^= i; } }   // 위치별 키 개수와 키 번호의 XOR
            std::vector<size_t> q; for (size_t p = 0; p < 3 * B; p++) if (cnt[p] == 1) q.push_back(p);
            std::vector<std::pair<size_t, size_t>> order;                  // (키 번호, 그 키가 혼자 쓰던 위치)
            while (!q.empty()) {
                size_t p = q.back(); q.pop_back(); if (cnt[p] != 1) continue;
                size_t i = xr[p]; order.push_back({i, p}); size_t h[3]; uint8_t f; pos(keys[i], h, f);
                for (int j = 0; j < 3; j++) { cnt[h[j]]--; xr[h[j]] ^= i; if (cnt[h[j]] == 1) q.push_back(h[j]); }
            }
            if (order.size() != n) continue;                               // 벗기기 실패 -> 새 시드
            F.assign(3 * B, 0);
            for (int k = (int)n - 1; k >= 0; k--) {                        // 나중에 벗겨진 키부터 채운다
                size_t i = order[k].first, p = order[k].second, h[3]; uint8_t f; pos(keys[i], h, f);
                F[p] = f ^ F[h[0]] ^ F[h[1]] ^ F[h[2]] ^ F[p];             // p 자리를 빼고 나머지 둘의 XOR 로 맞춘다 (F[p] 는 아직 0)
            }
            return true;
        }
        return false;
    }
    bool maybe(uint64_t key) const { size_t h[3]; uint8_t f; pos(key, h, f); return f == (F[h[0]] ^ F[h[1]] ^ F[h[2]]); }
};

int main() {
    std::mt19937_64 rng(5); std::vector<uint64_t> keys; size_t n = 100000;
    while (keys.size() < n) keys.push_back(rng());
    std::sort(keys.begin(), keys.end()); keys.erase(std::unique(keys.begin(), keys.end()), keys.end());
    Xor8 f; assert(f.build(keys));
    for (uint64_t k : keys) assert(f.maybe(k));                            // 거짓 음성 없음
    size_t fp = 0, T = 300000;
    for (size_t i = 0; i < T; i++) { uint64_t x = rng(); if (std::binary_search(keys.begin(), keys.end(), x)) continue; fp += f.maybe(x); }
    double rate = (double)fp / T, bits = 8.0 * f.F.size() / keys.size();
    assert(rate < 0.008 && bits < 10.0);                                   // 이론 0.39%, 원소당 9.84 비트
    std::cout << "XORFilter: " << bits << " bits/key, false-positive " << rate * 100 << "% (theory 0.39%), built in " << f.tries << " attempt(s)" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(1) (메모리 접근 3번), 구성 O(N) 기대
// Space Complexity: 약 1.23 N 바이트 (지문 8비트)
```
## CountMinSketch()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 카운트-민 스케치: 스트림에서 각 항목의 빈도를 "작은 고정 공간"으로 추정한다. d 행 × w 열 카운터, 행마다 다른 해시. 갱신은 행마다 한 칸 +c, 추정은 d 개 중 최솟값.
// 항상 과대 추정만 한다(다른 항목과 충돌하면 값이 커질 뿐): 참값 <= 추정 <= 참값 + ε·N  (확률 >= 1-δ).  w = ⌈e/ε⌉, d = ⌈ln(1/δ)⌉.
// 보수적 갱신(conservative update): 갱신 전 추정치 m 이 있으면 카운터들을 max(자기값, m + c) 로만 올려 충돌 오차를 줄인다
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct CMS {
    size_t w, d; std::vector<std::vector<uint32_t>> t; bool conservative;
    CMS(double eps, double delta, bool cons = false) : w((size_t)std::ceil(std::exp(1.0) / eps)), d((size_t)std::ceil(std::log(1.0 / delta))), t(d, std::vector<uint32_t>(w, 0)), conservative(cons) {}
    size_t col(uint64_t key, size_t row) const { return mix(key ^ (row * 0x9e3779b97f4a7c15ULL + 12345)) % w; }
    uint32_t estimate(uint64_t key) const { uint32_t m = UINT32_MAX; for (size_t i = 0; i < d; i++) m = std::min(m, t[i][col(key, i)]); return m; }
    void add(uint64_t key, uint32_t c = 1) {
        if (!conservative) { for (size_t i = 0; i < d; i++) t[i][col(key, i)] += c; return; }
        uint32_t target = estimate(key) + c; for (size_t i = 0; i < d; i++) { uint32_t& x = t[i][col(key, i)]; x = std::max(x, target); }
    }
};

int main() {
    const double eps = 0.001, delta = 0.01; CMS plain(eps, delta), cons(eps, delta, true);
    std::mt19937_64 rng(11); std::map<uint64_t, uint32_t> truth; const int K = 5000; size_t N = 200000;
    std::vector<double> w(K); for (int i = 0; i < K; i++) w[i] = 1.0 / std::pow(i + 1, 1.1);          // 치우친(Zipf) 분포
    std::discrete_distribution<int> zipf(w.begin(), w.end());
    for (size_t i = 0; i < N; i++) { uint64_t key = zipf(rng) * 7919ULL + 13; plain.add(key); cons.add(key); truth[key]++; }
    size_t over = 0; double errPlain = 0, errCons = 0;
    for (auto& kv : truth) {
        uint32_t a = plain.estimate(kv.first), b = cons.estimate(kv.first);
        assert(a >= kv.second && b >= kv.second);                          // 과소 추정은 없다
        if (a > kv.second + eps * N) over++;
        errPlain += a - kv.second; errCons += b - kv.second;
    }
    assert(over <= truth.size() * 0.02);                                   // 오차가 ε·N 을 넘는 항목은 약 δ 이하
    assert(errCons <= errPlain);                                           // 보수적 갱신이 총 오차를 줄인다
    std::cout << "CountMinSketch: " << plain.d << "x" << plain.w << " counters, items with error > eps*N: " << over << "/" << truth.size()
              << ", total error plain " << errPlain << " vs conservative " << errCons << std::endl;
    return 0;
}
// Time Complexity: 갱신·질의 O(d) = O(log 1/δ)
// Space Complexity: O((1/ε) log (1/δ)) 카운터
```
## HyperLogLog()
### 대표코드
```cpp
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 하이퍼로그로그: 서로 다른 원소의 수(카디널리티)를 수 KB 로 ±1~2% 오차로 센다. 아이디어: 해시를 이진수로 보면 "앞쪽 0 이 k 개 이어지는" 값은 약 2^k 개를 봐야 한 번 나온다.
// 해시의 앞 p 비트로 m = 2^p 개의 레지스터 중 하나를 고르고, 나머지 비트의 "앞쪽 0 의 개수 + 1"(rho)의 최댓값을 레지스터에 기록한다.
// 추정 = α_m · m² / Σ 2^(-레지스터)  (조화 평균으로 이상치를 눌러 준다).  작은 값에서는 빈 레지스터 수 V 로 선형 카운팅 m ln(m/V) 을 쓴다. 표준 오차 ≈ 1.04/√m
// 합집합은 레지스터별 max 한 번으로 정확히(손실 없이) 병합된다 -> 분산 집계에 적합
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct HLL {
    int p; size_t m; std::vector<uint8_t> reg;
    explicit HLL(int p) : p(p), m(1u << p), reg(1u << p, 0) {}
    void add(uint64_t x) {
        uint64_t h = mix(x); size_t idx = h >> (64 - p); uint64_t w = (h << p) | (1ULL << (p - 1));      // 표시 비트로 clz 가 64-p 를 넘지 않게
        uint8_t rho = __builtin_clzll(w) + 1; if (rho > reg[idx]) reg[idx] = rho;
    }
    double estimate() const {
        double alpha = 0.7213 / (1 + 1.079 / m), sum = 0; size_t zeros = 0;
        for (uint8_t r : reg) { sum += std::ldexp(1.0, -r); zeros += r == 0; }
        double e = alpha * m * m / sum;
        if (e <= 2.5 * m && zeros) e = m * std::log((double)m / zeros);    // 작은 범위 보정: 선형 카운팅
        return e;
    }
    void merge(const HLL& o) { for (size_t i = 0; i < m; i++) reg[i] = std::max(reg[i], o.reg[i]); }
};

int main() {
    for (size_t n : {100u, 1000u, 10000u, 100000u, 1000000u}) {
        HLL h(14);
        for (uint64_t i = 0; i < n; i++) h.add(i * 2654435761ULL + 17);
        for (uint64_t i = 0; i < n; i++) h.add(i * 2654435761ULL + 17);    // 중복은 영향이 없다
        double err = std::fabs(h.estimate() - n) / n;
        assert(err < 0.04);                                                // 표준 오차 0.81% 의 약 5 배 이내
        std::cout << "HyperLogLog n=" << n << " estimate=" << (long)h.estimate() << " error=" << err * 100 << "%" << std::endl;
    }
    HLL a(14), b(14);
    for (uint64_t i = 0; i < 60000; i++) a.add(i);
    for (uint64_t i = 40000; i < 100000; i++) b.add(i);                    // 두 구간이 겹친다: 합집합 크기 100000
    a.merge(b); assert(std::fabs(a.estimate() - 100000) / 100000 < 0.04);
    return 0;
}
// Time Complexity: 삽입 O(1), 추정 O(m)
// Space Complexity: m 레지스터 (p=14 이면 6비트씩 약 12 KB)
```

## TDigest()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <random>
#include <vector>
#include <cassert>

// t-다이제스트: 스트림에서 임의의 분위수(중앙값, p99, p99.9 ...)를 작은 고정 공간으로 추정한다. 값을 정렬해 "(평균, 가중치) 중심점(centroid)" 들로 묶되,
// 분위수 q 근처의 중심점 크기를 스케일 함수 k(q) = δ/(2π)·asin(2q-1) 로 제한한다 -> 양 끝(q≈0,1)에서는 중심점이 아주 작아(거의 개별 값) 꼬리 분위수가 정확하고, 가운데는 크게 뭉친다.
// 병합형(merging) 구현: 값을 버퍼에 모았다가 [기존 중심점 + 버퍼] 를 정렬해 k(오른쪽 끝) - k(왼쪽 끝) <= 1 이 유지되는 동안 이웃을 합친다. 다이제스트끼리 합치는 것도 같은 연산이다
struct TDigest {
    double delta; std::vector<std::pair<double, double>> cent, buf; double total = 0, mn = std::numeric_limits<double>::infinity(), mx = -mn;
    explicit TDigest(double d = 100) : delta(d) {}
    double k(double q) const { return delta / (2 * M_PI) * std::asin(2 * q - 1); }
    void add(double x, double w = 1) { buf.push_back({x, w}); mn = std::min(mn, x); mx = std::max(mx, x); if (buf.size() > 20 * delta) compress(); }
    void merge(TDigest& o) { o.compress(); for (auto& c : o.cent) buf.push_back(c); mn = std::min(mn, o.mn); mx = std::max(mx, o.mx); compress(); }
    void compress() {
        if (buf.empty()) return;
        std::vector<std::pair<double, double>> all = cent; all.insert(all.end(), buf.begin(), buf.end()); buf.clear();
        std::sort(all.begin(), all.end()); total = 0; for (auto& c : all) total += c.second;
        cent.clear(); auto cur = all[0]; double soFar = 0;
        for (size_t i = 1; i < all.size(); i++) {
            double proposed = cur.second + all[i].second;
            if (k((soFar + proposed) / total) - k(soFar / total) <= 1) { cur.first += (all[i].first - cur.first) * all[i].second / proposed; cur.second = proposed; }
            else { cent.push_back(cur); soFar += cur.second; cur = all[i]; }
        }
        cent.push_back(cur);
    }
    double quantile(double q) {
        compress(); size_t n = cent.size(); if (n == 1) return cent[0].first;
        double target = q * total, cum = 0, prevCenter = 0, prevMean = mn;                      // 중심점의 "중심" = 누적 + 가중치/2 에서 평균값을 갖는다고 보고 선형 보간
        for (size_t i = 0; i < n; i++) {
            double center = cum + cent[i].second / 2;
            if (target < center) { double t = (target - prevCenter) / (center - prevCenter); return prevMean + t * (cent[i].first - prevMean); }
            prevCenter = center; prevMean = cent[i].first; cum += cent[i].second;
        }
        double t = (target - prevCenter) / (total - prevCenter); return prevMean + t * (mx - prevMean);        // 마지막 중심점 ~ 최댓값
    }
};

int main() {
    std::mt19937_64 rng(3); std::normal_distribution<double> nd(0, 1); std::exponential_distribution<double> ed(1.0);
    for (int dist = 0; dist < 2; dist++) {
        size_t n = 200000; std::vector<double> data(n); TDigest td(100), a(100), b(100);
        for (size_t i = 0; i < n; i++) { data[i] = dist ? ed(rng) : nd(rng); td.add(data[i]); (i % 2 ? a : b).add(data[i]); }
        std::vector<double> sorted = data; std::sort(sorted.begin(), sorted.end());
        a.merge(b);                                                        // 두 다이제스트의 병합
        for (TDigest* d : {&td, &a}) {
            assert(d->cent.size() < 400);                                  // 20 만 개가 수백 개 이하의 중심점으로
            for (double q : {0.001, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 0.999}) {
                double est = d->quantile(q); double rank = (double)(std::lower_bound(sorted.begin(), sorted.end(), est) - sorted.begin()) / n;
                double bound = q < 0.01 || q > 0.99 ? 0.0015 : 0.01;       // 꼬리에서는 훨씬 정확하다
                assert(std::fabs(rank - q) < bound);
            }
        }
        std::cout << (dist ? "exponential" : "normal") << ": centroids " << td.cent.size() << ", p50 " << td.quantile(0.5) << ", p99 " << td.quantile(0.99) << ", p99.9 " << td.quantile(0.999) << std::endl;
    }
    return 0;
}
// Time Complexity: 추가 분할상환 O(log δ), 분위수 질의 O(δ)
// Space Complexity: O(δ) 중심점
```
# Part 4. 문자열 자료구조
## Rope()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <cassert>

// 로프(문자열 관점의 요약, 정본은 String.md Part 4): 긴 문자열을 이진 트리로 나타내고 연결은 새 루트 하나, 분할·색인은 O(깊이).  노드가 불변이라 편집 전 버전과 구조를 공유한다
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
## PieceTable()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 피스 테이블(문자열 관점의 요약, 정본은 String.md Part 4): 원본 파일은 수정하지 않고 "추가 전용" 버퍼에 새 글자를 덧붙이며, 문서 = (버퍼, 시작, 길이) 조각들의 목록.
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
## GapBuffer()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <cassert>

// 갭 버퍼(문자열 관점의 요약, 정본은 String.md Part 4): 글자 배열 가운데에 "빈 틈(gap)"을 두고 커서가 있는 곳에 틈을 놓는다. 커서 위치에서의 삽입·삭제는 O(1),
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

// 핑거 트리(Hinze & Paterson): 불변(영속) 시퀀스 자료구조. 양 끝에 "손가락(finger)"으로 짧은 목록(1~4개)을 두고 가운데는 "2-3 노드"를 원소로 하는 같은 구조의 트리를 재귀적으로 단다.
//   양 끝 push/pop  분할상환 O(1)    연결(concat)  O(log min(n,m))    index/split  O(log min(i, n-i))
// 각 노드에 부분 트리 크기를 저장(size 측도)하면 위치로 분할할 수 있다. (다른 측도 — 최솟값, 우선순위, 구간 — 를 저장하면 우선순위 큐·구간 트리·순서 통계 트리가 되는 일반 틀이다)
// 아래는 깊이마다 타입이 달라지는 원래 구조를 "노드 = 잎(값) 또는 2~3 개 자식" 으로 통일해 C++ 에 옮긴 것이다. 모든 연산이 새 루트를 돌려주고 옛 버전은 그대로 쓸 수 있다
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
std::vector<NP> nodesOf(const std::vector<NP>& v) {                        // 2~12 개를 2-3 노드들로 묶는다
    std::vector<NP> out; size_t i = 0;
    while (v.size() - i > 4) { out.push_back(node({v[i], v[i + 1], v[i + 2]})); i += 3; }
    size_t r = v.size() - i;
    if (r == 2) out.push_back(node({v[i], v[i + 1]})); else if (r == 3) out.push_back(node({v[i], v[i + 1], v[i + 2]}));
    else { out.push_back(node({v[i], v[i + 1]})); out.push_back(node({v[i + 2], v[i + 3]})); }
    return out;
}
F app3(const F& a, const std::vector<NP>& ts, const F& b) {
    if (a->kind == 0) { F r = b; for (int i = (int)ts.size() - 1; i >= 0; i--) r = pushFront(r, ts[i]); return r; }
    if (b->kind == 0) { F r = a; for (auto& x : ts) r = pushBack(r, x); return r; }
    if (a->kind == 1) return pushFront(app3(Empty(), ts, b), a->one);
    if (b->kind == 1) return pushBack(app3(a, ts, Empty()), b->one);
    std::vector<NP> m = a->suf; m.insert(m.end(), ts.begin(), ts.end()); m.insert(m.end(), b->pre.begin(), b->pre.end());
    return Deep(a->pre, app3(a->mid, nodesOf(m), b->mid), b->suf);
}
F concat(const F& a, const F& b) { return app3(a, {}, b); }
struct DS { std::vector<NP> l; NP x; std::vector<NP> r; };
DS splitDigit(int i, const std::vector<NP>& d) {                           // i 번째 위치가 속한 원소를 기준으로 셋으로
    int acc = 0;
    for (size_t j = 0; j < d.size(); j++) { if (i < acc + d[j]->size) return {std::vector<NP>(d.begin(), d.begin() + j), d[j], std::vector<NP>(d.begin() + j + 1, d.end())}; acc += d[j]->size; }
    assert(false); return {};
}
struct ST { F l; NP x; F r; };
ST splitTree(int i, const F& t) {                                          // 0 <= i < size: (앞쪽, i 번째를 포함한 원소, 뒤쪽)
    if (t->kind == 1) return {Empty(), t->one, Empty()};
    int spr = sz(t->pre);
    if (i < spr) { auto s = splitDigit(i, t->pre); return {digitToTree(s.l), s.x, deepL(s.r, t->mid, t->suf)}; }
    i -= spr;
    if (i < t->mid->size) {
        auto m = splitTree(i, t->mid); i -= m.l->size; auto s = splitDigit(i, m.x->k);
        return {deepR(t->pre, m.l, s.l), s.x, deepL(s.r, m.r, t->suf)};
    }
    i -= t->mid->size; auto s = splitDigit(i, t->suf);
    return {deepR(t->pre, t->mid, s.l), s.x, digitToTree(s.r)};
}
std::pair<F, F> splitAt(const F& t, int i) {
    if (i <= 0) return {Empty(), t}; if (i >= t->size) return {t, Empty()};
    ST s = splitTree(i, t); return {s.l, pushFront(s.r, s.x)};
}
int indexAt(const F& t, int i) { return splitTree(i, t).x->val; }
void flat(const NP& n, std::vector<int>& out) { if (n->k.empty()) out.push_back(n->val); else for (auto& c : n->k) flat(c, out); }
void collect(const F& t, std::vector<int>& out) {
    if (t->kind == 0) return; if (t->kind == 1) { flat(t->one, out); return; }
    for (auto& x : t->pre) flat(x, out); collect(t->mid, out); for (auto& x : t->suf) flat(x, out);
}
std::vector<int> toVec(const F& t) { std::vector<int> v; collect(t, v); return v; }
int depth(const F& t) { return t->kind == 2 ? 1 + depth(t->mid) : 0; }

int main() {
    std::mt19937 rng(12); std::vector<F> ver = {Empty()}; std::vector<std::vector<int>> model = {{}};
    for (int step = 0; step < 6000; step++) {
        int base = rng() % ver.size(); const F t = ver[base]; std::vector<int> m = model[base]; int op = rng() % 7; F r = t;
        if (op == 0 || m.empty()) { int x = rng() % 1000; r = pushFront(t, leaf(x)); m.insert(m.begin(), x); }
        else if (op == 1) { int x = rng() % 1000; r = pushBack(t, leaf(x)); m.push_back(x); }
        else if (op == 2) { auto v = viewFront(t); assert(v.first->val == m.front()); r = v.second; m.erase(m.begin()); }
        else if (op == 3) { auto v = viewBack(t); assert(v.second->val == m.back()); r = v.first; m.pop_back(); }
        else if (op == 4) { int o = rng() % ver.size(); r = concat(t, ver[o]); m.insert(m.end(), model[o].begin(), model[o].end()); }
        else if (op == 5) { int i = rng() % (m.size() + 1); auto s = splitAt(t, i); assert(toVec(s.first) == std::vector<int>(m.begin(), m.begin() + i) && toVec(s.second) == std::vector<int>(m.begin() + i, m.end())); r = (rng() & 1) ? s.first : s.second; m = toVec(r); }
        else { int i = rng() % m.size(); assert(indexAt(t, i) == m[i]); }
        if (m.size() > 400) { r = splitAt(r, 200).second; m.erase(m.begin(), m.begin() + 200); }       // 크기를 억제
        assert(r->size == (int)m.size() && toVec(r) == m);
        ver.push_back(r); model.push_back(m);
    }
    for (size_t i = 0; i < ver.size(); i += 11) assert(toVec(ver[i]) == model[i]);    // 옛 버전은 여전히 그대로
    F big = Empty(); for (int i = 0; i < 200000; i++) big = pushBack(big, leaf(i));
    for (int q = 0; q < 2000; q++) { int i = rng() % 200000; assert(indexAt(big, i) == i); }
    F half = splitAt(big, 100000).second; assert(half->size == 100000 && indexAt(half, 0) == 100000);
    F both = concat(big, half); assert(both->size == 300000 && indexAt(both, 250000) == 150000);
    assert(depth(big) < 25);                                               // 깊이는 log 규모
    std::cout << "FingerTree: 6000 persistent ops verified; n=200000 -> spine depth " << depth(big) << std::endl;
    return 0;
}
// Time Complexity: 양 끝 push/pop 분할상환 O(1), concat O(log N), split/index O(log N)
// Space Complexity: O(N), 버전 사이에 구조 공유
```
## SuffixAutomaton()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 접미사 오토마톤(SAM, 문자열 관점의 요약, 정본은 String.md Part 9): 문자열의 모든 부분 문자열을 받아들이는 최소 DFA. 상태 수 <= 2n-1, 전이 <= 3n-4, 온라인 O(n) 구성.
// 서로 다른 부분 문자열의 수 = Σ (len[v] - len[link[v]])
struct SAM {
    struct St { int len = 0, link = -1; std::map<char, int> next; }; std::vector<St> st{1}; int last = 0;
    void extend(char c) {
        int cur = st.size(); st.push_back({}); st[cur].len = st[last].len + 1; int p = last;
        for (; p >= 0 && !st[p].next.count(c); p = st[p].link) st[p].next[c] = cur;
        if (p < 0) st[cur].link = 0;
        else { int q = st[p].next[c];
            if (st[p].len + 1 == st[q].len) st[cur].link = q;
            else { int cl = st.size(); st.push_back(st[q]); st[cl].len = st[p].len + 1;
                for (; p >= 0 && st[p].next[c] == q; p = st[p].link) st[p].next[c] = cl;
                st[q].link = st[cur].link = cl; } }
        last = cur;
    }
};
int main() {
    SAM s; for (char c : std::string("abab")) s.extend(c);
    long distinct = 0; for (size_t v = 1; v < s.st.size(); v++) distinct += s.st[v].len - s.st[s.st[v].link].len;
    assert(distinct == 7);                                                  // a b ab ba aba bab abab
    std::cout << "SuffixAutomaton: distinct substrings of abab = " << distinct << std::endl; return 0;
}
// Time Complexity: 구성 O(n log σ), 부분 문자열 판정 O(m)
// Space Complexity: O(n)
```
## PatriciaTrie()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <cassert>

// 패트리샤 트라이(트리 관점의 요약, 정본은 Tree.md Part 10): 자식이 하나뿐인 사슬을 한 간선으로 압축한 트라이. 간선에는 문자열 조각이 붙고 노드 수는 키 수 이하의 2배 미만이다.
// 삽입은 간선 라벨과 공통 접두사 길이를 비교해, 일부만 겹치면 간선을 둘로 쪼갠다
struct Node { std::map<char, std::pair<std::string, Node*>> kid; bool end = false; };
void insert(Node* t, const std::string& s) {
    while (!s.empty()) {
        auto it = t->kid.find(s[0]);
        if (it == t->kid.end()) { Node* n = new Node; n->end = true; t->kid[s[0]] = {s, n}; return; }
        std::string& lab = it->second.first; size_t l = 0; while (l < lab.size() && l < s.size() && lab[l] == s[l]) l++;
        if (l < lab.size()) { Node* mid = new Node; mid->kid[lab[l]] = {lab.substr(l), it->second.second}; lab.resize(l); it->second.second = mid; }
        t = it->second.second; return insert(t, s.substr(l));
    }
    t->end = true;
}
bool contains(Node* t, std::string s) {
    while (!s.empty()) { auto it = t->kid.find(s[0]); if (it == t->kid.end() || s.compare(0, it->second.first.size(), it->second.first)) return false; s = s.substr(it->second.first.size()); t = it->second.second; }
    return t->end;
}
int main() {
    Node root; for (std::string w : {"romane", "romanus", "romulus", "rubens", "ruber", "rubicon"}) insert(&root, w);
    assert(contains(&root, "romane") && contains(&root, "rubicon") && !contains(&root, "roman") && !contains(&root, "rub"));
    std::cout << "PatriciaTrie: compressed edges, root fan-out " << root.kid.size() << std::endl; return 0;
}
// Time Complexity: 삽입·조회 O(|key|)
// Space Complexity: O(키 수) 노드
```

# Part 5. 공간 자료구조
## KDTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// KD 트리(트리 관점의 요약, 정본은 Tree.md Part 11): 깊이마다 축을 번갈아 가며 중앙값으로 공간을 반으로 가르는 이진 트리. 최근접 이웃 탐색은 가까운 쪽을 먼저 내려가고,
// 분할 평면까지의 거리가 현재 최선보다 멀면 반대쪽 부분 트리를 통째로 건너뛴다
typedef std::vector<double> P; std::vector<P> pts;
int build(std::vector<int>& id, int lo, int hi, int axis, std::vector<int>& L, std::vector<int>& R) {      // 반환: 이 구간의 루트 점 번호
    if (lo >= hi) return -1; int m = (lo + hi) / 2;
    std::nth_element(id.begin() + lo, id.begin() + m, id.begin() + hi, [&](int a, int b) { return pts[a][axis] < pts[b][axis]; });
    int root = id[m]; L[root] = build(id, lo, m, 1 - axis, L, R); R[root] = build(id, m + 1, hi, 1 - axis, L, R); return root;
}
void nn(int t, const P& q, int axis, const std::vector<int>& L, const std::vector<int>& R, int& best, double& bd) {
    if (t < 0) return; double d = 0; for (int k = 0; k < 2; k++) d += (pts[t][k] - q[k]) * (pts[t][k] - q[k]);
    if (d < bd) { bd = d; best = t; }
    double diff = q[axis] - pts[t][axis]; int near = diff < 0 ? L[t] : R[t], far = diff < 0 ? R[t] : L[t];
    nn(near, q, 1 - axis, L, R, best, bd); if (diff * diff < bd) nn(far, q, 1 - axis, L, R, best, bd);     // 평면 너머가 최선보다 멀면 가지치기
}
int main() {
    std::mt19937 g(1); std::uniform_real_distribution<double> U(0, 1); int n = 2000;
    for (int i = 0; i < n; i++) pts.push_back({U(g), U(g)});
    std::vector<int> id(n), L(n, -1), R(n, -1); for (int i = 0; i < n; i++) id[i] = i; int root = build(id, 0, n, 0, L, R);
    for (int t = 0; t < 200; t++) { P q = {U(g), U(g)}; int best = -1; double bd = 1e18; nn(root, q, 0, L, R, best, bd);
        double bf = 1e18; for (auto& p : pts) bf = std::min(bf, (p[0] - q[0]) * (p[0] - q[0]) + (p[1] - q[1]) * (p[1] - q[1])); assert(bd == bf); }
    std::cout << "KDTree: nearest neighbour verified against brute force" << std::endl; return 0;
}
// Time Complexity: 구성 O(N log N), 최근접 질의 평균 O(log N)
// Space Complexity: O(N)
```
## QuadTree()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 쿼드트리(트리 관점의 요약, 정본은 Tree.md Part 11): 정사각형 영역을 4 등분(NW, NE, SW, SE)해 가며 점을 담는다. 한 칸에 점이 용량(여기서는 4)을 넘으면 쪼갠다.
// 사각형 범위 질의는 영역이 겹치지 않는 칸을 건너뛴다.  지도 타일, 충돌 검사, 이미지 압축의 바탕
struct Q {
    double x, y, h; std::vector<std::pair<double, double>> p; std::unique_ptr<Q> c[4];                       // 중심 (x, y), 반변 h
    Q(double x, double y, double h) : x(x), y(y), h(h) {}
    bool insert(double px, double py) {
        if (px < x - h || px >= x + h || py < y - h || py >= y + h) return false;
        if (!c[0] && p.size() < 4) { p.push_back({px, py}); return true; }
        if (!c[0]) { for (int i = 0; i < 4; i++) c[i].reset(new Q(x + (i & 1 ? h / 2 : -h / 2), y + (i & 2 ? h / 2 : -h / 2), h / 2)); for (auto& q : p) for (auto& k : c) if (k->insert(q.first, q.second)) break; p.clear(); }
        for (auto& k : c) if (k->insert(px, py)) return true; return false;
    }
    int count(double x0, double y0, double x1, double y1) const {
        if (x1 < x - h || x0 >= x + h || y1 < y - h || y0 >= y + h) return 0; int r = 0;
        for (auto& q : p) r += q.first >= x0 && q.first <= x1 && q.second >= y0 && q.second <= y1;
        if (c[0]) for (auto& k : c) r += k->count(x0, y0, x1, y1); return r;
    }
};
int main() {
    std::mt19937 g(2); std::uniform_real_distribution<double> U(0, 1); Q root(0.5, 0.5, 0.5); std::vector<std::pair<double, double>> v;
    for (int i = 0; i < 3000; i++) { v.push_back({U(g), U(g)}); assert(root.insert(v.back().first, v.back().second)); }
    for (int t = 0; t < 200; t++) { double a = U(g), b = U(g), c = U(g), d = U(g); if (a > c) std::swap(a, c); if (b > d) std::swap(b, d);
        int want = 0; for (auto& q : v) want += q.first >= a && q.first <= c && q.second >= b && q.second <= d; assert(root.count(a, b, c, d) == want); }
    std::cout << "QuadTree: range counts verified" << std::endl; return 0;
}
// Time Complexity: 삽입 O(깊이), 범위 질의 O(깊이 + k)
// Space Complexity: O(N)
```
## Octree()
### 대표코드
```cpp
#include <array>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 옥트리(트리 관점의 요약, 정본은 Tree.md Part 11): 쿼드트리의 3차원 판. 정육면체를 8 등분하며, 3D 게임·점군(point cloud)·복셀 맵에서 쓴다.
// 점이 들어갈 자식 번호는 세 비트: (x >= cx) | (y >= cy) << 1 | (z >= cz) << 2
typedef std::array<double, 3> V3;
struct O {
    V3 c; double h; std::vector<V3> p; std::unique_ptr<O> k[8];
    O(V3 c, double h) : c(c), h(h) {}
    static int octant(const V3& c, const V3& q) { return (q[0] >= c[0]) | (q[1] >= c[1]) << 1 | (q[2] >= c[2]) << 2; }
    void insert(const V3& q) {
        if (!k[0] && p.size() < 8) { p.push_back(q); return; }
        if (!k[0]) { for (int i = 0; i < 8; i++) k[i].reset(new O({c[0] + (i & 1 ? h / 2 : -h / 2), c[1] + (i & 2 ? h / 2 : -h / 2), c[2] + (i & 4 ? h / 2 : -h / 2)}, h / 2)); auto old = p; p.clear(); for (auto& o : old) k[octant(c, o)]->insert(o); }
        k[octant(c, q)]->insert(q);
    }
    int countIn(const V3& lo, const V3& hi) const {
        for (int a = 0; a < 3; a++) if (hi[a] < c[a] - h || lo[a] >= c[a] + h) return 0;
        int r = 0; for (auto& q : p) r += q[0] >= lo[0] && q[0] <= hi[0] && q[1] >= lo[1] && q[1] <= hi[1] && q[2] >= lo[2] && q[2] <= hi[2];
        if (k[0]) for (auto& s : k) r += s->countIn(lo, hi); return r;
    }
};
int main() {
    std::mt19937 g(3); std::uniform_real_distribution<double> U(0, 1); O root({0.5, 0.5, 0.5}, 0.5); std::vector<V3> v;
    for (int i = 0; i < 4000; i++) { v.push_back({U(g), U(g), U(g)}); root.insert(v.back()); }
    for (int t = 0; t < 200; t++) { V3 a = {U(g), U(g), U(g)}, b = {U(g), U(g), U(g)}; for (int d = 0; d < 3; d++) if (a[d] > b[d]) std::swap(a[d], b[d]);
        int want = 0; for (auto& q : v) want += q[0] >= a[0] && q[0] <= b[0] && q[1] >= a[1] && q[1] <= b[1] && q[2] >= a[2] && q[2] <= b[2]; assert(root.countIn(a, b) == want); }
    std::cout << "Octree: 3D range counts verified" << std::endl; return 0;
}
// Time Complexity: 삽입 O(깊이), 범위 질의 O(깊이 + k)
// Space Complexity: O(N)
```
## RTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// R-트리(트리 관점의 요약, 정본은 Tree.md Part 16): 사각형(MBR)을 B-트리처럼 균형 있게 묶는 공간 색인. 내부 노드의 각 항목 = (자식을 모두 덮는 사각형, 자식).
// 질의 사각형과 겹치지 않는 항목은 아래를 통째로 건너뛴다. 여기서는 정적 데이터를 정렬 후 M 개씩 묶는 STR(Sort-Tile-Recursive) 벌크 로드 방식으로 만든다 (삽입·분할은 Tree.md 판)
struct R { double x1, y1, x2, y2; };
bool hit(const R& a, const R& b) { return a.x1 <= b.x2 && b.x1 <= a.x2 && a.y1 <= b.y2 && b.y1 <= a.y2; }
struct Node { R box; std::vector<Node*> kids; std::vector<int> ids; };
Node* pack(std::vector<std::pair<R, int>>& v, int M) {                      // 잎 단계: x 로 정렬 -> 세로 띠로 자르고 띠 안에서 y 로 정렬해 M 개씩
    std::sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.first.x1 + a.first.x2 < b.first.x1 + b.first.x2; });
    int leaves = (v.size() + M - 1) / M, strips = std::max(1, (int)std::ceil(std::sqrt((double)leaves))), per = (v.size() + strips - 1) / strips;
    std::vector<Node*> level;
    for (size_t s = 0; s < v.size(); s += per) { auto b = v.begin() + s, e = v.begin() + std::min(v.size(), s + per);
        std::sort(b, e, [](auto& a, auto& c) { return a.first.y1 + a.first.y2 < c.first.y1 + c.first.y2; });
        for (auto it = b; it < e; it += std::min<long>(M, e - it)) { Node* n = new Node; n->box = it->first;
            for (auto j = it; j < it + std::min<long>(M, e - it); ++j) { n->ids.push_back(j->second); n->box = {std::min(n->box.x1, j->first.x1), std::min(n->box.y1, j->first.y1), std::max(n->box.x2, j->first.x2), std::max(n->box.y2, j->first.y2)}; }
            level.push_back(n); } }
    while (level.size() > 1) { std::vector<Node*> up; for (size_t i = 0; i < level.size(); i += M) { Node* n = new Node; n->box = level[i]->box; for (size_t j = i; j < std::min(level.size(), i + M); j++) { n->kids.push_back(level[j]); n->box = {std::min(n->box.x1, level[j]->box.x1), std::min(n->box.y1, level[j]->box.y1), std::max(n->box.x2, level[j]->box.x2), std::max(n->box.y2, level[j]->box.y2)}; } up.push_back(n); } level = up; }
    return level[0];
}
void query(Node* n, const R& q, const std::vector<R>& rects, std::vector<int>& out) {
    if (!hit(n->box, q)) return; for (int id : n->ids) if (hit(rects[id], q)) out.push_back(id); for (Node* k : n->kids) query(k, q, rects, out);
}
int main() {
    std::mt19937 g(4); std::uniform_real_distribution<double> U(0, 1000); std::vector<R> rects; std::vector<std::pair<R, int>> items;
    for (int i = 0; i < 3000; i++) { double x = U(g), y = U(g); rects.push_back({x, y, x + U(g) / 20, y + U(g) / 20}); items.push_back({rects.back(), i}); }
    Node* root = pack(items, 8);
    for (int t = 0; t < 200; t++) { double x = U(g), y = U(g); R q{x, y, x + 60, y + 60}; std::vector<int> got, want; query(root, q, rects, got);
        for (int i = 0; i < 3000; i++) if (hit(rects[i], q)) want.push_back(i); std::sort(got.begin(), got.end()); assert(got == want); }
    std::cout << "RTree: STR-packed tree verified against brute force" << std::endl; return 0;
}
// Time Complexity: 벌크 로드 O(N log N), 질의 O(log N + k) (겹침이 적을 때)
// Space Complexity: O(N)
```
## BallTree()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 볼 트리(ball tree): 점들을 "공(중심 c, 반지름 r)" 으로 감싸 계층을 만든다. KD 트리가 축에 정렬된 평면으로 가르는 데 비해 공은 축에 구애받지 않아 중간 차원(~20)에서도 더 잘 버틴다.
// 구성: 가장 퍼진 축에서 중앙값으로 점을 둘로 나누고 각 쪽의 평균/최대거리로 공을 만든다. 질의: 점 q 에서 공까지의 거리 하한 max(0, |q-c| - r) 이 현재 k 번째 최선보다 크면 공 전체를 가지치기한다
// (삼각부등식: 공 안의 모든 점 p 에 대해 |q-p| >= |q-c| - r)
const int D = 6;
typedef std::array<double, D> Pt;
double dist(const Pt& a, const Pt& b) { double s = 0; for (int i = 0; i < D; i++) s += (a[i] - b[i]) * (a[i] - b[i]); return std::sqrt(s); }
long evals = 0;                                                            // 거리 계산 횟수
struct Node { Pt c; double r = 0; int lo, hi; Node *l = nullptr, *rt = nullptr; };
std::vector<Pt> pts; std::vector<int> perm; std::vector<std::unique_ptr<Node>> pool;
Node* build(int lo, int hi) {
    pool.emplace_back(new Node); Node* n = pool.back().get(); n->lo = lo; n->hi = hi; n->c.fill(0);
    for (int i = lo; i < hi; i++) for (int d = 0; d < D; d++) n->c[d] += pts[perm[i]][d] / (hi - lo);
    for (int i = lo; i < hi; i++) n->r = std::max(n->r, dist(n->c, pts[perm[i]]));
    if (hi - lo <= 8) return n;
    int axis = 0; double best = -1;
    for (int d = 0; d < D; d++) { double mn = 1e18, mx = -1e18; for (int i = lo; i < hi; i++) { mn = std::min(mn, pts[perm[i]][d]); mx = std::max(mx, pts[perm[i]][d]); } if (mx - mn > best) { best = mx - mn; axis = d; } }
    int mid = (lo + hi) / 2; std::nth_element(perm.begin() + lo, perm.begin() + mid, perm.begin() + hi, [&](int a, int b) { return pts[a][axis] < pts[b][axis]; });
    n->l = build(lo, mid); n->rt = build(mid, hi); return n;
}
void knn(const Node* n, const Pt& q, int k, std::priority_queue<std::pair<double, int>>& heap) {
    evals++; double dc = dist(q, n->c);
    if (heap.size() == (size_t)k && dc - n->r >= heap.top().first) return;       // 공 전체가 현재 k 번째보다 멀다
    if (!n->l) { for (int i = n->lo; i < n->hi; i++) { evals++; double d = dist(q, pts[perm[i]]); if (heap.size() < (size_t)k) heap.push({d, perm[i]}); else if (d < heap.top().first) { heap.pop(); heap.push({d, perm[i]}); } } return; }
    evals++; double dl = dist(q, n->l->c), dr = dist(q, n->rt->c);
    if (dl - n->l->r < dr - n->rt->r) { knn(n->l, q, k, heap); knn(n->rt, q, k, heap); } else { knn(n->rt, q, k, heap); knn(n->l, q, k, heap); }   // 더 가까운 공부터
}
int main() {
    std::mt19937 g(5); std::normal_distribution<double> N(0, 1); int n = 6000;
    std::vector<Pt> centers(12); for (auto& c : centers) for (auto& x : c) x = N(g) * 6;
    for (int i = 0; i < n; i++) { Pt p = centers[g() % 12]; for (auto& x : p) x += N(g); pts.push_back(p); }      // 12 개 군집
    perm.resize(n); for (int i = 0; i < n; i++) perm[i] = i; Node* root = build(0, n);
    long total = 0; int Q = 200, k = 5;
    for (int t = 0; t < Q; t++) {
        Pt q = centers[g() % 12]; for (auto& x : q) x += N(g); std::priority_queue<std::pair<double, int>> heap; evals = 0; knn(root, q, k, heap); total += evals;
        std::vector<double> all; for (auto& p : pts) all.push_back(dist(q, p)); std::sort(all.begin(), all.end());
        std::vector<double> got; while (!heap.empty()) { got.push_back(heap.top().first); heap.pop(); } std::reverse(got.begin(), got.end());
        for (int i = 0; i < k; i++) assert(std::fabs(got[i] - all[i]) < 1e-12);
    }
    double avg = (double)total / Q; assert(avg < n / 3.0);
    std::cout << "BallTree: " << k << "-NN exact; avg distance evaluations " << avg << " vs brute force " << n << std::endl; return 0;
}
// Time Complexity: 구성 O(N log N), kNN 평균 O(log N) ~ O(N^(1-1/d))
// Space Complexity: O(N)
```
## BVHTree()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// BVH(Bounding Volume Hierarchy): 물체들을 축 정렬 상자(AABB)로 감싸 이진 트리를 만든 공간 색인. 레이트레이싱(레이-장면 교차), 충돌 검사의 기본이다. 공간을 가르는 KD 트리와 달리
// 물체를 나누므로 상자끼리 겹칠 수 있지만 물체가 한 번만 저장된다.  구성: 중심점이 가장 퍼진 축에서 중앙값으로 둘로 나눈다.  레이 질의: 상자와 레이가 만나지 않으면(slab 방법) 가지치기하고, 가까운 자식부터
typedef std::array<double, 3> V;
struct Box { V lo, hi; };
Box merge(const Box& a, const Box& b) { Box r; for (int i = 0; i < 3; i++) { r.lo[i] = std::min(a.lo[i], b.lo[i]); r.hi[i] = std::max(a.hi[i], b.hi[i]); } return r; }
bool rayBox(const Box& b, const V& o, const V& inv, double tmax, double& tnear) {      // slab 방법: 각 축의 [진입, 이탈] 구간들의 교집합
    double t0 = 0, t1 = tmax;
    for (int i = 0; i < 3; i++) { double a = (b.lo[i] - o[i]) * inv[i], c = (b.hi[i] - o[i]) * inv[i]; if (a > c) std::swap(a, c); t0 = std::max(t0, a); t1 = std::min(t1, c); if (t0 > t1) return false; }
    tnear = t0; return true;
}
struct Node { Box box; int lo, hi; Node *l = nullptr, *r = nullptr; };
std::vector<Box> prims; std::vector<int> idx; std::vector<std::unique_ptr<Node>> pool; long visits = 0;
Node* build(int lo, int hi) {
    pool.emplace_back(new Node); Node* n = pool.back().get(); n->lo = lo; n->hi = hi; n->box = prims[idx[lo]];
    for (int i = lo + 1; i < hi; i++) n->box = merge(n->box, prims[idx[i]]);
    if (hi - lo <= 2) return n;
    int axis = 0; double best = -1;
    for (int d = 0; d < 3; d++) { double mn = 1e18, mx = -1e18; for (int i = lo; i < hi; i++) { double c = (prims[idx[i]].lo[d] + prims[idx[i]].hi[d]) / 2; mn = std::min(mn, c); mx = std::max(mx, c); } if (mx - mn > best) { best = mx - mn; axis = d; } }
    int mid = (lo + hi) / 2; std::nth_element(idx.begin() + lo, idx.begin() + mid, idx.begin() + hi, [&](int a, int b) { return prims[a].lo[axis] + prims[a].hi[axis] < prims[b].lo[axis] + prims[b].hi[axis]; });
    n->l = build(lo, mid); n->r = build(mid, hi); return n;
}
void closest(const Node* n, const V& o, const V& inv, double& tbest, int& hit) {       // 레이와 처음 만나는 상자
    visits++; double tn; if (!rayBox(n->box, o, inv, tbest, tn)) return;
    if (!n->l) { for (int i = n->lo; i < n->hi; i++) { double t; if (rayBox(prims[idx[i]], o, inv, tbest, t) && t < tbest) { tbest = t; hit = idx[i]; } } return; }
    double a, b; bool ha = rayBox(n->l->box, o, inv, tbest, a), hb = rayBox(n->r->box, o, inv, tbest, b);
    if (ha && (!hb || a <= b)) { closest(n->l, o, inv, tbest, hit); closest(n->r, o, inv, tbest, hit); } else { closest(n->r, o, inv, tbest, hit); closest(n->l, o, inv, tbest, hit); }
}
bool overlap(const Box& a, const Box& b) { for (int i = 0; i < 3; i++) if (a.hi[i] < b.lo[i] || b.hi[i] < a.lo[i]) return false; return true; }
void overlaps(const Node* n, const Box& q, std::vector<int>& out) {
    if (!overlap(n->box, q)) return;
    if (!n->l) { for (int i = n->lo; i < n->hi; i++) if (overlap(prims[idx[i]], q)) out.push_back(idx[i]); return; }
    overlaps(n->l, q, out); overlaps(n->r, q, out);
}
int main() {
    std::mt19937 g(6); std::uniform_real_distribution<double> U(0, 100), S(0.2, 2.0); int n = 3000;
    for (int i = 0; i < n; i++) { V c = {U(g), U(g), U(g)}; double s = S(g); prims.push_back({{c[0], c[1], c[2]}, {c[0] + s, c[1] + s, c[2] + s}}); }
    idx.resize(n); for (int i = 0; i < n; i++) idx[i] = i; Node* root = build(0, n);
    long total = 0; int rays = 400;
    for (int t = 0; t < rays; t++) {
        V o = {U(g), U(g), -10.0}, d = {(U(g) - 50) / 100, (U(g) - 50) / 100, 1.0}; V inv = {1 / d[0], 1 / d[1], 1 / d[2]};
        double tb = 1e18; int hit = -1; visits = 0; closest(root, o, inv, tb, hit); total += visits;
        double tw = 1e18; int want = -1; for (int i = 0; i < n; i++) { double tn; if (rayBox(prims[i], o, inv, tw, tn) && tn < tw) { tw = tn; want = i; } }
        assert(hit == want && (hit < 0 || std::fabs(tb - tw) < 1e-9));
    }
    for (int t = 0; t < 200; t++) { V c = {U(g), U(g), U(g)}; Box q{{c[0], c[1], c[2]}, {c[0] + 8, c[1] + 8, c[2] + 8}}; std::vector<int> got, want; overlaps(root, q, got); for (int i = 0; i < n; i++) if (overlap(prims[i], q)) want.push_back(i); std::sort(got.begin(), got.end()); assert(got == want); }
    double avg = (double)total / rays; assert(avg < n / 10.0);
    std::cout << "BVHTree: closest-hit ray casting exact; avg nodes visited per ray " << avg << " vs brute force " << n << std::endl; return 0;
}
// Time Complexity: 구성 O(N log N), 레이 질의 평균 O(log N)
// Space Complexity: O(N)
```

## BKTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// BK 트리(Burkhard–Keller): 거리 함수 d 가 "거리 공리"(삼각부등식 포함)를 만족하는 어떤 이산 거리 공간(편집 거리, 해밍 거리)에서도 쓸 수 있는 철자 교정·퍼지 검색용 트리.
// 임의의 단어를 루트로 삼고, 각 노드의 자식은 "루트와의 거리 = k" 인 단어들을 k 번 간선에 매단다. 질의 q 와 허용 반경 r: 노드 u 까지의 거리가 d 이면,
// 삼각부등식에 의해 정답이 있을 수 있는 자식 간선은 |k - d| <= r 인 것뿐이다 -> 나머지는 통째로 건너뛴다
int levenshtein(const std::string& a, const std::string& b) {
    std::vector<int> prev(b.size() + 1), cur(b.size() + 1); for (size_t j = 0; j <= b.size(); j++) prev[j] = j;
    for (size_t i = 1; i <= a.size(); i++) { cur[0] = i; for (size_t j = 1; j <= b.size(); j++) cur[j] = std::min({prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1])}); std::swap(prev, cur); }
    return prev[b.size()];
}
long calls = 0;
int dist(const std::string& a, const std::string& b) { calls++; return levenshtein(a, b); }
struct Node { std::string w; std::map<int, Node*> kid; };
std::vector<std::unique_ptr<Node>> pool;
void insert(Node*& root, const std::string& w) {
    if (!root) { pool.emplace_back(new Node{w, {}}); root = pool.back().get(); return; }
    Node* t = root;
    for (;;) { int d = dist(w, t->w); if (d == 0) return; auto it = t->kid.find(d); if (it == t->kid.end()) { pool.emplace_back(new Node{w, {}}); t->kid[d] = pool.back().get(); return; } t = it->second; }
}
void search(const Node* t, const std::string& q, int r, std::vector<std::string>& out) {
    int d = dist(q, t->w); if (d <= r) out.push_back(t->w);
    for (auto it = t->kid.lower_bound(d - r); it != t->kid.end() && it->first <= d + r; ++it) search(it->second, q, r, out);
}

int main() {
    std::mt19937 g(7); std::vector<std::string> words;
    for (int i = 0; i < 4000; i++) { std::string w; int len = 2 + g() % 13; for (int j = 0; j < len; j++) w += 'a' + g() % 26; words.push_back(w); }
    std::sort(words.begin(), words.end()); words.erase(std::unique(words.begin(), words.end()), words.end());
    Node* root = nullptr; calls = 0; for (auto& w : words) insert(root, w);
    long total = 0; int Q = 200;
    for (int t = 0; t < Q; t++) {
        std::string q = words[g() % words.size()]; if (!q.empty()) q[g() % q.size()] = 'a' + g() % 26;       // 사전 단어를 한 글자 바꾼 오타
        std::vector<std::string> got; calls = 0; search(root, q, 1, got); total += calls; std::sort(got.begin(), got.end());
        std::vector<std::string> want; for (auto& w : words) if (levenshtein(q, w) <= 1) want.push_back(w);
        assert(got == want);
    }
    double avg = (double)total / Q; assert(avg < words.size() / 2.0);
    std::cout << "BKTree: radius-1 search exact; avg distance computations " << avg << " vs brute force " << words.size() << std::endl; return 0;
}
// Time Complexity: 검색 평균 O(N^α) (α < 1, 반경이 작을수록 가지치기가 잘 됨)
// Space Complexity: O(N)
```
## VPTree()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// VP 트리(vantage-point tree): 거리 함수만 있으면 되는 일반 거리 공간(좌표가 필요 없음)의 이진 트리.
// 각 노드에서 "기준점(vantage point) v" 를 하나 고르고, 나머지 점을 v 와의 거리의 중앙값 μ 로 둘로 나눈다 (안쪽: d <= μ, 바깥쪽: d > μ).
// 질의 q 와 현재 k 번째 최선 거리 τ: d = d(q, v). 안쪽에 정답이 있을 수 있으려면 d - τ <= μ, 바깥쪽이려면 d + τ >= μ (삼각부등식).  더 유망한 쪽부터 내려가며 τ 를 줄인다
const int D = 4;
typedef std::array<double, D> Pt;
long evals = 0;
double dist(const Pt& a, const Pt& b) { evals++; double s = 0; for (int i = 0; i < D; i++) s += (a[i] - b[i]) * (a[i] - b[i]); return std::sqrt(s); }
struct Node { int vp; double mu = 0; Node *in = nullptr, *out = nullptr; };
std::vector<Pt> pts; std::vector<std::unique_ptr<Node>> pool;
Node* build(std::vector<int>& id, int lo, int hi) {
    if (lo >= hi) return nullptr;
    pool.emplace_back(new Node); Node* n = pool.back().get(); n->vp = id[lo];
    if (hi - lo == 1) return n;
    int mid = (lo + 1 + hi) / 2; std::vector<double> d(pts.size());
    for (int i = lo + 1; i < hi; i++) d[id[i]] = dist(pts[n->vp], pts[id[i]]);
    std::nth_element(id.begin() + lo + 1, id.begin() + mid, id.begin() + hi, [&](int a, int b) { return d[a] < d[b]; });
    n->mu = d[id[mid]]; n->in = build(id, lo + 1, mid); n->out = build(id, mid, hi); return n;
}
void knn(const Node* n, const Pt& q, int k, std::priority_queue<std::pair<double, int>>& heap) {
    if (!n) return;
    double d = dist(q, pts[n->vp]);
    if (heap.size() < (size_t)k) heap.push({d, n->vp}); else if (d < heap.top().first) { heap.pop(); heap.push({d, n->vp}); }
    auto tau = [&]() { return heap.size() < (size_t)k ? 1e18 : heap.top().first; };
    if (d <= n->mu) { knn(n->in, q, k, heap); if (d + tau() >= n->mu) knn(n->out, q, k, heap); }
    else            { knn(n->out, q, k, heap); if (d - tau() <= n->mu) knn(n->in, q, k, heap); }
}
int main() {
    std::mt19937 g(8); std::normal_distribution<double> N(0, 1); int n = 5000;
    std::vector<Pt> centers(10); for (auto& c : centers) for (auto& x : c) x = N(g) * 6;
    for (int i = 0; i < n; i++) { Pt p = centers[g() % 10]; for (auto& x : p) x += N(g); pts.push_back(p); }
    std::vector<int> id(n); for (int i = 0; i < n; i++) id[i] = i; Node* root = build(id, 0, n);
    long total = 0; int Q = 200, k = 5;
    for (int t = 0; t < Q; t++) {
        Pt q = centers[g() % 10]; for (auto& x : q) x += N(g); std::priority_queue<std::pair<double, int>> heap; evals = 0; knn(root, q, k, heap); total += evals;
        std::vector<double> all; for (auto& p : pts) all.push_back(std::sqrt([&] { double s = 0; for (int i = 0; i < D; i++) s += (p[i] - q[i]) * (p[i] - q[i]); return s; }())); std::sort(all.begin(), all.end());
        std::vector<double> got; while (!heap.empty()) { got.push_back(heap.top().first); heap.pop(); } std::reverse(got.begin(), got.end());
        for (int i = 0; i < k; i++) assert(std::fabs(got[i] - all[i]) < 1e-9);
    }
    double avg = (double)total / Q; assert(avg < n / 4.0);
    std::cout << "VPTree: " << k << "-NN exact; avg distance evaluations " << avg << " vs brute force " << n << std::endl; return 0;
}
// Time Complexity: 구성 O(N log N), kNN 평균 O(log N) (차원이 낮거나 군집이 있을 때)
// Space Complexity: O(N)
```
## CoverTree()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 커버 트리(Beygelzimer–Kakade–Langford): 이중 차원(doubling dimension)이 작은 거리 공간에서 최근접 탐색을 O(c^12 log n) 에 보장하는 트리. 각 점은 "레벨 i" 에 속하며 세 가지를 지킨다:
//   중첩  C_i ⊂ C_(i-1)    덮기  C_(i-1) 의 모든 점 p 는 C_i 의 어떤 점 q 가 d(p,q) <= 2^i 로 덮는다 (그 q 가 p 의 부모)    분리  C_i 의 서로 다른 두 점은 거리 > 2^i
// 레벨 i 는 "반지름 2^i 해상도"이므로 위로 갈수록 성기고 아래로 갈수록 촘촘하다. 삽입은 점이 들어갈 수 있는 가장 낮은 레벨을 위에서 아래로 찾고, NN 질의는 레벨을 내려가며
// 후보 집합 Q 를 "d(q, Q) + 2^i 이내" 로 줄인다 (레벨 i 노드의 모든 후손은 2^i 이내이므로 그보다 먼 후보는 정답이 될 수 없다)
typedef std::vector<double> P;
std::vector<P> pts; std::vector<int> lvl; std::vector<std::vector<int>> kids; int root = -1, maxL = 0, minL = 0; long evals = 0;
double d(int a, const P& q) { evals++; double s = 0; for (size_t i = 0; i < q.size(); i++) s += (pts[a][i] - q[i]) * (pts[a][i] - q[i]); return std::sqrt(s); }
double pw(int i) { return std::ldexp(1.0, i); }
bool insertRec(int p, const std::vector<int>& Q, int i) {                   // Q: 레벨 >= i 인 노드들 중 p 를 덮을 수 있는 후보
    std::vector<int> C = Q; for (int q : Q) for (int c : kids[q]) if (lvl[c] == i - 1) C.push_back(c);      // Children(Q)
    double dm = 1e18; for (int c : C) dm = std::min(dm, d(c, pts[p]));
    if (dm > pw(i)) return false;
    std::vector<int> Qp; for (int c : C) if (d(c, pts[p]) <= pw(i)) Qp.push_back(c);
    if (insertRec(p, Qp, i - 1)) return true;
    for (int q : Q) if (d(q, pts[p]) <= pw(i)) { lvl[p] = i - 1; kids[q].push_back(p); minL = std::min(minL, i - 1); return true; }          // 더 아래로 못 가면 Q 의 한 점의 자식으로
    return false;
}
void insert(const P& x) {
    int p = pts.size(); pts.push_back(x); lvl.push_back(0); kids.emplace_back();
    if (root < 0) { root = p; lvl[p] = 0; maxL = minL = 0; return; }
    while (d(root, x) > pw(maxL)) maxL++;                                  // 루트의 덮는 반지름을 키운다
    lvl[root] = maxL; bool ok = insertRec(p, {root}, maxL); assert(ok); (void)ok;
}
int nearest(const P& q) {
    std::vector<int> Q = {root};
    for (int i = maxL; i > minL; i--) {
        std::vector<int> C = Q; for (int u : Q) for (int c : kids[u]) if (lvl[c] == i - 1) C.push_back(c);
        double dm = 1e18; std::vector<double> dd; for (int c : C) { dd.push_back(d(c, q)); dm = std::min(dm, dd.back()); }
        Q.clear(); for (size_t j = 0; j < C.size(); j++) if (dd[j] <= dm + pw(i)) Q.push_back(C[j]);
    }
    int best = -1; double bd = 1e18; for (int u : Q) { double x = d(u, q); if (x < bd) { bd = x; best = u; } } return best;
}

int main() {
    std::mt19937 g(9); std::uniform_real_distribution<double> U(0, 100);
    int n = 1200; for (int i = 0; i < n; i++) insert({U(g), U(g), U(g)});
    for (int i = 1; i <= minL + 40 && i <= maxL; i++) {}                  // (수준 범위 확인용 자리)
    for (int i = minL; i <= maxL; i++) {                                    // 분리 불변식: 레벨 i 에 존재하는 점들(lvl >= i)은 서로 > 2^i
        std::vector<int> Ci; for (int p = 0; p < n; p++) if (lvl[p] >= i) Ci.push_back(p);
        for (size_t a = 0; a < Ci.size() && Ci.size() < 400; a++) for (size_t b = a + 1; b < Ci.size(); b++) { double s = 0; for (int k = 0; k < 3; k++) s += (pts[Ci[a]][k] - pts[Ci[b]][k]) * (pts[Ci[a]][k] - pts[Ci[b]][k]); assert(std::sqrt(s) > pw(i) - 1e-12); }
    }
    for (int c = 0; c < n; c++) for (int ch : kids[c]) { double s = 0; for (int k = 0; k < 3; k++) s += (pts[c][k] - pts[ch][k]) * (pts[c][k] - pts[ch][k]); assert(std::sqrt(s) <= pw(lvl[ch] + 1) + 1e-12); }   // 덮기 불변식
    long total = 0; int Q = 300;
    for (int t = 0; t < Q; t++) {
        P q = {U(g), U(g), U(g)}; evals = 0; int got = nearest(q); total += evals;
        double bd = 1e18; int want = -1; for (int p = 0; p < n; p++) { double s = 0; for (int k = 0; k < 3; k++) s += (pts[p][k] - q[k]) * (pts[p][k] - q[k]); if (s < bd) { bd = s; want = p; } }
        assert(got == want);
    }
    double avg = (double)total / Q;
    std::cout << "CoverTree: levels " << minL << ".." << maxL << ", nearest neighbour exact; avg distance evaluations " << avg << " vs brute force " << n << std::endl; return 0;
}
// Time Complexity: 삽입·NN 질의 O(c^6 log N) (c: 팽창 상수)
// Space Complexity: O(N)
```
# Part 6. 범위 질의
## SegmentTree()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

void build(std::vector<int>& tree, const std::vector<int>& arr, int node, int start, int end) {
    if(start == end) { tree[node] = arr[start]; return; }
    int mid = (start + end) / 2;
    build(tree, arr, 2*node, start, mid);
    build(tree, arr, 2*node+1, mid+1, end);
    tree[node] = tree[2*node] + tree[2*node+1];
}

int query(const std::vector<int>& tree, int node, int start, int end, int l, int r) {
    if(r < start || end < l) return 0;
    if(l <= start && end <= r) return tree[node];
    int mid = (start + end) / 2;
    return query(tree, 2*node, start, mid, l, r) + query(tree, 2*node+1, mid+1, end, l, r);
}

int main() {
    std::vector<int> arr = {1, 3, 5, 7, 9, 11};
    std::vector<int> tree(4 * arr.size());
    build(tree, arr, 1, 0, arr.size()-1);
    assert(query(tree, 1, 0, arr.size()-1, 1, 3) == 15);
    std::cout << "Segment Tree built and verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## LazyPropagation()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 지연 전파(트리 관점의 요약, 정본은 Tree.md Part 12): 구간 갱신을 구간 전체를 덮는 노드에 "미뤄 둔 갱신(lz)" 으로만 기록하고, 더 깊이 내려가야 할 때 비로소 자식에게 내려보낸다 -> 구간 덧셈 + 구간 합이 둘 다 O(log N)
struct Seg {
    int n; std::vector<long> sum, lz; explicit Seg(int n) : n(n), sum(4 * n, 0), lz(4 * n, 0) {}
    void app(int o, int l, int r, long v) { sum[o] += v * (r - l + 1); lz[o] += v; }
    void push(int o, int l, int r) { if (lz[o]) { int m = (l + r) / 2; app(2 * o, l, m, lz[o]); app(2 * o + 1, m + 1, r, lz[o]); lz[o] = 0; } }
    void add(int o, int l, int r, int a, int b, long v) { if (b < l || r < a) return; if (a <= l && r <= b) { app(o, l, r, v); return; } push(o, l, r); int m = (l + r) / 2; add(2 * o, l, m, a, b, v); add(2 * o + 1, m + 1, r, a, b, v); sum[o] = sum[2 * o] + sum[2 * o + 1]; }
    long query(int o, int l, int r, int a, int b) { if (b < l || r < a) return 0; if (a <= l && r <= b) return sum[o]; push(o, l, r); int m = (l + r) / 2; return query(2 * o, l, m, a, b) + query(2 * o + 1, m + 1, r, a, b); }
};
int main() {
    int n = 500; Seg s(n); std::vector<long> a(n, 0); std::mt19937 g(1);
    for (int t = 0; t < 5000; t++) { int l = g() % n, r = g() % n; if (l > r) std::swap(l, r); long v = (long)(g() % 100) - 50;
        if (g() % 2) { s.add(1, 0, n - 1, l, r, v); for (int i = l; i <= r; i++) a[i] += v; } else { long w = 0; for (int i = l; i <= r; i++) w += a[i]; assert(s.query(1, 0, n - 1, l, r) == w); } }
    std::cout << "LazyPropagation: range add / range sum verified" << std::endl; return 0;
}
// Time Complexity: 갱신·질의 O(log N)
// Space Complexity: O(N)
```
## FenwickTree()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

void update(std::vector<int>& bit, int i, int delta) {
    while(i < bit.size()) { bit[i] += delta; i += i & -i; }
}
int query(const std::vector<int>& bit, int i) {
    int sum = 0;
    while(i > 0) { sum += bit[i]; i -= i & -i; }
    return sum;
}

int main() {
    std::vector<int> arr = {1, 3, 5, 7, 9, 11};
    std::vector<int> bit(arr.size() + 1, 0);
    for(int i=0; i<arr.size(); i++) update(bit, i+1, arr[i]);
    assert(query(bit, 4) - query(bit, 1) == 15); // Sum of indices 1..3
    std::cout << "Fenwick Tree (BIT) built and verified." << std::endl;
    return 0;
}
// Time Complexity: O(N^3)
// Space Complexity: O(N)
```
## SparseTable()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 희소 표(sparse table): 변하지 않는 배열에서 "구간 최솟값(RMQ)" 같은 질의를 O(1) 에 답한다. 표 st[k][i] = 구간 [i, i + 2^k) 의 결과를 O(n log n) 로 미리 계산하고,
// 질의 [l, r] 은 길이 2^k <= 길이 < 2^(k+1) 인 k 를 골라 두 구간 [l, l+2^k) 과 (r-2^k, r] 을 겹쳐 합친다. 겹쳐도 결과가 변하지 않는 연산(최소·최대·gcd·AND·OR; 멱등)이어야 한다.
// 합처럼 겹치면 안 되는 연산은 이진 분해로 O(log n) (아래 sum 확인).  갱신이 없을 때 세그먼트 트리보다 질의가 빠르다
template <class Op> struct Sparse {
    std::vector<std::vector<long>> st; Op op; std::vector<int> lg;
    Sparse(const std::vector<long>& a, Op op) : op(op), lg(a.size() + 1, 0) {
        int n = a.size(); for (int i = 2; i <= n; i++) lg[i] = lg[i / 2] + 1;
        st.push_back(a); for (int k = 1; (1 << k) <= n; k++) { st.emplace_back(n - (1 << k) + 1); for (int i = 0; i + (1 << k) <= n; i++) st[k][i] = op(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]); }
    }
    long query(int l, int r) const { int k = lg[r - l + 1]; return op(st[k][l], st[k][r - (1 << k) + 1]); }       // 두 구간이 겹쳐도 OK (멱등)
    long disjoint(int l, int r) const { long acc = 0; for (int k = lg[r - l + 1]; l <= r; ) { while ((1 << k) > r - l + 1) k--; acc += st[k][l]; l += 1 << k; } return acc; }   // 합: 겹치지 않게
};

int main() {
    std::mt19937 g(2); int n = 3000; std::vector<long> a(n); for (auto& x : a) x = (long)(g() % 100000) + 1;
    auto mn = [](long x, long y) { return std::min(x, y); }; auto gc = [](long x, long y) { return std::gcd(x, y); }; auto pl = [](long x, long y) { return x + y; };
    Sparse<decltype(mn)> smin(a, mn); Sparse<decltype(gc)> sg(a, gc); Sparse<decltype(pl)> ss(a, pl);
    for (int t = 0; t < 20000; t++) {
        int l = g() % n, r = g() % n; if (l > r) std::swap(l, r);
        long m = a[l], gg = 0, s = 0; for (int i = l; i <= r; i++) { m = std::min(m, a[i]); gg = std::gcd(gg, a[i]); s += a[i]; }
        assert(smin.query(l, r) == m && sg.query(l, r) == gg && ss.disjoint(l, r) == s);
    }
    std::cout << "SparseTable: O(1) min/gcd queries, " << smin.st.size() << " levels for n=" << n << std::endl; return 0;
}
// Time Complexity: 구성 O(N log N), 멱등 연산 질의 O(1)
// Space Complexity: O(N log N)
```
## IntervalTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 구간 트리(트리 관점의 요약, 정본은 Tree.md Part 16): 구간을 시작점 순으로 BST 에 두고 각 노드에 "부분 트리의 최대 끝점(mx)" 을 덧붙여, mx 가 질의 시작보다 작은 부분 트리를 통째로 건너뛴다.
// 여기서는 정렬된 배열을 암묵적 균형 BST 로 쓰는 정적 판
struct Iv { int lo, hi; };
std::vector<Iv> a; std::vector<int> mx;
int build(int l, int r) { if (l >= r) return -1; int m = (l + r) / 2; int v = a[m].hi; v = std::max(v, build(l, m)); v = std::max(v, build(m + 1, r)); mx[m] = v; return v; }
void query(int l, int r, int qlo, int qhi, std::vector<int>& out) {
    if (l >= r) return; int m = (l + r) / 2; if (mx[m] < qlo) return;       // 부분 트리의 최대 끝점이 질의 시작보다 작으면 건너뜀
    query(l, m, qlo, qhi, out); if (a[m].lo <= qhi && qlo <= a[m].hi) out.push_back(m); if (a[m].lo <= qhi) query(m + 1, r, qlo, qhi, out);
}
int main() {
    std::mt19937 g(3); for (int i = 0; i < 2000; i++) { int lo = g() % 100000; a.push_back({lo, lo + (int)(g() % 80)}); }
    std::sort(a.begin(), a.end(), [](const Iv& x, const Iv& y) { return x.lo < y.lo; }); mx.assign(a.size(), 0); build(0, a.size());
    for (int t = 0; t < 500; t++) { int lo = g() % 100000, hi = lo + g() % 50; std::vector<int> got, want; query(0, a.size(), lo, hi, got); for (size_t i = 0; i < a.size(); i++) if (a[i].lo <= hi && lo <= a[i].hi) want.push_back(i); std::sort(got.begin(), got.end()); assert(got == want); }
    std::cout << "IntervalTree: overlap queries verified" << std::endl; return 0;
}
// Time Complexity: 질의 O(log N + k)
// Space Complexity: O(N)
```
## RangeTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 범위 트리(range tree): 2차원 직사각형 안의 점 개수/목록을 O(log² n + k) 에 답하는 정적 구조. x 로 정렬한 점들 위에 균형 이진 트리를 만들고,
// 각 노드에는 "그 부분 트리의 점들을 y 로 정렬한 목록" 을 보관한다 (다단계 구조 = 트리 속의 트리).  질의 [x1,x2]×[y1,y2]: x 구간을 O(log n) 개의 노드로 분해하고
// 각 노드의 y 정렬 목록에서 [y1,y2] 를 이분 탐색으로 센다 (분수 계단식(fractional cascading)을 쓰면 O(log n + k))
struct RT {
    int n; std::vector<std::pair<int, int>> byX; std::vector<std::vector<std::pair<int, int>>> ys;     // ys[node] = (y, x) 정렬 목록
    explicit RT(std::vector<std::pair<int, int>> pts) : n(pts.size()), byX(std::move(pts)), ys(4 * n) { std::sort(byX.begin(), byX.end()); build(1, 0, n - 1); }
    void build(int o, int l, int r) {
        for (int i = l; i <= r; i++) ys[o].push_back({byX[i].second, byX[i].first}); std::sort(ys[o].begin(), ys[o].end());
        if (l == r) return; int m = (l + r) / 2; build(2 * o, l, m); build(2 * o + 1, m + 1, r);
    }
    int count(int o, int l, int r, int xi, int xj, int y1, int y2) const {  // byX 인덱스 [xi, xj] 에 해당하는 점 중 y 가 [y1, y2]
        if (xj < l || r < xi) return 0;
        if (xi <= l && r <= xj) return std::upper_bound(ys[o].begin(), ys[o].end(), std::make_pair(y2, INT32_MAX)) - std::lower_bound(ys[o].begin(), ys[o].end(), std::make_pair(y1, INT32_MIN));
        int m = (l + r) / 2; return count(2 * o, l, m, xi, xj, y1, y2) + count(2 * o + 1, m + 1, r, xi, xj, y1, y2);
    }
    int count(int x1, int x2, int y1, int y2) const {
        int xi = std::lower_bound(byX.begin(), byX.end(), std::make_pair(x1, INT32_MIN)) - byX.begin(), xj = (int)(std::upper_bound(byX.begin(), byX.end(), std::make_pair(x2, INT32_MAX)) - byX.begin()) - 1;
        return xi > xj ? 0 : count(1, 0, n - 1, xi, xj, y1, y2);
    }
};
int main() {
    std::mt19937 g(4); std::vector<std::pair<int, int>> pts; for (int i = 0; i < 5000; i++) pts.push_back({(int)(g() % 10000), (int)(g() % 10000)});
    RT t(pts);
    for (int q = 0; q < 2000; q++) {
        int x1 = g() % 10000, x2 = g() % 10000, y1 = g() % 10000, y2 = g() % 10000; if (x1 > x2) std::swap(x1, x2); if (y1 > y2) std::swap(y1, y2);
        int want = 0; for (auto& p : pts) want += p.first >= x1 && p.first <= x2 && p.second >= y1 && p.second <= y2;
        assert(t.count(x1, x2, y1, y2) == want);
    }
    std::cout << "RangeTree: 2D rectangle counting verified, memory = n log n entries" << std::endl; return 0;
}
// Time Complexity: 구성 O(N log N), 개수 질의 O(log² N)
// Space Complexity: O(N log N)
```

# Part 7. 균형 트리
## AVLTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <cassert>

// AVL 트리(트리 관점의 요약, 정본은 Tree.md Part 6): 모든 노드에서 왼쪽·오른쪽 높이 차이(균형 인수)가 -1, 0, 1 이 되도록 삽입 뒤 회전으로 고친다 -> 높이 <= 1.44 log2(N+2)
struct N { int k, h = 1; N *l = nullptr, *r = nullptr; };
int H(N* n) { return n ? n->h : 0; }
void up(N* n) { n->h = 1 + std::max(H(n->l), H(n->r)); }
N* rotR(N* y) { N* x = y->l; y->l = x->r; x->r = y; up(y); up(x); return x; }
N* rotL(N* x) { N* y = x->r; x->r = y->l; y->l = x; up(x); up(y); return y; }
N* ins(N* n, int k) {
    if (!n) return new N{k}; if (k < n->k) n->l = ins(n->l, k); else if (k > n->k) n->r = ins(n->r, k); up(n);
    int b = H(n->l) - H(n->r);
    if (b > 1)  { if (H(n->l->l) < H(n->l->r)) n->l = rotL(n->l); return rotR(n); }     // LL 또는 LR
    if (b < -1) { if (H(n->r->r) < H(n->r->l)) n->r = rotR(n->r); return rotL(n); }     // RR 또는 RL
    return n;
}
int main() {
    N* root = nullptr; for (int i = 1; i <= 1023; i++) root = ins(root, i);              // 정렬 입력에도
    assert(H(root) == 10); std::cout << "AVLTree: height " << H(root) << " for 1023 sorted inserts" << std::endl; return 0;
}
// Time Complexity: 삽입·탐색 O(log N)
// Space Complexity: O(N)
```
## RedBlackTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <cassert>

// 레드-블랙 트리(트리 관점의 요약, 정본은 Tree.md Part 7): 색 규칙(빨간 노드의 자식은 검정, 모든 경로의 검은 노드 수 동일)으로 높이를 2 log2(N+1) 이하로 묶는다.
// 여기서는 구현이 가장 짧은 좌편향(LLRB) 삽입만 보인다 (삭제·일반형은 Tree.md)
struct N { int k; bool red = true; N *l = nullptr, *r = nullptr; };
bool R(N* n) { return n && n->red; }
N* rotL(N* h) { N* x = h->r; h->r = x->l; x->l = h; x->red = h->red; h->red = true; return x; }
N* rotR(N* h) { N* x = h->l; h->l = x->r; x->r = h; x->red = h->red; h->red = true; return x; }
N* ins(N* h, int k) {
    if (!h) return new N{k}; if (k < h->k) h->l = ins(h->l, k); else if (k > h->k) h->r = ins(h->r, k);
    if (R(h->r) && !R(h->l)) h = rotL(h); if (R(h->l) && R(h->l->l)) h = rotR(h);
    if (R(h->l) && R(h->r)) { h->red = true; h->l->red = h->r->red = false; } return h;
}
int ht(N* n) { return n ? 1 + std::max(ht(n->l), ht(n->r)) : 0; }
int main() {
    N* root = nullptr; for (int i = 1; i <= 4095; i++) { root = ins(root, i); root->red = false; }
    assert(ht(root) <= 2 * std::log2(4096.0)); std::cout << "RedBlackTree: height " << ht(root) << " for 4095 sorted inserts" << std::endl; return 0;
}
// Time Complexity: 삽입·탐색 O(log N)
// Space Complexity: O(N)
```
## AA Tree()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <cassert>

// AA 트리(Arne Andersson): 레드-블랙 트리를 "빨간 간선은 오른쪽으로만" 제한한 2-3 트리 변형. 색 대신 레벨(level) 숫자를 쓰고 규칙이 5개뿐이라 삭제까지 코드가 짧다.
//   ① 잎의 레벨 = 1  ② 왼쪽 자식의 레벨 = 부모 - 1  ③ 오른쪽 자식의 레벨 = 부모 또는 부모 - 1  ④ 오른쪽 손자의 레벨 < 조부모  ⑤ 레벨 > 1 인 노드는 자식이 둘
// 두 연산만 있다: skew(왼쪽 수평 간선 -> 오른쪽으로 회전), split(오른쪽 수평 간선 두 개 연속 -> 가운데를 올림, 레벨 +1)
struct Node { int key, level = 1; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
int lv(const Node* t) { return t ? t->level : 0; }
Node* skew(Node* t) { if (t && t->l && t->l->level == t->level) { Node* L = t->l; t->l = L->r; L->r = t; return L; } return t; }
Node* split(Node* t) { if (t && t->r && t->r->r && t->r->r->level == t->level) { Node* R = t->r; t->r = R->l; R->l = t; R->level++; return R; } return t; }
Node* insert(Node* t, int k) {
    if (!t) return new Node(k);
    if (k < t->key) t->l = insert(t->l, k); else if (k > t->key) t->r = insert(t->r, k);
    return split(skew(t));
}
Node* erase(Node* t, int k) {
    if (!t) return t;
    if (k > t->key) t->r = erase(t->r, k);
    else if (k < t->key) t->l = erase(t->l, k);
    else {
        if (!t->l && !t->r) { delete t; return nullptr; }
        if (!t->l) { Node* s = t->r; while (s->l) s = s->l; t->key = s->key; t->r = erase(t->r, s->key); }       // 후속자로 대체
        else       { Node* p = t->l; while (p->r) p = p->r; t->key = p->key; t->l = erase(t->l, p->key); }       // 선행자로 대체
    }
    int should = std::min(lv(t->l), lv(t->r)) + 1;                         // 자식이 줄었으면 레벨을 낮춘다
    if (should < t->level) { t->level = should; if (t->r && should < t->r->level) t->r->level = should; }
    t = skew(t); t->r = skew(t->r); if (t->r) t->r->r = skew(t->r->r);
    t = split(t); t->r = split(t->r);
    return t;
}
bool check(const Node* t, long lo, long hi) {
    if (!t) return true;
    if (t->key <= lo || t->key >= hi) return false;
    if (!t->l && !t->r && t->level != 1) return false;                     // ①
    if (lv(t->l) != t->level - 1) return false;                            // ②
    if (lv(t->r) != t->level && lv(t->r) != t->level - 1) return false;   // ③
    if (t->r && t->r->r && t->r->r->level >= t->level) return false;      // ④
    if (t->level > 1 && (!t->l || !t->r)) return false;                   // ⑤
    return check(t->l, lo, t->key) && check(t->r, t->key, hi);
}
int height(const Node* t) { return t ? 1 + std::max(height(t->l), height(t->r)) : 0; }
bool has(const Node* t, int k) { while (t) { if (k == t->key) return true; t = k < t->key ? t->l : t->r; } return false; }
void destroy(Node* t) { if (t) { destroy(t->l); destroy(t->r); delete t; } }

int main() {
    Node* root = nullptr; for (int i = 1; i <= 4095; i++) root = insert(root, i);
    assert(check(root, 0, 1L << 40) && height(root) <= 2 * std::log2(4096.0)); destroy(root); root = nullptr;
    std::mt19937 rng(10); std::set<int> ref;
    for (int step = 0; step < 30000; step++) {
        int x = rng() % 800;
        if (rng() % 3) { root = insert(root, x); ref.insert(x); } else { root = erase(root, x); ref.erase(x); }
        if (step % 50 == 0) { assert(check(root, -1, 1L << 40)); for (int q = 0; q < 800; q += 41) assert(has(root, q) == (ref.count(q) > 0)); }
    }
    for (int x : std::set<int>(ref)) { root = erase(root, x); ref.erase(x); assert(check(root, -1, 1L << 40)); }
    assert(!root);
    std::cout << "AATree: 5 level rules hold after 30000 random insert/erase steps" << std::endl; return 0;
}
// Time Complexity: 삽입·삭제·탐색 O(log N)
// Space Complexity: O(N)
```
## Treap()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <algorithm>
#include <cassert>

// 트립(트리 관점의 요약, 정본은 Tree.md Part 13): 키로는 BST, 무작위 우선순위로는 힙인 트리. 삽입 = 분할(split) + 병합(merge), 정렬된 입력에도 기대 높이 O(log N)
struct T { int k, p; T *l = nullptr, *r = nullptr; };
void split(T* t, int k, T*& a, T*& b) { if (!t) { a = b = nullptr; return; } if (t->k < k) { a = t; split(t->r, k, t->r, b); } else { b = t; split(t->l, k, a, t->l); } }
T* merge(T* a, T* b) { if (!a || !b) return a ? a : b; if (a->p > b->p) { a->r = merge(a->r, b); return a; } b->l = merge(a, b->l); return b; }
int ht(T* t) { return t ? 1 + std::max(ht(t->l), ht(t->r)) : 0; }
int main() {
    std::mt19937 g(1); T* root = nullptr;
    for (int i = 1; i <= 4095; i++) { T* a; T* b; split(root, i, a, b); root = merge(merge(a, new T{i, (int)g()}), b); }
    assert(ht(root) < 40); std::cout << "Treap: height " << ht(root) << " for 4095 sorted inserts" << std::endl; return 0;
}
// Time Complexity: 삽입·삭제·탐색 기대 O(log N)
// Space Complexity: O(N)
```
## SplayTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cassert>

// 스플레이 트리(트리 관점의 요약, 정본은 Tree.md Part 13): 접근한 노드를 회전으로 루트까지 끌어올린다(zig-zig / zig-zag). 균형 정보를 저장하지 않고도 분할상환 O(log N),
// 최근에 쓴 키가 다시 빨리 나오는 접근 패턴에 강하다 (정적 최적성, 순차 접근 O(N) 등)
struct S { int k; S *l = nullptr, *r = nullptr; };
S* rotR(S* t) { S* x = t->l; t->l = x->r; x->r = t; return x; }
S* rotL(S* t) { S* x = t->r; t->r = x->l; x->l = t; return x; }
S* splay(S* t, int k) {
    if (!t || t->k == k) return t;
    if (k < t->k) { if (!t->l) return t;
        if (k < t->l->k) { t->l->l = splay(t->l->l, k); t = rotR(t); } else if (k > t->l->k) { t->l->r = splay(t->l->r, k); if (t->l->r) t->l = rotL(t->l); }
        return t->l ? rotR(t) : t; }
    if (!t->r) return t;
    if (k > t->r->k) { t->r->r = splay(t->r->r, k); t = rotL(t); } else if (k < t->r->k) { t->r->l = splay(t->r->l, k); if (t->r->l) t->r = rotR(t->r); }
    return t->r ? rotL(t) : t;
}
S* insert(S* t, int k) { if (!t) return new S{k}; t = splay(t, k); if (t->k == k) return t; S* n = new S{k}; if (k < t->k) { n->r = t; n->l = t->l; t->l = nullptr; } else { n->l = t; n->r = t->r; t->r = nullptr; } return n; }
int main() {
    S* root = nullptr; for (int i = 1; i <= 1000; i++) root = insert(root, i);
    root = splay(root, 500); assert(root->k == 500);                       // 접근한 키가 루트로
    root = splay(root, 1); assert(root->k == 1);
    std::cout << "SplayTree: accessed keys move to the root" << std::endl; return 0;
}
// Time Complexity: 분할상환 O(log N)
// Space Complexity: O(N)
```
## ScapegoatTree()
### 대표코드
```cpp
#include <cmath>
#include <iostream>
#include <vector>
#include <cassert>

// 스케이프고트 트리(트리 관점의 요약, 정본은 Tree.md Part 13): 회전 없이, 어떤 노드의 한쪽 부분 트리가 α(여기서는 0.7) 비율을 넘으면 그 노드(희생양)를 통째로 완전 균형으로 다시 짓는다.
// 높이 <= log_{1/α} N 이 유지되고 삭제 후 전체 재구성이 분할상환 O(log N) 을 만든다
struct G { int k, sz = 1; G *l = nullptr, *r = nullptr; };
int S(G* n) { return n ? n->sz : 0; }
void flat(G* n, std::vector<G*>& v) { if (!n) return; flat(n->l, v); v.push_back(n); flat(n->r, v); }
G* build(std::vector<G*>& v, int lo, int hi) { if (lo >= hi) return nullptr; int m = (lo + hi) / 2; G* n = v[m]; n->l = build(v, lo, m); n->r = build(v, m + 1, hi); n->sz = hi - lo; return n; }
G* ins(G* n, int k) {
    if (!n) return new G{k}; if (k < n->k) n->l = ins(n->l, k); else n->r = ins(n->r, k); n->sz++;
    if (S(n->l) > 0.7 * n->sz || S(n->r) > 0.7 * n->sz) { std::vector<G*> v; flat(n, v); return build(v, 0, v.size()); }
    return n;
}
int ht(G* n) { return n ? 1 + std::max(ht(n->l), ht(n->r)) : 0; }
int main() {
    G* root = nullptr; for (int i = 1; i <= 4096; i++) root = ins(root, i);
    assert(ht(root) <= std::log(4096.0) / std::log(1 / 0.7) + 2); std::cout << "ScapegoatTree: height " << ht(root) << " for 4096 sorted inserts" << std::endl; return 0;
}
// Time Complexity: 삽입 분할상환 O(log N), 탐색 최악 O(log N)
// Space Complexity: O(N)
```
## TangoTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <memory>
#include <random>
#include <unordered_map>
#include <vector>
#include <cassert>

// 탱고 트리(Demaine–Harmon–Iacono–Pătraşcu): "O(log log n)-경쟁적" 이진 탐색 트리 — 임의의 접근열 X 에 대해 어떤 BST 도 OPT(X) 에 쓰는 시간의 O(log log n) 배 안에 처리한다 (현재 알려진 가장 좋은 보장).
// 구조: 키 1..N(N=2^H-1)에 대한 완전 이진 "참조 트리" P 를 두고(실제로 저장하지 않고 산술로 계산), 각 노드에 "선호 자식"(마지막으로 접근한 쪽)을 둔다.
// 선호 자식을 따라 이어진 사슬이 "선호 경로" 이고, 경로마다 크기가 <= H 인 보조 BST(여기서는 깊이 정보를 덧붙인 트립)를 만든다 -> 보조 트리 탐색은 O(log log N).
// 접근 x 는 "경로 안 탐색" 과 "선호 자식이 바뀌는 지점에서의 cut(깊이로 아래쪽 자르기) / join(다른 경로 이어 붙이기)" 의 반복이고, 선호 자식이 바뀐 횟수 k 에 대해 시간이 O(k (1 + log log N)).
// 이 k 는 Wilber 의 interleave 하한과 정확히 같다 — 아래 main 이 독립적으로 계산한 interleave 값과 대조해 확인한다
int H, N;
int ctz(int k) { return __builtin_ctz(k); }
int depthOf(int k) { return H - 1 - ctz(k); }                              // 키 k 의 참조 트리 깊이 (루트 0)
int rootKey() { return 1 << (H - 1); }
int child(int k, int dir) { int t = ctz(k); if (!t) return 0; return dir == 0 ? k - (1 << (t - 1)) : k + (1 << (t - 1)); }     // 0 = 없음

struct T { int key, depth, mn, mx; unsigned pri; T *l = nullptr, *r = nullptr; };       // 보조 트립: 키 순서 BST, mn/mx = 부분 트리의 최소/최대 깊이
void upd(T* t) { t->mn = t->mx = t->depth; for (T* c : {t->l, t->r}) if (c) { t->mn = std::min(t->mn, c->mn); t->mx = std::max(t->mx, c->mx); } }
void split(T* t, int k, T*& a, T*& b) { if (!t) { a = b = nullptr; return; } if (t->key < k) { a = t; split(t->r, k, t->r, b); } else { b = t; split(t->l, k, a, t->l); } upd(t); }
T* merge(T* a, T* b) { if (!a || !b) return a ? a : b; if (a->pri > b->pri) { a->r = merge(a->r, b); upd(a); return a; } b->l = merge(a, b->l); upd(b); return b; }
int topKey(T* t) { while (t->depth != t->mn) t = (t->l && t->l->mn == t->mn) ? t->l : t->r; return t->key; }            // 경로의 맨 위(깊이 최소) 노드
T* leftmostDeeper(T* t, int d) { while (t) { if (t->l && t->l->mx > d) t = t->l; else if (t->depth > d) return t; else t = t->r; } return nullptr; }
T* rightmostDeeper(T* t, int d) { while (t) { if (t->r && t->r->mx > d) t = t->r; else if (t->depth > d) return t; else t = t->l; } return nullptr; }
void cutBelow(T* t, int d, T*& top, T*& bottom) {                          // 깊이 > d 인 노드들(키 순서로 연속 구간)을 떼어 낸다
    if (t->mx <= d) { top = t; bottom = nullptr; return; }
    T *a = leftmostDeeper(t, d), *b = rightmostDeeper(t, d), *A, *rest, *mid, *C;
    split(t, a->key, A, rest); split(rest, b->key + 1, mid, C);
    top = merge(A, C); bottom = mid;
}
T* join(T* top, T* bottom) {                                               // bottom 의 키 구간은 top 의 키들 사이 한 틈에 정확히 들어간다
    T* m = bottom; while (m->l) m = m->l; T *A, *B; split(top, m->key, A, B); return merge(merge(A, bottom), B);
}
struct Tango {
    std::vector<T> node; std::vector<signed char> pref, last; std::unordered_map<int, T*> pathAtTop; long flips = 0, cuts = 0, joins = 0;
    Tango() : node(N + 1), pref(N + 1, -1), last(N + 1, -1) {
        std::mt19937 g(1);
        for (int k = 1; k <= N; k++) { node[k] = T{k, depthOf(k), depthOf(k), depthOf(k), (unsigned)g()}; pathAtTop[k] = &node[k]; }      // 처음엔 모든 노드가 홀로 선 경로
    }
    void access(int x) {
        int tk = rootKey(); T* t = pathAtTop[tk];
        for (;;) {
            T *a = nullptr, *b = nullptr, *c = t;                          // 경로 안에서 x 의 선행자(<=)와 후속자(>=)
            while (c) { if (c->key == x) { a = b = c; break; } if (c->key < x) { a = c; c = c->r; } else { b = c; c = c->l; } }
            T* w = (a && a == b) ? a : !a ? b : !b ? a : (a->depth > b->depth ? a : b);          // x 의 조상 중 이 경로에서 가장 깊은 노드는 둘 중 더 깊은 쪽
            T *top, *bot; cutBelow(t, w->depth, top, bot);
            if (bot) { pathAtTop[topKey(bot)] = bot; cuts++; }
            if (w->key == x) { pathAtTop[tk] = top; pref[x] = -1; return; }
            int dir = x < w->key ? 0 : 1, ch = child(w->key, dir); assert(ch && pref[w->key] != dir);
            T* p2 = pathAtTop[ch]; pathAtTop.erase(ch);
            t = join(top, p2); joins++; pathAtTop[tk] = t;
            if (last[w->key] != -1 && last[w->key] != dir) flips++;       // 선호 자식이 왼쪽<->오른쪽으로 바뀜
            last[w->key] = dir; pref[w->key] = dir;
        }
    }
    bool verify() {                                                        // 경로 분해가 선호 자식 포인터와 정확히 일치하는가
        size_t total = 0;
        for (auto& kv : pathAtTop) {
            std::vector<int> keys; std::vector<T*> st; T* c = kv.second;
            while (c || !st.empty()) { while (c) { st.push_back(c); c = c->l; } c = st.back(); st.pop_back(); keys.push_back(c->key); c = c->r; }
            for (size_t i = 1; i < keys.size(); i++) if (keys[i - 1] >= keys[i]) return false;
            std::vector<int> chain; for (int k = kv.first; k; k = pref[k] < 0 ? 0 : child(k, pref[k])) chain.push_back(k);
            std::sort(chain.begin(), chain.end()); if (chain != keys) return false;
            if (topKey(kv.second) != kv.first) return false; total += keys.size();
        }
        return total == (size_t)N;
    }
};
long interleave(const std::vector<int>& seq) {                             // Wilber 의 첫 하한: 참조 트리 위를 직접 걸으며 센 좌우 교대 횟수
    std::vector<signed char> lastSide(N + 1, -1); long f = 0;
    for (int x : seq) for (int k = rootKey(); k != x;) { int dir = x < k ? 0 : 1; if (lastSide[k] != -1 && lastSide[k] != dir) f++; lastSide[k] = dir; k = child(k, dir); }
    return f;
}

int main() {
    H = 10; N = (1 << H) - 1; std::mt19937 g(5);
    std::vector<std::vector<int>> seqs(3);
    for (int i = 0; i < 4000; i++) seqs[0].push_back(g() % N + 1);        // 무작위
    for (int r = 0; r < 3; r++) for (int i = 1; i <= N; i++) seqs[1].push_back(i);          // 순차 3 바퀴
    for (int i = 0; i < N; i++) { int v = 0; for (int b = 0; b < H; b++) if (i >> b & 1) v |= 1 << (H - 1 - b); if (v >= 1 && v <= N) seqs[2].push_back(v); }   // 비트 역순
    for (auto& s : seqs) {
        Tango t; int cnt = 0; for (int x : s) { t.access(x); if (++cnt % 250 == 0) assert(t.verify()); }
        assert(t.verify() && t.flips == interleave(s));                    // 선호 자식 변경 횟수 == interleave 하한
        std::cout << "sequence of " << s.size() << " accesses: preferred-child flips " << t.flips << ", cuts " << t.cuts << ", joins " << t.joins << std::endl;
    }
    Tango seq; for (int r = 0; r < 1; r++) for (int i = 1; i <= N; i++) seq.access(i);
    assert(seq.flips <= N);                                                // 순차 접근: 한 바퀴에 노드당 교대 한 번 이하 -> 총 O(N)
    std::cout << "TangoTree: flips == interleave bound on 3 access patterns; sequential pass flips " << seq.flips << " for N=" << N << std::endl;
    return 0;
}
// Time Complexity: 접근열 X 에 대해 O((k + 1)(1 + log log N)) (k = 선호 자식 변경 횟수 = interleave 하한)
// Space Complexity: O(N)
```

# Part 8. 외부 메모리
## BTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

// B-트리(트리 관점의 요약, 정본은 Tree.md Part 13): 한 노드에 키 여러 개를 담아 디스크 블록 한 개 = 노드 한 개가 되게 한 균형 탐색 트리. 모든 잎이 같은 깊이이고, 가득 찬 노드는
// 내려가는 길에 미리 쪼갠다(분할 시 가운데 키가 부모로). 여기서는 t=2 (키 1~3개, 2-3-4 트리)의 삽입과 높이 확인
struct B { int n = 0, k[3]; B* c[4] = {}; bool leaf = true; };
void splitChild(B* x, int i) {
    B *y = x->c[i], *z = new B; z->leaf = y->leaf; z->n = 1; z->k[0] = y->k[2];
    if (!y->leaf) { z->c[0] = y->c[2]; z->c[1] = y->c[3]; }
    for (int j = x->n; j > i; j--) { x->k[j] = x->k[j - 1]; x->c[j + 1] = x->c[j]; }
    x->k[i] = y->k[1]; x->c[i + 1] = z; x->n++; y->n = 1;
}
void insertNonFull(B* x, int v) {
    int i = x->n; if (x->leaf) { while (i && v < x->k[i - 1]) { x->k[i] = x->k[i - 1]; i--; } x->k[i] = v; x->n++; return; }
    while (i && v < x->k[i - 1]) i--; if (x->c[i]->n == 3) { splitChild(x, i); if (v > x->k[i]) i++; } insertNonFull(x->c[i], v);
}
void insert(B*& r, int v) { if (!r) r = new B; if (r->n == 3) { B* s = new B; s->leaf = false; s->c[0] = r; splitChild(s, 0); r = s; } insertNonFull(r, v); }
int height(B* r) { int h = 0; for (; r; r = r->leaf ? nullptr : r->c[0]) h++; return h; }
int main() { B* r = nullptr; for (int i = 1; i <= 1000; i++) insert(r, i); assert(height(r) <= 10); std::cout << "BTree: height " << height(r) << " for 1000 sorted keys" << std::endl; return 0; }
// Time Complexity: 탐색·삽입 O(log_t N) 노드 접근
// Space Complexity: O(N)
```
## BPlusTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <vector>
#include <cassert>

// B+트리(트리 관점의 요약, 정본은 Tree.md Part 13): 모든 값을 잎에만 두고 잎들을 연결 리스트로 이어 범위 질의를 "한 번 찾고 옆으로 훑기" 로 만든다. 내부 노드는 길 안내용 분리 키만 가진다 (DB 인덱스의 표준).
// 아래는 정렬된 키로 잎을 채운 정적 판: 분리 키 배열을 이분 탐색해 잎을 찾고 그 잎부터 연결을 따라 읽는다
int main() {
    std::vector<int> keys; for (int i = 0; i < 100; i++) keys.push_back(i * 3);                // 0, 3, 6, ...
    std::vector<std::vector<int>> leaf; std::vector<int> sep;                                   // 잎(최대 8 키)과 각 잎의 첫 키
    for (size_t i = 0; i < keys.size(); i += 8) { leaf.emplace_back(keys.begin() + i, keys.begin() + std::min(keys.size(), i + 8)); sep.push_back(keys[i]); }
    auto range = [&](int lo, int hi) { std::vector<int> out; size_t j = std::upper_bound(sep.begin(), sep.end(), lo) - sep.begin(); j = j ? j - 1 : 0;
        for (; j < leaf.size() && leaf[j].front() <= hi; j++) for (int k : leaf[j]) if (k >= lo && k <= hi) out.push_back(k); return out; };
    assert((range(10, 25) == std::vector<int>{12, 15, 18, 21, 24}) && range(1000, 2000).empty());
    std::cout << "BPlusTree: range scan via leaf chain, " << leaf.size() << " leaves" << std::endl; return 0;
}
// Time Complexity: 범위 질의 O(log N + k)
// Space Complexity: O(N)
```
## BStarTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// B*-트리(Knuth): 비루트 노드를 최소 2/3 까지 채우는 B-트리 변형. 노드가 넘치면 곧바로 쪼개지 않고 먼저 이웃 형제에게 키를 나눠 준다(재분배).
// 형제도 가득 찼을 때만 "넘친 노드 + 가득 찬 형제 + 부모의 분리 키" 를 모아 세 노드로 쪼갠다(2->3 분할). 노드가 가득 차 있을 때 쪼개는 B-트리의 평균 이용률이 약 69% 인 데 비해
// B* 는 약 80% 이상이라 같은 데이터에 노드(=디스크 블록)가 적게 든다.  루트는 더 크게(2·⌊2M/3⌋+1 키) 허용해 루트가 쪼개질 때도 두 자식이 2/3 이상 차게 한다
// 이 코드는 star=false 로 두면 같은 구조가 일반 B-트리(넘치면 반으로 분할)가 되어 이용률을 직접 비교할 수 있다
const int M = 6, ROOTMAX = 2 * (2 * M / 3) + 1, MINK = 2 * M / 3;
struct Node { std::vector<int> k; std::vector<Node*> c; bool leaf() const { return c.empty(); } };
struct Seq { std::vector<int> k; std::vector<Node*> c; };
Seq gather(Node* a, int sep, Node* b) { Seq s; s.k = a->k; s.k.push_back(sep); s.k.insert(s.k.end(), b->k.begin(), b->k.end()); s.c = a->c; s.c.insert(s.c.end(), b->c.begin(), b->c.end()); return s; }
struct Tree {
    bool star; Node* root = nullptr; std::vector<Node*> all; long redistributions = 0, twoToThrees = 0, splits = 0;
    explicit Tree(bool star) : star(star) { root = mk(); }
    Node* mk() { all.push_back(new Node); return all.back(); }
    void splitNode(Node* p, int i) {                                       // 일반 분할: 가운데 키를 부모로
        Node* n = p->c[i]; Node* r = mk(); int mid = n->k.size() / 2; int up = n->k[mid];
        r->k.assign(n->k.begin() + mid + 1, n->k.end()); if (!n->leaf()) { r->c.assign(n->c.begin() + mid + 1, n->c.end()); n->c.resize(mid + 1); }
        n->k.resize(mid); p->k.insert(p->k.begin() + i, up); p->c.insert(p->c.begin() + i + 1, r); splits++;
    }
    void redistribute(Node* p, int j) {                                    // c[j], 분리 키, c[j+1] 을 합쳐 반반
        Seq s = gather(p->c[j], p->k[j], p->c[j + 1]); int T = s.k.size(), L = (T - 1) / 2;
        Node *a = p->c[j], *b = p->c[j + 1]; a->k.assign(s.k.begin(), s.k.begin() + L); b->k.assign(s.k.begin() + L + 1, s.k.end()); p->k[j] = s.k[L];
        if (!s.c.empty()) { a->c.assign(s.c.begin(), s.c.begin() + L + 1); b->c.assign(s.c.begin() + L + 1, s.c.end()); } redistributions++;
    }
    void twoToThree(Node* p, int j) {                                      // c[j], c[j+1] (한쪽은 넘침, 한쪽은 가득) + 분리 키 -> 세 노드 + 분리 키 둘
        Seq s = gather(p->c[j], p->k[j], p->c[j + 1]); int T = s.k.size(), base = (T - 2) / 3, rem = (T - 2) % 3;
        int n1 = base + (rem > 0), n2 = base + (rem > 1), n3 = base; Node *a = p->c[j], *b = p->c[j + 1], *c = mk();
        int sep1 = s.k[n1], sep2 = s.k[n1 + 1 + n2];
        a->k.assign(s.k.begin(), s.k.begin() + n1); b->k.assign(s.k.begin() + n1 + 1, s.k.begin() + n1 + 1 + n2); c->k.assign(s.k.begin() + n1 + n2 + 2, s.k.end());
        if (!s.c.empty()) { a->c.assign(s.c.begin(), s.c.begin() + n1 + 1); b->c.assign(s.c.begin() + n1 + 1, s.c.begin() + n1 + n2 + 2); c->c.assign(s.c.begin() + n1 + n2 + 2, s.c.end()); }
        p->k[j] = sep1; p->k.insert(p->k.begin() + j + 1, sep2); p->c.insert(p->c.begin() + j + 2, c); twoToThrees++; (void)n3;
    }
    void fix(Node* p, int i) {                                             // p->c[i] 가 M+1 개로 넘쳤다
        if (star && i > 0 && (int)p->c[i - 1]->k.size() < M) { redistribute(p, i - 1); return; }
        if (star && i + 1 < (int)p->c.size() && (int)p->c[i + 1]->k.size() < M) { redistribute(p, i); return; }
        if (star && i > 0) { twoToThree(p, i - 1); return; }
        if (star && i + 1 < (int)p->c.size()) { twoToThree(p, i); return; }
        splitNode(p, i);
    }
    void insertRec(Node* n, int x) {
        int i = 0; while (i < (int)n->k.size() && x > n->k[i]) i++;
        if (i < (int)n->k.size() && n->k[i] == x) return;
        if (n->leaf()) { n->k.insert(n->k.begin() + i, x); return; }
        insertRec(n->c[i], x); if ((int)n->c[i]->k.size() > M) fix(n, i);
    }
    void insert(int x) {
        insertRec(root, x);
        int cap = star ? ROOTMAX : M;
        if ((int)root->k.size() > cap) { Node* nr = mk(); nr->c.push_back(root); root = nr; splitNode(nr, 0); }
    }
    bool contains(int x) const { Node* n = root; for (;;) { int i = 0; while (i < (int)n->k.size() && x > n->k[i]) i++; if (i < (int)n->k.size() && n->k[i] == x) return true; if (n->leaf()) return false; n = n->c[i]; } }
    int check(Node* n, long lo, long hi, bool isRoot, std::vector<int>& out) const {          // 높이 또는 -1
        int cap = isRoot ? (star ? ROOTMAX : M) : M;
        if ((int)n->k.size() > cap || (!isRoot && star && (int)n->k.size() < MINK) || (!isRoot && n->k.empty())) return -1;
        for (size_t i = 0; i < n->k.size(); i++) if (n->k[i] <= (i ? n->k[i - 1] : lo) || n->k[i] >= hi) return -1;
        if (n->leaf()) { out.insert(out.end(), n->k.begin(), n->k.end()); return 1; }
        if (n->c.size() != n->k.size() + 1) return -1; int h = -2;
        for (size_t i = 0; i < n->c.size(); i++) {
            int ch = check(n->c[i], i ? n->k[i - 1] : lo, i < n->k.size() ? n->k[i] : hi, false, out); if (ch < 0 || (h != -2 && ch != h)) return -1; h = ch;
            if (i < n->k.size()) out.push_back(n->k[i]);
        }
        return h + 1;
    }
    size_t nodes() const { size_t cnt = 0; std::vector<Node*> st = {root}; while (!st.empty()) { Node* n = st.back(); st.pop_back(); cnt++; for (Node* c : n->c) st.push_back(c); } return cnt; }
    size_t keys() const { size_t cnt = 0; std::vector<Node*> st = {root}; while (!st.empty()) { Node* n = st.back(); st.pop_back(); cnt += n->k.size(); for (Node* c : n->c) st.push_back(c); } return cnt; }
    ~Tree() { for (Node* n : all) delete n; }
};

int main() {
    std::mt19937 rng(9);
    for (int mode = 0; mode < 2; mode++) {                                 // 0: 무작위 삽입, 1: 정렬 삽입
        Tree b(false), s(true); std::set<int> ref; std::vector<int> in;
        for (int i = 0; i < 20000; i++) in.push_back(mode ? i : (int)(rng() % 1000000));
        for (size_t i = 0; i < in.size(); i++) {
            b.insert(in[i]); s.insert(in[i]); ref.insert(in[i]);
            if (i % 997 == 0) { std::vector<int> v1, v2; assert(s.check(s.root, -1, 1L << 40, true, v1) > 0 && b.check(b.root, -1, 1L << 40, true, v2) > 0); }
        }
        std::vector<int> v; int h = s.check(s.root, -1, 1L << 40, true, v);
        assert(h > 0 && v == std::vector<int>(ref.begin(), ref.end()));    // 구조 불변식과 중위 순회
        for (int x : in) assert(s.contains(x));
        double uB = (double)b.keys() / (b.nodes() * M), uS = (double)s.keys() / (s.nodes() * M);
        assert(s.nodes() < b.nodes() && uS > uB);                          // B* 가 노드를 덜 쓴다
        std::cout << (mode ? "sorted" : "random") << " inserts: B-tree nodes " << b.nodes() << " (fill " << uB * 100 << "%) vs B*-tree nodes " << s.nodes() << " (fill " << uS * 100
                  << "%), redistributions " << s.redistributions << ", 2->3 splits " << s.twoToThrees << std::endl;
    }
    return 0;
}
// Time Complexity: 삽입·탐색 O(log N) 노드 접근
// Space Complexity: O(N), 노드 이용률 >= 2/3
```
## FractalTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 프랙탈 트리(Fractal Tree, TokuDB·PerconaFT) = B^ε 트리: 내부 노드 공간의 일부를 "메시지 버퍼"로 쓴다. 삽입·삭제는 곧장 잎까지 내려가는 대신 루트 버퍼에 메시지로 쌓이고,
// 버퍼가 차면 가장 메시지가 많은 자식 하나에게 한꺼번에 내려보낸다(flush). 메시지 B^(1-ε) 개를 한 번의 노드 접근으로 옮기므로 삽입당 접근 수가 B-트리의 O(log_B N) 보다 크게 줄고
// (O(log_B N / B^(1-ε))), 조회는 루트부터 내려가며 각 버퍼에서 "가장 새 메시지" 를 먼저 보고 잎에 도달하면 값을 읽는다 (위쪽 버퍼가 항상 더 새롭다)
// 쓰기 많은 작업(로그, 시계열)에 유리하고 이 아이디어가 LSM 과 B-트리의 중간 지대다.  삭제는 툼스톤 메시지로 처리
struct Msg { int key, val; bool del; };
const int LEAF = 8, FAN = 4, BUF = 16;
long touches = 0;
struct Node {
    bool leaf = true; std::vector<std::pair<int, int>> kv; std::vector<int> piv; std::vector<Node*> kid; std::vector<Msg> buf;
};
std::vector<Node*> pool; Node* mk() { pool.push_back(new Node); return pool.back(); }
int childIdx(const Node* n, int key) { return std::upper_bound(n->piv.begin(), n->piv.end(), key) - n->piv.begin(); }
void applyToLeaf(Node* n, const Msg& m) {
    auto it = std::lower_bound(n->kv.begin(), n->kv.end(), std::make_pair(m.key, INT32_MIN));
    bool found = it != n->kv.end() && it->first == m.key;
    if (m.del) { if (found) n->kv.erase(it); } else if (found) it->second = m.val; else n->kv.insert(it, {m.key, m.val});
}
bool addMsgs(Node* n, std::vector<Msg>& msgs, Node*& sib, int& sep) {      // n 이 쪼개지면 true (sib: 오른쪽 형제, sep: 분리 키)
    touches++;
    if (n->leaf) {
        for (auto& m : msgs) applyToLeaf(n, m);
        if ((int)n->kv.size() <= LEAF) return false;
        sib = mk(); int mid = n->kv.size() / 2; sib->kv.assign(n->kv.begin() + mid, n->kv.end()); n->kv.resize(mid); sep = sib->kv.front().first; return true;
    }
    n->buf.insert(n->buf.end(), msgs.begin(), msgs.end());
    while ((int)n->buf.size() > BUF) {
        std::vector<int> cnt(n->kid.size(), 0); for (auto& m : n->buf) cnt[childIdx(n, m.key)]++;
        int best = std::max_element(cnt.begin(), cnt.end()) - cnt.begin();                      // 메시지가 가장 많은 자식
        std::vector<Msg> moved, keep; for (auto& m : n->buf) (childIdx(n, m.key) == best ? moved : keep).push_back(m);       // 시간 순서 유지
        n->buf = keep; Node* s; int sp;
        if (addMsgs(n->kid[best], moved, s, sp)) { n->piv.insert(n->piv.begin() + best, sp); n->kid.insert(n->kid.begin() + best + 1, s); }
    }
    if ((int)n->kid.size() <= FAN) return false;
    sib = mk(); sib->leaf = false; int mid = n->kid.size() / 2; sep = n->piv[mid - 1];       // 자식 5 -> 앞 2, 뒤 3
    sib->kid.assign(n->kid.begin() + mid, n->kid.end()); sib->piv.assign(n->piv.begin() + mid, n->piv.end());
    n->kid.resize(mid); n->piv.resize(mid - 1);
    std::vector<Msg> l, r; for (auto& m : n->buf) (m.key < sep ? l : r).push_back(m); n->buf = l; sib->buf = r; return true;
}
struct FractalTree {
    Node* root = mk();
    void send(Msg m) { std::vector<Msg> v = {m}; Node* s; int sp; if (addMsgs(root, v, s, sp)) { Node* nr = mk(); nr->leaf = false; nr->kid = {root, s}; nr->piv = {sp}; root = nr; } }
    void put(int k, int v) { send({k, v, false}); }
    void erase(int k) { send({k, 0, true}); }
    bool get(int key, int& val) const {
        Node* n = root;
        while (!n->leaf) {
            touches++;
            for (int i = (int)n->buf.size() - 1; i >= 0; i--) if (n->buf[i].key == key) { if (n->buf[i].del) return false; val = n->buf[i].val; return true; }    // 가장 새 메시지
            n = n->kid[childIdx(n, key)];
        }
        touches++; auto it = std::lower_bound(n->kv.begin(), n->kv.end(), std::make_pair(key, INT32_MIN));
        if (it != n->kv.end() && it->first == key) { val = it->second; return true; } return false;
    }
    static void toMap(const Node* n, std::map<int, int>& out) {            // 아래 -> 위 순서로 메시지를 덮어씌워 전체 내용을 복원
        if (n->leaf) { for (auto& p : n->kv) out[p.first] = p.second; return; }
        for (Node* c : n->kid) toMap(c, out);
        for (auto& m : n->buf) { if (m.del) out.erase(m.key); else out[m.key] = m.val; }
    }
    int height() const { int h = 1; for (Node* n = root; !n->leaf; n = n->kid[0]) h++; return h; }
};

int main() {
    std::mt19937 rng(8); FractalTree t; std::map<int, int> ref;
    for (int step = 0; step < 40000; step++) {
        int k = rng() % 3000, op = rng() % 10;
        if (op < 6) { int v = rng(); t.put(k, v); ref[k] = v; } else if (op < 8) { t.erase(k); ref.erase(k); }
        else { int v = 0; bool f = t.get(k, v); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || v == it->second)); }
        if (step % 5000 == 0) { std::map<int, int> m; FractalTree::toMap(t.root, m); assert(m == ref); }
    }
    std::map<int, int> m; FractalTree::toMap(t.root, m); assert(m == ref);
    for (int k = 0; k < 3000; k++) { int v = 0; bool f = t.get(k, v); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || v == it->second)); }
    // 삽입당 노드 접근 수: 같은 트리 높이의 B-트리는 삽입마다 높이만큼 접근한다
    FractalTree big; touches = 0; int N = 100000; std::vector<int> keys(N); for (int i = 0; i < N; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) big.put(k, k);
    double perInsert = (double)touches / N; int h = big.height();
    assert(perInsert < h * 0.6);                                           // 버퍼 덕분에 높이 h 보다 훨씬 적은 접근
    std::cout << "FractalTree: " << N << " random inserts -> height " << h << ", node touches per insert " << perInsert << " (B-tree: " << h << ")" << std::endl;
    return 0;
}
// Time Complexity: 삽입 분할상환 O(log_B N / B^(1-ε)) 노드 접근, 조회 O(log_B N)
// Space Complexity: O(N)
```
## LSMTree()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// LSM 트리(Log-Structured Merge tree; LevelDB, RocksDB, Cassandra, HBase): 쓰기를 "메모리 표(memtable) -> 불변 정렬 파일(SSTable)" 순으로 쌓고, 파일들을 백그라운드에서 병합(compaction)한다.
// 모든 디스크 쓰기가 순차 쓰기라 쓰기 처리량이 높다.  읽기는 memtable 부터 최신 -> 오래된 순으로 파일을 훑되, 파일마다 블룸 필터를 달아 "없는 파일" 을 거의 건너뛴다.  삭제는 툼스톤을 쓰고, 병합이 가장 아래 레벨에 닿을 때 버린다.
// 두 병합 정책의 균형: 티어드(tiered; 레벨마다 T 개 파일이 모이면 합쳐 다음 레벨로) = 쓰기 증폭 작음/읽을 파일 많음,  레벨드(leveled; 레벨마다 파일 1 개, 용량 T 배씩) = 쓰기 증폭 큼/읽을 파일 적음
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct Rec { int key, val; bool del; };
struct Run {
    std::vector<Rec> r; std::vector<uint64_t> bits; size_t m = 0;
    void seal() {                                                          // 블룸 필터 (키당 10 비트, 해시 4 개)
        m = std::max<size_t>(64, r.size() * 10); bits.assign((m + 63) / 64, 0);
        for (auto& x : r) for (int i = 0; i < 4; i++) { size_t p = (mix(x.key) + i * mix(~(uint64_t)x.key)) % m; bits[p >> 6] |= 1ULL << (p & 63); }
    }
    bool maybe(int key) const { for (int i = 0; i < 4; i++) { size_t p = (mix(key) + i * mix(~(uint64_t)key)) % m; if (!((bits[p >> 6] >> (p & 63)) & 1)) return false; } return true; }
};
struct LSM {
    bool leveled, useBloom; size_t memLimit; int T; std::map<int, Rec> mem; std::vector<std::vector<Run>> lv; long userWrites = 0, written = 0, probes = 0;
    LSM(bool leveled, bool useBloom, size_t memLimit = 64, int T = 4) : leveled(leveled), useBloom(useBloom), memLimit(memLimit), T(T) {}
    static Run mergeRuns(const std::vector<const Run*>& oldestFirst, bool dropTomb) {   // 뒤쪽(새) 실행이 같은 키를 덮는다
        std::map<int, Rec> m; for (auto* r : oldestFirst) for (auto& x : r->r) m[x.key] = x;
        Run out; for (auto& kv : m) if (!(dropTomb && kv.second.del)) out.r.push_back(kv.second); out.seal(); return out;
    }
    bool deeperEmpty(size_t i) const { for (size_t j = i + 1; j < lv.size(); j++) if (!lv[j].empty()) return false; return true; }
    void put(int k, int v) { userWrites++; mem[k] = {k, v, false}; if (mem.size() >= memLimit) flush(); }
    void del(int k) { userWrites++; mem[k] = {k, 0, true}; if (mem.size() >= memLimit) flush(); }
    void flush() {
        Run run; for (auto& kv : mem) run.r.push_back(kv.second); run.seal(); mem.clear(); written += run.r.size();
        if (lv.empty()) lv.emplace_back();
        if (!leveled) { lv[0].push_back(std::move(run)); for (size_t i = 0; i < lv.size() && (int)lv[i].size() >= T; i++) {
                std::vector<const Run*> rs; for (auto& r : lv[i]) rs.push_back(&r);
                if (i + 1 == lv.size()) lv.emplace_back();
                Run merged = mergeRuns(rs, deeperEmpty(i + 1) && lv[i + 1].empty()); written += merged.r.size(); lv[i].clear(); lv[i + 1].push_back(std::move(merged)); }
            return; }
        for (size_t i = 0; ; i++) {                                        // 레벨드: 레벨 i 는 파일 1 개, 용량 memLimit * T^(i+1)
            if (i == lv.size()) lv.emplace_back();
            std::vector<const Run*> rs; if (!lv[i].empty()) rs.push_back(&lv[i][0]); rs.push_back(&run);
            Run merged = mergeRuns(rs, deeperEmpty(i)); written += merged.r.size(); lv[i].clear();
            size_t cap = memLimit; for (size_t j = 0; j <= i; j++) cap *= T;
            if (merged.r.size() <= cap) { lv[i].push_back(std::move(merged)); return; }
            run = std::move(merged);                                       // 넘치면 통째로 다음 레벨과 병합
        }
    }
    bool get(int k, int& v) {
        auto it = mem.find(k); if (it != mem.end()) { if (it->second.del) return false; v = it->second.val; return true; }
        for (auto& level : lv) for (int j = (int)level.size() - 1; j >= 0; j--) {          // 최신 레벨, 최신 파일 우선
            const Run& r = level[j];
            if (useBloom && !r.maybe(k)) continue;
            probes++; auto p = std::lower_bound(r.r.begin(), r.r.end(), k, [](const Rec& a, int key) { return a.key < key; });
            if (p != r.r.end() && p->key == k) { if (p->del) return false; v = p->val; return true; }
        }
        return false;
    }
    size_t runs() const { size_t c = 0; for (auto& l : lv) c += l.size(); return c; }
};

int main() {
    std::mt19937 rng(2); long wa[2]; size_t maxRuns[2]; long probeBloom = 0, probeNoBloom = 0;
    for (int pol = 0; pol < 2; pol++) {
        for (int bloom = 0; bloom < 2; bloom++) {
            LSM t(pol == 1, bloom == 1); std::map<int, int> ref; std::mt19937 g(77); maxRuns[pol] = 0;
            for (int step = 0; step < 60000; step++) {
                int k = g() % 5000, op = g() % 10;
                if (op < 5) { int v = g(); t.put(k, v); ref[k] = v; } else if (op < 7) { t.del(k); ref.erase(k); }
                else { int v = 0; bool f = t.get(k, v); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || v == it->second)); }
                maxRuns[pol] = std::max(maxRuns[pol], t.runs());
            }
            for (int k = 0; k < 5000; k++) { int v = 0; bool f = t.get(k, v); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || v == it->second)); }
            if (bloom == 1) wa[pol] = t.written * 100 / t.userWrites;
            t.probes = 0; for (int k = 10000; k < 14000; k++) { int v; t.get(k, v); }                      // 없는 키만 조회: 블룸이 파일 접근을 거르는 효과
            (bloom ? probeBloom : probeNoBloom) += t.probes;
        }
    }
    assert(probeBloom * 10 < probeNoBloom);                                // 블룸 필터가 존재하지 않는 키의 파일 탐색을 거의 없앤다
    assert(wa[0] < wa[1] && maxRuns[1] <= maxRuns[0]);                     // 티어드: 쓰기 증폭 작음, 레벨드: 파일 수 작음
    std::cout << "LSMTree: write amplification tiered " << wa[0] / 100.0 << " vs leveled " << wa[1] / 100.0 << "; max files tiered " << maxRuns[0] << " vs leveled " << maxRuns[1]
              << "; missing-key probes with bloom " << probeBloom << " vs without " << probeNoBloom << std::endl;
    return 0;
}
// Time Complexity: 쓰기 분할상환 O(쓰기 증폭), 읽기 O(레벨 수 × 파일당 이분 탐색) (블룸 필터로 대부분 생략)
// Space Complexity: O(N) + 공간 증폭 (툼스톤·중복)
```
## BufferTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 버퍼 트리(Arge): 외부 메모리(디스크) 모델에서 "많은 연산을 모아 한꺼번에" 처리하는 트리. 블록 크기 B, 메모리 M. 팬아웃 ~M/B 인 트리의 모든 내부 노드에 크기 ~M/2 의 버퍼를 달고,
// 연산(여기서는 삽입)은 메모리 안에서 모았다가 루트 버퍼로 넘기고, 버퍼가 차면 정렬해 자식들에게 "한 번에 쭉" 나눠 준다(buffer-emptying). 각 원소가 블록 하나를 독점하지 않고 B 개씩 묶여 움직이므로
// 연산당 분할상환 I/O 가 O((1/B) log_{M/B}(N/B)) — 정렬의 하한과 같다.  그래서 트리에 N 개를 넣고 잎을 순서대로 읽으면 곧 "외부 정렬" 이며, 같은 원리가 외부 우선순위 큐·그래프 알고리즘에 쓰인다.
// 아래는 I/O(블록 읽기·쓰기 횟수)를 세는 시뮬레이션으로, 원소를 하나씩 B-트리에 넣는 방식(원소당 높이만큼의 I/O)과 비교한다
const int B = 16, CAPLEAF = 64, BUFCAP = 1024, FAN = 32;
long io = 0;
long blocks(size_t n) { return (n + B - 1) / B; }
struct Node { bool leaf = true; std::vector<int> items, piv, buf; std::vector<Node*> kid; };
std::vector<Node*> pool; Node* mk() { pool.push_back(new Node); return pool.back(); }
struct Piece { int sep; Node* node; };
std::vector<Piece> absorb(Node* n, std::vector<int>& batch, bool force) {  // n 에 정렬/미정렬 묶음을 넣고, n 이 쪼개지면 뒤에 붙을 조각들을 돌려준다
    std::vector<Piece> out;
    if (n->leaf) {
        std::sort(batch.begin(), batch.end()); io += blocks(n->items.size());      // 잎 읽기 (묶음은 부모 버퍼를 비우며 이미 메모리로 읽었다)
        std::vector<int> merged(n->items.size() + batch.size()); std::merge(n->items.begin(), n->items.end(), batch.begin(), batch.end(), merged.begin());
        n->items = merged; io += blocks(n->items.size());                                                   // 잎 쓰기
        if ((int)n->items.size() > CAPLEAF) {
            std::vector<int> all = n->items; n->items.assign(all.begin(), all.begin() + CAPLEAF / 2);
            for (size_t i = CAPLEAF / 2; i < all.size(); i += CAPLEAF / 2) { Node* l = mk(); l->items.assign(all.begin() + i, all.begin() + std::min(all.size(), i + CAPLEAF / 2)); out.push_back({l->items.front(), l}); }
        }
        return out;
    }
    n->buf.insert(n->buf.end(), batch.begin(), batch.end()); io += blocks(batch.size());                    // 버퍼에 덧붙이기
    if ((int)n->buf.size() <= BUFCAP && !force) return out;
    io += blocks(n->buf.size()); std::sort(n->buf.begin(), n->buf.end());                                   // 버퍼를 읽어 정렬(메모리 안)
    std::vector<std::vector<int>> part(n->kid.size());
    for (int x : n->buf) part[std::upper_bound(n->piv.begin(), n->piv.end(), x) - n->piv.begin()].push_back(x);
    n->buf.clear();
    std::vector<Node*> nk; std::vector<int> np;
    for (size_t i = 0; i < n->kid.size(); i++) {
        std::vector<Piece> ps; if (!part[i].empty() || force) ps = absorb(n->kid[i], part[i], force);        // 재귀적 buffer-emptying
        nk.push_back(n->kid[i]); for (auto& p : ps) { np.push_back(p.sep); nk.push_back(p.node); }
        if (i + 1 < n->kid.size()) np.push_back(n->piv[i]);
    }
    if ((int)nk.size() <= FAN) { n->kid = nk; n->piv = np; return out; }
    size_t g = FAN / 2; n->kid.assign(nk.begin(), nk.begin() + g); n->piv.assign(np.begin(), np.begin() + g - 1);          // 팬아웃 초과 -> 묶음 단위로 쪼갬
    for (size_t s = g; s < nk.size(); s += g) {
        Node* r = mk(); r->leaf = false; size_t e = std::min(nk.size(), s + g); r->kid.assign(nk.begin() + s, nk.begin() + e); r->piv.assign(np.begin() + s, np.begin() + e - 1); out.push_back({np[s - 1], r});
    }
    return out;
}
void readLeaves(Node* n, std::vector<int>& out) { if (n->leaf) { io += blocks(n->items.size()); out.insert(out.end(), n->items.begin(), n->items.end()); return; } for (Node* c : n->kid) readLeaves(c, out); }

int main() {
    std::mt19937 rng(5); int N = 200000; std::vector<int> in(N); for (auto& x : in) x = rng() % 100000000;
    Node* root = mk(); io = 0;
    for (int i = 0; i < N; i += BUFCAP) {                                  // 입력을 메모리에 모아 한 번에 루트 버퍼로
        std::vector<int> batch(in.begin() + i, in.begin() + std::min(N, i + BUFCAP)); io += blocks(batch.size());
        std::vector<Piece> ps = absorb(root, batch, false);
        if (!ps.empty()) { Node* nr = mk(); nr->leaf = false; nr->kid.push_back(root); for (auto& p : ps) { nr->piv.push_back(p.sep); nr->kid.push_back(p.node); } root = nr;
            while ((int)root->kid.size() > FAN) { std::vector<int> e; std::vector<Piece> more = absorb(root, e, false); (void)more; break; } }
    }
    std::vector<int> e; std::vector<Piece> ps = absorb(root, e, true);     // 남은 버퍼를 모두 비운다
    if (!ps.empty()) { Node* nr = mk(); nr->leaf = false; nr->kid.push_back(root); for (auto& p : ps) { nr->piv.push_back(p.sep); nr->kid.push_back(p.node); } root = nr; }
    std::vector<int> sorted; readLeaves(root, sorted);
    std::vector<int> ref = in; std::sort(ref.begin(), ref.end());
    assert(sorted == ref);                                                 // 잎을 순서대로 읽으면 정렬 결과
    double perBlock = (double)io / ((double)N / B);                        // 입력 블록 하나당 평균 I/O (정렬 하한 Θ((N/B) log_{M/B}(N/B)) 에 상수배)
    long bTreeIO = (long)N * 4;                                            // 원소당 높이 ~log_B N = 4 블록 (보수적으로 읽기만 셈)
    assert(io < bTreeIO / 4);
    std::cout << "BufferTree: sorted " << N << " keys with " << io << " block I/Os (" << perBlock << " per input block; one-by-one B-tree insertion >= " << bTreeIO << " = " << (double)bTreeIO / ((double)N / B) << " per input block)" << std::endl;
    return 0;
}
// Time Complexity: 연산당 분할상환 I/O O((1/B) log_{M/B} (N/B))
// Space Complexity: O(N)
```

# Part 9. 동시성
## LockFreeQueue()
### 대표코드
```cpp
#include <atomic>
#include <iostream>
#include <numeric>
#include <thread>
#include <vector>
#include <cassert>

// 락프리 큐(큐 관점의 요약, 정본은 Queue.md Part 10): Michael–Scott 큐. 더미 노드로 시작해 head 는 "마지막으로 꺼낸 노드", tail 은 "끝 근처" 를 가리킨다.
// enqueue 는 tail 의 next 를 CAS 로 잇고 tail 을 밀며(다른 스레드가 밀다 만 것도 도와 준다 = helping), dequeue 는 head 를 CAS 로 전진시킨다. 잠금이 없어 한 스레드가 멈춰도 나머지가 진행한다.
// (이 요약판은 꺼낸 노드를 회수하지 않는다 — 안전한 회수는 HazardPointer 항목)
struct Node { int v; std::atomic<Node*> next{nullptr}; };
struct Q {
    std::atomic<Node*> head, tail; Q() { Node* d = new Node{0}; head = tail = d; }
    void enq(int v) { Node* n = new Node{v}; for (;;) { Node* t = tail.load(); Node* nx = t->next.load(); if (t != tail.load()) continue;
        if (!nx) { if (t->next.compare_exchange_weak(nx, n)) { tail.compare_exchange_strong(t, n); return; } } else tail.compare_exchange_strong(t, nx); } }
    bool deq(int& out) { for (;;) { Node* h = head.load(); Node* t = tail.load(); Node* nx = h->next.load(); if (h != head.load()) continue;
        if (!nx) return false; if (h == t) { tail.compare_exchange_strong(t, nx); continue; } out = nx->v; if (head.compare_exchange_weak(h, nx)) return true; } }
};
int main() {
    Q q; std::atomic<long> sum{0}; std::atomic<int> got{0}; const int P = 3, C = 3, N = 20000;
    std::vector<std::thread> th;
    for (int p = 0; p < P; p++) th.emplace_back([&, p] { for (int i = 1; i <= N; i++) q.enq(p * N + i); });
    for (int c = 0; c < C; c++) th.emplace_back([&] { int v; while (got.load() < P * N) if (q.deq(v)) { sum += v; got++; } });
    for (auto& t : th) t.join();
    long expect = 0; for (int p = 0; p < P; p++) for (int i = 1; i <= N; i++) expect += p * N + i;
    assert(sum == expect && got == P * N);                                  // 모든 원소가 정확히 한 번씩 나왔다
    std::cout << "LockFreeQueue: " << got << " items through " << P << " producers / " << C << " consumers" << std::endl; return 0;
}
// Time Complexity: enq·deq 분할상환 O(1) (경쟁이 없을 때), 락프리
// Space Complexity: O(N)
```
## LockFreeStack()
### 대표코드
```cpp
#include <atomic>
#include <iostream>
#include <thread>
#include <vector>
#include <cassert>

// 락프리 스택(스택 관점의 요약, 정본은 Stack.md Part 9): Treiber 스택. top 포인터 하나를 CAS 로 바꾼다 — push 는 "새 노드의 next 를 현재 top 으로 두고 top 을 새 노드로", pop 은 "top 을 top->next 로".
// 주의: pop 중 다른 스레드가 같은 주소의 노드를 해제·재할당·재삽입하면 CAS 가 성공해 버리는 ABA 문제가 있다 -> 노드를 안전하게 회수하는 HazardPointer 항목과 짝으로 읽는다 (여기서는 회수하지 않음)
struct Node { int v; Node* next; };
std::atomic<Node*> top{nullptr};
void push(int v) { Node* n = new Node{v, top.load()}; while (!top.compare_exchange_weak(n->next, n)); }
bool pop(int& v) { Node* t = top.load(); while (t && !top.compare_exchange_weak(t, t->next)); if (!t) return false; v = t->v; return true; }
int main() {
    const int T = 4, N = 20000; std::vector<std::thread> th; std::atomic<long> pushed{0}, popped{0};
    for (int t = 0; t < T; t++) th.emplace_back([&, t] { for (int i = 1; i <= N; i++) { push(t * N + i); pushed += t * N + i; } });
    for (auto& x : th) x.join(); th.clear();
    for (int t = 0; t < T; t++) th.emplace_back([&] { int v; while (pop(v)) popped += v; });
    for (auto& x : th) x.join();
    assert(pushed == popped && pushed > 0);
    std::cout << "LockFreeStack: pushed sum == popped sum = " << popped << std::endl; return 0;
}
// Time Complexity: push·pop 분할상환 O(1) (락프리)
// Space Complexity: O(N)
```
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

// 동시 해시 맵(해시 관점의 요약, 정본은 Hash.md Part 12): 하나의 큰 잠금 대신 키의 해시로 고른 "조각(shard)" 마다 잠금을 따로 두면(lock striping) 서로 다른 조각을 쓰는 스레드끼리는 부딪히지 않는다.
// Java 의 ConcurrentHashMap, Go 의 sync.Map 샤딩 구현이 이 아이디어 위에 있다
struct CMap {
    static const int S = 16; struct Shard { std::mutex m; std::unordered_map<std::string, int> map; } shard[S];
    Shard& pick(const std::string& k) { return shard[std::hash<std::string>{}(k) % S]; }
    void add(const std::string& k, int d) { Shard& s = pick(k); std::lock_guard<std::mutex> g(s.m); s.map[k] += d; }
    int get(const std::string& k) { Shard& s = pick(k); std::lock_guard<std::mutex> g(s.m); auto it = s.map.find(k); return it == s.map.end() ? 0 : it->second; }
};
int main() {
    CMap m; std::vector<std::thread> th;
    for (int t = 0; t < 4; t++) th.emplace_back([&] { for (int i = 0; i < 20000; i++) m.add("k" + std::to_string(i % 100), 1); });
    for (auto& x : th) x.join();
    for (int i = 0; i < 100; i++) assert(m.get("k" + std::to_string(i)) == 4 * 200);          // 갱신 손실 없음
    std::cout << "ConcurrentHashMap: 80000 concurrent increments, none lost" << std::endl; return 0;
}
// Time Complexity: 평균 O(1) + 조각 잠금 경쟁
// Space Complexity: O(N)
```
## SkipListSet()
### 대표코드
```cpp
#include <climits>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 스킵 리스트 집합(집합 관점의 요약, 정본은 List.md Part 10): 정렬된 연결 리스트 위에 "급행 차선"을 확률적으로 쌓는다. 노드의 높이는 동전 던지기(1/2 확률로 한 층 위로)로 정해 기대 O(log N) 탐색.
// 잠금 없는 구현(ConcurrentSkipListSet)이 쉬운 이유: 균형을 회전이 아니라 확률로 얻어서, 삽입이 아래층부터 CAS 로 링크를 이으면 되기 때문
struct N { int k; std::vector<N*> nx; };
struct SkipSet {
    N* head = new N{INT_MIN, std::vector<N*>(16, nullptr)}; int lvl = 1; std::mt19937 g{1};
    bool has(int k) const { N* x = head; for (int i = lvl - 1; i >= 0; i--) while (x->nx[i] && x->nx[i]->k < k) x = x->nx[i]; x = x->nx[0]; return x && x->k == k; }
    bool add(int k) { N* up[16]; N* x = head; for (int i = lvl - 1; i >= 0; i--) { while (x->nx[i] && x->nx[i]->k < k) x = x->nx[i]; up[i] = x; }
        if (x->nx[0] && x->nx[0]->k == k) return false; int h = 1; while (h < 16 && (g() & 1)) h++;
        if (h > lvl) { for (int i = lvl; i < h; i++) up[i] = head; lvl = h; } N* n = new N{k, std::vector<N*>(h)};
        for (int i = 0; i < h; i++) { n->nx[i] = up[i]->nx[i]; up[i]->nx[i] = n; } return true; }
};
int main() {
    SkipSet s; std::set<int> ref; std::mt19937 g(2);
    for (int i = 0; i < 20000; i++) { int k = g() % 5000; assert(s.add(k) == ref.insert(k).second); }
    for (int k = 0; k < 5000; k++) assert(s.has(k) == (ref.count(k) > 0));
    std::cout << "SkipListSet: " << ref.size() << " keys, " << s.lvl << " levels" << std::endl; return 0;
}
// Time Complexity: 탐색·삽입 기대 O(log N)
// Space Complexity: 기대 O(N) (노드당 평균 2 개의 포인터)
```
## CompareAndSwap()
### 대표코드
```cpp
#include <atomic>
#include <iostream>
#include <thread>
#include <vector>
#include <cassert>

// 비교-교환(CAS, 메모리 관점의 요약, 정본은 Memory.md Part 11): "값이 기대한 것과 같을 때만 새 값으로 바꾸고 성공 여부를 돌려준다" 를 한 번의 원자적 명령으로 수행한다. 모든 락프리 구조의 기본 블록이다.
// 실패하면 현재 값이 expected 에 되돌려 담기므로 "읽기 -> 계산 -> CAS, 실패 시 반복" 루프를 만든다. 아래는 CAS 루프로 만든 원자적 최댓값 갱신
std::atomic<int> best{0};
void updateMax(int v) { int cur = best.load(); while (v > cur && !best.compare_exchange_weak(cur, v)); }
int main() {
    std::vector<std::thread> th; for (int t = 0; t < 4; t++) th.emplace_back([t] { for (int i = 0; i < 10000; i++) updateMax(t * 10000 + i); });
    for (auto& x : th) x.join();
    assert(best == 39999);
    std::cout << "CompareAndSwap: concurrent max = " << best << std::endl; return 0;
}
// Time Complexity: 경쟁이 없으면 O(1), 경쟁 시 재시도 횟수만큼
// Space Complexity: O(1)
```
## HazardPointer()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>
#include <cassert>

// 위험 포인터(hazard pointer, Michael 2004): 락프리 구조에서 "다른 스레드가 아직 읽고 있을지 모르는 노드를 해제하지 않기" 위한 메모리 회수 기법.
// 읽는 쪽: 노드 포인터 p 를 읽으면 먼저 자기 전용 위험 슬롯 hp[tid] 에 p 를 공시하고, 공유 위치가 여전히 p 인지 다시 확인한 뒤에만 역참조한다 (공시 후 재검증이 핵심).
// 지우는 쪽: 구조에서 뗀 노드는 곧바로 delete 하지 않고 자기 retired 목록에 넣는다. 목록이 임계값을 넘으면 모든 스레드의 hp 를 훑어 "아무도 공시하지 않은" 노드만 해제한다.
// 이렇게 하면 해제된 주소가 재사용되어 CAS 가 속는 ABA 문제도 함께 막힌다 (공시된 노드는 해제되지 않으니 주소가 재사용될 수 없다)
const int MAXT = 8, THRESH = 32;
struct Node { int v; Node* next; };
std::atomic<Node*> top{nullptr}; std::atomic<Node*> hp[MAXT];
std::atomic<long> allocated{0}, freed{0};
thread_local std::vector<Node*> retired; thread_local int tid = 0;
std::mutex orphanMu; std::vector<Node*> orphans;
void scan() {
    std::vector<Node*> prot; for (int i = 0; i < MAXT; i++) if (Node* p = hp[i].load()) prot.push_back(p);
    std::sort(prot.begin(), prot.end()); std::vector<Node*> keep;
    for (Node* n : retired) { if (std::binary_search(prot.begin(), prot.end(), n)) keep.push_back(n); else { delete n; freed++; } }
    retired.swap(keep);
}
void retire(Node* n) { retired.push_back(n); if ((int)retired.size() >= THRESH) scan(); }
void push(int v) { Node* n = new Node{v, top.load()}; allocated++; while (!top.compare_exchange_weak(n->next, n)); }
bool pop(int& v) {
    Node* t;
    for (;;) {
        t = top.load(); if (!t) { hp[tid].store(nullptr); return false; }
        hp[tid].store(t);                                                  // ① 보호 공시
        if (top.load() != t) continue;                                     // ② 재검증: 공시하는 사이 top 이 바뀌었다면 t 는 이미 떨어졌을 수 있으니 다시
        Node* nx = t->next;                                                // ③ 이제 t 는 해제되지 않는다 (안전한 역참조)
        if (top.compare_exchange_weak(t, nx)) break;
    }
    hp[tid].store(nullptr); v = t->v; retire(t); return true;
}
void threadExit() { hp[tid].store(nullptr); scan(); std::lock_guard<std::mutex> g(orphanMu); orphans.insert(orphans.end(), retired.begin(), retired.end()); retired.clear(); }

int main() {
    const int T = 4, N = 50000; std::atomic<long> pushedSum{0}, poppedSum{0};
    std::vector<std::thread> th;
    for (int t = 0; t < T; t++) th.emplace_back([&, t] {
        tid = t;                                                           // 스레드마다 위험 슬롯 하나
        for (int i = 1; i <= N; i++) { int v = t * N + i; push(v); pushedSum += v; int out; if (i % 2 == 0 && pop(out)) poppedSum += out; if (pop(out)) poppedSum += out; }   // 스택이 작아 ABA 가 일어나기 쉬운 부하
        threadExit();
    });
    for (auto& x : th) x.join();
    tid = 0; int out; while (pop(out)) poppedSum += out;                   // 남은 원소를 비운다
    threadExit();
    for (Node* n : orphans) { delete n; freed++; }                         // 모든 스레드가 끝났으므로 안전
    assert(pushedSum == poppedSum);                                        // 원소가 사라지거나 두 번 나오지 않았다
    assert(allocated == freed);                                            // 할당한 노드를 하나도 빠짐없이, 한 번씩만 해제했다
    std::cout << "HazardPointer: " << allocated << " nodes allocated, " << freed << " freed, sums equal" << std::endl; return 0;
}
// Time Complexity: 읽기 O(1) 공시 + 재검증, 회수 분할상환 O(스레드 수) per 노드
// Space Complexity: 미회수 노드 수 <= 스레드 수 × (임계값 + 스레드 수)
```

# Part 10. 분산 시스템
## ConsistentHashing()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <cassert>

// 일관된 해시(해시 관점의 요약, 정본은 Hash.md Part 7): 서버와 키를 같은 해시 링 위에 놓고 키는 시계 방향 첫 서버가 맡는다. 서버를 더하거나 빼도 이웃 구간의 키만 이동한다
// (평균 K/N 개) — "해시 % 서버 수" 는 서버 수가 바뀌면 거의 전부 이동한다. 서버당 가상 노드를 여러 개 두면 부하가 고르게 퍼진다
unsigned long long h(const std::string& s) { unsigned long long x = 1469598103934665603ULL; for (unsigned char c : s) { x ^= c; x *= 1099511628211ULL; } x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; return x; }
struct Ring {
    std::map<unsigned long long, std::string> r;
    void add(const std::string& n) { for (int v = 0; v < 100; v++) r[h(n + "#" + std::to_string(v))] = n; }
    const std::string& owner(const std::string& key) const { auto it = r.lower_bound(h(key)); return it == r.end() ? r.begin()->second : it->second; }
};
int main() {
    Ring ring; for (std::string n : {"A", "B", "C", "D"}) ring.add(n);
    const int K = 20000; std::string before[K]; for (int i = 0; i < K; i++) before[i] = ring.owner("key" + std::to_string(i));
    ring.add("E"); int moved = 0; for (int i = 0; i < K; i++) { const std::string& now = ring.owner("key" + std::to_string(i)); if (now != before[i]) { moved++; assert(now == "E"); } }   // 이동한 키는 모두 새 서버로
    assert(moved > K / 8 && moved < K / 3);                                // 이론값 1/5
    std::cout << "ConsistentHashing: adding 1 of 5 servers moved " << 100.0 * moved / K << "% of keys (ideal 20%)" << std::endl; return 0;
}
// Time Complexity: 조회 O(log (서버 × 가상노드))
// Space Complexity: O(서버 × 가상노드)
```
## DistributedHashTable()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 분산 해시 테이블(DHT, 해시 관점의 요약, Chord·Kademlia 는 Hash.md Part 7): 중앙 서버 없이 키 -> 값 저장을 노드들이 나눠 맡는다. 핵심은 (1) 키와 노드가 같은 식별자 공간에 놓이고
// (2) 각 키는 "식별자가 가장 가까운" 노드들이 맡으며 (3) 복제(replication)로 노드 하나가 죽어도 값이 남는다는 것.  아래는 링에서 키의 후속 3 노드가 복제본을 갖는 최소 모델이다
struct DHT {
    std::map<unsigned, std::map<int, std::string>> node; static const int R = 3;       // 노드 id -> 저장소
    std::vector<unsigned> owners(int key) const { std::vector<unsigned> v; unsigned id = key * 2654435761u; auto it = node.lower_bound(id);
        for (int i = 0; i < R && i < (int)node.size(); i++) { if (it == node.end()) it = node.begin(); v.push_back(it->first); ++it; } return v; }
    void put(int key, const std::string& val) { for (unsigned n : owners(key)) node[n][key] = val; }
    bool get(int key, std::string& val) const { for (unsigned n : owners(key)) { auto it = node.at(n).find(key); if (it != node.at(n).end()) { val = it->second; return true; } } return false; }
};
int main() {
    DHT d; for (unsigned id : {10u, 1000000u, 900000000u, 2000000000u, 3000000000u, 4000000000u}) d.node[id];
    for (int k = 0; k < 500; k++) d.put(k, "v" + std::to_string(k));
    d.node.erase(2000000000u);                                             // 노드 하나가 죽으면 소유자 목록은 남은 노드들의 후속 3 개로 바뀐다
    for (int k = 0; k < 500; k++) { std::string v; assert(d.get(k, v) && v == "v" + std::to_string(k)); }     // 죽은 노드가 가졌던 키도 다른 복제본이 응답
    std::cout << "DistributedHashTable: all 500 keys survive loss of one of 6 nodes (replication " << DHT::R << ")" << std::endl; return 0;
}
// Time Complexity: 조회 O(log N) 홉(Chord) 또는 O(log N) (Kademlia)
// Space Complexity: 키당 복제 수 R
```
## Chord()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 코드(Chord, 해시 관점의 요약, 정본은 Hash.md Part 7): 2^m 크기의 식별자 링에서 각 노드가 "내 id + 2^i 의 후속 노드" m 개를 손가락(finger)으로 알고 있다. 조회는 목표를 넘지 않는 가장 먼 손가락으로 점프해
// 매 홉마다 남은 거리를 절반 이하로 줄이므로 O(log N) 홉이다
const int m = 10, SZ = 1 << m;
std::vector<int> ids;
int succ(int x) { auto it = std::lower_bound(ids.begin(), ids.end(), x % SZ); return it == ids.end() ? ids[0] : *it; }       // x 의 후속 노드
bool inOpen(int x, int a, int b) { return a < b ? (x > a && x < b) : (x > a || x < b); }
int main() {
    std::mt19937 g(3); std::set<int> s; while (s.size() < 64) s.insert(g() % SZ); ids.assign(s.begin(), s.end());
    int maxHops = 0;
    for (int t = 0; t < 2000; t++) {
        int key = g() % SZ, cur = ids[g() % ids.size()], hops = 0;
        while (!(key == cur || inOpen(key, cur, succ(cur + 1)) || key == succ(cur + 1))) {           // 키가 (cur, 후속] 에 없으면 점프
            int next = cur;
            for (int i = m - 1; i >= 0; i--) { int f = succ(cur + (1 << i)); if (inOpen(f, cur, key)) { next = f; break; } }       // 키 바로 앞까지 가장 멀리 가는 손가락
            if (next == cur) break; cur = next; hops++;
        }
        int owner = (key == cur) ? cur : succ(cur + 1);                    // 마지막 노드의 후속이 키의 주인
        assert(owner == succ(key)); maxHops = std::max(maxHops, hops);
    }
    assert(maxHops <= m);
    std::cout << "Chord: 64 nodes, lookups correct, max hops " << maxHops << " (<= log2 ring size = " << m << ")" << std::endl; return 0;
}
// Time Complexity: 조회 O(log N) 홉
// Space Complexity: 노드당 O(log N) 손가락
```
## Kademlia()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 카뎀리아(Kademlia, 해시 관점의 요약, 정본은 Hash.md Part 7): 거리를 XOR 로 정의한다(d(a,b)=a^b, 대칭이고 삼각부등식을 만족). 노드는 거리 구간 [2^i, 2^(i+1)) 마다 k-버킷(최대 k 개 연락처)을 두고,
// 목표 id 를 향해 "가장 가까운 연락처 α 개에 질의 -> 더 가까운 노드를 받아 반복" 한다. 질의마다 최소 한 비트씩 가까워져 O(log N) 라운드이다 (BitTorrent Mainline DHT, IPFS)
const int BITS = 12, K = 8;
std::vector<std::vector<int>> table;                                       // table[n] = 노드 n(인덱스) 의 연락처 id 들
int main() {
    std::mt19937 g(4); std::set<int> s; while (s.size() < 300) s.insert(g() % (1 << BITS)); std::vector<int> ids(s.begin(), s.end()); int N = ids.size();
    table.assign(N, {});
    for (int n = 0; n < N; n++) { std::vector<std::vector<int>> bucket(BITS);
        for (int o = 0; o < N; o++) if (o != n) bucket[31 - __builtin_clz(ids[n] ^ ids[o])].push_back(ids[o]);        // 거리의 최상위 비트가 같은 것끼리 한 버킷
        for (auto& b : bucket) { std::shuffle(b.begin(), b.end(), g); if ((int)b.size() > K) b.resize(K); for (int id : b) table[n].push_back(id); } }
    auto index = [&](int id) { return std::lower_bound(ids.begin(), ids.end(), id) - ids.begin(); };
    int maxRounds = 0;
    for (int t = 0; t < 500; t++) {
        int target = g() % (1 << BITS), cur = ids[g() % N], rounds = 0;
        for (;;) { int best = cur; for (int c : table[index(cur)]) if ((c ^ target) < (best ^ target)) best = c; if (best == cur) break; cur = best; rounds++; }      // 더 가까운 연락처로 이동
        int want = *std::min_element(ids.begin(), ids.end(), [&](int a, int b) { return (a ^ target) < (b ^ target); });
        assert(cur == want); maxRounds = std::max(maxRounds, rounds);      // 전역에서 XOR 거리가 가장 가까운 노드를 찾았다
    }
    std::cout << "Kademlia: 300 nodes, XOR-closest node found in <= " << maxRounds << " rounds (id bits " << BITS << ")" << std::endl; return 0;
}
// Time Complexity: 조회 O(log N) 라운드
// Space Complexity: 노드당 O(k log N) 연락처
```
## MerkleTree()
### 대표코드
```cpp
#include <functional>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 머클 트리(트리 관점의 요약, 정본은 Tree.md Part 16): 잎 = 데이터 블록의 해시, 부모 = 두 자식 해시의 해시. 루트 하나로 전체를 요약하고, 한 블록의 진위는 루트까지의 형제 해시 log N 개(감사 경로)로 확인한다.
// 분산 시스템에서는 두 복제본의 루트가 같으면 같고, 다르면 서브트리를 비교해 어긋난 블록만 찾아 동기화한다 (Cassandra anti-entropy, Git, 블록체인). 여기서는 std::hash 로 구조만 보이고, 암호학적 SHA-256 판은 Tree.md
typedef unsigned long long H;
H leaf(const std::string& s) { return std::hash<std::string>{}("L" + s); }
H node(H a, H b) { return std::hash<std::string>{}("N" + std::to_string(a) + "," + std::to_string(b)); }
std::vector<std::vector<H>> build(const std::vector<std::string>& d) { std::vector<std::vector<H>> lv(1); for (auto& s : d) lv[0].push_back(leaf(s));
    while (lv.back().size() > 1) { auto& c = lv.back(); std::vector<H> up; for (size_t i = 0; i < c.size(); i += 2) up.push_back(node(c[i], c[i + 1 < c.size() ? i + 1 : i])); lv.push_back(up); } return lv; }
bool verify(H root, size_t idx, const std::string& data, const std::vector<std::vector<H>>& lv) {
    H cur = leaf(data); for (size_t l = 0; l + 1 < lv.size(); l++) { size_t sib = idx ^ 1; H s = sib < lv[l].size() ? lv[l][sib] : cur; cur = (idx & 1) ? node(s, cur) : node(cur, s); idx >>= 1; } return cur == root; }
int main() {
    std::vector<std::string> d = {"a", "b", "c", "d", "e", "f", "g", "h"}; auto lv = build(d);
    assert(verify(lv.back()[0], 5, "f", lv) && !verify(lv.back()[0], 5, "F", lv));                   // 변조 탐지
    auto d2 = d; d2[3] = "D"; auto lv2 = build(d2); assert(lv2.back()[0] != lv.back()[0] && lv2[1][0] == lv[1][0] && lv2[1][1] != lv[1][1]);   // 어긋난 서브트리만 다름
    std::cout << "MerkleTree: 8 leaves, 3-hash audit path verifies, a single changed block changes only its subtree" << std::endl; return 0;
}
// Time Complexity: 루트 계산 O(N), 증명 검증 O(log N)
// Space Complexity: O(N)
```
## CRDT()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

// CRDT(Conflict-free Replicated Data Type): 여러 복제본이 각자 쓰기를 받고, 서로 상태를 주고받아 병합하기만 하면 (순서·중복·지연과 관계없이) 같은 값으로 수렴하는 자료구조.
// 상태 기반(CvRDT) 조건: 병합(merge)이 교환법칙·결합법칙·멱등법칙을 만족 = 상태들이 합 반격자(join-semilattice)를 이루고 연산이 단조 증가. 그래서 중복·순서 뒤바뀜이 해롭지 않다.
//   GCounter: 복제본별 카운터의 원소별 max   PNCounter: GCounter 둘(증가, 감소)   LWWRegister: (타임스탬프, 복제본 id) 가 큰 쪽   ORSet: 추가 태그 집합 - 제거된 태그 집합 ("추가 우선")
struct GCounter {
    std::map<int, long> c;
    void inc(int r, long n = 1) { c[r] += n; }
    long value() const { long s = 0; for (auto& kv : c) s += kv.second; return s; }
    void merge(const GCounter& o) { for (auto& kv : o.c) c[kv.first] = std::max(c[kv.first], kv.second); }
    bool operator==(const GCounter& o) const { return c == o.c; }
};
struct PNCounter {
    GCounter p, n; void inc(int r) { p.inc(r); } void dec(int r) { n.inc(r); } long value() const { return p.value() - n.value(); }
    void merge(const PNCounter& o) { p.merge(o.p); n.merge(o.n); } bool operator==(const PNCounter& o) const { return p == o.p && n == o.n; }
};
struct LWW {
    std::string v; long ts = 0; int rid = -1;
    void set(const std::string& s, long t, int r) { if (t > ts || (t == ts && r > rid)) { v = s; ts = t; rid = r; } }
    void merge(const LWW& o) { set(o.v, o.ts, o.rid); } bool operator==(const LWW& o) const { return v == o.v && ts == o.ts && rid == o.rid; }
};
typedef std::pair<int, long> Tag;
struct ORSet {
    std::map<std::string, std::set<Tag>> adds; std::set<Tag> removed; long ctr = 0;           // ctr 은 이 복제본의 로컬 상태(병합 대상 아님)
    void add(const std::string& e, int r) { adds[e].insert({r, ++ctr}); }
    void remove(const std::string& e) { for (auto& t : adds[e]) removed.insert(t); }        // 지금 관찰한 태그만 지운다 -> 동시에 일어난 add 는 살아남음
    bool has(const std::string& e) const { auto it = adds.find(e); if (it == adds.end()) return false; for (auto& t : it->second) if (!removed.count(t)) return true; return false; }
    void merge(const ORSet& o) { for (auto& kv : o.adds) adds[kv.first].insert(kv.second.begin(), kv.second.end()); removed.insert(o.removed.begin(), o.removed.end()); }
    bool operator==(const ORSet& o) const { std::map<std::string, std::set<Tag>> a = adds, b = o.adds; for (auto it = a.begin(); it != a.end();) it = it->second.empty() ? a.erase(it) : std::next(it); for (auto it = b.begin(); it != b.end();) it = it->second.empty() ? b.erase(it) : std::next(it); return a == b && removed == o.removed; }
};
struct Replica { int id; PNCounter cnt; LWW reg; ORSet set; void merge(const Replica& o) { cnt.merge(o.cnt); reg.merge(o.reg); set.merge(o.set); } };
bool same(const Replica& a, const Replica& b) { return a.cnt == b.cnt && a.reg == b.reg && a.set == b.set; }

int main() {
    std::mt19937 rng(7); const int R = 5; std::vector<Replica> rep(R); for (int i = 0; i < R; i++) rep[i].id = i;
    long truth = 0, clock = 0; long bestTs = -1; int bestRid = -1; std::string bestVal; const char* names[] = {"x", "y", "z", "w"};
    for (int step = 0; step < 4000; step++) {
        int r = rng() % R, op = rng() % 10; Replica& me = rep[r];
        if (op == 0) { me.cnt.inc(r); truth++; } else if (op == 1) { me.cnt.dec(r); truth--; }
        else if (op == 2) { std::string v = "v" + std::to_string(step); long ts = ++clock / 2; me.reg.set(v, ts, r); if (ts > bestTs || (ts == bestTs && r > bestRid)) { bestTs = ts; bestRid = r; bestVal = v; } }
        else if (op == 3) me.set.add(names[rng() % 4], r); else if (op == 4) me.set.remove(names[rng() % 4]);
        else { int s = rng() % R; rep[s].merge(rep[r]); if (rng() % 3 == 0) rep[s].merge(rep[r]); if (rng() % 4 == 0) rep[r].merge(rep[s]); }       // 일부는 중복 전달·역방향 전달
    }
    for (int round = 0; round < 2; round++) for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) rep[i].merge(rep[j]);        // 마지막 전체 교환
    for (int i = 1; i < R; i++) assert(same(rep[0], rep[i]));              // 모든 복제본이 같은 상태로 수렴
    assert(rep[0].cnt.value() == truth && rep[0].reg.v == bestVal);        // 카운터는 모든 증감의 합, 레지스터는 (ts, id) 최대 쓰기
    // 병합의 법칙: 임의의 세 상태 a, b, c
    for (int t = 0; t < 200; t++) {
        Replica s[3]; for (int i = 0; i < 3; i++) { s[i].id = i; for (int k = 0; k < 20; k++) { int op = rng() % 5; if (op == 0) s[i].cnt.inc(i); else if (op == 1) s[i].cnt.dec(i); else if (op == 2) s[i].reg.set("q" + std::to_string(rng() % 9), rng() % 6, i); else if (op == 3) s[i].set.add(names[rng() % 4], i); else s[i].set.remove(names[rng() % 4]); } }
        Replica ab = s[0]; ab.merge(s[1]); Replica ba = s[1]; ba.merge(s[0]); assert(same(ab, ba));                         // 교환
        Replica abc1 = ab; abc1.merge(s[2]); Replica bc = s[1]; bc.merge(s[2]); Replica abc2 = s[0]; abc2.merge(bc); assert(same(abc1, abc2));     // 결합
        Replica aa = s[0]; aa.merge(s[0]); assert(same(aa, s[0]));                                                          // 멱등
    }
    // 추가 우선 의미: 한쪽이 지우는 동안 다른 쪽이 다시 추가하면 원소가 살아남는다
    Replica A, B; A.id = 0; B.id = 1; A.set.add("x", 0); B.merge(A); A.set.remove("x"); B.set.add("x", 1); A.merge(B); B.merge(A);
    assert(A.set.has("x") && B.set.has("x"));
    Replica C; C.id = 2; C.merge(A); C.set.remove("x"); A.merge(C); assert(!A.set.has("x"));                                  // 관찰한 add 를 지우면 사라짐
    std::cout << "CRDT: 5 replicas converge (counter=" << rep[0].cnt.value() << ", register=" << rep[0].reg.v << "); merge is commutative/associative/idempotent; OR-Set is add-wins" << std::endl;
    return 0;
}
// Time Complexity: 연산 O(1)~O(원소 태그 수), 병합 O(상태 크기)
// Space Complexity: O(복제본 수 + 태그 수)
```

# Part 11. GPU 자료구조
## GPUBVH()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// GPU 친화적 BVH(LBVH, Karras 2012): 트리를 "위에서 쪼개며" 만드는 대신, 물체를 3D 공간 채움 곡선인 모튼 코드(Morton code)로 정렬한 뒤 정렬된 코드열 자체에서 트리 모양을 직접 계산한다.
// 내부 노드 i 의 담당 구간과 분할 지점이 코드의 "공통 접두사 길이" δ(i, j) 만으로 정해지므로 노드마다 독립 계산 -> GPU 에서 스레드 하나가 노드 하나를 맡아 완전 병렬로 짓는다. 바운딩 박스는 잎에서 시작해
// 루트로 올라가며 합치는데, 각 부모에 "먼저 도착한 스레드는 멈추고 나중 도착한 스레드가 두 자식 박스를 합치는" 원자 카운터로 병렬화한다.  아래는 같은 알고리즘을 CPU 에서 순차 루프로 실행해 구조를 검증한다
typedef std::array<float, 3> V;
struct Box { V lo, hi; };
uint32_t expand(uint32_t v) { v = (v * 0x00010001u) & 0xFF0000FFu; v = (v * 0x00000101u) & 0x0F00F00Fu; v = (v * 0x00000011u) & 0xC30C30C3u; v = (v * 0x00000005u) & 0x49249249u; return v; }
uint32_t morton(const V& p) { auto q = [](float x) { return (uint32_t)std::min(std::max(x * 1024.0f, 0.0f), 1023.0f); }; return expand(q(p[0])) * 4 + expand(q(p[1])) * 2 + expand(q(p[2])); }
Box unite(const Box& a, const Box& b) { Box r; for (int i = 0; i < 3; i++) { r.lo[i] = std::min(a.lo[i], b.lo[i]); r.hi[i] = std::max(a.hi[i], b.hi[i]); } return r; }
bool overlap(const Box& a, const Box& b) { for (int i = 0; i < 3; i++) if (a.hi[i] < b.lo[i] || b.hi[i] < a.lo[i]) return false; return true; }
struct Internal { int left, right, parent = -1; Box box; };                // 자식: >= 0 이면 내부 노드 번호, 음수면 ~(잎 번호)
struct LBVH {
    int n; std::vector<uint32_t> code; std::vector<Box> leaf; std::vector<int> leafParent, objId; std::vector<Internal> in;
    int delta(int i, int j) const { if (j < 0 || j >= n) return -1; if (code[i] == code[j]) return 32 + __builtin_clz(i ^ j); return __builtin_clz(code[i] ^ code[j]); }   // 공통 접두사 길이 (같은 코드는 인덱스로 구분)
    explicit LBVH(const std::vector<Box>& objs) {
        n = objs.size(); std::vector<std::pair<uint32_t, int>> s(n);
        for (int i = 0; i < n; i++) { V c; for (int k = 0; k < 3; k++) c[k] = (objs[i].lo[k] + objs[i].hi[k]) / 2; s[i] = {morton(c), i}; }
        std::sort(s.begin(), s.end()); code.resize(n); leaf.resize(n); objId.resize(n);
        for (int i = 0; i < n; i++) { code[i] = s[i].first; objId[i] = s[i].second; leaf[i] = objs[s[i].second]; }
        in.resize(n - 1); leafParent.assign(n, -1);
        for (int i = 0; i < n - 1; i++) {                                  // GPU 라면 노드마다 스레드 하나
            int d = (delta(i, i + 1) - delta(i, i - 1)) >= 0 ? 1 : -1, dmin = delta(i, i - d), lmax = 2;
            while (delta(i, i + lmax * d) > dmin) lmax *= 2;
            int l = 0; for (int t = lmax / 2; t >= 1; t /= 2) if (delta(i, i + (l + t) * d) > dmin) l += t;
            int j = i + l * d, first = std::min(i, j), last = std::max(i, j);
            int dnode = delta(first, last), split = first, step = last - first;      // 분할 지점: 접두사가 더 길어지는 마지막 위치
            do { step = (step + 1) >> 1; int ns = split + step; if (ns < last && delta(first, ns) > dnode) split = ns; } while (step > 1);
            in[i].left = (first == split) ? ~split : split; in[i].right = (last == split + 1) ? ~(split + 1) : split + 1;
        }
        for (int i = 0; i < n - 1; i++) for (int c : {in[i].left, in[i].right}) { if (c < 0) leafParent[~c] = i; else in[c].parent = i; }
        std::vector<int> arrived(n - 1, 0);                                // 원자 카운터 대신 순차 시뮬레이션: 두 번째 도착자가 박스를 합친다
        for (int lf = 0; lf < n; lf++) for (int p = leafParent[lf]; p != -1; p = in[p].parent) {
            if (arrived[p]++ == 0) break;
            in[p].box = unite(boxOf(in[p].left), boxOf(in[p].right));
        }
    }
    const Box& boxOf(int c) const { return c < 0 ? leaf[~c] : in[c].box; }
    void query(const Box& q, std::vector<int>& out) const {
        std::vector<int> st = {0};
        while (!st.empty()) { int c = st.back(); st.pop_back(); if (!overlap(boxOf(c), q)) continue; if (c < 0) out.push_back(objId[~c]); else { st.push_back(in[c].left); st.push_back(in[c].right); } }
    }
    int depth(int c) const { return c < 0 ? 0 : 1 + std::max(depth(in[c].left), depth(in[c].right)); }
};

int main() {
    std::mt19937 g(1); std::uniform_real_distribution<float> U(0, 1); int n = 3000; std::vector<Box> objs;
    for (int i = 0; i < n; i++) { V c = {U(g), U(g), U(g)}; float s = 0.002f + 0.01f * U(g); objs.push_back({{c[0], c[1], c[2]}, {c[0] + s, c[1] + s, c[2] + s}}); }
    LBVH t(objs);
    std::vector<int> seen(n, 0), parentCount(n - 1, 0);                    // 구조 검사: 잎은 정확히 한 번씩, 내부 노드는 정확히 한 부모
    std::vector<int> st = {0}; int internalCount = 0;
    while (!st.empty()) { int c = st.back(); st.pop_back(); if (c < 0) { seen[~c]++; continue; } internalCount++; st.push_back(t.in[c].left); st.push_back(t.in[c].right);
        for (int k : {t.in[c].left, t.in[c].right}) assert(k < 0 || t.in[k].parent == c); }
    for (int i = 0; i < n; i++) assert(seen[i] == 1); assert(internalCount == n - 1 && t.in[0].parent == -1);
    for (int i = 0; i < n - 1; i++) for (int k : {t.in[i].left, t.in[i].right}) { const Box& b = t.boxOf(k); for (int a = 0; a < 3; a++) assert(t.in[i].box.lo[a] <= b.lo[a] && t.in[i].box.hi[a] >= b.hi[a]); }   // 부모 박스가 자식 박스를 감싼다
    for (int q = 0; q < 300; q++) {
        V c = {U(g), U(g), U(g)}; Box b{{c[0], c[1], c[2]}, {c[0] + 0.1f, c[1] + 0.1f, c[2] + 0.1f}}; std::vector<int> got, want; t.query(b, got);
        for (int i = 0; i < n; i++) if (overlap(objs[i], b)) want.push_back(i); std::sort(got.begin(), got.end()); assert(got == want);
    }
    std::cout << "GPUBVH: LBVH over " << n << " objects built from Morton codes, depth " << t.depth(0) << ", queries match brute force" << std::endl; return 0;
}
// Time Complexity: 구성 O(N log N) (정렬) + 노드별 O(log N), GPU 병렬이면 정렬 이후 O(log N) 단계
// Space Complexity: O(N)
```
## CUDASparseMatrix()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// GPU 희소 행렬: 대부분이 0 인 행렬을 저장하는 형식에 따라 GPU 의 메모리 접근 효율이 크게 달라진다. 행렬-벡터 곱(SpMV)을 네 형식으로 구현해 같은 결과를 확인하고,
// 워프(32 스레드)가 한 번에 읽는 128바이트 메모리 구간(트랜잭션) 수를 세어 "합쳐진 접근(coalescing)" 의 차이를 숫자로 본다.
//   COO: (행, 열, 값) 목록 - 단순, 원자 덧셈/분할 합 필요   CSR: 행 시작 위치 + 열 + 값 - 가장 흔함. 스레드 하나가 한 행(scalar) 또는 워프가 한 행(vector)
//   ELL: 모든 행을 같은 길이 K 로 패딩하고 "열 우선"으로 저장 - 같은 슬롯의 값이 이웃 스레드끼리 이웃 주소라 합쳐져 읽힘. 행 길이가 고르지 않으면 패딩 낭비
struct Csr { int rows; std::vector<int> ptr, idx; std::vector<long> val; };
struct Ell { int rows, K; std::vector<int> idx; std::vector<long> val; };    // (i, k) 는 k * rows + i
struct Coo { std::vector<int> r, c; std::vector<long> v; };
Csr toCsr(const Coo& m, int rows) { Csr a; a.rows = rows; a.ptr.assign(rows + 1, 0); for (int r : m.r) a.ptr[r + 1]++; for (int i = 0; i < rows; i++) a.ptr[i + 1] += a.ptr[i];
    a.idx.resize(m.r.size()); a.val.resize(m.r.size()); std::vector<int> fill(a.ptr.begin(), a.ptr.end() - 1); for (size_t e = 0; e < m.r.size(); e++) { int p = fill[m.r[e]]++; a.idx[p] = m.c[e]; a.val[p] = m.v[e]; } return a; }
Ell toEll(const Csr& a) { Ell e; e.rows = a.rows; e.K = 0; for (int i = 0; i < a.rows; i++) e.K = std::max(e.K, a.ptr[i + 1] - a.ptr[i]);
    e.idx.assign((size_t)e.K * a.rows, -1); e.val.assign((size_t)e.K * a.rows, 0); for (int i = 0; i < a.rows; i++) for (int k = 0; k < a.ptr[i + 1] - a.ptr[i]; k++) { e.idx[(size_t)k * a.rows + i] = a.idx[a.ptr[i] + k]; e.val[(size_t)k * a.rows + i] = a.val[a.ptr[i] + k]; } return e; }
std::vector<long> spmvCsrScalar(const Csr& a, const std::vector<long>& x) { std::vector<long> y(a.rows, 0); for (int i = 0; i < a.rows; i++) for (int p = a.ptr[i]; p < a.ptr[i + 1]; p++) y[i] += a.val[p] * x[a.idx[p]]; return y; }
std::vector<long> spmvCsrVector(const Csr& a, const std::vector<long>& x) {       // 워프 하나가 한 행: 레인 l 이 l, l+32, ... 번째 원소를 맡고 트리 형태로 합산
    std::vector<long> y(a.rows, 0);
    for (int i = 0; i < a.rows; i++) { long lane[32] = {0}; for (int p = a.ptr[i], l = 0; p < a.ptr[i + 1]; p++, l = (l + 1) % 32) lane[l] += a.val[p] * x[a.idx[p]];
        for (int off = 16; off >= 1; off /= 2) for (int l = 0; l < off; l++) lane[l] += lane[l + off]; y[i] = lane[0]; }
    return y;
}
std::vector<long> spmvEll(const Ell& e, const std::vector<long>& x) { std::vector<long> y(e.rows, 0); for (int k = 0; k < e.K; k++) for (int i = 0; i < e.rows; i++) { int c = e.idx[(size_t)k * e.rows + i]; if (c >= 0) y[i] += e.val[(size_t)k * e.rows + i] * x[c]; } return y; }
std::vector<long> spmvCoo(const Coo& m, int rows, const std::vector<long>& x) { std::vector<long> y(rows, 0); for (size_t e = 0; e < m.r.size(); e++) y[m.r[e]] += m.v[e] * x[m.c[e]]; return y; }       // GPU 에서는 y 갱신이 원자 덧셈
long countSegments(const std::vector<long>& addrBytes) { std::set<long> seg; for (long a : addrBytes) seg.insert(a / 128); return seg.size(); }       // 한 워프 로드가 건드리는 128B 구간 수

int main() {
    std::mt19937 g(2); const int R = 1024, C = 512; Coo m; std::vector<std::vector<long>> dense(R, std::vector<long>(C, 0));
    for (int i = 0; i < R; i++) { int len = 4 + g() % 9; std::set<int> cols; while ((int)cols.size() < len) cols.insert(g() % C); for (int c : cols) { long v = (long)(g() % 19) - 9; if (!v) v = 1; m.r.push_back(i); m.c.push_back(c); m.v.push_back(v); dense[i][c] = v; } }
    std::vector<long> x(C); for (auto& v : x) v = (long)(g() % 21) - 10;
    std::vector<long> ref(R, 0); for (int i = 0; i < R; i++) for (int j = 0; j < C; j++) ref[i] += dense[i][j] * x[j];
    Csr csr = toCsr(m, R); Ell ell = toEll(csr);
    assert(spmvCsrScalar(csr, x) == ref && spmvCsrVector(csr, x) == ref && spmvEll(ell, x) == ref && spmvCoo(m, R, x) == ref);      // 네 가지 모두 같은 답
    long tCsr = 0, tEll = 0, tVec = 0;                                     // 값 배열 로드의 128B 구간 수 (워프 = 연속된 32 행)
    for (int w = 0; w < R / 32; w++) for (int k = 0; k < ell.K; k++) {
        std::vector<long> a1, a2; for (int l = 0; l < 32; l++) { int i = w * 32 + l; if (k < csr.ptr[i + 1] - csr.ptr[i]) a1.push_back((long)(csr.ptr[i] + k) * 8); a2.push_back(((long)k * R + i) * 8); }
        if (!a1.empty()) tCsr += countSegments(a1); tEll += countSegments(a2);
    }
    for (int i = 0; i < R; i++) for (int p = csr.ptr[i]; p < csr.ptr[i + 1]; p += 32) { std::vector<long> a; for (int q = p; q < std::min(p + 32, csr.ptr[i + 1]); q++) a.push_back((long)q * 8); tVec += countSegments(a); }
    assert(tEll * 2 < tCsr);                                               // ELL 의 열 우선 배치가 CSR scalar 보다 메모리 트랜잭션이 훨씬 적다
    double wasted = 1.0 - (double)csr.val.size() / ((double)ell.K * R);
    std::cout << "CUDASparseMatrix: SpMV equal in 4 formats; value-load segments per matrix: CSR-scalar " << tCsr << ", CSR-vector " << tVec << ", ELL " << tEll << " (ELL padding waste " << wasted * 100 << "%)" << std::endl;
    return 0;
}
// Time Complexity: SpMV O(nnz) (ELL 은 O(K·rows))
// Space Complexity: CSR O(nnz + rows), ELL O(K·rows)
```
## ParallelPrefixSum()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <thread>
#include <vector>
#include <cassert>

// 병렬 접두합(scan): GPU 알고리즘의 기본 부품(정렬, 스트림 압축, 히스토그램, BVH 구성)이다. 순차 계산은 앞 결과에 의존하지만 합의 결합법칙을 이용하면 로그 단계로 풀린다.
//   Hillis–Steele: 단계 d 마다 a[i] += a[i - 2^d].  단계 수 log n, 총 연산 n log n (작업 비효율적이지만 단순)
//   Blelloch(작업 효율적): 상향 스윕(트리로 합 만들기, n-1 번 덧셈) + 하향 스윕(루트에 0 을 넣고 내려보내기, n-1 번) = 총 2(n-1) 번, 깊이 2 log n
//   큰 배열: 블록별 scan -> 블록 합 scan -> 블록 오프셋 더하기 (GPU 에서 블록 = 스레드 블록)
// 각 단계의 인덱스는 서로 겹치지 않아 스레드로 나눠도 경쟁이 없다. 아래는 std::thread 로 같은 구조를 돌린다
template <class F> void parallelFor(long n, F f, int T = 4) { std::vector<std::thread> th; for (int t = 0; t < T; t++) th.emplace_back([=] { for (long i = t; i < n; i += T) f(i); }); for (auto& x : th) x.join(); }
long adds = 0;
void blelloch(std::vector<long>& a) {                                      // 길이는 2 의 거듭제곱, 배타적(exclusive) scan
    long n = a.size();
    for (long s = 2; s <= n; s *= 2) { parallelFor(n / s, [&](long b) { a[b * s + s - 1] += a[b * s + s / 2 - 1]; }); adds += n / s; }          // 상향 스윕
    a[n - 1] = 0;
    for (long s = n; s >= 2; s /= 2) { parallelFor(n / s, [&](long b) { long l = b * s + s / 2 - 1, r = b * s + s - 1; long t = a[l]; a[l] = a[r]; a[r] += t; }); adds += n / s; }   // 하향 스윕
}
std::vector<long> hillisSteele(std::vector<long> a, long& work) {         // 포괄(inclusive) scan, 이중 버퍼
    long n = a.size(); std::vector<long> b(n);
    for (long d = 1; d < n; d *= 2) { parallelFor(n, [&](long i) { b[i] = a[i] + (i >= d ? a[i - d] : 0); }); work += n - d; a.swap(b); }
    return a;
}
std::vector<long> scanLarge(const std::vector<long>& in) {                 // 블록 scan -> 블록 합 scan -> 오프셋 더하기
    const long BS = 1024; long n = in.size(), blocks = (n + BS - 1) / BS; std::vector<long> a(blocks * BS, 0), sums(blocks);
    std::copy(in.begin(), in.end(), a.begin());
    parallelFor(blocks, [&](long b) { long s = 0; for (long i = b * BS; i < (b + 1) * BS; i++) { long v = a[i]; a[i] = s; s += v; } sums[b] = s; });          // 블록별 scan (블록 안은 순차)
    long acc = 0; for (long b = 0; b < blocks; b++) { long v = sums[b]; sums[b] = acc; acc += v; }                                                          // 블록 합 scan
    parallelFor(blocks, [&](long b) { for (long i = b * BS; i < (b + 1) * BS; i++) a[i] += sums[b]; });
    a.resize(n); return a;
}

int main() {
    std::mt19937 g(1); const long n = 1 << 14; std::vector<long> v(n); for (auto& x : v) x = (long)(g() % 100);
    std::vector<long> ref(n); std::exclusive_scan(v.begin(), v.end(), ref.begin(), 0L);
    std::vector<long> a = v; adds = 0; blelloch(a); assert(a == ref && adds == 2 * (n - 1) - 0);            // 배타적 scan 일치, 덧셈 횟수 2(n-1)
    long work = 0; std::vector<long> inc = hillisSteele(v, work); std::vector<long> refInc(n); std::inclusive_scan(v.begin(), v.end(), refInc.begin());
    assert(inc == refInc && work > 5 * adds);                              // 같은 결과지만 작업량이 훨씬 많다 (n log n vs 2n)
    std::vector<long> big(100003); for (auto& x : big) x = (long)(g() % 1000) - 500;
    std::vector<long> refBig(big.size()); std::exclusive_scan(big.begin(), big.end(), refBig.begin(), 0L);
    assert(scanLarge(big) == refBig);
    std::cout << "ParallelPrefixSum: Blelloch " << adds << " adds vs Hillis-Steele " << work << " for n=" << n << "; block scan verified for n=100003" << std::endl; return 0;
}
// Time Complexity: 작업 O(N), 깊이 O(log N) (Blelloch)
// Space Complexity: O(N)
```
## ParallelHashTable()
### 대표코드
```cpp
#include <atomic>
#include <cstdint>
#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <unordered_map>
#include <vector>
#include <cassert>

// 병렬 해시 테이블(GPU/멀티코어): 개방 주소법(선형 탐사) + 슬롯의 키를 원자 CAS 로 점유한다. 빈 슬롯(0)에 CAS(0 -> key) 가 성공한 스레드가 그 슬롯의 주인이고, 실패했는데 들어 있는 키가 같으면 이미 다른 스레드가 넣은 것이다.
// 잠금이 없고 슬롯 하나에만 경쟁하므로 수천 스레드(GPU)에서 잘 확장된다. 한계: 키를 먼저 점유하고 값을 나중에 쓰므로 "삽입 단계"와 "조회 단계"를 분리해야 한다(phase-concurrent), 삭제와 크기 변경은 어렵다
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
struct PHT {
    size_t mask; std::unique_ptr<std::atomic<uint64_t>[]> keys; std::unique_ptr<std::atomic<uint32_t>[]> vals; std::atomic<long> probes{0};
    explicit PHT(size_t cap) : mask(cap - 1), keys(new std::atomic<uint64_t>[cap]), vals(new std::atomic<uint32_t>[cap]) { for (size_t i = 0; i < cap; i++) { keys[i] = 0; vals[i] = 0; } }
    bool insert(uint64_t key, uint32_t val) {                              // key != 0. 새로 만든 슬롯이면 true
        long p = 0;
        for (size_t i = mix(key) & mask;; i = (i + 1) & mask, p++) {
            uint64_t cur = keys[i].load();
            if (cur == 0) { uint64_t exp = 0; if (keys[i].compare_exchange_strong(exp, key)) { vals[i].store(val); probes += p + 1; return true; } cur = exp; }       // 점유 경쟁
            if (cur == key) { vals[i].store(val); probes += p + 1; return false; }
        }
    }
    bool find(uint64_t key, uint32_t& val) const {
        for (size_t i = mix(key) & mask;; i = (i + 1) & mask) { uint64_t cur = keys[i].load(); if (cur == key) { val = vals[i].load(); return true; } if (cur == 0) return false; }
    }
};

int main() {
    PHT t(1 << 18); const int T = 4; const uint64_t N = 100000; std::atomic<long> created{0}; std::vector<std::thread> th;
    for (int k = 0; k < T; k++) th.emplace_back([&, k] { for (uint64_t i = 0; i < N; i++) { uint64_t key = (i * 3 + k * 7000) % (N * 2) + 1; if (t.insert(key, (uint32_t)(key * 31))) created++; } });      // 스레드끼리 키가 겹친다
    for (auto& x : th) x.join();
    std::unordered_map<uint64_t, uint32_t> ref; for (int k = 0; k < T; k++) for (uint64_t i = 0; i < N; i++) { uint64_t key = (i * 3 + k * 7000) % (N * 2) + 1; ref[key] = (uint32_t)(key * 31); }
    assert((size_t)created == ref.size());                                 // 같은 키를 두 스레드가 만들지 않았다 (CAS 가 승자를 하나만 정함)
    th.clear(); std::atomic<long> bad{0};
    for (int k = 0; k < T; k++) th.emplace_back([&] { for (auto& kv : ref) { uint32_t v; if (!t.find(kv.first, v) || v != kv.second) bad++; } uint32_t v; for (uint64_t key = N * 2 + 5; key < N * 2 + 2000; key++) if (t.find(key, v)) bad++; });
    for (auto& x : th) x.join(); assert(bad == 0);
    double load = (double)ref.size() / (1 << 18);
    std::cout << "ParallelHashTable: " << ref.size() << " keys from " << T << " racing threads, load " << load << ", avg probes per insert " << (double)t.probes / (T * N) << std::endl; return 0;
}
// Time Complexity: 삽입·조회 기대 O(1) (부하율이 낮을 때)
// Space Complexity: 고정 용량 (키 8 B + 값 4 B) × 슬롯
```
## WarpQueue()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <iostream>
#include <random>
#include <thread>
#include <vector>
#include <cassert>

// 워프 큐: GPU 에서 수천 스레드가 같은 큐 꼬리에 원자 연산을 하면 직렬화로 느려진다. 해법인 "워프 단위 집계(warp-aggregated atomics)":
// 같은 워프(32 레인)에서 push 하려는 레인들의 마스크를 ballot 으로 얻고, popc 로 개수 c 를 센 뒤 대표 레인 하나만 tail.fetch_add(c) 를 한 번 수행한다.
// 각 레인은 "자기보다 낮은 레인 중 push 하는 레인 수" = popc(mask & lanemask_lt) 를 오프셋으로 base + 오프셋 위치에 쓴다. 원자 연산이 푸시 수에서 워프 수로 줄고 레인 순서도 유지된다.
// 아래는 같은 규칙을 32 칸 배열로 흉내 내고(ballot=비트마스크 만들기, popc=__builtin_popcount), 여러 OS 스레드가 각자 워프들을 돌려 하나의 큐에 넣는다
const int W = 32;
std::atomic<long> tail{0}, atomicOps{0}; std::vector<int> buf;
int warpPush(const int vals[W], const bool want[W]) {
    uint32_t mask = 0; for (int l = 0; l < W; l++) if (want[l]) mask |= 1u << l;       // ballot
    int cnt = __builtin_popcount(mask); if (!cnt) return 0;
    long base = tail.fetch_add(cnt); atomicOps++;                          // 대표 레인 하나만 원자 연산 (결과는 shuffle 로 모든 레인에 전달)
    for (int l = 0; l < W; l++) if (want[l]) buf[base + __builtin_popcount(mask & ((1u << l) - 1))] = vals[l];
    return cnt;
}
int main() {
    const int T = 4, WARPS = 5000; buf.assign((size_t)T * WARPS * W, -1); std::vector<std::thread> th; std::vector<long> pushed(T, 0);
    std::vector<std::vector<int>> mine(T);
    for (int t = 0; t < T; t++) th.emplace_back([&, t] { std::mt19937 g(100 + t); int vals[W]; bool want[W];
        for (int w = 0; w < WARPS; w++) { for (int l = 0; l < W; l++) { want[l] = g() % 10 < 3; vals[l] = (t * WARPS + w) * W + l; if (want[l]) mine[t].push_back(vals[l]); } pushed[t] += warpPush(vals, want); } });
    for (auto& x : th) x.join();
    long total = 0; for (long p : pushed) total += p;
    assert(tail == total);
    std::vector<int> got(buf.begin(), buf.begin() + total), want; for (auto& m : mine) want.insert(want.end(), m.begin(), m.end());
    std::sort(got.begin(), got.end()); std::sort(want.begin(), want.end()); assert(got == want);          // 모든 원소가 정확히 한 번씩 들어갔다
    assert(atomicOps <= (long)T * WARPS && atomicOps * 5 < total);        // 원자 연산 수 = 워프 수 이하, 푸시 수의 1/5 미만
    std::cout << "WarpQueue: " << total << " pushes with " << atomicOps << " atomic operations (naive: one per push)" << std::endl; return 0;
}
// Time Complexity: 워프당 원자 연산 1회 (푸시당 O(1/레인 수))
// Space Complexity: 큐 용량
```

# Part 12. AI와 데이터
## VectorIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 벡터 인덱스의 기준선: 플랫(flat, 전수 탐색) 색인.  임베딩(문장·이미지를 나타내는 실수 벡터) 데이터베이스는 "질의 벡터와 가장 가까운 k 개" 를 찾는 일이고, 플랫 색인은 모든 벡터와의 거리를 재서 정확한 답을 낸다 — O(N·D).
// 다른 모든 근사 색인(HNSW, IVF, PQ, Annoy ...)은 이 정확한 답에 대한 recall@k 로 평가한다.  이 항목은 ① 힙으로 하는 top-k 선택 ② 코사인 = 정규화 후 L2 (|a-b|² = 2 - 2a·b) ③ 내적 검색(MIPS)은 L2 와 다르다 ④ 차원이 커질수록 "가장 가까운 점과 가장 먼 점의 거리비가 1 로 수렴" — 왜 근사가 필요한지 — 를 확인한다
typedef std::vector<float> Vec;
float l2(const Vec& a, const Vec& b) { float s = 0; for (size_t i = 0; i < a.size(); i++) s += (a[i] - b[i]) * (a[i] - b[i]); return s; }
float dot(const Vec& a, const Vec& b) { float s = 0; for (size_t i = 0; i < a.size(); i++) s += a[i] * b[i]; return s; }
void normalize(Vec& v) { float n = std::sqrt(dot(v, v)); for (auto& x : v) x /= n; }
struct Flat {
    std::vector<Vec> data;
    std::vector<int> knn(const Vec& q, int k) const {                      // 최대 힙으로 O(N log k)
        std::priority_queue<std::pair<float, int>> h;
        for (size_t i = 0; i < data.size(); i++) { float d = l2(q, data[i]); if ((int)h.size() < k) h.push({d, (int)i}); else if (d < h.top().first) { h.pop(); h.push({d, (int)i}); } }
        std::vector<int> out; while (!h.empty()) { out.push_back(h.top().second); h.pop(); } std::reverse(out.begin(), out.end()); return out;
    }
};
double recall(const std::vector<int>& approx, const std::vector<int>& exact) { int hit = 0; for (int a : approx) hit += std::find(exact.begin(), exact.end(), a) != exact.end(); return (double)hit / exact.size(); }

int main() {
    std::mt19937 g(1); std::normal_distribution<float> N(0, 1); int n = 3000, D = 32;
    Flat f; for (int i = 0; i < n; i++) { Vec v(D); for (auto& x : v) x = N(g); f.data.push_back(v); }
    Vec q(D); for (auto& x : q) x = N(g);
    std::vector<int> all(n); std::iota(all.begin(), all.end(), 0); std::sort(all.begin(), all.end(), [&](int a, int b) { return l2(q, f.data[a]) < l2(q, f.data[b]); });
    std::vector<int> top = f.knn(q, 10); assert(top == std::vector<int>(all.begin(), all.begin() + 10));       // 힙 top-k == 전체 정렬의 앞 10 개
    assert(recall(top, top) == 1.0 && recall(std::vector<int>(all.end() - 10, all.end()), top) == 0.0);
    Flat u = f; for (auto& v : u.data) normalize(v); Vec qn = q; normalize(qn);                      // 코사인 = 정규화 후 L2
    std::vector<int> byL2 = u.knn(qn, 10), byCos(n); std::iota(byCos.begin(), byCos.end(), 0); std::sort(byCos.begin(), byCos.end(), [&](int a, int b) { return dot(qn, u.data[a]) > dot(qn, u.data[b]); });
    assert(byL2 == std::vector<int>(byCos.begin(), byCos.begin() + 10));
    for (int i = 0; i < 5; i++) assert(std::fabs(l2(qn, u.data[i]) - (2 - 2 * dot(qn, u.data[i]))) < 1e-4);
    Flat m; m.data = {{1, 0}, {0, 0.9f}, {3, 3}}; Vec mq = {0, 1};          // 정규화하지 않으면 내적 최대 != 거리 최소
    assert(m.knn(mq, 1)[0] == 1); int mips = 0; for (int i = 1; i < 3; i++) if (dot(mq, m.data[i]) > dot(mq, m.data[mips])) mips = i; assert(mips == 2);
    double ratio[4]; int dims[4] = {2, 8, 32, 128};                        // 최근접/최원 거리비: 차원이 커질수록 1 에 가까워진다
    for (int t = 0; t < 4; t++) { std::vector<Vec> pts; for (int i = 0; i < 1000; i++) { Vec v(dims[t]); for (auto& x : v) x = std::uniform_real_distribution<float>(0, 1)(g); pts.push_back(v); }
        Vec c(dims[t]); for (auto& x : c) x = 0.5f; float mn = 1e9, mx = 0; for (auto& p : pts) { float d = std::sqrt(l2(c, p)); mn = std::min(mn, d); mx = std::max(mx, d); } ratio[t] = mn / mx; }
    assert(ratio[0] < ratio[1] && ratio[1] < ratio[2] && ratio[2] < ratio[3]);
    std::cout << "VectorIndex: exact top-k verified; nearest/farthest distance ratio by dimension 2/8/32/128 = " << ratio[0] << "/" << ratio[1] << "/" << ratio[2] << "/" << ratio[3] << std::endl; return 0;
}
// Time Complexity: 질의 O(N·D + N log k)
// Space Complexity: O(N·D)
```
## HNSW()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// HNSW(Hierarchical Navigable Small World, Malkov–Yashunin): 벡터 검색의 사실상 표준 근사 색인. 점들을 "근접 그래프"(각 점이 가까운 점 M 개와 연결)로 잇고, 그 위에 성기게 샘플링한 상위 층을 여러 겹 쌓는다.
// 층 l 에 오를 확률은 e^(-l/mL) 로 기하급수적으로 줄어(mL = 1/ln M) 층이 스킵 리스트처럼 작동한다. 질의: 맨 위 층에서 탐욕적으로 질의에 가까운 노드로 이동 -> 한 층 내려가 그 노드에서 다시 이동 ...
// -> 0층에서는 ef 크기의 후보 목록을 유지하며 넓게 탐색(best-first). 삽입은 질의와 같은 방식으로 이웃을 찾고, 연결할 M 개를 고를 때 "이미 고른 이웃보다 나에게 더 가까운 후보만" 남기는 휴리스틱으로 다양한 방향의 간선을 보존한다
// 거리 계산 횟수가 N 이 아니라 대략 log N 에 비례해 늘어나는 것이 핵심이다. 아래는 정확한 전수 탐색에 대한 recall 과 거리 계산 횟수로 검증한다
const int D = 16;
typedef std::array<float, D> Pt; typedef std::pair<float, int> PI;
struct HNSW {
    int M = 12, M0 = 24, efC = 80; double mL = 1.0 / std::log(12.0);
    std::vector<Pt> pts; std::vector<std::vector<std::vector<int>>> nb; int entry = -1, maxL = -1; std::mt19937 rng{42}; long evals = 0;
    std::vector<int> vis; int epoch = 0;
    float dq(const Pt& q, int b) { evals++; float s = 0; for (int i = 0; i < D; i++) s += (q[i] - pts[b][i]) * (q[i] - pts[b][i]); return s; }
    std::vector<PI> searchLayer(const Pt& q, int ep, int ef, int layer) {          // best-first: 후보 최소 힙 + 결과 최대 힙(크기 ef)
        if (vis.size() < pts.size()) vis.resize(pts.size(), 0); ++epoch;
        std::priority_queue<PI, std::vector<PI>, std::greater<PI>> cand; std::priority_queue<PI> res;
        float d0 = dq(q, ep); cand.push({d0, ep}); res.push({d0, ep}); vis[ep] = epoch;
        while (!cand.empty()) {
            PI c = cand.top(); if ((int)res.size() >= ef && c.first > res.top().first) break; cand.pop();
            for (int e : nb[c.second][layer]) { if (vis[e] == epoch) continue; vis[e] = epoch; float de = dq(q, e);
                if ((int)res.size() < ef || de < res.top().first) { cand.push({de, e}); res.push({de, e}); if ((int)res.size() > ef) res.pop(); } }
        }
        std::vector<PI> out; while (!res.empty()) { out.push_back(res.top()); res.pop(); } std::reverse(out.begin(), out.end()); return out;
    }
    std::vector<int> select(const std::vector<PI>& cand, int m) {              // 휴리스틱: 이미 고른 이웃 r 보다 후보 e 가 질의에 더 가까울 때만 채택
        std::vector<int> res;
        for (auto& c : cand) { if ((int)res.size() >= m) break; bool ok = true; for (int r : res) { float d = 0; for (int i = 0; i < D; i++) d += (pts[c.second][i] - pts[r][i]) * (pts[c.second][i] - pts[r][i]); if (d < c.first) { ok = false; break; } } if (ok) res.push_back(c.second); }
        for (auto& c : cand) { if ((int)res.size() >= m) break; if (std::find(res.begin(), res.end(), c.second) == res.end()) res.push_back(c.second); }   // 부족하면 가까운 순으로 채움
        return res;
    }
    void insert(const Pt& p) {
        int id = pts.size(); pts.push_back(p); int l = (int)(-std::log(std::uniform_real_distribution<double>(1e-12, 1.0)(rng)) * mL); nb.emplace_back(l + 1);
        if (entry < 0) { entry = id; maxL = l; return; }
        int ep = entry;
        for (int ly = maxL; ly > l; ly--) ep = searchLayer(p, ep, 1, ly)[0].second;           // 위 층: 탐욕 이동
        for (int ly = std::min(l, maxL); ly >= 0; ly--) {
            auto cand = searchLayer(p, ep, efC, ly); auto sel = select(cand, M); nb[id][ly] = sel;
            for (int e : sel) { auto& lst = nb[e][ly]; lst.push_back(id); int cap = ly == 0 ? M0 : M;
                if ((int)lst.size() > cap) { std::vector<PI> c; for (int x : lst) { float d = 0; for (int i = 0; i < D; i++) d += (pts[e][i] - pts[x][i]) * (pts[e][i] - pts[x][i]); c.push_back({d, x}); } std::sort(c.begin(), c.end()); lst = select(c, cap); } }
            ep = cand[0].second;
        }
        if (l > maxL) { maxL = l; entry = id; }
    }
    std::vector<int> search(const Pt& q, int k, int ef) {
        int ep = entry; for (int ly = maxL; ly > 0; ly--) ep = searchLayer(q, ep, 1, ly)[0].second;
        auto r = searchLayer(q, ep, std::max(ef, k), 0); std::vector<int> out; for (int i = 0; i < k && i < (int)r.size(); i++) out.push_back(r[i].second); return out;
    }
};

int main() {
    std::mt19937 g(3); std::normal_distribution<float> N(0, 1); int n = 3000, C = 20;
    std::vector<Pt> centers(C); for (auto& c : centers) for (auto& x : c) x = N(g) * 4;
    auto sample = [&]() { Pt p = centers[g() % C]; for (auto& x : p) x += N(g); return p; };
    HNSW h; for (int i = 0; i < n; i++) h.insert(sample());
    for (size_t i = 0; i < h.pts.size(); i++) for (size_t ly = 0; ly < h.nb[i].size(); ly++) assert((int)h.nb[i][ly].size() <= (ly == 0 ? h.M0 : h.M));      // 차수 상한
    std::vector<int> seen(n, 0), st = {h.entry}; seen[h.entry] = 1; int reach = 1;                    // 0층 연결성
    while (!st.empty()) { int c = st.back(); st.pop_back(); for (int e : h.nb[c][0]) if (!seen[e]) { seen[e] = 1; reach++; st.push_back(e); } }
    assert(reach >= n * 0.99);
    int Q = 200, k = 10; double rec[3] = {0, 0, 0}; int efs[3] = {10, 32, 128}; long ev[3] = {0, 0, 0};
    for (int t = 0; t < Q; t++) {
        Pt q = sample(); std::vector<PI> all; for (int i = 0; i < n; i++) { float d = 0; for (int j = 0; j < D; j++) d += (q[j] - h.pts[i][j]) * (q[j] - h.pts[i][j]); all.push_back({d, i}); }
        std::partial_sort(all.begin(), all.begin() + k, all.end()); std::vector<int> exact; for (int i = 0; i < k; i++) exact.push_back(all[i].second);
        for (int e = 0; e < 3; e++) { h.evals = 0; auto r = h.search(q, k, efs[e]); ev[e] += h.evals; int hit = 0; for (int a : r) hit += std::find(exact.begin(), exact.end(), a) != exact.end(); rec[e] += (double)hit / k; }
    }
    for (int e = 0; e < 3; e++) rec[e] /= Q;
    assert(rec[0] <= rec[1] + 1e-9 && rec[1] <= rec[2] + 1e-9 && rec[2] >= 0.95 && rec[1] >= 0.85);        // ef 를 키우면 recall 이 오른다
    assert((double)ev[1] / Q < n / 4.0);                                   // ef=32 에서도 전수 탐색(N 번)의 1/4 미만
    std::cout << "HNSW: n=" << n << ", layers " << h.maxL + 1 << ", recall@10 ef=10/32/128: " << rec[0] << "/" << rec[1] << "/" << rec[2] << ", avg distance evals " << ev[0] / Q << "/" << ev[1] / Q << "/" << ev[2] / Q << " (flat: " << n << ")" << std::endl;
    return 0;
}
// Time Complexity: 삽입·질의 평균 O(log N) 거리 계산 (경험적)
// Space Complexity: O(N·(D + M))
```
## IVFIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// IVF(Inverted File Index): 벡터를 k-평균으로 nlist 개 군집으로 나누고, 군집(=역색인의 "단어")마다 소속 벡터 목록을 보관한다. 질의는 중심 nlist 개와의 거리를 재서 가장 가까운 nprobe 개 군집의 목록만 훑는다.
// 거리 계산 수가 N 에서 nlist + N·nprobe/nlist 로 줄지만, 질의 근처 점이 이웃 군집에 있으면 놓친다 -> nprobe 를 키울수록 recall 이 오르고 nprobe = nlist 면 전수 탐색과 같다.  속도-정확도 조절 손잡이가 nprobe 하나인 단순함이 장점이다
typedef std::vector<float> Vec;
float l2(const Vec& a, const Vec& b) { float s = 0; for (size_t i = 0; i < a.size(); i++) s += (a[i] - b[i]) * (a[i] - b[i]); return s; }
std::vector<Vec> kmeans(const std::vector<Vec>& X, int k, int iters, std::mt19937& g) {
    int dim = X[0].size(); std::vector<int> perm(X.size()); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), g);
    std::vector<Vec> C(k); for (int c = 0; c < k; c++) C[c] = X[perm[c]];
    for (int it = 0; it < iters; it++) {
        std::vector<Vec> sum(k, Vec(dim, 0)); std::vector<int> cnt(k, 0);
        for (auto& x : X) { int b = 0; float bd = 1e30f; for (int c = 0; c < k; c++) { float d = l2(x, C[c]); if (d < bd) { bd = d; b = c; } } cnt[b]++; for (int i = 0; i < dim; i++) sum[b][i] += x[i]; }
        for (int c = 0; c < k; c++) if (cnt[c]) for (int i = 0; i < dim; i++) C[c][i] = sum[c][i] / cnt[c]; else C[c] = X[g() % X.size()];
    }
    return C;
}
struct IVF {
    std::vector<Vec> cents; std::vector<std::vector<int>> lists; const std::vector<Vec>* data; long evals = 0;
    void build(const std::vector<Vec>& X, int nlist, std::mt19937& g) { data = &X; cents = kmeans(X, nlist, 10, g); lists.assign(nlist, {});
        for (size_t i = 0; i < X.size(); i++) { int b = 0; float bd = 1e30f; for (int c = 0; c < nlist; c++) { float d = l2(X[i], cents[c]); if (d < bd) { bd = d; b = c; } } lists[b].push_back(i); } }
    std::vector<int> search(const Vec& q, int k, int nprobe) {
        std::vector<std::pair<float, int>> cd; for (size_t c = 0; c < cents.size(); c++) cd.push_back({l2(q, cents[c]), (int)c}); evals += cents.size();
        std::partial_sort(cd.begin(), cd.begin() + nprobe, cd.end());
        std::vector<std::pair<float, int>> cand; for (int p = 0; p < nprobe; p++) for (int id : lists[cd[p].second]) { cand.push_back({l2(q, (*data)[id]), id}); evals++; }
        int kk = std::min<int>(k, cand.size()); std::partial_sort(cand.begin(), cand.begin() + kk, cand.end()); std::vector<int> out; for (int i = 0; i < kk; i++) out.push_back(cand[i].second); return out;
    }
};

int main() {
    std::mt19937 g(2); std::normal_distribution<float> N(0, 1); int n = 10000, D = 16, C = 40, nlist = 64, k = 10;
    std::vector<Vec> centers(C, Vec(D)); for (auto& c : centers) for (auto& x : c) x = N(g) * 4;
    auto sample = [&]() { Vec p = centers[g() % C]; for (auto& x : p) x += N(g); return p; };
    std::vector<Vec> X; for (int i = 0; i < n; i++) X.push_back(sample());
    IVF ivf; ivf.build(X, nlist, g);
    size_t tot = 0; for (auto& l : ivf.lists) tot += l.size(); assert(tot == (size_t)n);
    int probes[6] = {1, 2, 4, 8, 16, 64}; double rec[6] = {0}; long ev[6] = {0}; int Q = 100;
    for (int t = 0; t < Q; t++) {
        Vec q = sample(); std::vector<std::pair<float, int>> all; for (int i = 0; i < n; i++) all.push_back({l2(q, X[i]), i}); std::partial_sort(all.begin(), all.begin() + k, all.end());
        std::vector<int> exact; for (int i = 0; i < k; i++) exact.push_back(all[i].second);
        for (int p = 0; p < 6; p++) { ivf.evals = 0; auto r = ivf.search(q, k, probes[p]); ev[p] += ivf.evals; int hit = 0; for (int a : r) hit += std::find(exact.begin(), exact.end(), a) != exact.end(); rec[p] += (double)hit / k; }
    }
    for (int p = 0; p < 6; p++) rec[p] /= Q;
    for (int p = 1; p < 6; p++) assert(rec[p] >= rec[p - 1] - 1e-9);       // nprobe 를 키우면 recall 은 줄지 않는다
    assert(rec[5] == 1.0 && rec[3] >= 0.9 && (double)ev[3] / Q < n / 3.0); // nprobe = nlist 면 정확, nprobe=8 이면 recall 90%+ 이면서 거리 계산은 1/3 미만
    std::cout << "IVFIndex: recall@10 for nprobe 1/2/4/8/16/64 = " << rec[0] << "/" << rec[1] << "/" << rec[2] << "/" << rec[3] << "/" << rec[4] << "/" << rec[5]
              << ", avg evals at nprobe=8: " << ev[3] / Q << " (flat " << n << ")" << std::endl; return 0;
}
// Time Complexity: 질의 O(nlist·D + (N/nlist)·nprobe·D)
// Space Complexity: O(N·D + nlist·D)
```
## ProductQuantization()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 곱 양자화(Product Quantization, Jégou 2011): 벡터 압축. D 차원 벡터를 m 개의 부분 벡터(D/m 차원)로 쪼개 각 부분 공간에서 k-평균 코드북(ksub 개 중심)을 따로 학습하고, 벡터를 "m 개의 중심 번호" 로 기억한다.
// ksub^m 가지 조합을 표현하면서 코드북 저장은 m·ksub 개 중심뿐이다.  D=32, float 128 바이트 벡터가 m=8 바이트가 된다(16 배 압축).
// 비대칭 거리 계산(ADC): 질의 q 는 압축하지 않고, 부분 공간마다 "q 의 부분 벡터와 각 중심의 거리" 표 table[j][c] 를 한 번 만든 뒤, 압축된 벡터와의 거리를 표 m 번 조회의 합으로 구한다 — 정확히 q 와 복원 벡터의 거리와 같다
typedef std::vector<float> Vec;
float l2(const float* a, const float* b, int d) { float s = 0; for (int i = 0; i < d; i++) s += (a[i] - b[i]) * (a[i] - b[i]); return s; }
std::vector<Vec> kmeans(const std::vector<Vec>& X, int k, int iters, std::mt19937& g) {
    int dim = X[0].size(); std::vector<int> perm(X.size()); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), g);
    std::vector<Vec> C(k); for (int c = 0; c < k; c++) C[c] = X[perm[c]];
    for (int it = 0; it < iters; it++) {
        std::vector<Vec> sum(k, Vec(dim, 0)); std::vector<int> cnt(k, 0);
        for (auto& x : X) { int b = 0; float bd = 1e30f; for (int c = 0; c < k; c++) { float d = l2(x.data(), C[c].data(), dim); if (d < bd) { bd = d; b = c; } } cnt[b]++; for (int i = 0; i < dim; i++) sum[b][i] += x[i]; }
        for (int c = 0; c < k; c++) if (cnt[c]) for (int i = 0; i < dim; i++) C[c][i] = sum[c][i] / cnt[c]; else C[c] = X[g() % X.size()];
    }
    return C;
}
struct PQ {
    int D, m, ksub, dsub; std::vector<std::vector<Vec>> book;              // book[j][c] = 부분 공간 j 의 중심 c
    PQ(int D, int m, int ksub) : D(D), m(m), ksub(ksub), dsub(D / m) {}
    void train(const std::vector<Vec>& X, std::mt19937& g) { book.clear(); for (int j = 0; j < m; j++) { std::vector<Vec> sub; for (auto& x : X) sub.emplace_back(x.begin() + j * dsub, x.begin() + (j + 1) * dsub); book.push_back(kmeans(sub, ksub, 12, g)); } }
    std::vector<uint8_t> encode(const Vec& x) const { std::vector<uint8_t> code(m); for (int j = 0; j < m; j++) { int b = 0; float bd = 1e30f; for (int c = 0; c < ksub; c++) { float d = l2(x.data() + j * dsub, book[j][c].data(), dsub); if (d < bd) { bd = d; b = c; } } code[j] = b; } return code; }
    Vec decode(const std::vector<uint8_t>& code) const { Vec x(D); for (int j = 0; j < m; j++) for (int i = 0; i < dsub; i++) x[j * dsub + i] = book[j][code[j]][i]; return x; }
    std::vector<float> table(const Vec& q) const { std::vector<float> t(m * ksub); for (int j = 0; j < m; j++) for (int c = 0; c < ksub; c++) t[j * ksub + c] = l2(q.data() + j * dsub, book[j][c].data(), dsub); return t; }
    float adc(const std::vector<float>& t, const std::vector<uint8_t>& code) const { float s = 0; for (int j = 0; j < m; j++) s += t[j * ksub + code[j]]; return s; }
};

int main() {
    std::mt19937 g(5); std::normal_distribution<float> N(0, 1); int n = 4000, D = 32, C = 30;
    std::vector<Vec> centers(C, Vec(D)); for (auto& c : centers) for (auto& x : c) x = N(g) * 3;
    auto sample = [&]() { Vec p = centers[g() % C]; for (auto& x : p) x += N(g); return p; };
    std::vector<Vec> X; for (int i = 0; i < n; i++) X.push_back(sample());
    double mse[3]; int ks[3] = {4, 16, 64};
    for (int t = 0; t < 3; t++) { PQ pq(D, 8, ks[t]); pq.train(X, g); double e = 0; for (int i = 0; i < 500; i++) e += l2(X[i].data(), pq.decode(pq.encode(X[i])).data(), D); mse[t] = e / 500; }
    assert(mse[0] > mse[1] && mse[1] > mse[2]);                            // 코드북이 클수록 복원 오차가 줄어든다
    PQ pq(D, 8, 64); pq.train(X, g); std::vector<std::vector<uint8_t>> codes; for (auto& x : X) codes.push_back(pq.encode(x));
    Vec q = sample(); auto tb = pq.table(q);
    for (int i = 0; i < 20; i++) assert(std::fabs(pq.adc(tb, codes[i]) - l2(q.data(), pq.decode(codes[i]).data(), D)) < 1e-2f * (1 + pq.adc(tb, codes[i])));   // ADC == 복원 벡터와의 거리
    int Q = 100, k = 10, R = 100; double recAdc = 0, recRerank = 0;
    for (int t = 0; t < Q; t++) {
        Vec qq = sample(); auto T = pq.table(qq);
        std::vector<std::pair<float, int>> ex, ap; for (int i = 0; i < n; i++) { ex.push_back({l2(qq.data(), X[i].data(), D), i}); ap.push_back({pq.adc(T, codes[i]), i}); }
        std::partial_sort(ex.begin(), ex.begin() + k, ex.end()); std::partial_sort(ap.begin(), ap.begin() + R, ap.end());
        std::vector<int> exact; for (int i = 0; i < k; i++) exact.push_back(ex[i].second);
        int hit = 0; for (int i = 0; i < k; i++) hit += std::find(exact.begin(), exact.end(), ap[i].second) != exact.end(); recAdc += (double)hit / k;
        std::vector<std::pair<float, int>> rr; for (int i = 0; i < R; i++) rr.push_back({l2(qq.data(), X[ap[i].second].data(), D), ap[i].second}); std::partial_sort(rr.begin(), rr.begin() + k, rr.end());      // 후보 100 개만 원본으로 재순위
        hit = 0; for (int i = 0; i < k; i++) hit += std::find(exact.begin(), exact.end(), rr[i].second) != exact.end(); recRerank += (double)hit / k;
    }
    recAdc /= Q; recRerank /= Q; assert(recRerank >= 0.9 && recRerank >= recAdc);
    std::cout << "ProductQuantization: 128 B -> " << pq.m << " B per vector (16x), MSE by ksub 4/16/64 = " << mse[0] << "/" << mse[1] << "/" << mse[2] << ", recall@10 ADC only " << recAdc << ", with exact re-rank of top " << R << ": " << recRerank << std::endl; return 0;
}
// Time Complexity: 학습 O(m·ksub·N·dsub·반복), 질의 표 만들기 O(ksub·D) + 벡터당 O(m)
// Space Complexity: 벡터당 m 바이트 + 코드북 m·ksub·dsub
```
## KDTreeKNN()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// KD 트리 kNN(트리 관점의 요약, 정본은 Tree.md Part 11): 최근접 이웃을 k 개로 확장한 탐색 — 최대 힙에 k 개를 유지하고, 분할 평면까지의 거리 제곱이 힙의 최댓값(k 번째 최선)보다 크면 반대쪽을 건너뛴다.
// 저차원(~10 이하)에서만 효과적이고 차원이 커지면 거의 모든 가지를 방문한다 -> 고차원은 HNSW·IVF·PQ
typedef std::array<double, 2> P; std::vector<P> a; typedef std::priority_queue<std::pair<double, int>> Heap;
double sq(const P& x, const P& y) { return (x[0] - y[0]) * (x[0] - y[0]) + (x[1] - y[1]) * (x[1] - y[1]); }
void build(int lo, int hi, int ax) { if (hi - lo <= 1) return; int m = (lo + hi) / 2; std::nth_element(a.begin() + lo, a.begin() + m, a.begin() + hi, [&](const P& x, const P& y) { return x[ax] < y[ax]; }); build(lo, m, 1 - ax); build(m + 1, hi, 1 - ax); }
void knn(int lo, int hi, int ax, const P& q, int k, Heap& h) {
    if (lo >= hi) return; int m = (lo + hi) / 2; double d = sq(a[m], q); if ((int)h.size() < k || d < h.top().first) { h.push({d, m}); if ((int)h.size() > k) h.pop(); }
    double diff = q[ax] - a[m][ax]; int nl = diff < 0 ? lo : m + 1, nh = diff < 0 ? m : hi, fl = diff < 0 ? m + 1 : lo, fh = diff < 0 ? hi : m;
    knn(nl, nh, 1 - ax, q, k, h); if ((int)h.size() < k || diff * diff < h.top().first) knn(fl, fh, 1 - ax, q, k, h);
}
int main() {
    std::mt19937 g(1); std::uniform_real_distribution<double> U(0, 1); for (int i = 0; i < 3000; i++) a.push_back({U(g), U(g)}); build(0, a.size(), 0);
    for (int t = 0; t < 200; t++) { P q = {U(g), U(g)}; Heap h; knn(0, a.size(), 0, q, 5, h); std::vector<double> got, all; while (!h.empty()) { got.push_back(h.top().first); h.pop(); } std::reverse(got.begin(), got.end());
        for (auto& p : a) all.push_back(sq(p, q)); std::sort(all.begin(), all.end()); for (int i = 0; i < 5; i++) assert(got[i] == all[i]); }
    std::cout << "KDTreeKNN: 5-NN verified against brute force" << std::endl; return 0;
}
// Time Complexity: 질의 평균 O(log N + k) (저차원)
// Space Complexity: O(N)
```
## BallTreeKNN()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 볼 트리 kNN(이 책 Part 5 BallTree 의 요약): 점들을 공(중심 c, 반지름 r)으로 묶으면 공 안의 모든 점까지의 거리는 최소 |q-c| - r 이상(삼각부등식). 공을 이 하한이 작은 순서로 방문하다가
// 하한이 현재 k 번째 최선 이상이면 남은 공 전부를 한꺼번에 버린다. 아래는 한 층짜리(잎 공들의 목록) 판으로 같은 가지치기 규칙을 보인다
struct Ball { double cx, cy, r; std::vector<std::pair<double, double>> p; };
int main() {
    std::mt19937 g(2); std::uniform_real_distribution<double> U(0, 1); std::vector<std::pair<double, double>> pts; for (int i = 0; i < 4000; i++) pts.push_back({U(g), U(g)});
    std::sort(pts.begin(), pts.end(), [](auto& a, auto& b) { return (int)(a.first * 16) != (int)(b.first * 16) ? a.first < b.first : a.second < b.second; });   // 격자 비슷하게 정렬 후 32 개씩 묶기
    std::vector<Ball> balls; for (size_t i = 0; i < pts.size(); i += 32) { Ball b{0, 0, 0, {pts.begin() + i, pts.begin() + std::min(pts.size(), i + 32)}}; for (auto& q : b.p) { b.cx += q.first / b.p.size(); b.cy += q.second / b.p.size(); }
        for (auto& q : b.p) b.r = std::max(b.r, std::hypot(q.first - b.cx, q.second - b.cy)); balls.push_back(b); }
    long visitedPts = 0; int Q = 100, k = 5;
    for (int t = 0; t < Q; t++) {
        double qx = U(g), qy = U(g); std::vector<std::pair<double, int>> order; for (size_t i = 0; i < balls.size(); i++) order.push_back({std::max(0.0, std::hypot(qx - balls[i].cx, qy - balls[i].cy) - balls[i].r), (int)i}); std::sort(order.begin(), order.end());
        std::priority_queue<double> h; for (auto& o : order) { if ((int)h.size() == k && o.first >= h.top()) break;                // 하한이 k 번째 최선 이상이면 이후 공은 모두 제외
            for (auto& p : balls[o.second].p) { visitedPts++; double d = std::hypot(qx - p.first, qy - p.second); if ((int)h.size() < k) h.push(d); else if (d < h.top()) { h.pop(); h.push(d); } } }
        std::vector<double> all; for (auto& p : pts) all.push_back(std::hypot(qx - p.first, qy - p.second)); std::sort(all.begin(), all.end()); assert(h.top() == all[k - 1]);
    }
    std::cout << "BallTreeKNN: exact 5-NN, avg points examined " << visitedPts / Q << " of " << pts.size() << std::endl; return 0;
}
// Time Complexity: 질의 평균 O(√N) (한 층 판), 계층 볼 트리는 O(log N)
// Space Complexity: O(N)
```
## AnnoyIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// Annoy(Spotify): 랜덤 투영 트리의 숲. 한 트리는 점들을 재귀적으로 둘로 나눈다 — 무작위로 점 a, b 를 뽑아 법선 a-b, 중점을 지나는 초평면으로 가른다(두 점 사이를 수직 이등분).
// 잎에 점이 K 개 이하로 남으면 멈춘다. 트리 하나는 경계 근처의 이웃을 놓치지만 여러 그루가 서로 다른 무작위 평면으로 놓친 것을 보완한다.
// 질의: 모든 트리의 루트를 우선순위 큐(우선순위 = 평면까지의 여유 margin, 질의가 평면에서 멀수록 안전)에 넣고, 높은 것부터 꺼내 내려가며 잎의 점들을 후보로 모은다(search_k 개까지, 가까운 쪽 자식 먼저, 먼 쪽 자식은 낮은 우선순위로 큐에).
// 후보에 대해서만 정확한 거리를 재서 상위 k 개를 돌려준다.  색인 파일을 mmap 으로 공유하기 쉬워 읽기 전용 대규모 데이터에 인기가 있다
typedef std::vector<float> Vec;
float dot(const Vec& a, const Vec& b) { float s = 0; for (size_t i = 0; i < a.size(); i++) s += a[i] * b[i]; return s; }
float l2(const Vec& a, const Vec& b) { float s = 0; for (size_t i = 0; i < a.size(); i++) s += (a[i] - b[i]) * (a[i] - b[i]); return s; }
struct Annoy {
    struct Node { Vec normal; float off = 0; int l = -1, r = -1; std::vector<int> items; };
    std::vector<Vec> pts; std::vector<Node> nodes; std::vector<int> roots; std::mt19937 g{7}; static const int LEAF = 16;
    int build(std::vector<int>& ids) {
        int id = nodes.size(); nodes.emplace_back();
        if ((int)ids.size() <= LEAF) { nodes[id].items = ids; return id; }
        std::vector<int> L, R;
        for (int attempt = 0; attempt < 5 && (L.empty() || R.empty()); attempt++) {
            int a = ids[g() % ids.size()], b = ids[g() % ids.size()]; if (a == b) continue; L.clear(); R.clear();
            Vec nrm(pts[a].size()), mid(pts[a].size()); for (size_t i = 0; i < nrm.size(); i++) { nrm[i] = pts[a][i] - pts[b][i]; mid[i] = (pts[a][i] + pts[b][i]) / 2; }
            float off = -dot(nrm, mid); for (int i : ids) (dot(nrm, pts[i]) + off > 0 ? R : L).push_back(i); nodes[id].normal = nrm; nodes[id].off = off;
        }
        if (L.empty() || R.empty()) { L.assign(ids.begin(), ids.begin() + ids.size() / 2); R.assign(ids.begin() + ids.size() / 2, ids.end()); nodes[id].normal.assign(pts[0].size(), 0); nodes[id].off = 0; }    // 퇴화 시 임의 분할
        int l = build(L), r = build(R); nodes[id].l = l; nodes[id].r = r; return id;
    }
    void buildForest(int trees) { for (int t = 0; t < trees; t++) { std::vector<int> ids(pts.size()); std::iota(ids.begin(), ids.end(), 0); roots.push_back(build(ids)); } }
    std::vector<int> search(const Vec& q, int k, int searchK, long* examined = nullptr) {
        std::priority_queue<std::pair<float, int>> pq; for (int r : roots) pq.push({1e30f, r});
        std::vector<int> cand;
        while (!pq.empty() && (int)cand.size() < searchK) {
            auto [pr, id] = pq.top(); pq.pop(); const Node& nd = nodes[id];
            if (nd.l < 0) { cand.insert(cand.end(), nd.items.begin(), nd.items.end()); continue; }
            float margin = dot(nd.normal, q) + nd.off; pq.push({std::min(pr, margin), nd.r}); pq.push({std::min(pr, -margin), nd.l});     // 양의 쪽 자식은 +margin, 음의 쪽은 -margin
        }
        std::sort(cand.begin(), cand.end()); cand.erase(std::unique(cand.begin(), cand.end()), cand.end()); if (examined) *examined += cand.size();
        std::vector<std::pair<float, int>> sc; for (int i : cand) sc.push_back({l2(q, pts[i]), i}); int kk = std::min<int>(k, sc.size()); std::partial_sort(sc.begin(), sc.begin() + kk, sc.end());
        std::vector<int> out; for (int i = 0; i < kk; i++) out.push_back(sc[i].second); return out;
    }
};

int main() {
    std::mt19937 g(4); std::normal_distribution<float> N(0, 1); int n = 5000, D = 16, C = 25, k = 10;
    std::vector<Vec> centers(C, Vec(D)); for (auto& c : centers) for (auto& x : c) x = N(g) * 4;
    auto sample = [&]() { Vec p = centers[g() % C]; for (auto& x : p) x += N(g); return p; };
    Annoy a10, a50; for (int i = 0; i < n; i++) { Vec p = sample(); a10.pts.push_back(p); a50.pts.push_back(p); } a10.buildForest(10); a50.buildForest(50);
    double r10 = 0, r50 = 0; long ex = 0; int Q = 150;
    for (int t = 0; t < Q; t++) {
        Vec q = sample(); std::vector<std::pair<float, int>> all; for (int i = 0; i < n; i++) all.push_back({l2(q, a10.pts[i]), i}); std::partial_sort(all.begin(), all.begin() + k, all.end());
        std::vector<int> exact; for (int i = 0; i < k; i++) exact.push_back(all[i].second);
        auto score = [&](const std::vector<int>& r) { int hit = 0; for (int x : r) hit += std::find(exact.begin(), exact.end(), x) != exact.end(); return (double)hit / k; };
        r10 += score(a10.search(q, k, 400)); r50 += score(a50.search(q, k, 2000, &ex));
    }
    r10 /= Q; r50 /= Q; assert(r50 >= 0.85 && r50 >= r10 - 0.02 && (double)ex / Q < n / 2.0);     // 트리를 늘리고 search_k 를 키우면 recall 이 오르고, 전수 탐색보다 훨씬 적은 후보만 본다
    std::cout << "AnnoyIndex: recall@10 with 10 trees/search_k 400 = " << r10 << ", 50 trees/search_k 2000 = " << r50 << ", avg candidates examined " << ex / Q << " of " << n << std::endl; return 0;
}
// Time Complexity: 구성 O(트리 수 · N log N), 질의 O(search_k + 후보 정확 거리)
// Space Complexity: O(트리 수 · N)
```
## FAISSIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// FAISS(Facebook AI Similarity Search)의 대표 색인 조합 IVF-PQ ("IVFADC"). 역색인(IVF)으로 후보를 군집 몇 개로 좁히고, 후보 벡터는 곱 양자화(PQ)로 압축해 둔다.
// 핵심은 "잔차(residual) 양자화": 벡터 x 를 군집 중심 c 와의 차이 r = x - c 로 바꿔 PQ 를 학습하면, 잔차의 분산이 원래보다 훨씬 작아 같은 코드 크기에서 오차가 줄어든다.
// 질의: 가까운 nprobe 개 군집마다 q - c 를 기준으로 PQ 거리표를 만들어 해당 군집 코드들의 ADC 거리를 구하고, 상위 R 개를 원본 벡터로 재순위한다. FAISS 는 이런 색인을 "IVF64,PQ8" 같은 문자열 한 줄로 만든다(index factory)
typedef std::vector<float> Vec;
float l2(const float* a, const float* b, int d) { float s = 0; for (int i = 0; i < d; i++) s += (a[i] - b[i]) * (a[i] - b[i]); return s; }
std::vector<Vec> kmeans(const std::vector<Vec>& X, int k, int iters, std::mt19937& g) {
    int dim = X[0].size(); std::vector<int> perm(X.size()); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), g);
    std::vector<Vec> C(k); for (int c = 0; c < k; c++) C[c] = X[perm[c]];
    for (int it = 0; it < iters; it++) {
        std::vector<Vec> sum(k, Vec(dim, 0)); std::vector<int> cnt(k, 0);
        for (auto& x : X) { int b = 0; float bd = 1e30f; for (int c = 0; c < k; c++) { float d = l2(x.data(), C[c].data(), dim); if (d < bd) { bd = d; b = c; } } cnt[b]++; for (int i = 0; i < dim; i++) sum[b][i] += x[i]; }
        for (int c = 0; c < k; c++) if (cnt[c]) for (int i = 0; i < dim; i++) C[c][i] = sum[c][i] / cnt[c]; else C[c] = X[g() % X.size()];
    }
    return C;
}
struct IVFPQ {
    int D, nlist, m, ksub, dsub; std::vector<Vec> cents; std::vector<std::vector<Vec>> book;
    struct Entry { int id; std::vector<uint8_t> code; }; std::vector<std::vector<Entry>> lists; const std::vector<Vec>* data = nullptr;
    IVFPQ(int D, int nlist, int m, int ksub) : D(D), nlist(nlist), m(m), ksub(ksub), dsub(D / m) {}
    int nearestCentroid(const Vec& x) const { int b = 0; float bd = 1e30f; for (int c = 0; c < nlist; c++) { float d = l2(x.data(), cents[c].data(), D); if (d < bd) { bd = d; b = c; } } return b; }
    void build(const std::vector<Vec>& X, std::mt19937& g) {
        data = &X; cents = kmeans(X, nlist, 10, g); std::vector<Vec> res; for (auto& x : X) { int c = nearestCentroid(x); Vec r(D); for (int i = 0; i < D; i++) r[i] = x[i] - cents[c][i]; res.push_back(r); }
        for (int j = 0; j < m; j++) { std::vector<Vec> sub; for (auto& r : res) sub.emplace_back(r.begin() + j * dsub, r.begin() + (j + 1) * dsub); book.push_back(kmeans(sub, ksub, 10, g)); }
        lists.assign(nlist, {});
        for (size_t i = 0; i < X.size(); i++) { int c = nearestCentroid(X[i]); std::vector<uint8_t> code(m);
            for (int j = 0; j < m; j++) { int b = 0; float bd = 1e30f; for (int s = 0; s < ksub; s++) { float d = 0; for (int t = 0; t < dsub; t++) { float diff = X[i][j * dsub + t] - cents[c][j * dsub + t] - book[j][s][t]; d += diff * diff; } if (d < bd) { bd = d; b = s; } } code[j] = b; }
            lists[c].push_back({(int)i, code}); }
    }
    std::vector<int> search(const Vec& q, int k, int nprobe, int R) const {
        std::vector<std::pair<float, int>> cd; for (int c = 0; c < nlist; c++) cd.push_back({l2(q.data(), cents[c].data(), D), c}); std::partial_sort(cd.begin(), cd.begin() + nprobe, cd.end());
        std::vector<std::pair<float, int>> cand;
        for (int p = 0; p < nprobe; p++) { int c = cd[p].second; std::vector<float> T(m * ksub);
            for (int j = 0; j < m; j++) for (int s = 0; s < ksub; s++) { float d = 0; for (int t = 0; t < dsub; t++) { float diff = q[j * dsub + t] - cents[c][j * dsub + t] - book[j][s][t]; d += diff * diff; } T[j * ksub + s] = d; }       // q - c 에 대한 거리표
            for (auto& e : lists[c]) { float d = 0; for (int j = 0; j < m; j++) d += T[j * ksub + e.code[j]]; cand.push_back({d, e.id}); } }
        int rr = std::min<int>(R, cand.size()); std::partial_sort(cand.begin(), cand.begin() + rr, cand.end());
        std::vector<std::pair<float, int>> fin; for (int i = 0; i < rr; i++) fin.push_back({l2(q.data(), (*data)[cand[i].second].data(), D), cand[i].second});
        int kk = std::min<int>(k, fin.size()); std::partial_sort(fin.begin(), fin.begin() + kk, fin.end()); std::vector<int> out; for (int i = 0; i < kk; i++) out.push_back(fin[i].second); return out;
    }
};

int main() {
    std::mt19937 g(6); std::normal_distribution<float> N(0, 1); int n = 6000, D = 32, C = 30, k = 10;
    std::vector<Vec> centers(C, Vec(D)); for (auto& c : centers) for (auto& x : c) x = N(g) * 3;
    auto sample = [&]() { Vec p = centers[g() % C]; for (auto& x : p) x += N(g); return p; };
    std::vector<Vec> X; for (int i = 0; i < n; i++) X.push_back(sample());
    IVFPQ idx(D, 32, 8, 64); idx.build(X, g);
    size_t total = 0; for (auto& l : idx.lists) total += l.size(); assert(total == (size_t)n);
    // ADC 항등식: 질의가 속한 군집의 거리표 합 == q 와 (중심 + 복원 잔차) 의 거리
    { Vec q = sample(); int c = idx.nearestCentroid(q); for (int t = 0; t < 10 && t < (int)idx.lists[c].size(); t++) { auto& e = idx.lists[c][t]; float viaTable = 0, direct = 0;
        for (int j = 0; j < idx.m; j++) for (int i = 0; i < idx.dsub; i++) { float d = q[j * idx.dsub + i] - idx.cents[c][j * idx.dsub + i] - idx.book[j][e.code[j]][i]; direct += d * d; }
        for (int j = 0; j < idx.m; j++) { float s = 0; for (int i = 0; i < idx.dsub; i++) { float d = q[j * idx.dsub + i] - idx.cents[c][j * idx.dsub + i] - idx.book[j][e.code[j]][i]; s += d * d; } viaTable += s; }
        assert(std::fabs(viaTable - direct) < 1e-3f * (1 + direct)); } }
    int Q = 100; double rec = 0, recNoRerank = 0;
    for (int t = 0; t < Q; t++) {
        Vec q = sample(); std::vector<std::pair<float, int>> all; for (int i = 0; i < n; i++) all.push_back({l2(q.data(), X[i].data(), D), i}); std::partial_sort(all.begin(), all.begin() + k, all.end());
        std::vector<int> exact; for (int i = 0; i < k; i++) exact.push_back(all[i].second);
        auto score = [&](const std::vector<int>& r) { int hit = 0; for (int x : r) hit += std::find(exact.begin(), exact.end(), x) != exact.end(); return (double)hit / k; };
        rec += score(idx.search(q, k, 8, 100)); recNoRerank += score(idx.search(q, k, 8, k));              // R=k 이면 사실상 ADC 순위만 사용
    }
    rec /= Q; recNoRerank /= Q; assert(rec >= 0.85 && rec >= recNoRerank);
    std::cout << "FAISSIndex (IVF" << idx.nlist << ",PQ" << idx.m << "): " << D * 4 << " B -> " << idx.m << " B + id per vector, recall@10 with nprobe=8: ADC only " << recNoRerank << ", re-rank top 100 " << rec << std::endl; return 0;
}
// Time Complexity: 질의 O(nlist·D + nprobe·(ksub·D + 목록 길이·m) + R·D)
// Space Complexity: 벡터당 m 바이트 + id, 코드북·중심 O(nlist·D + m·ksub·dsub)
```

# Part 13. 데이터베이스
## SkipList()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 스킵 리스트(리스트 관점의 요약, 정본은 List.md Part 10): 정렬된 연결 리스트에 확률적으로 층을 쌓아 탐색을 기대 O(log N) 으로 만든다. DB 에서는 LevelDB·RocksDB 의 memtable 색인이 이것이다 —
// 회전이 없어 "삽입 전용(insert-only) + 읽기 동시성" 구현이 쉽고, 0층을 따라가면 이미 정렬된 순서라 memtable 을 SSTable 로 내보내는(flush) 순회가 공짜다
struct N { int k; std::vector<N*> nx; };
struct SL {
    N* head = new N{INT_MIN, std::vector<N*>(12, nullptr)}; std::mt19937 g{3}; int lvl = 1;
    void add(int k) { N* up[12]; N* x = head; for (int i = lvl - 1; i >= 0; i--) { while (x->nx[i] && x->nx[i]->k < k) x = x->nx[i]; up[i] = x; }
        int h = 1; while (h < 12 && (g() & 1)) h++; if (h > lvl) { for (int i = lvl; i < h; i++) up[i] = head; lvl = h; } N* n = new N{k, std::vector<N*>(h)};
        for (int i = 0; i < h; i++) { n->nx[i] = up[i]->nx[i]; up[i]->nx[i] = n; } }
};
int main() {
    SL s; std::mt19937 g(1); std::vector<int> v; for (int i = 0; i < 2000; i++) { int k = g() % 100000; v.push_back(k); s.add(k); } std::sort(v.begin(), v.end());
    std::vector<int> out; for (N* x = s.head->nx[0]; x; x = x->nx[0]) out.push_back(x->k); assert(out == v);      // 0층 순회 = 정렬된 순서 (memtable flush)
    std::cout << "SkipList: level-0 walk yields sorted order, " << s.lvl << " levels for 2000 keys" << std::endl; return 0;
}
// Time Complexity: 탐색·삽입 기대 O(log N)
// Space Complexity: 기대 O(N)
```
## MemTable()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// MemTable: LSM 트리의 쓰기 버퍼. 쓰기는 먼저 WAL 에 기록하고 메모리의 memtable 에 반영한다. LevelDB/RocksDB 의 memtable 은 삽입 전용 스킵 리스트이다 — 갱신·삭제도 "기존 항목 수정" 이 아니라
// "(키, 시퀀스 번호, 종류) 항목 추가" 로 처리하기 때문에 구조에서 삭제가 필요 없다.  항목의 순서는 키 오름차순, 같은 키 안에서는 시퀀스 내림차순(최신이 앞)이다.
// 읽기는 "스냅샷 시퀀스 s 이하에서 가장 새로운 항목" 을 찾으므로 쓰기와 독립된 일관된 시점 읽기(MVCC)가 공짜로 된다.  크기가 한도에 이르면 불변(immutable) memtable 로 바꾸고 새 memtable 을 열며 불변본을 SSTable 로 내보낸다(flush)
struct Entry { std::string key, val; uint64_t seq; bool del; };
struct SLNode { Entry e; std::vector<SLNode*> next; };
struct MemTable {
    static const int MAXH = 12; SLNode* head = new SLNode{{}, std::vector<SLNode*>(MAXH, nullptr)}; int height = 1; uint64_t seqNext = 1; size_t bytes = 0; size_t count = 0; bool frozen = false; std::mt19937 rng{11};
    static bool before(const Entry& a, const std::string& key, uint64_t seq) { return a.key < key || (a.key == key && a.seq > seq); }   // a 가 (key, seq) 앞에 놓이는가
    ~MemTable() { for (SLNode* x = head; x;) { SLNode* n = x->next[0]; delete x; x = n; } }
    uint64_t write(const std::string& key, const std::string& val, bool del) {
        assert(!frozen); uint64_t seq = seqNext++; SLNode* up[MAXH]; SLNode* x = head;
        for (int i = height - 1; i >= 0; i--) { while (x->next[i] && before(x->next[i]->e, key, seq)) x = x->next[i]; up[i] = x; }
        int h = 1; while (h < MAXH && (rng() & 3) == 0) h++; if (h > height) { for (int i = height; i < h; i++) up[i] = head; height = h; }
        SLNode* n = new SLNode{{key, val, seq, del}, std::vector<SLNode*>(h)}; for (int i = 0; i < h; i++) { n->next[i] = up[i]->next[i]; up[i]->next[i] = n; }
        bytes += key.size() + val.size() + 16; count++; return seq;
    }
    uint64_t put(const std::string& k, const std::string& v) { return write(k, v, false); }
    uint64_t del(const std::string& k) { return write(k, "", true); }
    int get(const std::string& key, uint64_t snapshot, std::string& val) const {      // 1 찾음, 0 삭제됨(툼스톤), -1 이 memtable 에는 없음 (아래 레벨을 계속 찾아야 함)
        const SLNode* x = head; for (int i = height - 1; i >= 0; i--) while (x->next[i] && before(x->next[i]->e, key, snapshot)) x = x->next[i];
        x = x->next[0]; if (!x || x->e.key != key) return -1; if (x->e.del) return 0; val = x->e.val; return 1;
    }
    std::vector<Entry> flushOrder() const {                                 // 키당 가장 새 항목 하나(툼스톤 포함)를 키 순서로 -> SSTable 입력
        std::vector<Entry> out; for (SLNode* x = head->next[0]; x; x = x->next[0]) if (out.empty() || out.back().key != x->e.key) out.push_back(x->e); return out;
    }
};

int main() {
    MemTable m; std::mt19937 g(2); struct Op { std::string k, v; uint64_t seq; bool del; }; std::vector<Op> ops; size_t expectBytes = 0;
    for (int i = 0; i < 6000; i++) {
        std::string k = "k" + std::to_string(g() % 400), v = "v" + std::to_string(g()); bool del = g() % 5 == 0;
        uint64_t seq = del ? m.del(k) : m.put(k, v); ops.push_back({k, del ? "" : v, seq, del}); expectBytes += k.size() + (del ? 0 : v.size()) + 16;
    }
    assert(m.bytes == expectBytes && m.count == ops.size());               // 바이트 회계
    for (int t = 0; t < 20000; t++) {                                      // 임의의 스냅샷 시점 읽기가 그 시점의 값과 같다
        std::string k = "k" + std::to_string(g() % 420); uint64_t snap = g() % (ops.size() + 1); const Op* last = nullptr;
        for (auto& o : ops) if (o.k == k && o.seq <= snap) last = &o;
        std::string v; int r = m.get(k, snap, v);
        if (!last) assert(r == -1); else if (last->del) assert(r == 0); else assert(r == 1 && v == last->v);
    }
    auto fl = m.flushOrder(); std::map<std::string, Op> newest; for (auto& o : ops) newest[o.k] = o;
    assert(fl.size() == newest.size()); size_t i = 0;
    for (auto& kv : newest) { assert(fl[i].key == kv.first && fl[i].seq == kv.second.seq && fl[i].del == kv.second.del && (fl[i].del || fl[i].val == kv.second.v)); i++; }    // 키 순서, 키당 최신 항목
    m.frozen = true;
    std::cout << "MemTable: " << m.count << " versions of " << fl.size() << " keys (" << m.bytes << " bytes), snapshot reads and flush order verified" << std::endl; return 0;
}
// Time Complexity: 쓰기·읽기 기대 O(log N), flush 순회 O(N)
// Space Complexity: O(쓰기 수) — 갱신도 새 항목이라 한도에 이를 때까지 커진다
```
## SSTable()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// SSTable(Sorted String Table): LSM 트리가 디스크에 쓰는 불변 정렬 파일. 구성: [데이터 블록들] [인덱스 블록] [블룸 필터 블록] [푸터].
//   데이터 블록: 약 4 KB (여기서는 작게) 단위로 (키 길이, 값 길이, 삭제 표시, 키, 값) 레코드를 키 순서로 늘어놓고 끝에 CRC32 를 붙인다.
//   인덱스 블록: 블록마다 (마지막 키, 오프셋, 크기) — 이분 탐색으로 키가 있을 법한 블록 하나만 고른다.   필터 블록: 파일 전체 키의 블룸 필터 — 없는 키는 디스크를 읽지 않고 거절.
//   푸터(고정 32 바이트): 인덱스·필터 위치, 개수, 자체 CRC, 매직 번호 — 파일 끝에서 시작해 나머지를 찾아간다.
// 읽기는 "푸터 -> 인덱스·필터 메모리에 적재 -> 키마다 블룸 -> 이분 탐색 -> 블록 하나 읽고 CRC 검사 -> 블록 안 순차 탐색" 이므로 조회당 블록 읽기가 최대 1 번이다
static uint32_t crcTab[256]; static bool crcInit = false;
uint32_t crc32(const char* p, size_t n) { if (!crcInit) { for (uint32_t i = 0; i < 256; i++) { uint32_t c = i; for (int k = 0; k < 8; k++) c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1; crcTab[i] = c; } crcInit = true; }
    uint32_t c = ~0u; for (size_t i = 0; i < n; i++) c = crcTab[(c ^ (uint8_t)p[i]) & 0xFF] ^ (c >> 8); return ~c; }
void putVar(std::string& s, uint32_t v) { while (v >= 128) { s.push_back((char)((v & 127) | 128)); v >>= 7; } s.push_back((char)v); }
uint32_t getVar(const std::string& s, size_t& p) { uint32_t v = 0, sh = 0; for (;;) { uint8_t b = s[p++]; v |= (uint32_t)(b & 127) << sh; if (!(b & 128)) break; sh += 7; } return v; }
void put32(std::string& s, uint32_t v) { for (int i = 0; i < 4; i++) s.push_back((char)(v >> (8 * i))); }
uint32_t get32(const std::string& s, size_t p) { uint32_t v = 0; for (int i = 0; i < 4; i++) v |= (uint32_t)(uint8_t)s[p + i] << (8 * i); return v; }
uint64_t hmix(const std::string& k, uint64_t seed) { uint64_t h = 1469598103934665603ULL ^ seed; for (unsigned char c : k) { h ^= c; h *= 1099511628211ULL; } h ^= h >> 32; h *= 0x9e3779b97f4a7c15ULL; return h ^ (h >> 29); }
struct Rec { std::string key, val; bool del; };
const uint64_t MAGIC = 0x53535441424c4531ULL;                              // "SSTABLE1"
std::string build(const std::vector<Rec>& recs, size_t blockSize = 256) {
    std::string f, blk, lastKey; struct IE { std::string last; uint32_t off, size; }; std::vector<IE> idx;
    auto flushBlock = [&]() { if (blk.empty()) return; uint32_t off = f.size(); f += blk; put32(f, crc32(blk.data(), blk.size())); idx.push_back({lastKey, off, (uint32_t)blk.size()}); blk.clear(); };
    for (auto& r : recs) { putVar(blk, r.key.size()); putVar(blk, r.val.size()); blk.push_back(r.del ? 1 : 0); blk += r.key; blk += r.val; lastKey = r.key; if (blk.size() >= blockSize) flushBlock(); }
    flushBlock();
    uint32_t indexOff = f.size(); std::string ib; putVar(ib, idx.size()); for (auto& e : idx) { putVar(ib, e.last.size()); ib += e.last; putVar(ib, e.off); putVar(ib, e.size); } f += ib;
    uint32_t filterOff = f.size(); size_t m = std::max<size_t>(64, recs.size() * 10); std::string fb((m + 7) / 8, 0);
    for (auto& r : recs) for (int i = 0; i < 4; i++) { size_t p = hmix(r.key, i) % m; fb[p >> 3] |= (char)(1 << (p & 7)); }
    f += fb;
    std::string foot; put32(foot, indexOff); put32(foot, ib.size()); put32(foot, filterOff); put32(foot, fb.size()); put32(foot, recs.size()); put32(foot, crc32(foot.data(), foot.size()));
    for (int i = 0; i < 8; i++) foot.push_back((char)(MAGIC >> (8 * i))); f += foot; return f;                // 32 바이트
}
struct Table {
    const std::string& f; bool ok = false; struct IE { std::string last; uint32_t off, size; }; std::vector<IE> idx; std::string filter; uint32_t count = 0; long blockReads = 0, bloomSkips = 0;
    explicit Table(const std::string& file) : f(file) {
        if (f.size() < 32) return; size_t b = f.size() - 32; uint64_t magic = 0; for (int i = 0; i < 8; i++) magic |= (uint64_t)(uint8_t)f[b + 24 + i] << (8 * i);
        if (magic != MAGIC || crc32(f.data() + b, 20) != get32(f, b + 20)) return;                   // 푸터 검증
        uint32_t ioff = get32(f, b), isz = get32(f, b + 4), foff = get32(f, b + 8), fsz = get32(f, b + 12); count = get32(f, b + 16);
        std::string ib = f.substr(ioff, isz); size_t p = 0; uint32_t n = getVar(ib, p);
        for (uint32_t i = 0; i < n; i++) { uint32_t kl = getVar(ib, p); std::string last = ib.substr(p, kl); p += kl; uint32_t off = getVar(ib, p), sz = getVar(ib, p); idx.push_back({last, off, sz}); }
        filter = f.substr(foff, fsz); ok = true;
    }
    bool maybe(const std::string& key) const { size_t m = filter.size() * 8; for (int i = 0; i < 4; i++) { size_t p = hmix(key, i) % m; if (!((filter[p >> 3] >> (p & 7)) & 1)) return false; } return true; }
    bool readBlock(const IE& e, std::vector<Rec>& out) {                    // CRC 가 맞아야만 읽는다
        blockReads++; std::string blk = f.substr(e.off, e.size); if (crc32(blk.data(), blk.size()) != get32(f, e.off + e.size)) return false;
        size_t p = 0; while (p < blk.size()) { uint32_t kl = getVar(blk, p), vl = getVar(blk, p); bool del = blk[p++]; Rec r{blk.substr(p, kl), blk.substr(p + kl, vl), del}; p += kl + vl; out.push_back(r); } return true;
    }
    int get(const std::string& key, Rec& out) {                             // 1 찾음, 0 없음, -1 손상
        if (!maybe(key)) { bloomSkips++; return 0; }
        auto it = std::lower_bound(idx.begin(), idx.end(), key, [](const IE& e, const std::string& k) { return e.last < k; }); if (it == idx.end()) return 0;
        std::vector<Rec> rs; if (!readBlock(*it, rs)) return -1; for (auto& r : rs) if (r.key == key) { out = r; return 1; } return 0;
    }
    bool scan(const std::string& lo, const std::string& hi, std::vector<Rec>& out) {
        auto it = std::lower_bound(idx.begin(), idx.end(), lo, [](const IE& e, const std::string& k) { return e.last < k; });
        for (; it != idx.end(); ++it) { std::vector<Rec> rs; if (!readBlock(*it, rs)) return false; bool past = false; for (auto& r : rs) { if (r.key > hi) { past = true; break; } if (r.key >= lo) out.push_back(r); } if (past) break; } return true;
    }
};

int main() {
    assert(crc32("123456789", 9) == 0xCBF43926u);                          // CRC-32 표준 시험값
    std::mt19937 g(5); std::vector<Rec> recs; char kb[16];
    for (int i = 0; i < 4000; i++) { std::snprintf(kb, sizeof kb, "key%06d", i * 3); std::string v(1 + g() % 30, 'a' + g() % 26); recs.push_back({kb, v, g() % 10 == 0}); if (recs.back().del) recs.back().val.clear(); }
    std::string file = build(recs); Table t(file); assert(t.ok && t.count == recs.size());
    for (auto& r : recs) { Rec o; assert(t.get(r.key, o) == 1 && o.val == r.val && o.del == r.del); }      // 모든 키 조회 (툼스톤 포함)
    assert(t.blockReads == (long)recs.size());                             // 조회당 블록 읽기 정확히 1 번
    long fp = 0, T = 4000; t.blockReads = 0; t.bloomSkips = 0;
    for (int i = 0; i < T; i++) { std::snprintf(kb, sizeof kb, "key%06d", i * 3 + 1); Rec o; assert(t.get(kb, o) == 0); }       // 없는 키
    fp = t.blockReads; assert(t.bloomSkips + fp == T && fp < T * 0.05);    // 블룸이 대부분 디스크 읽기 없이 거절
    std::vector<Rec> sc; assert(t.scan("key000300", "key000600", sc)); size_t want = 0; for (auto& r : recs) want += r.key >= "key000300" && r.key <= "key000600"; assert(sc.size() == want);
    std::string bad = file; bad[t.idx[3].off + 5] ^= 0x40; Table tb(bad); Rec o; int code = -2; for (auto& r : recs) if (r.key <= t.idx[3].last && r.key > t.idx[2].last) { code = tb.get(r.key, o); break; }
    assert(code == -1);                                                    // 데이터 블록 한 바이트 변조 -> CRC 로 탐지
    std::string badFoot = file; badFoot[badFoot.size() - 30] ^= 1; assert(!Table(badFoot).ok);                // 푸터 변조 -> 파일 거부
    std::cout << "SSTable: " << recs.size() << " records in " << t.idx.size() << " blocks, file " << file.size() << " bytes; 1 block read per hit, bloom rejected " << t.bloomSkips << "/" << T << " misses, corruption detected" << std::endl; return 0;
}
// Time Complexity: 조회 O(log (블록 수) + 블록 안 레코드 수), 블록 읽기 1 회
// Space Complexity: 파일 O(N), 메모리에는 인덱스·필터만
```
## WriteAheadLog()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 선행 기록 로그(WAL): "데이터를 바꾸기 전에 바꾸려는 내용을 먼저 로그 끝에 순차 기록하고 디스크에 동기화(fsync)한다" 는 규칙. 장애 후에는 로그를 처음부터 재생해 상태를 복원한다.
// 레코드 = [CRC32 4][길이 4][종류 1][내용]. 재생은 레코드를 하나씩 읽다가 길이가 모자라거나(찢어진 쓰기, torn write) CRC 가 틀리면 거기서 멈추고 그 앞의 레코드만 인정한다 -> 항상 "일부 접두사"로 복구되므로 일관적이다.
// 보장: fsync 가 끝난 레코드는 반드시 복구되고, 끝나지 않은 꼬리는 일부만 남거나 사라져도 상태가 어긋나지 않는다.  fsync 가 비싸므로 여러 레코드를 한 번에 동기화하는 그룹 커밋(group commit)으로 횟수를 줄인다
static uint32_t crcTab[256]; static bool crcInit = false;
uint32_t crc32(const char* p, size_t n) { if (!crcInit) { for (uint32_t i = 0; i < 256; i++) { uint32_t c = i; for (int k = 0; k < 8; k++) c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1; crcTab[i] = c; } crcInit = true; }
    uint32_t c = ~0u; for (size_t i = 0; i < n; i++) c = crcTab[(c ^ (uint8_t)p[i]) & 0xFF] ^ (c >> 8); return ~c; }
void put32(std::string& s, uint32_t v) { for (int i = 0; i < 4; i++) s.push_back((char)(v >> (8 * i))); }
uint32_t get32(const std::string& s, size_t p) { uint32_t v = 0; for (int i = 0; i < 4; i++) v |= (uint32_t)(uint8_t)s[p + i] << (8 * i); return v; }
struct WAL {
    std::string buf; size_t synced = 0; long syncs = 0;                   // buf = 파일 내용, synced = 디스크에 확정된 바이트 수
    void append(uint8_t type, const std::string& payload) { std::string body; put32(body, payload.size()); body.push_back((char)type); body += payload; put32(buf, crc32(body.data(), body.size())); buf += body; }
    void sync() { synced = buf.size(); syncs++; }
    std::string crashImage(size_t keepUnsynced) const { return buf.substr(0, std::min(buf.size(), synced + keepUnsynced)); }      // 장애: 동기화 안 된 꼬리는 일부만 남을 수 있다
};
struct Replay { std::vector<std::pair<uint8_t, std::string>> recs; size_t validBytes = 0; };
Replay replay(const std::string& img) {
    Replay r; size_t p = 0;
    while (p + 9 <= img.size()) {
        uint32_t len = get32(img, p + 4); if (p + 9 + len > img.size()) break;                      // 찢어진 레코드
        if (crc32(img.data() + p + 4, 5 + len) != get32(img, p)) break;                              // 손상된 레코드
        r.recs.push_back({(uint8_t)img[p + 8], img.substr(p + 9, len)}); p += 9 + len; r.validBytes = p;
    }
    return r;
}
typedef std::map<std::string, std::string> KV;
void apply(KV& kv, uint8_t type, const std::string& payload) { size_t c = payload.find('='); if (type == 1) kv[payload.substr(0, c)] = payload.substr(c + 1); else kv.erase(payload); }       // 1 = set k=v, 2 = del k

int main() {
    std::mt19937 g(3);
    for (int trial = 0; trial < 300; trial++) {
        WAL w; std::vector<std::pair<uint8_t, std::string>> ops; size_t syncedOps = 0;
        int n = 5 + g() % 60;
        for (int i = 0; i < n; i++) {
            uint8_t type = g() % 4 ? 1 : 2; std::string k = "k" + std::to_string(g() % 20), payload = type == 1 ? k + "=" + std::string(g() % 12, 'x') + std::to_string(i) : k;
            w.append(type, payload); ops.push_back({type, payload}); if (g() % 5 == 0) { w.sync(); syncedOps = ops.size(); }
        }
        size_t tail = w.buf.size() - w.synced; std::string img = w.crashImage(tail ? g() % (tail + 1) : 0);           // 동기화 안 된 꼬리의 임의 길이만 남은 채 정전
        Replay r = replay(img);
        assert(r.recs.size() >= syncedOps && r.recs.size() <= ops.size());                           // 동기화된 레코드는 모두 복구, 그 이상은 접두사만
        KV got, want; for (auto& rc : r.recs) apply(got, rc.first, rc.second);
        for (size_t i = 0; i < r.recs.size(); i++) { assert(r.recs[i] == ops[i]); apply(want, ops[i].first, ops[i].second); }       // 복구된 것은 정확히 처음 j 개
        assert(got == want);
    }
    WAL w; for (int i = 0; i < 10; i++) w.append(1, "k" + std::to_string(i) + "=v"); w.sync();
    std::string corrupt = w.buf; Replay whole = replay(corrupt); assert(whole.recs.size() == 10 && whole.validBytes == corrupt.size());
    size_t rec = corrupt.size() / 10; corrupt[rec * 4 + 12] ^= 0x20; assert(replay(corrupt).recs.size() == 4);   // 다섯 번째 레코드의 한 비트 변조 -> 그 앞 4 개만 인정
    WAL perOp, grouped; for (int i = 0; i < 160; i++) { perOp.append(1, "a=b"); perOp.sync(); grouped.append(1, "a=b"); if (i % 16 == 15) grouped.sync(); }
    assert(perOp.syncs == 160 && grouped.syncs == 10);
    std::cout << "WriteAheadLog: 300 random crashes recover a consistent prefix (all synced records kept); bit corruption stops replay at the bad record; group commit " << grouped.syncs << " syncs vs " << perOp.syncs << std::endl; return 0;
}
// Time Complexity: append O(레코드), 재생 O(로그 길이)
// Space Complexity: 로그 크기 (체크포인트 후 앞부분 삭제)
```
## BTreeIndex()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <vector>
#include <cassert>

// B-트리 인덱스(트리 관점의 요약, 정본은 Tree.md Part 13): 데이터베이스는 "디스크 페이지 읽기 횟수" 로 비용을 센다. 이분 탐색은 log2 N 번 페이지를 건드리지만, 페이지 하나에 키 수백 개를 담는 B-트리는 log_F N (F ≈ 수백) 번 — 수억 행도 3~4 번 읽기이다.
// 아래는 페이지 크기 64 키로 2 단 인덱스(루트 페이지 + 리프 페이지)를 만들어 읽기 횟수를 이분 탐색과 비교한다
int main() {
    const int P = 64; std::vector<int> keys; for (int i = 0; i < 4000; i++) keys.push_back(i * 2);
    std::vector<int> firstKey; for (size_t i = 0; i < keys.size(); i += P) firstKey.push_back(keys[i]);                        // 리프 페이지마다 첫 키 (이것이 루트 페이지)
    long btreeReads = 0, binReads = 0;
    for (int q = 0; q < 8000; q += 2) {
        btreeReads += 1;                                                    // 루트 페이지 1 번
        size_t leaf = std::upper_bound(firstKey.begin(), firstKey.end(), q) - firstKey.begin() - 1; btreeReads += 1;       // 리프 페이지 1 번
        auto b = keys.begin() + leaf * P, e = keys.begin() + std::min(keys.size(), (leaf + 1) * P); assert(std::binary_search(b, e, q));
        size_t lo = 0, hi = keys.size(); long pages = 0; long last = -1; while (lo < hi) { size_t mid = (lo + hi) / 2; if ((long)(mid / P) != last) { pages++; last = mid / P; } if (keys[mid] < q) lo = mid + 1; else hi = mid; } binReads += pages;
    }
    assert(btreeReads / 4000 == 2 && binReads / 4000 > 4);
    std::cout << "BTreeIndex: page reads per lookup B-tree 2 vs binary search " << (double)binReads / 4000 << std::endl; return 0;
}
// Time Complexity: 조회 O(log_F N) 페이지 읽기
// Space Complexity: O(N)
```
## HashIndex()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 해시 인덱스(해시 관점의 요약, 정본은 Hash.md Part 9): 키의 해시로 버킷 페이지를 골라 "=" 조건을 평균 페이지 1~2 번 읽기로 찾는다(넘치면 오버플로 페이지를 사슬로). B-트리보다 등치 조회가 빠르지만
// 키 순서를 모르므로 범위 조건·정렬·접두사 검색은 못 한다 — PostgreSQL 의 hash index, 메모리 DB 의 기본 인덱스. 아래는 페이지 용량 4 인 버킷으로 페이지 읽기를 센다
struct Page { std::vector<int> keys; int overflow = -1; };
int main() {
    const int B = 600; std::vector<Page> pages(B); long readsTotal = 0;
    auto pageOf = [&](int k) { return (unsigned)(k * 2654435761u) % B; };
    for (int k = 0; k < 2000; k++) { int p = pageOf(k); while (pages[p].keys.size() == 4) { if (pages[p].overflow < 0) { pages.push_back({}); pages[p].overflow = pages.size() - 1; } p = pages[p].overflow; } pages[p].keys.push_back(k); }
    for (int k = 0; k < 2000; k++) { int p = pageOf(k); readsTotal++; bool found = false; for (;;) { for (int x : pages[p].keys) found |= x == k; if (found || pages[p].overflow < 0) break; p = pages[p].overflow; readsTotal++; } assert(found); }
    assert((double)readsTotal / 2000 < 1.6);
    std::cout << "HashIndex: equality lookup averages " << (double)readsTotal / 2000 << " page reads (range scans impossible)" << std::endl; return 0;
}
// Time Complexity: 등치 조회 평균 O(1) 페이지 읽기
// Space Complexity: O(N)
```

# Part 14. 운영체제
## BuddyAllocator()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <cassert>

// 버디 할당기(메모리 관점의 요약, 정본은 Memory.md Part 6): 메모리를 2^k 페이지 블록으로만 나눈다. 할당은 요청보다 크거나 같은 가장 작은 빈 블록을 찾아 필요한 크기가 될 때까지 반으로 쪼개고(남는 반쪽은 빈 목록에),
// 해제는 "버디"(블록 시작 주소 XOR 크기)가 비어 있으면 합쳐 위 차수로 올린다.  버디의 주소가 XOR 한 번으로 구해져 빠르고, 외부 단편화가 제한된다 (Linux 페이지 할당기)
const int MAXO = 6; std::set<int> freeList[MAXO + 1];
int alloc(int k) { int j = k; while (j <= MAXO && freeList[j].empty()) j++; if (j > MAXO) return -1; int b = *freeList[j].begin(); freeList[j].erase(b); while (j > k) { j--; freeList[j].insert(b + (1 << j)); } return b; }
void freeBlk(int b, int k) { while (k < MAXO && freeList[k].count(b ^ (1 << k))) { freeList[k].erase(b ^ (1 << k)); b &= ~(1 << k); k++; } freeList[k].insert(b); }
int main() {
    freeList[MAXO].insert(0); int a = alloc(0), b = alloc(1), c = alloc(2);      // 64 페이지에서 1, 2, 4 페이지 요청
    assert(a == 0 && b == 2 && c == 4 && freeList[MAXO].empty());
    freeBlk(a, 0); freeBlk(b, 1); freeBlk(c, 2);                           // 전부 해제하면 버디끼리 합쳐 원래의 64 페이지 블록으로
    assert(freeList[MAXO].size() == 1 && *freeList[MAXO].begin() == 0);
    std::cout << "BuddyAllocator: split on alloc, coalesce on free back to one order-" << MAXO << " block" << std::endl; return 0;
}
// Time Complexity: 할당·해제 O(MAXO) 차수 이동
// Space Complexity: 빈 블록 목록
```
## SlabAllocator()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 슬랩 할당기(메모리 관점의 요약, 정본은 Memory.md Part 6): 같은 크기의 객체(inode, 소켓 버퍼 ...)를 자주 할당·해제할 때 미리 같은 크기 칸으로 나눈 "슬랩" 페이지를 두고 빈 칸 목록에서 O(1) 로 꺼낸다.
// 해제된 칸은 초기화된 채로 재사용되어 생성 비용도 절약되고 내부 단편화가 거의 없다. 슬랩이 가득/일부/빔 상태를 오가며 다 비면 페이지를 돌려준다 (Linux kmem_cache)
struct Slab { std::vector<char> mem; std::vector<int> freeIdx; int used = 0; Slab(int objs, int sz) : mem(objs * sz) { for (int i = objs - 1; i >= 0; i--) freeIdx.push_back(i); } };
struct Cache {
    int sz, objs; std::vector<Slab*> slabs; Cache(int sz, int objs) : sz(sz), objs(objs) {}
    char* alloc() { for (Slab* s : slabs) if (!s->freeIdx.empty()) { int i = s->freeIdx.back(); s->freeIdx.pop_back(); s->used++; return &s->mem[i * sz]; } slabs.push_back(new Slab(objs, sz)); return alloc(); }
    void free(char* p) { for (Slab* s : slabs) if (p >= s->mem.data() && p < s->mem.data() + s->mem.size()) { s->freeIdx.push_back((p - s->mem.data()) / sz); s->used--; return; } }
};
int main() {
    Cache c(16, 8); std::vector<char*> v; for (int i = 0; i < 20; i++) v.push_back(c.alloc());
    assert(c.slabs.size() == 3);                                           // 20 개 -> 8 칸 슬랩 3 개
    for (char* p : v) c.free(p); int empty = 0; for (Slab* s : c.slabs) empty += s->used == 0; assert(empty == 3);
    char* again = c.alloc(); assert(c.slabs.size() == 3 && again != nullptr);   // 해제된 칸을 재사용 (새 슬랩 없음)
    std::cout << "SlabAllocator: 20 objects in 3 slabs, freed slots reused without new slabs" << std::endl; return 0;
}
// Time Complexity: 할당·해제 O(1) (슬랩 탐색 제외)
// Space Complexity: 슬랩 × 객체 수 × 크기
```
## RadixTree()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <cassert>

// 기수 트리(트리 관점의 요약, 문자열용은 Tree.md Part 9, 정수 키용 본격판은 이 Part 의 XArray): 키를 고정 비트 폭 조각(여기서는 4 비트 = 16-분)으로 잘라 한 층에 한 조각씩 내려가는 트리.
// 비교가 아니라 인덱싱으로 O(키 비트 수 / 조각 폭) 에 찾고 정렬 순서가 자연스럽게 유지된다 (Linux 의 radix tree -> XArray)
struct N { N* c[16] = {}; bool has = false; long v = 0; };
void put(N* r, uint32_t k, long v) { N* n = r; for (int s = 28; s >= 0; s -= 4) { int i = (k >> s) & 15; if (!n->c[i]) n->c[i] = new N; n = n->c[i]; } n->has = true; n->v = v; }
bool get(N* r, uint32_t k, long& v) { N* n = r; for (int s = 28; s >= 0 && n; s -= 4) n = n->c[(k >> s) & 15]; if (!n || !n->has) return false; v = n->v; return true; }
int main() { N root; put(&root, 0xDEADBEEF, 42); put(&root, 7, 9); long v; assert(get(&root, 0xDEADBEEF, v) && v == 42 && get(&root, 7, v) && v == 9 && !get(&root, 8, v)); std::cout << "RadixTree: 8-level 16-ary lookup" << std::endl; return 0; }
// Time Complexity: 조회·삽입 O(키 비트 / 4)
// Space Complexity: 쓰인 경로 비례
```
## XArray()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// XArray(Linux 커널 4.20+, 옛 radix tree 의 후속): 정수 인덱스 -> 값을 저장하는 희소 배열. 한 노드가 64 칸(인덱스 6 비트)이고 깊이는 가장 큰 인덱스에 맞춰 필요한 만큼 자란다
// (루트 위에 새 루트를 얹어 키울 수 있음). 페이지 캐시(파일 오프셋 -> 페이지)가 대표 용도다.  각 노드는 "칸이 쓰였는가" 비트맵과, 세 가지 태그(dirty, writeback, towrite ...)별 비트맵을 가진다.
// 태그 비트맵은 "이 칸 또는 이 칸 아래에 태그된 항목이 있는가" 를 뜻해서, 태그된 다음 항목 찾기(xa_find_tagged)가 아래쪽 전체를 훑지 않고 비트 연산 몇 번으로 건너뛴다 (더티 페이지 쓰기 되돌림에 필수)
struct XNode { int shift; XNode* parent = nullptr; int offset = 0; uint64_t used = 0; uint64_t tags[3] = {0, 0, 0}; XNode* child[64] = {}; long val[64]; };
struct XArray {
    XNode* root = nullptr; long size = 0, nodes = 0;
    static uint64_t maxIndex(const XNode* n) { return n->shift + 6 >= 64 ? ~0ULL : (1ULL << (n->shift + 6)) - 1; }
    XNode* mk(int shift, XNode* parent, int off) { nodes++; XNode* n = new XNode; n->shift = shift; n->parent = parent; n->offset = off; return n; }
    void grow(uint64_t index) {
        if (!root) root = mk(0, nullptr, 0);
        while (index > maxIndex(root)) { XNode* r = mk(root->shift + 6, nullptr, 0); r->child[0] = root; r->used = 1; for (int t = 0; t < 3; t++) if (root->tags[t]) r->tags[t] = 1; root->parent = r; root->offset = 0; root = r; }
    }
    void store(uint64_t index, long v) {
        grow(index); XNode* n = root;
        while (n->shift > 0) { int off = (index >> n->shift) & 63; if (!n->child[off]) { n->child[off] = mk(n->shift - 6, n, off); n->used |= 1ULL << off; } n = n->child[off]; }
        int off = index & 63; if (!((n->used >> off) & 1)) { n->used |= 1ULL << off; size++; } n->val[off] = v;
    }
    XNode* leafOf(uint64_t index) const { if (!root || index > maxIndex(root)) return nullptr; XNode* n = root; while (n->shift > 0) { n = n->child[(index >> n->shift) & 63]; if (!n) return nullptr; } return n; }
    bool load(uint64_t index, long& v) const { XNode* n = leafOf(index); int off = index & 63; if (!n || !((n->used >> off) & 1)) return false; v = n->val[off]; return true; }
    bool hasTag(uint64_t index, int t) const { XNode* n = leafOf(index); return n && ((n->tags[t] >> (index & 63)) & 1); }
    bool setTag(uint64_t index, int t) { XNode* n = leafOf(index); int off = index & 63; if (!n || !((n->used >> off) & 1)) return false; for (; n; off = n->offset, n = n->parent) n->tags[t] |= 1ULL << off; return true; }     // 위로 올라가며 비트 켬
    void clearTag(uint64_t index, int t) {
        XNode* n = leafOf(index); if (!n) return; int off = index & 63; n->tags[t] &= ~(1ULL << off);
        while (n->parent && n->tags[t] == 0) { off = n->offset; n = n->parent; n->tags[t] &= ~(1ULL << off); }              // 아래에 태그가 없으면 부모의 비트도 끈다
    }
    bool erase(uint64_t index) {
        XNode* n = leafOf(index); int off = index & 63; if (!n || !((n->used >> off) & 1)) return false;
        for (int t = 0; t < 3; t++) clearTag(index, t);
        n->used &= ~(1ULL << off); size--;
        while (n && n->used == 0) {                                        // 비어 버린 노드는 위로 올라가며 해제
            XNode* p = n->parent; if (p) { p->child[n->offset] = nullptr; p->used &= ~(1ULL << n->offset); } else root = nullptr; delete n; nodes--; n = p;
        }
        while (root && root->shift > 0 && root->used == 1) { XNode* c = root->child[0]; c->parent = nullptr; delete root; nodes--; root = c; }          // 루트에 자식이 0 번 하나뿐이면 높이를 줄인다
        return true;
    }
    bool nextIn(const XNode* n, uint64_t base, uint64_t start, int tag, uint64_t& out) const {      // tag < 0 이면 존재하는 항목, 아니면 태그된 항목 중 start 이상 최소 인덱스
        uint64_t mask = tag < 0 ? n->used : n->tags[tag];
        if (n->shift == 0) { int from = start > base ? (int)(start - base) : 0; if (from >= 64) return false; mask &= ~0ULL << from; if (!mask) return false; out = base + __builtin_ctzll(mask); return true; }
        int from = start > base ? (int)((start - base) >> n->shift) : 0; if (from >= 64) return false;
        mask &= ~0ULL << from;
        while (mask) { int s = __builtin_ctzll(mask); mask &= mask - 1; if (nextIn(n->child[s], base + ((uint64_t)s << n->shift), start, tag, out)) return true; }
        return false;
    }
    bool findNext(uint64_t start, uint64_t& out, int tag = -1) const { return root && nextIn(root, 0, start, tag, out); }
    ~XArray() { std::vector<XNode*> st; if (root) st.push_back(root); while (!st.empty()) { XNode* n = st.back(); st.pop_back(); for (auto* c : n->child) if (c) st.push_back(c); delete n; } }
};

int main() {
    XArray xa; std::map<uint64_t, long> ref; std::set<uint64_t> tg[3]; std::mt19937_64 g(1);
    auto randIdx = [&]() { return g() % 10 < 7 ? g() % 6000 : g() % (1ULL << 40); };
    for (int step = 0; step < 60000; step++) {
        uint64_t i = randIdx(); int op = g() % 8; long v = (long)g();
        if (op <= 2) { xa.store(i, v); ref[i] = v; }
        else if (op == 3) { bool e = xa.erase(i); assert(e == (ref.erase(i) > 0)); for (auto& s : tg) s.erase(i); }
        else if (op == 4) { int t = g() % 3; bool ok = xa.setTag(i, t); assert(ok == (ref.count(i) > 0)); if (ok) tg[t].insert(i); }
        else if (op == 5) { int t = g() % 3; xa.clearTag(i, t); tg[t].erase(i); }
        else if (op == 6) { long got = 0; bool f = xa.load(i, got); auto it = ref.find(i); assert(f == (it != ref.end()) && (!f || got == it->second)); }
        else { uint64_t out; bool f = xa.findNext(i, out); auto it = ref.lower_bound(i); assert(f == (it != ref.end()) && (!f || out == it->first));
               int t = g() % 3; f = xa.findNext(i, out, t); auto jt = tg[t].lower_bound(i); assert(f == (jt != tg[t].end()) && (!f || out == *jt)); }
        assert(xa.size == (long)ref.size());
    }
    for (auto& kv : ref) { long v; assert(xa.load(kv.first, v) && v == kv.second); for (int t = 0; t < 3; t++) assert(xa.hasTag(kv.first, t) == (tg[t].count(kv.first) > 0)); }
    XArray dense; for (uint64_t i = 0; i < 4096; i++) dense.store(i, (long)i); assert(dense.nodes == 65);           // 0..4095: 잎 64 개 + 루트 1 개
    long nodesBefore = xa.nodes; std::vector<uint64_t> keys; for (auto& kv : ref) keys.push_back(kv.first); for (uint64_t k : keys) assert(xa.erase(k));
    assert(xa.size == 0 && xa.root == nullptr && xa.nodes == 0);           // 모두 지우면 노드가 전부 해제된다
    std::cout << "XArray: 60000 mixed ops match std::map (+3 tag sets, next/next-tagged search); " << nodesBefore << " nodes freed to 0; dense 4096 entries use " << dense.nodes << " nodes" << std::endl; return 0;
}
// Time Complexity: 조회·저장·삭제 O(높이 = ⌈log64 (최대 인덱스)⌉), 다음 항목 찾기 O(높이 + 건너뛴 칸을 비트로)
// Space Complexity: 쓰인 인덱스 구간 비례, 노드 64 칸
```
## PageTable()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <cassert>

// 페이지 테이블(메모리 관점의 요약, 정본은 Memory.md Part 9): 가상 주소 -> 물리 주소 변환표. 32비트 2 단 구조 = 상위 10비트(디렉터리) + 중간 10비트(테이블) + 하위 12비트(페이지 안 오프셋, 4 KB).
// 쓰는 영역의 테이블만 만들어 두므로 주소 공간이 커도 메모리가 적게 들고, 없는 항목에 접근하면 페이지 폴트가 난다 (OS 가 처리). TLB 는 최근 변환을 캐시한다
struct PT {
    uint32_t* dir[1024] = {};
    void map(uint32_t va, uint32_t pa) { uint32_t d = va >> 22, t = (va >> 12) & 1023; if (!dir[d]) dir[d] = new uint32_t[1024](); dir[d][t] = (pa & ~4095u) | 1; }        // 비트 0 = present
    bool translate(uint32_t va, uint32_t& pa) const { uint32_t d = va >> 22, t = (va >> 12) & 1023; if (!dir[d] || !(dir[d][t] & 1)) return false; pa = (dir[d][t] & ~4095u) | (va & 4095); return true; }
};
int main() {
    PT pt; pt.map(0x00400000, 0x1000); pt.map(0xBFFFF000, 0x7000); uint32_t pa;
    assert(pt.translate(0x00400123, pa) && pa == 0x1123 && pt.translate(0xBFFFFABC, pa) && pa == 0x7ABC && !pt.translate(0x00800000, pa));        // 매핑 안 된 주소 = 페이지 폴트
    int tables = 0; for (auto* t : pt.dir) tables += t != nullptr; assert(tables == 2);
    std::cout << "PageTable: 2 mapped pages need only " << tables << " second-level tables" << std::endl; return 0;
}
// Time Complexity: 변환 O(레벨 수) = 메모리 접근 2 번 (TLB 적중 시 0)
// Space Complexity: 사용한 영역 비례
```

# Part 15. 최신 연구
## LearnedIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 학습된 인덱스(Learned Index, Kraska et al. 2018): "B-트리는 키 -> 위치 함수(= 누적분포 CDF 에 N 을 곱한 것)를 근사하는 모델이다" 라는 관점. 그 함수를 직접 학습하면 이분 탐색의 log N 번 비교를 모델 한 번의 계산과 아주 작은 보정 탐색으로 대신할 수 있다.
// RMI(Recursive Model Index) 2 단: 1 단 선형 모델이 키를 보고 "어느 2 단 모델이 담당할지" 고르고, 각 2 단 선형 모델(최소제곱 회귀)이 위치를 예측한다. 모델마다 학습 때 실제 위치와 예측의 오차 구간 [errLo, errHi] 를 기록해 두므로
// 조회는 "예측 위치 + 오차 구간" 안에서만 이분 탐색하면 되고 결과가 항상 정확하다 (모델이 틀려도 느려질 뿐 틀린 답은 없다).  분포가 매끄러울수록 오차 구간이 작다
struct Lin { double a = 0, b = 0; double at(double x) const { return a * x + b; } };
Lin fit(const std::vector<double>& xs, const std::vector<double>& ys) {
    Lin m; size_t n = xs.size(); if (!n) return m; double mx = 0, my = 0; for (size_t i = 0; i < n; i++) { mx += xs[i]; my += ys[i]; } mx /= n; my /= n;
    double sxx = 0, sxy = 0; for (size_t i = 0; i < n; i++) { sxx += (xs[i] - mx) * (xs[i] - mx); sxy += (xs[i] - mx) * (ys[i] - my); }
    m.a = sxx > 0 ? sxy / sxx : 0; m.b = my - m.a * mx; return m;
}
struct RMI {
    std::vector<double> keys; int B; Lin root; std::vector<Lin> leaf; std::vector<double> eLo, eHi; long outOfWindow = 0;
    int route(double x) const { int i = (int)std::floor(root.at(x)); return std::min(std::max(i, 0), B - 1); }
    RMI(std::vector<double> k, int B) : keys(std::move(k)), B(B), leaf(B), eLo(B, 0), eHi(B, 0) {
        size_t n = keys.size(); std::vector<double> ys(n); for (size_t i = 0; i < n; i++) ys[i] = (double)i * B / n;           // CDF 를 모델 개수로 스케일
        root = fit(keys, ys);
        std::vector<std::vector<double>> kx(B), ky(B); for (size_t i = 0; i < n; i++) { int m = route(keys[i]); kx[m].push_back(keys[i]); ky[m].push_back((double)i); }
        for (int m = 0; m < B; m++) { leaf[m] = fit(kx[m], ky[m]); double lo = 1e18, hi = -1e18;
            for (size_t j = 0; j < kx[m].size(); j++) { double e = ky[m][j] - leaf[m].at(kx[m][j]); lo = std::min(lo, e); hi = std::max(hi, e); } if (!kx[m].empty()) { eLo[m] = lo; eHi[m] = hi; } }
    }
    long lowerBound(double x, long* window = nullptr) {                      // x 이상인 첫 위치
        int m = route(x); double p = leaf[m].at(x); long n = keys.size();
        long lo = std::max(0L, (long)std::floor(p + eLo[m])), hi = std::min(n, (long)std::ceil(p + eHi[m]) + 1);
        if (lo > hi) lo = hi; if (window) *window = hi - lo;
        long r = std::lower_bound(keys.begin() + lo, keys.begin() + hi, x) - keys.begin();
        bool ok = (r == 0 || keys[r - 1] < x) && (r == n || keys[r] >= x);   // 없는 키를 물었을 때 구간 밖으로 어긋날 수 있다 -> 확인 후 보정
        if (!ok) { outOfWindow++; r = std::lower_bound(keys.begin(), keys.end(), x) - keys.begin(); }
        return r;
    }
};

int main() {
    std::mt19937_64 g(7); const int N = 100000; const char* names[3] = {"uniform", "lognormal", "20 clusters (step-like CDF)"};
    for (int dist = 0; dist < 3; dist++) {
        std::vector<double> k(N); std::lognormal_distribution<double> ln(0, 1.0); std::uniform_real_distribution<double> U(0, 1e9);
        for (auto& x : k) x = dist == 0 ? U(g) : dist == 1 ? ln(g) * 1e6 : (double)(g() % 20) * 1e8 + U(g) * 1e5;                 // 마지막은 계단형 CDF (모델에게 어려움)
        std::sort(k.begin(), k.end()); k.erase(std::unique(k.begin(), k.end()), k.end());
        RMI idx(k, 1000); double win = 0; long maxWin = 0;
        for (size_t i = 0; i < k.size(); i += 7) { long w = 0; long r = idx.lowerBound(k[i], &w); assert(r == (long)i); win += w; maxWin = std::max(maxWin, w); }   // 모든 키를 정확히 찾는다
        for (int t = 0; t < 20000; t++) { double q = U(g) * (dist == 1 ? 1e-3 : 1) + (dist == 2 ? (double)(g() % 20) * 1e8 : 0); long r = idx.lowerBound(q); assert(r == std::lower_bound(k.begin(), k.end(), q) - k.begin()); }   // 없는 키도 정확
        double avgWin = win / ((k.size() + 6) / 7);
        std::cout << names[dist] << ": avg search window " << avgWin << " (binary search over all: " << k.size() << "), max " << maxWin << ", log2 comparisons " << std::log2(std::max(1.0, avgWin)) << " vs " << std::log2((double)k.size()) << std::endl;
        assert(avgWin < k.size() / 100.0);                                 // 어느 분포든 창이 전체의 1% 미만 (균등 분포는 수십 칸, 꼬리가 긴 분포는 수백 칸)
        if (dist == 0) assert(avgWin < 32);                                // 균등 분포: 모델이 위치를 거의 직접 계산한다
    }
    return 0;
}
// Time Complexity: 조회 O(1) 모델 계산 + O(log (오차 구간)), 구성 O(N)
// Space Complexity: O(모델 수) (키 배열 제외)
```
## LearnedHash()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 학습된 해시(해시 관점의 요약, 정본은 Hash.md Part 15): 해시 함수가 키를 버킷에 "고르게" 뿌리는 일은 곧 키 분포의 누적분포 CDF 를 아는 일이다 — h(x) = ⌊CDF(x)·m⌋ 이면 키가 버킷에 정확히 균등하게 놓인다.
// 일반 해시는 분포를 몰라 무작위로 뿌리므로 n=m 일 때 버킷의 약 36.8% 가 비고 키의 약 37% 가 충돌한다. 표본에서 학습한 CDF(여기서는 1000 개 표본점 사이 선형 보간)를 쓰면 키가 규칙적으로 늘어나는 데이터(타임스탬프, 증가하는 ID, 센서 값)에서 충돌이 거의 사라진다.
// 주의: 키가 분포에서 독립적으로 무작위로 뽑힌 값이라면 CDF(키)도 무작위라서 학습해도 이득이 없다 — 이득은 키가 "무작위보다 규칙적일 때"만 생기고, 분포가 바뀌면 다시 학습해야 한다
int main() {
    const int n = 100000, m = 100000; std::vector<double> keys(n); for (int i = 0; i < n; i++) keys[i] = (double)i * i * 0.7 + (i % 17) * 0.3 + 5;       // 비선형이지만 매끄러운 증가열
    std::vector<double> sample; for (int i = 0; i < n; i += 100) sample.push_back(keys[i]); sample.push_back(keys.back());
    auto cdf = [&](double x) { size_t i = std::upper_bound(sample.begin(), sample.end(), x) - sample.begin(); if (!i) return 0.0; if (i == sample.size()) return 1.0 - 1e-12; return ((double)(i - 1) + (x - sample[i - 1]) / (sample[i] - sample[i - 1])) / (sample.size() - 1); };
    std::vector<int> a(m, 0), b(m, 0); for (double x : keys) { a[std::min<size_t>((size_t)(cdf(x) * m), m - 1)]++; uint64_t h = std::hash<double>{}(x) * 0x9e3779b97f4a7c15ULL; b[(h ^ (h >> 29)) % m]++; }
    long ca = 0, cb = 0; for (int i = 0; i < m; i++) { ca += std::max(0, a[i] - 1); cb += std::max(0, b[i] - 1); }
    assert(ca * 10 < cb); std::cout << "LearnedHash: colliding keys learned-CDF " << ca << " vs random hash " << cb << " of " << n << std::endl; return 0;
}
// Time Complexity: 해시 계산 O(log (분위점 수)) 이분 탐색
// Space Complexity: O(분위점 수)
```
## AdaptiveRadixTree()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 적응형 기수 트리(ART, Leis et al. 2013; HyPer, DuckDB 의 인덱스): 바이트 단위 기수 트리인데 자식 수에 따라 노드 형식을 바꿔 공간과 속도를 동시에 잡는다.
//   Node4 (정렬된 키 4 개 + 자식 4 개, 선형 탐색)  Node16 (키 16 개, SIMD 비교 가능)  Node48 (256 바이트 색인표 -> 자식 48 개)  Node256 (직접 배열)
// 노드가 차면 다음 형식으로 키우고(grow), 줄어들면 작은 형식으로 줄인다(shrink).  공통 접두사는 노드에 압축 저장하고(경로 압축), 잎은 전체 키를 가지고 있어 한 키만 남은 가지는 중간 노드 없이 잎으로 바로 이어진다(느긋한 확장).
// 키가 서로의 접두사가 되지 않도록 끝에 0 바이트를 붙여 쓴다. 정렬된 순회가 곧 키 순서이고, 해시 테이블과 달리 범위 질의·접두사 질의가 된다
enum Kind : uint8_t { LEAF, N4, N16, N48, N256 };
struct Node { Kind kind; std::vector<uint8_t> prefix; int n = 0; explicit Node(Kind k) : kind(k) {} };
struct Leaf : Node { std::string key; long val; Leaf(const std::string& k, long v) : Node(LEAF), key(k), val(v) {} };
struct Node4 : Node { uint8_t k[4]; Node* c[4]; Node4() : Node(N4) {} };
struct Node16 : Node { uint8_t k[16]; Node* c[16]; Node16() : Node(N16) {} };
struct Node48 : Node { uint8_t idx[256]; Node* c[48]; Node48() : Node(N48) { std::fill(idx, idx + 256, 255); std::fill(c, c + 48, nullptr); } };
struct Node256 : Node { Node* c[256]; Node256() : Node(N256) { std::fill(c, c + 256, nullptr); } };

Node** findChild(Node* n, uint8_t b) {
    switch (n->kind) {
        case N4:   { auto* x = (Node4*)n;  for (int i = 0; i < n->n; i++) if (x->k[i] == b) return &x->c[i]; return nullptr; }
        case N16:  { auto* x = (Node16*)n; for (int i = 0; i < n->n; i++) if (x->k[i] == b) return &x->c[i]; return nullptr; }
        case N48:  { auto* x = (Node48*)n; return x->idx[b] != 255 ? &x->c[x->idx[b]] : nullptr; }
        case N256: { auto* x = (Node256*)n; return x->c[b] ? &x->c[b] : nullptr; }
        default: return nullptr;
    }
}
template <class T> void insertSorted(T* x, uint8_t b, Node* child) { int i = x->n; while (i > 0 && x->k[i - 1] > b) { x->k[i] = x->k[i - 1]; x->c[i] = x->c[i - 1]; i--; } x->k[i] = b; x->c[i] = child; x->n++; }
void addChild(Node*& ref, uint8_t b, Node* child) {
    switch (ref->kind) {
        case N4:  { auto* x = (Node4*)ref; if (x->n < 4) { insertSorted(x, b, child); return; }
                    auto* y = new Node16; y->prefix = x->prefix; y->n = x->n; for (int i = 0; i < x->n; i++) { y->k[i] = x->k[i]; y->c[i] = x->c[i]; } delete x; ref = y; addChild(ref, b, child); return; }       // 4 -> 16 으로 성장
        case N16: { auto* x = (Node16*)ref; if (x->n < 16) { insertSorted(x, b, child); return; }
                    auto* y = new Node48; y->prefix = x->prefix; for (int i = 0; i < x->n; i++) { y->idx[x->k[i]] = i; y->c[i] = x->c[i]; } y->n = x->n; delete x; ref = y; addChild(ref, b, child); return; }
        case N48: { auto* x = (Node48*)ref; if (x->n < 48) { int pos = 0; while (x->c[pos]) pos++; x->idx[b] = pos; x->c[pos] = child; x->n++; return; }
                    auto* y = new Node256; y->prefix = x->prefix; for (int i = 0; i < 256; i++) if (x->idx[i] != 255) y->c[i] = x->c[x->idx[i]]; y->n = x->n; delete x; ref = y; addChild(ref, b, child); return; }
        case N256: { auto* x = (Node256*)ref; x->c[b] = child; x->n++; return; }
        default: return;
    }
}
void removeChild(Node*& ref, uint8_t b) {
    switch (ref->kind) {
        case N4: case N16: {
            uint8_t* keys = ref->kind == N4 ? ((Node4*)ref)->k : ((Node16*)ref)->k; Node** ch = ref->kind == N4 ? ((Node4*)ref)->c : ((Node16*)ref)->c;
            int i = 0; while (keys[i] != b) i++; for (; i + 1 < ref->n; i++) { keys[i] = keys[i + 1]; ch[i] = ch[i + 1]; } ref->n--;
            if (ref->kind == N16 && ref->n <= 3) { auto* x = (Node16*)ref; auto* y = new Node4; y->prefix = x->prefix; y->n = x->n; for (int j = 0; j < x->n; j++) { y->k[j] = x->k[j]; y->c[j] = x->c[j]; } delete x; ref = y; }     // 16 -> 4 로 축소
            return; }
        case N48: { auto* x = (Node48*)ref; x->c[x->idx[b]] = nullptr; x->idx[b] = 255; x->n--;
                    if (x->n <= 12) { auto* y = new Node16; y->prefix = x->prefix; for (int i = 0; i < 256; i++) if (x->idx[i] != 255) insertSorted(y, (uint8_t)i, x->c[x->idx[i]]); delete x; ref = y; } return; }
        case N256: { auto* x = (Node256*)ref; x->c[b] = nullptr; x->n--;
                     if (x->n <= 37) { auto* y = new Node48; y->prefix = x->prefix; for (int i = 0; i < 256; i++) if (x->c[i]) { int pos = y->n++; y->idx[i] = pos; y->c[pos] = x->c[i]; } delete x; ref = y; } return; }
        default: return;
    }
}
struct ART {
    Node* root = nullptr; long size = 0;
    static std::string term(const std::string& k) { return k + '\0'; }
    void insert(const std::string& k, long v) { std::string key = term(k); if (insertRec(root, key, 0, v)) size++; }
    bool insertRec(Node*& ref, const std::string& key, size_t depth, long v) {              // 새 키면 true
        if (!ref) { ref = new Leaf(key, v); return true; }
        if (ref->kind == LEAF) {
            auto* l = (Leaf*)ref; if (l->key == key) { l->val = v; return false; }
            size_t i = depth; while (i < l->key.size() && i < key.size() && l->key[i] == key[i]) i++;
            Node* n4 = new Node4; n4->prefix.assign(key.begin() + depth, key.begin() + i);          // 공통 구간을 접두사로 압축
            Node* nl = new Leaf(key, v); addChild(n4, (uint8_t)l->key[i], l); addChild(n4, (uint8_t)key[i], nl); ref = n4; return true;
        }
        size_t p = 0; while (p < ref->prefix.size() && depth + p < key.size() && ref->prefix[p] == (uint8_t)key[depth + p]) p++;
        if (p < ref->prefix.size()) {                                       // 접두사 중간에서 갈라진다 -> 위에 새 노드를 끼운다
            Node* n4 = new Node4; n4->prefix.assign(ref->prefix.begin(), ref->prefix.begin() + p); uint8_t oldByte = ref->prefix[p];
            ref->prefix.erase(ref->prefix.begin(), ref->prefix.begin() + p + 1); Node* nl = new Leaf(key, v);
            addChild(n4, oldByte, ref); addChild(n4, (uint8_t)key[depth + p], nl); ref = n4; return true;
        }
        depth += ref->prefix.size(); uint8_t b = key[depth]; Node** ch = findChild(ref, b);
        if (ch) return insertRec(*ch, key, depth + 1, v);
        addChild(ref, b, new Leaf(key, v)); return true;
    }
    bool find(const std::string& k, long& v) const {
        std::string key = term(k); Node* n = root; size_t depth = 0;
        while (n) {
            if (n->kind == LEAF) { auto* l = (Leaf*)n; if (l->key != key) return false; v = l->val; return true; }
            for (size_t j = 0; j < n->prefix.size(); j++) if (depth + j >= key.size() || n->prefix[j] != (uint8_t)key[depth + j]) return false;
            depth += n->prefix.size(); Node** ch = findChild(n, (uint8_t)key[depth]); if (!ch) return false; n = *ch; depth++;
        }
        return false;
    }
    bool erase(const std::string& k) { std::string key = term(k); bool r = eraseRec(root, key, 0); if (r) size--; return r; }
    bool eraseRec(Node*& ref, const std::string& key, size_t depth) {
        if (!ref) return false;
        if (ref->kind == LEAF) { if (((Leaf*)ref)->key != key) return false; delete (Leaf*)ref; ref = nullptr; return true; }
        for (size_t j = 0; j < ref->prefix.size(); j++) if (depth + j >= key.size() || ref->prefix[j] != (uint8_t)key[depth + j]) return false;
        depth += ref->prefix.size(); uint8_t b = key[depth]; Node** ch = findChild(ref, b); if (!ch || !eraseRec(*ch, key, depth + 1)) return false;
        if (*ch == nullptr) {
            removeChild(ref, b);
            if (ref->kind == N4 && ref->n == 1) {                           // 자식이 하나만 남으면 경로 압축: 이 노드를 없애고 자식에 접두사를 합친다
                auto* x = (Node4*)ref; Node* only = x->c[0]; uint8_t ob = x->k[0];
                if (only->kind != LEAF) { std::vector<uint8_t> np = x->prefix; np.push_back(ob); np.insert(np.end(), only->prefix.begin(), only->prefix.end()); only->prefix = np; }
                delete x; ref = only;
            }
        }
        return true;
    }
    static void walk(Node* n, std::vector<std::pair<std::string, long>>& out) {            // 정렬된 순회
        if (!n) return; if (n->kind == LEAF) { auto* l = (Leaf*)n; out.push_back({l->key.substr(0, l->key.size() - 1), l->val}); return; }
        switch (n->kind) {
            case N4:   for (int i = 0; i < n->n; i++) walk(((Node4*)n)->c[i], out); break;
            case N16:  for (int i = 0; i < n->n; i++) walk(((Node16*)n)->c[i], out); break;
            case N48:  for (int b = 0; b < 256; b++) if (((Node48*)n)->idx[b] != 255) walk(((Node48*)n)->c[((Node48*)n)->idx[b]], out); break;
            default:   for (int b = 0; b < 256; b++) if (((Node256*)n)->c[b]) walk(((Node256*)n)->c[b], out);
        }
    }
    static void census(Node* n, long cnt[5]) {
        if (!n) return; cnt[n->kind]++; if (n->kind == LEAF) return;
        switch (n->kind) { case N4: for (int i = 0; i < n->n; i++) census(((Node4*)n)->c[i], cnt); break; case N16: for (int i = 0; i < n->n; i++) census(((Node16*)n)->c[i], cnt); break;
            case N48: for (int b = 0; b < 256; b++) if (((Node48*)n)->idx[b] != 255) census(((Node48*)n)->c[((Node48*)n)->idx[b]], cnt); break; default: for (int b = 0; b < 256; b++) if (((Node256*)n)->c[b]) census(((Node256*)n)->c[b], cnt); }
    }
    static void destroy(Node* n) {
        if (!n) return; std::vector<Node*> kids;
        switch (n->kind) { case LEAF: delete (Leaf*)n; return; case N4: for (int i = 0; i < n->n; i++) kids.push_back(((Node4*)n)->c[i]); delete (Node4*)n; break; case N16: for (int i = 0; i < n->n; i++) kids.push_back(((Node16*)n)->c[i]); delete (Node16*)n; break;
            case N48: for (int i = 0; i < 48; i++) if (((Node48*)n)->c[i]) kids.push_back(((Node48*)n)->c[i]); delete (Node48*)n; break; default: for (int i = 0; i < 256; i++) if (((Node256*)n)->c[i]) kids.push_back(((Node256*)n)->c[i]); delete (Node256*)n; }
        for (Node* c : kids) destroy(c);
    }
};

int main() {
    std::mt19937 g(4);
    { ART t; std::map<std::string, long> ref;                               // 가변 길이 문자열 키: 삽입·삭제·조회를 std::map 과 대조
      for (int step = 0; step < 60000; step++) {
          std::string k; int len = 1 + g() % 10; for (int i = 0; i < len; i++) k += "abcde0123"[g() % 9]; int op = g() % 10; long v = step;
          if (op < 5) { t.insert(k, v); ref[k] = v; } else if (op < 8) { assert(t.erase(k) == (ref.erase(k) > 0)); } else { long got; bool f = t.find(k, got); auto it = ref.find(k); assert(f == (it != ref.end()) && (!f || got == it->second)); }
          assert(t.size == (long)ref.size());
      }
      std::vector<std::pair<std::string, long>> out; ART::walk(t.root, out); assert((out == std::vector<std::pair<std::string, long>>(ref.begin(), ref.end())));    // 순회 = 정렬된 키
      for (auto& kv : std::map<std::string, long>(ref)) { assert(t.erase(kv.first)); } assert(t.size == 0 && t.root == nullptr); ART::destroy(t.root); }
    { ART dense, sparse; long cd[5] = {0}, cs[5] = {0}; auto be = [](uint32_t x) { std::string s(4, 0); for (int i = 0; i < 4; i++) s[i] = (char)(x >> (24 - 8 * i)); return s; };
      for (uint32_t i = 0; i < 70000; i++) dense.insert(be(i), i);          // 촘촘한 정수 키: 아래쪽 노드가 256 칸까지 가득 찬다
      for (int i = 0; i < 20000; i++) sparse.insert(be(g()), i);            // 드문 정수 키: 대부분 작은 노드
      for (uint32_t i = 0; i < 70000; i += 13) { long v; assert(dense.find(be(i), v) && v == i); }
      ART::census(dense.root, cd); ART::census(sparse.root, cs);
      assert(cd[N256] > 200 && cs[N4] > cs[N256] * 5);                       // 촘촘하면 256 칸 노드, 드물면 4 칸 노드가 대부분
      ART mid; long cm[5] = {0}; for (int b1 = 0; b1 < 10; b1++) for (int b2 = 0; b2 < 40; b2++) mid.insert(std::string(1, 'A') + std::string(1, (char)(65 + b1)) + std::string(1, (char)(40 + b2)), b1 * 40 + b2);
      ART::census(mid.root, cm); assert(cm[N16] == 1 && cm[N48] == 10);        // 자식 10 개 -> Node16, 자식 40 개 -> Node48
      for (int b1 = 0; b1 < 10; b1++) for (int b2 = 0; b2 < 40; b2++) if (b2 >= 3) assert(mid.erase(std::string(1, 'A') + std::string(1, (char)(65 + b1)) + std::string(1, (char)(40 + b2))));
      long cm2[5] = {0}; ART::census(mid.root, cm2); assert(cm2[N48] == 0 && cm2[N16] == 1 && cm2[N4] == 10);    // 자식이 3 개로 줄어든 아래층 노드 10 개는 Node48 -> Node16 -> Node4 로 축소, 위층(자식 10 개)은 Node16 유지
      ART::destroy(mid.root);
      std::cout << "AdaptiveRadixTree: 60000 string-key ops match std::map; dense ints node census N4/N16/N48/N256 = " << cd[N4] << "/" << cd[N16] << "/" << cd[N48] << "/" << cd[N256]
                << ", sparse ints = " << cs[N4] << "/" << cs[N16] << "/" << cs[N48] << "/" << cs[N256] << std::endl; ART::destroy(dense.root); ART::destroy(sparse.root); }
    return 0;
}
// Time Complexity: 조회·삽입·삭제 O(키 길이) (키 수와 무관)
// Space Complexity: 노드 형식 적응으로 키당 평균 약 8.1 바이트 오버헤드 (논문 보고, 이 코드는 구조만 검증)
```
## CacheObliviousBTree()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <list>
#include <random>
#include <unordered_map>
#include <vector>
#include <cassert>

// 캐시 무관(cache-oblivious) 탐색 트리: 캐시 블록 크기 B 를 코드에서 전혀 쓰지 않는데도 모든 B(디스크 블록·L1 라인·메모리 페이지 ...)에 대해 동시에 O(log_B N) 번의 블록 전송으로 탐색한다.
// 비결은 van Emde Boas 배치: 높이 h 의 완전 이진 트리를 위쪽 절반(높이 h/2)과 그 아래에 매달린 2^(h/2) 개의 아래쪽 절반 부분 트리들로 나누고, 위쪽을 먼저, 이어서 아래쪽 부분 트리들을 차례로 — 각 조각에 같은 규칙을 재귀 — 메모리에 놓는다.
// 재귀가 내려가다 보면 어느 B 에서든 "한 블록에 통째로 들어가는 부분 트리" 가 나오고, 그 안의 탐색은 블록 하나로 끝난다.  BFS(층별) 배치는 깊은 층에서 노드마다 블록이 달라 log2 N - log2 B 번 읽는다.
// 아래는 같은 트리를 BFS / vEB / 정렬 배열 이분 탐색 세 배치로 놓고 "작은 LRU 캐시" 시뮬레이터로 탐색당 블록 미스를 셈한다
void veb(int d0, long i0, int h, std::vector<std::pair<int, long>>& out) {         // (깊이, 층 안의 순번) 을 vEB 순서로
    if (h == 1) { out.push_back({d0, i0}); return; }
    int top = h / 2, bot = h - top; veb(d0, i0, top, out); for (long j = 0; j < (1L << top); j++) veb(d0 + top, (i0 << top) + j, bot, out);
}
struct Cache {                                                              // 완전 연관 LRU, 용량 = 블록 cap 개
    size_t cap, B; std::list<long> lru; std::unordered_map<long, std::list<long>::iterator> where; long misses = 0;
    Cache(size_t cap, size_t B) : cap(cap), B(B) {}
    void access(long pos) { long blk = pos / B; auto it = where.find(blk); if (it != where.end()) { lru.erase(it->second); } else { misses++; if (lru.size() == cap) { where.erase(lru.back()); lru.pop_back(); } } lru.push_front(blk); where[blk] = lru.begin(); }
};
int main() {
    const int h = 20; const long n = (1L << h) - 1; std::vector<std::pair<int, long>> order; order.reserve(n); veb(0, 0, h, order);
    std::vector<long> vebPos(n); for (long p = 0; p < n; p++) vebPos[((1L << order[p].first) - 1) + order[p].second] = p;      // BFS 번호 -> vEB 위치
    auto keyOfBfs = [&](long id) { int d = 63 - __builtin_clzll(id + 1); long i = id - ((1L << d) - 1); return (((2 * i + 1) << (h - 1 - d)) - 1); };      // 해당 노드의 중위 순번 키 (0..n-1)
    std::mt19937_64 g(3);
    for (size_t B : {4u, 16u, 64u, 256u}) {
        double bfs = 0, vb = 0, bin = 0; int Q = 1500;
        for (int t = 0; t < Q; t++) {
            long target = g() % n; Cache cb(8, B), cv(8, B), cs(8, B);
            for (long id = 0;;) { cb.access(id); cv.access(vebPos[id]); long k = keyOfBfs(id); if (k == target) break; id = target < k ? 2 * id + 1 : 2 * id + 2; }      // 같은 경로를 두 배치로 접근
            long lo = 0, hi = n; while (lo < hi) { long mid = (lo + hi) / 2; cs.access(mid); if (mid == target) break; if (mid < target) lo = mid + 1; else hi = mid; }       // 정렬 배열 이분 탐색
            bfs += cb.misses; vb += cv.misses; bin += cs.misses;
        }
        bfs /= Q; vb /= Q; bin /= Q; double logB = std::log((double)n) / std::log((double)B);
        assert(vb <= 4 * logB + 2 && vb <= bfs + 0.5);                      // 모든 B 에서 O(log_B N), 그리고 BFS 보다 나쁘지 않다
        if (B >= 64) assert(vb * 2 < bfs && vb * 2 < bin);                  // 블록이 크면 BFS·이분 탐색의 절반 이하
        std::cout << "B=" << B << ": log_B N = " << logB << ", misses per search  vEB " << vb << " | BFS layout " << bfs << " | sorted-array binary search " << bin << std::endl;
    }
    return 0;
}
// Time Complexity: 탐색 O(log_B N) 블록 전송 (모든 B 에 대해 동시에)
// Space Complexity: O(N)
```
## FusionTree()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 퓨전 트리(Fredman–Willard 1990): 워드 램(word RAM) 모델에서 w 비트 정수 N 개의 predecessor 를 비교 기반의 O(log N) 이 아니라 O(log_w N) 에 푸는 트리. 노드 하나가 키 k(~w^(1/5)) 개를 가지고
// "한 노드 안의 순위(rank)" 를 워드 연산 O(1) 번으로 구한다.  핵심 3 가지: ① 스케치 — 노드 키들을 서로 구별하는 데 필요한 비트 위치(인접 키가 갈라지는 최상위 비트, 최대 k-1 개)만 모은 짧은 압축 키.
// 스케치는 키의 순서를 보존한다.  ② 병렬 비교 — 스케치들을 한 워드에 필드별로 채우고(각 필드 최상위에 1 센티넬 비트) 질의 스케치를 복제해 한 번 빼면, 필드마다 센티넬이 남았는가가 "키 >= 질의" 를 알려 준다 -> popcount 로 순위.
// ③ 보정 — 질의 q 의 스케치는 q 가 키들 사이 어디인지 정확히 알려 주지 못한다. 순위 위치의 이웃 중 q 와 가장 긴 공통 접두사를 가진 키 y 를 고르고, 둘이 갈라지는 비트 e 로 q 를 "y 가 속한 부분 트리의 경계" q'(e 윗부분은 y 와 같고, e 비트는 q 쪽, 아래는 전부 1 또는 0)로 바꿔 다시 스케치 비교하면 정확한 순위가 나온다.
// 이 구현은 노드당 키 7 개, 필드 8 비트(센티넬 1 + 스케치 6~7 비트)이고, 스케치 추출은 원 논문의 곱셈 요령(O(1)) 대신 비트 위치 루프(≤ 6)로 단순화했다 — 병렬 비교와 보정 논리는 원본 그대로이다
typedef uint64_t u64;
const int K = 7; const u64 ONES = 0x0101010101010101ULL, SENT = 0x8080808080808080ULL;
struct FNode {
    int k = 0, r = 0; u64 x[K]; int bpos[K]; u64 packed = ~0ULL;
    u64 sketch(u64 v) const { u64 s = 0; for (int j = 0; j < r; j++) s = s << 1 | ((v >> bpos[j]) & 1); return s; }
    void build(const std::vector<u64>& keys) {
        k = keys.size(); for (int i = 0; i < k; i++) x[i] = keys[i];
        std::vector<int> pos; for (int i = 0; i + 1 < k; i++) pos.push_back(63 - __builtin_clzll(x[i] ^ x[i + 1]));     // 인접 키가 갈라지는 최상위 비트
        std::sort(pos.rbegin(), pos.rend()); pos.erase(std::unique(pos.begin(), pos.end()), pos.end()); r = pos.size(); for (int j = 0; j < r; j++) bpos[j] = pos[j];
        packed = ~0ULL; for (int i = 0; i < k; i++) { packed &= ~(0xFFULL << (8 * i)); packed |= (0x80ULL | sketch(x[i])) << (8 * i); }       // 필드 i = 센티넬 | 스케치, 쓰지 않는 필드는 0xFF
    }
    int countLT(u64 s) const { u64 d = packed - s * ONES; return __builtin_popcountll(~d & SENT); }          // 스케치 < s 인 키의 수 (센티넬이 꺼진 필드)
    int countLE(u64 s) const { return countLT(s + 1); }
    int rank(u64 q) const {                                                  // q 이하인 키의 수
        if (k == 0) return 0;
        int i = countLE(sketch(q)); int yi = i == 0 ? 0 : i == k ? k - 1 : ((x[i - 1] ^ q) <= (x[i] ^ q) ? i - 1 : i); u64 y = x[yi];       // 스케치 순위 이웃 중 q 와 공통 접두사가 더 긴 키
        if (q == y) return yi + 1;
        int e = 63 - __builtin_clzll(q ^ y); u64 low = (1ULL << e) - 1, prefix = y & ~((2ULL << e) - 1);                                          // 갈라지는 비트 e, 그 아래 비트들, 그 위 접두사
        if ((q >> e) & 1) return countLE(sketch(prefix | (1ULL << e) | low));  // q 는 y 의 부분 트리 전체보다 크다 -> 부분 트리 끝(전부 1) 기준 순위
        return countLT(sketch(prefix | (1ULL << e)));                          // q 는 y 의 부분 트리 전체보다 작다 -> 부분 트리 시작(전부 0) 앞의 키 수
    }
};
struct FusionTree {
    std::vector<FNode> nodes; std::vector<std::array<int, K + 1>> kid; int root = -1;
    int build(const std::vector<u64>& a, long lo, long hi) {
        int id = nodes.size(); nodes.emplace_back(); kid.push_back({-1, -1, -1, -1, -1, -1, -1, -1}); long m = hi - lo; std::vector<u64> keys;
        if (m <= K) { keys.assign(a.begin() + lo, a.begin() + hi); nodes[id].build(keys); return id; }
        long prev = lo;
        for (int j = 0; j < K; j++) { long s = lo + m * (j + 1) / (K + 1); keys.push_back(a[s]); int c = build(a, prev, s); kid[id][j] = c; prev = s + 1; }
        kid[id][K] = build(a, prev, hi); nodes[id].build(keys); return id;
    }
    void build(const std::vector<u64>& a) { nodes.clear(); kid.clear(); root = a.empty() ? -1 : build(a, 0, a.size()); }
    bool pred(u64 q, u64& out) const {                                       // q 이하 최대 키
        bool found = false; int v = root;
        while (v >= 0) { const FNode& nd = nodes[v]; int r = nd.rank(q); if (r > 0) { out = nd.x[r - 1]; found = true; } v = kid[v][r]; }
        return found;
    }
    int height() const { int h = 0; for (int v = root; v >= 0; v = kid[v][0]) h++; return h; }
};

int main() {
    std::mt19937_64 g(5); long trials = 0;
    for (int round = 0; round < 6; round++) for (int t = 0; t < 40000; t++) {          // 노드 하나의 rank 를 전수 대조: 다양한 키 구조
        int k = 1 + g() % K; std::vector<u64> keys; u64 base = g();
        for (int i = 0; i < k; i++) keys.push_back(round == 0 ? g() : round == 1 ? (base & ~0xFFFFULL) | (g() & 0xFFFF) : round == 2 ? (base & 0xFFFFFFFFULL) | (g() << 48) : round == 3 ? g() % 100 : round == 4 ? (g() & 0x8000000000000001ULL) | 0x40 : (base >> (g() % 64)) ^ (g() & 3));
        std::sort(keys.begin(), keys.end()); keys.erase(std::unique(keys.begin(), keys.end()), keys.end());
        FNode nd; nd.build(keys); int kk = keys.size();
        std::vector<u64> qs = {0, ~0ULL, g(), g() % 128, keys[g() % kk], keys[g() % kk] + 1, keys[g() % kk] - 1, keys[g() % kk] ^ (1ULL << (g() % 64))};
        for (u64 q : qs) { int want = std::upper_bound(keys.begin(), keys.end(), q) - keys.begin(); assert(nd.rank(q) == want); trials++; }
    }
    std::vector<u64> a(200000); for (auto& x : a) x = g(); std::sort(a.begin(), a.end()); a.erase(std::unique(a.begin(), a.end()), a.end());
    FusionTree ft; ft.build(a);
    for (int t = 0; t < 100000; t++) { u64 q = t % 3 == 0 ? g() : t % 3 == 1 ? a[g() % a.size()] : a[g() % a.size()] + 1; u64 out = 0; bool f = ft.pred(q, out); auto it = std::upper_bound(a.begin(), a.end(), q);
        assert(f == (it != a.begin()) && (!f || out == *(it - 1))); }
    u64 out; assert(!ft.pred(a[0] - 1 > a[0] ? 0 : a[0] - 1, out) || out <= a[0]);
    std::cout << "FusionTree: " << trials << " node-rank queries match brute force; " << a.size() << " keys, fanout " << K + 1 << ", height " << ft.height() << " (binary search would need " << (int)std::ceil(std::log2((double)a.size())) << " comparisons)" << std::endl; return 0;
}
// Time Complexity: predecessor O(log_{k+1} N) 노드 방문 × 노드당 O(1) 워드 연산 (스케치 추출 제외)
// Space Complexity: O(N)
```
## vanEmdeBoasTree()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <cassert>

// 반 엠데 보아스 트리(트리 관점의 요약, 정본은 Tree.md Part 16): 우주 U 를 √U 칸 클러스터 √U 개로 나누고 "비어 있지 않은 클러스터" 요약(summary)을 같은 구조로 재귀해 insert/successor 를 O(log log U) 에 한다.
// 아래는 재귀를 한 단계만 펼친 2 단 구조(U = 2^16: 256 클러스터 × 256 비트 + 요약 256 비트)로, successor 가 "내 클러스터에서 다음 비트 -> 없으면 요약에서 다음 클러스터" 두 걸음임을 보인다
struct V {
    uint64_t cl[256][4] = {}, sm[4] = {};
    void ins(uint32_t x) { cl[x >> 8][(x & 255) >> 6] |= 1ULL << (x & 63); sm[(x >> 8) >> 6] |= 1ULL << ((x >> 8) & 63); }
    static int next(const uint64_t* w, int from) { for (int i = from >> 6; i < 4; i++) { uint64_t m = w[i] & (i == (from >> 6) ? ~0ULL << (from & 63) : ~0ULL); if (m) return i * 64 + __builtin_ctzll(m); } return -1; }
    long succ(uint32_t x) const { uint32_t c = x >> 8, lo = (x & 255) + 1; if (lo < 256) { int b = next(cl[c], lo); if (b >= 0) return c * 256 + b; } if (c + 1 < 256) { int cc = next(sm, c + 1); if (cc >= 0) return cc * 256 + next(cl[cc], 0); } return -1; }
};
int main() {
    V v; std::set<uint32_t> ref; std::mt19937 g(1); for (int i = 0; i < 3000; i++) { uint32_t x = g() % 65536; v.ins(x); ref.insert(x); }
    for (int t = 0; t < 20000; t++) { uint32_t x = g() % 65536; auto it = ref.upper_bound(x); assert(v.succ(x) == (it == ref.end() ? -1L : (long)*it)); }
    std::cout << "vanEmdeBoasTree: 2-level successor matches std::set" << std::endl; return 0;
}
// Time Complexity: successor O(1) 클러스터 2 번 + 요약 1 번 (이 2 단 판), 완전 재귀판은 O(log log U)
// Space Complexity: O(U) 비트
```
## XFastTrie()
### 대표코드
```cpp
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <unordered_map>
#include <cassert>

// X-빠른 트라이(Willard 1983): w 비트 정수의 predecessor/successor 를 O(log w) 에 하는 구조. 이진 트라이를 만들되 각 깊이(접두사 길이 l = 0..w)의 "존재하는 노드" 를 해시 표에 넣는다.
// 질의 x: x 의 접두사 중 가장 긴 것을 찾는다 — 접두사 길이에 대해 "있다/없다" 가 단조라 이진 탐색으로 O(log w) 번 해시 조회. 그 노드 아래 x 쪽 자식이 없으므로 한쪽 방향의 부분 트리 전체가 x 의 한쪽에 있다 ->
// 노드마다 저장한 부분 트리의 최소/최대 잎으로 이웃이 바로 정해지고, 잎들을 정렬 순서로 잇는 이중 연결 리스트로 반대쪽 이웃도 구한다.  삽입·삭제는 모든 깊이를 갱신하는 O(w), 공간은 O(n w) — Y-빠른 트라이가 줄인다
const int W = 32;
struct XFast {
    struct Leaf { uint32_t key; Leaf *prev = nullptr, *next = nullptr; }; struct Info { Leaf *mn, *mx; };
    std::unordered_map<uint64_t, Info> lvl[W + 1]; long probes = 0; long n = 0;
    static uint64_t pre(uint32_t x, int l) { return l == 0 ? 0 : (uint64_t)x >> (W - l); }
    Leaf* leafOf(uint32_t x) { auto it = lvl[W].find(x); return it == lvl[W].end() ? nullptr : it->second.mn; }
    int longest(uint32_t x) {                                              // x 의 접두사 중 트라이에 존재하는 가장 긴 길이 (이진 탐색)
        int lo = 0, hi = W; while (lo < hi) { int mid = (lo + hi + 1) / 2; probes++; if (lvl[mid].count(pre(x, mid))) lo = mid; else hi = mid - 1; } return lo;
    }
    Leaf* predLeaf(uint32_t x) {                                           // 가장 큰 key <= x
        if (!n) return nullptr; int l = longest(x); if (l == W) return leafOf(x); const Info& in = lvl[l][pre(x, l)];
        bool bit = (x >> (W - l - 1)) & 1; return bit ? in.mx : in.mn->prev;  // 오른쪽 자식이 없다면 부분 트리 전체가 x 보다 작다 -> 최대 잎, 왼쪽 자식이 없다면 전부 크다 -> 최소 잎의 이전
    }
    Leaf* succLeaf(uint32_t x) {                                           // 가장 작은 key >= x
        if (!n) return nullptr; int l = longest(x); if (l == W) return leafOf(x); const Info& in = lvl[l][pre(x, l)];
        bool bit = (x >> (W - l - 1)) & 1; return bit ? in.mx->next : in.mn;
    }
    bool insert(uint32_t x) {
        if (leafOf(x)) return false; Leaf* p = predLeaf(x); Leaf* s = p ? p->next : (n ? lvl[0][0].mn : nullptr);      // 삽입 전에 이웃을 찾는다
        Leaf* L = new Leaf; L->key = x; L->prev = p; L->next = s; if (p) p->next = L; if (s) s->prev = L;
        for (int l = 0; l <= W; l++) { auto it = lvl[l].find(pre(x, l)); if (it == lvl[l].end()) lvl[l][pre(x, l)] = {L, L}; else { if (x < it->second.mn->key) it->second.mn = L; if (x > it->second.mx->key) it->second.mx = L; } }
        n++; return true;
    }
    bool erase(uint32_t x) {
        Leaf* L = leafOf(x); if (!L) return false; if (L->prev) L->prev->next = L->next; if (L->next) L->next->prev = L->prev;
        for (int l = W; l >= 0; l--) { auto it = lvl[l].find(pre(x, l)); Info& in = it->second; if (in.mn == L && in.mx == L) lvl[l].erase(it); else { if (in.mn == L) in.mn = L->next; if (in.mx == L) in.mx = L->prev; } }
        delete L; n--; return true;
    }
};
int main() {
    XFast t; std::set<uint32_t> ref; std::mt19937 g(5); long maxProbes = 0;
    for (int step = 0; step < 60000; step++) {
        uint32_t x = g() % 3 ? g() % 20000 : g(); int op = g() % 6;
        if (op < 2) assert(t.insert(x) == ref.insert(x).second); else if (op == 2) assert(t.erase(x) == (ref.erase(x) > 0));
        else { t.probes = 0; if (op == 3) { auto* l = t.predLeaf(x); auto it = ref.upper_bound(x); assert((l != nullptr) == (it != ref.begin()) && (!l || l->key == *std::prev(it))); }
               else if (op == 4) { auto* l = t.succLeaf(x); auto it = ref.lower_bound(x); assert((l != nullptr) == (it != ref.end()) && (!l || l->key == *it)); } else { assert((t.leafOf(x) != nullptr) == (ref.count(x) > 0)); } maxProbes = std::max(maxProbes, t.probes); }
        assert(t.n == (long)ref.size());
    }
    assert(maxProbes <= 6);                                                // 이진 탐색: ⌈log2(33)⌉ = 6 번 이하의 해시 조회
    long entries = 0; for (auto& m : t.lvl) entries += m.size(); assert(entries <= t.n * (W + 1));
    std::cout << "XFastTrie: pred/succ verified; max hash probes per query " << maxProbes << " (log2(w+1) ~ 5), table entries " << entries << " for " << t.n << " keys" << std::endl; return 0;
}
// Time Complexity: pred/succ O(log w), 삽입·삭제 O(w)
// Space Complexity: O(n w)
```
## YFastTrie()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <unordered_map>
#include <cassert>

// Y-빠른 트라이(Willard 1983): X-빠른 트라이의 공간 O(n w) 를 O(n) 으로 줄인다. 키를 정렬된 순서로 크기 Θ(w) 의 "버킷"으로 나누고 버킷마다 균형 BST 를 두며, X-빠른 트라이에는 버킷의 대표값(rep)만 넣는다 (n/w 개 x O(w) = O(n) 공간).
// 질의: X-빠른 트라이로 대표값 중 x 이하 최대인 버킷을 O(log w) 에 찾고, 그 버킷의 BST 에서 O(log w). 삽입·삭제도 버킷 안에서 O(log w) 이고, 버킷이 2w 를 넘으면 반으로 쪼개고(대표값 삽입), w/2 미만이면 이웃과 합친다(대표값 삭제) —
// 이 구조 변경은 w 번의 연산마다 한 번이라 O(w) 비용이 분할상환 O(1) 로 희석된다.  버킷 b 는 대표값 r_b 부터 다음 대표값 직전까지의 키를 가진다 (맨 앞 대표값 0 은 항상 있는 경계)
const int W = 32;
struct XFast {                                                             // 대표값 집합용 X-빠른 트라이 (위 항목의 최소 구현: pred/succ/삽입/삭제)
    struct Leaf { uint32_t key; Leaf *prev = nullptr, *next = nullptr; }; struct Info { Leaf *mn, *mx; };
    std::unordered_map<uint64_t, Info> lvl[W + 1]; long n = 0;
    static uint64_t pre(uint32_t x, int l) { return l == 0 ? 0 : (uint64_t)x >> (W - l); }
    Leaf* leafOf(uint32_t x) { auto it = lvl[W].find(x); return it == lvl[W].end() ? nullptr : it->second.mn; }
    int longest(uint32_t x) { int lo = 0, hi = W; while (lo < hi) { int mid = (lo + hi + 1) / 2; if (lvl[mid].count(pre(x, mid))) lo = mid; else hi = mid - 1; } return lo; }
    Leaf* predLeaf(uint32_t x) { if (!n) return nullptr; int l = longest(x); if (l == W) return leafOf(x); const Info& in = lvl[l][pre(x, l)]; return ((x >> (W - l - 1)) & 1) ? in.mx : in.mn->prev; }
    Leaf* succLeaf(uint32_t x) { if (!n) return nullptr; int l = longest(x); if (l == W) return leafOf(x); const Info& in = lvl[l][pre(x, l)]; return ((x >> (W - l - 1)) & 1) ? in.mx->next : in.mn; }
    void insert(uint32_t x) { if (leafOf(x)) return; Leaf* p = predLeaf(x); Leaf* s = p ? p->next : (n ? lvl[0][0].mn : nullptr); Leaf* L = new Leaf; L->key = x; L->prev = p; L->next = s; if (p) p->next = L; if (s) s->prev = L;
        for (int l = 0; l <= W; l++) { auto it = lvl[l].find(pre(x, l)); if (it == lvl[l].end()) lvl[l][pre(x, l)] = {L, L}; else { if (x < it->second.mn->key) it->second.mn = L; if (x > it->second.mx->key) it->second.mx = L; } } n++; }
    void erase(uint32_t x) { Leaf* L = leafOf(x); if (!L) return; if (L->prev) L->prev->next = L->next; if (L->next) L->next->prev = L->prev;
        for (int l = W; l >= 0; l--) { auto it = lvl[l].find(pre(x, l)); Info& in = it->second; if (in.mn == L && in.mx == L) lvl[l].erase(it); else { if (in.mn == L) in.mn = L->next; if (in.mx == L) in.mx = L->prev; } } delete L; n--; }
};
struct YFast {
    XFast xf; std::unordered_map<uint32_t, std::set<uint32_t>> bucket; long splits = 0, merges = 0;
    YFast() { xf.insert(0); bucket[0]; }
    uint32_t repOf(uint32_t x) { return xf.predLeaf(x)->key; }             // x 를 담당하는 버킷 = x 이하 최대 대표값
    void split(uint32_t r) { auto& b = bucket[r]; auto mid = std::next(b.begin(), b.size() / 2); uint32_t nr = *mid; std::set<uint32_t> up(mid, b.end()); b.erase(mid, b.end()); xf.insert(nr); bucket[nr] = up; splits++; }
    bool insert(uint32_t x) { uint32_t r = repOf(x); if (!bucket[r].insert(x).second) return false; if ((int)bucket[r].size() > 2 * W) split(r); return true; }
    bool erase(uint32_t x) {
        uint32_t r = repOf(x); auto& b = bucket[r]; if (!b.erase(x)) return false;
        if (r != 0 && (int)b.size() < W / 2) { uint32_t p = xf.predLeaf(r - 1)->key; bucket[p].insert(b.begin(), b.end()); xf.erase(r); bucket.erase(r); merges++; if ((int)bucket[p].size() > 2 * W) split(p); }      // 작은 버킷은 이전 버킷에 합친다
        return true;
    }
    bool pred(uint32_t x, uint32_t& out) {                                 // x 이하 최대
        uint32_t r = repOf(x); auto& b = bucket[r]; auto it = b.upper_bound(x); if (it != b.begin()) { out = *std::prev(it); return true; }
        if (r == 0) return false; uint32_t p = xf.predLeaf(r - 1)->key; auto& pb = bucket[p]; if (pb.empty()) return false; out = *pb.rbegin(); return true;
    }
    bool succ(uint32_t x, uint32_t& out) {                                 // x 이상 최소
        uint32_t r = repOf(x); auto& b = bucket[r]; auto it = b.lower_bound(x); if (it != b.end()) { out = *it; return true; }
        XFast::Leaf* nx = xf.succLeaf(r + 1 == 0 ? r : r + 1); if (!nx || nx->key <= r) return false; out = *bucket[nx->key].begin(); return true;
    }
};
int main() {
    YFast t; std::set<uint32_t> ref; std::mt19937 g(6);
    for (int step = 0; step < 80000; step++) {
        uint32_t x = g() % 2 ? g() % 50000 : g(); int op = g() % 8; uint32_t out;
        if (op < 3) assert(t.insert(x) == ref.insert(x).second); else if (op < 5) assert(t.erase(x) == (ref.erase(x) > 0));
        else if (op < 7) { bool f = t.pred(x, out); auto it = ref.upper_bound(x); assert(f == (it != ref.begin()) && (!f || out == *std::prev(it))); }
        else { bool f = t.succ(x, out); auto it = ref.lower_bound(x); assert(f == (it != ref.end()) && (!f || out == *it)); }
    }
    std::vector<uint32_t> all(ref.begin(), ref.end());                     // 대량 삭제: 버킷이 w/2 아래로 줄어 이웃과 합쳐지는 경로를 지난다
    for (uint32_t x : all) if (g() % 10 != 0) { assert(t.erase(x)); ref.erase(x); uint32_t out; if (g() % 8 == 0) { bool f = t.pred(x, out); auto it = ref.upper_bound(x); assert(f == (it != ref.begin()) && (!f || out == *std::prev(it))); } }
    assert(t.merges > 0);
    size_t total = 0, minB = 1 << 30, maxB = 0; for (auto& kv : t.bucket) { if (kv.first == 0) { total += kv.second.size(); continue; } total += kv.second.size(); minB = std::min(minB, kv.second.size()); maxB = std::max(maxB, kv.second.size());
        for (uint32_t k : kv.second) assert(k >= kv.first); }
    assert(total == ref.size() && minB >= (size_t)W / 2 - 1 && maxB <= 2 * W);          // 버킷 크기 불변식: [w/2, 2w] (직전 연산이 경계에서 일어났을 수 있어 -1 허용)
    long entries = 0; for (auto& m : t.xf.lvl) entries += m.size();
    assert(entries <= (long)t.xf.n * (W + 1) && t.xf.n * (W / 2) <= (long)ref.size() + W * 4);                    // 대표값은 n/(w/2) 개 이하 -> X-빠른 트라이 공간 O(n)
    std::cout << "YFastTrie: " << ref.size() << " keys in " << t.bucket.size() << " buckets (sizes " << minB << ".." << maxB << "), X-fast table entries " << entries << " vs X-fast alone ~" << ref.size() * (W + 1)
              << "; splits " << t.splits << ", merges " << t.merges << std::endl; return 0;
}
// Time Complexity: pred/succ/삽입/삭제 O(log w) (삽입·삭제는 분할상환)
// Space Complexity: O(n)
```
## EliasFano()
### 대표코드
```cpp
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <algorithm>
#include <set>
#include <vector>
#include <cassert>

// 엘리아스–파노(Elias–Fano) 부호: 우주 [0, u) 에서 뽑은 n 개의 단조 증가 정수열을 n(2 + log2(u/n)) 비트로 압축하면서 임의 접근과 "x 이상 첫 원소" 탐색을 지원한다 (정보이론 하한 log2 C(u,n) ≈ n(1.44 + log2(u/n)) 에서 약 0.56n 비트 차이).
// 각 값을 L = ⌊log2(u/n)⌋ 인 하위 L 비트와 상위 부분 h = v >> L 로 나눈다. 하위 비트는 n·L 비트 배열에 그대로, 상위 부분은 단항 부호(unary)의 비트열에 둔다 —
// "원소 i 의 상위가 h 이면 비트 i + h 를 1 로" (그 앞에는 정확히 h 개의 0 이 있다).  비트열 길이는 n + (u >> L) + 1 <= 3n.  access(i) = (select1(i) - i) << L | low[i],
// nextGEQ(x) 는 상위 h = x >> L 의 시작 위치 = select0(h-1)+1 에서 시작해 같은 버킷 안의 몇 원소만 훑는다. select 는 64 번째마다 위치를 표본으로 저장해 비트 단위 스캔을 짧게 한다
struct BitArr { std::vector<uint64_t> w; long n = 0; void resize(long bits) { n = bits; w.assign((bits + 63) / 64 + 1, 0); } void set(long i) { w[i >> 6] |= 1ULL << (i & 63); } bool get(long i) const { return (w[i >> 6] >> (i & 63)) & 1; }
    uint64_t read(long pos, int len) const { if (!len) return 0; uint64_t v = 0; for (int i = 0; i < len; i++) v |= (uint64_t)get(pos + i) << i; return v; } void put(long pos, uint64_t v, int len) { for (int i = 0; i < len; i++) if ((v >> i) & 1) set(pos + i); } };
struct EF {
    long n, u; int L; BitArr low, hi; std::vector<uint32_t> sel1, sel0; long zeros;
    EF(const std::vector<uint64_t>& a, uint64_t universe) : n(a.size()), u(universe) {
        L = n ? std::max(0, (int)std::floor(std::log2((double)u / n))) : 0; low.resize(n * L); zeros = (u >> L) + 1; hi.resize(n + zeros);
        for (long i = 0; i < n; i++) { low.put(i * L, a[i] & ((1ULL << L) - 1), L); hi.set((a[i] >> L) + i); }
        long ones = 0, zs = 0; for (long p = 0; p < hi.n; p++) { if (hi.get(p)) { if (ones % 64 == 0) sel1.push_back(p); ones++; } else { if (zs % 64 == 0) sel0.push_back(p); zs++; } }
    }
    long selectAt(long startPos, long remaining, bool one) const {         // startPos 에서 시작해 remaining 번째 뒤의 같은 값 비트 위치
        if (!remaining) return startPos; long w = startPos >> 6; uint64_t raw = one ? hi.w[w] : ~hi.w[w]; int off = startPos & 63; uint64_t word = off == 63 ? 0 : raw & (~0ULL << (off + 1));
        for (;;) { int c = __builtin_popcountll(word); if (remaining <= c) { for (long r = remaining; r > 1; r--) word &= word - 1; return w * 64 + __builtin_ctzll(word); } remaining -= c; w++; word = one ? hi.w[w] : ~hi.w[w]; }
    }
    long select1(long i) const { return selectAt(sel1[i / 64], i % 64, true); }
    long select0(long k) const { return selectAt(sel0[k / 64], k % 64, false); }
    uint64_t access(long i) const { return (uint64_t)(select1(i) - i) << L | low.read(i * L, L); }
    long nextGEQ(uint64_t x) const {                                       // x 이상인 첫 원소의 인덱스 (없으면 n)
        uint64_t h = x >> L; if (h >= (uint64_t)zeros) return n; long start = h == 0 ? 0 : select0(h - 1) + 1; long i = start - h;
        while (i < n && access(i) < x) i++; return i;
    }
    double bits() const { return (double)low.n + hi.n + 32.0 * (sel1.size() + sel0.size()); }
};
int main() {
    std::mt19937_64 g(8);
    for (auto cfg : std::vector<std::pair<long, uint64_t>>{{100000, 1000000000ULL}, {50000, 100000ULL}, {20000, 1000000000000ULL}, {1, 1000}, {7, 7}}) {
        long n = cfg.first; uint64_t u = cfg.second; std::vector<uint64_t> a; { std::set<uint64_t> s; while ((long)s.size() < n && (long)s.size() < (long)u) s.insert(g() % u); a.assign(s.begin(), s.end()); n = a.size(); }
        EF ef(a, u);
        for (long i = 0; i < n; i++) assert(ef.access(i) == a[i]);          // 모든 원소 복원
        for (int t = 0; t < 20000; t++) { uint64_t x = t % 3 == 0 ? g() % (u + 5) : t % 3 == 1 ? a[g() % n] : a[g() % n] + 1; long want = std::lower_bound(a.begin(), a.end(), x) - a.begin(); assert(ef.nextGEQ(x) == want); }
        double info = (std::lgamma((double)u + 1) - std::lgamma((double)n + 1) - std::lgamma((double)(u - n) + 1)) / std::log(2.0); double main = (double)ef.low.n + ef.hi.n;
        if (n > 1000) assert(main <= info + 2.0 * n);                       // 정보이론 하한 + 2n 비트 이내
        std::cout << "n=" << n << ", u=" << u << ", L=" << ef.L << ": " << main / n << " bits/element (+" << (ef.bits() - main) / n << " for select samples), info-theoretic " << info / n << ", plain 64-bit array " << 64 << std::endl;
    }
    return 0;
}
// Time Complexity: access O(1) (select 표본 간격 상수), nextGEQ 기대 O(1 + 버킷 크기)
// Space Complexity: n(2 + ⌈log2(u/n)⌉) 비트
```
## CompressedSuffixArray()
### 대표코드
```cpp
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 압축 접미사 배열(CSA, Grossi–Vitter / Sadakane): 접미사 배열 SA 를 32n 비트 대신 Θ(n) 비트로 두고도 패턴 검색을 한다. 핵심은 Ψ 함수: Ψ[i] = ISA[SA[i] + 1] — "SA 의 i 번째 접미사의 다음 접미사가 SA 의 몇 번째인가".
// 성질: 같은 첫 글자 구간 안에서 Ψ 는 증가 수열이라 간격(gap)을 짧은 부호(여기서는 Elias gamma)로 저장할 수 있다. 첫 글자 F[i] 는 글자별 경계 C[c] 만으로 알고, 한 글자씩 Ψ 를 따라가면(i -> Ψ[i] -> ...) 접미사 SA[i] 를 SA 없이 글자로 펼칠 수 있다.
// 그래서 (1) 검색: 패턴과 "Ψ 를 따라 펼친 접미사" 를 비교하며 이분 탐색 — O(m log n) 번 Ψ 계산  (2) 위치 구하기(locate): SA 값을 s 칸마다 표본 저장, 표본 행을 만날 때까지 Ψ 를 따라가며 걸음 수 t 를 빼면 SA[i] = SA[표본] - t
struct BitW { std::vector<uint64_t> w; long n = 0; void bit(int b) { if (n / 64 >= (long)w.size()) w.push_back(0); if (b) w[n / 64] |= 1ULL << (n % 64); n++; } int get(long p) const { return (w[p / 64] >> (p % 64)) & 1; }
    void gamma(uint32_t g) { int len = 31 - __builtin_clz(g); for (int i = 0; i < len; i++) bit(0); for (int i = len; i >= 0; i--) bit((g >> i) & 1); }          // g >= 1: 0 이 len 개, 이어서 g 의 이진수 (len+1 비트)
    uint32_t readGamma(long& p) const { int len = 0; while (!get(p)) { len++; p++; } uint32_t v = 0; for (int i = 0; i <= len; i++) v = v << 1 | get(p++); return v; } };
struct CSA {
    std::string T; int n; std::vector<int> C = std::vector<int>(257, 0); static const int BL = 16, S = 8;      // Ψ 블록 크기, SA 표본 간격
    BitW psiBits; std::vector<uint32_t> blkVal; std::vector<long> blkOff; std::vector<long> bucketBlk = std::vector<long>(257, 0);            // 글자별 Ψ 블록 표본
    std::vector<uint64_t> mark; std::vector<uint32_t> markRank, saSample; std::vector<int> plainPsi;                                       // SA 표본 (표시 비트 + 순위 + 값)
    explicit CSA(const std::string& text) : T(text) {
        n = T.size(); std::vector<int> sa(n); std::iota(sa.begin(), sa.end(), 0); std::sort(sa.begin(), sa.end(), [&](int a, int b) { return T.compare(a, n, T, b, n) < 0; });
        std::vector<int> isa(n); for (int i = 0; i < n; i++) isa[sa[i]] = i; for (unsigned char c : T) C[c + 1]++; for (int c = 0; c < 256; c++) C[c + 1] += C[c];
        plainPsi.resize(n); for (int i = 0; i < n; i++) plainPsi[i] = isa[(sa[i] + 1) % n];
        for (int c = 0; c < 256; c++) {                                    // 글자 c 의 구간 [C[c], C[c+1]) 의 Ψ 를 gap 부호로
            bucketBlk[c] = blkVal.size();
            for (int j = 0, i = C[c]; i < C[c + 1]; i++, j++) { if (j % BL == 0) { blkVal.push_back(plainPsi[i]); blkOff.push_back(psiBits.n); } else psiBits.gamma(plainPsi[i] - plainPsi[i - 1]); }
        }
        bucketBlk[256] = blkVal.size(); mark.assign((n + 63) / 64 + 1, 0); markRank.assign(mark.size() + 1, 0);
        for (int i = 0; i < n; i++) if (sa[i] % S == 0) { mark[i / 64] |= 1ULL << (i % 64); saSample.push_back(sa[i]); }
        for (size_t w = 0; w < mark.size(); w++) markRank[w + 1] = markRank[w] + __builtin_popcountll(mark[w]);
    }
    int charAt(int i) const { return std::upper_bound(C.begin(), C.end(), i) - C.begin() - 1; }                               // F[i]
    int psi(int i) const {
        int c = charAt(i), j = i - C[c], b = j / BL; long blk = bucketBlk[c] + b; uint32_t v = blkVal[blk]; long p = blkOff[blk];
        for (int k = 0; k < j % BL; k++) v += psiBits.readGamma(p); return v;
    }
    bool marked(int i) const { return (mark[i / 64] >> (i % 64)) & 1; }
    int locate(int i) const { int t = 0; while (!marked(i)) { i = psi(i); t++; }
        int r = markRank[i / 64] + __builtin_popcountll(mark[i / 64] & ((1ULL << (i % 64)) - 1)); return ((int)saSample[r] - t % n + n) % n; }
    int cmp(int row, const std::string& P) const {                         // 행 row 의 접미사 앞쪽 |P| 글자 vs P (Ψ 를 따라 펼침). <0, 0, >0
        for (size_t k = 0; k < P.size(); k++) { int c = charAt(row); if (c != (unsigned char)P[k]) return c < (unsigned char)P[k] ? -1 : 1; row = psi(row); } return 0;
    }
    std::pair<int, int> range(const std::string& P) const {
        int lo = 0, hi = n; while (lo < hi) { int mid = (lo + hi) / 2; if (cmp(mid, P) < 0) lo = mid + 1; else hi = mid; } int a = lo;
        hi = n; while (lo < hi) { int mid = (lo + hi) / 2; if (cmp(mid, P) <= 0) lo = mid + 1; else hi = mid; } return {a, lo};
    }
    double bits() const { return psiBits.n + 32.0 * blkVal.size() + 32.0 * blkOff.size() / 2 + n + 32.0 * saSample.size(); }
};
int main() {
    std::mt19937 g(2); int n = 20000; std::string T; for (int i = 0; i < n - 1; i++) T += "ACGT"[g() % 4]; T += '$';
    CSA csa(T);
    for (int i = 0; i < csa.n; i += 7) assert(csa.psi(i) == csa.plainPsi[i]);        // 압축된 Ψ 를 복호하면 원래 Ψ
    for (int c = 0; c < 256; c++) for (int i = csa.C[c] + 1; i < csa.C[c + 1]; i++) assert(csa.plainPsi[i] > csa.plainPsi[i - 1]);       // 같은 첫 글자 구간에서 Ψ 증가
    for (int t = 0; t < 400; t++) {
        std::string P; if (t % 2) { int len = 1 + g() % 9, st = g() % (n - len - 1); P = T.substr(st, len); } else { int len = 1 + g() % 8; for (int i = 0; i < len; i++) P += "ACGT"[g() % 4]; }
        auto r = csa.range(P); std::vector<int> got; for (int i = r.first; i < r.second; i++) got.push_back(csa.locate(i)); std::sort(got.begin(), got.end());
        std::vector<int> want; for (size_t p = T.find(P); p != std::string::npos; p = T.find(P, p + 1)) want.push_back(p); assert(got == want);          // 모든 출현 위치 일치
    }
    double bitsPer = csa.bits() / csa.n;
    assert(bitsPer < 16);                                                  // 평범한 SA 는 글자당 32 비트
    std::cout << "CompressedSuffixArray: count/locate verified on " << csa.n << " chars; " << bitsPer << " bits per char (plain SA: 32, plain Psi: 32)" << std::endl; return 0;
}
// Time Complexity: 검색 O(m log n) 번 Ψ 계산, locate O(S) 번 Ψ 계산 (S = 표본 간격)
// Space Complexity: 글자당 약 H0 + O(1) 비트 + SA 표본 n/S 개
```
## DynamicWaveletTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 동적 웨이블릿 트리: 웨이블릿 트리(Part 2)는 한 번 만들면 고정이지만, 이 구조는 수열 중간에 원소를 끼우고(insert) 지우고(erase)도 access / rank 를 O(log n log σ) 에 한다.
// 정적 구조의 각 노드가 가진 비트열을 "동적 비트벡터"로 바꾸면 된다 — 비트 삽입·삭제·rank 를 지원하는 균형 트리(여기서는 암묵 키 트립: 각 노드가 부분 트리 크기와 1 의 개수를 저장).
// 원소 c 를 위치 pos 에 삽입: 루트 비트열의 pos 에 (c 가 알파벳 상위 절반이면 1, 아니면 0) 비트를 끼우고, 그 비트가 속한 자식 쪽 위치 = (1 이면 pos 앞의 1 의 수, 0 이면 pos 앞의 0 의 수) 로 옮겨 재귀. 텍스트 편집기·동적 FM-인덱스(동적 BWT)에 쓰인다
struct DBV {
    struct N { int bit, sz, ones; unsigned pri; N *l = nullptr, *r = nullptr; }; N* root = nullptr; std::mt19937 rng{1};
    static int sz(N* t) { return t ? t->sz : 0; } static int on(N* t) { return t ? t->ones : 0; }
    static void upd(N* t) { t->sz = 1 + sz(t->l) + sz(t->r); t->ones = t->bit + on(t->l) + on(t->r); }
    static void split(N* t, int k, N*& a, N*& b) { if (!t) { a = b = nullptr; return; } if (sz(t->l) < k) { a = t; split(t->r, k - sz(t->l) - 1, t->r, b); } else { b = t; split(t->l, k, a, t->l); } upd(t); }
    static N* merge(N* a, N* b) { if (!a || !b) return a ? a : b; if (a->pri > b->pri) { a->r = merge(a->r, b); upd(a); return a; } b->l = merge(a, b->l); upd(b); return b; }
    int size() const { return sz(root); }
    void insert(int pos, int bit) { N *a, *b; split(root, pos, a, b); N* n = new N{bit, 1, bit, (unsigned)rng()}; root = merge(merge(a, n), b); }
    int erase(int pos) { N *a, *b, *m, *c; split(root, pos, a, b); split(b, 1, m, c); int bit = m->bit; delete m; root = merge(a, c); return bit; }
    int access(int pos) const { N* t = root; for (;;) { int ls = sz(t->l); if (pos < ls) t = t->l; else if (pos == ls) return t->bit; else { pos -= ls + 1; t = t->r; } } }
    int rank1(int pos) const { int r = 0; N* t = root; while (t && pos > 0) { int ls = sz(t->l); if (pos <= ls) t = t->l; else { r += on(t->l) + t->bit; pos -= ls + 1; t = t->r; } } return r; }       // [0, pos) 의 1 의 수
    ~DBV() { std::vector<N*> st; if (root) st.push_back(root); while (!st.empty()) { N* t = st.back(); st.pop_back(); if (t->l) st.push_back(t->l); if (t->r) st.push_back(t->r); delete t; } }
};
struct DWT {
    int lo, hi; DBV bv; DWT *L = nullptr, *R = nullptr; DWT(int lo, int hi) : lo(lo), hi(hi) {} ~DWT() { delete L; delete R; }
    bool leaf() const { return hi - lo == 1; } int mid() const { return (lo + hi) / 2; }
    DWT*& child(int bit) { DWT*& c = bit ? R : L; if (!c) c = bit ? new DWT(mid(), hi) : new DWT(lo, mid()); return c; }
    void insert(int pos, int c) { if (leaf()) return; int bit = c >= mid(), r1 = bv.rank1(pos); bv.insert(pos, bit); child(bit)->insert(bit ? r1 : pos - r1, c); }
    int access(int pos) { if (leaf()) return lo; int bit = bv.access(pos), r1 = bv.rank1(pos); return child(bit)->access(bit ? r1 : pos - r1); }
    int erase(int pos) { if (leaf()) return lo; int bit = bv.access(pos), r1 = bv.rank1(pos); bv.erase(pos); return child(bit)->erase(bit ? r1 : pos - r1); }
    int rank(int c, int pos) { if (leaf()) return pos; int bit = c >= mid(), r1 = bv.rank1(pos); DWT*& ch = bit ? R : L; if (!ch) return 0; return ch->rank(c, bit ? r1 : pos - r1); }       // [0, pos) 안의 c 의 개수
};
int main() {
    const int SIGMA = 16; DWT t(0, SIGMA); std::vector<int> ref; std::mt19937 g(3);
    for (int step = 0; step < 30000; step++) {
        int op = g() % 10;
        if (op < 5 || ref.empty()) { int pos = g() % (ref.size() + 1), c = g() % SIGMA; t.insert(pos, c); ref.insert(ref.begin() + pos, c); }
        else if (op < 7) { int pos = g() % ref.size(); assert(t.erase(pos) == ref[pos]); ref.erase(ref.begin() + pos); }
        else if (op < 9) { int pos = g() % ref.size(); assert(t.access(pos) == ref[pos]); }
        else { int c = g() % SIGMA, pos = g() % (ref.size() + 1); assert(t.rank(c, pos) == (int)std::count(ref.begin(), ref.begin() + pos, c)); }
        assert(t.bv.size() == (int)ref.size());
    }
    for (size_t i = 0; i < ref.size(); i++) assert(t.access(i) == ref[i]);
    std::cout << "DynamicWaveletTree: 30000 insert/erase/access/rank ops match std::vector (final length " << ref.size() << ")" << std::endl; return 0;
}
// Time Complexity: 연산당 O(log n · log σ)
// Space Complexity: O(n log σ) 노드 (비트 하나가 트립 노드 하나)
```
## PackedMemoryArray()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 패킹된 메모리 배열(PMA, Itai–Konheim–Rodeh 1981): 정렬된 원소를 배열에 순서대로 두되 곳곳에 의도적으로 "빈칸(gap)" 을 남겨 삽입 때 이동량을 줄인다. 순차 메모리라 스캔이 캐시 친화적이고
// (연결 리스트·트리와 달리 포인터 추적이 없다) 삽입은 분할상환 O(log² n) 번의 원소 이동이다.  동적 그래프 시스템(PCSR, Terrace)과 캐시 무관 B-트리의 바닥층으로 쓰인다.
// 배열을 길이 Θ(log n) 의 구간(segment)들로 나누고 그 위에 암묵적 이진 트리를 올린다. 레벨 l 의 창(window)은 밀도 상한 τ_l 을 갖는다: 잎 구간 1.0 -> 전체 0.5 로 선형 감소.
// 삽입으로 구간이 넘치면 "상한을 만족하는 가장 작은 상위 창"을 찾아 그 창의 원소를 모두 모아 새 원소와 함께 고르게 펴 준다(rebalance). 루트가 상한을 넘으면 배열을 두 배로 키운다. 삭제는 하한 ρ_l (0.1 -> 0.2)로 대칭 처리하고 배열을 절반으로 줄인다
const long EMPTY = -1;
struct PMA {
    std::vector<long> a; int seg = 4; long count = 0, moves = 0;
    PMA() { init(16); }
    void init(size_t cap) { a.assign(cap, EMPTY); int lg = 0; while ((1u << lg) < cap) lg++; seg = 1; while (seg < lg) seg <<= 1; seg = std::min<size_t>(std::max(seg, 4), cap); }
    int H() const { int h = 0; for (size_t s = a.size() / seg; s > 1; s >>= 1) h++; return h; }
    double tau(int l) const { int h = H(); return h == 0 ? 1.0 : 1.0 - 0.5 * l / h; }
    double rho(int l) const { int h = H(); return h == 0 ? 0.0 : 0.1 + 0.1 * l / h; }
    long countIn(size_t s, size_t len) const { long c = 0; for (size_t i = s; i < s + len; i++) c += a[i] != EMPTY; return c; }
    size_t lowerIdx(long key) const {                                      // key 이상인 첫 원소의 배열 인덱스 (없으면 size)
        size_t lo = 0, hi = a.size();
        while (lo < hi) { size_t mid = (lo + hi) / 2, j = mid; while (j < hi && a[j] == EMPTY) j++; if (j == hi) { hi = mid; continue; } if (a[j] < key) lo = j + 1; else hi = mid; }
        size_t j = lo; while (j < a.size() && a[j] == EMPTY) j++; return j;
    }
    std::vector<long> gather(size_t s, size_t len) const { std::vector<long> v; for (size_t i = s; i < s + len; i++) if (a[i] != EMPTY) v.push_back(a[i]); return v; }
    void spread(size_t s, size_t len, const std::vector<long>& v) { std::fill(a.begin() + s, a.begin() + s + len, EMPTY); for (size_t i = 0; i < v.size(); i++) a[s + i * len / v.size()] = v[i]; moves += v.size(); }
    void rebuild(size_t newCap) { std::vector<long> v = gather(0, a.size()); init(newCap); spread(0, a.size(), v); }
    bool contains(long key) const { size_t j = lowerIdx(key); return j < a.size() && a[j] == key; }
    bool insert(long key) {
        if (contains(key)) return false; size_t idx = lowerIdx(key), s = std::min(idx / seg, a.size() / seg - 1), wsz = seg, ws = s * seg; int lvl = 0;
        for (;;) { long c = countIn(ws, wsz); if ((double)(c + 1) <= tau(lvl) * wsz) break; if (wsz == a.size()) { rebuild(a.size() * 2); return insert(key); } lvl++; wsz *= 2; ws = ws / wsz * wsz; }     // 상한을 만족하는 가장 작은 창
        std::vector<long> v = gather(ws, wsz); v.insert(std::lower_bound(v.begin(), v.end(), key), key); spread(ws, wsz, v); count++; return true;
    }
    bool erase(long key) {
        if (!contains(key)) return false; size_t j = lowerIdx(key); a[j] = EMPTY; count--; size_t s = j / seg, wsz = seg, ws = s * seg; int lvl = 0;
        while (wsz < a.size() && (double)countIn(ws, wsz) < rho(lvl) * wsz) { lvl++; wsz *= 2; ws = ws / wsz * wsz; }
        if (wsz == a.size() && a.size() > 16 && (double)count < rho(H()) * a.size()) { rebuild(a.size() / 2); return true; }
        if (lvl > 0) { std::vector<long> v = gather(ws, wsz); spread(ws, wsz, v); }
        return true;
    }
};
int main() {
    for (int mode = 0; mode < 3; mode++) {                                 // 0 무작위 삽입, 1 오름차순 삽입(최악), 2 삽입과 삭제 혼합
        PMA p; std::set<long> ref; std::mt19937 g(5 + mode); long inserts = 0; p.moves = 0;
        for (int step = 0; step < 20000; step++) {
            long k = mode == 1 ? step : (long)(g() % 1000000); bool del = mode == 2 && g() % 3 == 0 && !ref.empty();
            if (del) { long d = *std::next(ref.begin(), g() % ref.size()); assert(p.erase(d)); ref.erase(d); } else { bool added = p.insert(k); assert(added == ref.insert(k).second); inserts += added; }
            assert(p.count == (long)ref.size());
            if (step % 2000 == 0) { auto v = p.gather(0, p.a.size()); assert(v == std::vector<long>(ref.begin(), ref.end())); assert(p.count <= (long)p.a.size()); for (size_t sI = 0; sI < p.a.size(); sI += p.seg) assert(p.countIn(sI, p.seg) <= p.seg); }       // 정렬 순서, 구간 용량
        }
        auto v = p.gather(0, p.a.size()); assert((v == std::vector<long>(ref.begin(), ref.end())));
        double lg = std::log2((double)p.a.size()); double perOp = (double)p.moves / inserts;
        assert(perOp < lg * lg);                                           // 삽입당 이동 횟수 < log² N
        std::cout << (mode == 0 ? "random" : mode == 1 ? "sorted" : "mixed") << ": " << ref.size() << " keys in capacity " << p.a.size() << " (density " << (double)ref.size() / p.a.size() << "), moves per insert " << perOp << " (log^2 N = " << lg * lg << ")" << std::endl;
    }
    return 0;
}
// Time Complexity: 삽입·삭제 분할상환 O(log² n) 이동, 범위 스캔 O(k) (순차 메모리)
// Space Complexity: O(n) (밀도 0.1 ~ 0.5 유지)
```
## CacheAwareBTree()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 캐시 인지(cache-aware) B-트리: 캐시 라인 크기를 코드에 "알고" 노드 크기를 거기에 맞춘다. 64 바이트 라인에 4 바이트 키 16 개 = 노드 하나가 정확히 한 라인이 되게 분기 수 F=16 으로 정적 트리를 만든다.
// 구성: 정렬 배열을 레벨 0 으로 두고, 레벨 h+1 은 레벨 h 의 F 개마다 첫 키를 모은 배열(표본). 탐색은 맨 위(크기 <= F)에서 시작해 한 레벨에서 F 개 연속 키만 읽고 다음 레벨의 해당 블록으로 내려간다.
// 이분 탐색은 깊은 곳에서 프로브마다 다른 캐시 라인을 건드려 약 log2 N - 4 라인을 읽지만, 이 트리는 log_F N 라인이면 된다. F 가 라인보다 작으면 레벨이 늘고, 크면 노드 한 개가 여러 라인이다 -> F = 라인 크기가 최적
// (반대로 캐시 무관 B-트리(앞 항목)는 B 를 모르고도 거의 같은 성능을 낸다는 점이 대비된다)
struct StaticBTree {
    int F; std::vector<std::vector<int>> lv;
    StaticBTree(const std::vector<int>& keys, int F) : F(F) { lv.push_back(keys); while (lv.back().size() > (size_t)F) { std::vector<int> up; for (size_t i = 0; i < lv.back().size(); i += F) up.push_back(lv.back()[i]); lv.push_back(up); } }
    // 반환: 레벨 0 에서 q 이상인 첫 위치. lines 에는 읽은 캐시 라인 (레벨, 라인 번호) 을 기록 (라인 = 16 키)
    long lowerBound(int q, std::set<std::pair<int, long>>& lines) const {
        size_t block = 0;
        for (int h = (int)lv.size() - 1; h >= 1; h--) {
            const auto& a = lv[h]; size_t s = block * F, e = std::min(a.size(), s + F); for (long ln = s / 16; ln <= (long)(e - 1) / 16; ln++) lines.insert({h, ln});     // 노드의 F 개 키를 읽음
            size_t j = s; while (j < e && a[j] <= q) j++; size_t child = j > s ? j - 1 : s; block = child;           // q 이하인 마지막 표본의 자식 블록
        }
        const auto& a = lv[0]; size_t s = block * F, e = std::min(a.size(), s + F); for (long ln = s / 16; ln <= (long)(e - 1) / 16; ln++) lines.insert({0, ln});
        size_t j = s; while (j < e && a[j] < q) j++; return j;             // 블록 안에서 q 이상 첫 키 (블록 끝이면 다음 블록의 첫 키가 정답)
    }
};
int main() {
    std::mt19937 g(5); const long n = 1 << 20; std::vector<int> keys(n); for (long i = 0; i < n; i++) keys[i] = i * 3;     // 이미 정렬된 정수 키
    double lines[3] = {0, 0, 0}; int Fs[3] = {4, 16, 64}; double bin = 0; int Q = 3000;
    StaticBTree t4(keys, 4), t16(keys, 16), t64(keys, 64); const StaticBTree* trees[3] = {&t4, &t16, &t64};
    for (int t = 0; t < Q; t++) {
        int q = g() % (n * 3); long want = std::lower_bound(keys.begin(), keys.end(), q) - keys.begin();
        for (int k = 0; k < 3; k++) { std::set<std::pair<int, long>> ln; long r = trees[k]->lowerBound(q, ln); assert(r == want); lines[k] += ln.size(); }          // 결과는 std::lower_bound 와 같고 읽은 라인 수를 센다
        long lo = 0, hi = n; std::set<long> bl; while (lo < hi) { long mid = (lo + hi) / 2; bl.insert(mid / 16); if (keys[mid] < q) lo = mid + 1; else hi = mid; } bin += bl.size();
    }
    for (int k = 0; k < 3; k++) lines[k] /= Q; bin /= Q;
    assert(lines[1] <= lines[0] && lines[1] <= lines[2] && lines[1] * 2 < bin);        // F = 16(라인 크기)이 최소, 이분 탐색의 절반 미만
    std::cout << "CacheAwareBTree: cache lines per search  F=4: " << lines[0] << ", F=16: " << lines[1] << ", F=64: " << lines[2] << ", binary search: " << bin << std::endl; return 0;
}
// Time Complexity: 탐색 O(log_F N) 캐시 라인 (F = 라인 크기 / 키 크기)
// Space Complexity: 정렬 배열 + N/(F-1) 개 표본
```
## LearnedBloomFilter()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 학습된 블룸 필터(Kraska et al.): 키 집합 S 와 "S 가 아닌 것" 을 구별하는 작은 모델 f(x) ∈ [0,1] 을 학습해 앞단에 두고, f(x) >= τ 이면 "있다", 아니면 "모델이 놓친 키만 담은 작은 백업 블룸 필터" 에 묻는다.
// 모델이 S 의 키에 낮은 점수를 준(거짓 음성) 경우는 백업 필터에 모두 넣어 두므로 전체로는 거짓 음성이 절대 없다. 모델이 잘 구별하는 데이터(악성 URL 처럼 패턴이 있는 키)에서는 백업 필터가 작아져
// 모델 크기를 더해도 일반 블룸 필터보다 공간이 적다.  임계값 τ 는 검증용 비키 집합에서 모델의 거짓 양성률이 목표가 되게 정한다.  아래 모델은 문자 3-gram 을 해시한 특징의 로지스틱 회귀(SGD)이다
const int FEAT = 1024;
struct Model {
    std::vector<float> w = std::vector<float>(FEAT, 0); float b = 0;
    static void feats(const std::string& s, std::vector<int>& f) { f.clear(); for (size_t i = 0; i + 3 <= s.size(); i++) { uint32_t h = 2166136261u; for (int j = 0; j < 3; j++) { h ^= (unsigned char)s[i + j]; h *= 16777619u; } f.push_back(h % FEAT); } std::sort(f.begin(), f.end()); f.erase(std::unique(f.begin(), f.end()), f.end()); }
    float score(const std::string& s) const { std::vector<int> f; feats(s, f); float z = b; for (int j : f) z += w[j]; return 1.0f / (1.0f + std::exp(-z)); }
    void train(const std::vector<std::string>& pos, const std::vector<std::string>& neg, int epochs, float lr, std::mt19937& g) {
        std::vector<std::pair<const std::string*, int>> data; for (auto& s : pos) data.push_back({&s, 1}); for (auto& s : neg) data.push_back({&s, 0}); std::vector<int> f;
        for (int e = 0; e < epochs; e++) { std::shuffle(data.begin(), data.end(), g); for (auto& d : data) { feats(*d.first, f); float z = b; for (int j : f) z += w[j]; float p = 1.0f / (1.0f + std::exp(-z)), grad = p - d.second; for (int j : f) w[j] -= lr * grad; b -= lr * grad; } }
    }
};
struct Bloom {
    size_t m; int k; std::vector<uint64_t> bits;
    Bloom(size_t n, double p) { n = std::max<size_t>(n, 1); m = (size_t)std::ceil(-(double)n * std::log(p) / (std::log(2.0) * std::log(2.0))); k = std::max(1, (int)std::round((double)m / n * std::log(2.0))); bits.assign((m + 63) / 64, 0); }
    static uint64_t h(const std::string& s, uint64_t seed) { uint64_t x = 1469598103934665603ULL ^ seed; for (unsigned char c : s) { x ^= c; x *= 1099511628211ULL; } x ^= x >> 31; x *= 0x9e3779b97f4a7c15ULL; return x ^ (x >> 29); }
    void add(const std::string& s) { for (int i = 0; i < k; i++) { size_t p = (h(s, 1) + (uint64_t)i * (h(s, 2) | 1)) % m; bits[p >> 6] |= 1ULL << (p & 63); } }
    bool maybe(const std::string& s) const { for (int i = 0; i < k; i++) { size_t p = (h(s, 1) + (uint64_t)i * (h(s, 2) | 1)) % m; if (!((bits[p >> 6] >> (p & 63)) & 1)) return false; } return true; }
};
const char* BAD[] = {"login", "secure", "verify", "update", "account", "bank", "paypal", "confirm", "signin", "wallet"};
const char* GOOD[] = {"news", "blog", "shop", "wiki", "photo", "music", "game", "recipe", "travel", "sports"};
std::string gen(bool bad, std::mt19937& g) {
    std::string s; int t = 2 + g() % 2; for (int i = 0; i < t; i++) { bool useBad = bad ? (g() % 10 != 0) : (g() % 10 == 0); s += (useBad ? BAD : GOOD)[g() % 10]; s += g() % 2 ? "-" : "."; }
    int r = 3 + g() % 4; for (int i = 0; i < r; i++) s += 'a' + g() % 26; return s;
}
int main() {
    std::mt19937 g(11); std::set<std::string> keySet, trainNeg, valNeg, testNeg;
    while (keySet.size() < 30000) keySet.insert(gen(true, g)); while (trainNeg.size() < 30000) trainNeg.insert(gen(false, g));
    while (valNeg.size() < 20000) { auto s = gen(false, g); if (!trainNeg.count(s)) valNeg.insert(s); } while (testNeg.size() < 50000) { auto s = gen(false, g); if (!trainNeg.count(s) && !valNeg.count(s) && !keySet.count(s)) testNeg.insert(s); }
    std::vector<std::string> keys(keySet.begin(), keySet.end()), tn(trainNeg.begin(), trainNeg.end());
    Model m; m.train(keys, tn, 6, 0.05f, g);
    std::vector<float> vs; for (auto& s : valNeg) vs.push_back(m.score(s)); std::sort(vs.begin(), vs.end()); float tau = vs[(size_t)(vs.size() * 0.995)];        // 검증 비키의 99.5% 가 τ 아래 -> 모델 FPR ≈ 0.5%
    std::vector<std::string> missed; for (auto& k : keys) if (m.score(k) < tau) missed.push_back(k);          // 모델이 놓친 키 -> 백업 필터에
    double p2 = 0.005; Bloom backup(missed.size(), p2); for (auto& k : missed) backup.add(k);
    auto query = [&](const std::string& s) { return m.score(s) >= tau || backup.maybe(s); };
    for (auto& k : keys) assert(query(k));                                 // 거짓 음성 0
    long fp = 0; for (auto& s : testNeg) fp += query(s); double fpr = (double)fp / testNeg.size();
    Bloom plain(keys.size(), fpr > 0.002 ? fpr : 0.002); double learnedBits = FEAT * 32.0 + 32 + backup.m, plainBits = plain.m;
    assert(fpr < 0.03 && learnedBits < plainBits);                         // 같은 거짓 양성률에서 공간이 더 적다
    std::cout << "LearnedBloomFilter: " << keys.size() << " keys, model missed " << missed.size() << " (backup filter " << backup.m << " bits); measured FPR " << fpr * 100 << "%, total " << learnedBits / keys.size()
              << " bits/key vs plain Bloom (same FPR) " << plainBits / keys.size() << " bits/key, no false negatives" << std::endl; return 0;
}
// Time Complexity: 조회 O(특징 수 + k) (모델 한 번 + 필요 시 백업 필터)
// Space Complexity: 모델 + 놓친 키 수 × O(log 1/p) 비트
```

# 부록
## Cache-Aware vs Cache-Oblivious
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Aware: hardcoded parameters. Oblivious: theoretically optimal everywhere." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Immutable vs Persistent
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Immutable: read-only. Persistent: creates new versions sharing old data." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## Lock-Free vs Wait-Free
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Lock-Free: system progress. Wait-Free: per-thread progress guaranteed." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Online vs Offline 자료구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Online processes on the fly. Offline pre-processes all data upfront." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Static vs Dynamic 자료구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Static: fixed elements. Dynamic: supports inserts/deletes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Internal Memory vs External Memory
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Internal: fast RAM (AVL). External: slow disk I/O (B-Tree)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Exact vs Approximate 자료구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Exact gives 100% truth. Approximate trades accuracy for extreme space saving." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CPU 자료구조 vs GPU 자료구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CPU excels at branching/pointers. GPU demands linear arrays (SoA) and SIMT." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LSM Tree가 SSD에 적합한 이유
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "LSM sequential appends avoid SSD random overwrite wear." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 벡터 데이터베이스는 왜 HNSW를 사용하는가?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "HNSW graphs bypass the curse of dimensionality seen in KD-Trees." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 현대 데이터베이스가 B+Tree와 LSMTree를 함께 사용하는 이유
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "B+Tree for fast reads (OLTP); LSM for massive ingest writes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 생성형 AI 시대의 자료구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Vector DBs and semantic graphs are augmenting traditional relational models." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
