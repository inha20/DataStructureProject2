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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 영속 스택(스택 관점의 요약, 정본은 Stack.md Part 10): push 는 "새 머리 셀 → 옛 머리", pop 은 옛 머리의 next 를 새 스택으로 돌려줄 뿐이다.  옛 버전을 건드리지 않으므로 실행 취소(undo)·분기 탐색·스레드 간 공유가 공짜다.  push·pop·top 이 모두 O(1) 이고 push 마다 셀 하나만 늘어난다.
//  버전 = 머리 셀의 인덱스(−1 = 빈 스택), 셀은 한 번 쓰면 바뀌지 않는 풀에 둔다 — 포인터 체인과 달리 100 만 개짜리 스택을 버려도 소멸자 재귀가 없다.
//  ① 무작위 버전 트리: 임의의 옛 버전에서 push/pop/top 을 6000 번 하고 모든 버전을 std::vector 모형(복사본)과 *끝에서* 다시 대조  ② 셀 수 = push 횟수 (pop 은 새 셀을 만들지 않는다), 버전들의 원소 합보다 훨씬 적다
//  ③ 공유 접미사: 두 버전이 공유하는 꼬리 길이를 셀 인덱스 비교로 구한 값 = 셀 번호 열의 공통 접미사 (독립 오라클)  ④ 100 만 번 push/pop 의 모든 버전을 8 바이트씩만 저장하고, 중간 체크포인트 100 개를 모형 스냅샷과 대조.
struct PStack {
    struct Cell { int val, next, len; };
    std::vector<Cell> cells;
    int push(int v, int x) { cells.push_back({x, v, len(v) + 1}); return (int)cells.size() - 1; }
    int pop(int v) const { return cells[v].next; }                                                                // v ≠ −1
    int top(int v) const { return cells[v].val; }
    int len(int v) const { return v < 0 ? 0 : cells[v].len; }
    std::vector<int> toVec(int v) const { std::vector<int> out; for (; v >= 0; v = cells[v].next) out.push_back(cells[v].val); return out; }       // 머리 → 바닥
    int sharedTail(int a, int b) const { while (len(a) > len(b)) a = cells[a].next; while (len(b) > len(a)) b = cells[b].next; while (a != b) { a = cells[a].next; b = cells[b].next; } return len(a); }   // 같은 셀을 처음 만날 때까지 올라간다
    std::vector<int> cellIds(int v) const { std::vector<int> out; for (; v >= 0; v = cells[v].next) out.push_back(v); return out; }
};

int main() {
    std::mt19937 rng(101); PStack ps; std::vector<int> ver = {-1}; std::vector<std::vector<int>> model = {{}}; long pushes = 0;
    for (int step = 0; step < 6000; ++step) {
        int base = (int)(rng() % ver.size()); int v = ver[base]; std::vector<int> m = model[base]; int op = (int)(rng() % 3);
        if (op == 0 || m.empty()) { int x = (int)(rng() % 1000); v = ps.push(v, x); m.insert(m.begin(), x); ++pushes; }
        else if (op == 1) { assert(ps.top(v) == m.front()); v = ps.pop(v); m.erase(m.begin()); }
        else { assert(ps.top(v) == m.front() && ps.len(v) == (int)m.size()); }
        assert(ps.toVec(v) == m && ps.len(v) == (int)m.size()); ver.push_back(v); model.push_back(m);
    }
    for (size_t i = 0; i < ver.size(); ++i) assert(ps.toVec(ver[i]) == model[i]);                                    // 옛 버전은 전부 그대로
    long total = 0; for (auto& m : model) total += (long)m.size(); assert((long)ps.cells.size() == pushes && pushes < total);   // ② 셀 수 = push 수, 공유 덕에 훨씬 적다
    for (int it = 0; it < 3000; ++it) { int a = ver[rng() % ver.size()], b = ver[rng() % ver.size()];                 // ③ 공유 접미사
        std::vector<int> ia = ps.cellIds(a), ib = ps.cellIds(b); int want = 0; while (want < (int)ia.size() && want < (int)ib.size() && ia[ia.size() - 1 - want] == ib[ib.size() - 1 - want]) ++want; assert(ps.sharedTail(a, b) == want); }
    { PStack big; std::vector<int> versions; versions.reserve(1000001); std::vector<int> cur; int head = -1; versions.push_back(head); std::vector<std::pair<int, std::vector<int>>> checkpoints;      // ④
      for (long step = 1; step <= 1000000; ++step) { if (head < 0 || rng() % 2) { int x = (int)(rng() % 1000000); head = big.push(head, x); cur.push_back(x); } else { head = big.pop(head); cur.pop_back(); }
        versions.push_back(head); if (step % 10000 == 0) checkpoints.push_back({(int)step, std::vector<int>(cur.rbegin(), cur.rend())}); }
      for (auto& cp : checkpoints) assert(big.toVec(versions[cp.first]) == cp.second);                               // 100 개의 옛 버전이 100 만 번 뒤에도 정확
      assert(checkpoints.size() == 100 && big.cells.size() <= 1000000);
      PStack chain; int h = -1; for (int i = 0; i < 1000000; ++i) h = chain.push(h, i); assert(chain.len(h) == 1000000 && chain.top(h) == 999999 && chain.len(chain.pop(h)) == 999999); }              // 100 만 개 사슬: 소멸 때 재귀 없음
    std::cout << "PersistentStack: 6000 operations on random versions kept all " << ver.size() << " versions intact with only " << ps.cells.size() << " cells (vs " << total << " elements across versions); shared-tail lengths matched the cell-id oracle; 10^6 push/pop versions were retained and 100 checkpoints verified" << std::endl;
    return 0;
}
// Time Complexity: push·pop·top O(1), 공유 접미사 O(길이)
// Space Complexity: 버전당 O(1), push 마다 셀 하나
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

## HAMT()
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <vector>

// HAMT(Hash Array Mapped Trie, Bagwell 2001): 해시를 5 비트씩 끊어 32 갈래 트라이를 내려가되, 노드마다 "32 비트 비트맵 + 실제 있는 자식만 담은 압축 배열" 을 둔다 — 자식 i 가 있으면 비트맵의 i 번째 비트가 1 이고
// 배열 위치는 popcount(비트맵 & (비트 - 1)) 이다. 빈 칸이 없으니 메모리가 해시 표 수준이고, 불변 노드를 경로 복사(path copying)로 갱신하므로 새 버전이 옛 버전과 거의 모든 노드를 공유한다 → 영속 맵.
// Clojure·Scala 의 불변 맵, Haskell 의 unordered-containers 가 이 구조다. 깊이는 64/5 → 최대 13 층(O(1)) 이고, 해시가 완전히 같은 키는 맨 아래 충돌 노드(선형 목록)에 모인다.
// 삭제하면 잎 하나만 남은 노드는 위로 올려 접는다 → 트라이 모양이 "키 집합" 만으로 정해져(정규형) 삽입·삭제 순서와 무관하다.
// 검증: ① 무작위 삽입·덮어쓰기·삭제 4 만 번을 std::map 과 대조 — 좋은 해시와, 키 4 개가 완전히 같은 해시가 되는 나쁜 해시(충돌 노드 사용) 두 가지 ② 모든 옛 버전이 그대로(영속성) ③ 한 번의 삽입이 새로 만드는 노드 <= 14 개
//       ④ 같은 키 집합을 오름차순·내림차순·무작위·"추가했다 지움" 순서로 만들어도 구조 문자열이 같다 ⑤ 배열 칸 합 = 키 수 + 노드 수 - 1 (잎 칸 + 자식 칸)
struct Hamt {
    struct Node; typedef std::shared_ptr<const Node> P;
    struct Entry { uint64_t key = 0; int val = 0; P child; };                                      // child 가 있으면 하위 노드, 없으면 (key, val) 잎
    struct Node { uint32_t bitmap = 0; std::vector<Entry> items; };                                // items.size() == popcount(bitmap) (충돌 노드는 bitmap 을 쓰지 않고 잎만 나열)
    typedef uint64_t (*HashFn)(uint64_t);
    HashFn hash; P root; size_t count = 0;
    explicit Hamt(HashFn h) : hash(h), root(std::make_shared<const Node>()) {}
    static int slot(uint32_t bitmap, uint32_t bit) { return (int)std::bitset<32>(bitmap & (bit - 1)).count(); }
    static uint32_t bitOf(uint64_t h, int shift) { return 1u << ((h >> shift) & 31); }
    P insertAt(const P& n, uint64_t h, int shift, uint64_t k, int v, bool& added) const {
        auto m = std::make_shared<Node>(*n);                                                       // 경로 위의 노드만 복사한다
        if (shift >= 65) {                                                                         // 64 비트를 다 썼다: 해시가 완전히 같은 키들의 충돌 노드
            for (auto& e : m->items) if (e.key == k) { e.val = v; return m; }
            m->items.push_back({k, v, nullptr}); added = true; return m;
        }
        const uint32_t bit = bitOf(h, shift); const int i = slot(m->bitmap, bit);
        if (!(m->bitmap & bit)) { m->bitmap |= bit; m->items.insert(m->items.begin() + i, Entry{k, v, nullptr}); added = true; return m; }
        Entry& e = m->items[i];
        if (e.child) { e.child = insertAt(e.child, h, shift + 5, k, v, added); return m; }
        if (e.key == k) { e.val = v; return m; }
        bool dummy = false; P sub = std::make_shared<const Node>();                                // 잎 둘이 같은 조각에 걸렸다: 한 층 내려 새 노드에 둘을 넣는다
        sub = insertAt(sub, hash(e.key), shift + 5, e.key, e.val, dummy); sub = insertAt(sub, h, shift + 5, k, v, added);
        e = Entry{0, 0, sub}; return m;
    }
    P eraseAt(const P& n, uint64_t h, int shift, uint64_t k, bool& removed) const {
        if (shift >= 65) {
            for (size_t i = 0; i < n->items.size(); ++i) if (n->items[i].key == k) { auto m = std::make_shared<Node>(*n); m->items.erase(m->items.begin() + (long)i); removed = true; return m; }
            return n;
        }
        const uint32_t bit = bitOf(h, shift); if (!(n->bitmap & bit)) return n;
        const int i = slot(n->bitmap, bit); const Entry& e = n->items[i];
        if (e.child) {
            P c = eraseAt(e.child, h, shift + 5, k, removed); if (!removed) return n;
            auto m = std::make_shared<Node>(*n);
            if (c->items.size() == 1 && !c->items[0].child) m->items[i] = c->items[0];             // 잎 하나만 남은 하위 노드는 접어 올린다(정규형 유지)
            else m->items[i].child = c;
            return m;
        }
        if (e.key != k) return n;
        auto m = std::make_shared<Node>(*n); m->items.erase(m->items.begin() + i); m->bitmap &= ~bit; removed = true; return m;
    }
    Hamt with(uint64_t k, int v) const { Hamt r = *this; bool added = false; r.root = insertAt(root, hash(k), 0, k, v, added); r.count += added; return r; }     // 새 버전을 돌려주고 this 는 그대로
    Hamt without(uint64_t k) const { Hamt r = *this; bool removed = false; r.root = eraseAt(root, hash(k), 0, k, removed); r.count -= removed; return r; }
    const int* find(uint64_t k) const {
        const uint64_t h = hash(k); const Node* n = root.get();
        for (int shift = 0;; shift += 5) {
            if (shift >= 65) { for (const auto& e : n->items) if (e.key == k) return &e.val; return nullptr; }
            const uint32_t bit = bitOf(h, shift); if (!(n->bitmap & bit)) return nullptr;
            const Entry& e = n->items[slot(n->bitmap, bit)];
            if (e.child) { n = e.child.get(); continue; }
            return e.key == k ? &e.val : nullptr;
        }
    }
    static void walk(const P& n, std::vector<std::pair<uint64_t, int>>& out, std::set<const Node*>& nodes, size_t& slots) {
        nodes.insert(n.get()); slots += n->items.size();
        for (const auto& e : n->items) { if (e.child) walk(e.child, out, nodes, slots); else out.push_back({e.key, e.val}); }
    }
    std::vector<std::pair<uint64_t, int>> items(std::set<const Node*>* nodes = nullptr, size_t* slots = nullptr) const {
        std::vector<std::pair<uint64_t, int>> out; std::set<const Node*> ns; size_t sl = 0; walk(root, out, ns, sl);
        if (nodes) *nodes = ns; if (slots) *slots = sl; std::sort(out.begin(), out.end()); return out;
    }
    static void shape(const P& n, std::string& s) { s += "("; s += std::to_string(n->bitmap); for (const auto& e : n->items) { if (e.child) shape(e.child, s); else s += "[" + std::to_string(e.key) + "]"; } s += ")"; }
    std::string shape() const { std::string s; shape(root, s); return s; }
};
uint64_t goodHash(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }   // splitmix64
uint64_t badHash(uint64_t x) { return goodHash(x / 4); }                                           // 연속한 키 4 개의 해시가 완전히 같다 → 충돌 노드
void check(const Hamt& h, const std::map<uint64_t, int>& model) {
    assert(h.count == model.size());
    std::set<const Hamt::Node*> nodes; size_t slots = 0; auto it = h.items(&nodes, &slots);
    assert((it == std::vector<std::pair<uint64_t, int>>(model.begin(), model.end())));
    assert(slots == model.size() + nodes.size() - 1);                                              // 배열 칸 = 잎 칸(키 수) + 자식 칸(노드 수 - 루트)
}
std::set<const Hamt::Node*> collect(const Hamt& h) { std::set<const Hamt::Node*> ns; std::vector<std::pair<uint64_t, int>> o; size_t s = 0; Hamt::walk(h.root, o, ns, s); return ns; }

int main() {
    {   Hamt h(goodHash); assert(h.find(1) == nullptr);                                            // 손으로 확인: 빈 맵, 삽입, 덮어쓰기, 옛 버전 보존
        Hamt a = h.with(1, 10), b = a.with(2, 20), c = b.with(1, 11), d = c.without(2);
        assert(h.count == 0 && a.count == 1 && b.count == 2 && c.count == 2 && d.count == 1);
        assert(*a.find(1) == 10 && a.find(2) == nullptr && *b.find(2) == 20 && *b.find(1) == 10 && *c.find(1) == 11 && d.find(2) == nullptr && *d.find(1) == 11); }
    for (int variant = 0; variant < 2; ++variant) {                                                // 0: 좋은 해시, 1: 충돌이 많은 해시
        Hamt h(variant ? badHash : goodHash); std::map<uint64_t, int> model; std::mt19937 rng(31 + variant);
        std::vector<std::pair<Hamt, std::map<uint64_t, int>>> history;
        for (int step = 0; step < 40000; ++step) {
            const uint64_t k = rng() % 3000; const int op = (int)(rng() % 10);
            if (op < 6) { const int v = (int)rng(); h = h.with(k, v); model[k] = v; } else if (op < 9) { h = h.without(k); model.erase(k); } else { const int* f = h.find(k); auto it = model.find(k); assert((f != nullptr) == (it != model.end()) && (!f || *f == it->second)); }
            if (step % 4000 == 0) { check(h, model); history.push_back({h, model}); }
        }
        check(h, model); for (const auto& snap : history) check(snap.first, snap.second);          // 오래된 버전이 전혀 망가지지 않았다
        for (uint64_t k = 0; k < 3000; ++k) { const int* f = h.find(k); auto it = model.find(k); assert((f != nullptr) == (it != model.end())); }
    }
    {   Hamt h(goodHash); std::mt19937 rng(8); for (int i = 0; i < 5000; ++i) h = h.with(rng(), i);
        size_t worst = 0; for (int i = 0; i < 300; ++i) {                                          // 한 번의 삽입이 새로 만드는 노드: 경로 위의 것뿐이다
            Hamt g = h.with(rng(), i); auto before = collect(h), after = collect(g); size_t fresh = 0; for (const auto* n : after) fresh += !before.count(n); worst = std::max(worst, fresh); h = g; }
        assert(worst <= 14 && collect(h).size() > 100); }
    {   std::vector<uint64_t> keys; std::mt19937 rng(9); for (int i = 0; i < 600; ++i) keys.push_back(rng() % 100000);
        std::sort(keys.begin(), keys.end()); keys.erase(std::unique(keys.begin(), keys.end()), keys.end());
        auto build = [&](std::vector<uint64_t> order, bool extra) { Hamt h(badHash); for (uint64_t k : order) h = h.with(k, 1);
            if (extra) { for (uint64_t k = 100000; k < 100300; ++k) h = h.with(k, 2); for (uint64_t k = 100000; k < 100300; ++k) h = h.without(k); } return h.shape(); };
        std::vector<uint64_t> rev(keys.rbegin(), keys.rend()), mixed = keys; std::shuffle(mixed.begin(), mixed.end(), rng);
        const std::string s = build(keys, false); assert(s == build(rev, false) && s == build(mixed, false) && s == build(mixed, true));      // 정규형: 순서·이력과 무관
    }
    std::cout << "HAMT: 80000 random insert/overwrite/erase operations matched std::map with a good hash and with a collision-heavy hash (4 keys share every 64-bit hash); all saved versions stayed intact; one insert created at most 14 new nodes; the trie shape was independent of insertion/deletion history" << std::endl;
    return 0;
}
// Time Complexity: 조회·삽입·삭제 O(log32 N) — 해시 64 비트라서 최대 13 층(= 사실상 O(1)), 삽입 한 번이 만드는 노드는 경로 길이만큼
// Space Complexity: O(N) (노드마다 실제 자식 수만큼의 배열 + 비트맵), 버전 하나를 더 두는 비용은 O(log32 N)
```

## RRBVector()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <vector>

// RRB-벡터(Relaxed Radix Balanced Vector, Bagwell & Rompf 2011): 영속 벡터(Clojure 의 PersistentVector 같은 기수 트리)에 "느슨한 노드" 를 허용해 O(log N) 이어 붙이기(concat)와 자르기(slice)를 가능하게 한 구조다.
// 보통의 기수 트리는 모든 노드가 가득 차 있어야 인덱스를 비트 연산으로 찾는데, 이어 붙이면 가운데에 덜 찬 노드가 생긴다. 그래서 노드마다 "자식별 누적 원소 수 표" 를 두고 거기서 자식을 찾는다(가득 찬 노드는 표 없이 빠른 길을 쓴다).
// 이 구현은 갈래 M=4 로 줄여 트리가 깊어지게 했고(실제는 32), 표를 모든 내부 노드에 둔다. 이어 붙이기는 두 트리의 이음매(왼쪽의 맨 오른쪽 가지, 오른쪽의 맨 왼쪽 가지)를 위로 올라가며 다시 포장한다.
// 한계: 이음매 한 줄만 다시 포장하므로 Bagwell–Rompf 의 "탐색 단계 불변식" 을 지키려는 추가 재균형은 하지 않는다 → 이어 붙이기를 아주 많이 하면 덜 찬 노드가 쌓여 높이가 이상적 값보다 커질 수 있다(아래 시험은 측정한 높이를 확인).
// 검증: ① 손으로 확인한 작은 예 ② 무작위 push_back·set·concat·slice 를 std::vector 와 비교하고 매번 불변식(누적 표·높이·노드 크기)을 검사 ③ 모든 옛 버전이 그대로(영속성) ④ 이어 붙이기가 새로 만드는 노드 수 <= 2(높이+1)+2 (나머지는 공유)
//       ⑤ 작은 조각 수백 개를 이어 붙여 만든 벡터의 높이가 이상적인 높이 + 2 이내
const int M = 4;
struct RrbVector {
    struct Node; typedef std::shared_ptr<const Node> P;
    struct Node { int height = 0; std::vector<int> items; std::vector<P> kids; std::vector<size_t> cum; };   // 높이 0: 잎(items), 그 위: kids 와 cum (cum[i] = kids[0..i] 의 원소 수 합)
    P root;
    static size_t sizeOf(const P& n) { return n->height == 0 ? n->items.size() : n->cum.back(); }
    static P leaf(std::vector<int> v) { auto n = std::make_shared<Node>(); n->items = std::move(v); return n; }
    static P inner(int h, std::vector<P> kids) { auto n = std::make_shared<Node>(); n->height = h; size_t s = 0; for (const P& k : kids) { s += sizeOf(k); n->cum.push_back(s); } n->kids = std::move(kids); return n; }
    size_t size() const { return root ? sizeOf(root) : 0; }
    int height() const { return root ? root->height : -1; }
    int get(size_t i) const {
        const Node* n = root.get();
        while (n->height > 0) { size_t c = 0; while (n->cum[c] <= i) ++c; if (c) i -= n->cum[c - 1]; n = n->kids[c].get(); }                 // 누적 표에서 자식을 고른다
        return n->items[i];
    }
    static P setAt(const P& n, size_t i, int v) {
        if (n->height == 0) { auto m = std::make_shared<Node>(*n); m->items[i] = v; return m; }                                                    // 경로 위의 노드만 복사
        size_t c = 0; while (n->cum[c] <= i) ++c; auto m = std::make_shared<Node>(*n); m->kids[c] = setAt(n->kids[c], c ? i - n->cum[c - 1] : i, v); return m;
    }
    RrbVector set(size_t i, int v) const { RrbVector r; r.root = setAt(root, i, v); return r; }
    static std::vector<P> pack(std::vector<P> kids, int h) {                                       // 자식 목록(<= 2M)을 노드 한두 개로: 앞 노드를 가득 채운다
        if ((int)kids.size() <= M) return {inner(h, std::move(kids))};
        std::vector<P> a(kids.begin(), kids.begin() + M), b(kids.begin() + M, kids.end()); return {inner(h, a), inner(h, b)};
    }
    static std::vector<P> cat(const P& a, const P& b) {                                            // 높이가 max(a, b) 인 노드 한두 개로 이어 붙인다
        if (a->height == b->height) {
            if (a->height == 0) {
                std::vector<int> all = a->items; all.insert(all.end(), b->items.begin(), b->items.end());
                if ((int)all.size() <= M) return {leaf(all)};
                return {leaf(std::vector<int>(all.begin(), all.begin() + M)), leaf(std::vector<int>(all.begin() + M, all.end()))};
            }
            std::vector<P> mid = cat(a->kids.back(), b->kids.front()), kids(a->kids.begin(), a->kids.end() - 1);        // 이음매: 왼쪽의 마지막 가지 + 오른쪽의 첫 가지
            kids.insert(kids.end(), mid.begin(), mid.end()); kids.insert(kids.end(), b->kids.begin() + 1, b->kids.end());
            return pack(std::move(kids), a->height);
        }
        if (a->height > b->height) { std::vector<P> mid = cat(a->kids.back(), b), kids(a->kids.begin(), a->kids.end() - 1); kids.insert(kids.end(), mid.begin(), mid.end()); return pack(std::move(kids), a->height); }
        std::vector<P> mid = cat(a, b->kids.front()), kids = mid; kids.insert(kids.end(), b->kids.begin() + 1, b->kids.end()); return pack(std::move(kids), b->height);
    }
    RrbVector concat(const RrbVector& o) const {
        if (!root) return o; if (!o.root) return *this;
        std::vector<P> parts = cat(root, o.root); RrbVector r; r.root = parts.size() == 1 ? parts[0] : inner(parts[0]->height + 1, parts); return r;
    }
    RrbVector pushBack(int v) const { RrbVector one; one.root = leaf({v}); return concat(one); }
    static P take(const P& n, size_t k) {                                                          // 앞 k 개 (0 < k <= 크기)
        if (k == sizeOf(n)) return n;
        if (n->height == 0) return leaf(std::vector<int>(n->items.begin(), n->items.begin() + (long)k));
        size_t c = 0; while (n->cum[c] < k) ++c; std::vector<P> kids(n->kids.begin(), n->kids.begin() + (long)c); kids.push_back(take(n->kids[c], c ? k - n->cum[c - 1] : k)); return inner(n->height, kids);
    }
    static P drop(const P& n, size_t k) {                                                          // 앞 k 개를 버린다 (0 <= k < 크기)
        if (k == 0) return n;
        if (n->height == 0) return leaf(std::vector<int>(n->items.begin() + (long)k, n->items.end()));
        size_t c = 0; while (n->cum[c] <= k) ++c; std::vector<P> kids{drop(n->kids[c], c ? k - n->cum[c - 1] : k)}; kids.insert(kids.end(), n->kids.begin() + (long)c + 1, n->kids.end()); return inner(n->height, kids);
    }
    RrbVector slice(size_t from, size_t to) const {                                                // [from, to)
        RrbVector r; if (from >= to) return r;
        P p = drop(take(root, to), from); while (p->height > 0 && p->kids.size() == 1) p = p->kids[0]; r.root = p; return r;              // 뿌리에 자식이 하나뿐이면 한 층 걷어낸다
    }
    static bool valid(const P& n, int h) {
        if (n->height != h) return false;
        if (h == 0) return !n->items.empty() && (int)n->items.size() <= M;
        if (n->kids.empty() || (int)n->kids.size() > M || n->cum.size() != n->kids.size()) return false;
        size_t s = 0; for (size_t i = 0; i < n->kids.size(); ++i) { if (!valid(n->kids[i], h - 1)) return false; s += sizeOf(n->kids[i]); if (n->cum[i] != s) return false; }
        return true;
    }
    bool valid() const { return !root || valid(root, root->height); }
    static void nodes(const P& n, std::set<const Node*>& out) { out.insert(n.get()); for (const P& k : n->kids) nodes(k, out); }
    std::set<const Node*> nodeSet() const { std::set<const Node*> s; if (root) nodes(root, s); return s; }
};
std::vector<int> toVector(const RrbVector& v) { std::vector<int> out; for (size_t i = 0; i < v.size(); ++i) out.push_back(v.get(i)); return out; }

int main() {
    {   RrbVector a, b; for (int i = 0; i < 6; ++i) a = a.pushBack(i); for (int i = 6; i < 10; ++i) b = b.pushBack(i);        // 손으로 확인: 0..5 와 6..9 를 이어 붙인다
        RrbVector c = a.concat(b); assert(c.size() == 10 && c.valid() && (toVector(c) == std::vector<int>{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}));
        RrbVector d = c.set(7, 70); assert(c.get(7) == 7 && d.get(7) == 70 && d.get(6) == 6);                                    // 영속: c 는 그대로
        RrbVector s = c.slice(3, 8); assert(s.valid() && (toVector(s) == std::vector<int>{3, 4, 5, 6, 7})); }
    std::mt19937 rng(37); size_t worstFresh = 0;
    std::vector<std::pair<RrbVector, std::vector<int>>> history;
    {   RrbVector v; std::vector<int> model; int next = 0;
        for (int step = 0; step < 6000; ++step) {
            const int op = (int)(rng() % 10);
            if (op < 3) { v = v.pushBack(next); model.push_back(next++); }
            else if (op < 5 && model.size() < 3000) { const int len = (int)(rng() % 40); RrbVector piece; std::vector<int> pm; for (int i = 0; i < len; ++i) { piece = piece.pushBack(next); pm.push_back(next++); }
                const bool front = rng() % 2; RrbVector r = front ? piece.concat(v) : v.concat(piece);                    // 앞에 붙이거나 뒤에 붙인다
                std::vector<int> rm = model; rm.insert(front ? rm.begin() : rm.end(), pm.begin(), pm.end());
                std::set<const RrbVector::Node*> vs = v.nodeSet(), ps = piece.nodeSet(), rs = r.nodeSet(); size_t fresh = 0; for (const auto* n : rs) fresh += !vs.count(n) && !ps.count(n);   // 두 입력과 공유하지 않는 새 노드
                worstFresh = std::max(worstFresh, fresh); assert(fresh <= 2 * (size_t)(std::max(v.height(), piece.height()) + 1) + 2);
                v = r; model = rm; }
            else if (op == 5 && !model.empty()) { const size_t i = rng() % model.size(); const int x = (int)rng(); v = v.set(i, x); model[i] = x; }
            else if (op == 6 && model.size() > 2) { size_t a = rng() % model.size(), b = rng() % model.size(); if (a > b) std::swap(a, b); ++b; if (b - a >= 1) { v = v.slice(a, b); model = std::vector<int>(model.begin() + (long)a, model.begin() + (long)b); } }
            else if (!model.empty()) { const size_t i = rng() % model.size(); assert(v.get(i) == model[i]); }
            if (step % 50 == 0) { assert(v.valid() && v.size() == model.size()); history.push_back({v, model}); }
        }
        assert(toVector(v) == model && v.valid());
    }
    for (const auto& h : history) assert(toVector(h.first) == h.second && h.first.valid());       // 모든 옛 버전이 그대로
    RrbVector big; std::vector<int> bigModel; int next = 0;                                       // 작은 조각 수백 개를 이어 붙인 벡터의 높이
    for (int piece = 0; piece < 400; ++piece) { RrbVector p; const int len = 1 + (int)(rng() % 25); for (int i = 0; i < len; ++i) { p = p.pushBack(next); bigModel.push_back(next++); } big = big.concat(p); }
    assert(toVector(big) == bigModel && big.valid());
    int ideal = 0; for (size_t cap = M; cap < big.size(); cap *= M) ++ideal;                      // 가득 찬 트리라면 높이
    assert(big.height() <= ideal + 2);
    std::cout << "RRBVector: 6000 random push_back/set/concat/slice operations matched std::vector with the size-table invariants checked every 50 steps; all " << history.size() << " saved versions stayed intact; a concat created at most " << worstFresh << " new nodes; 400 concatenated pieces (" << big.size() << " elements, M=4) gave height " << big.height() << " vs ideal " << ideal << std::endl;
    return 0;
}
// Time Complexity: get·set O(M log_M N), concat·slice O(M log_M N) (이음매 한 줄만 다시 만든다), pushBack O(M log_M N)
// Space Complexity: O(N), 새 버전 하나는 경로만큼(O(M log_M N))의 새 노드
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
        double naive = (n + 1) * 4.0 / (n / 8.0);                          // 위치마다 32비트 누적 개수를 두는 배열: (n+1)*32 비트 / n 비트 = 약 3200%
        assert(overhead < 0.08 && naive > 31);                             // 원본 비트 배열 대비 약 6% 추가 공간 (누적 배열이면 3200%)
        std::cout << "Rank: density " << density << ", overhead " << overhead * 100 << "% (naive prefix array +" << (long)(naive * 100 + 0.5) << "%)" << std::endl;
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
#include <string>
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

std::string levelBits(const WaveletMatrix& w) {                         // 그림: 레벨마다 비트열(위에서 아래로 최상위 비트부터)과 0 의 개수 — 0 은 앞으로, 1 은 뒤로 안정 분할되어 다음 레벨이 된다
    std::string s; for (int b = 0; b < w.B; ++b) { s += "level " + std::to_string(b) + ": "; for (size_t i = 0; i < w.n; ++i) s += w.lv[b].ones[i + 1] - w.lv[b].ones[i] ? '1' : '0'; s += " zeros=" + std::to_string(w.lv[b].zeros) + "\n"; }
    return s;
}
int main() {
    {   const std::vector<uint32_t> s = {5, 1, 4, 3, 7, 0, 6, 2}; WaveletMatrix w(s, 3);                // 값 0..7 (3 비트) 8 개
        const std::string pic = "level 0: 10101010 zeros=4\nlevel 1: 01010011 zeros=4\nlevel 2: 10101010 zeros=4\n";
        assert(levelBits(w) == pic);                                                                    // 레벨 0 은 각 값의 최상위 비트(5=101 -> 1, 1=001 -> 0, ...), 0 인 값 4 개가 앞으로 가고 나머지가 뒤로 간다
        for (size_t i = 0; i < s.size(); ++i) assert(w.access(i) == s[i]);                              // 각 레벨의 비트를 이어 읽으면 값이 복원된다 (access(2): 1 -> 0 -> 0 = 100 = 4)
        assert(w.rank(4, 8) == 1 && w.rank(4, 2) == 0 && w.rank(7, 8) == 1);
        std::cout << pic; }
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
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

// FM-인덱스(문자열 관점의 요약, 정본은 String.md Part 9): BWT(Burrows–Wheeler 변환)와 두 표 C[c](c 보다 작은 문자 수), Occ(c, i)(BWT[0..i) 안의 c 개수)만으로 패턴의 출현 횟수를 원문 없이 O(|P|) 에 센다 (backward search).
//  원문을 BWT 로 압축해 두고도 검색이 되는 "자기 색인" 구조다.  LF 사상(행 → 한 글자 앞 접미사의 행)을 걸으면 *위치 찾기*(sampled SA: s 번째 위치마다만 저장)와 *원문 복원*(역변환)도 된다.  Occ 는 B = 64 칸마다 체크포인트 + 나머지 선형 스캔.
//  ① 전수: 이진 텍스트 길이 ≤ 10 전부 × 길이 ≤ 5 의 모든 패턴(빈 패턴 포함)에서 count·locate 가 순진한 탐색과 같고 restore() 가 원문을 복원 (표본 간격 s = 1, 3, 8)  ② 무작위 텍스트(알파벳 2~4, 길이 ≤ 300)  ③ 20 만 글자 DNA 텍스트 / 반복 텍스트에서 300 개 패턴을 순진한 탐색과 대조.
std::vector<int> buildSA(const std::string& s) {                                                                 // 접두사 두 배 + 계수 정렬 (센티널 '\0' 이 가장 작다)
    int n = (int)s.size(); int m = std::max(n, 256) + 1; std::vector<int> sa(n), rk(n), tmp(n), cnt(m, 0);
    for (int i = 0; i < n; ++i) { rk[i] = (unsigned char)s[i]; ++cnt[rk[i]]; } for (int i = 1; i < m; ++i) cnt[i] += cnt[i - 1]; for (int i = n - 1; i >= 0; --i) sa[--cnt[rk[i]]] = i;
    for (int k = 1;; k <<= 1) {
        int p = 0; for (int i = n - k; i < n; ++i) if (i >= 0) tmp[p++] = i; for (int j = 0; j < n; ++j) if (sa[j] >= k) tmp[p++] = sa[j] - k;
        std::fill(cnt.begin(), cnt.end(), 0); for (int i = 0; i < n; ++i) ++cnt[rk[i]]; for (int i = 1; i < m; ++i) cnt[i] += cnt[i - 1]; for (int j = n - 1; j >= 0; --j) sa[--cnt[rk[tmp[j]]]] = tmp[j];
        tmp[sa[0]] = 0; int classes = 1; for (int j = 1; j < n; ++j) { int x = sa[j], y = sa[j - 1]; int x2 = x + k < n ? rk[x + k] : -1, y2 = y + k < n ? rk[y + k] : -1; tmp[x] = (rk[x] == rk[y] && x2 == y2) ? classes - 1 : classes++; }
        rk = tmp; if (classes == n) break; }
    return sa; }
struct FMIndex {
    static const int B = 64; int N; std::string bwt; std::vector<int> rankOf, C, cp; int sigma; int sample;                // N = 센티널 포함 길이
    std::vector<int> sampledRows, sampledPos;                                                                    // SA[row] % sample == 0 인 행(오름차순)과 그 SA 값
    FMIndex(const std::string& text, int sampleRate) : sample(sampleRate) {
        std::string t = text + '\0'; N = (int)t.size(); std::vector<int> sa = buildSA(t); bwt.resize(N); for (int i = 0; i < N; ++i) bwt[i] = t[(sa[i] + N - 1) % N];
        rankOf.assign(256, -1); std::vector<int> present(256, 0); for (unsigned char c : t) present[c] = 1; sigma = 0; for (int c = 0; c < 256; ++c) if (present[c]) rankOf[c] = sigma++;
        C.assign(sigma + 1, 0); for (unsigned char c : t) ++C[rankOf[c] + 1]; for (int r = 0; r < sigma; ++r) C[r + 1] += C[r];                 // C[r] = r 번째 문자보다 작은 문자 수
        cp.assign((size_t)(N / B + 1) * sigma, 0); std::vector<int> run(sigma, 0); for (int i = 0; i < N; ++i) { if (i % B == 0) for (int r = 0; r < sigma; ++r) cp[(size_t)(i / B) * sigma + r] = run[r]; ++run[rankOf[(unsigned char)bwt[i]]]; }
        if (N % B == 0) for (int r = 0; r < sigma; ++r) cp[(size_t)(N / B) * sigma + r] = run[r];                    // i = N 의 체크포인트(N 이 B 의 배수일 때)
        for (int row = 0; row < N; ++row) if (sa[row] % sample == 0) { sampledRows.push_back(row); sampledPos.push_back(sa[row]); } }
    int occ(int r, int i) const { int base = (i / B) * B, c = cp[(size_t)(i / B) * sigma + r]; for (int j = base; j < i; ++j) c += rankOf[(unsigned char)bwt[j]] == r; return c; }              // BWT[0..i) 의 r 번째 문자 수
    int lf(int row) const { int r = rankOf[(unsigned char)bwt[row]]; return C[r] + occ(r, row); }
    bool range(const std::string& p, int& lo, int& hi) const {                                                    // backward search: p 로 시작하는 접미사의 행 구간 [lo, hi)
        lo = 0; hi = N; for (size_t k = p.size(); k-- > 0;) { int r = rankOf[(unsigned char)p[k]]; if (r < 0) return false; lo = C[r] + occ(r, lo); hi = C[r] + occ(r, hi); if (lo >= hi) return false; } return true; }
    int count(const std::string& p) const { int lo, hi; if (!range(p, lo, hi)) return 0; return hi - lo; }
    std::vector<int> locate(const std::string& p) const { std::vector<int> pos; int lo, hi; if (!range(p, lo, hi)) return pos;
        for (int row = lo; row < hi; ++row) { int r = row, steps = 0; for (;;) { auto it = std::lower_bound(sampledRows.begin(), sampledRows.end(), r); if (it != sampledRows.end() && *it == r) { pos.push_back(sampledPos[it - sampledRows.begin()] + steps); break; } r = lf(r); ++steps; } }
        std::sort(pos.begin(), pos.end()); return pos; }
    std::string restore() const { std::string t(N - 1, ' '); int row = 0; for (int k = N - 1; k >= 1; --k) { t[k - 1] = bwt[row]; row = lf(row); } return t; }          // 행 0 = 센티널 접미사 → 거꾸로 복원
};
std::vector<int> naiveFind(const std::string& t, const std::string& p) { std::vector<int> pos; if (p.empty()) { for (int i = 0; i <= (int)t.size(); ++i) pos.push_back(i); return pos; } for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) pos.push_back((int)i); return pos; }

int main() {
    { FMIndex fm("banana", 2); assert(fm.count("ana") == 2 && fm.count("na") == 2 && fm.count("x") == 0 && fm.count("") == 7 && fm.locate("ana") == (std::vector<int>{1, 3}) && fm.restore() == "banana" && fm.bwt == std::string("annb\0aa", 7)); }          // BWT(banana$) = annb$aa
    std::vector<std::string> patterns = {""}; for (int len = 1; len <= 5; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; patterns.push_back(s); }
    for (int len = 0; len <= 10; ++len) for (int m = 0; m < (1 << len); ++m) { std::string t; for (int b = len - 1; b >= 0; --b) t += (m >> b & 1) ? 'b' : 'a';
        for (int s : {1, 3, 8}) { FMIndex fm(t, s); assert(fm.restore() == t); for (auto& p : patterns) { std::vector<int> want = naiveFind(t, p); assert(fm.count(p) == (int)want.size()); if (!p.empty() || s == 1) assert(fm.locate(p) == want); } } }                  // ① 전수
    std::mt19937 rng(77);
    for (int it = 0; it < 200; ++it) { int n = 1 + (int)(rng() % 300), sigma = 2 + (int)(rng() % 3); std::string t(n, 'a'); for (char& c : t) c = (char)('a' + rng() % sigma); FMIndex fm(t, 1 + (int)(rng() % 10)); assert(fm.restore() == t);   // ②
        for (int q = 0; q < 30; ++q) { int pl = 1 + (int)(rng() % 6); std::string p; if (rng() % 2 && n >= pl) p = t.substr(rng() % (n - pl + 1), pl); else for (int i = 0; i < pl; ++i) p += (char)('a' + rng() % (sigma + 1)); std::vector<int> want = naiveFind(t, p); assert(fm.count(p) == (int)want.size() && fm.locate(p) == want); } }
    for (int mode = 0; mode < 2; ++mode) {                                                                       // ③ 20 만 글자
        const int n = 200000; std::string t(n, 'a'); if (mode == 0) for (char& c : t) c = "acgt"[rng() % 4]; else { std::string unit; for (int i = 0; i < 37; ++i) unit += "acgt"[rng() % 4]; for (int i = 0; i < n; ++i) t[i] = unit[i % 37]; }
        FMIndex fm(t, 32); assert(fm.restore() == t);
        for (int q = 0; q < 300; ++q) { int pl = 1 + (int)(rng() % 20); std::string p; if (rng() % 3) p = t.substr(rng() % (n - pl), pl); else for (int i = 0; i < pl; ++i) p += "acgt"[rng() % 4]; std::vector<int> want = naiveFind(t, p); assert(fm.count(p) == (int)want.size()); if (want.size() <= 300) assert(fm.locate(p) == want); }
    }
    std::cout << "FMIndex: BWT, C and Occ tables answered count/locate exactly like naive search for every binary text up to length 10 (sampling 1/3/8), restore() inverted the BWT, and 2*10^5-character DNA and periodic texts matched on 300 patterns each" << std::endl;
    return 0;
}
// Time Complexity: count O(|P|·B) (Occ 체크포인트 간격 B), locate 는 행마다 O(s·log) 걸음, 구성 O(n log n)
// Space Complexity: BWT n 바이트 + Occ 체크포인트 n/B·σ 정수 + SA 표본 n/s 개
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
// 각 노드마다 "자식 수만큼의 1 과 0 하나"를 이어 쓰고, 맨 앞에 가상 루트용 "10" 을 붙인다. 노드 n 개면 비트는 2n+1 개뿐이다 (*논리적* 비트 수: 이 데모는 읽기 쉽게 B 를 vector<int>, rank/select 표를 int 배열로 두므로 메모리까지 간결한 것은 아니다 —
// 진짜 간결 구조라면 B 는 비트 배열이고 rank/select 는 o(n) 비트짜리 디렉터리(Rank 항목처럼 블록 누적 개수)로 대신한다).
// rank/select 만으로 이동한다 (x = BFS 번호, 1-기준):
//   첫째 자식 = select0(x)+1 위치의 1 의 순번(rank1),  다음 형제 = 바로 다음 비트가 1 이면 y+1,  부모 = rank0(select1(y))
// 간선 라벨은 BFS 순서로 별도 배열에, "단어의 끝" 표시는 비트 배열 하나에 둔다
struct Louds {
    std::vector<int> B;                                                    // 비트열 (논리적으로 2n+1 비트, 여기서는 int 로 저장)
    std::vector<char> label;                                               // label[y] = 노드 y 로 들어오는 간선의 문자 (y >= 2, 1 번이 루트)
    std::vector<bool> terminal;                                            // terminal[y] = 단어의 끝인가
    std::vector<int> pos0, pos1, pre1;                                     // select0, select1 표와 rank1 접두합 (교육용 int 표: 진짜 간결 구조에서는 o(n) 디렉터리)
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
    size_t tableBits = (t.pre1.size() + t.pos0.size() + t.pos1.size()) * sizeof(int) * 8;   // 이 데모의 rank/select 표가 실제로 쓰는 비트 수
    std::cout << "SuccinctTrie: " << words.size() << " words, " << t.nodes() << " nodes, " << t.B.size() << " logical structure bits (2n+1; this demo stores B as int and its int rank/select tables take " << tableBits << " bits, which a real o(n) directory would replace) vs pointer trie " << t.nodes() * 4 * 8 << " bits for 4 children pointers" << std::endl;
    return 0;
}
// Time Complexity: 이동 O(1) (rank/select 가 O(1) 일 때), 단어 조회 O(|w|·σ)
// Space Complexity: 구조 2N+1 논리 비트 + 라벨 N 문자 (이 데모의 int 로 저장한 B 와 rank/select 표는 O(N) 워드; 간결 구현은 N 비트 + o(N) 디렉터리)
```

## BitmapIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// 비트맵 인덱스(Bitmap Index): 값이 몇 종류 안 되는 열(성별·상태·분류)에서 "값마다 행 번호 집합을 비트열 하나로" 저장한다. 행 i 가 그 값이면 비트 i = 1.
// WHERE 절의 AND·OR·NOT 이 비트열의 &, |, ~ 가 되어 워드 하나(64 행)를 한 명령으로 처리한다. 개수 세기는 popcount. OLAP·데이터 웨어하우스·검색 엔진(Lucene 의 필터 캐시)에서 쓴다.
// 정수 열의 범위 질의는 "비트 슬라이스 인덱스(BSI, O'Neil–Quass)": 값의 i 번째 비트를 모은 비트열 B 개로 열 전체를 가로로 자른다. x 이하 행 = 높은 비트부터 훑으며 "지금까지 x 와 같은 행(eq)" 에서
// x 의 비트가 1 인 자리에 0 을 가진 행을 "작은 행(lt)" 으로 옮긴다. 선택된 행의 합 = sum_i 2^i x popcount(슬라이스_i & 선택) — 행을 하나도 읽지 않고 집계한다.
// 비트맵이 드물게만 1 이면 워드 단위 연속 길이 압축(WAH 와 같은 발상: 전부 0 또는 전부 1 인 워드의 연속을 (비트, 길이) 하나로)이 크게 줄이고, AND 를 풀지 않고 실행의 두 포인터로 한다.
// 검증: ① 행 10 만 개 표(분류 8종·상태 3종·가격 0..1023)에서 동치·IN·AND/OR/NOT·범위·개수·가격 합 질의 수백 개를 행 훑기와 비교 ② 압축 후 풀면 원본이고, 압축한 채 AND 한 결과 == 풀어서 AND ③ 드문 비트맵의 압축률
typedef std::vector<uint64_t> Bits;
Bits zeros(size_t n) { return Bits((n + 63) / 64, 0); }
Bits ones(size_t n) { Bits b(zeros(n)); for (auto& w : b) w = ~0ULL; if (n % 64) b.back() = (1ULL << (n % 64)) - 1; return b; }
void setBit(Bits& b, size_t i) { b[i >> 6] |= 1ULL << (i & 63); }
Bits operator&(const Bits& a, const Bits& b) { Bits r(a); for (size_t i = 0; i < r.size(); ++i) r[i] &= b[i]; return r; }
Bits operator|(const Bits& a, const Bits& b) { Bits r(a); for (size_t i = 0; i < r.size(); ++i) r[i] |= b[i]; return r; }
Bits notBits(const Bits& a, size_t n) { Bits r(a); for (auto& w : r) w = ~w; if (n % 64) r.back() &= (1ULL << (n % 64)) - 1; return r; }
size_t popcount(const Bits& a) { size_t c = 0; for (uint64_t w : a) { while (w) { w &= w - 1; ++c; } } return c; }
struct BitmapIndex {                                                                               // 열 하나에 대한 동치 부호화 비트맵: 값 -> 행 집합
    size_t n; std::map<int, Bits> byValue;
    explicit BitmapIndex(const std::vector<int>& col) : n(col.size()) { for (size_t i = 0; i < n; ++i) { auto it = byValue.find(col[i]); if (it == byValue.end()) it = byValue.emplace(col[i], zeros(n)).first; setBit(it->second, i); } }
    Bits eq(int v) const { auto it = byValue.find(v); return it == byValue.end() ? zeros(n) : it->second; }
    Bits in(const std::vector<int>& vs) const { Bits r = zeros(n); for (int v : vs) r = r | eq(v); return r; }
};
struct BitSliced {                                                                                 // 정수 열의 비트 슬라이스: slice[i] = 값의 i 번째 비트가 1 인 행
    size_t n; int B; std::vector<Bits> slice;
    BitSliced(const std::vector<int>& col, int bits) : n(col.size()), B(bits), slice(bits, zeros(col.size())) { for (size_t r = 0; r < n; ++r) for (int i = 0; i < B; ++i) if (col[r] >> i & 1) setBit(slice[i], r); }
    void compare(int x, Bits& lt, Bits& eq) const {                                                // lt: 값 < x 인 행, eq: 값 == x 인 행
        lt = zeros(n); eq = ones(n);
        for (int i = B - 1; i >= 0; --i) { if (x >> i & 1) { lt = lt | (eq & notBits(slice[i], n)); eq = eq & slice[i]; } else eq = eq & notBits(slice[i], n); }
    }
    Bits lessEq(int x) const { Bits lt, eq; compare(x, lt, eq); return lt | eq; }
    Bits greaterEq(int x) const { Bits lt, eq; compare(x, lt, eq); return notBits(lt, n); }
    Bits between(int lo, int hi) const { return greaterEq(lo) & lessEq(hi); }
    long long sum(const Bits& sel) const { long long s = 0; for (int i = 0; i < B; ++i) s += (long long)popcount(slice[i] & sel) << i; return s; }
};
struct Seg { bool fill; bool bit; uint64_t count; uint64_t lit; };                                  // 워드 연속 길이 압축: 전부 0/1 인 워드 count 개, 또는 리터럴 워드 하나
std::vector<Seg> compress(const Bits& b) {
    std::vector<Seg> out;
    for (uint64_t w : b) {
        if (w == 0 || w == ~0ULL) { const bool bit = w != 0; if (!out.empty() && out.back().fill && out.back().bit == bit) ++out.back().count; else out.push_back({true, bit, 1, 0}); }
        else out.push_back({false, false, 1, w});
    }
    return out;
}
Bits decompress(const std::vector<Seg>& s) { Bits b; for (const Seg& g : s) { if (g.fill) b.insert(b.end(), g.count, g.bit ? ~0ULL : 0ULL); else b.push_back(g.lit); } return b; }
std::vector<Seg> andCompressed(const std::vector<Seg>& a, const std::vector<Seg>& b) {              // 풀지 않고 두 포인터로 AND
    std::vector<Seg> out; size_t i = 0, j = 0, ra = a.empty() ? 0 : a[0].count, rb = b.empty() ? 0 : b[0].count;
    auto emit = [&](uint64_t w, uint64_t cnt) { if (w == 0 || w == ~0ULL) { const bool bit = w != 0; if (!out.empty() && out.back().fill && out.back().bit == bit) out.back().count += cnt; else out.push_back({true, bit, cnt, 0}); } else out.push_back({false, false, 1, w}); };
    while (i < a.size() && j < b.size()) {
        if (a[i].fill && b[j].fill) { const uint64_t m = std::min(ra, rb); emit((a[i].bit && b[j].bit) ? ~0ULL : 0ULL, m); ra -= m; rb -= m; }          // 둘 다 연속 구간: 짧은 쪽만큼 한 번에
        else { const uint64_t wa = a[i].fill ? (a[i].bit ? ~0ULL : 0ULL) : a[i].lit, wb = b[j].fill ? (b[j].bit ? ~0ULL : 0ULL) : b[j].lit; emit(wa & wb, 1); --ra; --rb; }
        if (ra == 0 && ++i < a.size()) ra = a[i].count;
        if (rb == 0 && ++j < b.size()) rb = b[j].count;
    }
    return out;
}

int main() {
    {   const std::vector<int> col = {2, 0, 1, 0, 2, 2, 1, 0}; BitmapIndex ix(col);                  // 손으로 확인: 행 8 개, 값 0/1/2
        assert(ix.eq(0)[0] == 0x8AULL && ix.eq(1)[0] == 0x44ULL && ix.eq(2)[0] == 0x31ULL);          // 값 0 은 행 1,3,7 -> 0b10001010, 값 1 은 행 2,6, 값 2 은 행 0,4,5
        assert(popcount(ix.in({0, 2})) == 6 && ix.eq(9)[0] == 0 && notBits(ix.eq(0), 8)[0] == 0x75ULL); }
    std::mt19937 rng(41); const size_t n = 100000; std::vector<int> cat(n), status(n), price(n);
    for (size_t i = 0; i < n; ++i) { cat[i] = (int)(rng() % 8); status[i] = (int)(rng() % 3); price[i] = (int)(rng() % 1024); }
    BitmapIndex ci(cat), si(status); BitSliced pi(price, 10);
    for (int q = 0; q < 300; ++q) {
        const int c = (int)(rng() % 8), st = (int)(rng() % 3); int lo = (int)(rng() % 1024), hi = (int)(rng() % 1024); if (lo > hi) std::swap(lo, hi);
        const std::vector<int> cs = {(int)(rng() % 8), (int)(rng() % 8), (int)(rng() % 8)};
        Bits sel = (ci.eq(c) & notBits(si.eq(st), n)) | (ci.in(cs) & pi.between(lo, hi));          // (분류 = c AND 상태 != st) OR (분류 IN cs AND 가격 BETWEEN lo AND hi)
        size_t cnt = 0; long long sum = 0;
        for (size_t r = 0; r < n; ++r) {
            const bool inCs = std::find(cs.begin(), cs.end(), cat[r]) != cs.end();
            const bool want = (cat[r] == c && status[r] != st) || (inCs && price[r] >= lo && price[r] <= hi);
            assert(((sel[r >> 6] >> (r & 63)) & 1) == (uint64_t)want);
            cnt += want; sum += want ? price[r] : 0;
        }
        assert(popcount(sel) == cnt && pi.sum(sel) == sum);                                          // 개수는 popcount, 가격 합은 슬라이스 popcount 의 가중합 (행을 읽지 않는다)
        Bits le = pi.lessEq(lo), ge = pi.greaterEq(hi); size_t cl = 0, cg = 0; for (size_t r = 0; r < n; ++r) { cl += price[r] <= lo; cg += price[r] >= hi; } assert(popcount(le) == cl && popcount(ge) == cg);
    }
    {   Bits sparse = zeros(1 << 20); for (int i = 0; i < 40; ++i) setBit(sparse, rng() % (1 << 20)); Bits other = zeros(1 << 20); for (int i = 0; i < 40; ++i) setBit(other, rng() % (1 << 20));
        for (int i = 0; i < 4000; ++i) setBit(other, 5000 + (size_t)i);                              // other 에는 연속한 1 구간도 있다
        auto cs = compress(sparse), co = compress(other);
        assert(decompress(cs) == sparse && decompress(co) == other);
        assert(decompress(andCompressed(cs, co)) == (sparse & other));                               // 압축한 채 AND == 풀어서 AND
        assert(cs.size() <= 100 && cs.size() * 20 < sparse.size());                                  // 1 이 40 개뿐인 2^20 비트 열: 16384 워드 -> 100 개 이하의 구간
        std::cout << "BitmapIndex: 300 random AND/OR/NOT/IN/BETWEEN queries over 100000 rows matched a row scan (counts and SUM(price) via bit slices); a 2^20-bit bitmap with 40 ones compressed from " << sparse.size() << " words to " << cs.size() << " runs, AND-ed without decompression" << std::endl; }
    return 0;
}
// Time Complexity: 동치·AND·OR·NOT O(N/64), 범위 질의·합 O(B·N/64) (B: 값의 비트 수), 압축 AND O(두 압축열 길이의 합)
// Space Complexity: 동치 부호화 O(C·N/8) 바이트(C: 서로 다른 값 수), 비트 슬라이스 O(B·N/8)
```
# Part 3. 확률적 자료구조
## BloomFilter()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 블룸 필터: "이 키가 집합에 있을 수도 있다 / 확실히 없다" 만 답하는 확률적 집합.  m 비트 배열과 해시 k 개. 삽입은 k 개 비트를 켜고, 조회는 k 개가 모두 켜졌는지 본다.
//  거짓 음성은 없고(넣은 키는 항상 "있을 수도"), 거짓 양성 확률은 p ≈ (1 − e^(−kn/m))^k.  목표 p 와 개수 n 이 주어지면 m = −n ln p / (ln 2)², k = (m/n) ln 2 가 최적이고 그때 원소당 약 1.44·log2(1/p) 비트(p = 1% 이면 9.6 비트)면 된다.
//  해시 k 개는 해시 둘로 흉내 낸다(Kirsch–Mitzenmacher: h1 + i·h2).  OR 로 합집합, 삭제는 불가(→ Counting/Cuckoo).  검증(결정적 시드): ① 크기 공식 ② 거짓 음성 0 ③ 측정한 거짓 양성률이 이론값과 *이항 분포 5σ* 안
//  ④ k 를 1..12 로 바꾼 곡선이 이론 곡선과 맞고 최솟값이 k = (m/n) ln 2 근처  ⑤ 합집합: 두 필터의 OR 이 합집합으로 만든 필터와 *비트 단위로 같다*, AND 는 교집합의 키를 놓치지 않는다  ⑥ 켜진 비트 수 X 로 개수 추정 n̂ = −(m/k)·ln(1 − X/m)  ⑦ 이중 해시 vs k 개 독립 해시.
static uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }     // splitmix64
struct Bloom {
    size_t m; int k; bool independent; std::vector<uint64_t> bits;
    Bloom(size_t m_, int k_, bool indep = false) : m(m_), k(k_), independent(indep), bits((m_ + 63) / 64, 0) {}
    static Bloom sized(size_t n, double p) { double m = std::ceil(-(double)n * std::log(p) / (std::log(2.0) * std::log(2.0))); int k = std::max(1, (int)std::lround(m / (double)n * std::log(2.0))); return Bloom((size_t)m, k); }
    size_t idx(uint64_t key, int i) const { if (independent) return (size_t)(mix(key + 0x1000000ULL * (uint64_t)(i + 1)) % m); uint64_t h1 = mix(key), h2 = mix(key ^ 0xD6E8FEB86659FD93ULL) | 1; return (size_t)((h1 + (uint64_t)i * h2) % m); }
    void add(uint64_t key) { for (int i = 0; i < k; ++i) { size_t b = idx(key, i); bits[b >> 6] |= 1ULL << (b & 63); } }
    bool maybe(uint64_t key) const { for (int i = 0; i < k; ++i) { size_t b = idx(key, i); if (!(bits[b >> 6] >> (b & 63) & 1)) return false; } return true; }
    size_t popcount() const { size_t c = 0; for (uint64_t w : bits) c += (size_t)__builtin_popcountll(w); return c; }
    double estimate() const { return -((double)m / k) * std::log(1.0 - (double)popcount() / (double)m); }       // 켜진 비트 수로부터 원소 수 추정
};
double theory(size_t m, int k, size_t n) { return std::pow(1.0 - std::exp(-(double)k * (double)n / (double)m), k); }
double measure(const Bloom& f, uint64_t lo, long trials) { long fp = 0; for (long i = 0; i < trials; ++i) fp += f.maybe(lo + (uint64_t)i); return (double)fp / (double)trials; }       // 키 공간이 [0, lo) 와 겹치지 않는 부재 키

int main() {
    const size_t n = 100000; Bloom f = Bloom::sized(n, 0.01);                                                    // ① 크기 공식
    assert(f.m == 958506 && f.k == 7 && std::fabs((double)f.m / n - 1.4427 * std::log2(100.0)) < 0.01);       // 원소당 9.585 비트 ≈ 1.44·log2(1/p)
    for (uint64_t i = 0; i < n; ++i) f.add(i); for (uint64_t i = 0; i < n; ++i) assert(f.maybe(i));          // ② 거짓 음성 0
    const long T = 1000000; double p = theory(f.m, f.k, n), meas = measure(f, 1ULL << 40, T), sigma = std::sqrt(p * (1 - p) / T); assert(std::fabs(meas - p) < 5 * sigma && meas < 0.0125 && meas > 0.0075);   // ③ 이론값(≈1.0%)과 5σ 이내
    const size_t m = 600000; double bestMeas = 1, bestTheory = 1; int bestK = 0, bestKT = 0;                    // ④ k 곡선 (m 고정, n = 50000)
    for (int k = 1; k <= 12; ++k) { Bloom g(m, k); for (uint64_t i = 0; i < 50000; ++i) g.add(i); double t = theory(m, k, 50000), a = measure(g, 1ULL << 40, 200000), s = std::sqrt(t * (1 - t) / 200000); assert(std::fabs(a - t) < 5 * s + 1e-4);
        if (a < bestMeas) { bestMeas = a; bestK = k; } if (t < bestTheory) { bestTheory = t; bestKT = k; } }
    int kopt = (int)std::lround((double)m / 50000 * std::log(2.0)); assert(std::abs(bestK - kopt) <= 1 && bestKT == kopt);
    { Bloom a(500000, 6), b(500000, 6), u(500000, 6), in(500000, 6); std::set<uint64_t> sa, sb; std::mt19937_64 rng(5); for (int i = 0; i < 30000; ++i) { uint64_t x = rng() % 100000, y = rng() % 100000; a.add(x); sa.insert(x); b.add(y); sb.insert(y); u.add(x); u.add(y); }
      Bloom orF = a; for (size_t i = 0; i < orF.bits.size(); ++i) orF.bits[i] |= b.bits[i]; assert(orF.bits == u.bits);                  // ⑤ OR = 합집합으로 만든 필터와 비트 단위로 같다
      Bloom andF = a; for (size_t i = 0; i < andF.bits.size(); ++i) andF.bits[i] &= b.bits[i]; for (uint64_t x : sa) if (sb.count(x)) assert(andF.maybe(x)); }
    { Bloom g(1000000, 7); for (uint64_t i = 0; i < 80000; ++i) g.add(i * 7919); double e = g.estimate(); assert(std::fabs(e - 80000) < 0.02 * 80000); }          // ⑥ 개수 추정 오차 2% 이내
    { Bloom dbl(958506, 7, false), ind(958506, 7, true); for (uint64_t i = 0; i < n; ++i) { dbl.add(i); ind.add(i); } double t = theory(958506, 7, n), s = std::sqrt(t * (1 - t) / T); double a = measure(dbl, 1ULL << 40, T), b = measure(ind, 1ULL << 40, T); assert(std::fabs(a - t) < 5 * s && std::fabs(b - t) < 5 * s);   // ⑦ 이중 해시도 독립 해시만큼 좋다
      std::cout << "BloomFilter: sized 958506 bits / 7 hashes for 10^5 keys at 1% (9.585 bits per key), zero false negatives, measured false-positive rate " << meas << " vs theory " << p << ", the k-sweep minimum fell at k=" << bestK << " (optimum " << kopt << "), OR equalled the filter of the union bit for bit, and double hashing (" << a << ") matched independent hashing (" << b << ")" << std::endl; }
    return 0;
}
// Time Complexity: 삽입·조회 O(k)
// Space Complexity: 약 1.44 n log2(1/p) 비트
```
## CountingBloomFilter()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// 카운팅 블룸 필터: 비트 대신 작은 카운터(보통 4비트)를 두어 삭제를 지원한다. 삽입은 k 개 카운터 +1, 삭제는 −1, 조회는 모두 > 0 인지.
//  4비트(최대 15)면 충분한 이유: 카운터 하나가 16 이상이 될 확률이 m·1.37e−15 수준이라 무시할 만하다.  그래도 포화(15)한 카운터는 "더 이상 줄이지 않는다" — 줄이면 실제보다 낮아져 거짓 음성이 생길 수 있기 때문이다.
//  (일반 블룸 필터보다 공간 4배.  없는 키를 삭제하면 필터가 깨지므로 "넣었던 키만 삭제" 가 전제)  검증: ① 무작위 삽입·삭제 20 만 번 동안 (997 단계마다 약 200 번, 그리고 끝에서) *지금 들어 있는 모든 키*를 전수 조회해 모두 "있을 수도" (거짓 음성 0)  ② 전부 지우면 필터가 비어 있다 (포화가 없었다면)
//  ③ 거짓 양성률이 이론값(블룸 필터와 같은 식)과 5σ 이내  ④ 포화 규칙의 필요성: 카운터 하나(m = 1)에 20 개 키를 넣어 포화시킨 뒤 19 개를 지우면, 규칙을 지킨 필터는 남은 키를 계속 "있을 수도"로 답하지만 포화를 무시하고 줄이는 필터는 거짓 음성을 낸다
//  ⑤ 부하 ln 2 에서 관측된 최대 카운터 값이 15 보다 훨씬 작다.
static uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }
struct CBloom {
    size_t m; int k; bool honorSaturation; std::vector<uint8_t> bytes; long saturated = 0;                        // 카운터 두 개를 한 바이트에 (하위·상위 4비트)
    CBloom(size_t m_, int k_, bool honor = true) : m(m_), k(k_), honorSaturation(honor), bytes((m_ + 1) / 2, 0) {}
    int get(size_t i) const { return (bytes[i >> 1] >> ((i & 1) * 4)) & 15; }
    void put(size_t i, int v) { int sh = (int)((i & 1) * 4); bytes[i >> 1] = (uint8_t)((bytes[i >> 1] & ~(15 << sh)) | (v << sh)); }
    size_t idx(uint64_t key, int i) const { uint64_t h1 = mix(key), h2 = mix(key ^ 0xD6E8FEB86659FD93ULL) | 1; return (size_t)((h1 + (uint64_t)i * h2) % m); }
    void add(uint64_t key) { for (int i = 0; i < k; ++i) { size_t b = idx(key, i); int c = get(b); if (c < 15) { put(b, c + 1); if (c + 1 == 15) ++saturated; } } }       // 15 에서 멈춘다
    void remove(uint64_t key) { for (int i = 0; i < k; ++i) { size_t b = idx(key, i); int c = get(b); if (c == 15 && honorSaturation) continue; if (c > 0) put(b, c - 1); } }    // 포화한 카운터는 줄이지 않는다
    bool maybe(uint64_t key) const { for (int i = 0; i < k; ++i) if (get(idx(key, i)) == 0) return false; return true; }
    int maxCounter() const { int mx = 0; for (size_t i = 0; i < m; ++i) mx = std::max(mx, get(i)); return mx; }
    bool empty() const { for (uint8_t b : bytes) if (b) return false; return true; }
};

int main() {
    std::mt19937_64 rng(3); CBloom f(400000, 5); std::map<uint64_t, int> live; long ops = 0;                       // ① ②
    for (int step = 0; step < 200000; ++step) {
        if (live.empty() || rng() % 100 < 55) { uint64_t key = rng() % 60000; f.add(key); ++live[key]; }
        else { auto it = live.begin(); std::advance(it, (long)(rng() % live.size())); f.remove(it->first); if (--it->second == 0) live.erase(it); }
        ++ops; if (step % 997 == 0) for (auto& kv : live) assert(f.maybe(kv.first)); }                             // 지금 있는 키는 모두 "있을 수도"
    for (auto& kv : live) assert(f.maybe(kv.first));
    CBloom g(400000, 5); for (int i = 0; i < 30000; ++i) g.add((uint64_t)i * 31 + 7); assert(!g.empty()); for (int i = 0; i < 30000; ++i) g.remove((uint64_t)i * 31 + 7); assert(g.empty() && g.saturated == 0);               // ② 전부 지우면 비어 있다
    CBloom h(600000, 6); const int n = 60000; for (int i = 0; i < n; ++i) h.add((uint64_t)i); const long T = 400000; long fp = 0; for (long i = 0; i < T; ++i) fp += h.maybe((1ULL << 40) + (uint64_t)i); double p = std::pow(1.0 - std::exp(-6.0 * n / 600000), 6), meas = (double)fp / T, sigma = std::sqrt(p * (1 - p) / T);
    assert(std::fabs(meas - p) < 5 * sigma);                                                                      // ③
    { CBloom good(1, 1, true), bad(1, 1, false); for (uint64_t key = 0; key < 20; ++key) { good.add(key); bad.add(key); } assert(good.get(0) == 15 && bad.get(0) == 15);                      // ④ 포화
      for (uint64_t key = 0; key < 19; ++key) { good.remove(key); bad.remove(key); } assert(good.maybe(19) && !bad.maybe(19)); }                          // 규칙을 지키면 남은 키가 살아 있고, 안 지키면 거짓 음성
    { CBloom e(1000000, 5); const int cnt = (int)(1000000 * std::log(2.0) / 5); for (int i = 0; i < cnt; ++i) e.add((uint64_t)i); int mx = e.maxCounter(); assert(mx < 12 && e.saturated == 0);  // ⑤
      std::cout << "CountingBloomFilter: " << ops << " random insert/remove operations never lost a live key (full live-key check every 997th step and at the end), removing everything emptied the filter, false-positive rate " << meas << " matched theory " << p << ", a saturated counter kept a surviving key visible (the naive variant lost it), and at load ln 2 the largest 4-bit counter was only " << mx << std::endl; }
    return 0;
}
// Time Complexity: 삽입·삭제·조회 O(k)
// Space Complexity: 카운터당 4비트 → 블룸 필터의 4배
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
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 하이퍼로그로그: 서로 다른 원소의 수(카디널리티)를 수 KB 로 ±1~2% 오차로 센다. 아이디어: 해시를 이진수로 보면 "앞쪽 0 이 k 개 이어지는" 값은 약 2^k 개를 봐야 한 번 나온다.
// 해시의 앞 p 비트로 m = 2^p 개의 레지스터 중 하나를 고르고, 나머지 비트의 "앞쪽 0 의 개수 + 1"(rho)의 최댓값을 레지스터에 기록한다.
// 추정 = α_m · m² / Σ 2^(-레지스터)  (조화 평균으로 이상치를 눌러 준다).  작은 값에서는 빈 레지스터 수 V 로 선형 카운팅 m ln(m/V) 을 쓴다. 표준 오차 ≈ 1.04/√m
// 합집합은 레지스터별 max 한 번으로 정확히(손실 없이) 병합된다 -> 분산 집계에 적합
//  ① 레지스터 *자체* 검증: p = 4, 8, 12, 14 에서 20 만 개를 넣은 레지스터 배열이, 해시를 비트 하나씩 훑어 앞쪽 0 을 세는 독립 오라클이 계산한 배열과 정확히 같다  ② 병합 법칙: 두 집합의 병합 == 합집합 스트림을 직접 넣은 것(교환·결합·멱등), 같은 원소를 두 번 넣어도 레지스터 불변
//  ③ 통계: p = 10(표준 오차 1.04/√m = 3.25%) 에서 서로 다른 원소 2 만 개짜리 독립 시행 400 번의 평균 오차가 0 에서 3σ/√400 이내이고 제곱평균 제곱근(RMS)이 이론 표준 오차의 0.8~1.2 배  ④ rho 분포: 무작위 해시 100 만 개에서 "앞쪽 0 의 개수 + 1 = k" 인 개수가 N·2^−k 의 5σ 이내 (k = 1..12)
//  ⑤ 범위 훑기: p = 12 로 n = 50 … 100 만 (작은 범위 보정이 바뀌는 2.5m = 10 240 근처 포함)에서 상대 오차 < 8% (표준 오차의 5 배), 아주 작은 n 은 절대 오차 ≤ 3
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
    {   auto oracleRho = [](uint64_t h, int p) { uint64_t w = h << p; int k = 1; for (int bit = 63; bit >= 0 && !((w >> bit) & 1); --bit) ++k; return std::min(k, 64 - p + 1); };           // ① 독립 오라클
        for (int p : {4, 8, 12, 14}) { HLL h(p); std::vector<uint8_t> want((size_t)1 << p, 0); std::mt19937_64 rng(1000 + p); for (int i = 0; i < 200000; ++i) { uint64_t x = rng(); h.add(x); uint64_t hh = mix(x); size_t idx = hh >> (64 - p); want[idx] = (uint8_t)std::max<int>(want[idx], oracleRho(hh, p)); } assert(h.reg == want); } }
    {   HLL x(10), y(10), u(10), twice(10); std::mt19937_64 rng(5); std::vector<uint64_t> xs(5000), ys(5000), zs(3000); for (auto& v : xs) v = rng(); for (auto& v : ys) v = rng(); for (auto& v : zs) v = rng();             // ② 병합 법칙
        for (uint64_t v : xs) { x.add(v); u.add(v); twice.add(v); twice.add(v); } for (uint64_t v : ys) { y.add(v); u.add(v); } assert(x.reg == twice.reg);
        HLL xy = x; xy.merge(y); HLL yx = y; yx.merge(x); assert(xy.reg == u.reg && yx.reg == u.reg); HLL again = xy; again.merge(x); again.merge(y); assert(again.reg == xy.reg);
        HLL z(10); for (uint64_t v : zs) z.add(v); HLL left = xy; left.merge(z); HLL yz = y; yz.merge(z); HLL right = x; right.merge(yz); assert(left.reg == right.reg); }
    {   const int p = 10, trials = 400; const double n = 20000, se = 1.04 / std::sqrt((double)(1 << p)); double sum = 0, sq = 0; std::mt19937_64 rng(77);                                                          // ③ 통계
        for (int t = 0; t < trials; ++t) { HLL h(p); for (int i = 0; i < (int)n; ++i) h.add(rng()); double e = (h.estimate() - n) / n; sum += e; sq += e * e; }
        double mean = sum / trials, rms = std::sqrt(sq / trials); assert(std::fabs(mean) < 3 * se / std::sqrt((double)trials) && rms > 0.8 * se && rms < 1.2 * se); }
    {   const uint64_t N = 1000000; long cnt[14] = {0}; std::mt19937_64 rng(31); for (uint64_t i = 0; i < N; ++i) { uint64_t w = rng() << 4; int k = 1; for (int bit = 63; bit >= 0 && !((w >> bit) & 1); --bit) ++k; if (k <= 13) ++cnt[k]; }                // ④ rho 분포
        for (int k = 1; k <= 12; ++k) { double expect = (double)N / std::pow(2.0, k); assert(std::fabs(cnt[k] - expect) <= 5 * std::sqrt(expect)); } }
    {   const int p = 12; const double se = 1.04 / std::sqrt((double)(1 << p));                                                                                                                               // ⑤ 범위 훑기
        for (size_t n : {50u, 100u, 500u, 1000u, 5000u, 8000u, 10240u, 10300u, 12000u, 20000u, 50000u, 200000u, 1000000u}) { HLL h(p); for (uint64_t i = 0; i < n; ++i) h.add(i * 0x9e3779b97f4a7c15ULL + 12345); double e = h.estimate();
            if (n <= 100) assert(std::fabs(e - (double)n) <= 3.0); else assert(std::fabs(e - (double)n) / (double)n < 5 * se); } }
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
## MisraGries()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// Misra–Gries 요약: 스트림을 한 번 훑으며 카운터 k 개만으로 "자주 나오는 항목" 을 찾는다. 항목이 카운터에 있으면 +1, 없고 빈 카운터가 있으면 새로 달고,
// 카운터가 가득 찼으면 모든 카운터를 -1 한다(0 이 된 것은 제거). 이 "전체 -1" 은 서로 다른 k+1 개(카운터 k 개 + 방금 온 항목)를 한 개씩 지우는 것과 같고,
// 그런 삭제는 많아야 n/(k+1) 번뿐이므로 어떤 항목 x 의 추정치는 f(x) - n/(k+1) <= est(x) <= f(x) (항상 과소 추정), 빈도가 n/(k+1) 를 넘는 항목은 반드시 요약에 남는다.
// 요약끼리 합칠 수 있다(mergeable summary): 카운터를 더한 뒤 (k+1) 번째로 큰 값을 모든 카운터에서 빼고 양수만 남기면 합친 스트림에 대해 같은 보장이 성립한다.
// 검증: ① 손으로 따라간 작은 예 ② 치우친 스트림·균일 스트림·전부 다른 항목 스트림에서 모든 항목의 오차 한계와 "빈번 항목은 반드시 있다", 그리고 n - (남은 카운터 합) = (k+1) x (전체 -1 횟수)
//       ③ 스트림을 둘로 나눠 각각 요약한 뒤 합쳐도 같은 한계 ④ 카운터 수는 k 를 넘지 않는다
struct MisraGries {
    size_t k; std::map<int, long> c; long n = 0, rounds = 0;                       // c: 항목 -> 카운터, rounds: "전체 -1" 을 한 횟수
    explicit MisraGries(size_t k_) : k(k_) {}
    void add(int x) {
        ++n; auto it = c.find(x);
        if (it != c.end()) { ++it->second; return; }
        if (c.size() < k) { c[x] = 1; return; }
        ++rounds;                                                                   // 가득 참: 새 항목을 달지 않고 모든 카운터를 하나씩 줄인다
        for (auto i = c.begin(); i != c.end();) { if (--i->second == 0) i = c.erase(i); else ++i; }
    }
    long estimate(int x) const { auto it = c.find(x); return it == c.end() ? 0 : it->second; }
    long counted() const { long s = 0; for (const auto& kv : c) s += kv.second; return s; }
    void merge(const MisraGries& o) {
        n += o.n; for (const auto& kv : o.c) c[kv.first] += kv.second;
        if (c.size() <= k) return;
        std::vector<long> v; for (const auto& kv : c) v.push_back(kv.second);
        std::nth_element(v.begin(), v.begin() + (long)k, v.end(), std::greater<long>());
        const long cut = v[k];                                                     // (k+1) 번째로 큰 카운터: 이만큼 모두에게서 빼면 많아야 k 개가 양수로 남는다
        for (auto i = c.begin(); i != c.end();) { i->second -= cut; if (i->second <= 0) i = c.erase(i); else ++i; }
    }
};
std::map<int, long> exact(const std::vector<int>& s) { std::map<int, long> f; for (int x : s) ++f[x]; return f; }
void checkGuarantee(const MisraGries& mg, const std::map<int, long>& f) {
    for (const auto& kv : f) {
        const long est = mg.estimate(kv.first);
        assert(est <= kv.second && (kv.second - est) * (long)(mg.k + 1) <= mg.n);   // f - n/(k+1) <= est <= f
        if (kv.second * (long)(mg.k + 1) > mg.n) assert(est > 0);                     // 빈도 > n/(k+1) 이면 반드시 요약에 있다
    }
    assert(mg.c.size() <= mg.k);
}

int main() {
    {   MisraGries mg(2); for (int x : {1, 2, 1, 3, 1, 4, 1, 5}) mg.add(x);                // 손으로 따라간 예: k=2, 스트림 1 2 1 3 1 4 1 5
        assert(mg.n == 8 && mg.rounds == 2 && mg.c.size() == 1 && mg.estimate(1) == 2);       // 3 과 5 가 올 때 전체 -1 이 두 번 → 1 은 4 번 나왔지만 2 로 추정(오차 2 <= 8/3)
        assert(mg.n - mg.counted() == 3 * mg.rounds); }
    std::mt19937 rng(11);
    for (int kind = 0; kind < 3; ++kind) for (size_t k : {1, 2, 5, 10, 50}) for (int rep = 0; rep < 8; ++rep) {
        std::vector<int> s; const int n = 2000 + (int)(rng() % 20000);
        for (int i = 0; i < n; ++i) s.push_back(kind == 0 ? (rng() % 1000 < 500 ? (int)(rng() % 3) : (int)(rng() % 200))      // 항목 0,1,2 가 각각 약 17%
                                              : kind == 1 ? (int)(rng() % 40) : i);                                           // 균일 40 종 / 전부 다른 항목
        MisraGries mg(k); for (int x : s) mg.add(x);
        const auto f = exact(s); checkGuarantee(mg, f);
        assert(mg.n - mg.counted() == (long)(k + 1) * mg.rounds);                                                          // 지운 총량 = (k+1) x 횟수
        const size_t half = s.size() / 3; MisraGries a(k), b(k);                                                           // 스트림을 둘로 나눠 요약한 뒤 합친다
        for (size_t i = 0; i < s.size(); ++i) (i < half ? a : b).add(s[i]);
        a.merge(b); assert(a.n == mg.n); checkGuarantee(a, f);
        if (kind == 0 && k >= 5) for (int hot = 0; hot < 3; ++hot) assert(a.estimate(hot) > 0 && mg.estimate(hot) > 0);  // 17% > 1/(k+1) 인 세 항목은 반드시 남는다
    }
    std::cout << "MisraGries: error bound f-n/(k+1) <= est <= f held for every item on 120 streams (skewed / uniform / all-distinct, k=1..50), also after merging two halves; n - sum(counters) == (k+1) * rounds" << std::endl;
    return 0;
}
// Time Complexity: add 분할상환 O(1)~O(k) (전체 -1 은 k 개 카운터를 훑지만 그 전에 최소 k 번 +1 이 필요), merge O(k)
// Space Complexity: O(k)
```

## SpaceSaving()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <unordered_map>
#include <vector>

// Space-Saving (Metwally 등): 카운터 k 개를 최소 힙으로 들고 있다가, 모니터링 안 하는 항목이 오면 "가장 작은 카운터" 의 항목을 쫓아내고 그 자리를 (최솟값 + 1) 로 물려받는다.
// 항목마다 오차 err(물려받은 값)를 함께 기록하므로 구간 [count - err, count] 가 진짜 빈도를 반드시 포함한다. 모든 카운터의 합은 늘 n(=지금까지의 항목 수)이고, 따라서 최솟값 <= n/k 이다.
// 빈도가 n/k 를 넘는 항목은 반드시 모니터링되고, 모니터링되지 않는 항목의 빈도는 최솟값 이하이다. Misra–Gries 와 달리 과대 추정이며 상위 k 순위에 더 정확하다.
// 검증: ① 손으로 따라간 예 ② 치우친·균일·전부 다른 스트림에서 매 단계 "합 == n", 모니터링 항목은 count - err <= f <= count, 비모니터링 항목은 f <= min, n/k 초과 빈도는 반드시 모니터링
//       ③ 힙 불변식(부모 <= 자식)과 위치 표 일치
struct SpaceSaving {
    struct Slot { int item; long count, err; };
    size_t k; std::vector<Slot> h; std::unordered_map<int, size_t> pos; long n = 0;       // h: count 기준 최소 힙, pos: 항목 -> 힙 위치
    explicit SpaceSaving(size_t k_) : k(k_) {}
    void put(size_t i, const Slot& s) { h[i] = s; pos[s.item] = i; }
    void siftUp(size_t i) { Slot s = h[i]; while (i > 0 && h[(i - 1) / 2].count > s.count) { put(i, h[(i - 1) / 2]); i = (i - 1) / 2; } put(i, s); }
    void siftDown(size_t i) {
        Slot s = h[i];
        for (;;) { size_t l = 2 * i + 1, r = l + 1, m = l; if (l >= h.size()) break; if (r < h.size() && h[r].count < h[l].count) m = r; if (h[m].count >= s.count) break; put(i, h[m]); i = m; }
        put(i, s);
    }
    void add(int x) {
        ++n; auto it = pos.find(x);
        if (it != pos.end()) { ++h[it->second].count; siftDown(it->second); return; }       // 모니터링 중: 카운터만 +1 (커졌으니 아래로)
        if (h.size() < k) { h.push_back({x, 1, 0}); pos[x] = h.size() - 1; siftUp(h.size() - 1); return; }
        Slot& root = h[0]; pos.erase(root.item); const long m = root.count;                    // 가장 작은 카운터의 항목을 쫓아낸다
        root = {x, m + 1, m}; pos[x] = 0; siftDown(0);                                         // 새 항목: 카운터 m+1, 오차 m (최대 m 번은 이미 나왔을 수 있다)
    }
    long minCount() const { return h.size() < k ? 0 : h[0].count; }
    const Slot* find(int x) const { auto it = pos.find(x); return it == pos.end() ? nullptr : &h[it->second]; }
    bool valid() const {
        long sum = 0; for (size_t i = 0; i < h.size(); ++i) { sum += h[i].count; if (i && h[(i - 1) / 2].count > h[i].count) return false; auto it = pos.find(h[i].item); if (it == pos.end() || it->second != i) return false; }
        return sum == n && pos.size() == h.size();
    }
};

int main() {
    {   SpaceSaving ss(2); for (int x : {1, 2, 1, 3, 1, 4, 1, 5}) ss.add(x);                  // 손으로 따라간 예: k=2, 스트림 1 2 1 3 1 4 1 5
        const auto* one = ss.find(1); const auto* five = ss.find(5);
        assert(ss.valid() && ss.n == 8 && one && one->count == 4 && one->err == 0);             // 1 은 한 번도 쫓겨나지 않아 정확히 4
        assert(five && five->count == 4 && five->err == 3 && ss.find(2) == nullptr && ss.find(4) == nullptr);   // 5 는 쫓겨난 4(3)를 물려받아 count 4, 오차 3 → 진짜 빈도는 [1,4] 안
        assert(ss.minCount() == 4 && ss.minCount() <= ss.n / (long)ss.k); }
    std::mt19937 rng(21);
    for (int kind = 0; kind < 3; ++kind) for (size_t k : {1, 2, 5, 10, 50}) for (int rep = 0; rep < 6; ++rep) {
        const int n = 1500 + (int)(rng() % 12000); SpaceSaving ss(k); std::map<int, long> f; std::vector<long> seen;
        for (int i = 0; i < n; ++i) {
            const int x = kind == 0 ? (rng() % 1000 < 500 ? (int)(rng() % 3) : (int)(rng() % 200)) : kind == 1 ? (int)(rng() % 40) : i;
            ss.add(x); ++f[x];
            if (i % 211 == 0) assert(ss.valid());
        }
        assert(ss.valid() && (long)ss.n == n && ss.minCount() * (long)k <= ss.n);               // 합 == n 이므로 최솟값 <= n/k
        for (const auto& kv : f) {
            const auto* s = ss.find(kv.first);
            if (s) assert(s->count - s->err <= kv.second && kv.second <= s->count);               // 모니터링 항목: 진짜 빈도는 [count-err, count]
            else assert(kv.second <= ss.minCount());                                              // 아니면 최솟값 이하
            if (kv.second * (long)k > ss.n) assert(s != nullptr);                                 // n/k 를 넘는 빈도는 반드시 모니터링
        }
    }
    std::cout << "SpaceSaving: counters always summed to n; every monitored item satisfied count-err <= f <= count, unmonitored items had f <= min, items with f > n/k were always monitored (90 random streams, k=1..50)" << std::endl;
    return 0;
}
// Time Complexity: add O(log k) (힙 내리기·올리기), 조회 O(1)
// Space Complexity: O(k)
```

## CountSketch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// Count Sketch (Charikar 등): d x w 카운터 표. 행 j 마다 항목 x 를 열 h_j(x) 에 대응시키고 부호 s_j(x) = ±1 을 곱해 더한다: T[j][h_j(x)] += s_j(x) * c.
// 추정은 행마다 s_j(x) * T[j][h_j(x)] 를 구해 중앙값을 취한다. 부호가 무작위라 다른 항목의 기여가 평균 0 으로 상쇄되므로 추정은 불편(unbiased)이고, 오차는 ||f||_2 / sqrt(w) 에 비례한다.
// Count-Min 이 빈도 합(L1)에 비례하는 한쪽 오차인 데 비해 빈도가 한두 항목에 쏠린 스트림에서 훨씬 정확하다. 표가 선형이라 갱신에 음수를 쓸 수 있고(turnstile) 두 표를 더하면 두 스트림의 합과 같다.
// 해시는 소수 p = 2^31 - 1 위의 3차 다항식(4-독립)을 쓴다. 곱이 64 비트 안에 들어가 어느 컴파일러에서나 같은 값이 나온다.
// 검증: ① 한 항목만 있으면 정확 ② 큰 항목 5 개 + 꼬리 5000 개 스트림에서 거의 모든 항목이 오차 한계 3 sqrt(F2/w) 이내, 큰 항목은 상대오차 5% 이내, F2 추정(행별 제곱합의 중앙값)이 참값의 30% 이내
//       ③ 선형성: 표를 더한 것 == 이어 붙인 스트림으로 만든 표 ④ 삽입한 모든 갱신을 음수로 되돌리면 표가 0
struct PolyHash {
    static constexpr uint64_t P = 2147483647ULL; uint64_t a[4];
    PolyHash() : a{1, 0, 0, 0} {}
    explicit PolyHash(std::mt19937& g) { for (auto& x : a) x = g() % P; if (a[3] == 0) a[3] = 1; }
    uint64_t operator()(uint64_t x) const { x %= P; uint64_t r = a[3]; for (int i = 2; i >= 0; --i) r = (r * x + a[i]) % P; return r; }       // Horner: 3차 다항식 mod p
};
struct CountSketch {
    int d, w; std::vector<std::vector<long>> t; std::vector<PolyHash> col, sgn;
    CountSketch(int d_, int w_, unsigned seed) : d(d_), w(w_), t(d_, std::vector<long>(w_, 0)) { std::mt19937 g(seed); for (int j = 0; j < d; ++j) { col.emplace_back(g); sgn.emplace_back(g); } }
    int sign(int j, uint64_t x) const { return (sgn[j](x) & 1) ? 1 : -1; }
    void update(uint64_t x, long c) { for (int j = 0; j < d; ++j) t[j][col[j](x) % w] += sign(j, x) * c; }
    long estimate(uint64_t x) const { std::vector<long> v; for (int j = 0; j < d; ++j) v.push_back(sign(j, x) * t[j][col[j](x) % w]); std::nth_element(v.begin(), v.begin() + d / 2, v.end()); return v[d / 2]; }
    double f2() const { std::vector<double> v; for (int j = 0; j < d; ++j) { double s = 0; for (long c : t[j]) s += (double)c * c; v.push_back(s); } std::nth_element(v.begin(), v.begin() + d / 2, v.end()); return v[d / 2]; }
    void add(const CountSketch& o) { for (int j = 0; j < d; ++j) for (int i = 0; i < w; ++i) t[j][i] += o.t[j][i]; }
};

int main() {
    {   CountSketch cs(5, 64, 1); cs.update(42, 7); cs.update(42, 3); assert(cs.estimate(42) == 10);       // 항목이 하나뿐이면 충돌이 없어 정확
        cs.update(42, -10); assert(cs.estimate(42) == 0); }
    std::mt19937 rng(5); const int D = 7, W = 512;
    CountSketch cs(D, W, 77); std::map<uint64_t, long> f; std::vector<std::pair<uint64_t, long>> stream;
    for (int i = 0; i < 100000; ++i) { const bool heavy = rng() % 5 == 0; const uint64_t x = heavy ? 1 + rng() % 5 : 100 + rng() % 5000; const long c = 1 + (long)(rng() % 3); stream.push_back({x, c}); cs.update(x, c); f[x] += c; }   // 갱신의 20% 는 5 개의 큰 항목(각 빈도 약 8000), 80% 는 5000 개 꼬리 항목(각 약 32)
    double F2 = 0; for (const auto& kv : f) F2 += (double)kv.second * kv.second;
    const double bound = 3 * std::sqrt(F2 / W); int within = 0, total = 0; double heavyRel = 0; int heavyCount = 0;
    for (const auto& kv : f) {
        const double err = std::fabs((double)(cs.estimate(kv.first) - kv.second)); ++total; within += err <= bound;
        if (kv.second >= 4000) { heavyRel = std::max(heavyRel, err / (double)kv.second); ++heavyCount; }
    }
    assert(within >= total * 99 / 100 && heavyCount == 5 && heavyRel < 0.05);                          // 99% 이상이 3 sqrt(F2/w) 이내, 큰 항목 5 개의 상대오차 < 5% (꼬리 항목은 오차 한계가 자기 빈도보다 커서 추정 불가 — 그게 이 표의 한계)
    assert(std::fabs(cs.f2() - F2) < 0.3 * F2);                                                        // 행별 제곱합의 중앙값 ≈ F2 (AMS 추정)
    CountSketch a(D, W, 77), b(D, W, 77), whole(D, W, 77);                                              // 선형성: 같은 시드의 표를 더하면 이어 붙인 스트림의 표
    for (size_t i = 0; i < stream.size(); ++i) { (i % 3 ? a : b).update(stream[i].first, stream[i].second); whole.update(stream[i].first, stream[i].second); }
    a.add(b); assert(a.t == whole.t && a.t == cs.t);
    for (const auto& u : stream) cs.update(u.first, -u.second);                                         // turnstile: 모든 갱신을 되돌리면 표가 0
    for (const auto& row : cs.t) for (long c : row) assert(c == 0);
    std::cout << "CountSketch: " << within << "/" << total << " items within 3*sqrt(F2/w) (heavy items " << heavyRel * 100 << "% worst relative error), F2 estimated within 30%, tables add linearly and cancel exactly" << std::endl;
    return 0;
}
// Time Complexity: update·estimate O(d), 표 합치기 O(d·w)
// Space Complexity: O(d·w)
```

## ReservoirSampling()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// 저수지 샘플링(Reservoir Sampling): 길이를 모르는 스트림에서 크기 k 의 표본을 균등하게(모든 k-부분집합이 같은 확률로) 뽑는다. 메모리는 k 개뿐이다.
// 알고리즘 R(Vitter): 처음 k 개는 그대로 담고, i 번째(0 기준 i >= k) 항목은 [0, i] 에서 무작위 j 를 뽑아 j < k 이면 j 번 칸을 덮어쓴다 → 항목마다 정확히 k/n 의 확률로 남는다. 난수를 항목마다 하나씩 쓴다.
// 알고리즘 L(Li): 다음에 "저수지에 들어갈 항목" 까지 건너뛸 길이를 한 번에 뽑는다(기하분포): W *= exp(log(u)/k), skip = floor(log(u')/log(1-W)). 난수를 O(k (1 + log(n/k))) 번만 쓴다.
// 검증: ① n <= k 면 전부 그대로 ② n=12, k=3 에서 두 알고리즘 모두 항목별 포함 횟수가 k/n 의 기대값 근처이고, 220 개 모든 3-부분집합의 출현 횟수가 균등(카이제곱 검정)
//       ③ 저수지 크기는 항상 min(n, k) ④ 알고리즘 L 이 쓴 난수 수는 R 의 1% 이하(n = 10^6, k = 10)
struct Uniform { std::mt19937 g; long draws = 0; explicit Uniform(uint32_t s) : g(s) {}                          // draws: 엔진을 부른 횟수
    uint32_t next() { ++draws; return g(); }
    uint64_t below(uint64_t n) { return (next() * n) >> 32; }                                                      // 0 <= r < n (n < 2^32, 곱셈-시프트)
    double unit() { uint64_t hi = next() >> 5, lo = next() >> 6; return ((double)(hi * 67108864ULL + lo) + 0.5) / 9007199254740992.0; } };   // (0, 1) 의 53 비트 실수
std::vector<int> algorithmR(int n, int k, Uniform& u) {
    std::vector<int> res; for (int i = 0; i < n; ++i) { if (i < k) res.push_back(i); else { uint64_t j = u.below((uint64_t)i + 1); if (j < (uint64_t)k) res[j] = i; } }
    return res;
}
std::vector<int> algorithmL(int n, int k, Uniform& u) {
    std::vector<int> res; for (int i = 0; i < n && i < k; ++i) res.push_back(i);
    if (n <= k) return res;
    double W = std::exp(std::log(u.unit()) / k); long i = k - 1;
    for (;;) {
        i += 1 + (long)std::floor(std::log(u.unit()) / std::log1p(-W));                                                // 다음에 저수지로 들어갈 항목의 위치
        if (i >= n) break;
        res[u.below((uint64_t)k)] = (int)i; W *= std::exp(std::log(u.unit()) / k);
    }
    return res;
}

int main() {
    {   Uniform u(1); assert((algorithmR(3, 5, u) == std::vector<int>{0, 1, 2}) && (algorithmL(5, 5, u) == std::vector<int>{0, 1, 2, 3, 4})); }       // 항목이 k 개 이하면 전부 담는다
    const int n = 12, k = 3, trials = 120000; const double expectEach = (double)trials * k / n, sd = std::sqrt(trials * ((double)k / n) * (1 - (double)k / n));
    for (int alg = 0; alg < 2; ++alg) {
        Uniform u(100 + alg); std::vector<long> incl(n, 0); std::map<std::vector<int>, long> subsets;
        for (int t = 0; t < trials; ++t) {
            std::vector<int> s = alg == 0 ? algorithmR(n, k, u) : algorithmL(n, k, u); assert((int)s.size() == k);
            for (int x : s) ++incl[x]; std::sort(s.begin(), s.end()); assert(std::adjacent_find(s.begin(), s.end()) == s.end()); ++subsets[s];
        }
        for (int x = 0; x < n; ++x) assert(std::fabs((double)incl[x] - expectEach) < 6 * sd);                        // 항목마다 k/n 의 확률(6 시그마 이내)
        assert(subsets.size() == 220);                                                                              // C(12,3) = 220 개 부분집합이 모두 나왔고
        const double e = (double)trials / 220; double chi2 = 0; for (const auto& kv : subsets) chi2 += (kv.second - e) * (kv.second - e) / e;
        assert(chi2 < 219 + 6 * std::sqrt(2.0 * 219));                                                              // 카이제곱(자유도 219)이 평균 + 6 시그마 이내: 균등
    }
    Uniform ur(7), ul(8); const int big = 1000000, kk = 10;
    std::vector<int> sr = algorithmR(big, kk, ur), sl = algorithmL(big, kk, ul);
    assert((int)sr.size() == kk && (int)sl.size() == kk && ul.draws * 100 < ur.draws);                              // L 은 난수를 R 의 1% 미만만 쓴다
    std::cout << "ReservoirSampling: algorithms R and L gave uniform 3-of-12 samples (220 subsets, chi-square within 6 sigma, " << trials << " trials each); for n=10^6, k=10 algorithm L drew " << ul.draws << " random numbers vs " << ur.draws << " for R" << std::endl;
    return 0;
}
// Time Complexity: 알고리즘 R O(n), 알고리즘 L 기대 O(k (1 + log(n/k)))  (건너뛴 항목은 읽지 않아도 된다)
// Space Complexity: O(k)
```
# Part 4. 문자열 자료구조
## Rope()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 로프(문자열 관점의 요약, 정본은 String.md Part 4): 긴 문자열을 이진 트리로 나타내고 연결은 새 루트 하나, 분할·색인은 O(깊이).  정본은 AVL 식 join 으로 균형을 맞춘 *영속* 로프였다 — 여기서는 같은 인터페이스를 *암시적 트립*(implicit treap)으로 만든다.
//  키 대신 "위치(= 왼쪽 부분 트리 크기)" 로 가르고 무작위 우선순위(힙)로 균형을 잡는다 → 기대 깊이 O(log n).  지연 전파(lazy) 한 칸으로 *구간 뒤집기*가 O(log n) 에 된다 (std::reverse 는 O(길이)) — 문자열 편집기의 "선택 영역 뒤집기/잘라 붙이기".
//  ① std::string 과 20000 번의 무작위 편집(삽입·삭제·뒤집기·잘라 붙이기·부분 문자열·색인·이어 붙이기) 대조  ② 깊이 ≤ 4·log2(n) + 12  ③ 100 만 글자 문서에서 편집 3000 번 — 구간 뒤집기·이동은 최대 10^5 글자짜리를 O(log n) 에 하고 끝에 전체 대조  ④ 삭제된 노드는 free-list 로 재사용 (arena 크기 ≤ 최대 동시 노드 수 + 1).
struct Rope {
    struct N { char c; uint32_t pri; int l = -1, r = -1, sz = 1; bool rev = false; };
    std::vector<N> t; std::vector<int> freeList; std::mt19937 rng;
    explicit Rope(unsigned seed = 1) : rng(seed) {}
    int node(char c) { N n; n.c = c; n.pri = rng(); int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); t[u] = n; } else { t.push_back(n); u = (int)t.size() - 1; } return u; }
    int sz(int u) const { return u < 0 ? 0 : t[u].sz; }
    void upd(int u) { t[u].sz = 1 + sz(t[u].l) + sz(t[u].r); }
    void push(int u) { if (u >= 0 && t[u].rev) { std::swap(t[u].l, t[u].r); if (t[u].l >= 0) t[t[u].l].rev ^= true; if (t[u].r >= 0) t[t[u].r].rev ^= true; t[u].rev = false; } }
    void split(int u, int k, int& a, int& b) {                                                                  // 앞 k 글자 → a, 나머지 → b
        if (u < 0) { a = b = -1; return; } push(u);
        if (sz(t[u].l) < k) { int x, y; split(t[u].r, k - sz(t[u].l) - 1, x, y); t[u].r = x; upd(u); a = u; b = y; }
        else { int x, y; split(t[u].l, k, x, y); t[u].l = y; upd(u); a = x; b = u; } }
    int merge(int a, int b) {
        if (a < 0) return b; if (b < 0) return a;
        if (t[a].pri > t[b].pri) { push(a); int m = merge(t[a].r, b); t[a].r = m; upd(a); return a; }
        push(b); int m = merge(a, t[b].l); t[b].l = m; upd(b); return b; }
    int fromString(const std::string& s) { int root = -1; for (char c : s) root = merge(root, node(c)); return root; }
    int insert(int root, size_t pos, const std::string& s) { int a, b; split(root, (int)pos, a, b); return merge(merge(a, fromString(s)), b); }
    void release(int u) { std::vector<int> st; if (u >= 0) st.push_back(u); while (!st.empty()) { int x = st.back(); st.pop_back(); if (t[x].l >= 0) st.push_back(t[x].l); if (t[x].r >= 0) st.push_back(t[x].r); freeList.push_back(x); } }
    int erase(int root, size_t pos, size_t len) { int a, b, c, d; split(root, (int)pos, a, b); split(b, (int)len, c, d); release(c); return merge(a, d); }
    int reverse(int root, size_t pos, size_t len) { int a, b, c, d; split(root, (int)pos, a, b); split(b, (int)len, c, d); if (c >= 0) t[c].rev ^= true; return merge(merge(a, c), d); }
    int move(int root, size_t pos, size_t len, size_t to) {                                                     // [pos, pos+len) 를 잘라 (나머지 문자열에서의) 위치 to 에 붙인다
        int a, b, c, d; split(root, (int)pos, a, b); split(b, (int)len, c, d); int rest = merge(a, d); int x, y; split(rest, (int)to, x, y); return merge(merge(x, c), y); }
    char at(int root, size_t i) { int u = root; for (;;) { push(u); int ls = sz(t[u].l); if ((int)i < ls) u = t[u].l; else if ((int)i == ls) return t[u].c; else { i -= ls + 1; u = t[u].r; } } }
    std::string str(int root) { std::string out; std::vector<int> st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { push(u); st.push_back(u); u = t[u].l; } u = st.back(); st.pop_back(); out += t[u].c; u = t[u].r; } return out; }
    std::string substr(int& root, size_t pos, size_t len) { int a, b, c, d; split(root, (int)pos, a, b); split(b, (int)len, c, d); std::string s = str(c); root = merge(merge(a, c), d); return s; }
    int depth(int root) { int best = 0; std::vector<std::pair<int, int>> st; if (root >= 0) st.push_back({root, 1}); while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); push(p.first); if (t[p.first].l >= 0) st.push_back({t[p.first].l, p.second + 1}); if (t[p.first].r >= 0) st.push_back({t[p.first].r, p.second + 1}); } return best; }
};

int main() {
    Rope rp(7); int doc = rp.fromString("Hello, world!"); assert(rp.sz(doc) == 13 && rp.at(doc, 7) == 'w'); doc = rp.insert(doc, 7, "beautiful "); assert(rp.str(doc) == "Hello, beautiful world!");
    doc = rp.reverse(doc, 0, 5); assert(rp.str(doc) == "olleH, beautiful world!"); doc = rp.erase(doc, 5, 11); assert(rp.str(doc) == "olleH world!");
    std::mt19937 rng(83); std::string ref; int root = -1; Rope r2(9); size_t maxDepth = 0;                          // ①
    auto randStr = [&](size_t n) { std::string s(n, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); return s; };
    for (int op = 0; op < 20000; ++op) {
        int k = (int)(rng() % 8); size_t n = ref.size();
        if (k <= 1 || n < 4) { size_t pos = rng() % (n + 1); std::string x = randStr(rng() % 40); root = r2.insert(root, pos, x); ref.insert(pos, x); }
        else if (k == 2) { size_t pos = rng() % n, len = rng() % std::min<size_t>(40, n - pos + 1); root = r2.erase(root, pos, len); ref.erase(pos, len); }
        else if (k == 3) { size_t pos = rng() % n, len = rng() % (n - pos + 1); root = r2.reverse(root, pos, len); std::reverse(ref.begin() + pos, ref.begin() + pos + len); }
        else if (k == 4) { size_t pos = rng() % n, len = rng() % (n - pos + 1); size_t to = rng() % (n - len + 1); root = r2.move(root, pos, len, to); std::string cut = ref.substr(pos, len); ref.erase(pos, len); ref.insert(to, cut); }
        else if (k == 5) { size_t pos = rng() % n, len = rng() % (n - pos + 1); assert(r2.substr(root, pos, len) == ref.substr(pos, len)); }
        else if (k == 6) { std::string x = randStr(1 + rng() % 20); int right = r2.fromString(x); if (rng() & 1) { root = r2.merge(root, right); ref += x; } else { root = r2.merge(right, root); ref = x + ref; } }          // 양쪽 이어 붙이기
        else { size_t i = rng() % n; assert(r2.at(root, i) == ref[i]); }
        assert(r2.sz(root) == (int)ref.size());
        if (op % 25 == 0) { assert(r2.str(root) == ref); size_t d = (size_t)r2.depth(root); maxDepth = std::max(maxDepth, d); assert(d <= 4 * std::log2((double)std::max<size_t>(ref.size(), 2)) + 12); }          // ② 깊이
    }
    assert(r2.str(root) == ref);
    { const size_t N = 1000000; Rope big(11); std::string text = randStr(N); int b = big.fromString(text); size_t peak = big.t.size();                       // ③ 100 만 글자
      for (int op = 0; op < 3000; ++op) {
          size_t n = text.size(); int k = (int)(rng() % 4);
          if (k == 0) { size_t pos = rng() % (n + 1); std::string x = randStr(1 + rng() % 100); b = big.insert(b, pos, x); text.insert(pos, x); }
          else if (k == 1) { size_t pos = rng() % n, len = rng() % std::min<size_t>(200, n - pos + 1); b = big.erase(b, pos, len); text.erase(pos, len); }
          else if (k == 2) { size_t pos = rng() % n, len = rng() % std::min<size_t>(100000, n - pos + 1); b = big.reverse(b, pos, len); std::reverse(text.begin() + pos, text.begin() + pos + len); }
          else { size_t pos = rng() % n, len = rng() % std::min<size_t>(100000, n - pos + 1); size_t to = rng() % (n - len + 1); b = big.move(b, pos, len, to); std::string cut = text.substr(pos, len); text.erase(pos, len); text.insert(to, cut); }
          assert(big.sz(b) == (int)text.size()); for (int q = 0; q < 5; ++q) { size_t i = rng() % text.size(); assert(big.at(b, i) == text[i]); }
          peak = std::max(peak, big.t.size() - big.freeList.size()); }
      assert(big.str(b) == text && (int)big.depth(b) <= 4 * std::log2((double)text.size()) + 12 && big.t.size() <= peak + 400000);                          // ④ 노드 재사용: arena 가 동시 노드 수에서 크게 벗어나지 않는다
      std::cout << "Rope: 20000 random edits (insert/erase/reverse/cut-paste/substr/index/concat) matched std::string with depth <= " << maxDepth << "; a 10^6-character document survived 3000 edits including reversals/moves of up to 10^5 characters (depth " << big.depth(b) << ")" << std::endl; }
    return 0;
}
// Time Complexity: 색인·분할·삽입·삭제·구간 뒤집기·이동 기대 O(log N)
// Space Complexity: O(N) (글자당 노드 하나)
```
## PieceTable()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 피스 테이블(문자열 관점의 요약, 정본은 String.md Part 4): 원본 파일은 수정하지 않고 "추가 전용" 버퍼에 새 글자를 덧붙이며, 문서 = (버퍼, 시작, 길이) 조각들의 목록.
//  삽입은 조각을 둘로 쪼개고 새 조각 하나를 끼우는 일이고, 조각 목록의 복사본이 곧 실행 취소(undo) 기록이다 (VS Code 의 텍스트 버퍼가 이 계열).  연속해서 타자를 치면 *마지막 추가 조각을 늘려* 조각 수가 늘지 않는다(coalescing).
//  ① std::string 과 8000 번의 무작위 편집(삽입·삭제·undo·redo)을 대조하고 undo/redo 가 *직전 문서 문자열*을 정확히 복원  ② 원본 버퍼는 한 번도 바뀌지 않고 추가 버퍼는 접두사가 유지되는 append-only
//  ③ 조각 수 ≤ 2·삽입 + 삭제 + 1  ④ 100 만 글자 원본에서 10^5 글자를 한 글자씩 타자 → 조각은 3 개(앞·새 글·뒤)에 머문다  ⑤ 끝까지 undo 하면 원본이 그대로.  ⑥ undo/redo 는 조각 목록을 복사하지 않고 버퍼를 맞바꾼다 (조각 목록 버퍼의 주소로 확인).
struct PieceTable {
    struct Piece { bool added; size_t start, len; };
    std::string original, added; std::vector<Piece> pieces; std::vector<std::vector<Piece>> undoStack, redoStack; long inserts = 0, erases = 0;
    explicit PieceTable(std::string text) : original(std::move(text)) { if (!original.empty()) pieces.push_back({false, 0, original.size()}); }
    size_t size() const { size_t n = 0; for (auto& p : pieces) n += p.len; return n; }
    std::string text() const { std::string out; for (auto& p : pieces) out.append(p.added ? added : original, p.start, p.len); return out; }
    char at(size_t pos) const { for (auto& p : pieces) { if (pos < p.len) return (p.added ? added : original)[p.start + pos]; pos -= p.len; } return 0; }
    size_t splitAt(size_t pos) {                                                                                  // pos 가 조각 경계가 되도록 쪼개고, 그 경계 *앞*의 조각 수를 돌려준다
        size_t idx = 0;
        for (; idx < pieces.size(); ++idx) { if (pos == 0) return idx; if (pos < pieces[idx].len) { Piece right = {pieces[idx].added, pieces[idx].start + pos, pieces[idx].len - pos}; pieces[idx].len = pos; pieces.insert(pieces.begin() + idx + 1, right); return idx + 1; } pos -= pieces[idx].len; }
        return idx; }
    void insert(size_t pos, const std::string& s) {
        if (s.empty()) return; undoStack.push_back(pieces); redoStack.clear(); ++inserts;
        size_t at = splitAt(pos); bool extend = at > 0 && pieces[at - 1].added && pieces[at - 1].start + pieces[at - 1].len == added.size();                // 직전 조각이 추가 버퍼의 맨 끝이면 그대로 늘린다
        size_t start = added.size(); added += s; if (extend) pieces[at - 1].len += s.size(); else pieces.insert(pieces.begin() + at, Piece{true, start, s.size()}); }
    void erase(size_t pos, size_t len) {
        len = std::min(len, size() - pos); if (len == 0) return; undoStack.push_back(pieces); redoStack.clear(); ++erases;
        size_t a = splitAt(pos), b = splitAt(pos + len); pieces.erase(pieces.begin() + a, pieces.begin() + b); }
    bool undo() { if (undoStack.empty()) return false; std::swap(pieces, undoStack.back()); redoStack.push_back(std::move(undoStack.back())); undoStack.pop_back(); return true; }     // 스냅샷을 복사 없이 교체(swap/move)
    bool redo() { if (redoStack.empty()) return false; std::swap(pieces, redoStack.back()); undoStack.push_back(std::move(redoStack.back())); redoStack.pop_back(); return true; }
};

int main() {
    std::mt19937 rng(91); std::string base; for (int i = 0; i < 500; ++i) base += (char)('a' + rng() % 26);
    PieceTable pt(base); std::vector<std::string> past; std::string cur = base; std::vector<std::string> future; std::string addedSnapshot; long edits = 0;
    auto randStr = [&](size_t n) { std::string s(n, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); return s; };
    for (int op = 0; op < 8000; ++op) {
        int k = (int)(rng() % 10); size_t n = cur.size();
        if (k <= 3) { size_t pos = rng() % (n + 1); std::string x = randStr(1 + rng() % 30); pt.insert(pos, x); past.push_back(cur); future.clear(); cur.insert(pos, x); ++edits; }
        else if (k <= 5 && n > 0) { size_t pos = rng() % n, len = 1 + rng() % std::min<size_t>(40, n - pos); pt.erase(pos, len); past.push_back(cur); future.clear(); cur.erase(pos, len); ++edits; }
        else if (k <= 7) { bool did = pt.undo(); assert(did == !past.empty()); if (did) { future.push_back(cur); cur = past.back(); past.pop_back(); } }
        else if (k == 8) { bool did = pt.redo(); assert(did == !future.empty()); if (did) { past.push_back(cur); cur = future.back(); future.pop_back(); } }
        else if (n > 0) { size_t i = rng() % n; assert(pt.at(i) == cur[i]); }
        assert(pt.size() == cur.size()); if (op % 50 == 0) assert(pt.text() == cur);
        if (op == 4000) addedSnapshot = pt.added; else if (op > 4000) assert(pt.added.compare(0, addedSnapshot.size(), addedSnapshot) == 0);          // ② 추가 버퍼는 append-only
        assert(pt.original == base);                                                                              // 원본은 바뀌지 않는다
        assert((long)pt.pieces.size() <= 2 * pt.inserts + pt.erases + 1);                                         // ③
    }
    assert(pt.text() == cur);
    while (pt.undo()) {} assert(pt.text() == base && pt.pieces.size() == 1);                                      // ⑤ 끝까지 undo
    {   PieceTable t("abcdefgh"); t.insert(3, "XY"); t.erase(1, 2); const PieceTable::Piece* snap = t.undoStack.back().data(); const PieceTable::Piece* now = t.pieces.data();       // ⑥ 스냅샷 교체는 O(1): 같은 버퍼가 오간다
        bool u = t.undo(); assert(u && t.pieces.data() == snap && t.redoStack.back().data() == now); bool r = t.redo(); assert(r && t.pieces.data() == now && t.undoStack.back().data() == snap); }
    { std::string big(1000000, 'x'); for (size_t i = 0; i < big.size(); ++i) big[i] = (char)('a' + i % 26); PieceTable doc(big); std::string typed = randStr(100000); size_t pos = 500000;
      for (size_t i = 0; i < typed.size(); ++i) doc.insert(pos + i, std::string(1, typed[i]));                    // ④ 한 글자씩 타자
      assert(doc.pieces.size() == 3 && doc.size() == 1100000 && doc.text() == big.substr(0, pos) + typed + big.substr(pos));
      std::cout << "PieceTable: 8000 random insert/erase/undo/redo steps matched std::string (" << edits << " edits, undo restored the original exactly), the original buffer never changed, and 10^5 single-character keystrokes in a 10^6-character file stayed in " << doc.pieces.size() << " pieces" << std::endl; }
    return 0;
}
// Time Complexity: 삽입·삭제 O(조각 수), 텍스트 조립 O(길이), undo·redo O(1) (스냅샷 버퍼 교체, 복사 없음; 삽입·삭제가 조각 목록을 스냅샷으로 복사하므로 O(조각 수))
// Space Complexity: 원본 + 추가 버퍼 + 조각 목록 (+ undo 스냅샷마다 조각 목록 한 벌)
```
## GapBuffer()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 갭 버퍼(문자열 관점의 요약, 정본은 String.md Part 4): 글자 배열 가운데에 "빈 틈(gap)"을 두고 커서가 있는 곳에 틈을 놓는다. 커서 위치에서의 삽입·삭제는 O(1),
//  커서를 옮기면 틈을 따라 옮기는 데 이동 거리만큼의 복사가 든다. 편집은 지역적이라는 관찰에 기대는 Emacs 의 버퍼 구조.  틈이 바닥나면 용량을 두 배로 늘린다(분할상환 O(1)).
//  ① std::string(+ 커서 정수) 과 6 만 번의 무작위 연산(삽입·앞/뒤 삭제·커서 이동·색인) 대조, 매 단계 불변식(틈 경계·크기·커서)과 100 단계마다 내용 전체(= 앞 + 뒤) 비교,
//  그리고 용량(16)보다 훨씬 긴 문자열(100 자, 5000 자)을 한 번에 넣어 reserve 의 "필요량" 가지(need > 2·용량)를 확인  ② 복사량 계산: moveTo 가 옮긴 글자 수 = 커서 이동 거리의 합 (정확히)
//  ③ 성장 비용: 확장 때 복사한 글자 수 총합 ≤ 2·최대 크기 + 용량  ④ 지역성: 100 만 글자를 이어서 타자 → 이동 0, ±5 칸 걷는 커서 → 이동 ≤ 5·연산 수, 문서 곳곳으로 튀는 커서는 이동량이 훨씬 크다 (연산 수가 10 배 적어도 10 배 이상).
struct GapBuffer {
    std::vector<char> buf; size_t gs, ge; long moved = 0, grown = 0;                                              // 틈은 [gs, ge)
    explicit GapBuffer(size_t cap = 16) : buf(cap), gs(0), ge(cap) {}
    size_t size() const { return buf.size() - (ge - gs); }
    size_t cursor() const { return gs; }
    void moveTo(size_t pos) {
        if (pos < gs) { size_t d = gs - pos; std::copy_backward(buf.begin() + pos, buf.begin() + gs, buf.begin() + ge); gs = pos; ge -= d; moved += (long)d; }
        else if (pos > gs) { size_t d = pos - gs; std::copy(buf.begin() + ge, buf.begin() + ge + d, buf.begin() + gs); gs += d; ge += d; moved += (long)d; } }
    void reserve(size_t extra) {
        if (ge - gs >= extra) return; size_t need = size() + extra, cap = std::max(buf.size() * 2, need); std::vector<char> nb(cap);
        std::copy(buf.begin(), buf.begin() + gs, nb.begin()); size_t tail = buf.size() - ge; std::copy(buf.begin() + ge, buf.end(), nb.begin() + (cap - tail)); grown += (long)size(); ge = cap - tail; buf.swap(nb); }
    void insert(char c) { reserve(1); buf[gs++] = c; }
    void insert(const std::string& s) { reserve(s.size()); for (char c : s) buf[gs++] = c; }
    bool eraseBefore() { if (gs == 0) return false; --gs; return true; }                                          // Backspace
    bool eraseAfter() { if (ge == buf.size()) return false; ++ge; return true; }                                  // Delete
    char at(size_t i) const { return i < gs ? buf[i] : buf[i + (ge - gs)]; }
    std::string text() const { return std::string(buf.begin(), buf.begin() + gs) + std::string(buf.begin() + ge, buf.end()); }
    bool valid() const { return gs <= ge && ge <= buf.size(); }
};

int main() {
    std::mt19937 rng(97); GapBuffer gb; std::string ref; size_t cur = 0; long distSum = 0; size_t maxSize = 0;
    for (int op = 0; op < 60000; ++op) {
        int k = (int)(rng() % 10);
        if (k <= 3) { char c = (char)('a' + rng() % 26); gb.insert(c); ref.insert(ref.begin() + cur, c); ++cur; }
        else if (k == 4) { std::string s(1 + rng() % 12, 'q'); for (char& c : s) c = (char)('a' + rng() % 26); gb.insert(s); ref.insert(cur, s); cur += s.size(); }
        else if (k == 5) { bool ok = gb.eraseBefore(); assert(ok == (cur > 0)); if (ok) { ref.erase(cur - 1, 1); --cur; } }
        else if (k == 6) { bool ok = gb.eraseAfter(); assert(ok == (cur < ref.size())); if (ok) ref.erase(cur, 1); }
        else if (k == 7) { size_t pos = rng() % (ref.size() + 1); distSum += (long)(pos > cur ? pos - cur : cur - pos); gb.moveTo(pos); cur = pos; }
        else if (k == 8 && !ref.empty()) { size_t i = rng() % ref.size(); assert(gb.at(i) == ref[i]); }
        else { long step = (long)(rng() % 11) - 5; long pos = std::max<long>(0, std::min<long>((long)ref.size(), (long)cur + step)); distSum += std::labs(pos - (long)cur); gb.moveTo((size_t)pos); cur = (size_t)pos; }
        assert(gb.valid() && gb.size() == ref.size() && gb.cursor() == cur); maxSize = std::max(maxSize, ref.size()); if (op % 100 == 0) assert(gb.text() == ref); }
    assert(gb.text() == ref && gb.moved == distSum && gb.grown <= 2 * (long)maxSize + (long)gb.buf.size());       // ② ③
    {   GapBuffer lg; std::string r2; lg.insert(std::string(100, 'x')); r2 = std::string(100, 'x'); assert(lg.valid() && lg.size() == 100 && lg.text() == r2);               // 용량 16 에 100 자를 한 번에: 두 배(32)로는 모자라 need 가지
        lg.moveTo(40); std::string mid(5000, 'm'); lg.insert(mid); r2.insert(40, mid); assert(lg.valid() && lg.size() == 5100 && lg.cursor() == 5040 && lg.text() == r2);          // 용량의 두 배보다 훨씬 긴 삽입이 틈 가운데에서도 정확
        lg.moveTo(0); lg.insert(std::string(300, 'h')); r2.insert(0, std::string(300, 'h')); assert(lg.valid() && lg.text() == r2); for (size_t i = 0; i < r2.size(); i += 97) assert(lg.at(i) == r2[i]); }
    { GapBuffer typing; std::string out; for (int i = 0; i < 1000000; ++i) typing.insert((char)('a' + i % 26)); assert(typing.moved == 0 && typing.size() == 1000000 && typing.grown <= 2 * 1000000);                           // ④ 이어서 타자
      GapBuffer local, jumpy; for (int i = 0; i < 100000; ++i) { local.insert('x'); jumpy.insert('x'); } local.moveTo(50000); jumpy.moveTo(50000); long l0 = local.moved, j0 = jumpy.moved;
      for (int i = 0; i < 20000; ++i) { long p = (long)local.cursor() + (long)(rng() % 11) - 5; if (rng() % 2) p = (long)local.cursor(); p = std::min<long>((long)local.size(), std::max<long>(0, p)); local.moveTo((size_t)p); local.insert('y'); }
      for (int i = 0; i < 2000; ++i) { jumpy.moveTo(rng() % (jumpy.size() + 1)); jumpy.insert('y'); }
      long localMoved = local.moved - l0, jumpMoved = jumpy.moved - j0; assert(localMoved <= 5 * 20000 && jumpMoved > 100 * (localMoved + 1) / 10);                                                           // 튀는 커서는 (연산 수가 10 배 적어도) 이동량이 훨씬 크다
      std::cout << "GapBuffer: 60000 random edits matched std::string with the copy count equal to the total cursor travel (" << gb.moved << "), inserts of 100 and 5000 characters far beyond the capacity were exact, 10^6 keystrokes moved nothing, and a local cursor moved " << localMoved << " characters in 20000 edits versus " << jumpMoved << " for 2000 random jumps" << std::endl; }
    return 0;
}
// Time Complexity: 커서 위치 삽입·삭제 분할상환 O(1), 커서 이동 O(거리)
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 접미사 오토마톤(SAM, 문자열 관점의 요약, 정본은 String.md Part 9): 문자열의 모든 부분 문자열을 받아들이는 최소 DFA. 상태 수 ≤ 2n−1, 전이 ≤ 3n−4, 온라인 O(n) 구성.
//  서로 다른 부분 문자열의 수 = Σ (len[v] − len[link[v]]).  상태 v 의 endpos 크기 cnt[v] 는 len 이 큰 순서로 link 를 따라 합산하면 되고, 패턴의 출현 횟수 = 패턴이 닿는 상태의 cnt.
//  ① 전수: 이진 문자열 길이 ≤ 12 전부 — 상태 수 ≤ 2n − 1, 전이 수 ≤ 3n − 4 (n ≥ 3), 서로 다른 부분 문자열 수가 집합 오라클과 같고, (텍스트 길이 ≤ 9 에 대해서만) 길이 ≤ 6 의 모든 이진 패턴에 대해 contains / 출현 횟수가 순진한 탐색과 같다
//  ② 최장 공통 부분 문자열: 무작위 문자열 쌍에서 SAM 으로 b 를 훑은 길이가 동적 계획법(O(nm))과 같다  ③ 20 만 글자: 상태 수 ≤ 2n − 1, 실제 부분 문자열 300 개는 받아들이고 무작위 길이 25 문자열은 순진한 탐색과 같은 판정.
struct SAM {
    struct State { int len, link; int next[26]; };
    std::vector<State> st; std::vector<char> isClone; std::vector<long long> cnt; int last;
    SAM() { st.push_back(newState(0, -1)); isClone.push_back(0); last = 0; }
    static State newState(int len, int link) { State s; s.len = len; s.link = link; for (int& x : s.next) x = -1; return s; }
    void extend(char ch) {
        int c = ch - 'a', cur = (int)st.size(); st.push_back(newState(st[last].len + 1, 0)); isClone.push_back(0); int p = last;
        while (p != -1 && st[p].next[c] < 0) { st[p].next[c] = cur; p = st[p].link; }
        if (p != -1) { int q = st[p].next[c];
            if (st[p].len + 1 == st[q].len) st[cur].link = q;
            else { int clone = (int)st.size(); State cp = st[q]; cp.len = st[p].len + 1; st.push_back(cp); isClone.push_back(1);
                while (p != -1 && st[p].next[c] == q) { st[p].next[c] = clone; p = st[p].link; }
                st[q].link = st[cur].link = clone; } }
        last = cur; }
    void build(const std::string& s) { for (char c : s) extend(c); }
    void countEndpos() { cnt.assign(st.size(), 0); std::vector<int> order(st.size()); for (size_t i = 0; i < st.size(); ++i) { order[i] = (int)i; if (!isClone[i] && i != 0) cnt[i] = 1; }
        std::sort(order.begin(), order.end(), [&](int a, int b) { return st[a].len > st[b].len; }); for (int v : order) if (st[v].link >= 0) cnt[st[v].link] += cnt[v]; }
    int walk(const std::string& p) const { int v = 0; for (char ch : p) { v = st[v].next[ch - 'a']; if (v < 0) return -1; } return v; }
    bool contains(const std::string& p) const { return walk(p) >= 0; }
    long long occurrences(const std::string& p) const { int v = walk(p); return v < 0 ? 0 : (v == 0 ? -1 : cnt[v]); }
    long long distinctSubstrings() const { long long s = 0; for (size_t v = 1; v < st.size(); ++v) s += st[v].len - st[st[v].link].len; return s; }
    long long transitions() const { long long t = 0; for (auto& s : st) for (int x : s.next) t += x >= 0; return t; }
    int longestCommon(const std::string& b) const { int v = 0, l = 0, best = 0; for (char ch : b) { int c = ch - 'a'; while (v != 0 && st[v].next[c] < 0) { v = st[v].link; l = st[v].len; } if (st[v].next[c] >= 0) { v = st[v].next[c]; ++l; } best = std::max(best, l); } return best; }
};
int naiveCount(const std::string& t, const std::string& p) { int c = 0; for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) ++c; return c; }
int lcsDP(const std::string& a, const std::string& b) { int best = 0; std::vector<std::vector<int>> d(a.size() + 1, std::vector<int>(b.size() + 1, 0)); for (size_t i = 1; i <= a.size(); ++i) for (size_t j = 1; j <= b.size(); ++j) if (a[i - 1] == b[j - 1]) { d[i][j] = d[i - 1][j - 1] + 1; best = std::max(best, d[i][j]); } return best; }

int main() {
    { SAM s; s.build("abcbc"); assert(s.distinctSubstrings() == 12 && s.contains("bcb") && !s.contains("cc")); }                                   // abcbc: a b c ab bc cb abc bcb cbc abcb bcbc abcbc = 12
    std::vector<std::string> patterns; for (int len = 1; len <= 6; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; patterns.push_back(s); }
    for (int len = 1; len <= 12; ++len) for (int m = 0; m < (1 << len); ++m) { std::string t; for (int b = len - 1; b >= 0; --b) t += (m >> b & 1) ? 'b' : 'a'; SAM s; s.build(t); s.countEndpos(); int n = len;
        assert((int)s.st.size() <= std::max(2, 2 * n - 1) && (n < 3 || s.transitions() <= 3 * n - 4));
        std::set<std::string> sub; for (int i = 0; i < n; ++i) for (int l = 1; i + l <= n; ++l) sub.insert(t.substr(i, l)); assert(s.distinctSubstrings() == (long long)sub.size());
        if (len <= 9) for (auto& p : patterns) { int c = naiveCount(t, p); assert(s.contains(p) == (c > 0) && s.occurrences(p) == c); } }             // ①
    std::mt19937 rng(21);
    for (int it = 0; it < 300; ++it) { int n = 1 + (int)(rng() % 40), m = 1 + (int)(rng() % 40), sg = 2 + (int)(rng() % 3); std::string a(n, 'a'), b(m, 'a'); for (char& c : a) c = (char)('a' + rng() % sg); for (char& c : b) c = (char)('a' + rng() % sg); SAM s; s.build(a); assert(s.longestCommon(b) == lcsDP(a, b)); }   // ②
    { const int n = 200000; std::string t(n, 'a'); for (char& c : t) c = (char)('a' + rng() % 4); SAM s; s.build(t); s.countEndpos(); assert((int)s.st.size() <= 2 * n - 1 && s.transitions() <= 3LL * n - 4);
      for (int q = 0; q < 300; ++q) { int pl = 1 + (int)(rng() % 30); std::string p = t.substr(rng() % (n - pl), pl); assert(s.contains(p) && s.occurrences(p) >= 1 && s.occurrences(p) == naiveCount(t, p)); }
      for (int q = 0; q < 100; ++q) { std::string p(25, 'a'); for (char& c : p) c = (char)('a' + rng() % 4); assert(s.contains(p) == (t.find(p) != std::string::npos)); }
      std::cout << "SuffixAutomaton: states <= 2n-1 and transitions <= 3n-4 held for every binary string up to length 12, distinct-substring counts matched naive enumeration for all of them, contains/occurrence counts matched naive search for every binary text up to length 9 and every binary pattern up to length 6, the longest common substring matched dynamic programming, and a 2*10^5-character string produced " << s.st.size() << " states" << std::endl; }
    return 0;
}
// Time Complexity: 구성 O(n·σ) (복제 시 전이 배열 복사), 출현 횟수 집계 countEndpos 는 std::sort 때문에 O(n log n) (계수 정렬이면 O(n)), 부분 문자열 판정 O(m)
// Space Complexity: O(n·σ)
```
## PatriciaTrie()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// 패트리샤 트라이(트리 관점의 요약, 정본은 Tree.md Part 10): 자식이 하나뿐인 사슬을 한 간선으로 압축한 트라이. 간선에는 문자열 조각이 붙고 노드 수는 키 수의 2배 미만이다.
//  삽입은 간선 라벨과 공통 접두사 길이를 비교해, 일부만 겹치면 간선을 둘로 쪼갠다.  *삭제*는 반대로 단말에서 자식이 하나만 남은 부모를 자식과 합친다(두 간선 라벨을 이어 붙임).  IP 라우팅의 최장 접두사 일치(LPM)와 자동 완성이 이 구조다.
//  ① 전수: 알파벳 {a, b}, 길이 ≤ 3 인 12 개 문자열(빈 문자열 포함)의 *모든 부분 집합*(4096) 에서 삽입 순서를 바꿔 만들고 — 불변식, 노드 수 = 1 + |{접두사 p ≠ ε : p 가 키이거나 다음 문자가 둘 이상 갈라짐}|, contains / 사전순 목록 / startsWith / 최장 접두사 일치가 std::set 오라클과 같다
//  ② 무작위 삽입·삭제 12 만 연산(알파벳 3, 길이 ≤ 8)을 std::set 과 대조하고 매 연산 뒤 합치기가 일어나 불변식이 유지됨  ③ 길이 10^5 의 단일 키도 반복 구현으로 처리.
//  불변식: 루트 외 모든 노드는 라벨이 비어 있지 않고 라벨의 첫 글자가 자식 슬롯과 같으며, 키가 아니면서 자식이 하나 이하인 노드는 없다.
struct Patricia {
    struct Node { std::string label; std::array<int, 26> kid; bool end = false; Node() { kid.fill(-1); } };
    std::vector<Node> n; std::vector<int> freeList; size_t words = 0;
    Patricia() { n.push_back(Node()); }
    int make(const std::string& label, bool end) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); n[u] = Node(); } else { n.push_back(Node()); u = (int)n.size() - 1; } n[u].label = label; n[u].end = end; return u; }
    int children(int u) const { int c = 0; for (int x : n[u].kid) c += x >= 0; return c; }
    bool insert(const std::string& w) {
        int u = 0; size_t i = 0;
        for (;;) {
            if (i == w.size()) { if (n[u].end) return false; n[u].end = true; ++words; return true; }
            int c = w[i] - 'a', v = n[u].kid[c];
            if (v < 0) { int leaf = make(w.substr(i), true); n[u].kid[c] = leaf; ++words; return true; }
            size_t l = 0; const std::string label = n[v].label; while (l < label.size() && i + l < w.size() && label[l] == w[i + l]) ++l;
            if (l == label.size()) { u = v; i += l; continue; }
            int mid = make(label.substr(0, l), false); n[v].label = label.substr(l); n[mid].kid[n[v].label[0] - 'a'] = v; n[u].kid[c] = mid; u = mid; i += l; } }   // 라벨 중간에서 갈라짐: 중간 노드를 끼운다
    int find(const std::string& w, std::vector<std::pair<int, int>>* path = nullptr) const {                          // w 가 정확히 닿는 노드(없으면 −1); path = (부모, 노드) 열
        int u = 0; size_t i = 0; while (i < w.size()) { int v = n[u].kid[w[i] - 'a']; if (v < 0) return -1; const std::string& lb = n[v].label; if (w.compare(i, lb.size(), lb) != 0 || i + lb.size() > w.size()) return -1; if (path) path->push_back({u, v}); u = v; i += lb.size(); } return u; }
    bool contains(const std::string& w) const { int u = find(w); return u >= 0 && n[u].end; }
    bool erase(const std::string& w) {
        std::vector<std::pair<int, int>> path; int v = find(w, &path); if (v < 0 || !n[v].end) return false; n[v].end = false; --words; if (v == 0) return true;
        int parent = path.back().first;
        if (children(v) == 0) { n[parent].kid[n[v].label[0] - 'a'] = -1; freeList.push_back(v); v = parent; }                                  // 잎이 사라지면 부모를 다시 본다
        if (v != 0 && !n[v].end && children(v) == 1) { int only = -1; for (int x : n[v].kid) if (x >= 0) only = x; n[v].label += n[only].label; n[v].kid = n[only].kid; n[v].end = n[only].end; freeList.push_back(only); }   // 합치기
        return true; }
    void collect(int u, std::string cur, std::vector<std::string>& out) const { cur += n[u].label; if (n[u].end) out.push_back(cur); for (int x : n[u].kid) if (x >= 0) collect(x, cur, out); }
    std::vector<std::string> keys() const { std::vector<std::string> out; if (n[0].end) out.push_back(""); for (int x : n[0].kid) if (x >= 0) collect(x, "", out); return out; }
    std::vector<std::string> startsWith(const std::string& p) const {                                              // p 로 시작하는 키 (사전순)
        int u = 0; size_t i = 0; std::string cur; std::vector<std::string> out;
        while (i < p.size()) { int v = n[u].kid[p[i] - 'a']; if (v < 0) return out; const std::string& lb = n[v].label; size_t m = std::min(lb.size(), p.size() - i); if (lb.compare(0, m, p, i, m) != 0) return out; cur += lb; i += m; u = v; }
        if (u == 0) return keys(); if (n[u].end) out.push_back(cur); for (int x : n[u].kid) if (x >= 0) collect(x, cur, out); return out; }
    int longestPrefixOf(const std::string& q) const {                                                              // q 의 접두사인 키 중 가장 긴 것의 길이 (없으면 −1)
        int best = n[0].end ? 0 : -1; int u = 0; size_t i = 0; while (i < q.size()) { int v = n[u].kid[q[i] - 'a']; if (v < 0) break; const std::string& lb = n[v].label; if (q.compare(i, lb.size(), lb) != 0 || i + lb.size() > q.size()) break; i += lb.size(); u = v; if (n[u].end) best = (int)i; } return best; }
    bool valid() const { size_t live = 0; return check(0, true, live) && live + freeList.size() == n.size() && words == keys().size(); }
    bool check(int u, bool root, size_t& live) const { ++live; if (!root) { if (n[u].label.empty()) return false; if (!n[u].end && children(u) <= 1) return false; } for (int c = 0; c < 26; ++c) { int v = n[u].kid[c]; if (v >= 0) { if (n[v].label.empty() || n[v].label[0] - 'a' != c || !check(v, false, live)) return false; } } return true; }
    size_t nodeCount() const { return n.size() - freeList.size(); }
};
size_t expectedNodes(const std::set<std::string>& keys) {                                                       // 오라클: 루트 + (접두사 p ≠ ε 중 키이거나 다음 문자가 둘 이상인 것)
    std::map<std::string, std::set<char>> next; for (auto& k : keys) for (size_t l = 0; l < k.size(); ++l) next[k.substr(0, l)].insert(k[l]); size_t cnt = 1;
    std::set<std::string> prefixes; for (auto& k : keys) for (size_t l = 1; l <= k.size(); ++l) prefixes.insert(k.substr(0, l)); for (auto& p : prefixes) if (keys.count(p) || next[p].size() >= 2) ++cnt; return cnt; }
int refLongestPrefix(const std::set<std::string>& keys, const std::string& q) { int best = -1; for (auto& k : keys) if (q.compare(0, k.size(), k) == 0 && q.size() >= k.size()) best = std::max(best, (int)k.size()); return best; }

int main() {
    std::vector<std::string> universe = {"", "a", "b", "aa", "ab", "ba", "bb", "aab", "aba", "abb", "baa", "bba"};                                  // 12 개: 길이 ≤ 3 이면서 가지가 갈라지고 접두사 관계가 섞이는 문자열
    std::vector<std::string> queries = universe; for (const char* q : {"aaa", "bab", "bbb", "aaaa", "abab", "bbbb", "abba", "baba"}) queries.push_back(q);
    std::mt19937 rng(105);
    for (int mask = 0; mask < (1 << 12); ++mask) {
        std::vector<std::string> ks; std::set<std::string> ref; for (int i = 0; i < 12; ++i) if (mask >> i & 1) { ks.push_back(universe[i]); ref.insert(universe[i]); }
        std::shuffle(ks.begin(), ks.end(), rng); Patricia t; for (auto& k : ks) { bool a = t.insert(k); assert(a); assert(!t.insert(k)); }
        assert(t.valid() && t.words == ref.size() && t.nodeCount() == expectedNodes(ref) && t.keys() == std::vector<std::string>(ref.begin(), ref.end()));
        for (auto& q : queries) { assert(t.contains(q) == (ref.count(q) > 0)); assert(t.longestPrefixOf(q) == refLongestPrefix(ref, q)); std::vector<std::string> want; for (auto& k : ref) if (k.compare(0, q.size(), q) == 0 && k.size() >= q.size()) want.push_back(k); assert(t.startsWith(q) == want); } }
    { Patricia t; std::set<std::string> ref; size_t merges = 0;
      for (long step = 0; step < 120000; ++step) { std::string w; int len = (int)(rng() % 9); for (int j = 0; j < len; ++j) w += (char)('a' + rng() % 3);
          if (rng() % 2) { bool a = t.insert(w); bool r = ref.insert(w).second; assert(a == r); } else { size_t before = t.nodeCount(); bool a = t.erase(w); bool r = ref.erase(w) > 0; assert(a == r); if (a && t.nodeCount() + 1 < before) ++merges; }
          if (step % 6007 == 0) assert(t.valid() && t.nodeCount() == expectedNodes(ref)); }
      assert(t.valid() && t.keys() == std::vector<std::string>(ref.begin(), ref.end()) && merges > 100);
      for (auto& k : std::vector<std::string>(ref.begin(), ref.end())) { bool a = t.erase(k); assert(a); } assert(t.words == 0 && t.nodeCount() == 1 && t.valid());
      Patricia one; std::string big(100000, 'a'); one.insert(big); assert(one.nodeCount() == 2 && one.contains(big) && !one.contains(std::string(99999, 'a')) && one.longestPrefixOf(big + "b") == 100000);
      std::cout << "PatriciaTrie: all 4096 subsets of 12 short strings (random insertion orders) satisfied the compression invariants with the exact node count, and 1.2*10^5 random insert/erase operations matched std::set (" << merges << " erases merged an edge pair); longest-prefix-match matched brute force" << std::endl; }
    return 0;
}
// Time Complexity: 삽입·삭제·조회 O(|key|)
// Space Complexity: O(키 수) 노드 (노드 수 < 2 · 키 수)
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
void destroyR(Node* n) { for (Node* k : n->kids) destroyR(k); delete n; }
void query(Node* n, const R& q, const std::vector<R>& rects, std::vector<int>& out) {
    if (!hit(n->box, q)) return; for (int id : n->ids) if (hit(rects[id], q)) out.push_back(id); for (Node* k : n->kids) query(k, q, rects, out);
}
int main() {
    std::mt19937 g(4); std::uniform_real_distribution<double> U(0, 1000); std::vector<R> rects; std::vector<std::pair<R, int>> items;
    for (int i = 0; i < 3000; i++) { double x = U(g), y = U(g); rects.push_back({x, y, x + U(g) / 20, y + U(g) / 20}); items.push_back({rects.back(), i}); }
    Node* root = pack(items, 8);
    for (int t = 0; t < 200; t++) { double x = U(g), y = U(g); R q{x, y, x + 60, y + 60}; std::vector<int> got, want; query(root, q, rects, got);
        for (int i = 0; i < 3000; i++) if (hit(rects[i], q)) want.push_back(i); std::sort(got.begin(), got.end()); assert(got == want); }
    std::cout << "RTree: STR-packed tree verified against brute force" << std::endl; destroyR(root); return 0;
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

// 커버 트리(Beygelzimer–Kakade–Langford): 이중 차원(doubling dimension)이 작은 거리 공간에서 최근접 탐색을 O(c^12 log n) 에(삽입은 O(c^6 log n)) 보장하는 트리. 점들은 서로 달라야 한다 (같은 점을 또 넣으면 어느 레벨에서도 분리되지 않아 끝없이 내려간다). 각 점은 "레벨 i" 에 속하며 세 가지를 지킨다:
//   중첩  C_i ⊂ C_(i-1)    덮기  C_(i-1) 의 모든 점 p 는 C_i 의 어떤 점 q 가 d(p,q) <= 2^i 로 덮는다 (그 q 가 p 의 부모)    분리  C_i 의 서로 다른 두 점은 거리 > 2^i
// 검증: 모든 레벨 minL..maxL 에서 분리 불변식(전수 쌍 검사)과 덮기 불변식, 무작위 질의 300 개의 NN 이 전수 탐색과 같다 (거리 계산 횟수는 참고로 출력).
// 레벨 i 는 "반지름 2^i 해상도"이므로 위로 갈수록 성기고 아래로 갈수록 촘촘하다. 삽입은 점이 들어갈 수 있는 가장 낮은 레벨을 위에서 아래로 찾고, NN 질의는 레벨을 내려가며
// 후보 집합 Q 를 "d(q, Q) + 2^i 이내" 로 줄인다 (레벨 i 노드의 모든 후손은 2^i 이내이므로 그보다 먼 후보는 정답이 될 수 없다)
typedef std::vector<double> P;
std::vector<P> pts; std::vector<int> lvl; std::vector<std::vector<int>> kids; int root = -1, maxL = 0, minL = 0; long evals = 0;
double d(int a, const P& q) { evals++; double s = 0; for (size_t i = 0; i < q.size(); i++) s += (pts[a][i] - q[i]) * (pts[a][i] - q[i]); return std::sqrt(s); }
double pw(int i) { return std::ldexp(1.0, i); }
bool insertRec(int p, const std::vector<int>& Q, int i) {                   // Q: 레벨 >= i 인 노드들 중 p 를 덮을 수 있는 후보
    assert(i > -500);                                                      // 점이 모두 다르다는 전제: 중복 점이면 레벨이 끝없이 내려간다
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
    for (int i = minL; i <= maxL; i++) {                                    // 분리 불변식: 레벨 i 에 존재하는 점들(lvl >= i)은 서로 > 2^i
        std::vector<int> Ci; for (int p = 0; p < n; p++) if (lvl[p] >= i) Ci.push_back(p);
        for (size_t a = 0; a < Ci.size(); a++) for (size_t b = a + 1; b < Ci.size(); b++) { double s = 0; for (int k = 0; k < 3; k++) s += (pts[Ci[a]][k] - pts[Ci[b]][k]) * (pts[Ci[a]][k] - pts[Ci[b]][k]); assert(std::sqrt(s) > pw(i) - 1e-12); }
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
// Time Complexity: 삽입 O(c^6 log N), NN 질의 O(c^12 log N) (c: 팽창 상수)
// Space Complexity: O(N)
```
## DCEL()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// DCEL(Doubly-Connected Edge List, 반변 구조): 평면 그래프를 "방향 있는 반변" 으로 저장한다. 무방향 변 하나가 서로 반대인 두 반변(twin)이 되고, 각 반변은
// origin(시작점), twin(반대 반변), next(같은 면의 경계를 따라 이어지는 다음 반변: 면을 왼쪽에 두고 반시계로 돈다), prev, face(왼쪽 면) 를 가진다.
// 덕분에 "면의 경계 훑기", "점 둘레의 변 훑기", "변 양쪽의 면 알기", "면 쪼개기(대각선 추가)" 가 모두 포인터 몇 개를 따라가는 O(1) 단계이다 (계산기하의 지도 겹치기·삼각분할·보로노이의 기본 틀).
// 만드는 법: 점마다 나가는 반변을 각도(정수 외적으로 정확히)순으로 정렬해 e_0..e_{m-1} 이라 하면 next(twin(e_i)) = e_{i-1}  (들어온 변 다음에는 시계 방향으로 한 칸 앞의 변으로 나간다). 면 = next 의 순환.
// 검증: ① 손으로 확인한 정사각형+대각선: 반변 10 개, 면 3 개(삼각형 둘 + 바깥), 바깥 면의 넓이 부호는 음수 ② 무작위 격자형 평면 그래프(변 일부 삭제, 칸마다 대각선 0~1 개): twin·next·prev 일관성, 점 둘레의
//       순환 길이 = 차수, 오일러 공식 V - E + F = 2C (성분마다 바깥 면 하나), 양의 넓이 면의 수 = E - V + C (유계 면), 넓이 합 = 0 ③ 볼록 다각형을 무작위 대각선으로 삼각분할: 면 +1, 두 새 면의 넓이 합 = 옛 면의 넓이
struct Pt { long long x, y; };
long long cross(Pt o, Pt a, Pt b) { return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x); }
struct Dcel {
    struct HE { int origin, twin, next, prev, face; };
    std::vector<Pt> p; std::vector<HE> h; std::vector<int> out; int faces = 0;                   // out[v]: v 에서 나가는 반변 하나(-1 이면 간선 없는 점)
    int dest(int e) const { return h[h[e].twin].origin; }
    Dcel(const std::vector<Pt>& pts, const std::vector<std::pair<int, int>>& edges) : p(pts), out(pts.size(), -1) {
        for (auto [u, w] : edges) { int a = (int)h.size(); h.push_back({u, a + 1, -1, -1, -1}); h.push_back({w, a, -1, -1, -1}); }
        std::vector<std::vector<int>> around(p.size()); for (int e = 0; e < (int)h.size(); ++e) around[h[e].origin].push_back(e);
        for (int v = 0; v < (int)p.size(); ++v) {
            auto dir = [&](int e) { return Pt{p[dest(e)].x - p[v].x, p[dest(e)].y - p[v].y}; };
            auto half = [](Pt d) { return (d.y > 0 || (d.y == 0 && d.x > 0)) ? 0 : 1; };           // 위쪽 반평면(0°..180° 미만) 먼저
            std::sort(around[v].begin(), around[v].end(), [&](int a, int b) { Pt da = dir(a), db = dir(b); if (half(da) != half(db)) return half(da) < half(db); return da.x * db.y - da.y * db.x > 0; });
            const int m = (int)around[v].size(); if (m) out[v] = around[v][0];
            for (int i = 0; i < m; ++i) { int nx = h[around[v][i]].twin, to = around[v][(i + m - 1) % m]; h[nx].next = to; h[to].prev = nx; }
        }
        labelFaces();
    }
    void labelFaces() { for (auto& e : h) e.face = -1; faces = 0; for (int e = 0; e < (int)h.size(); ++e) if (h[e].face < 0) { for (int x = e; h[x].face < 0; x = h[x].next) h[x].face = faces; ++faces; } }
    std::vector<int> boundary(int e) const { std::vector<int> r; int x = e; do { r.push_back(x); x = h[x].next; } while (x != e); return r; }       // e 와 같은 면의 경계를 한 바퀴
    long long area2(int e) const { long long s = 0; for (int x : boundary(e)) { Pt a = p[h[x].origin], b = p[dest(x)]; s += a.x * b.y - b.x * a.y; } return s; }   // 2 x 부호 있는 넓이 (반시계 > 0)
    void splitFace(int h1, int h2) {                                                              // 같은 면의 두 반변 h1, h2 의 시작점을 잇는 변을 넣어 면을 둘로 쪼갠다
        int a = (int)h.size(), b = a + 1, before1 = h[h1].prev, before2 = h[h2].prev;
        h.push_back({h[h1].origin, b, h2, before1, -1}); h.push_back({h[h2].origin, a, h1, before2, -1});     // a: u→v, b: v→u
        h[before1].next = a; h[h2].prev = a; h[before2].next = b; h[h1].prev = b; labelFaces();
    }
    bool consistent() const {
        for (int e = 0; e < (int)h.size(); ++e) {
            if (h[h[e].twin].twin != e || h[h[e].next].prev != e || h[h[e].prev].next != e || h[h[e].next].origin != dest(e) || h[h[e].next].face != h[e].face) return false;
            if (h[e].origin == dest(e)) return false;
        }
        return true;
    }
};

int main() {
    {   Dcel d({{0, 0}, {2, 0}, {2, 2}, {0, 2}}, {{0, 1}, {1, 2}, {2, 3}, {3, 0}, {0, 2}});          // 손으로 확인: 정사각형 + 대각선 0-2
        assert(d.h.size() == 10 && d.faces == 3 && d.consistent());
        std::vector<long long> areas; for (int f = 0; f < d.faces; ++f) { int e = 0; while (d.h[e].face != f) ++e; areas.push_back(d.area2(e)); }
        std::sort(areas.begin(), areas.end()); assert((areas == std::vector<long long>{-8, 4, 4}));    // 바깥 면 -8 (넓이 -4 x 2), 삼각형 둘 +4 (넓이 2 x 2)
        int e01 = 0; assert(d.h[e01].origin == 0 && d.dest(e01) == 1 && d.h[d.h[e01].twin].face != d.h[e01].face);   // 변 0→1 의 왼쪽은 안쪽 삼각형, 오른쪽은 바깥
        int deg = 0, e = d.out[0]; do { ++deg; e = d.h[d.h[e].twin].next; } while (e != d.out[0]); assert(deg == 3); }   // 점 0 둘레: 변 3 개 (시계 방향으로 한 바퀴)
    std::mt19937 rng(23);
    for (int trial = 0; trial < 300; ++trial) {
        const int R = 2 + (int)(rng() % 5), C = 2 + (int)(rng() % 5); std::vector<Pt> pts; for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) pts.push_back({c * 4, r * 4});
        std::vector<std::pair<int, int>> edges; auto id = [&](int r, int c) { return r * C + c; };
        for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) {
            if (c + 1 < C && rng() % 4) edges.push_back({id(r, c), id(r, c + 1)});
            if (r + 1 < R && rng() % 4) edges.push_back({id(r, c), id(r + 1, c)});
            if (r + 1 < R && c + 1 < C) { int k = (int)(rng() % 3); if (k == 1) edges.push_back({id(r, c), id(r + 1, c + 1)}); else if (k == 2) edges.push_back({id(r, c + 1), id(r + 1, c)}); }   // 칸마다 대각선 0~1 개(교차 없음)
        }
        if (edges.empty()) continue;
        Dcel d(pts, edges); assert(d.consistent());
        std::vector<int> uf(pts.size()); std::iota(uf.begin(), uf.end(), 0); auto find = [&](int x) { while (uf[x] != x) x = uf[x] = uf[uf[x]]; return x; };
        std::vector<char> used(pts.size(), 0); for (auto [u, w] : edges) { uf[find(u)] = find(w); used[u] = used[w] = 1; }
        int V = 0, C2 = 0; for (size_t v = 0; v < pts.size(); ++v) if (used[v]) { ++V; C2 += find((int)v) == (int)v; }          // 변이 있는 점의 수와 성분 수
        const int E = (int)edges.size();
        assert(V - E + d.faces == 2 * C2);                                                            // 오일러: 성분마다 V_i - E_i + F_i = 2 (바깥 면을 성분별로 센다)
        int bounded = 0, outer = 0; long long total = 0;
        for (int f = 0; f < d.faces; ++f) { int e = 0; while (d.h[e].face != f) ++e; long long a2 = d.area2(e); total += a2; (a2 > 0 ? bounded : outer)++; }
        assert(bounded == E - V + C2 && outer == C2 && total == 0);                                  // 유계 면 E-V+C 개는 넓이 > 0, 성분마다 바깥 경계 하나(넓이 <= 0), 넓이 합 0
        for (size_t v = 0; v < pts.size(); ++v) if (used[v]) { int deg = 0, x = d.out[v]; do { ++deg; x = d.h[d.h[x].twin].next; } while (x != d.out[v]); int want = 0; for (auto [a, b] : edges) want += (a == (int)v) + (b == (int)v); assert(deg == want); }
    }
    for (int trial = 0; trial < 100; ++trial) {                                                       // 포물선 위의 점 n 개로 이루어진 볼록 다각형을 무작위 대각선으로 삼각분할
        const int n = 4 + (int)(rng() % 12); std::vector<Pt> pts; for (int i = 0; i < n; ++i) { long long t = i * 7 - (long long)n * 3; pts.push_back({t, t * t}); }   // 포물선 위의 점들: 어느 세 점도 일직선이 아니고 볼록
        std::vector<std::pair<int, int>> edges; for (int i = 0; i < n; ++i) edges.push_back({i, (i + 1) % n});
        Dcel d(pts, edges); assert(d.faces == 2 && d.consistent());
        int inner = 0; while (d.h[inner].face < 0 || d.area2(inner) <= 0) ++inner; long long total = d.area2(inner);
        std::vector<int> pieceEdge = {inner};
        for (int step = 0; step < n - 3; ++step) {                                                    // 아직 쪼개지지 않은 가장 큰 조각의 꼭짓점 둘을 골라 대각선을 넣는다
            int best = 0; for (size_t i = 1; i < pieceEdge.size(); ++i) if (d.boundary(pieceEdge[i]).size() > d.boundary(pieceEdge[best]).size()) best = (int)i;
            std::vector<int> bd = d.boundary(pieceEdge[best]); const int m = (int)bd.size(); assert(m >= 4);
            int i = (int)(rng() % m), j = (i + 2 + (int)(rng() % (m - 3))) % m;                      // 이웃하지 않는 두 꼭짓점
            long long before = d.area2(bd[0]); const int facesBefore = d.faces; d.splitFace(bd[i], bd[j]);
            assert(d.faces == facesBefore + 1 && d.consistent());
            int a = (int)d.h.size() - 2, b = a + 1;                                                   // 새 반변 a(u→v), b(v→u)
            assert(d.area2(a) > 0 && d.area2(b) > 0 && d.area2(a) + d.area2(b) == before);            // 두 새 조각의 넓이 합 = 옛 조각의 넓이
            pieceEdge[best] = a; pieceEdge.push_back(b);
        }
        assert(d.faces == n - 1);                                                                     // 삼각형 n-2 개 + 바깥 면
        long long sum = 0; for (int e : pieceEdge) { assert(d.boundary(e).size() == 3); sum += d.area2(e); } assert(sum == total);
    }
    std::cout << "DCEL: twin/next/prev stayed consistent on 300 random grid-like planar graphs and 100 triangulated convex polygons; Euler's formula V-E+F=2C, bounded-face count E-V+C (positive area), per-vertex cycle length = degree and area conservation under face splitting all held" << std::endl;
    return 0;
}
// Time Complexity: 만들기 O(E log E) (점마다 각도 정렬), 면·점 둘레 훑기 O(둘레 길이), splitFace O(1) (+ 면 번호 다시 매기기 O(E))
// Space Complexity: O(V + E)
```

## QuadEdge()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 쿼드엣지(Quad-Edge, Guibas–Stolfi 1985): 변 하나를 "네 개의 방향 있는 변" 으로 저장한다 — 본래 변 e, 그 위치의 쌍대 변(Rot, 오른쪽 면에서 왼쪽 면으로 가는 변), 반대 방향 Sym, 반대 방향의 쌍대 InvRot.
// 변 참조는 4q + r (q: 변 번호, r: 회전 0..3), Rot(e) = e 를 90° 돌린 것, Sym = Rot², Onext(e) = 같은 시작점에서 반시계로 다음 변 하나만 저장하면 나머지(Oprev, Lnext 등)는 Rot 으로 구한다.
// 한 구조가 평면 분할과 그 쌍대(점 <-> 면)를 동시에 표현하므로 볼록 껍질·보로노이/들로네 알고리즘에서 "삼각형의 이웃" 을 포인터 하나로 돈다. 기본 연산은 둘뿐이다: MakeEdge(떨어진 변 하나 만들기)와
// Splice(a, b)(a 와 b 의 Onext 고리를 합치거나 가르고, 쌍대 고리에도 같은 일을 한다). Connect·DeleteEdge 는 Splice 두 번이다. 점의 둘레 = Onext 의 순환, 면의 경계 = Lnext 의 순환.
// 검증: ① 항등식 rot^4 = id, rot^2 = sym, onext∘oprev = id ② 정다면체(정사면체·정육면체)와 토러스 격자의 회전계(각 점의 이웃 순서)로 쿼드엣지를 만들어 오일러 지표 V - E + F 가 2(구) 와 0(토러스)
//       ③ 다각형을 Connect 로 삼각분할: 면 수가 한 개씩 늘고 모두 삼각형, DeleteEdge 를 거꾸로 하면 원래의 두 면(길이 n)으로 정확히 돌아온다
struct QuadEdge {
    std::vector<int> onextOf, orgOf;                                                              // onextOf[e]: Onext(e), orgOf[e]: 본래 변(r 가 짝수)의 시작점
    static int rot(int e) { return (e & ~3) | ((e + 1) & 3); }
    static int invrot(int e) { return (e & ~3) | ((e + 3) & 3); }
    static int sym(int e) { return e ^ 2; }
    int onext(int e) const { return onextOf[e]; }
    int oprev(int e) const { return rot(onextOf[rot(e)]); }
    int lnext(int e) const { return rot(onextOf[invrot(e)]); }                                    // 왼쪽 면의 경계를 따라 다음 변
    int org(int e) const { return orgOf[e]; }
    int dest(int e) const { return orgOf[sym(e)]; }
    int makeEdge(int a, int b) { int e = (int)onextOf.size(); onextOf.insert(onextOf.end(), {e, e + 3, e + 2, e + 1}); orgOf.insert(orgOf.end(), {a, -1, b, -1}); return e; }   // Onext: e→e, Rot→InvRot, Sym→Sym, InvRot→Rot
    void splice(int a, int b) { int alpha = rot(onextOf[a]), beta = rot(onextOf[b]); std::swap(onextOf[a], onextOf[b]); std::swap(onextOf[alpha], onextOf[beta]); }
    int connect(int a, int b) { int e = makeEdge(dest(a), org(b)); splice(e, lnext(a)); splice(sym(e), b); return e; }   // a 의 도착점에서 b 의 시작점으로 가는 새 변: 면 하나를 둘로 쪼갠다
    void deleteEdge(int e) { splice(e, oprev(e)); splice(sym(e), oprev(sym(e))); }
    // 짝수 참조(본래 변) 중 live 에 속한 것들을 f 의 순환으로 묶어 각 순환의 길이를 돌려준다
    template <class F> std::vector<int> orbits(const std::vector<int>& live, F f) const {
        std::set<int> seen; std::vector<int> sizes;
        for (int q : live) for (int r : {0, 2}) { int e = 4 * q + r; if (seen.count(e)) continue; int len = 0; for (int x = e; !seen.count(x); x = f(x)) { seen.insert(x); ++len; } sizes.push_back(len); }
        return sizes;
    }
};
// 회전계(각 점의 이웃을 반시계 순서로 나열)에서 쿼드엣지를 만든다. 변 {u,v} 마다 makeEdge, 점마다 Splice 를 이어 붙여 Onext 고리를 이웃 순서대로 맞춘다.
QuadEdge fromRotationSystem(const std::vector<std::vector<int>>& nbrs, std::vector<int>& live) {
    QuadEdge qe; std::map<std::pair<int, int>, int> ref;                                          // (u, v) -> u 에서 v 로 가는 변 참조
    for (int u = 0; u < (int)nbrs.size(); ++u) for (int v : nbrs[u]) if (u < v) { int e = qe.makeEdge(u, v); ref[{u, v}] = e; ref[{v, u}] = QuadEdge::sym(e); live.push_back(e / 4); }
    for (int u = 0; u < (int)nbrs.size(); ++u) for (size_t i = 1; i < nbrs[u].size(); ++i) qe.splice(ref[{u, nbrs[u][i - 1]}], ref[{u, nbrs[u][i]}]);   // d0, d1, ... 순서의 고리가 된다
    return qe;
}
int eulerCharacteristic(const QuadEdge& qe, const std::vector<int>& live, int V) {
    int E = (int)live.size(), F = (int)qe.orbits(live, [&](int e) { return qe.lnext(e); }).size();
    int Vorb = (int)qe.orbits(live, [&](int e) { return qe.onext(e); }).size();                   // 점 = Onext 의 순환 (고립점 제외)
    assert(Vorb == V);
    return V - E + F;
}
void identities(const QuadEdge& qe, const std::vector<int>& live) {
    for (int q : live) for (int r = 0; r < 4; ++r) {
        int e = 4 * q + r;
        assert(QuadEdge::rot(QuadEdge::rot(QuadEdge::rot(QuadEdge::rot(e)))) == e && QuadEdge::rot(QuadEdge::rot(e)) == QuadEdge::sym(e) && QuadEdge::sym(QuadEdge::sym(e)) == e);
        assert(qe.onext(qe.oprev(e)) == e && qe.oprev(qe.onext(e)) == e);                       // Oprev 는 Onext 의 역
    }
}

int main() {
    {   std::vector<int> live; QuadEdge qe = fromRotationSystem({{1, 2, 3}, {0, 3, 2}, {0, 1, 3}, {0, 2, 1}}, live);   // 정사면체 K4 (한 면을 바깥으로 펼친 평면 그림의 회전계)
        identities(qe, live); assert(live.size() == 6 && eulerCharacteristic(qe, live, 4) == 2);
        for (int s : qe.orbits(live, [&](int e) { return qe.lnext(e); })) assert(s == 3); }      // 면 4 개, 모두 삼각형
    {   // 정육면체: 아래 4 점 0..3 (반시계), 위 4 점 4..7. 평면 그림: 안쪽 정사각형 4..7 이 바깥 정사각형 0..3 안에 있다
        std::vector<std::vector<int>> nb = {{1, 3, 4}, {2, 0, 5}, {3, 1, 6}, {0, 2, 7}, {7, 5, 0}, {4, 6, 1}, {5, 7, 2}, {6, 4, 3}};
        std::vector<int> live; QuadEdge qe = fromRotationSystem(nb, live);
        identities(qe, live); assert(live.size() == 12 && eulerCharacteristic(qe, live, 8) == 2);
        for (int s : qe.orbits(live, [&](int e) { return qe.lnext(e); })) assert(s == 4); }      // 면 6 개, 모두 사각형
    {   const int R = 3, C = 3; std::vector<std::vector<int>> nb(R * C);                         // 토러스 격자: 각 점의 이웃을 동·북·서·남 순서로 (가장자리가 반대편과 이어진다)
        for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) nb[r * C + c] = {r * C + (c + 1) % C, ((r + 1) % R) * C + c, r * C + (c + C - 1) % C, ((r + R - 1) % R) * C + c};
        std::vector<int> live; QuadEdge qe = fromRotationSystem(nb, live);
        identities(qe, live); assert(live.size() == 18 && eulerCharacteristic(qe, live, 9) == 0);   // 구가 아니라 토러스: V - E + F = 0
        for (int s : qe.orbits(live, [&](int e) { return qe.lnext(e); })) assert(s == 4); }      // 면 9 개
    std::mt19937 rng(29);
    for (int trial = 0; trial < 200; ++trial) {                                                   // 다각형 삼각분할: MakeEdge + Splice 로 고리를 만들고 Connect 로 쪼갠다
        const int n = 4 + (int)(rng() % 12); QuadEdge qe; std::vector<int> ring, live;
        for (int i = 0; i < n; ++i) { ring.push_back(qe.makeEdge(i, (i + 1) % n)); live.push_back(ring.back() / 4); }
        for (int i = 0; i < n; ++i) qe.splice(QuadEdge::sym(ring[i]), ring[(i + 1) % n]);        // 변 i 의 도착점에서 변 i+1 이 시작하도록 Onext 고리를 잇는다
        identities(qe, live); assert(eulerCharacteristic(qe, live, n) == 2);
        auto before = qe.orbits(live, [&](int e) { return qe.lnext(e); }); assert(before.size() == 2 && before[0] == n && before[1] == n);
        std::vector<int> added; std::set<int> outer; for (int x = QuadEdge::sym(ring[0]); outer.insert(x).second; x = qe.lnext(x)) {}      // sym(ring[0]) 의 왼쪽 면 = 바깥 면 (쪼개지 않는다)
        for (int step = 0; step < n - 3; ++step) {                                                // 안쪽에서 가장 긴 면의 경계에서 이웃하지 않는 두 변을 골라 Connect
            int best = -1, bestLen = 0; for (int q : live) for (int r : {0, 2}) { int e = 4 * q + r, len = 1; if (outer.count(e)) continue; for (int x = qe.lnext(e); x != e; x = qe.lnext(x)) ++len; if (len > bestLen) { bestLen = len; best = e; } }
            std::vector<int> face{best}; for (int x = qe.lnext(best); x != best; x = qe.lnext(x)) face.push_back(x);
            const int m = (int)face.size(); assert(m >= 4); int i = (int)(rng() % m), j = (i + 3 + (int)(rng() % (m - 3))) % m;   // Connect(a, b) 는 a 의 도착점과 b 의 시작점을 잇는다: 둘이 이웃(또는 같은 점)이 되지 않게
            int e = qe.connect(face[i], face[j]); added.push_back(e); live.push_back(e / 4);
            identities(qe, live); assert(eulerCharacteristic(qe, live, n) == 2);                  // V - E + F = 2 가 매 단계 유지된다 (F 가 하나씩 늘어난다)
        }
        auto faces = qe.orbits(live, [&](int e) { return qe.lnext(e); }); std::sort(faces.begin(), faces.end());
        assert((int)faces.size() == n - 1 && faces.front() == 3 && std::count(faces.begin(), faces.end(), 3) == n - 2 && faces.back() == n);   // 삼각형 n-2 개 + 바깥 면 하나(길이 n)
        for (size_t k = added.size(); k-- > 0;) { qe.deleteEdge(added[k]); live.pop_back(); identities(qe, live); assert(eulerCharacteristic(qe, live, n) == 2); }
        auto after = qe.orbits(live, [&](int e) { return qe.lnext(e); }); assert(after == before);   // 거꾸로 지우면 원래의 두 면으로 정확히 돌아온다
    }
    std::cout << "QuadEdge: rot/sym/onext-oprev identities held; tetrahedron, cube and 3x3 torus rotation systems gave Euler characteristics 2, 2 and 0 from the Lnext face orbits; 200 random polygon triangulations via Connect kept V-E+F=2 and DeleteEdge restored the original two faces" << std::endl;
    return 0;
}
// Time Complexity: MakeEdge·Splice·Connect·DeleteEdge 모두 O(1), 점·면 훑기는 둘레 길이에 비례
// Space Complexity: 변 하나당 4 칸 (Onext) + 시작점 — O(E)
```
# Part 6. 범위 질의
## SegmentTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>

// 세그먼트 트리 (게으른 전파, lazy propagation): 구간 [l, r] 의 모든 원소에 *아핀 변환* x → a·x + b (mod p) 를 O(log n) 에 적용하고 구간 합을 O(log n) 에 구한다.
//  덧셈(a = 1), 대입(a = 0), 곱셈(b = 0) 이 모두 이 하나의 틀이다 — 합성 (a2, b2)∘(a1, b1) = (a2·a1, a2·b1 + b2) 이 결합 법칙을 만족하는 *모노이드*이므로 "미뤄 둔 변환"을 노드에 쌓아 둘 수 있다.  노드 합에 변환을 적용할 때는 구간 길이를 곱한다: sum' = a·sum + b·len.
//  (반복형 비재귀 판과 모노이드 일반형은 Tree.md Part 11, 일반 지연 전파는 Tree.md Part 12.)  ① n = 1..30 의 모든 구간에서 무작위 연산 열(변환·구간 합)을 순진한 배열과 대조  ② n = 1000 에서 4 만 번  ③ n = 10^6 에서 연산 300 번을 순진한 배열과 대조(구간 길이 최대 10^6)
//  ④ n = 10^6 에서 *덧셈만* 100 만 번: 독립 구조(펜윅 두 개로 만든 구간 갱신-구간 합)와 대조.
static const uint64_t MOD = 998244353ULL;
struct Lazy { uint64_t a, b; };
Lazy compose(Lazy second, Lazy first) { return {second.a * first.a % MOD, (second.a * first.b + second.b) % MOD}; }       // second ∘ first
struct SegTree {
    int n; std::vector<uint64_t> sum; std::vector<Lazy> lz; std::vector<char> has;
    explicit SegTree(const std::vector<uint64_t>& a) : n((int)a.size()), sum(4 * a.size()), lz(4 * a.size(), Lazy{1, 0}), has(4 * a.size(), 0) { build(1, 0, n - 1, a); }
    void build(int u, int l, int r, const std::vector<uint64_t>& a) { if (l == r) { sum[u] = a[l] % MOD; return; } int m = (l + r) / 2; build(2 * u, l, m, a); build(2 * u + 1, m + 1, r, a); sum[u] = (sum[2 * u] + sum[2 * u + 1]) % MOD; }
    void applyNode(int u, int len, Lazy f) { sum[u] = (f.a * sum[u] + f.b * (uint64_t)len) % MOD; lz[u] = compose(f, lz[u]); has[u] = 1; }
    void push(int u, int l, int r) { if (!has[u]) return; int m = (l + r) / 2; applyNode(2 * u, m - l + 1, lz[u]); applyNode(2 * u + 1, r - m, lz[u]); lz[u] = {1, 0}; has[u] = 0; }
    void update(int u, int l, int r, int ql, int qr, Lazy f) { if (qr < l || r < ql) return; if (ql <= l && r <= qr) { applyNode(u, r - l + 1, f); return; } push(u, l, r); int m = (l + r) / 2; update(2 * u, l, m, ql, qr, f); update(2 * u + 1, m + 1, r, ql, qr, f); sum[u] = (sum[2 * u] + sum[2 * u + 1]) % MOD; }
    uint64_t query(int u, int l, int r, int ql, int qr) { if (qr < l || r < ql) return 0; if (ql <= l && r <= qr) return sum[u]; push(u, l, r); int m = (l + r) / 2; return (query(2 * u, l, m, ql, qr) + query(2 * u + 1, m + 1, r, ql, qr)) % MOD; }
    void apply(int l, int r, uint64_t a, uint64_t b) { update(1, 0, n - 1, l, r, Lazy{a % MOD, b % MOD}); }
    uint64_t rangeSum(int l, int r) { return query(1, 0, n - 1, l, r); }
};
struct Fen { int n; std::vector<uint64_t> t; explicit Fen(int n_) : n(n_), t(n_ + 2, 0) {} void add(int i, uint64_t v) { for (++i; i <= n + 1; i += i & -i) t[i] = (t[i] + v) % MOD; } uint64_t pre(int i) const { uint64_t s = 0; for (++i; i > 0; i -= i & -i) s = (s + t[i]) % MOD; return s; } };
struct RangeAddSum { int n; Fen b1, b2; explicit RangeAddSum(int n_) : n(n_), b1(n_ + 1), b2(n_ + 1) {}                          // 독립 오라클: 구간 더하기 + 구간 합
    void add(int l, int r, uint64_t v) { b1.add(l, v); b1.add(r + 1, MOD - v % MOD); b2.add(l, v % MOD * (uint64_t)l % MOD); b2.add(r + 1, (MOD - v % MOD) % MOD * (uint64_t)(r + 1) % MOD); }
    uint64_t prefix(int i) const { return (b1.pre(i) * (uint64_t)(i + 1) % MOD + MOD - b2.pre(i)) % MOD; } uint64_t range(int l, int r) const { return (prefix(r) + MOD - (l ? prefix(l - 1) : 0)) % MOD; } };

int main() {
    std::mt19937_64 rng(131);
    auto randomRun = [&](int n, int ops) {
        std::vector<uint64_t> ref(n); for (auto& x : ref) x = rng() % MOD; SegTree st(ref);
        for (int op = 0; op < ops; ++op) { int l = (int)(rng() % n), r = l + (int)(rng() % (n - l));
            if (rng() % 2) { int kind = (int)(rng() % 3); uint64_t a = kind == 0 ? 1 : kind == 1 ? 0 : rng() % MOD, b = kind == 2 ? 0 : rng() % MOD; st.apply(l, r, a, b); for (int i = l; i <= r; ++i) ref[i] = (a * ref[i] + b) % MOD; }
            else { uint64_t s = 0; for (int i = l; i <= r; ++i) s = (s + ref[i]) % MOD; assert(st.rangeSum(l, r) == s); } }
        uint64_t total = 0; for (uint64_t x : ref) total = (total + x) % MOD; assert(st.rangeSum(0, n - 1) == total); };
    for (int n = 1; n <= 30; ++n) for (int rep = 0; rep < 20; ++rep) randomRun(n, 300);                          // ①
    randomRun(1000, 40000);                                                                                      // ②
    randomRun(1000000, 300);                                                                                     // ③
    { const int n = 1000000; RangeAddSum oracle(n); std::vector<uint64_t> zeros(n, 0); SegTree st(zeros);                                // ④
      for (int op = 0; op < 1000000; ++op) { int l = (int)(rng() % n), r = l + (int)(rng() % (n - l)); if (rng() % 2) { uint64_t v = rng() % MOD; st.apply(l, r, 1, v); oracle.add(l, r, v); } else assert(st.rangeSum(l, r) == oracle.range(l, r)); } }
    std::cout << "SegmentTree: lazy affine updates (add / assign / multiply) and range sums matched a naive array for every size 1..30, 4*10^4 operations at n=1000 and 300 operations at n=10^6, and 10^6 range-add/range-sum operations matched an independent two-Fenwick structure" << std::endl;
    return 0;
}
// Time Complexity: build O(N), 구간 갱신·구간 합 O(log N)
// Space Complexity: O(N) (4N 칸)
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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 펜윅 트리(이진 인덱스 트리) 확장 — 2 차원: t[i][j] 가 직사각형 (i − lowbit(i), i] × (j − lowbit(j), j] 의 합을 담고, 점 갱신과 접두 직사각형 합이 각각 O(log R · log C).
//  임의의 직사각형 합은 포함-배제 4 항: S(r2, c2) − S(r1−1, c2) − S(r2, c1−1) + S(r1−1, c1−1).  *직사각형 갱신 + 점 질의*는 차분 4 점으로 한다: add(r1,c1,+v), add(r1,c2+1,−v), add(r2+1,c1,−v), add(r2+1,c2+1,+v) 후 점 (r, c) 의 값 = 접두 합.
//  (1 차원 판은 Tree.md Part 11.)  ① 격자 1×1 .. 6×6 전부에서 무작위 갱신 뒤 *모든* 직사각형 합을 순진한 합과 대조  ② 직사각형 갱신 + 점 질의를 순진한 격자와 대조  ③ 2000×2000 격자에서 갱신 100 만 번 — 10 만 번마다 2 차원 접두 합 표로 직사각형 2000 개를 대조.
struct Fenwick2D {
    int R, C; std::vector<long long> t;
    Fenwick2D(int r, int c) : R(r), C(c), t((size_t)(r + 1) * (c + 1), 0) {}
    long long& at(int i, int j) { return t[(size_t)i * (C + 1) + j]; }
    void add(int r, int c, long long v) { for (int i = r + 1; i <= R; i += i & -i) for (int j = c + 1; j <= C; j += j & -j) at(i, j) += v; }                  // 범위 밖(= R 또는 C) 은 무시
    long long prefix(int r, int c) { long long s = 0; for (int i = r + 1; i > 0; i -= i & -i) for (int j = c + 1; j > 0; j -= j & -j) s += at(i, j); return s; }       // [0..r] × [0..c], 음수 인덱스는 0
    long long rect(int r1, int c1, int r2, int c2) { return prefix(r2, c2) - (r1 ? prefix(r1 - 1, c2) : 0) - (c1 ? prefix(r2, c1 - 1) : 0) + (r1 && c1 ? prefix(r1 - 1, c1 - 1) : 0); }
    void rectAdd(int r1, int c1, int r2, int c2, long long v) { add(r1, c1, v); add(r1, c2 + 1, -v); add(r2 + 1, c1, -v); add(r2 + 1, c2 + 1, v); }                // 차분
    long long point(int r, int c) { return prefix(r, c); }
};

int main() {
    std::mt19937 rng(137);
    for (int R = 1; R <= 6; ++R) for (int C = 1; C <= 6; ++C) for (int rep = 0; rep < 20; ++rep) {                // ①
        Fenwick2D f(R, C); std::vector<std::vector<long long>> g(R, std::vector<long long>(C, 0));
        for (int k = 0; k < 15; ++k) { int r = (int)(rng() % R), c = (int)(rng() % C); long long v = (long long)(rng() % 21) - 10; f.add(r, c, v); g[r][c] += v; }
        for (int r1 = 0; r1 < R; ++r1) for (int c1 = 0; c1 < C; ++c1) for (int r2 = r1; r2 < R; ++r2) for (int c2 = c1; c2 < C; ++c2) { long long s = 0; for (int i = r1; i <= r2; ++i) for (int j = c1; j <= c2; ++j) s += g[i][j]; assert(f.rect(r1, c1, r2, c2) == s); } }
    for (int rep = 0; rep < 200; ++rep) {                                                                        // ② 직사각형 갱신 + 점 질의
        int R = 1 + (int)(rng() % 12), C = 1 + (int)(rng() % 12); Fenwick2D f(R, C); std::vector<std::vector<long long>> g(R, std::vector<long long>(C, 0));
        for (int k = 0; k < 30; ++k) { int r1 = (int)(rng() % R), c1 = (int)(rng() % C), r2 = r1 + (int)(rng() % (R - r1)), c2 = c1 + (int)(rng() % (C - c1)); long long v = (long long)(rng() % 21) - 10; f.rectAdd(r1, c1, r2, c2, v); for (int i = r1; i <= r2; ++i) for (int j = c1; j <= c2; ++j) g[i][j] += v; }
        for (int i = 0; i < R; ++i) for (int j = 0; j < C; ++j) assert(f.point(i, j) == g[i][j]); }
    { const int N = 2000; Fenwick2D f(N, N); std::vector<long long> g((size_t)N * N, 0);                          // ③
      for (long step = 1; step <= 1000000; ++step) { int r = (int)(rng() % N), c = (int)(rng() % N); long long v = (long long)(rng() % 2001) - 1000; f.add(r, c, v); g[(size_t)r * N + c] += v;
        if (step % 100000 == 0) { std::vector<long long> pre((size_t)(N + 1) * (N + 1), 0); for (int i = 0; i < N; ++i) for (int j = 0; j < N; ++j) pre[(size_t)(i + 1) * (N + 1) + j + 1] = g[(size_t)i * N + j] + pre[(size_t)i * (N + 1) + j + 1] + pre[(size_t)(i + 1) * (N + 1) + j] - pre[(size_t)i * (N + 1) + j];
          for (int q = 0; q < 2000; ++q) { int r1 = (int)(rng() % N), c1 = (int)(rng() % N), r2 = r1 + (int)(rng() % (N - r1)), c2 = c1 + (int)(rng() % (N - c1)); long long want = pre[(size_t)(r2 + 1) * (N + 1) + c2 + 1] - pre[(size_t)r1 * (N + 1) + c2 + 1] - pre[(size_t)(r2 + 1) * (N + 1) + c1] + pre[(size_t)r1 * (N + 1) + c1]; assert(f.rect(r1, c1, r2, c2) == want); } } } }
    std::cout << "FenwickTree (2D): every rectangle sum on all grids from 1x1 to 6x6 matched naive sums, rectangle-add/point-query through four difference points matched a naive grid, and 10^6 updates on a 2000x2000 grid matched a 2D prefix table" << std::endl;
    return 0;
}
// Time Complexity: 점 갱신·접두 합 O(log R · log C), 직사각형 합 4 번의 접두 합
// Space Complexity: O(R · C)
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

## DisjointSparseTable()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 분리 희소 표(Disjoint Sparse Table): 희소 표(Sparse Table)는 구간을 겹쳐 덮어야 해서 min·max·gcd 처럼 "겹쳐도 같은 값"(멱등) 연산만 되지만,
// 이 표는 구간을 겹치지 않게 둘로 나눠 덮으므로 합·곱·행렬곱·문자열 이어 붙이기처럼 결합법칙만 성립하는 연산이면 모두 O(1) 에 답한다(교환법칙도 필요 없다).
// 구조: 수준 h(1..log N) 마다 배열을 길이 2^h 의 블록으로 나누고 각 블록의 가운데 mid 에서 왼쪽 절반은 "i 부터 mid-1 까지", 오른쪽 절반은 "mid 부터 i 까지" 의 값을 저장한다.
// 질의 [l, r] (l < r): l 과 r 이 처음 갈라지는 비트 h-1 = 가장 높은 1 비트(l xor r) 를 찾으면 수준 h 의 블록 가운데를 사이에 두므로 답 = table[h][l] ⊕ table[h][r]. 전처리 O(N log N), 질의 O(1).
// 검증: ① 교환법칙이 성립하는 min·합 ② 교환법칙이 없는 2x2 행렬곱(mod p)·문자열 이어 붙이기 — 길이 1..40 은 모든 구간, 큰 길이는 무작위 구간을 순진한 접기와 비교 ③ 수준 수 = ceil(log2 N), 저장량 = N x 수준 수
template <class T, class Op> struct DisjointSparseTable {
    int n, LOG; std::vector<std::vector<T>> tb; std::vector<T> a; Op op;
    DisjointSparseTable(const std::vector<T>& v, Op o) : n((int)v.size()), LOG(1), a(v), op(o) {
        while ((1 << LOG) < n) ++LOG;
        const int N = 1 << LOG; a.resize(N, v.empty() ? T() : v.back());                          // 2 의 거듭제곱으로 채운다(채운 칸은 질의에 쓰이지 않는다)
        tb.assign(LOG + 1, std::vector<T>(N));
        for (int h = 1; h <= LOG; ++h) {
            const int half = 1 << (h - 1);
            for (int s = 0; s < N; s += 2 * half) {
                const int mid = s + half;
                tb[h][mid - 1] = a[mid - 1]; for (int i = mid - 2; i >= s; --i) tb[h][i] = op(a[i], tb[h][i + 1]);     // 가운데에서 왼쪽으로 쌓는다: a[i] ⊕ ... ⊕ a[mid-1]
                tb[h][mid] = a[mid]; for (int i = mid + 1; i < s + 2 * half; ++i) tb[h][i] = op(tb[h][i - 1], a[i]);   // 오른쪽으로 쌓는다: a[mid] ⊕ ... ⊕ a[i]
            }
        }
    }
    T query(int l, int r) const {                                                                 // 0 <= l <= r < n, 양 끝 포함
        if (l == r) return a[l];
        const int h = 32 - __builtin_clz((unsigned)(l ^ r));                                      // l, r 이 갈라지는 수준 (가장 높은 다른 비트의 위치 + 1)
        return op(tb[h][l], tb[h][r]);
    }
};
struct Mat { long long a, b, c, d; bool operator==(const Mat& o) const { return a == o.a && b == o.b && c == o.c && d == o.d; } };
const long long MOD = 1000000007LL;
Mat matMul(const Mat& x, const Mat& y) { return {(x.a * y.a + x.b * y.c) % MOD, (x.a * y.b + x.b * y.d) % MOD, (x.c * y.a + x.d * y.c) % MOD, (x.c * y.b + x.d * y.d) % MOD}; }
template <class T, class Op> T naiveFold(const std::vector<T>& v, int l, int r, Op op) { T res = v[l]; for (int i = l + 1; i <= r; ++i) res = op(res, v[i]); return res; }

int main() {
    std::mt19937 rng(13);
    {   const std::vector<long long> v = {3, 1, 4, 1, 5, 9, 2, 6};                                // 손으로 확인: 합 (겹쳐 덮으면 틀리는 연산)
        DisjointSparseTable<long long, std::plus<long long>> t(v, std::plus<long long>());
        assert(t.query(0, 7) == 31 && t.query(2, 5) == 19 && t.query(3, 4) == 6 && t.query(5, 5) == 9 && t.LOG == 3); }
    for (int n : {1, 2, 3, 5, 8, 17, 40}) {
        std::vector<long long> v(n); for (auto& x : v) x = (long long)(rng() % 100) - 50;
        auto mn = [](long long x, long long y) { return std::min(x, y); }; auto sum = [](long long x, long long y) { return x + y; };
        DisjointSparseTable<long long, decltype(mn)> tm(v, mn); DisjointSparseTable<long long, decltype(sum)> ts(v, sum);
        std::vector<Mat> m(n); for (auto& x : m) x = {(long long)(rng() % 10), (long long)(rng() % 10), (long long)(rng() % 10), (long long)(rng() % 10)};
        DisjointSparseTable<Mat, Mat (*)(const Mat&, const Mat&)> tx(m, matMul);
        std::vector<std::string> st(n); for (auto& x : st) x = std::string(1, (char)('a' + rng() % 26));
        auto cat = [](const std::string& x, const std::string& y) { return x + y; }; DisjointSparseTable<std::string, decltype(cat)> tc(st, cat);
        for (int l = 0; l < n; ++l) for (int r = l; r < n; ++r) {                                  // 모든 구간
            assert(tm.query(l, r) == naiveFold(v, l, r, mn) && ts.query(l, r) == naiveFold(v, l, r, sum));
            assert(tx.query(l, r) == naiveFold(m, l, r, matMul));                                  // 행렬곱: 교환법칙 없음 -> 순서가 틀리면 바로 걸린다
            assert(tc.query(l, r) == naiveFold(st, l, r, cat));                                    // 문자열: 이어 붙이는 순서
        }
    }
    const int n = 5000; std::vector<Mat> m(n); for (auto& x : m) x = {(long long)(rng() % 1000), (long long)(rng() % 1000), (long long)(rng() % 1000), (long long)(rng() % 1000)};
    DisjointSparseTable<Mat, Mat (*)(const Mat&, const Mat&)> big(m, matMul);
    for (int q = 0; q < 3000; ++q) { int l = (int)(rng() % n), r = (int)(rng() % n); if (l > r) std::swap(l, r); assert(big.query(l, r) == naiveFold(m, l, r, matMul)); }
    assert(big.LOG == 13 && big.tb.size() == 14);                                                  // 5000 -> 8192 = 2^13 : 수준 13 개
    std::cout << "DisjointSparseTable: O(1) queries equalled the naive fold for sum, min, 2x2 matrix product mod p and string concatenation (all ranges for n<=40, 3000 random ranges for n=5000); " << big.LOG << " levels x " << (1 << big.LOG) << " cells" << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(N log N), 질의 O(1) (연산 ⊕ 두 번)
// Space Complexity: O(N log N)
```

## SqrtTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 제곱근 트리(Sqrt Tree): 결합법칙만 있는 연산(합·곱·행렬곱·문자열 이어 붙이기)의 구간 질의를 전처리 O(N log log N), 질의 O(1) 에 답한다. 저장 칸 수가 분리 희소 표의 N log N 보다 적은 N log log N 이다(상수가 커서 N 이 작을 때는 차이가 크지 않고, N 이 커질수록 벌어진다).
// 구조: 길이 2^L 의 구간을 크기 2^b (b = ceil(L/2)) 의 블록 2^(L-b) 개로 나누고, 이 "층" 에 대해 ① 블록 안 접두 pre[i] ② 블록 안 접미 suf[i] ③ 블록 i..j 전체의 값 between[i][j] (블록 수의 제곱 ≈ 구간 길이) 를 저장한다.
// 그 다음 길이 2^b 인 블록 각각에 같은 방식을 되풀이하므로 층의 크기가 2^L → 2^(L/2) → ... 로 줄어 층 수가 log log N. 질의 [l, r]: l 과 r 이 처음 갈라지는 비트 d = (가장 높은 1 비트 of l xor r) 로 어느 층인지
// 곧바로 알 수 있다(층 (L, b) 는 b <= d < L 을 맡는다). 같은 블록이 아니므로 답 = suf[l] ⊕ between[bl+1][br-1] ⊕ pre[r] (사이 블록이 없으면 생략).
// 검증: ① 손으로 확인한 합 ② 교환법칙 없는 2x2 행렬곱 mod p·문자열 이어 붙이기, min — 길이 1..70 은 모든 구간, 큰 길이는 무작위 구간을 순진한 접기와 비교 ③ 층 수 = ceil(log2 log2 N)+1 이하이고 저장 칸 수 ≈ 층 수 x 3N 으로 N log N 이 아님
template <class T, class Op> struct SqrtTree {
    struct Layer { int L, b, nb; std::vector<T> pre, suf, between; };                              // between: 구간(2^L)마다 nb x nb 표를 이어 붙인 것
    int n, LOG; std::vector<T> a; std::vector<Layer> layers; std::vector<int> layerOfBit; Op op;
    SqrtTree(const std::vector<T>& v, Op o) : n((int)v.size()), LOG(0), a(v), op(o) {
        while ((1 << LOG) < n) ++LOG;
        const int N = 1 << LOG; a.resize(N, v.empty() ? T() : v.back()); layerOfBit.assign(LOG + 1, -1);
        for (int L = LOG; L > 1; L = (L + 1) / 2) {
            Layer ly; ly.L = L; ly.b = (L + 1) / 2; ly.nb = 1 << (L - ly.b); const int B = 1 << ly.b, S = 1 << L, segs = N >> L;
            ly.pre.resize(N); ly.suf.resize(N); ly.between.resize((size_t)segs * ly.nb * ly.nb);
            for (int s = 0; s < segs; ++s) {
                std::vector<T> total(ly.nb);
                for (int k = 0; k < ly.nb; ++k) {
                    const int lo = s * S + k * B, hi = lo + B;
                    ly.pre[lo] = a[lo]; for (int i = lo + 1; i < hi; ++i) ly.pre[i] = op(ly.pre[i - 1], a[i]);
                    ly.suf[hi - 1] = a[hi - 1]; for (int i = hi - 2; i >= lo; --i) ly.suf[i] = op(a[i], ly.suf[i + 1]);
                    total[k] = ly.pre[hi - 1];
                }
                T* tab = &ly.between[(size_t)s * ly.nb * ly.nb];
                for (int i = 0; i < ly.nb; ++i) { tab[i * ly.nb + i] = total[i]; for (int j = i + 1; j < ly.nb; ++j) tab[i * ly.nb + j] = op(tab[i * ly.nb + j - 1], total[j]); }
            }
            for (int d = ly.b; d < L; ++d) layerOfBit[d] = (int)layers.size();
            layers.push_back(std::move(ly));
        }
    }
    T query(int l, int r) const {                                                                 // 0 <= l <= r < n, 양 끝 포함
        if (l == r) return a[l];
        const int d = 31 - __builtin_clz((unsigned)(l ^ r));                                      // 처음 갈라지는 비트
        if (d == 0) return op(a[l], a[r]);                                                        // 짝을 이룬 이웃 두 칸
        const Layer& ly = layers[layerOfBit[d]]; const int bl = (l >> ly.b) & (ly.nb - 1), br = (r >> ly.b) & (ly.nb - 1);
        T res = ly.suf[l];
        if (br - bl > 1) res = op(res, ly.between[(size_t)(l >> ly.L) * ly.nb * ly.nb + (bl + 1) * ly.nb + (br - 1)]);
        return op(res, ly.pre[r]);
    }
    size_t cells() const { size_t c = 0; for (const Layer& ly : layers) c += ly.pre.size() + ly.suf.size() + ly.between.size(); return c; }
};
struct Mat { long long a, b, c, d; bool operator==(const Mat& o) const { return a == o.a && b == o.b && c == o.c && d == o.d; } };
const long long MOD = 1000000007LL;
Mat matMul(const Mat& x, const Mat& y) { return {(x.a * y.a + x.b * y.c) % MOD, (x.a * y.b + x.b * y.d) % MOD, (x.c * y.a + x.d * y.c) % MOD, (x.c * y.b + x.d * y.d) % MOD}; }
template <class T, class Op> T naiveFold(const std::vector<T>& v, int l, int r, Op op) { T res = v[l]; for (int i = l + 1; i <= r; ++i) res = op(res, v[i]); return res; }
typedef Mat (*MatOp)(const Mat&, const Mat&);

int main() {
    std::mt19937 rng(17);
    {   const std::vector<long long> v = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3};          // 손으로 확인: N=16, L=4 → 층 (4,2)와 (2,1), 합
        SqrtTree<long long, std::plus<long long>> t(v, std::plus<long long>());
        assert(t.layers.size() == 2 && t.layers[0].L == 4 && t.layers[0].b == 2 && t.layers[1].L == 2 && t.layers[1].b == 1);
        assert(t.query(0, 15) == 80);
        long long s = 0; for (int i = 2; i <= 12; ++i) s += v[i]; assert(t.query(2, 12) == s && t.query(5, 5) == 9 && t.query(6, 7) == 8 && t.query(3, 8) == 1 + 5 + 9 + 2 + 6 + 5); }
    for (int n : {1, 2, 3, 4, 5, 8, 9, 16, 17, 33, 70}) {
        std::vector<long long> v(n); for (auto& x : v) x = (long long)(rng() % 100) - 50;
        auto mn = [](long long x, long long y) { return std::min(x, y); };
        SqrtTree<long long, decltype(mn)> tm(v, mn);
        std::vector<Mat> m(n); for (auto& x : m) x = {(long long)(rng() % 10), (long long)(rng() % 10), (long long)(rng() % 10), (long long)(rng() % 10)};
        SqrtTree<Mat, MatOp> tx(m, matMul);
        std::vector<std::string> st(n); for (auto& x : st) x = std::string(1, (char)('a' + rng() % 26));
        auto cat = [](const std::string& x, const std::string& y) { return x + y; }; SqrtTree<std::string, decltype(cat)> tc(st, cat);
        for (int l = 0; l < n; ++l) for (int r = l; r < n; ++r) {
            assert(tm.query(l, r) == naiveFold(v, l, r, mn) && tx.query(l, r) == naiveFold(m, l, r, matMul) && tc.query(l, r) == naiveFold(st, l, r, cat));
        }
    }
    for (int n : {1000, 4096, 5000, 65536}) {
        std::vector<Mat> m(n); for (auto& x : m) x = {(long long)(rng() % 1000), (long long)(rng() % 1000), (long long)(rng() % 1000), (long long)(rng() % 1000)};
        SqrtTree<Mat, MatOp> t(m, matMul);
        for (int q = 0; q < 3000; ++q) { int l = (int)(rng() % n), r = (int)(rng() % n); if (l > r) std::swap(l, r); assert(t.query(l, r) == naiveFold(m, l, r, matMul)); }
        int logn = 0; while ((1 << logn) < n) ++logn; int bound = 1; for (int x = logn; x > 2; x = (x + 1) / 2) ++bound;           // 층 수 <= 약 log2(log2 N) + 1
        assert((int)t.layers.size() <= bound + 1 && t.cells() <= (size_t)(t.layers.size() * 3 + 1) * (size_t)(1 << logn));        // 칸 수 ≈ 층 수 x 3N
    }
    SqrtTree<Mat, MatOp> big(std::vector<Mat>(1 << 16, Mat{1, 1, 0, 1}), matMul);
    std::cout << "SqrtTree: O(1) queries matched the naive fold for min, 2x2 matrix product mod p (non-commutative) and string concatenation (all ranges for n<=70, 12000 random ranges up to n=65536); N=65536 uses " << big.layers.size() << " layers and " << big.cells() << " cells (a disjoint sparse table would need " << 16 * 65536 << ")" << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(N log log N), 질의 O(1)
// Space Complexity: O(N log log N)
```
# Part 7. 균형 트리
## AVLTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <tuple>
#include <vector>

// AVL 트리(트리 관점의 요약, 정본은 Tree.md Part 6): 모든 노드에서 왼쪽·오른쪽 높이 차이(균형 인수)가 −1, 0, 1 이 되도록 고친다 → 높이 ≤ 1.44 log2(N+2).  정본은 삽입·삭제마다 회전했다.
//  여기서는 *join 기반* 구현(Blelloch–Ferizovic–Sun 2016)을 보인다 — 회전 대신 join(L, k, R) 하나만 구현하면 split, 합집합·교집합·차집합이 모두 *재귀 몇 줄*로 나오고, 작은 집합(m)과 큰 집합(n)의 연산이 O(m log(n/m + 1)) 이다.
//  join(L, k, R): 높이가 크게 다르면 큰 쪽의 바깥 가장자리를 따라 내려가 R(또는 L) 과 높이가 맞는 곳에 붙이고, 올라오며 AVL 불변식을 단일·이중 회전으로 복구한다.  노드는 불변(함수형) — 연산은 새 노드를 만들 뿐 입력을 바꾸지 않는다.
//  ① 전수: {0..5} 의 부분 집합 64 개의 모든 쌍(4096)에서 합집합·교집합·차집합이 std::set 연산과 같고 결과가 AVL 불변식을 지킨다  ② 무작위 집합(크기 ≤ 60 / ≤ 20 만): std::set_union 등과 대조  ③ 비용: 10^5 개 집합에 100 개 집합을 합칠 때 만든 새 노드 수 ≤ 8·m·(log2(n/m) + 1), n 이 아니다(새로 짓는 것보다 훨씬 적다)  ④ 모든 입력이 연산 뒤에도 그대로.
struct AvlSets {
    std::vector<int> key, h, sz, L, R;                                                                           // 노드 풀 (한 번 쓰면 바뀌지 않는다)
    int H(int t) const { return t < 0 ? 0 : h[t]; }
    int S(int t) const { return t < 0 ? 0 : sz[t]; }
    int mk(int l, int k, int r) { key.push_back(k); h.push_back(1 + std::max(H(l), H(r))); sz.push_back(1 + S(l) + S(r)); L.push_back(l); R.push_back(r); return (int)key.size() - 1; }
    int rotL(int t) { int r = R[t]; return mk(mk(L[t], key[t], L[r]), key[r], R[r]); }
    int rotR(int t) { int l = L[t]; return mk(L[l], key[l], mk(R[l], key[t], R[t])); }
    int joinRight(int l, int k, int r) {                                                                         // H(l) > H(r) + 1
        int c = R[l];
        if (H(c) <= H(r) + 1) { int t2 = mk(c, k, r); if (H(t2) <= H(L[l]) + 1) return mk(L[l], key[l], t2); return rotL(mk(L[l], key[l], rotR(t2))); }
        int t2 = joinRight(c, k, r); int t3 = mk(L[l], key[l], t2); if (H(t2) <= H(L[l]) + 1) return t3; return rotL(t3); }
    int joinLeft(int l, int k, int r) {                                                                          // H(r) > H(l) + 1
        int c = L[r];
        if (H(c) <= H(l) + 1) { int t2 = mk(l, k, c); if (H(t2) <= H(R[r]) + 1) return mk(t2, key[r], R[r]); return rotR(mk(rotL(t2), key[r], R[r])); }
        int t2 = joinLeft(l, k, c); int t3 = mk(t2, key[r], R[r]); if (H(t2) <= H(R[r]) + 1) return t3; return rotR(t3); }
    int join(int l, int k, int r) { if (H(l) > H(r) + 1) return joinRight(l, k, r); if (H(r) > H(l) + 1) return joinLeft(l, k, r); return mk(l, k, r); }
    std::tuple<int, bool, int> split(int t, int k) { if (t < 0) return {-1, false, -1}; if (k == key[t]) return {L[t], true, R[t]};
        if (k < key[t]) { auto s = split(L[t], k); return {std::get<0>(s), std::get<1>(s), join(std::get<2>(s), key[t], R[t])}; }
        auto s = split(R[t], k); return {join(L[t], key[t], std::get<0>(s)), std::get<1>(s), std::get<2>(s)}; }
    std::pair<int, int> splitLast(int t) { if (R[t] < 0) return {L[t], key[t]}; auto s = splitLast(R[t]); return {join(L[t], key[t], s.first), s.second}; }
    int join2(int l, int r) { if (l < 0) return r; auto s = splitLast(l); return join(s.first, s.second, r); }
    int unionOf(int a, int b) { if (a < 0) return b; if (b < 0) return a; auto s = split(b, key[a]); return join(unionOf(L[a], std::get<0>(s)), key[a], unionOf(R[a], std::get<2>(s))); }
    int intersect(int a, int b) { if (a < 0 || b < 0) return -1; auto s = split(b, key[a]); int l = intersect(L[a], std::get<0>(s)), r = intersect(R[a], std::get<2>(s)); return std::get<1>(s) ? join(l, key[a], r) : join2(l, r); }
    int difference(int a, int b) { if (a < 0) return -1; if (b < 0) return a; auto s = split(a, key[b]); return join2(difference(std::get<0>(s), L[b]), difference(std::get<2>(s), R[b])); }       // a \ b
    int insert(int t, int k) { auto s = split(t, k); return join(std::get<0>(s), k, std::get<2>(s)); }
    int erase(int t, int k) { auto s = split(t, k); return join2(std::get<0>(s), std::get<2>(s)); }
    int build(const std::vector<int>& sorted, int lo, int hi) { if (lo >= hi) return -1; int m = (lo + hi) / 2; int l = build(sorted, lo, m), r = build(sorted, m + 1, hi); return mk(l, sorted[m], r); }       // 정렬된 키 → 완전 균형 트리
    bool valid(int t, long long lo, long long hi, int& height, int& size) const {                                // BST 순서, 저장된 높이·크기, |균형 인수| ≤ 1
        if (t < 0) { height = 0; size = 0; return true; } if (!(key[t] > lo && key[t] < hi)) return false; int hl, hr, sl, sr;
        if (!valid(L[t], lo, key[t], hl, sl) || !valid(R[t], key[t], hi, hr, sr)) return false; height = 1 + std::max(hl, hr); size = 1 + sl + sr; return std::abs(hl - hr) <= 1 && h[t] == height && sz[t] == size; }
    bool ok(int t) const { int a, b; return valid(t, -(1LL << 40), 1LL << 40, a, b); }
    void toVec(int t, std::vector<int>& out) const { if (t < 0) return; toVec(L[t], out); out.push_back(key[t]); toVec(R[t], out); }
    std::vector<int> items(int t) const { std::vector<int> v; toVec(t, v); return v; }
};
std::vector<int> setOp(const std::set<int>& a, const std::set<int>& b, int op) { std::vector<int> out; if (op == 0) std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(out)); else if (op == 1) std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(out)); else std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(out)); return out; }

int main() {
    AvlSets pool; std::vector<std::set<int>> subs; std::vector<int> roots;                                         // ① 전수
    for (int mask = 0; mask < 64; ++mask) { std::set<int> s; std::vector<int> v; for (int i = 0; i < 6; ++i) if (mask >> i & 1) { s.insert(i); v.push_back(i); } subs.push_back(s); roots.push_back(pool.build(v, 0, (int)v.size())); assert(pool.ok(roots.back())); }
    for (int i = 0; i < 64; ++i) for (int j = 0; j < 64; ++j) { int ops[3] = {pool.unionOf(roots[i], roots[j]), pool.intersect(roots[i], roots[j]), pool.difference(roots[i], roots[j])};
        for (int op = 0; op < 3; ++op) { assert(pool.ok(ops[op]) && pool.items(ops[op]) == setOp(subs[i], subs[j], op)); } }
    for (int i = 0; i < 64; ++i) { assert(pool.items(roots[i]) == std::vector<int>(subs[i].begin(), subs[i].end())); }                  // ④ 입력 불변
    std::mt19937 rng(139);
    for (int it = 0; it < 400; ++it) { AvlSets p; std::set<int> a, b; int na = (int)(rng() % 61), nb = (int)(rng() % 61); for (int i = 0; i < na; ++i) a.insert((int)(rng() % 100)); for (int i = 0; i < nb; ++i) b.insert((int)(rng() % 100));
        int ra = p.build(std::vector<int>(a.begin(), a.end()), 0, (int)a.size()), rb = p.build(std::vector<int>(b.begin(), b.end()), 0, (int)b.size());
        for (int op = 0; op < 3; ++op) { int r = op == 0 ? p.unionOf(ra, rb) : op == 1 ? p.intersect(ra, rb) : p.difference(ra, rb); assert(p.ok(r) && p.items(r) == setOp(a, b, op)); }
        int rr = ra; std::set<int> ref = a; for (int k = 0; k < 40; ++k) { int x = (int)(rng() % 100); if (rng() % 2) { rr = p.insert(rr, x); ref.insert(x); } else { rr = p.erase(rr, x); ref.erase(x); } assert(p.ok(rr) && p.items(rr) == std::vector<int>(ref.begin(), ref.end())); } }          // ② 삽입·삭제도 split/join 으로
    for (int it = 0; it < 6; ++it) { AvlSets p; std::set<int> a, b; int na = 200000, nb = (it % 2) ? 200000 : 1000; for (int i = 0; i < na; ++i) a.insert((int)(rng() % 1000000)); for (int i = 0; i < nb; ++i) b.insert((int)(rng() % 1000000));
        int ra = p.build(std::vector<int>(a.begin(), a.end()), 0, (int)a.size()), rb = p.build(std::vector<int>(b.begin(), b.end()), 0, (int)b.size());
        for (int op = 0; op < 3; ++op) { int r = op == 0 ? p.unionOf(ra, rb) : op == 1 ? p.intersect(ra, rb) : p.difference(ra, rb); assert(p.ok(r) && p.items(r) == setOp(a, b, op)); } }
    { AvlSets p; std::vector<int> big(100000); for (int i = 0; i < 100000; ++i) big[i] = 10 * i; int ra = p.build(big, 0, 100000); std::vector<int> few(100); for (int i = 0; i < 100; ++i) few[i] = 10 * (i * 997 % 100000) + 5; std::sort(few.begin(), few.end()); int rb = p.build(few, 0, 100);
      size_t before = p.key.size(); int r = p.unionOf(ra, rb); size_t created = p.key.size() - before; assert(p.ok(r) && p.S(r) == 100100 && created <= 8.0 * 100 * (std::log2(100000.0 / 100) + 1));            // ③ 새 노드는 O(m log(n/m + 1))
      std::cout << "AVLTree: join-based union/intersection/difference matched std::set operations on all 4096 subset pairs of {0..5}, 400 random pairs and six pairs of up to 2*10^5 keys, every result satisfied the AVL invariants, and merging 100 keys into 10^5 created only " << created << " new nodes" << std::endl; }
    return 0;
}
// Time Complexity: join O(|높이 차|), split O(log N), 합집합·교집합·차집합 O(m log(n/m + 1))
// Space Complexity: O(N) (함수형 — 연산마다 O(log N) 새 노드)
```
## RedBlackTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 레드-블랙 트리(트리 관점의 요약, 정본은 Tree.md Part 7): 색 규칙(빨간 노드의 자식은 검정, 모든 경로의 검은 노드 수 동일)으로 높이를 2 log2(N+1) 이하로 묶는다.
//  여기서는 구현이 가장 짧은 *좌편향*(LLRB, Sedgewick) 2-3 트리 판 — 삽입뿐 아니라 *삭제*(moveRedLeft / moveRedRight 로 "내려가는 길에 빨간 링크를 미리 만들어 둔다")까지 보인다.  불변식: 루트는 검정, 오른쪽 링크는 빨강이 아니고, 빨강이 연속하지 않으며, 모든 경로의 검은 링크 수가 같다.
//  ① 전수: 키 6 개의 *모든 삽입 순서(720) × 모든 삭제 순서(720)* 에서 매 단계 뒤 불변식·std::set 내용 일치(518400 열)  ② 키 7 개의 모든 삽입 순서 + 삭제 순서 무작위 20 개  ③ 무작위 삽입·삭제 100 만 번을 std::set 과 대조(주기적 불변식·높이 ≤ 2 log2(n+1))
//  ④ 정렬 입력 10 만 개: 높이 ≤ 2 log2(n+1), 연산당 회전 수 평균 < 3, 삭제된 노드는 free-list 로 재사용.
struct LLRB {
    std::vector<int> key, L, R; std::vector<char> red; std::vector<int> freeList; int root = -1; size_t cnt = 0; long rotations = 0, flips = 0;
    int node(int k) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); key[u] = k; L[u] = R[u] = -1; red[u] = 1; } else { key.push_back(k); L.push_back(-1); R.push_back(-1); red.push_back(1); u = (int)key.size() - 1; } return u; }
    bool isRed(int h) const { return h >= 0 && red[h]; }
    int lc(int h) const { return h < 0 ? -1 : L[h]; }
    int rotL(int h) { int x = R[h]; R[h] = L[x]; L[x] = h; red[x] = red[h]; red[h] = 1; ++rotations; return x; }
    int rotR(int h) { int x = L[h]; L[h] = R[x]; R[x] = h; red[x] = red[h]; red[h] = 1; ++rotations; return x; }
    void flip(int h) { red[h] ^= 1; red[L[h]] ^= 1; red[R[h]] ^= 1; ++flips; }
    int fixUp(int h) { if (isRed(R[h]) && !isRed(L[h])) h = rotL(h); if (isRed(L[h]) && isRed(lc(L[h]))) h = rotR(h); if (isRed(L[h]) && isRed(R[h])) flip(h); return h; }
    int ins(int h, int k, bool& added) { if (h < 0) { added = true; return node(k); } if (k < key[h]) { int c = ins(L[h], k, added); L[h] = c; } else if (k > key[h]) { int c = ins(R[h], k, added); R[h] = c; } else return h; return fixUp(h); }
    bool insert(int k) { bool added = false; root = ins(root, k, added); red[root] = 0; if (added) ++cnt; return added; }
    bool contains(int k) const { int h = root; while (h >= 0 && key[h] != k) h = k < key[h] ? L[h] : R[h]; return h >= 0; }
    int moveRedLeft(int h) { flip(h); if (isRed(lc(R[h]))) { int c = rotR(R[h]); R[h] = c; h = rotL(h); flip(h); } return h; }
    int moveRedRight(int h) { flip(h); if (isRed(lc(L[h]))) { h = rotR(h); flip(h); } return h; }
    int deleteMin(int h, int& removed) { if (L[h] < 0) { removed = h; return -1; } if (!isRed(L[h]) && !isRed(lc(L[h]))) h = moveRedLeft(h); int c = deleteMin(L[h], removed); L[h] = c; return fixUp(h); }
    int del(int h, int k) {
        if (k < key[h]) { if (!isRed(L[h]) && !isRed(lc(L[h]))) h = moveRedLeft(h); int c = del(L[h], k); L[h] = c; }
        else { if (isRed(L[h])) h = rotR(h); if (k == key[h] && R[h] < 0) { freeList.push_back(h); return -1; }
            if (!isRed(R[h]) && !isRed(lc(R[h]))) h = moveRedRight(h);
            if (k == key[h]) { int m = -1; int nr = deleteMin(R[h], m); key[h] = key[m]; freeList.push_back(m); R[h] = nr; } else { int c = del(R[h], k); R[h] = c; } }
        return fixUp(h); }
    bool erase(int k) { if (!contains(k)) return false; if (!isRed(L[root]) && !isRed(R[root])) red[root] = 1; root = del(root, k); if (root >= 0) red[root] = 0; --cnt; return true; }
    int check(int h, long long lo, long long hi, size_t& seen) const {                                           // 검정 높이(−1 이면 위반)
        if (h < 0) return 1; if (!(key[h] > lo && key[h] < hi)) return -1; ++seen;
        if (isRed(R[h]) || (isRed(h) && isRed(L[h]))) return -1;                                                  // 왼쪽 기울기·연속 빨강 금지
        int a = check(L[h], lo, key[h], seen), b = check(R[h], key[h], hi, seen); if (a < 0 || b < 0 || a != b) return -1; return a + (red[h] ? 0 : 1); }
    bool valid() const { if (root < 0) return cnt == 0; size_t seen = 0; return !isRed(root) && check(root, -(1LL << 40), 1LL << 40, seen) > 0 && seen == cnt; }
    int height(int h) const { return h < 0 ? 0 : 1 + std::max(height(L[h]), height(R[h])); }
    void inorder(int h, std::vector<int>& out) const { if (h < 0) return; inorder(L[h], out); out.push_back(key[h]); inorder(R[h], out); }
    std::vector<int> items() const { std::vector<int> v; inorder(root, v); return v; }
};

int main() {
    { const int n = 6; std::vector<int> ins(n), del(n); std::iota(ins.begin(), ins.end(), 0); long seqs = 0;                                          // ① 6! × 6!
      do { std::iota(del.begin(), del.end(), 0);
           do { LLRB t; std::set<int> ref; for (int k : ins) { t.insert(k); ref.insert(k); } assert(t.valid());
                for (int k : del) { bool a = t.erase(k); bool r = ref.erase(k) > 0; assert(a && r); assert(t.valid() && t.items() == std::vector<int>(ref.begin(), ref.end())); } assert(t.root < 0); ++seqs;
           } while (std::next_permutation(del.begin(), del.end()));
      } while (std::next_permutation(ins.begin(), ins.end())); assert(seqs == 518400); }
    std::mt19937 rng(141);
    { std::vector<int> ins(7); std::iota(ins.begin(), ins.end(), 0);                                                                                // ②
      do { for (int rep = 0; rep < 20; ++rep) { std::vector<int> del = ins; std::shuffle(del.begin(), del.end(), rng); LLRB t; std::set<int> ref; for (int k : ins) { t.insert(k); ref.insert(k); } assert(t.valid());
            for (int k : del) { assert(t.erase(k)); ref.erase(k); assert(t.valid() && t.items() == std::vector<int>(ref.begin(), ref.end())); } } } while (std::next_permutation(ins.begin(), ins.end())); }
    { LLRB t; std::set<int> ref; for (long step = 0; step < 1000000; ++step) { int k = (int)(rng() % 50000); if (rng() % 100 < 52) { bool a = t.insert(k); bool r = ref.insert(k).second; assert(a == r); } else { bool a = t.erase(k); bool r = ref.erase(k) > 0; assert(a == r); }
        assert(t.cnt == ref.size()); if (step % 4001 == 0) { assert(t.valid() && t.height(t.root) <= 2 * std::log2((double)t.cnt + 1) + 1e-9); } }
      assert(t.valid() && t.items() == std::vector<int>(ref.begin(), ref.end())); }                                                                   // ③
    { LLRB t; const int n = 100000; for (int i = 1; i <= n; ++i) t.insert(i); assert(t.valid() && t.height(t.root) <= 2 * std::log2((double)n + 1) && (double)t.rotations / n < 3.0);
      for (int i = 1; i <= n; i += 2) assert(t.erase(i)); assert(t.valid() && t.cnt == n / 2 && t.key.size() == (size_t)n); size_t arena = t.key.size(); for (int i = 1; i <= n; i += 2) t.insert(i); assert(t.valid() && t.key.size() == arena);    // ④ 노드 재사용
      std::cout << "RedBlackTree: left-leaning red-black insert and delete kept all invariants for all 518400 (insert order, delete order) pairs of 6 keys and for 7-key insert orders, matched std::set over 10^6 random operations, and 10^5 sorted inserts gave height " << t.height(t.root) << " with " << (double)t.rotations / (2 * n) << " rotations per operation" << std::endl; }
    return 0;
}
// Time Complexity: 삽입·삭제·조회 O(log N)
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
void destroy(T* t) { if (!t) return; destroy(t->l); destroy(t->r); delete t; }
int main() {
    std::mt19937 g(1); T* root = nullptr;
    for (int i = 1; i <= 4095; i++) { T* a; T* b; split(root, i, a, b); root = merge(merge(a, new T{i, (int)g()}), b); }
    assert(ht(root) < 40); std::cout << "Treap: height " << ht(root) << " for 4095 sorted inserts" << std::endl; destroy(root); return 0;
}
// Time Complexity: 삽입·삭제·탐색 기대 O(log N)
// Space Complexity: O(N)
```
## SplayTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 스플레이 트리(트리 관점의 요약, 정본은 Tree.md Part 13): 접근한 노드를 회전으로 루트까지 끌어올린다(zig-zig / zig-zag). 균형 정보를 저장하지 않고도 분할상환 O(log N),
//  최근에 쓴 키가 다시 빨리 나오는 접근 패턴에 강하다 (정적 최적성, 순차 접근 O(N) 등).  여기서는 재귀 없이 *위에서 아래로* 한 번에 끝내는 top-down 스플레이(Sleator–Tarjan)를 보인다 —
//  내려가면서 경로를 "왼쪽 트리(작은 키)"와 "오른쪽 트리(큰 키)"에 떼어 붙이고 마지막에 조립한다.  깊이가 10^5 인 사슬에도 안전하다.
//  ① 전수: 키 7 개의 모든 삽입 순서(5040) 뒤 각 키를 접근하면 그 키가 루트가 되고 BST 가 유지됨, 모든 삭제 순서 일부  ② 무작위 삽입·삭제·조회 100 만 번을 std::set 과 대조
//  ③ *순차 접근 정리*: 무작위 순서로 만든 n = 10^5 트리(와 정렬 입력으로 생긴 사슬)를 키 순서대로 한 번 훑는 총 비용 ≤ 4n 스플레이 단계(zig-zig·zig-zag 한 쌍이 한 단계)이고 실제로 내려간 링크 수로 세면 ≤ 8n — 왼쪽으로 기운 사슬과 오른쪽으로 기운 사슬(내림차순 삽입 + 내림차순 훑기) 모두에서  ④ *작업 집합 성질*: 64 개 핫키를 반복 접근하면 접근당 비용이 O(log 64) 로 작아진다 — 10^5 개 트리 안인데도 평균 < 10 링크 (균형 트리는 17 근처; 링크는 단계 수와 달리 zig-zig 를 둘로 센 실제 내려간 간선 수).
struct Splay {
    std::vector<int> key, L, R; std::vector<int> freeList; int root = -1; size_t cnt = 0; long steps = 0, links = 0;     // 인덱스 0 은 조립용 머리 노드.  steps = 스플레이 단계 수(반복 한 번; zig-zig·zig-zag 는 링크 2 개를 내려가도 한 단계), links = 실제로 내려간 링크 수
    Splay() { key.push_back(0); L.push_back(-1); R.push_back(-1); }
    int node(int k) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); key[u] = k; L[u] = R[u] = -1; } else { key.push_back(k); L.push_back(-1); R.push_back(-1); u = (int)key.size() - 1; } return u; }
    void splay(int k) {                                                                                           // k 가 있으면 루트로, 없으면 탐색 경로의 마지막 노드를 루트로
        if (root < 0) return; int H = 0, lt = H, rt = H, t = root; L[H] = R[H] = -1;
        for (;;) { ++steps;
            if (k < key[t]) { if (L[t] < 0) break; if (k < key[L[t]]) { int y = L[t]; L[t] = R[y]; R[y] = t; t = y; ++links; if (L[t] < 0) break; } L[rt] = t; rt = t; t = L[t]; ++links; }              // zig-zig 후 오른쪽 트리에 붙임
            else if (k > key[t]) { if (R[t] < 0) break; if (k > key[R[t]]) { int y = R[t]; R[t] = L[y]; L[y] = t; t = y; ++links; if (R[t] < 0) break; } R[lt] = t; lt = t; t = R[t]; ++links; }            // 왼쪽 트리에 붙임
            else break; }
        R[lt] = L[t]; L[rt] = R[t]; L[t] = R[H]; R[t] = L[H]; root = t; }                                          // 조립
    bool contains(int k) { if (root < 0) return false; splay(k); return key[root] == k; }
    bool insert(int k) { if (root < 0) { root = node(k); ++cnt; return true; } splay(k); if (key[root] == k) return false; int n = node(k);
        if (k < key[root]) { L[n] = L[root]; R[n] = root; L[root] = -1; } else { R[n] = R[root]; L[n] = root; R[root] = -1; } root = n; ++cnt; return true; }
    bool erase(int k) { if (root < 0) return false; splay(k); if (key[root] != k) return false; int dead = root;
        if (L[root] < 0) root = R[root]; else { int r = R[root]; root = L[root]; splay(k); R[root] = r; }              // 왼쪽 트리의 최댓값을 루트로 올리고(k 보다 크므로 오른쪽 끝) 오른쪽을 붙인다
        freeList.push_back(dead); --cnt; return true; }
    bool valid() const { std::vector<int> st; std::vector<int> out; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(key[u]); u = R[u]; } return out.size() == cnt && std::is_sorted(out.begin(), out.end()) && std::adjacent_find(out.begin(), out.end()) == out.end(); }
    int depthOf(int k) const { int d = 0, u = root; while (u >= 0 && key[u] != k) { u = k < key[u] ? L[u] : R[u]; ++d; } return u >= 0 ? d : -1; }
};

int main() {
    std::mt19937 rng(143);
    { std::vector<int> ins(7); std::iota(ins.begin(), ins.end(), 0);                                                // ①
      do { Splay t; for (int k : ins) t.insert(k); assert(t.valid());
           for (int k = 0; k < 7; ++k) { assert(t.contains(k) && t.key[t.root] == k && t.valid()); } assert(!t.contains(99) && t.valid());
           std::vector<int> del = ins; std::shuffle(del.begin(), del.end(), rng); std::set<int> ref(ins.begin(), ins.end()); for (int k : del) { assert(t.erase(k)); ref.erase(k); assert(t.valid() && t.cnt == ref.size()); } assert(t.root < 0);
      } while (std::next_permutation(ins.begin(), ins.end())); }
    { Splay t; std::set<int> ref; for (long step = 0; step < 1000000; ++step) { int k = (int)(rng() % 40000); int op = (int)(rng() % 3);
        if (op == 0) { bool a = t.insert(k); bool r = ref.insert(k).second; assert(a == r); } else if (op == 1) { bool a = t.erase(k); bool r = ref.erase(k) > 0; assert(a == r); } else { bool a = t.contains(k); assert(a == (ref.count(k) > 0)); }
        assert(t.cnt == ref.size()); if (step % 9973 == 0) assert(t.valid()); } assert(t.valid()); }                    // ②
    { const int n = 100000; std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); Splay t; for (int k : keys) t.insert(k);
      t.steps = t.links = 0; for (int k = 0; k < n; ++k) assert(t.contains(k)); long scanSteps = t.steps, scanLinks = t.links; assert(scanSteps <= 4L * n && scanLinks <= 8L * n);                         // ③ 순차 접근 정리
      Splay chain; for (int k = 0; k < n; ++k) chain.insert(k); assert(chain.valid() && chain.depthOf(0) >= n / 2);       // 정렬 입력이면 사슬(깊이 ~ n) — top-down 이라 재귀 없이 안전
      chain.steps = chain.links = 0; for (int k = 0; k < n; ++k) assert(chain.contains(k)); long chainSteps = chain.steps, chainLinks = chain.links; assert(chainSteps <= 4L * n && chainLinks <= 8L * n);      // 왼쪽으로 기운 사슬 (왼쪽 zig-zig)
      Splay mirror; for (int k = n - 1; k >= 0; --k) mirror.insert(k); assert(mirror.valid() && mirror.depthOf(n - 1) >= n / 2);                    // 내림차순 삽입 -> 오른쪽으로 기운 사슬
      mirror.steps = mirror.links = 0; for (int k = n - 1; k >= 0; --k) assert(mirror.contains(k)); long mirrorSteps = mirror.steps, mirrorLinks = mirror.links; assert(mirrorSteps <= 4L * n && mirrorLinks <= 8L * n);   // 거울 대칭 (오른쪽 zig-zig)
      int hot[64]; for (int& h : hot) h = keys[rng() % n]; for (int rep = 0; rep < 100; ++rep) for (int h : hot) t.contains(h);                                      // 워밍업
      t.links = 0; const int reps = 2000; for (int rep = 0; rep < reps; ++rep) for (int h : hot) assert(t.contains(h)); double avg = (double)t.links / (reps * 64.0); assert(avg < 10.0);   // ④ 작업 집합
      std::cout << "SplayTree: top-down splaying matched std::set over 10^6 operations and every 7-key insertion order; scanning all 10^5 keys in ascending order cost " << (double)scanSteps / n << " splay steps (" << (double)scanLinks / n << " links) per key on a random tree, " << (double)chainSteps / n << " (" << (double)chainLinks / n << ") on a left-leaning chain and " << (double)mirrorSteps / n << " (" << (double)mirrorLinks / n << ") on its mirror image (sequential access theorem: O(1) each), and 64 hot keys cost " << avg << " links per access" << std::endl; }
    return 0;
}
// Time Complexity: 분할상환 O(log N), 작업 집합 크기 w 에서 O(log w)
// Space Complexity: O(N)
```
## ScapegoatTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 스케이프고트 트리(트리 관점의 요약, 정본은 Tree.md Part 13): 회전 없이, 삽입한 노드가 너무 깊이 들어갔을 때 경로를 거슬러 올라가며 "한쪽 부분 트리가 전체의 α 비율을 넘는" 첫 조상(희생양)을 찾아 그 부분 트리를 통째로 완전 균형으로 다시 짓는다.
//  높이 ≤ log_{1/α}(N) + 1 이 유지되고 삭제는 n < α·(최대 크기) 가 되면 *전체*를 다시 짓는다 — 모두 분할상환 O(log N).  노드는 부분 트리 크기를 저장해 희생양 판정이 O(1) 이다.
//  ① 키 7 개의 모든 삽입·삭제 순서에서 불변식(BST, 크기, 높이 한계)  ② 무작위 삽입·삭제 30 만 번 std::set 대조 + 높이 상한 매 100 번 검증  ③ 정렬된 입력 10 만 개: 일반 BST 라면 높이 10 만이지만 ≤ log_{1/α}(n) + 1  ④ 재구성 비용: 총 재구성 노드 수 / 연산 수가 상수·log 규모(< 30)  ⑤ 모든 삭제 뒤 노드를 free-list 로 재사용.
struct Scapegoat {
    static constexpr double ALPHA = 0.7;
    std::vector<int> key, L, R, sz; std::vector<int> freeList; int root = -1; size_t n = 0, maxN = 0; long rebuildWork = 0, rebuilds = 0;
    int node(int k) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); key[u] = k; L[u] = R[u] = -1; sz[u] = 1; } else { key.push_back(k); L.push_back(-1); R.push_back(-1); sz.push_back(1); u = (int)key.size() - 1; } return u; }
    int S(int t) const { return t < 0 ? 0 : sz[t]; }
    void flatten(int t, std::vector<int>& out) const { std::vector<int> st; int u = t; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(u); u = R[u]; } }
    int build(const std::vector<int>& v, int lo, int hi) { if (lo >= hi) return -1; int m = (lo + hi) / 2, u = v[m]; int l = build(v, lo, m), r = build(v, m + 1, hi); L[u] = l; R[u] = r; sz[u] = 1 + S(l) + S(r); return u; }
    int rebuild(int t) { std::vector<int> v; flatten(t, v); ++rebuilds; rebuildWork += (long)v.size(); return build(v, 0, (int)v.size()); }
    int heightLimit() const { return (int)std::floor(std::log((double)std::max<size_t>(n, 1)) / std::log(1.0 / ALPHA)); }
    bool contains(int k) const { int t = root; while (t >= 0 && key[t] != k) t = k < key[t] ? L[t] : R[t]; return t >= 0; }
    bool insert(int k) {
        if (contains(k)) return false; std::vector<int> path; int t = root; while (t >= 0) { path.push_back(t); t = k < key[t] ? L[t] : R[t]; }
        int u = node(k); if (path.empty()) root = u; else if (k < key[path.back()]) L[path.back()] = u; else R[path.back()] = u; for (int a : path) ++sz[a]; ++n; maxN = std::max(maxN, n);
        if ((int)path.size() > heightLimit()) {                                                                  // 너무 깊다: 새 노드에서 올라가며 희생양을 찾는다
            int child = u; for (int i = (int)path.size() - 1; i >= 0; --i) { int p = path[i];
                if ((double)sz[child] > ALPHA * (double)sz[p]) { int sub = rebuild(p); if (i == 0) root = sub; else if (L[path[i - 1]] == p) L[path[i - 1]] = sub; else R[path[i - 1]] = sub; break; }
                child = p; } }
        return true; }
    bool erase(int k) {
        std::vector<int> path; int t = root; while (t >= 0 && key[t] != k) { path.push_back(t); t = k < key[t] ? L[t] : R[t]; } if (t < 0) return false;
        if (L[t] >= 0 && R[t] >= 0) { path.push_back(t); int s = R[t]; while (L[s] >= 0) { path.push_back(s); s = L[s]; } key[t] = key[s]; t = s; }
        int child = L[t] >= 0 ? L[t] : R[t]; if (path.empty()) root = child; else if (L[path.back()] == t) L[path.back()] = child; else R[path.back()] = child;
        for (int a : path) --sz[a]; freeList.push_back(t); --n;
        if ((double)n < ALPHA * (double)maxN && root >= 0) { root = rebuild(root); maxN = n; }                    // 너무 많이 지웠다: 전체 재구성
        return true; }
    int height() const { int best = 0; std::vector<std::pair<int, int>> st; if (root >= 0) st.push_back({root, 1}); while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return best; }
    bool valid() const { std::vector<int> v; flatten(root, v); if (v.size() != n) return false; for (size_t i = 1; i < v.size(); ++i) if (key[v[i - 1]] >= key[v[i]]) return false;
        std::vector<int> order = {root}; if (root < 0) return n == 0; for (size_t i = 0; i < order.size(); ++i) { int u = order[i]; if (L[u] >= 0) order.push_back(L[u]); if (R[u] >= 0) order.push_back(R[u]); }
        std::vector<int> want(key.size(), 0); for (size_t i = order.size(); i-- > 0;) { int u = order[i]; want[u] = 1 + (L[u] >= 0 ? want[L[u]] : 0) + (R[u] >= 0 ? want[R[u]] : 0); if (want[u] != sz[u]) return false; } return true; }
    bool heightOk() const { double lim = std::log((double)std::max<size_t>(std::max(n, maxN), 2)) / std::log(1.0 / ALPHA) + 2; return height() <= lim; }
};

int main() {
    std::mt19937 rng(147);
    { std::vector<int> ins(7); std::iota(ins.begin(), ins.end(), 0);
      do { Scapegoat t; for (int k : ins) { assert(t.insert(k)); assert(t.valid() && t.heightOk()); } std::vector<int> del = ins; std::shuffle(del.begin(), del.end(), rng); for (int k : del) { assert(t.erase(k)); assert(t.valid() && t.heightOk()); } assert(t.n == 0 && t.root < 0);
      } while (std::next_permutation(ins.begin(), ins.end())); }                                                  // ①
    { Scapegoat t; std::set<int> ref; for (long step = 0; step < 300000; ++step) { int k = (int)(rng() % 30000); bool ins = rng() % 100 < 55;
        if (ins) { bool a = t.insert(k); bool r = ref.insert(k).second; assert(a == r); } else { bool a = t.erase(k); bool r = ref.erase(k) > 0; assert(a == r); } assert(t.n == ref.size());
        if (step % 100 == 0) assert(t.heightOk()); if (step % 5003 == 0) assert(t.valid()); } assert(t.valid() && t.heightOk()); }                  // ②
    { Scapegoat t; const int N = 100000; for (int k = 1; k <= N; ++k) t.insert(k); assert(t.valid() && t.height() <= std::log((double)N) / std::log(1 / Scapegoat::ALPHA) + 2); int h = t.height();                    // ③
      double perOp = (double)t.rebuildWork / N; assert(perOp < 30.0);                                             // ④ 재구성 비용: 삽입당 O(log N) 분할상환
      size_t arena = t.key.size(); for (int k = 1; k <= N; k += 2) assert(t.erase(k)); for (int k = 1; k <= N; k += 2) t.insert(k); assert(t.key.size() <= arena + 8 && t.valid());                                            // ⑤ 노드 재사용 (재구성이 끼어도 크기는 유지)
      std::cout << "ScapegoatTree: invariants held for every 7-key insertion/deletion order, 3*10^5 random operations matched std::set with the height bound checked every 100 operations, and 10^5 sorted inserts gave height " << h << " (plain BST: 100000) with " << perOp << " nodes rebuilt per insert" << std::endl; }
    return 0;
}
// Time Complexity: 삽입·삭제 분할상환 O(log N), 검색 O(log N)
// Space Complexity: O(N) (노드마다 부분 트리 크기)
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
// 선호 자식이 왼쪽<->오른쪽으로 *교대한* 횟수 flips 는 Wilber 의 interleave 하한과 정확히 같다 — 아래 main 이 독립적으로 계산한 interleave 값과 대조해 확인한다.
// 그러나 실제 일(join·cut 횟수)은 flips 와 같지 않다: 선호 자식이 처음 정해질 때, 그리고 노드 자신이 접근되어 선호가 지워진 뒤 다시 정해질 때도 join 이 일어난다.  main 이 joins <= flips + N + 접근 수, cuts <= joins + 접근 수 를 단언한다.
// 보조 트리는 키 순서 BST 이기만 하면 되므로 여기서는 트립(무작위 우선순위)으로 구현했다 -> 보조 트리 연산은 크기 <= H 에서 *기대* O(log H) = O(log log N) 이고 최악이 아니다 (논문은 균형 트리로 최악 보장).
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
        assert(t.verify() && t.flips == interleave(s));                    // 선호 자식의 좌우 교대 횟수 == interleave 하한
        assert(t.joins <= t.flips + N + (long)s.size() && t.cuts <= t.joins + (long)s.size() && t.joins >= t.flips);        // 처음 지정 (노드당 한 번) + 자기 접근 뒤 재지정 (접근당 한 번)을 합쳐도 이 이상은 없다
        std::cout << "sequence of " << s.size() << " accesses: preferred-child flips " << t.flips << ", cuts " << t.cuts << ", joins " << t.joins << std::endl;
    }
    Tango seq; for (int r = 0; r < 1; r++) for (int i = 1; i <= N; i++) seq.access(i);
    assert(seq.flips <= N);                                                // 순차 접근: 한 바퀴에 노드당 교대 한 번 이하 -> 총 O(N)
    std::cout << "TangoTree: flips == interleave bound on 3 access patterns; sequential pass flips " << seq.flips << " for N=" << N << std::endl;
    return 0;
}
// Time Complexity: 접근열 X 에 대해 기대 O((k + 1)(1 + log log N)) (k = 선호 자식이 바뀐(join 한) 횟수 <= interleave 하한 + N + |X|; 보조 트리가 트립이므로 log log N 은 기대값)
// Space Complexity: O(N)
```

# Part 8. 외부 메모리
## BTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// B-트리(트리 관점의 요약, 정본은 Tree.md Part 13): 한 노드에 키 여러 개를 담아 디스크 블록 한 개 = 노드 한 개가 되게 한 균형 탐색 트리. 최소 차수 t 이면 루트를 뺀 모든 노드가 키를 t−1 ~ 2t−1 개 갖고 모든 잎의 깊이가 같다.
//  삽입은 내려가는 길에 가득 찬 노드를 미리 쪼개고(가운데 키가 부모로), 삭제(CLRS)는 내려가는 길에 최소치(t−1)인 자식을 미리 채운다 — 형제에게 빌리거나(회전), 형제와 부모의 구분 키를 합친다.  루트가 비면 높이가 1 줄어든다.
//  ① 전수: t = 2 (2-3-4 트리) 에서 키 8 개의 *모든 삽입 순서*(40320) 뒤 불변식 + 삭제 순서 무작위 3 개씩(매 단계 불변식·내용 대조)  ② t = 2, 3, 5, 16 에서 무작위 삽입·삭제 100 만 번을 std::set 과 대조(주기적 불변식)
//  ③ 정렬된 입력 10 만 개: 높이 ≤ 1 + log_t((n+1)/2) (CLRS 정리), 조회 한 번에 방문하는 노드 수(= 디스크 읽기) = 높이 이하  ④ 삭제된 노드는 free-list 로 재사용.
struct BTree {
    struct Node { std::vector<int> keys, kids; bool leaf = true; };
    int t; std::vector<Node> pool; std::vector<int> freeList; int root; size_t cnt = 0; long visited = 0;
    explicit BTree(int minDegree) : t(minDegree) { root = make(true); }
    int make(bool leaf) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); pool[u] = Node(); } else { pool.push_back(Node()); u = (int)pool.size() - 1; } pool[u].leaf = leaf; return u; }
    bool full(int x) const { return (int)pool[x].keys.size() == 2 * t - 1; }
    void splitChild(int x, int i) {                                                                              // x.kids[i] 가 가득 찼을 때 가운데 키를 x 로 올리고 둘로 쪼갠다
        int y = pool[x].kids[i], z = make(pool[y].leaf); int mid = pool[y].keys[t - 1];
        pool[z].keys.assign(pool[y].keys.begin() + t, pool[y].keys.end()); if (!pool[y].leaf) { pool[z].kids.assign(pool[y].kids.begin() + t, pool[y].kids.end()); pool[y].kids.resize(t); }
        pool[y].keys.resize(t - 1); pool[x].keys.insert(pool[x].keys.begin() + i, mid); pool[x].kids.insert(pool[x].kids.begin() + i + 1, z); }
    bool contains(int k) { int x = root; for (;;) { ++visited; const Node& nd = pool[x]; int i = (int)(std::lower_bound(nd.keys.begin(), nd.keys.end(), k) - nd.keys.begin()); if (i < (int)nd.keys.size() && nd.keys[i] == k) return true; if (nd.leaf) return false; x = nd.kids[i]; } }
    bool insert(int k) {
        if (contains(k)) return false;
        if (full(root)) { int s = make(false); pool[s].kids.push_back(root); root = s; splitChild(s, 0); }
        int x = root; for (;;) { int i = (int)(std::upper_bound(pool[x].keys.begin(), pool[x].keys.end(), k) - pool[x].keys.begin());
            if (pool[x].leaf) { pool[x].keys.insert(pool[x].keys.begin() + i, k); break; }
            if (full(pool[x].kids[i])) { splitChild(x, i); if (k > pool[x].keys[i]) ++i; } x = pool[x].kids[i]; }
        ++cnt; return true; }
    int maxKey(int x) const { while (!pool[x].leaf) x = pool[x].kids.back(); return pool[x].keys.back(); }
    int minKey(int x) const { while (!pool[x].leaf) x = pool[x].kids.front(); return pool[x].keys.front(); }
    void mergeKids(int x, int i) {                                                                               // kids[i] + keys[i] + kids[i+1] → kids[i]
        int y = pool[x].kids[i], z = pool[x].kids[i + 1]; pool[y].keys.push_back(pool[x].keys[i]); pool[y].keys.insert(pool[y].keys.end(), pool[z].keys.begin(), pool[z].keys.end());
        if (!pool[y].leaf) pool[y].kids.insert(pool[y].kids.end(), pool[z].kids.begin(), pool[z].kids.end()); pool[x].keys.erase(pool[x].keys.begin() + i); pool[x].kids.erase(pool[x].kids.begin() + i + 1); freeList.push_back(z); }
    int fill(int x, int i) {                                                                                     // kids[i] 의 키가 t−1 개 → t 개 이상으로 만들고 (병합으로 인덱스가 바뀔 수 있어) 내려갈 자식 인덱스를 돌려준다
        int c = pool[x].kids[i];
        if (i > 0 && (int)pool[pool[x].kids[i - 1]].keys.size() >= t) { int l = pool[x].kids[i - 1];                       // 왼쪽 형제에게서 빌린다
            pool[c].keys.insert(pool[c].keys.begin(), pool[x].keys[i - 1]); pool[x].keys[i - 1] = pool[l].keys.back(); pool[l].keys.pop_back();
            if (!pool[c].leaf) { pool[c].kids.insert(pool[c].kids.begin(), pool[l].kids.back()); pool[l].kids.pop_back(); } return i; }
        if (i + 1 < (int)pool[x].kids.size() && (int)pool[pool[x].kids[i + 1]].keys.size() >= t) { int r = pool[x].kids[i + 1];   // 오른쪽 형제에게서 빌린다
            pool[c].keys.push_back(pool[x].keys[i]); pool[x].keys[i] = pool[r].keys.front(); pool[r].keys.erase(pool[r].keys.begin());
            if (!pool[c].leaf) { pool[c].kids.push_back(pool[r].kids.front()); pool[r].kids.erase(pool[r].kids.begin()); } return i; }
        if (i + 1 < (int)pool[x].kids.size()) { mergeKids(x, i); return i; } mergeKids(x, i - 1); return i - 1; }
    bool eraseFrom(int x, int k) {
        int i = (int)(std::lower_bound(pool[x].keys.begin(), pool[x].keys.end(), k) - pool[x].keys.begin());
        if (i < (int)pool[x].keys.size() && pool[x].keys[i] == k) {
            if (pool[x].leaf) { pool[x].keys.erase(pool[x].keys.begin() + i); return true; }
            int y = pool[x].kids[i], z = pool[x].kids[i + 1];
            if ((int)pool[y].keys.size() >= t) { int p = maxKey(y); pool[x].keys[i] = p; return eraseFrom(y, p); }
            if ((int)pool[z].keys.size() >= t) { int s = minKey(z); pool[x].keys[i] = s; return eraseFrom(z, s); }
            mergeKids(x, i); return eraseFrom(y, k); }
        if (pool[x].leaf) return false;
        if ((int)pool[pool[x].kids[i]].keys.size() < t) i = fill(x, i); return eraseFrom(pool[x].kids[i], k); }
    bool erase(int k) { bool r = eraseFrom(root, k); if (pool[root].keys.empty() && !pool[root].leaf) { int old = root; root = pool[root].kids[0]; freeList.push_back(old); } if (r) --cnt; return r; }
    int height() const { int h = 1; for (int x = root; !pool[x].leaf; x = pool[x].kids[0]) ++h; return h; }
    bool check(int x, bool isRoot, int depth, int leafDepth, long long lo, long long hi, size_t& seen) const {
        const Node& nd = pool[x]; int n = (int)nd.keys.size(); if (n > 2 * t - 1 || (!isRoot && n < t - 1)) return false; seen += n;
        for (int i = 0; i < n; ++i) { if (!(nd.keys[i] > lo && nd.keys[i] < hi) || (i && nd.keys[i - 1] >= nd.keys[i])) return false; }
        if (nd.leaf) return depth == leafDepth; if ((int)nd.kids.size() != n + 1) return false;
        for (int i = 0; i <= n; ++i) if (!check(nd.kids[i], false, depth + 1, leafDepth, i ? nd.keys[i - 1] : lo, i < n ? nd.keys[i] : hi, seen)) return false; return true; }
    bool valid() const { size_t seen = 0; return check(root, true, 1, height(), -(1LL << 40), 1LL << 40, seen) && seen == cnt; }
    void inorder(int x, std::vector<int>& out) const { for (size_t i = 0; i < pool[x].keys.size(); ++i) { if (!pool[x].leaf) inorder(pool[x].kids[i], out); out.push_back(pool[x].keys[i]); } if (!pool[x].leaf) inorder(pool[x].kids.back(), out); }
    std::vector<int> items() const { std::vector<int> v; inorder(root, v); return v; }
};

int main() {
    std::mt19937 rng(151);
    { std::vector<int> ins(8); std::iota(ins.begin(), ins.end(), 0); long seqs = 0;                              // ① t = 2, 키 8 개
      do { BTree b(2); std::set<int> ref; for (int k : ins) { assert(b.insert(k)); ref.insert(k); } assert(b.valid() && b.items() == std::vector<int>(ref.begin(), ref.end()));
           for (int rep = 0; rep < 3; ++rep) { BTree c(2); for (int k : ins) c.insert(k); std::vector<int> del = ins; std::shuffle(del.begin(), del.end(), rng); std::set<int> r2 = ref;
               for (int k : del) { assert(c.erase(k)); r2.erase(k); assert(c.valid() && c.items() == std::vector<int>(r2.begin(), r2.end())); } assert(c.cnt == 0); ++seqs; }
      } while (std::next_permutation(ins.begin(), ins.end())); assert(seqs == 3 * 40320); }
    for (int t : {2, 3, 5, 16}) { BTree b(t); std::set<int> ref; for (long step = 0; step < 1000000; ++step) { int k = (int)(rng() % 60000); if (rng() % 100 < 52) { bool a = b.insert(k); bool r = ref.insert(k).second; assert(a == r); } else { bool a = b.erase(k); bool r = ref.erase(k) > 0; assert(a == r); }
        assert(b.cnt == ref.size()); if (step % 20011 == 0) assert(b.valid()); } assert(b.valid() && b.items() == std::vector<int>(ref.begin(), ref.end())); }                                     // ②
    for (int t : {2, 8, 64}) { BTree b(t); const int n = 100000; for (int k = 1; k <= n; ++k) b.insert(k); int h = b.height(); assert(b.valid() && h <= 1 + std::log((n + 1) / 2.0) / std::log((double)t) + 1e-9);                   // ③
        b.visited = 0; for (int k = 1; k <= n; k += 7) assert(b.contains(k)); assert(b.visited <= (long)h * ((n + 6) / 7)); size_t arena = b.pool.size(); for (int k = 1; k <= n; k += 2) b.erase(k); for (int k = 1; k <= n; k += 2) b.insert(k); assert(b.valid() && b.pool.size() <= arena + 8);          // ④
        if (t == 2) std::cout << "BTree: all 3*40320 (insert order, delete order) samples at t=2 kept the invariants, random insert/erase over t=2/3/5/16 matched std::set for 10^6 operations each, and 10^5 sorted keys gave height " << h << " at t=2" << std::endl; }
    return 0;
}
// Time Complexity: 검색·삽입·삭제 O(t · log_t N), 디스크 접근 O(log_t N)
// Space Complexity: O(N)
```
## BPlusTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// B+트리(트리 관점의 요약, 정본은 Tree.md Part 13): 모든 값을 잎에만 두고 잎들을 연결 리스트로 이어 범위 질의를 "한 번 찾고 옆으로 훑기" 로 만든다. 내부 노드는 길 안내용 분리 키만 가진다 (DB 인덱스의 표준).
//  정본은 삽입만 있었다 — 여기서는 *삭제*(잎 재분배/병합, 내부 노드 재분배/병합, 루트 축소)까지 갖춘 동적 B+트리를 보이고, 분리 키는 "오른쪽 부분 트리의 키 ≥ 분리 키 > 왼쪽 부분 트리의 키" 만 지키면 되므로 삭제 뒤에 갱신하지 않아도 된다.
//  차수 M(노드당 최대 키 수): 잎 최소 ⌈M/2⌉ 개(분할 시 ⌊(M+1)/2⌋ 와 나머지), 내부 최소 ⌊M/2⌋ 개.  ① 전수: M = 3, 4 에서 키 8 개의 모든 삽입 순서(40320) 뒤 불변식 + 삭제 순서 무작위 2 개씩  ② M = 3, 4, 5, 16, 64 에서 무작위 삽입·삭제 100 만 번을 std::map 과 대조(주기적 불변식·잎 연결 순회)
//  ③ 범위 질의 [lo, hi]: 잎 연결을 따라가며 읽은 값이 std::map 의 구간과 같고, 읽은 노드 수 = 높이 + (구간이 걸친 잎 수 − 1)  ④ 불변식: 모든 잎 깊이 동일, 키 수 범위, 분리 키 경계, 잎 연결이 모든 키를 정렬된 순서로 담음.
struct BPlus {
    struct Node { bool leaf = true; std::vector<int> keys, kids, vals; int next = -1; };
    int M; std::vector<Node> pool; std::vector<int> freeList; int root; size_t cnt = 0; long reads = 0;
    explicit BPlus(int maxKeys) : M(maxKeys) { root = make(true); }
    int minLeaf() const { return (M + 1) / 2; }
    int minInternal() const { return M / 2; }
    int make(bool leaf) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); pool[u] = Node(); } else { pool.push_back(Node()); u = (int)pool.size() - 1; } pool[u].leaf = leaf; return u; }
    int childIndex(int x, int k) const { return (int)(std::upper_bound(pool[x].keys.begin(), pool[x].keys.end(), k) - pool[x].keys.begin()); }
    int leafFor(int k) { int x = root; ++reads; while (!pool[x].leaf) { x = pool[x].kids[childIndex(x, k)]; ++reads; } return x; }
    bool find(int k, int& val) { int l = leafFor(k); auto it = std::lower_bound(pool[l].keys.begin(), pool[l].keys.end(), k); if (it == pool[l].keys.end() || *it != k) return false; val = pool[l].vals[it - pool[l].keys.begin()]; return true; }
    bool insRec(int x, int k, int v, int& up, int& right, bool& added) {                                          // 분할이 일어나면 true
        if (pool[x].leaf) { auto it = std::lower_bound(pool[x].keys.begin(), pool[x].keys.end(), k); size_t pos = it - pool[x].keys.begin(); if (it != pool[x].keys.end() && *it == k) { pool[x].vals[pos] = v; return false; }
            pool[x].keys.insert(it, k); pool[x].vals.insert(pool[x].vals.begin() + pos, v); added = true; if ((int)pool[x].keys.size() <= M) return false;
            int mid = (M + 1) / 2, r = make(true); pool[r].keys.assign(pool[x].keys.begin() + mid, pool[x].keys.end()); pool[r].vals.assign(pool[x].vals.begin() + mid, pool[x].vals.end()); pool[x].keys.resize(mid); pool[x].vals.resize(mid);
            pool[r].next = pool[x].next; pool[x].next = r; up = pool[r].keys[0]; right = r; return true; }
        int i = childIndex(x, k), u, r; if (!insRec(pool[x].kids[i], k, v, u, r, added)) return false;
        pool[x].keys.insert(pool[x].keys.begin() + i, u); pool[x].kids.insert(pool[x].kids.begin() + i + 1, r); if ((int)pool[x].keys.size() <= M) return false;
        int mid = (M + 1) / 2, nr = make(false); up = pool[x].keys[mid]; pool[nr].keys.assign(pool[x].keys.begin() + mid + 1, pool[x].keys.end()); pool[nr].kids.assign(pool[x].kids.begin() + mid + 1, pool[x].kids.end()); pool[x].keys.resize(mid); pool[x].kids.resize(mid + 1); right = nr; return true; }
    bool insert(int k, int v) { int up, r; bool added = false; if (insRec(root, k, v, up, r, added)) { int nr = make(false); pool[nr].keys = {up}; pool[nr].kids = {root, r}; root = nr; } if (added) ++cnt; return added; }
    void fix(int x, int i) {                                                                                     // kids[i] 가 최소치 미만 → 형제에게 빌리거나 병합
        int c = pool[x].kids[i]; bool leaf = pool[c].leaf; int mn = leaf ? minLeaf() : minInternal();
        if (i > 0) { int l = pool[x].kids[i - 1]; if ((int)pool[l].keys.size() > mn) {
            if (leaf) { pool[c].keys.insert(pool[c].keys.begin(), pool[l].keys.back()); pool[c].vals.insert(pool[c].vals.begin(), pool[l].vals.back()); pool[l].keys.pop_back(); pool[l].vals.pop_back(); pool[x].keys[i - 1] = pool[c].keys[0]; }
            else { pool[c].keys.insert(pool[c].keys.begin(), pool[x].keys[i - 1]); pool[c].kids.insert(pool[c].kids.begin(), pool[l].kids.back()); pool[l].kids.pop_back(); pool[x].keys[i - 1] = pool[l].keys.back(); pool[l].keys.pop_back(); } return; } }
        if (i + 1 < (int)pool[x].kids.size()) { int r = pool[x].kids[i + 1]; if ((int)pool[r].keys.size() > mn) {
            if (leaf) { pool[c].keys.push_back(pool[r].keys.front()); pool[c].vals.push_back(pool[r].vals.front()); pool[r].keys.erase(pool[r].keys.begin()); pool[r].vals.erase(pool[r].vals.begin()); pool[x].keys[i] = pool[r].keys[0]; }
            else { pool[c].keys.push_back(pool[x].keys[i]); pool[c].kids.push_back(pool[r].kids.front()); pool[r].kids.erase(pool[r].kids.begin()); pool[x].keys[i] = pool[r].keys.front(); pool[r].keys.erase(pool[r].keys.begin()); } return; } }
        int s = i > 0 ? i - 1 : i; int a = pool[x].kids[s], b = pool[x].kids[s + 1];                              // 병합: b 를 a 로
        if (leaf) { pool[a].keys.insert(pool[a].keys.end(), pool[b].keys.begin(), pool[b].keys.end()); pool[a].vals.insert(pool[a].vals.end(), pool[b].vals.begin(), pool[b].vals.end()); pool[a].next = pool[b].next; }
        else { pool[a].keys.push_back(pool[x].keys[s]); pool[a].keys.insert(pool[a].keys.end(), pool[b].keys.begin(), pool[b].keys.end()); pool[a].kids.insert(pool[a].kids.end(), pool[b].kids.begin(), pool[b].kids.end()); }
        pool[x].keys.erase(pool[x].keys.begin() + s); pool[x].kids.erase(pool[x].kids.begin() + s + 1); freeList.push_back(b); }
    bool eraseRec(int x, int k) {
        if (pool[x].leaf) { auto it = std::lower_bound(pool[x].keys.begin(), pool[x].keys.end(), k); if (it == pool[x].keys.end() || *it != k) return false; size_t pos = it - pool[x].keys.begin(); pool[x].keys.erase(it); pool[x].vals.erase(pool[x].vals.begin() + pos); return true; }
        int i = childIndex(x, k); if (!eraseRec(pool[x].kids[i], k)) return false; int c = pool[x].kids[i];
        if ((int)pool[c].keys.size() < (pool[c].leaf ? minLeaf() : minInternal())) fix(x, i); return true; }
    bool erase(int k) { bool r = eraseRec(root, k); if (r) --cnt; if (!pool[root].leaf && pool[root].keys.empty()) { int old = root; root = pool[root].kids[0]; freeList.push_back(old); } return r; }
    std::vector<std::pair<int, int>> range(int lo, int hi) { std::vector<std::pair<int, int>> out; int first = leafFor(lo); for (int l = first; l >= 0; l = pool[l].next) { if (l != first) ++reads; for (size_t i = 0; i < pool[l].keys.size(); ++i) { if (pool[l].keys[i] > hi) return out; if (pool[l].keys[i] >= lo) out.push_back({pool[l].keys[i], pool[l].vals[i]}); } } return out; }
    int height() const { int h = 1; for (int x = root; !pool[x].leaf; x = pool[x].kids[0]) ++h; return h; }
    bool check(int x, bool isRoot, int depth, int leafDepth, long long lo, long long hi, size_t& seen) const {
        const Node& nd = pool[x]; int n = (int)nd.keys.size();
        if (nd.leaf) { if (n > M || (!isRoot && n < minLeaf()) || nd.vals.size() != nd.keys.size() || depth != leafDepth) return false; for (int i = 0; i < n; ++i) { if (!(nd.keys[i] >= lo && nd.keys[i] < hi) || (i && nd.keys[i - 1] >= nd.keys[i])) return false; } seen += n; return true; }
        if (n > M || (!isRoot && n < minInternal()) || (isRoot && n < 1) || (int)nd.kids.size() != n + 1) return false; for (int i = 1; i < n; ++i) if (nd.keys[i - 1] >= nd.keys[i]) return false;
        for (int i = 0; i <= n; ++i) if (!check(nd.kids[i], false, depth + 1, leafDepth, i ? nd.keys[i - 1] : lo, i < n ? nd.keys[i] : hi, seen)) return false; return true; }
    bool valid() const { size_t seen = 0; if (!check(root, true, 1, height(), -(1LL << 40), 1LL << 40, seen) || seen != cnt) return false; int l = root; while (!pool[l].leaf) l = pool[l].kids[0]; size_t total = 0; long long prev = -(1LL << 40); for (; l >= 0; l = pool[l].next) for (int k : pool[l].keys) { if (k <= prev) return false; prev = k; ++total; } return total == cnt; }
};

int main() {
    std::mt19937 rng(153);
    for (int M : {3, 4}) { std::vector<int> ins(8); std::iota(ins.begin(), ins.end(), 0);                         // ①
        do { BPlus b(M); std::map<int, int> ref; for (int k : ins) { assert(b.insert(k, k * 10)); ref[k] = k * 10; } assert(b.valid());
             for (int rep = 0; rep < 2; ++rep) { BPlus c(M); for (int k : ins) c.insert(k, k * 10); std::vector<int> del = ins; std::shuffle(del.begin(), del.end(), rng); std::map<int, int> r2 = ref; for (int k : del) { assert(c.erase(k)); r2.erase(k); assert(c.valid() && c.cnt == r2.size()); } assert(c.cnt == 0); }
        } while (std::next_permutation(ins.begin(), ins.end())); }
    for (int M : {3, 4, 5, 16, 64}) { BPlus b(M); std::map<int, int> ref; for (long step = 0; step < 1000000; ++step) { int k = (int)(rng() % 80000); int op = (int)(rng() % 100);                          // ②
        if (op < 50) { bool a = b.insert(k, (int)step); bool r = ref.insert({k, (int)step}).second; if (!r) ref[k] = (int)step; assert(a == r); } else if (op < 90) { bool a = b.erase(k); bool r = ref.erase(k) > 0; assert(a == r); } else { int v; bool a = b.find(k, v); auto it = ref.find(k); assert(a == (it != ref.end()) && (!a || v == it->second)); }
        assert(b.cnt == ref.size()); if (step % 25013 == 0) assert(b.valid()); } assert(b.valid());
      for (int q = 0; q < 300; ++q) { int lo = (int)(rng() % 80000), hi = lo + (int)(rng() % 3000); b.reads = 0; auto got = b.range(lo, hi); std::vector<std::pair<int, int>> want(ref.lower_bound(lo), ref.upper_bound(hi)); assert(got == want); } }        // ③ 범위 질의
    { BPlus b(64); const int n = 200000; for (int k = 0; k < n; ++k) b.insert(k, k); assert(b.valid()); int h = b.height(); b.reads = 0; auto r = b.range(1000, 1000 + 64 * 20); std::vector<int> ks; for (auto& p : r) ks.push_back(p.first); assert((int)r.size() == 64 * 20 + 1 && std::is_sorted(ks.begin(), ks.end()));
      int overlapping = 0; { int l = b.root; while (!b.pool[l].leaf) l = b.pool[l].kids[0]; for (; l >= 0; l = b.pool[l].next) if (b.pool[l].keys.back() >= 1000 && b.pool[l].keys.front() <= 1000 + 64 * 20) ++overlapping; }
      assert(b.reads >= h + overlapping - 1 && b.reads <= h + overlapping);                                      // 읽은 노드 수 = 높이 + (걸친 잎 수 − 1) (끝이 잎 경계면 잎 하나 더)
      std::cout << "BPlusTree: all insertion orders of 8 keys with random deletions kept the invariants at M=3 and 4, 10^6 random operations at M=3/4/5/16/64 matched std::map including range scans over the leaf chain, and a 200000-key tree of order 64 had height " << h << " with a 1281-key range read touching " << b.reads << " nodes" << std::endl; }
    return 0;
}
// Time Complexity: 검색·삽입·삭제 O(log_M N), 범위 질의 O(log_M N + k)
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
struct PoolCleaner { ~PoolCleaner() { for (Node* n : pool) delete n; } } poolCleaner;                       // 프로그램이 끝날 때 노드 풀을 해제
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
struct PoolCleaner { ~PoolCleaner() { for (Node* n : pool) delete n; } } poolCleaner;                       // 프로그램이 끝날 때 노드 풀을 해제
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

## CSBPlusTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <vector>

// CSB+-트리(Cache-Sensitive B+-Tree, Rao & Ross 2000): B+-트리의 내부 노드는 키 K 개와 자식 포인터 K+1 개를 담는데, 메인 메모리 인덱스에서는 노드 하나가 캐시 줄(64 B)에 딱 맞을 때 가장 빠르다.
// 포인터 8 B 가 공간의 대부분을 먹으므로 64 B 노드에 키가 5 개(4 B 키 + 8 B 포인터)밖에 안 들어간다. CSB+ 는 "한 부모의 자식들을 메모리에 연속 배열(노드 그룹)로 둔다" — 그러면 자식 포인터 하나(그룹의 첫 주소)와
// 인덱스만으로 i 번째 자식을 찾을 수 있어 같은 64 B 에 키가 13 개 들어간다. 팬아웃이 6 → 14 로 늘어 트리가 낮아지고(캐시 미스 감소) 노드 안 이분 탐색이 한 캐시 줄에서 끝난다.
// 대가: 자식이 갈라지면 그룹 안의 노드들을 한 칸씩 밀어야 하고(노드 복사), 그룹이 가득 차 있으면 부모를 쪼개 두 개의 새 그룹으로 나눈다. 노드는 자식 그룹의 주소만 들고 있어 노드를 통째로 복사해도 아래 서브트리는 그대로 유효하다.
// 이 구현: 내부 노드(KI=13)와 잎(KL=7)을 분리한 템플릿, 삽입(덮어쓰기)·검색·lower_bound 순회·게으른 삭제(잎에서만 지우고 병합하지 않는다 — 읽기 위주 메모리 인덱스의 흔한 선택).
// 검증: ① 노드 크기 <= 64 B 와 팬아웃(14 대 6) ② 무작위 삽입·덮어쓰기를 std::map 과 대조(작은 노드 KI=3·KL=3 의 깊은 트리와 KI=13·KL=7), 삽입만 한 트리는 불변식(키 순서·분리 키 범위·점유율 >= 절반) 검사
//       ③ 삭제 섞인 연산도 std::map 과 대조 ④ 같은 알고리즘을 포인터 방식 팬아웃(KI=5)으로 돌리면 트리가 더 높다 — 검색 한 번이 건드리는 캐시 줄 수 비교
template <int KI, int KL> class CsbTree {
public:
    struct Leaf { int n = 0; int key[KL]; int val[KL]; };
    struct Inner { int n = 0; int key[KI]; void* group = nullptr; };                              // group: 자식들의 연속 배열(내부 노드 또는 잎) 첫 주소 하나만 안다
    CsbTree() { root.group = new Leaf[KI + 1]; }                                                   // 빈 트리: 키 0 개, 빈 잎 하나
    ~CsbTree() { release(root, height); }
    CsbTree(const CsbTree&) = delete; CsbTree& operator=(const CsbTree&) = delete;
    bool insert(int key, int val) {                                                                // 새 키면 true, 덮어쓰기면 false
        bool inserted = false; Inner right; int sep;
        if (insertInner(root, height, key, val, right, sep, inserted)) {                          // 뿌리가 갈라졌다: 새 뿌리의 그룹에 [옛 뿌리 복사본, 오른쪽] 을 둔다
            Inner* g = new Inner[KI + 1]; g[0] = root; g[1] = right; root = Inner(); root.n = 1; root.key[0] = sep; root.group = g; ++height;
        }
        count += inserted; return inserted;
    }
    bool erase(int key) {                                                                          // 게으른 삭제: 잎에서만 지운다
        Leaf& lf = leafFor(key); int i = (int)(std::lower_bound(lf.key, lf.key + lf.n, key) - lf.key);
        if (i == lf.n || lf.key[i] != key) return false;
        for (int j = i; j + 1 < lf.n; ++j) { lf.key[j] = lf.key[j + 1]; lf.val[j] = lf.val[j + 1]; } --lf.n; --count; return true;
    }
    const int* find(int key) const { const Leaf& lf = leafFor(key); int i = (int)(std::lower_bound(lf.key, lf.key + lf.n, key) - lf.key); return i < lf.n && lf.key[i] == key ? &lf.val[i] : nullptr; }
    void scan(int from, std::vector<std::pair<int, int>>& out, size_t limit) const { scanRec(root, height, from, out, limit); }        // key >= from 인 항목을 키 순서로 최대 limit 개
    size_t size() const { return count; } int levels() const { return height; }                    // levels: 내부 노드 층 수(검색 한 번이 읽는 내부 노드 수)
    bool valid(bool checkOccupancy) const { long lo = -(1L << 40), hi = 1L << 40; size_t seen = 0; bool ok = validRec(root, height, lo, hi, true, checkOccupancy, seen); return ok && seen == count; }
private:
    Inner root; int height = 1; size_t count = 0;
    static void release(Inner& n, int level) {
        if (level == 1) { delete[] static_cast<Leaf*>(n.group); return; }
        Inner* g = static_cast<Inner*>(n.group); for (int i = 0; i <= n.n; ++i) release(g[i], level - 1); delete[] g;
    }
    const Leaf& leafFor(int key) const {
        const Inner* n = &root;
        for (int level = height; level > 1; --level) { int i = (int)(std::upper_bound(n->key, n->key + n->n, key) - n->key); n = &static_cast<const Inner*>(n->group)[i]; }
        int i = (int)(std::upper_bound(n->key, n->key + n->n, key) - n->key); return static_cast<const Leaf*>(n->group)[i];
    }
    Leaf& leafFor(int key) { return const_cast<Leaf&>(static_cast<const CsbTree*>(this)->leafFor(key)); }
    static bool insertLeaf(Leaf& lf, int key, int val, Leaf& right, int& sep, bool& inserted) {
        int i = (int)(std::lower_bound(lf.key, lf.key + lf.n, key) - lf.key);
        if (i < lf.n && lf.key[i] == key) { lf.val[i] = val; return false; }
        inserted = true;
        if (lf.n < KL) { for (int j = lf.n; j > i; --j) { lf.key[j] = lf.key[j - 1]; lf.val[j] = lf.val[j - 1]; } lf.key[i] = key; lf.val[i] = val; ++lf.n; return false; }
        int k[KL + 1], v[KL + 1]; for (int j = 0, s = 0; j <= KL; ++j) { if (j == i) { k[j] = key; v[j] = val; } else { k[j] = lf.key[s]; v[j] = lf.val[s]; ++s; } }       // 가득 찬 잎: 임시 배열에 합쳐 둘로 가른다
        const int left = (KL + 2) / 2; lf.n = left; right.n = KL + 1 - left;
        for (int j = 0; j < left; ++j) { lf.key[j] = k[j]; lf.val[j] = v[j]; } for (int j = left; j <= KL; ++j) { right.key[j - left] = k[j]; right.val[j - left] = v[j]; }
        sep = right.key[0]; return true;                                                           // B+ 의 복사 올리기: 분리 키는 오른쪽 잎의 첫 키
    }
    template <class C> static bool addChild(Inner& nd, int i, int sep, const C& child, Inner& rightOut, int& sepOut) {       // nd 의 i 번째 자식이 갈라져 오른쪽 조각 child 가 생겼다
        C* g = static_cast<C*>(nd.group);
        if (nd.n < KI) {                                                                           // 그룹에 빈자리: 뒤의 자식 노드들을 한 칸씩 민다(노드 복사)
            for (int j = nd.n; j > i; --j) nd.key[j] = nd.key[j - 1];
            for (int j = nd.n + 1; j > i + 1; --j) g[j] = g[j - 1];
            nd.key[i] = sep; g[i + 1] = child; ++nd.n; return false;
        }
        int keys[KI + 1]; std::vector<C> kids(g, g + KI + 1);                                      // 그룹이 가득: 부모(nd)를 쪼갠다
        for (int j = 0, s = 0; j <= KI; ++j) { if (j == i) keys[j] = sep; else keys[j] = nd.key[s++]; }
        kids.insert(kids.begin() + i + 1, child);
        const int mid = (KI + 1) / 2; C* lg = new C[KI + 1]; C* rg = new C[KI + 1];                // 키 KI+1 개 중 가운데는 위로, 새 그룹 둘을 만든다
        for (int j = 0; j <= mid; ++j) lg[j] = kids[(size_t)j]; for (int j = mid + 1; j <= KI + 1; ++j) rg[j - mid - 1] = kids[(size_t)j];
        delete[] g; nd.group = lg; nd.n = mid; for (int j = 0; j < mid; ++j) nd.key[j] = keys[j];
        rightOut = Inner(); rightOut.group = rg; rightOut.n = KI - mid; for (int j = mid + 1; j <= KI; ++j) rightOut.key[j - mid - 1] = keys[j];
        sepOut = keys[mid]; return true;
    }
    static bool insertInner(Inner& nd, int level, int key, int val, Inner& rightOut, int& sepOut, bool& inserted) {
        int i = (int)(std::upper_bound(nd.key, nd.key + nd.n, key) - nd.key); int sep;
        if (level == 1) { Leaf right; if (!insertLeaf(static_cast<Leaf*>(nd.group)[i], key, val, right, sep, inserted)) return false; return addChild<Leaf>(nd, i, sep, right, rightOut, sepOut); }
        Inner right; if (!insertInner(static_cast<Inner*>(nd.group)[i], level - 1, key, val, right, sep, inserted)) return false; return addChild<Inner>(nd, i, sep, right, rightOut, sepOut);
    }
    static void scanRec(const Inner& nd, int level, int from, std::vector<std::pair<int, int>>& out, size_t limit) {
        int start = (int)(std::upper_bound(nd.key, nd.key + nd.n, from) - nd.key);                // from 이 속한 자식부터
        for (int i = start; i <= nd.n && out.size() < limit; ++i) {
            if (level == 1) { const Leaf& lf = static_cast<const Leaf*>(nd.group)[i]; for (int j = 0; j < lf.n && out.size() < limit; ++j) if (lf.key[j] >= from) out.push_back({lf.key[j], lf.val[j]}); }
            else scanRec(static_cast<const Inner*>(nd.group)[i], level - 1, from, out, limit);
        }
    }
    bool validRec(const Inner& nd, int level, long lo, long hi, bool isRoot, bool occ, size_t& seen) const {
        if (nd.n > KI || (occ && !isRoot && nd.n < KI / 2)) return false;
        for (int i = 0; i + 1 < nd.n; ++i) if (nd.key[i] >= nd.key[i + 1]) return false;
        for (int i = 0; i <= nd.n; ++i) {
            long clo = i ? nd.key[i - 1] : lo, chi = i < nd.n ? nd.key[i] : hi; if (nd.n && (clo < lo || chi > hi)) return false;
            if (level == 1) { const Leaf& lf = static_cast<const Leaf*>(nd.group)[i]; if (lf.n > KL || (occ && lf.n < KL / 2 && !(isRoot && nd.n == 0))) return false;
                for (int j = 0; j < lf.n; ++j) { if (lf.key[j] < clo || lf.key[j] >= chi || (j && lf.key[j - 1] >= lf.key[j])) return false; ++seen; } }
            else if (!validRec(static_cast<const Inner*>(nd.group)[i], level - 1, clo, chi, false, occ, seen)) return false;
        }
        return true;
    }
};

int main() {
    static_assert(sizeof(CsbTree<13, 7>::Inner) <= 64 && sizeof(CsbTree<13, 7>::Leaf) <= 64, "한 노드가 캐시 줄 하나");
    {   CsbTree<3, 3> t; assert(t.find(5) == nullptr && t.valid(true));                           // 손으로 확인: 작은 노드(키 3 개)에서 1..10 삽입
        for (int k = 1; k <= 10; ++k) assert(t.insert(k, k * 10));
        assert(t.size() == 10 && t.levels() >= 2 && t.valid(true) && *t.find(7) == 70 && t.find(11) == nullptr && !t.insert(7, 71) && *t.find(7) == 71);
        std::vector<std::pair<int, int>> out; t.scan(4, out, 3); assert((out == std::vector<std::pair<int, int>>{{4, 40}, {5, 50}, {6, 60}})); }
    for (int cfg = 0; cfg < 2; ++cfg) for (int pass = 0; pass < 6; ++pass) {
        std::mt19937 rng(100 + cfg * 10 + pass); std::map<int, int> model; const bool withErase = pass >= 3;
        CsbTree<3, 3> small; CsbTree<13, 7> wide;
        for (int step = 0; step < 20000; ++step) {
            const int k = (int)(rng() % 5000), op = (int)(rng() % 10);
            if (op < 7 || !withErase) { const int v = (int)rng(); bool added = model.find(k) == model.end(); model[k] = v; bool a1 = small.insert(k, v), a2 = wide.insert(k, v); assert(a1 == added && a2 == added); }
            else { bool had = model.erase(k) > 0; assert(small.erase(k) == had && wide.erase(k) == had); }
            if (step % 3000 == 0) { assert(small.valid(!withErase) && wide.valid(!withErase) && small.size() == model.size() && wide.size() == model.size()); }
        }
        for (int k = 0; k < 5000; ++k) { auto it = model.find(k); const int* a = small.find(k); const int* b = wide.find(k); assert((a != nullptr) == (it != model.end()) && (b != nullptr) == (a != nullptr) && (!a || (*a == it->second && *b == it->second))); }
        for (int q = 0; q < 200; ++q) { int from = (int)(rng() % 5000); size_t lim = 1 + rng() % 40; std::vector<std::pair<int, int>> o1, o2, want; small.scan(from, o1, lim); wide.scan(from, o2, lim);
            for (auto it = model.lower_bound(from); it != model.end() && want.size() < lim; ++it) want.push_back(*it); assert(o1 == want && o2 == want); }
        if (cfg == 0 && pass == 0) assert(small.levels() > wide.levels());                         // 작은 노드일수록 깊다
    }
    std::mt19937 rng(7); CsbTree<13, 7> csb; CsbTree<5, 7> classic;                                // 팬아웃 비교: 같은 64 B 에 CSB+ 는 키 13 개, 포인터 방식은 5 개
    for (int i = 0; i < 200000; ++i) { int k = (int)rng(); csb.insert(k, i); classic.insert(k, i); }
    assert(csb.valid(true) && classic.valid(true) && csb.size() == classic.size() && csb.levels() < classic.levels());
    std::cout << "CsbPlusTree: matched std::map over 120000 random operations with 3-key and 13-key nodes (inserts, overwrites, lazy deletes, ordered scans); 200000 keys need " << csb.levels() << " inner levels with fan-out 14 (64-byte nodes) versus " << classic.levels() << " with fan-out 6, i.e. " << csb.levels() + 1 << " vs " << classic.levels() + 1 << " cache lines per lookup" << std::endl;
    return 0;
}
// Time Complexity: 검색 O(log_{K+1} N) 노드 (노드 안 이분 탐색), 삽입은 그룹 안 이동 O(K) 이 층마다 더해져 O(K log_{K+1} N)
// Space Complexity: O(N), 내부 노드에 자식 포인터가 하나뿐이라 같은 크기 노드에 키가 약 2.6 배
```

## BwTree()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <climits>
#include <iostream>
#include <map>
#include <random>
#include <thread>
#include <vector>

// Bw-트리(Levandoski·Lomet·Sengupta 2013, Microsoft Hekaton/Azure Cosmos DB): 락 없는 B-트리. 두 가지 발상으로 락과 제자리 수정을 모두 없앴다.
// ① 매핑 표(mapping table): 페이지를 포인터가 아니라 논리 번호(PID)로 가리키고, PID -> 현재 페이지 포인터를 원자 변수 배열에 둔다. 페이지를 바꾸는 일은 이 한 칸에 대한 CAS 한 번이다.
// ② 델타 레코드(delta record): 페이지를 고치지 않고, "키 k 를 v 로 삽입/삭제" 라는 불변 레코드를 만들어 옛 체인 머리 앞에 붙인 뒤 매핑 칸을 CAS 로 새 머리로 바꾼다. 읽기는 체인을 머리부터 훑다가 기본 페이지에서 이분 탐색한다.
// 체인이 길어지면 통합(consolidation): 체인을 접어 새 기본 페이지를 만들어 CAS 로 갈아 끼운다(그 사이에 누가 델타를 붙였으면 CAS 가 실패하므로 나중에 다시). 기본 페이지가 가득 차면 둘로 가른다:
// 오른쪽 조각을 새 PID 에 먼저 올리고, 왼쪽 기본 페이지(상한 키 = 분리 키, 오른쪽 형제 = 새 PID)를 CAS 로 갈아 끼운 뒤 부모(뿌리)에 분리 키를 CAS 로 넣는다. 부모 갱신이 늦어도 읽기·쓰기는 "키 >= 상한" 이면 오른쪽 형제로 건너가므로(B-link) 틀리지 않는다.
// 단순화: 내부 노드는 뿌리 한 층(PID 0, 통합 때 통째로 복사해 CAS)만 두고 내부 분할은 생략했다 — 실제 Bw-트리는 내부 노드에도 같은 델타·분할 델타를 쓴다. 교체된 레코드는 스레드별 휴지통에 모았다가 모든 스레드가 끝난 뒤 해제한다(실제로는 에포크 기반 회수를 쓴다 → EpochBasedReclamation).
// 검증: 4 스레드가 서로 섞인 키(k % 4 = 스레드 번호)에 삽입 65% · 삭제 25% · 조회 10% 를 6 만 번씩. 각 스레드는 자기 키의 모델을 갖고 있어 조회 결과가 정확히 일치해야 하고(선형성), 끝난 뒤 왼쪽 끝 페이지에서 오른쪽 형제를 따라 읽은 전체 내용이
//       모델들의 합집합과 같고 페이지 상한이 올바르다. 분할·통합이 여러 번 일어났는지, CAS 실패(경쟁)가 있었는지 보고한다.
struct Rec {
    enum Kind { BASE, INS, DEL, INNER } kind; int key = 0, val = 0; const Rec* next = nullptr; int high = INT_MAX; int right = -1; int deltas = 0;     // high: 이 페이지가 맡는 키의 상한(미포함), right: 오른쪽 형제 PID
    std::vector<std::pair<int, int>> items;                                                        // BASE: (키, 값) 정렬, INNER: (분리 키, 자식 PID) 정렬
    explicit Rec(Kind k) : kind(k) {}
};
const int MAXPID = 1 << 16, MAXLEAF = 16, CONSOLIDATE_AT = 6;
struct BwTree {
    std::atomic<const Rec*> table[MAXPID]; std::atomic<int> nextPid{2}; std::atomic<long> splits{0}, consolidations{0}, casFailures{0};
    std::vector<std::vector<const Rec*>> garbage;                                                  // 스레드별 휴지통(스레드 번호로 접근)
    explicit BwTree(int threads) : garbage((size_t)threads) {
        for (auto& t : table) t.store(nullptr);
        Rec* leaf = new Rec(Rec::BASE); table[1].store(leaf);                                      // 페이지 1: 가장 왼쪽 잎(분할해도 항상 PID 1 에 남는다)
        Rec* root = new Rec(Rec::INNER); root->items = {{INT_MIN, 1}}; table[0].store(root);
    }
    ~BwTree() { for (auto& g : garbage) for (const Rec* r : g) delete r; std::vector<const Rec*> live; for (int p = 0; p < nextPid.load(); ++p) for (const Rec* r = table[p].load(); r; r = r->next) live.push_back(r); for (const Rec* r : live) delete r; }
    int leafFor(int key) const {                                                                   // 뿌리에서 분리 키 <= key 인 마지막 자식
        const Rec* root = table[0].load(std::memory_order_acquire);
        auto it = std::upper_bound(root->items.begin(), root->items.end(), key, [](int k, const std::pair<int, int>& e) { return k < e.first; }); return (it - 1)->second;
    }
    bool lookup(int key, int& val) const {
        for (int pid = leafFor(key);;) {
            const Rec* head = table[pid].load(std::memory_order_acquire);
            if (key >= head->high) { pid = head->right; continue; }                                // 분할 뒤라 이 페이지 몫이 아니다: 오른쪽 형제로
            for (const Rec* r = head; r; r = r->next) {
                if (r->kind == Rec::INS && r->key == key) { val = r->val; return true; }
                if (r->kind == Rec::DEL && r->key == key) return false;
                if (r->kind == Rec::BASE) { auto it = std::lower_bound(r->items.begin(), r->items.end(), key, [](const std::pair<int, int>& e, int k) { return e.first < k; }); if (it != r->items.end() && it->first == key) { val = it->second; return true; } return false; }
            }
        }
    }
    void update(int t, Rec::Kind kind, int key, int val) {                                         // 델타를 붙인다 (INS/DEL)
        for (int pid = leafFor(key);;) {
            const Rec* head = table[pid].load(std::memory_order_acquire);
            if (key >= head->high) { pid = head->right; continue; }
            Rec* d = new Rec(kind); d->key = key; d->val = val; d->next = head; d->high = head->high; d->right = head->right; d->deltas = head->deltas + 1;
            const Rec* expect = head;
            if (table[pid].compare_exchange_strong(expect, d, std::memory_order_acq_rel)) { if (d->deltas >= CONSOLIDATE_AT) consolidate(t, pid); return; }
            delete d; casFailures.fetch_add(1);                                                    // 다른 스레드가 먼저 바꿨다: 새 머리를 읽고 다시
        }
    }
    void consolidate(int t, int pid) {
        const Rec* head = table[pid].load(std::memory_order_acquire); if (head->deltas == 0) return;
        std::vector<const Rec*> chain; for (const Rec* r = head; r; r = r->next) chain.push_back(r);
        std::map<int, int> m; for (auto it = chain.rbegin(); it != chain.rend(); ++it) { const Rec* r = *it; if (r->kind == Rec::BASE) m.insert(r->items.begin(), r->items.end()); else if (r->kind == Rec::INS) m[r->key] = r->val; else m.erase(r->key); }
        std::vector<std::pair<int, int>> items(m.begin(), m.end()); Rec* left = new Rec(Rec::BASE); left->high = head->high; left->right = head->right;
        Rec* rightRec = nullptr; int q = -1, sep = 0;
        if ((int)items.size() > MAXLEAF) {                                                         // 분할: 오른쪽 조각을 새 PID 에 먼저 올려 둔다(아직 아무도 모른다)
            const size_t mid = items.size() / 2; sep = items[mid].first; rightRec = new Rec(Rec::BASE); rightRec->items.assign(items.begin() + (long)mid, items.end()); rightRec->high = head->high; rightRec->right = head->right;
            left->items.assign(items.begin(), items.begin() + (long)mid); q = nextPid.fetch_add(1); table[q].store(rightRec, std::memory_order_release); left->high = sep; left->right = q;
        } else left->items = items;
        const Rec* expect = head;
        if (!table[pid].compare_exchange_strong(expect, left, std::memory_order_acq_rel)) { casFailures.fetch_add(1); delete left; if (rightRec) { table[q].store(nullptr); delete rightRec; } return; }   // 그 사이 델타가 붙었다: 포기
        for (const Rec* r : chain) garbage[(size_t)t].push_back(r); consolidations.fetch_add(1);
        if (rightRec) { splits.fetch_add(1); addSeparator(t, sep, q); }
    }
    void addSeparator(int t, int sep, int q) {                                                     // 부모(뿌리)에 (분리 키, 새 PID) 를 CAS 로 넣는다
        for (;;) {
            const Rec* root = table[0].load(std::memory_order_acquire); Rec* nr = new Rec(Rec::INNER); nr->items = root->items;
            auto it = std::lower_bound(nr->items.begin(), nr->items.end(), sep, [](const std::pair<int, int>& e, int k) { return e.first < k; }); nr->items.insert(it, {sep, q});
            const Rec* expect = root; if (table[0].compare_exchange_strong(expect, nr, std::memory_order_acq_rel)) { garbage[(size_t)t].push_back(root); return; }
            delete nr; casFailures.fetch_add(1);
        }
    }
    std::vector<std::pair<int, int>> scanAll(bool& boundsOk) const {                               // 왼쪽 끝 페이지에서 오른쪽 형제를 따라 전체를 읽는다
        std::vector<std::pair<int, int>> out; boundsOk = true; int lowKey = INT_MIN;
        for (int pid = 1; pid != -1;) {
            const Rec* head = table[pid].load(); std::map<int, int> m; std::vector<const Rec*> chain; for (const Rec* r = head; r; r = r->next) chain.push_back(r);
            for (auto it = chain.rbegin(); it != chain.rend(); ++it) { const Rec* r = *it; if (r->kind == Rec::BASE) m.insert(r->items.begin(), r->items.end()); else if (r->kind == Rec::INS) m[r->key] = r->val; else m.erase(r->key); }
            for (const auto& kv : m) { if (kv.first < lowKey || kv.first >= head->high) boundsOk = false; out.push_back(kv); }
            lowKey = head->high; pid = head->right;
        }
        return out;
    }
};

// audit: stress
int main() {
    const int T = 4, KEYS = 40000, OPS = 60000; BwTree tree(T); std::vector<std::map<int, int>> models((size_t)T); std::atomic<long> mismatches{0}, lookups{0};
    std::vector<std::thread> threads;
    for (int t = 0; t < T; ++t) threads.emplace_back([&, t] {
        std::mt19937 rng(500 + (unsigned)t); auto& model = models[(size_t)t];
        for (int op = 0; op < OPS; ++op) {
            const int k = (int)(rng() % (unsigned)(KEYS / T)) * T + t, r = (int)(rng() % 100);        // 키 k 는 스레드 t 의 몫(k % T == t): 서로 다른 스레드의 키가 같은 페이지에 섞인다
            if (r < 65) { const int v = (int)(rng() % 1000000); tree.update(t, Rec::INS, k, v); model[k] = v; }
            else if (r < 90) { tree.update(t, Rec::DEL, k, 0); model.erase(k); }
            else { int v = 0; const bool found = tree.lookup(k, v); auto it = model.find(k); lookups.fetch_add(1); if (found != (it != model.end()) || (found && v != it->second)) mismatches.fetch_add(1); }
        } });
    for (auto& th : threads) th.join();
    std::map<int, int> expect; for (const auto& m : models) expect.insert(m.begin(), m.end());
    bool boundsOk = false; auto all = tree.scanAll(boundsOk);
    assert((mismatches.load() == 0 && boundsOk && all == std::vector<std::pair<int, int>>(expect.begin(), expect.end())));      // 조회는 모두 선형적으로 맞았고 최종 내용 == 모델의 합집합
    assert(tree.splits.load() > 10 && tree.consolidations.load() > tree.splits.load());
    for (const auto& kv : expect) { int v = 0; assert(tree.lookup(kv.first, v) && v == kv.second); }
    std::cout << "BwTree: " << T << " threads ran " << T * OPS << " inserts/deletes/lookups on interleaved keys with no lookup mismatch; final contents (" << expect.size() << " keys) equalled the models; " << tree.splits.load() << " page splits, " << tree.consolidations.load() << " consolidations, " << tree.casFailures.load() << " lost CAS races" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(체인 길이 + log 페이지 크기) — 체인은 CONSOLIDATE_AT 이하, 갱신 O(1) CAS (+ 통합 O(페이지 크기))
// Space Complexity: O(N + 델타·휴지통) — 휴지통은 통합마다 늘어 (실제로는 에포크 회수로 비운다)
```

## Masstree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <string>
#include <vector>

// Masstree(Mao·Kohler·Morris 2012, 메인 메모리 키-값 저장소): 가변 길이 문자열 키를 위한 "B+-트리들의 트라이". 키를 8 바이트 조각으로 자르고, 층(layer) 하나가 조각 하나를 키로 하는 정렬 인덱스(원래는 동시성 제어가 붙은 B+-트리)다.
// 8 바이트 정수 비교 한 번으로 노드 안 탐색이 끝나므로 긴 문자열 비교를 하지 않고, 공통 접두사가 긴 키(URL, 경로)도 층이 깊어질 뿐 비교 횟수는 늘지 않는다. 층 안의 항목 키는 (조각, 길이): 길이 0..8 은 "키가 이 조각에서 끝남"(값 저장),
// 길이 9 는 "키가 더 이어짐" — 이어지는 키가 하나뿐이면 나머지 바이트(접미사)를 항목에 그대로 달아 두고, 같은 조각으로 시작하는 키가 둘 이상이 되면 그제야 새 층을 만들어 둘 다 옮긴다(층 지연 생성).
// 지우면 그 반대로, 층에 항목이 하나만 남으면 부모 항목의 접미사로 접어 올려 층 구조가 키 집합만으로 정해지게(정규형) 한다. 항목은 (조각 값, 길이) 순으로 정렬되며 이 순서가 곧 키의 사전식 순서다("abc" < "abc\0" < "abc\0x").
// 이 구현은 층 인덱스를 std::map 으로 대신하고 동시성 제어(버전 번호 기반 낙관적 읽기)는 생략했다 — 핵심인 조각 트라이, 지연 층 생성·접기, 순서 보존 순회를 구현·검증한다.
// 검증: 알파벳 {a, b, \0} 의 짧은 키와 18~30 바이트 공통 접두사를 가진 긴 키를 섞은 무작위 삽입·덮어쓰기·삭제·조회·범위 순회 5 만 번을 std::map<string,int> 와 대조, 접두사 관계·\0 포함·빈 키 포함.
//       끝난 트리의 층 구조 문자열이 같은 키 집합을 무작위 순서로 새로 만든 트리와 동일(정규형), 깊은 층(>= 3)이 실제로 쓰였음
struct Masstree {
    struct Layer;
    struct Entry { int val = 0; bool link = false; std::string suffix; std::unique_ptr<Layer> next; };       // link=false 이고 길이 9 면 접미사 항목, link=true 면 하위 층
    struct Layer { std::map<std::pair<uint64_t, int>, Entry> m; };
    typedef std::pair<uint64_t, int> Key;
    std::unique_ptr<Layer> root{new Layer}; size_t count = 0;
    static uint64_t sliceOf(const std::string& s, size_t off, size_t len) { uint64_t v = 0; for (size_t i = 0; i < 8; ++i) v = v << 8 | (i < len ? (unsigned char)s[off + i] : 0); return v; }     // 큰 자리부터: 정수 비교 = 바이트 사전식 비교
    static std::string bytesOf(uint64_t slice, size_t len) { std::string s; for (size_t i = 0; i < len; ++i) s += (char)(slice >> (56 - 8 * i) & 0xFF); return s; }
    static Key keyAt(const std::string& s, size_t off) { const size_t rem = s.size() - off; return rem <= 8 ? Key{sliceOf(s, off, rem), (int)rem} : Key{sliceOf(s, off, 8), 9}; }
    bool put(const std::string& key, int val) {                                                    // 새 키면 true
        bool added = putIn(*root, key, 0, val); count += added; return added;
    }
    static bool putIn(Layer& L, const std::string& key, size_t off, int val) {
        const Key k = keyAt(key, off); auto it = L.m.find(k);
        if (k.second <= 8) { const bool added = it == L.m.end(); Entry& e = L.m[k]; e.val = val; return added; }                      // 이 조각에서 끝나는 키
        if (it == L.m.end()) { Entry& e = L.m[k]; e.val = val; e.suffix = key.substr(off + 8); return true; }                       // 첫 키: 접미사를 항목에 단다(층을 만들지 않는다)
        Entry& e = it->second;
        if (e.link) return putIn(*e.next, key, off + 8, val);
        if (e.suffix == key.substr(off + 8)) { e.val = val; return false; }
        e.next.reset(new Layer); e.link = true;                                                                                       // 같은 조각으로 시작하는 키가 둘: 새 층을 만들고 둘 다 옮긴다
        putIn(*e.next, e.suffix, 0, e.val); e.suffix.clear(); return putIn(*e.next, key, off + 8, val);
    }
    const int* get(const std::string& key) const {
        const Layer* L = root.get(); size_t off = 0;
        for (;;) {
            const Key k = keyAt(key, off); auto it = L->m.find(k); if (it == L->m.end()) return nullptr;
            const Entry& e = it->second;
            if (k.second <= 8) return &e.val;
            if (e.link) { L = e.next.get(); off += 8; continue; }
            return e.suffix == key.substr(off + 8) ? &e.val : nullptr;
        }
    }
    bool erase(const std::string& key) { const bool r = eraseIn(*root, key, 0); count -= r; return r; }
    static bool eraseIn(Layer& L, const std::string& key, size_t off) {
        const Key k = keyAt(key, off); auto it = L.m.find(k); if (it == L.m.end()) return false;
        Entry& e = it->second;
        if (k.second <= 8) { L.m.erase(it); return true; }
        if (!e.link) { if (e.suffix != key.substr(off + 8)) return false; L.m.erase(it); return true; }
        if (!eraseIn(*e.next, key, off + 8)) return false;
        Layer& sub = *e.next;
        if (sub.m.empty()) { L.m.erase(it); return true; }
        if (sub.m.size() == 1) {                                                                                                      // 하위 층에 항목 하나: 부모의 접미사 항목으로 접어 올린다
            auto only = sub.m.begin(); Entry& o = only->second;
            if (!o.link) { std::string rest = o.suffix; if (only->first.second <= 8) rest = bytesOf(only->first.first, (size_t)only->first.second); else rest = bytesOf(only->first.first, 8) + o.suffix;
                int v = o.val; e.suffix = rest; e.val = v; e.link = false; e.next.reset(); }
        }
        return true;
    }
    static void scanIn(const Layer& L, const std::string& prefix, const std::string& from, size_t limit, std::vector<std::pair<std::string, int>>& out) {
        for (const auto& kv : L.m) {
            if (out.size() >= limit) return;
            const Entry& e = kv.second; const bool isLayer = kv.first.second == 9 && e.link;
            if (kv.first.second <= 8) { std::string key = prefix + bytesOf(kv.first.first, (size_t)kv.first.second); if (key >= from) out.push_back({key, e.val}); }
            else if (!e.link) { std::string key = prefix + bytesOf(kv.first.first, 8) + e.suffix; if (key >= from) out.push_back({key, e.val}); }
            else if (isLayer) { std::string base = prefix + bytesOf(kv.first.first, 8); if (base < from.substr(0, base.size())) continue; scanIn(*e.next, base, from, limit, out); }       // 부분 트리의 키는 모두 base 로 시작한다
        }
    }
    std::vector<std::pair<std::string, int>> scan(const std::string& from, size_t limit) const { std::vector<std::pair<std::string, int>> out; scanIn(*root, "", from, limit, out); return out; }
    static void shape(const Layer& L, std::string& s) {
        s += "{"; for (const auto& kv : L.m) { s += std::to_string(kv.first.first) + "/" + std::to_string(kv.first.second); const Entry& e = kv.second;
            if (e.link) shape(*e.next, s); else if (kv.first.second == 9) s += "~" + e.suffix; s += ":" + (e.link ? std::string() : std::to_string(e.val)) + ","; } s += "}";
    }
    std::string shape() const { std::string s; shape(*root, s); return s; }
    static int depth(const Layer& L) { int d = 1; for (const auto& kv : L.m) if (kv.second.link) d = std::max(d, 1 + depth(*kv.second.next)); return d; }
    int depth() const { return depth(*root); }
};
std::string randomKey(std::mt19937& rng) {
    static const std::vector<std::string> bases = {"", "abababab", "abababababababab", "aabbaabbaabbaabbaabb", "bbbbbbbbbbbbbbbbbbbbbbbb", std::string("ab\0ab\0ab\0ab\0ab\0", 15)};
    std::string k = bases[rng() % bases.size()]; const int extra = (int)(rng() % 12); for (int i = 0; i < extra; ++i) k += "ab\0"[rng() % 3];
    if (rng() % 4 == 0) k = k.substr(0, rng() % (k.size() + 1));                                                                       // 접두사 관계가 많이 생기게
    return k;
}

int main() {
    {   Masstree t; assert(t.put("hello", 1) && t.put("hello world, long key", 2) && t.put("hello world, long kex", 3) && !t.put("hello", 4));        // 손으로 확인
        assert(*t.get("hello") == 4 && *t.get("hello world, long key") == 2 && *t.get("hello world, long kex") == 3 && t.get("hello world") == nullptr && t.depth() == 3);   // "hello wo|rld, lon|g key" : 두 긴 키가 17 바이트까지 같아 층이 3 개
        auto all = t.scan("", 10); assert(all.size() == 3 && all[0].first == "hello" && all[1].first == "hello world, long kex" && all[2].first == "hello world, long key");      // 사전식 순서 (kex < key)
        assert(t.erase("hello world, long kex") && t.depth() == 1 && *t.get("hello world, long key") == 2); }                                                                 // 하나가 지워지면 층이 접혀 올라간다
    std::mt19937 rng(61); Masstree t; std::map<std::string, int> model; int maxDepth = 0;
    for (int step = 0; step < 50000; ++step) {
        const std::string k = randomKey(rng); const int op = (int)(rng() % 10);
        if (op < 5) { const int v = (int)rng(); const bool added = model.find(k) == model.end(); model[k] = v; assert(t.put(k, v) == added); }
        else if (op < 8) { const bool had = model.erase(k) > 0; assert(t.erase(k) == had); }
        else if (op < 9) { auto it = model.find(k); const int* g = t.get(k); assert((g != nullptr) == (it != model.end()) && (!g || *g == it->second)); }
        else { size_t lim = 1 + rng() % 12; auto got = t.scan(k, lim); std::vector<std::pair<std::string, int>> want; for (auto it = model.lower_bound(k); it != model.end() && want.size() < lim; ++it) want.push_back(*it); assert(got == want); }
        if (step % 2500 == 0) { assert(t.count == model.size()); maxDepth = std::max(maxDepth, t.depth()); }
    }
    assert(t.count == model.size() && maxDepth >= 3);
    auto full = t.scan("", model.size() + 1); assert((full == std::vector<std::pair<std::string, int>>(model.begin(), model.end())));          // 전체 순회 == 정렬된 모델
    std::vector<std::pair<std::string, int>> items(model.begin(), model.end()); std::shuffle(items.begin(), items.end(), rng);
    Masstree fresh; for (const auto& kv : items) fresh.put(kv.first, kv.second);
    assert(fresh.shape() == t.shape());                                                                                                    // 정규형: 이력과 무관하게 같은 키 집합이면 같은 층 구조
    std::cout << "Masstree: 50000 random put/erase/get/scan operations on short keys, 18-30 byte shared-prefix keys, prefix pairs and keys containing NUL matched std::map<string,int>; layer depth reached " << maxDepth << "; the layer structure after churn equalled a fresh build of the same " << model.size() << " keys" << std::endl;
    return 0;
}
// Time Complexity: 키 길이 L 바이트에 대해 O(L/8) 층 x 층당 O(log N) 정수 비교 (원래 구현은 B+-트리, 여기서는 std::map)
// Space Complexity: O(N·L) 최악, 접미사 달기로 층은 키 둘 이상이 8 바이트 조각을 공유할 때만 생긴다
```
# Part 9. 동시성
## LockFreeQueue()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <thread>
#include <vector>

// 락프리 큐(큐 관점의 요약, 정본은 Queue.md Part 10): Michael–Scott 큐. 더미 노드로 시작해 head 는 "마지막으로 꺼낸 노드", tail 은 "끝 근처" 를 가리킨다.
//  enqueue 는 tail 의 next 를 CAS 로 잇고 tail 을 밀며(다른 스레드가 밀다 만 것도 도와 준다 = helping), dequeue 는 head 를 CAS 로 전진시킨다. 잠금이 없어 한 스레드가 멈춰도 나머지가 진행한다.
//  노드는 *한 번 쓰고 다시 쓰지 않는* 풀에서 꺼낸다(인덱스 연결) — 그래서 ABA 도 회수 문제도 없다.  (노드를 재활용하는 구조는 이 Part 의 HazardPointer 항목과 LockFreeStack 의 태그 포인터.)
//  ① 단일 스레드: std::queue 와 무작위 연산 20 만 번 대조(빈 큐 dequeue 포함)  ② *helping*: 스레드 하나가 "next 를 잇고 tail 을 밀기 전에 멈춘" 상태를 결정적으로 만들고, 다음 스레드의 enqueue / dequeue 가 tail 을 대신 밀어 준 뒤 정상 진행함을 확인
//  ③ 다중 생산자·다중 소비자 4 × 4, 각 생산자 4 만 개: 모든 항목이 *정확히 한 번* 소비되고, 소비자마다 생산자별 순서가 보존(FIFO)된다.  ThreadSanitizer 로도 데이터 경쟁이 없다.
struct MSQueue {
    struct Node { int value; std::atomic<int> next; };
    std::vector<Node> pool; std::atomic<int> head, tail, allocated;
    explicit MSQueue(size_t capacity) : pool(capacity + 1), head(0), tail(0), allocated(1) { pool[0].value = 0; pool[0].next.store(-1); }
    int alloc() { int n = allocated.fetch_add(1); assert((size_t)n < pool.size()); return n; }
    void enqueue(int v, bool linkOnly = false) {                                                                   // linkOnly: 테스트용 — tail 을 밀지 않고 멈춘 스레드를 흉내낸다
        int n = alloc(); pool[n].value = v; pool[n].next.store(-1);
        for (;;) { int t = tail.load(); int nx = pool[t].next.load(); if (t != tail.load()) continue;
            if (nx == -1) { if (pool[t].next.compare_exchange_weak(nx, n)) { if (!linkOnly) tail.compare_exchange_strong(t, n); return; } }       // 끝에 잇는다
            else tail.compare_exchange_strong(t, nx); } }                                                           // tail 이 뒤처졌다: 도와서 민다
    bool dequeue(int& out) {
        for (;;) { int h = head.load(), t = tail.load(); int nx = pool[h].next.load(); if (h != head.load()) continue;
            if (nx == -1) return false;                                                                              // 비었다
            if (h == t) { tail.compare_exchange_strong(t, nx); continue; }                                           // tail 이 head 를 못 따라왔다: 도와서 민다
            int v = pool[nx].value; if (head.compare_exchange_weak(h, nx)) { out = v; return true; } } }
};

int main() {
    { MSQueue q(300000); std::queue<int> ref; std::mt19937 rng(163); int pushes = 0; for (int step = 0; step < 200000; ++step) { if (rng() % 100 < 55 && pushes < 290000) { int v = (int)(rng() % 1000000); q.enqueue(v); ref.push(v); ++pushes; } else { int out = -1; bool ok = q.dequeue(out); assert(ok == !ref.empty()); if (ok) { assert(out == ref.front()); ref.pop(); } } } }
    { MSQueue q(10); q.enqueue(1); q.enqueue(2, true);                                                              // ② 2 를 이었지만 tail 은 아직 1 번 노드를 가리킨다
      assert(q.pool[q.tail.load()].next.load() != -1);                                                              // tail 노드에 이미 다음 노드가 달려 있다 = tail 이 뒤처진 상태
      int out; q.enqueue(3);                                                                                         // 다른 스레드의 enqueue 가 tail 을 먼저 밀어 준 뒤 자기 노드를 잇는다
      assert(q.pool[q.tail.load()].next.load() == -1);
      assert(q.dequeue(out) && out == 1 && q.dequeue(out) && out == 2 && q.dequeue(out) && out == 3 && !q.dequeue(out));
      MSQueue r(10); r.enqueue(7, true); assert(r.tail.load() == 0 && r.pool[0].next.load() == 1); int v; assert(r.dequeue(v) && v == 7);                    // tail 이 head(더미) 에 머문 채 dequeue 가 tail 을 밀어 주고 값을 돌려준다
      assert(r.tail.load() == 1 && r.head.load() == 1); }
    { const int P = 4, C = 4, K = 40000; MSQueue q((size_t)P * K); std::vector<std::atomic<int>> seen((size_t)P * K); for (auto& s : seen) s.store(0); std::atomic<int> consumed(0); std::vector<std::vector<int>> got(C);
      std::vector<std::thread> th; for (int p = 0; p < P; ++p) th.emplace_back([&, p] { for (int s = 0; s < K; ++s) q.enqueue(p * K + s); });
      for (int c = 0; c < C; ++c) th.emplace_back([&, c] { while (consumed.load() < P * K) { int v; if (q.dequeue(v)) { got[c].push_back(v); seen[v].fetch_add(1); consumed.fetch_add(1); } else std::this_thread::yield(); } });
      for (auto& t : th) t.join();
      for (int v = 0; v < P * K; ++v) assert(seen[v].load() == 1);                                                  // 정확히 한 번
      for (int c = 0; c < C; ++c) { std::vector<int> last(P, -1); for (int v : got[c]) { int p = v / K, s = v % K; assert(s > last[p]); last[p] = s; } }          // 소비자마다 생산자별 FIFO
      std::cout << "LockFreeQueue: Michael-Scott queue matched std::queue over 2*10^5 single-thread operations, a stalled enqueuer's lagging tail was repaired by helping, and 4 producers x 4 consumers moved " << P * K << " items exactly once with per-producer FIFO order" << std::endl; }
    return 0;
}
// Time Complexity: enqueue·dequeue 락프리 (경쟁 없을 때 O(1))
// Space Complexity: O(N) 노드 풀 (재활용 없음)
```
## LockFreeStack()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <thread>
#include <vector>

// 락프리 스택(스택 관점의 요약, 정본은 Stack.md Part 9): Treiber 스택. top 포인터 하나를 CAS 로 바꾼다 — push 는 "새 노드의 next 를 현재 top 으로 두고 top 을 새 노드로", pop 은 "top 을 top->next 로".
//  주의: pop 중 다른 스레드가 같은 주소의 노드를 해제·재할당·재삽입하면 CAS 가 성공해 버리는 ABA 문제가 있다.  해법 하나는 (태그, 인덱스)를 64 비트에 묶어 CAS 때마다 태그를 올리는 것이다 — 같은 노드가 돌아와도 태그가 달라 CAS 가 실패한다.
//  ① ABA 를 *결정적으로* 재현: 스레드 1 이 top = A, next = B 를 읽고 멈춘 사이 스레드 2 가 A, B 를 pop 하고 A 를 다시 push 하는 일정을 손으로 짜 — 태그 없는 스택은 CAS 가 성공해 이미 꺼낸 B 가 부활하고 A 가 사라지며, 태그 스택은 CAS 가 실패해 재시도한다
//  ② 단일 스레드 대조(std::vector) 20 만 번  ③ 노드를 풀로 *재활용*(자유 목록도 같은 태그 스택)하는 4 스레드 × 5 만 번 push/pop 스트레스: 넣은 값의 다중 집합 = 꺼낸 값의 다중 집합, 최종 스택이 비어 있다.  TSan 무결.
struct TaggedStack {
    struct Cell { int value; std::atomic<int> next; };
    std::vector<Cell>& pool; std::atomic<uint64_t> head;                                                          // 상위 32 비트 = 태그, 하위 32 비트 = 인덱스 + 1 (0 = 빈 스택)
    explicit TaggedStack(std::vector<Cell>& p) : pool(p), head(0) {}
    static int idx(uint64_t h) { return (int)(uint32_t)h - 1; }
    static uint32_t tag(uint64_t h) { return (uint32_t)(h >> 32); }
    static uint64_t pack(uint32_t t, int i) { return ((uint64_t)t << 32) | (uint32_t)(i + 1); }
    void push(int n) { uint64_t h = head.load(); do { pool[n].next.store(idx(h), std::memory_order_relaxed); } while (!head.compare_exchange_weak(h, pack(tag(h) + 1, n))); }
    int pop() { uint64_t h = head.load(); for (;;) { int top = idx(h); if (top < 0) return -1; int nx = pool[top].next.load(std::memory_order_relaxed); if (head.compare_exchange_weak(h, pack(tag(h) + 1, nx))) return top; } }
};
struct LockFreeStack {
    std::vector<TaggedStack::Cell> pool; TaggedStack used, freeList;
    explicit LockFreeStack(size_t capacity) : pool(capacity), used(pool), freeList(pool) { for (size_t i = 0; i < capacity; ++i) { pool[i].value = 0; pool[i].next.store(-1); freeList.push((int)i); } }
    bool push(int v) { int n = freeList.pop(); if (n < 0) return false; pool[n].value = v; used.push(n); return true; }
    bool pop(int& out) { int n = used.pop(); if (n < 0) return false; out = pool[n].value; freeList.push(n); return true; }
};

int main() {
    {   // ① ABA 재현: 노드 1(A) → 2(B) → 3(C).  untagged: top 만 비교, tagged: (tag, top) 비교
        int next[4] = {0, 2, 3, -1}; int top = 1;                                                                  // 태그 없는 스택 (노드 번호 1..3, next = −1 이 끝)
        int t1Top = top, t1Next = next[t1Top];                                                                    // 스레드 1: top = 1, next = 2 를 읽고 멈춤
        int p1 = top; top = next[p1]; int p2 = top; top = next[p2];                                               // 스레드 2: pop → 1, pop → 2
        next[p1] = top; top = p1;                                                                                 // 스레드 2: 노드 1 을 다시 push (next = 3)
        assert(top == 1 && next[1] == 3);                                                                         // 현재 스택: 1 → 3  (노드 2 는 스레드 2 가 갖고 있다)
        bool casOk = (top == t1Top); if (casOk) top = t1Next;                                                     // 스레드 1 의 CAS(top: 1 → 2): 태그가 없어 성공!
        assert(casOk && top == 2);                                                                                // 이미 꺼낸 노드 2 가 스택의 top 으로 부활했고, 노드 3 은 2 를 통해서만 닿으며 노드 1 은 사라졌다
        std::vector<int> reach; for (int u = top; u != -1; u = next[u]) reach.push_back(u); assert(reach == (std::vector<int>{2, 3}));   // 노드 1 이 유실됨

        uint64_t head = ((uint64_t)0 << 32) | 2; int nx2[4] = {0, 2, 3, -1};                                      // 태그 스택: 상위 = 태그, 하위 = 인덱스 + 1
        auto idxOf = [](uint64_t h) { return (int)(uint32_t)h - 1; }; auto tagOf = [](uint64_t h) { return (uint32_t)(h >> 32); }; auto pk = [](uint32_t t, int i) { return ((uint64_t)t << 32) | (uint32_t)(i + 1); };
        uint64_t seen = head; int seenNext = nx2[idxOf(seen)];                                                    // 스레드 1: (tag 0, 노드 1), next = 2
        int a = idxOf(head); head = pk(tagOf(head) + 1, nx2[a]); int b = idxOf(head); head = pk(tagOf(head) + 1, nx2[b]);          // 스레드 2: pop, pop (태그 올라감)
        nx2[a] = idxOf(head); head = pk(tagOf(head) + 1, a);                                                      // 노드 1 을 다시 push (태그 또 올라감)
        bool casTagged = (head == seen); assert(idxOf(head) == idxOf(seen) && !casTagged);                       // 같은 노드가 top 이어도 태그가 달라 CAS 실패 → 재시도
        (void)seenNext; (void)b; }                                                                                      // (seenNext 는 CAS 가 성공했을 때 쓰일 값)
    {   LockFreeStack s(1000); std::vector<int> ref; std::mt19937 rng(167); for (int step = 0; step < 200000; ++step) { if (rng() % 2) { int v = (int)(rng() % 100000); bool ok = s.push(v); assert(ok == (ref.size() < 1000)); if (ok) ref.push_back(v); } else { int out = -1; bool ok = s.pop(out); assert(ok == !ref.empty()); if (ok) { assert(out == ref.back()); ref.pop_back(); } } } }          // ②
    {   const int T = 4, K = 50000; LockFreeStack s(64); std::vector<std::atomic<int>> pushed(T * K), popped(T * K); for (auto& x : pushed) x.store(0); for (auto& x : popped) x.store(0); std::vector<std::thread> th;
        for (int t = 0; t < T; ++t) th.emplace_back([&, t] { for (int i = 0; i < K; ++i) { int v = t * K + i; while (!s.push(v)) { int out; if (s.pop(out)) popped[out].fetch_add(1); } pushed[v].fetch_add(1); if (i % 3 == 2) { int out; if (s.pop(out)) popped[out].fetch_add(1); } } });
        for (auto& t : th) t.join(); int out; while (s.pop(out)) popped[out].fetch_add(1);
        for (int v = 0; v < T * K; ++v) assert(pushed[v].load() == 1 && popped[v].load() == 1);                    // ③ 모든 값이 정확히 한 번 꺼내졌다 (노드 재활용 중에도)
        assert(!s.pop(out));
        std::cout << "LockFreeStack: the ABA schedule corrupted the untagged stack (node 1 lost, popped node 2 resurrected) while the tagged stack's CAS failed, and 4 threads recycling a 64-cell pool pushed and popped " << T * K << " values exactly once each" << std::endl; }
    return 0;
}
// Time Complexity: push·pop 락프리 (경쟁 없을 때 O(1))
// Space Complexity: O(N) 고정 풀 (노드 재활용, 태그로 ABA 방지)
```
## ConcurrentHashMap()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <map>
#include <mutex>
#include <numeric>
#include <random>
#include <thread>
#include <unordered_map>
#include <vector>

// 동시 해시 맵(해시 관점의 요약, 정본은 Hash.md Part 12): 하나의 큰 잠금 대신 키의 해시로 고른 "조각(shard)" 마다 잠금을 따로 두면(lock striping) 서로 다른 조각을 쓰는 스레드끼리는 부딪히지 않는다.
//  Java 의 ConcurrentHashMap, Go 의 sync.Map 샤딩 구현이 이 아이디어 위에 있다.  연산: put / get / erase 와 *원자적 갱신* compute(key, f)(조각 잠금 안에서 읽고-계산하고-쓰므로 합산 같은 갱신을 잃지 않는다).
//  전체를 보는 연산(size, snapshot)은 조각 잠금을 *항상 같은 순서(0..S−1)*로 잡아 교착을 피한다.
//  ① 단일 스레드 대조: std::unordered_map 과 무작위 연산 20 만 번  ② 8 스레드 × 5 만 번 compute(+1) 이 겹치는 키에서도 합계가 정확 — 최종 값 = 스레드별 결정적 열의 단일 스레드 재생  ③ put/erase/get 이 섞인 스트레스 중에 size() 와 snapshot() 을 계속 호출해도 교착이 없고, 마지막 스냅샷 = 모형
//  ④ 조각 분포: 키 10^5 개가 64 조각에 고르게 퍼진다 (최대 조각 ≤ 평균의 1.2 배).  TSan 무결.
template <class K, class V> struct ShardedMap {
    struct Shard { std::mutex m; std::unordered_map<K, V> map; };
    std::vector<Shard> shards; std::hash<K> hasher;
    explicit ShardedMap(size_t n) : shards(n) {}
    size_t shardOf(const K& k) const { uint64_t x = (uint64_t)hasher(k); x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; return (size_t)(x % shards.size()); }       // 해시를 한 번 더 섞어 조각 번호를 고른다
    void put(const K& k, const V& v) { Shard& s = shards[shardOf(k)]; std::lock_guard<std::mutex> g(s.m); s.map[k] = v; }
    bool get(const K& k, V& out) { Shard& s = shards[shardOf(k)]; std::lock_guard<std::mutex> g(s.m); auto it = s.map.find(k); if (it == s.map.end()) return false; out = it->second; return true; }
    bool erase(const K& k) { Shard& s = shards[shardOf(k)]; std::lock_guard<std::mutex> g(s.m); return s.map.erase(k) > 0; }
    template <class F> void compute(const K& k, F f) { Shard& s = shards[shardOf(k)]; std::lock_guard<std::mutex> g(s.m); auto it = s.map.find(k); if (it == s.map.end()) s.map[k] = f(V()); else it->second = f(it->second); }          // 원자적 읽기-갱신
    size_t size() { size_t n = 0; for (auto& s : shards) { std::lock_guard<std::mutex> g(s.m); n += s.map.size(); } return n; }
    std::map<K, V> snapshot() { std::vector<std::unique_lock<std::mutex>> locks; for (auto& s : shards) locks.emplace_back(s.m); std::map<K, V> out; for (auto& s : shards) out.insert(s.map.begin(), s.map.end()); return out; }              // 모든 조각을 번호순으로 잠근 일관된 스냅샷
};

int main() {
    { ShardedMap<int, int> m(8); std::unordered_map<int, int> ref; std::mt19937 rng(173); for (int step = 0; step < 200000; ++step) { int k = (int)(rng() % 3000), op = (int)(rng() % 4);
        if (op == 0) { int v = (int)rng(); m.put(k, v); ref[k] = v; } else if (op == 1) { assert(m.erase(k) == (ref.erase(k) > 0)); } else if (op == 2) { m.compute(k, [](int v) { return v + 1; }); ref[k] = (ref.count(k) ? ref[k] : 0) + 1; } else { int v; bool ok = m.get(k, v); assert(ok == (ref.count(k) > 0) && (!ok || v == ref[k])); } } assert(m.size() == ref.size()); }          // ①
    {   const int T = 8, K = 50000, KEYS = 997; ShardedMap<int, long> m(16); std::vector<std::thread> th; for (int t = 0; t < T; ++t) th.emplace_back([&, t] { std::mt19937 rng(1000 + t); for (int i = 0; i < K; ++i) m.compute((int)(rng() % KEYS), [](long v) { return v + 1; }); });
        for (auto& t : th) t.join(); std::map<int, long> expect; for (int t = 0; t < T; ++t) { std::mt19937 rng(1000 + t); for (int i = 0; i < K; ++i) ++expect[(int)(rng() % KEYS)]; } assert(m.snapshot() == expect);                              // ② 단일 스레드 재생과 같다
        long total = 0; for (auto& kv : m.snapshot()) total += kv.second; assert(total == (long)T * K); }
    {   ShardedMap<int, int> m(8); std::atomic<bool> stop(false); std::atomic<long> snaps(0); std::vector<std::thread> th;                                                            // ③ put/erase/get + size()/snapshot() 동시에
        for (int t = 0; t < 4; ++t) th.emplace_back([&, t] { for (int i = 0; i < 40000; ++i) { int k = t * 100000 + i % 5000; if (i % 3 == 2) m.erase(k); else m.put(k, i); int v; m.get(k, v); } });
        std::thread watcher([&] { while (!stop.load()) { size_t n = m.size(); auto snap = m.snapshot(); assert(snap.size() <= 20000 && n <= 20000); snaps.fetch_add(1); std::this_thread::yield(); } });
        for (auto& t : th) t.join(); stop.store(true); watcher.join(); assert(snaps.load() > 0);
        std::map<int, int> expect; for (int t = 0; t < 4; ++t) for (int i = 0; i < 40000; ++i) { int k = t * 100000 + i % 5000; if (i % 3 == 2) expect.erase(k); else expect[k] = i; } assert(m.snapshot() == expect); }
    {   ShardedMap<int, int> m(64); for (int k = 0; k < 100000; ++k) m.put(k, k); size_t mx = 0; for (auto& s : m.shards) mx = std::max(mx, s.map.size()); assert(m.size() == 100000 && mx <= (size_t)(1.2 * 100000 / 64));                      // ④ 조각 분포
      std::cout << "ConcurrentHashMap: 2*10^5 single-thread operations matched std::unordered_map, 8 threads x 5*10^4 overlapping atomic compute() updates equalled their single-thread replay, size()/snapshot() ran concurrently with writers without deadlock, and 10^5 keys spread over 64 shards with a largest shard of " << mx << " (mean 1563)" << std::endl; }
    return 0;
}
// Time Complexity: 평균 O(1) (조각 잠금 구간), size·snapshot 은 O(S + N)
// Space Complexity: O(N + S)
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
    ~SkipSet() { N* x = head; while (x) { N* nx = x->nx[0]; delete x; x = nx; } }
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
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <thread>
#include <vector>

// 비교-교환(CAS, 메모리 관점의 요약, 정본은 Memory.md Part 11): "값이 기대한 것과 같을 때만 새 값으로 바꾸고 성공 여부를 돌려준다" 를 한 번의 원자적 명령으로 수행한다. 모든 락프리 구조의 기본 블록이다.
//  실패하면 현재 값이 expected 에 되돌려 담기므로 "읽기 → 계산 → CAS, 실패 시 반복" 루프를 만든다.  이 틀로 fetch_add 가 제공하지 않는 연산 — 최댓값 갱신, 곱셈, 포화(상한) 카운터, 스핀락 — 을 락 없이 만든다.
//  ① 의미: 성공하면 값이 바뀌고, 실패하면 expected 가 현재 값으로 갱신된다 (단일 스레드에서 결정적으로 확인)  ② "읽고-쓰기" 를 비원자적으로 하면 갱신을 잃는다 — 일정을 손으로 짜 재현하고 CAS 는 그 일정에서 실패해 재시도함을 확인 (최댓값 갱신도 같다: 읽은 뒤 끼어든 다른 갱신이 더 큰 값을 넣어도 덮어쓰지 않는다 — 읽기와 CAS 사이에 훅을 끼워 일정을 고정)
//  ③ 8 스레드 × 10 만 번: CAS 최댓값 = 전체 최댓값, CAS 곱셈 = 3^(총 횟수) mod 2^64, 포화 카운터 = min(총 횟수, 상한), CAS 스핀락으로 지킨 비원자 카운터 = 총 횟수 (TSan 무결)  ④ 포화 카운터의 성공 횟수는 정확히 상한(500000)이고 총 연산 800000 중 나머지는 상한에서 거절되며, 실패한 CAS 는 재시도일 뿐 성공 횟수에 들어가지 않는다.
// audit: stress (보존 법칙이 오라클: 최댓값 = 전체 최댓값, 곱 = 3^(총 횟수) mod 2^64, 포화 카운터 = min(총 횟수, 상한), 스핀락 보호 카운터 = 총 횟수)
template <class T, class H> T atomicMaxHook(std::atomic<T>& a, T v, long& retries, H afterRead) { T cur = a.load(); afterRead(); while (cur < v && !a.compare_exchange_weak(cur, v)) { ++retries; afterRead(); } return cur; }   // 실패하면 cur 가 현재 값으로 바뀌어 다시 비교 (afterRead: 읽기와 CAS 사이에 일정을 끼워 넣는 시험용 훅)
template <class T> T atomicMax(std::atomic<T>& a, T v, long& retries) { return atomicMaxHook(a, v, retries, [] {}); }
void atomicMulMod(std::atomic<uint64_t>& a, uint64_t m, long& retries) { uint64_t cur = a.load(); while (!a.compare_exchange_weak(cur, cur * m)) ++retries; }                                    // mod 2^64 곱셈
bool saturatingInc(std::atomic<int>& a, int limit, long& retries) { int cur = a.load(); while (cur < limit) { if (a.compare_exchange_weak(cur, cur + 1)) return true; ++retries; } return false; }
struct SpinLock { std::atomic<int> flag{0}; void lock() { int expected = 0; while (!flag.compare_exchange_weak(expected, 1, std::memory_order_acquire)) { expected = 0; std::this_thread::yield(); } } void unlock() { flag.store(0, std::memory_order_release); } };

int main() {
    { std::atomic<int> a(5); int expected = 3; bool ok = a.compare_exchange_strong(expected, 9); assert(!ok && expected == 5 && a.load() == 5);                      // ① 실패: 값 그대로, expected 는 현재 값(5)
      ok = a.compare_exchange_strong(expected, 9); assert(ok && a.load() == 9 && expected == 5); }                                                                      // 성공: 값 교체
    {   // ② 갱신 손실: 두 스레드가 x = 0 을 읽고 각자 +1 을 쓴다
        int x = 0; int r1 = x, r2 = x; x = r1 + 1; x = r2 + 1; assert(x == 1);                                                                                          // 비원자적: 갱신 하나가 사라졌다
        std::atomic<int> y(0); int e1 = y.load(), e2 = y.load(); bool c1 = y.compare_exchange_strong(e1, e1 + 1); bool c2 = y.compare_exchange_strong(e2, e2 + 1);        // 같은 일정에서 CAS: 두 번째는 실패
        assert(c1 && !c2 && e2 == 1 && y.load() == 1); bool c3 = y.compare_exchange_strong(e2, e2 + 1); assert(c3 && y.load() == 2); }                                 // e2 가 최신 값(1)으로 갱신되어 재시도하면 성공
    {   // ② 최댓값: A(5)가 0 을 읽은 직후 B(9)가 끼어들어 끝까지 실행된다 — 읽은 값(0)을 믿고 5 를 쓰면 최댓값 9 를 덮어쓴다 (확인-후-저장 구현은 여기서 5 가 된다)
        std::atomic<int> m(0); long rA = 0, rB = 0; bool injected = false; atomicMaxHook(m, 5, rA, [&] { if (!injected) { injected = true; atomicMax(m, 9, rB); } });
        assert(m.load() == 9 && rA >= 1);                                                                                                            // A 의 CAS 는 실패해(9 != 0) 현재 값 9 를 보고 그만둔다
        std::atomic<int> n2(0); long rC = 0, rD = 0; bool inj2 = false; atomicMaxHook(n2, 9, rC, [&] { if (!inj2) { inj2 = true; atomicMax(n2, 5, rD); } });   // 반대 순서: 작은 값이 먼저 들어가면 큰 값은 재시도로 이긴다
        assert(n2.load() == 9 && rC >= 1); }
    const int T = 8, K = 100000;
    std::atomic<int> maxV(-1); std::atomic<uint64_t> prod(1); std::atomic<int> sat(0); std::atomic<long> mulRetries(0), maxRetries(0), satRetries(0), satOk(0); SpinLock lock; long guarded = 0;
    std::vector<int> best(T, -1); std::vector<std::thread> th;
    for (int t = 0; t < T; ++t) th.emplace_back([&, t] { long r1 = 0, r2 = 0, r3 = 0; long ok = 0; uint64_t x = 88172645463325252ULL + 7919ULL * (uint64_t)t; int mine = -1;
        for (int i = 0; i < K; ++i) { x ^= x << 13; x ^= x >> 7; x ^= x << 17; int v = (int)(x % 1000003); mine = std::max(mine, v); atomicMax(maxV, v, r1); atomicMulMod(prod, 3, r2); ok += saturatingInc(sat, 500000, r3); lock.lock(); ++guarded; lock.unlock(); }
        best[t] = mine; maxRetries += r1; mulRetries += r2; satRetries += r3; satOk += ok; });
    for (auto& t : th) t.join();
    uint64_t pw = 1; for (int i = 0; i < T * K; ++i) pw *= 3;                                                                                                          // 3^(총 횟수) mod 2^64
    assert(maxV.load() == *std::max_element(best.begin(), best.end()) && prod.load() == pw && sat.load() == 500000 && satOk.load() == 500000 && guarded == (long)T * K);                 // ③ ④
    std::cout << "CompareAndSwap: failed CASes refreshed the expected value, the lost-update schedule was reproduced and repaired by CAS (also for max with a hand-scheduled interleaving), and 8 threads x 10^5 operations produced the exact atomic max, the exact product 3^" << T * K << " mod 2^64, a counter saturating at exactly 500000 (" << satOk.load() << " successes, " << satRetries.load() << " retries) and a spin-lock-protected total of " << guarded << std::endl;
    return 0;
}
// Time Complexity: 경쟁 없을 때 연산당 O(1), 경쟁이 있으면 재시도 (락프리: 시스템 전체로는 진행)
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
// audit: exhaustive (모델 검사 부분은 두 스레드의 모든 인터리빙을 전수 탐색, 실제 스레드 부분은 합계·할당=해제 보존 법칙)
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

//  모델 검사(모든 스케줄 전수): 스택 1→2→3 에서 스레드 A 는 pop 한 번, 스레드 B 는 pop 두 번(각 pop 뒤 retire·scan)을 *명령 단위*(top 읽기 / 위험 공시 / 재검증 / t->next 읽기 / CAS / 위험 해제 / scan)로 쪼개 두 스레드의 모든 인터리빙을 DFS 로 훑는다.
//  모드 0 = 보호 없음(scan 이 모두 해제), 1 = 공시만 하고 재검증 안 함, 2 = 공시 + 재검증(위의 프로토콜).  "해제된 노드의 next 를 읽는" 스케줄이 모드 0·1 에는 *존재* 하고 모드 2 에는 *하나도 없음* 을 보이며, 모든 스케줄에서 같은 노드를 두 스레드가 pop 하지 않는다.
struct MC {
    int mode; int next[4] = {0, 2, 3, 0}; bool freed[4] = {false, false, false, false}; int top = 1, hp[2] = {0, 0};
    int pc[2] = {0, 0}, t[2] = {0, 0}, nx[2] = {0, 0}, restarts[2] = {0, 0}, pops[2] = {0, 0}; std::vector<int> retiredList; bool uaf = false; std::vector<int> got[2];
    explicit MC(int m) : mode(m) {}
    void step(int x) {
        switch (pc[x]) {
            case 0: t[x] = top; pc[x] = t[x] == 0 ? 99 : (mode >= 1 ? 1 : 3); break;                                            // top 읽기 (빈 스택이면 끝)
            case 1: hp[x] = t[x]; pc[x] = mode >= 2 ? 2 : 3; break;                                                              // 위험 공시
            case 2: if (top != t[x]) pc[x] = ++restarts[x] > 1 ? 99 : 0; else pc[x] = 3; break;                                  // 재검증 실패면 처음부터
            case 3: if (freed[t[x]]) uaf = true; nx[x] = next[t[x]]; pc[x] = 4; break;                                         // t->next 읽기: 해제된 노드면 위반
            case 4: if (top == t[x]) { top = nx[x]; got[x].push_back(t[x]); pc[x] = 5; } else pc[x] = ++restarts[x] > 1 ? 99 : 0; break;   // CAS
            case 5: hp[x] = 0; if (x == 1) { retiredList.push_back(t[x]); pc[x] = 6; } else pc[x] = 99; break;                  // 위험 해제, B 는 retire
            default: { std::vector<int> keep; for (int n : retiredList) { if (mode >= 1 && (hp[0] == n || hp[1] == n)) keep.push_back(n); else freed[n] = true; } retiredList = keep; ++pops[x]; pc[x] = pops[x] < 2 ? 0 : 99; } }   // scan
    }
};
void explore(const MC& s, long& schedules, long& bad) {
    bool moved = false;
    for (int x = 0; x < 2; ++x) if (s.pc[x] != 99) { moved = true; MC c = s; c.step(x); explore(c, schedules, bad); }
    if (!moved) { ++schedules; if (s.uaf) ++bad; std::vector<int> all = s.got[0]; all.insert(all.end(), s.got[1].begin(), s.got[1].end()); std::sort(all.begin(), all.end()); assert(std::adjacent_find(all.begin(), all.end()) == all.end()); }   // 같은 노드를 두 번 pop 하지 않는다
}
int main() {
    {   long sch[3] = {0, 0, 0}, uaf[3] = {0, 0, 0}; for (int mode = 0; mode < 3; ++mode) { MC s(mode); explore(s, sch[mode], uaf[mode]); }
        assert(uaf[0] > 0 && uaf[1] > 0 && uaf[2] == 0 && sch[2] > 1000);                                                          // 보호 없음·재검증 없음은 위반이 있고, 프로토콜은 모든 스케줄에서 안전
        std::cout << "HazardPointer model check: " << sch[2] << " schedules, unsafe schedules without protection " << uaf[0] << ", without revalidation " << uaf[1] << ", with the full protocol " << uaf[2] << std::endl; }
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

## ChaseLevDeque()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>

// Chase–Lev 작업 훔치기 덱(Chase & Lev 2005, 메모리 순서는 Lê 등 2013): 작업 스레드 하나(소유자)가 자기 덱의 "아래(bottom)" 에서 push·pop 하고, 한가한 다른 스레드(도둑)가 "위(top)" 에서 steal 한다.
// 소유자는 LIFO(방금 만든 작업 = 캐시에 따뜻함), 도둑은 FIFO(가장 오래된 = 가장 큰 작업) 순서로 가져가므로 충돌이 드물다. 대부분의 경우 소유자는 원자 연산 없이(순서 지정 load·store 만으로) 동작하고,
// 남은 원소가 하나일 때만 소유자와 도둑이 top 에 대한 CAS 로 겨룬다. 배열이 차면 두 배로 키운다(옛 배열은 도둑이 아직 읽을 수 있어 덱이 사라질 때까지 보관). Cilk·Rayon·Java ForkJoinPool·Tokio 스케줄러의 핵심 부품이다.
// 검증: ① 단일 스레드: 소유자는 LIFO, 도둑은 FIFO, 빈 덱, 용량 증가 ② 소유자 1 + 도둑 3 스레드 스트레스: 작업 번호 1..N 이 정확히 한 번씩 실행(누락·중복 없음), 합이 같고 각 작업이 소유자 또는 도둑 중 한 곳에서만 나온다
template <class T> class ChaseLevDeque {
    struct Array { long cap, mask; std::unique_ptr<std::atomic<T>[]> slot; explicit Array(long c) : cap(c), mask(c - 1), slot(new std::atomic<T>[(size_t)c]) {}
        T get(long i) const { return slot[(size_t)(i & mask)].load(std::memory_order_relaxed); } void put(long i, T v) { slot[(size_t)(i & mask)].store(v, std::memory_order_relaxed); } };
    alignas(64) std::atomic<long> top_{0}; alignas(64) std::atomic<long> bottom_{0}; std::atomic<Array*> array_;
    std::vector<std::unique_ptr<Array>> arrays_;                                                   // 옛 배열도 소멸 때까지 보관
public:
    explicit ChaseLevDeque(long cap = 4) { arrays_.emplace_back(new Array(cap)); array_.store(arrays_.back().get(), std::memory_order_relaxed); }
    void push(T x) {                                                                               // 소유자만
        long b = bottom_.load(std::memory_order_relaxed), t = top_.load(std::memory_order_acquire); Array* a = array_.load(std::memory_order_relaxed);
        if (b - t > a->cap - 1) { Array* bigger = new Array(a->cap * 2); for (long i = t; i < b; ++i) bigger->put(i, a->get(i)); arrays_.emplace_back(bigger); array_.store(bigger, std::memory_order_release); a = bigger; }
        a->put(b, x); std::atomic_thread_fence(std::memory_order_release); bottom_.store(b + 1, std::memory_order_relaxed);
    }
    bool pop(T& out) {                                                                             // 소유자만: 아래에서 꺼낸다
        long b = bottom_.load(std::memory_order_relaxed) - 1; Array* a = array_.load(std::memory_order_relaxed); bottom_.store(b, std::memory_order_relaxed);
        std::atomic_thread_fence(std::memory_order_seq_cst); long t = top_.load(std::memory_order_relaxed);
        if (t > b) { bottom_.store(b + 1, std::memory_order_relaxed); return false; }              // 비어 있었다
        out = a->get(b);
        if (t == b) {                                                                              // 마지막 하나: 도둑과 top 을 놓고 겨룬다
            bool won = top_.compare_exchange_strong(t, t + 1, std::memory_order_seq_cst, std::memory_order_relaxed);
            bottom_.store(b + 1, std::memory_order_relaxed); return won;
        }
        return true;
    }
    bool steal(T& out) {                                                                           // 아무 스레드나: 위에서 가져간다 (실패해도 비었다는 뜻은 아님)
        long t = top_.load(std::memory_order_acquire); std::atomic_thread_fence(std::memory_order_seq_cst); long b = bottom_.load(std::memory_order_acquire);
        if (t >= b) return false;
        Array* a = array_.load(std::memory_order_acquire); T v = a->get(t);
        if (!top_.compare_exchange_strong(t, t + 1, std::memory_order_seq_cst, std::memory_order_relaxed)) return false;              // 다른 도둑·소유자가 먼저 가져갔다
        out = v; return true;
    }
    long capacity() const { return array_.load()->cap; }
    size_t grows() const { return arrays_.size() - 1; }
};

// audit: stress
int main() {
    {   ChaseLevDeque<int> d(4); int x; assert(!d.pop(x) && !d.steal(x));                          // 단일 스레드 의미: 소유자 LIFO, 도둑 FIFO, 증가
        for (int i = 1; i <= 10; ++i) d.push(i);
        assert(d.capacity() == 16 && d.grows() == 2);                                              // 4 -> 8 -> 16
        assert(d.steal(x) && x == 1 && d.steal(x) && x == 2 && d.pop(x) && x == 10 && d.pop(x) && x == 9);
        int rest = 0; while (d.pop(x)) rest += x; assert(rest == 3 + 4 + 5 + 6 + 7 + 8 && !d.pop(x) && !d.steal(x)); }
    const int N = 200000, THIEVES = 3; ChaseLevDeque<int> deque(8);
    std::vector<std::atomic<int>> ran((size_t)N + 1); for (auto& r : ran) r.store(0);
    std::atomic<bool> done{false}; std::atomic<long> stolen{0}, popped{0}, sum{0};
    std::vector<std::thread> thieves;
    for (int t = 0; t < THIEVES; ++t) thieves.emplace_back([&] { int x; long mine = 0; for (;;) { if (deque.steal(x)) { ran[(size_t)x].fetch_add(1); sum.fetch_add(x); ++mine; } else if (done.load()) { if (!deque.steal(x)) break; ran[(size_t)x].fetch_add(1); sum.fetch_add(x); ++mine; } else std::this_thread::yield(); } stolen.fetch_add(mine); });
    {   int x; long mine = 0; unsigned rng = 12345;                                                  // 소유자: 작업을 만들고(push), 가끔 직접 꺼내 실행(pop)
        for (int i = 1; i <= N; ++i) { deque.push(i); rng = rng * 1103515245u + 12345u; if ((rng >> 16) % 3 == 0 && deque.pop(x)) { ran[(size_t)x].fetch_add(1); sum.fetch_add(x); ++mine; } }
        while (deque.pop(x)) { ran[(size_t)x].fetch_add(1); sum.fetch_add(x); ++mine; }
        popped.store(mine); done.store(true); }
    for (auto& t : thieves) t.join();
    for (int i = 1; i <= N; ++i) assert(ran[(size_t)i].load() == 1);                               // 모든 작업이 정확히 한 번 실행됐다
    assert(sum.load() == (long)N * (N + 1) / 2 && stolen.load() + popped.load() == N);
    std::cout << "ChaseLevDeque: " << N << " tasks were each executed exactly once by 1 owner (popped " << popped.load() << ") and " << THIEVES << " thieves (stole " << stolen.load() << "); the deque grew " << deque.grows() << " times" << std::endl;
    return 0;
}
// Time Complexity: push·pop 상수(소유자, 대개 원자 연산 없음), steal 상수(CAS 한 번), 증가는 분할상환 O(1)
// Space Complexity: O(최대 원소 수) (옛 배열 합쳐 최대 2배)
```

## Disruptor()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>

// 디스럽터(LMAX Disruptor): 고정 크기(2 의 거듭제곱) 링 버퍼와 "순번(sequence)" 만으로 생산자와 소비자를 잇는 저지연 큐. 락도 노드 할당도 없다.
// 생산자는 순번 s 를 선점(claim)하고 슬롯 s & mask 에 쓴 뒤 발행(publish)한다. 소비자마다 자기가 처리한 마지막 순번을 기록하고, 모든 소비자의 최솟값보다 한 바퀴(size) 넘게 앞서지 못하게(gating) 생산자를 세운다.
// 소비자는 순번 s 가 발행되기를 기다렸다가 읽는다 — 모든 소비자가 모든 이벤트를 같은 순서로 받는다(방송). 다중 생산자는 순번을 fetch_add 로 나눠 갖고, 슬롯마다 "몇 번째 바퀴에 발행됐는가" 를 적어
// (availability 배열) 소비자가 빈틈(앞 순번이 아직 안 쓰인 경우)을 건너뛰지 않게 한다. 슬롯 쓰기 → 발행(release) → 소비자 읽기(acquire) → 소비 완료(release) → 생산자의 재사용(acquire) 이 해피닝 비포 사슬이라 데이터 경쟁이 없다.
// 검증: 생산자 3 x 이벤트 2 만 개를 크기 64(작은 링: 수백 번 되감김, 생산자가 자주 막힘)에 흘려 소비자 2 개가 각각 ① 6 만 개 모두 ② 순번 순서대로 ③ 생산자별 번호가 1 씩 증가(생산자 안 순서 보존, 누락·중복 없음) ④ 페이로드 검사합이 맞음(덮어쓰기 없음)
template <class T> class Disruptor {
    struct Cell { std::atomic<long> round{-1}; T value{}; };                                      // round: 이 슬롯에 마지막으로 발행된 바퀴 번호
    const long size_, mask_; std::unique_ptr<Cell[]> cells_; alignas(64) std::atomic<long> next_{0}; std::unique_ptr<std::atomic<long>[]> consumed_; int consumers_;
public:
    Disruptor(long size, int consumers) : size_(size), mask_(size - 1), cells_(new Cell[(size_t)size]), consumed_(new std::atomic<long>[(size_t)consumers]), consumers_(consumers) { for (int i = 0; i < consumers; ++i) consumed_[(size_t)i].store(-1); }
    long minConsumed() const { long m = consumed_[0].load(std::memory_order_acquire); for (int i = 1; i < consumers_; ++i) m = std::min(m, consumed_[(size_t)i].load(std::memory_order_acquire)); return m; }
    void publish(const T& v) {                                                                    // 생산자: 순번 선점 -> (가장 느린 소비자가 따라올 때까지) 대기 -> 쓰기 -> 발행
        const long s = next_.fetch_add(1, std::memory_order_relaxed);
        while (s - size_ > minConsumed()) std::this_thread::yield();                               // 한 바퀴 앞서면 아직 안 읽힌 슬롯을 덮어쓰게 된다
        Cell& c = cells_[(size_t)(s & mask_)]; c.value = v; c.round.store(s / size_, std::memory_order_release);
    }
    T consume(int id, long seq) {                                                                  // 소비자 id: 순번 seq 를 기다려 읽고 "처리 완료" 를 알린다
        Cell& c = cells_[(size_t)(seq & mask_)];
        while (c.round.load(std::memory_order_acquire) != seq / size_) std::this_thread::yield();
        T v = c.value; consumed_[(size_t)id].store(seq, std::memory_order_release); return v;
    }
};
struct Event { int producer; int counter; uint32_t check; };
uint32_t checksum(int p, int c) { return (uint32_t)p * 2654435761u ^ (uint32_t)c * 40503u; }

// audit: stress
int main() {
    const int P = 3, C = 2, PER = 20000; const long TOTAL = (long)P * PER;
    Disruptor<Event> ring(64, C); std::vector<std::thread> threads; std::atomic<long> okConsumers{0};
    for (int p = 0; p < P; ++p) threads.emplace_back([&, p] { for (int i = 0; i < PER; ++i) ring.publish(Event{p, i, checksum(p, i)}); });
    for (int c = 0; c < C; ++c) threads.emplace_back([&, c] {
        std::vector<int> last((size_t)P, -1); long good = 0;
        for (long s = 0; s < TOTAL; ++s) { Event e = ring.consume(c, s);
            if (e.check == checksum(e.producer, e.counter) && e.counter == last[(size_t)e.producer] + 1) { last[(size_t)e.producer] = e.counter; ++good; } }   // 페이로드 온전 + 생산자 안에서 번호가 1 씩 증가
        for (int p = 0; p < P; ++p) good += last[(size_t)p] == PER - 1;
        okConsumers.fetch_add(good == TOTAL + P ? 1 : 0); });
    for (auto& t : threads) t.join();
    assert(okConsumers.load() == C);                                                               // 두 소비자 모두 6 만 개를 빠짐없이·순서대로·온전히 받았다
    std::cout << "Disruptor: " << P << " producers published " << TOTAL << " events through a 64-slot ring (about " << TOTAL / 64 << " wrap-arounds); " << C << " consumers each received every event, in order per producer, with intact payloads" << std::endl;
    return 0;
}
// Time Complexity: publish·consume 상수(원자 연산 몇 번 + 대기), 대기는 가장 느린 소비자에 좌우
// Space Complexity: O(링 크기) 고정, 이벤트 할당 없음
```

## RCU()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

// RCU(Read-Copy-Update): 읽기가 압도적으로 많은 공유 자료구조에서 읽는 쪽에 락·원자 쓰기 경쟁을 전혀 두지 않는 동기화. 읽는 스레드는 read_lock ~ read_unlock 사이에서 포인터를 그냥 읽는다.
// 갱신자는 (Read) 현재 객체를 (Copy) 복사해 새 객체를 만들고 (Update) 포인터를 한 번에 바꿔 끼운다. 옛 객체를 읽고 있는 독자가 있을 수 있으므로 즉시 지우지 않고 synchronize() — "그 시점에 읽고 있던 독자가 모두 끝나기"
// (유예 기간, grace period) — 를 기다린 뒤에 지운다. 새로 들어온 독자는 이미 새 포인터를 보므로 기다릴 필요가 없다. 리눅스 커널 연결 리스트·라우팅 표, 사용자 공간 liburcu 가 쓰는 방식이다.
// 이 구현: 전역 시대(epoch) 카운터 + 독자별 칸. 독자는 칸에 현재 시대를 적고(seq_cst) 전역 시대가 그대로인지 다시 확인(적는 순간 갱신자가 시대를 올렸다면 다시 시도)한다. 갱신자는 시대를 올린 뒤
// "시대 값이 새 시대보다 작은 0 아닌 칸" — 즉 갱신 전에 들어와 아직 안 나간 독자 — 이 없어질 때까지 기다린다. 독자의 읽기가 끝나는 release 저장과 갱신자의 acquire 읽기가 옛 객체의 해제 앞에 순서를 만든다.
// 검증: 독자 4 x 무한 읽기, 갱신자 1 (3 천 번 교체): 독자가 본 객체는 항상 살아 있고(valid 표지) 내부가 일관(a == b) — 해제 직전 표지를 지우고 delete 하므로 너무 일찍 지우면 바로 걸린다(ASan 에서는 use-after-free).
//       할당 수 == 해제 수 + 1(마지막 객체) ③ 갱신자가 버전마다 독자의 읽기를 기다리므로 읽기와 교체가 실제로 겹친다
struct Rcu {
    static constexpr int MAXR = 16;
    struct alignas(64) Slot { std::atomic<unsigned long> epoch{0}; };                              // 0 = 읽는 중 아님, 그 외 = 들어올 때의 시대
    std::atomic<unsigned long> global{1}; Slot slots[MAXR]; std::mutex writers;
    void readLock(int id) { for (;;) { unsigned long e = global.load(); slots[id].epoch.store(e); if (global.load() == e) return; } }       // 시대를 적은 뒤에도 그대로인지 확인
    void readUnlock(int id) { slots[id].epoch.store(0, std::memory_order_release); }
    void synchronize() {                                                                           // 이 호출 전에 시작한 읽기 구간이 모두 끝날 때까지 기다린다
        std::lock_guard<std::mutex> g(writers); const unsigned long e = global.fetch_add(1) + 1;
        for (auto& s : slots) for (;;) { unsigned long c = s.epoch.load(std::memory_order_acquire); if (c == 0 || c >= e) break; std::this_thread::yield(); }
    }
};
struct Data { int a, b; int valid; };
std::atomic<long> allocated{0}, freed{0};
Data* make(int v) { ++allocated; return new Data{v, v, 1}; }

// audit: stress
int main() {
    Rcu rcu; std::atomic<Data*> shared{make(0)}; std::atomic<bool> stop{false}; std::atomic<long> bad{0}, reads{0}, versionChanges{0}, readsDone{0};
    const int R = 4, UPDATES = 3000; std::vector<std::thread> readers;
    for (int id = 0; id < R; ++id) readers.emplace_back([&, id] {
        int lastSeen = -1; long mine = 0, changes = 0;
        while (!stop.load()) {
            rcu.readLock(id); const Data* d = shared.load(std::memory_order_acquire);              // 읽기 구간: 락 없이 포인터를 따라간다
            if (d->valid != 1 || d->a != d->b) bad.fetch_add(1);
            const int v = d->a; rcu.readUnlock(id); ++mine; readsDone.fetch_add(1, std::memory_order_relaxed); if (v != lastSeen) { ++changes; lastSeen = v; }
            if (mine % 64 == 0) std::this_thread::yield();                                         // 코어 수보다 스레드가 많아도 갱신자가 굶지 않게
        }
        reads.fetch_add(mine); versionChanges.fetch_add(changes); });
    std::thread writer([&] { for (int i = 1; i <= UPDATES; ++i) {
        Data* fresh = make(i); Data* old = shared.exchange(fresh, std::memory_order_acq_rel);     // 복사본을 만들어 한 번에 교체
        rcu.synchronize();                                                                         // 옛 객체를 읽는 독자가 모두 나갈 때까지
        old->valid = 0; delete old; ++freed;
        while (readsDone.load(std::memory_order_relaxed) < 2L * i) std::this_thread::yield(); }       // 버전마다 독자가 평균 두 번은 읽도록 기다린다(독자와 갱신이 실제로 겹치게)
        stop.store(true); });
    writer.join(); for (auto& t : readers) t.join();
    delete shared.load(); ++freed;
    assert(bad.load() == 0 && allocated.load() == freed.load() && allocated.load() == UPDATES + 1);
    assert(reads.load() >= 2L * UPDATES);                                                          // 독자와 갱신이 실제로 겹쳤다(버전마다 평균 두 번 이상 읽힘)
    std::cout << "RCU: " << R << " lock-free readers performed " << reads.load() << " reads (" << versionChanges.load() << " version changes observed) while the writer replaced the object " << UPDATES << " times; no reader ever saw a freed or inconsistent object" << std::endl;
    return 0;
}
// Time Complexity: 읽기 O(1) (락 없음), synchronize O(독자 칸 수 + 가장 긴 읽기 구간)
// Space Complexity: O(독자 수) 칸 + 객체 (유예 기간 동안 옛 버전 하나가 더 산다)
```

## Seqlock()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

// 시퀀스 락(Seqlock): 읽기가 매우 많고 데이터가 작은 공유 값(시계, 통계 카운터, 설정값)을 위한 낙관적 락. 쓰는 쪽이 카운터 seq 를 홀수로 올리고(쓰는 중) 값을 쓰고 짝수로 올린다(끝남).
// 읽는 쪽은 락을 잡지 않는다: seq 를 읽어(짝수여야 한다) 값을 복사한 뒤 seq 를 다시 읽어 같으면 복사본이 쓰는 도중의 값이 섞이지 않은 온전한 스냅샷이고, 다르면 버리고 다시 읽는다.
// 읽기는 공유 변수에 쓰기를 하지 않아(캐시 줄을 빼앗지 않아) 읽는 코어 수에 따라 확장되지만, 쓰기가 잦으면 독자가 계속 재시도(굶음)한다. 리눅스 커널의 jiffies·시계(seqcount_t)가 이 방식이다.
// C++ 메모리 모델에서는 읽는 도중 쓰이는 일반 변수가 데이터 경쟁(정의되지 않은 동작)이므로 데이터를 원자 변수(relaxed)로 두고 seq 와 울타리(fence)로 순서를 만든다(Boehm 2012).
// 검증: 쓰는 스레드 2(뮤텍스로 직렬화) x 8 개 워드가 모두 같은 값 k 로 채워진 레코드 5 만 번 쓰기, 읽는 스레드 3 이 계속 읽는다: 읽은 레코드의 8 워드가 모두 같고(찢어진 읽기 없음) 값이 단조 증가, 재시도가 한 번이라도 있었는지 보고
//       손으로 확인: 쓰기 전후 seq 가 2 씩 오르고 읽기 중 홀수 seq 면 재시도
template <int N> class Seqlock {
    std::atomic<unsigned> seq_{0}; std::atomic<uint64_t> data_[N]; std::mutex writers_;
public:
    Seqlock() { for (auto& d : data_) d.store(0, std::memory_order_relaxed); }
    void write(const uint64_t (&v)[N]) {
        std::lock_guard<std::mutex> g(writers_);                                                   // 쓰는 쪽끼리는 직렬화 (seq 를 하나의 쓰기 스레드가 올린다는 가정)
        const unsigned s = seq_.load(std::memory_order_relaxed);
        seq_.store(s + 1, std::memory_order_relaxed);                                              // 홀수: 쓰는 중
        std::atomic_thread_fence(std::memory_order_release);                                       // 홀수 표시가 데이터 쓰기보다 먼저 보이게
        for (int i = 0; i < N; ++i) data_[i].store(v[i], std::memory_order_relaxed);
        seq_.store(s + 2, std::memory_order_release);                                              // 짝수: 끝
    }
    unsigned read(uint64_t (&out)[N]) const {                                                      // 재시도 횟수를 돌려준다
        unsigned retries = 0;
        for (;;) {
            const unsigned s0 = seq_.load(std::memory_order_acquire);
            if (s0 & 1) { ++retries; std::this_thread::yield(); continue; }                        // 쓰는 중
            for (int i = 0; i < N; ++i) out[i] = data_[i].load(std::memory_order_relaxed);
            std::atomic_thread_fence(std::memory_order_acquire);                                   // 데이터 읽기가 두 번째 seq 읽기보다 앞서게
            if (seq_.load(std::memory_order_relaxed) == s0) return retries;                        // 그동안 쓰기가 없었다: 온전한 스냅샷
            ++retries;
        }
    }
    unsigned sequence() const { return seq_.load(); }
};

// audit: stress
int main() {
    {   Seqlock<4> s; uint64_t in[4] = {7, 7, 7, 7}, out[4]; assert(s.sequence() == 0 && s.read(out) == 0 && out[0] == 0);   // 손으로 확인
        s.write(in); assert(s.sequence() == 2 && s.read(out) == 0 && out[0] == 7 && out[3] == 7); s.write(in); assert(s.sequence() == 4); }
    const int W = 2, R = 3, PER = 25000; Seqlock<8> lock; std::atomic<bool> stop{false}; std::atomic<long> torn{0}, nonMonotonic{0}, retries{0}, reads{0}, readsDone{0};
    std::vector<std::thread> threads; std::atomic<uint64_t> counter{0};
    for (int w = 0; w < W; ++w) threads.emplace_back([&] { for (int i = 0; i < PER; ++i) { while (readsDone.load(std::memory_order_relaxed) < i) std::this_thread::yield();      // 쓰기 i 번째까지 독자가 최소 i 번은 읽도록 기다려 읽기와 쓰기가 실제로 겹치게 한다
            static std::mutex m; std::lock_guard<std::mutex> g(m); const uint64_t k = ++counter; uint64_t rec[8]; for (auto& x : rec) x = k; lock.write(rec); } });
    for (int r = 0; r < R; ++r) threads.emplace_back([&] { uint64_t last = 0, out[8]; long mine = 0, re = 0;
        while (!stop.load()) { re += lock.read(out); ++mine; readsDone.fetch_add(1, std::memory_order_relaxed); for (int i = 1; i < 8; ++i) if (out[i] != out[0]) torn.fetch_add(1); if (out[0] < last) nonMonotonic.fetch_add(1); last = out[0]; if (mine % 64 == 0) std::this_thread::yield(); }
        retries.fetch_add(re); reads.fetch_add(mine); });
    for (int i = 0; i < W; ++i) threads[(size_t)i].join();
    stop.store(true); for (size_t i = W; i < threads.size(); ++i) threads[i].join();
    assert(reads.load() >= PER && torn.load() == 0 && nonMonotonic.load() == 0 && lock.sequence() == 2u * W * PER && counter.load() == (uint64_t)W * PER);
    std::cout << "Seqlock: " << reads.load() << " lock-free reads of an 8-word record during " << W * PER << " writes saw no torn record and no value going backwards (" << retries.load() << " retries)" << std::endl;
    return 0;
}
// Time Complexity: 읽기 O(N) 복사 + 재시도(쓰기와 겹칠 때), 쓰기 O(N)
// Space Complexity: O(N) + 카운터 하나
```

## EpochBasedReclamation()
### 대표코드
```cpp
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <thread>
#include <vector>

// 에포크 기반 회수(Epoch-Based Reclamation, EBR, Fraser 2004): 락 없는 자료구조에서 "지운 노드를 누가 아직 읽고 있을지 모르는" 문제(ABA·use-after-free)를 시대(epoch) 번호로 푼다.
// 스레드는 자료구조에 들어갈 때 enter() 로 현재 전역 시대를 칸에 적고 나올 때 leave() 한다. 지운 노드는 바로 free 하지 않고 현재 시대의 폐기 목록(limbo)에 넣는다.
// 모든 "들어와 있는" 스레드가 현재 시대를 본 뒤에만 전역 시대를 하나 올린다 → 시대 e 에 폐기한 노드는 시대가 e+2 가 되면, 폐기 시점에 들어와 있던 모든 스레드가 이미 한 번 나갔다 들어왔다는 뜻이므로
// 안전하게 free 한다(그래서 목록은 3 개를 돌려 쓴다). 위험 포인터(Hazard Pointer)와 달리 읽을 때마다 포인터를 등록하지 않아 읽기가 싸고, 대신 멈춘 스레드 하나가 시대 전진을 막아 메모리가 쌓일 수 있다.
// 이 구현은 스레드별 폐기 목록(소유 스레드만 만짐)과 전역 시대 CAS 를 쓰고, 트라이버 스택(Treiber stack)에 적용한다.
// 검증: 4 스레드가 각각 push 5 만 + pop 5 만(섞어서) 하는 락 없는 스택: ① 값 합 보존, 모든 노드가 정확히 한 번 해제(할당 수 == 해제 수) ② 시험 중 해제된 노드를 읽는 일 없음 — ASan 에서 use-after-free 가 없고,
//       해제 직전 노드에 독 값을 써 두므로 읽는 쪽이 독 값을 보면 단언이 걸린다 ③ 시대가 실제로 여러 번 전진했고 폐기 목록이 끝에서 비었다
struct Ebr {
    static constexpr int MAXT = 8; static constexpr unsigned long INACTIVE = ~0UL;
    struct alignas(64) Local { std::atomic<unsigned long> epoch{INACTIVE}; std::vector<void*> limbo[3]; unsigned retired = 0; };       // limbo: 이 스레드가 시대 mod 3 에 폐기한 노드
    std::atomic<unsigned long> global{0}; Local loc[MAXT]; void (*deleter)(void*); std::atomic<long> advances{0};
    explicit Ebr(void (*d)(void*)) : deleter(d) {}
    void enter(int t) { for (;;) { unsigned long e = global.load(); loc[t].epoch.store(e); if (global.load() == e) return; } }             // 시대를 적은 뒤에도 그대로인지 확인
    void leave(int t) { loc[t].epoch.store(INACTIVE, std::memory_order_release); }
    bool tryAdvance() {                                                                            // 들어와 있는 모든 스레드가 현재 시대를 봤다면 전역 시대를 올린다
        unsigned long e = global.load();
        for (auto& l : loc) { unsigned long le = l.epoch.load(); if (le != INACTIVE && le != e) return false; }
        if (global.compare_exchange_strong(e, e + 1)) { advances.fetch_add(1); return true; }
        return false;
    }
    void freeBucket(int t, int b) { for (void* p : loc[t].limbo[b]) deleter(p); loc[t].limbo[b].clear(); }
    void retire(int t, void* p) {                                                                  // 스레드 t 만 호출: 현재 시대의 목록에 넣고, 가끔 시대를 올려 두 시대 전 목록을 비운다
        unsigned long e = global.load(); loc[t].limbo[e % 3].push_back(p);
        if (++loc[t].retired % 32 == 0 && tryAdvance()) freeBucket(t, (int)((global.load() + 1) % 3));       // 새 시대 e' 에서 안전한 것: 시대 e'-2 에 폐기한 목록 = (e'+1) mod 3
    }
    void drainAll() { for (int t = 0; t < MAXT; ++t) for (int b = 0; b < 3; ++b) freeBucket(t, b); }      // 모든 스레드가 끝난 뒤
    size_t pending() const { size_t n = 0; for (const auto& l : loc) for (const auto& v : l.limbo) n += v.size(); return n; }
};
struct Node { int value; Node* next; int poison; };                                                // poison: 해제 직전 -1 로 바꾼다 (읽는 쪽이 보면 use-after-free)
std::atomic<long> allocated{0}, freed{0};
void deleteNode(void* p) { static_cast<Node*>(p)->poison = -1; ++freed; delete static_cast<Node*>(p); }
struct Stack {                                                                                     // 트라이버 스택 + EBR
    std::atomic<Node*> head{nullptr}; Ebr& ebr; std::atomic<long> poisoned{0};
    explicit Stack(Ebr& e) : ebr(e) {}
    void push(int t, int v) { ++allocated; Node* n = new Node{v, nullptr, 0}; ebr.enter(t); n->next = head.load(); while (!head.compare_exchange_weak(n->next, n)) {} ebr.leave(t); }
    bool pop(int t, int& out) {
        ebr.enter(t);
        for (;;) {
            Node* h = head.load(); if (!h) { ebr.leave(t); return false; }
            if (h->poison != 0) poisoned.fetch_add(1);                                            // 해제된 노드를 읽고 있다면 여기서 걸린다
            Node* nx = h->next;                                                                    // 보호 구간 안이라 h 가 지워졌더라도 메모리는 살아 있다
            if (head.compare_exchange_weak(h, nx)) { out = h->value; ebr.leave(t); ebr.retire(t, h); return true; }     // 뺀 노드는 바로 지우지 않고 폐기 목록으로
        }
    }
};

// audit: stress
int main() {
    Ebr ebr(deleteNode); Stack st(ebr); const int T = 4, N = 50000; std::atomic<long> pushed{0}, popped{0}; std::vector<std::thread> ts;
    for (int t = 0; t < T; ++t) ts.emplace_back([&, t] { long ps = 0, po = 0; unsigned rng = 77u + (unsigned)t;
        for (int i = 1; i <= N; ++i) { st.push(t, i); ps += i; rng = rng * 1664525u + 1013904223u; if (rng >> 31) { int v; if (st.pop(t, v)) po += v; } }
        int v; while (st.pop(t, v)) po += v; pushed.fetch_add(ps); popped.fetch_add(po); });
    for (auto& t : ts) t.join();
    int v; while (st.pop(0, v)) popped.fetch_add(v);                                               // 남은 것 비우기(혹시)
    const size_t pendingBefore = ebr.pending(); ebr.drainAll();
    assert(pushed.load() == popped.load() && st.poisoned.load() == 0);                              // 값 합 보존, 해제된 노드를 읽은 적 없음
    assert(allocated.load() == (long)T * N && freed.load() == allocated.load() && ebr.pending() == 0);   // 모든 노드가 정확히 한 번 해제
    assert(ebr.advances.load() > 10);                                                              // 시대가 실제로 여러 번 전진했다
    std::cout << "EpochBasedReclamation: " << T << " threads pushed/popped " << (long)T * N << " nodes through a lock-free stack; the global epoch advanced " << ebr.advances.load() << " times, " << pendingBefore << " nodes were still waiting in limbo at the end, and every node was freed exactly once without any read of freed memory" << std::endl;
    return 0;
}
// Time Complexity: enter·leave O(1), retire 분할상환 O(스레드 수) (시대 전진 검사 32 번에 한 번)
// Space Complexity: O(스레드 수 + 폐기 대기 노드) — 멈춘 스레드가 있으면 대기 노드가 무한히 쌓일 수 있다
```
# Part 10. 분산 시스템
## ConsistentHashing()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <vector>

// 일관된 해시(해시 관점의 요약, 정본은 Hash.md Part 7): 서버와 키를 같은 해시 링 위에 놓고 키는 시계 방향 첫 서버가 맡는다. 서버를 더하거나 빼도 이웃 구간의 키만 이동한다(평균 K/N 개) — "해시 % 서버 수" 는 서버 수가 바뀌면 거의 전부 이동한다.
//  서버당 가상 노드(vnode)를 여러 개 두면 부하가 고르게 퍼지고, 가중치 w 인 서버에 w 배의 가상 노드를 주면 부하가 가중치에 비례한다.  *한도 있는 부하*(bounded load, Mirrokni 등): 서버 용량을 ⌈(1+ε)·K/N⌉ 로 제한하고 가득 찬 서버는 건너뛰어 다음 서버로 보낸다.
//  ① 단조성(정확히): 서버를 더하면 옮겨 가는 키는 *전부 새 서버로* 가고 옛 서버끼리는 한 키도 바뀌지 않으며, 서버를 빼면 그 서버의 키만 옮겨 간다  ② 이동 비율이 이론값 1/(N+1) 에 근접 (vnode 200 개, 키 20 만)  ③ 균형: vnode 1 개는 최대 부하가 평균의 2 배를 넘고 200 개는 1.3 배 이내  ④ 가중치 비례  ⑤ 한도 있는 부하의 최대 부하 ≤ 용량  ⑥ 복제 r = 3 은 시계 방향의 *서로 다른* 서버 3 개  ⑦ 비교: hash % N 은 서버 하나를 더하면 N/(N+1) 의 키가 이동.
static uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }
struct Ring {
    std::vector<std::pair<uint64_t, int>> points;                                                                  // (링 위치, 서버 번호) 정렬
    void add(int server, int vnodes) { for (int v = 0; v < vnodes; ++v) points.push_back({mix(((uint64_t)server << 32) ^ (uint64_t)v ^ 0xABCDEF1234567ULL), server}); std::sort(points.begin(), points.end()); }
    void remove(int server) { points.erase(std::remove_if(points.begin(), points.end(), [&](const std::pair<uint64_t, int>& p) { return p.second == server; }), points.end()); }
    int owner(uint64_t key) const { uint64_t h = mix(key ^ 0x5555555555ULL); auto it = std::lower_bound(points.begin(), points.end(), std::make_pair(h, -1)); if (it == points.end()) it = points.begin(); return it->second; }       // 시계 방향 첫 서버 (끝에서 처음으로 돌아옴)
    std::vector<int> replicas(uint64_t key, int r) const { uint64_t h = mix(key ^ 0x5555555555ULL); size_t i = std::lower_bound(points.begin(), points.end(), std::make_pair(h, -1)) - points.begin(); std::vector<int> out; for (size_t step = 0; step < points.size() && (int)out.size() < r; ++step) { int s = points[(i + step) % points.size()].second; if (std::find(out.begin(), out.end(), s) == out.end()) out.push_back(s); } return out; }
    std::vector<int> assignBounded(const std::vector<uint64_t>& keys, int servers, double eps, std::vector<int>& load) const {              // 가득 찬 서버는 건너뛴다
        size_t cap = (size_t)std::ceil((1 + eps) * (double)keys.size() / servers); load.assign(servers, 0); std::vector<int> out; for (uint64_t key : keys) { uint64_t h = mix(key ^ 0x5555555555ULL); size_t i = std::lower_bound(points.begin(), points.end(), std::make_pair(h, -1)) - points.begin();
            for (size_t step = 0;; ++step) { int s = points[(i + step) % points.size()].second; if ((size_t)load[s] < cap) { ++load[s]; out.push_back(s); break; } } } return out; }
};

int main() {
    const int K = 200000; std::vector<uint64_t> keys(K); for (int i = 0; i < K; ++i) keys[i] = (uint64_t)i * 2654435761ULL + 12345;
    for (int N : {5, 10, 20, 40}) {
        Ring ring; for (int s = 0; s < N; ++s) ring.add(s, 200); std::vector<int> before(K); for (int i = 0; i < K; ++i) before[i] = ring.owner(keys[i]);
        ring.add(N, 200); int moved = 0; for (int i = 0; i < K; ++i) { int now = ring.owner(keys[i]); if (now != before[i]) { ++moved; assert(now == N); } }                  // ① 옮겨 간 키는 전부 새 서버로
        double frac = (double)moved / K, ideal = 1.0 / (N + 1); assert(std::fabs(frac - ideal) < 0.2 * ideal);                                                      // ② 이론값 근처
        int onNew = 0; for (int i = 0; i < K; ++i) onNew += ring.owner(keys[i]) == N; assert(onNew == moved);
        Ring after = ring; after.remove(N / 2); for (int i = 0; i < K; ++i) { int a = ring.owner(keys[i]), b = after.owner(keys[i]); if (a != N / 2) assert(a == b); else assert(b != N / 2); }         // 삭제는 그 서버의 키만 이동
        int modMoved = 0; for (int i = 0; i < K; ++i) modMoved += (mix(keys[i]) % N) != (mix(keys[i]) % (N + 1)); assert((double)modMoved / K > 0.7 * N / (N + 1));                                  // ⑦ hash % N
    }
    for (int vn : {1, 200}) { Ring ring; const int N = 20; for (int s = 0; s < N; ++s) ring.add(s, vn); std::vector<int> load(N, 0); for (uint64_t k : keys) ++load[ring.owner(k)]; double mean = (double)K / N; int mx = *std::max_element(load.begin(), load.end());      // ③
        if (vn == 1) assert(mx > 2 * mean); else assert(mx < 1.3 * mean); }
    { Ring ring; const int N = 6; const int w[N] = {1, 2, 3, 4, 5, 6}; int totalW = 21; for (int s = 0; s < N; ++s) ring.add(s, 100 * w[s]); std::vector<int> load(N, 0); for (uint64_t k : keys) ++load[ring.owner(k)]; for (int s = 0; s < N; ++s) assert(std::fabs(load[s] - (double)K * w[s] / totalW) < 0.15 * K * w[s] / totalW); }     // ④ 가중치
    { Ring ring; const int N = 20; for (int s = 0; s < N; ++s) ring.add(s, 100); std::vector<int> load; ring.assignBounded(keys, N, 0.1, load); size_t cap = (size_t)std::ceil(1.1 * K / N); int sum = 0, mx = 0; for (int x : load) { sum += x; mx = std::max(mx, x); } assert(sum == K && (size_t)mx <= cap);                  // ⑤
      for (int i = 0; i < 2000; ++i) { auto r = ring.replicas(keys[i], 3); assert(r.size() == 3 && std::set<int>(r.begin(), r.end()).size() == 3 && r[0] == ring.owner(keys[i])); }                          // ⑥
      std::cout << "ConsistentHashing: adding a server moved keys only onto the new server (about 1/(N+1) of them for N=5..40, within 20%), removing one moved only its own keys, max load stayed within 1.3x the mean with 200 vnodes (vs >2x with one), weighted loads were proportional, bounded loads respected the capacity " << cap << ", and replicas were 3 distinct servers" << std::endl; }
    return 0;
}
// Time Complexity: 조회 O(log (N·V)) (이분 탐색), 서버 추가·삭제 O(V log (N·V))
// Space Complexity: O(N · V)
```
## DistributedHashTable()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>

// 분산 해시 테이블(DHT, 해시 관점의 요약, Chord·Kademlia 는 Hash.md Part 7): 중앙 서버 없이 키 → 값 저장을 노드들이 나눠 맡는다. 핵심은 (1) 키와 노드가 같은 식별자 공간에 놓이고
//  (2) 각 키는 "식별자가 가장 가까운" 노드들이 맡으며 (3) 복제(replication)로 노드 하나가 죽어도 값이 남는다는 것.  여기서는 Chord 식 링을 직접 만든다: 식별자 2^24, 노드 i 는 finger[j] = successor(id + 2^j) 를 안다.
//  라우팅: 키를 넘지 않는 가장 먼 finger 로 점프(closest preceding finger) — 홉 수 O(log N).  복제: 키를 맡은 노드와 그 뒤 R − 1 개 후속 노드가 사본을 가진다.  repair() 는 죽은 노드를 링에서 빼고 사본을 R 개로 다시 채운다.
//  ① N = 1, 2, 3, 16, 100, 1000, 3000 에서 라우팅이 모든 (시작 노드, 키) 쌍에서 후속자 이분 탐색(오라클)과 같고 평균 홉 수 ≤ 0.6·log2(N) + 1, 최대 ≤ 2·⌈log2 N⌉ + 2  ② 키 2 만 개 put/get 전부 성공, 사본 수 = R·K
//  ③ 노드를 20% 확률로 죽이면 사본이 모두 죽은 키만 유실 — 유실 수는 독립 계산과 정확히 같고, 100 번의 무작위 실패 평균 유실률이 p^R 과 표준오차의 4 배 이내로 일치  ④ repair() 후 살아남은 키는 사본 R 개를 회복해 두 번째 실패 라운드에서도 유실률이 다시 ≈ p^R (누적되지 않음)  ⑤ 새 노드 합류: 옮겨 가는 키는 정확히 (선행자, 새 id] 구간.
struct Chord {
    static const int M = 24; static const uint32_t SPACE = 1u << M; int R;
    std::vector<uint32_t> ids; std::vector<std::array<int, M>> finger; std::vector<std::unordered_map<uint32_t, int>> store; std::vector<char> alive;
    explicit Chord(int r) : R(r) {}
    int succIndex(uint32_t key) const { size_t i = std::lower_bound(ids.begin(), ids.end(), key) - ids.begin(); return (int)(i % ids.size()); }
    void rebuild() { int n = (int)ids.size(); finger.assign(n, {}); for (int i = 0; i < n; ++i) for (int j = 0; j < M; ++j) finger[i][j] = succIndex((ids[i] + (1u << j)) % SPACE); }
    void setNodes(std::vector<uint32_t> v) { ids = std::move(v); std::sort(ids.begin(), ids.end()); ids.erase(std::unique(ids.begin(), ids.end()), ids.end()); store.assign(ids.size(), {}); alive.assign(ids.size(), 1); rebuild(); }
    static bool inHalfOpen(uint32_t x, uint32_t a, uint32_t b) { return a < b ? (x > a && x <= b) : (x > a || x <= b); }                       // x ∈ (a, b] (원형)
    static bool inOpen(uint32_t x, uint32_t a, uint32_t b) { return a < b ? (x > a && x < b) : (x > a || x < b); }                           // x ∈ (a, b)
    int route(int start, uint32_t key, int& hops) const {
        int n = (int)ids.size(); int cur = start; hops = 0; if (n == 1) return 0;
        for (;;) { int succ = (cur + 1) % n; if (inHalfOpen(key, ids[cur], ids[succ])) return succ;                                            // 담당 노드는 cur 의 후속자
            int next = cur; for (int j = M - 1; j >= 0; --j) { int f = finger[cur][j]; if (inOpen(ids[f], ids[cur], key)) { next = f; break; } } if (next == cur) return succ; cur = next; ++hops; } }
    std::vector<int> replicaNodes(uint32_t key) const { int n = (int)ids.size(), o = succIndex(key); std::vector<int> r; for (int i = 0; i < std::min(R, n); ++i) r.push_back((o + i) % n); return r; }
    void put(uint32_t key, int value) { for (int node : replicaNodes(key)) store[node][key] = value; }
    bool get(uint32_t key, int& value) const { for (int node : replicaNodes(key)) if (alive[node]) { auto it = store[node].find(key); if (it != store[node].end()) { value = it->second; return true; } } return false; }
    void repair() {                                                                                              // 죽은 노드를 링에서 빼고 사본을 다시 R 개로 채운다
        std::unordered_map<uint32_t, int> survivors; std::vector<uint32_t> live; for (size_t i = 0; i < ids.size(); ++i) if (alive[i]) { live.push_back(ids[i]); for (auto& kv : store[i]) survivors[kv.first] = kv.second; }
        ids.clear(); setNodes(live); for (auto& kv : survivors) put(kv.first, kv.second); }
};

int main() {
    std::mt19937 rng(179);
    for (int N : {1, 2, 3, 16, 100, 1000, 3000}) {                                                               // ①
        Chord c(3); std::vector<uint32_t> v; while ((int)v.size() < N) v.push_back((uint32_t)(rng() % Chord::SPACE)); c.setNodes(v); N = (int)c.ids.size(); long totalHops = 0; int maxHops = 0; const int Q = 20000;
        for (int q = 0; q < Q; ++q) { int start = (int)(rng() % N); uint32_t key = (uint32_t)(rng() % Chord::SPACE); int hops; int got = c.route(start, key, hops); assert(got == c.succIndex(key)); totalHops += hops; maxHops = std::max(maxHops, hops); }
        double lg = N > 1 ? std::log2((double)N) : 0; assert((double)totalHops / Q <= 0.6 * lg + 1 && maxHops <= 2 * (int)std::ceil(lg) + 2);
        if (N == 3000 || N == 1000) std::cout << "DistributedHashTable: Chord routing on N=" << N << " nodes took " << (double)totalHops / Q << " hops on average (max " << maxHops << ", log2 N = " << lg << "); "; }
    const int K = 20000, R = 3; Chord dht(R); { std::vector<uint32_t> v; for (int i = 0; i < 500; ++i) v.push_back((uint32_t)(rng() % Chord::SPACE)); dht.setNodes(v); }
    std::vector<uint32_t> keys(K); for (int i = 0; i < K; ++i) { keys[i] = (uint32_t)(rng() % Chord::SPACE); dht.put(keys[i], i); }
    { size_t copies = 0; for (auto& s : dht.store) copies += s.size(); std::set<uint32_t> distinct(keys.begin(), keys.end()); assert(copies == (size_t)R * distinct.size()); for (int i = 0; i < K; ++i) { int v; bool ok = dht.get(keys[i], v); assert(ok); } }                          // ②
    const double p = 0.2; std::vector<double> losses; const int PATTERNS = 100;
    for (int pat = 0; pat < PATTERNS; ++pat) { std::fill(dht.alive.begin(), dht.alive.end(), 1); for (size_t i = 0; i < dht.alive.size(); ++i) if ((double)(rng() % 1000000) / 1e6 < p) dht.alive[i] = 0; long lost = 0;
        for (int i = 0; i < K; ++i) { int v; bool ok = dht.get(keys[i], v); bool oracle = false; for (int node : dht.replicaNodes(keys[i])) oracle |= dht.alive[node] != 0; assert(ok == oracle); lost += !ok; } losses.push_back((double)lost / K); }
    { double mean = 0, var = 0; for (double x : losses) mean += x; mean /= PATTERNS; for (double x : losses) var += (x - mean) * (x - mean); var /= (PATTERNS - 1); double se = std::sqrt(var / PATTERNS); assert(std::fabs(mean - std::pow(p, R)) < 4 * se); }          // ③ 평균 유실률 ≈ p^R (0.008): 표준오차의 4 배 이내
    std::fill(dht.alive.begin(), dht.alive.end(), 1); for (size_t i = 0; i < dht.alive.size(); ++i) if ((double)(rng() % 1000000) / 1e6 < p) dht.alive[i] = 0;
    dht.repair(); size_t alive1 = dht.ids.size(); std::set<uint32_t> survivors; for (auto& s : dht.store) for (auto& kv : s) survivors.insert(kv.first); size_t copies = 0; for (auto& s : dht.store) copies += s.size(); assert(copies == (size_t)R * survivors.size());                    // ④ 사본 R 개 회복
    std::fill(dht.alive.begin(), dht.alive.end(), 1); for (size_t i = 0; i < dht.alive.size(); ++i) if ((double)(rng() % 1000000) / 1e6 < p) dht.alive[i] = 0; long lost2 = 0; for (uint32_t k : survivors) { int v; lost2 += !dht.get(k, v); } assert((double)lost2 / (double)survivors.size() < 3 * std::pow(p, R));
    { Chord c(R); std::vector<uint32_t> v; for (int i = 0; i < 200; ++i) v.push_back((uint32_t)(rng() % Chord::SPACE)); c.setNodes(v); std::vector<uint32_t> ks(20000); std::vector<uint32_t> ownerId(ks.size()); for (size_t i = 0; i < ks.size(); ++i) { ks[i] = (uint32_t)(rng() % Chord::SPACE); ownerId[i] = c.ids[c.succIndex(ks[i])]; }
      uint32_t nid; do { nid = (uint32_t)(rng() % Chord::SPACE); } while (std::binary_search(c.ids.begin(), c.ids.end(), nid)); std::vector<uint32_t> v2 = c.ids; v2.push_back(nid); Chord d(R); d.setNodes(v2); size_t pi = std::lower_bound(d.ids.begin(), d.ids.end(), nid) - d.ids.begin(); uint32_t pred = d.ids[(pi + d.ids.size() - 1) % d.ids.size()];
      int movedCount = 0; for (size_t i = 0; i < ks.size(); ++i) { uint32_t now = d.ids[d.succIndex(ks[i])]; bool inRange = Chord::inHalfOpen(ks[i], pred, nid); assert((now != ownerId[i]) == inRange && (!inRange || now == nid)); movedCount += inRange; }
      std::cout << "after 20% node failures " << alive1 << " live nodes remained, repair restored " << R << " copies of all " << survivors.size() << " surviving keys, and a joining node took over exactly the " << movedCount << " keys in (predecessor, id]" << std::endl; }       // ⑤
    return 0;
}
// Time Complexity: 라우팅 O(log N) 홉, put/get O(log N + R)
// Space Complexity: 노드당 finger 24 개 + 맡은 키
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
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 머클 트리(트리 관점의 요약, 정본은 Tree.md Part 16): 잎 = 데이터 블록의 해시, 부모 = 두 자식 해시의 해시. 루트 하나로 전체를 요약하고, 한 블록의 진위는 루트까지의 형제 해시 ⌈log2 N⌉ 개(감사 경로)로 확인한다.
//  분산 시스템에서는 두 복제본의 루트가 같으면 같고, 다르면 서브트리를 비교해 어긴 블록만 찾아 동기화한다 (Cassandra anti-entropy, Git, 블록체인).  여기서는 64 비트 비암호학적 믹서로 *구조와 알고리즘*을 보이고(암호학적 SHA-256 판은 Tree.md), RFC 6962 의 규칙을 따른다:
//  잎 해시와 내부 해시에 서로 다른 접두 바이트(도메인 분리)를 쓰고, n 개를 *가장 큰 2 의 거듭제곱 k < n* 에서 갈라 왼쪽 k 개·오른쪽 n−k 개로 묶는다 — 홀수 개에서 마지막을 복제하는 비트코인 식 규칙과 달리 [a,b,c] 와 [a,b,c,c] 의 루트가 *다르다*.
//  ① n = 1..130 의 모든 잎에서 감사 경로가 길이 ≤ ⌈log2 n⌉ 로 검증되고, 데이터나 (경로 길이가 달라지는) 크기가 틀리면 실패  ② 작은 트리에서 *모든 잎의 모든 한 비트 변조*가 루트를 바꾼다  ③ 복제 규칙: 비트코인 식은 [a,b,c] = [a,b,c,c] 로 루트가 같아 변이 공격이 가능, RFC 식은 다르다
//  ④ 차이 찾기: n = 10^5 에서 잎 k 개만 다른 두 트리를 위에서부터 비교해 정확히 그 잎들을 찾고 해시 비교 수 ≤ 2k(⌈log2 n⌉ + 1) + 1.
static uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }
uint64_t leafHash(const std::string& d) { uint64_t h = 0x0000000000000000ULL ^ 0x6C6561665F5F5F5FULL; for (unsigned char c : d) h = mix(h ^ c); return mix(h ^ d.size()); }                      // 접두 0x00: 잎
uint64_t nodeHash(uint64_t l, uint64_t r) { return mix(mix(l ^ 0x6E6F64655F5F5F5FULL) + r * 0xD6E8FEB86659FD93ULL + 1); }                                                                     // 접두 0x01: 내부 (비대칭)
size_t splitPoint(size_t n) { size_t k = 1; while (k * 2 < n) k *= 2; return k; }                                                                                                              // n 보다 작은 가장 큰 2 의 거듭제곱
struct Merkle {
    struct Node { size_t lo, hi; uint64_t hash; int l = -1, r = -1; }; std::vector<Node> nodes; int root = -1; size_t n = 0;
    explicit Merkle(const std::vector<std::string>& data) : n(data.size()) { std::vector<uint64_t> lh(n); for (size_t i = 0; i < n; ++i) lh[i] = leafHash(data[i]); if (n) root = build(lh, 0, n); }
    int build(const std::vector<uint64_t>& lh, size_t lo, size_t hi) { Node nd; nd.lo = lo; nd.hi = hi; if (hi - lo == 1) { nd.hash = lh[lo]; nodes.push_back(nd); return (int)nodes.size() - 1; } size_t k = splitPoint(hi - lo); nd.l = build(lh, lo, lo + k); nd.r = build(lh, lo + k, hi); nd.hash = nodeHash(nodes[nd.l].hash, nodes[nd.r].hash); nodes.push_back(nd); return (int)nodes.size() - 1; }
    uint64_t rootHash() const { return nodes[root].hash; }
    std::vector<uint64_t> proof(size_t m) const { std::vector<uint64_t> p; int cur = root; std::vector<uint64_t> top; while (nodes[cur].l >= 0) { const Node& nd = nodes[cur]; if (m < nodes[nd.l].hi) { top.push_back(nodes[nd.r].hash); cur = nd.l; } else { top.push_back(nodes[nd.l].hash); cur = nd.r; } } p.assign(top.rbegin(), top.rend()); return p; }          // 잎 쪽 형제가 앞
    static uint64_t rebuild(uint64_t leaf, size_t m, size_t n, const std::vector<uint64_t>& p, size_t& pos, bool& ok) {
        if (n == 1) return leaf; if (pos == 0) { ok = false; return 0; } size_t k = splitPoint(n); uint64_t sib = p[--pos];
        if (m < k) { uint64_t left = rebuild(leaf, m, k, p, pos, ok); return nodeHash(left, sib); } uint64_t right = rebuild(leaf, m - k, n - k, p, pos, ok); return nodeHash(sib, right); }
    static bool verify(uint64_t rootH, const std::string& data, size_t m, size_t n, const std::vector<uint64_t>& p) { if (m >= n) return false; size_t pos = p.size(); bool ok = true; uint64_t h = rebuild(leafHash(data), m, n, p, pos, ok); return ok && pos == 0 && h == rootH; }
    static void diff(const Merkle& a, const Merkle& b, int x, int y, std::vector<size_t>& out, long& cmps) { ++cmps; if (a.nodes[x].hash == b.nodes[y].hash) return; if (a.nodes[x].l < 0) { out.push_back(a.nodes[x].lo); return; } diff(a, b, a.nodes[x].l, b.nodes[y].l, out, cmps); diff(a, b, a.nodes[x].r, b.nodes[y].r, out, cmps); }
};
size_t pathLength(size_t m, size_t n) { size_t len = 0; while (n > 1) { size_t k = splitPoint(n); if (m < k) n = k; else { m -= k; n -= k; } ++len; } return len; }
uint64_t bitcoinRoot(std::vector<uint64_t> level) { while (level.size() > 1) { if (level.size() % 2) level.push_back(level.back()); std::vector<uint64_t> up; for (size_t i = 0; i < level.size(); i += 2) up.push_back(nodeHash(level[i], level[i + 1])); level = up; } return level[0]; }

int main() {
    for (size_t n = 1; n <= 130; ++n) { std::vector<std::string> d(n); for (size_t i = 0; i < n; ++i) d[i] = "block-" + std::to_string(i * 7919 % 1009); Merkle t(d);
        size_t lg = 0; while ((1ULL << lg) < n) ++lg;
        for (size_t m = 0; m < n; ++m) { auto p = t.proof(m); assert(p.size() <= lg && Merkle::verify(t.rootHash(), d[m], m, n, p));                                          // ① 검증 성공
            assert(!Merkle::verify(t.rootHash(), d[m] + "x", m, n, p));                                                                                                                            // 데이터가 틀리면 실패
            if (pathLength(m, n + 7) != p.size()) assert(!Merkle::verify(t.rootHash(), d[m], m, n + 7, p));                                                                              // 경로 길이가 맞지 않는 크기는 실패
            if (n > 1) { size_t other = (m + 1) % n; if (d[other] != d[m]) assert(!Merkle::verify(t.rootHash(), d[m], other, n, p)); } } }
    for (size_t n : {1, 2, 3, 5, 8, 13}) { std::vector<std::string> d(n); for (size_t i = 0; i < n; ++i) d[i] = "ab" + std::to_string(i) + "cd"; uint64_t base = Merkle(d).rootHash();                                              // ② 모든 한 비트 변조
        for (size_t i = 0; i < n; ++i) for (size_t byte = 0; byte < d[i].size(); ++byte) for (int bit = 0; bit < 8; ++bit) { std::vector<std::string> e = d; e[i][byte] = (char)(e[i][byte] ^ (1 << bit)); assert(Merkle(e).rootHash() != base); } }
    { std::vector<std::string> abc = {"a", "b", "c"}, abcc = {"a", "b", "c", "c"}; std::vector<uint64_t> l3, l4; for (auto& s : abc) l3.push_back(leafHash(s)); for (auto& s : abcc) l4.push_back(leafHash(s));                                    // ③
      assert(bitcoinRoot(l3) == bitcoinRoot(l4)); assert(Merkle(abc).rootHash() != Merkle(abcc).rootHash()); assert(nodeHash(1, 2) != nodeHash(2, 1) && leafHash("x") != nodeHash(leafHash("x"), leafHash("x"))); }
    { const size_t n = 100000; std::mt19937 rng(181); std::vector<std::string> a(n); for (size_t i = 0; i < n; ++i) a[i] = "row" + std::to_string(i); std::vector<std::string> b = a; std::set<size_t> changed; while (changed.size() < 5) changed.insert(rng() % n); for (size_t i : changed) b[i] += "!";
      Merkle ta(a), tb(b); std::vector<size_t> found; long cmps = 0; Merkle::diff(ta, tb, ta.root, tb.root, found, cmps); std::sort(found.begin(), found.end()); assert(found == std::vector<size_t>(changed.begin(), changed.end()));              // ④
      size_t lg = 0; while ((1ULL << lg) < n) ++lg; assert(cmps <= 2 * 5 * (long)(lg + 1) + 1); auto p = ta.proof(54321); assert(p.size() <= lg && Merkle::verify(ta.rootHash(), a[54321], 54321, n, p) && !Merkle::verify(tb.rootHash(), a[54321], 54321, n, p));              // 감사 경로는 자기 트리의 루트에서만 통한다
      std::cout << "MerkleTree: audit paths verified for every leaf of trees with 1..130 leaves (and failed for altered data, a wrong index, or a size that changes the path length), every single-bit change altered the root, the Bitcoin-style duplicate rule gave [a,b,c] and [a,b,c,c] the same root while the RFC 6962 rule did not, and two 10^5-leaf trees differing in 5 leaves were diffed with " << cmps << " hash comparisons" << std::endl; }
    return 0;
}
// Time Complexity: 구축 O(N), 감사 경로 생성·검증 O(log N), 차이 찾기 O(k log N)
// Space Complexity: O(N)
```
## MerklePatriciaTrie()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <string>
#include <vector>

// 머클 패트리샤 트라이(Merkle Patricia Trie, 이더리움의 상태 저장 구조): 키를 니블(4 비트)로 쪼갠 16진 패트리샤 트라이에 "노드 해시" 를 얹어, 뿌리 해시 하나가 전체 내용을 대표하게 한다.
// 패트리샤(경로 압축): 잎(남은 경로, 값), 확장(공통 경로, 자식 하나), 가지(16 갈래 + 이 자리에서 끝나는 값) 세 종류. 노드 해시 = SHA-256(노드의 직렬화), 부모는 자식의 해시를 담는다 → 한 키를 바꾸면 경로 위의 해시만 다시 계산하고 뿌리 해시가 달라진다.
// 구조가 키 집합만으로 정해지므로(삽입·삭제 순서 무관) 두 쪽이 뿌리 해시 하나만 비교하면 내용이 같은지 안다. 증명(proof): 뿌리에서 키까지의 노드 직렬화 목록만 주면, 받는 쪽이 뿌리 해시부터 해시를 따라 내려가며
// 값이 있음(포함 증명) 또는 없음(비포함 증명)을 전체 트리 없이 확인한다. 경로 길이만큼 O(키 길이) 크기다. 영속(불변 노드, 경로 복사)이라 옛 뿌리 해시로 옛 상태도 증명할 수 있다.
// 직렬화는 이더리움의 RLP/Keccak 이 아니라 이 항목이 정한 단순한 형식이다(SHA-256 은 직접 구현, 공개 시험 벡터로 검증). 노드 인라인(32 바이트 미만) 최적화는 생략했다.
// 검증: ① SHA-256 공개 시험 벡터(빈 문자열·abc·두 블록·백만 개의 a) ② 무작위 삽입·덮어쓰기·삭제를 std::map 과 대조, 같은 내용을 다른 순서로 만든 트리의 뿌리 해시 동일, 내용이 다르면 해시도 다름
//       ③ 모든 키의 포함 증명·없는 키의 비포함 증명이 검증되고, 증명의 한 바이트라도 바꾸거나 다른 뿌리 해시로 검증하면 실패 ④ 옛 뿌리 해시로 옛 값을 증명
typedef std::array<uint8_t, 32> Hash;
Hash sha256(const std::string& msg) {
    static const uint32_t K[64] = {0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
    uint32_t h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    std::string m = msg; m += (char)0x80; while (m.size() % 64 != 56) m += (char)0; const uint64_t bits = (uint64_t)msg.size() * 8; for (int i = 7; i >= 0; --i) m += (char)(bits >> (8 * i) & 0xFF);
    auto rotr = [](uint32_t x, int n) { return x >> n | x << (32 - n); };
    for (size_t off = 0; off < m.size(); off += 64) {
        uint32_t w[64]; for (int i = 0; i < 16; ++i) w[i] = (uint32_t)(uint8_t)m[off + 4 * (size_t)i] << 24 | (uint32_t)(uint8_t)m[off + 4 * (size_t)i + 1] << 16 | (uint32_t)(uint8_t)m[off + 4 * (size_t)i + 2] << 8 | (uint32_t)(uint8_t)m[off + 4 * (size_t)i + 3];
        for (int i = 16; i < 64; ++i) { uint32_t s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3), s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10); w[i] = w[i - 16] + s0 + w[i - 7] + s1; }
        uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
        for (int i = 0; i < 64; ++i) { uint32_t S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25), ch = (e & f) ^ (~e & g), t1 = hh + S1 + ch + K[i] + w[i], S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22), mj = (a & b) ^ (a & c) ^ (b & c), t2 = S0 + mj;
            hh = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2; }
        h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
    }
    Hash out; for (int i = 0; i < 8; ++i) for (int j = 0; j < 4; ++j) out[(size_t)(4 * i + j)] = (uint8_t)(h[i] >> (24 - 8 * j) & 0xFF); return out;
}
std::string hex(const Hash& h) { static const char* d = "0123456789abcdef"; std::string s; for (uint8_t b : h) { s += d[b >> 4]; s += d[b & 15]; } return s; }
typedef std::vector<uint8_t> Nib;
Nib nibbles(const std::string& key) { Nib n; for (unsigned char c : key) { n.push_back(c >> 4); n.push_back(c & 15); } return n; }
struct Node; typedef std::shared_ptr<const Node> NP;
struct Node {
    enum Kind { LEAF, EXT, BRANCH } kind = LEAF; Nib path; std::string value; bool hasValue = false; NP child; NP kids[16]; std::string enc; Hash hash{};
    static std::string h32(const NP& n) { return n ? std::string((const char*)n->hash.data(), 32) : std::string(32, '\0'); }
    void seal() {                                                                                  // 직렬화 enc 를 만들고 그 SHA-256 을 hash 에 둔다
        enc.clear(); enc += (char)kind;
        if (kind != BRANCH) { enc += (char)path.size(); for (uint8_t x : path) enc += (char)x; }
        if (kind == LEAF) { enc += std::to_string(value.size()) + ":" + value; }
        else if (kind == EXT) enc += h32(child);
        else { for (const NP& k : kids) enc += h32(k); enc += hasValue ? '1' : '0'; if (hasValue) enc += std::to_string(value.size()) + ":" + value; }
        hash = sha256(enc);
    }
};
NP leaf(Nib p, std::string v) { auto n = std::make_shared<Node>(); n->kind = Node::LEAF; n->path = std::move(p); n->value = std::move(v); n->hasValue = true; n->seal(); return n; }
NP ext(Nib p, NP c) { auto n = std::make_shared<Node>(); n->kind = Node::EXT; n->path = std::move(p); n->child = std::move(c); n->seal(); return n; }
NP withPrefix(Nib pre, const NP& n);                                                              // 자식 n 앞에 경로 pre 를 붙인 노드(경로 압축 유지)
NP branch(const std::array<NP, 16>& kids, bool hasV, const std::string& v) { auto n = std::make_shared<Node>(); n->kind = Node::BRANCH; for (int i = 0; i < 16; ++i) n->kids[i] = kids[(size_t)i]; n->hasValue = hasV; n->value = v; n->seal(); return n; }
NP withPrefix(Nib pre, const NP& n) {
    if (pre.empty()) return n;
    if (n->kind == Node::LEAF) { pre.insert(pre.end(), n->path.begin(), n->path.end()); return leaf(pre, n->value); }
    if (n->kind == Node::EXT) { pre.insert(pre.end(), n->path.begin(), n->path.end()); return ext(pre, n->child); }
    return ext(pre, n);
}
size_t common(const Nib& a, const Nib& b, size_t bo) { size_t c = 0; while (c < a.size() && bo + c < b.size() && a[c] == b[bo + c]) ++c; return c; }
NP insert(const NP& n, const Nib& key, size_t off, const std::string& v) {                        // key[off..] 를 n 아래에 넣은 새 노드 (경로 복사)
    const Nib rest(key.begin() + (long)off, key.end());
    if (!n) return leaf(rest, v);
    if (n->kind == Node::BRANCH) {
        std::array<NP, 16> kids; for (int i = 0; i < 16; ++i) kids[(size_t)i] = n->kids[i];
        if (rest.empty()) return branch(kids, true, v);
        kids[rest[0]] = insert(n->kids[rest[0]], key, off + 1, v); return branch(kids, n->hasValue, n->value);
    }
    const size_t c = common(n->path, key, off);
    if (n->kind == Node::EXT && c == n->path.size()) return ext(n->path, insert(n->child, key, off + c, v));
    if (n->kind == Node::LEAF && c == n->path.size() && c == rest.size()) return leaf(rest, v);    // 같은 키: 덮어쓰기
    std::array<NP, 16> kids; bool hasV = false; std::string bv;                                    // 갈라지는 곳에 가지를 만든다
    const Nib oldRest(n->path.begin() + (long)c, n->path.end());
    if (n->kind == Node::LEAF) { if (oldRest.empty()) { hasV = true; bv = n->value; } else kids[oldRest[0]] = leaf(Nib(oldRest.begin() + 1, oldRest.end()), n->value); }
    else kids[oldRest[0]] = oldRest.size() == 1 ? n->child : ext(Nib(oldRest.begin() + 1, oldRest.end()), n->child);
    const Nib newRest(rest.begin() + (long)c, rest.end());
    if (newRest.empty()) { hasV = true; bv = v; } else kids[newRest[0]] = leaf(Nib(newRest.begin() + 1, newRest.end()), v);
    return withPrefix(Nib(rest.begin(), rest.begin() + (long)c), branch(kids, hasV, bv));
}
NP erase(const NP& n, const Nib& key, size_t off, bool& removed) {
    if (!n) return n;
    const Nib rest(key.begin() + (long)off, key.end());
    if (n->kind == Node::LEAF) { if (n->path == rest) { removed = true; return nullptr; } return n; }
    if (n->kind == Node::EXT) {
        const size_t c = common(n->path, key, off); if (c != n->path.size()) return n;
        NP sub = erase(n->child, key, off + c, removed); if (!removed) return n; return sub ? withPrefix(n->path, sub) : nullptr;       // 자식이 잎·확장으로 줄었으면 경로를 합친다
    }
    std::array<NP, 16> kids; for (int i = 0; i < 16; ++i) kids[(size_t)i] = n->kids[i]; bool hasV = n->hasValue; std::string bv = n->value;
    if (rest.empty()) { if (!hasV) return n; hasV = false; bv.clear(); removed = true; }
    else { NP sub = erase(n->kids[rest[0]], key, off + 1, removed); if (!removed) return n; kids[rest[0]] = sub; }
    int cnt = 0, only = -1; for (int i = 0; i < 16; ++i) if (kids[(size_t)i]) { ++cnt; only = i; }
    if (cnt == 0 && !hasV) return nullptr;
    if (cnt == 0) return leaf(Nib(), bv);                                                          // 값만 남은 가지 -> 빈 경로 잎
    if (cnt == 1 && !hasV) return withPrefix(Nib{(uint8_t)only}, kids[(size_t)only]);              // 자식 하나뿐인 가지는 접는다
    return branch(kids, hasV, bv);
}
bool lookup(const NP& root, const std::string& key, std::string& out) {
    NP n = root; const Nib k = nibbles(key); size_t off = 0;
    while (n) {
        if (n->kind == Node::BRANCH) { if (off == k.size()) { if (!n->hasValue) return false; out = n->value; return true; } n = n->kids[k[off++]]; continue; }
        const Nib rest(k.begin() + (long)off, k.end());
        if (n->kind == Node::LEAF) { if (n->path != rest) return false; out = n->value; return true; }
        if (rest.size() < n->path.size() || !std::equal(n->path.begin(), n->path.end(), rest.begin())) return false; off += n->path.size(); n = n->child;
    }
    return false;
}
void prove(const NP& root, const std::string& key, std::vector<std::string>& proof) {               // 뿌리에서 키 쪽으로 내려가며 방문한 노드의 직렬화를 모은다
    NP n = root; const Nib k = nibbles(key); size_t off = 0;
    while (n) {
        proof.push_back(n->enc);
        if (n->kind == Node::BRANCH) { if (off == k.size()) return; n = n->kids[k[off++]]; continue; }
        if (n->kind == Node::LEAF) return;
        const Nib rest(k.begin() + (long)off, k.end()); if (rest.size() < n->path.size() || !std::equal(n->path.begin(), n->path.end(), rest.begin())) return; off += n->path.size(); n = n->child;
    }
}
enum Verdict { PRESENT, ABSENT, INVALID };
Verdict verify(const Hash& root, const std::string& key, const std::vector<std::string>& proof, std::string& value) {     // 전체 트리 없이 뿌리 해시와 증명만으로
    const Nib k = nibbles(key); size_t off = 0; std::string want((const char*)root.data(), 32); const std::string zero(32, '\0');
    if (want == zero) return proof.empty() ? ABSENT : INVALID;                                    // 빈 트리
    for (size_t i = 0; i < proof.size(); ++i) {
        const std::string& e = proof[i]; const Hash h = sha256(e); if (std::string((const char*)h.data(), 32) != want) return INVALID;                  // 이 노드가 부모가 약속한 해시와 같은가
        if (e.empty()) return INVALID; const int kind = (unsigned char)e[0]; const bool last = i + 1 == proof.size();
        if (kind == Node::BRANCH) {
            if (e.size() < 1 + 32 * 16 + 1) return INVALID; const size_t vpos = 1 + 32 * 16;
            if (off == k.size()) { if (!last) return INVALID; if (e[vpos] == '0') return ABSENT; const size_t colon = e.find(':', vpos + 1); if (colon == std::string::npos) return INVALID; value = e.substr(colon + 1); return PRESENT; }
            want = e.substr(1 + 32 * k[off++], 32); if (want == zero) return last ? ABSENT : INVALID;
        } else {
            if (e.size() < 2) return INVALID; const size_t plen = (unsigned char)e[1]; if (e.size() < 2 + plen) return INVALID; const Nib path(e.begin() + 2, e.begin() + 2 + (long)plen);
            const Nib rest(k.begin() + (long)off, k.end());
            if (kind == Node::LEAF) { if (!last) return INVALID; if (path != rest) return ABSENT; const size_t colon = e.find(':', 2 + plen); if (colon == std::string::npos) return INVALID; value = e.substr(colon + 1); return PRESENT; }
            if (rest.size() < plen || !std::equal(path.begin(), path.end(), rest.begin())) return last ? ABSENT : INVALID;
            if (e.size() != 2 + plen + 32) return INVALID; off += plen; want = e.substr(2 + plen, 32);
        }
    }
    return INVALID;                                                                                // 증명이 중간에 끊겼다
}
Hash rootHash(const NP& r) { return r ? r->hash : Hash{}; }

int main() {
    assert(hex(sha256("")) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    assert(hex(sha256("abc")) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    assert(hex(sha256("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq")) == "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");     // 두 블록
    assert(hex(sha256(std::string(1000000, 'a'))) == "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");                                            // 공개 시험 벡터
    NP t; assert(rootHash(t) == Hash{});
    t = insert(t, nibbles("do"), 0, "verb"); t = insert(t, nibbles("dog"), 0, "puppy"); t = insert(t, nibbles("doge"), 0, "coin"); t = insert(t, nibbles("horse"), 0, "stallion");     // 이더리움 문서의 예시 키
    std::string v; assert(lookup(t, "dog", v) && v == "puppy" && lookup(t, "do", v) && v == "verb" && !lookup(t, "dogs", v) && !lookup(t, "d", v));
    std::mt19937 rng(71); std::map<std::string, std::string> model; NP trie; std::vector<std::pair<NP, std::map<std::string, std::string>>> history;
    auto randomKey = [&]() { std::string k; const int len = (int)(rng() % 5); for (int i = 0; i < len; ++i) k += (char)("\x01\x02\x11\x12\x21"[rng() % 5]); return k; };      // 니블이 겹치도록 작은 알파벳
    for (int step = 0; step < 6000; ++step) {
        const std::string k = randomKey(); const int op = (int)(rng() % 10); const Hash before = rootHash(trie);
        if (op < 6) { const std::string val = "v" + std::to_string(rng() % 1000); trie = insert(trie, nibbles(k), 0, val); const bool changed = model.find(k) == model.end() || model[k] != val; model[k] = val; assert((rootHash(trie) != before) == changed); }
        else if (op < 9) { bool removed = false; trie = erase(trie, nibbles(k), 0, removed); assert(removed == (model.erase(k) > 0)); assert((rootHash(trie) != before) == removed); }
        else { std::string got; assert(lookup(trie, k, got) == (model.find(k) != model.end()) && (model.find(k) == model.end() || got == model[k])); }
        if (step % 600 == 0) history.push_back({trie, model});                                    // 불변 노드라 옛 뿌리를 그대로 들고 있으면 옛 상태가 보존된다
    }
    std::vector<std::pair<std::string, std::string>> items(model.begin(), model.end()); std::shuffle(items.begin(), items.end(), rng);
    NP fresh; for (const auto& kv : items) fresh = insert(fresh, nibbles(kv.first), 0, kv.second);
    assert(rootHash(fresh) == rootHash(trie));                                                     // 내용이 같으면 삽입·삭제 순서·이력과 무관하게 뿌리 해시가 같다
    NP other = fresh; other = insert(other, nibbles("zzz"), 0, "x"); assert(rootHash(other) != rootHash(fresh));
    size_t maxProof = 0, checked = 0;
    for (const auto& kv : model) {                                                                 // 포함 증명
        std::vector<std::string> proof; prove(trie, kv.first, proof); std::string got; assert(verify(rootHash(trie), kv.first, proof, got) == PRESENT && got == kv.second);
        maxProof = std::max(maxProof, proof.size()); ++checked;
        if (checked % 7 == 0) { auto bad = proof; const size_t i = rng() % bad.size(); bad[i][rng() % bad[i].size()] ^= 1; std::string g2; assert(verify(rootHash(trie), kv.first, bad, g2) == INVALID);   // 한 비트라도 바꾸면 거부
            Hash wrong = rootHash(trie); wrong[0] ^= 1; assert(verify(wrong, kv.first, proof, g2) == INVALID); }
    }
    for (int i = 0; i < 400; ++i) { const std::string k = randomKey() + "\x31"; if (model.count(k)) continue; std::vector<std::string> proof; prove(trie, k, proof); std::string g; assert(verify(rootHash(trie), k, proof, g) == ABSENT); }          // 비포함 증명
    for (const auto& h : history) { int n = 0; for (const auto& kv : h.second) { if (++n > 30) break; std::vector<std::string> proof; prove(h.first, kv.first, proof); std::string got; assert(verify(rootHash(h.first), kv.first, proof, got) == PRESENT && got == kv.second); } }     // 옛 뿌리 해시로 옛 값을 증명
    std::cout << "MerklePatriciaTrie: SHA-256 matched the NIST vectors; " << model.size() << " keys built in two different orders gave identical root hashes; all membership proofs (longest " << maxProof << " nodes) and 400 absence proofs verified without the tree, and every tampered proof or wrong root was rejected; root " << hex(rootHash(trie)).substr(0, 16) << "..." << std::endl;
    return 0;
}
// Time Complexity: 조회·삽입·삭제·증명 생성 O(키 길이(니블)), 검증 O(증명 길이) 번의 SHA-256
// Space Complexity: O(N·키 길이) 노드 + 갱신 한 번당 경로 길이만큼의 새 노드(영속)
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
// audit: differential (단일 스레드 std::unordered_map 이 독립 기준: 새로 만든 슬롯 수 == 서로 다른 키 수, 모든 키의 값, 없는 키의 부재)
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
// 핵심은 거리 계산 횟수가 N 보다 훨씬 느리게(부선형) 늘어난다는 점이다 — 저차원에서는 대략 log N 으로 보고되지만 이 16 차원 군집 데이터에서는 N 이 5 배일 때 약 2.3 배 정도로 관측되며, 아래는 "log N" 을 증명하지 않고 부선형임을 확인한다.\n// 검증: ① 정확한 전수 탐색에 대한 recall@10 (ef=10/32/128 에서 각각 0.95/0.99/0.995 이상)  ② 층이 실제로 여러 겹 생겼다 (최상층 >= 2)  ③ 위 층이 비용을 줄인다 — 같은 점·같은 코드로 만든 평평한 NSW(상위 층 없음)보다, 그리고 같은 그래프에서 상위 층 하강을 생략한 질의보다 거리 계산이 적고, 삽입 때의 거리 계산도 평평한 NSW 보다 적다\n//  ④ N = 1000 / 3000 / 5000 에서 ef=32 의 거리 계산이 N 에 비해 부선형으로 늘어난다 (전수 탐색은 5 배, 여기서는 3 배 미만)  ⑤ 차수 상한과 0층 연결성
const int D = 16;
typedef std::array<float, D> Pt; typedef std::pair<float, int> PI;
struct HNSW {
    int M = 12, M0 = 24, efC = 80; double mL = 1.0 / std::log(12.0);
    std::vector<Pt> pts; std::vector<std::vector<std::vector<int>>> nb; int entry = -1, maxL = -1; std::mt19937 rng{42}; long evals = 0; bool flat = false;      // flat: 상위 층 없이 모든 점을 0층에만 넣는 비교용 NSW
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
        int id = pts.size(); pts.push_back(p); int l = (int)(-std::log(std::uniform_real_distribution<double>(1e-12, 1.0)(rng)) * mL); if (flat) l = 0; nb.emplace_back(l + 1);
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
    std::vector<int> search(const Pt& q, int k, int ef, bool descend = true) {      // descend=false: 상위 층 하강을 생략하고 진입점에서 바로 0층 탐색 (비교용)
        int ep = entry; if (descend) for (int ly = maxL; ly > 0; ly--) ep = searchLayer(q, ep, 1, ly)[0].second;
        auto r = searchLayer(q, ep, std::max(ef, k), 0); std::vector<int> out; for (int i = 0; i < k && i < (int)r.size(); i++) out.push_back(r[i].second); return out;
    }
};

int main() {
    std::mt19937 g(3); std::normal_distribution<float> N(0, 1); const int C = 20, Q = 200, k = 10, n = 3000, NBIG = 5000, efs[3] = {10, 32, 128};
    std::vector<Pt> centers(C); for (auto& c : centers) for (auto& x : c) x = N(g) * 4;
    auto sample = [&]() { Pt p = centers[g() % C]; for (auto& x : p) x += N(g); return p; };
    std::vector<Pt> data, qs; for (int i = 0; i < NBIG; i++) data.push_back(sample()); for (int t = 0; t < Q; t++) qs.push_back(sample());
    struct Res { double rec[3], ev[3]; };
    auto measure = [&](HNSW& h, bool descend) {                            // 지금까지 넣은 점들에 대한 정확한 10-NN 과 비교한 recall, 질의당 평균 거리 계산 횟수 (삽입 때 센 evals 는 보존)
        Res r = {{0, 0, 0}, {0, 0, 0}}; int m = (int)h.pts.size(); long keep = h.evals;
        for (int t = 0; t < Q; t++) {
            std::vector<PI> all; for (int i = 0; i < m; i++) { float d = 0; for (int j = 0; j < D; j++) d += (qs[t][j] - data[i][j]) * (qs[t][j] - data[i][j]); all.push_back({d, i}); }
            std::partial_sort(all.begin(), all.begin() + k, all.end()); std::vector<int> exact; for (int i = 0; i < k; i++) exact.push_back(all[i].second);
            for (int e = 0; e < 3; e++) { h.evals = 0; auto res = h.search(qs[t], k, efs[e], descend); r.ev[e] += h.evals; int hit = 0; for (int a : res) hit += std::find(exact.begin(), exact.end(), a) != exact.end(); r.rec[e] += (double)hit / k; }
        }
        for (int e = 0; e < 3; e++) { r.rec[e] /= Q; r.ev[e] /= Q; } h.evals = keep; return r; };
    HNSW h, hf; hf.flat = true;                                            // 같은 점·같은 코드, 다른 것은 상위 층 유무뿐 (hf: 상위 층 없는 평평한 NSW)
    for (int i = 0; i < 1000; i++) h.insert(data[i]);
    Res r1 = measure(h, true);                                             // N = 1000
    for (int i = 1000; i < n; i++) h.insert(data[i]);
    for (int i = 0; i < n; i++) hf.insert(data[i]);
    long buildH = h.evals, buildF = hf.evals;
    for (size_t i = 0; i < h.pts.size(); i++) for (size_t ly = 0; ly < h.nb[i].size(); ly++) assert((int)h.nb[i][ly].size() <= (ly == 0 ? h.M0 : h.M));      // 차수 상한
    std::vector<int> seen(n, 0), st = {h.entry}; seen[h.entry] = 1; int reach = 1;                    // 0층 연결성
    while (!st.empty()) { int c = st.back(); st.pop_back(); for (int e : h.nb[c][0]) if (!seen[e]) { seen[e] = 1; reach++; st.push_back(e); } }
    assert(reach >= n * 0.99);
    Res a = measure(h, true), nd = measure(h, false), f = measure(hf, true);   // 계층 + 하강 / 같은 그래프에서 하강 생략 / 평평한 그래프
    assert(h.maxL >= 2 && hf.maxL == 0);                                    // 층이 실제로 여러 겹 생겼다 (기대 최상층 ln n / ln 12 ≈ 3)
    assert(a.rec[0] <= a.rec[1] + 1e-9 && a.rec[1] <= a.rec[2] + 1e-9 && a.rec[0] >= 0.95 && a.rec[1] >= 0.99 && a.rec[2] >= 0.995);        // ef 를 키우면 recall 이 오른다
    assert(a.ev[1] < n / 10.0);                                             // ef=32 에서도 전수 탐색(N 번)의 1/10 미만
    for (int e = 0; e < 3; e++) assert(a.ev[e] * 1.05 < f.ev[e] && a.ev[e] * 1.05 < nd.ev[e]);   // 위 층이 질의 비용을 줄인다 (평평한 NSW 보다, 그리고 같은 그래프에서 하강을 생략한 것보다)
    assert(buildH < buildF);                                                // 삽입도 위 층 하강 덕에 더 싸다 (같은 점들)
    for (int i = n; i < NBIG; i++) h.insert(data[i]);
    Res r5 = measure(h, true);                                              // N = 5000
    assert(r5.rec[1] >= 0.98 && r5.ev[1] < 3.0 * r1.ev[1]);                 // N 이 5 배가 되어도 거리 계산은 3 배 미만 (전수 탐색은 5 배)
    std::cout << "HNSW: n=" << n << ", layers " << h.maxL + 1 << ", recall@10 ef=10/32/128: " << a.rec[0] << "/" << a.rec[1] << "/" << a.rec[2] << ", avg distance evals " << a.ev[0] << "/" << a.ev[1] << "/" << a.ev[2] << " (flat scan: " << n << "; flat NSW without upper layers: " << f.ev[0] << "/" << f.ev[1] << "/" << f.ev[2] << "; same graph without the descent: " << nd.ev[0] << "/" << nd.ev[1] << "/" << nd.ev[2] << "), build evals " << buildH << " vs flat " << buildF << "; ef=32 evals at n=1000/3000/5000: " << r1.ev[1] << "/" << a.ev[1] << "/" << r5.ev[1] << std::endl;
    return 0;
}
// Time Complexity: 질의·삽입 평균 거리 계산이 N 에 대해 부선형 (저차원에서는 대략 O(log N) 으로 보고, 이 16 차원 군집 데이터는 N 이 5 배일 때 약 2.3 배로 관측 — 경험적, 보장 아님)
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
    ~SL() { N* x = head; while (x) { N* nx = x->nx[0]; delete x; x = nx; } }
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
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// B-트리 인덱스(트리 관점의 요약, 정본은 Tree.md Part 13): 데이터베이스는 "디스크 페이지 읽기 횟수" 로 비용을 센다. 이분 탐색은 log2(페이지 수) 번 페이지를 건드리지만, 페이지 하나에 키 수백 개를 담는 B-트리는 log_F N (F ≈ 수백) 번 — 수억 행도 3~4 번 읽기이다.
//  여기서는 정렬된 키 파일을 *벌크 로딩*한 정적 다단 인덱스를 만들어 읽기 횟수를 정확히 센다.  데이터 페이지는 키 P 개, 인덱스 페이지는 아래 단계 페이지들의 첫 키를 F 개씩 담고, 맨 위가 한 페이지(루트)가 될 때까지 단계를 쌓는다.  읽기 횟수 = 인덱스 단계 수 + 데이터 페이지 1.
//  ① 모든 조회(있는 키·틈에 있는 없는 키·범위 밖)에서 읽기 횟수가 단계 수와 *정확히* 같고 반환 위치가 std::lower_bound 와 같다  ② 단계 수 공식이 n ≤ 10^6, 여러 (P, F) 에서 실제 구조와 일치  ③ 이분 탐색(직전에 읽은 페이지는 캐시)과 비교: n = 10^6, P = F = 64 에서 B-트리 4 번 대 이분 탐색 평균 ≈ 15 번
//  ④ 범위 [lo, hi] 읽기 = 단계 수 + (걸친 데이터 페이지 수 − 1) 이고 읽은 키가 std::lower_bound/upper_bound 구간과 같다  ⑤ n = 10^8, P = F = 256 (구조를 짓지 않고 공식): B-트리 4 번 대 이분 탐색 약 20 번.  (갱신이 있는 동적 판은 이 Part 의 BPlusTree.)
struct StaticIndex {
    int P, F; std::vector<int> keys; std::vector<std::vector<int>> levels;                                       // levels[j] = 단계 j 의 항목(아래 단계 페이지들의 첫 키), 한 페이지에 F 개; levels[0] 은 데이터 페이지별 첫 키
    StaticIndex(std::vector<int> sortedKeys, int p, int f) : P(p), F(f), keys(std::move(sortedKeys)) {
        std::vector<int> cur; for (size_t i = 0; i < keys.size(); i += P) cur.push_back(keys[i]); levels.push_back(cur);
        while ((int)cur.size() > F) { std::vector<int> up; for (size_t i = 0; i < cur.size(); i += F) up.push_back(cur[i]); levels.push_back(up); cur = up; } }
    int levelCount() const { return (int)levels.size() + 1; }                                                    // 인덱스 단계들 + 데이터 페이지
    size_t lowerBound(int key, int& reads) const {                                                               // key 이상인 첫 위치
        reads = 0; size_t page = 0;                                                                              // 현재 단계에서 읽을 페이지 번호 (맨 위는 0)
        for (int lv = (int)levels.size() - 1; lv >= 0; --lv) { ++reads;                                          // 이 단계의 페이지 한 번 읽기
            size_t first = page * F, last = std::min(levels[lv].size(), first + (size_t)F), c = first; for (size_t i = first; i < last; ++i) if (levels[lv][i] <= key) c = i;                  // key 이하인 마지막 항목 (없으면 첫 항목)
            page = c; }                                                                                          // 다음 단계(또는 데이터)의 페이지 번호 = 고른 항목 번호
        ++reads; size_t begin = page * P, end = std::min(keys.size(), begin + P);                                // 데이터 페이지 읽기
        return std::lower_bound(keys.begin() + begin, keys.begin() + end, key) - keys.begin(); }                 // 페이지 끝이면 다음 페이지 첫 위치 = end (읽기 불필요)
    std::vector<int> range(int lo, int hi, int& reads) const {
        size_t pos = lowerBound(lo, reads); std::vector<int> out; while (pos < keys.size() && keys[pos] <= hi) { if (!out.empty() && pos % P == 0) ++reads; out.push_back(keys[pos]); ++pos; } return out; }          // 페이지 경계를 넘을 때마다 한 번 더 읽는다
};
size_t binarySearchPages(const std::vector<int>& keys, int key, int P, int& reads) {                              // 정렬 파일을 이분 탐색, 직전에 읽은 페이지는 캐시
    reads = 0; long lastPage = -1; size_t lo = 0, hi = keys.size();
    while (lo < hi) { size_t mid = (lo + hi) / 2; long pg = (long)(mid / P); if (pg != lastPage) { ++reads; lastPage = pg; } if (keys[mid] < key) lo = mid + 1; else hi = mid; }
    return lo; }
int levelsFormula(size_t n, int P, int F) { size_t entries = (n + P - 1) / P; int idx = 1; while (entries > (size_t)F) { entries = (entries + F - 1) / F; ++idx; } return idx + 1; }

int main() {
    std::mt19937 rng(157);
    for (int P : {4, 16, 64}) for (int F : {4, 16, 64}) for (size_t n : {1, 3, 63, 64, 65, 1000, 4096, 100000, 1000000}) {
        std::vector<int> keys(n); int cur = 0; for (size_t i = 0; i < n; ++i) { cur += 2 + (int)(rng() % 3); keys[i] = cur; }                           // 키 사이에 틈을 둬서 없는 키도 조회
        StaticIndex idx(keys, P, F); assert(idx.levelCount() == levelsFormula(n, P, F));                         // ②
        int probes = n <= 100000 ? 300 : 40;
        for (int q = 0; q < probes; ++q) { int key = (q % 3 == 0) ? keys[rng() % n] : (q % 3 == 1) ? (int)(rng() % (cur + 5)) : (q % 2 ? -5 : cur + 100); int reads; size_t pos = idx.lowerBound(key, reads); size_t want = std::lower_bound(keys.begin(), keys.end(), key) - keys.begin(); assert(pos == want && reads == idx.levelCount());          // ①
            if (n >= 1000000 && F >= 16 && P >= 16) { int br; binarySearchPages(keys, key, P, br); assert(reads <= br); } }                                // ③
        if (n >= 1000) for (int q = 0; q < 50; ++q) { int lo = (int)(rng() % (cur + 5)), hi = lo + (int)(rng() % (8 * P * 3)); int reads; std::vector<int> got = idx.range(lo, hi, reads); std::vector<int> want(std::lower_bound(keys.begin(), keys.end(), lo), std::upper_bound(keys.begin(), keys.end(), hi)); assert(got == want);
            size_t startPos = std::lower_bound(keys.begin(), keys.end(), lo) - keys.begin(); long extra = want.empty() ? 0 : (long)((startPos + want.size() - 1) / P - startPos / P); assert(reads == idx.levelCount() + extra); } }                  // ④
    { const size_t n = 1000000; std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); StaticIndex idx(keys, 64, 64); long idxReads = 0, binReads = 0; for (int q = 0; q < 2000; ++q) { int key = (int)(rng() % n); int r1, r2; idx.lowerBound(key, r1); binarySearchPages(keys, key, 64, r2); idxReads += r1; binReads += r2; } assert(idx.levelCount() == 4 && idxReads == 4 * 2000 && idxReads * 3 < binReads);
      assert(levelsFormula(100000000ULL, 256, 256) == 4); double binModel = std::ceil(std::log2(1e8 / 256)) + 1; assert(binModel >= 19 && binModel <= 21);                                                      // ⑤ 수억 행
      std::cout << "BTreeIndex: a bulk-loaded " << idx.levelCount() << "-level index (P=F=64, n=10^6) returned std::lower_bound's position for every probe with exactly one page read per level (" << (double)idxReads / 2000 << " reads versus " << (double)binReads / 2000 << " for binary search); for 10^8 keys at P=F=256 the formula gives 4 reads versus about " << binModel << std::endl; }
    return 0;
}
// Time Complexity: 조회 O(log_F N) 페이지 읽기 (페이지 안 탐색은 메모리)
// Space Complexity: 데이터 N 키 + 인덱스 단계들 (전체의 1/P 정도)
```
## HashIndex()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_set>
#include <vector>

// 해시 인덱스(해시 관점의 요약, 정본은 Hash.md Part 9): 키의 해시로 버킷 페이지를 골라 "=" 조건을 평균 페이지 1~2 번 읽기로 찾는다(넘치면 오버플로 페이지를 사슬로). B-트리보다 등치 조회가 빠르지만
//  키 순서를 모르므로 범위 조건·정렬·접두사 검색은 못 한다 — PostgreSQL 의 hash index, 메모리 DB 의 기본 인덱스.  여기서는 페이지 용량 cap 인 고정 버킷 수(B)의 인덱스로 *페이지 읽기 횟수*를 정확히 센다.
//  버킷 하나의 키 수 S 는 푸아송(λ = n/B)이므로 기대 읽기 횟수를 *닫힌 형태*로 계산할 수 있다 — 실패 조회: E[max(1, ⌈S/cap⌉)], 성공 조회(키를 고르면 그 버킷은 크기 편향: S = 1 + Poisson(λ), 위치는 균등): E[(1/S)·Σ_{i<S} (⌊i/cap⌋ + 1)].
//  ① 적재율 λ/cap ∈ {0.25, 0.5, 0.75, 1, 1.5} 에서 측정한 평균 읽기가 푸아송 계산값과 1.5% 안  ② 사슬 불변식(마지막 페이지만 덜 참)과 std::unordered_set 대조 — 삽입·삭제·조회 40 만 번  ③ 범위 조건은 전 페이지 순회(읽기 = 사용 페이지 수), 정렬된 인덱스는 같은 범위를 단계 수 + ⌈k/cap⌉ 근처로 읽는다.
static uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }
struct HashIdx {
    struct Page { std::vector<uint64_t> keys; int next = -1; };
    int cap; size_t B; std::vector<Page> pages; std::vector<int> freeList; size_t cnt = 0;                         // pages[0..B) = 버킷 머리 페이지
    HashIdx(int c, size_t buckets) : cap(c), B(buckets), pages(buckets) {}
    size_t bucket(uint64_t key) const { return (size_t)(mix(key) % B); }
    int newPage() { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); pages[u] = Page(); } else { pages.push_back(Page()); u = (int)pages.size() - 1; } return u; }
    bool contains(uint64_t key, long* reads = nullptr) const { long r = 0; for (int p = (int)bucket(key); p >= 0; p = pages[p].next) { ++r; for (uint64_t k : pages[p].keys) if (k == key) { if (reads) *reads += r; return true; } } if (reads) *reads += r; return false; }
    bool insert(uint64_t key) { if (contains(key)) return false; int p = (int)bucket(key); while ((int)pages[p].keys.size() == cap && pages[p].next >= 0) p = pages[p].next;
        if ((int)pages[p].keys.size() == cap) { int q = newPage(); pages[p].next = q; p = q; } pages[p].keys.push_back(key); ++cnt; return true; }
    bool erase(uint64_t key) {
        int head = (int)bucket(key), p = head; while (p >= 0) { auto it = std::find(pages[p].keys.begin(), pages[p].keys.end(), key); if (it != pages[p].keys.end()) {
                int prev = -1, tail = head; while (pages[tail].next >= 0) { prev = tail; tail = pages[tail].next; }                    // 사슬의 마지막 페이지
                *it = pages[tail].keys.back(); pages[tail].keys.pop_back(); if (pages[tail].keys.empty() && tail != head) { pages[prev].next = -1; freeList.push_back(tail); } --cnt; return true; }
            p = pages[p].next; }
        return false; }
    size_t usedPages() const { return pages.size() - freeList.size(); }
    bool valid() const { size_t total = 0, chains = 0; for (size_t b = 0; b < B; ++b) { for (int p = (int)b; p >= 0; p = pages[p].next) { ++chains; total += pages[p].keys.size(); int n = (int)pages[p].keys.size(); if (n > cap) return false; if (pages[p].next >= 0 && n != cap) return false; if (p != (int)b && n == 0) return false; for (uint64_t k : pages[p].keys) if (bucket(k) != b) return false; } } return total == cnt && chains == usedPages(); }
};
double poissonPmf(int s, double lam) { return std::exp(-lam + s * std::log(lam) - std::lgamma(s + 1.0)); }
double expectedFailReads(double lam, int cap) { double e = 0; for (int s = 0; s <= 400; ++s) e += poissonPmf(s, lam) * std::max(1, (s + cap - 1) / cap); return e; }
double expectedHitReads(double lam, int cap) { double e = 0; for (int t = 0; t <= 400; ++t) { int S = 1 + t; double acc = 0; for (int i = 0; i < S; ++i) acc += i / cap + 1; e += poissonPmf(t, lam) * acc / S; } return e; }

int main() {
    std::mt19937_64 rng(161); const int cap = 4; const size_t B = 1 << 15;
    for (double load : {0.25, 0.5, 0.75, 1.0, 1.5}) {                                                            // ① 푸아송 예측
        double lam = load * cap; size_t n = (size_t)(lam * B); HashIdx idx(cap, B); std::vector<uint64_t> keys; while (keys.size() < n) { uint64_t k = rng(); if (idx.insert(k)) keys.push_back(k); } assert(idx.valid() && idx.cnt == n);
        long hitReads = 0; for (uint64_t k : keys) { bool f = idx.contains(k, &hitReads); assert(f); } double hit = (double)hitReads / (double)n;
        long missReads = 0; const long Q = 400000; for (long i = 0; i < Q; ++i) { bool f = idx.contains(rng() | 1ULL << 63 | 1, &missReads); (void)f; } double miss = (double)missReads / Q;                                  // 부재 키 (상위 비트를 켠 값은 저장 키와 겹칠 수 있으나 확률 2^-n)
        double eh = expectedHitReads(lam, cap), em = expectedFailReads(lam, cap); assert(std::fabs(hit - eh) < 0.015 * eh && std::fabs(miss - em) < 0.015 * em);
        double pagesPred = 0; for (int s = 0; s <= 400; ++s) pagesPred += poissonPmf(s, lam) * std::max(1, (s + cap - 1) / cap); assert(std::fabs((double)idx.usedPages() / (double)B - pagesPred) < 0.01 * pagesPred);     // 사용 페이지 수도 예측과 일치
        if (load == 1.0) std::cout << "HashIndex: measured page reads matched the Poisson prediction at load factors 0.25..1.5 (at load 1.0: hit " << hit << " vs " << eh << ", miss " << miss << " vs " << em << ")"; }
    { HashIdx idx(cap, 1 << 10); std::unordered_set<uint64_t> ref; for (long step = 0; step < 400000; ++step) { uint64_t k = rng() % 6000; int op = (int)(rng() % 3);                                          // ②
        if (op == 0) { bool a = idx.insert(k); bool r = ref.insert(k).second; assert(a == r); } else if (op == 1) { bool a = idx.erase(k); bool r = ref.erase(k) > 0; assert(a == r); } else { assert(idx.contains(k) == (ref.count(k) > 0)); }
        assert(idx.cnt == ref.size()); if (step % 20011 == 0) assert(idx.valid()); } assert(idx.valid());
      HashIdx big(cap, 1 << 10); for (uint64_t k = 0; k < 6000; ++k) big.insert(k); long scan = 0; for (size_t b = 0; b < big.B; ++b) for (int p = (int)b; p >= 0; p = big.pages[p].next) ++scan; assert((size_t)scan == big.usedPages());     // ③ 범위 조건 = 전 페이지
      long orderedReads = 3 + (100 + cap - 1) / cap; assert(scan > 20 * orderedReads);
      std::cout << "; a 100-key range needs all " << scan << " pages on a hash index versus about " << orderedReads << " on an ordered index" << std::endl; }
    return 0;
}
// Time Complexity: 등치 조회 평균 O(1) 페이지, 범위 조건은 O(전체 페이지)
// Space Complexity: O(N / cap + B) 페이지
```

# Part 14. 운영체제
## BuddyAllocator()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 버디 할당기(메모리 관점의 요약, 정본은 Memory.md Part 6): 메모리를 2^k 페이지 블록으로만 나눈다. 할당은 요청보다 크거나 같은 가장 작은 빈 블록을 찾아 필요한 크기가 될 때까지 반으로 쪼개고(남는 반쪽은 빈 목록에),
//  해제는 "버디"(블록 시작 주소 XOR 크기)가 비어 있으면 합쳐 위 차수로 올린다.  버디의 주소가 XOR 한 번으로 구해져 빠르고, 외부 단편화가 제한된다 (Linux 페이지 할당기).
//  ① 불변식(매 연산 뒤): 할당 블록 + 빈 블록이 [0, 2^K) 를 틈과 겹침 없이 *정확히 덮고*, 모든 블록은 자기 크기로 정렬되며, 같은 차수의 빈 버디 쌍이 없다(최대 병합)  ② 무작위 할당·해제 20 만 번(요청 1..64 페이지) 의 불변식 + 오라클(페이지별 사용 표시)  ③ 할당 실패는 상태를 바꾸지 않고, 이중 해제·잘못된 주소 해제는 거부된다
//  ④ 내부 단편화: 요청 r 이 2^⌈log2 r⌉ 로 올림되어 낭비 < 50%, 균등 요청 평균 낭비가 공식 합과 같다  ⑤ 외부 단편화 장면: 1024 페이지를 모두 1 페이지씩 할당 → 하나 걸러 해제하면 512 페이지가 비었어도 2 페이지 할당은 실패 → 나머지를 해제하면 완전히 병합되어 1024 페이지가 한 번에 할당된다
//  ⑥ 새 할당기에서 1 페이지를 할당하면 빈 목록에는 차수 0..K−1 마다 정확히 블록 하나(쪼개고 남은 버디)가 있다.
struct Buddy {
    int K; std::vector<std::set<size_t>> freeLists; std::map<size_t, int> allocated; long splits = 0, merges = 0;
    explicit Buddy(int maxOrder) : K(maxOrder), freeLists(maxOrder + 1) { freeLists[maxOrder].insert(0); }
    static int orderFor(size_t pages) { int o = 0; while ((size_t(1) << o) < pages) ++o; return o; }
    long alloc(size_t pages) {
        int need = orderFor(pages); int o = need; while (o <= K && freeLists[o].empty()) ++o; if (o > K) return -1;               // 실패는 상태를 바꾸지 않는다
        size_t off = *freeLists[o].begin(); freeLists[o].erase(freeLists[o].begin());
        while (o > need) { --o; freeLists[o].insert(off + (size_t(1) << o)); ++splits; }                                          // 반으로 쪼개고 위쪽 반쪽은 빈 목록에
        allocated[off] = need; return (long)off; }
    bool free(size_t off) {
        auto it = allocated.find(off); if (it == allocated.end()) return false; int o = it->second; allocated.erase(it);
        while (o < K) { size_t buddy = off ^ (size_t(1) << o); auto b = freeLists[o].find(buddy); if (b == freeLists[o].end()) break; freeLists[o].erase(b); off = std::min(off, buddy); ++o; ++merges; }          // 버디가 비어 있으면 합친다
        freeLists[o].insert(off); return true; }
    size_t freePages() const { size_t n = 0; for (int o = 0; o <= K; ++o) n += freeLists[o].size() << o; return n; }
    int largestFreeOrder() const { for (int o = K; o >= 0; --o) if (!freeLists[o].empty()) return o; return -1; }
    bool valid() const {
        std::vector<std::pair<size_t, size_t>> blocks; for (auto& kv : allocated) blocks.push_back({kv.first, size_t(1) << kv.second}); for (int o = 0; o <= K; ++o) for (size_t off : freeLists[o]) blocks.push_back({off, size_t(1) << o});
        std::sort(blocks.begin(), blocks.end()); size_t pos = 0; for (auto& b : blocks) { if (b.first != pos || b.first % b.second != 0) return false; pos += b.second; } if (pos != (size_t(1) << K)) return false;      // 틈·겹침 없이 정렬된 타일링
        for (int o = 0; o < K; ++o) for (size_t off : freeLists[o]) if (freeLists[o].count(off ^ (size_t(1) << o))) return false; return true; }                                               // 최대 병합
};

int main() {
    { Buddy b(10); long a = b.alloc(1); assert(a == 0 && b.valid()); for (int o = 0; o < 10; ++o) assert(b.freeLists[o].size() == 1 && *b.freeLists[o].begin() == (size_t(1) << o)); assert(b.freeLists[10].empty());          // ⑥
      assert(b.free(0) && b.freeLists[10].size() == 1 && b.valid() && !b.free(0) && !b.free(5)); }                                                                                                                     // ③ 이중·잘못된 해제 거부, 전부 합쳐짐
    std::mt19937 rng(197); const int K = 12; Buddy b(K); std::vector<long> live; std::vector<size_t> liveSize; std::vector<char> page(size_t(1) << K, 0); long failed = 0;                                                     // ②
    for (int step = 0; step < 200000; ++step) {
        if (live.empty() || rng() % 100 < 55) { size_t req = 1 + rng() % 64; auto before = b.freeLists; auto beforeAlloc = b.allocated; long off = b.alloc(req);
            if (off < 0) { ++failed; assert(b.freeLists == before && b.allocated == beforeAlloc); assert(b.largestFreeOrder() < Buddy::orderFor(req)); }                                                                           // 실패: 정말 맞는 블록이 없다
            else { size_t sz = size_t(1) << Buddy::orderFor(req); for (size_t p = off; p < (size_t)off + sz; ++p) { assert(!page[p]); page[p] = 1; } live.push_back(off); liveSize.push_back(sz); } }
        else { size_t i = rng() % live.size(); assert(b.free((size_t)live[i])); for (size_t p = live[i]; p < (size_t)live[i] + liveSize[i]; ++p) page[p] = 0; live[i] = live.back(); live.pop_back(); liveSize[i] = liveSize.back(); liveSize.pop_back(); }
        if (step % 17 == 0) assert(b.valid()); }
    assert(b.valid()); for (size_t i = 0; i < live.size(); ++i) assert(b.free((size_t)live[i])); assert(b.valid() && b.freeLists[K].size() == 1 && b.freePages() == (size_t(1) << K));
    { double waste = 0, expect = 0; for (size_t r = 1; r <= 64; ++r) { size_t blk = size_t(1) << Buddy::orderFor(r); waste += (double)(blk - r) / (double)blk; assert(blk - r < blk / 2 + (blk == r ? 1 : 0) || r == 1); expect += (double)(blk - r) / (double)blk; } assert(std::fabs(waste - expect) < 1e-9 && waste / 64 < 0.5); }                    // ④
    { Buddy f(10); std::vector<long> singles; for (int i = 0; i < 1024; ++i) singles.push_back(f.alloc(1)); assert(f.freePages() == 0 && f.alloc(1) == -1);
      for (int i = 0; i < 1024; i += 2) assert(f.free((size_t)singles[i])); assert(f.freePages() == 512 && f.largestFreeOrder() == 0 && f.alloc(2) == -1 && f.valid());                                                          // ⑤ 512 페이지가 비었지만 2 페이지가 없다
      for (int i = 1; i < 1024; i += 2) assert(f.free((size_t)singles[i])); assert(f.valid() && f.freeLists[10].size() == 1 && f.alloc(1024) == 0);
      std::cout << "BuddyAllocator: allocated and free blocks tiled the whole arena with maximal coalescing after every checked step of 2*10^5 random operations (" << failed << " allocations failed without changing state), double frees were rejected, a half-free arena of single pages could not serve a 2-page request until the rest was freed (then one 1024-page block), and requests rounded up with <50% waste" << std::endl; }
    return 0;
}
// Time Complexity: 할당·해제 O(log (전체 페이지 수))
// Space Complexity: 차수별 빈 목록 + 할당 표
```
## SlabAllocator()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 슬랩 할당기(메모리 관점의 요약, 정본은 Memory.md Part 6): 같은 크기의 객체(inode, 소켓 버퍼 ...)를 자주 할당·해제할 때 미리 같은 크기 칸으로 나눈 "슬랩" 페이지를 두고 빈 칸 목록에서 O(1) 로 꺼낸다.
//  해제된 칸은 재사용되어 생성 비용도 절약되고 내부 단편화가 거의 없다.  슬랩이 가득 / 일부 / 빔 상태를 오가며 비는 슬랩은 한 장만 남기고 페이지를 돌려준다 (Linux kmem_cache).  주소 → (슬랩, 칸 번호)가 나눗셈 한 번으로 구해지므로 해제에 별도 헤더가 필요 없다.
//  ① 객체 크기 16 / 24 / 100 / 1000 바이트, 페이지 4096: 무작위 할당·해제 40 만 번에서 반환 주소가 (정렬된 칸 경계, 서로 다름, 한 슬랩 안) 이고 살아 있는 집합이 오라클과 일치, 슬랩 상태 분류(가득 / 일부 / 빔)가 칸 수와 일치
//  ② 이중 해제·칸 경계가 아닌 주소·모르는 슬랩 해제는 거부  ③ 모두 해제하면 비어 있는 슬랩이 ≤ 1 장만 남고 나머지 페이지는 반환됨  ④ 공간 효율: S = 100 이면 슬랩은 4096/100 = 40 칸(낭비 2.3%), 2 의 거듭제곱(128 B)으로 올림하는 방식은 28% 낭비.
struct SlabCache {
    struct Slab { std::vector<int> freeIdx; std::vector<char> used; int inUse = 0; bool live = false; };
    size_t objSize, pageSize, perSlab; std::vector<Slab> slabs; std::set<int> partial, full, empty; std::vector<int> freePages; long pagesTaken = 0, pagesReturned = 0;                       // 슬랩 번호 = 페이지 번호
    SlabCache(size_t s, size_t page = 4096) : objSize(s), pageSize(page), perSlab(page / s) {}
    int takePage() { int id; if (!freePages.empty()) { id = freePages.back(); freePages.pop_back(); } else { slabs.push_back(Slab()); id = (int)slabs.size() - 1; } Slab& s = slabs[id]; s.live = true; s.inUse = 0; s.used.assign(perSlab, 0); s.freeIdx.clear(); for (int i = (int)perSlab - 1; i >= 0; --i) s.freeIdx.push_back(i); ++pagesTaken; return id; }
    long alloc() {
        int id; if (!partial.empty()) id = *partial.begin(); else if (!empty.empty()) { id = *empty.begin(); empty.erase(empty.begin()); partial.insert(id); } else { id = takePage(); partial.insert(id); }
        Slab& s = slabs[id]; int idx = s.freeIdx.back(); s.freeIdx.pop_back(); s.used[idx] = 1; ++s.inUse; if (s.inUse == (int)perSlab) { partial.erase(id); full.insert(id); } return (long)(id * pageSize + (size_t)idx * objSize); }
    bool free(long addr) {
        if (addr < 0) return false; size_t id = (size_t)addr / pageSize, off = (size_t)addr % pageSize; if (id >= slabs.size() || !slabs[id].live || off % objSize != 0 || off / objSize >= perSlab) return false; Slab& s = slabs[id]; size_t idx = off / objSize; if (!s.used[idx]) return false;
        bool wasFull = s.inUse == (int)perSlab; s.used[idx] = 0; s.freeIdx.push_back((int)idx); --s.inUse; if (wasFull) { full.erase((int)id); partial.insert((int)id); }
        if (s.inUse == 0) { partial.erase((int)id); empty.insert((int)id); if (empty.size() > 1) { int victim = *empty.rbegin(); empty.erase(victim); slabs[victim].live = false; freePages.push_back(victim); ++pagesReturned; } }          // 빈 슬랩은 한 장만 캐시
        return true; }
    long livePages() const { return pagesTaken - pagesReturned; }
    bool valid(size_t liveObjects) const { size_t total = 0; for (size_t i = 0; i < slabs.size(); ++i) { const Slab& s = slabs[i]; if (!s.live) continue; int cnt = 0; for (char u : s.used) cnt += u; if (cnt != s.inUse || (int)s.freeIdx.size() != (int)perSlab - cnt) return false; total += cnt;
            bool inFull = full.count((int)i) > 0, inPartial = partial.count((int)i) > 0, inEmpty = empty.count((int)i) > 0; if (cnt == (int)perSlab ? !(inFull && !inPartial && !inEmpty) : cnt == 0 ? !(inEmpty && !inFull && !inPartial) : !(inPartial && !inFull && !inEmpty)) return false; } return total == liveObjects; }
};

int main() {
    std::mt19937 rng(199);
    for (size_t S : {16, 24, 100, 1000}) { SlabCache c(S); std::set<long> live; std::vector<long> ids; size_t maxLive = 0;
        for (int step = 0; step < 400000; ++step) {
            if (ids.empty() || rng() % 100 < 52) { long a = c.alloc(); assert((size_t)a % 4096 % S == 0 && ((size_t)a % 4096) / S < c.perSlab && live.insert(a).second); ids.push_back(a); }          // ① 정렬·유일·한 슬랩 안
            else { size_t i = rng() % ids.size(); long a = ids[i]; assert(c.free(a)); live.erase(a); ids[i] = ids.back(); ids.pop_back(); }
            maxLive = std::max(maxLive, live.size()); if (step % 1999 == 0) assert(c.valid(live.size())); }
        assert(c.valid(live.size()));
        if (!ids.empty()) { long a = ids[0]; assert(c.free(a) && !c.free(a)); ids[0] = ids.back(); ids.pop_back(); live.erase(a); }                                     // ② 이중 해제
        assert(!c.free((long)((c.slabs.size() + 10) * 4096)) && !c.free(-5)); if (!ids.empty()) assert(!c.free(ids[0] + 1));                                   // 모르는 슬랩·칸 경계가 아닌 주소
        for (long a : ids) assert(c.free(a)); assert(c.valid(0) && c.empty.size() <= 1 && c.full.empty() && c.partial.empty() && c.livePages() == (long)c.empty.size()); }                          // ③
    { double slabWaste = 1.0 - (double)(4096 / 100 * 100) / 4096, pow2Waste = 1.0 - 100.0 / 128; assert(slabWaste < 0.03 && pow2Waste > 0.2);                          // ④
      SlabCache c(100); std::vector<long> v; for (int i = 0; i < 40000; ++i) v.push_back(c.alloc()); double eff = (double)v.size() * 100 / (double)(c.livePages() * 4096); assert(eff > 0.975);
      std::cout << "SlabAllocator: objects of 16/24/100/1000 bytes survived 4*10^5 random allocations and frees per size with valid slab lists (full / partial / empty) and at most one cached empty slab at the end; double and misaligned frees were rejected; a 100-byte cache used " << eff * 100 << "% of its pages versus " << (1 - pow2Waste) * 100 << "% with power-of-two rounding" << std::endl; }
    return 0;
}
// Time Complexity: 할당·해제 O(1) (집합 연산은 슬랩 수에 로그; 실제 구현은 이중 연결 리스트로 O(1))
// Space Complexity: 슬랩 페이지 + 칸당 1 바이트 표
```
## RadixTree()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <vector>

// 기수 트리(트리 관점의 요약, 문자열용은 Tree.md Part 9, 정수 키용 본격판은 이 Part 의 XArray): 키를 고정 비트 폭 조각(여기서는 4 비트 = 16-분)으로 잘라 한 층에 한 조각씩 내려가는 트리.
//  비교가 아니라 인덱싱으로 O(키 비트 수 / 조각 폭) 에 찾고 정렬 순서가 자연스럽게 유지된다 (Linux 의 radix tree → XArray).  노드는 arena 에 두고 자식 수를 세어 *삭제 시 빈 가지를 잘라낸다*(pruning).
//  정렬 순서 덕에 후속자(successor: k 보다 큰 가장 작은 키)·최솟값·구간 순회가 O(깊이 · 16) 에 된다 — 내려가다 막히면 가장 가까운 오른쪽 형제로 올라가 최솟값을 따라간다.
//  ① 무작위 삽입·삭제·조회·후속자·구간 합 80 만 번을 std::map 과 대조(키 폭 12 비트의 조밀한 공간 / 32 비트의 성긴 공간)  ② 삭제로 키가 0 개가 되면 노드는 루트 하나만 남는다  ③ 노드 수: 연속 키 0..n−1 이면 깊이 d 의 노드가 정확히 ⌈n / 16^(8−d)⌉ 개, 성긴 무작위 키 K 개는 ≤ 8K + 1.
struct Radix {
    struct Node { std::array<int, 16> c; int cnt = 0; bool has = false; long v = 0; Node() { c.fill(-1); } };
    std::vector<Node> n; std::vector<int> freeList; size_t keys = 0;
    Radix() { n.push_back(Node()); }
    int make() { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); n[u] = Node(); } else { n.push_back(Node()); u = (int)n.size() - 1; } return u; }
    static int digit(uint32_t k, int level) { return (int)((k >> (28 - 4 * level)) & 15); }                          // level 0 = 최상위 4 비트
    void put(uint32_t k, long v) { int u = 0; for (int l = 0; l < 8; ++l) { int d = digit(k, l); int ch = n[u].c[d]; if (ch < 0) { ch = make(); n[u].c[d] = ch; ++n[u].cnt; } u = ch; } if (!n[u].has) ++keys; n[u].has = true; n[u].v = v; }
    bool get(uint32_t k, long& v) const { int u = 0; for (int l = 0; l < 8 && u >= 0; ++l) u = n[u].c[digit(k, l)]; if (u < 0 || !n[u].has) return false; v = n[u].v; return true; }
    bool erase(uint32_t k) { int path[9]; int u = 0; path[0] = 0; for (int l = 0; l < 8; ++l) { u = n[u].c[digit(k, l)]; if (u < 0) return false; path[l + 1] = u; } if (!n[u].has) return false; n[u].has = false; --keys;
        for (int l = 8; l >= 1; --l) { int x = path[l]; if (n[x].has || n[x].cnt > 0) break; int parent = path[l - 1], d = digit(k, l - 1); n[parent].c[d] = -1; --n[parent].cnt; freeList.push_back(x); }          // 비어 가는 노드를 위로 올라가며 잘라낸다
        return true; }
    long long minFrom(int u, int level, uint32_t prefix) const {                                                    // u 아래의 최솟값 (없으면 −1)
        if (level == 8) return n[u].has ? (long long)prefix : -1; for (int d = 0; d < 16; ++d) { int ch = n[u].c[d]; if (ch >= 0) { long long r = minFrom(ch, level + 1, (prefix << 4) | d); if (r >= 0) return r; } } return -1; }
    long long successor(uint32_t k) const {                                                                         // k 보다 큰 가장 작은 키 (없으면 −1)
        int path[9]; int u = 0; path[0] = 0; int depth = 0; for (int l = 0; l < 8; ++l) { int ch = n[u].c[digit(k, l)]; if (ch < 0) break; u = ch; path[l + 1] = u; depth = l + 1; }
        for (int l = depth; l >= 0; --l) { if (l == 8) continue; int node = path[l]; for (int d = digit(k, l) + 1; d < 16; ++d) { int ch = n[node].c[d]; if (ch >= 0) { uint32_t prefix = (l == 0) ? 0 : (k >> (32 - 4 * l)); prefix = (prefix << 4) | d; long long r = minFrom(ch, l + 1, prefix); if (r >= 0) return r; } } }
        return -1; }
    long long minKey() const { return minFrom(0, 0, 0); }
    size_t liveNodes() const { return n.size() - freeList.size(); }
};

int main() {
    std::mt19937 rng(191);
    for (int space = 0; space < 2; ++space) { Radix t; std::map<uint32_t, long> ref; const uint32_t MASK = space ? 0xFFFFFFFFu : 0xFFFu;                    // ①
        for (long step = 0; step < 400000; ++step) { uint32_t k = (uint32_t)rng() & MASK; int op = (int)(rng() % 6);
            if (op <= 1) { t.put(k, step); ref[k] = step; } else if (op == 2) { bool a = t.erase(k); bool r = ref.erase(k) > 0; assert(a == r); } else if (op == 3) { long v; bool a = t.get(k, v); auto it = ref.find(k); assert(a == (it != ref.end()) && (!a || v == it->second)); }
            else if (op == 4) { auto it = ref.upper_bound(k); long long want = it == ref.end() ? -1 : (long long)it->first; assert(t.successor(k) == want); } else { long long want = ref.empty() ? -1 : (long long)ref.begin()->first; assert(t.minKey() == want); }
            assert(t.keys == ref.size()); }
        std::vector<uint32_t> all; for (long long k = t.minKey(); k >= 0; k = t.successor((uint32_t)k)) all.push_back((uint32_t)k); std::vector<uint32_t> want; for (auto& kv : ref) want.push_back(kv.first); assert(all == want);                    // 후속자를 이어 가면 정렬된 전체 순회
        for (uint32_t k : want) assert(t.erase(k)); assert(t.keys == 0 && t.liveNodes() == 1 && t.minKey() == -1); }                                  // ② 모두 지우면 루트만
    { Radix t; const uint32_t N = 100000; for (uint32_t k = 0; k < N; ++k) t.put(k, k); size_t expect = 0; for (int d = 0; d <= 8; ++d) { uint64_t per = 1; for (int j = 0; j < 8 - d; ++j) per *= 16; expect += (N + per - 1) / per; } assert(t.liveNodes() == expect);       // ③ 조밀한 키: 정확한 노드 수
      Radix s; const int K = 20000; for (int i = 0; i < K; ++i) s.put((uint32_t)rng(), i); assert(s.liveNodes() <= 8 * (size_t)K + 1);
      std::cout << "RadixTree: 8-level 16-ary tree matched std::map over 8*10^5 mixed operations (get, put, erase, successor, min) in a dense 12-bit and a sparse 32-bit key space, erasing everything pruned it back to the root, and 10^5 consecutive keys used exactly " << t.liveNodes() << " nodes" << std::endl; }
    return 0;
}
// Time Complexity: 조회·삽입·삭제 O(키 비트 / 4), 후속자 O(깊이 · 16)
// Space Complexity: 쓰인 경로 비례 (조밀하면 키 수 / 15 근처)
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
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <vector>

// 페이지 테이블(메모리 관점의 요약, 정본은 Memory.md Part 9): 가상 주소 → 물리 주소 변환표. x86-64 식 4 단 구조 = 9 + 9 + 9 + 9 비트 인덱스 + 12 비트 페이지 안 오프셋(4 KB).
//  쓰는 영역의 테이블만 만들어 두므로 주소 공간이 커도 메모리가 적게 들고, 없는 항목에 접근하면 페이지 폴트(OS 가 처리). 2 MB *큰 페이지*는 3 단째 항목이 곧바로 물리 주소를 가리켜 한 단계를 건너뛴다.
//  항목에는 present / writable / user / accessed / dirty 비트가 있고 접근 때 하드웨어가 accessed·dirty 를 켠다.  TLB 는 최근 (가상 페이지 → 물리 프레임) 변환을 캐시한다(LRU).
//  ① 무작위로 4 KB·2 MB 페이지를 매핑·해제한 열을 std::map 오라클과 대조: 변환 결과·폴트 종류(없음 / 쓰기 금지 / 사용자 접근 금지)·accessed/dirty 비트  ② 메모리 접근 횟수(워크 단계): 4 KB 는 4 번, 2 MB 는 3 번, TLB 적중이면 0 번
//  ③ 테이블 쪽수: 매핑 3 곳(서로 먼 주소)에 필요한 테이블 쪽수가 공식과 같다(3 영역 × 3 하위 단계 + 루트)  ④ TLB: 8 바이트 간격 순차 접근의 적중률 = 1 − 1/512, 작업 집합이 TLB 보다 크면 무작위 접근 적중률 ≈ TLB 크기 / 작업 집합 쪽수.
struct MMU {
    enum Fault { OK = 0, NOT_PRESENT = 1, WRITE_PROTECT = 2, USER_PROTECT = 3 };
    static const uint64_t P = 1, W = 2, U = 4, A = 8, D = 16, HUGE = 32;
    struct Table { std::array<uint64_t, 512> e; Table() { e.fill(0); } };                                           // 항목: 하위 12 비트 플래그 | 물리 프레임 번호 << 12
    std::vector<Table> tables; size_t tlbCap; std::list<std::pair<uint64_t, uint64_t>> tlb; long hits = 0, misses = 0, walkReads = 0;
    explicit MMU(size_t tlbSize = 64) : tlbCap(tlbSize) { tables.push_back(Table()); }
    static int idx(uint64_t va, int level) { return (int)((va >> (39 - 9 * level)) & 511); }                       // level 0 = 최상위
    int child(int t, int i) { if (!(tables[t].e[i] & P)) { tables.push_back(Table()); tables[t].e[i] = ((uint64_t)(tables.size() - 1) << 12) | P | W | U; } return (int)(tables[t].e[i] >> 12); }
    void map4k(uint64_t va, uint64_t frame, uint64_t flags) { int t = 0; for (int l = 0; l < 3; ++l) t = child(t, idx(va, l)); tables[t].e[idx(va, 3)] = (frame << 12) | flags | P; }
    void map2m(uint64_t va, uint64_t frame, uint64_t flags) { int t = 0; for (int l = 0; l < 2; ++l) t = child(t, idx(va, l)); tables[t].e[idx(va, 2)] = (frame << 12) | flags | P | HUGE; }
    void invalidate(uint64_t vpage) { for (auto it = tlb.begin(); it != tlb.end(); ++it) if (it->first == vpage) { tlb.erase(it); return; } }
    void unmap4k(uint64_t va) { int t = 0; for (int l = 0; l < 3; ++l) { uint64_t e = tables[t].e[idx(va, l)]; if (!(e & P) || (l == 2 && (e & HUGE))) return; t = (int)(e >> 12); } tables[t].e[idx(va, 3)] = 0; invalidate(va >> 12); }
    Fault translate(uint64_t va, bool write, bool user, uint64_t& pa, int* reads = nullptr) {
        uint64_t vpage = va >> 12; int r = 0;
        for (auto it = tlb.begin(); it != tlb.end(); ++it) if (it->first == vpage) { uint64_t flags = it->second & 4095; if (write && !(flags & W)) return WRITE_PROTECT; if (user && !(flags & U)) return USER_PROTECT; tlb.splice(tlb.begin(), tlb, it); ++hits; pa = ((it->second >> 12) << 12) | (va & 4095); if (reads) *reads = 0; return OK; }       // TLB 적중 (플래그 검사는 캐시된 값으로)
        ++misses; int t = 0; uint64_t e = 0; bool huge = false;
        for (int l = 0; l < 4; ++l) { ++r; uint64_t& ent = tables[t].e[idx(va, l)]; if (!(ent & P)) { walkReads += r; if (reads) *reads = r; return NOT_PRESENT; } if (l == 2 && (ent & HUGE)) { e = ent; huge = true; break; } if (l == 3) { e = ent; break; } t = (int)(ent >> 12); }
        walkReads += r; if (reads) *reads = r;
        if (write && !(e & W)) return WRITE_PROTECT; if (user && !(e & U)) return USER_PROTECT;
        int level = huge ? 2 : 3; uint64_t* ent = nullptr; { int tt = 0; for (int l = 0; l < level; ++l) tt = (int)(tables[tt].e[idx(va, l)] >> 12); ent = &tables[tt].e[idx(va, level)]; } *ent |= A | (write ? D : 0);          // 하드웨어가 accessed/dirty 를 켠다
        uint64_t frameBase = huge ? (((e >> 12) << 12) + (va & 0x1FF000)) : ((e >> 12) << 12); pa = frameBase | (va & 4095);
        tlb.push_front({vpage, (frameBase & ~4095ULL) | (e & 4095)}); if (tlb.size() > tlbCap) tlb.pop_back(); return OK; }
};

int main() {
    std::mt19937_64 rng(193);
    { MMU m; uint64_t pa; assert(m.translate(0x1000, false, false, pa) == MMU::NOT_PRESENT);                      // 매핑 전: 폴트
      m.map4k(0x400000, 0x77, MMU::W | MMU::U); int reads; assert(m.translate(0x400123, false, true, pa, &reads) == MMU::OK && pa == (0x77ULL << 12 | 0x123) && reads == 4);          // 4 KB: 4 번
      assert(m.translate(0x400FFF, false, true, pa, &reads) == MMU::OK && reads == 0 && pa == (0x77ULL << 12 | 0xFFF));                                                              // 같은 페이지: TLB 적중, 0 번
      m.map2m(0x40000000, 0x1000, MMU::W | MMU::U); assert(m.translate(0x40000000 + 0x5ABCD, true, true, pa, &reads) == MMU::OK && pa == ((0x1000ULL << 12) + 0x5ABCD) && reads == 3);      // 2 MB: 3 번
      m.map4k(0x800000, 0x88, 0); assert(m.translate(0x800000, true, false, pa) == MMU::WRITE_PROTECT && m.translate(0x800000, false, true, pa) == MMU::USER_PROTECT && m.translate(0x800000, false, false, pa) == MMU::OK);   // 권한 폴트
      m.unmap4k(0x400000); assert(m.translate(0x400000, false, true, pa) == MMU::NOT_PRESENT); }                 // 해제 + TLB 무효화
    {   // ③ 테이블 쪽수: 서로 먼 3 영역 (각 영역은 4 단계 중 아래 3 단을 새로 만든다) + 루트
        MMU m; m.map4k(0x0000000000ULL << 12, 1, MMU::W | MMU::U); m.map4k(0x8000000000ULL, 2, MMU::W | MMU::U); m.map4k(0x700000000000ULL, 3, MMU::W | MMU::U); assert(m.tables.size() == 1 + 3 * 3);
        m.map4k(0x1000, 4, MMU::W | MMU::U); assert(m.tables.size() == 1 + 3 * 3); }                              // 같은 영역의 이웃 페이지는 쪽수를 늘리지 않는다
    {   // ① 무작위 열 vs 오라클
        MMU m(16); std::map<uint64_t, std::pair<uint64_t, uint64_t>> oracle4k; std::map<uint64_t, std::pair<uint64_t, uint64_t>> oracle2m; std::map<uint64_t, bool> dirtyA, accessedA;
        for (int step = 0; step < 200000; ++step) { uint64_t region = rng() % 8; uint64_t va = (region << 36) | ((rng() % 4096) << 12); int op = (int)(rng() % 10);
            if (op < 2) { uint64_t flags = (rng() & 1 ? MMU::W : 0) | (rng() & 1 ? MMU::U : 0); if (!oracle4k.count(va >> 12) && !oracle2m.count(va >> 21)) { uint64_t fr = rng() % 100000; m.map4k(va, fr, flags); oracle4k[va >> 12] = {fr, flags}; } }
            else if (op == 2) { uint64_t base = (region << 36) | ((rng() % 8) << 21); if (!oracle2m.count(base >> 21)) { bool clash = false; for (uint64_t pg = base >> 12; pg < (base >> 12) + 512; ++pg) clash |= oracle4k.count(pg) > 0; /* 4KB 와 겹치면 건너뜀 */ if (!clash) { uint64_t fr = (rng() % 1000) * 512; m.map2m(base, fr, MMU::W | MMU::U); oracle2m[base >> 21] = {fr, MMU::W | MMU::U}; } } }
            else if (op == 3) { m.unmap4k(va); oracle4k.erase(va >> 12); }
            else { bool write = rng() & 1, user = rng() & 1; uint64_t off = rng() % 4096, pa; MMU::Fault f = m.translate(va | off, write, user, pa);
                MMU::Fault want = MMU::NOT_PRESENT; uint64_t wantPa = 0; auto it = oracle4k.find(va >> 12);
                if (it != oracle4k.end()) { uint64_t fl = it->second.second; want = (write && !(fl & MMU::W)) ? MMU::WRITE_PROTECT : (user && !(fl & MMU::U)) ? MMU::USER_PROTECT : MMU::OK; wantPa = (it->second.first << 12) | off; }
                else { auto h = oracle2m.find(va >> 21); if (h != oracle2m.end()) { uint64_t fl = h->second.second; want = (write && !(fl & MMU::W)) ? MMU::WRITE_PROTECT : (user && !(fl & MMU::U)) ? MMU::USER_PROTECT : MMU::OK; wantPa = ((h->second.first << 12) + (va & 0x1FF000)) | off; } }
                assert(f == want); if (f == MMU::OK) assert(pa == wantPa); } } }
    {   // ④ TLB 적중률
        MMU seq(64); seq.map4k(0, 0, 0); for (int p = 0; p < 4; ++p) seq.map4k((uint64_t)p << 12, 10 + p, MMU::W | MMU::U); uint64_t pa; long total = 0; for (uint64_t a = 0; a < 4 * 4096; a += 8) { seq.translate(a, false, true, pa); ++total; } assert(seq.misses == 4 && seq.hits == total - 4 && (double)seq.hits / total >= 1 - 1.0 / 512 - 1e-12);
        MMU rnd(64); const int PAGES = 512; for (int p = 0; p < PAGES; ++p) rnd.map4k((uint64_t)p << 12, p, MMU::W | MMU::U); const int Q = 400000; for (int q = 0; q < Q; ++q) rnd.translate((rng() % PAGES) << 12, false, true, pa);
        double hit = (double)rnd.hits / Q; assert(std::fabs(hit - 64.0 / PAGES) < 0.01);
        std::cout << "PageTable: a 4-level table with 2 MB huge pages matched a std::map oracle on 2*10^5 random map/unmap/translate operations (translation, fault kind), walks cost 4/3/0 memory reads for 4 KB / 2 MB / TLB hit, 3 distant regions needed 10 table pages, and a 64-entry TLB hit " << hit << " on random access over 512 pages (ideal 0.125) and 1-1/512 on a sequential scan" << std::endl; }
    return 0;
}
// Time Complexity: 변환 O(레벨 수) = 메모리 접근 4 번 (큰 페이지 3 번, TLB 적중 0 번)
// Space Complexity: 사용한 영역 비례 (영역마다 테이블 쪽 3 개 + 공유 루트)
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
        long lo = std::max(0L, (long)std::floor(p + eLo[m])), hi = std::max(0L, std::min(n, (long)std::ceil(p + eHi[m]) + 1));          // 예측이 음수로 크게 벗어나도 구간이 배열 밖으로 나가지 않게 0 으로 고정
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
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 학습된 해시(해시 관점의 요약, 정본은 Hash.md Part 15): 해시 함수가 키를 버킷에 "고르게" 뿌리는 일은 곧 키 분포의 누적분포 CDF 를 아는 일이다 — h(x) = ⌊CDF(x)·m⌋ 이면 키가 버킷에 정확히 균등하게 놓인다.
//  일반 해시는 분포를 몰라 무작위로 뿌리므로 n = m 일 때 버킷의 약 36.8% 가 비고 키의 약 36.8% 가 이미 찬 버킷에 들어가 충돌한다. 표본에서 학습한 CDF(여기서는 표본점 1000 개 사이 선형 보간)를 쓰면 키가 규칙적으로 늘어나는 데이터(타임스탬프, 증가하는 ID, 센서 값)에서 충돌이 크게 줄어든다.
//  주의: 키가 분포에서 독립적으로 무작위로 뽑힌 값이라면 CDF(키)도 무작위라서 학습해도 이득이 없다 — 이득은 키가 "무작위보다 규칙적일 때"만 생기고, 분포가 바뀌면(drift) 다시 학습해야 한다.
//  측정(n = m = 10^5, 충돌 키 비율 = (n − 채워진 버킷 수)/n 과 최대 버킷 부하): ① 매끄러운 2 차 증가열은 학습 모델이 충돌을 1% 대로 줄이고(무작위 36.8%)  ② 지터가 있는 등간격열은 학습 14% 대 무작위 37%  ③ 균등·지수 분포의 *무작위* 키는 이득이 없다(학습 ≥ 0.9 × 무작위)
//  ④ 세 군집(간격이 큰 분포)은 충돌 비율은 줄지만 표본 해상도 때문에 최대 버킷 부하가 무작위보다 훨씬 크다 — 평균이 좋다고 최악이 좋은 것은 아니다  ⑤ *분포가 바뀌면*(키가 모델 범위 밖으로 이동) 낡은 모델은 모든 키를 마지막 버킷에 몰아 충돌 100%, 무작위 해시는 영향 없음  ⑥ 새 표본으로 다시 학습하면 회복.
static uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }
struct Model {
    std::vector<double> pts;                                                                                     // 정렬된 표본점: pts[i] 가 (i / (표본 수 − 1)) 분위수
    explicit Model(std::vector<double> sortedSample) : pts(std::move(sortedSample)) {}
    static Model train(std::vector<double> keys, size_t points = 1000) { std::sort(keys.begin(), keys.end()); std::vector<double> s; size_t step = std::max<size_t>(1, keys.size() / points); for (size_t i = 0; i < keys.size(); i += step) s.push_back(keys[i]); s.push_back(keys.back()); return Model(s); }
    double cdf(double x) const { size_t i = std::upper_bound(pts.begin(), pts.end(), x) - pts.begin(); if (!i) return 0.0; if (i == pts.size()) return 1.0 - 1e-12; double den = pts[i] - pts[i - 1], frac = den > 0 ? (x - pts[i - 1]) / den : 0.0; return ((double)(i - 1) + frac) / (double)(pts.size() - 1); }
    size_t bucket(double x, size_t m) const { return std::min<size_t>((size_t)(cdf(x) * (double)m), m - 1); }
};
size_t randomBucket(double x, size_t m) { uint64_t u; std::memcpy(&u, &x, 8); return (size_t)(mix(u) % m); }
struct Stats { double colliding; int maxLoad; };
template <class F> Stats measure(const std::vector<double>& keys, size_t m, F bucketOf) { std::vector<int> cnt(m, 0); for (double x : keys) ++cnt[bucketOf(x)]; long occupied = 0; int mx = 0; for (int c : cnt) { occupied += c > 0; mx = std::max(mx, c); } return {(double)((long)keys.size() - occupied) / (double)keys.size(), mx}; }

int main() {
    const size_t n = 100000, m = 100000; std::mt19937_64 rng(211);
    std::vector<double> ramp(n), quad(n), unif(n), expo(n), clusters(n);
    for (size_t i = 0; i < n; ++i) { ramp[i] = 3.7 * i + (i % 7) * 0.01 + 5; quad[i] = 0.7 * (double)i * (double)i + (i % 17) * 0.3 + 5; unif[i] = (double)(rng() % 1000000000) / 1000.0; expo[i] = -std::log(((double)(rng() % 1000000) + 1) / 1000001.0) * 1000; int c = (int)(i % 3); clusters[i] = (c == 0 ? 0.0 : c == 1 ? 1e6 : 5e6) + (double)(i / 3) * 0.1 + c; }
    struct Case { const char* name; const std::vector<double>* keys; } cases[] = {{"ramp", &ramp}, {"quad", &quad}, {"uniform", &unif}, {"expo", &expo}, {"clusters", &clusters}};
    Stats L[5], Rn[5];
    for (int i = 0; i < 5; ++i) { Model md = Model::train(*cases[i].keys); L[i] = measure(*cases[i].keys, m, [&](double x) { return md.bucket(x, m); }); Rn[i] = measure(*cases[i].keys, m, [&](double x) { return randomBucket(x, m); }); }
    for (int i = 0; i < 5; ++i) assert(std::fabs(Rn[i].colliding - std::exp(-1.0)) < 0.02);                         // 무작위 해시: 충돌 키 ≈ e^−1 = 36.8%
    assert(L[1].colliding < 0.03);                                                                               // ① 매끄러운 2 차열: 학습 모델이 거의 완전 해시
    assert(L[0].colliding < 0.2 && L[0].colliding < 0.6 * Rn[0].colliding);                                      // ② 지터 있는 등간격열
    assert(L[2].colliding >= 0.9 * Rn[2].colliding && L[3].colliding >= 0.9 * Rn[3].colliding);                  // ③ 무작위 키는 이득이 없다
    assert(L[4].colliding < 0.5 * Rn[4].colliding && L[4].maxLoad > 3 * Rn[4].maxLoad);                          // ④ 평균은 좋아도 최악 부하는 나쁘다
    Model stale = Model::train(ramp); std::vector<double> moved(n); for (size_t i = 0; i < n; ++i) moved[i] = ramp[i] * 1.5 + 1e6;                // ⑤ 분포가 바뀐다 (모든 키가 학습 범위 밖)
    Stats S = measure(moved, m, [&](double x) { return stale.bucket(x, m); }), SR = measure(moved, m, [&](double x) { return randomBucket(x, m); }); assert(S.colliding > 0.9999 && S.maxLoad == (int)n && std::fabs(SR.colliding - std::exp(-1.0)) < 0.02);
    Model fresh = Model::train(moved); Stats F = measure(moved, m, [&](double x) { return fresh.bucket(x, m); }); assert(F.colliding < 0.2 && std::fabs(F.colliding - L[0].colliding) < 0.02);                                        // ⑥ 다시 학습하면 회복
    std::cout << "LearnedHash (collision share, learned vs random): smooth quadratic " << L[1].colliding << " vs " << Rn[1].colliding << ", jittered ramp " << L[0].colliding << " vs " << Rn[0].colliding << ", random uniform " << L[2].colliding << " vs " << Rn[2].colliding << ", clusters " << L[4].colliding << " vs " << Rn[4].colliding << " (but max bucket " << L[4].maxLoad << " vs " << Rn[4].maxLoad << "); after drift the stale model collided " << S.colliding << " until retrained (" << F.colliding << ")" << std::endl;
    return 0;
}
// Time Complexity: 해시 계산 O(log (표본점 수)) 이분 탐색
// Space Complexity: O(표본점 수)
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
    ~XFast() { Leaf* l = n ? lvl[0][0].mn : nullptr; while (l) { Leaf* nx = l->next; delete l; l = nx; } }
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
    ~XFast() { Leaf* l = n ? lvl[0][0].mn : nullptr; while (l) { Leaf* nx = l->next; delete l; l = nx; } }
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
// (반대로 캐시 무관 B-트리(CacheObliviousBTree 항목)는 B 를 모르고도 거의 같은 성능을 낸다는 점이 대비된다)
// 검증: 모든 질의 결과가 std::lower_bound 와 같고, 읽은 캐시 라인 수를 *정확히* 센다 — n = 2^20 개 키에서 F=16 은 노드 하나가 정확히 한 라인이라 질의당 레벨 수(t16.lv.size()=5) 라인,
//  F=4 도 노드가 한 라인 안이라 레벨 수 라인, F=64 는 노드가 4 라인이라 (맨 위 레벨만 1 라인) 4·(레벨 수−1)+1 라인이고, 최적인 F=16 은 이분 탐색(약 16 라인)의 절반 미만이다
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
    double lines[3] = {0, 0, 0}; double bin = 0; int Q = 3000;
    StaticBTree t4(keys, 4), t16(keys, 16), t64(keys, 64); const StaticBTree* trees[3] = {&t4, &t16, &t64};
    for (int t = 0; t < Q; t++) {
        int q = g() % (n * 3); long want = std::lower_bound(keys.begin(), keys.end(), q) - keys.begin();
        for (int k = 0; k < 3; k++) { std::set<std::pair<int, long>> ln; long r = trees[k]->lowerBound(q, ln); assert(r == want); lines[k] += ln.size(); }          // 결과는 std::lower_bound 와 같고 읽은 라인 수를 센다
        long lo = 0, hi = n; std::set<long> bl; while (lo < hi) { long mid = (lo + hi) / 2; bl.insert(mid / 16); if (keys[mid] < q) lo = mid + 1; else hi = mid; } bin += bl.size();
    }
    for (int k = 0; k < 3; k++) lines[k] /= Q; bin /= Q;
    assert(lines[1] <= lines[0] && lines[1] <= lines[2] && lines[1] * 2 < bin);        // F = 16(라인 크기)이 최소, 이분 탐색의 절반 미만
    assert(lines[1] == (double)t16.lv.size() && lines[0] == (double)t4.lv.size() && lines[2] == 4.0 * (t64.lv.size() - 1) + 1);   // 라인 수 자체도 정확히 (노드당 라인 수 x 레벨 수)
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
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <list>
#include <random>
#include <unordered_map>
#include <vector>

// 캐시 인지(cache-aware): 캐시 블록 크기 L 과 용량 M(줄 수)을 알고 그 값에 맞춰 알고리즘을 조정한다(타일 크기 = 캐시에 맞춘 값). 캐시 무관(cache-oblivious): L 과 M 을 코드에서 모르는 채 "문제를 재귀적으로 반으로 나누기" 만으로
//  모든 캐시 수준에서 동시에 거의 최적이 되도록 설계한다.  행렬 전치(N×N)와 곱셈으로 확인한다 — 읽는 쪽은 행 단위로 연속이지만 쓰는 쪽은 열 단위라 단순 이중 루프는 쓸 때마다 새 캐시 줄을 건드린다.
//  측정 도구는 접근 열(trace)을 만들고 *완전 연관 LRU 캐시*에 흘려 넣는 시뮬레이터다 — 시간이 아니라 미스 횟수를 센다(결정적).  ① 시뮬레이터 검증: 무작위 접근 열 200 개에서 독립 오라클(스택 거리: LRU 스택에서 깊이 ≥ M 이면 미스)과 미스 수가 같다
//  ② 전치(N = 512) 를 캐시 9 가지 (M ∈ {16, 64, 256} 줄 × L ∈ {4, 8, 16} 워드) 에서: 모든 타일 크기 T 중 최선(인지형이 *알고 고른* 값) 대비 재귀 버전이 1.5 배 이내이고 이론 하한 2N²/L(콜드 미스) 이상  ③ 인지형의 약점: T = 8 로 고정한 코드는 다른 캐시에서 최선보다 1.4 배 이상 나쁘고, 타일이 캐시보다 크면 단순 루프에 가까워진다
//  ④ 곱셈 C += A·B (N = 48): 단순 ijk 루프는 재귀(가장 긴 차원을 반으로)보다 3 배 이상 많은 미스.
struct Cache {
    size_t cap, L; std::list<long> lru; std::unordered_map<long, std::list<long>::iterator> where; long miss = 0;
    Cache(size_t capacityLines, size_t lineWords) : cap(capacityLines), L(lineWords) {}
    void touch(long addr) { long blk = addr / (long)L; auto it = where.find(blk); if (it != where.end()) lru.erase(it->second); else { ++miss; if (lru.size() == cap) { where.erase(lru.back()); lru.pop_back(); } } lru.push_front(blk); where[blk] = lru.begin(); }
};
struct Trace { std::vector<long> a; void touch(long x) { a.push_back(x); } };
long replay(const Trace& t, size_t M, size_t L) { Cache c(M, L); for (long x : t.a) c.touch(x); return c.miss; }
long stackDistanceMisses(const Trace& t, size_t M, size_t L) { std::vector<long> stack; long miss = 0; for (long x : t.a) { long blk = x / (long)L; size_t i = 0; while (i < stack.size() && stack[i] != blk) ++i; if (i >= M || i == stack.size()) ++miss; if (i < stack.size()) stack.erase(stack.begin() + i); stack.insert(stack.begin(), blk); if (stack.size() > M) stack.pop_back(); } return miss; }

const int N = 512;
void access(Trace& t, int i, int j) { t.touch((long)i * N + j); t.touch((long)N * N + (long)j * N + i); }                  // B[j][i] = A[i][j]
Trace naive() { Trace t; for (int i = 0; i < N; ++i) for (int j = 0; j < N; ++j) access(t, i, j); return t; }
Trace tiled(int T) { Trace t; for (int ii = 0; ii < N; ii += T) for (int jj = 0; jj < N; jj += T) for (int i = ii; i < ii + T; ++i) for (int j = jj; j < jj + T; ++j) access(t, i, j); return t; }
void rec(Trace& t, int i0, int i1, int j0, int j1) { int di = i1 - i0, dj = j1 - j0; if (di == 1 && dj == 1) { access(t, i0, j0); return; } if (di >= dj) { int m = (i0 + i1) / 2; rec(t, i0, m, j0, j1); rec(t, m, i1, j0, j1); } else { int m = (j0 + j1) / 2; rec(t, i0, i1, j0, m); rec(t, i0, i1, m, j1); } }
Trace oblivious() { Trace t; rec(t, 0, N, 0, N); return t; }
const int Q = 48;                                                                                                // 행렬 곱 C[i][j] += A[i][k] · B[k][j]
void mulAccess(Trace& t, int i, int j, int k) { t.touch((long)i * Q + k); t.touch((long)Q * Q + (long)k * Q + j); t.touch(2L * Q * Q + (long)i * Q + j); }
Trace mulNaive() { Trace t; for (int i = 0; i < Q; ++i) for (int j = 0; j < Q; ++j) for (int k = 0; k < Q; ++k) mulAccess(t, i, j, k); return t; }
void mulRec(Trace& t, int i0, int i1, int j0, int j1, int k0, int k1) { int di = i1 - i0, dj = j1 - j0, dk = k1 - k0; if (di == 1 && dj == 1 && dk == 1) { mulAccess(t, i0, j0, k0); return; }
    if (di >= dj && di >= dk) { int m = (i0 + i1) / 2; mulRec(t, i0, m, j0, j1, k0, k1); mulRec(t, m, i1, j0, j1, k0, k1); } else if (dj >= dk) { int m = (j0 + j1) / 2; mulRec(t, i0, i1, j0, m, k0, k1); mulRec(t, i0, i1, m, j1, k0, k1); } else { int m = (k0 + k1) / 2; mulRec(t, i0, i1, j0, j1, k0, m); mulRec(t, i0, i1, j0, j1, m, k1); } }
Trace mulOblivious() { Trace t; mulRec(t, 0, Q, 0, Q, 0, Q); return t; }

int main() {
    std::mt19937 rng(223);
    for (int it = 0; it < 200; ++it) { Trace t; int n = 1 + (int)(rng() % 400), span = 1 + (int)(rng() % 120); for (int i = 0; i < n; ++i) t.touch((long)(rng() % span)); size_t M = 1 + rng() % 12, L = 1 + rng() % 4; assert(replay(t, M, L) == stackDistanceMisses(t, M, L)); }          // ① 시뮬레이터 검증
    { Trace t; for (long x : {0, 1, 2, 3, 4, 0, 8}) t.touch(x); assert(replay(t, 2, 4) == 3 && stackDistanceMisses(t, 2, 4) == 3); }                  // 블록 0,0,0,0,1,0,2 → 미스 3 번
    Trace tNaive = naive(), tObl = oblivious(); std::vector<int> tiles = {1, 2, 4, 8, 16, 32, 64, 128}; std::vector<Trace> tTile; for (int T : tiles) tTile.push_back(tiled(T)); assert(tNaive.a.size() == tObl.a.size());
    int worseThanBestWithT8 = 0; double worstOblivious = 0; bool tooBigHurts = false;
    for (size_t M : {16, 64, 256}) for (size_t L : {4, 8, 16}) {
        long best = 1L << 60; int bestT = 0; std::vector<long> byT; for (size_t k = 0; k < tiles.size(); ++k) { long m = replay(tTile[k], M, L); byT.push_back(m); if (m < best) { best = m; bestT = tiles[k]; } }
        long ob = replay(tObl, M, L), nv = replay(tNaive, M, L), lower = 2L * N * N / (long)L; assert(ob >= lower && best >= lower && ob <= 1.5 * best);                // ② 재귀는 최선 타일의 1.5 배 이내
        worstOblivious = std::max(worstOblivious, (double)ob / best); if ((double)byT[3] >= 1.4 * best) ++worseThanBestWithT8;                                               // ③ T = 8 고정은 환경이 바뀌면 나쁘다
        if (M == 16 && L == 8 && (double)byT[7] >= 1.5 * best && nv >= byT[7]) tooBigHurts = true; if (M == 64 && L == 8) assert(nv > 3 * ob);
        (void)bestT; }
    assert(worseThanBestWithT8 >= 1 && tooBigHurts);
    Trace m1 = mulNaive(), m2 = mulOblivious(); long naiveMiss = replay(m1, 64, 8), recMiss = replay(m2, 64, 8); assert(m1.a.size() == m2.a.size() && naiveMiss > 3 * recMiss);                                      // ④
    std::cout << "Cache-Aware vs Cache-Oblivious: the LRU simulator matched an independent stack-distance oracle on 200 random traces; for 512x512 transpose on 9 cache shapes the recursive layout-free code stayed within " << worstOblivious << "x of the best hand-tuned tile (fixed tile T=8 was 1.4x+ worse in " << worseThanBestWithT8 << " shapes), and 48^3 matrix multiply missed " << naiveMiss << " times naively vs " << recMiss << " recursively" << std::endl;
    return 0;
}
// Time Complexity: 전치 O(N²) 연산, 캐시 미스는 인지형·무관형 모두 O(N²/L) (곱셈은 O(N³ / (L·√M)))
// Space Complexity: O(N²)
```
## Immutable vs Persistent
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 불변(immutable) 자료구조: 만들어진 뒤 절대 변하지 않는다. 그래서 스레드 사이에 잠금 없이 공유할 수 있다. 하지만 "수정" 이 필요하면 전체를 새로 복사해야 하니 O(N).
// 영속(persistent) 자료구조: 수정하면 새 버전이 생기되 옛 버전도 계속 쓸 수 있고, 두 버전이 변하지 않은 부분을 공유하므로 수정 비용이 O(log N) 이다. 영속 = "불변 + 구조 공유로 갱신을 싸게 만든 것".
// 수정 가능한(ephemeral) 구조는 옛 버전이 사라지고, 영속 구조는 모든 버전이 남는다 -> 실행 취소, 시간 여행 질의, 분기 탐색, 락프리 읽기. 대가는 갱신마다 O(log N) 노드 할당과 가비지 수집이다
struct Node { std::shared_ptr<const Node> l, r; int val; };
typedef std::shared_ptr<const Node> P; long allocated = 0;
P build(int lo, int hi) { allocated++; if (lo == hi) return std::make_shared<const Node>(Node{nullptr, nullptr, 0}); int m = (lo + hi) / 2; return std::make_shared<const Node>(Node{build(lo, m), build(m + 1, hi), 0}); }
P setAt(const P& t, int lo, int hi, int i, int v) { allocated++; if (lo == hi) return std::make_shared<const Node>(Node{nullptr, nullptr, v}); int m = (lo + hi) / 2;
    return i <= m ? std::make_shared<const Node>(Node{setAt(t->l, lo, m, i, v), t->r, 0}) : std::make_shared<const Node>(Node{t->l, setAt(t->r, m + 1, hi, i, v), 0}); }
int getAt(P t, int lo, int hi, int i) { while (lo < hi) { int m = (lo + hi) / 2; if (i <= m) { t = t->l; hi = m; } else { t = t->r; lo = m + 1; } } return t->val; }
int main() {
    const int N = 4096, U = 1000; std::mt19937 g(1);
    std::vector<int> immutableCopy(N, 0); long copied = 0; std::vector<std::vector<int>> versionsCopy = {immutableCopy};     // 불변 벡터: 수정 = 전체 복사
    P root = build(0, N - 1); allocated = 0; std::vector<P> versions = {root};
    for (int u = 0; u < U; u++) { int i = g() % N, v = g(); auto c = versionsCopy.back(); c[i] = v; copied += N; versionsCopy.push_back(std::move(c)); versions.push_back(setAt(versions.back(), 0, N - 1, i, v)); }
    for (int t = 0; t < 5000; t++) { int ver = g() % versions.size(), i = g() % N; assert(getAt(versions[ver], 0, N - 1, i) == versionsCopy[ver][i]); }       // 두 방식 모두 모든 옛 버전이 그대로
    assert(allocated <= (long)U * 14 && copied == (long)U * N);            // 영속: 갱신당 노드 약 13 개, 불변 복사: 갱신당 4096 칸
    std::cout << "after " << U << " updates of " << N << " cells: full-copy immutable wrote " << copied << " cells, persistent tree allocated " << allocated << " nodes (" << (double)copied / allocated << "x less), all " << versions.size() << " versions intact" << std::endl; return 0;
}
// Time Complexity: 전체 복사 갱신 O(N), 영속 갱신 O(log N)
// Space Complexity: 영속 버전당 O(log N)
```
## Lock-Free vs Wait-Free
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cassert>
#include <iostream>
#include <thread>
#include <vector>

// 진행 보장의 세 단계. 블로킹(잠금): 잠금을 쥔 스레드가 멈추면 모두 멈춘다.  락프리(lock-free): 어떤 시점에도 "적어도 한 스레드는" 유한 단계 안에 연산을 끝낸다(시스템 전체의 진행 보장, 개별 스레드는 굶을 수 있다).
//  웨이트프리(wait-free): "모든 스레드가" 다른 스레드와 무관하게 유한한(상한이 있는) 단계 안에 끝낸다.  CAS 재시도 루프는 락프리이지만 웨이트프리가 아니다 — 경쟁에서 계속 지는 스레드가 있을 수 있다.
//  fetch_add 같은 하드웨어 원자 명령 한 번으로 끝나는 연산은 웨이트프리이다.  여기서는 스레드 둘의 명령 단위 상태 기계를 만들고 *모든 스케줄을 전수 탐색*해 두 성질을 숫자로 가른다.
//  CAS 증가 연산 = [읽기] → [CAS(읽은 값, +1)] (실패하면 처음부터), fetch_add 연산 = [fetch_add] 한 단계.  스케줄 = 매 단계 어느 스레드가 한 명령을 실행하는지의 열 (길이 S 인 2^S 가지를 전부 본다).
//  ① 락프리 성질: 모든 스케줄에서 *성공한 CAS 가 하나도 없는 연속 구간*의 최대 길이가 상수(3 단계)로 묶인다 — 실패한 CAS 는 그 사이 다른 스레드의 성공이 있었다는 뜻이므로  ② 웨이트프리 위반: 스레드 B 가 *자기 명령을 정확히 S/2 개 실행하고도* 연산을 하나도 못 끝내는 스케줄이 존재하며(매 라운드 A.읽기, B.읽기, A.CAS 성공, B.CAS 실패) S 에 비례해 늘어난다
//  ③ fetch_add 는 모든 스케줄에서 스레드가 자기 명령 하나마다 연산을 하나씩 끝낸다(상한 1)  ④ 정확성: 모든 스케줄에서 최종 카운터 = 성공한 연산 수  ⑤ 실제 스레드 4 개의 CAS / fetch_add 카운터가 정확하다(진행 보장은 정확성과 별개).
// audit: exhaustive (두 스레드의 *모든* 스케줄을 길이 20 까지 전수 탐색)
struct Sim {
    long x = 0; int pc[2] = {0, 0}; long seen[2] = {0, 0}; long done[2] = {0, 0}; long failed[2] = {0, 0}; long ownSteps[2] = {0, 0}; long sinceDone[2] = {0, 0}; long maxSinceDone[2] = {0, 0}; long sinceSuccess = 0, maxSinceSuccess = 0;
    void stepCas(int t) { ++ownSteps[t]; ++sinceDone[t]; ++sinceSuccess;
        if (pc[t] == 0) { seen[t] = x; pc[t] = 1; } else { if (x == seen[t]) { x = seen[t] + 1; ++done[t]; sinceDone[t] = 0; sinceSuccess = 0; } else ++failed[t]; pc[t] = 0; }
        maxSinceDone[t] = std::max(maxSinceDone[t], sinceDone[t]); maxSinceSuccess = std::max(maxSinceSuccess, sinceSuccess); }
    void stepFetchAdd(int t) { ++ownSteps[t]; ++x; ++done[t]; sinceDone[t] = 0; sinceSuccess = 0; maxSinceDone[t] = std::max(maxSinceDone[t], 1L); maxSinceSuccess = std::max(maxSinceSuccess, 1L); }
};
struct Result { long worstWindow = 0, worstStarvationB = 0, maxDoneA = 0; bool exactCounter = true; long schedules = 0; };
Result explore(int S, bool useFetchAdd) {
    Result r; for (unsigned mask = 0; mask < (1u << S); ++mask) { Sim s; for (int i = 0; i < S; ++i) { int t = (mask >> i) & 1; if (useFetchAdd) s.stepFetchAdd(t); else s.stepCas(t); }
        r.worstWindow = std::max(r.worstWindow, s.maxSinceSuccess); r.worstStarvationB = std::max(r.worstStarvationB, s.maxSinceDone[1]); r.maxDoneA = std::max(r.maxDoneA, s.done[0]); r.exactCounter &= (s.x == s.done[0] + s.done[1]); ++r.schedules; } return r; }

int main() {
    long prevStarve = 0;
    for (int S : {8, 12, 16, 20}) {
        Result c = explore(S, false), f = explore(S, true); assert(c.schedules == (1L << S) && c.exactCounter && f.exactCounter);                                              // ④ 정확성: 모든 스케줄에서
        assert(c.worstWindow <= 3);                                                                                                  // ① 락프리: 성공 없는 구간은 3 단계 이하
        assert(c.worstStarvationB == S / 2 && c.worstStarvationB > prevStarve);                                                    // ② B 가 굶는 스케줄이 존재하고(자기 명령 S/2 개), 길이에 비례해 늘어난다
        assert(f.worstStarvationB == 1 && f.worstWindow == 1);                                                                       // ③ fetch_add: 명령 하나마다 연산 하나 — 상한 1
        prevStarve = c.worstStarvationB; std::cout << "S=" << S << ": CAS loop worst no-success window " << c.worstWindow << ", thread B starved for " << c.worstStarvationB << " of its own steps; fetch_add: window " << f.worstWindow << ", starvation " << f.worstStarvationB << std::endl; }
    {   Sim s; for (int r = 0; r < 1000; ++r) { s.stepCas(0); s.stepCas(1); s.stepCas(0); s.stepCas(1); } assert(s.x == 1000 && s.done[0] == 1000 && s.done[1] == 0 && s.failed[1] == 1000); }                                  // 손으로 짠 일정 A.읽기 B.읽기 A.CAS B.CAS: B 는 1000 번 모두 실패
    {   std::atomic<long> cas(0), fa(0); std::vector<std::thread> th;                                                                // ⑤ 실제 스레드
        for (int t = 0; t < 4; ++t) th.emplace_back([&] { for (int i = 0; i < 50000; ++i) { long v = cas.load(); while (!cas.compare_exchange_weak(v, v + 1)) {} fa.fetch_add(1); } });
        for (auto& t : th) t.join(); assert(cas.load() == 200000 && fa.load() == 200000); }
    std::cout << "Lock-Free vs Wait-Free: exhaustive schedules of two threads showed the CAS loop is lock-free (no more than 3 steps without a success) but not wait-free (thread B can starve for any number of its own steps), while fetch_add completes one operation per step" << std::endl;
    return 0;
}
// Time Complexity: CAS 루프: 경쟁 시 한 스레드의 재시도에 상한이 없다(락프리), fetch_add: O(1) 웨이트프리
// Space Complexity: O(1)
```
## Online vs Offline 자료구조
### 대표코드
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 온라인(online): 질의를 하나씩 받아 그때그때 답해야 한다(미래를 모름).  오프라인(offline): 질의 전체를 미리 알고 순서를 바꾸거나 한꺼번에 처리해도 된다.
// 같은 문제도 오프라인이면 더 단순하고 가볍게 풀리는 경우가 많다. 최소 공통 조상(LCA)으로 비교한다 — 온라인: 이진 도약(binary lifting) 표 O(N log N) 공간, 질의마다 O(log N).
// 오프라인: Tarjan 알고리즘 — 트리를 DFS 하며 서로소 집합(Union-Find)만 쓰고 질의 두 끝점이 모두 방문된 순간 답한다. O(N) 공간(질의 목록 제외), 거의 O(1) 분할상환.
// 대가: 질의를 미리 모두 알아야 하고 결과 순서가 방문 순서와 달라 되돌려 놓아야 한다.  (다른 예: 간선 삭제가 있는 연결성 — 온라인은 어렵지만 오프라인은 시간 분할 정복 + 롤백 DSU 로 쉽다)
int main() {
    std::mt19937 g(2); const int N = 5000, Q = 10000; std::vector<int> par(N, -1), depth(N, 0); std::vector<std::vector<int>> kids(N);
    for (int i = 1; i < N; i++) { par[i] = g() % i; depth[i] = depth[par[i]] + 1; kids[par[i]].push_back(i); }
    std::vector<std::pair<int, int>> qs(Q); for (auto& q : qs) q = {(int)(g() % N), (int)(g() % N)};
    int LOG = 1; while ((1 << LOG) < N) LOG++; std::vector<std::vector<int>> up(LOG, std::vector<int>(N, 0));        // 온라인: 이진 도약 표
    for (int i = 0; i < N; i++) up[0][i] = par[i] < 0 ? i : par[i]; for (int k = 1; k < LOG; k++) for (int i = 0; i < N; i++) up[k][i] = up[k - 1][up[k - 1][i]];
    auto lcaOnline = [&](int a, int b) { if (depth[a] < depth[b]) std::swap(a, b); for (int k = 0; k < LOG; k++) if ((depth[a] - depth[b]) >> k & 1) a = up[k][a]; if (a == b) return a;
        for (int k = LOG - 1; k >= 0; k--) if (up[k][a] != up[k][b]) { a = up[k][a]; b = up[k][b]; } return up[0][a]; };
    std::vector<int> online(Q); for (int i = 0; i < Q; i++) online[i] = lcaOnline(qs[i].first, qs[i].second);
    std::vector<int> dsu(N), anc(N), offline(Q, -1); std::iota(dsu.begin(), dsu.end(), 0); std::iota(anc.begin(), anc.end(), 0); std::vector<char> visited(N, 0);      // 오프라인: Tarjan
    std::vector<std::vector<std::pair<int, int>>> at(N); for (int i = 0; i < Q; i++) { at[qs[i].first].push_back({qs[i].second, i}); at[qs[i].second].push_back({qs[i].first, i}); }
    std::function<int(int)> find = [&](int x) { return dsu[x] == x ? x : dsu[x] = find(dsu[x]); };
    std::function<void(int)> dfs = [&](int u) { visited[u] = 1; for (int c : kids[u]) { dfs(c); dsu[find(c)] = find(u); anc[find(u)] = u; }
        for (auto& pr : at[u]) if (visited[pr.first] && offline[pr.second] < 0) offline[pr.second] = anc[find(pr.first)]; };
    dfs(0);
    assert(online == offline);                                             // 두 방식의 답이 같다
    long onlineWords = (long)LOG * N, offlineWords = 2L * N;               // 보조 구조 크기 (워드 수)
    assert(offlineWords * 4 < onlineWords);
    std::cout << "LCA of " << Q << " queries on a " << N << "-node tree: identical answers; auxiliary memory online " << onlineWords << " words (binary lifting) vs offline " << offlineWords << " words (union-find)" << std::endl; return 0;
}
// Time Complexity: 온라인 질의당 O(log N), 오프라인 전체 O((N + Q) α(N))
// Space Complexity: 온라인 O(N log N), 오프라인 O(N + Q)
```
## Static vs Dynamic 자료구조
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 정적(static): 한 번 만들고 읽기만 한다 -> 갱신 지원을 버린 대가로 더 작고 빠르고 단순하다(희소 표 O(1) 질의, 정렬 배열 + 이분 탐색, 완전 해시, 성기게 압축된 비트열).
// 동적(dynamic): 삽입·삭제·갱신을 지원하는 대신 포인터·여유 공간·균형 정보 같은 비용을 낸다. 선택 기준은 "읽기 대 쓰기 비율".  구간 최솟값(RMQ)으로 비교한다:
// 희소 표: 질의 2 번 조회, 하지만 값이 하나 바뀌면 표를 다시 짓는다 O(N log N).  세그먼트 트리: 질의·갱신 모두 O(log N).  LSM 의 SSTable 이 정적 구조이고 변경은 새 정적 구조로 병합하는 것도 같은 생각이다
long ops = 0;
struct Sparse { std::vector<std::vector<int>> t; std::vector<int> lg; explicit Sparse(const std::vector<int>& a) { int n = a.size(); lg.assign(n + 1, 0); for (int i = 2; i <= n; i++) lg[i] = lg[i / 2] + 1; t.push_back(a);
        for (int k = 1; (1 << k) <= n; k++) { t.emplace_back(n - (1 << k) + 1); for (int i = 0; i + (1 << k) <= n; i++) { t[k][i] = std::min(t[k - 1][i], t[k - 1][i + (1 << (k - 1))]); ops++; } } }
    int query(int l, int r) const { int k = lg[r - l + 1]; ops += 2; return std::min(t[k][l], t[k][r - (1 << k) + 1]); } };
struct Seg { int n; std::vector<int> t; explicit Seg(const std::vector<int>& a) : n(a.size()), t(2 * a.size()) { for (int i = 0; i < n; i++) t[n + i] = a[i]; for (int i = n - 1; i > 0; i--) t[i] = std::min(t[2 * i], t[2 * i + 1]); }
    void set(int p, int v) { for (t[p += n] = v; p > 1; p >>= 1) { t[p >> 1] = std::min(t[p], t[p ^ 1]); ops++; } }
    int query(int l, int r) { int res = 1 << 30; for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) { if (l & 1) { res = std::min(res, t[l++]); ops++; } if (r & 1) { res = std::min(res, t[--r]); ops++; } } return res; } };
long runStatic(std::vector<int> a, int Q, int U, std::mt19937& g) {            // 갱신마다 희소 표를 다시 지음
    ops = 0; Sparse s(a); int n = a.size(); for (int i = 0; i < Q + U; i++) { if (i % ((Q + U) / std::max(U, 1)) == 0 && U > 0 && i / ((Q + U) / U) < U) { a[g() % n] = g() % 1000; s = Sparse(a); } else { int l = g() % n, r = g() % n; if (l > r) std::swap(l, r); s.query(l, r); } } return ops;
}
long runDynamic(std::vector<int> a, int Q, int U, std::mt19937& g) {
    ops = 0; Seg s(a); int n = a.size(); for (int i = 0; i < Q + U; i++) { if (i % ((Q + U) / std::max(U, 1)) == 0 && U > 0 && i / ((Q + U) / U) < U) s.set(g() % n, g() % 1000); else { int l = g() % n, r = g() % n; if (l > r) std::swap(l, r); s.query(l, r); } } return ops;
}
int main() {
    std::mt19937 g(1); const int N = 1 << 12; std::vector<int> a(N); for (auto& x : a) x = g() % 1000; const int Q = 20000;
    std::mt19937 g1(5), g2(5); long s0 = runStatic(a, Q, 0, g1), d0 = runDynamic(a, Q, 0, g2);
    std::mt19937 g3(6), g4(6); long s1 = runStatic(a, Q, 200, g3), d1 = runDynamic(a, Q, 200, g4);
    assert(s0 < d0);                                                       // 갱신이 없으면 정적 구조가 이긴다
    assert(s1 > d1 * 5);                                                   // 갱신이 조금만 있어도 매번 다시 짓는 정적 구조는 크게 진다
    std::cout << "RMQ, N=" << N << ", " << Q << " queries: no updates -> static " << s0 << " vs dynamic " << d0 << " node operations; with 200 updates -> static " << s1 << " vs dynamic " << d1 << std::endl; return 0;
}
// Time Complexity: 정적 질의 O(1)·갱신 시 재구성 O(N log N), 동적 질의·갱신 O(log N)
// Space Complexity: 정적 O(N log N), 동적 O(N)
```
## Internal Memory vs External Memory
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

// 내부 메모리 모델(RAM)은 모든 접근이 같은 비용이라고 보고 연산 횟수를 센다. 외부 메모리(I/O) 모델은 데이터가 디스크에 있고 한 번에 블록 B 개 원소를 옮기며 메모리에는 M 개만 들어간다고 보고 "블록 전송 횟수" 를 센다 —
// 디스크 한 번 접근이 CPU 연산 수십만 번의 시간이기 때문이다.  정렬의 I/O 하한은 Θ((N/B) log_{M/B}(N/B)) 이고, 외부 병합 정렬(M 크기 런을 만든 뒤 (M/B-1)-way 병합)이 그것을 달성한다.
// 반면 RAM 에서 최적인 힙 정렬은 접근이 배열 전체를 뛰어다녀 거의 모든 접근이 블록 미스이다.  같은 O(N log N) 알고리즘이 외부 메모리에서는 수십 배 느릴 수 있다는 것(여기서 N=2^18 일 때 약 68 배, 단언은 20 배 초과)을 I/O 횟수로 확인한다.
// 측정 방식: 힙 정렬의 I/O 는 M/B 블록짜리 LRU 캐시(Cache)를 거친 접근마다 세는 *측정*이고, 외부 병합 정렬의 I/O 는 런 형성·병합 때마다 읽고 쓴 블록 수를 더하는 *계산*(blocks())이다 — 순차 접근이라 블록 수가 곧 I/O 이다.
// 검증: 병합 정렬 I/O 가 공식 2·(N/B)·(1+패스 수) 와 *정확히* 같고(런 형성 읽기+쓰기, 패스마다 읽기+쓰기), 패스 수가 ceil(log_F(N/M)) 이며, 병합 팬인 F+1 개 블록 버퍼가 메모리 M 안에 들어간다
const int B = 64, M = 4096, N = 1 << 18;
long blocks(long n) { return (n + B - 1) / B; }
struct Cache { size_t cap; std::list<long> lru; std::unordered_map<long, std::list<long>::iterator> where; long miss = 0; explicit Cache(size_t c) : cap(c) {}
    void touch(long idx) { long blk = idx / B; auto it = where.find(blk); if (it != where.end()) lru.erase(it->second); else { miss++; if (lru.size() == cap) { where.erase(lru.back()); lru.pop_back(); } } lru.push_front(blk); where[blk] = lru.begin(); } };
long heapSortIO(std::vector<int> a) {                                      // 제자리 힙 정렬을 M/B 블록짜리 LRU 캐시 위에서 실행
    Cache c(M / B); long n = a.size();
    auto rd = [&](long i) { c.touch(i); return a[i]; }; auto wr = [&](long i, int v) { c.touch(i); a[i] = v; };
    auto sift = [&](long root, long end) { for (;;) { long ch = 2 * root + 1; if (ch >= end) break; if (ch + 1 < end && rd(ch) < rd(ch + 1)) ch++; if (rd(root) >= rd(ch)) break; int t = rd(root); wr(root, rd(ch)); wr(ch, t); root = ch; } };
    for (long i = n / 2 - 1; i >= 0; i--) sift(i, n);
    for (long e = n - 1; e > 0; e--) { int t = rd(0); wr(0, rd(e)); wr(e, t); sift(0, e); }
    assert(std::is_sorted(a.begin(), a.end())); return c.miss;
}
long externalMergeSortIO(const std::vector<int>& in, int& passes) {
    long io = 0; std::vector<std::vector<int>> runs;
    for (size_t i = 0; i < in.size(); i += M) { std::vector<int> r(in.begin() + i, in.begin() + std::min(in.size(), i + M)); io += blocks(r.size()); std::sort(r.begin(), r.end()); io += blocks(r.size()); runs.push_back(r); }      // 1 단계: 메모리 크기 런 (읽기+쓰기)
    const size_t F = M / B - 1; passes = 0; assert((F + 1) * B <= M);      // 입력 버퍼 F 개 + 출력 버퍼 1 개가 메모리에 들어간다
    while (runs.size() > 1) { std::vector<std::vector<int>> next; passes++;
        for (size_t g = 0; g < runs.size(); g += F) { size_t e = std::min(runs.size(), g + F); using E = std::pair<int, std::pair<size_t, size_t>>; std::priority_queue<E, std::vector<E>, std::greater<E>> pq; std::vector<int> out;
            for (size_t r = g; r < e; r++) { io += blocks(runs[r].size()); pq.push({runs[r][0], {r, 0}}); }          // 입력 런 읽기
            while (!pq.empty()) { auto t = pq.top(); pq.pop(); out.push_back(t.first); size_t r = t.second.first, i = t.second.second + 1; if (i < runs[r].size()) pq.push({runs[r][i], {r, i}}); }
            io += blocks(out.size()); next.push_back(out); }                                                         // 출력 쓰기
        runs = next; }
    assert(runs.size() == 1 && std::is_sorted(runs[0].begin(), runs[0].end()) && runs[0].size() == in.size()); return io;
}
int main() {
    std::mt19937 g(1); std::vector<int> data(N); for (auto& x : data) x = g();
    int passes = 0; long ext = externalMergeSortIO(data, passes), heap = heapSortIO(data); double bound = (double)N / B * (1 + std::max(1.0, std::ceil(std::log((double)N / M) / std::log((double)M / B - 1))));
    assert(passes == (int)std::ceil(std::log((double)(N / M)) / std::log(M / B - 1.0)) && ext == 2L * (N / B) * (1 + passes) && ext <= 2 * bound);      // 정확한 I/O 공식 (N/B=4096, 2 패스: 24576)
    assert(heap > ext * 20);                                                // 같은 캐시 규칙에서 힙 정렬은 20 배 넘게 더 많은 블록 전송
    std::cout << "sorting " << N << " ints (B=" << B << ", M=" << M << "): external merge sort " << ext << " block I/Os vs in-place heapsort through the same cache " << heap << " (" << heap / ext << "x more)" << std::endl; return 0;
}
// Time Complexity: 외부 병합 정렬 I/O O((N/B) log_{M/B}(N/B)), 힙 정렬 I/O O(N log (N/M))
// Space Complexity: O(N) 디스크 + O(M) 메모리
```
## Exact vs Approximate 자료구조
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <cassert>

// 정확한 자료구조는 원소 수에 비례하는 공간을 쓴다(집합 = 키를 전부 저장, 빈도표 = 키와 횟수를 전부). 근사 자료구조는 "작은 오차를 허용하면" 공간을 원소 수와 거의 무관하게 고정하거나 몇 십 분의 일로 줄인다.
//   집합 소속: 블룸 필터 (거짓 양성만, 키당 ~10 비트)   서로 다른 개수: HyperLogLog (±1~2%, 16 KB 고정)   빈도: 카운트-민 스케치 (과대 추정만, ε·N 이내)
// 같은 스트림에 정확 구조와 근사 구조를 모두 적용해 메모리와 오차를 나란히 잰다. 근사의 오차는 마음대로가 아니라 이론으로 보장된 한계(파라미터 ε, δ, p)를 갖는다는 것이 핵심이다
static inline uint64_t mix(uint64_t x) { x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL; return x ^ (x >> 31); }
int main() {
    std::mt19937_64 g(7); const int K = 200000, EVENTS = 600000; std::vector<double> w(K); for (int i = 0; i < K; i++) w[i] = 1.0 / std::pow(i + 1, 0.9);
    std::discrete_distribution<int> zipf(w.begin(), w.end());
    std::unordered_map<uint64_t, uint32_t> exactFreq; std::unordered_set<uint64_t> exactSet;
    const int p = 14; std::vector<uint8_t> hll(1 << p, 0);                                                  // HyperLogLog 16 KB
    const size_t mb = (size_t)(K * 9.6); std::vector<uint64_t> bloom((mb + 63) / 64, 0); const int bk = 7;      // 블룸 필터 ~9.6 비트/키 (등록 키 수 = 서로 다른 키 수)
    const double eps = 0.001; const size_t cw = (size_t)std::ceil(std::exp(1.0) / eps), cd = 5; std::vector<std::vector<uint32_t>> cms(cd, std::vector<uint32_t>(cw, 0));        // 카운트-민
    std::vector<uint64_t> distinctKeys;
    for (int e = 0; e < EVENTS; e++) {
        uint64_t key = (uint64_t)zipf(g) * 1000003ULL + 17; if (!exactFreq.count(key)) distinctKeys.push_back(key); exactFreq[key]++; exactSet.insert(key);
        uint64_t h = mix(key); size_t idx = h >> (64 - p); uint64_t ww = (h << p) | (1ULL << (p - 1)); uint8_t rho = __builtin_clzll(ww) + 1; if (rho > hll[idx]) hll[idx] = rho;
        for (int i = 0; i < bk; i++) { size_t pos = (mix(key) + (uint64_t)i * (mix(~key) | 1)) % mb; bloom[pos >> 6] |= 1ULL << (pos & 63); }
        for (size_t i = 0; i < cd; i++) cms[i][mix(key ^ (i * 0x9e3779b97f4a7c15ULL + 1)) % cw]++;
    }
    double alpha = 0.7213 / (1 + 1.079 / (1 << p)), sum = 0; size_t zeros = 0; for (uint8_t r : hll) { sum += std::ldexp(1.0, -r); zeros += r == 0; } double est = alpha * (1 << p) * (1 << p) / sum; if (est <= 2.5 * (1 << p) && zeros) est = (1 << p) * std::log((double)(1 << p) / zeros);
    double hllErr = std::fabs(est - (double)exactSet.size()) / exactSet.size(); assert(hllErr < 0.03);
    long fp = 0, T = 100000; for (long i = 0; i < T; i++) { uint64_t key = (1ULL << 50) + i; bool in = true; for (int j = 0; j < bk; j++) { size_t pos = (mix(key) + (uint64_t)j * (mix(~key) | 1)) % mb; if (!((bloom[pos >> 6] >> (pos & 63)) & 1)) { in = false; break; } } fp += in; }
    double fpr = (double)fp / T; assert(fpr < 0.02);
    long over = 0; for (auto& kv : exactFreq) { uint32_t m = UINT32_MAX; for (size_t i = 0; i < cd; i++) m = std::min(m, cms[i][mix(kv.first ^ (i * 0x9e3779b97f4a7c15ULL + 1)) % cw]); assert(m >= kv.second); if (m > kv.second + eps * EVENTS) over++; }
    assert(over <= exactFreq.size() * 0.02);
    size_t exactBytes = exactSet.size() * 8, exactFreqBytes = exactFreq.size() * 12;                // 키 8 B + 횟수 4 B 의 순수 페이로드만 센 하한 (실제 해시 표는 훨씬 큼)
    size_t hllBytes = hll.size(), bloomBytes = bloom.size() * 8, cmsBytes = cd * cw * 4;
    assert(exactBytes > hllBytes * 50 && exactBytes > bloomBytes * 1.5 && exactFreqBytes > cmsBytes * 4);
    std::cout << exactSet.size() << " distinct keys / " << EVENTS << " events\n  distinct count: exact >=" << exactBytes << " B vs HyperLogLog " << hllBytes << " B (error " << hllErr * 100 << "%)\n  membership: exact >=" << exactBytes
              << " B vs Bloom " << bloomBytes << " B (false positives " << fpr * 100 << "%)\n  frequency: exact >=" << exactFreqBytes << " B vs Count-Min " << cmsBytes << " B (keys off by more than eps*N: " << over << "/" << exactFreq.size() << ")" << std::endl; return 0;
}
// Time Complexity: 근사 구조 연산은 모두 O(1)~O(d)
// Space Complexity: 근사 구조는 원소 수와 무관한 고정 크기(ε, δ, p 로 결정), 정확 구조는 O(N)
```
## CPU 자료구조 vs GPU 자료구조
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// CPU 는 복잡한 제어 흐름과 불규칙한 메모리 접근(포인터 따라가기)을 캐시와 분기 예측으로 견디도록 만들어졌고, GPU 는 수천 스레드가 "같은 명령을 같은 모양의 데이터에" 적용할 때 빛난다. 그래서 자료구조 선택 기준이 달라진다:
// ① 메모리 배치: GPU 의 워프(32 스레드)가 연속 주소를 읽어야 한 번의 128 B 트랜잭션으로 합쳐진다 -> 구조체의 배열(AoS) 대신 필드별 배열(SoA) ② 분기: 워프 안의 스레드가 서로 다른 분기를 타면 양쪽을 모두 순서대로 실행(divergence)하므로
// 입력을 조건별로 미리 분류(분할)한다 ③ 포인터 추적(연결 리스트·고전 트리)은 스레드마다 주소가 흩어져 합쳐지지 않으므로 배열 기반(CSR, 암묵적 힙, 구조 평탄화) 구조를 쓴다.  숫자로 확인한다
long segments(const std::vector<long>& addr) { std::set<long> s; for (long a : addr) s.insert(a / 128); return s.size(); }
int main() {
    const int N = 1 << 16; std::mt19937 g(1);
    long aos = 0, soa = 0, chase = 0;                                      // 입자 N 개의 x 좌표 하나를 읽는 워프 로드
    for (int w = 0; w < N / 32; w++) {
        std::vector<long> a1, a2, a3; for (int l = 0; l < 32; l++) { long i = w * 32 + l; a1.push_back(i * 32); a2.push_back(i * 4); a3.push_back((long)(g() % N) * 32); }      // AoS: 구조체 32 B 중 x / SoA: float 배열 / 무작위 포인터
        aos += segments(a1); soa += segments(a2); chase += segments(a3);
    }
    assert(soa * 6 < aos && soa * 20 < chase);                             // SoA 는 워프당 1 트랜잭션, AoS 는 8, 무작위 접근은 32 에 가깝다
    long cost[2] = {0, 0}; const int T_COST = 10, F_COST = 10;             // 분기 양쪽 비용 각 10 사이클: 워프는 "참인 레인이 있으면 참쪽" + "거짓인 레인이 있으면 거짓쪽" 을 모두 실행
    std::vector<int> pred(N); for (auto& p : pred) p = g() % 2;
    auto warpCost = [&](const std::vector<int>& v) { long c = 0; for (int w = 0; w < N / 32; w++) { bool anyT = false, anyF = false; for (int l = 0; l < 32; l++) (v[w * 32 + l] ? anyT : anyF) = true; c += (anyT ? T_COST : 0) + (anyF ? F_COST : 0); } return c; };
    cost[0] = warpCost(pred); std::vector<int> sorted = pred; std::sort(sorted.begin(), sorted.end()); cost[1] = warpCost(sorted);        // 조건별로 모아 두면 워프 안이 모두 같은 분기
    assert(cost[1] * 19 < cost[0] * 10 + cost[0] / 100);                  // 분류 후 거의 절반
    std::cout << "warp loads of one field: AoS " << aos << " segments, SoA " << soa << ", random pointer chasing " << chase << " (of " << N / 32 << " warps)\nbranch divergence cost: random predicate " << cost[0] << " cycles vs partitioned input " << cost[1] << " cycles" << std::endl; return 0;
}
// Time Complexity: 이 시뮬레이션은 O(N)
// Space Complexity: O(N)
```
## LSM Tree가 SSD에 적합한 이유
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// SSD 의 NAND 플래시는 ① 페이지(4~16 KB) 단위로만 쓰고 ② 이미 쓴 페이지는 덮어쓸 수 없으며 ③ 지우기(erase)는 수십~수백 페이지의 블록 단위로만 한다. 그래서 제자리 덮어쓰기는 불가능하고 SSD 컨트롤러(FTL)가
// 새 페이지에 쓰고 옛 페이지는 "무효" 표시를 한 뒤, 여유가 모자라면 무효 페이지가 많은 블록을 골라 아직 유효한 페이지를 다른 곳에 복사하고(가비지 컬렉션, GC) 지운다. 이 복사 때문에 호스트가 쓴 양보다 NAND 에 실제로 쓰는 양이 많아진다(쓰기 증폭 WA = NAND 쓰기 / 호스트 쓰기).
// B-트리처럼 작은 페이지를 무작위로 제자리 갱신하면 무효 페이지가 블록 곳곳에 흩어져 GC 가 많이 복사해야 해서 WA 가 크고 수명이 짧아진다. LSM 은 큰 순차 파일을 쓰고 한 번에 통째로 지우므로(한 파일의 페이지가 같은 블록에 모여 같이 무효화) GC 가 거의 복사할 게 없다.
// 아래는 간단한 FTL(탐욕 GC) 시뮬레이터로 두 쓰기 패턴의 WA 를 잰다. LSM 자체의 쓰기 증폭(압축)은 별개(LSMTree 항목)이지만 장치 수준에서는 이점이 있다
struct FTL {
    static const int P = 64, NB = 256; std::vector<int> l2p, p2l = std::vector<int>(NB * P, -1), valid = std::vector<int>(NB, 0); std::vector<char> state = std::vector<char>(NB, 0);
    int active = -1, fill = 0, freeBlocks = NB; long host = 0, nand = 0, erases = 0; bool inGC = false;
    explicit FTL(int logical) : l2p(logical, -1) {}
    void program(int lpn) {
        for (;;) {                                                         // GC 가 활성 블록을 열거나 채웠을 수 있으므로 다시 판정한다
            if (active >= 0 && fill == P) { state[active] = 2; active = -1; }                          // 활성 블록이 다 찼다
            if (active >= 0) break;
            if (!inGC && freeBlocks <= 3) { gc(); continue; }               // 여유 블록이 모자라면 먼저 GC
            int b = 0; while (state[b] != 0) b++; state[b] = 1; active = b; fill = 0; freeBlocks--; break;
        }
        int ppn = active * P + fill++; p2l[ppn] = lpn; l2p[lpn] = ppn; valid[active]++; nand++;
    }
    void write(int lpn) { host++; int old = l2p[lpn]; if (old >= 0) { valid[old / P]--; p2l[old] = -1; } program(lpn); }
    void gc() {
        inGC = true;
        while (freeBlocks <= 3) {
            int v = -1; for (int b = 0; b < NB; b++) if (state[b] == 2 && (v < 0 || valid[b] < valid[v])) v = b;           // 유효 페이지가 가장 적은 블록 (탐욕)
            for (int i = 0; i < P; i++) { int lpn = p2l[v * P + i]; if (lpn >= 0) { valid[v]--; p2l[v * P + i] = -1; program(lpn); } }       // 아직 유효한 페이지를 옮겨 쓴다 (쓰기 증폭의 원인)
            state[v] = 0; valid[v] = 0; freeBlocks++; erases++;
        }
        inGC = false;
    }
    double wa() const { return (double)nand / host; }
};
int main() {
    const int logical = (int)(FTL::NB * FTL::P * 0.80); std::mt19937 g(1);
    FTL rnd(logical); for (int i = 0; i < logical; i++) rnd.write(i); rnd.host = rnd.nand = 0;
    for (int i = 0; i < 400000; i++) rnd.write(g() % logical);              // B-트리식: 작은 페이지의 무작위 제자리 갱신
    FTL seq(logical); for (int i = 0; i < logical; i++) seq.write(i); seq.host = seq.nand = 0;
    for (int r = 0; r < 25; r++) for (int i = 0; i < logical; i++) seq.write(i);                         // LSM 식: 큰 순차 쓰기, 옛 파일은 통째로 무효
    assert(rnd.wa() > 2.0 && seq.wa() < 1.1 && rnd.wa() > seq.wa() * 2);
    std::cout << "FTL write amplification at 80% utilization: random in-place updates " << rnd.wa() << " (" << rnd.erases << " erases) vs sequential log-structured writes " << seq.wa() << " (" << seq.erases << " erases)" << std::endl; return 0;
}
// Time Complexity: 시뮬레이션 O(쓰기 수 × 블록 수)
// Space Complexity: O(물리 페이지 수)
```
## 벡터 데이터베이스는 왜 HNSW를 사용하는가?
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

// 벡터 검색은 "질의와 가까운 k 개" 를 찾는 일이다. 구조 없는 고차원 데이터에서는 공간 분할 트리(KD, Ball)가 거의 모든 가지를 방문해 전수 탐색과 다를 바 없어진다 — 아래에서 16 차원 가우시안 데이터로 직접 재면 KD 트리가 N 의 99% 이상을 본다.
// (군집이 뚜렷한 데이터에서는 KD 트리도 훨씬 적게 본다: 같은 군집 데이터에서는 N 의 9~22%.  그러니 근거는 "구조가 없으면 트리는 소용없다" 이지 "트리는 항상 나쁘다" 가 아니다.)  남는 선택이 IVF(군집 -> 일부 군집만 탐색)와 근접 그래프(HNSW 계열)이다.
// IVF 는 군집 수를 √N 으로 두면 탐색량이 ~√N 으로 늘어난다 (여기서 N 이 8 배일 때 약 3.8 배).  근접 그래프는 "이웃의 이웃이 더 가깝다" 는 성질로 질의 쪽으로 걸어가기 때문에 같은 recall 에서 거리 계산이 N 보다 훨씬 느리게 늘어난다
// (여기서 N 이 8 배일 때 약 2.5 배 — N 에 "무관" 한 것은 아니고, 작은 N 에서는 IVF 와 비슷하다: N=1000 에서 103 대 100.  격차는 N 이 클수록 벌어진다).  실제 HNSW 는 새 벡터를 재학습 없이 이웃 몇 개와 연결만 하면 되고(군집 중심을 다시 학습할 필요가 없다) 압축 없이도 정확한 거리를 쓴다. 대가는 메모리(벡터 + 간선)와 삭제의 어려움이다.
// 아래는 같은 데이터에서 N 을 키우며 "recall@10 >= 0.9 를 처음 달성하는 설정" (후보 격자에서 가장 싼 설정) 의 평균 거리 계산 수를 전수 탐색·IVF(k-means 6 회)·근접 그래프(계층 없는 단순판)로 비교한다 (HNSW 본체와 삽입으로 그래프를 만드는 방법은 이 책 Part 12 HNSW 항목)
// 단순화(주의): 여기서 그래프는 삽입으로 만든 것이 아니라 O(N²) 전수 계산으로 만든 정확한 kNN 그래프(이웃 10 개 + 무작위 간선 2 개)이고 그 빌드 비용은 거리 계산 수에 넣지 않았다. 그래서 "재학습 없는 삽입" 같은 구성 쪽 장점은 이 항목이 아니라 HNSW 항목이 보인다.
// 검증: 모든 N 에서 그래프가 N 의 25% 미만만 보고, N 이 8 배가 될 때 그래프의 증가 배율이 IVF 의 0.8 배 미만이며 N=8000 에서 IVF 보다 적고, KD 트리는 정확(전수 탐색과 같은 집합)한 답을 내며 가우시안 데이터에서는 N 의 90% 이상을 보고, IVF 의 k-means 가 군집 내 제곱 거리 합을 실제로 줄인다
const int D = 16; typedef std::array<float, D> V;
float dist(const V& a, const V& b) { float s = 0; for (int i = 0; i < D; i++) s += (a[i] - b[i]) * (a[i] - b[i]); return s; }
struct Graph {
    const std::vector<V>* P; std::vector<std::vector<int>> nb; long evals = 0; std::mt19937 g{3};
    void build(const std::vector<V>& pts, int M) { P = &pts; int n = pts.size(); nb.assign(n, {}); std::vector<std::pair<float, int>> d(n);
        for (int i = 0; i < n; i++) { for (int j = 0; j < n; j++) d[j] = {dist(pts[i], pts[j]), j}; std::partial_sort(d.begin(), d.begin() + M + 1, d.end()); for (int k = 1; k <= M; k++) nb[i].push_back(d[k].second); nb[i].push_back(g() % n); nb[i].push_back(g() % n); } }
    std::vector<int> search(const V& q, int k, int ef) {
        int n = P->size(); std::vector<char> seen(n, 0); using PI = std::pair<float, int>; std::priority_queue<PI, std::vector<PI>, std::greater<PI>> cand; std::priority_queue<PI> res;
        for (int s = 0; s < 16; s++) { int id = g() % n; if (seen[id]) continue; seen[id] = 1; float d = dist(q, (*P)[id]); evals++; cand.push({d, id}); res.push({d, id}); if ((int)res.size() > ef) res.pop(); }       // 시작점 16 개
        while (!cand.empty()) { PI c = cand.top(); if ((int)res.size() >= ef && c.first > res.top().first) break; cand.pop();
            for (int e : nb[c.second]) { if (seen[e]) continue; seen[e] = 1; float d = dist(q, (*P)[e]); evals++; if ((int)res.size() < ef || d < res.top().first) { cand.push({d, e}); res.push({d, e}); if ((int)res.size() > ef) res.pop(); } } }
        std::vector<PI> v; while (!res.empty()) { v.push_back(res.top()); res.pop(); } std::reverse(v.begin(), v.end()); std::vector<int> out; for (int i = 0; i < k && i < (int)v.size(); i++) out.push_back(v[i].second); return out;
    }
};
struct KD {                                                                // 정확한 k-NN 용 KD 트리: 가장 퍼진 축에서 중앙값으로 분할, 분할 평면까지의 거리로 가지치기
    const std::vector<V>* P; std::vector<int> idx; std::vector<char> ax; long evals = 0; std::vector<std::pair<float, int>> heap;
    void build(const std::vector<V>& pts) { P = &pts; idx.resize(pts.size()); ax.assign(pts.size(), 0); for (size_t i = 0; i < idx.size(); i++) idx[i] = (int)i; rec(0, (int)idx.size()); }
    void rec(int lo, int hi) { if (hi - lo <= 1) return; int best = 0; float bw = -1; for (int a = 0; a < D; a++) { float mn = 1e30f, mx = -1e30f; for (int i = lo; i < hi; i++) { mn = std::min(mn, (*P)[idx[i]][a]); mx = std::max(mx, (*P)[idx[i]][a]); } if (mx - mn > bw) { bw = mx - mn; best = a; } }
        int mid = (lo + hi) / 2; std::nth_element(idx.begin() + lo, idx.begin() + mid, idx.begin() + hi, [&](int x, int y) { return (*P)[x][best] < (*P)[y][best]; }); ax[mid] = (char)best; rec(lo, mid); rec(mid + 1, hi); }
    void knn(const V& q, int lo, int hi, int k) { if (lo >= hi) return; int mid = (lo + hi) / 2, id = idx[mid]; float d = dist(q, (*P)[id]); evals++; heap.push_back({d, id}); std::push_heap(heap.begin(), heap.end()); if ((int)heap.size() > k) { std::pop_heap(heap.begin(), heap.end()); heap.pop_back(); }
        if (hi - lo == 1) return; float diff = q[(int)ax[mid]] - (*P)[id][(int)ax[mid]]; bool left = diff < 0; if (left) knn(q, lo, mid, k); else knn(q, mid + 1, hi, k);
        if ((int)heap.size() < k || diff * diff < heap.front().first) { if (left) knn(q, mid + 1, hi, k); else knn(q, lo, mid, k); } }
    std::vector<int> search(const V& q, int k) { heap.clear(); knn(q, 0, (int)idx.size(), k); std::vector<int> out; for (auto& h : heap) out.push_back(h.second); return out; }
};
struct IVF {
    const std::vector<V>* P; std::vector<V> cents; std::vector<std::vector<int>> lists; long evals = 0; double sse0 = 0, sse1 = 0;
    void build(const std::vector<V>& pts, int nlist, std::mt19937& g) { P = &pts; for (int c = 0; c < nlist; c++) cents.push_back(pts[g() % pts.size()]); lists.assign(nlist, {});
        assign(); sse0 = sse();           // 무작위 표본으로 시작해 k-means 6 회 (평균으로 중심 갱신 -> 재배정)
        for (int it = 0; it < 6; it++) { std::vector<V> sum(nlist); for (auto& v : sum) v.fill(0); for (int c = 0; c < nlist; c++) { for (int id : lists[c]) for (int j = 0; j < D; j++) sum[c][j] += pts[id][j]; if (!lists[c].empty()) for (int j = 0; j < D; j++) cents[c][j] = sum[c][j] / lists[c].size(); } assign(); } sse1 = sse(); }
    double sse() const { double s = 0; for (size_t c = 0; c < lists.size(); c++) for (int id : lists[c]) s += dist((*P)[id], cents[c]); return s; }      // 군집 내 제곱 거리 합 (k-means 목적함수)
    void assign() { for (auto& l : lists) l.clear(); for (size_t i = 0; i < P->size(); i++) { int b = 0; float bd = 1e30f; for (int c = 0; c < (int)cents.size(); c++) { float d = dist((*P)[i], cents[c]); if (d < bd) { bd = d; b = c; } } lists[b].push_back((int)i); } }
    std::vector<int> search(const V& q, int k, int nprobe) {
        std::vector<std::pair<float, int>> cd; for (size_t c = 0; c < cents.size(); c++) cd.push_back({dist(q, cents[c]), (int)c}); evals += cents.size(); std::partial_sort(cd.begin(), cd.begin() + nprobe, cd.end());
        std::vector<std::pair<float, int>> cand; for (int p = 0; p < nprobe; p++) for (int id : lists[cd[p].second]) { cand.push_back({dist(q, (*P)[id]), id}); evals++; }
        int kk = std::min<int>(k, cand.size()); std::partial_sort(cand.begin(), cand.begin() + kk, cand.end()); std::vector<int> out; for (int i = 0; i < kk; i++) out.push_back(cand[i].second); return out;
    }
};
int main() {
    std::mt19937 g(5); std::normal_distribution<float> N(0, 1); const int Q = 60, K = 10; double gEv[4], iEv[4], kdC[4], kdU[4]; int sizes[4] = {1000, 2000, 4000, 8000};
    for (int s = 0; s < 4; s++) {
        int n = sizes[s]; std::vector<V> centers(20); for (auto& c : centers) for (auto& x : c) x = N(g) * 4; auto sample = [&]() { V p = centers[g() % 20]; for (auto& x : p) x += N(g); return p; };
        std::vector<V> pts; for (int i = 0; i < n; i++) pts.push_back(sample()); std::vector<V> qs; std::vector<std::vector<int>> exact;
        for (int t = 0; t < Q; t++) { qs.push_back(sample()); std::vector<std::pair<float, int>> d; for (int i = 0; i < n; i++) d.push_back({dist(qs.back(), pts[i]), i}); std::partial_sort(d.begin(), d.begin() + K, d.end()); std::vector<int> e; for (int i = 0; i < K; i++) e.push_back(d[i].second); exact.push_back(e); }
        auto recall = [&](std::vector<std::vector<int>>& got) { double r = 0; for (int t = 0; t < Q; t++) { int hit = 0; for (int a : got[t]) hit += std::find(exact[t].begin(), exact[t].end(), a) != exact[t].end(); r += (double)hit / K; } return r / Q; };
        Graph gr; gr.build(pts, 10); gEv[s] = 1e18; for (int ef : {16, 24, 32, 48, 64, 96, 128, 192, 256}) { gr.evals = 0; std::vector<std::vector<int>> got; for (auto& q : qs) got.push_back(gr.search(q, K, ef)); if (recall(got) >= 0.9) { gEv[s] = (double)gr.evals / Q; break; } }
        { KD kd; kd.build(pts); std::vector<std::vector<int>> got; for (auto& q : qs) got.push_back(kd.search(q, K)); assert(recall(got) == 1.0); kdC[s] = (double)kd.evals / Q; }                       // 군집 데이터에서의 정확한 KD 트리 (재현율 1)
        { std::mt19937 gu(77 + s); std::normal_distribution<float> NU(0, 1); std::vector<V> up(n); for (auto& p : up) for (auto& x : p) x = NU(gu); KD kd; kd.build(up); long ev = 0;       // 구조 없는 16 차원 가우시안 데이터
          for (int t = 0; t < Q; t++) { V q; for (auto& x : q) x = NU(gu); kd.evals = 0; auto r = kd.search(q, K); ev += kd.evals; std::vector<std::pair<float, int>> d; for (int i = 0; i < n; i++) d.push_back({dist(q, up[i]), i}); std::partial_sort(d.begin(), d.begin() + K, d.end());
            std::vector<int> e; for (int i = 0; i < K; i++) e.push_back(d[i].second); std::sort(e.begin(), e.end()); std::sort(r.begin(), r.end()); assert(e == r); } kdU[s] = (double)ev / Q; assert(kdU[s] >= 0.9 * n); }    // 거의 전수 탐색
        int nlist = (int)std::sqrt((double)n); IVF iv; iv.build(pts, nlist, g); assert(iv.sse1 < iv.sse0); iEv[s] = n; for (int np = 1; np <= nlist; np = np < 4 ? np + 1 : np * 3 / 2) { iv.evals = 0; std::vector<std::vector<int>> got; for (auto& q : qs) got.push_back(iv.search(q, K, np)); if (recall(got) >= 0.9) { iEv[s] = (double)iv.evals / Q; break; } }
        std::cout << "N=" << n << ": distance evaluations for recall@10>=0.9  flat " << n << " | IVF " << iEv[s] << " | proximity graph " << gEv[s] << "  (exact KD-tree: " << kdC[s] << " on this clustered data, " << kdU[s] << " = " << 100 * kdU[s] / n << "% of N on structureless Gaussian data)" << std::endl;
    }
    for (int s = 0; s < 4; s++) assert(gEv[s] < 0.25 * sizes[s]);                                                                  // 그래프는 모든 N 에서 전수 탐색의 1/4 미만
    assert(gEv[3] / gEv[0] < (double)sizes[3] / sizes[0] / 2 && gEv[3] / gEv[0] < 0.8 * (iEv[3] / iEv[0]) && gEv[3] < iEv[3]);      // N 이 8 배가 되어도 그래프의 계산량은 4 배 미만이고, IVF 보다 덜 늘며, 큰 N 에서는 IVF 보다 적다
    std::cout << "growth for N x" << sizes[3] / sizes[0] << ": proximity graph x" << gEv[3] / gEv[0] << " (exponent " << std::log(gEv[3] / gEv[0]) / std::log((double)sizes[3] / sizes[0]) << "), IVF x" << iEv[3] / iEv[0] << " (exponent " << std::log(iEv[3] / iEv[0]) / std::log((double)sizes[3] / sizes[0]) << "), flat x" << sizes[3] / sizes[0] << std::endl;
    return 0;
}
// Time Complexity: 그래프 질의는 경험적으로 부선형 (이 데모에서 N 이 8 배일 때 약 2.5 배; 저차원 가정 하에서 O(log N) 으로 보고됨, 보장 아님), IVF 는 이상적으로 O(√N)(여기서 약 3.8 배), 플랫·구조 없는 고차원의 KD 트리는 O(N) (그래프 구성은 이 데모에서 전수 kNN 이라 O(N² D))
// Space Complexity: 그래프 O(N·(D + M)), IVF·KD 트리 O(N·D)
```
## 현대 데이터베이스가 B+Tree와 LSMTree를 함께 사용하는 이유
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <unordered_map>
#include <vector>

// B+트리는 읽기에 최적화되어 있다: 점 조회는 잎 페이지 하나(상위는 캐시), 범위 조회는 연결된 잎을 순차로. 그러나 쓰기는 "페이지를 읽고 → 수정하고 → 같은 자리에 쓰는" 무작위 I/O 이고 분할이 겹치면 더 든다.
//  LSM 은 쓰기에 최적화되어 있다: 쓰기는 메모리에서 합쳐져 큰 순차 쓰기로 나가지만 읽기는 여러 레벨·파일을 확인해야 한다(블룸 필터로 줄여도 완전히 1 은 아니다) + 병합(compaction)의 쓰기 증폭.
//  그래서 현대 DB 는 한쪽만 고집하지 않고 워크로드·계층에 맞게 섞는다: 읽기 중심 OLTP 의 기본 저장소는 B+트리(InnoDB, PostgreSQL), 쓰기·로그·시계열은 LSM(RocksDB, Cassandra), 같은 서버 안에서 두 엔진을 고르게 하는 MySQL(InnoDB / MyRocks)과 MongoDB(WiredTiger 의 B-트리 / LSM 옵션),
//  LSM 위에 B-트리식 범위 분할과 SQL 층을 올린 분산 DB(TiDB, CockroachDB), 그리고 두 구조의 중간인 B^ε 트리(프랙탈 트리).  어느 쪽이 이기는지는 "쓰기 비율" 이 정한다.
//  여기서는 *두 구조를 실제로 돌려* I/O 를 센다: B+트리는 노드 접근을 LRU 버퍼 풀(2000 쪽)에 흘려 읽기 미스(무작위 읽기)와 더러운 쪽 축출(무작위 쓰기)을 세고, LSM 은 크기 단계형 병합(T = 4)에서 기록한 항목 수(순차 쓰기)와 블룸 필터를 통과한 런 조회 수(무작위 읽기)를 센다.
//  비용 모델: 무작위 I/O 한 번 = 1, 순차 쓰기 한 쪽 = 0.1.  ① 두 구조가 std::map 과 같은 값을 돌려준다(삽입 후 조회 전수)  ② LSM 쓰기 증폭이 이론 log_T(N/F) 근처  ③ 쓰기 100% 에서는 LSM 이, 읽기 100% 에서는 B+트리가 이긴다 — 교차점이 쓰기 비율 5%~95% 사이에 있다.
struct PageCache {
    size_t cap; std::list<std::pair<int, bool>> lru; std::unordered_map<int, std::list<std::pair<int, bool>>::iterator> where; long reads = 0, writes = 0;
    explicit PageCache(size_t c) : cap(c) {}
    void access(int page, bool dirty, bool fresh) {
        auto it = where.find(page); bool wasDirty = false;
        if (it != where.end()) { wasDirty = it->second->second; lru.erase(it->second); } else { if (!fresh) ++reads; if (lru.size() >= cap) { auto victim = lru.back(); if (victim.second) ++writes; where.erase(victim.first); lru.pop_back(); } }
        lru.push_front({page, wasDirty || dirty}); where[page] = lru.begin(); }
    void flush() { for (auto& p : lru) if (p.second) ++writes; lru.clear(); where.clear(); }
};
struct BPlus {
    struct Node { bool leaf = true; std::vector<long> keys; std::vector<long> vals; std::vector<int> kids; };
    int M; std::vector<Node> pool; int root; PageCache* cache;
    BPlus(int maxKeys, PageCache* pc) : M(maxKeys), cache(pc) { pool.push_back(Node()); root = 0; }
    int childIndex(int x, long k) const { return (int)(std::upper_bound(pool[x].keys.begin(), pool[x].keys.end(), k) - pool[x].keys.begin()); }
    bool find(long k, long& v) { int x = root; for (;;) { cache->access(x, false, false); if (pool[x].leaf) { auto it = std::lower_bound(pool[x].keys.begin(), pool[x].keys.end(), k); if (it == pool[x].keys.end() || *it != k) return false; v = pool[x].vals[it - pool[x].keys.begin()]; return true; } x = pool[x].kids[childIndex(x, k)]; } }
    bool ins(int x, long k, long v, long& up, int& right) {
        cache->access(x, false, false);
        if (pool[x].leaf) { auto it = std::lower_bound(pool[x].keys.begin(), pool[x].keys.end(), k); size_t pos = it - pool[x].keys.begin(); if (it != pool[x].keys.end() && *it == k) { pool[x].vals[pos] = v; cache->access(x, true, false); return false; }
            pool[x].keys.insert(it, k); pool[x].vals.insert(pool[x].vals.begin() + pos, v); cache->access(x, true, false); if ((int)pool[x].keys.size() <= M) return false;
            int mid = (M + 1) / 2, r = (int)pool.size(); pool.push_back(Node()); pool[r].keys.assign(pool[x].keys.begin() + mid, pool[x].keys.end()); pool[r].vals.assign(pool[x].vals.begin() + mid, pool[x].vals.end()); pool[x].keys.resize(mid); pool[x].vals.resize(mid); cache->access(r, true, true); up = pool[r].keys[0]; right = r; return true; }
        int i = childIndex(x, k); long u; int r; if (!ins(pool[x].kids[i], k, v, u, r)) return false; pool[x].keys.insert(pool[x].keys.begin() + i, u); pool[x].kids.insert(pool[x].kids.begin() + i + 1, r); cache->access(x, true, false); if ((int)pool[x].keys.size() <= M) return false;
        int mid = (M + 1) / 2, nr = (int)pool.size(); pool.push_back(Node()); pool[nr].leaf = false; up = pool[x].keys[mid]; pool[nr].keys.assign(pool[x].keys.begin() + mid + 1, pool[x].keys.end()); pool[nr].kids.assign(pool[x].kids.begin() + mid + 1, pool[x].kids.end()); pool[x].keys.resize(mid); pool[x].kids.resize(mid + 1); cache->access(nr, true, true); right = nr; return true; }
    void put(long k, long v) { long up; int r; if (ins(root, k, v, up, r)) { int nr = (int)pool.size(); pool.push_back(Node()); pool[nr].leaf = false; pool[nr].keys = {up}; pool[nr].kids = {root, r}; root = nr; cache->access(nr, true, true); } }
};
struct Lsm {
    struct Run { std::vector<std::pair<long, long>> kv; std::vector<uint64_t> bloom; };
    size_t F, T; std::map<long, long> mem; std::vector<std::vector<Run>> levels; long entriesWritten = 0, userWrites = 0, probes = 0;
    Lsm(size_t flushSize, size_t fanout) : F(flushSize), T(fanout) {}
    static uint64_t h(long k, int i) { uint64_t x = (uint64_t)k * 0x9E3779B97F4A7C15ULL + (uint64_t)i * 0xD6E8FEB86659FD93ULL; x ^= x >> 31; x *= 0xBF58476D1CE4E5B9ULL; x ^= x >> 29; return x; }
    static Run makeRun(const std::map<long, long>& m) { Run r; r.kv.assign(m.begin(), m.end()); r.bloom.assign((r.kv.size() * 10 + 63) / 64 + 1, 0); size_t bits = r.bloom.size() * 64; for (auto& p : r.kv) for (int i = 0; i < 7; ++i) { size_t b = h(p.first, i) % bits; r.bloom[b >> 6] |= 1ULL << (b & 63); } return r; }
    static bool maybe(const Run& r, long k) { size_t bits = r.bloom.size() * 64; for (int i = 0; i < 7; ++i) { size_t b = h(k, i) % bits; if (!(r.bloom[b >> 6] >> (b & 63) & 1)) return false; } return true; }
    void put(long k, long v) { mem[k] = v; ++userWrites; if (mem.size() >= F) flush(); }
    void flush() { if (mem.empty()) return; if (levels.empty()) levels.resize(1); levels[0].push_back(makeRun(mem)); entriesWritten += (long)mem.size(); mem.clear();
        for (size_t l = 0; l < levels.size() && levels[l].size() >= T; ++l) { std::map<long, long> merged; for (auto& run : levels[l]) for (auto& p : run.kv) merged[p.first] = p.second; levels[l].clear(); if (l + 1 >= levels.size()) levels.resize(l + 2); levels[l + 1].push_back(makeRun(merged)); entriesWritten += (long)merged.size(); } }   // 오래된 런부터 덮어써 최신 값이 남는다
    bool get(long k, long& v) { auto it = mem.find(k); if (it != mem.end()) { v = it->second; return true; }
        for (size_t l = 0; l < levels.size(); ++l) for (size_t i = levels[l].size(); i-- > 0;) { const Run& r = levels[l][i]; if (!maybe(r, k)) continue; ++probes; auto p = std::lower_bound(r.kv.begin(), r.kv.end(), std::make_pair(k, (long)-(1L << 60))); if (p != r.kv.end() && p->first == k) { v = p->second; return true; } }
        return false; }
};

int main() {
    const int N0 = 200000, OPS = 100000; const double E = 64, RAND = 1.0, SEQ = 0.1; std::mt19937_64 rng(227);
    std::vector<long> base; std::map<long, long> truth; while ((int)base.size() < N0) { long k = (long)(rng() % 2000000000); if (truth.emplace(k, k * 3 + 1).second) base.push_back(k); }
    PageCache bc0(2000); BPlus preBt(63, &bc0); Lsm preLsm(4096, 4); for (long k : base) { preBt.put(k, k * 3 + 1); preLsm.put(k, k * 3 + 1); }                                // 초기 적재 N0 개
    for (int i = 0; i < 20000; ++i) { long k = base[rng() % base.size()], v; bool a = preBt.find(k, v); assert(a && v == truth[k]); bool b = preLsm.get(k, v); assert(b && v == truth[k]); }          // ① 같은 값
    for (int i = 0; i < 5000; ++i) { long k = (long)(rng() % 2000000000); long v; assert(preBt.find(k, v) == (truth.count(k) > 0)); assert(preLsm.get(k, v) == (truth.count(k) > 0)); }
    double wa = (double)preLsm.entriesWritten / (double)preLsm.userWrites, theory = std::log((double)N0 / 4096) / std::log(4.0) + 1; assert(wa > 0.5 * theory && wa < 1.5 * theory);                                    // ② 쓰기 증폭 ≈ log_T(N/F) + 1
    double crossing = -1, costBt[6], costLsm[6]; const double fracs[6] = {0.0, 0.05, 0.2, 0.5, 0.8, 1.0};
    for (int fi = 0; fi < 6; ++fi) { double f = fracs[fi];
        PageCache pc(2000); BPlus bt(63, &pc); Lsm lsm(4096, 4); for (long k : base) { bt.put(k, k * 3 + 1); lsm.put(k, k * 3 + 1); } pc.reads = pc.writes = 0; lsm.entriesWritten = 0; lsm.probes = 0;     // 적재 비용은 빼고 측정 구간만
        std::vector<long> keys = base; for (int i = 0; i < OPS; ++i) { if ((double)(rng() % 1000000) / 1e6 < f) { long k = (long)(rng() % 2000000000); bt.put(k, k * 3 + 1); lsm.put(k, k * 3 + 1); keys.push_back(k); } else { long k = keys[rng() % keys.size()], v; bool a = bt.find(k, v); (void)a; bool b = lsm.get(k, v); (void)b; } }
        pc.flush(); costBt[fi] = (double)(pc.reads + pc.writes) * RAND / OPS; costLsm[fi] = ((double)lsm.entriesWritten / E * SEQ + (double)lsm.probes * RAND) / OPS; }
    assert(costBt[0] < costLsm[0] && costLsm[5] < costBt[5]);                                                    // ③ 읽기 100% → B+트리, 쓰기 100% → LSM
    for (int fi = 1; fi < 6 && crossing < 0; ++fi) if (costLsm[fi] < costBt[fi]) crossing = fracs[fi]; assert(crossing > 0.0 && crossing <= 0.95);
    std::cout << "B+Tree vs LSM (I/O units per operation, random I/O = 1, sequential page = 0.1):" << std::endl; for (int fi = 0; fi < 6; ++fi) std::cout << "  writes " << fracs[fi] * 100 << "%: B+tree " << costBt[fi] << ", LSM " << costLsm[fi] << std::endl;
    std::cout << "measured LSM write amplification " << wa << " (theory ~" << theory << "); LSM becomes cheaper once writes reach " << crossing * 100 << "% of operations" << std::endl;
    return 0;
}
// Time Complexity: 시뮬레이션 O(연산 수 · log N)
// Space Complexity: O(N)
```
## 생성형 AI 시대의 자료구조
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 대형 언어 모델 서비스에서 자료구조는 곳곳에 있다. ① 토크나이저: 병합 규칙 우선순위 큐(BPE), 트라이/더블 배열 사전(String.md Part 17) ② 임베딩 검색(RAG): HNSW·IVF-PQ 같은 벡터 색인(Part 12) ③ 어텐션의 KV 캐시: 생성할 때마다 모든 층에서
// 지금까지의 모든 토큰의 키·값 벡터를 저장한다 — 7B 모델 기준 토큰당 약 0.5 MB 라 메모리가 처리량을 정한다 ④ 요청 스케줄링: 우선순위 큐·배칭.  KV 캐시를 요청마다 "최대 길이만큼 연속으로 예약" 하면 실제 생성은 대부분 그보다 짧아 내부 단편화로 메모리 대부분이 낭비된다.
// vLLM 의 PagedAttention 은 OS 의 가상 메모리 페이징을 그대로 가져와 KV 캐시를 고정 크기 블록(예: 16 토큰)으로 나누고, 요청마다 "블록 테이블"(= 페이지 테이블)이 논리 토큰 위치를 물리 블록에 대응시키게 한다 — 필요할 때 블록을 한 장씩 할당하므로 낭비가 마지막 블록의 빈 칸뿐이고,
// 같은 시스템 프롬프트를 쓰는 요청들은 접두 블록을 참조 횟수로 공유한다(copy-on-write).  아래는 두 할당 방식의 낭비와 동시 처리 가능한 요청 수를 비교한다
int main() {
    std::mt19937 g(4); const int R = 400, MAXLEN = 2048, BLOCK = 16, POOL = 60000; const long layers = 32, heads = 32, dim = 128, bytes = 2; long kvPerToken = 2 * layers * heads * dim * bytes;
    struct Req { int len; }; std::vector<Req> reqs(R); for (auto& r : reqs) r.len = 20 + g() % 200 + 1 + g() % 500;           // 프롬프트 + 생성 길이 (대부분 MAXLEN 보다 훨씬 짧다)
    for (auto& r : reqs) r.len = std::min(r.len, MAXLEN);
    long used = 0, reservedContig = 0, reservedPaged = 0; for (auto& r : reqs) { used += r.len; reservedContig += MAXLEN; reservedPaged += (r.len + BLOCK - 1) / BLOCK * BLOCK; }
    double wasteContig = 1.0 - (double)used / reservedContig, wastePaged = 1.0 - (double)used / reservedPaged;
    int admitContig = POOL / MAXLEN, admitPaged = 0; { long free = POOL; for (auto& r : reqs) { long need = (r.len + BLOCK - 1) / BLOCK * BLOCK; if (need > free) break; free -= need; admitPaged++; } }
    assert(wasteContig > 0.5 && wastePaged < 0.05 && admitPaged >= 2 * admitContig);
    // 블록 테이블 + 접두 공유: 시스템 프롬프트 128 토큰(8 블록)을 가진 요청 50 개
    const int SYS = 128, SHARED = 50; std::vector<int> refcount(POOL / BLOCK, 0); std::vector<std::vector<int>> table(SHARED); int nextFree = 0;
    std::vector<int> sysBlocks; for (int b = 0; b < SYS / BLOCK; b++) sysBlocks.push_back(nextFree++);
    for (int r = 0; r < SHARED; r++) { for (int b : sysBlocks) { table[r].push_back(b); refcount[b]++; } int own = (reqs[r].len + BLOCK - 1) / BLOCK; for (int b = 0; b < own; b++) { int blk = nextFree++; table[r].push_back(blk); refcount[blk] = 1; } }
    long withShare = nextFree, withoutShare = 0; for (int r = 0; r < SHARED; r++) withoutShare += SYS / BLOCK + (reqs[r].len + BLOCK - 1) / BLOCK;
    for (int b : sysBlocks) assert(refcount[b] == SHARED);                 // 접두 블록은 50 개 요청이 하나를 공유
    assert(withShare < withoutShare && withoutShare - withShare == (long)(SHARED - 1) * (SYS / BLOCK));
    std::cout << "KV cache per token (7B-class model, fp16): " << kvPerToken / 1024 << " KiB; reserved-max-length waste " << wasteContig * 100 << "% vs paged waste " << wastePaged * 100 << "%; requests admitted in a "
              << POOL << "-token pool: " << admitContig << " vs " << admitPaged << "; shared 128-token prefix saves " << withoutShare - withShare << " of " << withoutShare << " blocks" << std::endl; return 0;
}
// Time Complexity: 블록 할당·해제 O(1), 논리 위치 -> 물리 블록 변환 O(1) (블록 테이블 조회)
// Space Complexity: 요청당 O(길이/블록) 테이블 + 사용한 블록
```
