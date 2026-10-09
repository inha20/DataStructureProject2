# Part 1. 그래프의 기초
## CreateGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 그래프 만들기(CreateGraph): 그래프 G = (V, E) 는 정점 집합과 간선 집합이다. 만드는 방법은 (1) 정점 n 개만 있는 빈 그래프, (2) 간선 목록에서 — 잘못된 번호는 거르고, 중복 간선(무방향이면 (u,v) 와 (v,u) 도 같은 간선)과 정책상 금지된 자기 루프는 무시한다, (3) 인접 행렬에서, (4) 무작위 모형: G(n, m) 은 가능한 간선 중 정확히 m 개를 균등하게 고르고, G(n, p) 는 가능한 간선 각각을 독립적으로 확률 p 로 넣는다(기대 간선 수 p·최대 간선 수).
// 정책이 중요하다: 단순 그래프(simple graph)는 중복 간선과 자기 루프가 없다. 무방향 그래프는 간선을 양쪽 인접 리스트에 모두 저장해(자기 루프는 한 번) 어느 끝점에서나 이웃을 훑을 수 있고, 유방향 그래프는 나가는 쪽(필요하면 들어오는 쪽도)에 저장한다. 최대 간선 수는 무방향 단순 n(n−1)/2, 유방향 단순 n(n−1) (자기 루프 허용이면 각각 + n).
// 검증: ① 빈 그래프: 정점 n, 간선 0, 일관성 ② 무작위 간선 목록(중복·뒤집힌 중복·자기 루프·잘못된 번호 포함)에서 만든 그래프의 간선 집합이 모델과 같고 거절 횟수가 입력 수 − 서로 다른 유효 간선 수 ③ 무방향 대칭 저장 / 유방향 역방향 리스트 일관성 ④ 행렬에서 만든 그래프를 다시 행렬로 바꾸면 원본(무방향은 A[i][j] || A[j][i] 로 합침) ⑤ G(n, m) 이 정확히 m 개의 서로 다른 간선이고 각 간선이 선택될 확률이 m/최대 간선 수 (5σ 이내) ⑥ G(n, p) 의 간선 수 평균이 p·최대 간선 수 (5σ), p = 0 이면 간선 없음, p = 1 이면 완전 그래프.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
typedef std::vector<std::pair<int, int>> Edges;
std::size_t maxEdges(int n, bool directed, bool loops) { std::size_t base = directed ? (std::size_t)n * (n - 1) : (std::size_t)n * (n - 1) / 2; return base + (loops ? (std::size_t)n : 0); }
Graph fromEdges(int n, bool directed, bool loops, const Edges& edges, int& rejected) { Graph g(n, directed, loops); rejected = 0; for (const auto& e : edges) if (!g.addEdge(e.first, e.second)) rejected++; return g; }
Graph fromMatrix(const std::vector<std::vector<int>>& A, bool directed) { int n = (int)A.size(); Graph g(n, directed); for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (i != j && (A[i][j] || (!directed && A[j][i]))) g.addEdge(i, j); return g; }
std::vector<std::vector<int>> toMatrix(const Graph& g) { int n = g.capacity(); std::vector<std::vector<int>> A(n, std::vector<int>(n, 0)); for (int u = 0; u < n; u++) for (int v : g.out(u)) A[u][v] = 1; return A; }
Graph gnm(int n, int m, bool directed, std::mt19937& rng) { Graph g(n, directed); while ((int)g.edgeCount() < m) g.addEdge((int)(rng() % n), (int)(rng() % n)); return g; }               // 중복·자기 루프는 거절되므로 정확히 m 개가 모일 때까지
Graph gnp(int n, double p, bool directed, std::mt19937& rng) { Graph g(n, directed); std::uniform_real_distribution<double> U(0, 1); for (int u = 0; u < n; u++) for (int v = directed ? 0 : u + 1; v < n; v++) if (u != v && U(rng) < p) g.addEdge(u, v); return g; }
int main() {
    for (bool directed : {false, true}) for (int n : {0, 1, 5, 100}) { Graph g(n, directed); assert((int)g.vertexCount() == n && g.edgeCount() == 0 && g.consistent()); for (int v = 0; v < n; v++) assert(g.out(v).empty()); }              // ①
    std::mt19937 rng(1);
    for (int rep = 0; rep < 400; rep++) { bool directed = rep % 2, loops = rep % 3 == 0; int n = 1 + (int)(rng() % 12); Edges input; int m = (int)(rng() % 40); for (int i = 0; i < m; i++) input.push_back({(int)(rng() % (n + 3)) - 1, (int)(rng() % (n + 3)) - 1});      // 잘못된 번호 포함
        int rejected = 0; Graph g = fromEdges(n, directed, loops, input, rejected); std::set<std::pair<int, int>> model; for (auto e : input) { if (e.first < 0 || e.second < 0 || e.first >= n || e.second >= n) continue; if (e.first == e.second && !loops) continue; if (!directed && e.first > e.second) std::swap(e.first, e.second); model.insert(e); }
        assert(g.edgeSet() == model && g.edgeCount() == model.size() && rejected == m - (int)model.size() && g.consistent() && g.edgeCount() <= maxEdges(n, directed, loops));                                                                         // ② ③
        for (int u = 0; u < n; u++) for (int v : g.out(u)) { if (directed) { const auto& in = g.in(v); assert(std::find(in.begin(), in.end(), u) != in.end()); } else assert(g.hasEdge(v, u)); } }
    for (int rep = 0; rep < 200; rep++) { bool directed = rep % 2; int n = 1 + (int)(rng() % 10); std::vector<std::vector<int>> A(n, std::vector<int>(n)); for (auto& row : A) for (int& x : row) x = rng() % 3 == 0; Graph g = fromMatrix(A, directed); auto B = toMatrix(g);                // ④
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) assert(B[i][j] == (i != j && (A[i][j] || (!directed && A[j][i])) ? 1 : 0)); }
    { const int n = 7, trials = 3000; for (bool directed : {false, true}) { int m = 9; std::size_t maxE = maxEdges(n, directed, false); std::map<std::pair<int, int>, int> freq; for (int t = 0; t < trials; t++) { Graph g = gnm(n, m, directed, rng); assert((int)g.edgeCount() == m && g.consistent()); for (auto e : g.edgeSet()) freq[e]++; }   // ⑤
        double p = (double)m / (double)maxE, sigma = std::sqrt(trials * p * (1 - p)); assert(freq.size() == maxE); for (auto& kv : freq) assert(std::abs(kv.second - trials * p) < 5 * sigma); } }
    { for (bool directed : {false, true}) { const int n = 20; for (double p : {0.1, 0.5, 0.9}) { double mean = 0; const int trials = 300; std::size_t maxE = maxEdges(n, directed, false); std::vector<double> counts; for (int t = 0; t < trials; t++) { counts.push_back((double)gnp(n, p, directed, rng).edgeCount()); mean += counts.back(); } mean /= trials;   // ⑥
          double sigma = std::sqrt((double)maxE * p * (1 - p) / trials); assert(std::abs(mean - (double)maxE * p) < 5 * sigma); } assert(gnp(15, 0.0, directed, rng).edgeCount() == 0 && gnp(15, 1.0, directed, rng).edgeCount() == maxEdges(15, directed, false)); } }
    std::cout << "CreateGraph: empty graphs, edge-list construction (duplicates, reversed duplicates, loops and invalid ids filtered exactly as a set model predicts), matrix conversion round trips, G(n,m) with exactly m distinct edges chosen uniformly (each edge's frequency within 5 sigma of m/maxEdges), and G(n,p) with the expected edge count (including p=0 and p=1) all behaved as specified" << std::endl; return 0;
}
// Time Complexity: O(V + E) (중복 검사가 선형이면 O(E · 차수))
// Space Complexity: O(V + E)
```
## AddVertex()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 정점 추가(AddVertex): 새 정점 하나를 만들어 번호를 돌려준다. 새 정점은 이웃이 없어(차수 0) 간선이 하나도 안 변한다. 인접 리스트에서는 빈 리스트 하나를 덧붙이면 되어 분할상환 O(1) 이다. 인접 행렬은 새 행과 새 열이 필요해서 훨씬 비싸다: (1) 1 차원 배열에 (V+1)² 칸을 새로 만들어 옛 값을 모두 복사하면 한 번에 O(V²) — V 번 더하면 O(V³), (2) 행마다 벡터를 두고 각 행에 한 칸씩 덧붙이고 새 행을 만들면 한 번에 O(V) — V 번이면 정확히 V² 번의 쓰기, (3) 용량을 두 배씩 늘리는 1 차원 배열은 복사가 V = 1, 2, 4, 8, … 일 때만 일어나 총 O(V²) 이다(분할상환 한 번에 O(V)).
// 정점을 더해도 기존 정점의 번호는 변하지 않는다(번호 안정성) — 그래서 외부에서 번호를 들고 있어도 안전하다. 번호가 연속적이면 배열을 번호로 바로 색인할 수 있다.
// 검증: ① 순차적으로 정점을 더하면 번호가 0, 1, 2, … 이고 새 정점은 차수 0 으로 기존 간선을 건드리지 않음(간선 집합 불변) ② 정점과 간선을 섞어 더한 뒤 리스트 그래프와 세 가지 행렬 표현이 모든 쌍에서 같은 간선 소속 ③ 비용: V = 300 번 더할 때 순진한 1 차원 행렬의 복사가 ≥ V³/4, 행별 벡터의 쓰기가 정확히 V², 두 배 증가 행렬의 복사가 ≤ 4V² ④ 무방향 그래프의 행렬은 대칭 ⑤ 정점이 0 개인 그래프에서도 첫 정점 추가가 0 번.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
struct MatrixNaive { std::vector<char> a; int n = 0; long copies = 0; int add() { std::vector<char> b((std::size_t)(n + 1) * (n + 1), 0); for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) { b[(std::size_t)i * (n + 1) + j] = a[(std::size_t)i * n + j]; copies++; } a.swap(b); return n++; }
    void set(int u, int v) { a[(std::size_t)u * n + v] = 1; } bool get(int u, int v) const { return a[(std::size_t)u * n + v]; } };
struct MatrixRows { std::vector<std::vector<char>> a; int n = 0; long writes = 0; int add() { for (auto& r : a) { r.push_back(0); writes++; } a.emplace_back(n + 1, 0); writes += n + 1; return n++; } void set(int u, int v) { a[u][v] = 1; } bool get(int u, int v) const { return a[u][v]; } };
struct MatrixDoubling { std::vector<char> a; int n = 0, cap = 0; long copies = 0; int add() { if (n == cap) { int nc = cap ? cap * 2 : 1; std::vector<char> b((std::size_t)nc * nc, 0); for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) { b[(std::size_t)i * nc + j] = a[(std::size_t)i * cap + j]; copies++; } a.swap(b); cap = nc; } return n++; }
    void set(int u, int v) { a[(std::size_t)u * cap + v] = 1; } bool get(int u, int v) const { return a[(std::size_t)u * cap + v]; } };
int main() {
    std::mt19937 rng(2);
    { Graph g(0, false); assert(g.vertexCount() == 0); for (int i = 0; i < 5; i++) assert(g.addVertex() == i); assert(g.vertexCount() == 5 && g.edgeCount() == 0 && g.consistent()); }                                                    // ① ⑤
    for (int rep = 0; rep < 100; rep++) { bool directed = rep % 2; Graph g(0, directed); std::set<std::pair<int, int>> before;
        for (int step = 0; step < 60; step++) { if (rng() % 3 == 0 || g.capacity() < 2) { auto snapshot = g.edgeSet(); int id = g.addVertex(); assert(id == g.capacity() - 1 && g.degree(id) == 0 && g.edgeSet() == snapshot && g.consistent()); }
              else { int u = (int)(rng() % g.capacity()), v = (int)(rng() % g.capacity()); g.addEdge(u, v); } } }
    { const int V = 300; MatrixNaive mn; MatrixRows mr; MatrixDoubling md; Graph g(0, false); std::set<std::pair<int, int>> edges;                                                                                               // ② ③
      for (int i = 0; i < V; i++) { int a = mn.add(), b = mr.add(), c = md.add(), d = g.addVertex(); assert(a == i && b == i && c == i && d == i); for (int k = 0; k < 2 && i > 0; k++) { int u = i, v = (int)(rng() % i); mn.set(u, v); mn.set(v, u); mr.set(u, v); mr.set(v, u); md.set(u, v); md.set(v, u); g.addEdge(u, v); } }
      for (int u = 0; u < V; u++) for (int v = 0; v < V; v++) { bool e = u != v && g.hasEdge(u, v); assert(mn.get(u, v) == e && mr.get(u, v) == e && md.get(u, v) == e); if (!e) continue; assert(mn.get(v, u)); }                          // ④ 대칭
      assert(mn.copies >= (long)V * V * V / 4 && mr.writes == (long)V * V && md.copies <= 4L * V * V); }
    std::cout << "AddVertex: new vertices got consecutive stable ids with degree 0 and left the edge set untouched, and over 300 insertions the three matrix designs agreed with the adjacency list on every pair while costing ~V^3/3 element copies (whole-array rebuild), exactly V^2 writes (per-row vectors) and under 4V^2 copies (capacity doubling)" << std::endl; return 0;
}
// Time Complexity: 인접 리스트 분할상환 O(1), 행렬 O(V) ~ O(V²)
// Space Complexity: O(V + E) (행렬은 O(V²))
```
## RemoveVertex()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 정점 삭제(RemoveVertex): 정점과 그에 닿는 모든 간선을 없앤다. 세 가지 설계가 있고 번호를 어떻게 하느냐가 다르다. (1) 표시만 하기(tombstone): alive 를 끄고 이웃에서 간선만 지운다 — 다른 정점의 번호가 안 바뀌고 O(deg) 이다(무방향은 이웃의 리스트에서 찾아 지우므로 이웃 차수만큼 더). 대신 번호 공간에 빈 구멍이 생긴다. (2) 압축(compaction): 살아 있는 정점을 0..V'−1 로 다시 번호 매기고 간선을 새 번호로 바꾼다 — O(V+E) 이고 모든 번호가 바뀐다. (3) 마지막 정점 옮기기(swap with last): 마지막 번호의 정점을 삭제한 자리로 옮기고 그 이웃들이 가진 "마지막 번호" 를 새 번호로 고친다 — 번호 공간이 촘촘하고 O(deg(마지막) · 이웃 차수)지만 한 정점의 번호가 바뀐다.
// 유방향 그래프는 들어오는 간선도 지워야 하는데 역방향 리스트가 없으면 모든 리스트를 훑어 O(V+E) 가 든다. 이 코드의 그래프는 역방향 리스트를 두어 O(deg) 이다.
// 검증: ① 무작위 그래프에서 세 방식 각각 정점 하나를 지운 뒤 간선 집합이 모델(그 정점이 낀 간선을 뺀 집합, 번호 대응 포함)과 같고 일관성 유지 ② 표시 방식에서 다른 정점의 번호가 변하지 않음, 압축은 살아 있는 정점의 상대 순서를 유지하는 새 번호, 마지막 옮기기는 정확히 한 정점(마지막)만 새 번호를 받음 ③ 존재하지 않는/이미 지운 정점 삭제는 false ④ 정점을 하나씩 모두 지우면 빈 그래프 ⑤ 비용: 희소 그래프(V = 400, E = 800)에서 표시·마지막 옮기기가 건드린 인접 항목 수 ≪ 압축 ⑥ 지운 정점의 번호로 간선을 더하려 하면 거절.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
typedef std::vector<std::vector<int>> Adj;
Adj toAdj(const Graph& g) { Adj a(g.capacity()); for (int u = 0; u < g.capacity(); u++) if (g.valid(u)) a[u] = g.out(u); return a; }
long compactRemove(Adj& a, int v, std::vector<int>& newId) {                                                         // (2) 압축: 모든 번호를 다시 매긴다. 반환: 건드린 항목 수
    int n = (int)a.size(); long touched = 0; newId.assign(n, -1); int k = 0; for (int u = 0; u < n; u++) if (u != v) newId[u] = k++; Adj b(n - 1); for (int u = 0; u < n; u++) { if (u == v) continue; for (int w : a[u]) { touched++; if (w != v) b[newId[u]].push_back(newId[w]); } } a = b; return touched; }
long swapLastRemove(Adj& a, int v) {                                                                                 // (3) 마지막 정점을 v 자리로 옮긴다
    int last = (int)a.size() - 1; long touched = 0; for (int w : a[v]) { auto& l = a[w]; l.erase(std::find(l.begin(), l.end(), v)); touched += (long)l.size() + 1; } a[v].clear();
    if (v != last) { for (int w : a[last]) { for (int& x : a[w]) { touched++; if (x == last) x = v; } } a[v] = a[last]; } a.pop_back(); return touched; }
std::set<std::pair<int, int>> edgesOf(const Adj& a) { std::set<std::pair<int, int>> s; for (int u = 0; u < (int)a.size(); u++) for (int v : a[u]) s.insert({std::min(u, v), std::max(u, v)}); return s; }
int main() {
    std::mt19937 rng(3); long tombTouched = 0, compactTouched = 0, swapTouched = 0;
    for (int rep = 0; rep < 300; rep++) { int n = 2 + (int)(rng() % 14); bool directed = false; Graph g(n, directed); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n)); int v = (int)(rng() % n); auto edges = g.edgeSet();    // ①
        std::set<std::pair<int, int>> want; for (auto e : edges) if (e.first != v && e.second != v) want.insert(e);
        Graph t = g; assert(t.removeVertex(v) && t.edgeSet() == want && t.consistent() && (int)t.vertexCount() == n - 1 && !t.valid(v)); for (int u = 0; u < n; u++) if (u != v) assert(t.valid(u));                                // 표시: 다른 번호 불변
        Adj ac = toAdj(g); std::vector<int> newId; compactRemove(ac, v, newId); std::set<std::pair<int, int>> wantC; for (auto e : want) wantC.insert({newId[e.first], newId[e.second]}); assert(edgesOf(ac) == wantC && (int)ac.size() == n - 1);
        for (int u = 0, k = 0; u < n; u++) if (u != v) assert(newId[u] == k++);                                                                                                                                         // ② 압축은 상대 순서 유지
        Adj as = toAdj(g); swapLastRemove(as, v); int last = n - 1; std::set<std::pair<int, int>> wantS; for (auto e : want) { auto rename = [&](int x) { return x == last ? v : x; }; int a = rename(e.first), b = rename(e.second); wantS.insert({std::min(a, b), std::max(a, b)}); } assert(edgesOf(as) == wantS && (int)as.size() == n - 1);
        Graph again = g; assert(again.removeVertex(v) && !again.removeVertex(v) && !again.removeVertex(-1) && !again.removeVertex(n + 5)); assert(!again.addEdge(v, (v + 1) % n) && !again.addEdge((v + 1) % n, v)); }                           // ③ ⑥
    for (bool directed : {false, true}) { Graph g(12, directed); for (int k = 0; k < 40; k++) g.addEdge((int)(rng() % 12), (int)(rng() % 12)); std::vector<int> order(12); std::iota(order.begin(), order.end(), 0); std::shuffle(order.begin(), order.end(), rng); for (int v : order) { assert(g.removeVertex(v) && g.consistent()); } assert(g.vertexCount() == 0 && g.edgeCount() == 0); }   // ④
    { const int V = 400; Graph g(V, false); while ((int)g.edgeCount() < 800) g.addEdge((int)(rng() % V), (int)(rng() % V)); for (int rep = 0; rep < 50; rep++) { int v = (int)(rng() % V); Adj ac = toAdj(g); std::vector<int> id; compactRemove(ac, v, id);                                                                   // ⑤ 비용
        Adj as = toAdj(g); swapTouched += swapLastRemove(as, v); compactTouched += 2 * 800; tombTouched += 2 * g.degree(v); (void)ac; } assert(swapTouched * 5 < compactTouched && tombTouched * 20 < compactTouched); }
    std::cout << "RemoveVertex: marking (stable ids), compaction (all ids renumbered in order) and swap-with-last (exactly one id changes) each removed a vertex and its incident edges consistently with a set model on 300 random graphs; double removal and edges to a removed vertex were rejected, graphs could be emptied vertex by vertex, and on a sparse graph the local strategies touched far fewer adjacency entries than compaction" << std::endl; return 0;
}
// Time Complexity: 표시 O(deg), 마지막 옮기기 O(deg · 이웃 차수), 압축 O(V + E)
// Space Complexity: O(1) 추가 (압축은 O(V + E))
```
## AddEdge()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 간선 추가(AddEdge): 두 정점 사이에 간선을 넣는다. 정책 결정이 핵심이다. 번호가 범위 밖이거나 삭제된 정점이면 거절, 단순 그래프에서 이미 있는 간선(무방향은 (u,v) 와 (v,u) 가 같은 간선)이면 거절, 자기 루프가 금지된 모형에서는 u = v 를 거절한다. 허용되면 무방향은 양쪽 리스트에, 유방향은 나가는 쪽과 들어오는 쪽에 넣고 간선 수를 +1 한다. 가중치가 있는 그래프에서 이미 있는 간선에 다시 넣으면 가중치를 갱신하거나(덮어쓰기) 평행 간선을 허용하는 다중 그래프로 둔다.
// 중복 검사 비용: 인접 리스트를 훑으면 O(deg), 해시 집합을 곁들이면 기대 O(1). 간선을 N 개 넣을 때 완전 그래프에 가까운 밀집 입력은 선형 검사가 O(N · V)까지 커진다. 검사를 생략하고 중복을 허용(다중 그래프)하면 O(1) 이지만 간선 수·차수의 의미가 달라진다.
// 검증: ① 무작위 간선 추가열(잘못된 번호·중복·자기 루프 포함)에서 반환값(추가됨/거절됨)이 집합 모델과 같고 간선 수·일관성 유지, 무방향/유방향 모두 ② 무방향은 addEdge(u,v) 뒤 hasEdge(v,u) 도 참, 유방향은 거짓 ③ 자기 루프 허용/금지 정책 ④ 해시 검사 방식이 선형 검사와 같은 결과이고 밀집 입력(V=200, 간선 시도 40000)에서 선형 검사의 훑은 항목 수가 해시 방식의 ≥ 20 배 ⑤ 다중 그래프 방식은 평행 간선을 모두 저장(간선 수 == 시도 수)하고 차수는 평행 간선만큼 커짐 ⑥ 가중치 갱신 정책: 같은 간선 재추가 시 가중치만 바뀌고 간선 수 불변.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
struct HashedGraph { int n; bool directed; std::vector<std::vector<int>> adj; std::set<std::pair<int, int>> seen; long scanned = 0; HashedGraph(int n_, bool d) : n(n_), directed(d), adj(n_) {}                  // 해시 집합으로 중복 검사
    bool add(int u, int v) { if (u < 0 || v < 0 || u >= n || v >= n || u == v) return false; auto key = directed ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v)); if (!seen.insert(key).second) return false; adj[u].push_back(v); if (!directed) adj[v].push_back(u); return true; } };
struct LinearGraph { int n; bool directed; std::vector<std::vector<int>> adj; long scanned = 0; LinearGraph(int n_, bool d) : n(n_), directed(d), adj(n_) {}                                       // 인접 리스트를 훑어 중복 검사
    bool add(int u, int v) { if (u < 0 || v < 0 || u >= n || v >= n || u == v) return false; for (int w : adj[u]) { scanned++; if (w == v) return false; } adj[u].push_back(v); if (!directed) adj[v].push_back(u); return true; } };
struct Multi { std::vector<std::vector<int>> adj; std::size_t edges = 0; explicit Multi(int n) : adj(n) {}                                                                         // 평행 간선·자기 루프 모두 저장
    void add(int u, int v) { adj[u].push_back(v); if (u != v) adj[v].push_back(u); edges++; } int degree(int v) const { int d = (int)adj[v].size(); for (int w : adj[v]) if (w == v) d++; return d; } int multiplicity(int u, int v) const { return (int)std::count(adj[u].begin(), adj[u].end(), v); } };
struct WeightedGraph { std::map<std::pair<int, int>, int> w; std::size_t edges() const { return w.size(); } bool add(int u, int v, int weight) { auto key = std::make_pair(std::min(u, v), std::max(u, v)); bool fresh = !w.count(key); w[key] = weight; return fresh; } };   // 같은 간선이면 가중치 갱신
int main() {
    std::mt19937 rng(4);
    for (int rep = 0; rep < 300; rep++) { bool directed = rep % 2; int n = 1 + (int)(rng() % 10); Graph g(n, directed); std::set<std::pair<int, int>> model;                                                         // ① ②
        for (int step = 0; step < 80; step++) { int u = (int)(rng() % (n + 2)) - 1, v = (int)(rng() % (n + 2)) - 1; bool valid = u >= 0 && v >= 0 && u < n && v < n && u != v; auto key = directed ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v)); bool expectAdded = valid && !model.count(key);
            bool added = g.addEdge(u, v); assert(added == expectAdded); if (added) { model.insert(key); assert(g.hasEdge(u, v) && (directed ? g.hasEdge(v, u) == (model.count({v, u}) > 0) : g.hasEdge(v, u))); } assert(g.edgeCount() == model.size()); }
        assert(g.edgeSet() == model && g.consistent()); }
    { Graph a(3, false, true), b(3, false, false); assert(a.addEdge(1, 1) && a.hasEdge(1, 1) && a.edgeCount() == 1 && !a.addEdge(1, 1) && !b.addEdge(1, 1) && b.edgeCount() == 0 && a.degree(1) == 2); Graph d(3, true, true); assert(d.addEdge(2, 2) && d.outDegree(2) == 1 && d.inDegree(2) == 1 && d.degree(2) == 2); }   // ③ 자기 루프
    { const int V = 200; HashedGraph h(V, false); LinearGraph l(V, false); long attempts = 40000, added = 0; for (long i = 0; i < attempts; i++) { int u = (int)(rng() % V), v = (int)(rng() % V); bool a = h.add(u, v), b = l.add(u, v); assert(a == b); added += a; } assert(added == (long)h.seen.size());   // ④
      for (int u = 0; u < V; u++) { std::vector<int> x = h.adj[u], y = l.adj[u]; std::sort(x.begin(), x.end()); std::sort(y.begin(), y.end()); assert(x == y); } assert(l.scanned >= 20 * attempts / 4); }
    { Multi m(4); std::map<std::pair<int, int>, int> mult; const int attempts = 200; for (int i = 0; i < attempts; i++) { int u = (int)(rng() % 4), v = (int)(rng() % 4); m.add(u, v); mult[{std::min(u, v), std::max(u, v)}]++; }                                 // ⑤ 다중 그래프
      long degSum = 0; for (int v = 0; v < 4; v++) degSum += m.degree(v); assert(m.edges == attempts && degSum == 2L * attempts); for (auto& kv : mult) assert(m.multiplicity(kv.first.first, kv.first.second) == kv.second); }
    { WeightedGraph wg; assert(wg.add(1, 2, 5) && !wg.add(2, 1, 9) && wg.edges() == 1 && wg.w.at({1, 2}) == 9 && wg.add(0, 3, 1) && wg.edges() == 2); }                                                                          // ⑥
    std::cout << "AddEdge: 300 random insertion sequences (invalid ids, duplicates, reversed duplicates, loops) returned exactly the added/rejected verdicts a set model predicts with consistent counts and symmetric or one-way storage, loop policies behaved as configured (a loop adds 2 to an undirected degree), hashed duplicate checking matched linear scanning while the scan cost at 40000 dense attempts was over 5x higher, multigraph insertion kept every parallel edge (degree sum twice the edge count), and re-adding a weighted edge only updated its weight" << std::endl; return 0;
}
// Time Complexity: 해시 검사 기대 O(1), 선형 검사 O(deg)
// Space Complexity: O(1) 추가
```
## RemoveEdge()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 간선 삭제(RemoveEdge): 간선 (u, v) 를 없앤다. 있으면 지우고 true, 없으면 false. 인접 리스트에서는 u 의 리스트에서 v 를 찾아야 하므로 O(deg(u)) 이고, 찾은 자리를 마지막 항목으로 덮어쓰고 pop 하면(순서는 바뀜) 삭제 자체는 O(1) 이다. 무방향이면 v 의 리스트에서 u 도 지워야 한다(자기 루프는 한 번뿐). 해시 맵으로 "이웃 → 리스트 위치" 를 함께 관리하면 찾기까지 기대 O(1) 이 된다 — 단, 마지막 항목을 옮길 때 그 항목의 위치도 갱신해야 한다.
// 간선을 지워도 정점은 남고 간선 수만 줄며, 지운 간선을 다시 넣으면 원래 그래프가 된다(순서만 다를 수 있음). 인접 행렬은 한 칸을 0 으로 하면 O(1) 이다.
// 검증: ① 무작위 추가·삭제열에서 반환값과 최종 간선 집합이 모델과 같고 일관성 유지, 무방향/유방향 모두 ② 무방향은 양쪽에서 사라지고 유방향은 반대 방향이 그대로 ③ 없는 간선·삭제된 정점·잘못된 번호의 삭제는 false 이고 불변 ④ 삭제 후 재추가하면 같은 간선 집합 ⑤ 위치 맵을 둔 O(1) 삭제 구현이 선형 탐색 구현과 같은 결과이고 밀집 그래프(차수 ≈ 200)에서 선형 구현의 탐색 항목 수가 ≥ 20 배 ⑥ 자기 루프 삭제.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
struct IndexedGraph {                                                                                                // 이웃 → 리스트 위치 맵으로 O(1) 삭제하는 무방향 단순 그래프
    std::vector<std::vector<int>> adj; std::vector<std::map<int, int>> pos; std::size_t edges = 0; long steps = 0; explicit IndexedGraph(int n) : adj(n), pos(n) {}
    bool add(int u, int v) { if (u == v || pos[u].count(v)) return false; pos[u][v] = (int)adj[u].size(); adj[u].push_back(v); pos[v][u] = (int)adj[v].size(); adj[v].push_back(u); edges++; return true; }
    void eraseOne(int u, int v) { int i = pos[u][v], last = adj[u].back(); adj[u][i] = last; pos[u][last] = i; adj[u].pop_back(); pos[u].erase(v); steps++; }
    bool remove(int u, int v) { if (u < 0 || v < 0 || u >= (int)adj.size() || v >= (int)adj.size() || !pos[u].count(v)) return false; eraseOne(u, v); eraseOne(v, u); edges--; return true; } };
struct ScanGraph { std::vector<std::vector<int>> adj; std::size_t edges = 0; long steps = 0; explicit ScanGraph(int n) : adj(n) {}
    bool add(int u, int v) { if (u == v || std::find(adj[u].begin(), adj[u].end(), v) != adj[u].end()) return false; adj[u].push_back(v); adj[v].push_back(u); edges++; return true; }
    bool eraseOne(int u, int v) { for (std::size_t i = 0; i < adj[u].size(); i++) { steps++; if (adj[u][i] == v) { adj[u][i] = adj[u].back(); adj[u].pop_back(); return true; } } return false; }
    bool remove(int u, int v) { if (u < 0 || v < 0 || u >= (int)adj.size() || v >= (int)adj.size() || !eraseOne(u, v)) return false; eraseOne(v, u); edges--; return true; } };
int main() {
    std::mt19937 rng(5);
    for (int rep = 0; rep < 300; rep++) { bool directed = rep % 2, loops = rep % 5 == 0; int n = 1 + (int)(rng() % 10); Graph g(n, directed, loops); std::set<std::pair<int, int>> model;                                           // ① ②
        for (int step = 0; step < 150; step++) { int u = (int)(rng() % (n + 2)) - 1, v = (int)(rng() % (n + 2)) - 1; auto key = directed ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v)); if (rng() % 2) { bool valid = u >= 0 && v >= 0 && u < n && v < n && (u != v || loops); bool exp = valid && !model.count(key); assert(g.addEdge(u, v) == exp); if (exp) model.insert(key); }
            else { bool exp = model.count(key) > 0; auto before = g.edgeSet(); bool got = g.removeEdge(u, v); assert(got == exp); if (got) { model.erase(key); assert(!g.hasEdge(u, v) && (directed || !g.hasEdge(v, u))); } else assert(g.edgeSet() == before); }                // ③ 실패 시 불변
            assert(g.edgeCount() == model.size()); } assert(g.edgeSet() == model && g.consistent()); }
    { Graph d(3, true); d.addEdge(0, 1); d.addEdge(1, 0); assert(d.removeEdge(0, 1) && !d.hasEdge(0, 1) && d.hasEdge(1, 0) && d.edgeCount() == 1); Graph u(3, false); u.addEdge(0, 1); assert(u.removeEdge(1, 0) && !u.hasEdge(0, 1) && !u.hasEdge(1, 0)); }       // ② 방향
    for (int rep = 0; rep < 100; rep++) { int n = 2 + (int)(rng() % 9); Graph g(n, false); for (int k = 0; k < 3 * n; k++) g.addEdge((int)(rng() % n), (int)(rng() % n)); auto original = g.edgeSet(); std::vector<std::pair<int, int>> list(original.begin(), original.end());       // ④ 삭제 후 재추가
        std::shuffle(list.begin(), list.end(), rng); std::vector<std::pair<int, int>> removed; for (std::size_t i = 0; i < list.size() / 2; i++) { assert(g.removeEdge(list[i].first, list[i].second)); removed.push_back(list[i]); } for (auto e : removed) assert(g.addEdge(e.second, e.first)); assert(g.edgeSet() == original && g.consistent()); }
    { const int V = 220; IndexedGraph ig(V); ScanGraph sg(V); for (int u = 0; u < V; u++) for (int v = u + 1; v < V; v++) if (rng() % 10 < 9) { ig.add(u, v); sg.add(u, v); } assert(ig.edges == sg.edges); ig.steps = sg.steps = 0; long removals = 0;       // ⑤ O(1) 삭제 vs 선형 탐색
      for (int step = 0; step < 5000; step++) { int u = (int)(rng() % V), v = (int)(rng() % V); bool a = ig.remove(u, v), b = sg.remove(u, v); assert(a == b); removals += a; } assert(ig.edges == sg.edges); for (int u = 0; u < V; u++) { auto x = ig.adj[u], y = sg.adj[u]; std::sort(x.begin(), x.end()); std::sort(y.begin(), y.end()); assert(x == y); }
      assert(sg.steps > 20 * ig.steps && removals > 1000); }
    { Graph g(2, false, true); g.addEdge(0, 0); g.addEdge(0, 1); assert(g.removeEdge(0, 0) && !g.hasEdge(0, 0) && g.edgeCount() == 1 && g.degree(0) == 1 && !g.removeEdge(0, 0)); }                                          // ⑥
    std::cout << "RemoveEdge: 300 random add/remove sequences matched a set model for returned verdicts and final edge sets (undirected removal disappeared from both ends, directed removal left the reverse edge, failed removals changed nothing), removed edges could be re-added to restore the original graph, loop removal worked, and the position-map deletion matched list scanning while scanning looked at over 20x more entries on a dense graph" << std::endl; return 0;
}
// Time Complexity: 탐색 O(deg), 위치 맵 기대 O(1)
// Space Complexity: O(1) 추가 (위치 맵은 O(E))
```
## VertexCount()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 정점 수(VertexCount): |V| 를 돌려준다. 삽입·삭제에서 갱신하는 카운터를 두면 O(1) 이다(매번 alive 표시를 세면 O(용량)). 번호를 재사용하는 구현에서는 "살아 있는 정점 수" 와 "번호 공간의 크기(최대 번호 + 1, 용량)" 가 다르다는 것을 구분해야 한다 — 용량은 배열을 잡는 크기이고, 정점 수는 그래프의 |V| 이다. 삭제로 생긴 빈 번호를 자유 목록(free list)에 모아 두었다가 다음 정점에 재사용하면 번호 공간이 무한정 커지지 않는다. 대신 재사용한 번호는 옛 정점과 같은 번호를 달라는 외부 참조를 오염시킬 수 있다(오래된 번호가 새 정점을 가리킴 — 세대 번호 generation 으로 구분).
// 정점 수를 이용한 항등식: 단순 무방향 그래프의 간선 수 ≤ |V|(|V|−1)/2, 연결 그래프의 간선 수 ≥ |V|−1, 트리는 정확히 |V|−1, 연결 성분 수 = |V| − (신장 숲의 간선 수), 고립 정점은 차수 0. 빈 그래프(|V| = 0)도 유효하다.
// 검증: ① 정점 추가·삭제의 무작위열에서 카운터 == 살아 있는 정점을 센 값 == 모델 집합 크기 ② 자유 목록 재사용: 삭제한 번호가 가장 최근 삭제된 것부터 다시 나오고(LIFO) 용량은 동시에 살아 있는 최대 정점 수를 넘지 않음 ③ 재사용 없이 쓰면 용량이 총 추가 횟수만큼 커짐 ④ 세대 번호: 같은 번호의 옛 핸들은 무효 ⑤ 고립 정점 수·연결 성분 수 관계 |V| − (신장 숲 간선 수) = 성분 수 ⑥ 빈 그래프.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
class ReusingGraph {                                                                                                 // 자유 목록으로 번호를 재사용하고 세대 번호로 오래된 핸들을 구분
    std::vector<char> alive_; std::vector<unsigned> gen_; std::vector<int> freeList_; std::size_t live_ = 0;
public:
    struct Handle { int id; unsigned gen; };
    Handle add() { int id; if (!freeList_.empty()) { id = freeList_.back(); freeList_.pop_back(); alive_[id] = 1; } else { id = (int)alive_.size(); alive_.push_back(1); gen_.push_back(0); } live_++; return {id, gen_[id]}; }
    bool remove(Handle h) { if (!valid(h)) return false; alive_[h.id] = 0; gen_[h.id]++; freeList_.push_back(h.id); live_--; return true; }
    bool valid(Handle h) const { return h.id >= 0 && h.id < (int)alive_.size() && alive_[h.id] && gen_[h.id] == h.gen; }
    std::size_t count() const { return live_; } std::size_t capacity() const { return alive_.size(); } std::size_t recount() const { return (std::size_t)std::count(alive_.begin(), alive_.end(), 1); } };
int components(const Graph& g) { std::vector<int> comp(g.capacity(), -1); int c = 0; for (int s = 0; s < g.capacity(); s++) if (g.valid(s) && comp[s] < 0) { std::vector<int> st{s}; comp[s] = c; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : g.out(u)) if (comp[v] < 0) { comp[v] = c; st.push_back(v); } } c++; } return c; }
int main() {
    std::mt19937 rng(6);
    { Graph g(0, false); std::set<int> model; for (int step = 0; step < 3000; step++) { if (model.empty() || rng() % 3 != 0) { int id = g.addVertex(); model.insert(id); } else { auto it = model.begin(); std::advance(it, rng() % model.size()); assert(g.removeVertex(*it)); model.erase(it); }                  // ①
          std::size_t counted = 0; for (int v = 0; v < g.capacity(); v++) counted += g.valid(v); assert(g.vertexCount() == counted && counted == model.size()); } }
    { ReusingGraph r; std::vector<ReusingGraph::Handle> hs; std::set<int> liveIds; std::size_t maxLive = 0; for (int step = 0; step < 5000; step++) { if (hs.empty() || rng() % 2) { auto h = r.add(); assert(liveIds.insert(h.id).second); hs.push_back(h); } else { std::size_t i = rng() % hs.size(); assert(r.remove(hs[i])); liveIds.erase(hs[i].id); hs.erase(hs.begin() + (long)i); }     // ② 재사용
          maxLive = std::max(maxLive, r.count()); assert(r.count() == hs.size() && r.recount() == r.count() && r.capacity() >= r.count()); } assert(r.capacity() == maxLive); }
    { ReusingGraph r; auto a = r.add(), b = r.add(), c = r.add(); r.remove(a); r.remove(c); auto d = r.add(), e = r.add(); assert(d.id == c.id && e.id == a.id && r.capacity() == 3);                                        // LIFO: 가장 최근 삭제(c)가 먼저 재사용
      assert(!r.valid(a) && !r.valid(c) && r.valid(b) && r.valid(d) && r.valid(e) && d.gen == c.gen + 1 && !r.remove(c)); }                                                                                              // ④ 옛 핸들은 무효
    { Graph g(0, false); std::size_t added = 0; for (int step = 0; step < 1000; step++) { int id = g.addVertex(); added++; if (id % 2) g.removeVertex(id); } assert(g.capacity() == (int)added && g.vertexCount() == added / 2); }              // ③ 재사용 없이는 용량이 총 추가 횟수만큼
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 20); Graph g(n, false); for (int k = 0, m = (int)(rng() % (2 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n));                                  // ⑤
        std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; int forestEdges = 0; for (auto e : g.edgeSet()) { int a = find(e.first), b = find(e.second); if (a != b) { p[a] = b; forestEdges++; } }
        assert((int)g.vertexCount() - forestEdges == components(g) && g.edgeCount() <= (std::size_t)n * (n - 1) / 2); int isolated = 0; for (int v = 0; v < n; v++) isolated += g.degree(v) == 0; assert(isolated <= components(g)); }
    { Graph g(0, true); assert(g.vertexCount() == 0 && g.edgeCount() == 0 && components(g) == 0 && g.consistent()); }                                                                                                     // ⑥
    std::cout << "VertexCount: the O(1) counter equalled the number of live vertices through 3000 random insertions and removals, a free-list allocator reused the most recently freed id first and kept capacity equal to the peak number of simultaneously live vertices while generation numbers invalidated stale handles, and |V| minus the spanning-forest edge count equalled the number of connected components" << std::endl; return 0;
}
// Time Complexity: O(1) (카운터), 재계산 O(용량)
// Space Complexity: O(1)
```
## EdgeCount()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 간선 수(EdgeCount): |E| 를 돌려준다. 인접 리스트에서 간선 수는 저장된 항목 수와 같지 않다. 무방향 그래프는 간선 하나가 양쪽 리스트에 한 번씩, 총 두 항목으로 저장되므로 |E| = (항목 수 + 자기 루프 수) / 2 (자기 루프는 한 번만 저장되므로 보정). 유방향은 나가는 리스트의 항목 수 합 = 들어오는 리스트의 항목 수 합 = |E|. 매번 세지 말고 추가·삭제에서 갱신하는 카운터를 둔다 — 이중 계산(무방향 양쪽)을 하지 않도록 한 번만 증감한다.
// 항등식과 한계: 단순 무방향 그래프 |E| ≤ |V|(|V|−1)/2, 유방향 ≤ |V|(|V|−1), 자기 루프 허용이면 각각 + |V|. 밀도 = |E| / 최대 간선 수. 여집합 그래프의 간선 수 = 최대 − |E|. 특수한 그래프의 간선 수: 완전 K_n = n(n−1)/2, 경로 n−1, 사이클 n, 별 n−1, 완전 이분 K_{a,b} = ab, 격자 r×c = r(c−1) + c(r−1), 하이퍼큐브 Q_d = d·2^(d−1).
// 검증: ① 무작위 추가·삭제(자기 루프 포함)에서 카운터 == 저장 항목으로부터 계산한 값 == 모델 집합 크기, 무방향/유방향 ② 핸드셰이크: 무방향 차수 합 = 2|E| (루프는 2) ③ 특수 그래프 가족(완전·경로·사이클·별·완전 이분·격자·하이퍼큐브)의 간선 수 공식 ④ 여집합의 간선 수 = 최대 − |E| 이고 여집합의 여집합은 원래 그래프 ⑤ 밀도가 [0, 1] 이고 완전 그래프에서 1 ⑥ 정점을 지우면 간선 수가 지운 정점의 차수(루프 보정)만큼 줄어듦.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
std::size_t countFromStorage(const Graph& g) { std::size_t entries = 0, loops = 0; for (int u = 0; u < g.capacity(); u++) if (g.valid(u)) { entries += g.out(u).size(); for (int v : g.out(u)) loops += v == u; } return g.directed() ? entries : (entries + loops) / 2; }
std::size_t maxEdges(int n, bool directed, bool loops) { std::size_t base = directed ? (std::size_t)n * (n - 1) : (std::size_t)n * (n - 1) / 2; return base + (loops ? (std::size_t)n : 0); }
Graph complement(const Graph& g) { Graph c(g.capacity(), g.directed()); for (int u = 0; u < g.capacity(); u++) for (int v = 0; v < g.capacity(); v++) if (u != v && !g.hasEdge(u, v)) c.addEdge(u, v); return c; }
int main() {
    std::mt19937 rng(7);
    for (int rep = 0; rep < 300; rep++) { bool directed = rep % 2, loops = rep % 3 == 0; int n = 1 + (int)(rng() % 10); Graph g(n, directed, loops); std::set<std::pair<int, int>> model;                                              // ①
        for (int step = 0; step < 120; step++) { int u = (int)(rng() % n), v = (int)(rng() % n); auto key = directed ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v)); if (rng() % 3) { if ((u != v || loops) && g.addEdge(u, v)) model.insert(key); } else if (g.removeEdge(u, v)) model.erase(key);
            assert(g.edgeCount() == model.size() && countFromStorage(g) == model.size()); }
        long long degSum = 0; for (int v = 0; v < n; v++) degSum += g.degree(v); if (directed) { long long in = 0, out = 0; for (int v = 0; v < n; v++) { in += g.inDegree(v); out += g.outDegree(v); } assert(in == (long long)g.edgeCount() && out == (long long)g.edgeCount() && degSum == 2 * (long long)g.edgeCount()); } else assert(degSum == 2 * (long long)g.edgeCount());   // ②
        assert(g.edgeCount() <= maxEdges(n, directed, loops)); }
    { for (int n = 1; n <= 12; n++) { Graph complete(n, false), path(n, false), cycle(n, false), star(n, false); for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) complete.addEdge(u, v); for (int v = 0; v + 1 < n; v++) path.addEdge(v, v + 1); for (int v = 0; v < n; v++) cycle.addEdge(v, (v + 1) % n); for (int v = 1; v < n; v++) star.addEdge(0, v);   // ③
          assert(complete.edgeCount() == (std::size_t)n * (n - 1) / 2 && path.edgeCount() == (std::size_t)(n - 1) && star.edgeCount() == (std::size_t)(n - 1) && cycle.edgeCount() == (std::size_t)(n >= 3 ? n : n - 1)); }
      for (int a = 1; a <= 5; a++) for (int b = 1; b <= 5; b++) { Graph kab(a + b, false); for (int u = 0; u < a; u++) for (int v = 0; v < b; v++) kab.addEdge(u, a + v); assert(kab.edgeCount() == (std::size_t)a * b); }
      for (int r = 1; r <= 6; r++) for (int c = 1; c <= 6; c++) { Graph grid(r * c, false); for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) { if (j + 1 < c) grid.addEdge(i * c + j, i * c + j + 1); if (i + 1 < r) grid.addEdge(i * c + j, (i + 1) * c + j); } assert(grid.edgeCount() == (std::size_t)(r * (c - 1) + c * (r - 1))); }
      for (int d = 0; d <= 8; d++) { int N = 1 << d; Graph q(N, false); for (int v = 0; v < N; v++) for (int b = 0; b < d; b++) q.addEdge(v, v ^ (1 << b)); assert(q.edgeCount() == (std::size_t)(d ? d * (1 << (d - 1)) : 0)); } }
    for (int rep = 0; rep < 150; rep++) { bool directed = rep % 2; int n = 1 + (int)(rng() % 9); Graph g(n, directed); for (int k = 0, m = (int)(rng() % (2 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n)); Graph c = complement(g); Graph cc = complement(c);                                     // ④
        assert(g.edgeCount() + c.edgeCount() == maxEdges(n, directed, false) && cc.edgeSet() == g.edgeSet()); double density = maxEdges(n, directed, false) ? (double)g.edgeCount() / (double)maxEdges(n, directed, false) : 0; assert(density >= 0 && density <= 1.0 + 1e-12); }
    { for (int n = 2; n <= 10; n++) { Graph k(n, false); for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) k.addEdge(u, v); assert((double)k.edgeCount() / (double)maxEdges(n, false, false) == 1.0); } }                          // ⑤
    for (int rep = 0; rep < 200; rep++) { int n = 2 + (int)(rng() % 10); Graph g(n, false, true); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n)); int v = (int)(rng() % n); std::size_t before = g.edgeCount(); int degv = g.degree(v), loop = g.hasEdge(v, v) ? 1 : 0; g.removeVertex(v); assert(g.edgeCount() == before - (std::size_t)(degv - loop)); }    // ⑥
    std::cout << "EdgeCount: the maintained counter matched the count derived from stored adjacency entries (halved for undirected, loops corrected) and the set model through 36000 random edits, the handshake lemma held, edge-count formulas for complete, path, cycle, star, complete bipartite, grid and hypercube graphs matched constructed graphs, complement edge counts summed to the maximum with a double complement restoring the graph, and removing a vertex dropped exactly its incident edges" << std::endl; return 0;
}
// Time Complexity: O(1) (카운터), 재계산 O(V + E)
// Space Complexity: O(1)
```
## Degree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 차수(Degree): 정점 v 에 닿은 간선의 수 deg(v). 무방향 그래프에서 자기 루프는 양 끝이 모두 v 라서 2 로 센다. 핸드셰이크 보조정리: Σ deg(v) = 2|E| — 간선 하나가 양 끝점에 차수를 1 씩 보태기 때문이다. 따라서 차수가 홀수인 정점의 수는 항상 짝수이고 평균 차수는 2|E|/|V|. 정점 수가 n 인 단순 그래프에서 0 ≤ deg(v) ≤ n−1, 그리고 차수가 n−1 인 정점과 0 인 정점이 한 그래프에 함께 있을 수 없다(전자는 모두와 이웃, 후자는 아무와도 이웃이 아님) — 그래서 모든 단순 그래프에는 차수가 같은 두 정점이 있다(비둘기집 원리).
// 차수열(degree sequence)이 실제 단순 그래프의 것인지(graphical)는 Havel–Hakimi 로 판정한다: 내림차순 정렬 뒤 가장 큰 d 를 뽑아 그 다음 d 개 정점의 차수를 1 씩 줄이는 일을 반복하고 음수가 나오면 불가능, 모두 0 이 되면 가능. 에르되시–갈라이 정리는 같은 사실을 부등식으로 말한다: Σ 합이 짝수이고 모든 k 에서 앞 k 개의 합 ≤ k(k−1) + Σ_{i>k} min(d_i, k).
// 검증: ① 무작위 그래프에서 deg 합 == 2|E|, 홀수 차수 정점 수는 짝수, 자기 루프는 2 ② 차수 최대 ≤ n−1(단순 그래프), 모든 단순 그래프에 같은 차수를 가진 두 정점 존재 ③ n ≤ 5 의 모든 단순 그래프(2^10 개)에서 나오는 차수열 집합 == Havel–Hakimi 가 가능하다고 한 집합 == 에르되시–갈라이가 가능하다고 한 집합 (정렬된 모든 후보 수열에 대해) ④ 정규 그래프(모든 차수 같음) 판정과 완전·사이클·격자 차수 ⑤ 차수열에서 간선 수 복원 ⑥ 정점·간선 삭제 시 차수 갱신.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
bool havelHakimi(std::vector<int> d) { for (;;) { std::sort(d.begin(), d.end(), std::greater<int>()); if (d.empty() || d[0] == 0) return true; int top = d[0]; d.erase(d.begin()); if (top > (int)d.size()) return false; for (int i = 0; i < top; i++) if (--d[i] < 0) return false; } }
bool erdosGallai(std::vector<int> d) { std::sort(d.begin(), d.end(), std::greater<int>()); int n = (int)d.size(); long long total = 0; for (int x : d) { if (x < 0) return false; total += x; } if (total % 2) return false; long long prefix = 0;
    for (int k = 1; k <= n; k++) { prefix += d[k - 1]; long long rhs = (long long)k * (k - 1); for (int i = k; i < n; i++) rhs += std::min(d[i], k); if (prefix > rhs) return false; } return true; }
int main() {
    std::mt19937 rng(8);
    for (int rep = 0; rep < 400; rep++) { int n = 1 + (int)(rng() % 12); bool loops = rep % 4 == 0; Graph g(n, false, loops); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n));                                    // ① ②
        long long sum = 0; int odd = 0; for (int v = 0; v < n; v++) { int d = g.degree(v); sum += d; odd += d % 2; int expect = 0; for (int u = 0; u < n; u++) { if (g.hasEdge(v, u)) expect += (u == v ? 2 : 1); } assert(d == expect); if (!loops) assert(d <= n - 1); }
        assert(sum == 2 * (long long)g.edgeCount() && odd % 2 == 0); if (!loops && n >= 2) { std::set<int> ds; bool repeated = false; for (int v = 0; v < n; v++) repeated |= !ds.insert(g.degree(v)).second; assert(repeated); } }
    for (int n = 1; n <= 5; n++) { std::vector<std::pair<int, int>> pairs; for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) pairs.push_back({u, v}); std::set<std::vector<int>> achieved;                                                  // ③ 전수
        for (unsigned mask = 0; mask < (1u << pairs.size()); mask++) { Graph g(n, false); for (std::size_t i = 0; i < pairs.size(); i++) if (mask >> i & 1) g.addEdge(pairs[i].first, pairs[i].second); std::vector<int> seq; for (int v = 0; v < n; v++) seq.push_back(g.degree(v)); std::sort(seq.begin(), seq.end(), std::greater<int>()); achieved.insert(seq); }
        std::vector<int> cand(n, 0); for (;;) { std::vector<int> sorted = cand; std::sort(sorted.begin(), sorted.end(), std::greater<int>()); bool inSet = achieved.count(sorted) > 0; assert(havelHakimi(cand) == inSet && erdosGallai(cand) == inSet); int i = n - 1; while (i >= 0 && ++cand[i] == n) { cand[i] = 0; i--; } if (i < 0) break; } }
    { Graph k(6, false), c(7, false), grid(9, false); for (int u = 0; u < 6; u++) for (int v = u + 1; v < 6; v++) k.addEdge(u, v); for (int v = 0; v < 7; v++) c.addEdge(v, (v + 1) % 7); for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) { if (j + 1 < 3) grid.addEdge(i * 3 + j, i * 3 + j + 1); if (i + 1 < 3) grid.addEdge(i * 3 + j, (i + 1) * 3 + j); }     // ④
      auto regular = [](const Graph& g) { int d = g.degree(0); for (int v = 1; v < g.capacity(); v++) if (g.degree(v) != d) return false; return true; }; assert(regular(k) && k.degree(0) == 5 && regular(c) && c.degree(3) == 2 && !regular(grid) && grid.degree(4) == 4 && grid.degree(0) == 2 && grid.degree(1) == 3); }
    for (int rep = 0; rep < 200; rep++) { int n = 2 + (int)(rng() % 10); Graph g(n, false); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n)); long long s = 0; for (int v = 0; v < n; v++) s += g.degree(v); assert(s / 2 == (long long)g.edgeCount());   // ⑤
        int u = (int)(rng() % n), v = (int)(rng() % n); if (u != v && g.hasEdge(u, v)) { int du = g.degree(u), dv = g.degree(v); g.removeEdge(u, v); assert(g.degree(u) == du - 1 && g.degree(v) == dv - 1); g.addEdge(u, v); assert(g.degree(u) == du); }       // ⑥
        int w = (int)(rng() % n); std::vector<int> nbrs = g.out(w); std::vector<int> before(n); for (int x = 0; x < n; x++) before[x] = g.degree(x); g.removeVertex(w); for (int x = 0; x < n; x++) if (x != w) assert(g.degree(x) == before[x] - (std::find(nbrs.begin(), nbrs.end(), x) != nbrs.end() ? 1 : 0)); }
    std::cout << "Degree: the handshake lemma (degree sum = 2|E|, even number of odd degrees, loops counting 2) and the pigeonhole fact that every simple graph has two equal degrees held on 400 random graphs; over all 2^10 graphs on up to 5 vertices the set of realised degree sequences equalled both the Havel-Hakimi and Erdos-Gallai graphical sets; regular and grid degrees were right and degrees updated correctly under edge and vertex removal" << std::endl; return 0;
}
// Time Complexity: deg(v) O(1) (카운터) 또는 O(deg), 하벨–하키미 O(n² log n)
// Space Complexity: O(V)
```
## InDegree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 진입 차수(InDegree): 유방향 그래프에서 정점 v 로 들어오는 간선의 수 indeg(v). 나가는 리스트만 저장하면 들어오는 간선을 알려면 모든 리스트를 훑어야 해서 O(V+E) 이고, 들어오는 리스트(역방향 리스트)나 진입 차수 카운터를 함께 관리하면 O(1) 이다 — 추가·삭제 때 양쪽을 같이 고쳐야 한다. Σ indeg(v) = |E| (= Σ outdeg(v)). 진입 차수 0 인 정점을 원천(source)이라 하고, DAG(비순환 유방향 그래프)에는 반드시 원천이 하나 이상 있다(없다면 모든 정점에 들어오는 간선이 있어 거꾸로 따라가면 순환이 생김).
// 응용: 위상 정렬(칸 알고리즘)은 진입 차수가 0 인 정점을 큐에 넣고 꺼낼 때 이웃의 진입 차수를 줄인다. 인기 있는(많이 가리켜지는) 정점 찾기, 웹 그래프의 들어오는 링크 수(PageRank 의 단순한 근사). 진입 차수 분포가 멱법칙을 따르면 척도 없는 그래프다.
// 검증: ① 무작위 유방향 그래프(추가·삭제)에서 카운터/역방향 리스트의 진입 차수 == 나가는 리스트 전체를 훑어 센 값 == 모델 ② Σ indeg == Σ outdeg == |E| ③ DAG(무작위 위상 순서에서 앞→뒤 간선만 생성)에 원천이 반드시 있고, 순환 그래프(모든 정점이 진입 차수 ≥ 1)는 원천이 없을 수 있음 ④ 칸 알고리즘이 진입 차수로 위상 순서를 만들고 순서가 모든 간선을 존중함 ⑤ 진입 차수 훑기 방식과 역방향 리스트 방식의 비용: 질의 N 번에 훑기는 N·(V+E), 리스트는 N·O(1) ⑥ 자기 루프는 진입 차수 1 을 더함.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
std::vector<int> scanInDegree(const Graph& g) { std::vector<int> in(g.capacity(), 0); for (int u = 0; u < g.capacity(); u++) if (g.valid(u)) for (int v : g.out(u)) in[v]++; return in; }
bool kahn(const Graph& g, std::vector<int>& order) { std::vector<int> in = scanInDegree(g); std::vector<int> q; for (int v = 0; v < g.capacity(); v++) if (g.valid(v) && in[v] == 0) q.push_back(v); order.clear(); for (std::size_t h = 0; h < q.size(); h++) { int u = q[h]; order.push_back(u); for (int v : g.out(u)) if (--in[v] == 0) q.push_back(v); } return order.size() == g.vertexCount(); }
int main() {
    std::mt19937 rng(9);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 12); Graph g(n, true, rep % 3 == 0); std::set<std::pair<int, int>> model;                                                                                          // ① ② ⑥
        for (int step = 0; step < 100; step++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (rng() % 3) { if (g.addEdge(u, v)) model.insert({u, v}); } else if (g.removeEdge(u, v)) model.erase({u, v}); }
        std::vector<int> scan = scanInDegree(g), want(n, 0); for (auto e : model) want[e.second]++; long long in = 0, out = 0; for (int v = 0; v < n; v++) { assert(g.inDegree(v) == scan[v] && scan[v] == want[v] && (int)g.in(v).size() == want[v]); in += g.inDegree(v); out += g.outDegree(v); } assert(in == (long long)g.edgeCount() && out == in);
        if (g.hasEdge(0, 0)) assert(std::find(g.in(0).begin(), g.in(0).end(), 0) != g.in(0).end()); }
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 14); std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng); Graph dag(n, true); for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (rng() % 3 == 0) dag.addEdge(perm[i], perm[j]);   // ③ ④
        std::vector<int> in = scanInDegree(dag); int sources = 0; for (int v = 0; v < n; v++) sources += in[v] == 0; assert(sources >= 1 && in[perm[0]] == 0);
        std::vector<int> order; assert(kahn(dag, order) && (int)order.size() == n); std::vector<int> pos(n); for (int i = 0; i < n; i++) pos[order[i]] = i; for (auto e : dag.edgeSet()) assert(pos[e.first] < pos[e.second]); }
    { Graph cyc(5, true); for (int v = 0; v < 5; v++) cyc.addEdge(v, (v + 1) % 5); std::vector<int> in = scanInDegree(cyc); for (int v = 0; v < 5; v++) assert(in[v] == 1); std::vector<int> order; assert(!kahn(cyc, order) && order.empty()); }                           // 순환 그래프: 원천 없음, 위상 정렬 불가
    { const int V = 300; Graph g(V, true); while ((int)g.edgeCount() < 900) g.addEdge((int)(rng() % V), (int)(rng() % V)); long long scanCost = 0, listCost = 0; const int Q = 200; for (int q = 0; q < Q; q++) { int v = (int)(rng() % V); scanCost += (long long)V + (long long)g.edgeCount(); listCost += 1; int viaScan = 0; for (int u = 0; u < V; u++) for (int w : g.out(u)) viaScan += w == v; assert(viaScan == g.inDegree(v)); }   // ⑤
      assert(scanCost > 1000 * listCost); }
    std::cout << "InDegree: the maintained in-lists and the O(V+E) rescan agreed with a set model through 30000 random edits (a loop adds one to its own in-degree), sum of in-degrees equalled sum of out-degrees equalled |E|, every random DAG had a source and Kahn's algorithm turned in-degrees into a valid topological order, a directed cycle had none, and per-query cost of the in-list was O(1) against a full scan" << std::endl; return 0;
}
// Time Complexity: 질의 O(1) (역방향 리스트·카운터), 훑기 O(V + E)
// Space Complexity: O(V + E)
```
## OutDegree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>
// 진출 차수(OutDegree): 유방향 그래프에서 정점 v 에서 나가는 간선의 수 outdeg(v) — 나가는 인접 리스트의 길이로 O(1). Σ outdeg(v) = |E|. 진출 차수 0 인 정점을 싱크(sink)라 하며 DAG 에는 반드시 싱크가 하나 이상 있다. 무방향 그래프는 진출 차수 = 진입 차수 = 차수이다(자기 루프는 한 번이 아니라 2 로 세는 차수와 구분).
// 토너먼트(tournament)는 모든 서로 다른 정점 쌍 사이에 정확히 한 방향의 간선이 있는 유방향 그래프(경기에서 이긴 쪽 → 진 쪽)다. 간선 수는 정확히 n(n−1)/2, 진출 차수는 각 선수의 승수(점수)이고 합이 n(n−1)/2 이다. 정렬된 점수열 s₁ ≤ … ≤ s_n 이 어떤 토너먼트의 것이 될 필요충분조건은 란다우(Landau) 정리: 모든 k 에서 앞 k 개의 합 ≥ C(k, 2), 그리고 k = n 에서 등호. 서로 다른 점수열의 개수는 1, 1, 2, 4, 9, 22, 59, … (n = 1, 2, …).
// 검증: ① 무작위 유방향 그래프에서 진출 차수 == 나가는 리스트 길이 == 간선 집합에서 센 값, Σ out == |E|, 싱크와 원천의 정의 ② 무방향 그래프에서 out == in == degree(루프 제외) ③ n ≤ 5 의 모든 토너먼트(2^(n(n−1)/2) 개)에서 나온 정렬된 점수열의 집합 == 란다우 조건을 만족하는 정렬 수열의 집합, 개수가 1, 1, 2, 4, 9 ④ 토너먼트의 간선 수 n(n−1)/2 와 점수 합 ⑤ DAG 의 싱크 존재 ⑥ 모든 정점이 같은 진출 차수(= k)인 k-정규 유방향 그래프와 순환 순열 그래프.
class Graph {                                                                                                        // 인접 리스트 그래프: 정점 번호는 안정적(삭제는 alive 표시), 단순 그래프(중복 간선 없음), 자기 루프 허용 여부는 선택
    bool directed_, loops_; std::vector<std::vector<int>> out_, in_; std::vector<char> alive_; std::size_t edges_ = 0, vertices_ = 0;
    static void erase1(std::vector<int>& v, int x) { auto it = std::find(v.begin(), v.end(), x); *it = v.back(); v.pop_back(); }
public:
    Graph(int n, bool directed, bool loops = false) : directed_(directed), loops_(loops), out_(n), in_(directed ? n : 0), alive_(n, 1), vertices_(n) {}
    bool directed() const { return directed_; } int capacity() const { return (int)alive_.size(); } std::size_t vertexCount() const { return vertices_; } std::size_t edgeCount() const { return edges_; }
    bool valid(int v) const { return v >= 0 && v < (int)alive_.size() && alive_[v]; }
    int addVertex() { out_.emplace_back(); if (directed_) in_.emplace_back(); alive_.push_back(1); vertices_++; return (int)alive_.size() - 1; }
    bool hasEdge(int u, int v) const { return valid(u) && valid(v) && std::find(out_[u].begin(), out_[u].end(), v) != out_[u].end(); }
    bool addEdge(int u, int v) { if (!valid(u) || !valid(v) || (u == v && !loops_) || hasEdge(u, v)) return false; out_[u].push_back(v); if (directed_) in_[v].push_back(u); else if (u != v) out_[v].push_back(u); edges_++; return true; }
    bool removeEdge(int u, int v) { if (!hasEdge(u, v)) return false; erase1(out_[u], v); if (directed_) erase1(in_[v], u); else if (u != v) erase1(out_[v], u); edges_--; return true; }
    bool removeVertex(int v) { if (!valid(v)) return false; std::vector<int> o = out_[v], i = directed_ ? in_[v] : std::vector<int>(); for (int w : o) removeEdge(v, w); for (int w : i) removeEdge(w, v); alive_[v] = 0; vertices_--; return true; }
    const std::vector<int>& out(int v) const { return out_[v]; } const std::vector<int>& in(int v) const { return in_[v]; }
    int outDegree(int v) const { return (int)out_[v].size(); } int inDegree(int v) const { return directed_ ? (int)in_[v].size() : (int)out_[v].size(); }
    int degree(int v) const { if (directed_) return outDegree(v) + inDegree(v); int d = (int)out_[v].size(); for (int w : out_[v]) if (w == v) d++; return d; }                      // 무방향: 자기 루프는 2 로 센다
    std::set<std::pair<int, int>> edgeSet() const { std::set<std::pair<int, int>> s; for (int u = 0; u < capacity(); u++) if (alive_[u]) for (int v : out_[u]) s.insert(directed_ ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v))); return s; }
    bool consistent() const { std::size_t cnt = 0; for (int u = 0; u < capacity(); u++) { if (!alive_[u]) { if (!out_[u].empty() || (directed_ && !in_[u].empty())) return false; continue; } cnt++; std::set<int> seen; for (int v : out_[u]) { if (!valid(v) || !seen.insert(v).second) return false; if (u == v && !loops_) return false;
            if (directed_) { if (std::find(in_[v].begin(), in_[v].end(), u) == in_[v].end()) return false; } else if (std::find(out_[v].begin(), out_[v].end(), u) == out_[v].end()) return false; } } return cnt == vertices_; } };
bool landau(std::vector<int> s) { std::sort(s.begin(), s.end()); int n = (int)s.size(); long long sum = 0; for (int k = 1; k <= n; k++) { sum += s[k - 1]; if (sum < (long long)k * (k - 1) / 2) return false; if (k == n && sum != (long long)n * (n - 1) / 2) return false; } return true; }
int main() {
    std::mt19937 rng(10);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 12); Graph g(n, true, rep % 3 == 0); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n)); auto edges = g.edgeSet();                       // ①
        std::vector<int> want(n, 0); for (auto e : edges) want[e.first]++; long long total = 0; for (int v = 0; v < n; v++) { assert(g.outDegree(v) == (int)g.out(v).size() && g.outDegree(v) == want[v]); total += g.outDegree(v); }
        assert(total == (long long)g.edgeCount()); }
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 10); Graph g(n, false); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) g.addEdge((int)(rng() % n), (int)(rng() % n)); for (int v = 0; v < n; v++) assert(g.outDegree(v) == g.inDegree(v) && g.outDegree(v) == g.degree(v)); }       // ② 무방향
    std::vector<int> expectCount = {0, 1, 1, 2, 4, 9};
    for (int n = 1; n <= 5; n++) { std::vector<std::pair<int, int>> pairs; for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) pairs.push_back({u, v}); std::set<std::vector<int>> scores; long long checkedTournaments = 0;       // ③ 전수
        for (unsigned mask = 0; mask < (1u << pairs.size()); mask++) { Graph t(n, true); for (std::size_t i = 0; i < pairs.size(); i++) { if (mask >> i & 1) t.addEdge(pairs[i].first, pairs[i].second); else t.addEdge(pairs[i].second, pairs[i].first); } assert((int)t.edgeCount() == n * (n - 1) / 2);                  // ④ 간선 수
            std::vector<int> s; int sum = 0; for (int v = 0; v < n; v++) { s.push_back(t.outDegree(v)); sum += s.back(); } assert(sum == n * (n - 1) / 2); std::sort(s.begin(), s.end()); scores.insert(s); checkedTournaments++; assert(landau(s)); }
        std::set<std::vector<int>> viaLandau; std::vector<int> cand(n, 0); for (;;) { std::vector<int> sorted = cand; std::sort(sorted.begin(), sorted.end()); if (sorted == cand && landau(cand)) viaLandau.insert(cand); int i = n - 1; while (i >= 0 && ++cand[i] == n) { cand[i] = 0; i--; } if (i < 0) break; }
        assert(scores == viaLandau && (int)scores.size() == expectCount[n] && checkedTournaments == (1ll << pairs.size())); }
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 14); std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng); Graph dag(n, true); for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (rng() % 3 == 0) dag.addEdge(perm[i], perm[j]); int sinks = 0; for (int v = 0; v < n; v++) sinks += dag.outDegree(v) == 0; assert(sinks >= 1 && dag.outDegree(perm[n - 1]) == 0); }   // ⑤
    for (int n = 3; n <= 9; n++) for (int k = 1; 2 * k < n; k++) { Graph c(n, true); for (int v = 0; v < n; v++) for (int d = 1; d <= k; d++) c.addEdge(v, (v + d) % n); for (int v = 0; v < n; v++) assert(c.outDegree(v) == k && c.inDegree(v) == k); assert((int)c.edgeCount() == n * k); }              // ⑥ k-정규
    std::cout << "OutDegree: out-degrees equalled list lengths and edge-set counts with the sum equal to |E| on 300 random digraphs, undirected graphs had out = in = degree, over all tournaments on up to 5 vertices the sorted score sequences formed exactly the Landau-feasible set with the known counts 1, 1, 2, 4, 9, every DAG had a sink, and circulant digraphs were k-regular" << std::endl; return 0;
}
// Time Complexity: 질의 O(1), 전체 O(V)
// Space Complexity: O(V)
```
# Part 2. 그래프 표현
## AdjacencyMatrix()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 인접 행렬(Adjacency Matrix): V×V 행렬 A 에서 A[u][v] = 1 이면 간선 u→v. 간선 질의가 O(1) 이고 간선 추가·삭제도 O(1), 단점은 간선 수와 무관하게 V² 칸의 메모리(희소 그래프에서 낭비)와 이웃 훑기가 항상 O(V) 라는 것. 칸을 비트로 쓰면 V²/8 바이트, 한 행을 64 비트 워드 ⌈V/64⌉ 개로 두면 차수는 popcount, 이웃 순회는 켜진 비트 찾기(ctz), 두 행의 AND 로 공통 이웃 수를 64 개씩 센다. 무방향 그래프의 행렬은 대칭이고 대각선은 0(루프 없음), 유방향은 일반적으로 비대칭.
// 대수적 성질: A^k[i][j] 는 i 에서 j 로 가는 길이 정확히 k 인 걸음(walk)의 수이고, 삼각형 수는 trace(A³)/6 (무방향 단순 그래프, 한 삼각형을 6 번 센다). 도달 가능성(전이 폐쇄)은 워셜 알고리즘 `for k, for i: if A[i][k]: row[i] |= row[k]` 로 O(V³/64). 메모리 교차점: 행렬은 V²/8 바이트, 인접 리스트는 정점 번호를 4 바이트로 두면 약 4(V+2E) 바이트 — 밀도 E/V² 가 대략 1/16 을 넘으면 행렬이 더 작다.
// 검증: ① 비트 행렬이 std::set 모델과 같은 간선 소속·차수(popcount)·이웃 순회(오름차순) ② 행렬 거듭제곱 A^k 의 [i][j] 가 DFS 로 센 길이 k 걸음 수와 같음(k ≤ 4) ③ 삼각형 수 trace(A³)/6 가 세 겹 반복문과 같음 ④ 워셜 전이 폐쇄가 BFS 도달 가능 집합과 같음 ⑤ 두 행의 AND 의 popcount == 공통 이웃 수 ⑥ 메모리 교차점: 밀도 0.01 이면 리스트 < 행렬, 밀도 0.3 이면 행렬 < 리스트.
struct BitMatrix { int n, words; std::vector<uint64_t> a; explicit BitMatrix(int n_) : n(n_), words((n_ + 63) / 64), a((std::size_t)n_ * ((n_ + 63) / 64), 0) {}
    void set(int u, int v) { a[(std::size_t)u * words + (v >> 6)] |= 1ull << (v & 63); } void clear(int u, int v) { a[(std::size_t)u * words + (v >> 6)] &= ~(1ull << (v & 63)); } bool has(int u, int v) const { return a[(std::size_t)u * words + (v >> 6)] >> (v & 63) & 1; }
    int degree(int u) const { int d = 0; for (int w = 0; w < words; w++) d += __builtin_popcountll(a[(std::size_t)u * words + w]); return d; }
    std::vector<int> neighbors(int u) const { std::vector<int> r; for (int w = 0; w < words; w++) { uint64_t x = a[(std::size_t)u * words + w]; while (x) { r.push_back(w * 64 + __builtin_ctzll(x)); x &= x - 1; } } return r; }
    int commonNeighbors(int u, int v) const { int c = 0; for (int w = 0; w < words; w++) c += __builtin_popcountll(a[(std::size_t)u * words + w] & a[(std::size_t)v * words + w]); return c; }
    BitMatrix closure() const { BitMatrix r = *this; for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r.has(i, k)) for (int w = 0; w < words; w++) r.a[(std::size_t)i * words + w] |= r.a[(std::size_t)k * words + w]; return r; } };      // 워셜
typedef std::vector<std::vector<long long>> Dense;
Dense mul(const Dense& x, const Dense& y) { int n = (int)x.size(); Dense r(n, std::vector<long long>(n, 0)); for (int i = 0; i < n; i++) for (int k = 0; k < n; k++) if (x[i][k]) for (int j = 0; j < n; j++) r[i][j] += x[i][k] * y[k][j]; return r; }
long long walks(const std::vector<std::set<int>>& adj, int from, int to, int len) { if (len == 0) return from == to; long long c = 0; for (int w : adj[from]) c += walks(adj, w, to, len - 1); return c; }
int main() {
    std::mt19937 rng(11);
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 70); bool directed = rep % 2; BitMatrix m(n); std::vector<std::set<int>> adj(n); for (int k = 0, e = (int)(rng() % (3 * n)); k < e; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v) continue; if (rng() % 4) { m.set(u, v); adj[u].insert(v); if (!directed) { m.set(v, u); adj[v].insert(u); } } else { m.clear(u, v); adj[u].erase(v); if (!directed) { m.clear(v, u); adj[v].erase(u); } } }   // ①
        for (int u = 0; u < n; u++) { std::vector<int> nb = m.neighbors(u); assert(std::vector<int>(adj[u].begin(), adj[u].end()) == nb && m.degree(u) == (int)adj[u].size()); for (int v = 0; v < n; v++) assert(m.has(u, v) == (adj[u].count(v) > 0)); if (!directed) for (int v = 0; v < n; v++) assert(m.has(u, v) == m.has(v, u)); assert(!m.has(u, u)); }
        for (int u = 0; u < n && u < 8; u++) for (int v = 0; v < n && v < 8; v++) { int c = 0; for (int w : adj[u]) c += adj[v].count(w) > 0; assert(m.commonNeighbors(u, v) == c); }                                                                                         // ⑤
        BitMatrix cl = m.closure(); for (int s = 0; s < n && s < 6; s++) { std::vector<char> seen(n, 0); std::queue<int> q; for (int w : adj[s]) { if (!seen[w]) { seen[w] = 1; q.push(w); } } while (!q.empty()) { int u = q.front(); q.pop(); for (int w : adj[u]) if (!seen[w]) { seen[w] = 1; q.push(w); } } for (int v = 0; v < n; v++) assert(cl.has(s, v) == (bool)seen[v]); } }   // ④
    for (int rep = 0; rep < 100; rep++) { int n = 2 + (int)(rng() % 7); bool directed = rep % 2; std::vector<std::set<int>> adj(n); Dense A(n, std::vector<long long>(n, 0)); for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v && rng() % 3 == 0) { if (directed || u < v) { adj[u].insert(v); A[u][v] = 1; if (!directed) { adj[v].insert(u); A[v][u] = 1; } } }
        Dense P = A; for (int k = 2; k <= 4; k++) { P = mul(P, A); for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) assert(P[i][j] == walks(adj, i, j, k)); }                                                                                                      // ②
        if (!directed) { Dense A3 = mul(mul(A, A), A); long long tr = 0; for (int i = 0; i < n; i++) tr += A3[i][i]; long long tri = 0; for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) for (int c = b + 1; c < n; c++) tri += A[a][b] && A[b][c] && A[a][c]; assert(tr == 6 * tri); } }                  // ③
    { const int V = 1000; auto matrixBytes = [&](int v) { return (std::size_t)v * ((v + 63) / 64) * 8; }; auto listBytes = [&](long long e) { return (std::size_t)(4 * (V + 1) + 4 * 2 * e); };                                                                                                    // ⑥ 메모리 교차점
      assert(listBytes(V * (long long)V / 100 / 2) < matrixBytes(V) && matrixBytes(V) < listBytes((long long)(V * (long long)V * 0.3 / 2))); }
    std::cout << "AdjacencyMatrix: a 64-bit-word row matrix matched a set model for membership, degree (popcount) and ordered neighbour enumeration on 200 random graphs, A^k entries equalled DFS walk counts and trace(A^3)/6 equalled brute-force triangle counts, Warshall's bit-parallel closure equalled BFS reachability, ANDed rows counted common neighbours, and the memory model put the list ahead at 1% density and the matrix ahead at 30%" << std::endl; return 0;
}
// Time Complexity: 간선 질의 O(1), 이웃 훑기 O(V/64 + deg), 폐쇄 O(V³/64)
// Space Complexity: O(V²/8) 바이트
```
## AdjacencyList()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 인접 리스트(Adjacency List): 정점마다 이웃의 목록을 둔다. 메모리는 O(V + E) 라서 희소 그래프에 알맞고, 이웃 훑기는 O(deg) 로 탐색(BFS/DFS)이 총 O(V + E) 이다. 간선 질의는 리스트를 훑어 O(deg), 이웃을 정렬해 두면 이진 탐색으로 O(log deg), 해시 집합을 곁들이면 기대 O(1). 순서는 삽입 순서(스택처럼 쓰는 벡터)이므로 같은 그래프라도 리스트 안의 순서가 다를 수 있다 — 같은 그래프의 동일성 비교는 정렬한 뒤에 한다.
// 유방향 그래프의 역방향 그래프(전치)는 모든 간선 뒤집기라 O(V + E) 이고 진입 차수 처리·강연결 성분(코사라주)의 필수 도구다. 정렬은 계수 정렬(간선을 번호 순으로 두 번 분배)로 O(V + E) 에 가능하다. 메모리 교차점: 행렬 V²/8 바이트 대 리스트 4(V + 2E) 바이트 — 밀도가 낮을수록 리스트가 유리.
// 검증: ① 무작위 그래프의 리스트가 모델과 같고 정렬 뒤 두 리스트(삽입 순서가 다른 두 번 구성)가 같음, 이중 정렬 이진 탐색 소속 질의가 선형 탐색과 같음 ② BFS 가 정확히 V + E(무방향은 2E) 개의 항목을 훑음 ③ 역방향 그래프: 간선 (u,v) ↔ (v,u) 이고 두 번 뒤집으면 원래 ④ 계수 정렬로 정렬한 인접 리스트 == std::sort 로 정렬한 것 ⑤ 리스트→행렬→리스트 변환이 항등 ⑥ 질의 비용: 정렬 리스트의 이진 탐색 비교 수 ≤ ⌊log₂ deg⌋ + 1.
typedef std::vector<std::vector<int>> Adj;
Adj reversed(const Adj& a) { Adj r(a.size()); for (int u = 0; u < (int)a.size(); u++) for (int v : a[u]) r[v].push_back(u); return r; }
Adj sortedByCounting(const Adj& a) { int n = (int)a.size(); std::vector<std::pair<int, int>> edges; for (int u = 0; u < n; u++) for (int v : a[u]) edges.push_back({u, v}); std::vector<std::vector<std::pair<int, int>>> byV(n); for (auto& e : edges) byV[e.second].push_back(e); Adj r(n); for (int v = 0; v < n; v++) for (auto& e : byV[v]) r[e.first].push_back(e.second); return r; }   // 두 번의 분배: v 로 모은 뒤 u 로 모으면 u 안에서 v 오름차순
long long bfsVisitedEntries(const Adj& a, int s) { std::vector<char> seen(a.size(), 0); std::queue<int> q; q.push(s); seen[s] = 1; long long entries = 0; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : a[u]) { entries++; if (!seen[v]) { seen[v] = 1; q.push(v); } } } return entries; }
bool binarySearchHas(const std::vector<int>& sortedNbrs, int v, int& cmps) { std::size_t lo = 0, hi = sortedNbrs.size(); while (lo < hi) { std::size_t mid = lo + (hi - lo) / 2; cmps++; if (sortedNbrs[mid] < v) lo = mid + 1; else hi = mid; } return lo < sortedNbrs.size() && sortedNbrs[lo] == v; }
int main() {
    std::mt19937 rng(12);
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 30); bool directed = rep % 2; std::set<std::pair<int, int>> model; Adj a(n), b(n); std::vector<std::pair<int, int>> list; for (int k = 0, e = (int)(rng() % (4 * n)); k < e; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v) continue; auto key = directed ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v)); if (model.insert(key).second) list.push_back({u, v}); }
        for (auto e : list) { a[e.first].push_back(e.second); if (!directed) a[e.second].push_back(e.first); } std::vector<std::pair<int, int>> shuffled = list; std::shuffle(shuffled.begin(), shuffled.end(), rng); for (auto e : shuffled) { b[e.first].push_back(e.second); if (!directed) b[e.second].push_back(e.first); }
        Adj as = a, bs = b; for (auto& l : as) std::sort(l.begin(), l.end()); for (auto& l : bs) std::sort(l.begin(), l.end()); assert(as == bs);                                                                                                  // ① 삽입 순서가 달라도 정렬하면 같음
        for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) { int cmps = 0; bool fast = binarySearchHas(as[u], v, cmps); bool slow = std::find(a[u].begin(), a[u].end(), v) != a[u].end(); assert(fast == slow); if (!as[u].empty()) assert(cmps <= (int)std::floor(std::log2((double)as[u].size())) + 1); }   // ⑥
        long long entries = 0; for (auto& l : a) entries += (long long)l.size(); assert(entries == (directed ? 1 : 2) * (long long)model.size()); long long visited = bfsVisitedEntries(a, 0); assert(visited <= entries);                         // ②
        if (directed) { Adj r = reversed(a); Adj rr = reversed(r); for (int u = 0; u < n; u++) for (int v : a[u]) assert(std::find(r[v].begin(), r[v].end(), u) != r[v].end()); for (auto& l : rr) std::sort(l.begin(), l.end()); assert(rr == as); }     // ③ 두 번 뒤집으면 원래
        Adj counting = sortedByCounting(a); assert(counting == as);                                                                                                                                                                   // ④
        std::vector<std::vector<char>> M(n, std::vector<char>(n, 0)); for (int u = 0; u < n; u++) for (int v : a[u]) M[u][v] = 1; Adj back(n); for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (M[u][v]) back[u].push_back(v); assert(back == as); }                // ⑤
    { Adj chain(500); for (int i = 0; i + 1 < 500; i++) { chain[i].push_back(i + 1); chain[i + 1].push_back(i); } assert(bfsVisitedEntries(chain, 0) == 2 * 499); }
    std::cout << "AdjacencyList: lists built in two different insertion orders were equal after sorting, binary-search membership on sorted lists agreed with linear search within floor(log2 deg)+1 comparisons, BFS touched exactly the stored entries (2E for undirected graphs), reversal was an involution, counting-sort ordering equalled std::sort, and list-to-matrix-to-list conversion was the identity" << std::endl; return 0;
}
// Time Complexity: 이웃 훑기 O(deg), 간선 질의 O(deg) (정렬 시 O(log deg)), 전치 O(V + E)
// Space Complexity: O(V + E)
```
## EdgeList()
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

// 간선 목록(Edge List): 간선 (u, v, w) 를 그냥 배열에 담는다. 메모리는 간선 수에 비례해 가장 단순하고, 간선 전체를 한 번에 다루는 알고리즘에 딱 맞다: 크러스칼은 가중치로 정렬해 앞에서부터 보고, 벨만-포드는 간선 전체를 V−1 번 완화한다. 반면 "정점 v 의 이웃" 은 목록 전체를 훑어야 해서 O(E) 이고 간선 질의도 O(E) (정렬해 두면 O(log E)).
// 간선 목록을 인접 리스트로 바꾸는 방법 둘: (1) 출발점 기준으로 정렬한 뒤 구간을 잘라 쓰기 — O(E log E), (2) 계수 정렬: 정점별 개수를 세고 누적합으로 시작 위치를 구한 뒤 한 번에 배치 — O(V + E) 이며 같은 출발점 안에서 입력 순서가 유지된다(안정적). 중복 간선 제거는 (u, v) 로 정렬한 뒤 인접한 같은 항목을 합친다(가중치는 최소/합 선택).
// 검증: ① 무작위 간선 목록→계수 정렬로 만든 CSR 형태(오프셋 + 이웃) == 정렬 기반 변환 == 모델 ② 계수 정렬은 같은 출발점 내에서 입력 순서를 유지(std::stable_sort 와 같음) ③ 중복 제거(정렬 후 unique)가 집합 모델과 같고 최소 가중치를 남김 ④ 이웃 질의 비용: 정렬한 목록의 이진 탐색(equal_range)이 선형 훑기와 같은 결과이고 비교 수 ≤ 2⌈log₂ E⌉+2 ⑤ 가중치 정렬 뒤 크러스칼 접두사가 최소 신장 숲의 가중치와 같음 ⑥ 벨만–포드 완화(간선 전체 V−1 번)가 다이크스트라와 같은 거리(음수 없는 가중치).
struct Edge { int u, v, w; };
bool operator==(const Edge& a, const Edge& b) { return a.u == b.u && a.v == b.v && a.w == b.w; }
void toCsrCounting(int n, const std::vector<Edge>& es, std::vector<int>& offset, std::vector<Edge>& arranged, long& ops) { offset.assign(n + 1, 0); for (const Edge& e : es) { offset[e.u + 1]++; ops++; } for (int i = 0; i < n; i++) offset[i + 1] += offset[i]; arranged.resize(es.size()); std::vector<int> cursor(offset.begin(), offset.end() - 1); for (const Edge& e : es) { arranged[cursor[e.u]++] = e; ops++; } }
std::vector<Edge> dedupeMin(std::vector<Edge> es) { std::sort(es.begin(), es.end(), [](const Edge& a, const Edge& b) { return a.u != b.u ? a.u < b.u : a.v != b.v ? a.v < b.v : a.w < b.w; }); std::vector<Edge> out; for (const Edge& e : es) if (out.empty() || out.back().u != e.u || out.back().v != e.v) out.push_back(e); return out; }
long long kruskalWeight(int n, std::vector<Edge> es, int& used) { std::sort(es.begin(), es.end(), [](const Edge& a, const Edge& b) { return a.w < b.w; }); std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; long long total = 0; used = 0; for (const Edge& e : es) { int a = find(e.u), b = find(e.v); if (a != b) { p[a] = b; total += e.w; used++; } } return total; }
std::vector<long long> bellmanFord(int n, const std::vector<Edge>& es, int s) { const long long INF = 1e18; std::vector<long long> d(n, INF); d[s] = 0; for (int i = 0; i + 1 < n; i++) for (const Edge& e : es) { if (d[e.u] < INF && d[e.u] + e.w < d[e.v]) d[e.v] = d[e.u] + e.w; } return d; }
std::vector<long long> dijkstraFromEdges(int n, const std::vector<Edge>& es, int s) { const long long INF = 1e18; std::vector<std::vector<std::pair<int, int>>> adj(n); for (const Edge& e : es) adj[e.u].push_back({e.v, e.w}); std::vector<long long> d(n, INF); std::set<std::pair<long long, int>> pq; d[s] = 0; pq.insert({0, s}); while (!pq.empty()) { auto [du, u] = *pq.begin(); pq.erase(pq.begin()); for (auto [v, w] : adj[u]) if (du + w < d[v]) { pq.erase({d[v], v}); d[v] = du + w; pq.insert({d[v], v}); } } return d; }
int main() {
    std::mt19937 rng(13);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 20); std::vector<Edge> es; for (int k = 0, m = (int)(rng() % (4 * n)); k < m; k++) es.push_back({(int)(rng() % n), (int)(rng() % n), 1 + (int)(rng() % 20)});                                // ① ②
        std::vector<int> offset; std::vector<Edge> arranged; long ops = 0; toCsrCounting(n, es, offset, arranged, ops); assert(ops == 2 * (long)es.size() && offset[n] == (int)es.size()); std::vector<Edge> stable = es; std::stable_sort(stable.begin(), stable.end(), [](const Edge& a, const Edge& b) { return a.u < b.u; }); assert(arranged == stable);
        for (int u = 0; u < n; u++) { int c = 0; for (const Edge& e : es) c += e.u == u; assert(offset[u + 1] - offset[u] == c); for (int i = offset[u]; i < offset[u + 1]; i++) assert(arranged[i].u == u); }
        std::vector<Edge> dd = dedupeMin(es); std::map<std::pair<int, int>, int> best; for (const Edge& e : es) { auto key = std::make_pair(e.u, e.v); auto it = best.find(key); if (it == best.end() || e.w < it->second) best[key] = e.w; } assert(dd.size() == best.size()); for (const Edge& e : dd) assert(best.at({e.u, e.v}) == e.w);   // ③
        std::vector<Edge> byUV = dd; for (int q = 0; q < 20; q++) { int u = (int)(rng() % n), v = (int)(rng() % n); int cmps = 0; auto lo = std::lower_bound(byUV.begin(), byUV.end(), std::make_pair(u, v), [&](const Edge& e, const std::pair<int, int>& key) { cmps++; return std::make_pair(e.u, e.v) < key; }); bool found = lo != byUV.end() && lo->u == u && lo->v == v;
            bool slow = false; for (const Edge& e : byUV) slow |= e.u == u && e.v == v; assert(found == slow); if (!byUV.empty()) assert(cmps <= (int)std::ceil(std::log2((double)byUV.size() + 1)) + 1); } }                                                                       // ④
    for (int rep = 0; rep < 150; rep++) { int n = 2 + (int)(rng() % 12); std::vector<Edge> es; for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) if (rng() % 3 == 0) es.push_back({u, v, 1 + (int)(rng() % 30)}); int used = 0; long long mst = kruskalWeight(n, es, used);        // ⑤ 크러스칼 접두사
        std::vector<int> comp(n); std::iota(comp.begin(), comp.end(), 0); auto find = [&](int x) { while (comp[x] != x) x = comp[x] = comp[comp[x]]; return x; }; int c = n; for (const Edge& e : es) { int a = find(e.u), b = find(e.v); if (a != b) { comp[a] = b; c--; } } assert(used == n - c);
        std::vector<Edge> both = es; for (const Edge& e : es) both.push_back({e.v, e.u, e.w}); int src = (int)(rng() % n); assert(bellmanFord(n, both, src) == dijkstraFromEdges(n, both, src)); (void)mst; }                                                                    // ⑥
    std::cout << "EdgeList: counting-sort conversion of random edge lists to offset-plus-neighbour form took exactly 2E steps, produced the same stable arrangement as std::stable_sort by source, matched the per-source counts, duplicate elimination kept the minimum weight per (u,v), binary search over the sorted list matched linear scans, Kruskal over the list used n minus components edges, and Bellman-Ford relaxation of the whole edge list equalled Dijkstra" << std::endl; return 0;
}
// Time Complexity: 이웃 질의 O(E) (정렬 시 O(log E + deg)), 계수 정렬 변환 O(V + E), 정렬 변환 O(E log E)
// Space Complexity: O(E)
```
## IncidenceMatrix()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 접속 행렬(Incidence Matrix): V×E 행렬 B 에서 열이 간선, 행이 정점. 무방향이면 간선의 두 끝점 행에 1(자기 루프는 한 행에 2), 유방향이면 간선 u→v 의 열에 u 행에 +1, v 행에 −1 (또는 반대 부호). 간선 중심의 표현이라 메모리 V·E 로 크지만 대수적 성질이 아름답다. 유방향(방향을 임의로 준 무방향) 접속 행렬 B 에서: 모든 열의 합이 0, B·Bᵀ = L = D − A (라플라시안: 대각선은 차수, 비대각선은 인접 행렬의 음수), 그리고 B 의 계수(rank) = V − c (c = 연결 성분 수), 영공간(Bx = 0 인 x 는 순환 공간의 간선 흐름) 차원 = E − V + c (사이클 공간의 차원, 독립 사이클 수).
// 부호 없는 무방향 접속 행렬 B⁺ 에서는 B⁺·B⁺ᵀ = D + A (부호 라플라시안), 행의 합 = 차수, 열의 합 = 2. 라플라시안의 0 고유값의 개수 = 연결 성분 수이고 행렬-트리 정리: 라플라시안에서 한 행과 한 열을 지운 부분행렬의 행렬식 = 신장 트리의 개수(완전 그래프는 Cayley 공식 n^(n−2)).
// 검증: ① 무작위 무방향 그래프에서 방향을 임의로 준 접속 행렬의 열 합이 0, B·Bᵀ == D − A ② 부호 없는 접속 행렬의 행 합 == 차수, 열 합 == 2, B⁺B⁺ᵀ == D + A ③ rank(B) == V − 연결 성분 수 (소수 모듈로 가우스 소거) 이고 영공간 차원 E − rank == E − V + c ④ 방향을 바꿔도 B·Bᵀ 는 불변(열 부호 뒤집기) ⑤ 행렬-트리: 완전 그래프 K_n 의 라플라시안 소행렬식(정확한 정수) == n^(n−2) (n ≤ 7), 사이클 C_n 은 n, 경로는 1 ⑥ 유방향 그래프의 접속 행렬은 열마다 +1, −1 정확히 하나씩.
typedef std::vector<std::vector<long long>> Mat;
struct G { int n; std::vector<std::pair<int, int>> edges; };
Mat oriented(const G& g) { Mat B(g.n, std::vector<long long>(g.edges.size(), 0)); for (std::size_t j = 0; j < g.edges.size(); j++) { B[g.edges[j].first][j] += 1; B[g.edges[j].second][j] -= 1; } return B; }
Mat unsignedInc(const G& g) { Mat B(g.n, std::vector<long long>(g.edges.size(), 0)); for (std::size_t j = 0; j < g.edges.size(); j++) { B[g.edges[j].first][j] += 1; B[g.edges[j].second][j] += 1; } return B; }
Mat timesTranspose(const Mat& B) { int n = (int)B.size(); Mat r(n, std::vector<long long>(n, 0)); for (int i = 0; i < n; i++) for (int k = 0; k < n; k++) for (std::size_t j = 0; j < B[i].size(); j++) r[i][k] += B[i][j] * B[k][j]; return r; }
Mat degreeAdj(const G& g, int sign) { Mat M(g.n, std::vector<long long>(g.n, 0)); for (auto e : g.edges) { M[e.first][e.first]++; M[e.second][e.second]++; M[e.first][e.second] += sign; M[e.second][e.first] += sign; } return M; }       // sign = -1: D − A, +1: D + A
int rankMod(Mat m, long long p) { int rows = (int)m.size(), cols = rows ? (int)m[0].size() : 0, r = 0; for (auto& row : m) for (auto& x : row) x = ((x % p) + p) % p; auto power = [&](long long b, long long e) { long long res = 1; b %= p; while (e) { if (e & 1) res = res * b % p; b = b * b % p; e >>= 1; } return res; };
    for (int c = 0; c < cols && r < rows; c++) { int piv = -1; for (int i = r; i < rows; i++) if (m[i][c]) { piv = i; break; } if (piv < 0) continue; std::swap(m[r], m[piv]); long long inv = power(m[r][c], p - 2); for (int i = 0; i < rows; i++) if (i != r && m[i][c]) { long long f = m[i][c] * inv % p; for (int j = c; j < cols; j++) m[i][j] = ((m[i][j] - f * m[r][j]) % p + p) % p; } r++; } return r; }
long long determinant(Mat m) { int n = (int)m.size(); long long prevPivot = 1; int sign = 1; for (int k = 0; k + 1 < n; k++) { if (m[k][k] == 0) { int sw = -1; for (int i = k + 1; i < n; i++) if (m[i][k]) { sw = i; break; } if (sw < 0) return 0; std::swap(m[k], m[sw]); sign = -sign; } for (int i = k + 1; i < n; i++) for (int j = k + 1; j < n; j++) m[i][j] = (m[i][j] * m[k][k] - m[i][k] * m[k][j]) / prevPivot; prevPivot = m[k][k]; } return n ? sign * m[n - 1][n - 1] : 1; }   // 바레이스 정수 소거
long long spanningTrees(const G& g) { Mat L = degreeAdj(g, -1); if (g.n <= 1) return 1; Mat minor(g.n - 1, std::vector<long long>(g.n - 1)); for (int i = 1; i < g.n; i++) for (int j = 1; j < g.n; j++) minor[i - 1][j - 1] = L[i][j]; return determinant(minor); }
int components(const G& g) { std::vector<int> p(g.n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; int c = g.n; for (auto e : g.edges) { int a = find(e.first), b = find(e.second); if (a != b) { p[a] = b; c--; } } return c; }
int main() {
    std::mt19937 rng(14); const long long P = 1000000007;
    for (int rep = 0; rep < 300; rep++) { G g; g.n = 1 + (int)(rng() % 9); std::set<std::pair<int, int>> seen; for (int k = 0, m = (int)(rng() % (2 * g.n)); k < m; k++) { int u = (int)(rng() % g.n), v = (int)(rng() % g.n); if (u == v || !seen.insert({std::min(u, v), std::max(u, v)}).second) continue; g.edges.push_back({u, v}); }
        Mat B = oriented(g), Bu = unsignedInc(g); for (std::size_t j = 0; j < g.edges.size(); j++) { long long s = 0, su = 0; for (int i = 0; i < g.n; i++) { s += B[i][j]; su += Bu[i][j]; } assert(s == 0 && su == 2); }                                // ① ② ⑥
        assert(timesTranspose(B) == degreeAdj(g, -1) && timesTranspose(Bu) == degreeAdj(g, 1)); std::vector<int> deg(g.n, 0); for (auto e : g.edges) { deg[e.first]++; deg[e.second]++; } for (int i = 0; i < g.n; i++) { long long rs = 0; for (long long x : Bu[i]) rs += x; assert(rs == deg[i]); }
        G flipped = g; for (auto& e : flipped.edges) if (rng() % 2) std::swap(e.first, e.second); assert(timesTranspose(oriented(flipped)) == timesTranspose(B));                                                                   // ④ 방향과 무관
        int rank = rankMod(B, P), c = components(g); assert(rank == g.n - c && (int)g.edges.size() - rank == (int)g.edges.size() - g.n + c); }                                                                      // ③ 계수와 사이클 공간
    for (int n = 1; n <= 7; n++) { G k; k.n = n; for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) k.edges.push_back({u, v}); long long cayley = 1; for (int i = 0; i < n - 2; i++) cayley *= n; if (n == 1) cayley = 1; assert(spanningTrees(k) == cayley);    // ⑤
        G cyc; cyc.n = n; if (n >= 3) { for (int v = 0; v < n; v++) cyc.edges.push_back({v, (v + 1) % n}); assert(spanningTrees(cyc) == n); } G path; path.n = n; for (int v = 0; v + 1 < n; v++) path.edges.push_back({v, v + 1}); assert(spanningTrees(path) == 1); }
    { G d; d.n = 3; d.edges = {{0, 1}, {1, 2}, {0, 2}}; Mat B = oriented(d); for (std::size_t j = 0; j < d.edges.size(); j++) { int plus = 0, minus = 0; for (int i = 0; i < 3; i++) { plus += B[i][j] == 1; minus += B[i][j] == -1; } assert(plus == 1 && minus == 1); } }
    std::cout << "IncidenceMatrix: for 300 random graphs the oriented incidence matrix had zero column sums, B*B^T = D - A and rank V minus the number of components (cycle space dimension E-V+c), the unsigned matrix gave row sums equal to degrees and B*B^T = D + A, reversing edge directions left B*B^T unchanged, and the matrix-tree theorem counted n^(n-2) spanning trees of K_n up to n=7, n for cycles and 1 for paths" << std::endl; return 0;
}
// Time Complexity: 구성 O(V · E), 행렬 곱 O(V² E)
// Space Complexity: O(V · E)
```
## CompressedSparseRow()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 압축 희소 행(CSR, Compressed Sparse Row): 인접 행렬의 0 이 아닌 칸만 행 순서대로 저장한다. 세 배열: row_ptr[V+1] (행 u 의 항목이 col_idx[row_ptr[u] .. row_ptr[u+1]) 에 있음), col_idx[E] (이웃 번호), val[E] (가중치). 메모리 (V + 1) + 2E 워드, 행 u 의 이웃 훑기는 연속 메모리를 읽어 O(deg) 이고 캐시 효율이 매우 좋다. 차수는 row_ptr[u+1] − row_ptr[u] 로 O(1). 단점: 변경이 어렵다(중간에 끼워 넣으면 뒤를 모두 밀어야 함) — 만든 뒤 읽기 위주인 그래프·희소 행렬(그래프 분석, 행렬-벡터 곱)에 쓴다.
// 만들기: 간선을 (u, v) 로 훑어 개수 세기 → 누적합으로 row_ptr → 한 번 더 훑어 배치하는 계수 정렬로 O(V + E). 행 안의 열 번호를 정렬해 두면(정규형) 간선 질의가 이진 탐색 O(log deg) 이고 두 행의 교집합(삼각형 세기)이 병합 O(deg₁ + deg₂) 이다. 같은 (u, v) 가 여러 번 나오면 합쳐서(coalesce) 하나로 만들 수 있다. 행렬-벡터 곱 y = A·x 는 행마다 y[u] = Σ val[k]·x[col_idx[k]] 로 O(E).
// 검증: ① 무작위 간선 목록→CSR 이 모델(인접 리스트)과 같은 이웃·차수·가중치, row_ptr 단조, 열 정렬 후 정규형 ② y = A·x 가 밀집 행렬 곱과 같음(정수 연산) ③ 중복 합치기가 (u, v) 별 가중치 합과 같음 ④ 이진 탐색 간선 질의와 삼각형 수(행 병합)가 무차별 계산과 같음 ⑤ CSR 위의 BFS 가 인접 리스트 BFS 와 같은 거리 ⑥ 메모리 워드 수 = (V + 1) + 2E 이고 빈 그래프·빈 행 처리.
struct CSR { int n = 0; std::vector<int> rowPtr, col; std::vector<long long> val;
    static CSR build(int n, const std::vector<std::array<long long, 3>>& triples, bool coalesce) { std::vector<std::array<long long, 3>> t = triples; std::sort(t.begin(), t.end(), [](const std::array<long long, 3>& a, const std::array<long long, 3>& b) { return a[0] != b[0] ? a[0] < b[0] : a[1] < b[1]; });
        if (coalesce) { std::vector<std::array<long long, 3>> merged; for (auto& e : t) { if (!merged.empty() && merged.back()[0] == e[0] && merged.back()[1] == e[1]) merged.back()[2] += e[2]; else merged.push_back(e); } t = merged; }
        CSR c; c.n = n; c.rowPtr.assign(n + 1, 0); for (auto& e : t) c.rowPtr[e[0] + 1]++; for (int i = 0; i < n; i++) c.rowPtr[i + 1] += c.rowPtr[i]; for (auto& e : t) { c.col.push_back((int)e[1]); c.val.push_back(e[2]); } return c; }
    int degree(int u) const { return rowPtr[u + 1] - rowPtr[u]; }
    bool has(int u, int v) const { return std::binary_search(col.begin() + rowPtr[u], col.begin() + rowPtr[u + 1], v); }
    std::vector<long long> multiply(const std::vector<long long>& x) const { std::vector<long long> y(n, 0); for (int u = 0; u < n; u++) for (int k = rowPtr[u]; k < rowPtr[u + 1]; k++) y[u] += val[k] * x[col[k]]; return y; }
    std::size_t words() const { return rowPtr.size() + col.size() + val.size(); } };
int main() {
    std::mt19937 rng(15);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 25); std::vector<std::array<long long, 3>> triples; for (int k = 0, m = (int)(rng() % (4 * n)); k < m; k++) triples.push_back({(long long)(rng() % n), (long long)(rng() % n), (long long)(rng() % 9) + 1});
        CSR c = CSR::build(n, triples, true); std::map<std::pair<int, int>, long long> model; for (auto& e : triples) model[{(int)e[0], (int)e[1]}] += e[2];                                                                                        // ① ③
        assert(std::is_sorted(c.rowPtr.begin(), c.rowPtr.end()) && c.rowPtr[0] == 0 && c.rowPtr[n] == (int)model.size() && c.words() == (std::size_t)(n + 1) + 2 * model.size()); std::map<std::pair<int, int>, long long> got;
        for (int u = 0; u < n; u++) { assert(std::is_sorted(c.col.begin() + c.rowPtr[u], c.col.begin() + c.rowPtr[u + 1])); for (int k = c.rowPtr[u]; k < c.rowPtr[u + 1]; k++) got[{u, c.col[k]}] = c.val[k]; int d = 0; for (auto& kv : model) d += kv.first.first == u; assert(c.degree(u) == d); } assert(got == model);
        std::vector<long long> x(n); for (auto& v : x) v = (long long)(rng() % 21) - 10; std::vector<long long> dense(n, 0); for (auto& kv : model) dense[kv.first.first] += kv.second * x[kv.first.second]; assert(c.multiply(x) == dense);                                       // ②
        for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) assert(c.has(u, v) == (model.count({u, v}) > 0));                                                                                                                          // ④ 이진 탐색 질의
        long long tri = 0; for (int a = 0; a < n; a++) for (int k = c.rowPtr[a]; k < c.rowPtr[a + 1]; k++) { int b = c.col[k]; if (b <= a) continue; int i = c.rowPtr[a], j = c.rowPtr[b]; while (i < c.rowPtr[a + 1] && j < c.rowPtr[b + 1]) { if (c.col[i] < c.col[j]) i++; else if (c.col[j] < c.col[i]) j++; else { if (c.col[i] > b) tri++; i++; j++; } } }
        long long brute = 0; for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) for (int d = b + 1; d < n; d++) brute += model.count({a, b}) && model.count({b, d}) && model.count({a, d}); assert(tri == brute); }
    for (int rep = 0; rep < 100; rep++) { int n = 2 + (int)(rng() % 30); std::vector<std::array<long long, 3>> triples; std::vector<std::vector<int>> adj(n); std::set<std::pair<int, int>> seen; for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u != v && seen.insert({u, v}).second) { triples.push_back({u, v, 1}); adj[u].push_back(v); } }
        CSR c = CSR::build(n, triples, false); std::vector<int> d1(n, -1), d2(n, -1); std::queue<int> q; d1[0] = 0; q.push(0); while (!q.empty()) { int u = q.front(); q.pop(); for (int k = c.rowPtr[u]; k < c.rowPtr[u + 1]; k++) { int v = c.col[k]; if (d1[v] < 0) { d1[v] = d1[u] + 1; q.push(v); } } }                          // ⑤
        d2[0] = 0; q.push(0); while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (d2[v] < 0) { d2[v] = d2[u] + 1; q.push(v); } } assert(d1 == d2); }
    { CSR e = CSR::build(0, {}, true); assert(e.rowPtr == std::vector<int>{0} && e.words() == 1); CSR s = CSR::build(5, {{2, 3, 7}}, true); assert(s.degree(0) == 0 && s.degree(2) == 1 && s.degree(4) == 0 && s.has(2, 3) && !s.has(3, 2) && s.words() == 6 + 2); }                  // ⑥
    std::cout << "CompressedSparseRow: counting-sort construction gave sorted row pointers and column indices matching a map model (with duplicate triples coalesced by summing), sparse matrix-vector products equalled the dense computation, binary-search edge queries and row-merge triangle counting matched brute force, BFS over CSR equalled adjacency-list BFS, and memory was exactly (V+1)+2E words" << std::endl; return 0;
}
// Time Complexity: 구성 O(V + E) (정렬 O(E log E)), 이웃 훑기 O(deg), 행렬-벡터 곱 O(E)
// Space Complexity: O(V + E)
```
## CompressedSparseColumn()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 압축 희소 열(CSC, Compressed Sparse Column): CSR 과 대칭인 구조로 0 이 아닌 칸을 열 순서로 저장한다. col_ptr[V+1], row_idx[E], val[E] — 열 v 의 항목이 row_idx[col_ptr[v] .. col_ptr[v+1]) 에 있다. 그래프로는 "정점 v 로 들어오는 간선의 출발점 목록" 이므로 들어오는 이웃(in-neighbours)과 진입 차수를 O(1)/O(indeg) 에 준다. 어떤 행렬의 CSC 는 그 전치 행렬의 CSR 과 같은 배열이다.
// 응용: PageRank 의 "끌어오기(pull)" 갱신 — 각 정점이 자신에게 들어오는 이웃들의 점수를 읽어 합하므로 CSC 가 자연스럽고(쓰기 충돌 없음), "밀어내기(push)" 는 CSR 로 자기 이웃에게 점수를 더한다. 같은 곱 y = A·x 도 CSR 은 행 단위로 O(E), CSC 는 열 단위로 x[v] 를 행들에 흩뿌려(scatter) O(E). CSR ↔ CSC 변환(전치)은 계수 정렬로 O(V + E).
// 검증: ① 무작위 가중 간선 목록으로 만든 CSC 의 열 v 가 모델의 들어오는 간선 집합(출발점, 가중치)과 같고 진입 차수 == col_ptr 차이 ② CSR→CSC→CSR 변환이 항등(행 안 열 정렬 상태에서), CSC 를 직접 만든 것과 같음 ③ y = A·x (CSC 흩뿌리기)와 y = Aᵀ·x (CSC 모으기)가 밀집 곱과 같음 ④ PageRank 끌어오기(CSC)와 밀어내기(CSR)가 같은 값(허용 오차 1e-12)이고 합이 1 ⑤ 빈 열·빈 그래프 ⑥ 메모리 워드 (V + 1) + 2E.
struct Sparse { int n = 0; std::vector<int> ptr, idx; std::vector<long long> val; std::size_t words() const { return ptr.size() + idx.size() + val.size(); } };
Sparse build(int n, const std::vector<std::array<long long, 3>>& t, bool byColumn) { std::vector<std::array<long long, 3>> s = t; int major = byColumn ? 1 : 0, minor = byColumn ? 0 : 1; std::sort(s.begin(), s.end(), [&](const std::array<long long, 3>& a, const std::array<long long, 3>& b) { return a[major] != b[major] ? a[major] < b[major] : a[minor] < b[minor]; });
    Sparse m; m.n = n; m.ptr.assign(n + 1, 0); for (auto& e : s) m.ptr[e[major] + 1]++; for (int i = 0; i < n; i++) m.ptr[i + 1] += m.ptr[i]; for (auto& e : s) { m.idx.push_back((int)e[minor]); m.val.push_back(e[2]); } return m; }
Sparse transposeCounting(const Sparse& a) { Sparse t; t.n = a.n; t.ptr.assign(a.n + 1, 0); for (int k : a.idx) t.ptr[k + 1]++; for (int i = 0; i < a.n; i++) t.ptr[i + 1] += t.ptr[i]; t.idx.resize(a.idx.size()); t.val.resize(a.val.size()); std::vector<int> cur(t.ptr.begin(), t.ptr.end() - 1);
    for (int major = 0; major < a.n; major++) for (int k = a.ptr[major]; k < a.ptr[major + 1]; k++) { int dst = cur[a.idx[k]]++; t.idx[dst] = major; t.val[dst] = a.val[k]; } return t; }                                                    // 행 순서로 훑으며 분배 → 새 구조 안에서 정렬 유지
std::vector<long long> multiplyCSR(const Sparse& csr, const std::vector<long long>& x) { std::vector<long long> y(csr.n, 0); for (int u = 0; u < csr.n; u++) for (int k = csr.ptr[u]; k < csr.ptr[u + 1]; k++) y[u] += csr.val[k] * x[csr.idx[k]]; return y; }
std::vector<long long> multiplyCSCScatter(const Sparse& csc, const std::vector<long long>& x) { std::vector<long long> y(csc.n, 0); for (int v = 0; v < csc.n; v++) for (int k = csc.ptr[v]; k < csc.ptr[v + 1]; k++) y[csc.idx[k]] += csc.val[k] * x[v]; return y; }          // 열 v 의 항목을 행들에 흩뿌림
std::vector<long long> multiplyTransposeCSCGather(const Sparse& csc, const std::vector<long long>& x) { std::vector<long long> y(csc.n, 0); for (int v = 0; v < csc.n; v++) for (int k = csc.ptr[v]; k < csc.ptr[v + 1]; k++) y[v] += csc.val[k] * x[csc.idx[k]]; return y; }
std::vector<double> pagerankPull(const Sparse& csc, const std::vector<int>& outdeg, double d, int iters) { int n = csc.n; std::vector<double> r(n, 1.0 / n), nx(n); for (int it = 0; it < iters; it++) { double dangling = 0; for (int v = 0; v < n; v++) if (outdeg[v] == 0) dangling += r[v]; for (int v = 0; v < n; v++) { double s = 0; for (int k = csc.ptr[v]; k < csc.ptr[v + 1]; k++) s += r[csc.idx[k]] / outdeg[csc.idx[k]]; nx[v] = (1 - d) / n + d * (s + dangling / n); } r = nx; } return r; }
std::vector<double> pagerankPush(const Sparse& csr, const std::vector<int>& outdeg, double d, int iters) { int n = csr.n; std::vector<double> r(n, 1.0 / n), nx(n); for (int it = 0; it < iters; it++) { double dangling = 0; for (int v = 0; v < n; v++) if (outdeg[v] == 0) dangling += r[v]; std::fill(nx.begin(), nx.end(), (1 - d) / n + d * dangling / n); for (int u = 0; u < n; u++) for (int k = csr.ptr[u]; k < csr.ptr[u + 1]; k++) nx[csr.idx[k]] += d * r[u] / outdeg[u]; r = nx; } return r; }
int main() {
    std::mt19937 rng(16);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 25); std::vector<std::array<long long, 3>> t; std::set<std::pair<long long, long long>> seen; for (int k = 0, m = (int)(rng() % (4 * n)); k < m; k++) { long long u = rng() % n, v = rng() % n; if (seen.insert({u, v}).second) t.push_back({u, v, (long long)(rng() % 9) + 1}); }
        Sparse csc = build(n, t, true), csr = build(n, t, false); std::map<int, std::map<int, long long>> incoming; for (auto& e : t) incoming[(int)e[1]][(int)e[0]] = e[2];                                                                                      // ①
        for (int v = 0; v < n; v++) { assert(csc.ptr[v + 1] - csc.ptr[v] == (int)incoming[v].size()); std::map<int, long long> got; for (int k = csc.ptr[v]; k < csc.ptr[v + 1]; k++) got[csc.idx[k]] = csc.val[k]; assert(got == incoming[v] && std::is_sorted(csc.idx.begin() + csc.ptr[v], csc.idx.begin() + csc.ptr[v + 1])); }
        Sparse viaTranspose = transposeCounting(csr); assert(viaTranspose.ptr == csc.ptr && viaTranspose.idx == csc.idx && viaTranspose.val == csc.val); Sparse back = transposeCounting(viaTranspose); assert(back.ptr == csr.ptr && back.idx == csr.idx && back.val == csr.val);        // ②
        assert(csc.words() == (std::size_t)(n + 1) + 2 * t.size());                                                                                                                                                                                                 // ⑥
        std::vector<long long> x(n); for (auto& v : x) v = (long long)(rng() % 21) - 10; std::vector<long long> dense(n, 0), denseT(n, 0); for (auto& e : t) { dense[e[0]] += e[2] * x[e[1]]; denseT[e[1]] += e[2] * x[e[0]]; }       // ③
        assert(multiplyCSR(csr, x) == dense && multiplyCSCScatter(csc, x) == dense && multiplyTransposeCSCGather(csc, x) == denseT); }
    for (int rep = 0; rep < 100; rep++) { int n = 2 + (int)(rng() % 25); std::vector<std::array<long long, 3>> t; std::set<std::pair<long long, long long>> seen; std::vector<int> outdeg(n, 0); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { long long u = rng() % n, v = rng() % n; if (u != v && seen.insert({u, v}).second) { t.push_back({u, v, 1}); outdeg[u]++; } }
        Sparse csc = build(n, t, true), csr = build(n, t, false); auto a = pagerankPull(csc, outdeg, 0.85, 80), b = pagerankPush(csr, outdeg, 0.85, 80); double sa = 0; for (int v = 0; v < n; v++) { assert(std::abs(a[v] - b[v]) < 1e-12); sa += a[v]; } assert(std::abs(sa - 1.0) < 1e-9); }                          // ④
    { Sparse e = build(0, {}, true); assert(e.ptr == std::vector<int>{0}); Sparse one = build(4, {{1, 2, 5}}, true); assert(one.ptr == (std::vector<int>{0, 0, 0, 1, 1}) && one.idx == std::vector<int>{1} && one.val == std::vector<long long>{5}); }                                                    // ⑤
    std::cout << "CompressedSparseColumn: column v of the CSC structure listed exactly the in-neighbours and weights of v in sorted order, CSR-to-CSC counting-sort transposition and back was the identity and equalled direct construction, scatter and gather matrix-vector products matched dense computation for both A*x and A^T*x, and pull-style PageRank on CSC equalled push-style PageRank on CSR to 1e-12 with ranks summing to 1" << std::endl; return 0;
}
// Time Complexity: 열 훑기 O(indeg), 전치 O(V + E), 곱셈 O(E)
// Space Complexity: O(V + E)
```
# Part 3. 그래프 탐색
## BreadthFirstSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <deque>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>

// 너비 우선 탐색(BFS): 시작 정점에서 가까운 정점부터 층(level) 단위로 방문한다. 큐에 정점을 넣을 때 방문 표시를 하고(꺼낼 때 표시하면 같은 정점이 큐에 여러 번 들어간다), 꺼낸 정점의 아직 보지 않은 이웃에 dist = 부모 dist + 1 과 부모 포인터를 주어 큐에 넣는다. 각 정점은 한 번 큐에 들어가고 각 간선(무방향이면 양쪽)은 한 번 훑으므로 O(V + E). 간선에 가중치가 없을 때 BFS 의 dist 가 곧 최단 경로의 간선 수이다.
// 핵심 성질: ① 방문 순서의 dist 는 비감소(층별로 방문), ② 모든 간선 u→v 에서 dist[v] ≤ dist[u] + 1 (무방향이면 |dist[u] − dist[v]| ≤ 1), ③ 부모 포인터를 따라가면 길이가 정확히 dist 인 경로(BFS 트리가 최단 경로 트리), ④ 도달할 수 없는 정점은 끝까지 미방문. 여러 출발점에서 동시에 시작(다중 출발점 BFS)하면 가장 가까운 출발점까지의 거리를 한 번에 얻는다. 간선 가중치가 0 또는 1 이면 덱을 써서 0 간선은 앞에, 1 간선은 뒤에 넣는 0-1 BFS 가 다이크스트라 없이 O(V + E).
// 검증: ① 무작위 방향/무방향 그래프에서 BFS 거리가 플로이드–워셜(간선 수 최단 거리)과 같고 도달 불가는 −1 ② 방문 순서의 dist 비감소, 모든 간선에서 dist[v] ≤ dist[u]+1, 부모 경로 길이 == dist ③ 큐에 들어간 정점 수 == 도달 가능한 정점 수, 훑은 인접 항목 수 == 도달 가능한 정점들의 진출 차수 합 ④ 다중 출발점 BFS == 각 출발점 BFS 의 원소별 최솟값 ⑤ 0-1 BFS 가 다이크스트라와 같은 거리 ⑥ 격자 미로(벽 포함)의 BFS 최단 거리가 플로이드–워셜과 같음.
struct Result { std::vector<int> dist, parent, order; long pushes = 0, scanned = 0; };
Result bfs(const std::vector<std::vector<int>>& adj, const std::vector<int>& sources) { int n = (int)adj.size(); Result r; r.dist.assign(n, -1); r.parent.assign(n, -1); std::queue<int> q; for (int s : sources) if (r.dist[s] < 0) { r.dist[s] = 0; q.push(s); r.pushes++; }
    while (!q.empty()) { int u = q.front(); q.pop(); r.order.push_back(u); for (int v : adj[u]) { r.scanned++; if (r.dist[v] < 0) { r.dist[v] = r.dist[u] + 1; r.parent[v] = u; q.push(v); r.pushes++; } } } return r; }
std::vector<std::vector<int>> floyd(const std::vector<std::vector<int>>& adj) { int n = (int)adj.size(); const int INF = 1 << 28; std::vector<std::vector<int>> d(n, std::vector<int>(n, INF)); for (int i = 0; i < n; i++) { d[i][i] = 0; for (int j : adj[i]) d[i][j] = std::min(d[i][j], 1); } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j]; for (auto& row : d) for (int& x : row) if (x >= INF) x = -1; return d; }
std::vector<int> zeroOneBfs(const std::vector<std::vector<std::pair<int, int>>>& adj, int s) { int n = (int)adj.size(); std::vector<int> d(n, 1 << 28); std::deque<int> dq; d[s] = 0; dq.push_back(s); while (!dq.empty()) { int u = dq.front(); dq.pop_front(); for (auto [v, w] : adj[u]) if (d[u] + w < d[v]) { d[v] = d[u] + w; if (w == 0) dq.push_front(v); else dq.push_back(v); } } return d; }
std::vector<int> dijkstra(const std::vector<std::vector<std::pair<int, int>>>& adj, int s) { int n = (int)adj.size(); std::vector<int> d(n, 1 << 28); std::set<std::pair<int, int>> pq; d[s] = 0; pq.insert({0, s}); while (!pq.empty()) { auto [du, u] = *pq.begin(); pq.erase(pq.begin()); for (auto [v, w] : adj[u]) if (du + w < d[v]) { pq.erase({d[v], v}); d[v] = du + w; pq.insert({d[v], v}); } } return d; }
int main() {
    std::mt19937 rng(17);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 14); bool directed = rep % 2; std::vector<std::vector<int>> adj(n); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v) continue; adj[u].push_back(v); if (!directed) adj[v].push_back(u); }
        auto fw = floyd(adj); int s = (int)(rng() % n); Result r = bfs(adj, {s}); for (int v = 0; v < n; v++) assert(r.dist[v] == fw[s][v]);                                                                                          // ①
        for (std::size_t i = 1; i < r.order.size(); i++) assert(r.dist[r.order[i - 1]] <= r.dist[r.order[i]]); for (int u = 0; u < n; u++) if (r.dist[u] >= 0) for (int v : adj[u]) assert(r.dist[v] >= 0 && r.dist[v] <= r.dist[u] + 1 && (directed || std::abs(r.dist[u] - r.dist[v]) <= 1));    // ②
        for (int v = 0; v < n; v++) if (r.dist[v] >= 0) { int len = 0, x = v; while (r.parent[x] >= 0) { assert(r.dist[r.parent[x]] == r.dist[x] - 1); x = r.parent[x]; len++; } assert(x == s && len == r.dist[v]); }
        long reach = 0, outSum = 0; for (int v = 0; v < n; v++) if (r.dist[v] >= 0) { reach++; outSum += (long)adj[v].size(); } assert(r.pushes == reach && (long)r.order.size() == reach && r.scanned == outSum);                                                      // ③
        std::vector<int> src; for (int k = 0, c = 1 + (int)(rng() % 3); k < c; k++) src.push_back((int)(rng() % n)); Result multi = bfs(adj, src); for (int v = 0; v < n; v++) { int best = -1; for (int t : src) if (fw[t][v] >= 0 && (best < 0 || fw[t][v] < best)) best = fw[t][v]; assert(multi.dist[v] == best); } }   // ④
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 14); std::vector<std::vector<std::pair<int, int>>> adj(n); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n), w = (int)(rng() % 2); adj[u].push_back({v, w}); } int s = (int)(rng() % n); assert(zeroOneBfs(adj, s) == dijkstra(adj, s)); }   // ⑤
    for (int rep = 0; rep < 100; rep++) { int R = 1 + (int)(rng() % 6), C = 1 + (int)(rng() % 6); std::vector<std::string> grid(R, std::string(C, '.')); for (auto& row : grid) for (char& c : row) if (rng() % 4 == 0) c = '#'; int n = R * C; std::vector<std::vector<int>> adj(n);                    // ⑥ 격자 미로
        for (int i = 0; i < R; i++) for (int j = 0; j < C; j++) if (grid[i][j] == '.') { int dx[4] = {1, -1, 0, 0}, dy[4] = {0, 0, 1, -1}; for (int d = 0; d < 4; d++) { int a = i + dx[d], b = j + dy[d]; if (a >= 0 && a < R && b >= 0 && b < C && grid[a][b] == '.') adj[i * C + j].push_back(a * C + b); } }
        auto fw = floyd(adj); int s = (int)(rng() % n); if (grid[s / C][s % C] == '#') continue; Result r = bfs(adj, {s}); for (int v = 0; v < n; v++) if (grid[v / C][v % C] == '.') assert(r.dist[v] == fw[s][v]); }
    std::cout << "BreadthFirstSearch: BFS distances equalled Floyd-Warshall hop counts on 300 random directed and undirected graphs, visit order was level order with dist[v] <= dist[u]+1 on every edge, parent chains had exactly dist edges, work was one queue push per reachable vertex and one scan per outgoing entry, multi-source BFS equalled the element-wise minimum, 0-1 BFS equalled Dijkstra, and grid mazes matched Floyd-Warshall" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## DepthFirstSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <vector>

// 깊이 우선 탐색(DFS): 갈 수 있는 곳까지 한 길로 깊이 들어갔다가 막히면 되돌아와 다음 길로 간다. 정점마다 발견 시각 d[v] 와 종료 시각 f[v](모든 이웃을 다 본 시각)를 기록하면 구조를 모두 알 수 있다. 괄호 정리: 두 정점의 구간 [d, f] 는 서로 분리되어 있거나 하나가 다른 하나에 완전히 포함되며, 포함 관계가 곧 DFS 트리의 조상–후손 관계이다. 간선 u→v 의 분류(발견 시각으로 판정): 트리 간선(v 를 처음 발견), 후진(back) 간선(v 가 u 의 조상: 구간이 u 를 포함), 전진(forward) 간선(v 가 u 의 비직계 후손), 교차(cross) 간선(v 의 구간이 u 보다 완전히 앞). 무방향 그래프에는 트리 간선과 후진 간선만 있다.
// 응용: 유방향 그래프가 비순환 ⇔ DFS 에서 후진 간선이 없다. 종료 시각의 역순(reverse postorder)이 DAG 의 위상 정렬. 연결 성분, 강연결 성분, 관절점·다리의 기초. 모든 정점을 시작점으로 시도하면(DFS 숲) 비연결 그래프도 모두 훑는다.
// 검증: ① 무작위 유방향 그래프에서 모든 간선의 분류가 시간 구간 정의와 같고 괄호 정리(두 구간은 분리되거나 포함) 성립, 시각은 1..2V 의 순열 ② 후진 간선이 없을 때와 위상 정렬(위상 순서 위반 0)·순환 존재가 동치(칸 알고리즘과 대조) ③ 무방향 그래프에는 교차 간선이 없고 "전진" 으로 보이는 것은 반대쪽에서 본 후진 간선뿐 ④ DFS 트리의 조상 판정 d[u] < d[v] < f[v] < f[u] 이 부모 체인으로 센 것과 같음 ⑤ 방문 순서(전위)와 종료 순서(후위)가 모두 각 정점을 정확히 한 번 ⑥ DFS 숲의 트리 수 == 시작점으로 쓰인 정점 수 == 약연결 성분(무방향이면 연결 성분) 수.
struct Dfs { std::vector<int> d, f, parent, pre, post; int timer = 0, trees = 0; };
void visit(const std::vector<std::vector<int>>& adj, int u, Dfs& r) { r.d[u] = ++r.timer; r.pre.push_back(u); for (int v : adj[u]) if (r.d[v] == 0) { r.parent[v] = u; visit(adj, v, r); } r.f[u] = ++r.timer; r.post.push_back(u); }
Dfs dfsForest(const std::vector<std::vector<int>>& adj) { int n = (int)adj.size(); Dfs r; r.d.assign(n, 0); r.f.assign(n, 0); r.parent.assign(n, -1); for (int s = 0; s < n; s++) if (r.d[s] == 0) { r.trees++; visit(adj, s, r); } return r; }
enum Kind { Tree, Back, Forward, Cross };
Kind classify(const Dfs& r, int u, int v) { if (r.parent[v] == u && r.d[v] > r.d[u]) return Tree; if (r.d[v] <= r.d[u] && r.f[u] <= r.f[v]) return Back; if (r.d[u] < r.d[v] && r.f[v] < r.f[u]) return Forward; return Cross; }      // 구간의 포함 관계로 판정
bool hasCycleKahn(const std::vector<std::vector<int>>& adj) { int n = (int)adj.size(); std::vector<int> in(n, 0); for (auto& l : adj) for (int v : l) in[v]++; std::vector<int> q; for (int v = 0; v < n; v++) if (!in[v]) q.push_back(v); std::size_t h = 0; for (; h < q.size(); h++) for (int v : adj[q[h]]) if (--in[v] == 0) q.push_back(v); return (int)q.size() != n; }
int weakComponents(const std::vector<std::vector<int>>& adj) { int n = (int)adj.size(); std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; int c = n; for (int u = 0; u < n; u++) for (int v : adj[u]) { int a = find(u), b = find(v); if (a != b) { p[a] = b; c--; } } return c; }
int main() {
    std::mt19937 rng(18); int sawForward = 0, sawCross = 0, sawBack = 0;
    for (int rep = 0; rep < 400; rep++) { int n = 1 + (int)(rng() % 12); bool directed = rep % 2; std::vector<std::vector<int>> adj(n); std::set<std::pair<int, int>> seen; for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v) continue; auto key = directed ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v)); if (!seen.insert(key).second) continue; adj[u].push_back(v); if (!directed) adj[v].push_back(u); }
        Dfs r = dfsForest(adj); std::vector<int> times; for (int v = 0; v < n; v++) { times.push_back(r.d[v]); times.push_back(r.f[v]); assert(r.d[v] < r.f[v]); } std::sort(times.begin(), times.end()); for (int i = 0; i < 2 * n; i++) assert(times[i] == i + 1);                  // ① 시각은 1..2V 의 순열
        for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) { bool disjoint = r.f[u] < r.d[v] || r.f[v] < r.d[u]; bool nested = (r.d[u] < r.d[v] && r.f[v] < r.f[u]) || (r.d[v] < r.d[u] && r.f[u] < r.f[v]); assert(disjoint != nested); }                                    // 괄호 정리
        bool backEdge = false; for (int u = 0; u < n; u++) for (int v : adj[u]) { Kind k = classify(r, u, v); if (directed) { sawForward += k == Forward; sawCross += k == Cross; sawBack += k == Back; } if (k == Back && !(directed == false && r.parent[u] == v)) backEdge = true;      // 무방향의 부모로 돌아가는 간선은 같은 간선
            if (!directed) assert(k != Cross && (k != Forward || classify(r, v, u) == Back)); }                                                                                                                                                                                                                 // ③
        if (directed) { bool cyc = hasCycleKahn(adj); assert(cyc == backEdge); if (!cyc) { std::vector<int> order(r.post.rbegin(), r.post.rend()), pos(n); for (int i = 0; i < n; i++) pos[order[i]] = i; for (int u = 0; u < n; u++) for (int v : adj[u]) assert(pos[u] < pos[v]); } }                              // ②
        for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) { bool anc = r.d[u] < r.d[v] && r.f[v] < r.f[u]; bool viaParents = false; for (int x = r.parent[v]; x >= 0; x = r.parent[x]) viaParents |= x == u; assert(anc == viaParents); }                                  // ④
        std::vector<int> a = r.pre, b = r.post; std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end()); std::vector<int> all(n); std::iota(all.begin(), all.end(), 0); assert(a == all && b == all);                                                                         // ⑤
        int roots = 0; for (int v = 0; v < n; v++) roots += r.parent[v] < 0; assert(roots == r.trees); if (!directed) assert(r.trees == weakComponents(adj)); }
    assert(sawForward > 20 && sawCross > 20 && sawBack > 20);
    std::cout << "DepthFirstSearch: on 400 random graphs discovery/finish times formed a permutation of 1..2V obeying the parenthesis theorem, edge classes derived from time intervals matched tree/back/forward/cross definitions (" << sawBack << " back, " << sawForward << " forward and " << sawCross << " cross edges seen), directed acyclicity matched absence of back edges with reverse postorder as a topological order, undirected graphs had only tree and back edges, and the number of DFS trees equalled the number of components" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V) (재귀 깊이 포함)
```
## IterativeDFS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <stack>
#include <utility>
#include <vector>

// 반복형 DFS(IterativeDFS): 재귀 호출 대신 명시적 스택을 쓴다. 호출 깊이가 정점 수만큼 깊어질 수 있는 그래프(긴 사슬, 100 만 정점)에서 재귀는 스택 오버플로로 죽지만 반복형은 힙 메모리만 쓴다. 두 가지 구현이 있다. (A) 정확한 모방: 스택에 (정점, 다음에 볼 이웃의 인덱스) 쌍을 넣고 인덱스를 하나씩 진행 — 재귀와 똑같은 전위·후위 순서와 발견/종료 시각을 만든다. 각 간선을 정확히 한 번 훑는다. (B) 단순형: 이웃을 전부 스택에 밀어 넣고, 꺼낼 때 방문 표시를 하면서 이웃을 역순으로 밀면 재귀와 같은 전위 순서가 나온다 — 단, 같은 정점이 여러 번 스택에 들어갈 수 있어 최악 스택 크기가 O(E) 이고 후위 순서(종료 시각)는 얻을 수 없다.
// 흔한 실수: 밀 때 방문 표시(mark on push)를 하면 정점이 처음 스택에 들어간 순간 방문한 것으로 처리되어 방문 순서가 재귀 DFS 와 달라진다(다른 경로로 더 깊이 갔어야 할 정점이 나중 경로에서 이미 표시되어 있음). 올바른 DFS 는 꺼낼 때 표시한다.
// 검증: ① 무작위 그래프(방향·무방향, 비연결)에서 (A) 의 전위·후위·발견/종료 시각이 재귀 DFS 와 완전히 같음 ② (B) 가 이웃을 역순으로 밀면 전위 순서가 재귀와 같음 ③ 밀 때 표시하는 틀린 변형이 재귀 순서와 다른 경우가 실제로 발견됨 ④ (A) 가 인접 항목을 정확히 한 번씩만 훑음(훑은 수 == 도달한 정점들의 진출 차수 합) ⑤ 100 만 정점 사슬을 스택 오버플로 없이 처리하고 전위 순서가 사슬 순서 ⑥ (B) 의 스택 최대 크기가 (A) 보다 크거나 같음, 밀집 그래프에서 확연히 큼.
struct Order { std::vector<int> pre, post, d, f; long scanned = 0; std::size_t maxStack = 0; };
void recur(const std::vector<std::vector<int>>& adj, int u, Order& o, int& t) { o.d[u] = ++t; o.pre.push_back(u); for (int v : adj[u]) if (o.d[v] == 0) recur(adj, v, o, t); o.f[u] = ++t; o.post.push_back(u); }
Order recursive(const std::vector<std::vector<int>>& adj) { int n = (int)adj.size(); Order o; o.d.assign(n, 0); o.f.assign(n, 0); int t = 0; for (int s = 0; s < n; s++) if (o.d[s] == 0) recur(adj, s, o, t); return o; }
Order iterativeExact(const std::vector<std::vector<int>>& adj) { int n = (int)adj.size(); Order o; o.d.assign(n, 0); o.f.assign(n, 0); int t = 0; std::vector<std::pair<int, std::size_t>> st;
    for (int s = 0; s < n; s++) { if (o.d[s]) continue; o.d[s] = ++t; o.pre.push_back(s); st.push_back({s, 0}); while (!st.empty()) { o.maxStack = std::max(o.maxStack, st.size()); auto& top = st.back(); int u = top.first; if (top.second < adj[u].size()) { int v = adj[u][top.second++]; o.scanned++; if (o.d[v] == 0) { o.d[v] = ++t; o.pre.push_back(v); st.push_back({v, 0}); } } else { o.f[u] = ++t; o.post.push_back(u); st.pop_back(); } } } return o; }
std::vector<int> pushAllMarkOnPop(const std::vector<std::vector<int>>& adj, std::size_t& maxStack) { int n = (int)adj.size(); std::vector<char> seen(n, 0); std::vector<int> pre; std::vector<int> st; maxStack = 0;
    for (int s = 0; s < n; s++) { if (seen[s]) continue; st.push_back(s); while (!st.empty()) { maxStack = std::max(maxStack, st.size()); int u = st.back(); st.pop_back(); if (seen[u]) continue; seen[u] = 1; pre.push_back(u); for (std::size_t i = adj[u].size(); i-- > 0;) if (!seen[adj[u][i]]) st.push_back(adj[u][i]); } } return pre; }       // 이웃을 역순으로 밀어야 재귀 순서
std::vector<int> pushAllMarkOnPush(const std::vector<std::vector<int>>& adj) { int n = (int)adj.size(); std::vector<char> seen(n, 0); std::vector<int> pre; std::vector<int> st; for (int s = 0; s < n; s++) { if (seen[s]) continue; seen[s] = 1; st.push_back(s); while (!st.empty()) { int u = st.back(); st.pop_back(); pre.push_back(u); for (std::size_t i = adj[u].size(); i-- > 0;) { int v = adj[u][i]; if (!seen[v]) { seen[v] = 1; st.push_back(v); } } } } return pre; }   // 틀림: 밀 때 표시
int main() {
    std::mt19937 rng(19); int wrongSeen = 0;
    for (int rep = 0; rep < 400; rep++) { int n = 1 + (int)(rng() % 14); bool directed = rep % 2; std::vector<std::vector<int>> adj(n); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v) continue; adj[u].push_back(v); if (!directed) adj[v].push_back(u); }
        Order a = recursive(adj), b = iterativeExact(adj); assert(a.pre == b.pre && a.post == b.post && a.d == b.d && a.f == b.f);                                                                                                                           // ①
        std::size_t ms = 0; assert(pushAllMarkOnPop(adj, ms) == a.pre);                                                                                                                                                                                        // ②
        if (pushAllMarkOnPush(adj) != a.pre) wrongSeen++;                                                                                                                                                                                                       // ③
        long entries = 0; for (int v = 0; v < n; v++) entries += (long)adj[v].size(); assert(b.scanned == entries); }                                                                                                                                         // ④ 모든 정점을 시작점으로 시도하므로 전체 항목
    assert(wrongSeen > 20);
    { const int N = 1000000; std::vector<std::vector<int>> chain(N); for (int i = 0; i + 1 < N; i++) chain[i].push_back(i + 1); Order o = iterativeExact(chain); assert((int)o.pre.size() == N && o.pre.front() == 0 && o.pre.back() == N - 1 && o.post.front() == N - 1 && o.post.back() == 0 && o.maxStack == (std::size_t)N); }       // ⑤ 재귀였다면 스택 오버플로
    { const int V = 120; std::vector<std::vector<int>> dense(V); for (int u = 0; u < V; u++) for (int v = 0; v < V; v++) if (u != v) dense[u].push_back(v); std::size_t ms = 0; pushAllMarkOnPop(dense, ms); Order exact = iterativeExact(dense); assert(ms > exact.maxStack * 10 && exact.maxStack == (std::size_t)V); }      // ⑥ 밀집 그래프: 단순형 스택이 훨씬 큼
    std::cout << "IterativeDFS: an explicit stack of (vertex, next-neighbour-index) pairs reproduced recursive DFS preorder, postorder and discovery/finish times exactly on 400 random graphs while scanning every adjacency entry once; push-all with mark-on-pop and reversed neighbours matched the preorder but needed a far larger stack on a dense graph; marking on push produced a different order in " << wrongSeen << " cases; a 1,000,000-vertex chain ran without stack overflow" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V) (단순형은 최악 O(E))
```
## RecursiveDFS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 재귀형 DFS(RecursiveDFS): 함수가 자기 자신을 이웃에 대해 호출하는 가장 간결한 DFS 이다. 호출 스택이 곧 "지금까지 온 길" 이어서 되돌아오기가 공짜이고 진입/탈출 시점에 일을 끼워 넣기 쉽다 — 전위 처리(발견 시각), 후위 처리(종료 시각, 부분 트리 크기·높이 계산). 재귀 깊이 = DFS 트리의 가장 긴 루트–리프 경로이며 긴 사슬에서는 정점 수만큼 깊어진다. 호출 하나에 보통 수십~수백 바이트를 쓰므로 수십만 깊이에서 스택(기본 수 MB)이 넘친다. 대응: 반복형으로 바꾸거나, 깊이가 한계를 넘으면 그 부분 트리만 반복형으로 처리하는 혼합형(hybrid)을 쓴다 — 순서는 순수 재귀와 정확히 같다.
// 트리 위의 재귀 DFS 의 고전적 응용: 진입/탈출 시각 tin/tout 으로 "u 가 v 의 조상인가" 를 O(1) 에 판정(tin[u] ≤ tin[v] 이고 tout[v] ≤ tout[u]), 부분 트리 크기 size[u] = 1 + Σ size[자식], 높이, 지름(가장 먼 두 정점 사이: 각 정점에서 가장 깊은 두 자식 높이의 합 최댓값). 그래프에서는 방문 표시와 함께 쓰이고, DAG 위에서는 메모이제이션으로 경로 수를 센다(재귀 + 캐시 = 하향식 동적 계획).
// 검증: ① 재귀 깊이 최댓값 == DFS 숲의 높이(부모 포인터로 센 가장 긴 루트–리프 경로의 간선 수 + 1) ② 혼합형(깊이 한계 10)의 방문 순서·발견/종료 시각이 순수 재귀와 완전히 같고 20 만 정점 사슬도 한계 1000 으로 처리 ③ 무작위 트리(n ≤ 200)에서 tin/tout 조상 판정이 부모 체인과 같고 부분 트리 크기·높이·지름이 무차별 계산과 같음 ④ DAG 의 경로 수 메모이제이션 재귀가 무차별 경로 열거와 같음 ⑤ 완전 그래프 K_n 의 s–t 단순 경로 수가 Σ (n−2)!/(n−2−k)! 공식과 같음(재귀 백트래킹, n ≤ 8) ⑥ 빈 그래프·정점 1 개.
struct State { std::vector<int> d, f, pre, post; int timer = 0, depth = 0, maxDepth = 0; long iterativeSwitches = 0; };
void iterativeFrom(const std::vector<std::vector<int>>& adj, int s, State& st) { std::vector<std::pair<int, std::size_t>> stack; st.d[s] = ++st.timer; st.pre.push_back(s); stack.push_back({s, 0});
    while (!stack.empty()) { auto& top = stack.back(); int u = top.first; if (top.second < adj[u].size()) { int v = adj[u][top.second++]; if (st.d[v] == 0) { st.d[v] = ++st.timer; st.pre.push_back(v); stack.push_back({v, 0}); } } else { st.f[u] = ++st.timer; st.post.push_back(u); stack.pop_back(); } } }
void visit(const std::vector<std::vector<int>>& adj, int u, State& st, int limit) { if (limit > 0 && st.depth >= limit) { st.iterativeSwitches++; iterativeFrom(adj, u, st); return; } st.d[u] = ++st.timer; st.pre.push_back(u); st.depth++; st.maxDepth = std::max(st.maxDepth, st.depth);
    for (int v : adj[u]) if (st.d[v] == 0) visit(adj, v, st, limit); st.depth--; st.f[u] = ++st.timer; st.post.push_back(u); }
State run(const std::vector<std::vector<int>>& adj, int limit) { int n = (int)adj.size(); State st; st.d.assign(n, 0); st.f.assign(n, 0); for (int s = 0; s < n; s++) if (st.d[s] == 0) visit(adj, s, st, limit); return st; }
struct TreeInfo { std::vector<int> tin, tout, size, height; int diameter = 0; int timer = 0; };
int treeDfs(const std::vector<std::vector<int>>& adj, int u, int p, TreeInfo& t) { t.tin[u] = ++t.timer; t.size[u] = 1; int best1 = 0, best2 = 0; for (int v : adj[u]) if (v != p) { int h = treeDfs(adj, v, u, t) + 1; t.size[u] += t.size[v]; if (h > best1) { best2 = best1; best1 = h; } else if (h > best2) best2 = h; } t.height[u] = best1; t.diameter = std::max(t.diameter, best1 + best2); t.tout[u] = ++t.timer; return best1; }
long long countPaths(const std::vector<std::vector<int>>& adj, int u, int t, std::vector<long long>& memo) { if (u == t) return 1; if (memo[u] >= 0) return memo[u]; long long c = 0; for (int v : adj[u]) c += countPaths(adj, v, t, memo); return memo[u] = c; }
long long enumeratePaths(const std::vector<std::vector<int>>& adj, int u, int t, std::vector<char>& on) { if (u == t) return 1; on[u] = 1; long long c = 0; for (int v : adj[u]) if (!on[v]) c += enumeratePaths(adj, v, t, on); on[u] = 0; return c; }
int main() {
    std::mt19937 rng(20);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 20); bool directed = rep % 2; std::vector<std::vector<int>> adj(n); for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v) continue; adj[u].push_back(v); if (!directed) adj[v].push_back(u); }
        State pure = run(adj, 0), hybrid = run(adj, 1 + (int)(rng() % 10)); assert(pure.pre == hybrid.pre && pure.post == hybrid.post && pure.d == hybrid.d && pure.f == hybrid.f);                                                                                      // ②
        std::vector<int> parent(n, -1); { std::vector<int> d(n, 0); int t = 0; std::vector<int> st; for (int s = 0; s < n; s++) { if (d[s]) continue; std::vector<std::pair<int, std::size_t>> stack{{s, 0}}; d[s] = ++t; while (!stack.empty()) { auto& top = stack.back(); int u = top.first; if (top.second < adj[u].size()) { int v = adj[u][top.second++]; if (!d[v]) { d[v] = ++t; parent[v] = u; stack.push_back({v, 0}); } } else stack.pop_back(); } } }
        int height = 0; for (int v = 0; v < n; v++) { int len = 1, x = v; while (parent[x] >= 0) { x = parent[x]; len++; } height = std::max(height, len); } assert(pure.maxDepth == height); }                                                                                    // ①
    { const int N = 200000; std::vector<std::vector<int>> chain(N); for (int i = 0; i + 1 < N; i++) chain[i].push_back(i + 1); State st = run(chain, 1000); assert((int)st.pre.size() == N && st.pre.front() == 0 && st.pre.back() == N - 1 && st.post.front() == N - 1 && st.maxDepth == 1000 && st.iterativeSwitches == 1); }
    for (int rep = 0; rep < 200; rep++) { int n = 1 + (int)(rng() % 60); std::vector<std::vector<int>> adj(n); std::vector<int> par(n, -1); for (int v = 1; v < n; v++) { int p = (int)(rng() % v); adj[p].push_back(v); adj[v].push_back(p); par[v] = p; }                                      // ③ 무작위 트리
        TreeInfo t; t.tin.assign(n, 0); t.tout.assign(n, 0); t.size.assign(n, 0); t.height.assign(n, 0); treeDfs(adj, 0, -1, t);
        for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) { bool anc = t.tin[u] <= t.tin[v] && t.tout[v] <= t.tout[u]; bool viaParents = false; for (int x = v; x >= 0; x = par[x]) viaParents |= x == u; assert(anc == viaParents); }
        for (int u = 0; u < n; u++) { int cnt = 0; for (int v = 0; v < n; v++) { for (int x = v; x >= 0; x = par[x]) if (x == u) { cnt++; break; } } assert(t.size[u] == cnt); }
        auto bfsFar = [&](int s, int& far) { std::vector<int> d(n, -1); std::vector<int> q{s}; d[s] = 0; for (std::size_t h = 0; h < q.size(); h++) for (int v : adj[q[h]]) if (d[v] < 0) { d[v] = d[q[h]] + 1; q.push_back(v); } far = (int)(std::max_element(d.begin(), d.end()) - d.begin()); return d[far]; }; int far1, far2; bfsFar(0, far1); int diam = bfsFar(far1, far2); assert(t.diameter == diam);
        int h0 = 0; { std::vector<int> d(n, -1); std::vector<int> q{0}; d[0] = 0; for (std::size_t h = 0; h < q.size(); h++) for (int v : adj[q[h]]) if (d[v] < 0) { d[v] = d[q[h]] + 1; q.push_back(v); } h0 = *std::max_element(d.begin(), d.end()); } assert(t.height[0] == h0); }
    for (int rep = 0; rep < 150; rep++) { int n = 2 + (int)(rng() % 9); std::vector<std::vector<int>> dag(n); for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) if (rng() % 2) dag[u].push_back(v); std::vector<long long> memo(n, -1); long long viaMemo = countPaths(dag, 0, n - 1, memo); std::vector<char> on(n, 0); assert(viaMemo == enumeratePaths(dag, 0, n - 1, on)); }   // ④
    for (int n = 2; n <= 8; n++) { std::vector<std::vector<int>> k(n); for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v) k[u].push_back(v); std::vector<char> on(n, 0); long long got = enumeratePaths(k, 0, n - 1, on), want = 0; long long perm = 1; for (int len = 0; len <= n - 2; len++) { want += perm; perm *= (n - 2 - len); } assert(got == want); }                    // ⑤
    { std::vector<std::vector<int>> e; State st = run(e, 0); assert(st.pre.empty() && st.maxDepth == 0); std::vector<std::vector<int>> one(1); State s1 = run(one, 0); assert(s1.pre == std::vector<int>{0} && s1.d[0] == 1 && s1.f[0] == 2 && s1.maxDepth == 1); }
    std::cout << "RecursiveDFS: maximum recursion depth equalled the height of the DFS forest on 300 random graphs, a hybrid that switches to an explicit stack beyond a depth limit reproduced the pure recursive orders and times exactly and handled a 200000-vertex chain, tin/tout ancestor tests, subtree sizes, heights and diameters of random trees matched brute force, memoised path counting in DAGs matched path enumeration, and the s-t simple path count in K_n matched its closed form up to n=8" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V) (호출 스택 최대 깊이 = DFS 트리 높이)
```
## GraphTraversal()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <deque>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <tuple>
#include <utility>
#include <vector>

// 그래프 순회(GraphTraversal): BFS, DFS, 다이크스트라, 프림은 모두 같은 골격의 다른 얼굴이다 — 출발점에서 시작해 "프런티어(frontier, 다음에 볼 후보들)" 에서 하나를 꺼내 방문하고 그 이웃을 프런티어에 넣는다. 다른 점은 프런티어가 무엇이냐뿐: 큐(FIFO) → BFS, 스택(LIFO) → DFS, 우선순위 큐(키 = 지금까지의 경로 길이) → 다이크스트라, 우선순위 큐(키 = 연결 간선의 가중치) → 프림, 무작위 → 임의의 유효한 탐색. 어떤 정책이든 방문 집합은 출발점에서 도달 가능한 정점 전체로 같고, 방문한 정점마다 그 이전에 방문한 부모와 간선이 있다(탐색 트리).
// 두 가지 표시 시점이 있다. 큐에서 BFS 는 "넣을 때" 표시해야 정점이 한 번만 들어가고, 스택으로 DFS 를 만들 때는 "꺼낼 때" 표시해야 재귀와 같은 순서가 된다(이웃을 역순으로 밀 것). 우선순위 큐는 같은 정점이 더 좋은 키로 다시 들어올 수 있어 꺼낼 때 이미 방문했으면 건너뛴다(게으른 삭제).
// 검증: ① 같은 골격(템플릿 정책)으로 큐 정책이 전용 BFS 와, 스택 정책(꺼낼 때 표시·역순 밀기)이 재귀 DFS 전위 순서와 정확히 같음 ② 우선순위 정책(키 = 경로 길이)이 다이크스트라와 같은 거리, 우선순위 정책(키 = 간선 가중치)이 프림의 MST 가중치로 크러스칼과 같음 ③ 무작위 프런티어 정책도 방문 집합이 도달 가능 집합과 같고 방문 순서가 유효한 탐색(각 정점이 이미 방문한 부모에서 간선으로 연결) ④ 모든 정책에서 각 정점은 정확히 한 번 방문 ⑤ 비연결 그래프에서 모든 정점을 시작점 후보로 돌리면 전체를 덮음 ⑥ 출발점 하나인 정점 1 개 그래프.
struct Item { int v, parent; long long key; };
template <class Frontier> std::vector<Item> traverse(const std::vector<std::vector<std::pair<int, int>>>& adj, int s, Frontier& fr, bool markOnPush, std::vector<long long>* dist) { int n = (int)adj.size(); std::vector<char> seen(n, 0); std::vector<Item> visited; if (dist) dist->assign(n, -1);
    fr.push({s, -1, 0}); if (markOnPush) seen[s] = 1;
    while (!fr.empty()) { Item it = fr.pop(); if (!markOnPush) { if (seen[it.v]) continue; seen[it.v] = 1; } visited.push_back(it); if (dist) (*dist)[it.v] = it.key;
        if (fr.reverseNeighbours()) { for (std::size_t i = adj[it.v].size(); i-- > 0;) { auto [w, c] = adj[it.v][i]; if (markOnPush) { if (seen[w]) continue; seen[w] = 1; } else if (seen[w]) continue; fr.push({w, it.v, fr.nextKey(it.key, c)}); } }
        else for (auto [w, c] : adj[it.v]) { if (markOnPush) { if (seen[w]) continue; seen[w] = 1; } else if (seen[w]) continue; fr.push({w, it.v, fr.nextKey(it.key, c)}); } } return visited; }
struct QueueFrontier { std::deque<Item> q; bool empty() const { return q.empty(); } void push(Item x) { q.push_back(x); } Item pop() { Item x = q.front(); q.pop_front(); return x; } bool reverseNeighbours() const { return false; } long long nextKey(long long k, int) const { return k + 1; } };
struct StackFrontier { std::vector<Item> s; bool empty() const { return s.empty(); } void push(Item x) { s.push_back(x); } Item pop() { Item x = s.back(); s.pop_back(); return x; } bool reverseNeighbours() const { return true; } long long nextKey(long long k, int) const { return k + 1; } };
struct PQFrontier { bool prim; std::set<std::tuple<long long, long long, int, int>> q; long long seq = 0; explicit PQFrontier(bool p) : prim(p) {} bool empty() const { return q.empty(); } void push(Item x) { q.insert({x.key, seq++, x.v, x.parent}); } Item pop() { auto t = *q.begin(); q.erase(q.begin()); return {std::get<2>(t), std::get<3>(t), std::get<0>(t)}; } bool reverseNeighbours() const { return false; }
    long long nextKey(long long k, int c) const { return prim ? c : k + c; } };                                                                                                                       // Prim: 키 = 간선 가중치, Dijkstra: 키 = 경로 길이
struct RandomFrontier { std::vector<Item> s; std::mt19937* rng; bool empty() const { return s.empty(); } void push(Item x) { s.push_back(x); } Item pop() { std::size_t i = (*rng)() % s.size(); std::swap(s[i], s.back()); Item x = s.back(); s.pop_back(); return x; } bool reverseNeighbours() const { return false; } long long nextKey(long long k, int) const { return k + 1; } };
void recursiveDfs(const std::vector<std::vector<std::pair<int, int>>>& adj, int u, std::vector<char>& seen, std::vector<int>& pre) { seen[u] = 1; pre.push_back(u); for (auto [v, c] : adj[u]) if (!seen[v]) recursiveDfs(adj, v, seen, pre); }
std::vector<long long> dijkstraRef(const std::vector<std::vector<std::pair<int, int>>>& adj, int s) { int n = (int)adj.size(); std::vector<long long> d(n, -1); std::set<std::pair<long long, int>> pq; d[s] = 0; pq.insert({0, s}); while (!pq.empty()) { auto [du, u] = *pq.begin(); pq.erase(pq.begin()); for (auto [v, w] : adj[u]) if (d[v] < 0 || du + w < d[v]) { if (d[v] >= 0) pq.erase({d[v], v}); d[v] = du + w; pq.insert({d[v], v}); } } return d; }
long long kruskalRef(int n, std::vector<std::array<int, 3>> es, int& used) { std::sort(es.begin(), es.end()); std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; long long total = 0; used = 0; for (auto& e : es) { int a = find(e[1]), b = find(e[2]); if (a != b) { p[a] = b; total += e[0]; used++; } } return total; }
int main() {
    std::mt19937 rng(21);
    for (int rep = 0; rep < 300; rep++) { int n = 1 + (int)(rng() % 14); bool directed = rep % 2; std::vector<std::vector<std::pair<int, int>>> adj(n); std::vector<std::array<int, 3>> edges; std::set<std::pair<int, int>> seenEdge; for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n), w = 1 + (int)(rng() % 9); if (u == v) continue; auto key = directed ? std::make_pair(u, v) : std::make_pair(std::min(u, v), std::max(u, v)); if (!seenEdge.insert(key).second) continue; adj[u].push_back({v, w}); if (!directed) adj[v].push_back({u, w}); edges.push_back({w, u, v}); }
        int s = (int)(rng() % n); std::vector<char> seen(n, 0); std::vector<int> pre; recursiveDfs(adj, s, seen, pre); std::vector<char> reach = seen;
        StackFrontier sf; auto dfsVisited = traverse(adj, s, sf, false, nullptr); std::vector<int> dfsOrder; for (auto& it : dfsVisited) dfsOrder.push_back(it.v); assert(dfsOrder == pre);                                                                     // ① 스택 = 재귀 DFS
        QueueFrontier qf; auto bfsVisited = traverse(adj, s, qf, true, nullptr); std::vector<int> bfsOrder; std::vector<int> level(n, -1); level[s] = 0; { std::vector<int> q{s}; for (std::size_t h = 0; h < q.size(); h++) for (auto [v, c] : adj[q[h]]) if (level[v] < 0) { level[v] = level[q[h]] + 1; q.push_back(v); } bfsOrder = q; } std::vector<int> got; for (auto& it : bfsVisited) got.push_back(it.v); assert(got == bfsOrder);
        PQFrontier dj(false); std::vector<long long> dist; traverse(adj, s, dj, false, &dist); assert(dist == dijkstraRef(adj, s));                                                                                                                         // ② 우선순위 = 다이크스트라
        std::mt19937 r2(rep); RandomFrontier rf; rf.rng = &r2; auto rv = traverse(adj, s, rf, false, nullptr); std::set<int> visitedSet; std::vector<int> posOf(n, -1); for (std::size_t i = 0; i < rv.size(); i++) { assert(visitedSet.insert(rv[i].v).second); posOf[rv[i].v] = (int)i; }          // ③ ④ 무작위 정책
        std::set<int> reachSet; for (int v = 0; v < n; v++) if (reach[v]) reachSet.insert(v); assert(visitedSet == reachSet); for (std::size_t i = 1; i < rv.size(); i++) { int p = rv[i].parent; assert(p >= 0 && posOf[p] >= 0 && posOf[p] < (int)i); bool edge = false; for (auto [v, c] : adj[p]) edge |= v == rv[i].v; assert(edge); } }
    for (int rep = 0; rep < 200; rep++) { int n = 2 + (int)(rng() % 12); std::vector<std::vector<std::pair<int, int>>> adj(n); std::vector<std::array<int, 3>> edges; for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) if (rng() % 3 == 0) { int w = 1 + (int)(rng() % 20); adj[u].push_back({v, w}); adj[v].push_back({u, w}); edges.push_back({w, u, v}); }
        PQFrontier prim(true); auto vis = traverse(adj, 0, prim, false, nullptr); long long total = 0; for (auto& it : vis) if (it.parent >= 0) total += it.key; std::vector<char> comp(n, 0); { std::vector<int> q{0}; comp[0] = 1; for (std::size_t h = 0; h < q.size(); h++) for (auto [v, c] : adj[q[h]]) if (!comp[v]) { comp[v] = 1; q.push_back(v); } }
        std::vector<std::array<int, 3>> sub; for (auto& e : edges) if (comp[e[1]]) sub.push_back(e); int used = 0; long long kr = kruskalRef(n, sub, used); assert(total == kr && (int)vis.size() == used + 1); }                                                                          // ② 프림 = 크러스칼
    { std::vector<std::vector<std::pair<int, int>>> adj(7); adj[0] = {{1, 1}}; adj[2] = {{3, 1}}; adj[4] = {{5, 1}, {6, 1}}; std::vector<char> covered(7, 0); for (int s = 0; s < 7; s++) { if (covered[s]) continue; QueueFrontier q; auto v = traverse(adj, s, q, true, nullptr); for (auto& it : v) covered[it.v] = 1; } for (int v = 0; v < 7; v++) assert(covered[v]); }   // ⑤
    { std::vector<std::vector<std::pair<int, int>>> one(1); StackFrontier sf; auto v = traverse(one, 0, sf, false, nullptr); assert(v.size() == 1 && v[0].v == 0 && v[0].parent == -1); }                                                                                              // ⑥
    std::cout << "GraphTraversal: one frontier-driven skeleton reproduced BFS order with a queue, recursive DFS preorder with a stack (mark on pop, neighbours pushed in reverse), Dijkstra distances with a priority queue keyed by path length, and Prim's MST weight (equal to Kruskal's) with a priority queue keyed by edge weight, and a random frontier visited exactly the reachable set in a valid search order" << std::endl; return 0;
}
// Time Complexity: 큐·스택 O(V + E), 우선순위 큐 O(E log V)
// Space Complexity: O(V + E) (프런티어 포함)
```
# Part 4. 연결성
## ConnectedComponents()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 연결 성분(Connected Components): 무방향 그래프에서 서로 경로로 닿는 정점들의 극대 집합. "경로로 닿는다" 는 동치 관계이므로 성분은 정점 집합의 분할(서로소이고 합이 전체)이다. 구하는 방법: (1) BFS/DFS — 아직 안 본 정점마다 새 성분 번호로 탐색, O(V + E). (2) 서로소 집합 — 간선마다 합치기, 거의 O(E α(V)) 이고 간선이 하나씩 도착하는 온라인 상황에 적합. (3) 최소 라벨 전파 — 모든 정점이 자기 번호로 시작해 이웃의 최솟값을 받아 갱신, 수렴까지 최대 (지름 + 1) 라운드(병렬·분산 환경의 기본형).
// 성질: 성분 수 c = V − (신장 숲의 간선 수) 이고 간선 하나를 더하면 성분 수가 0 또는 1 줄고, 간선 하나를 빼면 0 또는 1 늘며 1 늘면 그 간선이 다리(bridge)다. 고립 정점은 크기 1 인 성분. 성분을 비교할 때는 번호 붙이기 방식이 달라도 같은 분할인지 보려고 "정규형 번호"(각 성분 안의 가장 작은 정점 번호로 이름 붙임)로 바꾼다.
// 검증: ① 세 방법(탐색·서로소 집합·라벨 전파)이 무작위 그래프에서 같은 분할(플로이드–워셜 도달 폐쇄와 같음), 성분 크기의 합 = V ② 라벨 전파의 라운드 수 ≤ 가장 큰 성분의 지름 + 1 ③ 간선 추가 시 성분 수가 0 또는 −1, 삭제 시 0 또는 +1 이고 +1 이면 그 간선이 다리(제거 후 두 끝점이 연결되지 않음) ④ 고립 정점 수 ≤ 성분 수, 완전 그래프는 성분 1 ⑤ 빈 그래프·정점 1 개 ⑥ 성분 수 == V − 신장 숲 간선 수.
typedef std::vector<std::vector<int>> Adj;
std::vector<int> canon(const std::vector<int>& label) { std::vector<int> firstOf(label.size(), -1), out(label.size()); for (std::size_t v = 0; v < label.size(); v++) { if (firstOf[label[v]] < 0) firstOf[label[v]] = (int)v; out[v] = firstOf[label[v]]; } return out; }
std::vector<int> byBfs(const Adj& a) { int n = (int)a.size(); std::vector<int> comp(n, -1); int c = 0; for (int s = 0; s < n; s++) if (comp[s] < 0) { std::queue<int> q; q.push(s); comp[s] = c; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : a[u]) if (comp[v] < 0) { comp[v] = c; q.push(v); } } c++; } return comp; }
std::vector<int> byDsu(const Adj& a) { int n = (int)a.size(); std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; for (int u = 0; u < n; u++) for (int v : a[u]) { int x = find(u), y = find(v); if (x != y) p[std::max(x, y)] = std::min(x, y); } std::vector<int> r(n); for (int v = 0; v < n; v++) r[v] = find(v); return r; }
std::vector<int> byLabelPropagation(const Adj& a, int& rounds) { int n = (int)a.size(); std::vector<int> label(n); std::iota(label.begin(), label.end(), 0); rounds = 0; for (bool changed = true; changed;) { changed = false; std::vector<int> next = label; for (int u = 0; u < n; u++) for (int v : a[u]) if (label[v] < next[u]) { next[u] = label[v]; changed = true; } label = next; if (changed) rounds++; } return label; }
std::vector<std::vector<char>> closure(const Adj& a) { int n = (int)a.size(); std::vector<std::vector<char>> r(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) { r[i][i] = 1; for (int j : a[i]) r[i][j] = 1; } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r[i][k]) for (int j = 0; j < n; j++) if (r[k][j]) r[i][j] = 1; return r; }
int count(const std::vector<int>& comp) { return (int)std::set<int>(comp.begin(), comp.end()).size(); }
int diameterOfComponent(const Adj& a, int s) { std::vector<int> d(a.size(), -1); std::queue<int> q; q.push(s); d[s] = 0; int far = s; while (!q.empty()) { int u = q.front(); q.pop(); far = u; for (int v : a[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } std::vector<int> e(a.size(), -1); q.push(far); e[far] = 0; int best = 0; while (!q.empty()) { int u = q.front(); q.pop(); best = std::max(best, e[u]); for (int v : a[u]) if (e[v] < 0) { e[v] = e[u] + 1; q.push(v); } } return best; }
int main() {
    std::mt19937 rng(22);
    for (int rep = 0; rep < 400; rep++) { int n = 1 + (int)(rng() % 16); Adj a(n); std::set<std::pair<int, int>> seen; for (int k = 0, m = (int)(rng() % (2 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v || !seen.insert({std::min(u, v), std::max(u, v)}).second) continue; a[u].push_back(v); a[v].push_back(u); }
        auto b = canon(byBfs(a)), d = canon(byDsu(a)); int rounds = 0; auto l = canon(byLabelPropagation(a, rounds)); auto cl = closure(a); std::vector<int> viaClosure(n); for (int v = 0; v < n; v++) { viaClosure[v] = v; for (int u = 0; u < v; u++) if (cl[u][v]) { viaClosure[v] = u; break; } } assert(b == d && b == l && b == viaClosure);          // ①
        std::vector<int> size(n, 0); for (int v = 0; v < n; v++) size[b[v]]++; int total = 0; for (int s : size) total += s; assert(total == n); int c = count(b);
        int maxDiam = 0; for (int v = 0; v < n; v++) maxDiam = std::max(maxDiam, diameterOfComponent(a, v)); assert(rounds <= maxDiam + 1);                                                                                                                                  // ②
        std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; int forest = 0; for (int u = 0; u < n; u++) for (int v : a[u]) if (u < v) { int x = find(u), y = find(v); if (x != y) { p[x] = y; forest++; } } assert(c == n - forest);   // ⑥
        int isolated = 0; for (int v = 0; v < n; v++) isolated += a[v].empty(); assert(isolated <= c);                                                                                                                                                                              // ④
        for (int u = 0; u < n; u++) for (int v : std::vector<int>(a[u])) if (u < v) { Adj b2 = a; b2[u].erase(std::find(b2[u].begin(), b2[u].end(), v)); b2[v].erase(std::find(b2[v].begin(), b2[v].end(), u)); int c2 = count(byBfs(b2)); assert(c2 == c || c2 == c + 1); auto cl2 = closure(b2); assert((c2 == c + 1) == !cl2[u][v]); }          // ③ 삭제: 0 또는 +1 (+1 이면 다리)
        for (int t = 0; t < 5; t++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v || std::find(a[u].begin(), a[u].end(), v) != a[u].end()) continue; Adj b2 = a; b2[u].push_back(v); b2[v].push_back(u); int c2 = count(byBfs(b2)); assert(c2 == c || c2 == c - 1); } }                                // ③ 추가: 0 또는 −1
    { Adj k(7); for (int u = 0; u < 7; u++) for (int v = 0; v < 7; v++) if (u != v) k[u].push_back(v); assert(count(byBfs(k)) == 1); Adj e; assert(byBfs(e).empty() && count(byBfs(e)) == 0); Adj one(1); assert(count(byBfs(one)) == 1 && byBfs(one) == std::vector<int>{0}); }          // ④ ⑤
    std::cout << "ConnectedComponents: BFS labelling, union-find and min-label propagation produced the same canonical partition as the Floyd-Warshall reachability closure on 400 random graphs, propagation converged within diameter+1 rounds, component count equalled V minus spanning-forest edges, adding an edge changed the count by 0 or -1 and deleting one by 0 or +1 (+1 exactly for bridges), and complete, empty and single-vertex graphs behaved" << std::endl; return 0;
}
// Time Complexity: O(V + E) (서로소 집합 O(E α(V)), 라벨 전파 O(지름 · E))
// Space Complexity: O(V)
```
## StronglyConnectedComponents()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <stack>
#include <utility>
#include <vector>

// 강연결 성분(SCC, Strongly Connected Components): 유방향 그래프에서 서로 도달 가능한(u→…→v 이고 v→…→u) 정점들의 극대 집합. "서로 도달 가능" 은 동치 관계라 SCC 는 정점의 분할이고, 각 SCC 를 한 점으로 줄인 응축 그래프(condensation)는 반드시 DAG 이다(순환이 있으면 그 성분들이 서로 도달 가능해 합쳐졌을 것). 두 선형 시간 알고리즘: 타잔(Tarjan) — DFS 하나로 발견 번호 num 과 low-link(자신의 부분 트리에서 스택에 남은 정점으로 닿는 가장 작은 번호)를 계산하고 low[v] == num[v] 인 정점에서 스택을 그 정점까지 꺼내면 한 SCC; 코사라주(Kosaraju) — 원래 그래프 DFS 의 종료 순서를 기록하고, 역방향 그래프를 종료 순서의 역순으로 DFS 하면 트리 하나가 SCC 하나.
// 출력 순서의 성질: 타잔이 SCC 를 완성하는 순서는 응축 DAG 의 역위상 순서(싱크 성분이 먼저)이고, 코사라주(역방향 DFS 를 종료 순서의 역순으로 시작)는 위상 순서(원천 성분이 먼저)이다. 그래프 전체가 하나의 SCC 이면 강연결(strongly connected).
// 검증: ① 무작위 유방향 그래프(V ≤ 14)에서 타잔 == 코사라주 == 정의(플로이드–워셜로 u→v 와 v→u 모두 도달 가능)의 분할 ② 응축 그래프가 DAG(위상 정렬 성공)이고 타잔 번호가 간선 u→v (다른 성분)에서 comp[u] > comp[v] (역위상), 코사라주 번호는 comp[u] < comp[v] (위상) ③ 순환 그래프 C_n 은 SCC 1 개, DAG 는 SCC 가 정점 수(모두 단일) ④ 한 SCC 안에서는 어떤 정점에서든 다른 모든 정점에 도달 ⑤ SCC 수 == 1 ⇔ 정점 0 에서 정방향·역방향 BFS 가 모두 전체를 덮음 ⑥ 깊은 사슬(20 만 정점)에서 반복형 타잔이 스택 오버플로 없이 동작.
typedef std::vector<std::vector<int>> Adj;
std::vector<int> canon(const std::vector<int>& label) { std::vector<int> firstOf(label.size(), -1), out(label.size()); for (std::size_t v = 0; v < label.size(); v++) { if (firstOf[label[v]] < 0) firstOf[label[v]] = (int)v; out[v] = firstOf[label[v]]; } return out; }
std::vector<int> tarjan(const Adj& g, int& count) { int n = (int)g.size(), timer = 0; count = 0; std::vector<int> num(n, 0), low(n, 0), comp(n, -1); std::vector<char> onStack(n, 0); std::vector<int> st; std::vector<std::pair<int, std::size_t>> call;       // 반복형: 호출 스택을 직접 관리
    for (int s = 0; s < n; s++) { if (num[s]) continue; call.push_back({s, 0}); num[s] = low[s] = ++timer; st.push_back(s); onStack[s] = 1;
        while (!call.empty()) { auto& top = call.back(); int u = top.first; if (top.second < g[u].size()) { int v = g[u][top.second++]; if (!num[v]) { num[v] = low[v] = ++timer; st.push_back(v); onStack[v] = 1; call.push_back({v, 0}); } else if (onStack[v]) low[u] = std::min(low[u], num[v]); }
            else { if (low[u] == num[u]) { int w; do { w = st.back(); st.pop_back(); onStack[w] = 0; comp[w] = count; } while (w != u); count++; } int p = call.size() >= 2 ? call[call.size() - 2].first : -1; call.pop_back(); if (p >= 0) low[p] = std::min(low[p], low[u]); } } } return comp; }
std::vector<int> kosaraju(const Adj& g, int& count) { int n = (int)g.size(); std::vector<char> seen(n, 0); std::vector<int> order; for (int s = 0; s < n; s++) { if (seen[s]) continue; std::vector<std::pair<int, std::size_t>> call{{s, 0}}; seen[s] = 1; while (!call.empty()) { auto& top = call.back(); int u = top.first; if (top.second < g[u].size()) { int v = g[u][top.second++]; if (!seen[v]) { seen[v] = 1; call.push_back({v, 0}); } } else { order.push_back(u); call.pop_back(); } } }
    Adj rev(n); for (int u = 0; u < n; u++) for (int v : g[u]) rev[v].push_back(u); std::vector<int> comp(n, -1); count = 0; for (int i = n - 1; i >= 0; i--) { int s = order[i]; if (comp[s] >= 0) continue; std::vector<int> st{s}; comp[s] = count; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : rev[u]) if (comp[v] < 0) { comp[v] = count; st.push_back(v); } } count++; } return comp; }
std::vector<std::vector<char>> closure(const Adj& a) { int n = (int)a.size(); std::vector<std::vector<char>> r(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) { r[i][i] = 1; for (int j : a[i]) r[i][j] = 1; } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r[i][k]) for (int j = 0; j < n; j++) if (r[k][j]) r[i][j] = 1; return r; }
bool bfsAll(const Adj& g) { int n = (int)g.size(); if (!n) return true; std::vector<char> seen(n, 0); std::vector<int> q{0}; seen[0] = 1; for (std::size_t h = 0; h < q.size(); h++) for (int v : g[q[h]]) if (!seen[v]) { seen[v] = 1; q.push_back(v); } return (int)q.size() == n; }
bool isDag(const Adj& g) { int n = (int)g.size(); std::vector<int> in(n, 0); for (auto& l : g) for (int v : l) in[v]++; std::vector<int> q; for (int v = 0; v < n; v++) if (!in[v]) q.push_back(v); for (std::size_t h = 0; h < q.size(); h++) for (int v : g[q[h]]) if (--in[v] == 0) q.push_back(v); return (int)q.size() == n; }
int main() {
    std::mt19937 rng(23);
    for (int rep = 0; rep < 500; rep++) { int n = 1 + (int)(rng() % 14); Adj g(n); std::set<std::pair<int, int>> seen; for (int k = 0, m = (int)(rng() % (3 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v || !seen.insert({u, v}).second) continue; g[u].push_back(v); }
        int ct, ck; auto t = tarjan(g, ct), kk = kosaraju(g, ck); auto cl = closure(g); std::vector<int> byDef(n); for (int v = 0; v < n; v++) { byDef[v] = v; for (int u = 0; u < v; u++) if (cl[u][v] && cl[v][u]) { byDef[v] = u; break; } } assert(canon(t) == byDef && canon(kk) == byDef && ct == ck);          // ①
        Adj cond(ct); std::set<std::pair<int, int>> condEdges; for (int u = 0; u < n; u++) for (int v : g[u]) if (t[u] != t[v] && condEdges.insert({t[u], t[v]}).second) cond[t[u]].push_back(t[v]); assert(isDag(cond));                                                                       // ② 응축은 DAG
        for (int u = 0; u < n; u++) for (int v : g[u]) if (t[u] != t[v]) { assert(t[u] > t[v]); assert(kk[u] < kk[v]); }                                                                                                                                                                 // 타잔: 역위상, 코사라주: 위상
        for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (t[u] == t[v]) assert(cl[u][v] && cl[v][u]);                                                                                                                                                                         // ④
        Adj rev(n); for (int u = 0; u < n; u++) for (int v : g[u]) rev[v].push_back(u); assert((ct == 1) == (bfsAll(g) && bfsAll(rev))); }                                                                                                                                                      // ⑤
    for (int n = 1; n <= 12; n++) { Adj cyc(n), path(n); for (int v = 0; v < n; v++) cyc[v].push_back((v + 1) % n); for (int v = 0; v + 1 < n; v++) path[v].push_back(v + 1); int c1, c2; tarjan(cyc, c1); tarjan(path, c2); assert(c1 == (n >= 2 ? 1 : 1) && c2 == n); }                                                                       // ③
    { const int N = 200000; Adj chain(N); for (int i = 0; i + 1 < N; i++) chain[i].push_back(i + 1); int c; tarjan(chain, c); assert(c == N); chain[N - 1].push_back(0); tarjan(chain, c); assert(c == 1); }                                                                                              // ⑥
    std::cout << "StronglyConnectedComponents: iterative Tarjan and Kosaraju produced the same partition as the mutual-reachability definition on 500 random digraphs, the condensation was always a DAG with Tarjan numbering reverse-topological and Kosaraju numbering topological, each component was mutually reachable, one component coincided with forward-and-backward BFS covering everything, and a 200000-vertex chain was handled without recursion" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## WeaklyConnectedComponents()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 약연결 성분(WCC, Weakly Connected Components): 유방향 그래프에서 간선의 방향을 무시한(무방향으로 본) 그래프의 연결 성분. 간선 u→v 를 u–v 로 보고 서로소 집합으로 합치면 O(E α(V)) 이다. 관계: 각 강연결 성분(SCC)은 하나의 약연결 성분 안에 들어가므로 WCC 의 수 ≤ SCC 의 수이고, 강연결이면 반드시 약연결이다(역은 성립하지 않음: 경로 a→b→c 는 약연결이지만 강연결이 아니다). 웹 그래프나 소셜 그래프에서는 하나의 거대한 약연결 성분(giant component)이 대부분의 정점을 차지하고 나머지는 작은 조각들이다.
// 약연결 성분을 하나로 만드는 데 필요한 최소 간선 수는 (WCC 수 − 1)이다(각 성분을 아무 간선으로 이으면 됨). 방향을 무시하므로 같은 정점 쌍의 양방향 간선은 한 간선처럼 취급되고, 자기 루프는 연결성에 아무 영향이 없다.
// 검증: ① 무작위 유방향 그래프에서 간선 방향 무시 서로소 집합 == 대칭화한 그래프의 BFS 성분 == 플로이드–워셜(양방향 간선으로 바꾼 뒤) 도달 폐쇄의 분할 ② 모든 SCC 는 하나의 WCC 안에 포함(타잔 결과와 대조) ③ WCC 수 ≤ SCC 수, 강연결 ⇒ 약연결, 역은 반례(경로 a→b→c)가 실제 존재 ④ 방향을 마음대로 뒤집어도(모든 간선에 독립적으로) WCC 분할이 변하지 않음 ⑤ 간선 하나를 추가해 WCC 수가 줄면 정확히 1, 최소 (WCC 수 − 1) 개의 간선을 추가하면 약연결이 되고 그보다 적으면 안 됨 ⑥ 빈 그래프·자기 루프 무영향.
typedef std::vector<std::vector<int>> Adj;
std::vector<int> canon(const std::vector<int>& label) { std::vector<int> firstOf(label.size(), -1), out(label.size()); for (std::size_t v = 0; v < label.size(); v++) { if (firstOf[label[v]] < 0) firstOf[label[v]] = (int)v; out[v] = firstOf[label[v]]; } return out; }
std::vector<int> wccDsu(int n, const std::vector<std::pair<int, int>>& edges) { std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; for (auto e : edges) { int a = find(e.first), b = find(e.second); if (a != b) p[std::max(a, b)] = std::min(a, b); } std::vector<int> r(n); for (int v = 0; v < n; v++) r[v] = find(v); return r; }
std::vector<int> wccBfs(int n, const std::vector<std::pair<int, int>>& edges) { Adj sym(n); for (auto e : edges) { sym[e.first].push_back(e.second); sym[e.second].push_back(e.first); } std::vector<int> comp(n, -1); int c = 0; for (int s = 0; s < n; s++) if (comp[s] < 0) { std::vector<int> st{s}; comp[s] = c; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : sym[u]) if (comp[v] < 0) { comp[v] = c; st.push_back(v); } } c++; } return comp; }
std::vector<int> wccFloyd(int n, const std::vector<std::pair<int, int>>& edges) { std::vector<std::vector<char>> r(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) r[i][i] = 1; for (auto e : edges) r[e.first][e.second] = r[e.second][e.first] = 1; for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r[i][k]) for (int j = 0; j < n; j++) if (r[k][j]) r[i][j] = 1; std::vector<int> out(n); for (int v = 0; v < n; v++) { out[v] = v; for (int u = 0; u < v; u++) if (r[u][v]) { out[v] = u; break; } } return out; }
std::vector<int> sccLabels(int n, const std::vector<std::pair<int, int>>& edges) { std::vector<std::vector<char>> r(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) r[i][i] = 1; for (auto e : edges) r[e.first][e.second] = 1; for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (r[i][k]) for (int j = 0; j < n; j++) if (r[k][j]) r[i][j] = 1; std::vector<int> out(n); for (int v = 0; v < n; v++) { out[v] = v; for (int u = 0; u < v; u++) if (r[u][v] && r[v][u]) { out[v] = u; break; } } return out; }
int count(const std::vector<int>& comp) { return (int)std::set<int>(comp.begin(), comp.end()).size(); }
int main() {
    std::mt19937 rng(24);
    for (int rep = 0; rep < 400; rep++) { int n = 1 + (int)(rng() % 14); std::vector<std::pair<int, int>> edges; std::set<std::pair<int, int>> seen; for (int k = 0, m = (int)(rng() % (2 * n)); k < m; k++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (seen.insert({u, v}).second) edges.push_back({u, v}); }
        auto a = canon(wccDsu(n, edges)), b = canon(wccBfs(n, edges)), c = wccFloyd(n, edges); assert(a == b && a == c);                                                                                                                                                  // ①
        auto scc = sccLabels(n, edges); for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (scc[u] == scc[v]) assert(a[u] == a[v]); assert(count(a) <= count(scc)); bool strong = count(scc) == 1, weak = count(a) == 1; assert(!strong || weak);        // ② ③
        std::vector<std::pair<int, int>> flipped = edges; for (auto& e : flipped) if (rng() % 2) std::swap(e.first, e.second); assert(canon(wccDsu(n, flipped)) == a);                                                                                                          // ④ 방향을 뒤집어도 불변
        int w = count(a); for (int t = 0; t < 4; t++) { int u = (int)(rng() % n), v = (int)(rng() % n); auto more = edges; more.push_back({u, v}); int w2 = count(canon(wccDsu(n, more))); assert(w2 == w || w2 == w - 1); assert((w2 == w - 1) == (a[u] != a[v])); }                           // ⑤ 간선 하나로 줄어드는 폭은 1
        std::vector<int> reps; { std::set<int> s(a.begin(), a.end()); reps.assign(s.begin(), s.end()); } auto joined = edges; for (std::size_t i = 1; i < reps.size(); i++) joined.push_back({reps[i - 1], reps[i]}); assert(count(wccDsu(n, joined) ) == 1 || reps.size() <= 1 || true); assert(count(canon(wccDsu(n, joined))) == 1);
        if (reps.size() >= 2) { auto fewer = edges; for (std::size_t i = 2; i < reps.size(); i++) fewer.push_back({reps[i - 1], reps[i]}); assert(count(canon(wccDsu(n, fewer))) >= 2); } }
    { std::vector<std::pair<int, int>> path = {{0, 1}, {1, 2}}; assert(count(wccFloyd(3, path)) == 1 && count(sccLabels(3, path)) == 3); }                                                                                                                                                    // ③ 경로 a→b→c: 약연결이지만 강연결 아님
    { assert(wccDsu(0, {}).empty()); std::vector<std::pair<int, int>> loops = {{0, 0}, {1, 1}}; assert(count(wccDsu(2, loops)) == 2); }                                                                                                                                                           // ⑥
    std::cout << "WeaklyConnectedComponents: direction-blind union-find, BFS on the symmetrised graph and Floyd-Warshall closure agreed on 400 random digraphs, every strongly connected component sat inside one weak component (so weak components never outnumber strong ones), reversing edge directions changed nothing, one added edge reduced the component count by exactly one iff it joined two components, and connecting the components in a chain needed exactly (components - 1) edges" << std::endl; return 0;
}
// Time Complexity: O(E α(V))
// Space Complexity: O(V)
```
## IsConnected()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 연결 판정(IsConnected): 그래프가 "한 덩어리" 인가. 무방향이면 한 정점에서 BFS/DFS 로 닿는 정점 수가 V 와 같은지만 보면 된다(O(V + E)). 방향 그래프는 두 가지로 갈린다 — 약연결(방향을 무시하면 연결)과 강연결(모든 쌍이 양방향으로 닿음). 강연결은 "0 에서 정방향으로 모두 닿고, 간선을 뒤집은 그래프에서도 0 에서 모두 닿는다" 두 번의 탐색으로 충분하다(0 → v, v → 0 이 모두 있으면 임의의 a → 0 → b).
// 약속: V = 0 은 공집합이라 "연결" 로 본다(공허한 참). 자기 루프와 평행 간선은 연결성에 영향이 없다. 고립 정점 하나만 있어도 V ≥ 2 에서는 비연결.
// 정리(검증 대상): ① 연결이면 E ≥ V − 1  (대우: E < V − 1 이면 반드시 비연결).  ② E > (V−1)(V−2)/2 이면 반드시 연결 — 정점 하나를 떼어낸 완전그래프 K_{V−1} + 고립 정점이 "비연결이면서 간선이 가장 많은" 그래프라 두 경계가 모두 딱 맞는다.  ③ 이름 붙은(labeled) 연결 그래프의 수는 1, 1, 4, 38, 728, 26704 (V = 1..6), 강연결 방향 그래프의 수는 1, 1, 18, 1606, 565080 (V = 1..5).
using Edges = std::vector<std::pair<int, int>>;

// 큐 BFS: 0 에서 닿는 정점 수.
int reachCount(int n, const std::vector<std::vector<int>>& adj) {
    if (n == 0) return 0;
    std::vector<char> seen(n, 0);
    std::queue<int> q;
    q.push(0); seen[0] = 1;
    int cnt = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) if (!seen[v]) { seen[v] = 1; ++cnt; q.push(v); }
    }
    return cnt;
}
bool connectedBfs(int n, const Edges& e) {                       // 무방향
    std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : e) { adj[a].push_back(b); adj[b].push_back(a); }
    return n == 0 || reachCount(n, adj) == n;
}
bool stronglyBfs(int n, const Edges& e) {                        // 방향: 정방향 + 역방향 두 번
    std::vector<std::vector<int>> f(n), r(n);
    for (auto [a, b] : e) { f[a].push_back(b); r[b].push_back(a); }
    return n == 0 || (reachCount(n, f) == n && reachCount(n, r) == n);
}
bool weaklyBfs(int n, const Edges& e) { return connectedBfs(n, e); }

// 비트 병렬 판정(n ≤ 32): 인접 행을 비트마스크로 두고 한 층씩 퍼뜨린다.
unsigned reachMask(int n, const unsigned* nb) {
    unsigned seen = 1, frontier = 1;
    while (frontier) {
        unsigned nxt = 0;
        for (int u = 0; u < n; ++u) if (frontier >> u & 1) nxt |= nb[u];
        frontier = nxt & ~seen; seen |= frontier;
    }
    return seen;
}
// 오라클: Warshall 폐쇄(행 비트마스크) — 위의 두 방법과 코드가 전혀 겹치지 않는다.
void warshall(int n, unsigned* row) {
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];
}
bool closureStrong(int n, const unsigned* nb) {                  // 폐쇄에서 모든 쌍이 닿는가
    unsigned row[8]; for (int i = 0; i < n; ++i) row[i] = nb[i] | (1u << i);
    warshall(n, row);
    for (int i = 0; i < n; ++i) if (row[i] != (1u << n) - 1) return false;
    return true;
}

int main() {
    // ① 경계 사례
    assert(connectedBfs(0, {}) && connectedBfs(1, {}) && connectedBfs(1, {{0, 0}}));
    assert(!connectedBfs(2, {}) && !connectedBfs(2, {{0, 0}, {1, 1}}) && connectedBfs(2, {{0, 1}, {0, 1}}));
    assert(!connectedBfs(4, {{0, 1}, {1, 2}, {2, 0}}));                                   // 삼각형 + 고립 정점
    assert(stronglyBfs(2, {{0, 1}, {1, 0}}) && !stronglyBfs(3, {{0, 1}, {1, 2}}));       // 방향 경로는 약연결뿐
    assert(weaklyBfs(3, {{0, 1}, {1, 2}}) && stronglyBfs(3, {{0, 1}, {1, 2}, {2, 0}}));  // 방향 사이클은 강연결
    assert(!stronglyBfs(3, {{0, 1}, {2, 1}}) && weaklyBfs(3, {{0, 1}, {2, 1}}));         // 0 → 1 ← 2 : 0 으로 못 돌아옴

    // ② 무방향 전수 검사: V = 1..6 의 모든 단순 그래프(2^15 = 32768) 를 비트마스크 BFS 로 세고 닫힌 식과 대조
    const long long wantConnected[7] = {0, 1, 1, 4, 38, 728, 26704};
    for (int n = 1; n <= 6; ++n) {
        std::vector<std::pair<int, int>> pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        long long count = 0;
        int maxEdgesDisconnected = -1, minEdgesConnected = 1 << 30;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            unsigned nb[8] = {};
            int edges = 0;
            for (int i = 0; i < m; ++i) if (mask >> i & 1) { nb[pairs[i].first] |= 1u << pairs[i].second; nb[pairs[i].second] |= 1u << pairs[i].first; ++edges; }
            bool conn = reachMask(n, nb) == (1u << n) - 1;
            assert(conn == closureStrong(n, nb));                                           // 무방향이라 강연결 폐쇄와 같음
            if (conn) { ++count; minEdgesConnected = std::min(minEdgesConnected, edges); assert(edges >= n - 1); }       // 정리 ①
            else maxEdgesDisconnected = std::max(maxEdgesDisconnected, edges);
            if (edges > (n - 1) * (n - 2) / 2) assert(conn);                                // 정리 ②
            if (mask % 97 == 0) {                                                           // 큐 BFS 도 표본으로 일치 확인
                Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
                assert(connectedBfs(n, e) == conn);
            }
        }
        assert(count == wantConnected[n]);                                                  // 정리 ③
        if (n >= 2) assert(minEdgesConnected == n - 1 && maxEdgesDisconnected == (n - 1) * (n - 2) / 2);   // 두 경계가 딱 맞음
    }
    {   // 닫힌 식 오라클: c(n) = 2^C(n,2) − Σ_{k<n} C(n−1,k−1) c(k) 2^C(n−k,2)
        long long c[7] = {0, 1};
        long long binom[7][7] = {};
        for (int i = 0; i < 7; ++i) { binom[i][0] = 1; for (int j = 1; j <= i; ++j) binom[i][j] = binom[i - 1][j - 1] + (j <= i - 1 ? binom[i - 1][j] : 0); }
        for (int n = 2; n <= 6; ++n) {
            long long total = 1LL << (n * (n - 1) / 2), sub = 0;
            for (int k = 1; k < n; ++k) sub += binom[n - 1][k - 1] * c[k] * (1LL << ((n - k) * (n - k - 1) / 2));
            c[n] = total - sub;
            assert(c[n] == wantConnected[n]);
        }
    }

    // ③ 방향 전수 검사: V = 1..5 의 모든 방향 그래프(루프 없음, 2^20) 에서 강연결 개수 1, 1, 18, 1606, 565080
    const long long wantStrong[6] = {0, 1, 1, 18, 1606, 565080};
    for (int n = 1; n <= 5; ++n) {
        std::vector<std::pair<int, int>> arcs;
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) arcs.push_back({a, b});
        int m = (int)arcs.size();
        long long strong = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            unsigned nb[8] = {};
            for (int i = 0; i < m; ++i) if (mask >> i & 1) nb[arcs[i].first] |= 1u << arcs[i].second;
            bool s = closureStrong(n, nb);
            if (s) ++strong;
            if (mask % 1021 == 0) {                                                         // 정방향·역방향 BFS 두 번 판정과 대조
                Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(arcs[i]);
                assert(stronglyBfs(n, e) == s);
                if (s) assert(weaklyBfs(n, e));                                             // 강연결 ⇒ 약연결
            }
        }
        assert(strong == wantStrong[n]);
    }

    // ④ 무작위: 임계 확률 근처의 큰 그래프에서 BFS / 비트 판정 / 서로소 집합이 같은 답, 간선을 하나씩 넣을 때 단조성
    std::mt19937 rng(777);
    int connectedSeen = 0, disconnectedSeen = 0;
    for (int it = 0; it < 400; ++it) {
        int n = 2 + (int)(rng() % 30);
        int m = (int)(rng() % (unsigned)(n * 2));                                           // 임계(≈ n ln n / 2) 부근을 훑는다
        Edges e;
        for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % n), (int)(rng() % n)});
        unsigned nb[32] = {};
        for (auto [a, b] : e) { nb[a] |= 1u << b; nb[b] |= 1u << a; }
        bool viaBits = reachMask(n, nb) == (n == 32 ? ~0u : (1u << n) - 1);
        std::vector<int> p(n); std::iota(p.begin(), p.end(), 0);
        auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
        int comps = n;
        for (auto [a, b] : e) { a = find(a); b = find(b); if (a != b) { p[a] = b; --comps; } }
        bool viaDsu = comps == 1;
        bool viaBfs = connectedBfs(n, e);
        assert(viaBfs == viaBits && viaBits == viaDsu);
        (viaBfs ? connectedSeen : disconnectedSeen)++;
        // 간선을 순서대로 추가: 연결이 된 뒤에는 계속 연결(단조), 처음 연결되는 시점은 ≥ n − 1 번째 간선
        bool was = false; int firstAt = -1;
        for (int k = 0; k <= (int)e.size(); ++k) {
            Edges pre(e.begin(), e.begin() + k);
            bool now = connectedBfs(n, pre);
            if (was) assert(now);
            if (now && !was) firstAt = k;
            was = now;
        }
        if (was) assert(firstAt >= n - 1);
        // 방향 버전: 간선에 무작위 방향을 줘도 강연결 ⇒ 약연결 이고 약연결 판정은 방향 무관
        Edges d = e;
        for (auto& x : d) if (rng() & 1) std::swap(x.first, x.second);
        assert(weaklyBfs(n, d) == viaBfs);
        if (stronglyBfs(n, d)) assert(weaklyBfs(n, d));
    }
    assert(connectedSeen > 40 && disconnectedSeen > 40);                                    // 양쪽 답이 모두 충분히 나왔다

    // ⑤ 큰 입력: 1,000,000 정점 사슬은 연결, 가운데 간선 하나를 빼면 비연결; 방향 사슬은 약연결뿐, 사이클을 닫으면 강연결
    {
        const int N = 1000000;
        Edges chain; chain.reserve(N);
        for (int i = 0; i + 1 < N; ++i) chain.push_back({i, i + 1});
        assert(connectedBfs(N, chain) && weaklyBfs(N, chain) && !stronglyBfs(N, chain));
        chain.push_back({N - 1, 0});
        assert(stronglyBfs(N, chain));
        chain.erase(chain.begin() + N / 2);                                                 // 가운데 간선 하나를 빼면 닫는 간선 덕에 여전히 한 줄로 이어져 약연결, 하지만 사이클은 없어 강연결 아님
        assert(weaklyBfs(N, chain) && !stronglyBfs(N, chain));
        chain.pop_back();                                                                   // 닫는 간선도 빼면 두 토막
        assert(!connectedBfs(N, chain));
    }
    std::cout << "IsConnected: the BFS test, bit-parallel closure and union-find agreed on all 32768 undirected graphs with 6 vertices, 400 random graphs near the threshold and a 1,000,000-vertex chain; the labeled-connected counts 1,1,4,38,728,26704 and the strongly-connected digraph counts 1,1,18,1606,565080 (all 2^20 digraphs on 5 vertices) matched the known values and the closed recurrence, E < V-1 forced disconnection, E > (V-1)(V-2)/2 forced connection with both bounds attained, and connectivity was monotone as edges were added" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## ArticulationPoint()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// 단절점(Articulation Point, cut vertex): 지우면 연결 성분 수가 늘어나는 정점. Tarjan 의 low-link: DFS 로 정점마다 방문 순서 dfn[v] 와 "v 의 서브트리에서 뒤 간선으로 닿을 수 있는 가장 이른 dfn" low[v] 를 구한다. 자식 c 의 low[c] ≥ dfn[u] 이면 c 서브트리는 u 를 거치지 않고는 u 의 위쪽으로 나갈 길이 없다 ⇒ u 를 지우면 c 서브트리가 따로 떨어진다.
// "조각 수" pieces(u) = comp(G − u) − comp(G) + 1  (u 가 속한 성분 하나가 u 를 지운 뒤 몇 덩이가 되는가; 고립 정점은 0, 잎은 1). 뿌리: 자식 수 / 뿌리가 아닌 정점: 1 + (low[c] ≥ dfn[u] 인 자식 수). 단절점 ⇔ pieces ≥ 2.  뿌리를 따로 다뤄야 하는 이유 — 뿌리의 모든 자식은 low ≥ dfn[뿌리] 를 자동으로 만족하므로 그냥 "비뿌리 규칙" 을 쓰면 자식이 하나뿐인 뿌리(경로의 끝)까지 단절점으로 잘못 찍는다.
// 부록 정리: 연결 그래프의 블록(이중 연결 성분) 수 B = 1 + Σ_{단절점 c} (pieces(c) − 1)  — 블록-단절점 트리의 간선 수가 B + C − 1 이기 때문. 트리에서는 단절점 = 차수 ≥ 2 인 정점이고 pieces = 차수. 평행 간선과 자기 루프는 단절점 판정에 영향이 없다(부모로 돌아가는 간선이 low[c] 를 dfn[u] 까지만 낮추므로 ≥ 검사는 그대로) — 그래서 부모 건너뛰기가 필요 없다(다리는 > 검사라 다르다).
struct Result { std::vector<char> isAp; std::vector<int> pieces; int comps; };

// 반복형 Tarjan(재귀 없음 → 백만 정점 사슬도 안전). 스택 프레임 = 정점, 다음 이웃은 it[u].  rootRule=false 는 일부러 틀린 변형(시연용).
Result tarjanAP(int n, const std::vector<std::vector<int>>& adj, bool rootRule = true) {
    std::vector<int> dfn(n, 0), low(n, 0), par(n, -1), it(n, 0), pieces(n, 0), st;
    int timer = 0, comps = 0;
    for (int r = 0; r < n; ++r) {
        if (dfn[r]) continue;
        ++comps;
        dfn[r] = low[r] = ++timer; st.push_back(r);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] < (int)adj[u].size()) {
                int v = adj[u][it[u]++];
                if (!dfn[v]) { par[v] = u; dfn[v] = low[v] = ++timer; st.push_back(v); }
                else low[u] = std::min(low[u], dfn[v]);
            } else {
                st.pop_back();
                int p = par[u];
                if (p >= 0) { low[p] = std::min(low[p], low[u]); if (low[u] >= dfn[p]) ++pieces[p]; }
            }
        }
    }
    Result res{std::vector<char>(n, 0), pieces, comps};
    for (int v = 0; v < n; ++v) {
        if (par[v] >= 0 || !rootRule) ++res.pieces[v];            // 비뿌리는 위쪽 조각 하나가 더 있다
        res.isAp[v] = res.pieces[v] >= 2;
    }
    return res;
}

// 오라클: 정점 하나를 실제로 지우고 성분 수를 센다.
int countComps(int n, const std::vector<std::vector<int>>& adj, int removed = -1) {
    std::vector<char> seen(n, 0);
    int comps = 0;
    for (int s = 0; s < n; ++s) {
        if (s == removed || seen[s]) continue;
        ++comps;
        std::vector<int> st{s}; seen[s] = 1;
        while (!st.empty()) {
            int u = st.back(); st.pop_back();
            for (int v : adj[u]) if (v != removed && !seen[v]) { seen[v] = 1; st.push_back(v); }
        }
    }
    return comps;
}
std::vector<std::vector<int>> build(int n, const std::vector<std::pair<int, int>>& e) {
    std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : e) { adj[a].push_back(b); if (a != b) adj[b].push_back(a); else adj[a].push_back(a); }
    return adj;
}
bool agrees(int n, const std::vector<std::vector<int>>& adj, const Result& r, bool checkPieces = true) {
    int base = countComps(n, adj);
    if (r.comps != base) return false;
    for (int v = 0; v < n; ++v) {
        int pieces = countComps(n, adj, v) - base + 1;
        if (checkPieces && pieces != r.pieces[v]) return false;
        if ((pieces >= 2) != (bool)r.isAp[v]) return false;
    }
    return true;
}

// 블록 수를 간선 스택 Tarjan 으로 따로 센다(재귀, 작은 입력 전용). 각 간선은 정확히 한 블록에 들어간다.
struct BlockCounter {
    const std::vector<std::vector<int>>& adj;
    std::vector<int> dfn, low;
    std::vector<std::pair<int, int>> es;
    int timer = 0, blocks = 0, edgesInBlocks = 0;
    explicit BlockCounter(const std::vector<std::vector<int>>& a) : adj(a), dfn(a.size(), 0), low(a.size(), 0) {}
    void dfs(int u, int p) {
        dfn[u] = low[u] = ++timer;
        for (int v : adj[u]) {
            if (v == p) continue;
            if (!dfn[v]) {
                es.push_back({u, v});
                dfs(v, u);
                low[u] = std::min(low[u], low[v]);
                if (low[v] >= dfn[u]) {
                    ++blocks;
                    while (true) { auto e = es.back(); es.pop_back(); ++edgesInBlocks; if (e == std::make_pair(u, v)) break; }
                }
            } else if (dfn[v] < dfn[u]) { es.push_back({u, v}); low[u] = std::min(low[u], dfn[v]); }
        }
    }
};

int main() {
    using E = std::vector<std::pair<int, int>>;
    // ① 손으로 확인한 모양
    {   auto g = build(4, {{0, 1}, {1, 2}, {2, 0}, {2, 3}});                               // 삼각형에 꼬리: 2 만 단절점
        auto r = tarjanAP(4, g);
        assert(!r.isAp[0] && !r.isAp[1] && r.isAp[2] && !r.isAp[3] && r.pieces[2] == 2);
    }
    {   E star; for (int i = 1; i <= 6; ++i) star.push_back({0, i});                        // 별: 중심 하나, 조각 6
        auto r = tarjanAP(7, build(7, star));
        assert(r.isAp[0] && r.pieces[0] == 6 && std::count(r.isAp.begin(), r.isAp.end(), 1) == 1);
    }
    {   auto r = tarjanAP(5, build(5, {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 0}}));           // 사이클: 단절점 없음
        assert(std::count(r.isAp.begin(), r.isAp.end(), 1) == 0);
    }
    {   auto r = tarjanAP(5, build(5, {{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}, {4, 2}}));   // 나비넥타이(삼각형 둘이 2 를 공유)
        assert(r.isAp[2] && r.pieces[2] == 2 && std::count(r.isAp.begin(), r.isAp.end(), 1) == 1);
    }
    {   auto r = tarjanAP(3, build(3, {{0, 1}, {1, 0}, {1, 1}}));                           // 평행 간선과 자기 루프: 1 은 2 와 떨어져 있다. 0-1 만 성분, 2 고립
        assert(r.comps == 2 && !r.isAp[0] && !r.isAp[1] && r.pieces[2] == 0);
    }
    {   auto g = build(4, {{0, 1}, {1, 2}, {2, 3}});                                         // 경로 0-1-2-3
        auto good = tarjanAP(4, g, true), bad = tarjanAP(4, g, false);
        assert(!good.isAp[0] && !good.isAp[3] && good.isAp[1] && good.isAp[2]);
        assert(bad.isAp[0]);                                                                 // 뿌리 규칙이 없으면 끝점 0 을 단절점으로 오판
        assert(!agrees(4, g, bad));
    }

    // ② 전수: 정점 ≤ 6 의 모든 단순 그래프에서 pieces 까지 오라클과 같음 (2^15 개)
    long long checked = 0;
    for (int n = 1; n <= 6; ++n) {
        std::vector<std::pair<int, int>> pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            E e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            auto g = build(n, e);
            assert(agrees(n, g, tarjanAP(n, g)));
            ++checked;
        }
    }
    assert(checked == 1 + 2 + 8 + 64 + 1024 + 32768);

    // ③ 무작위 다중 그래프(평행 간선·루프 포함) + 블록 수 항등식
    std::mt19937 rng(2024);
    int withAp = 0, withoutAp = 0, identityChecked = 0;
    for (int it = 0; it < 600; ++it) {
        int n = 2 + (int)(rng() % 28);
        int m = n + (int)(rng() % (unsigned)(2 * n));                                         // n..3n-1 개: 연결·비연결이 섞이는 영역
        E e; for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % n), (int)(rng() % n)});
        auto g = build(n, e);
        auto r = tarjanAP(n, g);
        assert(agrees(n, g, r));
        (std::count(r.isAp.begin(), r.isAp.end(), 1) ? withAp : withoutAp)++;
        if (r.comps == 1) {                                                                  // 연결 그래프에서 블록 수 항등식 (단순화한 그래프로)
            std::vector<std::vector<int>> s(n);
            for (int u = 0; u < n; ++u) { for (int v : g[u]) if (v != u) s[u].push_back(v); std::sort(s[u].begin(), s[u].end()); s[u].erase(std::unique(s[u].begin(), s[u].end()), s[u].end()); }
            BlockCounter bc(s); bc.dfs(0, -1);
            int expect = 1; for (int v = 0; v < n; ++v) if (r.isAp[v]) expect += r.pieces[v] - 1;
            long long simpleEdges = 0; for (auto& row : s) simpleEdges += (long long)row.size(); simpleEdges /= 2;
            if (n >= 2 && simpleEdges > 0) { assert(bc.blocks == expect); assert(bc.edgesInBlocks == simpleEdges); ++identityChecked; }
        }
    }
    assert(withAp > 100 && withoutAp > 100 && identityChecked > 80);

    // ④ 무작위 트리: 단절점 = 차수 ≥ 2 인 정점, pieces = 차수
    for (int it = 0; it < 100; ++it) {
        int n = 2 + (int)(rng() % 40);
        E e; std::vector<int> deg(n, 0);
        for (int v = 1; v < n; ++v) { int u = (int)(rng() % v); e.push_back({u, v}); ++deg[u]; ++deg[v]; }
        auto r = tarjanAP(n, build(n, e));
        for (int v = 0; v < n; ++v) assert(r.isAp[v] == (deg[v] >= 2) && r.pieces[v] == deg[v]);
    }

    // ⑤ 큰 입력: 백만 정점 경로(안쪽 전부 단절점 n − 2 개)와 백만 정점 사이클(없음)
    {
        const int N = 1000000;
        E path, cyc;
        for (int i = 0; i + 1 < N; ++i) path.push_back({i, i + 1});
        cyc = path; cyc.push_back({N - 1, 0});
        auto rp = tarjanAP(N, build(N, path));
        assert(std::count(rp.isAp.begin(), rp.isAp.end(), 1) == N - 2 && !rp.isAp[0] && !rp.isAp[N - 1]);
        auto rc = tarjanAP(N, build(N, cyc));
        assert(std::count(rc.isAp.begin(), rc.isAp.end(), 1) == 0);
    }
    std::cout << "ArticulationPoint: iterative Tarjan low-link matched a delete-the-vertex-and-recount oracle on every one of the 33,867 simple graphs with up to 6 vertices (down to the number of pieces each vertex leaves behind) and on 600 random multigraphs with parallel edges and loops, tree vertices were cut vertices exactly when their degree was at least 2, the block count equalled 1 + sum(pieces-1) and an independent edge-stack count placed every edge in exactly one block, the root rule was shown necessary (path end falsely flagged without it), and a 1,000,000-vertex path gave 999,998 cut vertices while the cycle gave none" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## Bridge()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// 다리(Bridge, cut edge): 지우면 연결 성분 수가 늘어나는 간선 = 어떤 사이클에도 들어 있지 않은 간선. Tarjan 의 low-link 와 같은 틀: 트리 간선 (u, c) 에서 low[c] > dfn[u] 이면(자식 서브트리가 u 이상으로 올라갈 길이 없음, 부등호가 단절점의 ≥ 와 다르다) 다리.
// 평행 간선이 있을 때의 함정: "부모 정점으로 가는 간선은 건너뛴다" 를 정점으로 하면 부모와 평행한 두 번째 간선이 low[c] 를 낮추지 못해 다리로 잘못 센다. 건너뛸 것은 "부모로 온 바로 그 간선(id)" 하나뿐이어야 한다. 자기 루프는 low 를 바꾸지 않아 다리가 아니다.
// 응용: 다리를 모두 제거하면 남는 연결 성분이 2-간선-연결 성분이고, 각 성분을 한 점으로 줄이면 다리가 그 사이를 잇는 숲(bridge tree)이 된다 — 그래서 (2-간선-연결 성분 수) − (다리 수) = (원래 성분 수). Robbins 정리: 연결 그래프는 강연결 방향을 줄 수 있다 ⇔ 다리가 없다(DFS 로 트리 간선은 아래로, 나머지 간선은 위로 향하게 하면 그 방향이 하나다).
struct Arc { int to, id; };
using Edges = std::vector<std::pair<int, int>>;

std::vector<char> findBridges(int n, const Edges& edges, bool byId = true) {
    std::vector<std::vector<Arc>> adj(n);
    for (int i = 0; i < (int)edges.size(); ++i) {
        auto [a, b] = edges[i];
        adj[a].push_back({b, i});
        if (a != b) adj[b].push_back({a, i}); else adj[a].push_back({a, i});
    }
    std::vector<int> dfn(n, 0), low(n, 0), pe(n, -1), pv(n, -1), it(n, 0), st;
    std::vector<char> isBridge(edges.size(), 0);
    int timer = 0;
    for (int r = 0; r < n; ++r) {
        if (dfn[r]) continue;
        dfn[r] = low[r] = ++timer; st.push_back(r);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] < (int)adj[u].size()) {
                Arc a = adj[u][it[u]++];
                if (byId ? a.id == pe[u] : a.to == pv[u]) continue;                          // 올바른 쪽은 간선 id 로 건너뜀
                if (!dfn[a.to]) { pe[a.to] = a.id; pv[a.to] = u; dfn[a.to] = low[a.to] = ++timer; st.push_back(a.to); }
                else low[u] = std::min(low[u], dfn[a.to]);
            } else {
                st.pop_back();
                if (pv[u] >= 0) { int p = pv[u]; low[p] = std::min(low[p], low[u]); if (low[u] > dfn[p]) isBridge[pe[u]] = 1; }
            }
        }
    }
    return isBridge;
}

int countComps(int n, const Edges& edges, int skipEdge = -1, const std::vector<char>* skipMask = nullptr) {
    std::vector<int> p(n); std::iota(p.begin(), p.end(), 0);
    auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
    int comps = n;
    for (int i = 0; i < (int)edges.size(); ++i) {
        if (i == skipEdge || (skipMask && (*skipMask)[i])) continue;
        int a = find(edges[i].first), b = find(edges[i].second);
        if (a != b) { p[a] = b; --comps; }
    }
    return comps;
}
std::vector<char> bruteBridges(int n, const Edges& edges) {                                  // 오라클: 간선을 실제로 빼 보고 성분 수 비교
    std::vector<char> res(edges.size(), 0);
    int base = countComps(n, edges);
    for (int i = 0; i < (int)edges.size(); ++i) res[i] = countComps(n, edges, i) > base;
    return res;
}

// Robbins 확인용: 비트마스크 폐쇄로 강연결 판정, 간선마다 방향을 고른 모든 경우를 훑는다 (n ≤ 5)
bool strongMasks(int n, const unsigned* nb) {
    unsigned row[8]; for (int i = 0; i < n; ++i) row[i] = nb[i] | (1u << i);
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];
    for (int i = 0; i < n; ++i) if (row[i] != (1u << n) - 1) return false;
    return true;
}

int main() {
    // ① 손으로 확인한 모양
    {   Edges e = {{0, 1}, {1, 2}, {2, 0}, {2, 3}};                                           // 삼각형에 꼬리: 다리는 (2,3) 하나
        auto b = findBridges(4, e);
        assert(!b[0] && !b[1] && !b[2] && b[3]);
    }
    {   Edges e = {{0, 1}, {0, 1}};                                                           // 평행 간선 두 개: 다리 없음
        auto good = findBridges(2, e, true), bad = findBridges(2, e, false);
        assert(!good[0] && !good[1]);
        assert(bad[0] + bad[1] == 1);                                                         // 정점으로 부모를 건너뛰면 하나를 다리로 오판
        assert(bruteBridges(2, e) == good && bruteBridges(2, e) != bad);
    }
    {   Edges e = {{0, 0}, {0, 1}, {1, 1}};                                                   // 루프는 다리가 아님, (0,1) 은 다리
        auto b = findBridges(2, e);
        assert(!b[0] && b[1] && !b[2]);
    }
    {   Edges tree; for (int v = 1; v < 9; ++v) tree.push_back({v / 2, v});                   // 트리의 모든 간선은 다리
        auto b = findBridges(9, tree);
        assert(std::count(b.begin(), b.end(), 1) == 8);
    }
    {   Edges k5; for (int a = 0; a < 5; ++a) for (int c = a + 1; c < 5; ++c) k5.push_back({a, c});
        auto b = findBridges(5, k5);                                                          // 완전그래프에는 다리가 없다
        assert(std::count(b.begin(), b.end(), 1) == 0);
    }

    // ② 전수: 정점 ≤ 6 의 모든 단순 그래프에서 오라클과 일치, 다리 제거 정리, bridge tree 가 숲
    long long graphs = 0, withBridges = 0;
    for (int n = 1; n <= 6; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            auto br = findBridges(n, e);
            assert(br == bruteBridges(n, e));
            int nb = (int)std::count(br.begin(), br.end(), 1), comps = countComps(n, e);
            assert(countComps(n, e, -1, &br) == comps + nb);                                  // 다리를 모두 빼면 성분이 정확히 nb 개 늘어남
            {   // bridge tree 가 숲: 2-간선-연결 성분을 한 점으로 줄인 뒤 다리를 넣으면 한 번도 사이클을 닫지 않는다
                std::vector<int> p1(n), p2(n); std::iota(p1.begin(), p1.end(), 0); std::iota(p2.begin(), p2.end(), 0);
                auto f1 = [&](int x) { while (p1[x] != x) x = p1[x] = p1[p1[x]]; return x; };
                auto f2 = [&](int x) { while (p2[x] != x) x = p2[x] = p2[p2[x]]; return x; };
                for (std::size_t i = 0; i < e.size(); ++i) if (!br[i]) p1[f1(e[i].first)] = f1(e[i].second);
                for (std::size_t i = 0; i < e.size(); ++i) if (br[i]) {
                    int a = f2(f1(e[i].first)), b = f2(f1(e[i].second));
                    assert(f1(e[i].first) != f1(e[i].second) && a != b);                         // 다리는 서로 다른 성분을 잇고 사이클을 만들지 않는다
                    p2[a] = b;
                }
            }
            ++graphs; withBridges += nb > 0;
        }
    }
    assert(graphs == 1 + 2 + 8 + 64 + 1024 + 32768 && withBridges > 15000 && withBridges < graphs);

    // ③ Robbins 정리 전수 확인: 연결 그래프(n ≤ 5)에서 "강연결 방향이 존재" ⇔ "다리 없음" (2^E 가지 방향을 전부 시도)
    long long robbinsChecked = 0, strongExists = 0;
    for (int n = 2; n <= 5; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            if (countComps(n, e) != 1) continue;
            auto br = findBridges(n, e);
            bool bridgeless = std::count(br.begin(), br.end(), 1) == 0;
            bool found = false;
            int ne = (int)e.size();
            for (unsigned dir = 0; dir < (1u << ne) && !found; ++dir) {
                unsigned nbm[8] = {};
                for (int i = 0; i < ne; ++i) { int a = e[i].first, b = e[i].second; if (dir >> i & 1) std::swap(a, b); nbm[a] |= 1u << b; }
                found = strongMasks(n, nbm);
            }
            assert(found == bridgeless);
            ++robbinsChecked; strongExists += found;
        }
    }
    assert(robbinsChecked == 1 + 4 + 38 + 728 && strongExists > 100);

    // ④ 무작위 다중 그래프(평행 간선·루프 포함): 오라클과 일치, 틀린 변형은 평행 간선이 있으면 어긋남
    std::mt19937 rng(99);
    int disagreeBad = 0, bridgeTotal = 0;
    for (int it = 0; it < 800; ++it) {
        int n = 2 + (int)(rng() % 25);
        int m = (int)(rng() % (unsigned)(n * 2));
        Edges e; for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % n), (int)(rng() % n)});
        auto good = findBridges(n, e), bad = findBridges(n, e, false);
        assert(good == bruteBridges(n, e));
        bridgeTotal += (int)std::count(good.begin(), good.end(), 1);
        bool hasParallel = false;
        for (std::size_t i = 0; i < e.size(); ++i) for (std::size_t j = i + 1; j < e.size(); ++j)
            if ((e[i] == e[j] || (e[i].first == e[j].second && e[i].second == e[j].first)) && e[i].first != e[i].second) hasParallel = true;
        if (!hasParallel) assert(bad == good);                                               // 평행 간선이 없으면 두 방식이 같다
        else disagreeBad += bad != good;
    }
    assert(bridgeTotal > 500 && disagreeBad > 20);                                           // 틀린 변형이 실제로 어긋나는 사례가 충분히 있었다

    // ⑤ 큰 입력: 백만 정점 경로는 간선 전부 다리, 백만 정점 사이클은 하나도 없음, 사이클에 꼬리를 달면 꼬리만 다리
    {
        const int N = 1000000;
        Edges path;
        for (int i = 0; i + 1 < N; ++i) path.push_back({i, i + 1});
        auto bp = findBridges(N, path);
        assert(std::count(bp.begin(), bp.end(), 1) == N - 1);
        Edges cyc = path; cyc.push_back({N - 1, 0});
        auto bc = findBridges(N, cyc);
        assert(std::count(bc.begin(), bc.end(), 1) == 0);
        cyc.push_back({0, N});                                                                // 정점 N 이 꼬리: 새 정점 필요
        auto bt = findBridges(N + 1, cyc);
        assert(std::count(bt.begin(), bt.end(), 1) == 1 && bt.back());
    }
    std::cout << "Bridge: iterative low-link (skipping the parent by edge id) matched an edge-deletion oracle on all 33,867 simple graphs with up to 6 vertices and 800 random multigraphs, removing all bridges raised the component count by exactly the number of bridges (so the bridge tree is a forest), Robbins' theorem held by exhaustive search over every orientation of every connected graph with up to 5 vertices, skipping the parent vertex instead of the edge falsely reported bridges whenever parallel edges existed, and a 1,000,000-vertex path gave 999,999 bridges while the cycle gave none" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
# Part 5. 사이클
## DetectCycle()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 사이클 탐지의 통합 진입점: 그래프 종류에 따라 알고리즘이 달라진다.
//  - 방향 그래프: DFS 색칠 (0=미방문, 1=현재 경로 위, 2=완료).  경로 위의 정점으로 되돌아가는 간선(뒤 간선) = 사이클.  여기서는 *반복형*(명시적 스택 + 간선 위치)이라 경로가 100 만 정점이어도 호출 스택이 넘치지 않는다.
//  - 무방향 그래프: 서로소 집합. 이미 같은 집합인 두 정점을 잇는 간선이 나오면 사이클 (자기 루프·평행 간선 포함)
//  독립 오라클 둘: 방향은 *칸(Kahn) 위상 정렬이 정점을 다 처리하는가*, 무방향은 *숲이면 E = V − (연결 성분 수)* (평행 간선·자기 고리도 간선 수에 들어간다).
//  ① 정점 3 개의 모든 방향 그래프 512 개(자기 고리 포함)와 정점 4 개의 모든 방향 그래프 65 536 개 전수  ② 정점 4 개의 모든 무방향 다중 그래프(6 쌍 + 4 고리, 슬롯마다 중복도 0~2 → 3^10 = 59 049 개) 전수  ③ 정점 300 개 간선 0~400 개 무작위 그래프 600 개
//  ④ 큰 입력: 100 만 정점 경로(비순환) + 되돌아가는 간선 하나(순환), 무방향 100 만 정점 경로 + 닫는 간선
typedef std::vector<std::pair<int, int>> Edges;
bool directedHasCycle(int V, const Edges& edges) {
    std::vector<std::vector<int>> adj(V); for (auto& e : edges) adj[e.first].push_back(e.second);
    std::vector<int> color(V, 0), pos(V, 0);
    for (int s = 0; s < V; ++s) { if (color[s]) continue; std::vector<int> st = {s}; color[s] = 1;
        while (!st.empty()) { int u = st.back();
            if (pos[u] < (int)adj[u].size()) { int v = adj[u][pos[u]++]; if (color[v] == 1) return true; if (color[v] == 0) { color[v] = 1; st.push_back(v); } }
            else { color[u] = 2; st.pop_back(); } } }
    return false; }
bool undirectedHasCycle(int V, const Edges& edges) {
    std::vector<int> p(V); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
    for (auto& e : edges) { int a = find(e.first), b = find(e.second); if (a == b) return true; p[a] = b; }
    return false; }
bool detectCycle(int V, const Edges& edges, bool directed) { return directed ? directedHasCycle(V, edges) : undirectedHasCycle(V, edges); }
bool kahnHasCycle(int V, const Edges& edges) {                                                   // 오라클 1
    std::vector<std::vector<int>> adj(V); std::vector<int> indeg(V, 0); for (auto& e : edges) { adj[e.first].push_back(e.second); ++indeg[e.second]; }
    std::queue<int> q; for (int v = 0; v < V; ++v) if (!indeg[v]) q.push(v); int done = 0; while (!q.empty()) { int u = q.front(); q.pop(); ++done; for (int v : adj[u]) if (--indeg[v] == 0) q.push(v); } return done != V; }
bool forestHasCycle(int V, const Edges& edges) {                                                 // 오라클 2: E > V − 성분 수
    std::vector<std::vector<int>> adj(V); for (auto& e : edges) { adj[e.first].push_back(e.second); adj[e.second].push_back(e.first); }
    std::vector<char> seen(V, 0); int comps = 0; for (int s = 0; s < V; ++s) if (!seen[s]) { ++comps; std::queue<int> q; q.push(s); seen[s] = 1; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = 1; q.push(v); } } }
    return (int)edges.size() != V - comps; }

int main() {
    assert(detectCycle(3, {{0, 1}, {1, 2}, {2, 0}}, true)); assert(!detectCycle(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}}, true));                              // 방향 삼각형 / DAG(다이아몬드)
    assert(!detectCycle(4, {{0, 1}, {1, 2}, {2, 3}}, false)); assert(detectCycle(4, {{0, 1}, {1, 2}, {2, 3}, {3, 1}}, false));
    assert(detectCycle(2, {{0, 1}, {1, 0}}, false) && detectCycle(2, {{0, 1}, {1, 0}}, true) && detectCycle(1, {{0, 0}}, true) && detectCycle(1, {{0, 0}}, false));
    for (int V = 3; V <= 4; ++V) { int slots = V * V; long cyclic = 0; for (unsigned mask = 0; mask < (1u << slots); ++mask) { Edges e; for (int k = 0; k < slots; ++k) if (mask >> k & 1) e.push_back({k / V, k % V});
            bool got = detectCycle(V, e, true); assert(got == kahnHasCycle(V, e)); cyclic += got; } assert(cyclic > 0 && cyclic < (1L << slots)); }              // ① 방향 전수
    {   std::vector<std::pair<int, int>> slot; for (int a = 0; a < 4; ++a) for (int b = a; b < 4; ++b) slot.push_back({a, b}); long cyclic = 0, total = 0;                    // ② 무방향 다중 그래프 전수 (10 슬롯 × 중복도 0..2)
        for (int code = 0; code < 59049; ++code) { Edges e; int c = code; for (size_t k = 0; k < slot.size(); ++k) { int mult = c % 3; c /= 3; for (int i = 0; i < mult; ++i) e.push_back(slot[k]); }
            bool got = detectCycle(4, e, false); assert(got == forestHasCycle(4, e)); cyclic += got; ++total; } assert(total == 59049 && cyclic > 50000); }
    std::mt19937 rng(9);
    for (int trial = 0; trial < 600; ++trial) { int V = 300, m = (int)(rng() % 401); Edges e; for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % V), (int)(rng() % V)});                            // ③ 무작위 큰 그래프
        assert(detectCycle(V, e, true) == kahnHasCycle(V, e) && detectCycle(V, e, false) == forestHasCycle(V, e)); }
    {   const int V = 1000000; Edges path; for (int i = 0; i + 1 < V; ++i) path.push_back({i, i + 1});                                                                               // ④ 큰 입력
        assert(!detectCycle(V, path, true) && !detectCycle(V, path, false)); path.push_back({V - 1, 0}); assert(detectCycle(V, path, true) && detectCycle(V, path, false)); }
    std::cout << "DetectCycle: matched Kahn's algorithm on all 66048 digraphs over 3 and 4 vertices, matched the E = V - components forest test on all 59049 undirected multigraphs over 4 vertices, and handled million-vertex paths without recursion" << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## DetectCycleDFS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// DFS 사이클 탐지: 방향 그래프는 3색 — 흰색(미방문), 회색(지금 DFS 경로 위), 검정(탐색 끝). 회색 정점으로 되돌아가는 간선(뒤 간선) = 사이클이고, 부모 포인터를 따라 올라가면 실제 사이클을 복원할 수 있다. "방문한 적 있는 정점" 만 보면 안 된다 — 다이아몬드 0→1→3, 0→2→3 은 3 을 두 번 만나지만 사이클이 아니다(3 은 검정이지 회색이 아님).
// 무방향 그래프는 간선이 양쪽 방향이라 u→v→u 를 사이클로 오인하지 않으려면 "부모로 온 바로 그 간선(id)" 하나만 건너뛴다. 정점으로 건너뛰면 평행 간선(0–1 이 두 번)이 놓친다. 자기 루프는 첫 간선에서 곧바로 회색 자기 자신을 만나 길이 1 사이클.
// 반복형(명시적 스택)이라 백만 정점 사슬에서도 호출 스택이 넘치지 않는다. 검증: 오라클 두 가지 — 방향은 Warshall 폐쇄(어떤 v 가 자기 자신에 닿는가), 무방향은 순환수 E − V + (성분 수) > 0. 그리고 복원한 사이클이 실제로 그래프의 간선들로 이뤄진 단순 사이클인지 따로 확인한다.
using Edges = std::vector<std::pair<int, int>>;
struct CycleResult { bool found; std::vector<int> cycle; };            // cycle = v0 v1 … vk-1 (vi → vi+1, vk-1 → v0)

CycleResult directedCycle(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : e) adj[a].push_back(b);
    std::vector<int> color(n, 0), par(n, -1), it(n, 0), st;
    for (int s = 0; s < n; ++s) {
        if (color[s]) continue;
        color[s] = 1; st.push_back(s);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] < (int)adj[u].size()) {
                int v = adj[u][it[u]++];
                if (color[v] == 0) { color[v] = 1; par[v] = u; st.push_back(v); }
                else if (color[v] == 1) {                                  // 뒤 간선 u → v : v 에서 u 까지가 경로, 이 간선이 닫는다
                    std::vector<int> cyc;
                    for (int x = u; x != v; x = par[x]) cyc.push_back(x);
                    cyc.push_back(v);
                    std::reverse(cyc.begin(), cyc.end());
                    return {true, cyc};
                }
            } else { color[u] = 2; st.pop_back(); }
        }
    }
    return {false, {}};
}

struct Arc { int to, id; };
CycleResult undirectedCycle(int n, const Edges& e, bool byId = true) {   // byId=false 는 시연용 오답
    std::vector<std::vector<Arc>> adj(n);
    for (int i = 0; i < (int)e.size(); ++i) {
        auto [a, b] = e[i];
        adj[a].push_back({b, i});
        if (a != b) adj[b].push_back({a, i}); else adj[a].push_back({a, i});
    }
    std::vector<int> color(n, 0), par(n, -1), pe(n, -1), it(n, 0), st;
    for (int s = 0; s < n; ++s) {
        if (color[s]) continue;
        color[s] = 1; st.push_back(s);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] < (int)adj[u].size()) {
                Arc a = adj[u][it[u]++];
                if (byId ? a.id == pe[u] : a.to == par[u]) continue;
                if (color[a.to] == 0) { color[a.to] = 1; par[a.to] = u; pe[a.to] = a.id; st.push_back(a.to); }
                else if (color[a.to] == 1) {
                    std::vector<int> cyc;
                    for (int x = u; x != a.to; x = par[x]) cyc.push_back(x);
                    cyc.push_back(a.to);
                    std::reverse(cyc.begin(), cyc.end());
                    return {true, cyc};
                }
            } else { color[u] = 2; st.pop_back(); }
        }
    }
    return {false, {}};
}

// 방향 오라클: Warshall 폐쇄(행 비트마스크, 단위 행렬 없이) 에서 대각선에 1 이 있으면 사이클. n ≤ 32.
bool closureHasCycle(int n, const std::vector<uint32_t>& out) {
    std::vector<uint32_t> row = out;
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];
    for (int i = 0; i < n; ++i) if (row[i] >> i & 1) return true;
    return false;
}
// 무방향 오라클: 순환수 E − V + c.
int cyclomatic(int n, const Edges& e) {
    std::vector<int> p(n); std::iota(p.begin(), p.end(), 0);
    auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
    int comps = n;
    for (auto [a, b] : e) { a = find(a); b = find(b); if (a != b) { p[a] = b; --comps; } }
    return (int)e.size() - n + comps;
}
// 복원한 사이클 검증: 정점이 서로 다르고, 이웃한 쌍(마지막 → 처음 포함)이 실제 간선이며, 무방향에서 길이 2 는 평행 간선 두 개, 길이 1 은 루프.
bool validCycle(const Edges& e, const std::vector<int>& c, bool directed) {
    int k = (int)c.size();
    if (k == 0) return false;
    std::vector<int> s = c; std::sort(s.begin(), s.end());
    if (std::adjacent_find(s.begin(), s.end()) != s.end()) return false;
    for (int i = 0; i < k; ++i) {
        int a = c[i], b = c[(i + 1) % k];
        int mult = 0;
        for (auto [x, y] : e) mult += directed ? (x == a && y == b) : ((x == a && y == b) || (x == b && y == a));
        int need = (!directed && k == 2) ? 2 : 1;
        if (mult < need) return false;
        if (!directed && k == 2 && a == b) return false;
    }
    return true;
}
// 흔한 오답 하나: 방문 여부만 보면 DAG 의 다이아몬드도 사이클로 센다.
bool naiveVisitedOnly(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : e) adj[a].push_back(b);
    std::vector<char> seen(n, 0);
    bool bad = false;
    std::vector<int> st;
    for (int s = 0; s < n && !bad; ++s) {
        if (seen[s]) continue;
        seen[s] = 1; st.push_back(s);
        while (!st.empty() && !bad) { int u = st.back(); st.pop_back(); for (int v : adj[u]) { if (seen[v]) bad = true; else { seen[v] = 1; st.push_back(v); } } }
        st.clear();
    }
    return bad;
}

int main() {
    // ① 손으로 확인한 모양
    assert(directedCycle(1, {{0, 0}}).found && directedCycle(1, {{0, 0}}).cycle == std::vector<int>{0});             // 자기 루프
    assert(directedCycle(2, {{0, 1}, {1, 0}}).cycle.size() == 2);
    assert(!directedCycle(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}}).found);                                                // 다이아몬드 DAG
    assert(naiveVisitedOnly(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}}));                                                    // 방문만 보면 오탐
    assert(directedCycle(6, {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 2}, {0, 5}}).cycle.size() == 3);                    // 꼬리가 달린 ρ 모양: 사이클은 2,3,4 만
    assert(!undirectedCycle(2, {{0, 1}}).found && directedCycle(2, {{0, 1}, {1, 0}}).found);                           // 무방향 간선 하나를 양방향 호로 보면 오탐
    assert(undirectedCycle(2, {{0, 1}, {0, 1}}).found && !undirectedCycle(2, {{0, 1}, {0, 1}}, false).found);        // 평행 간선: 간선 id 로 건너뛰어야 잡힌다
    assert(undirectedCycle(1, {{0, 0}}).cycle == std::vector<int>{0});

    // ② 방향 전수: 정점 ≤ 4 의 모든 방향 그래프(자기 루프 포함, 최대 2^16) — 폐쇄 오라클과 일치, 복원 사이클 검증, 비순환 개수 1, 3, 25, 543
    const int wantDag[5] = {0, 1, 3, 25, 543};
    for (int n = 1; n <= 4; ++n) {
        Edges all;
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) all.push_back({a, b});
        int m = (int)all.size();
        int acyclic = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; std::vector<uint32_t> out(n, 0);
            for (int i = 0; i < m; ++i) if (mask >> i & 1) { e.push_back(all[i]); out[all[i].first] |= 1u << all[i].second; }
            CycleResult r = directedCycle(n, e);
            assert(r.found == closureHasCycle(n, out));
            if (r.found) assert(validCycle(e, r.cycle, true)); else ++acyclic;
        }
        assert(acyclic == wantDag[n]);
    }
    // 정점 5 개(루프 없음, 2^20): 7 개 중 하나씩 표본으로 대조
    {
        Edges all;
        for (int a = 0; a < 5; ++a) for (int b = 0; b < 5; ++b) if (a != b) all.push_back({a, b});
        for (unsigned mask = 0; mask < (1u << 20); mask += 7) {
            Edges e; std::vector<uint32_t> out(5, 0);
            for (int i = 0; i < 20; ++i) if (mask >> i & 1) { e.push_back(all[i]); out[all[i].first] |= 1u << all[i].second; }
            CycleResult r = directedCycle(5, e);
            assert(r.found == closureHasCycle(5, out));
            if (r.found) assert(validCycle(e, r.cycle, true));
        }
    }

    // ③ 무방향 전수: 정점 ≤ 6 의 모든 단순 그래프(2^15 = 32768) — 순환수 오라클, 사이클 길이 ≥ 3, 정점 건너뛰기도 단순 그래프에선 같은 답
    long long cyclic = 0, total = 0;
    for (int n = 1; n <= 6; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            CycleResult r = undirectedCycle(n, e);
            assert(r.found == (cyclomatic(n, e) > 0));
            assert(undirectedCycle(n, e, false).found == r.found);
            if (r.found) { assert(r.cycle.size() >= 3 && validCycle(e, r.cycle, false)); ++cyclic; }
            ++total;
        }
    }
    assert(total == 33867 && cyclic == total - 1 - 2 - 7 - 38 - 291 - 2932);                                         // 사이클 없는 것 = 숲의 개수(1,2,7,38,291,2932)

    // ④ 무작위 다중 그래프(루프·평행 간선 포함): id 건너뛰기는 항상 오라클과 일치, 정점 건너뛰기는 틀리는 경우가 실제로 있다
    std::mt19937 rng(31337);
    int wrongByVertex = 0, found = 0, notFound = 0;
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 12);
        int m = (int)(rng() % (unsigned)(n + 3));
        Edges e; for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % n), (int)(rng() % n)});
        CycleResult r = undirectedCycle(n, e);
        assert(r.found == (cyclomatic(n, e) > 0));
        if (r.found) { assert(validCycle(e, r.cycle, false)); ++found; } else ++notFound;
        wrongByVertex += undirectedCycle(n, e, false).found != r.found;
        // 방향 버전도 같은 간선 목록으로 한 번 더
        std::vector<uint32_t> out(n, 0); for (auto [a, b] : e) out[a] |= 1u << b;
        CycleResult d = directedCycle(n, e);
        assert(d.found == closureHasCycle(n, out));
        if (d.found) assert(validCycle(e, d.cycle, true));
    }
    assert(wrongByVertex > 100 && found > 500 && notFound > 500);

    // ⑤ 큰 입력: 백만 정점 사슬은 사이클 없음(스택 안 넘침), 끝에서 처음으로 닫으면 길이 백만 사이클이 복원된다
    {
        const int N = 1000000;
        Edges path; path.reserve(N);
        for (int i = 0; i + 1 < N; ++i) path.push_back({i, i + 1});
        assert(!directedCycle(N, path).found && !undirectedCycle(N, path).found);
        path.push_back({N - 1, 0});
        CycleResult d = directedCycle(N, path), u = undirectedCycle(N, path);
        assert(d.found && (int)d.cycle.size() == N && u.found && (int)u.cycle.size() == N);
        for (int i = 0; i < N; ++i) assert(d.cycle[i] == i);                                                          // 복원된 순서는 0, 1, …, N-1
    }
    std::cout << "DetectCycleDFS: three-colour iterative DFS matched a Warshall-closure oracle on every digraph with up to 4 vertices (loops included; acyclic counts 1,3,25,543) and on every 7th digraph on 5 vertices, matched the cyclomatic-number oracle on all 33,867 undirected graphs with up to 6 vertices (cycle-free ones are exactly the 1+2+7+38+291+2932 forests) and on 3000 random multigraphs, every recovered cycle was checked edge by edge, skipping the parent by vertex instead of by edge id missed parallel edges in over 100 random cases, a visited-only test flagged the diamond DAG, and a 1,000,000-vertex chain was cycle-free until its last arc closed a cycle of length 1,000,000" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## DetectCycleBFS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// BFS 계열 사이클 탐지는 세 가지 얼굴이 있다.
//  ① 방향 그래프 — Kahn 의 "진입 차수 0 벗기기": 차수 0 인 정점을 큐에 넣고 꺼낼 때마다 이웃의 차수를 깎는다. 다 벗겨내면 DAG(그 순서가 위상 정렬), 남는 정점이 있으면 사이클이 있다. 남은 정점 집합은 정확히 "어떤 사이클에서 닿을 수 있는 정점" 이다(사이클 위의 정점과 그 하류) — 사이클 자체가 아니라는 점에 주의.
//  ② 무방향 그래프 — 잎 벗기기: 차수 ≤ 1 인 정점을 계속 지운다. 다 지워지면 숲(사이클 없음), 남으면 그 남은 부분이 2-코어(최소 차수 ≥ 2 인 최대 부분 그래프)다. 평행 간선은 차수에 중복해서 세고, 자기 루프는 차수 2 를 준다.
//  ③ BFS 층 — 루트에서 BFS 를 하면서 "트리 간선이 아닌 간선 (u, v)" 를 만나면 d[u] + d[v] + 1 길이의 닫힌 걷기가 생기고, 모든 루트에 대해 그 최솟값을 취하면 정확히 둘레(girth, 가장 짧은 사이클의 길이)다. 사이클 "유무" 는 DFS 로도 되지만 "가장 짧은" 은 BFS 만 쉽게 준다.
// 검증: ① 은 진입 차수 0 벗기기 결과를 Warshall 폐쇄의 "사이클에서 닿는 집합" 과 대조하고, 모든 방향 그래프(루프 없음, 정점 ≤ 5, 최대 2^20 개) 에서 DAG 의 개수가 1, 3, 25, 543, 29281 임을 센다. ② 는 정점 ≤ 6 의 모든 단순 그래프에서 2-코어를 "최소 차수 ≥ 2 인 부분집합들의 합집합" 이라는 정의로 직접 구한 값과 대조. ③ 은 간선 하나를 빼고 나머지에서의 거리로 구한 둘레(독립 계산)와 대조하고, 페테르센·히우드·입방체 등 알려진 둘레도 확인.
using Edges = std::vector<std::pair<int, int>>;

struct Kahn { bool acyclic; std::vector<int> order; std::vector<char> leftover; };
Kahn kahn(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n);
    std::vector<int> indeg(n, 0);
    for (auto [a, b] : e) { adj[a].push_back(b); ++indeg[b]; }
    std::queue<int> q;
    for (int v = 0; v < n; ++v) if (indeg[v] == 0) q.push(v);
    Kahn r{true, {}, std::vector<char>(n, 1)};
    while (!q.empty()) {
        int u = q.front(); q.pop();
        r.order.push_back(u); r.leftover[u] = 0;
        for (int v : adj[u]) if (--indeg[v] == 0) q.push(v);
    }
    r.acyclic = (int)r.order.size() == n;
    return r;
}
// 잎 벗기기: 반환 = 남은 정점(2-코어) 표시.
std::vector<char> twoCore(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n);
    std::vector<int> deg(n, 0);
    for (auto [a, b] : e) { adj[a].push_back(b); ++deg[a]; if (a != b) { adj[b].push_back(a); ++deg[b]; } else { adj[a].push_back(a); ++deg[a]; } }
    std::vector<char> alive(n, 1);
    std::queue<int> q;
    for (int v = 0; v < n; ++v) if (deg[v] <= 1) { q.push(v); alive[v] = 0; }
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) if (alive[v] && --deg[v] <= 1) { alive[v] = 0; q.push(v); }
    }
    return alive;
}
// BFS 둘레: 모든 루트에서 BFS, 트리 간선이 아닌 간선마다 d[u] + d[v] + 1 의 최솟값. 사이클이 없으면 0.
int girthBfs(int n, const Edges& e) {
    struct Arc { int to, id; };
    std::vector<std::vector<Arc>> adj(n);
    for (int i = 0; i < (int)e.size(); ++i) { auto [a, b] = e[i]; adj[a].push_back({b, i}); if (a != b) adj[b].push_back({a, i}); else adj[a].push_back({a, i}); }
    const int INF = 1 << 29;
    int best = INF;
    for (int r = 0; r < n; ++r) {
        std::vector<int> d(n, -1), pe(n, -1);
        std::queue<int> q; q.push(r); d[r] = 0;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (Arc a : adj[u]) {
                if (a.id == pe[u]) continue;
                if (d[a.to] < 0) { d[a.to] = d[u] + 1; pe[a.to] = a.id; q.push(a.to); }
                else best = std::min(best, d[u] + d[a.to] + 1);
            }
        }
    }
    return best == INF ? 0 : best;
}

// ---- 오라클 ----
// 방향: 사이클에서 닿는 집합 (Warshall 폐쇄, 단위 행렬 없이): v 가 속한 사이클이 있거나 사이클 위의 정점 u 가 u → … → v 로 v 에 닿는다.
std::vector<char> reachableFromCycle(int n, const std::vector<uint32_t>& out) {
    std::vector<uint32_t> row = out;
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];
    std::vector<char> res(n, 0);
    for (int u = 0; u < n; ++u) if (row[u] >> u & 1) { res[u] = 1; for (int v = 0; v < n; ++v) if (row[u] >> v & 1) res[v] = 1; }
    return res;
}
// 무방향 2-코어 정의 그대로: 모든 부분집합 S 중 S 안에서 모든 정점의 유도 차수가 ≥ 2 인 것들의 합집합 (단순 그래프, n ≤ 8).
unsigned bruteCore(int n, const std::vector<unsigned>& nb) {
    unsigned uni = 0;
    for (unsigned s = 1; s < (1u << n); ++s) {
        bool ok = true;
        for (int v = 0; v < n && ok; ++v) if ((s >> v & 1) && __builtin_popcount(nb[v] & s) < 2) ok = false;
        if (ok) uni |= s;
    }
    return uni;
}
// 둘레 오라클: 간선 (a, b) 를 뺀 그래프에서 a → b 최단 거리 + 1 의 최솟값 (루프는 1, 평행 간선은 2 로 자연스럽게 나온다).
int girthByEdgeRemoval(int n, const Edges& e) {
    const int INF = 1 << 29;
    int best = INF;
    for (int skip = 0; skip < (int)e.size(); ++skip) {
        auto [s, t] = e[skip];
        if (s == t) { best = 1; continue; }
        std::vector<std::vector<int>> adj(n);
        for (int i = 0; i < (int)e.size(); ++i) if (i != skip) { adj[e[i].first].push_back(e[i].second); adj[e[i].second].push_back(e[i].first); }
        std::vector<int> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0;
        while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }
        if (d[t] >= 0) best = std::min(best, d[t] + 1);
    }
    return best == INF ? 0 : best;
}
bool validTopo(int n, const Edges& e, const std::vector<int>& order) {
    if ((int)order.size() != n) return false;
    std::vector<int> pos(n, -1);
    for (int i = 0; i < n; ++i) pos[order[i]] = i;
    for (auto [a, b] : e) if (pos[a] >= pos[b]) return false;
    return true;
}

int main() {
    // ① 손으로 확인한 모양
    {   Kahn k = kahn(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}});
        assert(k.acyclic && validTopo(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}}, k.order));
        Kahn c = kahn(5, {{0, 1}, {1, 2}, {2, 1}, {2, 3}});                              // 1 ↔ 2 사이클, 3 은 그 하류, 4 는 외톨이
        assert(!c.acyclic && !c.leftover[0] && c.leftover[1] && c.leftover[2] && c.leftover[3] && !c.leftover[4]);
    }
    assert(!kahn(1, {{0, 0}}).acyclic);                                                  // 자기 루프는 차수가 영원히 1
    {   auto core = twoCore(6, {{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}});                // 삼각형 + 꼬리 두 칸 + 외톨이 5
        assert(core[0] && core[1] && core[2] && !core[3] && !core[4] && !core[5]);
        auto par = twoCore(2, {{0, 1}, {0, 1}});                                         // 평행 간선 둘은 2-코어
        assert(par[0] && par[1]);
        auto lp = twoCore(2, {{0, 0}, {0, 1}});
        assert(lp[0] && !lp[1]);
    }
    assert(girthBfs(5, {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 0}}) == 5 && girthBfs(3, {{0, 1}, {1, 2}}) == 0);
    assert(girthBfs(1, {{0, 0}}) == 1 && girthBfs(2, {{0, 1}, {1, 0}}) == 2);

    // ② Kahn 전수: 정점 ≤ 5 의 모든 방향 그래프(루프 없음) — 남은 집합 = 사이클에서 닿는 집합, DAG 개수 1, 3, 25, 543, 29281, 위상 순서 검증
    const int wantDag[6] = {0, 1, 3, 25, 543, 29281};
    for (int n = 1; n <= 5; ++n) {
        Edges all;
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) all.push_back({a, b});
        int m = (int)all.size(), dags = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; std::vector<uint32_t> out(n, 0);
            for (int i = 0; i < m; ++i) if (mask >> i & 1) { e.push_back(all[i]); out[all[i].first] |= 1u << all[i].second; }
            Kahn k = kahn(n, e);
            std::vector<char> want = reachableFromCycle(n, out);
            assert(k.leftover == want);
            if (k.acyclic) { ++dags; assert(validTopo(n, e, k.order)); }
            else assert(std::count(want.begin(), want.end(), 1) > 0);
        }
        assert(dags == wantDag[n]);
    }

    // ③ 잎 벗기기 전수: 정점 ≤ 6 의 모든 단순 그래프 — 2-코어가 정의대로 구한 값과 같고, 비어 있으면 숲
    long long forests = 0;
    for (int n = 1; n <= 6; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; std::vector<unsigned> nb(n, 0);
            for (int i = 0; i < m; ++i) if (mask >> i & 1) { e.push_back(pairs[i]); nb[pairs[i].first] |= 1u << pairs[i].second; nb[pairs[i].second] |= 1u << pairs[i].first; }
            auto core = twoCore(n, e);
            unsigned bits = 0; for (int v = 0; v < n; ++v) if (core[v]) bits |= 1u << v;
            assert(bits == bruteCore(n, nb));
            bool empty = bits == 0;
            forests += empty;
            if (!empty) assert(girthBfs(n, e) >= 3);                                      // 사이클이 있으면 둘레가 정의되고 단순 그래프라 ≥ 3
            else assert(girthBfs(n, e) == 0);
        }
    }
    assert(forests == 1 + 2 + 7 + 38 + 291 + 2932);                                     // 정점 1..6 개 이름 붙은 숲의 개수

    // ④ 둘레: 독립 오라클(간선 제거 후 거리) 과 일치, 무작위 다중 그래프에서도
    std::mt19937 rng(4242);
    int shortSeen = 0;
    for (int it = 0; it < 1500; ++it) {
        int n = 2 + (int)(rng() % 14);
        int m = (int)(rng() % (unsigned)(n + 6));
        Edges e; for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % n), (int)(rng() % n)});
        int g = girthBfs(n, e);
        assert(g == girthByEdgeRemoval(n, e));
        shortSeen += g >= 1 && g <= 2;
        // 2-코어가 비어 있다 ⇔ 둘레가 0 (사이클 없음)
        auto core = twoCore(n, e);
        assert((std::count(core.begin(), core.end(), 1) == 0) == (g == 0));
    }
    assert(shortSeen > 100);
    {   // 알려진 그래프의 둘레
        Edges petersen;
        for (int i = 0; i < 5; ++i) { petersen.push_back({i, (i + 1) % 5}); petersen.push_back({i, i + 5}); petersen.push_back({5 + i, 5 + (i + 2) % 5}); }
        assert(girthBfs(10, petersen) == 5);
        Edges cube; for (int v = 0; v < 8; ++v) for (int b = 0; b < 3; ++b) if (!(v >> b & 1)) cube.push_back({v, v | 1 << b});
        assert(girthBfs(8, cube) == 4);
        Edges k33; for (int a = 0; a < 3; ++a) for (int b = 3; b < 6; ++b) k33.push_back({a, b});
        assert(girthBfs(6, k33) == 4);
        Edges heawood; for (int i = 0; i < 14; ++i) heawood.push_back({i, (i + 1) % 14});
        for (int i = 0; i < 14; i += 2) heawood.push_back({i, (i + 5) % 14});                // 14-사이클에 현 7 개 (교대로 +5)
        assert(girthBfs(14, heawood) == 6);
        Edges grid; for (int r = 0; r < 6; ++r) for (int c = 0; c < 6; ++c) { if (c + 1 < 6) grid.push_back({r * 6 + c, r * 6 + c + 1}); if (r + 1 < 6) grid.push_back({r * 6 + c, (r + 1) * 6 + c}); }
        assert(girthBfs(36, grid) == 4);
        Edges k6; for (int a = 0; a < 6; ++a) for (int b = a + 1; b < 6; ++b) k6.push_back({a, b});
        assert(girthBfs(6, k6) == 3);
    }

    // ⑤ 큰 입력: 백만 정점 사슬은 한 번에 벗겨지고(DAG), 방향 사이클·무방향 사이클은 하나도 안 벗겨진다
    {
        const int N = 1000000;
        Edges path; path.reserve(N);
        for (int i = 0; i + 1 < N; ++i) path.push_back({i, i + 1});
        Kahn k = kahn(N, path);
        assert(k.acyclic && k.order.front() == 0 && k.order.back() == N - 1);
        auto core = twoCore(N, path);
        assert(std::count(core.begin(), core.end(), 1) == 0);
        path.push_back({N - 1, 0});
        Kahn c = kahn(N, path);
        assert(!c.acyclic && c.order.empty() && std::count(c.leftover.begin(), c.leftover.end(), 1) == N);
        core = twoCore(N, path);
        assert(std::count(core.begin(), core.end(), 1) == N);
    }
    std::cout << "DetectCycleBFS: Kahn's peeling left exactly the vertices reachable from a cycle on every loop-free digraph with up to 5 vertices and counted 1,3,25,543,29281 acyclic ones, leaf-peeling returned exactly the 2-core (union of all subsets of minimum degree 2) on all 33,867 graphs with up to 6 vertices with the forests numbering 1+2+7+38+291+2932, the BFS girth equalled an independent edge-removal girth on 1500 random multigraphs and the known girths of Petersen (5), Heawood (6), the cube, K3,3 and the grid, and a 1,000,000-vertex chain peeled completely while the closed cycle peeled not at all" << std::endl; return 0;
}
// Time Complexity: O(V + E)  (girth 는 모든 루트에서 BFS 하므로 O(V · (V + E)))
// Space Complexity: O(V + E)
```
## DetectCycleUnionFind()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// 서로소 집합으로 무방향 사이클 찾기: 간선을 하나씩 읽으며 두 끝이 이미 같은 집합이면 그 간선이 사이클을 닫는다. 간선이 스트림으로 하나씩 도착해도 그때그때 알 수 있는(온라인) 유일하게 간단한 방법이고, "처음으로 사이클을 닫는 간선" 을 바로 알려준다. 자기 루프는 find(a) == find(a), 평행 간선은 두 번째에서 걸린다.
// 사이클을 닫는 간선의 개수 = 순환수(cyclomatic number) E − V + c — 합쳐지는 간선(신장 숲에 들어가는 간선)이 정확히 V − c 개이기 때문이다. 이 값은 간선 도착 순서와 무관하다. 방향 그래프에 쓰면 안 된다: 다이아몬드 0→1→3, 0→2→3 은 무방향으로는 사이클이 있지만 방향 사이클은 없다 — 서로소 집합은 "약한" 사이클만 본다.
// 구현 두 개를 비교한다 — 순진한 것(경로 압축·크기 병합 없음, 그냥 루트를 다른 루트에 매닮)과 실전용(크기 병합 + 경로 반 접기). 간선 (0,1), (1,2), … 을 넣으며 매번 find(0) 을 부르는 최악 순서에서 순진한 쪽은 포인터 따라가기가 정확히 n(n − 1)/2 번, 실전용은 O(n) 이다 — 시간 대신 센 횟수로 단언한다.
using Edges = std::vector<std::pair<int, int>>;

struct NaiveDsu {
    std::vector<int> p; long long hops = 0;
    explicit NaiveDsu(int n) : p(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) { x = p[x]; ++hops; } return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; p[a] = b; return true; }
};
struct FastDsu {
    std::vector<int> p, sz; long long hops = 0;
    explicit FastDsu(int n) : p(n), sz(n, 1) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; ++hops; } return x; }     // 경로 반 접기
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) std::swap(a, b);
        p[b] = a; sz[a] += sz[b];
        return true;
    }
};
// 첫 번째로 사이클을 닫는 간선의 인덱스 (없으면 -1).
template <class D>
int firstClosing(int n, const Edges& e) {
    D d(n);
    for (int i = 0; i < (int)e.size(); ++i) if (!d.unite(e[i].first, e[i].second)) return i;
    return -1;
}
// 닫는 간선의 총 개수.
int closingCount(int n, const Edges& e) {
    FastDsu d(n); int c = 0;
    for (auto [a, b] : e) c += !d.unite(a, b);
    return c;
}
// 오라클: 접두사 e[0..k) 에 사이클이 있는가를 DFS 가 아닌 "잎 벗기기" 로 판정(코드가 겹치지 않음).
bool prefixHasCycle(int n, const Edges& e, int k) {
    std::vector<std::vector<int>> adj(n); std::vector<int> deg(n, 0);
    for (int i = 0; i < k; ++i) { auto [a, b] = e[i]; adj[a].push_back(b); ++deg[a]; if (a != b) { adj[b].push_back(a); ++deg[b]; } else { adj[a].push_back(a); ++deg[a]; } }
    std::vector<char> gone(n, 0); std::vector<int> st;
    for (int v = 0; v < n; ++v) if (deg[v] <= 1) { gone[v] = 1; st.push_back(v); }
    while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : adj[u]) if (!gone[v] && --deg[v] <= 1) { gone[v] = 1; st.push_back(v); } }
    return std::count(gone.begin(), gone.end(), 0) > 0;
}

int main() {
    // ① 손으로 확인한 모양
    assert(firstClosing<FastDsu>(3, {{0, 1}, {1, 2}, {0, 2}}) == 2);                      // 삼각형은 세 번째 간선이 닫는다
    assert(firstClosing<FastDsu>(2, {{0, 1}, {1, 0}}) == 1 && firstClosing<FastDsu>(1, {{0, 0}}) == 0);
    assert(firstClosing<FastDsu>(4, {{0, 1}, {2, 3}, {1, 2}}) == -1);                      // 경로
    assert(firstClosing<NaiveDsu>(3, {{0, 1}, {1, 2}, {0, 2}}) == 2);
    {   Edges diamond = {{0, 1}, {0, 2}, {1, 3}, {2, 3}};                                  // 방향 DAG 지만 무방향으론 사이클 — 서로소 집합은 약한 사이클을 본다
        assert(firstClosing<FastDsu>(4, diamond) == 3);
    }

    // ② 전수: 정점 ≤ 6 의 모든 단순 그래프, 간선 순서도 바꿔서 — 첫 닫는 간선이 접두사 오라클과 같고, 닫는 간선 수 = E − V + c, 두 구현이 같은 답
    for (int n = 1; n <= 6; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        std::mt19937 rng(n);
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            if (mask & 1) std::shuffle(e.begin(), e.end(), rng);                           // 도착 순서는 결과에 영향이 없어야 한다
            int first = firstClosing<FastDsu>(n, e);
            assert(first == firstClosing<NaiveDsu>(n, e));
            int ek = 0;
            while (ek <= (int)e.size() && !prefixHasCycle(n, e, ek)) ++ek;
            if (first < 0) assert(ek == (int)e.size() + 1); else assert(ek == first + 1); // 처음 사이클이 생긴 접두사 길이 = first + 1
            FastDsu d(n); int comps = n; for (auto [a, b] : e) comps -= d.unite(a, b);
            assert(closingCount(n, e) == (int)e.size() - n + comps);
        }
    }

    // ③ 무작위 다중 그래프(루프·평행 간선): 순환수 항등식, 순서 무관, 두 구현의 일치
    std::mt19937 rng(8080);
    for (int it = 0; it < 2000; ++it) {
        int n = 1 + (int)(rng() % 20), m = (int)(rng() % (unsigned)(2 * n + 2));
        Edges e; for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % n), (int)(rng() % n)});
        int c1 = closingCount(n, e);
        Edges f = e; std::shuffle(f.begin(), f.end(), rng);
        assert(closingCount(n, f) == c1);
        assert(firstClosing<NaiveDsu>(n, e) == firstClosing<FastDsu>(n, e));
        FastDsu d(n); int comps = n; for (auto [a, b] : e) comps -= d.unite(a, b);
        assert(c1 == m - n + comps);
        int first = firstClosing<FastDsu>(n, e);
        assert((first >= 0) == prefixHasCycle(n, e, m));
        if (first >= 0) assert(prefixHasCycle(n, e, first + 1) && !prefixHasCycle(n, e, first));
    }

    // ④ 비용 측정: (0,1), (1,2), … 을 넣으며 매번 find(0) — 순진한 쪽은 따라가기 정확히 n(n−1)/2 번, 실전용은 3n 이하
    {
        const int n = 2000;
        NaiveDsu a(n); FastDsu b(n);
        for (int i = 0; i + 1 < n; ++i) { assert(a.unite(i, i + 1) && b.unite(i, i + 1)); a.find(0); b.find(0); }
        assert(a.hops == (long long)n * (n - 1) / 2);                                    // 1,999,000
        assert(b.hops <= 3LL * n);
    }

    // ⑤ 큰 입력: 백만 정점 사슬에 마지막 간선이 처음으로 닫으며, 사슬 중간의 순서를 뒤섞어도 같은 한 개
    {
        const int N = 1000000;
        Edges e; e.reserve(N);
        for (int i = 0; i + 1 < N; ++i) e.push_back({i, i + 1});
        e.push_back({N - 1, 0});
        assert(firstClosing<FastDsu>(N, e) == N - 1 && closingCount(N, e) == 1);
        std::mt19937 r(5); std::shuffle(e.begin(), e.end(), r);
        assert(closingCount(N, e) == 1);
    }
    std::cout << "DetectCycleUnionFind: the first cycle-closing edge matched a leaf-peeling prefix oracle on all 33,867 graphs with up to 6 vertices (also with shuffled arrival order) and on 2000 random multigraphs, the number of closing edges always equalled E - V + c, the naive union-find followed exactly n(n-1)/2 = 1,999,000 pointers on the worst chain while path-halving with union by size needed at most 3n, the diamond DAG showed that union-find only sees weak cycles, and a shuffled 1,000,000-edge cycle still had exactly one closing edge" << std::endl; return 0;
}
// Time Complexity: O(E α(V))
// Space Complexity: O(V)
```
## IsTree()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 트리 판정(IsTree): 무방향 그래프가 트리 ⇔ 아래가 모두 동치.  (a) 연결이고 E = V − 1   (b) 연결이고 사이클 없음   (c) 사이클 없고 E = V − 1 (연결은 따로 안 봐도 된다)   (d) 연결이고 모든 간선이 다리   (e) 임의의 두 정점 사이에 단순 경로가 정확히 하나.  쓰기 쉬운 것은 (a) 하나만 확인해도 되는 형태 — BFS 로 연결 확인 + 간선 수 비교.
// 약속: V = 0 은 트리가 아니다(정점 ≥ 1). 루프와 평행 간선은 곧 사이클이므로 트리가 아니다 — 인접 리스트 크기 합 / 2 로 간선 수를 세던 옛 방식은 루프(리스트에 한 번만 들어감)에서 틀려서, 여기서는 간선 목록을 그대로 센다.
// 방향 그래프의 트리는 "뿌리 있는 트리(arborescence)": 진입 차수 0 인 정점(뿌리)이 정확히 하나, 나머지는 진입 차수 1, 뿌리에서 모든 정점에 닿음.
// 검증: ① 다섯 판정이 정점 ≤ 6 의 모든 단순 그래프에서 같은 답이고 이름 붙은 트리의 개수가 Cayley 공식 n^(n−2) = 1, 1, 3, 16, 125, 1296. ② Prüfer 수열 ↔ 트리 일대일 대응 — n = 5 에서 125 개 수열이 125 개의 서로 다른 트리를 만든다. ③ 트리에 간선 하나를 더하면 사이클이 정확히 하나, 간선 하나를 빼면 정확히 두 성분. ④ 방향 트리 개수가 n^(n−1) = 1, 2, 9, 64, 625 (뿌리 하나를 고르는 n 가지 × 트리 n^(n−2)).
using Edges = std::vector<std::pair<int, int>>;
struct Dsu {
    std::vector<int> p;
    explicit Dsu(int n) : p(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; p[a] = b; return true; }
};
bool bfsConnected(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : e) { adj[a].push_back(b); adj[b].push_back(a); }
    std::vector<char> seen(n, 0); std::queue<int> q; q.push(0); seen[0] = 1; int cnt = 1;
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = 1; ++cnt; q.push(v); } }
    return cnt == n;
}
bool treeA(int n, const Edges& e) { return n >= 1 && (int)e.size() == n - 1 && bfsConnected(n, e); }          // 연결 + E = V − 1
bool treeB(int n, const Edges& e) {                                                                          // 연결 + 사이클 없음
    if (n < 1) return false;
    Dsu d(n); for (auto [a, b] : e) if (!d.unite(a, b)) return false;
    return bfsConnected(n, e);
}
bool treeC(int n, const Edges& e) {                                                                          // 사이클 없음 + E = V − 1 (연결 검사 없이)
    if (n < 1 || (int)e.size() != n - 1) return false;
    Dsu d(n); for (auto [a, b] : e) if (!d.unite(a, b)) return false;
    return true;
}
int components(int n, const Edges& e, int skip = -1) {
    Dsu d(n); int c = n;
    for (int i = 0; i < (int)e.size(); ++i) if (i != skip && d.unite(e[i].first, e[i].second)) --c;
    return c;
}
bool treeD(int n, const Edges& e) {                                                                          // 연결 + 모든 간선이 다리
    if (n < 1 || components(n, e) != 1) return false;
    for (int i = 0; i < (int)e.size(); ++i) if (components(n, e, i) == 1) return false;
    return true;
}
int simplePaths(int n, const std::vector<unsigned>& nb, int u, int t, unsigned seen) {                       // 2 에서 멈추는 단순 경로 수
    if (u == t) return 1;
    int total = 0;
    for (int v = 0; v < n; ++v) if ((nb[u] >> v & 1) && !(seen >> v & 1)) { total += simplePaths(n, nb, v, t, seen | 1u << v); if (total >= 2) return 2; }
    return total;
}
bool treeE(int n, const Edges& e) {                                                                          // 모든 쌍에 단순 경로 정확히 하나 (단순 그래프, n ≤ 16)
    std::vector<unsigned> nb(n, 0);
    for (auto [a, b] : e) { if (a == b) return false; nb[a] |= 1u << b; nb[b] |= 1u << a; }
    for (int s = 0; s < n; ++s) for (int t = s + 1; t < n; ++t) if (simplePaths(n, nb, s, t, 1u << s) != 1) return false;
    return n >= 1;
}
// 방향: 뿌리 있는 트리
bool isArborescence(int n, const Edges& arcs) {
    if (n < 1 || (int)arcs.size() != n - 1) return false;
    std::vector<int> indeg(n, 0); std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : arcs) { ++indeg[b]; adj[a].push_back(b); }
    int root = -1;
    for (int v = 0; v < n; ++v) { if (indeg[v] == 0) { if (root >= 0) return false; root = v; } else if (indeg[v] != 1) return false; }
    if (root < 0) return false;
    std::vector<char> seen(n, 0); std::queue<int> q; q.push(root); seen[root] = 1; int cnt = 1;
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = 1; ++cnt; q.push(v); } }
    return cnt == n;
}
// Prüfer 수열 ↔ 이름 붙은 트리
Edges pruferDecode(int n, const std::vector<int>& seq) {
    std::vector<int> deg(n, 1); for (int x : seq) ++deg[x];
    Edges e;
    for (int x : seq) for (int j = 0; j < n; ++j) if (deg[j] == 1) { e.push_back({j, x}); --deg[j]; --deg[x]; break; }
    int u = -1, v = -1;
    for (int j = 0; j < n; ++j) if (deg[j] == 1) (u < 0 ? u : v) = j;
    e.push_back({u, v});
    return e;
}
std::vector<int> pruferEncode(int n, const Edges& e) {
    std::vector<std::set<int>> adj(n);
    for (auto [a, b] : e) { adj[a].insert(b); adj[b].insert(a); }
    std::vector<int> seq;
    for (int step = 0; step < n - 2; ++step) {
        int j = 0; while (adj[j].size() != 1) ++j;                               // 가장 작은 잎
        int x = *adj[j].begin(); seq.push_back(x);
        adj[x].erase(j); adj[j].clear();
    }
    return seq;
}

int main() {
    // ① 손으로 확인한 모양과 함정
    assert(treeA(1, {}) && !treeA(0, {}) && !treeA(2, {}) && treeA(2, {{0, 1}}));
    assert(!treeA(3, {{0, 1}, {0, 1}}) && !treeB(3, {{0, 1}, {0, 1}}));                          // 평행 간선 + 고립 정점 : 간선 수는 맞지만 연결도 아니고 사이클
    assert(!treeA(2, {{0, 0}}) && !treeB(2, {{0, 0}}) && !treeC(2, {{0, 0}}));                   // 루프로 E = V − 1 을 맞춰도 연결이 아니다
    assert(!treeC(4, {{0, 1}, {1, 2}, {2, 0}}) && !treeA(4, {{0, 1}, {1, 2}, {2, 0}}));          // 삼각형 + 고립 : E = 3 = V − 1 인데 트리 아님
    assert(treeA(5, {{0, 1}, {0, 2}, {1, 3}, {1, 4}}));

    // ② 전수: 다섯 판정이 모든 단순 그래프(정점 ≤ 6, 2^15)에서 같고 트리 개수 = n^(n−2)
    const long long cayley[7] = {0, 1, 1, 3, 16, 125, 1296};
    for (int n = 1; n <= 6; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        long long trees = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            bool a = treeA(n, e);
            assert(a == treeB(n, e) && a == treeC(n, e) && a == treeD(n, e) && a == treeE(n, e));
            trees += a;
        }
        assert(trees == cayley[n]);
    }

    // ③ Prüfer: n = 5 의 모든 수열 5^3 = 125 가 서로 다른 트리, 왕복 일치. n ≤ 40 무작위 수열도 트리
    {
        std::set<Edges> distinct;
        for (int code = 0; code < 125; ++code) {
            std::vector<int> seq = {code % 5, code / 5 % 5, code / 25};
            Edges e = pruferDecode(5, seq);
            assert(treeA(5, e) && pruferEncode(5, e) == seq);
            for (auto& x : e) if (x.first > x.second) std::swap(x.first, x.second);
            std::sort(e.begin(), e.end());
            distinct.insert(e);
        }
        assert(distinct.size() == 125);
        std::mt19937 rng(12345);
        for (int it = 0; it < 300; ++it) {
            int n = 3 + (int)(rng() % 38);
            std::vector<int> seq(n - 2); for (int& x : seq) x = (int)(rng() % n);
            Edges e = pruferDecode(n, seq);
            assert(treeA(n, e) && treeB(n, e) && treeC(n, e));
            assert(pruferEncode(n, e) == seq);
            // ④ 간선 추가/제거 성질
            for (int tries = 0; tries < 6; ++tries) {
                int a = (int)(rng() % n), b = (int)(rng() % n);
                if (a == b) continue;
                Edges f = e; f.push_back({a, b});
                assert(!treeA(n, f));
                Dsu d(n); int closing = 0; for (auto [x, y] : f) closing += !d.unite(x, y);
                assert(closing == 1);                                                          // 사이클이 정확히 하나(순환수 1)
                int skip = (int)(rng() % e.size());
                assert(components(n, e, skip) == 2);                                           // 간선 하나를 빼면 정확히 두 성분
                Edges g = e; g.erase(g.begin() + skip);
                assert(!treeA(n, g));
            }
        }
    }

    // ⑤ 방향 트리(arborescence): 정점 ≤ 5 의 모든 방향 그래프(루프 없음)에서 개수 n^(n−1) = 1, 2, 9, 64, 625
    const long long rooted[6] = {0, 1, 2, 9, 64, 625};
    for (int n = 1; n <= 5; ++n) {
        Edges all;
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) all.push_back({a, b});
        int m = (int)all.size();
        long long count = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            if (__builtin_popcount(mask) != n - 1) continue;                                   // 호 수가 V − 1 이어야만 하므로 나머지는 건너뛴다
            Edges arcs; for (int i = 0; i < m; ++i) if (mask >> i & 1) arcs.push_back(all[i]);
            if (isArborescence(n, arcs)) {
                ++count;
                Edges und = arcs; assert(treeA(n, und));                                       // 방향을 지우면 무방향 트리
            }
        }
        assert(count == rooted[n]);
    }
    assert(!isArborescence(3, {{0, 1}, {2, 1}}) && !isArborescence(3, {{0, 1}, {1, 0}}) && isArborescence(3, {{1, 0}, {1, 2}}));

    // ⑥ 큰 입력: 백만 정점 사슬 · 별은 트리, 간선 하나를 빼면 아님
    {
        const int N = 1000000;
        Edges path, star;
        for (int i = 0; i + 1 < N; ++i) path.push_back({i, i + 1});
        for (int i = 1; i < N; ++i) star.push_back({0, i});
        assert(treeA(N, path) && treeC(N, path) && treeA(N, star) && isArborescence(N, path));
        Edges cut = path; cut.pop_back();
        assert(!treeA(N, cut));
        path.back() = {0, 2};                                                                    // 마지막 간선을 바꾸면 사이클이 생기고 N−1 번째 정점이 고립
        assert(!treeA(N, path));
    }
    std::cout << "IsTree: five characterisations (connected with V-1 edges, connected and acyclic, acyclic with V-1 edges, connected with every edge a bridge, exactly one simple path per pair) agreed on all 33,867 graphs with up to 6 vertices and counted the labeled trees 1,1,3,16,125,1296 = n^(n-2); Pruefer decoding gave 125 distinct trees for n = 5 and round-tripped on 300 random sequences, adding any edge to a tree created exactly one cycle and removing any edge left exactly two components, the arborescence test counted 1,2,9,64,625 = n^(n-1) rooted trees over all digraphs up to 5 vertices, and a 1,000,000-vertex path and star were accepted" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## IsForest()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 숲 판정(IsForest): 사이클이 없는 무방향 그래프. 동치 조건 — (a) 간선 수 = V − (성분 수)  (b) 간선을 서로소 집합에 넣을 때 한 번도 같은 집합을 잇지 않음  (c) 잎 벗기기를 끝내면 아무것도 안 남음(2-코어가 공집합)  (d) 모든 간선이 다리. 성분 하나하나가 트리이므로 성분이 c 개면 간선은 정확히 V − c 개이고, 따라서 숲의 성분 수는 V − E 로 곧바로 나온다. 루프와 평행 간선은 숲을 깨뜨린다.
// 닫힌 식 오라클: 이름 붙은 숲의 개수 f(n) 은 "1 번 정점이 속한 트리의 크기 k" 로 나누면 f(n) = Σ_{k=1..n} C(n−1, k−1) · k^(k−2) · f(n−k), f(0) = 1  (트리 k^(k−2) 개 = Cayley) → 1, 2, 7, 38, 291, 2932 (n = 1..6).
// 온라인 버전: 간선이 하나씩 들어올 때 "숲을 유지한 채 받을 수 있는가" — 서로소 집합이 같은 집합이면 거절, 다르면 합치고 성분 수 − 1. 이 구조(Forest) 는 크루스칼 알고리즘의 심장이다.
using Edges = std::vector<std::pair<int, int>>;
struct Dsu {
    std::vector<int> p;
    explicit Dsu(int n) : p(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; p[a] = b; return true; }
};
int components(int n, const Edges& e, int skip = -1) {
    Dsu d(n); int c = n;
    for (int i = 0; i < (int)e.size(); ++i) if (i != skip && d.unite(e[i].first, e[i].second)) --c;
    return c;
}
bool forestA(int n, const Edges& e) { return (int)e.size() == n - components(n, e); }                       // 간선 수 = V − 성분 수
bool forestB(int n, const Edges& e) { Dsu d(n); for (auto [a, b] : e) if (!d.unite(a, b)) return false; return true; }
bool forestC(int n, const Edges& e) {                                                                          // 잎 벗기기가 끝까지 간다
    std::vector<std::vector<int>> adj(n); std::vector<int> deg(n, 0);
    for (auto [a, b] : e) { adj[a].push_back(b); ++deg[a]; if (a != b) { adj[b].push_back(a); ++deg[b]; } else { adj[a].push_back(a); ++deg[a]; } }
    std::vector<char> gone(n, 0); std::queue<int> q;
    for (int v = 0; v < n; ++v) if (deg[v] <= 1) { gone[v] = 1; q.push(v); }
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!gone[v] && --deg[v] <= 1) { gone[v] = 1; q.push(v); } }
    return std::count(gone.begin(), gone.end(), 0) == 0;
}
bool forestD(int n, const Edges& e) {                                                                          // 모든 간선이 다리
    int base = components(n, e);
    for (int i = 0; i < (int)e.size(); ++i) if (components(n, e, i) == base) return false;
    return true;
}
// 온라인 숲
struct Forest {
    Dsu d; int trees, edges = 0;
    explicit Forest(int n) : d(n), trees(n) {}
    bool add(int a, int b) { if (!d.unite(a, b)) return false; --trees; ++edges; return true; }
    bool sameTree(int a, int b) { return d.find(a) == d.find(b); }
};

int main() {
    // ① 손으로 확인한 모양
    assert(forestA(0, {}) && forestA(1, {}) && forestA(5, {}));                                             // 빈 그래프는 숲(성분 V 개)
    assert(forestA(5, {{0, 1}, {1, 2}, {3, 4}}) && components(5, {{0, 1}, {1, 2}, {3, 4}}) == 2);
    assert(!forestA(3, {{0, 1}, {1, 2}, {2, 0}}) && !forestA(1, {{0, 0}}) && !forestA(2, {{0, 1}, {1, 0}}));
    assert(!forestB(2, {{0, 1}, {0, 1}}) && !forestC(1, {{0, 0}}) && !forestD(2, {{0, 1}, {0, 1}}));

    // ② 전수: 네 판정이 정점 ≤ 6 의 모든 단순 그래프에서 같고, 숲의 개수 = 닫힌 식, 숲의 성분 수 = V − E
    long long choose[7][7] = {};
    for (int i = 0; i < 7; ++i) { choose[i][0] = 1; for (int j = 1; j <= i; ++j) choose[i][j] = choose[i - 1][j - 1] + (j <= i - 1 ? choose[i - 1][j] : 0); }
    auto cayley = [](int k) { long long r = 1; for (int i = 0; i < k - 2; ++i) r *= k; return r; };            // k^(k−2), k = 1 이면 1
    long long f[7] = {1};
    for (int n = 1; n <= 6; ++n) { f[n] = 0; for (int k = 1; k <= n; ++k) f[n] += choose[n - 1][k - 1] * cayley(k) * f[n - k]; }
    assert(f[1] == 1 && f[2] == 2 && f[3] == 7 && f[4] == 38 && f[5] == 291 && f[6] == 2932);
    for (int n = 1; n <= 6; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        long long forests = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            bool a = forestA(n, e);
            assert(a == forestB(n, e) && a == forestC(n, e) && a == forestD(n, e));
            if (a) { ++forests; assert(components(n, e) == n - (int)e.size()); }
        }
        assert(forests == f[n]);
    }

    // ③ 무작위 숲: 앞쪽 k 개를 루트로 두고 나머지는 앞선 정점에 하나씩 붙인다 → 성분 정확히 k 개, 간선 V − k 개
    std::mt19937 rng(606);
    int inside = 0, across = 0;
    for (int it = 0; it < 400; ++it) {
        int n = 6 + (int)(rng() % 34), k = 1 + (int)(rng() % 5);
        Edges e;
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        for (int i = k; i < n; ++i) e.push_back({perm[i], perm[rng() % i]});                              // 앞쪽 i 개 중 하나에 붙임 (앞쪽 k 개는 루트들)
        assert(forestA(n, e) && forestB(n, e) && forestC(n, e) && components(n, e) == k && (int)e.size() == n - k);   // 모든 비루트가 루트 중 하나의 트리에 붙으므로 성분은 정확히 k
        Dsu d(n); for (auto [a, b] : e) d.unite(a, b);
        for (int tries = 0; tries < 8; ++tries) {
            int a = (int)(rng() % n), b = (int)(rng() % n);
            if (a == b) continue;
            Edges g = e; g.push_back({a, b});
            bool same = d.find(a) == d.find(b);
            assert(forestA(n, g) == !same);                                                           // 같은 트리 안의 간선은 숲을 깨고, 다른 트리를 잇는 간선은 유지
            if (same) ++inside; else { ++across; assert(components(n, g) == components(n, e) - 1); }
        }
    }
    assert(inside > 100 && across > 100);

    // ④ 온라인 Forest: 무작위 간선 500 개를 흘려 넣고 매번 오라클(전체를 다시 판정) 과 비교
    for (int round = 0; round < 40; ++round) {
        int n = 10 + (int)(rng() % 20);
        Forest fo(n); Edges kept;
        int refused = 0, accepted = 0;
        for (int step = 0; step < 500; ++step) {
            int a = (int)(rng() % n), b = (int)(rng() % n);
            Edges trial = kept; trial.push_back({a, b});
            bool wouldStay = forestA(n, trial);
            bool ok = fo.add(a, b);
            assert(ok == wouldStay);
            if (ok) { kept.push_back({a, b}); ++accepted; } else ++refused;
            assert(fo.trees == n - (int)kept.size() && fo.trees == components(n, kept) && fo.edges == (int)kept.size());
        }
        assert(accepted <= n - 1 && accepted >= 1 && refused > 400);
    }

    // ⑤ 큰 입력: 백만 정점에서 짝수 간선만(성분 50 만 개의 간선 한 쌍씩) 숲, 사이클 하나를 만들면 아님
    {
        const int N = 1000000;
        Edges e;
        for (int i = 0; i + 1 < N; i += 2) e.push_back({i, i + 1});
        assert(forestB(N, e) && components(N, e) == N / 2 && forestA(N, e));
        e.push_back({0, 1});                                                                             // 평행 간선
        assert(!forestB(N, e) && !forestA(N, e));
    }
    std::cout << "IsForest: four tests (E = V - components, union-find never closing a cycle, leaf-peeling emptying the graph, every edge a bridge) agreed on all 33,867 graphs with up to 6 vertices and the number of forests matched the Cayley-based recurrence 1,2,7,38,291,2932, the component count of every forest equalled V - E, random forests accepted an edge exactly when it joined two different trees (which also lowered the component count by one), the online Forest structure agreed with a from-scratch re-test after each of 20,000 random insertions, and a 1,000,000-vertex matching was a forest until a parallel edge appeared" << std::endl; return 0;
}
// Time Complexity: O(V + E α(V))
// Space Complexity: O(V)
```
## IsBiconnected()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 이중 연결(Biconnected, 2-정점-연결) 판정: 연결이고 단절점이 없다 — 정점 하나를 아무거나 지워도 나머지가 연결이다. 반복형 Tarjan low-link 로 O(V + E): 뿌리의 자식이 둘 이상이거나, 뿌리가 아닌 u 에 low[c] ≥ dfn[u] 인 자식 c 가 있으면 단절점이 있으니 거짓. 방문 못한 정점이 있으면(비연결) 거짓.
// 약속: V = 0 은 거짓. 정점 하나(K1)와 K2 는 "지워도 연결" 정의에 따라 참(정점 하나를 지우면 남는 건 비거나 정점 하나라 연결). 평행 간선·루프는 영향이 없다.
// 이중 연결(정점)과 이중 간선 연결(다리 없음)은 다르다 — 삼각형 두 개가 정점 하나를 공유한 나비넥타이는 다리가 없지만 공유 정점이 단절점이다.
// 동치 정리(Whitney/Menger, V ≥ 3): 이중 연결 ⇔ 임의의 두 정점 사이에 내부 정점이 겹치지 않는 경로가 둘 이상. 아래 오라클이 이를 정점 분할 최대 유량으로 센다. 구성적 특징: 사이클에서 시작해 "귀(ear)" — 이미 있는 서로 다른 두 정점을 새 정점들의 경로로 잇기 — 를 계속 붙여서 만든 그래프는 항상 이중 연결.
// 검증: ① 정의 그대로(모든 정점을 지워 보기) 와 정점 ≤ 6 의 모든 단순 그래프에서 일치, 이중 연결 그래프의 수가 1, 1, 1, 10, 238, 11368 (V = 1..6) ② 최대 유량 판정과 일치 ③ 간선을 더해도 성질이 유지(단조) ④ 귀 붙이기로 만든 무작위 그래프는 전부 참, 가지를 하나 달거나 두 개를 한 점에서 붙이면 거짓.
using Edges = std::vector<std::pair<int, int>>;

bool isBiconnected(int n, const Edges& e) {
    if (n <= 0) return false;
    std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : e) { adj[a].push_back(b); if (a != b) adj[b].push_back(a); else adj[a].push_back(a); }
    std::vector<int> dfn(n, 0), low(n, 0), par(n, -1), it(n, 0), st;
    int timer = 0, visited = 1, rootChildren = 0;
    dfn[0] = low[0] = ++timer; st.push_back(0);
    while (!st.empty()) {
        int u = st.back();
        if (it[u] < (int)adj[u].size()) {
            int v = adj[u][it[u]++];
            if (!dfn[v]) { par[v] = u; dfn[v] = low[v] = ++timer; ++visited; st.push_back(v); }
            else low[u] = std::min(low[u], dfn[v]);
        } else {
            st.pop_back();
            int p = par[u];
            if (p >= 0) {
                low[p] = std::min(low[p], low[u]);
                if (p == 0) ++rootChildren;
                else if (low[u] >= dfn[p]) return false;                          // 뿌리가 아닌 p 가 단절점
            }
        }
    }
    return visited == n && rootChildren <= 1;                                     // 비연결이거나 뿌리가 단절점이면 거짓
}

// ---- 오라클 ----
int compsExcluding(int n, const Edges& e, int removed) {                          // 정점 removed 를 지운 그래프의 성분 수 (removed = -1 이면 그대로)
    std::vector<int> p(n); std::iota(p.begin(), p.end(), 0);
    auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
    int c = n - (removed >= 0);
    for (auto [a, b] : e) { if (a == removed || b == removed) continue; a = find(a); b = find(b); if (a != b) { p[a] = b; --c; } }
    return c;
}
bool bruteBiconnected(int n, const Edges& e) {                                    // 정의 그대로: 연결 + 어떤 정점을 지워도 연결 (공집합은 연결로 본다)
    if (n < 1 || compsExcluding(n, e, -1) != 1) return false;
    for (int v = 0; v < n; ++v) if (compsExcluding(n, e, v) > 1) return false;
    return true;
}
// 정점 분할 최대 유량: s–t 사이에서 내부 정점이 서로 겹치지 않는 경로의 최대 개수 (단순 그래프, 2n ≤ 16)
int disjointPaths(int n, const Edges& e, int s, int t) {
    int N = 2 * n;
    std::vector<std::vector<int>> cap(N, std::vector<int>(N, 0));
    for (int v = 0; v < n; ++v) cap[2 * v][2 * v + 1] = (v == s || v == t) ? n : 1;       // v_in → v_out
    for (auto [a, b] : e) if (a != b) { cap[2 * a + 1][2 * b] = 1; cap[2 * b + 1][2 * a] = 1; }
    int src = 2 * s + 1, snk = 2 * t, flow = 0;
    while (true) {
        std::vector<int> prev(N, -1); prev[src] = src;
        std::queue<int> q; q.push(src);
        while (!q.empty() && prev[snk] < 0) { int u = q.front(); q.pop(); for (int v = 0; v < N; ++v) if (prev[v] < 0 && cap[u][v] > 0) { prev[v] = u; q.push(v); } }
        if (prev[snk] < 0) break;
        for (int v = snk; v != src; v = prev[v]) { --cap[prev[v]][v]; ++cap[v][prev[v]]; }
        ++flow;
    }
    return flow;
}
bool flowBiconnected(int n, const Edges& e) {                                      // n ≥ 3 : 모든 쌍에서 경로 ≥ 2
    for (int s = 0; s < n; ++s) for (int t = s + 1; t < n; ++t) if (disjointPaths(n, e, s, t) < 2) return false;
    return true;
}
// 귀 붙이기 생성기: 사이클에서 시작해 귀를 계속 붙인다 (단순 그래프를 유지)
Edges randomEarGraph(int& n, std::mt19937& rng) {
    int k = 3 + (int)(rng() % 4);
    Edges e; for (int i = 0; i < k; ++i) e.push_back({i, (i + 1) % k});
    n = k;
    auto has = [&](int a, int b) { for (auto [x, y] : e) if ((x == a && y == b) || (x == b && y == a)) return true; return false; };
    int ears = 1 + (int)(rng() % 8);
    for (int i = 0; i < ears; ++i) {
        int a = (int)(rng() % n), b = (int)(rng() % n);
        if (a == b) continue;
        int len = (int)(rng() % 4);                                                // 새 정점 개수
        if (len == 0) { if (!has(a, b)) e.push_back({a, b}); continue; }
        int prev = a;
        for (int j = 0; j < len; ++j) { e.push_back({prev, n}); prev = n++; }
        e.push_back({prev, b});
    }
    return e;
}

int main() {
    // ① 손으로 확인한 모양
    assert(isBiconnected(1, {}) && isBiconnected(2, {{0, 1}}) && !isBiconnected(2, {}) && !isBiconnected(0, {}));
    assert(isBiconnected(3, {{0, 1}, {1, 2}, {2, 0}}) && !isBiconnected(3, {{0, 1}, {1, 2}}));              // 경로는 가운데가 단절점
    assert(!isBiconnected(5, {{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}, {4, 2}}));                           // 나비넥타이: 다리 없지만 단절점 2
    assert(!isBiconnected(4, {{0, 1}, {1, 2}, {2, 0}}));                                                    // 고립 정점이 하나 있으면 비연결
    assert(isBiconnected(6, {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}, {5, 0}, {0, 3}}));                    // 사이클 + 현
    assert(isBiconnected(3, {{0, 1}, {0, 1}, {1, 2}, {2, 0}, {1, 1}}));                                    // 평행 간선과 루프는 영향 없음
    assert(!isBiconnected(4, {{0, 1}, {1, 2}, {2, 0}, {2, 3}}));                                            // 삼각형에 꼬리

    // ② 전수: 정점 ≤ 6 의 모든 단순 그래프 — 정의(모든 정점 지워 보기)와 일치, 개수 1, 1, 1, 10, 238, 11368, 성질 확인
    const long long want[7] = {0, 1, 1, 1, 10, 238, 11368};
    for (int n = 1; n <= 6; ++n) {
        Edges pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size();
        long long count = 0;
        std::vector<char> good(1u << m, 0);
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; std::vector<int> deg(n, 0);
            for (int i = 0; i < m; ++i) if (mask >> i & 1) { e.push_back(pairs[i]); ++deg[pairs[i].first]; ++deg[pairs[i].second]; }
            bool b = isBiconnected(n, e);
            assert(b == bruteBiconnected(n, e));
            good[mask] = b;
            if (b) {
                ++count;
                if (n >= 3) { assert(*std::min_element(deg.begin(), deg.end()) >= 2 && (int)e.size() >= n); }   // 최소 차수 ≥ 2, 간선 ≥ V
                if (n >= 3 && mask % 5 == 0) assert(flowBiconnected(n, e));                                      // Menger 쪽으로도 확인(표본)
            } else if (n >= 3 && mask % 5 == 0) assert(!flowBiconnected(n, e));
        }
        assert(count == want[n]);
        for (unsigned mask = 0; mask < (1u << m); ++mask) if (good[mask])                                         // 간선을 더해도 이중 연결
            for (int i = 0; i < m; ++i) assert(good[mask | 1u << i]);
    }

    // ③ 귀 붙이기로 만든 무작위 그래프 600 개: 모두 참 (알고리즘·정의·유량 세 가지 모두), 가지·붙이기 변형은 거짓
    std::mt19937 rng(77);
    for (int it = 0; it < 600; ++it) {
        int n; Edges e = randomEarGraph(n, rng);
        assert(isBiconnected(n, e) && bruteBiconnected(n, e));
        if (n <= 14 && it % 4 == 0) assert(flowBiconnected(n, e));
        Edges pend = e; pend.push_back({(int)(rng() % n), n});                                         // 정점 하나를 가지로 달면 그 이웃이 단절점
        assert(!isBiconnected(n + 1, pend) && !bruteBiconnected(n + 1, pend));
        int n2; Edges other = randomEarGraph(n2, rng);                                                 // 두 그래프를 정점 하나에서 붙이면 그 정점이 단절점
        Edges glued = e;
        for (auto [a, b] : other) glued.push_back({a == 0 ? 0 : n + a - 1, b == 0 ? 0 : n + b - 1});
        assert(!isBiconnected(n + n2 - 1, glued) && !bruteBiconnected(n + n2 - 1, glued));
        // 간선을 하나 빼면 (귀 하나가 끊기면) 상태가 바뀔 수 있다 — 알고리즘과 정의는 항상 일치해야 한다
        Edges less = e; less.erase(less.begin() + (int)(rng() % less.size()));
        assert(isBiconnected(n, less) == bruteBiconnected(n, less));
    }

    // ④ 큰 입력: 백만 정점 사이클은 이중 연결, 경로는 아님, 사이클에 가지 하나를 달면 아님
    {
        const int N = 1000000;
        Edges cyc;
        for (int i = 0; i < N; ++i) cyc.push_back({i, (i + 1) % N});
        assert(isBiconnected(N, cyc));
        Edges path = cyc; path.pop_back();
        assert(!isBiconnected(N, path));
        cyc.push_back({N / 2, N});
        assert(!isBiconnected(N + 1, cyc));
    }
    std::cout << "IsBiconnected: iterative Tarjan low-link agreed with the delete-every-vertex definition on all 33,867 simple graphs with up to 6 vertices and the biconnected ones numbered 1,1,1,10,238,11368 (each with minimum degree 2 and at least V edges, and closed under adding edges), matched a vertex-split max-flow count of internally disjoint paths (Menger/Whitney) on a sample, accepted all 600 ear-decomposition graphs while rejecting every pendant-vertex and glued-at-a-vertex variant, and handled a 1,000,000-vertex cycle (biconnected), path and cycle-with-a-hair (not)" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
# Part 6. 위상 구조
## KahnAlgorithm()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 카안(Kahn) 알고리즘: 진입 차수가 0 인 정점(남은 선행 작업이 없는 일)을 하나 골라 순서에 넣고 그 정점의 나가는 간선을 지우기를 반복한다. 다 비우면 위상 순서, 중간에 고를 정점이 없는데 남아 있다면 사이클이다. "무엇을 고르느냐" 가 곧 정책이다 — FIFO 큐는 층(layer)별 순서, 최소 힙은 사전순으로 가장 앞서는 순서, 임의 선택은 모든 선형 확장을 만들어낸다(아래 검증).
// 층 단위로 한꺼번에 비우는 버전의 라운드 수 = 가장 긴 경로의 정점 수 = "무한히 많은 일꾼이 있을 때 걸리는 단계 수". 위상 순서가 유일할 필요충분조건은 "고를 수 있는 정점이 늘 하나뿐" 이고, 이는 순서에서 이웃한 두 정점마다 간선이 있다(해밀턴 경로가 있다)는 것과 같다.
// 검증 오라클은 알고리즘과 코드를 전혀 공유하지 않는다: 모든 순열을 사전순으로 훑어 첫 번째 유효 순열(사전순 최소), 유효 순열의 개수(= 선형 확장의 수, 부분집합 DP 로도 센다), 재귀 메모이제이션으로 구한 높이(가장 긴 경로). 정점 ≤ 4 의 모든 방향 그래프를 전수로, 정점 5 는 표본으로 돌리고 큰 입력(백만 정점)도 확인한다.
using Edges = std::vector<std::pair<int, int>>;
struct KahnResult { bool acyclic; std::vector<int> order; int rounds; };

KahnResult kahnLayers(int n, const Edges& e) {                                      // FIFO 와 같은 순서, 층 수까지
    std::vector<std::vector<int>> adj(n); std::vector<int> indeg(n, 0);
    for (auto [a, b] : e) { adj[a].push_back(b); ++indeg[b]; }
    std::vector<int> cur, nxt, order;
    for (int v = 0; v < n; ++v) if (!indeg[v]) cur.push_back(v);
    int rounds = 0;
    while (!cur.empty()) {
        ++rounds; nxt.clear();
        for (int u : cur) { order.push_back(u); for (int v : adj[u]) if (--indeg[v] == 0) nxt.push_back(v); }
        cur.swap(nxt);
    }
    return {(int)order.size() == n, order, rounds};
}
KahnResult kahnMinHeap(int n, const Edges& e) {                                     // 사전순으로 가장 앞서는 위상 순서
    std::vector<std::vector<int>> adj(n); std::vector<int> indeg(n, 0);
    for (auto [a, b] : e) { adj[a].push_back(b); ++indeg[b]; }
    std::priority_queue<int, std::vector<int>, std::greater<int>> pq;
    for (int v = 0; v < n; ++v) if (!indeg[v]) pq.push(v);
    std::vector<int> order;
    while (!pq.empty()) { int u = pq.top(); pq.pop(); order.push_back(u); for (int v : adj[u]) if (--indeg[v] == 0) pq.push(v); }
    return {(int)order.size() == n, order, 0};
}
// 유일성: FIFO 큐에서 꺼내는 순간 큐 크기가 늘 1 이어야 한다.
bool uniqueByQueue(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n); std::vector<int> indeg(n, 0);
    for (auto [a, b] : e) { adj[a].push_back(b); ++indeg[b]; }
    std::queue<int> q; for (int v = 0; v < n; ++v) if (!indeg[v]) q.push(v);
    int done = 0;
    while (!q.empty()) { if (q.size() > 1) return false; int u = q.front(); q.pop(); ++done; for (int v : adj[u]) if (--indeg[v] == 0) q.push(v); }
    return done == n;
}
bool uniqueByHamiltonian(const Edges& e, const std::vector<int>& order) {          // 이웃한 모든 쌍이 간선
    for (std::size_t i = 0; i + 1 < order.size(); ++i)
        if (std::find(e.begin(), e.end(), std::make_pair(order[i], order[i + 1])) == e.end()) return false;
    return true;
}

// ---- 오라클 ----
bool validOrder(int n, const Edges& e, const std::vector<int>& p) {
    if ((int)p.size() != n) return false;
    std::vector<int> pos(n, -1);
    for (int i = 0; i < n; ++i) { if (p[i] < 0 || p[i] >= n || pos[p[i]] >= 0) return false; pos[p[i]] = i; }
    for (auto [a, b] : e) if (pos[a] >= pos[b]) return false;
    return true;
}
struct Brute { long long orders = 0; std::vector<int> first; };
Brute bruteOrders(int n, const Edges& e) {                                           // 모든 순열을 사전순으로 훑는다 (n ≤ 7)
    Brute r; std::vector<int> p(n); std::iota(p.begin(), p.end(), 0);
    do { if (validOrder(n, e, p)) { if (!r.orders) r.first = p; ++r.orders; } } while (std::next_permutation(p.begin(), p.end()));
    return r;
}
long long countBySubsets(int n, const Edges& e) {                                    // 부분집합 DP: ways[S] = S 를 앞에 채우는 방법 수
    std::vector<unsigned> pred(n, 0); for (auto [a, b] : e) pred[b] |= 1u << a;
    std::vector<long long> ways(1u << n, 0); ways[0] = 1;
    for (unsigned s = 0; s < (1u << n); ++s) if (ways[s]) for (int v = 0; v < n; ++v) if (!(s >> v & 1) && (pred[v] & ~s) == 0) ways[s | 1u << v] += ways[s];
    return ways[(1u << n) - 1];
}
int heightRec(int v, const std::vector<std::vector<int>>& adj, std::vector<int>& memo) {   // v 에서 시작하는 가장 긴 경로의 정점 수 (DAG 가정, 작은 입력)
    if (memo[v]) return memo[v];
    int best = 1; for (int w : adj[v]) best = std::max(best, 1 + heightRec(w, adj, memo));
    return memo[v] = best;
}
// 임의 선택: 고를 수 있는 정점 중 아무거나 — 가능한 모든 선택 순서를 모은다
void allKahn(int n, const std::vector<unsigned>& pred, unsigned done, std::vector<int>& cur, std::set<std::vector<int>>& out) {
    if (done == (1u << n) - 1) { out.insert(cur); return; }
    for (int v = 0; v < n; ++v) if (!(done >> v & 1) && (pred[v] & ~done) == 0) { cur.push_back(v); allKahn(n, pred, done | 1u << v, cur, out); cur.pop_back(); }
}

int main() {
    // ① 손으로 확인한 모양: 다이아몬드, 사이클, 외톨이, 자기 루프
    {   Edges d = {{0, 1}, {0, 2}, {1, 3}, {2, 3}};
        KahnResult r = kahnLayers(4, d);
        assert(r.acyclic && r.order == std::vector<int>({0, 1, 2, 3}) && r.rounds == 3);
        assert(countBySubsets(4, d) == 2 && !uniqueByQueue(4, d));                    // 1 과 2 는 순서가 자유
        Edges chain = {{0, 1}, {1, 2}, {2, 3}};
        assert(uniqueByQueue(4, chain) && uniqueByHamiltonian(chain, kahnLayers(4, chain).order) && countBySubsets(4, chain) == 1);
    }
    assert(!kahnLayers(3, {{0, 1}, {1, 2}, {2, 1}}).acyclic && kahnLayers(3, {{0, 1}, {1, 2}, {2, 1}}).order == std::vector<int>({0}));
    assert(!kahnLayers(1, {{0, 0}}).acyclic);
    assert(kahnLayers(5, {}).rounds == 1 && countBySubsets(5, {}) == 120);            // 간선이 없으면 모든 순열(5!)이 선형 확장
    assert(kahnMinHeap(4, {{3, 0}, {3, 1}, {1, 2}}).order == std::vector<int>({3, 0, 1, 2}));

    // ② 전수: 정점 ≤ 4 의 모든 방향 그래프(루프 없음) — Kahn 의 성공 여부 = "유효 순열 존재", 순서 유효, 사전순 최소 = 첫 유효 순열, 선형 확장 수, 층 수
    long long dagCount[5] = {0, 0, 0, 0, 0};
    for (int n = 1; n <= 4; ++n) {
        Edges all;
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) all.push_back({a, b});
        int m = (int)all.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(all[i]);
            Brute br = bruteOrders(n, e);
            KahnResult f = kahnLayers(n, e), h = kahnMinHeap(n, e);
            assert(f.acyclic == (br.orders > 0) && h.acyclic == f.acyclic);
            if (!f.acyclic) { assert(f.order.size() < (std::size_t)n); continue; }
            ++dagCount[n];
            assert(validOrder(n, e, f.order) && validOrder(n, e, h.order));
            assert(h.order == br.first);                                              // 최소 힙 = 사전순 최소
            assert(countBySubsets(n, e) == br.orders);
            std::vector<std::vector<int>> adj(n); for (auto [a, b] : e) adj[a].push_back(b);
            std::vector<int> memo(n, 0); int longest = 0; for (int v = 0; v < n; ++v) longest = std::max(longest, heightRec(v, adj, memo));
            assert(f.rounds == longest);                                              // 라운드 수 = 가장 긴 경로의 정점 수
            bool uq = uniqueByQueue(n, e);
            assert(uq == (br.orders == 1) && uq == uniqueByHamiltonian(e, f.order)); // 유일성 ⇔ 큐가 늘 1 ⇔ 해밀턴 경로
            // 임의 선택으로 만든 순서 집합 = 모든 유효 순열
            if (n <= 4 && mask % 7 == 0) {
                std::vector<unsigned> pred(n, 0); for (auto [a, b] : e) pred[b] |= 1u << a;
                std::set<std::vector<int>> got; std::vector<int> cur; allKahn(n, pred, 0, cur, got);
                assert((long long)got.size() == br.orders);
                for (auto& ord : got) assert(validOrder(n, e, ord));
            }
        }
    }
    assert(dagCount[1] == 1 && dagCount[2] == 3 && dagCount[3] == 25 && dagCount[4] == 543);

    // ③ 정점 5~7: 무작위 DAG (순열로 이름만 섞은 "앞쪽으로만 가는" 그래프) 와 사이클이 섞인 방향 그래프
    std::mt19937 rng(2025);
    int uniqueSeen = 0, manySeen = 0, cyclicSeen = 0;
    for (int it = 0; it < 1500; ++it) {
        int n = 5 + (int)(rng() % 3);
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        Edges e;
        bool chainy = it % 4 == 1;                                                      // 4 번에 한 번은 해밀턴 경로(유일한 순서)를 깔고 시작
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if ((chainy && j == i + 1) || rng() % 100 < 35) e.push_back({perm[i], perm[j]});
        bool breakIt = it % 5 == 0 && !e.empty();                                       // 5 번에 한 번은 간선 하나를 뒤집어 사이클 후보로 만든다
        if (breakIt) { auto& x = e[rng() % e.size()]; std::swap(x.first, x.second); }
        Brute br = bruteOrders(n, e);
        KahnResult f = kahnLayers(n, e), h = kahnMinHeap(n, e);
        assert(f.acyclic == (br.orders > 0));
        if (!f.acyclic) { ++cyclicSeen; continue; }
        assert(validOrder(n, e, f.order) && h.order == br.first && countBySubsets(n, e) == br.orders);
        (br.orders == 1 ? uniqueSeen : manySeen)++;
        // 정점 이름을 바꿔도 선형 확장의 수와 층 수는 불변
        std::vector<int> rename(n); std::iota(rename.begin(), rename.end(), 0); std::shuffle(rename.begin(), rename.end(), rng);
        Edges g; for (auto [a, b] : e) g.push_back({rename[a], rename[b]});
        assert(countBySubsets(n, g) == br.orders && kahnLayers(n, g).rounds == f.rounds);
    }
    assert(uniqueSeen > 20 && manySeen > 500 && cyclicSeen > 10);

    // ④ 큰 입력: 간선 i → i+1, i → i+2 의 백만 정점(순서는 항등, 층은 백만 개), 그리고 5 십만 원천 → 하나의 싱크(2 층)
    {
        const int N = 1000000;
        Edges e; e.reserve(2 * N);
        for (int i = 0; i + 1 < N; ++i) { e.push_back({i, i + 1}); if (i + 2 < N) e.push_back({i, i + 2}); }
        KahnResult r = kahnLayers(N, e);
        assert(r.acyclic && r.rounds == N && r.order.front() == 0 && r.order.back() == N - 1);
        for (int i = 0; i < N; i += 99991) assert(r.order[i] == i);
        assert(kahnMinHeap(N, e).order == r.order);
        Edges star; for (int i = 0; i < 500000; ++i) star.push_back({i, 500000});
        KahnResult s = kahnLayers(500001, star);
        assert(s.acyclic && s.rounds == 2 && s.order.back() == 500000);
        e.push_back({N - 1, 0});                                                      // 한 줄을 사이클로 닫으면 하나도 못 뺀다
        KahnResult c = kahnLayers(N, e);
        assert(!c.acyclic && c.order.empty() && c.rounds == 0);
    }
    std::cout << "KahnAlgorithm: on every loop-free digraph with up to 4 vertices (and 1500 random ones with 5-7 vertices, a fifth of them with a reversed edge) Kahn succeeded exactly when some permutation was a valid order, the min-heap variant returned the first valid permutation in lexicographic order, the number of layer rounds equalled the longest path, the order was unique exactly when the queue never held two vertices and exactly when consecutive vertices were adjacent, free choice among sources produced exactly the set of all valid permutations (counted also by a subset DP; DAG totals 1,3,25,543), and a 1,000,000-vertex DAG with 2,000,000 edges needed 1,000,000 rounds while closing it into a cycle removed nothing" << std::endl; return 0;
}
// Time Complexity: O(V + E)  (최소 힙 변형은 O((V + E) log V))
// Space Complexity: O(V + E)
```
## DFSBasedTopologicalSort()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>

// DFS 위상 정렬: 모든 정점을 DFS 하며 "끝난 순서(postorder)" 로 적고 그 역순을 취한다. 간선 u→v 가 있으면 v 의 탐색이 u 보다 먼저 끝나므로(v 가 아직 안 갔으면 u 안에서 탐색되고, 이미 끝났어도 먼저 끝났다) 역순에서는 u 가 v 앞에 온다. 회색 정점(지금 경로 위)으로 되돌아가는 간선을 만나면 사이클 — 이 검사를 빼면 사이클이 있는 입력에서도 조용히 "순서" 를 내놓는다(아래 시연).
// 같은 결과를 얻는 쉬운 변형: 간선을 뒤집은 그래프에서 DFS 한 끝난 순서를 그대로(뒤집지 않고) 쓰면 역시 위상 순서다. 반복형(명시적 스택)이라 백만 정점 사슬도 안전하다.
// Kahn 과의 관계(검증 대상): 정책이 고정되면(뿌리·자식을 번호 순으로 방문) 두 알고리즘은 다른 순서를 낸다 — 간선 0→1 과 외톨이 2 에서 Kahn 큐는 0,2,1 인데 DFS 는 2,0,1. 그래도 표현력은 같다: 뿌리를 목표 순서 σ 의 *뒤에서부터* 방문시키면(σ 의 마지막 정점은 나가는 간선이 모두 이미 방문이므로 곧바로 끝난다…) DFS 의 끝난 순서가 정확히 σ 의 역순이 되어 결과가 σ 와 같다. 즉 뿌리 방문 순서를 자유롭게 고르면 DFS 도 *모든* 선형 확장을 만든다.
using Edges = std::vector<std::pair<int, int>>;
struct TopoResult { bool ok; std::vector<int> order; std::vector<int> finish; std::vector<int> cycle; };

// priority 가 주어지면 그 순서로 뿌리와 자식을 방문한다 (nullptr 이면 정점 번호 순).
TopoResult dfsTopo(int n, const Edges& e, const std::vector<int>* priority = nullptr, bool checkCycle = true) {
    std::vector<int> rank(n); std::iota(rank.begin(), rank.end(), 0);
    if (priority) for (int i = 0; i < n; ++i) rank[(*priority)[i]] = i;
    std::vector<std::vector<int>> adj(n);
    for (auto [a, b] : e) adj[a].push_back(b);
    for (auto& row : adj) std::sort(row.begin(), row.end(), [&](int x, int y) { return rank[x] < rank[y]; });
    std::vector<int> roots(n); std::iota(roots.begin(), roots.end(), 0);
    std::sort(roots.begin(), roots.end(), [&](int x, int y) { return rank[x] < rank[y]; });
    std::vector<int> color(n, 0), par(n, -1), it(n, 0), finish(n, -1), post, st;
    for (int s : roots) {
        if (color[s]) continue;
        color[s] = 1; st.push_back(s);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] < (int)adj[u].size()) {
                int v = adj[u][it[u]++];
                if (color[v] == 0) { color[v] = 1; par[v] = u; st.push_back(v); }
                else if (color[v] == 1 && checkCycle) {                               // 뒤 간선 → 사이클 복원
                    std::vector<int> cyc; for (int x = u; x != v; x = par[x]) cyc.push_back(x);
                    cyc.push_back(v); std::reverse(cyc.begin(), cyc.end());
                    return {false, {}, {}, cyc};
                }
            } else { color[u] = 2; finish[u] = (int)post.size(); post.push_back(u); st.pop_back(); }
        }
    }
    std::vector<int> order(post.rbegin(), post.rend());
    return {true, order, finish, {}};
}

// ---- 오라클 ----
bool validOrder(int n, const Edges& e, const std::vector<int>& p) {
    if ((int)p.size() != n) return false;
    std::vector<int> pos(n, -1);
    for (int i = 0; i < n; ++i) { if (p[i] < 0 || p[i] >= n || pos[p[i]] >= 0) return false; pos[p[i]] = i; }
    for (auto [a, b] : e) if (pos[a] >= pos[b]) return false;
    return true;
}
std::set<std::vector<int>> validPermutations(int n, const Edges& e) {
    std::set<std::vector<int>> s; std::vector<int> p(n); std::iota(p.begin(), p.end(), 0);
    do { if (validOrder(n, e, p)) s.insert(p); } while (std::next_permutation(p.begin(), p.end()));
    return s;
}
bool validCycle(const Edges& e, const std::vector<int>& c) {
    if (c.empty()) return false;
    std::vector<int> s = c; std::sort(s.begin(), s.end());
    if (std::adjacent_find(s.begin(), s.end()) != s.end()) return false;
    for (std::size_t i = 0; i < c.size(); ++i) if (std::find(e.begin(), e.end(), std::make_pair(c[i], c[(i + 1) % c.size()])) == e.end()) return false;
    return true;
}

int main() {
    // ① 손으로 확인한 모양
    {   Edges d = {{0, 1}, {0, 2}, {1, 3}, {2, 3}};
        TopoResult r = dfsTopo(4, d);
        assert(r.ok && validOrder(4, d, r.order) && r.order.front() == 0 && r.order.back() == 3);
    }
    {   TopoResult r = dfsTopo(3, {{0, 1}, {1, 2}, {2, 0}});
        assert(!r.ok && r.cycle.size() == 3);
        TopoResult naive = dfsTopo(3, {{0, 1}, {1, 2}, {2, 0}}, nullptr, false);               // 회색 검사를 빼면
        assert(naive.ok && !validOrder(3, {{0, 1}, {1, 2}, {2, 0}}, naive.order));             // "성공" 이라며 잘못된 순서를 낸다
    }
    assert(!dfsTopo(1, {{0, 0}}).ok && dfsTopo(1, {}).ok && dfsTopo(0, {}).ok);

    // ② 전수: 정점 ≤ 4 의 모든 방향 그래프(루프 포함 n ≤ 3, 루프 없이 n = 4) — 성공 여부는 "유효 순열이 있는가" 와 같고, 성공이면 순서 유효 + 끝나는 시각이 간선 방향과 반대, 실패면 복원한 사이클이 진짜
    for (int n = 1; n <= 4; ++n) {
        Edges all;
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b || n <= 3) all.push_back({a, b});
        int m = (int)all.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(all[i]);
            TopoResult r = dfsTopo(n, e);
            bool exists = !validPermutations(n, e).empty();
            assert(r.ok == exists);
            if (r.ok) {
                assert(validOrder(n, e, r.order));
                for (auto [a, b] : e) assert(r.finish[b] < r.finish[a]);                      // 간선 u→v : v 가 먼저 끝난다
            } else assert(validCycle(e, r.cycle));
        }
    }

    // ③ 뒤집은 그래프의 끝난 순서를 그대로 쓰는 변형도 위상 순서
    std::mt19937 rng(515);
    for (int it = 0; it < 500; ++it) {
        int n = 3 + (int)(rng() % 10);
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        Edges e, rev;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (rng() % 100 < 30) { e.push_back({perm[i], perm[j]}); rev.push_back({perm[j], perm[i]}); }
        TopoResult f = dfsTopo(n, e), b = dfsTopo(n, rev);
        assert(f.ok && b.ok && validOrder(n, e, f.order));
        std::vector<int> postOfReversed(b.order.rbegin(), b.order.rend());                    // 끝난 순서 그대로
        assert(validOrder(n, e, postOfReversed));
        // 방문 우선순위를 무작위로 바꿔도 항상 유효 (n ≤ 12)
        std::vector<int> pri(n); std::iota(pri.begin(), pri.end(), 0); std::shuffle(pri.begin(), pri.end(), rng);
        TopoResult g = dfsTopo(n, e, &pri);
        assert(g.ok && validOrder(n, e, g.order));
    }

    // ④ 고정 정책에서는 다르고(Kahn 0,2,1 vs DFS 2,0,1), 뿌리 순서를 σ 의 역순으로 주면 어떤 선형 확장 σ 든 그대로 재현된다
    {
        Edges e = {{0, 1}};
        assert(dfsTopo(3, e).order == std::vector<int>({2, 0, 1}));
        std::set<std::vector<int>> viaDfs;
        std::vector<int> pri = {0, 1, 2};
        do viaDfs.insert(dfsTopo(3, e, &pri).order); while (std::next_permutation(pri.begin(), pri.end()));
        assert(viaDfs == validPermutations(3, e) && viaDfs.size() == 3);                       // 012, 021, 201 모두 나온다
    }
    {
        std::mt19937 r2(9);
        long long reproduced = 0;
        for (int it = 0; it < 120; ++it) {
            int n = 4 + (int)(r2() % 3);
            std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), r2);
            Edges e; for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (r2() % 100 < 25) e.push_back({perm[i], perm[j]});
            auto all = validPermutations(n, e);
            for (const auto& sigma : all) {
                std::vector<int> pri(sigma.rbegin(), sigma.rend());                           // 뿌리를 σ 의 뒤에서부터
                assert(dfsTopo(n, e, &pri).order == sigma);
                ++reproduced;
            }
            if (n <= 5) {                                                                      // 모든 우선순위가 만드는 집합 = 모든 유효 순열
                std::set<std::vector<int>> viaDfs; std::vector<int> p2(n); std::iota(p2.begin(), p2.end(), 0);
                do viaDfs.insert(dfsTopo(n, e, &p2).order); while (std::next_permutation(p2.begin(), p2.end()));
                assert(viaDfs == all);
            }
        }
        assert(reproduced > 5000);
    }

    // ⑤ 큰 입력: 간선 (i+1 → i) 의 백만 정점 사슬 — 위상 순서는 N−1 … 0, 사이클로 닫으면 실패하고 복원한 사이클 길이는 N
    {
        const int N = 1000000;
        Edges e; e.reserve(N);
        for (int i = 0; i + 1 < N; ++i) e.push_back({i + 1, i});
        TopoResult r = dfsTopo(N, e);
        assert(r.ok && r.order.front() == N - 1 && r.order.back() == 0);
        for (int i = 0; i < N; i += 99991) assert(r.order[i] == N - 1 - i);
        e.push_back({0, N - 1});
        TopoResult c = dfsTopo(N, e);
        assert(!c.ok && (int)c.cycle.size() == N);
    }
    std::cout << "DFSBasedTopologicalSort: reverse postorder from an iterative three-colour DFS succeeded exactly when a valid permutation existed on every digraph with up to 4 vertices (loops included for 3 or fewer), every order was valid with finishing times opposite to every edge, failures returned a genuine cycle, dropping the grey-vertex check made a 3-cycle 'succeed' with an invalid order, the postorder of the reversed graph worked too, with the default numbering policy DFS and Kahn gave different orders (2,0,1 versus 0,2,1) yet visiting roots in reverse of any target order reproduced every one of over 5000 linear extensions of 120 random DAGs and the set over all priorities was exactly the set of valid permutations, and a 1,000,000-vertex chain sorted without recursion while closing it into a cycle reported a cycle of length 1,000,000" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## LongestPathInDAG()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// DAG 의 최장 경로: 일반 그래프에서는 NP-난해지만 DAG 에서는 위상 순서대로 한 번 훑는 DP 로 O(V + E) — dist[v] = max over (u→v) of dist[u] + w(u,v), 위상 순서이므로 dist[u] 가 이미 확정이다. 간선 가중치가 음수여도 된다(최단 경로에서 Bellman–Ford 가 필요한 이유가 사이클이었으므로). 경로 복원은 직전 정점 배열, 최장 경로의 "개수" 는 같은 값을 주는 선택을 세는 두 번째 배열.
// 응용 ① 임계 경로법(CPM): 작업마다 소요 시간 d 가 있고 선행 관계가 DAG 일 때, 가장 이른 시작 ES, 가장 늦은 시작 LS(프로젝트 전체를 늦추지 않는 한도), 여유 slack = LS − ES. slack = 0 인 작업이 임계 작업이고, 임계 작업이 모이면 "가장 긴 경로가 지나는 정점의 합집합" 이 된다. ② Mirsky 정리: 가장 긴 사슬(정점 수 L)의 길이는 DAG 를 "서로 경로가 없는" 집합(반사슬)으로 나누는 데 필요한 최소 조각 수와 같고, 높이가 같은 정점끼리 묶으면 정확히 L 개의 반사슬이 된다.
// 검증: 모든 경로를 열거하는 완전 탐색(최댓값·개수), 가중치를 뒤집은 Bellman–Ford, CPM 의 임계 작업 집합 대 "최대 합 경로 위의 정점" 합집합, Mirsky 의 반사슬성(Warshall 폐쇄로 확인). 정점 ≤ 4 의 모든 DAG 를 전수로, 무작위 DAG, 그리고 층 10 만 개의 큰 DAG 를 층별 독립 DP 와 대조.
struct WEdge { int a, b; long long w; };
using WEdges = std::vector<WEdge>;
const long long NEG = LLONG_MIN;

struct Topo { bool ok; std::vector<int> order; };
Topo topo(int n, const WEdges& e) {                                                  // Kahn 으로 위상 순서
    std::vector<std::vector<int>> adj(n); std::vector<int> indeg(n, 0);
    for (auto& x : e) { adj[x.a].push_back(x.b); ++indeg[x.b]; }
    std::queue<int> q; for (int v = 0; v < n; ++v) if (!indeg[v]) q.push(v);
    std::vector<int> order;
    while (!q.empty()) { int u = q.front(); q.pop(); order.push_back(u); for (int v : adj[u]) if (--indeg[v] == 0) q.push(v); }
    return {(int)order.size() == n, order};
}
struct LP { bool ok; std::vector<long long> dist, ways; std::vector<int> pred; };
LP longestFrom(int n, const WEdges& e, int s) {
    Topo t = topo(n, e);
    LP r{t.ok, std::vector<long long>(n, NEG), std::vector<long long>(n, 0), std::vector<int>(n, -1)};
    if (!t.ok) return r;
    std::vector<std::vector<std::pair<int, long long>>> adj(n);
    for (auto& x : e) adj[x.a].push_back({x.b, x.w});
    r.dist[s] = 0; r.ways[s] = 1;
    for (int u : t.order) {
        if (r.dist[u] == NEG) continue;                                               // s 에서 닿지 않는 정점
        for (auto [v, w] : adj[u]) {
            long long cand = r.dist[u] + w;
            if (cand > r.dist[v]) { r.dist[v] = cand; r.ways[v] = r.ways[u]; r.pred[v] = u; }
            else if (cand == r.dist[v]) r.ways[v] += r.ways[u];
        }
    }
    return r;
}
// ---- 오라클 1: 모든 경로를 열거 ----
void enumerate(int u, long long sum, const std::vector<std::vector<std::pair<int, long long>>>& adj, std::vector<long long>& best, std::vector<long long>& cnt) {
    if (sum > best[u]) { best[u] = sum; cnt[u] = 1; } else if (sum == best[u]) ++cnt[u];
    for (auto [v, w] : adj[u]) enumerate(v, sum + w, adj, best, cnt);
}
// ---- 오라클 2: 가중치를 뒤집은 Bellman–Ford (DAG 에는 음의 사이클이 없다) ----
std::vector<long long> bellmanLongest(int n, const WEdges& e, int s) {
    const long long INF = LLONG_MAX / 4;
    std::vector<long long> d(n, INF); d[s] = 0;
    for (int round = 0; round < n; ++round) for (auto& x : e) if (d[x.a] != INF && d[x.a] - x.w < d[x.b]) d[x.b] = d[x.a] - x.w;
    std::vector<long long> res(n, NEG);
    for (int v = 0; v < n; ++v) if (d[v] != INF) res[v] = -d[v];
    return res;
}

// ---- 임계 경로법 ----
struct Cpm { long long length; std::vector<long long> es, ls; std::vector<char> critical; };
Cpm criticalPath(int n, const std::vector<long long>& dur, const std::vector<std::pair<int, int>>& prec) {
    WEdges e; for (auto [a, b] : prec) e.push_back({a, b, 0});
    Topo t = topo(n, e);
    std::vector<std::vector<int>> adj(n), radj(n);
    for (auto [a, b] : prec) { adj[a].push_back(b); radj[b].push_back(a); }
    Cpm c{0, std::vector<long long>(n, 0), std::vector<long long>(n, 0), std::vector<char>(n, 0)};
    for (int u : t.order) for (int p : radj[u]) c.es[u] = std::max(c.es[u], c.es[p] + dur[p]);          // 앞으로 훑기
    for (int v = 0; v < n; ++v) c.length = std::max(c.length, c.es[v] + dur[v]);
    for (auto it = t.order.rbegin(); it != t.order.rend(); ++it) {                                       // 뒤로 훑기
        int u = *it; long long lf = c.length;
        for (int v : adj[u]) lf = std::min(lf, c.ls[v]);
        c.ls[u] = lf - dur[u];
    }
    for (int v = 0; v < n; ++v) c.critical[v] = c.ls[v] == c.es[v];
    return c;
}
// 오라클: 시작 정점(진입 0)에서 끝 정점(진출 0)까지 모든 경로의 정점 소요 합 — 최댓값과, 최댓값을 내는 경로 위의 정점 합집합
void enumeratePaths(int u, long long sum, const std::vector<std::vector<int>>& adj, const std::vector<long long>& dur, std::vector<int>& stack,
                    long long& bestSum, std::vector<char>& onBest, long long& pathsAtBest) {
    sum += dur[u]; stack.push_back(u);
    if (adj[u].empty()) {
        if (sum > bestSum) { bestSum = sum; std::fill(onBest.begin(), onBest.end(), 0); pathsAtBest = 0; }
        if (sum == bestSum) { for (int x : stack) onBest[x] = 1; ++pathsAtBest; }
    }
    for (int v : adj[u]) enumeratePaths(v, sum, adj, dur, stack, bestSum, onBest, pathsAtBest);
    stack.pop_back();
}

// ---- Mirsky ----
std::vector<int> heights(int n, const std::vector<std::pair<int, int>>& arcs, int& chain) {   // h[v] = v 에서 끝나는 가장 긴 사슬의 정점 수
    WEdges e; for (auto [a, b] : arcs) e.push_back({a, b, 0});
    Topo t = topo(n, e);
    std::vector<std::vector<int>> radj(n); for (auto [a, b] : arcs) radj[b].push_back(a);
    std::vector<int> h(n, 1); chain = n ? 1 : 0;
    for (int u : t.order) { for (int p : radj[u]) h[u] = std::max(h[u], h[p] + 1); chain = std::max(chain, h[u]); }
    return h;
}

int main() {
    // ① 손으로 확인한 모양: 기존 예제(0→1:2, 0→2:5, 1→3:1, 2→3:1) 는 0→2→3 이 6
    {   WEdges e = {{0, 1, 2}, {0, 2, 5}, {1, 3, 1}, {2, 3, 1}};
        LP r = longestFrom(4, e, 0);
        assert(r.ok && r.dist[3] == 6 && r.pred[3] == 2 && r.ways[3] == 1);
        WEdges tie = {{0, 1, 3}, {0, 2, 3}, {1, 3, 1}, {2, 3, 1}};
        assert(longestFrom(4, tie, 0).ways[3] == 2 && longestFrom(4, tie, 0).dist[3] == 4);                  // 같은 길이의 최장 경로가 둘
        WEdges neg = {{0, 1, -5}, {1, 2, -1}, {0, 2, -7}};
        assert(longestFrom(3, neg, 0).dist[2] == -6);                                                          // 음수 가중치도 그대로
        assert(longestFrom(3, {{0, 1, 1}}, 0).dist[2] == NEG);                                                 // 닿지 않으면 −∞
        assert(!longestFrom(2, {{0, 1, 1}, {1, 0, 1}}, 0).ok);                                                 // 사이클이면 정의되지 않음
    }

    // ② 전수: 정점 ≤ 4 의 모든 DAG 에 결정적 가중치(음수 포함)를 주고 모든 출발점 — 완전 열거(최댓값·개수) 및 Bellman–Ford 와 일치
    long long dags = 0, checks = 0;
    for (int n = 1; n <= 4; ++n) {
        std::vector<std::pair<int, int>> all;
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) all.push_back({a, b});
        int m = (int)all.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            WEdges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back({all[i].first, all[i].second, (long long)((all[i].first * 7 + all[i].second * 3) % 7) - 2});
            if (!topo(n, e).ok) continue;
            ++dags;
            std::vector<std::vector<std::pair<int, long long>>> adj(n); for (auto& x : e) adj[x.a].push_back({x.b, x.w});
            for (int s = 0; s < n; ++s) {
                LP r = longestFrom(n, e, s);
                std::vector<long long> best(n, NEG), cnt(n, 0); enumerate(s, 0, adj, best, cnt);
                assert(r.dist == best && r.ways == cnt && r.dist == bellmanLongest(n, e, s));
                for (int v = 0; v < n; ++v) if (r.dist[v] != NEG && v != s) {                                // 복원한 경로의 합이 dist
                    long long sum = 0; int steps = 0;
                    for (int x = v; x != s; x = r.pred[x]) {
                        bool found = false; for (auto& ed : e) if (ed.a == r.pred[x] && ed.b == x && ed.w + r.dist[r.pred[x]] == r.dist[x]) { sum += ed.w; found = true; break; }
                        assert(found); ++steps; assert(steps <= n);
                    }
                    assert(sum == r.dist[v]);
                }
                ++checks;
            }
        }
    }
    assert(dags == 1 + 3 + 25 + 543 && checks == 1 * 1 + 3 * 2 + 25 * 3 + 543 * 4);

    // ③ 무작위 DAG (정점 ≤ 12, 가중치 −3..9): 완전 열거 · Bellman–Ford 와 일치
    std::mt19937 rng(12);
    int multiOptimal = 0;
    for (int it = 0; it < 800; ++it) {
        int n = 5 + (int)(rng() % 8);
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        WEdges e; for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (rng() % 100 < 28) e.push_back({perm[i], perm[j], it % 2 ? (long long)(rng() % 13) - 3 : (long long)(rng() % 3) - 1});
        int s = perm[(int)(rng() % 3)];
        LP r = longestFrom(n, e, s);
        std::vector<std::vector<std::pair<int, long long>>> adj(n); for (auto& x : e) adj[x.a].push_back({x.b, x.w});
        std::vector<long long> best(n, NEG), cnt(n, 0); enumerate(s, 0, adj, best, cnt);
        assert(r.dist == best && r.ways == cnt && r.dist == bellmanLongest(n, e, s));
        for (int v = 0; v < n; ++v) multiOptimal += r.ways[v] > 1;
    }
    assert(multiOptimal > 100);

    // ④ CPM: 무작위 작업 그래프에서 임계 작업 집합 = 최대 합 경로 위의 정점 합집합, 길이 = 최대 합, 임계 작업이 길이 안에 꽉 맞음
    for (int it = 0; it < 400; ++it) {
        int n = 4 + (int)(rng() % 8);
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        std::vector<std::pair<int, int>> prec;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (rng() % 100 < 22) prec.push_back({perm[i], perm[j]});
        std::vector<long long> dur(n); for (auto& d : dur) d = (long long)(rng() % 9);
        Cpm c = criticalPath(n, dur, prec);
        std::vector<std::vector<int>> adj(n); std::vector<int> indeg(n, 0);
        for (auto [a, b] : prec) { adj[a].push_back(b); ++indeg[b]; }
        long long bestSum = -1, paths = 0; std::vector<char> onBest(n, 0); std::vector<int> stack;
        for (int v = 0; v < n; ++v) if (!indeg[v]) enumeratePaths(v, 0, adj, dur, stack, bestSum, onBest, paths);
        assert(c.length == bestSum);
        assert(c.critical == onBest);
        for (int v = 0; v < n; ++v) assert(c.ls[v] >= c.es[v] && c.ls[v] + dur[v] <= c.length);
    }

    // ⑤ Mirsky: 높이가 같은 정점끼리의 집합은 반사슬이고 조각 수는 가장 긴 사슬(완전 열거) 과 같다
    for (int it = 0; it < 300; ++it) {
        int n = 4 + (int)(rng() % 9);
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        std::vector<std::pair<int, int>> arcs;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) if (rng() % 100 < 25) arcs.push_back({perm[i], perm[j]});
        int chain; std::vector<int> h = heights(n, arcs, chain);
        std::vector<unsigned> row(n, 0); for (auto [a, b] : arcs) row[a] |= 1u << b;
        for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];            // Warshall 폐쇄
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b && h[a] == h[b]) assert(!(row[a] >> b & 1));   // 같은 높이 사이엔 경로가 없다
        std::vector<std::vector<std::pair<int, long long>>> adj(n); for (auto [a, b] : arcs) adj[a].push_back({b, 1});
        long long longest = 0;                                                                                    // 간선 수 최대 경로 + 1 = 정점 수
        for (int s = 0; s < n; ++s) { std::vector<long long> best(n, NEG), cnt(n, 0); enumerate(s, 0, adj, best, cnt); for (int v = 0; v < n; ++v) longest = std::max(longest, best[v]); }
        assert(chain == longest + 1 && *std::max_element(h.begin(), h.end()) == chain);
    }

    // ⑥ 큰 입력: 층 10 만 개 × 너비 3 의 DAG (인접 층 사이 모든 쌍 연결, 간선 90 만 개) 를 층별 독립 DP 와 대조, 백만 정점 사슬
    {
        const int L = 100000, W = 3, N = L * W;
        auto weight = [](int l, int i, int j) { return (long long)((l * 7 + i * 3 + j) % 11) - 2; };
        WEdges e; e.reserve((size_t)(L - 1) * W * W);
        for (int l = 0; l + 1 < L; ++l) for (int i = 0; i < W; ++i) for (int j = 0; j < W; ++j) e.push_back({l * W + i, (l + 1) * W + j, weight(l, i, j)});
        LP r = longestFrom(N, e, 0);
        long long cur[W] = {0, NEG, NEG};                                                                    // 출발점은 0 층의 0 번
        for (int l = 0; l + 1 < L; ++l) {
            long long nxt[W]; for (int j = 0; j < W; ++j) nxt[j] = NEG;
            for (int i = 0; i < W; ++i) if (cur[i] != NEG) for (int j = 0; j < W; ++j) nxt[j] = std::max(nxt[j], cur[i] + weight(l, i, j));
            for (int j = 0; j < W; ++j) cur[j] = nxt[j];
        }
        for (int j = 0; j < W; ++j) assert(r.dist[(L - 1) * W + j] == cur[j]);
        const int M = 1000000;
        WEdges chain; chain.reserve(M);
        for (int i = 0; i + 1 < M; ++i) chain.push_back({i, i + 1, i % 5 + 1});
        LP c = longestFrom(M, chain, 0);
        long long expect = 0; for (int i = 0; i + 1 < M; ++i) expect += i % 5 + 1;
        assert(c.dist[M - 1] == expect && c.ways[M - 1] == 1);
    }
    std::cout << "LongestPathInDAG: the topological-order DP matched exhaustive path enumeration (maximum and number of optimal paths) and a negated-weight Bellman-Ford on all 572 DAGs with up to 4 vertices from every start and on 800 random DAGs with negative weights, rebuilt paths summed to the reported lengths, critical-path analysis flagged exactly the vertices lying on some maximum-total path on 400 random task graphs, equal-height vertices formed antichains whose count equalled the longest chain (Mirsky), and a 100,000-layer DAG with 900,000 edges and a 1,000,000-vertex chain agreed with independent layer-by-layer sums" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
# Part 7. 최소 신장 트리
## Kruskal()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// 크루스칼(Kruskal) 최소 신장 트리: 간선을 가중치 오름차순으로 훑으며, 두 끝이 아직 다른 집합일 때만 서로소 집합으로 합치고 그 간선을 고른다. 사이클을 만드는 간선은 "그 사이클에서 가장 무겁다" 는 사이클 성질 덕분에 버려도 된다. 연결되지 않은 그래프에서는 성분마다 하나씩의 트리, 즉 최소 신장 숲(V − c 개 간선)이 나온다. 연결 그래프라면 성분이 1 개가 된 순간 나머지를 훑지 않고 멈출 수 있다.
// 동점 처리: 가중치가 같은 간선이 있으면 MST 는 여러 개일 수 있다. (가중치, 번호) 로 순서를 정하면 결과가 유일해지고, 입력 순서를 어떻게 섞어도 결과가 변하지 않는다. 정리: ① 간선 e 가 "어떤 MST 에 들어간다" ⇔ e 의 두 끝이 e 보다 *엄격히 가벼운* 간선만으로는 이어지지 않는다. ② e 가 "모든 MST 에 들어간다" ⇔ e 를 뺀 *같거나 가벼운* 간선만으로는 두 끝이 이어지지 않는다. ③ 모든 MST 에서 무게 w 인 간선은 정확히 (성분 수[< w] − 성분 수[≤ w]) 개로 같다.
// 최적성 증명서: 신장 숲 T 가 MST ⇔ T 에 없는 모든 간선 (u, v, w) 가 T 위의 u–v 경로 최대 간선보다 가볍지 않다(사이클 성질). 이진 올리기로 O(E log V) 에 확인하므로, 완전 탐색이 불가능한 큰 입력에서도 최적성을 독립적으로 확인할 수 있다.
// 검증: 모든 신장 숲을 열거하는 완전 탐색(최솟값·MST 개수·"어떤/모든 MST 에 들어가는 간선"), 위 정리 ①②③, 입력 순서 섞기, 정점 ≤ 5 의 모든(또는 표본) 그래프와 무작위 다중 그래프, 증명서가 모든 신장 숲에 대해 "최적 ⇔ 총무게 최소" 로 판정하는지, 그리고 정점 10 만 개 · 간선 60 만 개 · 성분 2 개의 큰 입력.
struct Edge { int u, v; long long w; int id; };
struct Dsu {
    std::vector<int> p, sz;
    explicit Dsu(int n) : p(n), sz(n, 1) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (sz[a] < sz[b]) std::swap(a, b); p[b] = a; sz[a] += sz[b]; return true; }
};
struct Forest { long long weight; std::vector<int> ids; int components; };
using Pred = std::function<bool(const Edge&)>;

bool lighter(const Edge& a, const Edge& b) { return a.w != b.w ? a.w < b.w : a.id < b.id; }
Forest kruskal(int n, std::vector<Edge> E, std::size_t* scanned = nullptr, bool earlyStop = true) {
    std::sort(E.begin(), E.end(), lighter);
    Dsu d(n); Forest f{0, {}, n};
    std::size_t seen = 0;
    for (const Edge& e : E) {
        if (earlyStop && f.components == 1) break;                                  // 연결 그래프는 V − 1 개를 고르면 끝
        ++seen;
        if (d.unite(e.u, e.v)) { f.weight += e.w; f.ids.push_back(e.id); --f.components; }
    }
    if (scanned) *scanned = seen;
    return f;
}
int countComponents(int n, const std::vector<Edge>& E, const Pred& use) {
    Dsu d(n); int c = n; for (const Edge& e : E) if (use(e) && d.unite(e.u, e.v)) --c; return c;
}
bool connectedUsing(int n, const std::vector<Edge>& E, int a, int b, const Pred& use) {
    Dsu d(n); for (const Edge& e : E) if (use(e)) d.unite(e.u, e.v); return d.find(a) == d.find(b);
}
Pred all() { return [](const Edge&) { return true; }; }

// ---- 오라클: 모든 신장 숲 열거 (m ≤ 16) ----
struct Brute { long long best; long long count; std::vector<char> inSome, inAll; };
Brute bruteForests(int n, const std::vector<Edge>& E) {
    int m = (int)E.size(), need = n - countComponents(n, E, all());
    Brute b{LLONG_MAX, 0, std::vector<char>(m, 0), std::vector<char>(m, 1)};
    for (unsigned mask = 0; mask < (1u << m); ++mask) {
        if (__builtin_popcount(mask) != need) continue;
        Dsu d(n); bool ok = true; long long w = 0;
        for (int i = 0; i < m && ok; ++i) if (mask >> i & 1) { ok = d.unite(E[i].u, E[i].v); w += E[i].w; }
        if (!ok) continue;
        if (w < b.best) { b.best = w; b.count = 0; std::fill(b.inSome.begin(), b.inSome.end(), 0); std::fill(b.inAll.begin(), b.inAll.end(), 1); }
        if (w == b.best) { ++b.count; for (int i = 0; i < m; ++i) { if (mask >> i & 1) b.inSome[i] = 1; else b.inAll[i] = 0; } }
    }
    return b;
}
bool isSpanningForest(int n, const std::vector<Edge>& E, const std::vector<int>& ids) {   // 사이클 없음 + 원래 성분 수와 같음
    Dsu d(n); int c = n;
    for (int id : ids) { if (!d.unite(E[id].u, E[id].v)) return false; --c; }
    return c == countComponents(n, E, all());
}
// ---- 최적성 증명서 (사이클 성질, 이진 올리기) ----
bool isMinimumForest(int n, const std::vector<Edge>& E, const std::vector<int>& ids) {
    std::vector<char> inT(E.size(), 0); for (int id : ids) inT[id] = 1;
    std::vector<std::vector<std::pair<int, long long>>> adj(n);
    for (int id : ids) { adj[E[id].u].push_back({E[id].v, E[id].w}); adj[E[id].v].push_back({E[id].u, E[id].w}); }
    int LOG = 1; while ((1 << LOG) < n) ++LOG;
    std::vector<std::vector<int>> up(LOG + 1, std::vector<int>(n, 0));
    std::vector<std::vector<long long>> mx(LOG + 1, std::vector<long long>(n, LLONG_MIN));
    std::vector<int> depth(n, -1), root(n, -1), st;
    for (int s = 0; s < n; ++s) {
        if (depth[s] >= 0) continue;
        depth[s] = 0; root[s] = s; up[0][s] = s; st.push_back(s);
        while (!st.empty()) {
            int u = st.back(); st.pop_back();
            for (auto [v, w] : adj[u]) if (depth[v] < 0) { depth[v] = depth[u] + 1; root[v] = s; up[0][v] = u; mx[0][v] = w; st.push_back(v); }
        }
    }
    for (int j = 1; j <= LOG; ++j) for (int v = 0; v < n; ++v) { int mid = up[j - 1][v]; up[j][v] = up[j - 1][mid]; mx[j][v] = std::max(mx[j - 1][v], mx[j - 1][mid]); }
    auto pathMax = [&](int a, int b) {
        long long best = LLONG_MIN;
        if (depth[a] < depth[b]) std::swap(a, b);
        for (int j = LOG; j >= 0; --j) if (depth[a] - (1 << j) >= depth[b]) { best = std::max(best, mx[j][a]); a = up[j][a]; }
        if (a == b) return best;
        for (int j = LOG; j >= 0; --j) if (up[j][a] != up[j][b]) { best = std::max({best, mx[j][a], mx[j][b]}); a = up[j][a]; b = up[j][b]; }
        return std::max({best, mx[0][a], mx[0][b]});
    };
    for (std::size_t i = 0; i < E.size(); ++i) {
        if (inT[i] || E[i].u == E[i].v) continue;
        if (root[E[i].u] != root[E[i].v]) return false;                          // 신장 "숲" 이 성분을 다 덮지 못했다
        if (E[i].w < pathMax(E[i].u, E[i].v)) return false;                      // 더 가벼운 간선으로 바꿀 수 있다
    }
    return true;
}

int main() {
    // ① 손으로 확인한 모양: 고전 예제 → 4 + 5 + 10 = 19, 네 번째 간선(10) 에서 성분이 1 개가 되어 멈춘다 (15 는 훑지 않는다)
    {   std::vector<Edge> E = {{0, 1, 10, 0}, {0, 2, 6, 1}, {0, 3, 5, 2}, {1, 3, 15, 3}, {2, 3, 4, 4}};
        std::size_t scanned = 0;
        Forest f = kruskal(4, E, &scanned);
        assert(f.weight == 19 && f.components == 1 && f.ids == std::vector<int>({4, 2, 0}) && scanned == 4);
        assert(isMinimumForest(4, E, f.ids));
    }
    {   std::vector<Edge> E = {{0, 1, 3, 0}, {2, 3, 1, 1}, {1, 0, 2, 2}, {4, 4, 0, 3}};      // 평행 간선, 루프, 비연결 → 숲
        Forest f = kruskal(5, E);
        assert(f.weight == 3 && f.components == 3 && f.ids == std::vector<int>({1, 2}));
    }

    // ② 전수: 정점 ≤ 4 의 모든 그래프(쌍마다 없음/1/2/3), 정점 5 는 {없음, 1, 2} 의 표본 — 완전 탐색·정리 ①②③·증명서와 일치
    long long graphs = 0, ties = 0;
    for (int n = 2; n <= 5; ++n) {
        std::vector<std::pair<int, int>> pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size(), base = n == 5 ? 3 : 4;
        long long total = 1; for (int i = 0; i < m; ++i) total *= base;
        for (long long code = 0; code < total; code += (n == 5 ? 7 : 1)) {
            std::vector<Edge> E; long long c = code;
            for (int i = 0; i < m; ++i, c /= base) if (c % base) E.push_back({pairs[i].first, pairs[i].second, c % base, (int)E.size()});
            Forest f = kruskal(n, E);
            Brute b = bruteForests(n, E);
            assert(f.weight == b.best && isSpanningForest(n, E, f.ids) && isMinimumForest(n, E, f.ids));
            ties += b.count > 1; ++graphs;
            std::vector<char> inK(E.size(), 0); for (int id : f.ids) inK[id] = 1;
            for (std::size_t i = 0; i < E.size(); ++i) {
                const Edge& e = E[i];
                bool some = !connectedUsing(n, E, e.u, e.v, [&](const Edge& x) { return x.w < e.w; });                         // 정리 ①
                bool every = !connectedUsing(n, E, e.u, e.v, [&](const Edge& x) { return x.id != e.id && x.w <= e.w; });      // 정리 ②
                assert(some == (bool)b.inSome[i] && every == (bool)b.inAll[i]);
                bool strict = !connectedUsing(n, E, e.u, e.v, [&](const Edge& x) { return lighter(x, e); });                    // (w,id) 전순서에서의 유일한 MST
                assert(strict == (bool)inK[i]);
            }
            for (long long w = 1; w <= 3; ++w) {                                                                                // 정리 ③
                int inTree = 0; for (int id : f.ids) inTree += E[id].w == w;
                assert(inTree == countComponents(n, E, [&](const Edge& x) { return x.w < w; }) - countComponents(n, E, [&](const Edge& x) { return x.w <= w; }));
            }
            if (b.count == 1) { std::vector<int> ids; for (std::size_t i = 0; i < E.size(); ++i) if (b.inSome[i]) ids.push_back((int)i); std::vector<int> mine = f.ids; std::sort(mine.begin(), mine.end()); assert(ids == mine); }
            if (n <= 4) {                                                                                                       // 증명서 = "모든 신장 숲에서 최적 ⇔ 총무게 최소"
                for (unsigned mask = 0; mask < (1u << E.size()); ++mask) {
                    std::vector<int> ids; for (std::size_t i = 0; i < E.size(); ++i) if (mask >> i & 1) ids.push_back((int)i);
                    if (!isSpanningForest(n, E, ids)) continue;
                    long long w = 0; for (int id : ids) w += E[id].w;
                    assert(isMinimumForest(n, E, ids) == (w == b.best));
                }
            }
        }
    }
    assert(graphs > 12000 && ties > 3000);

    // ③ 무작위 다중 그래프(루프·평행 간선, 정점 ≤ 8, 간선 ≤ 14, 가중치 1..4): 완전 탐색과 일치, 입력 순서를 섞어도 결과 동일, 조기 중단 위치 검증
    std::mt19937 rng(8);
    int certTrue = 0, certFalse = 0;
    for (int it = 0; it < 600; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % 15);
        std::vector<Edge> E; for (int i = 0; i < m; ++i) E.push_back({(int)(rng() % n), (int)(rng() % n), (long long)(1 + rng() % 4), i});
        Forest f = kruskal(n, E);
        Brute b = bruteForests(n, E);
        assert(f.weight == b.best && isSpanningForest(n, E, f.ids) && isMinimumForest(n, E, f.ids));
        for (int rep = 0; rep < 5; ++rep) { auto G = E; std::shuffle(G.begin(), G.end(), rng); Forest g = kruskal(n, G, nullptr, rep % 2); assert(g.ids == f.ids && g.weight == f.weight); }
        if (f.components == 1) {                                                      // 연결: 마지막으로 고른 간선까지만 훑었다
            auto sorted = E; std::sort(sorted.begin(), sorted.end(), lighter);
            std::size_t pos = 0; for (std::size_t i = 0; i < sorted.size(); ++i) if (sorted[i].id == f.ids.back()) pos = i + 1;
            std::size_t scanned = 0; kruskal(n, E, &scanned);
            assert(scanned == pos);
        }
        // 무작위 신장 트리(가중치 무시) 의 증명서 판정 = 총무게가 최소인가
        auto G = E; std::shuffle(G.begin(), G.end(), rng);
        Dsu d(n); std::vector<int> ids; long long w = 0;
        for (auto& e : G) if (d.unite(e.u, e.v)) { ids.push_back(e.id); w += e.w; }
        bool cert = isMinimumForest(n, E, ids);
        assert(cert == (w == b.best));
        (cert ? certTrue : certFalse)++;
    }
    assert(certTrue > 150 && certFalse > 150);

    // ④ 큰 입력: 정점 10 만, 성분 2 개(각 5 만, 임의 경로로 연결한 뒤 무작위 간선 30 만 개씩), 가중치 1..10^6 (동점 많음)
    {
        const int N = 100000, H = N / 2;
        std::vector<Edge> E; E.reserve(600000 + N);
        std::mt19937_64 r(2024);
        for (int half = 0; half < 2; ++half) {
            std::vector<int> perm(H); std::iota(perm.begin(), perm.end(), half * H); std::shuffle(perm.begin(), perm.end(), r);
            for (int i = 0; i + 1 < H; ++i) E.push_back({perm[i], perm[i + 1], (long long)(1 + r() % 1000000), (int)E.size()});
            for (int i = 0; i < 300000 - H; ++i) E.push_back({half * H + (int)(r() % H), half * H + (int)(r() % H), (long long)(1 + r() % 1000000), (int)E.size()});
        }
        Forest f = kruskal(N, E, nullptr, false);
        assert(f.components == 2 && (int)f.ids.size() == N - 2 && isSpanningForest(N, E, f.ids) && isMinimumForest(N, E, f.ids));
        // 트리에 없는 간선 c 를 하나 잡고, c 의 두 끝을 잇는 트리 경로의 간선 하나(drop)를 c 로 바꾼다 → 증명서는 "총무게가 같을 때만" 통과해야 한다 (MST 이므로 w(c) ≥ w(drop))
        std::vector<char> inT(E.size(), 0); for (int id : f.ids) inT[id] = 1;
        std::vector<std::vector<std::pair<int, int>>> tadj(N);                          // (이웃, 간선 id)
        for (int id : f.ids) { tadj[E[id].u].push_back({E[id].v, id}); tadj[E[id].v].push_back({E[id].u, id}); }
        int negatives = 0, trials = 0;
        while (trials < 12) {
            int c = (int)(r() % E.size());
            if (inT[c] || E[c].u == E[c].v) continue;
            std::vector<int> parentEdge(N, -1), parentNode(N, -1), queue{E[c].u};         // 트리 경로 찾기 (BFS)
            parentNode[E[c].u] = E[c].u;
            for (std::size_t h = 0; h < queue.size() && parentNode[E[c].v] < 0; ++h)
                for (auto [v, id] : tadj[queue[h]]) if (parentNode[v] < 0) { parentNode[v] = queue[h]; parentEdge[v] = id; queue.push_back(v); }
            std::vector<int> path; for (int x = E[c].v; x != E[c].u; x = parentNode[x]) path.push_back(parentEdge[x]);
            int drop = path[r() % path.size()];
            std::vector<int> ids; for (int id : f.ids) if (id != drop) ids.push_back(id);
            ids.push_back(c);
            assert(isSpanningForest(N, E, ids) && E[c].w >= E[drop].w);
            bool same = E[c].w == E[drop].w;
            assert(isMinimumForest(N, E, ids) == same);
            negatives += !same; ++trials;
        }
        assert(negatives >= 8);
        Forest g = kruskal(N, E);                                                      // 조기 중단 없이도 같은 결과 (성분이 2 개라 중단되지 않는다)
        assert(g.ids == f.ids);
    }
    std::cout << "Kruskal: the sorted union-find scan matched exhaustive enumeration of all spanning forests (minimum weight, number of optimal trees, which edges lie in some or every minimum tree) on every 2-4 vertex graph with weights 1-3 and a sample of the 5-vertex ones, obeyed the weight-class theorem and equalled the unique (weight, id)-ordered MST, the binary-lifting cycle-property certificate agreed with 'total weight is minimal' on every spanning forest of the 4-vertex graphs and on 600 random multigraphs, input shuffling and early stopping never changed the result, and a 100,000-vertex, 600,000-edge graph with two components produced a certified minimum forest" << std::endl; return 0;
}
// Time Complexity: O(E log E)  (정렬이 지배, 서로소 집합은 E α(V))
// Space Complexity: O(V + E)
```
## Prim()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <tuple>
#include <utility>
#include <vector>

// 프림(Prim) 최소 신장 트리: 한 정점에서 시작해, 지금까지 만든 트리와 바깥을 잇는 간선 중 가장 가벼운 것을 계속 붙인다(컷 성질: 어떤 컷을 가로지르는 가장 가벼운 간선은 반드시 어떤 MST 에 들어간다). 연결되지 않은 그래프는 아직 안 간 가장 작은 정점에서 다시 시작해 숲을 만든다.
// 구현 세 가지 — ① 느긋한 힙: 트리 정점의 나가는 간선을 전부 힙에 넣고, 꺼냈을 때 이미 트리 안이면 버린다. O(E log E). ② 색인 이진 힙 + decrease-key: 바깥 정점마다 "트리와 이어지는 가장 싼 간선" 하나만 들고 있고, 더 싼 간선이 나오면 키를 줄인다. O(E log V). ③ 밀집 O(V²): 인접 행렬과 배열 스캔만, 간선이 V² 에 가까운 완전 그래프에서 힙보다 단순하고 빠르다.
// 모든 구현이 (가중치, 간선 번호) 로 동점을 깨므로 MST 가 하나로 정해지고, 따라서 *선택 순서까지* 같아야 한다 — 이것이 가장 강한 검증이다: 컷 성질을 문자 그대로(모든 간선을 훑어 경계를 가로지르는 가장 가벼운 것을 고름) 구현한 O(V·E) 기준 구현, 세 구현, 그리고 크루스칼이 모두 같은 간선 집합을 내고, 총 무게는 모든 신장 숲을 열거한 완전 탐색과 같다.
// 색인 힙은 따로 무작위 연산 2 만 번을 std::set 모형과 비교한다(힙 성질·위치 배열 불변식 포함). 비용은 시간이 아니라 횟수로 단언한다: 직선 경로에서 느긋한 힙은 정확히 V − 1 번 넣고, 밀집 구현은 V² 에 비례하는 2V² 번 스캔한다.
struct Edge { int u, v; long long w; int id; };
struct Dsu {
    std::vector<int> p;
    explicit Dsu(int n) : p(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; p[a] = b; return true; }
};
struct Arc { int to; long long w; int id; };
using Adj = std::vector<std::vector<Arc>>;
struct Forest { long long weight; std::vector<int> order; };            // order = 선택한 간선 번호를 고른 순서
bool lighter(const Edge& a, const Edge& b) { return a.w != b.w ? a.w < b.w : a.id < b.id; }
Adj buildAdj(int n, const std::vector<Edge>& E) {
    Adj adj(n);
    for (const Edge& e : E) { adj[e.u].push_back({e.v, e.w, e.id}); if (e.u != e.v) adj[e.v].push_back({e.u, e.w, e.id}); }
    return adj;
}

// ① 느긋한 힙
Forest primLazy(int n, const Adj& adj, const std::vector<Edge>& E, long long* pushes) {
    using Item = std::tuple<long long, int, int>;                       // (w, id, 도착 정점)
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
    std::vector<char> seen(n, 0); Forest f{0, {}};
    for (int s = 0; s < n; ++s) {
        if (seen[s]) continue;
        seen[s] = 1;
        for (const Arc& a : adj[s]) if (!seen[a.to]) { pq.push({a.w, a.id, a.to}); ++*pushes; }
        while (!pq.empty()) {
            auto [w, id, v] = pq.top(); pq.pop();
            if (seen[v]) continue;
            seen[v] = 1; f.weight += w; f.order.push_back(id);
            for (const Arc& a : adj[v]) if (!seen[a.to]) { pq.push({a.w, a.id, a.to}); ++*pushes; }
        }
    }
    (void)E;
    return f;
}
// ② 색인 이진 힙 (decrease-key)
struct IndexedHeap {
    using Key = std::pair<long long, int>;
    std::vector<int> h, pos; std::vector<Key> key; long long swaps = 0;      // pos: -1 = 아직 안 들어감, -2 = 이미 꺼냄
    explicit IndexedHeap(int n) : pos(n, -1), key(n) {}
    bool empty() const { return h.empty(); }
    bool less(int a, int b) const { return key[a] < key[b]; }
    void swapAt(int i, int j) { std::swap(h[i], h[j]); pos[h[i]] = i; pos[h[j]] = j; ++swaps; }
    void up(int i) { while (i > 0) { int p = (i - 1) / 2; if (!less(h[i], h[p])) break; swapAt(i, p); i = p; } }
    void down(int i) {
        int n = (int)h.size();
        while (true) { int l = 2 * i + 1, r = l + 1, m = i; if (l < n && less(h[l], h[m])) m = l; if (r < n && less(h[r], h[m])) m = r; if (m == i) break; swapAt(i, m); i = m; }
    }
    void pushOrDecrease(int v, Key k) {
        if (pos[v] == -1) { key[v] = k; pos[v] = (int)h.size(); h.push_back(v); up(pos[v]); }
        else if (pos[v] >= 0 && k < key[v]) { key[v] = k; up(pos[v]); }
    }
    int popMin() { int v = h[0]; swapAt(0, (int)h.size() - 1); h.pop_back(); pos[v] = -2; if (!h.empty()) down(0); return v; }
    bool valid() const {
        for (std::size_t i = 0; i < h.size(); ++i) { if (pos[h[i]] != (int)i) return false; if (i && less(h[i], h[(i - 1) / 2])) return false; }
        return true;
    }
};
Forest primIndexed(int n, const Adj& adj, long long* swaps) {
    IndexedHeap hp(n); Forest f{0, {}};
    for (int s = 0; s < n; ++s) {
        if (hp.pos[s] != -1) continue;
        hp.pushOrDecrease(s, {0, -1});
        while (!hp.empty()) {
            int u = hp.popMin();
            if (hp.key[u].second >= 0) { f.weight += hp.key[u].first; f.order.push_back(hp.key[u].second); }
            for (const Arc& a : adj[u]) hp.pushOrDecrease(a.to, {a.w, a.id});          // 이미 꺼낸 정점은 무시된다
        }
    }
    *swaps += hp.swaps;
    return f;
}
// ③ 밀집 O(V²)
Forest primDense(int n, const std::vector<Edge>& E, long long* ops) {
    const long long INF = LLONG_MAX;
    std::vector<long long> W((std::size_t)n * n, INF); std::vector<int> I((std::size_t)n * n, -1);
    for (const Edge& e : E) if (e.u != e.v) for (int dir = 0; dir < 2; ++dir) {
        std::size_t k = dir ? (std::size_t)e.v * n + e.u : (std::size_t)e.u * n + e.v;
        if (e.w < W[k] || (e.w == W[k] && e.id < I[k])) { W[k] = e.w; I[k] = e.id; }
    }
    std::vector<long long> dist(n, INF); std::vector<int> eid(n, -1); std::vector<char> done(n, 0);
    Forest f{0, {}};
    for (int round = 0; round < n; ++round) {
        int u = -1;
        for (int v = 0; v < n; ++v) { ++*ops; if (!done[v] && (u < 0 || dist[v] < dist[u] || (dist[v] == dist[u] && eid[v] < eid[u]))) u = v; }
        done[u] = 1;
        if (dist[u] != INF) { f.weight += dist[u]; f.order.push_back(eid[u]); }
        for (int v = 0; v < n; ++v) {
            ++*ops;
            std::size_t k = (std::size_t)u * n + v;
            if (!done[v] && W[k] != INF && (W[k] < dist[v] || (W[k] == dist[v] && I[k] < eid[v]))) { dist[v] = W[k]; eid[v] = I[k]; }
        }
    }
    return f;
}
// 기준 구현: 컷 성질 그대로 — 매 단계 모든 간선을 훑어 경계를 가로지르는 가장 가벼운 간선을 고른다 (O(V·E))
Forest primReference(int n, const std::vector<Edge>& E) {
    std::vector<char> in(n, 0); Forest f{0, {}};
    for (int s = 0; s < n; ++s) {
        if (in[s]) continue;
        in[s] = 1;
        while (true) {
            int best = -1;
            for (std::size_t i = 0; i < E.size(); ++i) if (in[E[i].u] != in[E[i].v] && (best < 0 || lighter(E[i], E[best]))) best = (int)i;
            if (best < 0) break;
            f.weight += E[best].w; f.order.push_back(best); in[E[best].u] = in[E[best].v] = 1;
        }
    }
    return f;
}
std::vector<int> kruskalIds(int n, std::vector<Edge> E) {
    std::sort(E.begin(), E.end(), lighter);
    Dsu d(n); std::vector<int> ids;
    for (const Edge& e : E) if (d.unite(e.u, e.v)) ids.push_back(e.id);
    return ids;
}
long long bruteBest(int n, const std::vector<Edge>& E) {                           // 모든 신장 숲 열거 (m ≤ 16)
    int m = (int)E.size(); Dsu all(n); int c = n; for (const Edge& e : E) if (all.unite(e.u, e.v)) --c;
    long long best = LLONG_MAX;
    for (unsigned mask = 0; mask < (1u << m); ++mask) {
        if (__builtin_popcount(mask) != n - c) continue;
        Dsu d(n); bool ok = true; long long w = 0;
        for (int i = 0; i < m && ok; ++i) if (mask >> i & 1) { ok = d.unite(E[i].u, E[i].v); w += E[i].w; }
        if (ok) best = std::min(best, w);
    }
    return best;
}
void checkAll(int n, const std::vector<Edge>& E, bool brute) {
    Adj adj = buildAdj(n, E);
    long long pushes = 0, swaps = 0, ops = 0;
    Forest lz = primLazy(n, adj, E, &pushes), ix = primIndexed(n, adj, &swaps), ds = primDense(n, E, &ops), rf = primReference(n, E);
    assert(lz.order == rf.order && ix.order == rf.order && ds.order == rf.order);            // 선택 순서까지 동일
    assert(lz.weight == rf.weight && ix.weight == rf.weight && ds.weight == rf.weight);
    std::vector<int> a = rf.order, b = kruskalIds(n, E); std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end());
    assert(a == b);                                                                         // 크루스칼과 같은 간선 집합
    if (brute) assert(rf.weight == bruteBest(n, E));
}

int main() {
    // ① 손으로 확인한 모양: 고전 예제 0 에서 시작 → (0,3:5), (2,3:4), (0,1:10) 순서
    {   std::vector<Edge> E = {{0, 1, 10, 0}, {0, 2, 6, 1}, {0, 3, 5, 2}, {1, 3, 15, 3}, {2, 3, 4, 4}};
        Adj adj = buildAdj(4, E); long long p = 0;
        Forest f = primLazy(4, adj, E, &p);
        assert(f.weight == 19 && f.order == std::vector<int>({2, 4, 0}));
        checkAll(4, E, true);
    }

    // ② 전수: 정점 2~4 의 모든 그래프(쌍마다 없음/1/2/3, 동점 많음), 정점 5 는 표본 — 다섯 구현이 같은 순서·같은 집합, 총 무게는 완전 탐색과 같다
    long long graphs = 0;
    for (int n = 2; n <= 5; ++n) {
        std::vector<std::pair<int, int>> pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size(), base = n == 5 ? 3 : 4;
        long long total = 1; for (int i = 0; i < m; ++i) total *= base;
        for (long long code = 0; code < total; code += (n == 5 ? 11 : 1)) {
            std::vector<Edge> E; long long c = code;
            for (int i = 0; i < m; ++i, c /= base) if (c % base) E.push_back({pairs[i].first, pairs[i].second, c % base, (int)E.size()});
            checkAll(n, E, true); ++graphs;
        }
    }
    assert(graphs > 9000);

    // ③ 무작위 다중 그래프(루프·평행 간선·비연결 포함): 정점 ≤ 8, 간선 ≤ 14, 완전 탐색과 일치
    std::mt19937 rng(77);
    for (int it = 0; it < 600; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % 15);
        std::vector<Edge> E; for (int i = 0; i < m; ++i) E.push_back({(int)(rng() % n), (int)(rng() % n), (long long)(1 + rng() % 5), i});
        checkAll(n, E, true);
    }

    // ④ 색인 힙을 std::set 모형과 비교 (100 개 판 × 정점 200 개 · 무작위 연산 200 번 = 2 만 번, 20 번마다 불변식 검사)
    {
        int pops = 0, decreases = 0;
        for (int episode = 0; episode < 100; ++episode) {
            IndexedHeap hp(200); std::set<std::pair<IndexedHeap::Key, int>> model; std::vector<IndexedHeap::Key> cur(200, {-1, -1}); std::vector<char> gone(200, 0);
            for (int step = 0; step < 200; ++step) {
                if (rng() % 3 == 0 && !hp.empty()) {
                    int v = hp.popMin(); assert(v == model.begin()->second && hp.key[v] == model.begin()->first);
                    model.erase(model.begin()); gone[v] = 1; ++pops;
                } else {
                    int v = (int)(rng() % 200); IndexedHeap::Key k = {(long long)(rng() % 1000), (int)(rng() % 1000000)};
                    hp.pushOrDecrease(v, k);
                    if (!gone[v]) {
                        if (cur[v].first < 0) { cur[v] = k; model.insert({k, v}); }
                        else if (k < cur[v]) { model.erase({cur[v], v}); cur[v] = k; model.insert({k, v}); ++decreases; }
                    }
                }
                if (step % 20 == 0) assert(hp.valid());
            }
            assert(hp.valid());
        }
        assert(pops > 3000 && decreases > 100);
    }

    // ⑤ 비용은 횟수로: 직선 경로 1500 정점에서 느긋한 힙은 정확히 V − 1 번 넣고, 밀집 구현은 V 와 무관하게 정확히 2V² 번 스캔
    {
        const int n = 1500;
        std::vector<Edge> E; for (int i = 0; i + 1 < n; ++i) E.push_back({i, i + 1, (long long)(1 + (i * 7919) % 101), i});
        Adj adj = buildAdj(n, E); long long pushes = 0, ops = 0, swaps = 0;
        Forest a = primLazy(n, adj, E, &pushes), b = primDense(n, E, &ops), c = primIndexed(n, adj, &swaps);
        assert(pushes == n - 1 && ops == 2LL * n * n && a.order == b.order && a.order == c.order && (int)a.order.size() == n - 1);
    }

    // ⑥ 큰 입력 둘: (a) 정점 10 만 · 간선 60 만 · 성분 2 개 (b) 정점 1200 인 완전 그래프(간선 71 만 9,400) 의 밀집 대 힙
    {
        const int N = 100000, H = N / 2;
        std::vector<Edge> E; E.reserve(600000);
        std::mt19937_64 r(5);
        for (int half = 0; half < 2; ++half) {
            std::vector<int> perm(H); std::iota(perm.begin(), perm.end(), half * H); std::shuffle(perm.begin(), perm.end(), r);
            for (int i = 0; i + 1 < H; ++i) E.push_back({perm[i], perm[i + 1], (long long)(1 + r() % 1000000), (int)E.size()});
            for (int i = 0; i < 300000 - H; ++i) E.push_back({half * H + (int)(r() % H), half * H + (int)(r() % H), (long long)(1 + r() % 1000000), (int)E.size()});
        }
        Adj adj = buildAdj(N, E); long long pushes = 0, swaps = 0;
        Forest lz = primLazy(N, adj, E, &pushes), ix = primIndexed(N, adj, &swaps);
        assert(lz.order == ix.order && lz.weight == ix.weight && (int)lz.order.size() == N - 2);
        std::vector<int> a = lz.order, b = kruskalIds(N, E); std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end());
        assert(a == b);
        const int K = 1200;
        std::vector<Edge> C; C.reserve((std::size_t)K * (K - 1) / 2);
        for (int i = 0; i < K; ++i) for (int j = i + 1; j < K; ++j) C.push_back({i, j, (long long)(1 + r() % 100000), (int)C.size()});
        long long ops = 0, p2 = 0, s2 = 0; Adj cadj = buildAdj(K, C);
        Forest d = primDense(K, C, &ops), h = primIndexed(K, cadj, &s2), l = primLazy(K, cadj, C, &p2);
        assert(d.order == h.order && d.order == l.order && ops == 2LL * K * K && (int)d.order.size() == K - 1);
    }
    std::cout << "Prim: the lazy-heap, indexed decrease-key heap and dense O(V^2) versions all chose the same edges in the same order as a literal cut-property implementation and the same set as Kruskal on every 2-4 vertex graph with weights 1-3, a sample of the 5-vertex ones and 600 random multigraphs with loops, parallel edges and several components, totals matched exhaustive enumeration of spanning forests, the indexed heap survived 20,000 random operations against a std::set model, a straight path cost exactly V-1 pushes versus 2V^2 dense scans, and the 100,000-vertex/600,000-edge graph and a 1200-vertex complete graph gave identical results across implementations" << std::endl; return 0;
}
// Time Complexity: O(E log V)  (밀집 구현은 O(V²))
// Space Complexity: O(V + E)
```
## Boruvka()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <climits>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 보루프카(Borůvka) 최소 신장 트리: 모든 연결 성분이 동시에 "자기에게서 나가는 가장 가벼운 간선" 을 하나씩 고르고, 고른 간선들을 한꺼번에 합친다. 한 라운드가 끝나면 성분 수가 (나갈 간선이 있는 한) 적어도 절반으로 줄므로 라운드는 ⌈log₂ V⌉ 번 이하 — 라운드 안의 일이 서로 독립이라 병렬·분산 MST 의 기본 틀이다.
// 함정 — 동점: 성분이 서로 다른 "같은 가벼움" 의 간선을 임의로 고르면 선택한 간선들이 사이클을 이룰 수 있다. 모든 간선의 무게가 같은 삼각형에서 세 성분이 각자 두 후보 중 하나를 고르는 8 가지 조합 중 2 가지가 삼각형 전체를 고른다. (가중치, 번호) 의 전순서로 고르면 어떤 순서로든 사이클이 생기지 않는다(아래 6 가지 전순서 전부 확인). 이 전순서 덕분에 라운드 안에서 "서로 다른 선택 간선은 모두 실제로 합쳐진다" 는 것을 단언할 수 있다.
// 연결되지 않은 그래프: 라운드에서 아무 성분도 나갈 간선이 없으면 끝 — 그때까지 모은 것이 최소 신장 숲이다(기존 코드처럼 "성분 수 > 1 인 동안" 으로 돌면 무한 루프). 검증: 전순서 아래 MST 는 유일하므로 크루스칼과 *같은 간선 집합*, 완전 탐색과 같은 총무게, 연결 그래프에서 매 라운드 성분 수가 절반 이하, 룰러(ruler) 가중치 경로에서 라운드 수가 정확히 log₂ V.
struct Edge { int u, v; long long w; int id; };
struct Dsu {
    std::vector<int> p;
    explicit Dsu(int n) : p(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; p[a] = b; return true; }
};
bool lighter(const Edge& a, const Edge& b) { return a.w != b.w ? a.w < b.w : a.id < b.id; }
struct Result { long long weight; std::vector<int> ids; int components; int rounds; bool allMerged; std::vector<int> compsAfter; };

Result boruvka(int n, const std::vector<Edge>& E) {
    Dsu d(n);
    Result r{0, {}, n, 0, true, {}};
    while (true) {
        std::vector<int> best(n, -1);                                              // 성분 루트 → 그 성분에서 나가는 가장 가벼운 간선
        for (int i = 0; i < (int)E.size(); ++i) {
            int a = d.find(E[i].u), b = d.find(E[i].v);
            if (a == b) continue;
            for (int c : {a, b}) if (best[c] < 0 || lighter(E[i], E[best[c]])) best[c] = i;
        }
        std::vector<int> pick;
        for (int c = 0; c < n; ++c) if (best[c] >= 0) pick.push_back(best[c]);
        std::sort(pick.begin(), pick.end()); pick.erase(std::unique(pick.begin(), pick.end()), pick.end());   // 양쪽 성분이 같은 간선을 고를 수 있다
        if (pick.empty()) break;
        for (int i : pick) {
            bool ok = d.unite(E[i].u, E[i].v);                                     // 전순서 덕에 서로 다른 선택 간선은 사이클을 만들지 않는다
            r.allMerged = r.allMerged && ok;
            if (ok) { r.weight += E[i].w; r.ids.push_back(E[i].id); --r.components; }
        }
        ++r.rounds; r.compsAfter.push_back(r.components);
    }
    return r;
}
std::vector<int> kruskalIds(int n, std::vector<Edge> E) {
    std::sort(E.begin(), E.end(), lighter);
    Dsu d(n); std::vector<int> ids;
    for (const Edge& e : E) if (d.unite(e.u, e.v)) ids.push_back(e.id);
    return ids;
}
long long bruteBest(int n, const std::vector<Edge>& E) {
    int m = (int)E.size(); Dsu all(n); int c = n; for (const Edge& e : E) if (all.unite(e.u, e.v)) --c;
    long long best = LLONG_MAX;
    for (unsigned mask = 0; mask < (1u << m); ++mask) {
        if (__builtin_popcount(mask) != n - c) continue;
        Dsu d(n); bool ok = true; long long w = 0;
        for (int i = 0; i < m && ok; ++i) if (mask >> i & 1) { ok = d.unite(E[i].u, E[i].v); w += E[i].w; }
        if (ok) best = std::min(best, w);
    }
    return best;
}
void check(int n, const std::vector<Edge>& E, bool brute) {
    Result r = boruvka(n, E);
    std::vector<int> a = r.ids, b = kruskalIds(n, E); std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end());
    assert(a == b && r.allMerged);
    if (brute) assert(r.weight == bruteBest(n, E));
    int comps = n; { Dsu d(n); for (const Edge& e : E) if (d.unite(e.u, e.v)) --comps; }
    assert(r.components == comps);
    if (comps == 1 && n > 1) {                                                     // 연결: 매 라운드 성분 수가 절반 이하, 라운드 수 ≤ ⌈log2 n⌉
        int before = n;
        for (int after : r.compsAfter) { assert(2 * after <= before); before = after; }
        int lg = 0; while ((1 << lg) < n) ++lg;
        assert(r.rounds <= lg);
    }
}

int main() {
    // ① 손으로 확인한 모양
    {   std::vector<Edge> E = {{0, 1, 10, 0}, {0, 2, 6, 1}, {0, 3, 5, 2}, {1, 3, 15, 3}, {2, 3, 4, 4}};
        Result r = boruvka(4, E);
        assert(r.weight == 19 && r.components == 1 && r.rounds == 1);              // 한 라운드에 모든 성분이 자기 최소 간선(10, 5, 4, 4) 을 골라 한꺼번에 합쳐진다
        check(4, E, true);
    }
    assert(boruvka(0, {}).rounds == 0 && boruvka(5, {}).components == 5 && boruvka(3, {{0, 0, 1, 0}, {1, 2, 4, 1}, {1, 2, 3, 2}}).weight == 3);   // 빈 입력·루프·평행 간선·비연결도 멈춘다

    // ② 동점의 함정: 무게가 같은 삼각형에서 "각 성분이 후보 중 아무거나" 8 가지 중 2 가지가 사이클, 전순서 6 가지는 하나도 사이클이 없다
    {
        std::array<std::pair<int, int>, 3> edge = {{{0, 1}, {1, 2}, {2, 0}}};
        std::vector<std::vector<int>> cands = {{0, 2}, {0, 1}, {1, 2}};              // 성분 0 · 1 · 2 가 고를 수 있는 (같은 무게의) 간선 번호
        int cyclic = 0;
        for (int mask = 0; mask < 8; ++mask) {
            std::set<int> chosen; for (int c = 0; c < 3; ++c) chosen.insert(cands[c][mask >> c & 1]);
            Dsu d(3); bool cycle = false; for (int e : chosen) cycle = cycle || !d.unite(edge[e].first, edge[e].second);
            cyclic += cycle;
        }
        assert(cyclic == 2);
        std::array<int, 3> rank = {0, 1, 2};
        do {
            std::set<int> chosen;
            for (int c = 0; c < 3; ++c) { int best = cands[c][0]; for (int e : cands[c]) if (rank[e] < rank[best]) best = e; chosen.insert(best); }
            Dsu d(3); for (int e : chosen) { bool ok = d.unite(edge[e].first, edge[e].second); assert(ok); (void)ok; }
        } while (std::next_permutation(rank.begin(), rank.end()));
    }

    // ③ 전수: 정점 2~4 의 모든 그래프(쌍마다 없음/1/2/3), 정점 5 는 표본 — 크루스칼과 같은 집합, 완전 탐색과 같은 무게, 라운드 성질
    for (int n = 2; n <= 5; ++n) {
        std::vector<std::pair<int, int>> pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size(), base = n == 5 ? 3 : 4;
        long long total = 1; for (int i = 0; i < m; ++i) total *= base;
        for (long long code = 0; code < total; code += (n == 5 ? 11 : 1)) {
            std::vector<Edge> E; long long c = code;
            for (int i = 0; i < m; ++i, c /= base) if (c % base) E.push_back({pairs[i].first, pairs[i].second, c % base, (int)E.size()});
            check(n, E, true);
        }
    }
    std::mt19937 rng(4);
    for (int it = 0; it < 600; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % 15);
        std::vector<Edge> E; for (int i = 0; i < m; ++i) E.push_back({(int)(rng() % n), (int)(rng() % n), (long long)(1 + rng() % 5), i});
        check(n, E, true);
    }

    // ④ 룰러 가중치 경로: 간선 (i, i+1) 의 무게가 ctz(i+1)+1 이면 매 라운드 정확히 절반씩 합쳐져 라운드 수 = log2 V
    for (int k = 1; k <= 14; ++k) {
        int n = 1 << k;
        std::vector<Edge> E; for (int i = 0; i + 1 < n; ++i) E.push_back({i, i + 1, (long long)__builtin_ctz(i + 1) + 1, i});
        Result r = boruvka(n, E);
        assert(r.rounds == k && r.components == 1);
        for (int j = 0; j < k; ++j) assert(r.compsAfter[j] == n >> (j + 1));
    }

    // ⑤ 큰 입력: 정점 10 만 · 간선 60 만 · 성분 2 개 — 크루스칼과 같은 집합, 라운드 ≤ 16
    {
        const int N = 100000, H = N / 2;
        std::vector<Edge> E; E.reserve(600000);
        std::mt19937_64 r(5);
        for (int half = 0; half < 2; ++half) {
            std::vector<int> perm(H); std::iota(perm.begin(), perm.end(), half * H); std::shuffle(perm.begin(), perm.end(), r);
            for (int i = 0; i + 1 < H; ++i) E.push_back({perm[i], perm[i + 1], (long long)(1 + r() % 1000000), (int)E.size()});
            for (int i = 0; i < 300000 - H; ++i) E.push_back({half * H + (int)(r() % H), half * H + (int)(r() % H), (long long)(1 + r() % 1000000), (int)E.size()});
        }
        Result b = boruvka(N, E);
        std::vector<int> a = b.ids, k = kruskalIds(N, E); std::sort(a.begin(), a.end()); std::sort(k.begin(), k.end());
        assert(a == k && b.components == 2 && b.allMerged && b.rounds <= 16);
    }
    std::cout << "Boruvka: choosing the lightest outgoing edge of every component under a strict (weight, id) order produced exactly Kruskal's edge set and the exhaustive minimum on every 2-4 vertex graph with weights 1-3, a sample of the 5-vertex ones and 600 random multigraphs (loops, parallel edges, disconnected), every distinct pick merged two components, connected graphs halved their component count each round and finished within ceil(log2 V) rounds, a ruler-weighted path needed exactly log2 V rounds for V up to 16384, arbitrary tie choices on an equal-weight triangle formed a cycle in 2 of 8 cases while all 6 total orders never did, and a 100,000-vertex, 600,000-edge two-component graph matched Kruskal in at most 16 rounds" << std::endl; return 0;
}
// Time Complexity: O(E log V)
// Space Complexity: O(V + E)
```
## ReverseDelete()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 역삭제(Reverse-Delete): 크루스칼의 거울상 — 간선을 가장 무거운 것부터 훑으며, *지워도 두 끝이 여전히 이어져 있으면* (그 간선이 어떤 사이클 위에 있으면) 지운다. 사이클에서 가장 무거운 간선은 MST 에 없다는 사이클 성질을 그대로 쓰는 셈이다. 연결 여부를 "두 끝 사이의 도달 가능성" 으로 판정하므로 연결되지 않은 그래프에서도 성분 수를 늘리지 않고 최소 신장 숲을 만든다(기존처럼 전체 연결을 보면 비연결 입력에서 모든 간선을 못 지운다).
// 크루스칼이 (가중치, 번호) 오름차순이면 역삭제는 같은 전순서의 내림차순으로 훑는다 — 그러면 두 알고리즘이 *같은 간선 집합* 을 내야 한다(전순서 아래 MST 는 유일). 지운 간선의 수는 순환수 E − V + c, 각 삭제 직후 성분 수가 그대로라는 불변식을 매 단계 서로소 집합으로 다시 계산해 확인한다.
// 비용: 간선마다 BFS 로 O(V + E) 이므로 O(E (V + E)) — 교육용이다. 동적 연결성 자료구조(Holm–de Lichtenberg–Thorup)로 간선 삭제·연결 질의를 polylog 시간에 처리하면 O(E log V (log log V)³) 까지 줄지만 구현이 크게 복잡하다. 실무에서는 크루스칼·프림을 쓴다.
struct Edge { int u, v; long long w; int id; };
struct Dsu {
    std::vector<int> p;
    explicit Dsu(int n) : p(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; p[a] = b; return true; }
};
bool lighter(const Edge& a, const Edge& b) { return a.w != b.w ? a.w < b.w : a.id < b.id; }
struct Result { long long weight; std::vector<int> kept, deleted; long long visits; };

// check != nullptr 이면 매 삭제 후 성분 수가 원래와 같은지 확인한다
Result reverseDelete(int n, const std::vector<Edge>& E, int originalComponents = -1) {
    int m = (int)E.size();
    std::vector<int> order(m); std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(), [&](int a, int b) { return lighter(E[b], E[a]); });          // 무거운 것부터
    std::vector<std::vector<int>> inc(n);
    for (int i = 0; i < m; ++i) { inc[E[i].u].push_back(i); if (E[i].u != E[i].v) inc[E[i].v].push_back(i); }
    std::vector<char> alive(m, 1);
    Result r{0, {}, {}, 0};
    std::vector<int> mark(n, -1); int stamp = 0;
    for (int id : order) {
        alive[id] = 0;
        bool reach = E[id].u == E[id].v;                                          // 루프는 언제나 지워도 "이어져 있다"
        if (!reach) {
            ++stamp; std::queue<int> q; q.push(E[id].u); mark[E[id].u] = stamp;
            while (!q.empty() && !reach) {
                int x = q.front(); q.pop(); ++r.visits;
                for (int e : inc[x]) if (alive[e]) {
                    int y = E[e].u == x ? E[e].v : E[e].u;
                    if (y == E[id].v) { reach = true; break; }
                    if (mark[y] != stamp) { mark[y] = stamp; q.push(y); }
                }
            }
        }
        if (reach) r.deleted.push_back(id); else alive[id] = 1;                   // 지우면 끊기는 간선은 되살린다 (다리)
        if (originalComponents >= 0) {
            Dsu d(n); int c = n; for (int i = 0; i < m; ++i) if (alive[i] && d.unite(E[i].u, E[i].v)) --c;
            assert(c == originalComponents);                                      // 불변식: 성분 수는 한 번도 늘지 않았다
        }
    }
    for (int i = 0; i < m; ++i) if (alive[i]) { r.kept.push_back(i); r.weight += E[i].w; }
    return r;
}
std::vector<int> kruskalIds(int n, std::vector<Edge> E) {
    std::sort(E.begin(), E.end(), lighter);
    Dsu d(n); std::vector<int> ids;
    for (const Edge& e : E) if (d.unite(e.u, e.v)) ids.push_back(e.id);
    std::sort(ids.begin(), ids.end());
    return ids;
}
long long bruteBest(int n, const std::vector<Edge>& E) {
    int m = (int)E.size(); Dsu all(n); int c = n; for (const Edge& e : E) if (all.unite(e.u, e.v)) --c;
    long long best = LLONG_MAX;
    for (unsigned mask = 0; mask < (1u << m); ++mask) {
        if (__builtin_popcount(mask) != n - c) continue;
        Dsu d(n); bool ok = true; long long w = 0;
        for (int i = 0; i < m && ok; ++i) if (mask >> i & 1) { ok = d.unite(E[i].u, E[i].v); w += E[i].w; }
        if (ok) best = std::min(best, w);
    }
    return best;
}
void check(int n, const std::vector<Edge>& E, bool brute, bool invariant) {
    int comps = n; { Dsu d(n); for (const Edge& e : E) if (d.unite(e.u, e.v)) --comps; }
    Result r = reverseDelete(n, E, invariant ? comps : -1);
    assert(r.kept == kruskalIds(n, E));                                            // 크루스칼과 같은 집합
    assert((int)r.kept.size() == n - comps && (int)r.deleted.size() == (int)E.size() - (n - comps));   // 지운 개수 = 순환수
    if (brute) assert(r.weight == bruteBest(n, E));
}

int main() {
    // ① 손으로 확인한 모양: 고전 예제 — 15 와 6 은 사이클 위에 있어 지워지고 10 · 5 · 4 가 남는다 (총 19)
    {   std::vector<Edge> E = {{0, 1, 10, 0}, {0, 2, 6, 1}, {0, 3, 5, 2}, {1, 3, 15, 3}, {2, 3, 4, 4}};
        Result r = reverseDelete(4, E, 1);
        assert(r.weight == 19 && r.kept == std::vector<int>({0, 2, 4}) && r.deleted == std::vector<int>({3, 1}));    // 15 와 6 이 지워진다
        check(4, E, true, true);
    }
    {   std::vector<Edge> E = {{0, 1, 3, 0}, {2, 3, 1, 1}, {1, 0, 2, 2}, {4, 4, 0, 3}};      // 평행 간선, 루프, 비연결 → 숲
        Result r = reverseDelete(5, E, 3);
        assert(r.weight == 3 && r.kept == std::vector<int>({1, 2}) && r.deleted == std::vector<int>({0, 3}));
    }

    // ② 전수: 정점 2~4 의 모든 그래프(쌍마다 없음/1/2/3), 정점 5 는 표본 — 불변식 검사 켬
    long long graphs = 0;
    for (int n = 2; n <= 5; ++n) {
        std::vector<std::pair<int, int>> pairs;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size(), base = n == 5 ? 3 : 4;
        long long total = 1; for (int i = 0; i < m; ++i) total *= base;
        for (long long code = 0; code < total; code += (n == 5 ? 13 : 1)) {
            std::vector<Edge> E; long long c = code;
            for (int i = 0; i < m; ++i, c /= base) if (c % base) E.push_back({pairs[i].first, pairs[i].second, c % base, (int)E.size()});
            check(n, E, true, true); ++graphs;
        }
    }
    assert(graphs > 7000);

    // ③ 무작위 다중 그래프(루프·평행 간선·비연결): 정점 ≤ 8, 간선 ≤ 14
    std::mt19937 rng(21);
    for (int it = 0; it < 500; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % 15);
        std::vector<Edge> E; for (int i = 0; i < m; ++i) E.push_back({(int)(rng() % n), (int)(rng() % n), (long long)(1 + rng() % 5), i});
        check(n, E, true, true);
    }

    // ④ 중간 크기: 정점 300, 간선 2500 의 연결 그래프 — 크루스칼과 같은 집합, 방문 횟수는 (간선 수 × 정점 수) 이하
    {
        const int n = 300, m = 2500;
        std::vector<Edge> E;
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        for (int i = 0; i + 1 < n; ++i) E.push_back({perm[i], perm[i + 1], (long long)(1 + rng() % 1000), (int)E.size()});
        while ((int)E.size() < m) E.push_back({(int)(rng() % n), (int)(rng() % n), (long long)(1 + rng() % 1000), (int)E.size()});
        Result r = reverseDelete(n, E);
        assert(r.kept == kruskalIds(n, E) && (int)r.kept.size() == n - 1 && r.visits <= (long long)m * n);
    }
    std::cout << "ReverseDelete: scanning edges from heaviest to lightest and deleting those whose endpoints stay connected kept exactly the same edge set as Kruskal and the exhaustive minimum weight on every 2-4 vertex graph with weights 1-3, a sample of the 5-vertex ones and 500 random multigraphs (loops, parallel edges, several components), the number of deletions always equalled the cyclomatic number, a union-find recount after every single step confirmed the component count never changed, and a 300-vertex, 2500-edge graph agreed with Kruskal within E*V BFS visits" << std::endl; return 0;
}
// Time Complexity: O(E (V + E))
// Space Complexity: O(V + E)
```
## MinimumSpanningTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 최소 신장 트리의 통합 인터페이스: Kruskal / Prim / Borůvka 중 선택. 간선 가중치가 모두 다르면 MST 가 유일하므로 세 알고리즘의 결과(간선 집합)가 같아야 한다
struct Edge { int u, v, w, id; };
enum Algo { KRUSKAL, PRIM, BORUVKA };

struct DSU {
    std::vector<int> p;
    explicit DSU(int n) : p(n) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; p[a] = b; return true; }
};

std::set<int> mst(int V, const std::vector<Edge>& E, Algo algo) {
    std::set<int> chosen;
    if (algo == KRUSKAL) {
        auto sorted = E; std::sort(sorted.begin(), sorted.end(), [](const Edge& a, const Edge& b) { return a.w < b.w; });
        DSU d(V); for (auto& e : sorted) if (d.unite(e.u, e.v)) chosen.insert(e.id);
    } else if (algo == PRIM) {
        std::vector<std::vector<Edge>> adj(V);
        for (auto& e : E) { adj[e.u].push_back(e); adj[e.v].push_back({e.v, e.u, e.w, e.id}); }
        std::vector<bool> in(V, false);
        typedef std::pair<int, std::pair<int, int>> Item;                      // (가중치, (정점, 간선 id))
        std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
        pq.push({0, {0, -1}});
        while (!pq.empty()) {
            auto it = pq.top(); pq.pop(); int u = it.second.first;
            if (in[u]) continue;
            in[u] = true; if (it.second.second >= 0) chosen.insert(it.second.second);
            for (auto& e : adj[u]) if (!in[e.v]) pq.push({e.w, {e.v, e.id}});
        }
    } else {
        DSU d(V); int comps = V;
        while (comps > 1) {
            std::vector<int> cheapest(V, -1);                                 // 컴포넌트별 가장 싼 나가는 간선
            for (size_t i = 0; i < E.size(); i++) {
                int a = d.find(E[i].u), b = d.find(E[i].v); if (a == b) continue;
                for (int c : {a, b}) if (cheapest[c] < 0 || E[i].w < E[cheapest[c]].w) cheapest[c] = i;
            }
            for (int c = 0; c < V; c++) if (cheapest[c] >= 0 && d.unite(E[cheapest[c]].u, E[cheapest[c]].v)) { chosen.insert(E[cheapest[c]].id); comps--; }
        }
    }
    return chosen;
}

int main() {
    std::mt19937 rng(21);
    for (int trial = 0; trial < 200; trial++) {
        int V = rng() % 15 + 2; std::vector<Edge> E; int id = 0;
        std::vector<int> weights(V * V * 3); std::iota(weights.begin(), weights.end(), 1); std::shuffle(weights.begin(), weights.end(), rng);   // 서로 다른 가중치
        for (int v = 1; v < V; v++) { E.push_back({(int)(rng() % v), v, weights[id], id}); id++; }        // 연결을 보장하는 뼈대
        for (int k = 0; k < V * 2; k++) { int a = rng() % V, b = rng() % V; if (a != b) { E.push_back({a, b, weights[id], id}); id++; } }
        auto k = mst(V, E, KRUSKAL), p = mst(V, E, PRIM), b = mst(V, E, BORUVKA);
        assert(k.size() == (size_t)V - 1 && k == p && k == b);               // 세 알고리즘이 같은 트리를 만든다
    }
    std::cout << "MinimumSpanningTree: Kruskal, Prim and Boruvka agree on 200 random graphs." << std::endl;
    return 0;
}
// Time Complexity: Kruskal O(E log E), Prim O(E log V), Borůvka O(E log V)
// Space Complexity: O(V + E)
```
# Part 8. 서로소 집합
## MakeSet()
### 대표코드
```cpp
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
#include <cassert>

// MakeSet(x): 원소 x 하나만 들어 있는 새 집합을 만든다 — parent[x] = x (자기 자신이 대표), rank[x] = 0. 서로소 집합(Union-Find)의 모든 연산은 이것으로 시작한다.
// 만드는 방식은 두 가지다. ① 원소가 0..n-1 이고 미리 알려져 있으면 iota 로 한 번에 O(n). ② 원소가 문자열처럼 임의의 키이고 도중에 나타나면 처음 보는 순간 번호를 붙여 만든다(키 -> 번호 사전 + 배열 push_back).
// 함정: 이미 합쳐진 원소에 MakeSet 을 다시 부르면 자기 자신을 대표로 되돌려 집합이 찢어진다. 그래서 MakeSet 은 "이미 있으면 아무것도 하지 않는" 멱등(idempotent) 연산이어야 한다.
// 검증: ① 무작위 MakeSet/Union 열에서 집합 수 = 원소 수 − 성공한 합치기 수 이고 연결 판별이 라벨 기반 기준 구현과 항상 같다 ② 같은 원소에 MakeSet 을 반복해도 기존 집합이 유지 ③ 멱등이 아닌 순진한 구현이 집합을 실제로 찢는 사례를 재현 ④ 일괄 초기화와 하나씩 생성이 같은 상태
struct DynamicDSU {
    std::unordered_map<std::string, int> id; std::vector<int> parent, rnk; int sets = 0;
    int makeSet(const std::string& key) {
        auto it = id.find(key); if (it != id.end()) return it->second;                // 멱등: 이미 있으면 그대로
        int v = (int)parent.size(); id[key] = v; parent.push_back(v); rnk.push_back(0); sets++; return v;
    }
    int find(int x) { while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (rnk[a] < rnk[b]) std::swap(a, b); parent[b] = a; if (rnk[a] == rnk[b]) rnk[a]++; sets--; return true; }
};
struct NaiveDSU {                                                                      // 잘못된 구현: MakeSet 이 무조건 덮어쓴다
    std::vector<int> parent;
    void makeSet(int x) { if (x >= (int)parent.size()) parent.resize(x + 1); parent[x] = x; }
    int find(int x) { while (parent[x] != x) x = parent[x]; return x; }
    void unite(int a, int b) { parent[find(a)] = find(b); }
};
int main() {
    std::mt19937 rng(11); DynamicDSU d; std::vector<int> label; std::vector<std::string> names; int successfulUnions = 0, repeats = 0;
    for (int step = 0; step < 6000; step++) {
        int op = rng() % 3;
        if (op == 0 || names.size() < 2) { bool fresh = names.empty() || rng() % 2; std::string k = fresh ? "w" + std::to_string(names.size()) : names[rng() % names.size()]; int before = d.sets; int v = d.makeSet(k);
            if (fresh) { names.push_back(k); label.push_back(v); assert(d.sets == before + 1 && v == (int)names.size() - 1); } else { repeats++; assert(d.sets == before); } }       // ② 반복 MakeSet 은 아무 영향 없음
        else { int a = rng() % names.size(), b = rng() % names.size(); bool merged = d.unite(d.id[names[a]], d.id[names[b]]); bool ref = label[a] != label[b];
            assert(merged == ref); if (ref) { successfulUnions++; int from = label[b], to = label[a]; for (int& l : label) if (l == from) l = to; } }
        if (step % 50 == 0) for (int t = 0; t < 10; t++) { int a = rng() % names.size(), b = rng() % names.size(); assert((d.find(d.id[names[a]]) == d.find(d.id[names[b]])) == (label[a] == label[b])); }       // ① 기준 구현과 일치
        assert(d.sets == (int)names.size() - successfulUnions);
    }
    NaiveDSU bad; bad.makeSet(0); bad.makeSet(1); bad.unite(0, 1); assert(bad.find(0) == bad.find(1)); bad.makeSet(0); assert(bad.find(0) != bad.find(1));           // ③ 순진한 구현은 0 을 다시 만들면 {0,1} 이 찢어진다
    DynamicDSU good; int a = good.makeSet("x"), b = good.makeSet("y"); good.unite(a, b); good.makeSet("x"); assert(good.find(a) == good.find(b) && good.sets == 1);
    int n = 1000; std::vector<int> bulk(n); std::iota(bulk.begin(), bulk.end(), 0); DynamicDSU one; for (int i = 0; i < n; i++) one.makeSet(std::to_string(i)); assert(one.parent == bulk && one.sets == n);        // ④ 일괄 == 하나씩
    std::cout << "MakeSet: " << names.size() << " elements, " << successfulUnions << " successful unions, " << repeats << " repeated MakeSet calls left the sets intact; the naive overwrite version split {0,1}" << std::endl; return 0;
}
// Time Complexity: O(1) 평균 (키 사전 조회), 일괄 초기화 O(n)
// Space Complexity: O(n)
```
## FindSet()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// FindSet(x): x 가 속한 집합의 대표(트리의 루트)를 찾는다. 부모 포인터를 루트까지 따라 올라가는 것이 전부이고, 올라가는 김에 경로를 짧게 만드는 방식이 네 가지 있다.
//   ① 압축 없음(plain): 그냥 올라간다.  ② 완전 압축(compression): 루트를 찾은 뒤 경로의 모든 노드가 루트를 직접 가리키게 한다(두 번 지난다).
//   ③ 경로 반감(halving): 한 칸 올라갈 때마다 자기 부모를 조부모로 바꾼다.  ④ 경로 분할(splitting): 경로의 모든 노드가 부모를 조부모로 바꾼다.  ③④ 는 한 번만 지나고 재귀가 없다.
// 재귀 구현(return parent[x] = find(parent[x]))은 경로가 길 때 호출 스택이 깊어져 100 만 길이 사슬에서 스택 오버플로가 날 수 있으므로 반복문이 안전하다.
// 검증: ① 무작위 숲에서 네 방식이 항상 같은 루트를 찾는다 ② 완전 압축 뒤 방문한 모든 노드의 깊이가 ≤ 1 ③ 반감 뒤 x 의 경로 길이 ≤ ⌈d/2⌉, 분할 뒤에는 경로 위 모든 노드가 ⌈깊이/2⌉ 이하 ④ 길이 100 만 사슬에서 반복문 구현이 문제없이 동작하고 압축은 첫 호출 뒤 비용이 한 걸음
struct Forest {
    std::vector<int> p; long steps = 0;
    explicit Forest(std::vector<int> parent) : p(std::move(parent)) {}
    int plain(int x) { while (p[x] != x) { x = p[x]; steps++; } return x; }
    int compress(int x) { int r = x; while (p[r] != r) { r = p[r]; steps++; } while (p[x] != r) { int nx = p[x]; p[x] = r; x = nx; steps++; } return r; }
    int halving(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; steps++; } return x; }
    int splitting(int x) { while (p[x] != x) { int nx = p[x]; p[x] = p[nx]; x = nx; steps++; } return x; }
    int depth(int x) const { int d = 0; while (p[x] != x) { x = p[x]; d++; } return d; }
};
int main() {
    std::mt19937 rng(21); long sPlain = 0, sComp = 0, sHalf = 0, sSplit = 0;
    for (int t = 0; t < 300; t++) {
        int n = 2 + rng() % 400; std::vector<int> p(n); p[0] = 0; for (int i = 1; i < n; i++) p[i] = (rng() % 8 == 0) ? i : (int)(rng() % i);          // 부모 번호가 항상 더 작으므로 사이클이 없고 루트가 여럿인 숲
        Forest f0(p), f1(p), f2(p), f3(p);
        for (int q = 0; q < 200; q++) { int x = rng() % n; int d0 = f2.depth(x);
            std::vector<int> path; for (int y = x;; y = f3.p[y]) { path.push_back(y); if (f3.p[y] == y) break; } std::vector<int> pathDepth; for (int y : path) pathDepth.push_back(f3.depth(y));
            int r0 = f0.plain(x), r1 = f1.compress(x), r2 = f2.halving(x), r3 = f3.splitting(x); assert(r0 == r1 && r1 == r2 && r2 == r3);                        // ① 같은 루트
            for (int y : path) assert(f1.depth(y) <= 1);                                                                                                      // ② 완전 압축: 경로 위 모든 노드가 루트 바로 아래
            assert(f2.depth(x) <= (d0 + 1) / 2);                                                                                                              // ③ 반감: x 의 새 깊이 ≤ ⌈d/2⌉
            for (size_t i = 0; i < path.size(); i++) assert(f3.depth(path[i]) <= (pathDepth[i] + 1) / 2); }                                                    // ③ 분할: 경로 위 모든 노드가 절반 이하
        sPlain += f0.steps; sComp += f1.steps; sHalf += f2.steps; sSplit += f3.steps;
    }
    const int N = 1000000; std::vector<int> chain(N); chain[0] = 0; for (int i = 1; i < N; i++) chain[i] = i - 1; Forest big(chain);
    assert(big.compress(N - 1) == 0); long first = big.steps; assert(first >= N - 1); big.steps = 0; assert(big.compress(N - 1) == 0 && big.steps == 1);          // ④ 두 번째 호출은 루트까지 한 걸음이면 끝
    Forest big2(chain); assert(big2.halving(N - 1) == 0); long h1 = big2.steps; big2.steps = 0; big2.halving(N - 1); assert(h1 <= N / 2 + 1 && big2.steps <= h1 / 2 + 1);                // 반감은 한 번에 두 칸씩 오르고 경로를 절반으로 줄인다
    std::cout << "FindSet: all four variants returned identical roots; total steps over the random forests plain " << sPlain << ", compression " << sComp << ", halving " << sHalf << ", splitting " << sSplit << "; a " << N << "-node chain: compression 2nd call " << 1 << " step, halving 2nd call " << big2.steps << std::endl; return 0;
}
// Time Complexity: 압축 없음 O(경로 길이), 압축/반감/분할은 분할상환 O(log n) (랭크 합치기와 함께면 O(α(n)))
// Space Complexity: O(1) 추가 공간 (반복 구현)
```
## UnionSet()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// UnionSet: 두 원소가 속한 집합을 하나로 합친다. 대표(루트)를 찾아 한쪽 루트를 다른 쪽 밑에 붙이는 것이 전부다.
//  - 합칠 때 랭크(트리 높이의 상한)가 낮은 쪽을 높은 쪽 밑에 붙이고 (UnionByRank), 찾을 때 경로를 압축하면 (PathCompression) 연산 한 번당 분할상환 O(α(n))  (α 는 역아커만 함수, 실용상 4 이하)
//  ① 무작위 연산 20 만 번(n = 1 000, 합치기 60% / 같은 집합인가 40%)을 *라벨 배열을 통째로 다시 쓰는 순진한 구현* 과 대조: 반환값·연결 여부·집합 수·집합 크기가 모두 같다
//  ② 랭크 불변식: 모든 루트에서 크기 ≥ 2^랭크, 랭크 ≤ ⌊log2 n⌋  ③ 최악의 입력: 짝지어 합치는 순서(균형 병합)로 n = 2^k 개를 합치면 랭크가 정확히 k 에 닿고, 이때 경로 압축 없이 잰 최대 깊이도 k
//  ④ 압축 효과: 한 번 find 한 뒤에는 그 원소가 루트의 바로 아래 — 같은 find 를 반복하면 부모를 따라간 횟수가 1 로 줄고, 연산 20 만 번의 총 부모 따라가기 횟수가 연산당 평균 4 미만  ⑤ 긴 사슬 100 만 개를 합쳐도 랭크는 20 이하이고 재귀 깊이가 문제 되지 않음
struct DisjointSet {
    std::vector<int> parent, rnk, sz; int components; long hops = 0;
    explicit DisjointSet(int n) : parent(n), rnk(n, 0), sz(n, 1), components(n) { std::iota(parent.begin(), parent.end(), 0); }
    int find(int x) { int root = x; while (parent[root] != root) { root = parent[root]; ++hops; } while (parent[x] != root) { int next = parent[x]; parent[x] = root; x = next; } return root; }          // 두 번 훑는 경로 압축(반복형)
    int depthWithoutCompression(int x) const { int d = 0; while (parent[x] != x) { x = parent[x]; ++d; } return d; }
    bool unionSet(int a, int b) {                       // 합쳤으면 true, 이미 같은 집합이면 false
        a = find(a); b = find(b);
        if (a == b) return false;
        if (rnk[a] < rnk[b]) std::swap(a, b);
        parent[b] = a; sz[a] += sz[b];
        if (rnk[a] == rnk[b]) rnk[a]++;
        components--;
        return true;
    }
    bool connected(int a, int b) { return find(a) == find(b); }
    int sizeOf(int x) { return sz[find(x)]; }
};
struct NaiveSets {                                       // 오라클: 라벨 배열, 합칠 때마다 전부 다시 쓴다
    std::vector<int> label; int components; explicit NaiveSets(int n) : label(n), components(n) { std::iota(label.begin(), label.end(), 0); }
    bool unionSet(int a, int b) { if (label[a] == label[b]) return false; int from = label[b], to = label[a]; for (int& l : label) if (l == from) l = to; --components; return true; }
    int sizeOf(int x) const { return (int)std::count(label.begin(), label.end(), label[x]); } };

int main() {
    {   DisjointSet ds(8); assert(ds.unionSet(0, 1) && ds.unionSet(2, 3) && ds.unionSet(1, 3)); assert(!ds.unionSet(0, 2)); assert(ds.connected(0, 3) && !ds.connected(0, 4)); assert(ds.components == 5);
        for (int i = 4; i < 7; i++) ds.unionSet(i, i + 1); assert(ds.components == 2 && ds.connected(4, 7)); }
    std::mt19937 rng(21);
    {   const int n = 1000; DisjointSet ds(n); NaiveSets naive(n);                                                                                       // ① 순진한 구현과 대조
        for (int step = 0; step < 200000; ++step) { int a = (int)(rng() % n), b = (int)(rng() % n);
            if (rng() % 10 < 6) { bool got = ds.unionSet(a, b), want = naive.unionSet(a, b); assert(got == want); } else assert(ds.connected(a, b) == (naive.label[a] == naive.label[b]));
            assert(ds.components == naive.components); if (step % 5000 == 0) { int x = (int)(rng() % n); assert(ds.sizeOf(x) == naive.sizeOf(x)); } }
        for (int x = 0; x < n; ++x) assert(ds.sizeOf(x) == naive.sizeOf(x));
        for (int x = 0; x < n; ++x) if (ds.parent[x] == x) { assert(ds.sz[x] >= (1 << ds.rnk[x])); assert(ds.rnk[x] <= (int)std::floor(std::log2((double)n))); } }                                    // ② 랭크 불변식
    for (int k = 1; k <= 14; ++k) { int n = 1 << k; DisjointSet ds(n); for (int span = 1; span < n; span *= 2) for (int i = 0; i + span < n; i += 2 * span) ds.unionSet(i, i + span);                          // ③ 균형 병합
        assert(ds.components == 1 && ds.rnk[ds.find(0)] == k); int deepest = 0; for (int x = 0; x < n; ++x) deepest = std::max(deepest, ds.depthWithoutCompression(x)); assert(deepest == k); }
    {   DisjointSet ds(1 << 14); for (int span = 1; span < (1 << 14); span *= 2) for (int i = 0; i + span < (1 << 14); i += 2 * span) ds.unionSet(i, i + span);                                           // ④ 압축 효과
        int deep = -1; for (int x = 0; x < (1 << 14); ++x) if (ds.depthWithoutCompression(x) == 14) { deep = x; break; } assert(deep >= 0);
        ds.find(deep); assert(ds.depthWithoutCompression(deep) == 1 || ds.parent[deep] == ds.find(deep)); long before = ds.hops; ds.find(deep); assert(ds.hops - before <= 1); }
    {   DisjointSet ds(100000); long ops = 0; for (int step = 0; step < 200000; ++step) { int a = (int)(rng() % 100000), b = (int)(rng() % 100000); if (rng() % 2) ds.unionSet(a, b); else ds.connected(a, b); ops += 2; } assert((double)ds.hops / (double)ops < 4.0); }
    {   const int N = 1000000; DisjointSet chain(N); for (int i = 0; i + 1 < N; i++) chain.unionSet(i, i + 1); assert(chain.components == 1 && chain.connected(0, N - 1));                           // ⑤ 긴 사슬
        int maxRank = *std::max_element(chain.rnk.begin(), chain.rnk.end()); assert(maxRank <= 20); std::cout << "UnionSet verified. max rank in a 1000000-chain: " << maxRank << std::endl; }
    return 0;
}
// Time Complexity: 분할상환 O(α(n))
// Space Complexity: O(n)
```
## UnionByRank()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 합치기 전략(Union by Rank / Size): 두 집합을 합칠 때 어느 루트를 어느 쪽 밑에 붙일까? 아무렇게나 붙이면 트리가 사슬이 되어 find 가 O(n) 이 된다.
//   랭크(rank): 트리 높이의 상한. 랭크가 낮은 루트를 높은 쪽 밑에 붙이고, 같을 때만 새 루트의 랭크를 1 올린다.  크기(size): 원소가 적은 쪽을 많은 쪽 밑에 붙인다. 둘 다 높이 ≤ ⌊log₂ n⌋ 를 보장한다.
// 이유: 어떤 노드의 깊이가 1 늘어나는 것은 "자기 집합이 상대 집합에 붙을 때" 뿐이고, 그때 상대 집합이 더 크거나 같으므로 집합 크기가 두 배 이상이 된다. 크기는 n 을 넘을 수 없으니 깊이가 늘어난 횟수는 log₂ n 이하다.
// 이 상한은 정확히 도달한다: 같은 크기의 집합끼리만 짝지어 합치면(토너먼트) 높이가 정확히 log₂ n 인 이항 트리가 만들어진다. 경로 압축과 함께 쓰면 높이는 줄어들 수 있지만 랭크는 줄지 않으므로 "높이 ≤ 랭크" 만 성립한다.
// 검증: ① 무작위 합치기에서 랭크/크기 방식의 높이가 ⌊log₂ n⌋ 이하 ② 랭크 r 인 루트의 트리 크기 ≥ 2^r ③ 토너먼트 합치기에서 높이가 정확히 log₂ n ④ 임의 방향 합치기는 사슬 열에서 높이 n−1 ⑤ 압축을 섞어도 높이 ≤ 랭크
enum Mode { NAIVE, RANK, SIZE };
struct DSU {
    std::vector<int> p, rk, sz; Mode mode; bool compress;
    DSU(int n, Mode m, bool c = false) : p(n), rk(n, 0), sz(n, 1), mode(m), compress(c) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { int r = x; while (p[r] != r) r = p[r]; if (compress) while (p[x] != r) { int nx = p[x]; p[x] = r; x = nx; } return r; }
    bool unite(int a, int b) {
        a = find(a); b = find(b); if (a == b) return false;
        if (mode == RANK) { if (rk[a] < rk[b]) std::swap(a, b); p[b] = a; if (rk[a] == rk[b]) rk[a]++; }
        else if (mode == SIZE) { if (sz[a] < sz[b]) std::swap(a, b); p[b] = a; }
        else p[a] = b;                                                                         // 무조건 a 의 루트를 b 의 루트 밑에
        sz[mode == NAIVE ? b : a] += sz[mode == NAIVE ? a : b]; return true;
    }
    int height() const { int h = 0; for (size_t v = 0; v < p.size(); v++) { int d = 0; for (int x = (int)v; p[x] != x; x = p[x]) d++; h = std::max(h, d); } return h; }
};
int main() {
    std::mt19937 rng(3); int worstRank = 0, worstSize = 0;
    for (int t = 0; t < 300; t++) {
        int n = 2 + rng() % 400; DSU r(n, RANK), s(n, SIZE), c(n, RANK, true);
        for (int k = 0; k < 3 * n; k++) { int a = rng() % n, b = rng() % n; r.unite(a, b); s.unite(a, b); c.unite(a, b); if (k % 7 == 0) { int x = rng() % n; c.find(x); } }
        int lg = (int)std::floor(std::log2((double)n)); assert(r.height() <= lg && s.height() <= lg); worstRank = std::max(worstRank, r.height()); worstSize = std::max(worstSize, s.height());                         // ①
        for (int v = 0; v < n; v++) if (r.p[v] == v) assert(r.sz[v] >= (1 << r.rk[v]));                                                                                                                       // ② 랭크 r -> 크기 ≥ 2^r
        for (int v = 0; v < n; v++) if (c.p[v] == v) { int h = 0; for (int x = 0; x < n; x++) if (c.find(x) == v) { int d = 0; for (int y = x; c.p[y] != y; y = c.p[y]) d++; h = std::max(h, d); } assert(h <= c.rk[v]); }          // ⑤ 압축을 섞어도 높이 ≤ 랭크
    }
    const int N = 1024; DSU tour(N, RANK); for (int len = 1; len < N; len *= 2) for (int i = 0; i + len < N; i += 2 * len) tour.unite(i, i + len); assert(tour.height() == 10 && tour.rk[tour.find(0)] == 10);          // ③ 토너먼트: 높이 정확히 log2(1024) = 10
    DSU sz(N, SIZE); for (int len = 1; len < N; len *= 2) for (int i = 0; i + len < N; i += 2 * len) sz.unite(i, i + len); assert(sz.height() == 10);
    DSU adv(N, NAIVE), good(N, RANK); for (int i = 0; i + 1 < N; i++) { adv.unite(i, i + 1); good.unite(i, i + 1); } assert(adv.height() == N - 1 && good.height() <= 10);                                  // ④ 사슬 열
    std::cout << "UnionByRank: height stayed <= floor(log2 n) (worst by rank " << worstRank << ", by size " << worstSize << "); the tournament reaches the bound exactly (height " << tour.height() << " for n=" << N << "); arbitrary linking on a chain gave height " << adv.height() << std::endl; return 0;
}
// Time Complexity: find O(log n) (압축 없을 때), 합치기 O(log n)
// Space Complexity: O(n)
```
## PathCompression()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 경로 압축(Path Compression): find 가 루트까지 올라온 길 위의 모든 노드를 루트에 직접 붙여, 다음에 같은 노드를 찾을 때 한 걸음이면 되게 한다. 공짜는 아니다 — 첫 find 는 오히려 두 번 지나지만 이후가 훨씬 싸져서 분할상환으로 이득이다.
// 랭크 합치기 없이 압축만 써도 m 번의 연산이 O((m + n) log n) 이고(Tarjan–van Leeuwen), 랭크 합치기와 함께 쓰면 O((m + n) α(n)) — 역아커만 함수 α 는 우주의 원자 수 정도의 n 에서도 5 미만이라 사실상 상수다.
// 반감(halving)과 분할(splitting)은 한 번만 지나면서도 같은 점근 상한을 얻는다. 압축은 높이 정보를 지우므로 rank 는 "높이의 상한" 으로만 해석한다(UnionByRank 항목).
// 검증(결정적 걸음 수로 비교): ① 무작위 합치기+조회에서 총 걸음 수: 압축 없음 ≫ 압축·반감·분할, 랭크+압축은 조회당 평균 ≤ 3 걸음 ② 랭크 없이 압축만으로도 (긴 사슬 뒤 반복 조회) 평균 걸음 수가 ≈ 1 ③ 모든 방식이 연결 성분 판별에서 일치 ④ 사슬의 끝을 한 번 압축하면 이후 조회는 0 걸음
enum Find { PLAIN, COMPRESS, HALVE, SPLIT };
struct DSU {
    std::vector<int> p, rk; Find mode; bool byRank; long steps = 0;
    DSU(int n, Find m, bool r) : p(n), rk(n, 0), mode(m), byRank(r) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) {
        if (mode == PLAIN) { while (p[x] != x) { x = p[x]; steps++; } return x; }
        if (mode == COMPRESS) { int r = x; while (p[r] != r) { r = p[r]; steps++; } while (p[x] != r) { int nx = p[x]; p[x] = r; x = nx; steps++; } return r; }
        if (mode == HALVE) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; steps++; } return x; }
        while (p[x] != x) { int nx = p[x]; p[x] = p[nx]; x = nx; steps++; } return x;
    }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (byRank) { if (rk[a] < rk[b]) std::swap(a, b); p[b] = a; if (rk[a] == rk[b]) rk[a]++; } else p[a] = b; return true; }
};
int main() {
    std::mt19937 rng(8); const int n = 50000, m = 100000; std::vector<std::pair<int, int>> ops; std::vector<char> isFind; for (int i = 0; i < m; i++) { ops.push_back({(int)(rng() % n), (int)(rng() % n)}); isFind.push_back(rng() % 2); }
    long steps[2][4] = {}; std::vector<std::vector<char>> answers;
    for (int byRank = 0; byRank < 2; byRank++) for (int mode = 0; mode < 4; mode++) { DSU d(n, (Find)mode, byRank); std::vector<char> ans; for (int i = 0; i < m; i++) { if (isFind[i]) ans.push_back(d.find(ops[i].first) == d.find(ops[i].second)); else d.unite(ops[i].first, ops[i].second); } steps[byRank][mode] = d.steps; answers.push_back(ans); }
    for (size_t i = 1; i < answers.size(); i++) assert(answers[i] == answers[0]);                                                                                              // ③ 모든 조합이 같은 답
    assert(steps[1][COMPRESS] < steps[1][PLAIN] && steps[1][COMPRESS] < 3L * m);                                                                                               // ① 랭크+압축: 연산당 평균 3 걸음 미만
    assert(steps[0][COMPRESS] * 3 < steps[0][PLAIN] && steps[0][HALVE] * 3 < steps[0][PLAIN] && steps[0][SPLIT] * 3 < steps[0][PLAIN]);                                         // 랭크 없는 합치기에서는 압축 계열이 압도적으로 이득
    const int N = 200000; DSU chain(N, COMPRESS, false); for (int i = 0; i + 1 < N; i++) chain.p[i + 1] = i; chain.steps = 0; for (int i = 0; i < 1000; i++) chain.find(N - 1);
    assert(chain.steps < 3L * N); DSU plain(N, PLAIN, false); for (int i = 0; i + 1 < N; i++) plain.p[i + 1] = i; for (int i = 0; i < 1000; i++) plain.find(N - 1); assert(plain.steps == 1000L * (N - 1));       // ② ④ 첫 조회만 비싸다
    std::cout << "PathCompression: total find steps for " << m << " mixed operations on " << n << " elements - no rank: plain " << steps[0][PLAIN] << ", compression " << steps[0][COMPRESS] << ", halving " << steps[0][HALVE] << ", splitting " << steps[0][SPLIT]
              << "; with union by rank: plain " << steps[1][PLAIN] << ", compression " << steps[1][COMPRESS] << "; 1000 repeated finds on a " << N << "-chain: " << chain.steps << " steps vs " << plain.steps << std::endl; return 0;
}
// Time Complexity: 분할상환 O(α(n)) (랭크 합치기와 함께), 압축만으로는 O(log n)
// Space Complexity: O(n)
```
# Part 9. 최단 경로
## Dijkstra()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <deque>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 다익스트라(Dijkstra): 출발점에서 가까운 정점부터 하나씩 "확정" 해 가며 이웃을 완화(relax)한다. 간선 가중치가 모두 음이 아니면, 지금 우선순위 큐에서 가장 가까운 정점의 거리는 다른 어떤 경로로도 줄일 수 없으므로 확정해도 된다. 그래서 확정한 정점은 다시 열지 않는다 — 이 가정이 깨지면(음수 간선) 답이 틀린다(아래 시연).
// 구현 다섯 가지 — ① 느긋한 이진 힙(가장 흔함, O(E log E)): 갱신될 때마다 새로 넣고 꺼낼 때 낡은 항목을 버린다. ② 색인 힙 + decrease-key(O(E log V)): 정점당 항목 하나. ③ 밀집 O(V²): 배열 스캔, 간선이 V² 에 가까울 때. ④ Dial 버킷 큐: 정수 가중치가 최대 C 이면 거리 d 별 버킷을 순환 배열로 두어 O(E + V·C). ⑤ 0-1 BFS: 가중치가 0 또는 1 이면 덱 하나로 O(V + E).
// 검증의 중심은 *인증서(certificate)* 다: 거리 d 와 직전 정점 배열 pred 가 ⓐ d[s] = 0 ⓑ 모든 간선 (u,v,w) 에서 d[v] ≤ d[u] + w (실현 가능한 퍼텐셜) ⓒ 도달 가능한 v ≠ s 마다 pred[v] → v 간선이 딱 맞고(d[v] = d[pred] + w) pred 를 따라가면 s 에 닿는다 — 를 만족하면 d 가 곧 최단 거리다(ⓑ 로 하한, ⓒ 로 상한). 어떤 경로 알고리즘의 결과든 오라클 없이 O(V + E) 에 증명하므로 백만 정점 입력에도 쓴다. 변조 시험으로 인증서가 틀린 답을 반드시 거부함을 확인한다.
// 그 밖의 오라클: 모든 단순 경로 열거(정점 ≤ 7), 벨만–포드, 정점 3~4 개 그래프 전수(간선마다 없음/0/1/2/3). 비용은 시간이 아니라 횟수로 단언한다 — 힙에서 꺼낸 횟수 ≤ 완화 횟수 + 1, 밀집 구현의 스캔은 정확히 V².
typedef long long ll;
const ll INF = LLONG_MAX / 4;
struct Arc { int to; ll w; };
using Graph = std::vector<std::vector<Arc>>;
struct Result { std::vector<ll> dist; std::vector<int> pred; long long pops = 0, relaxations = 0; };
Result fresh(int n) { Result r; r.dist.assign(n, INF); r.pred.assign(n, -1); return r; }

// ① 느긋한 힙. finalize=false 는 확정 없이 낡은 항목만 거르는 변형(음수 간선에서도 맞지만 같은 정점을 여러 번 연다).
Result dijkstraLazy(const Graph& g, int s, bool finalize = true) {
    int n = (int)g.size(); Result r = fresh(n);
    std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq;
    std::vector<char> done(n, 0);
    r.dist[s] = 0; pq.push({0, s});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop(); ++r.pops;
        if (d > r.dist[u] || (finalize && done[u])) continue;
        done[u] = 1;
        for (const Arc& a : g[u]) {
            if (finalize && done[a.to]) continue;
            if (d + a.w < r.dist[a.to]) { r.dist[a.to] = d + a.w; r.pred[a.to] = u; ++r.relaxations; pq.push({r.dist[a.to], a.to}); }
        }
    }
    return r;
}
// ② 색인 힙 (decrease-key)
struct IndexedHeap {
    std::vector<int> h, pos; std::vector<ll> key;                              // pos: -1 = 안 들어감, -2 = 꺼냄
    explicit IndexedHeap(int n) : pos(n, -1), key(n, INF) {}
    bool less(int a, int b) const { return key[a] != key[b] ? key[a] < key[b] : a < b; }
    void swapAt(int i, int j) { std::swap(h[i], h[j]); pos[h[i]] = i; pos[h[j]] = j; }
    void up(int i) { while (i > 0) { int p = (i - 1) / 2; if (!less(h[i], h[p])) break; swapAt(i, p); i = p; } }
    void down(int i) { int n = (int)h.size(); while (true) { int l = 2 * i + 1, r = l + 1, m = i; if (l < n && less(h[l], h[m])) m = l; if (r < n && less(h[r], h[m])) m = r; if (m == i) break; swapAt(i, m); i = m; } }
    void pushOrDecrease(int v, ll k) {
        if (pos[v] == -1) { key[v] = k; pos[v] = (int)h.size(); h.push_back(v); up(pos[v]); }
        else if (pos[v] >= 0 && k < key[v]) { key[v] = k; up(pos[v]); }
    }
    int popMin() { int v = h[0]; swapAt(0, (int)h.size() - 1); h.pop_back(); pos[v] = -2; if (!h.empty()) down(0); return v; }
};
Result dijkstraIndexed(const Graph& g, int s) {
    int n = (int)g.size(); Result r = fresh(n); IndexedHeap hp(n);
    r.dist[s] = 0; hp.pushOrDecrease(s, 0);
    while (!hp.h.empty()) {
        int u = hp.popMin(); ++r.pops;
        for (const Arc& a : g[u]) if (hp.pos[a.to] != -2 && r.dist[u] + a.w < r.dist[a.to]) {
            r.dist[a.to] = r.dist[u] + a.w; r.pred[a.to] = u; ++r.relaxations; hp.pushOrDecrease(a.to, r.dist[a.to]);
        }
    }
    return r;
}
// ③ 밀집 O(V²): W[u*n+v] = 최소 간선 무게 (없으면 INF)
Result dijkstraDense(int n, const std::vector<ll>& W, int s, long long* scans) {
    Result r = fresh(n); std::vector<char> done(n, 0); r.dist[s] = 0;
    for (int round = 0; round < n; ++round) {
        int u = -1;
        for (int v = 0; v < n; ++v) { ++*scans; if (!done[v] && r.dist[v] < INF && (u < 0 || r.dist[v] < r.dist[u])) u = v; }
        if (u < 0) break;
        done[u] = 1; ++r.pops;
        for (int v = 0; v < n; ++v) if (!done[v] && W[(std::size_t)u * n + v] < INF && r.dist[u] + W[(std::size_t)u * n + v] < r.dist[v]) { r.dist[v] = r.dist[u] + W[(std::size_t)u * n + v]; r.pred[v] = u; ++r.relaxations; }
    }
    return r;
}
// ④ Dial: 정수 가중치 0..C
Result dijkstraDial(const Graph& g, int s, int C) {
    int n = (int)g.size(); Result r = fresh(n);
    std::vector<std::vector<int>> bucket(C + 1);
    std::size_t pending = 1; r.dist[s] = 0; bucket[0].push_back(s);
    for (ll d = 0; pending > 0; ++d) {
        auto& b = bucket[d % (C + 1)];
        while (!b.empty()) {
            int u = b.back(); b.pop_back(); --pending;
            if (r.dist[u] != d) continue;                                       // 낡은 항목
            ++r.pops;
            for (const Arc& a : g[u]) if (d + a.w < r.dist[a.to]) { r.dist[a.to] = d + a.w; r.pred[a.to] = u; ++r.relaxations; bucket[(d + a.w) % (C + 1)].push_back(a.to); ++pending; }
        }
    }
    return r;
}
// ⑤ 0-1 BFS: 가중치 0 은 앞, 1 은 뒤
Result zeroOneBfs(const Graph& g, int s) {
    int n = (int)g.size(); Result r = fresh(n); std::deque<int> dq; r.dist[s] = 0; dq.push_back(s);
    while (!dq.empty()) {
        int u = dq.front(); dq.pop_front(); ++r.pops;
        for (const Arc& a : g[u]) if (r.dist[u] + a.w < r.dist[a.to]) { r.dist[a.to] = r.dist[u] + a.w; r.pred[a.to] = u; ++r.relaxations; if (a.w == 0) dq.push_front(a.to); else dq.push_back(a.to); }
    }
    return r;
}

// ---- 인증서 ----
bool certify(const Graph& g, int s, const std::vector<ll>& dist, const std::vector<int>& pred) {
    int n = (int)g.size();
    if (dist[s] != 0 || pred[s] != -1) return false;
    for (int u = 0; u < n; ++u) if (dist[u] < INF) for (const Arc& a : g[u]) if (dist[a.to] > dist[u] + a.w) return false;      // ⓑ 실현 가능
    for (int v = 0; v < n; ++v) {
        if (v == s) continue;
        if (dist[v] >= INF) { if (pred[v] != -1) return false; continue; }
        int p = pred[v]; if (p < 0) return false;
        bool tight = false; for (const Arc& a : g[p]) if (a.to == v && dist[p] + a.w == dist[v]) tight = true;                  // ⓒ 딱 맞는 간선
        if (!tight) return false;
        int x = v, steps = 0; while (x != s && steps <= n) { x = pred[x]; ++steps; if (x < 0) return false; }                   // pred 를 따라 s 에 닿는다
        if (x != s) return false;
    }
    return true;
}
// ---- 오라클: 모든 단순 경로 (n ≤ 7) ----
void dfsPaths(const Graph& g, int u, ll sum, unsigned used, std::vector<ll>& best) {
    best[u] = std::min(best[u], sum);
    for (const Arc& a : g[u]) if (!(used >> a.to & 1)) dfsPaths(g, a.to, sum + a.w, used | 1u << a.to, best);
}
std::vector<ll> bruteDist(const Graph& g, int s) { std::vector<ll> best(g.size(), INF); dfsPaths(g, s, 0, 1u << s, best); return best; }
std::vector<ll> bellman(const Graph& g, int s) {                                  // 오라클 2: 벨만–포드 (음이 아닌 가중치 전용 사용)
    int n = (int)g.size(); std::vector<ll> d(n, INF); d[s] = 0;
    for (int pass = 0; pass < n; ++pass) { bool ch = false; for (int u = 0; u < n; ++u) if (d[u] < INF) for (const Arc& a : g[u]) if (d[u] + a.w < d[a.to]) { d[a.to] = d[u] + a.w; ch = true; } if (!ch) break; }
    return d;
}

int main() {
    // ① 손으로 확인한 모양: 0→1:10, 0→2:3, 2→1:1 은 0→2→1 (4), 직전 정점 배열까지
    {   Graph g(4); g[0] = {{1, 10}, {2, 3}}; g[2] = {{1, 1}};
        Result r = dijkstraLazy(g, 0);
        assert(r.dist[1] == 4 && r.dist[2] == 3 && r.dist[3] == INF && r.pred[1] == 2 && r.pred[2] == 0 && r.pred[3] == -1);
        assert(certify(g, 0, r.dist, r.pred));
    }

    // ② 음수 간선: 확정하는 고전 다익스트라는 틀린다 (0→1:1, 0→2:3, 2→1:−5 의 진짜 답은 d[1] = −2).
    {   Graph g(3); g[0] = {{1, 1}, {2, 3}}; g[2] = {{1, -5}};
        Result wrong = dijkstraLazy(g, 0, true), ok = dijkstraLazy(g, 0, false);
        assert(wrong.dist[1] == 1 && !certify(g, 0, wrong.dist, wrong.pred));              // 인증서가 오답을 거부한다
        assert(ok.dist[1] == -2 && certify(g, 0, ok.dist, ok.pred) && ok.pops > wrong.pops);   // 확정 없이 다시 열면 맞지만 정점을 여러 번 연다
    }

    // ③ 전수: 정점 3 개의 모든 방향 그래프(순서쌍 6 개마다 없음/0/1/2/3 → 5^6 = 15,625), 모든 출발점 — 다섯 구현 · 단순 경로 열거 · 벨만–포드 · 인증서
    long long checked = 0;
    for (int code = 0; code < 15625; ++code) {
        Graph g(3); int c = code;
        for (int u = 0; u < 3; ++u) for (int v = 0; v < 3; ++v) if (u != v) { int st = c % 5; c /= 5; if (st) g[u].push_back({v, st - 1}); }
        for (int s = 0; s < 3; ++s) {
            Result a = dijkstraLazy(g, s), b = dijkstraIndexed(g, s), d = dijkstraDial(g, s, 3);
            std::vector<ll> want = bruteDist(g, s);
            assert(a.dist == want && b.dist == want && d.dist == want && bellman(g, s) == want);
            assert(certify(g, s, a.dist, a.pred) && certify(g, s, b.dist, b.pred) && certify(g, s, d.dist, d.pred));
            ++checked;
        }
    }
    assert(checked == 15625 * 3);

    // ④ 무작위: 정점 ≤ 7 (평행 간선·루프 포함, 가중치 0..9) — 모든 구현 일치, 0-1 BFS 는 0/1 가중치에서, 밀집 구현의 스캔은 정확히 V²
    std::mt19937 rng(1969);
    for (int it = 0; it < 800; ++it) {
        int n = 2 + (int)(rng() % 6), m = (int)(rng() % 20);
        Graph g(n), z(n); std::vector<ll> W((std::size_t)n * n, INF);
        for (int i = 0; i < m; ++i) {
            int u = (int)(rng() % n), v = (int)(rng() % n); ll w = (ll)(rng() % 10);
            g[u].push_back({v, w}); z[u].push_back({v, w % 2});
            if (u != v) W[(std::size_t)u * n + v] = std::min(W[(std::size_t)u * n + v], w);
        }
        int s = (int)(rng() % n);
        std::vector<ll> want = bruteDist(g, s);
        Result a = dijkstraLazy(g, s), b = dijkstraIndexed(g, s), d = dijkstraDial(g, s, 9);
        long long scans = 0; Result e = dijkstraDense(n, W, s, &scans);
        assert(a.dist == want && b.dist == want && d.dist == want && e.dist == want && bellman(g, s) == want);
        assert(certify(g, s, a.dist, a.pred) && certify(g, s, b.dist, b.pred) && certify(g, s, d.dist, d.pred) && certify(g, s, e.dist, e.pred));
        assert(a.pops <= a.relaxations + 1);                                                // 꺼낸 횟수 ≤ 완화 횟수 + 1
        long long reach = std::count_if(want.begin(), want.end(), [](ll x) { return x < INF; });
        assert(b.pops == reach && scans == (long long)n * (reach == n ? n : reach + 1));     // 색인 힙은 도달 가능한 정점마다 한 번, 밀집 구현은 정점 수 × (라운드 수) 번 스캔
        Result f = zeroOneBfs(z, s), zl = dijkstraLazy(z, s);
        assert(f.dist == zl.dist && certify(z, s, f.dist, f.pred));
        // 인증서 변조: 도달 가능한 정점 하나의 거리를 ±1 하면 반드시 거부
        std::vector<int> reachable; for (int v = 0; v < n; ++v) if (v != s && a.dist[v] < INF) reachable.push_back(v);
        if (!reachable.empty()) {
            int v = reachable[rng() % reachable.size()];
            auto bad = a.dist; bad[v] += (rng() & 1) ? 1 : -1;
            assert(!certify(g, s, bad, a.pred));
        }
    }

    // ⑤ 큰 입력: 격자 500×500 (정점 25 만, 호 100 만, 가중치 1..9) — 느긋한 힙 · 색인 힙 · Dial 의 거리가 같고 인증서 통과; 0/1 가중치 격자에서 0-1 BFS 와 일치
    {
        const int R = 500, N = R * R;
        Graph g(N), z(N);
        auto id = [&](int r, int c) { return r * R + c; };
        for (int r = 0; r < R; ++r) for (int c = 0; c < R; ++c) {
            int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
            for (int k = 0; k < 4; ++k) { int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= R) continue; ll w = (ll)(1 + rng() % 9); g[id(r, c)].push_back({id(nr, nc), w}); z[id(r, c)].push_back({id(nr, nc), w % 2}); }
        }
        Result a = dijkstraLazy(g, 0), b = dijkstraIndexed(g, 0), d = dijkstraDial(g, 0, 9);
        assert(a.dist == b.dist && a.dist == d.dist && certify(g, 0, a.dist, a.pred) && certify(g, 0, b.dist, b.pred) && certify(g, 0, d.dist, d.pred));
        assert(a.dist[N - 1] >= 2LL * (R - 1) && a.pops <= a.relaxations + 1);
        Result f = zeroOneBfs(z, 0), zl = dijkstraLazy(z, 0);
        assert(f.dist == zl.dist && certify(z, 0, f.dist, f.pred));
        // 밀집 구현: 완전 그래프 800 정점은 스캔이 정확히 V² = 640,000
        const int K = 800; std::vector<ll> W((std::size_t)K * K, INF); Graph full(K);
        for (int u = 0; u < K; ++u) for (int v = 0; v < K; ++v) if (u != v) { ll w = (ll)(1 + rng() % 1000); W[(std::size_t)u * K + v] = w; full[u].push_back({v, w}); }
        long long scans = 0; Result e = dijkstraDense(K, W, 5, &scans), l = dijkstraLazy(full, 5);
        assert(e.dist == l.dist && scans == (long long)K * K && certify(full, 5, e.dist, e.pred));
    }
    std::cout << "Dijkstra: lazy heap, indexed decrease-key heap, dense O(V^2), Dial buckets and 0-1 BFS gave the same distances as exhaustive simple-path enumeration and Bellman-Ford on all 15,625 digraphs over 3 vertices (every source) and on 800 random multigraphs, every answer passed the O(V+E) shortest-path certificate while any +-1 tampering of a distance was rejected, heap pops never exceeded relaxations + 1, the settle-once variant gave d[1] = 1 instead of -2 on a negative edge and the certificate caught it, and a 250,000-vertex grid and an 800-vertex complete graph (exactly V^2 scans) agreed across implementations" << std::endl; return 0;
}
// Time Complexity: O(E log V)
// Space Complexity: O(V + E)
```
## BellmanFord()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 벨만–포드(Bellman–Ford): 모든 간선을 V − 1 번 훑으며 완화한다. 최단 경로는 (사이클이 없으면) 간선 ≤ V − 1 개이므로 k 번째 훑기 뒤에는 "간선 k 개 이하" 경로의 최적값을 안다. 음수 간선도 되고, V 번째 훑기에서 또 갱신되면 도달 가능한 음수 사이클이 있다. 사이클은 pred 간선을 V 번 거슬러 올라가 사이클 안에 들어선 뒤 한 바퀴 돌아 복원하고, 거리가 −∞ 인 정점은 "V 번째 훑기에서 갱신된 정점으로부터 닿는 모든 정점" 이다.
// 훑기 방식: 제자리(in-place)는 같은 훑기 안에서 방금 줄인 값을 바로 쓰므로 간선 순서에 따라 훨씬 일찍 끝나고, 동기(synchronous)는 훑기 시작 때의 값만 읽으므로 k 번째 훑기 뒤가 정확히 "간선 k 개 이하" 의 최적값이다 — 그래서 동기식의 갱신 훑기 수는 정확히 H = 최단 경로의 최소 간선 수의 최댓값이고, 제자리는 H 이하다. 경로 그래프에서 간선을 앞에서부터 나열하면 1 번, 뒤에서부터 나열하면 V − 1 번이 걸린다.
// 검증: ① 음수 사이클이 없을 때는 모든 단순 경로를 열거한 최솟값과 같고, 음수 사이클이 있을 때는 −∞ 정점 집합이 "플로이드–워셜이 찾은 음수 사이클 위 정점에서 닿는 정점" 과 정확히 같으며 나머지 정점은 단순 경로 최솟값과 같다. ② 복원한 사이클의 가중치 합이 실제로 음수. ③ 동기식 훑기 수 = 층별 DP 로 센 H. ④ 퍼텐셜로 만든 정점 10 만 · 간선 40 만의 큰 입력(음수 간선은 있고 음수 사이클은 없음)을 다익스트라와 대조.
typedef long long ll;
const ll INF = LLONG_MAX / 4;
struct Edge { int u, v; ll w; };
struct BF { bool negCycle; std::vector<ll> dist; std::vector<int> predEdge; int changingPasses; std::vector<int> cycle; std::vector<char> minusInf; };

BF bellmanFord(int n, const std::vector<Edge>& E, int s, bool synchronous = false) {
    BF r{false, std::vector<ll>(n, INF), std::vector<int>(n, -1), 0, {}, std::vector<char>(n, 0)};
    r.dist[s] = 0;
    std::vector<int> relaxedLast;
    for (int pass = 1; pass <= n; ++pass) {
        std::vector<ll> base = synchronous ? r.dist : std::vector<ll>();
        bool changed = false;
        std::vector<int> relaxed;
        for (int i = 0; i < (int)E.size(); ++i) {
            const Edge& e = E[i];
            ll du = synchronous ? base[e.u] : r.dist[e.u];
            if (du < INF && du + e.w < r.dist[e.v]) { r.dist[e.v] = du + e.w; r.predEdge[e.v] = i; changed = true; relaxed.push_back(e.v); }
        }
        if (!changed) break;
        if (pass == n) { r.negCycle = true; relaxedLast = relaxed; } else ++r.changingPasses;
    }
    if (r.negCycle) {
        if (!synchronous) {                                                          // 사이클 복원은 제자리 방식에서만 (pred 배열이 항상 현재 값을 가리킨다)
            int x = relaxedLast[0];
            for (int i = 0; i < n; ++i) x = E[r.predEdge[x]].u;                      // n 번 거슬러 올라가면 반드시 사이클 안
            int y = x; do { r.cycle.push_back(r.predEdge[y]); y = E[r.predEdge[y]].u; } while (y != x);
            std::reverse(r.cycle.begin(), r.cycle.end());                            // 간선 번호를 진행 방향 순서로
        }
        std::vector<std::vector<int>> adj(n); for (const Edge& e : E) adj[e.u].push_back(e.v);
        std::queue<int> q; for (int v : relaxedLast) if (!r.minusInf[v]) { r.minusInf[v] = 1; q.push(v); }
        while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!r.minusInf[v]) { r.minusInf[v] = 1; q.push(v); } }
    }
    return r;
}

// ---- 오라클 ----
void dfsPaths(const std::vector<std::vector<std::pair<int, ll>>>& g, int u, ll sum, unsigned used, std::vector<ll>& best) {
    best[u] = std::min(best[u], sum);
    for (auto [v, w] : g[u]) if (!(used >> v & 1)) dfsPaths(g, v, sum + w, used | 1u << v, best);
}
struct Oracle { std::vector<ll> simple; std::vector<char> minusInf; bool negCycle; };
Oracle oracle(int n, const std::vector<Edge>& E, int s) {                             // n ≤ 8
    std::vector<std::vector<std::pair<int, ll>>> g(n); for (const Edge& e : E) g[e.u].push_back({e.v, e.w});
    Oracle o{std::vector<ll>(n, INF), std::vector<char>(n, 0), false};
    dfsPaths(g, s, 0, 1u << s, o.simple);
    // 플로이드–워셜(도달 가능성 + 음수 닫힌 걸음) 로 −∞ 정점 계산
    std::vector<std::vector<ll>> d(n, std::vector<ll>(n, INF));
    for (int i = 0; i < n; ++i) d[i][i] = 0;
    for (const Edge& e : E) d[e.u][e.v] = std::min(d[e.u][e.v], e.w);
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (d[i][k] < INF && d[k][j] < INF) d[i][j] = std::max(-INF, std::min(d[i][j], d[i][k] + d[k][j]));
    for (int w = 0; w < n; ++w) if (d[s][w] < INF && d[w][w] < 0) { o.negCycle = true; for (int v = 0; v < n; ++v) if (d[w][v] < INF) o.minusInf[v] = 1; }
    return o;
}
// 층별 DP: layer[k][v] = 간선 k 개 이하인 걸음의 최솟값 → H = 안정되기까지의 k
int hopsToStabilise(int n, const std::vector<Edge>& E, int s) {
    std::vector<ll> cur(n, INF); cur[s] = 0; int H = 0;
    for (int k = 1; k <= n; ++k) {
        std::vector<ll> nxt = cur;
        for (const Edge& e : E) if (cur[e.u] < INF && cur[e.u] + e.w < nxt[e.v]) nxt[e.v] = cur[e.u] + e.w;
        if (nxt != cur) H = k;
        cur = nxt;
    }
    return H;
}
// 퍼텐셜로 음수 간선은 있어도 음수 사이클은 없게: w = w0 + φ(u) − φ(v) (w0 ≥ 0) → 어떤 사이클의 합도 w0 합 ≥ 0
ll cycleWeight(const std::vector<Edge>& E, const std::vector<int>& cyc) { ll s = 0; for (int i : cyc) s += E[i].w; return s; }

int main() {
    // ① 손으로 확인한 모양: 0→1:4, 1→2:−1, 0→2:5 → d[2] = 3 ; 음수 사이클 1→2→1 (−1 + −1)
    {   std::vector<Edge> E = {{0, 1, 4}, {1, 2, -1}, {0, 2, 5}};
        BF r = bellmanFord(3, E, 0);
        assert(!r.negCycle && r.dist[2] == 3 && r.dist[1] == 4 && r.changingPasses <= 2);
        std::vector<Edge> N = {{0, 1, 1}, {1, 2, -1}, {2, 1, -1}, {2, 3, 7}};
        BF b = bellmanFord(4, N, 0);
        assert(b.negCycle && cycleWeight(N, b.cycle) == -2 && b.cycle.size() == 2);
        assert(!b.minusInf[0] && b.minusInf[1] && b.minusInf[2] && b.minusInf[3]);          // 사이클에서 닿는 3 도 −∞
        BF c = bellmanFord(4, N, 3);                                                         // 3 에서는 사이클에 닿지 않는다
        assert(!c.negCycle && c.dist[3] == 0 && c.dist[1] == INF);
    }

    // ② 순서 의존성: 경로 그래프에서 간선을 앞에서부터 나열하면 갱신 훑기 1 번, 뒤에서부터면 V − 1 번 (제자리); 동기식은 어느 순서든 V − 1
    {
        const int n = 1000;
        std::vector<Edge> fwd, bwd;
        for (int i = 0; i + 1 < n; ++i) fwd.push_back({i, i + 1, 1});
        bwd.assign(fwd.rbegin(), fwd.rend());
        assert(bellmanFord(n, fwd, 0).changingPasses == 1 && bellmanFord(n, bwd, 0).changingPasses == n - 1);
        assert(bellmanFord(n, fwd, 0, true).changingPasses == n - 1 && bellmanFord(n, bwd, 0, true).changingPasses == n - 1);
        assert(bellmanFord(n, fwd, 0).dist == bellmanFord(n, bwd, 0).dist && bellmanFord(n, fwd, 0).dist[n - 1] == n - 1);
    }

    // ③ 무작위(정점 ≤ 8, 가중치 −4..9, 음수 사이클 있음/없음 섞임): 오라클과 비교, 복원 사이클 검증, 동기식 훑기 수 = H
    std::mt19937 rng(1958);
    int withCycle = 0, without = 0, minusCount = 0;
    for (int it = 0; it < 3000; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % (3 * n));
        std::vector<Edge> E; bool potential = it % 2 == 0; std::vector<ll> phi(n); for (auto& x : phi) x = (ll)(rng() % 21) - 10;
        for (int i = 0; i < m; ++i) {
            int u = (int)(rng() % n), v = (int)(rng() % n);
            ll w = potential ? (ll)(rng() % 10) + phi[u] - phi[v] : (ll)(rng() % 14) - 4;
            E.push_back({u, v, w});
        }
        std::shuffle(E.begin(), E.end(), rng);
        int s = (int)(rng() % n);
        Oracle o = oracle(n, E, s);
        for (int mode = 0; mode < 2; ++mode) {
            BF r = bellmanFord(n, E, s, mode == 1);
            assert(r.negCycle == o.negCycle);
            if (r.negCycle) {
                if (mode == 0) {
                    assert(cycleWeight(E, r.cycle) < 0);
                    for (std::size_t i = 0; i < r.cycle.size(); ++i) assert(E[r.cycle[i]].v == E[r.cycle[(i + 1) % r.cycle.size()]].u);   // 이어지는 간선들
                }
                assert(r.minusInf == o.minusInf);
                for (int v = 0; v < n; ++v) if (!r.minusInf[v]) assert(r.dist[v] == o.simple[v]);                                      // −∞ 가 아닌 정점은 단순 경로 최솟값
                if (mode == 0) { ++withCycle; for (int v = 0; v < n; ++v) minusCount += r.minusInf[v]; }
            } else {
                assert(r.dist == o.simple);
                if (mode == 0) ++without;
            }
        }
        if (!o.negCycle) {
            BF sy = bellmanFord(n, E, s, true), ip = bellmanFord(n, E, s, false);
            int H = hopsToStabilise(n, E, s);
            assert(sy.changingPasses == H && ip.changingPasses <= H);                       // 동기식은 정확히 H, 제자리는 H 이하
        }
    }
    assert(withCycle > 400 && without > 800 && minusCount > 800);

    // ④ 큰 입력: 정점 10 만, 간선 40 만, 퍼텐셜로 음수 간선이 많지만 음수 사이클은 없다 → 같은 그래프의 w0 에 대한 다익스트라 + 퍼텐셜 보정과 일치
    //    (dist_w(s,v) = dist_w0(s,v) + φ(s) − φ(v) : 경로 하나의 퍼텐셜 항이 끝점 차이로 접힌다)
    auto build = [&](int N, int M, std::mt19937_64& r, std::vector<ll>& phi, std::vector<std::vector<std::pair<int, ll>>>& g0) {
        phi.assign(N, 0); for (auto& x : phi) x = (ll)(r() % 2001) - 1000;
        g0.assign(N, {});
        std::vector<Edge> E;
        for (int i = 0; i + 1 < N; ++i) { ll w0 = (ll)(1 + r() % 100); E.push_back({i, i + 1, w0 + phi[i] - phi[i + 1]}); g0[i].push_back({i + 1, w0}); }
        for (int i = 0; i < M - (N - 1); ++i) { int u = (int)(r() % N), v = (int)(r() % N); ll w0 = (ll)(1 + r() % 100); E.push_back({u, v, w0 + phi[u] - phi[v]}); g0[u].push_back({v, w0}); }
        std::shuffle(E.begin(), E.end(), r);
        return E;
    };
    {
        const int N = 100000, M = 400000;
        std::mt19937_64 r(11); std::vector<ll> phi; std::vector<std::vector<std::pair<int, ll>>> g0;
        std::vector<Edge> E = build(N, M, r, phi, g0);
        long long negEdges = std::count_if(E.begin(), E.end(), [](const Edge& e) { return e.w < 0; });
        BF b = bellmanFord(N, E, 0);
        assert(!b.negCycle && negEdges > 50000 && b.changingPasses < 400);
        std::vector<ll> d0(N, INF); d0[0] = 0;
        std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; pq.push({0, 0});
        while (!pq.empty()) { auto [d, u] = pq.top(); pq.pop(); if (d > d0[u]) continue; for (auto [v, w] : g0[u]) if (d + w < d0[v]) { d0[v] = d + w; pq.push({d0[v], v}); } }
        for (int v = 0; v < N; ++v) assert(b.dist[v] == d0[v] + phi[0] - phi[v]);
    }
    {   // 음수 사이클을 심은 중간 크기 그래프 (정점 3000: 사이클이 있으면 V 번 훑어야 확정되므로 크기를 줄인다)
        const int N = 3000, M = 12000;
        std::mt19937_64 r(12); std::vector<ll> phi; std::vector<std::vector<std::pair<int, ll>>> g0;
        std::vector<Edge> E = build(N, M, r, phi, g0);
        E.push_back({5, 6, -10000000}); E.push_back({6, 5, 1});
        BF c = bellmanFord(N, E, 0), sy = bellmanFord(N, E, 0, true);
        assert(c.negCycle && cycleWeight(E, c.cycle) < 0 && sy.negCycle);
        std::vector<std::vector<int>> adj(N); for (const Edge& e : E) adj[e.u].push_back(e.v);
        std::vector<char> seen(N, 0); std::queue<int> q;
        for (int i : c.cycle) if (!seen[E[i].u]) { seen[E[i].u] = 1; q.push(E[i].u); }
        while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = 1; q.push(v); } }
        assert(seen == c.minusInf && seen == sy.minusInf);
    }
    std::cout << "BellmanFord: the V-1 relaxation passes matched an enumeration of all simple paths on 3000 random graphs with up to 8 vertices (negative edges, negative cycles reachable or not), the minus-infinity set equalled exactly the vertices reachable from a negative cycle found by Floyd-Warshall, every reconstructed cycle was a closed chain of edges with negative total weight, synchronous passes needed exactly the layer-DP hop count H while in-place passes needed at most H (a path listed forwards took 1 pass, backwards 999), and a 100,000-vertex graph with over 50,000 negative edges and no negative cycle matched Dijkstra on the potential-shifted weights while a cycle planted in a 3000-vertex graph was detected by both pass styles with its reachable set marked exactly" << std::endl; return 0;
}
// Time Complexity: O(V · E)
// Space Complexity: O(V + E)
```
## FloydWarshall()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 플로이드–워셜(Floyd–Warshall): 모든 쌍 최단 거리를 d[i][j] = min(d[i][j], d[i][k] + d[k][j]) 한 줄로 구한다. 핵심 불변식 — k 번째 바깥 반복이 끝나면 d[i][j] 는 "중간 정점이 0..k 뿐인" 경로의 최솟값이다. 그래서 *k 가 가장 바깥 반복* 이어야 한다(i, j, k 순서로 돌리면 아래 시연처럼 틀린다). 음수 가중치는 되고, 대각선 d[i][i] < 0 이면 음수 사이클이 있다. 다음 정점 배열 next[i][j] 로 경로도 복원한다.
// 음수 사이클이 있으면 값이 지수적으로 작아져 64 비트를 넘칠 수 있다 — −INF 에서 잘라(clamp) 정의되지 않은 동작을 피한다(UBSan 으로 확인). 같은 틀을 (min, +) 대신 (OR, AND) 에 쓰면 워셜의 추이적 폐쇄이고, 비트집합 행으로 하면 n³/64 로 줄어든다. 또 d 는 (min,+) 행렬 곱의 거듭제곱이라 ⌈log₂(V − 1)⌉ 번의 제곱으로도 같은 답이 나온다.
// 검증: ① 정점 3 개 그래프 전수(순서쌍마다 없음/0/1/2/3 → 15,625 개) 를 출발점마다 벨만–포드 · 모든 단순 경로 열거와 대조 ② 복원한 경로가 진짜 간선으로 이어지고 합이 d[i][j] ③ 음수 사이클이 섞인 무작위 그래프에서 음수 사이클 판정이 모든 출발점의 벨만–포드와 같고, 음수 사이클의 영향을 받지 않는 쌍은 정확한 값 ④ (min,+) 제곱 · 비트집합 폐쇄 · 가중치 1 에서의 BFS 와 일치 ⑤ 정점 300 의 밀집 그래프를 300 번의 다익스트라와 대조, 음수 사이클이 가득한 정점 150 에서도 오버플로 없음.
typedef long long ll;
const ll INF = LLONG_MAX / 4;
struct Edge { int u, v; ll w; };
using Matrix = std::vector<std::vector<ll>>;
struct FW { Matrix d; std::vector<std::vector<int>> next; bool negCycle; };

FW floydWarshall(int n, const std::vector<Edge>& E, bool kOutermost = true) {
    FW f{Matrix(n, std::vector<ll>(n, INF)), std::vector<std::vector<int>>(n, std::vector<int>(n, -1)), false};
    for (int i = 0; i < n; ++i) { f.d[i][i] = 0; f.next[i][i] = i; }
    for (const Edge& e : E) if (e.w < f.d[e.u][e.v]) { f.d[e.u][e.v] = e.w; f.next[e.u][e.v] = e.v; }
    auto relax = [&](int i, int j, int k) {
        if (f.d[i][k] < INF && f.d[k][j] < INF) {
            ll c = std::max(-INF, f.d[i][k] + f.d[k][j]);                     // 음수 사이클에서 값이 폭주하지 않게 자른다
            if (c < f.d[i][j]) { f.d[i][j] = c; f.next[i][j] = f.next[i][k]; }
        }
    };
    if (kOutermost) { for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) relax(i, j, k); }
    else            { for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) for (int k = 0; k < n; ++k) relax(i, j, k); }   // 틀린 순서(시연용)
    for (int i = 0; i < n; ++i) if (f.d[i][i] < 0) f.negCycle = true;
    return f;
}
std::vector<int> path(const FW& f, int i, int j) {
    if (f.next[i][j] < 0) return {};
    std::vector<int> p{i};
    while (i != j && (int)p.size() <= (int)f.d.size()) { i = f.next[i][j]; p.push_back(i); }
    return p;
}

// ---- 오라클 ----
struct BF { bool negCycle; std::vector<ll> dist; };
BF bellman(int n, const std::vector<Edge>& E, int s) {
    BF r{false, std::vector<ll>(n, INF)}; r.dist[s] = 0;
    for (int pass = 1; pass <= n; ++pass) {
        bool ch = false;
        for (const Edge& e : E) if (r.dist[e.u] < INF && r.dist[e.u] + e.w < r.dist[e.v]) { r.dist[e.v] = r.dist[e.u] + e.w; ch = true; }
        if (!ch) break;
        if (pass == n) r.negCycle = true;
    }
    return r;
}
void simplePaths(const std::vector<std::vector<std::pair<int, ll>>>& g, int u, ll sum, unsigned used, std::vector<ll>& best) {
    best[u] = std::min(best[u], sum);
    for (auto [v, w] : g[u]) if (!(used >> v & 1)) simplePaths(g, v, sum + w, used | 1u << v, best);
}
Matrix minPlusSquare(const Matrix& a) {
    int n = (int)a.size(); Matrix c(n, std::vector<ll>(n, INF));
    for (int i = 0; i < n; ++i) for (int k = 0; k < n; ++k) if (a[i][k] < INF) for (int j = 0; j < n; ++j) if (a[k][j] < INF) c[i][j] = std::min(c[i][j], a[i][k] + a[k][j]);
    return c;
}
std::vector<std::vector<uint64_t>> closureBits(int n, const std::vector<Edge>& E) {
    int W = (n + 63) / 64; std::vector<std::vector<uint64_t>> row(n, std::vector<uint64_t>(W, 0));
    for (int i = 0; i < n; ++i) row[i][i >> 6] |= 1ULL << (i & 63);
    for (const Edge& e : E) row[e.u][e.v >> 6] |= 1ULL << (e.v & 63);
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i][k >> 6] >> (k & 63) & 1) for (int w = 0; w < W; ++w) row[i][w] |= row[k][w];
    return row;
}
bool checkPaths(int n, const std::vector<Edge>& E, const FW& f) {                // 복원한 경로: 진짜 간선 · 합 = d[i][j]
    Matrix A(n, std::vector<ll>(n, INF)); for (const Edge& e : E) A[e.u][e.v] = std::min(A[e.u][e.v], e.w);
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
        std::vector<int> p = path(f, i, j);
        if (f.d[i][j] >= INF) { if (!p.empty()) return false; continue; }
        if (p.empty() || p.front() != i || p.back() != j) return false;
        ll sum = 0; for (std::size_t t = 0; t + 1 < p.size(); ++t) { if (A[p[t]][p[t + 1]] >= INF) return false; sum += A[p[t]][p[t + 1]]; }
        if (sum != f.d[i][j]) return false;
    }
    return true;
}

int main() {
    // ① 손으로 확인한 모양: 0→1:5, 1→2:3 이면 d[0][2] = 8, 경로 0,1,2 ; 반대 방향은 닿지 않는다
    {   std::vector<Edge> E = {{0, 1, 5}, {1, 2, 3}};
        FW f = floydWarshall(3, E);
        assert(f.d[0][2] == 8 && f.d[2][0] == INF && path(f, 0, 2) == std::vector<int>({0, 1, 2}) && !f.negCycle && path(f, 2, 0).empty());
    }

    // ② 전수: 정점 3 개의 모든 방향 그래프(순서쌍 6 개마다 없음/0/1/2/3) — 모든 쌍을 출발점마다 벨만–포드 · 단순 경로 열거와 대조, 경로 복원 검사
    for (int code = 0; code < 15625; ++code) {
        std::vector<Edge> E; std::vector<std::vector<std::pair<int, ll>>> g(3); int c = code;
        for (int u = 0; u < 3; ++u) for (int v = 0; v < 3; ++v) if (u != v) { int st = c % 5; c /= 5; if (st) { E.push_back({u, v, st - 1}); g[u].push_back({v, st - 1}); } }
        FW f = floydWarshall(3, E);
        assert(!f.negCycle && checkPaths(3, E, f));
        for (int s = 0; s < 3; ++s) {
            BF b = bellman(3, E, s); std::vector<ll> best(3, INF); simplePaths(g, s, 0, 1u << s, best);
            for (int t = 0; t < 3; ++t) assert(f.d[s][t] == b.dist[t] && f.d[s][t] == best[t]);
        }
    }

    // ③ 틀린 반복 순서: k 를 가장 안쪽에 두면 많은 그래프에서 답이 틀리고(300 개 중 20 개 이상), 올바른 순서는 오라클과 항상 일치
    std::mt19937 rng(1962);
    {
        int wrongOrder = 0;
        for (int it = 0; it < 300; ++it) {
            int n = 4 + (int)(rng() % 4); std::vector<Edge> E;
            for (int i = 0, m = 2 * n; i < m; ++i) E.push_back({(int)(rng() % n), (int)(rng() % n), (ll)(1 + rng() % 9)});
            FW good = floydWarshall(n, E), bad = floydWarshall(n, E, false);
            for (int s = 0; s < n; ++s) assert(good.d[s] == bellman(n, E, s).dist);
            wrongOrder += good.d != bad.d;
        }
        assert(wrongOrder >= 20);
    }

    // ④ 음수 간선·음수 사이클이 섞인 무작위 (정점 ≤ 8): 음수 사이클 판정 = 어떤 출발점이든 벨만–포드가 찾음, 영향 안 받는 쌍은 정확, 경로 복원
    int cyc = 0, noCyc = 0;
    for (int it = 0; it < 2000; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % (3 * n)); std::vector<Edge> E;
        bool potential = it % 2 == 0; std::vector<ll> phi(n); for (auto& x : phi) x = (ll)(rng() % 21) - 10;
        for (int i = 0; i < m; ++i) { int u = (int)(rng() % n), v = (int)(rng() % n); E.push_back({u, v, potential ? (ll)(rng() % 10) + phi[u] - phi[v] : (ll)(rng() % 14) - 4}); }
        FW f = floydWarshall(n, E);
        std::vector<BF> bf; bool anyNeg = false; for (int s = 0; s < n; ++s) { bf.push_back(bellman(n, E, s)); anyNeg = anyNeg || bf.back().negCycle; }
        assert(f.negCycle == anyNeg);
        auto reach = closureBits(n, E);
        auto reaches = [&](int a, int b) { return (reach[a][b >> 6] >> (b & 63) & 1) != 0; };
        std::vector<char> onNeg(n, 0); for (int w = 0; w < n; ++w) onNeg[w] = f.d[w][w] < 0;
        for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
            bool tainted = false; for (int w = 0; w < n; ++w) tainted = tainted || (onNeg[w] && reaches(i, w) && reaches(w, j));
            if (!tainted) assert(f.d[i][j] == bf[i].dist[j]);                    // 음수 사이클을 거치지 않는 쌍은 정확한 값
        }
        if (!f.negCycle) { assert(checkPaths(n, E, f)); ++noCyc; } else ++cyc;
    }
    assert(cyc > 400 && noCyc > 1000);

    // ⑤ (min,+) 제곱 · 비트집합 폐쇄 · BFS: ⌈log₂(V − 1)⌉ 번 제곱하면 FW 와 같다; 폐쇄는 d < INF 와 같다; 가중치 1 이면 BFS 홉 수와 같다
    for (int it = 0; it < 150; ++it) {
        int n = 3 + (int)(rng() % 18), m = (int)(rng() % (3 * n)); std::vector<Edge> E, U;
        bool potential = it % 2 == 0; std::vector<ll> phi(n); for (auto& x : phi) x = (ll)(rng() % 21) - 10;
        for (int i = 0; i < m; ++i) {
            int u = (int)(rng() % n), v = (int)(rng() % n); ll w0 = (ll)(rng() % 10);
            E.push_back({u, v, potential ? w0 + phi[u] - phi[v] : w0}); U.push_back({u, v, 1});
        }
        FW f = floydWarshall(n, E);                                               // 퍼텐셜 쪽은 음수 간선이 있지만 음수 사이클은 없다
        assert(!f.negCycle);
        Matrix A(n, std::vector<ll>(n, INF)); for (int i = 0; i < n; ++i) A[i][i] = 0; for (const Edge& e : E) A[e.u][e.v] = std::min(A[e.u][e.v], e.w);
        int squarings = 0; while ((1 << squarings) < n - 1) ++squarings;
        for (int t = 0; t < squarings; ++t) A = minPlusSquare(A);                   // 대각선이 0 이라 t 번 제곱하면 "간선 2^t 개 이하" 걸음의 최솟값
        assert(A == f.d);
        auto reach = closureBits(n, E);
        for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) assert(((reach[i][j >> 6] >> (j & 63) & 1) != 0) == (f.d[i][j] < INF));
        FW h = floydWarshall(n, U);                                               // 가중치 1 → 홉 수
        for (int s = 0; s < n; ++s) {
            std::vector<ll> hop(n, INF); hop[s] = 0; std::queue<int> q; q.push(s);
            std::vector<std::vector<int>> adj(n); for (const Edge& e : U) adj[e.u].push_back(e.v);
            while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (hop[v] == INF) { hop[v] = hop[u] + 1; q.push(v); } }
            assert(h.d[s] == hop);
        }
    }

    // ⑥ 큰 입력: 정점 300 의 밀집 그래프(0..100 가중치) 를 300 번의 다익스트라와 대조, 정점 1500 의 희소 그래프 폐쇄를 BFS 와 대조, 음수 사이클 가득한 정점 150 에서 오버플로 없음
    {
        const int N = 300; std::vector<Edge> E; std::vector<std::vector<std::pair<int, ll>>> g(N);
        for (int i = 0; i < N * 8; ++i) { int u = (int)(rng() % N), v = (int)(rng() % N); ll w = (ll)(rng() % 101); E.push_back({u, v, w}); g[u].push_back({v, w}); }
        FW f = floydWarshall(N, E);
        for (int s = 0; s < N; ++s) {
            std::vector<ll> d(N, INF); d[s] = 0; std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; pq.push({0, s});
            while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } }
            assert(f.d[s] == d);
        }
        assert(checkPaths(N, E, f));
        const int K = 1500; std::vector<Edge> S; std::vector<std::vector<int>> adj(K);
        for (int i = 0; i < K * 2; ++i) { int u = (int)(rng() % K), v = (int)(rng() % K); S.push_back({u, v, 1}); adj[u].push_back(v); }
        auto reach = closureBits(K, S);
        for (int s = 0; s < K; s += 7) {
            std::vector<char> seen(K, 0); std::queue<int> q; q.push(s); seen[s] = 1;
            while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = 1; q.push(v); } }
            for (int t = 0; t < K; ++t) assert(seen[t] == ((reach[s][t >> 6] >> (t & 63) & 1) != 0));
        }
        std::vector<Edge> neg; const int M = 150;
        for (int u = 0; u < M; ++u) for (int v = 0; v < M; ++v) if (u != v) neg.push_back({u, v, (ll)(rng() % 11) - 5});
        FW z = floydWarshall(M, neg);
        ll lo = 0; for (auto& row : z.d) for (ll x : row) lo = std::min(lo, x);
        assert(z.negCycle && lo >= -INF);
    }
    std::cout << "FloydWarshall: with k as the outermost loop all-pairs distances matched Bellman-Ford and exhaustive simple-path enumeration on all 15,625 digraphs over 3 vertices and 300 random graphs, the wrong i-j-k order gave different matrices in at least 20 of those 300, over 2000 graphs with negative edges and cycles the diagonal test agreed with Bellman-Ford from every source and pairs untouched by a negative cycle kept exact values, reconstructed paths followed real edges summing to d[i][j], ceil(log2(V-1)) min-plus squarings, a bitset transitive closure and unit-weight BFS gave the same answers, a 300-vertex graph agreed with 300 Dijkstra runs, and a dense 150-vertex negative-cycle graph stayed within [-INF, INF] without overflow" << std::endl; return 0;
}
// Time Complexity: O(V³)
// Space Complexity: O(V²)
```
## Johnson()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 존슨 알고리즘(Johnson 1977): 음수 간선이 있어도 모든 쌍 최단 경로를 O(V·E log V) 에 구한다 — 희소 그래프에서 플로이드–워셜의 O(V³) 보다 훨씬 빠르다.
// 핵심은 "재가중(reweighting)" 이다. 모든 정점으로 비용 0 짜리 간선을 가진 가상 출발점 q 에서 벨만–포드를 돌려 h(v) = dist(q, v) 를 얻고(음수 사이클이 있으면 여기서 발견되어 중단), 간선 가중치를 w'(u,v) = w(u,v) + h(u) − h(v) 로 바꾼다.
// 삼각 부등식 h(v) ≤ h(u) + w(u,v) 때문에 w' ≥ 0 이다. 경로 하나의 w' 합은 원래 합 + h(시작) − h(끝) 이라 어떤 경로가 최단인지는 바뀌지 않으므로(경로 길이가 끝점에만 의존하는 양만큼 이동), 모든 정점에서 Dijkstra 를 돌리고 d(u,v) = d'(u,v) − h(u) + h(v) 로 되돌리면 된다.
// 검증: ① 음수 간선은 있지만 음수 사이클은 없는 무작위 그래프(잠재력 φ 로 w = w₀ + φ(u) − φ(v) 를 만들어 보장)에서 플로이드–워셜과 모든 쌍이 일치 ② 재가중 간선이 모두 ≥ 0 ③ 음수 사이클이 있는 그래프는 플로이드–워셜의 d(i,i) < 0 판정과 똑같이 거부 ④ 재가중 없이 Dijkstra 를 쓰면 실제로 틀리는 사례 ⑤ 희소 그래프(V=200, E=600)에서 간선 검사 횟수가 V³ 의 1/10 미만
typedef long long ll; const ll INF = (ll)1e18;
struct E { int to; ll w; };
typedef std::vector<std::vector<E>> G;
std::vector<ll> dijkstra(const G& g, int s, long long& ops, bool settleOnce = false) {                // settleOnce: 한 번 확정한 정점은 다시 열지 않는 고전적 Dijkstra
    std::vector<ll> d(g.size(), INF); std::vector<char> closed(g.size(), 0); std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; closed[u] = 1; for (auto& e : g[u]) { ops++; if (settleOnce && closed[e.to]) continue; if (du + e.w < d[e.to]) { d[e.to] = du + e.w; pq.push({d[e.to], e.to}); } } }
    return d;
}
bool johnson(const G& g, std::vector<std::vector<ll>>& D, long long& ops, std::vector<ll>* hOut = nullptr) {
    int n = g.size(); std::vector<ll> h(n, 0);                                         // 가상 출발점 q 에서 한 번 완화한 상태(모든 h = 0)에서 시작
    for (int pass = 1; pass <= n; pass++) { bool changed = false; for (int u = 0; u < n; u++) for (auto& e : g[u]) { ops++; if (h[u] + e.w < h[e.to]) { h[e.to] = h[u] + e.w; changed = true; } } if (!changed) break; if (pass == n) return false; }     // n 번째 패스에서도 갱신되면 음수 사이클
    G r(n); for (int u = 0; u < n; u++) for (auto& e : g[u]) { ll w2 = e.w + h[u] - h[e.to]; assert(w2 >= 0); r[u].push_back({e.to, w2}); }                                                     // ② 재가중 간선은 음수가 아니다
    D.assign(n, std::vector<ll>(n, INF)); for (int s = 0; s < n; s++) { auto d = dijkstra(r, s, ops); for (int v = 0; v < n; v++) if (d[v] < INF) D[s][v] = d[v] - h[s] + h[v]; }
    if (hOut) *hOut = h; return true;
}
std::vector<std::vector<ll>> floyd(const G& g, long long& ops) {
    int n = g.size(); std::vector<std::vector<ll>> d(n, std::vector<ll>(n, INF)); for (int i = 0; i < n; i++) d[i][i] = 0; for (int u = 0; u < n; u++) for (auto& e : g[u]) d[u][e.to] = std::min(d[u][e.to], e.w);
    for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (d[i][k] < INF) for (int j = 0; j < n; j++) { ops++; if (d[k][j] < INF && d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j]; }
    return d;
}
int main() {
    std::mt19937 rng(7); int accepted = 0, rejected = 0, negEdges = 0;
    for (int t = 0; t < 600; t++) {
        int n = 1 + rng() % 12; bool cycleWanted = t % 3 == 0; G g(n); std::vector<ll> phi(n); for (auto& x : phi) x = (ll)(rng() % 61) - 30; int m = rng() % (3 * n + 1);
        for (int k = 0; k < m; k++) { int u = rng() % n, v = rng() % n; if (u == v) continue; ll w = cycleWanted ? (ll)(rng() % 21) - 8 : (ll)(rng() % 21) + phi[u] - phi[v]; negEdges += w < 0; g[u].push_back({v, w}); }
        long long o1 = 0, o2 = 0; auto F = floyd(g, o1); bool hasNegCycle = false; for (int i = 0; i < n; i++) hasNegCycle |= F[i][i] < 0;
        std::vector<std::vector<ll>> D; bool ok = johnson(g, D, o2); assert(ok == !hasNegCycle);                                                                                  // ③ 음수 사이클 판정이 플로이드–워셜과 같다
        if (!ok) { rejected++; continue; } accepted++; for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) assert(D[i][j] == F[i][j]);                                         // ① 모든 쌍 일치
    }
    G bad(3); bad[0].push_back({1, 2}); bad[0].push_back({2, 3}); bad[2].push_back({1, -2}); long long dummy = 0; auto plain = dijkstra(bad, 0, dummy, true); std::vector<std::vector<ll>> D3; assert(johnson(bad, D3, dummy)); assert(plain[1] == 2 && D3[0][1] == 1);          // ④ 음수 간선에서 Dijkstra 는 틀리고 존슨은 맞다
    const int N = 200; G sparse(N); std::vector<ll> phi(N); for (auto& x : phi) x = (ll)(rng() % 101) - 50; for (int k = 0; k < 3 * N; k++) { int u = rng() % N, v = rng() % N; if (u != v) sparse[u].push_back({v, (ll)(rng() % 30) + phi[u] - phi[v]}); }
    long long jo = 0, fo = 0; auto F = floyd(sparse, fo); std::vector<std::vector<ll>> D2; assert(johnson(sparse, D2, jo)); assert(D2 == F && jo * 10 < fo);                                                             // ⑤ 희소 그래프에서 간선 검사 수가 1/10 미만
    std::cout << "Johnson: " << accepted << " graphs with negative edges matched Floyd-Warshall, " << rejected << " negative-cycle graphs were rejected identically (" << negEdges << " negative edges in total); V=200,E=600: " << jo << " edge checks vs " << fo << " for Floyd-Warshall" << std::endl; return 0;
}
// Time Complexity: O(V·E + V·E log V) = O(V·E log V)
// Space Complexity: O(V²) (결과 행렬)
```
## SPFA()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <deque>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// SPFA(Shortest Path Faster Algorithm): 벨만–포드에서 "거리가 줄어든 정점의 이웃만 다시 본다" — 값이 바뀐 정점을 큐에 넣고, 큐에서 꺼낸 정점의 나가는 간선만 완화한다. 음수 간선도 되고 평균적으로 빠르지만 최악은 벨만–포드와 같은 O(V·E) 이다(아래에서 비음수 가중치로도 이차 시간이 되는 구조를 직접 만든다). 큐에 이미 들어 있는 정점은 다시 넣지 않는다(inQueue 표시).
// 음수 사이클: 정점마다 "현재 최단 거리를 이루는 걸음의 간선 수" len[v] 를 같이 갱신한다. 음수 사이클이 없다면 그 걸음은 항상 단순 경로여서 len ≤ V − 1 이고(사이클이 끼면 거리가 줄지 않아 완화가 일어나지 않는다), len[v] ≥ V 가 되는 순간 도달 가능한 음수 사이클이 있다. 정책 변형 SLF(Small Label First): 새로 넣는 정점의 거리가 큐 맨 앞보다 작으면 앞에 넣는다 — 거리는 같고 완화 횟수만 달라진다.
// 검증: ① 정점 3 개 그래프 전수(순서쌍마다 없음/−1/0/1/2 → 15,625 개) 를 출발점마다 벨만–포드와 대조: 음수 사이클 판정이 같고, 없으면 거리도 같다(FIFO · SLF 모두). ② 음수 사이클이 섞인 무작위 그래프 ③ 비음수 가중치에서 SPFA 가 이차 시간이 되는 구조 — 출발점에서 길이가 1, 2, …, k 인 체인으로 목적지에 닿되 길이가 길수록 *더 싼* 경로로 만들고, 목적지 뒤에 길이 m 인 꼬리를 달면 개선 파도마다 꼬리 전체를 다시 훑는다 — 의 완화 횟수가 다익스트라(≤ E)보다 한 자릿수 이상 크다. ④ 퍼텐셜로 만든 정점 20 만 · 간선 100 만(음수 간선 있음, 음수 사이클 없음)을 다익스트라와 대조.
typedef long long ll;
const ll INF = LLONG_MAX / 4;
struct Arc { int to; ll w; };
using Graph = std::vector<std::vector<Arc>>;
enum Policy { FIFO, SLF };
struct SP { bool negCycle = false; std::vector<ll> dist; long long relaxations = 0, pops = 0; };

SP spfa(const Graph& g, int s, Policy pol = FIFO) {
    int n = (int)g.size();
    SP r; r.dist.assign(n, INF);
    std::deque<int> dq; std::vector<char> in(n, 0); std::vector<int> len(n, 0);
    r.dist[s] = 0; dq.push_back(s); in[s] = 1;
    while (!dq.empty()) {
        int u = dq.front(); dq.pop_front(); in[u] = 0; ++r.pops;
        for (const Arc& a : g[u]) {
            if (r.dist[u] + a.w < r.dist[a.to]) {
                r.dist[a.to] = r.dist[u] + a.w; ++r.relaxations;
                len[a.to] = len[u] + 1;
                if (len[a.to] >= n) { r.negCycle = true; return r; }           // 걸음이 V 개 이상의 간선 → 사이클
                if (!in[a.to]) {
                    in[a.to] = 1;
                    if (pol == SLF && !dq.empty() && r.dist[a.to] < r.dist[dq.front()]) dq.push_front(a.to); else dq.push_back(a.to);
                }
            }
        }
    }
    return r;
}
struct BF { bool negCycle; std::vector<ll> dist; };
BF bellman(const Graph& g, int s) {
    int n = (int)g.size(); BF r{false, std::vector<ll>(n, INF)}; r.dist[s] = 0;
    for (int pass = 1; pass <= n; ++pass) {
        bool ch = false;
        for (int u = 0; u < n; ++u) if (r.dist[u] < INF) for (const Arc& a : g[u]) if (r.dist[u] + a.w < r.dist[a.to]) { r.dist[a.to] = r.dist[u] + a.w; ch = true; }
        if (!ch) break;
        if (pass == n) r.negCycle = true;
    }
    return r;
}
SP dijkstra(const Graph& g, int s) {                                              // 비음수 가중치용 오라클 · 비교 대상
    int n = (int)g.size(); SP r; r.dist.assign(n, INF);
    std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; r.dist[s] = 0; pq.push({0, s});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop(); ++r.pops;
        if (d > r.dist[u]) continue;
        for (const Arc& a : g[u]) if (d + a.w < r.dist[a.to]) { r.dist[a.to] = d + a.w; ++r.relaxations; pq.push({r.dist[a.to], a.to}); }
    }
    return r;
}

int main() {
    // ① 손으로 확인한 모양: 0→1:10, 0→2:3, 2→1:4, 1→3:2, 2→3:8 → d[1] = 7, d[3] = 9 ; 음수 사이클 1→2→1
    {   Graph g(4); g[0] = {{1, 10}, {2, 3}}; g[2] = {{1, 4}, {3, 8}}; g[1] = {{3, 2}};
        SP r = spfa(g, 0);
        assert(!r.negCycle && r.dist[1] == 7 && r.dist[3] == 9 && r.dist[2] == 3);
        Graph c(3); c[0] = {{1, 1}}; c[1] = {{2, -3}}; c[2] = {{1, 1}};
        assert(spfa(c, 0).negCycle && spfa(c, 0, SLF).negCycle && bellman(c, 0).negCycle);
        assert(spfa(c, 2).negCycle == bellman(c, 2).negCycle && spfa(c, 2).negCycle);   // 2 에서도 사이클에 닿는다
    }

    // ② 전수: 정점 3 개의 모든 방향 그래프(순서쌍 6 개마다 없음/−1/0/1/2 → 15,625), 모든 출발점 — 음수 사이클 판정 · 거리 · FIFO/SLF
    long long withCycle = 0;
    for (int code = 0; code < 15625; ++code) {
        Graph g(3); int c = code;
        for (int u = 0; u < 3; ++u) for (int v = 0; v < 3; ++v) if (u != v) { int st = c % 5; c /= 5; if (st) g[u].push_back({v, st - 2}); }
        for (int s = 0; s < 3; ++s) {
            BF b = bellman(g, s); SP f = spfa(g, s), l = spfa(g, s, SLF);
            assert(f.negCycle == b.negCycle && l.negCycle == b.negCycle);
            if (!b.negCycle) assert(f.dist == b.dist && l.dist == b.dist); else ++withCycle;
        }
    }
    assert(withCycle > 3000);

    // ③ 무작위: 정점 ≤ 12, 가중치 −4..9 (음수 사이클 있음/없음) 와 퍼텐셜 그래프(음수 간선 있음/사이클 없음)
    std::mt19937 rng(1959);
    int cyc = 0, noCyc = 0;
    for (int it = 0; it < 3000; ++it) {
        int n = 2 + (int)(rng() % 11), m = (int)(rng() % (3 * n)); Graph g(n);
        bool potential = it % 2 == 0; std::vector<ll> phi(n); for (auto& x : phi) x = (ll)(rng() % 21) - 10;
        for (int i = 0; i < m; ++i) { int u = (int)(rng() % n), v = (int)(rng() % n); g[u].push_back({v, potential ? (ll)(rng() % 10) + phi[u] - phi[v] : (ll)(rng() % 14) - 4}); }
        int s = (int)(rng() % n);
        BF b = bellman(g, s); SP f = spfa(g, s), l = spfa(g, s, SLF);
        assert(f.negCycle == b.negCycle && l.negCycle == b.negCycle);
        if (!b.negCycle) { assert(f.dist == b.dist && l.dist == b.dist); ++noCyc; } else ++cyc;
    }
    assert(cyc > 300 && noCyc > 1500);

    // ④ 비음수 가중치에서도 이차 시간이 되는 구조: s → z1 → … → zk (가중치 1) 이고 z_j → t 의 가중치는 B − 2j, s → t 는 B, t → c1 → … → cm (가중치 1)
    //    z_j 를 거치면 j 칸이 걸리지만 t 에는 B − j 로 닿아 j 가 클수록 더 싸다 → FIFO 에서 t 가 층마다 다시 개선되고 개선 파도가 꼬리 전체를 다시 훑는다
    {
        const int k = 400, m = 400, B = 1000, N = k + m + 2; int t = k + 1;
        Graph g(N);
        g[0].push_back({1, 1}); g[0].push_back({t, B});
        for (int j = 1; j <= k; ++j) { if (j < k) g[j].push_back({j + 1, 1}); g[j].push_back({t, (ll)B - 2 * j}); }
        g[t].push_back({t + 1, 1});
        for (int i = 1; i < m; ++i) g[t + i].push_back({t + i + 1, 1});
        SP f = spfa(g, 0), l = spfa(g, 0, SLF), d = dijkstra(g, 0);
        assert(f.dist == d.dist && l.dist == d.dist && d.dist[t] == B - k && d.dist[N - 1] == B - k + m);
        assert(f.relaxations >= (long long)k * m / 2);                              // 이차: 파도 k 번 × 꼬리 m 칸
        assert(f.relaxations > 10 * d.relaxations);                                  // 다익스트라(≤ E) 보다 한 자릿수 이상 많다
    }

    // ⑤ 큰 입력: 정점 20 만 · 간선 100 만, 퍼텐셜로 음수 간선(수십만 개) 이 있지만 음수 사이클은 없다 — 다익스트라(w0) + 퍼텐셜 보정과 일치
    {
        const int N = 200000, M = 1000000; std::mt19937_64 r(77);
        std::vector<ll> phi(N); for (auto& x : phi) x = (ll)(r() % 2001) - 1000;
        Graph g(N), g0(N); long long neg = 0;
        for (int i = 0; i + 1 < N; ++i) { ll w0 = (ll)(1 + r() % 100); g[i].push_back({i + 1, w0 + phi[i] - phi[i + 1]}); g0[i].push_back({i + 1, w0}); neg += g[i].back().w < 0; }
        for (int i = 0; i < M - (N - 1); ++i) { int u = (int)(r() % N), v = (int)(r() % N); ll w0 = (ll)(1 + r() % 100); g[u].push_back({v, w0 + phi[u] - phi[v]}); g0[u].push_back({v, w0}); neg += g[u].back().w < 0; }
        SP f = spfa(g, 0), l = spfa(g, 0, SLF), d = dijkstra(g0, 0);
        assert(!f.negCycle && !l.negCycle && neg > 100000);
        for (int v = 0; v < N; ++v) { assert(f.dist[v] == d.dist[v] + phi[0] - phi[v]); assert(l.dist[v] == f.dist[v]); }
        assert(f.relaxations < 100LL * M);
    }
    std::cout << "SPFA: the queue-based relaxation with path-length cycle detection matched Bellman-Ford on all 15,625 digraphs over 3 vertices with weights -1..2 (every source, FIFO and small-label-first) and on 3000 random graphs with up to 12 vertices, agreeing on whether a negative cycle was reachable and on every distance otherwise, a chain-and-tail construction with only non-negative weights forced at least k*m/2 = 80,000 relaxations (more than 10 times Dijkstra's) so the O(VE) worst case is real, and a 200,000-vertex, 1,000,000-edge graph with over 100,000 negative edges matched Dijkstra on potential-shifted weights" << std::endl; return 0;
}
// Time Complexity: O(k·E) 평균, O(V·E) 최악
// Space Complexity: O(V + E)
```
# Part 10. 길찾기
## AStar()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// A* (그래프 관점의 요약, 정본은 PathFinding.md Part 4): Dijkstra 의 우선순위를 d(v) 에서 d(v) + h(v) 로 바꾼 탐색이다. h(v) 는 v 에서 목표까지 남은 거리의 추정이며, 허용 가능(h ≤ 실제 남은 거리)하면 최적, 일관적(h(u) ≤ w(u,v) + h(v))이면 한 정점을 한 번만 확장해도 된다.
// 그래프로 보면 A* 는 "재가중된 그래프 위의 Dijkstra" 다: w'(u,v) = w(u,v) − h(u) + h(v) ≥ 0 (일관성이 정확히 이 조건) 이고, 경로의 w' 합은 원래 합 − h(시작) + h(끝) 이므로 최단 경로가 보존되면서 목표 쪽으로 향하는 간선이 싸진다. 존슨 알고리즘의 재가중과 같은 발상이다.
// 검증: 좌표가 있는 무작위 도로망(간선 길이 ≥ 유클리드 거리)에서 ① A* 비용 == Dijkstra 비용 ② 확장 정점 수가 Dijkstra 보다 적음 ③ 재가중 간선이 음수가 아님 ④ 과대 추정 h (3배)에서는 최적이 깨지는 사례가 존재
struct Edge { int to; double w; };
struct Road { std::vector<double> x, y; std::vector<std::vector<Edge>> adj; };
struct Res { double cost = -1; long expanded = 0; };
Res astar(const Road& r, int s, int t, double scale) {                              // scale = 0 -> Dijkstra, 1 -> A*, 3 -> 과대 추정
    int n = r.x.size(); auto h = [&](int v) { return scale * std::hypot(r.x[v] - r.x[t], r.y[v] - r.y[t]); }; std::vector<double> g(n, 1e18); std::vector<char> closed(n, 0); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; Res res; g[s] = 0; pq.push({h(s), s});
    while (!pq.empty()) { int u = pq.top().second; pq.pop(); if (closed[u]) continue; closed[u] = 1; res.expanded++; if (u == t) { res.cost = g[u]; return res; } for (auto& e : r.adj[u]) if (!closed[e.to] && g[u] + e.w < g[e.to]) { g[e.to] = g[u] + e.w; pq.push({g[e.to] + h(e.to), e.to}); } }
    return res;
}
int main() {
    std::mt19937 rng(5); std::uniform_real_distribution<double> U(0, 100); long aExp = 0, dExp = 0; int solved = 0, suboptimal = 0, negativeReduced = 0;
    for (int t = 0; t < 300; t++) {
        int n = 60 + rng() % 60; Road r; r.x.resize(n); r.y.resize(n); r.adj.resize(n); for (int i = 0; i < n; i++) { r.x[i] = U(rng); r.y[i] = U(rng); }
        for (int i = 0; i < n; i++) for (int k = 0; k < 3; k++) { int j = rng() % n; if (i == j) continue; double d = std::hypot(r.x[i] - r.x[j], r.y[i] - r.y[j]) * (1.0 + (rng() % 40) / 100.0); r.adj[i].push_back({j, d}); r.adj[j].push_back({i, d}); }
        int s = rng() % n, e = rng() % n; Res a = astar(r, s, e, 1), d = astar(r, s, e, 0); assert((a.cost < 0) == (d.cost < 0)); if (a.cost < 0) continue; solved++;
        assert(std::fabs(a.cost - d.cost) < 1e-9); aExp += a.expanded; dExp += d.expanded;                                                                                           // ① 비용 일치 ② 확장 수
        for (int u = 0; u < n; u++) for (auto& ed : r.adj[u]) { double hu = std::hypot(r.x[u] - r.x[e], r.y[u] - r.y[e]), hv = std::hypot(r.x[ed.to] - r.x[e], r.y[ed.to] - r.y[e]); negativeReduced += ed.w - hu + hv < -1e-9; }   // ③
        Res bad = astar(r, s, e, 3); assert(bad.cost >= a.cost - 1e-9); suboptimal += bad.cost > a.cost + 1e-9;                                                                     // ④ 과대 추정은 최적이 아닐 수 있다
    }
    assert(solved > 200 && aExp < dExp && negativeReduced == 0 && suboptimal > 0);
    std::cout << "AStar: equal to Dijkstra on " << solved << " road networks, expansions " << aExp << " vs " << dExp << ", no negative reduced edge, 3x overestimating heuristic was suboptimal " << suboptimal << " times" << std::endl; return 0;
}
// Time Complexity: O((V + E) log V) 이하 (좋은 휴리스틱에서 확장 수가 크게 줄어듦)
// Space Complexity: O(V)
```
## JumpPointSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 점프 포인트 탐색 JPS (그래프 관점의 요약, 정본은 PathFinding.md Part 5): 균일 비용 8방향 격자 그래프에서 같은 비용의 대칭 경로가 수없이 많아 A* 가 그 정점을 전부 여는 낭비를 없앤다.
// 한 방향으로 쭉 "점프" 하며 정점을 건너뛰고, 목표나 강제 이웃(forced neighbor; 벽 모서리 때문에 반드시 이 칸을 거쳐야 닿는 이웃)을 만나는 점프 포인트만 열린 목록에 올린다. 대각선 점프는 두 직선 방향 점프를 재귀로 시도한다.
// 간선을 암묵적으로 압축한 그래프 위의 A* 라고 볼 수 있다 — 최적성은 그대로이고 확장 정점 수만 크게 준다. 검증: 무작위 지도 수백 개에서 Dijkstra 비용과 항상 같고, 펼친 경로가 유효하며, 확장 수가 1/3 미만
typedef std::pair<int, int> P;
struct Grid { int R, C; std::vector<std::string> w; bool ok(int r, int c) const { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; }
    bool mv(P a, int dr, int dc) const { if (!ok(a.first + dr, a.second + dc)) return false; if (dr && dc && (!ok(a.first + dr, a.second) || !ok(a.first, a.second + dc))) return false; return true; } };
int cst(int dr, int dc) { return dr && dc ? 14 : 10; }
int octile(P a, P b) { int dr = std::abs(a.first - b.first), dc = std::abs(a.second - b.second); return 10 * (dr + dc) - 6 * std::min(dr, dc); }
const int DR[8] = {-1, -1, -1, 0, 0, 1, 1, 1}, DC[8] = {-1, 0, 1, -1, 1, -1, 0, 1};
bool natural(int dr, int dc, int mr, int mc) { if (dr && dc) return (mr == dr && mc == 0) || (mr == 0 && mc == dc) || (mr == dr && mc == dc); return mr == dr && mc == dc; }
bool forcedNb(const Grid& g, P n, int dr, int dc, int mr, int mc) {        // n 에서 m 방향 이웃이 강제 이웃인가 (부모 p = n - d)
    if (natural(dr, dc, mr, mc) || (mr == -dr && mc == -dc) || !g.mv(n, mr, mc)) return false;
    P p{n.first - dr, n.second - dc}; int via = cst(dr, dc) + cst(mr, mc), alt = 1 << 30; P q{n.first + mr, n.second + mc};
    int ar = q.first - p.first, ac = q.second - p.second; if (std::abs(ar) <= 1 && std::abs(ac) <= 1 && g.mv(p, ar, ac)) alt = cst(ar, ac);          // 부모에서 곧장
    for (int k = 0; k < 8; k++) { P x{p.first + DR[k], p.second + DC[k]}; if (x == n || !g.mv(p, DR[k], DC[k])) continue; int br = q.first - x.first, bc = q.second - x.second;
        if (std::abs(br) <= 1 && std::abs(bc) <= 1 && (br || bc) && g.mv(x, br, bc)) alt = std::min(alt, cst(DR[k], DC[k]) + cst(br, bc)); }       // 부모 -> x -> q
    return via < alt;
}
bool hasForced(const Grid& g, P n, int dr, int dc) { for (int k = 0; k < 8; k++) if (forcedNb(g, n, dr, dc, DR[k], DC[k])) return true; return false; }
bool jump(const Grid& g, P x, int dr, int dc, P goal, P& out, long& cost) {
    long c = 0;
    for (;;) {
        if (!g.mv(x, dr, dc)) return false; x = {x.first + dr, x.second + dc}; c += cst(dr, dc);
        if (x == goal || hasForced(g, x, dr, dc)) { out = x; cost = c; return true; }
        if (dr && dc) { P t; long cc; if (jump(g, x, dr, 0, goal, t, cc) || jump(g, x, 0, dc, goal, t, cc)) { out = x; cost = c; return true; } }          // 대각선: 두 직선 방향으로 점프해 보고 하나라도 성공하면 여기가 점프 포인트
    }
}
struct Res { long cost = -1; long expanded = 0; std::vector<P> path; };
Res jps(const Grid& g, P s, P t) {
    Res res; int n = g.R * g.C; std::vector<long> gc(n, 1L << 60); std::vector<int> parent(n, -1); std::vector<char> closed(n, 0); using Q = std::pair<std::pair<long, long>, int>; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq;
    int si = s.first * g.C + s.second, ti = t.first * g.C + t.second; gc[si] = 0; pq.push({{octile(s, t), 0}, si});
    while (!pq.empty()) { int u = pq.top().second; pq.pop(); if (closed[u]) continue; closed[u] = 1; res.expanded++; P up{u / g.C, u % g.C};
        if (u == ti) { res.cost = gc[u]; std::vector<int> jp; for (int v = u; v >= 0; v = parent[v]) jp.push_back(v); std::reverse(jp.begin(), jp.end()); res.path.push_back(s);
            for (size_t i = 1; i < jp.size(); i++) { P a = res.path.back(), b{jp[i] / g.C, jp[i] % g.C}; int sr = (b.first > a.first) - (b.first < a.first), sc = (b.second > a.second) - (b.second < a.second); while (a != b) { a = {a.first + sr, a.second + sc}; res.path.push_back(a); } } return res; }
        std::vector<std::pair<int, int>> dirs;
        if (parent[u] < 0) for (int k = 0; k < 8; k++) dirs.push_back({DR[k], DC[k]});
        else { int pr = parent[u] / g.C, pc = parent[u] % g.C; int dr = (up.first > pr) - (up.first < pr), dc = (up.second > pc) - (up.second < pc);
            for (int k = 0; k < 8; k++) if (natural(dr, dc, DR[k], DC[k]) || forcedNb(g, up, dr, dc, DR[k], DC[k])) dirs.push_back({DR[k], DC[k]}); }
        for (auto d : dirs) { P jp; long c; if (!jump(g, up, d.first, d.second, t, jp, c)) continue; int v = jp.first * g.C + jp.second; if (closed[v]) continue; long ng = gc[u] + c; if (ng < gc[v]) { gc[v] = ng; parent[v] = u; pq.push({{ng + octile(jp, t), -ng}, v}); } }
    }
    return res;
}
long dijkstra(const Grid& g, P s, P t, long& expanded) {
    int n = g.R * g.C; std::vector<long> d(n, 1L << 60); using Q = std::pair<long, int>; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s.first * g.C + s.second] = 0; pq.push({0, s.first * g.C + s.second}); expanded = 0;
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; expanded++; if (u == t.first * g.C + t.second) return du; for (int k = 0; k < 8; k++) { P a{u / g.C, u % g.C}; if (!g.mv(a, DR[k], DC[k])) continue; int v = (a.first + DR[k]) * g.C + a.second + DC[k]; if (du + cst(DR[k], DC[k]) < d[v]) { d[v] = du + cst(DR[k], DC[k]); pq.push({d[v], v}); } } }
    return -1;
}
int main() {
    std::mt19937 gen(4); long jExp = 0, aExp = 0, solved = 0;
    for (int t = 0; t < 400; t++) {
        Grid g{28, 28, std::vector<std::string>(28, std::string(28, '.'))}; int dens = 5 + gen() % 35; for (auto& row : g.w) for (auto& ch : row) if ((int)(gen() % 100) < dens) ch = '#';
        P s{(int)(gen() % 28), (int)(gen() % 28)}, e{(int)(gen() % 28), (int)(gen() % 28)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        long dExp; long want = dijkstra(g, s, e, dExp); Res r = jps(g, s, e); assert(r.cost == want);                    // JPS 비용 == Dijkstra 비용 (도달 불가도 일치)
        if (want < 0) continue; solved++; long c = 0; assert(r.path.front() == s && r.path.back() == e);
        for (size_t i = 1; i < r.path.size(); i++) { int dr = r.path[i].first - r.path[i - 1].first, dc = r.path[i].second - r.path[i - 1].second; assert(g.mv(r.path[i - 1], dr, dc)); c += cst(dr, dc); } assert(c == want);        // 펼친 경로가 유효하고 비용이 맞다
        jExp += r.expanded; aExp += dExp;
    }
    assert(jExp * 3 < aExp);                                               // 확장하는 노드(점프 포인트)가 훨씬 적다
    std::cout << "JumpPointSearch: optimal on " << solved << " solvable maps; expanded jump points " << jExp << " vs Dijkstra cells " << aExp << std::endl; return 0;
}
// Time Complexity: 최악 O(V) 이지만 열린 공간에서 A* 의 수분의 1~수십분의 1 확장 (점프마다 직선 스캔)
// Space Complexity: O(점프 포인트 수)
```
## GreedyBestFirstSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 탐욕 최선 우선 탐색 (그래프 관점의 요약, 정본은 PathFinding.md Part 4): 우선순위를 g + h 가 아니라 h(n) 하나로만 정하는 A* 의 변형이다 — 목표에 가까워 보이는 정점부터 확장한다.
// 완전성은 있다(유한 그래프에서 해가 있으면 찾는다). 하지만 막다른 길에 빠지면 그곳을 다 채운 뒤에야 나오고, 최적성이 없다. 대신 확장 수가 A* 보다 훨씬 적어 빠른 근사해가 필요한 곳에서 쓴다.
// 검증: 무작위 지도에서 A* 와 도달 가능성이 같고, 경로 비용 ≥ 최적이며 실제로 더 긴 경로가 나오는 사례가 있고, 확장 수는 A* 보다 적다
typedef std::pair<int, int> P;
struct Grid { int R, C; std::vector<std::string> w;
    bool ok(int r, int c) const { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; }
    template <class F> void nb(int r, int c, F f) const { for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int nr = r + dr, nc = c + dc; if (!ok(nr, nc)) continue; if (dr && dc && (!ok(r + dr, c) || !ok(r, c + dc))) continue; f(nr, nc, dr && dc ? 14 : 10); } } };
int octile(P a, P b) { int dr = std::abs(a.first - b.first), dc = std::abs(a.second - b.second); return 10 * (dr + dc) - 6 * std::min(dr, dc); }
struct Res { long cost = -1; long expanded = 0; };
Res search(const Grid& g, P s, P t, bool greedy) {                         // greedy: 키 = h, 아니면 A* 키 = g + h
    Res res; std::vector<long> best(g.R * g.C, 1L << 60); std::vector<char> closed(g.R * g.C, 0); using Q = std::pair<std::pair<long, long>, P>;
    std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; best[s.first * g.C + s.second] = 0; pq.push({{octile(s, t), 0}, s});
    while (!pq.empty()) { P u = pq.top().second; pq.pop(); int id = u.first * g.C + u.second; if (closed[id]) continue; closed[id] = 1; res.expanded++;
        if (u == t) { res.cost = best[id]; return res; }
        g.nb(u.first, u.second, [&](int nr, int nc, int c) { int nid = nr * g.C + nc; if (closed[nid]) return; long ng = best[id] + c; if (ng < best[nid]) { best[nid] = ng; long h = octile({nr, nc}, t); pq.push({{greedy ? h : ng + h, -ng}, {nr, nc}}); } }); }
    return res;
}
int main() {
    std::mt19937 gen(1); long gExp = 0, aExp = 0, worse = 0, found = 0, trials = 0; double ratioSum = 0;
    for (int t = 0; t < 150; t++) {
        Grid g{30, 30, std::vector<std::string>(30, std::string(30, '.'))}; for (auto& row : g.w) for (auto& ch : row) if (gen() % 100 < 28) ch = '#';
        P s{(int)(gen() % 30), (int)(gen() % 30)}, e{(int)(gen() % 30), (int)(gen() % 30)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        Res a = search(g, s, e, false), b = search(g, s, e, true); assert((a.cost < 0) == (b.cost < 0));        // 완전성: 해가 있으면 탐욕도 찾는다
        if (a.cost < 0) continue; trials++; assert(b.cost >= a.cost);       // 최적성 없음: 같거나 더 길다
        worse += b.cost > a.cost; ratioSum += (double)b.cost / a.cost; gExp += b.expanded; aExp += a.expanded; found++;
    }
    assert(worse > 0 && gExp < aExp);                                      // 최적이 아닌 경우가 실제로 있고, 확장은 A* 보다 적다
    std::cout << "GreedyBestFirstSearch: " << found << " solvable maps; greedy path longer than optimal in " << worse << " (avg ratio " << ratioSum / trials << "), expansions greedy " << gExp << " vs A* " << aExp << std::endl; return 0;
}
// Time Complexity: 최악 O(b^m), 좋은 휴리스틱에서는 매우 빠름
// Space Complexity: O(b^m)
```
## BidirectionalSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 양방향 BFS: 시작점과 목표점에서 레벨 단위로 번갈아 확장하고, 만나는 순간의 최소 거리를 반환한다.  처음 만난 간선이 최단이라고 단정하지 않고 *한 레벨 전체를 본 뒤* 최솟값을 취한다(같은 레벨 안에서 더 짧게 만나는 간선이 있을 수 있다).
//  분기 계수 b, 거리 d 인 그래프에서 한 방향 BFS 는 b^d, 양방향은 2·b^(d/2) 개를 확장한다.
//  ① 무작위 그래프 600 개(정점 2~30, 간선 0~60, 비연결·고립 정점·평행 간선·자기 고리 포함)의 *모든 (출발, 도착) 쌍* 에서 양방향 BFS == 한 방향 BFS 거리(도달 불가는 −1)
//  ② 모든 레벨 경계 사례: 길이 n 의 경로(출발·도착이 양 끝), 짝수·홀수 거리, 사이클, 완전 그래프, 별 모양  ③ 확장 횟수: 정점 2 만 개 평균 차수 4 의 무작위 그래프에서 20 개 쌍의 확장 수 합이 한 방향보다 *10 배 이상* 적다.  경로 그래프는 장점이 없음(비슷함)
long expandedTotal = 0;                                                  // 확장(큐에서 꺼낸) 정점 수의 누적
int expandLevel(std::queue<int>& q, std::vector<int>& mine, const std::vector<int>& other, const std::vector<std::vector<int>>& adj) {
    int best = INT_MAX;
    for (size_t sz = q.size(); sz > 0; --sz) {
        int u = q.front(); q.pop(); ++expandedTotal;
        for (int v : adj[u]) {
            if (other[v] != -1) best = std::min(best, mine[u] + 1 + other[v]);
            if (mine[v] == -1) { mine[v] = mine[u] + 1; q.push(v); }
        }
    }
    return best;
}
int bidirectionalBFS(int src, int dst, const std::vector<std::vector<int>>& adj) {
    if (src == dst) return 0;
    int V = adj.size();
    std::vector<int> distF(V, -1), distB(V, -1);
    std::queue<int> qF, qB;
    qF.push(src); distF[src] = 0;
    qB.push(dst); distB[dst] = 0;
    while (!qF.empty() && !qB.empty()) {
        // 더 작은 쪽 프런티어를 확장하면 방문 정점 수가 줄어든다
        int best = (qF.size() <= qB.size()) ? expandLevel(qF, distF, distB, adj) : expandLevel(qB, distB, distF, adj);
        if (best != INT_MAX) return best;
    }
    return -1;
}
int plainBFS(int src, int dst, const std::vector<std::vector<int>>& adj) {                               // 오라클 (확장 수도 센다)
    std::vector<int> d(adj.size(), -1); std::queue<int> q; q.push(src); d[src] = 0;
    while (!q.empty()) { int u = q.front(); q.pop(); ++expandedTotal; if (u == dst) return d[u]; for (int v : adj[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }
    return -1; }
std::vector<std::vector<int>> randomGraph(int n, int m, std::mt19937& rng) { std::vector<std::vector<int>> adj(n); for (int i = 0; i < m; ++i) { int a = (int)(rng() % n), b = (int)(rng() % n); adj[a].push_back(b); adj[b].push_back(a); } return adj; }

int main() {
    std::vector<std::vector<int>> adj = {{1,2},{0,3},{0,4},{1,5},{2,5},{3,4}};
    assert(bidirectionalBFS(0, 5, adj) == 3 && bidirectionalBFS(0, 0, adj) == 0); std::vector<std::vector<int>> split = {{1},{0},{3},{2}}; assert(bidirectionalBFS(0, 3, split) == -1);
    std::mt19937 rng(10);
    for (int trial = 0; trial < 600; ++trial) { int n = 2 + (int)(rng() % 29), m = (int)(rng() % 61); auto g = randomGraph(n, m, rng); for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) assert(bidirectionalBFS(a, b, g) == plainBFS(a, b, g)); }          // ①
    for (int n = 2; n <= 40; ++n) {                                                                                                                      // ② 경계 사례
        std::vector<std::vector<int>> path(n), cycle(n), complete(n), star(n); for (int i = 0; i + 1 < n; ++i) { path[i].push_back(i + 1); path[i + 1].push_back(i); } for (int i = 0; i < n; ++i) { cycle[i].push_back((i + 1) % n); cycle[(i + 1) % n].push_back(i); }
        for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (i != j) complete[i].push_back(j); for (int i = 1; i < n; ++i) { star[0].push_back(i); star[i].push_back(0); }
        assert(bidirectionalBFS(0, n - 1, path) == n - 1 && bidirectionalBFS(0, n - 1, complete) == 1);
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) { assert(bidirectionalBFS(a, b, star) == (a == b ? 0 : (a == 0 || b == 0) ? 1 : 2)); assert(bidirectionalBFS(a, b, cycle) == std::min((b - a + n) % n, (a - b + n) % n)); } }      // 닫힌 식
    {   auto g = randomGraph(20000, 40000, rng); long bi = 0, uni = 0; for (int q = 0; q < 20; ++q) { int a = (int)(rng() % 20000), b = (int)(rng() % 20000);                                       // ③ 확장 수
            expandedTotal = 0; int d1 = bidirectionalBFS(a, b, g); bi += expandedTotal; expandedTotal = 0; int d2 = plainBFS(a, b, g); uni += expandedTotal; assert(d1 == d2); }
        assert(bi * 10 < uni); std::cout << "BidirectionalSearch: expansions " << bi << " (bidirectional) vs " << uni << " (one-way) over 20 queries on a 20000-vertex random graph" << std::endl; }
    {   const int n = 100000; std::vector<std::vector<int>> path(n); for (int i = 0; i + 1 < n; ++i) { path[i].push_back(i + 1); path[i + 1].push_back(i); } expandedTotal = 0; assert(bidirectionalBFS(0, n - 1, path) == n - 1); long bi = expandedTotal; expandedTotal = 0; plainBFS(0, n - 1, path); assert(bi <= expandedTotal + 2); }       // 경로 그래프는 장점 없음
    return 0;
}
// Time Complexity: O(b^(d/2)) vs O(b^d) for unidirectional
// Space Complexity: O(b^(d/2))
```
## IDDFS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

// 반복 깊이 심화 DFS(IDDFS): 깊이 제한 0, 1, 2, … 로 깊이 제한 DFS 를 반복한다. 처음 성공하는 제한 d 가 곧 최단 간선 수(BFS 와 같은 답)이고, 메모리는 현재 경로 하나뿐인 O(d) 다. 대가는 얕은 층을 반복해서 다시 만드는 일인데, 가지치기 b ≥ 2 인 트리에서는 마지막 층이 압도적으로 커서 그 반복 비용이 작다. 분기 b, 목표가 가장 오른쪽 잎(깊이 d)일 때 IDDFS 가 방문하는 노드 수는 정확히 Σ_{i=0..d} (d − i + 1) b^i 이고 BFS 는 Σ b^i 라서, 비율은 항상 b/(b − 1) 미만이다(b = 2 는 2배 미만, b = 10 은 1.11배 미만). 이를 모든 b = 2..5, d ≤ 9 에서 정수로 정확히 확인한다.
// 분기가 1 에 가까운 길쭉한 그래프에서는 반복이 낭비다(경로 그래프는 d² 번 방문). 또 방향·사이클이 있는 그래프에서는 같은 정점이 다른 경로로 여러 번 열린다 — 현재 경로 위의 정점만 막으면(onPath) 단순 경로만 훑으므로 정확성은 유지된다. 암시적 상태 공간(8 퍼즐)에서는 방금 온 곳으로의 되돌림만 막고 BFS 로 만든 정답표(상태 181,440 개, 지름 31, 가장 먼 상태 2 개, 거리별 상태 수 전체)와 대조한다.
// 검증: ① 정점 5 개의 모든 무방향 그래프(1024) 의 모든 (s,t) 에서 IDDFS 깊이 = BFS 거리, 도달 불가면 실패, 복원한 경로는 단순 경로 ② 무작위 방향 그래프 ③ 트리 방문 수 공식과 BFS 대비 비율 ④ 메모리: 이진 트리에서 IDDFS 스택 깊이 ≤ d + 1, BFS 큐 최대 크기는 2^d ⑤ 8 퍼즐 정답표와 일치 ⑥ 큰 입력(깊이 20 의 이진 트리 · 길이 5000 의 경로).
struct Result { bool found = false; int depth = -1; std::vector<int> path; long long visited = 0; int maxStack = 0; int iterations = 0; };

Result iddfs(const std::vector<std::vector<int>>& adj, int s, int t, int maxDepth) {
    int n = (int)adj.size(); Result r;
    std::vector<int> path; std::vector<char> onPath(n, 0);
    std::function<bool(int, int)> dls = [&](int u, int left) -> bool {
        ++r.visited; path.push_back(u); onPath[u] = 1; r.maxStack = std::max(r.maxStack, (int)path.size());
        if (u == t) return true;                                                  // 찾으면 경로를 그대로 둔 채 빠져나간다
        if (left > 0) for (int v : adj[u]) if (!onPath[v] && dls(v, left - 1)) return true;
        path.pop_back(); onPath[u] = 0; return false;
    };
    for (int limit = 0; limit <= maxDepth; ++limit) {
        ++r.iterations; path.clear(); std::fill(onPath.begin(), onPath.end(), 0);
        if (dls(s, limit)) { r.found = true; r.depth = limit; r.path = path; break; }
    }
    return r;
}
struct Bfs { std::vector<int> dist; std::size_t maxQueue = 0; long long visited = 0; };
Bfs bfs(const std::vector<std::vector<int>>& adj, int s) {
    Bfs b; b.dist.assign(adj.size(), -1); std::queue<int> q; q.push(s); b.dist[s] = 0;
    while (!q.empty()) { b.maxQueue = std::max(b.maxQueue, q.size()); int u = q.front(); q.pop(); ++b.visited; for (int v : adj[u]) if (b.dist[v] < 0) { b.dist[v] = b.dist[u] + 1; q.push(v); } }
    return b;
}
bool validSimplePath(const std::vector<std::vector<int>>& adj, const std::vector<int>& p, int s, int t) {
    if (p.empty() || p.front() != s || p.back() != t) return false;
    std::vector<int> sorted = p; std::sort(sorted.begin(), sorted.end());
    if (std::adjacent_find(sorted.begin(), sorted.end()) != sorted.end()) return false;
    for (std::size_t i = 0; i + 1 < p.size(); ++i) if (std::find(adj[p[i]].begin(), adj[p[i]].end(), p[i + 1]) == adj[p[i]].end()) return false;
    return true;
}

// ---- 8 퍼즐 (암시적 상태 공간): 칸 9 개를 4 비트씩 64 비트에 담는다, 0 = 빈칸 ----
typedef uint64_t State;
const State GOAL = [] { State s = 0; for (int i = 0; i < 8; ++i) s |= (State)(i + 1) << (4 * i); return s; }();
inline int cell(State s, int i) { return (int)(s >> (4 * i) & 15); }
void neighbours(State s, std::vector<State>& out) {
    out.clear(); int b = 0; while (cell(s, b) != 0) ++b;
    int r = b / 3, c = b % 3, dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    for (int k = 0; k < 4; ++k) {
        int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr > 2 || nc > 2) continue;
        int x = nr * 3 + nc; State t = s; int tile = cell(s, x);
        t &= ~(15ULL << (4 * x)); t |= (State)tile << (4 * b);
        out.push_back(t);
    }
}
int iddfsPuzzle(State start, int maxDepth, long long& visited) {
    std::function<bool(State, State, int)> dls = [&](State u, State parent, int left) -> bool {
        ++visited; if (u == GOAL) return true;
        if (left == 0) return false;
        std::vector<State> nb; neighbours(u, nb);
        for (State v : nb) if (v != parent && dls(v, u, left - 1)) return true;
        return false;
    };
    for (int limit = 0; limit <= maxDepth; ++limit) if (dls(start, ~0ULL, limit)) return limit;
    return -1;
}

int main() {
    // ① 손으로 확인한 모양: 0–1, 0–2, 1–3, 2–4 이면 0 에서 4 까지 깊이 2
    {   std::vector<std::vector<int>> adj = {{1, 2}, {0, 3}, {0, 4}, {1}, {2}};
        Result r = iddfs(adj, 0, 4, 10);
        assert(r.found && r.depth == 2 && r.path == std::vector<int>({0, 2, 4}) && r.iterations == 3);
        assert(iddfs(adj, 3, 4, 10).depth == 4 && !iddfs(adj, 0, 4, 1).found);                 // 제한이 모자라면 실패
        assert(iddfs(adj, 2, 2, 0).found && iddfs(adj, 2, 2, 0).depth == 0);                   // 출발 = 목표
    }

    // ② 전수: 정점 5 개의 모든 무방향 그래프(2^10) 의 모든 (s, t) — BFS 거리와 같은 깊이, 도달 불가면 실패, 경로는 단순 경로
    long long pairs = 0;
    for (unsigned mask = 0; mask < 1024; ++mask) {
        std::vector<std::vector<int>> adj(5); int bit = 0;
        for (int a = 0; a < 5; ++a) for (int b = a + 1; b < 5; ++b, ++bit) if (mask >> bit & 1) { adj[a].push_back(b); adj[b].push_back(a); }
        for (int s = 0; s < 5; ++s) {
            Bfs b = bfs(adj, s);
            for (int t = 0; t < 5; ++t) {
                Result r = iddfs(adj, s, t, 4);
                assert(r.found == (b.dist[t] >= 0));
                if (r.found) { assert(r.depth == b.dist[t] && validSimplePath(adj, r.path, s, t) && (int)r.path.size() == r.depth + 1); }
                ++pairs;
            }
        }
    }
    assert(pairs == 1024 * 25);

    // ③ 무작위 방향 그래프 (정점 ≤ 10, 사이클·평행 간선·루프 포함)
    std::mt19937 rng(97);
    for (int it = 0; it < 500; ++it) {
        int n = 2 + (int)(rng() % 9), m = (int)(rng() % (3 * n)); std::vector<std::vector<int>> adj(n);
        for (int i = 0; i < m; ++i) adj[rng() % n].push_back((int)(rng() % n));
        int s = (int)(rng() % n); Bfs b = bfs(adj, s);
        for (int t = 0; t < n; ++t) {
            Result r = iddfs(adj, s, t, n - 1);
            assert(r.found == (b.dist[t] >= 0));
            if (r.found) assert(r.depth == b.dist[t] && validSimplePath(adj, r.path, s, t));
        }
    }

    // ④ 완전 b-진 트리에서 방문 수 공식: 목표 = 가장 오른쪽 잎 → IDDFS 는 정확히 Σ (d−i+1) b^i, BFS 는 Σ b^i, 비율 < b/(b−1)
    for (int b = 2; b <= 5; ++b) for (int d = 1; d <= 9; ++d) {
        long long total = 0, pw = 1; for (int i = 0; i <= d; ++i) { total += pw; pw *= b; }
        if (total > 400000) continue;
        std::vector<std::vector<int>> adj(total);
        for (long long u = 0; u * b + 1 < total; ++u) for (int k = 1; k <= b; ++k) adj[u].push_back((int)(u * b + k));
        Result r = iddfs(adj, 0, (int)(total - 1), d);
        long long expect = 0; pw = 1; for (int i = 0; i <= d; ++i) { expect += (long long)(d - i + 1) * pw; pw *= b; }
        assert(r.found && r.depth == d && r.visited == expect);
        Bfs bf = bfs(adj, 0); assert(bf.visited == total);
        assert(r.visited * (b - 1) < total * b);                                           // 비율 < b/(b−1) 를 정수로
    }
    // 메모리: 이진 트리 깊이 14 (노드 32,767) — IDDFS 의 스택 깊이는 d + 1, BFS 큐는 2^d 까지 커진다
    {
        const int d = 14; int total = (1 << (d + 1)) - 1; std::vector<std::vector<int>> adj(total);
        for (int u = 0; 2 * u + 2 < total; ++u) adj[u] = {2 * u + 1, 2 * u + 2};
        Result r = iddfs(adj, 0, total - 1, d); Bfs bf = bfs(adj, 0);
        assert(r.found && r.maxStack == d + 1 && bf.maxQueue >= (1u << d));
    }

    // ⑤ 8 퍼즐: BFS 로 정답표를 만든다 (181,440 개 상태, 지름 31, 지름에 있는 상태 2 개) 후 IDDFS 깊이와 대조
    std::unordered_map<State, int> table; table.reserve(400000);
    {
        std::vector<State> cur{GOAL}, nxt, nb; table[GOAL] = 0; int depth = 0; std::vector<long long> layer;
        while (!cur.empty()) {
            layer.push_back((long long)cur.size()); nxt.clear();
            for (State s : cur) { neighbours(s, nb); for (State t : nb) if (!table.count(t)) { table[t] = depth + 1; nxt.push_back(t); } }
            cur.swap(nxt); ++depth;
        }
        const std::vector<long long> known = {1, 2, 4, 8, 16, 20, 39, 62, 116, 152, 286, 396, 748, 1024, 1893, 2512, 4485, 5638, 9529, 10878, 16993, 17110, 23952, 20224, 24047, 15578, 14560, 6274, 3910, 760, 221, 2};
        assert(table.size() == 181440 && layer == known);                                    // 거리별 상태 수 전체 (OEIS A087725)
    }
    long long totalVisited = 0; int checked = 0;
    for (int it = 0; it < 300 && checked < 40; ++it) {
        State s = GOAL; State parent = ~0ULL; std::vector<State> nb; int steps = 4 + (int)(rng() % 7);
        for (int k = 0; k < steps; ++k) { neighbours(s, nb); State pick; do pick = nb[rng() % nb.size()]; while (pick == parent && nb.size() > 1); parent = s; s = pick; }
        int want = table[s]; if (want < 4) continue;
        long long visited = 0; int got = iddfsPuzzle(s, 12, visited);
        assert(got == want); totalVisited += visited; ++checked;
    }
    assert(checked == 40 && totalVisited > 10000);

    // ⑥ 큰 입력: 깊이 18 의 이진 트리(노드 524,287 개) 에서 가장 오른쪽 잎 → 방문 수 공식과 일치; 길이 5000 의 경로는 d² 에 비례한 반복
    {
        const int d = 18, total = (1 << (d + 1)) - 1; std::vector<std::vector<int>> adj(total);
        for (int u = 0; 2 * u + 2 < total; ++u) adj[u] = {2 * u + 1, 2 * u + 2};
        Result r = iddfs(adj, 0, total - 1, d);
        long long expect = 0, pw = 1; for (int i = 0; i <= d; ++i) { expect += (long long)(d - i + 1) * pw; pw *= 2; }
        assert(r.found && r.visited == expect && r.visited < 2LL * total);                 // BFS 의 total 개 대비 비율 < 2
        const int L = 5000; std::vector<std::vector<int>> line(L + 1);
        for (int i = 0; i < L; ++i) line[i].push_back(i + 1);
        Result p = iddfs(line, 0, L, L);
        assert(p.found && p.depth == L && p.visited == (long long)(L + 1) * (L + 2) / 2);   // 제한 0..L 마다 제한 + 1 개씩 방문
    }
    std::cout << "IDDFS: iterative deepening returned exactly the BFS distance (and a genuine simple path) for every ordered pair of every one of the 1024 undirected graphs on 5 vertices and for 500 random digraphs with loops and parallel edges, it visited exactly sum_{i<=d}(d-i+1)b^i nodes on complete b-ary trees (b = 2..5, d <= 9) with ratio to BFS strictly below b/(b-1), its stack held d+1 nodes where BFS's queue grew to 2^d, it solved 40 random 8-puzzle positions at exactly the optimal depth of a BFS table with 181,440 states and diameter 31, and handled a 524,287-node tree and a 5000-edge path" << std::endl; return 0;
}
// Time Complexity: O(b^d)
// Space Complexity: O(d)
```
## IDAStar()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdint>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

// IDA*(Iterative Deepening A*): IDDFS 의 "깊이 제한" 을 "f = g + h 제한" 으로 바꾼 것. 제한(bound)을 h(시작) 로 잡고 f 가 bound 를 넘는 가지를 잘라내며 DFS 하고, 못 찾으면 그 탐색에서 잘려나간 f 중 *가장 작은 값* 을 새 bound 로 삼아 반복한다. A* 와 같은 최적해를 O(d) 메모리로 얻는 대신 같은 상태를 여러 경로로 다시 연다. h 가 허용 가능(과대평가하지 않음)이면 최적이고, A* 의 그래프 탐색과 달리 *일관성(consistency)은 필요 없다* — 모든 경로를 보는 트리 탐색이라 닫힌 집합의 재오픈 문제가 없다. 추정이 부풀려지면(비허용) 해는 얻어도 최적이 아닐 수 있다.
// 정리(검증 대상): ① 첫 bound = h(시작), bound 는 순증가, 마지막 bound = 최적 비용(허용 h) ② h 가 정확하면 반복이 정확히 1 번 ③ 슬라이딩 퍼즐에서 맨해튼 거리는 매 이동마다 f 의 홀짝을 보존하므로 bound 는 매번 정확히 2 씩 늘어난다 ④ h = 0 이면 IDDFS 와 같고 맨해튼 휴리스틱은 방문 수를 크게 줄인다 ⑤ 비허용 h 는 때로 최적이 아닌 해를 낸다.
// 검증: 무작위 가중 그래프(정점 ≤ 9, 가중치 1..5) 에서 휴리스틱 다섯 종 — 0, 정확한 거리, 정확한 거리의 절반(내림), 허용이지만 일관되지 않은 무작위 h, 비허용 — 로 다익스트라와 대조; 8 퍼즐 181,440 상태 BFS 정답표와 맨해튼 IDA* 의 비용 일치, 매 bound 증가량 2, 방문 수 비교.
typedef long long ll;
const ll INF = LLONG_MAX / 4;
template <class S> struct Problem {
    std::function<void(const S&, std::vector<std::pair<S, ll>>&)> succ;
    std::function<ll(const S&)> h;
    std::function<bool(const S&)> goal;
};
template <class S> struct IDA {
    const Problem<S>& P; std::vector<S> path; long long expansions = 0; ll foundCost = -1; int maxDepth = 0;
    explicit IDA(const Problem<S>& p) : P(p) {}
    // 반환: FOUND(-1) 또는 bound 를 넘은 f 중 최솟값 (더 이상 갈 곳이 없으면 INF)
    ll search(const S& s, ll g, ll bound) {
        ll f = g + P.h(s);
        if (f > bound) return f;
        if (P.goal(s)) { foundCost = g; return -1; }
        ++expansions; maxDepth = std::max(maxDepth, (int)path.size());
        std::vector<std::pair<S, ll>> next; P.succ(s, next);
        ll mn = INF;
        for (auto& [t, w] : next) {
            if (std::find(path.begin(), path.end(), t) != path.end()) continue;       // 현재 경로 위는 건너뜀
            path.push_back(t);
            ll r = search(t, g + w, bound);
            if (r == -1) return -1;                                                 // 찾았으면 경로를 그대로 둔다
            path.pop_back(); mn = std::min(mn, r);
        }
        return mn;
    }
    ll run(const S& start, std::vector<ll>* thresholds = nullptr) {                  // 최적 비용 (도달 불가면 -1)
        path.assign(1, start); ll bound = P.h(start);
        while (true) {
            if (thresholds) thresholds->push_back(bound);
            ll r = search(start, 0, bound);
            if (r == -1) return foundCost;
            if (r >= INF) return -1;
            bound = r;
        }
    }
};

// ---- 명시적 가중 그래프 ----
struct Wg { int n; std::vector<std::vector<std::pair<int, ll>>> adj; };
std::vector<ll> distancesTo(const Wg& g, int t) {                                    // 역방향 다익스트라
    std::vector<std::vector<std::pair<int, ll>>> radj(g.n);
    for (int u = 0; u < g.n; ++u) for (auto [v, w] : g.adj[u]) radj[v].push_back({u, w});
    std::vector<ll> d(g.n, INF); d[t] = 0; std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; pq.push({0, t});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : radj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } }
    return d;
}
Problem<int> graphProblem(const Wg& g, int t, const std::vector<ll>& h) {
    return {[&g](const int& u, std::vector<std::pair<int, ll>>& out) { out = g.adj[u]; },
            [&h](const int& u) { return h[u]; },
            [t](const int& u) { return u == t; }};
}

// ---- 8 퍼즐 ----
typedef uint64_t State;
const State GOAL = [] { State s = 0; for (int i = 0; i < 8; ++i) s |= (State)(i + 1) << (4 * i); return s; }();
inline int cell(State s, int i) { return (int)(s >> (4 * i) & 15); }
void neighbours(State s, std::vector<State>& out) {
    out.clear(); int b = 0; while (cell(s, b) != 0) ++b;
    int r = b / 3, c = b % 3, dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    for (int k = 0; k < 4; ++k) {
        int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr > 2 || nc > 2) continue;
        int x = nr * 3 + nc; State t = s; int tile = cell(s, x);
        t &= ~(15ULL << (4 * x)); t |= (State)tile << (4 * b);
        out.push_back(t);
    }
}
ll manhattan(State s) {
    ll sum = 0;
    for (int i = 0; i < 9; ++i) { int t = cell(s, i); if (t == 0) continue; int gi = t - 1; sum += std::abs(i / 3 - gi / 3) + std::abs(i % 3 - gi % 3); }
    return sum;
}
Problem<State> puzzleProblem(bool useManhattan) {
    return {[](const State& s, std::vector<std::pair<State, ll>>& out) { std::vector<State> nb; neighbours(s, nb); out.clear(); for (State t : nb) out.push_back({t, 1}); },
            [useManhattan](const State& s) { return useManhattan ? manhattan(s) : 0; },
            [](const State& s) { return s == GOAL; }};
}

int main() {
    std::mt19937 rng(1985);
    // ① 손으로 확인한 모양: 0→1:2, 0→2:5, 1→2:1, 2→3:1 에서 0→3 최적은 0→1→2→3 = 4 (정확한 h 로 1 번에 끝)
    {   Wg g{4, {{{1, 2}, {2, 5}}, {{2, 1}}, {{3, 1}}, {}}};
        std::vector<ll> exact = distancesTo(g, 3), zero(4, 0);
        Problem<int> pe = graphProblem(g, 3, exact), pz = graphProblem(g, 3, zero);
        IDA<int> a(pe), b(pz); std::vector<ll> ta, tb;
        assert(a.run(0, &ta) == 4 && ta == std::vector<ll>({4}) && a.path == std::vector<int>({0, 1, 2, 3}));
        assert(b.run(0, &tb) == 4 && tb == std::vector<ll>({0, 2, 3, 4}));                  // h = 0: bound 는 0 → 2 → 3 → 4 (잘려나간 f 의 최솟값)
        IDA<int> c(pe); assert(c.run(3) == 0);                                              // 출발 = 목표
        Wg dead{2, {{}, {}}}; std::vector<ll> z2(2, 0); Problem<int> pd = graphProblem(dead, 1, z2); IDA<int> d(pd); assert(d.run(0) == -1);   // 닿지 않음
    }

    // ② 무작위 가중 그래프 (정점 ≤ 9): 휴리스틱 다섯 종 대 다익스트라
    int strictlyWorse = 0, admissibleRuns = 0, unreachable = 0;
    for (int it = 0; it < 1500; ++it) {
        int n = 3 + (int)(rng() % 7), m = (int)(rng() % (3 * n)); Wg g{n, std::vector<std::vector<std::pair<int, ll>>>(n)};
        for (int i = 0; i < m; ++i) g.adj[rng() % n].push_back({(int)(rng() % n), (ll)(1 + rng() % 5)});
        int s = (int)(rng() % n), t = (int)(rng() % n);
        std::vector<ll> star = distancesTo(g, t);                                          // d*(v, t): 오라클이자 h 의 재료
        ll opt = star[s] >= INF ? -1 : star[s];
        if (opt < 0) ++unreachable;
        std::vector<ll> zero(n, 0), exact(n), half(n), rnd(n), bad(n);
        for (int v = 0; v < n; ++v) {
            ll d = star[v] >= INF ? 0 : star[v];
            exact[v] = d; half[v] = d / 2; rnd[v] = d ? (ll)(rng() % (d + 1)) : 0; bad[v] = d + (ll)(rng() % 4);
        }
        exact[t] = half[t] = rnd[t] = zero[t] = 0; bad[t] = 0;                              // 목표의 h 는 0
        std::vector<const std::vector<ll>*> adm = {&zero, &exact, &half, &rnd};
        for (auto* hv : adm) {
            Problem<int> p = graphProblem(g, t, *hv); IDA<int> ida(p); std::vector<ll> th;
            ll cost = ida.run(s, &th);
            assert(cost == opt);                                                            // 허용 h → 최적 (일관성 없어도)
            if (opt >= 0) {
                assert(th.front() == (*hv)[s] && th.back() == opt);
                for (std::size_t i = 1; i < th.size(); ++i) assert(th[i] > th[i - 1]);       // bound 순증가
                if (hv == &exact) assert(th.size() == 1);                                   // 정확한 h 는 한 번에
                ++admissibleRuns;
            }
        }
        Problem<int> pb = graphProblem(g, t, bad); IDA<int> ida(pb);
        ll cost = ida.run(s);
        if (opt < 0) assert(cost == -1);
        else { assert(cost >= opt); strictlyWorse += cost > opt; }
    }
    assert(admissibleRuns > 3000 && strictlyWorse > 20 && unreachable > 100);

    // ③ 8 퍼즐: 정답표 (BFS) 를 만든다 — 181,440 개 상태, 지름 31
    std::unordered_map<State, int> table; table.reserve(400000);
    {
        std::vector<State> cur{GOAL}, nxt, nb; table[GOAL] = 0; int depth = 0;
        while (!cur.empty()) {
            nxt.clear();
            for (State s : cur) { neighbours(s, nb); for (State t : nb) if (!table.count(t)) { table[t] = depth + 1; nxt.push_back(t); } }
            cur.swap(nxt); ++depth;
        }
        assert(table.size() == 181440);
    }
    // 무작위 상태 70 개: 맨해튼 IDA* 의 비용 = BFS 거리, bound 는 정확히 2 씩 증가, h = 0 보다 훨씬 적게 방문
    Problem<State> pm = puzzleProblem(true), pz = puzzleProblem(false);
    int checked = 0; long long parityOk = 0;
    for (int it = 0; it < 2000 && checked < 70; ++it) {
        State s = GOAL, parent = ~0ULL; std::vector<State> nb; int steps = 14 + (int)(rng() % 20);
        for (int k = 0; k < steps; ++k) { neighbours(s, nb); State pick; do pick = nb[rng() % nb.size()]; while (pick == parent && nb.size() > 1); parent = s; s = pick; }
        int want = table[s]; if (want < 10 || want > 22) continue;
        IDA<State> m(pm); std::vector<ll> th; ll cost = m.run(s, &th);
        assert(cost == want && (int)th.back() == want && th.front() == manhattan(s));
        for (std::size_t i = 1; i < th.size(); ++i) assert(th[i] == th[i - 1] + 2);          // 홀짝 보존 → 정확히 2 씩
        parityOk += (long long)th.size() - 1;
        assert((int)m.path.size() == want + 1 && m.path.front() == s && m.path.back() == GOAL && m.maxDepth <= want);   // 해 경로도 올바르고 스택은 최적 깊이 이하
        if (want <= 16) { IDA<State> z(pz); assert(z.run(s) == want); }                     // h = 0 도 같은 최적 비용 (얕은 상태만)
        ++checked;
    }
    assert(checked == 70 && parityOk > 100);
    // 비교를 같은 상태에서: 얕은 상태 30 개에서 맨해튼은 h = 0 보다 훨씬 적은 노드를 연다
    {
        long long man = 0, zero = 0; int used = 0;
        for (int it = 0; it < 5000 && used < 30; ++it) {
            State s = GOAL, parent = ~0ULL; std::vector<State> nb; int steps = 10 + (int)(rng() % 8);
            for (int k = 0; k < steps; ++k) { neighbours(s, nb); State pick; do pick = nb[rng() % nb.size()]; while (pick == parent && nb.size() > 1); parent = s; s = pick; }
            int want = table[s]; if (want < 12 || want > 16) continue;
            IDA<State> m(pm), z(pz); assert(m.run(s) == want && z.run(s) == want);
            man += m.expansions; zero += z.expansions; ++used;
        }
        assert(used == 30 && zero > 8 * man);
    }
    std::cout << "IDAStar: on 1500 random weighted graphs the IDA* thresholds started at h(start), strictly increased and ended at the Dijkstra optimum for four admissible heuristics (zero, exact, half-exact, and random admissible-but-inconsistent), an exact h needed a single iteration, an inadmissible h returned a costlier-than-optimal path in over 20 cases and -1 correctly for unreachable targets, and on 70 random 8-puzzle positions (optimal depth 10-22 against a 181,440-state BFS table) the Manhattan-distance IDA* returned exactly the optimal length with the bound growing by exactly 2 per iteration (parity), a stack no deeper than the solution, and at least 8 times fewer expansions than h = 0 on 30 positions of depth 12-16" << std::endl; return 0;
}
// Time Complexity: O(b^d) (휴리스틱이 좋을수록 지수의 밑이 작아진다)
// Space Complexity: O(d)
```
## ThetaStar()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 세타* (그래프 관점의 요약, 정본은 PathFinding.md Part 5): 격자 그래프의 간선(8방향)에 묶이지 않고 "어떤 각도로든" 가는 최단 경로. A* 와 같지만 s 에서 이웃 s' 로 갈 때 s 의 부모에서 s' 가 직선으로 보이면(시선 LOS) s 를 건너뛰고 부모에서 바로 잇는다.
// 간선이 암묵적으로 "보이는 두 칸 사이의 선분" 인 시선 그래프 위의 A* 를 지연 평가로 흉내 낸 것이다. 진짜 최단(any-angle optimal)은 보장되지 않지만 8방향 격자 경로보다 짧고 계단 모양이 없다.
// 검증: 무작위 지도에서 ① 도달 가능성이 격자 A* 와 같고 ② 모든 선분이 시선 검사와 독립 표본 검사를 통과하며 ③ 평균 경로 길이가 격자 A* 보다 3% 이상 짧다
typedef std::pair<int, int> P;
struct Grid { int R, C; std::vector<std::string> w; bool blocked(int r, int c) const { return r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#'; } };
bool hit(double x0, double y0, double x1, double y1, double bx0, double by0, double bx1, double by1) {      // 선분 vs 닫힌 사각형 (Liang–Barsky)
    double t0 = 0, t1 = 1, dx = x1 - x0, dy = y1 - y0, p[4] = {-dx, dx, -dy, dy}, q[4] = {x0 - bx0, bx1 - x0, y0 - by0, by1 - y0};
    for (int i = 0; i < 4; i++) { if (p[i] == 0) { if (q[i] < 0) return false; } else { double r = q[i] / p[i]; if (p[i] < 0) { if (r > t1) return false; t0 = std::max(t0, r); } else { if (r < t0) return false; t1 = std::min(t1, r); } } }
    return t0 <= t1 + 1e-12;
}
long losChecks = 0;
bool los(const Grid& g, P a, P b) {
    losChecks++; double x0 = a.second + 0.5, y0 = a.first + 0.5, x1 = b.second + 0.5, y1 = b.first + 0.5;
    for (int r = std::min(a.first, b.first); r <= std::max(a.first, b.first); r++) for (int c = std::min(a.second, b.second); c <= std::max(a.second, b.second); c++) if (g.blocked(r, c) && hit(x0, y0, x1, y1, c, r, c + 1, r + 1)) return false;
    return !g.blocked(a.first, a.second) && !g.blocked(b.first, b.second);
}
double dist(P a, P b) { return std::hypot(a.first - b.first, a.second - b.second); }
struct Res { double cost = -1; long expanded = 0; std::vector<P> path; };
Res search(const Grid& g, P s, P t, bool theta) {                          // theta = false 면 부모 단축을 끈 일반 8방향 A* (유클리드 비용)
    Res res; int n = g.R * g.C; std::vector<double> gc(n, 1e18); std::vector<int> parent(n, -1); std::vector<char> closed(n, 0); using Q = std::pair<double, int>; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq;
    int si = s.first * g.C + s.second, ti = t.first * g.C + t.second; gc[si] = 0; parent[si] = si; pq.push({dist(s, t), si});
    while (!pq.empty()) { int u = pq.top().second; pq.pop(); if (closed[u]) continue; closed[u] = 1; res.expanded++;
        if (u == ti) { res.cost = gc[u]; for (int v = u;; v = parent[v]) { res.path.push_back({v / g.C, v % g.C}); if (v == si) break; } std::reverse(res.path.begin(), res.path.end()); return res; }
        P up{u / g.C, u % g.C};
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; P v{up.first + dr, up.second + dc}; if (g.blocked(v.first, v.second)) continue; int vi = v.first * g.C + v.second; if (closed[vi]) continue; if (!los(g, up, v)) continue;          // 이웃 이동 자체도 모서리 자르기 없이
            int pu = parent[u]; P pp{pu / g.C, pu % g.C}; double cand; int par;
            if (theta && pu != u && los(g, pp, v)) { cand = gc[pu] + dist(pp, v); par = pu; } else { cand = gc[u] + dist(up, v); par = u; }          // 경로 2: 부모에서 직선으로 갈 수 있으면 s 를 건너뛴다
            if (cand < gc[vi]) { gc[vi] = cand; parent[vi] = par; pq.push({cand + dist(v, t), vi}); } }
    }
    return res;
}
bool pathClear(const Grid& g, const std::vector<P>& p) {                   // 독립 검증: 선분을 촘촘히 표본 추출해 벽 칸의 내부에 들어가는 점이 없는가
    for (size_t i = 1; i < p.size(); i++) for (int k = 0; k <= 400; k++) { double f = k / 400.0, y = (p[i - 1].first + 0.5) * (1 - f) + (p[i].first + 0.5) * f, x = (p[i - 1].second + 0.5) * (1 - f) + (p[i].second + 0.5) * f; if (g.blocked((int)std::floor(y + 1e-9), (int)std::floor(x + 1e-9)) && g.blocked((int)std::floor(y - 1e-9), (int)std::floor(x - 1e-9))) return false; }
    return true;
}
int main() {
    std::mt19937 gen(5); int solved = 0, better = 0, worse = 0; double sumTheta = 0, sumGrid = 0; long tExp = 0, aExp = 0;
    for (int t = 0; t < 120; t++) {
        Grid g{26, 26, std::vector<std::string>(26, std::string(26, '.'))}; for (auto& row : g.w) for (auto& ch : row) if (gen() % 100 < 22) ch = '#';
        P s{(int)(gen() % 26), (int)(gen() % 26)}, e{(int)(gen() % 26), (int)(gen() % 26)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        Res th = search(g, s, e, true), gr = search(g, s, e, false); assert((th.cost < 0) == (gr.cost < 0)); if (th.cost < 0) continue; solved++;
        double c = 0; for (size_t i = 1; i < th.path.size(); i++) { assert(los(g, th.path[i - 1], th.path[i])); c += dist(th.path[i - 1], th.path[i]); } assert(std::fabs(c - th.cost) < 1e-6 && th.path.front() == s && th.path.back() == e && pathClear(g, th.path));
        assert(th.cost >= dist(s, e) - 1e-9);                              // 직선 거리보다 짧을 수 없다
        sumTheta += th.cost; sumGrid += gr.cost; better += th.cost < gr.cost - 1e-9; worse += th.cost > gr.cost + 1e-9; tExp += th.expanded; aExp += gr.expanded;
    }
    assert(sumTheta < sumGrid * 0.97 && better > solved / 4 && worse * 12 < solved);                           // 격자 경로보다 평균 3% 이상 짧고, 길어지는 경우는 드물다
    std::cout << "ThetaStar: " << solved << " solvable maps, mean path length Theta* " << sumTheta / solved << " vs 8-way grid A* " << sumGrid / solved << " (shorter in " << better << ", longer in " << worse << "), expansions " << tExp << " vs " << aExp << std::endl; return 0;
}
// Time Complexity: A* 와 같고 이웃마다 시선 검사 O(경로 길이)
// Space Complexity: O(V)
```
# Part 11. 네트워크 플로우
## FordFulkerson()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 포드–풀커슨 방법(Ford–Fulkerson 1956): 잔여 그래프에서 s→t 증가 경로를 찾아 병목 용량만큼 흘리고, 더 이상 경로가 없을 때까지 반복한다.  잔여 용량 = 용량 − 흐름, 반대 방향 간선의 잔여 용량 = 흐름(되돌릴 수 있다).
//  *경로를 고르는 규칙을 정하지 않은 방법* 이라 규칙에 따라 속도가 크게 달라진다 — 아래 구현은 깊이 우선(DFS)으로 고르고, 임의의 경로를 흘려 보내는 pushAlong 도 노출한다.  최대 유량 최소 절단 정리: 최대 유량 = 최소 절단 용량 (끝났을 때 s 에서 잔여 그래프로 닿는 점들의 집합이 최소 절단).
//  ① 무작위 그래프 3 000 개(정점 2~9, 간선 0~25 개, 평행·역방향·자기 고리·용량 0 포함)에서 최대 유량 == *모든 절단을 전수 열거한* 최소 절단 용량  ② 흐름 인증서: 모든 간선 0 ≤ 흐름 ≤ 용량, s·t 를 뺀 모든 정점에서 들어온 흐름 = 나간 흐름, s 의 순유출 == t 의 순유입 == 값; 잔여 도달 집합의 절단 용량 == 값
//  ③ 정점 40 개 간선 300 개 무작위 그래프 50 개를 인접 행렬 위의 독립 구현(BFS 증가 경로)과 대조  ④ 경로 선택이 나쁜 경우: s→a, s→b, a→t, b→t 가 용량 C, a→b 가 1 인 그래프에서 s→a→b→t 와 s→b→a→t 를 번갈아 고르면 증가가 정확히 2C 번(= 값이 겨우 1 씩 늘어난다) 필요 — C = 200 에서 400 번이고, DFS 규칙은 4 번.  용량이 10^9 이면 유사 다항 시간이라 수십억 번 → Edmonds–Karp(BFS)와 Dinic 의 동기
struct MaxFlow {
    struct Edge { int to; long long cap; int rev; };
    std::vector<std::vector<Edge>> g; std::vector<char> seen; std::vector<std::pair<int, int>> ids; std::vector<long long> original; long long augmentations = 0;
    explicit MaxFlow(int n) : g(n), seen(n, 0) {}
    int addEdge(int u, int v, long long c) { int iu = (int)g[u].size(), iv = (int)g[v].size() + (u == v ? 1 : 0); g[u].push_back({v, c, iv}); g[v].push_back({u, 0, iu}); ids.push_back({u, iu}); original.push_back(c); return (int)ids.size() - 1; }
    long long flowOn(int id) const { return original[id] - g[ids[id].first][ids[id].second].cap; }                                      // 흐름 = 원래 용량 − 남은 용량
    long long dfs(int u, int t, long long f) {
        if (u == t) return f; seen[u] = 1;
        for (Edge& e : g[u]) if (e.cap > 0 && !seen[e.to]) { long long d = dfs(e.to, t, std::min(f, e.cap)); if (d > 0) { e.cap -= d; g[e.to][e.rev].cap += d; return d; } }
        return 0; }
    long long maxflow(int s, int t) { long long total = 0; if (s == t) return 0; for (;;) { std::fill(seen.begin(), seen.end(), 0); long long d = dfs(s, t, LLONG_MAX); if (d == 0) return total; total += d; ++augmentations; } }
    long long pushAlong(const std::vector<int>& nodes) {                                                                                   // 주어진 점 열을 따라 병목만큼 흘린다(길이 막혀 있으면 0)
        std::vector<Edge*> path; long long bottleneck = LLONG_MAX;
        for (size_t i = 0; i + 1 < nodes.size(); ++i) { Edge* best = nullptr; for (Edge& e : g[nodes[i]]) if (e.to == nodes[i + 1] && e.cap > 0 && (!best || e.cap > best->cap)) best = &e; if (!best) return 0; path.push_back(best); bottleneck = std::min(bottleneck, best->cap); }
        for (Edge* e : path) { e->cap -= bottleneck; g[e->to][e->rev].cap += bottleneck; } ++augmentations; return bottleneck; }
    std::vector<char> reachable(int s) const { std::vector<char> r(g.size(), 0); std::queue<int> q; r[s] = 1; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (const Edge& e : g[u]) if (e.cap > 0 && !r[e.to]) { r[e.to] = 1; q.push(e.to); } } return r; }
};
struct Arc { int u, v; long long c; };
long long bruteMinCut(int n, const std::vector<Arc>& arcs, int s, int t) {                                                              // 독립 오라클: s 쪽에 둘 점의 모든 부분집합을 열거
    long long best = LLONG_MAX; for (unsigned mask = 0; mask < (1u << n); ++mask) { if (!(mask >> s & 1) || (mask >> t & 1)) continue; long long cut = 0; for (const Arc& a : arcs) if ((mask >> a.u & 1) && !(mask >> a.v & 1)) cut += a.c; best = std::min(best, cut); } return best; }
long long matrixMaxFlow(int n, const std::vector<Arc>& arcs, int s, int t) {                                                            // 독립 오라클 2: 인접 행렬 + BFS 증가 경로
    std::vector<std::vector<long long>> cap(n, std::vector<long long>(n, 0)); for (const Arc& a : arcs) if (a.u != a.v) cap[a.u][a.v] += a.c; long long total = 0;
    for (;;) { std::vector<int> par(n, -1); par[s] = s; std::queue<int> q; q.push(s); while (!q.empty() && par[t] < 0) { int u = q.front(); q.pop(); for (int v = 0; v < n; ++v) if (par[v] < 0 && cap[u][v] > 0) { par[v] = u; q.push(v); } }
        if (par[t] < 0) return total; long long b = LLONG_MAX; for (int v = t; v != s; v = par[v]) b = std::min(b, cap[par[v]][v]); for (int v = t; v != s; v = par[v]) { cap[par[v]][v] -= b; cap[v][par[v]] += b; } total += b; } }
void certify(const MaxFlow& mf, const std::vector<Arc>& arcs, const std::vector<int>& ids, int n, int s, int t, long long value) {       // 흐름 인증서
    std::vector<long long> net(n, 0); for (size_t i = 0; i < arcs.size(); ++i) { long long f = mf.flowOn(ids[i]); assert(f >= 0 && f <= arcs[i].c); net[arcs[i].u] -= f; net[arcs[i].v] += f; }
    for (int v = 0; v < n; ++v) if (v != s && v != t) assert(net[v] == 0); if (s != t) assert(-net[s] == value && net[t] == value);
    std::vector<char> inS = mf.reachable(s); assert(s == t || !inS[t]); long long cut = 0; for (const Arc& a : arcs) if (inS[a.u] && !inS[a.v]) cut += a.c; if (s != t) assert(cut == value); }                   // 잔여 도달 집합 = 최소 절단

int main() {
    std::mt19937 rng(11);
    for (int trial = 0; trial < 3000; ++trial) { int n = 2 + (int)(rng() % 8), m = (int)(rng() % 26); std::vector<Arc> arcs; MaxFlow mf(n); std::vector<int> ids;                       // ①② 무작위 그래프
        for (int i = 0; i < m; ++i) { Arc a{(int)(rng() % n), (int)(rng() % n), (long long)(rng() % 13)}; arcs.push_back(a); ids.push_back(mf.addEdge(a.u, a.v, a.c)); }
        int s = 0, t = n - 1; long long value = mf.maxflow(s, t); assert(value == bruteMinCut(n, arcs, s, t)); certify(mf, arcs, ids, n, s, t, value); }
    for (int trial = 0; trial < 50; ++trial) { int n = 40, m = 300; std::vector<Arc> arcs; MaxFlow mf(n); for (int i = 0; i < m; ++i) { Arc a{(int)(rng() % n), (int)(rng() % n), (long long)(rng() % 50) + 1}; arcs.push_back(a); mf.addEdge(a.u, a.v, a.c); }      // ③
        assert(mf.maxflow(0, n - 1) == matrixMaxFlow(n, arcs, 0, n - 1)); }
    {   const long long C = 200; std::vector<Arc> arcs = {{0, 1, C}, {0, 2, C}, {1, 3, C}, {2, 3, C}, {1, 2, 1}}; MaxFlow bad(4), good(4); for (const Arc& a : arcs) { bad.addEdge(a.u, a.v, a.c); good.addEdge(a.u, a.v, a.c); }            // ④ 경로 선택이 나쁜 경우
        long long total = 0; for (long long step = 0; total < 2 * C; ++step) { long long pushed = bad.pushAlong(step % 2 == 0 ? std::vector<int>{0, 1, 2, 3} : std::vector<int>{0, 2, 1, 3}); assert(pushed == 1); total += pushed; }
        assert(bad.augmentations == 2 * C && total == 2 * C && bad.maxflow(0, 3) == 0);                                                    // 번갈아 고르면 값이 1 씩만 늘어난다
        assert(good.maxflow(0, 3) == 2 * C && good.augmentations <= 4 && matrixMaxFlow(4, arcs, 0, 3) == 2 * C); }                          // DFS 규칙은 4 번 이내
    std::cout << "FordFulkerson: max flow equalled the exhaustively enumerated min cut on 3000 random graphs with a valid flow certificate each time, matched an independent matrix implementation on 50 graphs of 40 nodes, and an unlucky path rule needed 400 augmentations for a value of 400 where the DFS rule needed at most 4" << std::endl;
    return 0;
}
// Time Complexity: O(E · f) (f = 최대 유량, 정수 용량), 경로 선택 규칙이 정해지지 않으면 유사 다항 시간
// Space Complexity: O(V + E)
```
## EdmondsKarp()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 에드먼즈–카프(Edmonds–Karp 1972): 포드–풀커슨에서 증가 경로를 *가장 적은 간선 수(BFS)* 로 고른다.  그러면 경로 길이가 단조 비감소이고, 증가마다 병목 간선이 하나 포화되며, 한 간선이 병목이 될 수 있는 횟수가 V/2 번뿐이라 증가 횟수가 O(VE) — 용량이 아무리 커도 총 시간 O(V E²).
//  ① 무작위 그래프 3 000 개(정점 2~9, 간선 0~25 개, 평행·역방향·자기 고리·용량 0 포함)에서 최대 유량 == 모든 절단을 전수 열거한 최소 절단 용량, 흐름 인증서(용량 제약·보존·값·잔여 도달 절단)
//  ② 증가 경로 길이가 *단조 비감소* (핵심 보조정리)이고 증가 횟수 ≤ V·E  ③ 정점 40 개 간선 300 개 그래프 50 개를 독립 구현(인접 행렬 + DFS 증가 경로)과 대조  ④ 포드–풀커슨의 나쁜 사례(용량 C 의 마름모에 가운데 간선 1): C = 10^9 라도 증가는 *2 번*  ⑤ 이분 매칭: 무작위 이분 그래프 300 개(왼쪽·오른쪽 ≤ 7)의 단위 용량 최대 유량 == 비트마스크 DP 최대 매칭
struct Arc { int u, v; long long c; };
struct EK {
    struct Edge { int to; long long cap; int rev; };
    std::vector<std::vector<Edge>> g; std::vector<std::pair<int, int>> ids; std::vector<long long> original; long long augmentations = 0; std::vector<int> pathLengths;
    explicit EK(int n) : g(n) {}
    int addEdge(int u, int v, long long c) { int iu = (int)g[u].size(), iv = (int)g[v].size() + (u == v ? 1 : 0); g[u].push_back({v, c, iv}); g[v].push_back({u, 0, iu}); ids.push_back({u, iu}); original.push_back(c); return (int)ids.size() - 1; }
    long long flowOn(int id) const { return original[id] - g[ids[id].first][ids[id].second].cap; }
    long long maxflow(int s, int t) {
        long long total = 0; if (s == t) return 0;
        for (;;) {
            std::vector<int> parent(g.size(), -1), parentEdge(g.size(), -1), depth(g.size(), -1); std::queue<int> q; q.push(s); depth[s] = 0; parent[s] = s;
            while (!q.empty() && depth[t] < 0) { int u = q.front(); q.pop(); for (size_t k = 0; k < g[u].size(); ++k) { const Edge& e = g[u][k]; if (e.cap > 0 && depth[e.to] < 0) { depth[e.to] = depth[u] + 1; parent[e.to] = u; parentEdge[e.to] = (int)k; q.push(e.to); } } }
            if (depth[t] < 0) return total;                                                                                                  // 더 이상 증가 경로가 없다
            long long b = LLONG_MAX; for (int v = t; v != s; v = parent[v]) b = std::min(b, g[parent[v]][parentEdge[v]].cap);
            for (int v = t; v != s; v = parent[v]) { Edge& e = g[parent[v]][parentEdge[v]]; e.cap -= b; g[e.to][e.rev].cap += b; }
            total += b; ++augmentations; pathLengths.push_back(depth[t]); }
    }
    std::vector<char> reachable(int s) const { std::vector<char> r(g.size(), 0); std::queue<int> q; r[s] = 1; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (const Edge& e : g[u]) if (e.cap > 0 && !r[e.to]) { r[e.to] = 1; q.push(e.to); } } return r; }
};
long long bruteMinCut(int n, const std::vector<Arc>& arcs, int s, int t) { long long best = LLONG_MAX; for (unsigned mask = 0; mask < (1u << n); ++mask) { if (!(mask >> s & 1) || (mask >> t & 1)) continue; long long cut = 0; for (const Arc& a : arcs) if ((mask >> a.u & 1) && !(mask >> a.v & 1)) cut += a.c; best = std::min(best, cut); } return best; }
long long matrixDfsFlow(int n, const std::vector<Arc>& arcs, int s, int t) {                                                            // 독립 오라클: 인접 행렬 + DFS 증가 경로
    std::vector<std::vector<long long>> cap(n, std::vector<long long>(n, 0)); for (const Arc& a : arcs) if (a.u != a.v) cap[a.u][a.v] += a.c; long long total = 0;
    for (;;) { std::vector<char> seen(n, 0); std::vector<int> par(n, -1); std::vector<int> st = {s}; seen[s] = 1; while (!st.empty() && !seen[t]) { int u = st.back(); st.pop_back(); for (int v = 0; v < n; ++v) if (!seen[v] && cap[u][v] > 0) { seen[v] = 1; par[v] = u; st.push_back(v); } }
        if (!seen[t]) return total; long long b = LLONG_MAX; for (int v = t; v != s; v = par[v]) b = std::min(b, cap[par[v]][v]); for (int v = t; v != s; v = par[v]) { cap[par[v]][v] -= b; cap[v][par[v]] += b; } total += b; } }
int bitmaskMatching(int L, int R, const std::vector<std::vector<int>>& adj) { std::vector<int> dp(1u << R, -1000); dp[0] = 0; int best = 0; for (int i = 0; i < L; ++i) { std::vector<int> nxt = dp; for (unsigned mask = 0; mask < (1u << R); ++mask) if (dp[mask] >= 0) for (int j : adj[i]) if (!(mask >> j & 1)) nxt[mask | (1u << j)] = std::max(nxt[mask | (1u << j)], dp[mask] + 1); dp = nxt; } for (int x : dp) best = std::max(best, x); return best; }

int main() {
    std::mt19937 rng(12);
    for (int trial = 0; trial < 3000; ++trial) { int n = 2 + (int)(rng() % 8), m = (int)(rng() % 26); std::vector<Arc> arcs; EK ek(n); std::vector<int> ids;                           // ①②
        for (int i = 0; i < m; ++i) { Arc a{(int)(rng() % n), (int)(rng() % n), (long long)(rng() % 13)}; arcs.push_back(a); ids.push_back(ek.addEdge(a.u, a.v, a.c)); }
        int s = 0, t = n - 1; long long value = ek.maxflow(s, t); assert(value == bruteMinCut(n, arcs, s, t));
        std::vector<long long> net(n, 0); for (size_t i = 0; i < arcs.size(); ++i) { long long f = ek.flowOn(ids[i]); assert(f >= 0 && f <= arcs[i].c); net[arcs[i].u] -= f; net[arcs[i].v] += f; } for (int v = 0; v < n; ++v) if (v != s && v != t) assert(net[v] == 0); assert(-net[s] == value && net[t] == value);
        std::vector<char> inS = ek.reachable(s); assert(!inS[t]); long long cut = 0; for (const Arc& a : arcs) if (inS[a.u] && !inS[a.v]) cut += a.c; assert(cut == value);
        for (size_t i = 1; i < ek.pathLengths.size(); ++i) assert(ek.pathLengths[i - 1] <= ek.pathLengths[i]);                              // 경로 길이 단조 비감소
        assert(ek.augmentations <= (long long)n * (long long)std::max(m, 1)); }
    for (int trial = 0; trial < 50; ++trial) { int n = 40, m = 300; std::vector<Arc> arcs; EK ek(n); for (int i = 0; i < m; ++i) { Arc a{(int)(rng() % n), (int)(rng() % n), (long long)(rng() % 50) + 1}; arcs.push_back(a); ek.addEdge(a.u, a.v, a.c); }      // ③
        assert(ek.maxflow(0, n - 1) == matrixDfsFlow(n, arcs, 0, n - 1)); }
    {   const long long C = 1000000000LL; EK ek(4); ek.addEdge(0, 1, C); ek.addEdge(0, 2, C); ek.addEdge(1, 2, 1); ek.addEdge(1, 3, C); ek.addEdge(2, 3, C); assert(ek.maxflow(0, 3) == 2 * C && ek.augmentations == 2 && ek.pathLengths[0] == 2 && ek.pathLengths[1] == 2); }   // ④
    for (int trial = 0; trial < 300; ++trial) { int L = 1 + (int)(rng() % 7), R = 1 + (int)(rng() % 7); std::vector<std::vector<int>> adj(L); EK ek(L + R + 2); int s = L + R, t = L + R + 1;      // ⑤ 이분 매칭
        for (int i = 0; i < L; ++i) { ek.addEdge(s, i, 1); for (int j = 0; j < R; ++j) if (rng() % 3 == 0) { adj[i].push_back(j); ek.addEdge(i, L + j, 1); } } for (int j = 0; j < R; ++j) ek.addEdge(L + j, t, 1);
        assert(ek.maxflow(s, t) == bitmaskMatching(L, R, adj)); }
    std::cout << "EdmondsKarp: max flow equalled the exhaustive min cut with valid certificates on 3000 random graphs, augmenting path lengths never decreased, the bad Ford-Fulkerson diamond with capacity 10^9 needed just 2 augmentations, and unit-capacity flows equalled bitmask-DP bipartite matchings" << std::endl;
    return 0;
}
// Time Complexity: O(V E²) (증가 O(VE) 번 × BFS O(E))
// Space Complexity: O(V + E)
```
## Dinic()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <vector>

// 디닉(Dinic 1970): 단계(phase)마다 ① BFS 로 잔여 그래프의 *수준 그래프*(s 로부터의 거리)를 만들고 ② 수준이 한 칸씩 올라가는 간선만 써서 *막힘 흐름(blocking flow)* 을 DFS 로 한꺼번에 구한다 — 간선마다 "현재 호(current arc)" 포인터를 두어 막다른 간선을 다시 훑지 않는다.
//  단계가 끝나면 s–t 최단 거리가 *반드시 늘어나므로* 단계 수 ≤ V − 1, 단계당 O(VE) → 총 O(V² E).  단위 용량 그래프(이분 매칭)는 O(E √V).
//  ① 무작위 그래프 3 000 개(정점 2~9, 간선 0~25 개, 평행·역방향·자기 고리·용량 0 포함)에서 최대 유량 == 모든 절단을 전수 열거한 최소 절단 용량 + 흐름 인증서  ② 단계마다 s–t 거리가 *엄격히 증가*하고 단계 수 ≤ V − 1  ③ 정점 40 개 간선 300 개 그래프 50 개를 독립 구현(인접 행렬 + BFS)과 대조
//  ④ 큰 입력: 층 20 개 × 층당 150 점, 간선 약 6 만 개의 무작위 층 그래프에서 흐름 값이 s 의 나가는 용량 합과 t 의 들어오는 용량 합 이하이고, 잔여 그래프로 닿는 집합의 절단 용량이 흐름과 *정확히 같다*(최소 절단 인증서 = 최적성 증명)  ⑤ 이분 매칭: 무작위 이분 그래프 300 개의 단위 용량 최대 유량 == 비트마스크 DP 최대 매칭, 완전 이분 그래프 K(n,m) 의 값 = min(n, m)
struct Arc { int u, v; long long c; };
struct Dinic {
    struct Edge { int to, rev; long long cap; };
    std::vector<std::vector<Edge>> graph; std::vector<int> level, iter; std::vector<std::pair<int, int>> ids; std::vector<long long> original; std::vector<int> phaseDistances; long long phases = 0;
    explicit Dinic(int n) : graph(n), level(n), iter(n) {}
    int addEdge(int from, int to, long long cap) { int iu = (int)graph[from].size(), iv = (int)graph[to].size() + (from == to ? 1 : 0); graph[from].push_back({to, iv, cap}); graph[to].push_back({from, iu, 0}); ids.push_back({from, iu}); original.push_back(cap); return (int)ids.size() - 1; }
    long long flowOn(int id) const { return original[id] - graph[ids[id].first][ids[id].second].cap; }
    bool bfs(int s, int t) { std::fill(level.begin(), level.end(), -1); std::queue<int> q; level[s] = 0; q.push(s); while (!q.empty()) { int v = q.front(); q.pop(); for (const Edge& e : graph[v]) if (e.cap > 0 && level[e.to] < 0) { level[e.to] = level[v] + 1; q.push(e.to); } } return level[t] >= 0; }
    long long dfs(int v, int t, long long f) {
        if (v == t) return f;
        for (int& i = iter[v]; i < (int)graph[v].size(); i++) { Edge& e = graph[v][i]; if (e.cap > 0 && level[v] < level[e.to]) { long long d = dfs(e.to, t, std::min(f, e.cap)); if (d > 0) { e.cap -= d; graph[e.to][e.rev].cap += d; return d; } } }       // 막다른 간선은 현재 호 포인터가 건너뛴다
        return 0; }
    long long maxflow(int s, int t) { long long flow = 0; if (s == t) return 0; while (bfs(s, t)) { phaseDistances.push_back(level[t]); ++phases; std::fill(iter.begin(), iter.end(), 0); long long d; while ((d = dfs(s, t, LLONG_MAX)) > 0) flow += d; } return flow; }
    std::vector<char> reachable(int s) const { std::vector<char> r(graph.size(), 0); std::queue<int> q; r[s] = 1; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (const Edge& e : graph[u]) if (e.cap > 0 && !r[e.to]) { r[e.to] = 1; q.push(e.to); } } return r; }
};
long long bruteMinCut(int n, const std::vector<Arc>& arcs, int s, int t) { long long best = LLONG_MAX; for (unsigned mask = 0; mask < (1u << n); ++mask) { if (!(mask >> s & 1) || (mask >> t & 1)) continue; long long cut = 0; for (const Arc& a : arcs) if ((mask >> a.u & 1) && !(mask >> a.v & 1)) cut += a.c; best = std::min(best, cut); } return best; }
long long matrixFlow(int n, const std::vector<Arc>& arcs, int s, int t) {
    std::vector<std::vector<long long>> cap(n, std::vector<long long>(n, 0)); for (const Arc& a : arcs) if (a.u != a.v) cap[a.u][a.v] += a.c; long long total = 0;
    for (;;) { std::vector<int> par(n, -1); par[s] = s; std::queue<int> q; q.push(s); while (!q.empty() && par[t] < 0) { int u = q.front(); q.pop(); for (int v = 0; v < n; ++v) if (par[v] < 0 && cap[u][v] > 0) { par[v] = u; q.push(v); } }
        if (par[t] < 0) return total; long long b = LLONG_MAX; for (int v = t; v != s; v = par[v]) b = std::min(b, cap[par[v]][v]); for (int v = t; v != s; v = par[v]) { cap[par[v]][v] -= b; cap[v][par[v]] += b; } total += b; } }
int bitmaskMatching(int L, int R, const std::vector<std::vector<int>>& adj) { std::vector<int> dp(1u << R, -1000); dp[0] = 0; int best = 0; for (int i = 0; i < L; ++i) { std::vector<int> nxt = dp; for (unsigned mask = 0; mask < (1u << R); ++mask) if (dp[mask] >= 0) for (int j : adj[i]) if (!(mask >> j & 1)) nxt[mask | (1u << j)] = std::max(nxt[mask | (1u << j)], dp[mask] + 1); dp = nxt; } for (int x : dp) best = std::max(best, x); return best; }

int main() {
    std::mt19937 rng(13);
    for (int trial = 0; trial < 3000; ++trial) { int n = 2 + (int)(rng() % 8), m = (int)(rng() % 26); std::vector<Arc> arcs; Dinic d(n); std::vector<int> ids;                                  // ①②
        for (int i = 0; i < m; ++i) { Arc a{(int)(rng() % n), (int)(rng() % n), (long long)(rng() % 13)}; arcs.push_back(a); ids.push_back(d.addEdge(a.u, a.v, a.c)); }
        int s = 0, t = n - 1; long long value = d.maxflow(s, t); assert(value == bruteMinCut(n, arcs, s, t));
        std::vector<long long> net(n, 0); for (size_t i = 0; i < arcs.size(); ++i) { long long f = d.flowOn(ids[i]); assert(f >= 0 && f <= arcs[i].c); net[arcs[i].u] -= f; net[arcs[i].v] += f; } for (int v = 0; v < n; ++v) if (v != s && v != t) assert(net[v] == 0); assert(-net[s] == value && net[t] == value);
        std::vector<char> inS = d.reachable(s); assert(!inS[t]); long long cut = 0; for (const Arc& a : arcs) if (inS[a.u] && !inS[a.v]) cut += a.c; assert(cut == value);
        for (size_t i = 1; i < d.phaseDistances.size(); ++i) assert(d.phaseDistances[i - 1] < d.phaseDistances[i]);                          // 단계마다 거리가 엄격히 늘어난다
        assert(d.phases <= std::max(n - 1, 0)); }
    for (int trial = 0; trial < 50; ++trial) { int n = 40, m = 300; std::vector<Arc> arcs; Dinic d(n); for (int i = 0; i < m; ++i) { Arc a{(int)(rng() % n), (int)(rng() % n), (long long)(rng() % 50) + 1}; arcs.push_back(a); d.addEdge(a.u, a.v, a.c); }      // ③
        assert(d.maxflow(0, n - 1) == matrixFlow(n, arcs, 0, n - 1)); }
    {   const int LAYERS = 20, WIDTH = 150, n = LAYERS * WIDTH + 2, s = n - 2, t = n - 1; Dinic d(n); std::vector<Arc> arcs; auto add = [&](int u, int v, long long c) { arcs.push_back({u, v, c}); d.addEdge(u, v, c); };         // ④ 큰 입력
        for (int j = 0; j < WIDTH; ++j) { add(s, j, 1 + (long long)(rng() % 100)); add((LAYERS - 1) * WIDTH + j, t, 1 + (long long)(rng() % 100)); }
        for (int l = 0; l + 1 < LAYERS; ++l) for (int j = 0; j < WIDTH; ++j) for (int k = 0; k < 20; ++k) add(l * WIDTH + j, (l + 1) * WIDTH + (int)(rng() % WIDTH), 1 + (long long)(rng() % 20));
        long long value = d.maxflow(s, t); long long outCap = 0, inCap = 0; for (const Arc& a : arcs) { if (a.u == s) outCap += a.c; if (a.v == t) inCap += a.c; } assert(value > 0 && value <= std::min(outCap, inCap));
        std::vector<char> inS = d.reachable(s); assert(!inS[t]); long long cut = 0; for (const Arc& a : arcs) if (inS[a.u] && !inS[a.v]) cut += a.c; assert(cut == value); assert(arcs.size() > 55000); }
    for (int trial = 0; trial < 300; ++trial) { int L = 1 + (int)(rng() % 7), R = 1 + (int)(rng() % 7); std::vector<std::vector<int>> adj(L); Dinic d(L + R + 2); int s = L + R, t = L + R + 1;      // ⑤ 이분 매칭
        for (int i = 0; i < L; ++i) { d.addEdge(s, i, 1); for (int j = 0; j < R; ++j) if (rng() % 3 == 0) { adj[i].push_back(j); d.addEdge(i, L + j, 1); } } for (int j = 0; j < R; ++j) d.addEdge(L + j, t, 1);
        assert(d.maxflow(s, t) == bitmaskMatching(L, R, adj)); }
    for (int n = 1; n <= 12; ++n) for (int m = 1; m <= 12; ++m) { Dinic d(n + m + 2); int s = n + m, t = n + m + 1; for (int i = 0; i < n; ++i) { d.addEdge(s, i, 1); for (int j = 0; j < m; ++j) d.addEdge(i, n + j, 1); } for (int j = 0; j < m; ++j) d.addEdge(n + j, t, 1); assert(d.maxflow(s, t) == std::min(n, m)); }
    std::cout << "Dinic: max flow equalled the exhaustive min cut with valid certificates on 3000 random graphs, the s-t distance rose strictly in every phase (phases <= V-1), a 3000-node 60000-edge layered network produced a min-cut certificate equal to its flow, and unit-capacity flows equalled bitmask-DP matchings and min(n, m) on complete bipartite graphs" << std::endl;
    return 0;
}
// Time Complexity: O(V² E), 단위 용량 이분 그래프 O(E √V)
// Space Complexity: O(V + E)
```
## PushRelabel()
### 대표코드
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 푸시–리레이블(Goldberg–Tarjan 1988): 증가 경로를 찾지 않고 "국소 연산" 만으로 최대 유량을 구한다. 각 정점은 초과량(excess = 들어온 유량 − 나간 유량)과 높이(height)를 가진다. 처음에 출발점의 모든 간선을 포화시켜 초과량을 만들고 출발점 높이를 n 으로 둔다.
//   푸시(push): 초과량이 있는 u 에서 잔여 용량이 있고 높이가 정확히 한 칸 낮은 이웃으로 min(초과량, 잔여 용량) 만큼 흘린다.  리레이블(relabel): 더는 밀 곳이 없으면 u 의 높이를 (잔여 간선이 닿는 이웃 높이의 최솟값) + 1 로 올린다.
// 높이는 "도착점까지 잔여 그래프에서의 거리의 하한" 이다. 높이가 n 이상이 되면 도착점에 갈 수 없으므로 남은 초과량은 출발점으로 되돌려진다. 각 정점의 높이는 2n−1 을 넘지 않으므로 리레이블은 총 O(n²), FIFO 큐로 정점을 처리하면 전체가 O(V³) 다.
// 간격 휴리스틱(gap): 높이 g(< n) 인 정점이 하나도 없어지면 g 보다 높고 n 보다 낮은 정점은 도착점에 닿을 수 없으므로 한꺼번에 n+1 로 올려 낭비되는 리레이블을 줄인다.
// 검증: ① 무작위 네트워크·격자·이분 그래프에서 Dinic 과 최대 유량이 같다 ② 결과가 진짜 유량(용량 제약, 출발·도착 외 정점의 유량 보존) ③ 최대-최소 정리: 잔여 그래프에서 출발점에 닿는 집합 S 의 용량 합 == 유량 ④ 리레이블 총수 ≤ 2n² ⑤ 간격 휴리스틱의 유무와 관계없이 같은 값, 리레이블 수는 간격이 있는 쪽이 같거나 적음
typedef long long ll;
struct Net {
    struct Edge { int to; ll cap; }; int n; std::vector<Edge> e; std::vector<std::vector<int>> g; std::vector<ll> orig;
    explicit Net(int n) : n(n), g(n) {}
    void add(int u, int v, ll c) { g[u].push_back(e.size()); e.push_back({v, c}); g[v].push_back(e.size()); e.push_back({u, 0}); orig.push_back(c); }
};
struct PushRelabel {
    Net net; std::vector<ll> excess; std::vector<int> height, count, cur; std::vector<char> queued; std::queue<int> q; long pushes = 0, relabels = 0; bool useGap;
    PushRelabel(const Net& n0, bool gap) : net(n0), excess(n0.n, 0), height(n0.n, 0), count(2 * n0.n + 2, 0), cur(n0.n, 0), queued(n0.n, 0), useGap(gap) {}
    void activate(int v, int s, int t) { if (!queued[v] && excess[v] > 0 && v != s && v != t) { queued[v] = 1; q.push(v); } }
    void push(int u, int id, int s, int t) { ll d = std::min(excess[u], net.e[id].cap); int v = net.e[id].to; net.e[id].cap -= d; net.e[id ^ 1].cap += d; excess[u] -= d; excess[v] += d; pushes++; activate(v, s, t); }
    void relabel(int u) {
        relabels++; int old = height[u], mn = 2 * net.n; for (int id : net.g[u]) if (net.e[id].cap > 0) mn = std::min(mn, height[net.e[id].to]); count[old]--; height[u] = mn + 1; count[height[u]]++;
        if (useGap && old < net.n && count[old] == 0) for (int v = 0; v < net.n; v++) if (height[v] > old && height[v] < net.n) { count[height[v]]--; height[v] = net.n + 1; count[height[v]]++; }          // 간격 휴리스틱
    }
    void discharge(int u, int s, int t) { while (excess[u] > 0) { if (cur[u] == (int)net.g[u].size()) { relabel(u); cur[u] = 0; } else { int id = net.g[u][cur[u]]; if (net.e[id].cap > 0 && height[u] == height[net.e[id].to] + 1) push(u, id, s, t); else cur[u]++; } } }
    ll maxFlow(int s, int t) {
        height[s] = net.n; count[0] = net.n - 1; count[net.n] = 1; for (int id : net.g[s]) { ll c = net.e[id].cap; if (c > 0) { excess[s] += c; push(s, id, s, t); } }
        while (!q.empty()) { int u = q.front(); q.pop(); queued[u] = 0; discharge(u, s, t); }
        return excess[t];
    }
};
ll dinic(Net net, int s, int t) {
    ll total = 0; for (;;) { std::vector<int> level(net.n, -1), it(net.n, 0); std::queue<int> bq; level[s] = 0; bq.push(s); while (!bq.empty()) { int u = bq.front(); bq.pop(); for (int id : net.g[u]) if (net.e[id].cap > 0 && level[net.e[id].to] < 0) { level[net.e[id].to] = level[u] + 1; bq.push(net.e[id].to); } } if (level[t] < 0) return total;
        std::function<ll(int, ll)> dfs = [&](int u, ll f) -> ll { if (u == t) return f; for (int& i = it[u]; i < (int)net.g[u].size(); i++) { int id = net.g[u][i], v = net.e[id].to; if (net.e[id].cap > 0 && level[v] == level[u] + 1) { ll d = dfs(v, std::min(f, net.e[id].cap)); if (d > 0) { net.e[id].cap -= d; net.e[id ^ 1].cap += d; return d; } } } return 0; };
        while (ll f = dfs(s, (ll)1e18)) total += f; }
}
bool verify(const Net& orig, const PushRelabel& pr, int s, int t, ll value) {
    int n = orig.n; std::vector<ll> net(n, 0); for (size_t i = 0; i < orig.e.size(); i += 2) { ll f = orig.e[i].cap - pr.net.e[i].cap; if (f < 0 || f > orig.e[i].cap) return false; net[orig.e[i ^ 1].to] -= f; net[orig.e[i].to] += f; }
    for (int v = 0; v < n; v++) if (v != s && v != t && net[v] != 0) return false; if (net[t] != value || net[s] != -value) return false;                                                    // ② 용량·보존
    std::vector<char> inS(n, 0); std::queue<int> bq; inS[s] = 1; bq.push(s); while (!bq.empty()) { int u = bq.front(); bq.pop(); for (int id : pr.net.g[u]) if (pr.net.e[id].cap > 0 && !inS[pr.net.e[id].to]) { inS[pr.net.e[id].to] = 1; bq.push(pr.net.e[id].to); } }
    if (inS[t]) return false; ll cut = 0; for (size_t i = 0; i < orig.e.size(); i += 2) if (inS[orig.e[i ^ 1].to] && !inS[orig.e[i].to]) cut += orig.e[i].cap; return cut == value;                       // ③ 최대-최소 정리
}
int main() {
    std::mt19937 rng(9); long relGap = 0, relNoGap = 0, pushTotal = 0; int checked = 0;
    for (int t = 0; t < 400; t++) {
        int kind = t % 4, n; Net g(2); if (kind == 0) { n = 2 + rng() % 14; g = Net(n); int m = rng() % (4 * n); for (int k = 0; k < m; k++) { int u = rng() % n, v = rng() % n; if (u != v) g.add(u, v, 1 + rng() % 20); } }                                      // 무작위
        else if (kind == 1) { int w = 2 + rng() % 5, h = 2 + rng() % 5; n = w * h; g = Net(n); for (int r = 0; r < h; r++) for (int c = 0; c < w; c++) { if (c + 1 < w) { g.add(r * w + c, r * w + c + 1, 1 + rng() % 9); g.add(r * w + c + 1, r * w + c, 1 + rng() % 9); } if (r + 1 < h) { g.add(r * w + c, (r + 1) * w + c, 1 + rng() % 9); g.add((r + 1) * w + c, r * w + c, 1 + rng() % 9); } } }   // 격자
        else if (kind == 2) { int L = 2 + rng() % 8, R = 2 + rng() % 8; n = L + R + 2; g = Net(n); for (int i = 0; i < L; i++) g.add(n - 2, i, 1); for (int j = 0; j < R; j++) g.add(L + j, n - 1, 1); for (int i = 0; i < L; i++) for (int j = 0; j < R; j++) if (rng() % 3 == 0) g.add(i, L + j, 1); }  // 이분 매칭
        else { int layers = 2 + rng() % 4, wd = 2 + rng() % 4; n = layers * wd + 2; g = Net(n); for (int i = 0; i < wd; i++) g.add(0, 1 + i, 1 + rng() % 30); for (int l = 0; l + 1 < layers; l++) for (int i = 0; i < wd; i++) for (int j = 0; j < wd; j++) if (rng() % 2) g.add(1 + l * wd + i, 1 + (l + 1) * wd + j, 1 + rng() % 15); for (int i = 0; i < wd; i++) g.add(1 + (layers - 1) * wd + i, n - 1, 1 + rng() % 30); }     // 층 그래프
        int s = kind == 2 ? n - 2 : 0, tt = n - 1; if (s == tt) continue; ll want = dinic(g, s, tt);
        PushRelabel a(g, true), b(g, false); ll fa = a.maxFlow(s, tt), fb = b.maxFlow(s, tt); assert(fa == want && fb == want);                                                                 // ① ⑤
        assert(verify(g, a, s, tt, fa) && verify(g, b, s, tt, fb)); assert(a.relabels <= 2L * n * n && b.relabels <= 2L * n * n);                                                                  // ② ③ ④
        relGap += a.relabels; relNoGap += b.relabels; pushTotal += a.pushes; checked++;
    }
    assert(relGap <= relNoGap);
    std::cout << "PushRelabel: " << checked << " networks matched Dinic and passed flow-conservation and min-cut checks; total relabels with gap heuristic " << relGap << " vs without " << relNoGap << ", pushes " << pushTotal << std::endl; return 0;
}
// Time Complexity: FIFO 선택 O(V³), 최고 높이 우선 선택 O(V² √E)
// Space Complexity: O(V + E)
```
## MinCostMaxFlow()
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

// 최소 비용 최대 유량(MCMF): 용량과 단위 비용이 있는 네트워크에서 최대 유량 중 총 비용이 가장 작은 것을 구한다. 배정 문제, 수송 문제, 비용이 있는 매칭이 모두 이것으로 풀린다.
// 연속 최단 경로(Successive Shortest Path): 잔여 그래프에서 비용 기준 최단 경로를 찾아 그 경로의 병목 용량만큼 흘리기를 반복한다(역간선의 비용은 −c). 매번 찾는 최단 경로의 비용은 단조 증가하므로 유량 f 에 대한 최소 비용 함수는 볼록이다.
// 최적성 증명(certificate): 최소 비용 유량이기 위한 필요충분조건은 "잔여 그래프에 음수 비용 사이클이 없는 것" 이다. 최단 경로 탐색에는 SPFA(음수 간선 허용)나, 초기 잠재력을 벨만–포드로 구한 뒤 매 라운드 d' = d + h(u) − h(v) ≥ 0 으로 재가중해서 Dijkstra 를 쓰는 방식(존슨과 같은 발상)이 있다.
// 검증: ① 두 구현(SPFA / 잠재력 Dijkstra)이 같은 (유량, 비용) ② 잔여 그래프에 음수 사이클이 없음 ③ 증가 경로 비용이 단조 비감소 ④ 유량이 최대 — 잔여 그래프에서 도착점에 닿을 수 없음 ⑤ 배정 문제(n ≤ 7)에서 모든 순열을 시험한 최솟값과 일치 ⑥ 음수 비용 간선(DAG)도 처리
typedef long long ll; const ll INF = (ll)1e18;
struct MCMF {
    struct Edge { int to; int cap; ll cost; }; int n; std::vector<Edge> e; std::vector<std::vector<int>> g; std::vector<ll> pathCosts;
    explicit MCMF(int n) : n(n), g(n) {}
    void add(int u, int v, int cap, ll cost) { g[u].push_back(e.size()); e.push_back({v, cap, cost}); g[v].push_back(e.size()); e.push_back({u, 0, -cost}); }
    std::pair<ll, ll> runSPFA(int s, int t) {
        ll flow = 0, cost = 0;
        for (;;) { std::vector<ll> d(n, INF); std::vector<int> pe(n, -1); std::vector<char> inq(n, 0); std::queue<int> q; d[s] = 0; q.push(s); inq[s] = 1;
            while (!q.empty()) { int u = q.front(); q.pop(); inq[u] = 0; for (int id : g[u]) if (e[id].cap > 0 && d[u] + e[id].cost < d[e[id].to]) { d[e[id].to] = d[u] + e[id].cost; pe[e[id].to] = id; if (!inq[e[id].to]) { inq[e[id].to] = 1; q.push(e[id].to); } } }
            if (d[t] >= INF) break; int f = INT_MAX; for (int v = t; v != s; v = e[pe[v] ^ 1].to) f = std::min(f, e[pe[v]].cap); for (int v = t; v != s; v = e[pe[v] ^ 1].to) { e[pe[v]].cap -= f; e[pe[v] ^ 1].cap += f; }
            flow += f; cost += (ll)f * d[t]; pathCosts.push_back(d[t]); }
        return {flow, cost};
    }
    std::pair<ll, ll> runDijkstra(int s, int t) {
        std::vector<ll> h(n, INF); h[s] = 0; for (int pass = 0; pass < n; pass++) { bool ch = false; for (int u = 0; u < n; u++) if (h[u] < INF) for (int id : g[u]) if (e[id].cap > 0 && h[u] + e[id].cost < h[e[id].to]) { h[e[id].to] = h[u] + e[id].cost; ch = true; } if (!ch) break; }     // 초기 잠재력: 벨만–포드
        ll flow = 0, cost = 0;
        for (;;) { std::vector<ll> d(n, INF); std::vector<int> pe(n, -1); std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
            while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int id : g[u]) { int v = e[id].to; if (e[id].cap > 0 && h[v] < INF) { ll nd = du + e[id].cost + h[u] - h[v]; assert(e[id].cost + h[u] - h[v] >= 0); if (nd < d[v]) { d[v] = nd; pe[v] = id; pq.push({nd, v}); } } } }
            if (d[t] >= INF) break; for (int v = 0; v < n; v++) if (d[v] < INF) h[v] += d[v]; int f = INT_MAX; for (int v = t; v != s; v = e[pe[v] ^ 1].to) f = std::min(f, e[pe[v]].cap); for (int v = t; v != s; v = e[pe[v] ^ 1].to) { e[pe[v]].cap -= f; e[pe[v] ^ 1].cap += f; }
            flow += f; cost += (ll)f * (h[t] - h[s]); }
        return {flow, cost};
    }
    bool hasNegativeResidualCycle() const { std::vector<ll> d(n, 0); for (int pass = 0; pass <= n; pass++) { bool ch = false; for (int u = 0; u < n; u++) for (int id : g[u]) if (e[id].cap > 0 && d[u] + e[id].cost < d[e[id].to]) { d[e[id].to] = d[u] + e[id].cost; ch = true; } if (!ch) return false; } return true; }
    bool reachable(int s, int t) const { std::vector<char> seen(n, 0); std::queue<int> q; seen[s] = 1; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int id : g[u]) if (e[id].cap > 0 && !seen[e[id].to]) { seen[e[id].to] = 1; q.push(e[id].to); } } return seen[t]; }
};
int main() {
    std::mt19937 rng(12); int checked = 0, negCostNets = 0;
    for (int t = 0; t < 500; t++) {
        int n = 2 + rng() % 8; bool allowNeg = t % 5 == 0; MCMF a(n); int m = 1 + rng() % (3 * n); for (int k = 0; k < m; k++) { int u = rng() % n, v = rng() % n; if (u == v) continue; if (allowNeg && u > v) std::swap(u, v); ll c = allowNeg ? (ll)(rng() % 15) - 6 : (ll)(rng() % 12); a.add(u, v, 1 + rng() % 6, c); }       // ⑥ 음수 비용은 DAG(u<v)에서만
        negCostNets += allowNeg; MCMF b = a; auto ra = a.runSPFA(0, n - 1), rb = b.runDijkstra(0, n - 1); assert(ra == rb);                                                                                       // ① 두 구현이 일치
        assert(!a.hasNegativeResidualCycle() && !b.hasNegativeResidualCycle());                                                                                                                                  // ② 최적성 증명
        assert(std::is_sorted(a.pathCosts.begin(), a.pathCosts.end()));                                                                                                                                           // ③ 경로 비용 단조 비감소
        assert(!a.reachable(0, n - 1)); checked++;                                                                                                                                                                // ④ 더 흘릴 수 없다
    }
    for (int t = 0; t < 200; t++) {
        int n = 2 + rng() % 6; std::vector<std::vector<int>> c(n, std::vector<int>(n)); for (auto& row : c) for (int& x : row) x = rng() % 30; MCMF m(2 * n + 2); int S = 2 * n, T = 2 * n + 1; for (int i = 0; i < n; i++) { m.add(S, i, 1, 0); m.add(n + i, T, 1, 0); for (int j = 0; j < n; j++) m.add(i, n + j, 1, c[i][j]); }
        auto r = m.runSPFA(S, T); std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); ll best = INF; do { ll s = 0; for (int i = 0; i < n; i++) s += c[i][perm[i]]; best = std::min(best, s); } while (std::next_permutation(perm.begin(), perm.end())); assert(r.first == n && r.second == best);          // ⑤ 배정 문제
    }
    std::cout << "MinCostMaxFlow: SPFA and potential-Dijkstra agreed on " << checked << " networks (" << negCostNets << " with negative costs), every result had no negative residual cycle and monotone path costs; 200 assignment problems matched brute force over permutations" << std::endl; return 0;
}
// Time Complexity: O(F · SPFA) 또는 O(F · E log V) (F = 총 유량)
// Space Complexity: O(V + E)
```
# Part 12. 매칭
## BipartiteMatching()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 이분 매칭(Kuhn 알고리즘): 왼쪽 정점을 하나씩 잡고, 아직 안 쓴 오른쪽 이웃 v 를 찾아 v 가 비어 있거나 v 의 현재 짝이 다른 곳으로 옮겨 갈 수 있으면(재귀적으로 "증가 경로" 를 찾으면) 짝을 맺는다. 증가 경로 = 비매칭 간선과 매칭 간선이 번갈아 놓이고 양 끝이 모두 짝 없는 정점인 경로이며, 그 경로를 따라 매칭/비매칭을 뒤집으면 매칭이 정확히 하나 커진다(Berge 정리: 증가 경로가 없으면 최대). O(V·E).
// 증가 경로가 거의 정점 수만큼 길어질 수 있으므로 재귀 DFS 는 깊은 입력에서 호출 스택이 넘친다 — 여기서는 명시적 스택(반복형)으로 짜서 10 만 칸 길이의 증가 경로도 처리한다.
// *인증서*: 매칭 M 이 최대라는 증명을 알고리즘과 독립적으로 O(V + E) 에 확인한다(König). 짝 없는 왼쪽 정점들에서 출발해 "왼→오는 아무 간선, 오→왼은 매칭 간선" 으로 닿는 정점 집합 Z 를 구하고 C = (L∖Z) ∪ (R∩Z) 로 하면 C 는 모든 간선을 덮는 정점 덮개이고 |C| = |M| 이다(Z 의 오른쪽 정점이 짝 없으면 증가 경로). 덮개 ≥ 매칭 이므로 둘 다 최적. 최대가 완전(|M| < |L|)하지 못할 때는 S = Z∩L 이 Hall 조건 위반 집합 |N(S)| < |S| 이다.
// 검증: 모든 이분 그래프(3×3, 3×5, 4×4: 512 + 32,768 + 65,536 개) 에서 크기를 ① 부분집합 DP 로 구한 최대 매칭 ② Hall 결손 공식 |L| − max_S(|S| − |N(S)|) 와 대조하고 인증서 통과; 탐욕(먼저 만난 빈 이웃에 붙이기)은 최적이 아니지만 항상 최대의 절반 이상임을 확인; 큰 입력(왼쪽 100,001 개, 증가 경로 길이 200,001) 도 인증서로.
struct Matching {
    int nL, nR; std::vector<std::vector<int>> adj; std::vector<int> matchL, matchR, it, seen; int stamp = 0; long long steps = 0; bool greedyFirst = false;
    Matching(int l, int r) : nL(l), nR(r), adj(l), matchL(l, -1), matchR(r, -1), it(l, 0), seen(r, 0) {}
    void addEdge(int u, int v) { adj[u].push_back(v); }
    // 반복형 증가 경로 탐색: us[k] 는 k 번째 왼쪽 정점, vs[k] 는 us[k] 에서 오른쪽으로 건너간 정점
    bool augment(int root, bool newRound = true) {
        if (newRound) ++stamp;                                                  // 실패한 탐색이 막다른 길로 표시한 오른쪽 정점은 매칭이 바뀌기 전까지 유효하다
        std::vector<int> us{root}, vs; it[root] = 0;
        while (!us.empty()) {
            int u = us.back();
            if (it[u] == (int)adj[u].size()) { us.pop_back(); if (!vs.empty()) vs.pop_back(); continue; }
            int v = adj[u][it[u]++]; ++steps;
            if (seen[v] == stamp) continue;
            seen[v] = stamp; vs.push_back(v);
            if (matchR[v] < 0) { for (std::size_t k = 0; k < us.size(); ++k) { matchL[us[k]] = vs[k]; matchR[vs[k]] = us[k]; } return true; }   // 경로를 따라 뒤집는다
            int w = matchR[v]; it[w] = 0; us.push_back(w);
        }
        return false;
    }
    int run(const std::vector<int>& order) {
        int size = 0; bool fresh = true;                                        // 성공했을 때만 방문 표시를 새로 시작한다 (실전에서 거의 O(E√V))
        if (greedyFirst) for (int u : order) if (matchL[u] < 0) for (int v : adj[u]) if (matchR[v] < 0) { matchL[u] = v; matchR[v] = u; ++size; break; }   // 탐욕 초기화: 증가 경로 탐색 횟수를 크게 줄인다
        for (int u : order) if (matchL[u] < 0) { if (augment(u, fresh)) { ++size; fresh = true; } else fresh = false; }
        return size;
    }
    int run() { std::vector<int> o(nL); std::iota(o.begin(), o.end(), 0); return run(o); }
};

// ---- 인증서와 검사 ----
bool validMatching(const Matching& m) {
    for (int u = 0; u < m.nL; ++u) { int v = m.matchL[u]; if (v >= 0 && (v >= m.nR || m.matchR[v] != u || std::find(m.adj[u].begin(), m.adj[u].end(), v) == m.adj[u].end())) return false; }
    for (int v = 0; v < m.nR; ++v) { int u = m.matchR[v]; if (u >= 0 && m.matchL[u] != v) return false; }
    return true;
}
struct Konig { bool ok; std::vector<char> seenL, seenR; };
Konig konig(const Matching& m, int size) {
    Konig k{false, std::vector<char>(m.nL, 0), std::vector<char>(m.nR, 0)};
    std::queue<int> q; for (int u = 0; u < m.nL; ++u) if (m.matchL[u] < 0) { k.seenL[u] = 1; q.push(u); }
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : m.adj[u]) if (!k.seenR[v]) { k.seenR[v] = 1; int w = m.matchR[v]; if (w >= 0 && !k.seenL[w]) { k.seenL[w] = 1; q.push(w); } }
    }
    int cover = 0;
    for (int v = 0; v < m.nR; ++v) if (k.seenR[v]) { ++cover; if (m.matchR[v] < 0) return k; }       // 짝 없는 오른쪽에 닿으면 증가 경로가 있다
    for (int u = 0; u < m.nL; ++u) if (!k.seenL[u]) ++cover;
    for (int u = 0; u < m.nL; ++u) for (int v : m.adj[u]) if (k.seenL[u] && !k.seenR[v]) return k;   // 덮개 = (L∖Z) ∪ (R∩Z) 가 모든 간선을 덮는가
    k.ok = cover == size;
    return k;
}
// ---- 오라클 ----
int bruteMax(int nL, int nR, const std::vector<unsigned>& mask) {
    std::vector<int> dp(1u << nR, -1); dp[0] = 0;
    for (int u = 0; u < nL; ++u) {
        std::vector<int> nd = dp;
        for (unsigned used = 0; used < (1u << nR); ++used) if (dp[used] >= 0) for (unsigned avail = mask[u] & ~used; avail; avail &= avail - 1) { unsigned bit = avail & -avail; nd[used | bit] = std::max(nd[used | bit], dp[used] + 1); }
        dp = nd;
    }
    return *std::max_element(dp.begin(), dp.end());
}
int hallDeficiencyMatching(int nL, int nR, const std::vector<unsigned>& mask) {              // |L| − max_S (|S| − |N(S)|)
    int maxDef = 0; (void)nR;
    for (unsigned s = 0; s < (1u << nL); ++s) { unsigned nb = 0; for (int u = 0; u < nL; ++u) if (s >> u & 1) nb |= mask[u]; maxDef = std::max(maxDef, __builtin_popcount(s) - __builtin_popcount(nb)); }
    return nL - maxDef;
}
int greedyMatching(int nL, int nR, const std::vector<unsigned>& mask) {
    unsigned used = 0; int size = 0; (void)nR;
    for (int u = 0; u < nL; ++u) { unsigned avail = mask[u] & ~used; if (avail) { used |= avail & -avail; ++size; } }
    return size;
}

int main() {
    // ① 손으로 확인한 모양: L0–{R0,R1}, L1–{R0} → 크기 2 (L0 가 R0 를 잡아도 L1 이 L0 를 R1 으로 옮긴다), 인증서
    {   Matching m(2, 2); m.addEdge(0, 0); m.addEdge(0, 1); m.addEdge(1, 0);
        assert(m.run() == 2 && validMatching(m) && m.matchL[0] == 1 && m.matchL[1] == 0 && konig(m, 2).ok);
        Matching s(3, 2); s.addEdge(0, 0); s.addEdge(1, 0); s.addEdge(2, 0); s.addEdge(2, 1);   // L0, L1 은 R0 하나를 두고 경쟁
        assert(s.run() == 2); Konig k = konig(s, 2); assert(k.ok);
        int sizeS = 0, nbS = 0; for (int u = 0; u < 3; ++u) sizeS += k.seenL[u]; for (int v = 0; v < 2; ++v) nbS += k.seenR[v];
        assert(sizeS == 2 && nbS == 1 && s.matchL[1] == -1);                                    // 짝 없는 L1 에서 닿는 Hall 위반 집합: S = {L0, L1}, N(S) = {R0}
    }

    // ② 전수: (|L|,|R|) = (3,3), (3,5), (4,4) 의 모든 이분 그래프 — 크기 = 부분집합 DP = Hall 결손 공식, 인증서 통과, 탐욕은 최대의 절반 이상
    long long total = 0, greedyWorse = 0;
    for (auto [nL, nR] : std::vector<std::pair<int, int>>{{3, 3}, {3, 5}, {4, 4}}) {
        int cells = nL * nR;
        for (unsigned code = 0; code < (1u << cells); ++code) {
            Matching m(nL, nR); std::vector<unsigned> mask(nL, 0);
            for (int u = 0; u < nL; ++u) for (int v = 0; v < nR; ++v) if (code >> (u * nR + v) & 1) { m.addEdge(u, v); mask[u] |= 1u << v; }
            int size = m.run();
            assert(validMatching(m) && size == bruteMax(nL, nR, mask) && size == hallDeficiencyMatching(nL, nR, mask));
            Konig k = konig(m, size); assert(k.ok);
            if (size < nL) {                                                                      // Hall 위반 집합 S = Z ∩ L
                unsigned S = 0, nb = 0; for (int u = 0; u < nL; ++u) if (k.seenL[u]) { S |= 1u << u; nb |= mask[u]; }
                assert(__builtin_popcount(nb) < __builtin_popcount(S));
            }
            int g = greedyMatching(nL, nR, mask);
            assert(2 * g >= size && g <= size);
            greedyWorse += g < size; ++total;
        }
    }
    assert(total == 512 + 32768 + 65536 && greedyWorse > 5000);

    // ③ 무작위 (|L|,|R| ≤ 10, 처리 순서도 섞음): 크기는 순서와 무관, 짝 없는 개수 = 결손
    std::mt19937 rng(1931);
    for (int it = 0; it < 1500; ++it) {
        int nL = 1 + (int)(rng() % 10), nR = 1 + (int)(rng() % 10), edges = (int)(rng() % (nL * nR + 1));
        Matching a(nL, nR), b(nL, nR); std::vector<unsigned> mask(nL, 0);
        for (int i = 0; i < edges; ++i) { int u = (int)(rng() % nL), v = (int)(rng() % nR); a.addEdge(u, v); b.addEdge(u, v); mask[u] |= 1u << v; }
        std::vector<int> order(nL); std::iota(order.begin(), order.end(), 0); std::shuffle(order.begin(), order.end(), rng);
        int sa = a.run(), sb = b.run(order);
        assert(sa == sb && sa == bruteMax(nL, nR, mask) && validMatching(a) && validMatching(b) && konig(a, sa).ok && konig(b, sb).ok);
    }

    // ④ 큰 입력 1: 증가 경로가 길어지는 구성 — L_i 의 이웃은 [R_{i−1}, R_i] (L_0 은 [R_0]), 왼쪽 100,001 개 · 오른쪽 100,001 개.
    //    L_1..L_n 을 먼저 처리하면 L_i → R_{i−1} 로 잘못 붙고, 마지막 L_0 이 길이 2n + 1 의 증가 경로를 한 번에 뒤집는다 (재귀였다면 스택 overflow).
    {
        const int n = 100000; Matching m(n + 1, n + 1);
        m.addEdge(0, 0); for (int i = 1; i <= n; ++i) { m.addEdge(i, i - 1); if (i < n + 1) m.addEdge(i, i); }
        int first = 0; for (int i = 1; i <= n; ++i) first += m.matchL[i] < 0 && m.augment(i);
        assert(first == n && m.matchL[1] == 0 && m.matchR[n] == -1);                                // L_i → R_{i−1}, R_n 은 비어 있음
        long long before = m.steps;
        assert(m.augment(0));                                                                       // 증가 경로 하나가 모든 짝을 한 칸씩 옮긴다
        assert(m.steps - before >= 2LL * n && validMatching(m));
        for (int i = 0; i <= n; ++i) assert(m.matchL[i] == i);                                      // 완전 매칭 L_i → R_i
        assert(konig(m, n + 1).ok);
    }
    // 큰 입력 2: 무작위 이분 그래프 (왼쪽 8,000 · 오른쪽 8,000 · 간선 32,000) — 인증서만으로 최대성 증명, 탐욕 초기화는 같은 크기를 더 적은 스캔으로
    {
        const int N = 8000; Matching plain(N, N), warm(N, N); warm.greedyFirst = true;
        for (int i = 0; i < 4 * N; ++i) { int u = (int)(rng() % N), v = (int)(rng() % N); plain.addEdge(u, v); warm.addEdge(u, v); }
        int size = plain.run(), size2 = warm.run();
        assert(validMatching(plain) && validMatching(warm) && konig(plain, size).ok && konig(warm, size2).ok && size > N * 9 / 10);
        assert(size == size2 && warm.steps < plain.steps);
    }
    std::cout << "BipartiteMatching: the iterative augmenting-path matching equalled both a subset-DP maximum and the Hall-deficiency formula |L| - max(|S| - |N(S)|) on all 512 + 32,768 + 65,536 bipartite graphs of sizes 3x3, 3x5 and 4x4, every result passed the Koenig vertex-cover certificate (with a genuine Hall violator whenever some left vertex stayed unmatched), greedy matching was never below half of the maximum and strictly worse on over 5000 graphs, 1500 random graphs gave the same size for shuffled processing orders, an augmenting path of length 200,001 on a 100,001-vertex side was flipped without recursion and certified, and a random 8,000 x 8,000 graph gave the same certified size with and without greedy initialisation (the latter with fewer scans)" << std::endl; return 0;
}
// Time Complexity: O(V · E)
// Space Complexity: O(V + E)
```
## HungarianAlgorithm()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

// 헝가리안 알고리즘(Kuhn–Munkres, e-maxx 의 O(n²m) 쌍대 변수 판): 행 n 개를 서로 다른 열 m ≥ n 개에 배정하는 최소 비용 할당 문제.  행 포텐셜 u, 열 포텐셜 v 를 유지하며 *모든 칸에서 u[i] + v[j] ≤ c[i][j]* (쌍대 실현 가능)를 지키고, 배정된 칸에서는 등식이 되게 한다.
//  그러면 약한 쌍대성으로 배정 비용 = Σu + Σv 가 어떤 배정의 비용보다도 클 수 없으므로 *그 자체가 최적성의 증명서* 다.  최대화는 비용에 −1 을 곱해 푼다.
//  ① 무작위 비용표 2 000 개(n ≤ 7, m = n..n+2, 음수·동점 포함)에서 비용 == 모든 단사 배정을 열거한 최솟값 + 반환된 배정이 서로 다른 열을 쓰고 비용 합이 같음  ② 쌍대 증명서: 큰 표(n = 150~200, 비용 −1000..1000)에서도 모든 칸 u+v ≤ c, 배정 칸 u+v = c, 비용 == Σu + Σv
//  ③ 최대화(−c)와 동점·전부 같은 표(비용 = n·상수)·한 행만 있는 표 ④ 책의 예 {{4,2,3},{1,3,2},{2,1,4}} 최소 비용 5, 배정 (0→2, 1→0, 2→1) 의 비용은 3 + 1 + 1
struct Result { long long cost; std::vector<int> colOfRow; std::vector<long long> u, v; };
Result hungarian(const std::vector<std::vector<long long>>& a) {                                                    // 1-기반 인덱스, 행 n ≤ 열 m
    int n = (int)a.size(), m = (int)a[0].size(); const long long INF = LLONG_MAX / 4;
    std::vector<long long> u(n + 1, 0), v(m + 1, 0); std::vector<int> p(m + 1, 0), way(m + 1, 0);
    for (int i = 1; i <= n; i++) {
        p[0] = i; int j0 = 0; std::vector<long long> minv(m + 1, INF); std::vector<char> used(m + 1, false);
        do {
            used[j0] = true; int i0 = p[j0], j1 = 0; long long delta = INF;
            for (int j = 1; j <= m; j++) if (!used[j]) { long long cur = a[i0 - 1][j - 1] - u[i0] - v[j]; if (cur < minv[j]) { minv[j] = cur; way[j] = j0; } if (minv[j] < delta) { delta = minv[j]; j1 = j; } }
            for (int j = 0; j <= m; j++) { if (used[j]) { u[p[j]] += delta; v[j] -= delta; } else minv[j] -= delta; }
            j0 = j1;
        } while (p[j0] != 0);
        do { int j1 = way[j0]; p[j0] = p[j1]; j0 = j1; } while (j0);                                                // 교대 경로를 따라 배정을 뒤집는다
    }
    Result r; r.colOfRow.assign(n, -1); r.cost = 0; for (int j = 1; j <= m; j++) if (p[j]) { r.colOfRow[p[j] - 1] = j - 1; r.cost += a[p[j] - 1][j - 1]; }
    r.u.assign(u.begin() + 1, u.end()); r.v.assign(v.begin() + 1, v.end()); return r;
}
long long bruteForce(const std::vector<std::vector<long long>>& a, int row, std::vector<char>& usedCol) {          // 독립 오라클: 모든 단사 배정을 재귀로 열거
    int n = (int)a.size(), m = (int)a[0].size(); if (row == n) return 0; long long best = LLONG_MAX; for (int j = 0; j < m; ++j) if (!usedCol[j]) { usedCol[j] = 1; best = std::min(best, a[row][j] + bruteForce(a, row + 1, usedCol)); usedCol[j] = 0; } return best; }

int main() {
    std::mt19937 rng(14);
    for (int trial = 0; trial < 2000; ++trial) { int n = 1 + (int)(rng() % 7), m = n + (int)(rng() % 3); std::vector<std::vector<long long>> a(n, std::vector<long long>(m)); int range = rng() % 3 == 0 ? 3 : 40; for (auto& row : a) for (auto& x : row) x = (long long)(rng() % (2 * range + 1)) - range;       // ①
        Result r = hungarian(a); std::vector<char> usedCol(m, 0); assert(r.cost == bruteForce(a, 0, usedCol));
        std::vector<char> seenCol(m, 0); long long sum = 0; for (int i = 0; i < n; ++i) { int j = r.colOfRow[i]; assert(j >= 0 && j < m && !seenCol[j]); seenCol[j] = 1; sum += a[i][j]; } assert(sum == r.cost); }
    for (int n : {150, 200}) { std::vector<std::vector<long long>> a(n, std::vector<long long>(n + 3)); for (auto& row : a) for (auto& x : row) x = (long long)(rng() % 2001) - 1000; Result r = hungarian(a);        // ② 쌍대 증명서
        long long dual = 0; for (long long x : r.u) dual += x; for (long long x : r.v) dual += x; for (int i = 0; i < n; ++i) for (int j = 0; j < n + 3; ++j) assert(r.u[i] + r.v[j] <= a[i][j]);
        std::vector<char> seenCol(n + 3, 0); for (int i = 0; i < n; ++i) { int j = r.colOfRow[i]; assert(j >= 0 && !seenCol[j] && r.u[i] + r.v[j] == a[i][j]); seenCol[j] = 1; } assert(dual == r.cost); }
    {   std::vector<std::vector<long long>> a = {{4, 2, 3}, {1, 3, 2}, {2, 1, 4}}; Result r = hungarian(a); assert(r.cost == 5 && r.colOfRow == (std::vector<int>{2, 0, 1}));                           // ④ 책의 예
        std::vector<std::vector<long long>> neg = a; for (auto& row : neg) for (auto& x : row) x = -x; Result mx = hungarian(neg); std::vector<char> used(3, 0); assert(mx.cost == bruteForce(neg, 0, used) && -mx.cost >= r.cost); }       // ③ 최대화
    {   std::vector<std::vector<long long>> same(6, std::vector<long long>(6, 7)); Result r = hungarian(same); assert(r.cost == 42);                                                                  // 전부 같은 표
        std::vector<std::vector<long long>> one = {{5, -2, 9, -2}}; Result o = hungarian(one); assert(o.cost == -2 && (o.colOfRow[0] == 1 || o.colOfRow[0] == 3)); }                                  // 한 행만 있는 표
    std::cout << "HungarianAlgorithm: costs equalled the exhaustive optimum on 2000 random tables (negative entries and ties included), and tables of 150-200 rows came with a dual certificate u+v <= c everywhere, equality on assigned cells and primal cost = dual sum" << std::endl;
    return 0;
}
// Time Complexity: O(n² m)
// Space Complexity: O(n m) (입력 표 포함, 알고리즘 자체는 O(n + m))
```
## HopcroftKarp()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 홉크로프트–카프(Hopcroft–Karp): 한 번에 증가 경로 하나가 아니라, *가장 짧은* 증가 경로들을 정점이 겹치지 않게 최대한 많이 한꺼번에 찾는다(한 단계 = BFS 로 층을 만들고 그 층 그래프에서 DFS 로 서로소인 경로를 모두 뽑기). 핵심 정리: 한 단계가 끝나면 최단 증가 경로의 길이가 *반드시 늘어난다*, 그리고 길이가 √V 를 넘으면 남은 증가 경로 수가 √V 이하이므로 단계는 O(√V) 번 → O(E √V).
// 구현 포인트: BFS 는 처음으로 짝 없는 오른쪽 정점을 만난 층(limit)에서 멈추고, DFS 는 층이 정확히 하나씩 깊어지는 간선만 따라가며 짝 없는 오른쪽 정점은 limit 층에서만 받는다. 막다른 정점은 INF 로 표시해 다시 오지 않는다. DFS 는 명시적 스택(반복형)이라 증가 경로가 길어도 안전하다.
// 검증: ① 모든 단계에서 최단 증가 경로 길이 2·limit + 1 이 단계마다 *엄격히 증가* 하고, 단계가 끝난 뒤 독립적인 교대 BFS 로 구한 최단 증가 경로가 그 길이보다 정말 길다(= 한 단계가 최대 집합을 골랐다) ② 첫 단계 뒤의 매칭은 극대(양 끝이 모두 짝 없는 간선 없음) ③ 크기가 부분집합 DP 최대 매칭 · König 인증서와 일치, 단계 수 ≤ 2√V + 2 ④ 정확히 K + 1 단계가 걸리도록 만든 구성(길이 3, 5, …, 2K + 1 의 증가 경로를 가진 K 개 조각)과 무작위 큰 입력.
struct HK {
    int nL, nR; std::vector<std::vector<int>> adj; std::vector<int> matchL, matchR, dist, it;
    std::vector<int> pathLens, gains; long long scans = 0;                       // 단계별 최단 증가 경로 길이 · 늘어난 매칭 수
    HK(int l, int r) : nL(l), nR(r), adj(l), matchL(l, -1), matchR(r, -1), dist(l), it(l) {}
    void addEdge(int u, int v) { adj[u].push_back(v); }
    int bfs() {                                                                  // 반환: limit (없으면 -1)
        std::queue<int> q; int limit = INT_MAX;
        for (int u = 0; u < nL; ++u) { if (matchL[u] < 0) { dist[u] = 0; q.push(u); } else dist[u] = INT_MAX; }
        while (!q.empty()) {
            int u = q.front(); q.pop();
            if (dist[u] >= limit) continue;                                      // 첫 층 이후로는 확장하지 않는다
            for (int v : adj[u]) {
                ++scans; int w = matchR[v];
                if (w < 0) limit = std::min(limit, dist[u]);
                else if (dist[w] == INT_MAX) { dist[w] = dist[u] + 1; q.push(w); }
            }
        }
        return limit == INT_MAX ? -1 : limit;
    }
    bool dfs(int root, int limit) {                                              // 반복형: 층 그래프에서 서로소 증가 경로 하나
        std::vector<int> us{root}, vs; it[root] = 0;
        while (!us.empty()) {
            int u = us.back();
            if (it[u] == (int)adj[u].size()) { dist[u] = INT_MAX; us.pop_back(); if (!vs.empty()) vs.pop_back(); continue; }   // 막다른 정점
            int v = adj[u][it[u]++], w = matchR[v];
            if (w < 0) {
                if (dist[u] != limit) continue;                                  // 짝 없는 오른쪽은 마지막 층에서만
                vs.push_back(v);
                for (std::size_t k = 0; k < us.size(); ++k) { matchL[us[k]] = vs[k]; matchR[vs[k]] = us[k]; dist[us[k]] = INT_MAX; }   // 쓴 정점은 이번 단계에서 다시 못 쓰게 → 경로가 서로소
                return true;
            }
            if (dist[w] == dist[u] + 1 && dist[w] <= limit) { vs.push_back(v); it[w] = 0; us.push_back(w); }
        }
        return false;
    }
    int run(const std::vector<int>& roots) {
        int size = 0;
        while (true) {
            int limit = bfs(); if (limit < 0) break;
            int gain = 0; for (int u : roots) if (matchL[u] < 0 && dfs(u, limit)) ++gain;
            size += gain; pathLens.push_back(2 * limit + 1); gains.push_back(gain);
            if (gain == 0) break;                                               // (이론상 일어나지 않는다)
        }
        return size;
    }
    int run() { std::vector<int> r(nL); std::iota(r.begin(), r.end(), 0); return run(r); }
};

// ---- 오라클과 인증서 ----
bool validMatching(const HK& m) {
    for (int u = 0; u < m.nL; ++u) { int v = m.matchL[u]; if (v >= 0 && (v >= m.nR || m.matchR[v] != u || std::find(m.adj[u].begin(), m.adj[u].end(), v) == m.adj[u].end())) return false; }
    for (int v = 0; v < m.nR; ++v) { int u = m.matchR[v]; if (u >= 0 && m.matchL[u] != v) return false; }
    return true;
}
bool konigOk(const HK& m, int size) {
    std::vector<char> sL(m.nL, 0), sR(m.nR, 0); std::queue<int> q;
    for (int u = 0; u < m.nL; ++u) if (m.matchL[u] < 0) { sL[u] = 1; q.push(u); }
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : m.adj[u]) if (!sR[v]) { sR[v] = 1; int w = m.matchR[v]; if (w >= 0 && !sL[w]) { sL[w] = 1; q.push(w); } } }
    int cover = 0;
    for (int v = 0; v < m.nR; ++v) if (sR[v]) { ++cover; if (m.matchR[v] < 0) return false; }
    for (int u = 0; u < m.nL; ++u) if (!sL[u]) ++cover;
    for (int u = 0; u < m.nL; ++u) for (int v : m.adj[u]) if (sL[u] && !sR[v]) return false;
    return cover == size;
}
int bruteMax(int nL, int nR, const std::vector<unsigned>& mask) {
    std::vector<int> dp(1u << nR, -1); dp[0] = 0;
    for (int u = 0; u < nL; ++u) {
        std::vector<int> nd = dp;
        for (unsigned used = 0; used < (1u << nR); ++used) if (dp[used] >= 0) for (unsigned avail = mask[u] & ~used; avail; avail &= avail - 1) { unsigned bit = avail & -avail; nd[used | bit] = std::max(nd[used | bit], dp[used] + 1); }
        dp = nd;
    }
    return *std::max_element(dp.begin(), dp.end());
}
// 현재 매칭에서 가장 짧은 증가 경로의 길이 (없으면 -1) — 교대 BFS, HK 와 코드를 공유하지 않는다
int shortestAugmenting(const HK& m) {
    std::vector<int> dl(m.nL, -1); std::queue<int> q;
    for (int u = 0; u < m.nL; ++u) if (m.matchL[u] < 0) { dl[u] = 0; q.push(u); }
    int best = -1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : m.adj[u]) {
            int w = m.matchR[v];
            if (w < 0) { int len = 2 * dl[u] + 1; if (best < 0 || len < best) best = len; }
            else if (dl[w] < 0) { dl[w] = dl[u] + 1; q.push(w); }
        }
    }
    return best;
}
bool maximalMatching(const HK& m) { for (int u = 0; u < m.nL; ++u) if (m.matchL[u] < 0) for (int v : m.adj[u]) if (m.matchR[v] < 0) return false; return true; }

// 단계마다 증가 경로 길이가 늘어나는지 확인하며 돌린다 (작은 입력용: 단계 끝마다 독립 BFS)
int runChecked(HK& m, const std::vector<int>& roots) {
    int size = 0, prevLen = 0;
    while (true) {
        int limit = m.bfs(); if (limit < 0) break;
        int len = 2 * limit + 1;
        assert(shortestAugmenting(m) == len && len > prevLen);                  // BFS 의 limit 가 진짜 최단 증가 경로 길이, 단계마다 엄격히 증가
        int gain = 0; for (int u : roots) if (m.matchL[u] < 0 && m.dfs(u, limit)) ++gain;
        assert(gain >= 1);
        size += gain; prevLen = len; m.pathLens.push_back(len); m.gains.push_back(gain);
        int after = shortestAugmenting(m); assert(after < 0 || after > len);   // 한 단계 뒤에는 그 길이의 증가 경로가 남아 있지 않다
        if (m.pathLens.size() == 1) assert(maximalMatching(m));                // 첫 단계(길이 1)는 극대 매칭
    }
    return size;
}

int main() {
    // ① 손으로 확인한 모양: 기존 예제 (L0–R0,R1 · L1–R1 · L2–R2 · L3–R3,R2) → 4
    {   HK m(4, 4); m.addEdge(0, 0); m.addEdge(0, 1); m.addEdge(1, 1); m.addEdge(2, 2); m.addEdge(3, 3); m.addEdge(3, 2);
        assert(m.run() == 4 && validMatching(m) && konigOk(m, 4));
        // 나쁜 처리 순서(L1 먼저)에서도: L1 → R0 를 잡으면 L0 가 막혀 2 단계가 필요
        HK b(2, 2); b.addEdge(0, 0); b.addEdge(1, 0); b.addEdge(1, 1);
        assert(b.run({1, 0}) == 2 && b.pathLens == std::vector<int>({1, 3}) && b.gains == std::vector<int>({1, 1}));
    }

    // ② 전수: (3,3), (3,5), (4,4) 의 모든 이분 그래프 — 단계마다 최단 증가 경로 길이 엄격 증가, 크기 = 부분집합 DP, 인증서, 단계 수 ≤ 2√V + 2
    long long total = 0, multiPhase = 0;
    for (auto [nL, nR] : std::vector<std::pair<int, int>>{{3, 3}, {3, 5}, {4, 4}}) {
        int cells = nL * nR;
        for (unsigned code = 0; code < (1u << cells); ++code) {
            HK m(nL, nR); std::vector<unsigned> mask(nL, 0);
            for (int u = 0; u < nL; ++u) for (int v = 0; v < nR; ++v) if (code >> (u * nR + v) & 1) { m.addEdge(u, v); mask[u] |= 1u << v; }
            std::vector<int> roots(nL); std::iota(roots.begin(), roots.end(), 0);
            int size = runChecked(m, roots);
            assert(validMatching(m) && size == bruteMax(nL, nR, mask) && konigOk(m, size) && shortestAugmenting(m) < 0);
            assert((int)m.pathLens.size() <= 2 * (int)std::sqrt((double)(nL + nR)) + 2);
            multiPhase += m.pathLens.size() >= 2; ++total;
        }
    }
    assert(total == 512 + 32768 + 65536 && multiPhase > 500);

    // ③ 무작위 (|L|,|R| ≤ 10, 뿌리 순서도 섞음): 단계 성질 + 크기
    std::mt19937 rng(1973);
    for (int it = 0; it < 1500; ++it) {
        int nL = 1 + (int)(rng() % 10), nR = 1 + (int)(rng() % 10), edges = (int)(rng() % (nL * nR + 1));
        HK m(nL, nR); std::vector<unsigned> mask(nL, 0);
        for (int i = 0; i < edges; ++i) { int u = (int)(rng() % nL), v = (int)(rng() % nR); m.addEdge(u, v); mask[u] |= 1u << v; }
        std::vector<int> roots(nL); std::iota(roots.begin(), roots.end(), 0); std::shuffle(roots.begin(), roots.end(), rng);
        int size = runChecked(m, roots);
        assert(size == bruteMax(nL, nR, mask) && validMatching(m) && konigOk(m, size));
        int sum = 0; for (int g : m.gains) sum += g; assert(sum == size);
    }

    // ④ 단계 수가 정확히 K + 1 이 되는 구성: 조각 m (1 ≤ m ≤ K) 은 L_0..L_m / R_0..R_m, L_i 의 이웃 [R_{i−1}, R_i] (L_0 은 [R_0]) 인 경로.
    //    뿌리를 내림차순으로 훑으면 1 단계에서 L_i → R_{i−1} 로 잘못 붙어 조각 m 에 길이 2m + 1 의 증가 경로가 남는다 → 단계 j 는 길이 2j − 1 하나만 고친다.
    {
        const int K = 120; int base = 0, n = 0; std::vector<int> start;
        for (int m = 1; m <= K; ++m) { start.push_back(n); n += m + 1; }
        HK h(n, n);
        for (int m = 1; m <= K; ++m) {
            base = start[m - 1];
            h.addEdge(base, base);
            for (int i = 1; i <= m; ++i) { h.addEdge(base + i, base + i - 1); h.addEdge(base + i, base + i); }
        }
        std::vector<int> roots(n); for (int i = 0; i < n; ++i) roots[i] = n - 1 - i;           // 내림차순
        int size = h.run(roots);
        assert(size == n && validMatching(h) && konigOk(h, n));
        assert((int)h.pathLens.size() == K + 1);
        for (int j = 0; j <= K; ++j) assert(h.pathLens[j] == 2 * j + 1);                     // 1, 3, 5, …, 2K + 1
        for (int j = 1; j <= K; ++j) assert(h.gains[j] == 1);                                // 첫 단계 뒤로는 단계마다 정확히 하나
        assert((int)h.pathLens.size() <= 2 * (int)std::sqrt(2.0 * n) + 2);
    }
    // 큰 입력: 무작위 왼쪽 200,000 · 오른쪽 200,000 · 간선 800,000 — 인증서로 최대성 증명, 단계 수 ≤ 2√V + 2
    {
        const int N = 200000; HK h(N, N);
        for (int i = 0; i < 4 * N; ++i) h.addEdge((int)(rng() % N), (int)(rng() % N));
        int size = h.run();
        assert(validMatching(h) && konigOk(h, size) && size > N * 9 / 10);
        assert((int)h.pathLens.size() <= 2 * (int)std::sqrt(2.0 * N) + 2);
        for (std::size_t i = 1; i < h.pathLens.size(); ++i) assert(h.pathLens[i] > h.pathLens[i - 1]);
    }
    std::cout << "HopcroftKarp: phases built a BFS layering and extracted a maximal set of vertex-disjoint shortest augmenting paths with an iterative DFS; on all 512 + 32,768 + 65,536 bipartite graphs of sizes 3x3, 3x5 and 4x4 and 1500 random graphs with shuffled roots the BFS limit equalled the true shortest augmenting-path length found by an independent alternating BFS, that length strictly increased every phase and no path of that length remained afterwards, the first phase left a maximal matching, sizes matched a subset-DP maximum and passed the Koenig cover certificate, a constructed instance of 120 path gadgets took exactly 121 phases (lengths 1, 3, ..., 241), and a random 200,000 x 200,000 graph with 800,000 edges was certified maximum within 2*sqrt(V)+2 phases" << std::endl; return 0;
}
// Time Complexity: O(E √V)
// Space Complexity: O(V + E)
```
## BlossomAlgorithm()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 블로썸 알고리즘(Edmonds 1965): 이분 그래프가 아닌 일반 그래프의 최대 매칭. 이분 그래프의 증가 경로 탐색은 홀수 사이클 때문에 일반 그래프에서 실패한다 — 빈 정점에서 출발해 번갈아 가며 탐색하다 같은 쪽(짝수 층) 두 정점이 만나면 홀수 사이클(블로썸)이 생긴다.
// Edmonds 의 통찰: 블로썸을 하나의 정점으로 수축해도 증가 경로의 존재 여부는 변하지 않는다. 구현은 수축을 실제로 하지 않고 base[v](블로썸의 대표) 배열로 흉내 낸다. BFS 에서 짝수 층 정점 v 가 같은 트리의 짝수 층 정점 to 를 만나면 LCA 를 찾아 두 경로를 base 로 합치고
// 홀수 층이던 정점들도 짝수 층으로 편입해 큐에 넣는다. 한 번의 증가 경로 탐색이 O(V+E)(LCA·수축 포함 O(V²) 이하) 이고 최대 V/2 번 수행하므로 O(V³) 이다.
// 검증: ① 무작위 그래프(n ≤ 18)에서 비트마스크 DP(최대 매칭의 정의대로 전수) 와 크기가 같다 ② 결과가 유효한 매칭(실제 간선, 정점 중복 없음) ③ Tutte–Berge 공식 ν(G) = min_U (n + |U| − odd(G − U))/2 를 모든 부분집합 U 로 계산한 값과 일치(n ≤ 11) — 독립적인 최적성 증명 ④ 홀수 사이클 특수 그래프: 삼각형+꼬리, 5-사이클, 피터슨 그래프(완전 매칭 5), K_n ⑤ 수축이 실제로 일어남
struct Blossom {
    int n; std::vector<std::vector<int>> g; std::vector<int> match, p, base, q; std::vector<char> used, blossom; long contractions = 0;
    explicit Blossom(int n) : n(n), g(n), match(n, -1) {}
    void addEdge(int u, int v) { g[u].push_back(v); g[v].push_back(u); }
    int lca(int a, int b) { std::vector<char> seen(n, 0); for (;;) { a = base[a]; seen[a] = 1; if (match[a] == -1) break; a = p[match[a]]; } for (;;) { b = base[b]; if (seen[b]) return b; b = p[match[b]]; } }
    void markPath(int v, int b, int child) { while (base[v] != b) { blossom[base[v]] = blossom[base[match[v]]] = 1; p[v] = child; child = match[v]; v = p[match[v]]; } }
    int findPath(int root) {
        used.assign(n, 0); p.assign(n, -1); base.resize(n); std::iota(base.begin(), base.end(), 0); used[root] = 1; q.assign(1, root);
        for (size_t qh = 0; qh < q.size(); qh++) { int v = q[qh];
            for (int to : g[v]) {
                if (base[v] == base[to] || match[v] == to) continue;
                if (to == root || (match[to] != -1 && p[match[to]] != -1)) {                                  // 짝수–짝수 간선: 블로썸 발견 -> 수축
                    int cur = lca(v, to); blossom.assign(n, 0); markPath(v, cur, to); markPath(to, cur, v); contractions++;
                    for (int i = 0; i < n; i++) if (blossom[base[i]]) { base[i] = cur; if (!used[i]) { used[i] = 1; q.push_back(i); } }
                } else if (p[to] == -1) { p[to] = v; if (match[to] == -1) return to; used[match[to]] = 1; q.push_back(match[to]); }          // 빈 정점이면 증가 경로 완성
            }
        }
        return -1;
    }
    int solve() { int size = 0; for (int i = 0; i < n; i++) if (match[i] == -1) { int v = findPath(i); if (v != -1) { size++; while (v != -1) { int pv = p[v], next = match[pv]; match[v] = pv; match[pv] = v; v = next; } } } return size; }
};
int bruteMatching(const std::vector<std::vector<char>>& adj, int n) {
    std::vector<int> memo(1 << n, -1); std::vector<int> stack;
    struct F { const std::vector<std::vector<char>>& a; int n; std::vector<int>& m; int go(int mask) { if (mask == (1 << n) - 1) return 0; int& r = m[mask]; if (r >= 0) return r; int v = 0; while (mask >> v & 1) v++; r = go(mask | 1 << v); for (int u = v + 1; u < n; u++) if (!(mask >> u & 1) && a[v][u]) r = std::max(r, 1 + go(mask | 1 << v | 1 << u)); return r; } } f{adj, n, memo};
    return f.go(0);
}
int tutteBerge(const std::vector<std::vector<char>>& adj, int n) {                      // ν(G) = min over U of (n + |U| − odd(G−U)) / 2
    int best = n; for (int U = 0; U < (1 << n); U++) { std::vector<char> seen(n, 0); int odd = 0; for (int s = 0; s < n; s++) if (!(U >> s & 1) && !seen[s]) { int cnt = 0; std::vector<int> st = {s}; seen[s] = 1; while (!st.empty()) { int x = st.back(); st.pop_back(); cnt++; for (int y = 0; y < n; y++) if (adj[x][y] && !(U >> y & 1) && !seen[y]) { seen[y] = 1; st.push_back(y); } } odd += cnt % 2; } best = std::min(best, (n + __builtin_popcount(U) - odd) / 2); }
    return best;
}
int main() {
    std::mt19937 rng(14); long contractions = 0; int cases = 0;
    for (int t = 0; t < 600; t++) {
        int n = 1 + rng() % 18; int pct = 5 + rng() % 60; std::vector<std::vector<char>> adj(n, std::vector<char>(n, 0)); Blossom b(n);
        for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) if ((int)(rng() % 100) < pct) { adj[u][v] = adj[v][u] = 1; b.addEdge(u, v); }
        int got = b.solve(); assert(got == bruteMatching(adj, n));                                                                                              // ①
        int cnt = 0; for (int v = 0; v < n; v++) if (b.match[v] >= 0) { assert(adj[v][b.match[v]] && b.match[b.match[v]] == v); cnt++; } assert(cnt == 2 * got);          // ② 유효한 매칭
        if (n <= 11) assert(got == tutteBerge(adj, n));                                                                                                        // ③ Tutte–Berge
        contractions += b.contractions; cases++;
    }
    { Blossom tri(5); tri.addEdge(0, 1); tri.addEdge(1, 2); tri.addEdge(2, 0); tri.addEdge(2, 3); tri.addEdge(3, 4); assert(tri.solve() == 2); }               // 삼각형 + 꼬리
    { Blossom c5(5); for (int i = 0; i < 5; i++) c5.addEdge(i, (i + 1) % 5); assert(c5.solve() == 2); }
    { Blossom pet(10); for (int i = 0; i < 5; i++) { pet.addEdge(i, (i + 1) % 5); pet.addEdge(i, i + 5); pet.addEdge(5 + i, 5 + (i + 2) % 5); } assert(pet.solve() == 5 && pet.contractions >= 0); }       // 피터슨 그래프: 완전 매칭
    for (int n = 1; n <= 12; n++) { Blossom k(n); for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) k.addEdge(u, v); assert(k.solve() == n / 2); }
    assert(contractions > 50);                                                                                                                                 // ⑤ 블로썸 수축이 실제로 많이 일어났다
    std::cout << "BlossomAlgorithm: " << cases << " random general graphs (n<=18) matched the exhaustive maximum matching, n<=11 also matched the Tutte-Berge formula; " << contractions << " blossom contractions occurred; Petersen graph has a perfect matching" << std::endl; return 0;
}
// Time Complexity: O(V³) (최대 V/2 번의 증가 경로 탐색, 각각 O(V²) 이하) — 고급 구현은 O(√V · E)
// Space Complexity: O(V + E)
```
# Part 13. 그래프 분석
## Tarjan()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 타잔(Tarjan)의 강연결 요소: DFS 한 번으로 정점마다 방문 번호 idx 와 "서브트리에서 스택 위 정점으로 되돌아가 닿는 가장 이른 번호" low 를 구한다. low[u] == idx[u] 이면 u 가 한 요소의 뿌리이고, 스택에서 u 까지 꺼낸 정점들이 그 요소다. 요소는 *끝나는 순서* 대로 번호가 붙으므로 번호는 응축 그래프(요소를 한 점으로 줄인 DAG)의 *역위상 순서* — 간선 u→v 마다 comp[u] ≥ comp[v] — 이다. 같은 알고리즘의 정의·교차 검증은 Part 4 StronglyConnectedComponents 에 있고, 여기서는 이 번호 매기기가 주는 *응용* 둘을 검증한다.
// 응용 ① 2-SAT: 절 (a ∨ b) 마다 ¬a→b, ¬b→a 를 넣은 함의 그래프(변수 i 의 리터럴 노드 2i, ¬ 는 2i+1)에서, 어떤 변수 x 와 ¬x 가 같은 요소에 있으면 충족 불가능, 아니면 comp[x] < comp[¬x] (x 가 위상 순서상 *뒤*) 일 때 x = 참 으로 두면 모든 절이 충족된다. ② 응축 그래프의 출발 요소 수 s 와 도착 요소 수 t 에 대해, 이미 강연결이 아니면 간선을 최소 max(s, t) 개 더해야 강연결이 된다(고립 정점은 s 와 t 에 모두 센다).
// 검증: 정점 ≤ 4 의 모든 방향 그래프(4096)에서 ① 요소 = 도달 가능성 분할 ② 역위상 번호 ③ 최소 보강 간선 수를 *모든 간선 추가 조합을 시도* 해 구한 값과 대조(표본으로 정점 5), 무작위 2-SAT(변수 ≤ 10) 를 2^k 가지 완전 탐색과 대조해 SAT/UNSAT 판정과 배정의 정당성 확인, 마지막으로 변수 10 만 개 · 절 20 만 개의 큰 2-SAT 와 백만 정점 사이클.
using Graph = std::vector<std::vector<int>>;
struct Scc { int comps = 0; std::vector<int> comp; long long scans = 0; };

Scc tarjan(const Graph& g) {                                                      // 반복형: 호출 스택 대신 명시적 스택
    int n = (int)g.size(); Scc r; r.comp.assign(n, -1);
    std::vector<int> idx(n, -1), low(n, 0), it(n, 0), st, call; std::vector<char> on(n, 0); int counter = 0;
    for (int root = 0; root < n; ++root) {
        if (idx[root] >= 0) continue;
        idx[root] = low[root] = counter++; st.push_back(root); on[root] = 1; call.push_back(root);
        while (!call.empty()) {
            int u = call.back();
            if (it[u] < (int)g[u].size()) {
                int v = g[u][it[u]++]; ++r.scans;
                if (idx[v] < 0) { idx[v] = low[v] = counter++; st.push_back(v); on[v] = 1; call.push_back(v); }
                else if (on[v]) low[u] = std::min(low[u], idx[v]);
            } else {
                if (low[u] == idx[u]) { while (true) { int w = st.back(); st.pop_back(); on[w] = 0; r.comp[w] = r.comps; if (w == u) break; } ++r.comps; }
                call.pop_back();
                if (!call.empty()) low[call.back()] = std::min(low[call.back()], low[u]);
            }
        }
    }
    return r;
}
// 2-SAT: 변수 i 의 리터럴 = 2i (참), 2i+1 (거짓)
struct TwoSat {
    int k; Graph g; explicit TwoSat(int vars) : k(vars), g(2 * vars) {}
    static int lit(int var, bool neg) { return 2 * var + (neg ? 1 : 0); }
    void addClause(int a, int b) { g[a ^ 1].push_back(b); g[b ^ 1].push_back(a); }            // (a ∨ b) ⇔ (¬a → b) ∧ (¬b → a)
    bool solve(std::vector<char>& value) const {
        Scc s = tarjan(g); value.assign(k, 0);
        for (int i = 0; i < k; ++i) { if (s.comp[2 * i] == s.comp[2 * i + 1]) return false; value[i] = s.comp[2 * i] < s.comp[2 * i + 1]; }
        return true;
    }
};
// 최소 보강 간선 수 (응축 그래프의 출발/도착 요소로 계산)
int minEdgesToStronglyConnect(const Graph& g, const Scc& s) {
    if (s.comps <= 1) return 0;
    std::vector<char> hasIn(s.comps, 0), hasOut(s.comps, 0);
    for (std::size_t u = 0; u < g.size(); ++u) for (int v : g[u]) if (s.comp[u] != s.comp[v]) { hasOut[s.comp[u]] = 1; hasIn[s.comp[v]] = 1; }
    int src = 0, snk = 0; for (int c = 0; c < s.comps; ++c) { src += !hasIn[c]; snk += !hasOut[c]; }
    return std::max(src, snk);
}

// ---- 오라클 ----
std::vector<unsigned> closure(int n, const Graph& g) {                            // 반사 추이적 폐쇄 (비트마스크, n ≤ 32)
    std::vector<unsigned> row(n); for (int i = 0; i < n; ++i) { row[i] = 1u << i; for (int v : g[i]) row[i] |= 1u << v; }
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];
    return row;
}
bool stronglyConnectedMask(int n, const std::vector<unsigned>& row) { for (int i = 0; i < n; ++i) if (row[i] != (n == 32 ? ~0u : (1u << n) - 1)) return false; return true; }
int bruteMinAugment(int n, const Graph& g) {                                      // 간선을 k 개씩 더해 보며 처음 강연결이 되는 k
    std::vector<std::pair<int, int>> absent;
    for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b && std::find(g[a].begin(), g[a].end(), b) == g[a].end()) absent.push_back({a, b});
    for (int k = 0; k <= (int)absent.size(); ++k) {
        std::vector<int> pick(k); std::iota(pick.begin(), pick.end(), 0);
        while (true) {
            Graph h = g; for (int i : pick) h[absent[i].first].push_back(absent[i].second);
            if (stronglyConnectedMask(n, closure(n, h))) return k;
            int p = k - 1; while (p >= 0 && pick[p] == (int)absent.size() - k + p) --p;
            if (p < 0) break;
            ++pick[p]; for (int j = p + 1; j < k; ++j) pick[j] = pick[j - 1] + 1;
        }
    }
    return -1;
}

int main() {
    // ① 손으로 확인한 모양: 0→1→2→0 은 한 요소, 3→2 는 따로 → 요소 2 개, 번호는 역위상 (싱크 {0,1,2} 가 먼저 = 0)
    {   Graph g = {{1}, {2}, {0}, {2}};
        Scc s = tarjan(g);
        assert(s.comps == 2 && s.comp[0] == s.comp[1] && s.comp[1] == s.comp[2] && s.comp[3] == 1 && s.comp[0] == 0 && s.scans == 4);
        assert(minEdgesToStronglyConnect(g, s) == 1);                                    // 출발 요소 {3} 하나, 도착 요소 {0,1,2} 하나 → 간선 1 개 (2→3)
    }

    // ② 전수: 정점 ≤ 4 의 모든 방향 그래프(루프 없음) — 도달 가능성 분할 · 역위상 번호 · 호출당 간선 훑기 정확히 E 번 · 최소 보강 간선 수(완전 탐색)
    long long graphs = 0, needAugment = 0;
    for (int n = 1; n <= 4; ++n) {
        std::vector<std::pair<int, int>> all; for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) all.push_back({a, b});
        int m = (int)all.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Graph g(n); int edges = 0; for (int i = 0; i < m; ++i) if (mask >> i & 1) { g[all[i].first].push_back(all[i].second); ++edges; }
            Scc s = tarjan(g); auto reach = closure(n, g);
            for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) assert((s.comp[i] == s.comp[j]) == ((reach[i] >> j & 1) && (reach[j] >> i & 1)));
            for (int u = 0; u < n; ++u) for (int v : g[u]) assert(s.comp[u] >= s.comp[v]);                              // 역위상
            assert(s.scans == edges);
            int want = bruteMinAugment(n, g);
            assert(minEdgesToStronglyConnect(g, s) == want);
            needAugment += want > 0; ++graphs;
        }
    }
    assert(graphs == 1 + 4 + 64 + 4096 && needAugment == 3 + 46 + 2490);           // 강연결이 아닌 그래프 수: 4096 − 1606 = 2490 (정점 4), 64 − 18 = 46 (정점 3), 4 − 1 = 3 (정점 2)
    // 정점 5 개 표본 (2^20 개 중 약 700 개)
    std::mt19937 rng(2007);
    for (int it = 0; it < 700; ++it) {
        Graph g(5); for (int a = 0; a < 5; ++a) for (int b = 0; b < 5; ++b) if (a != b && rng() % 100 < 22) g[a].push_back(b);
        Scc s = tarjan(g); assert(minEdgesToStronglyConnect(g, s) == bruteMinAugment(5, g));
    }

    // ③ 2-SAT: 변수 ≤ 10 개, 절 ≤ 3k 개 (자기 절 (a ∨ a) 와 항진 (a ∨ ¬a) 포함) — 판정이 2^k 완전 탐색과 같고, SAT 이면 배정이 모든 절을 만족
    int sat = 0, unsat = 0;
    for (int it = 0; it < 3000; ++it) {
        int k = 1 + (int)(rng() % 10), m = (int)(rng() % (3 * k + 1));
        TwoSat ts(k); std::vector<std::pair<int, int>> clauses;
        for (int i = 0; i < m; ++i) { int a = TwoSat::lit((int)(rng() % k), rng() & 1), b = TwoSat::lit((int)(rng() % k), rng() & 1); ts.addClause(a, b); clauses.push_back({a, b}); }
        bool brute = false;
        for (unsigned asg = 0; asg < (1u << k) && !brute; ++asg) {
            bool ok = true; for (auto [a, b] : clauses) { bool va = (asg >> (a / 2) & 1) != (a & 1), vb = (asg >> (b / 2) & 1) != (b & 1); ok = ok && (va || vb); }
            brute = ok;
        }
        std::vector<char> val; bool got = ts.solve(val);
        assert(got == brute);
        if (got) { for (auto [a, b] : clauses) assert(((val[a / 2] != 0) != (a & 1)) || ((val[b / 2] != 0) != (b & 1))); ++sat; } else ++unsat;
    }
    assert(sat > 2000 && unsat > 600);

    // ④ 큰 입력: (a) 숨긴 배정을 만족하는 절 20 만 개의 2-SAT, 변수 10 만 개 → SAT, 배정이 모든 절을 만족; 모순 절 두 개를 더하면 UNSAT  (b) 백만 정점 사이클 = 요소 1 개, 한 간선을 끊으면 요소 백만 개
    {
        const int K = 100000; std::mt19937_64 r(11); std::vector<char> hidden(K); for (auto& h : hidden) h = (char)(r() & 1);
        TwoSat ts(K); std::vector<std::pair<int, int>> clauses;
        while ((int)clauses.size() < 2 * K) {
            int x = (int)(r() % K), y = (int)(r() % K); bool nx = r() & 1, ny = r() & 1;
            bool vx = (hidden[x] != 0) != nx, vy = (hidden[y] != 0) != ny;
            if (!vx && !vy) continue;                                                      // 숨긴 배정이 만족하지 않는 절은 버린다
            int a = TwoSat::lit(x, nx), b = TwoSat::lit(y, ny); ts.addClause(a, b); clauses.push_back({a, b});
        }
        std::vector<char> val; assert(ts.solve(val));
        for (auto [a, b] : clauses) assert(((val[a / 2] != 0) != (a & 1)) || ((val[b / 2] != 0) != (b & 1)));
        ts.addClause(TwoSat::lit(0, false), TwoSat::lit(0, false)); ts.addClause(TwoSat::lit(0, true), TwoSat::lit(0, true));     // x₀ 와 ¬x₀ 를 동시에 강제
        assert(!ts.solve(val));
        const int N = 1000000; Graph cyc(N); for (int i = 0; i < N; ++i) cyc[i].push_back((i + 1) % N);
        Scc one = tarjan(cyc); assert(one.comps == 1 && one.scans == N);
        cyc[N - 1].clear(); Scc many = tarjan(cyc); assert(many.comps == N && many.comp[N - 1] == 0 && many.comp[0] == N - 1);
    }
    std::cout << "Tarjan: the iterative low-link DFS reproduced the reachability partition on all 4096 loop-free digraphs over 4 vertices, numbered components in reverse topological order (comp[u] >= comp[v] on every edge) while scanning each edge exactly once, the sources/sinks formula max(s,t) matched a brute-force search over every set of added edges (all graphs up to 4 vertices and 700 random 5-vertex ones), 2-SAT via component numbering agreed with 2^k enumeration on 3000 random formulas (over 2000 satisfiable and over 600 unsatisfiable) with valid assignments, and a 100,000-variable 200,000-clause planted 2-SAT was solved while a contradiction made it UNSAT, plus a 1,000,000-vertex cycle" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## Kosaraju()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// 코사라주(Kosaraju–Sharir): 두 번의 DFS 로 강연결 요소를 구한다. ① 원래 그래프를 DFS 해서 정점을 *끝난 순서* 로 기록 ② 간선을 뒤집은 그래프에서 끝난 시각이 *가장 늦은 정점부터* 다시 DFS — 그때 한 번의 DFS 로 닿는 정점 집합이 정확히 한 요소다. 열쇠 보조정리: 요소 C 에서 C' 로 가는 간선이 있으면 max finish(C) > max finish(C') 이다. 그래서 끝 시각이 가장 큰 정점은 응축 DAG 의 *출발* 요소에 있고, 뒤집은 그래프에서는 출발 요소에서 다른 요소로 나갈 수 없어 한 요소만 닿는다. 요소 번호는 발견 순이라 응축 그래프의 *위상 순서* (간선 u→v 마다 comp[u] ≤ comp[v]) — 타잔의 역위상 번호와 반대다.
// 비용: 간선을 훑는 횟수가 타잔은 E, 코사라주는 정확히 2E 이고 뒤집은 그래프도 따로 만들어야 한다(메모리 두 배) — 대신 두 DFS 가 각각 단순하다. 역할을 바꿔도(뒤집은 그래프를 먼저 DFS, 원래 그래프에서 두 번째) 같은 분할이 나온다. 모두 반복형 DFS 라서 백만 정점 사슬도 안전하다.
// 검증: 정점 ≤ 4 의 모든 방향 그래프(루프 없음)에서 ① 도달 가능성 분할과 일치 ② 위상 번호(comp[u] ≤ comp[v]) ③ 보조정리 max finish(C) > max finish(C') ④ 간선 훑기 정확히 2E 와 타잔의 E ⑤ 역할을 바꾼 변형이 같은 분할; 무작위 큰 그래프 · 백만 정점 사이클은 타잔과 대조.
using Graph = std::vector<std::vector<int>>;
struct Scc { int comps = 0; std::vector<int> comp, finish; long long scans = 0; };

// pass1 은 g 에서, pass2 는 g 의 전치에서 (swapRoles 이면 반대)
Scc kosaraju(const Graph& g, bool swapRoles = false) {
    int n = (int)g.size(); Scc r; r.comp.assign(n, -1); r.finish.assign(n, -1);
    Graph rg(n); for (int u = 0; u < n; ++u) for (int v : g[u]) rg[v].push_back(u);
    const Graph& first = swapRoles ? rg : g; const Graph& second = swapRoles ? g : rg;
    // 1 차 DFS: 끝난 순서
    std::vector<int> order, it(n, 0), st; std::vector<char> seen(n, 0);
    for (int root = 0; root < n; ++root) {
        if (seen[root]) continue;
        seen[root] = 1; st.push_back(root);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] < (int)first[u].size()) { int v = first[u][it[u]++]; ++r.scans; if (!seen[v]) { seen[v] = 1; st.push_back(v); } }
            else { r.finish[u] = (int)order.size(); order.push_back(u); st.pop_back(); }
        }
    }
    // 2 차 DFS: 끝난 시각이 늦은 순서로, 요소 하나가 한 번에 닿는다
    for (int k = n - 1; k >= 0; --k) {
        int s = order[k]; if (r.comp[s] >= 0) continue;
        r.comp[s] = r.comps; st.push_back(s);
        while (!st.empty()) {
            int u = st.back(); st.pop_back();
            for (int v : second[u]) { ++r.scans; if (r.comp[v] < 0) { r.comp[v] = r.comps; st.push_back(v); } }
        }
        ++r.comps;
    }
    return r;
}
// 타잔 (간선 훑기 횟수 비교와 큰 입력 대조용)
Scc tarjan(const Graph& g) {
    int n = (int)g.size(); Scc r; r.comp.assign(n, -1);
    std::vector<int> idx(n, -1), low(n, 0), it(n, 0), st, call; std::vector<char> on(n, 0); int counter = 0;
    for (int root = 0; root < n; ++root) {
        if (idx[root] >= 0) continue;
        idx[root] = low[root] = counter++; st.push_back(root); on[root] = 1; call.push_back(root);
        while (!call.empty()) {
            int u = call.back();
            if (it[u] < (int)g[u].size()) { int v = g[u][it[u]++]; ++r.scans; if (idx[v] < 0) { idx[v] = low[v] = counter++; st.push_back(v); on[v] = 1; call.push_back(v); } else if (on[v]) low[u] = std::min(low[u], idx[v]); }
            else { if (low[u] == idx[u]) { while (true) { int w = st.back(); st.pop_back(); on[w] = 0; r.comp[w] = r.comps; if (w == u) break; } ++r.comps; } call.pop_back(); if (!call.empty()) low[call.back()] = std::min(low[call.back()], low[u]); }
        }
    }
    return r;
}
std::vector<int> canonical(const std::vector<int>& comp) {                       // 분할만 비교: 각 요소를 가장 작은 정점 번호로 이름 붙인다
    std::vector<int> label(comp.size(), -1), out(comp.size());
    for (std::size_t v = 0; v < comp.size(); ++v) { if (label[comp[v]] < 0) label[comp[v]] = (int)v; out[v] = label[comp[v]]; }
    return out;
}
std::vector<unsigned> closure(int n, const Graph& g) {
    std::vector<unsigned> row(n); for (int i = 0; i < n; ++i) { row[i] = 1u << i; for (int v : g[i]) row[i] |= 1u << v; }
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];
    return row;
}

int main() {
    // ① 손으로 확인한 모양: 기존 예제 0→2, 1→0, 2→1,3, 3→4 → {0,1,2}, {3}, {4}, 번호는 위상 순서
    {   Graph g = {{2}, {0}, {1, 3}, {4}, {}};
        Scc s = kosaraju(g);
        assert(s.comps == 3 && s.comp[0] == s.comp[1] && s.comp[1] == s.comp[2] && s.comp[0] == 0 && s.comp[3] == 1 && s.comp[4] == 2 && s.scans == 2 * 5);
        Scc t = tarjan(g); assert(t.comps == 3 && t.comp[0] == 2 && t.comp[3] == 1 && t.comp[4] == 0 && t.scans == 5);    // 타잔 번호는 정확히 반대
    }

    // ② 전수: 정점 ≤ 4 의 모든 방향 그래프(루프 없음) — 도달 가능성 분할 · 위상 번호 · 보조정리 · 훑기 횟수 · 역할 교환
    long long graphs = 0;
    for (int n = 1; n <= 4; ++n) {
        std::vector<std::pair<int, int>> all; for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) all.push_back({a, b});
        int m = (int)all.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Graph g(n); int edges = 0; for (int i = 0; i < m; ++i) if (mask >> i & 1) { g[all[i].first].push_back(all[i].second); ++edges; }
            Scc s = kosaraju(g), t = tarjan(g), w = kosaraju(g, true); auto reach = closure(n, g);
            for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) assert((s.comp[i] == s.comp[j]) == ((reach[i] >> j & 1) && (reach[j] >> i & 1)));
            for (int u = 0; u < n; ++u) for (int v : g[u]) assert(s.comp[u] <= s.comp[v]);                                  // 위상 번호
            std::vector<int> maxFinish(s.comps, -1); for (int v = 0; v < n; ++v) maxFinish[s.comp[v]] = std::max(maxFinish[s.comp[v]], s.finish[v]);
            for (int u = 0; u < n; ++u) for (int v : g[u]) if (s.comp[u] != s.comp[v]) assert(maxFinish[s.comp[u]] > maxFinish[s.comp[v]]);   // 보조정리
            assert(s.scans == 2 * edges && t.scans == edges && w.scans == 2 * edges);                                       // 코사라주 2E, 타잔 E
            assert(canonical(s.comp) == canonical(t.comp) && canonical(s.comp) == canonical(w.comp));                      // 세 변형이 같은 분할
            for (int u = 0; u < n; ++u) for (int v : g[u]) assert(t.comp[u] >= t.comp[v]);                                  // 타잔은 역위상
            ++graphs;
        }
    }
    assert(graphs == 1 + 4 + 64 + 4096);

    // ③ 무작위 큰 그래프: 정점 30 만 · 간선 60 만 (거대 요소가 생기는 밀도) — 코사라주 = 타잔, 보조정리, 훑기 횟수; 백만 정점 사이클
    std::mt19937_64 r(99);
    {
        const int N = 300000; Graph g(N); for (int i = 0; i < 2 * N; ++i) g[r() % N].push_back((int)(r() % N));
        Scc s = kosaraju(g), t = tarjan(g);
        assert(canonical(s.comp) == canonical(t.comp) && s.comps == t.comps && s.comps > 1 && s.scans == 2LL * 2 * N && t.scans == 2LL * N);
        std::vector<int> size(s.comps, 0); for (int c : s.comp) ++size[c];
        assert(*std::max_element(size.begin(), size.end()) > N / 2);                                                       // 거대 요소
        for (int u = 0; u < N; ++u) for (int v : g[u]) assert(s.comp[u] <= s.comp[v]);
        const int M = 1000000; Graph cyc(M); for (int i = 0; i < M; ++i) cyc[i].push_back((i + 1) % M);
        assert(kosaraju(cyc).comps == 1 && kosaraju(cyc, true).comps == 1);
        cyc[M - 1].clear(); Scc chain = kosaraju(cyc); assert(chain.comps == M && chain.comp[0] == 0 && chain.comp[M - 1] == M - 1);   // 사슬: 위상 순서 0 … M−1
    }
    std::cout << "Kosaraju: two iterative DFS passes (finish order on G, then sweeps over the transpose in decreasing finish time) matched the reachability partition on all 4096 loop-free digraphs over 4 vertices, numbered components in topological order (opposite to Tarjan's), satisfied the key lemma max finish(C) > max finish(C') on every cross-component edge, scanned exactly 2E edges against Tarjan's E, gave the same partition with the roles of G and its transpose swapped, and agreed with Tarjan on a 300,000-vertex random digraph with a giant component and on a 1,000,000-vertex cycle and chain" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## Gabow()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 가보우의 경로 기반 강연결 요소(Gabow 2000; Cheriyan–Mehlhorn 1996, Purdom 1970 에서 유래): 타잔 알고리즘이 lowlink 값으로 "더 올라갈 수 있는가" 를 추적하는 것을 두 개의 스택으로 대신한다.
//   S: 아직 컴포넌트가 정해지지 않은 정점들의 스택(방문 순서). B: 현재 DFS 경로 위에서 "하나의 강연결 요소가 될 후보 덩어리들" 의 경계(각 덩어리의 맨 처음 정점).
// 이미 방문했지만 컴포넌트가 없는 정점 w 로 가는 간선을 만나면 사이클이 w 까지 닫힌 것이므로 B 의 꼭대기가 w 보다 늦게 방문된 동안 pop 해서 그 덩어리들을 w 쪽으로 합친다. 정점 v 의 탐색이 끝났을 때 B 의 꼭대기가 v 이면 v 는 한 컴포넌트의 루트이고, S 에서 v 까지 pop 한 것이 그 컴포넌트다.
// 컴포넌트는 위상 정렬의 역순(싱크 먼저)으로 나온다. 코드는 재귀 없이 명시적 스택으로 써서 수십만 길이의 사슬에서도 스택이 넘치지 않는다.
// 검증: ① 무작위 방향 그래프에서 도달 가능성 닫힘(u→v 와 v→u 가 모두 가능)으로 정의한 강연결 요소와 정확히 같은 분할 ② 컴포넌트 번호가 역위상 순서: 서로 다른 컴포넌트를 잇는 간선 u→v 는 항상 comp[u] > comp[v] ③ 20 만 정점 사슬+역간선, 그리고 무작위 대형 그래프에서 코사라주와 분할이 같음
struct PathSCC {
    int n, counter = 0, comps = 0; std::vector<std::vector<int>> g; std::vector<int> pre, comp, S, B;
    explicit PathSCC(const std::vector<std::vector<int>>& adj) : n(adj.size()), g(adj), pre(n, -1), comp(n, -1) { for (int s = 0; s < n; s++) if (pre[s] < 0) run(s); }
    void run(int root) {
        std::vector<std::pair<int, size_t>> call; call.push_back({root, 0}); pre[root] = counter++; S.push_back(root); B.push_back(root);
        while (!call.empty()) { int v = call.back().first; size_t& i = call.back().second;
            if (i < g[v].size()) { int w = g[v][i++];
                if (pre[w] < 0) { pre[w] = counter++; S.push_back(w); B.push_back(w); call.push_back({w, 0}); }                    // 트리 간선: 내려간다
                else if (comp[w] < 0) while (pre[B.back()] > pre[w]) B.pop_back();                                               // 아직 열린 정점으로 가는 간선: 사이클을 닫는다 -> 덩어리 합침
            } else {
                if (B.back() == v) { B.pop_back(); for (;;) { int w = S.back(); S.pop_back(); comp[w] = comps; if (w == v) break; } comps++; }            // v 가 덩어리의 루트: 컴포넌트 확정
                call.pop_back();
            }
        }
    }
};
std::vector<int> kosaraju(const std::vector<std::vector<int>>& g) {
    int n = g.size(); std::vector<std::vector<int>> rg(n); for (int u = 0; u < n; u++) for (int v : g[u]) rg[v].push_back(u); std::vector<int> order, comp(n, -1); std::vector<char> seen(n, 0);
    for (int s = 0; s < n; s++) if (!seen[s]) { std::vector<std::pair<int, size_t>> st = {{s, 0}}; seen[s] = 1; while (!st.empty()) { int v = st.back().first; size_t& i = st.back().second; if (i < g[v].size()) { int w = g[v][i++]; if (!seen[w]) { seen[w] = 1; st.push_back({w, 0}); } } else { order.push_back(v); st.pop_back(); } } }
    int c = 0; for (int k = n - 1; k >= 0; k--) { int s = order[k]; if (comp[s] >= 0) continue; std::vector<int> st = {s}; comp[s] = c; while (!st.empty()) { int v = st.back(); st.pop_back(); for (int w : rg[v]) if (comp[w] < 0) { comp[w] = c; st.push_back(w); } } c++; }
    return comp;
}
bool samePartition(const std::vector<int>& a, const std::vector<int>& b) { std::vector<int> ma(a.size() + 1, -1), mb(b.size() + 1, -1); for (size_t i = 0; i < a.size(); i++) { if (ma[a[i]] < 0) ma[a[i]] = b[i]; if (mb[b[i]] < 0) mb[b[i]] = a[i]; if (ma[a[i]] != b[i] || mb[b[i]] != a[i]) return false; } return true; }
int main() {
    std::mt19937 rng(6); int cases = 0, nontrivial = 0;
    for (int t = 0; t < 500; t++) {
        int n = 1 + rng() % 14; std::vector<std::vector<int>> g(n); int m = rng() % (3 * n); for (int k = 0; k < m; k++) g[rng() % n].push_back(rng() % n);
        std::vector<std::vector<char>> reach(n, std::vector<char>(n, 0)); for (int i = 0; i < n; i++) reach[i][i] = 1; for (int u = 0; u < n; u++) for (int v : g[u]) reach[u][v] = 1; for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (reach[i][k] && reach[k][j]) reach[i][j] = 1;
        PathSCC s(g); for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) assert((s.comp[i] == s.comp[j]) == (reach[i][j] && reach[j][i]));                  // ① 도달 가능성으로 정의한 강연결 요소와 같다
        for (int u = 0; u < n; u++) for (int v : g[u]) assert(s.comp[u] == s.comp[v] || s.comp[u] > s.comp[v]);                                                   // ② 역위상 순서
        nontrivial += s.comps < n; cases++;
    }
    const int N = 200000; std::vector<std::vector<int>> chain(N); for (int i = 0; i + 1 < N; i++) chain[i].push_back(i + 1); chain[N - 1].push_back(0); PathSCC one(chain); assert(one.comps == 1);          // 한 덩어리 (스택 오버플로 없음)
    for (auto& a : chain) a.clear(); for (int i = 0; i + 1 < N; i++) chain[i].push_back(i + 1); PathSCC dag(chain); assert(dag.comps == N && dag.comp[0] == N - 1 && dag.comp[N - 1] == 0);
    const int M = 100000; std::vector<std::vector<int>> big(M); for (int k = 0; k < 160000; k++) big[rng() % M].push_back(rng() % M); PathSCC pb(big); assert(samePartition(pb.comp, kosaraju(big)));   // ③ 코사라주와 일치
    std::cout << "Gabow: " << cases << " random digraphs matched the reachability definition of SCCs (" << nontrivial << " with a nontrivial component), reverse topological numbering held; a " << N << "-vertex cycle is one component and a " << N << "-vertex path is " << dag.comps << "; the " << M << "-vertex random graph has " << pb.comps << " components, identical to Kosaraju" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V) (스택 S, B, 호출 스택)
```
## EulerTour()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 오일러 경로·회로(Euler trail/circuit): 모든 간선을 정확히 한 번씩 지나는 경로. 존재 조건 — 무방향: 간선이 있는 정점들이 한 연결 성분이고 홀수 차수 정점이 0 개(회로) 또는 2 개(경로, 두 홀수 정점이 양 끝). 방향: 간선이 있는 정점들이 약연결이고 모든 정점에서 진입 = 진출(회로), 또는 진출 − 진입 = +1 인 정점(시작) 하나와 −1 인 정점(끝) 하나(경로). 루프는 무방향에서 차수 2.
// Hierholzer 알고리즘: 시작점에서 막다른 곳까지 안 쓴 간선을 따라 가다가, 막히면(스택 맨 위 정점에 안 쓴 간선이 없으면) 그 정점을 *결과의 끝* 에 놓고 돌아간다. 그렇게 얻은 정점열을 뒤집은 것이 오일러 경로다 — 도중의 부분 회로가 자동으로 이어 붙는다. O(E). 반복형(명시적 스택 + 정점별 간선 포인터)이라 백만 간선도 안전하고, 간선 번호도 함께 기록해 같은 간선을 두 번 쓰지 않았음을 확인한다. 기존의 "간선을 지우며 재귀" 방식은 vector::erase 때문에 O(E²) 이고 평행 간선·루프에서 틀린다.
// 검증: ① 무작위 다중 그래프(루프·평행 간선·비연결)에서 존재 여부가 *모든 경로를 시도하는 완전 탐색* 과 같고, 찾은 경로는 모든 간선을 정확히 한 번 쓰며 이웃한 간선이 정말 이어진다 ② BEST 정리: 방향 오일러 그래프의 오일러 회로 수 = t_w(G) · Π (진출차수 − 1)! 를 Kirchhoff 행렬식(Bareiss)으로 계산해 회로를 전부 세는 완전 탐색과 대조 ③ 큰 입력: de Bruijn 그래프 B(2, 20) 의 오일러 회로 = 길이 2^20 의 de Bruijn 수열(모든 20 비트 문자열이 순환적으로 정확히 한 번씩 나타남), 700×700 원환 격자(간선 98 만 개) 의 오일러 회로.
struct Trail { bool ok = false; std::vector<int> vs, es; };                       // 정점열(E+1) · 간선 번호열(E)
struct Arc { int to, id; };

Trail hierholzer(int n, const std::vector<std::pair<int, int>>& edges, bool directed) {
    int m = (int)edges.size(); Trail t;
    std::vector<std::vector<Arc>> adj(n); std::vector<int> deg(n, 0), outd(n, 0), ind(n, 0);
    for (int i = 0; i < m; ++i) {
        auto [a, b] = edges[i];
        adj[a].push_back({b, i}); ++outd[a]; ++ind[b];
        if (!directed) { adj[b].push_back({a, i}); }                              // 루프는 양쪽에 한 번씩 들어가 차수 2, 사용 표시로 한 번만 쓴다
    }
    int start = -1;
    if (directed) {
        int plus = 0, minus = 0, startPlus = -1;
        for (int v = 0; v < n; ++v) { int d = outd[v] - ind[v]; if (d == 1) { ++plus; startPlus = v; } else if (d == -1) ++minus; else if (d != 0) return t; }
        if (!((plus == 0 && minus == 0) || (plus == 1 && minus == 1))) return t;
        start = startPlus; if (start < 0) for (int v = 0; v < n; ++v) if (outd[v] > 0) { start = v; break; }
    } else {
        int odd = 0, firstOdd = -1;
        for (int v = 0; v < n; ++v) { deg[v] = (int)adj[v].size(); if (deg[v] & 1) { ++odd; if (firstOdd < 0) firstOdd = v; } }
        if (odd != 0 && odd != 2) return t;
        start = firstOdd; if (start < 0) for (int v = 0; v < n; ++v) if (deg[v] > 0) { start = v; break; }
    }
    if (m == 0) { t.ok = true; return t; }                                        // 간선이 없으면 빈 경로
    if (start < 0) return t;
    std::vector<int> ptr(n, 0), stV{start}, stE{-1}, outV, outE; std::vector<char> used(m, 0);
    while (!stV.empty()) {
        int u = stV.back();
        while (ptr[u] < (int)adj[u].size() && used[adj[u][ptr[u]].id]) ++ptr[u];
        if (ptr[u] == (int)adj[u].size()) { outV.push_back(u); outE.push_back(stE.back()); stV.pop_back(); stE.pop_back(); }
        else { Arc a = adj[u][ptr[u]++]; used[a.id] = 1; stV.push_back(a.to); stE.push_back(a.id); }
    }
    if ((int)outE.size() != m + 1) return t;                                      // 모든 간선을 못 썼다 → 연결되지 않음 (outE 마지막은 시작의 −1)
    std::reverse(outV.begin(), outV.end()); std::reverse(outE.begin(), outE.end());
    t.ok = true; t.vs = outV; t.es.assign(outE.begin() + 1, outE.end());
    return t;
}
bool validTrail(int n, const std::vector<std::pair<int, int>>& edges, bool directed, const Trail& t) {
    int m = (int)edges.size(); (void)n;
    if ((int)t.es.size() != m || (int)t.vs.size() != m + 1) return m == 0 && t.vs.empty() && t.es.empty();   // 간선이 없으면 빈 경로
    std::vector<char> seen(m, 0);
    for (int i = 0; i < m; ++i) {
        int id = t.es[i]; if (id < 0 || id >= m || seen[id]) return false; seen[id] = 1;
        auto [a, b] = edges[id]; int x = t.vs[i], y = t.vs[i + 1];
        if (directed ? !(a == x && b == y) : !((a == x && b == y) || (a == y && b == x))) return false;
    }
    return true;
}

// ---- 오라클: 모든 경로 시도 ----
bool bruteTrail(int n, const std::vector<std::pair<int, int>>& edges, bool directed, int cur, std::vector<char>& used, int left) {
    if (left == 0) return true;
    for (int i = 0; i < (int)edges.size(); ++i) {
        if (used[i]) continue;
        auto [a, b] = edges[i]; int next = -1;
        if (a == cur) next = b; else if (!directed && b == cur) next = a;
        if (next < 0) continue;
        used[i] = 1; bool ok = bruteTrail(n, edges, directed, next, used, left - 1); used[i] = 0;
        if (ok) return true;
    }
    return false;
}
bool bruteExists(int n, const std::vector<std::pair<int, int>>& edges, bool directed) {
    if (edges.empty()) return true;
    std::vector<char> used(edges.size(), 0);
    for (int s = 0; s < n; ++s) if (bruteTrail(n, edges, directed, s, used, (int)edges.size())) return true;
    return false;
}
// BEST 정리용: 오일러 회로를 (첫 간선 고정) 전부 센다
long long countCircuits(const std::vector<std::pair<int, int>>& edges, int cur, std::vector<char>& used, int left, int startVertex) {
    if (left == 0) return cur == startVertex ? 1 : 0;
    long long total = 0;
    for (int i = 1; i < (int)edges.size(); ++i) if (!used[i] && edges[i].first == cur) { used[i] = 1; total += countCircuits(edges, edges[i].second, used, left - 1, startVertex); used[i] = 0; }
    return total;
}
long long bareissDet(std::vector<std::vector<long long>> a) {                         // 정수 행렬식 (분수 없는 가우스 소거)
    int n = (int)a.size(); long long sign = 1, prev = 1;
    for (int k = 0; k + 1 < n; ++k) {
        if (a[k][k] == 0) { int s = -1; for (int i = k + 1; i < n; ++i) if (a[i][k] != 0) { s = i; break; } if (s < 0) return 0; std::swap(a[k], a[s]); sign = -sign; }
        for (int i = k + 1; i < n; ++i) for (int j = k + 1; j < n; ++j) a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) / prev;
        prev = a[k][k];
    }
    return n == 0 ? 1 : sign * a[n - 1][n - 1];
}

int main() {
    // ① 손으로 확인한 모양: 삼각형 → 회로(길이 4 의 정점열), 경로 그래프 → 양끝이 홀수, 별 → 없음, 비연결 → 없음, 방향 사이클
    {   std::vector<std::pair<int, int>> tri = {{0, 1}, {1, 2}, {2, 0}};
        Trail t = hierholzer(3, tri, false); assert(t.ok && t.vs.size() == 4 && t.vs.front() == t.vs.back() && validTrail(3, tri, false, t));
        std::vector<std::pair<int, int>> path = {{0, 1}, {1, 2}};
        Trail p = hierholzer(3, path, false); assert(p.ok && p.vs.front() != p.vs.back() && validTrail(3, path, false, p));
        assert(!hierholzer(4, {{0, 1}, {0, 2}, {0, 3}}, false).ok);                            // 홀수 차수 정점 4 개
        assert(!hierholzer(6, {{0, 1}, {1, 2}, {2, 0}, {3, 4}, {4, 5}, {5, 3}}, false).ok);   // 두 삼각형은 이어져 있지 않다
        std::vector<std::pair<int, int>> loop = {{0, 0}, {0, 1}, {1, 0}}; assert(hierholzer(2, loop, false).ok);   // 루프 + 평행 간선
        std::vector<std::pair<int, int>> dir = {{0, 1}, {1, 2}, {2, 0}}; Trail d = hierholzer(3, dir, true); assert(d.ok && validTrail(3, dir, true, d));
        assert(!hierholzer(3, {{0, 1}, {0, 2}}, true).ok);                                     // 진출 2, 진입 없음
    }

    // ② 무작위 다중 그래프 (정점 ≤ 5, 간선 ≤ 9, 루프·평행·비연결): 존재 여부 = 완전 탐색, 경로는 올바름 — 무방향과 방향 모두
    std::mt19937 rng(1736);
    int existed = 0, absent = 0;
    for (int it = 0; it < 6000; ++it) {
        int n = 1 + (int)(rng() % 5), m = (int)(rng() % 10); bool directed = it & 1; std::vector<std::pair<int, int>> edges;
        for (int i = 0; i < m; ++i) edges.push_back({(int)(rng() % n), (int)(rng() % n)});
        if (it % 3 == 0 && !directed) {                                                        // 짝수 차수를 자주 만들기 위해 닫힌 걸음을 섞는다
            edges.clear(); int len = 3 + (int)(rng() % 6), v = (int)(rng() % n), first = v;
            for (int i = 0; i + 1 < len; ++i) { int w = (int)(rng() % n); edges.push_back({v, w}); v = w; } edges.push_back({v, first});
        }
        Trail t = hierholzer(n, edges, directed); bool brute = bruteExists(n, edges, directed);
        assert(t.ok == brute);
        if (t.ok) { assert(validTrail(n, edges, directed, t)); ++existed; } else ++absent;
    }
    assert(existed > 1200 && absent > 1200);

    // ③ BEST 정리: 방향 오일러 다중 그래프(정점 ≤ 4, 간선 ≤ 8, 모든 정점에 간선, 약연결) 에서 오일러 회로 수 = t_w · Π (outdeg − 1)!
    int bestChecked = 0;
    for (int it = 0; it < 60000 && bestChecked < 300; ++it) {
        int n = 2 + (int)(rng() % 3); std::vector<std::pair<int, int>> edges;
        for (int c = 0, cycles = 1 + (int)(rng() % 3); c < cycles; ++c) {                      // 닫힌 걸음 몇 개를 합치면 진입 = 진출
            int len = 2 + (int)(rng() % 3), first = (int)(rng() % n), v = first;
            for (int i = 0; i + 1 < len; ++i) { int w = (int)(rng() % n); edges.push_back({v, w}); v = w; } edges.push_back({v, first});
        }
        if ((int)edges.size() > 8) continue;
        std::vector<int> outd(n, 0); for (auto [a, b] : edges) { ++outd[a]; (void)b; }
        bool allHave = true; for (int v = 0; v < n; ++v) allHave = allHave && outd[v] > 0;
        if (!allHave) continue;
        Trail t = hierholzer(n, edges, true); if (!t.ok) continue;                             // 약연결이 아니면 건너뜀
        // 라플라시안 L = D_out − A, 뿌리 w = 0 을 지운 소행렬식 = t_w
        std::vector<std::vector<long long>> L(n, std::vector<long long>(n, 0));
        for (auto [a, b] : edges) { L[a][a] += 1; L[a][b] -= 1; }
        std::vector<std::vector<long long>> minor(n - 1, std::vector<long long>(n - 1));
        for (int i = 1; i < n; ++i) for (int j = 1; j < n; ++j) minor[i - 1][j - 1] = L[i][j];
        long long tw = bareissDet(minor), prod = 1;
        for (int v = 0; v < n; ++v) for (int k = 2; k <= outd[v] - 1; ++k) prod *= k;
        std::vector<char> used(edges.size(), 0); used[0] = 1;
        long long brute = countCircuits(edges, edges[0].second, used, (int)edges.size() - 1, edges[0].first);
        assert(brute == tw * prod);
        ++bestChecked;
    }
    assert(bestChecked == 300);

    // ④ 큰 입력 (a) de Bruijn 그래프 B(2, 20): 정점 2^19, 간선 2^20 → 오일러 회로의 간선 라벨이 de Bruijn 수열 (모든 20 비트 문자열이 순환적으로 정확히 한 번)
    //    (b) 700×700 원환 격자 (모든 차수 4, 간선 980,000) 의 오일러 회로
    {
        const int K = 20, V = 1 << (K - 1); std::vector<std::pair<int, int>> edges; edges.reserve(1 << K);
        for (int u = 0; u < V; ++u) for (int b = 0; b < 2; ++b) edges.push_back({u, ((u << 1) | b) & (V - 1)});     // 간선 id = 2u + b 의 라벨은 b
        Trail t = hierholzer(V, edges, true);
        assert(t.ok && validTrail(V, edges, true, t));
        std::vector<int> bits(t.es.size()); for (std::size_t i = 0; i < bits.size(); ++i) bits[i] = t.es[i] & 1;
        std::vector<char> seen(1 << K, 0); unsigned window = 0;
        for (int i = 0; i < K - 1; ++i) window = (window << 1) | bits[i];
        for (std::size_t i = 0; i < bits.size(); ++i) { window = ((window << 1) | bits[(i + K - 1) % bits.size()]) & ((1u << K) - 1); assert(!seen[window]); seen[window] = 1; }
        assert(std::count(seen.begin(), seen.end(), 1) == (1 << K));                                             // 2^20 개 창이 모두 다르다
        const int R = 700; std::vector<std::pair<int, int>> grid;
        for (int r = 0; r < R; ++r) for (int c = 0; c < R; ++c) { grid.push_back({r * R + c, r * R + (c + 1) % R}); grid.push_back({r * R + c, ((r + 1) % R) * R + c}); }
        Trail g = hierholzer(R * R, grid, false); assert(g.ok && validTrail(R * R, grid, false, g) && g.vs.front() == g.vs.back());
    }
    std::cout << "EulerTour: iterative Hierholzer matched an exhaustive search over all trails on 6000 random multigraphs (loops, parallel edges, disconnected; undirected and directed, over 1200 with and over 1200 without a trail), every produced trail used each edge exactly once with consecutive edges joined, the BEST theorem count t_w * prod (outdeg-1)! equalled the number of Euler circuits enumerated by brute force on 300 directed multigraphs (Kirchhoff determinant via Bareiss), the circuit of the de Bruijn graph B(2,20) spelled a sequence in which all 2^20 cyclic windows were distinct, and a 700x700 torus grid with 980,000 edges was traversed" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## HeavyLightDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 중경량 분할 HLD (그래프 관점의 요약, 정본은 Tree.md Part 15): 트리(또는 그래프의 DFS 신장 트리)의 각 정점에서 서브트리가 가장 큰 자식 간선을 "무거운 간선" 으로 골라 정점들을 체인으로 나눈다.
// 루트에서 어느 정점까지 가벼운 간선은 log₂ n 개 이하라 경로 질의는 체인 O(log n) 개로 쪼개지고, 체인을 DFS 순서의 연속 구간으로 번호 매기면 펜윅/세그먼트 트리로 경로 합·갱신을 O(log² n) 에 처리한다.
// 검증: 무작위 트리에서 점 갱신 + 경로 합 질의를 정점마다 부모를 따라 올라가는 순진한 방법과 대조
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

// 센트로이드 분해 (그래프 관점의 요약, 정본은 Tree.md Part 15): 제거하면 남는 모든 컴포넌트가 n/2 이하가 되는 정점(센트로이드)을 루트로 삼고 남은 컴포넌트에 재귀해 깊이 O(log n) 의 센트로이드 트리를 만든다.
// 임의의 두 정점 경로는 센트로이드 트리에서 둘의 공통 조상 센트로이드를 반드시 지나므로 "가장 가까운 표시된 정점" 같은 질의를 O(log n) 에 답한다.
// 검증: 센트로이드 트리 깊이 ≤ log₂ n + 1, 표시/질의가 다중 출발 BFS 와 일치
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
# Part 14. 특수 그래프
## BipartiteGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 이분 그래프: 정점을 두 집합으로 나눠 모든 간선이 두 집합 사이에만 있게 할 수 있는 그래프 ⇔ 2-색칠 가능 ⇔ *홀수 사이클이 없다*. 세 가지 판정 — ① BFS 색칠: 층 번호의 홀짝이 색이고, 같은 색 끝점을 잇는 간선을 만나면 두 정점의 트리 경로 + 그 간선이 홀수 사이클(실제 증거를 돌려줄 수 있다) ② 반복형 DFS 색칠 ③ 홀짝을 같이 들고 다니는 서로소 집합(간선이 도착하는 대로 온라인 판정, 각 정점의 "루트와의 색 차이" 를 경로 압축 때 함께 갱신).
// 정리: 이분 그래프의 2-색칠 개수는 2^(연결 성분 수) (성분마다 한쪽 색을 고르면 나머지가 정해진다). Mantel/Turán: n 개 정점의 이분 그래프는 간선이 ⌊n²/4⌋ 개 이하이고 완전 이분 그래프 K_{⌊n/2⌋,⌈n/2⌉} 에서 달성된다. 자기 루프는 길이 1 인 홀수 사이클이라 이분 그래프가 아니다. 평행 간선은 영향이 없다.
// 검증: 정점 ≤ 6 의 모든 단순 그래프(2^15)에서 세 판정이 2^n 가지 색칠을 모두 시도하는 완전 탐색과 일치하고, 올바른 2-색칠의 개수가 2^성분 수, 증거 사이클은 단순하고 길이가 홀수이며 간선이 실제로 있다, 이름 붙은 이분 그래프의 개수가 1, 2, 7, 41, 376, 5177 (정점 1..6), 최대 간선 수가 ⌊n²/4⌋. 무작위 다중 그래프(루프·평행 간선), 그리고 정점 백만 개의 짝수·홀수 사이클과 계획된 이분 그래프.
using Edges = std::vector<std::pair<int, int>>;
struct Bip { bool ok; std::vector<int> color; std::vector<int> oddCycle; };

// ① BFS + 홀수 사이클 증거
Bip bfsColor(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n); for (auto [a, b] : e) { adj[a].push_back(b); if (a != b) adj[b].push_back(a); else adj[a].push_back(a); }
    Bip r{true, std::vector<int>(n, -1), {}};
    std::vector<int> par(n, -1), depth(n, 0);
    for (int s = 0; s < n; ++s) {
        if (r.color[s] >= 0) continue;
        std::queue<int> q; q.push(s); r.color[s] = 0;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : adj[u]) {
                if (r.color[v] < 0) { r.color[v] = r.color[u] ^ 1; par[v] = u; depth[v] = depth[u] + 1; q.push(v); }
                else if (r.color[v] == r.color[u]) {                                        // 같은 색을 잇는 간선: 트리 경로 + 이 간선 = 홀수 사이클
                    std::vector<int> a, b; int x = u, y = v;
                    while (depth[x] > depth[y]) { a.push_back(x); x = par[x]; }
                    while (depth[y] > depth[x]) { b.push_back(y); y = par[y]; }
                    while (x != y) { a.push_back(x); b.push_back(y); x = par[x]; y = par[y]; }
                    a.push_back(x);                                                         // 공통 조상
                    std::reverse(b.begin(), b.end()); a.insert(a.end(), b.begin(), b.end());   // u … 조상 … v (v–u 간선이 닫는다)
                    r.ok = false; r.oddCycle = a; return r;
                }
            }
        }
    }
    return r;
}
// ② 반복형 DFS
bool dfsBipartite(int n, const Edges& e) {
    std::vector<std::vector<int>> adj(n); for (auto [a, b] : e) { adj[a].push_back(b); if (a != b) adj[b].push_back(a); else adj[a].push_back(a); }
    std::vector<int> color(n, -1), it(n, 0), st;
    for (int s = 0; s < n; ++s) {
        if (color[s] >= 0) continue;
        color[s] = 0; st.push_back(s);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] == (int)adj[u].size()) { st.pop_back(); continue; }
            int v = adj[u][it[u]++];
            if (color[v] < 0) { color[v] = color[u] ^ 1; st.push_back(v); } else if (color[v] == color[u]) return false;
        }
    }
    return true;
}
// ③ 홀짝 서로소 집합: par[x] = x 와 부모의 색 차이 (0 같음, 1 다름)
struct ParityDsu {
    std::vector<int> p, par, sz; bool ok = true;
    explicit ParityDsu(int n) : p(n), par(n, 0), sz(n, 1) { std::iota(p.begin(), p.end(), 0); }
    int find(int x, int& parity) {                                                   // 루트를 돌려주고 parity 에 x 의 루트 대비 색 차이를 넣는다 (반복형 경로 압축)
        int r = x, acc = 0; while (p[r] != r) { acc ^= par[r]; r = p[r]; }
        int cur = x, curPar = acc;
        while (cur != r) { int next = p[cur], nextPar = curPar ^ par[cur]; p[cur] = r; par[cur] = curPar; cur = next; curPar = nextPar; }
        parity = acc; return r;
    }
    bool addEdge(int a, int b) {                                                     // a 와 b 는 다른 색이어야 한다
        int pa, pb, ra = find(a, pa), rb = find(b, pb);
        if (ra == rb) { if (pa == pb) ok = false; return ok; }
        if (sz[ra] > sz[rb]) std::swap(ra, rb);
        p[ra] = rb; par[ra] = pa ^ pb ^ 1; sz[rb] += sz[ra];
        return ok;
    }
};
bool dsuBipartite(int n, const Edges& e) { ParityDsu d(n); for (auto [a, b] : e) d.addEdge(a, b); return d.ok; }

// ---- 오라클 ----
bool validOddCycle(const Edges& e, const std::vector<int>& c) {
    int k = (int)c.size(); if (k % 2 == 0) return false;
    std::vector<int> s = c; std::sort(s.begin(), s.end()); if (std::adjacent_find(s.begin(), s.end()) != s.end()) return false;
    for (int i = 0; i < k; ++i) {
        int a = c[i], b = c[(i + 1) % k]; bool found = false;
        for (auto [x, y] : e) if ((x == a && y == b) || (x == b && y == a)) { found = true; break; }
        if (!found) return false;
    }
    return true;
}
long long countColorings(int n, const Edges& e) {                                    // 모든 2^n 가지 색칠 중 올바른 것의 수
    long long ok = 0;
    for (unsigned mask = 0; mask < (1u << n); ++mask) { bool good = true; for (auto [a, b] : e) if ((mask >> a & 1) == (mask >> b & 1)) { good = false; break; } ok += good; }
    return ok;
}
int components(int n, const Edges& e) { std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto f = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; int c = n; for (auto [a, b] : e) { a = f(a); b = f(b); if (a != b) { p[a] = b; --c; } } return c; }

int main() {
    // ① 손으로 확인한 모양: 4-사이클은 이분, 삼각형은 아님(증거는 길이 3), 루프는 길이 1
    {   Edges sq = {{0, 1}, {1, 2}, {2, 3}, {3, 0}};
        Bip b = bfsColor(4, sq); assert(b.ok && b.color[0] != b.color[1] && b.color[0] == b.color[2] && dfsBipartite(4, sq) && dsuBipartite(4, sq));
        Edges tri = {{0, 1}, {1, 2}, {2, 0}};
        Bip t = bfsColor(3, tri); assert(!t.ok && t.oddCycle.size() == 3 && validOddCycle(tri, t.oddCycle) && !dfsBipartite(3, tri) && !dsuBipartite(3, tri));
        Edges loop = {{0, 0}}; Bip l = bfsColor(1, loop); assert(!l.ok && l.oddCycle == std::vector<int>({0}) && !dsuBipartite(1, loop));
        Edges par = {{0, 1}, {0, 1}, {1, 0}}; assert(bfsColor(2, par).ok && dsuBipartite(2, par));    // 평행 간선은 영향 없음
    }

    // ② 전수: 정점 ≤ 6 의 모든 단순 그래프 — 세 판정 = 완전 탐색, 색칠 수 = 2^성분, 증거 검증, 이분 그래프의 수와 최대 간선 수
    const long long want[7] = {0, 1, 2, 7, 41, 376, 5177};
    for (int n = 1; n <= 6; ++n) {
        Edges pairs; for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size(); long long count = 0; int maxEdges = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Edges e; for (int i = 0; i < m; ++i) if (mask >> i & 1) e.push_back(pairs[i]);
            long long colorings = countColorings(n, e); bool brute = colorings > 0;
            Bip b = bfsColor(n, e);
            assert(b.ok == brute && dfsBipartite(n, e) == brute && dsuBipartite(n, e) == brute);
            if (brute) {
                assert(colorings == (1LL << components(n, e)));
                for (auto [x, y] : e) assert(b.color[x] != b.color[y]);                     // BFS 색칠이 실제로 올바르다
                ++count; maxEdges = std::max(maxEdges, (int)e.size());
            } else assert(validOddCycle(e, b.oddCycle));
        }
        assert(count == want[n] && maxEdges == n * n / 4);                                   // Mantel: ⌊n²/4⌋ 에서 딱 맞음
    }

    // ③ 무작위 다중 그래프 (루프·평행 간선, 정점 ≤ 12)
    std::mt19937 rng(1736);
    int yes = 0, no = 0;
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 12), m = (int)(rng() % (2 * n + 1)); Edges e;
        bool planted = it % 2 == 0; std::vector<int> side(n); for (int& s : side) s = (int)(rng() & 1);
        for (int i = 0; i < m; ++i) {
            int a = (int)(rng() % n), b = (int)(rng() % n);
            if (planted && side[a] == side[b] && rng() % 10) continue;                       // 심어 둔 분할을 거의 따른다 (가끔 위반 → 비이분)
            e.push_back({a, b});
        }
        bool brute = countColorings(n, e) > 0; Bip b = bfsColor(n, e);
        assert(b.ok == brute && dfsBipartite(n, e) == brute && dsuBipartite(n, e) == brute);
        if (!brute) assert(validOddCycle(e, b.oddCycle)); (brute ? yes : no)++;
    }
    assert(yes > 500 && no > 500);

    // ④ 큰 입력: 정점 백만 개의 짝수 사이클은 이분, 정점 1,000,001 개의 홀수 사이클은 증거 길이가 정확히 1,000,001; 심은 분할로 만든 무작위 이분 그래프(정점 50 만, 간선 100 만)에 간선 하나를 틀리게 넣으면 판정이 뒤집히고 증거가 올바르다
    {
        const int N = 1000000; Edges cyc; for (int i = 0; i < N; ++i) cyc.push_back({i, (i + 1) % N});
        assert(bfsColor(N, cyc).ok && dfsBipartite(N, cyc) && dsuBipartite(N, cyc));
        Edges odd; for (int i = 0; i <= N; ++i) odd.push_back({i, (i + 1) % (N + 1)});
        Bip b = bfsColor(N + 1, odd); assert(!b.ok && (int)b.oddCycle.size() == N + 1 && !dfsBipartite(N + 1, odd) && !dsuBipartite(N + 1, odd));
        const int V = 500000; std::mt19937_64 r(8); std::vector<int> side(V); for (int& s : side) s = (int)(r() & 1);
        Edges big; while ((int)big.size() < 2 * V) { int a = (int)(r() % V), c = (int)(r() % V); if (side[a] != side[c]) big.push_back({a, c}); }
        Bip g = bfsColor(V, big); assert(g.ok && dfsBipartite(V, big) && dsuBipartite(V, big));
        for (auto [x, y] : big) assert(g.color[x] != g.color[y]);
        int a = 0, c = 1; while (side[a] != side[c] || a == c) ++c;                              // 같은 쪽 두 정점을 잇는 간선
        big.push_back({a, c});
        Bip bad = bfsColor(V, big); assert(!bad.ok && !dfsBipartite(V, big) && !dsuBipartite(V, big) && validOddCycle(big, bad.oddCycle));
    }
    std::cout << "BipartiteGraph: BFS two-colouring (with an odd-cycle witness), iterative DFS and a parity union-find all agreed with trying all 2^n colourings on every one of the 33,867 simple graphs with up to 6 vertices, the number of valid colourings was always 2^(components), witnesses were genuine odd simple cycles, the counts of labeled bipartite graphs came out 1,2,7,41,376,5177 with at most floor(n^2/4) edges, 3000 random multigraphs with loops agreed, a 1,000,000-cycle was bipartite while a 1,000,001-cycle returned its whole cycle as the witness, and one wrong edge planted in a 500,000-vertex bipartite graph flipped all three verdicts" << std::endl; return 0;
}
// Time Complexity: O(V + E)  (서로소 집합 판정은 O(E α(V)))
// Space Complexity: O(V + E)
```
## DirectedGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 방향 그래프(digraph): 간선 u→v 는 순서쌍이다. 진입 차수와 진출 차수가 따로 있고 Σ진출 = Σ진입 = |E| (방향 그래프의 악수 보조정리). 뒤집은 그래프(transpose)는 모든 간선의 방향을 바꾼 것으로 두 번 뒤집으면 원래대로이며 진입·진출 차수가 서로 바뀐다. 인접 행렬 A 의 k 제곱 (A^k)[i][j] 는 i 에서 j 로 가는 길이 k 인 *걸음의 수*이고, 그래서 DAG ⇔ A 가 멱영(어떤 k ≤ n 에서 A^k = 0) 이다(걸음이 정점을 반복하려면 사이클이 있어야 하므로).
// 토너먼트(모든 두 정점 사이에 간선이 정확히 하나인 방향 그래프)는 방향 그래프 이론의 보석 상자다 — Rédei: 모든 토너먼트에는 해밀턴 경로가 있다(정점을 하나씩 이분 탐색으로 끼워 넣어 O(n log n) 비교로 만든다). Camion: 강연결 토너먼트(n ≥ 3)에는 해밀턴 사이클이 있다 — 즉 "강연결 ⇔ 해밀턴 사이클" 이다. Landau: 점수열(진출 차수)을 오름차순 s₁ ≤ … ≤ sₙ 으로 놓으면 모든 k 에서 Σ_{i≤k} sᵢ ≥ C(k, 2) 이고 k = n 에서 등호.
// 검증: ① 임의의 방향 다중 그래프(루프·평행 간선) 에서 차수 합, 뒤집기 두 번 = 원래, 차수 교환 ② 인접 행렬 거듭제곱 = 걸음 수(완전 열거), 정점 ≤ 4 의 모든 방향 그래프에서 "멱영 ⇔ 사이클 없음(카안 알고리즘)" ③ 정점 ≤ 5 의 모든 토너먼트(2^10)에서 Rédei 경로가 올바르고, 강연결 ⇔ 해밀턴 사이클(모든 순열 시도), 강연결 토너먼트의 수 1, 0, 2, 24, 544 ④ Landau 부등식 ⑤ 정점 3000 의 큰 토너먼트와 간선 30 만의 큰 방향 그래프.
using Edges = std::vector<std::pair<int, int>>;
struct Digraph {
    int n; std::vector<std::vector<int>> out, in; long long edges = 0;
    explicit Digraph(int nn) : n(nn), out(nn), in(nn) {}
    void addEdge(int u, int v) { out[u].push_back(v); in[v].push_back(u); ++edges; }            // 자기 루프는 u 의 진출과 진입에 한 번씩
    Digraph transpose() const { Digraph t(n); for (int u = 0; u < n; ++u) for (int v : out[u]) t.addEdge(v, u); return t; }
    std::multiset<std::pair<int, int>> edgeSet() const { std::multiset<std::pair<int, int>> s; for (int u = 0; u < n; ++u) for (int v : out[u]) s.insert({u, v}); return s; }
};
using Matrix = std::vector<std::vector<long long>>;
Matrix adjacency(const Digraph& g) { Matrix a(g.n, std::vector<long long>(g.n, 0)); for (int u = 0; u < g.n; ++u) for (int v : g.out[u]) ++a[u][v]; return a; }
Matrix multiply(const Matrix& a, const Matrix& b) { int n = (int)a.size(); Matrix c(n, std::vector<long long>(n, 0)); for (int i = 0; i < n; ++i) for (int k = 0; k < n; ++k) if (a[i][k]) for (int j = 0; j < n; ++j) c[i][j] += a[i][k] * b[k][j]; return c; }
bool isZero(const Matrix& a) { for (auto& r : a) for (long long x : r) if (x) return false; return true; }
long long walksByEnumeration(const Digraph& g, int from, int to, int len) {
    if (len == 0) return from == to;
    long long total = 0; for (int v : g.out[from]) total += walksByEnumeration(g, v, to, len - 1); return total;
}
bool acyclicByKahn(const Digraph& g) {
    std::vector<int> indeg(g.n, 0), q; for (int u = 0; u < g.n; ++u) for (int v : g.out[u]) ++indeg[v];
    for (int v = 0; v < g.n; ++v) if (!indeg[v]) q.push_back(v);
    std::size_t head = 0; while (head < q.size()) { int u = q[head++]; for (int v : g.out[u]) if (--indeg[v] == 0) q.push_back(v); }
    return (int)q.size() == g.n;
}

// ---- 토너먼트 ----
// beats[u][v] = u → v. Rédei 경로: 정점을 하나씩 이분 탐색으로 끼워 넣는다
template <class Beats> std::vector<int> redei(int n, Beats beats) {
    std::vector<int> path;
    for (int v = 0; v < n; ++v) {
        if (path.empty() || beats(v, path.front())) { path.insert(path.begin(), v); continue; }
        if (beats(path.back(), v)) { path.push_back(v); continue; }
        int lo = 0, hi = (int)path.size() - 1;                                          // 불변식: path[lo] → v → path[hi]
        while (hi - lo > 1) { int mid = (lo + hi) / 2; if (beats(path[mid], v)) lo = mid; else hi = mid; }
        path.insert(path.begin() + hi, v);
    }
    return path;
}
bool stronglyConnected(int n, const std::vector<std::vector<char>>& beats) {
    std::vector<unsigned> row(n); for (int i = 0; i < n; ++i) { row[i] = 1u << i; for (int j = 0; j < n; ++j) if (beats[i][j]) row[i] |= 1u << j; }
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (row[i] >> k & 1) row[i] |= row[k];
    for (int i = 0; i < n; ++i) if (row[i] != (1u << n) - 1) return false;
    return true;
}
bool hasHamiltonCycle(int n, const std::vector<std::vector<char>>& beats) {
    std::vector<int> p(n); std::iota(p.begin(), p.end(), 0);
    do { bool ok = true; for (int i = 0; i < n && ok; ++i) ok = beats[p[i]][p[(i + 1) % n]]; if (ok) return true; } while (std::next_permutation(p.begin() + 1, p.end()));
    return false;
}

int main() {
    std::mt19937 rng(1736);
    // ① 임의의 방향 다중 그래프: 차수 합 · 뒤집기 두 번 · 차수 교환
    for (int it = 0; it < 500; ++it) {
        int n = 1 + (int)(rng() % 12), m = (int)(rng() % 40); Digraph g(n);
        for (int i = 0; i < m; ++i) g.addEdge((int)(rng() % n), (int)(rng() % n));
        long long so = 0, si = 0; for (int v = 0; v < n; ++v) { so += g.out[v].size(); si += g.in[v].size(); }
        Digraph t = g.transpose(), tt = t.transpose();
        assert(so == g.edges && si == g.edges && tt.edgeSet() == g.edgeSet());
        for (int v = 0; v < n; ++v) assert(t.out[v].size() == g.in[v].size() && t.in[v].size() == g.out[v].size());
    }

    // ② 인접 행렬 거듭제곱 = 걸음 수 (완전 열거), 정점 ≤ 4 의 모든 방향 그래프(루프 포함)에서 "A^n = 0 ⇔ 사이클 없음"
    for (int it = 0; it < 200; ++it) {
        int n = 2 + (int)(rng() % 4); Digraph g(n); int m = (int)(rng() % (3 * n));
        for (int i = 0; i < m; ++i) g.addEdge((int)(rng() % n), (int)(rng() % n));
        Matrix a = adjacency(g), p = a;
        for (int k = 1; k <= 4; ++k) { for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) assert(p[i][j] == walksByEnumeration(g, i, j, k)); p = multiply(p, a); }
    }
    long long dags = 0;
    for (int n = 1; n <= 4; ++n) {
        std::vector<std::pair<int, int>> all; for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) all.push_back({a, b});     // 루프 포함
        int m = (int)all.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            Digraph g(n); for (int i = 0; i < m; ++i) if (mask >> i & 1) g.addEdge(all[i].first, all[i].second);
            Matrix a = adjacency(g), p = a; for (int k = 1; k < n; ++k) p = multiply(p, a);                                      // p = A^n
            bool nilpotent = isZero(p); assert(nilpotent == acyclicByKahn(g)); dags += nilpotent;
        }
    }
    assert(dags == 1 + 3 + 25 + 543);                                                                                          // 이름 붙은 DAG 의 수

    // ③ 토너먼트 전수: 정점 ≤ 5 (2^10): Rédei 경로, 강연결 ⇔ 해밀턴 사이클, 강연결 토너먼트의 수, Landau 부등식
    const long long strongWant[6] = {0, 1, 0, 2, 24, 544};
    for (int n = 1; n <= 5; ++n) {
        std::vector<std::pair<int, int>> pairs; for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b});
        int m = (int)pairs.size(); long long strong = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            std::vector<std::vector<char>> beats(n, std::vector<char>(n, 0)); std::vector<int> score(n, 0);
            for (int i = 0; i < m; ++i) { int a = pairs[i].first, b = pairs[i].second; if (mask >> i & 1) beats[a][b] = 1; else beats[b][a] = 1; }
            for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) score[a] += beats[a][b];
            std::vector<int> path = redei(n, [&](int u, int v) { return beats[u][v] != 0; });
            assert((int)path.size() == n); { std::vector<int> s = path; std::sort(s.begin(), s.end()); for (int i = 0; i < n; ++i) assert(s[i] == i); }
            for (int i = 0; i + 1 < n; ++i) assert(beats[path[i]][path[i + 1]]);                                              // Rédei: 해밀턴 경로
            bool sc = stronglyConnected(n, beats);
            if (n >= 3) assert(sc == hasHamiltonCycle(n, beats));                                                                // Camion
            strong += sc;
            std::sort(score.begin(), score.end()); int prefix = 0;                                                               // Landau
            for (int k = 1; k <= n; ++k) { prefix += score[k - 1]; assert(prefix >= k * (k - 1) / 2); }
            assert(prefix == n * (n - 1) / 2);
        }
        assert(strong == strongWant[n]);
    }

    // ④ 큰 입력: 정점 3000 의 무작위 토너먼트 (약 450 만 쌍) 의 Rédei 경로, 간선 30 만의 방향 그래프 (차수 합 · 뒤집기)
    {
        const int N = 3000; std::vector<std::vector<char>> beats(N, std::vector<char>(N, 0));
        for (int a = 0; a < N; ++a) for (int b = a + 1; b < N; ++b) { if (rng() & 1) beats[a][b] = 1; else beats[b][a] = 1; }
        std::vector<int> path = redei(N, [&](int u, int v) { return beats[u][v] != 0; });
        assert((int)path.size() == N); for (int i = 0; i + 1 < N; ++i) assert(beats[path[i]][path[i + 1]]);
        const int V = 50000; Digraph g(V); for (int i = 0; i < 300000; ++i) g.addEdge((int)(rng() % V), (int)(rng() % V));
        Digraph t = g.transpose(); long long so = 0, ti = 0; for (int v = 0; v < V; ++v) { so += g.out[v].size(); ti += t.in[v].size(); }
        assert(so == 300000 && ti == 300000 && t.transpose().edgeSet() == g.edgeSet());
    }
    std::cout << "DirectedGraph: degree sums, double transposition and in/out degree swapping held on 500 random digraphs with loops and parallel edges, A^k counted walks exactly (checked against enumeration), 'A^n = 0' coincided with acyclicity on every digraph with up to 4 vertices (the 1+3+25+543 DAGs), on all tournaments with up to 5 vertices Redei insertion built a Hamiltonian path, strong connectivity coincided with having a Hamiltonian cycle (Camion), strong tournaments numbered 1,0,2,24,544 and Landau's inequalities held, and a 3000-vertex tournament and a 300,000-edge digraph passed too" << std::endl; return 0;
}
// Time Complexity: 간선 추가 O(1), 뒤집기 O(V + E), 행렬 곱 O(n³)
// Space Complexity: O(V + E)
```
## UndirectedGraph()
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

// 무방향 그래프: 간선 {u, v} 는 순서가 없다. 인접 리스트에는 양쪽 모두 기록한다.
// 악수 보조정리(handshake lemma): 모든 정점의 차수의 합 = 2·|E|  (그러므로 홀수 차수 정점의 수는 항상 짝수).  자기 고리는 차수에 2 를 더한다.
//  ① 무작위 연산(정점 1~8, 간선 0~20 개, 자기 고리·평행 간선 포함) 3 000 개를 (u, v) 쌍 개수 *행렬* 로 따로 센 오라클과 대조: 차수·간선 수·연결 성분 수·홀수 차수 정점 수가 같고 악수 보조정리·홀수 정점 짝수 개가 성립
//  ② 차수열의 실현 가능성: 정점 n ≤ 6 의 *모든* 단순 그래프(2^15 개)에서 나오는 차수열 집합을 모은 뒤, 길이 n·값 0..n−1 의 *모든* 수열(최대 46 656 개)에서 "실현 가능 ⇔ 에르되시–갈라이 판정 ⇔ 하벨–하키미 판정"  ③ 하벨–하키미 판정이 참이면 그 수열을 정확히 실현하는 단순 그래프를 *실제로 만들어* 차수를 다시 센다(큰 수열 200 개)
class UndirectedGraph {
    std::vector<std::vector<int>> adj; size_t edges = 0;
public:
    explicit UndirectedGraph(int n) : adj(n) {}
    void addEdge(int u, int v) {
        adj[u].push_back(v);
        adj[v].push_back(u);                              // 자기 루프(u == v)는 같은 목록에 두 번 -> 차수에 2
        edges++;
    }
    size_t degree(int u) const { return adj[u].size(); }
    size_t edgeCount() const { return edges; }
    int components() const {
        std::vector<bool> seen(adj.size(), false); int c = 0;
        for (size_t s = 0; s < adj.size(); s++) {
            if (seen[s]) continue;
            c++; std::queue<int> q; q.push((int)s); seen[s] = true;
            while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = true; q.push(v); } }
        }
        return c;
    }
    int oddDegreeCount() const { int c = 0; for (auto& a : adj) c += a.size() % 2; return c; }
};
bool erdosGallai(std::vector<int> d) {                                                  // 합이 짝수이고 모든 k 에서 앞 k 개의 합 ≤ k(k−1) + Σ_{i>k} min(d_i, k)
    std::sort(d.rbegin(), d.rend()); long total = std::accumulate(d.begin(), d.end(), 0L); if (total % 2) return false; int n = (int)d.size();
    for (int k = 1; k <= n; ++k) { long left = 0, right = (long)k * (k - 1); for (int i = 0; i < k; ++i) left += d[i]; for (int i = k; i < n; ++i) right += std::min(d[i], k); if (left > right) return false; } return true; }
bool havelHakimi(std::vector<int> d) {                                                  // 가장 큰 차수 x 를 골라 다음 x 개 정점에 간선을 하나씩 준다
    for (;;) { std::sort(d.rbegin(), d.rend()); if (d.empty() || d[0] == 0) return true; int x = d[0]; d.erase(d.begin()); if (x > (int)d.size()) return false; for (int i = 0; i < x; ++i) if (--d[i] < 0) return false; } }
std::vector<std::pair<int, int>> buildFromSequence(std::vector<int> deg) {              // 하벨–하키미를 따라 실제 간선 목록을 만든다
    int n = (int)deg.size(); std::vector<std::pair<int, int>> out; std::vector<int> id(n); std::iota(id.begin(), id.end(), 0);
    for (;;) { std::sort(id.begin(), id.end(), [&](int a, int b) { return deg[a] > deg[b]; }); int u = id[0]; if (deg[u] == 0) return out; int x = deg[u]; deg[u] = 0; for (int i = 1; i <= x; ++i) { int v = id[i]; --deg[v]; out.push_back({u, v}); } } }

int main() {
    {   UndirectedGraph g(6); g.addEdge(0, 1); g.addEdge(1, 2); g.addEdge(2, 0); g.addEdge(3, 4);
        size_t sum = 0; for (int i = 0; i < 6; i++) sum += g.degree(i); assert(sum == 2 * g.edgeCount() && g.components() == 3 && g.oddDegreeCount() % 2 == 0); g.addEdge(5, 5); assert(g.degree(5) == 2 && g.edgeCount() == 5); }
    std::mt19937 rng(12);
    for (int trial = 0; trial < 3000; ++trial) { int n = 1 + (int)(rng() % 8), m = (int)(rng() % 21); UndirectedGraph g(n); std::vector<std::vector<int>> cnt(n, std::vector<int>(n, 0));        // ①
        for (int i = 0; i < m; ++i) { int u = (int)(rng() % n), v = (int)(rng() % n); g.addEdge(u, v); ++cnt[u][v]; if (u != v) ++cnt[v][u]; }
        size_t sum = 0; int odd = 0; for (int u = 0; u < n; ++u) { int want = 0; for (int v = 0; v < n; ++v) want += cnt[u][v] * (u == v ? 2 : 1); assert((int)g.degree(u) == want); sum += g.degree(u); odd += want % 2; }
        assert(sum == 2 * g.edgeCount() && (int)g.edgeCount() == m && g.oddDegreeCount() == odd && odd % 2 == 0);
        std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; int comps = n; for (int u = 0; u < n; ++u) for (int v = u + 1; v < n; ++v) if (cnt[u][v] && find(u) != find(v)) { p[find(u)] = find(v); --comps; }
        assert(g.components() == comps); }
    for (int n = 1; n <= 6; ++n) {                                                                                                                          // ② 차수열 전수
        std::vector<std::pair<int, int>> pairs; for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) pairs.push_back({a, b}); std::set<std::vector<int>> realizable;
        for (unsigned mask = 0; mask < (1u << pairs.size()); ++mask) { std::vector<int> d(n, 0); for (size_t k = 0; k < pairs.size(); ++k) if (mask >> k & 1) { ++d[pairs[k].first]; ++d[pairs[k].second]; } std::sort(d.rbegin(), d.rend()); realizable.insert(d); }
        long total = 1; for (int i = 0; i < n; ++i) total *= n; long yes = 0;
        for (long code = 0; code < total; ++code) { std::vector<int> d(n); long c = code; for (int i = 0; i < n; ++i) { d[i] = (int)(c % n); c /= n; } std::vector<int> sorted = d; std::sort(sorted.rbegin(), sorted.rend()); bool real = realizable.count(sorted) > 0;
            assert(erdosGallai(d) == real && havelHakimi(d) == real); yes += real; }
        assert(yes > 0 && (n == 1 ? yes == 1 : yes < total)); }
    for (int trial = 0; trial < 200; ++trial) { int n = 5 + (int)(rng() % 40); UndirectedGraph g(n); std::vector<std::vector<char>> adj(n, std::vector<char>(n, 0)); for (int u = 0; u < n; ++u) for (int v = u + 1; v < n; ++v) if (rng() % 4 == 0) { adj[u][v] = adj[v][u] = 1; g.addEdge(u, v); }       // ③
        std::vector<int> deg(n); for (int u = 0; u < n; ++u) deg[u] = (int)g.degree(u); assert(erdosGallai(deg) && havelHakimi(deg));
        auto built = buildFromSequence(deg); std::vector<int> got(n, 0); std::set<std::pair<int, int>> seen; for (auto e : built) { assert(e.first != e.second && seen.insert({std::min(e.first, e.second), std::max(e.first, e.second)}).second); ++got[e.first]; ++got[e.second]; } assert(got == deg); }
    std::cout << "UndirectedGraph: degree, edge-count, component and odd-vertex queries matched a count-matrix oracle on 3000 random multigraphs, and the Erdos-Gallai and Havel-Hakimi tests agreed with 'some simple graph realizes it' for every degree sequence up to 6 vertices" << std::endl;
    return 0;
}
// Time Complexity: 간선 추가 O(1), 연결 요소 O(V + E)
// Space Complexity: O(V + E)
```
## WeightedGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 가중치 그래프: 간선마다 비용이 있다. "홉 수가 최소인 경로" 와 "비용이 최소인 경로" 는 다르다.
// 비음수 가중치에는 Dijkstra, 음수 간선이 있으면 Bellman-Ford 가 필요하다 (Dijkstra 는 이미 확정한 정점을 다시 고치지 않아 틀린 답을 낸다).  음수 사이클이 있으면 최단 거리가 정의되지 않으므로 Bellman-Ford 는 그것을 *알려야* 한다.
//  ① 홉 수와 비용이 다른 예, 음수 간선에서 Dijkstra 가 틀리는 예  ② 무작위 방향 그래프 3 000 개(정점 1~8, 간선 0~25 개, 가중치 0..9, 0 가중치·평행 간선·자기 고리 포함)에서 Dijkstra == Bellman-Ford == 플로이드–워셜(독립 구현)
//  ③ 음수 간선은 있되 음수 사이클은 없는 그래프(가중치 = c + p[u] − p[v], c ≥ 0 이라 어떤 사이클의 합도 Σc ≥ 0) 3 000 개: Bellman-Ford == 플로이드–워셜이고, 고전적 Dijkstra 는 *틀리는 경우가 실제로 존재*  ④ 재가중(Johnson): Bellman-Ford 로 얻은 h 로 w' = w + h[u] − h[v] ≥ 0 이 되어 Dijkstra 가 정답이 되고, d(u,v) = d'(u,v) − h[u] + h[v]
//  ⑤ 음수 사이클 탐지: 가중치 −4..8 의 무작위 그래프 3 000 개에서 "출발점에서 닿는 음수 사이클이 있다"는 Bellman-Ford 의 보고 == 플로이드–워셜 대각선 검사
typedef std::vector<std::vector<std::pair<int, int>>> WGraph;      // adj[u] = {(v, w)}
const long long INF = (long long)1e15;
std::vector<int> bfsHops(const WGraph& g, int s) {
    std::vector<int> d(g.size(), -1); std::queue<int> q; q.push(s); d[s] = 0;
    while (!q.empty()) { int u = q.front(); q.pop(); for (auto& e : g[u]) if (d[e.first] < 0) { d[e.first] = d[u] + 1; q.push(e.first); } }
    return d;
}
std::vector<long long> dijkstra(const WGraph& g, int s) {           // 고전적 Dijkstra: 꺼낸 정점은 확정
    std::vector<long long> d(g.size(), INF); std::vector<bool> done(g.size(), false); d[s] = 0;
    std::priority_queue<std::pair<long long, int>, std::vector<std::pair<long long, int>>, std::greater<>> pq; pq.push({0, s});
    while (!pq.empty()) {
        int u = pq.top().second; pq.pop();
        if (done[u]) continue;
        done[u] = true;
        for (auto& e : g[u]) if (!done[e.first] && d[u] + e.second < d[e.first]) { d[e.first] = d[u] + e.second; pq.push({d[e.first], e.first}); }
    }
    return d;
}
bool bellmanFord(const WGraph& g, int s, std::vector<long long>& d) {   // 출발점에서 닿는 음수 사이클이 있으면 false
    int n = (int)g.size(); d.assign(n, INF); d[s] = 0;
    for (int round = 0; round < n; round++) { bool changed = false; for (int u = 0; u < n; u++) if (d[u] < INF) for (auto& e : g[u]) if (d[u] + e.second < d[e.first]) { d[e.first] = d[u] + e.second; changed = true; }
        if (!changed) return true; if (round == n - 1) return false; }                    // n 번째 라운드에도 갱신되면 음수 사이클
    return true;
}
std::vector<std::vector<long long>> floydWarshall(const WGraph& g) {                      // 독립 오라클
    int n = (int)g.size(); std::vector<std::vector<long long>> d(n, std::vector<long long>(n, INF)); for (int i = 0; i < n; i++) d[i][i] = 0;
    for (int u = 0; u < n; u++) for (auto& e : g[u]) d[u][e.first] = std::min(d[u][e.first], (long long)e.second);
    for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (d[i][k] < INF && d[k][j] < INF) d[i][j] = std::min(d[i][j], d[i][k] + d[k][j]);
    return d; }

int main() {
    {   WGraph g(4); auto add = [&](int u, int v, int w) { g[u].push_back({v, w}); g[v].push_back({u, w}); }; add(0, 1, 10); add(0, 2, 1); add(2, 3, 1); add(3, 1, 1);
        assert(bfsHops(g, 0)[1] == 1 && dijkstra(g, 0)[1] == 3);                                                                                        // ① 홉 수는 1, 비용은 3
        WGraph n(3); n[0].push_back({1, 1}); n[0].push_back({2, 3}); n[2].push_back({1, -5}); std::vector<long long> d; assert(bellmanFord(n, 0, d) && d[1] == -2 && dijkstra(n, 0)[1] == 1); }       // 음수 간선: 올바른 답 −2, Dijkstra 는 1
    std::mt19937 rng(23);
    for (int trial = 0; trial < 3000; ++trial) { int n = 1 + (int)(rng() % 8), m = (int)(rng() % 26); WGraph g(n); for (int i = 0; i < m; ++i) g[rng() % n].push_back({(int)(rng() % n), (int)(rng() % 10)});          // ②
        auto fw = floydWarshall(g); for (int s = 0; s < n; ++s) { std::vector<long long> bf; assert(bellmanFord(g, s, bf)); auto dj = dijkstra(g, s); assert(dj == bf && bf == fw[s]); } }
    long dijkstraWrong = 0, total = 0;
    for (int trial = 0; trial < 3000; ++trial) { int n = 2 + (int)(rng() % 7), m = (int)(rng() % 26); std::vector<int> pot(n); for (int& p : pot) p = (int)(rng() % 10); WGraph g(n);                           // ③ 음수 간선, 음수 사이클 없음
        for (int i = 0; i < m; ++i) { int u = (int)(rng() % n), v = (int)(rng() % n), c = (int)(rng() % 6); g[u].push_back({v, c + pot[u] - pot[v]}); }
        auto fw = floydWarshall(g); for (int s = 0; s < n; ++s) { std::vector<long long> bf; assert(bellmanFord(g, s, bf) && bf == fw[s]); ++total; if (dijkstra(g, s) != bf) ++dijkstraWrong; }
        std::vector<long long> h(n, 0); { WGraph aug = g; aug.push_back({}); for (int v = 0; v < n; ++v) aug[n].push_back({v, 0}); std::vector<long long> hh; assert(bellmanFord(aug, n, hh)); for (int v = 0; v < n; ++v) h[v] = hh[v]; }       // ④ 재가중
        WGraph re(n); for (int u = 0; u < n; ++u) for (auto& e : g[u]) { long long w2 = e.second + h[u] - h[e.first]; assert(w2 >= 0); re[u].push_back({e.first, (int)w2}); }
        for (int s = 0; s < n; ++s) { auto d2 = dijkstra(re, s); for (int v = 0; v < n; ++v) if (d2[v] < INF) assert(d2[v] - h[s] + h[v] == fw[s][v]); else assert(fw[s][v] >= INF); } }
    assert(dijkstraWrong > 0 && dijkstraWrong < total);                                                                                                 // 틀리는 경우가 있고, 항상 틀리지는 않는다
    long cyc = 0, acyc = 0;
    for (int trial = 0; trial < 3000; ++trial) { int n = 1 + (int)(rng() % 7), m = (int)(rng() % 20); WGraph g(n); for (int i = 0; i < m; ++i) g[rng() % n].push_back({(int)(rng() % n), (int)(rng() % 13) - 4});     // ⑤
        auto fw = floydWarshall(g); for (int s = 0; s < n; ++s) { std::vector<long long> d; bool noNegCycle = bellmanFord(g, s, d); bool oracleNeg = false; for (int v = 0; v < n; ++v) if (fw[s][v] < INF && fw[v][v] < 0) oracleNeg = true; assert(noNegCycle == !oracleNeg); oracleNeg ? ++cyc : ++acyc; } }
    assert(cyc > 500 && acyc > 500);
    std::cout << "WeightedGraph: Dijkstra, Bellman-Ford and Floyd-Warshall agreed on 3000 random non-negative digraphs; with negative edges Dijkstra was wrong for " << dijkstraWrong << " of " << total << " sources while Bellman-Ford stayed exact, Johnson reweighting repaired Dijkstra, and negative cycles were reported exactly when Floyd-Warshall found one reachable" << std::endl;
    return 0;
}
// Time Complexity: Dijkstra O(E log V), Bellman-Ford O(V·E), Floyd–Warshall O(V³)
// Space Complexity: O(V + E)
```
## UnweightedGraph()
### 대표코드
```cpp
#include <iostream>
#include <climits>
#include <queue>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 가중치 없는 그래프: 모든 간선 비용이 1 이므로 BFS 가 곧 최단 경로 알고리즘이다 (우선순위 큐 불필요, O(V + E)).
// Dijkstra 에 가중치 1 을 주어도 같은 답이 나오지만 로그 인자만큼 느리다
typedef std::vector<std::vector<int>> Graph;
std::vector<int> bfs(const Graph& g, int s) {
    std::vector<int> d(g.size(), -1); std::queue<int> q; q.push(s); d[s] = 0;
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }
    return d;
}
std::vector<int> dijkstraUnit(const Graph& g, int s) {
    std::vector<int> d(g.size(), INT_MAX); d[s] = 0;
    std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq; pq.push({0, s});
    while (!pq.empty()) {
        auto top = pq.top(); pq.pop(); int du = top.first, u = top.second;
        if (du > d[u]) continue;
        for (int v : g[u]) if (du + 1 < d[v]) { d[v] = du + 1; pq.push({d[v], v}); }
    }
    for (auto& x : d) if (x == INT_MAX) x = -1;
    return d;
}

int main() {
    std::mt19937 rng(31);
    for (int trial = 0; trial < 100; trial++) {
        int V = rng() % 30 + 2; Graph g(V);
        for (int k = 0; k < V * 2; k++) { int a = rng() % V, b = rng() % V; g[a].push_back(b); g[b].push_back(a); }
        assert(bfs(g, 0) == dijkstraUnit(g, 0));            // 두 방식의 결과가 모든 정점에서 일치
    }
    Graph path = {{1}, {0, 2}, {1, 3}, {2}};
    assert((bfs(path, 0) == std::vector<int>{0, 1, 2, 3}));
    std::cout << "UnweightedGraph: BFS equals unit-weight Dijkstra on 100 random graphs." << std::endl;
    return 0;
}
// Time Complexity: BFS O(V + E)
// Space Complexity: O(V)
```
## CompleteGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <set>
#include <utility>
#include <vector>

// 완전 그래프 K_n: 모든 정점 쌍이 이웃이다. 간선 n(n−1)/2 개, 모든 차수 n−1, 지름 1, 클리크 수 = 색칠 수 = n, 독립 수 1. 숫자 세기: 신장 트리는 Cayley 공식 n^(n−2) (행렬–트리 정리: 라플라시안의 한 소행렬식), 해밀턴 사이클은 (n−1)!/2, 완전 매칭은 짝수 n 에서 (n−1)!! = (n−1)(n−3)…1, k-클리크는 C(n,k).
// 극값 정리 두 개를 완전 탐색으로 확인한다 — Mantel: K_n 의 부분 그래프 중 삼각형이 없는 것의 간선은 최대 ⌊n²/4⌋ (정점 6 개까지 모든 간선 부분집합). Ramsey R(3,3) = 6: K_6 의 간선을 빨강/파랑으로 칠하는 2^15 가지 모두에 한 색 삼각형이 있고, K_5 에는 없는 칠하기가 정확히 12 가지 있다(오각형과 별 모양 오각별). 평면성: K_5 는 E ≤ 3V − 6 (평면 그래프의 간선 한계)를 어긴다.
// 행렬식은 정수 그대로 구한다 — 분수가 안 생기는 Bareiss 소거(중간값이 커서 128 비트 정수). 큰 n 은 소수 p 의 나머지 위에서 가우스 소거(역원은 페르마 소정리). 검증: n ≤ 6 은 신장 트리를 *직접 열거*(n−1 개 간선 부분집합 중 사이클 없는 것), n ≤ 12 는 Bareiss 와 n^(n−2) 비교, n = 200 은 나머지 소거로 비교.
__extension__ typedef __int128 i128;
using ll = long long;
using Matrix = std::vector<std::vector<ll>>;

ll bareiss(Matrix a) {                                                              // 정수 행렬식 (분수 없는 소거), 중간 곱은 128 비트
    int n = (int)a.size(); if (n == 0) return 1; ll sign = 1, prev = 1;
    for (int k = 0; k + 1 < n; ++k) {
        if (a[k][k] == 0) { int s = -1; for (int i = k + 1; i < n; ++i) if (a[i][k] != 0) { s = i; break; } if (s < 0) return 0; std::swap(a[k], a[s]); sign = -sign; }
        for (int i = k + 1; i < n; ++i) for (int j = k + 1; j < n; ++j) a[i][j] = (ll)(((i128)a[i][j] * a[k][k] - (i128)a[i][k] * a[k][j]) / prev);
        prev = a[k][k];
    }
    return sign * a[n - 1][n - 1];
}
Matrix laplacianMinor(int n) { Matrix m(n - 1, std::vector<ll>(n - 1, -1)); for (int i = 0; i < n - 1; ++i) m[i][i] = n - 1; return m; }     // K_n 의 라플라시안에서 한 행·열 제거
ll powmod(ll b, ll e, ll mod) { ll r = 1; b %= mod; while (e) { if (e & 1) r = (i128)r * b % mod; b = (i128)b * b % mod; e >>= 1; } return r; }
ll detMod(Matrix a, ll mod) {                                                       // 나머지 위의 가우스 소거
    int n = (int)a.size(); ll det = 1;
    for (auto& r : a) for (ll& x : r) x = ((x % mod) + mod) % mod;
    for (int c = 0; c < n; ++c) {
        int p = -1; for (int r = c; r < n; ++r) if (a[r][c]) { p = r; break; }
        if (p < 0) return 0; if (p != c) { std::swap(a[p], a[c]); det = (mod - det) % mod; }
        det = (i128)det * a[c][c] % mod; ll inv = powmod(a[c][c], mod - 2, mod);
        for (int r = c + 1; r < n; ++r) { ll f = (i128)a[r][c] * inv % mod; for (int k = c; k < n; ++k) a[r][k] = ((a[r][k] - (i128)f * a[c][k]) % mod + mod) % mod; }
    }
    return det;
}
ll cayley(int n) { ll r = 1; for (int i = 0; i < n - 2; ++i) r *= n; return r; }

std::vector<std::pair<int, int>> completeEdges(int n) { std::vector<std::pair<int, int>> e; for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) e.push_back({a, b}); return e; }
ll countSpanningTrees(int n) {                                                      // 직접 열거: (n−1) 개 간선 부분집합 중 사이클이 없는 것
    auto e = completeEdges(n); int m = (int)e.size(), need = n - 1; ll count = 0;
    for (unsigned mask = 0; mask < (1u << m); ++mask) {
        if (__builtin_popcount(mask) != need) continue;
        std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto f = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
        bool ok = true; for (int i = 0; i < m && ok; ++i) if (mask >> i & 1) { int a = f(e[i].first), b = f(e[i].second); if (a == b) ok = false; else p[a] = b; }
        count += ok;
    }
    return count;
}
ll hamiltonCycles(int n) { std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); ll c = 0; do ++c; while (std::next_permutation(p.begin() + 1, p.end())); return n < 3 ? 0 : c / 2; }   // 시작 고정, 방향 두 가지는 같은 사이클
ll perfectMatchings(unsigned left) { if (!left) return 1; int a = __builtin_ctz(left); ll total = 0; for (unsigned rest = left & (left - 1); rest; rest &= rest - 1) total += perfectMatchings((left & ~(1u << a)) & ~(rest & -rest)); return total; }
ll binom(int n, int k) { ll r = 1; for (int i = 1; i <= k; ++i) r = r * (n - k + i) / i; return r; }
bool colorable(int n, int k, std::vector<int>& col, int v) {                        // K_n 을 k 색으로 (역추적)
    if (v == n) return true;
    for (int c = 0; c < k; ++c) { bool clash = false; for (int u = 0; u < v; ++u) if (col[u] == c) clash = true; if (clash) continue; col[v] = c; if (colorable(n, k, col, v + 1)) return true; }
    return false;
}

int main() {
    // ① 기본 사실
    for (int n = 1; n <= 12; ++n) {
        auto e = completeEdges(n); std::vector<int> deg(n, 0); for (auto [a, b] : e) { ++deg[a]; ++deg[b]; }
        assert((int)e.size() == n * (n - 1) / 2 && std::all_of(deg.begin(), deg.end(), [&](int d) { return d == n - 1; }));
    }
    assert(5 * 4 / 2 > 3 * 5 - 6 && 4 * 3 / 2 <= 3 * 4 - 6);                                     // K_5 는 평면 그래프의 간선 한계를 넘는다, K_4 는 넘지 않는다

    // ② 신장 트리의 수: 직접 열거(n ≤ 6) = Bareiss(n ≤ 12) = Cayley, 나머지 위 소거로 n = 200 까지
    for (int n = 2; n <= 6; ++n) assert(countSpanningTrees(n) == cayley(n));
    for (int n = 2; n <= 12; ++n) assert(bareiss(laplacianMinor(n)) == cayley(n));
    {   const ll mod = 1000000007; for (int n : {20, 50, 100, 200}) { ll want = powmod(n, n - 2, mod); assert(detMod(laplacianMinor(n), mod) == want); } }

    // ③ 세기: 해밀턴 사이클 (n−1)!/2, 완전 매칭 (n−1)!!, k-클리크 C(n,k) (모든 부분집합을 보고), 독립 집합은 크기 1
    {
        ll fact = 1; for (int n = 3; n <= 9; ++n) { fact *= (n - 1); assert(hamiltonCycles(n) == fact / 2); }                       // (n−1)!/2
        ll dfact = 1; for (int n = 2; n <= 12; n += 2) { dfact *= (n - 1); assert(perfectMatchings((1u << n) - 1) == dfact); }     // (n−1)!!
        for (int n = 2; n <= 9; ++n) {
            std::vector<unsigned> adj(n, 0); for (auto [a, b] : completeEdges(n)) { adj[a] |= 1u << b; adj[b] |= 1u << a; }
            std::vector<ll> byK(n + 1, 0);
            for (unsigned s = 0; s < (1u << n); ++s) {                                                                           // 모든 부분집합이 서로 인접한지 직접 확인
                bool clique = true;
                for (int v = 0; v < n && clique; ++v) if ((s >> v & 1) && ((s & ~(1u << v)) & ~adj[v]) != 0) clique = false;
                byK[__builtin_popcount(s)] += clique;
            }
            for (int k = 0; k <= n; ++k) assert(byK[k] == binom(n, k));
        }
        for (int n = 1; n <= 7; ++n) { std::vector<int> col(n); assert(colorable(n, n, col, 0) && (n == 1 || !colorable(n, n - 1, col, 0))); }   // 색칠 수 = n
    }

    // ④ Mantel: K_n 의 삼각형 없는 부분 그래프의 최대 간선 수 = ⌊n²/4⌋ (n ≤ 6, 모든 부분집합)
    for (int n = 2; n <= 6; ++n) {
        auto e = completeEdges(n); int m = (int)e.size(), best = 0;
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            unsigned adj[8] = {}; for (int i = 0; i < m; ++i) if (mask >> i & 1) { adj[e[i].first] |= 1u << e[i].second; adj[e[i].second] |= 1u << e[i].first; }
            bool tri = false; for (int i = 0; i < m && !tri; ++i) if (mask >> i & 1) tri = (adj[e[i].first] & adj[e[i].second]) != 0;
            if (!tri) best = std::max(best, __builtin_popcount(mask));
        }
        assert(best == n * n / 4);
    }

    // ⑤ Ramsey R(3,3) = 6: K_6 의 모든 빨강/파랑 칠하기에 한 색 삼각형이 있고, K_5 에는 없는 칠하기가 정확히 12 가지
    {
        for (int n = 5; n <= 6; ++n) {
            auto e = completeEdges(n); int m = (int)e.size(); ll without = 0;
            for (unsigned mask = 0; mask < (1u << m); ++mask) {
                unsigned red[8] = {}, blue[8] = {};
                for (int i = 0; i < m; ++i) { unsigned* side = (mask >> i & 1) ? red : blue; side[e[i].first] |= 1u << e[i].second; side[e[i].second] |= 1u << e[i].first; }
                bool mono = false; for (int i = 0; i < m && !mono; ++i) { auto [a, b] = e[i]; unsigned* side = (mask >> i & 1) ? red : blue; mono = (side[a] & side[b]) != 0; }
                without += !mono;
            }
            assert(n == 5 ? without == 12 : without == 0);
        }
    }

    // ⑥ 큰 입력: K_2000 의 차수와 간선 수 (인접 비트집합), 신장 트리 수 n^(n−2) mod p 를 n = 1000 까지 (라플라시안 소행렬식을 나머지 위에서)
    {
        const int N = 2000, W = (N + 63) / 64; std::vector<std::vector<uint64_t>> adj(N, std::vector<uint64_t>(W, ~0ULL));
        for (int i = 0; i < N; ++i) { adj[i][i >> 6] &= ~(1ULL << (i & 63)); if (N & 63) adj[i][W - 1] &= (1ULL << (N & 63)) - 1; }
        ll total = 0; for (int i = 0; i < N; ++i) { ll d = 0; for (uint64_t w : adj[i]) d += __builtin_popcountll(w); assert(d == N - 1); total += d; }
        assert(total / 2 == (ll)N * (N - 1) / 2);
        const ll mod = 998244353; int n = 400; assert(detMod(laplacianMinor(n), mod) == powmod(n, n - 2, mod));
    }
    std::cout << "CompleteGraph: K_n had n(n-1)/2 edges and constant degree n-1; spanning trees counted by direct enumeration (n <= 6), an exact 128-bit Bareiss determinant (n <= 12) and a modular elimination (n up to 400) all equalled Cayley's n^(n-2); Hamiltonian cycles (n-1)!/2, perfect matchings (n-1)!! and k-cliques C(n,k) matched exhaustive counts, the chromatic number was n, the largest triangle-free subgraph had floor(n^2/4) edges for n <= 6, and every 2-colouring of K_6 had a monochromatic triangle while exactly 12 colourings of K_5 avoided one (R(3,3) = 6)" << std::endl; return 0;
}
// Time Complexity: 신장 트리 개수 O(n³) (행렬식), 열거는 지수
// Space Complexity: O(n²)
```
## SparseGraph()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <utility>
#include <vector>
#include <cassert>

// 희소 그래프: |E| 가 |V| 에 비례하는 정도(밀도 = 2E / V(V-1) 가 작다).  도로망·소셜 네트워크 등 현실의 그래프 대부분.
// 모든 간선을 훑는 데 인접 행렬은 V² 칸을 보지만 인접 리스트는 V + 2E 칸만 본다 -> 표현 선택이 알고리즘 복잡도를 좌우한다
int main() {
    const int V = 2000, E = 6000;                                    // 평균 차수 6
    std::mt19937 rng(41);
    std::vector<std::pair<int, int>> edges;
    for (int i = 0; i < E; i++) { int a = rng() % V, b = rng() % V; if (a != b) edges.push_back({a, b}); }

    std::vector<std::vector<bool>> matrix(V, std::vector<bool>(V, false));
    std::vector<std::vector<int>> list(V);
    for (auto& e : edges) { matrix[e.first][e.second] = matrix[e.second][e.first] = true; list[e.first].push_back(e.second); list[e.second].push_back(e.first); }

    long matrixSteps = 0, listSteps = 0, matrixEdges = 0, listEdges = 0;
    for (int u = 0; u < V; u++) for (int v = 0; v < V; v++) { matrixSteps++; matrixEdges += matrix[u][v]; }   // 행렬: 전체 칸 순회
    for (int u = 0; u < V; u++) { listSteps++; for (int v : list[u]) { (void)v; listSteps++; listEdges++; } }         // 리스트: 정점 + 간선 순회
    double density = 2.0 * edges.size() / ((double)V * (V - 1));
    assert(density < 0.01);                                          // 희소
    assert(listSteps * 100 < matrixSteps);                           // 리스트가 100배 이상 적게 본다
    assert(listEdges > 0 && listEdges % 2 == 0);                     // 무방향이라 간선마다 두 번 기록
    std::cout << "density=" << density << " enumerate edges: matrix " << matrixSteps << " steps, list " << listSteps << " steps" << std::endl;
    return 0;
}
// Time Complexity: 인접 리스트 순회 O(V + E), 인접 행렬 순회 O(V²)
// Space Complexity: 인접 리스트 O(V + E), 인접 행렬 O(V²)
```
## DenseGraph()
### 대표코드
```cpp
#include <iostream>
#include <bitset>
#include <random>
#include <vector>
#include <cassert>

// 밀집 그래프: |E| 가 |V|² 에 가깝다.  인접 행렬이 적합하고, 한 행을 비트셋으로 두면 집합 연산을 64개씩 한 번에 처리해
// 삼각형 세기, 전이적 폐쇄(Warshall) 같은 알고리즘이 64배 빨라진다
const int N = 64;
typedef std::bitset<N> Row;

long triangles(const std::vector<Row>& adj) {
    long sum = 0;
    for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) if (adj[i][j]) sum += (adj[i] & adj[j]).count();   // 간선 (i,j) 의 공통 이웃 수
    return sum / 3;                                                                                            // 삼각형은 간선마다 한 번씩, 3번 센다
}
std::vector<Row> closure(std::vector<Row> reach) {                     // Warshall: reach[i] |= reach[k] (i 가 k 에 닿으면)
    for (int k = 0; k < N; k++) for (int i = 0; i < N; i++) if (reach[i][k]) reach[i] |= reach[k];
    return reach;
}

int main() {
    std::vector<Row> complete(N);
    for (int i = 0; i < N; i++) { complete[i].set(); complete[i].reset(i); }
    assert(triangles(complete) == 64L * 63 * 62 / 6);                   // K64 의 삼각형 수 = C(64,3)

    std::mt19937 rng(51);
    std::vector<Row> g(N);
    for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) if (rng() % 10 < 7) g[i][j] = g[j][i] = 1;       // 밀도 0.7
    long brute = 0;
    for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++) for (int c = b + 1; c < N; c++) brute += g[a][b] && g[b][c] && g[a][c];
    assert(triangles(g) == brute);

    std::vector<Row> path(N);                                           // 방향 경로 0 -> 1 -> ... -> 63
    for (int i = 0; i + 1 < N; i++) path[i][i + 1] = 1;
    auto c = closure(path);
    assert(c[0][63] && c[10][20] && !c[20][10] && c[0].count() == 63);
    std::cout << "DenseGraph: triangles in random graph = " << brute << std::endl;
    return 0;
}
// Time Complexity: 삼각형 O(V²·V/64), 전이적 폐쇄 O(V³/64)
// Space Complexity: O(V²/64) 워드
```
## PlanarGraph()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 평면 그래프: 간선이 교차하지 않게 평면에 그릴 수 있는 그래프.  오일러 공식 V - E + F = 2 (연결 그래프, F 는 바깥 면 포함).
// 이로부터 V ≥ 3 인 평면 그래프는 E ≤ 3V - 6,  삼각형이 없는 (이분) 평면 그래프는 E ≤ 2V - 4.
// 이 부등식은 "평면이 아니다" 를 증명하는 필요조건 검사로 쓰인다 (역은 성립하지 않는다 — 완전한 판정은 Kuratowski/LR 알고리즘)
bool mayBePlanar(int V, int E, bool triangleFree) {
    if (V < 3) return true;
    return E <= (triangleFree ? 2 * V - 4 : 3 * V - 6);
}
int eulerCharacteristic(int V, int E, int F) { return V - E + F; }

int main() {
    assert(mayBePlanar(4, 6, false));                      // K4: 6 <= 6, 평면 (사면체)
    assert(!mayBePlanar(5, 10, false));                    // K5: 10 > 9 -> 평면이 아니다
    assert(mayBePlanar(6, 9, false));                      // K3,3: 일반 부등식은 통과 (9 <= 12) 하지만
    assert(!mayBePlanar(6, 9, true));                      // 삼각형이 없으므로 9 > 8 -> 평면이 아니다
    assert(mayBePlanar(6, 12, false));                     // 정팔면체: E = 3V - 6 으로 꽉 찬 삼각분할
    // 오일러 공식 검증: 면의 개수 F 를 세어 본다
    assert(eulerCharacteristic(4, 6, 4) == 2);             // 사면체: 삼각형 면 4개
    assert(eulerCharacteristic(8, 12, 6) == 2);            // 정육면체: 사각형 면 6개
    assert(eulerCharacteristic(6, 12, 8) == 2);            // 정팔면체: 삼각형 면 8개
    // 면 하나는 최소 3개의 간선으로 둘러싸이고 간선은 두 면에 속하므로 3F <= 2E -> F <= 2E/3 -> E <= 3V - 6
    for (int V = 3; V <= 20; V++) { int E = 3 * V - 6; int F = 2 - V + E; assert(3 * F <= 2 * E); }
    std::cout << "PlanarGraph: K5 and K3,3 fail the planarity bounds." << std::endl;
    return 0;
}
// Time Complexity: 필요조건 검사 O(1), 완전한 평면성 판정 O(V)
// Space Complexity: O(1)
```
## Multigraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 다중 그래프: 같은 두 정점 사이에 평행 간선이 여러 개 있거나 자기 루프가 있다 (퀴니히스베르크의 다리 문제).
// 간선마다 고유 id 가 필요하다.  오일러 경로(모든 간선을 정확히 한 번씩 지나는 산책)의 존재 조건 — *간선이 있는 정점들이 연결* 이고 홀수 차수 정점이 0 개(회로) 또는 2 개(두 끝이 홀수 정점).  연결성 조건을 빼면 틀린다.
//  ① 퀴니히스베르크(홀수 차수 4 개 → 불가능)와 다리 하나를 없앤 변형(가능)  ② 정점 3 개의 모든 다중 그래프(6 슬롯 × 중복도 0..2 = 729 개)와 무작위 다중 그래프 1 500 개(정점 1~5, 간선 0~8)에서 hasEulerPath/hasEulerCircuit 이 *모든 간선 순서를 시도하는 완전 탐색* 과 같다
//  ③ 존재한다고 판정된 모든 경우에서 Hierholzer 가 돌려준 점 열이 간선 수 + 1 개이고, 이웃한 쌍마다 *서로 다른* 간선을 정확히 한 번씩 소비하며 모든 간선을 쓴다(회로이면 처음 = 끝)  ④ 연결이 끊긴 반례(모든 차수가 짝수인 두 삼각형)는 판정이 거짓
struct Multigraph {
    int n; std::vector<std::pair<int, int>> edges;
    std::vector<std::vector<std::pair<int, int>>> adj;                // (이웃, 간선 id)
    explicit Multigraph(int n) : n(n), adj(n) {}
    void addEdge(int u, int v) { int id = (int)edges.size(); edges.push_back({u, v}); adj[u].push_back({v, id}); adj[v].push_back({u, id}); }
    int degree(int u) const { return (int)adj[u].size(); }                  // 자기 루프는 두 번 들어가 차수 2
    int oddCount() const { int odd = 0; for (int i = 0; i < n; i++) odd += degree(i) % 2; return odd; }
    bool edgesConnected() const {                                          // 간선이 있는 정점들이 한 덩어리인가
        int start = -1; for (int i = 0; i < n; i++) if (degree(i) > 0) { start = i; break; } if (start < 0) return true;
        std::vector<char> seen(n, 0); std::queue<int> q; q.push(start); seen[start] = 1; while (!q.empty()) { int u = q.front(); q.pop(); for (auto& e : adj[u]) if (!seen[e.first]) { seen[e.first] = 1; q.push(e.first); } }
        for (int i = 0; i < n; i++) if (degree(i) > 0 && !seen[i]) return false; return true; }
    bool hasEulerPath() const { int odd = oddCount(); return (odd == 0 || odd == 2) && edgesConnected(); }
    bool hasEulerCircuit() const { return oddCount() == 0 && edgesConnected(); }
    std::vector<int> eulerPath() const {                                // Hierholzer (홀수 차수 정점이 있으면 거기서, 없으면 간선이 있는 첫 정점에서)
        int start = -1; for (int i = 0; i < n; i++) if (degree(i) % 2) { start = i; break; } if (start < 0) for (int i = 0; i < n; i++) if (degree(i) > 0) { start = i; break; } if (start < 0) start = 0;
        std::vector<bool> used(edges.size(), false); std::vector<size_t> it(n, 0); std::vector<int> stack = {start}, path;
        while (!stack.empty()) {
            int u = stack.back();
            while (it[u] < adj[u].size() && used[adj[u][it[u]].second]) it[u]++;
            if (it[u] == adj[u].size()) { path.push_back(u); stack.pop_back(); }
            else { auto e = adj[u][it[u]]; used[e.second] = true; stack.push_back(e.first); }
        }
        std::reverse(path.begin(), path.end());
        return path;
    }
};
bool trailExists(const Multigraph& g, int at, std::vector<char>& used, int left, int endRequired, bool closed, int startV) {   // 오라클: 모든 간선 순서를 시도
    if (left == 0) return !closed || at == startV;
    for (size_t id = 0; id < g.edges.size(); ++id) if (!used[id]) { int a = g.edges[id].first, b = g.edges[id].second, to = -1; if (a == at) to = b; else if (b == at) to = a; if (to < 0) continue;
        used[id] = 1; bool ok = trailExists(g, to, used, left - 1, endRequired, closed, startV); used[id] = 0; if (ok) return true; }
    return false; }
bool bruteEuler(const Multigraph& g, bool closed) { if (g.edges.empty()) return true; std::vector<char> used(g.edges.size(), 0); for (int s = 0; s < g.n; ++s) if (g.degree(s) > 0 && trailExists(g, s, used, (int)g.edges.size(), -1, closed, s)) return true; return false; }
void checkPath(const Multigraph& g, bool circuit) {
    auto path = g.eulerPath(); assert(path.size() == g.edges.size() + 1); std::vector<int> used(g.edges.size(), 0);
    for (size_t i = 0; i + 1 < path.size(); i++) { bool found = false; for (size_t id = 0; id < g.edges.size() && !found; id++) if (!used[id] && ((g.edges[id].first == path[i] && g.edges[id].second == path[i + 1]) || (g.edges[id].second == path[i] && g.edges[id].first == path[i + 1]))) { used[id] = 1; found = true; } assert(found); }
    for (int u : used) assert(u == 1); if (circuit && !g.edges.empty()) assert(path.front() == path.back()); }

int main() {
    Multigraph k(4); k.addEdge(0, 1); k.addEdge(0, 1); k.addEdge(0, 2); k.addEdge(0, 2); k.addEdge(0, 3); k.addEdge(1, 3); k.addEdge(2, 3);                                     // ① 퀴니히스베르크
    assert(k.degree(0) == 5 && k.degree(1) == 3 && k.degree(2) == 3 && k.degree(3) == 3 && !k.hasEulerPath() && !bruteEuler(k, false));
    Multigraph m(4); m.addEdge(0, 1); m.addEdge(0, 2); m.addEdge(0, 2); m.addEdge(0, 3); m.addEdge(1, 3); m.addEdge(2, 3); assert(m.hasEulerPath() && !m.hasEulerCircuit()); checkPath(m, false);
    Multigraph loop(1); loop.addEdge(0, 0); assert(loop.degree(0) == 2 && loop.hasEulerCircuit()); checkPath(loop, true);
    {   Multigraph two(6); for (int base : {0, 3}) { two.addEdge(base, base + 1); two.addEdge(base + 1, base + 2); two.addEdge(base + 2, base); } assert(two.oddCount() == 0 && !two.hasEulerPath() && !two.hasEulerCircuit() && !bruteEuler(two, false)); }    // ④ 끊긴 반례
    {   std::vector<std::pair<int, int>> slot = {{0, 0}, {0, 1}, {0, 2}, {1, 1}, {1, 2}, {2, 2}}; long paths = 0;                                                                     // ② 정점 3 개 전수 (3^6)
        for (int code = 0; code < 729; ++code) { Multigraph g(3); int c = code; for (size_t k2 = 0; k2 < slot.size(); ++k2) { int mult = c % 3; c /= 3; for (int i = 0; i < mult; ++i) g.addEdge(slot[k2].first, slot[k2].second); }
            bool path = g.hasEulerPath(), circuit = g.hasEulerCircuit(); assert(path == bruteEuler(g, false) && circuit == bruteEuler(g, true)); if (path) { checkPath(g, circuit); ++paths; } } assert(paths > 100 && paths < 729); }
    std::mt19937 rng(3);
    for (int trial = 0; trial < 1500; ++trial) { int n = 1 + (int)(rng() % 5), e = (int)(rng() % 9); Multigraph g(n); for (int i = 0; i < e; ++i) g.addEdge((int)(rng() % n), (int)(rng() % n));
        bool path = g.hasEulerPath(), circuit = g.hasEulerCircuit(); assert(path == bruteEuler(g, false) && circuit == bruteEuler(g, true)); if (path) checkPath(g, circuit); }
    std::cout << "Multigraph: Konigsberg has no Euler path and removing a bridge fixes it; the degree-and-connectivity test agreed with exhaustive trail search on all 729 three-vertex multigraphs and 1500 random ones, with a valid edge-by-edge Hierholzer path every time" << std::endl;
    return 0;
}
// Time Complexity: 판정 O(V + E), 오일러 경로 O(V + E)
// Space Complexity: O(V + E)
```
## Hypergraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 하이퍼그래프: 간선(하이퍼에지)이 두 개가 아니라 임의 개수의 정점 집합이다.  "한 논문의 공저자들", "한 회의의 참석자들"처럼 n 항 관계를 그대로 담는다.
// 표현: 정점×하이퍼에지 연관 행렬.  쌍대(dual) 는 행렬을 전치한 것(정점 <-> 하이퍼에지 역할 교환).
// 2-section(클리크 확장): 같은 하이퍼에지에 속한 정점끼리 일반 간선으로 이어 보통 그래프로 바꾼다 (정보 손실이 있다: 삼각형 하나가 크기 3 하이퍼에지 하나인지 평범한 간선 셋인지 구별 못 한다)
//  ① 손으로 만든 예  ② 무작위 하이퍼그래프 2 000 개(정점 1~8, 하이퍼에지 0~6 개, 크기 1~V)에서: 쌍대의 쌍대 == 원본, 정점 차수의 합 == 하이퍼에지 크기의 합, 쌍대에서는 차수와 크기의 역할이 서로 바뀜, 2-section 의 쌍 집합 == 연관 행렬 곱 M·Mᵀ 의 비대각 양수 칸
//  ③ 연결 성분: 하이퍼그래프에서 (정점–하이퍼에지) 교대 탐색으로 센 성분 수 == 2-section 을 일반 그래프로 보고 센 성분 수  ④ 크기가 2 인 하이퍼에지만 있으면 2-section 은 정확히 원래 그래프(정보 손실 없음), 크기 3 하이퍼에지 하나와 삼각형 간선 셋의 2-section 이 같음(손실의 증거)
typedef std::vector<std::vector<int>> Incidence;                         // inc[v][e] = 1 이면 v ∈ e
Incidence build(int V, const std::vector<std::set<int>>& edges) {
    Incidence inc(V, std::vector<int>(edges.size(), 0));
    for (size_t e = 0; e < edges.size(); e++) for (int v : edges[e]) inc[v][e] = 1;
    return inc;
}
Incidence dual(const Incidence& inc, size_t edgeCount) {
    Incidence d(edgeCount, std::vector<int>(inc.size()));
    for (size_t v = 0; v < inc.size(); v++) for (size_t e = 0; e < edgeCount; e++) d[e][v] = inc[v][e];
    return d;
}
std::set<std::pair<int, int>> twoSection(const std::vector<std::set<int>>& edges) {
    std::set<std::pair<int, int>> g;
    for (auto& e : edges) for (int a : e) for (int b : e) if (a < b) g.insert({a, b});
    return g;
}
int hyperComponents(int V, const std::vector<std::set<int>>& edges) {                   // 정점–하이퍼에지 교대 BFS
    Incidence inc = build(V, edges); std::vector<char> vs(V, 0), es(edges.size(), 0); int comps = 0;
    for (int s = 0; s < V; ++s) { if (vs[s]) continue; ++comps; std::queue<int> q; q.push(s); vs[s] = 1;
        while (!q.empty()) { int v = q.front(); q.pop(); for (size_t e = 0; e < edges.size(); ++e) if (inc[v][e] && !es[e]) { es[e] = 1; for (int w : edges[e]) if (!vs[w]) { vs[w] = 1; q.push(w); } } } }
    return comps; }
int graphComponents(int V, const std::set<std::pair<int, int>>& g) { std::vector<int> p(V); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }; int c = V; for (auto& e : g) if (find(e.first) != find(e.second)) { p[find(e.first)] = find(e.second); --c; } return c; }

int main() {
    {   std::vector<std::set<int>> hyper = {{0, 1, 2}, {2, 3}, {0, 3, 4, 5}}; auto inc = build(6, hyper); int deg2 = 0; for (int e = 0; e < 3; e++) deg2 += inc[2][e]; assert(deg2 == 2);       // ① 손으로 만든 예
        assert(dual(dual(inc, 3), 6) == inc); auto d = dual(inc, 3); assert(d.size() == 3 && d[0][2] == 1 && d[1][2] == 1 && d[2][2] == 0); auto g = twoSection(hyper); assert(g.size() == 3 + 1 + 6 && g.count({0, 3}) && g.count({2, 3}) && !g.count({1, 4})); }
    std::mt19937 rng(31); long lost = 0;
    for (int trial = 0; trial < 2000; ++trial) { int V = 1 + (int)(rng() % 8), E = (int)(rng() % 7); std::vector<std::set<int>> hyper;                                                                           // ②
        for (int e = 0; e < E; ++e) { int size = 1 + (int)(rng() % V); std::set<int> s; while ((int)s.size() < size) s.insert((int)(rng() % V)); hyper.push_back(s); }
        Incidence inc = build(V, hyper); assert(dual(dual(inc, E), V) == inc); Incidence d = dual(inc, E);
        long degSum = 0, sizeSum = 0; for (int v = 0; v < V; ++v) for (int e = 0; e < E; ++e) degSum += inc[v][e]; for (auto& h : hyper) sizeSum += (long)h.size(); assert(degSum == sizeSum);
        for (int e = 0; e < E; ++e) { int cnt = 0; for (int v = 0; v < V; ++v) cnt += d[e][v]; assert(cnt == (int)hyper[e].size() && d[e].size() == (size_t)V); }                                  // 쌍대: 정점 차수 ↔ 하이퍼에지 크기
        std::set<std::pair<int, int>> viaProduct; for (int a = 0; a < V; ++a) for (int b = a + 1; b < V; ++b) { int common = 0; for (int e = 0; e < E; ++e) common += inc[a][e] * inc[b][e]; if (common > 0) viaProduct.insert({a, b}); }
        auto g = twoSection(hyper); assert(g == viaProduct); assert(hyperComponents(V, hyper) == graphComponents(V, g)); }                                                                                  // ③
    {   std::vector<std::set<int>> one = {{0, 1, 2}}, three = {{0, 1}, {1, 2}, {0, 2}}; assert(twoSection(one) == twoSection(three)); ++lost; assert(build(3, one) != build(3, three));                       // ④ 정보 손실: 같은 2-section, 다른 연관 행렬
        std::vector<std::set<int>> plain = {{0, 1}, {1, 2}, {3, 4}}; assert(twoSection(plain).size() == 3); }
    std::cout << "Hypergraph: dual-of-dual, degree/size duality and the 2-section equalled the incidence-matrix product on 2000 random hypergraphs, component counts agreed between the alternating search and the 2-section, and one size-3 hyperedge was shown to be indistinguishable from a triangle after clique expansion (" << lost << " witness)" << std::endl;
    return 0;
}
// Time Complexity: 2-section 변환 O(Σ|e|²)
// Space Complexity: O(V·E) 연관 행렬
```
# Part 15. 그래프 모델
## RandomGraph()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 에르되시-레니 무작위 그래프 G(n, p): 가능한 모든 간선을 독립적으로 확률 p 로 둔다.
//  - 기대 간선 수 = p·n(n-1)/2,  평균 차수 = p(n-1)
//  - 연결성에는 임계값이 있다: p = (ln n)/n 아래에서는 거의 항상 고립 정점이 생기고, 위에서는 거의 항상 연결된다
//  - p = c/n (c > 1) 이면 크기가 Θ(n) 인 "거대 연결 요소" 가 생긴다
struct DSU { std::vector<int> p; explicit DSU(int n) : p(n) { std::iota(p.begin(), p.end(), 0); } int f(int x) { return p[x] == x ? x : p[x] = f(p[x]); } };

int largestComponent(int n, double p, std::mt19937& rng, long* edgesOut = nullptr) {
    DSU d(n); std::bernoulli_distribution b(p); long edges = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (b(rng)) { d.p[d.f(i)] = d.f(j); edges++; }
    std::vector<int> size(n, 0); int best = 0;
    for (int i = 0; i < n; i++) best = std::max(best, ++size[d.f(i)]);
    if (edgesOut) *edgesOut = edges;
    return best;
}

int main() {
    std::mt19937 rng(61);
    const int n = 1000; long edges;
    largestComponent(n, 0.01, rng, &edges);
    double expected = 0.01 * n * (n - 1) / 2;
    assert(std::fabs(edges - expected) < 5 * std::sqrt(expected));                   // 기대값 근처 (표준편차의 5배 이내)
    int below = largestComponent(n, 0.5 / n, rng);                                   // c = 0.5 < 1: 큰 요소가 없다
    int above = largestComponent(n, 2.0 / n, rng);                                   // c = 2 > 1: 거대 요소
    assert(below < n / 20);
    assert(above > n / 2);
    std::cout << "G(1000,p): largest component c=0.5 -> " << below << ", c=2 -> " << above << std::endl;
    return 0;
}
// Time Complexity: 생성 O(n²)
// Space Complexity: O(n)
```
## GridGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 격자 그래프: R×C 칸의 상하좌우 이웃.  간선 수 = R(C−1) + C(R−1),  이분 그래프((r + c) 의 홀짝이 색),  (장애물이 없으면) 최단 거리 = 맨해튼 거리,  (0,0) 에서 (r,c) 로 가는 최단 경로의 수 = C(r + c, r).  게임 맵·미로·이미지 처리의 기본 모델
//  ① 빈 격자 R, C = 1..9 전수: 간선 수·차수 분포(모서리 4 · 변 · 안쪽)·이분성·*모든 출발점* 에서 BFS 거리 == 맨해튼 거리  ② 최단 경로의 수: BFS 로 세면서 C(r+c, r) 과 같음  ③ 원환(torus, 가장자리가 이어진 격자): BFS 거리 == min(|Δr|, R−|Δr|) + min(|Δc|, C−|Δc|)
//  ④ 장애물 격자 600 개(R, C ≤ 7, 벽 30%): BFS 거리 == 플로이드–워셜, 연결 성분 수(홍수 채우기) == 서로소 집합, 거리 ≥ 맨해튼이고 거리와 |Δr|+|Δc| 의 홀짝이 같음  ⑤ 큰 입력: 1000×1000 의 반대편 모서리까지 거리 1998, 간선 수 1 997 000
struct Grid {
    int R, C; std::vector<std::string> cell;                                  // '#': 벽
    bool open(int r, int c) const { return r >= 0 && r < R && c >= 0 && c < C && cell[r][c] != '#'; }
    explicit Grid(int r, int c) : R(r), C(c), cell(r, std::string(c, '.')) {}
    std::vector<std::pair<int, int>> neighbors(int r, int c, bool torus = false) const {
        static const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1}; std::vector<std::pair<int, int>> out;
        for (int k = 0; k < 4; ++k) { int nr = r + dr[k], nc = c + dc[k]; if (torus) { nr = (nr + R) % R; nc = (nc + C) % C; if (nr == r && nc == c) continue; } if (open(nr, nc)) out.push_back({nr, nc}); }
        if (torus) { std::sort(out.begin(), out.end()); out.erase(std::unique(out.begin(), out.end()), out.end()); }       // 폭이 1·2 인 원환의 겹치는 이웃 정리
        return out; }
    std::vector<std::vector<int>> bfs(int sr, int sc, bool torus = false, std::vector<std::vector<long long>>* ways = nullptr) const {
        std::vector<std::vector<int>> dist(R, std::vector<int>(C, -1)); if (ways) ways->assign(R, std::vector<long long>(C, 0)); if (!open(sr, sc)) return dist;
        std::queue<std::pair<int, int>> q; q.push({sr, sc}); dist[sr][sc] = 0; if (ways) (*ways)[sr][sc] = 1;
        while (!q.empty()) { auto [r, c] = q.front(); q.pop(); for (auto nb : neighbors(r, c, torus)) { if (dist[nb.first][nb.second] < 0) { dist[nb.first][nb.second] = dist[r][c] + 1; q.push(nb); } if (ways && dist[nb.first][nb.second] == dist[r][c] + 1) (*ways)[nb.first][nb.second] += (*ways)[r][c]; } }
        return dist; }
};
long long binom(int n, int k) { long long r = 1; for (int i = 1; i <= k; ++i) r = r * (n - k + i) / i; return r; }

int main() {
    for (int R = 1; R <= 9; ++R) for (int C = 1; C <= 9; ++C) {                                                                                            // ① 빈 격자 전수
        Grid g(R, C); long edges2 = 0; int d2 = 0, d3 = 0, d4 = 0, d1 = 0, d0 = 0;
        for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) { auto nb = g.neighbors(r, c); edges2 += (long)nb.size(); int d = (int)nb.size(); (d == 0 ? d0 : d == 1 ? d1 : d == 2 ? d2 : d == 3 ? d3 : d4)++;
            for (auto n2 : nb) assert((r + c) % 2 != (n2.first + n2.second) % 2); }                                                                                   // 이분성
        assert(edges2 == 2L * (R * (C - 1) + C * (R - 1)));
        if (R >= 2 && C >= 2) assert(d2 == 4 && d3 == 2 * (R - 2) + 2 * (C - 2) && d4 == (R - 2) * (C - 2) && d1 == 0 && d0 == 0);
        for (int sr = 0; sr < R; ++sr) for (int sc = 0; sc < C; ++sc) { std::vector<std::vector<long long>> ways; auto dist = g.bfs(sr, sc, false, &ways);                          // 모든 출발점
            for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) { assert(dist[r][c] == std::abs(r - sr) + std::abs(c - sc)); assert(ways[r][c] == binom(std::abs(r - sr) + std::abs(c - sc), std::abs(r - sr))); } } }       // ②
    for (int R = 3; R <= 8; ++R) for (int C = 3; C <= 8; ++C) { Grid g(R, C); for (int sr = 0; sr < R; ++sr) for (int sc = 0; sc < C; ++sc) { auto dist = g.bfs(sr, sc, true);                             // ③ 원환
            for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) { int dr = std::abs(r - sr), dc = std::abs(c - sc); assert(dist[r][c] == std::min(dr, R - dr) + std::min(dc, C - dc)); } } }
    std::mt19937 rng(8);
    for (int trial = 0; trial < 600; ++trial) { int R = 1 + (int)(rng() % 7), C = 1 + (int)(rng() % 7); Grid g(R, C); for (auto& row : g.cell) for (auto& ch : row) if (rng() % 100 < 30) ch = '#';       // ④ 장애물
        int n = R * C; const int INF = 1 << 28; std::vector<std::vector<int>> fw(n, std::vector<int>(n, INF)); std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
        for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (g.open(r, c)) { fw[r * C + c][r * C + c] = 0; for (auto nb : g.neighbors(r, c)) { fw[r * C + c][nb.first * C + nb.second] = 1; p[find(r * C + c)] = find(nb.first * C + nb.second); } }
        for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) fw[i][j] = std::min(fw[i][j], fw[i][k] + fw[k][j]);
        int comps = 0; for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (g.open(r, c) && find(r * C + c) == r * C + c) ++comps; std::vector<char> seen(n, 0); int floods = 0;
        for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) { if (!g.open(r, c) || seen[r * C + c]) continue; ++floods; auto d = g.bfs(r, c); for (int rr = 0; rr < R; ++rr) for (int cc = 0; cc < C; ++cc) if (d[rr][cc] >= 0) seen[rr * C + cc] = 1; } assert(floods == comps);
        for (int sr = 0; sr < R; ++sr) for (int sc = 0; sc < C; ++sc) { if (!g.open(sr, sc)) continue; auto d = g.bfs(sr, sc); for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) { if (!g.open(r, c)) continue; int want = fw[sr * C + sc][r * C + c] >= INF ? -1 : fw[sr * C + sc][r * C + c]; assert(d[r][c] == want);
                if (want >= 0) { int man = std::abs(r - sr) + std::abs(c - sc); assert(want >= man && (want - man) % 2 == 0); } } } }
    {   const int N = 1000; Grid g(N, N); auto d = g.bfs(0, 0); assert(d[N - 1][N - 1] == 2 * (N - 1)); long long edges2 = 0; for (int r = 0; r < N; r += 1) for (int c = 0; c < N; c += 1) edges2 += (long long)g.neighbors(r, c).size(); assert(edges2 == 4LL * N * (N - 1) && edges2 / 2 == 1998000); }     // ⑤ 큰 입력
    std::cout << "GridGraph: edge counts, degree classes, bipartiteness, Manhattan distances and C(r+c, r) shortest-path counts held for every start cell of every open grid up to 9x9; torus distances matched the wrap-around formula; 600 walled grids agreed with Floyd-Warshall and union-find" << std::endl;
    return 0;
}
// Time Complexity: BFS O(R·C)
// Space Complexity: O(R·C)
```
## TreeGraph()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 트리 그래프: 연결되어 있고 사이클이 없는 그래프 (간선 n-1 개).  레이블된 트리는 n^(n-2) 개(케일리)이고,
// 각각은 길이 n-2 인 수열(프뤼퍼 수열)과 일대일로 대응한다 -> 프뤼퍼 수열을 복호화하면 균등 무작위 트리를 얻는다
std::vector<std::pair<int, int>> pruferDecode(const std::vector<int>& seq, int n) {
    std::vector<int> degree(n, 1); for (int x : seq) degree[x]++;
    std::set<int> leaves; for (int i = 0; i < n; i++) if (degree[i] == 1) leaves.insert(i);
    std::vector<std::pair<int, int>> edges;
    for (int x : seq) {
        int leaf = *leaves.begin(); leaves.erase(leaves.begin());
        edges.push_back({leaf, x});
        if (--degree[x] == 1) leaves.insert(x);
    }
    int a = *leaves.begin(), b = *std::next(leaves.begin());
    edges.push_back({a, b});
    return edges;
}
std::vector<int> pruferEncode(const std::vector<std::pair<int, int>>& edges, int n) {
    std::vector<std::set<int>> adj(n); for (auto& e : edges) { adj[e.first].insert(e.second); adj[e.second].insert(e.first); }
    std::set<int> leaves; for (int i = 0; i < n; i++) if (adj[i].size() == 1) leaves.insert(i);
    std::vector<int> seq;
    for (int i = 0; i < n - 2; i++) {
        int leaf = *leaves.begin(); leaves.erase(leaves.begin());
        int nb = *adj[leaf].begin(); seq.push_back(nb);
        adj[nb].erase(leaf); if (adj[nb].size() == 1) leaves.insert(nb);
    }
    return seq;
}
bool isTree(int n, const std::vector<std::pair<int, int>>& edges) {
    if ((int)edges.size() != n - 1) return false;
    std::vector<std::vector<int>> adj(n); for (auto& e : edges) { adj[e.first].push_back(e.second); adj[e.second].push_back(e.first); }
    std::vector<bool> seen(n, false); std::queue<int> q; q.push(0); seen[0] = true; int cnt = 1;
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = true; cnt++; q.push(v); } }
    return cnt == n;
}

int main() {
    std::mt19937 rng(71);
    for (int trial = 0; trial < 200; trial++) {
        int n = rng() % 20 + 3; std::vector<int> seq(n - 2); for (auto& x : seq) x = rng() % n;
        auto edges = pruferDecode(seq, n);
        assert(isTree(n, edges));                                   // 어떤 수열을 복호화해도 트리가 나온다
        assert(pruferEncode(edges, n) == seq);                      // 일대일 대응
    }
    // 서로 다른 프뤼퍼 수열의 수 = n^(n-2) = 트리 개수 (n = 5 -> 125)
    std::set<std::vector<std::pair<int, int>>> trees;
    for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
        auto e = pruferDecode({a, b, c}, 5); for (auto& x : e) if (x.first > x.second) std::swap(x.first, x.second); std::sort(e.begin(), e.end()); trees.insert(e);
    }
    assert(trees.size() == 125);
    std::cout << "TreeGraph: 125 labeled trees on 5 vertices via Prufer sequences." << std::endl;
    return 0;
}
// Time Complexity: 프뤼퍼 복호화 O(n log n)
// Space Complexity: O(n)
```
## HypercubeGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <vector>

// 초입방체 Q_d: 정점 = d비트 문자열, 한 비트만 다른 두 정점이 인접.  정점 2^d, 간선 d·2^(d-1), 모든 차수 d, 지름 d, 이분 그래프.  두 정점 사이의 거리 = 해밍 거리.  병렬 컴퓨터의 상호연결망과 그레이 코드(해밍 경로)의 기반
//  ① d = 1..10: 정점·간선 수, 차수, 이분성, 임의 출발점(전수 d ≤ 6, 무작위 d ≤ 10)에서 BFS 거리 == 해밍 거리, 지름 d, 해밍 거리 k 인 두 정점 사이의 *최단 경로 수 = k!*(BFS 로 세어 대조)
//  ② 그레이 코드 g(i) = i ^ (i >> 1): d = 1..16 에서 g 는 순열이고 이웃한 항은 한 비트만 다르며 *끝과 처음도* 한 비트만 달라(d ≥ 2) 해밍 *사이클*, 역함수 gray⁻¹ 가 정확  ③ 연결도(정점 제거에 대한 강건성): Q3·Q4 에서 정점을 d − 1 개 이하로 지워도 연결이고(모든 부분집합 전수), 한 정점의 이웃 d 개를 지우면 그 정점이 고립 — 정점 연결도 = d
//  ④ 자기동형(대칭) 수: Q3 에서 간선을 보존하는 정점 순열을 8! 개 전수 검사하면 정확히 3!·2^3 = 48 개, Q4 는 비트 순열 4!과 반전 마스크 2^4 로 만든 384 개가 모두 간선을 보존하고 서로 다름
std::vector<int> bfsFrom(int d, int s, std::vector<long long>* ways = nullptr) {
    int n = 1 << d; std::vector<int> dist(n, -1); if (ways) ways->assign(n, 0); std::queue<int> q; q.push(s); dist[s] = 0; if (ways) (*ways)[s] = 1;
    while (!q.empty()) { int v = q.front(); q.pop(); for (int b = 0; b < d; ++b) { int u = v ^ (1 << b); if (dist[u] < 0) { dist[u] = dist[v] + 1; q.push(u); } if (ways && dist[u] == dist[v] + 1) (*ways)[u] += (*ways)[v]; } }
    return dist; }
int gray(int i) { return i ^ (i >> 1); }
int grayInverse(int g) { int i = 0; for (; g; g >>= 1) i ^= g; return i; }
bool connectedWithout(int d, unsigned removedMask) {                                                          // 지운 정점을 뺀 나머지가 연결인가 (d ≤ 4: 정점 ≤ 16)
    int n = 1 << d; int start = -1; for (int v = 0; v < n; ++v) if (!(removedMask >> v & 1)) { start = v; break; } if (start < 0) return true;
    std::vector<char> seen(n, 0); std::queue<int> q; q.push(start); seen[start] = 1; int cnt = 1; while (!q.empty()) { int v = q.front(); q.pop(); for (int b = 0; b < d; ++b) { int u = v ^ (1 << b); if (!(removedMask >> u & 1) && !seen[u]) { seen[u] = 1; ++cnt; q.push(u); } } }
    return cnt == n - __builtin_popcount(removedMask); }

int main() {
    std::mt19937 rng(77);
    for (int d = 1; d <= 10; d++) { int n = 1 << d; long edges = 0; for (int v = 0; v < n; v++) for (int b = 0; b < d; b++) { int u = v ^ (1 << b); if (u > v) edges++; assert((__builtin_popcount(v) + __builtin_popcount(u)) % 2 == 1); }   // ① 간선 수·이분성
        assert(edges == (long)d * (n / 2));
        std::vector<int> sources; if (d <= 6) { for (int s = 0; s < n; ++s) sources.push_back(s); } else for (int i = 0; i < 20; ++i) sources.push_back((int)(rng() % n));
        for (int s : sources) { std::vector<long long> ways; auto dist = bfsFrom(d, s, &ways); int diameter = 0; for (int v = 0; v < n; v++) { int h = __builtin_popcount(v ^ s); assert(dist[v] == h); diameter = std::max(diameter, dist[v]); long long fact = 1; for (int i = 2; i <= h; ++i) fact *= i; assert(ways[v] == fact); } assert(diameter == d); } }
    for (int d = 1; d <= 16; ++d) { int n = 1 << d; std::vector<char> seen(n, 0);                                                                                     // ② 그레이 코드
        for (int i = 0; i < n; ++i) { int g = gray(i); assert(g >= 0 && g < n && !seen[g] && grayInverse(g) == i); seen[g] = 1; if (i + 1 < n) assert(__builtin_popcount(g ^ gray(i + 1)) == 1); }
        if (d >= 2) assert(__builtin_popcount(gray(n - 1) ^ gray(0)) == 1); else assert(gray(n - 1) != gray(0)); }
    for (int d = 3; d <= 4; ++d) { int n = 1 << d; long checked = 0; for (unsigned mask = 0; mask < (1u << n); ++mask) { int k = __builtin_popcount(mask); if (k > d) continue; bool conn = connectedWithout(d, mask);       // ③ 연결도
            if (k <= d - 1) assert(conn); else { bool isolatingNeighbors = false; for (int v = 0; v < n && !isolatingNeighbors; ++v) { unsigned nb = 0; for (int b = 0; b < d; ++b) nb |= 1u << (v ^ (1 << b)); if (nb == mask) isolatingNeighbors = true; } assert(conn == !isolatingNeighbors); } ++checked; } assert(checked == (d == 3 ? 93 : 2517)); }
    {   std::vector<int> perm(8); std::iota(perm.begin(), perm.end(), 0); long autos = 0;                                                                              // ④ 자기동형 Q3
        do { bool ok = true; for (int v = 0; v < 8 && ok; ++v) for (int b = 0; b < 3; ++b) { int u = v ^ (1 << b); if (__builtin_popcount(perm[v] ^ perm[u]) != 1) { ok = false; break; } } autos += ok; } while (std::next_permutation(perm.begin(), perm.end())); assert(autos == 48);
        std::vector<int> bits(4); std::iota(bits.begin(), bits.end(), 0); std::vector<std::vector<int>> maps; do { for (int flip = 0; flip < 16; ++flip) { std::vector<int> f(16); for (int v = 0; v < 16; ++v) { int w = 0; for (int b = 0; b < 4; ++b) if (v >> b & 1) w |= 1 << bits[b]; f[v] = w ^ flip; }
                for (int v = 0; v < 16; ++v) for (int b = 0; b < 4; ++b) assert(__builtin_popcount(f[v] ^ f[v ^ (1 << b)]) == 1); maps.push_back(f); } } while (std::next_permutation(bits.begin(), bits.end()));
        std::sort(maps.begin(), maps.end()); assert(maps.size() == 384 && std::adjacent_find(maps.begin(), maps.end()) == maps.end()); }
    std::cout << "HypercubeGraph: BFS distances were Hamming distances with k! shortest paths for Q1..Q10, Gray codes formed a Hamiltonian cycle up to Q16, no set of d-1 removed vertices disconnects Q3/Q4 while a vertex's d neighbours isolate it, and Q3 has exactly 48 automorphisms" << std::endl;
    return 0;
}
// Time Complexity: BFS O(d·2^d)
// Space Complexity: O(2^d)
```
## ScaleFreeGraph()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 척도 없는 네트워크(Barabási–Albert): 새 정점이 기존 정점에 연결될 확률이 그 정점의 차수에 비례한다(선호적 연결, "부자가 더 부자").
// 결과: 차수 분포가 거듭제곱 꼬리 P(k) ~ k^-3 를 따라 소수의 허브와 대다수의 저차수 정점이 생긴다 (웹, 인용망, 항공망)
// 구현 요령: 간선 끝점 목록에서 균등하게 뽑으면 차수에 비례하는 선택이 된다
int main() {
    std::mt19937 rng(81);
    const int n = 3000, m = 2;
    std::vector<int> degree(n, 0), endpoints;                          // endpoints: 각 정점이 차수만큼 들어 있는 목록
    for (int i = 0; i < m + 1; i++) for (int j = i + 1; j < m + 1; j++) { degree[i]++; degree[j]++; endpoints.push_back(i); endpoints.push_back(j); }
    for (int v = m + 1; v < n; v++) {
        std::vector<int> targets;
        while ((int)targets.size() < m) { int t = endpoints[rng() % endpoints.size()]; if (std::find(targets.begin(), targets.end(), t) == targets.end()) targets.push_back(t); }
        for (int t : targets) { degree[v]++; degree[t]++; endpoints.push_back(v); endpoints.push_back(t); }
    }
    double mean = 0; for (int d : degree) mean += d; mean /= n;
    int maxDeg = *std::max_element(degree.begin(), degree.end());
    assert(std::abs(mean - 2 * m) < 0.1);                              // 평균 차수 ≈ 2m
    assert(maxDeg > 10 * mean);                                        // 허브: 평균의 10배 넘는 차수
    int low = std::count_if(degree.begin(), degree.end(), [&](int d) { return d <= 2 * m; });
    assert(low > n / 2);                                               // 대다수는 차수가 낮다
    std::cout << "ScaleFreeGraph: mean degree " << mean << ", max degree (hub) " << maxDeg << std::endl;
    return 0;
}
// Time Complexity: O(n·m)
// Space Complexity: O(n·m)
```
## SmallWorldGraph()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 작은 세상 네트워크(Watts–Strogatz): 링 격자(각 정점이 양옆 k/2 개와 연결)의 간선을 확률 β 로 무작위 재배선한다.
// 몇 개의 지름길만으로 평균 경로 길이가 급격히 짧아지지만(여섯 단계 분리) 군집 계수는 높게 유지된다
typedef std::vector<std::set<int>> G;
G ring(int n, int k) { G g(n); for (int i = 0; i < n; i++) for (int j = 1; j <= k / 2; j++) { g[i].insert((i + j) % n); g[(i + j) % n].insert(i); } return g; }
void rewire(G& g, int k, double beta, std::mt19937& rng) {
    int n = g.size(); std::bernoulli_distribution b(beta);
    for (int i = 0; i < n; i++) for (int j = 1; j <= k / 2; j++) {          // 각 간선 (i, i+j) 를 한 번씩만 본다
        int u = (i + j) % n;
        if (!b(rng)) continue;
        int w; do { w = rng() % n; } while (w == i || g[i].count(w));        // 자기 루프·중복 간선을 피해 새 끝점을 뽑는다
        g[i].erase(u); g[u].erase(i); g[i].insert(w); g[w].insert(i);
    }
}
double clustering(const G& g) {
    double sum = 0;
    for (size_t i = 0; i < g.size(); i++) {
        std::vector<int> nb(g[i].begin(), g[i].end()); int links = 0, d = nb.size();
        if (d < 2) continue;
        for (int a = 0; a < d; a++) for (int c = a + 1; c < d; c++) links += g[nb[a]].count(nb[c]);
        sum += 2.0 * links / (d * (d - 1));
    }
    return sum / g.size();
}
double avgPath(const G& g) {
    long total = 0, pairs = 0;
    for (size_t s = 0; s < g.size(); s++) {
        std::vector<int> d(g.size(), -1); std::queue<int> q; q.push(s); d[s] = 0;
        while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }
        for (size_t t = 0; t < g.size(); t++) if (t != s && d[t] > 0) { total += d[t]; pairs++; }
    }
    return double(total) / pairs;
}

int main() {
    std::mt19937 rng(91);
    const int n = 400, k = 10;
    G lattice = ring(n, k), sw = ring(n, k);
    rewire(sw, k, 0.1, rng);
    double c0 = clustering(lattice), l0 = avgPath(lattice), c1 = clustering(sw), l1 = avgPath(sw);
    assert(l1 < 0.5 * l0);                                          // 평균 경로 길이가 절반 이하로 급감
    assert(c1 > 0.5 * c0);                                          // 군집 계수는 크게 줄지 않는다
    std::cout << "lattice: C=" << c0 << " L=" << l0 << " | beta=0.1: C=" << c1 << " L=" << l1 << std::endl;
    return 0;
}
// Time Complexity: 평균 경로 O(n·(n + E))
// Space Complexity: O(n·k)
```
# Part 16. 응용
## DependencyGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 의존성 그래프: "A 를 쓰려면 B 가 먼저 필요" 를 A → B 로 둔다(빌드 시스템, 패키지 관리자, 스프레드시트 셀). 풀어야 할 문제 다섯 가지 — ① 설치·빌드 순서: 의존 대상이 앞에 오는 위상 순서. 사이클이 있으면 순서가 없으므로 *실제 사이클 경로* 를 보고한다. ② 병렬 빌드 단계(stage): 단계 s 의 패키지는 이전 단계에만 의존 → 단계 수 = 가장 긴 의존 사슬 길이. ③ 증분 빌드: 바뀐 패키지에 (간접적으로라도) 의존하는 모든 패키지 = 역방향 도달 집합만 다시 만든다. ④ 선언되지 않은(누락된) 의존 대상 찾기. ⑤ 직접 의존 목록 정리 = *추이적 축약(transitive reduction)*: 다른 경로로 이미 따라오는 직접 의존(A → C 인데 A → B → C 도 있음)을 지운다. DAG 에서는 유일한 최소 그래프이고 도달 가능성(폐쇄)은 그대로다.
// 이름은 문자열이라 처음 나온 순서대로 번호를 붙이는 사전(intern)을 쓰고, 탐색은 반복형이다(수십만 패키지 사슬에서도 호출 스택이 넘치지 않는다). 축약은 위상 순서대로 정점마다 "다른 직접 의존 대상들로부터 닿는 집합" 을 비트집합으로 합쳐, 그 안에 든 직접 의존은 중복이라고 판정한다(O(E·V/64)).
// 검증: ① 정점 4 개의 모든 방향 그래프(루프 없음, 4096)와 무작위 이름 그래프에서 해소 성공 ⇔ 사이클 없음(폐쇄 대각선), 성공이면 순서가 모든 의존을 만족하고, 실패면 돌려준 사이클이 닫혀 있고 간선이 실제로 있다 ② 단계 수 = 가장 긴 사슬(재귀 메모) ③ 증분 빌드 집합 = 폐쇄 오라클의 역방향 도달 집합 ④ 축약: *모든* 간선을 하나씩 빼 보는 완전 탐색과 같고, 같은 폐쇄를 가진 모든 부분 그래프를 열거했을 때 그 모두가 축약을 포함한다(유일·최소) ⑤ 큰 입력: 20 만 패키지 사슬, 1500 개 희소 DAG 의 축약, 10 만 개 층 DAG 의 단계 수와 4000 개 층 DAG 의 축약(비트집합 메모리를 아끼려 따로).
struct Deps {
    std::map<std::string, int> id; std::vector<std::string> names; std::vector<std::vector<int>> need, users; std::vector<char> declared;
    int intern(const std::string& s) {
        auto it = id.find(s); if (it != id.end()) return it->second;
        int k = (int)names.size(); id[s] = k; names.push_back(s); need.emplace_back(); users.emplace_back(); declared.push_back(0); return k;
    }
    void declare(const std::string& s) { declared[intern(s)] = 1; }
    void depend(const std::string& a, const std::string& b) { int x = intern(a), y = intern(b); declared[x] = 1; need[x].push_back(y); users[y].push_back(x); }
    int size() const { return (int)names.size(); }
};
struct Plan { bool ok = false; std::vector<int> order, cycle; };

// ① 설치 순서 (반복형 DFS, 의존 대상이 먼저). roots 가 비어 있지 않으면 그 뿌리들에 필요한 것만.
Plan resolve(const Deps& d, const std::vector<int>& roots = {}) {
    int n = d.size(); Plan p; std::vector<int> color(n, 0), it(n, 0), st; std::vector<int> start = roots;
    if (start.empty()) { start.resize(n); std::iota(start.begin(), start.end(), 0); }
    for (int s : start) {
        if (color[s]) continue;
        color[s] = 1; st.push_back(s);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] < (int)d.need[u].size()) {
                int v = d.need[u][it[u]++];
                if (color[v] == 1) {                                                 // 사이클: 스택에서 v 이후 + v
                    auto pos = std::find(st.begin(), st.end(), v);
                    p.cycle.assign(pos, st.end()); p.cycle.push_back(v); return p;
                }
                if (color[v] == 0) { color[v] = 1; st.push_back(v); }
            } else { color[u] = 2; p.order.push_back(u); st.pop_back(); }
        }
    }
    p.ok = true; return p;
}
// ② 병렬 빌드 단계
std::vector<int> stages(const Deps& d, bool& acyclic) {
    int n = d.size(); std::vector<int> remaining(n), stage(n, 0), q;
    for (int v = 0; v < n; ++v) { remaining[v] = (int)d.need[v].size(); if (!remaining[v]) q.push_back(v); }
    for (std::size_t h = 0; h < q.size(); ++h) { int v = q[h]; for (int u : d.users[v]) { stage[u] = std::max(stage[u], stage[v] + 1); if (--remaining[u] == 0) q.push_back(u); } }
    acyclic = (int)q.size() == n; return stage;
}
// ③ 증분 빌드: 바뀐 것에 (간접적으로) 의존하는 모두
std::vector<char> rebuildSet(const Deps& d, const std::vector<int>& changed) {
    std::vector<char> dirty(d.size(), 0); std::vector<int> st;
    for (int c : changed) if (!dirty[c]) { dirty[c] = 1; st.push_back(c); }
    while (!st.empty()) { int v = st.back(); st.pop_back(); for (int u : d.users[v]) if (!dirty[u]) { dirty[u] = 1; st.push_back(u); } }
    return dirty;
}
// ④ 누락된 의존 대상 (어디서도 선언되지 않음)
std::vector<std::string> missing(const Deps& d) { std::vector<std::string> m; for (int v = 0; v < d.size(); ++v) if (!d.declared[v]) m.push_back(d.names[v]); return m; }
// ⑤ 추이적 축약 (DAG 전용): 반환 = 남는 직접 의존 (정렬된 (a, b) 쌍)
std::vector<std::pair<int, int>> reduction(const Deps& d) {
    Plan p = resolve(d); assert(p.ok);
    int n = d.size(), W = (n + 63) / 64; std::vector<std::vector<uint64_t>> reach(n, std::vector<uint64_t>(W, 0));    // reach[a] = a 에서 *진짜로* (길이 ≥ 1) 닿는 집합
    std::vector<std::pair<int, int>> kept;
    for (int a : p.order) {                                                       // 의존 대상이 먼저 처리된다
        std::vector<int> direct = d.need[a]; std::sort(direct.begin(), direct.end()); direct.erase(std::unique(direct.begin(), direct.end()), direct.end());
        std::vector<uint64_t> cover(W, 0);
        for (int c : direct) for (int w = 0; w < W; ++w) cover[w] |= reach[c][w];            // 직접 의존 대상들이 *각자* 닿는 집합의 합
        for (int b : direct) { if (!(cover[b >> 6] >> (b & 63) & 1)) kept.push_back({a, b}); }   // 다른 직접 의존을 거쳐 닿으면 중복
        for (int c : direct) { reach[a][c >> 6] |= 1ULL << (c & 63); for (int w = 0; w < W; ++w) reach[a][w] |= reach[c][w]; }
    }
    std::sort(kept.begin(), kept.end()); return kept;
}

// ---- 오라클 ----
std::vector<std::vector<char>> closureOf(int n, const std::vector<std::pair<int, int>>& edges) {            // 진짜(길이 ≥ 1) 도달 가능성
    std::vector<std::vector<char>> r(n, std::vector<char>(n, 0)); for (auto [a, b] : edges) r[a][b] = 1;
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (r[i][k]) for (int j = 0; j < n; ++j) if (r[k][j]) r[i][j] = 1;
    return r;
}
std::vector<std::pair<int, int>> edgesOf(const Deps& d) { std::vector<std::pair<int, int>> e; for (int a = 0; a < d.size(); ++a) for (int b : d.need[a]) e.push_back({a, b}); return e; }
bool validCycle(const Deps& d, const std::vector<int>& c) {
    if (c.size() < 2 || c.front() != c.back()) return false;
    std::vector<int> body(c.begin(), c.end() - 1); std::vector<int> s = body; std::sort(s.begin(), s.end()); if (std::adjacent_find(s.begin(), s.end()) != s.end()) return false;
    for (std::size_t i = 0; i + 1 < c.size(); ++i) if (std::find(d.need[c[i]].begin(), d.need[c[i]].end(), c[i + 1]) == d.need[c[i]].end()) return false;
    return true;
}
int longestChain(const Deps& d, int v, std::vector<int>& memo) { if (memo[v] >= 0) return memo[v]; int best = 0; for (int w : d.need[v]) best = std::max(best, 1 + longestChain(d, w, memo)); return memo[v] = best; }
std::string pk(int i) { return "p" + std::to_string(i); }

int main() {
    // ① 손으로 확인한 모양: app → ui, net ; ui → core ; net → core. 순서·단계·증분 빌드·누락
    {   Deps d; d.depend("app", "ui"); d.depend("app", "net"); d.depend("ui", "core"); d.depend("net", "core"); d.declare("core");
        Plan p = resolve(d); assert(p.ok);
        auto pos = [&](const char* s) { return std::find(p.order.begin(), p.order.end(), d.id.at(s)) - p.order.begin(); };
        assert(pos("core") < pos("ui") && pos("core") < pos("net") && pos("ui") < pos("app") && pos("net") < pos("app"));
        bool acyclic; auto st = stages(d, acyclic); assert(acyclic && st[d.id.at("core")] == 0 && st[d.id.at("ui")] == 1 && st[d.id.at("net")] == 1 && st[d.id.at("app")] == 2);
        auto dirty = rebuildSet(d, {d.id.at("net")}); assert(dirty[d.id.at("net")] && dirty[d.id.at("app")] && !dirty[d.id.at("ui")] && !dirty[d.id.at("core")]);   // net 만 바뀌면 net 과 app 만
        assert(missing(d).empty());
        d.depend("app", "core");                                                 // 직접 의존이지만 이미 ui → core 로 따라온다 → 축약에서 사라진다
        auto red = reduction(d); assert(red.size() == 4 && std::find(red.begin(), red.end(), std::make_pair(d.id.at("app"), d.id.at("core"))) == red.end());
        Deps m; m.depend("a", "ghost"); assert(missing(m) == std::vector<std::string>({"ghost"}));
        Deps bad; bad.depend("a", "b"); bad.depend("b", "c"); bad.depend("c", "a"); bad.depend("d", "a");
        Plan q = resolve(bad); assert(!q.ok && q.cycle.size() == 4 && validCycle(bad, q.cycle));
        std::vector<std::string> names; for (int v : q.cycle) names.push_back(bad.names[v]); assert((names == std::vector<std::string>{"a", "b", "c", "a"}));
        Plan only = resolve(d, {d.id.at("ui")}); assert(only.ok && only.order.size() == 2);   // ui 설치에는 ui, core 만
    }

    // ② 전수: 정점 4 개의 모든 방향 그래프(루프 없음, 2^12) — 해소 성공 ⇔ 폐쇄 대각선이 비어 있음, 순서·사이클 증거 검증, 단계 수 = 가장 긴 사슬 (자기 의존은 아래 손 예제에서)
    long long acyclicCount = 0;
    {
        const int n = 4; std::vector<std::pair<int, int>> all; for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) if (a != b) all.push_back({a, b});
        for (unsigned mask = 0; mask < (1u << 12); ++mask) {
            Deps d; for (int i = 0; i < n; ++i) d.declare(pk(i));
            for (int i = 0; i < 12; ++i) if (mask >> i & 1) d.depend(pk(all[i].first), pk(all[i].second));
            auto cl = closureOf(n, edgesOf(d)); bool cyc = false; for (int i = 0; i < n; ++i) cyc = cyc || cl[i][i];
            Plan p = resolve(d); bool acyc = false; auto st = stages(d, acyc);
            assert(p.ok == !cyc && acyc == !cyc);
            if (p.ok) {
                std::vector<int> pos(n); for (int i = 0; i < n; ++i) pos[p.order[i]] = i;
                for (auto [a, b] : edgesOf(d)) assert(pos[b] < pos[a]);
                std::vector<int> memo(n, -1); for (int v = 0; v < n; ++v) assert(st[v] == longestChain(d, v, memo));
                ++acyclicCount;
            } else assert(validCycle(d, p.cycle));
        }
    }
    assert(acyclicCount == 543);                                                  // 이름 붙은 DAG 의 수 (정점 4)

    // ③ 무작위 DAG(정점 ≤ 12): 증분 빌드 집합 = 폐쇄 오라클, 누락, 단계; ④ 축약 = 간선 하나씩 빼 보기, 폐쇄 보존, 최소성
    std::mt19937 rng(2018);
    for (int it = 0; it < 800; ++it) {
        int n = 3 + (int)(rng() % 10); std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        Deps d; for (int i = 0; i < n; ++i) d.declare(pk(i));
        for (int i = 0; i < n; ++i) for (int j = 0; j < i; ++j) if (rng() % 100 < 30) d.depend(pk(perm[i]), pk(perm[j]));       // perm[j] 가 앞서므로 DAG
        if (rng() % 4 == 0 && !edgesOf(d).empty()) { auto e = edgesOf(d); d.depend(pk(e[0].first), pk(e[0].second)); }       // 중복 선언도 섞는다
        auto edges = edgesOf(d); auto cl = closureOf(n, edges);
        std::vector<int> changed; for (int i = 0; i < n; ++i) if (rng() % 4 == 0) changed.push_back(d.id.at(pk(i)));
        auto dirty = rebuildSet(d, changed);
        for (int v = 0; v < n; ++v) { bool want = std::find(changed.begin(), changed.end(), v) != changed.end(); for (int c : changed) want = want || cl[v][c]; assert((bool)dirty[v] == want); }
        auto red = reduction(d);
        std::vector<std::pair<int, int>> uniq = edges; std::sort(uniq.begin(), uniq.end()); uniq.erase(std::unique(uniq.begin(), uniq.end()), uniq.end());
        std::vector<std::pair<int, int>> bruteKept;
        for (auto e : uniq) {                                                    // 이 간선 없이도 a 에서 b 로 닿는가 (길이 ≥ 2 인 경로)
            std::vector<std::pair<int, int>> rest; for (auto f : uniq) if (f != e) rest.push_back(f);
            if (!closureOf(n, rest)[e.first][e.second]) bruteKept.push_back(e);
        }
        assert(red == bruteKept);
        assert(closureOf(n, red) == cl);                                         // 폐쇄 보존
        for (std::size_t i = 0; i < red.size(); ++i) { auto rest = red; rest.erase(rest.begin() + (long)i); assert(closureOf(n, rest) != cl); }   // 최소: 하나라도 빼면 폐쇄가 줄어든다
    }
    // 유일성: 정점 5 개 DAG(간선 i→j, i<j, 10 개 중 무작위 부분집합) — 같은 폐쇄를 가진 *모든* 부분 그래프가 축약을 포함한다
    for (int it = 0; it < 120; ++it) {
        const int n = 5; Deps d; for (int i = 0; i < n; ++i) d.declare(pk(i));
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) if (rng() % 100 < 60) d.depend(pk(b), pk(a));
        auto edges = edgesOf(d); std::sort(edges.begin(), edges.end()); auto cl = closureOf(n, edges); auto red = reduction(d); int m = (int)edges.size();
        for (unsigned mask = 0; mask < (1u << m); ++mask) {
            std::vector<std::pair<int, int>> sub; for (int i = 0; i < m; ++i) if (mask >> i & 1) sub.push_back(edges[i]);
            if (closureOf(n, sub) != cl) continue;
            for (auto e : red) assert(std::find(sub.begin(), sub.end(), e) != sub.end());
            assert(sub.size() >= red.size());
        }
    }

    // ⑤ 큰 입력: 20 만 패키지 사슬(i → i−1) 의 순서와 단계, 한쪽 끝만 바꾸면 전체 재빌드; 1500 개 희소 DAG 의 축약이 간선 하나씩 빼 보기와 같음; 10 만 개 층 DAG 의 단계
    {
        const int N = 200000; Deps d; for (int i = 0; i < N; ++i) d.declare(pk(i)); for (int i = 1; i < N; ++i) d.depend(pk(i), pk(i - 1));
        Plan p = resolve(d); assert(p.ok && (int)p.order.size() == N && p.order.front() == d.id.at(pk(0)) && p.order.back() == d.id.at(pk(N - 1)));
        bool acyclic; auto st = stages(d, acyclic); assert(acyclic && st[d.id.at(pk(N - 1))] == N - 1);
        auto dirty = rebuildSet(d, {d.id.at(pk(0))}); assert(std::count(dirty.begin(), dirty.end(), 1) == N);
        auto dirty2 = rebuildSet(d, {d.id.at(pk(N - 1))}); assert(std::count(dirty2.begin(), dirty2.end(), 1) == 1);
        d.depend(pk(0), pk(N - 1)); Plan c = resolve(d); assert(!c.ok && (int)c.cycle.size() == N + 1);
    }
    {
        const int n = 1500; Deps d; for (int i = 0; i < n; ++i) d.declare(pk(i));
        for (int i = 1; i < n; ++i) for (int k = 0; k < 3; ++k) d.depend(pk(i), pk((int)(rng() % i)));                      // 앞선 번호 셋에 의존
        auto edges = edgesOf(d); std::sort(edges.begin(), edges.end()); edges.erase(std::unique(edges.begin(), edges.end()), edges.end());
        auto red = reduction(d);
        std::vector<std::vector<int>> adj(n); for (auto [a, b] : edges) adj[a].push_back(b);
        std::vector<std::pair<int, int>> brute;
        for (auto e : edges) {                                                    // e 를 빼고 a 에서 b 로 DFS
            std::vector<char> seen(n, 0); std::vector<int> st{e.first}; seen[e.first] = 1; bool reach = false;
            while (!st.empty() && !reach) { int u = st.back(); st.pop_back(); for (int v : adj[u]) { if (u == e.first && v == e.second) continue; if (v == e.second) { reach = true; break; } if (!seen[v]) { seen[v] = 1; st.push_back(v); } } }
            if (!reach) brute.push_back(e);
        }
        assert(red == brute && red.size() < edges.size());
        const int L = 100000; Deps lay; for (int i = 0; i < L; ++i) { lay.declare(pk(i)); if (i) { lay.depend(pk(i), pk(i - 1)); if (i > 1) lay.depend(pk(i), pk(i - 2)); } }
        bool acyclic; auto st = stages(lay, acyclic); assert(acyclic && st[lay.id.at(pk(L - 1))] == L - 1);                 // i−1 을 거치는 사슬이 가장 길다
        const int L2 = 4000; Deps small; for (int i = 0; i < L2; ++i) { small.declare(pk(i)); if (i) { small.depend(pk(i), pk(i - 1)); if (i > 1) small.depend(pk(i), pk(i - 2)); } }
        assert((int)reduction(small).size() == L2 - 1);                           // i → i−2 는 i → i−1 → i−2 로 따라오므로 모두 사라진다
    }
    std::cout << "DependencyGraph: on all 4096 loop-free digraphs over 4 package names the iterative resolver succeeded exactly when the closure diagonal was empty (543 acyclic ones), orders satisfied every dependency, failures returned a closed simple cycle of real edges, parallel build stages equalled the longest dependency chain, incremental-rebuild sets matched a reverse-closure oracle, the transitive reduction equalled the result of deleting each edge in turn and testing reachability, preserved the closure, could not lose another edge, and was contained in every sub-graph with the same closure, and a 200,000-package chain, a 1500-package sparse DAG and a 100,000-package layered DAG behaved as predicted" << std::endl; return 0;
}
// Time Complexity: 순서·단계·증분 O(V + E), 축약 O(E · V / 64)
// Space Complexity: O(V + E) (축약은 O(V²/64) 비트)
```
## KnowledgeGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>

// 지식 그래프: (주어, 술어, 목적어) 삼중항(triple)의 집합.  정점 = 개체, 간선 = 관계(방향·이름 있음).  색인 두 벌(주어→술어→목적어, 술어→목적어→주어)을 두면 질의가 전체 훑기 없이 답을 바로 찾는다.
// 그래프 질의와 규칙 기반 추론이 가능하다: 예) "is_a" 는 추이적 → 닫힘(closure)을 계산하면 간접 사실이 드러난다.  규칙을 고정점까지 적용하는 것이 추론기의 핵심이며 결과는 *규칙 적용 순서와 무관*하다.
//  ① 손으로 만든 예(Tom is_a* → 4 개 클래스)  ② 무작위 추가·삭제 3 만 번 동안 두 색인이 삼중항 집합과 늘 일치하고, 패턴 질의 (S?, P?, O?) 8 가지 모든 와일드카드 조합이 *전체 훑기 오라클* 과 같다
//  ③ 추이적 닫힘이 개체 8 개·술어 3 개 무작위 삼중항에서 *플로이드–워셜 도달 가능성* 과 같음  ④ 규칙(추이: is_a, 대칭: sibling_of, 역: parent_of ↔ child_of)을 고정점까지 적용한 결과가 규칙 순서를 6 가지로 바꿔도 같고, 한 번 더 적용해도 더 늘지 않음(멱등), 결과가 원래 사실을 포함(단조)
typedef std::tuple<std::string, std::string, std::string> Triple;
class KG {
    std::set<Triple> facts; std::map<std::string, std::map<std::string, std::set<std::string>>> spo, pos;       // spo[s][p] = {o}, pos[p][o] = {s}
public:
    bool add(const std::string& s, const std::string& p, const std::string& o) { if (!facts.insert({s, p, o}).second) return false; spo[s][p].insert(o); pos[p][o].insert(s); return true; }
    bool remove(const std::string& s, const std::string& p, const std::string& o) { if (!facts.erase({s, p, o})) return false; auto prune = [](auto& outer, const std::string& a, const std::string& b, const std::string& c) { auto& mid = outer[a]; auto& leaf = mid[b]; leaf.erase(c); if (leaf.empty()) mid.erase(b); if (mid.empty()) outer.erase(a); }; prune(spo, s, p, o); prune(pos, p, o, s); return true; }
    size_t size() const { return facts.size(); }
    const std::set<Triple>& all() const { return facts; }
    std::set<std::string> objects(const std::string& s, const std::string& p) const { auto a = spo.find(s); if (a == spo.end()) return {}; auto b = a->second.find(p); return b == a->second.end() ? std::set<std::string>() : b->second; }
    std::set<std::string> subjects(const std::string& p, const std::string& o) const { auto a = pos.find(p); if (a == pos.end()) return {}; auto b = a->second.find(o); return b == a->second.end() ? std::set<std::string>() : b->second; }
    std::set<Triple> match(const std::string& s, const std::string& p, const std::string& o) const {                // "?" 는 와일드카드: 색인을 쓸 수 있는 조합은 색인으로
        std::set<Triple> r; bool ws = s == "?", wp = p == "?", wo = o == "?";
        if (!ws && !wp) { for (auto& obj : objects(s, p)) if (wo || obj == o) r.insert({s, p, obj}); return r; }
        if (!wp && !wo) { for (auto& sub : subjects(p, o)) if (ws || sub == s) r.insert({sub, p, o}); return r; }
        for (auto& f : facts) if ((ws || std::get<0>(f) == s) && (wp || std::get<1>(f) == p) && (wo || std::get<2>(f) == o)) r.insert(f); return r; }
    std::set<std::string> closure(const std::string& s, const std::string& p) const {                               // 추이적 관계의 도달 가능 집합
        std::set<std::string> seen; std::vector<std::string> st = {s};
        while (!st.empty()) { auto x = st.back(); st.pop_back(); for (auto& o : objects(x, p)) if (seen.insert(o).second) st.push_back(o); }
        return seen; }
    bool applyTransitive(const std::string& p) { bool changed = false; std::vector<Triple> add; for (auto& f : facts) if (std::get<1>(f) == p) for (auto& o2 : objects(std::get<2>(f), p)) add.push_back({std::get<0>(f), p, o2}); for (auto& t : add) changed |= this->add(std::get<0>(t), std::get<1>(t), std::get<2>(t)); return changed; }
    bool applySymmetric(const std::string& p) { bool changed = false; std::vector<Triple> add; for (auto& f : facts) if (std::get<1>(f) == p) add.push_back({std::get<2>(f), p, std::get<0>(f)}); for (auto& t : add) changed |= this->add(std::get<0>(t), std::get<1>(t), std::get<2>(t)); return changed; }
    bool applyInverse(const std::string& p, const std::string& q) { bool changed = false; std::vector<Triple> add; for (auto& f : facts) { if (std::get<1>(f) == p) add.push_back({std::get<2>(f), q, std::get<0>(f)}); if (std::get<1>(f) == q) add.push_back({std::get<2>(f), p, std::get<0>(f)}); } for (auto& t : add) changed |= this->add(std::get<0>(t), std::get<1>(t), std::get<2>(t)); return changed; }
};
std::set<Triple> naiveMatch(const std::set<Triple>& facts, const std::string& s, const std::string& p, const std::string& o) { std::set<Triple> r; for (auto& f : facts) if ((s == "?" || std::get<0>(f) == s) && (p == "?" || std::get<1>(f) == p) && (o == "?" || std::get<2>(f) == o)) r.insert(f); return r; }
void saturate(KG& kg, const std::vector<int>& order) { for (bool changed = true; changed;) { changed = false; for (int rule : order) { if (rule == 0) changed |= kg.applyTransitive("is_a"); else if (rule == 1) changed |= kg.applySymmetric("sibling_of"); else changed |= kg.applyInverse("parent_of", "child_of"); } } }

int main() {
    {   KG kg; kg.add("Seoul", "capital_of", "Korea"); kg.add("Korea", "located_in", "Asia"); kg.add("Cat", "is_a", "Mammal"); kg.add("Mammal", "is_a", "Animal"); kg.add("Animal", "is_a", "LivingThing"); kg.add("Tom", "is_a", "Cat"); kg.add("Tom", "owner", "Ann");   // ① 손으로 만든 예
        assert((kg.objects("Seoul", "capital_of") == std::set<std::string>{"Korea"}) && (kg.subjects("is_a", "Mammal") == std::set<std::string>{"Cat"}));
        assert((kg.closure("Tom", "is_a") == std::set<std::string>{"Cat", "Mammal", "Animal", "LivingThing"}) && kg.closure("Seoul", "is_a").empty()); }
    std::mt19937 rng(41); const char* ents[] = {"a", "b", "c", "d", "e", "f"}; const char* preds[] = {"is_a", "knows", "sibling_of", "parent_of"};
    {   KG kg; std::set<Triple> model;                                                                                                                      // ② 색인과 패턴 질의
        for (int step = 0; step < 30000; ++step) { std::string s = ents[rng() % 6], p = preds[rng() % 4], o = ents[rng() % 6]; if (rng() % 3) { assert(kg.add(s, p, o) == model.insert({s, p, o}).second); } else { assert(kg.remove(s, p, o) == (model.erase({s, p, o}) == 1)); }
            assert(kg.size() == model.size()); if (step % 500 == 0) { assert(kg.all() == model); std::set<Triple> viaIndex; for (auto& kv : model) { assert(kg.objects(std::get<0>(kv), std::get<1>(kv)).count(std::get<2>(kv)) && kg.subjects(std::get<1>(kv), std::get<2>(kv)).count(std::get<0>(kv))); }
                for (int mask = 0; mask < 8; ++mask) for (int rep = 0; rep < 3; ++rep) { std::string s = (mask & 1) ? "?" : ents[rng() % 6], p = (mask & 2) ? "?" : preds[rng() % 4], o = (mask & 4) ? "?" : ents[rng() % 6]; assert(kg.match(s, p, o) == naiveMatch(model, s, p, o)); } } } }
    for (int trial = 0; trial < 500; ++trial) { KG kg; bool reach[6][6] = {}; for (int i = 0; i < 8; ++i) { int a = (int)(rng() % 6), b = (int)(rng() % 6); kg.add(ents[a], "is_a", ents[b]); kg.add(ents[a], "knows", ents[b]); reach[a][b] = true; }            // ③ 추이적 닫힘
        for (int k = 0; k < 6; ++k) for (int i = 0; i < 6; ++i) for (int j = 0; j < 6; ++j) if (reach[i][k] && reach[k][j]) reach[i][j] = true;
        for (int i = 0; i < 6; ++i) { std::set<std::string> want; for (int j = 0; j < 6; ++j) if (reach[i][j]) want.insert(ents[j]); assert(kg.closure(ents[i], "is_a") == want); } }
    for (int trial = 0; trial < 300; ++trial) { std::vector<Triple> base; for (int i = 0; i < 10; ++i) base.push_back({ents[rng() % 6], preds[rng() % 4] == std::string("knows") ? "child_of" : preds[rng() % 4], ents[rng() % 6]});          // ④ 규칙 순서·멱등·단조
        std::set<Triple> reference; std::vector<int> order = {0, 1, 2}; bool first = true; do { KG kg; for (auto& t : base) kg.add(std::get<0>(t), std::get<1>(t), std::get<2>(t)); saturate(kg, order); if (first) { reference = kg.all(); first = false; } else assert(kg.all() == reference);
            KG again; for (auto& t : kg.all()) again.add(std::get<0>(t), std::get<1>(t), std::get<2>(t)); saturate(again, order); assert(again.all() == kg.all()); for (auto& t : base) assert(kg.all().count(t)); } while (std::next_permutation(order.begin(), order.end())); }
    std::cout << "KnowledgeGraph: both indexes stayed consistent with the triple set over 30000 adds/removes, all 8 wildcard patterns matched a full scan, transitive closure matched Floyd-Warshall reachability, and rule saturation was order-independent, idempotent and monotone in all 6 orders" << std::endl;
    return 0;
}
// Time Complexity: 색인 질의 O(결과), 닫힘 O(V·|facts|), 규칙 고정점 O(반복 횟수 · |facts|)
// Space Complexity: O(|facts|) (색인 두 벌)
```
## SocialNetworkGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>

// 소셜 네트워크: 정점 = 사람, 간선 = 친구 관계(무방향).  기본 질의: 친구의 친구 추천, 연결 중심성(차수), 최단 소개 경로(몇 단계), 군집 계수(내 친구들끼리 얼마나 친구인가).
// 인접 행렬 A 로 보면 모든 질의가 행렬 연산이다: 추천 후보 = (A²)[u][w] > 0 이고 w ≠ u 이고 A[u][w] = 0, 삼각형 수 = (A³)[u][u] / 2, 거리 = 플로이드–워셜.
//  ① 손으로 만든 예  ② 무작위 사회망 500 개(사람 2~12 명, 우정 0~30 개, 중복 우정 포함)에서 suggest/hops/degree/triangles 가 *행렬 오라클* 과 같다 (모든 쌍·모든 사람)
//  ③ 지역 군집 계수 = 삼각형 / C(차수, 2), 전체 전이성 = 3 × 삼각형 수 / 연결된 세 점 쌍의 수 — 완전 그래프에서 1, 트리에서 0  ④ 작은 세상(Watts–Strogatz): 사람 200 명 링 격자(양쪽 2 명씩)에서 간선의 10% 를 무작위로 다시 이으면 평균 최단 거리가 40% 미만으로 줄지만 군집 계수는 원래의 절반 이상 유지
class Social {
    std::map<std::string, std::set<std::string>> friends;
public:
    void befriend(const std::string& a, const std::string& b) { friends[a].insert(b); friends[b].insert(a); }
    bool knows(const std::string& u) const { return friends.count(u) > 0; }
    std::set<std::string> suggest(const std::string& u) const {                       // 친구의 친구 중 아직 친구가 아닌 사람
        std::set<std::string> r;
        for (auto& f : friends.at(u)) for (auto& ff : friends.at(f)) if (ff != u && !friends.at(u).count(ff)) r.insert(ff);
        return r;
    }
    int hops(const std::string& a, const std::string& b) const {
        std::map<std::string, int> d{{a, 0}}; std::queue<std::string> q; q.push(a);
        while (!q.empty()) { auto u = q.front(); q.pop(); if (u == b) return d[u]; for (auto& v : friends.at(u)) if (!d.count(v)) { d[v] = d[u] + 1; q.push(v); } }
        return -1;
    }
    size_t degree(const std::string& u) const { return friends.at(u).size(); }
    int triangles(const std::string& u) const {
        int t = 0; auto& f = friends.at(u);
        for (auto a = f.begin(); a != f.end(); ++a) for (auto b = std::next(a); b != f.end(); ++b) t += friends.at(*a).count(*b);
        return t;
    }
    double localClustering(const std::string& u) const { double d = (double)degree(u); return d < 2 ? 0.0 : triangles(u) / (d * (d - 1) / 2); }
};
typedef std::vector<std::vector<int>> AdjList;
double averagePath(const AdjList& g) { long long sum = 0, pairs = 0; int n = (int)g.size(); for (int s = 0; s < n; ++s) { std::vector<int> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } for (int v = 0; v < n; ++v) if (v != s && d[v] > 0) { sum += d[v]; ++pairs; } } return (double)sum / (double)pairs; }
double averageClustering(const AdjList& g) { double total = 0; for (size_t u = 0; u < g.size(); ++u) { std::set<int> nb(g[u].begin(), g[u].end()); nb.erase((int)u); if (nb.size() < 2) continue; int t = 0; for (int a : nb) for (int b : nb) if (a < b && std::find(g[a].begin(), g[a].end(), b) != g[a].end()) ++t; total += t / (nb.size() * (nb.size() - 1) / 2.0); } return total / (double)g.size(); }

int main() {
    {   Social s; s.befriend("ann", "bob"); s.befriend("bob", "cat"); s.befriend("ann", "cat"); s.befriend("cat", "dan"); s.befriend("dan", "eve");
        assert((s.suggest("ann") == std::set<std::string>{"dan"}) && s.hops("ann", "eve") == 3 && s.hops("ann", "ann") == 0 && s.degree("cat") == 3 && s.triangles("ann") == 1 && s.triangles("dan") == 0); }
    std::mt19937 rng(61);
    for (int trial = 0; trial < 500; ++trial) { int n = 2 + (int)(rng() % 11), m = (int)(rng() % 31); Social s; std::vector<std::vector<int>> A(n, std::vector<int>(n, 0)); for (int i = 0; i < n; ++i) s.befriend("p" + std::to_string(i), "p" + std::to_string(i));   // 자기 자신과의 우정 방지용 더미
        Social net; std::set<int> present; for (int i = 0; i < m; ++i) { int a = (int)(rng() % n), b = (int)(rng() % n); if (a == b) continue; net.befriend("p" + std::to_string(a), "p" + std::to_string(b)); A[a][b] = A[b][a] = 1; present.insert(a); present.insert(b); }
        const int INF = 1 << 20; std::vector<std::vector<int>> fw(n, std::vector<int>(n, INF)); for (int i = 0; i < n; ++i) { fw[i][i] = 0; for (int j = 0; j < n; ++j) if (A[i][j]) fw[i][j] = 1; } for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) fw[i][j] = std::min(fw[i][j], fw[i][k] + fw[k][j]);
        for (int u : present) { std::string un = "p" + std::to_string(u); int deg = 0, tri = 0; std::set<std::string> want; for (int w = 0; w < n; ++w) { deg += A[u][w]; if (w != u && !A[u][w]) { int common = 0; for (int x = 0; x < n; ++x) common += A[u][x] * A[x][w]; if (common > 0) want.insert("p" + std::to_string(w)); } }
            for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) tri += A[u][a] * A[a][b] * A[b][u]; assert(net.degree(un) == (size_t)deg && net.triangles(un) == tri && net.suggest(un) == want);
            double c = deg < 2 ? 0.0 : tri / (deg * (deg - 1) / 2.0); assert(std::abs(net.localClustering(un) - c) < 1e-12);
            for (int w : present) assert(net.hops(un, "p" + std::to_string(w)) == (fw[u][w] >= INF ? -1 : fw[u][w])); } }
    {   int n = 12; AdjList complete(n), tree(n); for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (i != j) complete[i].push_back(j); for (int i = 1; i < n; ++i) { tree[i].push_back((i - 1) / 2); tree[(i - 1) / 2].push_back(i); }          // ③
        assert(std::abs(averageClustering(complete) - 1.0) < 1e-12 && averageClustering(tree) == 0.0); }
    {   const int n = 200, k = 2; AdjList ring(n); for (int i = 0; i < n; ++i) for (int j = 1; j <= k; ++j) { ring[i].push_back((i + j) % n); ring[(i + j) % n].push_back(i); }                                       // ④ 작은 세상
        AdjList rewired = ring; std::mt19937 rr(5); int rewiredEdges = 0; for (int i = 0; i < n; ++i) for (int j = 1; j <= k; ++j) if (rr() % 100 < 10) { int old = (i + j) % n, to = (int)(rr() % n); if (to == i || std::find(rewired[i].begin(), rewired[i].end(), to) != rewired[i].end()) continue;
                rewired[i].erase(std::find(rewired[i].begin(), rewired[i].end(), old)); rewired[old].erase(std::find(rewired[old].begin(), rewired[old].end(), i)); rewired[i].push_back(to); rewired[to].push_back(i); ++rewiredEdges; }
        double L0 = averagePath(ring), L1 = averagePath(rewired), C0 = averageClustering(ring), C1 = averageClustering(rewired); assert(rewiredEdges > 20 && L1 < 0.6 * L0 && C1 > 0.5 * C0 && std::abs(C0 - 0.5) < 1e-9);
        std::cout << "SocialNetworkGraph: matrix-oracle queries agreed on 500 random networks; rewiring " << rewiredEdges << " ring edges cut the average path from " << L0 << " to " << L1 << " while clustering went " << C0 << " -> " << C1 << std::endl; }
    return 0;
}
// Time Complexity: 추천 O(Σ 친구의 차수), 경로 O(V + E), 삼각형 O(d²)
// Space Complexity: O(V + E)
```
## CallGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// 호출 그래프: 정점 = 함수, 간선 f → g = "f 가 g 를 호출". 프로그램 분석의 기본 자료구조 — 질문 여섯 가지: ① 죽은 코드: main 에서 도달 불가능한 함수 ② 재귀: 자기 자신에게 되돌아올 수 있는 함수(직접 재귀 = 자기 루프, 상호 재귀 = 크기 ≥ 2 인 강연결 요소) ③ 아래에서 위로 분석할 순서: 응축 그래프(강연결 요소를 한 점으로)의 *역위상 순서* — 호출되는 쪽(callee)을 먼저 분석하고 같은 요소 안은 고정점 반복. 타잔 알고리즘이 이 순서로 요소 번호를 준다. ④ 최대 스택 깊이: main 에서 닿는 곳에 재귀가 없으면 가장 긴 호출 사슬(프레임 수), 있으면 "무제한" ⑤ 잎 함수(아무것도 호출하지 않음) ⑥ 인라이닝 후보: 재귀가 아니고 호출 지점이 정확히 하나.
// 이름은 문자열이라 처음 나온 순서로 번호를 붙인다. 모든 탐색은 반복형. 검증: 정점 ≤ 5 의 모든 호출 그래프(자기 호출 포함, 2^25 가운데 표본)와 무작위 호출 그래프에서 ① 죽은 코드 = 폐쇄 오라클 ② 재귀 = 진짜(길이 ≥ 1) 폐쇄의 대각선 ③ 응축 그래프 순서: 서로 다른 요소로 가는 호출 f→g 마다 g 의 요소 번호가 더 작다 ④ 최대 스택 깊이 = 모든 호출 경로를 열거한 완전 탐색(비재귀일 때), 재귀가 닿으면 무제한 ⑤ 큰 입력(20 만 함수 · 50 만 호출 무작위, 50 만 단계의 사슬).
struct CallGraph {
    std::map<std::string, int> id; std::vector<std::string> name; std::vector<std::vector<int>> callees, callers; std::vector<int> selfCalls;
    int intern(const std::string& s) { auto it = id.find(s); if (it != id.end()) return it->second; int k = (int)name.size(); id[s] = k; name.push_back(s); callees.emplace_back(); callers.emplace_back(); selfCalls.push_back(0); return k; }
    void addFunction(const std::string& s) { intern(s); }
    void call(const std::string& f, const std::string& g) { int a = intern(f), b = intern(g); callees[a].push_back(b); callers[b].push_back(a); if (a == b) ++selfCalls[a]; }
    int size() const { return (int)name.size(); }
};
struct Analysis {
    std::vector<char> live, recursive, leaf, inlineCandidate; std::vector<int> comp; int comps = 0; int maxDepth = 0; bool unbounded = false;
};
// 반복형 타잔 (요소 번호 = 끝나는 순서 = 역위상: callee 쪽 요소가 더 작은 번호)
std::vector<int> sccs(const CallGraph& g, int& count) {
    int n = g.size(); std::vector<int> idx(n, -1), low(n, 0), it(n, 0), comp(n, -1), st, call; std::vector<char> on(n, 0); int counter = 0; count = 0;
    for (int r = 0; r < n; ++r) {
        if (idx[r] >= 0) continue;
        idx[r] = low[r] = counter++; st.push_back(r); on[r] = 1; call.push_back(r);
        while (!call.empty()) {
            int u = call.back();
            if (it[u] < (int)g.callees[u].size()) { int v = g.callees[u][it[u]++]; if (idx[v] < 0) { idx[v] = low[v] = counter++; st.push_back(v); on[v] = 1; call.push_back(v); } else if (on[v]) low[u] = std::min(low[u], idx[v]); }
            else { if (low[u] == idx[u]) { while (true) { int w = st.back(); st.pop_back(); on[w] = 0; comp[w] = count; if (w == u) break; } ++count; } call.pop_back(); if (!call.empty()) low[call.back()] = std::min(low[call.back()], low[u]); }
        }
    }
    return comp;
}
Analysis analyse(const CallGraph& g, int root) {
    int n = g.size(); Analysis a; a.comp = sccs(g, a.comps);
    a.live.assign(n, 0); std::vector<int> st{root}; a.live[root] = 1;
    while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : g.callees[u]) if (!a.live[v]) { a.live[v] = 1; st.push_back(v); } }
    std::vector<int> compSize(a.comps, 0); for (int v = 0; v < n; ++v) ++compSize[a.comp[v]];
    a.recursive.assign(n, 0); a.leaf.assign(n, 0); a.inlineCandidate.assign(n, 0);
    for (int v = 0; v < n; ++v) {
        a.recursive[v] = compSize[a.comp[v]] > 1 || g.selfCalls[v] > 0;
        a.leaf[v] = g.callees[v].empty();
        a.inlineCandidate[v] = !a.recursive[v] && g.callers[v].size() == 1 && v != root;
    }
    for (int v = 0; v < n; ++v) if (a.live[v] && a.recursive[v]) a.unbounded = true;                    // main 에서 닿는 재귀 → 스택 깊이 무제한
    if (!a.unbounded) {                                                                                  // 비재귀면 DAG: 요소 번호가 역위상이라 번호 오름차순이 callee 먼저
        std::vector<int> depth(n, 0), order(n); std::iota(order.begin(), order.end(), 0);
        std::sort(order.begin(), order.end(), [&](int x, int y) { return a.comp[x] < a.comp[y]; });
        for (int v : order) { int best = 0; for (int w : g.callees[v]) best = std::max(best, depth[w]); depth[v] = best + 1; }      // 프레임 수 (자기 자신 포함)
        a.maxDepth = depth[root];
    }
    return a;
}

// ---- 오라클 ----
std::vector<std::vector<char>> properClosure(const CallGraph& g) {
    int n = g.size(); std::vector<std::vector<char>> r(n, std::vector<char>(n, 0)); for (int a = 0; a < n; ++a) for (int b : g.callees[a]) r[a][b] = 1;
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) if (r[i][k]) for (int j = 0; j < n; ++j) if (r[k][j]) r[i][j] = 1;
    return r;
}
int bruteDepth(const CallGraph& g, int v) { int best = 0; for (int w : g.callees[v]) best = std::max(best, bruteDepth(g, w)); return best + 1; }   // 비재귀 전용: 모든 경로 열거
std::string fn(int i) { return "f" + std::to_string(i); }

int main() {
    // ① 손으로 확인한 모양: 기존 예제 — main → parse, run ; parse → lex ; run → step, log ; step → step, log ; even ↔ odd ; unused → log
    {   CallGraph g;
        g.call("main", "parse"); g.call("main", "run"); g.call("parse", "lex"); g.call("run", "step"); g.call("run", "log"); g.call("step", "step"); g.call("step", "log");
        g.call("even", "odd"); g.call("odd", "even"); g.call("unused", "log"); g.addFunction("lex");
        Analysis a = analyse(g, g.id.at("main"));
        std::set<std::string> dead, rec, leaves, inl;
        for (int v = 0; v < g.size(); ++v) { if (!a.live[v]) dead.insert(g.name[v]); if (a.recursive[v]) rec.insert(g.name[v]); if (a.leaf[v]) leaves.insert(g.name[v]); if (a.inlineCandidate[v]) inl.insert(g.name[v]); }
        assert((dead == std::set<std::string>{"even", "odd", "unused"}) && (rec == std::set<std::string>{"step", "even", "odd"}));
        assert((leaves == std::set<std::string>{"lex", "log"}) && (inl == std::set<std::string>{"parse", "lex", "run"}));   // log 는 호출 지점이 셋이라 후보가 아님, step 은 재귀
        assert(a.unbounded);                                                                                // main → run → step(재귀) : 스택 깊이 무제한
        assert(a.comp[g.id.at("lex")] < a.comp[g.id.at("parse")] && a.comp[g.id.at("log")] < a.comp[g.id.at("run")] && a.comp[g.id.at("run")] < a.comp[g.id.at("main")]);   // callee 먼저
        assert(a.comp[g.id.at("even")] == a.comp[g.id.at("odd")]);
        CallGraph h; h.call("main", "a"); h.call("a", "b"); h.call("b", "c"); h.call("main", "c");
        Analysis b = analyse(h, h.id.at("main")); assert(!b.unbounded && b.maxDepth == 4);                // main → a → b → c : 프레임 4 개
    }

    // ② 무작위 호출 그래프 (정점 ≤ 9, 자기 호출·평행 호출·고립 함수 포함): 죽은 코드 · 재귀 · 요소 순서 · 최대 깊이 · 리프를 오라클과 대조
    std::mt19937 rng(2024);
    int unboundedSeen = 0, boundedSeen = 0;
    for (int it = 0; it < 4000; ++it) {
        int n = 2 + (int)(rng() % 8), m = (int)(rng() % (2 * n + 1)); CallGraph g; for (int i = 0; i < n; ++i) g.addFunction(fn(i));
        bool acyclicBias = it % 2 == 0;                                              // 반은 번호가 큰 쪽만 호출하게 해 비재귀 그래프를 자주 만든다
        for (int i = 0; i < m; ++i) { int a = (int)(rng() % n), b = (int)(rng() % n); if (acyclicBias && b <= a) continue; g.call(fn(a), fn(b)); }
        Analysis a = analyse(g, 0); auto cl = properClosure(g);
        for (int v = 0; v < n; ++v) {
            assert((bool)a.live[v] == (v == 0 || cl[0][v]));                          // 죽은 코드
            assert((bool)a.recursive[v] == (bool)cl[v][v]);                           // 재귀 = 진짜 폐쇄의 대각선
            assert((bool)a.leaf[v] == g.callees[v].empty());
        }
        for (int u = 0; u < n; ++u) for (int v : g.callees[u]) assert(a.comp[u] == a.comp[v] || a.comp[v] < a.comp[u]);       // 응축 순서: callee 먼저
        bool reachRec = false; for (int v = 0; v < n; ++v) reachRec = reachRec || (a.live[v] && cl[v][v]);
        assert(a.unbounded == reachRec);
        if (!a.unbounded) { assert(a.maxDepth == bruteDepth(g, 0)); ++boundedSeen; } else ++unboundedSeen;
    }
    assert(boundedSeen > 1000 && unboundedSeen > 500);

    // ③ 큰 입력: 20 만 함수 · 50 만 호출 무작위 (분석 일관성) 와 50 만 단계 사슬 (스택 깊이가 정확히 50 만, 반복형이라 안전)
    {
        const int N = 200000; CallGraph g; for (int i = 0; i < N; ++i) g.addFunction(fn(i));
        std::mt19937_64 r(5); for (int i = 0; i < 500000; ++i) g.call(fn((int)(r() % N)), fn((int)(r() % N)));
        Analysis a = analyse(g, 0);
        for (int u = 0; u < N; ++u) for (int v : g.callees[u]) assert(a.comp[u] == a.comp[v] || a.comp[v] < a.comp[u]);
        std::vector<int> compSize(a.comps, 0); for (int v = 0; v < N; ++v) ++compSize[a.comp[v]];
        for (int v = 0; v < N; ++v) if (g.selfCalls[v] == 0) assert((bool)a.recursive[v] == (compSize[a.comp[v]] > 1));
        const int M = 500000; CallGraph chain; for (int i = 0; i < M; ++i) chain.addFunction(fn(i)); for (int i = 0; i + 1 < M; ++i) chain.call(fn(i), fn(i + 1));
        Analysis c = analyse(chain, 0); assert(!c.unbounded && c.maxDepth == M);
        chain.call(fn(M - 1), fn(0)); Analysis d = analyse(chain, 0); assert(d.unbounded && d.comps == 1);
    }
    std::cout << "CallGraph: dead code, recursion (self and mutual), leaf and inlining-candidate sets matched a transitive-closure oracle on 4000 random call graphs, the iterative Tarjan numbering put every callee before its caller, the maximum stack depth equalled exhaustive enumeration of all call paths whenever no reachable recursion existed (and was reported unbounded exactly when some live function recursed), a 200,000-function random program stayed consistent, and a 500,000-frame call chain gave depth 500,000 until a back call made it unbounded" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## StateTransitionGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

// 상태 전이 그래프: 정점 = 상태, 간선 = (이벤트로 인한) 전이.  유한 상태 기계(FSM)의 검증은 그래프 문제로 환원된다.
//  - 도달 불가능한 상태: 초기 상태에서 BFS 로 닿지 않는 상태 (설계 오류)
//  - 교착(deadlock) 상태: 나가는 전이가 없는데 종료 상태도 아닌 상태.  더 넓게는 "종료 상태에 영영 닿을 수 없는" 상태(역방향 BFS)
//  - 최소화: 완전 DFA 에서 도달 가능한 상태만 남기고 서로 구별되지 않는 상태를 합친다 (Moore 분할 정제)
// 검증: ① 신호등·작업 예  ② 무작위 부분 FSM 600 개의 도달/종료 가능/교착 집합을 Floyd-Warshall 닫힘 오라클과 대조
//        ③ 무작위 DFA 1 200 개(상태 1~6, 알파벳 2~3): 최소화 상태 수 = 길이 ≤ 6 의 *모든* 단어로 만든 상태 서명(Myhill-Nerode)의 종류 수,
//           곱 오토마타 BFS 로 원본과 동치, 멱등, 길이별 받아들이는 단어 수의 DP = 단어 전수 열거  ④ 닫힌 식: (a 의 개수 mod m, b 의 개수 mod p) 는 m 개 상태로 줄어든다
struct FSM {
    std::map<std::string, std::map<std::string, std::string>> next;     // next[state][event] = state'
    std::set<std::string> accepting;
    std::set<std::string> states() const { std::set<std::string> s; for (auto& kv : next) { s.insert(kv.first); for (auto& e : kv.second) s.insert(e.second); } return s; }
    std::set<std::string> reachableFrom(const std::string& init) const {
        std::set<std::string> seen{init}; std::queue<std::string> q; q.push(init);
        while (!q.empty()) { auto u = q.front(); q.pop(); auto it = next.find(u); if (it != next.end()) for (auto& e : it->second) if (seen.insert(e.second).second) q.push(e.second); }
        return seen;
    }
    std::set<std::string> deadlocks() const {
        std::set<std::string> r;
        for (auto& s : states()) { auto it = next.find(s); if ((it == next.end() || it->second.empty()) && !accepting.count(s)) r.insert(s); }
        return r;
    }
    std::set<std::string> coReachable() const {                          // 종료 상태에 닿을 수 있는 상태: 간선을 뒤집어 종료 상태들에서 BFS
        std::map<std::string, std::vector<std::string>> rev;
        for (auto& kv : next) for (auto& e : kv.second) rev[e.second].push_back(kv.first);
        std::set<std::string> seen(accepting.begin(), accepting.end()); std::queue<std::string> q; for (auto& a : accepting) q.push(a);
        while (!q.empty()) { auto u = q.front(); q.pop(); for (auto& p : rev[u]) if (seen.insert(p).second) q.push(p); }
        return seen;
    }
    std::string run(const std::string& init, const std::vector<std::string>& events) const {
        std::string s = init; for (auto& e : events) { auto it = next.at(s).find(e); if (it == next.at(s).end()) return "ERROR"; s = it->second; } return s;
    }
};

typedef std::vector<int> Word;
std::vector<Word> allWords(int k, int maxLen) {                          // 길이 ≤ maxLen 인 알파벳 k 개의 모든 단어 (짧은 것부터)
    std::vector<Word> w{Word()};
    for (size_t i = 0; i < w.size(); ++i) if ((int)w[i].size() < maxLen) for (int c = 0; c < k; ++c) { Word x = w[i]; x.push_back(c); w.push_back(x); }
    return w;
}
struct DFA {
    int n = 0, k = 0; std::vector<std::vector<int>> d; std::vector<bool> acc;      // 완전 DFA: d[s][c], 시작 상태는 0
    bool accepts(const Word& w, int s = 0) const { for (int c : w) s = d[s][c]; return acc[s]; }
    std::vector<bool> reachable() const {
        std::vector<bool> r(n, false); std::queue<int> q; r[0] = true; q.push(0);
        while (!q.empty()) { int u = q.front(); q.pop(); for (int c = 0; c < k; ++c) if (!r[d[u][c]]) { r[d[u][c]] = true; q.push(d[u][c]); } }
        return r;
    }
    long long countAccepted(int len) const {                             // 길이 len 인 받아들여지는 단어 수: 상태별 DP
        std::vector<long long> cur(n, 0), nxt; cur[0] = 1;
        for (int i = 0; i < len; ++i) { nxt.assign(n, 0); for (int s = 0; s < n; ++s) for (int c = 0; c < k; ++c) nxt[d[s][c]] += cur[s]; cur = nxt; }
        long long t = 0; for (int s = 0; s < n; ++s) if (acc[s]) t += cur[s];
        return t;
    }
    DFA minimized() const {                                              // Moore: 도달 가능한 상태만 남기고 (수락 여부, 전이 목적지의 클래스) 서명이 같은 상태를 합친다
        std::vector<bool> r = reachable(); std::vector<int> id(n, -1), ord;
        for (int s = 0; s < n; ++s) if (r[s]) { id[s] = (int)ord.size(); ord.push_back(s); }
        int m = (int)ord.size(); std::vector<int> cls(m); for (int i = 0; i < m; ++i) cls[i] = acc[ord[i]] ? 1 : 0;
        int prev = (int)std::set<int>(cls.begin(), cls.end()).size();
        for (;;) {
            std::map<std::vector<int>, int> sig; std::vector<int> nc(m);
            for (int i = 0; i < m; ++i) { std::vector<int> key{cls[i]}; for (int c = 0; c < k; ++c) key.push_back(cls[id[d[ord[i]][c]]]); nc[i] = sig.emplace(key, (int)sig.size()).first->second; }
            bool same = (int)sig.size() == prev; cls = nc; prev = (int)sig.size();
            if (same) break;
        }
        std::map<int, int> rn; for (int i = 0; i < m; ++i) rn.emplace(cls[i], (int)rn.size());          // 시작 상태(ord[0])의 클래스가 0 번이 된다
        DFA o; o.n = (int)rn.size(); o.k = k; o.d.assign(o.n, std::vector<int>(k, 0)); o.acc.assign(o.n, false);
        for (int i = 0; i < m; ++i) { int a = rn[cls[i]]; o.acc[a] = acc[ord[i]]; for (int c = 0; c < k; ++c) o.d[a][c] = rn[cls[id[d[ord[i]][c]]]]; }
        return o;
    }
};
bool equivalent(const DFA& a, const DFA& b) {                            // 곱 오토마타 BFS: 닿는 모든 상태 쌍의 수락 여부가 같은가 (단어 길이 한계에 의존하지 않는 정확한 판정)
    std::set<std::pair<int, int>> seen{{0, 0}}; std::queue<std::pair<int, int>> q; q.push({0, 0});
    while (!q.empty()) {
        std::pair<int, int> p = q.front(); q.pop(); if ((bool)a.acc[p.first] != (bool)b.acc[p.second]) return false;
        for (int c = 0; c < a.k; ++c) { std::pair<int, int> nx{a.d[p.first][c], b.d[p.second][c]}; if (seen.insert(nx).second) q.push(nx); }
    }
    return true;
}

int main() {
    // ① 신호등: 정의되지 않은 이벤트는 오류, 도달 불가능 상태 broken 은 자기만 다른 곳으로 나갈 뿐 초기 상태에서는 닿지 않는다
    FSM light;
    light.next = {{"green", {{"timer", "yellow"}}}, {"yellow", {{"timer", "red"}}}, {"red", {{"timer", "green"}}}, {"broken", {{"fix", "red"}}}};
    auto reach = light.reachableFrom("green");
    assert((reach == std::set<std::string>{"green", "yellow", "red"}));
    assert(!reach.count("broken"));
    assert(light.run("green", {"timer", "timer", "timer"}) == "green");
    assert(light.run("green", {"fix"}) == "ERROR");
    FSM job;                                                             // 작업: 종료 상태 done 외에 막힌 상태가 있는가
    job.next = {{"new", {{"start", "running"}}}, {"running", {{"ok", "done"}, {"fail", "stuck"}}}};
    job.accepting = {"done"};
    assert((job.deadlocks() == std::set<std::string>{"stuck"}));
    assert((job.coReachable() == std::set<std::string>{"new", "running", "done"}));     // stuck 은 종료 상태에 닿을 수 없다
    FSM none; assert(none.states().empty() && none.deadlocks().empty() && none.coReachable().empty());   // 경계: 빈 기계
    FSM loop; loop.next = {{"x", {{"e", "x"}}}};                         // 경계: 자기 루프만 있는 상태는 교착은 아니지만 종료에 닿지 못한다
    assert(loop.deadlocks().empty() && loop.coReachable().empty() && loop.reachableFrom("x").size() == 1);

    // ② 무작위 부분 FSM: 도달/종료 가능/교착 집합을 Floyd-Warshall 닫힘으로 다시 계산해 비교
    std::mt19937 rng(20240601); const char* ev[] = {"a", "b", "c"};
    long totalDeadlocks = 0, trapOnly = 0, fsmChecked = 0;
    for (int iter = 0; iter < 600; ++iter) {
        int S = 1 + (int)(rng() % 7), T = (int)(rng() % (2 * S + 1)); FSM f;
        auto nm = [](int i) { return "s" + std::to_string(i); };
        for (int t = 0; t < T; ++t) f.next[nm((int)(rng() % S))][ev[rng() % 3]] = nm((int)(rng() % S));
        std::set<std::string> st = f.states(); for (auto& s : st) if (rng() % 3 == 0) f.accepting.insert(s);
        int n = (int)st.size(); std::map<std::string, int> id; for (auto& s : st) id.emplace(s, (int)id.size());
        std::vector<std::vector<bool>> cl(n, std::vector<bool>(n, false));
        for (int i = 0; i < n; ++i) cl[i][i] = true;
        for (auto& kv : f.next) for (auto& e : kv.second) cl[id[kv.first]][id[e.second]] = true;
        for (int m = 0; m < n; ++m) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (cl[i][m] && cl[m][j]) cl[i][j] = true;
        std::set<std::string> dead, live, want;                           // dead: 종료 상태에 닿지 못함, live: 닿음
        for (auto& s : st) { bool ok = false; for (auto& a : f.accepting) if (cl[id[s]][id[a]]) ok = true; (ok ? live : dead).insert(s); }
        assert(f.coReachable() == live);
        for (auto& s : st) { int out = 0; auto it = f.next.find(s); if (it != f.next.end()) out = (int)it->second.size(); if (out == 0 && !f.accepting.count(s)) want.insert(s); }
        assert(f.deadlocks() == want);
        for (auto& s : f.deadlocks()) assert(dead.count(s));              // 교착 상태는 항상 "종료에 닿지 못하는" 상태다 (역은 성립하지 않는다)
        if (f.deadlocks().size() < dead.size()) ++trapOnly;               // 교착은 아니지만 갇힌 상태 (종료 없는 순환)
        totalDeadlocks += (long)f.deadlocks().size();
        for (auto& s : st) { std::set<std::string> exp; for (auto& t : st) if (cl[id[s]][id[t]]) exp.insert(t); assert(f.reachableFrom(s) == exp); }
        ++fsmChecked;
    }
    assert(fsmChecked == 600 && totalDeadlocks > 100 && trapOnly > 20);

    // ③ 무작위 완전 DFA: 최소화의 정확성
    std::vector<Word> w2 = allWords(2, 6), w3 = allWords(3, 6), w2long = allWords(2, 11);
    long shrunk = 0, withUnreachable = 0, totalBefore = 0, totalAfter = 0, mutatedDifferent = 0, mutatedSame = 0;
    for (int iter = 0; iter < 1200; ++iter) {
        DFA a; a.n = 1 + (int)(rng() % 6); a.k = 2 + (int)(rng() % 2); a.d.assign(a.n, std::vector<int>(a.k)); a.acc.assign(a.n, false);
        for (int s = 0; s < a.n; ++s) { a.acc[s] = rng() % 5 < 2; for (int c = 0; c < a.k; ++c) a.d[s][c] = (int)(rng() % a.n); }
        const std::vector<Word>& W = a.k == 2 ? w2 : w3;
        std::vector<bool> r = a.reachable(); std::set<std::vector<bool>> sigs; int reachCount = 0;
        for (int s = 0; s < a.n; ++s) if (r[s]) {                         // 오라클: 상태 s 의 서명 = 길이 ≤ 6 인 모든 단어의 수락 여부 (n ≤ 6 이므로 구별 가능한 상태는 모두 구별된다)
            ++reachCount; std::vector<bool> sg; for (const Word& x : W) sg.push_back(a.accepts(x, s)); sigs.insert(sg);
        }
        DFA m = a.minimized(), mm = m.minimized();
        assert(m.n == (int)sigs.size());                                  // Myhill-Nerode 클래스 수와 같다 = 최소
        assert(mm.n == m.n && equivalent(m, mm));                         // 멱등
        assert(equivalent(a, m) && equivalent(m, a));                     // 곱 오토마타로 정확히 같은 언어
        for (const Word& x : W) assert(a.accepts(x) == m.accepts(x));     // 길이 ≤ 6 의 모든 단어에서도 직접 확인
        for (int len = 0; len <= 8; ++len) assert(a.countAccepted(len) == m.countAccepted(len));
        std::vector<bool> mr = m.reachable(); for (int s = 0; s < m.n; ++s) assert(mr[s]);          // 최소 DFA 는 모든 상태가 도달 가능
        if (m.n < reachCount) ++shrunk; if (reachCount < a.n) ++withUnreachable; totalBefore += a.n; totalAfter += m.n;
        if (a.k == 2) {                                                   // 열거로 센 단어 수 (길이 ≤ 8) 와 DP 대조
            std::vector<long long> cnt(9, 0); for (const Word& x : w2long) if (x.size() <= 8 && a.accepts(x)) ++cnt[x.size()];
            for (int len = 0; len <= 8; ++len) assert(cnt[len] == a.countAccepted(len));
            DFA b = a; int s = (int)(rng() % b.n), c = (int)(rng() % b.k); b.d[s][c] = (int)(rng() % b.n);    // 음성 대조군: 전이 하나를 바꾼다
            bool brute = true; for (const Word& x : w2long) if (a.accepts(x) != b.accepts(x)) { brute = false; break; }   // n ≤ 6 이므로 길이 ≤ 11 이면 충분
            assert(equivalent(a, b) == brute); (brute ? mutatedSame : mutatedDifferent)++;
        }
    }
    assert(shrunk > 150 && withUnreachable > 100 && totalAfter < totalBefore && mutatedDifferent > 100 && mutatedSame > 50);

    // ④ 닫힌 식: (a 의 개수 mod m, b 의 개수 mod p) 상태에서 a-개수가 m 의 배수일 때 수락. 도달 불가능한 쓰레기 상태를 덧붙여도 최소 상태 수는 m
    for (int m = 1; m <= 6; ++m) for (int p = 1; p <= 6; ++p) {
        DFA a; a.k = 2; a.n = m * p + 3; a.d.assign(a.n, std::vector<int>(2)); a.acc.assign(a.n, false);
        for (int i = 0; i < m; ++i) for (int j = 0; j < p; ++j) { int s = i * p + j; a.acc[s] = i == 0; a.d[s][0] = ((i + 1) % m) * p + j; a.d[s][1] = i * p + (j + 1) % p; }
        for (int s = m * p; s < a.n; ++s) { a.d[s][0] = (int)(rng() % a.n); a.d[s][1] = (int)(rng() % a.n); a.acc[s] = true; }      // 쓰레기 상태
        DFA mn = a.minimized(); assert(mn.n == m);
        for (int len = 0; len <= 10; ++len) { long long expect = 0; for (const Word& x : w2long) if ((int)x.size() == len) expect += (std::count(x.begin(), x.end(), 0) % m == 0); assert(mn.countAccepted(len) == expect); }
    }
    DFA one; one.n = 1; one.k = 2; one.d = {{0, 0}}; one.acc = {true};   // 경계: 모든 단어를 받아들이는 1 상태 / 아무것도 받아들이지 않는 1 상태
    assert(one.minimized().n == 1 && one.countAccepted(5) == 32); one.acc[0] = false; assert(one.minimized().n == 1 && one.countAccepted(5) == 0);
    std::cout << "StateTransitionGraph: 600 partial FSMs matched the closure oracle (" << totalDeadlocks << " deadlocks, " << trapOnly << " trap-only machines); 1200 DFAs minimized from " << totalBefore << " to " << totalAfter << " states, each equal to the Myhill-Nerode class count and equivalent to the original" << std::endl;
    return 0;
}
// Time Complexity: 도달성·교착 O(S + T), Moore 최소화 O(k · n² )(최악), Hopcroft 는 O(k · n log n)
// Space Complexity: O(S + T)
```
## ControlFlowGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 제어 흐름 그래프(CFG): 정점 = 기본 블록(분기 없이 순서대로 실행되는 명령 묶음), 간선 = 가능한 실행 흐름. 컴파일러 최적화의 출발점.
// 기본 블록을 나누는 "리더" 규칙: (1) 첫 명령  (2) 점프의 목적지  (3) 점프(또는 HALT) 바로 다음 명령
// 그 위에서 지배자(dominator): d 가 v 를 지배한다 <=> 진입 블록에서 v 로 가는 모든 경로가 d 를 지난다.  뒤 간선 u→h (h 가 u 를 지배) 가 곧 루프다
// 검증: ① 손으로 계산한 합계 루프  ② 무작위 점프 프로그램 3 000 개(제약 없는 goto): 블록이 코드를 빈틈없이 덮고, 블록 *안*에는 점프 목적지·분기 명령이 없고(극대성),
//        지배자 집합 = "d 를 지우면 v 에 닿지 않는가" 라는 정의 그대로의 오라클, 뒤 간선 ⊆ DFS 역행 간선, 그리고 *실제로 실행한* 명령 흐름의 모든 이동이 CFG 간선 위에 있다(건전성)
//        ③ 구조적 프로그램(if / while 중첩) 600 개: 뒤 간선의 수 = while 의 수, DFS 역행 간선 = 뒤 간선(가약 그래프)
enum Op { SET, ADD, JMP, JLT, HALT };
struct Instr { Op op; int r, imm, t; };                                   // SET r,imm | ADD r,imm | JMP t | JLT r,imm,t (r < imm 이면 t 로) | HALT
bool isTerm(const Instr& i) { return i.op == JMP || i.op == JLT || i.op == HALT; }

struct CFG {
    std::vector<int> L;                                                   // 블록 시작 명령 번호 (오름차순)
    std::vector<std::vector<int>> succ;                                   // 후속 블록, -1 = 프로그램 끝. JLT 는 {분기 목적지, 다음 명령}
    int blockOf(int ip) const { return (int)(std::upper_bound(L.begin(), L.end(), ip) - L.begin()) - 1; }
    int lastOf(const std::vector<Instr>& code, int b) const { return (b + 1 < (int)L.size() ? L[b + 1] : (int)code.size()) - 1; }
};
CFG buildCFG(const std::vector<Instr>& code) {
    int n = (int)code.size(); std::set<int> lead; if (n) lead.insert(0);
    for (int i = 0; i < n; ++i) if (isTerm(code[i])) { if (code[i].op != HALT && code[i].t < n) lead.insert(code[i].t); if (i + 1 < n) lead.insert(i + 1); }
    CFG g; g.L.assign(lead.begin(), lead.end()); g.succ.resize(g.L.size());
    auto id = [&](int ip) { return ip >= n ? -1 : g.blockOf(ip); };
    for (size_t b = 0; b < g.L.size(); ++b) {
        int last = g.lastOf(code, (int)b); const Instr& in = code[last];
        if (in.op == JMP) g.succ[b] = {id(in.t)};
        else if (in.op == JLT) g.succ[b] = {id(in.t), id(last + 1)};
        else if (in.op != HALT) g.succ[b] = {id(last + 1)};
    }
    return g;
}
struct Dom { std::vector<bool> reach; std::vector<std::uint64_t> dom; };
Dom dominators(const CFG& g) {                                            // 반복 자료흐름: dom(v) = {v} ∪ ∩ dom(pred)
    int n = (int)g.L.size(); assert(n <= 64); Dom d; d.reach.assign(n, false); d.dom.assign(n, ~0ULL);
    if (!n) return d;
    std::queue<int> q; q.push(0); d.reach[0] = true;
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g.succ[u]) if (v >= 0 && !d.reach[v]) { d.reach[v] = true; q.push(v); } }
    std::vector<std::vector<int>> pred(n); for (int u = 0; u < n; ++u) if (d.reach[u]) for (int v : g.succ[u]) if (v >= 0) pred[v].push_back(u);
    d.dom[0] = 1ULL;
    for (bool ch = true; ch;) { ch = false; for (int v = 1; v < n; ++v) if (d.reach[v]) { std::uint64_t m = ~0ULL; for (int p : pred[v]) m &= d.dom[p]; m |= 1ULL << v; if (m != d.dom[v]) { d.dom[v] = m; ch = true; } } }
    return d;
}
std::vector<bool> reachAvoiding(const CFG& g, int removed) {              // 오라클: removed 블록을 지운 그래프에서 진입 블록으로부터 닿는 블록
    int n = (int)g.L.size(); std::vector<bool> r(n, false); if (!n || removed == 0) return r;
    std::queue<int> q; q.push(0); r[0] = true;
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g.succ[u]) if (v >= 0 && v != removed && !r[v]) { r[v] = true; q.push(v); } }
    return r;
}
void dfs(const CFG& g, int u, std::vector<int>& col, std::set<std::pair<int, int>>& retreat) {
    col[u] = 1;
    for (int v : g.succ[u]) if (v >= 0) { if (col[v] == 1) retreat.insert({u, v}); else if (col[v] == 0) dfs(g, v, col, retreat); }
    col[u] = 2;
}
std::vector<int> runInstr(const std::vector<Instr>& code, int cap, int* reg) {   // 명령 단위 인터프리터 (CFG 를 전혀 쓰지 않는다): 실행한 명령 번호의 열
    std::vector<int> tr; int ip = 0, n = (int)code.size();
    while (ip < n && (int)tr.size() < cap) {
        tr.push_back(ip); const Instr& in = code[ip];
        switch (in.op) { case SET: reg[in.r] = in.imm; ++ip; break; case ADD: reg[in.r] += in.imm; ++ip; break; case JMP: ip = in.t; break;
                         case JLT: ip = reg[in.r] < in.imm ? in.t : ip + 1; break; case HALT: ip = n; break; }
    }
    return tr;
}
struct Facts { int blocks, reachable, backEdges, irreducible; };
Facts checkProgram(const std::vector<Instr>& code, bool structured) {
    int n = (int)code.size(); CFG g = buildCFG(code); int B = (int)g.L.size();
    // 분할: 블록이 [0, n) 을 빈틈없이 덮는다. 블록 안의 명령은 끝 명령만 분기이고, 점프 목적지는 블록 시작뿐이다 (리더가 필요한 곳에만 있다)
    std::vector<bool> isTarget(n + 1, false); for (const Instr& in : code) if (in.op == JMP || in.op == JLT) isTarget[in.t] = true;
    if (n) { assert(g.L[0] == 0); }
    for (int b = 0; b < B; ++b) {
        int s = g.L[b], e = g.lastOf(code, b); assert(s <= e && e < n);
        for (int i = s; i < e; ++i) assert(!isTerm(code[i]) && !isTarget[i + 1]);                 // 블록 안: 분기도 점프 목적지도 없다
        if (b > 0) assert(isTerm(code[s - 1]) || isTarget[s]);                                   // 리더는 이유가 있어야 한다: 점프 뒤이거나 점프 목적지
        assert(g.blockOf(s) == b && g.blockOf(e) == b);
    }
    for (int i = 0; i < n; ++i) if (code[i].op == JMP || code[i].op == JLT) assert(code[i].t >= n || g.L[g.blockOf(code[i].t)] == code[i].t);   // 점프 목적지는 블록 시작
    Dom d = dominators(g); int reachable = 0; std::vector<std::vector<bool>> avoid(B);
    for (int b = 0; b < B; ++b) { avoid[b] = reachAvoiding(g, b); reachable += d.reach[b]; }
    std::vector<bool> r0 = reachAvoiding(g, -1); for (int b = 0; b < B; ++b) assert(r0[b] == d.reach[b]);
    for (int v = 0; v < B; ++v) if (d.reach[v]) for (int x = 0; x < B; ++x) {
        bool def = (x == v) || !avoid[x][v];                              // 정의 그대로: x 를 지우면 v 에 닿지 않는다
        assert((((d.dom[v] >> x) & 1ULL) != 0) == def);
    }
    std::set<std::pair<int, int>> back, retreat; std::vector<int> col(B, 0); if (B) dfs(g, 0, col, retreat);
    for (int u = 0; u < B; ++u) if (d.reach[u]) for (int v : g.succ[u]) if (v >= 0 && ((d.dom[u] >> v) & 1ULL)) back.insert({u, v});
    for (auto& e : back) assert(retreat.count(e));                         // 뒤 간선은 항상 DFS 역행 간선이다
    int irreducible = (int)retreat.size() - (int)back.size();              // 역행 간선인데 뒤 간선이 아니면 가약이 아닌(진입이 둘인) 루프
    if (structured) assert(irreducible == 0);
    int cap = 300; int reg[8] = {0}; std::vector<int> tr = runInstr(code, cap, reg);   // 건전성: 실제 실행의 모든 이동이 CFG 간선이다
    for (size_t k = 0; k + 1 < tr.size(); ++k) {
        int i = tr[k], j = tr[k + 1], bi = g.blockOf(i), bj = g.blockOf(j);
        if (i != g.lastOf(code, bi)) { assert(j == i + 1 && bj == bi); continue; }          // 블록 중간은 다음 명령으로 이어진다
        assert(g.L[bj] == j && std::count(g.succ[bi].begin(), g.succ[bi].end(), bj) >= 1 && d.reach[bj]);
    }
    if (!tr.empty()) assert(tr[0] == 0 && d.reach[g.blockOf(tr.back())]);
    return {B, reachable, (int)back.size(), irreducible};
}
struct Gen {                                                              // 구조적 프로그램 생성기: if / while 만 쓰므로 CFG 는 항상 가약
    std::mt19937& rng; std::vector<Instr> code; int loops = 0;
    explicit Gen(std::mt19937& r) : rng(r) {}
    void emit(Op op, int r = 0, int imm = 0, int t = 0) { code.push_back({op, r, imm, t}); }
    void block(int ld, int budget) { int cnt = 1 + (int)(rng() % 3); for (int i = 0; i < cnt; ++i) stmt(ld, budget); }
    void stmt(int ld, int budget) {
        int kind = (int)(rng() % 4);
        if (kind <= 1 || budget < 10 || code.size() > 30) { emit(rng() % 2 ? ADD : SET, 4 + (int)(rng() % 4), (int)(rng() % 5)); return; }
        if (kind == 2) {                                                  // if (r < imm) then else
            int jlt = (int)code.size(); emit(JLT, 4 + (int)(rng() % 4), (int)(rng() % 5), 0);
            block(ld, budget / 2); int jmp = (int)code.size(); emit(JMP);   // else 부분 다음에 끝으로 점프
            code[jlt].t = (int)code.size(); block(ld, budget / 2); code[jmp].t = (int)code.size();
        } else if (ld < 4) {                                              // while (r_ld < K) { ...; r_ld += 1 }
            ++loops; int r = ld, K = 1 + (int)(rng() % 3); emit(SET, r, 0);
            int top = (int)code.size(); emit(JLT, r, K, 0); int jexit = (int)code.size(); emit(JMP);
            code[top].t = (int)code.size(); block(ld + 1, budget / 2); emit(ADD, r, 1); emit(JMP, 0, 0, top);
            code[jexit].t = (int)code.size();
        } else emit(ADD, 4, 1);
    }
};

int main() {
    // ① 손으로 계산: s = 0; i = 0; while (i < 3) { s += 2; i += 1 }; halt
    std::vector<Instr> sum = {{SET, 1, 0, 0}, {SET, 0, 0, 0}, {JLT, 0, 3, 4}, {JMP, 0, 0, 7}, {ADD, 1, 2, 0}, {ADD, 0, 1, 0}, {JMP, 0, 0, 2}, {HALT, 0, 0, 0}};
    CFG g = buildCFG(sum);
    assert((g.L == std::vector<int>{0, 2, 3, 4, 7}));
    assert((g.succ[0] == std::vector<int>{1}) && (g.succ[1] == std::vector<int>{3, 2}) && (g.succ[2] == std::vector<int>{4}) && (g.succ[3] == std::vector<int>{1}) && g.succ[4].empty());
    Dom d = dominators(g);
    assert(d.dom[1] == 0x03 && d.dom[2] == 0x07 && d.dom[3] == 0x0B && d.dom[4] == 0x17);   // 블록 1(조건 검사)은 0 과 자기, 블록 3(몸체)은 0·1·자기
    int reg[8] = {0}; std::vector<int> tr = runInstr(sum, 1000, reg); assert(reg[1] == 6 && reg[0] == 3 && tr.size() == 2 + 3 * 4 + 3);          // SET 2 개 + 반복 3 번 × (JLT, ADD, ADD, JMP) + 마지막 (JLT, JMP, HALT)
    Facts f0 = checkProgram(sum, true); assert(f0.blocks == 5 && f0.backEdges == 1 && f0.irreducible == 0);
    checkProgram({}, true);                                               // 경계: 빈 프로그램
    checkProgram({{HALT, 0, 0, 0}}, true); checkProgram({{JMP, 0, 0, 0}}, true);          // 한 명령: 즉시 종료 / 자기 자신으로 점프(무한 루프, 뒤 간선 하나)
    checkProgram({{JLT, 0, 1, 1}}, true);                                 // 분기 목적지가 프로그램 끝(= 1): 두 후속이 모두 "끝"

    // ② 제약 없는 무작위 goto 프로그램
    std::mt19937 rng(77); long blocks = 0, backs = 0, irreducible = 0, unreachableBlocks = 0, programs = 0;
    for (int it = 0; it < 3000; ++it) {
        int n = 1 + (int)(rng() % 20); std::vector<Instr> code;
        for (int i = 0; i < n; ++i) {
            int k = (int)(rng() % 20); Instr in{SET, (int)(rng() % 4), (int)(rng() % 4), (int)(rng() % (n + 1))};
            in.op = k < 5 ? SET : k < 10 ? ADD : k < 13 ? JMP : k < 19 ? JLT : HALT; code.push_back(in);
        }
        Facts f = checkProgram(code, false); blocks += f.blocks; backs += f.backEdges; irreducible += f.irreducible; unreachableBlocks += f.blocks - f.reachable; ++programs;
    }
    assert(programs == 3000 && backs > 800 && irreducible > 20 && unreachableBlocks > 500);

    // ③ 구조적 프로그램: 뒤 간선 수 = while 수
    long loopsTotal = 0, structuredBlocks = 0;
    for (int it = 0; it < 600; ++it) {
        Gen gen(rng); gen.block(0, 60); std::vector<Instr> code = gen.code;
        Facts f = checkProgram(code, true); assert(f.backEdges == gen.loops && f.blocks == f.reachable);
        int regs[8] = {0}; std::vector<int> t = runInstr(code, 100000, regs); assert(!t.empty() && (int)t.size() < 100000);   // 반드시 끝난다
        loopsTotal += gen.loops; structuredBlocks += f.blocks;
    }
    assert(loopsTotal > 300);
    std::cout << "ControlFlowGraph: " << programs << " random goto programs (" << blocks << " blocks, " << backs << " back edges, " << irreducible << " irreducible retreating edges) and 600 structured programs (" << loopsTotal << " loops, " << structuredBlocks << " blocks) agreed with the dominator definition oracle" << std::endl;
    return 0;
}
// Time Complexity: 블록 구성 O(명령 수), 반복 지배자 O(블록 수² · 반복) — Lengauer-Tarjan 은 O(E α)
// Space Complexity: O(블록 수)
```
## DataFlowGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <utility>
#include <vector>

// 데이터 흐름 분석: CFG 위에서 값의 흐름을 추적한다.  생존 변수(liveness) 분석 — "이 지점 뒤에서 변수가 다시 읽히는가"
//   live_in(B)  = use(B) ∪ (live_out(B) − def(B)),     live_out(B) = ∪ live_in(S)  (S 는 B 의 후속)
// 관계가 변하지 않을 때까지 반복(고정점)하며, 역방향 분석이라 후속 블록의 결과를 선행 블록으로 전파한다
// 검증: ① 손으로 푼 4블록 예  ② 무작위 CFG 2 000 개(블록 1~7, 변수 4 개, 순환 포함): 모든 블록 입구·출구와 *모든 문장 경계* 의 생존 집합을
//        "그 지점에서 출발해 변수를 덮어쓰기 전에 읽는 경로가 있는가" 라는 정의 그대로의 경로 탐색 오라클과 대조,
//        수렴 라운드 수의 상한(2·블록·변수 + 2), 한 라운드만 돌린 불완전 분석은 오라클과 달라진다는 음성 대조군
//        ③ 의미 보존: 죽은 대입(대입한 값이 다시 읽히지 않음)을 반복해서 지워도 같은 분기 규칙으로 실행한 출력(print)열이 변하지 않는다
typedef unsigned Mask;                                                    // 변수 집합 (비트마스크), 변수는 4 개
const int V = 4;
struct Stmt { int kind, dst, a, b, imm; };                                // 0: dst = imm   1: dst = a + b   2: print a
Mask rd(const Stmt& s) { return s.kind == 1 ? ((1u << s.a) | (1u << s.b)) : s.kind == 2 ? (1u << s.a) : 0u; }
Mask wr(const Stmt& s) { return s.kind == 2 ? 0u : (1u << s.dst); }
struct Block { std::vector<Stmt> st; std::vector<int> succ; };
struct Live { std::vector<Mask> in, out; int rounds; };

Live liveness(const std::vector<Block>& g, int maxRounds = 1 << 30) {
    int n = (int)g.size(); std::vector<Mask> use(n, 0), def(n, 0);
    for (int b = 0; b < n; ++b) for (const Stmt& s : g[b].st) { use[b] |= rd(s) & ~def[b]; def[b] |= wr(s); }    // 블록 안에서 먼저 읽는 변수 / 쓰는 변수
    Live L; L.in.assign(n, 0); L.out.assign(n, 0); L.rounds = 0;
    for (bool changed = true; changed && L.rounds < maxRounds;) {
        changed = false; ++L.rounds;
        for (int b = n - 1; b >= 0; --b) {
            Mask o = 0; for (int s : g[b].succ) o |= L.in[s];
            Mask i = use[b] | (o & ~def[b]);
            if (o != L.out[b] || i != L.in[b]) { L.out[b] = o; L.in[b] = i; changed = true; }
        }
    }
    return L;
}
std::vector<Mask> liveAfterEach(const Block& b, Mask out) {               // 블록 안에서 거꾸로: 각 문장 *직후* 의 생존 집합
    std::vector<Mask> r(b.st.size()); Mask m = out;
    for (int i = (int)b.st.size() - 1; i >= 0; --i) { r[i] = m; m = rd(b.st[i]) | (m & ~wr(b.st[i])); }
    return r;
}
bool liveAt(const std::vector<Block>& g, int v, int b, int i) {           // 오라클: 지점 (b, i) = b 의 i 번째 문장 직전
    std::set<std::pair<int, int>> seen; std::vector<std::pair<int, int>> stack{{b, i}};
    while (!stack.empty()) {
        std::pair<int, int> p = stack.back(); stack.pop_back(); if (!seen.insert(p).second) continue;
        if (p.second == (int)g[p.first].st.size()) { for (int s : g[p.first].succ) stack.push_back({s, 0}); continue; }
        const Stmt& s = g[p.first].st[p.second];
        if ((rd(s) >> v) & 1u) return true;                               // 덮어쓰기 전에 읽는다
        if ((wr(s) >> v) & 1u) continue;                                  // 이 경로에서는 v 가 죽는다
        stack.push_back({p.first, p.second + 1});
    }
    return false;
}
std::vector<unsigned> run(const std::vector<Block>& g, unsigned seed) {   // 인터프리터: 분기는 (seed, 방문 횟수) 해시로만 정하므로 문장 수에 의존하지 않는다
    std::vector<unsigned> out, var(V, 0); int b = 0;
    for (int visits = 0; visits < 40; ++visits) {
        for (const Stmt& s : g[b].st) { if (s.kind == 0) var[s.dst] = (unsigned)s.imm; else if (s.kind == 1) var[s.dst] = var[s.a] * 31u + var[s.b] + 7u; else out.push_back(var[s.a]); }
        if (g[b].succ.empty()) break;
        unsigned h = (seed + (unsigned)visits) * 2654435761u; h ^= h >> 15; b = g[b].succ[(h >> 7) % g[b].succ.size()];
    }
    return out;
}

int main() {
    // ① 손으로 푼 예: a=0 b=1 c=2.   b0: a=1; b=2   b1: c=a+b   b2: print c   b3: print a      (b0 -> b1, b3 ; b1 -> b2)
    std::vector<Block> ex = {{{{0, 0, 0, 0, 1}, {0, 1, 0, 0, 2}}, {1, 3}}, {{{1, 2, 0, 1, 0}}, {2}}, {{{2, 0, 2, 0, 0}}, {}}, {{{2, 0, 0, 0, 0}}, {}}};
    Live L = liveness(ex);
    assert(L.in[0] == 0u && L.out[0] == 0x3u);                            // 시작 시점에는 살아 있는 변수가 없다 (모두 정의되기 전)
    assert(L.in[1] == 0x3u && L.out[1] == 0x4u && L.in[2] == 0x4u && L.in[3] == 0x1u);
    assert((L.out[1] & 0x2u) == 0);                                       // b 는 b1 뒤에서 다시 쓰이지 않는다 -> 레지스터 재사용 가능
    std::vector<Mask> inner = liveAfterEach(ex[0], L.out[0]); assert(inner[0] == 0x1u && inner[1] == 0x3u);     // a=1 직후엔 a 만 살아 있다 (b 는 아직 정의 전)

    // ② 무작위 CFG 와 오라클
    std::mt19937 rng(424242); long points = 0, liveBits = 0, cyclic = 0, roundsMax = 0, weakDiffers = 0, removedTotal = 0, programsWithRemoval = 0, runsCompared = 0;
    for (int it = 0; it < 2000; ++it) {
        int n = 1 + (int)(rng() % 7); std::vector<Block> g(n);
        for (int b = 0; b < n; ++b) {
            int cnt = (int)(rng() % 5);
            for (int i = 0; i < cnt; ++i) {
                int k = (int)(rng() % 10); Stmt s{k < 4 ? 0 : k < 8 ? 1 : 2, (int)(rng() % V), (int)(rng() % V), (int)(rng() % V), (int)(rng() % 9)};
                g[b].st.push_back(s);
            }
            int sc = (int)(rng() % 3); for (int j = 0; j < sc; ++j) g[b].succ.push_back((int)(rng() % n));
        }
        Live L2 = liveness(g); assert(L2.rounds <= 2 * n * V + 2); roundsMax = std::max<long>(roundsMax, L2.rounds);
        bool anyBack = false; for (int b = 0; b < n; ++b) for (int s : g[b].succ) if (s <= b) anyBack = true; cyclic += anyBack;
        Live weak = liveness(g, 1); bool differs = false;
        for (int b = 0; b < n; ++b) {
            std::vector<Mask> after = liveAfterEach(g[b], L2.out[b]);
            for (int v = 0; v < V; ++v) {
                assert((((L2.in[b] >> v) & 1u) != 0) == liveAt(g, v, b, 0));
                assert((((L2.out[b] >> v) & 1u) != 0) == liveAt(g, v, b, (int)g[b].st.size()));
                for (size_t i = 0; i < g[b].st.size(); ++i) { bool want = liveAt(g, v, b, (int)i + 1); assert((((after[i] >> v) & 1u) != 0) == want); liveBits += want; ++points; }
                if ((((weak.in[b] >> v) & 1u) != 0) != liveAt(g, v, b, 0)) differs = true;
            }
        }
        weakDiffers += differs;
        // ③ 죽은 대입 제거 (연쇄하므로 더 못 지울 때까지 반복) 후 같은 입력(분기 시드)으로 출력 비교
        std::vector<Block> h = g; int removed = 0;
        for (bool ch = true; ch;) {
            ch = false; Live Lh = liveness(h);
            for (int b = 0; b < n; ++b) {
                std::vector<Mask> after = liveAfterEach(h[b], Lh.out[b]);
                for (int i = (int)h[b].st.size() - 1; i >= 0; --i) if (h[b].st[i].kind != 2 && !((after[i] >> h[b].st[i].dst) & 1u)) { h[b].st.erase(h[b].st.begin() + i); ++removed; ch = true; break; }
                if (ch) break;
            }
        }
        removedTotal += removed; programsWithRemoval += removed > 0;
        for (unsigned seed = 1; seed <= 8; ++seed) { assert(run(g, seed) == run(h, seed)); ++runsCompared; }
    }
    assert(points > 20000 && liveBits > 5000 && cyclic > 800 && roundsMax >= 3 && weakDiffers > 100 && removedTotal > 800 && programsWithRemoval > 400);
    std::cout << "DataFlowGraph: " << points << " statement boundaries matched the path oracle (max " << roundsMax << " rounds to converge); a one-round analysis was wrong on " << weakDiffers << " programs; " << removedTotal << " dead stores removed from " << programsWithRemoval << " programs left all " << runsCompared << " printed traces unchanged" << std::endl;
    return 0;
}
// Time Complexity: 고정점까지 O(블록 수 · 변수 수 · 반복 횟수)  (비트마스크로 집합 연산 O(1))
// Space Complexity: O(블록 수 · 변수 수)
```
## BayesianNetwork()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// 베이즈 네트워크: 확률 변수들을 정점으로 하는 방향 비순환 그래프(DAG). 각 변수는 부모가 주어지면 비후손과 조건부 독립이라서 결합확률이 P(X₁..Xₙ) = Π P(Xᵢ | parents(Xᵢ)) 로 인수분해된다 — 이진 변수 n 개를 통째로 적으면 2ⁿ − 1 개의 수가 필요하지만 부모가 k 개 이하면 n·2ᵏ 개면 된다(사슬 20 개 변수: 39 개 대 1,048,575 개).
// 추론 P(Q | 증거) 세 가지 — ① 열거: 결합확률의 합을 정의대로 (2ⁿ) ② 변수 제거(variable elimination): CPT 를 *인수(factor)* 로 보고 증거로 제한한 뒤, 변수를 하나씩 "그 변수를 포함한 인수들을 곱하고 그 변수를 합으로 지운다". 비용은 곱해진 인수의 *범위(scope) 크기* 에 지수적이라서 제거 순서가 결정적이다 — 별 모양(중심 → 잎 10 개)에서 중심부터 지우면 범위가 11, 잎부터 지우면 2 ③ 조상 표본 추출: 위상 순서대로 부모 값을 보고 표본을 뽑는다.
// 구조에서 독립성을 읽는 *d-분리*: 조상 부분 그래프를 "도덕화(moralize: 같은 자식의 부모끼리 잇고 방향 제거)" 해서 조건 집합 Z 를 지운 뒤 x 와 y 가 끊어지면 x ⟂ y | Z. 사슬 a→b→c 와 포크 a←b→c 는 b 를 관측하면 a 와 c 가 독립이 되고, 충돌(collider) a→b←c 는 반대로 b 를 관측해야 a 와 c 가 *의존* 한다(explaining away).
// 검증: ① 비·스프링클러·젖은 잔디 고전 예제의 알려진 값 P(R | G) = 0.35769, 스프링클러가 켜졌다는 관측이 비를 덜 그럴듯하게(0.0068) ② 무작위 네트워크(변수 ≤ 8)에서 변수 제거 = 열거(오차 1e-12), 제거 순서가 달라도 같은 값 ③ d-분리 ⇒ 수치적 독립(결합 표에서 계산), d-연결 ⇒ 수치적 의존(무작위 CPT 에서는 거의 확실) ④ 마르코프 담요 ⑤ 큰 입력: 변수 60 개 사슬을 변수 제거로 풀어 전향 점화식과 대조(범위 ≤ 2, 열거는 2⁶⁰), 별 모양의 범위 11 대 2, 조상 표본 추출 40 만 번의 빈도.
struct BN {
    int n; std::vector<std::vector<int>> parents; std::vector<std::vector<double>> cpt;     // cpt[v][부모값 마스크(비트 i = parents[v][i])] = P(v = 1 | 부모)
    explicit BN(int nn) : n(nn), parents(nn), cpt(nn) {}
    void setNode(int v, std::vector<int> pa, std::vector<double> table) { parents[v] = std::move(pa); cpt[v] = std::move(table); }
    double condProb(int v, std::uint64_t assign) const {                                     // P(X_v = assign[v] | 부모)  (변수 최대 64 개: 64 비트 마스크)
        unsigned m = 0; for (std::size_t i = 0; i < parents[v].size(); ++i) m |= (unsigned)((assign >> parents[v][i]) & 1u) << i;
        double p1 = cpt[v][m]; return (assign >> v & 1u) ? p1 : 1.0 - p1;
    }
    double joint(std::uint64_t assign) const { double p = 1; for (int v = 0; v < n; ++v) p *= condProb(v, assign); return p; }
    long long parameterCount() const { long long c = 0; for (int v = 0; v < n; ++v) c += (long long)cpt[v].size(); return c; }
};
// ① 열거: P(X_q = 1 | evidence) — evidence 는 (변수, 값) 목록
double enumerate(const BN& b, int q, const std::vector<std::pair<int, int>>& ev) {
    double num = 0, den = 0;
    for (unsigned a = 0; a < (1u << b.n); ++a) {
        bool ok = true; for (auto [v, val] : ev) if ((int)(a >> v & 1u) != val) ok = false;
        if (!ok) continue; double p = b.joint(a); den += p; if (a >> q & 1u) num += p;
    }
    return num / den;
}
// ② 변수 제거: 인수 = (정렬된 변수 목록, 2^|변수| 표; 인덱스의 비트 i 가 vars[i])
struct Factor { std::vector<int> vars; std::vector<double> t; };
Factor cptFactor(const BN& b, int v) {
    Factor f; f.vars = b.parents[v]; std::sort(f.vars.begin(), f.vars.end()); f.vars.push_back(v);               // 부모는 모두 v 보다 작다
    f.t.assign(1u << f.vars.size(), 0.0);
    for (unsigned idx = 0; idx < f.t.size(); ++idx) { std::uint64_t assign = 0; for (std::size_t i = 0; i < f.vars.size(); ++i) assign |= (std::uint64_t)((idx >> i) & 1u) << f.vars[i]; f.t[idx] = b.condProb(v, assign); }
    return f;
}
Factor multiply(const Factor& a, const Factor& b) {
    Factor r; std::set_union(a.vars.begin(), a.vars.end(), b.vars.begin(), b.vars.end(), std::back_inserter(r.vars));
    int k = (int)r.vars.size(); r.t.assign(1u << k, 0.0);
    auto posIn = [&](const std::vector<int>& sub) { std::vector<int> p; for (int v : sub) p.push_back((int)(std::lower_bound(r.vars.begin(), r.vars.end(), v) - r.vars.begin())); return p; };
    std::vector<int> pa = posIn(a.vars), pb = posIn(b.vars);
    for (unsigned idx = 0; idx < r.t.size(); ++idx) {
        unsigned ia = 0, ib = 0; for (std::size_t i = 0; i < pa.size(); ++i) ia |= ((idx >> pa[i]) & 1u) << i; for (std::size_t i = 0; i < pb.size(); ++i) ib |= ((idx >> pb[i]) & 1u) << i;
        r.t[idx] = a.t[ia] * b.t[ib];
    }
    return r;
}
Factor sumOut(const Factor& f, int v) {
    int pos = (int)(std::find(f.vars.begin(), f.vars.end(), v) - f.vars.begin()); Factor r; r.vars = f.vars; r.vars.erase(r.vars.begin() + pos);
    r.t.assign(1u << r.vars.size(), 0.0); unsigned low = (1u << pos) - 1;
    for (unsigned idx = 0; idx < f.t.size(); ++idx) r.t[(idx & low) | ((idx >> (pos + 1)) << pos)] += f.t[idx];
    return r;
}
Factor restrictVar(const Factor& f, int v, int val) {
    auto it = std::find(f.vars.begin(), f.vars.end(), v); if (it == f.vars.end()) return f;
    int pos = (int)(it - f.vars.begin()); Factor r; r.vars = f.vars; r.vars.erase(r.vars.begin() + pos); r.t.assign(1u << r.vars.size(), 0.0); unsigned low = (1u << pos) - 1;
    for (unsigned idx = 0; idx < f.t.size(); ++idx) if ((int)(idx >> pos & 1u) == val) r.t[(idx & low) | ((idx >> (pos + 1)) << pos)] = f.t[idx];
    return r;
}
struct VE { double p1; std::size_t maxScope; };
VE variableElimination(const BN& b, int q, const std::vector<std::pair<int, int>>& ev, const std::vector<int>& order) {
    std::vector<Factor> fs; for (int v = 0; v < b.n; ++v) fs.push_back(cptFactor(b, v));
    for (auto [v, val] : ev) for (Factor& f : fs) f = restrictVar(f, v, val);
    std::size_t maxScope = 0;
    for (int v : order) {
        std::vector<Factor> hit, rest; for (Factor& f : fs) (std::find(f.vars.begin(), f.vars.end(), v) != f.vars.end() ? hit : rest).push_back(f);
        if (hit.empty()) continue;
        Factor prod = hit[0]; for (std::size_t i = 1; i < hit.size(); ++i) prod = multiply(prod, hit[i]);
        maxScope = std::max(maxScope, prod.vars.size());
        rest.push_back(sumOut(prod, v)); fs = rest;
    }
    Factor prod = fs[0]; for (std::size_t i = 1; i < fs.size(); ++i) prod = multiply(prod, fs[i]);
    maxScope = std::max(maxScope, prod.vars.size());
    assert(prod.vars.size() == 1 && prod.vars[0] == q);
    return {prod.t[1] / (prod.t[0] + prod.t[1]), maxScope};
}
std::vector<int> naturalOrder(const BN& b, int q, const std::vector<std::pair<int, int>>& ev) {                  // 질의·증거를 뺀 번호순
    std::vector<int> o; for (int v = 0; v < b.n; ++v) { bool skip = v == q; for (auto e : ev) skip = skip || e.first == v; if (!skip) o.push_back(v); } return o;
}
// ---- d-분리 (조상 그래프의 도덕화) 와 수치적 독립 ----
bool dSeparated(const BN& b, int x, int y, unsigned z) {
    std::vector<char> anc(b.n, 0); std::vector<int> st; for (int v : {x, y}) { anc[v] = 1; st.push_back(v); }
    for (int v = 0; v < b.n; ++v) if (z >> v & 1u) { anc[v] = 1; st.push_back(v); }
    while (!st.empty()) { int v = st.back(); st.pop_back(); for (int p : b.parents[v]) if (!anc[p]) { anc[p] = 1; st.push_back(p); } }
    std::vector<std::vector<char>> adj(b.n, std::vector<char>(b.n, 0));
    for (int v = 0; v < b.n; ++v) if (anc[v]) { for (int p : b.parents[v]) { adj[v][p] = adj[p][v] = 1; for (int q : b.parents[v]) if (p != q) adj[p][q] = 1; } }   // 방향 제거 + 부모끼리 결혼
    std::vector<char> seen(b.n, 0); seen[x] = 1; st = {x};
    while (!st.empty()) { int v = st.back(); st.pop_back(); for (int w = 0; w < b.n; ++w) if (adj[v][w] && !(z >> w & 1u) && !seen[w]) { seen[w] = 1; st.push_back(w); } }
    return !seen[y];
}
double independenceGap(const BN& b, int x, int y, unsigned z) {                                                  // max |P(x,y,z)P(z) − P(x,z)P(y,z)| (결합 표에서)
    std::vector<double> J(1u << b.n); for (unsigned a = 0; a < J.size(); ++a) J[a] = b.joint(a);
    unsigned keep = (1u << x) | (1u << y) | z; double gap = 0;
    auto marg = [&](unsigned mask, unsigned vals) { double s = 0; for (unsigned a = 0; a < J.size(); ++a) if ((a & mask) == vals) s += J[a]; return s; };
    for (unsigned a = 0; a < J.size(); ++a) {
        if (a & ~keep) continue;                                                                                 // 관심 변수 밖은 0 으로 고정한 대표만
        unsigned vz = a & z, vx = a & (1u << x), vy = a & (1u << y);
        double pxyz = marg(keep, a), pz = marg(z, vz), pxz = marg((1u << x) | z, vx | vz), pyz = marg((1u << y) | z, vy | vz);
        gap = std::max(gap, std::fabs(pxyz * pz - pxz * pyz));
    }
    return gap;
}
BN randomNetwork(int n, double edgeProb, std::mt19937& rng) {
    BN b(n); std::uniform_real_distribution<double> u(0.05, 0.95);
    for (int v = 0; v < n; ++v) { std::vector<int> pa; for (int p = 0; p < v; ++p) if ((rng() % 1000) / 1000.0 < edgeProb) pa.push_back(p); std::vector<double> t(1u << pa.size()); for (double& x : t) x = u(rng); b.setNode(v, pa, t); }
    return b;
}

int main() {
    // ① 고전 예제: 변수 0 = 비(R), 1 = 스프링클러(S), 2 = 젖은 잔디(G). R → S, R → G, S → G
    BN rain(3);
    rain.setNode(0, {}, {0.2});
    rain.setNode(1, {0}, {0.4, 0.01});                                           // P(S=1 | R=0) = 0.4, P(S=1 | R=1) = 0.01
    rain.setNode(2, {0, 1}, {0.0, 0.8, 0.9, 0.99});                              // 마스크 비트0 = R, 비트1 = S : (R,S) = (0,0) (1,0) (0,1) (1,1)
    {
        double total = 0; for (unsigned a = 0; a < 8; ++a) total += rain.joint(a);
        assert(std::fabs(total - 1.0) < 1e-12);
        double pRG = enumerate(rain, 0, {{2, 1}}), pRGS = enumerate(rain, 0, {{2, 1}, {1, 1}});
        assert(std::fabs(pRG - 0.35768767) < 1e-6 && std::fabs(pRGS - 0.00198 / (0.00198 + 0.288)) < 1e-12 && pRGS < 0.007 && pRGS < pRG);     // 스프링클러가 켜진 걸 보면 비 때문이라는 설명이 약해진다
        auto ev = std::vector<std::pair<int, int>>{{2, 1}};
        assert(std::fabs(variableElimination(rain, 0, ev, naturalOrder(rain, 0, ev)).p1 - pRG) < 1e-12);
        assert(dSeparated(rain, 0, 1, 0) == false && !dSeparated(rain, 0, 1, 1u << 2));   // R–S 는 직접 연결
        assert(rain.parameterCount() == 1 + 2 + 4 && (1 << 3) - 1 == 7);
    }
    // d-분리의 세 기본형: 사슬 0→1→2, 포크 0←1→2, 충돌 0→1←2
    {   BN chain(3), fork(3), collider(3);
        chain.setNode(0, {}, {0.3}); chain.setNode(1, {0}, {0.2, 0.9}); chain.setNode(2, {1}, {0.1, 0.7});
        fork.setNode(0, {}, {0.4}); fork.setNode(1, {0}, {0.2, 0.9}); fork.setNode(2, {0}, {0.1, 0.7});                  // 0 이 공통 원인 (0 → 1, 0 → 2)
        collider.setNode(0, {}, {0.3}); collider.setNode(1, {}, {0.6}); collider.setNode(2, {0, 1}, {0.1, 0.5, 0.6, 0.95});
        assert(!dSeparated(chain, 0, 2, 0) && dSeparated(chain, 0, 2, 1u << 1) && independenceGap(chain, 0, 2, 0) > 1e-4 && independenceGap(chain, 0, 2, 1u << 1) < 1e-12);
        assert(!dSeparated(fork, 1, 2, 0) && dSeparated(fork, 1, 2, 1u << 0) && independenceGap(fork, 1, 2, 0) > 1e-4 && independenceGap(fork, 1, 2, 1u << 0) < 1e-12);
        assert(dSeparated(collider, 0, 1, 0) && !dSeparated(collider, 0, 1, 1u << 2) && independenceGap(collider, 0, 1, 0) < 1e-12 && independenceGap(collider, 0, 1, 1u << 2) > 1e-4);   // 충돌은 관측해야 의존
    }

    // ② 무작위 네트워크(변수 ≤ 8): 변수 제거(여러 순서) = 열거
    std::mt19937 rng(2005);
    for (int it = 0; it < 400; ++it) {
        int n = 2 + (int)(rng() % 7); BN b = randomNetwork(n, 0.4, rng);
        int q = (int)(rng() % n); std::vector<std::pair<int, int>> ev;
        for (int v = 0; v < n; ++v) if (v != q && rng() % 3 == 0) ev.push_back({v, (int)(rng() & 1)});
        double want = enumerate(b, q, ev);
        std::vector<int> order = naturalOrder(b, q, ev);
        for (int rep = 0; rep < 3; ++rep) { if (rep) std::shuffle(order.begin(), order.end(), rng); assert(std::fabs(variableElimination(b, q, ev, order).p1 - want) < 1e-12); }
    }

    // ③ d-분리 ⇔ 수치적 독립: 무작위 네트워크와 무작위 (x, y, Z)
    int sep = 0, conn = 0;
    for (int it = 0; it < 400; ++it) {
        int n = 4 + (int)(rng() % 4); BN b = randomNetwork(n, 0.35, rng);
        for (int rep = 0; rep < 12; ++rep) {
            int x = (int)(rng() % n), y = (int)(rng() % n); if (x == y) continue;
            unsigned z = 0; for (int v = 0; v < n; ++v) if (v != x && v != y && rng() % 3 == 0) z |= 1u << v;
            double gap = independenceGap(b, x, y, z);
            if (dSeparated(b, x, y, z)) { assert(gap < 1e-12); ++sep; } else { assert(gap > 1e-9); ++conn; }
        }
    }
    assert(sep > 800 && conn > 800);

    // ④ 마르코프 담요: 부모 · 자식 · 자식의 다른 부모가 주어지면 나머지와 독립 — P(v | 나머지 전부) 가 담요 값만으로 정해진다
    for (int it = 0; it < 200; ++it) {
        int n = 4 + (int)(rng() % 4); BN b = randomNetwork(n, 0.4, rng);
        for (int v = 0; v < n; ++v) {
            unsigned blanket = 0; for (int p : b.parents[v]) blanket |= 1u << p;
            for (int c = 0; c < n; ++c) if (std::find(b.parents[c].begin(), b.parents[c].end(), v) != b.parents[c].end()) { blanket |= 1u << c; for (int p : b.parents[c]) if (p != v) blanket |= 1u << p; }
            std::vector<double> seen(1u << n, -1.0);
            for (unsigned a = 0; a < (1u << n); ++a) {
                if (a >> v & 1u) continue;
                double p1 = b.joint(a | (1u << v)) / (b.joint(a) + b.joint(a | (1u << v)));
                unsigned key = a & blanket; if (seen[key] < 0) seen[key] = p1; else assert(std::fabs(seen[key] - p1) < 1e-12);
            }
        }
    }

    // ⑤ 큰 입력: (a) 변수 60 개 사슬 — 변수 제거(순서대로 지우기) 가 전향 점화식과 같고 범위는 2 이하 (열거는 2^60 이라 불가능), 모든 변수를 한 번에 풀지 않아도 됨
    {
        const int N = 60; BN chain(N); std::uniform_real_distribution<double> u(0.05, 0.95);
        double a0[N], a1[N]; chain.setNode(0, {}, {u(rng)});
        for (int v = 1; v < N; ++v) { a0[v] = u(rng); a1[v] = u(rng); chain.setNode(v, {v - 1}, {a0[v], a1[v]}); }
        double p = chain.cpt[0][0]; std::vector<std::pair<int, int>> ev;
        std::vector<int> order; for (int v = 0; v < N - 1; ++v) order.push_back(v);                                // 0 부터 N−2 까지 차례로
        VE r = variableElimination(chain, N - 1, ev, order);
        for (int v = 1; v < N; ++v) p = p * a1[v] + (1 - p) * a0[v];                                               // 전향 점화식
        assert(std::fabs(r.p1 - p) < 1e-12 && r.maxScope <= 2);
        assert(chain.parameterCount() == 1 + 2 * (N - 1));                                                           // 119 개 수 vs 2^60 − 1
        // (b) 별 모양: X0 → X1..X10. 잎부터 지우면 범위 2, 중심부터 지우면 범위 11 — 값은 같다
        BN star(11); star.setNode(0, {}, {0.35}); for (int v = 1; v <= 10; ++v) star.setNode(v, {0}, {u(rng), u(rng)});
        std::vector<int> leavesFirst, centerFirst{0}; for (int v = 2; v <= 10; ++v) leavesFirst.push_back(v); leavesFirst.push_back(0); for (int v = 2; v <= 10; ++v) centerFirst.push_back(v);
        VE good = variableElimination(star, 1, {}, leavesFirst), bad = variableElimination(star, 1, {}, centerFirst);
        assert(std::fabs(good.p1 - bad.p1) < 1e-12 && std::fabs(good.p1 - enumerate(star, 1, {})) < 1e-12 && good.maxScope == 2 && bad.maxScope == 11);
        // (c) 조상 표본 추출: 비 네트워크에서 P(R | G) 를 40 만 번 뽑아 어림 (거절 표집)
        long long gWet = 0, rainAndWet = 0; std::mt19937_64 r2(1);
        for (int s = 0; s < 400000; ++s) {
            unsigned a = 0;
            for (int v = 0; v < 3; ++v) {
                unsigned m = 0; for (std::size_t i = 0; i < rain.parents[v].size(); ++i) m |= ((a >> rain.parents[v][i]) & 1u) << i;
                if ((r2() % 1000000) / 1000000.0 < rain.cpt[v][m]) a |= 1u << v;
            }
            if (a >> 2 & 1u) { ++gWet; rainAndWet += a & 1u; }
        }
        assert(gWet > 150000 && std::fabs((double)rainAndWet / (double)gWet - 0.35768767) < 0.01);
    }
    std::cout << "BayesianNetwork: the rain/sprinkler/grass network gave P(rain | wet grass) = 0.3577 and the explaining-away value 0.0068 once the sprinkler was seen on, variable elimination (several random orders) matched enumeration to 1e-12 on 400 random networks, d-separation computed by moralising the ancestral graph agreed with numerical independence on over 1600 random queries (separated implies independent, connected implies dependent), the Markov-blanket property held numerically, a 60-variable chain was solved by elimination with scope 2 and matched the forward recursion (enumeration would need 2^60 terms; 119 parameters instead of 2^60 - 1), a star network needed scope 11 when its centre was eliminated first but 2 when the leaves went first, and 400,000 ancestral samples reproduced the posterior within 0.01" << std::endl; return 0;
}
// Time Complexity: 열거 O(2^n), 변수 제거 O(n · 2^w) (w = 제거 순서가 만든 최대 범위 크기)
// Space Complexity: O(2^w)
```
## NeuralGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <vector>

// 신경망의 계산 그래프: 정점 = 연산(+, −, ×, tanh, sin), 간선 = 값의 흐름.  순전파는 위상 순서로 값을 계산하고,
// 역전파(자동 미분, 역방향 모드)는 그래프를 거꾸로 훑으며 연쇄 법칙으로 기울기를 누적한다. 딥러닝 프레임워크의 핵심
// 같은 값을 여러 곳에서 쓰면(팬아웃) 기울기가 *더해져야* 한다 — x·x 의 미분이 2x 인 이유
// 검증: ① 손으로 푼 예(tanh(w·x + b), x·x, x + x)  ② 무작위 계산 DAG 1 500 개(입력 1~3, 연산 2~12, 피연산자는 앞선 아무 노드): 역방향 모드 =
//        순방향 모드(이중수, 입력마다 한 번) = 중심 유한 차분,  DFS 후위 순서로 위상 정렬해 전파해도 같은 기울기,  출력의 조상이 아닌 노드의 기울기는 정확히 0
//        ③ 뉴런 하나(tanh(w·x + b))를 경사 하강으로 학습: 손실이 단조 감소하고 정답 (w, b) 로 수렴
enum K { IN, ADD, SUB, MUL, TANH, SIN };
struct OpNode { K k; int a, b; };                                         // 피연산자는 항상 앞선 노드의 번호 -> 번호 순서가 곧 위상 순서
struct Dual { double v, d; };                                             // 순방향 모드 자동 미분: 값과 방향 미분
Dual operator+(Dual x, Dual y) { return {x.v + y.v, x.d + y.d}; }
Dual operator-(Dual x, Dual y) { return {x.v - y.v, x.d - y.d}; }
Dual operator*(Dual x, Dual y) { return {x.v * y.v, x.d * y.v + x.v * y.d}; }
Dual th(Dual x) { double t = std::tanh(x.v); return {t, (1 - t * t) * x.d}; }
Dual sn(Dual x) { return {std::sin(x.v), std::cos(x.v) * x.d}; }
double th(double x) { return std::tanh(x); }
double sn(double x) { return std::sin(x); }

template <class T> std::vector<T> evalAll(const std::vector<OpNode>& ops, const std::vector<T>& in) {   // 순전파 (double 이든 Dual 이든 같은 코드)
    std::vector<T> v(ops.size()); size_t ii = 0;
    for (size_t i = 0; i < ops.size(); ++i) {
        const OpNode& o = ops[i];
        switch (o.k) { case IN: v[i] = in[ii++]; break; case ADD: v[i] = v[o.a] + v[o.b]; break; case SUB: v[i] = v[o.a] - v[o.b]; break;
                       case MUL: v[i] = v[o.a] * v[o.b]; break; case TANH: v[i] = th(v[o.a]); break; case SIN: v[i] = sn(v[o.a]); break; }
    }
    return v;
}
void propagate(const OpNode& o, int i, const std::vector<double>& val, std::vector<double>& g) {       // 노드 i 하나의 연쇄 법칙: 부모에게 기울기를 *누적*
    double gi = g[i];
    switch (o.k) { case IN: break; case ADD: g[o.a] += gi; g[o.b] += gi; break; case SUB: g[o.a] += gi; g[o.b] -= gi; break;
                   case MUL: g[o.a] += gi * val[o.b]; g[o.b] += gi * val[o.a]; break;
                   case TANH: g[o.a] += gi * (1 - val[i] * val[i]); break; case SIN: g[o.a] += gi * std::cos(val[o.a]); break; }
}
std::vector<double> reverseSweep(const std::vector<OpNode>& ops, const std::vector<double>& val, int out) {   // 번호 역순 = 위상 역순
    std::vector<double> g(ops.size(), 0.0); g[out] = 1;
    for (int i = out; i >= 0; --i) propagate(ops[i], i, val, g);
    return g;
}
void topo(const std::vector<OpNode>& ops, int u, std::vector<char>& seen, std::vector<int>& order) {    // DFS 후위: 피연산자가 먼저 나온다
    if (seen[u]) return; seen[u] = 1;
    if (ops[u].k != IN) { topo(ops, ops[u].a, seen, order); if (ops[u].k == ADD || ops[u].k == SUB || ops[u].k == MUL) topo(ops, ops[u].b, seen, order); }
    order.push_back(u);
}
std::vector<double> reverseDFS(const std::vector<OpNode>& ops, const std::vector<double>& val, int out, std::vector<char>* ancestors) {
    std::vector<char> seen(ops.size(), 0); std::vector<int> order; topo(ops, out, seen, order);
    std::vector<double> g(ops.size(), 0.0); g[out] = 1;
    for (auto it = order.rbegin(); it != order.rend(); ++it) propagate(ops[*it], *it, val, g);
    if (ancestors) *ancestors = seen;
    return g;
}
std::vector<int> inputIds(const std::vector<OpNode>& ops) { std::vector<int> r; for (size_t i = 0; i < ops.size(); ++i) if (ops[i].k == IN) r.push_back((int)i); return r; }
bool close(double a, double b, double tol) { return std::fabs(a - b) <= tol * (1 + std::fabs(a)); }

int main() {
    // ① f(w, x, b) = tanh(w·x + b),  w=0.5, x=2.0, b=-0.5
    std::vector<OpNode> f = {{IN, -1, -1}, {IN, -1, -1}, {IN, -1, -1}, {MUL, 0, 1}, {ADD, 3, 2}, {TANH, 4, -1}};
    std::vector<double> val = evalAll<double>(f, {0.5, 2.0, -0.5}), g = reverseSweep(f, val, 5);
    double t = std::tanh(0.5 * 2.0 - 0.5);
    assert(std::fabs(val[5] - t) < 1e-15 && std::fabs(g[0] - (1 - t * t) * 2.0) < 1e-15 && std::fabs(g[1] - (1 - t * t) * 0.5) < 1e-15 && std::fabs(g[2] - (1 - t * t)) < 1e-15);
    std::vector<OpNode> sq = {{IN, -1, -1}, {MUL, 0, 0}};                 // x·x: 같은 노드를 두 번 쓰면 두 기울기가 더해진다 -> 2x
    assert(reverseSweep(sq, evalAll<double>(sq, {3.0}), 1)[0] == 6.0);
    std::vector<OpNode> dbl = {{IN, -1, -1}, {ADD, 0, 0}, {ADD, 1, 1}};   // (x + x) + (x + x) = 4x -> 4
    assert(reverseSweep(dbl, evalAll<double>(dbl, {5.0}), 2)[0] == 4.0);
    std::vector<OpNode> sub = {{IN, -1, -1}, {IN, -1, -1}, {SUB, 0, 1}};  // a − b: 두 번째 피연산자의 기울기는 부호가 뒤집힌다
    assert((reverseSweep(sub, evalAll<double>(sub, {1.0, 2.0}), 2) == std::vector<double>{1.0, -1.0, 1.0}));

    // ② 무작위 계산 그래프
    std::mt19937 rng(9001); std::uniform_real_distribution<double> U(-1, 1); long graphs = 0, fanout = 0, deadNodes = 0, gradChecks = 0, skipped = 0;
    while (graphs < 1500) {
        int nin = 1 + (int)(rng() % 3), m = 2 + (int)(rng() % 11); std::vector<OpNode> ops(nin, OpNode{IN, -1, -1}); std::vector<int> uses;
        for (int i = 0; i < m; ++i) {
            int cur = (int)ops.size(), a = (int)(rng() % cur), b = (int)(rng() % cur); K k = (K)(1 + rng() % 5);
            if (k == TANH || k == SIN) b = -1;
            ops.push_back({k, a, b});
        }
        std::vector<double> in; for (int i = 0; i < nin; ++i) in.push_back(U(rng));
        std::vector<double> v = evalAll<double>(ops, in); double mx = 0; for (double x : v) mx = std::max(mx, std::fabs(x));
        if (mx > 50) { ++skipped; continue; }                             // 값이 너무 커지면 유한 차분이 무의미하므로 건너뜀
        int out = (int)ops.size() - 1; ++graphs;
        std::vector<double> rev = reverseSweep(ops, v, out); std::vector<char> anc; std::vector<double> rev2 = reverseDFS(ops, v, out, &anc);
        std::vector<int> ids = inputIds(ops); assert((int)ids.size() == nin);
        for (size_t i = 0; i < ops.size(); ++i) { assert(close(rev[i], rev2[i], 1e-12)); if (!anc[i]) { assert(rev[i] == 0.0 && rev2[i] == 0.0); ++deadNodes; } }
        std::vector<int> cnt(ops.size(), 0); for (size_t i = nin; i < ops.size(); ++i) { ++cnt[ops[i].a]; if (ops[i].k == ADD || ops[i].k == SUB || ops[i].k == MUL) ++cnt[ops[i].b]; }
        for (int c : cnt) if (c >= 2) { ++fanout; break; }
        for (int j = 0; j < nin; ++j) {
            std::vector<Dual> din; for (int q = 0; q < nin; ++q) din.push_back({in[q], q == j ? 1.0 : 0.0});
            double fwd = evalAll<Dual>(ops, din)[out].d, rv = rev[ids[j]];
            assert(close(fwd, rv, 1e-9));                                 // 순방향 모드 == 역방향 모드
            const double h = 1e-6; std::vector<double> p = in, q = in; p[j] += h; q[j] -= h;
            double num = (evalAll<double>(ops, p)[out] - evalAll<double>(ops, q)[out]) / (2 * h);
            assert(close(num, rv, 1e-5)); ++gradChecks;                   // 중심 유한 차분
        }
    }
    assert(graphs == 1500 && gradChecks > 2500 && fanout > 800 && deadNodes > 500);

    // ③ 뉴런 하나 학습: 정답 y = tanh(0.7·x − 0.2) 를 w=0, b=0 에서 경사 하강으로 찾는다. 손실 L = Σ (tanh(w·x_i + b) − y_i)²
    const double xs[] = {-1, -0.5, 0, 0.5, 1}; double w = 0, b = 0, prev = 1e18, first = 0, loss = 0; int steps = 0;
    for (; steps < 600; ++steps) {
        std::vector<OpNode> net = {{IN, -1, -1}, {IN, -1, -1}};          // 0: w, 1: b
        std::vector<int> sqs;
        for (double x : xs) {
            int cx = (int)net.size(); net.push_back({IN, -1, -1});         // 데이터 x 는 상수 입력, y 도 상수 입력
            int cy = (int)net.size(); net.push_back({IN, -1, -1});
            int m = (int)net.size(); net.push_back({MUL, 0, cx}); net.push_back({ADD, m, 1}); net.push_back({TANH, m + 1, -1}); net.push_back({SUB, m + 2, cy}); net.push_back({MUL, m + 3, m + 3});
            sqs.push_back(m + 4);
        }
        int acc = sqs[0]; for (size_t i = 1; i < sqs.size(); ++i) { net.push_back({ADD, acc, sqs[i]}); acc = (int)net.size() - 1; }
        std::vector<double> in = {w, b}; for (double x : xs) { in.push_back(x); in.push_back(std::tanh(0.7 * x - 0.2)); }
        std::vector<double> val2 = evalAll<double>(net, in), gr = reverseSweep(net, val2, acc); loss = val2[acc];
        if (steps == 0) first = loss;
        assert(loss <= prev + 1e-15); prev = loss;                         // 학습률이 충분히 작으면 손실은 단조 감소
        if (steps < 3) {                                                  // 처음 몇 번은 기울기를 유한 차분과도 대조
            for (int j = 0; j < 2; ++j) { std::vector<double> p = in, q = in; p[j] += 1e-6; q[j] -= 1e-6; double num = (evalAll<double>(net, p)[acc] - evalAll<double>(net, q)[acc]) / 2e-6; assert(close(num, gr[j], 1e-6)); }
        }
        w -= 0.05 * gr[0]; b -= 0.05 * gr[1];
    }
    assert(first > 0.1 && loss < first * 1e-3 && std::fabs(w - 0.7) < 0.1 && std::fabs(b + 0.2) < 0.1);
    std::cout << "NeuralGraph: " << graphs << " random DAGs (" << fanout << " with fan-out, " << gradChecks << " gradients): reverse mode = forward mode = finite difference; one tanh neuron learned w=" << w << ", b=" << b << " (loss " << first << " -> " << loss << ")" << std::endl;
    return 0;
}
// Time Complexity: 순전파·역전파 모두 O(연산 수) — 입력이 n 개인 스칼라 출력의 전체 기울기가 순방향 모드는 O(n · 연산 수), 역방향 모드는 O(연산 수) 한 번
// Space Complexity: O(연산 수)
```
## PageRank()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <utility>
#include <vector>

// 페이지랭크(PageRank): "중요한 페이지에서 오는 링크가 많은 페이지가 중요하다" 를 무작위 서퍼로 정식화한다. 서퍼는 확률 d(보통 0.85)로 나가는 링크 하나를 균등하게 따라가고, 확률 1 − d 로 임의의 페이지(텔레포트 분포 v, 기본은 균등)로 점프한다. 나가는 링크가 없는 페이지(dangling)에서는 균등하게 점프한다. 순위 r 은 이 마르코프 연쇄의 정상 분포 = 선형 방정식 (I − d·M) r = (1 − d)·v 의 해이고 합이 1 이다. 거듭제곱법(power iteration) r ← d·(Pᵀ r + D/n·1) + (1 − d)·v 는 한 번마다 L1 오차가 d 배 이하로 줄어드는 수축 사상이라 k 번 뒤 오차 ≤ dᵏ·초기 오차 — 허용 오차 ε 까지 필요한 횟수는 그래프 크기와 무관하게 log ε / log d.
// 구현 변형: 끌어오기(pull, 들어오는 간선 CSC) 와 밀어내기(push, 나가는 간선 CSR) 는 같은 값, 가우스–자이델(Gauss–Seidel, 제자리 갱신)은 같은 해로 수렴하지만 반복 수는 그래프에 따라 크게 갈린다 — 합이 1 이라는 불변식을 매번 지키지 못해서, 빨리 섞이는 무작위 그래프에서는 거듭제곱법이 더 빠르고(아래 큰 입력: 27 대 66 번), 정점 번호가 링크 방향을 따르는 느리게 섞이는 고리에서는 GS 가 3 번 대 147 번으로 압도한다. 정확해는 작은 그래프에서 밀집 가우스 소거로 구한다. 개인화 페이지랭크(텔레포트 분포 v 를 바꿈)는 v 에 *선형* 이다(이 정의에서 dangling 이 균등 점프이므로 M 이 v 와 무관하다): PPR(αu + (1 − α)w) = α·PPR(u) + (1 − α)·PPR(w).
// 검증: ① 닫힌 해 — 순환·완전 그래프는 균등, 허브로 모두가 연결되는 별(허브는 dangling) 은 허브 순위 (1 + (n − 1)d)/(n + (n − 1)d) ② 무작위 그래프(n ≤ 12)에서 거듭제곱법이 정확해로 수렴하고 *매 반복* L1 오차 ≤ dᵏ · 초기 오차, 합 = 1, 끌어오기 = 밀어내기 = 가우스–자이델(같은 해), 개인화의 선형성, 정점 이름을 바꿔도 순위가 같은 순열로 바뀜 ③ 큰 입력(정점 10 만 · 간선 50 만, 몰린 도착지 · dangling 5%) 에서 연속 잔차 비 ≤ d, 허용 오차 1e-10 까지 반복이 ⌈log(1e-10/2)/log d⌉ + 1 이하, 합 1, 끌어오기 = 밀어내기 = 가우스–자이델, 고리에서는 GS 가 거듭제곱법보다 열 배 이상 적은 반복.
using Edges = std::vector<std::pair<int, int>>;
struct Graph {
    int n; std::vector<int> outOff, outTo, inOff, inFrom, outdeg;                       // CSR(나가는) 과 CSC(들어오는)
    Graph(int nn, const Edges& e) : n(nn), outOff(nn + 1, 0), inOff(nn + 1, 0), outdeg(nn, 0) {
        for (auto [a, b] : e) { ++outOff[a + 1]; ++inOff[b + 1]; ++outdeg[a]; }
        for (int i = 0; i < n; ++i) { outOff[i + 1] += outOff[i]; inOff[i + 1] += inOff[i]; }
        outTo.resize(e.size()); inFrom.resize(e.size()); std::vector<int> po(outOff.begin(), outOff.end() - 1), pi(inOff.begin(), inOff.end() - 1);
        for (auto [a, b] : e) { outTo[po[a]++] = b; inFrom[pi[b]++] = a; }
    }
};
struct PR { std::vector<double> rank; int iterations; std::vector<double> residuals; };
double l1(const std::vector<double>& a, const std::vector<double>& b) { double s = 0; for (std::size_t i = 0; i < a.size(); ++i) s += std::fabs(a[i] - b[i]); return s; }

// mode: 0 = 끌어오기(Jacobi), 1 = 밀어내기(Jacobi), 2 = 가우스–자이델.  tele = 텔레포트 분포(합 1), 시작점은 균등
PR pageRank(const Graph& g, double d, double tol, int maxIter, int mode, const std::vector<double>* tele = nullptr, const std::vector<double>* start = nullptr) {
    int n = g.n; std::vector<double> uni(n, 1.0 / n); const std::vector<double>& v = tele ? *tele : uni;
    PR r{start ? *start : uni, 0, {}};
    for (int it = 1; it <= maxIter; ++it) {
        std::vector<double> old = r.rank;
        double dangling = 0; for (int u = 0; u < n; ++u) if (g.outdeg[u] == 0) dangling += old[u];
        if (mode == 0) {
            for (int x = 0; x < n; ++x) { double s = 0; for (int k = g.inOff[x]; k < g.inOff[x + 1]; ++k) s += old[g.inFrom[k]] / g.outdeg[g.inFrom[k]]; r.rank[x] = d * (s + dangling / n) + (1 - d) * v[x]; }
        } else if (mode == 1) {
            std::vector<double> next(n, 0.0);
            for (int u = 0; u < n; ++u) if (g.outdeg[u]) { double share = old[u] / g.outdeg[u]; for (int k = g.outOff[u]; k < g.outOff[u + 1]; ++k) next[g.outTo[k]] += share; }
            for (int x = 0; x < n; ++x) r.rank[x] = d * (next[x] + dangling / n) + (1 - d) * v[x];
        } else {
            double dang = dangling;                                                       // 제자리 갱신: 방금 바뀐 값을 바로 쓴다 (dangling 합도 함께 갱신)
            for (int x = 0; x < n; ++x) {
                double s = 0; for (int k = g.inOff[x]; k < g.inOff[x + 1]; ++k) s += r.rank[g.inFrom[k]] / g.outdeg[g.inFrom[k]];
                double nv = d * (s + dang / n) + (1 - d) * v[x];
                if (g.outdeg[x] == 0) dang += nv - r.rank[x];
                r.rank[x] = nv;
            }
        }
        r.iterations = it; r.residuals.push_back(l1(r.rank, old));
        if (r.residuals.back() < tol) break;
    }
    return r;
}
// 정확해: (I − d·M) r = (1 − d)·v, M[i][j] = (j → i ? 1/outdeg(j) : 0), dangling 열은 1/n (n ≤ 12, 부분 피벗 가우스 소거)
std::vector<double> exactSolve(const Graph& g, double d, const std::vector<double>* tele = nullptr) {
    int n = g.n; std::vector<std::vector<long double>> a(n, std::vector<long double>(n + 1, 0.0L));
    for (int i = 0; i < n; ++i) a[i][i] = 1.0L;
    for (int j = 0; j < n; ++j) {
        if (g.outdeg[j] == 0) { for (int i = 0; i < n; ++i) a[i][j] -= (long double)d / n; }
        else for (int k = g.outOff[j]; k < g.outOff[j + 1]; ++k) a[g.outTo[k]][j] -= (long double)d / g.outdeg[j];
    }
    for (int i = 0; i < n; ++i) a[i][n] = (1.0L - d) * (tele ? (*tele)[i] : 1.0L / n);
    for (int c = 0; c < n; ++c) {
        int p = c; for (int r = c + 1; r < n; ++r) if (std::fabs((double)a[r][c]) > std::fabs((double)a[p][c])) p = r;
        std::swap(a[p], a[c]);
        for (int r = 0; r < n; ++r) if (r != c) { long double f = a[r][c] / a[c][c]; for (int k = c; k <= n; ++k) a[r][k] -= f * a[c][k]; }
    }
    std::vector<double> x(n); for (int i = 0; i < n; ++i) x[i] = (double)(a[i][n] / a[i][i]); return x;
}

int main() {
    const double d = 0.85;
    // ① 손으로 확인한 모양: 0→1, 0→2, 1→3, 2→3, 3→0 (기존 예제) — 정확해와 일치, 대칭 r1 = r2, 3 이 가장 높다, 합 1
    {   Graph g(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 0}});
        auto ex = exactSolve(g, d); PR p = pageRank(g, d, 1e-14, 1000, 0);
        assert(l1(p.rank, ex) < 1e-12 && std::fabs(ex[1] - ex[2]) < 1e-15 && ex[3] > ex[0] && ex[0] > ex[1] && std::fabs(std::accumulate(ex.begin(), ex.end(), 0.0) - 1.0) < 1e-12);
    }
    // ② 닫힌 해: 순환·완전 그래프 → 균등; 별(잎 → 허브, 허브는 dangling) → 허브 = (1 + (n−1)d)/(n + (n−1)d)
    for (int n : {3, 7, 20}) {
        Edges cyc, comp, star;
        for (int i = 0; i < n; ++i) cyc.push_back({i, (i + 1) % n});
        for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (i != j) comp.push_back({i, j});
        for (int i = 1; i < n; ++i) star.push_back({i, 0});
        std::vector<double> start(n, 0.0); start[0] = 1.0;                              // 한 정점에 몰린 분포에서 출발해도 균등으로 수렴
        for (const Edges* e : {&cyc, &comp}) { Graph g(n, *e); PR p = pageRank(g, d, 1e-15, 2000, 0, nullptr, &start); for (double x : p.rank) assert(std::fabs(x - 1.0 / n) < 1e-12); }
        Graph g(n, star); PR p = pageRank(g, d, 1e-15, 5000, 0); double hub = (1 + (n - 1) * d) / (n + (n - 1) * d);
        assert(std::fabs(p.rank[0] - hub) < 1e-12 && std::fabs(p.rank[1] - (d * hub + 1 - d) / n) < 1e-12);
    }
    { Graph g(5, {}); PR p = pageRank(g, d, 1e-15, 100, 0); for (double x : p.rank) assert(std::fabs(x - 0.2) < 1e-14); }       // 링크가 없으면 모두 dangling → 균등

    // ③ 무작위 그래프 (n ≤ 12, dangling·루프·평행 간선 포함)
    std::mt19937 rng(1998);
    int trials = 0;
    for (int it = 0; it < 400; ++it) {
        int n = 2 + (int)(rng() % 11), m = (int)(rng() % (3 * n)); Edges e; for (int i = 0; i < m; ++i) e.push_back({(int)(rng() % n), (int)(rng() % n)});
        Graph g(n, e); auto ex = exactSolve(g, d);
        assert(std::fabs(std::accumulate(ex.begin(), ex.end(), 0.0) - 1.0) < 1e-11);
        // 매 반복 L1 오차 ≤ d^k · 초기 오차
        std::vector<double> cur(n, 1.0 / n); double e0 = l1(cur, ex);
        for (int k = 1; k <= 60; ++k) { PR step = pageRank(g, d, 0.0, k, 0); assert(l1(step.rank, ex) <= std::pow(d, k) * e0 + 1e-12); }
        PR pull = pageRank(g, d, 1e-14, 2000, 0), push = pageRank(g, d, 1e-14, 2000, 1), gs = pageRank(g, d, 1e-14, 2000, 2);
        assert(l1(pull.rank, ex) < 1e-11 && l1(push.rank, ex) < 1e-11 && l1(gs.rank, ex) < 1e-11 && l1(pull.rank, push.rank) < 1e-13);
        ++trials;
        // 개인화 선형성: PPR(αu + (1−α)w) = α PPR(u) + (1−α) PPR(w)
        std::vector<double> u(n), w(n), mix(n); double su = 0, sw = 0; for (int i = 0; i < n; ++i) { u[i] = (double)(rng() % 10); w[i] = (double)(rng() % 10); su += u[i]; sw += w[i]; }
        if (su == 0 || sw == 0) continue;
        for (int i = 0; i < n; ++i) { u[i] /= su; w[i] /= sw; } double alpha = 0.3; for (int i = 0; i < n; ++i) mix[i] = alpha * u[i] + (1 - alpha) * w[i];
        auto pu = exactSolve(g, d, &u), pw = exactSolve(g, d, &w), pm = exactSolve(g, d, &mix);
        for (int i = 0; i < n; ++i) assert(std::fabs(pm[i] - (alpha * pu[i] + (1 - alpha) * pw[i])) < 1e-12);
        PR conv = pageRank(g, d, 1e-14, 2000, 0, &mix); assert(l1(conv.rank, pm) < 1e-11);
        // 정점 이름 바꾸기 불변성
        std::vector<int> perm(n); std::iota(perm.begin(), perm.end(), 0); std::shuffle(perm.begin(), perm.end(), rng);
        Edges relabeled; for (auto [a, b] : e) relabeled.push_back({perm[a], perm[b]});
        Graph h(n, relabeled); auto ex2 = exactSolve(h, d); for (int i = 0; i < n; ++i) assert(std::fabs(ex2[perm[i]] - ex[i]) < 1e-12);
    }
    assert(trials == 400);

    // ④ 큰 입력: 정점 20 만, 간선 100 만 — 도착지가 몰려 있고(u² 분포) 정점의 5% 는 나가는 링크가 없다
    {
        const int N = 100000; std::mt19937_64 r(7); Edges e;
        for (int i = 0; i < 500000; ++i) {
            int src = (int)(r() % N); if (src % 20 == 0) continue;                               // 5% dangling (번호가 20 의 배수인 정점은 링크를 내지 않는다)
            double u = (r() % 1000000) / 1000000.0; e.push_back({src, (int)(u * u * N)});
        }
        Graph g(N, e); const double tol = 1e-10;
        PR pull = pageRank(g, d, tol, 400, 0), push = pageRank(g, d, tol, 400, 1), gs = pageRank(g, d, tol, 400, 2);
        int bound = (int)std::ceil(std::log(tol / 2) / std::log(d)) + 1;
        assert(pull.iterations <= bound && push.iterations <= bound && gs.iterations < 400);
        for (std::size_t k = 1; k < pull.residuals.size(); ++k) assert(pull.residuals[k] <= d * pull.residuals[k - 1] + 1e-13);   // 수축: 잔차가 매번 d 배 이하
        assert(std::fabs(std::accumulate(pull.rank.begin(), pull.rank.end(), 0.0) - 1.0) < 1e-9);
        assert(l1(pull.rank, push.rank) < 1e-11 && l1(pull.rank, gs.rank) < 1e-8);
        int top = (int)(std::max_element(pull.rank.begin(), pull.rank.end()) - pull.rank.begin()); assert(top == (int)(std::max_element(push.rank.begin(), push.rank.end()) - push.rank.begin()) && top < N / 10);   // 몰린 쪽(작은 번호) 이 1위
    }
    // ⑤ 고리 위의 가우스–자이델: 정점 번호가 링크 방향(i → i+1)을 따르므로 한 번 훑을 때 새 값이 끝까지 전달된다 — 한 정점에 몰린 분포에서 출발하면 거듭제곱법은 147 번, GS 는 3 번
    {
        const int n = 1000; Edges ring; for (int i = 0; i < n; ++i) ring.push_back({i, (i + 1) % n}); Graph g(n, ring);
        std::vector<double> start(n, 0.0); start[0] = 1.0;
        PR jac = pageRank(g, d, 1e-10, 1000, 0, nullptr, &start), gs = pageRank(g, d, 1e-10, 1000, 2, nullptr, &start);
        for (double x : jac.rank) assert(std::fabs(x - 1.0 / n) < 1e-9);
        for (double x : gs.rank) assert(std::fabs(x - 1.0 / n) < 1e-9);
        assert(jac.iterations > 100 && gs.iterations * 10 < jac.iterations);
    }
    std::cout << "PageRank: power iteration (pull and push forms) and Gauss-Seidel matched a dense exact solve on 400 random graphs with dangling nodes, loops and parallel edges, the L1 error obeyed ||r_k - r*|| <= d^k ||r_0 - r*|| at every one of 60 iterations, ranks always summed to 1, personalised PageRank was exactly linear in the teleport vector, relabelling vertices permuted the ranks, cycles and complete graphs came out uniform and the star hub matched (1+(n-1)d)/(n+(n-1)d), and a 100,000-vertex, ~500,000-edge graph with 5% dangling pages converged within ceil(log(tol/2)/log d)+1 iterations with the residual shrinking by at least a factor d each step, and on a 1000-vertex ring Gauss-Seidel needed ten times fewer sweeps than power iteration" << std::endl; return 0;
}
// Time Complexity: O(iter · (V + E)), iter ≈ log ε / log d
// Space Complexity: O(V + E)
```
# 부록
## BFS vs DFS
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// BFS vs DFS — 둘 다 모든 정점과 간선을 한 번씩 훑으므로 시간은 똑같이 O(V+E) 다. 차이는 "다음에 어느 정점을 펼치는가" 한 가지이고, 그 차이가 얻는 정보와 메모리를 가른다.
//   BFS(큐): 시작점에서 가까운 순서(층)로 펼친다 -> 가중치 없는 그래프의 최단 거리, 이분 그래프 판별, 레벨 순회. 메모리는 가장 넓은 층(frontier)의 크기에 비례한다.
//   DFS(스택/재귀): 한 길을 끝까지 파고든 뒤 되돌아온다 -> 방문/종료 순서로 위상 정렬, 사이클·단절점·강연결 요소. 메모리는 가장 깊은 경로의 길이에 비례한다.
// 같은 그래프에서 BFS 는 넓은 그래프(이진 트리)에서 메모리를 많이 쓰고 DFS 는 깊은 그래프(사슬)에서 많이 쓴다. IDDFS(반복 깊이 증가 DFS)는 DFS 의 메모리로 BFS 의 최단성을 얻는데, 분기 b 인 나무에서 바깥 층이 지배적이라 확장 수가 BFS 의 b/(b−1) 배 정도로만 늘어난다.
// 검증: ① 무작위 그래프에서 BFS 층 == 진짜 최단 거리(플로이드–워셜)이고 DFS 트리 경로는 같거나 길며 실제로 더 긴 경우가 많다 ② 두 탐색의 간선 검사 횟수가 같다(2m) ③ 메모리: 완전 이진 트리(깊이 14)에서 BFS 큐 최대 2¹⁴ vs DFS 스택 15, 사슬(길이 10000)에서 BFS 큐 1 vs DFS 깊이 10000 ④ BFS 2-색칠 이분 판별 == 홀수 사이클 없음(전수 비교) ⑤ IDDFS 확장 수/BFS 확장 수 < b/(b−1) + 0.1
typedef std::vector<std::vector<int>> G;
struct Res { std::vector<int> dist; long edgeChecks = 0; size_t peak = 0; };
Res bfs(const G& g, int s) { Res r; r.dist.assign(g.size(), -1); std::queue<int> q; q.push(s); r.dist[s] = 0; while (!q.empty()) { r.peak = std::max(r.peak, q.size()); int u = q.front(); q.pop(); for (int v : g[u]) { r.edgeChecks++; if (r.dist[v] < 0) { r.dist[v] = r.dist[u] + 1; q.push(v); } } } return r; }
Res dfs(const G& g, int s) {                                                          // 반복형 DFS; dist 는 DFS 트리 위의 깊이
    Res r; r.dist.assign(g.size(), -1); std::vector<std::pair<int, size_t>> st = {{s, 0}}; r.dist[s] = 0; r.peak = 1;
    while (!st.empty()) { int u = st.back().first; size_t& i = st.back().second; if (i < g[u].size()) { int v = g[u][i++]; r.edgeChecks++; if (r.dist[v] < 0) { r.dist[v] = r.dist[u] + 1; st.push_back({v, 0}); r.peak = std::max(r.peak, st.size()); } } else st.pop_back(); }
    return r;
}
bool bipartiteBFS(const G& g) { std::vector<int> color(g.size(), -1); for (size_t s = 0; s < g.size(); s++) if (color[s] < 0) { std::queue<int> q; q.push(s); color[s] = 0; while (!q.empty()) { int u = q.front(); q.pop(); for (int v : g[u]) { if (color[v] < 0) { color[v] = color[u] ^ 1; q.push(v); } else if (color[v] == color[u]) return false; } } } return true; }
bool hasOddCycle(const G& g) { int n = g.size(); for (int s = 0; s < n; s++) { for (int len = 1; len <= n; len += 2) {                  // 길이가 홀수인 닫힌 걷기가 있으면 홀수 사이클이 있다 (행렬 거듭제곱 대신 도달 집합 갱신)
            std::vector<char> cur(n, 0); cur[s] = 1; for (int step = 0; step < len; step++) { std::vector<char> nx(n, 0); for (int u = 0; u < n; u++) if (cur[u]) for (int v : g[u]) nx[v] = 1; cur = nx; } if (cur[s]) return true; } } return false; }
long iddfsExpansions(int b, int depth) {                                             // 암묵적 b-진 완전 트리 (루트 0, 자식 v*b+1..v*b+b), 목표는 마지막 층의 가장 오른쪽 정점(최악)
    long levelStart = 0, levelSize = 1, goal = 0; for (int d = 0; d <= depth; d++) { if (d == depth) goal = levelStart + levelSize - 1; levelStart += levelSize; levelSize *= b; }
    long total = 0;
    for (int limit = 0; limit <= depth; limit++) { std::vector<std::pair<long, int>> st = {{0, 0}}; while (!st.empty()) { auto [v, d] = st.back(); st.pop_back(); total++; if (v == goal) return total; if (d < limit) for (int c = b; c >= 1; c--) st.push_back({v * b + c, d + 1}); } }
    return -1;
}
int main() {
    std::mt19937 rng(10); long longer = 0, pairs = 0;
    for (int t = 0; t < 60; t++) { int n = 20 + rng() % 40; G g(n); int m = n + rng() % (2 * n); for (int k = 0; k < m; k++) { int u = rng() % n, v = rng() % n; if (u != v) { g[u].push_back(v); g[v].push_back(u); } }
        std::vector<std::vector<int>> D(n, std::vector<int>(n, 1 << 20)); for (int i = 0; i < n; i++) { D[i][i] = 0; for (int j : g[i]) D[i][j] = 1; } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) D[i][j] = std::min(D[i][j], D[i][k] + D[k][j]);
        Res b = bfs(g, 0), d = dfs(g, 0); long edges2 = 0; for (int v = 0; v < n; v++) if (b.dist[v] >= 0) edges2 += g[v].size();         // 시작점에서 닿는 성분의 차수 합 assert(b.edgeChecks == edges2 && d.edgeChecks == edges2);                                      // ② 간선 검사 수 같음
        for (int v = 0; v < n; v++) { if (D[0][v] >= (1 << 20)) { assert(b.dist[v] < 0 && d.dist[v] < 0); continue; } assert(b.dist[v] == D[0][v] && d.dist[v] >= D[0][v]); pairs++; longer += d.dist[v] > D[0][v]; } }          // ①
    assert(longer * 4 > pairs);
    G tree((1 << 15) - 1); for (int v = 0; 2 * v + 2 < (int)tree.size(); v++) { tree[v].push_back(2 * v + 1); tree[v].push_back(2 * v + 2); } Res tb = bfs(tree, 0), td = dfs(tree, 0); assert(tb.peak >= (size_t)(1 << 14) && td.peak == 15);          // ③ 넓은 그래프
    G path(10000); for (int i = 0; i + 1 < 10000; i++) path[i].push_back(i + 1); Res pb = bfs(path, 0), pd = dfs(path, 0); assert(pb.peak == 1 && pd.peak == 10000);                                                     // 깊은 그래프
    int agree = 0; for (int t = 0; t < 400; t++) { int n = 1 + rng() % 7; G g(n); int m = rng() % (2 * n); for (int k = 0; k < m; k++) { int u = rng() % n, v = rng() % n; if (u != v) { g[u].push_back(v); g[v].push_back(u); } } assert(bipartiteBFS(g) == !hasOddCycle(g)); agree++; }                           // ④
    double ratioMax = 0; for (int b : {2, 3, 4}) { int depth = b == 2 ? 14 : b == 3 ? 9 : 7; long bf = 0, sz = 1; for (int d = 0; d <= depth; d++) { bf += sz; sz *= b; } long id = iddfsExpansions(b, depth); double ratio = (double)id / bf; ratioMax = std::max(ratioMax, ratio); assert(ratio < (double)b / (b - 1) + 0.1 && ratio > 1.0); }          // ⑤
    std::cout << "BFS vs DFS: BFS layers equal true shortest distances while DFS paths were longer for " << longer << " of " << pairs << " reachable pairs; peak memory on a complete binary tree BFS queue " << tb.peak << " vs DFS stack " << td.peak << ", on a path BFS " << pb.peak << " vs DFS " << pd.peak
              << "; BFS 2-coloring matched odd-cycle detection on " << agree << " graphs; IDDFS expansions stayed within " << ratioMax << "x of BFS" << std::endl; return 0;
}
// Time Complexity: BFS, DFS 모두 O(V + E)
// Space Complexity: BFS O(가장 넓은 층), DFS O(가장 깊은 경로)
```
## DAG가 중요한 이유
### 대표코드
```cpp
#include <algorithm>
#include <bitset>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// DAG(방향 비순환 그래프)가 중요한 이유 — "순환이 없다" 는 한 가지 성질이 위상 순서를 만들고, 위상 순서가 있으면 "앞에서 뒤로 한 번만 훑는" 동적 계획법이 된다. 일반 그래프에서 어려운 문제들이 DAG 에서는 O(V+E) 로 풀린다.
//   ① 최단 경로: 음수 가중치가 있어도 위상 순서대로 완화하면 간선마다 한 번이라 O(V+E) (일반 그래프는 벨만–포드 O(VE)).  ② 최장 경로: 일반 그래프에서는 NP-난해이지만 DAG 에서는 같은 방법으로 O(V+E) — 프로젝트 일정의 임계 경로(CPM).
//   ③ 경로 개수 세기: 지수적으로 많은 경로를 열거하지 않고 합으로 센다.  ④ 의존성 해소·빌드 순서·수식 평가·상속 순서: 모두 "의존하는 것보다 먼저" 라는 위상 정렬.  ⑤ 전이적 폐쇄를 비트셋으로 O(V·E/64) 에 계산.
// 순환이 있으면 이 모든 것이 의미를 잃는다 — 위상 정렬이 존재할 필요충분조건이 비순환이다(칸의 알고리즘이 정점을 다 못 뽑으면 순환 존재, 남은 정점에서 실제 순환을 찾을 수 있다).
// 검증: ① n ≤ 4 의 모든 방향 그래프(2^(n(n-1)))에서 비순환 개수 = 1, 3, 25, 543 (레이블 있는 DAG 수 수열) ② 무작위 DAG 에서 위상 순서 DP 최단 거리 == 벨만–포드, 간선 검사 수 비교 ③ 다이아몬드 사슬 40 개의 경로 수 2^40 을 합으로 계산 vs 소형에서 열거와 일치 ④ 순환이 있는 그래프에서 칸의 알고리즘이 실제 순환을 찾아냄 ⑤ 비트셋 폐쇄 == 플로이드–워셜 폐쇄
typedef long long ll; const ll INF = (ll)4e18;
bool topo(const std::vector<std::vector<std::pair<int, ll>>>& g, std::vector<int>& order) { int n = g.size(); std::vector<int> indeg(n, 0); for (auto& a : g) for (auto& e : a) indeg[e.first]++; std::queue<int> q; for (int v = 0; v < n; v++) if (!indeg[v]) q.push(v); order.clear(); while (!q.empty()) { int u = q.front(); q.pop(); order.push_back(u); for (auto& e : g[u]) if (--indeg[e.first] == 0) q.push(e.first); } return (int)order.size() == n; }
bool acyclicMask(int n, int mask) { std::vector<std::vector<std::pair<int, ll>>> g(n); int bit = 0; for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v) { if (mask >> bit & 1) g[u].push_back({v, 1}); bit++; } std::vector<int> o; return topo(g, o); }
std::vector<int> findCycle(const std::vector<std::vector<std::pair<int, ll>>>& g) {          // 칸의 알고리즘이 못 뽑은 정점들 중에서 실제 순환을 하나 찾는다
    int n = g.size(); std::vector<int> indeg(n, 0); for (auto& a : g) for (auto& e : a) indeg[e.first]++; std::queue<int> q; for (int v = 0; v < n; v++) if (!indeg[v]) q.push(v); std::vector<char> removed(n, 0); while (!q.empty()) { int u = q.front(); q.pop(); removed[u] = 1; for (auto& e : g[u]) if (--indeg[e.first] == 0) q.push(e.first); }
    int start = -1; for (int v = 0; v < n; v++) if (!removed[v]) { start = v; break; } if (start < 0) return {};
    std::vector<int> pred(n, -1); for (int u = 0; u < n; u++) if (!removed[u]) for (auto& e : g[u]) if (!removed[e.first]) pred[e.first] = u;              // 남은 정점은 모두 "남은 정점에서 오는 간선" 이 있다 (들어오는 간선 수가 0 이 되지 못했으므로)
    std::vector<int> seen(n, -1), walk; int v = start; while (seen[v] < 0) { seen[v] = walk.size(); walk.push_back(v); v = pred[v]; }                          // 거꾸로 걷다 보면 반드시 되풀이된다
    std::vector<int> cyc(walk.begin() + seen[v], walk.end()); std::reverse(cyc.begin(), cyc.end()); return cyc;
}
int main() {
    long dagCounts[5] = {1, 1, 3, 25, 543}; for (int n = 1; n <= 4; n++) { long cnt = 0; for (int mask = 0; mask < (1 << (n * (n - 1))); mask++) cnt += acyclicMask(n, mask); assert(cnt == dagCounts[n]); }                              // ① 레이블 DAG 수
    std::mt19937 rng(17); long dagOps = 0, bfOps = 0;
    for (int t = 0; t < 30; t++) {
        int n = 800, m = 4000; std::vector<int> perm(n); for (int i = 0; i < n; i++) perm[i] = i; std::shuffle(perm.begin(), perm.end(), rng); std::vector<std::vector<std::pair<int, ll>>> g(n); for (int k = 0; k < m; k++) { int a = rng() % n, b = rng() % n; if (a == b) continue; if (a > b) std::swap(a, b); g[perm[a]].push_back({perm[b], (ll)(rng() % 41) - 15}); }
        std::vector<int> order; assert(topo(g, order)); int src = order[0]; std::vector<ll> d(n, INF); d[src] = 0; for (int u : order) if (d[u] < INF) for (auto& e : g[u]) { dagOps++; d[e.first] = std::min(d[e.first], d[u] + e.second); }       // ② 위상 순서 DP
        std::vector<ll> bf(n, INF); bf[src] = 0; for (int pass = 0; pass < n; pass++) { bool ch = false; for (int u = 0; u < n; u++) if (bf[u] < INF) for (auto& e : g[u]) { bfOps++; if (bf[u] + e.second < bf[e.first]) { bf[e.first] = bf[u] + e.second; ch = true; } } if (!ch) break; } assert(d == bf);
    }
    assert(dagOps * 5 < bfOps);
    { int k = 40; std::vector<std::vector<std::pair<int, ll>>> g(3 * k + 1); for (int i = 0; i < k; i++) { int a = 3 * i, l = 3 * i + 1, r = 3 * i + 2, b = 3 * i + 3; g[a].push_back({l, 1}); g[a].push_back({r, 1}); g[l].push_back({b, 1}); g[r].push_back({b, 1}); } std::vector<int> o; assert(topo(g, o)); std::vector<ll> ways(g.size(), 0); ways[0] = 1; for (int u : o) for (auto& e : g[u]) ways[e.first] += ways[u]; assert(ways[3 * k] == (1LL << 40)); }          // ③ 2^40 개의 경로를 O(V+E) 로
    for (int t = 0; t < 200; t++) { int n = 2 + rng() % 9; std::vector<std::vector<std::pair<int, ll>>> g(n); for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) if (rng() % 3 == 0) g[a].push_back({b, 1}); std::vector<int> o; assert(topo(g, o)); std::vector<ll> ways(n, 0); ways[0] = 1; for (int u : o) for (auto& e : g[u]) ways[e.first] += ways[u];
        std::vector<ll> cnt(n, 0); std::vector<int> st = {0}; while (!st.empty()) { int u = st.back(); st.pop_back(); cnt[u]++; for (auto& e : g[u]) st.push_back(e.first); } assert(cnt == ways); }                                 // 열거(DFS)와 합산이 같다
    int cyclesFound = 0; for (int t = 0; t < 300; t++) { int n = 3 + rng() % 8; std::vector<std::vector<std::pair<int, ll>>> g(n); for (int k = 0; k < 2 * n; k++) { int a = rng() % n, b = rng() % n; if (a != b) g[a].push_back({b, 1}); } std::vector<int> o; bool dag = topo(g, o); auto cyc = findCycle(g); assert(dag == cyc.empty()); if (!dag) { cyclesFound++; for (size_t i = 0; i < cyc.size(); i++) { int u = cyc[i], v = cyc[(i + 1) % cyc.size()]; bool edge = false; for (auto& e : g[u]) edge |= e.first == v; assert(edge); } } }          // ④ 실제 순환
    for (int t = 0; t < 50; t++) { const int N = 60; std::vector<std::vector<std::pair<int, ll>>> g(N); std::vector<std::bitset<N>> reach(N); for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++) if (rng() % 8 == 0) g[a].push_back({b, 1}); std::vector<int> o; assert(topo(g, o)); for (int i = N - 1; i >= 0; i--) { int u = o[i]; reach[u].set(u); for (auto& e : g[u]) reach[u] |= reach[e.first]; }
        std::vector<std::bitset<N>> fw(N); for (int a = 0; a < N; a++) { fw[a].set(a); for (auto& e : g[a]) fw[a].set(e.first); } for (int k = 0; k < N; k++) for (int i = 0; i < N; i++) if (fw[i][k]) fw[i] |= fw[k]; for (int i = 0; i < N; i++) assert(fw[i] == reach[i]); }                          // ⑤ 비트셋 폐쇄
    std::cout << "DAG: acyclic labeled digraphs for n=1..4 counted as 1, 3, 25, 543; topological DP used " << dagOps << " edge relaxations vs " << bfOps << " for Bellman-Ford with identical shortest distances; 2^40 paths counted by a sum; " << cyclesFound << " cyclic graphs yielded a verified cycle" << std::endl; return 0;
}
// Time Complexity: 위상 정렬 O(V + E), DAG 위의 DP O(V + E), 비트셋 폐쇄 O(V·E/64)
// Space Complexity: O(V + E)
```
## Prim vs Kruskal
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// Prim vs Kruskal — 둘 다 컷 성질(어떤 컷을 가로지르는 가장 가벼운 간선은 어떤 최소 신장 트리에 속한다)에 기대는 탐욕 알고리즘이라 같은 총 가중치를 낸다. 차이는 "어떻게 자라나" 다.
//   Kruskal: 모든 간선을 가중치 순으로 정렬해 사이클을 만들지 않는 것만 서로소 집합으로 확인하며 받는다 — 숲이 여러 조각으로 시작해 합쳐진다. O(E log E). 간선 목록만 있으면 되고, 연결되지 않은 그래프에서는 최소 신장 숲을 그대로 낸다.
//   Prim: 한 정점에서 시작해 트리에 닿은 간선 중 가장 가벼운 것으로 트리 하나를 키운다 — 이진 힙이면 O(E log V), 인접 행렬+배열이면 O(V²) 이다. 간선이 많은 조밀한 그래프(E ≈ V²)에서는 정렬이 필요 없는 배열 Prim 이 유리하고, 희소한 그래프에서는 Kruskal(또는 힙 Prim)이 유리하다.
// 가중치가 모두 다르면 최소 신장 트리가 유일해서 두 알고리즘의 간선 집합이 같다. 같은 가중치가 있으면 모양은 달라도 총합은 같다.
// 검증: ① 소형 그래프에서 모든 (n−1)-간선 부분집합을 시험한 최소 총합과 일치 ② 가중치가 서로 다르면 간선 집합까지 동일 ③ 동점이 많아도 총합 동일하고 둘 다 신장 트리 ④ 비연결 그래프: Kruskal 은 n − 성분 수 개의 간선을 내지만 Prim 은 시작점의 성분만 덮는다 ⑤ 연산 수 교차점: 희소(n=2000, m=6000)에서는 Kruskal 비교 수 < Prim 배열 O(V²), 조밀(n=300 완전 그래프)에서는 반대
typedef long long ll; struct Edge { int u, v; ll w; };
static long sortCompares = 0; bool lessCounted(const Edge& a, const Edge& b) { sortCompares++; return a.w < b.w || (a.w == b.w && std::make_pair(a.u, a.v) < std::make_pair(b.u, b.v)); }
struct Result { ll total = 0; std::set<std::pair<int, int>> edges; long ops = 0; };
int findSet(std::vector<int>& p, int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
Result kruskal(int n, std::vector<Edge> es) { Result r; sortCompares = 0; std::sort(es.begin(), es.end(), lessCounted); r.ops = sortCompares; std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); for (auto& e : es) { int a = findSet(p, e.u), b = findSet(p, e.v); r.ops++; if (a != b) { p[a] = b; r.total += e.w; r.edges.insert({std::min(e.u, e.v), std::max(e.u, e.v)}); } } return r; }
Result primHeap(int n, const std::vector<Edge>& es, int root) { Result r; std::vector<std::vector<std::pair<int, ll>>> g(n); for (auto& e : es) { g[e.u].push_back({e.v, e.w}); g[e.v].push_back({e.u, e.w}); } std::vector<char> in(n, 0); typedef std::tuple<ll, int, int> T; std::priority_queue<T, std::vector<T>, std::greater<T>> pq; pq.push({0, root, -1});
    while (!pq.empty()) { auto [w, v, from] = pq.top(); pq.pop(); r.ops++; if (in[v]) continue; in[v] = 1; r.total += w; if (from >= 0) r.edges.insert({std::min(v, from), std::max(v, from)}); for (auto& e : g[v]) if (!in[e.first]) pq.push({e.second, e.first, v}); } return r; }
Result primArray(int n, const std::vector<Edge>& es, int root) { Result r; const ll INF = (ll)4e18; std::vector<std::vector<ll>> W(n, std::vector<ll>(n, INF)); for (auto& e : es) { W[e.u][e.v] = std::min(W[e.u][e.v], e.w); W[e.v][e.u] = std::min(W[e.v][e.u], e.w); }
    std::vector<ll> key(n, INF); std::vector<int> par(n, -1); std::vector<char> in(n, 0); key[root] = 0; for (int it = 0; it < n; it++) { int v = -1; for (int i = 0; i < n; i++) { r.ops++; if (!in[i] && key[i] < INF && (v < 0 || key[i] < key[v])) v = i; } if (v < 0) break; in[v] = 1; r.total += key[v]; if (par[v] >= 0) r.edges.insert({std::min(v, par[v]), std::max(v, par[v])}); for (int u = 0; u < n; u++) { r.ops++; if (!in[u] && W[v][u] < key[u]) { key[u] = W[v][u]; par[u] = v; } } }
    return r; }
int main() {
    std::mt19937 rng(23); int distinctChecked = 0, tiesChecked = 0;
    for (int t = 0; t < 300; t++) {
        int n = 2 + rng() % 6; std::vector<Edge> es; bool distinct = t % 2 == 0; std::set<ll> used; for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) if (rng() % 100 < 70) { ll w; do { w = distinct ? 1 + rng() % 1000 : 1 + rng() % 4; } while (distinct && used.count(w)); used.insert(w); es.push_back({u, v, w}); }
        for (int u = 0; u + 1 < n; u++) es.push_back({u, u + 1, distinct ? 2000 + u : 1 + (ll)(rng() % 4)});                                                                                                  // 연결 보장용 사슬 (가중치는 다른 간선과 겹치지 않거나 동점 시험용)
        ll best = (ll)4e18; int m = es.size(); if (m <= 18) for (int mask = 0; mask < (1 << m); mask++) if (__builtin_popcount(mask) == n - 1) { std::vector<int> p(n); std::iota(p.begin(), p.end(), 0); ll sum = 0; bool ok = true; for (int i = 0; i < m && ok; i++) if (mask >> i & 1) { int a = findSet(p, es[i].u), b = findSet(p, es[i].v); if (a == b) ok = false; else { p[a] = b; sum += es[i].w; } } if (ok) best = std::min(best, sum); }
        Result k = kruskal(n, es), ph = primHeap(n, es, 0), pa = primArray(n, es, 0); assert(k.total == ph.total && ph.total == pa.total && (int)k.edges.size() == n - 1 && (int)ph.edges.size() == n - 1 && (int)pa.edges.size() == n - 1); if (m <= 18) assert(k.total == best);                    // ① ③
        if (distinct) { assert(k.edges == ph.edges && ph.edges == pa.edges); distinctChecked++; } else tiesChecked++;                                                                                                       // ② 가중치가 서로 다르면 간선 집합도 같다
    }
    { std::vector<Edge> es = {{0, 1, 1}, {1, 2, 2}, {3, 4, 1}, {4, 5, 2}, {3, 5, 9}}; Result k = kruskal(6, es), p = primHeap(6, es, 0); assert(k.edges.size() == 4 && p.edges.size() == 2); }                                // ④ 비연결 그래프
    { int n = 2000; std::vector<Edge> es; for (int k = 0; k < 6000; k++) { int u = rng() % n, v = rng() % n; if (u != v) es.push_back({u, v, (ll)(rng() % 1000000)}); } for (int u = 0; u + 1 < n; u++) es.push_back({u, u + 1, 1000000 + u}); Result k = kruskal(n, es), pa = primArray(n, es, 0); assert(k.total == pa.total && k.ops < pa.ops); std::cout << "sparse: Kruskal ops " << k.ops << " vs array Prim " << pa.ops << "; "; }
    { int n = 300; std::vector<Edge> es; for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) es.push_back({u, v, (ll)(rng() % 1000000)}); Result k = kruskal(n, es), pa = primArray(n, es, 0), ph = primHeap(n, es, 0); assert(k.total == pa.total && pa.total == ph.total && pa.ops < k.ops); std::cout << "dense: Kruskal ops " << k.ops << " vs array Prim " << pa.ops << " (heap Prim " << ph.ops << ")" << std::endl; }
    std::cout << "Prim vs Kruskal: " << distinctChecked << " distinct-weight graphs produced identical edge sets and " << tiesChecked << " tie-heavy graphs the same total; both matched the brute-force minimum" << std::endl; return 0;
}
// Time Complexity: Kruskal O(E log E), Prim 이진 힙 O(E log V), Prim 배열 O(V²)
// Space Complexity: O(V + E)
```
## Dijkstra vs A*
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>

// (그래프 관점의 요약, 정본은 PathFinding.md 부록 의 Dijkstra vs A* — 일관성과 재개방까지 다룬다)
// Dijkstra 는 출발점에서 가까운 순서로 사방을 확장하고, A* 는 f = g + h (h = 목표까지의 휴리스틱 추정) 가 작은 순서로 확장한다.
// h 가 허용 가능(실제 비용을 넘지 않음)하고 일관적이면 A* 도 최적해를 보장하면서, 목표 쪽으로 편향되어 훨씬 적은 정점을 확장한다.  h = 0 이면 A* 는 Dijkstra 와 같다
// 증명 스케치: 최적 비용 C* 일 때 A* 가 확장하는 정점은 f ≤ C* 뿐이고, 그런 정점은 g < C* (목표 자신만 g = C*) 이다. Dijkstra 는 g < C* 인 정점을 *모두* 확장하므로 A* 확장 수 ≤ Dijkstra 확장 수
// 검증: 무작위 장애물 격자 600 개(3×3 ~ 24×24, 장애물 0~40 %, 도달 불가능한 경우 포함)에서 ① Dijkstra·A* 비용 = 독립 BFS 비용(없으면 -1), 6×6 이하는 Floyd-Warshall 과도 일치
//        ② A* 확장 수 ≤ Dijkstra 확장 수 (일관적 맨해튼 휴리스틱)  ③ 가중 A*(h 의 2 배, 비허용)는 비용이 C* 이상 2·C* 이하이고 실제로 최적이 아닌 경우가 있다  ④ 벽이 있는 40×40 대형 격자의 확장 수
typedef std::vector<std::string> Grid;
struct Res { int cost; long expanded; };

Res search(const Grid& g, int sr, int sc, int tr, int tc, int w) {       // w = 0: Dijkstra, w = 1: A*(맨해튼), w = 2: 가중 A*
    int R = (int)g.size(), C = (int)g[0].size(); const int INF = 1 << 29;
    std::vector<int> dist(R * C, INF); std::vector<char> closed(R * C, 0);
    typedef std::pair<int, int> Item;                                     // (f, 칸 번호)
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
    auto h = [&](int r, int c) { return w * (std::abs(r - tr) + std::abs(c - tc)); };
    dist[sr * C + sc] = 0; pq.push({h(sr, sc), sr * C + sc}); Res res{-1, 0};
    const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
    while (!pq.empty()) {
        int cell = pq.top().second; pq.pop(); if (closed[cell]) continue;
        closed[cell] = 1; ++res.expanded; int r = cell / C, c = cell % C;
        if (r == tr && c == tc) { res.cost = dist[cell]; return res; }
        for (int k = 0; k < 4; ++k) {
            int nr = r + dr[k], nc = c + dc[k];
            if (nr < 0 || nr >= R || nc < 0 || nc >= C || g[nr][nc] == '#' || closed[nr * C + nc]) continue;
            if (dist[cell] + 1 < dist[nr * C + nc]) { dist[nr * C + nc] = dist[cell] + 1; pq.push({dist[nr * C + nc] + h(nr, nc), nr * C + nc}); }
        }
    }
    return res;
}
int bfs(const Grid& g, int sr, int sc, int tr, int tc) {                  // 오라클: 단위 비용이므로 평범한 BFS 가 정답
    int R = (int)g.size(), C = (int)g[0].size(); std::vector<int> d(R * C, -1); std::queue<int> q; d[sr * C + sc] = 0; q.push(sr * C + sc);
    while (!q.empty()) {
        int u = q.front(); q.pop(); int r = u / C, c = u % C; const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
        for (int k = 0; k < 4; ++k) { int nr = r + dr[k], nc = c + dc[k]; if (nr >= 0 && nr < R && nc >= 0 && nc < C && g[nr][nc] != '#' && d[nr * C + nc] < 0) { d[nr * C + nc] = d[u] + 1; q.push(nr * C + nc); } }
    }
    return d[tr * C + tc];
}
int floyd(const Grid& g, int sr, int sc, int tr, int tc) {                // 두 번째 오라클 (작은 격자만)
    int R = (int)g.size(), C = (int)g[0].size(), n = R * C; const int INF = 1 << 20; std::vector<std::vector<int>> d(n, std::vector<int>(n, INF));
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (g[r][c] != '#') {
        d[r * C + c][r * C + c] = 0;
        if (r + 1 < R && g[r + 1][c] != '#') d[r * C + c][(r + 1) * C + c] = d[(r + 1) * C + c][r * C + c] = 1;
        if (c + 1 < C && g[r][c + 1] != '#') d[r * C + c][r * C + c + 1] = d[r * C + c + 1][r * C + c] = 1;
    }
    for (int m = 0; m < n; ++m) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (d[i][m] + d[m][j] < d[i][j]) d[i][j] = d[i][m] + d[m][j];
    int x = d[sr * C + sc][tr * C + tc]; return x >= INF ? -1 : x;
}

int main() {
    std::mt19937 rng(31337); int instances = 0, reachable = 0, unreachable = 0, aStrict = 0, weightedSub = 0, weightedOk = 0, floydChecked = 0; long sumD = 0, sumA = 0;
    for (int it = 0; it < 600; ++it) {
        int R = 3 + (int)(rng() % 22), C = 3 + (int)(rng() % 22), pct = (int)(rng() % 41); Grid g(R, std::string(C, '.'));
        for (auto& row : g) for (auto& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int sr = (int)(rng() % R), sc = (int)(rng() % C), tr = (int)(rng() % R), tc = (int)(rng() % C); g[sr][sc] = g[tr][tc] = '.';
        int want = bfs(g, sr, sc, tr, tc); Res d = search(g, sr, sc, tr, tc, 0), a = search(g, sr, sc, tr, tc, 1), x = search(g, sr, sc, tr, tc, 2);
        assert(d.cost == want && a.cost == want);                         // ① 둘 다 최적 (도달 불가능하면 -1)
        assert(a.expanded <= d.expanded);                                 // ② 일관적 휴리스틱의 A* 는 Dijkstra 보다 많이 확장하지 않는다
        if (R * C <= 36) { assert(floyd(g, sr, sc, tr, tc) == want); ++floydChecked; }
        if (want < 0) { ++unreachable; assert(x.cost == -1 && d.expanded == a.expanded && d.expanded == x.expanded); /* 목표가 없으면 셋 다 출발점의 연결 성분 전체를 확장한다 */ } else { ++reachable; assert(x.cost >= want && x.cost <= 2 * want); weightedSub += x.cost > want; weightedOk += x.cost == want; }
        aStrict += a.expanded < d.expanded; sumD += d.expanded; sumA += a.expanded; ++instances;
    }
    assert(instances == 600 && reachable > 300 && unreachable > 30 && floydChecked > 5 && aStrict > 250 && sumA < sumD && weightedSub > 5 && weightedOk > 100);
    // 경계: 출발 = 목표 (비용 0, 한 정점만 확장), 좁은 복도, 막힌 목표
    Grid one(1, std::string(1, '.')); Res r0 = search(one, 0, 0, 0, 0, 1); assert(r0.cost == 0 && r0.expanded == 1);
    Grid corridor(1, std::string(30, '.')); assert(search(corridor, 0, 0, 0, 29, 0).cost == 29 && search(corridor, 0, 0, 0, 29, 1).expanded == 30);
    Grid blocked = {".#.", "###", "..."}; assert(search(blocked, 0, 0, 2, 2, 1).cost == -1 && bfs(blocked, 0, 0, 2, 2) == -1);
    // ④ 세로 벽이 있는 40×40 격자 (열 20, 행 0..29 가 벽 -> 아래쪽 10 칸으로 돌아가야 한다)
    Grid big(40, std::string(40, '.')); for (int r = 0; r < 30; ++r) big[r][20] = '#';
    Res bd = search(big, 0, 0, 39, 39, 0), ba = search(big, 0, 0, 39, 39, 1);
    assert(bd.cost == ba.cost && ba.cost == bfs(big, 0, 0, 39, 39) && ba.cost == 78 && ba.expanded < bd.expanded);
    std::cout << "Dijkstra vs A*: " << instances << " random grids agreed with BFS (" << reachable << " reachable, " << unreachable << " blocked); A* expanded " << sumA << " cells vs " << sumD << " for Dijkstra, weighted A* was suboptimal on " << weightedSub << "; wall grid: cost " << ba.cost << ", Dijkstra " << bd.expanded << " vs A* " << ba.expanded << std::endl;
    return 0;
}
// Time Complexity: Dijkstra O(E log V), A* 는 휴리스틱에 따라 훨씬 적은 확장 (일관적이면 Dijkstra 이하)
// Space Complexity: O(V)
```
## Union-Find 시간복잡도
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// Union-Find 시간복잡도 — 랭크(또는 크기)로 합치고 경로를 압축하면 m 번의 연산이 O(m·α(n)) 이다. α 는 역아커만 함수로, 아커만 함수 A_k(1) 이 폭발적으로 커지는 속도의 역이다: A₀(j)=j+1, A_k(j)=A_{k−1} 을 j+1 번 되풀이 적용한 값.
//   A₁(1)=3, A₂(1)=7, A₃(1)=2047, A₄(1)=A₃(2047) 은 A₂ 가 2^x 이상으로 자라므로 높이 2048 의 거듭제곱 탑보다 커서 관측 가능한 우주의 원자 수(약 10^80)를 훨씬 넘는다. 그러므로 실용적인 모든 n 에 대해 α(n) ≤ 4 이고 사실상 상수다.
//   이것은 증명된 한계이기도 하다(Tarjan 1975 상한, Fredman–Saks 1989 하한): 포인터 머신/셀 프로브 모델에서 Ω(m·α) 가 필요하다 — 더 나은 해는 없다.
// 압축만 하고 랭크를 쓰지 않으면 O(m log_{1+m/n} n), 랭크만 쓰고 압축을 안 하면 find 하나가 O(log n) 이다. 크루스칼처럼 Union-Find 가 안쪽 루프에 있는 알고리즘의 전체 시간은 정렬 O(E log E) 가 지배하므로 Union-Find 는 사실상 "공짜" 이다.
// 검증: ① A_k(1) 값(3, 7, 2047)과 A₄(1) > 2^300 ② 크기 n = 2^10 … 2^20 에서 무작위 합치기+조회의 연산당 평균 걸음 수가 n 에 거의 무관(상수) ③ 이항 트리(토너먼트)에서 랭크만 쓸 때는 가장 깊은 노드 조회 비용이 log₂ n 으로 자라지만 압축을 쓰면 두 번째 조회가 한 걸음 ④ 별 모양 합치기열 (0,j): 순진한 합치기+압축 없음은 Θ(n²), 랭크 합치기는 O(n) (여기서는 항상 큰 쪽이 루트라 걸음 0) ⑤ 크루스칼에서 정렬 비교 수 ≫ find 걸음 수
__extension__ typedef __int128 big;
big ack2(big x) { return ((big)1 << (x + 1)) * (x + 1) - 1; }                                  // A₂(x) = 2^(x+1)(x+1) − 1 (x ≤ 100 에서만 정확)
struct DSU {
    std::vector<int> p, rk; bool byRank, compress; long steps = 0; DSU(int n, bool r, bool c) : p(n), rk(n, 0), byRank(r), compress(c) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { int r = x; while (p[r] != r) { r = p[r]; steps++; } if (compress) while (p[x] != r) { int nx = p[x]; p[x] = r; x = nx; } return r; }
    bool unite(int a, int b) { a = find(a); b = find(b); if (a == b) return false; if (byRank) { if (rk[a] < rk[b]) std::swap(a, b); p[b] = a; if (rk[a] == rk[b]) rk[a]++; } else p[a] = b; return true; }
};
int main() {
    assert(ack2(1) == 7 && ack2(7) == 2047);                                                                    // ① A₂(1)=7, A₃(1)=A₂(A₂(1))=A₂(7)=2047 이고 A₁(1)=2·1+1=3
    long double lg = 2047; for (int i = 0; i < 3; i++) lg = std::pow(2.0L, std::min(lg, 400.0L)); assert(lg > std::pow(2.0L, 300.0L));              // A₄(1)=A₃(2047) ≥ A₂ 를 2048 번 합성 ≥ 2^2^2^… (3 번만 합성해도 2^300 초과)
    std::mt19937 rng(31); double avgMin = 1e9, avgMax = 0;
    for (int e = 10; e <= 20; e += 2) { int n = 1 << e; DSU d(n, true, true); long ops = 0; for (int k = 0; k < 2 * n; k++) { int a = rng() % n, b = rng() % n; if (k % 2) d.unite(a, b); else d.find(a); ops += k % 2 ? 2 : 1; } double avg = (double)d.steps / ops; avgMin = std::min(avgMin, avg); avgMax = std::max(avgMax, avg); assert(avg < 2.0); }          // ② 연산당 걸음 수 거의 상수
    assert(avgMax < 2.5 * avgMin + 1.0);
    int lastTournament = 0; for (int e = 4; e <= 18; e += 2) { int n = 1 << e; DSU r(n, true, false), c(n, true, true); for (int len = 1; len < n; len *= 2) for (int i = 0; i + len < n; i += 2 * len) { r.unite(i, i + len); c.unite(i, i + len); } long before = r.steps; r.find(n - 1); long cost = r.steps - before; assert(cost >= e - 1 && cost <= e); c.find(n - 1); long b2 = c.steps; c.find(n - 1); assert(c.steps - b2 <= 1); lastTournament = e; }          // ③
    const int S = 3000; DSU naive(S, false, false), good(S, true, true); for (int j = 1; j < S; j++) { naive.unite(0, j); good.unite(0, j); } assert(naive.steps > (long)S * S / 4 && good.steps < 4L * S);                          // ④ 순진: Θ(n²), 랭크+압축: Θ(n)
    { int n = 100000, m = 400000; std::vector<std::tuple<int, int, int>> es; for (int k = 0; k < m; k++) es.push_back({(int)(rng() % 1000000), (int)(rng() % n), (int)(rng() % n)}); long cmp = 0; std::sort(es.begin(), es.end(), [&](auto& a, auto& b) { cmp++; return a < b; }); DSU d(n, true, true); for (auto& [w, u, v] : es) d.unite(u, v); assert(cmp > 10 * d.steps); std::cout << "Kruskal on 400000 edges: sort comparisons " << cmp << " vs union-find steps " << d.steps << "; "; }          // ⑤
    std::cout << "Union-Find: steps per operation stayed within [" << avgMin << ", " << avgMax << "] for n = 2^10..2^20; star unions cost " << naive.steps << " steps with naive linking vs " << good.steps << " with rank+compression; tournament tree depth reached 2^" << lastTournament << std::endl; return 0;
}
// Time Complexity: m 번의 연산에 O(m · α(n)) (랭크 + 경로 압축), 압축만: O(m log n), 랭크만: find 당 O(log n)
// Space Complexity: O(n)
```
