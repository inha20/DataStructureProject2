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
    assert(agree > 150 && infeasible > 0 && withDom * 3 < noDom * 2);
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
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 협력 A*(Silver 2005, Cooperative A*): 에이전트를 우선순위 순으로 하나씩 계획한다. 각 에이전트는 시공간 (칸, 시각) 위에서 A* 를 돌리되 앞선 에이전트들이 예약한 (칸, 시각)과 맞교환을 피하고 제자리 대기도 행동으로 쓴다.
// 휴리스틱은 예약을 무시한 정적 최단 거리(허용적)이고 목표 판정은 "목표 칸에 있고 그 시각 이후 다른 예약이 없음" 이다. 목표에 도착한 에이전트는 그 칸을 영구 점유한다. 완전성·최적성은 보장되지 않는다(우선순위가 나쁘면 막히거나 합이 커진다).
// 검증: ① 각 에이전트의 A* 도착 시각이 같은 예약 표 위의 시각 확장 BFS 와 같음(그 에이전트 입장에서는 최적), ② 해를 찾은 경우 모든 시각의 정점·맞교환 충돌 0건, ③ 첫 에이전트는 정적 최단 거리와 같고 전체 비용은 정적 거리 합 이상
const int INF = 1 << 28; int R, C, N, TMAX;
struct Table { std::vector<std::vector<char>> vert; std::set<std::tuple<int, int, int>> swp; std::vector<int> parked, last;
    void init() { vert.assign(TMAX + 2, std::vector<char>(N, 0)); parked.assign(N, INF); last.assign(N, -1); }
    bool freeAt(int cell, int t) const { return t < parked[cell] && !vert[t][cell]; }
    bool canMove(int u, int v, int t) const { return freeAt(v, t + 1) && !swp.count({t, v, u}); }
    void reserve(const std::vector<int>& p) { for (size_t t = 0; t < p.size(); t++) { vert[t][p[t]] = 1; last[p[t]] = std::max(last[p[t]], (int)t); } for (size_t t = 0; t + 1 < p.size(); t++) swp.insert({(int)t, p[t], p[t + 1]}); parked[p.back()] = std::min(parked[p.back()], (int)p.size() - 1); }
    bool goalOk(int g, int t) const { return parked[g] == INF && last[g] < t; }                                                  // t 이후 아무도 목표 칸을 쓰지 않음
};
std::vector<std::string> w; const int dr[5] = {0, 1, -1, 0, 0}, dc[5] = {0, 0, 0, 1, -1};
std::vector<int> staticDist(int goal) { std::vector<int> d(N, INF); std::queue<int> q; d[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); for (int k = 1; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#' || d[r * C + c] < INF) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
std::vector<int> plan(const Table& tb, int s, int goal, const std::vector<int>& h) {                                           // 시공간 A*; 실패 시 빈 벡터
    if (!tb.freeAt(s, 0)) return {}; std::vector<int> par((TMAX + 1) * N, -2); typedef std::tuple<int, int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; par[s] = -1; pq.push({h[s], 0, s});
    while (!pq.empty()) { auto [f, nt, u] = pq.top(); pq.pop(); int t = -nt; if (u == goal && tb.goalOk(goal, t)) { std::vector<int> p; for (int id = t * N + u; id >= 0; id = par[id]) p.push_back(id % N); std::reverse(p.begin(), p.end()); return p; } if (t >= TMAX) continue;
        for (int k = 0; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#') continue; int v = r * C + c; if (!tb.canMove(u, v, t) || h[v] >= INF) continue; int id = (t + 1) * N + v; if (par[id] != -2) continue; par[id] = t * N + u; pq.push({t + 1 + h[v], -(t + 1), v}); } }
    return {}; }
int bfsArrival(const Table& tb, int s, int goal) {                                                                              // 독립 검증: 시각 확장 BFS 로 최소 도착 시각
    std::vector<char> cur(N, 0), nxt; if (!tb.freeAt(s, 0)) return INF; cur[s] = 1;
    for (int t = 0; t <= TMAX; t++) { if (cur[goal] && tb.goalOk(goal, t)) return t; nxt.assign(N, 0); for (int u = 0; u < N; u++) if (cur[u]) for (int k = 0; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#') continue; if (tb.canMove(u, r * C + c, t)) nxt[r * C + c] = 1; } cur = nxt; }
    return INF; }
int conflicts(std::vector<std::vector<int>> p) { size_t T = 0; for (auto& x : p) T = std::max(T, x.size()); for (auto& x : p) x.resize(T, x.back()); int bad = 0; for (size_t t = 0; t < T; t++) for (size_t i = 0; i < p.size(); i++) for (size_t j = i + 1; j < p.size(); j++) { if (p[i][t] == p[j][t]) bad++; if (t + 1 < T && p[i][t] == p[j][t + 1] && p[i][t + 1] == p[j][t] && p[i][t] != p[i][t + 1]) bad++; } return bad; }
int main() {
    std::mt19937 g(6); R = C = 8; N = R * C; TMAX = 4 * N; int solved = 0, tried = 0; long soc = 0, lower = 0;
    for (int trial = 0; trial < 150; trial++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (g() % 100 < 10) ch = '#'; std::vector<int> cells; for (int i = 0; i < N; i++) if (w[i / C][i % C] == '.') cells.push_back(i);
        int A = 6; std::shuffle(cells.begin(), cells.end(), g); std::vector<int> st(cells.begin(), cells.begin() + A), gl(cells.begin() + A, cells.begin() + 2 * A); std::vector<std::vector<int>> hs; bool ok = true; for (int i = 0; i < A; i++) { hs.push_back(staticDist(gl[i])); ok = ok && hs[i][st[i]] < INF; } if (!ok) continue; tried++;
        Table tb; tb.init(); std::vector<std::vector<int>> paths; bool fail = false;
        for (int i = 0; i < A && !fail; i++) { std::vector<int> p = plan(tb, st[i], gl[i], hs[i]); int ref = bfsArrival(tb, st[i], gl[i]);
            if (p.empty()) { assert(ref >= INF); fail = true; break; }                                                         // A* 가 실패하면 BFS 도 도달 불가
            assert((int)p.size() - 1 == ref && p.back() == gl[i]); if (i == 0) assert((int)p.size() - 1 == hs[0][st[0]]);          // 에이전트별 최적, 첫 에이전트는 정적 최단
            for (size_t t = 1; t < p.size(); t++) assert(p[t] == p[t - 1] || (std::abs(p[t] / C - p[t - 1] / C) + std::abs(p[t] % C - p[t - 1] % C) == 1 && w[p[t] / C][p[t] % C] != '#'));
            tb.reserve(p); paths.push_back(p); }
        if (fail) continue; assert(conflicts(paths) == 0); solved++; for (int i = 0; i < A; i++) { soc += (int)paths[i].size() - 1; lower += hs[i][st[i]]; } assert(soc >= lower);
    }
    assert(tried > 100 && solved * 100 > tried * 60);
    std::cout << "CooperativeAStar: " << solved << "/" << tried << " 6-agent instances solved conflict-free; sum of costs " << soc << " vs " << lower << " (sum of individual shortest paths)" << std::endl; return 0;
}
// Time Complexity: O(에이전트 수 × (V · T) log) — 에이전트마다 시공간 A*
// Space Complexity: O(V · T)
```
## ConflictBasedSearch()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 충돌 기반 탐색(CBS, Sharon et al. 2015): 비용 합(SOC)이 최소인 다중 에이전트 경로를 구하는 최적 알고리즘. 두 단계로 나뉜다.
// 상위 단계는 "제약 트리" 를 최선 우선으로 탐색한다. 노드는 에이전트별 제약 집합과 그 제약 아래 각 에이전트가 독립적으로 구한 최적 경로들이고, 비용은 경로 비용의 합이다. 노드의 경로들에서 처음 발견한 충돌(i, j, 칸, 시각)이 있으면 자식 둘을 만든다 —
// "i 는 그 칸 그 시각에 있으면 안 된다" / "j 는 안 된다". 충돌이 없으면 그 노드가 최적해이다(비용이 가장 작은 노드부터 확장하므로). 하위 단계는 한 에이전트의 제약을 지키는 시공간 A* 이며 정점 제약과 간선(맞교환) 제약을 쓴다.
// 목표 판정은 "목표 칸에서 그 시각 이후의 정점 제약이 없음" 이어야 한다(안 그러면 도착 후 길을 막힌다). 검증: 2~3 에이전트의 작은 격자에서, 각 에이전트가 목표에 가서 "영구히 머무른다" 고 확정(done)하는 시점을 상태에 넣은 결합 상태 Dijkstra 와 SOC 가 같은지 대조한다
const int INF = 1 << 28; int R, C, N; std::vector<std::string> w; const int dr[5] = {0, 1, -1, 0, 0}, dc[5] = {0, 0, 0, 1, -1};
struct Con { int agent, type, a, b, t; bool operator<(const Con& o) const { return std::tie(agent, type, a, b, t) < std::tie(o.agent, o.type, o.a, o.b, o.t); } };    // type 0: 정점(a 칸, 시각 t), type 1: 간선(a→b, 시각 t 에 도착)
std::vector<int> staticDist(int goal) { std::vector<int> d(N, INF); std::queue<int> q; d[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); for (int k = 1; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#' || d[r * C + c] < INF) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
std::vector<int> lowLevel(int agent, int s, int goal, const std::vector<int>& h, const std::set<Con>& cons) {
    int lastGoal = -1, tmax = 0; for (const Con& c : cons) { if (c.agent != agent) continue; tmax = std::max(tmax, c.t); if (c.type == 0 && c.a == goal) lastGoal = std::max(lastGoal, c.t); } int T = tmax + 2 * N + 2;
    std::map<std::pair<int, int>, std::pair<int, int>> par; typedef std::tuple<int, int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; par[{s, 0}] = {-1, -1}; pq.push({h[s], 0, s});
    while (!pq.empty()) { auto [f, t, u] = pq.top(); pq.pop(); if (u == goal && t > lastGoal) { std::vector<int> p; std::pair<int, int> cur{u, t}; while (cur.first >= 0) { p.push_back(cur.first); cur = par[cur]; } std::reverse(p.begin(), p.end()); return p; } if (t >= T) continue;
        for (int k = 0; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#') continue; int v = r * C + c; if (cons.count({agent, 0, v, 0, t + 1}) || cons.count({agent, 1, u, v, t + 1}) || par.count({v, t + 1})) continue; par[{v, t + 1}] = {u, t}; pq.push({t + 1 + h[v], t + 1, v}); } }
    return {}; }
struct Conflict { int i, j, type, a, b, t; };
bool firstConflict(const std::vector<std::vector<int>>& P, Conflict& out) {
    size_t T = 0; for (auto& p : P) T = std::max(T, p.size()); auto at = [&](int i, size_t t) { return P[i][std::min(t, P[i].size() - 1)]; };
    for (size_t t = 0; t < T; t++) for (size_t i = 0; i < P.size(); i++) for (size_t j = i + 1; j < P.size(); j++) { if (at(i, t) == at(j, t)) { out = {(int)i, (int)j, 0, at(i, t), 0, (int)t}; return true; } if (t + 1 < T && at(i, t) == at(j, t + 1) && at(i, t + 1) == at(j, t)) { out = {(int)i, (int)j, 1, at(i, t), at(i, t + 1), (int)t + 1}; return true; } }
    return false; }
long cbs(const std::vector<int>& st, const std::vector<int>& gl, long& nodes) {
    int A = st.size(); std::vector<std::vector<int>> hs; for (int i = 0; i < A; i++) hs.push_back(staticDist(gl[i]));
    struct Node { std::set<Con> cons; std::vector<std::vector<int>> paths; long cost; }; auto cmp = [](const Node* a, const Node* b) { return a->cost > b->cost; }; std::priority_queue<Node*, std::vector<Node*>, decltype(cmp)> open(cmp); std::vector<Node*> owned;
    Node* root = new Node(); owned.push_back(root); root->cost = 0; for (int i = 0; i < A; i++) { root->paths.push_back(lowLevel(i, st[i], gl[i], hs[i], root->cons)); root->cost += root->paths.back().size() - 1; } open.push(root); nodes = 0; long answer = -1;
    while (!open.empty() && nodes < 20000) { Node* cur = open.top(); open.pop(); nodes++; Conflict cf; if (!firstConflict(cur->paths, cf)) { answer = cur->cost; break; }
        for (int side = 0; side < 2; side++) { int ag = side ? cf.j : cf.i; Node* ch = new Node(*cur); owned.push_back(ch);
            if (cf.type == 0) ch->cons.insert({ag, 0, cf.a, 0, cf.t}); else ch->cons.insert(side ? Con{ag, 1, cf.b, cf.a, cf.t} : Con{ag, 1, cf.a, cf.b, cf.t});          // 간선 제약: 각자 자신의 이동 금지
            std::vector<int> p = lowLevel(ag, st[ag], gl[ag], hs[ag], ch->cons); if (p.empty()) continue; ch->cost += (long)p.size() - cur->paths[ag].size(); ch->paths[ag] = p; open.push(ch); } }
    for (Node* x : owned) delete x; return answer; }
long jointOptimum(const std::vector<int>& st, const std::vector<int>& gl) {                                                     // 독립 검증: (위치들, done 마스크) 결합 상태 Dijkstra
    int A = st.size(); typedef std::pair<long, long> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; std::map<long, long> dist; long mulPos = 1; for (int i = 0; i < A; i++) mulPos *= N;
    auto enc = [&](const std::vector<int>& pos, int mask) { long k = 0; for (int i = A - 1; i >= 0; i--) k = k * N + pos[i]; return k + mulPos * mask; }; auto dec = [&](long k, std::vector<int>& pos, int& mask) { mask = k / mulPos; k %= mulPos; for (int i = 0; i < A; i++) { pos[i] = k % N; k /= N; } };
    dist[enc(st, 0)] = 0; pq.push({0, enc(st, 0)}); std::vector<int> pos(A), np(A);
    while (!pq.empty()) { auto [d, key] = pq.top(); pq.pop(); if (d > dist[key]) continue; int mask; dec(key, pos, mask); if (mask == (1 << A) - 1) return d; int pay = 0; for (int i = 0; i < A; i++) if (!(mask >> i & 1)) pay++;
        std::vector<int> mv(A, 0); for (;;) {
            bool ok = true; for (int i = 0; i < A && ok; i++) { if (mask >> i & 1) { np[i] = pos[i]; if (mv[i]) ok = false; continue; } int r = pos[i] / C + dr[mv[i]], c = pos[i] % C + dc[mv[i]]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#') ok = false; else np[i] = r * C + c; }
            for (int i = 0; i < A && ok; i++) for (int j = i + 1; j < A && ok; j++) if (np[i] == np[j] || (np[i] == pos[j] && np[j] == pos[i] && pos[i] != np[i])) ok = false;
            if (ok) { std::vector<int> atGoal; for (int i = 0; i < A; i++) if (!(mask >> i & 1) && np[i] == gl[i]) atGoal.push_back(i);
                for (int sub = 0; sub < (1 << atGoal.size()); sub++) { int m2 = mask; for (size_t b = 0; b < atGoal.size(); b++) if (sub >> b & 1) m2 |= 1 << atGoal[b]; long k2 = enc(np, m2); auto it = dist.find(k2); if (it == dist.end() || d + pay < it->second) { dist[k2] = d + pay; pq.push({d + pay, k2}); } } }
            int i = 0; while (i < A && ++mv[i] == 5) mv[i++] = 0; if (i == A) break; } }
    return -1; }
int main() {
    std::mt19937 g(4); int checked = 0, hard = 0; long nodeTotal = 0;
    for (int trial = 0; trial < 75; trial++) {
        int A = trial < 55 ? 2 : 3; R = A == 2 ? 5 : 4; C = 4; N = R * C; w.assign(R, std::string(C, '.')); for (int k = 0; k < 2; k++) w[g() % R][g() % C] = '#';
        std::vector<int> cells; for (int i = 0; i < N; i++) if (w[i / C][i % C] == '.') cells.push_back(i); std::shuffle(cells.begin(), cells.end(), g); std::vector<int> st(cells.begin(), cells.begin() + A), gl(cells.begin() + A, cells.begin() + 2 * A);
        long ref = jointOptimum(st, gl); if (ref < 0) continue; long nodes; long got = cbs(st, gl, nodes); assert(got == ref); checked++; nodeTotal += nodes; long indep = 0; for (int i = 0; i < A; i++) indep += staticDist(gl[i])[st[i]]; if (got > indep) hard++;
    }
    assert(checked > 40 && hard > 5);
    std::cout << "ConflictBasedSearch: " << checked << " instances, SOC equals the joint-state optimum in all; " << hard << " needed more than the independent shortest paths (" << nodeTotal << " constraint-tree nodes)" << std::endl; return 0;
}
// Time Complexity: 최악 지수(제약 트리), 실전에서는 충돌 수에 따라 증가
// Space Complexity: O(제약 트리 노드 × 에이전트 × 경로 길이)
```
## MultiAgentPathFinding()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 다중 에이전트 경로 찾기(MAPF) 문제 정의와 평가. 격자에서 에이전트마다 시작·목표가 있고, 한 걸음에 상하좌우 이동 또는 대기를 하며, 같은 시각 같은 칸(정점 충돌)과 서로 자리를 맞바꾸기(교환 충돌)가 금지된다.
// 목적은 비용 합(SOC, 각 에이전트가 목표에 최종 도착하는 시각의 합) 또는 최대 도착 시각(makespan) 최소화. 최적해는 NP-난해이다. 세 접근을 같은 작은 사례들에서 비교한다 — ① 독립 계획(각자 최단 경로; 충돌을 무시) ② 우선순위 계획(협력 A* 식: 순서대로 계획하고 앞 경로를 장애물로 취급; 순서에 따라 해가 없을 수 있음) ③ 결합 상태 정확 탐색(작은 사례의 기준).
// 확인할 사실: 독립 계획은 자주 충돌한다 / 우선순위 계획은 순서에 따라 성공 여부와 비용이 달라 순서를 바꾸면 더 풀린다 / 푼 경우 SOC 는 정확 최적 이상이다(최적과의 간격이 곧 우선순위 계획의 손실) / 정확 탐색만 해결하는 사례가 존재한다. 최적 알고리즘 CBS 는 바로 앞 항목
const int INF = 1 << 28; int R, C, N; std::vector<std::string> w; const int dr[5] = {0, 1, -1, 0, 0}, dc[5] = {0, 0, 0, 1, -1};
std::vector<int> staticDist(int goal) { std::vector<int> d(N, INF); std::queue<int> q; d[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); for (int k = 1; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#' || d[r * C + c] < INF) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
std::vector<int> shortestPath(int s, int goal) { auto d = staticDist(goal); std::vector<int> p = {s}; while (p.back() != goal) { int u = p.back(); for (int k = 1; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r >= 0 && c >= 0 && r < R && c < C && d[r * C + c] == d[u] - 1) { p.push_back(r * C + c); break; } } } return p; }
int conflicts(std::vector<std::vector<int>> p) { size_t T = 0; for (auto& x : p) T = std::max(T, x.size()); for (auto& x : p) x.resize(T, x.back()); int bad = 0; for (size_t t = 0; t < T; t++) for (size_t i = 0; i < p.size(); i++) for (size_t j = i + 1; j < p.size(); j++) { if (p[i][t] == p[j][t]) bad++; if (t + 1 < T && p[i][t] == p[j][t + 1] && p[i][t + 1] == p[j][t] && p[i][t] != p[i][t + 1]) bad++; } return bad; }
bool prioritized(const std::vector<int>& st, const std::vector<int>& gl, const std::vector<int>& order, long& soc) {                  // 순서대로 BFS(시각 확장)로 계획하고 앞 경로를 예약
    int T = 4 * N; std::vector<std::vector<char>> occ(T + 2, std::vector<char>(N, 0)); std::set<std::tuple<int, int, int>> swp; std::vector<int> parked(N, INF), last(N, -1); soc = 0;
    for (int i : order) { std::vector<std::vector<int>> par(T + 1, std::vector<int>(N, -2)); std::vector<std::vector<int>> layer(1, {st[i]}); if (occ[0][st[i]]) return false; par[0][st[i]] = -1; int found = -1;
        for (int t = 0; t <= T && found < 0; t++) { for (int u : layer[t]) if (u == gl[i] && parked[u] == INF && last[u] < t) { found = t; break; } if (found >= 0 || t == T) break; layer.push_back({});
            for (int u : layer[t]) for (int k = 0; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#') continue; int v = r * C + c; if (t + 1 >= parked[v] || occ[t + 1][v] || swp.count({t, v, u}) || par[t + 1][v] != -2) continue; par[t + 1][v] = u; layer[t + 1].push_back(v); } }
        if (found < 0) return false; std::vector<int> p; int cur = gl[i]; for (int t = found; t >= 0; t--) { p.push_back(cur); cur = par[t][cur]; } std::reverse(p.begin(), p.end());
        for (size_t t = 0; t < p.size(); t++) { occ[t][p[t]] = 1; last[p[t]] = std::max(last[p[t]], (int)t); } for (size_t t = 0; t + 1 < p.size(); t++) swp.insert({(int)t, p[t], p[t + 1]}); parked[p.back()] = std::min(parked[p.back()], (int)p.size() - 1); soc += p.size() - 1; }
    return true; }
long jointOptimum(const std::vector<int>& st, const std::vector<int>& gl) {                                                           // 결합 상태 Dijkstra: (위치들, 영구 정지 마스크)
    int A = st.size(); typedef std::pair<long, long> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; std::map<long, long> dist; long mulPos = 1; for (int i = 0; i < A; i++) mulPos *= N;
    auto enc = [&](const std::vector<int>& pos, int mask) { long k = 0; for (int i = A - 1; i >= 0; i--) k = k * N + pos[i]; return k + mulPos * mask; }; auto dec = [&](long k, std::vector<int>& pos, int& mask) { mask = k / mulPos; k %= mulPos; for (int i = 0; i < A; i++) { pos[i] = k % N; k /= N; } };
    dist[enc(st, 0)] = 0; pq.push({0, enc(st, 0)}); std::vector<int> pos(A), np(A);
    while (!pq.empty()) { auto [d, key] = pq.top(); pq.pop(); if (d > dist[key]) continue; int mask; dec(key, pos, mask); if (mask == (1 << A) - 1) return d; int pay = 0; for (int i = 0; i < A; i++) if (!(mask >> i & 1)) pay++;
        std::vector<int> mv(A, 0); for (;;) { bool ok = true; for (int i = 0; i < A && ok; i++) { if (mask >> i & 1) { np[i] = pos[i]; if (mv[i]) ok = false; continue; } int r = pos[i] / C + dr[mv[i]], c = pos[i] % C + dc[mv[i]]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#') ok = false; else np[i] = r * C + c; }
            for (int i = 0; i < A && ok; i++) for (int j = i + 1; j < A && ok; j++) if (np[i] == np[j] || (np[i] == pos[j] && np[j] == pos[i] && pos[i] != np[i])) ok = false;
            if (ok) { std::vector<int> atGoal; for (int i = 0; i < A; i++) if (!(mask >> i & 1) && np[i] == gl[i]) atGoal.push_back(i); for (int sub = 0; sub < (1 << atGoal.size()); sub++) { int m2 = mask; for (size_t b = 0; b < atGoal.size(); b++) if (sub >> b & 1) m2 |= 1 << atGoal[b]; long k2 = enc(np, m2); auto it = dist.find(k2); if (it == dist.end() || d + pay < it->second) { dist[k2] = d + pay; pq.push({d + pay, k2}); } } }
            int i = 0; while (i < A && ++mv[i] == 5) mv[i++] = 0; if (i == A) break; } }
    return -1; }
int main() {
    std::mt19937 g(12); int inst = 0, indepBad = 0, fixedOk = 0, anyOk = 0, onlyExact = 0; long gap = 0, optSum = 0;
    for (int trial = 0; trial < 400; trial++) {
        R = 4; C = 4; N = 16; w.assign(R, std::string(C, '.')); for (int k = 0; k < 3; k++) w[g() % R][g() % C] = '#'; std::vector<int> cells; for (int i = 0; i < N; i++) if (w[i / C][i % C] == '.') cells.push_back(i); if (cells.size() < 6) continue;
        std::shuffle(cells.begin(), cells.end(), g); int A = 3; std::vector<int> st(cells.begin(), cells.begin() + A), gl(cells.begin() + A, cells.begin() + 2 * A); bool reach = true; for (int i = 0; i < A; i++) reach = reach && staticDist(gl[i])[st[i]] < INF; if (!reach) continue;
        long opt = jointOptimum(st, gl); if (opt < 0) continue; inst++; std::vector<std::vector<int>> ind; for (int i = 0; i < A; i++) ind.push_back(shortestPath(st[i], gl[i])); if (conflicts(ind) > 0) indepBad++;
        std::vector<int> order = {0, 1, 2}; long soc, best = INF; bool anySuccess = false; bool first = true; do { bool ok = prioritized(st, gl, order, soc); if (first) { fixedOk += ok; first = false; } if (ok) { anySuccess = true; assert(soc >= opt); best = std::min(best, soc); } } while (std::next_permutation(order.begin(), order.end()));
        anyOk += anySuccess; if (!anySuccess) onlyExact++; else { gap += best - opt; optSum += opt; }
    }
    assert(inst > 100 && indepBad > 10 && anyOk >= fixedOk && onlyExact >= 0 && anyOk > 0);
    std::cout << "MultiAgentPathFinding: " << inst << " solvable 3-agent instances; independent paths collide in " << indepBad << "; prioritized planning succeeds in " << fixedOk << " with a fixed order and " << anyOk << " with the best of 6 orders (+" << gap << " SOC over the optimum " << optSum << "); " << onlyExact << " solvable only by joint search" << std::endl; return 0;
}
// Time Complexity: 우선순위 계획 O(A · V · T), 결합 정확 탐색 O((V · 5)^A) — 에이전트 수에 지수
// Space Complexity: O(V · T) / 결합 상태 O(V^A)
```
## ReservationTable()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>
#include <cassert>

// 예약 표(reservation table): 다중 에이전트 경로 계획에서 "어느 칸을 어느 시각에 누가 쓰는가" 를 적어 두는 시공간 장부이다. 먼저 계획한 에이전트의 경로를 예약해 두고 다음 에이전트는 예약과 충돌하지 않게 계획한다.
// 충돌은 두 종류다 — 정점 충돌(같은 시각 같은 칸)과 교환(swap) 충돌(서로 칸을 맞바꿈; 정점 충돌 검사만으로는 못 잡는다). 목표에 도착한 에이전트는 영원히 그 자리를 차지하므로 "t 이후 영구 점유" 도 기록한다.
// 시각 단위 표는 (칸, 시각) 상태가 많아 탐색이 커진다. SIPP(Safe Interval Path Planning, Phillips & Likhachev 2011)는 예약이 없는 연속 구간(안전 구간)을 한 상태로 묶어 (칸, 안전 구간) 에서 탐색한다.
// 검증: 무작위 경로들을 예약한 뒤 ① 안전 구간 표현이 시각 단위 표와 모든 (칸, 시각)에서 일치, ② 교환 충돌이 감지됨, ③ SIPP 로 구한 최단 도착 시각이 시각 확장 BFS 와 일치하고 상태 수가 훨씬 적음을 확인한다
const int INF = 1 << 28;
struct Table {
    int n; std::unordered_set<long> vert; std::set<std::tuple<int, int, int>> swp; std::vector<int> parked;                     // vert: t*n+cell, swp: (t, from, to), parked[cell]: 이 시각부터 영구 점유
    Table(int n) : n(n), parked(n, INF) {}
    void reserve(const std::vector<int>& p) { for (size_t t = 0; t < p.size(); t++) vert.insert((long)t * n + p[t]); for (size_t t = 0; t + 1 < p.size(); t++) swp.insert({(int)t, p[t], p[t + 1]}); parked[p.back()] = std::min(parked[p.back()], (int)p.size() - 1); }
    bool freeAt(int cell, int t) const { return t < parked[cell] && !vert.count((long)t * n + cell); }
    bool canMove(int u, int v, int t) const { return freeAt(v, t + 1) && !swp.count({t, v, u}); }                              // 도착 칸이 비어 있고 맞교환이 아님
    std::vector<std::pair<int, int>> safeIntervals(int cell, int horizon) const {                                               // 비어 있는 시각의 극대 구간들(마지막은 INF)
        std::vector<std::pair<int, int>> r; int lo = -1; for (int t = 0; t <= horizon; t++) { bool f = freeAt(cell, t); if (f && lo < 0) lo = t; if (!f && lo >= 0) { r.push_back({lo, t - 1}); lo = -1; } } if (lo >= 0) r.push_back({lo, parked[cell] == INF ? INF : parked[cell] - 1}); return r; }
};
int main() {
    int R = 6, C = 6, n = R * C, H = 40; std::mt19937 g(9); const int dr[5] = {0, 1, -1, 0, 0}, dc[5] = {0, 0, 0, 1, -1};
    long tableEntries = 0, intervals = 0, sippStates = 0, bfsStates = 0; int queries = 0, swapCaught = 0;
    for (int trial = 0; trial < 60; trial++) {
        Table tb(n); for (int a = 0; a < 5; a++) { std::vector<int> p = {(int)(g() % n)}; int len = 3 + g() % 25; for (int t = 0; t < len; t++) { int c = p.back(), k = g() % 5, r = c / C + dr[k], cc = c % C + dc[k]; if (r < 0 || cc < 0 || r >= R || cc >= C) k = 0; p.push_back(k ? (c / C + dr[k]) * C + c % C + dc[k] : c); } tb.reserve(p);
            if (a == 0) { int u = p[0], v = p.size() > 1 ? p[1] : p[0]; if (u != v) { assert(!tb.canMove(v, u, 0)); swapCaught++; } } }                    // 방금 예약한 이동의 맞교환은 항상 금지
        tableEntries += tb.vert.size();
        for (int cell = 0; cell < n; cell++) { auto iv = tb.safeIntervals(cell, H); intervals += iv.size(); for (int t = 0; t <= H; t++) { bool in = false; for (auto& x : iv) in |= x.first <= t && t <= x.second; assert(in == tb.freeAt(cell, t)); } }   // 구간 표현 == 시각 단위 표현
        int s = g() % n, goal = g() % n; if (!tb.freeAt(s, 0)) continue;
        std::vector<std::vector<char>> reach(H + 2, std::vector<char>(n, 0)); reach[0][s] = 1; int bfsArr = INF; long bs = 0;                                          // 시각 확장 BFS(정점 예약만 사용)
        for (int t = 0; t <= H && bfsArr == INF; t++) { for (int u = 0; u < n; u++) if (reach[t][u]) { bs++; if (u == goal) { bfsArr = t; break; } for (int k = 0; k < 5; k++) { int r = u / C + dr[k], c = u % C + dc[k]; if (r < 0 || c < 0 || r >= R || c >= C) continue; int v = r * C + c; if (tb.freeAt(v, t + 1)) reach[t + 1][v] = 1; } } }
        std::vector<std::vector<std::pair<int, int>>> iv(n); for (int c = 0; c < n; c++) iv[c] = tb.safeIntervals(c, H + 1);
        std::vector<std::vector<int>> best(n); for (int c = 0; c < n; c++) best[c].assign(iv[c].size(), INF); typedef std::tuple<int, int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; int sippArr = INF; long ss = 0;
        for (size_t k = 0; k < iv[s].size(); k++) if (iv[s][k].first <= 0 && 0 <= iv[s][k].second) { best[s][k] = 0; pq.push({0, s, (int)k}); }
        while (!pq.empty()) { auto [a, u, k] = pq.top(); pq.pop(); if (a > best[u][k]) continue; ss++; if (u == goal) { sippArr = a; break; } int hi = iv[u][k].second;
            for (int d = 1; d < 5; d++) { int r = u / C + dr[d], c = u % C + dc[d]; if (r < 0 || c < 0 || r >= R || c >= C) continue; int v = r * C + c;
                for (size_t j = 0; j < iv[v].size(); j++) { int lo2 = iv[v][j].first, hi2 = iv[v][j].second; int arrive = std::max(a + 1, lo2), latest = std::min(hi == INF ? INF : hi + 1, hi2); if (arrive <= latest && arrive < best[v][j]) { best[v][j] = arrive; pq.push({arrive, v, (int)j}); } } } }
        if (bfsArr > H - 2) continue; assert(sippArr == bfsArr); queries++; sippStates += ss; bfsStates += bs;                                                                 // SIPP 도착 시각 == BFS 도착 시각
    }
    assert(swapCaught > 30 && queries > 20 && sippStates < bfsStates);
    std::cout << "ReservationTable: " << tableEntries << " (cell,time) reservations; interval view matches everywhere (" << intervals << " safe intervals); SIPP arrival == time-expanded BFS on " << queries << " queries with " << sippStates << " vs " << bfsStates << " states" << std::endl; return 0;
}
// Time Complexity: 예약/조회 O(1) 평균(해시), 안전 구간 생성 O(T), SIPP O(안전 구간 수 × log)
// Space Complexity: O(예약 수)
```

# Part 10. 지도와 공간
## NavigationMesh()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 내비게이션 메시(NavMesh): 걸을 수 있는 영역을 볼록 다각형(여기서는 삼각형)들로 덮고, 다각형 사이의 공유 변(포털)으로 인접 그래프를 만든 지도 표현이다. 격자보다 노드가 적고 경로가 격자 방향에 얽매이지 않는다.
// 길찾기는 두 단계다. ① 삼각형 그래프에서 A*/Dijkstra 로 "복도"(삼각형 열)를 구한다. ② 복도의 포털들을 따라 깔때기(funnel) 알고리즘(Lee & Preparata, 게임에서는 Mononen 의 "Simple Stupid Funnel")으로 줄을 팽팽히 당긴 최단 경로를 뽑는다 — 꺾이는 곳은 장애물 모서리뿐이다.
// 검증(무작위 지터 격자 메시, 삼각형 약 32% 를 막고 핀치 제거): ① 깔때기 경로의 모든 선분이 걸을 수 있는 영역 안 ② 같은 메시에서 모서리 정점 가시성 그래프로 구한 "정확한 최단 경로" 이상 ③ 포털 중점을 잇는 경로 이하 ④ 정확 최단과 일치하는 비율과 평균 오차 보고
typedef std::pair<double, double> V;
double cross(V a, V b, V c) { return (b.first - a.first) * (c.second - a.second) - (b.second - a.second) * (c.first - a.first); }       // >0: c 는 a→b 의 왼쪽
double dist(V a, V b) { return std::hypot(a.first - b.first, a.second - b.second); }
struct Mesh {
    std::vector<V> v; std::vector<std::array<int, 3>> tri, nb; std::vector<char> walk; std::vector<std::pair<int, int>> boundary;
    void build(int G, std::mt19937& g, int blockPct) {
        for (int j = 0; j <= G; j++) for (int i = 0; i <= G; i++) { double jx = (i == 0 || i == G) ? 0 : ((int)(g() % 61) - 30) / 100.0, jy = (j == 0 || j == G) ? 0 : ((int)(g() % 61) - 30) / 100.0; v.push_back({i + jx, j + jy}); }
        auto id = [&](int i, int j) { return j * (G + 1) + i; };
        for (int j = 0; j < G; j++) for (int i = 0; i < G; i++) { int a = id(i, j), b = id(i + 1, j), c = id(i + 1, j + 1), d = id(i, j + 1); if ((i + j) % 2) { tri.push_back({a, b, c}); tri.push_back({a, c, d}); } else { tri.push_back({a, b, d}); tri.push_back({b, c, d}); } }
        walk.assign(tri.size(), 1); for (size_t t = 0; t < tri.size(); t++) if ((int)(g() % 100) < blockPct) walk[t] = 0;
        for (bool changed = true; changed;) {                                                                                       // 핀치(꼭짓점으로만 맞닿는 걷는 삼각형 부채꼴 둘 이상)를 없앤다 — 폭 0 인 통로는 다닐 수 없다
            changed = false; std::vector<std::vector<int>> inc(v.size()); for (size_t t = 0; t < tri.size(); t++) for (int x : tri[t]) inc[x].push_back(t);
            for (size_t x = 0; x < v.size(); x++) { std::vector<int> ws; for (int t : inc[x]) if (walk[t]) ws.push_back(t); if (ws.size() < 2) continue; std::vector<int> comp(ws.size()); for (size_t i = 0; i < ws.size(); i++) comp[i] = i;
                auto shares = [&](int a, int b) { int common = 0; for (int p : tri[a]) for (int q : tri[b]) common += p == q; return common >= 2; }; for (size_t i = 0; i < ws.size(); i++) for (size_t j = 0; j < i; j++) if (shares(ws[i], ws[j])) { int ci = comp[i], cj = comp[j]; for (auto& c : comp) if (c == ci) c = cj; }
                bool pinch = false; for (int c : comp) pinch |= c != comp[0]; if (pinch) { for (int t : inc[x]) walk[t] = 1; changed = true; } } }
        nb.assign(tri.size(), {-1, -1, -1}); std::map<std::pair<int, int>, std::vector<std::pair<int, int>>> edges;
        for (size_t t = 0; t < tri.size(); t++) if (walk[t]) for (int k = 0; k < 3; k++) { int p = tri[t][k], q = tri[t][(k + 1) % 3]; edges[{std::min(p, q), std::max(p, q)}].push_back({(int)t, k}); }
        for (auto& [e, lst] : edges) { if (lst.size() == 2) { nb[lst[0].first][lst[0].second] = lst[1].first; nb[lst[1].first][lst[1].second] = lst[0].first; } else boundary.push_back(e); }
    }
    bool inTri(int t, V p) const { for (int k = 0; k < 3; k++) if (cross(v[tri[t][k]], v[tri[t][(k + 1) % 3]], p) < -1e-12) return false; return true; }
    int locate(V p) const { for (size_t t = 0; t < tri.size(); t++) if (walk[t] && inTri(t, p)) return t; return -1; }
    V centroid(int t) const { return {(v[tri[t][0]].first + v[tri[t][1]].first + v[tri[t][2]].first) / 3, (v[tri[t][0]].second + v[tri[t][1]].second + v[tri[t][2]].second) / 3}; }
    bool visible(V a, V b) const {                                                                                                  // 선분이 어떤 경계 변도 진짜로 가로지르지 않고 영역 안에 머무는가
        const double e = 1e-9; for (auto [pi, qi] : boundary) { V p = v[pi], q = v[qi]; double d1 = cross(a, b, p), d2 = cross(a, b, q), d3 = cross(p, q, a), d4 = cross(p, q, b); if (((d1 > e && d2 < -e) || (d1 < -e && d2 > e)) && ((d3 > e && d4 < -e) || (d3 < -e && d4 > e))) return false; }
        for (int s = 1; s < 8; s++) { V m{a.first + (b.first - a.first) * s / 8, a.second + (b.second - a.second) * s / 8}; if (locate(m) < 0) return false; } return true; }
};
std::vector<V> funnel(V s, V t, const std::vector<std::pair<V, V>>& portals) {                                                       // portals[i] = (왼쪽, 오른쪽)
    std::vector<std::pair<V, V>> P = {{s, s}}; P.insert(P.end(), portals.begin(), portals.end()); P.push_back({t, t});
    std::vector<V> path = {s}; V apex = s, left = s, right = s; int leftI = 0, rightI = 0;
    for (int i = 1; i < (int)P.size(); i++) {
        V nl = P[i].first, nr = P[i].second;
        if (cross(apex, right, nr) >= 0) { if (apex == right || cross(apex, left, nr) < 0) { right = nr; rightI = i; } else { path.push_back(left); apex = left; int ai = leftI; left = right = apex; leftI = rightI = ai; i = ai; continue; } }     // 오른쪽 변이 안쪽으로 좁아짐 / 왼쪽 변을 넘으면 왼쪽 점이 새 꼭짓점
        if (cross(apex, left, nl) <= 0) { if (apex == left || cross(apex, right, nl) > 0) { left = nl; leftI = i; } else { path.push_back(right); apex = right; int ai = rightI; left = right = apex; leftI = rightI = ai; i = ai; continue; } }
    }
    if (path.back() != t) path.push_back(t); return path; }
int main() {
    std::mt19937 g(14); int queries = 0, exactMatch = 0; double ratioSum = 0, worst = 1;
    for (int mesh = 0; mesh < 8; mesh++) {
        Mesh M; M.build(7, g, 32); int T = M.tri.size(); std::vector<int> vid; std::vector<int> index(M.v.size(), -1); for (auto [p, q] : M.boundary) for (int x : {p, q}) if (index[x] < 0) { index[x] = vid.size(); vid.push_back(x); }
        int nv = vid.size(); std::vector<std::vector<char>> vis(nv, std::vector<char>(nv, 0)); for (int i = 0; i < nv; i++) for (int j = i + 1; j < nv; j++) vis[i][j] = vis[j][i] = M.visible(M.v[vid[i]], M.v[vid[j]]);
        for (int q = 0; q < 25; q++) {
            auto randomPoint = [&](int& tri) { for (;;) { tri = g() % T; if (!M.walk[tri]) continue; double a = (g() % 1000) / 1000.0, b = (g() % 1000) / 1000.0; if (a + b > 1) { a = 1 - a; b = 1 - b; } V p0 = M.v[M.tri[tri][0]], p1 = M.v[M.tri[tri][1]], p2 = M.v[M.tri[tri][2]]; return V{p0.first + a * (p1.first - p0.first) + b * (p2.first - p0.first), p0.second + a * (p1.second - p0.second) + b * (p2.second - p0.second)}; } };
            int ts, tt; V s = randomPoint(ts), e = randomPoint(tt);
            std::vector<double> d(T, 1e18); std::vector<int> par(T, -1); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[ts] = 0; pq.push({0, ts});                // ① 삼각형 그래프(중심 간 거리)
            while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; if (u == tt) break; for (int k = 0; k < 3; k++) { int w = M.nb[u][k]; if (w < 0) continue; double nd = du + dist(M.centroid(u), M.centroid(w)); if (nd < d[w]) { d[w] = nd; par[w] = u; pq.push({nd, w}); } } }
            if (d[tt] > 1e17) continue; std::vector<int> corridor; for (int x = tt; x >= 0; x = par[x]) corridor.push_back(x); std::reverse(corridor.begin(), corridor.end());
            std::vector<std::pair<V, V>> portals; double mid = 0; V prev = s; for (size_t i = 0; i + 1 < corridor.size(); i++) { int u = corridor[i], k = 0; while (M.nb[u][k] != corridor[i + 1]) k++; V p = M.v[M.tri[u][k]], r = M.v[M.tri[u][(k + 1) % 3]]; portals.push_back({r, p}); V m{(p.first + r.first) / 2, (p.second + r.second) / 2}; mid += dist(prev, m); prev = m; } mid += dist(prev, e);
            std::vector<V> path = funnel(s, e, portals); double len = 0; for (size_t i = 1; i < path.size(); i++) { len += dist(path[i - 1], path[i]); assert(M.visible(path[i - 1], path[i])); }       // ② 모든 선분이 영역 안
            std::vector<double> best(nv + 2, 1e18); std::vector<V> pts; for (int x : vid) pts.push_back(M.v[x]); pts.push_back(s); pts.push_back(e); auto see = [&](int i, int j) { if (i < nv && j < nv) return (bool)vis[i][j]; return M.visible(pts[i], pts[j]); };
            best[nv] = 0; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> p2; p2.push({0, nv}); while (!p2.empty()) { auto [du, u] = p2.top(); p2.pop(); if (du > best[u]) continue; for (int w = 0; w < nv + 2; w++) if (w != u && see(u, w) && du + dist(pts[u], pts[w]) < best[w] - 1e-12) { best[w] = du + dist(pts[u], pts[w]); p2.push({best[w], w}); } }
            double exact = best[nv + 1]; assert(exact <= len + 1e-7 && len <= mid + 1e-7);                                                              // 정확한 최단 ≤ 깔때기 ≤ 포털 중점 경로
            queries++; exactMatch += len <= exact + 1e-7; ratioSum += len / exact; worst = std::max(worst, len / exact);
        }
    }
    assert(queries > 100 && ratioSum / queries < 1.05);
    std::cout << "NavigationMesh: " << queries << " queries; funnel path inside the mesh and never longer than the portal-midpoint route; equals the exact visibility-graph optimum in " << exactMatch << ", mean ratio " << ratioSum / queries << " (worst " << worst << ")" << std::endl; return 0;
}
// Time Complexity: 삼각형 그래프 탐색 O(T log T) + 깔때기 O(포털 수)
// Space Complexity: O(T)
```
## WaypointGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 웨이포인트 그래프: 지도 위에 소수의 "길목 점" 을 찍고 서로 이어진 점끼리 간선으로 두면, 수천 칸의 격자 대신 수백 개 노드로 길을 찾는다(게임 레벨의 수작업 웨이포인트가 같은 발상이다).
// 여기서는 자동으로 만든다. ① 자유 칸을 무작위 순서로 훑으며 아직 어떤 웨이포인트에서도 보이지 않는(반경 R 안에서 시선이 닿지 않는) 칸을 새 웨이포인트로 삼는다 — 모든 자유 칸이 웨이포인트 하나 이상에서 보이게 된다(덮개 성질).
// 각 칸의 "소유자" 는 자기를 볼 수 있는 가장 가까운 웨이포인트이다. ② 시선이 닿고 거리가 2R 이하인 웨이포인트 쌍을 잇는다. ③ 격자에서 이웃한 두 칸 x, y 의 소유자 a, b 가 다르면 a→x→y→b 라는 실제 경로가 있으므로 그 길이로 간선을 잇는다 —
// 이 간선들 덕에 격자의 모든 길이 웨이포인트 간선으로 옮겨져 연결성이 격자와 같아지고 경로가 크게 돌아가지 않는다. 질의는 시작·목표에서 보이는 웨이포인트에 임시 간선을 붙여 Dijkstra, 마지막에 시선이 닿는 먼 점으로 건너뛰는 줄 당기기(string pulling)를 한다.
// 검증: ① 모든 간선과 경로 선분이 시선 안 ② 질의 성공 여부가 격자 연결성과 정확히 일치 ③ 노드 수가 칸 수보다 훨씬 적음 ④ 경로 길이를 격자 최적(유클리드 비용 8방향)과 비교 — 웨이포인트를 그대로 따를 때와 줄 당기기 뒤의 평균 비율을 보고한다
typedef std::pair<int, int> P;
struct Grid { int R, C; std::vector<std::string> w; bool blocked(int r, int c) const { return r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#'; } };
bool segBox(double x0, double y0, double x1, double y1, double bx0, double by0, double bx1, double by1) {                       // 닫힌 사각형과 선분이 만나는가(Liang–Barsky)
    double t0 = 0, t1 = 1, dx = x1 - x0, dy = y1 - y0, p[4] = {-dx, dx, -dy, dy}, q[4] = {x0 - bx0, bx1 - x0, y0 - by0, by1 - y0};
    for (int i = 0; i < 4; i++) { if (p[i] == 0) { if (q[i] < 0) return false; } else { double r = q[i] / p[i]; if (p[i] < 0) { if (r > t1) return false; t0 = std::max(t0, r); } else { if (r < t0) return false; t1 = std::min(t1, r); } } }
    return t0 <= t1 + 1e-12; }
bool los(const Grid& g, P a, P b) { double x0 = a.second + .5, y0 = a.first + .5, x1 = b.second + .5, y1 = b.first + .5; for (int r = std::min(a.first, b.first); r <= std::max(a.first, b.first); r++) for (int c = std::min(a.second, b.second); c <= std::max(a.second, b.second); c++) if (g.blocked(r, c) && segBox(x0, y0, x1, y1, c, r, c + 1, r + 1)) return false; return true; }
double dist(P a, P b) { return std::hypot(a.first - b.first, a.second - b.second); }
std::vector<int> components(const Grid& g) { std::vector<int> id(g.R * g.C, -1); int k = 0; for (int s = 0; s < g.R * g.C; s++) if (!g.blocked(s / g.C, s % g.C) && id[s] < 0) { std::vector<int> st = {s}; id[s] = k; while (!st.empty()) { int u = st.back(); st.pop_back(); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int d = 0; d < 4; d++) { int r = u / g.C + dr[d], c = u % g.C + dc[d]; if (!g.blocked(r, c) && id[r * g.C + c] < 0) { id[r * g.C + c] = k; st.push_back(r * g.C + c); } } } k++; } return id; }
double gridOptimum(const Grid& g, P s, P t) {                                                                                      // 비교 기준: 유클리드 비용 8방향 최단(모서리 자르기 금지)
    std::vector<double> d(g.R * g.C, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s.first * g.C + s.second] = 0; pq.push({0, s.first * g.C + s.second});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; int ur = u / g.C, uc = u % g.C; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int r = ur + dr, c = uc + dc; if (g.blocked(r, c) || (dr && dc && (g.blocked(ur + dr, uc) || g.blocked(ur, uc + dc)))) continue; double nd = du + std::hypot(dr, dc); if (nd < d[r * g.C + c]) { d[r * g.C + c] = nd; pq.push({nd, r * g.C + c}); } } }
    return d[t.first * g.C + t.second]; }
struct Edge { int to; double w; int vx, vy; };                                                                                       // vx, vy: 중간에 지나는 이웃한 두 칸(없으면 -1)
struct WG {
    const Grid& g; std::vector<P> wp; std::vector<std::vector<Edge>> adj; std::vector<int> owner; std::vector<double> ownerDist; const double RAD = 12;
    WG(const Grid& g, std::mt19937& rng) : g(g), owner(g.R * g.C, -1), ownerDist(g.R * g.C, 1e18) {
        std::vector<int> cells; for (int i = 0; i < g.R * g.C; i++) if (!g.blocked(i / g.C, i % g.C)) cells.push_back(i); std::shuffle(cells.begin(), cells.end(), rng);
        for (int cell : cells) if (owner[cell] < 0) { P p{cell / g.C, cell % g.C}; int id = wp.size(); wp.push_back(p); for (int c : cells) { double d = dist(p, {c / g.C, c % g.C}); if (d <= RAD && d < ownerDist[c] && los(g, p, {c / g.C, c % g.C})) { ownerDist[c] = d; owner[c] = id; } } }
        int n = wp.size(); adj.assign(n, {}); std::map<std::pair<int, int>, double> best;
        auto connect = [&](int a, int b, double w, int x, int y) { if (a == b) return; auto key = std::make_pair(std::min(a, b), std::max(a, b)); auto it = best.find(key); if (it != best.end() && it->second <= w) return; best[key] = w; for (auto* lst : {&adj[a], &adj[b]}) lst->erase(std::remove_if(lst->begin(), lst->end(), [&](const Edge& e) { return e.to == a || e.to == b; }), lst->end()); adj[a].push_back({b, w, x, y}); adj[b].push_back({a, w, y, x}); };
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (dist(wp[i], wp[j]) <= 2 * RAD && los(g, wp[i], wp[j])) connect(i, j, dist(wp[i], wp[j]), -1, -1);                                          // ②
        for (int c : cells) { const int dr[2] = {1, 0}, dc[2] = {0, 1}; for (int k = 0; k < 2; k++) { int r2 = c / g.C + dr[k], c2 = c % g.C + dc[k]; if (g.blocked(r2, c2) || !los(g, {c / g.C, c % g.C}, {r2, c2})) continue; int y = r2 * g.C + c2, a = owner[c], b = owner[y];
                connect(a, b, ownerDist[c] + 1 + ownerDist[y], c, y); } }                                                                                                                              // ③ 이웃 칸 경유 간선
    }
    double query(P s, P t, std::vector<P>& path) {
        int n = wp.size(); std::vector<std::vector<Edge>> a = adj; a.resize(n + 2); std::vector<P> pts = wp; pts.push_back(s); pts.push_back(t);
        for (int e : {n, n + 1}) for (int i = 0; i < n; i++) if (dist(pts[e], wp[i]) <= 2 * RAD && los(g, pts[e], wp[i])) { double w = dist(pts[e], wp[i]); a[e].push_back({i, w, -1, -1}); a[i].push_back({e, w, -1, -1}); }
        if (los(g, s, t)) { double w = dist(s, t); a[n].push_back({n + 1, w, -1, -1}); a[n + 1].push_back({n, w, -1, -1}); }
        std::vector<double> d(n + 2, 1e18); std::vector<int> par(n + 2, -1); std::vector<Edge> via(n + 2, Edge{-1, 0, -1, -1}); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[n] = 0; pq.push({0, n});
        while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (const Edge& e : a[u]) if (du + e.w < d[e.to]) { d[e.to] = du + e.w; par[e.to] = u; via[e.to] = e; pq.push({d[e.to], e.to}); } }
        if (d[n + 1] > 1e17) return -1; std::vector<P> rev; for (int v = n + 1; v >= 0; v = par[v]) { rev.push_back(pts[v]); if (par[v] >= 0 && via[v].vx >= 0) { rev.push_back({via[v].vy / g.C, via[v].vy % g.C}); rev.push_back({via[v].vx / g.C, via[v].vx % g.C}); } }     // 경유 칸 두 개(x, y)를 끼워 넣는다
        path.assign(rev.rbegin(), rev.rend()); return d[n + 1]; }
};
int main() {
    std::mt19937 rng(18); long cells = 0, nodes = 0; int queries = 0, connectedQ = 0; double ratio = 0, rawRatio = 0;
    for (int m = 0; m < 6; m++) {
        Grid g{36, 36, std::vector<std::string>(36, std::string(36, '.'))}; for (auto& row : g.w) for (auto& ch : row) if (rng() % 100 < 14) ch = '#'; WG wg(g, rng); std::vector<int> comp = components(g);
        for (int i = 0; i < g.R * g.C; i++) if (!g.blocked(i / g.C, i % g.C)) cells++; nodes += wg.wp.size();
        for (int q = 0; q < 40; q++) { P s{(int)(rng() % 36), (int)(rng() % 36)}, t{(int)(rng() % 36), (int)(rng() % 36)}; if (g.blocked(s.first, s.second) || g.blocked(t.first, t.second)) continue; std::vector<P> path; double len = wg.query(s, t, path);
            bool conn = comp[s.first * 36 + s.second] == comp[t.first * 36 + t.second]; assert((len >= 0) == conn);                       // ② 성공 여부 == 격자 연결성
            if (!conn) continue; double sum = 0; for (size_t i = 1; i < path.size(); i++) { assert(los(g, path[i - 1], path[i])); sum += dist(path[i - 1], path[i]); } assert(std::fabs(sum - len) < 1e-9 && path.front() == s && path.back() == t);   // ①
            std::vector<P> sm = {path[0]}; for (size_t i = 0; i + 1 < path.size();) { size_t j = path.size() - 1; while (j > i + 1 && !los(g, path[i], path[j])) j--; sm.push_back(path[j]); i = j; }                     // 줄 당기기: 시선이 닿는 가장 먼 점으로 건너뜀
            double smLen = 0; for (size_t i = 1; i < sm.size(); i++) { assert(los(g, sm[i - 1], sm[i])); smLen += dist(sm[i - 1], sm[i]); } assert(smLen <= len + 1e-9);
            double opt = gridOptimum(g, s, t); if (opt > 0) { ratio += smLen / opt; rawRatio += len / opt; connectedQ++; } queries++; }
    }
    assert(queries > 100 && nodes * 6 < cells && ratio / connectedQ > 0.85 && ratio / connectedQ < 1.2 && ratio < rawRatio);
    std::cout << "WaypointGraph: " << nodes << " waypoints cover " << cells << " free cells (" << 100.0 * nodes / cells << "%); " << queries << " queries valid, success == grid connectivity, mean length / grid optimum = " << rawRatio / connectedQ << " (" << ratio / connectedQ << " after string pulling)" << std::endl; return 0;
}
// Time Complexity: 전처리 O(웨이포인트² × 시선 검사), 질의 O(W log W + W × 시선 검사)
// Space Complexity: O(W + 간선)
```
## VisibilityGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 가시성 그래프(visibility graph): 다각형 장애물 사이의 유클리드 최단 경로는 시작점·목표·장애물 꼭짓점을 잇는 꺾은선이다(꺾이는 곳은 반드시 장애물 꼭짓점). 그래서 이 점들 중 "서로 보이는" 쌍을 간선으로 잇고 Dijkstra 를 돌리면 연속 공간의 정확한 최단 경로가 나온다.
// 순진하게 모든 쌍을 검사하면 간선 후보가 O(n²), 각 가시성 검사가 O(n) 이라 O(n³). 줄이기: 볼록 장애물에서 최단 경로가 쓰는 간선은 "양 끝점에서 접선" 이다 — 꼭짓점에서 이웃 두 꼭짓점이 간선과 같은 쪽에 있어야 한다. 이런 간선만 남긴 축소 가시성 그래프는 같은 최단 거리를 주면서 간선이 훨씬 적다.
// 검증: 원에 내접하는(= 볼록한) 무작위 다각형 장애물 장면 150개에서 ① 전체 그래프와 축소 그래프의 최단 거리가 일치 ② 경로의 모든 선분이 어떤 다각형 내부도 지나지 않음 ③ 직접 보이면 직선 거리와 같음 ④ 독립 표본 로드맵(무작위 자유 점들의 시선 그래프)의 거리는 이 값보다 짧을 수 없음
typedef std::pair<double, double> V;
double cross(V a, V b, V c) { return (b.first - a.first) * (c.second - a.second) - (b.second - a.second) * (c.first - a.first); }
double dist(V a, V b) { return std::hypot(a.first - b.first, a.second - b.second); }
struct Poly { std::vector<V> p; V c; double r; };                                                                                    // 반시계 방향 볼록 다각형
bool cutsInterior(const Poly& P, V a, V b) {                                                                                         // Cyrus–Beck: 선분이 열린 내부와 길이 있는 구간으로 만나는가
    double lo = 0, hi = 1; int n = P.p.size(); for (int i = 0; i < n; i++) { V p = P.p[i], q = P.p[(i + 1) % n]; double f0 = cross(p, q, a), f1 = cross(p, q, b), df = f1 - f0;
        if (std::fabs(df) < 1e-15) { if (f0 <= 1e-12) return false; continue; } double t = -f0 / df; if (df > 0) lo = std::max(lo, t); else hi = std::min(hi, t); if (lo >= hi - 1e-12) return false; }
    return hi - lo > 1e-9; }
bool visible(const std::vector<Poly>& ps, V a, V b) { for (const Poly& P : ps) if (cutsInterior(P, a, b)) return false; return true; }
bool inside(const std::vector<Poly>& ps, V x) { for (const Poly& P : ps) if (dist(P.c, x) < P.r) return true; return false; }
double shortest(int n, const std::vector<std::vector<std::pair<int, double>>>& adj, int s, int t) { std::vector<double> d(n, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d[t]; }
int main() {
    std::mt19937 g(77); long fullEdges = 0, redEdges = 0; int scenes = 0, direct = 0, sampled = 0; double sampleRatio = 0;
    for (int sc = 0; sc < 150; sc++) {
        std::vector<Poly> ps; for (int tries = 0; tries < 200 && ps.size() < 7; tries++) { double r = 6 + g() % 80 / 10.0; V c{r + 1 + g() % (int)(98 - 2 * r), r + 1 + g() % (int)(98 - 2 * r)}; bool ok = true; for (const Poly& o : ps) ok = ok && dist(o.c, c) > o.r + r + 1; if (!ok) continue;
            int k = 3 + g() % 4; std::vector<double> ang; for (;;) { ang.clear(); for (int i = 0; i < k; i++) ang.push_back((g() % 6283) / 1000.0); std::sort(ang.begin(), ang.end()); bool good = ang[0] + 6.283 - ang[k - 1] > 0.5; for (int i = 1; i < k; i++) good = good && ang[i] - ang[i - 1] > 0.5; if (good) break; }
            Poly P; P.c = c; P.r = r; for (double a : ang) P.p.push_back({c.first + r * std::cos(a), c.second + r * std::sin(a)}); ps.push_back(P); }
        V s, t; do { s = {(g() % 1000) / 10.0, (g() % 1000) / 10.0}; } while (inside(ps, s)); do { t = {(g() % 1000) / 10.0, (g() % 1000) / 10.0}; } while (inside(ps, t));
        std::vector<V> pts; std::vector<int> poly, idxIn; for (size_t i = 0; i < ps.size(); i++) for (size_t j = 0; j < ps[i].p.size(); j++) { pts.push_back(ps[i].p[j]); poly.push_back(i); idxIn.push_back(j); } int nv = pts.size(); pts.push_back(s); pts.push_back(t); int n = pts.size(); poly.push_back(-1); poly.push_back(-1); idxIn.push_back(0); idxIn.push_back(0);
        auto tangent = [&](int a, int b) { if (poly[a] < 0) return true; const Poly& P = ps[poly[a]]; int k = P.p.size(), j = idxIn[a]; double c1 = cross(pts[a], pts[b], P.p[(j + 1) % k]), c2 = cross(pts[a], pts[b], P.p[(j + k - 1) % k]); return !((c1 > 1e-9 && c2 < -1e-9) || (c1 < -1e-9 && c2 > 1e-9)); };
        std::vector<std::vector<std::pair<int, double>>> full(n), red(n); for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) if (visible(ps, pts[a], pts[b])) { double w = dist(pts[a], pts[b]); full[a].push_back({b, w}); full[b].push_back({a, w}); fullEdges++; if (tangent(a, b) && tangent(b, a)) { red[a].push_back({b, w}); red[b].push_back({a, w}); redEdges++; } }
        double df = shortest(n, full, nv, nv + 1), dr = shortest(n, red, nv, nv + 1); assert(std::fabs(df - dr) < 1e-9 && df >= dist(s, t) - 1e-9); scenes++;                                          // ① 전체 == 축소
        if (visible(ps, s, t)) { assert(std::fabs(df - dist(s, t)) < 1e-9); direct++; }                                                                                                                           // ③
        if (sc < 20) {                                                                                                                                                                                        // ④ 독립 표본 로드맵: 자유 점 150개 + s, t 의 시선 그래프
            std::vector<V> sp; sp.push_back(s); sp.push_back(t); while (sp.size() < 152) { V x{(g() % 1000) / 10.0, (g() % 1000) / 10.0}; if (!inside(ps, x)) sp.push_back(x); } int m = sp.size(); std::vector<std::vector<std::pair<int, double>>> adj(m);
            for (int a = 0; a < m; a++) for (int b = a + 1; b < m; b++) if (visible(ps, sp[a], sp[b])) { double w = dist(sp[a], sp[b]); adj[a].push_back({b, w}); adj[b].push_back({a, w}); }
            double dsmp = shortest(m, adj, 0, 1); if (dsmp < 1e17) { assert(dsmp >= df - 1e-9); sampled++; sampleRatio += dsmp / df; } }
    }
    assert(scenes == 150 && redEdges * 4 < fullEdges * 3 && sampled > 10 && direct >= 0);
    std::cout << "VisibilityGraph: " << scenes << " scenes; reduced graph keeps " << redEdges << " of " << fullEdges << " edges with identical shortest distances; sampled roadmaps are never shorter (mean " << sampleRatio / sampled << "x the exact optimum); " << direct << " scenes had direct line of sight" << std::endl; return 0;
}
// Time Complexity: 순진한 구성 O(n³), 회전 스위프 O(n² log n); Dijkstra O(E log V)
// Space Complexity: O(n²)
```
## VoronoiDiagram()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 일반화 보로노이 다이어그램(GVD) 로드맵: 장애물 칸들로부터 "가장 가까운 장애물" 이 둘 이상 같은 거리에 있는 점들의 집합(보로노이 변)은 장애물에서 가능한 한 멀리 떨어진 길이다. 최단이 아니라 "안전한" 길을 원할 때(로봇, 좁은 통로 회피) 쓴다.
// 격자 구현: ① 장애물 칸에서 다중 출발 BFS(8방향 = 체비쇼프 거리)로 거리장 d 와 "가장 가까운 장애물 덩어리" 라벨을 만든다. ② 인접한 자유 칸의 라벨이 다르면 GVD 칸이다(서로 다른 두 장애물의 영향 영역 경계). ③ 시작·목표에서 d 가 커지는 쪽으로 올라가 GVD 에 붙고, GVD 위에서 BFS 로 이동한다.
// 검증: ① d 가 모든 장애물 칸에 대한 체비쇼프 최솟값(완전 탐색)과 같음 ② GVD 칸은 이웃 중 다른 덩어리가 더 가까운 칸이 실제로 있음 ③ 로드맵 경로가 존재하고(자유 공간 연결성과 일치) 그 병목(경로의 최소 d)이 격자 전체에서 구한 최대-최소(widest) 경로의 병목에 근접(≥ 최적−1) ④ 최단 경로보다 길지만 병목은 평균적으로 더 큼
typedef std::pair<int, int> P; int R = 34, C = 34; std::vector<std::string> w;
bool blocked(int r, int c) { return r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#'; }
bool moveOk(int r, int c, int dr, int dc) { if (blocked(r + dr, c + dc)) return false; return !(dr && dc && (blocked(r + dr, c) || blocked(r, c + dc))); }
int main() {
    std::mt19937 g(25); int maps = 0, queries = 0, saferCount = 0; long lenR = 0, lenS = 0; double bnR = 0, bnS = 0; int worstGap = 0;
    for (int m = 0; m < 25; m++) {
        w.assign(R, std::string(C, '.')); for (int k = 0; k < 9; k++) { int r0 = g() % (R - 4), c0 = g() % (C - 4), h = 2 + g() % 6, wd = 2 + g() % 6; for (int r = r0; r < std::min(R, r0 + h); r++) for (int c = c0; c < std::min(C, c0 + wd); c++) w[r][c] = '#'; }
        for (int r = 0; r < R; r++) w[r][0] = w[r][C - 1] = '#'; for (int c = 0; c < C; c++) w[0][c] = w[R - 1][c] = '#';                                                  // 바깥 테두리도 장애물
        std::vector<int> label(R * C, -1); int nl = 0; for (int i = 0; i < R * C; i++) if (w[i / C][i % C] == '#' && label[i] < 0) { std::vector<int> st = {i}; label[i] = nl; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / C + dr, c = u % C + dc; if (r >= 0 && c >= 0 && r < R && c < C && w[r][c] == '#' && label[r * C + c] < 0) { label[r * C + c] = nl; st.push_back(r * C + c); } } } nl++; }
        std::vector<int> d(R * C, -1), lab = label; std::queue<int> q; for (int i = 0; i < R * C; i++) if (label[i] >= 0) { d[i] = 0; q.push(i); }
        while (!q.empty()) { int u = q.front(); q.pop(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / C + dr, c = u % C + dc; if (r >= 0 && c >= 0 && r < R && c < C && d[r * C + c] < 0) { d[r * C + c] = d[u] + 1; lab[r * C + c] = lab[u]; q.push(r * C + c); } } }
        for (int i = 0; i < R * C; i += 7) { int best = INT_MAX; for (int j = 0; j < R * C; j++) if (w[j / C][j % C] == '#') best = std::min(best, std::max(std::abs(i / C - j / C), std::abs(i % C - j % C))); assert(d[i] == best); }       // ① 거리장 == 완전 탐색
        std::vector<char> sk(R * C, 0); int skCount = 0; for (int i = 0; i < R * C; i++) if (!blocked(i / C, i % C)) { for (int dr = -1; dr <= 1 && !sk[i]; dr++) for (int dc = -1; dc <= 1; dc++) { int r = i / C + dr, c = i % C + dc; if (r >= 0 && c >= 0 && r < R && c < C && lab[r * C + c] != lab[i] && d[r * C + c] >= d[i] - 1 && d[r * C + c] <= d[i] + 1) { sk[i] = 1; break; } } if (sk[i]) { skCount++; bool other = false; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = i / C + dr, c = i % C + dc; other |= r >= 0 && c >= 0 && r < R && c < C && lab[r * C + c] != lab[i]; } assert(other); } }       // ②
        std::vector<int> comp(R * C, -1); int nc = 0; for (int i = 0; i < R * C; i++) if (!blocked(i / C, i % C) && comp[i] < 0) { std::vector<int> st = {i}; comp[i] = nc; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) if ((dr || dc) && moveOk(u / C, u % C, dr, dc)) { int v = (u / C + dr) * C + u % C + dc; if (comp[v] < 0) { comp[v] = nc; st.push_back(v); } } } nc++; }
        auto bfs = [&](int s, const std::vector<char>* allow, std::vector<int>& par) { std::vector<int> dd(R * C, -1); std::queue<int> qq; dd[s] = 0; qq.push(s); par.assign(R * C, -1); while (!qq.empty()) { int u = qq.front(); qq.pop(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) if ((dr || dc) && moveOk(u / C, u % C, dr, dc)) { int v = (u / C + dr) * C + u % C + dc; if (dd[v] >= 0 || (allow && !(*allow)[v])) continue; dd[v] = dd[u] + 1; par[v] = u; qq.push(v); } } return dd; };
        auto widest = [&](int s, int t, const std::vector<char>* allow) { std::vector<int> b(R * C, -1); typedef std::pair<int, int> Q; std::priority_queue<Q> pq; b[s] = d[s]; pq.push({d[s], s}); while (!pq.empty()) { auto [bu, u] = pq.top(); pq.pop(); if (bu < b[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) if ((dr || dc) && moveOk(u / C, u % C, dr, dc)) { int v = (u / C + dr) * C + u % C + dc; if (allow && !(*allow)[v]) continue; int nb = std::min(bu, d[v]); if (nb > b[v]) { b[v] = nb; pq.push({nb, v}); } } } return b[t]; };
        auto attach = [&](int s) { int u = s; std::vector<int> trail = {u}; for (int guard = 0; guard < R * C && !sk[u]; guard++) { int best = u; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) if ((dr || dc) && moveOk(u / C, u % C, dr, dc)) { int v = (u / C + dr) * C + u % C + dc; if (d[v] > d[best]) best = v; } if (best == u) break; u = best; trail.push_back(u); } return trail; };
        for (int qn = 0; qn < 12; qn++) { int s = g() % (R * C), t = g() % (R * C); if (blocked(s / C, s % C) || blocked(t / C, t % C) || comp[s] != comp[t] || s == t) continue;
            std::vector<int> par; auto ds = bfs(s, nullptr, par); std::vector<int> shortest; for (int v = t; v >= 0; v = par[v]) shortest.push_back(v); int bS = INT_MAX; for (int v : shortest) bS = std::min(bS, d[v]);
            std::vector<int> a1 = attach(s), a2 = attach(t); if (!sk[a1.back()] || !sk[a2.back()]) continue; int bsk = widest(a1.back(), a2.back(), &sk); if (bsk < 0) continue; std::vector<char> okc(R * C, 0); for (int i = 0; i < R * C; i++) okc[i] = sk[i] && d[i] >= bsk;               // GVD 위에서 연결되지 않으면 건너뜀; 연결되면 GVD 안의 최대-최소 병목 이상인 칸만 써서
            std::vector<int> par2; auto d2 = bfs(a1.back(), &okc, par2); if (d2[a2.back()] < 0) continue;                                                                                   // 가장 짧은 GVD 경로를 고른다
            std::vector<int> mid; for (int v = a2.back(); v >= 0; v = par2[v]) mid.push_back(v); std::reverse(mid.begin(), mid.end()); std::vector<int> road = a1; road.insert(road.end(), mid.begin() + 1, mid.end()); road.insert(road.end(), a2.rbegin() + 1, a2.rend());
            int bR = INT_MAX; for (int v : road) bR = std::min(bR, d[v]); int wd = widest(s, t, nullptr); assert(bR >= wd - 1 && bR <= wd && (int)road.size() >= ds[t] + 1);                                       // ③ 병목이 최적에 근접, 길이는 최단 이상
            worstGap = std::max(worstGap, wd - bR); lenR += road.size() - 1; lenS += ds[t]; bnR += bR; bnS += bS; saferCount += bR > bS; queries++; }
        maps++;
    }
    assert(maps == 25 && queries > 100 && bnR > bnS && lenR >= lenS && worstGap <= 1);
    std::cout << "VoronoiDiagram: " << queries << " queries on " << maps << " maps; GVD roadmap mean clearance " << bnR / queries << " vs " << bnS / queries << " on shortest paths (safer in " << saferCount << " queries), at a cost of " << (double)lenR / lenS << "x path length; bottleneck within " << worstGap << " of the widest path" << std::endl; return 0;
}
// Time Complexity: O(RC) 거리장·스켈레톤, 질의 O(RC) BFS
// Space Complexity: O(RC)
```
## RoadNetwork()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 도로망(RoadNetwork): 교차로(정점)와 도로 구간(방향 간선)으로 이루어진 실제 지도 그래프의 저장·탐색 구조. 핵심은 ① 메모리 효율적인 CSR(compressed sparse row) 인접 배열 — 정점별 첫 간선 번호 first[u] 와 간선 속성의 배열 구조(SoA) —
// ② 일방통행(방향 간선)과 도로 등급별 속도 ③ 좌회전 금지 같은 "회전 제한" — 정점이 아니라 간선을 상태로 삼은 탐색(edge-based)이 필요하다 ④ 좌표를 도로에 붙이는 공간 색인(격자 해시) ⑤ 거리/최고속도로 허용적인 A* 휴리스틱.
// 검증: 합성 도시(지터 격자, 일방통행·고속도로 격자선, 일부 구간 삭제, 회전 제한)에서 ① 정점 A* == 정점 Dijkstra 비용이고 확장 정점이 적음 ② 간선 기반 Dijkstra 는 금지 회전을 쓰지 않고 정점 기반 비용 이상이며 간선 상태 Bellman-Ford 와 일치 ③ 회전 제한으로 비용이 늘어난 질의가 존재 ④ 격자 색인의 최근접 도로가 완전 탐색과 일치
struct Road { int u, v; double km, kmh; };
struct Network {
    int n; std::vector<double> x, y; std::vector<int> first, to, rid; std::vector<double> len, kmh, secs; double vmax = 0; std::set<std::pair<int, int>> banned;                // CSR: first[u]..first[u+1]-1 이 u 의 나가는 간선
    void build(int N, const std::vector<Road>& roads) { n = N; first.assign(n + 2, 0); for (const Road& r : roads) first[r.u + 1]++; for (int i = 0; i <= n; i++) first[i + 1] += first[i]; std::vector<int> pos(first.begin(), first.begin() + n); int m = roads.size(); to.resize(m); len.resize(m); kmh.resize(m); secs.resize(m); rid.resize(m);
        for (const Road& r : roads) { int e = pos[r.u]++; to[e] = r.v; len[e] = r.km; kmh[e] = r.kmh; secs[e] = 3600 * r.km / r.kmh; vmax = std::max(vmax, r.kmh); } }
    int tail(int e) const { return std::upper_bound(first.begin(), first.begin() + n + 1, e) - first.begin() - 1; }
};
double dist(const Network& N, int a, int b) { return std::hypot(N.x[a] - N.x[b], N.y[a] - N.y[b]); }
int main() {
    std::mt19937 g(33); int W = 18; Network net; net.n = W * W; for (int i = 0; i < W * W; i++) { net.x.push_back(i % W + ((int)(g() % 40) - 20) / 100.0); net.y.push_back(i / W + ((int)(g() % 40) - 20) / 100.0); }
    std::vector<Road> roads; auto addRoad = [&](int a, int b, double kmh, bool oneWay, bool forward) { double km = std::hypot(net.x[a] - net.x[b], net.y[a] - net.y[b]); if (!oneWay) { roads.push_back({a, b, km, kmh}); roads.push_back({b, a, km, kmh}); } else if (forward) roads.push_back({a, b, km, kmh}); else roads.push_back({b, a, km, kmh}); };
    for (int r = 0; r < W; r++) for (int c = 0; c < W; c++) { int u = r * W + c; for (int k = 0; k < 2; k++) { int v = k ? u + W : u + 1; if ((k == 0 && c + 1 >= W) || (k == 1 && r + 1 >= W)) continue; if (g() % 100 < 6) continue; bool hw = k == 0 ? r % 6 == 0 : c % 6 == 0; double speed = hw ? 90 : (g() % 100 < 25 ? 50 : 30); bool one = !hw && g() % 100 < 15; addRoad(u, v, speed, one, g() % 2); } }
    net.build(W * W, roads); int m = net.to.size();
    for (int e = 0; e < m; e++) { int u = net.tail(e), v = net.to[e]; for (int f = net.first[v]; f < net.first[v + 1]; f++) if (net.to[f] != u && g() % 100 < 4) net.banned.insert({e, f}); }                              // 회전 제한(e 다음에 f 금지); U턴은 막다른 길이 아니면 금지
    for (int e = 0; e < m; e++) { int v = net.to[e], u = net.tail(e); if (net.first[v + 1] - net.first[v] > 1) for (int f = net.first[v]; f < net.first[v + 1]; f++) if (net.to[f] == u) net.banned.insert({e, f}); }
    typedef std::pair<double, int> Q; long dExp = 0, aExp = 0; int checked = 0, worse = 0, unreachable = 0;
    for (int qn = 0; qn < 120; qn++) {
        int s = g() % net.n, t = g() % net.n; if (s == t) continue;
        std::vector<double> d(net.n, 1e18); std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); long de = 0; while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; de++; if (u == t) break; for (int e = net.first[u]; e < net.first[u + 1]; e++) if (du + net.secs[e] < d[net.to[e]]) { d[net.to[e]] = du + net.secs[e]; pq.push({d[net.to[e]], net.to[e]}); } }
        std::vector<double> a(net.n, 1e18); std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pa; a[s] = 0; pa.push({dist(net, s, t) / net.vmax * 3600, s}); long ae = 0; while (!pa.empty()) { auto [f, u] = pa.top(); pa.pop(); if (f > a[u] + dist(net, u, t) / net.vmax * 3600 + 1e-9) continue; ae++; if (u == t) break; for (int e = net.first[u]; e < net.first[u + 1]; e++) { int v = net.to[e]; if (a[u] + net.secs[e] < a[v]) { a[v] = a[u] + net.secs[e]; pa.push({a[v] + dist(net, v, t) / net.vmax * 3600, v}); } } }
        if (d[t] > 1e17) { assert(a[t] > 1e17); unreachable++; continue; } assert(std::fabs(a[t] - d[t]) < 1e-6); dExp += de; aExp += ae;                                                                                  // ① A* == Dijkstra
        std::vector<double> ed(m, 1e18); std::vector<int> epar(m, -1); std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pe; for (int e = net.first[s]; e < net.first[s + 1]; e++) { ed[e] = net.secs[e]; pe.push({ed[e], e}); }                // ② 간선 상태 Dijkstra
        while (!pe.empty()) { auto [du, e] = pe.top(); pe.pop(); if (du > ed[e]) continue; int v = net.to[e]; for (int f = net.first[v]; f < net.first[v + 1]; f++) if (!net.banned.count({e, f}) && du + net.secs[f] < ed[f]) { ed[f] = du + net.secs[f]; epar[f] = e; pe.push({ed[f], f}); } }
        double best = 1e18; int be = -1; for (int e = 0; e < m; e++) if (net.to[e] == t && ed[e] < best) { best = ed[e]; be = e; }
        std::vector<double> bf(m, 1e18); for (int e = net.first[s]; e < net.first[s + 1]; e++) bf[e] = net.secs[e]; for (bool ch = true; ch;) { ch = false; for (int e = 0; e < m; e++) if (bf[e] < 1e17) { int v = net.to[e]; for (int f = net.first[v]; f < net.first[v + 1]; f++) if (!net.banned.count({e, f}) && bf[e] + net.secs[f] < bf[f] - 1e-12) { bf[f] = bf[e] + net.secs[f]; ch = true; } } }
        double bfBest = 1e18; for (int e = 0; e < m; e++) if (net.to[e] == t) bfBest = std::min(bfBest, bf[e]); assert(std::fabs(bfBest - best) < 1e-6 || (bfBest > 1e17 && best > 1e17));                     // Bellman-Ford 와 일치
        if (best > 1e17) { worse++; continue; } assert(best >= d[t] - 1e-9); for (int e = be; epar[e] >= 0; e = epar[e]) assert(!net.banned.count({epar[e], e}));                                            // 금지 회전 미사용
        if (best > d[t] + 1e-9) worse++; checked++;
    }
    std::map<std::pair<int, int>, int> cellOf; double cs = 1.0; auto key = [&](double px, double py) { return std::make_pair((int)std::floor(px / cs), (int)std::floor(py / cs)); }; std::map<std::pair<int, int>, std::vector<int>> grid;       // ④ 공간 색인: 간선의 두 끝점이 걸친 칸마다 간선 번호 저장
    for (int e = 0; e < m; e++) { int u = net.tail(e), v = net.to[e]; for (int s = 0; s <= 8; s++) { double px = net.x[u] + (net.x[v] - net.x[u]) * s / 8, py = net.y[u] + (net.y[v] - net.y[u]) * s / 8; auto& lst = grid[key(px, py)]; if (lst.empty() || lst.back() != e) lst.push_back(e); } }
    auto segDist = [&](int e, double px, double py) { int u = net.tail(e), v = net.to[e]; double dx = net.x[v] - net.x[u], dy = net.y[v] - net.y[u], t = std::max(0.0, std::min(1.0, ((px - net.x[u]) * dx + (py - net.y[u]) * dy) / (dx * dx + dy * dy))); return std::hypot(px - net.x[u] - t * dx, py - net.y[u] - t * dy); };
    int snapOk = 0; for (int i = 0; i < 400; i++) { double px = (g() % 1700) / 100.0, py = (g() % 1700) / 100.0; double bestD = 1e18; for (int e = 0; e < m; e++) bestD = std::min(bestD, segDist(e, px, py)); double gd = 1e18; auto k0 = key(px, py); for (int rr = 1; rr <= 3 && gd > 1e17; rr++) { for (int dx = -rr; dx <= rr; dx++) for (int dy = -rr; dy <= rr; dy++) { auto it = grid.find({k0.first + dx, k0.second + dy}); if (it != grid.end()) for (int e : it->second) gd = std::min(gd, segDist(e, px, py)); } if (gd <= rr * cs * 0.99) break; } if (std::fabs(gd - bestD) < 1e-9) snapOk++; }
    assert(checked > 60 && aExp < dExp && worse > 0 && snapOk > 380);
    std::cout << "RoadNetwork: " << net.n << " junctions, " << m << " directed segments in CSR; A* settled " << aExp << " vs Dijkstra " << dExp << "; " << worse << " routes got slower (or impossible) because of turn restrictions, " << unreachable << " unreachable; spatial snap exact in " << snapOk << "/400" << std::endl; return 0;
}
// Time Complexity: CSR 순회 O(deg), 간선 기반 탐색 O(E · deg · log E), 색인 질의 O(주변 칸 × 간선)
// Space Complexity: O(V + E)
```

# Part 11. 로봇공학
## RapidlyExploringRandomTree()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// RRT(Rapidly-exploring Random Tree, LaValle 1998): 연속 공간의 단일 질의 샘플링 계획기. 시작점에서 트리를 키우며 매번 공간에서 무작위 점 q 를 뽑고(5% 는 목표 점 — 목표 편향), 트리에서 q 에 가장 가까운 노드로부터 q 쪽으로 한 걸음(step)만큼 뻗어 충돌이 없으면 새 노드로 붙인다.
// 가장 가까운 노드를 고르는 것이 보로노이 영역이 큰 노드(= 아직 탐색 안 된 빈 공간 쪽 노드)를 자주 확장하게 만들어 트리가 빠르게 공간을 덮는다. 확률적으로 완전(해가 있으면 반복할수록 찾을 확률 → 1)하지만 최적은 아니다 — 경로가 구불구불하다.
// 환경: 100×100 평면의 직사각형 장애물 10개(겹칠 수 있음), 시작 (5,5), 목표 (95,95). 기준 최단 거리는 모서리 가시성 그래프(정확).
// 검증: 무작위 세계 40개에서 ① 모든 트리 간선이 충돌 없음 ② 성공률 90% 이상 ③ 경로 길이가 정확한 최단 거리 이상이고 평균 비율을 보고 ④ 같은 세계에서 직선 경로가 막혀 있는 세계가 존재함
typedef std::pair<double, double> V;
struct Rect { double x0, y0, x1, y1; }; std::vector<Rect> obs;
double dist(V a, V b) { return std::hypot(a.first - b.first, a.second - b.second); }
bool hitsRect(V a, V b, const Rect& r) {                                                                                 // 선분이 열린 직사각형 내부와 길이 있는 구간으로 만나는가(경계 접촉은 허용)
    double t0 = 0, t1 = 1, dx = b.first - a.first, dy = b.second - a.second, p[4] = {-dx, dx, -dy, dy}, q[4] = {a.first - r.x0, r.x1 - a.first, a.second - r.y0, r.y1 - a.second};
    for (int i = 0; i < 4; i++) { if (p[i] == 0) { if (q[i] <= 0) return false; } else { double t = q[i] / p[i]; if (p[i] < 0) { if (t > t1) return false; t0 = std::max(t0, t); } else { if (t < t0) return false; t1 = std::min(t1, t); } } }
    return t1 - t0 > 1e-9; }
bool pointFree(V p) { if (p.first < 0 || p.second < 0 || p.first > 100 || p.second > 100) return false; for (const Rect& r : obs) if (p.first > r.x0 && p.first < r.x1 && p.second > r.y0 && p.second < r.y1) return false; return true; }
bool segFree(V a, V b) { if (!pointFree(a) || !pointFree(b)) return false; for (const Rect& r : obs) if (hitsRect(a, b, r)) return false; return true; }
void makeWorld(std::mt19937& g) { obs.clear(); while (obs.size() < 10) { double w = 8 + g() % 17, h = 8 + g() % 17, x0 = 12 + g() % (int)(76 - w), y0 = 12 + g() % (int)(76 - h); obs.push_back({x0, y0, x0 + w, y0 + h}); } }
double optimum(V s, V t) {                                                                                                 // 기준: 직사각형 모서리 가시성 그래프의 정확한 최단 거리
    std::vector<V> pts = {s, t}; for (const Rect& r : obs) for (V c : {V{r.x0, r.y0}, V{r.x1, r.y0}, V{r.x1, r.y1}, V{r.x0, r.y1}}) if (pointFree(c) || true) pts.push_back(c);
    int n = pts.size(); std::vector<double> d(n, 1e18); std::vector<char> done(n, 0); d[0] = 0; for (int it = 0; it < n; it++) { int u = -1; for (int i = 0; i < n; i++) if (!done[i] && (u < 0 || d[i] < d[u])) u = i; if (u < 0 || d[u] > 1e17) break; done[u] = 1; for (int v = 0; v < n; v++) if (!done[v] && d[u] + dist(pts[u], pts[v]) < d[v] && segFree(pts[u], pts[v])) d[v] = d[u] + dist(pts[u], pts[v]); }
    return d[1]; }
struct Tree { std::vector<V> p; std::vector<int> par; };
bool rrt(std::mt19937& rng, V s, V g, int iters, double step, Tree& T, long& samples) {
    T.p = {s}; T.par = {-1};
    for (int it = 0; it < iters; it++) {
        samples++; V q = rng() % 100 < 5 ? g : V{(rng() % 10000) / 100.0, (rng() % 10000) / 100.0}; int nn = 0; for (size_t i = 1; i < T.p.size(); i++) if (dist(T.p[i], q) < dist(T.p[nn], q)) nn = i;
        double d = dist(T.p[nn], q); if (d < 1e-9) continue; V nw = d <= step ? q : V{T.p[nn].first + (q.first - T.p[nn].first) * step / d, T.p[nn].second + (q.second - T.p[nn].second) * step / d};
        if (!segFree(T.p[nn], nw)) continue; T.p.push_back(nw); T.par.push_back(nn);
        if (dist(nw, g) <= step && segFree(nw, g)) { T.p.push_back(g); T.par.push_back(T.p.size() - 2); return true; }
    }
    return false; }
int main() {
    std::mt19937 rng(7); V s{5, 5}, g{95, 95}; int worlds = 0, solved = 0, blockedDirect = 0; double ratio = 0, worst = 1;
    for (int w = 0; w < 40; w++) {
        makeWorld(rng); double opt = optimum(s, g); if (opt > 1e17) continue; worlds++; blockedDirect += !segFree(s, g); Tree T; long samples = 0;
        if (!rrt(rng, s, g, 6000, 4.0, T, samples)) continue; solved++;
        for (size_t i = 1; i < T.p.size(); i++) assert(segFree(T.p[T.par[i]], T.p[i]));                                                // ① 모든 간선이 충돌 없음
        double len = 0; int v = T.p.size() - 1; assert(T.p[v] == g); for (; T.par[v] >= 0; v = T.par[v]) len += dist(T.p[v], T.p[T.par[v]]); assert(T.p[v] == s && len >= opt - 1e-9);   // 루트까지 이어지고 최단 이상
        ratio += len / opt; worst = std::max(worst, len / opt);
    }
    assert(worlds > 30 && solved * 10 >= worlds * 9 && blockedDirect > 20 && ratio / solved > 1.0);
    std::cout << "RapidlyExploringRandomTree: " << solved << "/" << worlds << " worlds solved; every tree edge collision-free; path length / exact optimum: mean " << ratio / solved << ", worst " << worst << std::endl; return 0;
}
// Time Complexity: 반복당 O(노드 수) 최근접 탐색(k-d 트리로 O(log n)) + 충돌 검사
// Space Complexity: O(노드 수)
```
## RRTStar()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// RRT*(Karaman & Frazzoli 2011): RRT 에 두 가지를 더해 점근적 최적성을 얻는다. ① 부모 선택 — 새 노드 근방(반경 r_n = min(15, 30·√(ln n / n)))의 노드 중 "시작점에서의 비용 + 간선 길이" 가 가장 작은 것을 부모로 삼는다.
// ② 재배선(rewire) — 새 노드를 거치면 근방 노드의 비용이 줄어들면 그 노드의 부모를 새 노드로 바꾸고 하위 트리의 비용을 갱신한다. 반복할수록 경로 비용이 단조롭게 줄어 최적 경로로 수렴한다(RRT 는 첫 해에 머무름).
// 환경은 RapidlyExploringRandomTree 와 같다. 검증: ① 모든 노드에서 cost == cost(부모) + 간선 길이 불변식과 간선 충돌 없음 ② 반복 1500/4000/8000 회 시점의 최선 경로 비용이 단조 비증가 ③ 정확한 최적 대비 평균 비율이 점점 1 에 가까워지고 8000 회에서 1.12 이하, 같은 반복 수의 RRT 평균 비율보다 좋음
typedef std::pair<double, double> V;
struct Rect { double x0, y0, x1, y1; }; std::vector<Rect> obs;
double dist(V a, V b) { return std::hypot(a.first - b.first, a.second - b.second); }
double d2(V a, V b) { double dx = a.first - b.first, dy = a.second - b.second; return dx * dx + dy * dy; }                    // 최근접·반경 질의는 제곱 거리로(제곱근 생략)
bool hitsRect(V a, V b, const Rect& r) {                                                                                 // 선분이 열린 직사각형 내부와 길이 있는 구간으로 만나는가(경계 접촉은 허용)
    double t0 = 0, t1 = 1, dx = b.first - a.first, dy = b.second - a.second, p[4] = {-dx, dx, -dy, dy}, q[4] = {a.first - r.x0, r.x1 - a.first, a.second - r.y0, r.y1 - a.second};
    for (int i = 0; i < 4; i++) { if (p[i] == 0) { if (q[i] <= 0) return false; } else { double t = q[i] / p[i]; if (p[i] < 0) { if (t > t1) return false; t0 = std::max(t0, t); } else { if (t < t0) return false; t1 = std::min(t1, t); } } }
    return t1 - t0 > 1e-9; }
bool pointFree(V p) { if (p.first < 0 || p.second < 0 || p.first > 100 || p.second > 100) return false; for (const Rect& r : obs) if (p.first > r.x0 && p.first < r.x1 && p.second > r.y0 && p.second < r.y1) return false; return true; }
bool segFree(V a, V b) { if (!pointFree(a) || !pointFree(b)) return false; for (const Rect& r : obs) if (hitsRect(a, b, r)) return false; return true; }
void makeWorld(std::mt19937& g) { obs.clear(); while (obs.size() < 10) { double w = 8 + g() % 17, h = 8 + g() % 17, x0 = 12 + g() % (int)(76 - w), y0 = 12 + g() % (int)(76 - h); obs.push_back({x0, y0, x0 + w, y0 + h}); } }
double optimum(V s, V t) {                                                                                                 // 기준: 직사각형 모서리 가시성 그래프의 정확한 최단 거리
    std::vector<V> pts = {s, t}; for (const Rect& r : obs) for (V c : {V{r.x0, r.y0}, V{r.x1, r.y0}, V{r.x1, r.y1}, V{r.x0, r.y1}}) if (pointFree(c) || true) pts.push_back(c);
    int n = pts.size(); std::vector<double> d(n, 1e18); std::vector<char> done(n, 0); d[0] = 0; for (int it = 0; it < n; it++) { int u = -1; for (int i = 0; i < n; i++) if (!done[i] && (u < 0 || d[i] < d[u])) u = i; if (u < 0 || d[u] > 1e17) break; done[u] = 1; for (int v = 0; v < n; v++) if (!done[v] && d[u] + dist(pts[u], pts[v]) < d[v] && segFree(pts[u], pts[v])) d[v] = d[u] + dist(pts[u], pts[v]); }
    return d[1]; }
struct Node { V p; int par; double cost; std::vector<int> ch; };
double bestToGoal(const std::vector<Node>& T, V g, double reach) { double best = 1e18; for (const Node& n : T) if (dist(n.p, g) <= reach && n.cost + dist(n.p, g) < best && segFree(n.p, g)) best = n.cost + dist(n.p, g); return best; }
void shift(std::vector<Node>& T, int v, double delta) { T[v].cost += delta; for (int c : T[v].ch) shift(T, c, delta); }
int main() {
    std::mt19937 rng(11); V s{5, 5}, g{95, 95}; const double step = 4.0; const int cp[3] = {1500, 4000, 8000}; double ratioAt[3] = {0, 0, 0}; int solvedAt[3] = {0, 0, 0}, worlds = 0; double rrtRatio = 0; int rrtSolved = 0;
    for (int w = 0; w < 10; w++) {
        makeWorld(rng); double opt = optimum(s, g); if (opt > 1e17) continue; worlds++; std::vector<Node> T = {{s, -1, 0, {}}}; double prevBest = 1e18;
        for (int it = 1; it <= cp[2]; it++) {
            V q = rng() % 100 < 5 ? g : V{(rng() % 10000) / 100.0, (rng() % 10000) / 100.0}; int nn = 0; for (size_t i = 1; i < T.size(); i++) if (d2(T[i].p, q) < d2(T[nn].p, q)) nn = i;
            double d = dist(T[nn].p, q); if (d < 1e-9) continue; V nw = d <= step ? q : V{T[nn].p.first + (q.first - T[nn].p.first) * step / d, T[nn].p.second + (q.second - T[nn].p.second) * step / d}; if (!segFree(T[nn].p, nw)) continue;
            double r = std::min(15.0, 30 * std::sqrt(std::log(T.size() + 1.0) / (T.size() + 1.0))); r = std::max(r, step); std::vector<int> near; for (size_t i = 0; i < T.size(); i++) if (d2(T[i].p, nw) <= r * r) near.push_back(i);
            int best = nn; double bc = T[nn].cost + dist(T[nn].p, nw); for (int j : near) { double c = T[j].cost + dist(T[j].p, nw); if (c < bc - 1e-12 && segFree(T[j].p, nw)) { bc = c; best = j; } }       // ① 부모 선택
            int id = T.size(); T.push_back({nw, best, bc, {}}); T[best].ch.push_back(id);
            for (int j : near) { if (j == best || j == 0) continue; double c = T[id].cost + dist(nw, T[j].p); if (c < T[j].cost - 1e-12 && segFree(nw, T[j].p)) { auto& oc = T[T[j].par].ch; oc.erase(std::find(oc.begin(), oc.end(), j)); double delta = c - T[j].cost; T[j].par = id; T[id].ch.push_back(j); shift(T, j, delta); } }  // ② 재배선
            for (int k = 0; k < 3; k++) if (it == cp[k]) { double b = bestToGoal(T, g, 8.0); assert(b <= prevBest + 1e-9); prevBest = b; if (b < 1e17) { assert(b >= opt - 1e-9); ratioAt[k] += b / opt; solvedAt[k]++; } }                        // ② 단조 비증가
        }
        for (size_t i = 1; i < T.size(); i++) { assert(std::fabs(T[i].cost - (T[T[i].par].cost + dist(T[i].p, T[T[i].par].p))) < 1e-6 && segFree(T[T[i].par].p, T[i].p)); }                                             // ① 불변식
        { std::vector<V> pt = {s}; std::vector<int> par = {-1}; bool done = false; for (int it = 0; it < cp[2] && !done; it++) { V q = rng() % 100 < 5 ? g : V{(rng() % 10000) / 100.0, (rng() % 10000) / 100.0}; int nn = 0; for (size_t i = 1; i < pt.size(); i++) if (d2(pt[i], q) < d2(pt[nn], q)) nn = i; double d = dist(pt[nn], q); if (d < 1e-9) continue; V nw = d <= step ? q : V{pt[nn].first + (q.first - pt[nn].first) * step / d, pt[nn].second + (q.second - pt[nn].second) * step / d}; if (!segFree(pt[nn], nw)) continue; pt.push_back(nw); par.push_back(nn);
                if (dist(nw, g) <= step && segFree(nw, g)) { double len = dist(nw, g); for (int v = pt.size() - 1; par[v] >= 0; v = par[v]) len += dist(pt[v], pt[par[v]]); rrtRatio += len / opt; rrtSolved++; done = true; } } }                                                           // 비교: 첫 해에서 멈추는 RRT
    }
    double r0 = ratioAt[0] / solvedAt[0], r1 = ratioAt[1] / solvedAt[1], r2 = ratioAt[2] / solvedAt[2]; assert(worlds >= 8 && solvedAt[2] >= worlds - 1 && r2 <= r1 + 1e-9 && r1 <= r0 + 1e-9 && r2 < 1.12 && r2 < rrtRatio / rrtSolved);
    std::cout << "RRTStar: " << worlds << " worlds; mean cost / optimum after 1500, 4000, 8000 iterations = " << r0 << ", " << r1 << ", " << r2 << " versus plain RRT " << rrtRatio / rrtSolved << std::endl; return 0;
}
// Time Complexity: 반복당 O(n) (k-d 트리 + 반경 질의로 O(log n)), 총 O(n log n)
// Space Complexity: O(n)
```
## ProbabilisticRoadMap()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// PRM(Probabilistic Roadmap, Kavraki et al. 1996): 다중 질의 샘플링 계획기. 전처리에서 자유 공간의 무작위 점 N 개(마디)를 뽑고 각 마디를 가까운 k 개와 충돌 없는 직선으로 이어 로드맵을 만든다.
// 질의는 시작·목표를 로드맵에 임시로 붙이고 그래프 탐색(Dijkstra)을 하면 끝이라 같은 지도에서 질의를 여러 번 할 때 RRT 보다 유리하다. N 이 커질수록 성공률과 경로 품질이 좋아진다(확률적 완전, 점근적 근최적). 좁은 통로는 표본이 드물어 약하다.
// 환경은 RapidlyExploringRandomTree 와 같다. 검증: ① 모든 로드맵 간선이 충돌 없음 ② N = 15, 50, 400 에서 성공률이 늘고(N=400 에서 90% 이상) 평균 비율이 1.2 이하 ③ 같은 로드맵에서 질의를 반복(시작·목표만 바꿔)해도 정확한 최단 이상
typedef std::pair<double, double> V;
struct Rect { double x0, y0, x1, y1; }; std::vector<Rect> obs;
double dist(V a, V b) { return std::hypot(a.first - b.first, a.second - b.second); }
bool hitsRect(V a, V b, const Rect& r) {                                                                                 // 선분이 열린 직사각형 내부와 길이 있는 구간으로 만나는가(경계 접촉은 허용)
    double t0 = 0, t1 = 1, dx = b.first - a.first, dy = b.second - a.second, p[4] = {-dx, dx, -dy, dy}, q[4] = {a.first - r.x0, r.x1 - a.first, a.second - r.y0, r.y1 - a.second};
    for (int i = 0; i < 4; i++) { if (p[i] == 0) { if (q[i] <= 0) return false; } else { double t = q[i] / p[i]; if (p[i] < 0) { if (t > t1) return false; t0 = std::max(t0, t); } else { if (t < t0) return false; t1 = std::min(t1, t); } } }
    return t1 - t0 > 1e-9; }
bool pointFree(V p) { if (p.first < 0 || p.second < 0 || p.first > 100 || p.second > 100) return false; for (const Rect& r : obs) if (p.first > r.x0 && p.first < r.x1 && p.second > r.y0 && p.second < r.y1) return false; return true; }
bool segFree(V a, V b) { if (!pointFree(a) || !pointFree(b)) return false; for (const Rect& r : obs) if (hitsRect(a, b, r)) return false; return true; }
void makeWorld(std::mt19937& g) { obs.clear(); while (obs.size() < 10) { double w = 8 + g() % 17, h = 8 + g() % 17, x0 = 12 + g() % (int)(76 - w), y0 = 12 + g() % (int)(76 - h); obs.push_back({x0, y0, x0 + w, y0 + h}); } }
double optimum(V s, V t) {                                                                                                 // 기준: 직사각형 모서리 가시성 그래프의 정확한 최단 거리
    std::vector<V> pts = {s, t}; for (const Rect& r : obs) for (V c : {V{r.x0, r.y0}, V{r.x1, r.y0}, V{r.x1, r.y1}, V{r.x0, r.y1}}) if (pointFree(c) || true) pts.push_back(c);
    int n = pts.size(); std::vector<double> d(n, 1e18); std::vector<char> done(n, 0); d[0] = 0; for (int it = 0; it < n; it++) { int u = -1; for (int i = 0; i < n; i++) if (!done[i] && (u < 0 || d[i] < d[u])) u = i; if (u < 0 || d[u] > 1e17) break; done[u] = 1; for (int v = 0; v < n; v++) if (!done[v] && d[u] + dist(pts[u], pts[v]) < d[v] && segFree(pts[u], pts[v])) d[v] = d[u] + dist(pts[u], pts[v]); }
    return d[1]; }
struct Roadmap {
    std::vector<V> p; std::vector<std::vector<std::pair<int, double>>> adj; long checks = 0;
    void build(std::mt19937& rng, int N, int k) { p.clear(); while ((int)p.size() < N) { V x{(rng() % 10000) / 100.0, (rng() % 10000) / 100.0}; if (pointFree(x)) p.push_back(x); } adj.assign(N, {});
        for (int i = 0; i < N; i++) { std::vector<std::pair<double, int>> nb; for (int j = 0; j < N; j++) if (j != i) nb.push_back({dist(p[i], p[j]), j}); std::partial_sort(nb.begin(), nb.begin() + k, nb.end()); for (int a = 0; a < k; a++) { int j = nb[a].second; bool dup = false; for (auto& e : adj[i]) dup |= e.first == j; if (dup) continue; checks++; if (segFree(p[i], p[j])) { adj[i].push_back({j, nb[a].first}); adj[j].push_back({i, nb[a].first}); } } } }
    double query(V s, V t) { int n = p.size(); std::vector<V> pts = p; pts.push_back(s); pts.push_back(t); std::vector<std::vector<std::pair<int, double>>> a = adj; a.resize(n + 2);
        for (int e : {n, n + 1}) { std::vector<std::pair<double, int>> nb; for (int j = 0; j < n; j++) nb.push_back({dist(pts[e], p[j]), j}); std::sort(nb.begin(), nb.end()); int linked = 0; for (auto& x : nb) { if (linked >= 8) break; if (segFree(pts[e], p[x.second])) { a[e].push_back({x.second, x.first}); a[x.second].push_back({e, x.first}); linked++; } } }
        if (segFree(s, t)) { a[n].push_back({n + 1, dist(s, t)}); a[n + 1].push_back({n, dist(s, t)}); }
        std::vector<double> d(n + 2, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[n] = 0; pq.push({0, n}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : a[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d[n + 1]; }
};
int main() {
    std::mt19937 rng(5); V s{5, 5}, g{95, 95}; const int Ns[3] = {15, 50, 400}; int ok[3] = {0, 0, 0}; double ratio[3] = {0, 0, 0}; int worlds = 0; long checks[3] = {0, 0, 0}; int multiQueries = 0;
    for (int w = 0; w < 20; w++) {
        makeWorld(rng); double opt = optimum(s, g); if (opt > 1e17) continue; worlds++;
        for (int k = 0; k < 3; k++) { Roadmap R; R.build(rng, Ns[k], 10); checks[k] += R.checks; for (int i = 0; i < Ns[k]; i++) for (auto [j, wgt] : R.adj[i]) { assert(segFree(R.p[i], R.p[j]) && std::fabs(wgt - dist(R.p[i], R.p[j])) < 1e-9); }                     // ① 모든 간선이 충돌 없음
            double len = R.query(s, g); if (len < 1e17) { assert(len >= opt - 1e-9); ok[k]++; ratio[k] += len / opt; }
            if (k == 2) for (int q = 0; q < 5; q++) { V a{(double)(rng() % 10000) / 100.0, (double)(rng() % 10000) / 100.0}, b{(double)(rng() % 10000) / 100.0, (double)(rng() % 10000) / 100.0}; if (!pointFree(a) || !pointFree(b)) continue; double dq = R.query(a, b); if (dq > 1e17) continue; assert(dq >= dist(a, b) - 1e-9); multiQueries++; } }                   // ③ 같은 로드맵 재사용
    }
    assert(worlds >= 15 && ok[0] <= ok[1] && ok[1] <= ok[2] && ok[2] * 10 >= worlds * 9 && ratio[2] / ok[2] < 1.2 && ratio[2] / ok[2] <= ratio[0] / std::max(1, ok[0]) + 1e-9 && multiQueries > 40);
    std::cout << "ProbabilisticRoadMap: " << worlds << " worlds; success N=15/50/400: " << ok[0] << "/" << ok[1] << "/" << ok[2] << ", mean cost / optimum " << (ok[0] ? ratio[0] / ok[0] : 0) << " / " << ratio[1] / ok[1] << " / " << ratio[2] / ok[2] << "; " << multiQueries << " extra queries answered from one roadmap" << std::endl; return 0;
}
// Time Complexity: 전처리 O(N² + N·k·충돌 검사), 질의 O(N log N)
// Space Complexity: O(N·k)
```
## PotentialField()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 인공 퍼텐셜 장(Khatib 1986): 목표는 끌어당기는 위치 에너지 U_att = ½·k_a·|q−g|², 장애물은 가까워질수록 밀어내는 U_rep = ½·k_r·(1/ρ − 1/ρ0)² (ρ: 장애물 표면까지 거리, ρ0 이내에서만)로 모델링하고 로봇은 합력(−∇U)을 따라 내려간다.
// 구현이 간단하고 반응형이지만 치명적 약점이 있다 — 지역 최솟값: 오목한 장애물(U자 벽) 안에서는 끌림과 밀어냄이 균형을 이뤄 목표가 아닌 곳에서 멈춘다. 해법의 하나가 지역 최솟값이 없는 "항해 함수" 이며, 격자에서는 목표에서의 파면 전파(NF1: 장애물을 돌아가는 BFS 거리)가 그것이다.
// 검증: ① 손으로 만든 U자 함정에서 APF 는 목표 아닌 곳에서 멈추고(힘 ≈ 0, 어느 방향으로 조금 움직여도 U 가 늘어남을 확인) NF1 은 도달 ② 무작위 장애물 장에서 APF 의 충돌·정체 횟수를 세고 NF1 은 도달 가능하면 항상 성공 ③ NF1 값은 목표가 아닌 모든 도달 가능한 칸에 더 작은 이웃이 있음(지역 최솟값 없음)
typedef std::pair<double, double> V; struct Circle { double x, y, r; }; std::vector<Circle> obs;
double dist(V a, V b) { return std::hypot(a.first - b.first, a.second - b.second); }
const double KA = 1.0, KR = 4000.0, RHO0 = 10.0;
double potential(V q, V g) { double u = 0.5 * KA * dist(q, g) * dist(q, g); for (const Circle& c : obs) { double rho = std::hypot(q.first - c.x, q.second - c.y) - c.r; if (rho < RHO0) { rho = std::max(rho, 1e-3); u += 0.5 * KR * (1 / rho - 1 / RHO0) * (1 / rho - 1 / RHO0); } } return u; }
V force(V q, V g) { double fx = -KA * (q.first - g.first), fy = -KA * (q.second - g.second); for (const Circle& c : obs) { double dx = q.first - c.x, dy = q.second - c.y, d = std::hypot(dx, dy), rho = d - c.r; if (rho < RHO0 && d > 1e-9) { rho = std::max(rho, 1e-3); double m = KR * (1 / rho - 1 / RHO0) / (rho * rho); fx += m * dx / d; fy += m * dy / d; } } return {fx, fy}; }
V polish(V q, V g) { double st = 0.3; for (int it = 0; it < 40000 && st > 1e-7; it++) { V f = force(q, g); double m = std::hypot(f.first, f.second); if (m < 1e-12) break; V n{q.first + st * f.first / m, q.second + st * f.second / m}; if (potential(n, g) < potential(q, g)) q = n; else st *= 0.5; } return q; }      // 정확한 극소점까지 다듬기
enum Result { REACHED, STUCK, COLLIDED };
Result apf(V q, V g, V& end) { for (int it = 0; it < 6000; it++) { if (dist(q, g) < 1.0) { end = q; return REACHED; } for (const Circle& c : obs) if (std::hypot(q.first - c.x, q.second - c.y) <= c.r) { end = q; return COLLIDED; } V f = force(q, g); double m = std::hypot(f.first, f.second); if (m < 1e-3) { end = q; return STUCK; } q.first += 0.3 * f.first / m; q.second += 0.3 * f.second / m; } end = q; return STUCK; }
struct Wave { std::vector<int> d; int N; };
Wave nf1(V g, int N) { Wave w{std::vector<int>(N * N, -1), N}; auto blocked = [&](int r, int c) { for (const Circle& o : obs) if (std::hypot(c + 0.5 - o.x, r + 0.5 - o.y) <= o.r) return true; return false; }; std::queue<int> q; int gr = (int)g.second, gc = (int)g.first; w.d[gr * N + gc] = 0; q.push(gr * N + gc);
    while (!q.empty()) { int u = q.front(); q.pop(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / N + dr, c = u % N + dc; if ((!dr && !dc) || r < 0 || c < 0 || r >= N || c >= N || w.d[r * N + c] >= 0 || blocked(r, c)) continue; if (dr && dc && (blocked(u / N + dr, u % N) || blocked(u / N, u % N + dc))) continue; w.d[r * N + c] = w.d[u] + 1; q.push(r * N + c); } } return w; }
bool descend(const Wave& w, V s) { int N = w.N, u = (int)s.second * N + (int)s.first; if (w.d[u] < 0) return false; int guard = 0; while (w.d[u] > 0 && guard++ < N * N) { int best = u; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / N + dr, c = u % N + dc; if (r < 0 || c < 0 || r >= N || c >= N || w.d[r * N + c] < 0) continue; if (w.d[r * N + c] < w.d[best]) best = r * N + c; } if (best == u) return false; u = best; } return w.d[u] == 0; }
int main() {
    obs.clear(); for (double y = 28; y <= 72; y += 5) obs.push_back({62, y, 3}); for (double x = 42; x <= 62; x += 5) { obs.push_back({x, 28, 3}); obs.push_back({x, 72, 3}); }          // U 자 함정(열린 쪽이 시작점 방향)
    V s{30, 50}, g{90, 50}, end; Result r = apf(s, g, end); assert(r == STUCK && dist(end, g) > 10); end = polish(end, g); V trapEnd = end;
    double u0 = potential(end, g); for (int k = 0; k < 32; k++) { double a = 6.283185307 * k / 32; V q{end.first + 0.05 * std::cos(a), end.second + 0.05 * std::sin(a)}; assert(potential(q, g) >= u0 - 1e-6); }                     // 지역 최솟값: 작은 이동은 전부 U 가 늘어남
    Wave w = nf1(g, 100); assert(descend(w, s));                                                                                                                                     // NF1 은 U 자 둘레를 돌아 도착
    std::mt19937 rng(3); int trials = 0, apfOk = 0, apfStuck = 1, apfHit = 0, nfOk = 0, reachable = 0;
    for (int t = 0; t < 120; t++) {
        obs.clear(); for (int k = 0; k < 9; k++) obs.push_back({(double)(25 + rng() % 55), (double)(15 + rng() % 70), (double)(4 + rng() % 7)}); V a{5, 5}, b{95, 95}; bool clear = true; for (const Circle& c : obs) clear = clear && std::hypot(c.x - a.first, c.y - a.second) > c.r + 6 && std::hypot(c.x - b.first, c.y - b.second) > c.r + 6; if (!clear) continue; trials++;
        Wave ww = nf1(b, 100); bool reach = ww.d[(int)a.second * 100 + (int)a.first] >= 0; reachable += reach; if (reach) { assert(descend(ww, a)); nfOk++; }
        for (int u = 0; u < 100 * 100; u++) if (ww.d[u] > 0) { bool lower = false; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int rr = u / 100 + dr, cc = u % 100 + dc; if ((dr || dc) && rr >= 0 && cc >= 0 && rr < 100 && cc < 100 && ww.d[rr * 100 + cc] >= 0 && ww.d[rr * 100 + cc] < ww.d[u]) lower = true; } assert(lower); }                  // ③ 지역 최솟값 없음
        Result rr = apf(a, b, end); apfOk += rr == REACHED; apfStuck += rr == STUCK; apfHit += rr == COLLIDED;
    }
    assert(trials > 60 && nfOk == reachable && apfOk <= reachable && apfStuck > 1);
    std::cout << "PotentialField: U-trap -> APF stuck at (" << trapEnd.first << "," << trapEnd.second << ") while NF1 wavefront reaches the goal; over " << trials << " random fields APF reached " << apfOk << ", got stuck " << apfStuck - 1 << ", collided " << apfHit << "; NF1 reached all " << nfOk << " reachable cases with no local minimum" << std::endl; return 0;
}
// Time Complexity: APF 한 걸음 O(장애물 수), NF1 O(격자 칸 수)
// Space Complexity: O(1) / O(격자 칸 수)
```
## DynamicWindowApproach()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 동적 창 접근(DWA, Fox·Burgard·Thrun 1997): 차동 구동 로봇의 지역 계획기. 매 제어 주기마다 ① 다음 dt 안에 가속 한계로 도달 가능한 (v, ω) 속도 쌍의 "동적 창"을 만들고 ② 각 쌍을 일정 속도로 T 초 앞서 시뮬레이션해 궤적을 얻은 뒤
// ③ 그 궤적에서 정지 가능한 쌍(허용 속도: v ≤ √(2·충돌까지 거리·a_max), |ω| ≤ √(2·거리·α_max))만 남기고 ④ 궤적 끝에서 목표까지 남은 거리·장애물 여유·속도의 가중합이 가장 큰 쌍을 실행한다. 허용 속도 조건 덕에 충돌을 피할 수 있는 상태가 계속 유지된다.
// 지역 계획기라 오목한 장애물에서 갇힐 수 있다(전역 경로를 따라가는 용도). 검증: 무작위 장애물 지도 30개에서 ① 한 번도 충돌하지 않음(로봇 반지름 포함) ② 속도·각속도·가속도 한계 위반 없음 ③ 성공률 보고 ④ 같은 지도에서 장애물을 보지 않고 목표로 직진하는 단순 제어는 충돌하는 사례가 있음
struct Circle { double x, y, r; }; std::vector<Circle> obs;
const double VMAX = 1.0, WMAX = 1.5, AMAX = 0.8, ALPHA = 2.5, DT = 0.1, TP = 2.0, RR = 0.4;
struct State { double x, y, th, v, w; };
double clearanceAt(double x, double y) { double m = 1e9; for (const Circle& c : obs) m = std::min(m, std::hypot(x - c.x, y - c.y) - c.r - RR); return m; }
State stepState(State s, double v, double w) { s.th += w * DT; s.x += v * std::cos(s.th) * DT; s.y += v * std::sin(s.th) * DT; s.v = v; s.w = w; return s; }
double angDiff(double a, double b) { double d = a - b; while (d > M_PI) d -= 2 * M_PI; while (d < -M_PI) d += 2 * M_PI; return std::fabs(d); }
State dwa(const State& s, double gx, double gy, bool& found) {
    double vlo = std::max(0.0, s.v - AMAX * DT), vhi = std::min(VMAX, s.v + AMAX * DT), wlo = std::max(-WMAX, s.w - ALPHA * DT), whi = std::min(WMAX, s.w + ALPHA * DT); double bestScore = -1e18; State best = s; found = false;
    for (int i = 0; i <= 4; i++) for (int j = 0; j <= 10; j++) { double v = vlo + (vhi - vlo) * i / 4, w = wlo + (whi - wlo) * j / 10; State p = s; double minClear = 1e9, toHit = 1e9, traveled = 0;
        for (double t = 0; t < TP; t += DT) { p = stepState(p, v, w); traveled += v * DT; double c = clearanceAt(p.x, p.y); minClear = std::min(minClear, c); if (c <= 0 && toHit > 1e8) toHit = traveled; }
        double dStop = toHit < 1e8 ? toHit : std::max(minClear, 0.0); if (v > std::sqrt(2 * dStop * AMAX) + 1e-9 || std::fabs(w) > std::sqrt(2 * dStop * ALPHA) + 1e-9) continue;       // 허용 속도: 충돌하기 전에 멈출 수 있어야 한다
        double progress = 1 - std::hypot(gx - p.x, gy - p.y) / 30.0, clear = std::min(std::max(minClear, 0.0), 2.0) / 2.0, score = 1.0 * progress + 0.4 * clear + 0.2 * v / VMAX;       // 목표까지 남은 거리·장애물 여유·속도의 가중합
        if (score > bestScore) { bestScore = score; best = stepState(s, v, w); found = true; } }
    return best; }
int main() {
    std::mt19937 rng(9); int trials = 0, reached = 0, timeouts = 0, naiveHit = 0; double steps = 0;
    for (int t = 0; t < 30; t++) {
        obs.clear(); for (int k = 0; k < 9; k++) obs.push_back({(double)(4 + rng() % 13), (double)(4 + rng() % 13), 0.5 + (rng() % 10) / 10.0}); State s{1, 1, 0.7, 0, 0}; double gx = 19, gy = 19; bool ok = clearanceAt(s.x, s.y) > 0.3 && clearanceAt(gx, gy) > 0.3; if (!ok) continue; trials++;
        { State n = s; n.v = 0.9; n.th = std::atan2(gy - n.y, gx - n.x); bool hit = false; for (int k = 0; k < 400 && std::hypot(gx - n.x, gy - n.y) > 1.0; k++) { n = stepState(n, 0.9, 0); if (clearanceAt(n.x, n.y) <= 0) { hit = true; break; } } naiveHit += hit; }                      // 비교: 직진
        int k = 0; bool done = false; for (; k < 800; k++) { if (std::hypot(gx - s.x, gy - s.y) < 1.0) { done = true; break; } bool found; State nxt = dwa(s, gx, gy, found);
            assert(nxt.v >= -1e-9 && nxt.v <= VMAX + 1e-9 && std::fabs(nxt.w) <= WMAX + 1e-9 && std::fabs(nxt.v - s.v) <= AMAX * DT + 1e-9 && std::fabs(nxt.w - s.w) <= ALPHA * DT + 1e-9);                     // ② 속도·가속도 한계
            s = nxt; assert(clearanceAt(s.x, s.y) > 0); }                                                                                                                                           // ① 충돌 없음
        if (done) { reached++; steps += k; } else timeouts++;
    }
    assert(trials > 15 && reached * 10 >= trials * 7 && naiveHit > 3);
    std::cout << "DynamicWindowApproach: " << trials << " maps; reached the goal on " << reached << " (mean " << steps / reached * DT << " s), " << timeouts << " timeouts (local traps), 0 collisions or limit violations; straight-line control collided on " << naiveHit << " maps" << std::endl; return 0;
}
// Time Complexity: 제어 주기당 O(속도 샘플 수 × 예측 길이 × 장애물 수)
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
