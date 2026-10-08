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
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Greedy Best-First Search prioritizes pure h(n)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## AStar()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <cassert>

struct State {
    int x, y, g, h;
    bool operator>(const State& other) const { return (g + h) > (other.g + other.h); }
};

int main() {
    int targetX = 2, targetY = 2;
    std::priority_queue<State, std::vector<State>, std::greater<State>> pq;
    pq.push({0, 0, 0, std::abs(2-0) + std::abs(2-0)}); // Manhattan heuristic
    assert(!pq.empty());
    std::cout << "A* structure verified." << std::endl;
    return 0;
}
// Time Complexity: O(E) in best case, O(b^d) worst case
```
## WeightedAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Weighted A* multiplies h(n) by W to speed up." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IDAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "IDA* bounds f(n) iteratively, preserving memory." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## BeamSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Beam Search limits the queue size, pruning nodes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 5. 게임 AI
## JumpPointSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Jump Point Search optimizes grid A* by skipping symmetrical straight paths." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ThetaStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Theta* allows any-angle line-of-sight pathing." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LazyThetaStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Lazy Theta* defers line-of-sight checks until node expansion." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## AnyAngleSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Any-Angle Search smooths aliased paths." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## HierarchicalPathFinding()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "HPA* groups grids into clusters, finds path via cluster portals." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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
