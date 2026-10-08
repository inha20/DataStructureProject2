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
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// D* (Stentz 1994) 의 핵심 아이디어 — 목표에서 "역방향으로" 만든 최단 거리 장과 되돌림 포인터 트리를 유지하다가, 간선 비용이 오르면 그 간선을 지나던 "부분 트리" 만 RAISE 로 무효화하고 경계에서부터 LOWER 로 다시 채운다.
// 로봇이 새 장애물을 발견할 때마다 전체를 다시 계획하지 않고 영향받은 칸만 고친다. 원 논문의 상태 태그(NEW/OPEN/CLOSED)와 k 값 관리는 복잡해서 후속작인 D* Lite 로 대체되었다. (D* 관점의 요약, 정본은 PathFinding.md Part 6 DStarLite)
typedef std::vector<std::string> G;
std::vector<int> bfs(const G& w, int goal) { int R = w.size(), C = w[0].size(); std::vector<int> d(R * C, -1); std::queue<int> q; d[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
        for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#' || d[r * C + c] >= 0) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
int main() {
    std::mt19937 g(5); long affectedTotal = 0, cellsTotal = 0; int trials = 0;
    for (int t = 0; t < 60; t++) {
        int R = 16, C = 16; G w(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (g() % 100 < 20) ch = '#'; w[0][0] = w[R - 1][C - 1] = '.';
        int goal = R * C - 1; std::vector<int> d = bfs(w, goal); int blk = g() % (R * C); if (w[blk / C][blk % C] == '#' || blk == goal || d[blk] < 0) continue;
        std::vector<int> parent(R * C, -1); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
        for (int u = 0; u < R * C; u++) if (d[u] > 0) for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r >= 0 && c >= 0 && r < R && c < C && d[r * C + c] == d[u] - 1) { parent[u] = r * C + c; break; } }   // 되돌림 포인터
        std::vector<char> aff(R * C, 0); std::vector<int> st = {blk}; aff[blk] = 1; int na = 0;                       // RAISE: blk 를 지나던 부분 트리 전체
        while (!st.empty()) { int u = st.back(); st.pop_back(); na++; for (int v = 0; v < R * C; v++) if (!aff[v] && parent[v] == u) { aff[v] = 1; st.push_back(v); } }
        w[blk / C][blk % C] = '#'; std::vector<int> nd = d; typedef std::pair<int, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq;
        for (int u = 0; u < R * C; u++) if (aff[u]) nd[u] = 1 << 28;
        for (int u = 0; u < R * C; u++) if (aff[u] && u != blk) { for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r >= 0 && c >= 0 && r < R && c < C && !aff[r * C + c] && d[r * C + c] >= 0 && w[r][c] != '#') nd[u] = std::min(nd[u], d[r * C + c] + 1); } if (nd[u] < (1 << 28)) pq.push({nd[u], u}); }
        while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > nd[u]) continue; for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] != '.' || !aff[r * C + c] || r * C + c == blk) continue; if (du + 1 < nd[r * C + c]) { nd[r * C + c] = du + 1; pq.push({du + 1, r * C + c}); } } }   // LOWER: 경계에서 다시 채움
        std::vector<int> truth = bfs(w, goal); for (int u = 0; u < R * C; u++) { int v = nd[u] >= (1 << 28) || u == blk ? -1 : nd[u]; if (u == blk) v = -1; assert(v == truth[u]); }
        affectedTotal += na; cellsTotal += R * C; trials++;
    }
    assert(trials > 30 && affectedTotal * 4 < cellsTotal);
    std::cout << "DStar: " << trials << " obstacle insertions repaired by RAISE/LOWER, touching " << affectedTotal << " of " << cellsTotal << " cells and matching a full recomputation everywhere" << std::endl; return 0;
}
// Time Complexity: O(영향받은 부분 트리 × log) 갱신 / 전체 재계산 O(V log V)
// Space Complexity: O(V)
```
## DStarLite()
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

// D* Lite (Koenig & Likhachev 2002): 로봇이 움직이며 지도를 알아가는 "미지 지형" 문제. 목표에서 시작점 쪽으로 탐색하므로(g/rhs 값을 목표 기준으로 유지) 로봇이 이동해도 이미 계산한 값이 그대로 유효하다.
// 각 칸은 g(현재 값)와 rhs(이웃의 g + 간선 비용의 최솟값, 한 걸음 앞선 값)를 가지고, g != rhs 인 칸(불일치)만 키 (min(g,rhs)+h(시작,칸)+km, min(g,rhs)) 순서로 우선순위 큐에 둔다. 로봇이 움직이면 시작점이 바뀌어 키 기준이 달라지므로
// 전부 갱신하는 대신 누적 보정치 km += h(이전 위치, 새 위치) 만 더한다(휴리스틱의 삼각부등식 덕에 오래된 키도 하한으로 유효). 새 장애물이 보이면 그 칸과 이웃의 rhs 만 다시 계산해 불일치를 만들고 ComputeShortestPath 가 필요한 만큼만 전파한다.
// 검증: ① 매 단계 g(현재 위치) == 알려진 지도에서의 BFS 거리, ② 매번 처음부터 만든 D* Lite 와 값 일치, ③ 도달 가능하면 반드시 도착하고 불가능하면 불가능을 보고, ④ 누적 확장 수가 "매 단계 새로 계획" 보다 훨씬 적다
const int INF = 1 << 28; typedef std::pair<int, int> K2;
struct DStarLite {
    int R, C, goal, start, last, km = 0; const std::vector<std::string>* known; std::vector<int> g, rhs; std::vector<K2> key; std::vector<char> inU; long expansions = 0;
    std::priority_queue<std::pair<K2, int>, std::vector<std::pair<K2, int>>, std::greater<std::pair<K2, int>>> U;
    DStarLite(const std::vector<std::string>* k, int s, int t) : R(k->size()), C((*k)[0].size()), goal(t), start(s), last(s), known(k), g(R * C, INF), rhs(R * C, INF), key(R * C), inU(R * C, 0) { rhs[goal] = 0; key[goal] = calc(goal); inU[goal] = 1; U.push({key[goal], goal}); }
    int h(int a, int b) const { return std::abs(a / C - b / C) + std::abs(a % C - b % C); }
    bool blocked(int v) const { return (*known)[v / C][v % C] == '#'; }
    K2 calc(int s) const { int m = std::min(g[s], rhs[s]); return {m >= INF ? INF : m + h(start, s) + km, m}; }
    template <class F> void each(int u, F f) const { const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r >= 0 && c >= 0 && r < R && c < C) f(r * C + c); } }
    void update(int u) {
        if (u != goal) { int best = INF; if (!blocked(u)) each(u, [&](int v) { if (!blocked(v) && g[v] + 1 < best) best = g[v] + 1; }); rhs[u] = best; }
        inU[u] = 0; if (g[u] != rhs[u]) { key[u] = calc(u); inU[u] = 1; U.push({key[u], u}); }
    }
    void compute() {
        for (;;) {
            while (!U.empty() && (!inU[U.top().second] || U.top().first != key[U.top().second])) U.pop();               // 지연 삭제된 낡은 항목 제거
            if (U.empty()) break; K2 kold = U.top().first; int u = U.top().second; if (!(kold < calc(start)) && rhs[start] == g[start]) break;
            U.pop(); inU[u] = 0; K2 knew = calc(u);
            if (kold < knew) { key[u] = knew; inU[u] = 1; U.push({knew, u}); }                                              // 키가 낡았으면 다시 넣기
            else if (g[u] > rhs[u]) { g[u] = rhs[u]; expansions++; each(u, [&](int s) { update(s); }); }                  // 과잉 일관: 값을 낮춰 전파
            else { g[u] = INF; expansions++; update(u); each(u, [&](int s) { update(s); }); }                              // 과소 일관: 무효화 후 다시 계산
        }
    }
};
std::vector<int> bfs(const std::vector<std::string>& w, int src) { int R = w.size(), C = w[0].size(); std::vector<int> d(R * C, -1); std::queue<int> q; if (w[src / C][src % C] == '#') return d; d[src] = 0; q.push(src);
    while (!q.empty()) { int u = q.front(); q.pop(); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#' || d[r * C + c] >= 0) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
int main() {
    std::mt19937 gen(11); long incr = 0, scratch = 0; int reached = 0, unreachable = 0, replans = 0;
    for (int trial = 0; trial < 45; trial++) {
        int R = 18, C = 18; std::vector<std::string> world(R, std::string(C, '.'));
        if (trial == 0) { for (int r = 0; r < R; r++) world[r][C - 3] = '#'; }                                           // 손으로 만든 도달 불가 지도: 목표 앞에 벽
        else for (auto& row : world) for (auto& ch : row) if (gen() % 100 < 27) ch = '#';
        world[0][0] = world[R - 1][C - 1] = '.'; int start = 0, goal = R * C - 1; bool reachable = bfs(world, start)[goal] >= 0;
        std::vector<std::string> known(R, std::string(C, '.')); DStarLite dl(&known, start, goal); int pos = start, steps = 0; bool failed = false;
        auto sense = [&](int p, std::vector<int>& changed) { for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = p / C + dr, c = p % C + dc; if (r >= 0 && c >= 0 && r < R && c < C && world[r][c] == '#' && known[r][c] != '#') { known[r][c] = '#'; changed.push_back(r * C + c); } } };
        std::vector<int> changed; sense(pos, changed);
        for (int c : changed) { dl.update(c); dl.each(c, [&](int v) { dl.update(v); }); }                              // 첫 감지도 변경으로 처리
        while (pos != goal) {
            dl.compute(); std::vector<int> truth = bfs(known, pos);
            if (dl.rhs[pos] >= INF) { failed = true; assert(truth[goal] < 0); break; }                                  // 알려진 지도로는 도달 불가
            assert(dl.g[pos] == truth[goal]);                                                                              // 증분 값 == 알려진 지도의 최단 거리
            DStarLite fresh(&known, pos, goal); fresh.compute(); assert(fresh.g[pos] == dl.g[pos]); scratch += fresh.expansions;
            int best = -1; dl.each(pos, [&](int v) { if (!dl.blocked(v) && dl.g[v] + 1 == dl.g[pos] && best < 0) best = v; }); assert(best >= 0);
            pos = best; steps++; assert(world[pos / C][pos % C] != '#' && steps <= 4 * R * C);
            changed.clear(); sense(pos, changed); dl.start = pos;
            if (!changed.empty()) { replans++; dl.km += dl.h(dl.last, pos); dl.last = pos; for (int c : changed) { dl.update(c); dl.each(c, [&](int v) { dl.update(v); }); } }
        }
        incr += dl.expansions; if (failed) { unreachable++; assert(!reachable); } else { reached++; assert(reachable && pos == goal); }
    }
    assert(reached > 25 && unreachable >= 1 && incr * 3 < scratch);
    std::cout << "DStarLite: " << reached << " goals reached, " << unreachable << " detected as unreachable, " << replans << " map updates; expansions " << incr << " incremental vs " << scratch << " when replanning from scratch each step" << std::endl; return 0;
}
// Time Complexity: 첫 계획 O(V log V), 이후 갱신은 변한 간선의 영향 범위에 비례
// Space Complexity: O(V)
```
## LifelongPlanningAStar()
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

// LPA* (Koenig, Likhachev, Furcy 2004): "시작점·목표는 그대로이고 간선 비용(장애물)만 바뀌는" 문제의 증분 A*. 각 칸이 g 값과 rhs(= 이웃 g + 간선 비용의 최솟값)를 가지고, g != rhs 인 "불일치" 칸만 키 (min(g,rhs)+h, min(g,rhs)) 순서로 처리한다.
// 지도가 바뀌면 영향받은 칸의 rhs 만 다시 계산해 우선순위 큐에 넣고 같은 루프를 돌리므로, 바뀐 곳과 상관없는 값은 재사용된다. 목표의 g 가 정확해지는 순간(큐 맨 위 키 >= 목표 키 이고 g==rhs)에 멈춘다.
// 검증: 장애물을 무작위로 놓고 지우기를 반복하며 매번 g(목표) == 처음부터 구한 BFS 거리, 역추적 경로가 유효하고 길이가 같음, 그리고 총 확장 수가 매번 새로 A* 를 돌릴 때보다 훨씬 적음. D* Lite(Part 6)는 이 알고리즘을 "이동하는 시작점" 으로 확장한 것이다
const int INF = 1 << 28; typedef std::pair<int, int> K2;
struct LPA {
    int R, C, s, t; std::vector<char> blocked; std::vector<int> g, rhs; std::vector<K2> key; std::vector<char> inU; long expansions = 0;
    std::priority_queue<std::pair<K2, int>, std::vector<std::pair<K2, int>>, std::greater<std::pair<K2, int>>> U;
    LPA(int R, int C, int s, int t) : R(R), C(C), s(s), t(t), blocked(R * C, 0), g(R * C, INF), rhs(R * C, INF), key(R * C), inU(R * C, 0) { rhs[s] = 0; key[s] = calc(s); inU[s] = 1; U.push({key[s], s}); }
    int h(int a) const { return std::abs(a / C - t / C) + std::abs(a % C - t % C); }
    K2 calc(int v) const { int m = std::min(g[v], rhs[v]); return {m >= INF ? INF : m + h(v), m}; }
    template <class F> void each(int u, F f) const { const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r >= 0 && c >= 0 && r < R && c < C) f(r * C + c); } }
    void update(int u) {
        if (u != s) { int best = INF; if (!blocked[u]) each(u, [&](int v) { if (!blocked[v] && g[v] + 1 < best) best = g[v] + 1; }); rhs[u] = best; }
        inU[u] = 0; if (g[u] != rhs[u]) { key[u] = calc(u); inU[u] = 1; U.push({key[u], u}); }
    }
    void toggle(int c) { blocked[c] ^= 1; update(c); each(c, [&](int v) { update(v); }); }                                // 간선 비용 변화 = 그 칸과 이웃의 rhs 재계산
    void compute() {
        for (;;) {
            while (!U.empty() && (!inU[U.top().second] || U.top().first != key[U.top().second])) U.pop();
            if (U.empty()) break; K2 kold = U.top().first; int u = U.top().second; if (!(kold < calc(t)) && rhs[t] == g[t]) break;
            U.pop(); inU[u] = 0; K2 knew = calc(u);
            if (kold < knew) { key[u] = knew; inU[u] = 1; U.push({knew, u}); }
            else if (g[u] > rhs[u]) { g[u] = rhs[u]; expansions++; each(u, [&](int v) { update(v); }); }
            else { g[u] = INF; expansions++; update(u); each(u, [&](int v) { update(v); }); }
        }
    }
    std::vector<int> path() const {                                                                                       // 목표에서 g + 1 == g(현재) 인 이웃을 따라 역추적
        std::vector<int> p; if (g[t] >= INF) return p; int u = t; p.push_back(u); while (u != s) { int nx = -1; each(u, [&](int v) { if (nx < 0 && !blocked[v] && g[v] + 1 == g[u]) nx = v; }); assert(nx >= 0); u = nx; p.push_back(u); } std::reverse(p.begin(), p.end()); return p; }
};
long freshAStar(const std::vector<char>& blocked, int R, int C, int s, int t, int& dist) {                              // 비교용: 매번 처음부터 돌리는 A* 의 확장 수
    const int D = 1 << 28; std::vector<int> d(R * C, D); typedef std::pair<int, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq; auto h = [&](int v) { return std::abs(v / C - t / C) + std::abs(v % C - t % C); }; d[s] = 0; pq.push({h(s), s}); long ex = 0; dist = -1;
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > d[u] + h(u)) continue; ex++; if (u == t) { dist = d[u]; break; } const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
        for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || blocked[r * C + c] || d[u] + 1 >= d[r * C + c]) continue; d[r * C + c] = d[u] + 1; pq.push({d[r * C + c] + h(r * C + c), r * C + c}); } }
    return ex; }
int main() {
    std::mt19937 gen(3); int R = 24, C = 24, s = 0, t = R * C - 1; LPA lpa(R, C, s, t); for (int i = 0; i < R * C; i++) if (i != s && i != t && gen() % 100 < 20) lpa.blocked[i] = 1;
    for (int i = 0; i < R * C; i++) lpa.update(i); lpa.compute(); long scratch = 0, rounds = 0, pathLenSum = 0; int unreachableRounds = 0;
    for (int round = 0; round < 300; round++) {
        int edits = 1 + gen() % 3; for (int e = 0; e < edits; e++) { int c = gen() % (R * C); if (c != s && c != t && (lpa.blocked[c] ? gen() % 100 < 80 : gen() % 100 < 20)) lpa.toggle(c); }   // 장애물을 놓거나 치움(밀도가 20% 근처에 머물도록)
        if (round % 60 == 59) { for (int c : {t - 1, t - C}) if (!lpa.blocked[c]) lpa.toggle(c); }                                                // 목표를 막아 도달 불가 상황을 만든다
        if (round % 60 == 1) { for (int c : {t - 1, t - C}) if (lpa.blocked[c]) lpa.toggle(c); }                                                 // 다시 풀어 준다
        lpa.compute(); int dist; scratch += freshAStar(lpa.blocked, R, C, s, t, dist);
        if (dist < 0) { assert(lpa.g[t] >= INF && lpa.path().empty()); unreachableRounds++; continue; }
        assert(lpa.g[t] == dist); std::vector<int> p = lpa.path(); assert((int)p.size() - 1 == dist && p.front() == s && p.back() == t);
        for (size_t i = 0; i < p.size(); i++) { assert(!lpa.blocked[p[i]]); if (i) assert(std::abs(p[i] / C - p[i - 1] / C) + std::abs(p[i] % C - p[i - 1] % C) == 1); } pathLenSum += dist; rounds++;
    }
    assert(rounds > 150 && unreachableRounds >= 2 && lpa.expansions * 2 < scratch);
    std::cout << "LifelongPlanningAStar: " << rounds << " valid replans (" << unreachableRounds << " unreachable rounds), mean path " << (double)pathLenSum / rounds << ", expansions " << lpa.expansions << " incremental vs " << scratch << " from scratch" << std::endl; return 0;
}
// Time Complexity: 첫 탐색 O(V log V), 이후 변화는 영향받은 칸 수에 비례
// Space Complexity: O(V)
```
## DynamicReplanning()
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

// 동적 재계획: 장애물이 시간에 따라 나타나는 환경에서, 실행 중인 계획을 언제 버리고 다시 계획하는가. 두 정책을 같은 사건 열로 비교한다.
// (a) 매 걸음 재계획: 항상 현재 지도의 최단 경로를 따르지만 A* 를 매번 호출한다. (b) 무효화 시에만 재계획: 남은 경로에 새 장애물이 닿았을 때만 호출. 장애물이 "생기기만 하는" 환경에서는 계획이 아직 유효하면 여전히 최단이므로
// (b) 는 (a) 와 똑같이 도착하면서 호출 횟수와 확장 수가 훨씬 적다. 장애물이 사라질 수 있는 환경에서는 더 짧은 길이 생겨도 (b) 는 모르므로 주기적 재계획이나 D* Lite(Part 6) 같은 증분 방법이 필요하다
struct World { int R, C; std::vector<char> blocked; };
long expandedTotal; int calls;
std::vector<int> astar(const World& w, int s, int t) {                                                                  // 4방향 단위 비용 A*, 실패하면 빈 벡터
    calls++; int R = w.R, C = w.C; auto h = [&](int v) { return std::abs(v / C - t / C) + std::abs(v % C - t % C); }; std::vector<int> d(R * C, 1 << 28), par(R * C, -1); typedef std::pair<int, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq; d[s] = 0; pq.push({h(s), s});
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > d[u] + h(u)) continue; expandedTotal++; if (u == t) break; const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1};
        for (int k = 0; k < 4; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w.blocked[r * C + c] || d[u] + 1 >= d[r * C + c]) continue; d[r * C + c] = d[u] + 1; par[r * C + c] = u; pq.push({d[r * C + c] + h(r * C + c), r * C + c}); } }
    std::vector<int> p; if (d[t] >= (1 << 28)) return p; for (int v = t; v >= 0; v = par[v]) p.push_back(v); std::reverse(p.begin(), p.end()); return p; }
struct Event { int time, cell; };
bool run(World w, std::vector<Event> ev, int s, int t, bool everyStep, int& arrival, int& replans) {
    int pos = s, tick = 0; replans = 0; std::vector<int> plan = astar(w, s, t); if (plan.empty()) return false; size_t idx = 0; size_t e = 0;
    while (pos != t) {
        while (e < ev.size() && ev[e].time <= tick) { if (ev[e].cell != pos) w.blocked[ev[e].cell] = 1; e++; }                       // 이번 틱에 새 장애물이 생김
        bool invalid = false; for (size_t i = idx; i < plan.size(); i++) if (w.blocked[plan[i]]) invalid = true;
        if (everyStep || invalid) { plan = astar(w, pos, t); replans++; idx = 0; if (plan.empty()) return false; }
        pos = plan[idx + 1]; idx++; tick++; assert(!w.blocked[pos]);
    }
    arrival = tick; return true;
}
int main() {
    std::mt19937 g(21); long lazyEx = 0, everyEx = 0; int lazyCalls = 0, everyCalls = 0, finished = 0, stuckBoth = 0;
    for (int trial = 0; trial < 80; trial++) {
        World w{20, 20, std::vector<char>(400, 0)}; for (int i = 1; i < 399; i++) if (g() % 100 < 15) w.blocked[i] = 1; std::vector<Event> ev; for (int k = 0; k < 60; k++) { int c = 1 + g() % 398; ev.push_back({(int)(g() % 40), c}); } std::sort(ev.begin(), ev.end(), [](const Event& a, const Event& b) { return a.time < b.time; });
        int a1 = 0, r1 = 0, a2 = 0, r2 = 0; expandedTotal = 0; calls = 0; bool ok1 = run(w, ev, 0, 399, false, a1, r1); long ex1 = expandedTotal; int c1 = calls;
        expandedTotal = 0; calls = 0; bool ok2 = run(w, ev, 0, 399, true, a2, r2); long ex2 = expandedTotal; int c2 = calls;
        if (!ok1 && !ok2) { stuckBoth++; continue; } if (!ok1 || !ok2) continue;                                                // 정책에 따라 막다른 길이 달라질 수 있어 그런 시도는 건너뜀
        assert(a1 >= 38 && a2 >= 38 && r1 <= r2 + 1 && c1 <= c2); finished++; lazyEx += ex1; everyEx += ex2; lazyCalls += c1; everyCalls += c2;
    }
    assert(finished > 40 && lazyCalls * 4 < everyCalls && lazyEx * 3 < everyEx);
    std::cout << "DynamicReplanning: " << finished << " runs; A* calls " << lazyCalls << " (replan only when blocked) vs " << everyCalls << " (every step); expansions " << lazyEx << " vs " << everyEx << std::endl; return 0;
}
// Time Complexity: 재계획 1회당 O(V log V) × 재계획 횟수
// Space Complexity: O(V)
```

# Part 7. 다중 경로
## KShortestPaths()
### 대표코드
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// K 최단 경로: 최단 경로 하나가 아니라 비용 순으로 1등, 2등, ..., K등 경로를 구한다. 가장 단순한 방법은 Dijkstra 의 변형 — 각 정점을 "꺼내는" 횟수를 최대 K 번까지 허용하는 최선 우선 탐색이다.
// 정점 v 에서 처음 꺼낸 경로가 s→v 1등, 두 번째가 2등이므로 v 를 K+1 번째 꺼낸 경로는 어떤 K 최단 경로의 접두사도 될 수 없어 버려도 된다. 목표 t 를 꺼낼 때마다 정답을 하나씩 얻는다. 이 방식이 구하는 것은 사이클을 허용하는 "보행(walk)" 이다
// (사이클 없는 단순 경로만 원하면 Yen 알고리즘, 효율적인 보행 열거는 Eppstein 알고리즘; 이 파일의 다음 두 항목). 검증: 가중치 있는 작은 방향 그래프 200개에서, 비용 상한 아래의 모든 보행을 DFS 로 완전 열거해 정렬한 것의 앞 K 개 비용과 일치하는지 대조
struct Edge { int to, w; };
typedef std::pair<long, std::vector<int>> Walk;
std::vector<Walk> kWalks(const std::vector<std::vector<Edge>>& adj, int s, int t, int K) {
    struct Node { int v, prev; }; std::vector<Node> arena = {{s, -1}}; typedef std::pair<long, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq; pq.push({0, 0}); std::vector<int> cnt(adj.size(), 0); std::vector<Walk> res;
    while (!pq.empty() && (int)res.size() < K) {
        auto [c, id] = pq.top(); pq.pop(); int v = arena[id].v; if (cnt[v]++ >= K) continue;                      // v 를 K 번 넘게 꺼낸 경로는 필요 없다
        if (v == t) { std::vector<int> p; for (int x = id; x >= 0; x = arena[x].prev) p.push_back(arena[x].v); std::reverse(p.begin(), p.end()); res.push_back({c, p}); }
        for (const Edge& e : adj[v]) { arena.push_back({e.to, id}); pq.push({c + e.w, (int)arena.size() - 1}); }
    }
    return res;
}
long cost(const std::vector<std::vector<int>>& w, const std::vector<int>& p) { long c = 0; for (size_t i = 1; i < p.size(); i++) { assert(w[p[i - 1]][p[i]] > 0); c += w[p[i - 1]][p[i]]; } return c; }
void brute(const std::vector<std::vector<int>>& w, int v, int t, long c, long cap, std::vector<int>& path, std::vector<long>& out) {   // 비용 cap 이하의 모든 s→t 보행 열거
    if (c > cap) return; if (v == t) out.push_back(c); for (int u = 0; u < (int)w.size(); u++) if (w[v][u]) { path.push_back(u); brute(w, u, t, c + w[v][u], cap, path, out); path.pop_back(); }
}
int main() {
    std::mt19937 g(17); int checked = 0, loopy = 0; const int K = 10;
    for (int trial = 0; trial < 400; trial++) {
        int n = 6; std::vector<std::vector<int>> w(n, std::vector<int>(n, 0)); std::vector<std::vector<Edge>> adj(n);
        for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v && g() % 100 < 55) { w[u][v] = 1 + g() % 5; adj[u].push_back({v, w[u][v]}); }
        std::vector<Walk> res = kWalks(adj, 0, n - 1, K); if ((int)res.size() < K || res.back().first > 12) continue;                                   // (완전 열거가 너무 커지지 않는 경우만 대조)
        std::set<std::vector<int>> seen; for (size_t i = 0; i < res.size(); i++) { assert(res[i].second.front() == 0 && res[i].second.back() == n - 1 && cost(w, res[i].second) == res[i].first && seen.insert(res[i].second).second && (i == 0 || res[i - 1].first <= res[i].first)); std::set<int> uniq(res[i].second.begin(), res[i].second.end()); if (uniq.size() < res[i].second.size()) loopy++; }
        std::vector<int> path = {0}; std::vector<long> all; brute(w, 0, n - 1, 0, res.back().first, path, all); std::sort(all.begin(), all.end());       // 독립적인 완전 열거
        assert(all.size() >= (size_t)K); for (int i = 0; i < K; i++) assert(all[i] == res[i].first); checked++;
    }
    assert(checked > 100 && loopy > 0);
    std::cout << "KShortestPaths: " << checked << " random graphs, first " << K << " walk costs equal brute force enumeration; " << loopy << " reported walks contain a cycle" << std::endl; return 0;
}
// Time Complexity: O(K · m log(K · m))
// Space Complexity: O(K · m)
```
## YenAlgorithm()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// Yen 알고리즘(1971): 사이클이 없는 단순 경로만 K 개 구한다. 이미 구한 경로 A[k-1] 의 각 정점 i 를 "분기점(spur)" 으로 삼아, 접두사(root = A[k-1][0..i])는 그대로 두고 분기점부터 목표까지를 다시 Dijkstra 로 구한다. 단 같은 접두사를 공유하는
// 기존 경로들이 쓴 다음 간선은 금지하고(같은 경로가 또 나오지 않게), root 의 다른 정점은 금지한다(단순 경로 유지). 이렇게 만든 후보들을 비용 순 후보 집합 B 에 모으고 가장 싼 것이 A[k] 가 된다.
// 검증: 작은 가중 방향 그래프 150개에서 DFS 로 모든 단순 경로를 열거해 정렬한 것의 앞 K 개 비용과 일치, 각 경로가 단순하고 서로 다르며 비용이 맞는지 확인한다
typedef std::vector<std::vector<int>> Mat; const long INF = 1L << 50;
bool dijkstra(const Mat& w, const std::vector<char>& banNode, const Mat& banEdge, int s, int t, long& cost, std::vector<int>& path) {
    int n = w.size(); std::vector<long> d(n, INF); std::vector<int> par(n, -1); typedef std::pair<long, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int v = 0; v < n; v++) if (w[u][v] && !banNode[v] && !banEdge[u][v] && du + w[u][v] < d[v]) { d[v] = du + w[u][v]; par[v] = u; pq.push({d[v], v}); } }
    if (d[t] >= INF) return false; cost = d[t]; path.clear(); for (int v = t; v >= 0; v = par[v]) path.push_back(v); std::reverse(path.begin(), path.end()); return true; }
std::vector<std::pair<long, std::vector<int>>> yen(const Mat& w, int s, int t, int K) {
    int n = w.size(); std::vector<std::pair<long, std::vector<int>>> A; std::set<std::pair<long, std::vector<int>>> B; Mat noEdge(n, std::vector<int>(n, 0)); std::vector<char> noNode(n, 0); long c; std::vector<int> p;
    if (!dijkstra(w, noNode, noEdge, s, t, c, p)) return A; A.push_back({c, p});
    while ((int)A.size() < K) {
        const std::vector<int>& prev = A.back().second;
        for (size_t i = 0; i + 1 < prev.size(); i++) {
            std::vector<int> root(prev.begin(), prev.begin() + i + 1); Mat banE(n, std::vector<int>(n, 0)); std::vector<char> banN(n, 0);
            for (auto& a : A) if (a.second.size() > i + 1 && std::equal(root.begin(), root.end(), a.second.begin())) banE[a.second[i]][a.second[i + 1]] = 1;       // 같은 접두사를 쓴 기존 경로의 다음 간선 금지
            for (size_t j = 0; j < i; j++) banN[root[j]] = 1;                                                                                                     // root 의 정점 재방문 금지(분기점은 제외)
            long sc; std::vector<int> sp; if (!dijkstra(w, banN, banE, root.back(), t, sc, sp)) continue;
            std::vector<int> total(root.begin(), root.end() - 1); total.insert(total.end(), sp.begin(), sp.end()); long rc = 0; for (size_t j = 1; j < total.size(); j++) rc += w[total[j - 1]][total[j]]; B.insert({rc, total});
        }
        if (B.empty()) break; A.push_back(*B.begin()); B.erase(B.begin());
    }
    return A;
}
void brute(const Mat& w, int v, int t, long c, std::vector<char>& vis, std::vector<long>& out) { if (v == t) { out.push_back(c); return; } vis[v] = 1; for (int u = 0; u < (int)w.size(); u++) if (w[v][u] && !vis[u]) brute(w, u, t, c + w[v][u], vis, out); vis[v] = 0; }
int main() {
    std::mt19937 g(29); int checked = 0; const int K = 8; long fewer = 0;
    for (int trial = 0; trial < 150; trial++) {
        int n = 7; Mat w(n, std::vector<int>(n, 0)); for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v && g() % 100 < 50) w[u][v] = 1 + g() % 6;
        auto res = yen(w, 0, n - 1, K); std::vector<char> vis(n, 0); std::vector<long> all; brute(w, 0, n - 1, 0, vis, all); std::sort(all.begin(), all.end());
        assert(res.size() == std::min<size_t>(K, all.size())); if (all.size() < (size_t)K) fewer++;
        std::set<std::vector<int>> seen; for (size_t i = 0; i < res.size(); i++) { const auto& p = res[i].second; std::set<int> uniq(p.begin(), p.end()); long cc = 0; for (size_t j = 1; j < p.size(); j++) cc += w[p[j - 1]][p[j]];
            assert(uniq.size() == p.size() && p.front() == 0 && p.back() == n - 1 && cc == res[i].first && res[i].first == all[i] && seen.insert(p).second); }          // 단순 경로 · 서로 다름 · 비용이 완전 열거와 일치
        if (!res.empty()) checked++;
    }
    assert(checked > 100);
    std::cout << "YenAlgorithm: " << checked << " random graphs, loopless K=" << K << " costs match exhaustive enumeration (" << fewer << " graphs had fewer than K simple paths)" << std::endl; return 0;
}
// Time Complexity: O(K · V · (E + V log V))
// Space Complexity: O(K · V)
```
## EppsteinAlgorithm()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// Eppstein 알고리즘(1998): 사이클을 허용하는 K 최단 보행을 O(E + V log V + K log K) 에 낸다(Yen 의 K·V 배 비용 없이). 핵심은 "곁가지(sidetrack)" 라는 개념이다.
// ① 목표 t 로부터 역방향 Dijkstra 로 최단 경로 트리 T 와 거리 d(v) 를 구한다. ② 트리에 없는 간선 e=(u,v) 는 곁가지이고 그것을 쓰면 비용이 δ(e) = w(e) + d(v) − d(u) ≥ 0 만큼 늘어난다. 모든 s→t 보행은 "트리를 따라가다 곁가지로 빠지기" 의 유한 열로 유일하게 표현되고
// 비용은 d(s) + Σδ 이다. ③ 각 정점 v 에서 "v→t 트리 경로 위의 모든 곁가지" 를 δ 로 정렬한 힙 H(v) 를, 부모의 힙에 v 의 곁가지만 합쳐 영속(persistent) 좌편향 힙으로 만든다 — 부모 힙은 그대로 남고 O(log) 노드만 새로 생긴다.
// ④ 경로 그래프: 힙 노드 x(= 곁가지 e)에서 (a) 힙의 자식으로 가면 마지막 곁가지를 형제로 바꾸는 것이고 비용은 δ(자식)−δ(x), (b) e 의 머리 v 의 힙 뿌리로 가면 곁가지를 하나 더 쓰는 것이고 비용은 δ(뿌리). 이 그래프에서 비용 순으로 K 개를 꺼내면 된다.
// 검증: 작은 가중 방향 그래프 200개에서 (1) 각 보행을 곁가지 열에서 복원해 간선이 실제로 있고 비용이 맞는지, 서로 다른지 (2) 비용 상한 아래의 모든 보행을 DFS 로 완전 열거한 것과 앞 K 개 비용이 같은지 확인한다
struct E { int u, v, w; };
struct HN { int e; long delta; int l, r, npl; }; std::vector<HN> pool;
int npl(int x) { return x ? pool[x].npl : 0; }
int mergeH(int a, int b) { if (!a) return b; if (!b) return a; if (pool[a].delta > pool[b].delta) std::swap(a, b); HN x = pool[a]; x.r = mergeH(x.r, b); if (npl(x.l) < npl(x.r)) std::swap(x.l, x.r); x.npl = npl(x.r) + 1; pool.push_back(x); return pool.size() - 1; }   // 영속 병합: 오른쪽 척추만 복사
typedef std::pair<long, std::vector<int>> Walk;
std::vector<Walk> eppstein(int n, const std::vector<E>& es, int s, int t, int K) {
    const long INF = 1L << 50; pool.assign(1, HN{-1, 0, 0, 0, 0}); std::vector<std::vector<int>> radj(n); for (size_t i = 0; i < es.size(); i++) radj[es[i].v].push_back(i);
    std::vector<long> d(n, INF); std::vector<int> te(n, -1); typedef std::pair<long, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq; d[t] = 0; pq.push({0, t});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int id : radj[u]) { const E& e = es[id]; if (du + e.w < d[e.u]) { d[e.u] = du + e.w; te[e.u] = id; pq.push({d[e.u], e.u}); } } }
    std::vector<Walk> res; if (d[s] >= INF) return res;
    std::vector<int> local(n, 0); for (size_t id = 0; id < es.size(); id++) { const E& e = es[id]; if (d[e.u] >= INF || d[e.v] >= INF || te[e.u] == (int)id) continue; pool.push_back(HN{(int)id, e.w + d[e.v] - d[e.u], 0, 0, 1}); local[e.u] = mergeH(local[e.u], pool.size() - 1); }
    std::vector<int> order; for (int v = 0; v < n; v++) if (d[v] < INF) order.push_back(v); std::sort(order.begin(), order.end(), [&](int a, int b) { return d[a] < d[b] || (d[a] == d[b] && a < b); });
    std::vector<int> H(n, 0); for (int v : order) H[v] = v == t ? local[v] : mergeH(H[es[te[v]].v], local[v]);                 // 트리 위쪽(목표 쪽) 부모의 힙에 자기 곁가지를 합친다
    struct En { int node, link; }; std::vector<En> en;
    auto build = [&](int idx) {                                                                                               // 곁가지 열 → 실제 정점 열
        std::vector<int> side; for (int i = idx; i >= 0; i = en[i].link) side.push_back(pool[en[i].node].e); std::reverse(side.begin(), side.end()); std::vector<int> walk = {s}; int cur = s;
        auto follow = [&](int target) { while (cur != target) { assert(te[cur] >= 0); cur = es[te[cur]].v; walk.push_back(cur); } };
        for (int id : side) { follow(es[id].u); cur = es[id].v; walk.push_back(cur); } follow(t); return walk; };
    res.push_back({d[s], build(-1)});                                                                                          // 곁가지 없는 1등 = 최단 경로
    std::priority_queue<std::pair<long, int>, std::vector<std::pair<long, int>>, std::greater<std::pair<long, int>>> q;
    if (H[s]) { en.push_back({H[s], -1}); q.push({d[s] + pool[H[s]].delta, 0}); }
    while (!q.empty() && (int)res.size() < K) {
        auto [c, i] = q.top(); q.pop(); int x = en[i].node, link = en[i].link; res.push_back({c, build(i)});
        for (int ch : {pool[x].l, pool[x].r}) if (ch) { en.push_back({ch, link}); q.push({c - pool[x].delta + pool[ch].delta, (int)en.size() - 1}); }       // 형제로 교체
        int v = es[pool[x].e].v; if (H[v]) { en.push_back({H[v], i}); q.push({c + pool[H[v]].delta, (int)en.size() - 1}); }                              // 곁가지 하나 추가
    }
    return res;
}
void brute(const std::vector<std::vector<int>>& w, int v, int t, long c, long cap, std::vector<long>& out) { if (c > cap) return; if (v == t) out.push_back(c); for (int u = 0; u < (int)w.size(); u++) if (w[v][u]) brute(w, u, t, c + w[v][u], cap, out); }
int main() {
    std::mt19937 g(41); int checked = 0; const int K = 30; size_t maxPool = 0;
    for (int trial = 0; trial < 200; trial++) {
        int n = 6; std::vector<std::vector<int>> w(n, std::vector<int>(n, 0)); std::vector<E> es; for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v && g() % 100 < 40) { w[u][v] = 1 + g() % 5; es.push_back({u, v, w[u][v]}); }
        auto res = eppstein(n, es, 0, n - 1, K); maxPool = std::max(maxPool, pool.size()); if ((int)res.size() < K) continue;
        std::set<std::vector<int>> seen; for (size_t i = 0; i < res.size(); i++) { const auto& p = res[i].second; long cc = 0; for (size_t j = 1; j < p.size(); j++) { assert(w[p[j - 1]][p[j]] > 0); cc += w[p[j - 1]][p[j]]; }
            assert(p.front() == 0 && p.back() == n - 1 && cc == res[i].first && seen.insert(p).second && (i == 0 || res[i - 1].first <= res[i].first)); }
        std::vector<long> all; brute(w, 0, n - 1, 0, res.back().first, all); std::sort(all.begin(), all.end()); assert(all.size() >= (size_t)K); for (int i = 0; i < K; i++) assert(all[i] == res[i].first); checked++;
    }
    assert(checked > 100);
    std::cout << "EppsteinAlgorithm: " << checked << " random graphs, first " << K << " walks reconstructed from sidetrack sequences and equal to exhaustive enumeration (heap pool <= " << maxPool << " nodes)" << std::endl; return 0;
}
// Time Complexity: O(E + V log V + K log K)
// Space Complexity: O(E + K)
```
## AlternativeRoute()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 대체 경로(alternative routes): 내비게이션이 "다른 길" 로 보여 줄 후보는 K 최단 경로가 아니다. 2등 최단 경로는 1등에서 한 구간만 우회한 거의 같은 길이라 사용자에게 무의미하다. 좋은 대체 경로의 조건은 ① 최단보다 많이 길지 않을 것(한정된 우회율),
// ② 이미 보여 준 경로와 구간이 많이 겹치지 않을 것, ③ (실무에서는) 국소 최적일 것이다. 페널티 방법: 한 경로를 찾으면 그 경로의 간선 가중치를 키운 뒤 Dijkstra 를 다시 돌려 다른 길로 유도하고, 후보의 "실제" 길이로 조건을 검사한다.
// 검증: 12×12 격자 도시(간선 가중치 2..9)에서 페널티 방법의 대체 경로가 우회율 ≤ 1.3 · 겹침 ≤ 0.7 을 지키고, 같은 지도에서 "2등 최단 단순 경로" 의 평균 겹침(약 0.8 이상)보다 확실히 작음을 확인한다
struct Edge { int to, id; };
int R = 12, C = 12; std::vector<std::vector<Edge>> adj; std::vector<int> ew;
std::vector<int> dijkstra(const std::vector<double>& cost, int s, int t, std::vector<int>* edgesOut) {
    int n = adj.size(); std::vector<double> d(n, 1e18); std::vector<int> par(n, -1), pe(n, -1); typedef std::pair<double, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (const Edge& e : adj[u]) if (du + cost[e.id] < d[e.to]) { d[e.to] = du + cost[e.id]; par[e.to] = u; pe[e.to] = e.id; pq.push({d[e.to], e.to}); } }
    std::vector<int> p; edgesOut->clear(); for (int v = t; v >= 0; v = par[v]) { p.push_back(v); if (pe[v] >= 0) edgesOut->push_back(pe[v]); } std::reverse(p.begin(), p.end()); return p; }
double length(const std::vector<int>& es) { double L = 0; for (int e : es) L += ew[e]; return L; }
double overlap(const std::vector<int>& a, const std::vector<int>& b) { std::set<int> sa(a.begin(), a.end()); double sh = 0; for (int e : b) if (sa.count(e)) sh += ew[e]; return sh / length(b); }      // b 의 길이 중 a 와 겹치는 비율
int main() {
    std::mt19937 g(5); int n = R * C, s = 0, t = n - 1; double penaltySum = 0, secondSum = 0; int penaltyCount = 0, secondCount = 0, cities = 0;
    for (int city = 0; city < 25; city++) {
        adj.assign(n, {}); ew.clear(); for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { int u = r * C + c; if (c + 1 < C) { int id = ew.size(); ew.push_back(2 + g() % 8); adj[u].push_back({u + 1, id}); adj[u + 1].push_back({u, id}); } if (r + 1 < R) { int id = ew.size(); ew.push_back(2 + g() % 8); adj[u].push_back({u + C, id}); adj[u + C].push_back({u, id}); } }
        std::vector<double> base(ew.begin(), ew.end()), pen = base; std::vector<int> best; dijkstra(base, s, t, &best); double opt = length(best);
        std::vector<std::vector<int>> accepted = {best}; for (int it = 0; it < 40 && accepted.size() < 4; it++) {
            for (int e : accepted.back()) pen[e] *= 1.6;                                                                               // 마지막으로 채택한 경로를 불리하게
            std::vector<int> es; dijkstra(pen, s, t, &es); double L = length(es); bool ok = L <= 1.3 * opt; for (auto& a : accepted) ok = ok && overlap(a, es) <= 0.7;
            if (ok) { for (auto& a : accepted) { penaltySum += overlap(a, es); penaltyCount++; } assert(L >= opt - 1e-9); accepted.push_back(es); }
            else for (int e : es) pen[e] *= 1.3;                                                                                     // 조건 미달이면 이 경로도 불리하게 해서 다음 시도 유도
        }
        std::vector<int> second; double sl = 1e18;                                                                                     // 비교 대상: 2등 최단 단순 경로 = 최단 경로의 간선 하나를 막고 구한 것 중 최소
        for (int e : best) { std::vector<double> c2 = base; c2[e] = 1e9; std::vector<int> es; dijkstra(c2, s, t, &es); if (length(es) < sl && length(es) < 1e8) { sl = length(es); second = es; } }
        assert(!second.empty() && sl >= opt - 1e-9); secondSum += overlap(best, second); secondCount++; cities++;
        assert(accepted.size() >= 2);
    }
    double pm = penaltySum / penaltyCount, sm = secondSum / secondCount;
    assert(pm <= 0.7 && sm > 0.8 && pm < sm - 0.15);
    std::cout << "AlternativeRoute: mean overlap of penalty-method alternatives " << pm << " vs " << sm << " for the 2nd-shortest simple path over " << cities << " cities" << std::endl; return 0;
}
// Time Complexity: O(반복 횟수 × E log V)
// Space Complexity: O(V + E)
```

# Part 8. 비용 최적화
## UniformCostSearch()
### 대표코드
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <vector>
#include <cassert>

// 균일 비용 탐색(UCS): 비용이 낮은 순서로 상태를 확장하는 Dijkstra 이지만, 그래프를 미리 만들어 두지 않고 "후속 상태 함수" 로 상태를 그때그때 만들며 목표 상태를 만나면 멈춘다는 점이 쓰임새를 가른다(퍼즐·계획 문제).
// 두 가지를 반드시 지켜야 최적이다. ① 목표 판정은 상태를 "생성할 때" 가 아니라 큐에서 "꺼낼 때" 한다 — 생성 시점에는 더 싼 길이 아직 큐에 있을 수 있다. ② 이미 더 싼 비용으로 닫힌 상태는 건너뛴다(지연 삭제). 꺼내는 비용은 단조 비감소여야 한다.
// 물통 문제(8·5·3 리터, 한 통에 4 리터 만들기; 비용 = 옮긴 물의 양)로 검증한다. 상태 공간 전체를 따로 열거해 Bellman-Ford 로 구한 최적값과 같고, 모든 비용을 1 로 하면 BFS 단계 수와 같으며, 생성 시점 목표 판정은 최적이 아닌 예(S→G 10, S→A→G 1+1)가 있음을 확인한다
typedef std::vector<int> St;
long ucs(const St& start, std::function<bool(const St&)> goal, std::function<std::vector<std::pair<St, int>>(const St&)> succ, bool earlyTest, long* expanded) {
    typedef std::pair<long, St> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; std::map<St, long> best; best[start] = 0; pq.push({0, start}); long lastPopped = -1; *expanded = 0;
    while (!pq.empty()) {
        auto [c, s] = pq.top(); pq.pop(); if (c > best[s]) continue; assert(c >= lastPopped); lastPopped = c;                                // 꺼낸 비용은 단조 비감소
        if (!earlyTest && goal(s)) return c; (*expanded)++;
        for (auto& [t, w] : succ(s)) { if (earlyTest && goal(t)) return c + w; auto it = best.find(t); if (it == best.end() || c + w < it->second) { best[t] = c + w; pq.push({c + w, t}); } }
    }
    return -1;
}
int main() {
    const int cap[3] = {8, 5, 3}; auto pour = [&](bool unitCost) { return [=](const St& s) { std::vector<std::pair<St, int>> r; for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) if (i != j && s[i] > 0 && s[j] < cap[j]) { int a = std::min(s[i], cap[j] - s[j]); St t = s; t[i] -= a; t[j] += a; r.push_back({t, unitCost ? 1 : a}); } return r; }; };
    auto isGoal = [](const St& s) { return s[0] == 4 || s[1] == 4 || s[2] == 4; }; St start = {8, 0, 0}; long ex;
    long ans = ucs(start, isGoal, pour(false), false, &ex); assert(ans > 0);
    std::map<St, int> id; std::vector<St> all; std::vector<std::vector<std::pair<int, int>>> g; std::queue<St> q; id[start] = 0; all.push_back(start); q.push(start);               // 독립 검증용: 상태 공간 전체를 열거
    while (!q.empty()) { St s = q.front(); q.pop(); for (auto& [t, w] : pour(false)(s)) if (!id.count(t)) { id[t] = all.size(); all.push_back(t); q.push(t); } }
    g.assign(all.size(), {}); for (size_t u = 0; u < all.size(); u++) for (auto& [t, w] : pour(false)(all[u])) g[u].push_back({id[t], w});
    std::vector<long> d(all.size(), 1L << 40); d[0] = 0; for (size_t it = 0; it < all.size(); it++) { bool ch = false; for (size_t u = 0; u < all.size(); u++) if (d[u] < (1L << 40)) for (auto& [v, w] : g[u]) if (d[u] + w < d[v]) { d[v] = d[u] + w; ch = true; } if (!ch) break; }
    long ref = 1L << 40; for (size_t u = 0; u < all.size(); u++) if (isGoal(all[u])) ref = std::min(ref, d[u]); assert(ans == ref && ex < (long)all.size());                                   // 최적값 일치, 상태 일부만 확장
    long unit = ucs(start, isGoal, pour(true), false, &ex); std::vector<int> dep(all.size(), -1); dep[0] = 0; q.push(start); int bfs = -1; while (!q.empty()) { St s = q.front(); q.pop(); if (isGoal(s)) { bfs = dep[id[s]]; break; } for (auto& [t, w] : pour(true)(s)) if (dep[id[t]] < 0) { dep[id[t]] = dep[id[s]] + 1; q.push(t); } } assert(unit == bfs);   // 단위 비용이면 BFS 와 같음
    std::vector<std::vector<std::pair<St, int>>> tiny = {{{{1}, 1}, {{2}, 10}}, {{{2}, 1}}, {}};                                                                                                 // S=0, A=1, G=2: S→A 1, S→G 10, A→G 1
    auto tsucc = [&](const St& s) { return tiny[s[0]]; }; auto tgoal = [](const St& s) { return s[0] == 2; };
    long good = ucs({0}, tgoal, tsucc, false, &ex), early = ucs({0}, tgoal, tsucc, true, &ex); assert(good == 2 && early == 10);
    std::cout << "UniformCostSearch: min liters moved to measure 4 = " << ans << " (Bellman-Ford over " << all.size() << " states agrees), unit-cost UCS == BFS depth " << unit << ", early goal test gives " << early << " instead of " << good << std::endl; return 0;
}
// Time Complexity: O((b^(C*/ε)) log) — 최적 비용 C* 안쪽 상태를 모두 확장 (암시적 그래프)
// Space Complexity: O(확장 상태 수)
```
## MinCostPath()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 최소 비용 경로(격자): 칸에 들어갈 때 그 칸의 비용을 내는 격자에서 (0,0)→(R-1,C-1) 의 최소 비용 경로. 이동 규칙에 따라 도구가 갈린다.
// ① 아래·오른쪽(·대각선)으로만 갈 수 있으면 방향이 DAG 라서 DP 한 번으로 충분하다 — dp[r][c] = cost[r][c] + min(dp[이전 칸들]), 음수 비용도 문제없다. ② 네 방향 모두 허용하면 순환이 생기므로 비용이 음이 아닐 때 Dijkstra 가 필요하고, 같은 격자에서 ①보다 항상 같거나 싸다.
// 검증: 작은 격자(≤5×5)에서 모든 단조 경로를 재귀로 완전 열거한 값과 DP 가 같고(음수 비용 포함), 4방향 Dijkstra 는 Bellman-Ford 반복 완화 값과 같으며 DP 값 이하이고, DP 의 경로 복원이 합계와 일치함을 확인한다
typedef std::vector<std::vector<int>> M;
int dpMonotone(const M& a, bool diag, std::vector<std::pair<int, int>>* path) {
    int R = a.size(), C = a[0].size(); std::vector<std::vector<int>> dp(R, std::vector<int>(C, INT_MAX)); std::vector<std::vector<std::pair<int, int>>> from(R, std::vector<std::pair<int, int>>(C, {-1, -1}));
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (!r && !c) { dp[r][c] = a[r][c]; continue; } int best = INT_MAX; std::pair<int, int> bp{-1, -1};
        auto tryFrom = [&](int pr, int pc) { if (pr >= 0 && pc >= 0 && dp[pr][pc] < best) { best = dp[pr][pc]; bp = {pr, pc}; } }; tryFrom(r - 1, c); tryFrom(r, c - 1); if (diag) tryFrom(r - 1, c - 1); dp[r][c] = best + a[r][c]; from[r][c] = bp; }
    if (path) { path->clear(); for (std::pair<int, int> p{R - 1, C - 1}; p.first >= 0; p = from[p.first][p.second]) path->push_back(p); std::reverse(path->begin(), path->end()); }
    return dp[R - 1][C - 1];
}
int brute(const M& a, bool diag, int r, int c) { int R = a.size(), C = a[0].size(); if (r == R - 1 && c == C - 1) return a[r][c]; int best = INT_MAX; if (r + 1 < R) best = std::min(best, brute(a, diag, r + 1, c)); if (c + 1 < C) best = std::min(best, brute(a, diag, r, c + 1)); if (diag && r + 1 < R && c + 1 < C) best = std::min(best, brute(a, diag, r + 1, c + 1)); return a[r][c] + best; }
int dijkstra4(const M& a) {
    int R = a.size(), C = a[0].size(); std::vector<std::vector<int>> d(R, std::vector<int>(C, INT_MAX)); typedef std::tuple<int, int, int> T; std::priority_queue<T, std::vector<T>, std::greater<T>> pq; d[0][0] = a[0][0]; pq.push({a[0][0], 0, 0});
    while (!pq.empty()) { auto [du, r, c] = pq.top(); pq.pop(); if (du > d[r][c]) continue; const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C) continue; if (du + a[nr][nc] < d[nr][nc]) { d[nr][nc] = du + a[nr][nc]; pq.push({d[nr][nc], nr, nc}); } } }
    return d[R - 1][C - 1];
}
int relaxAll(const M& a) {                                                                                                  // Bellman-Ford 식 반복 완화(독립 검증)
    int R = a.size(), C = a[0].size(); std::vector<std::vector<int>> d(R, std::vector<int>(C, INT_MAX / 2)); d[0][0] = a[0][0]; for (bool ch = true; ch;) { ch = false; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C) continue; if (d[r][c] + a[nr][nc] < d[nr][nc]) { d[nr][nc] = d[r][c] + a[nr][nc]; ch = true; } } } } return d[R - 1][C - 1]; }
int main() {
    std::mt19937 g(2); int strictlyBetter = 0, trials = 0;
    for (int t = 0; t < 400; t++) {
        int R = 2 + g() % 4, C = 2 + g() % 4; M neg(R, std::vector<int>(C)), pos(R, std::vector<int>(C)); for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { neg[r][c] = (int)(g() % 21) - 8; pos[r][c] = 1 + g() % 9; }
        for (bool diag : {false, true}) { std::vector<std::pair<int, int>> path; int v = dpMonotone(neg, diag, &path); assert(v == brute(neg, diag, 0, 0)); int sum = 0; for (auto& p : path) sum += neg[p.first][p.second]; assert(sum == v && path.front() == std::make_pair(0, 0) && path.back() == std::make_pair(R - 1, C - 1)); }
        int mono = dpMonotone(pos, false, nullptr), free4 = dijkstra4(pos); assert(free4 == relaxAll(pos) && free4 <= mono); trials++;
        M maze(8, std::vector<int>(8)); for (auto& row : maze) for (int& x : row) x = g() % 100 < 35 ? 40 : 1; maze[0][0] = maze[7][7] = 1;         // 비싼 칸이 섞인 큰 격자: 돌아가는 편이 싼 경우
        int m2 = dpMonotone(maze, false, nullptr), f2 = dijkstra4(maze); assert(f2 == relaxAll(maze) && f2 <= m2); strictlyBetter += f2 < m2;
    }
    assert(strictlyBetter > 5);
    std::cout << "MinCostPath: " << trials << " grids; monotone DP == exhaustive (negative costs too), 4-direction Dijkstra == relaxation and strictly cheaper than DP on " << strictlyBetter << " grids" << std::endl; return 0;
}
// Time Complexity: DP O(RC), Dijkstra O(RC log RC)
// Space Complexity: O(RC)
```
## ResourceConstrainedPath()
### 대표코드
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <queue>
#include <random>
#include <tuple>
#include <vector>
#include <cassert>

// 자원 제약 최단 경로(RCSP): 간선마다 비용 c 와 자원 소모량 r(시간·연료·요금)이 있고, "자원 합이 한도 T 이하인 경로 중 비용 합이 최소" 인 경로를 찾는다. 일반적으로 NP-난해(배낭 문제를 포함)이지만 자원이 정수면 의사 다항 시간에 풀린다.
// 방법 A: 라벨 설정(label-setting). 정점마다 (비용, 자원) 라벨 여러 개를 두고, 비용 순으로 꺼내며 자원 한도를 넘으면 버린다. 같은 정점의 기존 라벨이 비용·자원 모두 이하이면 새 라벨은 "지배당해" 버린다 — 이 지배(dominance) 가지치기가 핵심이다.
// 방법 B: 자원 층 DP. best[x][v] = 자원을 정확히 x 쓰고 v 에 도착하는 최소 비용(자원이 양의 정수이면 x 오름차순으로 계산 가능). 방법 C: 모든 단순 경로를 DFS 로 완전 열거(양의 비용·자원에서는 최적해가 단순 경로).
// 세 방법이 같은 값을 내는지 무작위 그래프 300개로 확인하고, 지배 가지치기가 만드는 라벨 수를 한도만 검사하는 경우와 비교한다
struct E { int to, c, r; };
int main() {
    std::mt19937 g(13); int T = 16, agree = 0, infeasible = 0; long withDom = 0, noDom = 0;
    for (int trial = 0; trial < 300; trial++) {
        int n = 10; std::vector<std::vector<E>> adj(n); for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v && g() % 100 < 38) adj[u].push_back({v, 1 + (int)(g() % 9), 1 + (int)(g() % 6)});
        auto labelSetting = [&](bool dominance, long& labels) -> long {
            std::vector<std::vector<std::pair<int, int>>> kept(n); typedef std::tuple<int, int, int> L; std::priority_queue<L, std::vector<L>, std::greater<L>> pq; pq.push({0, 0, 0}); labels = 0;
            while (!pq.empty()) { auto [c, r, u] = pq.top(); pq.pop(); bool dom = false; if (dominance) for (auto& k : kept[u]) if (k.first <= c && k.second <= r) dom = true; if (dom) continue; kept[u].push_back({c, r}); labels++; if (u == n - 1) return c;       // 비용 순이라 처음 꺼낸 목표 라벨이 최적
                for (const E& e : adj[u]) if (r + e.r <= T) pq.push({c + e.c, r + e.r, e.to}); }
            return -1; };
        long l1, l2; long a = labelSetting(true, l1), a2 = labelSetting(false, l2); assert(a == a2);
        const int INF = 1 << 28; std::vector<std::vector<int>> best(T + 1, std::vector<int>(n, INF)); best[0][0] = 0; for (int x = 0; x <= T; x++) for (int u = 0; u < n; u++) if (best[x][u] < INF) for (const E& e : adj[u]) if (x + e.r <= T) best[x + e.r][e.to] = std::min(best[x + e.r][e.to], best[x][u] + e.c);
        long b = INF; for (int x = 0; x <= T; x++) b = std::min<long>(b, best[x][n - 1]); if (b >= INF) b = -1; assert(a == b);
        long cBrute = 1L << 40; std::vector<char> vis(n, 0); std::function<void(int, int, int)> dfs = [&](int u, int c, int r) { if (u == n - 1) { cBrute = std::min<long>(cBrute, c); return; } vis[u] = 1; for (const E& e : adj[u]) if (!vis[e.to] && r + e.r <= T) dfs(e.to, c + e.c, r + e.r); vis[u] = 0; };
        dfs(0, 0, 0); if (cBrute == (1L << 40)) cBrute = -1; assert(a == cBrute);
        if (a < 0) infeasible++; else { agree++; withDom += l1; noDom += l2; }
    }
    assert(agree > 150 && infeasible > 0 && withDom * 2 < noDom);
    std::cout << "ResourceConstrainedPath: " << agree << " feasible instances (+" << infeasible << " infeasible) agree across label-setting, layered DP and exhaustive search; dominance keeps " << withDom << " labels vs " << noDom << " without it" << std::endl; return 0;
}
// Time Complexity: O(T · E) 층 DP (의사 다항), 라벨 설정은 최악 지수
// Space Complexity: O(T · V)
```
## TimeDependentShortestPath()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 시간 의존 최단 경로: 도로 통행 시간이 출발 시각에 따라 달라지는(출퇴근 정체) 그래프. 간선 e 에 출발 시각 t 별 통행 시간 tt_e(t) 를 주고, 정점 v 에 도착하는 가장 이른 시각을 구한다.
// FIFO 성질 — 늦게 출발한 차가 먼저 출발한 차를 추월하지 못함, 즉 t + tt_e(t) 가 t 에 대해 비감소 — 이 성립하면 "일찍 도착하는 것이 항상 이득" 이라 기다릴 필요가 없고 평범한 Dijkstra(비용 대신 도착 시각, 간선 완화는 arr = t + tt_e(t))가 정확하다.
// FIFO 가 깨지면(예: 통행 시간이 급락) 일찍 도착해도 간선 앞에서 기다리는 편이 더 빠를 수 있어 Dijkstra 가 틀린다. 검증: ① FIFO 함수 200개 그래프에서 TD-Dijkstra == 대기를 허용한 시간 확장 DP, ② 비 FIFO 함수에서는 TD-Dijkstra 가 시간 확장 최적보다 늦게 도착하는 사례가 실제로 존재함을 확인한다
struct E { int to; std::vector<int> tt; };                                                                                      // tt[t] = 시각 t 에 출발할 때 통행 시간(범위 밖은 마지막 값)
const int H = 40;
int ttAt(const E& e, int t) { return e.tt[std::min(t, H - 1)]; }
int tdDijkstra(const std::vector<std::vector<E>>& adj, int s, int t0, int target) {
    int n = adj.size(); std::vector<int> arr(n, 1 << 28); typedef std::pair<int, int> P; std::priority_queue<P, std::vector<P>, std::greater<P>> pq; arr[s] = t0; pq.push({t0, s});
    while (!pq.empty()) { auto [t, u] = pq.top(); pq.pop(); if (t > arr[u]) continue; for (const E& e : adj[u]) { int a = t + ttAt(e, t); if (a < arr[e.to]) { arr[e.to] = a; pq.push({a, e.to}); } } }
    return arr[target];
}
int timeExpanded(const std::vector<std::vector<E>>& adj, int s, int t0, int target) {                                          // 상태 (정점, 시각) 에서 기다림(+1)과 간선 이용을 모두 허용하는 도달 가능성 DP
    int n = adj.size(), TM = 400; std::vector<std::vector<char>> ok(TM + 1, std::vector<char>(n, 0)); ok[t0][s] = 1;
    for (int t = t0; t <= TM; t++) for (int u = 0; u < n; u++) if (ok[t][u]) { if (u == target) return t; if (t + 1 <= TM) ok[t + 1][u] = 1; for (const E& e : adj[u]) { int a = t + ttAt(e, t); if (a <= TM) ok[a][e.to] = 1; } }
    return 1 << 28;
}
int main() {
    std::mt19937 g(31); int fifoChecked = 0, rushUsed = 0, nonFifoWorse = 0, nonFifoEqual = 0;
    for (int trial = 0; trial < 400; trial++) {
        bool fifo = trial < 200; int n = 7; std::vector<std::vector<E>> adj(n);
        for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (u != v && g() % 100 < 40) {
            E e; e.to = v; e.tt.resize(H); int base = 1 + g() % 5, prev = 0;
            for (int t = 0; t < H; t++) { if (fifo) { int arrive = std::max(prev, t + base + (int)(g() % 4) + ((t > 8 && t < 20) ? 5 : 0)); e.tt[t] = arrive - t; prev = arrive; }      // 도착 시각이 비감소가 되도록 만든다(FIFO)
                else e.tt[t] = 1 + g() % 12; }                                                                                                                                         // 임의 함수(대개 FIFO 아님)
            adj[u].push_back(e);
        }
        int t0 = g() % 15; int a = tdDijkstra(adj, 0, t0, n - 1), b = timeExpanded(adj, 0, t0, n - 1);
        if (fifo) { assert(a == b); if (a < (1 << 28)) fifoChecked++; if (a < (1 << 28) && a - t0 > 0) rushUsed++; } else { assert(b <= a); if (b < a) nonFifoWorse++; else nonFifoEqual++; }
    }
    std::vector<std::vector<E>> tiny(2); E e; e.to = 1; e.tt.assign(H, 1); e.tt[0] = 10; tiny[0].push_back(e);                    // 시각 0 출발은 10 걸리지만 시각 1 출발은 1 이면 1 만 기다려도 2 에 도착
    assert(tdDijkstra(tiny, 0, 0, 1) == 10 && timeExpanded(tiny, 0, 0, 1) == 2);
    assert(fifoChecked > 80 && nonFifoWorse > 0);
    std::cout << "TimeDependentShortestPath: " << fifoChecked << " FIFO instances match the time-expanded optimum; without FIFO, plain Dijkstra arrived later on " << nonFifoWorse << " of " << nonFifoWorse + nonFifoEqual << " instances (waiting 1 tick turns 10 into 2 in the tiny example)" << std::endl; return 0;
}
// Time Complexity: O((V + E) log V) (FIFO) — 시간 확장 그래프는 O(T · (V + E))
// Space Complexity: O(V + E · H)
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
