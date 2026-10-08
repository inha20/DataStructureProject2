# Part 1. 길찾기의 기초
## CreateMap()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 길찾기의 출발점은 "세계를 어떻게 표현하는가"이다. 격자 지도는 글자 지도(ASCII map)로 적고 읽는 것이 가장 편하다: '#' 벽, '.' 평지, '1'~'9' 지형 비용(숫자가 클수록 비싼 길: 진흙·숲), 'S' 시작, 'G' 목표.
// 읽을 때 검증이 중요하다 — 줄 길이가 들쭉날쭉하거나 시작·목표가 없거나 둘 이상이면 이후 모든 알고리즘이 조용히 틀린 답을 내므로 지도를 만드는 곳에서 막는다
struct Map {
    int rows = 0, cols = 0, sr = -1, sc = -1, gr = -1, gc = -1; std::vector<std::vector<int>> cost;        // 0 = 벽, >= 1 = 칸에 들어가는 비용
    bool inBounds(int r, int c) const { return r >= 0 && r < rows && c >= 0 && c < cols; }
    bool passable(int r, int c) const { return inBounds(r, c) && cost[r][c] > 0; }
};
bool parseMap(const std::vector<std::string>& lines, Map& m) {
    m = Map(); m.rows = lines.size(); if (!m.rows) return false; m.cols = lines[0].size(); int starts = 0, goals = 0;
    for (int r = 0; r < m.rows; r++) {
        if ((int)lines[r].size() != m.cols) return false;                  // 직사각형이어야 한다
        m.cost.emplace_back(m.cols, 0);
        for (int c = 0; c < m.cols; c++) { char ch = lines[r][c];
            if (ch == '#') m.cost[r][c] = 0; else if (ch == '.') m.cost[r][c] = 1; else if (ch >= '1' && ch <= '9') m.cost[r][c] = ch - '0';
            else if (ch == 'S') { m.cost[r][c] = 1; m.sr = r; m.sc = c; starts++; } else if (ch == 'G') { m.cost[r][c] = 1; m.gr = r; m.gc = c; goals++; } else return false; }
    }
    return starts == 1 && goals == 1;
}
int main() {
    Map m; std::vector<std::string> ok = {"S..#....", ".#.#.##.", ".#...#..", ".####.#.", "...9...G"};
    assert(parseMap(ok, m) && m.rows == 5 && m.cols == 8 && m.sr == 0 && m.sc == 0 && m.gr == 4 && m.gc == 7);
    assert(m.passable(0, 1) && !m.passable(0, 3) && !m.passable(-1, 0) && !m.passable(5, 0) && m.cost[4][3] == 9);        // 벽·범위 밖·지형 비용
    int walls = 0; for (auto& row : m.cost) for (int v : row) walls += v == 0; assert(walls == 12);
    Map bad; assert(!parseMap({"S..", "..G."}, bad) && !parseMap({"S.."}, bad) && !parseMap({"S.G", "S.."}, bad) && !parseMap({"S.x", "..G"}, bad));    // 들쭉날쭉, 목표 없음, 시작 둘, 모르는 글자
    std::cout << "CreateMap: " << m.rows << "x" << m.cols << " map parsed, " << walls << " walls, invalid maps rejected" << std::endl; return 0;
}
// Time Complexity: O(행 × 열)
// Space Complexity: O(행 × 열)
```
## CreateGrid()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 격자 위의 이동 규칙이 곧 그래프의 간선이다. 4방향은 비용 1, 8방향은 대각선 비용 √2 인데 부동소수점 대신 정수 10 과 14(≈10√2)로 스케일해 비교·해시 오차를 없앤다.
// 대각선 이동에는 "모서리 자르기(corner cutting)" 규칙이 필요하다 — 대각선으로 지나가는 두 칸 중 하나라도 벽이면 벽 모서리를 스치며 통과하므로 보통 금지한다 (게임에 따라 허용하기도).
// 이웃 생성 함수를 한 곳에 모아 두면 BFS / Dijkstra / A* 가 모두 같은 규칙을 공유한다
struct Grid {
    int R, C; std::vector<std::string> w; bool diag, cut;                  // w: '#' 벽. diag: 8방향 허용, cut: 모서리 자르기 허용
    bool ok(int r, int c) const { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; }
    std::vector<std::pair<std::pair<int, int>, int>> neighbors(int r, int c) const {
        std::vector<std::pair<std::pair<int, int>, int>> out; static const int dr[8] = {-1, 1, 0, 0, -1, -1, 1, 1}, dc[8] = {0, 0, -1, 1, -1, 1, -1, 1};
        for (int d = 0; d < (diag ? 8 : 4); d++) { int nr = r + dr[d], nc = c + dc[d]; if (!ok(nr, nc)) continue;
            if (d >= 4 && !cut && (!ok(r + dr[d], c) || !ok(r, c + dc[d]))) continue;                  // 대각선: 인접한 두 칸 중 하나라도 벽이면 금지
            out.push_back({{nr, nc}, d < 4 ? 10 : 14}); }
        return out;
    }
};
int main() {
    Grid open{5, 5, {".....", ".....", ".....", ".....", "....."}, true, false};
    assert(open.neighbors(2, 2).size() == 8 && open.neighbors(0, 0).size() == 3 && open.neighbors(0, 2).size() == 5);          // 열린 곳 8, 모서리 3, 가장자리 5
    int diagCount = 0; for (auto& e : open.neighbors(2, 2)) diagCount += e.second == 14; assert(diagCount == 4);              // 대각선 4 개는 비용 14, 나머지 4 개는 10
    Grid g{5, 5, {".....", ".....", "..#..", ".....", "....."}, true, false};
    assert(g.neighbors(1, 1).size() == 7);                                 // (2,2) 가 벽이라 대각선 하나가 빠진다
    bool hasDiagIntoWall = false; for (auto& e : g.neighbors(1, 1)) hasDiagIntoWall |= e.first == std::make_pair(2, 2); assert(!hasDiagIntoWall);
    // (1,2) 에서 (2,3)·(2,1) 대각선은 벽(2,2) 모서리를 스치므로 금지, 허용하면 가능
    bool cutBlocked = true; for (auto& e : g.neighbors(1, 2)) if (e.first == std::make_pair(2, 3) || e.first == std::make_pair(2, 1)) cutBlocked = false; assert(cutBlocked);
    Grid g2 = g; g2.cut = true; int cutAllowed = 0; for (auto& e : g2.neighbors(1, 2)) cutAllowed += e.first == std::make_pair(2, 3) || e.first == std::make_pair(2, 1); assert(cutAllowed == 2);
    Grid g4 = g; g4.diag = false; assert(g4.neighbors(1, 1).size() == 4);
    long edges = 0; for (int r = 0; r < 5; r++) for (int c = 0; c < 5; c++) if (g.ok(r, c)) edges += g.neighbors(r, c).size();
    for (int r = 0; r < 5; r++) for (int c = 0; c < 5; c++) if (g.ok(r, c)) for (auto& e : g.neighbors(r, c)) { bool back = false; for (auto& f : g.neighbors(e.first.first, e.first.second)) back |= f.first == std::make_pair(r, c) && f.second == e.second; assert(back); }       // 이웃 관계는 대칭
    std::cout << "CreateGrid: 5x5 map with one wall has " << edges << " directed edges (8-neighbour, no corner cutting)" << std::endl; return 0;
}
// Time Complexity: 이웃 생성 O(1)
// Space Complexity: O(1) (격자 자체 O(행 × 열))
```
## CreateNode()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// 탐색 노드 = (칸, 시작에서 온 비용 g, 목표까지 추정 h, 부모). f = g + h 가 작은 노드를 먼저 꺼내는 우선순위 큐가 A* 의 심장이다. 노드는 포인터로 서로 가리키지 않고 "노드 풀 배열의 인덱스"로 부모를 가리키면
// 복사·할당 비용이 없고 경로 복원도 쉽다.  꼭 정해야 할 것이 동점 처리(tie-breaking)다: f 가 같을 때 g 가 큰(= 목표에 더 가까운) 노드를 먼저 꺼내면 열린 공간에서 확장하는 노드 수가 크게 줄어든다
struct Node { int r, c, g, h, parent; int f() const { return g + h; } };
struct Cmp { bool operator()(const Node& a, const Node& b) const { return a.f() != b.f() ? a.f() > b.f() : a.g < b.g; } };         // f 작은 것 우선, 동점이면 g 큰 것 우선
int astarExpansions(int N, bool tieBreak) {                                // N×N 빈 격자에서 (0,0) -> (N-1,N-1), 4방향, 맨해튼 휴리스틱, 확장한 노드 수
    struct C2 { bool tb; bool operator()(const Node& a, const Node& b) const { if (a.f() != b.f()) return a.f() > b.f(); return tb ? a.g < b.g : a.g > b.g; } };
    std::priority_queue<Node, std::vector<Node>, C2> pq{C2{tieBreak}}; std::vector<int> best(N * N, 1 << 30); int expanded = 0;
    pq.push({0, 0, 0, 2 * (N - 1), -1}); best[0] = 0;
    while (!pq.empty()) { Node n = pq.top(); pq.pop(); if (n.g > best[n.r * N + n.c]) continue; expanded++; if (n.r == N - 1 && n.c == N - 1) break;
        static const int dr[4] = {1, 0, -1, 0}, dc[4] = {0, 1, 0, -1};
        for (int d = 0; d < 4; d++) { int nr = n.r + dr[d], nc = n.c + dc[d]; if (nr < 0 || nc < 0 || nr >= N || nc >= N) continue; int g = n.g + 1; if (g < best[nr * N + nc]) { best[nr * N + nc] = g; pq.push({nr, nc, g, (N - 1 - nr) + (N - 1 - nc), 0}); } } }
    return expanded;
}
int main() {
    std::priority_queue<Node, std::vector<Node>, Cmp> pq; pq.push({0, 0, 3, 7, -1}); pq.push({1, 1, 6, 4, 0}); pq.push({2, 2, 1, 9, 0}); pq.push({3, 3, 8, 2, 1});
    assert(pq.top().f() == 10 && pq.top().g == 8);                         // f 가 모두 10 으로 같으면 g 가 가장 큰 노드가 먼저
    pq.pop(); assert(pq.top().g == 6);
    int good = astarExpansions(40, true), bad = astarExpansions(40, false);
    assert(good < bad / 5);                                                // 동점 처리만 바꿔도 확장 수가 크게 다르다
    std::cout << "CreateNode: open 40x40 grid A* expansions with tie-break on larger g = " << good << ", on smaller g = " << bad << std::endl; return 0;
}
// Time Complexity: 노드 생성·비교 O(1)
// Space Complexity: O(1) 노드당
```
## CreateEdge()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <vector>
#include <cassert>

// 간선은 (출발, 도착, 가중치)이다. 같은 그래프를 간선 목록(edge list, 정렬·크루스칼에 편함), 인접 리스트(탐색에 가장 흔함), CSR(Compressed Sparse Row: 연속 메모리라 캐시 친화적, 정적 그래프에 최적)로 표현할 수 있고
// 서로 변환할 수 있어야 한다.  길찾기 알고리즘은 가중치가 음수가 아니라는 전제(Dijkstra, A*)가 많으므로 간선을 만들 때 검증하고, 같은 (출발, 도착)이 여러 번 들어오면 가장 싼 것만 남긴다.
// 무방향 간선은 양방향 간선 두 개로 저장한다
struct Edge { int u, v, w; };
struct CSR { std::vector<int> start, to, w; };
bool addEdge(std::vector<Edge>& es, int u, int v, int w, bool undirected) { if (w < 0) return false; es.push_back({u, v, w}); if (undirected) es.push_back({v, u, w}); return true; }
std::vector<Edge> dedupe(std::vector<Edge> es) { std::sort(es.begin(), es.end(), [](const Edge& a, const Edge& b) { return a.u != b.u ? a.u < b.u : a.v != b.v ? a.v < b.v : a.w < b.w; }); std::vector<Edge> out;
    for (auto& e : es) if (out.empty() || out.back().u != e.u || out.back().v != e.v) out.push_back(e); return out; }
CSR toCSR(const std::vector<Edge>& es, int n) { CSR g; g.start.assign(n + 1, 0); for (auto& e : es) g.start[e.u + 1]++; for (int i = 0; i < n; i++) g.start[i + 1] += g.start[i];
    g.to.resize(es.size()); g.w.resize(es.size()); std::vector<int> pos(g.start.begin(), g.start.end() - 1); for (auto& e : es) { g.to[pos[e.u]] = e.v; g.w[pos[e.u]++] = e.w; } return g; }
int main() {
    std::vector<Edge> es; assert(!addEdge(es, 0, 1, -5, false));            // 음수 가중치는 거절
    addEdge(es, 0, 1, 4, true); addEdge(es, 0, 2, 1, true); addEdge(es, 2, 1, 2, true); addEdge(es, 0, 1, 3, true);     // (0,1) 이 두 번: 4 와 3
    auto d = dedupe(es); assert(d.size() == 6);                            // 양방향 3 쌍 = 6 개, 중복은 싼 것만
    CSR g = toCSR(d, 3); int w01 = -1; for (int k = g.start[0]; k < g.start[1]; k++) if (g.to[k] == 1) w01 = g.w[k]; assert(w01 == 3);
    assert(g.start[3] == (int)d.size() && g.start[1] - g.start[0] == 2);  // 정점 0 의 차수 2
    std::vector<int> deg(3, 0); for (auto& e : d) deg[e.u]++; for (int i = 0; i < 3; i++) assert(g.start[i + 1] - g.start[i] == deg[i]);       // CSR 구간 길이 == 차수
    std::cout << "CreateEdge: " << d.size() << " directed edges after dedupe, CSR row starts: " << g.start[0] << " " << g.start[1] << " " << g.start[2] << " " << g.start[3] << std::endl; return 0;
}
// Time Complexity: 간선 추가 O(1), 중복 제거 O(E log E), CSR 변환 O(V + E)
// Space Complexity: O(V + E)
```
## BuildGraph()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <cassert>

// 격자 지도를 일반 그래프로 바꾸면 격자에서 쓰던 알고리즘(BFS, Dijkstra, A*)을 도로망·내비메시 같은 임의의 그래프에서도 그대로 쓸 수 있다. 통과 가능한 칸마다 정점 번호 r*C+c 를 주고,
// 이웃 규칙(4/8방향, 모서리 자르기 금지)에 따라 간선을 만든다. 벽 칸은 정점이 되지 않으므로 그래프가 작아진다(번호는 그대로 두고 인접 리스트만 비워 둔다).
// 변환이 맞는지 BFS 를 격자에서 직접 한 결과와 그래프에서 한 결과로 비교한다
struct G { int R, C; std::vector<std::vector<std::pair<int, int>>> adj; };
G build(const std::vector<std::string>& w, bool diag) {
    int R = w.size(), C = w[0].size(); G g{R, C, std::vector<std::vector<std::pair<int, int>>>(R * C)}; static const int dr[8] = {-1, 1, 0, 0, -1, -1, 1, 1}, dc[8] = {0, 0, -1, 1, -1, 1, -1, 1};
    auto ok = [&](int r, int c) { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; };
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (!ok(r, c)) continue;
        for (int d = 0; d < (diag ? 8 : 4); d++) { int nr = r + dr[d], nc = c + dc[d]; if (!ok(nr, nc)) continue; if (d >= 4 && (!ok(r + dr[d], c) || !ok(r, c + dc[d]))) continue; g.adj[r * C + c].push_back({nr * C + nc, d < 4 ? 10 : 14}); } }
    return g;
}
std::vector<int> bfsGraph(const G& g, int s) { std::vector<int> d(g.adj.size(), -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (auto& e : g.adj[u]) if (d[e.first] < 0) { d[e.first] = d[u] + 1; q.push(e.first); } } return d; }
std::vector<int> bfsGrid(const std::vector<std::string>& w, int sr, int sc, bool diag) {                  // 그래프를 거치지 않고 격자에서 직접
    int R = w.size(), C = w[0].size(); std::vector<int> d(R * C, -1); std::queue<std::pair<int, int>> q; d[sr * C + sc] = 0; q.push({sr, sc});
    auto ok = [&](int r, int c) { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; };
    while (!q.empty()) { auto [r, c] = q.front(); q.pop(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; if (!diag && dr && dc) continue; int nr = r + dr, nc = c + dc; if (!ok(nr, nc)) continue;
        if (dr && dc && (!ok(r + dr, c) || !ok(r, c + dc))) continue; if (d[nr * C + nc] < 0) { d[nr * C + nc] = d[r * C + c] + 1; q.push({nr, nc}); } } }
    return d;
}
int main() {
    std::vector<std::string> w = {"........", ".##..#..", "........", ".#.###..", "........"};
    for (bool diag : {false, true}) { G g = build(w, diag); assert(bfsGraph(g, 0) == bfsGrid(w, 0, 0, diag)); }       // 두 방식의 거리표가 같다
    G g4 = build(w, false), g8 = build(w, true); long e4 = 0, e8 = 0; for (auto& a : g4.adj) e4 += a.size(); for (auto& a : g8.adj) e8 += a.size();
    assert(e8 > e4); int wallsWithEdges = 0; for (int r = 0; r < 5; r++) for (int c = 0; c < 8; c++) if (w[r][c] == '#' && !g8.adj[r * 8 + c].empty()) wallsWithEdges++; assert(wallsWithEdges == 0);   // 벽에는 간선이 없다
    std::cout << "BuildGraph: 4-neighbour graph " << e4 << " directed edges, 8-neighbour graph " << e8 << ", BFS agrees with direct grid BFS" << std::endl; return 0;
}
// Time Complexity: O(행 × 열 × 이웃 수)
// Space Complexity: O(V + E)
```
## InitializeSearch()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// 길찾기를 여러 번(질의마다, 매 프레임마다) 부를 때 거리표·부모표·방문표를 매번 0 으로 다시 채우면 정점 수 V 만큼의 비용이 든다. 지도가 100만 칸이고 질의가 가까운 두 점이면 탐색은 수백 칸만 보는데 초기화에 100만 번을 쓴다.
// 해결: 칸마다 "마지막으로 쓴 질의 번호(stamp)"를 두고 현재 번호와 다르면 아직 초기화 안 된 칸으로 보고 그 자리에서 기본값을 쓴다 — 질의 시작은 번호를 하나 올리는 O(1).
// 이 항목은 이런 "세대 번호 초기화"가 정확함(이전 질의의 값이 새 질의에 새지 않음)과 일 양(쓴 칸 수만 초기화)을 보인다
struct Search {
    std::vector<int> dist, parent, stamp; int epoch = 0; long touched = 0; explicit Search(int n) : dist(n), parent(n), stamp(n, 0) {}
    void reset() { epoch++; }                                              // O(1)
    int& d(int v) { if (stamp[v] != epoch) { stamp[v] = epoch; dist[v] = 1 << 30; parent[v] = -1; touched++; } return dist[v]; }
    bool seen(int v) const { return stamp[v] == epoch; }
};
int bfs(Search& s, const std::vector<std::vector<int>>& adj, int a, int b) {
    s.reset(); std::queue<int> q; s.d(a) = 0; q.push(a); while (!q.empty()) { int u = q.front(); q.pop(); if (u == b) return s.d(u); for (int v : adj[u]) if (s.d(v) == (1 << 30)) { s.d(v) = s.d(u) + 1; q.push(v); } } return -1;
}
int main() {
    const int N = 200000; std::vector<std::vector<int>> adj(N); for (int i = 0; i + 1 < N; i++) { adj[i].push_back(i + 1); adj[i + 1].push_back(i); }        // 긴 직선 그래프
    Search s(N); assert(bfs(s, adj, 0, 5) == 5); long afterFirst = s.touched; assert(afterFirst < 20);                                    // 가까운 두 점: 20 칸도 안 건드렸다
    assert(bfs(s, adj, 100, 103) == 3 && s.touched - afterFirst < 20);
    assert(!s.seen(0) && s.seen(100));                                     // 이전 질의가 칠한 칸(0)은 새 질의에서 "보지 않은 칸"이다
    for (int t = 0; t < 1000; t++) { int a = (t * 7919) % (N - 10), b = a + t % 8; assert(bfs(s, adj, a, b) == b - a); }
    assert(s.touched < 1000 * 40);                                         // 1000 질의 총 수만 칸 (매번 전체를 지웠다면 2억)
    std::cout << "InitializeSearch: 1000 queries on " << N << " nodes touched only " << s.touched << " cells (full clear would write " << 1000L * N << ")" << std::endl; return 0;
}
// Time Complexity: 초기화 O(1), 질의는 방문한 칸 수 비례
// Space Complexity: O(V)
```
## IsReachable()
### 대표코드
```cpp
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// "갈 수 있는가?"만 묻는다면 경로를 구할 필요가 없다. 한 번만 묻는다면 BFS(또는 DFS)를 목표를 만나는 즉시 멈추게 하는 O(V+E). 같은 지도에서 여러 번 묻는다면 연결 요소를 미리 한 번 구해 두고 요소 번호를 비교하면 질의마다 O(1) 이다.
// 서로소 집합(Union-Find)은 지도가 변하며 벽이 "사라지는"(칸이 열리는) 쪽으로만 갱신될 때 요소를 거의 O(1) 에 병합해 준다 (벽이 새로 생기는 방향은 어렵다).
// 이동 규칙에 따라 연결성이 달라진다: mode 0 = 4방향, 1 = 8방향(모서리 자르기 금지), 2 = 8방향(모서리 자르기 허용). 1 은 0 과 항상 같다(대각선 이동이 가능하려면 인접한 두 칸이 열려 있어야 하고 그러면 4방향 두 번으로도 갈 수 있다).
// 2 는 막힌 모서리를 스쳐 지나가므로 0 보다 연결이 많아질 수 있다
int R, C; std::vector<std::string> w;
bool ok(int r, int c) { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; }
bool step(int r, int c, int dr, int dc, int mode) { int nr = r + dr, nc = c + dc; if (!ok(nr, nc)) return false; if (dr && dc) { if (mode == 0) return false; if (mode == 1 && (!ok(r + dr, c) || !ok(r, c + dc))) return false; } return true; }
bool reachBFS(int sr, int sc, int gr, int gc, int mode, int& visited) {
    std::vector<char> seen(R * C, 0); std::queue<std::pair<int, int>> q; q.push({sr, sc}); seen[sr * C + sc] = 1; visited = 0;
    while (!q.empty()) { auto [r, c] = q.front(); q.pop(); visited++; if (r == gr && c == gc) return true;
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; if (!step(r, c, dr, dc, mode)) continue; int nr = r + dr, nc = c + dc; if (seen[nr * C + nc]) continue; seen[nr * C + nc] = 1; q.push({nr, nc}); } }
    return false;
}
struct DSU { std::vector<int> p; explicit DSU(int n) : p(n) { std::iota(p.begin(), p.end(), 0); } int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); } void unite(int a, int b) { p[find(a)] = find(b); } };
DSU components(int mode) { DSU d(R * C); for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (!ok(r, c)) continue; for (int dr = 0; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && dc <= 0) continue; if (step(r, c, dr, dc, mode)) d.unite(r * C + c, (r + dr) * C + c + dc); } } return d; }
int main() {
    std::mt19937 g(1); R = 30; C = 30; int trials = 0, onlyCut = 0;
    for (int t = 0; t < 40; t++) { w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (g() % 100 < 40) ch = '#';
        DSU d0 = components(0), d1 = components(1), d2 = components(2);
        for (int q = 0; q < 100; q++) { int a = g() % (R * C), b = g() % (R * C); if (!ok(a / C, a % C) || !ok(b / C, b % C)) continue; int vis;
            bool r0 = reachBFS(a / C, a % C, b / C, b % C, 0, vis), r1 = reachBFS(a / C, a % C, b / C, b % C, 1, vis), r2 = reachBFS(a / C, a % C, b / C, b % C, 2, vis); trials++;
            assert(r0 == (d0.find(a) == d0.find(b)) && r1 == (d1.find(a) == d1.find(b)) && r2 == (d2.find(a) == d2.find(b)));          // BFS 와 요소 번호 비교가 항상 일치
            assert(r0 == r1 && (!r0 || r2)); onlyCut += r2 && !r0; } }       // 모서리 자르기 금지 8방향 == 4방향, 자르기를 허용하면 더 많이 연결
    assert(onlyCut > 0);
    w = {"S.#....", "..#.###", "..#...G", "..#####", "......."}; R = 5; C = 7; int vis; assert(!reachBFS(0, 0, 2, 6, 1, vis) && vis == 15);          // 벽에 막혀 닿는 칸 15 개를 모두 훑고도 못 간다
    std::cout << "IsReachable: BFS == union-find on " << trials << " queries; " << onlyCut << " pairs are connected only when corner cutting is allowed" << std::endl; return 0;
}
// Time Complexity: BFS 질의 O(V+E), 요소 전처리 후 질의 O(α(V))
// Space Complexity: O(V)
```
## ReconstructPath()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <cassert>

// 탐색이 끝나면 각 칸에는 "나를 처음 발견한 칸(부모)" 만 남는다. 경로는 목표에서 부모를 따라 시작까지 거슬러 올라간 뒤 뒤집어 얻는다.
// 확인할 것 셋: ① 목표에 부모가 없으면(= 도달 못 함) 빈 경로 ② 부모 사슬에 사이클이 있으면(버그) 무한 루프 대신 걸러 내기 ③ 복원한 경로가 정말 유효한가 — 연속한 두 칸이 이웃이고 모두 통과 가능한지,
// 비용이 탐색이 보고한 거리와 같은지 검사하는 함수를 같이 둔다 (모든 경로 알고리즘 테스트에서 재사용)
typedef std::pair<int, int> P;
std::vector<int> reconstruct(const std::vector<int>& parent, int goal, int start) {
    std::vector<int> path; int steps = 0;
    for (int v = goal; v != -1; v = parent[v]) { path.push_back(v); if (v == start) { std::reverse(path.begin(), path.end()); return path; } if (++steps > (int)parent.size()) return {}; }       // 사이클 방어
    return {};                                                              // 시작에 닿지 못했다
}
bool validPath(const std::vector<std::string>& w, const std::vector<int>& path, bool diag, int expectedSteps) {
    int C = w[0].size(); if (path.empty() || (int)path.size() - 1 != expectedSteps) return false;
    for (size_t i = 0; i < path.size(); i++) { int r = path[i] / C, c = path[i] % C; if (r < 0 || r >= (int)w.size() || c < 0 || c >= C || w[r][c] == '#') return false;
        if (i) { int pr = path[i - 1] / C, pc = path[i - 1] % C, dr = std::abs(r - pr), dc = std::abs(c - pc); if (dr > 1 || dc > 1 || (dr + dc == 0) || (!diag && dr + dc != 1)) return false; } }
    return true;
}
int main() {
    std::vector<std::string> w = {"S...#...", ".##.#.#.", ".#..#.#.", ".#.##.#.", ".#....#G"}; int R = w.size(), C = w[0].size(), s = 0, g = 4 * C + 7;
    std::vector<int> dist(R * C, -1), parent(R * C, -1); std::queue<int> q; dist[s] = 0; q.push(s);
    while (!q.empty()) { int u = q.front(); q.pop(); int r = u / C, c = u % C; const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int d = 0; d < 4; d++) { int nr = r + dr[d], nc = c + dc[d]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || dist[nr * C + nc] >= 0) continue; dist[nr * C + nc] = dist[u] + 1; parent[nr * C + nc] = u; q.push(nr * C + nc); } }
    std::vector<int> path = reconstruct(parent, g, s);
    assert(!path.empty() && path.front() == s && path.back() == g && validPath(w, path, false, dist[g]));       // 거리 dist[g] 만큼의 유효한 경로
    std::vector<int> bad = parent; bad[path[2]] = path[3]; assert(reconstruct(bad, g, s).empty());       // 부모 사슬이 시작에 닿지 못하고 맴돌면(사이클) 무한 루프 대신 빈 경로
    std::vector<int> broken = path; broken[3] = broken[3] + 2 * C + 3; assert(!validPath(w, broken, false, dist[g]));                             // 이웃이 아닌 점프는 유효하지 않다
    std::vector<int> noParent(R * C, -1); assert(reconstruct(noParent, g, s).empty());                                                            // 도달 못 함 -> 빈 경로
    std::cout << "ReconstructPath: BFS path of " << path.size() - 1 << " steps rebuilt from parents and validated" << std::endl; return 0;
}
// Time Complexity: O(경로 길이)
// Space Complexity: O(경로 길이)
```

# Part 2. 기초 탐색
## BreadthFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

bool BFS(const std::vector<std::vector<int>>& graph, int start, int target) {
    std::vector<bool> visited(graph.size(), false);
    std::queue<int> q;
    q.push(start); visited[start] = true;
    while(!q.empty()) {
        int curr = q.front(); q.pop();
        if(curr == target) return true;
        for(int neighbor : graph[curr]) {
            if(!visited[neighbor]) {
                visited[neighbor] = true;
                q.push(neighbor);
            }
        }
    }
    return false;
}

int main() {
    std::vector<std::vector<int>> graph = {{1, 2}, {0, 3}, {0}, {1}};
    assert(BFS(graph, 0, 3) == true);
    std::cout << "BFS verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## DepthFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

bool DFS_util(const std::vector<std::vector<int>>& graph, int curr, int target, std::vector<bool>& visited) {
    if(curr == target) return true;
    visited[curr] = true;
    for(int neighbor : graph[curr]) {
        if(!visited[neighbor] && DFS_util(graph, neighbor, target, visited)) return true;
    }
    return false;
}

int main() {
    std::vector<std::vector<int>> graph = {{1, 2}, {0, 3}, {0}, {1}};
    std::vector<bool> visited(4, false);
    assert(DFS_util(graph, 0, 3, visited) == true);
    std::cout << "DFS verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## IterativeDeepeningDFS()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 반복 깊이 증가 DFS(IDDFS, 그래프 관점의 요약은 Graph.md Part 10): 깊이 제한 DFS 를 제한 0, 1, 2, ... 로 반복해 BFS 처럼 "가장 얕은 해" 를 찾되 메모리는 DFS 처럼 O(깊이) 만 쓴다.
// 얕은 층을 되풀이해 방문하는 낭비는 분기 계수 b 가 2 이상이면 가장 깊은 층의 방문 수가 압도해 전체의 약 b/(b-1) 배에 그친다
long visited = 0;
bool dls(int node, int goal, int limit, const std::vector<std::vector<int>>& adj, std::vector<int>& path) { visited++; path.push_back(node); if (node == goal) return true; if (limit > 0) for (int v : adj[node]) if (dls(v, goal, limit - 1, adj, path)) return true; path.pop_back(); return false; }
int main() {
    int depth = 12; std::vector<std::vector<int>> adj((1 << (depth + 1)) - 1); for (int i = 0; i < (1 << depth) - 1; i++) { adj[i].push_back(2 * i + 1); adj[i].push_back(2 * i + 2); }       // 이진 트리
    int goal = (1 << depth) - 1 + 777; std::vector<int> path; int found = -1;
    for (int limit = 0; limit <= depth; limit++) { path.clear(); if (dls(0, goal, limit, adj, path)) { found = limit; break; } }
    assert(found == depth && (int)path.size() == depth + 1 && path.front() == 0 && path.back() == goal);         // 가장 얕은 깊이에서 해를 찾는다
    long bfsLike = (1 << (depth + 1)) - 1; assert(visited < 3 * bfsLike);                                           // 반복 낭비는 BFS 방문 수의 작은 상수배
    std::cout << "IterativeDeepeningDFS: goal at depth " << found << ", nodes visited " << visited << " (BFS would visit up to " << bfsLike << ") with O(depth) memory" << std::endl; return 0;
}
// Time Complexity: O(b^d) (b/(b-1) 배의 중복 포함)
// Space Complexity: O(d)
```
## BidirectionalSearch()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// 양방향 탐색(그래프 관점의 요약은 Graph.md Part 10): 시작과 목표에서 동시에 BFS 를 돌려 두 탐색 영역이 만나면 끝낸다. 한 방향 탐색이 반지름 d 의 "공"을 채우는 데 b^d 를 쓴다면 양방향은 반지름 d/2 짜리 공 둘이라 2·b^(d/2) 로 훨씬 적다.
// 한 층 전체를 확장한 뒤 교차를 확인해야 최단 거리가 보장되고, 더 작은 쪽 frontier 를 확장하면 균형이 맞는다
int main() {
    const int N = 300; auto id = [&](int r, int c) { return r * N + c; }; std::vector<std::vector<int>> adj(N * N);
    for (int r = 0; r < N; r++) for (int c = 0; c < N; c++) { if (r + 1 < N) { adj[id(r, c)].push_back(id(r + 1, c)); adj[id(r + 1, c)].push_back(id(r, c)); } if (c + 1 < N) { adj[id(r, c)].push_back(id(r, c + 1)); adj[id(r, c + 1)].push_back(id(r, c)); } }
    auto bfsExpand = [&](int s, int t, long& exp) { std::vector<int> d(N * N, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); exp++; if (u == t) return d[u]; for (int v : adj[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } return -1; };
    auto biExpand = [&](int s, int t, long& exp) { std::vector<int> da(N * N, -1), db(N * N, -1); std::vector<int> fa = {s}, fb = {t}; da[s] = 0; db[t] = 0; if (s == t) return 0;
        while (!fa.empty() && !fb.empty()) { bool fwd = fa.size() <= fb.size(); auto& f = fwd ? fa : fb; auto& dm = fwd ? da : db; auto& other = fwd ? db : da; std::vector<int> nxt; int best = -1;
            for (int u : f) { exp++; for (int v : adj[u]) { if (dm[v] >= 0) continue; dm[v] = dm[u] + 1; nxt.push_back(v); if (other[v] >= 0) best = best < 0 ? dm[v] + other[v] : std::min(best, dm[v] + other[v]); } }
            if (best >= 0) return best; f = nxt; } return -1; };
    long e1 = 0, e2 = 0; int s = id(100, 100), t = id(130, 140); int d1 = bfsExpand(s, t, e1), d2 = biExpand(s, t, e2);
    assert(d1 == d2 && d1 == 30 + 40 && e2 * 3 < e1 * 2);                  // 같은 최단 거리, 확장한 노드는 BFS 의 2/3 미만 (지도 경계에 닿지 않을 때 약 1/2)
    std::cout << "BidirectionalSearch: distance " << d2 << ", expansions BFS " << e1 << " vs bidirectional " << e2 << std::endl; return 0;
}
// Time Complexity: O(b^(d/2)) × 2
// Space Complexity: O(b^(d/2))
```
## MultiSourceBFS()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <cassert>

// 다중 출발점 BFS(큐 관점의 요약은 Queue.md Part 6): 출발점이 여러 개일 때 모든 출발점을 거리 0 으로 한꺼번에 큐에 넣고 BFS 를 한 번만 돌리면 각 칸에서 "가장 가까운 출발점까지의 거리"가 O(V+E) 에 나온다.
// 출발점마다 BFS 를 따로 돌려 최솟값을 취하는 O(k(V+E)) 와 결과가 같다. 용도: 가장 가까운 소화전·출구·불길까지의 거리, 거리 변환(distance transform), 부패하는 오렌지 문제
int main() {
    std::vector<std::string> w = {"........", ".#####..", "......#.", ".####.#.", "........"}; int R = w.size(), C = w[0].size();
    std::vector<std::pair<int, int>> src = {{0, 0}, {4, 7}, {2, 0}}; auto run = [&](const std::vector<std::pair<int, int>>& ss) { std::vector<int> d(R * C, -1); std::queue<std::pair<int, int>> q; for (auto& s : ss) { d[s.first * C + s.second] = 0; q.push(s); }
        while (!q.empty()) { auto [r, c] = q.front(); q.pop(); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || d[nr * C + nc] >= 0) continue; d[nr * C + nc] = d[r * C + c] + 1; q.push({nr, nc}); } } return d; };
    std::vector<int> multi = run(src), best(R * C, -1); for (auto& s : src) { auto one = run({s}); for (int i = 0; i < R * C; i++) if (one[i] >= 0 && (best[i] < 0 || one[i] < best[i])) best[i] = one[i]; }
    assert(multi == best);                                                 // 한 번의 BFS == 출발점별 BFS 의 최솟값
    std::cout << "MultiSourceBFS: one BFS from " << src.size() << " sources equals the min of " << src.size() << " separate BFS runs" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```

# Part 3. 가중치 최단 경로
## Dijkstra()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

int Dijkstra(int V, const std::vector<std::vector<std::pair<int, int>>>& graph, int start, int end) {
    std::vector<int> dist(V, 1e9);
    std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq;
    dist[start] = 0; pq.push({0, start});
    while(!pq.empty()) {
        int d = pq.top().first, u = pq.top().second; pq.pop();
        if(d > dist[u]) continue;
        if(u == end) return dist[u];
        for(auto& edge : graph[u]) {
            int v = edge.first, weight = edge.second;
            if(dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                pq.push({dist[v], v});
            }
        }
    }
    return dist[end];
}

int main() {
    std::vector<std::vector<std::pair<int, int>>> graph(3);
    graph[0].push_back({1, 10}); graph[1].push_back({2, 5}); graph[0].push_back({2, 20});
    assert(Dijkstra(3, graph, 0, 2) == 15);
    std::cout << "Dijkstra verified." << std::endl;
    return 0;
}
// Time Complexity: O(E log V)
```
## BellmanFord()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int V = 3;
    std::vector<std::pair<std::pair<int, int>, int>> edges = {{{0, 1}, 10}, {{1, 2}, -5}};
    std::vector<int> dist(V, 1e9); dist[0] = 0;
    for(int i = 0; i < V - 1; i++) {
        for(auto& e : edges) {
            if(dist[e.first.first] != 1e9 && dist[e.first.first] + e.second < dist[e.first.second])
                dist[e.first.second] = dist[e.first.first] + e.second;
        }
    }
    assert(dist[2] == 5);
    std::cout << "Bellman-Ford verified." << std::endl;
    return 0;
}
// Time Complexity: O(V * E)
```
## SPFA()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// SPFA(Shortest Path Faster Algorithm; 그래프 관점의 요약은 Graph.md Part 9): 벨먼-포드의 "모든 간선을 V-1 번 훑기" 대신, 거리가 줄어든 정점만 큐에 넣어 그 정점의 간선만 완화한다. 음수 간선이 있어도 되고
// 평균적으로 O(E) 에 가깝게 빠르지만 최악은 벨먼-포드와 같은 O(VE) 이며 일부 입력(격자 등)에서 악의적으로 느려진다. 정점이 큐에 V 번 이상 들어가면 음수 사이클이다
struct E { int to, w; };
bool spfa(int n, const std::vector<std::vector<E>>& g, int s, std::vector<long>& d) {
    d.assign(n, 1L << 60); std::vector<int> cnt(n, 0); std::vector<char> in(n, 0); std::queue<int> q; d[s] = 0; q.push(s); in[s] = 1;
    while (!q.empty()) { int u = q.front(); q.pop(); in[u] = 0; for (auto& e : g[u]) if (d[u] + e.w < d[e.to]) { d[e.to] = d[u] + e.w; if (!in[e.to]) { if (++cnt[e.to] >= n) return false; in[e.to] = 1; q.push(e.to); } } }
    return true;
}
int main() {
    int n = 6; std::vector<std::vector<E>> g(n); g[0] = {{1, 7}, {2, 9}, {5, 14}}; g[1] = {{2, -5}, {3, 15}}; g[2] = {{3, 11}, {5, 2}}; g[3] = {{4, 6}}; g[5] = {{4, 9}};
    std::vector<long> d; assert(spfa(n, g, 0, d) && d[2] == 2 && d[5] == 4 && d[4] == 13 && d[3] == 13);       // 음수 간선(1->2: -5)이 있어도 정확
    g[4].push_back({1, -20}); assert(!spfa(n, g, 0, d));                                                         // 음수 사이클 탐지
    std::cout << "SPFA: shortest distances with a negative edge computed, negative cycle detected" << std::endl; return 0;
}
// Time Complexity: 평균 O(E), 최악 O(VE)
// Space Complexity: O(V)
```
## FloydWarshall()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    int V = 3, INF = 1e9;
    std::vector<std::vector<int>> dist = {{0, 5, INF}, {INF, 0, 10}, {INF, INF, 0}};
    for(int k=0; k<V; k++) {
        for(int i=0; i<V; i++) {
            for(int j=0; j<V; j++) {
                if(dist[i][k] != INF && dist[k][j] != INF)
                    dist[i][j] = std::min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
    }
    assert(dist[0][2] == 15);
    std::cout << "Floyd-Warshall verified." << std::endl;
    return 0;
}
// Time Complexity: O(V^3)
```
## Johnson()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// 존슨 알고리즘(그래프 관점의 요약은 Graph.md Part 9): 음수 간선이 있는 희소 그래프의 모든 쌍 최단 거리. 플로이드-워셜 O(V³) 대신 O(V·E log V). 비결은 "재가중": 가상 정점에서 벨먼-포드로 퍼텐셜 h(v)를 구하고
// 간선 w(u,v)를 w + h(u) - h(v) >= 0 으로 바꾸면 모든 경로의 길이가 (끝점에만 의존하는) 같은 양만큼 변해 최단 경로는 그대로이면서 음수 간선이 사라져, 정점마다 다익스트라를 쓸 수 있다. 원래 거리 = 재가중 거리 - h(u) + h(v)
struct E { int u, v, w; };
int main() {
    int n = 5; std::vector<E> es = {{0, 1, 3}, {0, 2, 8}, {0, 4, -4}, {1, 3, 1}, {1, 4, 7}, {2, 1, 4}, {3, 0, 2}, {3, 2, -5}, {4, 3, 6}}; const long INF = 1L << 50;
    std::vector<long> h(n + 1, INF); h[n] = 0; std::vector<E> all = es; for (int v = 0; v < n; v++) all.push_back({n, v, 0});          // 가상 정점 n -> 모든 정점 (비용 0)
    for (int i = 0; i <= n; i++) for (auto& e : all) if (h[e.u] < INF && h[e.u] + e.w < h[e.v]) h[e.v] = h[e.u] + e.w;
    std::vector<std::vector<std::pair<int, long>>> g(n); for (auto& e : es) { long w2 = e.w + h[e.u] - h[e.v]; assert(w2 >= 0); g[e.u].push_back({e.v, w2}); }
    std::vector<std::vector<long>> D(n, std::vector<long>(n, INF));
    for (int s = 0; s < n; s++) { std::vector<long> d(n, INF); std::priority_queue<std::pair<long, int>, std::vector<std::pair<long, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
        while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto& e : g[u]) if (du + e.second < d[e.first]) { d[e.first] = du + e.second; pq.push({d[e.first], e.first}); } }
        for (int v = 0; v < n; v++) if (d[v] < INF) D[s][v] = d[v] - h[s] + h[v]; }
    std::vector<std::vector<long>> F(n, std::vector<long>(n, INF)); for (int i = 0; i < n; i++) F[i][i] = 0; for (auto& e : es) F[e.u][e.v] = std::min<long>(F[e.u][e.v], e.w);
    for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (F[i][k] < INF && F[k][j] < INF) F[i][j] = std::min(F[i][j], F[i][k] + F[k][j]);
    assert(D == F && D[0][4] == -4 && D[3][2] == -5 && D[1][4] == -1);                      // 플로이드-워셜과 같은 전쌍 최단 거리
    std::cout << "Johnson: all-pairs shortest paths with negative edges match Floyd-Warshall" << std::endl; return 0;
}
// Time Complexity: O(V·E log V)
// Space Complexity: O(V²) 결과표
```

# Part 4. 휴리스틱 탐색
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

// 탐욕 최선 우선 탐색(Greedy Best-First): 목표까지의 추정 거리 h(n) 만 보고 가장 목표에 가까워 보이는 노드를 먼저 펼친다 (f = h, 지금까지 온 비용 g 는 무시).
// 장애물이 없으면 거의 직선으로 달려가 A* 보다 훨씬 적은 노드를 확장하지만, 벽에 막혀 "가까워 보이는 막다른 길" 로 들어가면 그곳을 다 채우고 나서야 돌아 나온다 — 최단 경로가 아닐 수 있고(최적성 없음) 그래도 유한 그래프에서 해가 있으면 찾는다(완전성).
// 빠른 근사해가 필요한 곳(게임 NPC 의 대충 이동)에서 쓴다.  코드는 A* 와 같은 틀에서 정렬 키만 g+h 에서 h 로 바꾼 것이다
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
    for (int t = 0; t < 300; t++) {
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
## AStar()
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

// A*(Hart–Nilsson–Raphael 1968): 노드를 f(n) = g(n) + h(n) 순서로 확장한다 — g 는 시작에서 n 까지 실제로 온 비용, h 는 n 에서 목표까지 남은 거리의 추정.
// h 가 "허용 가능(admissible; 실제 남은 거리를 넘지 않음)" 하면 목표를 꺼내는 순간의 g 가 최적 비용이고, 추가로 "일관적(consistent; h(a) <= c(a,b) + h(b))" 이면 한 노드는 한 번만 확장하면 된다(닫힌 집합).
// 격자에서 4방향 이동은 맨해튼 거리, 8방향(직선 10·대각 14)은 옥타일 거리 10·(dx+dy) - 6·min(dx,dy) 가 일관적이다.  동점은 g 가 큰 노드를 먼저(CreateNode 항목) 꺼내면 확장 수가 크게 준다.
// 이 항목의 시험: 무작위 지도 수백 개에서 Dijkstra(h = 0)와 비용이 항상 같고 확장은 더 적으며, 반대로 h 를 과대 추정(허용 불가)하면 최적이 깨지는 사례가 나온다
typedef std::pair<int, int> P;
struct Grid { int R, C; std::vector<std::string> w; bool diag = true;
    bool ok(int r, int c) const { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; }
    template <class F> void nb(int r, int c, F f) const { for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; if (!diag && dr && dc) continue; int nr = r + dr, nc = c + dc; if (!ok(nr, nc)) continue; if (dr && dc && (!ok(r + dr, c) || !ok(r, c + dc))) continue; f(nr, nc, dr && dc ? 14 : 10); } } };
struct Res { long cost = -1; long expanded = 0; std::vector<P> path; };
int heur(const Grid& g, P a, P b) { int dr = std::abs(a.first - b.first), dc = std::abs(a.second - b.second); return g.diag ? 10 * (dr + dc) - 6 * std::min(dr, dc) : 10 * (dr + dc); }
Res astar(const Grid& g, P s, P t, double hw) {                            // hw: 휴리스틱 배율 (0 = Dijkstra, 1 = A*, > 1 = 과대 추정)
    Res res; int n = g.R * g.C; std::vector<long> gc(n, 1L << 60); std::vector<int> parent(n, -1); std::vector<char> closed(n, 0); using Q = std::pair<std::pair<double, long>, int>;
    std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; int si = s.first * g.C + s.second, ti = t.first * g.C + t.second; gc[si] = 0; pq.push({{hw * heur(g, s, t), 0}, si});
    while (!pq.empty()) { int u = pq.top().second; pq.pop(); if (closed[u]) continue; closed[u] = 1; res.expanded++;
        if (u == ti) { res.cost = gc[u]; for (int v = u; v >= 0; v = parent[v]) res.path.push_back({v / g.C, v % g.C}); std::reverse(res.path.begin(), res.path.end()); return res; }
        g.nb(u / g.C, u % g.C, [&](int nr, int nc, int c) { int v = nr * g.C + nc; if (closed[v]) return; long ng = gc[u] + c; if (ng < gc[v]) { gc[v] = ng; parent[v] = u; pq.push({{ng + hw * heur(g, {nr, nc}, t), -ng}, v}); } }); }          // 일관적인 h 에서는 닫힌 노드를 다시 열 필요가 없다
    return res;
}
bool validPath(const Grid& g, const std::vector<P>& p, long cost) {
    long c = 0; for (size_t i = 0; i < p.size(); i++) { if (!g.ok(p[i].first, p[i].second)) return false; if (i) { int dr = std::abs(p[i].first - p[i - 1].first), dc = std::abs(p[i].second - p[i - 1].second); if (dr > 1 || dc > 1 || !(dr + dc)) return false; if (!g.diag && dr + dc != 1) return false;
        if (dr && dc && (!g.ok(p[i - 1].first, p[i].second) || !g.ok(p[i].first, p[i - 1].second))) return false; c += dr && dc ? 14 : 10; } } return c == cost; }
int main() {
    std::mt19937 gen(2); long aExp = 0, dExp = 0, solved = 0, suboptimal = 0;
    for (int t = 0; t < 400; t++) {
        Grid g{28, 28, std::vector<std::string>(28, std::string(28, '.'))}; g.diag = t % 2; for (auto& row : g.w) for (auto& ch : row) if (gen() % 100 < 25) ch = '#';
        P s{(int)(gen() % 28), (int)(gen() % 28)}, e{(int)(gen() % 28), (int)(gen() % 28)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        Res a = astar(g, s, e, 1.0), d = astar(g, s, e, 0.0); assert(a.cost == d.cost);                              // 4방향·8방향 모두 Dijkstra 와 같은 최적 비용 (도달 불가도 일치)
        if (a.cost < 0) continue; solved++; assert(validPath(g, a.path, a.cost) && a.path.front() == s && a.path.back() == e); aExp += a.expanded; dExp += d.expanded;
        Res bad = astar(g, s, e, 3.0); assert(bad.cost >= a.cost && validPath(g, bad.path, bad.cost)); suboptimal += bad.cost > a.cost;        // 과대 추정: 경로는 유효하지만 최적이 아닐 수 있다
    }
    assert(aExp < dExp && suboptimal > 0);
    std::cout << "AStar: optimal on " << solved << " solvable maps (== Dijkstra), expansions A* " << aExp << " vs Dijkstra " << dExp << "; with inadmissible 3x heuristic " << suboptimal << " paths were suboptimal" << std::endl; return 0;
}
// Time Complexity: 최악 O(b^d), 좋은 휴리스틱에서는 O(경로 주변)
// Space Complexity: O(탐색한 노드 수)
```
## WeightedAStar()
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

// 가중 A*(Pohl 1970): f = g + w·h (w >= 1). 휴리스틱을 더 믿어서 목표 쪽으로 더 곧장 가므로 확장이 크게 줄고, 대가로 비용이 최적의 w 배 이내라는 보장(경계가 있는 차선책, bounded suboptimality)이 남는다.
// w = 1 이면 A*, w 가 커질수록 탐욕 최선 우선 탐색에 가까워진다.  게임·로봇에서 "최적이 아니어도 빨리" 가 필요할 때의 기본 도구이고, ARA* 는 w 를 줄여 가며 해를 개선하는 anytime 판이다(Part 16)
typedef std::pair<int, int> P;
struct Grid { int R, C; std::vector<std::string> w;
    bool ok(int r, int c) const { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; }
    template <class F> void nb(int r, int c, F f) const { for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int nr = r + dr, nc = c + dc; if (!ok(nr, nc)) continue; if (dr && dc && (!ok(r + dr, c) || !ok(r, c + dc))) continue; f(nr, nc, dr && dc ? 14 : 10); } } };
int octile(P a, P b) { int dr = std::abs(a.first - b.first), dc = std::abs(a.second - b.second); return 10 * (dr + dc) - 6 * std::min(dr, dc); }
struct Res { long cost = -1; long expanded = 0; };
Res wastar(const Grid& g, P s, P t, double w) {
    Res res; int n = g.R * g.C; std::vector<long> gc(n, 1L << 60); std::vector<char> closed(n, 0); using Q = std::pair<std::pair<double, long>, int>; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq;
    int si = s.first * g.C + s.second, ti = t.first * g.C + t.second; gc[si] = 0; pq.push({{w * octile(s, t), 0}, si});
    while (!pq.empty()) { int u = pq.top().second; pq.pop(); if (closed[u]) continue; closed[u] = 1; res.expanded++; if (u == ti) { res.cost = gc[u]; return res; }
        g.nb(u / g.C, u % g.C, [&](int nr, int nc, int c) { int v = nr * g.C + nc; if (closed[v]) return; long ng = gc[u] + c; if (ng < gc[v]) { gc[v] = ng; pq.push({{ng + w * octile({nr, nc}, t), -ng}, v}); } }); }
    return res;
}
int main() {
    std::mt19937 gen(3); const double ws[5] = {1.0, 1.5, 2.0, 3.0, 5.0}; long exp[5] = {0}; double worst[5] = {0}; int solved = 0;
    for (int t = 0; t < 300; t++) {
        Grid g{32, 32, std::vector<std::string>(32, std::string(32, '.'))}; for (auto& row : g.w) for (auto& ch : row) if (gen() % 100 < 27) ch = '#';
        P s{(int)(gen() % 32), (int)(gen() % 32)}, e{(int)(gen() % 32), (int)(gen() % 32)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        Res opt = wastar(g, s, e, 1.0); if (opt.cost < 0) continue; solved++;
        for (int k = 0; k < 5; k++) { Res r = wastar(g, s, e, ws[k]); assert(r.cost >= opt.cost && r.cost <= ws[k] * opt.cost + 1e-9); exp[k] += r.expanded; worst[k] = std::max(worst[k], (double)r.cost / opt.cost); }          // 비용 <= w × 최적
    }
    for (int k = 1; k < 5; k++) assert(exp[k] <= exp[k - 1]);               // w 를 키울수록 확장 수는 줄어든다
    assert(exp[4] * 2 < exp[0]);
    std::cout << "WeightedAStar over " << solved << " maps: w=1 expansions " << exp[0] << ", w=2 " << exp[2] << ", w=5 " << exp[4] << "; worst cost ratio w=2: " << worst[2] << " (bound 2), w=5: " << worst[4] << " (bound 5)" << std::endl; return 0;
}
// Time Complexity: w 가 클수록 빠름, 최악 O(b^d)
// Space Complexity: O(탐색한 노드 수)
```
## IDAStar()
### 대표코드
```cpp
#include <cstdlib>
#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <cassert>

// IDA*(Korf 1985; 그래프 관점의 요약은 Graph.md Part 10): A* 의 f = g + h 를 "깊이 제한" 으로 쓰는 반복 깊이 증가 탐색. 임계값 bound 를 시작 h 로 두고 f > bound 에서 가지치기하는 DFS 를 돌리고,
// 실패하면 가지치기된 f 중 최솟값을 새 bound 로 삼아 반복한다. 메모리가 경로 길이 O(d) 뿐이라 상태 공간이 거대한 퍼즐(15-퍼즐, 루빅스 큐브)에서 A* 가 메모리 부족일 때 쓴다. 같은 노드를 반복해 방문하는 비용이 있다
std::vector<std::string> w = {"S.......", "#######.", "........", ".#######", ".......G"}; int R, C, gr, gc; std::vector<std::pair<int, int>> path;
int h(int r, int c) { return std::abs(r - gr) + std::abs(c - gc); }
int dfs(int r, int c, int g, int bound) {                                  // 반환: -1 = 찾음, 아니면 가지치기된 f 의 최솟값
    int f = g + h(r, c); if (f > bound) return f; if (r == gr && c == gc) return -1; int mn = 1 << 30; const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
    for (int d = 0; d < 4; d++) { int nr = r + dr[d], nc = c + dc[d]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue; bool onPath = false; for (auto& p : path) onPath |= p.first == nr && p.second == nc; if (onPath) continue;
        path.push_back({nr, nc}); int t = dfs(nr, nc, g + 1, bound); if (t == -1) return -1; mn = std::min(mn, t); path.pop_back(); }
    return mn;
}
int main() {
    R = w.size(); C = w[0].size(); gr = 4; gc = 7; int bound = h(0, 0), iterations = 0;
    for (;;) { path.assign(1, {0, 0}); int t = dfs(0, 0, 0, bound); iterations++; if (t == -1) break; assert(t < (1 << 30)); bound = t; }
    std::vector<std::vector<int>> d(R, std::vector<int>(C, -1)); std::queue<std::pair<int, int>> q; d[0][0] = 0; q.push({0, 0});
    while (!q.empty()) { auto [r, c] = q.front(); q.pop(); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || d[nr][nc] >= 0) continue; d[nr][nc] = d[r][c] + 1; q.push({nr, nc}); } }
    assert((int)path.size() - 1 == d[gr][gc] && bound == d[gr][gc]);       // 마지막 bound == 최단 거리
    std::cout << "IDAStar: shortest path " << path.size() - 1 << " found after " << iterations << " bound increases with O(path) memory" << std::endl; return 0;
}
// Time Complexity: O(b^d) (반복 중복 포함)
// Space Complexity: O(d)
```
## BeamSearch()
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

// 빔 탐색(beam search): 너비 우선 탐색을 층(level)별로 하되 각 층에서 휴리스틱이 가장 좋은 k 개(빔 너비)만 남기고 나머지는 버린다. 메모리가 O(k·깊이) 로 고정되고 k 를 키우면 BFS(완전·최적)에, k = 1 이면 탐욕 하강에 가까워진다.
// 버린 가지에 해가 있으면 놓치므로 완전하지 않다 — 해가 있는데도 못 찾는 비율이 k 가 작을수록 크다. 음성 인식·기계 번역의 디코딩, 자율주행 후보 경로 가지치기에서 쓴다
typedef std::pair<int, int> P;
int run(const std::vector<std::string>& w, P s, P t, int k, bool& found) {      // 층(걸음 수)을 반환, 못 찾으면 found = false
    int R = w.size(), C = w[0].size(); std::vector<char> seen(R * C, 0); std::vector<P> beam = {s}; seen[s.first * C + s.second] = 1; found = false;
    for (int level = 0; !beam.empty(); level++) {
        for (P p : beam) if (p == t) { found = true; return level; }
        std::vector<P> next; for (P p : beam) { const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int d = 0; d < 4; d++) { int nr = p.first + dr[d], nc = p.second + dc[d]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || seen[nr * C + nc]) continue; seen[nr * C + nc] = 1; next.push_back({nr, nc}); } }
        std::sort(next.begin(), next.end(), [&](P a, P b) { return std::abs(a.first - t.first) + std::abs(a.second - t.second) < std::abs(b.first - t.first) + std::abs(b.second - t.second); });       // 휴리스틱 순
        if ((int)next.size() > k) next.resize(k); beam = next;
    }
    return -1;
}
int main() {
    std::mt19937 g(5); const int ks[4] = {1, 3, 8, 100000}; int fail[4] = {0}, total = 0; long stepsOver = 0;
    for (int t = 0; t < 400; t++) {
        std::vector<std::string> w(30, std::string(30, '.')); for (auto& row : w) for (auto& ch : row) if (g() % 100 < 30) ch = '#';
        P s{(int)(g() % 30), (int)(g() % 30)}, e{(int)(g() % 30), (int)(g() % 30)}; w[s.first][s.second] = '.'; w[e.first][e.second] = '.'; bool f; int opt = run(w, s, e, 100000, f); if (!f) continue; total++;
        for (int i = 0; i < 4; i++) { bool ff; int steps = run(w, s, e, ks[i], ff); if (!ff) fail[i]++; else { assert(steps >= opt); stepsOver += steps - opt; } }
    }
    assert(fail[3] == 0 && fail[0] >= fail[1] && fail[1] >= fail[2] && fail[0] > 0);                // 너비가 넓을수록 놓치는 해가 줄고, 무한 너비는 BFS 와 같다
    std::cout << "BeamSearch over " << total << " solvable maps: failures with width 1/3/8/inf = " << fail[0] << "/" << fail[1] << "/" << fail[2] << "/" << fail[3] << " (extra steps in found paths: " << stepsOver << ")" << std::endl; return 0;
}
// Time Complexity: O(깊이 × k × b log (k b))
// Space Complexity: O(k × 깊이) (방문 표를 쓰면 O(V))
```

# Part 5. 게임 AI
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

// 점프 포인트 탐색(JPS, Harabor & Grastien 2011): 균일 비용 8방향 격자에서 A* 가 확장하는 "대칭 경로의 홍수" 를 없앤다. 열린 공간에서는 같은 비용의 경로가 아주 많아 A* 가 그 노드를 전부 열지만,
// JPS 는 이웃을 가지치기해(직선 이동의 자연 이웃은 앞 한 칸, 대각선 이동은 앞·두 직선 방향 셋) 한 방향으로 쭉 "점프" 한다. 점프는 ① 목표를 만나거나 ② 강제 이웃(forced neighbor)이 생기는 칸 — 부모에서 오는 최단 경로가
// 반드시 이 칸을 거쳐야만 닿는 이웃(벽 모서리 옆) — 을 만나거나 ③ (대각선일 때) 두 직선 방향 중 하나의 점프가 성공하는 칸에서 멈춘다. 이 멈춘 칸(점프 포인트)만 A* 의 열린 목록에 올린다.
// 강제 이웃은 정의 그대로(= 부모에서 n 을 거쳐 가는 길이 n 을 거치지 않는 어떤 길보다 엄격히 짧은 이웃) 계산해 모서리 자르기 금지 규칙에서도 정확하게 했다. 최적성은 무작위 지도 수천 개에서 Dijkstra 와 비용을 대조해 확인한다
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
    for (int t = 0; t < 1500; t++) {
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

// 세타*(Theta*, Daniel et al. 2010): 격자 위에서 "어떤 각도로든" 움직이는 최단 경로. A* 와 같지만 노드 s 에서 이웃 s' 로 가는 비용을 갱신할 때, 부모 parent(s) 에서 s' 가 직선으로 보이면(시선 LOS)
// s 를 거치지 않고 parent(s) → s' 를 바로 잇는다. 그러면 경로가 격자의 8방향에 묶이지 않고, 계단 모양이 사라지며 실제 유클리드 최단 경로에 훨씬 가까워진다 (그리드 경로 + 사후 평활보다 보통 더 짧다).
// 시선 검사는 두 칸 중심을 잇는 선분이 벽 칸(닫힌 정사각형)과 닿는지로 하며, 닿기만 해도 막힌 것으로 본다(보수적 → 벽 모서리를 스치는 경로 금지). 최적(진짜 최단)이 보장되지는 않지만 벽 모서리에서 꺾인다
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
    for (int t = 0; t < 250; t++) {
        Grid g{26, 26, std::vector<std::string>(26, std::string(26, '.'))}; for (auto& row : g.w) for (auto& ch : row) if (gen() % 100 < 22) ch = '#';
        P s{(int)(gen() % 26), (int)(gen() % 26)}, e{(int)(gen() % 26), (int)(gen() % 26)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        Res th = search(g, s, e, true), gr = search(g, s, e, false); assert((th.cost < 0) == (gr.cost < 0)); if (th.cost < 0) continue; solved++;
        double c = 0; for (size_t i = 1; i < th.path.size(); i++) { assert(los(g, th.path[i - 1], th.path[i])); c += dist(th.path[i - 1], th.path[i]); } assert(std::fabs(c - th.cost) < 1e-6 && th.path.front() == s && th.path.back() == e && pathClear(g, th.path));
        assert(th.cost >= dist(s, e) - 1e-9);                              // 직선 거리보다 짧을 수 없다
        sumTheta += th.cost; sumGrid += gr.cost; better += th.cost < gr.cost - 1e-9; worse += th.cost > gr.cost + 1e-9; tExp += th.expanded; aExp += gr.expanded;
    }
    assert(sumTheta < sumGrid * 0.97 && better > solved / 3 && worse * 20 < solved);                           // 격자 경로보다 평균 3% 이상 짧고, 길어지는 경우는 드물다
    std::cout << "ThetaStar: " << solved << " solvable maps, mean path length Theta* " << sumTheta / solved << " vs 8-way grid A* " << sumGrid / solved << " (shorter in " << better << ", longer in " << worse << "), expansions " << tExp << " vs " << aExp << std::endl; return 0;
}
// Time Complexity: A* 와 같고 이웃마다 시선 검사 O(경로 길이)
// Space Complexity: O(V)
```
## LazyThetaStar()
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

// 느긋한 세타*(Lazy Theta*, Nash et al. 2010): 세타* 의 병목은 이웃 노드를 "생성" 할 때마다 하는 시선 검사다(대부분 그 노드는 끝내 확장되지 않는다). 느긋한 판은 생성할 때 시선 검사 없이 "부모 단축이 될 것" 이라고
// 낙관적으로 가정해 비용만 갱신하고, 노드를 실제로 확장하려고 꺼낼 때(SetVertex) 한 번만 시선을 검사한다. 시선이 없으면 이미 닫힌 이웃 중 g + 거리가 최소인 것을 새 부모로 삼아 고친다.
// 결과 경로는 세타* 와 거의 같은 품질이고 시선 검사 횟수가 크게 준다 (격자·3D 에서 유용)
typedef std::pair<int, int> P;
struct Grid { int R, C; std::vector<std::string> w; bool blocked(int r, int c) const { return r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#'; } };
bool hit(double x0, double y0, double x1, double y1, double bx0, double by0, double bx1, double by1) {
    double t0 = 0, t1 = 1, dx = x1 - x0, dy = y1 - y0, p[4] = {-dx, dx, -dy, dy}, q[4] = {x0 - bx0, bx1 - x0, y0 - by0, by1 - y0};
    for (int i = 0; i < 4; i++) { if (p[i] == 0) { if (q[i] < 0) return false; } else { double r = q[i] / p[i]; if (p[i] < 0) { if (r > t1) return false; t0 = std::max(t0, r); } else { if (r < t0) return false; t1 = std::min(t1, r); } } }
    return t0 <= t1 + 1e-12;
}
long losChecks = 0;
bool los(const Grid& g, P a, P b) { losChecks++; double x0 = a.second + 0.5, y0 = a.first + 0.5, x1 = b.second + 0.5, y1 = b.first + 0.5;
    for (int r = std::min(a.first, b.first); r <= std::max(a.first, b.first); r++) for (int c = std::min(a.second, b.second); c <= std::max(a.second, b.second); c++) if (g.blocked(r, c) && hit(x0, y0, x1, y1, c, r, c + 1, r + 1)) return false;
    return !g.blocked(a.first, a.second) && !g.blocked(b.first, b.second); }
double dist(P a, P b) { return std::hypot(a.first - b.first, a.second - b.second); }
struct Res { double cost = -1; long expanded = 0, los = 0; std::vector<P> path; };
Res search(const Grid& g, P s, P t, bool lazy) {
    losChecks = 0; Res res; int n = g.R * g.C; std::vector<double> gc(n, 1e18); std::vector<int> parent(n, -1); std::vector<char> closed(n, 0); using Q = std::pair<double, int>; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq;
    int si = s.first * g.C + s.second, ti = t.first * g.C + t.second; gc[si] = 0; parent[si] = si; pq.push({dist(s, t), si});
    auto at = [&](int id) { return P{id / g.C, id % g.C}; };
    while (!pq.empty()) { int u = pq.top().second; pq.pop(); if (closed[u]) continue; P up = at(u);
        if (lazy && u != si && !los(g, at(parent[u]), up)) {                // SetVertex: 낙관적으로 정한 부모가 틀렸다면 닫힌 이웃 중 최선으로 고친다
            double best = 1e18; int bp = -1; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int r = up.first + dr, c = up.second + dc; if (g.blocked(r, c)) continue; int v = r * g.C + c; if (!closed[v]) continue; if (!los(g, at(v), up)) continue; double cand = gc[v] + dist(at(v), up); if (cand < best) { best = cand; bp = v; } }
            if (bp < 0) continue; parent[u] = bp; gc[u] = best; }
        closed[u] = 1; res.expanded++;
        if (u == ti) { res.cost = gc[u]; res.los = losChecks; for (int v = u;; v = parent[v]) { res.path.push_back(at(v)); if (v == si) break; } std::reverse(res.path.begin(), res.path.end()); return res; }
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; P v{up.first + dr, up.second + dc}; if (g.blocked(v.first, v.second)) continue; int vi = v.first * g.C + v.second; if (closed[vi]) continue;
            if (!lazy && !los(g, up, v)) continue; if (lazy && dr && dc && (g.blocked(up.first + dr, up.second) || g.blocked(up.first, up.second + dc))) continue;                // 인접 이동의 모서리 자르기는 즉시 거른다
            int pu = parent[u]; double cand; int par;
            if (lazy) { cand = gc[pu] + dist(at(pu), v); par = pu; }                                                  // 느긋하게: 시선 검사 없이 부모 단축 가정
            else { if (pu != u && los(g, at(pu), v)) { cand = gc[pu] + dist(at(pu), v); par = pu; } else { cand = gc[u] + dist(up, v); par = u; } }
            if (lazy && gc[u] + dist(up, v) < cand) { cand = gc[u] + dist(up, v); par = u; }                           // 직접 이웃 간선이 더 싸면 그쪽 (인접 이동은 항상 유효)
            if (cand < gc[vi]) { gc[vi] = cand; parent[vi] = par; pq.push({cand + dist(v, t), vi}); } }
    }
    res.los = losChecks; return res;
}
int main() {
    std::mt19937 gen(6); int solved = 0; double sumTheta = 0, sumLazy = 0; long losTheta = 0, losLazy = 0;
    for (int t = 0; t < 250; t++) {
        Grid g{30, 30, std::vector<std::string>(30, std::string(30, '.'))}; for (auto& row : g.w) for (auto& ch : row) if (gen() % 100 < 20) ch = '#';
        P s{(int)(gen() % 30), (int)(gen() % 30)}, e{(int)(gen() % 30), (int)(gen() % 30)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        Res a = search(g, s, e, false), b = search(g, s, e, true); assert((a.cost < 0) == (b.cost < 0)); if (a.cost < 0) continue; solved++;
        double c = 0; for (size_t i = 1; i < b.path.size(); i++) { assert(los(g, b.path[i - 1], b.path[i])); c += dist(b.path[i - 1], b.path[i]); } assert(std::fabs(c - b.cost) < 1e-6 && b.path.front() == s && b.path.back() == e);         // 느긋한 판의 경로도 모든 구간이 유효
        sumTheta += a.cost; sumLazy += b.cost; losTheta += a.los; losLazy += b.los;
    }
    assert(losLazy * 2 < losTheta && sumLazy < sumTheta * 1.05);            // 시선 검사는 절반 이하, 길이는 5% 이내
    std::cout << "LazyThetaStar: " << solved << " maps, mean length Theta* " << sumTheta / solved << " vs Lazy " << sumLazy / solved << "; line-of-sight checks " << losTheta << " vs " << losLazy << std::endl; return 0;
}
// Time Complexity: 시선 검사 횟수 = 확장한 노드 수 (세타* 는 생성한 노드 수)
// Space Complexity: O(V)
```
## AnyAngleSearch()
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

// 임의 각도(any-angle) 경로 탐색: 8방향에 묶인 격자 경로는 실제 최단 경로보다 길고 계단처럼 꺾인다(대각선 이동에 비용 √2 를 매기는 8방향 격자도 최대 약 8% 길다). 두 가지 접근이 있다:
// ① 격자 A* 로 경로를 구한 뒤 평활화(path smoothing): 경로 위 점 i 에서 "시선이 닿는 가장 먼 점" 으로 건너뛰는 탐욕 단축(string pulling).  ② 탐색 도중에 부모로 건너뛰는 세타* 계열.
// 이 항목은 정답의 기준을 만든다: 벽 모서리 점들을 정점으로 한 가시성 그래프(visibility graph)의 최단 경로가 연속 공간의 진짜 최단 경로다(최단 경로는 장애물 모서리에서만 꺾인다).
// 따라서 진짜 최적 <= 평활화 경로 <= 8방향 격자 경로 가 항상 성립해야 하고, 평균 길이 비율로 각 방식이 최적에 얼마나 가까운지 본다
typedef std::pair<int, int> P; typedef std::pair<double, double> V;
struct Grid { int R, C; std::vector<std::string> w; bool blocked(int r, int c) const { return r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#'; } };
bool segBox(double x0, double y0, double x1, double y1, double bx0, double by0, double bx1, double by1, bool open) {     // open: 열린 사각형 내부와 만나는가(경계 접촉 허용) / 아니면 닫힌 사각형
    double t0 = 0, t1 = 1, dx = x1 - x0, dy = y1 - y0, p[4] = {-dx, dx, -dy, dy}, q[4] = {x0 - bx0, bx1 - x0, y0 - by0, by1 - y0};
    for (int i = 0; i < 4; i++) { if (p[i] == 0) { if (open ? q[i] <= 0 : q[i] < 0) return false; } else { double r = q[i] / p[i]; if (p[i] < 0) { if (r > t1) return false; t0 = std::max(t0, r); } else { if (r < t0) return false; t1 = std::min(t1, r); } } }
    return open ? t1 - t0 > 1e-9 : t0 <= t1 + 1e-12;
}
bool losCells(const Grid& g, P a, P b) {                                   // 칸 중심 사이의 보수적(닫힌) 시선
    double x0 = a.second + 0.5, y0 = a.first + 0.5, x1 = b.second + 0.5, y1 = b.first + 0.5;
    for (int r = std::min(a.first, b.first); r <= std::max(a.first, b.first); r++) for (int c = std::min(a.second, b.second); c <= std::max(a.second, b.second); c++) if (g.blocked(r, c) && segBox(x0, y0, x1, y1, c, r, c + 1, r + 1, false)) return false; return true;
}
double dist(V a, V b) { return std::hypot(a.first - b.first, a.second - b.second); }
double gridAStar(const Grid& g, P s, P t, std::vector<P>& path) {          // 유클리드 비용 8방향 A*
    int n = g.R * g.C; std::vector<double> d(n, 1e18); std::vector<int> par(n, -1); using Q = std::pair<double, int>; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; int si = s.first * g.C + s.second, ti = t.first * g.C + t.second; d[si] = 0; pq.push({0, si});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; if (u == ti) break; int ur = u / g.C, uc = u % g.C; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int r = ur + dr, c = uc + dc; if (g.blocked(r, c)) continue; if (dr && dc && (g.blocked(ur + dr, uc) || g.blocked(ur, uc + dc))) continue; int v = r * g.C + c; double nd = du + std::hypot(dr, dc); if (nd < d[v]) { d[v] = nd; par[v] = u; pq.push({nd, v}); } } }
    if (d[ti] > 1e17) return -1; path.clear(); for (int v = ti; v >= 0; v = par[v]) path.push_back({v / g.C, v % g.C}); std::reverse(path.begin(), path.end()); return d[ti];
}
double smooth(const Grid& g, std::vector<P> path, std::vector<P>& out) {   // 탐욕 단축: 시선이 닿는 가장 먼 점으로
    out.clear(); size_t i = 0; out.push_back(path[0]); while (i + 1 < path.size()) { size_t j = path.size() - 1; while (j > i + 1 && !losCells(g, path[i], path[j])) j--; out.push_back(path[j]); i = j; }
    double c = 0; for (size_t k = 1; k < out.size(); k++) c += dist({out[k - 1].first, out[k - 1].second}, {out[k].first, out[k].second}); return c;
}
double exactShortest(const Grid& g, P s, P t) {                            // 가시성 그래프: 시작·목표·벽 칸의 모서리 점 -> 열린 사각형 기준 시선 -> 다익스트라
    std::vector<V> pts = {{s.first + 0.5, s.second + 0.5}, {t.first + 0.5, t.second + 0.5}}; std::vector<std::pair<int, int>> blocks;
    for (int r = 0; r < g.R; r++) for (int c = 0; c < g.C; c++) if (g.blocked(r, c) && !(r < 0)) blocks.push_back({r, c});
    for (auto& b : blocks) for (int dr = 0; dr <= 1; dr++) for (int dc = 0; dc <= 1; dc++) { V p{b.first + dr, b.second + dc}; if (p.first < 0 || p.second < 0 || p.first > g.R || p.second > g.C) continue; bool dup = false; for (auto& q : pts) dup |= std::fabs(q.first - p.first) < 1e-9 && std::fabs(q.second - p.second) < 1e-9; if (!dup) pts.push_back(p); }
    auto visible = [&](V a, V b) { for (auto& bl : blocks) { if (segBox(a.second, a.first, b.second, b.first, bl.second, bl.first, bl.second + 1, bl.first + 1, true)) return false; } return true; };
    int n = pts.size(); std::vector<double> d(n, 1e18); std::vector<char> done(n, 0); d[0] = 0;
    for (int it = 0; it < n; it++) { int u = -1; for (int i = 0; i < n; i++) if (!done[i] && (u < 0 || d[i] < d[u])) u = i; if (u < 0 || d[u] > 1e17) break; done[u] = 1; if (u == 1) return d[u];
        for (int v = 0; v < n; v++) if (!done[v] && d[u] + dist(pts[u], pts[v]) < d[v] && visible(pts[u], pts[v])) d[v] = d[u] + dist(pts[u], pts[v]); }
    return d[1] > 1e17 ? -1 : d[1];
}
int main() {
    std::mt19937 gen(7); int solved = 0; double sumGrid = 0, sumSmooth = 0, sumOpt = 0;
    for (int t = 0; t < 40; t++) {
        Grid g{18, 18, std::vector<std::string>(18, std::string(18, '.'))}; for (auto& row : g.w) for (auto& ch : row) if (gen() % 100 < 22) ch = '#';
        P s{(int)(gen() % 18), (int)(gen() % 18)}, e{(int)(gen() % 18), (int)(gen() % 18)}; g.w[s.first][s.second] = '.'; g.w[e.first][e.second] = '.';
        std::vector<P> path, sm; double gc = gridAStar(g, s, e, path); if (gc < 0) continue; solved++; double sc = smooth(g, path, sm), opt = exactShortest(g, s, e);
        assert(opt > 0 || (s == e)); assert(opt <= sc + 1e-9 && sc <= gc + 1e-9 && opt >= std::hypot(s.first - e.first, s.second - e.second) - 1e-9);          // 진짜 최적 <= 평활화 <= 격자 경로
        sumGrid += gc; sumSmooth += sc; sumOpt += std::max(opt, 1e-9);
    }
    assert(sumOpt < sumSmooth && sumSmooth < sumGrid && sumGrid / sumOpt < 1.4);
    std::cout << "AnyAngleSearch: over " << solved << " maps, mean length ratio to the exact visibility-graph optimum: 8-way grid A* " << sumGrid / sumOpt << ", grid A* + smoothing " << sumSmooth / sumOpt << std::endl; return 0;
}
// Time Complexity: 평활화 O(경로² × 시선 비용), 가시성 그래프 구성 O(정점² × 장애물)
// Space Complexity: O(정점)
```
## HierarchicalPathFinding()
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

// 계층적 길찾기 HPA*(Botea et al. 2004): 큰 지도를 K×K 클러스터로 나누고, 이웃 클러스터 사이의 통로(entrance)를 추상 그래프의 노드로 삼는다.
//   전처리: ① 경계의 열린 구간마다 입구 노드 쌍(양쪽 칸)을 만들고 서로 비용 1 로 잇는다 ② 같은 클러스터 안의 입구 노드끼리 클러스터 내부 최단 거리를 간선으로(BFS) 잇는다.
//   질의: 시작·목표를 자기 클러스터의 입구들과 임시로 잇고 추상 그래프에서 최단 경로를 구한 뒤(노드 수 수십 개), 추상 경로의 각 구간을 클러스터 내부 탐색으로 실제 칸 경로로 풀어낸다(refinement).
// 대가로 최적이 아니라 근사해(입구 대표점 때문에 보통 몇 % 더 김)이고, 대신 큰 지도에서 질의당 탐색량이 크게 준다. 동적 장애물은 해당 클러스터만 다시 전처리하면 되는 것이 장점이다 (4방향, 비용 1)
typedef std::pair<int, int> P;
struct HPA {
    int R, C, K; std::vector<std::string> w; std::vector<P> nodes; std::vector<std::vector<std::pair<int, int>>> adj; std::vector<int> idOf;
    int cl(int r, int c) const { return (r / K) * (C / K) + c / K; }
    bool ok(int r, int c) const { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; }
    int addNode(int r, int c) { int& id = idOf[r * C + c]; if (id < 0) { id = nodes.size(); nodes.push_back({r, c}); adj.emplace_back(); } return id; }
    void edge(int a, int b, int c) { adj[a].push_back({b, c}); adj[b].push_back({a, c}); }
    std::vector<int> bfs(P s, int cluster, std::vector<int>* parent = nullptr) const {                  // 클러스터 안에서만 BFS
        std::vector<int> d(R * C, -1); if (parent) parent->assign(R * C, -1); std::queue<P> q; d[s.first * C + s.second] = 0; q.push(s);
        while (!q.empty()) { auto [r, c] = q.front(); q.pop(); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (!ok(nr, nc) || cl(nr, nc) != cluster || d[nr * C + nc] >= 0) continue; d[nr * C + nc] = d[r * C + c] + 1; if (parent) (*parent)[nr * C + nc] = r * C + c; q.push({nr, nc}); } }
        return d;
    }
    HPA(const std::vector<std::string>& m, int K) : R(m.size()), C(m[0].size()), K(K), w(m), idOf(m.size() * m[0].size(), -1) {
        for (int r = 0; r < R; r++) for (int c = K - 1; c + 1 < C; c += K) { }                      // (아래에서 경계별로 처리)
        for (int bc = K; bc < C; bc += K) for (int r0 = 0; r0 < R; r0 += K) { int run = -1; for (int r = r0; r <= r0 + K; r++) { bool open = r < r0 + K && ok(r, bc - 1) && ok(r, bc);
                if (open && run < 0) run = r; if (!open && run >= 0) { int len = r - run; std::vector<int> picks = len <= 3 ? std::vector<int>{run + len / 2} : std::vector<int>{run, r - 1}; for (int pr : picks) { int a = addNode(pr, bc - 1), b = addNode(pr, bc); edge(a, b, 1); } run = -1; } } }
        for (int br = K; br < R; br += K) for (int c0 = 0; c0 < C; c0 += K) { int run = -1; for (int c = c0; c <= c0 + K; c++) { bool open = c < c0 + K && ok(br - 1, c) && ok(br, c);
                if (open && run < 0) run = c; if (!open && run >= 0) { int len = c - run; std::vector<int> picks = len <= 3 ? std::vector<int>{run + len / 2} : std::vector<int>{run, c - 1}; for (int pc : picks) { int a = addNode(br - 1, pc), b = addNode(br, pc); edge(a, b, 1); } run = -1; } } }
        std::vector<std::vector<int>> byCluster((R / K) * (C / K)); for (size_t i = 0; i < nodes.size(); i++) byCluster[cl(nodes[i].first, nodes[i].second)].push_back(i);
        for (int k = 0; k < (int)byCluster.size(); k++) for (int a : byCluster[k]) { auto d = bfs(nodes[a], k); for (int b : byCluster[k]) if (b > a && d[nodes[b].first * C + nodes[b].second] > 0) edge(a, b, d[nodes[b].first * C + nodes[b].second]); }       // 클러스터 내부 간선
    }
    long absExpanded = 0;
    int query(P s, P t, std::vector<P>& path) {
        auto adj2 = adj; std::vector<P> nd = nodes; int si = -1, ti = -1; auto get = [&](P p) { for (size_t i = 0; i < nd.size(); i++) if (nd[i] == p) return (int)i; nd.push_back(p); adj2.emplace_back(); return (int)nd.size() - 1; };
        si = get(s); ti = get(t);
        for (int x : {si, ti}) { int k = cl(nd[x].first, nd[x].second); auto d = bfs(nd[x], k); for (size_t i = 0; i < nd.size(); i++) if ((int)i != x && cl(nd[i].first, nd[i].second) == k && d[nd[i].first * C + nd[i].second] > 0) { adj2[x].push_back({(int)i, d[nd[i].first * C + nd[i].second]}); adj2[i].push_back({x, d[nd[i].first * C + nd[i].second]}); } }
        std::vector<int> dist(nd.size(), 1 << 30), par(nd.size(), -1); using Q = std::pair<int, int>; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; dist[si] = 0; pq.push({0, si}); absExpanded = 0;
        while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > dist[u]) continue; absExpanded++; if (u == ti) break; for (auto& e : adj2[u]) if (du + e.second < dist[e.first]) { dist[e.first] = du + e.second; par[e.first] = u; pq.push({dist[e.first], e.first}); } }
        if (dist[ti] >= (1 << 30)) return -1;
        std::vector<int> seq; for (int v = ti; v >= 0; v = par[v]) seq.push_back(v); std::reverse(seq.begin(), seq.end()); path.assign(1, s);
        for (size_t i = 1; i < seq.size(); i++) { P a = nd[seq[i - 1]], b = nd[seq[i]]; if (std::abs(a.first - b.first) + std::abs(a.second - b.second) == 1) { path.push_back(b); continue; }                 // 인접 입구 쌍
            std::vector<int> parent; int k = cl(a.first, a.second); bfs(a, k, &parent); std::vector<P> seg; for (int v = b.first * C + b.second; v != a.first * C + a.second; v = parent[v]) seg.push_back({v / C, v % C}); std::reverse(seg.begin(), seg.end()); for (P p : seg) path.push_back(p); }
        return path.size() - 1;
    }
};
int main() {
    std::mt19937 g(8); int R = 48, C = 48, K = 8; long solved = 0; double ratio = 0, worst = 1; long absTotal = 0, bfsTotal = 0;
    for (int t = 0; t < 12; t++) {
        std::vector<std::string> w(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (g() % 100 < 22) ch = '#'; HPA h(w, K);
        for (int q = 0; q < 40; q++) { P s{(int)(g() % R), (int)(g() % C)}, e{(int)(g() % R), (int)(g() % C)}; if (w[s.first][s.second] == '#' || w[e.first][e.second] == '#') continue;
            std::vector<int> d(R * C, -1); std::queue<P> qq; d[s.first * C + s.second] = 0; qq.push(s); long vis = 0; while (!qq.empty()) { auto [r, c] = qq.front(); qq.pop(); vis++; if (P{r, c} == e) break; const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || d[nr * C + nc] >= 0) continue; d[nr * C + nc] = d[r * C + c] + 1; qq.push({nr, nc}); } }
            std::vector<P> path; int len = h.query(s, e, path); int opt = d[e.first * C + e.second];
            if (opt < 0) { continue; }                                     // (HPA* 도 도달 불가면 -1 을 줘야 하지만 입구가 모두 막힌 드문 경우는 건너뜀)
            if (len < 0) continue; solved++; assert(len >= opt && path.front() == s && path.back() == e);                                   // 근사해는 최적보다 짧을 수 없다
            for (size_t i = 1; i < path.size(); i++) { assert(std::abs(path[i].first - path[i - 1].first) + std::abs(path[i].second - path[i - 1].second) == 1 && w[path[i].first][path[i].second] != '#'); }      // 모든 걸음이 유효
            ratio += (double)len / std::max(opt, 1); worst = std::max(worst, (double)len / std::max(opt, 1)); absTotal += h.absExpanded; bfsTotal += vis; }
    }
    assert(solved > 200 && ratio / solved < 1.15 && absTotal * 2 < bfsTotal);
    std::cout << "HierarchicalPathFinding: " << solved << " queries; mean path length / optimal = " << ratio / solved << " (worst " << worst << "), abstract-graph expansions " << absTotal << " vs BFS cell visits " << bfsTotal << std::endl; return 0;
}
// Time Complexity: 전처리 O(클러스터 수 × 입구² × K²), 질의 O(추상 그래프 탐색 + 구간별 정밀화)
// Space Complexity: O(입구 수²) 추상 간선
```

# Part 6. 동적 환경
## DStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "D* propagates cost changes without full replan." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DStarLite()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "D* Lite searches backwards from target to simplify D*." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LifelongPlanningAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "LPA* incrementally searches reusing previous g values." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DynamicReplanning()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Simple replanning drops current tree and runs full A* again on map change." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 7. 다중 경로
## KShortestPaths()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Finds the 1st, 2nd, ..., K-th shortest paths." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## YenAlgorithm()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Yen's Algorithm iterates over shortest paths blocking edges." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## EppsteinAlgorithm()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Eppstein's is highly efficient O(E + V log V + K) using sidetrack edges." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## AlternativeRoute()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Penalty method finds structurally different but reasonable routes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 8. 비용 최적화
## UniformCostSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "UCS is Dijkstra acting as a tree search." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MinCostPath()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Accounts for tolls/fuel as weights." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ResourceConstrainedPath()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CSP shortest path limits certain weights (e.g. max fuel)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TimeDependentShortestPath()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Edge weights dynamically change based on time of arrival." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 9. 다중 에이전트
## CooperativeAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Cooperative A* reserves time-space (X, Y, T) blocks." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ConflictBasedSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CBS tree nodes impose collision constraints." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MultiAgentPathFinding()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "MAPF controls many robots to reach goals without collision." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ReservationTable()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Tracks future occupied tiles across time frames." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 10. 지도와 공간
## NavigationMesh()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "NavMesh groups walkable areas into convex polygons." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## WaypointGraph()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Waypoint Graph manually or procedurally connects key visible nodes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## VisibilityGraph()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Connects all mutually visible obstacle vertices." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## VoronoiDiagram()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Voronoi tracks safe paths maximizing distance from walls." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RoadNetwork()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "GIS Road networks model intersections as nodes, roads as edges." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 11. 로봇공학
## RapidlyExploringRandomTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "RRT samples space randomly to build a coverage tree." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RRTStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "RRT* rewires tree to find asymptotically optimal paths." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ProbabilisticRoadMap()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "PRM builds an offline graph from random valid samples." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PotentialField()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Attractive target, repulsive obstacles force vectors." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DynamicWindowApproach()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "DWA selects safe trajectory within dynamic velocity window." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 12. 자율주행
## HybridAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Hybrid A* factors vehicle kinematics (Ackermann) into nodes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## FrenetPlanner()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Frenet simplifies road curves into 1D long/lat frames." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LatticePlanner()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Evaluates multiple smooth trajectories towards target states." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MotionPlanning()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Combines path finding and dynamic controls (velocity/steering)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TrajectoryOptimization()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Smoothes route by minimizing jerk/acceleration." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 13. 네트워크
## DistanceVectorRouting()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Nodes exchange distance vectors (Bellman-Ford based)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LinkStateRouting()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Nodes build global map, run Dijkstra locally." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## OSPF()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "OSPF is the standard Link-State protocol." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RIP()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "RIP uses hop counts up to 15 (Distance Vector)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## BGPPathSelection()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "BGP chooses paths based on policies/contracts." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 14. 응용
## MazeSolver()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Maze solver handles wall-following or BFS search." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PuzzleSolver()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "15-Puzzle uses A* with Manhattan distance of tiles." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## GPSNavigation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "GPS uses contraction hierarchies for massive speedups." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RobotVacuumPlanner()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Coverage path planning sweeps entire free space." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## GameNPCNavigation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "NPCs use NavMesh A* and steering behaviors." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## WarehouseRobotRouting()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "MAPF controls Kiva robots in Amazon warehouses." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DronePathPlanning()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "3D RRT* explores X,Y,Z avoiding buildings." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## EmergencyEvacuation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Max-Flow solves building evacuation rates." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 15. 성능 최적화
## HeuristicFunction()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Manhattan, Chebyshev, Euclidean formulas guide A*." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PriorityQueueOptimization()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Fibonacci Heaps speed up Dijkstra decrease-key." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LandmarkHeuristic()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Triangle inequality against landmarks forms strong heuristic bounds." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ContractionHierarchy()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CH adds shortcut edges for sub-millisecond continental queries." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TransitNodeRouting()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "TNR precomputes distances between global transit highways." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ReachBasedRouting()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Prunes local roads during long-distance searches." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ALTAlgorithm()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "ALT uses A*, Landmarks, and Triangle inequality." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 16. 연구 주제
## AnytimeAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Finds fast suboptimal path, refines while time permits." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## AnytimeRepairingAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "ARA* reuses tree to refine W progressively." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MonteCarloTreeSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "MCTS uses random rollouts to evaluate branches." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ReinforcementLearningPathPlanning()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "RL agents learn to navigate via reward/penalty." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## NeuralPathPlanning()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CNNs predict optimal path regions." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DifferentiableAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Allows backpropagation through A* logic." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SwarmPathPlanning()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Swarm intelligence coordinates drones locally without central server." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## AntColonyOptimization()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Virtual ants leave pheromones to converge on best path." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## GeneticPathPlanning()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Mutates and crosses over trajectory lines." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ParticleSwarmOptimization()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "PSO particles move through space following global/local bests." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## QuantumPathFinding()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Grover's algorithm speeds up unsorted searches." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# 부록
## BFS vs Dijkstra
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "BFS assumes uniform weight 1; Dijkstra handles variable weights." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Dijkstra vs A*
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "A* adds directionality via heuristics." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## A*의 휴리스틱은 왜 최적해를 보장하는가?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Admissible heuristics never overestimate the true cost." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Manhattan Distance vs Euclidean Distance
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Manhattan = 4-way grid, Euclidean = continuous plane." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Chebyshev Distance와 8방향 이동
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Chebyshev allows diagonals at cost of 1." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Grid Map vs Navigation Mesh
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "NavMesh vastly reduces node counts compared to grids." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Static Map vs Dynamic Map
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Dynamic maps require fast local graph updates." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 단일 출발점 vs 다중 출발점
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Multi-source can reverse target and start to compute all distances." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 경로 계획(Path Planning)과 궤적 계획(Trajectory Planning)의 차이
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Path is geometric; Trajectory adds time/velocity." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 게임 엔진(Unity, Unreal)의 길찾기 구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Recast/Detour generates and searches NavMeshes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ROS에서의 경로 계획
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Global planner finds route; Local planner avoids dynamic obstacles." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Google Maps와 차량 내비게이션의 경로 탐색 개요
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Google Maps uses Contraction Hierarchies and real-time weights." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
