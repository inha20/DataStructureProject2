# Part 1. 트리의 기초
## CreateTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 트리를 만드는 세 가지 표현을 서로 변환하며 검증한다.
//  ① 부모 배열 parent[i] (루트는 −1): 가장 작고 질의가 쉽다.  ② 자식 목록(children[i]): 순회에 좋다.  ③ 왼쪽 자식–오른쪽 형제(LCRS): 차수와 무관하게 노드당 포인터 2 개 — 임의의 n 진 트리를 이진 트리로.
//  검증: 무작위 트리(균등·사슬 편향·별 편향·완전 이진)를 세 표현으로 만들어 서로 왕복 변환해도 같은 트리이고, 불변식(루트 1 개, 간선 n−1 개, 부모를 따라가면 루트에 도달 = 사이클 없음, 모든 노드가 루트에서 도달 가능)이 성립.
//  깊이 10^6 사슬·별도 반복문으로만 만든다(재귀 없음).
struct Tree {                                                                    // 노드는 배열 풀에 두고 인덱스로 잇는다 (소유권·해제 문제 없음)
    struct Node { int firstChild = -1, nextSibling = -1, parent = -1; };
    std::vector<Node> nd; std::vector<int> lastChild; int root = -1;
    int createRoot() { nd.emplace_back(); lastChild.push_back(-1); root = (int)nd.size() - 1; return root; }
    int addChild(int p) { nd.emplace_back(); lastChild.push_back(-1); int c = (int)nd.size() - 1; nd[c].parent = p; if (nd[p].firstChild < 0) nd[p].firstChild = c; else nd[lastChild[p]].nextSibling = c; lastChild[p] = c; return c; }       // 맨 뒤 자식으로 O(1)
    std::vector<int> parentArray() const { std::vector<int> p(nd.size()); for (size_t i = 0; i < nd.size(); ++i) p[i] = nd[i].parent; return p; }
    std::vector<std::vector<int>> childLists() const { std::vector<std::vector<int>> c(nd.size()); for (size_t i = 0; i < nd.size(); ++i) for (int k = nd[i].firstChild; k >= 0; k = nd[k].nextSibling) c[i].push_back(k); return c; }
    std::vector<int> preorder() const { std::vector<int> out, st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(u); std::vector<int> kids; for (int k = nd[u].firstChild; k >= 0; k = nd[k].nextSibling) kids.push_back(k); for (size_t i = kids.size(); i-- > 0;) st.push_back(kids[i]); } return out; }
    bool valid() const {                                                          // 루트 1 개, 부모 사슬이 루트에서 끝남, 간선 수 n−1, 형제 연결과 부모가 일치
        if (nd.empty()) return root < 0; int roots = 0; long edges = 0; for (size_t i = 0; i < nd.size(); ++i) { if (nd[i].parent < 0) ++roots; else ++edges; for (int k = nd[i].firstChild; k >= 0; k = nd[k].nextSibling) if (nd[k].parent != (int)i) return false; }
        if (roots != 1 || edges != (long)nd.size() - 1 || nd[root].parent >= 0) return false;
        std::vector<char> seen(nd.size(), 0); std::vector<int> st = {root}; size_t cnt = 0; while (!st.empty()) { int u = st.back(); st.pop_back(); if (seen[u]) return false; seen[u] = 1; ++cnt; for (int k = nd[u].firstChild; k >= 0; k = nd[k].nextSibling) st.push_back(k); }
        return cnt == nd.size();                                                  // 루트에서 모두 도달 + 한 번씩만 방문 = 연결이고 사이클 없음
    }
};
Tree fromParents(const std::vector<int>& parent) {                               // 부모 배열 → LCRS 트리 (자식은 번호 순)
    Tree t; size_t n = parent.size(); std::vector<std::vector<int>> kids(n); int root = -1; for (size_t i = 0; i < n; ++i) { if (parent[i] < 0) root = (int)i; else kids[parent[i]].push_back((int)i); }
    std::vector<int> id(n, -1); id[root] = t.createRoot(); std::vector<int> st = {root};                          // 원래 번호 → 새 번호
    while (!st.empty()) { int u = st.back(); st.pop_back(); for (int k : kids[u]) { id[k] = t.addChild(id[u]); st.push_back(k); } }
    return t;                                                                       // 새 번호는 BFS/DFS 생성 순서이므로 아래 비교는 구조(차수열)로 한다
}
std::vector<int> randomParents(int n, int shape, std::mt19937& rng) {              // parent[i] < i 인 무작위 트리를 만든 뒤 라벨을 섞는다
    std::vector<int> p(n, -1); for (int i = 1; i < n; ++i) p[i] = shape == 0 ? (int)(rng() % i) : shape == 1 ? std::max(0, i - 1 - (int)(rng() % 3)) : shape == 2 ? (int)(rng() % std::min(i, 3)) : (i - 1) / 2;       // 균등·사슬 편향·별 편향·완전 이진
    std::vector<int> perm(n); for (int i = 0; i < n; ++i) perm[i] = i; std::shuffle(perm.begin(), perm.end(), rng); std::vector<int> q(n, -1); for (int i = 0; i < n; ++i) q[perm[i]] = p[i] < 0 ? -1 : perm[p[i]]; return q;
}
std::vector<int> degreeSequence(const std::vector<int>& parent) { std::vector<int> d(parent.size(), 0); for (int p : parent) if (p >= 0) ++d[p]; std::sort(d.begin(), d.end()); return d; }

int main() {
    Tree small; int r = small.createRoot(); int a = small.addChild(r), b = small.addChild(r); small.addChild(a); (void)b; assert(small.valid() && small.nd.size() == 4 && small.nd[r].firstChild == a);
    std::mt19937 rng(10);
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 60), shape = (int)(rng() % 4); std::vector<int> parent = randomParents(n, shape, rng); Tree t = fromParents(parent); assert(t.valid() && (int)t.nd.size() == n);
        std::vector<int> back = t.parentArray(); int roots = (int)std::count(back.begin(), back.end(), -1); assert(roots == 1 && degreeSequence(back) == degreeSequence(parent));                // 같은 차수열
        std::vector<std::vector<int>> kids = t.childLists(); long edges = 0; for (auto& k : kids) edges += (long)k.size(); assert(edges == n - 1 && (int)t.preorder().size() == n);
        Tree again = fromParents(back); assert(again.valid() && degreeSequence(again.parentArray()) == degreeSequence(back) && again.preorder().size() == t.preorder().size());                    // 왕복
    }
    { int n = 1000000; Tree chain; int cur = chain.createRoot(); for (int i = 1; i < n; ++i) cur = chain.addChild(cur); assert(chain.valid() && (int)chain.preorder().size() == n);         // 깊이 10^6 사슬 (반복문)
      Tree star; int rt = star.createRoot(); for (int i = 1; i < n; ++i) star.addChild(rt); assert(star.valid() && star.preorder().size() == (size_t)n && star.nd[rt].firstChild == 1);
      std::cout << "CreateTree: parent array, child lists and left-child/right-sibling forms agreed on 3000 random trees; a depth-10^6 chain and a 10^6-child star were built iteratively" << std::endl; }
    return 0;
}
// Time Complexity: 노드 추가 O(1), 변환 O(n)
// Space Complexity: O(n) (노드당 포인터 2 개 + 부모)
```
## Root()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 루트: 부모가 없는 유일한 노드. 입력 형태에 따라 찾는 방법이 다르다 — 부모 배열에서는 −1 인 칸, 자식 목록에서는 어느 목록에도 안 나오는 노드, *뿌리 없는 트리*(간선 목록)에서는 직접 고른다.
//  ① 잘못된 입력 검출: 루트 0 개(사이클)·2 개 이상(숲)·고아·자기 부모를 가려내는 validate 를 무작위로 망가뜨린 부모 배열에서 브루트포스(DFS 도달성)와 대조.
//  ② 뿌리 없는 트리의 *중심*(리프를 한 겹씩 벗겨 마지막에 남는 1~2 개)은 이심률이 최소인 노드이고, 중심을 루트로 잡으면 높이가 최소(= 반지름).  브루트포스(모든 루트로 높이 계산)와 대조.
//  ③ 루트 바꾸기(reroot): 새 루트까지의 경로 위의 부모 관계를 뒤집으면 같은 간선 집합이 새 루트의 트리가 된다 — 깊이는 새 루트에서 BFS 한 값과 같다.
typedef std::vector<std::vector<int>> Adj;
int findRoot(const std::vector<int>& parent) { int root = -1; for (size_t i = 0; i < parent.size(); ++i) if (parent[i] < 0) { if (root >= 0) return -2; root = (int)i; } return root; }       // −1: 루트 없음, −2: 루트 여럿
bool validate(const std::vector<int>& parent) {                                  // 부모 배열이 정확히 하나의 트리인가
    int n = (int)parent.size(); if (findRoot(parent) < 0) return false; for (int p : parent) if (p >= n) return false;
    for (int i = 0; i < n; ++i) { int u = i, steps = 0; while (parent[u] >= 0 && steps <= n) { u = parent[u]; ++steps; } if (steps > n) return false; }       // 사슬이 끝나지 않으면 사이클
    return true;
}
bool bruteValid(const std::vector<int>& parent) {                                // 독립 판정: 간선을 방향 없는 그래프로 두고 루트에서 DFS — 모든 노드 도달 + 간선 n−1 개 + 자기 부모 없음
    int n = (int)parent.size(); std::vector<std::vector<int>> g(n); int roots = 0, root = -1; for (int i = 0; i < n; ++i) { if (parent[i] < 0) { ++roots; root = i; } else { if (parent[i] >= n || parent[i] == i) return false; g[i].push_back(parent[i]); g[parent[i]].push_back(i); } }
    if (roots != 1) return false; std::vector<char> seen(n, 0); std::vector<int> st = {root}; seen[root] = 1; int cnt = 0; while (!st.empty()) { int u = st.back(); st.pop_back(); ++cnt; for (int v : g[u]) if (!seen[v]) { seen[v] = 1; st.push_back(v); } } return cnt == n;
}
std::vector<int> bfsDist(const Adj& g, int s) { std::vector<int> d(g.size(), -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } return d; }
std::vector<int> centers(const Adj& g) {                                         // 리프 벗기기
    int n = (int)g.size(); std::vector<int> deg(n), leaves; for (int i = 0; i < n; ++i) { deg[i] = (int)g[i].size(); if (deg[i] <= 1) leaves.push_back(i); } int remaining = n;
    while (remaining > 2) { std::vector<int> next; remaining -= (int)leaves.size(); for (int u : leaves) for (int v : g[u]) if (--deg[v] == 1) next.push_back(v); leaves = next; } return leaves;
}
std::vector<int> reroot(const std::vector<int>& parent, int newRoot) { std::vector<int> p = parent; int prev = -1, u = newRoot; while (u >= 0) { int next = p[u]; p[u] = prev; prev = u; u = next; } return p; }         // newRoot → 옛 루트 경로의 부모 관계를 뒤집는다

int main() {
    assert(findRoot({-1, 0, 0, 1}) == 0 && findRoot({1, 0}) == -1 && findRoot({-1, -1}) == -2 && validate({-1, 0, 0, 1}) && !validate({1, 2, 0}) && !validate({-1, -1}));
    std::mt19937 rng(12);
    for (int it = 0; it < 100000; ++it) {                                        // ① 무작위로 망가뜨린 입력
        int n = 1 + (int)(rng() % 7); std::vector<int> p(n, -1); for (int i = 1; i < n; ++i) p[i] = (int)(rng() % i); for (int k = (int)(rng() % 3); k > 0; --k) p[rng() % n] = rng() % 4 == 0 ? -1 : (int)(rng() % (n + 1)) - (rng() % 4 == 0 ? 1 : 0);
        assert(validate(p) == bruteValid(p));
    }
    for (int it = 0; it < 3000; ++it) {                                          // ② 중심 = 이심률 최소, ③ 루트 바꾸기
        int n = 1 + (int)(rng() % 40); std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = (int)(rng() % i); Adj g(n); for (int i = 1; i < n; ++i) { g[i].push_back(par[i]); g[par[i]].push_back(i); }
        std::vector<int> ecc(n); for (int u = 0; u < n; ++u) { std::vector<int> d = bfsDist(g, u); ecc[u] = *std::max_element(d.begin(), d.end()); } int radius = *std::min_element(ecc.begin(), ecc.end()); std::vector<int> want; for (int u = 0; u < n; ++u) if (ecc[u] == radius) want.push_back(u);
        std::vector<int> c = centers(g); std::sort(c.begin(), c.end()); assert(c == want && (c.size() == 1 || c.size() == 2));                                        // 중심 1~2 개, 이심률 최소
        std::vector<int> best; int bestH = n; for (int u = 0; u < n; ++u) { std::vector<int> d = bfsDist(g, u); int h = *std::max_element(d.begin(), d.end()); if (h < bestH) { bestH = h; } } assert(bestH == radius);          // 높이가 가장 작은 루트의 높이 = 반지름
        int nr = (int)(rng() % n); std::vector<int> q = reroot(par, nr); std::vector<int> dd = bfsDist(g, nr); assert(findRoot(q) == nr && validate(q));
        for (int u = 0; u < n; ++u) { int depth = 0, x = u; while (q[x] >= 0) { x = q[x]; ++depth; } assert(depth == dd[u]); }                                                // 깊이 = 새 루트에서의 BFS 거리
        std::vector<std::pair<int, int>> e1, e2; for (int i = 0; i < n; ++i) { if (par[i] >= 0) e1.push_back({std::min(i, par[i]), std::max(i, par[i])}); if (q[i] >= 0) e2.push_back({std::min(i, q[i]), std::max(i, q[i])}); } std::sort(e1.begin(), e1.end()); std::sort(e2.begin(), e2.end()); assert(e1 == e2);          // 간선 집합 불변
    }
    { int n = 1000000; std::vector<int> chain(n, -1); for (int i = 1; i < n; ++i) chain[i] = i - 1; std::vector<int> r2 = reroot(chain, n - 1); assert(findRoot(r2) == n - 1 && r2[0] == 1 && r2[n - 2] == n - 1); std::cout << "Root: validators agreed on 10^5 corrupted parent arrays; centers = minimum-eccentricity vertices and rerooting preserved the edge set on 3000 random trees; a 10^6 chain was rerooted in one pass" << std::endl; }
    return 0;
}
// Time Complexity: 루트 찾기 O(n), 중심 O(n), reroot O(경로 길이)
// Space Complexity: O(n)
```
## Parent()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 부모 포인터와 자식 목록을 *함께* 유지하는 동적 트리: 리프 추가·리프 삭제·부분 트리 옮기기(reparent).  옮기려는 곳이 자기 자손이면 사이클이 생기므로 거부해야 한다.
//  ① 무작위 연산열을 간선 집합 모델(std::set)과 대조하고, 매 단계 양방향 일관성(parent[c] = p ⇔ c ∈ children[p])과 사이클 없음을 검사.
//  ② 거부 판정을 브루트포스(옮긴 뒤 사이클이 생기는지 직접 확인)와 대조.  ③ k 번째 조상: 이진 승(binary lifting) O(log n) vs 부모를 k 번 따라가기, 조상 사슬(루트까지의 경로).
struct DynTree {
    std::vector<int> parent; std::vector<std::vector<int>> children; std::vector<char> alive; int root = 0;
    explicit DynTree(int cap) : parent(cap, -2), children(cap), alive(cap, 0) {}
    void makeRoot(int r) { root = r; parent[r] = -1; alive[r] = 1; }
    bool addLeaf(int p, int c) { if (!alive[p] || alive[c]) return false; parent[c] = p; alive[c] = 1; children[p].push_back(c); return true; }
    bool removeLeaf(int c) { if (!alive[c] || c == root || !children[c].empty()) return false; auto& v = children[parent[c]]; v.erase(std::find(v.begin(), v.end(), c)); parent[c] = -2; alive[c] = 0; return true; }
    bool isAncestor(int a, int x) const { for (int u = x; u >= 0; u = parent[u]) if (u == a) return true; return false; }                 // a 가 x 의 조상(자기 자신 포함)인가
    bool move(int c, int newParent) {                                            // 부분 트리 c 를 newParent 아래로
        if (!alive[c] || !alive[newParent] || c == root || isAncestor(c, newParent)) return false;                                   // 자기 자손 밑으로는 못 간다 (사이클)
        auto& v = children[parent[c]]; v.erase(std::find(v.begin(), v.end(), c)); parent[c] = newParent; children[newParent].push_back(c); return true;
    }
    bool consistent() const {
        int cnt = 0; for (size_t i = 0; i < parent.size(); ++i) { if (!alive[i]) { if (!children[i].empty()) return false; continue; } ++cnt; if ((int)i == root) { if (parent[i] != -1) return false; } else { if (parent[i] < 0 || !alive[parent[i]]) return false; if (std::count(children[parent[i]].begin(), children[parent[i]].end(), (int)i) != 1) return false; } for (int c : children[i]) if (parent[c] != (int)i) return false; }
        for (size_t i = 0; i < parent.size(); ++i) if (alive[i]) { int u = (int)i, steps = 0; while (parent[u] >= 0 && steps <= cnt) { u = parent[u]; ++steps; } if (u != root || steps > cnt) return false; }               // 모든 노드의 부모 사슬이 루트에서 끝난다
        return true;
    }
};
struct Lifting {                                                                 // up[j][v] = v 의 2^j 번째 조상 (없으면 −1)
    std::vector<std::vector<int>> up; explicit Lifting(const std::vector<int>& parent) { int n = (int)parent.size(), L = 1; while ((1 << L) < n) ++L; up.assign(L + 1, std::vector<int>(n, -1)); up[0] = parent; for (int j = 1; j <= L; ++j) for (int v = 0; v < n; ++v) up[j][v] = up[j - 1][v] < 0 ? -1 : up[j - 1][up[j - 1][v]]; }
    int kth(int v, long k) const { for (int j = 0; k > 0 && v >= 0; ++j, k >>= 1) { if (j >= (int)up.size()) return -1; if (k & 1) v = up[j][v]; } return v; }
};

int main() {
    std::mt19937 rng(14);
    for (int round = 0; round < 200; ++round) {
        const int CAP = 30; DynTree t(CAP); t.makeRoot(0); std::set<std::pair<int, int>> edges;                                     // 모델: (부모, 자식) 간선 집합
        for (int op = 0; op < 300; ++op) {
            int k = (int)(rng() % 3), a = (int)(rng() % CAP), b = (int)(rng() % CAP);
            if (k == 0) { bool ok = t.addLeaf(a, b); bool want = std::count_if(edges.begin(), edges.end(), [&](auto& e) { return e.second == b; }) == 0 && b != 0 && (a == 0 || std::count_if(edges.begin(), edges.end(), [&](auto& e) { return e.second == a; }) == 1); assert(ok == want); if (ok) edges.insert({a, b}); }
            else if (k == 1) { bool ok = t.removeLeaf(a); bool isChild = std::count_if(edges.begin(), edges.end(), [&](auto& e) { return e.second == a; }) == 1, hasKid = std::count_if(edges.begin(), edges.end(), [&](auto& e) { return e.first == a; }) > 0; assert(ok == (isChild && !hasKid)); if (ok) for (auto it = edges.begin(); it != edges.end(); ++it) if (it->second == a) { edges.erase(it); break; } }
            else { DynTree copy = t; bool ok = t.move(a, b);                                                                      // ② 브루트포스: 실제로 옮겨 보고 사이클이 생기는지
                bool legal = copy.alive[a] && copy.alive[b] && a != copy.root; if (legal) { auto& v = copy.children[copy.parent[a]]; v.erase(std::find(v.begin(), v.end(), a)); copy.parent[a] = b; copy.children[b].push_back(a); int u = b, steps = 0; while (copy.parent[u] >= 0 && steps <= CAP) { u = copy.parent[u]; ++steps; } legal = u == copy.root && steps <= CAP; }
                assert(ok == legal); if (ok) { for (auto it = edges.begin(); it != edges.end(); ++it) if (it->second == a) { edges.erase(it); break; } edges.insert({b, a}); } }
            assert(t.consistent()); std::set<std::pair<int, int>> actual; for (int i = 0; i < CAP; ++i) if (t.alive[i] && i != t.root) actual.insert({t.parent[i], i}); assert(actual == edges);
        }
    }
    // ③ k 번째 조상 (이진 승 vs 부모 따라가기), 조상 사슬
    for (int it = 0; it < 300; ++it) { int n = 1 + (int)(rng() % 300); std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = std::max(0, i - 1 - (int)(rng() % 4)); Lifting lf(par);
        for (int q = 0; q < 200; ++q) { int v = (int)(rng() % n); long k = (long)(rng() % (n + 3)); int u = v; for (long s = 0; s < k && u >= 0; ++s) u = par[u]; assert(lf.kth(v, k) == u); }
        int v = (int)(rng() % n); std::vector<int> chain; for (int u = v; u >= 0; u = par[u]) chain.push_back(u); assert(chain.back() == 0 && lf.kth(v, (long)chain.size() - 1) == 0 && lf.kth(v, (long)chain.size()) == -1); }
    { int n = 1000000; std::vector<int> chain(n, -1); for (int i = 1; i < n; ++i) chain[i] = i - 1; Lifting lf(chain); assert(lf.kth(n - 1, 999999) == 0 && lf.kth(n - 1, 123456) == n - 1 - 123456 && lf.kth(n - 1, 1000000) == -1);
      std::cout << "Parent: 60000 random leaf-add / leaf-remove / move operations kept parent and child links consistent and rejected exactly the moves that would create a cycle; binary lifting answered k-th ancestor queries on a 10^6 chain" << std::endl; }
    return 0;
}
// Time Complexity: 추가·삭제 O(차수), 이동 O(깊이) (사이클 검사), k 번째 조상 O(log n)
// Space Complexity: O(n) (이진 승 O(n log n))
```
## Child()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 자식 접근: 순서가 있는 트리에서 k 번째 자식 읽기·그 자리에 삽입·삭제·교체·"이 노드는 몇 번째 자식인가".  왼쪽 자식–오른쪽 형제(LCRS) 표현에서 구현하고 std::vector<std::vector<int>> 모델과 무작위 연산열로 대조한다.
//  LCRS 에서 k 번째 자식은 형제 사슬을 k 번 따라가므로 O(k) 이고, 마지막 자식 추가는 꼬리 포인터로 O(1) 이다.  떼어 낸 부분 트리는 다시 다른 곳에 붙일 수 있다(이동).
//  불변식 — 모든 노드는 많아야 한 부모의 목록에만 있고, 목록을 걸으면 모델과 같은 순서이며, parent 가 일치하고, 자기 자손 밑으로는 붙이지 않는다.
struct Forest {
    std::vector<int> first, next, last, parent, count; explicit Forest(int n) : first(n, -1), next(n, -1), last(n, -1), parent(n, -1), count(n, 0) {}
    int nthChild(int u, int k) const { int c = first[u]; while (k-- > 0 && c >= 0) c = next[c]; return c; }               // O(k)
    int indexOf(int c) const { int p = parent[c]; if (p < 0) return -1; int k = 0; for (int x = first[p]; x != c; x = next[x]) ++k; return k; }
    bool isAncestorOrSelf(int a, int x) const { for (int u = x; u >= 0; u = parent[u]) if (u == a) return true; return false; }
    bool insertChildAt(int u, int pos, int c) {                                    // c 는 부모가 없는(떼어 낸) 노드여야 하고 u 의 조상이 아니어야 한다
        if (pos < 0 || pos > count[u] || parent[c] >= 0 || isAncestorOrSelf(c, u)) return false;
        parent[c] = u; next[c] = -1; if (count[u] == 0) { first[u] = last[u] = c; } else if (pos == 0) { next[c] = first[u]; first[u] = c; } else if (pos == count[u]) { next[last[u]] = c; last[u] = c; } else { int prev = nthChild(u, pos - 1); next[c] = next[prev]; next[prev] = c; }
        ++count[u]; return true;
    }
    int removeChildAt(int u, int pos) {                                            // 떼어 낸 자식(부분 트리 통째로)의 번호, 없으면 −1
        if (pos < 0 || pos >= count[u]) return -1; int c; if (pos == 0) { c = first[u]; first[u] = next[c]; if (first[u] < 0) last[u] = -1; } else { int prev = nthChild(u, pos - 1); c = next[prev]; next[prev] = next[c]; if (c == last[u]) last[u] = prev; }
        next[c] = -1; parent[c] = -1; --count[u]; return c;
    }
    bool replaceChild(int u, int pos, int c) { int old = removeChildAt(u, pos); if (old < 0) return false; if (!insertChildAt(u, pos, c)) { insertChildAt(u, pos, old); return false; } return true; }
};

int main() {
    std::mt19937 rng(21);
    for (int round = 0; round < 300; ++round) {
        const int N = 25; Forest f(N); std::vector<std::vector<int>> model(N); std::vector<int> mparent(N, -1);
        auto modelAncestor = [&](int a, int x) { for (int u = x; u >= 0; u = mparent[u]) if (u == a) return true; return false; };
        for (int op = 0; op < 400; ++op) {
            int u = (int)(rng() % N), c = (int)(rng() % N), pos = (int)(rng() % (model[u].size() + 2)), k = (int)(rng() % 4);
            if (k == 0) { bool want = pos <= (int)model[u].size() && mparent[c] < 0 && !modelAncestor(c, u); bool ok = f.insertChildAt(u, pos, c); assert(ok == want); if (ok) { model[u].insert(model[u].begin() + pos, c); mparent[c] = u; } }
            else if (k == 1) { int got = f.removeChildAt(u, pos); if (pos < (int)model[u].size()) { int want = model[u][pos]; assert(got == want); model[u].erase(model[u].begin() + pos); mparent[want] = -1; } else assert(got == -1); }
            else if (k == 2) { bool ok = f.replaceChild(u, pos, c); if (pos < (int)model[u].size()) { int old = model[u][pos]; bool legal = c == old || (mparent[c] < 0 && !modelAncestor(c, u)); assert(ok == legal); if (ok && c != old) { model[u][pos] = c; mparent[old] = -1; mparent[c] = u; } } else assert(!ok); }
            else { int p = mparent[c]; assert(f.indexOf(c) == (p < 0 ? -1 : (int)(std::find(model[p].begin(), model[p].end(), c) - model[p].begin()))); if (pos < (int)model[u].size()) assert(f.nthChild(u, pos) == model[u][pos]); else assert(f.nthChild(u, pos) == -1); }
            for (int x = 0; x < N; ++x) { std::vector<int> walk; for (int y = f.first[x]; y >= 0; y = f.next[y]) { walk.push_back(y); assert(f.parent[y] == x); } assert(walk == model[x] && f.count[x] == (int)model[x].size() && (walk.empty() ? f.last[x] < 0 : f.last[x] == walk.back()) && f.parent[x] == mparent[x]); }
        }
    }
    { Forest f(100001); int built = 0; for (int i = 1; i <= 100000; ++i) built += f.insertChildAt(0, f.count[0], i); assert(built == 100000 && f.nthChild(0, 99999) == 100000 && f.last[0] == 100000 && f.indexOf(77777) == 77776);
      std::cout << "Child: LCRS insert/remove/replace/nth-child matched a vector-of-vectors model over 120000 random operations, cycles were rejected, and 10^5 tail appends were O(1) each" << std::endl; }
    return 0;
}
// Time Complexity: k 번째 자식·위치 삽입·삭제 O(k), 맨 뒤 삽입 O(1)
// Space Complexity: O(n)
```
## Sibling()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <vector>

// 형제: 같은 부모를 가진 노드들. 한 방향 연결(nextSibling)만 있으면 "이전 형제" 와 "중간 삭제"가 형제 사슬을 처음부터 훑어야 하므로 O(k) 이고, 양방향(prevSibling 추가)으로 하면 O(1) 이다.
//  ① 두 방식을 모두 구현해 std::vector 모델과 무작위 연산(앞/뒤에 삽입, 특정 형제 앞/뒤에 삽입, 삭제, 인접 교환)을 대조  ② 걸음 수를 세어 단방향의 삭제가 정확히 (위치) 걸음, 양방향은 0 걸음임을 확인
//  ③ 성질: 형제 수 = 부모의 차수, 마지막 노드의 nextSibling 은 없음, 모든 노드에서 next→prev 가 제자리로 돌아옴.
struct Sib {
    std::vector<int> next, prev, parent, first, last; bool doubly; long steps = 0;
    Sib(int n, bool d) : next(n, -1), prev(n, -1), parent(n, -1), first(n, -1), last(n, -1), doubly(d) {}
    void append(int p, int c) { parent[c] = p; next[c] = -1; prev[c] = last[p]; if (last[p] >= 0) next[last[p]] = c; else first[p] = c; last[p] = c; }
    void insertAfter(int s, int c) { int p = parent[s]; parent[c] = p; next[c] = next[s]; prev[c] = s; if (next[s] >= 0) prev[next[s]] = c; else last[p] = c; next[s] = c; }
    int prevOf(int c) { if (doubly) return prev[c]; int p = parent[c]; int x = first[p], before = -1; while (x != c) { before = x; x = next[x]; ++steps; } return before; }              // 단방향이면 처음부터 훑는다
    void unlink(int c) {
        int p = parent[c], b = prevOf(c), a = next[c]; if (b >= 0) next[b] = a; else first[p] = a; if (a >= 0) { if (doubly) prev[a] = b; } else last[p] = b;
        next[c] = prev[c] = parent[c] = -1;
    }
    void swapWithNext(int c) { int n = next[c]; if (n < 0) return; int p = parent[c], b = prevOf(c), a = next[n]; if (b >= 0) next[b] = n; else first[p] = n; next[n] = c; next[c] = a; if (doubly) { prev[n] = b; prev[c] = n; if (a >= 0) prev[a] = c; } if (a < 0) last[p] = c; }
};

int main() {
    std::mt19937 rng(8);
    for (int round = 0; round < 300; ++round) {
        for (int dbl = 0; dbl < 2; ++dbl) {
            const int N = 40; Sib s(N, dbl == 1); std::vector<int> model; std::vector<char> in(N, 0);                // 부모 0 의 자식 목록 하나를 조작한다 (노드 1..N−1)
            for (int op = 0; op < 300; ++op) {
                int c = 1 + (int)(rng() % (N - 1)), k = (int)(rng() % 5);
                if (k == 0 && !in[c]) { s.append(0, c); model.push_back(c); in[c] = 1; }
                else if (k == 1 && !in[c] && !model.empty()) { int ref = model[rng() % model.size()]; s.insertAfter(ref, c); model.insert(std::find(model.begin(), model.end(), ref) + 1, c); in[c] = 1; }
                else if (k == 2 && in[c]) { s.unlink(c); model.erase(std::find(model.begin(), model.end(), c)); in[c] = 0; }
                else if (k == 3 && in[c]) { auto it = std::find(model.begin(), model.end(), c); if (it + 1 != model.end()) { s.swapWithNext(c); std::iter_swap(it, it + 1); } }
                else if (k == 4 && in[c]) { auto it = std::find(model.begin(), model.end(), c); int want = it == model.begin() ? -1 : *(it - 1); assert(s.prevOf(c) == want && s.next[c] == (it + 1 == model.end() ? -1 : *(it + 1))); }
                std::vector<int> walk; for (int x = s.first[0]; x >= 0; x = s.next[x]) walk.push_back(x); assert(walk == model && (model.empty() ? s.last[0] < 0 && s.first[0] < 0 : s.last[0] == model.back()));                 // 순서·꼬리
                if (dbl) for (size_t i = 0; i < walk.size(); ++i) { assert(s.prev[walk[i]] == (i ? walk[i - 1] : -1)); if (i + 1 < walk.size()) assert(s.prev[s.next[walk[i]]] == walk[i]); }                                // next → prev 가 제자리로
            }
        }
    }
    // ② 걸음 수: 목록 크기 n 의 k 번째(0 부터) 노드를 지울 때 단방향은 k 걸음, 양방향은 0 걸음
    { const int n = 10000; Sib one(n + 1, false), two(n + 1, true); for (int i = 1; i <= n; ++i) { one.append(0, i); two.append(0, i); } one.steps = two.steps = 0; for (int target : {5000, 9000, 9999}) { one.unlink(target + 1); two.unlink(target + 1); }
      assert(one.steps == 5000 + 8999 + 9997 && two.steps == 0 && one.first[0] == two.first[0]);              // 앞의 노드를 이미 두 개 지운 뒤의 위치: 5000, 9000−1, 9999−2
      std::cout << "Sibling: singly and doubly linked sibling lists matched a vector model over 180000 random operations; unlinking three nodes of a 10^4 list took " << one.steps << " steps with next-only links and " << two.steps << " with prev links" << std::endl; }
    return 0;
}
// Time Complexity: 이전 형제·삭제 단방향 O(k) / 양방향 O(1), 삽입 O(1)
// Space Complexity: O(n) (양방향은 노드당 포인터 하나 더)
```
## Degree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <random>
#include <vector>

// 차수(degree): 노드의 자식 수 (뿌리 없는 트리에서는 이웃 수). 모든 트리에 성립하는 항등식으로 검증한다.
//  ① 자식 수의 합 = n − 1 (간선 수),  리프 수 = 1 + Σ_{차수≥2}(차수 − 1)  — 완전 k 진 트리면 리프 = (k−1)·내부 + 1.   뿌리 없는 트리: Σ 이웃 수 = 2(n−1), 리프(이웃 1) = 2 + Σ_{이웃≥3}(이웃 − 2).
//  ② 전위 순회의 차수열은 순서 있는 트리를 유일하게 정한다: Σ(d_i − 1) = −1 이고 진짜 접두사마다 Σ(d_i − 1) ≥ 0.  n 이 주어졌을 때 그런 수열의 개수는 카탈랑 수 C(n−1) — 전부 나열해 세고, 각각 복원한 트리의 차수열이 같은지 본다.
//  ③ Prüfer 열: n 개의 이름 붙은 노드의 트리는 길이 n − 2 열과 일대일 대응(케일리: n^(n−2) 개)이고, 노드 v 의 이웃 수 = 1 + (열에서 v 가 나온 횟수).
long catalan(int n) { long c = 1; for (int i = 0; i < n; ++i) c = c * 2 * (2 * i + 1) / (i + 2); return c; }
void enumerateDegreeSeqs(int n, std::vector<int>& seq, int balance, std::vector<std::vector<int>>& out) {       // 전위 차수열 전부
    if ((int)seq.size() == n) { if (balance == -1) out.push_back(seq); return; }
    int remaining = n - (int)seq.size();                                                                        // balance = Σ(d−1) 누적. 끝나기 전에는 ≥ 0 이어야 한다
    for (int d = 0; d <= remaining; ++d) { int nb = balance + d - 1; bool last = remaining == 1; if (!last && (nb < 0 || nb > remaining - 2)) continue; if (last && nb != -1) continue; seq.push_back(d); enumerateDegreeSeqs(n, seq, nb, out); seq.pop_back(); }
}
std::vector<int> rebuildFromDegrees(const std::vector<int>& d) {                                                // 전위 차수열 → 부모 배열 (전위 순번이 id)
    std::vector<int> parent(d.size(), -1), stack; std::vector<int> remaining(d.size());                         // stack: 아직 자식이 더 필요한 노드
    for (size_t i = 0; i < d.size(); ++i) { if (i) { parent[i] = stack.back(); if (--remaining[stack.back()] == 0) stack.pop_back(); } remaining[i] = d[i]; if (d[i] > 0) stack.push_back((int)i); }
    assert(stack.empty()); return parent;
}
std::vector<std::pair<int, int>> pruferDecode(const std::vector<int>& seq, int n) {
    std::vector<int> deg(n, 1); for (int v : seq) ++deg[v]; std::vector<std::pair<int, int>> edges; int ptr = 0; while (deg[ptr] != 1) ++ptr; int leaf = ptr;
    for (int v : seq) { edges.push_back({std::min(leaf, v), std::max(leaf, v)}); if (--deg[v] == 1 && v < ptr) leaf = v; else { ++ptr; while (deg[ptr] != 1) ++ptr; leaf = ptr; } }
    edges.push_back({std::min(leaf, n - 1), std::max(leaf, n - 1)}); return edges;
}

int main() {
    std::mt19937 rng(6);
    for (int it = 0; it < 5000; ++it) {                                                                         // ① 항등식 (무작위 트리 n ≤ 60)
        int n = 1 + (int)(rng() % 60); std::vector<int> par(n, -1); int shape = (int)(rng() % 3); for (int i = 1; i < n; ++i) par[i] = shape == 0 ? (int)(rng() % i) : shape == 1 ? std::max(0, i - 1 - (int)(rng() % 2)) : (int)(rng() % std::min(i, 4));
        std::vector<int> d(n, 0), nb(n, 0); for (int i = 1; i < n; ++i) { ++d[par[i]]; ++nb[i]; ++nb[par[i]]; }
        long sum = 0, leaves = 0, extra = 0, nbSum = 0, nbExtra = 0, nbLeaves = 0; for (int i = 0; i < n; ++i) { sum += d[i]; leaves += d[i] == 0; if (d[i] >= 2) extra += d[i] - 1; nbSum += nb[i]; nbLeaves += nb[i] == 1; if (nb[i] >= 3) nbExtra += nb[i] - 2; }
        assert(sum == n - 1 && leaves == 1 + extra && nbSum == 2 * (n - 1));
        if (n >= 2) assert(nbLeaves == 2 + nbExtra);
    }
    for (int k : {2, 3, 5}) { int levels = 1 + (int)(rng() % 5); long internal = 0, leaves = 0, cur = 1; for (int l = 0; l < levels; ++l) { internal += cur; cur *= k; } leaves = cur; assert(leaves == (long)(k - 1) * internal + 1); }          // 완전 k 진 트리
    for (int n = 1; n <= 10; ++n) {                                                                             // ② 카탈랑
        std::vector<std::vector<int>> all; std::vector<int> seq; enumerateDegreeSeqs(n, seq, 0, all); assert((long)all.size() == catalan(n - 1));
        for (auto& dseq : all) { std::vector<int> par = rebuildFromDegrees(dseq); std::vector<int> d2(n, 0); for (int i = 1; i < n; ++i) { assert(par[i] >= 0 && par[i] < i); ++d2[par[i]]; } assert(d2 == dseq); }          // 복원한 트리의 차수열 = 입력
    }
    for (int n = 2; n <= 7; ++n) {                                                                              // ③ Prüfer: 모든 열 n^(n−2) 개
        long total = 1; for (int i = 0; i < n - 2; ++i) total *= n; std::vector<std::vector<std::pair<int, int>>> trees; std::vector<int> seq(n - 2, 0);
        for (long code = 0; code < total; ++code) { long c = code; for (int i = 0; i < n - 2; ++i) { seq[i] = (int)(c % n); c /= n; } auto e = pruferDecode(seq, n); std::sort(e.begin(), e.end()); assert((int)e.size() == n - 1);
            std::vector<int> nb(n, 0); for (auto& x : e) { ++nb[x.first]; ++nb[x.second]; } std::vector<int> occ(n, 0); for (int v : seq) ++occ[v]; for (int v = 0; v < n; ++v) assert(nb[v] == 1 + occ[v]);              // 이웃 수 = 1 + 출현 횟수
            std::vector<int> comp(n); for (int i = 0; i < n; ++i) comp[i] = i; std::function<int(int)> fnd = [&](int x) { return comp[x] == x ? x : comp[x] = fnd(comp[x]); }; for (auto& x : e) { int a = fnd(x.first), b = fnd(x.second); assert(a != b); comp[a] = b; }        // 사이클 없는 n−1 간선 = 트리
            trees.push_back(e); }
        std::sort(trees.begin(), trees.end()); assert(std::unique(trees.begin(), trees.end()) == trees.end() && (long)trees.size() == total);       // 서로 다른 트리 n^(n−2) 개
    }
    std::cout << "Degree: sum/leaf identities held on 5000 random trees; the preorder degree sequences of all ordered trees up to 10 nodes were enumerated and counted as Catalan numbers; Pruefer sequences for n <= 7 gave n^(n-2) distinct labelled trees with degree = 1 + occurrences" << std::endl;
    return 0;
}
// Time Complexity: 차수 계산 O(n), 카탈랑 열거 O(C(n−1)·n)
// Space Complexity: O(n)
```
## Depth()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 깊이(depth): 루트에서 노드까지의 간선 수. 노드마다 부모를 끝까지 따라가면 O(n·h) 이고 사슬 모양에서는 O(n²), 이미 구한 깊이를 재사용하면 O(n).
//  ① 세 방법을 대조: 부모 따라가기(순진) · BFS · 메모이제이션(부모가 *번호상 뒤*에 있어도 되는 반복문 — 재귀 없음).  걸음 수를 세어 순진한 쪽 Σ(깊이), 메모 쪽 ≤ 2n 을 확인.
//  ② 성질: 깊이의 합 = 경로 길이 합, 완전 이진 트리(높이 h)에서는 (h−1)·2^(h+1) + 2.   ③ 깊이 10^6 사슬을 반복문으로(재귀로는 스택 오버플로).
std::vector<int> depthNaive(const std::vector<int>& parent, long& steps) { std::vector<int> d(parent.size()); steps = 0; for (size_t i = 0; i < parent.size(); ++i) { int x = (int)i, k = 0; while (parent[x] >= 0) { x = parent[x]; ++k; ++steps; } d[i] = k; } return d; }
std::vector<int> depthBfs(const std::vector<int>& parent) { int n = (int)parent.size(); std::vector<std::vector<int>> kids(n); int root = -1; for (int i = 0; i < n; ++i) { if (parent[i] < 0) root = i; else kids[parent[i]].push_back(i); } std::vector<int> d(n, -1); std::queue<int> q; d[root] = 0; q.push(root); while (!q.empty()) { int u = q.front(); q.pop(); for (int v : kids[u]) { d[v] = d[u] + 1; q.push(v); } } return d; }
std::vector<int> depthMemo(const std::vector<int>& parent, long& steps) {                                       // 아직 모르는 노드에서 위로 올라가다 아는 곳을 만나면 되돌아 내려오며 채운다
    int n = (int)parent.size(); std::vector<int> d(n, -1), stack; steps = 0;
    for (int i = 0; i < n; ++i) { if (d[i] >= 0) continue; int x = i; while (x >= 0 && d[x] < 0) { stack.push_back(x); x = parent[x]; ++steps; } int base = x < 0 ? -1 : d[x]; while (!stack.empty()) { d[stack.back()] = ++base; stack.pop_back(); ++steps; } }
    return d;
}

int main() {
    std::mt19937 rng(19);
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 80), shape = (int)(rng() % 3); std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = shape == 0 ? (int)(rng() % i) : shape == 1 ? i - 1 : (int)(rng() % std::min(i, 3));
        std::vector<int> perm(n); for (int i = 0; i < n; ++i) perm[i] = i; std::shuffle(perm.begin(), perm.end(), rng); std::vector<int> p(n, -1); for (int i = 0; i < n; ++i) p[perm[i]] = par[i] < 0 ? -1 : perm[par[i]];      // 라벨을 섞어 부모가 뒤 번호일 수 있게
        long sn, sm; std::vector<int> a = depthNaive(p, sn), b = depthBfs(p), c = depthMemo(p, sm); assert(a == b && b == c && sm <= 2L * n);
        long sum = 0; for (int x : a) sum += x; assert(sn == sum);                                                // 순진한 걸음 수 = Σ 깊이
    }
    for (int h = 0; h <= 12; ++h) { int n = (1 << (h + 1)) - 1; std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = (i - 1) / 2; long steps; std::vector<int> d = depthMemo(par, steps); long sum = 0; for (int x : d) sum += x; assert(sum == (long)(h - 1) * (1L << (h + 1)) + 2 && *std::max_element(d.begin(), d.end()) == h); }
    { const int n = 1000000; std::vector<int> chain(n, -1); for (int i = 1; i < n; ++i) chain[i] = i - 1; long steps; std::vector<int> d = depthMemo(chain, steps); assert(d[n - 1] == n - 1 && steps <= 2L * n);
      long naiveSteps = (long)n * (n - 1) / 2;
      std::cout << "Depth: parent-climbing, BFS and memoised depths agreed on 3000 random trees (memoised steps <= 2n); the depth-10^6 chain took " << steps << " steps instead of the naive " << naiveSteps << std::endl; }
    return 0;
}
// Time Complexity: 순진 O(n·h), BFS·메모이제이션 O(n)
// Space Complexity: O(n)
```
## Height()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 높이(height): 노드에서 가장 깊은 후손까지의 간선 수 (리프 0, 빈 트리 −1).  트리의 높이 = 루트의 높이 = 최대 깊이.  재귀 풀이는 사슬 모양에서 스택이 깊어지므로 BFS 순서를 뒤집어 반복문으로 계산한다.
//  ① 재귀(작은 트리)·반복(BFS 역순)·최대 깊이 세 방법을 대조.  ② k 진 트리 경계: n ≤ (k^(h+1) − 1)/(k − 1), 즉 h ≥ ⌈log_k(n(k−1) + 1)⌉ − 1, 그리고 h ≤ n − 1.  완전 k 진 트리는 하한을 정확히 채운다.
//  ③ 이진 탐색 트리의 높이는 삽입 순서에 달려 있다: 정렬된 순서로 넣으면 n − 1 (사슬), 무작위 순서면 약 4.3·ln n (반복문으로 구현).
std::vector<int> heightsIterative(const std::vector<int>& parent, int& root) {
    int n = (int)parent.size(); std::vector<std::vector<int>> kids(n); root = -1; for (int i = 0; i < n; ++i) { if (parent[i] < 0) root = i; else kids[parent[i]].push_back(i); }
    std::vector<int> order = {root}; for (size_t i = 0; i < order.size(); ++i) for (int v : kids[order[i]]) order.push_back(v);                // BFS 순서
    std::vector<int> h(n, 0); for (size_t i = order.size(); i-- > 0;) { int u = order[i]; if (parent[u] >= 0) h[parent[u]] = std::max(h[parent[u]], h[u] + 1); }          // 자식이 먼저 확정되는 역순
    return h;
}
int heightRec(const std::vector<std::vector<int>>& kids, int u) { int h = 0; for (int v : kids[u]) h = std::max(h, 1 + heightRec(kids, v)); return h; }
int maxDepth(const std::vector<int>& parent) { int best = 0; for (size_t i = 0; i < parent.size(); ++i) { int d = 0; for (int x = (int)i; parent[x] >= 0; x = parent[x]) ++d; best = std::max(best, d); } return best; }
struct BST { std::vector<int> key, left, right; int root = -1;                                                  // 반복문 삽입 (재귀 없음)
    void insert(int k) { key.push_back(k); left.push_back(-1); right.push_back(-1); int id = (int)key.size() - 1; if (root < 0) { root = id; return; } int u = root; while (true) { int& next = k < key[u] ? left[u] : right[u]; if (next < 0) { next = id; return; } u = next; } }
    int height() const { if (root < 0) return -1; std::vector<std::pair<int, int>> st = {{root, 0}}; int best = 0; while (!st.empty()) { auto cur = st.back(); st.pop_back(); best = std::max(best, cur.second); if (left[cur.first] >= 0) st.push_back({left[cur.first], cur.second + 1}); if (right[cur.first] >= 0) st.push_back({right[cur.first], cur.second + 1}); } return best; } };

int main() {
    std::mt19937 rng(23);
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 80), shape = (int)(rng() % 3); std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = shape == 0 ? (int)(rng() % i) : shape == 1 ? std::max(0, i - 1 - (int)(rng() % 2)) : (int)(rng() % std::min(i, 3));
        int root; std::vector<int> h = heightsIterative(par, root); std::vector<std::vector<int>> kids(n); for (int i = 1; i < n; ++i) kids[par[i]].push_back(i);
        for (int u = 0; u < n; ++u) assert(h[u] == heightRec(kids, u)); assert(h[root] == maxDepth(par) && h[root] <= n - 1);                           // ①
        int maxDeg = 0; for (auto& v : kids) maxDeg = std::max<int>(maxDeg, (int)v.size()); if (maxDeg >= 2) { double lower = std::ceil(std::log((double)n * (maxDeg - 1) + 1) / std::log((double)maxDeg) - 1e-9) - 1; assert(h[root] >= lower); }                    // ② 하한
    }
    for (int k : {2, 3, 4}) for (int h = 0; h <= 6; ++h) { long n = 0, p = 1; for (int d = 0; d <= h; ++d) { n += p; p *= k; } assert(n == (long)((std::pow((double)k, h + 1) - 1) / (k - 1) + 0.5)); double lower = std::ceil(std::log((double)n * (k - 1) + 1) / std::log((double)k) - 1e-9) - 1; assert(lower == h); }         // 완전 k 진 트리는 하한을 정확히 채운다
    { BST sorted; for (int i = 0; i < 3000; ++i) sorted.insert(i); assert(sorted.height() == 2999);                                                      // ③ 정렬된 삽입 = 사슬
      std::vector<int> keys(100000); std::iota(keys.begin(), keys.end(), 0); long total = 0; int worst = 0; const int TRIALS = 5; for (int t = 0; t < TRIALS; ++t) { std::shuffle(keys.begin(), keys.end(), rng); BST b; for (int k : keys) b.insert(k); int h = b.height(); worst = std::max(worst, h); total += h; }
      double mean = (double)total / TRIALS, ln = std::log(100000.0); assert(mean > std::log2(100000.0) && mean < 4.5 * ln + 10 && worst < 6 * ln);
      std::cout << "Height: recursive, BFS-reverse and max-depth heights agreed on 3000 random trees; sorted insertion gave a BST of height 2999 while random insertion of 10^5 keys gave " << mean << " on average (4.3 ln n = " << 4.3 * ln << ")" << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n) (반복문; 재귀는 O(h) 호출 스택)
```
## Level()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 레벨(level): 루트가 0 층이고 깊이가 같은 노드들의 모임 — 레벨 순서 순회(BFS)의 단위.
//  ① 레벨별 노드 목록을 두 가지로 만든다: BFS 큐(층별 묶음) vs 깊이 우선 전위 순회에서 깊이별로 모으기 — 같은 자식 순서면 *층 안의 순서까지 완전히 같다*(왼쪽→오른쪽).
//  ② 성질: 층 d 의 노드 수 ≤ k^d (k = 최대 차수), 층별 크기의 합 = n, 완전 이진 트리의 층 d 는 정확히 2^d 개, 힙 배열(1 기반 인덱스 i)에서 레벨 = ⌊log₂ i⌋ — BFS 로 얻은 레벨과 같다.
//  ③ 지그재그(나선) 순서 = 홀수 층을 뒤집은 것.  너비(최대 층 크기)와 레벨 수(높이 + 1).
typedef std::vector<std::vector<int>> Levels;
Levels levelsBfs(const std::vector<std::vector<int>>& kids, int root) { Levels out; std::queue<int> q; q.push(root); while (!q.empty()) { size_t sz = q.size(); out.emplace_back(); for (size_t i = 0; i < sz; ++i) { int u = q.front(); q.pop(); out.back().push_back(u); for (int v : kids[u]) q.push(v); } } return out; }
Levels levelsDfs(const std::vector<std::vector<int>>& kids, int root) { Levels out; std::vector<std::pair<int, int>> st = {{root, 0}}; while (!st.empty()) { auto cur = st.back(); st.pop_back(); if ((int)out.size() <= cur.second) out.emplace_back(); out[cur.second].push_back(cur.first); for (size_t i = kids[cur.first].size(); i-- > 0;) st.push_back({kids[cur.first][i], cur.second + 1}); } return out; }       // 반복 전위 순회, 깊이별 수집
Levels zigzag(Levels l) { for (size_t d = 1; d < l.size(); d += 2) std::reverse(l[d].begin(), l[d].end()); return l; }

int main() {
    std::mt19937 rng(33);
    for (int it = 0; it < 5000; ++it) {
        int n = 1 + (int)(rng() % 100), shape = (int)(rng() % 4); std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = shape == 0 ? (int)(rng() % i) : shape == 1 ? std::max(0, i - 1 - (int)(rng() % 2)) : shape == 2 ? (int)(rng() % std::min(i, 3)) : (i - 1) / 2;
        std::vector<std::vector<int>> kids(n); for (int i = 1; i < n; ++i) kids[par[i]].push_back(i); Levels a = levelsBfs(kids, 0), b = levelsDfs(kids, 0); assert(a == b);                                         // ① 층 안의 순서까지 일치
        size_t total = 0, maxDeg = 0; for (auto& v : kids) maxDeg = std::max(maxDeg, v.size()); double cap = 1; for (size_t d = 0; d < a.size(); ++d) { total += a[d].size(); assert((double)a[d].size() <= cap + 1e-9); cap *= (double)std::max<size_t>(maxDeg, 1); }   // ② 층 크기 ≤ k^d
        assert((int)total == n); std::vector<int> depth(n, 0); for (int i = 1; i < n; ++i) depth[i] = depth[par[i]] + 1; for (size_t d = 0; d < a.size(); ++d) for (int u : a[d]) assert(depth[u] == (int)d);                                // 레벨 = 깊이
        Levels z = zigzag(a); for (size_t d = 0; d < a.size(); ++d) { auto expect = a[d]; if (d % 2) std::reverse(expect.begin(), expect.end()); assert(z[d] == expect); }                                              // ③
        size_t width = 0; for (auto& l : a) width = std::max(width, l.size()); assert(a.size() == (size_t)(*std::max_element(depth.begin(), depth.end())) + 1 && width >= 1);
    }
    for (int n = 1; n <= 1000; ++n) {                                                                           // 힙 배열: 레벨 = ⌊log₂ i⌋ (1 기반)
        std::vector<std::vector<int>> kids(n + 1); for (int i = 2; i <= n; ++i) kids[i / 2].push_back(i); Levels l = levelsBfs(kids, 1);
        for (size_t d = 0; d < l.size(); ++d) for (int u : l[d]) assert((int)d == 31 - __builtin_clz((unsigned)u)); for (size_t d = 0; d + 1 < l.size(); ++d) assert(l[d].size() == (1u << d));          // 마지막을 뺀 층은 가득 참
    }
    { int n = (1 << 20) - 1; std::vector<std::vector<int>> kids(n); for (int i = 1; i < n; ++i) kids[(i - 1) / 2].push_back(i); Levels l = levelsDfs(kids, 0); assert(l.size() == 20 && l[19].size() == (1u << 19) && l == levelsBfs(kids, 0));
      std::cout << "Level: BFS layering and DFS-by-depth collection agreed (including within-level order) on 5000 random trees and a 2^20-node complete tree; heap indices matched floor(log2 i); zig-zag order verified" << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n) (BFS 큐 = 가장 넓은 층)
```
## Size()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 크기(size): 노드 하나가 만드는 부분 트리의 노드 수.  BFS 역순으로 자식의 크기를 부모에 더하면 O(n) (재귀 없음).
//  ① 노드마다 부분 트리를 다시 세는 순진한 방법과 대조.  ② 오일러 투어 구간 성질 — 전위 번호 tin 에서 부분 트리는 *연속 구간* [tin, tin + size) 이다: 모든 쌍 (u, v) 에서 "v 가 u 의 부분 트리에 속함" ⇔ tin[u] ≤ tin[v] < tin[u] + size[u] ⇔ 부모 따라 올라가면 u 를 만남.
//  ③ Σ size = Σ (깊이 + 1).  ④ 센트로이드: 크기 배열만으로 max(n − size[u], 자식 최대 크기) ≤ n/2 인 노드를 찾고, 하나씩 지워 보는 브루트포스와 대조 (1 개 또는 2 개).
std::vector<int> subtreeSizes(const std::vector<int>& parent, std::vector<int>& order) {
    int n = (int)parent.size(); std::vector<std::vector<int>> kids(n); int root = -1; for (int i = 0; i < n; ++i) { if (parent[i] < 0) root = i; else kids[parent[i]].push_back(i); }
    order = {root}; for (size_t i = 0; i < order.size(); ++i) for (int v : kids[order[i]]) order.push_back(v); std::vector<int> sz(n, 1); for (size_t i = order.size(); i-- > 1;) sz[parent[order[i]]] += sz[order[i]]; return sz;
}
int countNaive(const std::vector<std::vector<int>>& kids, int u) { int c = 0; std::vector<int> st = {u}; while (!st.empty()) { int x = st.back(); st.pop_back(); ++c; for (int v : kids[x]) st.push_back(v); } return c; }
std::vector<int> preorderNumbers(const std::vector<std::vector<int>>& kids, int root) { std::vector<int> tin(kids.size(), -1), st = {root}; int t = 0; while (!st.empty()) { int u = st.back(); st.pop_back(); tin[u] = t++; for (size_t i = kids[u].size(); i-- > 0;) st.push_back(kids[u][i]); } return tin; }
std::vector<int> centroidsBySizes(const std::vector<int>& parent, const std::vector<int>& sz) { int n = (int)parent.size(); std::vector<int> big(n, 0); for (int i = 0; i < n; ++i) { big[i] = n - sz[i]; } for (int i = 0; i < n; ++i) if (parent[i] >= 0) big[parent[i]] = std::max(big[parent[i]], sz[i]); std::vector<int> c; for (int i = 0; i < n; ++i) if (2 * big[i] <= n) c.push_back(i); return c; }
std::vector<int> centroidsBrute(const std::vector<int>& parent) {                                                  // 노드를 지웠을 때 가장 큰 조각이 n/2 이하
    int n = (int)parent.size(); std::vector<std::vector<int>> g(n); for (int i = 0; i < n; ++i) if (parent[i] >= 0) { g[i].push_back(parent[i]); g[parent[i]].push_back(i); } std::vector<int> c;
    for (int r = 0; r < n; ++r) { std::vector<char> seen(n, 0); seen[r] = 1; int worst = 0; for (int s : g[r]) { if (seen[s]) continue; int cnt = 0; std::vector<int> st = {s}; seen[s] = 1; while (!st.empty()) { int x = st.back(); st.pop_back(); ++cnt; for (int y : g[x]) if (!seen[y]) { seen[y] = 1; st.push_back(y); } } worst = std::max(worst, cnt); } if (2 * worst <= n) c.push_back(r); }
    return c;
}

int main() {
    std::mt19937 rng(41);
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 70), shape = (int)(rng() % 3); std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = shape == 0 ? (int)(rng() % i) : shape == 1 ? std::max(0, i - 1 - (int)(rng() % 2)) : (int)(rng() % std::min(i, 3));
        std::vector<int> perm(n); for (int i = 0; i < n; ++i) perm[i] = i; std::shuffle(perm.begin(), perm.end(), rng); std::vector<int> p(n, -1); for (int i = 0; i < n; ++i) p[perm[i]] = par[i] < 0 ? -1 : perm[par[i]];
        std::vector<int> order; std::vector<int> sz = subtreeSizes(p, order); int root = order[0]; std::vector<std::vector<int>> kids(n); for (int i = 0; i < n; ++i) if (p[i] >= 0) kids[p[i]].push_back(i);
        for (int u = 0; u < n; ++u) assert(sz[u] == countNaive(kids, u)); assert(sz[root] == n);                  // ①
        std::vector<int> tin = preorderNumbers(kids, root); for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v) { bool inRange = tin[u] <= tin[v] && tin[v] < tin[u] + sz[u]; bool climbs = false; for (int x = v; x >= 0; x = p[x]) if (x == u) climbs = true; assert(inRange == climbs); }          // ② 구간 성질
        long sumSize = 0, sumDepth = 0; for (int u = 0; u < n; ++u) { sumSize += sz[u]; int d = 0; for (int x = u; p[x] >= 0; x = p[x]) ++d; sumDepth += d + 1; } assert(sumSize == sumDepth);                                  // ③
        std::vector<int> c1 = centroidsBySizes(p, sz), c2 = centroidsBrute(p); assert(c1 == c2 && (c1.size() == 1 || c1.size() == 2));                                                                              // ④
    }
    { int n = 1000000; std::vector<int> chain(n, -1); for (int i = 1; i < n; ++i) chain[i] = i - 1; std::vector<int> order; std::vector<int> sz = subtreeSizes(chain, order); assert(sz[0] == n && sz[n - 1] == 1 && sz[n / 2] == n - n / 2);
      std::vector<int> c = centroidsBySizes(chain, sz); assert(c.size() == 2 && c[0] == n / 2 - 1 && c[1] == n / 2); std::cout << "Size: iterative subtree sizes matched recounting on 3000 random trees; the preorder-interval property held for every node pair; centroids from sizes matched brute-force deletion; a 10^6 chain was handled without recursion" << std::endl; }
    return 0;
}
// Time Complexity: O(n) (구간 성질 검사는 O(n²))
// Space Complexity: O(n)
```
## IsLeaf()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <vector>

// 리프(leaf): 자식이 없는 노드. 정의를 세 가지로 구현해 서로 대조한다.
//  ① 자식 목록이 비어 있음  ② 부모 배열에서 *누구의 부모로도 나오지 않음*  ③ 뿌리 없는 트리에서 이웃이 1 개 — 뿌리 있는 트리와의 관계: 뿌리 없는 리프 수 = 뿌리 있는 리프 수 + (루트의 자식이 1 개면 1) (루트가 리프로 보이므로), n = 1 은 예외.
//  ④ 동적 유지: 리프 추가·삭제가 일어날 때 리프 집합을 *증분 갱신*(부모가 리프에서 내부 노드로, 또는 그 반대)한 결과가 매번 처음부터 다시 계산한 것과 같다.   ⑤ 모든 리프가 같은 깊이면 완전(perfect) 트리일 수 있다 — 리프 깊이 집합으로 판정.
struct Dyn {
    std::vector<int> parent; std::vector<std::vector<int>> kids; std::vector<char> alive; std::set<int> leaves; int root = 0;                       // 증분 유지되는 leaves
    explicit Dyn(int cap) : parent(cap, -2), kids(cap), alive(cap, 0) { alive[0] = 1; parent[0] = -1; leaves.insert(0); }
    bool addLeaf(int p, int c) { if (!alive[p] || alive[c]) return false; if (kids[p].empty()) leaves.erase(p); parent[c] = p; alive[c] = 1; kids[p].push_back(c); leaves.insert(c); return true; }
    bool removeLeaf(int c) { if (!alive[c] || c == root || !kids[c].empty()) return false; int p = parent[c]; auto& v = kids[p]; v.erase(std::find(v.begin(), v.end(), c)); leaves.erase(c); alive[c] = 0; parent[c] = -2; if (v.empty()) leaves.insert(p); return true; }
    std::set<int> recompute() const { std::set<int> r; for (size_t i = 0; i < alive.size(); ++i) if (alive[i] && kids[i].empty()) r.insert((int)i); return r; }
};

int main() {
    std::mt19937 rng(46);
    for (int it = 0; it < 5000; ++it) {                                                                          // ①②③ 무작위 트리 (shape 3 = 무작위 *꽉 찬* 이진 트리: 리프 하나에 자식 둘을 반복해서 붙인다)
        int n = 1 + (int)(rng() % 60), shape = (int)(rng() % 4); std::vector<int> par(1, -1);
        if (shape == 3) { n |= 1; std::vector<int> leafList = {0}; while ((int)par.size() + 2 <= n) { size_t pick = rng() % leafList.size(); int u = leafList[pick]; leafList[pick] = leafList.back(); leafList.pop_back(); for (int k = 0; k < 2; ++k) { par.push_back(u); leafList.push_back((int)par.size() - 1); } } n = (int)par.size(); }
        else { par.assign(n, -1); for (int i = 1; i < n; ++i) par[i] = shape == 0 ? (int)(rng() % i) : shape == 1 ? std::max(0, i - 1 - (int)(rng() % 2)) : (int)(rng() % std::min(i, 3)); }
        std::vector<std::vector<int>> kids(n); std::vector<char> isParent(n, 0); std::vector<int> nb(n, 0); for (int i = 1; i < n; ++i) { kids[par[i]].push_back(i); isParent[par[i]] = 1; ++nb[i]; ++nb[par[i]]; }
        std::set<int> a, b, c; for (int u = 0; u < n; ++u) { if (kids[u].empty()) a.insert(u); if (!isParent[u]) b.insert(u); if (nb[u] == 1) c.insert(u); } assert(a == b);
        if (n >= 2) { std::set<int> expect = a; if (kids[0].size() == 1) expect.insert(0); else expect.erase(0); assert(c == expect); } else assert(a.size() == 1 && c.empty());                                // 뿌리 없는 리프 = 뿌리 있는 리프 + (루트가 자식 1 개면 루트)
        std::set<int> depths; for (int u : a) { int d = 0; for (int x = u; par[x] >= 0; x = par[x]) ++d; depths.insert(d); }                                    // ⑤ 리프 깊이 집합
        bool full = true; for (auto& k : kids) if (!k.empty() && k.size() != 2) full = false;
        if (full) { assert(a.size() == (size_t)(n + 1) / 2); if (depths.size() == 1) { int h = *depths.begin(); assert(n == (1 << (h + 1)) - 1 && a.size() == (size_t)1 << h); } }                               // 꽉 찬 이진 트리: 리프 (n+1)/2 개, 모든 리프가 같은 깊이면 완전(perfect) 트리
    }
    for (int h = 0; h <= 10; ++h) { int n = (1 << (h + 1)) - 1; std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = (i - 1) / 2; std::vector<char> isParent(n, 0); for (int i = 1; i < n; ++i) isParent[par[i]] = 1; std::set<int> depths; for (int u = 0; u < n; ++u) if (!isParent[u]) { int d = 0; for (int x = u; par[x] >= 0; x = par[x]) ++d; depths.insert(d); } assert(depths.size() == 1 && *depths.begin() == h); }      // 완전 이진 트리의 리프 깊이는 모두 h
    for (int round = 0; round < 200; ++round) {                                                                  // ④ 증분 유지 vs 재계산
        const int CAP = 40; Dyn t(CAP);
        for (int op = 0; op < 300; ++op) { int a = (int)(rng() % CAP), b = (int)(rng() % CAP); if (rng() % 3) t.addLeaf(a, b); else t.removeLeaf(b); assert(t.leaves == t.recompute() && !t.leaves.empty()); }                 // 비어 있지 않은 트리에는 리프가 있다
    }
    std::cout << "IsLeaf: three leaf definitions agreed on 5000 random trees (unrooted leaves = rooted leaves +/- the root), complete binary trees were recognised by leaf depths, and incremental leaf maintenance matched recomputation over 60000 operations" << std::endl;
    return 0;
}
// Time Complexity: 판정 O(1), 전체 리프 O(n), 증분 갱신 O(log n)
// Space Complexity: O(n)
```
## IsRoot()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 루트 판별: 부모가 없는 노드. 표현에 따라 관례가 다르다 — 트리 부모 배열은 parent[u] = −1, 분리 집합(union-find)은 parent[u] = u (자기 자신이 부모).  한 숲에서 루트는 연결 요소마다 하나.
//  ① 숲에서 간선을 무작위로 끊으면 루트 수 = 끊은 횟수 + 1 이고, 두 관례 사이의 변환이 가역.  ② union-find: 합칠 때 크기가 큰 쪽의 루트가 새 루트(크기 합), 경로 압축 후에도 find(x) 의 결과(= 루트)는 불변 — 브루트포스 연결 요소 라벨링과 대조.
//  ③ isRoot(x) ⇔ find(x) == x, 루트 수 = 연결 요소 수.  100 만 개 합치기도 반복문으로.
struct DSU {
    std::vector<int> p, sz; long compressions = 0; explicit DSU(int n) : p(n), sz(n, 1) { std::iota(p.begin(), p.end(), 0); }
    bool isRoot(int x) const { return p[x] == x; }
    int find(int x) { int r = x; while (p[r] != r) r = p[r]; while (p[x] != r) { int nx = p[x]; p[x] = r; x = nx; ++compressions; } return r; }                          // 반복 경로 압축
    int findNoCompress(int x) const { while (p[x] != x) x = p[x]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (sz[a] < sz[b]) std::swap(a, b); p[b] = a; sz[a] += sz[b]; return true; }
};
std::vector<int> toTreeConvention(const std::vector<int>& dsuParent) { std::vector<int> t(dsuParent.size()); for (size_t i = 0; i < t.size(); ++i) t[i] = dsuParent[i] == (int)i ? -1 : dsuParent[i]; return t; }
std::vector<int> toDsuConvention(const std::vector<int>& treeParent) { std::vector<int> d(treeParent.size()); for (size_t i = 0; i < d.size(); ++i) d[i] = treeParent[i] < 0 ? (int)i : treeParent[i]; return d; }
std::vector<int> componentLabels(int n, const std::vector<std::pair<int, int>>& edges) {                                  // 브루트포스: BFS 연결 요소
    std::vector<std::vector<int>> g(n); for (auto& e : edges) { g[e.first].push_back(e.second); g[e.second].push_back(e.first); } std::vector<int> lab(n, -1); int c = 0;
    for (int s = 0; s < n; ++s) if (lab[s] < 0) { std::vector<int> st = {s}; lab[s] = c; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : g[u]) if (lab[v] < 0) { lab[v] = c; st.push_back(v); } } ++c; }
    return lab;
}

int main() {
    std::mt19937 rng(52);
    for (int it = 0; it < 3000; ++it) {                                                                          // ① 간선 끊기: 루트 수 = 끊은 횟수 + 1
        int n = 1 + (int)(rng() % 60); std::vector<int> par(n, -1); for (int i = 1; i < n; ++i) par[i] = (int)(rng() % i); int cuts = n > 1 ? (int)(rng() % n) : 0; std::vector<int> cutNodes(n - 1 > 0 ? n - 1 : 0); std::iota(cutNodes.begin(), cutNodes.end(), 1); std::shuffle(cutNodes.begin(), cutNodes.end(), rng);
        for (int k = 0; k < cuts && k < (int)cutNodes.size(); ++k) par[cutNodes[k]] = -1; int roots = (int)std::count(par.begin(), par.end(), -1); assert(roots == std::min(cuts, n - 1) + 1);
        std::vector<int> d = toDsuConvention(par); assert(toTreeConvention(d) == par); int dsuRoots = 0; for (int i = 0; i < n; ++i) dsuRoots += d[i] == i; assert(dsuRoots == roots);                  // 변환 왕복, 루트 수 일치
    }
    for (int it = 0; it < 2000; ++it) {                                                                          // ② ③ 무작위 합치기
        int n = 1 + (int)(rng() % 50); DSU dsu(n); std::vector<std::pair<int, int>> edges; int merges = 0;
        for (int op = 0; op < 80; ++op) { int a = (int)(rng() % n), b = (int)(rng() % n); int ra = dsu.findNoCompress(a), rb = dsu.findNoCompress(b); long sa = dsu.sz[ra], sb = dsu.sz[rb]; bool joined = dsu.unite(a, b); assert(joined == (ra != rb)); edges.push_back({a, b});
            if (joined) { ++merges; int newRoot = dsu.findNoCompress(a); assert(newRoot == (sa >= sb ? ra : rb) && dsu.sz[newRoot] == sa + sb && dsu.isRoot(newRoot)); } }                                     // 큰 쪽의 루트가 새 루트
        std::vector<int> lab = componentLabels(n, edges); int comps = *std::max_element(lab.begin(), lab.end()) + 1; int roots = 0; for (int i = 0; i < n; ++i) roots += dsu.isRoot(i); assert(roots == comps && roots == n - merges);
        for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) assert((lab[i] == lab[j]) == (dsu.findNoCompress(i) == dsu.findNoCompress(j)));                                                       // 같은 요소 ⇔ 같은 루트
        std::vector<int> before(n); for (int i = 0; i < n; ++i) before[i] = dsu.findNoCompress(i); for (int i = 0; i < n; ++i) assert(dsu.find(i) == before[i]); for (int i = 0; i < n; ++i) assert(dsu.p[i] == before[i]);          // 경로 압축은 루트를 바꾸지 않고, 압축 뒤 모두 루트에 직접 연결
    }
    { const int n = 1000000; DSU dsu(n); for (int i = 1; i < n; ++i) dsu.unite(i - 1, i); int roots = 0; for (int i = 0; i < n; ++i) roots += dsu.isRoot(i); assert(roots == 1 && dsu.find(n - 1) == dsu.find(0) && dsu.sz[dsu.find(0)] == n);
      std::cout << "IsRoot: root counts matched component counts on 5000 random forests; size-based roots, path compression invariance and parent[-1]/parent[self] conversions verified; 10^6 unions were done iteratively" << std::endl; }
    return 0;
}
// Time Complexity: 판별 O(1) (트리 표현) / 분리 집합은 find 기준 거의 O(1) 분할상환
// Space Complexity: O(n)
```

# Part 2. 이진트리
## CreateBinaryTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

// 이진 트리를 만드는 방법들을 서로 변환하며 검증한다 (노드는 배열 풀: val/left/right 인덱스, 해제 문제 없음).
//  ① 모양의 개수: n 개의 노드를 가진 서로 다른 이진 트리는 카탈랑 수 C(n) — 모든 모양을 만들어(재귀 조합) 직렬화가 서로 다르고 개수가 C(n) 인지 확인 (n ≤ 9).
//  ② 직렬화 왕복: 레벨 순서 + null ("1,2,3,null,4") 문자열 ↔ 트리.  ③ 전위+중위 또는 후위+중위 순회열(값이 서로 다르면) 로부터 트리를 *유일하게* 복원 — 해시맵으로 O(n).  전위+후위만으로는 모호함(반례 확인).
//  ④ 힙 배열(완전 이진 트리)  ⑤ 무작위 트리에서 모든 표현이 같은 트리를 가리킴, 깊이 10^5 사슬도 반복문으로.
struct BT {
    std::vector<int> val, L, R; int root = -1;
    int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; }
    int size() const { return (int)val.size(); }
};
std::string serialize(const BT& t) {                                                                           // 레벨 순서 + null, 끝의 null 은 생략
    if (t.root < 0) return ""; std::vector<int> q = {t.root}; std::vector<std::string> out; for (size_t i = 0; i < q.size(); ++i) { int u = q[i]; if (u < 0) { out.push_back("null"); continue; } out.push_back(std::to_string(t.val[u])); q.push_back(t.L[u]); q.push_back(t.R[u]); }
    while (!out.empty() && out.back() == "null") out.pop_back(); std::string s; for (size_t i = 0; i < out.size(); ++i) { if (i) s += ','; s += out[i]; } return s;
}
BT deserialize(const std::string& s) {
    BT t; if (s.empty()) return t; std::vector<std::string> tok; std::stringstream ss(s); std::string x; while (std::getline(ss, x, ',')) tok.push_back(x);
    t.root = t.add(std::stoi(tok[0])); std::vector<int> q = {t.root}; size_t i = 1; for (size_t h = 0; h < q.size() && i < tok.size(); ++h) { int u = q[h];
        for (int side = 0; side < 2 && i < tok.size(); ++side, ++i) if (tok[i] != "null") { int c = t.add(std::stoi(tok[i])); (side == 0 ? t.L[u] : t.R[u]) = c; q.push_back(c); } }
    return t;
}
std::vector<int> preorder(const BT& t) { std::vector<int> out, st; if (t.root >= 0) st.push_back(t.root); while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(t.val[u]); if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } return out; }
std::vector<int> inorder(const BT& t) { std::vector<int> out, st; int u = t.root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = t.L[u]; } u = st.back(); st.pop_back(); out.push_back(t.val[u]); u = t.R[u]; } return out; }
std::vector<int> postorder(const BT& t) { std::vector<int> out; std::vector<int> st; if (t.root >= 0) st.push_back(t.root); while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(t.val[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); if (t.R[u] >= 0) st.push_back(t.R[u]); } std::reverse(out.begin(), out.end()); return out; }       // (루트, 오른쪽, 왼쪽) 의 역순
BT fromPreIn(const std::vector<int>& pre, const std::vector<int>& in) {                                       // 전위+중위 → 트리 (반복문: 재귀 없음)
    BT t; if (pre.empty()) return t; std::map<int, int> pos; for (size_t i = 0; i < in.size(); ++i) pos[in[i]] = (int)i;
    struct Job { int node, preLo, inLo, inHi; }; t.root = t.add(pre[0]); std::vector<Job> st = {{t.root, 0, 0, (int)in.size() - 1}};
    while (!st.empty()) { Job j = st.back(); st.pop_back(); int p = pos[t.val[j.node]]; int leftCount = p - j.inLo, rightCount = j.inHi - p;
        if (rightCount > 0) { int c = t.add(pre[j.preLo + leftCount + 1]); t.R[j.node] = c; st.push_back({c, j.preLo + leftCount + 1, p + 1, j.inHi}); }
        if (leftCount > 0) { int c = t.add(pre[j.preLo + 1]); t.L[j.node] = c; st.push_back({c, j.preLo + 1, j.inLo, p - 1}); } }
    return t;
}
BT fromPostIn(const std::vector<int>& post, const std::vector<int>& in) {
    BT t; if (post.empty()) return t; std::map<int, int> pos; for (size_t i = 0; i < in.size(); ++i) pos[in[i]] = (int)i;
    struct Job { int node, postHi, inLo, inHi; }; t.root = t.add(post.back()); std::vector<Job> st = {{t.root, (int)post.size() - 1, 0, (int)in.size() - 1}};
    while (!st.empty()) { Job j = st.back(); st.pop_back(); int p = pos[t.val[j.node]]; int leftCount = p - j.inLo, rightCount = j.inHi - p;
        if (rightCount > 0) { int c = t.add(post[j.postHi - 1]); t.R[j.node] = c; st.push_back({c, j.postHi - 1, p + 1, j.inHi}); }
        if (leftCount > 0) { int c = t.add(post[j.postHi - 1 - rightCount]); t.L[j.node] = c; st.push_back({c, j.postHi - 1 - rightCount, j.inLo, p - 1}); } }
    return t;
}
BT randomBT(int n, int shape, std::mt19937& rng) {                                                            // 값은 1..n 의 순열. shape 0: 무작위 빈 칸 붙이기, 1: 왼쪽 사슬 편향, 2: 오른쪽 편향
    BT t; std::vector<int> vals(n); std::iota(vals.begin(), vals.end(), 1); std::shuffle(vals.begin(), vals.end(), rng); std::vector<std::pair<int, int>> slots; t.root = t.add(vals[0]); slots.push_back({t.root, 0}); slots.push_back({t.root, 1});
    for (int i = 1; i < n; ++i) { size_t pick = shape == 0 ? rng() % slots.size() : (shape == 1 ? slots.size() - 1 - (rng() % 4 == 0 && slots.size() > 1 ? 1 : 0) : (rng() % 4 == 0 && slots.size() > 1 ? slots.size() - 2 : slots.size() - 1)); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(vals[i]); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); }
    return t;
}
void allShapes(int n, std::vector<std::string>& out) {                                                          // 모양만 (여는/닫는 괄호): n 개 노드의 모든 이진 트리
    if (n == 0) { out.push_back("."); return; }
    for (int l = 0; l < n; ++l) { std::vector<std::string> a, b; allShapes(l, a); allShapes(n - 1 - l, b); for (auto& x : a) for (auto& y : b) out.push_back("(" + x + y + ")"); }
}
BT heapArrayToTree(const std::vector<int>& a) { BT t; if (a.empty()) return t; std::vector<int> id(a.size()); for (size_t i = 0; i < a.size(); ++i) id[i] = t.add(a[i]); t.root = id[0]; for (size_t i = 0; i < a.size(); ++i) { if (2 * i + 1 < a.size()) t.L[id[i]] = id[2 * i + 1]; if (2 * i + 2 < a.size()) t.R[id[i]] = id[2 * i + 2]; } return t; }

int main() {
    { BT t = deserialize("1,2,3,null,4"); assert(serialize(t) == "1,2,3,null,4" && preorder(t) == (std::vector<int>{1, 2, 4, 3}) && inorder(t) == (std::vector<int>{2, 4, 1, 3}) && postorder(t) == (std::vector<int>{4, 2, 3, 1})); }
    long catalan = 1; for (int n = 0; n <= 9; ++n) { std::vector<std::string> shapes; allShapes(n, shapes); std::sort(shapes.begin(), shapes.end()); assert(std::unique(shapes.begin(), shapes.end()) == shapes.end() && (long)shapes.size() == catalan); catalan = catalan * 2 * (2 * n + 1) / (n + 2); }      // ① C(n)
    std::mt19937 rng(7);
    for (int it = 0; it < 5000; ++it) {
        int n = 1 + (int)(rng() % 60); BT t = randomBT(n, (int)(rng() % 3), rng); std::string s = serialize(t); BT back = deserialize(s); assert(serialize(back) == s && preorder(back) == preorder(t) && inorder(back) == inorder(t) && back.size() == n);               // ② 직렬화 왕복
        BT a = fromPreIn(preorder(t), inorder(t)), b = fromPostIn(postorder(t), inorder(t)); assert(serialize(a) == s && serialize(b) == s);                                                                                                    // ③ 유일한 복원
    }
    { BT x = deserialize("1,2"), y = deserialize("1,null,2"); assert(preorder(x) == preorder(y) && postorder(x) == postorder(y) && serialize(x) != serialize(y) && inorder(x) != inorder(y)); }                                                  // 전위+후위로는 구분 못 한다 (중위가 필요)
    for (int n = 0; n <= 100; ++n) { std::vector<int> a(n); std::iota(a.begin(), a.end(), 1); BT t = heapArrayToTree(a); std::vector<int> pre = preorder(t); assert((int)pre.size() == n); std::string s = serialize(t); std::stringstream ss(s); std::string tok; int i = 1; while (std::getline(ss, tok, ',')) assert(tok == std::to_string(i++)); assert(i == n + 1); }      // ④ 힙 배열의 레벨 순서 = 배열 순서
    { int n = 100000; BT chain; int cur = chain.root = chain.add(0); for (int i = 1; i < n; ++i) { int c = chain.add(i); chain.L[cur] = c; cur = c; } BT rebuilt = fromPreIn(preorder(chain), inorder(chain)); assert(rebuilt.size() == n && inorder(rebuilt).front() == n - 1 && preorder(rebuilt).front() == 0);
      std::cout << "CreateBinaryTree: all binary tree shapes for n <= 9 were enumerated (Catalan counts), 5000 random trees round-tripped through level-order text and unique pre/in and post/in reconstruction, and a 10^5-deep chain was rebuilt iteratively" << std::endl; }
    return 0;
}
// Time Complexity: 직렬화·복원 O(n) (순회열 복원은 값→위치 맵으로 O(n log n)), 모양 열거 O(C(n)·n)
// Space Complexity: O(n)
```
## InsertLeft()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <vector>

// 왼쪽 자식 삽입: 새 노드를 p 의 왼쪽에 붙인다. p 에 이미 왼쪽 자식이 있을 때의 정책이 중요하다 — ① 거부(false) ② *밀어내기*: 새 노드가 그 자리를 차지하고 기존 부분 트리는 새 노드의 왼쪽 자식이 된다(트리 크기 +1, 기존 구조 보존).
//  배열 풀(인덱스) 구현과 unique_ptr 기반 포인터 구현을 같은 무작위 삽입열로 돌려 *전위 괄호 직렬화*가 항상 같은지 대조한다. 불변식 — 크기 +1, 부모 링크 일치, 기존 노드들의 상대적 후손 관계 보존.
//  InsertRight 와의 대칭: 오른쪽 삽입 = 좌우를 뒤집고 왼쪽 삽입한 뒤 다시 뒤집은 것 (mirror(insertLeft(mirror(T))) == insertRight(T)).
struct Arena {
    std::vector<int> val, L, R, parent; int root = -1;
    int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); parent.push_back(-1); return (int)val.size() - 1; }
    bool insertLeft(int p, int v, bool push) {
        if (L[p] >= 0 && !push) return false; int c = add(v); parent[c] = p; if (L[p] >= 0) { L[c] = L[p]; parent[L[p]] = c; } L[p] = c; return true;
    }
    bool insertRight(int p, int v, bool push) { if (R[p] >= 0 && !push) return false; int c = add(v); parent[c] = p; if (R[p] >= 0) { R[c] = R[p]; parent[R[p]] = c; } R[p] = c; return true; }
    std::string paren(int u) const { if (u < 0) return "."; return "(" + std::to_string(val[u]) + paren(L[u]) + paren(R[u]) + ")"; }                     // 작은 트리용 재귀 직렬화
    bool linksOk() const { for (size_t i = 0; i < val.size(); ++i) { if (L[i] >= 0 && parent[L[i]] != (int)i) return false; if (R[i] >= 0 && parent[R[i]] != (int)i) return false; } return parent[root] == -1; }
    void mirror() { for (size_t i = 0; i < val.size(); ++i) std::swap(L[i], R[i]); }
};
struct PNode { int val; std::unique_ptr<PNode> left, right; explicit PNode(int v) : val(v) {} };                      // 독립 구현: 포인터 소유 트리
std::string paren(const PNode* u) { if (!u) return "."; return "(" + std::to_string(u->val) + paren(u->left.get()) + paren(u->right.get()) + ")"; }
PNode* findNode(PNode* u, int v) { if (!u) return nullptr; if (u->val == v) return u; if (PNode* a = findNode(u->left.get(), v)) return a; return findNode(u->right.get(), v); }
bool insertLeftP(PNode* root, int p, int v, bool push) { PNode* n = findNode(root, p); if (!n || (n->left && !push)) return false; std::unique_ptr<PNode> c(new PNode(v)); c->left = std::move(n->left); n->left = std::move(c); return true; }

int main() {
    std::mt19937 rng(11);
    for (int round = 0; round < 2000; ++round) {
        Arena a; a.root = a.add(0); std::unique_ptr<PNode> root(new PNode(0)); int next = 1; bool push = rng() % 2;
        for (int op = 0; op < 40; ++op) {
            int p = (int)(rng() % a.val.size()); int before = (int)a.val.size(); bool okA = a.insertLeft(p, next, push), okP = insertLeftP(root.get(), p, next, push); assert(okA == okP);          // 값 = 번호이므로 p 는 노드 번호이자 값
            if (okA) { ++next; assert((int)a.val.size() == before + 1); } else assert((int)a.val.size() == before);
            assert(a.linksOk() && a.paren(a.root) == paren(root.get()));
        }
    }
    // 밀어내기 정책: 기존 부분 트리의 구조(전위 순서)가 새 노드 밑으로 그대로 보존된다
    { Arena a; a.root = a.add(1); a.insertLeft(0, 2, false); a.insertLeft(1, 3, false); a.insertRight(1, 4, false); std::string before = a.paren(a.L[0]); a.insertLeft(0, 9, true); assert(a.paren(a.L[0]) == "(9" + before + ".)" && a.paren(a.root) == "(1(9" + before + ".)" + ".)" && !a.insertLeft(0, 5, false)); }
    for (int round = 0; round < 1000; ++round) {                                                               // 대칭: insertRight(T) == mirror(insertLeft(mirror(T)))
        Arena a; a.root = a.add(0); for (int i = 1; i < 25; ++i) { int p = (int)(rng() % a.val.size()); if (rng() % 2) a.insertLeft(p, i, true); else a.insertRight(p, i, true); }
        Arena viaMirror = a; viaMirror.mirror(); int p = (int)(rng() % a.val.size()); viaMirror.insertLeft(p, 99, true); viaMirror.mirror(); Arena direct = a; direct.insertRight(p, 99, true); assert(viaMirror.paren(viaMirror.root) == direct.paren(direct.root));
    }
    { Arena a; a.root = a.add(0); int cur = 0; for (int i = 1; i <= 1000000; ++i) { a.insertLeft(cur, i, false); cur = a.L[cur]; } assert(a.val.size() == 1000001 && a.linksOk());                       // 100 만 번 삽입 (직렬화는 하지 않는다)
      std::cout << "InsertLeft: arena and unique_ptr implementations produced identical trees over 80000 random insertions with both collision policies; right insertion equals mirrored left insertion; 10^6 insertions took O(1) each" << std::endl; }
    return 0;
}
// Time Complexity: O(1) (노드를 이미 알 때), 값으로 찾으면 O(n)
// Space Complexity: O(1) 추가 (노드 하나)
```
## InsertRight()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 오른쪽 자식 삽입: 새 노드를 p 의 오른쪽에 붙인다 (이미 있으면 새 노드가 자리를 차지하고 기존 부분 트리는 새 노드의 *오른쪽* 자식이 된다).
//  이 항목은 삽입이 *순서 구조를 어떻게 바꾸는지* 본다: 오른쪽 삽입(밀어내기)은 p 의 중위 순서 바로 뒤에 새 노드를 끼우는 효과를 가지며, 오른쪽 사슬 위에서는 연결 리스트의 "p 뒤에 삽입" 과 같다.
//  ① 중위 순회열 오라클: p 의 오른쪽 자식이 없으면 새 노드는 중위에서 p 바로 뒤, 있으면 p 바로 뒤(= 기존 오른쪽 부분 트리 앞)에 들어간다 — 모든 경우에 inorder(after) = inorder(before) 에 새 값을 p 바로 뒤에 끼운 것.
//  ② 전위 순회열 오라클: 전위 순서에서 새 노드는 p 의 왼쪽 부분 트리 바로 뒤(오른쪽 부분 트리 앞).  ③ 오른쪽 사슬 = 단일 연결 리스트(리스트 insertAfter 와 일치).  ④ 중복 값 없는 트리에서 모든 삽입 뒤 트리가 유효(크기 +1, 사이클 없음).
struct BT {
    std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; }
    bool insertRight(int p, int v, bool push) { if (R[p] >= 0 && !push) return false; int c = add(v); R[c] = R[p]; R[p] = c; return true; }
    bool insertLeft(int p, int v, bool push) { if (L[p] >= 0 && !push) return false; int c = add(v); L[c] = L[p]; L[p] = c; return true; }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(val[u]); u = R[u]; } return out; }
    std::vector<int> preorder() const { std::vector<int> out, st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(val[u]); if (R[u] >= 0) st.push_back(R[u]); if (L[u] >= 0) st.push_back(L[u]); } return out; }
    bool valid() const { std::vector<char> seen(val.size(), 0); std::vector<int> st = {root}; size_t cnt = 0; while (!st.empty()) { int u = st.back(); st.pop_back(); if (seen[u]) return false; seen[u] = 1; ++cnt; if (L[u] >= 0) st.push_back(L[u]); if (R[u] >= 0) st.push_back(R[u]); } return cnt == val.size(); }
};
std::vector<int> preorderSubtree(const BT& t, int u) { std::vector<int> out, st = {u}; while (!st.empty()) { int x = st.back(); st.pop_back(); out.push_back(t.val[x]); if (t.R[x] >= 0) st.push_back(t.R[x]); if (t.L[x] >= 0) st.push_back(t.L[x]); } return out; }

int main() {
    std::mt19937 rng(17);
    for (int round = 0; round < 2000; ++round) {
        BT t; t.root = t.add(0); for (int i = 1; i < 20; ++i) { int p = (int)(rng() % t.val.size()); if (rng() % 2) t.insertLeft(p, i, true); else t.insertRight(p, i, true); }
        for (int op = 0; op < 10; ++op) {
            int p = (int)(rng() % t.val.size()), v = 100 + op; std::vector<int> in = t.inorder(), pre = t.preorder(); bool had = t.R[p] >= 0; bool ok = t.insertRight(p, v, true); assert(ok && t.valid());
            std::vector<int> wantIn = in; wantIn.insert(std::find(wantIn.begin(), wantIn.end(), t.val[p]) + 1, v); assert(t.inorder() == wantIn);                          // ① 중위: p 바로 뒤
            // ② 전위: p 의 왼쪽 부분 트리 바로 뒤(오른쪽 부분 트리 앞)
            std::vector<int> wantPre = pre; int posP = (int)(std::find(wantPre.begin(), wantPre.end(), t.val[p]) - wantPre.begin()); size_t leftSize = t.L[p] >= 0 ? preorderSubtree(t, t.L[p]).size() : 0; wantPre.insert(wantPre.begin() + posP + 1 + (long)leftSize, v); assert(t.preorder() == wantPre);
            (void)had;
        }
    }
    // ③ 오른쪽 사슬 = 단일 연결 리스트 insertAfter
    for (int round = 0; round < 500; ++round) { BT t; t.root = t.add(0); std::vector<int> list = {0}; for (int i = 1; i < 60; ++i) { int pos = (int)(rng() % list.size()); int node = -1; for (size_t k = 0; k < t.val.size(); ++k) if (t.val[k] == list[pos]) node = (int)k; t.insertRight(node, i, true); list.insert(list.begin() + pos + 1, i); }
        std::vector<int> walk; for (int u = t.root; u >= 0; u = t.R[u]) walk.push_back(t.val[u]); assert(walk == list && t.valid()); }
    // 거부 정책(push=false)
    { BT t; t.root = t.add(1); assert(t.insertRight(0, 2, false) && !t.insertRight(0, 3, false) && t.val.size() == 2 && t.valid()); }
    { BT t; t.root = t.add(0); int cur = 0; for (int i = 1; i <= 1000000; ++i) { t.insertRight(cur, i, false); cur = t.R[cur]; } assert(t.val.size() == 1000001 && t.valid());
      std::cout << "InsertRight: after every insertion the in-order sequence gained the new value right after its parent and the pre-order sequence gained it after the parent's left subtree (20000 checked insertions); the right spine behaved as a singly linked list; 10^6 appends were O(1)" << std::endl; }
    return 0;
}
// Time Complexity: O(1) (노드를 알 때)
// Space Complexity: O(1) 추가
```
## DeleteNode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <string>
#include <vector>

// 이진 트리(정렬되지 않은)에서 노드 삭제: 구조를 깨지 않으려면 *가장 깊은(레벨 순서의 마지막) 노드*의 값으로 대상 값을 덮어쓰고 그 마지막 노드를 떼어 낸다 — 모양이 유지되고 O(n).
//  (이진 탐색 트리의 삭제는 Part 5 DeleteBST 참고: 후계자로 대체)  구현 두 가지를 대조: ① 제자리(BFS 로 마지막 노드와 그 부모를 찾아 값 덮어쓰기 + 링크 끊기) ② 복사본을 재귀로 새로 만드는 함수형 구현.
//  검증: 값의 다중집합에서 정확히 하나가 줄어듦, 크기 −1, 트리 유효, 나머지 구조는 그대로(= 함수형 구현과 직렬화가 같음), 없는 값이면 변화 없음, 루트만 있는 트리의 삭제, 풀 재사용(해제된 칸 재활용)으로 100 만 번 반복해도 풀 크기가 늘지 않음.
struct BT {
    std::vector<int> val, L, R, freeList; int root = -1; int cnt = 0;
    int add(int v) { ++cnt; if (!freeList.empty()) { int i = freeList.back(); freeList.pop_back(); val[i] = v; L[i] = R[i] = -1; return i; } val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; }
    bool erase(int target) {                                                                                  // 값이 target 인 노드 하나를 삭제 (BFS 순서에서 처음 만난 것)
        if (root < 0) return false; std::vector<int> q = {root}, par = {-1}; int hit = -1; for (size_t i = 0; i < q.size(); ++i) { int u = q[i]; if (val[u] == target && hit < 0) hit = (int)i; if (L[u] >= 0) { q.push_back(L[u]); par.push_back(u); } if (R[u] >= 0) { q.push_back(R[u]); par.push_back(u); } }
        if (hit < 0) return false; int last = q.back(), lastParent = par.back(); val[q[hit]] = val[last];                                  // 마지막 노드의 값으로 덮어쓴 뒤
        if (lastParent < 0) root = -1; else if (R[lastParent] == last) R[lastParent] = -1; else L[lastParent] = -1; freeList.push_back(last); --cnt; return true;                         // 마지막 노드를 떼어 낸다
    }
    std::string paren() const { return parenRec(root); }                                                       // 작은 트리용 재귀 직렬화
    std::string parenRec(int u) const { if (u < 0) return "."; return "(" + std::to_string(val[u]) + parenRec(L[u]) + parenRec(R[u]) + ")"; }
    std::vector<int> values() const { std::vector<int> out, st; if (root >= 0) st.push_back(root); while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(val[u]); if (L[u] >= 0) st.push_back(L[u]); if (R[u] >= 0) st.push_back(R[u]); } std::sort(out.begin(), out.end()); return out; }
};
struct PNode { int val; std::unique_ptr<PNode> l, r; explicit PNode(int v) : val(v) {} };
std::unique_ptr<PNode> fromArena(const BT& t, int u) { if (u < 0) return nullptr; std::unique_ptr<PNode> n(new PNode(t.val[u])); n->l = fromArena(t, t.L[u]); n->r = fromArena(t, t.R[u]); return n; }
std::string paren(const PNode* u) { if (!u) return "."; return "(" + std::to_string(u->val) + paren(u->l.get()) + paren(u->r.get()) + ")"; }
const PNode* findFirstBfs(const PNode* root, int v) { std::vector<const PNode*> q = {root}; for (size_t i = 0; i < q.size(); ++i) { if (q[i]->val == v) return q[i]; if (q[i]->l) q.push_back(q[i]->l.get()); if (q[i]->r) q.push_back(q[i]->r.get()); } return nullptr; }
const PNode* lastBfs(const PNode* root) { std::vector<const PNode*> q = {root}; for (size_t i = 0; i < q.size(); ++i) { if (q[i]->l) q.push_back(q[i]->l.get()); if (q[i]->r) q.push_back(q[i]->r.get()); } return q.back(); }
std::unique_ptr<PNode> without(const PNode* u, const PNode* hit, const PNode* last, int newVal) {                    // 함수형: 복사하며 last 를 건너뛰고 hit 의 값을 바꾼다
    if (!u || u == last) return nullptr; std::unique_ptr<PNode> n(new PNode(u == hit ? newVal : u->val)); n->l = without(u->l.get(), hit, last, newVal); n->r = without(u->r.get(), hit, last, newVal); return n;
}

int main() {
    std::mt19937 rng(23);
    for (int it = 0; it < 5000; ++it) {
        BT t; int n = 1 + (int)(rng() % 30); std::vector<std::pair<int, int>> slots; t.root = t.add((int)(rng() % 10)); slots.push_back({t.root, 0}); slots.push_back({t.root, 1});
        for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add((int)(rng() % 10)); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); }     // 값이 겹칠 수 있다 (0..9)
        int target = (int)(rng() % 12); std::vector<int> before = t.values(); std::unique_ptr<PNode> p = fromArena(t, t.root); const PNode* hit = findFirstBfs(p.get(), target); const PNode* last = lastBfs(p.get());
        std::string expect; if (hit) expect = last == p.get() ? "." : paren(without(p.get(), hit, last, last->val).get()); bool ok = t.erase(target);
        assert(ok == (hit != nullptr)); if (!ok) { assert(t.values() == before); continue; }
        std::vector<int> expectVals = before; expectVals.erase(std::find(expectVals.begin(), expectVals.end(), target)); assert(t.values() == expectVals && t.cnt == (int)before.size() - 1);                                // 다중집합에서 target 하나가 빠졌다
        assert((t.root < 0 ? std::string(".") : t.paren()) == expect);                                                                                               // 함수형 구현과 같은 트리
    }
    // 풀 재사용: 하나 넣고 하나 지우기를 100 만 번 → 풀 크기 상수
    { BT t; t.root = t.add(1); size_t poolMax = 0; for (int i = 0; i < 1000000; ++i) { int c = t.add(i); t.R[t.root] = c; bool erased = t.erase(i); assert(erased); (void)erased; poolMax = std::max(poolMax, t.val.size()); } assert(poolMax <= 3 && t.cnt == 1);
      BT one; one.root = one.add(5); bool e1 = one.erase(5), e2 = one.erase(5); assert(e1 && !e2 && one.root < 0 && one.cnt == 0);
      std::cout << "DeleteNode: in-place deepest-node replacement matched a copying functional implementation (shape and multiset) over 5000 random trees with duplicate values; the node pool stayed at " << poolMax << " slots across 10^6 insert/delete pairs" << std::endl; }
    return 0;
}
// Time Complexity: O(n) (BFS 로 대상과 마지막 노드를 찾는다)
// Space Complexity: O(n) (BFS 큐)
```
## CopyTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <deque>
#include <iostream>
#include <memory>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 트리 복사: ① 깊은 복사(deep copy) — 모든 노드를 새로 만든다. 재귀 구현은 사슬 모양에서 호출 스택이 깊어지므로 명시적 스택으로 반복한다.  ② 경로 복사(path copying) — 값 하나를 바꿀 때 루트에서 그 노드까지의 경로(깊이 + 1 개)만 새로 만들고 나머지는 *공유*하는 영속(persistent) 복사.
//  검증: 구조 동일(반복 비교), 복사본을 고쳐도 원본이 변하지 않음(독립), 새로 만든 노드 수 = n (깊은 복사) / 깊이 + 1 (경로 복사), 이전 버전은 영구히 그대로, 공유된 노드 수 = n − (깊이 + 1), 깊이 10^6 사슬도 반복문으로.
struct Node { int val; Node *left = nullptr, *right = nullptr; explicit Node(int v) : val(v) {} };
struct Pool { std::deque<Node> nodes; Node* make(int v) { nodes.emplace_back(v); return &nodes.back(); } };            // deque: 주소가 변하지 않고, 풀이 사라지면 모든 노드가 한꺼번에 해제 (누수 없음)
Node* deepCopy(const Node* root, Pool& dst) {
    if (!root) return nullptr; Node* newRoot = dst.make(root->val); std::vector<std::pair<const Node*, Node*>> st = {{root, newRoot}};
    while (!st.empty()) { auto cur = st.back(); st.pop_back(); if (cur.first->left) { cur.second->left = dst.make(cur.first->left->val); st.push_back({cur.first->left, cur.second->left}); } if (cur.first->right) { cur.second->right = dst.make(cur.first->right->val); st.push_back({cur.first->right, cur.second->right}); } }
    return newRoot;
}
Node* copyRecursive(const Node* n, Pool& dst) { if (!n) return nullptr; Node* c = dst.make(n->val); c->left = copyRecursive(n->left, dst); c->right = copyRecursive(n->right, dst); return c; }
bool sameShapeAndValues(const Node* a, const Node* b) { std::vector<std::pair<const Node*, const Node*>> st = {{a, b}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); if (!p.first || !p.second) { if (p.first != p.second) return false; continue; } if (p.first->val != p.second->val) return false; st.push_back({p.first->left, p.second->left}); st.push_back({p.first->right, p.second->right}); } return true; }
size_t countNodes(const Node* r) { size_t c = 0; std::vector<const Node*> st; if (r) st.push_back(r); while (!st.empty()) { const Node* u = st.back(); st.pop_back(); ++c; if (u->left) st.push_back(u->left); if (u->right) st.push_back(u->right); } return c; }
Node* pathCopyUpdate(Node* root, const std::vector<int>& path, int newVal, Pool& dst) {                              // path: 0 = 왼쪽, 1 = 오른쪽. 루트→대상 경로의 노드만 새로 만든다
    Node* newRoot = dst.make(root->val); newRoot->left = root->left; newRoot->right = root->right; Node* cur = newRoot, *orig = root;
    for (int dir : path) { Node* child = dir == 0 ? orig->left : orig->right; Node* copy = dst.make(child->val); copy->left = child->left; copy->right = child->right; (dir == 0 ? cur->left : cur->right) = copy; cur = copy; orig = child; }
    cur->val = newVal; return newRoot;
}
Node* randomTree(int n, Pool& pool, std::mt19937& rng) { Node* root = pool.make((int)(rng() % 1000)); std::vector<Node**> slots = {&root->left, &root->right}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); Node** s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); *s = pool.make((int)(rng() % 1000)); slots.push_back(&(*s)->left); slots.push_back(&(*s)->right); } return root; }

int main() {
    std::mt19937 rng(5);
    for (int it = 0; it < 3000; ++it) {
        Pool src, d1, d2; int n = 1 + (int)(rng() % 60); Node* root = randomTree(n, src, rng); Node* c1 = deepCopy(root, d1); Node* c2 = copyRecursive(root, d2);
        assert(sameShapeAndValues(root, c1) && sameShapeAndValues(c1, c2) && d1.nodes.size() == (size_t)n && d2.nodes.size() == (size_t)n && countNodes(c1) == (size_t)n);                        // 구조 동일, 새 노드 n 개
        std::set<const Node*> orig; for (auto& x : src.nodes) orig.insert(&x); for (auto& x : d1.nodes) assert(!orig.count(&x));                                                        // 원본 노드를 하나도 공유하지 않는다
        c1->val += 1000; if (c1->left) c1->left->val += 1000; assert(!sameShapeAndValues(root, c1) && sameShapeAndValues(root, c2));                                                         // 독립: 복사본을 고쳐도 원본·다른 복사본은 그대로
        // 경로 복사
        std::vector<int> path; Node* cur = root; while ((cur->left || cur->right) && rng() % 4) { int dir = cur->left && cur->right ? (int)(rng() % 2) : (cur->left ? 0 : 1); path.push_back(dir); cur = dir == 0 ? cur->left : cur->right; }
        Pool v2; Node* newRoot = pathCopyUpdate(root, path, -5, v2); assert(v2.nodes.size() == path.size() + 1 && newRoot != root);
        Pool snapshot; Node* before = deepCopy(root, snapshot); assert(sameShapeAndValues(root, before));                                                                                       // 이전 버전은 그대로
        Node* t = newRoot; for (int dir : path) t = dir == 0 ? t->left : t->right; assert(t->val == -5);
        std::set<const Node*> newNodes; for (auto& x : v2.nodes) newNodes.insert(&x); size_t shared = 0, total = 0; { std::vector<const Node*> st = {newRoot}; while (!st.empty()) { const Node* u = st.back(); st.pop_back(); ++total; if (!newNodes.count(u)) { ++shared; } if (u->left) st.push_back(u->left); if (u->right) st.push_back(u->right); } }
        assert(total == (size_t)n && shared + path.size() + 1 == (size_t)n);                                                                                                 // 전체 n 개 중 공유 = n − (깊이 + 1)
    }
    { const int n = 1000000; Pool src, dst; Node* root = src.make(0); Node* cur = root; for (int i = 1; i < n; ++i) { cur->left = src.make(i); cur = cur->left; } Node* copy = deepCopy(root, dst); assert(sameShapeAndValues(root, copy) && dst.nodes.size() == (size_t)n && countNodes(copy) == (size_t)n);
      std::vector<int> path(n - 1, 0); Pool v2; Node* nr = pathCopyUpdate(root, path, -1, v2); assert(v2.nodes.size() == (size_t)n);                                                               // 가장 깊은 노드를 바꾸면 경로 복사도 n 개
      std::vector<int> shortPath(10, 0); Pool v3; pathCopyUpdate(root, shortPath, -1, v3); assert(v3.nodes.size() == 11 && nr != root);
      std::cout << "CopyTree: iterative deep copy matched the recursive one on 3000 random trees (no shared nodes, independent mutation); path copying created exactly depth+1 nodes and shared the rest; a depth-10^6 chain was copied without recursion" << std::endl; }
    return 0;
}
// Time Complexity: 깊은 복사 O(n), 경로 복사 O(깊이)
// Space Complexity: O(n) 새 노드 (경로 복사는 O(깊이)), 명시적 스택 O(h)
```
## MirrorTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

// 좌우 반전(mirror): 모든 노드에서 왼쪽과 오른쪽 자식을 맞바꾼다 — 노드마다 독립이므로 *순서와 상관없이* 어떤 순회로 해도(또는 배열 풀을 그냥 훑어도) 같은 결과.
//  성질: ① 두 번 하면 원래대로(involution) ② 반전한 트리의 중위 순회 = 원래의 역순, 전위 = (루트, 오른쪽, 왼쪽) 순서 전위, 높이·레벨별 너비 불변 ③ 대칭 트리(T = mirror(T)): 전위 쌍 스택 판정 vs 반전 후 비교,
//  n 개 노드의 대칭 이진 트리의 수 = C((n−1)/2) (n 홀수) / 0 (n 짝수) — 모든 모양을 열거해 센다.  ④ 깊이 10^6 사슬을 반복문으로.
struct BT {
    std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; }
    void mirrorEach() { for (size_t i = 0; i < val.size(); ++i) std::swap(L[i], R[i]); }                                         // 풀을 훑으며
    void mirrorBfs() { std::vector<int> q = {root}; for (size_t i = 0; i < q.size(); ++i) { int u = q[i]; std::swap(L[u], R[u]); if (L[u] >= 0) q.push_back(L[u]); if (R[u] >= 0) q.push_back(R[u]); } }       // 트리를 따라가며
};
std::vector<int> inorder(const BT& t) { std::vector<int> out, st; int u = t.root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = t.L[u]; } u = st.back(); st.pop_back(); out.push_back(t.val[u]); u = t.R[u]; } return out; }
std::vector<int> preorder(const BT& t, bool rightFirst) { std::vector<int> out, st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(t.val[u]); int a = rightFirst ? t.L[u] : t.R[u], b = rightFirst ? t.R[u] : t.L[u]; if (a >= 0) st.push_back(a); if (b >= 0) st.push_back(b); } return out; }        // rightFirst: 오른쪽을 먼저 방문
std::vector<int> levelWidths(const BT& t) { std::vector<int> w; std::vector<int> cur = {t.root}; while (!cur.empty()) { w.push_back((int)cur.size()); std::vector<int> next; for (int u : cur) { if (t.L[u] >= 0) next.push_back(t.L[u]); if (t.R[u] >= 0) next.push_back(t.R[u]); } cur.swap(next); } return w; }
int height(const BT& t) { return (int)levelWidths(t).size() - 1; }
bool isSymmetric(const BT& t) { std::vector<std::pair<int, int>> st = {{t.L[t.root], t.R[t.root]}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); if (p.first < 0 || p.second < 0) { if (p.first != p.second) return false; continue; } if (t.val[p.first] != t.val[p.second]) return false; st.push_back({t.L[p.first], t.R[p.second]}); st.push_back({t.R[p.first], t.L[p.second]}); } return true; }      // 안쪽끼리, 바깥쪽끼리 짝지어 비교
bool equalTrees(const BT& a, const BT& b) { std::vector<std::pair<int, int>> st = {{a.root, b.root}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); if (p.first < 0 || p.second < 0) { if (p.first != p.second) return false; continue; } if (a.val[p.first] != b.val[p.second]) return false; st.push_back({a.L[p.first], b.L[p.second]}); st.push_back({a.R[p.first], b.R[p.second]}); } return true; }
BT randomBT(int n, std::mt19937& rng, bool symmetricValues) { BT t; t.root = t.add(symmetricValues ? 7 : (int)(rng() % 20)); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(symmetricValues ? 7 : (int)(rng() % 20)); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
void shapes(int n, std::vector<BT>& out) {                                                                     // n 개 노드의 모든 이진 트리 모양 (값은 모두 같음: 모양만 본다)
    if (n == 0) { out.emplace_back(); return; }
    for (int l = 0; l < n; ++l) { std::vector<BT> a, b; shapes(l, a); shapes(n - 1 - l, b);
        for (auto& x : a) for (auto& y : b) { BT t; t.root = t.add(1); std::vector<int> mapX(x.val.size()), mapY(y.val.size()); for (size_t i = 0; i < x.val.size(); ++i) mapX[i] = t.add(1); for (size_t i = 0; i < y.val.size(); ++i) mapY[i] = t.add(1);
            for (size_t i = 0; i < x.val.size(); ++i) { t.L[mapX[i]] = x.L[i] >= 0 ? mapX[x.L[i]] : -1; t.R[mapX[i]] = x.R[i] >= 0 ? mapX[x.R[i]] : -1; } for (size_t i = 0; i < y.val.size(); ++i) { t.L[mapY[i]] = y.L[i] >= 0 ? mapY[y.L[i]] : -1; t.R[mapY[i]] = y.R[i] >= 0 ? mapY[y.R[i]] : -1; }
            if (x.root >= 0) t.L[t.root] = mapX[x.root]; if (y.root >= 0) t.R[t.root] = mapY[y.root]; out.push_back(t); } }
}

int main() {
    std::mt19937 rng(9);
    for (int it = 0; it < 4000; ++it) {
        BT t = randomBT(1 + (int)(rng() % 60), rng, false); BT a = t, b = t, c = t; a.mirrorEach(); b.mirrorBfs(); assert(equalTrees(a, b));                                          // 순서와 무관
        std::vector<int> in = inorder(t), pre = preorder(t, false), preRev = preorder(t, true); std::reverse(in.begin(), in.end()); assert(inorder(a) == in && preorder(a, false) == preRev && preorder(a, true) == pre);          // ②
        std::vector<int> w = levelWidths(t); assert(levelWidths(a) == w && height(a) == height(t)); a.mirrorEach(); assert(equalTrees(a, t));                                                                              // 폭·높이 불변, 두 번이면 원래대로
        BT m = t; m.mirrorEach(); assert(isSymmetric(t) == equalTrees(t, m));                                                                                                                                          // ③ 대칭 판정 두 방법
    }
    for (int n = 1; n <= 9; ++n) { std::vector<BT> all; shapes(n, all); long sym = 0; for (auto& t : all) { BT m = t; m.mirrorEach(); bool s1 = isSymmetric(t), s2 = equalTrees(t, m); assert(s1 == s2); sym += s1; }
        long catalan[] = {1, 1, 2, 5, 14, 42}; long expect = n % 2 == 1 ? catalan[(n - 1) / 2] : 0; assert(sym == expect); }                                                                                            // 대칭 모양 수
    { BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < 1000000; ++i) { int c = t.add(i); t.L[cur] = c; cur = c; } t.mirrorBfs(); assert(t.R[t.root] >= 0 && t.L[t.root] < 0 && !isSymmetric(t)); t.mirrorEach(); assert(t.L[t.root] >= 0 && t.R[t.root] < 0);
      std::cout << "MirrorTree: mirroring by pool sweep and by BFS gave identical trees; in-order reversed, pre-order became right-first, widths/height were invariant, double mirroring was the identity; symmetric shape counts matched Catalan numbers for n <= 9; a depth-10^6 chain was mirrored iteratively" << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: 풀을 훑으면 O(1) 추가, BFS 는 O(너비)
```
## MergeTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <string>
#include <vector>

// 두 이진 트리를 *같은 위치끼리* 합치기 (값은 더한다): 한쪽에만 있는 부분 트리는 그대로 가져온다. 오라클은 "위치 → 값" 맵이다 — 루트에서의 경로 문자열("", "L", "LR", …)을 키로 하여 합친 트리의 맵은 두 맵의 합집합이고 겹치는 위치는 값의 합.
//  ① 반복문으로 구현한 *파괴적*(첫 트리를 재사용) 합치기와 *함수형*(새 트리) 합치기가 모두 오라클과 같다.  ② 교환·결합 법칙(값과 모양), 빈 트리가 항등원, 노드 수 = 두 위치 집합의 합집합 크기.
//  ③ 자기 자신과 합치면 모든 값이 두 배.  ④ 깊이 10^6 사슬 둘을 합쳐도 스택이 터지지 않는다.
struct Node { int val; Node *l = nullptr, *r = nullptr; explicit Node(int v) : val(v) {} };
struct Pool { std::vector<std::unique_ptr<Node>> nodes; Node* make(int v) { nodes.emplace_back(new Node(v)); return nodes.back().get(); } };
Node* mergeInPlace(Node* a, Node* b) {                                                                          // a 를 재사용하고 b 에만 있는 부분 트리는 그대로 붙인다
    if (!a) return b; if (!b) return a; std::vector<std::pair<Node*, Node*>> st = {{a, b}};
    while (!st.empty()) { auto p = st.back(); st.pop_back(); p.first->val += p.second->val; if (p.first->l && p.second->l) st.push_back({p.first->l, p.second->l}); else if (!p.first->l) p.first->l = p.second->l; if (p.first->r && p.second->r) st.push_back({p.first->r, p.second->r}); else if (!p.first->r) p.first->r = p.second->r; }
    return a;
}
Node* mergeFunctional(const Node* a, const Node* b, Pool& out) {                                               // 새 노드로 복사하며 합친다
    if (!a && !b) return nullptr; struct Job { const Node* a; const Node* b; Node* dst; }; Node* root = out.make((a ? a->val : 0) + (b ? b->val : 0)); std::vector<Job> st = {{a, b, root}};
    while (!st.empty()) { Job j = st.back(); st.pop_back(); const Node* al = j.a ? j.a->l : nullptr; const Node* bl = j.b ? j.b->l : nullptr; const Node* ar = j.a ? j.a->r : nullptr; const Node* br = j.b ? j.b->r : nullptr;
        if (al || bl) { j.dst->l = out.make((al ? al->val : 0) + (bl ? bl->val : 0)); st.push_back({al, bl, j.dst->l}); } if (ar || br) { j.dst->r = out.make((ar ? ar->val : 0) + (br ? br->val : 0)); st.push_back({ar, br, j.dst->r}); } }
    return root;
}
std::map<std::string, int> toMap(const Node* root) { std::map<std::string, int> m; std::vector<std::pair<const Node*, std::string>> st; if (root) st.push_back({root, ""}); while (!st.empty()) { auto p = st.back(); st.pop_back(); m[p.second] = p.first->val; if (p.first->l) st.push_back({p.first->l, p.second + "L"}); if (p.first->r) st.push_back({p.first->r, p.second + "R"}); } return m; }
std::map<std::string, int> mergeMaps(const std::map<std::string, int>& a, const std::map<std::string, int>& b) { std::map<std::string, int> r = a; for (auto& kv : b) r[kv.first] += kv.second; return r; }
Node* randomTree(int n, Pool& pool, std::mt19937& rng) { if (n == 0) return nullptr; Node* root = pool.make((int)(rng() % 10)); std::vector<Node**> slots = {&root->l, &root->r}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); Node** s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); *s = pool.make((int)(rng() % 10)); slots.push_back(&(*s)->l); slots.push_back(&(*s)->r); } return root; }
Node* cloneTree(const Node* root, Pool& pool) { if (!root) return nullptr; Node* nr = pool.make(root->val); std::vector<std::pair<const Node*, Node*>> st = {{root, nr}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); if (p.first->l) { p.second->l = pool.make(p.first->l->val); st.push_back({p.first->l, p.second->l}); } if (p.first->r) { p.second->r = pool.make(p.first->r->val); st.push_back({p.first->r, p.second->r}); } } return nr; }

int main() {
    std::mt19937 rng(12);
    for (int it = 0; it < 4000; ++it) {
        Pool pa, pb, pc, out1, out2, out3, copyA, copyB; int na = (int)(rng() % 25), nb = (int)(rng() % 25), nc = (int)(rng() % 25); Node* a = randomTree(na, pa, rng); Node* b = randomTree(nb, pb, rng); Node* c = randomTree(nc, pc, rng);
        std::map<std::string, int> ma = toMap(a), mb = toMap(b), mc = toMap(c), want = mergeMaps(ma, mb);
        Node* f = mergeFunctional(a, b, out1); assert(toMap(f) == want && toMap(a) == ma && toMap(b) == mb);                                                              // ① 함수형: 입력은 그대로
        Node* ca = cloneTree(a, copyA); Node* cb = cloneTree(b, copyB); Node* m = mergeInPlace(ca, cb); assert(toMap(m) == want);                                          // 파괴적
        assert(toMap(mergeFunctional(b, a, out2)) == want);                                                                                                                // ② 교환
        std::map<std::string, int> left = toMap(mergeFunctional(mergeFunctional(a, b, out2), c, out3)), right = mergeMaps(mergeMaps(ma, mb), mc); assert(left == right);   // 결합 (두 번 합친 결과의 맵)
        assert(toMap(mergeFunctional(a, nullptr, out3)) == ma && toMap(mergeFunctional(nullptr, a, out3)) == ma);                                                          // 빈 트리가 항등원
        std::map<std::string, int> keys; for (auto& kv : ma) keys[kv.first]; for (auto& kv : mb) keys[kv.first]; assert(want.size() == keys.size());                      // 노드 수 = 위치 집합의 합집합
        std::map<std::string, int> twice = toMap(mergeFunctional(a, a, out3)); for (auto& kv : ma) assert(twice[kv.first] == 2 * kv.second);                                // ③ 자기 자신과: 두 배
    }
    { const int n = 1000000; Pool p1, p2, out; Node* a = p1.make(1); Node* cur = a; for (int i = 1; i < n; ++i) { cur->l = p1.make(1); cur = cur->l; } Node* b = p2.make(2); cur = b; for (int i = 1; i < n / 2; ++i) { cur->r = p2.make(2); cur = cur->r; }
      Node* m = mergeFunctional(a, b, out); size_t cnt = 0; long sum = 0; { std::vector<const Node*> st = {m}; while (!st.empty()) { const Node* u = st.back(); st.pop_back(); ++cnt; sum += u->val; if (u->l) st.push_back(u->l); if (u->r) st.push_back(u->r); } } assert(cnt == (size_t)n + n / 2 - 1 && sum == (long)n * 1 + (long)(n / 2) * 2);
      std::cout << "MergeTree: in-place and functional merges matched a position->value map oracle on 4000 random tree triples (commutative, associative, empty identity, self-merge doubles); two depth-10^6 chains were merged iteratively" << std::endl; }
    return 0;
}
// Time Complexity: O(min(n, m)) (겹치는 위치만 순회, 파괴적) / 함수형은 O(n + m)
// Space Complexity: O(h) 명시적 스택
```

# Part 3. 순회
## Preorder()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

// 전위 순회(preorder): 루트 → 왼쪽 → 오른쪽.  ① 재귀 구현(작은 트리)과 ② 명시적 스택 구현(깊이 제한 없음)을 *독립 오라클*과 대조한다 — 오라클은 순회 코드를 쓰지 않고 각 노드의 루트 경로 문자열("", "L", "LR", …)을 전위 규칙의 비교자로 정렬한 것이다:
//  경로 a 가 b 의 접두사면(조상) a 가 먼저, 아니면 처음 갈라지는 곳에서 'L' 이 'R' 보다 먼저.   ③ 성질: 전위 순회열의 첫 원소는 루트, 각 부분 트리는 *연속 구간*, 부분 트리의 크기로 건너뛸 수 있음.   ④ 깊이 10^6 사슬(재귀는 스택 오버플로, 반복문은 안전).
struct BT { std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; std::vector<int> vals(n); std::iota(vals.begin(), vals.end(), 0); std::shuffle(vals.begin(), vals.end(), rng); t.root = t.add(vals[0]); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}};
    for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(vals[i]); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
void preRec(const BT& t, int u, std::vector<int>& out) { if (u < 0) return; out.push_back(t.val[u]); preRec(t, t.L[u], out); preRec(t, t.R[u], out); }
std::vector<int> preIter(const BT& t) { std::vector<int> out, st; if (t.root >= 0) st.push_back(t.root); while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(t.val[u]); if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } return out; }       // 오른쪽을 먼저 넣어 왼쪽이 먼저 나온다
std::vector<std::pair<std::string, int>> paths(const BT& t) { std::vector<std::pair<std::string, int>> out; std::vector<std::pair<int, std::string>> st = {{t.root, ""}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); out.push_back({p.second, t.val[p.first]}); if (t.L[p.first] >= 0) st.push_back({t.L[p.first], p.second + "L"}); if (t.R[p.first] >= 0) st.push_back({t.R[p.first], p.second + "R"}); } return out; }
bool preLess(const std::string& a, const std::string& b) { size_t i = 0; while (i < a.size() && i < b.size() && a[i] == b[i]) ++i; if (i == a.size()) return i != b.size(); if (i == b.size()) return false; return a[i] == 'L' && b[i] == 'R'; }
std::vector<int> preOracle(const BT& t) { auto p = paths(t); std::sort(p.begin(), p.end(), [](auto& x, auto& y) { return preLess(x.first, y.first); }); std::vector<int> out; for (auto& e : p) out.push_back(e.second); return out; }
int subtreeSize(const BT& t, int u) { int c = 0; std::vector<int> st = {u}; while (!st.empty()) { int x = st.back(); st.pop_back(); ++c; if (t.L[x] >= 0) st.push_back(t.L[x]); if (t.R[x] >= 0) st.push_back(t.R[x]); } return c; }

int main() {
    std::mt19937 rng(3);
    for (int it = 0; it < 5000; ++it) { BT t = randomBT(1 + (int)(rng() % 80), rng); std::vector<int> rec; preRec(t, t.root, rec); std::vector<int> it1 = preIter(t); assert(rec == it1 && it1 == preOracle(t) && it1.front() == t.val[t.root]); }
    for (int it = 0; it < 500; ++it) {                                                                          // ③ 부분 트리 = 연속 구간: 위치 i 의 노드(전위 순서) 아래 부분 트리는 [i, i + 크기)
        BT t = randomBT(1 + (int)(rng() % 60), rng); std::vector<int> order; { std::vector<int> st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); order.push_back(u); if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } }
        for (size_t i = 0; i < order.size(); ++i) { int sz = subtreeSize(t, order[i]); std::vector<int> sub = preIter(BT{t.val, t.L, t.R, order[i]}); assert(sub == std::vector<int>([&] { std::vector<int> v; for (int k = 0; k < sz; ++k) v.push_back(t.val[order[i + k]]); return v; }())); }
    }
    { const int n = 1000000; BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i); if (i % 2) t.L[cur] = c; else t.R[cur] = c; cur = c; } std::vector<int> p = preIter(t); assert((int)p.size() == n && p[0] == 0 && p[n - 1] == n - 1);
      std::cout << "Preorder: recursive and stack-based traversals matched the path-comparator oracle on 5000 random trees; every subtree was a contiguous range; a depth-10^6 zig-zag was traversed iteratively" << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(h) (명시적 스택)
```
## Inorder()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

// 중위 순회(inorder): 왼쪽 → 루트 → 오른쪽.  ① 재귀 ② 스택 반복 ③ 오라클: 경로 비교자 — 경로 a 가 b 의 접두사면 b 의 다음 글자가 'R' 일 때만 a 가 먼저(b 가 a 의 오른쪽 후손), 아니면 처음 갈라지는 곳에서 'L' 이 먼저.
//  ④ 이진 탐색 트리의 중위 순회는 정렬된 열: 무작위 BST 를 만들어 확인.  ⑤ 중위 순회열의 이웃은 *후계자* 관계 — 각 노드의 다음 원소는 (오른쪽 부분 트리의 가장 왼쪽 노드) 또는 (오른쪽 자식이 없으면, 왼쪽에서 올라온 첫 조상) 이다. 부모 포인터 없이 스택으로 구하는 것과 대조.
//  ⑥ 깊이 10^6 사슬을 반복문으로.
struct BT { std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; std::vector<int> vals(n); std::iota(vals.begin(), vals.end(), 0); std::shuffle(vals.begin(), vals.end(), rng); t.root = t.add(vals[0]); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}};
    for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(vals[i]); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
void inRec(const BT& t, int u, std::vector<int>& out) { if (u < 0) return; inRec(t, t.L[u], out); out.push_back(t.val[u]); inRec(t, t.R[u], out); }
std::vector<int> inIter(const BT& t) { std::vector<int> out, st; int u = t.root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = t.L[u]; } u = st.back(); st.pop_back(); out.push_back(t.val[u]); u = t.R[u]; } return out; }
std::vector<std::pair<std::string, int>> paths(const BT& t) { std::vector<std::pair<std::string, int>> out; std::vector<std::pair<int, std::string>> st = {{t.root, ""}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); out.push_back({p.second, t.val[p.first]}); if (t.L[p.first] >= 0) st.push_back({t.L[p.first], p.second + "L"}); if (t.R[p.first] >= 0) st.push_back({t.R[p.first], p.second + "R"}); } return out; }
bool inLess(const std::string& a, const std::string& b) { size_t i = 0; while (i < a.size() && i < b.size() && a[i] == b[i]) ++i; if (i == a.size() && i == b.size()) return false; if (i == a.size()) return b[i] == 'R'; if (i == b.size()) return a[i] == 'L'; return a[i] == 'L' && b[i] == 'R'; }
std::vector<int> inOracle(const BT& t) { auto p = paths(t); std::sort(p.begin(), p.end(), [](auto& x, auto& y) { return inLess(x.first, y.first); }); std::vector<int> out; for (auto& e : p) out.push_back(e.second); return out; }
std::vector<int> successorsByStack(const BT& t) {                                                              // 각 노드(값 0..n−1)의 중위 다음 값 (없으면 −1), 부모 포인터 없이
    std::vector<int> next(t.val.size(), -1), st; int prevVal = -1; int u = t.root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = t.L[u]; } u = st.back(); st.pop_back(); if (prevVal >= 0) next[prevVal] = t.val[u]; prevVal = t.val[u]; u = t.R[u]; } return next;
}
int successorDirect(const BT& t, int target) {                                                                 // 루트에서 내려가며 값이 target 인 노드의 후계자 (BST 가 아니므로 먼저 경로를 찾는다)
    std::vector<int> parent(t.val.size(), -1), dir(t.val.size(), 0); int target_node = -1; std::vector<int> q = {t.root}; for (size_t i = 0; i < q.size(); ++i) { int u = q[i]; if (t.val[u] == target) target_node = u; if (t.L[u] >= 0) { parent[t.L[u]] = u; dir[t.L[u]] = 0; q.push_back(t.L[u]); } if (t.R[u] >= 0) { parent[t.R[u]] = u; dir[t.R[u]] = 1; q.push_back(t.R[u]); } }
    if (t.R[target_node] >= 0) { int u = t.R[target_node]; while (t.L[u] >= 0) u = t.L[u]; return t.val[u]; }
    int u = target_node; while (parent[u] >= 0 && dir[u] == 1) u = parent[u]; return parent[u] < 0 ? -1 : t.val[parent[u]];                                      // 오른쪽 자식이 없으면: 처음으로 "왼쪽에서 올라온" 조상
}

int main() {
    std::mt19937 rng(13);
    for (int it = 0; it < 5000; ++it) { BT t = randomBT(1 + (int)(rng() % 80), rng); std::vector<int> rec; inRec(t, t.root, rec); std::vector<int> v = inIter(t); assert(rec == v && v == inOracle(t)); }
    for (int it = 0; it < 2000; ++it) {                                                                          // ⑤ 후계자
        BT t = randomBT(1 + (int)(rng() % 60), rng); std::vector<int> nx = successorsByStack(t); for (int v = 0; v < (int)t.val.size(); ++v) assert(nx[v] == successorDirect(t, v));
    }
    for (int it = 0; it < 500; ++it) {                                                                           // ④ 무작위 BST 의 중위 = 정렬
        int n = 1 + (int)(rng() % 100); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); BT t; t.root = t.add(keys[0]);
        for (int i = 1; i < n; ++i) { int c = t.add(keys[i]); int u = t.root; while (true) { int& nextChild = keys[i] < t.val[u] ? t.L[u] : t.R[u]; if (nextChild < 0) { nextChild = c; break; } u = nextChild; } }
        std::vector<int> v = inIter(t); assert(std::is_sorted(v.begin(), v.end()) && (int)v.size() == n);
    }
    { const int n = 1000000; BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i); t.R[cur] = c; cur = c; } std::vector<int> v = inIter(t); assert((int)v.size() == n && v[0] == 0 && v[n - 1] == n - 1);          // 오른쪽 사슬: 중위 = 삽입 순서
      BT l; l.root = l.add(0); cur = l.root; for (int i = 1; i < n; ++i) { int c = l.add(i); l.L[cur] = c; cur = c; } std::vector<int> w = inIter(l); assert((int)w.size() == n && w[0] == n - 1 && w[n - 1] == 0);                           // 왼쪽 사슬: 거꾸로 (스택이 n 까지 깊어진다)
      std::cout << "Inorder: recursive and stack-based traversals matched the path-comparator oracle on 5000 random trees; successors from the stack agreed with the direct rule; BST in-order was sorted; 10^6-deep chains were traversed iteratively" << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(h) (스택) — 왼쪽 사슬이면 O(n); Morris 순회는 O(1)
```
## Postorder()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

// 후위 순회(postorder): 왼쪽 → 오른쪽 → 루트.  자식을 먼저 처리해야 하는 일(부분 트리 크기·높이 계산, 트리 해제, 수식 트리 평가)에 쓴다.
//  구현 세 가지 — ① 재귀 ② "(루트, 오른쪽, 왼쪽) 전위의 역순" 한 스택 ③ 정석적인 한 스택(마지막으로 방문한 노드를 기억) — 를 경로 비교자 오라클(자손이 조상보다 먼저, 갈라지면 'L' 먼저)과 대조.
//  응용: 수식 트리 평가(후위 순회 = 후위 표기법) — 무작위 수식을 트리로 만들어 재귀 평가 값과 후위 스택 평가 값이 같다.  깊이 10^6 사슬 반복.
struct BT { std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; std::vector<int> vals(n); std::iota(vals.begin(), vals.end(), 0); std::shuffle(vals.begin(), vals.end(), rng); t.root = t.add(vals[0]); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}};
    for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(vals[i]); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
void postRec(const BT& t, int u, std::vector<int>& out) { if (u < 0) return; postRec(t, t.L[u], out); postRec(t, t.R[u], out); out.push_back(t.val[u]); }
std::vector<int> postTwoStacks(const BT& t) { std::vector<int> out, st; if (t.root >= 0) st.push_back(t.root); while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(t.val[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); if (t.R[u] >= 0) st.push_back(t.R[u]); } std::reverse(out.begin(), out.end()); return out; }
std::vector<int> postOneStack(const BT& t) {                                                                    // 정석: 오른쪽 자식에서 돌아왔을 때만 루트를 방문
    std::vector<int> out, st; int u = t.root, last = -1;
    while (u >= 0 || !st.empty()) { if (u >= 0) { st.push_back(u); u = t.L[u]; } else { int top = st.back(); if (t.R[top] >= 0 && last != t.R[top]) u = t.R[top]; else { out.push_back(t.val[top]); last = top; st.pop_back(); } } }
    return out;
}
std::vector<std::pair<std::string, int>> paths(const BT& t) { std::vector<std::pair<std::string, int>> out; std::vector<std::pair<int, std::string>> st = {{t.root, ""}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); out.push_back({p.second, t.val[p.first]}); if (t.L[p.first] >= 0) st.push_back({t.L[p.first], p.second + "L"}); if (t.R[p.first] >= 0) st.push_back({t.R[p.first], p.second + "R"}); } return out; }
bool postLess(const std::string& a, const std::string& b) { size_t i = 0; while (i < a.size() && i < b.size() && a[i] == b[i]) ++i; if (i == a.size() && i == b.size()) return false; if (i == a.size()) return false; if (i == b.size()) return true; return a[i] == 'L' && b[i] == 'R'; }      // 접두사(조상)는 *나중*
std::vector<int> postOracle(const BT& t) { auto p = paths(t); std::sort(p.begin(), p.end(), [](auto& x, auto& y) { return postLess(x.first, y.first); }); std::vector<int> out; for (auto& e : p) out.push_back(e.second); return out; }
// 수식 트리: 리프 = 숫자, 내부 = + − ×.  값은 mod 1e9+7 로 정수 계산
struct ExprNode { char op; long long num; int l, r; };
long long evalRec(const std::vector<ExprNode>& e, int u) { if (e[u].op == 0) return e[u].num; long long a = evalRec(e, e[u].l), b = evalRec(e, e[u].r); const long long M = 1000000007LL; return e[u].op == '+' ? (a + b) % M : e[u].op == '-' ? ((a - b) % M + M) % M : a * b % M; }
long long evalPostfix(const std::vector<ExprNode>& e, int root) {                                               // 후위 순회로 만든 토큰열을 스택으로 평가
    std::vector<int> order; { std::vector<int> st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); order.push_back(u); if (e[u].op) { st.push_back(e[u].l); st.push_back(e[u].r); } } std::reverse(order.begin(), order.end()); }
    std::vector<long long> vs; const long long M = 1000000007LL; for (int u : order) { if (e[u].op == 0) vs.push_back(e[u].num); else { long long b = vs.back(); vs.pop_back(); long long a = vs.back(); vs.pop_back(); vs.push_back(e[u].op == '+' ? (a + b) % M : e[u].op == '-' ? ((a - b) % M + M) % M : a * b % M); } } return vs.back();
}

int main() {
    std::mt19937 rng(31);
    for (int it = 0; it < 5000; ++it) { BT t = randomBT(1 + (int)(rng() % 80), rng); std::vector<int> rec; postRec(t, t.root, rec); std::vector<int> a = postTwoStacks(t), b = postOneStack(t); assert(rec == a && a == b && b == postOracle(t) && a.back() == t.val[t.root]); }
    for (int it = 0; it < 3000; ++it) {                                                                          // 수식 트리
        int leaves = 1 + (int)(rng() % 20); std::vector<ExprNode> e; std::vector<int> pool; for (int i = 0; i < leaves; ++i) { e.push_back({0, (long long)(rng() % 1000), -1, -1}); pool.push_back((int)e.size() - 1); }
        while (pool.size() > 1) { size_t i = rng() % pool.size(); int a = pool[i]; pool[i] = pool.back(); pool.pop_back(); size_t j = rng() % pool.size(); int b = pool[j]; pool[j] = pool.back(); pool.pop_back(); e.push_back({"+-*"[rng() % 3], 0, a, b}); pool.push_back((int)e.size() - 1); }
        assert(evalRec(e, pool[0]) == evalPostfix(e, pool[0]));
    }
    { const int n = 1000000; BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i); t.L[cur] = c; cur = c; } std::vector<int> a = postTwoStacks(t), b = postOneStack(t); assert(a == b && a[0] == n - 1 && a[n - 1] == 0);
      std::cout << "Postorder: recursive, reversed (root,right,left) and canonical one-stack traversals matched the path-comparator oracle on 5000 random trees; postfix evaluation of 3000 random expression trees equalled recursive evaluation; a 10^6-deep chain was handled iteratively" << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(h)
```
## LevelOrder()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 레벨 순서 순회(BFS): 깊이 0, 1, 2, … 순으로 같은 깊이는 왼쪽 → 오른쪽.  큐 하나로 O(n).  층별로 묶어야 하면 큐의 현재 크기만큼 끊어 처리한다.
//  오라클: 경로 문자열의 비교자 (길이가 짧은 것 먼저, 같으면 'L' < 'R' 사전순).   검증: ① 큐 구현 ② 층별 묶음 ③ 깊이 우선(DFS)으로 깊이별 수집 후 이어 붙이기 — 모두 오라클과 같다.
//  ④ 지그재그(층마다 방향 번갈아)와 오른쪽 옆면(각 층의 마지막 노드)  ⑤ 힙 배열은 레벨 순서 그 자체: 완전 이진 트리를 배열로 저장했을 때 BFS 결과 = 배열.   ⑥ 큐의 최대 길이 ≤ 인접한 두 층의 너비 합 ≤ 2·(가장 넓은 층), 완전 이진 트리(2^20 − 1 개)에서는 정확히 2^19.
struct BT { std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; std::vector<int> vals(n); std::iota(vals.begin(), vals.end(), 0); std::shuffle(vals.begin(), vals.end(), rng); t.root = t.add(vals[0]); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}};
    for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(vals[i]); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
std::vector<int> levelQueue(const BT& t, size_t* maxQueue = nullptr) { std::vector<int> out; std::queue<int> q; if (t.root >= 0) q.push(t.root); size_t mq = 0; while (!q.empty()) { mq = std::max(mq, q.size()); int u = q.front(); q.pop(); out.push_back(t.val[u]); if (t.L[u] >= 0) q.push(t.L[u]); if (t.R[u] >= 0) q.push(t.R[u]); } if (maxQueue) *maxQueue = mq; return out; }
std::vector<std::vector<int>> levelGroups(const BT& t) { std::vector<std::vector<int>> out; std::queue<int> q; if (t.root >= 0) q.push(t.root); while (!q.empty()) { size_t sz = q.size(); out.emplace_back(); for (size_t i = 0; i < sz; ++i) { int u = q.front(); q.pop(); out.back().push_back(t.val[u]); if (t.L[u] >= 0) q.push(t.L[u]); if (t.R[u] >= 0) q.push(t.R[u]); } } return out; }
std::vector<int> levelByDfs(const BT& t) { std::vector<std::vector<int>> by; std::vector<std::pair<int, int>> st = {{t.root, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); if ((int)by.size() <= p.second) by.emplace_back(); by[p.second].push_back(t.val[p.first]); if (t.R[p.first] >= 0) st.push_back({t.R[p.first], p.second + 1}); if (t.L[p.first] >= 0) st.push_back({t.L[p.first], p.second + 1}); } std::vector<int> out; for (auto& l : by) out.insert(out.end(), l.begin(), l.end()); return out; }
std::vector<int> levelOracle(const BT& t) { std::vector<std::pair<std::string, int>> p; std::vector<std::pair<int, std::string>> st = {{t.root, ""}}; while (!st.empty()) { auto e = st.back(); st.pop_back(); p.push_back({e.second, t.val[e.first]}); if (t.L[e.first] >= 0) st.push_back({t.L[e.first], e.second + "L"}); if (t.R[e.first] >= 0) st.push_back({t.R[e.first], e.second + "R"}); }
    std::sort(p.begin(), p.end(), [](auto& x, auto& y) { return x.first.size() != y.first.size() ? x.first.size() < y.first.size() : x.first < y.first; }); std::vector<int> out; for (auto& e : p) out.push_back(e.second); return out; }       // 'L' < 'R' 이므로 문자열 사전순이 왼쪽→오른쪽

int main() {
    std::mt19937 rng(37);
    for (int it = 0; it < 5000; ++it) {
        BT t = randomBT(1 + (int)(rng() % 100), rng); size_t mq; std::vector<int> a = levelQueue(t, &mq), c = levelByDfs(t), o = levelOracle(t); auto g = levelGroups(t); assert(a == o && c == o);
        std::vector<int> flat; size_t widest = 0; for (auto& l : g) { flat.insert(flat.end(), l.begin(), l.end()); widest = std::max(widest, l.size()); } assert(flat == o && mq <= 2 * widest && widest <= t.val.size() / 2 + 1);                       // ② ⑥
        std::vector<int> zig; for (size_t d = 0; d < g.size(); ++d) { auto l = g[d]; if (d % 2) std::reverse(l.begin(), l.end()); zig.insert(zig.end(), l.begin(), l.end()); } std::vector<int> right; for (auto& l : g) right.push_back(l.back());      // ④
        assert(zig.size() == o.size() && right.size() == g.size() && right[0] == t.val[t.root]); for (size_t d = 0; d < g.size(); ++d) assert(right[d] == g[d].back());
    }
    for (int n = 1; n <= 500; ++n) { BT t; std::vector<int> id(n); for (int i = 0; i < n; ++i) id[i] = t.add(i); t.root = id[0]; for (int i = 0; i < n; ++i) { if (2 * i + 1 < n) t.L[id[i]] = id[2 * i + 1]; if (2 * i + 2 < n) t.R[id[i]] = id[2 * i + 2]; } std::vector<int> v = levelQueue(t); std::vector<int> want(n); std::iota(want.begin(), want.end(), 0); assert(v == want); }          // ⑤ 힙 배열
    { const int n = (1 << 20) - 1; BT t; std::vector<int> id(n); for (int i = 0; i < n; ++i) id[i] = t.add(i); t.root = id[0]; for (int i = 0; i < n; ++i) { if (2 * i + 1 < n) t.L[id[i]] = id[2 * i + 1]; if (2 * i + 2 < n) t.R[id[i]] = id[2 * i + 2]; } size_t mq; std::vector<int> v = levelQueue(t, &mq); assert((int)v.size() == n && mq == (1u << 19));
      std::cout << "LevelOrder: queue, layered and DFS-by-depth traversals matched the path oracle on 5000 random trees; zig-zag / right-side views checked; a heap array's BFS equalled the array; a 2^20-node complete tree peaked at queue length " << mq << std::endl; }
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(가장 넓은 층) (완전 이진 트리에서는 약 n/2)
```
## MorrisTraversal()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 모리스 순회: 스택·재귀 없이 O(1) 추가 공간으로 중위/전위 순회. 아이디어 — 왼쪽 부분 트리의 가장 오른쪽 노드(중위 선행자)의 빈 오른쪽 포인터를 *임시 스레드*로 현재 노드에 연결해 두었다가 돌아왔을 때(=이미 연결됨) 끊는다.
//  검증: ① 중위·전위 모두 스택 구현과 같은 열, ② 순회가 끝나면 L/R 배열이 *정확히 원래대로* 복원, ③ 포인터 이동 수 ≤ 3n (각 간선을 최대 3 번), ④ 각 노드의 스레드는 동시에 많아야 깊이만큼만 존재,
//  ⑤ 중간에 멈춘 순회(예: 처음 k 개만 읽기)는 복원을 못 하므로 끝까지 가야 안전 — 이를 위한 복구 함수 대조.  ⑥ 깊이 10^6 사슬에서 스택 없이.
struct BT { std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; std::vector<int> vals(n); std::iota(vals.begin(), vals.end(), 0); std::shuffle(vals.begin(), vals.end(), rng); t.root = t.add(vals[0]); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}};
    for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(vals[i]); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
std::vector<int> inStack(const BT& t) { std::vector<int> out, st; int u = t.root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = t.L[u]; } u = st.back(); st.pop_back(); out.push_back(t.val[u]); u = t.R[u]; } return out; }
std::vector<int> preStack(const BT& t) { std::vector<int> out, st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(t.val[u]); if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } return out; }
std::vector<int> morris(BT& t, bool preorder, long* moves = nullptr, int* maxThreads = nullptr) {
    std::vector<int> out; int cur = t.root; long mv = 0; int threads = 0, mt = 0;
    while (cur >= 0) {
        if (t.L[cur] < 0) { out.push_back(t.val[cur]); cur = t.R[cur]; ++mv; }                                    // 왼쪽이 없으면 방문하고 오른쪽(또는 스레드)으로
        else { int pre = t.L[cur]; while (t.R[pre] >= 0 && t.R[pre] != cur) { pre = t.R[pre]; ++mv; }              // 왼쪽 부분 트리의 가장 오른쪽 노드
            if (t.R[pre] < 0) { t.R[pre] = cur; ++threads; mt = std::max(mt, threads); if (preorder) out.push_back(t.val[cur]); cur = t.L[cur]; ++mv; }      // 스레드 연결: 처음 도착 (전위는 여기서 방문)
            else { t.R[pre] = -1; --threads; if (!preorder) out.push_back(t.val[cur]); cur = t.R[cur]; ++mv; } } }   // 스레드 제거: 왼쪽을 끝내고 돌아옴 (중위는 여기서 방문)
    if (moves) *moves = mv; if (maxThreads) *maxThreads = mt; return out;
}

int main() {
    std::mt19937 rng(43);
    for (int it = 0; it < 5000; ++it) {
        BT t = randomBT(1 + (int)(rng() % 100), rng); BT orig = t; long mv; int mt;
        std::vector<int> in = morris(t, false, &mv, &mt); assert(in == inStack(orig) && t.L == orig.L && t.R == orig.R && mv <= 3L * (long)t.val.size());                // ① ② ③
        std::vector<int> pre = morris(t, true); assert(pre == preStack(orig) && t.L == orig.L && t.R == orig.R);
        int depth = 0; { std::vector<std::pair<int, int>> st = {{orig.root, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); depth = std::max(depth, p.second); if (orig.L[p.first] >= 0) st.push_back({orig.L[p.first], p.second + 1}); if (orig.R[p.first] >= 0) st.push_back({orig.R[p.first], p.second + 1}); } } assert(mt <= depth + 1);          // ④ 동시에 존재하는 스레드 수
    }
    { BT t; t.root = t.add(1); t.L[t.root] = t.add(0); t.R[t.root] = t.add(2); BT orig = t; int cur = t.root, visited = 0;                // ⑤ 중간에 멈추면 스레드가 남는다: 왼쪽 자식 0 만 읽고 멈춘다
      while (cur >= 0 && visited < 1) { if (t.L[cur] < 0) { ++visited; cur = t.R[cur]; } else { int pre = t.L[cur]; while (t.R[pre] >= 0 && t.R[pre] != cur) pre = t.R[pre]; if (t.R[pre] < 0) { t.R[pre] = cur; cur = t.L[cur]; } else { t.R[pre] = -1; ++visited; cur = t.R[cur]; } } }
      assert(t.R != orig.R && t.R[t.L[t.root]] == t.root); }                                                      // 노드 0 의 오른쪽 포인터가 임시 스레드(루트)로 남아 구조가 달라졌다 — 끝까지 돌려야 복원된다
    { const int n = 1000000; BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i); t.L[cur] = c; cur = c; } BT orig = t; long mv; int mt; std::vector<int> v = morris(t, false, &mv, &mt); assert((int)v.size() == n && v[0] == n - 1 && t.L == orig.L && t.R == orig.R && mt <= n);
      std::cout << "MorrisTraversal: threaded in-order and pre-order traversals matched the stack versions on 5000 random trees, restored every pointer, and used at most 3n pointer moves; a depth-10^6 chain was traversed with no stack (" << mv << " moves)" << std::endl; }
    return 0;
}
// Time Complexity: O(n) (각 간선 최대 3 번)
// Space Complexity: O(1) 추가 (임시 스레드는 트리 안의 빈 포인터를 재사용)
```
## EulerTour()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 오일러 투어: 트리를 따라 한 바퀴 돌며 노드에 들어갈 때와 *자식에서 돌아올 때마다* 노드를 기록한다 — 이진 트리에서 길이는 정확히 2n − 1 이다 (간선마다 두 번 지나므로 n + (n − 1)).
//  ① 성질: 인접한 두 항목은 트리에서 이웃(깊이 차 ±1), 처음 등장 순서 = 전위, 마지막 등장 순서 = 후위, 노드 v 의 처음~마지막 등장 사이가 v 의 부분 트리(길이 = 2·크기 − 1)  ② 투어에서 트리를 되살리기(부모 배열)
//  ③ 응용: LCA(u, v) = 처음 등장 위치 사이에서 *깊이가 최소*인 항목 — 구간 최솟값(RMQ, 희소 표) 로 O(1) 질의 vs 부모를 따라 올라가는 방법.   ④ 깊이 10^6 사슬 반복.
struct BT { std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; t.root = t.add(0); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}};
    for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(i); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }       // 값 = 노드 번호
std::vector<int> eulerTour(const BT& t, std::vector<int>& depthOut) {                                           // 반복문: 프레임 상태 0 = 막 들어옴, 1 = 왼쪽 자식에서 돌아옴, 2 = 오른쪽 자식에서 돌아옴
    std::vector<int> out; depthOut.clear(); struct Frame { int u, depth, state; }; std::vector<Frame> st = {{t.root, 0, 0}};
    while (!st.empty()) { Frame& f = st.back(); int u = f.u, d = f.depth;
        if (f.state == 0) { out.push_back(u); depthOut.push_back(d); f.state = 1; if (t.L[u] >= 0) st.push_back({t.L[u], d + 1, 0}); }
        else if (f.state == 1) { if (t.L[u] >= 0) { out.push_back(u); depthOut.push_back(d); } f.state = 2; if (t.R[u] >= 0) st.push_back({t.R[u], d + 1, 0}); }
        else { if (t.R[u] >= 0) { out.push_back(u); depthOut.push_back(d); } st.pop_back(); } }
    return out;
}
std::vector<int> tourSimple(const BT& t, std::vector<int>& depthOut) {                                           // 재귀(작은 트리) — 정의 그대로
    std::vector<int> out; depthOut.clear(); struct R { const BT& t; std::vector<int>& out; std::vector<int>& dep; void go(int u, int d) { out.push_back(u); dep.push_back(d); if (t.L[u] >= 0) { go(t.L[u], d + 1); out.push_back(u); dep.push_back(d); } if (t.R[u] >= 0) { go(t.R[u], d + 1); out.push_back(u); dep.push_back(d); } } } r{t, out, depthOut}; r.go(t.root, 0); return out;
}
struct Sparse { std::vector<std::vector<int>> tab; std::vector<int> dep; explicit Sparse(const std::vector<int>& d) : dep(d) { int n = (int)d.size(), K = 1; while ((1 << K) <= n) ++K; tab.assign(K, std::vector<int>(n)); std::iota(tab[0].begin(), tab[0].end(), 0); for (int k = 1; k < K; ++k) for (int i = 0; i + (1 << k) <= n; ++i) { int a = tab[k - 1][i], b = tab[k - 1][i + (1 << (k - 1))]; tab[k][i] = dep[a] <= dep[b] ? a : b; } }
    int argmin(int l, int r) const { int k = 31 - __builtin_clz((unsigned)(r - l + 1)); int a = tab[k][l], b = tab[k][r - (1 << k) + 1]; return dep[a] <= dep[b] ? a : b; } };

int main() {
    std::mt19937 rng(47);
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 60); BT t = randomBT(n, rng); std::vector<int> d1, d2; std::vector<int> a = tourSimple(t, d1), b = eulerTour(t, d2); assert(a == b && d1 == d2 && (int)a.size() == 2 * n - 1);        // 길이 2n−1, 반복 구현 == 정의
        for (size_t i = 0; i + 1 < a.size(); ++i) assert(std::abs(d1[i] - d1[i + 1]) == 1);                                                               // 이웃은 깊이가 ±1
        std::vector<int> first(n, -1), last(n, -1); for (size_t i = 0; i < a.size(); ++i) { if (first[a[i]] < 0) first[a[i]] = (int)i; last[a[i]] = (int)i; }
        std::vector<int> pre, post; { std::vector<std::pair<int, int>> byFirst, byLast; for (int v = 0; v < n; ++v) { byFirst.push_back({first[v], v}); byLast.push_back({last[v], v}); } std::sort(byFirst.begin(), byFirst.end()); std::sort(byLast.begin(), byLast.end()); for (auto& p : byFirst) pre.push_back(p.second); for (auto& p : byLast) post.push_back(p.second); }
        std::vector<int> preRef, st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); preRef.push_back(u); if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } assert(pre == preRef);        // 처음 등장 순서 = 전위
        std::vector<int> postRef; { std::vector<int> s2 = {t.root}; while (!s2.empty()) { int u = s2.back(); s2.pop_back(); postRef.push_back(u); if (t.L[u] >= 0) s2.push_back(t.L[u]); if (t.R[u] >= 0) s2.push_back(t.R[u]); } std::reverse(postRef.begin(), postRef.end()); } assert(post == postRef);        // 마지막 등장 순서 = 후위
        std::vector<int> size(n, 1); for (int v : postRef) { if (t.L[v] >= 0) size[v] += size[t.L[v]]; if (t.R[v] >= 0) size[v] += size[t.R[v]]; } for (int v = 0; v < n; ++v) assert(last[v] - first[v] + 1 == 2 * size[v] - 1);
        // ② 투어에서 부모 배열 복원: 아래로 내려가는 걸음(깊이 +1)에서 직전 항목이 부모
        std::vector<int> parent(n, -2); parent[t.root] = -1; for (size_t i = 1; i < a.size(); ++i) if (d1[i] == d1[i - 1] + 1) parent[a[i]] = a[i - 1];
        std::vector<int> truth(n, -1); for (int v = 0; v < n; ++v) { if (t.L[v] >= 0) truth[t.L[v]] = v; if (t.R[v] >= 0) truth[t.R[v]] = v; } assert(parent == truth);
        // ③ LCA by RMQ
        Sparse sp(d1); for (int q = 0; q < 50; ++q) { int u = (int)(rng() % n), v = (int)(rng() % n); int l = std::min(first[u], first[v]), r = std::max(first[u], first[v]); int viaRmq = a[sp.argmin(l, r)];
            std::vector<char> anc(n, 0); for (int x = u; x >= 0; x = truth[x]) anc[x] = 1; int x = v; while (!anc[x]) x = truth[x]; assert(viaRmq == x); }
    }
    { const int n = 1000000; BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i); t.L[cur] = c; cur = c; } std::vector<int> d; std::vector<int> a = eulerTour(t, d); assert((int)a.size() == 2 * n - 1 && a[n - 1] == n - 1 && a.back() == 0 && d[n - 1] == n - 1);
      std::cout << "EulerTour: iterative tour = definition on 3000 random trees (length 2n-1, neighbours differ by 1 in depth), first/last occurrences gave pre/post-order, the parent array was recovered from the tour, and RMQ-based LCA matched ancestor climbing; a depth-10^6 chain was toured iteratively" << std::endl; }
    return 0;
}
// Time Complexity: 투어 O(n), RMQ 전처리 O(n log n) 질의 O(1)
// Space Complexity: O(n)
```

# Part 4. 탐색
## TreeSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>

// 정렬되지 않은 이진 트리에서 값 찾기: 모든 노드를 볼 수밖에 없으므로 O(n). 방문 순서에 따라 *어떤 일치를 먼저 만나는지*와 메모리가 다르다.
//  ① 깊이 우선(재귀·반복) vs 너비 우선 vs 반복 심화(IDDFS): 존재 여부는 항상 선형 탐색 오라클과 같다.   ② 값이 중복될 때 BFS·IDDFS 는 *가장 얕은* 일치를 찾고(깊이 = 오라클의 최소 깊이), DFS 는 더 깊은 것을 찾을 수 있다.
//  ③ 방문 횟수: 찾지 못하면 DFS·BFS 모두 정확히 n, 찾으면 ≤ n.  IDDFS 는 메모리 O(h) 로 BFS 의 가장 얕은 일치를 얻는 대신 방문 수가 늘어나 완전 이진 트리에서는 약 2n.   ④ 깊이 10^6 사슬을 반복 DFS 로.
struct BT { std::vector<int> val, L, R, depth; int root = -1; int add(int v, int d) { val.push_back(v); L.push_back(-1); R.push_back(-1); depth.push_back(d); return (int)val.size() - 1; } };
BT randomBT(int n, int valueRange, std::mt19937& rng) { BT t; t.root = t.add((int)(rng() % valueRange), 0); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add((int)(rng() % valueRange), t.depth[s.first] + 1); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
int dfsRec(const BT& t, int u, int target, long& visits) { if (u < 0) return -1; ++visits; if (t.val[u] == target) return u; int a = dfsRec(t, t.L[u], target, visits); return a >= 0 ? a : dfsRec(t, t.R[u], target, visits); }
int dfsIter(const BT& t, int target, long& visits) { std::vector<int> st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); ++visits; if (t.val[u] == target) return u; if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } return -1; }
int bfs(const BT& t, int target, long& visits) { std::queue<int> q; q.push(t.root); while (!q.empty()) { int u = q.front(); q.pop(); ++visits; if (t.val[u] == target) return u; if (t.L[u] >= 0) q.push(t.L[u]); if (t.R[u] >= 0) q.push(t.R[u]); } return -1; }
int depthLimited(const BT& t, int u, int limit, int target, long& visits) { if (u < 0) return -1; ++visits; if (limit == 0) return t.val[u] == target ? u : -1; int a = depthLimited(t, t.L[u], limit - 1, target, visits); return a >= 0 ? a : depthLimited(t, t.R[u], limit - 1, target, visits); }   // limit 층에서만 검사
int iddfs(const BT& t, int target, long& visits) { int maxDepth = *std::max_element(t.depth.begin(), t.depth.end()); for (int lim = 0; lim <= maxDepth; ++lim) { int r = depthLimited(t, t.root, lim, target, visits); if (r >= 0) return r; } return -1; }      // 층마다 다시 내려간다

int main() {
    std::mt19937 rng(2);
    for (int it = 0; it < 5000; ++it) {
        int n = 1 + (int)(rng() % 80), range = 1 + (int)(rng() % (2 * n)); BT t = randomBT(n, range, rng); int target = (int)(rng() % (range + 3)); long v1 = 0, v2 = 0, v3 = 0, v4 = 0;
        int a = dfsRec(t, t.root, target, v1), b = dfsIter(t, target, v2), c = bfs(t, target, v3), d = iddfs(t, target, v4); bool exists = std::find(t.val.begin(), t.val.end(), target) != t.val.end();                          // ① 오라클: 배열 선형 탐색
        assert((a >= 0) == exists && (b >= 0) == exists && (c >= 0) == exists && (d >= 0) == exists && a == b);
        if (exists) { int minDepth = 1 << 30; for (int i = 0; i < n; ++i) if (t.val[i] == target) minDepth = std::min(minDepth, t.depth[i]); assert(t.depth[c] == minDepth && t.depth[d] == minDepth && t.depth[a] >= minDepth && v1 <= n && v3 <= n); }         // ② 가장 얕은 일치
        else assert(v1 == n && v2 == n && v3 == n);                                                                                                                                                                                  // ③ 못 찾으면 정확히 n 번
    }
    { int n = (1 << 12) - 1; BT t; t.root = t.add(0, 0); std::vector<int> id(n); id[0] = t.root; for (int i = 1; i < n; ++i) id[i] = t.add(i, t.depth[id[(i - 1) / 2]] + 1); for (int i = 1; i < n; ++i) { if (i % 2) t.L[id[(i - 1) / 2]] = id[i]; else t.R[id[(i - 1) / 2]] = id[i]; }
      long vb = 0, vi = 0; assert(bfs(t, -1, vb) < 0 && iddfs(t, -1, vi) < 0 && vb == n && vi > n && vi < 2L * n); }                                                                                                                             // IDDFS: 완전 이진 트리에서 방문 수 약 2n
    { const int n = 1000000; BT t; t.root = t.add(0, 0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i, i); t.L[cur] = c; cur = c; } long v = 0; assert(dfsIter(t, n - 1, v) == n - 1 && v == n);
      std::cout << "TreeSearch: DFS (recursive/iterative), BFS and IDDFS agreed with a linear scan on 5000 random trees; BFS and IDDFS found the shallowest match among duplicates; unsuccessful searches visited exactly n nodes; IDDFS visited about 2n on a complete tree; a 10^6 chain was searched iteratively" << std::endl; }
    return 0;
}
// Time Complexity: O(n) (IDDFS 는 완전 이진 트리에서 O(n), 사슬에서는 O(n²))
// Space Complexity: DFS·IDDFS O(h), BFS O(너비)
```
## FindNode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

// 노드 찾기: ① 값으로 첫 일치(전위 DFS) · 레벨 순서 첫 일치(BFS) · 일치 전부  ② 경로 문자열("LRL")로 O(경로 길이)  ③ 전위 순서 k 번째 노드를 *부분 트리 크기*로 O(h) 에 (순서 통계)  ④ 번호→노드 해시 색인으로 O(1).
//  모두 전위 순회 목록·레벨 순서 목록이라는 독립 오라클과 대조한다.  검증: 값이 중복된 무작위 트리에서 첫 일치/전부/k 번째/경로가 오라클과 같고, 없는 값·범위 밖 k·잘못된 경로는 −1.
struct BT { std::vector<int> val, L, R; int root = -1; int add(int v) { val.push_back(v); L.push_back(-1); R.push_back(-1); return (int)val.size() - 1; } };
BT randomBT(int n, int range, std::mt19937& rng) { BT t; t.root = t.add((int)(rng() % range)); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add((int)(rng() % range)); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
std::vector<int> preorderIds(const BT& t) { std::vector<int> out, st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(u); if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } return out; }
std::vector<int> levelIds(const BT& t) { std::vector<int> out; std::queue<int> q; q.push(t.root); while (!q.empty()) { int u = q.front(); q.pop(); out.push_back(u); if (t.L[u] >= 0) q.push(t.L[u]); if (t.R[u] >= 0) q.push(t.R[u]); } return out; }
int findFirstDfs(const BT& t, int v) { std::vector<int> st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); if (t.val[u] == v) return u; if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } return -1; }
int findFirstBfs(const BT& t, int v) { std::queue<int> q; q.push(t.root); while (!q.empty()) { int u = q.front(); q.pop(); if (t.val[u] == v) return u; if (t.L[u] >= 0) q.push(t.L[u]); if (t.R[u] >= 0) q.push(t.R[u]); } return -1; }
std::vector<int> findAll(const BT& t, int v) { std::vector<int> out; for (int u : preorderIds(t)) if (t.val[u] == v) out.push_back(u); return out; }
int findByPath(const BT& t, const std::string& path) { int u = t.root; for (char c : path) { if (u < 0) return -1; u = c == 'L' ? t.L[u] : c == 'R' ? t.R[u] : -1; } return u; }
std::vector<int> subtreeSizes(const BT& t) { std::vector<int> sz(t.val.size(), 1); std::vector<int> order = preorderIds(t); for (size_t i = order.size(); i-- > 0;) { int u = order[i]; if (t.L[u] >= 0) sz[u] += sz[t.L[u]]; if (t.R[u] >= 0) sz[u] += sz[t.R[u]]; } return sz; }
int kthPreorder(const BT& t, const std::vector<int>& sz, int k) {                                               // 0 기반 k 번째 (전위). 왼쪽 부분 트리 크기로 내려간다 — O(h)
    int u = t.root; if (k < 0 || k >= sz[u]) return -1;
    while (true) { if (k == 0) return u; --k; int ls = t.L[u] >= 0 ? sz[t.L[u]] : 0; if (k < ls) u = t.L[u]; else { k -= ls; u = t.R[u]; } }
}

int main() {
    std::mt19937 rng(7);
    for (int it = 0; it < 5000; ++it) {
        int n = 1 + (int)(rng() % 80), range = 1 + (int)(rng() % n); BT t = randomBT(n, range, rng); std::vector<int> pre = preorderIds(t), lvl = levelIds(t); std::vector<int> sz = subtreeSizes(t);
        int v = (int)(rng() % (range + 2)); int wantDfs = -1, wantBfs = -1; for (int u : pre) if (t.val[u] == v) { wantDfs = u; break; } for (int u : lvl) if (t.val[u] == v) { wantBfs = u; break; }
        assert(findFirstDfs(t, v) == wantDfs && findFirstBfs(t, v) == wantBfs && (wantDfs < 0) == (wantBfs < 0)); std::vector<int> all = findAll(t, v); assert((int)all.size() == (int)std::count(t.val.begin(), t.val.end(), v) && (all.empty() || all[0] == wantDfs));       // ①
        for (int k = -1; k <= n; ++k) assert(kthPreorder(t, sz, k) == (k >= 0 && k < n ? pre[k] : -1));                                                                                                                                             // ③ k 번째
        std::string path; int u = t.root; while (u >= 0 && rng() % 4) { int dir = (int)(rng() % 2); path += dir ? 'R' : 'L'; u = dir ? t.R[u] : t.L[u]; } assert(findByPath(t, path) == u);                                                                // ② 경로 (잘못된 방향이면 −1)
        assert(findByPath(t, "") == t.root && findByPath(t, "X") == -1);
        std::unordered_map<int, int> index; for (int id = 0; id < n; ++id) index[id] = id; assert(index.count(n - 1) == 1 && index.count(n) == 0);                                                                                          // ④ 번호 색인
    }
    { const int n = 1000000; BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i); t.R[cur] = c; cur = c; } std::vector<int> sz = subtreeSizes(t); assert(kthPreorder(t, sz, 777777) == 777777 && findFirstDfs(t, n - 1) == n - 1 && findFirstBfs(t, 123456) == 123456 && findByPath(t, std::string(500000, 'R')) == 500000);
      std::cout << "FindNode: first-match DFS/BFS, all matches, k-th preorder node via subtree sizes and path lookup agreed with the traversal-list oracles on 5000 duplicate-heavy random trees; a 10^6 chain was handled iteratively" << std::endl; }
    return 0;
}
// Time Complexity: 값 찾기 O(n), 경로 O(경로 길이), k 번째 노드 O(h) (크기 배열 전처리 O(n))
// Space Complexity: O(n)
```
## FindParent()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>

// 부모 찾기: 부모 포인터가 없으면 루트에서 내려가며 탐색 O(n), 있으면 O(1).  질의가 q 개면 질의마다 탐색하는 방법은 O(n·q), 한 번 순회로 전부 구해 두면 O(n + q).
//  ① 세 방법을 대조: 질의마다 DFS · 한 번 순회로 부모 배열(BFS) · 반복 DFS.  연산 수를 세어 n·q vs n + q 를 확인.   ② 경계: 루트의 부모는 없음, 없는 노드는 −1, 자식 포인터가 아니라 *노드 번호*로 찾으므로 값이 같아도 구분됨.
//  ③ 조상 사슬(루트까지)과 k 번째 조상, "u 는 v 의 조상인가" 를 부모 따라 올라가기 vs 전위 번호 구간으로 판정.   ④ 깊이 10^6 사슬.
struct BT { std::vector<int> L, R; int root = -1; int add() { L.push_back(-1); R.push_back(-1); return (int)L.size() - 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; t.root = t.add(); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(); (s.second == 0 ? t.L[s.first] : t.R[s.first]) = c; slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
int findParentSearch(const BT& t, int target, long& steps) {                                                   // 질의마다 루트에서 DFS
    if (target < 0 || target >= (int)t.L.size() || target == t.root) return -1; std::vector<int> st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); ++steps; if (t.L[u] == target || t.R[u] == target) return u; if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } return -1; }
std::vector<int> parentArray(const BT& t, long& steps) { std::vector<int> p(t.L.size(), -1); std::queue<int> q; q.push(t.root); while (!q.empty()) { int u = q.front(); q.pop(); ++steps; if (t.L[u] >= 0) { p[t.L[u]] = u; q.push(t.L[u]); } if (t.R[u] >= 0) { p[t.R[u]] = u; q.push(t.R[u]); } } return p; }

int main() {
    std::mt19937 rng(11);
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 80); BT t = randomBT(n, rng); long bulk = 0; std::vector<int> par = parentArray(t, bulk); assert(bulk == n && par[t.root] == -1);
        long perQuery = 0; int queries = 20; for (int q = 0; q < queries; ++q) { int v = (int)(rng() % (n + 2)) - 1; int expect = v >= 0 && v < n ? par[v] : -1; assert(findParentSearch(t, v, perQuery) == expect); }                                    // ① 존재하지 않는 번호는 −1
        assert(perQuery <= (long)n * queries);                                                                                                                                                                                     // 질의마다 탐색은 최대 n·q
        for (int v = 0; v < n; ++v) { if (v == t.root) continue; int p = par[v]; assert(p >= 0 && (t.L[p] == v || t.R[p] == v)); }                                                                                              // 부모 ↔ 자식 링크
        // ③ 조상 사슬, 조상 판정 (전위 번호 구간 vs 올라가기)
        std::vector<int> tin(n), sz(n, 1), order; { std::vector<int> st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); tin[u] = (int)order.size(); order.push_back(u); if (t.R[u] >= 0) st.push_back(t.R[u]); if (t.L[u] >= 0) st.push_back(t.L[u]); } for (size_t i = order.size(); i-- > 0;) { int u = order[i]; if (par[u] >= 0) sz[par[u]] += sz[u]; } }
        for (int q = 0; q < 30; ++q) { int u = (int)(rng() % n), v = (int)(rng() % n); bool climbs = false; for (int x = v; x >= 0; x = par[x]) if (x == u) climbs = true; assert(climbs == (tin[u] <= tin[v] && tin[v] < tin[u] + sz[u])); }
        int v = (int)(rng() % n); std::vector<int> chain; for (int x = v; x >= 0; x = par[x]) chain.push_back(x); assert(chain.back() == t.root);
        for (int k = 0; k < (int)chain.size(); ++k) { int x = v; for (int s = 0; s < k; ++s) x = par[x]; assert(x == chain[k]); }
    }
    { const int n = 1000000; BT t; t.root = t.add(); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(); t.L[cur] = c; cur = c; } long steps = 0; std::vector<int> p = parentArray(t, steps); assert(p[n - 1] == n - 2 && p[0] == -1 && steps == n);
      long one = 0; assert(findParentSearch(t, n - 1, one) == n - 2 && one == n - 1);                                                                                                                                                // 단일 질의가 O(n): 마지막 노드의 부모
      std::cout << "FindParent: per-query DFS, bulk BFS parent arrays and ancestor tests (climbing vs preorder intervals) agreed on 3000 random trees; on a 10^6 chain one query cost " << one << " steps while the bulk pass cost " << steps << " for all queries" << std::endl; }
    return 0;
}
// Time Complexity: 질의마다 탐색 O(n), 부모 배열 전처리 O(n) 후 질의 O(1)
// Space Complexity: O(n)
```
## LowestCommonAncestor()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>

// 최소 공통 조상(LCA): 두 노드의 공통 조상 중 가장 깊은 것.  다섯 가지 방법을 서로 대조한다.
//  ① 브루트포스: u 의 조상 집합을 표시하고 v 에서 올라가며 처음 만나는 것  ② 깊이를 맞추고 함께 올라가기 O(h)  ③ 이진 승(binary lifting) O(log n)  ④ 오일러 투어 + 구간 최솟값(희소 표) O(1)  ⑤ 재귀(후위): 양쪽에서 하나씩 찾으면 현재 노드 — 두 노드가 모두 트리에 있다는 전제.
//  경계: u = v, u 가 v 의 조상(LCA = u), 루트. 사슬 10^6 에서는 LCA(u, v) = min(u, v) — 올라가기는 O(n) 이지만 이진 승·RMQ 는 O(log n)/O(1).  트리 10^5 개 노드에서 질의 10^5 개로 세 빠른 방법이 일치.
struct BT { std::vector<int> L, R, parent, depth; int root = -1; int add() { L.push_back(-1); R.push_back(-1); parent.push_back(-1); depth.push_back(0); return (int)L.size() - 1; } void link(int p, int c, bool left) { (left ? L[p] : R[p]) = c; parent[c] = p; depth[c] = depth[p] + 1; } };
BT randomBT(int n, std::mt19937& rng, int shape) { BT t; t.root = t.add(); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}}; for (int i = 1; i < n; ++i) { size_t pick = shape == 0 ? rng() % slots.size() : slots.size() - 1 - (rng() % 3 == 0 && slots.size() > 1 ? 1 : 0); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(); t.link(s.first, c, s.second == 0); slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
int lcaBrute(const BT& t, int u, int v) { std::vector<char> anc(t.L.size(), 0); for (int x = u; x >= 0; x = t.parent[x]) anc[x] = 1; int x = v; while (!anc[x]) x = t.parent[x]; return x; }
int lcaClimb(const BT& t, int u, int v, long& steps) { while (t.depth[u] > t.depth[v]) { u = t.parent[u]; ++steps; } while (t.depth[v] > t.depth[u]) { v = t.parent[v]; ++steps; } while (u != v) { u = t.parent[u]; v = t.parent[v]; steps += 2; } return u; }
struct Lifting { std::vector<std::vector<int>> up; const BT& t; explicit Lifting(const BT& tree) : t(tree) { int n = (int)t.L.size(), K = 1; while ((1 << K) < n) ++K; up.assign(K + 1, std::vector<int>(n, -1)); up[0] = t.parent; for (int k = 1; k <= K; ++k) for (int v = 0; v < n; ++v) up[k][v] = up[k - 1][v] < 0 ? -1 : up[k - 1][up[k - 1][v]]; }
    int lca(int u, int v) const { if (t.depth[u] < t.depth[v]) std::swap(u, v); int diff = t.depth[u] - t.depth[v]; for (size_t k = 0; diff; ++k, diff >>= 1) if (diff & 1) u = up[k][u]; if (u == v) return u; for (int k = (int)up.size() - 1; k >= 0; --k) if (up[k][u] != up[k][v]) { u = up[k][u]; v = up[k][v]; } return t.parent[u]; } };
struct EulerRmq { std::vector<int> tour, first, dep; std::vector<std::vector<int>> tab; explicit EulerRmq(const BT& t) : first(t.L.size(), -1) {
        struct F { int u, state; }; std::vector<F> st = {{t.root, 0}}; while (!st.empty()) { F& f = st.back(); int u = f.u; if (f.state == 0) { first[u] = (int)tour.size(); tour.push_back(u); f.state = 1; if (t.L[u] >= 0) st.push_back({t.L[u], 0}); } else if (f.state == 1) { if (t.L[u] >= 0) tour.push_back(u); f.state = 2; if (t.R[u] >= 0) st.push_back({t.R[u], 0}); } else { if (t.R[u] >= 0) tour.push_back(u); st.pop_back(); } }
        dep.resize(tour.size()); for (size_t i = 0; i < tour.size(); ++i) dep[i] = t.depth[tour[i]]; int m = (int)tour.size(), K = 1; while ((1 << K) <= m) ++K; tab.assign(K, std::vector<int>(m)); std::iota(tab[0].begin(), tab[0].end(), 0);
        for (int k = 1; k < K; ++k) for (int i = 0; i + (1 << k) <= m; ++i) { int a = tab[k - 1][i], b = tab[k - 1][i + (1 << (k - 1))]; tab[k][i] = dep[a] <= dep[b] ? a : b; } }
    int lca(int u, int v) const { int l = std::min(first[u], first[v]), r = std::max(first[u], first[v]); int k = 31 - __builtin_clz((unsigned)(r - l + 1)); int a = tab[k][l], b = tab[k][r - (1 << k) + 1]; return tour[dep[a] <= dep[b] ? a : b]; } };
int lcaRec(const BT& t, int u, int p, int q) { if (u < 0 || u == p || u == q) return u; int a = lcaRec(t, t.L[u], p, q), b = lcaRec(t, t.R[u], p, q); if (a >= 0 && b >= 0) return u; return a >= 0 ? a : b; }

int main() {
    std::mt19937 rng(5);
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 60); BT t = randomBT(n, rng, (int)(rng() % 2)); Lifting lf(t); EulerRmq er(t);
        for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v) { int want = lcaBrute(t, u, v); long s = 0; assert(lcaClimb(t, u, v, s) == want && lf.lca(u, v) == want && er.lca(u, v) == want && lcaRec(t, t.root, u, v) == want && want == lcaBrute(t, v, u)); }       // 모든 쌍 · 대칭
        for (int u = 0; u < n; ++u) { assert(lf.lca(u, u) == u && er.lca(t.root, u) == t.root); if (t.parent[u] >= 0) assert(lf.lca(u, t.parent[u]) == t.parent[u]); }                                                                                       // 경계: u = v, 루트, 부모
    }
    { const int n = 100000; BT t = randomBT(n, rng, 0); Lifting lf(t); EulerRmq er(t); long climbSteps = 0; for (int q = 0; q < 100000; ++q) { int u = (int)(rng() % n), v = (int)(rng() % n); int a = lf.lca(u, v), b = er.lca(u, v); assert(a == b); if (q < 2000) { long s = 0; assert(lcaClimb(t, u, v, s) == a); climbSteps += s; } } (void)climbSteps; }
    { const int n = 300000; BT t; t.root = t.add(); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(); t.link(cur, c, true); cur = c; } Lifting lf(t); for (int q = 0; q < 100000; ++q) { int u = (int)(rng() % n), v = (int)(rng() % n); assert(lf.lca(u, v) == std::min(u, v)); }
      long steps = 0; assert(lcaClimb(t, n - 1, n - 2, steps) == n - 2 && steps == 1);
      std::cout << "LowestCommonAncestor: brute force, level-and-climb, binary lifting, Euler tour + sparse table and recursive post-order agreed on all node pairs of 3000 random trees; 10^5 queries on a 10^5-node tree matched; on a 3*10^5 chain lifting returned min(u, v) for 10^5 queries" << std::endl; }
    return 0;
}
// Time Complexity: 올라가기 O(h), 이진 승 O(log n) (전처리 O(n log n)), 오일러 투어 + RMQ O(1) (전처리 O(n log n))
// Space Complexity: O(n log n)
```
## PathToNode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 루트에서 노드까지의 경로: ① 재귀 백트래킹(원래 구현: 경로 vector 에 넣고 못 찾으면 빼기) ② 부모 배열을 한 번 만들어 두고 target 에서 위로 올라가 뒤집기(질의마다 O(경로 길이)) ③ 임의의 두 노드 사이의 경로 = (u→LCA 역방향) + (LCA→v).
//  검증: 경로는 루트로 시작해 target 으로 끝나고, 연이은 항목이 부모–자식이며, 길이 = 깊이 + 1, 노드가 중복되지 않는다(단순 경로).  두 노드 사이 경로는 걸을 수 있고(이웃끼리), 단순하며, 길이 = 거리 + 1 — 모든 쌍에서 BFS 최단 경로와 같은 길이.
//  없는 노드는 빈 경로.  깊이 10^6 에서 ② 는 반복문이라 안전(① 은 스택 오버플로 위험, 작은 트리만).
struct BT { std::vector<int> L, R, parent, depth; int root = -1; int add() { L.push_back(-1); R.push_back(-1); parent.push_back(-1); depth.push_back(0); return (int)L.size() - 1; } void link(int p, int c, bool left) { (left ? L[p] : R[p]) = c; parent[c] = p; depth[c] = depth[p] + 1; } };
BT randomBT(int n, std::mt19937& rng) { BT t; t.root = t.add(); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(); t.link(s.first, c, s.second == 0); slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
bool pathRec(const BT& t, int u, int target, std::vector<int>& path) { if (u < 0) return false; path.push_back(u); if (u == target) return true; if (pathRec(t, t.L[u], target, path) || pathRec(t, t.R[u], target, path)) return true; path.pop_back(); return false; }
std::vector<int> pathUp(const BT& t, int target) { std::vector<int> p; if (target < 0 || target >= (int)t.L.size()) return p; for (int x = target; x >= 0; x = t.parent[x]) p.push_back(x); std::reverse(p.begin(), p.end()); return p; }
int lca(const BT& t, int u, int v) { while (t.depth[u] > t.depth[v]) u = t.parent[u]; while (t.depth[v] > t.depth[u]) v = t.parent[v]; while (u != v) { u = t.parent[u]; v = t.parent[v]; } return u; }
std::vector<int> pathBetween(const BT& t, int u, int v) { int a = lca(t, u, v); std::vector<int> left, right; for (int x = u; x != a; x = t.parent[x]) left.push_back(x); left.push_back(a); for (int x = v; x != a; x = t.parent[x]) right.push_back(x); std::reverse(right.begin(), right.end()); left.insert(left.end(), right.begin(), right.end()); return left; }
std::vector<int> bfsDist(const BT& t, int s) { int n = (int)t.L.size(); std::vector<std::vector<int>> g(n); for (int i = 0; i < n; ++i) { if (t.L[i] >= 0) { g[i].push_back(t.L[i]); g[t.L[i]].push_back(i); } if (t.R[i] >= 0) { g[i].push_back(t.R[i]); g[t.R[i]].push_back(i); } } std::vector<int> d(n, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } return d; }

int main() {
    std::mt19937 rng(17);
    for (int it = 0; it < 300; ++it) {
        int n = 1 + (int)(rng() % 60); BT t = randomBT(n, rng);
        for (int target = -1; target <= n; ++target) { std::vector<int> a; bool ok = pathRec(t, t.root, target, a); std::vector<int> b = pathUp(t, target); if (target < 0 || target >= n) { assert(!ok && a.empty() && b.empty()); continue; }
            assert(ok && a == b && a.front() == t.root && a.back() == target && (int)a.size() == t.depth[target] + 1 && std::set<int>(a.begin(), a.end()).size() == a.size()); for (size_t i = 0; i + 1 < a.size(); ++i) assert(t.parent[a[i + 1]] == a[i]); }       // ① ② 단순 경로, 부모–자식
        for (int u = 0; u < n; ++u) { std::vector<int> d = bfsDist(t, u); for (int v = 0; v < n; ++v) { std::vector<int> p = pathBetween(t, u, v); assert(p.front() == u && p.back() == v && (int)p.size() == d[v] + 1 && std::set<int>(p.begin(), p.end()).size() == p.size());   // ③ 길이 = 거리 + 1, 단순
                for (size_t i = 0; i + 1 < p.size(); ++i) assert(t.parent[p[i]] == p[i + 1] || t.parent[p[i + 1]] == p[i]); } }                                                                                                                                               // 이웃끼리
    }
    { const int n = 1000000; BT t; t.root = t.add(); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(); t.link(cur, c, true); cur = c; } std::vector<int> p = pathUp(t, n - 1); assert((int)p.size() == n && p[0] == 0 && p[n - 1] == n - 1); std::vector<int> mid = pathBetween(t, 250000, 750000); assert((int)mid.size() == 500001 && mid.front() == 250000 && mid.back() == 750000);
      std::cout << "PathToNode: recursive backtracking and parent-array paths agreed, were simple parent-child chains of length depth+1, and the u-to-v path through the LCA had length BFS-distance+1 for every pair of 300 random trees; a 10^6-node path was produced iteratively" << std::endl; }
    return 0;
}
// Time Complexity: 재귀 O(n), 부모 배열 O(경로 길이) (전처리 O(n)), 두 노드 사이 O(경로 길이)
// Space Complexity: O(경로 길이) (재귀 O(h) 호출 스택)
```
## DistanceBetweenNodes()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>

// 트리에서 두 노드 사이의 거리(간선 수) = depth[u] + depth[v] − 2·depth[LCA(u, v)].
//  ① 모든 쌍에서 BFS 거리와 같음 + 거리의 성질(대칭, 삼각부등식, d(u,v)=0 ⇔ u=v)  ② 지름(가장 먼 두 노드 사이): 임의 노드에서 가장 먼 노드 a → a 에서 가장 먼 노드 b 의 거리 (두 번 BFS) = 모든 쌍 중 최댓값(브루트포스).
//  ③ 거리의 총합(Wiener 지수): 모든 쌍의 합 = Σ_{간선} size·(n − size) (간선을 지나는 쌍의 수) — O(n) 이고 O(n²) 합과 같음.  ④ 한 점에서 모든 노드까지 거리의 합을 *재루팅* 으로 모든 점에 대해 O(n).
//  ⑤ 10^5 개 노드에서 지름·총합이 두 방법으로 일치.
struct BT { std::vector<int> L, R, parent, depth; int root = -1; int add() { L.push_back(-1); R.push_back(-1); parent.push_back(-1); depth.push_back(0); return (int)L.size() - 1; } void link(int p, int c, bool left) { (left ? L[p] : R[p]) = c; parent[c] = p; depth[c] = depth[p] + 1; } };
BT randomBT(int n, std::mt19937& rng, int shape) { BT t; t.root = t.add(); std::vector<std::pair<int, int>> slots = {{t.root, 0}, {t.root, 1}}; for (int i = 1; i < n; ++i) { size_t pick = shape == 0 ? rng() % slots.size() : slots.size() - 1 - (rng() % 3 == 0 && slots.size() > 1 ? 1 : 0); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); int c = t.add(); t.link(s.first, c, s.second == 0); slots.push_back({c, 0}); slots.push_back({c, 1}); } return t; }
int lca(const BT& t, int u, int v) { while (t.depth[u] > t.depth[v]) u = t.parent[u]; while (t.depth[v] > t.depth[u]) v = t.parent[v]; while (u != v) { u = t.parent[u]; v = t.parent[v]; } return u; }
int dist(const BT& t, int u, int v) { return t.depth[u] + t.depth[v] - 2 * t.depth[lca(t, u, v)]; }
std::vector<int> bfs(const std::vector<std::vector<int>>& g, int s) { std::vector<int> d(g.size(), -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } return d; }
std::vector<std::vector<int>> adj(const BT& t) { std::vector<std::vector<int>> g(t.L.size()); for (size_t i = 0; i < t.L.size(); ++i) { if (t.L[i] >= 0) { g[i].push_back(t.L[i]); g[t.L[i]].push_back((int)i); } if (t.R[i] >= 0) { g[i].push_back(t.R[i]); g[t.R[i]].push_back((int)i); } } return g; }
std::vector<long long> sumOfDistancesAll(const BT& t) {                                                           // 재루팅: ans[child] = ans[parent] + (n − 2·size[child])
    int n = (int)t.L.size(); std::vector<int> order = {t.root}; for (size_t i = 0; i < order.size(); ++i) { int u = order[i]; if (t.L[u] >= 0) order.push_back(t.L[u]); if (t.R[u] >= 0) order.push_back(t.R[u]); }
    std::vector<long long> size(n, 1), down(n, 0), ans(n, 0); for (size_t i = order.size(); i-- > 1;) { int u = order[i], p = t.parent[u]; size[p] += size[u]; down[p] += down[u] + size[u]; }
    ans[t.root] = down[t.root]; for (size_t i = 1; i < order.size(); ++i) { int u = order[i], p = t.parent[u]; ans[u] = ans[p] + n - 2 * size[u]; } return ans;
}

int main() {
    std::mt19937 rng(19);
    for (int it = 0; it < 2000; ++it) {
        int n = 1 + (int)(rng() % 50); BT t = randomBT(n, rng, (int)(rng() % 2)); auto g = adj(t); std::vector<std::vector<int>> D(n); for (int u = 0; u < n; ++u) D[u] = bfs(g, u);
        for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v) { assert(dist(t, u, v) == D[u][v] && D[u][v] == D[v][u] && ((D[u][v] == 0) == (u == v))); for (int w = 0; w < n; w += 7) assert(D[u][w] <= D[u][v] + D[v][w]); }          // ① 거리의 성질
        int a = (int)(std::max_element(D[0].begin(), D[0].end()) - D[0].begin()); std::vector<int> da = bfs(g, a); int diam = *std::max_element(da.begin(), da.end()); int best = 0; for (int u = 0; u < n; ++u) best = std::max(best, *std::max_element(D[u].begin(), D[u].end())); assert(diam == best);   // ② 지름 = 두 번 BFS
        long long wiener = 0; for (int u = 0; u < n; ++u) for (int v = u + 1; v < n; ++v) wiener += D[u][v]; std::vector<int> sz(n, 1), order = {t.root}; for (size_t i = 0; i < order.size(); ++i) { int u = order[i]; if (t.L[u] >= 0) order.push_back(t.L[u]); if (t.R[u] >= 0) order.push_back(t.R[u]); } for (size_t i = order.size(); i-- > 1;) sz[t.parent[order[i]]] += sz[order[i]];
        long long byEdges = 0; for (int v = 0; v < n; ++v) if (t.parent[v] >= 0) byEdges += (long long)sz[v] * (n - sz[v]); assert(wiener == byEdges);                                                                   // ③ 간선 기여 공식
        std::vector<long long> all = sumOfDistancesAll(t); for (int u = 0; u < n; ++u) { long long s = 0; for (int v = 0; v < n; ++v) s += D[u][v]; assert(all[u] == s); }                                                  // ④ 재루팅
    }
    { const int n = 100000; BT t = randomBT(n, rng, 0); auto g = adj(t); std::vector<int> d0 = bfs(g, 0); int a = (int)(std::max_element(d0.begin(), d0.end()) - d0.begin()); std::vector<int> da = bfs(g, a); int b = (int)(std::max_element(da.begin(), da.end()) - da.begin()); int diam = da[b]; std::vector<int> db = bfs(g, b);
      for (int v = 0; v < n; ++v) assert(std::max(da[v], db[v]) <= diam);                                                                                                                                                  // 지름의 양 끝에서 본 이심률이 지름 이하
      long long byEdges = 0; std::vector<int> sz(n, 1), order = {t.root}; for (size_t i = 0; i < order.size(); ++i) { int u = order[i]; if (t.L[u] >= 0) order.push_back(t.L[u]); if (t.R[u] >= 0) order.push_back(t.R[u]); } for (size_t i = order.size(); i-- > 1;) sz[t.parent[order[i]]] += sz[order[i]]; for (int v = 0; v < n; ++v) if (t.parent[v] >= 0) byEdges += (long long)sz[v] * (n - sz[v]);
      std::vector<long long> all = sumOfDistancesAll(t); long long totalOrdered = 0; for (long long x : all) totalOrdered += x; assert(totalOrdered == 2 * byEdges);                                                                    // ⑤ 순서쌍 합 = 2 × 비순서쌍 합
      std::cout << "DistanceBetweenNodes: LCA-based distance equalled BFS distance for all pairs of 2000 random trees; the double-BFS diameter, the edge-contribution Wiener index and the O(n) rerooting sums matched brute force; a 10^5-node tree had diameter " << diam << " and total pair distance " << byEdges << std::endl; }
    return 0;
}
// Time Complexity: 거리 O(h) (LCA 방법에 따라 O(1)), 지름 O(n), 총합 O(n)
// Space Complexity: O(n)
```

# Part 5. 이진 탐색 트리(BST)
## InsertBST()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 이진 탐색 트리(BST) 삽입: 루트에서 key 와 비교하며 내려가 빈 자리에 붙인다. 평균 O(log n), 최악(정렬된 입력) O(n).  노드는 배열 풀(인덱스)에 두어 해제 문제가 없다.
//  ① std::set 과 무작위 삽입열 대조(중복은 거부), 중위 순회가 정렬되고 BST 성질 유지.  ② 모양은 *삽입 순서*가 정한다: 같은 키 집합의 모든 순열(n ≤ 7)을 넣으면 서로 다른 모양의 수가 카탈랑 수 C(n).
//  ③ 정렬된 삽입 → 높이 n − 1 (사슬), 무작위 삽입 → 노드 평균 깊이 ≈ 2·ln n − 2.85 (n = 10^5 에서 약 20).   ④ 재귀(포인터)와 반복(배열) 구현이 같은 모양을 만든다.
struct BST {
    std::vector<int> key, L, R; int root = -1; size_t pathSteps = 0;
    bool insert(int k) {
        int parent = -1, u = root; bool left = false; while (u >= 0) { parent = u; ++pathSteps; if (k == key[u]) return false; left = k < key[u]; u = left ? L[u] : R[u]; }       // 중복 거부
        key.push_back(k); L.push_back(-1); R.push_back(-1); int c = (int)key.size() - 1; if (parent < 0) root = c; else (left ? L[parent] : R[parent]) = c; return true;
    }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(key[u]); u = R[u]; } return out; }
    int height() const { if (root < 0) return -1; int best = 0; std::vector<std::pair<int, int>> st = {{root, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return best; }
    long long internalPathLength() const { long long s = 0; if (root < 0) return 0; std::vector<std::pair<int, int>> st = {{root, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); s += p.second; if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return s; }
    bool isBst() const { std::vector<int> v = inorder(); for (size_t i = 1; i < v.size(); ++i) if (v[i - 1] >= v[i]) return false; return true; }                // 중위가 *엄격하게* 증가
    std::string shape(int u) const { if (u < 0) return "."; return "(" + shape(L[u]) + shape(R[u]) + ")"; }                                                                  // 모양만 (작은 트리용)
};
struct PNode { int key; PNode *l = nullptr, *r = nullptr; explicit PNode(int k) : key(k) {} };
PNode* insertRec(PNode* n, int k, std::vector<std::unique_ptr<PNode>>& own) { if (!n) { own.emplace_back(new PNode(k)); return own.back().get(); } if (k < n->key) n->l = insertRec(n->l, k, own); else if (k > n->key) n->r = insertRec(n->r, k, own); return n; }
std::string shapeP(const PNode* n) { if (!n) return "."; return "(" + shapeP(n->l) + shapeP(n->r) + ")"; }

int main() {
    std::mt19937 rng(14);
    for (int round = 0; round < 500; ++round) {                                                                  // ① std::set 대조
        BST t; std::set<int> ref; for (int op = 0; op < 300; ++op) { int k = (int)(rng() % 200); bool a = t.insert(k), b = ref.insert(k).second; assert(a == b); (void)a; (void)b; }
        std::vector<int> in = t.inorder(); assert(in == std::vector<int>(ref.begin(), ref.end()) && t.isBst());
    }
    for (int n = 1; n <= 7; ++n) {                                                                               // ② 모양의 수 = 카탈랑
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 1); std::set<std::string> shapes; do { BST t; for (int k : perm) t.insert(k); shapes.insert(t.shape(t.root)); } while (std::next_permutation(perm.begin(), perm.end()));
        long catalan[] = {1, 1, 2, 5, 14, 42, 132, 429}; assert((long)shapes.size() == catalan[n]);
    }
    { BST sorted; for (int i = 0; i < 3000; ++i) sorted.insert(i); assert(sorted.height() == 2999 && sorted.internalPathLength() == 2999LL * 3000 / 2);                // ③ 정렬된 삽입 = 사슬
      const int n = 100000; std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); BST t; for (int k : keys) t.insert(k); double avgDepth = (double)t.internalPathLength() / n, expect = 2 * std::log((double)n) - 2.85;
      assert(std::abs(avgDepth - expect) < 0.1 * expect && t.height() < 6 * std::log((double)n) && t.isBst());
      std::cout << "InsertBST: matched std::set over 150000 random insertions; the number of distinct BST shapes over all permutations of n <= 7 keys was the Catalan number; sorted insertion gave height 2999 while random insertion of 10^5 keys gave average depth " << avgDepth << " (2 ln n - 2.85 = " << expect << ")" << std::endl; }
    for (int it = 0; it < 2000; ++it) {                                                                          // ④ 재귀 포인터 구현과 같은 모양
        std::vector<int> keys(1 + (int)(rng() % 30)); for (int& k : keys) k = (int)(rng() % 50); BST a; std::vector<std::unique_ptr<PNode>> own; PNode* root = nullptr; for (int k : keys) { a.insert(k); root = insertRec(root, k, own); } assert(a.shape(a.root) == shapeP(root));
    }
    return 0;
}
// Time Complexity: 평균 O(log n), 최악 O(n) (정렬된 입력)
// Space Complexity: O(1) 추가 (반복문), 재귀는 O(h) 호출 스택
```
## SearchBST()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// BST 탐색: 한 번 비교할 때마다 한쪽 부분 트리를 통째로 버린다 — 비교 횟수 ≤ 높이 + 1.  ① 존재 여부·비교 횟수(≤ h + 1)를 std::set 과 대조  ② 정렬 순서 질의: ceil(≥ k 중 최소)·floor(≤ k 중 최대) = std::set::lower_bound / 이전 원소,
//  ③ 구간 [lo, hi] 안의 키 모으기: 방문한 노드 수 ≤ 결과 수 + 2·(높이 + 1) (경계 두 경로만 추가로 훑는다)  ④ 총 비용 항등식: 성공 탐색의 비교 합 = 내부 경로 길이 + n, 실패(모든 빈 자리) 탐색의 비교 합 = 외부 경로 길이 = 내부 경로 길이 + 2n.
struct BST {
    std::vector<int> key, L, R; int root = -1;
    void insert(int k) { int parent = -1, u = root; bool left = false; while (u >= 0) { parent = u; if (k == key[u]) return; left = k < key[u]; u = left ? L[u] : R[u]; } key.push_back(k); L.push_back(-1); R.push_back(-1); int c = (int)key.size() - 1; if (parent < 0) root = c; else (left ? L[parent] : R[parent]) = c; }
    bool contains(int k, int& comparisons) const { int u = root; comparisons = 0; while (u >= 0) { ++comparisons; if (k == key[u]) return true; u = k < key[u] ? L[u] : R[u]; } return false; }
    bool containsRec(int u, int k) const { if (u < 0) return false; if (k == key[u]) return true; return containsRec(k < key[u] ? L[u] : R[u], k); }
    int ceilKey(int k) const { int best = -1, u = root; while (u >= 0) { if (key[u] == k) return k; if (key[u] > k) { best = key[u]; u = L[u]; } else u = R[u]; } return best; }                    // ≥ k 중 최소 (없으면 −1; 키는 0 이상)
    int floorKey(int k) const { int best = -1, u = root; while (u >= 0) { if (key[u] == k) return k; if (key[u] < k) { best = key[u]; u = R[u]; } else u = L[u]; } return best; }
    void range(int u, int lo, int hi, std::vector<int>& out, long& visited) const { if (u < 0) return; ++visited; if (key[u] > lo) range(L[u], lo, hi, out, visited); if (key[u] >= lo && key[u] <= hi) out.push_back(key[u]); if (key[u] < hi) range(R[u], lo, hi, out, visited); }
    int height() const { if (root < 0) return -1; int best = 0; std::vector<std::pair<int, int>> st = {{root, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return best; }
    long long internalPath() const { long long s = 0; std::vector<std::pair<int, int>> st; if (root >= 0) st.push_back({root, 0}); while (!st.empty()) { auto p = st.back(); st.pop_back(); s += p.second; if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return s; }
};

int main() {
    std::mt19937 rng(8);
    for (int round = 0; round < 1000; ++round) {
        BST t; std::set<int> ref; int n = 1 + (int)(rng() % 100); for (int i = 0; i < n; ++i) { int k = (int)(rng() % 300); t.insert(k); ref.insert(k); } int h = t.height();
        for (int q = 0; q < 100; ++q) { int k = (int)(rng() % 320); int cmp; bool f = t.contains(k, cmp); assert(f == (ref.count(k) > 0) && f == t.containsRec(t.root, k) && cmp <= h + 1);            // ① 존재 여부, 비교 ≤ h + 1
            auto lb = ref.lower_bound(k); assert(t.ceilKey(k) == (lb == ref.end() ? -1 : *lb)); auto ub = ref.upper_bound(k); int fl = ub == ref.begin() ? -1 : *std::prev(ub); assert(t.floorKey(k) == fl); }            // ②
        for (int q = 0; q < 30; ++q) { int lo = (int)(rng() % 300), hi = lo + (int)(rng() % 80); std::vector<int> got; long visited = 0; t.range(t.root, lo, hi, got, visited); std::vector<int> want(ref.lower_bound(lo), ref.upper_bound(hi)); assert(got == want && visited <= (long)got.size() + 2L * (h + 1)); }   // ③
        long long successful = 0; for (int k : ref) { int c; t.contains(k, c); successful += c; } assert(successful == t.internalPath() + (long long)ref.size());                  // ④ 성공 탐색의 총 비교
        long long external = 0;
        { std::vector<std::pair<int, int>> st; if (t.root >= 0) st.push_back({t.root, 0}); while (!st.empty()) { auto p = st.back(); st.pop_back(); if (t.L[p.first] >= 0) st.push_back({t.L[p.first], p.second + 1}); else external += p.second + 1; if (t.R[p.first] >= 0) st.push_back({t.R[p.first], p.second + 1}); else external += p.second + 1; } }
        assert(external == t.internalPath() + 2LL * (long long)ref.size());                                                                                      // 외부 경로 길이 = 내부 경로 길이 + 2n  (모든 실패 탐색의 비교 합)
    }
    { const int mid = 500000; BST t; t.insert(mid); for (int i = 1; i < 2000; ++i) { t.insert(mid + i); t.insert(mid - i); } int cmp; assert(t.contains(mid + 1999, cmp) && cmp == 2000 && !t.contains(-5, cmp));
      std::cout << "SearchBST: existence, comparison counts (<= height+1), ceil/floor and range queries (visited <= results + 2(h+1)) matched std::set on 1000 random trees; the comparison-total identities (successful = internal path + n) held" << std::endl; }
    return 0;
}
// Time Complexity: 탐색·ceil·floor O(h), 구간 O(h + 결과 수)
// Space Complexity: O(1) (반복문)
```
## DeleteBST()
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

// BST 삭제의 세 경우: 리프(그냥 떼기), 자식 하나(자식으로 대체), 자식 둘(중위 *후계자* 또는 *선행자*의 키로 덮어쓰고 그 노드를 삭제).
//  ① 반복문 + 배열 풀(해제된 칸 재활용)으로 구현해 std::set 과 무작위 삽입/삭제열(키 중복·없는 키 포함)을 대조하고 매 단계 BST 성질·크기·풀 누수 없음 검사.
//  ② 후계자만 계속 쓰는 Hibbard 삭제는 삭제·삽입을 많이 반복하면 트리가 한쪽으로 기울어 평균 깊이가 늘어난다 — 후계자/선행자를 번갈아 쓰면 새로 만든 무작위 트리 수준에 머문다 (n = 1000, 200 만 번 삭제+삽입으로 측정).
//  ③ 삭제 뒤에도 위치 관계: 남은 키의 중위 순서는 변하지 않는다.  ④ 모든 키를 지우면 빈 트리가 되고 풀은 재사용된다.
struct BST {
    std::vector<int> key, L, R, freeList; int root = -1; size_t count = 0; bool alternate; bool flip = false; explicit BST(bool alt) : alternate(alt) {}
    int make(int k) { ++count; if (!freeList.empty()) { int i = freeList.back(); freeList.pop_back(); key[i] = k; L[i] = R[i] = -1; return i; } key.push_back(k); L.push_back(-1); R.push_back(-1); return (int)key.size() - 1; }
    bool insert(int k) { int parent = -1, u = root; bool left = false; while (u >= 0) { parent = u; if (k == key[u]) return false; left = k < key[u]; u = left ? L[u] : R[u]; } int c = make(k); if (parent < 0) root = c; else (left ? L[parent] : R[parent]) = c; return true; }
    bool erase(int k) {
        int parent = -1, u = root; bool left = false; while (u >= 0 && key[u] != k) { parent = u; left = k < key[u]; u = left ? L[u] : R[u]; } if (u < 0) return false;
        if (L[u] >= 0 && R[u] >= 0) {                                                                                   // 자식 둘: 후계자(오른쪽의 최솟값) 또는 선행자(왼쪽의 최댓값)의 키를 가져오고 그 노드를 지운다
            bool useSucc = !alternate || (flip = !flip); int p = u, s = useSucc ? R[u] : L[u]; while ((useSucc ? L[s] : R[s]) >= 0) { p = s; s = useSucc ? L[s] : R[s]; } key[u] = key[s];
            int child = useSucc ? R[s] : L[s]; if (p == u) (useSucc ? R[p] : L[p]) = child; else (useSucc ? L[p] : R[p]) = child; freeList.push_back(s); --count; return true; }
        int child = L[u] >= 0 ? L[u] : R[u]; if (parent < 0) root = child; else (left ? L[parent] : R[parent]) = child; freeList.push_back(u); --count; return true;                           // 리프 또는 자식 하나
    }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(key[u]); u = R[u]; } return out; }
    double avgDepth() const { long long s = 0; size_t n = 0; std::vector<std::pair<int, int>> st; if (root >= 0) st.push_back({root, 0}); while (!st.empty()) { auto p = st.back(); st.pop_back(); s += p.second; ++n; if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return n ? (double)s / n : 0; }
};

int main() {
    std::mt19937 rng(22);
    for (int round = 0; round < 300; ++round) {                                                                  // ① std::set 대조
        BST t(round % 2); std::set<int> ref; for (int op = 0; op < 400; ++op) { int k = (int)(rng() % 60); if (rng() % 2) { bool a = t.insert(k), b = ref.insert(k).second; assert(a == b); (void)a; (void)b; } else { bool a = t.erase(k), b = ref.erase(k) > 0; assert(a == b); (void)a; (void)b; }
            if (op % 20 == 0) { std::vector<int> in = t.inorder(); assert(in == std::vector<int>(ref.begin(), ref.end()) && t.count == ref.size() && t.key.size() - t.freeList.size() == ref.size()); } }                          // 풀 누수 없음
        std::vector<int> all(ref.begin(), ref.end()); std::shuffle(all.begin(), all.end(), rng); for (int k : all) { bool ok = t.erase(k); assert(ok); (void)ok; } assert(t.root < 0 && t.count == 0 && t.inorder().empty());                                  // ④ 전부 지우면 빈 트리
    }
    // ② Hibbard(후계자만) vs 번갈아: n = 1000 개의 키를 유지하며 200 만 번 (무작위 키 삭제 + 새 무작위 키 삽입).  후계자만 쓰면 오른쪽 부분 트리가 계속 얇아져 평균 깊이가 늘어난다 (Θ(n²) 번의 갱신 뒤 Θ(√n)).
    double depthHibbard = 0, depthAlt = 0, depthFresh = 0; const int N = 1000; const long ROUNDS = 2000000;
    for (int variant = 0; variant < 2; ++variant) {
        BST t(variant == 1); std::vector<int> present; const int range = 1 << 30; while ((int)present.size() < N) { int k = (int)(rng() % range); if (t.insert(k)) present.push_back(k); }
        if (variant == 0) { double sum = 0; for (int rep = 0; rep < 5; ++rep) { BST fresh(false); std::vector<int> keys(present); std::shuffle(keys.begin(), keys.end(), rng); for (int k : keys) fresh.insert(k); sum += fresh.avgDepth(); } depthFresh = sum / 5; }
        for (long step = 0; step < ROUNDS; ++step) { size_t idx = rng() % present.size(); bool erased = t.erase(present[idx]); assert(erased); (void)erased; int k; do k = (int)(rng() % range); while (!t.insert(k)); present[idx] = k; }          // 키가 없어질 때까지 새 키를 뽑는다 (충돌 확률 무시할 수준)
        (variant == 0 ? depthHibbard : depthAlt) = t.avgDepth(); std::sort(present.begin(), present.end()); assert(t.inorder() == present && t.count == present.size());
    }
    assert(depthHibbard > depthAlt * 1.25 && depthHibbard > depthFresh * 1.15 && depthAlt < depthFresh * 1.1);                                                                                                      // 후계자만 쓰면 눈에 띄게 깊어진다
    std::cout << "DeleteBST: leaf / one-child / two-child deletion matched std::set over 120000 random operations with no pool leaks; after 2*10^6 delete+insert rounds on 1000 keys the average depth was " << depthHibbard << " with successor-only (Hibbard) deletion, " << depthAlt << " when alternating successor/predecessor, versus " << depthFresh << " for fresh random trees" << std::endl;
    return 0;
}
// Time Complexity: O(h)
// Space Complexity: O(1) 추가 (반복문, 노드 풀 재사용)
```
## FindMin()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// BST 의 최솟값 = 가장 왼쪽 노드: 왼쪽 자식이 없을 때까지 내려간다 (비교 없음, ≤ 높이 번).  정렬되지 않은 이진 트리는 전부 훑어야 한다 (O(n)).
//  ① BST 의 findMin 을 std::set::begin 과 무작위 삽입/최솟값 제거열로 대조  ② 최솟값을 반복해서 빼면(popMin) 정렬된 열 — 트리 정렬(tree sort): std::sort 와 같다  ③ 어떤 노드의 *부분 트리* 최솟값(후계자 계산의 재료)
//  ④ 정렬되지 않은 트리의 최솟값 = 선형 탐색  ⑤ 걸음 수: 왼쪽 사슬은 n − 1, 오른쪽 사슬은 0  ⑥ 100 만 노드 왼쪽 사슬을 반복문으로.
struct BST {
    std::vector<int> key, L, R; int root = -1;
    void insert(int k) { int parent = -1, u = root; bool left = false; while (u >= 0) { parent = u; if (k == key[u]) return; left = k < key[u]; u = left ? L[u] : R[u]; } key.push_back(k); L.push_back(-1); R.push_back(-1); int c = (int)key.size() - 1; if (parent < 0) root = c; else (left ? L[parent] : R[parent]) = c; }
    int findMinNode(int u, long* steps = nullptr) const { while (L[u] >= 0) { u = L[u]; if (steps) ++*steps; } return u; }
    int popMin() { int parent = -1, u = root; while (L[u] >= 0) { parent = u; u = L[u]; } int v = key[u]; if (parent < 0) root = R[u]; else L[parent] = R[u]; return v; }       // 가장 왼쪽 노드는 오른쪽 자식만 가질 수 있어 그 자식으로 대체
    bool empty() const { return root < 0; }
};

int main() {
    std::mt19937 rng(31);
    for (int round = 0; round < 500; ++round) {
        BST t; std::set<int> ref; for (int op = 0; op < 200; ++op) { if (rng() % 3 && !t.empty()) { int m = t.popMin(); assert(m == *ref.begin()); ref.erase(ref.begin()); } else { int k = (int)(rng() % 100); t.insert(k); ref.insert(k); } if (!t.empty()) assert(t.key[t.findMinNode(t.root)] == *ref.begin()); else assert(ref.empty()); }       // ①
    }
    for (int it = 0; it < 500; ++it) {                                                                           // ② 트리 정렬
        int n = 1 + (int)(rng() % 200); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); BST t; for (int k : keys) t.insert(k); std::vector<int> out; while (!t.empty()) out.push_back(t.popMin()); std::sort(keys.begin(), keys.end()); assert(out == keys);
    }
    for (int it = 0; it < 500; ++it) {                                                                           // ③ 부분 트리 최솟값
        int n = 1 + (int)(rng() % 100); BST t; for (int i = 0; i < n; ++i) t.insert((int)(rng() % 300)); std::vector<int> parent(t.key.size(), -1); for (size_t u = 0; u < t.key.size(); ++u) { if (t.L[u] >= 0) parent[t.L[u]] = (int)u; if (t.R[u] >= 0) parent[t.R[u]] = (int)u; }
        for (size_t u = 0; u < t.key.size(); ++u) { std::vector<int> st = {(int)u}; int best = 1 << 30; while (!st.empty()) { int x = st.back(); st.pop_back(); best = std::min(best, t.key[x]); if (t.L[x] >= 0) st.push_back(t.L[x]); if (t.R[x] >= 0) st.push_back(t.R[x]); } assert(t.key[t.findMinNode((int)u)] == best); }
    }
    for (int it = 0; it < 1000; ++it) {                                                                          // ④ 정렬되지 않은 트리
        int n = 1 + (int)(rng() % 60); std::vector<int> val(n), L(n, -1), R(n, -1); for (int& v : val) v = (int)(rng() % 1000) - 500; std::vector<std::pair<int, int>> slots = {{0, 0}, {0, 1}}; for (int i = 1; i < n; ++i) { size_t pick = rng() % slots.size(); auto s = slots[pick]; slots[pick] = slots.back(); slots.pop_back(); (s.second == 0 ? L[s.first] : R[s.first]) = i; slots.push_back({i, 0}); slots.push_back({i, 1}); }
        int best = 1 << 30; std::vector<int> st = {0}; long visited = 0; while (!st.empty()) { int u = st.back(); st.pop_back(); ++visited; best = std::min(best, val[u]); if (L[u] >= 0) st.push_back(L[u]); if (R[u] >= 0) st.push_back(R[u]); } assert(best == *std::min_element(val.begin(), val.end()) && visited == n);
    }
    { BST left; left.key = std::vector<int>(1000000); std::iota(left.key.begin(), left.key.end(), 0); left.L.assign(1000000, -1); left.R.assign(1000000, -1); left.root = 999999; for (int i = 999999; i > 0; --i) left.L[i] = i - 1;                          // ⑤ 왼쪽 사슬: 키가 내려갈수록 작아진다
      long steps = 0; int m = left.findMinNode(left.root, &steps); assert(left.key[m] == 0 && steps == 999999);
      BST right; right.key = left.key; right.L.assign(1000000, -1); right.R.assign(1000000, -1); right.root = 0; for (int i = 0; i + 1 < 1000000; ++i) right.R[i] = i + 1; long s2 = 0; assert(right.findMinNode(right.root, &s2) == 0 && s2 == 0);
      std::cout << "FindMin: leftmost-node search matched std::set::begin under random insert/pop-min sequences; repeated popMin sorted 500 random key sets like std::sort; subtree minima and unsorted-tree minima matched exhaustive scans; the left chain took n-1 steps and the right chain 0 (n = 10^6)" << std::endl; }
    return 0;
}
// Time Complexity: BST O(h), 정렬 안 된 트리 O(n)
// Space Complexity: O(1)
```
## FindMax()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// BST 의 최댓값 = 가장 오른쪽 노드.  FindMin 의 거울상: 좌우를 뒤집은 트리의 최솟값과 같다.
//  ① std::set::rbegin 과 대조  ② popMax 를 반복하면 내림차순 정렬  ③ k 번째로 큰 수: 역중위(오른쪽 → 루트 → 왼쪽) 순회를 k 번째에서 멈춘다 — std::set 의 끝에서 k 번째와 대조, 방문 수 ≤ k + h  ④ 성질: 최댓값은 오른쪽 자식이 없고, 거울 트리에서의 findMin 과 같다.
//  ⑤ 정렬되지 않은 트리의 최댓값은 O(n) 순회  ⑥ 100 만 노드 오른쪽 사슬.
struct BST {
    std::vector<int> key, L, R; int root = -1;
    void insert(int k) { int parent = -1, u = root; bool left = false; while (u >= 0) { parent = u; if (k == key[u]) return; left = k < key[u]; u = left ? L[u] : R[u]; } key.push_back(k); L.push_back(-1); R.push_back(-1); int c = (int)key.size() - 1; if (parent < 0) root = c; else (left ? L[parent] : R[parent]) = c; }
    int findMaxNode(int u, long* steps = nullptr) const { while (R[u] >= 0) { u = R[u]; if (steps) ++*steps; } return u; }
    int popMax() { int parent = -1, u = root; while (R[u] >= 0) { parent = u; u = R[u]; } int v = key[u]; if (parent < 0) root = L[u]; else R[parent] = L[u]; return v; }
    int kthLargest(int k, long& visited) const { std::vector<int> st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = R[u]; } u = st.back(); st.pop_back(); ++visited; if (--k == 0) return key[u]; u = L[u]; } return -1; }       // 역중위: 큰 것부터
    void mirror() { std::swap(L, R); }                                                                           // 모든 노드의 좌우 교환 (키는 그대로이므로 거울 트리는 BST 가 아니다)
    bool empty() const { return root < 0; }
};

int main() {
    std::mt19937 rng(37);
    for (int round = 0; round < 500; ++round) {
        BST t; std::set<int> ref; for (int op = 0; op < 200; ++op) { if (rng() % 3 && !t.empty()) { int m = t.popMax(); assert(m == *ref.rbegin()); ref.erase(std::prev(ref.end())); } else { int k = (int)(rng() % 100); t.insert(k); ref.insert(k); } if (!t.empty()) { int mx = t.findMaxNode(t.root); assert(t.key[mx] == *ref.rbegin() && t.R[mx] < 0); } }          // ① ④ 최댓값은 오른쪽 자식이 없다
    }
    for (int it = 0; it < 500; ++it) {                                                                           // ② 내림차순 정렬
        int n = 1 + (int)(rng() % 200); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); BST t; for (int k : keys) t.insert(k); std::vector<int> out; while (!t.empty()) out.push_back(t.popMax()); std::sort(keys.rbegin(), keys.rend()); assert(out == keys);
    }
    for (int it = 0; it < 1000; ++it) {                                                                          // ③ k 번째로 큰 수
        int n = 1 + (int)(rng() % 150); BST t; std::set<int> ref; for (int i = 0; i < n; ++i) { int k = (int)(rng() % 400); t.insert(k); ref.insert(k); } int h = 0; { std::vector<std::pair<int, int>> st = {{t.root, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); h = std::max(h, p.second); if (t.L[p.first] >= 0) st.push_back({t.L[p.first], p.second + 1}); if (t.R[p.first] >= 0) st.push_back({t.R[p.first], p.second + 1}); } }
        for (int k = 1; k <= (int)ref.size() + 1; k += 1 + (int)(rng() % 5)) { long visited = 0; int got = t.kthLargest(k, visited); if (k <= (int)ref.size()) { auto it2 = ref.rbegin(); std::advance(it2, k - 1); assert(got == *it2 && visited <= k + h + 1); } else assert(got == -1); }
    }
    for (int it = 0; it < 500; ++it) {                                                                           // 거울 트리의 최솟값 위치 = 원래 트리의 최댓값 위치
        BST t; for (int i = 0; i < 80; ++i) t.insert((int)(rng() % 500)); int mx = t.findMaxNode(t.root); BST m = t; m.mirror(); int leftmostOfMirror = m.root; while (m.L[leftmostOfMirror] >= 0) leftmostOfMirror = m.L[leftmostOfMirror]; assert(leftmostOfMirror == mx);
    }
    { BST right; right.key = std::vector<int>(1000000); std::iota(right.key.begin(), right.key.end(), 0); right.L.assign(1000000, -1); right.R.assign(1000000, -1); right.root = 0; for (int i = 0; i + 1 < 1000000; ++i) right.R[i] = i + 1; long steps = 0; int m = right.findMaxNode(right.root, &steps); assert(right.key[m] == 999999 && steps == 999999);          // ⑥ 오른쪽 사슬
      std::cout << "FindMax: rightmost-node search matched std::set::rbegin under random insert/pop-max sequences; popMax sorted descending; the k-th largest via reverse in-order matched std::set with visited <= k + h + 1; the maximum was the mirror image of the minimum; a 10^6 right chain took n-1 steps" << std::endl; }
    return 0;
}
// Time Complexity: O(h), k 번째로 큰 수 O(h + k)
// Space Complexity: O(1) (k 번째 큰 수는 O(h) 스택)
```
## Successor()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 중위 후계자(successor): 정렬 순서에서 바로 다음 키.  규칙 — 오른쪽 자식이 있으면 *오른쪽 부분 트리의 가장 왼쪽*, 없으면 *왼쪽 자식 쪽으로 올라온 첫 조상*.
//  ① 부모 포인터 버전과 ② 부모 없이 루트에서 내려가며 "마지막으로 왼쪽으로 꺾은 노드" 를 기억하는 버전(트리에 없는 키에도 가능: upper_bound = k 초과 중 최소)을 std::set 과 대조.
//  ③ 후계자를 최솟값에서 시작해 반복하면 정렬 순서 전체를 도는데, 전체 걸음 수는 간선 수의 2 배 이하(각 간선을 많아야 두 번) — O(n) 이므로 한 번 호출당 분할상환 O(1).   ④ 왼쪽 사슬(높이 n)에서도 반복은 총 O(n).
struct BST {
    std::vector<int> key, L, R, P; int root = -1;
    void insert(int k) { int parent = -1, u = root; bool left = false; while (u >= 0) { parent = u; if (k == key[u]) return; left = k < key[u]; u = left ? L[u] : R[u]; } key.push_back(k); L.push_back(-1); R.push_back(-1); P.push_back(parent); int c = (int)key.size() - 1; if (parent < 0) root = c; else (left ? L[parent] : R[parent]) = c; }
    int succWithParent(int u, long& steps) const { if (R[u] >= 0) { u = R[u]; ++steps; while (L[u] >= 0) { u = L[u]; ++steps; } return u; } int p = P[u]; ++steps; while (p >= 0 && R[p] == u) { u = p; p = P[p]; ++steps; } return p; }          // 노드 → 노드 (없으면 −1)
    int upperBoundKey(int k) const { int best = -1, u = root; while (u >= 0) { if (key[u] > k) { best = key[u]; u = L[u]; } else u = R[u]; } return best; }                                                          // 부모 없이: k 초과 중 최소 (키는 0 이상, 없으면 −1)
    int minNode() const { int u = root; while (L[u] >= 0) u = L[u]; return u; }
};

int main() {
    std::mt19937 rng(41);
    for (int round = 0; round < 1000; ++round) {
        BST t; std::set<int> ref; int n = 1 + (int)(rng() % 120); for (int i = 0; i < n; ++i) { int k = (int)(rng() % 400); t.insert(k); ref.insert(k); }
        for (size_t u = 0; u < t.key.size(); ++u) { long steps = 0; int s = t.succWithParent((int)u, steps); auto it = ref.upper_bound(t.key[u]); assert((s < 0) == (it == ref.end()) && (s < 0 || t.key[s] == *it)); }                    // ① 노드의 후계자
        for (int q = 0; q < 50; ++q) { int k = (int)(rng() % 420); auto it = ref.upper_bound(k); assert(t.upperBoundKey(k) == (it == ref.end() ? -1 : *it)); }                                                              // ② 임의 키의 후계자 (트리에 없어도)
        long total = 0; int u = t.minNode(); std::vector<int> walk; while (u >= 0) { walk.push_back(t.key[u]); u = t.succWithParent(u, total); } assert(walk == std::vector<int>(ref.begin(), ref.end()) && total <= 2L * (long)t.key.size());                    // ③ 전체 순회 걸음 ≤ 2n
    }
    { const int n = 1000000; BST t; t.key.resize(n); t.L.assign(n, -1); t.R.assign(n, -1); t.P.assign(n, -1); std::iota(t.key.begin(), t.key.end(), 0); t.root = n - 1; for (int i = n - 1; i > 0; --i) { t.L[i] = i - 1; t.P[i - 1] = i; }    // ④ 왼쪽 사슬 (키 0 이 가장 깊다)
      long total = 0; int u = t.minNode(); int count = 0; while (u >= 0) { ++count; u = t.succWithParent(u, total); } assert(count == n && total <= 2L * n);
      std::cout << "Successor: parent-pointer and parent-free successors matched std::set::upper_bound on 1000 random trees (including keys absent from the tree); iterating successors visited every key in order using at most 2n steps, even on a 10^6-deep left chain (" << total << " steps)" << std::endl; }
    return 0;
}
// Time Complexity: 한 번 O(h), n 번 반복하면 총 O(n)
// Space Complexity: O(1)
```
## Predecessor()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 중위 선행자(predecessor): 정렬 순서에서 바로 앞 키 — Successor 의 거울상.  규칙: 왼쪽 자식이 있으면 *왼쪽 부분 트리의 가장 오른쪽*, 없으면 *오른쪽 자식 쪽으로 올라온 첫 조상*.
//  ① 부모 포인터 버전  ② 부모 없는 버전(k 미만 중 최대, 트리에 없는 키도 가능) — std::set 의 lower_bound 바로 앞 원소와 대조  ③ 최댓값에서 시작해 선행자를 반복하면 내림차순 전체, 걸음 ≤ 2n
//  ④ Successor 와의 쌍대성: succ(pred(x)) = x (경계 제외) 와 pred(succ(x)) = x — 모든 노드에서.   ⑤ 삭제 시 선행자 대체(Hibbard 의 대칭형)가 BST 성질을 보존: 두 자식 노드의 키를 선행자 키로 바꾸고 선행자를 지워도 정렬 순서가 유지됨.
struct BST {
    std::vector<int> key, L, R, P; int root = -1;
    void insert(int k) { int parent = -1, u = root; bool left = false; while (u >= 0) { parent = u; if (k == key[u]) return; left = k < key[u]; u = left ? L[u] : R[u]; } key.push_back(k); L.push_back(-1); R.push_back(-1); P.push_back(parent); int c = (int)key.size() - 1; if (parent < 0) root = c; else (left ? L[parent] : R[parent]) = c; }
    int predWithParent(int u, long& steps) const { if (L[u] >= 0) { u = L[u]; ++steps; while (R[u] >= 0) { u = R[u]; ++steps; } return u; } int p = P[u]; ++steps; while (p >= 0 && L[p] == u) { u = p; p = P[p]; ++steps; } return p; }
    int predSucc(int u, bool wantSucc, long& steps) const { if (wantSucc) { if (R[u] >= 0) { u = R[u]; ++steps; while (L[u] >= 0) { u = L[u]; ++steps; } return u; } int p = P[u]; ++steps; while (p >= 0 && R[p] == u) { u = p; p = P[p]; ++steps; } return p; } return predWithParent(u, steps); }
    int lowerNeighbor(int k) const { int best = -1, u = root; while (u >= 0) { if (key[u] < k) { best = key[u]; u = R[u]; } else u = L[u]; } return best; }                                                          // k 미만 중 최대 (없으면 −1)
    int maxNode() const { int u = root; while (R[u] >= 0) u = R[u]; return u; }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(key[u]); u = R[u]; } return out; }
};

int main() {
    std::mt19937 rng(43);
    for (int round = 0; round < 1000; ++round) {
        BST t; std::set<int> ref; int n = 1 + (int)(rng() % 120); for (int i = 0; i < n; ++i) { int k = (int)(rng() % 400); t.insert(k); ref.insert(k); }
        for (size_t u = 0; u < t.key.size(); ++u) { long steps = 0; int p = t.predWithParent((int)u, steps); auto it = ref.lower_bound(t.key[u]); assert((p < 0) == (it == ref.begin()) && (p < 0 || t.key[p] == *std::prev(it)));                         // ①
            long s2 = 0; int s = t.predSucc((int)u, true, s2); if (p >= 0) assert(t.predSucc(p, true, s2) == (int)u); if (s >= 0) assert(t.predWithParent(s, s2) == (int)u); }                                                          // ④ succ(pred(x)) = x, pred(succ(x)) = x
        for (int q = 0; q < 50; ++q) { int k = (int)(rng() % 420); auto it = ref.lower_bound(k); assert(t.lowerNeighbor(k) == (it == ref.begin() ? -1 : *std::prev(it))); }                                                         // ②
        long total = 0; int u = t.maxNode(); std::vector<int> walk; while (u >= 0) { walk.push_back(t.key[u]); u = t.predWithParent(u, total); } std::reverse(walk.begin(), walk.end()); assert(walk == std::vector<int>(ref.begin(), ref.end()) && total <= 2L * (long)t.key.size());                    // ③
    }
    for (int round = 0; round < 500; ++round) {                                                                  // ⑤ 선행자 대체 삭제
        BST t; std::set<int> ref; for (int i = 0; i < 60; ++i) { int k = (int)(rng() % 200); t.insert(k); ref.insert(k); }
        for (size_t u = 0; u < t.key.size(); ++u) if (t.L[u] >= 0 && t.R[u] >= 0) { BST c = t; long s = 0; int p = c.predWithParent((int)u, s); int pk = c.key[p]; c.key[u] = pk;                                    // 키를 선행자 것으로 바꾼 뒤 선행자 노드를 떼어 낸다 (오른쪽 자식이 없다)
              int child = c.L[p]; int par = c.P[p]; if (par == (int)u) c.L[par] = child; else c.R[par] = child; if (child >= 0) c.P[child] = par; std::vector<int> in = c.inorder(); std::vector<int> want(ref.begin(), ref.end()); want.erase(std::find(want.begin(), want.end(), t.key[u]));
              assert(in == want); break; }
    }
    { const int n = 1000000; BST t; t.key.resize(n); t.L.assign(n, -1); t.R.assign(n, -1); t.P.assign(n, -1); std::iota(t.key.begin(), t.key.end(), 0); t.root = 0; for (int i = 0; i + 1 < n; ++i) { t.R[i] = i + 1; t.P[i + 1] = i; } long total = 0; int u = t.maxNode(); int count = 0; while (u >= 0) { ++count; u = t.predWithParent(u, total); } assert(count == n && total <= 2L * n);
      std::cout << "Predecessor: parent-pointer and parent-free predecessors matched std::set (including absent keys); succ(pred(x)) = x and pred(succ(x)) = x held for every node; descending iteration cost at most 2n steps (10^6-deep right chain: " << total << "); predecessor-replacement deletion preserved the sorted order" << std::endl; }
    return 0;
}
// Time Complexity: 한 번 O(h), n 번 반복하면 총 O(n)
// Space Complexity: O(1)
```
## ValidateBST()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <numeric>
#include <optional>
#include <random>
#include <string>
#include <vector>

// BST 검증: "각 노드가 자기 자식과만 맞는다(왼쪽 < 루트 < 오른쪽)" 는 *부족하다* — 오른쪽 부분 트리의 왼쪽 자식이 루트보다 작을 수 있다.  올바른 판정 세 가지:
//  ① 위/아래 한계(상한·하한)를 내려보내며 확인  ② 중위 순회가 엄격히 증가하는지  ③ 모든 (조상, 후손) 쌍을 직접 확인하는 O(n·h) 브루트포스.
//  전수 검증: 모양 C(n) 가지 × 값 n! 가지(n ≤ 6)에서 세 판정이 항상 같고, BST 인 배치는 모양마다 *정확히 하나*(중위 순서대로 번호) — 총 C(n) 개.  국소 판정이 틀리는 트리를 센다.
//  경계: 키가 INT_MIN / INT_MAX 인 노드 — int 센티널 한계(INT_MIN, INT_MAX)를 쓰면 정상 BST 를 거부한다 → long long 또는 "한계 없음" 으로 표현.  중복 키는 정책(엄격 vs 허용)을 명시.  깊이 10^6 사슬을 반복문으로.
struct BT { std::vector<int> key, L, R; int root = -1; int add(int k) { key.push_back(k); L.push_back(-1); R.push_back(-1); return (int)key.size() - 1; } };
bool validBounds(const BT& t) {                                                                                  // 한계를 내려보내는 반복 DFS: long long 한계 (INT_MIN/INT_MAX 키도 안전)
    struct F { int u; long long lo, hi; }; std::vector<F> st; if (t.root >= 0) st.push_back({t.root, LLONG_MIN, LLONG_MAX});
    while (!st.empty()) { F f = st.back(); st.pop_back(); if (t.key[f.u] <= f.lo || t.key[f.u] >= f.hi) return false; if (t.L[f.u] >= 0) st.push_back({t.L[f.u], f.lo, t.key[f.u]}); if (t.R[f.u] >= 0) st.push_back({t.R[f.u], t.key[f.u], f.hi}); }
    return true;
}
bool validBoundsInt(const BT& t) {                                                                               // 흔한 실수: int 한계 센티널
    struct F { int u; int lo, hi; }; std::vector<F> st; if (t.root >= 0) st.push_back({t.root, INT_MIN, INT_MAX});
    while (!st.empty()) { F f = st.back(); st.pop_back(); if (t.key[f.u] <= f.lo || t.key[f.u] >= f.hi) return false; if (t.L[f.u] >= 0) st.push_back({t.L[f.u], f.lo, t.key[f.u]}); if (t.R[f.u] >= 0) st.push_back({t.R[f.u], t.key[f.u], f.hi}); }
    return true;
}
bool validInorder(const BT& t) { std::optional<int> prev; std::vector<int> st; int u = t.root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = t.L[u]; } u = st.back(); st.pop_back(); if (prev && *prev >= t.key[u]) return false; prev = t.key[u]; u = t.R[u]; } return true; }
bool validLocal(const BT& t) { for (size_t u = 0; u < t.key.size(); ++u) { if (t.L[u] >= 0 && t.key[t.L[u]] >= t.key[u]) return false; if (t.R[u] >= 0 && t.key[t.R[u]] <= t.key[u]) return false; } return true; }          // 틀린 판정: 부모–자식만 비교
bool validBrute(const BT& t) { for (size_t a = 0; a < t.key.size(); ++a) { if (t.L[a] >= 0) { std::vector<int> st = {t.L[a]}; while (!st.empty()) { int x = st.back(); st.pop_back(); if (t.key[x] >= t.key[a]) return false; if (t.L[x] >= 0) st.push_back(t.L[x]); if (t.R[x] >= 0) st.push_back(t.R[x]); } }
        if (t.R[a] >= 0) { std::vector<int> st = {t.R[a]}; while (!st.empty()) { int x = st.back(); st.pop_back(); if (t.key[x] <= t.key[a]) return false; if (t.L[x] >= 0) st.push_back(t.L[x]); if (t.R[x] >= 0) st.push_back(t.R[x]); } } } return true; }
// 모양 열거 (값은 나중에 배정): 노드 번호는 전위 순서
struct Shape { std::vector<int> L, R; };
void shapes(int n, std::vector<Shape>& out) { if (n == 0) { out.push_back({}); return; } for (int l = 0; l < n; ++l) { std::vector<Shape> a, b; shapes(l, a); shapes(n - 1 - l, b); for (auto& x : a) for (auto& y : b) { Shape s; s.L.assign(n, -1); s.R.assign(n, -1); int offX = 1, offY = 1 + l; for (int i = 0; i < l; ++i) { s.L[offX + i] = x.L[i] >= 0 ? x.L[i] + offX : -1; s.R[offX + i] = x.R[i] >= 0 ? x.R[i] + offX : -1; } for (int i = 0; i < n - 1 - l; ++i) { s.L[offY + i] = y.L[i] >= 0 ? y.L[i] + offY : -1; s.R[offY + i] = y.R[i] >= 0 ? y.R[i] + offY : -1; } if (l > 0) s.L[0] = offX; if (n - 1 - l > 0) s.R[0] = offY; out.push_back(s); } } }

int main() {
    { BT t; int r = t.add(10), a = t.add(5), b = t.add(15); t.root = r; t.L[r] = a; t.R[r] = b; assert(validBounds(t) && validInorder(t) && validBrute(t) && validLocal(t)); }
    { BT t; int r = t.add(10), a = t.add(5), b = t.add(15), c = t.add(6); t.root = r; t.L[r] = a; t.R[r] = b; t.L[b] = c; /* 15 의 왼쪽에 6: 국소로는 맞지만 루트 10 보다 작다 */ assert(validLocal(t) && !validBounds(t) && !validInorder(t) && !validBrute(t)); }
    long catalan[] = {1, 1, 2, 5, 14, 42, 132};
    for (int n = 1; n <= 6; ++n) {
        std::vector<Shape> all; shapes(n, all); assert((long)all.size() == catalan[n]); long validCount = 0, localOnly = 0; std::vector<int> perm(n);
        for (auto& sh : all) { std::iota(perm.begin(), perm.end(), 1); do { BT t; for (int i = 0; i < n; ++i) t.add(perm[i]); t.L = sh.L; t.R = sh.R; t.root = 0; bool a = validBounds(t), b = validInorder(t), c = validBrute(t); assert(a == b && b == c); validCount += a; localOnly += validLocal(t) && !a; } while (std::next_permutation(perm.begin(), perm.end())); }
        assert(validCount == catalan[n]); if (n >= 3) assert(localOnly > 0);                                                                                // 모양마다 BST 배치는 정확히 하나, 국소 판정만 통과하는 가짜 BST 가 존재
    }
    { BT t; int r = t.add(INT_MAX), l = t.add(INT_MIN); t.root = r; t.L[r] = l; assert(validBounds(t) && validInorder(t) && !validBoundsInt(t));                               // 정상 BST 인데 int 센티널 판정은 거부한다
      BT dup; int r2 = dup.add(5), l2 = dup.add(5); dup.root = r2; dup.L[r2] = l2; assert(!validBounds(dup) && !validInorder(dup)); }                                                 // 중복 키: 이 구현은 엄격한 BST 만 인정
    std::mt19937 rng(7);
    for (int it = 0; it < 2000; ++it) {                                                                          // 무작위 BST, 그리고 값 두 개를 바꾼 것
        int n = 2 + (int)(rng() % 30); BT t; std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); t.root = t.add(keys[0]); for (int i = 1; i < n; ++i) { int c = t.add(keys[i]); int u = t.root; while (true) { int& nx = keys[i] < t.key[u] ? t.L[u] : t.R[u]; if (nx < 0) { nx = c; break; } u = nx; } }
        assert(validBounds(t) && validInorder(t) && validBrute(t)); int a = (int)(rng() % n), b = (int)(rng() % n); std::swap(t.key[a], t.key[b]); bool v1 = validBounds(t), v2 = validInorder(t), v3 = validBrute(t); assert(v1 == v2 && v2 == v3);
    }
    { const int n = 1000000; BT t; t.root = t.add(0); int cur = t.root; for (int i = 1; i < n; ++i) { int c = t.add(i); t.R[cur] = c; cur = c; } assert(validBounds(t) && validInorder(t)); t.key[n / 2] = -5; assert(!validBounds(t) && !validInorder(t));
      std::cout << "ValidateBST: bounds, in-order and brute-force validators agreed on every labelled shape with n <= 6 (exactly Catalan(n) valid labellings, plus parent-child-only checks that wrongly accept some); INT_MIN/INT_MAX keys exposed the int-sentinel bug; a depth-10^6 chain was validated iteratively" << std::endl; }
    return 0;
}
// Time Complexity: 한계 방식·중위 방식 O(n), 브루트포스 O(n·h)
// Space Complexity: O(h)
```

# Part 6. AVL 트리
## AVLInsert()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// AVL 삽입: 보통의 BST 삽입 뒤 *돌아오는 길*에 각 조상에서 높이를 갱신하고 |bf| = 2 이면 단일(LL·RR)·이중(LR·RL) 회전으로 바로잡는다.  핵심 사실 두 가지를 검증한다:
//  ① 삽입 한 번에 재균형은 *최대 한 번*(회전 한 번 또는 이중 회전 한 번) — 고치고 나면 부분 트리 높이가 삽입 전과 같아져 위쪽은 변하지 않는다  ② 높이 < 1.4405·log2(n + 2) − 0.3277 (+1: 노드 수 기준) — 오름차순 100 만 개를 넣어도 일반 BST 처럼 사슬이 되지 않는다.
//  전수 확인: 키 n ≤ 8 개의 *모든 삽입 순서*(n! 가지)에서 각 삽입 뒤 불변식이 성립하고, 오름차순 2^k − 1 개를 넣으면 높이 k 의 완전 이진 트리가 된다.  무작위 삽입(중복 포함)은 std::set 과 내용이 같고 매 삽입 뒤 불변식을 검증한다.
struct Avl {
    std::vector<int> key, h, L, R, freeList; int root = -1; size_t cnt = 0; long fixes = 0;                       // fixes = 재균형(단일·이중 회전)을 한 노드 수
    int H(int u) const { return u < 0 ? 0 : h[u]; }
    int newNode(int k) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); key[u] = k; h[u] = 1; L[u] = R[u] = -1; } else { key.push_back(k); h.push_back(1); L.push_back(-1); R.push_back(-1); u = (int)key.size() - 1; } return u; }
    void upd(int u) { h[u] = 1 + std::max(H(L[u]), H(R[u])); }
    int rotR(int y) { int x = L[y]; L[y] = R[x]; R[x] = y; upd(y); upd(x); return x; }
    int rotL(int x) { int y = R[x]; R[x] = L[y]; L[y] = x; upd(x); upd(y); return y; }
    int fix(int u) { upd(u); int b = H(L[u]) - H(R[u]);                                                          // 한 노드를 바로잡고 새 부분 트리 루트를 돌려준다
        if (b > 1) { if (H(L[L[u]]) < H(R[L[u]])) L[u] = rotL(L[u]); ++fixes; return rotR(u); }                  // LL: 오른쪽 회전, LR: 왼쪽-오른쪽
        if (b < -1) { if (H(R[R[u]]) < H(L[R[u]])) R[u] = rotR(R[u]); ++fixes; return rotL(u); }                 // RR: 왼쪽 회전, RL: 오른쪽-왼쪽
        return u; }
    int ins(int u, int k, bool& added) { if (u < 0) { added = true; ++cnt; return newNode(k); } if (k < key[u]) { int c = ins(L[u], k, added); L[u] = c; } else if (k > key[u]) { int c = ins(R[u], k, added); R[u] = c; } else return u; return fix(u); }
    bool insert(int k) { bool added = false; root = ins(root, k, added); return added; }
    bool contains(int k) const { int u = root; while (u >= 0 && key[u] != k) u = k < key[u] ? L[u] : R[u]; return u >= 0; }
    int check(int u, long long lo, long long hi, size_t& seen) const {                                           // 불변식: BST 순서·저장 높이·|bf| ≤ 1 (재귀 깊이 ≤ 1.44 log n)
        if (u < 0) return 0; assert(key[u] > lo && key[u] < hi); ++seen; int hl = check(L[u], lo, key[u], seen), hr = check(R[u], key[u], hi, seen);
        assert(std::abs(hl - hr) <= 1 && h[u] == 1 + std::max(hl, hr)); return h[u]; }
    void validate() const { size_t seen = 0; check(root, -(1LL << 40), 1LL << 40, seen); assert(seen == cnt); }
    void inorder(int u, std::vector<int>& out) const { if (u < 0) return; inorder(L[u], out); out.push_back(key[u]); inorder(R[u], out); }
    std::string shape(int u) const { return u < 0 ? "." : "(" + shape(L[u]) + shape(R[u]) + ")"; }
};

int main() {
    // 전수: 모든 삽입 순서에서 불변식·삽입당 재균형 ≤ 1
    for (int n = 1; n <= 8; ++n) {
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::set<std::string> shapes; long perms = 0;
        do { Avl t; for (int k : perm) { long before = t.fixes; bool added = t.insert(k); assert(added); assert(t.fixes - before <= 1); t.validate(); } ++perms; shapes.insert(t.shape(t.root)); std::vector<int> in; t.inorder(t.root, in); assert((int)in.size() == n && std::is_sorted(in.begin(), in.end())); } while (std::next_permutation(perm.begin(), perm.end()));
        const size_t avlShapes[] = {0, 1, 2, 1, 4, 6, 4, 17, 32}; assert(shapes.size() <= avlShapes[n]);          // 가능한 AVL 모양 수(1,1,2,1,4,6,4,17,32)를 넘지 않는다
    }
    // 오름차순 2^k − 1 개 → 완전 이진 트리
    for (int k = 1; k <= 16; ++k) { Avl t; int n = (1 << k) - 1; for (int i = 1; i <= n; ++i) t.insert(i); t.validate(); assert(t.h[t.root] == k && (int)t.cnt == n); }
    // 대규모: 오름차순·내림차순 100 만, 중간에서 양쪽으로 퍼지는 순서
    const double a = 1.4405, b = 0.3277;
    for (int mode = 0; mode < 3; ++mode) {
        Avl t; const int n = 1000000; long maxStep = 0;
        for (int i = 0; i < n; ++i) { int k = mode == 0 ? i : mode == 1 ? n - i : (i % 2 ? n / 2 + i / 2 : n / 2 - i / 2); long before = t.fixes; t.insert(k); maxStep = std::max(maxStep, t.fixes - before); }
        t.validate(); double hbound = a * std::log2((double)t.cnt + 2) - b + 1; assert(t.h[t.root] <= hbound && t.h[t.root] >= (int)std::ceil(std::log2((double)t.cnt + 1)) && maxStep <= 1);
        assert((long)t.fixes <= (long)t.cnt);                                                                     // 총 재균형 ≤ 삽입 수
    }
    // 무작위(중복 포함) vs std::set
    std::mt19937 rng(5); Avl t; std::set<int> ref; long maxFix = 0, dup = 0;
    for (int step = 0; step < 200000; ++step) { int k = (int)(rng() % 300000); long before = t.fixes; bool added = t.insert(k); bool refAdded = ref.insert(k).second; assert(added == refAdded); dup += !added; maxFix = std::max(maxFix, t.fixes - before);
        if (step < 300 || step % 997 == 0) t.validate(); }
    t.validate(); std::vector<int> in; t.inorder(t.root, in); assert(in == std::vector<int>(ref.begin(), ref.end()) && maxFix <= 1 && dup > 0);
    for (int k = 0; k < 300000; k += 777) assert(t.contains(k) == (ref.count(k) > 0));
    std::cout << "AVLInsert: every insertion order of up to 8 keys kept the AVL invariants with at most one rebalance per insert; ascending 2^k-1 keys gave perfect trees; 10^6 ascending/descending/zig-zag inserts stayed within 1.44*log2(n); 2*10^5 random inserts (with " << dup << " duplicates) matched std::set" << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(N) (재귀 깊이 O(log N))
```
## AVLDelete()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// AVL 삭제: 삭제할 노드가 자식 둘이면 오른쪽 부분 트리의 최솟값 노드를 떼어 그 자리에 끼우고(키를 복사하지 않고 노드를 옮긴다), 돌아오는 길의 모든 조상에서 재균형한다.
//  삽입과 달리 *한 번 고쳐도 부분 트리 높이가 1 줄 수 있어* 위쪽 조상이 연쇄적으로 불균형해진다 — 재균형이 O(log N) 번 필요할 수 있다.  최악 사례: 높이 h 인 피보나치(최소 노드) 트리에서 최댓값을 지우면 정확히 ⌊(h − 1)/2⌋ 번 재균형(h = 2..24 확인).
//  전수 확인: 키 7 개의 서로 다른 AVL 모양(삽입 순서 전수에서 얻은 것) × 모든 삭제 순서(5040 가지)에서 각 단계 뒤 불변식·std::set 내용 일치.  대규모: 무작위 삽입·삭제 100 만 연산(살아 있는 키 최대 10^5)을 std::set 과 대조하고 노드 재사용(arena 크기 ≤ 최대 동시 노드 수)을 확인.
struct Avl {
    std::vector<int> key, h, L, R, freeList; int root = -1; size_t cnt = 0; long fixes = 0;                       // fixes = 재균형(단일·이중 회전)을 한 노드 수
    int H(int u) const { return u < 0 ? 0 : h[u]; }
    int newNode(int k) { int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); key[u] = k; h[u] = 1; L[u] = R[u] = -1; } else { key.push_back(k); h.push_back(1); L.push_back(-1); R.push_back(-1); u = (int)key.size() - 1; } return u; }
    void upd(int u) { h[u] = 1 + std::max(H(L[u]), H(R[u])); }
    int rotR(int y) { int x = L[y]; L[y] = R[x]; R[x] = y; upd(y); upd(x); return x; }
    int rotL(int x) { int y = R[x]; R[x] = L[y]; L[y] = x; upd(x); upd(y); return y; }
    int fix(int u) { upd(u); int b = H(L[u]) - H(R[u]);                                                          // 한 노드를 바로잡고 새 부분 트리 루트를 돌려준다
        if (b > 1) { if (H(L[L[u]]) < H(R[L[u]])) L[u] = rotL(L[u]); ++fixes; return rotR(u); }                  // LL: 오른쪽 회전, LR: 왼쪽-오른쪽
        if (b < -1) { if (H(R[R[u]]) < H(L[R[u]])) R[u] = rotR(R[u]); ++fixes; return rotL(u); }                 // RR: 왼쪽 회전, RL: 오른쪽-왼쪽
        return u; }
    int ins(int u, int k, bool& added) { if (u < 0) { added = true; ++cnt; return newNode(k); } if (k < key[u]) { int c = ins(L[u], k, added); L[u] = c; } else if (k > key[u]) { int c = ins(R[u], k, added); R[u] = c; } else return u; return fix(u); }
    bool insert(int k) { bool added = false; root = ins(root, k, added); return added; }
    bool contains(int k) const { int u = root; while (u >= 0 && key[u] != k) u = k < key[u] ? L[u] : R[u]; return u >= 0; }
    int check(int u, long long lo, long long hi, size_t& seen) const {                                           // 불변식: BST 순서·저장 높이·|bf| ≤ 1 (재귀 깊이 ≤ 1.44 log n)
        if (u < 0) return 0; assert(key[u] > lo && key[u] < hi); ++seen; int hl = check(L[u], lo, key[u], seen), hr = check(R[u], key[u], hi, seen);
        assert(std::abs(hl - hr) <= 1 && h[u] == 1 + std::max(hl, hr)); return h[u]; }
    void validate() const { size_t seen = 0; check(root, -(1LL << 40), 1LL << 40, seen); assert(seen == cnt); }
    void inorder(int u, std::vector<int>& out) const { if (u < 0) return; inorder(L[u], out); out.push_back(key[u]); inorder(R[u], out); }
    std::string shape(int u) const { return u < 0 ? "." : "(" + shape(L[u]) + shape(R[u]) + ")"; }

    int takeMin(int u, int& m) { if (L[u] < 0) { m = u; return R[u]; } int c = takeMin(L[u], m); L[u] = c; return fix(u); }          // 최소 노드 m 을 떼고 새 루트를 돌려준다
    int del(int u, int k, bool& gone) { if (u < 0) return -1;
        if (k < key[u]) { int c = del(L[u], k, gone); L[u] = c; } else if (k > key[u]) { int c = del(R[u], k, gone); R[u] = c; }
        else { gone = true; int l = L[u], r = R[u]; freeList.push_back(u); --cnt; if (l < 0) return r; if (r < 0) return l; int m = -1; int nr = takeMin(r, m); L[m] = l; R[m] = nr; return fix(m); }
        return fix(u); }
    bool erase(int k) { bool gone = false; root = del(root, k, gone); return gone; }
    int fibTree(int hh, int& nextKey) { if (hh <= 0) return -1; int l = fibTree(hh - 1, nextKey); int u = newNode(nextKey++); int r = fibTree(hh - 2, nextKey); L[u] = l; R[u] = r; upd(u); ++cnt; return u; }   // 왼쪽 T(h−1), 오른쪽 T(h−2)
};

int main() {
    // 최악 사례: 피보나치 트리에서 최댓값 삭제 → ⌊(h−1)/2⌋ 번 재균형 (삽입은 최대 1 번)
    for (int hh = 2; hh <= 24; ++hh) { Avl t; int nk = 0; t.root = t.fibTree(hh, nk); t.validate(); assert(t.h[t.root] == hh); long before = t.fixes; bool gone = t.erase(nk - 1); assert(gone); t.validate(); assert(t.fixes - before == (hh - 1) / 2); }
    // 전수: 서로 다른 AVL 모양 × 모든 삭제 순서
    { const int n = 7; std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::set<std::string> seen; std::vector<std::vector<int>> reps;
      do { Avl t; for (int k : perm) t.insert(k); if (seen.insert(t.shape(t.root)).second) reps.push_back(perm); } while (std::next_permutation(perm.begin(), perm.end())); assert(reps.size() >= 4);
      long sequences = 0;
      for (auto& rep : reps) { std::vector<int> order(n); std::iota(order.begin(), order.end(), 0);
        do { Avl t; for (int k : rep) t.insert(k); std::set<int> ref(rep.begin(), rep.end());
             for (int k : order) { bool gone = t.erase(k); bool rg = ref.erase(k) > 0; assert(gone == rg); t.validate(); std::vector<int> in; t.inorder(t.root, in); assert(in == std::vector<int>(ref.begin(), ref.end())); }
             assert(t.root < 0 && t.cnt == 0); ++sequences; } while (std::next_permutation(order.begin(), order.end())); }
      assert(sequences == (long)reps.size() * 5040); }
    // 없는 키 삭제는 아무 변화 없음
    { Avl t; for (int k = 0; k < 100; k += 2) t.insert(k); long f = t.fixes; size_t c = t.cnt; for (int k = 1; k < 100; k += 2) assert(!t.erase(k)); assert(t.cnt == c && t.fixes == f); t.validate(); }
    // 대규모 무작위 삽입·삭제
    std::mt19937 rng(8); Avl t; std::set<int> ref; size_t maxLive = 0; long maxDelFix = 0;
    for (long step = 0; step < 1000000; ++step) {
        int k = (int)(rng() % 200000); bool wantInsert = ref.size() < 100000 ? rng() % 100 < 55 : rng() % 100 < 45;
        if (wantInsert) { bool a = t.insert(k); bool r = ref.insert(k).second; assert(a == r); }
        else { long before = t.fixes; bool a = t.erase(k); bool r = ref.erase(k) > 0; assert(a == r); maxDelFix = std::max(maxDelFix, t.fixes - before); }
        maxLive = std::max(maxLive, ref.size()); assert(t.cnt == ref.size());
        if (step % 25000 == 0) t.validate();
    }
    t.validate(); std::vector<int> in; t.inorder(t.root, in); assert(in == std::vector<int>(ref.begin(), ref.end()));
    assert(t.key.size() <= maxLive + 1 && t.h[t.root] <= 1.4405 * std::log2((double)t.cnt + 2) + 0.6723);        // 노드가 재사용되어 arena 가 최대 동시 노드 수를 넘지 않는다, 높이 한계 유지
    std::vector<int> all(ref.begin(), ref.end()); std::shuffle(all.begin(), all.end(), rng); for (int k : all) { bool g = t.erase(k); assert(g); } assert(t.root < 0 && t.cnt == 0);                  // 전부 지우기
    std::cout << "AVLDelete: Fibonacci worst case needed floor((h-1)/2) rebalances for h=2..24; all deletion orders of 7-key AVL shapes kept the invariants; 10^6 random insert/delete operations matched std::set (largest rebalance run in one delete: " << maxDelFix << ") and the arena reused freed nodes" << std::endl;
    return 0;
}
// Time Complexity: O(log N) (재균형은 최대 O(log N) 번)
// Space Complexity: O(N) (재귀 깊이 O(log N))
```
## BalanceFactor()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 균형 인수(balance factor) bf(u) = 높이(왼쪽 부분 트리) − 높이(오른쪽 부분 트리) (빈 트리 높이 0, 노드 수 기준).  AVL 트리 = 모든 노드에서 |bf| ≤ 1 인 BST.
//  ① 모양 전수 확인: 키 n ≤ 8 개의 모든 삽입 순서가 만드는 BST 모양 중 AVL 인 것의 수가 독립적인 점화식 A(n,h) = Σ A(k,h−1)·[A(n−1−k,h−1) + A(n−1−k,h−2)] + A(k,h−2)·A(n−1−k,h−1) 와 같다  (1, 1, 2, 1, 4, 6, 4, 17, 32)
//  ② 높이 h 인 AVL 트리의 최소 노드 수 = 피보나치형 N(h) = N(h−1) + N(h−2) + 1, 최대 = 2^h − 1 (DP 로 확인), 피보나치 트리는 높이 ≥ 2 인 모든 노드가 bf = +1, 완전 이진 트리는 전부 0, 사슬의 루트는 bf = n
//  ③ 되짚기(retrace) 근거: 잎 하나를 달면 높이가 변하는 노드는 새 잎의 조상 사슬의 *앞부분*뿐이고(한 번 안 변하면 그 위는 모두 불변), bf 가 달라질 수 있는 것도 조상뿐이다  ④ 100 만 노드 사슬도 반복 계산으로 처리.
struct BT {
    std::vector<int> key, L, R; int root = -1;
    int add(int k) { key.push_back(k); L.push_back(-1); R.push_back(-1); return (int)key.size() - 1; }
    std::vector<int> heights() const {                                                                              // 높이(노드 수 기준): BFS 순서를 뒤집어 반복 계산
        std::vector<int> h(L.size(), 0), order; if (root < 0) return h; order.push_back(root);
        for (size_t i = 0; i < order.size(); ++i) { int u = order[i]; if (L[u] >= 0) order.push_back(L[u]); if (R[u] >= 0) order.push_back(R[u]); }
        for (size_t i = order.size(); i-- > 0;) { int u = order[i]; h[u] = 1 + std::max(L[u] >= 0 ? h[L[u]] : 0, R[u] >= 0 ? h[R[u]] : 0); }
        return h; }
    int bf(const std::vector<int>& h, int u) const { return (L[u] >= 0 ? h[L[u]] : 0) - (R[u] >= 0 ? h[R[u]] : 0); }
    bool isAvl() const { std::vector<int> h = heights(); for (size_t u = 0; u < L.size(); ++u) if (std::abs(bf(h, (int)u)) > 1) return false; return true; }
    std::string shape(int u) const { return u < 0 ? "." : "(" + shape(L[u]) + shape(R[u]) + ")"; }                  // 작은 트리 전용(재귀)
    void insertKey(int k) { int v = add(k); if (root < 0) { root = v; return; } int u = root; while (true) { int& nx = k < key[u] ? L[u] : R[u]; if (nx < 0) { nx = v; return; } u = nx; } }
};
int fibTree(BT& t, int h, int& nextKey) { if (h <= 0) return -1; int l = fibTree(t, h - 1, nextKey); int u = t.add(nextKey++); int r = fibTree(t, h - 2, nextKey); t.L[u] = l; t.R[u] = r; return u; }   // 왼쪽 T(h−1), 오른쪽 T(h−2)
int perfectTree(BT& t, int h, int& nextKey) { if (h <= 0) return -1; int l = perfectTree(t, h - 1, nextKey); int u = t.add(nextKey++); int r = perfectTree(t, h - 1, nextKey); t.L[u] = l; t.R[u] = r; return u; }

int main() {
    // ② 독립적인 점화식: A[n][h] = 노드 n 개, 높이 h 인 AVL 모양의 수
    const int NMAX = 64, HMAX = 8; static long long A[NMAX + 1][HMAX + 1]; A[0][0] = 1;
    for (int n = 1; n <= NMAX; ++n) for (int h = 1; h <= HMAX; ++h) { long long s = 0; for (int k = 0; k < n; ++k) { int m = n - 1 - k; s += A[k][h - 1] * A[m][h - 1]; if (h >= 2) s += A[k][h - 1] * A[m][h - 2] + A[k][h - 2] * A[m][h - 1]; } A[n][h] = s; }
    long long expect[] = {1, 1, 2, 1, 4, 6, 4, 17, 32};
    for (int n = 0; n <= 8; ++n) { long long tot = 0; for (int h = 0; h <= HMAX; ++h) tot += A[n][h]; assert(tot == expect[n]); }
    // ① 모든 삽입 순서 → 모양 → AVL 판정
    for (int n = 1; n <= 8; ++n) {
        std::set<std::string> avl, all; std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0);
        do { BT t; for (int k : perm) t.insertKey(k); std::string s = t.shape(t.root); all.insert(s); if (t.isAvl()) avl.insert(s); } while (std::next_permutation(perm.begin(), perm.end()));
        const long catalan[] = {1, 1, 2, 5, 14, 42, 132, 429, 1430}; assert((long)all.size() == catalan[n] && (long long)avl.size() == expect[n]);
    }
    int N[HMAX + 2]; N[0] = 0; N[1] = 1; for (int h = 2; h <= HMAX; ++h) N[h] = N[h - 1] + N[h - 2] + 1;                    // N: 0, 1, 2, 4, 7, 12, 20, 33
    for (int h = 1; h <= 6; ++h) { int mn = -1, mx = -1; for (int n = 1; n <= NMAX; ++n) if (A[n][h] > 0) { if (mn < 0) mn = n; mx = n; } assert(mn == N[h] && mx == (1 << h) - 1); }          // 최소·최대 노드 수
    std::vector<long> fibN(20, 0); fibN[1] = 1; for (int h = 2; h < 20; ++h) fibN[h] = fibN[h - 1] + fibN[h - 2] + 1;
    for (int h = 1; h <= 18; ++h) {
        BT f; int k = 0; f.root = fibTree(f, h, k); std::vector<int> hh = f.heights(); assert((long)f.key.size() == fibN[h]);                      // 노드 수 = N(h)
        assert(hh[f.root] == h && f.isAvl()); for (size_t u = 0; u < f.L.size(); ++u) assert(f.bf(hh, (int)u) == (hh[u] >= 2 ? 1 : 0));          // 높이 ≥ 2 → bf = +1
        BT pf; int k2 = 0; pf.root = perfectTree(pf, h, k2); std::vector<int> ph = pf.heights(); assert((int)pf.key.size() == (1 << h) - 1); for (size_t u = 0; u < pf.L.size(); ++u) assert(pf.bf(ph, (int)u) == 0);
    }
    // ③ 되짚기: 무작위 BST 에 잎을 하나 달 때 높이·bf 가 변하는 노드는 조상 사슬의 앞부분
    std::mt19937 rng(11);
    for (int it = 0; it < 300; ++it) {
        BT t; int n = 5 + (int)(rng() % 300); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); for (int k : keys) t.insertKey(k * 2);   // 짝수 키만 → 사이사이에 새 키를 넣을 수 있다
        std::vector<int> h0 = t.heights(); std::vector<int> bf0(t.L.size()); for (size_t u = 0; u < t.L.size(); ++u) bf0[u] = t.bf(h0, (int)u);
        int newKey = 2 * (int)(rng() % n) + 1; t.insertKey(newKey); int leaf = (int)t.key.size() - 1;
        std::vector<int> par(t.key.size(), -1); for (size_t u = 0; u < t.L.size(); ++u) { if (t.L[u] >= 0) par[t.L[u]] = (int)u; if (t.R[u] >= 0) par[t.R[u]] = (int)u; }
        std::vector<int> h1 = t.heights(); std::vector<char> anc(t.key.size(), 0); bool stopped = false;
        for (int u = par[leaf]; u >= 0; u = par[u]) { anc[u] = 1; bool changed = h1[u] != h0[u]; if (stopped) assert(!changed); if (!changed) stopped = true; assert(h1[u] - h0[u] <= 1); }   // 앞부분만 +1, 한 번 안 변하면 위는 모두 불변
        for (size_t u = 0; u + 1 < t.key.size(); ++u) if (!anc[u]) { assert(h1[u] == h0[u] && t.bf(h1, (int)u) == bf0[u]); }
    }
    // ④ 100 만 노드 사슬: 루트 bf = n, AVL 이 아니다
    { BT c; const int n = 1000000; for (int i = 0; i < n; ++i) c.add(i); c.root = 0; for (int i = 0; i + 1 < n; ++i) c.R[i] = i + 1; std::vector<int> h = c.heights(); assert(h[0] == n && c.bf(h, 0) == -(n - 1) && !c.isAvl()); }
    std::cout << "BalanceFactor: AVL shape counts for n <= 8 matched the recurrence (1,1,2,1,4,6,4,17,32), min/max AVL sizes matched Fibonacci and 2^h-1, Fibonacci trees had bf=+1 everywhere above the leaves, and a new leaf changed heights only on a prefix of its ancestors" << std::endl;
    return 0;
}
// Time Complexity: O(1) per node (저장된 높이 사용); 전체 재계산은 O(N)
// Space Complexity: O(N)
```
## RotateLeft()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>

// 왼쪽 회전(rotateLeft(x)): x 의 오른쪽 자식 y 를 올리고 x 를 y 의 왼쪽 자식으로 내린다; y 의 옛 왼쪽 부분 트리는 x 의 오른쪽으로.  *중위 순서를 바꾸지 않는* 국소 변형이라 AVL·레드-블랙·스플레이·트립이 모두 이것으로 균형을 맞춘다.
//  모든 모양을 열거해 전수 확인한다 (키 = 중위 순서 번호, n ≤ 7, 모양은 카탈란 수 C(n) 개): ① 어떤 x 에서 돌려도 중위 순서·BST 성질·부모 링크 유지  ② x 의 깊이 +1, y 의 깊이 −1, y 의 부분 트리 크기 = 옛 x 의 크기, 그 밖의 노드는 깊이가 ±1 이내이고 x 의 부분 트리 바깥은 불변
//  ③ rotateRight(y) 로 정확히 원래 모양으로 복귀  ④ 회전 그래프: 한 모양에서 가능한 회전은 (왼쪽 + 오른쪽) 정확히 n − 1 가지(간선마다 한 번)이고 서로 다른 모양을 만든다 — (n − 1) 정칙 연결 그래프, 오른쪽 사슬 → 왼쪽 사슬의 거리는 n − 1.
struct T {
    int n; std::vector<int> L, R, P; int root;
    explicit T(int nn) : n(nn), L(nn, -1), R(nn, -1), P(nn, -1), root(-1) {}
    void rotateLeft(int x) { int y = R[x]; R[x] = L[y]; if (L[y] >= 0) P[L[y]] = x; P[y] = P[x]; if (P[x] < 0) root = y; else if (L[P[x]] == x) L[P[x]] = y; else R[P[x]] = y; L[y] = x; P[x] = y; }
    void rotateRight(int y) { int x = L[y]; L[y] = R[x]; if (R[x] >= 0) P[R[x]] = y; P[x] = P[y]; if (P[y] < 0) root = x; else if (L[P[y]] == y) L[P[y]] = x; else R[P[y]] = x; R[x] = y; P[y] = x; }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(u); u = R[u]; } return out; }
    int height(int u) const { if (u < 0) return -1; int best = 0; std::vector<std::pair<int, int>> st = {{u, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return best; }
    int bf(int u) const { return height(L[u]) - height(R[u]); }
    bool same(const T& o) const { return root == o.root && L == o.L && R == o.R && P == o.P; }
    bool linksOk() const { if (P[root] != -1) return false; int cnt = 0; std::vector<int> st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); ++cnt; if (L[u] >= 0) { if (P[L[u]] != u || L[u] >= u) return false; st.push_back(L[u]); } if (R[u] >= 0) { if (P[R[u]] != u || R[u] <= u) return false; st.push_back(R[u]); } } return cnt == n; }   // 키 = 번호이므로 왼쪽 자식 < 부모 < 오른쪽 자식
};
T randomBst(int n, std::mt19937& rng) { T t(n); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); t.root = keys[0]; for (int i = 1; i < n; ++i) { int k = keys[i], u = t.root; while (true) { int& nx = k < u ? t.L[u] : t.R[u]; if (nx < 0) { nx = k; t.P[k] = u; break; } u = nx; } } return t; }
T mirrored(const T& t) { int n = t.n; T m(n); m.root = n - 1 - t.root; for (int k = 0; k < n; ++k) { int mk = n - 1 - k; m.L[mk] = t.R[k] >= 0 ? n - 1 - t.R[k] : -1; m.R[mk] = t.L[k] >= 0 ? n - 1 - t.L[k] : -1; m.P[mk] = t.P[k] >= 0 ? n - 1 - t.P[k] : -1; } return m; }   // 키 k → n−1−k, 좌우 교환

std::map<std::string, T> allShapes(int n) {                                                                       // 모든 삽입 순서(n! 가지)를 BST 에 넣어 서로 다른 모양을 모은다
    std::map<std::string, T> res; std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0);
    do { T t(n); t.root = perm[0]; for (int i = 1; i < n; ++i) { int k = perm[i], u = t.root; while (true) { int& nx = k < u ? t.L[u] : t.R[u]; if (nx < 0) { nx = k; t.P[k] = u; break; } u = nx; } }
         std::string code = std::to_string(t.root); for (int i = 0; i < n; ++i) code += "," + std::to_string(t.P[i]); res.emplace(code, t); } while (std::next_permutation(perm.begin(), perm.end()));
    return res;
}
std::string codeOf(const T& t) { std::string code = std::to_string(t.root); for (int i = 0; i < t.n; ++i) code += "," + std::to_string(t.P[i]); return code; }
std::vector<int> depths(const T& t) { std::vector<int> d(t.n, 0); std::vector<int> st = {t.root}; while (!st.empty()) { int u = st.back(); st.pop_back(); if (t.L[u] >= 0) { d[t.L[u]] = d[u] + 1; st.push_back(t.L[u]); } if (t.R[u] >= 0) { d[t.R[u]] = d[u] + 1; st.push_back(t.R[u]); } } return d; }
std::vector<int> subtreeSizes(const T& t) { std::vector<int> s(t.n, 1), order = {t.root}; for (size_t i = 0; i < order.size(); ++i) { int u = order[i]; if (t.L[u] >= 0) order.push_back(t.L[u]); if (t.R[u] >= 0) order.push_back(t.R[u]); } for (size_t i = order.size(); i-- > 1;) s[t.P[order[i]]] += s[order[i]]; return s; }
bool inSubtree(const T& t, int u, int x) { for (; u >= 0; u = t.P[u]) if (u == x) return true; return false; }

int main() {
    const long catalan[] = {1, 1, 2, 5, 14, 42, 132, 429};
    for (int n = 1; n <= 7; ++n) {
        std::map<std::string, T> shapeMap = allShapes(n); assert((long)shapeMap.size() == catalan[n]);               // 모양 수 = 카탈란 수
        std::vector<T> shapes; std::map<std::string, int> index; for (auto& kv : shapeMap) { index[kv.first] = (int)shapes.size(); shapes.push_back(kv.second); }
        std::vector<std::set<int>> adj(shapes.size()); long leftRot = 0, rightRot = 0;
        for (size_t i = 0; i < shapes.size(); ++i) {
            const T& t = shapes[i]; assert(t.linksOk()); std::vector<int> d0 = depths(t), s0 = subtreeSizes(t), in0 = t.inorder(); int moves = 0;
            for (int x = 0; x < n; ++x) {
                if (t.R[x] >= 0) { T c = t; int y = c.R[x]; c.rotateLeft(x); ++leftRot; ++moves;
                    bool ok = c.linksOk() && c.inorder() == in0; assert(ok);                                          // ① 중위·BST·링크 유지
                    std::vector<int> d1 = depths(c), s1 = subtreeSizes(c); assert(d1[x] == d0[x] + 1 && d1[y] == d0[y] - 1 && s1[y] == s0[x]);          // ② 깊이·크기
                    for (int v = 0; v < n; ++v) { assert(std::abs(d1[v] - d0[v]) <= 1); if (!inSubtree(t, v, x)) assert(d1[v] == d0[v]); }
                    T back = c; back.rotateRight(y); assert(back.same(t));                                           // ③ 역연산
                    adj[i].insert(index.at(codeOf(c))); }
                if (t.L[x] >= 0) { T c = t; c.rotateRight(x); ++rightRot; ++moves; bool ok = c.linksOk() && c.inorder() == in0; assert(ok); adj[i].insert(index.at(codeOf(c))); } }
            assert(moves == n - 1 && (int)adj[i].size() == n - 1);                                                      // ④ 간선(부모-자식 쌍)마다 정확히 한 번의 회전, 결과는 모두 서로 다른 모양
        }
        assert(leftRot == rightRot && leftRot + rightRot == (long)shapes.size() * (n - 1));                              // 거울 대칭으로 왼쪽·오른쪽 회전 수가 같다
        std::vector<int> dist(shapes.size(), -1); std::queue<int> q; dist[0] = 0; q.push(0); int reached = 1; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (dist[v] < 0) { dist[v] = dist[u] + 1; ++reached; q.push(v); } } assert(reached == (int)shapes.size());          // 연결 그래프
        T rightChain(n), leftChain(n); rightChain.root = 0; for (int i = 1; i < n; ++i) { rightChain.R[i - 1] = i; rightChain.P[i] = i - 1; } leftChain.root = n - 1; for (int i = n - 1; i > 0; --i) { leftChain.L[i] = i - 1; leftChain.P[i - 1] = i; }
        std::vector<int> d2(shapes.size(), -1); std::queue<int> q2; int s = index.at(codeOf(rightChain)); d2[s] = 0; q2.push(s); while (!q2.empty()) { int u = q2.front(); q2.pop(); for (int v : adj[u]) if (d2[v] < 0) { d2[v] = d2[u] + 1; q2.push(v); } } assert(d2[index.at(codeOf(leftChain))] == n - 1);   // 사슬 → 사슬 = n − 1 번
    }
    std::mt19937 rng(3);                                                                                          // 큰 트리: 무작위 회전열이 중위·링크를 보존 (n = 2000, 회전 20 만 번)
    const int n = 2000; T t = randomBst(n, rng);
    for (int step = 0; step < 200000; ++step) { int x = (int)(rng() % n); if (rng() % 2) { if (t.R[x] >= 0) t.rotateLeft(x); } else if (t.L[x] >= 0) t.rotateRight(x); }
    std::vector<int> in = t.inorder(); std::vector<int> want(n); std::iota(want.begin(), want.end(), 0); assert(t.linksOk() && in == want);
    std::cout << "RotateLeft: for every BST shape with n <= 7 (Catalan many) and every pivot, left rotation kept in-order, links and sizes, moved depths by +1/-1 and was undone by right rotation; the rotation graph was (n-1)-regular and connected, right chain to left chain took exactly n-1 rotations; 2*10^5 random rotations on 2000 nodes kept the keys sorted" << std::endl;
    return 0;
}
// Time Complexity: O(1) (포인터 몇 개)
// Space Complexity: O(1)
```
## RotateRight()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>

// 오른쪽 회전(rotateRight(y)): y 의 왼쪽 자식 x 를 올리고 y 를 x 의 오른쪽 자식으로 내린다 — 왼쪽 회전의 거울상.
//  ① 대칭성: rotateRight(T, y) == mirror(rotateLeft(mirror(T), n−1−y)) (키를 k → n−1−k 로 바꾸고 좌우를 교환한 트리에서 왼쪽 회전)  ② 무작위 BST 에서 회전 100 만 번 뒤에도 중위 순서·부모 링크가 유지
//  ③ AVL 응용: z 가 왼쪽으로 무거워(균형 인수 +2) 왼쪽 자식 x 의 균형 인수가 0 또는 +1 이면 오른쪽 회전 *한 번*으로 z·x 모두 |균형 인수| ≤ 1 이 되고, 부분 트리 높이는 x 가 +1 일 때(삽입 경우) 1 줄고 0 일 때(삭제 경우) 그대로
//  ④ 오른쪽 사슬을 루트에서 n − 1 번 왼쪽 회전하면 왼쪽 사슬이 되고, 같은 횟수의 오른쪽 회전으로 정확히 원래대로 돌아온다 (깊이 5000).
struct T {
    int n; std::vector<int> L, R, P; int root;
    explicit T(int nn) : n(nn), L(nn, -1), R(nn, -1), P(nn, -1), root(-1) {}
    void rotateLeft(int x) { int y = R[x]; R[x] = L[y]; if (L[y] >= 0) P[L[y]] = x; P[y] = P[x]; if (P[x] < 0) root = y; else if (L[P[x]] == x) L[P[x]] = y; else R[P[x]] = y; L[y] = x; P[x] = y; }
    void rotateRight(int y) { int x = L[y]; L[y] = R[x]; if (R[x] >= 0) P[R[x]] = y; P[x] = P[y]; if (P[y] < 0) root = x; else if (L[P[y]] == y) L[P[y]] = x; else R[P[y]] = x; R[x] = y; P[y] = x; }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(u); u = R[u]; } return out; }
    int height(int u) const { if (u < 0) return -1; int best = 0; std::vector<std::pair<int, int>> st = {{u, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return best; }
    int bf(int u) const { return height(L[u]) - height(R[u]); }
    bool same(const T& o) const { return root == o.root && L == o.L && R == o.R && P == o.P; }
    bool linksOk() const { if (P[root] != -1) return false; int cnt = 0; std::vector<int> st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); ++cnt; if (L[u] >= 0) { if (P[L[u]] != u || L[u] >= u) return false; st.push_back(L[u]); } if (R[u] >= 0) { if (P[R[u]] != u || R[u] <= u) return false; st.push_back(R[u]); } } return cnt == n; }   // 키 = 번호이므로 왼쪽 자식 < 부모 < 오른쪽 자식
};
T randomBst(int n, std::mt19937& rng) { T t(n); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); t.root = keys[0]; for (int i = 1; i < n; ++i) { int k = keys[i], u = t.root; while (true) { int& nx = k < u ? t.L[u] : t.R[u]; if (nx < 0) { nx = k; t.P[k] = u; break; } u = nx; } } return t; }
T mirrored(const T& t) { int n = t.n; T m(n); m.root = n - 1 - t.root; for (int k = 0; k < n; ++k) { int mk = n - 1 - k; m.L[mk] = t.R[k] >= 0 ? n - 1 - t.R[k] : -1; m.R[mk] = t.L[k] >= 0 ? n - 1 - t.L[k] : -1; m.P[mk] = t.P[k] >= 0 ? n - 1 - t.P[k] : -1; } return m; }   // 키 k → n−1−k, 좌우 교환

int main() {
    std::mt19937 rng(9);
    for (int it = 0; it < 3000; ++it) {                                                                          // ① 거울 대칭
        int n = 1 + (int)(rng() % 40); T t = randomBst(n, rng); int y = (int)(rng() % n); if (t.L[y] < 0) continue;
        T direct = t; direct.rotateRight(y); T m = mirrored(t); m.rotateLeft(n - 1 - y); T viaMirror = mirrored(m); assert(direct.same(viaMirror));
        std::vector<int> want(n); std::iota(want.begin(), want.end(), 0); assert(direct.inorder() == want && direct.linksOk());
    }
    { const int n = 1000; T t = randomBst(n, rng); for (long step = 0; step < 1000000; ++step) { int x = (int)(rng() % n); if (rng() % 2) { if (t.L[x] >= 0) t.rotateRight(x); } else if (t.R[x] >= 0) t.rotateLeft(x); }
      std::vector<int> in = t.inorder(); assert(t.linksOk() && std::is_sorted(in.begin(), in.end()) && (int)in.size() == n); }                // ②
    int cases[2] = {0, 0};
    for (int it = 0; it < 4000; ++it) {                                                                          // ③ AVL: 왼쪽 무거운 노드를 오른쪽 회전 한 번으로
        T t = randomBst(3 + (int)(rng() % 40), rng);
        for (int z = 0; z < t.n; ++z) { if (t.bf(z) != 2) continue; int x = t.L[z], bx = t.bf(x); if (bx != 0 && bx != 1) continue;
            int hz = t.height(z); T c = t; c.rotateRight(z); assert(c.P[z] == x && c.R[x] == z);
            assert(std::abs(c.bf(x)) <= 1 && std::abs(c.bf(z)) <= 1 && c.height(x) == hz - bx);                  // 높이: 삽입 경우(bx=1) −1, 삭제 경우(bx=0) 불변
            ++cases[bx]; }
    }
    assert(cases[0] > 0 && cases[1] > 0);
    const int N = 5000; T chain(N); chain.root = 0; for (int i = 1; i < N; ++i) { chain.R[i - 1] = i; chain.P[i] = i - 1; } T orig = chain;
    for (int i = 0; i + 1 < N; ++i) chain.rotateLeft(chain.root);                                                // 루트를 계속 왼쪽 회전
    assert(chain.linksOk() && chain.root == N - 1 && chain.R[chain.root] < 0 && chain.height(chain.root) == N - 1);   // 왼쪽 사슬
    for (int i = 0; i + 1 < N; ++i) chain.rotateRight(chain.root);                                               // ④ 되돌리기
    assert(chain.same(orig));
    std::cout << "RotateRight: matched the mirror image of rotateLeft on random trees, kept 10^6 random rotations consistent, repaired " << cases[1] << " insertion-type and " << cases[0] << " deletion-type left-heavy AVL violations with one rotation, and turned a 5000-node right chain into a left chain and back" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RotateLeftRight()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>

// 좌-우 이중 회전(LR): 노드 z 가 왼쪽으로 무거운데 그 왼쪽 자식 x 가 오른쪽으로 무거울 때(지그재그) 한 번의 회전으로는 안 된다 — x 를 먼저 왼쪽 회전해 (왼쪽, 왼쪽) 일직선으로 만든 뒤 z 를 오른쪽 회전.
//  결과적으로 x 의 오른쪽 자식 y 가 부분 트리의 루트가 되고 x 는 그 왼쪽, z 는 그 오른쪽 자식이 된다.  ① 회전 두 번의 결과 = 명시적 재구성 공식  ② 중위 순서·링크 유지, rotateLeft(y); rotateRight(y) 로 정확히 복귀
//  ③ AVL 에서 LR 불균형(z: +2, x: −1, y: |bf| ≤ 1)은 이중 회전으로 균형이 돌아오고 y 의 균형 인수는 0, 부분 트리 높이는 1 줄어든다  ④ 일직선 경우(LL: z +2, x +1)에 LR 을 잘못 쓰면 *항상* x 에서 균형이 깨진다 — 경우를 구분해야 하는 이유.
struct T {
    int n; std::vector<int> L, R, P; int root;
    explicit T(int nn) : n(nn), L(nn, -1), R(nn, -1), P(nn, -1), root(-1) {}
    void rotateLeft(int x) { int y = R[x]; R[x] = L[y]; if (L[y] >= 0) P[L[y]] = x; P[y] = P[x]; if (P[x] < 0) root = y; else if (L[P[x]] == x) L[P[x]] = y; else R[P[x]] = y; L[y] = x; P[x] = y; }
    void rotateRight(int y) { int x = L[y]; L[y] = R[x]; if (R[x] >= 0) P[R[x]] = y; P[x] = P[y]; if (P[y] < 0) root = x; else if (L[P[y]] == y) L[P[y]] = x; else R[P[y]] = x; R[x] = y; P[y] = x; }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(u); u = R[u]; } return out; }
    int height(int u) const { if (u < 0) return -1; int best = 0; std::vector<std::pair<int, int>> st = {{u, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return best; }
    int bf(int u) const { return height(L[u]) - height(R[u]); }
    bool same(const T& o) const { return root == o.root && L == o.L && R == o.R && P == o.P; }
    bool linksOk() const { if (P[root] != -1) return false; int cnt = 0; std::vector<int> st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); ++cnt; if (L[u] >= 0) { if (P[L[u]] != u || L[u] >= u) return false; st.push_back(L[u]); } if (R[u] >= 0) { if (P[R[u]] != u || R[u] <= u) return false; st.push_back(R[u]); } } return cnt == n; }   // 키 = 번호이므로 왼쪽 자식 < 부모 < 오른쪽 자식
};
T randomBst(int n, std::mt19937& rng) { T t(n); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); t.root = keys[0]; for (int i = 1; i < n; ++i) { int k = keys[i], u = t.root; while (true) { int& nx = k < u ? t.L[u] : t.R[u]; if (nx < 0) { nx = k; t.P[k] = u; break; } u = nx; } } return t; }
T mirrored(const T& t) { int n = t.n; T m(n); m.root = n - 1 - t.root; for (int k = 0; k < n; ++k) { int mk = n - 1 - k; m.L[mk] = t.R[k] >= 0 ? n - 1 - t.R[k] : -1; m.R[mk] = t.L[k] >= 0 ? n - 1 - t.L[k] : -1; m.P[mk] = t.P[k] >= 0 ? n - 1 - t.P[k] : -1; } return m; }   // 키 k → n−1−k, 좌우 교환

void rotateLR(T& t, int z) { t.rotateLeft(t.L[z]); t.rotateRight(z); }
void explicitLR(T& t, int z) {                                                                                  // 공식: x = z.left, y = x.right; y 가 루트, x = y.left (x.right ← y.left), z = y.right (z.left ← y.right)
    int x = t.L[z], y = t.R[x], pz = t.P[z], yl = t.L[y], yr = t.R[y];
    t.L[y] = x; t.R[y] = z; t.P[x] = y; t.P[z] = y; t.R[x] = yl; if (yl >= 0) t.P[yl] = x; t.L[z] = yr; if (yr >= 0) t.P[yr] = z;
    t.P[y] = pz; if (pz < 0) t.root = y; else if (t.L[pz] == z) t.L[pz] = y; else t.R[pz] = y;
}

int main() {
    { T t(3); t.root = 2; t.L[2] = 0; t.P[0] = 2; t.R[0] = 1; t.P[1] = 0; rotateLR(t, 2); assert(t.root == 1 && t.L[1] == 0 && t.R[1] == 2 && t.linksOk() && t.height(t.root) == 1); }   // 30, 10, 20 → 20 이 루트
    std::mt19937 rng(21); int checked = 0;
    for (int it = 0; it < 5000; ++it) {
        int n = 3 + (int)(rng() % 40); T t = randomBst(n, rng); std::vector<int> in0 = t.inorder();
        for (int z = 0; z < n; ++z) { if (t.L[z] < 0 || t.R[t.L[z]] < 0) continue; int x = t.L[z], y = t.R[x];
            T a = t, b = t; rotateLR(a, z); explicitLR(b, z); assert(a.same(b) && a.linksOk() && a.inorder() == in0);               // ① ②
            assert(a.L[y] == x && a.R[y] == z && a.P[y] == t.P[z]);                                                       // y 가 새 부분 트리 루트
            a.rotateLeft(y); a.rotateRight(y); assert(a.same(t)); ++checked; }                                            // 복귀: z 쪽 회전을 무르고 x 쪽 회전을 무른다
    }
    int fixedLR = 0, triedLL = 0, brokenLL = 0;
    for (int it = 0; it < 6000; ++it) {
        T t = randomBst(3 + (int)(rng() % 40), rng);
        for (int z = 0; z < t.n; ++z) { if (t.bf(z) != 2) continue; int x = t.L[z], bx = t.bf(x), hz = t.height(z);
            if (bx == -1 && std::abs(t.bf(t.R[x])) <= 1) { T c = t; int y = c.R[x]; rotateLR(c, z);                       // ③ 올바른 사용
                assert(c.bf(y) == 0 && std::abs(c.bf(x)) <= 1 && std::abs(c.bf(z)) <= 1 && c.height(y) == hz - 1); ++fixedLR; }
            else if (bx == 1 && t.R[x] >= 0) { T c = t; int y = c.R[x]; rotateLR(c, z); ++triedLL; if (std::abs(c.bf(x)) > 1) ++brokenLL; (void)y; } }   // ④ 잘못된 사용
    }
    assert(fixedLR > 0 && triedLL > 0 && brokenLL == triedLL);
    { const int n = 1000; T t = randomBst(n, rng); for (long step = 0; step < 1000000; ++step) { int z = (int)(rng() % n); if (t.L[z] >= 0 && t.R[t.L[z]] >= 0) rotateLR(t, z); else if (t.R[z] >= 0) t.rotateLeft(z); }     // 무작위 이중·단일 회전 100 만 번
      std::vector<int> in = t.inorder(); assert(t.linksOk() && std::is_sorted(in.begin(), in.end()) && (int)in.size() == n); }
    std::cout << "RotateLeftRight: double rotation equalled the explicit zig-zag reconstruction and was invertible on " << checked << " random pivots; " << fixedLR << " unbalanced AVL (LR) cases were repaired (balance factor 0 at the new root, height reduced by one), while applying it to " << triedLL << " straight (LL) cases broke balance in " << brokenLL << " of them" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RotateRightLeft()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>

// 우-좌 이중 회전(RL): 노드 z 가 오른쪽으로 무거운데 그 오른쪽 자식 x 가 왼쪽으로 무거울 때(지그재그) — x 를 먼저 오른쪽 회전한 뒤 z 를 왼쪽 회전.  LR 의 거울상이다.
//  ① 명시적 재구성(x 의 왼쪽 자식 y 가 루트, z 는 y.left, x 는 y.right) = 회전 두 번  ② 대칭: RL(T, z) = mirror(LR(mirror(T), n−1−z))  ③ 중위 보존, 링크 일관성
//  ④ AVL: RL 불균형(z: −2, x: +1, y: |bf| ≤ 1)을 이중 회전이 고친다 — y 의 균형 인수 0, 높이 1 감소  ⑤ 가장 작은 예: 삽입 순서 10, 30, 20 → 20 이 루트(높이 1).  100 만 번의 무작위 회전 뒤에도 일관.
struct T {
    int n; std::vector<int> L, R, P; int root;
    explicit T(int nn) : n(nn), L(nn, -1), R(nn, -1), P(nn, -1), root(-1) {}
    void rotateLeft(int x) { int y = R[x]; R[x] = L[y]; if (L[y] >= 0) P[L[y]] = x; P[y] = P[x]; if (P[x] < 0) root = y; else if (L[P[x]] == x) L[P[x]] = y; else R[P[x]] = y; L[y] = x; P[x] = y; }
    void rotateRight(int y) { int x = L[y]; L[y] = R[x]; if (R[x] >= 0) P[R[x]] = y; P[x] = P[y]; if (P[y] < 0) root = x; else if (L[P[y]] == y) L[P[y]] = x; else R[P[y]] = x; R[x] = y; P[y] = x; }
    std::vector<int> inorder() const { std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = L[u]; } u = st.back(); st.pop_back(); out.push_back(u); u = R[u]; } return out; }
    int height(int u) const { if (u < 0) return -1; int best = 0; std::vector<std::pair<int, int>> st = {{u, 0}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (L[p.first] >= 0) st.push_back({L[p.first], p.second + 1}); if (R[p.first] >= 0) st.push_back({R[p.first], p.second + 1}); } return best; }
    int bf(int u) const { return height(L[u]) - height(R[u]); }
    bool same(const T& o) const { return root == o.root && L == o.L && R == o.R && P == o.P; }
    bool linksOk() const { if (P[root] != -1) return false; int cnt = 0; std::vector<int> st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); ++cnt; if (L[u] >= 0) { if (P[L[u]] != u || L[u] >= u) return false; st.push_back(L[u]); } if (R[u] >= 0) { if (P[R[u]] != u || R[u] <= u) return false; st.push_back(R[u]); } } return cnt == n; }   // 키 = 번호이므로 왼쪽 자식 < 부모 < 오른쪽 자식
};
T randomBst(int n, std::mt19937& rng) { T t(n); std::vector<int> keys(n); std::iota(keys.begin(), keys.end(), 0); std::shuffle(keys.begin(), keys.end(), rng); t.root = keys[0]; for (int i = 1; i < n; ++i) { int k = keys[i], u = t.root; while (true) { int& nx = k < u ? t.L[u] : t.R[u]; if (nx < 0) { nx = k; t.P[k] = u; break; } u = nx; } } return t; }
T mirrored(const T& t) { int n = t.n; T m(n); m.root = n - 1 - t.root; for (int k = 0; k < n; ++k) { int mk = n - 1 - k; m.L[mk] = t.R[k] >= 0 ? n - 1 - t.R[k] : -1; m.R[mk] = t.L[k] >= 0 ? n - 1 - t.L[k] : -1; m.P[mk] = t.P[k] >= 0 ? n - 1 - t.P[k] : -1; } return m; }   // 키 k → n−1−k, 좌우 교환

void rotateRL(T& t, int z) { t.rotateRight(t.R[z]); t.rotateLeft(z); }
void rotateLR(T& t, int z) { t.rotateLeft(t.L[z]); t.rotateRight(z); }
void explicitRL(T& t, int z) {                                                                                  // x = z.right, y = x.left: y 가 루트, z = y.left (z.right ← y.left), x = y.right (x.left ← y.right)
    int x = t.R[z], y = t.L[x], pz = t.P[z], yl = t.L[y], yr = t.R[y];
    t.L[y] = z; t.R[y] = x; t.P[z] = y; t.P[x] = y; t.R[z] = yl; if (yl >= 0) t.P[yl] = z; t.L[x] = yr; if (yr >= 0) t.P[yr] = x;
    t.P[y] = pz; if (pz < 0) t.root = y; else if (t.L[pz] == z) t.L[pz] = y; else t.R[pz] = y;
}

int main() {
    { T t(3); t.root = 0; t.R[0] = 2; t.P[2] = 0; t.L[2] = 1; t.P[1] = 2; rotateRL(t, 0); assert(t.root == 1 && t.L[1] == 0 && t.R[1] == 2 && t.height(t.root) == 1 && t.linksOk()); }          // 10, 30, 20 (키 0, 2, 1)
    std::mt19937 rng(23); int checked = 0;
    for (int it = 0; it < 5000; ++it) {
        int n = 3 + (int)(rng() % 40); T t = randomBst(n, rng); std::vector<int> in0 = t.inorder();
        for (int z = 0; z < n; ++z) { if (t.R[z] < 0 || t.L[t.R[z]] < 0) continue; int x = t.R[z], y = t.L[x];
            T a = t, b = t; rotateRL(a, z); explicitRL(b, z); assert(a.same(b) && a.linksOk() && a.inorder() == in0);               // ① ③
            assert(a.L[y] == z && a.R[y] == x && a.P[y] == t.P[z]);
            T m = mirrored(t); rotateLR(m, n - 1 - z); T back = mirrored(m); assert(back.same(a));                          // ② RL(T) = mirror(LR(mirror(T)))
            a.rotateRight(y); a.rotateLeft(y); assert(a.same(t)); ++checked; }                                              // 복귀
    }
    int fixedRL = 0;
    for (int it = 0; it < 6000; ++it) {                                                                          // ④ AVL RL 불균형 수리
        T t = randomBst(3 + (int)(rng() % 40), rng);
        for (int z = 0; z < t.n; ++z) { if (t.bf(z) != -2) continue; int x = t.R[z]; if (t.bf(x) != 1 || std::abs(t.bf(t.L[x])) > 1) continue;
            int y = t.L[x], hz = t.height(z); T c = t; rotateRL(c, z);
            assert(c.bf(y) == 0 && std::abs(c.bf(x)) <= 1 && std::abs(c.bf(z)) <= 1 && c.height(y) == hz - 1); ++fixedRL; }
    }
    assert(fixedRL > 0);
    { const int n = 1000; T t = randomBst(n, rng); for (long step = 0; step < 1000000; ++step) { int z = (int)(rng() % n); if (t.R[z] >= 0 && t.L[t.R[z]] >= 0 && rng() % 2) rotateRL(t, z); else if (t.L[z] >= 0 && t.R[t.L[z]] >= 0) rotateLR(t, z); }
      std::vector<int> in = t.inorder(); assert(t.linksOk() && std::is_sorted(in.begin(), in.end()) && (int)in.size() == n); }
    std::cout << "RotateRightLeft: double rotation equalled the explicit zig-zag reconstruction and the mirror image of the LR rotation on " << checked << " random pivots and was invertible; " << fixedRL << " right-left unbalanced AVL cases were repaired (new root balanced, height reduced by one); 10^6 random double rotations kept the 1000-node tree sorted and consistent" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 7. Red-Black Tree
## RBInsert()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 레드-블랙 트리 삽입(CLRS): 새 노드를 빨강으로 BST 에 넣고, 빨강-빨강 위반을 (삼촌이 빨강이면) 색 바꾸기로 위로 올리거나 (삼촌이 검정이면) 회전 한두 번으로 끝낸다.
//  불변식 다섯 가지: ① 뿌리는 검정 ② 빨강 노드의 자식은 둘 다 검정 ③ 모든 뿌리-잎(nil) 경로의 검정 노드 수가 같다(검정 높이) ④ BST 순서 ⑤ 부모 링크 일치.  이로부터 높이 ≤ 2·log2(n+1) 이 나오고, 삽입 한 번의 회전은 *최대 2 번*이다.
//  ① 손으로 따라간 예 10 20 30 15 5 의 모양과 색을 그림으로 고정(왼쪽 회전 한 번, 색 바꾸기 한 번)  ② 1..8 의 모든 삽입 순서(40 320 가지)에서 매 삽입 뒤 불변식과 삽입당 회전 ≤ 2  ③ 무작위 삽입(중복 포함) 20 만 번을 std::set 과 대조(반환값·크기·조회)하고 주기적으로 불변식 검사
//  ④ 정렬·역정렬 10 만 개: 높이 ≤ 2·log2(n+1), 총 회전 ≤ 2n, 일반 BST 라면 높이 n  ⑤ 높이와 검정 높이의 관계: 높이 ≤ 2·검정 높이, 노드 수 ≥ 2^(검정 높이) − 1
enum Color { RED, BLACK };
class RedBlackTree {
public:
    RedBlackTree() : key(1, 0), color(1, BLACK), L(1, 0), R(1, 0), P(1, 0) {}                                              // 0 번 칸이 모든 nil 이 공유하는 검정 보초
    bool insert(int k) {
        int y = NIL, x = root;
        while (x != NIL) { y = x; if (k == key[x]) return false; x = k < key[x] ? L[x] : R[x]; }
        int z = (int)key.size(); key.push_back(k); color.push_back(RED); L.push_back(NIL); R.push_back(NIL); P.push_back(y);
        if (y == NIL) root = z; else if (k < key[y]) L[y] = z; else R[y] = z;
        long before = rotations; fixup(z); lastRotations = rotations - before; ++count; return true;
    }
    bool contains(int k) const { int x = root; while (x != NIL && key[x] != k) x = k < key[x] ? L[x] : R[x]; return x != NIL; }
    size_t size() const { return count; }
    int height() const { return height(root); }
    int blackHeight() const { int h = 0; for (int x = root; x != NIL; x = L[x]) h += color[x] == BLACK; return h; }
    int check() const {                                                                                                      // 불변식 전부를 검사하고 검정 높이를 돌려준다
        assert(color[root] == BLACK || root == NIL); size_t seen = 0; int bh = check(root, -(1LL << 40), 1LL << 40, seen); assert(seen == count); return bh; }
    std::vector<int> inorder() const { std::vector<int> out; inorder(root, out); return out; }
    std::string draw() const { return draw(root, 0); }                                                                       // 오른쪽 자식이 위, 왼쪽이 아래로 눕혀 그린다
    long rotations = 0, recolors = 0, lastRotations = 0;
private:
    static constexpr int NIL = 0;
    std::vector<int> key, color, L, R, P; int root = 0; size_t count = 0;
    void rotateLeft(int x) { int y = R[x]; R[x] = L[y]; if (L[y] != NIL) P[L[y]] = x; P[y] = P[x]; if (P[x] == NIL) root = y; else if (x == L[P[x]]) L[P[x]] = y; else R[P[x]] = y; L[y] = x; P[x] = y; ++rotations; }
    void rotateRight(int x) { int y = L[x]; L[x] = R[y]; if (R[y] != NIL) P[R[y]] = x; P[y] = P[x]; if (P[x] == NIL) root = y; else if (x == R[P[x]]) R[P[x]] = y; else L[P[x]] = y; R[y] = x; P[x] = y; ++rotations; }
    void fixup(int z) {
        while (color[P[z]] == RED) {
            int p = P[z], g = P[p];
            if (p == L[g]) { int u = R[g];
                if (color[u] == RED) { color[p] = BLACK; color[u] = BLACK; color[g] = RED; z = g; ++recolors; }               // 삼촌 빨강: 색만 바꾸고 할아버지에서 다시
                else { if (z == R[p]) { z = p; rotateLeft(z); } color[P[z]] = BLACK; color[P[P[z]]] = RED; rotateRight(P[P[z]]); } }   // 삼촌 검정: 꺾임이면 먼저 펴고 한 번 더 회전
            else { int u = L[g];
                if (color[u] == RED) { color[p] = BLACK; color[u] = BLACK; color[g] = RED; z = g; ++recolors; }
                else { if (z == L[p]) { z = p; rotateRight(z); } color[P[z]] = BLACK; color[P[P[z]]] = RED; rotateLeft(P[P[z]]); } }
        }
        color[root] = BLACK;
    }
    int height(int u) const { return u == NIL ? 0 : 1 + std::max(height(L[u]), height(R[u])); }
    int check(int u, long long lo, long long hi, size_t& seen) const {
        if (u == NIL) return 1; ++seen; assert(key[u] > lo && key[u] < hi);
        if (L[u] != NIL) assert(P[L[u]] == u); if (R[u] != NIL) assert(P[R[u]] == u);
        if (color[u] == RED) assert(color[L[u]] == BLACK && color[R[u]] == BLACK);                                           // 빨강-빨강 금지
        int bl = check(L[u], lo, key[u], seen), br = check(R[u], key[u], hi, seen); assert(bl == br); return bl + (color[u] == BLACK); }
    void inorder(int u, std::vector<int>& out) const { if (u == NIL) return; inorder(L[u], out); out.push_back(key[u]); inorder(R[u], out); }
    std::string draw(int u, int depth) const { if (u == NIL) return ""; return draw(R[u], depth + 1) + std::string(4 * depth, ' ') + std::to_string(key[u]) + (color[u] == RED ? "R" : "B") + "\n" + draw(L[u], depth + 1); }
};

int main() {
    {   RedBlackTree t; for (int k : {10, 20, 30}) t.insert(k);                                                              // ① 손으로 따라간 예
        assert(t.draw() == "    30R\n20B\n    10R\n");                                                                           // 10 20 30 → 20 이 뿌리(검정), 10·30 은 빨강 (왼쪽 회전 한 번)
        assert(t.rotations == 1 && t.recolors == 0);
        t.insert(15); assert(t.draw() == "    30B\n20B\n        15R\n    10B\n" && t.recolors == 1 && t.rotations == 1);       // 삼촌 30 이 빨강 → 색 바꾸기: 10·30 검정, 뿌리 20 은 다시 검정
        t.insert(5);  assert(t.draw() == "    30B\n20B\n        15R\n    10B\n        5R\n");
        t.check(); }
    for (int n = 1; n <= 8; ++n) { std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 1); long perms = 0;                                  // ② 모든 삽입 순서
        do { RedBlackTree t; for (int k : perm) { bool added = t.insert(k); assert(added && t.lastRotations <= 2); t.check(); } assert(t.size() == (size_t)n && t.height() <= 2 * std::log2(n + 1) + 1e-9); ++perms; } while (std::next_permutation(perm.begin(), perm.end()));
        long fact = 1; for (int i = 2; i <= n; ++i) fact *= i; assert(perms == fact); }
    {   std::mt19937 rng(88); RedBlackTree t; std::set<int> model;                                                            // ③ std::set 과 대조
        for (int step = 0; step < 200000; ++step) { int k = (int)(rng() % 50000);
            if (rng() % 4 != 0) { bool added = t.insert(k); bool want = model.insert(k).second; assert(added == want); } else assert(t.contains(k) == (model.count(k) == 1));
            assert(t.size() == model.size()); if (step % 20000 == 0) t.check(); }
        t.check(); std::vector<int> in = t.inorder(); assert(in == std::vector<int>(model.begin(), model.end())); }
    for (int mode = 0; mode < 2; ++mode) { const int n = 100000; RedBlackTree t; for (int i = 0; i < n; ++i) t.insert(mode == 0 ? i : n - i);            // ④ 정렬·역정렬
        int bh = t.check(); double bound = 2 * std::log2(n + 1.0); assert(t.height() <= bound && t.rotations <= 2L * n && t.rotations >= n / 2 - 1);
        assert(t.height() <= 2 * (bh - 1) + 1 && (double)t.size() >= std::pow(2.0, bh - 1) - 1); }                           // ⑤ 높이 ≤ 2·검정 높이, 노드 수 ≥ 2^bh − 1
    std::cout << "RBInsert: all 8! insertion orders kept the five invariants with at most 2 rotations per insert; 200000 random inserts matched std::set; sorted and reverse 100000 keys stayed within 2*log2(n+1) while a plain BST would be 100000 tall" << std::endl;
    return 0;
}
// Time Complexity: 삽입 O(log n) (회전 ≤ 2, 색 바꾸기는 분할상환 O(1))
// Space Complexity: O(n)
```
## RBDelete()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 레드-블랙 트리 삭제 (CLRS).  규칙: (1) 루트는 검정 (2) 빨강의 자식은 검정 (3) 모든 루트→nil 경로의 검정 개수가 같다.
// 빨강 노드를 지우면 규칙이 안 깨지지만, 검정 노드를 지우면 그 경로의 검정이 하나 모자란다 -> x 에 "추가 검정(double black)" 을 얹고 위로 올리며 해소
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
struct RBTree {
    Node *nil, *root;
    RBTree() { nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil; }
    void freeSub(Node* n) { if (n == nil) return; freeSub(n->l); freeSub(n->r); delete n; }
    ~RBTree() { freeSub(root); delete nil; }
    void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; }
    void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; }
    void insertFix(Node* z) {
        while (z->p->c == RED) {
            bool left = z->p == z->p->p->l;
            Node* y = left ? z->p->p->r : z->p->p->l;                          // 삼촌
            if (y->c == RED) { z->p->c = BLACK; y->c = BLACK; z->p->p->c = RED; z = z->p->p; }
            else {
                if (left && z == z->p->r) { z = z->p; rotL(z); } else if (!left && z == z->p->l) { z = z->p; rotR(z); }
                z->p->c = BLACK; z->p->p->c = RED;
                if (left) rotR(z->p->p); else rotL(z->p->p);
            }
        }
        root->c = BLACK;
    }
    void insert(int k) {
        Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
        while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
        z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
        insertFix(z);
    }
    void transplant(Node* u, Node* v) { if (u->p == nil) root = v; else if (u == u->p->l) u->p->l = v; else u->p->r = v; v->p = u->p; }
    Node* minimum(Node* x) { while (x->l != nil) x = x->l; return x; }
    Node* find(int k) { Node* x = root; while (x != nil && x->key != k) x = k < x->key ? x->l : x->r; return x; }
    void deleteFix(Node* x) {
        while (x != root && x->c == BLACK) {
            bool left = x == x->p->l;
            Node* w = left ? x->p->r : x->p->l;                                // 형제
            if (w->c == RED) { w->c = BLACK; x->p->c = RED; if (left) rotL(x->p); else rotR(x->p); w = left ? x->p->r : x->p->l; }     // 경우 1: 형제가 빨강
            Node *near = left ? w->l : w->r, *far = left ? w->r : w->l;
            if (near->c == BLACK && far->c == BLACK) { w->c = RED; x = x->p; }                                                          // 경우 2: 조카가 모두 검정 -> 문제를 위로
            else {
                if (far->c == BLACK) { near->c = BLACK; w->c = RED; if (left) rotR(w); else rotL(w); w = left ? x->p->r : x->p->l; far = left ? w->r : w->l; }   // 경우 3
                w->c = x->p->c; x->p->c = BLACK; far->c = BLACK; if (left) rotL(x->p); else rotR(x->p); x = root;                      // 경우 4: 한 번의 회전으로 해소
            }
        }
        x->c = BLACK;
    }
    void erase(int k) {
        Node* z = find(k); if (z == nil) return;
        Node *y = z, *x; Color orig = y->c;
        if (z->l == nil) { x = z->r; transplant(z, z->r); }
        else if (z->r == nil) { x = z->l; transplant(z, z->l); }
        else {
            y = minimum(z->r); orig = y->c; x = y->r;
            if (y->p == z) x->p = y; else { transplant(y, y->r); y->r = z->r; y->r->p = y; }
            transplant(z, y); y->l = z->l; y->l->p = y; y->c = z->c;
        }
        delete z;
        if (orig == BLACK) deleteFix(x);
    }
    int check(Node* n) {                                                       // 검정 높이를 반환, 규칙 위반이면 -1
        if (n == nil) return 1;
        if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
        int a = check(n->l), b = check(n->r);
        if (a < 0 || b < 0 || a != b) return -1;
        return a + (n->c == BLACK);
    }
    void inorder(Node* n, std::vector<int>& out) { if (n == nil) return; inorder(n->l, out); out.push_back(n->key); inorder(n->r, out); }
    bool valid() { return root->c == BLACK && check(root) > 0; }
};

int main() {
    RBTree t; std::set<int> oracle; std::mt19937 rng(11);
    for (int step = 0; step < 6000; step++) {
        int k = rng() % 500;
        if (rng() % 3 != 0) { if (!oracle.count(k)) { t.insert(k); oracle.insert(k); } }
        else { t.erase(k); oracle.erase(k); }
        if (step % 25 == 0) assert(t.valid());
    }
    assert(t.valid());
    std::vector<int> keys; t.inorder(t.root, keys);
    assert((keys == std::vector<int>(oracle.begin(), oracle.end())));          // 내용이 std::set 과 일치
    for (int k : std::vector<int>(oracle.begin(), oracle.end())) { t.erase(k); assert(t.valid()); }   // 하나씩 전부 삭제
    assert(t.root == t.nil);
    std::cout << "RBDelete verified: 6000 random operations kept all red-black rules." << std::endl;
    return 0;
}
// Time Complexity: O(log N), 삭제 후 회전은 최대 3번
// Space Complexity: O(N)
```
## FixViolation()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 삽입 후 규칙 위반 수리(fix-up): 새 노드는 빨강이므로 "빨강의 부모가 빨강" 위반만 생길 수 있다.  삼촌 색으로 세 경우를 가른다.
//  경우 1: 삼촌이 빨강       -> 부모·삼촌을 검정, 조부모를 빨강으로 (재색칠), 조부모에서 다시 검사 (위로 전파)
//  경우 2: 삼촌이 검정, 꺾인 모양(<, >) -> 회전으로 직선 모양을 만든다
//  경우 3: 삼촌이 검정, 직선 모양      -> 조부모 기준 회전 + 색 교환, 종료
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
Node* nil;
int caseCount[4];
Node* root;
void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; }
void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; }
void fixViolation(Node* z) {
    while (z->p->c == RED) {
        bool left = z->p == z->p->p->l;
        Node* uncle = left ? z->p->p->r : z->p->p->l;
        if (uncle->c == RED) { caseCount[1]++; z->p->c = BLACK; uncle->c = BLACK; z->p->p->c = RED; z = z->p->p; continue; }
        if (left && z == z->p->r) { caseCount[2]++; z = z->p; rotL(z); }
        else if (!left && z == z->p->l) { caseCount[2]++; z = z->p; rotR(z); }
        caseCount[3]++;
        z->p->c = BLACK; z->p->p->c = RED;
        if (left) rotR(z->p->p); else rotL(z->p->p);
    }
    root->c = BLACK;
}
void insert(int k) {
    Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
    while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
    z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
    fixViolation(z);
}
int blackHeight(Node* n) {                                          // 규칙 위반이면 -1
    if (n == nil) return 1;
    if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
    int a = blackHeight(n->l), b = blackHeight(n->r);
    return (a < 0 || b < 0 || a != b) ? -1 : a + (n->c == BLACK);
}
int height(Node* n) { return n == nil ? 0 : 1 + std::max(height(n->l), height(n->r)); }

int main() {
    nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil;
    std::mt19937 rng(12);
    std::vector<int> keys(2000); for (int i = 0; i < 2000; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) { insert(k); assert(root->c == BLACK && blackHeight(root) > 0); }   // 삽입할 때마다 모든 규칙 유지
    assert(caseCount[1] > 0 && caseCount[2] > 0 && caseCount[3] > 0);                       // 세 경우가 모두 실제로 쓰였다
    assert(caseCount[3] <= 2000);                                                           // 경우 3(회전)은 삽입당 최대 1번
    assert(height(root) <= 2 * std::log2(2001));                                            // 높이 <= 2·log2(n+1)
    std::cout << "FixViolation cases: recolor=" << caseCount[1] << " zigzag=" << caseCount[2] << " straight=" << caseCount[3] << ", height " << height(root) << std::endl;
    return 0;
}
// Time Complexity: O(log N), 회전은 삽입당 최대 2번
// Space Complexity: O(1) 추가 공간
```

## Recolor()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 재색칠(recolor): 삼촌이 빨강일 때의 수리는 포인터 하나 바꾸지 않고 색만 뒤집는다 (2-3-4 트리에서 4-노드를 분할해 가운데 키를 위로 올리는 것과 같다).
// 위로 전파될 수 있지만 분할상환하면 삽입당 O(1)번만 일어나고, 회전보다 훨씬 싸다.  전파가 루트에 닿으면 전체 검정 높이가 1 커진다
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
Node *nil, *root;
long recolors, rotations, maxCascade;
void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; rotations++; }
void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; rotations++; }
void insert(int k) {
    Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
    while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
    z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
    long cascade = 0;
    while (z->p->c == RED) {
        bool left = z->p == z->p->p->l; Node* u = left ? z->p->p->r : z->p->p->l;
        if (u->c == RED) { z->p->c = BLACK; u->c = BLACK; z->p->p->c = RED; z = z->p->p; recolors++; cascade++; }   // 재색칠: 회전 없음
        else {
            if (left && z == z->p->r) { z = z->p; rotL(z); } else if (!left && z == z->p->l) { z = z->p; rotR(z); }
            z->p->c = BLACK; z->p->p->c = RED; if (left) rotR(z->p->p); else rotL(z->p->p);
        }
    }
    root->c = BLACK; maxCascade = std::max(maxCascade, cascade);
}
int blackHeight(Node* n) {
    if (n == nil) return 1;
    if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
    int a = blackHeight(n->l), b = blackHeight(n->r);
    return (a < 0 || b < 0 || a != b) ? -1 : a + (n->c == BLACK);
}

int main() {
    nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil;
    std::mt19937 rng(13);
    const int n = 20000;
    std::vector<int> keys(n); for (int i = 0; i < n; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) insert(k);
    assert(blackHeight(root) > 0);
    assert(double(recolors) / n < 1.0);                              // 삽입당 평균 재색칠 < 1 (분할상환 O(1))
    assert(double(rotations) / n < 2.0);                             // 삽입당 회전 < 2
    assert(maxCascade <= std::log2(n + 1));                          // 한 번의 삽입에서 위로 전파되는 재색칠은 O(log n)
    std::cout << "per insert: recolors=" << double(recolors) / n << " rotations=" << double(rotations) / n << " max cascade=" << maxCascade << std::endl;
    return 0;
}
// Time Complexity: 삽입당 재색칠 분할상환 O(1), 최악 O(log N)
// Space Complexity: O(1)
```
## DoubleBlack()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 이중 검정(double black): 검정 노드를 지우면 그 아래 경로의 검정 개수가 하나 모자란다 -> 대체 노드 x 에 "검정 하나가 더 필요" 라는 표시를 단다.
// 형제 w 의 색과 조카의 색으로 네 경우를 나눠 해소한다 (오른쪽 자식일 때는 좌우 대칭).
//  1: w 가 빨강                  -> 회전·색 교환으로 w 를 검정으로 만들어 2~4 중 하나로
//  2: w, 두 조카 모두 검정       -> w 를 빨강으로 (검정 하나를 부모로 올림) -> 이중 검정이 위로 이동
//  3: w 검정, 먼 조카 검정·가까운 조카 빨강 -> w 와 가까운 조카를 회전해 4 로
//  4: w 검정, 먼 조카 빨강       -> 부모 기준 회전 + 색 교환 -> 종료
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
Node *nil, *root; long cases[5];
void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; }
void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; }
void insert(int k) {
    Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
    while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
    z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
    while (z->p->c == RED) {
        bool left = z->p == z->p->p->l; Node* u = left ? z->p->p->r : z->p->p->l;
        if (u->c == RED) { z->p->c = BLACK; u->c = BLACK; z->p->p->c = RED; z = z->p->p; }
        else { if (left && z == z->p->r) { z = z->p; rotL(z); } else if (!left && z == z->p->l) { z = z->p; rotR(z); }
               z->p->c = BLACK; z->p->p->c = RED; if (left) rotR(z->p->p); else rotL(z->p->p); }
    }
    root->c = BLACK;
}
void resolveDoubleBlack(Node* x) {
    while (x != root && x->c == BLACK) {
        bool left = x == x->p->l; Node* w = left ? x->p->r : x->p->l;
        if (w->c == RED) { cases[1]++; w->c = BLACK; x->p->c = RED; if (left) rotL(x->p); else rotR(x->p); w = left ? x->p->r : x->p->l; }
        Node *near = left ? w->l : w->r, *far = left ? w->r : w->l;
        if (near->c == BLACK && far->c == BLACK) { cases[2]++; w->c = RED; x = x->p; }
        else {
            if (far->c == BLACK) { cases[3]++; near->c = BLACK; w->c = RED; if (left) rotR(w); else rotL(w); w = left ? x->p->r : x->p->l; far = left ? w->r : w->l; }
            cases[4]++; w->c = x->p->c; x->p->c = BLACK; far->c = BLACK; if (left) rotL(x->p); else rotR(x->p); x = root;
        }
    }
    x->c = BLACK;                                                     // 빨강을 만나면 검정으로 칠해 이중 검정을 흡수
}
void transplant(Node* u, Node* v) { if (u->p == nil) root = v; else if (u == u->p->l) u->p->l = v; else u->p->r = v; v->p = u->p; }
void erase(int k) {
    Node* z = root; while (z != nil && z->key != k) z = k < z->key ? z->l : z->r;
    if (z == nil) return;
    Node *y = z, *x; Color orig = y->c;
    if (z->l == nil) { x = z->r; transplant(z, z->r); } else if (z->r == nil) { x = z->l; transplant(z, z->l); }
    else { y = z->r; while (y->l != nil) y = y->l; orig = y->c; x = y->r;
           if (y->p == z) x->p = y; else { transplant(y, y->r); y->r = z->r; y->r->p = y; }
           transplant(z, y); y->l = z->l; y->l->p = y; y->c = z->c; }
    delete z;
    if (orig == BLACK) resolveDoubleBlack(x);                         // 검정을 지웠을 때만 이중 검정이 생긴다
}
int blackHeight(Node* n) {
    if (n == nil) return 1;
    if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
    int a = blackHeight(n->l), b = blackHeight(n->r);
    return (a < 0 || b < 0 || a != b) ? -1 : a + (n->c == BLACK);
}

int main() {
    nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil;
    std::mt19937 rng(14);
    std::vector<int> keys(3000); for (int i = 0; i < 3000; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) insert(k);
    std::shuffle(keys.begin(), keys.end(), rng);
    for (size_t i = 0; i < keys.size(); i++) { erase(keys[i]); if (i % 10 == 0 && root != nil) assert(root->c == BLACK && blackHeight(root) > 0); }
    assert(root == nil);
    assert(cases[1] > 0 && cases[2] > 0 && cases[3] > 0 && cases[4] > 0);       // 네 경우가 모두 실제로 쓰였다
    assert(cases[4] <= 3000);                                                   // 종료 경우(4)는 삭제당 최대 1번
    std::cout << "DoubleBlack cases: 1=" << cases[1] << " 2=" << cases[2] << " 3=" << cases[3] << " 4=" << cases[4] << std::endl;
    return 0;
}
// Time Complexity: 삭제당 O(log N), 회전은 최대 3번
// Space Complexity: O(1) 추가 공간
```
## TwoThreeTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 2-3 트리: 모든 내부 노드가 자식 2개(키 1개) 또는 3개(키 2개)이고, 모든 잎이 같은 깊이에 있는 완전 균형 탐색 트리.
// 삽입은 잎까지 내려가 키를 넣고, 키가 3개가 되면 가운데 키를 위로 올리며 노드를 둘로 쪼갠다(분할이 루트까지 번지면 그때만 높이가 1 늘어난다).
// 균형이 "회전"이 아니라 "분할"로 유지되므로 모든 잎의 깊이가 항상 같다 -> 레드-블랙 트리(특히 LLRB)가 이 구조를 이진 트리로 흉내 낸 것이다
struct Node { std::vector<int> k; std::vector<Node*> c; bool leaf() const { return c.empty(); } };

bool contains(Node* n, int x) {
    while (n) {
        int i = 0; while (i < (int)n->k.size() && x > n->k[i]) i++;
        if (i < (int)n->k.size() && n->k[i] == x) return true;
        if (n->leaf()) return false;
        n = n->c[i];
    }
    return false;
}
bool insertRec(Node* n, int x, int& up, Node*& right) {                    // 분할이 일어나면 true, up 은 올릴 키, right 는 새로 생긴 오른쪽 노드
    int i = 0; while (i < (int)n->k.size() && x > n->k[i]) i++;
    if (i < (int)n->k.size() && n->k[i] == x) return false;                // 중복 키
    if (n->leaf()) n->k.insert(n->k.begin() + i, x);
    else {
        int u; Node* r;
        if (!insertRec(n->c[i], x, u, r)) return false;                    // 아래에서 분할이 없었으면 여기서 끝
        n->k.insert(n->k.begin() + i, u); n->c.insert(n->c.begin() + i + 1, r);
    }
    if (n->k.size() < 3) return false;
    up = n->k[1]; right = new Node; right->k = {n->k[2]};                  // [a b c] -> [a] ↑b [c]
    if (!n->leaf()) { right->c = {n->c[2], n->c[3]}; n->c.resize(2); }
    n->k.resize(1); return true;
}
void insert(Node*& root, int x) {
    if (!root) { root = new Node; root->k = {x}; return; }
    int u; Node* r;
    if (insertRec(root, x, u, r)) { Node* nr = new Node; nr->k = {u}; nr->c = {root, r}; root = nr; }
}
// 불변식 검사: 키 1~2개, 자식 수 = 키 수 + 1, 키 순서, 모든 잎의 깊이가 같음. 높이(잎=1)를 돌려주고 위반이면 -1
int check(Node* n, long lo, long hi, std::vector<int>& inorder) {
    if (n->k.empty() || n->k.size() > 2) return -1;
    for (size_t i = 0; i < n->k.size(); i++) if (n->k[i] <= (i ? n->k[i - 1] : lo) || n->k[i] >= hi) return -1;
    if (n->leaf()) { for (int x : n->k) inorder.push_back(x); return 1; }
    if (n->c.size() != n->k.size() + 1) return -1;
    int h = -2;
    for (size_t i = 0; i < n->c.size(); i++) {
        long l = i ? n->k[i - 1] : lo, r = i < n->k.size() ? n->k[i] : hi;
        int ch = check(n->c[i], l, r, inorder); if (ch < 0 || (h != -2 && ch != h)) return -1;
        h = ch; if (i < n->k.size()) inorder.push_back(n->k[i]);
    }
    return h + 1;
}
void destroy(Node* n) { if (!n) return; for (Node* c : n->c) destroy(c); delete n; }

int main() {
    std::mt19937 rng(23);
    Node* root = nullptr; std::set<int> ref;
    for (int i = 0; i < 5000; i++) {
        int x = rng() % 20000; insert(root, x); ref.insert(x);
        if (i % 500 == 0) { std::vector<int> v; assert(check(root, -1, 1L << 40, v) > 0); }
    }
    std::vector<int> v; int h = check(root, -1, 1L << 40, v);
    assert(h > 0 && v == std::vector<int>(ref.begin(), ref.end()));        // 구조가 올바르고 중위 순회가 정렬된 집합과 같다
    for (int x = 0; x < 20000; x += 7) assert(contains(root, x) == (ref.count(x) > 0));
    int n = ref.size();
    assert(h <= std::log2(n + 1) + 1e-9 && h >= std::log(n + 1.0) / std::log(3.0) - 1e-9);   // 3^h >= n+1 >= 2^h
    destroy(root); root = nullptr;
    for (int x = 1; x <= 4095; x++) insert(root, x);                       // 정렬 입력에도 균형이 유지된다
    v.clear(); int hs = check(root, 0, 1L << 40, v);
    assert(hs > 0 && hs <= 12 && v.size() == 4095);
    std::cout << "2-3 tree: " << n << " random keys -> height " << h << ", 4095 sorted keys -> height " << hs << std::endl;
    destroy(root);
    return 0;
}
// Time Complexity: 탐색·삽입 O(log N) (높이 log3 N ~ log2 N)
// Space Complexity: O(N)
```
## TwoThreeFourTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 2-3-4 트리: 노드가 키 1~3개(자식 2~4개)를 가지는 균형 탐색 트리. 삽입을 "내려가는 길에" 처리하는 것이 핵심이다.
// 루트에서 잎으로 내려가며 만나는 가득 찬 노드(키 3개, 4-노드)를 미리 쪼개 두면, 잎에 도착했을 때 부모에 자리가 있다는 것이 보장되어
// 위로 되돌아갈 필요가 없다(한 번의 하향 패스). 레드-블랙 트리는 2-3-4 트리를 이진 트리로 옮긴 것: 4-노드 = 검은 노드 + 빨간 자식 둘
struct Node { int n = 0; int k[3]; Node* c[4] = {}; bool leaf = true; };

void splitChild(Node* p, int i) {                                          // p->c[i] 는 가득 찬 노드, p 는 가득 차 있지 않다
    Node* y = p->c[i]; Node* z = new Node; z->leaf = y->leaf; z->n = 1; z->k[0] = y->k[2];
    if (!y->leaf) { z->c[0] = y->c[2]; z->c[1] = y->c[3]; }
    for (int j = p->n; j > i; j--) { p->k[j] = p->k[j - 1]; p->c[j + 1] = p->c[j]; }
    p->k[i] = y->k[1]; p->c[i + 1] = z; p->n++; y->n = 1;                  // 가운데 키가 부모로 올라간다
}
int splits = 0;
bool insert(Node*& root, int x) {
    if (!root) { root = new Node; root->n = 1; root->k[0] = x; return true; }
    if (root->n == 3) { Node* s = new Node; s->leaf = false; s->c[0] = root; splitChild(s, 0); root = s; splits++; }
    Node* t = root;
    for (;;) {
        int i = 0; while (i < t->n && x > t->k[i]) i++;
        if (i < t->n && t->k[i] == x) return false;
        if (t->leaf) { for (int j = t->n; j > i; j--) t->k[j] = t->k[j - 1]; t->k[i] = x; t->n++; return true; }
        if (t->c[i]->n == 3) {
            splitChild(t, i); splits++;
            if (x == t->k[i]) return false;
            if (x > t->k[i]) i++;
        }
        t = t->c[i];
    }
}
bool contains(Node* t, int x) {
    while (t) {
        int i = 0; while (i < t->n && x > t->k[i]) i++;
        if (i < t->n && t->k[i] == x) return true;
        if (t->leaf) return false;
        t = t->c[i];
    }
    return false;
}
int check(Node* t, long lo, long hi, std::vector<int>& out) {              // 높이(잎=1), 위반이면 -1
    if (t->n < 1 || t->n > 3) return -1;
    for (int i = 0; i < t->n; i++) if (t->k[i] <= (i ? t->k[i - 1] : lo) || t->k[i] >= hi) return -1;
    if (t->leaf) { for (int i = 0; i < t->n; i++) out.push_back(t->k[i]); return 1; }
    int h = -2;
    for (int i = 0; i <= t->n; i++) {
        if (!t->c[i]) return -1;
        int ch = check(t->c[i], i ? t->k[i - 1] : lo, i < t->n ? t->k[i] : hi, out);
        if (ch < 0 || (h != -2 && ch != h)) return -1;
        h = ch; if (i < t->n) out.push_back(t->k[i]);
    }
    return h + 1;
}
void destroy(Node* t) { if (!t) return; if (!t->leaf) for (int i = 0; i <= t->n; i++) destroy(t->c[i]); delete t; }

int main() {
    std::mt19937 rng(5);
    Node* root = nullptr; std::set<int> ref;
    for (int i = 0; i < 6000; i++) {
        int x = rng() % 30000; bool added = insert(root, x); assert(added == ref.insert(x).second);   // 중복이면 false
        if (i % 600 == 0) { std::vector<int> v; assert(check(root, -1, 1L << 40, v) > 0); }
    }
    std::vector<int> v; int h = check(root, -1, 1L << 40, v);
    assert(h > 0 && v == std::vector<int>(ref.begin(), ref.end()));
    for (int x = 0; x < 30000; x += 11) assert(contains(root, x) == (ref.count(x) > 0));
    int n = ref.size();
    assert(h <= std::log2(n + 1) + 1e-9 && h >= std::log(n + 1.0) / std::log(4.0) - 1e-9);   // 4^h >= n+1 >= 2^h
    std::cout << "2-3-4 tree: " << n << " keys -> height " << h << " (log4=" << std::log(n + 1.0) / std::log(4.0) << ", log2=" << std::log2(n + 1) << "), splits " << splits << std::endl;
    destroy(root); root = nullptr;
    for (int x = 1; x <= 3000; x++) insert(root, x);
    v.clear(); assert(check(root, 0, 1L << 40, v) > 0 && v.size() == 3000);
    destroy(root);
    return 0;
}
// Time Complexity: 탐색·삽입 O(log N), 삽입은 하향 한 번
// Space Complexity: O(N)
```
## LeftLeaningRedBlackTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <cassert>

// 좌편향 레드-블랙 트리(LLRB, Sedgewick): 빨간 링크는 반드시 왼쪽 자식으로만 허용한다. 빨간 왼쪽 링크로 묶인 두 노드 = 2-3 트리의 3-노드.
// 그 규칙 덕에 삽입은 "회전 2종 + 색 뒤집기" 세 줄(fix)만으로 끝나고, 삭제도 "빨간 링크를 아래로 밀어 내리는" moveRedLeft/moveRedRight 로 정리된다
struct Node { int key; Node *l = nullptr, *r = nullptr; bool red = true; explicit Node(int k) : key(k) {} };
bool isRed(Node* h) { return h && h->red; }
Node* rotL(Node* h) { Node* x = h->r; h->r = x->l; x->l = h; x->red = h->red; h->red = true; return x; }
Node* rotR(Node* h) { Node* x = h->l; h->l = x->r; x->r = h; x->red = h->red; h->red = true; return x; }
void flip(Node* h) { h->red = !h->red; h->l->red = !h->l->red; h->r->red = !h->r->red; }
Node* fix(Node* h) {
    if (isRed(h->r) && !isRed(h->l)) h = rotL(h);                          // 오른쪽 빨간 링크는 왼쪽으로 눕힌다
    if (isRed(h->l) && isRed(h->l->l)) h = rotR(h);                        // 빨간 링크 두 개가 연속 -> 4-노드로 만든다
    if (isRed(h->l) && isRed(h->r)) flip(h);                               // 4-노드를 쪼개 빨간 링크를 부모로 올린다
    return h;
}
Node* insert(Node* h, int k) {
    if (!h) return new Node(k);
    if (k < h->key) h->l = insert(h->l, k); else if (k > h->key) h->r = insert(h->r, k);
    return fix(h);
}
Node* moveRedLeft(Node* h) { flip(h); if (isRed(h->r->l)) { h->r = rotR(h->r); h = rotL(h); flip(h); } return h; }
Node* moveRedRight(Node* h) { flip(h); if (isRed(h->l->l)) { h = rotR(h); flip(h); } return h; }
Node* minNode(Node* h) { while (h->l) h = h->l; return h; }
Node* deleteMin(Node* h) {
    if (!h->l) { delete h; return nullptr; }
    if (!isRed(h->l) && !isRed(h->l->l)) h = moveRedLeft(h);
    h->l = deleteMin(h->l); return fix(h);
}
bool contains(Node* h, int k) { while (h) { if (k == h->key) return true; h = k < h->key ? h->l : h->r; } return false; }
Node* erase(Node* h, int k) {                                              // k 가 반드시 존재한다고 가정
    if (k < h->key) {
        if (!isRed(h->l) && !isRed(h->l->l)) h = moveRedLeft(h);
        h->l = erase(h->l, k);
    } else {
        if (isRed(h->l)) h = rotR(h);
        if (k == h->key && !h->r) { delete h; return nullptr; }
        if (!isRed(h->r) && !isRed(h->r->l)) h = moveRedRight(h);
        if (k == h->key) { h->key = minNode(h->r)->key; h->r = deleteMin(h->r); }
        else h->r = erase(h->r, k);
    }
    return fix(h);
}
Node* insertRoot(Node* root, int k) { root = insert(root, k); root->red = false; return root; }
Node* eraseRoot(Node* root, int k) {
    if (!contains(root, k)) return root;
    if (!isRed(root->l) && !isRed(root->r)) root->red = true;
    root = erase(root, k); if (root) root->red = false; return root;
}
// 불변식: BST 순서, 오른쪽 빨간 링크 없음, 빨간 노드의 빨간 자식 없음, 모든 경로의 검은 노드 수가 같음
int blackHeight(Node* h, long lo, long hi) {
    if (!h) return 1;
    if (h->key <= lo || h->key >= hi || isRed(h->r) || (h->red && isRed(h->l))) return -1;
    int a = blackHeight(h->l, lo, h->key), b = blackHeight(h->r, h->key, hi);
    if (a < 0 || b < 0 || a != b) return -1;
    return a + (h->red ? 0 : 1);
}
int height(Node* h) { return h ? 1 + std::max(height(h->l), height(h->r)) : 0; }
void destroy(Node* h) { if (!h) return; destroy(h->l); destroy(h->r); delete h; }

int main() {
    Node* root = nullptr;
    for (int i = 1; i <= 4095; i++) root = insertRoot(root, i);              // 정렬 입력(BST 라면 최악)
    assert(blackHeight(root, 0, 1L << 40) > 0);
    assert(height(root) <= 2 * std::log2(4096.0));                          // 높이 <= 2 log2(N+1)
    destroy(root); root = nullptr;

    std::mt19937 rng(77); std::set<int> ref;
    for (int step = 0; step < 20000; step++) {
        int x = rng() % 600;
        if (rng() % 3) { root = insertRoot(root, x); ref.insert(x); }
        else           { root = eraseRoot(root, x); ref.erase(x); }
        if (step % 25 == 0) {
            assert(!isRed(root) && blackHeight(root, -1, 1L << 40) > 0);
            for (int q = 0; q < 600; q += 37) assert(contains(root, q) == (ref.count(q) > 0));
        }
    }
    assert(blackHeight(root, -1, 1L << 40) > 0);
    for (int x : std::set<int>(ref)) { root = eraseRoot(root, x); ref.erase(x); assert(!root || blackHeight(root, -1, 1L << 40) > 0); }
    assert(!root);
    std::cout << "LLRB: 4095 sorted inserts OK, 20000 random insert/delete steps OK" << std::endl;
    return 0;
}
// Time Complexity: 삽입·삭제·탐색 O(log N)
// Space Complexity: O(N)
```
# Part 8. 힙
## BinaryHeap()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 이진 힙(최소 힙): 완전 이진 트리를 배열에 담는다 — 노드 i 의 부모 (i−1)/2, 자식 2i+1·2i+2.  모양이 항상 완전해서 포인터가 필요 없고, 각 노드 ≤ 자식(힙 성질)이라 최솟값은 배열의 맨 앞이다.
//  삽입: 끝에 붙이고 위로 올리기(sift-up), 삭제: 끝 원소를 뿌리로 옮기고 아래로 내리기(sift-down) — 둘 다 O(log n).  build: 아래에서부터 sift-down 하면 O(n) (n 번 삽입하는 O(n log n) 보다 빠르다).
//  ① 배열과 트리를 같이 그린 그림 고정(7 개: 1 3 2 7 4 5 6)  ② 무작위 연산(삽입 55% / 추출 45%) 30 만 번을 std::priority_queue 와 대조(top·size)하고 주기적으로 힙 성질 검사
//  ③ build: 무작위 배열 2 000 개에서 힙 성질 성립, 비교 횟수 ≤ 2n, 같은 배열을 하나씩 삽입한 것과 *원소 집합*이 같음; 정렬된 배열에서는 비교 n−1 에 가까움  ④ 힙 정렬: 반복 추출 결과 == std::sort  ⑤ 모든 모양 점검: n ≤ 7 의 모든 순열에서 build 결과가 힙, 삽입 순서에 따라 배열은 달라도 min 은 같음
class MinHeap {
public:
    MinHeap() {}
    explicit MinHeap(const std::vector<int>& arr) : a(arr) { for (int i = (int)a.size() / 2 - 1; i >= 0; --i) siftDown(i); }              // O(n) 힙 만들기
    void push(int v) { a.push_back(v); siftUp((int)a.size() - 1); }
    int top() const { return a.front(); }
    void pop() { a[0] = a.back(); a.pop_back(); if (!a.empty()) siftDown(0); }
    size_t size() const { return a.size(); }
    bool isHeap() const { for (size_t i = 1; i < a.size(); ++i) if (a[(i - 1) / 2] > a[i]) return false; return true; }
    const std::vector<int>& array() const { return a; }
    long comparisons = 0;
private:
    std::vector<int> a;
    void siftUp(int i) { while (i > 0) { int p = (i - 1) / 2; ++comparisons; if (a[p] <= a[i]) break; std::swap(a[p], a[i]); i = p; } }
    void siftDown(int i) { int n = (int)a.size();
        while (true) { int l = 2 * i + 1, r = l + 1, s = i;
            if (l < n) { ++comparisons; if (a[l] < a[s]) s = l; } if (r < n) { ++comparisons; if (a[r] < a[s]) s = r; }
            if (s == i) break; std::swap(a[i], a[s]); i = s; } }
};
std::string drawHeap(const std::vector<int>& a) {                                                                            // 한 칸 폭 3, 수준마다 들여쓰기·간격이 2 배씩
    int n = (int)a.size(), levels = 0; while ((1 << levels) - 1 < n) ++levels; std::string out; char cell[8];
    for (int d = 0, idx = 0; d < levels; ++d) { int indent = ((1 << (levels - d - 1)) - 1) * 3, gap = ((1 << (levels - d)) - 1) * 3; std::string row(indent, ' ');
        for (int k = 0; k < (1 << d) && idx < n; ++k, ++idx) { if (k) row += std::string(gap, ' '); std::snprintf(cell, sizeof cell, "%3d", a[idx]); row += cell; }
        out += row + "\n"; }
    return out; }

int main() {
    {   MinHeap h; for (int v : {7, 3, 5, 1, 4, 2, 6}) h.push(v);                                                           // ① 그림
        assert((h.array() == std::vector<int>{1, 3, 2, 7, 4, 5, 6}));
        assert(drawHeap(h.array()) == "           1\n     3           2\n  7     4     5     6\n");       // 부모의 칸은 두 자식 칸의 한가운데
        h.pop(); assert((h.array() == std::vector<int>{2, 3, 5, 7, 4, 6})); assert(h.isHeap()); }
    {   std::mt19937 rng(41); MinHeap h; std::priority_queue<int, std::vector<int>, std::greater<int>> model;                  // ② 대조
        for (int step = 0; step < 300000; ++step) {
            if (model.empty() || rng() % 100 < 55) { int v = (int)(rng() % 100000) - 50000; h.push(v); model.push(v); } else { assert(h.top() == model.top()); h.pop(); model.pop(); }
            assert(h.size() == model.size()); if (!model.empty()) assert(h.top() == model.top()); if (step % 25000 == 0) assert(h.isHeap()); }
        while (!model.empty()) { assert(h.top() == model.top()); h.pop(); model.pop(); } assert(h.size() == 0); }
    {   std::mt19937 rng(42);                                                                                                // ③ O(n) build
        for (int trial = 0; trial < 50; ++trial) { int n = 1 + (int)(rng() % 2000); std::vector<int> v(n); for (auto& x : v) x = (int)(rng() % 10000);
            MinHeap built(v); assert(built.isHeap() && built.comparisons <= 2L * n); MinHeap pushed; for (int x : v) pushed.push(x);
            std::vector<int> b1 = built.array(), b2 = pushed.array(); std::sort(b1.begin(), b1.end()); std::sort(b2.begin(), b2.end()); assert(b1 == b2); }
        std::vector<int> sorted(1000); for (int i = 0; i < 1000; ++i) sorted[i] = i; MinHeap s(sorted); assert(s.comparisons == 999); }                           // 이미 힙이면 뿌리를 뺀 모든 원소가 부모 쪽 비교에 정확히 한 번 나온다: n − 1
    {   std::mt19937 rng(43); std::vector<int> v(5000); for (auto& x : v) x = (int)(rng() % 3000); MinHeap h(v); std::vector<int> out; while (h.size()) { out.push_back(h.top()); h.pop(); }        // ④ 힙 정렬
        std::vector<int> want = v; std::sort(want.begin(), want.end()); assert(out == want); }
    for (int n = 1; n <= 7; ++n) { std::vector<int> perm(n); for (int i = 0; i < n; ++i) perm[i] = i; do { MinHeap h(perm); assert(h.isHeap() && h.top() == 0); MinHeap g; for (int x : perm) g.push(x); assert(g.isHeap() && g.top() == 0); } while (std::next_permutation(perm.begin(), perm.end())); }   // ⑤
    std::cout << "BinaryHeap: 300000 random push/pop operations matched std::priority_queue; O(n) build used at most 2n comparisons on 50 random arrays; heap sort equalled std::sort; every permutation up to 7 built a valid heap" << std::endl;
    return 0;
}
// Time Complexity: push·pop O(log n), top O(1), build O(n)
// Space Complexity: O(n)
```

## HeapInsert()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 힙 삽입(트리 관점의 요약, 정본은 Queue.md Part 5): 완전 이진 트리의 배열 표현에서 맨 끝(다음 빈 자리)에 넣고 부모보다 작으면 위로 올린다(sift-up).  배열 인덱스로 트리 관계가 정해진다: 부모 (i−1)/2, 왼쪽 자식 2i+1, 오른쪽 자식 2i+2.
//  ① 트리 관점 확인: 레벨 순서로 노드를 하나씩 "비어 있는 첫 자리"에 붙여 만든 *명시적* 이진 트리의 부모·자식 관계가 인덱스 공식과 같고 깊이 = ⌊log2(i+1)⌋, 높이 = ⌊log2 n⌋  ② 모든 삽입 순서(n ≤ 8)에서 힙 성질이 성립하고 만들 수 있는 서로 다른 힙은 n!/∏(부분 트리 크기) 개 이하
//  ③ 비용: 내림차순 삽입(매번 새 최솟값)은 총 Σ⌊log2 i⌋ 번 교환(최악), 오름차순은 0 번; 무작위 삽입의 평균 교환은 상수(<3).  100 만 개를 std::priority_queue 가 만든 것과 같은 정렬 결과로 대조 (std::is_heap 으로도 독립 검증).
struct MinHeap {
    std::vector<int> a; long swaps = 0;
    void push(int v) { a.push_back(v); size_t i = a.size() - 1; while (i > 0 && a[(i - 1) / 2] > a[i]) { std::swap(a[i], a[(i - 1) / 2]); i = (i - 1) / 2; ++swaps; } }
    bool valid() const { for (size_t i = 1; i < a.size(); ++i) if (a[(i - 1) / 2] > a[i]) return false; return true; }
};
long sumFloorLog2(int n) { long s = 0; for (int i = 1; i <= n; ++i) s += 31 - __builtin_clz((unsigned)i); return s; }

int main() {
    for (int n = 1; n <= 2000; ++n) {                                                                            // ① 명시적 트리: 노드를 레벨 순서로 첫 빈 자리에 붙인다
        std::vector<int> L(n, -1), R(n, -1), P(n, -1), dep(n, 0); std::queue<int> open; open.push(0);
        for (int v = 1; v < n; ++v) { int u = open.front(); if (L[u] < 0) L[u] = v; else { R[u] = v; open.pop(); } P[v] = u; dep[v] = dep[u] + 1; open.push(v); }
        for (int i = 0; i < n; ++i) { assert(L[i] == (2 * i + 1 < n ? 2 * i + 1 : -1) && R[i] == (2 * i + 2 < n ? 2 * i + 2 : -1) && (i == 0 ? P[i] == -1 : P[i] == (i - 1) / 2)); assert(dep[i] == 31 - __builtin_clz((unsigned)(i + 1))); }
        assert(*std::max_element(dep.begin(), dep.end()) == 31 - __builtin_clz((unsigned)n));
    }
    for (int n = 1; n <= 8; ++n) {                                                                               // ② 모든 삽입 순서
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::set<std::vector<int>> shapes;
        do { MinHeap h; for (int v : perm) { h.push(v); assert(h.valid()); } assert(h.a[0] == 0 && std::is_heap(h.a.begin(), h.a.end(), std::greater<int>())); shapes.insert(h.a); } while (std::next_permutation(perm.begin(), perm.end()));
        std::vector<long> sz(n, 1); for (int i = n - 1; i > 0; --i) sz[(i - 1) / 2] += sz[i]; double heaps = 1; for (int i = 1; i <= n; ++i) heaps *= i; for (int i = 0; i < n; ++i) heaps /= (double)sz[i];     // 훅 길이 공식 n!/∏ size
        assert((double)shapes.size() <= heaps + 0.5);
    }
    { const int n = 100000; MinHeap down, up; for (int i = n; i >= 1; --i) down.push(i); for (int i = 1; i <= n; ++i) up.push(i); assert(down.swaps == sumFloorLog2(n) && up.swaps == 0 && up.valid() && down.valid()); }          // ③ 최악·최선
    std::mt19937 rng(17); const int n = 1000000; MinHeap h; std::priority_queue<int, std::vector<int>, std::greater<int>> ref; std::vector<int> vals(n);
    for (int i = 0; i < n; ++i) { vals[i] = (int)(rng() % 2000001) - 1000000; h.push(vals[i]); ref.push(vals[i]); }
    assert(h.valid() && std::is_heap(h.a.begin(), h.a.end(), std::greater<int>()) && h.a[0] == *std::min_element(vals.begin(), vals.end()) && h.a[0] == ref.top());
    double avg = (double)h.swaps / n; assert(avg < 3.0);
    std::vector<int> sorted = h.a; std::sort(sorted.begin(), sorted.end()); std::vector<int> viaRef; viaRef.reserve(n); while (!ref.empty()) { viaRef.push_back(ref.top()); ref.pop(); } assert(sorted == viaRef);
    std::cout << "HeapInsert: array index formulas matched an explicit level-order tree up to n=2000, every insertion order of up to 8 keys gave a valid heap, descending inserts cost exactly sum(floor(log2 i)) swaps, and 10^6 random inserts (avg " << avg << " swaps) matched std::priority_queue" << std::endl;
    return 0;
}
// Time Complexity: O(log N) (평균 O(1))
// Space Complexity: O(1)
```
## HeapDelete()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 힙 삭제(요약, 정본은 Queue.md Part 5): 루트를 빼고 맨 끝 원소를 루트로 옮긴 뒤 더 작은 자식과 교환하며 내린다(sift-down).  임의 위치 i 삭제도 같다 — 맨 끝 원소를 i 로 옮기고, 부모보다 작으면 올리고(sift-up) 아니면 내린다(sift-down); 둘 중 *하나만* 일어난다.
//  ① 모든 삽입 순서(n ≤ 8)에서 전부 꺼내면 오름차순, 매 단계 힙 성질  ② 무작위 삽입·pop·임의 위치 삭제 100 만 연산을 std::multiset 과 대조 (중복 값 포함, 크기 최대 10^5)  ③ 교환 ≤ ⌊log2 n⌋, 전부 pop 하는 힙 정렬의 비교 ≤ 2·Σ⌊log2 i⌋ — 100 만 개를 std::sort 와 대조
//  ④ 임의 위치 삭제에서 sift-up 이 필요한 경우와 sift-down 이 필요한 경우가 모두 실제로 나타남.
struct MinHeap {
    std::vector<int> a; long swaps = 0, cmps = 0; long ups = 0, downs = 0;
    void siftUp(size_t i) { while (i > 0) { ++cmps; if (a[(i - 1) / 2] <= a[i]) break; std::swap(a[i], a[(i - 1) / 2]); i = (i - 1) / 2; ++swaps; } }
    void siftDown(size_t i) { size_t n = a.size(); for (;;) { size_t l = 2 * i + 1, r = l + 1, s = i; if (l < n) { ++cmps; if (a[l] < a[s]) s = l; } if (r < n) { ++cmps; if (a[r] < a[s]) s = r; } if (s == i) return; std::swap(a[i], a[s]); i = s; ++swaps; } }
    void push(int v) { a.push_back(v); siftUp(a.size() - 1); }
    int pop() { int top = a[0]; a[0] = a.back(); a.pop_back(); if (!a.empty()) siftDown(0); return top; }
    int eraseAt(size_t i) { int v = a[i]; a[i] = a.back(); a.pop_back(); if (i < a.size()) { if (i > 0 && a[(i - 1) / 2] > a[i]) { siftUp(i); ++ups; } else { siftDown(i); ++downs; } } return v; }
    bool valid() const { for (size_t i = 1; i < a.size(); ++i) if (a[(i - 1) / 2] > a[i]) return false; return true; }
};
long sumFloorLog2(int n) { long s = 0; for (int i = 1; i <= n; ++i) s += 31 - __builtin_clz((unsigned)i); return s; }

int main() {
    for (int n = 1; n <= 8; ++n) {                                                                               // ① 모든 삽입 순서 × 전부 pop
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0);
        do { MinHeap h; for (int v : perm) h.push(v); for (int want = 0; want < n; ++want) { assert(h.pop() == want); assert(h.valid()); } assert(h.a.empty()); } while (std::next_permutation(perm.begin(), perm.end()));
    }
    { MinHeap h; h.push(7); assert(h.pop() == 7 && h.a.empty()); h.push(3); h.push(3); assert(h.pop() == 3 && h.pop() == 3 && h.a.empty()); }          // 한 개·중복
    std::mt19937 rng(29); MinHeap h; std::multiset<int> ref;                                                     // ② 임의 연산 대조
    for (long step = 0; step < 1000000; ++step) {
        int op = (int)(rng() % 100);
        if (h.a.empty() || (op < 52 && h.a.size() < 100000)) { int v = (int)(rng() % 5000); h.push(v); ref.insert(v); }
        else if (op < 76) { int got = h.pop(); assert(got == *ref.begin()); ref.erase(ref.begin()); }
        else { size_t i = rng() % h.a.size(); int v = h.eraseAt(i); auto it = ref.find(v); assert(it != ref.end()); ref.erase(it); }
        if (step % 20011 == 0) { assert(h.valid() && h.a.size() == ref.size()); }
    }
    assert(h.valid() && h.a.size() == ref.size() && h.a[0] == *ref.begin()); std::vector<int> sortedA = h.a; std::sort(sortedA.begin(), sortedA.end()); assert(sortedA == std::vector<int>(ref.begin(), ref.end()));
    assert(h.ups > 0 && h.downs > 0);                                                                            // ④
    const int n = 1000000; MinHeap hs; std::vector<int> vals(n); for (int i = 0; i < n; ++i) { vals[i] = (int)(rng() % 1000000); hs.push(vals[i]); }
    hs.swaps = hs.cmps = 0; std::vector<int> out; out.reserve(n); long worstSwaps = 0; while (!hs.a.empty()) { long before = hs.swaps; size_t sz = hs.a.size(); out.push_back(hs.pop()); worstSwaps = std::max(worstSwaps, hs.swaps - before); assert(hs.swaps - before <= 31 - __builtin_clz((unsigned)sz)); }          // ③
    std::sort(vals.begin(), vals.end()); assert(out == vals && hs.cmps <= 2 * sumFloorLog2(n) && hs.swaps <= sumFloorLog2(n));
    std::cout << "HeapDelete: all insertion orders of up to 8 keys popped in sorted order, 10^6 random push/pop/erase-at operations matched std::multiset (" << h.ups << " sift-up and " << h.downs << " sift-down deletions), and heap-sorting 10^6 keys used " << hs.cmps << " comparisons (bound 2*sum floor(log2 i) = " << 2 * sumFloorLog2(n) << ")" << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## Heapify()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>

// Heapify(요약, 정본은 Queue.md Part 5): 노드 i 의 두 서브트리가 이미 힙일 때, i 를 아래로 내려 전체를 힙으로 만든다 (sift-down 한 번).  Floyd 의 build-heap = 마지막 내부 노드부터 루트까지 heapify 를 한 번씩 → O(N) (N 번 삽입의 O(N log N) 보다 싸다).
//  ① 전제 조건의 필요성: n = 7 의 5040 개 순열 중 두 서브트리가 모두 힙인 것은 정확히 5040·(1/3)·(1/3) = 560 개이고 전부 heapify(0) 으로 힙이 된다; 전제를 어긴 순열 중에는 heapify(0) 한 번으로 힙이 안 되는 것이 있다
//  ② build-heap: n ≤ 9 의 모든 순열에서 힙이 되고 만들어지는 서로 다른 힙의 수 = 훅 길이 공식 n!/∏(부분 트리 크기)  ③ 비용: 교환 ≤ Σ(노드 높이) = n − popcount(n), 비교 ≤ 2n — 무작위·정렬·역정렬 100 만 개로 확인하고 std::is_heap / std::make_heap 으로 독립 검증.
long swaps = 0, cmps = 0;
void heapify(std::vector<int>& a, size_t n, size_t i) {
    for (;;) { size_t l = 2 * i + 1, r = l + 1, s = i; if (l < n) { ++cmps; if (a[l] < a[s]) s = l; } if (r < n) { ++cmps; if (a[r] < a[s]) s = r; } if (s == i) return; std::swap(a[i], a[s]); i = s; ++swaps; }
}
void buildHeap(std::vector<int>& a) { for (size_t i = a.size() / 2; i-- > 0;) heapify(a, a.size(), i); }
bool isHeap(const std::vector<int>& a) { for (size_t i = 1; i < a.size(); ++i) if (a[(i - 1) / 2] > a[i]) return false; return true; }
bool subtreesAreHeaps(const std::vector<int>& a) { for (size_t j = 3; j < a.size(); ++j) if (a[(j - 1) / 2] > a[j]) return false; return true; }              // 루트의 두 서브트리가 힙인가 (루트를 부모로 갖는 간선 제외)

int main() {
    { const int n = 7; std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); int satisfied = 0, brokenAfter = 0;                                          // ①
      do { std::vector<int> a = perm; if (subtreesAreHeaps(a)) { ++satisfied; heapify(a, n, 0); assert(isHeap(a)); std::vector<int> s = a; std::sort(s.begin(), s.end()); assert(s == std::vector<int>({0, 1, 2, 3, 4, 5, 6})); }
           else { heapify(a, n, 0); if (!isHeap(a)) ++brokenAfter; } } while (std::next_permutation(perm.begin(), perm.end()));
      assert(satisfied == 560 && brokenAfter > 0); }
    for (int n = 1; n <= 9; ++n) {                                                                               // ② 모든 순열
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::set<std::vector<int>> heaps;
        do { std::vector<int> a = perm; buildHeap(a); assert(isHeap(a) && std::is_heap(a.begin(), a.end(), std::greater<int>())); heaps.insert(a); } while (std::next_permutation(perm.begin(), perm.end()));
        std::vector<long> sz(n, 1); for (int i = n - 1; i > 0; --i) sz[(i - 1) / 2] += sz[i]; double want = 1; for (int i = 1; i <= n; ++i) want *= i; for (int i = 0; i < n; ++i) want /= (double)sz[i];
        assert((double)heaps.size() > want - 0.5 && (double)heaps.size() < want + 0.5);                          // 모든 힙이 결과로 나온다(힙은 자기 자신으로 고정)
    }
    std::mt19937 rng(41); const int n = 1000000;
    for (int mode = 0; mode < 3; ++mode) {                                                                       // ③ 무작위 / 오름차순 / 내림차순(최악)
        std::vector<int> a(n); for (int i = 0; i < n; ++i) a[i] = mode == 0 ? (int)(rng() % 1000000) : mode == 1 ? i : n - i; std::vector<int> ref = a; swaps = cmps = 0; buildHeap(a);
        assert(isHeap(a) && std::is_heap(a.begin(), a.end(), std::greater<int>())); std::make_heap(ref.begin(), ref.end(), std::greater<int>()); std::vector<int> s1 = a, s2 = ref; std::sort(s1.begin(), s1.end()); std::sort(s2.begin(), s2.end()); assert(s1 == s2);
        assert(swaps <= n - __builtin_popcount(n) && cmps <= 2L * n);                                            // Σ 높이 = n − popcount(n)
        if (mode == 2) assert(swaps > n / 2);
    }
    std::cout << "Heapify: 560 of 5040 permutations satisfied the precondition and all became heaps (violators sometimes did not), Floyd build-heap produced exactly n!/prod(size) distinct heaps for n <= 9, and on 10^6 keys used at most n-popcount(n) swaps and 2n comparisons" << std::endl;
    return 0;
}
// Time Complexity: heapify O(log N), build-heap O(N)
// Space Complexity: O(1)
```
## BuildHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 힙 만들기(요약, 정본은 Queue.md Part 5): 마지막 내부 노드부터 루트까지 heapify 를 부르면 O(N)  (N log N 이 아니다).
// 높이 h 인 노드는 N/2^(h+1) 개이고 각 heapify 비용이 O(h) 이므로 합이 N·Σ h/2^(h+1) = O(N)
long swaps;
void heapify(std::vector<int>& a, size_t n, size_t i) {
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, s = i;
        if (l < n && a[l] < a[s]) s = l;
        if (r < n && a[r] < a[s]) s = r;
        if (s == i) return;
        std::swap(a[i], a[s]); swaps++; i = s;
    }
}

int main() {
    std::mt19937 rng(15);
    for (int n : {1000, 100000}) {
        std::vector<int> a(n); for (auto& x : a) x = rng();
        swaps = 0;
        for (int i = n / 2 - 1; i >= 0; i--) heapify(a, n, i);
        for (int i = 1; i < n; i++) assert(a[(i - 1) / 2] <= a[i]);
        assert(swaps < n);                                                      // 교환 횟수 < N (선형)
        std::cout << "BuildHeap n=" << n << " swaps=" << swaps << std::endl;
    }
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## HeapSort()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 힙 정렬(요약, 정본은 Queue.md Part 5): 최대 힙을 만든 뒤, 루트(최댓값)를 맨 뒤로 보내고 힙 크기를 줄이며 반복한다. 제자리, 최악 O(N log N)
void siftDown(std::vector<int>& a, size_t n, size_t i) {
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, m = i;
        if (l < n && a[l] > a[m]) m = l;
        if (r < n && a[r] > a[m]) m = r;
        if (m == i) return;
        std::swap(a[i], a[m]); i = m;
    }
}
void heapSort(std::vector<int>& a) {
    for (int i = (int)a.size() / 2 - 1; i >= 0; i--) siftDown(a, a.size(), i);
    for (size_t end = a.size(); end > 1; end--) { std::swap(a[0], a[end - 1]); siftDown(a, end - 1, 0); }
}

int main() {
    std::mt19937 rng(16);
    for (int iter = 0; iter < 200; iter++) {
        std::vector<int> a(rng() % 100 + 1); for (auto& x : a) x = rng() % 50;
        auto b = a; heapSort(a); std::sort(b.begin(), b.end());
        assert(a == b);
    }
    std::cout << "HeapSort verified on 200 random arrays." << std::endl;
    return 0;
}
// Time Complexity: O(N log N) 최악도 동일
// Space Complexity: O(1)
```
## FibonacciHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <climits>
#include <cmath>
#include <memory>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>
#include <cassert>

// 피보나치 힙: push·meld·findMin·decreaseKey 가 분할상환 O(1), extractMin 이 분할상환 O(log n).  Dijkstra/Prim 을 O(E + V log V) 로 만든다.
// 루트들을 원형 이중 연결 리스트로 느슨하게 두었다가, extractMin 때만 "차수가 같은 두 트리를 합치는" consolidate 를 한다.
// decreaseKey 는 부모보다 작아지면 그 노드를 루트 리스트로 잘라내고(cut), 자식을 하나 잃은 부모에 표시(mark)를 하다가 두 번째로 잃으면 연쇄 절단한다
struct FNode {
    int key, degree = 0; bool mark = false; FNode *p = nullptr, *child = nullptr, *l, *r;
    explicit FNode(int k) : key(k) { l = r = this; }
};
struct FibHeap {
    FNode* min = nullptr; size_t n = 0; std::vector<std::unique_ptr<FNode>> pool;
    void addRoot(FNode* x) {
        x->p = nullptr;
        if (!min) { x->l = x->r = x; min = x; return; }
        x->r = min->r; x->l = min; min->r->l = x; min->r = x;
        if (x->key < min->key) min = x;
    }
    FNode* push(int k) { pool.emplace_back(new FNode(k)); FNode* x = pool.back().get(); addRoot(x); n++; return x; }
    void meld(FibHeap& o) {                                                // 두 루트 리스트를 이어 붙인다: O(1)
        if (!o.min) return;
        for (auto& p : o.pool) pool.push_back(std::move(p));
        o.pool.clear();
        if (!min) min = o.min;
        else {
            FNode *a2 = min->r, *b2 = o.min->l;
            min->r = o.min; o.min->l = min; b2->r = a2; a2->l = b2;
            if (o.min->key < min->key) min = o.min;
        }
        n += o.n; o.min = nullptr; o.n = 0;
    }
    void link(FNode* y, FNode* x) {                                        // y 를 x 의 자식으로
        y->p = x; y->mark = false;
        if (!x->child) { x->child = y; y->l = y->r = y; }
        else { y->r = x->child->r; y->l = x->child; x->child->r->l = y; x->child->r = y; }
        x->degree++;
    }
    int maxDegree = 0;
    void consolidate() {
        std::vector<FNode*> roots; FNode* w = min; do { roots.push_back(w); w = w->r; } while (w != min);
        std::vector<FNode*> A(64, nullptr);
        for (FNode* x : roots) {
            int d = x->degree;
            while (A[d]) { FNode* y = A[d]; if (x->key > y->key) std::swap(x, y); link(y, x); A[d++] = nullptr; }
            A[d] = x;
        }
        min = nullptr; maxDegree = 0;
        for (FNode* x : A) if (x) { x->l = x->r = x; addRoot(x); maxDegree = std::max(maxDegree, x->degree); }
    }
    FNode* extractMin() {
        FNode* z = min; if (!z) return nullptr;
        if (z->child) {
            FNode* c = z->child; do { c->p = nullptr; c = c->r; } while (c != z->child);
            FNode *a2 = z->r, *b1 = z->child, *b2 = z->child->l;           // 자식 리스트를 z 바로 뒤에 끼운다
            z->r = b1; b1->l = z; b2->r = a2; a2->l = b2; z->child = nullptr;
        }
        if (z == z->r) min = nullptr;
        else { z->l->r = z->r; z->r->l = z->l; min = z->r; consolidate(); }
        n--; return z;
    }
    void cut(FNode* x, FNode* y) {
        if (x->r == x) y->child = nullptr;
        else { if (y->child == x) y->child = x->r; x->l->r = x->r; x->r->l = x->l; }
        y->degree--; x->mark = false; addRoot(x);
    }
    void decreaseKey(FNode* x, int k) {
        assert(k <= x->key); x->key = k; FNode* y = x->p;
        if (y && x->key < y->key) {
            cut(x, y);
            for (FNode* z = y; z->p; ) { FNode* up = z->p; if (!z->mark) { z->mark = true; break; } cut(z, up); z = up; }   // 연쇄 절단
        }
        if (x->key < min->key) min = x;
    }
    void erase(FNode* x) { decreaseKey(x, INT_MIN); extractMin(); }
};

int main() {
    std::mt19937 rng(7);
    FibHeap h; std::multiset<int> ms; std::vector<FNode*> hs; std::vector<char> alive; std::unordered_map<FNode*, int> idx;
    for (int step = 0; step < 20000; step++) {
        int op = rng() % 10;
        if (op < 5 || ms.empty()) { int k = rng() % 100000 + 1000; FNode* x = h.push(k); idx[x] = hs.size(); hs.push_back(x); alive.push_back(1); ms.insert(k); }
        else if (op < 7) { FNode* z = h.extractMin(); assert(z->key == *ms.begin()); ms.erase(ms.begin()); alive[idx[z]] = 0; }
        else if (op < 9) {
            int i; do { i = rng() % hs.size(); } while (!alive[i]);
            int old = hs[i]->key, nk = old - (int)(rng() % 1000) - 1; h.decreaseKey(hs[i], nk);
            ms.erase(ms.find(old)); ms.insert(nk);
        } else { int i; do { i = rng() % hs.size(); } while (!alive[i]); ms.erase(ms.find(hs[i]->key)); h.erase(hs[i]); alive[i] = 0; }
        assert(h.n == ms.size()); if (!ms.empty()) assert(h.min->key == *ms.begin());
    }
    FibHeap a, b; std::multiset<int> all;                                  // meld 검사
    for (int i = 0; i < 500; i++) { int x = rng() % 1000; a.push(x); all.insert(x); int y = rng() % 1000; b.push(y); all.insert(y); }
    a.meld(b); assert(b.n == 0 && a.n == 1000);
    while (a.n) { FNode* z = a.extractMin(); assert(z->key == *all.begin()); all.erase(all.begin()); }
    FibHeap big; for (int i = 0; i < 100000; i++) big.push((int)(rng() % 1000000));
    big.extractMin();                                                      // consolidate: 차수가 모두 달라지고 최대 차수는 log_phi(n) 이하
    assert(big.maxDegree <= (int)(std::log((double)big.n) / std::log(1.6180339887)) + 1);
    std::cout << "FibonacciHeap: 20000 mixed ops match multiset; max root degree after consolidate of 1e5 keys = " << big.maxDegree << std::endl;
    return 0;
}
// Time Complexity: push/meld/decreaseKey 분할상환 O(1), extractMin 분할상환 O(log N)
// Space Complexity: O(N)
```
## BinomialHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <memory>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 이항 힙: 이항 트리 B0, B1, B2, ... (Bk 는 노드 2^k 개, 루트 차수 k) 들의 모음. n 의 이진 표현이 곧 구성이다 (n = 13 = 1101 -> B3, B2, B0).
// 두 힙의 합치기(unite)는 이진수 덧셈과 똑같다: 차수가 같은 두 트리를 합치면 올림이 생긴다.  push = 크기 1 짜리 힙과 unite, extractMin = 루트의 자식들을 힙으로 보고 unite
struct BNode { int key, id, degree = 0; BNode *p = nullptr, *child = nullptr, *sibling = nullptr; };
struct BinomialHeap {
    BNode* head = nullptr; size_t n = 0; std::vector<std::unique_ptr<BNode>> pool; std::vector<BNode*> loc;
    static void link(BNode* y, BNode* z) { y->p = z; y->sibling = z->child; z->child = y; z->degree++; }   // y 를 z 의 첫 자식으로
    static BNode* mergeLists(BNode* a, BNode* b) {                         // 차수 오름차순 두 리스트를 병합
        BNode dummy; BNode* t = &dummy;
        while (a && b) { if (a->degree <= b->degree) { t->sibling = a; a = a->sibling; } else { t->sibling = b; b = b->sibling; } t = t->sibling; }
        t->sibling = a ? a : b; return dummy.sibling;
    }
    static BNode* unite(BNode* a, BNode* b) {
        BNode* h = mergeLists(a, b); if (!h) return nullptr;
        BNode *prev = nullptr, *x = h, *next = x->sibling;
        while (next) {
            if (x->degree != next->degree || (next->sibling && next->sibling->degree == x->degree)) { prev = x; x = next; }
            else if (x->key <= next->key) { x->sibling = next->sibling; link(next, x); }
            else { if (!prev) h = next; else prev->sibling = next; link(x, next); x = next; }
            next = x->sibling;
        }
        return h;
    }
    int push(int key) {
        int id = loc.size(); pool.emplace_back(new BNode{key, id}); loc.push_back(pool.back().get());
        head = unite(head, loc.back()); n++; return id;
    }
    int findMin() const { int m = INT32_MAX; for (BNode* x = head; x; x = x->sibling) m = std::min(m, x->key); return m; }
    int extractMin(int& id) {
        BNode *best = head, *bestPrev = nullptr;
        for (BNode *p = nullptr, *x = head; x; p = x, x = x->sibling) if (x->key < best->key) { best = x; bestPrev = p; }
        if (bestPrev) bestPrev->sibling = best->sibling; else head = best->sibling;
        BNode* rev = nullptr;                                              // 자식 리스트를 뒤집어 차수 오름차순으로
        for (BNode* c = best->child; c; ) { BNode* nx = c->sibling; c->sibling = rev; c->p = nullptr; rev = c; c = nx; }
        head = unite(head, rev); n--; id = best->id; loc[id] = nullptr; return best->key;
    }
    void decreaseKey(int id, int k) {                                      // 부모와 키·id 를 맞바꾸며 올라간다
        BNode* x = loc[id]; assert(k <= x->key); x->key = k;
        while (x->p && x->key < x->p->key) { BNode* p = x->p; std::swap(x->key, p->key); std::swap(x->id, p->id); loc[x->id] = x; loc[p->id] = p; x = p; }
    }
};

int main() {
    BinomialHeap h;
    for (int i = 1; i <= 1000; i++) { h.push(1000 - i); int trees = 0; for (BNode* x = h.head; x; x = x->sibling) trees++; assert(trees == __builtin_popcount(i)); }
    // 트리 개수 = n 의 이진 표현에서 1 의 개수, 각 루트의 차수는 켜진 비트의 위치와 같다
    int expectDeg = 0; for (BNode* x = h.head; x; x = x->sibling) { while (!((1000 >> expectDeg) & 1)) expectDeg++; assert(x->degree == expectDeg++); }

    std::mt19937 rng(3); BinomialHeap q; std::multiset<int> ms; std::vector<char> alive;
    for (int step = 0; step < 15000; step++) {
        int op = rng() % 10;
        if (op < 5 || ms.empty()) { int k = rng() % 100000 + 1000; int id = q.push(k); alive.push_back(1); assert(id == (int)alive.size() - 1); ms.insert(k); }
        else if (op < 8) { int id; int k = q.extractMin(id); assert(k == *ms.begin()); ms.erase(ms.begin()); alive[id] = 0; }
        else {
            int i; do { i = rng() % alive.size(); } while (!alive[i]);
            int old = q.loc[i]->key, nk = old - (int)(rng() % 500) - 1; q.decreaseKey(i, nk); ms.erase(ms.find(old)); ms.insert(nk);
        }
        assert(q.n == ms.size()); if (!ms.empty()) assert(q.findMin() == *ms.begin());
    }
    std::cout << "BinomialHeap: " << h.n << " keys -> trees = popcount, 15000 mixed ops match multiset" << std::endl;
    return 0;
}
// Time Complexity: push·unite·extractMin·decreaseKey 모두 O(log N) (push 는 분할상환 O(1))
// Space Complexity: O(N)
```
## PairingHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <memory>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>
#include <cassert>

// 페어링 힙: "힙 순서 트리"를 자식 리스트(첫 자식-다음 형제)로 표현한 가장 단순한 meld 가능 힙. 구현이 짧고 실전에서 피보나치 힙보다 빠른 경우가 많다.
// meld(a,b) 는 루트가 큰 쪽을 작은 쪽의 첫 자식으로 붙이면 끝(O(1)).  deleteMin 은 루트의 자식들을 "왼쪽→오른쪽으로 둘씩 짝 짓고(meld), 오른쪽→왼쪽으로 하나로 합치는" 2-pass 로 처리한다
struct PNode { int key; PNode *child = nullptr, *sibling = nullptr, *prev = nullptr; };   // prev: 첫 자식이면 부모, 아니면 왼쪽 형제
struct PairingHeap {
    PNode* root = nullptr; size_t n = 0; std::vector<std::unique_ptr<PNode>> pool;
    static PNode* meld(PNode* a, PNode* b) {
        if (!a) return b; if (!b) return a;
        if (b->key < a->key) std::swap(a, b);
        b->prev = a; b->sibling = a->child; if (a->child) a->child->prev = b; a->child = b;
        a->prev = a->sibling = nullptr; return a;
    }
    PNode* push(int k) { pool.emplace_back(new PNode{k}); PNode* x = pool.back().get(); root = meld(root, x); n++; return x; }
    void meld(PairingHeap& o) { for (auto& p : o.pool) pool.push_back(std::move(p)); o.pool.clear(); root = meld(root, o.root); n += o.n; o.root = nullptr; o.n = 0; }
    static PNode* twoPass(PNode* first) {
        if (!first) return nullptr;
        std::vector<PNode*> v;
        for (PNode* c = first; c; ) {
            PNode *a = c, *b = a->sibling, *nx = b ? b->sibling : nullptr;
            a->sibling = a->prev = nullptr; if (b) b->sibling = b->prev = nullptr;
            v.push_back(b ? meld(a, b) : a); c = nx;
        }
        PNode* r = v.back(); for (int i = (int)v.size() - 2; i >= 0; i--) r = meld(v[i], r);
        return r;
    }
    PNode* popMin() {
        PNode* z = root; root = twoPass(z->child); if (root) root->prev = nullptr; n--; z->child = nullptr; return z;
    }
    void decreaseKey(PNode* x, int k) {
        assert(k <= x->key); x->key = k; if (x == root) return;
        if (x->prev->child == x) x->prev->child = x->sibling; else x->prev->sibling = x->sibling;   // 부모(또는 형제)에서 떼어낸다
        if (x->sibling) x->sibling->prev = x->prev;
        x->prev = x->sibling = nullptr; root = meld(root, x);
    }
};

int main() {
    std::mt19937 rng(11);
    PairingHeap h; std::multiset<int> ms; std::vector<PNode*> hs; std::vector<char> alive; std::unordered_map<PNode*, int> idx;
    for (int step = 0; step < 20000; step++) {
        int op = rng() % 10;
        if (op < 5 || ms.empty()) { int k = rng() % 100000 + 1000; PNode* x = h.push(k); idx[x] = hs.size(); hs.push_back(x); alive.push_back(1); ms.insert(k); }
        else if (op < 7) { PNode* z = h.popMin(); assert(z->key == *ms.begin()); ms.erase(ms.begin()); alive[idx[z]] = 0; }
        else {
            int i; do { i = rng() % hs.size(); } while (!alive[i]);
            int old = hs[i]->key, nk = old - (int)(rng() % 700) - 1; h.decreaseKey(hs[i], nk); ms.erase(ms.find(old)); ms.insert(nk);
        }
        assert(h.n == ms.size()); if (!ms.empty()) assert(h.root->key == *ms.begin());
    }
    PairingHeap a, b; std::multiset<int> all;
    for (int i = 0; i < 400; i++) { int x = rng() % 1000, y = rng() % 1000; a.push(x); b.push(y); all.insert(x); all.insert(y); }
    a.meld(b); while (a.n) { PNode* z = a.popMin(); assert(z->key == *all.begin()); all.erase(all.begin()); }
    PairingHeap sorted; std::vector<int> v(5000); for (auto& x : v) x = rng() % 100000;
    for (int x : v) sorted.push(x);
    std::sort(v.begin(), v.end()); for (int x : v) assert(sorted.popMin()->key == x);                // 힙 정렬
    std::cout << "PairingHeap: 20000 mixed ops match multiset, meld and heap-sort OK" << std::endl;
    return 0;
}
// Time Complexity: push/meld O(1), deleteMin 분할상환 O(log N), decreaseKey 분할상환 o(log N) (정확한 한계는 미해결 문제)
// Space Complexity: O(N)
```
## LeftistHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <memory>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 좌편향 힙(leftist heap): 각 노드의 npl(null path length, 가장 가까운 빈 자리까지의 거리)을 두고 "왼쪽 자식의 npl >= 오른쪽 자식의 npl" 을 유지한다.
// 그러면 오른쪽 가지(right spine)의 길이가 O(log n) 이므로, 병합을 오른쪽 가지만 따라 내려가며 재귀로 처리할 수 있다.  insert/pop 은 모두 merge 한 번
struct LNode { int key, npl = 1; LNode *l = nullptr, *r = nullptr; };
int npl(LNode* x) { return x ? x->npl : 0; }
LNode* merge(LNode* a, LNode* b) {
    if (!a) return b; if (!b) return a;
    if (b->key < a->key) std::swap(a, b);
    a->r = merge(a->r, b);
    if (npl(a->l) < npl(a->r)) std::swap(a->l, a->r);                     // 왼쪽이 더 "무겁게"
    a->npl = npl(a->r) + 1; return a;
}
struct LeftistHeap {
    LNode* root = nullptr; size_t n = 0; std::vector<std::unique_ptr<LNode>> pool;
    void push(int k) { pool.emplace_back(new LNode{k}); root = merge(root, pool.back().get()); n++; }
    int top() const { return root->key; }
    int pop() { int k = root->key; root = merge(root->l, root->r); n--; return k; }
    void meld(LeftistHeap& o) { for (auto& p : o.pool) pool.push_back(std::move(p)); o.pool.clear(); root = merge(root, o.root); n += o.n; o.root = nullptr; o.n = 0; }
};
bool valid(LNode* x) {                                                     // 힙 순서 + 좌편향 성질 + npl 값
    if (!x) return true;
    if (x->l && x->l->key < x->key) return false;
    if (x->r && x->r->key < x->key) return false;
    if (npl(x->l) < npl(x->r) || x->npl != npl(x->r) + 1) return false;
    return valid(x->l) && valid(x->r);
}

int main() {
    std::mt19937 rng(19);
    LeftistHeap h; std::priority_queue<int, std::vector<int>, std::greater<int>> pq;
    for (int step = 0; step < 20000; step++) {
        if (rng() % 3 < 2 || pq.empty()) { int k = rng() % 100000; h.push(k); pq.push(k); }
        else { assert(h.top() == pq.top()); assert(h.pop() == pq.top()); pq.pop(); }
        assert(h.n == pq.size());
        if (step % 1000 == 0) assert(valid(h.root));
    }
    assert(npl(h.root) <= std::log2(h.n + 1) + 1);                         // 오른쪽 가지의 길이 <= log2(n+1)
    LeftistHeap a, b; std::vector<int> all;
    for (int i = 0; i < 700; i++) { int x = rng() % 5000, y = rng() % 5000; a.push(x); b.push(y); all.push_back(x); all.push_back(y); }
    a.meld(b); assert(valid(a.root) && b.n == 0);
    std::sort(all.begin(), all.end()); for (int x : all) assert(a.pop() == x);
    LeftistHeap lopsided; for (int i = 0; i < 4096; i++) lopsided.push(i);   // 정렬된 입력에도 오른쪽 가지는 짧다
    assert(npl(lopsided.root) <= 13);
    std::cout << "LeftistHeap: merge-only heap OK, right spine <= log2(n+1)" << std::endl;
    return 0;
}
// Time Complexity: merge·push·pop O(log N)
// Space Complexity: O(N)
```
## DAryHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <functional>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// d-ary 힙: 자식이 d 개인 완전 d-분 트리를 배열에 담는다. 부모 (i-1)/d, 자식 d*i+1 .. d*i+d.
// 높이가 log_d n 으로 낮아져서 push / decreaseKey (위로 올리기) 가 빨라지고, pop (아래로 내리기) 은 레벨마다 d 개를 비교하므로 느려진다.
// decreaseKey 가 많은 Dijkstra 에서는 d = 2 + E/V 정도가 좋다.  아래는 id(0..N-1) 로 원소를 가리키는 "인덱스 우선순위 큐"
template <int D> struct IndexedDHeap {
    std::vector<int> heap, pos, key; long compares = 0;
    explicit IndexedDHeap(int n) : pos(n, -1), key(n) {}
    bool empty() const { return heap.empty(); }
    void up(int i) {
        int id = heap[i];
        while (i > 0) { int p = (i - 1) / D; compares++; if (key[heap[p]] <= key[id]) break; heap[i] = heap[p]; pos[heap[i]] = i; i = p; }
        heap[i] = id; pos[id] = i;
    }
    void down(int i) {
        int id = heap[i], n = heap.size();
        for (;;) {
            int c = D * i + 1; if (c >= n) break;
            int best = c; for (int j = c + 1; j < std::min(n, c + D); j++) { compares++; if (key[heap[j]] < key[heap[best]]) best = j; }
            compares++; if (key[heap[best]] >= key[id]) break;
            heap[i] = heap[best]; pos[heap[i]] = i; i = best;
        }
        heap[i] = id; pos[id] = i;
    }
    void push(int id, int k) { key[id] = k; heap.push_back(id); up(heap.size() - 1); }
    int pop() { int top = heap[0], last = heap.back(); pos[top] = -1; heap.pop_back(); if (!heap.empty()) { heap[0] = last; pos[last] = 0; down(0); } return top; }
    void decrease(int id, int k) { key[id] = k; up(pos[id]); }
    bool contains(int id) const { return pos[id] >= 0; }
};
template <int D> std::vector<long> dijkstra(const std::vector<std::vector<std::pair<int, int>>>& g, int s, long& cmp) {
    std::vector<long> dist(g.size(), 1L << 60); IndexedDHeap<D> pq(g.size()); dist[s] = 0; pq.push(s, 0);
    while (!pq.empty()) {
        int u = pq.pop();
        for (auto [v, w] : g[u]) if (dist[u] + w < dist[v]) {
            bool had = pq.contains(v); dist[v] = dist[u] + w;
            if (had) pq.decrease(v, dist[v]); else pq.push(v, dist[v]);   // 키가 int 라 이 데모에서는 거리가 int 범위
        }
    }
    cmp = pq.compares; return dist;
}
template <int D> void fuzz() {
    std::mt19937 rng(D); IndexedDHeap<D> h(3000); std::set<std::pair<int, int>> ref; std::vector<int> cur(3000, -1);
    for (int step = 0; step < 30000; step++) {
        int id = rng() % 3000;
        if (cur[id] < 0 && rng() % 2) { int k = rng() % 100000 + 500; h.push(id, k); ref.insert({k, id}); cur[id] = k; }
        else if (cur[id] >= 0 && rng() % 2) { int nk = cur[id] - (int)(rng() % 400); h.decrease(id, nk); ref.erase({cur[id], id}); ref.insert({nk, id}); cur[id] = nk; }
        else if (!ref.empty() && rng() % 3 == 0) {
            int top = h.pop(); assert(h.key[top] == ref.begin()->first);       // 같은 키면 id 는 다를 수 있으므로 키만 비교
            auto it = ref.find({h.key[top], top}); assert(it != ref.end()); ref.erase(it); cur[top] = -1;
        }
        assert(h.heap.size() == ref.size());
    }
}
int main() {
    fuzz<2>(); fuzz<3>(); fuzz<4>(); fuzz<8>();
    std::mt19937 rng(42); int N = 2000, M = 20000;
    std::vector<std::vector<std::pair<int, int>>> g(N);
    for (int i = 0; i < M; i++) { int u = rng() % N, v = rng() % N, w = rng() % 100 + 1; g[u].push_back({v, w}); g[v].push_back({u, w}); }
    // 기준: 표준 priority_queue 로 구현한 lazy Dijkstra
    std::vector<long> ref(N, 1L << 60); std::priority_queue<std::pair<long, int>, std::vector<std::pair<long, int>>, std::greater<>> q; ref[0] = 0; q.push({0, 0});
    while (!q.empty()) { auto [d, u] = q.top(); q.pop(); if (d > ref[u]) continue; for (auto [v, w] : g[u]) if (d + w < ref[v]) { ref[v] = d + w; q.push({ref[v], v}); } }
    long c2, c4, c8; assert(dijkstra<2>(g, 0, c2) == ref); assert(dijkstra<4>(g, 0, c4) == ref); assert(dijkstra<8>(g, 0, c8) == ref);
    auto levels = [](long n, int d) { int h = 0; for (long i = n - 1; i > 0; i = (i - 1) / d) h++; return h; };
    assert(levels(1000000, 4) * 2 <= levels(1000000, 2) + 1 && levels(1000000, 8) < levels(1000000, 4));
    std::cout << "d-ary heap: Dijkstra compares  d=2: " << c2 << ", d=4: " << c4 << ", d=8: " << c8
              << " | depth for 1e6 keys  d=2: " << levels(1000000, 2) << ", d=4: " << levels(1000000, 4) << ", d=8: " << levels(1000000, 8) << std::endl;
    return 0;
}
// Time Complexity: push·decreaseKey O(log_d N), pop O(d log_d N)
// Space Complexity: O(N)
```
## MinMaxHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 최소-최대 힙: 하나의 배열 힙으로 최솟값과 최댓값을 모두 O(1) 로 보고 O(log n) 에 뺄 수 있다 (양방향 우선순위 큐).
// 깊이가 짝수인 레벨은 "자기 아래 모든 원소보다 작다"(min 레벨), 홀수 레벨은 "모든 후손보다 크다"(max 레벨).  최솟값은 a[0], 최댓값은 a[1], a[2] 중 큰 쪽.
// 삽입은 부모와 비교해 레벨 종류를 바꾼 뒤 같은 종류의 조부모 사슬로 올라가고, 삭제는 자식·손자 중 극값과 교환하며 내려간다
struct MinMaxHeap {
    std::vector<int> a;
    static bool minLevel(size_t i) { return (63 - __builtin_clzll(i + 1)) % 2 == 0; }
    void bubbleUpMin(size_t i) { while (i >= 3) { size_t g = ((i - 1) / 2 - 1) / 2; if (a[i] < a[g]) { std::swap(a[i], a[g]); i = g; } else break; } }
    void bubbleUpMax(size_t i) { while (i >= 3) { size_t g = ((i - 1) / 2 - 1) / 2; if (a[i] > a[g]) { std::swap(a[i], a[g]); i = g; } else break; } }
    void push(int x) {
        a.push_back(x); size_t i = a.size() - 1; if (!i) return;
        size_t p = (i - 1) / 2;
        if (minLevel(i)) { if (a[i] > a[p]) { std::swap(a[i], a[p]); bubbleUpMax(p); } else bubbleUpMin(i); }
        else             { if (a[i] < a[p]) { std::swap(a[i], a[p]); bubbleUpMin(p); } else bubbleUpMax(i); }
    }
    template <class Less> void trickleDown(size_t i, Less less) {          // less 가 < 이면 min 레벨, > 이면 max 레벨
        size_t n = a.size();
        while (2 * i + 1 < n) {
            size_t m = 2 * i + 1;                                          // 자식과 손자 중 "가장 극단적인" 것
            for (size_t c : {2 * i + 2, 4 * i + 3, 4 * i + 4, 4 * i + 5, 4 * i + 6}) if (c < n && less(a[c], a[m])) m = c;
            if (m > 2 * i + 2) {                                           // 손자인 경우
                if (!less(a[m], a[i])) break;
                std::swap(a[m], a[i]);
                size_t p = (m - 1) / 2; if (less(a[p], a[m])) std::swap(a[m], a[p]);   // 새 값이 부모(반대 레벨)와 충돌하면 교환
                i = m;
            } else { if (less(a[m], a[i])) std::swap(a[m], a[i]); break; }  // 자식인 경우는 잎 직전이라 끝
        }
    }
    int min() const { return a[0]; }
    int max() const { return a.size() == 1 ? a[0] : a.size() == 2 ? a[1] : std::max(a[1], a[2]); }
    int popMin() { int x = a[0]; a[0] = a.back(); a.pop_back(); if (!a.empty()) trickleDown(0, std::less<int>()); return x; }
    int popMax() {
        size_t i = a.size() == 1 ? 0 : a.size() == 2 ? 1 : (a[1] >= a[2] ? 1 : 2);
        int x = a[i]; a[i] = a.back(); a.pop_back(); if (i < a.size()) trickleDown(i, std::greater<int>()); return x;
    }
    bool valid() const {                                                   // 모든 노드가 자기 레벨의 규칙을 후손 전체에 대해 만족하는가 (O(n^2), 테스트용)
        for (size_t i = 0; i < a.size(); i++) {
            std::vector<size_t> st = {2 * i + 1, 2 * i + 2};
            while (!st.empty()) { size_t j = st.back(); st.pop_back(); if (j >= a.size()) continue;
                if (minLevel(i) ? a[j] < a[i] : a[j] > a[i]) return false; st.push_back(2 * j + 1); st.push_back(2 * j + 2); }
        }
        return true;
    }
};

int main() {
    std::mt19937 rng(31);
    MinMaxHeap h; std::multiset<int> ms;
    for (int step = 0; step < 6000; step++) {
        int op = rng() % 6;
        if (op < 3 || ms.empty()) { int x = rng() % 1000; h.push(x); ms.insert(x); }
        else if (op < 5) { assert(h.popMin() == *ms.begin()); ms.erase(ms.begin()); }
        else { assert(h.popMax() == *ms.rbegin()); ms.erase(std::prev(ms.end())); }
        if (!ms.empty()) { assert(h.min() == *ms.begin() && h.max() == *ms.rbegin()); }
        if (step % 100 == 0) assert(h.valid());
    }
    std::vector<int> v; while (!h.a.empty()) { v.push_back(h.popMin()); if (!h.a.empty()) v.push_back(h.popMax()); }   // 양 끝을 번갈아 꺼내기
    std::vector<int> ref(ms.begin(), ms.end()); std::vector<int> expect;
    for (size_t lo = 0, hi = ref.size(); lo < hi; ) { expect.push_back(ref[lo++]); if (lo < hi) expect.push_back(ref[--hi]); }
    assert(v == expect);
    std::cout << "MinMaxHeap: min/max both O(1), 6000 mixed ops match multiset" << std::endl;
    return 0;
}
// Time Complexity: min/max O(1), push·popMin·popMax O(log N)
// Space Complexity: O(N)
```
# Part 9. 다중 트리
## TrieInsert() & TrieSearch()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 트라이(트리 관점의 요약, 정본은 String.md Part 8): 문자마다 간선 하나, 단어 끝에 표시.  삽입·검색은 단어 길이 L 만큼의 걸음 — 사전 크기와 무관.  노드는 arena(벡터)에 두고 인덱스로 잇는다(raw new/delete 없음, 누수 불가).
//  ① 전수: 알파벳 {a, b}, 길이 ≤ 3 인 15 개 문자열의 *모든 부분 집합* 32768 개 × 길이 ≤ 4 인 31 개 질의 — search / startsWith / countPrefix / 사전순 목록 / 노드 수(= 서로 다른 접두사 수)를 std::set 으로 대조
//  ② 무작위 대조: 알파벳 26, 빈 단어 포함, 3 만 단어와 3 만 개의 없는 단어 질의  ③ 길이 20 만 의 단어도 반복 구현이라 스택 오버플로 없이 삽입·검색.
struct Trie {
    std::vector<std::array<int, 26>> nx; std::vector<int> pass, freeList; std::vector<char> end; size_t live = 0, words = 0;   // pass[u] = u 의 부분 트리에 있는 단어 수, live = 사용 중인 노드 수
    Trie() { newNode(); }                                                                                        // 노드 0 = 루트
    int newNode() { std::array<int, 26> e; e.fill(-1); int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); nx[u] = e; pass[u] = 0; end[u] = 0; } else { nx.push_back(e); pass.push_back(0); end.push_back(0); u = (int)nx.size() - 1; } ++live; return u; }
    int find(const std::string& s) const { int u = 0; for (char c : s) { u = nx[u][c - 'a']; if (u < 0) return -1; } return u; }
    bool search(const std::string& w) const { int u = find(w); return u >= 0 && end[u]; }
    bool startsWith(const std::string& p) const { return find(p) >= 0; }
    int countPrefix(const std::string& p) const { int u = find(p); return u < 0 ? 0 : pass[u]; }
    bool insert(const std::string& w) {
        if (search(w)) return false; int u = 0; ++pass[0];
        for (char c : w) { int v = nx[u][c - 'a']; if (v < 0) { v = newNode(); nx[u][c - 'a'] = v; } u = v; ++pass[u]; }              // 주의: newNode() 가 nx 를 재할당하므로 참조를 들고 있지 않는다
        end[u] = 1; ++words; return true; }
    std::vector<std::string> list() const {                                                                      // 사전순 단어 목록: 반복 DFS
        std::vector<std::string> out; std::string cur; std::vector<std::pair<int, int>> st = {{0, 0}}; if (end[0]) out.push_back(cur);
        while (!st.empty()) { auto& top = st.back(); int u = top.first; int& c = top.second; while (c < 26 && nx[u][c] < 0) ++c;
            if (c == 26) { st.pop_back(); if (!cur.empty()) cur.pop_back(); continue; }
            int v = nx[u][c]; cur.push_back((char)('a' + c)); ++c; if (end[v]) out.push_back(cur); st.push_back({v, 0}); }
        return out; }
};
size_t distinctPrefixes(const std::set<std::string>& s) { std::set<std::string> p; for (auto& w : s) for (size_t k = 0; k <= w.size(); ++k) p.insert(w.substr(0, k)); return std::max<size_t>(1, p.size()); }                       // 빈 접두사 포함 = 루트 포함 노드 수 (루트는 빈 트라이에도 있다)
int refCountPrefix(const std::set<std::string>& s, const std::string& p) { int c = 0; for (auto& w : s) if (w.compare(0, p.size(), p) == 0 && w.size() >= p.size()) ++c; return c; }

int main() {
    std::vector<std::string> universe = {""}; for (int len = 1; len <= 3; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; universe.push_back(s); }   // 15 개
    std::vector<std::string> queries = {""}; for (int len = 1; len <= 4; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; queries.push_back(s); }   // 31 개
    assert(universe.size() == 15 && queries.size() == 31);
    for (int mask = 0; mask < (1 << 15); ++mask) {
        Trie t; std::set<std::string> ref; for (int i = 0; i < 15; ++i) if (mask >> i & 1) { bool a = t.insert(universe[i]); bool r = ref.insert(universe[i]).second; assert(a == r); assert(!t.insert(universe[i])); }
        assert(t.words == ref.size() && t.live == distinctPrefixes(ref));
        for (auto& q : queries) { assert(t.search(q) == (ref.count(q) > 0)); assert(t.countPrefix(q) == refCountPrefix(ref, q)); assert(t.startsWith(q) == (q.empty() || refCountPrefix(ref, q) > 0)); }
        assert(t.list() == std::vector<std::string>(ref.begin(), ref.end()));
    }
    std::mt19937 rng(13); Trie t; std::set<std::string> ref;
    for (int i = 0; i < 30000; ++i) { std::string w; int len = (int)(rng() % 11); for (int j = 0; j < len; ++j) w += (char)('a' + rng() % 26); bool a = t.insert(w); bool r = ref.insert(w).second; assert(a == r); }
    assert(t.words == ref.size() && t.live == distinctPrefixes(ref) && t.list() == std::vector<std::string>(ref.begin(), ref.end()));
    for (int i = 0; i < 30000; ++i) { std::string q; int len = (int)(rng() % 11); for (int j = 0; j < len; ++j) q += (char)('a' + rng() % 26); assert(t.search(q) == (ref.count(q) > 0)); auto it = ref.lower_bound(q); bool pref = it != ref.end() && it->compare(0, q.size(), q) == 0; assert(t.startsWith(q) == pref); }
    for (auto& w : ref) assert(t.search(w));
    { Trie big; std::string longWord(200000, 'a'); assert(big.insert(longWord) && big.search(longWord) && !big.search(std::string(199999, 'a')) && big.startsWith(std::string(199999, 'a')) && big.live == 200001); }
    std::cout << "TrieInsert & TrieSearch: all 32768 subsets of 15 short strings matched std::set on search/prefix/count/listing/node count; 3*10^4 random words and queries matched; a 200000-letter word was handled iteratively" << std::endl;
    return 0;
}
// Time Complexity: O(L)
// Space Complexity: O(총 문자 수 · 알파벳) — 노드당 26 개의 간선 슬롯
```

## TrieDelete()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 트라이 삭제(트리 관점의 요약, 정본은 String.md Part 8): ① 단어 끝 표시를 지우고 ② 더 이상 어떤 단어도 지나가지 않는 노드(pass == 0)를 *아래에서 위로* 잘라낸다.  접두사가 다른 단어의 일부이면 표시만 지우고 노드는 남겨야 하고, 가지가 하나뿐이면 루트까지 잘린다.
//  pass[u] = u 의 부분 트리에 있는 단어 수 를 유지하면 "잘라도 되는가"가 O(1) 판정이다; 잘린 노드는 free-list 로 재사용된다.
//  ① 전수: 알파벳 {a, b}, 길이 ≤ 3 인 15 개 문자열의 모든 부분 집합(32768) × 31 개 질의 문자열 각각을 삭제 — 삭제 성공 여부, 남은 단어, *노드 수 = 남은 단어들의 서로 다른 접두사 수* (정확한 가지치기)를 std::set 으로 대조
//  ② 무작위 삽입·삭제·검색 100 만 연산을 대조 (노드 수 검증 포함, arena 가 최대 동시 노드 수를 넘지 않음)  ③ 길이 20 만 의 단어를 지우면 노드가 루트 하나만 남는다.
struct Trie {
    std::vector<std::array<int, 26>> nx; std::vector<int> pass, freeList; std::vector<char> end; size_t live = 0, words = 0;   // pass[u] = u 의 부분 트리에 있는 단어 수, live = 사용 중인 노드 수
    Trie() { newNode(); }                                                                                        // 노드 0 = 루트
    int newNode() { std::array<int, 26> e; e.fill(-1); int u; if (!freeList.empty()) { u = freeList.back(); freeList.pop_back(); nx[u] = e; pass[u] = 0; end[u] = 0; } else { nx.push_back(e); pass.push_back(0); end.push_back(0); u = (int)nx.size() - 1; } ++live; return u; }
    int find(const std::string& s) const { int u = 0; for (char c : s) { u = nx[u][c - 'a']; if (u < 0) return -1; } return u; }
    bool search(const std::string& w) const { int u = find(w); return u >= 0 && end[u]; }
    bool startsWith(const std::string& p) const { return find(p) >= 0; }
    int countPrefix(const std::string& p) const { int u = find(p); return u < 0 ? 0 : pass[u]; }
    bool insert(const std::string& w) {
        if (search(w)) return false; int u = 0; ++pass[0];
        for (char c : w) { int v = nx[u][c - 'a']; if (v < 0) { v = newNode(); nx[u][c - 'a'] = v; } u = v; ++pass[u]; }              // 주의: newNode() 가 nx 를 재할당하므로 참조를 들고 있지 않는다
        end[u] = 1; ++words; return true; }
    std::vector<std::string> list() const {                                                                      // 사전순 단어 목록: 반복 DFS
        std::vector<std::string> out; std::string cur; std::vector<std::pair<int, int>> st = {{0, 0}}; if (end[0]) out.push_back(cur);
        while (!st.empty()) { auto& top = st.back(); int u = top.first; int& c = top.second; while (c < 26 && nx[u][c] < 0) ++c;
            if (c == 26) { st.pop_back(); if (!cur.empty()) cur.pop_back(); continue; }
            int v = nx[u][c]; cur.push_back((char)('a' + c)); ++c; if (end[v]) out.push_back(cur); st.push_back({v, 0}); }
        return out; }

    bool erase(const std::string& w) {
        if (!search(w)) return false;                                                                            // 단어가 아니면 접두사만 있어도 아무것도 바꾸지 않는다
        std::vector<int> path = {0}; for (char c : w) path.push_back(nx[path.back()][c - 'a']);
        for (int u : path) --pass[u]; end[path.back()] = 0; --words;
        for (size_t k = path.size(); k-- > 1;) { int u = path[k]; if (pass[u] > 0) break; nx[path[k - 1]][w[k - 1] - 'a'] = -1; freeList.push_back(u); --live; }   // pass == 0 인 접미 구간만 잘라낸다
        return true; }
};
size_t distinctPrefixes(const std::set<std::string>& s) { std::set<std::string> p; for (auto& w : s) for (size_t k = 0; k <= w.size(); ++k) p.insert(w.substr(0, k)); return std::max<size_t>(1, p.size()); }

int main() {
    std::vector<std::string> universe = {""}; for (int len = 1; len <= 3; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; universe.push_back(s); }
    std::vector<std::string> queries = {""}; for (int len = 1; len <= 4; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; queries.push_back(s); }
    for (int mask = 0; mask < (1 << 15); ++mask) {
        std::set<std::string> base; for (int i = 0; i < 15; ++i) if (mask >> i & 1) base.insert(universe[i]);
        for (auto& q : queries) { Trie t; for (auto& w : base) t.insert(w); std::set<std::string> ref = base; bool a = t.erase(q); bool r = ref.erase(q) > 0; assert(a == r);
            assert(t.words == ref.size() && t.live == distinctPrefixes(ref) && t.list() == std::vector<std::string>(ref.begin(), ref.end()));                   // 정확한 가지치기
            assert(!t.erase(q)); for (auto& w : ref) assert(t.search(w)); }
    }
    std::mt19937 rng(31); Trie t; std::set<std::string> ref; size_t maxLive = 0; long inserts = 0, erases = 0, hits = 0;
    auto word = [&]() { std::string w; int len = (int)(rng() % 9); for (int j = 0; j < len; ++j) w += (char)('a' + rng() % 3); return w; };            // 알파벳 3 → 접두사 공유가 많다
    for (long step = 0; step < 1000000; ++step) {
        std::string w = word(); int op = (int)(rng() % 3);
        if (op == 0) { bool a = t.insert(w); bool r = ref.insert(w).second; assert(a == r); ++inserts; }
        else if (op == 1) { bool a = t.erase(w); bool r = ref.erase(w) > 0; assert(a == r); erases += a; }
        else { bool a = t.search(w); assert(a == (ref.count(w) > 0)); hits += a; }
        maxLive = std::max(maxLive, t.live);
        if (step % 5003 == 0) { assert(t.words == ref.size() && t.live == distinctPrefixes(ref)); }
    }
    assert(t.words == ref.size() && t.live == distinctPrefixes(ref) && t.list() == std::vector<std::string>(ref.begin(), ref.end()) && t.nx.size() <= maxLive && erases > 1000);
    for (auto& w : std::vector<std::string>(ref.begin(), ref.end())) { bool a = t.erase(w); assert(a); } assert(t.live == 1 && t.words == 0 && t.list().empty());                          // 전부 지우면 루트만
    { Trie big; std::string longWord(200000, 'a'); big.insert(longWord); assert(big.live == 200001); bool a = big.erase(longWord); assert(a && big.live == 1 && !big.startsWith("a")); }
    std::cout << "TrieDelete: exact pruning (node count == number of distinct prefixes) held for every subset of 15 short strings x 31 deletions; 10^6 random insert/erase/search operations matched std::set (" << erases << " successful erases) and the arena reused freed nodes; a 200000-letter word was removed down to the root" << std::endl;
    return 0;
}
// Time Complexity: O(L)
// Space Complexity: O(L) (경로 저장)
```
## RadixTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <vector>

// (정수 키·고정 폭 조각의 기수 트리는 AdvancedDataStructures.md Part 14.)
// 기수 트리(압축 트라이, radix tree): 자식이 하나뿐인 경로를 하나의 간선(문자열 레이블)으로 합친 트라이.  노드 수가 단어 수에 비례(≤ 2n)하고, 단어를 넣을 때 간선 레이블이 중간에서 갈라지면 그 자리에서 둘로 쪼갠다.
//  삭제는 단어 표시를 지운 뒤 자식이 없으면 노드를 떼고, 자식이 하나뿐이고 단어 끝이 아니면 부모 간선과 *합친다* — 그래서 모양은 단어 집합만으로 정해지는 *정준형*이다.  리눅스 커널의 페이지 캐시·IP 라우팅(최장 접두사 일치)·Redis 의 rax 가 쓴다.
//  ① 고전 예 romane romanus romulus rubens ruber rubicon rubicundus 의 트리를 그림으로 고정(노드 14 개, 보통 트라이는 뿌리 포함 28 개)  ② 무작위 삽입·삭제·조회·접두사 질의 30 만 번(알파벳 abc, 길이 0~8)을 std::set 과 대조, 매 1000 번마다 구조 불변식(뿌리를 뺀 모든 노드는 단어 끝이거나 자식 ≥ 2, 레이블 비지 않음, 노드 수 ≤ 2·단어 수 + 1)
//  ③ 정준형: 같은 단어 집합이면 *삽입·삭제 이력이 달라도* 직렬화가 같다(이력 6 가지 vs 정렬해서 새로 지은 트리)  ④ 최장 접두사 일치(LPM)가 "모든 접두사를 집합에 물어 가장 긴 것" 과 같음
struct Node { std::map<char, std::pair<std::string, Node*>> kids; bool end = false; ~Node() { for (auto& kv : kids) delete kv.second.second; } };

class RadixTree {
public:
    size_t nodes() const { return countNodes(&root); }
    size_t words() const { return wordCount; }
    bool insert(const std::string& w) {
        Node* n = &root; size_t i = 0;
        while (i < w.size()) {
            auto it = n->kids.find(w[i]);
            if (it == n->kids.end()) { Node* leaf = new Node; leaf->end = true; n->kids[w[i]] = {w.substr(i), leaf}; ++wordCount; return true; }
            std::string& label = it->second.first; Node* child = it->second.second;
            size_t l = 0; while (l < label.size() && i + l < w.size() && label[l] == w[i + l]) ++l;
            if (l == label.size()) { n = child; i += l; continue; }                                            // 레이블 전체 일치: 아래로
            Node* mid = new Node; mid->kids[label[l]] = {label.substr(l), child};                               // 레이블 중간에서 갈라짐: 중간 노드를 만들어 분할
            it->second = {label.substr(0, l), mid}; n = mid; i += l;
        }
        if (n->end) return false; n->end = true; ++wordCount; return true;
    }
    bool contains(const std::string& w) const { const Node* n = locate(w); return n && n->end; }
    bool erase(const std::string& w) {
        std::vector<Node*> path = {&root}; std::vector<char> via; Node* n = &root; size_t i = 0;
        while (i < w.size()) { auto it = n->kids.find(w[i]); if (it == n->kids.end()) return false; const std::string& label = it->second.first;
            if (w.compare(i, label.size(), label) != 0) return false; i += label.size(); via.push_back(w[i - label.size()]); n = it->second.second; path.push_back(n); }
        if (!n->end) return false; n->end = false; --wordCount;
        for (size_t d = path.size() - 1; d >= 1; --d) {                                                      // 아래에서 위로 정리
            Node* cur = path[d]; Node* parent = path[d - 1]; char key = via[d - 1];
            if (cur->end) break;
            if (cur->kids.empty()) { parent->kids.erase(key); delete cur; continue; }                         // 잎이 비면 떼어 낸다
            if (cur->kids.size() == 1) { auto kid = cur->kids.begin()->second; parent->kids[key].first += kid.first; parent->kids[key].second = kid.second; cur->kids.clear(); delete cur; }   // 자식 하나뿐: 간선을 합친다
            break; }
        return true;
    }
    std::vector<std::string> withPrefix(const std::string& p) const {
        const Node* n = &root; std::string cur; size_t i = 0;
        while (i < p.size()) { auto it = n->kids.find(p[i]); if (it == n->kids.end()) return {};
            const std::string& label = it->second.first; size_t m = std::min(label.size(), p.size() - i); if (label.compare(0, m, p, i, m) != 0) return {};
            cur += label; i += m; n = it->second.second; }                                                    // 접두사가 레이블 중간에서 끝나도 그 아래 전체가 후보
        std::vector<std::string> out; collect(n, cur, out); return out; }
    std::string longestPrefixOf(const std::string& q) const {                                                  // q 의 접두사인 저장 단어 중 가장 긴 것
        const Node* n = &root; size_t i = 0; std::string best = n->end ? "" : "\x01";
        while (i < q.size()) { auto it = n->kids.find(q[i]); if (it == n->kids.end()) break; const std::string& label = it->second.first;
            if (q.compare(i, label.size(), label) != 0) break; i += label.size(); n = it->second.second; if (n->end) best = q.substr(0, i); }
        return best; }
    bool wellFormed() const { return check(&root, true); }
    std::string draw() const { std::string out = "(root)\n"; drawKids(&root, "", out); return out; }
    std::string signature() const { std::string s; sig(&root, s); return s; }
private:
    Node root; size_t wordCount = 0;
    const Node* locate(const std::string& w) const { const Node* n = &root; size_t i = 0; while (i < w.size()) { auto it = n->kids.find(w[i]); if (it == n->kids.end()) return nullptr; const std::string& label = it->second.first; if (w.compare(i, label.size(), label) != 0) return nullptr; i += label.size(); n = it->second.second; } return n; }
    static size_t countNodes(const Node* n) { size_t c = 1; for (auto& kv : n->kids) c += countNodes(kv.second.second); return c; }
    static void collect(const Node* n, const std::string& cur, std::vector<std::string>& out) { if (n->end) out.push_back(cur); for (auto& kv : n->kids) collect(kv.second.second, cur + kv.second.first, out); }
    static bool check(const Node* n, bool isRoot) { if (!isRoot && !n->end && n->kids.size() < 2) return false;
        for (auto& kv : n->kids) { if (kv.second.first.empty() || kv.second.first[0] != kv.first || !check(kv.second.second, false)) return false; } return true; }
    static void sig(const Node* n, std::string& s) { s += n->end ? "*(" : "("; for (auto& kv : n->kids) { s += kv.second.first + ":"; sig(kv.second.second, s); } s += ")"; }
    static void drawKids(const Node* n, const std::string& prefix, std::string& out) {
        size_t k = 0; for (auto& kv : n->kids) { bool last = ++k == n->kids.size(); out += prefix + (last ? "└─ " : "├─ ") + kv.second.first + (kv.second.second->end ? "*" : "") + "\n"; drawKids(kv.second.second, prefix + (last ? "   " : "│  "), out); } }
};
std::string randomWord(std::mt19937& rng) { int len = (int)(rng() % 9); std::string w; for (int i = 0; i < len; ++i) w += (char)('a' + rng() % 3); return w; }

int main() {
    {   RadixTree t; std::vector<std::string> words = {"romane", "romanus", "romulus", "rubens", "ruber", "rubicon", "rubicundus"}; for (auto& w : words) assert(t.insert(w));      // ① 고전 예
        assert(t.draw() == "(root)\n└─ r\n   ├─ om\n   │  ├─ an\n   │  │  ├─ e*\n   │  │  └─ us*\n   │  └─ ulus*\n   └─ ub\n      ├─ e\n      │  ├─ ns*\n      │  └─ r*\n      └─ ic\n         ├─ on*\n         └─ undus*\n");
        size_t plain = 1; { std::set<std::string> prefixes; for (auto& w : words) for (size_t k = 1; k <= w.size(); ++k) prefixes.insert(w.substr(0, k)); plain += prefixes.size(); }
        assert(t.nodes() == 14 && plain == 28 && t.wellFormed());                                              // 보통 트라이는 (뿌리 포함) 28 개
        assert(!t.contains("rom") && !t.contains("roman") && !t.contains("rubicons") && t.contains("ruber"));
        assert((t.withPrefix("rub") == std::vector<std::string>{"rubens", "ruber", "rubicon", "rubicundus"}) && (t.withPrefix("roman") == std::vector<std::string>{"romane", "romanus"}) && t.withPrefix("x").empty());
        assert(t.erase("romane") && t.nodes() == 12 && t.draw().find("├─ anus*") != std::string::npos);        // an 아래 e 가 사라지면 an+us 가 합쳐져 anus
        assert(!t.erase("romane") && !t.erase("rom") && t.wellFormed()); }
    std::mt19937 rng(21); RadixTree t; std::set<std::string> model;                                          // ② 무작위 대조
    for (int step = 0; step < 300000; ++step) { std::string w = randomWord(rng); int op = (int)(rng() % 10);
        if (op < 4) { bool added = t.insert(w); assert(added == model.insert(w).second); }
        else if (op < 7) { bool removed = t.erase(w); assert(removed == (model.erase(w) == 1)); }
        else if (op < 9) assert(t.contains(w) == (model.count(w) == 1));
        else { std::vector<std::string> got = t.withPrefix(w), want; for (auto it = model.lower_bound(w); it != model.end() && it->compare(0, w.size(), w) == 0; ++it) want.push_back(*it); assert(got == want); }
        assert(t.words() == model.size());
        if (step % 1000 == 0) { assert(t.wellFormed() && t.nodes() <= 2 * model.size() + 1); } }
    {   std::vector<std::string> final(model.begin(), model.end()); std::string canonical; { RadixTree fresh; for (auto& w : final) fresh.insert(w); canonical = fresh.signature(); assert(canonical == t.signature()); }      // ③ 정준형
        for (int trial = 0; trial < 6; ++trial) { std::shuffle(final.begin(), final.end(), rng); RadixTree other; for (auto& w : final) other.insert(w); std::vector<std::string> extra; for (int i = 0; i < 200; ++i) extra.push_back(randomWord(rng) + "d");
            for (auto& w : extra) other.insert(w); for (auto& w : extra) other.erase(w); assert(other.signature() == canonical && other.nodes() == t.nodes()); } }
    for (int q = 0; q < 3000; ++q) { std::string w = randomWord(rng) + randomWord(rng); std::string best = "\x01"; for (size_t k = 0; k <= w.size(); ++k) if (model.count(w.substr(0, k))) best = w.substr(0, k); assert(t.longestPrefixOf(w) == best); }      // ④ 최장 접두사 일치
    std::cout << "RadixTree: the classic 7-word example needs 14 nodes where a plain trie needs 28; 300000 random insert/erase/contains/prefix operations matched std::set, structure stayed canonical (history-independent) and longest-prefix match agreed with a brute-force check; " << model.size() << " words ended in " << t.nodes() << " nodes" << std::endl;
    return 0;
}
// Time Complexity: 삽입·검색·삭제 O(L · σ) (σ = 한 노드의 자식 수 탐색, std::map 이면 L log σ)
// Space Complexity: O(단어 수) 노드 + 레이블 (노드 ≤ 2n + 1)
```

## GeneralTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 일반 트리: 자식 수에 제한이 없다.  표준 표현은 "왼쪽 자식-오른쪽 형제(LCRS)": 모든 노드가 (첫 자식 fc, 다음 형제 ns) 포인터 두 개만 가지므로 일반 트리가 곧 이진 트리가 된다.
//  성질: 일반 트리의 전위 순회 = LCRS 의 전위 순회,  일반 트리의 후위 순회 = LCRS 의 중위 순회.  노드는 arena 에 두고 마지막 자식 포인터(lc)로 자식 추가를 O(1) 에 한다.
//  ① 예제(A: B C D, B: E F, D: G)  ② 전수: 노드 n ≤ 8 개인 *모든* 순서 있는 트리(괄호열 = Dyck 단어, 카탈란 C(n−1) 개)가 서로 다른 LCRS 이진 트리가 되고 (LCRS 루트는 오른쪽 자식이 없다), 순회·높이·차수가 *재귀 오라클*과 같으며 LCRS 에서 부모 배열과 괄호열이 그대로 복원
//  ③ 무작위 트리 300 개와 100 만 노드 사슬·별·무작위 재귀 트리를 *반복* 순회로 대조 (재귀 없이 — 깊이 10^6 에서도 안전).
struct GT {
    std::vector<int> fc, ns, lc, par;
    int node() { fc.push_back(-1); ns.push_back(-1); lc.push_back(-1); par.push_back(-1); return (int)fc.size() - 1; }
    int addChild(int p) { int c = node(); par[c] = p; if (fc[p] < 0) fc[p] = c; else ns[lc[p]] = c; lc[p] = c; return c; }
    std::vector<int> preorder(int root) const {                                                                  // LCRS 전위: 방문 → 첫 자식 → 다음 형제 (스택에는 형제를 먼저 넣는다)
        std::vector<int> out, st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); out.push_back(u); if (u != root && ns[u] >= 0) { } if (ns[u] >= 0 && u != root) st.push_back(ns[u]); if (fc[u] >= 0) st.push_back(fc[u]); } return out; }
    std::vector<int> binaryInorder(int root) const {                                                             // LCRS 중위: 왼쪽(fc) → 방문 → 오른쪽(ns)
        std::vector<int> out, st; int u = root; while (u >= 0 || !st.empty()) { while (u >= 0) { st.push_back(u); u = fc[u]; } u = st.back(); st.pop_back(); out.push_back(u); u = (u == root) ? -1 : ns[u]; } return out; }
    std::vector<int> depthAll(int root) const {                                                                  // 전위 한 번으로 깊이: 첫 자식 +1, 형제는 같은 깊이
        std::vector<int> d(fc.size(), 0), st = {root}; while (!st.empty()) { int u = st.back(); st.pop_back(); if (ns[u] >= 0 && u != root) { d[ns[u]] = d[u]; st.push_back(ns[u]); } if (fc[u] >= 0) { d[fc[u]] = d[u] + 1; st.push_back(fc[u]); } } return d; }
    std::string dyck(int root) const {                                                                           // 괄호열: 자식 하나마다 "(" 자식 부분 트리 ")"
        std::string s; std::vector<std::pair<int, int>> st = {{root, fc[root]}}; while (!st.empty()) { auto& top = st.back(); if (top.second < 0) { st.pop_back(); if (!st.empty()) s += ')'; continue; } int c = top.second; top.second = ns[c]; s += '('; st.push_back({c, fc[c]}); } return s; }
};
// 오라클: 자식 목록과 재귀
struct Ref { std::vector<std::vector<int>> ch; explicit Ref(const GT& t) : ch(t.fc.size()) { for (size_t v = 1; v < t.par.size(); ++v) if (t.par[v] >= 0) ch[t.par[v]].push_back((int)v); }
    void pre(int u, std::vector<int>& o) const { o.push_back(u); for (int c : ch[u]) pre(c, o); }
    void post(int u, std::vector<int>& o) const { for (int c : ch[u]) post(c, o); o.push_back(u); }
    int height(int u) const { int h = 0; for (int c : ch[u]) h = std::max(h, 1 + height(c)); return h; } };
GT fromDyck(const std::string& s) { GT t; int cur = t.node(); std::vector<int> st = {cur}; for (char c : s) { if (c == '(') { cur = t.addChild(st.back()); st.push_back(cur); } else st.pop_back(); } return t; }
void genDyck(int open, int close, int m, std::string& cur, std::vector<std::string>& out) { if ((int)cur.size() == 2 * m) { out.push_back(cur); return; } if (open < m) { cur += '('; genDyck(open + 1, close, m, cur, out); cur.pop_back(); } if (close < open) { cur += ')'; genDyck(open, close + 1, m, cur, out); cur.pop_back(); } }

int main() {
    { GT t; int a = t.node(), b = t.addChild(a), c = t.addChild(a), d = t.addChild(a), e = t.addChild(b), f = t.addChild(b), g = t.addChild(d); (void)c; (void)e; (void)f; (void)g;     // 예제: 레이블 A..G = 0..6
      std::string pre, post, in; for (int u : t.preorder(0)) pre += (char)('A' + u); Ref r(t); std::vector<int> v; r.post(0, v); for (int u : v) post += (char)('A' + u); for (int u : t.binaryInorder(0)) in += (char)('A' + u);
      assert(pre == "ABEFCDG" && post == "EFBCGDA" && in == post && r.height(0) == 2); }                         // 간선 기준 높이 2 (노드 기준 3)
    const long catalan[] = {1, 1, 2, 5, 14, 42, 132, 429};
    for (int m = 0; m <= 7; ++m) {                                                                               // ② 모든 순서 있는 트리 (노드 m + 1 개)
        std::vector<std::string> words; std::string cur; genDyck(0, 0, m, cur, words); assert((long)words.size() == catalan[m]); std::set<std::pair<std::vector<int>, std::vector<int>>> shapes;
        for (auto& w : words) { GT t = fromDyck(w); Ref r(t); std::vector<int> pre, post; r.pre(0, pre); r.post(0, post);
            assert(t.preorder(0) == pre && t.binaryInorder(0) == post && t.dyck(0) == w);                          // 전위=전위, LCRS 중위=후위, LCRS 에서 괄호열 복원
            assert(t.ns[0] < 0); shapes.insert({t.fc, t.ns});                                                    // LCRS 루트는 오른쪽 자식이 없다
            std::vector<int> d = t.depthAll(0); int h = 0; for (int x : d) h = std::max(h, x); assert(h == r.height(0));
            for (int u = 1; u <= m; ++u) assert(d[u] == d[t.par[u]] + 1); }
        assert((long)shapes.size() == catalan[m]); }                                                             // 서로 다른 이진 트리 (일대일 대응)
    std::mt19937 rng(7);
    for (int it = 0; it < 300; ++it) { GT t; t.node(); int n = 1 + (int)(rng() % 400); for (int i = 1; i < n; ++i) t.addChild((int)(rng() % i)); Ref r(t); std::vector<int> pre, post; r.pre(0, pre); r.post(0, post);
        assert(t.preorder(0) == pre && t.binaryInorder(0) == post && (int)t.depthAll(0)[n - 1] >= 0); std::vector<int> d = t.depthAll(0); int h = 0; for (int x : d) h = std::max(h, x); assert(h == r.height(0)); }
    for (int shape = 0; shape < 3; ++shape) {                                                                    // ③ 100 만 노드: 사슬 / 별 / 무작위 재귀 트리
        GT t; t.node(); const int n = 1000000; for (int i = 1; i < n; ++i) t.addChild(shape == 0 ? i - 1 : shape == 1 ? 0 : (int)(rng() % i));
        std::vector<int> pre = t.preorder(0), in = t.binaryInorder(0); assert((int)pre.size() == n && (int)in.size() == n);
        std::vector<int> pos(n); for (int i = 0; i < n; ++i) pos[pre[i]] = i; for (int v = 1; v < n; ++v) assert(pos[t.par[v]] < pos[v]);               // 전위: 부모가 자식보다 먼저
        std::vector<int> pos2(n); for (int i = 0; i < n; ++i) pos2[in[i]] = i; for (int v = 1; v < n; ++v) assert(pos2[t.par[v]] > pos2[v]);             // 후위: 부모가 자식보다 나중
        std::vector<int> d = t.depthAll(0); int h = *std::max_element(d.begin(), d.end()); if (shape == 0) assert(h == n - 1 && pre[n - 1] == n - 1 && in[0] == n - 1); if (shape == 1) assert(h == 1 && t.ns[1] == 2);
        std::vector<int> want(n, 0); for (int v = 1; v < n; ++v) want[v] = want[t.par[v]] + 1; assert(want == d);
    }
    std::cout << "GeneralTree: all ordered trees with up to 8 nodes (Catalan many) mapped one-to-one onto LCRS binary trees with preorder=preorder and postorder=binary inorder, random trees matched a recursive oracle, and 10^6-node chain/star/random trees were traversed iteratively" << std::endl;
    return 0;
}
// Time Complexity: 자식 추가 O(1) (마지막 자식 포인터), 순회 O(N)
// Space Complexity: O(N)
```
## NaryTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// N-ary 트리: 모든 노드의 자식이 최대 N 개.  완전 N-ary 트리는 배열에 담을 수 있다 (N = 2 가 이진 힙).  부모(i) = (i−1)/N,  자식 k(0-based) 의 인덱스 = N·i + k + 1.
//  n 개 노드의 높이(간선 기준) = 가장 깊은 노드(= 마지막 인덱스 n−1)까지의 부모 사슬 길이 = ⌈log_N(n·(N−1) + 1)⌉ − 1.  N 이 클수록 얕아진다 (B-트리·캐시 친화적 힙의 동기).
//  ① 명시적 트리(레벨 순서로 첫 빈 자리에 붙임)와 인덱스 공식이 N = 1..8 에서 일치  ② 높이 공식 — 정수 루프(height)가 부모 사슬을 직접 센 값과 같다 (N = 2..16, n ≤ 6000) — 100 만 노드: 이진 19, 8진 7
//  ③ N-ary 힙: 여러 N 으로 같은 데이터를 std::sort 와 대조하고, 내림차순 삽입(최악)의 교환 수가 정확히 Σ(노드 깊이)임을 확인; N 이 커지면 삽입은 싸지고(교환 감소) 삭제의 *비교*는 N = 3 근처에서 최소(이진보다 3-진이 적다).
int height(long n, int N) { int h = 0; long levelEnd = 1, width = 1; while (levelEnd < n) { width *= N; levelEnd += width; h++; } return h; }   // 정수 루프
int hopsToRoot(long i, int N) { int h = 0; while (i > 0) { i = (i - 1) / N; ++h; } return h; }                       // 부모 사슬
struct DHeap {
    int d; std::vector<int> a; long cmps = 0, swaps = 0;
    explicit DHeap(int dd) : d(dd) {}
    void push(int v) { a.push_back(v); size_t i = a.size() - 1; while (i > 0) { ++cmps; size_t p = (i - 1) / d; if (a[p] <= a[i]) break; std::swap(a[p], a[i]); i = p; ++swaps; } }
    int pop() { int top = a[0]; a[0] = a.back(); a.pop_back(); size_t i = 0, n = a.size();
        for (;;) { size_t f = d * i + 1; if (f >= n) break; size_t best = f; for (size_t c = f + 1; c < std::min(n, f + d); ++c) { ++cmps; if (a[c] < a[best]) best = c; } ++cmps; if (a[best] >= a[i]) break; std::swap(a[i], a[best]); i = best; ++swaps; }
        return top; }
    bool valid() const { for (size_t i = 1; i < a.size(); ++i) if (a[(i - 1) / d] > a[i]) return false; return true; }
};

int main() {
    for (int N = 1; N <= 8; ++N)                                                                                 // ① 명시적 트리 vs 인덱스 공식
        for (int n : {1, 2, 3, 10, 100, 777, 2000}) {
            std::vector<int> par(n, -1), kids(n, 0), depth(n, 0); std::queue<int> open; open.push(0);
            for (int v = 1; v < n; ++v) { int u = open.front(); par[v] = u; depth[v] = depth[u] + 1; if (++kids[u] == N) open.pop(); open.push(v); }
            for (int i = 1; i < n; ++i) { assert(par[i] == (i - 1) / N); long k = (i - 1) % N; assert((long)N * par[i] + k + 1 == i); }
            assert(*std::max_element(depth.begin(), depth.end()) == depth[n - 1] && depth[n - 1] == hopsToRoot(n - 1, N));
        }
    for (int N = 2; N <= 16; ++N) for (int n = 1; n <= 6000; ++n) assert(height(n, N) == hopsToRoot(n - 1, N));    // ② 정수 루프 = 부모 사슬
    assert(height(1000000, 2) == 19 && height(1000000, 8) == 7 && height(1000000, 16) == 5);
    long fullLevels = 1; for (int N : {2, 3, 4, 10}) { fullLevels = 1; long width = 1; for (int lv = 0; lv < 6; ++lv) { assert(height(fullLevels, N) == lv && height(fullLevels + 1, N) == lv + 1); width *= N; fullLevels += width; } }   // 수준이 꽉 찬 경계
    std::mt19937 rng(37); const int n = 100000; std::vector<int> vals(n); for (auto& x : vals) x = (int)(rng() % 1000000); std::vector<int> sorted = vals; std::sort(sorted.begin(), sorted.end());
    long popCmps[17] = {0}, pushSwaps[17] = {0}; int bestD = 2;
    for (int d = 2; d <= 16; ++d) {                                                                              // ③ N-ary 힙
        DHeap h(d); for (int x : vals) h.push(x); assert(h.valid()); pushSwaps[d] = h.swaps; h.cmps = 0; std::vector<int> out; while (!h.a.empty()) { out.push_back(h.pop()); } assert(out == sorted); popCmps[d] = h.cmps;
        DHeap worst(d); for (int i = n; i >= 1; --i) worst.push(i); long depthSum = 0; for (int i = 0; i < n; ++i) depthSum += hopsToRoot(i, d); assert(worst.swaps == depthSum && worst.valid());          // 최악 삽입 = 깊이 합
        if (popCmps[d] < popCmps[bestD]) bestD = d;
        if (d > 2) assert(pushSwaps[d] < pushSwaps[d - 1]);                                                      // 삽입 교환은 N 이 클수록 줄어든다
    }
    assert(bestD == 3 && popCmps[3] < popCmps[2] && popCmps[16] > popCmps[3]);                                   // 삭제 비교는 N = 3 에서 최소
    std::cout << "NaryTree: index formulas matched explicit trees for N=1..8, the integer height loop matched parent-chain hops for N=2..16, and d-ary heaps for d=2..16 sorted 10^5 keys correctly (pop comparisons minimal at d=" << bestD << ": " << popCmps[2] << " (d=2) vs " << popCmps[3] << " (d=3))" << std::endl;
    return 0;
}
// Time Complexity: 인덱스 계산 O(1), N-ary 힙 삽입 O(log_N n), 삭제 O(N log_N n)
// Space Complexity: O(N) 배열
```
# Part 10. 문자열 자료구조
## SuffixTrie()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 접미사 트라이: 문자열의 *모든 접미사*를 압축하지 않은 트라이에 넣은 것.  부분 문자열 검색이 O(m) 이고, 노드마다 "지나간 접미사 수"를 두면 패턴의 출현 횟수도 O(m) 에 나온다.
//  대가는 공간: 노드 수 = 1 + (서로 다른 부분 문자열 수) 로 최악 Θ(n²) — 모든 글자가 다르면 정확히 1 + n(n+1)/2, 같은 글자뿐이면 n + 1.  (압축해서 O(n) 으로 만든 것이 접미사 트리/자동자)
//  ① 전수: 이진 문자열 길이 ≤ 10 전부에서 노드 수 = 1 + 서로 다른 부분 문자열 수(집합 오라클), 모든 패턴(길이 ≤ 5)의 contains / 출현 횟수가 순진한 탐색과 같다  ② 무작위 문자열(알파벳 4, 길이 ≤ 60)  ③ 최악·최선 공간.
struct SuffixNode {
    std::vector<SuffixNode*> children; int through = 0;                                                         // through = 이 노드를 지난 접미사 수 = 경로 문자열의 출현 횟수
    SuffixNode() : children(26, nullptr) {}
    ~SuffixNode() { for (SuffixNode* c : children) delete c; }
};
class SuffixTrie {
    SuffixNode* root; size_t nodes = 1;
public:
    explicit SuffixTrie(const std::string& text) : root(new SuffixNode()) { for (size_t i = 0; i < text.size(); ++i) insertSuffix(text, i); }
    ~SuffixTrie() { delete root; }
    SuffixTrie(const SuffixTrie&) = delete; SuffixTrie& operator=(const SuffixTrie&) = delete;
    void insertSuffix(const std::string& t, size_t from) { SuffixNode* cur = root; for (size_t i = from; i < t.size(); ++i) { SuffixNode*& nx = cur->children[t[i] - 'a']; if (!nx) { nx = new SuffixNode(); ++nodes; } cur = nx; ++cur->through; } }
    const SuffixNode* walk(const std::string& p) const { const SuffixNode* cur = root; for (char c : p) { cur = cur->children[c - 'a']; if (!cur) return nullptr; } return cur; }
    bool contains(const std::string& p) const { return walk(p) != nullptr; }
    int occurrences(const std::string& p) const { const SuffixNode* n = walk(p); return !n ? 0 : (n == root ? -1 : n->through); }
    size_t nodeCount() const { return nodes; }
};
size_t distinctSubstrings(const std::string& s) { std::set<std::string> sub; for (size_t i = 0; i < s.size(); ++i) for (size_t l = 1; i + l <= s.size(); ++l) sub.insert(s.substr(i, l)); return sub.size(); }
int naiveCount(const std::string& t, const std::string& p) { int c = 0; for (size_t i = t.find(p); i != std::string::npos; i = t.find(p, i + 1)) ++c; return c; }

int main() {
    { SuffixTrie st("banana"); assert(st.contains("nan") && !st.contains("apple") && st.occurrences("ana") == 2 && st.occurrences("a") == 3 && st.occurrences("banana") == 1 && st.occurrences("nab") == 0); }
    std::vector<std::string> patterns; for (int len = 1; len <= 5; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; patterns.push_back(s); }
    for (int len = 1; len <= 10; ++len) for (int m = 0; m < (1 << len); ++m) { std::string t; for (int b = len - 1; b >= 0; --b) t += (m >> b & 1) ? 'b' : 'a'; SuffixTrie st(t); assert(st.nodeCount() == 1 + distinctSubstrings(t));
        for (auto& p : patterns) { int c = naiveCount(t, p); assert(st.contains(p) == (c > 0) && st.occurrences(p) == c); } }                         // ① 전수
    std::mt19937 rng(14);
    for (int it = 0; it < 300; ++it) { int n = 1 + (int)(rng() % 60); std::string t(n, 'a'); for (char& c : t) c = (char)('a' + rng() % 4); SuffixTrie st(t); assert(st.nodeCount() == 1 + distinctSubstrings(t));
        for (int q = 0; q < 30; ++q) { int pl = 1 + (int)(rng() % 6); std::string p; if (rng() % 2 && n >= pl) p = t.substr(rng() % (n - pl + 1), pl); else for (int i = 0; i < pl; ++i) p += (char)('a' + rng() % 4); int c = naiveCount(t, p); assert(st.contains(p) == (c > 0) && st.occurrences(p) == c); } }
    { std::string distinct; for (char c = 'a'; c <= 'z'; ++c) distinct += c; SuffixTrie st(distinct); assert(st.nodeCount() == 1 + 26 * 27 / 2);                                  // ③ 최악: 모든 글자가 다르면 Θ(n²)
      SuffixTrie same(std::string(500, 'a')); assert(same.nodeCount() == 501); }                                                                                              // 최선: n + 1
    std::cout << "SuffixTrie: node count equalled 1 + (number of distinct substrings) for every binary string up to length 10 and 300 random strings, contains/occurrence counts matched naive search for all patterns, and the quadratic worst case (26 distinct letters -> 352 nodes) was reproduced" << std::endl;
    return 0;
}
// Time Complexity: 구성 O(N²), 검색 O(M)
// Space Complexity: O(N²) 노드 (서로 다른 부분 문자열 수에 비례)
```

## SuffixTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <vector>

// 접미사 트리: 문자열의 모든 접미사를 압축 트라이로 모은 것.  부분 문자열 검색이 O(m), 서로 다른 부분 문자열 수·최장 반복 부분 문자열·최장 공통 부분 문자열 같은 문제를 선형 시간에 푼다.
//  끝 표식 '$' 를 붙여 어떤 접미사도 다른 접미사의 접두사가 되지 않게 한다 (모든 접미사가 잎).  여기서는 접미사를 하나씩 넣는 O(n²) 구성 (선형 시간 알고리즘은 Ukkonen).
//  ① 전수: 이진 문자열 길이 ≤ 10 전부 — 잎 수 = n + 1, 내부 노드(루트 제외)는 모두 자식 ≥ 2 개이고 ≤ n 개, 간선 글자 총수 − (n + 1) = 서로 다른 부분 문자열 수, find(p) = 순진한 모든 출현 위치  ② 가장 긴 반복 부분 문자열 = 가장 깊은 내부 노드의 문자열 깊이 (완전 탐색과 대조)
//  ③ 무작위 문자열(알파벳 3, 길이 ≤ 80)  ④ 소멸자가 트리를 해제한다 (누수 없음).
struct Node { std::map<char, std::pair<std::string, Node*>> kids; int leafIndex = -1; ~Node() { for (auto& kv : kids) delete kv.second.second; } };

void insertSuffix(Node* root, const std::string& s, int start) {
    Node* n = root; size_t i = start;
    for (;;) {
        auto it = n->kids.find(s[i]);
        if (it == n->kids.end()) { Node* leaf = new Node; leaf->leafIndex = start; n->kids[s[i]] = {s.substr(i), leaf}; return; }
        std::string& label = it->second.first; Node* child = it->second.second;
        size_t l = 0; while (l < label.size() && s[i + l] == label[l]) l++;
        if (l == label.size()) { n = child; i += l; continue; }
        Node* mid = new Node;                                                                                    // 분할
        mid->kids[label[l]] = {label.substr(l), child};
        it->second = {label.substr(0, l), mid};
        n = mid; i += l;
    }
}
void leaves(const Node* n, std::set<int>& out) { if (n->leafIndex >= 0) out.insert(n->leafIndex); for (auto& kv : n->kids) leaves(kv.second.second, out); }
std::set<int> find(const Node* root, const std::string& p) {                                                      // 패턴의 모든 출현 위치 = 패턴 끝 아래의 잎들
    const Node* n = root; size_t i = 0;
    while (i < p.size()) {
        auto it = n->kids.find(p[i]); if (it == n->kids.end()) return {};
        const std::string& label = it->second.first; size_t m = std::min(label.size(), p.size() - i);
        if (label.compare(0, m, p, i, m) != 0) return {};
        i += m; n = it->second.second;
    }
    std::set<int> r; leaves(n, r); return r;
}
size_t edgeChars(const Node* n) { size_t s = 0; for (auto& kv : n->kids) s += kv.second.first.size() + edgeChars(kv.second.second); return s; }
void shape(const Node* n, bool isRoot, int& leafCount, int& inner, bool& branching, size_t depth, size_t& deepest) {          // 내부 노드의 문자열 깊이 최대값 = 가장 긴 반복 부분 문자열 길이
    if (n->leafIndex >= 0) { ++leafCount; return; }
    if (!isRoot) { ++inner; if (n->kids.size() < 2) branching = false; deepest = std::max(deepest, depth); }
    for (auto& kv : n->kids) shape(kv.second.second, false, leafCount, inner, branching, depth + kv.second.first.size(), deepest); }
size_t bruteLongestRepeat(const std::string& t) { size_t best = 0; for (size_t l = 1; l < t.size(); ++l) { std::set<std::string> seen; bool rep = false; for (size_t i = 0; i + l <= t.size() && !rep; ++i) rep = !seen.insert(t.substr(i, l)).second; if (rep) best = l; } return best; }
void checkAll(const std::string& text, const std::vector<std::string>& patterns) {
    std::string s = text + "$"; Node root; for (size_t i = 0; i < s.size(); i++) insertSuffix(&root, s, (int)i);
    int leafCount = 0, inner = 0; bool branching = true; size_t deepest = 0; shape(&root, true, leafCount, inner, branching, 0, deepest);
    std::set<std::string> sub; for (size_t i = 0; i < text.size(); i++) for (size_t l = 1; i + l <= text.size(); l++) sub.insert(text.substr(i, l));
    assert(leafCount == (int)s.size() && branching && inner <= (int)text.size() && edgeChars(&root) - s.size() == sub.size() && deepest == bruteLongestRepeat(text));
    for (auto& p : patterns) { std::set<int> want; for (size_t i = text.find(p); i != std::string::npos; i = text.find(p, i + 1)) want.insert((int)i); assert(find(&root, p) == want); } }

int main() {
    { std::string text = "banana", s = text + "$"; Node root; for (size_t i = 0; i < s.size(); i++) insertSuffix(&root, s, (int)i);
      assert((find(&root, "ana") == std::set<int>{1, 3}) && (find(&root, "na") == std::set<int>{2, 4}) && (find(&root, "banana") == std::set<int>{0}) && find(&root, "nab").empty() && edgeChars(&root) - s.size() == 15); }
    std::vector<std::string> patterns; for (int len = 1; len <= 5; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; patterns.push_back(s); }
    for (int len = 1; len <= 10; ++len) for (int m = 0; m < (1 << len); ++m) { std::string t; for (int b = len - 1; b >= 0; --b) t += (m >> b & 1) ? 'b' : 'a'; checkAll(t, patterns); }
    std::mt19937 rng(15);
    for (int it = 0; it < 150; ++it) { int n = 1 + (int)(rng() % 80); std::string t(n, 'a'); for (char& c : t) c = (char)('a' + rng() % 3); std::vector<std::string> ps; for (int q = 0; q < 20; ++q) { int pl = 1 + (int)(rng() % 6); std::string p; if (rng() % 2 && n >= pl) p = t.substr(rng() % (n - pl + 1), pl); else for (int i = 0; i < pl; ++i) p += (char)('a' + rng() % 3); ps.push_back(p); } checkAll(t, ps); }
    std::cout << "SuffixTree: for every binary string up to length 10 and 150 random strings, leaves = n+1, internal nodes all branch and number at most n, edge characters minus (n+1) equalled the distinct-substring count, the deepest internal node gave the longest repeated substring, and find() returned exactly the naive occurrence set" << std::endl;
    return 0;
}
// Time Complexity: 이 구성 O(n²), Ukkonen O(n); 검색 O(m + 출현 수)
// Space Complexity: O(n) 노드 (레이블은 부분 문자열 복사; 인덱스 쌍으로 두면 O(n))
```
## PatriciaTrie()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <set>
#include <cassert>

// 패트리샤 트라이(crit-bit 트리): 키를 비트열로 보고 "두 키가 처음 달라지는 비트(critical bit)" 만 내부 노드에 저장한다.
// 한 자식만 있는 노드가 없어서 n 개의 키에 정확히 n-1 개의 내부 노드가 있고, 비교는 비트 검사뿐이라 분기가 단순하다.  IP 라우팅의 최장 접두사 일치와 문자열 사전에 쓰인다
struct Node { bool leaf; uint32_t key; int bit; Node *l = nullptr, *r = nullptr; };
Node* newLeaf(uint32_t k) { return new Node{true, k, -1}; }
int topBit(uint32_t x) { return 31 - __builtin_clz(x); }
bool bitAt(uint32_t k, int b) { return k >> b & 1; }

Node* findLeaf(Node* n, uint32_t k) { while (!n->leaf) n = bitAt(k, n->bit) ? n->r : n->l; return n; }
Node* insert(Node* root, uint32_t k) {
    if (!root) return newLeaf(k);
    Node* best = findLeaf(root, k);
    if (best->key == k) return root;                                       // 이미 있다
    int crit = topBit(best->key ^ k);                                       // 처음 달라지는 비트
    Node** where = &root;                                                    // 비트 번호가 crit 보다 큰 내부 노드들을 지나 내려간다
    while (!(*where)->leaf && (*where)->bit > crit) where = bitAt(k, (*where)->bit) ? &(*where)->r : &(*where)->l;
    Node* leaf = newLeaf(k); Node* inner = new Node{false, 0, crit};
    if (bitAt(k, crit)) { inner->l = *where; inner->r = leaf; } else { inner->l = leaf; inner->r = *where; }
    *where = inner;
    return root;
}
bool contains(Node* root, uint32_t k) { return root && findLeaf(root, k)->key == k; }
int countLeaves(Node* n) { return !n ? 0 : n->leaf ? 1 : countLeaves(n->l) + countLeaves(n->r); }
int countInner(Node* n) { return (!n || n->leaf) ? 0 : 1 + countInner(n->l) + countInner(n->r); }
bool decreasing(Node* n) { if (n->leaf) return true; for (Node* c : {n->l, n->r}) if (!c->leaf && c->bit >= n->bit) return false; return decreasing(n->l) && decreasing(n->r); }

void destroy(Node* n) { if (!n) return; if (!n->leaf) { destroy(n->l); destroy(n->r); } delete n; }

int main() {
    std::mt19937 rng(18); Node* root = nullptr; std::set<uint32_t> truth;
    for (int i = 0; i < 2000; i++) { uint32_t k = rng() % 100000; root = insert(root, k); truth.insert(k); }
    for (uint32_t k = 0; k < 100000; k += 7) assert(contains(root, k) == (truth.count(k) > 0));
    assert(countLeaves(root) == (int)truth.size());
    assert(countInner(root) == (int)truth.size() - 1);                       // 내부 노드는 정확히 n-1 개
    assert(decreasing(root));                                                 // 내려갈수록 비교하는 비트가 낮아진다
    std::cout << "PatriciaTrie: " << truth.size() << " keys, " << countInner(root) << " internal nodes (n-1)" << std::endl;
    destroy(root);
    return 0;
}
// Time Complexity: 삽입·검색 O(키 길이 비트 수)
// Space Complexity: O(n)
```

## TernarySearchTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

// 삼진 탐색 트리(TST): 노드가 문자 하나와 세 개의 자식(작은 문자 lo / 같은 문자 eq 로 다음 글자 / 큰 문자 hi)을 갖는다.
// 트라이의 빠른 접두사 검색과 BST 의 작은 메모리를 합친 구조: 노드당 포인터 3개라 알파벳이 큰 트라이(문자당 배열)보다 훨씬 작고, 비교는 문자 단위.  자동 완성·철자 검사·와일드카드 검색에 쓴다.
//  ① 무작위 삽입·삭제·조회·접두사 질의 20 만 번(알파벳 abcde, 길이 1~6)을 std::set 과 대조, 주기적으로 구조 불변식(lo < c < hi, 단어 수 == 끝 표시 수, 노드 수 ≤ 삽입한 서로 다른 단어의 글자 수 합)
//  ② 와일드카드 질의 `a.c`(. 은 아무 글자 하나)를 *모든 단어에 대한 직접 비교* 와 대조  ③ 삽입 순서의 영향: 같은 단어를 사전순으로 넣으면 높이가 단어 수에 비례해 퇴화하고, 섞어서 넣으면 로그 수준 — 숫자로 확인  ④ 삭제는 끝 표시만 지우고 노드를 남겨 두는 단순한 방식(필요하면 가지치기)이라 `prune` 으로 빈 가지를 정리하면 노드 수가 단어 글자 수 합으로 줄어듦
struct Node { char c; Node *lo = nullptr, *eq = nullptr, *hi = nullptr; bool end = false; explicit Node(char ch) : c(ch) {} };

Node* insert(Node* n, const std::string& w, size_t i, size_t& created) {
    if (!n) { n = new Node(w[i]); ++created; }
    if (w[i] < n->c) n->lo = insert(n->lo, w, i, created);
    else if (w[i] > n->c) n->hi = insert(n->hi, w, i, created);
    else if (i + 1 < w.size()) n->eq = insert(n->eq, w, i + 1, created);
    else n->end = true;
    return n;
}
bool contains(const Node* n, const std::string& w) {
    size_t i = 0;
    while (n) {
        if (w[i] < n->c) n = n->lo; else if (w[i] > n->c) n = n->hi;
        else { if (i + 1 == w.size()) return n->end; n = n->eq; i++; }
    }
    return false;
}
bool erase(Node* n, const std::string& w) {                                                                // 끝 표시만 지운다
    size_t i = 0;
    while (n) {
        if (w[i] < n->c) n = n->lo; else if (w[i] > n->c) n = n->hi;
        else { if (i + 1 == w.size()) { bool was = n->end; n->end = false; return was; } n = n->eq; i++; }
    }
    return false;
}
void collect(const Node* n, std::string cur, std::vector<std::string>& out) {
    if (!n) return;
    collect(n->lo, cur, out);
    if (n->end) out.push_back(cur + n->c);
    collect(n->eq, cur + n->c, out);
    collect(n->hi, cur, out);
}
std::vector<std::string> startsWith(const Node* n, const std::string& p) {
    size_t i = 0; std::vector<std::string> out;
    while (n) {
        if (p[i] < n->c) n = n->lo; else if (p[i] > n->c) n = n->hi;
        else { if (i + 1 == p.size()) { if (n->end) out.push_back(p); collect(n->eq, p, out); return out; } n = n->eq; i++; }
    }
    return out;
}
void match(const Node* n, const std::string& pat, size_t i, std::string cur, std::vector<std::string>& out) {      // 와일드카드 '.' : lo/hi 를 모두 훑는다
    if (!n) return;
    char p = pat[i];
    if (p == '.' || p < n->c) match(n->lo, pat, i, cur, out);
    if (p == '.' || p == n->c) { if (i + 1 == pat.size()) { if (n->end) out.push_back(cur + n->c); } else match(n->eq, pat, i + 1, cur + n->c, out); }
    if (p == '.' || p > n->c) match(n->hi, pat, i, cur, out);
}
Node* prune(Node* n, size_t& removed) {                                                                    // 단어가 하나도 안 남은 가지를 떼어 낸다
    if (!n) return nullptr;
    n->lo = prune(n->lo, removed); n->eq = prune(n->eq, removed); n->hi = prune(n->hi, removed);
    if (!n->end && !n->lo && !n->eq && !n->hi) { delete n; ++removed; return nullptr; }
    return n;
}
size_t countNodes(const Node* n) { return n ? 1 + countNodes(n->lo) + countNodes(n->eq) + countNodes(n->hi) : 0; }
size_t countEnds(const Node* n) { return n ? (n->end ? 1 : 0) + countEnds(n->lo) + countEnds(n->eq) + countEnds(n->hi) : 0; }
int height(const Node* n) { return n ? 1 + std::max(height(n->lo), std::max(height(n->eq), height(n->hi))) : 0; }
bool ordered(const Node* n) { if (!n) return true; if (n->lo && n->lo->c >= n->c) return false; if (n->hi && n->hi->c <= n->c) return false; return ordered(n->lo) && ordered(n->eq) && ordered(n->hi); }
void destroy(Node* n) { if (!n) return; destroy(n->lo); destroy(n->eq); destroy(n->hi); delete n; }
std::string randomWord(std::mt19937& rng) { int len = 1 + (int)(rng() % 6); std::string w; for (int i = 0; i < len; ++i) w += (char)('a' + rng() % 5); return w; }
bool wildMatch(const std::string& w, const std::string& pat) { if (w.size() != pat.size()) return false; for (size_t i = 0; i < w.size(); ++i) if (pat[i] != '.' && pat[i] != w[i]) return false; return true; }

int main() {
    std::mt19937 rng(77); Node* root = nullptr; std::set<std::string> model, everInserted; size_t created = 0, charBudget = 0;
    for (int step = 0; step < 200000; ++step) { std::string w = randomWord(rng); int op = (int)(rng() % 10);                                    // ①
        if (op < 4) { model.insert(w); root = insert(root, w, 0, created); if (everInserted.insert(w).second) charBudget += w.size(); }
        else if (op < 6) { bool removed = erase(root, w); assert(removed == (model.erase(w) == 1)); }
        else if (op < 8) assert(contains(root, w) == (model.count(w) == 1));
        else { std::string p = w.substr(0, 1 + rng() % w.size()); std::vector<std::string> got = startsWith(root, p), want; for (auto it = model.lower_bound(p); it != model.end() && it->compare(0, p.size(), p) == 0; ++it) want.push_back(*it); assert(got == want); }
        if (step % 5000 == 0) { assert(ordered(root) && countEnds(root) == model.size() && countNodes(root) == created && created <= charBudget); } }
    for (int q = 0; q < 2000; ++q) { std::string pat = randomWord(rng); for (auto& c : pat) if (rng() % 3 == 0) c = '.'; std::vector<std::string> got, want; match(root, pat, 0, "", got);     // ②
        for (auto& w : model) if (wildMatch(w, pat)) want.push_back(w); assert(got == want); }
    {   std::vector<std::string> words; for (int i = 0; i < 1500; ++i) { std::string w; int v = i; for (int k = 0; k < 4; ++k) { w += (char)('a' + v % 26); v /= 26; } words.push_back(w); }   // ③ 삽입 순서
        std::sort(words.begin(), words.end()); Node* sorted = nullptr; size_t c = 0; for (auto& w : words) sorted = insert(sorted, w, 0, c);
        std::shuffle(words.begin(), words.end(), rng); Node* shuffled = nullptr; for (auto& w : words) shuffled = insert(shuffled, w, 0, c);
        int hs = height(sorted), hr = height(shuffled); assert(hs > 2 * hr && hr <= 4 * 12); destroy(sorted); destroy(shuffled); }
    {   size_t before = countNodes(root), removed = 0; root = prune(root, removed); size_t after = countNodes(root);                                    // ④ 가지치기
        assert(before - after == removed && countEnds(root) == model.size() && ordered(root));
        for (auto& w : model) assert(contains(root, w)); assert(after <= before && removed > 0); }
    std::cout << "TernarySearchTree: 200000 random operations matched std::set, wildcard queries matched direct comparison, sorted insertion degraded the height versus shuffled insertion, and pruning removed the nodes of erased words" << std::endl;
    destroy(root);
    return 0;
}
// Time Complexity: 삽입·검색 O(L + log σ) 평균 (σ = 알파벳 크기), 와일드카드 O(노드 수) 최악
// Space Complexity: O(총 글자 수) 노드 · 3 포인터
```
## SuffixArray()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 접미사 배열(트리 관점의 요약, 정본은 String.md Part 9): 접미사 트리의 잎을 사전순으로 훑은 순서를 평평한 정수 배열로 둔 것.  트리보다 공간이 훨씬 작고 캐시 친화적이다.  접두사 두 배(prefix doubling) + 계수 정렬로 O(n log n) 에 만들고 Kasai 로 LCP 를 O(n) 에 구한다.
//  LCP 배열이 접미사 트리의 내부 구조를 담는다: 서로 다른 부분 문자열 수 = n(n+1)/2 − ΣLCP,  가장 긴 반복 부분 문자열 = max LCP,  패턴 P 로 시작하는 접미사는 SA 의 연속 구간 (이진 탐색 O(m log n)).
//  ① 전수: 이진 문자열 길이 ≤ 14 전부(32766 개)와 3진 길이 ≤ 8 이 순진한 정렬과 같은 SA, 순진한 LCP, 순진한 부분 문자열 집합과 같은 개수  ② 피보나치·주기·같은 글자 문자열  ③ 100 만 글자: *정렬 인증서*(인접 쌍 (s[x], 순위[x+1]) < (s[y], 순위[y+1]), 순열)로 구성과 독립적으로 검증.
std::vector<int> buildSA(const std::string& s) {
    int n = (int)s.size(); if (n == 0) return {};
    int m = std::max(n, 256) + 1; std::vector<int> sa(n), rk(n), tmp(n), cnt(m, 0);
    for (int i = 0; i < n; ++i) { rk[i] = (unsigned char)s[i]; ++cnt[rk[i]]; } for (int i = 1; i < m; ++i) cnt[i] += cnt[i - 1]; for (int i = n - 1; i >= 0; --i) sa[--cnt[rk[i]]] = i;
    for (int k = 1;; k <<= 1) {
        int p = 0; for (int i = n - k; i < n; ++i) if (i >= 0) tmp[p++] = i;                                       // 두 번째 키가 빈 접미사 먼저
        for (int j = 0; j < n; ++j) if (sa[j] >= k) tmp[p++] = sa[j] - k;                                         // 나머지는 이전 정렬 순서대로
        std::fill(cnt.begin(), cnt.end(), 0); for (int i = 0; i < n; ++i) ++cnt[rk[i]]; for (int i = 1; i < m; ++i) cnt[i] += cnt[i - 1]; for (int j = n - 1; j >= 0; --j) sa[--cnt[rk[tmp[j]]]] = tmp[j];   // 첫 키로 안정 계수 정렬
        tmp[sa[0]] = 0; int classes = 1; for (int j = 1; j < n; ++j) { int x = sa[j], y = sa[j - 1]; int x2 = x + k < n ? rk[x + k] : -1, y2 = y + k < n ? rk[y + k] : -1; tmp[x] = (rk[x] == rk[y] && x2 == y2) ? classes - 1 : classes++; }
        rk = tmp; if (classes == n) break;
    }
    return sa;
}
std::vector<int> buildLCP(const std::string& s, const std::vector<int>& sa) {                                      // Kasai: lcp[i] = LCP(sa[i−1], sa[i]), lcp[0] = 0
    int n = (int)s.size(); std::vector<int> rank(n), lcp(n, 0); for (int i = 0; i < n; ++i) rank[sa[i]] = i;
    for (int i = 0, h = 0; i < n; ++i) { if (rank[i] > 0) { int j = sa[rank[i] - 1]; while (i + h < n && j + h < n && s[i + h] == s[j + h]) ++h; lcp[rank[i]] = h; if (h > 0) --h; } else h = 0; }
    return lcp;
}
std::pair<int, int> equalRange(const std::string& s, const std::vector<int>& sa, const std::string& p) {         // p 로 시작하는 접미사의 SA 구간 [lo, hi)
    auto lo = std::lower_bound(sa.begin(), sa.end(), p, [&](int i, const std::string& x) { return s.compare(i, x.size(), x) < 0; });
    auto hi = std::upper_bound(sa.begin(), sa.end(), p, [&](const std::string& x, int i) { return s.compare(i, x.size(), x) > 0; });
    return {(int)(lo - sa.begin()), (int)(hi - sa.begin())};
}
std::vector<int> naiveSA(const std::string& s) { std::vector<int> sa(s.size()); std::iota(sa.begin(), sa.end(), 0); std::sort(sa.begin(), sa.end(), [&](int a, int b) { return s.compare(a, std::string::npos, s, b, std::string::npos) < 0; }); return sa; }
bool certificate(const std::string& s, const std::vector<int>& sa) {                                               // 순열 + 인접 쌍이 (s[x], 순위[x+1]) 사전순
    int n = (int)s.size(); if ((int)sa.size() != n) return false; std::vector<int> rank(n, -1); for (int i = 0; i < n; ++i) { if (sa[i] < 0 || sa[i] >= n || rank[sa[i]] != -1) return false; rank[sa[i]] = i; }
    for (int i = 0; i + 1 < n; ++i) { int x = sa[i], y = sa[i + 1]; int rx = x + 1 < n ? rank[x + 1] : -1, ry = y + 1 < n ? rank[y + 1] : -1; if (s[x] > s[y] || (s[x] == s[y] && rx >= ry)) return false; }
    return true; }
void checkAll(const std::string& s) {
    std::vector<int> sa = buildSA(s), want = naiveSA(s); assert(sa == want); std::vector<int> lcp = buildLCP(s, sa); int n = (int)s.size(); long long sum = 0; int mx = 0;
    for (int i = 1; i < n; ++i) { int a = sa[i - 1], b = sa[i], h = 0; while (a + h < n && b + h < n && s[a + h] == s[b + h]) ++h; assert(lcp[i] == h); sum += h; mx = std::max(mx, h); }
    if (n <= 40) { std::set<std::string> subs; for (int i = 0; i < n; ++i) for (int l = 1; i + l <= n; ++l) subs.insert(s.substr(i, l)); assert((long long)subs.size() == (long long)n * (n + 1) / 2 - sum);
        int best = 0; for (int l = 1; l <= n; ++l) { std::set<std::string> cur; bool repeated = false; for (int i = 0; i + l <= n && !repeated; ++i) repeated = !cur.insert(s.substr(i, l)).second; if (repeated) best = l; } assert(best == mx); }   // 가장 긴 반복 부분 문자열
}

int main() {
    { std::string s = "banana"; assert(buildSA(s) == (std::vector<int>{5, 3, 1, 0, 4, 2})); std::vector<int> lcp = buildLCP(s, buildSA(s)); assert(lcp == (std::vector<int>{0, 1, 3, 0, 0, 2}));
      auto r = equalRange(s, buildSA(s), "ana"); assert(r.second - r.first == 2); r = equalRange(s, buildSA(s), "x"); assert(r.first == r.second); }                      // a, ana, anana, banana, na, nana
    for (int len = 0; len <= 14; ++len) for (int m = 0; m < (1 << len); ++m) { std::string s; for (int b = len - 1; b >= 0; --b) s += (m >> b & 1) ? 'b' : 'a'; checkAll(s); }         // ① 이진 전수 (길이 ≤ 14)
    for (int len = 1; len <= 8; ++len) { int total = 1; for (int i = 0; i < len; ++i) total *= 3; for (int m = 0; m < total; ++m) { std::string s; int x = m; for (int i = 0; i < len; ++i) { s += (char)('a' + x % 3); x /= 3; } checkAll(s); } }
    { std::string f1 = "a", f2 = "ab"; for (int i = 0; i < 12; ++i) { std::string f3 = f2 + f1; f1 = f2; f2 = f3; checkAll(f2.size() > 600 ? f2.substr(0, 600) : f2); } std::string per; for (int i = 0; i < 200; ++i) per += "abc"; checkAll(per); checkAll(std::string(300, 'a')); }          // ② 피보나치·주기
    std::mt19937 rng(23);
    for (int it = 0; it < 300; ++it) { int n = 1 + (int)(rng() % 60), sigma = 1 + (int)(rng() % 5); std::string s(n, 'a'); for (char& c : s) c = (char)('a' + rng() % sigma); checkAll(s);
        std::vector<int> sa = buildSA(s); for (int q = 0; q < 20; ++q) { std::string p; int pl = 1 + (int)(rng() % 4); for (int i = 0; i < pl; ++i) p += (char)('a' + rng() % (sigma + 1)); auto r = equalRange(s, sa, p); int occ = 0; for (int i = 0; i + pl <= n; ++i) occ += s.compare(i, pl, p) == 0; assert(r.second - r.first == occ); for (int k = r.first; k < r.second; ++k) assert(s.compare(sa[k], pl, p) == 0); } }   // 패턴 구간
    for (int mode = 0; mode < 3; ++mode) {                                                                       // ③ 100 만 글자
        const int n = 1000000; std::string s(n, 'a'); if (mode == 0) for (char& c : s) c = (char)('a' + rng() % 4); else if (mode == 1) for (int i = 0; i < n; ++i) s[i] = "ab"[i % 2];
        std::vector<int> sa = buildSA(s); assert(certificate(s, sa)); if (mode == 2) { for (int i = 0; i < n; ++i) assert(sa[i] == n - 1 - i); }                                   // aaaa…: 짧은 접미사가 먼저
    }
    std::cout << "SuffixArray: prefix-doubling SA matched naive sorting on every binary string up to length 14 and ternary up to 8 (plus LCP, distinct-substring count and longest repeat), pattern ranges matched naive counts, and 10^6-character strings passed the sortedness certificate" << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n log n), LCP O(n), 패턴 검색 O(m log n)
// Space Complexity: O(n)
```
# Part 11. 공간 분할 트리
## SegmentTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// 세그먼트 트리(반복형, 아래에서 위로): 배열 d[1 .. 2·size) 에 완전 이진 트리를 담고 잎은 d[size + i].  한 점 갱신 O(log n), 구간 [l, r) 질의 O(log n).
//  *모노이드*(결합 법칙 + 항등원) 이면 무엇이든 담을 수 있다 — 합·최솟값·gcd 뿐 아니라 교환 법칙이 없는 문자열 연결·행렬 곱·"최대 부분 배열 합"까지.  교환 법칙이 없으므로 질의는 왼쪽 누적(sl)과 오른쪽 누적(sr)을 따로 두어 순서를 지킨다.
//  (구간 아핀 변환 지연 전파 판은 AdvancedDataStructures.md Part 6, 일반 지연 전파는 Tree.md Part 12.)
//  maxRight(l, f): f(구간 값) 이 참인 가장 긴 [l, r) 의 r 을 트리 *내려가기*로 O(log n) 에 찾는다 (f 는 단조).  ① n = 1..70 에서 *모든* 구간 [l, r) 을 순진한 왼쪽→오른쪽 접기와 대조 (합·최솟값·gcd·문자열 연결·2×2 행렬 곱 mod p·최대 부분 배열 합)
//  ② maxRight 를 모든 (l, K) 에서 순진한 선형 탐색과 대조  ③ build(O(n)) 결과 = 점 갱신 n 번의 결과  ④ n = 10^6, 갱신 10^6 번 — 10^5 번마다 접두사 합 배열로 질의를 대조.
template <class T, class Op> struct SegTree {
    int n, size; T e; Op op; std::vector<T> d;
    SegTree(int n_, T e_, Op op_) : n(n_), e(e_), op(op_) { size = 1; while (size < n) size <<= 1; d.assign(2 * size, e); }
    void build(const std::vector<T>& a) { for (int i = 0; i < n; ++i) d[size + i] = a[i]; for (int i = size - 1; i >= 1; --i) d[i] = op(d[2 * i], d[2 * i + 1]); }
    void set(int p, T v) { p += size; d[p] = v; while (p >>= 1) d[p] = op(d[2 * p], d[2 * p + 1]); }
    T get(int p) const { return d[p + size]; }
    T query(int l, int r) const { T sl = e, sr = e; for (l += size, r += size; l < r; l >>= 1, r >>= 1) { if (l & 1) sl = op(sl, d[l++]); if (r & 1) sr = op(d[--r], sr); } return op(sl, sr); }
    template <class F> int maxRight(int l, F f) const {                                                          // f(op(a[l..r−1])) 이 참인 최대 r
        if (l == n) return n; l += size; T sm = e;
        do { while (l % 2 == 0) l >>= 1;
             if (!f(op(sm, d[l]))) { while (l < size) { l = 2 * l; if (f(op(sm, d[l]))) { sm = op(sm, d[l]); ++l; } } return l - size; }
             sm = op(sm, d[l]); ++l; } while ((l & -l) != l);
        return n; }
};
struct Best { long long sum, best, pre, suf; };                                                                  // 최대 부분 배열 합 모노이드 (best/pre/suf 는 비어 있지 않은 구간)
const long long NEG = -(1LL << 50);
Best bestOp(const Best& a, const Best& b) { return {a.sum + b.sum, std::max({a.best, b.best, a.suf + b.pre}), std::max(a.pre, a.sum + b.pre), std::max(b.suf, b.sum + a.suf)}; }
Best bestLeaf(long long v) { return {v, v, v, v}; }
const Best bestId = {0, NEG, NEG, NEG};
struct Mat { long long a, b, c, d; }; const long long MOD = 1000000007LL;
Mat matOp(const Mat& x, const Mat& y) { return {(x.a * y.a + x.b * y.c) % MOD, (x.a * y.b + x.b * y.d) % MOD, (x.c * y.a + x.d * y.c) % MOD, (x.c * y.b + x.d * y.d) % MOD}; }
bool operator==(const Mat& x, const Mat& y) { return x.a == y.a && x.b == y.b && x.c == y.c && x.d == y.d; }
bool operator==(const Best& x, const Best& y) { return x.sum == y.sum && x.best == y.best && x.pre == y.pre && x.suf == y.suf; }

template <class T, class Op> void exhaustive(int n, T e, Op op, const std::vector<T>& a) {                      // 모든 [l, r) × 순진한 접기
    SegTree<T, Op> st(n, e, op); st.build(a);
    for (int l = 0; l <= n; ++l) { T acc = e; for (int r = l; r <= n; ++r) { assert(st.query(l, r) == acc); if (r < n) acc = op(acc, a[r]); } }
    SegTree<T, Op> viaSet(n, e, op); for (int i = 0; i < n; ++i) viaSet.set(i, a[i]); assert(viaSet.d == st.d);   // ③ build = 점 갱신 n 번
}

int main() {
    std::mt19937 rng(61);
    for (int n = 1; n <= 70; ++n) {
        std::vector<long long> v(n); for (auto& x : v) x = (long long)(rng() % 2001) - 1000;
        { auto op = [](long long x, long long y) { return x + y; }; exhaustive<long long>(n, 0, op, v); }
        { auto op = [](long long x, long long y) { return std::min(x, y); }; exhaustive<long long>(n, (1LL << 60), op, v); }
        { std::vector<long long> g(n); for (int i = 0; i < n; ++i) g[i] = (long long)(rng() % 60); auto op = [](long long x, long long y) { return std::__gcd(x, y); }; exhaustive<long long>(n, 0, op, g); }
        { std::vector<std::string> s(n); for (int i = 0; i < n; ++i) s[i] = std::string(1, (char)('a' + rng() % 26)); auto op = [](const std::string& x, const std::string& y) { return x + y; }; exhaustive<std::string>(n, "", op, s); }   // 교환 법칙 없음
        { std::vector<Mat> m(n); for (auto& x : m) x = {(long long)(rng() % 10), (long long)(rng() % 10), (long long)(rng() % 10), (long long)(rng() % 10)}; auto op = [](const Mat& x, const Mat& y) { return matOp(x, y); }; exhaustive<Mat>(n, Mat{1, 0, 0, 1}, op, m); }
        { std::vector<Best> b(n); for (int i = 0; i < n; ++i) b[i] = bestLeaf(v[i]);
          SegTree<Best, Best (*)(const Best&, const Best&)> st(n, bestId, bestOp); st.build(b);
          for (int l = 0; l < n; ++l) { long long run = NEG; for (int r = l + 1; r <= n; ++r) { long long bestSum = NEG; for (int x = l; x < r; ++x) { long long s = 0; for (int y = x; y < r; ++y) { s += v[y]; bestSum = std::max(bestSum, s); } } assert(st.query(l, r).best == bestSum); run = bestSum; } (void)run; } }                // Kadane 대신 O(n³) 완전 탐색과 대조
    }
    for (int n : {1, 2, 5, 16, 33, 100}) {                                                                       // ② maxRight (합 ≤ K, 값은 음이 아님)
        std::vector<long long> a(n); for (auto& x : a) x = (long long)(rng() % 20); auto op = [](long long x, long long y) { return x + y; }; SegTree<long long, decltype(op)> st(n, 0, op); st.build(a);
        for (int l = 0; l <= n; ++l) for (long long K = 0; K <= 400; K += 7) { int r = l; long long s = 0; while (r < n && s + a[r] <= K) s += a[r++]; assert(st.maxRight(l, [K](long long x) { return x <= K; }) == r); }
    }
    { const int n = 1000000; auto op = [](long long x, long long y) { return x + y; }; SegTree<long long, decltype(op)> st(n, 0, op); std::vector<long long> a(n, 0);        // ④
      for (long step = 1; step <= 1000000; ++step) { int p = (int)(rng() % n); long long v = (long long)(rng() % 1000000) - 500000; a[p] = v; st.set(p, v);
        if (step % 100000 == 0) { std::vector<long long> pre(n + 1, 0); for (int i = 0; i < n; ++i) pre[i + 1] = pre[i] + a[i]; for (int q = 0; q < 2000; ++q) { int l = (int)(rng() % n), r = l + (int)(rng() % (n - l + 1)); assert(st.query(l, r) == pre[r] - pre[l]); } assert(st.d[1] == pre[n]); } } }
    std::cout << "SegmentTree: every range query on arrays of size 1..70 matched the naive left-to-right fold for sum/min/gcd/string-concat/2x2-matrix/max-subarray monoids, maxRight matched linear search, build equalled n point updates, and 10^6 updates on 10^6 elements matched prefix sums" << std::endl;
    return 0;
}
// Time Complexity: build O(N), update/query/maxRight O(log N)
// Space Complexity: O(N)
```

## FenwickTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 펜윅 트리(이진 인덱스 트리): t[i] 가 구간 (i − lowbit(i), i] 의 합을 담는다 (lowbit(i) = i & −i).  갱신은 i += lowbit(i) 로 올라가고 접두사 합은 i −= lowbit(i) 로 내려간다 — 둘 다 O(log n).  세그먼트 트리의 절반 메모리, 상수도 작지만 *역원이 있는 연산*(합)에 한정된다.
//  (2 차원 확장은 AdvancedDataStructures.md Part 6.)
//  ① 구조 성질: 모든 i 에서 t[i] 가 정확히 (i − lowbit(i), i] 의 합  ② 선형 시간 구성(각 칸을 부모에게 한 번 더하기) = 갱신 n 번의 결과  ③ lowerBound(target): 접두사 합이 target 이상이 되는 첫 인덱스를 트리 내려가기로 O(log n) (값은 음이 아님)
//  ④ 구간 갱신·구간 합(두 BIT)  ⑤ 응용: 역전 수(inversions) 를 병합 정렬 계수와 대조, 동적 k 번째 작은 값을 정렬 벡터와 대조  ⑥ n = 10^6 에서 갱신 10^6 번, 10^5 번마다 접두사 합 배열로 대조.
struct Fenwick {
    int n; std::vector<long long> t;
    explicit Fenwick(int n_) : n(n_), t(n_ + 1, 0) {}
    explicit Fenwick(const std::vector<long long>& a) : n((int)a.size()), t(a.size() + 1, 0) { for (int i = 1; i <= n; ++i) { t[i] += a[i - 1]; int j = i + (i & -i); if (j <= n) t[j] += t[i]; } }   // O(n) 구성
    void add(int i, long long v) { for (++i; i <= n; i += i & -i) t[i] += v; }
    long long prefix(int i) const { long long s = 0; for (++i; i > 0; i -= i & -i) s += t[i]; return s; }          // a[0..i] 의 합 (i = −1 이면 0)
    long long range(int l, int r) const { return prefix(r) - prefix(l - 1); }                                      // a[l..r]
    int lowerBound(long long target) const { int pos = 0, pw = 1; while (pw * 2 <= n) pw *= 2; long long rem = target; for (; pw; pw >>= 1) if (pos + pw <= n && t[pos + pw] < rem) { pos += pw; rem -= t[pos]; } return pos; }   // prefix(i) ≥ target 인 첫 i (없으면 n)
};
struct RangeFenwick {                                                                                           // 구간 더하기 + 구간 합: 차분 두 개 B1, B2 의 조합
    int n; Fenwick b1, b2; explicit RangeFenwick(int n_) : n(n_), b1(n_ + 1), b2(n_ + 1) {}
    void add(int l, int r, long long v) { b1.add(l, v); b1.add(r + 1, -v); b2.add(l, v * l); b2.add(r + 1, -v * (r + 1)); }                // [l, r] 에 v 를 더한다
    long long prefix(int i) const { return b1.prefix(i) * (i + 1) - b2.prefix(i); }                                // a[0..i] 의 합
    long long range(int l, int r) const { return prefix(r) - (l ? prefix(l - 1) : 0); }
};
long long mergeCount(std::vector<int>& a, std::vector<int>& tmp, int lo, int hi) {                               // 독립 오라클: 병합 정렬로 역전 수
    if (hi - lo < 2) return 0; int mid = (lo + hi) / 2; long long c = mergeCount(a, tmp, lo, mid) + mergeCount(a, tmp, mid, hi); int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) { if (a[i] <= a[j]) tmp[k++] = a[i++]; else { tmp[k++] = a[j++]; c += mid - i; } } while (i < mid) tmp[k++] = a[i++]; while (j < hi) tmp[k++] = a[j++]; for (int x = lo; x < hi; ++x) a[x] = tmp[x]; return c; }

int main() {
    std::mt19937 rng(71);
    for (int n = 1; n <= 200; ++n) {                                                                             // ① ② ③ 작은 n 전부
        std::vector<long long> a(n); for (auto& x : a) x = (long long)(rng() % 50); Fenwick built(a), viaAdd(n); for (int i = 0; i < n; ++i) viaAdd.add(i, a[i]); assert(built.t == viaAdd.t);
        for (int i = 1; i <= n; ++i) { long long s = 0; for (int j = i - (i & -i); j < i; ++j) s += a[j]; assert(built.t[i] == s); }          // t[i] = (i − lowbit, i] 의 합
        std::vector<long long> pre(n + 1, 0); for (int i = 0; i < n; ++i) pre[i + 1] = pre[i] + a[i];
        for (int l = 0; l < n; ++l) for (int r = l; r < n; ++r) assert(built.range(l, r) == pre[r + 1] - pre[l]);
        for (long long target = 0; target <= pre[n] + 3; ++target) { int want = 0; while (want < n && pre[want + 1] < target) ++want; assert(built.lowerBound(target) == want); }
        RangeFenwick rf(n); std::vector<long long> ref(n, 0); for (int op = 0; op < 60; ++op) { int l = (int)(rng() % n), r = l + (int)(rng() % (n - l)); long long v = (long long)(rng() % 21) - 10; rf.add(l, r, v); for (int i = l; i <= r; ++i) ref[i] += v;
            int ql = (int)(rng() % n), qr = ql + (int)(rng() % (n - ql)); long long s = 0; for (int i = ql; i <= qr; ++i) s += ref[i]; assert(rf.range(ql, qr) == s); }    // ④
    }
    for (int it = 0; it < 200; ++it) {                                                                           // ⑤ 역전 수
        int n = 1 + (int)(rng() % 300); std::vector<int> a(n); for (auto& x : a) x = (int)(rng() % 50); std::vector<int> sorted = a; std::sort(sorted.begin(), sorted.end()); sorted.erase(std::unique(sorted.begin(), sorted.end()), sorted.end());
        Fenwick bit(n + 1); long long inv = 0, brute = 0; for (int i = 0; i < n; ++i) { int rk = (int)(std::lower_bound(sorted.begin(), sorted.end(), a[i]) - sorted.begin()); inv += i - bit.prefix(rk); bit.add(rk, 1); }
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) brute += a[i] > a[j]; assert(inv == brute); }
    { const int n = 200000; std::vector<int> a(n); std::iota(a.begin(), a.end(), 0); std::shuffle(a.begin(), a.end(), rng); std::vector<int> b = a, tmp(n); long long want = mergeCount(b, tmp, 0, n); Fenwick bit(n); long long inv = 0; for (int i = 0; i < n; ++i) { inv += i - bit.prefix(a[i]); bit.add(a[i], 1); } assert(inv == want);
      std::vector<int> rev(n); for (int i = 0; i < n; ++i) rev[i] = n - 1 - i; Fenwick b2(n); long long inv2 = 0; for (int i = 0; i < n; ++i) { inv2 += i - b2.prefix(rev[i]); b2.add(rev[i], 1); } assert(inv2 == (long long)n * (n - 1) / 2); }
    { const int V = 5000; Fenwick cnt(V); std::vector<int> sortedVals; for (int step = 0; step < 100000; ++step) {                      // 동적 k 번째 작은 값
        int op = (int)(rng() % 3); if (op < 2 || sortedVals.empty()) { int v = (int)(rng() % V); cnt.add(v, 1); sortedVals.insert(std::upper_bound(sortedVals.begin(), sortedVals.end(), v), v); }
        else { size_t idx = rng() % sortedVals.size(); int v = sortedVals[idx]; cnt.add(v, -1); sortedVals.erase(sortedVals.begin() + idx); }
        if (!sortedVals.empty()) { size_t k = rng() % sortedVals.size(); assert(cnt.lowerBound((long long)k + 1) == sortedVals[k]); } } }                                    // (k+1) 번째 작은 값
    { const int n = 1000000; Fenwick bit(n); std::vector<long long> a(n, 0);                                     // ⑥
      for (long step = 1; step <= 1000000; ++step) { int p = (int)(rng() % n); long long v = (long long)(rng() % 2001) - 1000; a[p] += v; bit.add(p, v);
        if (step % 100000 == 0) { std::vector<long long> pre(n + 1, 0); for (int i = 0; i < n; ++i) pre[i + 1] = pre[i] + a[i]; for (int q = 0; q < 2000; ++q) { int i = (int)(rng() % n); assert(bit.prefix(i) == pre[i + 1]); } assert(bit.prefix(n - 1) == pre[n]); } } }
    std::cout << "FenwickTree: t[i] covered exactly (i-lowbit(i), i] for all n <= 200, linear build equalled n updates, descent-based lowerBound and range-update/range-sum matched naive scans, inversion counts matched merge-sort counting, dynamic k-th value matched a sorted vector, and 10^6 updates on 10^6 elements matched prefix sums" << std::endl;
    return 0;
}
// Time Complexity: build O(N), add/prefix O(log N)
// Space Complexity: O(N)
```

## KDTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <random>
#include <vector>
#include <cassert>

// k-d 트리: k 차원 점들을 축을 번갈아 가며 중앙값으로 이진 분할한다.  최근접 이웃 탐색은 "가까운 쪽 먼저, 반대쪽은 분할 평면까지의 거리가 현재 최선보다 작을 때만" 방문하는 가지치기로
// 평균 O(log n).  차원이 커지면(약 20 이상) 가지치기가 듣지 않는 "차원의 저주" 가 있다
typedef std::array<double, 2> P;
struct KD {
    std::vector<P> pts;
    void build(int lo, int hi, int axis) {                        // pts[lo, hi) 구간을 중앙값 기준으로 재배열 (구간 안에서 중앙이 노드)
        if (hi - lo <= 1) return;
        int mid = (lo + hi) / 2;
        std::nth_element(pts.begin() + lo, pts.begin() + mid, pts.begin() + hi, [&](const P& a, const P& b) { return a[axis] < b[axis]; });
        build(lo, mid, 1 - axis); build(mid + 1, hi, 1 - axis);
    }
    static double d2(const P& a, const P& b) { return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]); }
    void nearest(int lo, int hi, int axis, const P& q, P& best, double& bestD) const {
        if (lo >= hi) return;
        int mid = (lo + hi) / 2; const P& node = pts[mid];
        double d = d2(node, q); if (d < bestD) { bestD = d; best = node; }
        double diff = q[axis] - node[axis];
        int nearLo = diff < 0 ? lo : mid + 1, nearHi = diff < 0 ? mid : hi, farLo = diff < 0 ? mid + 1 : lo, farHi = diff < 0 ? hi : mid;
        nearest(nearLo, nearHi, 1 - axis, q, best, bestD);
        if (diff * diff < bestD) nearest(farLo, farHi, 1 - axis, q, best, bestD);     // 분할 평면이 최선보다 가까울 때만 반대쪽 탐색
    }
    int rangeCount(int lo, int hi, int axis, const P& a, const P& b) const {          // 직사각형 [a, b] 안의 점 수
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2; const P& n = pts[mid]; int c = (n[0] >= a[0] && n[0] <= b[0] && n[1] >= a[1] && n[1] <= b[1]);
        if (a[axis] <= n[axis]) c += rangeCount(lo, mid, 1 - axis, a, b);
        if (b[axis] >= n[axis]) c += rangeCount(mid + 1, hi, 1 - axis, a, b);
        return c;
    }
};

int main() {
    std::mt19937 rng(22); std::uniform_real_distribution<double> U(0, 100);
    KD kd; for (int i = 0; i < 3000; i++) kd.pts.push_back({U(rng), U(rng)});
    std::vector<P> original = kd.pts;
    kd.build(0, kd.pts.size(), 0);
    for (int t = 0; t < 200; t++) {
        P q = {U(rng), U(rng)}, best{}; double bestD = std::numeric_limits<double>::max();
        kd.nearest(0, kd.pts.size(), 0, q, best, bestD);
        double brute = std::numeric_limits<double>::max(); for (auto& p : original) brute = std::min(brute, KD::d2(p, q));
        assert(std::fabs(bestD - brute) < 1e-12);                           // 완전 탐색과 같은 최근접 거리
        P a = {U(rng) * 0.5, U(rng) * 0.5}, b = {a[0] + 30, a[1] + 30}; int cnt = 0;
        for (auto& p : original) cnt += (p[0] >= a[0] && p[0] <= b[0] && p[1] >= a[1] && p[1] <= b[1]);
        assert(kd.rangeCount(0, kd.pts.size(), 0, a, b) == cnt);            // 범위 질의도 일치
    }
    std::cout << "KDTree: nearest-neighbour and range queries match brute force on 3000 points." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n log n), 최근접 평균 O(log n)
// Space Complexity: O(n)
```
## QuadTree()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 쿼드트리: 2차원 영역을 4개의 사분면으로 재귀 분할한다.  한 영역에 점이 CAP 개를 넘으면 쪼갠다.  범위 질의는 질의 사각형과 겹치는 사분면만 방문한다.
// 게임의 충돌 후보 찾기, 지도 타일, 이미지 압축에 쓰인다.  (같은 점이 여러 개 몰리는 경우를 위해 최대 깊이를 둔다)
struct Pt { double x, y; };
struct Rect { double x0, y0, x1, y1; bool contains(const Pt& p) const { return p.x >= x0 && p.x < x1 && p.y >= y0 && p.y < y1; }
              bool intersects(const Rect& r) const { return x0 < r.x1 && r.x0 < x1 && y0 < r.y1 && r.y0 < y1; } };
class QuadTree {
    static const int CAP = 4, MAXD = 12;
    Rect box; int depth; std::vector<Pt> pts; std::unique_ptr<QuadTree> kid[4];
public:
    QuadTree(Rect b, int d = 0) : box(b), depth(d) {}
    bool insert(const Pt& p) {
        if (!box.contains(p)) return false;
        if (!kid[0] && ((int)pts.size() < CAP || depth >= MAXD)) { pts.push_back(p); return true; }
        if (!kid[0]) {                                                         // 분할: 네 사분면 생성 후 기존 점 재배치
            double mx = (box.x0 + box.x1) / 2, my = (box.y0 + box.y1) / 2;
            kid[0].reset(new QuadTree({box.x0, box.y0, mx, my}, depth + 1)); kid[1].reset(new QuadTree({mx, box.y0, box.x1, my}, depth + 1));
            kid[2].reset(new QuadTree({box.x0, my, mx, box.y1}, depth + 1));  kid[3].reset(new QuadTree({mx, my, box.x1, box.y1}, depth + 1));
            std::vector<Pt> old; old.swap(pts); for (auto& q : old) insert(q);
        }
        for (auto& k : kid) if (k->insert(p)) return true;
        return false;
    }
    int query(const Rect& r) const {
        if (!box.intersects(r)) return 0;
        int c = 0; for (auto& p : pts) c += (p.x >= r.x0 && p.x < r.x1 && p.y >= r.y0 && p.y < r.y1);
        if (kid[0]) for (auto& k : kid) c += k->query(r);
        return c;
    }
    int nodes() const { int c = 1; if (kid[0]) for (auto& k : kid) c += k->nodes(); return c; }
};

int main() {
    std::mt19937 rng(23); std::uniform_real_distribution<double> U(0, 1000);
    QuadTree qt({0, 0, 1000, 1000}); std::vector<Pt> all;
    for (int i = 0; i < 5000; i++) { Pt p{U(rng), U(rng)}; all.push_back(p); assert(qt.insert(p)); }
    assert(!qt.insert({-1, 5}));                                                 // 영역 밖의 점은 거부
    for (int t = 0; t < 200; t++) {
        double x = U(rng) * 0.9, y = U(rng) * 0.9; Rect r{x, y, x + 80, y + 80}; int brute = 0;
        for (auto& p : all) brute += (p.x >= r.x0 && p.x < r.x1 && p.y >= r.y0 && p.y < r.y1);
        assert(qt.query(r) == brute);
    }
    QuadTree dup({0, 0, 1, 1}); for (int i = 0; i < 100; i++) assert(dup.insert({0.5, 0.5}));        // 같은 점 100개도 무한 분할하지 않는다
    std::cout << "QuadTree: 5000 points in " << qt.nodes() << " nodes; range queries match brute force." << std::endl;
    return 0;
}
// Time Complexity: 삽입 O(깊이), 범위 질의 평균 O(log n + k)
// Space Complexity: O(n)
```
## Octree()
### 대표코드
```cpp
#include <iostream>
#include <array>
#include <cmath>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 옥트리: 3차원 공간을 8개의 팔분면으로 재귀 분할한다 (쿼드트리의 3차원판).  3D 렌더링의 가시성 판정·충돌 검출·포인트 클라우드·복셀 맵에 쓰인다.
// 반경 질의: 구와 겹치지 않는 팔분면은 통째로 건너뛴다
struct V3 { double x, y, z; };
class Octree {
    static const int CAP = 8, MAXD = 10;
    V3 lo, hi; int depth; std::vector<V3> pts; std::unique_ptr<Octree> kid[8];
    int child(const V3& p) const { V3 m{(lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2}; return (p.x >= m.x) | (p.y >= m.y) << 1 | (p.z >= m.z) << 2; }
    bool inside(const V3& p) const { return p.x >= lo.x && p.x < hi.x && p.y >= lo.y && p.y < hi.y && p.z >= lo.z && p.z < hi.z; }
    static double clamp(double v, double a, double b) { return v < a ? a : v > b ? b : v; }
    bool sphereHits(const V3& c, double r) const {                      // 구 중심에서 상자까지의 최단 거리 <= 반지름
        double dx = c.x - clamp(c.x, lo.x, hi.x), dy = c.y - clamp(c.y, lo.y, hi.y), dz = c.z - clamp(c.z, lo.z, hi.z);
        return dx * dx + dy * dy + dz * dz <= r * r;
    }
public:
    Octree(V3 a, V3 b, int d = 0) : lo(a), hi(b), depth(d) {}
    bool insert(const V3& p) {
        if (!inside(p)) return false;
        if (!kid[0] && ((int)pts.size() < CAP || depth >= MAXD)) { pts.push_back(p); return true; }
        if (!kid[0]) {
            V3 m{(lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2};
            for (int i = 0; i < 8; i++) kid[i].reset(new Octree({i & 1 ? m.x : lo.x, i & 2 ? m.y : lo.y, i & 4 ? m.z : lo.z}, {i & 1 ? hi.x : m.x, i & 2 ? hi.y : m.y, i & 4 ? hi.z : m.z}, depth + 1));
            std::vector<V3> old; old.swap(pts); for (auto& q : old) insert(q);
        }
        return kid[child(p)]->insert(p);
    }
    int radius(const V3& c, double r) const {
        if (!sphereHits(c, r)) return 0;
        int cnt = 0; for (auto& p : pts) cnt += ((p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y) + (p.z - c.z) * (p.z - c.z) <= r * r);
        if (kid[0]) for (auto& k : kid) cnt += k->radius(c, r);
        return cnt;
    }
};

int main() {
    std::mt19937 rng(24); std::uniform_real_distribution<double> U(0, 100);
    Octree oc({0, 0, 0}, {100, 100, 100}); std::vector<V3> all;
    for (int i = 0; i < 4000; i++) { V3 p{U(rng), U(rng), U(rng)}; all.push_back(p); assert(oc.insert(p)); }
    for (int t = 0; t < 100; t++) {
        V3 c{U(rng), U(rng), U(rng)}; double r = 5 + U(rng) * 0.2; int brute = 0;
        for (auto& p : all) brute += ((p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y) + (p.z - c.z) * (p.z - c.z) <= r * r);
        assert(oc.radius(c, r) == brute);
    }
    std::cout << "Octree: radius queries match brute force on 4000 points." << std::endl;
    return 0;
}
// Time Complexity: 삽입 O(깊이), 반경 질의 평균 O(log n + k)
// Space Complexity: O(n)
```
## BSPTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <memory>
#include <random>
#include <vector>

// BSP 트리(이진 공간 분할): 선분(3D 에서는 다각형) 하나의 직선으로 공간을 앞/뒤 두 반평면으로 나누고 재귀한다.  분할선에 걸친 선분은 교점에서 둘로 쪼갠다.
// 시점에서 먼 쪽부터 가까운 쪽 순서로 순회하면 정렬 없이 화가 알고리즘(painter's algorithm)의 올바른 그리기 순서가 나온다 (둠(DOOM) 등 초기 3D 게임의 렌더링).
//  ① 손으로 만든 예: 평행한 세로선 3 개의 먼 → 가까운 순서(시점 x=0 과 x=10), 십자 모양에서 세로선이 둘로 쪼개져 조각 3 개이고 *전체 길이는 보존*
//  ② 무작위 장면 250 개(정수 좌표 선분 2~12 개, 서로 교차 가능): 조각의 길이 합 == 원래 길이 합, 모든 조각이 원래 선분 위에 있고 조각들이 원래 선분을 겹침 없이 덮음  ③ 시점 40 개씩에서 *순서 정확성*: 시점에서 쏜 광선이 두 조각 X, Y 를 모두 맞히고 X 가 더 가까우면(= X 가 Y 를 가린다) X 가 Y 보다 *나중에* 그려져야 한다 — 임계 각도 사이 방향을 표본으로 쌍마다 직접 검사(트리 구조와 무관한 오라클)
//  ④ 좋은 분할선(조각 수가 적은 선분을 고르는 휴리스틱)이 임의 선택보다 조각을 덜 만든다는 것을 합계로 확인  ⑤ 가까운 → 먼 순회도 같은 조각 집합을 돌려준다
struct Seg { double x1, y1, x2, y2; int origin; double len() const { return std::hypot(x2 - x1, y2 - y1); } };
const double EPS = 1e-9;
double side(const Seg& line, double x, double y) { return (line.x2 - line.x1) * (y - line.y1) - (line.y2 - line.y1) * (x - line.x1); }    // >0: 왼쪽(앞), <0: 오른쪽(뒤)

struct Node { Seg splitter; std::vector<Seg> same; std::unique_ptr<Node> front, back; };
int splitsMade = 0;
size_t pickSplitter(const std::vector<Seg>& segs, bool smart) {                                       // 똑똑한 선택: 이 직선이 다른 선분을 가장 덜 가르는 것
    if (!smart) return 0; size_t best = 0; int bestCuts = 1 << 30;
    for (size_t i = 0; i < segs.size(); ++i) { int cuts = 0; for (size_t j = 0; j < segs.size(); ++j) { if (i == j) continue; double d1 = side(segs[i], segs[j].x1, segs[j].y1), d2 = side(segs[i], segs[j].x2, segs[j].y2); if ((d1 > EPS && d2 < -EPS) || (d1 < -EPS && d2 > EPS)) ++cuts; } if (cuts < bestCuts) { bestCuts = cuts; best = i; } }
    return best; }
std::unique_ptr<Node> build(std::vector<Seg> segs, bool smart = false) {
    if (segs.empty()) return nullptr;
    size_t pick = pickSplitter(segs, smart); std::swap(segs[0], segs[pick]);
    auto n = std::make_unique<Node>(); n->splitter = segs[0]; n->same.push_back(segs[0]);
    std::vector<Seg> f, b;
    for (size_t i = 1; i < segs.size(); i++) {
        const Seg& s = segs[i]; double d1 = side(n->splitter, s.x1, s.y1), d2 = side(n->splitter, s.x2, s.y2);
        if (std::fabs(d1) < EPS && std::fabs(d2) < EPS) n->same.push_back(s);          // 같은 직선 위
        else if (d1 > -EPS && d2 > -EPS) f.push_back(s);
        else if (d1 < EPS && d2 < EPS) b.push_back(s);
        else {                                                                            // 분할선을 가로지름: 교점에서 둘로 쪼갠다
            ++splitsMade; double t = d1 / (d1 - d2); double mx = s.x1 + t * (s.x2 - s.x1), my = s.y1 + t * (s.y2 - s.y1);
            Seg a{s.x1, s.y1, mx, my, s.origin}, c{mx, my, s.x2, s.y2, s.origin};
            if (d1 > 0) { f.push_back(a); b.push_back(c); } else { b.push_back(a); f.push_back(c); }
        }
    }
    n->front = build(f, smart); n->back = build(b, smart);
    return n;
}
void farToNear(const Node* n, double ex, double ey, std::vector<Seg>& out) {                    // 시점 (ex, ey) 에서 먼 순서
    if (!n) return;
    bool eyeFront = side(n->splitter, ex, ey) >= 0;
    farToNear(eyeFront ? n->back.get() : n->front.get(), ex, ey, out);                          // 시점 반대편이 더 멀다
    for (auto& s : n->same) out.push_back(s);
    farToNear(eyeFront ? n->front.get() : n->back.get(), ex, ey, out);
}
void nearToFar(const Node* n, double ex, double ey, std::vector<Seg>& out) {
    if (!n) return;
    bool eyeFront = side(n->splitter, ex, ey) >= 0;
    nearToFar(eyeFront ? n->front.get() : n->back.get(), ex, ey, out);
    for (auto& s : n->same) out.push_back(s);
    nearToFar(eyeFront ? n->back.get() : n->front.get(), ex, ey, out);
}
bool onSegment(const Seg& o, double x, double y) { double cross = (o.x2 - o.x1) * (y - o.y1) - (o.y2 - o.y1) * (x - o.x1); if (std::fabs(cross) > 1e-6 * (1 + o.len())) return false; double dot = (x - o.x1) * (o.x2 - o.x1) + (y - o.y1) * (o.y2 - o.y1); return dot > -1e-6 && dot < o.len() * o.len() + 1e-6; }
bool rayHit(double ex, double ey, double dx, double dy, const Seg& s, double& dist) {                  // 시점 (ex, ey) 에서 방향 (dx, dy) 광선이 선분을 맞히는가, 맞히면 거리
    double qx = s.x2 - s.x1, qy = s.y2 - s.y1, den = dx * qy - dy * qx; if (std::fabs(den) < 1e-12) return false;
    double px = s.x1 - ex, py = s.y1 - ey, t = (px * qy - py * qx) / den, u = (px * dy - py * dx) / den;
    if (t <= 1e-9 || u < -1e-9 || u > 1 + 1e-9) return false; dist = t * std::hypot(dx, dy); return true; }
bool occludes(const Seg& X, const Seg& Y, double ex, double ey) {                                      // 어떤 광선이 X 를 Y 보다 먼저 맞히는가 (오라클: 임계 각도 사이 방향 표본)
    std::vector<double> ang = {std::atan2(X.y1 - ey, X.x1 - ex), std::atan2(X.y2 - ey, X.x2 - ex), std::atan2(Y.y1 - ey, Y.x1 - ex), std::atan2(Y.y2 - ey, Y.x2 - ex)}; std::sort(ang.begin(), ang.end());
    for (size_t i = 0; i + 1 < ang.size(); ++i) { if (ang[i + 1] - ang[i] < 1e-7 || ang[i + 1] - ang[i] > 3.0) continue; double a = (ang[i] + ang[i + 1]) / 2, dx = std::cos(a), dy = std::sin(a), dX, dY;
        if (rayHit(ex, ey, dx, dy, X, dX) && rayHit(ex, ey, dx, dy, Y, dY) && dX < dY - 1e-6) return true; }
    return false; }

int main() {
    {   std::vector<Seg> lines = {{2, 0, 2, 5, 0}, {1, 0, 1, 5, 1}, {3, 0, 3, 5, 2}};                                    // ① 손으로 만든 예
        auto tree = build(lines); std::vector<Seg> order; farToNear(tree.get(), 0, 2, order);
        assert(order.size() == 3 && order[0].x1 == 3 && order[1].x1 == 2 && order[2].x1 == 1);
        order.clear(); farToNear(tree.get(), 10, 2, order); assert(order[0].x1 == 1 && order[1].x1 == 2 && order[2].x1 == 3);
        std::vector<Seg> cross = {{-2, 0, 2, 0, 0}, {0, -1, 0, 1, 1}}; auto t2 = build(cross); std::vector<Seg> out; farToNear(t2.get(), 5, 5, out);
        assert(out.size() == 3); double total = 0; for (auto& s : out) total += s.len(); assert(std::fabs(total - 6) < 1e-9); }
    std::mt19937 rng(1996); long fragmentsFirst = 0, fragmentsSmart = 0, pairsChecked = 0;
    for (int scene = 0; scene < 250; ++scene) {                                                                          // ②③ 무작위 장면
        int n = 2 + (int)(rng() % 11); std::vector<Seg> segs; for (int i = 0; i < n; ++i) { Seg s{(double)(rng() % 21) - 10, (double)(rng() % 21) - 10, (double)(rng() % 21) - 10, (double)(rng() % 21) - 10, i}; if (s.len() < 1e-9) s.x2 += 1; segs.push_back(s); }
        double totalLen = 0; for (auto& s : segs) totalLen += s.len();
        for (int smart = 0; smart < 2; ++smart) { auto tree = build(segs, smart == 1); std::vector<Seg> frags; farToNear(tree.get(), 1000, 1000, frags); (smart ? fragmentsSmart : fragmentsFirst) += (long)frags.size();
            double fragLen = 0; std::vector<double> perOrigin(n, 0.0); for (auto& f : frags) { fragLen += f.len(); perOrigin[f.origin] += f.len(); assert(onSegment(segs[f.origin], f.x1, f.y1) && onSegment(segs[f.origin], f.x2, f.y2)); }
            assert(std::fabs(fragLen - totalLen) < 1e-6); for (int i = 0; i < n; ++i) assert(std::fabs(perOrigin[i] - segs[i].len()) < 1e-6);   // 길이 보존, 각 원래 선분은 자기 조각들로 정확히 덮임
            if (smart == 1) continue;
            for (int e = 0; e < 40; ++e) { double ex = (double)(rng() % 4001) / 100 - 20 + 0.013, ey = (double)(rng() % 4001) / 100 - 20 + 0.007; std::vector<Seg> order; farToNear(tree.get(), ex, ey, order); assert(order.size() == frags.size());
                for (size_t a = 0; a < order.size(); ++a) for (size_t b = 0; b < order.size(); ++b) { if (a == b) continue; if (occludes(order[a], order[b], ex, ey)) { ++pairsChecked; assert(a > b); } }   // 가리는 쪽이 나중에
                std::vector<Seg> near; nearToFar(tree.get(), ex, ey, near); assert(near.size() == order.size()); } } }
    assert(pairsChecked > 10000 && fragmentsSmart <= fragmentsFirst);                                                   // ④ 똑똑한 선택은 조각을 더 만들지 않는다
    std::cout << "BSPTree: the painter's order was verified pair by pair on " << pairsChecked << " occlusion constraints from 250 random scenes; segment lengths were preserved by every split; first-segment splitters made " << fragmentsFirst << " fragments versus " << fragmentsSmart << " for the min-cut heuristic" << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n²) 최악 (좋은 분할선을 고르면 O(n log n) 기대), 순회 O(조각 수)
// Space Complexity: O(조각 수) (분할로 최대 O(n²))
```

# Part 12. 구간 연산
## RangeQuery()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 정적 배열의 구간 질의: 값이 바뀌지 않는다면 전처리로 질의를 O(1)에 답할 수 있다.
//  구간 합: 누적합 P[r] - P[l]   구간 최솟값(RMQ): 희소 표(sparse table) — 길이 2^k 구간의 최솟값을 모두 저장하고, 질의 [l, r] 은 겹치는 두 구간으로 덮는다 (min 은 겹쳐도 상관없다)
struct Static {
    std::vector<long> prefix; std::vector<std::vector<int>> sp; std::vector<int> lg;
    explicit Static(const std::vector<int>& a) : prefix(a.size() + 1, 0), lg(a.size() + 1, 0) {
        for (size_t i = 0; i < a.size(); i++) prefix[i + 1] = prefix[i] + a[i];
        for (size_t i = 2; i <= a.size(); i++) lg[i] = lg[i / 2] + 1;
        sp.assign(lg[a.size()] + 1, std::vector<int>(a.size())); sp[0] = a;
        for (int k = 1; k <= lg[a.size()]; k++) for (size_t i = 0; i + (1u << k) <= a.size(); i++) sp[k][i] = std::min(sp[k - 1][i], sp[k - 1][i + (1 << (k - 1))]);
    }
    long sum(int l, int r) const { return prefix[r + 1] - prefix[l]; }                    // [l, r]
    int rmq(int l, int r) const { int k = lg[r - l + 1]; return std::min(sp[k][l], sp[k][r - (1 << k) + 1]); }
};

int main() {
    std::mt19937 rng(25); std::vector<int> a(5000); for (auto& x : a) x = (int)(rng() % 20001) - 10000;
    Static s(a);
    for (int t = 0; t < 20000; t++) {
        int l = rng() % a.size(), r = rng() % a.size(); if (l > r) std::swap(l, r);
        assert(s.sum(l, r) == std::accumulate(a.begin() + l, a.begin() + r + 1, 0L));
        assert(s.rmq(l, r) == *std::min_element(a.begin() + l, a.begin() + r + 1));
    }
    std::cout << "RangeQuery: O(1) sum and RMQ verified on 20000 random queries." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(n log n), 질의 O(1)
// Space Complexity: O(n log n)
```
## LazyPropagation()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 지연 전파(lazy propagation): 구간 갱신(예: [l, r] 에 v 더하기)을 모든 원소에 적용하지 않고, 구간을 덮는 O(log n) 개 노드에 "보류 중인 갱신(lazy)" 으로만 표시해 둔다.
// 그 노드의 자식을 실제로 방문할 때 아래로 밀어 내린다(push down).  구간 갱신 + 구간 합을 둘 다 O(log n)
class SegTree {
    int n; std::vector<long> sum, lazy;
    void apply(int node, int len, long v) { sum[node] += v * len; lazy[node] += v; }
    void push(int node, int l, int r) {
        if (!lazy[node]) return;
        int m = (l + r) / 2; apply(2 * node, m - l + 1, lazy[node]); apply(2 * node + 1, r - m, lazy[node]); lazy[node] = 0;
    }
    void add(int node, int l, int r, int a, int b, long v) {
        if (b < l || r < a) return;
        if (a <= l && r <= b) { apply(node, r - l + 1, v); return; }
        push(node, l, r); int m = (l + r) / 2;
        add(2 * node, l, m, a, b, v); add(2 * node + 1, m + 1, r, a, b, v);
        sum[node] = sum[2 * node] + sum[2 * node + 1];
    }
    long query(int node, int l, int r, int a, int b) {
        if (b < l || r < a) return 0;
        if (a <= l && r <= b) return sum[node];
        push(node, l, r); int m = (l + r) / 2;
        return query(2 * node, l, m, a, b) + query(2 * node + 1, m + 1, r, a, b);
    }
public:
    explicit SegTree(int size) : n(size), sum(4 * size, 0), lazy(4 * size, 0) {}
    void rangeAdd(int a, int b, long v) { add(1, 0, n - 1, a, b, v); }
    long rangeSum(int a, int b) { return query(1, 0, n - 1, a, b); }
};

int main() {
    const int N = 2000; SegTree st(N); std::vector<long> brute(N, 0); std::mt19937 rng(26);
    for (int op = 0; op < 20000; op++) {
        int l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        if (rng() % 2) { long v = (long)(rng() % 201) - 100; st.rangeAdd(l, r, v); for (int i = l; i <= r; i++) brute[i] += v; }
        else { long s = 0; for (int i = l; i <= r; i++) s += brute[i]; assert(st.rangeSum(l, r) == s); }
    }
    std::cout << "LazyPropagation: range add / range sum match brute force over 20000 operations." << std::endl;
    return 0;
}
// Time Complexity: 갱신·질의 O(log n)
// Space Complexity: O(n)
```
## RangeUpdate()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 펜윅 트리(BIT)로 "구간 더하기 + 구간 합" 하기: 차분 배열 d[i] = a[i] - a[i-1] 을 두면 구간 더하기는 d 의 두 점 갱신이다.
// prefix(i) = Σ_{j<=i} a[j] = (i+1)·Σ d[j] - Σ j·d[j]  이므로 BIT 두 개(d 용, j·d 용)로 충분하다.  코드가 짧고 상수가 작아 세그먼트 트리보다 빠르다
class RangeBIT {
    int n; std::vector<long> b1, b2;
    void upd(std::vector<long>& b, int i, long v) { for (i++; i <= n; i += i & -i) b[i] += v; }
    long qry(const std::vector<long>& b, int i) const { long s = 0; for (i++; i > 0; i -= i & -i) s += b[i]; return s; }
    long prefix(int i) const { return i < 0 ? 0 : qry(b1, i) * (i + 1) - qry(b2, i); }
public:
    explicit RangeBIT(int size) : n(size), b1(size + 2, 0), b2(size + 2, 0) {}
    void rangeAdd(int l, int r, long v) {
        upd(b1, l, v); upd(b1, r + 1, -v);
        upd(b2, l, v * l); upd(b2, r + 1, -v * (r + 1));
    }
    long rangeSum(int l, int r) const { return prefix(r) - prefix(l - 1); }
};

int main() {
    const int N = 3000; RangeBIT bit(N); std::vector<long> brute(N, 0); std::mt19937 rng(27);
    for (int op = 0; op < 30000; op++) {
        int l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        if (rng() % 2) { long v = (long)(rng() % 2001) - 1000; bit.rangeAdd(l, r, v); for (int i = l; i <= r; i++) brute[i] += v; }
        else { long s = 0; for (int i = l; i <= r; i++) s += brute[i]; assert(bit.rangeSum(l, r) == s); }
    }
    std::cout << "RangeUpdate: BIT range add / range sum verified over 30000 operations." << std::endl;
    return 0;
}
// Time Complexity: O(log n)
// Space Complexity: O(n)
```

## SqrtDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 제곱근 분할: 배열을 크기 B ≈ √n 의 블록으로 나눈다.  구간 연산은 "완전히 덮이는 블록은 블록 단위로(O(1)), 양 끝의 부분 블록은 원소 단위로(O(B))" 처리해 O(√n).
// 세그먼트 트리(O(log n))보다 느리지만 구현이 단순하고, 블록 안에서 임의의 보조 구조(정렬된 사본, 해시, 비트셋)를 쓸 수 있어 더 이상한 질의에도 적용된다
class Sqrt {
    int n, B; std::vector<long> a, blockSum, blockAdd;
public:
    explicit Sqrt(int size) : n(size), B(std::max(1, (int)std::sqrt((double)size))), a(size, 0), blockSum((size + B - 1) / B, 0), blockAdd((size + B - 1) / B, 0) {}
    void rangeAdd(int l, int r, long v) {
        int bl = l / B, br = r / B;
        if (bl == br) { for (int i = l; i <= r; i++) { a[i] += v; blockSum[bl] += v; } return; }
        for (int i = l; i < (bl + 1) * B; i++) { a[i] += v; blockSum[bl] += v; }          // 왼쪽 부분 블록
        for (int b = bl + 1; b < br; b++) { blockAdd[b] += v; blockSum[b] += v * B; }       // 완전히 덮인 블록: 한 번에
        for (int i = br * B; i <= r; i++) { a[i] += v; blockSum[br] += v; }                // 오른쪽 부분 블록
    }
    long rangeSum(int l, int r) const {
        long s = 0; int bl = l / B, br = r / B;
        if (bl == br) { for (int i = l; i <= r; i++) s += a[i] + blockAdd[bl]; return s; }
        for (int i = l; i < (bl + 1) * B; i++) s += a[i] + blockAdd[bl];
        for (int b = bl + 1; b < br; b++) s += blockSum[b];
        for (int i = br * B; i <= r; i++) s += a[i] + blockAdd[br];
        return s;
    }
};

int main() {
    const int N = 2500; Sqrt sq(N); std::vector<long> brute(N, 0); std::mt19937 rng(28);
    for (int op = 0; op < 20000; op++) {
        int l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        if (rng() % 2) { long v = (long)(rng() % 201) - 100; sq.rangeAdd(l, r, v); for (int i = l; i <= r; i++) brute[i] += v; }
        else { long s = 0; for (int i = l; i <= r; i++) s += brute[i]; assert(sq.rangeSum(l, r) == s); }
    }
    std::cout << "SqrtDecomposition: block size " << (int)std::sqrt((double)N) << ", 20000 operations verified." << std::endl;
    return 0;
}
// Time Complexity: 갱신·질의 O(√n)
// Space Complexity: O(n)
```
## MergeSortTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 머지 소트 트리: 세그먼트 트리의 각 노드가 자기 구간의 "정렬된 사본" 을 가진다 (머지 소트의 병합 과정을 그대로 저장).
// 구간 [l, r] 에서 x 이하인 원소의 개수 = 구간을 덮는 O(log n) 개 노드에서 이진 탐색(upper_bound)한 결과의 합 -> O(log² n).  갱신이 없는 정적 배열의 "순위" 질의에 쓴다
class MergeSortTree {
    int n; std::vector<std::vector<int>> t;
    void build(int node, int l, int r, const std::vector<int>& a) {
        if (l == r) { t[node] = {a[l]}; return; }
        int m = (l + r) / 2; build(2 * node, l, m, a); build(2 * node + 1, m + 1, r, a);
        t[node].resize(t[2 * node].size() + t[2 * node + 1].size());
        std::merge(t[2 * node].begin(), t[2 * node].end(), t[2 * node + 1].begin(), t[2 * node + 1].end(), t[node].begin());     // 정렬된 두 사본을 병합
    }
    int count(int node, int l, int r, int a, int b, int x) const {
        if (b < l || r < a) return 0;
        if (a <= l && r <= b) return std::upper_bound(t[node].begin(), t[node].end(), x) - t[node].begin();
        int m = (l + r) / 2; return count(2 * node, l, m, a, b, x) + count(2 * node + 1, m + 1, r, a, b, x);
    }
public:
    explicit MergeSortTree(const std::vector<int>& a) : n(a.size()), t(4 * a.size()) { build(1, 0, n - 1, a); }
    int countLE(int l, int r, int x) const { return count(1, 0, n - 1, l, r, x); }
};

int main() {
    std::mt19937 rng(29); std::vector<int> a(3000); for (auto& v : a) v = rng() % 1000;
    MergeSortTree mt(a);
    for (int q = 0; q < 5000; q++) {
        int l = rng() % a.size(), r = rng() % a.size(); if (l > r) std::swap(l, r); int x = rng() % 1000;
        assert(mt.countLE(l, r, x) == (int)std::count_if(a.begin() + l, a.begin() + r + 1, [&](int v) { return v <= x; }));
    }
    std::cout << "MergeSortTree: count-less-or-equal in a range verified on 5000 queries." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n log n), 질의 O(log² n)
// Space Complexity: O(n log n)
```
# Part 13. 고급 트리
## BTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// B-트리: 한 노드에 여러 키를 담는 균형 다진 트리.  최소 차수 t 이면 루트 외 모든 노드는 키를 t-1 ~ 2t-1 개 가지며 모든 잎의 깊이가 같다.
// 노드 하나를 디스크 블록 하나에 맞추면 높이가 log_t(n) 이라 디스크 접근이 극히 적다 (데이터베이스·파일 시스템의 기본 구조).
// 삽입은 "내려가면서 꽉 찬 노드를 미리 쪼개는" 방식이라 위로 되돌아올 필요가 없다 (단일 패스)
const int T = 3;                                                     // 최소 차수: 키 2..5 개
struct Node {
    std::vector<int> keys; std::vector<Node*> kids; bool leaf = true;
    bool full() const { return (int)keys.size() == 2 * T - 1; }
};
struct BTree {
    Node* root = new Node();
    static void destroy(Node* x) { for (Node* c : x->kids) destroy(c); delete x; }
    ~BTree() { destroy(root); }
    void splitChild(Node* x, int i) {                                // x->kids[i] 가 꽉 찼을 때 가운데 키를 x 로 올리고 둘로 쪼갠다
        Node* y = x->kids[i]; Node* z = new Node(); z->leaf = y->leaf;
        int mid = y->keys[T - 1];
        z->keys.assign(y->keys.begin() + T, y->keys.end());
        if (!y->leaf) { z->kids.assign(y->kids.begin() + T, y->kids.end()); y->kids.resize(T); }
        y->keys.resize(T - 1);
        x->keys.insert(x->keys.begin() + i, mid);
        x->kids.insert(x->kids.begin() + i + 1, z);
    }
    void insertNonFull(Node* x, int k) {
        int i = std::upper_bound(x->keys.begin(), x->keys.end(), k) - x->keys.begin();
        if (x->leaf) { x->keys.insert(x->keys.begin() + i, k); return; }
        if (x->kids[i]->full()) { splitChild(x, i); if (k > x->keys[i]) i++; }
        insertNonFull(x->kids[i], k);
    }
    void insert(int k) {
        if (root->full()) { Node* s = new Node(); s->leaf = false; s->kids.push_back(root); root = s; splitChild(s, 0); }   // 루트가 쪼개질 때만 높이 증가
        insertNonFull(root, k);
    }
    bool search(const Node* x, int k) const {
        int i = std::lower_bound(x->keys.begin(), x->keys.end(), k) - x->keys.begin();
        if (i < (int)x->keys.size() && x->keys[i] == k) return true;
        return !x->leaf && search(x->kids[i], k);
    }
    void inorder(const Node* x, std::vector<int>& out) const {
        for (size_t i = 0; i < x->keys.size(); i++) { if (!x->leaf) inorder(x->kids[i], out); out.push_back(x->keys[i]); }
        if (!x->leaf) inorder(x->kids.back(), out);
    }
    int height(const Node* x) const { return x->leaf ? 1 : 1 + height(x->kids[0]); }
    bool valid(const Node* x, bool isRoot, int depth, int leafDepth) const {   // 최소/최대 키 수와 잎의 깊이 검사
        int n = x->keys.size();
        if (n > 2 * T - 1 || (!isRoot && n < T - 1)) return false;
        if (x->leaf) return depth == leafDepth;
        if ((int)x->kids.size() != n + 1) return false;
        for (auto* c : x->kids) if (!valid(c, false, depth + 1, leafDepth)) return false;
        return true;
    }
};

int main() {
    BTree t; std::mt19937 rng(17);
    const int n = 5000;
    std::vector<int> keys(n); for (int i = 0; i < n; i++) keys[i] = i * 3; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) t.insert(k);
    std::vector<int> out; t.inorder(t.root, out);
    assert((int)out.size() == n && std::is_sorted(out.begin(), out.end()));    // 중위 순회 = 정렬된 키
    for (int i = 0; i < n; i++) { assert(t.search(t.root, i * 3)); assert(!t.search(t.root, i * 3 + 1)); }
    int h = t.height(t.root);
    assert(t.valid(t.root, true, 1, h));                                       // 모든 잎의 깊이가 같고 키 수 제약을 지킨다
    assert(h <= 1 + std::log((n + 1) / 2.0) / std::log((double)T));            // 높이 <= 1 + log_t((n+1)/2)
    std::cout << "BTree t=" << T << ": " << n << " keys, height " << h << " (binary tree would need ~" << (int)std::log2(n) + 1 << ")" << std::endl;
    return 0;
}
// Time Complexity: 검색·삽입 O(t · log_t N), 디스크 접근 O(log_t N)
// Space Complexity: O(N)
```
## BPlusTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// B+ 트리: B-트리의 변형으로 (1) 모든 키-값은 잎에만 저장하고 내부 노드는 길 안내용 키만 갖는다 (2) 잎들을 연결 리스트로 이어 둔다.
// 내부 노드가 작아져 분기 계수가 커지고(높이가 낮고), 범위 질의는 첫 잎을 찾은 뒤 연결 리스트를 따라가기만 하면 된다.  거의 모든 데이터베이스 인덱스와 파일 시스템(NTFS, ext4 의 htree)이 쓴다
const int M = 4;                                              // 노드당 최대 키 수 (실제로는 디스크 블록 크기에 맞춰 수백)
struct Node { bool leaf; std::vector<int> keys; std::vector<Node*> kids; Node* next = nullptr; explicit Node(bool l) : leaf(l) {} };

bool insertRec(Node* n, int k, int& up, Node*& right) {      // 분할이 일어나면 true: up = 위로 올릴 키, right = 새 오른쪽 형제
    if (n->leaf) {
        auto it = std::lower_bound(n->keys.begin(), n->keys.end(), k);
        if (it != n->keys.end() && *it == k) return false;
        n->keys.insert(it, k);
        if ((int)n->keys.size() <= M) return false;
        int mid = n->keys.size() / 2; right = new Node(true);
        right->keys.assign(n->keys.begin() + mid, n->keys.end()); n->keys.resize(mid);
        right->next = n->next; n->next = right;               // 잎 연결 리스트 유지
        up = right->keys[0];                                   // 잎 분할: 오른쪽 첫 키를 "복사" 해서 올린다 (잎에도 남는다)
        return true;
    }
    int idx = std::upper_bound(n->keys.begin(), n->keys.end(), k) - n->keys.begin(); int u; Node* r;
    if (!insertRec(n->kids[idx], k, u, r)) return false;
    n->keys.insert(n->keys.begin() + idx, u); n->kids.insert(n->kids.begin() + idx + 1, r);
    if ((int)n->keys.size() <= M) return false;
    int mid = n->keys.size() / 2; right = new Node(false);
    up = n->keys[mid];                                         // 내부 노드 분할: 가운데 키는 위로 "이동"
    right->keys.assign(n->keys.begin() + mid + 1, n->keys.end()); right->kids.assign(n->kids.begin() + mid + 1, n->kids.end());
    n->keys.resize(mid); n->kids.resize(mid + 1);
    return true;
}
struct BPlus {
    Node* root = new Node(true);
    static void destroy(Node* n) { if (!n->leaf) for (Node* c : n->kids) destroy(c); delete n; }
    ~BPlus() { destroy(root); }
    void insert(int k) { int u; Node* r; if (insertRec(root, k, u, r)) { Node* nr = new Node(false); nr->keys = {u}; nr->kids = {root, r}; root = nr; } }
    Node* leafFor(int k) const { Node* n = root; while (!n->leaf) n = n->kids[std::upper_bound(n->keys.begin(), n->keys.end(), k) - n->keys.begin()]; return n; }
    bool contains(int k) const { Node* l = leafFor(k); return std::binary_search(l->keys.begin(), l->keys.end(), k); }
    std::vector<int> range(int lo, int hi) const {            // [lo, hi]: 첫 잎을 찾은 뒤 연결 리스트만 따라간다
        std::vector<int> out;
        for (Node* l = leafFor(lo); l; l = l->next)
            for (int k : l->keys) { if (k > hi) return out; if (k >= lo) out.push_back(k); }
        return out;
    }
    int depthOfLeaves(Node* n, int d, bool& same, int& first) const {
        if (n->leaf) { if (first < 0) first = d; else if (first != d) same = false; return d; }
        for (Node* c : n->kids) depthOfLeaves(c, d + 1, same, first); return d;
    }
};

int main() {
    std::mt19937 rng(30); BPlus t; std::set<int> truth;
    for (int i = 0; i < 5000; i++) { int k = rng() % 100000; t.insert(k); truth.insert(k); }
    for (int k = 0; k < 100000; k += 13) assert(t.contains(k) == (truth.count(k) > 0));
    for (int q = 0; q < 200; q++) {
        int lo = rng() % 100000, hi = lo + rng() % 3000;
        std::vector<int> expect(truth.lower_bound(lo), truth.upper_bound(hi));
        assert(t.range(lo, hi) == expect);                     // 범위 질의 == 정렬된 집합의 구간
    }
    bool same = true; int first = -1; t.depthOfLeaves(t.root, 0, same, first);
    assert(same);                                               // 모든 잎의 깊이가 같다 (균형)
    int total = 0; for (Node* l = t.leafFor(-1); l; l = l->next) total += l->keys.size();
    assert(total == (int)truth.size());                         // 잎 연결 리스트가 모든 키를 정렬된 순서로 담고 있다
    std::cout << "BPlusTree: " << truth.size() << " keys, leaf depth " << first << ", range scans verified." << std::endl;
    return 0;
}
// Time Complexity: 검색·삽입 O(log_M N), 범위 질의 O(log_M N + k)
// Space Complexity: O(N)
```
## SplayTree()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 스플레이 트리: 접근한 노드를 회전(zig, zig-zig, zig-zag)으로 루트까지 끌어올리는 자기 조정 BST.  균형 정보(높이·색)를 저장하지 않지만 모든 연산이 분할상환 O(log n).
// 최근에 쓴 키가 루트 근처에 모이므로 접근에 지역성이 있으면(작업 집합이 작으면) 균형 트리보다 빠르다.  캐시·메모리 할당기·가비지 컬렉터에 쓰인다
struct Node { int key; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
Node* rotR(Node* x) { Node* y = x->l; x->l = y->r; y->r = x; return y; }
Node* rotL(Node* x) { Node* y = x->r; x->r = y->l; y->l = x; return y; }
Node* splay(Node* root, int key) {                                  // key 가 있으면 루트로, 없으면 경로의 마지막 노드를 루트로
    if (!root || root->key == key) return root;
    if (key < root->key) {
        if (!root->l) return root;
        if (key < root->l->key) { root->l->l = splay(root->l->l, key); root = rotR(root); }                  // zig-zig
        else if (key > root->l->key) { root->l->r = splay(root->l->r, key); if (root->l->r) root->l = rotL(root->l); }   // zig-zag
        return root->l ? rotR(root) : root;
    }
    if (!root->r) return root;
    if (key > root->r->key) { root->r->r = splay(root->r->r, key); root = rotL(root); }
    else if (key < root->r->key) { root->r->l = splay(root->r->l, key); if (root->r->l) root->r = rotR(root->r); }
    return root->r ? rotL(root) : root;
}
Node* insert(Node* root, int k) {
    if (!root) return new Node(k);
    root = splay(root, k); if (root->key == k) return root;
    Node* n = new Node(k);
    if (k < root->key) { n->r = root; n->l = root->l; root->l = nullptr; } else { n->l = root; n->r = root->r; root->r = nullptr; }
    return n;
}
Node* erase(Node* root, int k) {
    if (!root) return nullptr;
    root = splay(root, k); if (root->key != k) return root;
    Node* dead = root;
    if (!root->l) { Node* r = root->r; delete dead; return r; }
    Node* nr = splay(root->l, k); nr->r = root->r; delete dead; return nr;      // 왼쪽 서브트리의 최댓값을 루트로 올리고 오른쪽을 붙인다
}
void destroy(Node* n) { std::vector<Node*> st; if (n) st.push_back(n); while (!st.empty()) { Node* c = st.back(); st.pop_back(); if (c->l) st.push_back(c->l); if (c->r) st.push_back(c->r); delete c; } }
int depthOf(Node* n, int k) { int d = 0; while (n && n->key != k) { n = k < n->key ? n->l : n->r; d++; } return n ? d : -1; }
bool isBST(Node* n, long lo, long hi) { return !n || (n->key > lo && n->key < hi && isBST(n->l, lo, n->key) && isBST(n->r, n->key, hi)); }

int main() {
    Node* root = nullptr; std::set<int> truth; std::mt19937 rng(31);
    for (int i = 0; i < 3000; i++) { int k = rng() % 1000; if (rng() % 3) { root = insert(root, k); truth.insert(k); } else { root = erase(root, k); truth.erase(k); } }
    assert(isBST(root, -1, 1 << 30));
    for (int k = 0; k < 1000; k++) { root = splay(root, k); bool present = root && root->key == k; assert(present == (truth.count(k) > 0)); }   // 접근하면 루트가 된다
    // 지역성: 키 5개만 반복 접근하면 평균 깊이가 아주 얕다 (균형 트리는 항상 log n)
    Node* big = nullptr; for (int k = 0; k < 10000; k++) big = insert(big, k);
    long steps = 0; int hot[5] = {17, 4000, 123, 9000, 555};
    for (int rep = 0; rep < 2000; rep++) for (int h : hot) { steps += depthOf(big, h); big = splay(big, h); assert(big->key == h); }
    assert(double(steps) / (2000 * 5) < 6.0);                                  // 평균 깊이 < 6  (log2(10000) ≈ 13)
    std::cout << "SplayTree: average depth of hot keys = " << double(steps) / 10000 << " (balanced tree: ~13)" << std::endl;
    destroy(root); destroy(big);
    return 0;
}
// Time Complexity: 분할상환 O(log N), 작업 집합 크기 w 에서 O(log w)
// Space Complexity: O(N)
```
## Treap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 트립(Treap = Tree + Heap): 키에 대해서는 BST, 무작위 우선순위에 대해서는 힙인 트리.  우선순위가 무작위이므로 기대 높이가 O(log n) — 키를 정렬된 순서로 넣어도 균형이 맞는다.
// split(키 기준 분할)과 merge(두 트립 합치기) 두 연산만으로 삽입·삭제·구간 연산이 모두 만들어진다.  코드가 짧고 병합/분할이 필요한 문제(Rope, 순서 통계)에 편하다
std::mt19937 rng(32);
struct Node { int key, pri; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k), pri(rng()) {} };
void split(Node* t, int key, Node*& a, Node*& b) {                          // a: 키 < key, b: 키 >= key
    if (!t) { a = b = nullptr; return; }
    if (t->key < key) { a = t; split(t->r, key, t->r, b); } else { b = t; split(t->l, key, a, t->l); }
}
Node* merge(Node* a, Node* b) {                                              // a 의 모든 키 < b 의 모든 키
    if (!a || !b) return a ? a : b;
    if (a->pri > b->pri) { a->r = merge(a->r, b); return a; }
    b->l = merge(a, b->l); return b;
}
bool contains(Node* t, int k) { while (t) { if (k == t->key) return true; t = k < t->key ? t->l : t->r; } return false; }
Node* insert(Node* t, int k) { if (contains(t, k)) return t; Node *a, *b; split(t, k, a, b); return merge(merge(a, new Node(k)), b); }
void destroy(Node* t) { if (!t) return; destroy(t->l); destroy(t->r); delete t; }
Node* erase(Node* t, int k) { Node *a, *b, *c, *d; split(t, k, a, b); split(b, k + 1, c, d); destroy(c); return merge(a, d); }
int height(Node* t) { return t ? 1 + std::max(height(t->l), height(t->r)) : 0; }
bool valid(Node* t, long lo, long hi) { return !t || (t->key > lo && t->key < hi && (!t->l || t->l->pri <= t->pri) && (!t->r || t->r->pri <= t->pri) && valid(t->l, lo, t->key) && valid(t->r, t->key, hi)); }

int main() {
    Node* t = nullptr; std::set<int> truth;
    for (int k = 0; k < 10000; k++) { t = insert(t, k); truth.insert(k); }          // 정렬된 입력도 균형을 유지한다 (일반 BST 라면 높이 10000)
    assert(height(t) <= 6 * std::log2(10000));
    for (int i = 0; i < 4000; i++) { int k = rng() % 10000; t = erase(t, k); truth.erase(k); }
    assert(valid(t, -1, 1 << 30));                                                 // BST 성질 + 힙 성질
    for (int k = 0; k < 10000; k += 3) assert(contains(t, k) == (truth.count(k) > 0));
    Node *a, *b; split(t, 5000, a, b);                                             // 분할: 5000 미만 / 이상
    std::vector<int> left; for (Node* n = a; n;) { left.push_back(n->key); n = n->r; }
    assert(!left.empty() && left.back() < 5000);
    t = merge(a, b);
    assert(valid(t, -1, 1 << 30));
    std::cout << "Treap: height " << height(t) << " for " << truth.size() << " keys inserted in sorted order." << std::endl;
    destroy(t);
    return 0;
}
// Time Complexity: 기대 O(log N)
// Space Complexity: O(N)
```
## CartesianTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 데카르트 트리: 배열 a 에서 (인덱스에 대해 BST 순서, 값에 대해 힙 순서)를 동시에 만족하는 트리.  중위 순회하면 원래 배열 순서가 나오고, 루트는 최솟값이다.
// 스택을 이용해 O(n) 에 구성한다: 새 원소보다 큰 스택 원소들을 pop 해 새 원소의 왼쪽 자식으로 달고, 새 원소를 스택 맨 위 원소의 오른쪽 자식으로 단다.
// 구간 [l, r] 의 최솟값 = 그 구간에 걸친 가장 높은 노드 -> RMQ 와 LCA 가 서로 환원되는 연결 고리 (트립은 우선순위가 무작위인 데카르트 트리)
struct Node { int idx, val, l = -1, r = -1; };
int build(std::vector<Node>& t, const std::vector<int>& a) {
    std::vector<int> st;
    for (int i = 0; i < (int)a.size(); i++) {
        t[i] = {i, a[i]}; int last = -1;
        while (!st.empty() && t[st.back()].val > a[i]) { last = st.back(); st.pop_back(); }
        t[i].l = last;
        if (!st.empty()) t[st.back()].r = i;
        st.push_back(i);
    }
    return st.front();                                              // 스택 바닥 = 최솟값 = 루트
}
void inorder(const std::vector<Node>& t, int u, std::vector<int>& out) { if (u < 0) return; inorder(t, t[u].l, out); out.push_back(t[u].val); inorder(t, t[u].r, out); }
bool heapOrdered(const std::vector<Node>& t, int u) { return u < 0 || ((t[u].l < 0 || t[t[u].l].val >= t[u].val) && (t[u].r < 0 || t[t[u].r].val >= t[u].val) && heapOrdered(t, t[u].l) && heapOrdered(t, t[u].r)); }
int rmqIndex(const std::vector<Node>& t, int u, int l, int r) {         // 루트에서 내려가며 구간 [l, r] 에 처음 걸치는 노드가 최솟값의 위치
    for (;;) { if (t[u].idx < l) u = t[u].r; else if (t[u].idx > r) u = t[u].l; else return t[u].idx; }
}

int main() {
    std::mt19937 rng(33); std::vector<int> a(3000); for (auto& x : a) x = rng() % 100000;
    std::vector<Node> t(a.size()); int root = build(t, a);
    assert(a[root] == *std::min_element(a.begin(), a.end()));
    std::vector<int> in; inorder(t, root, in);
    assert(in == a);                                                  // 중위 순회 == 원래 배열
    assert(heapOrdered(t, root));                                     // 부모 <= 자식
    for (int q = 0; q < 5000; q++) {
        int l = rng() % a.size(), r = rng() % a.size(); if (l > r) std::swap(l, r);
        int idx = rmqIndex(t, root, l, r);
        assert(idx >= l && idx <= r && a[idx] == *std::min_element(a.begin() + l, a.begin() + r + 1));
    }
    std::cout << "CartesianTree: built in O(n); inorder = array, range minimum by descent." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n), RMQ 는 트리 높이에 비례 (LCA 전처리 후 O(1))
// Space Complexity: O(n)
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

// 희생양 트리(scapegoat tree): 균형 정보를 노드에 저장하지 않는 BST.  삽입 후 깊이가 log_{1/α}(n) 을 넘으면, 경로를 거슬러 올라가며 "한쪽 서브트리가 전체의 α 배를 넘는" 첫 조상(희생양)을 찾아
// 그 서브트리를 통째로 완전 균형으로 다시 짓는다.  삭제는 n 이 최대치의 α 배 아래로 떨어지면 전체를 재구성.  모든 연산 분할상환 O(log n), 높이 ≤ log_{1/α}(n) + 1.
//  ① 무작위 삽입(50%)·삭제(30%)·조회(20%) 30 만 번을 std::set 과 대조하고 주기적으로 BST 순서·크기·높이 불변식(높이 ≤ log_{1/α}(max(n, 직전 최대치)) + 1)  ② 정렬된 5 000 개·역정렬: 높이가 n 이 아니라 로그 수준(깊이 한도 위반 시 희생양 재구성이 일어난 횟수를 센다)
//  ③ 재구성한 노드 수의 합이 연산 수 × log n 의 상수배 이내(분할상환 확인)  ④ 재구성 직후 서브트리는 *완전 균형*(높이 = ⌈log2(크기+1)⌉)  ⑤ α 를 0.55 / 0.7 / 0.9 로 바꾸면 높이 한도는 커지고 재구성은 줄어든다(같은 입력)
struct Node { int key; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
int size(const Node* n) { return n ? 1 + size(n->l) + size(n->r) : 0; }
void flatten(Node* n, std::vector<Node*>& out) { if (!n) return; flatten(n->l, out); out.push_back(n); flatten(n->r, out); }
Node* rebuild(std::vector<Node*>& v, int lo, int hi) {                       // [lo, hi) 를 완전 균형 BST 로
    if (lo >= hi) return nullptr;
    int mid = (lo + hi) / 2; Node* n = v[mid];
    n->l = rebuild(v, lo, mid); n->r = rebuild(v, mid + 1, hi); return n;
}
int height(const Node* x) { return x ? 1 + std::max(height(x->l), height(x->r)) : 0; }
struct Tree {
    double alpha; Node* root = nullptr; int n = 0, maxN = 0; long rebuilds = 0, rebuiltNodes = 0, globalRebuilds = 0; bool lastWasPerfect = true;
    explicit Tree(double a = 0.7) : alpha(a) {}
    ~Tree() { destroy(root); }
    static void destroy(Node* x) { if (!x) return; destroy(x->l); destroy(x->r); delete x; }
    double depthLimit(int count) const { return std::floor(std::log((double)std::max(count, 1)) / std::log(1 / alpha)); }
    bool insert(int k) {
        std::vector<Node*> path; Node* cur = root;
        while (cur) { if (cur->key == k) return false; path.push_back(cur); cur = k < cur->key ? cur->l : cur->r; }
        Node* nn = new Node(k);
        if (path.empty()) root = nn; else if (k < path.back()->key) path.back()->l = nn; else path.back()->r = nn;
        n++; maxN = std::max(maxN, n); path.push_back(nn);
        if ((int)path.size() - 1 > depthLimit(n)) {                                           // 너무 깊다: 희생양을 찾는다
            int childSize = 1;
            for (int i = (int)path.size() - 2; i >= 0; i--) {
                int total = 1 + childSize + size(sibling(path[i], path[i + 1]));
                if (childSize > alpha * total) { rebuildAt(path, i); break; }               // 균형이 깨진 첫 조상
                childSize = total;
            }
        }
        return true;
    }
    bool erase(int k) {
        Node* parent = nullptr; Node* cur = root;
        while (cur && cur->key != k) { parent = cur; cur = k < cur->key ? cur->l : cur->r; }
        if (!cur) return false;
        if (cur->l && cur->r) { Node* sp = cur; Node* s = cur->r; while (s->l) { sp = s; s = s->l; } cur->key = s->key; parent = sp; cur = s; }   // 후속자의 값을 가져오고 후속자를 떼어 낸다
        Node* child = cur->l ? cur->l : cur->r;
        if (!parent) root = child; else if (parent->l == cur) parent->l = child; else parent->r = child;
        delete cur; n--;
        if (n < alpha * maxN) { std::vector<Node*> v; flatten(root, v); root = rebuild(v, 0, (int)v.size()); maxN = n; ++globalRebuilds; rebuiltNodes += n; }   // 너무 줄었다: 전체 재구성
        return true;
    }
    static Node* sibling(Node* parent, Node* child) { return parent->l == child ? parent->r : parent->l; }
    void rebuildAt(std::vector<Node*>& path, int i) {
        std::vector<Node*> v; flatten(path[i], v); Node* sub = rebuild(v, 0, (int)v.size()); ++rebuilds; rebuiltNodes += (long)v.size();
        lastWasPerfect = height(sub) == (int)std::ceil(std::log2((double)v.size() + 1) - 1e-12);
        if (i == 0) root = sub; else if (path[i - 1]->l == path[i]) path[i - 1]->l = sub; else path[i - 1]->r = sub;
    }
    bool contains(int k) const { Node* c = root; while (c) { if (c->key == k) return true; c = k < c->key ? c->l : c->r; } return false; }
    int check(const Node* x, long long lo, long long hi, int& count) const { if (!x) return 0; assert(x->key > lo && x->key < hi); ++count; return 1 + std::max(check(x->l, lo, x->key, count), check(x->r, x->key, hi, count)); }
    int validate() const { int count = 0; int h = check(root, -(1LL << 40), 1LL << 40, count); assert(count == n); return h; }
};

int main() {
    {   std::mt19937 rng(5); Tree t; std::set<int> model;                                                                // ① 대조
        for (int step = 0; step < 300000; ++step) { int k = (int)(rng() % 20000); int op = (int)(rng() % 10);
            if (op < 5) { bool added = t.insert(k); assert(added == model.insert(k).second); } else if (op < 8) { bool removed = t.erase(k); assert(removed == (model.erase(k) == 1)); } else assert(t.contains(k) == (model.count(k) == 1));
            assert(t.n == (int)model.size());
            if (step % 3000 == 0) { int h = t.validate(); assert(h <= t.depthLimit(std::max(t.n, t.maxN)) + 2); } }
        std::vector<Node*> in; flatten(t.root, in); std::vector<int> keys; for (Node* x : in) keys.push_back(x->key); assert(keys == std::vector<int>(model.begin(), model.end())); }
    for (int mode = 0; mode < 2; ++mode) { Tree t; const int n = 5000; for (int i = 1; i <= n; i++) t.insert(mode == 0 ? i : n + 1 - i);                    // ② 정렬 입력
        int h = t.validate(); assert(h <= t.depthLimit(n) + 2 && t.rebuilds > 0); for (int k = 1; k <= n; k++) assert(t.contains(k)); assert(!t.contains(0) && !t.contains(n + 1)); }
    {   Tree t; const int n = 100000; for (int i = 1; i <= n; i++) t.insert(i); t.validate();                                                          // ③ 분할상환
        assert(t.rebuiltNodes <= 6.0 * n * std::log2((double)n) && t.lastWasPerfect); }                                                        // ④ 재구성 직후는 완전 균형
    {   long rebuilds[3]; int heights[3]; const double alphas[3] = {0.55, 0.7, 0.9};                                                          // ⑤ α 의 영향
        for (int a = 0; a < 3; ++a) { Tree t(alphas[a]); const int n = 20000; for (int i = 1; i <= n; i++) t.insert(i); heights[a] = t.validate(); rebuilds[a] = t.rebuilds; assert(heights[a] <= t.depthLimit(n) + 2); }
        assert(heights[0] < heights[2] && rebuilds[0] > rebuilds[2]); }
    std::cout << "ScapegoatTree: 300000 random operations matched std::set with the depth invariant intact; 100000 sorted inserts stayed within the log bound with amortized rebuild work, and alpha traded height for rebuild frequency" << std::endl;
    return 0;
}
// Time Complexity: 삽입·삭제 분할상환 O(log N), 검색 O(log N)
// Space Complexity: O(N) (노드에 균형 정보 없음)
```

## OrderStatisticTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 순서 통계 트리: BST 의 각 노드에 "자기 서브트리의 크기" 를 덧붙여 순위 질의를 O(log n) 에 한다.
//   select(k): 작은 쪽에서 k 번째 원소  /  rank(x): x 보다 작은 원소의 개수 (= x 의 순위).   중앙값, 백분위수, "k 번째로 작은 수" 에 쓴다.  (여기서는 균형을 트립으로 유지)
std::mt19937 rng(34);
struct Node { int key, pri, sz = 1; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k), pri(rng()) {} };
int sz(Node* n) { return n ? n->sz : 0; }
void upd(Node* n) { n->sz = 1 + sz(n->l) + sz(n->r); }
void split(Node* t, int key, Node*& a, Node*& b) { if (!t) { a = b = nullptr; return; } if (t->key < key) { a = t; split(t->r, key, t->r, b); upd(a); } else { b = t; split(t->l, key, a, t->l); upd(b); } }
Node* merge(Node* a, Node* b) { if (!a || !b) return a ? a : b; if (a->pri > b->pri) { a->r = merge(a->r, b); upd(a); return a; } b->l = merge(a, b->l); upd(b); return b; }
Node* insert(Node* t, int k) { Node *a, *b; split(t, k, a, b); return merge(merge(a, new Node(k)), b); }
void destroy(Node* t) { if (!t) return; destroy(t->l); destroy(t->r); delete t; }
Node* erase(Node* t, int k) { Node *a, *b, *c, *d; split(t, k, a, b); split(b, k + 1, c, d); destroy(c); return merge(a, d); }
int select(Node* t, int k) { for (;;) { int ls = sz(t->l); if (k < ls) t = t->l; else if (k == ls) return t->key; else { k -= ls + 1; t = t->r; } } }      // 0-기반
int rankOf(Node* t, int x) { int r = 0; while (t) { if (x <= t->key) t = t->l; else { r += sz(t->l) + 1; t = t->r; } } return r; }              // x 보다 작은 개수

int main() {
    Node* t = nullptr; std::set<int> truth;
    for (int i = 0; i < 4000; i++) { int k = rng() % 100000; if (truth.insert(k).second) t = insert(t, k); }          // 중복 키는 넣지 않는다 (집합)
    for (int i = 0; i < 1000; i++) { int k = *std::next(truth.begin(), rng() % truth.size()); t = erase(t, k); truth.erase(k); }
    std::vector<int> sorted(truth.begin(), truth.end());
    assert(sz(t) == (int)sorted.size());
    for (int q = 0; q < 2000; q++) {
        int k = rng() % sorted.size(); assert(select(t, k) == sorted[k]);        // k 번째로 작은 값
        int x = rng() % 100000; assert(rankOf(t, x) == (int)(std::lower_bound(sorted.begin(), sorted.end(), x) - sorted.begin()));   // 순위
    }
    int median = select(t, sorted.size() / 2); assert(median == sorted[sorted.size() / 2]);
    std::cout << "OrderStatisticTree: select / rank verified; median of " << sorted.size() << " keys = " << median << std::endl;
    destroy(t);
    return 0;
}
// Time Complexity: select·rank·삽입·삭제 기대 O(log N)
// Space Complexity: O(N) (노드당 크기 필드 하나)
```
## WeightBalancedTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 가중치 균형 트리(BB[α], Adams): 높이 대신 "서브트리 크기" 로 균형을 정의한다 — 어떤 노드든 한쪽 서브트리의 가중치(크기+1)가 다른 쪽의 Δ=3 배를 넘지 않는다.
// 위반되면 회전 한 번 또는 두 번(Γ=2 로 판단)으로 복구.  크기를 이미 저장하므로 순위 질의에 그대로 쓰이고, 함수형 언어의 표준 집합 구현(Haskell Data.Map, OCaml Set)이 쓴다
struct Node { int key, size = 1; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
int sz(Node* n) { return n ? n->size : 0; }
int w(Node* n) { return sz(n) + 1; }
void upd(Node* n) { n->size = 1 + sz(n->l) + sz(n->r); }
Node* rotL(Node* n) { Node* r = n->r; n->r = r->l; r->l = n; upd(n); upd(r); return r; }
Node* rotR(Node* n) { Node* l = n->l; n->l = l->r; l->r = n; upd(n); upd(l); return l; }
Node* balance(Node* n) {
    upd(n);
    if (sz(n->l) + sz(n->r) <= 1) return n;
    if (w(n->r) > 3 * w(n->l)) { if (w(n->r->l) >= 2 * w(n->r->r)) n->r = rotR(n->r); return rotL(n); }     // 오른쪽이 너무 무겁다: 단일 또는 이중 회전
    if (w(n->l) > 3 * w(n->r)) { if (w(n->l->r) >= 2 * w(n->l->l)) n->l = rotL(n->l); return rotR(n); }
    return n;
}
Node* insert(Node* n, int k) { if (!n) return new Node(k); if (k < n->key) n->l = insert(n->l, k); else if (k > n->key) n->r = insert(n->r, k); else return n; return balance(n); }
Node* eraseMin(Node* n, int& minKey) { if (!n->l) { minKey = n->key; Node* r = n->r; delete n; return r; } n->l = eraseMin(n->l, minKey); return balance(n); }
Node* erase(Node* n, int k) {
    if (!n) return nullptr;
    if (k < n->key) n->l = erase(n->l, k); else if (k > n->key) n->r = erase(n->r, k);
    else { if (!n->l) { Node* r = n->r; delete n; return r; } if (!n->r) { Node* l = n->l; delete n; return l; } int m; n->r = eraseMin(n->r, m); n->key = m; }
    return balance(n);
}
bool balanced(Node* n) { return !n || ((sz(n->l) + sz(n->r) <= 1 || (w(n->l) <= 3 * w(n->r) && w(n->r) <= 3 * w(n->l))) && n->size == 1 + sz(n->l) + sz(n->r) && balanced(n->l) && balanced(n->r)); }
int height(Node* n) { return n ? 1 + std::max(height(n->l), height(n->r)) : 0; }
void destroy(Node* n) { if (!n) return; destroy(n->l); destroy(n->r); delete n; }

int main() {
    Node* t = nullptr; std::set<int> truth; std::mt19937 rng(35);
    for (int k = 0; k < 8000; k++) { t = insert(t, k); truth.insert(k); }            // 정렬된 입력
    assert(balanced(t) && height(t) <= 3 * std::log2(8001));
    for (int i = 0; i < 6000; i++) { int k = rng() % 8000; t = erase(t, k); truth.erase(k); if (i % 500 == 0) assert(balanced(t)); }
    assert(balanced(t) && sz(t) == (int)truth.size());
    for (int k = 0; k < 8000; k += 5) { Node* c = t; while (c && c->key != k) c = k < c->key ? c->l : c->r; assert((c != nullptr) == (truth.count(k) > 0)); }
    std::cout << "WeightBalancedTree: size " << sz(t) << ", height " << height(t) << ", every node satisfies weight(left) <= 3*weight(right)." << std::endl;
    destroy(t);
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(N)
```
## ZipTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <utility>
#include <vector>
#include <cassert>

// 집 트리(Zip tree, Tarjan–Levy–Timmel 2019): 스킵 리스트를 이진 트리로 옮긴 구조.  각 노드가 기하분포 랭크(P(rank ≥ r) = 2^-r)를 받고, 랭크에 대한 힙이며
// 랭크가 같으면 키가 작은 쪽이 위다.  삽입 = 새 노드 아래에서 경로를 "풀어 쪼개기(unzip)", 삭제 = 두 자식 서브트리를 "지퍼처럼 합치기(zip)".  회전이 없고 코드가 짧다
std::mt19937 rng(36);
struct Node { int key, rank; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) { int r = 0; while (rng() & 1) r++; rank = r; } };
bool above(const Node* a, const Node* b) { return a->rank > b->rank || (a->rank == b->rank && a->key < b->key); }     // a 가 b 의 부모가 될 수 있는가

std::pair<Node*, Node*> unzip(Node* t, int key) {                       // 키 < key 와 키 > key 로 가르며 경로를 푼다
    if (!t) return {nullptr, nullptr};
    if (t->key < key) { auto p = unzip(t->r, key); t->r = p.first; return {t, p.second}; }
    auto p = unzip(t->l, key); t->l = p.second; return {p.first, t};
}
Node* insert(Node* root, Node* x) {
    if (!root) return x;
    if (above(x, root)) { auto p = unzip(root, x->key); x->l = p.first; x->r = p.second; return x; }   // x 가 이 자리의 루트가 된다
    if (x->key < root->key) root->l = insert(root->l, x); else root->r = insert(root->r, x);
    return root;
}
Node* zip(Node* a, Node* b) { if (!a) return b; if (!b) return a; if (above(a, b)) { a->r = zip(a->r, b); return a; } b->l = zip(a, b->l); return b; }
Node* erase(Node* root, int k) {
    if (!root) return nullptr;
    if (k < root->key) { root->l = erase(root->l, k); return root; }
    if (k > root->key) { root->r = erase(root->r, k); return root; }
    Node* dead = root; Node* z = zip(root->l, root->r); delete dead; return z;
}
void destroy(Node* n) { if (!n) return; destroy(n->l); destroy(n->r); delete n; }
bool valid(Node* n, long lo, long hi) {
    if (!n) return true;
    if (!(n->key > lo && n->key < hi)) return false;
    if (n->l && !above(n, n->l)) return false;
    if (n->r && !above(n, n->r)) return false;
    return valid(n->l, lo, n->key) && valid(n->r, n->key, hi);
}
int height(Node* n) { return n ? 1 + std::max(height(n->l), height(n->r)) : 0; }
bool contains(Node* n, int k) { while (n) { if (k == n->key) return true; n = k < n->key ? n->l : n->r; } return false; }

int main() {
    Node* root = nullptr; std::set<int> truth;
    for (int k = 0; k < 6000; k++) { root = insert(root, new Node(k)); truth.insert(k); }       // 정렬된 입력
    assert(valid(root, -1, 1 << 30) && height(root) <= 6 * std::log2(6000));
    for (int i = 0; i < 4000; i++) { int k = rng() % 6000; root = erase(root, k); truth.erase(k); }
    assert(valid(root, -1, 1 << 30));
    for (int k = 0; k < 6000; k += 7) assert(contains(root, k) == (truth.count(k) > 0));
    std::cout << "ZipTree: " << truth.size() << " keys, height " << height(root) << ", heap-on-rank invariant holds." << std::endl;
    destroy(root);
    return 0;
}
// Time Complexity: 기대 O(log N)
// Space Complexity: O(N) (랭크는 작은 정수)
```
## WAVLTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// WAVL 트리(weak AVL, Haeupler–Sen–Tarjan 2015): AVL 과 레드-블랙의 장점을 합친 균형 트리.  각 노드에 정수 "랭크" 를 두고, 부모와 자식의 랭크 차(rank difference)가 항상 1 또는 2 이며
// 잎(자식이 둘 다 없음)의 랭크는 0 이다 (널 노드의 랭크는 -1).  삽입만 하면 AVL 처럼 높이 ≤ log₂(n+1)·1.44 로 균형이 좋고, 삭제를 포함해도 레드-블랙 정도(≤ 2 log₂ n)를 보장하며 회전은 상수 번.
// 삽입 후 새 잎의 부모와 랭크 차가 0 이 되는 위반을 위로 올라가며 수리한다: 형제와의 차가 1 이면 승급(promote), 2 이면 회전
struct Node { int key, rank = 0; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
int rk(Node* n) { return n ? n->rank : -1; }
Node* rotL(Node* x) { Node* y = x->r; x->r = y->l; y->l = x; return y; }
Node* rotR(Node* x) { Node* y = x->l; x->l = y->r; y->r = x; return y; }

Node* fix(Node* t) {                                                          // t 의 자식 중 하나가 t 와 같은 랭크(0-자식)면 수리
    if (rk(t->l) == t->rank) {                                                // 왼쪽이 0-자식
        if (rk(t->r) == t->rank - 1) { t->rank++; return t; }                 // 형제 차이 1: 승급 (위반이 부모로 전파될 수 있다)
        Node* x = t->l;
        if (rk(x->r) == x->rank - 2) { t = rotR(t); t->r->rank--; return t; }                         // 바깥쪽이 무거움: 단일 회전 + t 강등
        Node* y = x->r; t->l = rotL(x); t = rotR(t); y->rank++; y->l->rank--; y->r->rank--; return t;      // 안쪽이 무거움: 이중 회전
    }
    if (rk(t->r) == t->rank) {                                                // 오른쪽이 0-자식 (대칭)
        if (rk(t->l) == t->rank - 1) { t->rank++; return t; }
        Node* x = t->r;
        if (rk(x->l) == x->rank - 2) { t = rotL(t); t->l->rank--; return t; }
        Node* y = x->l; t->r = rotR(x); t = rotL(t); y->rank++; y->l->rank--; y->r->rank--; return t;
    }
    return t;
}
Node* insert(Node* t, int k) {
    if (!t) return new Node(k);
    if (k < t->key) t->l = insert(t->l, k); else if (k > t->key) t->r = insert(t->r, k); else return t;
    return fix(t);
}
bool valid(Node* n, long lo, long hi) {                                       // BST 순서 + 랭크 규칙
    if (!n) return true;
    if (!(n->key > lo && n->key < hi)) return false;
    int dl = n->rank - rk(n->l), dr = n->rank - rk(n->r);
    if (dl < 1 || dl > 2 || dr < 1 || dr > 2) return false;                   // 모든 랭크 차는 1 또는 2
    if (!n->l && !n->r && n->rank != 0) return false;                         // 잎의 랭크는 0
    return valid(n->l, lo, n->key) && valid(n->r, n->key, hi);
}
int height(Node* n) { return n ? 1 + std::max(height(n->l), height(n->r)) : 0; }
void destroy(Node* n) { if (!n) return; destroy(n->l); destroy(n->r); delete n; }

int main() {
    Node* t = nullptr;
    for (int k = 0; k < 10000; k++) { t = insert(t, k); if (k % 997 == 0) assert(valid(t, -1, 1 << 30)); }    // 정렬된 입력
    assert(valid(t, -1, 1 << 30));
    assert(height(t) <= 1.45 * std::log2(10001) + 1);                         // 삽입만 있으면 AVL 수준의 높이
    std::mt19937 rng(37); Node* u = nullptr; std::vector<int> keys(5000); for (int i = 0; i < 5000; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) u = insert(u, k);
    assert(valid(u, -1, 1 << 30) && height(u) <= 1.45 * std::log2(5001) + 1);
    std::cout << "WAVLTree: height " << height(t) << " (sorted) / " << height(u) << " (random), all rank differences in {1,2}." << std::endl;
    destroy(t); destroy(u);
    return 0;
}
// Time Complexity: 삽입 O(log N), 회전 최대 2번
// Space Complexity: O(N) (랭크는 작은 정수; 랭크 차를 2비트로 저장 가능)
```
# Part 14. 함수형 자료구조
## PersistentTree()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cmath>
#include <cassert>

// 영속 세그먼트 트리: 점 갱신을 할 때 루트에서 그 잎까지의 경로(O(log n) 개 노드)만 새로 만들고 나머지는 이전 버전과 공유한다(경로 복사, path copying).
// 갱신할 때마다 새 루트가 하나 생기고, 옛 루트로도 질의할 수 있다 -> "버전 v 시점의 구간 합" 같은 과거 질의, k 번째 수 구하기(구간 내 k번째로 작은 값), 롤백/브랜칭에 쓴다
struct Node { int l = 0, r = 0; long sum = 0; };
std::vector<Node> pool(1);                                        // 0 번은 널 노드 (합 0, 자식 0)
int build(int l, int r, const std::vector<long>& a) {
    int id = pool.size(); pool.push_back({});
    if (l == r) { pool[id].sum = a[l]; return id; }
    int m = (l + r) / 2, L = build(l, m, a), R = build(m + 1, r, a);
    pool[id] = {L, R, pool[L].sum + pool[R].sum}; return id;
}
int update(int prev, int l, int r, int pos, long val) {            // prev 버전에서 pos 를 val 로 바꾼 새 버전의 루트
    int id = pool.size(); pool.push_back(pool[prev]);
    if (l == r) { pool[id].sum = val; return id; }
    int m = (l + r) / 2;
    if (pos <= m) { int c = update(pool[prev].l, l, m, pos, val); pool[id].l = c; }
    else          { int c = update(pool[prev].r, m + 1, r, pos, val); pool[id].r = c; }
    pool[id].sum = pool[pool[id].l].sum + pool[pool[id].r].sum; return id;
}
long query(int node, int l, int r, int a, int b) {
    if (!node || b < l || r < a) return 0;
    if (a <= l && r <= b) return pool[node].sum;
    int m = (l + r) / 2; return query(pool[node].l, l, m, a, b) + query(pool[node].r, m + 1, r, a, b);
}

int main() {
    const int N = 1000, U = 2000; std::mt19937 rng(40);
    std::vector<long> a(N); for (auto& x : a) x = rng() % 100;
    std::vector<int> roots = {build(0, N - 1, a)}; std::vector<std::vector<long>> snapshot = {a};
    size_t afterBuild = pool.size();
    for (int i = 0; i < U; i++) { int pos = rng() % N; long v = rng() % 1000; a[pos] = v; roots.push_back(update(roots.back(), 0, N - 1, pos, v)); snapshot.push_back(a); }
    assert(pool.size() - afterBuild <= (size_t)U * (std::log2(N) + 2));              // 갱신당 새 노드는 경로 길이만큼 (전체 복사였다면 갱신당 2000개)
    for (int q = 0; q < 3000; q++) {
        int ver = rng() % roots.size(), l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        long expect = 0; for (int i = l; i <= r; i++) expect += snapshot[ver][i];
        assert(query(roots[ver], 0, N - 1, l, r) == expect);                           // 어떤 과거 버전에서도 정확한 구간 합
    }
    std::cout << "PersistentTree: " << roots.size() << " versions in " << pool.size() << " nodes (full copies would need " << (size_t)U * 2 * N << ")" << std::endl;
    return 0;
}
// Time Complexity: 갱신·질의 O(log N)
// Space Complexity: 버전당 O(log N)
```
## ImmutableTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <random>
#include <tuple>
#include <utility>
#include <vector>
#include <cassert>

// 불변 트리 + 해시 컨싱(hash-consing): 노드를 (키, 왼쪽 id, 오른쪽 id) 로 "인터닝" 해서 같은 내용의 서브트리는 메모리에 단 하나만 둔다.
// 균형을 키의 해시로 정한 우선순위(트립)로 잡으면 트리 모양이 "삽입 순서와 무관하게 키 집합만으로 결정"(history independence)되므로,
// 같은 집합은 항상 같은 루트 id -> 두 집합이 같은지 O(1) 비교.  (Git 의 객체 저장소, 함수형 DB, 증분 계산이 쓰는 원리)
struct Node { int key, l, r, size; };
std::vector<Node> pool(1, Node{0, 0, 0, 0});                       // id 0 = 빈 트리
std::map<std::tuple<int, int, int>, int> interned;
int mk(int key, int l, int r) {
    auto k = std::make_tuple(key, l, r); auto it = interned.find(k);
    if (it != interned.end()) return it->second;                   // 이미 있는 내용이면 그 노드를 재사용
    int id = pool.size(); pool.push_back({key, l, r, 1 + pool[l].size + pool[r].size}); interned[k] = id; return id;
}
unsigned pri(int key) { unsigned x = key * 2654435761u; x ^= x >> 15; x *= 2246822519u; x ^= x >> 13; return x; }
std::pair<int, int> split(int t, int key) {                         // 키 < key 와 키 >= key (새 노드를 만들며 원본은 건드리지 않는다)
    if (!t) return {0, 0};
    const Node n = pool[t];
    if (n.key < key) { auto p = split(n.r, key); return {mk(n.key, n.l, p.first), p.second}; }
    auto p = split(n.l, key); return {p.first, mk(n.key, p.second, n.r)};
}
int merge(int a, int b) {
    if (!a) return b; if (!b) return a;
    const Node x = pool[a], y = pool[b];
    if (pri(x.key) > pri(y.key)) return mk(x.key, x.l, merge(x.r, b));
    return mk(y.key, merge(a, y.l), y.r);
}
int insert(int t, int k) { auto p = split(t, k); auto q = split(p.second, k + 1); return merge(merge(p.first, mk(k, 0, 0)), q.second); }
bool contains(int t, int k) { while (t) { if (k == pool[t].key) return true; t = k < pool[t].key ? pool[t].l : pool[t].r; } return false; }

int main() {
    std::vector<int> keys; for (int i = 1; i <= 500; i++) keys.push_back(i * 3);
    int asc = 0, desc = 0, shuffled = 0; std::mt19937 rng(41);
    for (int k : keys) asc = insert(asc, k);
    for (auto it = keys.rbegin(); it != keys.rend(); ++it) desc = insert(desc, *it);
    std::vector<int> sh = keys; std::shuffle(sh.begin(), sh.end(), rng); for (int k : sh) shuffled = insert(shuffled, k);
    assert(asc == desc && desc == shuffled);                          // 삽입 순서가 달라도 같은 집합은 같은 루트 (O(1) 동일성 판정)
    assert(pool[asc].size == 500);
    size_t before = pool.size();
    int next = insert(asc, 7);                                         // 새 버전: 키 하나 추가
    assert(pool.size() - before <= 60);                                // 새로 만든 노드는 경로 길이 정도뿐 (나머지는 공유)
    assert(contains(next, 7) && !contains(asc, 7) && next != asc);     // 이전 버전은 그대로
    assert(insert(next, 7) == next);                                    // 이미 있는 키를 또 넣어도 같은 트리 (멱등)
    std::cout << "ImmutableTree: three insertion orders -> one root id " << asc << "; new version allocated " << pool.size() - before << " nodes." << std::endl;
    return 0;
}
// Time Complexity: 삽입 기대 O(log N) (인터닝 조회 포함 O(log² N))
// Space Complexity: 버전당 O(log N), 같은 서브트리는 공유
```
## FingerTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <deque>
#include <iostream>
#include <memory>
#include <random>
#include <vector>

// 핑거 트리(요약, 정본은 AdvancedDataStructures.md Part 4): "핑거" 는 구조 안의 특정 위치를 가리키는 손가락 — 핑거 근처의 연산은 전체 크기가 아니라 *핑거까지의 거리*에 비례하는 비용만 든다.
//  양 끝에 짧은 목록(1~4 개, 손가락)을 두고 가운데는 "2-3 노드"를 원소로 하는 같은 구조의 트리를 재귀적으로 단다 → 양 끝 push/pop 분할상환 O(1), 노드마다 부분 트리 크기를 저장하면 위치 접근이 O(log min(i, n−i)).  모든 연산이 새 루트를 돌려주는 *영속* 구조다.
//  여기서는 덱 연산(pushFront/pushBack/viewFront/viewBack)과 색인 at(i) 만 옮겼다 (연결·분할은 정본).  ① 무작위 영속 연산 6000 번을 std::deque 모형과 대조하고 과거 버전이 그대로임을 확인  ② 100 만 번의 덱 연산을 std::deque 와 대조
//  ③ 분할상환: 100 만 번 push 에 만든 2-3 노드 수 ≤ n/2 + 상수  ④ 핑거 성질: at(i) 가 내려가는 수준 수 ≤ 2 + log2(min(i, n−1−i) + 1) — 양 끝 근처는 얕게, 가운데는 깊게  ⑤ 척추 깊이 < 22 (n = 10^6).
long nodeCalls = 0;
struct Node; typedef std::shared_ptr<const Node> NP;
struct Node { long long val; int size; std::vector<NP> k; };
NP leaf(long long v) { return std::make_shared<const Node>(Node{v, 1, {}}); }
NP node(std::vector<NP> k) { ++nodeCalls; int s = 0; for (auto& x : k) s += x->size; return std::make_shared<const Node>(Node{0, s, std::move(k)}); }
struct FT; typedef std::shared_ptr<const FT> F;
struct FT { int kind; NP one; std::vector<NP> pre, suf; F mid; int size; };                 // kind: 0 빈 트리, 1 단일 원소, 2 Deep(앞 손가락, 가운데 트리, 뒤 손가락)
int sz(const std::vector<NP>& d) { int s = 0; for (auto& x : d) s += x->size; return s; }
F Empty() { static F e = std::make_shared<const FT>(FT{0, nullptr, {}, {}, nullptr, 0}); return e; }
F Single(NP a) { return std::make_shared<const FT>(FT{1, a, {}, {}, nullptr, a->size}); }
F Deep(std::vector<NP> pre, F mid, std::vector<NP> suf) { int s = sz(pre) + mid->size + sz(suf); return std::make_shared<const FT>(FT{2, nullptr, std::move(pre), std::move(suf), std::move(mid), s}); }
F digitToTree(const std::vector<NP>& d) {
    switch (d.size()) { case 0: return Empty(); case 1: return Single(d[0]); case 2: return Deep({d[0]}, Empty(), {d[1]}); case 3: return Deep({d[0], d[1]}, Empty(), {d[2]}); default: return Deep({d[0], d[1]}, Empty(), {d[2], d[3]}); }
}
F pushFront(const F& t, NP a) {
    if (t->kind == 0) return Single(a);
    if (t->kind == 1) return Deep({a}, Empty(), {t->one});
    if (t->pre.size() < 4) { auto p = t->pre; p.insert(p.begin(), a); return Deep(p, t->mid, t->suf); }
    return Deep({a, t->pre[0]}, pushFront(t->mid, node({t->pre[1], t->pre[2], t->pre[3]})), t->suf);           // 손가락이 넘치면 3 개를 노드로 묶어 가운데로
}
F pushBack(const F& t, NP a) {
    if (t->kind == 0) return Single(a);
    if (t->kind == 1) return Deep({t->one}, Empty(), {a});
    if (t->suf.size() < 4) { auto s = t->suf; s.push_back(a); return Deep(t->pre, t->mid, s); }
    return Deep(t->pre, pushBack(t->mid, node({t->suf[0], t->suf[1], t->suf[2]})), {t->suf[3], a});
}
std::pair<NP, F> viewFront(const F& t);
std::pair<F, NP> viewBack(const F& t);
F deepL(std::vector<NP> pre, const F& mid, std::vector<NP> suf) { if (!pre.empty()) return Deep(pre, mid, suf); if (mid->kind == 0) return digitToTree(suf); auto v = viewFront(mid); return Deep(v.first->k, v.second, suf); }     // 앞 손가락이 비면 가운데에서 노드 하나를 꺼내 채운다
F deepR(std::vector<NP> pre, const F& mid, std::vector<NP> suf) { if (!suf.empty()) return Deep(pre, mid, suf); if (mid->kind == 0) return digitToTree(pre); auto v = viewBack(mid); return Deep(pre, v.first, v.second->k); }
std::pair<NP, F> viewFront(const F& t) { if (t->kind == 1) return {t->one, Empty()}; NP h = t->pre[0]; return {h, deepL(std::vector<NP>(t->pre.begin() + 1, t->pre.end()), t->mid, t->suf)}; }
std::pair<F, NP> viewBack(const F& t) { if (t->kind == 1) return {Empty(), t->one}; NP h = t->suf.back(); return {deepR(t->pre, t->mid, std::vector<NP>(t->suf.begin(), t->suf.end() - 1)), h}; }
long long leafAt(const Node* n, int i) { while (!n->k.empty()) { for (auto& c : n->k) { if (i < c->size) { n = c.get(); break; } i -= c->size; } } return n->val; }
long long digitAt(const std::vector<NP>& d, int i) { for (auto& x : d) { if (i < x->size) return leafAt(x.get(), i); i -= x->size; } return -1; }
long long at(const F& root, int i, int* levels = nullptr) {                                  // 척추를 따라 내려간다: 앞 손가락 → 가운데(다음 수준) → 뒤 손가락
    const FT* t = root.get(); int lv = 1;
    for (;;) { if (t->kind == 1) { if (levels) *levels = lv; return leafAt(t->one.get(), i); } int spr = sz(t->pre); if (i < spr) { if (levels) *levels = lv; return digitAt(t->pre, i); } i -= spr;
        if (i < t->mid->size) { t = t->mid.get(); ++lv; continue; } i -= t->mid->size; if (levels) *levels = lv; return digitAt(t->suf, i); }
}
void flat(const NP& n, std::vector<long long>& out) { if (n->k.empty()) out.push_back(n->val); else for (auto& c : n->k) flat(c, out); }
void collect(const F& t, std::vector<long long>& out) { if (t->kind == 0) return; if (t->kind == 1) { flat(t->one, out); return; } for (auto& x : t->pre) flat(x, out); collect(t->mid, out); for (auto& x : t->suf) flat(x, out); }
std::vector<long long> toVec(const F& t) { std::vector<long long> v; collect(t, v); return v; }
int spineDepth(const F& t) { int d = 0; for (const FT* c = t.get(); c->kind == 2; c = c->mid.get()) ++d; return d; }

int main() {
    std::mt19937 rng(12); std::vector<F> ver = {Empty()}; std::vector<std::vector<long long>> model = {{}};                // ① 영속 연산 6000 번
    for (int step = 0; step < 6000; ++step) {
        int base = (int)(rng() % ver.size()); const F t = ver[base]; std::vector<long long> m = model[base]; int op = (int)(rng() % 5); F r = t;
        if (op == 0 || m.empty()) { long long x = rng() % 1000; r = pushFront(t, leaf(x)); m.insert(m.begin(), x); }
        else if (op == 1) { long long x = rng() % 1000; r = pushBack(t, leaf(x)); m.push_back(x); }
        else if (op == 2) { auto v = viewFront(t); assert(v.first->val == m.front()); r = v.second; m.erase(m.begin()); }
        else if (op == 3) { auto v = viewBack(t); assert(v.second->val == m.back()); r = v.first; m.pop_back(); }
        else { int i = (int)(rng() % m.size()); assert(at(t, i) == m[i]); }
        if (m.size() > 300) { while (m.size() > 100) { r = viewFront(r).second; m.erase(m.begin()); } }
        assert(r->size == (int)m.size() && toVec(r) == m); ver.push_back(r); model.push_back(m);
    }
    for (size_t i = 0; i < ver.size(); i += 7) assert(toVec(ver[i]) == model[i]);                                    // 옛 버전은 그대로
    { std::deque<long long> ref; F t = Empty(); for (long step = 0; step < 1000000; ++step) {                      // ② 100 만 번의 덱 연산
          int op = (int)(rng() % 4); bool grow = ref.size() < 5000 || rng() % 2 == 0;
          if (ref.empty() || (grow && op < 2)) { long long x = (long long)rng(); if (op == 0) { t = pushFront(t, leaf(x)); ref.push_front(x); } else { t = pushBack(t, leaf(x)); ref.push_back(x); } }
          else if (op == 2) { auto v = viewFront(t); assert(v.first->val == ref.front()); t = v.second; ref.pop_front(); }
          else { auto v = viewBack(t); assert(v.second->val == ref.back()); t = v.first; ref.pop_back(); }
          assert(t->size == (int)ref.size()); if (step % 1000 == 0 && !ref.empty()) { int i = (int)(rng() % ref.size()); assert(at(t, i) == ref[i]); } if (step % 100000 == 0) assert(toVec(t) == std::vector<long long>(ref.begin(), ref.end())); } }
    const int n = 1000000;                                                                                       // ③ 분할상환
    { F t = Empty(); nodeCalls = 0; for (int i = 0; i < n; ++i) t = pushFront(t, leaf(i)); long front = nodeCalls; assert(front <= n / 2 + 100 && t->size == n && at(t, 0) == n - 1 && at(t, n - 1) == 0);
      F u = Empty(); nodeCalls = 0; for (int i = 0; i < n; ++i) u = pushBack(u, leaf(i)); long back = nodeCalls; assert(back <= n / 2 + 100);
      assert(spineDepth(t) < 22 && spineDepth(u) < 22);                                                          // ⑤
      for (int q = 0; q < 200000; ++q) { int i = (int)(rng() % n); int lv = 0; assert(at(u, i, &lv) == i); int d = std::min(i, n - 1 - i); assert(lv <= 2 + std::log2((double)d + 1)); }          // ④ 핑거 성질
      int lvEnd = 0, lvMid = 0; at(u, 0, &lvEnd); at(u, n / 2, &lvMid); assert(lvEnd == 1 && lvMid > 8);
      std::cout << "FingerTree: 6000 persistent deque operations and 10^6 mixed operations matched std::deque, " << front << " 2-3 nodes were built by 10^6 pushes (<= n/2), and indexing the ends touched " << lvEnd << " level versus " << lvMid << " in the middle" << std::endl; }
    return 0;
}
// Time Complexity: 양 끝 push/pop 분할상환 O(1), at(i) O(log min(i, N − i))
// Space Complexity: O(N), 영속 버전은 구조 공유
```

# Part 15. 그래프 확장
## RootingTree()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 트리 뿌리 내리기(rooting)와 재루팅(rerooting): 방향 없는 트리에 루트 r 을 정하고 부모·깊이·서브트리 크기를 구한다(반복 DFS 로 깊은 트리에서도 스택 오버플로 없음).
// 재루팅 DP: 모든 정점에서 "다른 모든 정점까지의 거리 합" 을 O(n) 에 구한다.  루트의 값을 한 번 구하면, 루트를 자식 c 로 옮길 때 c 의 서브트리(크기 s)는 1씩 가까워지고 나머지(n-s)는 1씩 멀어진다:
//   sum[c] = sum[parent] - s[c] + (n - s[c])
int main() {
    std::mt19937 rng(42);
    for (int trial = 0; trial < 50; trial++) {
        int n = rng() % 150 + 2; std::vector<std::vector<int>> g(n);
        for (int v = 1; v < n; v++) { int p = rng() % v; g[p].push_back(v); g[v].push_back(p); }
        std::vector<int> parent(n, -1), depth(n, 0), order, size(n, 1);
        std::vector<int> st = {0};
        while (!st.empty()) { int u = st.back(); st.pop_back(); order.push_back(u); for (int v : g[u]) if (v != parent[u]) { parent[v] = u; depth[v] = depth[u] + 1; st.push_back(v); } }
        for (int i = n - 1; i > 0; i--) size[parent[order[i]]] += size[order[i]];             // 자식이 먼저 나오는 역순으로 크기 누적
        std::vector<long> sum(n, 0); for (int v = 0; v < n; v++) sum[0] += depth[v];
        for (int i = 1; i < n; i++) { int c = order[i]; sum[c] = sum[parent[c]] - size[c] + (n - size[c]); }     // 부모가 먼저 나오는 순서로 재루팅
        for (int s = 0; s < n; s++) {                                                          // 검증: 모든 정점에서 BFS 로 거리 합
            std::vector<int> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0; long total = 0;
            while (!q.empty()) { int u = q.front(); q.pop(); total += d[u]; for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }
            assert(sum[s] == total);
        }
    }
    std::cout << "RootingTree: rerooting DP matched BFS from every vertex on 50 random trees." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## TreeDP()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 트리 DP: 트리에서는 "서브트리" 가 자연스러운 부분 문제다.  자식들의 결과를 합쳐 부모의 결과를 만든다 (후위 순서).  고전 두 가지:
//  (1) 가중치 최대 독립 집합(서로 인접하지 않은 정점의 가중치 합 최대): dp[v][0] = v 미선택 = Σ max(dp[c][0], dp[c][1]),  dp[v][1] = v 선택 = w[v] + Σ dp[c][0]
//  (2) 트리의 지름: 정점마다 "아래로 가장 긴 경로" 를 구하고, 가장 긴 두 개를 이은 것이 v 를 지나는 최장 경로
int main() {
    std::mt19937 rng(43);
    for (int trial = 0; trial < 200; trial++) {
        int n = rng() % 12 + 2; std::vector<std::vector<int>> g(n); std::vector<int> w(n);
        for (int v = 0; v < n; v++) w[v] = rng() % 20 + 1;
        std::vector<int> parent(n, -1), order;
        for (int v = 1; v < n; v++) { int p = rng() % v; g[p].push_back(v); g[v].push_back(p); }
        std::vector<int> st = {0};
        while (!st.empty()) { int u = st.back(); st.pop_back(); order.push_back(u); for (int v : g[u]) if (v != parent[u]) { parent[v] = u; st.push_back(v); } }
        std::vector<long> in(n), out(n); std::vector<int> down(n, 0); int diameter = 0;
        for (int i = n - 1; i >= 0; i--) {                                                 // 자식 -> 부모 순서
            int u = order[i]; in[u] = w[u]; out[u] = 0; int best1 = 0, best2 = 0;
            for (int c : g[u]) if (c != parent[u]) {
                in[u] += out[c]; out[u] += std::max(in[c], out[c]);
                int d = down[c] + 1; if (d > best1) { best2 = best1; best1 = d; } else if (d > best2) best2 = d;
            }
            down[u] = best1; diameter = std::max(diameter, best1 + best2);
        }
        long mis = std::max(in[0], out[0]);
        long brute = 0;                                                                    // 비트마스크 완전 탐색
        for (int mask = 0; mask < (1 << n); mask++) {
            bool ok = true; long s = 0;
            for (int v = 0; v < n && ok; v++) if (mask >> v & 1) { s += w[v]; for (int c : g[v]) if ((mask >> c & 1)) ok = false; }
            if (ok) brute = std::max(brute, s);
        }
        assert(mis == brute);
        auto bfs = [&](int s) { std::vector<int> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0; int last = s; while (!q.empty()) { int u = q.front(); q.pop(); last = u; for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } return std::make_pair(last, d[last]); };
        assert(bfs(bfs(0).first).second == diameter);                                      // BFS 두 번 방식의 지름과 일치
    }
    std::cout << "TreeDP: max-weight independent set and diameter verified on 200 random trees." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## HeavyLightDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 중경량 분할(HLD): 각 정점에서 서브트리가 가장 큰 자식으로 가는 간선을 "무거운 간선" 으로 정해 트리를 무거운 경로(체인)들로 나눈다.
// 루트에서 어떤 정점까지 가벼운 간선은 최대 log₂ n 개뿐이므로 경로 질의는 체인 O(log n) 개를 건너뛰는 것이 된다.  체인 안의 정점들이 DFS 순서에서 연속이 되게 번호를 매기면
// 각 체인은 배열 구간이므로 세그먼트 트리/펜윅 트리로 경로 합·갱신을 O(log² n) 에 처리한다 (트리 위의 경로 질의 문제의 표준 해법)
struct HLD {
    int n, cur = 0; std::vector<std::vector<int>> g; std::vector<int> parent, depth, heavy, head, pos, sz; std::vector<long> bit;
    explicit HLD(const std::vector<std::vector<int>>& adj) : n(adj.size()), g(adj), parent(n, -1), depth(n, 0), heavy(n, -1), head(n), pos(n), sz(n, 1), bit(n + 1, 0) { dfs1(0); dfs2(0, 0); }
    void dfs1(int v) { for (int c : g[v]) if (c != parent[v]) { parent[c] = v; depth[c] = depth[v] + 1; dfs1(c); sz[v] += sz[c]; if (heavy[v] < 0 || sz[c] > sz[heavy[v]]) heavy[v] = c; } }
    void dfs2(int v, int h) { head[v] = h; pos[v] = cur++; if (heavy[v] >= 0) dfs2(heavy[v], h); for (int c : g[v]) if (c != parent[v] && c != heavy[v]) dfs2(c, c); }
    void add(int v, long d) { for (int i = pos[v] + 1; i <= n; i += i & -i) bit[i] += d; }                    // 점 갱신: 펜윅
    long prefix(int i) const { long s = 0; for (; i > 0; i -= i & -i) s += bit[i]; return s; }
    long pathSum(int u, int v) const {
        long res = 0;
        while (head[u] != head[v]) {                                                                       // 더 깊은 체인의 머리부터 한 체인씩 올라간다
            if (depth[head[u]] < depth[head[v]]) std::swap(u, v);
            res += prefix(pos[u] + 1) - prefix(pos[head[u]]); u = parent[head[u]];
        }
        if (depth[u] > depth[v]) std::swap(u, v);
        return res + prefix(pos[v] + 1) - prefix(pos[u]);                                                   // 같은 체인: 구간 하나
    }
};

int main() {
    std::mt19937 rng(44); const int N = 3000;
    std::vector<std::vector<int>> g(N); std::vector<int> par(N, -1), dep(N, 0);
    for (int v = 1; v < N; v++) { int p = (rng() % 4 == 0) ? v - 1 : rng() % v; g[p].push_back(v); g[v].push_back(p); par[v] = p; dep[v] = dep[p] + 1; }
    HLD h(g); std::vector<long> val(N, 0);
    for (int op = 0; op < 8000; op++) {
        if (rng() % 3 == 0) { int v = rng() % N; long d = (long)(rng() % 100) - 50; val[v] += d; h.add(v, d); }
        else {
            int u = rng() % N, v = rng() % N; long expect = 0, a = u, b = v;                                // 순진한 방법: 깊은 쪽을 부모로 올려 가며 합산
            while (a != b) { if (dep[a] < dep[b]) std::swap(a, b); expect += val[a]; a = par[a]; }
            expect += val[a];
            assert(h.pathSum(u, v) == expect);
        }
    }
    std::cout << "HeavyLightDecomposition: path sums on a " << N << "-vertex tree match the naive walk." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(N), 경로 질의·갱신 O(log² N)
// Space Complexity: O(N)
```
## CentroidDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <climits>
#include <queue>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 센트로이드 분해: 트리에서 "제거하면 남는 모든 컴포넌트의 크기가 n/2 이하" 가 되는 정점(센트로이드)을 찾아 루트로 삼고, 남은 컴포넌트에 재귀한다.  깊이가 O(log n) 인 센트로이드 트리가 나온다.
// 어떤 두 정점 u, v 의 경로는 센트로이드 트리에서 둘의 공통 조상 센트로이드 하나를 반드시 지난다 -> "가장 가까운 표시된 정점" 같은 질의를 O(log n) 에 답한다:
//   표시(v): v 의 모든 센트로이드 조상 c 에 대해 best[c] = min(best[c], dist(v, c)).   질의(v): min over c (best[c] + dist(v, c))
struct CD {
    int n; std::vector<std::vector<int>> g; std::vector<bool> removed; std::vector<int> sz, best;
    std::vector<std::vector<std::pair<int, int>>> anc;                   // anc[v] = (센트로이드 조상, v 까지의 거리) — 위에서 아래 순서
    explicit CD(const std::vector<std::vector<int>>& adj) : n(adj.size()), g(adj), removed(n, false), sz(n), best(n, INT_MAX / 2), anc(n) { decompose(0); }
    int calcSize(int u, int p) { sz[u] = 1; for (int v : g[u]) if (v != p && !removed[v]) sz[u] += calcSize(v, u); return sz[u]; }
    int findCentroid(int u, int p, int total) { for (int v : g[u]) if (v != p && !removed[v] && sz[v] * 2 > total) return findCentroid(v, u, total); return u; }
    void decompose(int entry) {
        int total = calcSize(entry, -1), c = findCentroid(entry, -1, total);
        std::queue<std::pair<int, int>> q; std::vector<int> dist(n, -1); q.push({c, 0}); dist[c] = 0;           // 센트로이드에서 컴포넌트 안의 모든 정점까지 거리
        while (!q.empty()) { auto cur = q.front(); q.pop(); anc[cur.first].push_back({c, cur.second}); for (int v : g[cur.first]) if (!removed[v] && dist[v] < 0) { dist[v] = cur.second + 1; q.push({v, cur.second + 1}); } }
        removed[c] = true;
        for (int v : g[c]) if (!removed[v]) decompose(v);
    }
    void mark(int v) { for (auto& a : anc[v]) best[a.first] = std::min(best[a.first], a.second); }
    int nearest(int v) const { int r = INT_MAX / 2; for (auto& a : anc[v]) r = std::min(r, best[a.first] + a.second); return r; }
};

int main() {
    std::mt19937 rng(45); const int N = 1000;
    std::vector<std::vector<int>> g(N); for (int v = 1; v < N; v++) { int p = rng() % v; g[p].push_back(v); g[v].push_back(p); }
    CD cd(g); std::vector<int> marked;
    size_t maxDepth = 0; for (int v = 0; v < N; v++) maxDepth = std::max(maxDepth, cd.anc[v].size());
    assert(maxDepth <= 11);                                              // 센트로이드 트리의 깊이 <= log2(N) + 1
    for (int op = 0; op < 400; op++) {
        if (rng() % 2 || marked.empty()) { int v = rng() % N; cd.mark(v); marked.push_back(v); }
        else {
            int s = rng() % N; std::vector<int> d(N, -1); std::queue<int> q;                              // 검증: 표시된 정점들에서 동시에 BFS
            for (int m : marked) { d[m] = 0; q.push(m); }
            while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }
            assert(cd.nearest(s) == d[s]);
        }
    }
    std::cout << "CentroidDecomposition: centroid-tree depth " << maxDepth << ", nearest-marked queries match multi-source BFS." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(N log N), 표시·질의 O(log N)
// Space Complexity: O(N log N)
```
## BinaryLifting()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 이진 점프(binary lifting): up[k][v] = v 의 2^k 번째 조상을 전처리(O(n log n))해 두면 k 번째 조상을 이진수로 쪼개 O(log n) 에 구한다.
// LCA(최소 공통 조상): 두 정점의 깊이를 맞춘 뒤, 큰 점프부터 "조상이 서로 달라지는 동안" 같이 올라가면 바로 아래에서 멈춘다.  거리(u, v) = depth[u] + depth[v] - 2·depth[LCA]
struct Lift {
    int n, LOG; std::vector<std::vector<int>> up; std::vector<int> depth;
    Lift(const std::vector<int>& parent) : n(parent.size()), LOG(1), depth(parent.size(), 0) {
        while ((1 << LOG) < n) LOG++;
        up.assign(LOG, std::vector<int>(n));
        for (int v = 0; v < n; v++) { up[0][v] = parent[v] < 0 ? v : parent[v]; depth[v] = parent[v] < 0 ? 0 : depth[parent[v]] + 1; }       // 부모가 번호 순서상 앞이라고 가정
        for (int k = 1; k < LOG; k++) for (int v = 0; v < n; v++) up[k][v] = up[k - 1][up[k - 1][v]];
    }
    int kth(int v, int k) const { for (int i = 0; i < LOG; i++) if (k >> i & 1) v = up[i][v]; return v; }
    int lca(int u, int v) const {
        if (depth[u] < depth[v]) std::swap(u, v);
        u = kth(u, depth[u] - depth[v]);
        if (u == v) return u;
        for (int i = LOG - 1; i >= 0; i--) if (up[i][u] != up[i][v]) { u = up[i][u]; v = up[i][v]; }
        return up[0][u];
    }
    int dist(int u, int v) const { return depth[u] + depth[v] - 2 * depth[lca(u, v)]; }
};

int main() {
    std::mt19937 rng(46); const int N = 5000;
    std::vector<int> parent(N, -1); for (int v = 1; v < N; v++) parent[v] = (rng() % 3 == 0) ? v - 1 : rng() % v;
    Lift L(parent);
    for (int q = 0; q < 20000; q++) {
        int u = rng() % N, v = rng() % N;
        std::vector<bool> anc(N, false); for (int x = u;; x = parent[x]) { anc[x] = true; if (parent[x] < 0) break; }          // 순진한 LCA
        int x = v; while (!anc[x]) x = parent[x];
        assert(L.lca(u, v) == x);
        int d = 0; for (int a = u; a != x; a = parent[a]) d++; for (int b = v; b != x; b = parent[b]) d++;
        assert(L.dist(u, v) == d);
        int k = rng() % (L.depth[u] + 1), a = u; for (int i = 0; i < k; i++) a = parent[a];
        assert(L.kth(u, k) == a);
    }
    std::cout << "BinaryLifting: LCA, distance and k-th ancestor verified on 20000 random queries." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(N log N), 질의 O(log N)
// Space Complexity: O(N log N)
```
## EulerTourTechnique()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 오일러 투어 기법: DFS 로 정점에 들어갈 때 tin, 나올 때 tout 번호를 매기면 "v 의 서브트리 = 구간 [tin[v], tout[v])" 가 된다.  트리 문제가 배열 구간 문제로 바뀐다:
//   서브트리 합 질의 = 구간 합,   v 의 값 갱신 = 점 갱신 (펜윅 트리).  또 "루트에서 v 까지의 경로 합" 은 v 의 값을 서브트리 구간 [tin, tout) 에 더하고 tin[x] 에서 점 질의하면 된다
struct BIT {
    int n; std::vector<long> t; explicit BIT(int n) : n(n), t(n + 2, 0) {}
    void add(int i, long v) { for (i++; i <= n; i += i & -i) t[i] += v; }
    long prefix(int i) const { long s = 0; for (; i > 0; i -= i & -i) s += t[i]; return s; }       // [0, i)
};
int main() {
    std::mt19937 rng(47); const int N = 2000;
    std::vector<std::vector<int>> g(N); std::vector<int> parent(N, -1);
    for (int v = 1; v < N; v++) { int p = rng() % v; parent[v] = p; g[p].push_back(v); }
    std::vector<int> tin(N), tout(N); int timer = 0;
    std::vector<std::pair<int, size_t>> st = {{0, 0}}; tin[0] = timer++;                            // 반복 DFS
    while (!st.empty()) {
        auto& top = st.back(); int u = top.first;
        if (top.second < g[u].size()) { int c = g[u][top.second++]; tin[c] = timer++; st.push_back({c, 0}); }
        else { tout[u] = timer; st.pop_back(); }
    }
    for (int v = 0; v < N; v++) assert(tin[v] < tout[v] && tout[v] - tin[v] >= 1);
    BIT subtree(N), pathBit(N + 1); std::vector<long> val(N, 0);
    for (int op = 0; op < 8000; op++) {
        int v = rng() % N;
        if (rng() % 2) {
            long d = (long)(rng() % 100) - 30; val[v] += d;
            subtree.add(tin[v], d);                                                                   // 서브트리 합용: 점 갱신
            pathBit.add(tin[v], d); pathBit.add(tout[v], -d);                                         // 경로 합용: 서브트리 구간에 더하기
        } else {
            long expect = 0; for (int u = 0; u < N; u++) if (tin[u] >= tin[v] && tin[u] < tout[v]) expect += val[u];      // v 서브트리의 합
            assert(subtree.prefix(tout[v]) - subtree.prefix(tin[v]) == expect);
            long pathExpect = 0; for (int x = v; x >= 0; x = parent[x]) pathExpect += val[x];          // 루트에서 v 까지의 경로 합
            assert(pathBit.prefix(tin[v] + 1) == pathExpect);
        }
    }
    std::cout << "EulerTourTechnique: subtree sums and root-path sums match naive computation." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(N), 질의·갱신 O(log N)
// Space Complexity: O(N)
```

## LinkCutTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 링크-컷 트리: "간선을 추가(link)하고 끊는(cut)" 동적 포레스트에서 연결 여부와 경로 집계를 O(log n) 분할상환에 처리한다 (Sleator–Tarjan).
// 숲을 "선호 경로(preferred path)" 들로 나누고, 각 경로를 스플레이 트리 하나로 표현한다.  access(v) 는 루트에서 v 까지를 하나의 선호 경로로 만들고,
// makeroot(v) 는 그 경로를 뒤집어(reverse 태그) v 를 새 루트로 만든다.  link/cut/connected/pathSum 모두 이 두 연산으로 구성된다
const int MAXN = 205;
int ch[MAXN][2], par[MAXN]; bool rev[MAXN]; long val[MAXN], sum[MAXN];
bool isRoot(int x) { return !par[x] || (ch[par[x]][0] != x && ch[par[x]][1] != x); }
void pushup(int x) { sum[x] = sum[ch[x][0]] + sum[ch[x][1]] + val[x]; }
void pushdown(int x) { if (rev[x]) { std::swap(ch[x][0], ch[x][1]); rev[ch[x][0]] ^= 1; rev[ch[x][1]] ^= 1; rev[x] = false; } }
void rotate(int x) {
    int y = par[x], z = par[y], k = ch[y][1] == x;
    if (!isRoot(y)) ch[z][ch[z][1] == y] = x;
    par[x] = z; ch[y][k] = ch[x][!k]; if (ch[x][!k]) par[ch[x][!k]] = y; ch[x][!k] = y; par[y] = x; pushup(y);
}
void splay(int x) {
    std::vector<int> stack = {x}; for (int y = x; !isRoot(y); y = par[y]) stack.push_back(par[y]);
    for (int i = stack.size() - 1; i >= 0; i--) pushdown(stack[i]);                      // 위에서부터 지연된 뒤집기를 내려보낸다
    while (!isRoot(x)) { int y = par[x], z = par[y]; if (!isRoot(y)) rotate((ch[y][1] == x) == (ch[z][1] == y) ? y : x); rotate(x); }
    pushup(x);
}
void access(int x) { for (int last = 0; x; last = x, x = par[x]) { splay(x); ch[x][1] = last; pushup(x); } }
void makeRoot(int x) { access(x); splay(x); rev[x] ^= 1; }
int findRoot(int x) { access(x); splay(x); while (true) { pushdown(x); if (!ch[x][0]) break; x = ch[x][0]; } splay(x); return x; }
bool connected(int x, int y) { return findRoot(x) == findRoot(y); }
void link(int x, int y) { makeRoot(x); par[x] = y; }                                      // 호출 전에 서로 다른 트리인지 확인
void cut(int x, int y) { makeRoot(x); access(y); splay(y); ch[y][0] = par[x] = 0; pushup(y); }   // x-y 간선이 있다고 가정
long pathSum(int x, int y) { makeRoot(x); access(y); splay(y); return sum[y]; }
void setVal(int x, long v) { access(x); splay(x); val[x] = v; pushup(x); }

int main() {
    const int N = 60; std::mt19937 rng(48);
    for (int i = 1; i <= N; i++) val[i] = sum[i] = i;
    std::vector<std::vector<int>> adj(N + 1); std::vector<long> value(N + 1); for (int i = 1; i <= N; i++) value[i] = i;
    auto naivePath = [&](int s, int t, bool& ok) -> long {                                // 순진한 숲: BFS 로 경로를 찾아 합산
        std::vector<int> prev(N + 1, -1); std::queue<int> q; q.push(s); prev[s] = 0;
        while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (prev[v] < 0) { prev[v] = u; q.push(v); } }
        ok = prev[t] >= 0; long total = 0; if (ok) for (int x = t; x; x = prev[x]) { total += value[x]; if (x == s) break; } return total;
    };
    for (int op = 0; op < 4000; op++) {
        int u = rng() % N + 1, v = rng() % N + 1; bool ok; int kind = rng() % 4;
        if (kind == 0 && u != v) { naivePath(u, v, ok); if (!ok) { link(u, v); adj[u].push_back(v); adj[v].push_back(u); } }          // 서로 다른 트리일 때만 link
        else if (kind == 1 && !adj[u].empty()) { int w = adj[u][rng() % adj[u].size()]; cut(u, w); adj[u].erase(std::find(adj[u].begin(), adj[u].end(), w)); adj[w].erase(std::find(adj[w].begin(), adj[w].end(), u)); }
        else if (kind == 2) { long nv = rng() % 100; setVal(u, nv); value[u] = nv; }
        else { long expect = naivePath(u, v, ok); assert(connected(u, v) == ok); if (ok) assert(pathSum(u, v) == expect); }
    }
    std::cout << "LinkCutTree: link / cut / connected / path-sum verified against a naive forest over 4000 operations." << std::endl;
    return 0;
}
// Time Complexity: 모든 연산 분할상환 O(log N)
// Space Complexity: O(N)
```
## TopTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 탑 트리(top tree)의 핵심: 트리를 "클러스터" 들의 계층으로 쪼갠다.  클러스터는 경계 정점 두 개(a, b)를 가진 연결된 부분 트리이고, 두 가지 병합으로 만든다:
//   compress: a–m 클러스터와 m–b 클러스터를 이어 a–b 로 (경로를 따라 잇기),   rake: 경로 클러스터의 정점에 매달린 서브트리를 한 점으로 흡수.
// 클러스터마다 몇 가지 값만 저장해 두면 병합이 O(1) 이라 전체 트리의 값(여기서는 지름)이 루트 클러스터에서 바로 나온다.
// 이 구현은 정적 트리를 중경량 분할(heavy path)로 나눠 위 계층을 재귀적으로 만든다 (동적 갱신은 생략; 일반 탑 트리는 가중 균형으로 높이 O(log n) 보장)
struct Cluster { long len, down, up, diam; };                       // 경계 a(위)–b(아래): len = 경로 a-b 길이, down = a 에서 클러스터 내 가장 먼 거리, up = b 에서 가장 먼 거리, diam = 클러스터 내 지름
Cluster compress(const Cluster& A, const Cluster& B) {              // A 의 아래 경계 == B 의 위 경계
    return {A.len + B.len, std::max(A.down, A.len + B.down), std::max(B.up, B.len + A.up), std::max({A.diam, B.diam, A.up + B.down})};
}
struct TopTree {
    int n; std::vector<std::vector<std::pair<int, int>>> g; std::vector<int> parent, sz, heavy, pw; int maxDepth = 0;
    explicit TopTree(const std::vector<std::vector<std::pair<int, int>>>& adj) : n(adj.size()), g(adj), parent(n, -1), sz(n, 1), heavy(n, -1), pw(n, 0) { dfs(0); }
    void dfs(int v) { for (auto& e : g[v]) if (e.first != parent[v]) { parent[e.first] = v; pw[e.first] = e.second; dfs(e.first); sz[v] += sz[e.first]; if (heavy[v] < 0 || sz[e.first] > sz[heavy[v]]) heavy[v] = e.first; } }
    // 정점 v 에서 시작하는 무거운 경로 전체를 클러스터 하나로 만든다 (매달린 가벼운 서브트리는 rake 로 흡수)
    Cluster solvePath(int v, int depth) {
        std::vector<int> path; for (int x = v; x >= 0; x = heavy[x]) path.push_back(x);
        std::vector<Cluster> seq;                                                    // 정점 클러스터 Q_i 와 간선 클러스터 E_i 를 번갈아 놓는다
        for (size_t i = 0; i < path.size(); i++) {
            long best1 = 0, best2 = 0, innerDiam = 0;                                // rake: 정점에 매달린 가벼운 자식들
            for (auto& e : g[path[i]]) if (e.first != parent[path[i]] && e.first != heavy[path[i]]) {
                Cluster sub = solvePath(e.first, depth + 1); long d = e.second + sub.down;
                if (d > best1) { best2 = best1; best1 = d; } else if (d > best2) best2 = d;
                innerDiam = std::max(innerDiam, sub.diam);
            }
            seq.push_back({0, best1, best1, std::max(innerDiam, best1 + best2)});    // 정점 클러스터 (경로 길이 0)
            if (i + 1 < path.size()) seq.push_back({pw[path[i + 1]], pw[path[i + 1]], pw[path[i + 1]], pw[path[i + 1]]});   // 간선 클러스터
        }
        return combine(seq, 0, seq.size(), depth);
    }
    Cluster combine(const std::vector<Cluster>& s, size_t lo, size_t hi, int depth) {    // 균형 있게 compress: 높이 O(log 경로 길이)
        maxDepth = std::max(maxDepth, depth);
        if (hi - lo == 1) return s[lo];
        size_t mid = (lo + hi) / 2; return compress(combine(s, lo, mid, depth + 1), combine(s, mid, hi, depth + 1));
    }
};

int main() {
    std::mt19937 rng(49);
    for (int trial = 0; trial < 100; trial++) {
        int n = rng() % 200 + 2; std::vector<std::vector<std::pair<int, int>>> g(n);
        for (int v = 1; v < n; v++) { int p = (rng() % 3 == 0) ? v - 1 : rng() % v, w = rng() % 20 + 1; g[p].push_back({v, w}); g[v].push_back({p, w}); }
        TopTree tt(g); Cluster root = tt.solvePath(0, 0);
        auto far = [&](int s) { std::vector<long> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0; int last = s; while (!q.empty()) { int u = q.front(); q.pop(); if (d[u] > d[last]) last = u; for (auto& e : g[u]) if (d[e.first] < 0) { d[e.first] = d[u] + e.second; q.push(e.first); } } return std::make_pair(last, d[last]); };
        assert(root.diam == far(far(0).first).second);                           // 루트 클러스터의 지름 == 두 번 탐색으로 구한 트리 지름
        assert(root.down >= 0 && tt.maxDepth <= 2 * std::log2(n + 1) * std::log2(n + 1) + 4);   // 계층의 높이는 O(log² n)
    }
    std::cout << "TopTree: root cluster diameter matched the true diameter on 100 random weighted trees." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(N), 클러스터 병합 O(1)
// Space Complexity: O(N)
```
# Part 16. 특수 목적
## ExpressionTree()
### 대표코드
```cpp
#include <cctype>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// 수식 트리: 잎 = 피연산자(숫자·변수), 내부 노드 = 연산자.  중위 표기 -> (shunting-yard) -> 후위 표기 -> (스택) -> 트리.
// 후위 순회가 후위 표기, 전위 순회가 전위 표기, 중위 순회에 "필요한 괄호만" 붙이면 원래 식이 된다.  계산은 후위 순회 한 번, 미분은 트리를 재귀적으로 다시 쓰면 된다
struct Node; typedef std::shared_ptr<Node> P;
struct Node { std::string v; P l, r; };
P mk(const std::string& v, P l = nullptr, P r = nullptr) { return std::make_shared<Node>(Node{v, l, r}); }
bool isOp(const std::string& s) { return s.size() == 1 && std::string("+-*/^").find(s[0]) != std::string::npos; }
int prec(char c) { return c == '^' ? 3 : (c == '*' || c == '/') ? 2 : 1; }
bool rightAssoc(char c) { return c == '^'; }

std::vector<std::string> tokenize(const std::string& s) {
    std::vector<std::string> t;
    for (size_t i = 0; i < s.size();) {
        if (isspace((unsigned char)s[i])) { i++; continue; }
        if (isalnum((unsigned char)s[i]) || s[i] == '.') { size_t j = i; while (j < s.size() && (isalnum((unsigned char)s[j]) || s[j] == '.')) j++; t.push_back(s.substr(i, j - i)); i = j; }
        else t.push_back(std::string(1, s[i++]));
    }
    return t;
}
std::vector<std::string> toPostfix(const std::vector<std::string>& tok) {          // shunting-yard (단항 마이너스는 다루지 않는다)
    std::vector<std::string> out, st;
    for (auto& t : tok) {
        if (isOp(t)) {
            while (!st.empty() && isOp(st.back()) && (prec(st.back()[0]) > prec(t[0]) || (prec(st.back()[0]) == prec(t[0]) && !rightAssoc(t[0])))) { out.push_back(st.back()); st.pop_back(); }
            st.push_back(t);
        } else if (t == "(") st.push_back(t);
        else if (t == ")") { while (st.back() != "(") { out.push_back(st.back()); st.pop_back(); } st.pop_back(); }
        else out.push_back(t);
    }
    while (!st.empty()) { out.push_back(st.back()); st.pop_back(); }
    return out;
}
P fromPostfix(const std::vector<std::string>& pf) {
    std::vector<P> st;
    for (auto& t : pf) {
        if (isOp(t)) { P r = st.back(); st.pop_back(); P l = st.back(); st.pop_back(); st.push_back(mk(t, l, r)); }
        else st.push_back(mk(t));
    }
    return st.back();
}
P parse(const std::string& s) { return fromPostfix(toPostfix(tokenize(s))); }
typedef std::map<std::string, double> Env;
double eval(const P& n, const Env& env) {
    if (!n->l) { auto it = env.find(n->v); return it != env.end() ? it->second : std::stod(n->v); }
    double a = eval(n->l, env), b = eval(n->r, env);
    switch (n->v[0]) { case '+': return a + b; case '-': return a - b; case '*': return a * b; case '/': return a / b; default: return std::pow(a, b); }
}
std::string infix(const P& n, int parentPrec = 0, bool right = false, char parentOp = 0) {      // 필요한 괄호만 붙인다
    if (!n->l) return n->v;
    char op = n->v[0]; int p = prec(op);
    std::string s = infix(n->l, p, false, op) + op + infix(n->r, p, true, op);
    bool paren = p < parentPrec || (p == parentPrec && right != rightAssoc(parentOp));       // 같은 우선순위면 결합 방향의 반대쪽 자식만 괄호
    return paren ? "(" + s + ")" : s;
}
std::string prefix(const P& n)  { return !n->l ? n->v : n->v + " " + prefix(n->l) + " " + prefix(n->r); }
std::string postfix(const P& n) { return !n->l ? n->v : postfix(n->l) + " " + postfix(n->r) + " " + n->v; }
bool same(const P& a, const P& b) { return a->v == b->v && (!a->l) == (!b->l) && (!a->l || (same(a->l, b->l) && same(a->r, b->r))); }

// 기호 미분: d/dx.  수식 트리를 재귀적으로 새 트리로 다시 쓰고, simp 로 0·1 과 상수를 정리한다 (지수는 상수만 지원)
std::string fmt(double d) { std::ostringstream o; o << d; return o.str(); }
P num(double d) { return mk(fmt(d)); }
bool isNum(const P& n, double& v) { if (n->l || !(isdigit((unsigned char)n->v[0]) || n->v[0] == '.')) return false; v = std::stod(n->v); return true; }
P simp(const P& n) {
    if (!n->l) return n;
    P l = simp(n->l), r = simp(n->r); double a, b; char op = n->v[0];
    bool la = isNum(l, a), rb = isNum(r, b);
    if (la && rb) { switch (op) { case '+': return num(a + b); case '-': return num(a - b); case '*': return num(a * b); case '/': return num(a / b); default: return num(std::pow(a, b)); } }
    if (op == '+') { if (la && a == 0) return r; if (rb && b == 0) return l; }
    if (op == '-' && rb && b == 0) return l;
    if (op == '*') { if ((la && a == 0) || (rb && b == 0)) return num(0); if (la && a == 1) return r; if (rb && b == 1) return l; }
    if (op == '/') { if (la && a == 0) return num(0); if (rb && b == 1) return l; }
    if (op == '^') { if (rb && b == 1) return l; if (rb && b == 0) return num(1); }
    return mk(n->v, l, r);
}
P diff(const P& n, const std::string& x) {
    if (!n->l) return num(n->v == x ? 1 : 0);
    const P &a = n->l, &b = n->r;
    switch (n->v[0]) {
        case '+': case '-': return simp(mk(n->v, diff(a, x), diff(b, x)));
        case '*': return simp(mk("+", mk("*", diff(a, x), b), mk("*", a, diff(b, x))));
        case '/': return simp(mk("/", mk("-", mk("*", diff(a, x), b), mk("*", a, diff(b, x))), mk("^", b, num(2))));
        default: { double c; bool ok = isNum(b, c); assert(ok); (void)ok; return simp(mk("*", mk("*", b, mk("^", a, num(c - 1))), diff(a, x))); }
    }
}
P randomTree(std::mt19937& rng, int depth) {                               // 정수 잎, + - * 만 사용 (정확한 정수 계산)
    if (depth == 0 || rng() % 4 == 0) return mk(std::to_string(rng() % 10));
    return mk(std::string(1, "+-*"[rng() % 3]), randomTree(rng, depth - 1), randomTree(rng, depth - 1));
}

int main() {
    P t = parse("3+4*2");
    assert(postfix(t) == "3 4 2 * +" && prefix(t) == "+ 3 * 4 2" && infix(t) == "3+4*2" && eval(t, {}) == 11);
    assert(infix(parse("(3+4)*2")) == "(3+4)*2" && eval(parse("(3+4)*2"), {}) == 14);
    assert(eval(parse("2^3^2"), {}) == 512 && infix(parse("2^3^2")) == "2^3^2");         // ^ 는 오른쪽 결합
    assert(eval(parse("10-4-3"), {}) == 3 && infix(parse("10-(4-3)")) == "10-(4-3)");  // - 는 왼쪽 결합이라 오른쪽 괄호는 필수
    assert(eval(parse("x*x+y"), {{"x", 4}, {"y", 1}}) == 17);

    std::mt19937 rng(8);
    for (int i = 0; i < 2000; i++) {                                       // 트리 -> 중위 문자열 -> 트리 왕복이 구조까지 같다
        P a = randomTree(rng, 5); std::string s = infix(a); P b = parse(s);
        assert(same(a, b) && eval(a, {}) == eval(b, {}));
    }
    P f = parse("x^3+2*x*y-5");
    P d = diff(f, "x");
    assert(infix(d) == "3*x^2+2*y");                                       // d/dx (x^3 + 2xy - 5) = 3x^2 + 2y
    assert(eval(d, {{"x", 2}, {"y", 3}}) == 18);
    P g = parse("(x+1)/(x-1)"); P dg = diff(g, "x");                       // 몫의 미분은 수치 미분과 비교
    double h = 1e-6, num_ = (eval(g, {{"x", 3 + h}}) - eval(g, {{"x", 3 - h}})) / (2 * h);
    assert(std::fabs(eval(dg, {{"x", 3}}) - num_) < 1e-6 && std::fabs(eval(dg, {{"x", 3}}) + 0.5) < 1e-12);
    std::cout << "ExpressionTree: d/dx(x^3+2*x*y-5) = " << infix(d) << std::endl;
    return 0;
}
// Time Complexity: 구성·계산·출력 O(N), 미분 O(N) (정리 포함)
// Space Complexity: O(N)
```
## SyntaxTree()
### 대표코드
```cpp
#include <cctype>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <cassert>

// 추상 구문 트리(AST): 소스 코드의 "의미 구조"만 남긴 트리. 괄호·세미콜론·중간 문법 규칙(Term, Factor ...)은 사라지고 연산자 우선순위가 트리 모양으로 굳는다.
// 아래는 변수·산술·비교·if·while 만 있는 작은 언어의 토큰화 -> 우선순위 상승 파서 -> AST -> 상수 접기(최적화) -> 인터프리터.  컴파일러의 프런트엔드 전체를 축소한 모양이다
enum Kind { NUM, VAR, BIN, NEG, ASSIGN, WHILE, IF, BLOCK };
struct Node; typedef std::unique_ptr<Node> P;
struct Node { Kind k; long num = 0; std::string s; std::vector<P> c; };
P mk(Kind k, const std::string& s = "", long num = 0) { P n(new Node); n->k = k; n->s = s; n->num = num; return n; }

std::vector<std::string> lex(const std::string& src) {
    std::vector<std::string> t;
    for (size_t i = 0; i < src.size();) {
        char ch = src[i];
        if (isspace((unsigned char)ch)) { i++; continue; }
        if (isalnum((unsigned char)ch) || ch == '_') { size_t j = i; while (j < src.size() && (isalnum((unsigned char)src[j]) || src[j] == '_')) j++; t.push_back(src.substr(i, j - i)); i = j; continue; }
        bool two = false;
        for (const char* op : {"<=", ">=", "==", "!="}) if (src.compare(i, 2, op) == 0) { t.push_back(op); i += 2; two = true; break; }
        if (!two) t.push_back(std::string(1, src[i++]));
    }
    return t;
}
struct Parser {
    std::vector<std::string> t; size_t i = 0;
    std::string peek() const { return i < t.size() ? t[i] : ""; }
    std::string next() { return t[i++]; }
    void expect(const std::string& s) { assert(peek() == s); i++; }
    static int prec(const std::string& op) {
        if (op == "==" || op == "!=") return 1;
        if (op == "<" || op == ">" || op == "<=" || op == ">=") return 2;
        if (op == "+" || op == "-") return 3;
        if (op == "*" || op == "/" || op == "%") return 4;
        return 0;
    }
    P primary() {
        std::string s = next();
        if (isdigit((unsigned char)s[0])) return mk(NUM, "", std::stol(s));
        if (s == "(") { P e = expr(0); expect(")"); return e; }                        // 괄호는 여기서 사라진다
        if (s == "-") { P n = mk(NEG); n->c.push_back(primary()); return n; }
        return mk(VAR, s);
    }
    P expr(int minPrec) {                                                              // 우선순위 상승(precedence climbing)
        P lhs = primary();
        for (;;) {
            std::string op = peek(); int p = prec(op);
            if (p == 0 || p <= minPrec) break;
            i++; P rhs = expr(p);
            P b = mk(BIN, op); b->c.push_back(std::move(lhs)); b->c.push_back(std::move(rhs)); lhs = std::move(b);
        }
        return lhs;
    }
    P stmt() {
        std::string s = peek();
        if (s == "while") { i++; expect("("); P n = mk(WHILE); n->c.push_back(expr(0)); expect(")"); n->c.push_back(stmt()); return n; }
        if (s == "if") {
            i++; expect("("); P n = mk(IF); n->c.push_back(expr(0)); expect(")"); n->c.push_back(stmt());
            if (peek() == "else") { i++; n->c.push_back(stmt()); } return n;
        }
        if (s == "{") { i++; P n = mk(BLOCK); while (peek() != "}") n->c.push_back(stmt()); i++; return n; }
        P n = mk(ASSIGN, next()); expect("="); n->c.push_back(expr(0)); expect(";"); return n;
    }
    P program() { P n = mk(BLOCK); while (i < t.size()) n->c.push_back(stmt()); return n; }
};
P parse(const std::string& src) { Parser p; p.t = lex(src); return p.program(); }

long apply(const std::string& op, long a, long b) {
    if (op == "+") return a + b; if (op == "-") return a - b; if (op == "*") return a * b; if (op == "/") return a / b; if (op == "%") return a % b;
    if (op == "<") return a < b; if (op == ">") return a > b; if (op == "<=") return a <= b; if (op == ">=") return a >= b; if (op == "==") return a == b; return a != b;
}
typedef std::map<std::string, long> Env;
long evalExpr(const Node* n, Env& env) {
    switch (n->k) {
        case NUM: return n->num;
        case VAR: return env[n->s];
        case NEG: return -evalExpr(n->c[0].get(), env);
        default:  { long a = evalExpr(n->c[0].get(), env), b = evalExpr(n->c[1].get(), env); return apply(n->s, a, b); }
    }
}
void exec(const Node* n, Env& env) {
    switch (n->k) {
        case ASSIGN: env[n->s] = evalExpr(n->c[0].get(), env); break;
        case WHILE:  while (evalExpr(n->c[0].get(), env)) exec(n->c[1].get(), env); break;
        case IF:     if (evalExpr(n->c[0].get(), env)) exec(n->c[1].get(), env); else if (n->c.size() > 2) exec(n->c[2].get(), env); break;
        case BLOCK:  for (auto& ch : n->c) exec(ch.get(), env); break;
        default: break;
    }
}
std::string sexpr(const Node* n) {
    std::string r;
    switch (n->k) {
        case NUM: return std::to_string(n->num);
        case VAR: return n->s;
        case NEG: return "(- " + sexpr(n->c[0].get()) + ")";
        case BIN: return "(" + n->s + " " + sexpr(n->c[0].get()) + " " + sexpr(n->c[1].get()) + ")";
        case ASSIGN: return "(= " + n->s + " " + sexpr(n->c[0].get()) + ")";
        case WHILE: return "(while " + sexpr(n->c[0].get()) + " " + sexpr(n->c[1].get()) + ")";
        case IF: r = "(if"; break;
        case BLOCK: r = "(block"; break;
    }
    for (auto& ch : n->c) r += " " + sexpr(ch.get());
    return r + ")";
}
P fold(P n) {                                                              // 상수 접기: 컴파일 시점에 계산 가능한 부분 트리를 숫자 하나로
    for (auto& ch : n->c) ch = fold(std::move(ch));
    if (n->k == BIN && n->c[0]->k == NUM && n->c[1]->k == NUM && !((n->s == "/" || n->s == "%") && n->c[1]->num == 0))
        return mk(NUM, "", apply(n->s, n->c[0]->num, n->c[1]->num));
    if (n->k == NEG && n->c[0]->k == NUM) return mk(NUM, "", -n->c[0]->num);
    return n;
}
int size(const Node* n) { int s = 1; for (auto& ch : n->c) s += size(ch.get()); return s; }
long run(const std::string& src, const std::string& var) { Env env; P ast = parse(src); exec(ast.get(), env); return env[var]; }

int main() {
    assert(sexpr(parse("x = 1 + 2 * (3 + 4);").get()) == "(block (= x (+ 1 (* 2 (+ 3 4)))))");          // 괄호가 없어도 우선순위가 모양에 담겼다
    assert(sexpr(parse("x = (((1)));").get()) == sexpr(parse("x = 1;").get()));                           // 겹괄호는 AST 에서 구분되지 않는다
    assert(sexpr(parse("x = 10 - 4 - 3;").get()) == "(block (= x (- (- 10 4) 3)))");                       // 왼쪽 결합
    assert(sexpr(parse("x = a < b == c;").get()) == "(block (= x (== (< a b) c)))");                       // 비교 연산자의 우선순위 단계
    P ast = parse("x = 2 * 3 + 4 * 5; y = x - -1;"); int before = size(ast.get());
    ast = fold(std::move(ast));
    assert(sexpr(ast.get()) == "(block (= x 26) (= y (- x -1)))" && size(ast.get()) < before);            // 상수 부분식만 접힌다
    assert(run("n = 10; a = 0; b = 1; i = 0; while (i < n) { t = a + b; a = b; b = t; i = i + 1; } result = a;", "result") == 55);   // fib(10)
    assert(run("a = 48; b = 18; while (b != 0) { t = a % b; a = b; b = t; } result = a;", "result") == 6);                           // gcd
    assert(run("n = 27; steps = 0; while (n != 1) { if (n % 2 == 0) { n = n / 2; } else { n = 3 * n + 1; } steps = steps + 1; } result = steps;", "result") == 111);   // 콜라츠
    assert(run("x = 5; if (x > 3) y = 1; else y = 2; if (x > 9) z = 1; else z = 2; result = y * 10 + z;", "result") == 12);
    std::cout << "SyntaxTree: AST nodes for x = 2*3+4*5: " << before << " -> " << size(ast.get()) << " after constant folding" << std::endl;
    return 0;
}
// Time Complexity: 구문 분석 O(N), 실행은 프로그램에 따라 다름
// Space Complexity: O(N)
```
## ParseTree()
### 대표코드
```cpp
#include <cctype>
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <cassert>

// 파스 트리(구체 구문 트리, CST): 문법 규칙을 그대로 따라 만든, 입력의 모든 토큰이 잎으로 남는 트리. 내부 노드는 문법의 비단말 기호다.
// 잎을 왼쪽에서 오른쪽으로 읽으면(yield) 원래 입력이 복원된다는 것이 정의다.  AST 와 달리 괄호와 중간 규칙(Term, Factor)이 그대로 있다.
// 문법:  Expr -> Term (('+'|'-') Term)*   Term -> Factor (('*'|'/') Factor)*   Factor -> NUM | '(' Expr ')'   (재귀 하강 파서)
struct Node; typedef std::unique_ptr<Node> P;
struct Node { std::string label; std::vector<P> kids; };
P nt(const std::string& l) { P n(new Node); n->label = l; return n; }
struct Parser {
    std::vector<std::string> t; size_t i = 0;
    std::string peek() const { return i < t.size() ? t[i] : ""; }
    P leaf() { P n(new Node); n->label = t[i++]; return n; }
    P expr() { P n = nt("Expr"); n->kids.push_back(term()); while (peek() == "+" || peek() == "-") { n->kids.push_back(leaf()); n->kids.push_back(term()); } return n; }
    P term() { P n = nt("Term"); n->kids.push_back(factor()); while (peek() == "*" || peek() == "/") { n->kids.push_back(leaf()); n->kids.push_back(factor()); } return n; }
    P factor() {
        P n = nt("Factor");
        if (peek() == "(") { n->kids.push_back(leaf()); n->kids.push_back(expr()); assert(peek() == ")"); n->kids.push_back(leaf()); }
        else n->kids.push_back(leaf());
        return n;
    }
};
std::vector<std::string> tokens(const std::string& s) {
    std::vector<std::string> t;
    for (size_t i = 0; i < s.size();) {
        if (isspace((unsigned char)s[i])) { i++; continue; }
        if (isdigit((unsigned char)s[i])) { size_t j = i; while (j < s.size() && isdigit((unsigned char)s[j])) j++; t.push_back(s.substr(i, j - i)); i = j; }
        else t.push_back(std::string(1, s[i++]));
    }
    return t;
}
P parse(const std::string& s, std::vector<std::string>& tok) { Parser p; p.t = tok = tokens(s); P root = p.expr(); assert(p.i == p.t.size()); return root; }
std::string show(const Node* n) {
    if (n->kids.empty()) return n->label;
    std::string r = "(" + n->label; for (auto& k : n->kids) r += " " + show(k.get()); return r + ")";
}
void yield(const Node* n, std::vector<std::string>& out) { if (n->kids.empty()) out.push_back(n->label); for (auto& k : n->kids) yield(k.get(), out); }
int count(const Node* n) { int c = 1; for (auto& k : n->kids) c += count(k.get()); return c; }
long evalCst(const Node* n) {                                              // 파스 트리를 아래에서 위로 계산 (규칙 구조가 곧 우선순위)
    if (n->label == "Factor") return n->kids.size() == 1 ? std::stol(n->kids[0]->label) : evalCst(n->kids[1].get());
    long v = evalCst(n->kids[0].get());
    for (size_t j = 1; j < n->kids.size(); j += 2) {
        long r = evalCst(n->kids[j + 1].get()); char op = n->kids[j]->label[0];
        v = op == '+' ? v + r : op == '-' ? v - r : op == '*' ? v * r : v / r;
    }
    return v;
}
std::string toAst(const Node* n) {                                         // 파스 트리 -> AST 의 S-식: 괄호·중간 규칙을 걷어낸다
    if (n->label == "Factor") return n->kids.size() == 1 ? n->kids[0]->label : toAst(n->kids[1].get());
    std::string acc = toAst(n->kids[0].get());
    for (size_t j = 1; j < n->kids.size(); j += 2) acc = "(" + n->kids[j]->label + " " + acc + " " + toAst(n->kids[j + 1].get()) + ")";
    return acc;
}
// 모호한 문법 S -> S S | a : 같은 문자열에 파스 트리가 여러 개.  구간 DP(CYK 방식)로 트리 개수를 센다 -> 카탈란 수
long countTrees(int n) {
    std::vector<std::vector<long>> c(n + 1, std::vector<long>(n + 1, 0));
    for (int i = 0; i < n; i++) c[i][i + 1] = 1;
    for (int len = 2; len <= n; len++) for (int i = 0; i + len <= n; i++) for (int k = i + 1; k < i + len; k++) c[i][i + len] += c[i][k] * c[k][i + len];
    return c[0][n];
}

int main() {
    std::vector<std::string> tok;
    P t = parse("1+2*3", tok);
    assert(show(t.get()) == "(Expr (Term (Factor 1)) + (Term (Factor 2) * (Factor 3)))");
    std::vector<std::string> y; yield(t.get(), y); assert(y == tok);                                 // yield == 입력 토큰열
    for (std::string s : {"(1+2)*3", "10-4-3", "2*(3+(4-1))/3", "((7))"}) {
        P p = parse(s, tok); y.clear(); yield(p.get(), y); assert(y == tok);                         // 괄호까지 모두 잎으로 남는다
        assert(count(p.get()) > 2 * (int)tok.size() - 1 || s == "10-4-3");
    }
    assert(evalCst(parse("1+2*3", tok).get()) == 7 && evalCst(parse("(1+2)*3", tok).get()) == 9 && evalCst(parse("10-4-3", tok).get()) == 3);
    assert(toAst(parse("1+2*3", tok).get()) == "(+ 1 (* 2 3))");
    assert(toAst(parse("(1+2)*3", tok).get()) == "(* (+ 1 2) 3)");
    assert(toAst(parse("10-4-3", tok).get()) == "(- (- 10 4) 3)");
    P big = parse("1+2*3", tok);
    assert(count(big.get()) == 11);                                                                    // 파스 트리 11 노드 vs AST (+ 1 (* 2 3)) 5 노드
    long catalan[] = {1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862};
    for (int n = 1; n <= 10; n++) assert(countTrees(n) == catalan[n - 1]);
    std::cout << "ParseTree: " << show(t.get()) << " ; trees for a^10 under S->SS|a = " << countTrees(10) << std::endl;
    return 0;
}
// Time Complexity: 재귀 하강 파싱 O(N), 모호한 문법의 트리 수 세기 O(N^3)
// Space Complexity: O(N)
```
## DecisionTree()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 의사결정 트리: 내부 노드 = 속성에 대한 질문, 간선 = 답, 잎 = 예측.  "가장 불순도를 많이 줄이는 질문"을 탐욕적으로 고르며 재귀 분할한다.
// (1) ID3: 범주형 속성, 정보 이득 = H(S) - Σ |Sv|/|S| · H(Sv)   (2) CART: 수치형 속성, 임계값 분할과 지니 불순도 2p(1-p)
typedef std::vector<std::string> Row;                                      // 마지막 열 = 레이블
const char* attrName[] = {"Outlook", "Temperature", "Humidity", "Wind"};
double entropy(const std::vector<Row>& rows) {
    std::map<std::string, int> cnt; for (auto& r : rows) cnt[r.back()]++;
    double h = 0; for (auto& kv : cnt) { double p = (double)kv.second / rows.size(); h -= p * std::log2(p); } return h;
}
double gain(const std::vector<Row>& rows, int a) {
    std::map<std::string, std::vector<Row>> parts; for (auto& r : rows) parts[r[a]].push_back(r);
    double g = entropy(rows); for (auto& kv : parts) g -= (double)kv.second.size() / rows.size() * entropy(kv.second); return g;
}
struct Node { int attr = -1; std::string label; std::map<std::string, std::unique_ptr<Node>> kids; };
std::string majority(const std::vector<Row>& rows) {
    std::map<std::string, int> cnt; for (auto& r : rows) cnt[r.back()]++;
    return std::max_element(cnt.begin(), cnt.end(), [](auto& a, auto& b) { return a.second < b.second; })->first;
}
std::unique_ptr<Node> build(const std::vector<Row>& rows, std::set<int> attrs) {
    std::unique_ptr<Node> n(new Node); n->label = majority(rows);
    std::set<std::string> labels; for (auto& r : rows) labels.insert(r.back());
    if (labels.size() == 1 || attrs.empty()) return n;                     // 순수하거나 쓸 속성이 없으면 잎
    int best = -1; double bg = -1; for (int a : attrs) { double g = gain(rows, a); if (g > bg) { bg = g; best = a; } }
    n->attr = best; attrs.erase(best);
    std::map<std::string, std::vector<Row>> parts; for (auto& r : rows) parts[r[best]].push_back(r);
    for (auto& kv : parts) n->kids[kv.first] = build(kv.second, attrs);
    return n;
}
std::string predict(const Node* n, const Row& x) {
    while (n->attr >= 0) { auto it = n->kids.find(x[n->attr]); if (it == n->kids.end()) return n->label; n = it->second.get(); }
    return n->label;
}
std::string show(const Node* n) {
    if (n->attr < 0) return n->label;
    std::string s = std::string(attrName[n->attr]) + "("; bool first = true;
    for (auto& kv : n->kids) { if (!first) s += ","; first = false; s += kv.first + ":" + show(kv.second.get()); }
    return s + ")";
}
// ---- CART: 수치형 속성 2개, 이진 분할 ----
struct Pt { double x[2]; int y; };
struct CNode { int f = -1; double thr = 0; int label = 0; std::unique_ptr<CNode> l, r; };
double gini(int n0, int n1) { int n = n0 + n1; if (!n) return 0; double p = (double)n1 / n; return 2 * p * (1 - p); }
std::unique_ptr<CNode> buildCart(std::vector<Pt>& p, int lo, int hi, int depth, int maxDepth) {
    std::unique_ptr<CNode> n(new CNode); int c1 = 0; for (int i = lo; i < hi; i++) c1 += p[i].y;
    int c0 = (hi - lo) - c1; n->label = c1 > c0;
    if (c0 == 0 || c1 == 0 || depth == maxDepth) return n;
    double parent = gini(c0, c1), best = parent; int bf = -1; double bt = 0;
    for (int f = 0; f < 2; f++) {
        std::sort(p.begin() + lo, p.begin() + hi, [f](const Pt& a, const Pt& b) { return a.x[f] < b.x[f]; });
        int l0 = 0, l1 = 0;
        for (int i = lo; i + 1 < hi; i++) {
            (p[i].y ? l1 : l0)++;
            if (p[i].x[f] == p[i + 1].x[f]) continue;
            int m = i + 1 - lo; double g = (m * gini(l0, l1) + (hi - lo - m) * gini(c0 - l0, c1 - l1)) / (hi - lo);
            if (g < best - 1e-12) { best = g; bf = f; bt = (p[i].x[f] + p[i + 1].x[f]) / 2; }
        }
    }
    if (bf < 0) return n;                                                  // 불순도를 줄이는 분할이 없다
    n->f = bf; n->thr = bt;
    std::sort(p.begin() + lo, p.begin() + hi, [bf](const Pt& a, const Pt& b) { return a.x[bf] < b.x[bf]; });
    int mid = lo; while (mid < hi && p[mid].x[bf] <= bt) mid++;
    n->l = buildCart(p, lo, mid, depth + 1, maxDepth); n->r = buildCart(p, mid, hi, depth + 1, maxDepth);
    return n;
}
int predictCart(const CNode* n, const Pt& q) { while (n->f >= 0) n = q.x[n->f] <= n->thr ? n->l.get() : n->r.get(); return n->label; }
int depthOf(const CNode* n) { return n->f < 0 ? 0 : 1 + std::max(depthOf(n->l.get()), depthOf(n->r.get())); }

int main() {
    std::vector<Row> d = {
        {"Sunny","Hot","High","Weak","No"},       {"Sunny","Hot","High","Strong","No"},    {"Overcast","Hot","High","Weak","Yes"},
        {"Rain","Mild","High","Weak","Yes"},      {"Rain","Cool","Normal","Weak","Yes"},   {"Rain","Cool","Normal","Strong","No"},
        {"Overcast","Cool","Normal","Strong","Yes"}, {"Sunny","Mild","High","Weak","No"},  {"Sunny","Cool","Normal","Weak","Yes"},
        {"Rain","Mild","Normal","Weak","Yes"},    {"Sunny","Mild","Normal","Strong","Yes"}, {"Overcast","Mild","High","Strong","Yes"},
        {"Overcast","Hot","Normal","Weak","Yes"}, {"Rain","Mild","High","Strong","No"}};
    assert(std::fabs(entropy(d) - 0.9403) < 5e-4);                         // 9 Yes / 5 No
    assert(std::fabs(gain(d, 0) - 0.2467) < 5e-4 && std::fabs(gain(d, 1) - 0.0292) < 5e-4);      // 교과서의 정보 이득 값
    assert(std::fabs(gain(d, 2) - 0.1518) < 5e-4 && std::fabs(gain(d, 3) - 0.0481) < 5e-4);
    auto tree = build(d, {0, 1, 2, 3});
    assert(show(tree.get()) == "Outlook(Overcast:Yes,Rain:Wind(Strong:No,Weak:Yes),Sunny:Humidity(High:No,Normal:Yes))");
    for (auto& r : d) assert(predict(tree.get(), r) == r.back());          // 학습 데이터 14/14
    assert(predict(tree.get(), {"Sunny", "Cool", "Normal", "Strong", ""}) == "Yes");
    assert(predict(tree.get(), {"Rain", "Mild", "High", "Strong", ""}) == "No");

    std::mt19937 rng(2024); std::uniform_real_distribution<double> U(0, 10);
    auto make = [&](int n) { std::vector<Pt> v(n); for (auto& p : v) { p.x[0] = U(rng); p.x[1] = U(rng); p.y = (p.x[0] > 5 && p.x[1] < 3); } return v; };
    std::vector<Pt> train = make(2000), test = make(5000);
    auto cart = buildCart(train, 0, train.size(), 0, 5);
    int ok = 0; for (auto& q : test) ok += predictCart(cart.get(), q) == q.y;
    assert(depthOf(cart.get()) <= 3 && ok >= 0.98 * test.size());          // 두 임계값(x0>5, x1<3)을 찾아낸다
    for (auto& q : train) assert(predictCart(cart.get(), q) == q.y);
    std::cout << "DecisionTree: ID3 = " << show(tree.get()) << " ; CART depth " << depthOf(cart.get()) << ", test accuracy " << 100.0 * ok / test.size() << "%" << std::endl;
    return 0;
}
// Time Complexity: ID3 O(속성 수 × N × 깊이), CART 노드당 O(속성 수 × N log N)
// Space Complexity: O(N)
```
## MerkleTree()
### 대표코드
```cpp
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 머클 트리: 잎 = 데이터 블록의 해시, 내부 노드 = 두 자식 해시를 이은 것의 해시.  루트 해시 32바이트 하나가 전체 데이터의 지문이다.
// 어느 한 블록이 진짜인지는 "루트까지 형제 해시 log2 n 개(감사 경로)"만 받으면 O(log n) 에 검증된다 (Git, 비트코인, 인증서 투명성 로그, 분산 DB 의 동기화).
// 여기서는 RFC 6962(인증서 투명성)의 정의를 따른다: 잎 해시 = H(0x00 || 데이터), 내부 = H(0x01 || 왼쪽 || 오른쪽), n 개를 "n 보다 작은 가장 큰 2의 거듭제곱 k" 에서 둘로 나눈다.
// 접두 바이트(도메인 분리)와 "마지막 노드 복제 없음" 이 비트코인식 단순 구성의 취약점(잎과 내부 노드 혼동, [a,b,c] == [a,b,c,c])을 막는다
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
std::string sha256raw(const std::string& msg) {                            // SHA-256: 32바이트 원시 다이제스트
    static uint32_t K[64], H0[8]; static bool init = false;
    if (!init) {
        std::vector<uint32_t> pr; for (uint32_t p = 2; pr.size() < 64; p++) { bool ok = true; for (uint32_t q : pr) if (p % q == 0) { ok = false; break; } if (ok) pr.push_back(p); }
        for (int i = 0; i < 64; i++) { long double c = cbrtl((long double)pr[i]); K[i] = (uint32_t)((c - floorl(c)) * 4294967296.0L); }
        for (int i = 0; i < 8; i++)  { long double s = sqrtl((long double)pr[i]); H0[i] = (uint32_t)((s - floorl(s)) * 4294967296.0L); }
        init = true;
    }
    uint32_t H[8]; for (int i = 0; i < 8; i++) H[i] = H0[i];
    std::vector<uint8_t> m(msg.begin(), msg.end()); uint64_t bits = (uint64_t)msg.size() * 8;
    m.push_back(0x80); while (m.size() % 64 != 56) m.push_back(0);
    for (int i = 7; i >= 0; i--) m.push_back((bits >> (8 * i)) & 0xff);
    for (size_t off = 0; off < m.size(); off += 64) {
        uint32_t w[64];
        for (int i = 0; i < 16; i++) w[i] = m[off + 4*i] << 24 | m[off + 4*i + 1] << 16 | m[off + 4*i + 2] << 8 | m[off + 4*i + 3];
        for (int i = 16; i < 64; i++) {
            uint32_t s0 = rotr(w[i-15], 7) ^ rotr(w[i-15], 18) ^ (w[i-15] >> 3), s1 = rotr(w[i-2], 17) ^ rotr(w[i-2], 19) ^ (w[i-2] >> 10);
            w[i] = w[i-16] + s0 + w[i-7] + s1;
        }
        uint32_t a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
        for (int i = 0; i < 64; i++) {
            uint32_t t1 = h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i];
            uint32_t t2 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
            h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
        }
        H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
    std::string out(32, 0); for (int i = 0; i < 8; i++) for (int j = 0; j < 4; j++) out[4 * i + j] = (char)((H[i] >> (24 - 8 * j)) & 0xff);
    return out;
}
std::string hex(const std::string& s) { static const char* d = "0123456789abcdef"; std::string r; for (unsigned char c : s) { r += d[c >> 4]; r += d[c & 15]; } return r; }

typedef std::string Hash; typedef std::vector<std::string> Data;
Hash leafHash(const std::string& d) { return sha256raw(std::string(1, '\x00') + d); }
Hash nodeHash(const Hash& l, const Hash& r) { return sha256raw(std::string(1, '\x01') + l + r); }
size_t lpow2(size_t n) { size_t k = 1; while (k * 2 < n) k *= 2; return k; }            // n 보다 작은 가장 큰 2의 거듭제곱 (n >= 2)
Hash mth(const Data& D, size_t lo, size_t hi) {                             // Merkle Tree Hash (루트)
    size_t n = hi - lo; if (n == 0) return sha256raw(""); if (n == 1) return leafHash(D[lo]);
    size_t k = lpow2(n); return nodeHash(mth(D, lo, lo + k), mth(D, lo + k, hi));
}
void auditPath(const Data& D, size_t m, size_t lo, size_t hi, std::vector<Hash>& out) {   // 잎 m 에서 루트까지의 형제 해시들 (아래 -> 위)
    size_t n = hi - lo; if (n == 1) return; size_t k = lpow2(n);
    if (m < k) { auditPath(D, m, lo, lo + k, out); out.push_back(mth(D, lo + k, hi)); }
    else       { auditPath(D, m - k, lo + k, hi, out); out.push_back(mth(D, lo, lo + k)); }
}
bool rootFromPath(size_t m, size_t n, const Hash& leaf, const std::vector<Hash>& p, size_t& end, Hash& out) {
    if (n == 1) { out = leaf; return true; }
    if (end == 0) return false;
    const Hash& sib = p[--end]; size_t k = lpow2(n); Hash sub;
    if (m < k) { if (!rootFromPath(m, k, leaf, p, end, sub)) return false; out = nodeHash(sub, sib); }
    else       { if (!rootFromPath(m - k, n - k, leaf, p, end, sub)) return false; out = nodeHash(sib, sub); }
    return true;
}
bool verify(const Hash& root, size_t n, size_t m, const std::string& data, const std::vector<Hash>& path) {
    size_t end = path.size(); Hash r; return m < n && rootFromPath(m, n, leafHash(data), path, end, r) && end == 0 && r == root;
}
Hash naiveRoot(std::vector<Hash> level) {                                   // 비트코인식: 접두 없음, 홀수면 마지막 복제
    while (level.size() > 1) { if (level.size() % 2) level.push_back(level.back()); std::vector<Hash> nx; for (size_t i = 0; i < level.size(); i += 2) nx.push_back(sha256raw(level[i] + level[i + 1])); level = nx; }
    return level[0];
}

int main() {
    assert(hex(sha256raw("abc")) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    const char* expect[] = {                                                // 독립 구현(Python hashlib)으로 구한 "leaf0".."leaf8" 의 n = 0..9 루트
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "e6c410a9745b0151d82d1a9f007b81f378a1588c3fb63dc634a2ab001379c3d2",
        "82bbd1c5de08394573f035ab3871ffaa6d8aba80baf47c7b28fb2b167f18464e", "f1aed069e1b79c5f12193e715059c468eff1559a5c989c6d7c46bc29f4f84f6c",
        "86f9ec25a8a2b32a4bd733e04c213de63c8b0655bcb887b75cfd8b02691be0e5", "2f4e0d79b7e066069be4d391a858023d0acd245505ab6913a8fd69726b65741d",
        "2bec773a6ce6d83151210fdd24bea43e7c4c94902811ce6124a21c71951860bd", "4b6939132387c5bf27ebaf5ac122810ce866eb0c7bf44082364b35c06f713aa6",
        "d12334b61aa2f244f11754c40896641551d64cd5c79fa0f9760d2ec3079d1834", "d6fe82371b0d1ef3c1a646efa98551e16d7c07bb83c0b9fe97136f471dd45f82"};
    Data D; for (int i = 0; i < 40; i++) D.push_back("leaf" + std::to_string(i));
    for (int n = 0; n <= 9; n++) assert(hex(mth(D, 0, n)) == expect[n]);
    for (size_t n = 1; n <= 40; n++) {                                      // 모든 (크기, 잎) 쌍에서 감사 경로가 검증되고 길이는 ceil(log2 n) 이하
        Hash root = mth(D, 0, n);
        for (size_t m = 0; m < n; m++) {
            std::vector<Hash> path; auditPath(D, m, 0, n, path);
            assert(path.size() <= (size_t)std::ceil(std::log2((double)n)) && verify(root, n, m, D[m], path));
            assert(!verify(root, n, m, D[m] + "x", path));                  // 데이터 변조
            if (n > 1) { auto bad = path; bad[0][0] ^= 1; assert(!verify(root, n, m, D[m], bad)); }            // 경로 변조
            if (n > 1) assert(!verify(root, n, (m + 1) % n, D[m], path));   // 엉뚱한 위치 주장
        }
    }
    // 단순 구성의 약점: [a,b,c] 와 [a,b,c,c] 가 같은 루트 / 내부 노드가 잎으로 위장
    std::vector<Hash> abc = {sha256raw("a"), sha256raw("b"), sha256raw("c")}, abcc = abc; abcc.push_back(abc[2]);
    assert(naiveRoot(abc) == naiveRoot(abcc));
    assert(mth({"a", "b", "c"}, 0, 3) != mth({"a", "b", "c", "c"}, 0, 4));
    std::vector<Hash> ab = {sha256raw("a"), sha256raw("b")};
    assert(sha256raw(ab[0] + ab[1]) == naiveRoot(ab));                    // 두 해시를 이은 "데이터" 한 개짜리 트리(잎 해시 = H(데이터))가 둘짜리 트리와 같은 루트
    assert(mth({leafHash("a") + leafHash("b")}, 0, 1) != mth({"a", "b"}, 0, 2));       // 접두 바이트가 이를 막는다
    std::cout << "MerkleTree: root(8 leaves) = " << hex(mth(D, 0, 8)).substr(0, 16) << "..., proof length for 40 leaves <= " << std::ceil(std::log2(40.0)) << std::endl;
    return 0;
}
// Time Complexity: 루트 계산 O(N) 해시, 감사 경로 생성·검증 O(log N) (경로 생성은 부분 트리 해시 재계산 포함 O(N))
// Space Complexity: 증명 O(log N)
```
## IntervalTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <memory>
#include <random>
#include <tuple>
#include <vector>
#include <cassert>

// 구간 트리(증강 BST): 구간 [lo, hi] 들을 lo 순으로 BST 에 두고, 각 노드에 "부분 트리 안의 최대 hi(mx)" 를 덧붙인다 (CLRS 14장).
// "질의 구간과 겹치는 구간이 있는가" 는 왼쪽 부분 트리의 mx >= 질의.lo 이면 왼쪽에 겹침 후보가 있다는 사실로 한 길을 따라 내려가며 O(log n) 에 답한다.
// 모든 겹침을 찾는 연산은 mx 가 질의.lo 보다 작은 부분 트리를 통째로 건너뛰어 O(k + log n) 에 가깝다.  균형은 트레이프로 잡는다 (분할/병합이 mx 를 쉽게 유지)
struct Node { int lo, hi, mx, id; unsigned pri; Node *l = nullptr, *r = nullptr; };
typedef std::tuple<int, int, int> Key;
Key key(const Node* n) { return Key(n->lo, n->hi, n->id); }
void upd(Node* t) { t->mx = t->hi; if (t->l) t->mx = std::max(t->mx, t->l->mx); if (t->r) t->mx = std::max(t->mx, t->r->mx); }
void split(Node* t, const Key& k, bool leq, Node*& a, Node*& b) {          // a: 키 < k (leq 이면 <= k), b: 나머지
    if (!t) { a = b = nullptr; return; }
    if (leq ? key(t) <= k : key(t) < k) { a = t; split(t->r, k, leq, t->r, b); } else { b = t; split(t->l, k, leq, a, t->l); }
    upd(t);
}
Node* merge(Node* a, Node* b) {
    if (!a) return b; if (!b) return a;
    if (a->pri > b->pri) { a->r = merge(a->r, b); upd(a); return a; }
    b->l = merge(a, b->l); upd(b); return b;
}
struct IntervalTree {
    Node* root = nullptr; std::vector<std::unique_ptr<Node>> pool; std::mt19937 rng{12345};
    void insert(int lo, int hi, int id) {
        pool.emplace_back(new Node{lo, hi, hi, id, (unsigned)rng()}); Node* n = pool.back().get();
        Node *a, *b; split(root, key(n), false, a, b); root = merge(merge(a, n), b);
    }
    void erase(int lo, int hi, int id) {
        Key k(lo, hi, id); Node *a, *b, *m, *c; split(root, k, false, a, b); split(b, k, true, m, c); root = merge(a, c);   // m 은 정확히 그 구간 하나
    }
    Node* anyOverlap(int lo, int hi) const {                               // 겹치는 구간 하나 (없으면 null)
        Node* t = root;
        while (t) { if (t->lo <= hi && lo <= t->hi) return t; t = (t->l && t->l->mx >= lo) ? t->l : t->r; }
        return nullptr;
    }
    void allOverlaps(const Node* t, int lo, int hi, std::vector<int>& out, long& visited) const {
        if (!t || t->mx < lo) return;                                       // 이 부분 트리의 어떤 구간도 lo 에 닿지 못한다
        visited++;
        allOverlaps(t->l, lo, hi, out, visited);
        if (t->lo <= hi && lo <= t->hi) out.push_back(t->id);
        if (t->lo <= hi) allOverlaps(t->r, lo, hi, out, visited);           // 오른쪽은 모두 lo' >= t->lo 이므로 t->lo > hi 면 전부 제외
    }
};
bool checkMx(const Node* t) { if (!t) return true; int m = t->hi; if (t->l) m = std::max(m, t->l->mx); if (t->r) m = std::max(m, t->r->mx); return m == t->mx && checkMx(t->l) && checkMx(t->r); }

int main() {
    std::mt19937 rng(99); IntervalTree T; struct Iv { int lo, hi; bool alive; }; std::vector<Iv> iv;
    for (int i = 0; i < 5000; i++) { int lo = rng() % 100000, len = rng() % 60 + 1; iv.push_back({lo, lo + len, true}); T.insert(lo, lo + len, i); }
    assert(checkMx(T.root));
    auto brute = [&](int lo, int hi) { std::vector<int> r; for (size_t i = 0; i < iv.size(); i++) if (iv[i].alive && iv[i].lo <= hi && lo <= iv[i].hi) r.push_back(i); return r; };
    long visitedTotal = 0; int queries = 1000;
    for (int round = 0; round < 2; round++) {
        for (int q = 0; q < queries; q++) {
            int lo = rng() % 100000, hi = lo + rng() % 40; std::vector<int> got; long vis = 0;
            T.allOverlaps(T.root, lo, hi, got, vis); visitedTotal += vis; std::sort(got.begin(), got.end());
            auto want = brute(lo, hi); assert(got == want);
            Node* any = T.anyOverlap(lo, hi); assert((any != nullptr) == !want.empty());
            if (any) assert(any->lo <= hi && lo <= any->hi);
            int x = rng() % 100000; assert((T.anyOverlap(x, x) != nullptr) == !brute(x, x).empty());      // 점 질의(stabbing)
        }
        if (round == 0) {                                                   // 절반을 삭제한 뒤 같은 검사를 반복
            for (int i = 0; i < 5000; i += 2) { T.erase(iv[i].lo, iv[i].hi, i); iv[i].alive = false; }
            assert(checkMx(T.root));
        }
    }
    double avg = (double)visitedTotal / (2 * queries);
    assert(avg < 200);                                                      // 5000 개를 모두 훑는 대신 평균 수십~수백 노드만 방문
    std::cout << "IntervalTree: avg visited nodes per query = " << avg << " (brute force: 5000)" << std::endl;
    return 0;
}
// Time Complexity: 삽입·삭제 O(log N) 기대, 겹침 하나 O(log N), 겹침 k 개 모두 O(k log N) 이내
// Space Complexity: O(N)
```
## RopeTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 로프 트리(트리 관점의 요약, 정본은 String.md Part 4): 긴 문자열을 이진 트리로 표현하고 내부 노드에 "왼쪽 부분 트리 전체 길이(weight)"를 기록한다 — 색인은 weight 로 좌우를 고르며 내려가는 O(깊이), 연결은 새 루트 하나를 만드는 O(1).
//  그냥 이어 붙이면 트리가 사슬이 되어 깊이가 n 이 되므로 AVL 식 *join* 으로 높이를 O(log n) 에 묶는다.  노드는 불변(shared_ptr<const>) → 편집해도 옛 버전이 그대로이고 새 노드는 O(log n) 개뿐.
//  ① 예제 ② std::string 과 무작위 편집(삽입·삭제·부분 문자열·양쪽 붙이기) 3000 번을 대조하고 매 단계 AVL 불변식·높이 ≤ 1.45 log2(잎 수) + 2  ③ 옛 버전 150 개가 끝까지 그대로
//  ④ 순진한 연결(깊이 n − 1) 대 join(깊이 ≤ 30): 2 만 번 이어 붙이기  ⑤ 100 만 글자 문서의 편집 1000 번.
const size_t LEAF = 16;
struct Node; typedef std::shared_ptr<const Node> P;
struct Node { P l, r; std::string s; size_t size; int height; };                                                // 잎: s 사용(≤ LEAF), 내부: l, r
size_t sizeOf(const P& n) { return n ? n->size : 0; }
int heightOf(const P& n) { return n ? n->height : -1; }
bool isLeaf(const P& n) { return !n->l && !n->r; }
P leaf(std::string s) { size_t n = s.size(); return std::make_shared<const Node>(Node{nullptr, nullptr, std::move(s), n, 0}); }
P node(P l, P r) { size_t n = sizeOf(l) + sizeOf(r); int h = 1 + std::max(heightOf(l), heightOf(r)); return std::make_shared<const Node>(Node{std::move(l), std::move(r), "", n, h}); }      // size(l) = weight
P balance(const P& l, const P& r) {                                                                              // 높이 차 ≤ 2 인 두 트리를 AVL 회전으로 합친다
    if (heightOf(l) > heightOf(r) + 1) { if (heightOf(l->l) >= heightOf(l->r)) return node(l->l, node(l->r, r)); return node(node(l->l, l->r->l), node(l->r->r, r)); }
    if (heightOf(r) > heightOf(l) + 1) { if (heightOf(r->r) >= heightOf(r->l)) return node(node(l, r->l), r->r); return node(node(l, r->l->l), node(r->l->r, r->r)); }
    return node(l, r);
}
P join(const P& a, const P& b) {                                                                                 // a + b, O(|h(a) − h(b)| + 1)
    if (!a) return b; if (!b) return a;
    if (isLeaf(a) && isLeaf(b) && a->size + b->size <= LEAF) return leaf(a->s + b->s);
    int ha = heightOf(a), hb = heightOf(b);
    if (ha > hb + 1) return balance(a->l, join(a->r, b));
    if (hb > ha + 1) return balance(join(a, b->l), b->r);
    return node(a, b);
}
std::pair<P, P> split(const P& n, size_t i) {                                                                    // [0, i) 와 [i, size)
    if (!n || i == 0) return {nullptr, n}; if (i >= n->size) return {n, nullptr};
    if (isLeaf(n)) return {leaf(n->s.substr(0, i)), leaf(n->s.substr(i))};
    size_t w = sizeOf(n->l); if (i < w) { auto t = split(n->l, i); return {t.first, join(t.second, n->r)}; }
    if (i == w) return {n->l, n->r}; auto t = split(n->r, i - w); return {join(n->l, t.first), t.second};
}
P fromString(const std::string& s) { P r; for (size_t i = 0; i < s.size(); i += LEAF) r = join(r, leaf(s.substr(i, LEAF))); return r; }
char at(const P& n, size_t i) { const Node* c = n.get(); while (c->l || c->r) { size_t w = sizeOf(c->l); if (i < w) c = c->l.get(); else { i -= w; c = c->r.get(); } } return c->s[i]; }          // weight 로 내려가는 반복
std::string str(const P& n) { std::string out; std::vector<const Node*> st; if (n) st.push_back(n.get()); while (!st.empty()) { const Node* c = st.back(); st.pop_back(); if (!c->l && !c->r) out += c->s; else { if (c->r) st.push_back(c->r.get()); if (c->l) st.push_back(c->l.get()); } } return out; }
P insert(const P& n, size_t pos, const std::string& s) { auto t = split(n, pos); return join(join(t.first, fromString(s)), t.second); }
P erase(const P& n, size_t pos, size_t len) { auto a = split(n, pos); auto b = split(a.second, len); return join(a.first, b.second); }
P substr(const P& n, size_t pos, size_t len) { auto a = split(n, pos); return split(a.second, len).first; }
bool check(const P& n, size_t& leaves) {                                                                         // 불변식: 크기·높이 정확, AVL 균형, 잎은 1..LEAF 글자
    if (!n) return true; if (isLeaf(n)) { ++leaves; return n->height == 0 && n->size == n->s.size() && n->size >= 1 && n->size <= LEAF; }
    return n->l && n->r && n->size == n->l->size + n->r->size && n->height == 1 + std::max(n->l->height, n->r->height) && std::abs(n->l->height - n->r->height) <= 1 && check(n->l, leaves) && check(n->r, leaves); }

int main() {
    P doc = join(join(leaf("Hello, "), leaf("tree ")), leaf("world!")); assert(sizeOf(doc) == 18 && at(doc, 0) == 'H' && at(doc, 7) == 't' && at(doc, 12) == 'w' && at(doc, 17) == '!');           // ①
    P edited = insert(doc, 7, "binary "); assert(str(edited) == "Hello, binary tree world!" && str(doc) == "Hello, tree world!");                                                      // 원본 그대로
    std::mt19937 rng(55); std::string ref; P rope; std::vector<std::pair<P, std::string>> history;               // ②
    auto randStr = [&](size_t n) { std::string s(n, 'a'); for (char& c : s) c = (char)('a' + rng() % 26); return s; };
    for (int op = 0; op < 3000; ++op) {
        int t = (int)(rng() % 6); size_t n = ref.size();
        if (t <= 1 || n < 5) { size_t pos = rng() % (n + 1); std::string x = randStr(rng() % 60); rope = insert(rope, pos, x); ref.insert(pos, x); }
        else if (t == 2) { size_t pos = rng() % n, len = rng() % std::min<size_t>(60, n - pos + 1); rope = erase(rope, pos, len); ref.erase(pos, len); }
        else if (t == 3) { std::string x = randStr(1 + rng() % 30); rope = join(rope, fromString(x)); ref += x; }
        else if (t == 4) { std::string x = randStr(1 + rng() % 30); rope = join(fromString(x), rope); ref = x + ref; }
        else { size_t pos = rng() % n, len = rng() % (n - pos + 1); assert(str(substr(rope, pos, len)) == ref.substr(pos, len)); }
        size_t leaves = 0; assert(sizeOf(rope) == ref.size() && check(rope, leaves)); if (rope) assert(rope->height <= 1.45 * std::log2((double)std::max<size_t>(leaves, 1)) + 2);
        if (!ref.empty()) { size_t i = rng() % ref.size(); assert(at(rope, i) == ref[i]); } if (op % 20 == 0) history.emplace_back(rope, ref); if (op % 300 == 0) assert(str(rope) == ref); }
    assert(str(rope) == ref); for (auto& h : history) assert(str(h.first) == h.second);                         // ③
    int balHeight = 0;
    { P chain, bal; for (int i = 0; i < 20000; ++i) { chain = chain ? node(chain, leaf("x")) : leaf("x"); bal = join(bal, leaf("x")); }                                                     // ④
      balHeight = bal->height; assert(chain->height == 19999 && bal->height <= 30 && sizeOf(chain) == 20000 && str(bal) == std::string(20000, 'x') && at(chain, 0) == 'x'); }
    { std::string big = randStr(1000000); P r = fromString(big); size_t leaves = 0; assert(check(r, leaves) && r->height <= 28);                                                           // ⑤
      for (int op = 0; op < 1000; ++op) { size_t pos = rng() % big.size(); if (rng() % 2) { std::string x = randStr(1 + rng() % 100); r = insert(r, pos, x); big.insert(pos, x); } else { size_t len = rng() % std::min<size_t>(200, big.size() - pos + 1); r = erase(r, pos, len); big.erase(pos, len); }
        assert(sizeOf(r) == big.size()); for (int k = 0; k < 10; ++k) { size_t i = rng() % big.size(); assert(at(r, i) == big[i]); } }
      leaves = 0; assert(check(r, leaves) && str(r) == big);
      std::cout << "RopeTree: " << history.size() << " historical versions stayed intact, AVL invariants held after every edit, naive concatenation had height 19999 versus " << balHeight << " for join, and a 10^6-character document survived 1000 edits (height " << r->height << ")" << std::endl; }
    return 0;
}
// Time Complexity: 색인·분할·삽입·삭제·붙이기 O(log N)
// Space Complexity: O(N), 편집마다 O(log N) 새 노드
```
## RTree()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// R-트리: 2차원 이상 "사각형"(MBR, 최소 외접 사각형)을 B-트리처럼 균형 있게 모은 공간 색인 (PostGIS, SQLite R*Tree, 지도·게임 충돌 검사).
// 내부 노드의 각 항목 = (자식 노드 전체를 덮는 사각형, 자식).  질의 사각형과 겹치지 않는 항목은 그 아래를 통째로 건너뛴다.
// 삽입: 사각형이 "가장 적게 커지는" 자식으로 내려가고, 노드가 M+1 개가 되면 이차(quadratic) 분할 — 가장 낭비가 큰 한 쌍을 씨앗으로 삼아 나머지를 더 이득인 쪽에 배정 (각 쪽 최소 m 개 보장)
struct Rect { int x1, y1, x2, y2; };
long area(const Rect& r) { return (long)(r.x2 - r.x1) * (r.y2 - r.y1); }
Rect unite(const Rect& a, const Rect& b) { return {std::min(a.x1, b.x1), std::min(a.y1, b.y1), std::max(a.x2, b.x2), std::max(a.y2, b.y2)}; }
bool inter(const Rect& a, const Rect& b) { return a.x1 <= b.x2 && b.x1 <= a.x2 && a.y1 <= b.y2 && b.y1 <= a.y2; }
long enlarge(const Rect& r, const Rect& add) { return area(unite(r, add)) - area(r); }
struct Node;
struct Entry { Rect r; Node* child; int id; };
struct Node { bool leaf; std::vector<Entry> e; };
const int M = 4, m = 2;
Rect mbr(const Node* n) { Rect r = n->e[0].r; for (auto& x : n->e) r = unite(r, x.r); return r; }
Node* splitNode(Node* n) {                                                 // n 은 M+1 개를 가진다. 한 그룹은 n 에 남기고 다른 그룹을 새 노드로
    auto E = n->e; int a = 0, b = 1; long worst = -1;
    for (size_t i = 0; i < E.size(); i++) for (size_t j = i + 1; j < E.size(); j++) {
        long waste = area(unite(E[i].r, E[j].r)) - area(E[i].r) - area(E[j].r);
        if (waste > worst) { worst = waste; a = i; b = j; }
    }
    std::vector<Entry> g1 = {E[a]}, g2 = {E[b]}, rest; Rect r1 = E[a].r, r2 = E[b].r;
    for (size_t i = 0; i < E.size(); i++) if ((int)i != a && (int)i != b) rest.push_back(E[i]);
    while (!rest.empty()) {
        if (g1.size() + rest.size() <= (size_t)m) { for (auto& x : rest) g1.push_back(x); break; }        // 최소 개수 보장
        if (g2.size() + rest.size() <= (size_t)m) { for (auto& x : rest) g2.push_back(x); break; }
        int pick = 0; long bestDiff = -1;                                   // 두 그룹에 대한 선호 차이가 가장 큰 항목부터
        for (size_t i = 0; i < rest.size(); i++) { long d = std::labs(enlarge(r1, rest[i].r) - enlarge(r2, rest[i].r)); if (d > bestDiff) { bestDiff = d; pick = i; } }
        Entry x = rest[pick]; rest.erase(rest.begin() + pick);
        long d1 = enlarge(r1, x.r), d2 = enlarge(r2, x.r);
        bool to1 = d1 < d2 || (d1 == d2 && (area(r1) < area(r2) || (area(r1) == area(r2) && g1.size() <= g2.size())));
        if (to1) { g1.push_back(x); r1 = unite(r1, x.r); } else { g2.push_back(x); r2 = unite(r2, x.r); }
    }
    n->e = g1; return new Node{n->leaf, g2};
}
Node* insertRec(Node* n, const Entry& e) {                                 // 분할이 일어나면 새 형제를 돌려준다
    if (n->leaf) n->e.push_back(e);
    else {
        int best = 0; long bd = LONG_MAX, ba = LONG_MAX;
        for (size_t i = 0; i < n->e.size(); i++) {
            long d = enlarge(n->e[i].r, e.r), a = area(n->e[i].r);
            if (d < bd || (d == bd && a < ba)) { best = i; bd = d; ba = a; }
        }
        Node* s = insertRec(n->e[best].child, e);
        n->e[best].r = mbr(n->e[best].child);
        if (s) n->e.push_back(Entry{mbr(s), s, -1});
    }
    return (int)n->e.size() > M ? splitNode(n) : nullptr;
}
void insert(Node*& root, const Rect& r, int id) {
    Node* s = insertRec(root, Entry{r, nullptr, id});
    if (s) root = new Node{false, {Entry{mbr(root), root, -1}, Entry{mbr(s), s, -1}}};               // 루트 분할 -> 높이 +1
}
void search(const Node* n, const Rect& q, std::vector<int>& out, long& visited) {
    visited++;
    for (auto& x : n->e) if (inter(x.r, q)) { if (n->leaf) out.push_back(x.id); else search(x.child, q, out, visited); }
}
int check(const Node* n, bool isRoot, int& count) {                        // 높이(잎=1), 위반이면 -1: 항목 수, 같은 깊이, 부모의 사각형 == 자식의 MBR
    if (n->e.empty() || (int)n->e.size() > M || (!isRoot && (int)n->e.size() < m)) return -1;
    if (n->leaf) { count += n->e.size(); return 1; }
    int h = -2;
    for (auto& x : n->e) {
        Rect t = mbr(x.child); if (t.x1 != x.r.x1 || t.y1 != x.r.y1 || t.x2 != x.r.x2 || t.y2 != x.r.y2) return -1;
        int ch = check(x.child, false, count); if (ch < 0 || (h != -2 && ch != h)) return -1; h = ch;
    }
    return h + 1;
}
void destroy(Node* n) { if (!n->leaf) for (auto& x : n->e) destroy(x.child); delete n; }

int main() {
    std::mt19937 rng(17); Node* root = new Node{true, {}}; std::vector<Rect> rects; int N = 4000;
    for (int i = 0; i < N; i++) {
        int x = rng() % 10000, y = rng() % 10000, w = rng() % 100 + 1, h = rng() % 100 + 1;
        rects.push_back({x, y, x + w, y + h}); insert(root, rects.back(), i);
        if (i % 500 == 0) { int c = 0; assert(check(root, true, c) > 0 && c == i + 1); }
    }
    int cnt = 0; int height = check(root, true, cnt); assert(height > 0 && cnt == N);
    assert(height <= std::log2((double)N));                                // 모든 노드가 m=2 개 이상이므로 높이 <= log2 N
    long visitedTotal = 0;
    for (int q = 0; q < 400; q++) {
        int x = rng() % 10000, y = rng() % 10000; Rect w{x, y, x + (int)(rng() % 600), y + (int)(rng() % 600)};
        std::vector<int> got; long vis = 0; search(root, w, got, vis); visitedTotal += vis; std::sort(got.begin(), got.end());
        std::vector<int> want; for (int i = 0; i < N; i++) if (inter(rects[i], w)) want.push_back(i);
        assert(got == want);                                               // 브루트 포스와 같은 결과
    }
    double avg = (double)visitedTotal / 400;
    assert(avg < N / 8.0);                                                 // 전체 사각형 4000 개 대신 일부 노드만 방문
    std::cout << "RTree: height " << height << ", avg nodes visited per window query " << avg << " (rects: " << N << ")" << std::endl;
    destroy(root); return 0;
}
// Time Complexity: 삽입 O(M log_m N), 검색은 겹침 정도에 따라 O(log N) ~ O(N)
// Space Complexity: O(N)
```
## VanEmdeBoasTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 반 엠데 보아스(vEB) 트리: 정수 집합 U = 2^bits 를 지원하면서 insert/erase/member/min/max/successor/predecessor 가 모두 O(log log U).
// U 를 √U 개씩 √U 칸으로 나눠 "상위 비트 = 클러스터 번호, 하위 비트 = 클러스터 안 위치"로 재귀하고, 비어 있지 않은 클러스터를 다른 vEB(summary)로 관리한다.
// 두 가지 요령: (1) 최솟값은 클러스터에 넣지 않고 노드에 따로 두어 빈 클러스터 삽입을 O(1) 로, (2) min/max 를 O(1) 로 알고 있어 재귀 호출이 항상 하나뿐 -> T(U) = T(√U) + O(1).
// 클러스터는 필요할 때만 만들어(lazy) U = 2^24 도 메모리를 적게 쓴다
long calls = 0;                                                            // 재귀 호출 수 측정
struct VEB {
    int bits, lowBits, highBits; long mn = -1, mx = -1; VEB* summary = nullptr; std::vector<VEB*> cl;
    explicit VEB(int b) : bits(b), lowBits(b / 2), highBits(b - b / 2) { if (b > 1) cl.assign(1L << highBits, nullptr); }
    ~VEB() { delete summary; for (VEB* c : cl) delete c; }
    long high(long x) const { return x >> lowBits; }
    long low(long x) const { return x & ((1L << lowBits) - 1); }
    long index(long h, long l) const { return (h << lowBits) | l; }
    bool empty() const { return mn < 0; }
    bool member(long x) const {
        calls++; if (x == mn || x == mx) return true;
        if (bits == 1) return false;
        VEB* c = cl[high(x)]; return c && c->member(low(x));
    }
    void insert(long x) {
        calls++;
        if (mn < 0) { mn = mx = x; return; }
        if (x == mn || x == mx) return;
        if (x < mn) std::swap(x, mn);                                      // 새 최솟값은 이 노드에 두고, 밀려난 옛 최솟값을 아래로 내려보낸다
        if (bits > 1) {
            VEB*& c = cl[high(x)]; if (!c) c = new VEB(lowBits);
            if (c->empty()) { if (!summary) summary = new VEB(highBits); summary->insert(high(x)); }   // 빈 클러스터에 넣을 때는 아래 insert 가 O(1)
            c->insert(low(x));
        }
        if (x > mx) mx = x;
    }
    void erase(long x) {                                                   // x 가 집합에 있어야 한다
        calls++;
        if (mn == mx) { mn = mx = -1; return; }
        if (bits == 1) { mn = mx = (x == 0 ? 1 : 0); return; }
        if (x == mn) { long fc = summary->mn; x = index(fc, cl[fc]->mn); mn = x; }          // 최솟값을 지우려면 다음 최솟값을 끌어올린다
        long h = high(x); cl[h]->erase(low(x));
        if (cl[h]->empty()) {
            delete cl[h]; cl[h] = nullptr; summary->erase(h);
            if (x == mx) { long sm = summary->mx; mx = sm < 0 ? mn : index(sm, cl[sm]->mx); }
        } else if (x == mx) mx = index(h, cl[h]->mx);
    }
    long succ(long x) const {                                              // x 보다 큰 최소 원소, 없으면 -1
        calls++;
        if (bits == 1) return (x == 0 && mx == 1) ? 1 : -1;
        if (mn >= 0 && x < mn) return mn;
        VEB* c = cl[high(x)];
        if (c && !c->empty() && low(x) < c->mx) return index(high(x), c->succ(low(x)));
        long sc = summary ? summary->succ(high(x)) : -1;
        return sc < 0 ? -1 : index(sc, cl[sc]->mn);
    }
    long pred(long x) const {                                              // x 보다 작은 최대 원소, 없으면 -1
        calls++;
        if (bits == 1) return (x == 1 && mn == 0) ? 0 : -1;
        if (mx >= 0 && x > mx) return mx;
        VEB* c = cl[high(x)];
        if (c && !c->empty() && low(x) > c->mn) return index(high(x), c->pred(low(x)));
        long pc = summary ? summary->pred(high(x)) : -1;
        if (pc < 0) return (mn >= 0 && x > mn) ? mn : -1;
        return index(pc, cl[pc]->mx);
    }
};

int main() {
    const int BITS = 24; const long U = 1L << BITS;
    VEB v(BITS); std::set<long> ref; std::vector<long> keys; std::mt19937_64 rng(5); long maxCalls = 0;
    for (int step = 0; step < 80000; step++) {
        long x = rng() % U; int op = rng() % 6; calls = 0;
        if (op <= 1 || ref.empty()) { v.insert(x); if (ref.insert(x).second) keys.push_back(x); }          // 삽입 2/6 (중복 삽입도 포함)
        else if (op == 2) { size_t k = rng() % keys.size(); long y = keys[k]; keys[k] = keys.back(); keys.pop_back(); v.erase(y); ref.erase(y); }
        else if (op == 3) { auto it = ref.upper_bound(x); assert(v.succ(x) == (it == ref.end() ? -1 : *it)); }
        else if (op == 4) { auto it = ref.lower_bound(x); assert(v.pred(x) == (it == ref.begin() ? -1 : *std::prev(it))); }
        else              { assert(v.member(x) == (ref.count(x) > 0)); }
        maxCalls = std::max(maxCalls, calls);
        assert(v.member(x) == (ref.count(x) > 0));
        if (!ref.empty()) assert(v.mn == *ref.begin() && v.mx == *ref.rbegin());
    }
    assert(maxCalls <= 16);                                                // 재귀 깊이는 log2(24) ~ 5 단계, 상수 번만 호출
    VEB dense(16); for (long i = 0; i < 65536; i += 3) dense.insert(i);       // 작은 우주는 전부 채워 본다
    for (long i = 0; i < 65535; i++) assert(dense.succ(i) == ((i / 3 + 1) * 3 < 65536 ? (i / 3 + 1) * 3 : -1));
    for (long i = 0; i < 65536; i += 6) dense.erase(i);
    for (long i = 0; i < 65536; i++) assert(dense.member(i) == (i % 3 == 0 && i % 6 != 0));
    std::cout << "VanEmdeBoasTree: U=2^24, " << ref.size() << " keys, max recursive calls per op = " << maxCalls << std::endl;
    return 0;
}
// Time Complexity: 모든 연산 O(log log U)
// Space Complexity: O(N log log U) (lazy 할당; 즉시 할당하면 O(U))
```

# 부록
## 트리 순회의 재귀와 반복 구현
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 같은 순회를 세 가지 방식으로: (1) 재귀 - 호출 스택이 곧 방문 상태, 깊이 h 면 스택 프레임 h 개 (한쪽으로 치우친 100만 노드 트리는 스택 오버플로)
// (2) 반복 - 호출 스택을 명시적 스택(힙 메모리)으로 바꾼 것. 깊이에는 안전하지만 O(h) 공간은 그대로
// (3) Morris - 잎의 빈 오른쪽 자식 포인터를 "후속 노드로 가는 임시 실(thread)"로 쓰고 지나간 뒤 복구해 O(1) 공간.  전위·중위는 가능, 후위는 번거롭다
struct Node { int v; Node *l = nullptr, *r = nullptr; };
std::vector<std::unique_ptr<Node>> pool;
Node* mk(int v) { pool.emplace_back(new Node{v}); return pool.back().get(); }
int depthSeen = 0;
void inRec(const Node* t, std::vector<int>& o, int d = 1)   { if (!t) return; depthSeen = std::max(depthSeen, d); inRec(t->l, o, d + 1); o.push_back(t->v); inRec(t->r, o, d + 1); }
void preRec(const Node* t, std::vector<int>& o)             { if (!t) return; o.push_back(t->v); preRec(t->l, o); preRec(t->r, o); }
void postRec(const Node* t, std::vector<int>& o)            { if (!t) return; postRec(t->l, o); postRec(t->r, o); o.push_back(t->v); }
std::vector<int> inIter(Node* t) {
    std::vector<int> o; std::vector<Node*> st; Node* c = t;
    while (c || !st.empty()) { while (c) { st.push_back(c); c = c->l; } c = st.back(); st.pop_back(); o.push_back(c->v); c = c->r; }
    return o;
}
std::vector<int> preIter(Node* t) {
    std::vector<int> o; std::vector<Node*> st; if (t) st.push_back(t);
    while (!st.empty()) { Node* c = st.back(); st.pop_back(); o.push_back(c->v); if (c->r) st.push_back(c->r); if (c->l) st.push_back(c->l); }
    return o;
}
std::vector<int> postIter(Node* t) {                                       // 스택 하나 + "방금 방문한 노드" 로 오른쪽 부분 트리를 끝냈는지 판단
    std::vector<int> o; std::vector<Node*> st; Node *c = t, *last = nullptr;
    while (c || !st.empty()) {
        if (c) { st.push_back(c); c = c->l; }
        else { Node* top = st.back(); if (top->r && last != top->r) c = top->r; else { o.push_back(top->v); last = top; st.pop_back(); } }
    }
    return o;
}
std::vector<int> inMorris(Node* t, bool preorder = false) {                // preorder=true 이면 처음 도착했을 때 방문 (전위)
    std::vector<int> o; Node* c = t;
    while (c) {
        if (!c->l) { o.push_back(c->v); c = c->r; continue; }
        Node* p = c->l; while (p->r && p->r != c) p = p->r;                // 왼쪽 부분 트리의 가장 오른쪽 = 중위 선행자
        if (!p->r) { if (preorder) o.push_back(c->v); p->r = c; c = c->l; }          // 실을 걸고 내려간다
        else       { p->r = nullptr; if (!preorder) o.push_back(c->v); c = c->r; }   // 실을 풀고 올라온다 (트리 원상 복구)
    }
    return o;
}
Node* randomTree(std::mt19937& rng, int n, int& counter) {
    if (n == 0) return nullptr;
    int k = rng() % n; Node* t = mk(0); t->l = randomTree(rng, k, counter); t->v = counter++; t->r = randomTree(rng, n - 1 - k, counter);
    return t;                                                              // 중위 순서로 0..n-1 이 붙는다
}

int main() {
    std::mt19937 rng(4);
    for (int n = 0; n <= 300; n++) {
        int counter = 0; Node* t = randomTree(rng, n, counter);
        std::vector<int> in, pre, post; inRec(t, in); preRec(t, pre); postRec(t, post);
        assert(inIter(t) == in && preIter(t) == pre && postIter(t) == post);
        assert(inMorris(t) == in && inMorris(t, true) == pre);
        std::vector<int> again; preRec(t, again); assert(again == pre);    // Morris 가 트리를 망가뜨리지 않았다
        for (int i = 0; i < n; i++) assert(in[i] == i);
    }
    // 깊이 100만짜리 한쪽 치우친 트리: 반복·Morris 는 문제없고, 재귀는 같은 깊이를 흉내 낼 수 없다
    Node* chain = mk(0); Node* cur = chain; int N = 1000000;
    for (int i = 1; i < N; i++) { cur->l = mk(i); cur = cur->l; }
    auto a = inIter(chain), b = inMorris(chain), c = preIter(chain), d = postIter(chain);
    assert((int)a.size() == N && a == b && a.front() == N - 1 && a.back() == 0);      // 왼쪽 사슬: 중위 = 맨 아래부터
    assert(c.front() == 0 && c.back() == N - 1 && d == a);
    Node* small = mk(0); cur = small; for (int i = 1; i < 5000; i++) { cur->l = mk(i); cur = cur->l; }
    std::vector<int> o; depthSeen = 0; inRec(small, o); assert(depthSeen == 5000);    // 재귀는 깊이만큼 스택 프레임을 쓴다
    std::cout << "Traversal: recursive/iterative/Morris agree on 300 random trees; 1e6-deep chain handled without recursion (recursion depth 5000 here)" << std::endl;
    return 0;
}
// Time Complexity: 세 방식 모두 O(N) (Morris 는 간선을 최대 3번 지남)
// Space Complexity: 재귀 O(h) 호출 스택, 반복 O(h) 명시적 스택, Morris O(1)
```

## Binary Tree vs BST
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 이진 트리는 "모양"(노드마다 자식 최대 2개)만 정의하고, BST 는 거기에 "순서 불변식"(왼쪽 < 노드 < 오른쪽)을 더한 것이다.
// 모양만 있는 이진 트리에서는 값을 찾으려면 전부 뒤져야 한다(O(N)).  불변식이 있으면 비교 한 번에 절반(이상)을 버려 O(높이) 로 찾는다.
// 대신 BST 는 "어떤 모양이 되는가"가 입력 순서에 달려 있다 -> 정렬된 입력은 높이 N 의 연결 리스트가 되므로 AVL/레드-블랙 같은 균형 트리가 필요하다
struct Node { int v; Node *l = nullptr, *r = nullptr; };
std::vector<std::unique_ptr<Node>> pool;
Node* mk(int v) { pool.emplace_back(new Node{v}); return pool.back().get(); }
bool findAny(const Node* t, int x, long& visited) {                        // 순서 정보가 없는 이진 트리: 전위 탐색
    if (!t) return false; visited++;
    return t->v == x || findAny(t->l, x, visited) || findAny(t->r, x, visited);
}
bool findBst(const Node* t, int x, long& visited) {
    while (t) { visited++; if (x == t->v) return true; t = x < t->v ? t->l : t->r; }
    return false;
}
Node* insertBst(Node* root, int x) {
    Node* n = mk(x); if (!root) return n;
    Node* c = root; for (;;) { Node*& next = x < c->v ? c->l : c->r; if (!next) { next = n; return root; } c = next; }
}
bool isBst(const Node* t, long lo, long hi) { return !t || (t->v > lo && t->v < hi && isBst(t->l, lo, t->v) && isBst(t->r, t->v, hi)); }
void inorder(const Node* t, std::vector<int>& o) { if (!t) return; inorder(t->l, o); o.push_back(t->v); inorder(t->r, o); }
int height(const Node* t) { return t ? 1 + std::max(height(t->l), height(t->r)) : 0; }
Node* fromSorted(const std::vector<int>& a, int lo, int hi) {              // 가운데를 루트로: 높이 ceil(log2(N+1))
    if (lo >= hi) return nullptr; int mid = (lo + hi) / 2; Node* t = mk(a[mid]);
    t->l = fromSorted(a, lo, mid); t->r = fromSorted(a, mid + 1, hi); return t;
}

int main() {
    const int N = (1 << 14) - 1; std::mt19937 rng(10);
    std::vector<int> vals(N); std::iota(vals.begin(), vals.end(), 0); std::shuffle(vals.begin(), vals.end(), rng);
    std::vector<Node*> lvl; for (int x : vals) lvl.push_back(mk(x));       // 같은 값으로 (a) 완전 이진 트리(배열 순서 그대로) (b) 무작위 삽입 BST
    for (int i = 0; i < N; i++) { if (2 * i + 1 < N) lvl[i]->l = lvl[2 * i + 1]; if (2 * i + 2 < N) lvl[i]->r = lvl[2 * i + 2]; }
    Node* plain = lvl[0]; Node* bst = nullptr; for (int x : vals) bst = insertBst(bst, x);
    assert(!isBst(plain, -1, N) && isBst(bst, -1, N));                     // 모양은 같은 "이진 트리"여도 BST 인 것은 불변식을 지킨 쪽뿐
    std::vector<int> a, b; inorder(plain, a); inorder(bst, b);
    assert(!std::is_sorted(a.begin(), a.end()) && std::is_sorted(b.begin(), b.end()));   // BST 의 중위 순회는 정렬 결과
    long visPlain = 0, visBst = 0; int Q = 500;
    for (int q = 0; q < Q; q++) { int x = N + q; bool f1 = findAny(plain, x, visPlain), f2 = findBst(bst, x, visBst); assert(!f1 && !f2); }   // 없는 값 찾기
    for (int q = 0; q < Q; q++) { int x = rng() % N; long t1 = 0, t2 = 0; assert(findAny(plain, x, t1) && findBst(bst, x, t2)); visPlain += t1; visBst += t2; }
    assert(visPlain / (2 * Q) > 2000 && visBst / (2 * Q) < 60);            // 평균 방문 노드: 수천 개 vs 수십 개
    // 입력 순서에 따른 BST 모양
    std::vector<int> sorted(2000); std::iota(sorted.begin(), sorted.end(), 0);
    Node* degenerate = nullptr; for (int x : sorted) degenerate = insertBst(degenerate, x);
    Node* balanced = fromSorted(sorted, 0, sorted.size());
    assert(height(degenerate) == 2000 && height(balanced) == (int)std::ceil(std::log2(2001.0)));
    assert(height(bst) <= 4 * std::log2((double)N));                       // 무작위 순서 삽입의 높이는 평균 ~ 2 ln N, 거의 확실히 4 log2 N 이하
    std::cout << "Binary Tree vs BST: avg visited (plain/BST) = " << visPlain / (2 * Q) << " / " << visBst / (2 * Q)
              << ", height sorted-insert = " << height(degenerate) << ", balanced = " << height(balanced) << ", random = " << height(bst) << std::endl;
    return 0;
}
// Time Complexity: 이진 트리 탐색 O(N), BST 탐색 O(높이) (평균 O(log N), 최악 O(N))
// Space Complexity: O(N)
```
## BST vs AVL vs Red-Black
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// 같은 입력을 세 트리 — 일반 BST, AVL, 좌편향 레드-블랙(LLRB) — 에 넣고 모양을 비교한다.
//  - 일반 BST: 균형 장치가 없어 정렬된 입력이면 높이 n (연결 리스트로 퇴화).  무작위 입력이면 기대 높이 ≈ 4.31·ln n, 평균 깊이 ≈ 2·ln n.
//  - AVL: 모든 노드에서 좌우 높이 차 ≤ 1 → 높이 < 1.4405·log2(n+2).  삽입은 (단일 또는 이중) 회전 *한 번*이면 끝난다.  조회가 가장 빠르다.
//  - LLRB: 2-3 트리를 이진 트리로 옮긴 레드-블랙 변형 → 높이 ≤ 2·log2(n+1).  코드가 짧고 회전이 적어 쓰기에 유리하다 (std::map, Java TreeMap 은 일반 레드-블랙).
//  ① 정렬·역정렬·무작위·지그재그 입력 4 가지에서 높이·평균 깊이·회전 수를 재고 이론 한계를 단언  ② 세 트리 모두 *같은 중위 순서* (정렬된 서로 다른 키) 이고 std::set 과 삽입 결과(중복 20%)가 같다  ③ 불변식 검사: AVL 의 높이 차·저장 높이, LLRB 의 (뿌리 검정 / 빨강 오른쪽 링크 없음 / 연속 빨강 없음 / 검정 높이 균등)
//  ④ 1..7 의 모든 삽입 순서(5 040 가지)에서 높이 분포: BST 3..7, AVL 3..4, LLRB 3..5 — 한계 이내  ⑤ 1..7 을 정렬해 넣은 세 모양을 그림으로 고정(BST 는 사슬, AVL 은 완전 이진 트리, LLRB 도 모두 검정인 완전 이진 트리)
struct B { int k; B *l = nullptr, *r = nullptr; };
struct Bst {
    B* root = nullptr; size_t n = 0; long comparisons = 0;
    ~Bst() { std::vector<B*> st; if (root) st.push_back(root); while (!st.empty()) { B* x = st.back(); st.pop_back(); if (x->l) st.push_back(x->l); if (x->r) st.push_back(x->r); delete x; } }
    bool insert(int k) { B** link = &root; while (*link) { ++comparisons; if (k == (*link)->k) return false; link = k < (*link)->k ? &(*link)->l : &(*link)->r; } *link = new B{k}; ++n; return true; }
    int height() const { int best = 0; std::vector<std::pair<const B*, int>> st; if (root) st.push_back({root, 1}); while (!st.empty()) { auto p = st.back(); st.pop_back(); best = std::max(best, p.second); if (p.first->l) st.push_back({p.first->l, p.second + 1}); if (p.first->r) st.push_back({p.first->r, p.second + 1}); } return best; }
    double averageDepth() const { long sum = 0; std::vector<std::pair<const B*, int>> st; if (root) st.push_back({root, 1}); while (!st.empty()) { auto p = st.back(); st.pop_back(); sum += p.second; if (p.first->l) st.push_back({p.first->l, p.second + 1}); if (p.first->r) st.push_back({p.first->r, p.second + 1}); } return n ? (double)sum / n : 0; }
    void inorder(std::vector<int>& out) const { std::vector<const B*> st; const B* u = root; while (u || !st.empty()) { while (u) { st.push_back(u); u = u->l; } u = st.back(); st.pop_back(); out.push_back(u->k); u = u->r; } }
    std::string draw() const { std::string out; drawRec(root, 0, out); return out; }
    static void drawRec(const B* x, int d, std::string& out) { if (!x) return; drawRec(x->r, d + 1, out); out += std::string(4 * d, ' ') + std::to_string(x->k) + "\n"; drawRec(x->l, d + 1, out); }
};
struct A { int k, h = 1; A *l = nullptr, *r = nullptr; };
struct Avl {
    A* root = nullptr; size_t n = 0; long rotations = 0, fixes = 0, comparisons = 0, lastFixes = 0;
    ~Avl() { destroy(root); }
    static void destroy(A* x) { if (!x) return; destroy(x->l); destroy(x->r); delete x; }
    static int H(const A* x) { return x ? x->h : 0; }
    static void upd(A* x) { x->h = 1 + std::max(H(x->l), H(x->r)); }
    A* rotR(A* y) { A* x = y->l; y->l = x->r; x->r = y; upd(y); upd(x); ++rotations; return x; }
    A* rotL(A* x) { A* y = x->r; x->r = y->l; y->l = x; upd(x); upd(y); ++rotations; return y; }
    A* ins(A* x, int k, bool& added) {
        if (!x) { added = true; return new A{k}; }
        ++comparisons; if (k == x->k) return x; if (k < x->k) x->l = ins(x->l, k, added); else x->r = ins(x->r, k, added);
        upd(x); int bal = H(x->l) - H(x->r);
        if (bal > 1) { if (H(x->l->l) < H(x->l->r)) x->l = rotL(x->l); ++fixes; ++lastFixes; return rotR(x); }
        if (bal < -1) { if (H(x->r->r) < H(x->r->l)) x->r = rotR(x->r); ++fixes; ++lastFixes; return rotL(x); }
        return x; }
    bool insert(int k) { bool added = false; lastFixes = 0; root = ins(root, k, added); n += added; return added; }
    int height() const { return H(root); }
    double averageDepth() const { long sum = 0; depthSum(root, 1, sum); return n ? (double)sum / n : 0; }
    static void depthSum(const A* x, int d, long& sum) { if (!x) return; sum += d; depthSum(x->l, d + 1, sum); depthSum(x->r, d + 1, sum); }
    void check() const { size_t seen = 0; check(root, -(1LL << 40), 1LL << 40, seen); assert(seen == n); }
    int check(const A* x, long long lo, long long hi, size_t& seen) const { if (!x) return 0; assert(x->k > lo && x->k < hi); ++seen; int hl = check(x->l, lo, x->k, seen), hr = check(x->r, x->k, hi, seen); assert(std::abs(hl - hr) <= 1 && x->h == 1 + std::max(hl, hr)); return x->h; }
    void inorder(std::vector<int>& out) const { rec(root, out); }
    static void rec(const A* x, std::vector<int>& out) { if (!x) return; rec(x->l, out); out.push_back(x->k); rec(x->r, out); }
    std::string draw() const { std::string out; drawRec(root, 0, out); return out; }
    static void drawRec(const A* x, int d, std::string& out) { if (!x) return; drawRec(x->r, d + 1, out); out += std::string(4 * d, ' ') + std::to_string(x->k) + "\n"; drawRec(x->l, d + 1, out); }
};
struct R { int k; bool red; R *l = nullptr, *r = nullptr; };
struct Llrb {
    R* root = nullptr; size_t n = 0; long rotations = 0, flips = 0, comparisons = 0;
    ~Llrb() { destroy(root); }
    static void destroy(R* x) { if (!x) return; destroy(x->l); destroy(x->r); delete x; }
    static bool isRed(const R* x) { return x && x->red; }
    R* rotL(R* h) { R* x = h->r; h->r = x->l; x->l = h; x->red = h->red; h->red = true; ++rotations; return x; }
    R* rotR(R* h) { R* x = h->l; h->l = x->r; x->r = h; x->red = h->red; h->red = true; ++rotations; return x; }
    void flip(R* h) { h->red = !h->red; h->l->red = !h->l->red; h->r->red = !h->r->red; ++flips; }
    R* ins(R* h, int k, bool& added) {
        if (!h) { added = true; return new R{k, true}; }
        ++comparisons; if (k == h->k) return h; if (k < h->k) h->l = ins(h->l, k, added); else h->r = ins(h->r, k, added);
        if (isRed(h->r) && !isRed(h->l)) h = rotL(h);                          // 오른쪽 빨강 링크는 왼쪽으로 눕힌다
        if (isRed(h->l) && isRed(h->l->l)) h = rotR(h);                        // 연속 빨강이면 오른쪽 회전
        if (isRed(h->l) && isRed(h->r)) flip(h);                               // 4-노드는 색 뒤집기로 쪼갠다
        return h; }
    bool insert(int k) { bool added = false; root = ins(root, k, added); root->red = false; n += added; return added; }
    int height() const { return height(root); }
    static int height(const R* x) { return x ? 1 + std::max(height(x->l), height(x->r)) : 0; }
    double averageDepth() const { long sum = 0; depthSum(root, 1, sum); return n ? (double)sum / n : 0; }
    static void depthSum(const R* x, int d, long& sum) { if (!x) return; sum += d; depthSum(x->l, d + 1, sum); depthSum(x->r, d + 1, sum); }
    void check() const { assert(!root || !root->red); size_t seen = 0; check(root, -(1LL << 40), 1LL << 40, seen); assert(seen == n); }
    int check(const R* x, long long lo, long long hi, size_t& seen) const { if (!x) return 1; assert(x->k > lo && x->k < hi); ++seen; assert(!isRed(x->r)); if (x->red) assert(!isRed(x->l));   // 빨강 오른쪽 링크 없음, 연속 빨강 없음
        int bl = check(x->l, lo, x->k, seen), br = check(x->r, x->k, hi, seen); assert(bl == br); return bl + (x->red ? 0 : 1); }
    void inorder(std::vector<int>& out) const { rec(root, out); }
    static void rec(const R* x, std::vector<int>& out) { if (!x) return; rec(x->l, out); out.push_back(x->k); rec(x->r, out); }
    std::string draw() const { std::string out; drawRec(root, 0, out); return out; }
    static void drawRec(const R* x, int d, std::string& out) { if (!x) return; drawRec(x->r, d + 1, out); out += std::string(4 * d, ' ') + std::to_string(x->k) + (x->red ? "R" : "B") + "\n"; drawRec(x->l, d + 1, out); }
};
struct Result { int hb, ha, hr; double db, da, dr; long fixes, avlRot, llrbRot; };
Result runWorkload(const std::vector<int>& keys) {
    Bst b; Avl a; Llrb r; for (int k : keys) { b.insert(k); a.insert(k); r.insert(k); }
    a.check(); r.check(); std::vector<int> ib, ia, ir; b.inorder(ib); a.inorder(ia); r.inorder(ir); assert(ib == ia && ia == ir && std::is_sorted(ib.begin(), ib.end()));      // ② 같은 중위 순서
    assert(b.n == a.n && a.n == r.n);
    return {b.height(), a.height(), r.height(), b.averageDepth(), a.averageDepth(), r.averageDepth(), a.fixes, a.rotations, r.rotations};
}

int main() {
    const int n = 20000; std::mt19937 rng(2024);
    std::vector<int> sorted(n), reversed(n), random(n), zigzag; std::iota(sorted.begin(), sorted.end(), 1); reversed.assign(sorted.rbegin(), sorted.rend()); random = sorted; std::shuffle(random.begin(), random.end(), rng);
    for (int lo = 1, hi = n; lo <= hi; ++lo, --hi) { zigzag.push_back(lo); if (lo != hi) zigzag.push_back(hi); }
    const double avlBound = 1.4405 * std::log2(n + 2.0), llrbBound = 2 * std::log2(n + 1.0), ln = std::log((double)n);
    Result rs = runWorkload(sorted), rv = runWorkload(reversed), rr = runWorkload(random), rz = runWorkload(zigzag);                          // ① 네 가지 입력
    for (const Result* x : {&rs, &rv}) { assert(x->hb == n && x->db == (n + 1) / 2.0); }                                                      // 정렬·역정렬: BST 는 사슬, 평균 깊이 (n+1)/2
    assert(rz.hb >= n / 2);                                                                                                                    // 지그재그도 절반 이상으로 깊다
    assert(rr.hb < 4.5 * ln && rr.db > 1.4 * ln && rr.db < 2.1 * ln);                                                                          // 무작위 BST: 높이 ≈ 4.31 ln n, 평균 깊이 ≈ 2 ln n
    for (const Result* x : {&rs, &rv, &rr, &rz}) { assert(x->ha < avlBound && x->hr <= llrbBound); assert(x->fixes <= n && x->avlRot <= 2L * n); assert(x->da < x->ha && x->dr < x->hr); }      // 높이 한계, 삽입당 재균형 ≤ 1, 평균 깊이 < 높이
    {   std::vector<int> keys; for (int i = 0; i < 100000; ++i) keys.push_back((int)(rng() % 40000)); Bst b; Avl a; Llrb r; std::set<int> model;          // ② std::set 대조(중복 포함)
        for (int k : keys) { bool want = model.insert(k).second; assert(b.insert(k) == want && a.insert(k) == want && r.insert(k) == want); assert(a.lastFixes <= 1); }
        a.check(); r.check(); std::vector<int> ia, ir, ib; a.inorder(ia); r.inorder(ir); b.inorder(ib); std::vector<int> want(model.begin(), model.end()); assert(ia == want && ir == want && ib == want); }
    {   int minB = 99, maxB = 0, minA = 99, maxA = 0, minR = 99, maxR = 0; std::vector<int> perm(7); std::iota(perm.begin(), perm.end(), 1);              // ④ 모든 삽입 순서
        do { Bst b; Avl a; Llrb r; for (int k : perm) { b.insert(k); a.insert(k); r.insert(k); } a.check(); r.check();
             minB = std::min(minB, b.height()); maxB = std::max(maxB, b.height()); minA = std::min(minA, a.height()); maxA = std::max(maxA, a.height()); minR = std::min(minR, r.height()); maxR = std::max(maxR, r.height()); } while (std::next_permutation(perm.begin(), perm.end()));
        assert(minB == 3 && maxB == 7 && minA == 3 && maxA == 4 && minR == 3 && maxR <= 5 && maxA <= maxR); }
    {   Bst b; Avl a; Llrb r; for (int k = 1; k <= 7; ++k) { b.insert(k); a.insert(k); r.insert(k); }                                                // ⑤ 그림
        assert(b.draw() == "                        7\n                    6\n                5\n            4\n        3\n    2\n1\n");
        const char* perfect = "        7\n    6\n        5\n4\n        3\n    2\n        1\n";
        assert(a.draw() == perfect && a.height() == 3);
        assert(r.draw() == "        7B\n    6B\n        5B\n4B\n        3B\n    2B\n        1B\n" && r.height() == 3); }                          // 2-3 트리로 읽으면 3 층 완전 2-3-4 트리: 빨강 링크가 하나도 안 남는다
    std::cout << "BST vs AVL vs LLRB (n=" << n << "): sorted input -> BST height " << rs.hb << ", AVL " << rs.ha << " (" << rs.avlRot << " rotations), LLRB " << rs.hr << " (" << rs.llrbRot << " rotations); random input -> BST " << rr.hb << ", AVL " << rr.ha << ", LLRB " << rr.hr << std::endl;
    return 0;
}
// Time Complexity: BST 최악 O(N), AVL·LLRB O(log N)
// Space Complexity: O(N)
```
## Segment Tree vs Fenwick Tree
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 둘 다 "점 갱신 + 구간 질의"를 O(log n) 에 처리하지만 성격이 다르다.
// 펜윅(BIT): 배열 n+1 칸, 코드 10줄 안팎, 상수 작음.  그러나 "역연산이 있는 연산"(합, XOR)의 접두 질의가 본업이다. 구간 [l,r] = prefix(r) - prefix(l-1) 로 빼기가 필요하기 때문.
// 세그먼트 트리: 2n 칸 이상, 연산이 결합법칙만 만족하면 된다(최소·최대·gcd·행렬곱 ...).  지연 전파를 붙이면 구간 갱신도 가능.
// 아래에서 확인: (1) 합은 둘이 같은 답 (2) 최솟값은 세그먼트 트리만 임의 구간·임의 갱신을 지원 (3) 구간 덧셈+구간 합은 BIT 2개로도 가능
struct Fenwick {                                                           // 1-기준 인덱스
    int n; std::vector<long> t; explicit Fenwick(int n) : n(n), t(n + 1, 0) {}
    void add(int i, long d) { for (; i <= n; i += i & -i) t[i] += d; }
    long sum(int i) const { long s = 0; for (; i > 0; i -= i & -i) s += t[i]; return s; }
    long range(int l, int r) const { return sum(r) - sum(l - 1); }
};
struct RangeBit {                                                          // 구간 덧셈 + 구간 합: B1·i - B2 (차분 배열 두 개)
    Fenwick b1, b2; explicit RangeBit(int n) : b1(n), b2(n) {}
    void rangeAdd(int l, int r, long x) { b1.add(l, x); b1.add(r + 1, -x); b2.add(l, x * (l - 1)); b2.add(r + 1, -x * r); }
    long prefix(int i) const { return b1.sum(i) * i - b2.sum(i); }
    long range(int l, int r) const { return prefix(r) - prefix(l - 1); }
};
template <class Op> struct SegTree {                                       // 반복(bottom-up) 세그먼트 트리, [l, r) 질의
    int n; std::vector<long> t; long id; Op op;
    SegTree(int n, long id, Op op) : n(n), t(2 * n, id), id(id), op(op) {}
    void set(int p, long v) { for (t[p += n] = v; p > 1; p >>= 1) t[p >> 1] = op(t[p], t[p ^ 1]); }
    long query(int l, int r) const { long a = id, b = id; for (l += n, r += n; l < r; l >>= 1, r >>= 1) { if (l & 1) a = op(a, t[l++]); if (r & 1) b = op(t[--r], b); } return op(a, b); }
};
struct MinBit {                                                            // 접두 최솟값 BIT: 값이 "작아지는" 갱신만 가능
    int n; std::vector<long> t; explicit MinBit(int n) : n(n), t(n + 1, LONG_MAX) {}
    void lower(int i, long v) { for (; i <= n; i += i & -i) t[i] = std::min(t[i], v); }
    long prefixMin(int i) const { long m = LONG_MAX; for (; i > 0; i -= i & -i) m = std::min(m, t[i]); return m; }
};

int main() {
    const int N = 1000; std::mt19937 rng(6);
    Fenwick bit(N); SegTree<std::plus<long>> segSum(N, 0, std::plus<long>()); std::vector<long> a(N + 1, 0);
    auto mn = [](long x, long y) { return std::min(x, y); };
    SegTree<decltype(mn)> segMin(N, LONG_MAX, mn); for (int i = 1; i <= N; i++) { a[i] = rng() % 1000; bit.add(i, a[i]); segSum.set(i - 1, a[i]); segMin.set(i - 1, a[i]); }
    for (int step = 0; step < 20000; step++) {
        int p = rng() % N + 1; long v = rng() % 1000;
        bit.add(p, v - a[p]); segSum.set(p - 1, v); segMin.set(p - 1, v); a[p] = v;                // 점 갱신: 펜윅은 "차이"를, 세그먼트 트리는 "새 값"을
        int l = rng() % N + 1, r = rng() % N + 1; if (l > r) std::swap(l, r);
        long s = 0, m = LONG_MAX; for (int i = l; i <= r; i++) { s += a[i]; m = std::min(m, a[i]); }
        assert(bit.range(l, r) == s && segSum.query(l - 1, r) == s);       // 합: 둘 다 정확
        assert(segMin.query(l - 1, r) == m);                               // 최솟값: 세그먼트 트리는 임의 갱신 후에도 정확
    }
    RangeBit rb(N); std::vector<long> b(N + 2, 0);                         // 구간 덧셈·구간 합도 펜윅 2개로 가능
    for (int step = 0; step < 5000; step++) {
        int l = rng() % N + 1, r = rng() % N + 1; if (l > r) std::swap(l, r); long x = (long)(rng() % 200) - 100;
        rb.rangeAdd(l, r, x); for (int i = l; i <= r; i++) b[i] += x;
        int ql = rng() % N + 1, qr = rng() % N + 1; if (ql > qr) std::swap(ql, qr);
        long s = 0; for (int i = ql; i <= qr; i++) s += b[i]; assert(rb.range(ql, qr) == s);
    }
    // 최솟값 펜윅의 한계: 값이 작아지는 갱신만 가능하고, 접두 구간만 답한다
    MinBit mb(5); long arr[6] = {0, 5, 3, 8, 6, 7}; for (int i = 1; i <= 5; i++) mb.lower(i, arr[i]);
    assert(mb.prefixMin(5) == 3);
    arr[2] = 10; mb.lower(2, 10);                                          // 값을 키우는 갱신 -> BIT 는 반영하지 못한다
    long truth = *std::min_element(arr + 1, arr + 6);                      // 실제 최솟값은 5
    assert(truth == 5 && mb.prefixMin(5) == 3 && mb.prefixMin(5) != truth);   // BIT 의 답 3 은 낡았다. 세그먼트 트리는 set 한 번으로 정확히 5
    SegTree<decltype(mn)> st5(5, LONG_MAX, mn); for (int i = 1; i <= 5; i++) st5.set(i - 1, arr[i]); assert(st5.query(0, 5) == 5);
    std::cout << "Segment vs Fenwick: sum agrees, min needs segment tree; memory BIT " << (N + 1) << " vs segment " << 2 * N << " words" << std::endl;
    return 0;
}
// Time Complexity: 둘 다 점 갱신·질의 O(log N); 펜윅은 상수가 작고 세그먼트 트리는 연산 종류가 자유롭다
// Space Complexity: 펜윅 N, 세그먼트 트리 2N (재귀 구현은 4N)
```
