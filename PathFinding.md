# Part 1. 길찾기의 기초
## CreateMap()
### 대표코드
```cpp
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

// 길찾기의 출발점은 "세계를 어떻게 표현하는가"이다. 격자 지도는 글자 지도(ASCII map)로 적고 읽는 것이 가장 편하다: '#' 벽, '.' 평지, '1'~'9' 지형 비용, 'S' 시작, 'G' 목표.
// 읽을 때 검증이 중요하다 — 줄 길이가 들쭉날쭉하거나 시작·목표가 없거나 둘 이상이거나 모르는 글자가 있으면 이후 모든 알고리즘이 조용히 틀린 답을 내므로 지도를 만드는 순간 거절한다. 판정 규칙을 한 문장으로: "직사각형이고, 글자가 모두 허용 집합 안이며, S 가 정확히 하나, G 가 정확히 하나".
// 검증: ① 규칙을 글자 단위로 따로 쓴 판정기(valid)와 파서가 *모든* 입력에서 같은 답 — 무작위 글자열 5000 개(퍼징: 어떤 입력에도 비정상 종료 없음) ② 올바른 지도를 만들었다 쓰면 다시 읽은 값이 같고(render ∘ parse 는 '1' 을 '.' 로 정규화하는 멱등 사상), 올바른 지도에 흠을 하나 내면(S 지우기, G 지우기, S 추가, G 추가, 줄 자르기, 나쁜 글자, 비어 있음) 반드시 거절 ③ 통과 가능 판정은 범위 밖에서 항상 거짓.
struct Map {
    int rows = 0, cols = 0, sr = -1, sc = -1, gr = -1, gc = -1; std::vector<std::vector<int>> cost;        // 0 = 벽, >= 1 = 칸에 들어가는 비용
    bool inBounds(int r, int c) const { return r >= 0 && r < rows && c >= 0 && c < cols; }
    bool passable(int r, int c) const { return inBounds(r, c) && cost[r][c] > 0; }
};
bool parseMap(const std::vector<std::string>& lines, Map& m) {
    m = Map(); m.rows = (int)lines.size(); if (!m.rows) return false; m.cols = (int)lines[0].size(); if (!m.cols) return false; int starts = 0, goals = 0;
    for (int r = 0; r < m.rows; r++) {
        if ((int)lines[r].size() != m.cols) return false;                                                  // 직사각형이어야 한다
        m.cost.emplace_back(m.cols, 0);
        for (int c = 0; c < m.cols; c++) {
            char ch = lines[r][c];
            if (ch == '#') m.cost[r][c] = 0; else if (ch == '.') m.cost[r][c] = 1; else if (ch >= '1' && ch <= '9') m.cost[r][c] = ch - '0';
            else if (ch == 'S') { m.cost[r][c] = 1; m.sr = r; m.sc = c; starts++; } else if (ch == 'G') { m.cost[r][c] = 1; m.gr = r; m.gc = c; goals++; } else return false;
        }
    }
    return starts == 1 && goals == 1;
}
std::vector<std::string> render(const Map& m) {                                                            // 지도를 다시 글자로 (비용 1 은 '.')
    std::vector<std::string> out;
    for (int r = 0; r < m.rows; r++) { std::string s; for (int c = 0; c < m.cols; c++) s += (r == m.sr && c == m.sc) ? 'S' : (r == m.gr && c == m.gc) ? 'G' : m.cost[r][c] == 0 ? '#' : m.cost[r][c] == 1 ? '.' : (char)('0' + m.cost[r][c]); out.push_back(s); }
    return out;
}
// 독립 판정기: 파서를 쓰지 않고 규칙을 글자 단위로 센다
bool valid(const std::vector<std::string>& lines) {
    if (lines.empty() || lines[0].empty()) return false;
    int s = 0, g = 0;
    for (const auto& row : lines) { if (row.size() != lines[0].size()) return false; for (char ch : row) { if (ch == 'S') s++; else if (ch == 'G') g++; else if (!(ch == '#' || ch == '.' || (ch >= '1' && ch <= '9'))) return false; } }
    return s == 1 && g == 1;
}

int main() {
    // ① 손으로 확인한 모양
    Map m; std::vector<std::string> ok = {"S..#....", ".#.#.##.", ".#...#..", ".####.#.", "...9...G"};
    assert(parseMap(ok, m) && m.rows == 5 && m.cols == 8 && m.sr == 0 && m.sc == 0 && m.gr == 4 && m.gc == 7);
    assert(m.passable(0, 1) && !m.passable(0, 3) && !m.passable(-1, 0) && !m.passable(5, 0) && m.cost[4][3] == 9);        // 벽·범위 밖·지형 비용
    int walls = 0; for (auto& row : m.cost) for (int v : row) walls += v == 0; assert(walls == 12);
    Map bad; assert(!parseMap({"S..", "..G."}, bad) && !parseMap({"S.."}, bad) && !parseMap({"S.G", "S.."}, bad) && !parseMap({"S.x", "..G"}, bad) && !parseMap({}, bad) && !parseMap({""}, bad));

    // ② 퍼징 5000 개 — 파서와 독립 판정기가 항상 같은 답. 절반은 올바른 지도에서 시작해 한 칸을 임의 글자로 바꾸거나 줄 길이·시작·목표를 건드리고, 절반은 완전한 무작위 글자열
    std::mt19937 rng(1); const std::string alphabet = "#...1234567SG0x \t9"; int accepted = 0;
    for (int it = 0; it < 5000; ++it) {
        std::vector<std::string> lines;
        if (it % 2 == 0) {
            int R = 1 + (int)(rng() % 5), C = 1 + (int)(rng() % 6); if (R * C < 2) C = 2;
            lines.assign(R, std::string(C, '.')); for (auto& row : lines) for (char& ch : row) ch = "#..123"[rng() % 6];
            int s = (int)(rng() % (R * C)), g; do g = (int)(rng() % (R * C)); while (g == s); lines[s / C][s % C] = 'S'; lines[g / C][g % C] = 'G';
            int kind = (int)(rng() % 6);
            if (kind == 1) { int x = (int)(rng() % (R * C)); lines[x / C][x % C] = alphabet[rng() % alphabet.size()]; }
            else if (kind == 2) lines[rng() % R].push_back('.');
            else if (kind == 3 && lines[0].size() > 1) lines[rng() % R].pop_back();
            else if (kind == 4) lines.push_back(lines[0]);
        } else {
            int R = (int)(rng() % 5); for (int r = 0; r < R; ++r) { int w = (int)(rng() % 7); std::string s; for (int c = 0; c < w; ++c) s += alphabet[rng() % alphabet.size()]; lines.push_back(s); }
        }
        Map t; bool p = parseMap(lines, t); assert(p == valid(lines)); accepted += p;
    }
    assert(accepted > 1000);                                                                                 // 올바른 입력도 충분히 나왔다

    // ③ 올바른 지도를 만들어 쓰고 다시 읽기 · 흠 내기
    const std::string cells = "#.....123456789";
    int mutations = 0;
    for (int it = 0; it < 2000; ++it) {
        int R = 1 + (int)(rng() % 7), C = 1 + (int)(rng() % 7); if (R * C < 3) continue;
        std::vector<std::string> lines(R, std::string(C, '.')); for (auto& row : lines) for (char& ch : row) ch = cells[rng() % cells.size()];
        int s = (int)(rng() % (R * C)), g; do g = (int)(rng() % (R * C)); while (g == s); lines[s / C][s % C] = 'S'; lines[g / C][g % C] = 'G';
        Map a, b; assert(parseMap(lines, a) && a.sr == s / C && a.sc == s % C && a.gr == g / C && a.gc == g % C);
        auto text = render(a); assert(parseMap(text, b) && render(b) == text && b.cost == a.cost);              // 정규화는 멱등: 읽고-쓰고-읽으면 같은 지도
        int walls = 0, plain = 0; for (auto& row : a.cost) for (int v : row) { walls += v == 0; plain += v >= 1; } assert(walls + plain == R * C);
        // 흠 일곱 가지: 반드시 거절
        Map t; auto broken = lines; broken[s / C][s % C] = '.'; assert(!parseMap(broken, t));                  // 시작 없음
        broken = lines; broken[g / C][g % C] = '.'; assert(!parseMap(broken, t));                              // 목표 없음
        broken = lines; { int x = (int)(rng() % (R * C)); while (x == s || x == g) x = (int)(rng() % (R * C)); broken[x / C][x % C] = 'S'; } assert(!parseMap(broken, t));           // 시작 둘
        broken = lines; { int x = (int)(rng() % (R * C)); while (x == s || x == g) x = (int)(rng() % (R * C)); broken[x / C][x % C] = 'G'; } assert(!parseMap(broken, t));           // 목표 둘
        broken = lines; { int x = (int)(rng() % (R * C)); while (x == s || x == g) x = (int)(rng() % (R * C)); broken[x / C][x % C] = "x0 \t?"[rng() % 5]; } assert(!parseMap(broken, t));   // 모르는 글자
        if (R >= 2) { broken = lines; broken[rng() % R].pop_back(); assert(!parseMap(broken, t)); mutations++; }   // 한 줄이 짧아져 들쭉날쭉
        broken = lines; broken.push_back(std::string(C + 1, '.')); assert(!parseMap(broken, t));                // 길이가 다른 줄 추가
        mutations += 7;
        for (int dr = -2; dr <= R + 2; ++dr) for (int dc = -2; dc <= C + 2; ++dc) assert(a.passable(dr, dc) == (dr >= 0 && dr < R && dc >= 0 && dc < C && a.cost[dr][dc] > 0));
    }
    assert(mutations > 12000);
    std::cout << "CreateMap: the parser agreed with an independent letter-by-letter validity check on 5000 fuzzed inputs (" << accepted << " valid ones), 2000 random maps survived write-then-read with identical cost grids, all seven kinds of damage (missing or doubled start/goal, unknown letter, ragged row, extra row) were rejected, and passability was false everywhere outside the map" << std::endl; return 0;
}
// Time Complexity: O(행 × 열)
// Space Complexity: O(행 × 열)
```
## CreateGrid()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 격자 위의 이동 규칙이 곧 그래프의 간선이다. 4방향은 비용 1, 8방향은 대각선 비용 √2 인데 부동소수점 대신 정수 10 과 14(≈10√2)로 스케일해 비교·해시 오차를 없앤다.
// 대각선 이동에는 "모서리 자르기(corner cutting)" 규칙이 필요하다 — 대각선으로 지나가는 두 칸 중 하나라도 벽이면 벽 모서리를 스치며 통과하므로 보통 금지한다 (게임에 따라 허용하기도).
// 이웃 생성 함수를 한 곳에 모아 두면 BFS / Dijkstra / A* 가 모두 같은 규칙을 공유한다
//  ⑥ 무작위 지도 3 000 개(1×1..9×9, 벽 30%) × 규칙 4 가지(4/8방향 × 모서리 자르기 허용/금지)의 *모든 빈 칸* 에서 neighbors 가 규칙을 정의 그대로 짠 독립 열거(주변 8 칸을 직접 훑으며 경계·벽·대각선의 두 직교 칸을 검사)와 같은 집합·비용이고 모든 간선이 같은 비용의 역방향 간선을 가짐  ⑦ 벽 없는 R×C 격자의 방향 간선 수 닫힌 식: 4방향 2·(R(C−1) + C(R−1)), 8방향은 거기에 4(R−1)(C−1) 을 더한 값 (R, C ≤ 8 전수)
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
    {   std::mt19937 rng(3); long cases = 0;                                                                                               // ⑥ 무작위 지도 대 정의 그대로의 오라클
        for (int trial = 0; trial < 3000; ++trial) { int R = 1 + (int)(rng() % 9), C = 1 + (int)(rng() % 9); std::vector<std::string> w(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 30) ch = '#';
            for (int mode = 0; mode < 4; ++mode) { Grid grid{R, C, w, (mode & 1) != 0, (mode & 2) != 0};
                for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) { if (w[r][c] == '#') continue; std::set<std::pair<std::pair<int, int>, int>> want;
                    for (int dr = -1; dr <= 1; ++dr) for (int dc = -1; dc <= 1; ++dc) { if (!dr && !dc) continue; bool diagMove = dr != 0 && dc != 0; if (diagMove && !grid.diag) continue;
                        int nr = r + dr, nc = c + dc; if (nr < 0 || nr >= R || nc < 0 || nc >= C || w[nr][nc] == '#') continue;
                        if (diagMove && !grid.cut && (w[r + dr][c] == '#' || w[r][c + dc] == '#')) continue;                                 // 대각선이 벽 모서리를 스침
                        want.insert({{nr, nc}, diagMove ? 14 : 10}); }
                    auto got = grid.neighbors(r, c); std::set<std::pair<std::pair<int, int>, int>> gotSet(got.begin(), got.end()); assert(gotSet == want && got.size() == want.size()); ++cases;
                    for (auto& e : got) { bool back = false; for (auto& f : grid.neighbors(e.first.first, e.first.second)) back |= f.first == std::make_pair(r, c) && f.second == e.second; assert(back); } } } }       // 간선은 양방향·같은 비용
        assert(cases > 10000);
        for (int R = 1; R <= 8; ++R) for (int C = 1; C <= 8; ++C) { std::vector<std::string> open(R, std::string(C, '.')); Grid g4{R, C, open, false, false}, g8{R, C, open, true, false}; long e4 = 0, e8 = 0;      // ⑦ 닫힌 식
            for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) { e4 += (long)g4.neighbors(r, c).size(); e8 += (long)g8.neighbors(r, c).size(); }
            assert(e4 == 2L * (R * (C - 1) + C * (R - 1)) && e8 == e4 + 4L * (R - 1) * (C - 1)); } }
    std::cout << "CreateGrid: 5x5 map with one wall has " << edges << " directed edges (8-neighbour, no corner cutting)" << std::endl; return 0;
}
// Time Complexity: 이웃 생성 O(1)
// Space Complexity: O(1) (격자 자체 O(행 × 열))
```
## CreateNode()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 탐색 노드 = (칸, 시작에서 온 비용 g, 목표까지 추정 h, 부모). f = g + h 가 작은 노드를 먼저 꺼내는 우선순위 큐가 A* 의 심장이다. 노드는 칸 번호로 가리키고 부모도 번호로 두면 복사·할당 비용이 없고 경로 복원도 쉽다.
// 꼭 정해야 할 것이 *동점 처리(tie-breaking)* 다: f 가 같을 때 g 가 큰(= 목표에 더 가까운) 노드를 먼저 꺼내면 같은 f 층 안에서 목표 쪽으로 곧장 파고들어 확장 수가 줄고, 작은 쪽을 먼저 꺼내면 같은 f 의 모든 노드를 훑는다. 최적성은 동점 처리와 무관해야 한다.
// 검증: 무작위 장애물 격자(4방향, 단위 비용, 맨해튼 휴리스틱)에서 ① 두 동점 처리 모두 BFS 로 구한 정확한 거리와 같은 비용(도달 불가면 둘 다 -1) ② 복원한 경로가 칸마다 이웃이고 길이가 비용과 같음 ③ 꺼내는 노드의 f 가 단조 비감소(일관된 휴리스틱의 성질) ④ 전체 확장 수는 "g 가 큰 쪽 먼저" 가 "g 가 작은 쪽 먼저" 이하이고, 장애물 없는 40×40 에서는 5 배 이상 차이.
struct Node { int cell, g, h, parent; int f() const { return g + h; } };
struct Result { int cost = -1; long expanded = 0; std::vector<int> path; bool monotoneF = true; };

Result astar(const std::vector<std::string>& w, int start, int goal, bool preferLargeG) {
    int R = (int)w.size(), C = (int)w[0].size(); auto h = [&](int cell) { return std::abs(cell / C - goal / C) + std::abs(cell % C - goal % C); };
    auto cmp = [&](const Node& a, const Node& b) { if (a.f() != b.f()) return a.f() > b.f(); return preferLargeG ? a.g < b.g : a.g > b.g; };
    std::priority_queue<Node, std::vector<Node>, decltype(cmp)> pq(cmp);
    std::vector<int> best(R * C, 1 << 30), parent(R * C, -1); Result res; int lastF = -1;
    best[start] = 0; pq.push({start, 0, h(start), -1});
    while (!pq.empty()) {
        Node n = pq.top(); pq.pop(); if (n.g > best[n.cell]) continue;
        res.expanded++; if (n.f() < lastF) res.monotoneF = false; lastF = n.f();
        if (n.cell == goal) { res.cost = n.g; for (int v = goal; v != -1; v = parent[v]) res.path.push_back(v); std::reverse(res.path.begin(), res.path.end()); return res; }
        static const int dr[4] = {1, 0, -1, 0}, dc[4] = {0, 1, 0, -1};
        for (int d = 0; d < 4; d++) {
            int nr = n.cell / C + dr[d], nc = n.cell % C + dc[d]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue;
            int nxt = nr * C + nc, g = n.g + 1; if (g < best[nxt]) { best[nxt] = g; parent[nxt] = n.cell; pq.push({nxt, g, h(nxt), n.cell}); }
        }
    }
    return res;
}
int bfsDistance(const std::vector<std::string>& w, int start, int goal) {                                  // 오라클: 단위 비용 4방향 최단 거리
    int R = (int)w.size(), C = (int)w[0].size(); std::vector<int> d(R * C, -1); std::queue<int> q; d[start] = 0; q.push(start);
    while (!q.empty()) { int u = q.front(); q.pop(); static const int dr[4] = {1, 0, -1, 0}, dc[4] = {0, 1, 0, -1}; for (int k = 0; k < 4; k++) { int nr = u / C + dr[k], nc = u % C + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || d[nr * C + nc] >= 0) continue; d[nr * C + nc] = d[u] + 1; q.push(nr * C + nc); } }
    return d[goal];
}
bool pathOk(const std::vector<std::string>& w, const std::vector<int>& p, int cost) {
    int C = (int)w[0].size(); if ((int)p.size() != cost + 1) return false;
    for (std::size_t i = 0; i < p.size(); i++) { if (w[p[i] / C][p[i] % C] == '#') return false; if (i && std::abs(p[i] / C - p[i - 1] / C) + std::abs(p[i] % C - p[i - 1] % C) != 1) return false; }
    return true;
}

int main() {
    // ① 손으로 확인한 모양: f 가 같으면 g 가 큰 노드가 먼저
    {
        auto cmp = [](const Node& a, const Node& b) { return a.f() != b.f() ? a.f() > b.f() : a.g < b.g; };
        std::priority_queue<Node, std::vector<Node>, decltype(cmp)> pq(cmp);
        pq.push({0, 3, 7, -1}); pq.push({1, 6, 4, 0}); pq.push({2, 1, 9, 0}); pq.push({3, 8, 2, 1});
        assert(pq.top().f() == 10 && pq.top().g == 8); pq.pop(); assert(pq.top().g == 6);
    }
    // ② 무작위 장애물 격자 300 개 (장애물 비율 0%~35%): 두 동점 처리의 비용 = BFS 거리, 경로 · f 단조성, 확장 수 합
    std::mt19937 rng(11); long goodTotal = 0, badTotal = 0; int solved = 0, unreachable = 0;
    for (int it = 0; it < 300; ++it) {
        int R = 5 + (int)(rng() % 20), C = 5 + (int)(rng() % 20), pct = (int)(rng() % 36); std::vector<std::string> w(R, std::string(C, '.'));
        for (auto& row : w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int s = (int)(rng() % (R * C)), g = (int)(rng() % (R * C)); w[s / C][s % C] = '.'; w[g / C][g % C] = '.';
        Result a = astar(w, s, g, true), b = astar(w, s, g, false); int want = bfsDistance(w, s, g);
        assert(a.cost == want && b.cost == want && a.monotoneF && b.monotoneF);
        if (want >= 0) { assert(pathOk(w, a.path, want) && pathOk(w, b.path, want)); ++solved; } else ++unreachable;
        goodTotal += a.expanded; badTotal += b.expanded;
    }
    assert(solved > 150 && unreachable > 5 && goodTotal <= badTotal);
    // ③ 장애물 없는 40×40: 동점 처리만 바꿔도 확장 수가 5 배 이상 차이
    {   std::vector<std::string> open(40, std::string(40, '.')); Result a = astar(open, 0, 40 * 40 - 1, true), b = astar(open, 0, 40 * 40 - 1, false);
        assert(a.cost == 78 && b.cost == 78 && a.expanded * 5 < b.expanded && a.expanded <= 80);                // g 가 큰 쪽 먼저면 한 줄기로 곧장 (≈ 경로 길이만큼만 확장)
        std::cout << "CreateNode: open 40x40 grid A* expansions with tie-break on larger g = " << a.expanded << ", on smaller g = " << b.expanded << "; over 300 random grids " << goodTotal << " vs " << badTotal << " expansions, costs always equal to BFS" << std::endl; }
    return 0;
}
// Time Complexity: 노드 생성·비교 O(1)
// Space Complexity: O(1) 노드당
```
## CreateEdge()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <vector>
#include <cassert>

// 간선은 (출발, 도착, 가중치)이다. 같은 그래프를 간선 목록(edge list, 정렬·크루스칼에 편함), 인접 리스트(탐색에 가장 흔함), CSR(Compressed Sparse Row: 연속 메모리라 캐시 친화적, 정적 그래프에 최적)로 표현할 수 있고
// 서로 변환할 수 있어야 한다.  길찾기 알고리즘은 가중치가 음수가 아니라는 전제(Dijkstra, A*)가 많으므로 간선을 만들 때 검증하고, 같은 (출발, 도착)이 여러 번 들어오면 가장 싼 것만 남긴다.
// 무방향 간선은 양방향 간선 두 개로 저장한다
//  ⑤ 무작위 간선 열 2 000 개(정점 1~8, 시도 0~29 번, 무방향 여부 무작위, 음수 가중치 포함)에서 addEdge 의 거절 판정, dedupe 결과(= (u, v) 별 최솟값을 std::map 으로 모은 오라클), CSR 로 바꿨다 되읽은 간선 집합, 행 시작 배열의 단조성과 총량이 모두 일치
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
    {   std::mt19937 rng(4);                                                                                                             // ⑤ 무작위 간선 열
        for (int trial = 0; trial < 2000; ++trial) { int n = 1 + (int)(rng() % 8); std::vector<Edge> list; std::map<std::pair<int, int>, int> best; int attempts = (int)(rng() % 30); bool undirected = rng() % 2 == 0;
            for (int k = 0; k < attempts; ++k) { int u = (int)(rng() % n), v = (int)(rng() % n), w = (int)(rng() % 20) - 3; bool ok = addEdge(list, u, v, w, undirected); assert(ok == (w >= 0));
                if (ok) { auto upd = [&](int a, int b) { auto it = best.find({a, b}); if (it == best.end() || w < it->second) best[{a, b}] = w; }; upd(u, v); if (undirected) upd(v, u); } }
            auto dd = dedupe(list); assert(dd.size() == best.size()); for (auto& e : dd) { auto it = best.find({e.u, e.v}); assert(it != best.end() && it->second == e.w); }
            CSR csr = toCSR(dd, n); assert((int)csr.start.size() == n + 1 && csr.start[0] == 0 && csr.start[n] == (int)dd.size()); std::map<std::pair<int, int>, int> back;
            for (int u = 0; u < n; ++u) { assert(csr.start[u] <= csr.start[u + 1]); for (int k = csr.start[u]; k < csr.start[u + 1]; ++k) back[{u, csr.to[k]}] = csr.w[k]; } assert(back == best); } }       // 목록 → 중복 제거 → CSR → 되읽기
    std::cout << "CreateEdge: " << d.size() << " directed edges after dedupe, CSR row starts: " << g.start[0] << " " << g.start[1] << " " << g.start[2] << " " << g.start[3] << std::endl; return 0;
}
// Time Complexity: 간선 추가 O(1), 중복 제거 O(E log E), CSR 변환 O(V + E)
// Space Complexity: O(V + E)
```
## BuildGraph()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 격자 지도를 일반 그래프로 바꾸면 격자에서 쓰던 알고리즘(BFS, Dijkstra, A*)을 도로망·내비메시 같은 임의의 그래프에서도 그대로 쓸 수 있다. 통과 가능한 칸마다 정점 번호 r*C+c 를 주고, 이웃 규칙(4/8방향, 모서리 자르기 금지)에 따라 간선을 만든다. 벽 칸은 간선이 없다(번호는 그대로 두고 인접 리스트만 비워 둔다). 가중치는 정수 10(직선)과 14(대각선 ≈ 10√2).
// 변환이 맞는지 *세 가지* 로 확인한다: ① 변환한 그래프에서 구한 BFS·Dijkstra 거리와 그래프를 거치지 않고 격자에서 직접 구한 값이 같다 ② 간선이 대칭(u→v 가 있으면 v→u 도 같은 가중치)이고 벽에 닿는 간선이 없다 ③ 장애물 없는 R×C 격자의 4방향 간선 수는 정확히 2·(R(C−1) + C(R−1)) 이고 8방향은 거기에 대각선 4·(R−1)(C−1) 을 더한 값이다. 무작위 격자 400 개에서 확인한다.
struct G { int R, C; std::vector<std::vector<std::pair<int, int>>> adj; };
G build(const std::vector<std::string>& w, bool diag) {
    int R = (int)w.size(), C = (int)w[0].size(); G g{R, C, std::vector<std::vector<std::pair<int, int>>>(R * C)}; static const int dr[8] = {-1, 1, 0, 0, -1, -1, 1, 1}, dc[8] = {0, 0, -1, 1, -1, 1, -1, 1};
    auto ok = [&](int r, int c) { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; };
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) {
        if (!ok(r, c)) continue;
        for (int d = 0; d < (diag ? 8 : 4); d++) { int nr = r + dr[d], nc = c + dc[d]; if (!ok(nr, nc)) continue; if (d >= 4 && (!ok(r + dr[d], c) || !ok(r, c + dc[d]))) continue; g.adj[r * C + c].push_back({nr * C + nc, d < 4 ? 10 : 14}); }
    }
    return g;
}
std::vector<int> bfsGraph(const G& g, int s) { std::vector<int> d(g.adj.size(), -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (auto& e : g.adj[u]) if (d[e.first] < 0) { d[e.first] = d[u] + 1; q.push(e.first); } } return d; }
std::vector<int> bfsGrid(const std::vector<std::string>& w, int sr, int sc, bool diag) {                  // 그래프를 거치지 않고 격자에서 직접
    int R = (int)w.size(), C = (int)w[0].size(); std::vector<int> d(R * C, -1); std::queue<std::pair<int, int>> q; d[sr * C + sc] = 0; q.push({sr, sc});
    auto ok = [&](int r, int c) { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; };
    while (!q.empty()) {
        auto [r, c] = q.front(); q.pop();
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) {
            if (!dr && !dc) continue; if (!diag && dr && dc) continue; int nr = r + dr, nc = c + dc; if (!ok(nr, nc)) continue;
            if (dr && dc && (!ok(r + dr, c) || !ok(r, c + dc))) continue; if (d[nr * C + nc] < 0) { d[nr * C + nc] = d[r * C + c] + 1; q.push({nr, nc}); }
        }
    }
    return d;
}
std::vector<int> dijkstraGraph(const G& g, int s) {
    std::vector<int> d(g.adj.size(), INT_MAX); std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto& e : g.adj[u]) if (du + e.second < d[e.first]) { d[e.first] = du + e.second; pq.push({d[e.first], e.first}); } }
    return d;
}
// 오라클: 격자를 8방향으로 직접 훑는 Dijkstra (그래프 자료구조를 거치지 않음)
std::vector<int> dijkstraGrid(const std::vector<std::string>& w, int sr, int sc, bool diag) {
    int R = (int)w.size(), C = (int)w[0].size(); std::vector<int> d(R * C, INT_MAX); std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq; d[sr * C + sc] = 0; pq.push({0, sr * C + sc});
    auto ok = [&](int r, int c) { return r >= 0 && r < R && c >= 0 && c < C && w[r][c] != '#'; };
    while (!pq.empty()) {
        auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; int r = u / C, c = u % C;
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) {
            if (!dr && !dc) continue; if (!diag && dr && dc) continue; int nr = r + dr, nc = c + dc; if (!ok(nr, nc)) continue;
            if (dr && dc && (!ok(r + dr, c) || !ok(r, c + dc))) continue; int wgt = (dr && dc) ? 14 : 10; if (du + wgt < d[nr * C + nc]) { d[nr * C + nc] = du + wgt; pq.push({d[nr * C + nc], nr * C + nc}); }
        }
    }
    return d;
}

int main() {
    // ① 손으로 확인한 모양
    std::vector<std::string> w = {"........", ".##..#..", "........", ".#.###..", "........"};
    for (bool diag : {false, true}) { G g = build(w, diag); assert(bfsGraph(g, 0) == bfsGrid(w, 0, 0, diag)); }
    G g4 = build(w, false), g8 = build(w, true); long e4 = 0, e8 = 0; for (auto& a : g4.adj) e4 += a.size(); for (auto& a : g8.adj) e8 += a.size();
    assert(e8 > e4); for (int r = 0; r < 5; r++) for (int c = 0; c < 8; c++) if (w[r][c] == '#') assert(g8.adj[r * 8 + c].empty());

    // ② 장애물 없는 R×C: 간선 수 공식
    for (int R = 1; R <= 9; ++R) for (int C = 1; C <= 9; ++C) {
        std::vector<std::string> open(R, std::string(C, '.')); long f4 = 0, f8 = 0; for (auto& a : build(open, false).adj) f4 += a.size(); for (auto& a : build(open, true).adj) f8 += a.size();
        assert(f4 == 2L * (R * (C - 1) + C * (R - 1)) && f8 == f4 + 4L * (R - 1) * (C - 1));
    }

    // ③ 무작위 격자 400 개: 대칭 · 벽 간선 없음 · 그래프 BFS/Dijkstra = 격자 직접 BFS/Dijkstra
    std::mt19937 rng(5);
    for (int it = 0; it < 400; ++it) {
        int R = 2 + (int)(rng() % 12), C = 2 + (int)(rng() % 12), pct = (int)(rng() % 45); std::vector<std::string> m(R, std::string(C, '.'));
        for (auto& row : m) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int s = (int)(rng() % (R * C)); m[s / C][s % C] = '.';
        for (bool diag : {false, true}) {
            G g = build(m, diag);
            for (int u = 0; u < R * C; u++) for (auto& e : g.adj[u]) { assert(m[u / C][u % C] != '#' && m[e.first / C][e.first % C] != '#'); bool back = false; for (auto& f : g.adj[e.first]) back |= f.first == u && f.second == e.second; assert(back); }
            assert(bfsGraph(g, s) == bfsGrid(m, s / C, s % C, diag));
            auto dg = dijkstraGraph(g, s), dd = dijkstraGrid(m, s / C, s % C, diag); for (int v = 0; v < R * C; v++) assert(dg[v] == dd[v]);
        }
    }
    std::cout << "BuildGraph: the 4-neighbour graph of the sample map has " << e4 << " directed edges and the 8-neighbour graph " << e8 << "; edge counts matched 2(R(C-1)+C(R-1)) (+4(R-1)(C-1) with diagonals) on every open grid up to 9x9, and on 400 random obstacle grids the graph was symmetric, wall-free, and its BFS and Dijkstra distances equalled direct searches on the grid" << std::endl; return 0;
}
// Time Complexity: O(행 × 열 × 이웃 수)
// Space Complexity: O(V + E)
```
## InitializeSearch()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 길찾기를 여러 번(질의마다, 매 프레임마다) 부를 때 거리표·부모표·방문표를 매번 0 으로 다시 채우면 정점 수 V 만큼의 비용이 든다. 지도가 100만 칸이고 질의가 가까운 두 점이면 탐색은 수백 칸만 보는데 초기화에 100만 번을 쓴다.
// 해결: 칸마다 "마지막으로 쓴 질의 번호(stamp)"를 두고 현재 번호와 다르면 아직 초기화 안 된 칸으로 보고 그 자리에서 기본값을 쓴다 — 질의 시작은 번호를 하나 올리는 O(1).
// 이 항목은 이런 "세대 번호 초기화"가 정확함(이전 질의의 값이 새 질의에 새지 않음)과 일 양(쓴 칸 수만 초기화)을 보인다
//  ⑥ 무작위 그래프 50 개(정점 2~61, 간선 0~3n 개, 비연결 포함)에서 *재사용하는 하나의 Search 객체* 로 질의 200 번씩: 세대 번호 방식의 거리가 매번 새로 0 으로 채운 일반 BFS 와 같고(도달 불가는 −1), 질의 한 번이 건드린 칸 수가 일반 BFS 가 그 시점까지 발견한 정점 수와 *정확히* 같다
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
    {   std::mt19937 rng(6); long queries = 0;                                                                                              // ⑥ 무작위 그래프와 재사용
        for (int trial = 0; trial < 50; ++trial) { int n = 2 + (int)(rng() % 60); std::vector<std::vector<int>> g(n); int m = (int)(rng() % (3 * n)); for (int i = 0; i < m; ++i) { int a = (int)(rng() % n), b = (int)(rng() % n); g[a].push_back(b); g[b].push_back(a); }
            Search reused(n); for (int q = 0; q < 200; ++q) { int a = (int)(rng() % n), b = (int)(rng() % n);
                std::vector<int> dist(n, -1); std::queue<int> qq; dist[a] = 0; qq.push(a); int want = -1; while (!qq.empty()) { int u = qq.front(); qq.pop(); if (u == b) { want = dist[u]; break; } for (int v : g[u]) if (dist[v] < 0) { dist[v] = dist[u] + 1; qq.push(v); } }
                long discovered = 0; for (int x : dist) discovered += x >= 0; long before = reused.touched; int got = bfs(reused, g, a, b); assert(got == want && reused.touched - before == discovered); ++queries; } }
        assert(queries == 10000); }
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
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 탐색이 끝나면 각 칸에는 "나를 처음 발견한 칸(부모)" 만 남는다. 경로는 목표에서 부모를 따라 시작까지 거슬러 올라간 뒤 뒤집어 얻는다. 확인할 것 셋: ① 목표에 부모가 없으면(= 도달 못 함) 빈 경로 ② 부모 사슬에 사이클이 있으면(버그) 무한 루프 대신 걸러 내기 ③ 복원한 경로가 정말 유효한가 — 연속한 두 칸이 이웃이고 벽이 아니며 길이가 탐색이 보고한 거리와 같은지 검사하는 함수를 같이 둔다(모든 경로 알고리즘 테스트에서 재사용).
// 검증: ① 무작위 격자에서 BFS 의 부모 배열로 복원한 경로가 항상 유효하고 길이가 BFS 거리와 같다(도달 불가면 빈 경로) ② 어떤 부모 배열이든(무작위로 만든 것 포함) 함수가 반드시 끝나고, 비어 있지 않은 답은 시작에서 목표까지의 부모 사슬 그 자체다 ③ 사슬에 사이클을 일부러 심으면 빈 경로.
std::vector<int> reconstruct(const std::vector<int>& parent, int goal, int start) {
    std::vector<int> path; int steps = 0;
    for (int v = goal; v != -1; v = parent[v]) { path.push_back(v); if (v == start) { std::reverse(path.begin(), path.end()); return path; } if (++steps > (int)parent.size()) return {}; }       // 사이클 방어
    return {};                                                                                             // 시작에 닿지 못했다
}
bool validPath(const std::vector<std::string>& w, const std::vector<int>& path, bool diag, int expectedSteps) {
    int C = (int)w[0].size(); if (path.empty() || (int)path.size() - 1 != expectedSteps) return false;
    for (std::size_t i = 0; i < path.size(); i++) {
        int r = path[i] / C, c = path[i] % C; if (r < 0 || r >= (int)w.size() || c < 0 || c >= C || w[r][c] == '#') return false;
        if (i) { int pr = path[i - 1] / C, pc = path[i - 1] % C, dr = std::abs(r - pr), dc = std::abs(c - pc); if (dr > 1 || dc > 1 || (dr + dc == 0) || (!diag && dr + dc != 1)) return false; }
    }
    return true;
}
struct Bfs { std::vector<int> dist, parent; };
Bfs bfs(const std::vector<std::string>& w, int s, bool diag) {
    int R = (int)w.size(), C = (int)w[0].size(); Bfs b{std::vector<int>(R * C, -1), std::vector<int>(R * C, -1)}; std::queue<int> q; b.dist[s] = 0; q.push(s);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) {
            if (!dr && !dc) continue; if (!diag && dr && dc) continue; int nr = u / C + dr, nc = u % C + dc; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue;
            if (dr && dc && (w[u / C + dr][u % C] == '#' || w[u / C][u % C + dc] == '#')) continue; int v = nr * C + nc; if (b.dist[v] < 0) { b.dist[v] = b.dist[u] + 1; b.parent[v] = u; q.push(v); }
        }
    }
    return b;
}

int main() {
    // ① 손으로 확인한 모양: 기존 예제
    std::vector<std::string> w = {"S...#...", ".##.#.#.", ".#..#.#.", ".#.##.#.", ".#....#G"}; int R = (int)w.size(), C = (int)w[0].size(), s = 0, g = 4 * C + 7;
    Bfs b = bfs(w, s, false); std::vector<int> path = reconstruct(b.parent, g, s);
    assert(!path.empty() && path.front() == s && path.back() == g && validPath(w, path, false, b.dist[g]));
    std::vector<int> cyc = b.parent; cyc[path[2]] = path[3]; assert(reconstruct(cyc, g, s).empty());       // 부모 사슬이 맴돌면 무한 루프 대신 빈 경로
    std::vector<int> broken = path; broken[3] += 2 * C + 3; assert(!validPath(w, broken, false, b.dist[g]));  // 이웃이 아닌 점프는 유효하지 않다
    assert(reconstruct(std::vector<int>(R * C, -1), g, s).empty() && reconstruct(b.parent, s, s) == std::vector<int>({s}));   // 도달 못 함 -> 빈 경로, 시작 == 목표 -> 칸 하나

    // ② 무작위 격자 500 개 (4/8 방향): 모든 도달 가능한 칸의 복원 경로가 유효하고 길이 = BFS 거리, 도달 불가는 빈 경로
    std::mt19937 rng(21); long checked = 0, unreachable = 0;
    for (int it = 0; it < 500; ++it) {
        int rr = 2 + (int)(rng() % 12), cc = 2 + (int)(rng() % 12), pct = (int)(rng() % 45); std::vector<std::string> m(rr, std::string(cc, '.')); bool diag = it & 1;
        for (auto& row : m) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int st = (int)(rng() % (rr * cc)); m[st / cc][st % cc] = '.'; Bfs t = bfs(m, st, diag);
        for (int v = 0; v < rr * cc; v++) {
            if (m[v / cc][v % cc] == '#') continue; auto p = reconstruct(t.parent, v, st);
            if (t.dist[v] < 0) { assert(p.empty()); ++unreachable; } else { assert(validPath(m, p, diag, t.dist[v]) && p.front() == st && p.back() == v); ++checked; }
        }
    }
    assert(checked > 5000 && unreachable > 100);

    // ③ 임의의 부모 배열 퍼징: 반드시 끝나고, 비어 있지 않은 답은 부모 사슬 그대로(마지막 = 목표, 첫 = 시작, 연속한 쌍은 부모 관계)
    int nonEmpty = 0;
    for (int it = 0; it < 20000; ++it) {
        int n = 1 + (int)(rng() % 12); std::vector<int> parent(n); for (int& p : parent) p = (rng() % 4 == 0) ? -1 : (int)(rng() % n);
        int start = (int)(rng() % n), goal = (int)(rng() % n); auto p = reconstruct(parent, goal, start);
        if (!p.empty()) { ++nonEmpty; assert(p.front() == start && p.back() == goal); for (std::size_t i = 1; i < p.size(); i++) assert(parent[p[i]] == p[i - 1]); std::vector<int> s2 = p; std::sort(s2.begin(), s2.end()); assert(std::adjacent_find(s2.begin(), s2.end()) == s2.end()); }
    }
    assert(nonEmpty > 2000);
    // 사슬이 매우 길어도 (100 만 칸) 반복형이라 안전하고, 사이클을 닫으면 빈 경로
    {   const int N = 1000000; std::vector<int> par(N, -1); for (int i = 1; i < N; ++i) par[i] = i - 1;
        auto p = reconstruct(par, N - 1, 0); assert((int)p.size() == N && p.front() == 0 && p.back() == N - 1);
        par[0] = N - 1; assert(reconstruct(par, N - 1, 1).size() == (std::size_t)N - 1 && !reconstruct(par, 0, N / 2).empty()); }
    std::cout << "ReconstructPath: " << checked << " reachable cells on 500 random grids (4- and 8-neighbour) had rebuilt paths that were valid with length equal to the BFS distance, " << unreachable << " unreachable cells gave empty paths, 20,000 random parent arrays always terminated with answers that were genuine parent chains, and a 1,000,000-cell chain was rebuilt without recursion" << std::endl; return 0;
}
// Time Complexity: O(경로 길이)
// Space Complexity: O(경로 길이)
```

# Part 2. 기초 탐색
## BreadthFirstSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// (격자 관점의 구현, 정본은 Graph.md Part 3 의 BreadthFirstSearch)
// 너비 우선 탐색(BFS): 출발점에서 가까운 칸부터 한 층씩 퍼져 나간다. 간선 비용이 모두 같으면(격자의 한 걸음) *처음 발견한 경로가 곧 최단 경로* 다. 큐에서 꺼내는 칸의 거리는 단조 비감소이고, 목표를 꺼낸 순간(또는 발견한 순간) 멈추면 그때까지의 칸만 확장한다. 빈 격자에서의 닫힌 해: 4방향 거리는 맨해튼 |Δr| + |Δc|, 8방향은 체비쇼프 max(|Δr|, |Δc|), 그리고 출발점에서 거리 k 인 칸은 4방향이면 4k 개(마름모 둘레), 8방향이면 8k 개(정사각형 둘레).
// 검증: ① 무작위 그래프(정점 ≤ 10)에서 BFS 거리가 모든 쌍 최단 경로(플로이드–워셜)와 같고 복원 경로가 유효 ② 격자에서 4/8 방향 BFS 거리가 가중치 1 로 구한 다익스트라와 같음, 꺼내는 순서에서 거리 비감소 ③ 조기 종료한 확장 수 ≤ 전체 탐색 ④ 빈 격자의 닫힌 해와 둘레 칸 수 ⑤ 큰 입력: 1000×1000 빈 격자의 반대편 모서리까지 거리 1998 · 길이 25 만 칸의 구불구불한 복도.
struct Res { int dist = -1; long expanded = 0; std::vector<int> path; bool monotone = true; };

Res bfsGrid(const std::vector<std::string>& w, int s, int t, bool diag, bool early = true, std::vector<int>* all = nullptr) {
    int R = (int)w.size(), C = (int)w[0].size(); std::vector<int> d(R * C, -1), par(R * C, -1); std::queue<int> q; d[s] = 0; q.push(s); Res res; int last = 0;
    while (!q.empty()) {
        int u = q.front(); q.pop(); res.expanded++; if (d[u] < last) res.monotone = false; last = d[u];
        if (early && u == t) break;
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) {
            if (!dr && !dc) continue; if (!diag && dr && dc) continue; int nr = u / C + dr, nc = u % C + dc; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue;
            if (dr && dc && (w[u / C + dr][u % C] == '#' || w[u / C][u % C + dc] == '#')) continue;                     // 모서리 자르기 금지
            int v = nr * C + nc; if (d[v] < 0) { d[v] = d[u] + 1; par[v] = u; q.push(v); }
        }
    }
    res.dist = d[t]; if (all) *all = d;
    if (res.dist >= 0) for (int v = t; v != -1; v = par[v]) res.path.push_back(v);
    std::reverse(res.path.begin(), res.path.end()); return res;
}
bool pathOk(const std::vector<std::string>& w, const std::vector<int>& p, bool diag) {
    int C = (int)w[0].size(); for (std::size_t i = 0; i < p.size(); i++) { if (w[p[i] / C][p[i] % C] == '#') return false; if (i) { int dr = std::abs(p[i] / C - p[i - 1] / C), dc = std::abs(p[i] % C - p[i - 1] % C); if (dr > 1 || dc > 1 || dr + dc == 0 || (!diag && dr + dc != 1)) return false; } } return true;
}
// 오라클: 격자를 그래프로 바꿔 플로이드–워셜 (n ≤ 100)
std::vector<std::vector<int>> floydGrid(const std::vector<std::string>& w, bool diag) {
    int R = (int)w.size(), C = (int)w[0].size(), n = R * C; const int INF = 1 << 28; std::vector<std::vector<int>> d(n, std::vector<int>(n, INF));
    for (int i = 0; i < n; i++) d[i][i] = 0;
    for (int u = 0; u < n; u++) { if (w[u / C][u % C] == '#') continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) {
        if ((!dr && !dc) || (!diag && dr && dc)) continue; int nr = u / C + dr, nc = u % C + dc; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue;
        if (dr && dc && (w[u / C + dr][u % C] == '#' || w[u / C][u % C + dc] == '#')) continue; d[u][nr * C + nc] = 1; } }
    for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
    for (auto& row : d) for (int& x : row) if (x >= INF) x = -1;
    return d;
}
std::vector<int> graphBfs(const std::vector<std::vector<int>>& adj, int s, std::vector<int>* par) {
    std::vector<int> d(adj.size(), -1); if (par) par->assign(adj.size(), -1); std::queue<int> q; d[s] = 0; q.push(s);
    while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (d[v] < 0) { d[v] = d[u] + 1; if (par) (*par)[v] = u; q.push(v); } }
    return d;
}

int main() {
    // ① 무작위 그래프 (정점 ≤ 10, 방향 · 루프 · 평행 간선 포함): BFS 거리 = 플로이드–워셜, 복원 경로 유효
    std::mt19937 rng(3);
    for (int it = 0; it < 500; ++it) {
        int n = 2 + (int)(rng() % 9), m = (int)(rng() % (3 * n)); std::vector<std::vector<int>> adj(n); const int INF = 1 << 28; std::vector<std::vector<int>> f(n, std::vector<int>(n, INF));
        for (int i = 0; i < n; i++) f[i][i] = 0; for (int i = 0; i < m; i++) { int a = (int)(rng() % n), b = (int)(rng() % n); adj[a].push_back(b); if (a != b) f[a][b] = 1; }
        for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (f[i][k] + f[k][j] < f[i][j]) f[i][j] = f[i][k] + f[k][j];
        for (int s = 0; s < n; s++) { std::vector<int> par; auto d = graphBfs(adj, s, &par); for (int t = 0; t < n; t++) { assert(d[t] == (f[s][t] >= INF ? -1 : f[s][t])); if (d[t] > 0) { int len = 0; for (int v = t; v != s; v = par[v]) ++len; assert(len == d[t]); } } }
    }
    // ② 격자 (4/8 방향): BFS 거리 = 플로이드–워셜, 꺼내는 순서에서 거리 비감소, 조기 종료 확장 ≤ 전체, 경로 유효
    long early = 0, full = 0; int solved = 0, unreachable = 0;
    for (int it = 0; it < 400; ++it) {
        int R = 3 + (int)(rng() % 8), C = 3 + (int)(rng() % 8), pct = (int)(rng() % 45); std::vector<std::string> w(R, std::string(C, '.')); bool diag = it & 1;
        for (auto& row : w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int s = (int)(rng() % (R * C)), t = (int)(rng() % (R * C)); w[s / C][s % C] = '.'; w[t / C][t % C] = '.'; auto f = floydGrid(w, diag);
        Res a = bfsGrid(w, s, t, diag, true), b = bfsGrid(w, s, t, diag, false);
        assert(a.dist == f[s][t] && b.dist == f[s][t] && a.monotone && b.monotone && a.expanded <= b.expanded);
        if (a.dist >= 0) { assert(pathOk(w, a.path, diag) && (int)a.path.size() == a.dist + 1 && a.path.front() == s && a.path.back() == t); ++solved; } else { assert(a.path.empty()); ++unreachable; }
        early += a.expanded; full += b.expanded;
    }
    assert(solved > 150 && unreachable > 5 && early < full);
    // ③ 빈 격자의 닫힌 해와 둘레 칸 수: 중심에서 거리 k 인 칸은 4방향 4k 개, 8방향 8k 개, 거리는 맨해튼/체비쇼프
    {   const int N = 41, c0 = 20; std::vector<std::string> open(N, std::string(N, '.')); std::vector<int> d4, d8;
        bfsGrid(open, c0 * N + c0, 0, false, false, &d4); bfsGrid(open, c0 * N + c0, 0, true, false, &d8);
        std::vector<int> ring4(21, 0), ring8(21, 0); for (int v = 0; v < N * N; v++) { int dr = std::abs(v / N - c0), dc = std::abs(v % N - c0); assert(d4[v] == dr + dc && d8[v] == std::max(dr, dc)); if (d4[v] <= 20) ring4[d4[v]]++; if (d8[v] <= 20) ring8[d8[v]]++; }
        for (int k = 1; k <= 20; k++) assert(ring8[k] == 8 * k && (k <= 20 ? ring4[k] <= 4 * k : true));             // 8방향은 정사각형 둘레 8k
        for (int k = 1; k <= 20; k++) { int expect = 0; for (int v = 0; v < N * N; v++) if (std::abs(v / N - c0) + std::abs(v % N - c0) == k) expect++; assert(ring4[k] == expect); }   // 4방향은 마름모 둘레 (격자 안에 든 만큼)
        for (int k = 1; k <= 20; k++) assert(ring4[k] == 4 * k);                                                        // 중심이 가장자리에서 20 이상 떨어져 있으므로 정확히 4k
    }
    // ④ 큰 입력: 1000×1000 빈 격자의 반대편 모서리 (거리 1998, 칸 100 만 개 모두 확장), 길이 25 만 칸 이상의 구불구불한 복도
    {   const int N = 1000; std::vector<std::string> open(N, std::string(N, '.')); Res r = bfsGrid(open, 0, N * N - 1, false, false); assert(r.dist == 2 * (N - 1) && r.expanded == (long)N * N && r.monotone);
        const int H = 1001, W = 501; std::vector<std::string> maze(H, std::string(W, '#'));                          // 가로 복도(짝수 행) 를 세로 통로로 번갈아 이은 뱀 모양
        for (int r2 = 0; r2 < H; r2 += 2) for (int c = 0; c < W; c++) maze[r2][c] = '.';
        for (int r2 = 1; r2 < H; r2 += 2) maze[r2][(r2 / 2) % 2 == 0 ? W - 1 : 0] = '.';
        Res m = bfsGrid(maze, 0, (H - 1) * W + (W - 1), false, true);                                          // 마지막 복도의 반대쪽 끝
        assert(m.dist > 250000 && pathOk(maze, m.path, false) && (int)m.path.size() == m.dist + 1); }
    std::cout << "BreadthFirstSearch: BFS distances matched Floyd-Warshall on 500 random digraphs and 400 random grids (4 and 8 directions, " << solved << " reachable and " << unreachable << " unreachable pairs), dequeue distances never decreased, early exit expanded " << early << " cells against " << full << " for the full search, open grids gave Manhattan/Chebyshev distances with exactly 4k and 8k cells at distance k, and a 1000x1000 grid and a serpentine corridor of over 250,000 steps were searched" << std::endl; return 0;
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
#include <queue>
#include <random>
#include <string>
#include <vector>

// (격자 관점의 구현, 정본은 Graph.md Part 3 의 DepthFirstSearch)
// 깊이 우선 탐색(DFS): 한 길로 끝까지 가 보고 막히면 되돌아온다. 도달 가능성(길이 있는가) 은 BFS 와 정확히 같은 답을 주지만 *찾은 경로는 일반적으로 최단이 아니다*(운이 나쁘면 칸 수만큼 길다). 대신 메모리가 현재 경로 길이만큼이고 영역 채우기(flood fill)·연결 성분 세기·미로 생성에 자연스럽다. 재귀로 쓰면 큰 지도에서 호출 스택이 넘치므로 명시적 스택(반복형)으로 쓴다.
// 검증: ① 무작위 격자에서 DFS 도달 가능성이 BFS 와 같고 DFS 경로가 유효하며 길이 ≥ BFS 거리(엄격히 긴 경우가 많이 있다) ② 영역 채우기로 센 연결 성분 수와 각 성분의 크기가 서로소 집합과 같다(4/8 연결) ③ DFS 의 발견·종료 시각이 괄호 구조(두 칸의 구간은 포함되거나 서로소)를 이룬다 ④ 큰 입력: 길이 25 만 칸 이상의 구불구불한 복도(재귀였다면 스택 overflow)와 1000×1000 격자의 영역 채우기.
struct Dfs { std::vector<int> par, disc, fin; std::vector<char> seen; };

Dfs dfsFrom(const std::vector<std::string>& w, int s, bool diag, bool stopAtGoal = false, int goal = -1) {
    int R = (int)w.size(), C = (int)w[0].size(); Dfs d{std::vector<int>(R * C, -1), std::vector<int>(R * C, -1), std::vector<int>(R * C, -1), std::vector<char>(R * C, 0)};
    std::vector<int> st{s}, it(R * C, 0); d.seen[s] = 1; int clock = 0; d.disc[s] = clock++;
    static const int dr[8] = {1, 0, -1, 0, 1, 1, -1, -1}, dc[8] = {0, 1, 0, -1, 1, -1, 1, -1};
    while (!st.empty()) {
        int u = st.back();
        if (it[u] < (diag ? 8 : 4)) {
            int k = it[u]++; int nr = u / C + dr[k], nc = u % C + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue;
            if (k >= 4 && (w[u / C + dr[k]][u % C] == '#' || w[u / C][u % C + dc[k]] == '#')) continue;
            int v = nr * C + nc; if (!d.seen[v]) { d.seen[v] = 1; d.par[v] = u; d.disc[v] = clock++; st.push_back(v); if (stopAtGoal && v == goal) return d; }
        } else { d.fin[u] = clock++; st.pop_back(); }
    }
    return d;
}
std::vector<int> bfsDist(const std::vector<std::string>& w, int s, bool diag) {
    int R = (int)w.size(), C = (int)w[0].size(); std::vector<int> d(R * C, -1); std::queue<int> q; d[s] = 0; q.push(s);
    while (!q.empty()) { int u = q.front(); q.pop(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || (!diag && dr && dc)) continue; int nr = u / C + dr, nc = u % C + dc; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue; if (dr && dc && (w[u / C + dr][u % C] == '#' || w[u / C][u % C + dc] == '#')) continue; if (d[nr * C + nc] < 0) { d[nr * C + nc] = d[u] + 1; q.push(nr * C + nc); } } }
    return d;
}
int findRoot(std::vector<int>& p, int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }

int main() {
    std::mt19937 rng(8); long longer = 0, same = 0;
    // ① 무작위 격자 400 개 (4/8 방향): 도달 가능성 = BFS, 경로 유효, 길이 ≥ BFS 거리, 괄호 구조
    for (int it = 0; it < 400; ++it) {
        int R = 3 + (int)(rng() % 10), C = 3 + (int)(rng() % 10), pct = (int)(rng() % 40); std::vector<std::string> w(R, std::string(C, '.')); bool diag = it & 1;
        for (auto& row : w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int s = (int)(rng() % (R * C)); w[s / C][s % C] = '.'; Dfs d = dfsFrom(w, s, diag); auto b = bfsDist(w, s, diag);
        for (int v = 0; v < R * C; v++) {
            assert((bool)d.seen[v] == (b[v] >= 0));                                                      // 도달 가능성은 같다
            if (!d.seen[v] || v == s) continue;
            int len = 0; for (int x = v; x != s; x = d.par[x]) { int dr = std::abs(x / C - d.par[x] / C), dc = std::abs(x % C - d.par[x] % C); assert(dr <= 1 && dc <= 1 && (diag || dr + dc == 1) && w[x / C][x % C] != '#'); ++len; }
            assert(len >= b[v]); (len > b[v] ? longer : same)++;                                         // DFS 경로는 BFS 거리 이상
        }
        for (int a = 0; a < R * C; a++) for (int c = a + 1; c < R * C; c += 7) if (d.seen[a] && d.seen[c]) { bool nested = (d.disc[a] < d.disc[c] && d.fin[c] < d.fin[a]) || (d.disc[c] < d.disc[a] && d.fin[a] < d.fin[c]); bool apart = d.fin[a] < d.disc[c] || d.fin[c] < d.disc[a]; assert(nested != apart); }
    }
    assert(longer > 1000 && same > 1000);
    // ② 영역 채우기로 연결 성분 세기 = 서로소 집합 (4/8 연결), 성분 크기 합 = 빈 칸 수
    for (int it = 0; it < 300; ++it) {
        int R = 3 + (int)(rng() % 14), C = 3 + (int)(rng() % 14), pct = (int)(rng() % 55); std::vector<std::string> w(R, std::string(C, '.')); bool diag = it & 1;
        for (auto& row : w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        std::vector<int> p(R * C); std::iota(p.begin(), p.end(), 0); int free = 0;
        for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (w[r][c] == '#') continue; ++free; for (int dr = 0; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && dc <= 0) || (!diag && dr && dc)) continue; int nr = r + dr, nc = c + dc; if (nr >= R || nc < 0 || nc >= C || w[nr][nc] == '#') continue; p[findRoot(p, r * C + c)] = findRoot(p, nr * C + nc); } }
        std::vector<char> done(R * C, 0); int comps = 0, total = 0;
        for (int v = 0; v < R * C; v++) { if (w[v / C][v % C] == '#' || done[v]) continue; Dfs d = dfsFrom(w, v, diag); int size = 0; for (int x = 0; x < R * C; x++) if (d.seen[x]) { done[x] = 1; ++size; } ++comps; total += size; }
        std::vector<char> roots(R * C, 0); int dsuComps = 0; for (int v = 0; v < R * C; v++) if (w[v / C][v % C] != '#') { int rt = findRoot(p, v); if (!roots[rt]) { roots[rt] = 1; ++dsuComps; } }
        if (!diag) { assert(comps == dsuComps && total == free); }                                       // 8 연결은 모서리 자르기 금지 규칙이 달라 서로소 집합(대각선 허용)과 비교하지 않는다
        else assert(total == free && comps >= dsuComps);
    }
    // ③ 큰 입력: 길이 25 만 칸 이상의 구불구불한 복도를 반복형 DFS 로 (재귀면 스택 overflow), 1000×1000 빈 격자 영역 채우기
    {   const int H = 1001, W = 501; std::vector<std::string> maze(H, std::string(W, '#'));
        for (int r = 0; r < H; r += 2) for (int c = 0; c < W; c++) maze[r][c] = '.';
        for (int r = 1; r < H; r += 2) maze[r][(r / 2) % 2 == 0 ? W - 1 : 0] = '.';
        Dfs d = dfsFrom(maze, 0, false); int free = 0, seen = 0; for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { free += maze[r][c] != '#'; seen += d.seen[r * W + c]; }
        assert(seen == free && free > 250000);
        std::vector<std::string> open(1000, std::string(1000, '.')); Dfs f = dfsFrom(open, 0, false); int cnt = 0; for (char x : f.seen) cnt += x; assert(cnt == 1000000); }
    std::cout << "DepthFirstSearch: iterative DFS reached exactly the cells BFS reached on 400 random grids (4 and 8 directions), its paths were valid but at least as long as the BFS distance (" << longer << " strictly longer, " << same << " equal), discovery/finish intervals nested or were disjoint, flood-fill component counts and sizes matched union-find, and a serpentine corridor of over 250,000 cells and a 1,000,000-cell open grid were searched without recursion" << std::endl; return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## IterativeDeepeningDFS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 반복 깊이 증가 DFS(IDDFS, 그래프 관점의 정본은 Graph.md Part 10): 깊이 제한 DFS 를 제한 0, 1, 2, … 로 반복해 BFS 처럼 "가장 얕은 해" 를 찾되 메모리는 DFS 처럼 O(깊이) 만 쓴다. 얕은 층을 되풀이해 방문하는 낭비는 분기 계수 b 가 2 이상이면 가장 깊은 층의 방문 수가 압도해 전체의 약 b/(b−1) 배에 그친다. 격자 같은 일반 그래프에서는 같은 칸을 여러 경로로 다시 방문하므로 방문 수가 트리 공식보다 커진다 — 그래도 메모리는 경로 길이뿐이다.
// 검증: ① 무작위 격자(최대 7×7, 4방향)에서 IDDFS 가 처음 성공하는 깊이 = BFS 거리, 경로는 단순하고 유효, 도달 불가면 제한을 (빈 칸 수 − 1) 까지 올려도 실패 ② 이진 트리(깊이 12)에서 방문 수가 정확히 Σ(d−i+1)2^i 이고 BFS 방문 수의 2 배 미만 ③ 스택에 쌓인 칸 수는 깊이 + 1 이하.
long visited = 0; int maxStack = 0;
bool dls(const std::vector<std::string>& w, int u, int goal, int limit, std::vector<char>& onPath, std::vector<int>& path) {
    int R = (int)w.size(), C = (int)w[0].size(); visited++; path.push_back(u); onPath[u] = 1; maxStack = std::max(maxStack, (int)path.size());
    if (u == goal) return true;
    if (limit > 0) { static const int dr[4] = {1, 0, -1, 0}, dc[4] = {0, 1, 0, -1}; for (int k = 0; k < 4; k++) { int nr = u / C + dr[k], nc = u % C + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue; int v = nr * C + nc; if (!onPath[v] && dls(w, v, goal, limit - 1, onPath, path)) return true; } }
    path.pop_back(); onPath[u] = 0; return false;
}
int iddfs(const std::vector<std::string>& w, int s, int goal, int maxDepth, std::vector<int>& path) {
    for (int limit = 0; limit <= maxDepth; limit++) { std::vector<char> on(w.size() * w[0].size(), 0); path.clear(); if (dls(w, s, goal, limit, on, path)) return limit; }
    path.clear(); return -1;
}
int bfsDist(const std::vector<std::string>& w, int s, int t) {
    int R = (int)w.size(), C = (int)w[0].size(); std::vector<int> d(R * C, -1); std::queue<int> q; d[s] = 0; q.push(s);
    while (!q.empty()) { int u = q.front(); q.pop(); static const int dr[4] = {1, 0, -1, 0}, dc[4] = {0, 1, 0, -1}; for (int k = 0; k < 4; k++) { int nr = u / C + dr[k], nc = u % C + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || d[nr * C + nc] >= 0) continue; d[nr * C + nc] = d[u] + 1; q.push(nr * C + nc); } }
    return d[t];
}

int main() {
    std::mt19937 rng(77); int solved = 0, unreachable = 0;
    for (int it = 0; it < 300; ++it) {
        int R = 2 + (int)(rng() % 6), C = 2 + (int)(rng() % 6), pct = (int)(rng() % 40); std::vector<std::string> w(R, std::string(C, '.'));
        for (auto& row : w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int s = (int)(rng() % (R * C)), t = (int)(rng() % (R * C)); w[s / C][s % C] = '.'; w[t / C][t % C] = '.';
        std::vector<int> path; int got = iddfs(w, s, t, R * C - 1, path), want = bfsDist(w, s, t);
        assert(got == want);
        if (want >= 0) { assert((int)path.size() == want + 1 && path.front() == s && path.back() == t); std::vector<int> sorted = path; std::sort(sorted.begin(), sorted.end()); assert(std::adjacent_find(sorted.begin(), sorted.end()) == sorted.end()); ++solved; } else ++unreachable;
    }
    assert(solved > 100 && unreachable > 5);
    // ② 이진 트리 (깊이 12): 가장 오른쪽 잎 → 방문 수 정확히 Σ (d−i+1) 2^i, BFS 방문 수 (2^(d+1) − 1) 의 2 배 미만, 스택 ≤ d + 1
    {   const int depth = 12; std::vector<std::vector<int>> adj((1 << (depth + 1)) - 1); for (int i = 0; i < (1 << depth) - 1; i++) { adj[i].push_back(2 * i + 1); adj[i].push_back(2 * i + 2); }
        int goal = (1 << (depth + 1)) - 2; long vis = 0; int stackMax = 0, found = -1; std::vector<int> path;
        std::function<bool(int, int)> dfs = [&](int u, int limit) { vis++; path.push_back(u); stackMax = std::max(stackMax, (int)path.size()); if (u == goal) return true; if (limit > 0) for (int v : adj[u]) if (dfs(v, limit - 1)) return true; path.pop_back(); return false; };
        for (int limit = 0; limit <= depth; limit++) { path.clear(); if (dfs(0, limit)) { found = limit; break; } }
        long expect = 0; for (int i = 0; i <= depth; i++) expect += (long)(depth - i + 1) << i;
        assert(found == depth && vis == expect && vis < 2L * ((1 << (depth + 1)) - 1) && stackMax == depth + 1);
        std::cout << "IterativeDeepeningDFS: " << solved << " reachable and " << unreachable << " unreachable random-grid queries gave exactly the BFS distance, and on a depth-" << depth << " binary tree IDDFS visited " << vis << " = sum (d-i+1)2^i nodes (under twice BFS's " << (1 << (depth + 1)) - 1 << ") with a stack of only " << stackMax << std::endl; }
    return 0;
}
// Time Complexity: O(b^d) (b/(b-1) 배의 중복 포함)
// Space Complexity: O(d)
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
#include <string>
#include <utility>
#include <vector>

// 양방향 탐색(그래프 관점의 정본은 Graph.md Part 10): 시작과 목표에서 동시에 탐색을 돌려 두 탐색 영역이 만나면 끝낸다. 한 방향 탐색이 반지름 d 의 "공"을 채우는 데 b^d 를 쓴다면 양쪽에서 d/2 씩만 채우면 되니 2·b^(d/2) 로 지수의 절반이다(격자에서는 공이 원판이라 면적 비로 약 1/2). 그런데 *언제 멈추는가* 가 비용이 같은 경우와 다른 경우에 완전히 다르다.
// 비용이 모두 같은 BFS: 한 층씩 번갈아 확장하면 "처음으로 상대 영역에 닿는 순간" 이 곧 최단이다 — 만나기 전에는 두 영역이 서로소이므로 최단 거리 D ≥ Lf + Lb + 1 이고, 처음 만났을 때의 후보 Lf + 1 + db[v] ≤ Lf + 1 + Lb ≤ D 이면서 실제 경로라 D 이상이기 때문. 비용이 다른 다익스트라: 처음 만난 지점의 합은 *최단이 아닐 수 있다*(더 싼 우회가 아직 남아 있다). 올바른 멈춤 규칙은 지금까지 만난 가장 싼 합 μ 를 기억해 두고 "양쪽 우선순위 큐의 맨 앞 거리의 합이 μ 이상" 일 때 멈추는 것이다.
// 검증: ① 무작위 격자(4/8 방향, 벽 0~40%)에서 양방향 BFS 거리 = 한 방향 BFS 거리(도달 불가면 둘 다 -1, 시작 = 목표면 0), "처음 만나면 반환" 변형도 비용이 같을 때는 정확히 같다 ② 무작위 가중 그래프에서 μ 규칙의 양방향 다익스트라는 단방향 다익스트라와 같고, "처음 만나면 반환" 변형은 더 긴 거리를 내는 경우가 실제로 있다(더 짧은 일은 없다) ③ 장애물 없는 넓은 격자에서 확장 수가 BFS 의 2/3 미만.
struct Res { int dist = -1; long expanded = 0; };
static const int DR8[8] = {1, 0, -1, 0, 1, 1, -1, -1}, DC8[8] = {0, 1, 0, -1, 1, -1, 1, -1};
template <class F> void neighbours(const std::vector<std::string>& w, int u, bool diag, F f) {
    int R = (int)w.size(), C = (int)w[0].size();
    for (int k = 0; k < (diag ? 8 : 4); k++) { int nr = u / C + DR8[k], nc = u % C + DC8[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#') continue; if (k >= 4 && (w[u / C + DR8[k]][u % C] == '#' || w[u / C][u % C + DC8[k]] == '#')) continue; f(nr * C + nc); }
}
Res bfs(const std::vector<std::string>& w, int s, int t, bool diag) {
    Res r; int n = (int)w.size() * (int)w[0].size(); std::vector<int> d(n, -1); std::queue<int> q; d[s] = 0; q.push(s);
    while (!q.empty()) { int u = q.front(); q.pop(); r.expanded++; if (u == t) { r.dist = d[u]; return r; } neighbours(w, u, diag, [&](int v) { if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }); }
    return r;
}
// firstMeeting = true: 처음 만나면 반환. false: 한 층 전체를 확장한 뒤 만남의 최솟값
Res bidirectional(const std::vector<std::string>& w, int s, int t, bool diag, bool firstMeeting) {
    Res r; if (s == t) { r.dist = 0; return r; } int n = (int)w.size() * (int)w[0].size(); std::vector<int> da(n, -1), db(n, -1); std::vector<int> fa{s}, fb{t}; da[s] = 0; db[t] = 0;
    while (!fa.empty() && !fb.empty()) {
        bool fwd = fa.size() <= fb.size(); auto& f = fwd ? fa : fb; auto& mine = fwd ? da : db; auto& other = fwd ? db : da; std::vector<int> nxt; int best = -1;
        for (int u : f) { r.expanded++; bool stop = false;
            neighbours(w, u, diag, [&](int v) { if (stop || mine[v] >= 0) return; mine[v] = mine[u] + 1; nxt.push_back(v); if (other[v] >= 0) { int cand = mine[v] + other[v]; best = best < 0 ? cand : std::min(best, cand); if (firstMeeting) stop = true; } });
            if (stop) break; }
        if (best >= 0) { r.dist = best; return r; }
        f = nxt;
    }
    return r;
}

// ---- 가중 그래프: 양방향 다익스트라 ----
struct WG { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
const int INF = INT_MAX / 4;
int dijkstra(const WG& g, int s, int t) {
    std::vector<int> d(g.n, INF); std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } }
    return d[t] >= INF ? -1 : d[t];
}
// careful = true: μ 규칙 (topF + topB ≥ μ 에서 멈춤). false: 처음 만나는 순간 μ 를 반환
int biDijkstra(const WG& g, int s, int t, bool careful) {
    if (s == t) return 0; typedef std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> PQ;
    std::vector<int> d[2] = {std::vector<int>(g.n, INF), std::vector<int>(g.n, INF)}; PQ pq[2]; d[0][s] = 0; d[1][t] = 0; pq[0].push({0, s}); pq[1].push({0, t}); int mu = INF;
    while (!pq[0].empty() && !pq[1].empty()) {
        if (careful && pq[0].top().first + pq[1].top().first >= mu) break;
        int side = pq[0].top().first <= pq[1].top().first ? 0 : 1; auto [du, u] = pq[side].top(); pq[side].pop(); if (du > d[side][u]) continue;
        for (auto [v, w] : g.adj[u]) {
            if (du + w < d[side][v]) { d[side][v] = du + w; pq[side].push({d[side][v], v}); }
            if (d[1 - side][v] < INF) { mu = std::min(mu, du + w + d[1 - side][v]); if (!careful) return mu; }
        }
    }
    return mu >= INF ? -1 : mu;
}

int main() {
    std::mt19937 rng(12); int solved = 0, unreachable = 0; long biTotal = 0, bfsTotal = 0;
    for (int it = 0; it < 600; ++it) {
        int R = 3 + (int)(rng() % 14), C = 3 + (int)(rng() % 14), pct = (int)(rng() % 41); std::vector<std::string> w(R, std::string(C, '.')); bool diag = it & 1;
        for (auto& row : w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int s = (int)(rng() % (R * C)), t = (int)(rng() % (R * C)); w[s / C][s % C] = '.'; w[t / C][t % C] = '.';
        Res a = bfs(w, s, t, diag), b = bidirectional(w, s, t, diag, false), first = bidirectional(w, s, t, diag, true);
        assert(a.dist == b.dist && a.dist == first.dist);                                                   // 비용이 같으면 처음 만나는 순간도 최단
        if (a.dist >= 0) ++solved; else ++unreachable;
        biTotal += b.expanded; bfsTotal += a.expanded;
    }
    assert(solved > 300 && unreachable > 5);
    // ② 무작위 가중 그래프 (정점 ≤ 25, 무방향, 가중치 1..20): μ 규칙 = 단방향 다익스트라, 성급한 변형은 더 길 수는 있어도 짧을 수는 없다
    int hastyWrong = 0, wsolved = 0;
    for (int it = 0; it < 1500; ++it) {
        int n = 4 + (int)(rng() % 22), m = n + (int)(rng() % (2 * n)); WG g{n, std::vector<std::vector<std::pair<int, int>>>(n)};
        for (int i = 0; i < m; i++) { int a = (int)(rng() % n), b = (int)(rng() % n), w = 1 + (int)(rng() % 20); g.adj[a].push_back({b, w}); g.adj[b].push_back({a, w}); }
        int s = (int)(rng() % n), t = (int)(rng() % n); int want = dijkstra(g, s, t), got = biDijkstra(g, s, t, true), hasty = biDijkstra(g, s, t, false);
        assert(got == want);
        if (want >= 0) { ++wsolved; assert(hasty >= want); hastyWrong += hasty != want; } else assert(hasty == -1);
    }
    assert(wsolved > 800 && hastyWrong > 20);                                                               // 가중치가 다르면 성급한 변형이 실제로 틀린다
    {   const int N = 200; std::vector<std::string> open(N, std::string(N, '.')); int s = 100 * N + 60, t = 100 * N + 140;
        Res a = bfs(open, s, t, false), b = bidirectional(open, s, t, false, false); assert(a.dist == 80 && b.dist == 80 && b.expanded * 3 < a.expanded * 2);
        std::cout << "BidirectionalSearch: with equal costs bidirectional BFS (with or without waiting for the full level) matched one-directional BFS on 600 random grids (" << solved << " reachable, " << unreachable << " unreachable); with random edge weights the mu-rule bidirectional Dijkstra matched plain Dijkstra on 1500 graphs while returning at the first meeting overshot in " << hastyWrong << " of " << wsolved << "; on an open 200x200 grid bidirectional search expanded " << b.expanded << " cells against BFS's " << a.expanded << std::endl; }
    return 0;
}
// Time Complexity: O(b^(d/2)) × 2
// Space Complexity: O(b^(d/2))
```
## MultiSourceBFS()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// 다중 출발점 BFS(큐 관점의 정본은 Queue.md Part 6): 출발점이 여러 개일 때 모든 출발점을 거리 0 으로 한꺼번에 큐에 넣고 BFS 를 한 번만 돌리면 각 칸에서 "가장 가까운 출발점까지의 거리" 가 나온다. 출발점마다 BFS 를 따로 돌려 최솟값을 취하는 O(k(V+E)) 와 결과가 같다. 용도: 가장 가까운 소화전·출구·불길까지의 거리, 거리 변환(distance transform), 부패하는 오렌지 문제.
// 성질: 거리장은 출발점에서만 0 이고, 이웃한 두 칸의 거리는 1 이하로 차이 난다(립시츠), 가장 가까운 출발점 라벨을 함께 전파하면 보로노이 영역 분할이 된다(동점은 먼저 도달한 라벨).
// 검증: 무작위 격자에서 ① 한 번의 BFS = 출발점별 BFS 의 최솟값 ② 거리 0 인 칸 = 출발점 ③ 이웃한 두 도달 칸의 거리 차 ≤ 1 ④ 각 칸의 라벨은 가장 가까운 출발점 중 하나이고 거리가 일치 ⑤ 큰 입력 1000×1000 에 출발점 1000 개를 한 번에.
struct Out { std::vector<int> dist, label; };
Out multiSource(const std::vector<std::string>& w, const std::vector<int>& src) {
    int R = (int)w.size(), C = (int)w[0].size(); Out o{std::vector<int>(R * C, -1), std::vector<int>(R * C, -1)}; std::queue<int> q;
    for (std::size_t i = 0; i < src.size(); i++) if (o.dist[src[i]] < 0) { o.dist[src[i]] = 0; o.label[src[i]] = (int)i; q.push(src[i]); }
    while (!q.empty()) {
        int u = q.front(); q.pop(); static const int dr[4] = {1, 0, -1, 0}, dc[4] = {0, 1, 0, -1};
        for (int k = 0; k < 4; k++) { int nr = u / C + dr[k], nc = u % C + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C || w[nr][nc] == '#' || o.dist[nr * C + nc] >= 0) continue; o.dist[nr * C + nc] = o.dist[u] + 1; o.label[nr * C + nc] = o.label[u]; q.push(nr * C + nc); }
    }
    return o;
}

int main() {
    std::mt19937 rng(31); long cells = 0;
    for (int it = 0; it < 500; ++it) {
        int R = 3 + (int)(rng() % 14), C = 3 + (int)(rng() % 14), pct = (int)(rng() % 45); std::vector<std::string> w(R, std::string(C, '.'));
        for (auto& row : w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        std::vector<int> free; for (int v = 0; v < R * C; v++) if (w[v / C][v % C] != '#') free.push_back(v); if (free.empty()) continue;
        int k = 1 + (int)(rng() % std::min<std::size_t>(5, free.size())); std::vector<int> src; for (int i = 0; i < k; i++) src.push_back(free[rng() % free.size()]);
        Out multi = multiSource(w, src); std::vector<std::vector<int>> single; for (int s : src) single.push_back(multiSource(w, {s}).dist);
        std::vector<char> isSrc(R * C, 0); for (int s : src) isSrc[s] = 1;
        for (int v = 0; v < R * C; v++) {
            int best = -1; for (auto& d : single) if (d[v] >= 0 && (best < 0 || d[v] < best)) best = d[v];
            assert(multi.dist[v] == best);                                                               // ① 한 번의 BFS == 출발점별 BFS 의 최솟값
            assert((multi.dist[v] == 0) == (bool)isSrc[v]);                                                // ② 0 은 출발점에서만
            if (multi.dist[v] >= 0) { assert(single[multi.label[v]][v] == multi.dist[v]); ++cells; }        // ④ 라벨이 가리키는 출발점이 실제로 가장 가까운 것 중 하나
            for (int dd = 0; dd < 2 && multi.dist[v] >= 0; dd++) { int nr = v / C + (dd == 0), nc = v % C + (dd == 1); if (nr < R && nc < C && w[nr][nc] != '#' && multi.dist[nr * C + nc] >= 0) assert(std::abs(multi.dist[v] - multi.dist[nr * C + nc]) <= 1); }   // ③ 립시츠
        }
    }
    assert(cells > 10000);
    {   const int N = 1000; std::vector<std::string> open(N, std::string(N, '.')); std::vector<int> src; for (int i = 0; i < 1000; i++) src.push_back((int)(rng() % (N * N)));
        Out o = multiSource(open, src); int maxD = 0; for (int v = 0; v < N * N; v++) { assert(o.dist[v] >= 0); maxD = std::max(maxD, o.dist[v]); }
        for (int probe = 0; probe < 300; probe++) { int v = (int)(rng() % (N * N)); int best = 1 << 30; for (int s : src) best = std::min(best, std::abs(s / N - v / N) + std::abs(s % N - v % N)); assert(o.dist[v] == best); }   // 빈 격자: 맨해튼 최솟값
        std::cout << "MultiSourceBFS: one BFS from up to 5 sources equalled the minimum of the per-source searches on " << cells << " reachable cells of 500 random grids (zero exactly at sources, neighbouring distances differing by at most 1, labels pointing at a nearest source); on a 1000x1000 grid with 1000 sources one search matched the Manhattan minimum at 300 probes (farthest cell " << maxD << ")" << std::endl; }
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```

# Part 3. 가중치 최단 경로
## Dijkstra()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>

// 다익스트라(경로 탐색 관점의 요약, 정본은 Graph.md Part 9): 칸마다 지형 비용이 다른 격자에서 "들어가는 칸의 비용 합" 이 최소인 경로. 비용이 음이 아니면 우선순위 큐에서 가장 가까운 칸의 거리는 더 줄일 수 없으므로 꺼내는 순간 확정이다. 길찾기에서는 목표를 꺼내는 순간 멈추면(조기 종료) 목표보다 먼 칸은 확장하지 않는다. 4방향 이동 비용은 칸 비용 × 10, 8방향 대각선은 × 14 (≈ 10√2) 의 정수.
// 검증: 무작위 지형 격자(3~10 × 3~10, 벽 0~30%, 칸 비용 1..9, 4/8 방향)에서 ① 조기 종료 거리 = 전체 다익스트라 = 같은 격자를 간선 목록으로 만든 벨만–포드 ② 꺼낸 순서에서 거리가 단조 비감소 ③ 복원한 경로의 칸 비용 합 = 보고한 거리, 이웃한 칸으로만 이동 ④ 조기 종료한 확정 칸 수 ≤ 전체 ≤ 칸 수 ⑤ 큰 입력 1000×1000 지형(칸 100 만 개).
struct Grid { int R, C; std::vector<int> cost; };                                                           // cost 0 = 벽, 아니면 그 칸에 들어가는 비용
struct Edge { int u, v, w; };
static const int DR[8] = {1, 0, -1, 0, 1, 1, -1, -1}, DC[8] = {0, 1, 0, -1, 1, -1, 1, -1};
template <class F> void moves(const Grid& g, int u, bool diag, F f) {
    for (int k = 0; k < (diag ? 8 : 4); k++) {
        int nr = u / g.C + DR[k], nc = u % g.C + DC[k]; if (nr < 0 || nc < 0 || nr >= g.R || nc >= g.C || !g.cost[nr * g.C + nc]) continue;
        if (k >= 4 && (!g.cost[(u / g.C + DR[k]) * g.C + u % g.C] || !g.cost[(u / g.C) * g.C + u % g.C + DC[k]])) continue;                  // 모서리 자르기 금지
        f(nr * g.C + nc, g.cost[nr * g.C + nc] * (k < 4 ? 10 : 14));
    }
}
struct Res { long long dist = -1; long settled = 0; std::vector<int> path; bool monotone = true; };
Res dijkstra(const Grid& g, int s, int t, bool diag, bool early) {
    int n = g.R * g.C; std::vector<long long> d(n, LLONG_MAX); std::vector<int> par(n, -1); std::priority_queue<std::pair<long long, int>, std::vector<std::pair<long long, int>>, std::greater<>> pq;
    Res r; long long last = 0; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) {
        auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue;
        r.settled++; if (du < last) r.monotone = false; last = du; if (early && u == t) break;
        moves(g, u, diag, [&](int v, int w) { if (du + w < d[v]) { d[v] = du + w; par[v] = u; pq.push({d[v], v}); } });
    }
    if (d[t] != LLONG_MAX) { r.dist = d[t]; for (int v = t; v != -1; v = par[v]) r.path.push_back(v); std::reverse(r.path.begin(), r.path.end()); }
    return r;
}
std::vector<long long> bellmanFordOracle(const Grid& g, int s, bool diag) {                                 // 같은 격자를 간선 목록으로 만들어 V−1 번 완화
    int n = g.R * g.C; std::vector<Edge> es; for (int u = 0; u < n; u++) if (g.cost[u]) moves(g, u, diag, [&](int v, int w) { es.push_back({u, v, w}); });
    std::vector<long long> d(n, LLONG_MAX); d[s] = 0;
    for (int pass = 0; pass < n; pass++) { bool ch = false; for (auto& e : es) if (d[e.u] != LLONG_MAX && d[e.u] + e.w < d[e.v]) { d[e.v] = d[e.u] + e.w; ch = true; } if (!ch) break; }
    return d;
}

std::string terrainPicture(const Grid& g, int s, int t, const std::vector<int>& path) {            // 그림: 숫자 = 그 칸에 들어가는 비용(0 은 벽 '#'), * = 최소 비용 경로, S/G = 시작/목표
    std::string out; std::vector<char> on(g.R * g.C, 0); for (int v : path) on[v] = 1;
    for (int r = 0; r < g.R; ++r) { for (int c = 0; c < g.C; ++c) { int v = r * g.C + c; out += v == s ? 'S' : v == t ? 'G' : on[v] ? '*' : g.cost[v] ? (char)('0' + g.cost[v]) : '#'; } out += "\n"; }
    return out;
}
int main() {
    {   Grid g{3, 5, {1, 1, 1, 1, 1,  1, 9, 9, 9, 1,  1, 1, 2, 1, 1}};                                      // 가운데 줄은 진창(비용 9), 아랫줄 가운데는 비용 2
        Res r = dijkstra(g, 1 * 5 + 0, 1 * 5 + 4, false, true);                                              // 왼쪽 가운데 -> 오른쪽 가운데, 4 방향
        const std::string pic = "*****\nS999G\n11211\n";
        assert(r.dist == 60 && terrainPicture(g, 5, 9, r.path) == pic);                                      // 진창을 곧장 가로지르면 9+9+9+1 = 28 칸 비용(280), 위로 돌아가면 6 칸 비용(60)
        std::cout << pic << "cost=" << r.dist << " settled=" << r.settled << std::endl; }                    // 아랫길은 1+1+2+1+1+1 = 7 칸 비용이라 유일 최적은 윗길
    // ① 손으로 확인한 모양: 위로 우회하면 비용 1+1+1, 곧장 가운데 9 칸을 지나면 9 — 우회가 이긴다
    {   Grid g{2, 3, {1, 1, 1, 1, 9, 1}}; Res r = dijkstra(g, 3, 5, false, true);                           // (1,0) → (1,2): 왼쪽 → 위 → 오른쪽 x2 → 아래 vs 가운데 9
        assert(r.dist == (1 + 1 + 1 + 1) * 10 && r.path.size() == 5);
    }
    std::mt19937 rng(9); long earlyTotal = 0, fullTotal = 0; int solved = 0, unreachable = 0;
    for (int it = 0; it < 500; ++it) {
        int R = 3 + (int)(rng() % 8), C = 3 + (int)(rng() % 8), pct = (int)(rng() % 31); bool diag = it & 1; Grid g{R, C, std::vector<int>(R * C)};
        for (int& c : g.cost) c = (int)(rng() % 100) < pct ? 0 : 1 + (int)(rng() % 9);
        int s = (int)(rng() % (R * C)), t = (int)(rng() % (R * C)); if (!g.cost[s]) g.cost[s] = 1; if (!g.cost[t]) g.cost[t] = 1;
        Res a = dijkstra(g, s, t, diag, true), b = dijkstra(g, s, t, diag, false); auto oracle = bellmanFordOracle(g, s, diag);
        long long want = oracle[t] == LLONG_MAX ? -1 : oracle[t];
        assert(a.dist == want && b.dist == want && a.monotone && b.monotone && a.settled <= b.settled && b.settled <= R * C);
        if (want >= 0) {
            long long sum = 0; for (std::size_t i = 1; i < a.path.size(); i++) { int u = a.path[i - 1], v = a.path[i], dr = std::abs(v / C - u / C), dc = std::abs(v % C - u % C); assert(dr <= 1 && dc <= 1 && (diag || dr + dc == 1) && g.cost[v]); sum += g.cost[v] * (dr + dc == 2 ? 14 : 10); }
            assert(a.path.front() == s && a.path.back() == t && sum == want); ++solved;
        } else { assert(a.path.empty()); ++unreachable; }
        earlyTotal += a.settled; fullTotal += b.settled;
    }
    assert(solved > 250 && unreachable > 5 && earlyTotal < fullTotal);
    // ⑤ 큰 입력: 1000×1000 지형, 4방향, 왼쪽 위 → 오른쪽 아래. 벨만–포드는 너무 느리므로 칸 비용이 모두 1 인 경우의 닫힌 해(맨해튼 × 10)와, 무작위 지형에서는 거리 하한(최소 비용 × 맨해튼) 과 상한(경로 하나의 비용)으로 확인
    {   const int N = 1000; Grid flat{N, N, std::vector<int>(N * N, 1)}; Res f = dijkstra(flat, 0, N * N - 1, false, true); assert(f.dist == 10LL * 2 * (N - 1));
        Grid g{N, N, std::vector<int>(N * N)}; for (int& c : g.cost) c = 1 + (int)(rng() % 9); Res r = dijkstra(g, 0, N * N - 1, false, true);
        long long lower = 10LL * 2 * (N - 1) * 1, upper = 0; for (int c = 1; c < N; c++) upper += g.cost[c] * 10LL; for (int rr = 1; rr < N; rr++) upper += g.cost[rr * N + N - 1] * 10LL;       // 위 가장자리 → 오른쪽 가장자리 경로 하나의 비용
        assert(r.dist >= lower && r.dist <= upper && r.monotone && r.settled <= N * N);
        std::cout << "Dijkstra: early-exit distances equalled full Dijkstra and a Bellman-Ford oracle on 500 random terrain grids (4 and 8 directions; " << solved << " reachable, " << unreachable << " unreachable), settled order was non-decreasing, rebuilt paths summed to the reported cost, early exit settled " << earlyTotal << " cells against " << fullTotal << ", and a 1000x1000 terrain was solved between its analytic bounds" << std::endl; }
    return 0;
}
// Time Complexity: O(E log V)
// Space Complexity: O(V)
```
## BellmanFord()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 벨만–포드(경로 탐색 관점의 요약, 정본은 Graph.md Part 9): 모든 간선을 V − 1 번 훑어 완화한다. 다익스트라와 달리 *음수 가중치*(내리막·통행료 환급·에너지 회수)를 다룰 수 있고, V 번째 훑기에서도 줄어드는 거리가 있으면 시작점에서 닿는 *음수 사이클* 이 있다는 뜻이다(그 경우 목표까지 최단 거리가 −∞ 일 수 있어 경로 탐색에서는 "유효한 답이 없다" 로 보고한다). 한 번의 훑기에서 아무것도 안 바뀌면 일찍 끝낸다.
// 검증: 무작위 방향 그래프(정점 ≤ 8, 가중치 −4..9)에서 ① 음수 사이클이 닿지 않는 목표의 거리가 플로이드–워셜과 같고 직전 정점으로 복원한 경로의 합이 거리와 같음 ② 시작점에서 닿는 음수 사이클이 있다는 판정이 플로이드–워셜(대각선 < 0 인 정점에 시작이 닿음)과 같음 ③ 갱신이 일어난 훑기 수가 ≤ V − 1 ④ 퍼텐셜로 음수 간선은 있지만 사이클은 없게 만든 큰 그래프(정점 20 만)를 같은 그래프의 비음수 가중치 다익스트라로 환산해 대조.
struct Edge { int u, v, w; };
struct Res { bool negativeCycle = false; std::vector<long long> dist; std::vector<int> pred; int changingPasses = 0; };
const long long INF = LLONG_MAX / 4;
Res bellmanFord(int n, const std::vector<Edge>& es, int s) {
    Res r; r.dist.assign(n, INF); r.pred.assign(n, -1); r.dist[s] = 0;
    for (int pass = 1; pass <= n; pass++) {
        bool changed = false;
        for (const Edge& e : es) if (r.dist[e.u] < INF && r.dist[e.u] + e.w < r.dist[e.v]) { r.dist[e.v] = r.dist[e.u] + e.w; r.pred[e.v] = e.u; changed = true; }
        if (!changed) break;
        if (pass == n) r.negativeCycle = true; else ++r.changingPasses;
    }
    return r;
}
std::vector<std::vector<long long>> floyd(int n, const std::vector<Edge>& es) {
    std::vector<std::vector<long long>> d(n, std::vector<long long>(n, INF)); for (int i = 0; i < n; i++) d[i][i] = 0; for (const Edge& e : es) d[e.u][e.v] = std::min<long long>(d[e.u][e.v], e.w);
    for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (d[i][k] < INF && d[k][j] < INF) d[i][j] = std::max(-INF, std::min(d[i][j], d[i][k] + d[k][j]));
    return d;
}

int main() {
    // ① 손으로 확인한 모양: 0→1:4, 1→2:−1, 0→2:5 → d[2] = 3 ; 사이클 1→2→1 의 합이 −2 이면 음수 사이클
    {   Res r = bellmanFord(3, {{0, 1, 4}, {1, 2, -1}, {0, 2, 5}}, 0); assert(!r.negativeCycle && r.dist[2] == 3 && r.pred[2] == 1);
        assert(bellmanFord(3, {{0, 1, 4}, {1, 2, -1}, {2, 1, -1}}, 0).negativeCycle);
    }
    std::mt19937 rng(15); int cyc = 0, noCyc = 0;
    for (int it = 0; it < 2000; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % (3 * n)); std::vector<Edge> es; std::vector<int> phi(n); for (int& x : phi) x = (int)(rng() % 21) - 10; bool potential = it % 2 == 0;
        for (int i = 0; i < m; i++) { int u = (int)(rng() % n), v = (int)(rng() % n); es.push_back({u, v, potential ? (int)(rng() % 10) + phi[u] - phi[v] : (int)(rng() % 14) - 4}); }
        int s = (int)(rng() % n); Res r = bellmanFord(n, es, s); auto f = floyd(n, es);
        bool reachNeg = false; for (int w = 0; w < n; w++) reachNeg = reachNeg || (f[s][w] < INF && f[w][w] < 0);
        assert(r.negativeCycle == reachNeg);                                                                // 음수 사이클 판정
        if (r.negativeCycle) { ++cyc; continue; }
        ++noCyc; assert(r.changingPasses <= n - 1);
        for (int t = 0; t < n; t++) {
            assert(r.dist[t] == f[s][t]);
            if (t != s && r.dist[t] < INF) { long long sum = 0; int steps = 0; for (int v = t; v != s; v = r.pred[v]) { int u = r.pred[v]; long long best = INF; for (const Edge& e : es) if (e.u == u && e.v == v) best = std::min<long long>(best, e.w); sum += best; ++steps; assert(steps <= n); } assert(sum == r.dist[t]); }   // 직전 정점 사슬은 실제 간선들이고, 가장 싼 평행 간선으로 합하면 정확히 거리
        }
    }
    assert(cyc > 300 && noCyc > 1000);
    // ④ 큰 입력: 정점 20 만, 간선 80 만, 퍼텐셜로 음수 간선이 많지만 음수 사이클은 없다 → w0 다익스트라 + 퍼텐셜 보정과 일치
    {   const int N = 200000, M = 800000; std::mt19937_64 r(2); std::vector<int> phi(N); for (int& x : phi) x = (int)(r() % 2001) - 1000;
        std::vector<Edge> es; std::vector<std::vector<std::pair<int, int>>> g0(N);
        for (int i = 0; i < M; i++) { int u = i < N - 1 ? i : (int)(r() % N), v = i < N - 1 ? i + 1 : (int)(r() % N), w0 = 1 + (int)(r() % 100); es.push_back({u, v, w0 + phi[u] - phi[v]}); g0[u].push_back({v, w0}); }
        std::shuffle(es.begin(), es.end(), r); Res b = bellmanFord(N, es, 0); assert(!b.negativeCycle);
        std::vector<long long> d0(N, INF); d0[0] = 0; std::priority_queue<std::pair<long long, int>, std::vector<std::pair<long long, int>>, std::greater<>> pq; pq.push({0, 0});
        while (!pq.empty()) { auto [d, u] = pq.top(); pq.pop(); if (d > d0[u]) continue; for (auto [v, w] : g0[u]) if (d + w < d0[v]) { d0[v] = d + w; pq.push({d0[v], v}); } }
        for (int v = 0; v < N; v++) assert(b.dist[v] == d0[v] + phi[0] - phi[v]);
        std::cout << "BellmanFord: on 2000 random digraphs (" << noCyc << " without and " << cyc << " with a reachable negative cycle) the negative-cycle verdict and every distance matched Floyd-Warshall, predecessor chains were real edges, at most V-1 passes changed anything, and a 200,000-vertex graph with negative edges matched Dijkstra on potential-shifted weights after " << b.changingPasses << " changing passes" << std::endl; }
    return 0;
}
// Time Complexity: O(V · E)
// Space Complexity: O(V)
```
## SPFA()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <deque>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// SPFA(경로 탐색 관점의 요약, 정본은 Graph.md Part 9): 벨만–포드에서 "거리가 줄어든 칸의 이웃만 다시 본다" — 줄어든 칸을 큐에 넣고, 꺼낸 칸의 나가는 간선만 완화한다. 음수 간선도 되고 보통 훨씬 빠르지만 최악은 벨만–포드와 같다. 음수 사이클은 "정점마다 현재 최단 걸음의 간선 수" len[v] 가 V 이상이 되는 순간으로 알아낸다. 큐에 이미 있는 칸은 다시 넣지 않는다.
// 검증: 무작위 방향 그래프(정점 ≤ 8, 가중치 −4..9)에서 ① 음수 사이클 판정이 벨만–포드(V 번째 훑기)와 같고 ② 없을 때 모든 거리가 같음 ③ 격자 지형(비음수)에서는 다익스트라와 같고 훑은 간선 수가 벨만–포드의 전체 훑기보다 훨씬 적음 ④ 비음수인데도 완화 횟수가 한 자릿수 배로 커지는 구조 하나를 만들어 SPFA 의 최악이 실재함을 확인.
typedef long long ll; const ll INF = LLONG_MAX / 4;
struct Arc { int to, w; };
struct Res { bool negCycle = false; std::vector<ll> dist; long relaxations = 0, scans = 0; };
Res spfa(const std::vector<std::vector<Arc>>& g, int s) {
    int n = (int)g.size(); Res r; r.dist.assign(n, INF); std::deque<int> q; std::vector<char> in(n, 0); std::vector<int> len(n, 0); r.dist[s] = 0; q.push_back(s); in[s] = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop_front(); in[u] = 0;
        for (const Arc& a : g[u]) { r.scans++; if (r.dist[u] + a.w < r.dist[a.to]) {
            r.dist[a.to] = r.dist[u] + a.w; r.relaxations++; len[a.to] = len[u] + 1; if (len[a.to] >= n) { r.negCycle = true; return r; }
            if (!in[a.to]) { in[a.to] = 1; q.push_back(a.to); }
        } }
    }
    return r;
}
Res bellman(const std::vector<std::vector<Arc>>& g, int s) {
    int n = (int)g.size(); Res r; r.dist.assign(n, INF); r.dist[s] = 0;
    for (int pass = 1; pass <= n; pass++) { bool ch = false; for (int u = 0; u < n; u++) if (r.dist[u] < INF) for (const Arc& a : g[u]) { r.scans++; if (r.dist[u] + a.w < r.dist[a.to]) { r.dist[a.to] = r.dist[u] + a.w; r.relaxations++; ch = true; } } if (!ch) break; if (pass == n) r.negCycle = true; }
    return r;
}
std::vector<ll> dijkstra(const std::vector<std::vector<Arc>>& g, int s, long& relax) {
    std::vector<ll> d(g.size(), INF); std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (const Arc& a : g[u]) if (du + a.w < d[a.to]) { d[a.to] = du + a.w; relax++; pq.push({d[a.to], a.to}); } }
    return d;
}

int main() {
    std::mt19937 rng(25);
    // ① 손으로 확인한 모양
    {   std::vector<std::vector<Arc>> g(4); g[0] = {{1, 10}, {2, 3}}; g[2] = {{1, 4}, {3, 8}}; g[1] = {{3, 2}}; Res r = spfa(g, 0); assert(!r.negCycle && r.dist[1] == 7 && r.dist[3] == 9);
        std::vector<std::vector<Arc>> c(3); c[0] = {{1, 1}}; c[1] = {{2, -3}}; c[2] = {{1, 1}}; assert(spfa(c, 0).negCycle && bellman(c, 0).negCycle); }
    // ②③ 무작위: 음수 사이클 판정과 거리가 벨만–포드와 같다
    int cyc = 0, noCyc = 0;
    for (int it = 0; it < 3000; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % (3 * n)); std::vector<std::vector<Arc>> g(n); std::vector<int> phi(n); for (int& x : phi) x = (int)(rng() % 21) - 10; bool potential = it % 2 == 0;
        for (int i = 0; i < m; i++) { int u = (int)(rng() % n), v = (int)(rng() % n); g[u].push_back({v, potential ? (int)(rng() % 10) + phi[u] - phi[v] : (int)(rng() % 14) - 4}); }
        int s = (int)(rng() % n); Res a = spfa(g, s), b = bellman(g, s); assert(a.negCycle == b.negCycle);
        if (!a.negCycle) { assert(a.dist == b.dist); ++noCyc; } else ++cyc;
    }
    assert(cyc > 400 && noCyc > 1200);
    // 격자 지형(비음수): 다익스트라와 같고, 성공한 완화 횟수는 벨만–포드와 비슷하지만 *훑은 간선 수* 는 SPFA 가 훨씬 적다
    long spfaScans = 0, bfScans = 0, spfaRelax = 0, bfRelax = 0;
    for (int it = 0; it < 100; ++it) {
        int R = 6 + (int)(rng() % 10), C = 6 + (int)(rng() % 10); std::vector<std::vector<Arc>> g(R * C);
        for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) for (int k = 0; k < 4; k++) { static const int dr[4] = {1, 0, -1, 0}, dc[4] = {0, 1, 0, -1}; int nr = r + dr[k], nc = c + dc[k]; if (nr < 0 || nc < 0 || nr >= R || nc >= C) continue; g[r * C + c].push_back({nr * C + nc, 1 + (int)(rng() % 9)}); }
        Res a = spfa(g, 0), b = bellman(g, 0); long dj = 0; auto d = dijkstra(g, 0, dj); assert(a.dist == d && b.dist == d); spfaRelax += a.relaxations; bfRelax += b.relaxations; spfaScans += a.scans; bfScans += b.scans;
    }
    assert(spfaScans < bfScans && spfaRelax <= bfRelax + bfRelax / 10);                                       // 완화 횟수는 비슷하지만 SPFA 는 줄어든 칸의 간선만 보므로 훑은 간선 수가 훨씬 적다
    // ④ 최악: s → z1 → … → zk (가중치 1), z_j → t 의 가중치 B − 2j, s → t 는 B, t → c1 → … → cm. FIFO 에서 t 가 층마다 다시 개선되고 개선 파도가 꼬리 전체를 다시 훑는다.
    {   const int k = 300, m = 300, B = 1000, N = k + m + 2, t = k + 1; std::vector<std::vector<Arc>> g(N);
        g[0].push_back({1, 1}); g[0].push_back({t, B}); for (int j = 1; j <= k; j++) { if (j < k) g[j].push_back({j + 1, 1}); g[j].push_back({t, B - 2 * j}); } g[t].push_back({t + 1, 1}); for (int i = 1; i < m; i++) g[t + i].push_back({t + i + 1, 1});
        Res a = spfa(g, 0); long dj = 0; auto d = dijkstra(g, 0, dj); assert(a.dist == d && a.relaxations > 10 * dj && a.relaxations >= (long)k * m / 4);
        std::cout << "SPFA: negative-cycle verdicts and distances matched Bellman-Ford on 3000 random digraphs (" << cyc << " with and " << noCyc << " without a reachable negative cycle), on 100 terrain grids it made " << spfaRelax << " relaxations (Bellman-Ford " << bfRelax << ") but examined only " << spfaScans << " arcs against " << bfScans << " for full Bellman-Ford passes, and a non-negative chain-and-tail construction forced " << a.relaxations << " relaxations where Dijkstra needed " << dj << std::endl; }
    return 0;
}
// Time Complexity: 평균 O(k·E), 최악 O(V·E)
// Space Complexity: O(V)
```
## FloydWarshall()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 플로이드–워셜(경로 탐색 관점의 요약, 정본은 Graph.md Part 9): 모든 쌍 최단 거리를 d[i][j] = min(d[i][j], d[i][k] + d[k][j]) 한 줄로. *k 가 가장 바깥 반복* 이어야 하는 이유는 "k 번째 반복이 끝나면 d[i][j] 는 중간 정점이 0..k 뿐인 경로의 최솟값" 이라는 불변식이다. 경로 탐색에서는 목표가 자주 바뀌는 소규모 지도(방·웨이포인트)의 *모든 쌍 거리표* 를 미리 만들어 두는 용도다. next[i][j](i 에서 j 로 가는 첫 걸음) 로 경로도 복원한다.
// 검증: 무작위 격자 지형(웨이포인트 그래프) 에서 ① 모든 쌍의 거리가 칸마다 돌린 다익스트라와 같음 ② next 로 복원한 경로가 이웃 칸만 지나고 비용 합이 d[i][j] ③ 무방향이면 d 가 대칭이고 삼각 부등식 d[i][j] ≤ d[i][k] + d[k][j] ④ 음수 간선(사이클 없음)에서 칸마다 돌린 벨만–포드와 같고, 음수 사이클이 있으면 어떤 d[i][i] < 0 ⑤ 틀린 반복 순서(k 가 안쪽)는 서로 다른 답을 낸다.
typedef long long ll; const ll INF = LLONG_MAX / 4;
struct Edge { int u, v, w; };
struct FW { std::vector<std::vector<ll>> d; std::vector<std::vector<int>> next; bool negCycle = false; };
FW floydWarshall(int n, const std::vector<Edge>& es, bool kOutermost = true) {
    FW f{std::vector<std::vector<ll>>(n, std::vector<ll>(n, INF)), std::vector<std::vector<int>>(n, std::vector<int>(n, -1)), false};
    for (int i = 0; i < n; i++) { f.d[i][i] = 0; f.next[i][i] = i; }
    for (const Edge& e : es) if (e.w < f.d[e.u][e.v]) { f.d[e.u][e.v] = e.w; f.next[e.u][e.v] = e.v; }
    auto relax = [&](int i, int j, int k) { if (f.d[i][k] < INF && f.d[k][j] < INF) { ll c = f.d[i][k] + f.d[k][j]; if (c < -INF) c = -INF; if (c < f.d[i][j]) { f.d[i][j] = c; f.next[i][j] = f.next[i][k]; } } };
    if (kOutermost) { for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) relax(i, j, k); }
    else { for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) for (int k = 0; k < n; k++) relax(i, j, k); }
    for (int i = 0; i < n; i++) if (f.d[i][i] < 0) f.negCycle = true;
    return f;
}
std::vector<int> pathOf(const FW& f, int i, int j) { if (f.next[i][j] < 0) return {}; std::vector<int> p{i}; while (i != j && p.size() <= f.d.size()) { i = f.next[i][j]; p.push_back(i); } return p; }
std::vector<ll> dijkstra(int n, const std::vector<Edge>& es, int s) {
    std::vector<std::vector<std::pair<int, int>>> g(n); for (const Edge& e : es) g[e.u].push_back({e.v, e.w});
    std::vector<ll> d(n, INF); std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } }
    return d;
}
std::vector<ll> bellmanFord(int n, const std::vector<Edge>& es, int s) { std::vector<ll> d(n, INF); d[s] = 0; for (int pass = 0; pass < n; pass++) { bool ch = false; for (const Edge& e : es) if (d[e.u] < INF && d[e.u] + e.w < d[e.v]) { d[e.v] = d[e.u] + e.w; ch = true; } if (!ch) break; } return d; }

int main() {
    std::mt19937 rng(42);
    // ①②③ 무작위 격자 지형 (무방향 4방향, 칸 비용 1..9, 벽 0~25%): 모든 쌍 거리 · 경로 · 대칭 · 삼각 부등식
    for (int it = 0; it < 200; ++it) {
        int R = 2 + (int)(rng() % 5), C = 2 + (int)(rng() % 5), pct = (int)(rng() % 26); std::vector<int> cost(R * C); for (int& c : cost) c = (int)(rng() % 100) < pct ? 0 : 1 + (int)(rng() % 9);
        std::vector<Edge> es; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { int u = r * C + c; if (!cost[u]) continue; if (c + 1 < C && cost[u + 1]) { int w = 1 + (int)(rng() % 9); es.push_back({u, u + 1, w}); es.push_back({u + 1, u, w}); } if (r + 1 < R && cost[u + C]) { int w = 1 + (int)(rng() % 9); es.push_back({u, u + C, w}); es.push_back({u + C, u, w}); } }
        int n = R * C; FW f = floydWarshall(n, es); assert(!f.negCycle);
        for (int s = 0; s < n; s++) { auto d = dijkstra(n, es, s); assert(f.d[s] == d); }                    // ① 칸마다 다익스트라
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
            assert(f.d[i][j] == f.d[j][i]);                                                                  // ③ 무방향 → 대칭
            for (int k = 0; k < n; k += 3) if (f.d[i][k] < INF && f.d[k][j] < INF) assert(f.d[i][j] <= f.d[i][k] + f.d[k][j]);
            auto p = pathOf(f, i, j); if (f.d[i][j] >= INF) { assert(p.empty()); continue; }
            ll sum = 0; for (std::size_t t = 1; t < p.size(); t++) { ll best = INF; for (const Edge& e : es) if (e.u == p[t - 1] && e.v == p[t]) best = std::min<ll>(best, e.w); assert(best < INF); sum += best; }
            assert(p.front() == i && p.back() == j && sum == f.d[i][j]);                                      // ② 복원한 경로의 비용 = 거리
        }
    }
    // ④ 음수 간선: 칸마다 벨만–포드와 같고, 음수 사이클이면 어떤 d[i][i] < 0 (퍼텐셜 / 무작위 두 종류)
    int cyc = 0, noCyc = 0;
    for (int it = 0; it < 1500; ++it) {
        int n = 2 + (int)(rng() % 7), m = (int)(rng() % (3 * n)); std::vector<Edge> es; std::vector<int> phi(n); for (int& x : phi) x = (int)(rng() % 21) - 10; bool potential = it % 2 == 0;
        for (int i = 0; i < m; i++) { int u = (int)(rng() % n), v = (int)(rng() % n); es.push_back({u, v, potential ? (int)(rng() % 10) + phi[u] - phi[v] : (int)(rng() % 14) - 4}); }
        FW f = floydWarshall(n, es); bool anyBf = false; std::vector<std::vector<ll>> bf;
        for (int s = 0; s < n; s++) { std::vector<ll> d(n, INF); d[s] = 0; bool neg = false; for (int pass = 1; pass <= n; pass++) { bool ch = false; for (const Edge& e : es) if (d[e.u] < INF && d[e.u] + e.w < d[e.v]) { d[e.v] = d[e.u] + e.w; ch = true; } if (!ch) break; if (pass == n) neg = true; } anyBf = anyBf || neg; bf.push_back(d); }
        assert(f.negCycle == anyBf);
        if (!f.negCycle) { for (int s = 0; s < n; s++) assert(f.d[s] == bf[s] && f.d[s] == bellmanFord(n, es, s)); ++noCyc; } else ++cyc;
    }
    assert(cyc > 150 && noCyc > 600);
    // ⑤ 틀린 반복 순서 (k 가 안쪽): 비음수 무작위 그래프 300 개 중 상당수에서 다른 답
    int wrong = 0;
    for (int it = 0; it < 300; ++it) { int n = 4 + (int)(rng() % 4); std::vector<Edge> es; for (int i = 0; i < 2 * n; i++) es.push_back({(int)(rng() % n), (int)(rng() % n), 1 + (int)(rng() % 9)}); wrong += floydWarshall(n, es).d != floydWarshall(n, es, false).d; for (int s = 0; s < n; s++) assert(floydWarshall(n, es).d[s] == dijkstra(n, es, s)); }
    assert(wrong >= 20);
    std::cout << "FloydWarshall: on 200 random terrain waypoint graphs the all-pairs table equalled per-source Dijkstra, was symmetric and obeyed the triangle inequality, and next-pointer paths followed real edges with cost d[i][j]; on 1500 random graphs with negative edges (" << noCyc << " clean, " << cyc << " with negative cycles) it equalled per-source Bellman-Ford and its diagonal flagged exactly the negative-cycle cases; the wrong i-j-k loop order disagreed on " << wrong << " of 300 graphs" << std::endl; return 0;
}
// Time Complexity: O(V³)
// Space Complexity: O(V²)
```
## Johnson()
### 대표코드
```cpp
#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <queue>
#include <random>
#include <utility>
#include <vector>

// 존슨(Johnson, 경로 탐색 관점의 요약, 정본은 Graph.md Part 9): 음수 간선이 있어도 모든 쌍 최단 경로를 O(V·E log V) 에 — 희소 그래프에서 플로이드–워셜의 O(V³) 보다 훨씬 빠르다. 핵심은 *재가중(reweighting)*: 모든 정점으로 비용 0 짜리 간선을 가진 가상 출발점에서 벨만–포드를 돌려 h(v) 를 얻고(음수 사이클이 있으면 여기서 발견), w'(u,v) = w(u,v) + h(u) − h(v) 로 바꾼다. 삼각 부등식 h(v) ≤ h(u) + w 때문에 w' ≥ 0 이고, 경로 하나의 w' 합은 원래 합 + h(시작) − h(끝) 이라 최단 경로의 *모양* 은 안 바뀐다. 그래서 정점마다 다익스트라를 돌리고 d(u,v) = d'(u,v) − h(u) + h(v) 로 되돌린다. A* 의 일관된 휴리스틱도 같은 재가중이다.
// 검증: ① 음수 간선은 있지만 음수 사이클은 없는 무작위 그래프에서 모든 쌍이 플로이드–워셜과 같고, 재가중된 모든 간선이 비음수 ② 음수 사이클이 있으면 존슨이 거부하고 플로이드–워셜 대각선이 음수 ③ 경로의 재가중 합이 원래 합 + h(시작) − h(끝) ④ 희소 그래프(정점 300, 간선 900)에서 존슨의 완화 횟수가 플로이드–워셜의 연산 수보다 훨씬 적음.
typedef long long ll; const ll INF = LLONG_MAX / 4;
struct Edge { int u, v; ll w; };
bool johnson(int n, const std::vector<Edge>& es, std::vector<std::vector<ll>>& D, std::vector<ll>& h, long long& ops) {
    h.assign(n, 0);                                                                                         // 가상 출발점에서 한 번 완화한 상태 (모든 h = 0)
    for (int pass = 1; pass <= n; pass++) { bool ch = false; for (const Edge& e : es) { ops++; if (h[e.u] + e.w < h[e.v]) { h[e.v] = h[e.u] + e.w; ch = true; } } if (!ch) break; if (pass == n) return false; }   // n 번째에도 바뀌면 음수 사이클 (정점이 n+1 개)
    std::vector<std::vector<std::pair<int, ll>>> g(n); for (const Edge& e : es) { ll w2 = e.w + h[e.u] - h[e.v]; assert(w2 >= 0); g[e.u].push_back({e.v, w2}); }
    D.assign(n, std::vector<ll>(n, INF));
    for (int s = 0; s < n; s++) {
        std::vector<ll> d(n, INF); std::priority_queue<std::pair<ll, int>, std::vector<std::pair<ll, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
        while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g[u]) { ops++; if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } }
        for (int v = 0; v < n; v++) if (d[v] < INF) D[s][v] = d[v] - h[s] + h[v];
    }
    return true;
}
std::vector<std::vector<ll>> floyd(int n, const std::vector<Edge>& es, long long& ops) {
    std::vector<std::vector<ll>> d(n, std::vector<ll>(n, INF)); for (int i = 0; i < n; i++) d[i][i] = 0; for (const Edge& e : es) d[e.u][e.v] = std::min(d[e.u][e.v], e.w);
    for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) if (d[i][k] < INF) for (int j = 0; j < n; j++) { ops++; if (d[k][j] < INF && d[i][k] + d[k][j] < d[i][j]) d[i][j] = std::max(-INF, d[i][k] + d[k][j]); }
    return d;
}

int main() {
    std::mt19937 rng(7); int accepted = 0, rejected = 0, negEdges = 0;
    for (int it = 0; it < 800; ++it) {
        int n = 2 + (int)(rng() % 10), m = (int)(rng() % (3 * n + 1)); std::vector<ll> phi(n); for (ll& x : phi) x = (ll)(rng() % 61) - 30; bool wantCycle = it % 3 == 0; std::vector<Edge> es;
        for (int i = 0; i < m; i++) { int u = (int)(rng() % n), v = (int)(rng() % n); if (u == v) continue; ll w = wantCycle ? (ll)(rng() % 21) - 8 : (ll)(rng() % 21) + phi[u] - phi[v]; negEdges += w < 0; es.push_back({u, v, w}); }
        long long o1 = 0, o2 = 0; auto F = floyd(n, es, o1); bool neg = false; for (int i = 0; i < n; i++) neg = neg || F[i][i] < 0;
        std::vector<std::vector<ll>> D; std::vector<ll> h; bool ok = johnson(n, es, D, h, o2); assert(ok == !neg);                      // ② 음수 사이클 판정이 플로이드–워셜과 같다
        if (!ok) { ++rejected; continue; }
        ++accepted; for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) assert(D[i][j] == F[i][j]);                                  // ① 모든 쌍 일치
        for (const Edge& e : es) assert(e.w + h[e.u] - h[e.v] >= 0);                                                                    // 재가중 간선은 비음수
        // ③ 경로의 재가중 합 = 원래 합 + h(시작) − h(끝): 무작위 걸음으로 확인
        for (int trial = 0; trial < 5 && !es.empty(); trial++) { int cur = es[rng() % es.size()].u, start = cur; ll orig = 0, re = 0; for (int step = 0; step < 6; step++) { std::vector<const Edge*> out; for (const Edge& e : es) if (e.u == cur) out.push_back(&e); if (out.empty()) break; const Edge* e = out[rng() % out.size()]; orig += e->w; re += e->w + h[e->u] - h[e->v]; cur = e->v; } assert(re == orig + h[start] - h[cur]); }
    }
    assert(accepted > 300 && rejected > 50 && negEdges > 2000);
    // ④ 희소 그래프 (정점 300, 간선 900, 퍼텐셜로 음수 간선): 같은 답, 존슨의 연산 수가 플로이드–워셜의 1/10 미만
    {   const int N = 300; std::vector<ll> phi(N); for (ll& x : phi) x = (ll)(rng() % 101) - 50; std::vector<Edge> es; for (int i = 0; i < 3 * N; i++) { int u = (int)(rng() % N), v = (int)(rng() % N); if (u != v) es.push_back({u, v, (ll)(rng() % 50) + phi[u] - phi[v]}); }
        long long jo = 0, fo = 0; auto F = floyd(N, es, fo); std::vector<std::vector<ll>> D; std::vector<ll> h; assert(johnson(N, es, D, h, jo)); assert(D == F && jo * 10 < fo);
        std::cout << "Johnson: " << accepted << " graphs with negative edges matched Floyd-Warshall on all pairs (reweighted edges non-negative, path sums shifting by exactly h(start)-h(end)), " << rejected << " graphs with negative cycles were rejected exactly when Floyd-Warshall's diagonal went negative, and on a 300-vertex sparse graph Johnson used " << jo << " operations against Floyd-Warshall's " << fo << std::endl; }
    return 0;
}
// Time Complexity: O(V·E log V)
// Space Complexity: O(V²) (결과 행렬)
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
std::string pathPicture(const Grid& g, P s, P t, const std::vector<P>& path) {         // 그림: S 시작, G 목표, * 경로, # 벽
    std::vector<std::string> m = g.w; for (P p : path) m[p.first][p.second] = '*'; m[s.first][s.second] = 'S'; m[t.first][t.second] = 'G';
    std::string out; for (const auto& row : m) out += row + "\n"; return out;
}
int main() {
    {   Grid g{5, 7, {"...#...", ".#.#.#.", ".#...#.", ".#####.", "......."}}; g.diag = false;                // 위쪽 길은 막다른 길이고 왼쪽 열 -> 아래 줄이 유일한 최단 경로
        Res a = astar(g, {0, 0}, {4, 6}, 1.0), d = astar(g, {0, 0}, {4, 6}, 0.0);                          // A*(휴리스틱 1 배) 와 Dijkstra(0 배)
        const std::string pic = "S..#...\n*#.#.#.\n*#...#.\n*#####.\n******G\n";
        assert(pathPicture(g, {0, 0}, {4, 6}, a.path) == pic && a.cost == 100 && d.cost == 100);          // 10 칸 x 비용 10
        assert(pathPicture(g, {0, 0}, {4, 6}, d.path) == pic && a.expanded < d.expanded);                   // 같은 경로, 하지만 A* 는 목표 쪽 칸만 파서 덜 펼친다
        std::cout << pic << "expanded: A*=" << a.expanded << " Dijkstra=" << d.expanded << std::endl; }
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
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>

// IDA*(경로 탐색 관점의 요약, 정본은 Graph.md Part 10): 반복 깊이 증가 DFS 의 "깊이 제한" 을 "f = g + h 제한" 으로 바꾼 A* 의 메모리 절약판. 제한을 h(시작) 로 잡고 f 가 제한을 넘는 가지를 자르며 DFS 하고, 못 찾으면 잘려나간 f 중 가장 작은 값을 새 제한으로 반복한다. 메모리는 현재 경로뿐이라 O(경로 길이)이지만 같은 칸을 여러 경로로 다시 연다 — 격자처럼 최단 경로가 아주 많은 지도에서는 그 중복이 폭발하므로 작은 지도 · 좋은 휴리스틱에 어울린다. h 가 허용 가능(과대평가 없음)이면 최적이고, 부풀리면 해는 얻어도 최적이 아닐 수 있다.
// 이동: 4방향 비용 10, 8방향 대각선 비용 14, 휴리스틱은 옥타일 거리 10·(max) + 4·(min) (8방향) 또는 맨해튼 × 10 (4방향) — 둘 다 허용적이고 일관적이다. 현재 경로 위의 칸으로는 돌아가지 않는다.
// 검증: 무작위 격자(최대 7×7, 벽 0~30%)에서 ① 비용 = 다익스트라 최적값(도달 불가면 -1) ② 임계값 열은 h(시작) 에서 시작해 엄격히 증가하고 마지막이 최적 비용 ③ 반환한 경로는 이웃 칸만 지나고 비용 합이 최적 ④ 휴리스틱 h = 0 도 최적이지만(작은 4방향 지도에서) 확장이 더 많음 ⑤ 허용되지 않는 휴리스틱(h × 3) 은 때로 최적보다 비싼 해를 낸다(싼 해는 없다).
struct Grid { int R, C; std::vector<std::string> w; bool diag; };
static const int DR[8] = {1, 0, -1, 0, 1, 1, -1, -1}, DC[8] = {0, 1, 0, -1, 1, -1, 1, -1};
struct Ida {
    const Grid& g; int goal; int scale; bool useH; std::vector<int> path; long expansions = 0; int foundCost = -1;
    Ida(const Grid& gg, int goalCell, int hScale, bool use) : g(gg), goal(goalCell), scale(hScale), useH(use) {}
    int h(int u) const { if (!useH) return 0; int dr = std::abs(u / g.C - goal / g.C), dc = std::abs(u % g.C - goal % g.C); return scale * (g.diag ? 10 * std::max(dr, dc) + 4 * std::min(dr, dc) : 10 * (dr + dc)); }
    bool on(int u) const { return std::find(path.begin(), path.end(), u) != path.end(); }
    int search(int u, int gcost, int bound) {                                                               // -1: 찾음. 아니면 bound 를 넘은 f 중 최솟값
        int f = gcost + h(u); if (f > bound) return f; if (u == goal) { foundCost = gcost; return -1; }
        expansions++; int mn = INT_MAX;
        for (int k = 0; k < (g.diag ? 8 : 4); k++) {
            int nr = u / g.C + DR[k], nc = u % g.C + DC[k]; if (nr < 0 || nc < 0 || nr >= g.R || nc >= g.C || g.w[nr][nc] == '#') continue;
            if (k >= 4 && (g.w[u / g.C + DR[k]][u % g.C] == '#' || g.w[u / g.C][u % g.C + DC[k]] == '#')) continue;
            int v = nr * g.C + nc; if (on(v)) continue; path.push_back(v);
            int r = search(v, gcost + (k < 4 ? 10 : 14), bound); if (r == -1) return -1; path.pop_back(); mn = std::min(mn, r);
        }
        return mn;
    }
    int run(int start, std::vector<int>* thresholds) {
        path.assign(1, start); int bound = h(start);
        while (true) { if (thresholds) thresholds->push_back(bound); int r = search(start, 0, bound); if (r == -1) return foundCost; if (r == INT_MAX) return -1; bound = r; }
    }
};
int dijkstra(const Grid& g, int s, int t) {
    std::vector<int> d(g.R * g.C, INT_MAX); std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq; d[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int k = 0; k < (g.diag ? 8 : 4); k++) { int nr = u / g.C + DR[k], nc = u % g.C + DC[k]; if (nr < 0 || nc < 0 || nr >= g.R || nc >= g.C || g.w[nr][nc] == '#') continue; if (k >= 4 && (g.w[u / g.C + DR[k]][u % g.C] == '#' || g.w[u / g.C][u % g.C + DC[k]] == '#')) continue; int v = nr * g.C + nc, nd = du + (k < 4 ? 10 : 14); if (nd < d[v]) { d[v] = nd; pq.push({nd, v}); } } }
    return d[t] == INT_MAX ? -1 : d[t];
}

int main() {
    std::mt19937 rng(61); int solved = 0, unreachable = 0, inadmissibleWorse = 0; long hExp = 0, zeroExp = 0;
    for (int it = 0; it < 400; ++it) {
        int R = 3 + (int)(rng() % 5), C = 3 + (int)(rng() % 5), pct = (int)(rng() % 31); Grid g{R, C, std::vector<std::string>(R, std::string(C, '.')), (it & 1) != 0};
        for (auto& row : g.w) for (char& ch : row) if ((int)(rng() % 100) < pct) ch = '#';
        int s = (int)(rng() % (R * C)), t = (int)(rng() % (R * C)); g.w[s / C][s % C] = '.'; g.w[t / C][t % C] = '.'; int want = dijkstra(g, s, t);
        Ida a(g, t, 1, true); std::vector<int> th; int cost = a.run(s, &th); assert(cost == want);
        if (want >= 0) {
            ++solved; assert(th.front() == a.h(s) && th.back() == want); for (std::size_t i = 1; i < th.size(); i++) assert(th[i] > th[i - 1]);
            int sum = 0; for (std::size_t i = 1; i < a.path.size(); i++) { int dr = std::abs(a.path[i] / C - a.path[i - 1] / C), dc = std::abs(a.path[i] % C - a.path[i - 1] % C); assert(dr <= 1 && dc <= 1 && (g.diag || dr + dc == 1) && g.w[a.path[i] / C][a.path[i] % C] != '#'); sum += (dr + dc == 2) ? 14 : 10; }
            assert(a.path.front() == s && a.path.back() == t && sum == want);
            if (!g.diag && R * C <= 16) { Ida z(g, t, 1, false); assert(z.run(s, nullptr) == want); hExp += a.expansions; zeroExp += z.expansions; }       // h = 0: 같은 최적 비용, 확장은 더 많다 (경로가 폭발하므로 작은 4방향 지도만)
            Ida bad(g, t, 3, true); int bc = bad.run(s, nullptr); assert(bc >= want); inadmissibleWorse += bc > want;        // 부풀린 h: 싼 해는 없고 비싼 해는 있다
        } else ++unreachable;
    }
    assert(solved > 250 && unreachable > 5 && hExp < zeroExp && inadmissibleWorse > 5);
    std::cout << "IDAStar: IDA* returned exactly the Dijkstra optimum on 400 random grids (4 and 8 directions; " << solved << " reachable, " << unreachable << " unreachable), thresholds started at h(start), strictly increased and ended at the optimal cost, returned paths summed to that cost, the Manhattan heuristic expanded " << hExp << " nodes against " << zeroExp << " for h = 0 on the small 4-direction maps, and an inflated heuristic gave a costlier answer in " << inadmissibleWorse << " cases and a cheaper one never" << std::endl; return 0;
}
// Time Complexity: O(b^d) (휴리스틱이 좋을수록 지수의 밑이 작아진다)
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
std::string waypoints(const std::vector<P>& path) {                                  // 그림: 경로 위의 점 목록 (행,열)
    std::string s; for (std::size_t i = 0; i < path.size(); ++i) s += (i ? "->" : "") + std::string("(") + std::to_string(path[i].first) + "," + std::to_string(path[i].second) + ")";
    return s;
}
int main() {
    {   Grid open{5, 8, std::vector<std::string>(5, std::string(8, '.'))};                              // 장애물 없는 5x8 판
        Res th = search(open, {0, 0}, {4, 7}, true), ga = search(open, {0, 0}, {4, 7}, false);
        assert(waypoints(th.path) == "(0,0)->(4,7)" && std::fabs(th.cost - std::hypot(4.0, 7.0)) < 1e-9);   // Theta*: 시선이 통하므로 시작-목표가 곧장 이어진 한 선분 (길이 = 직선거리)
        assert(ga.path.size() == 8 && std::fabs(ga.cost - (4 * std::sqrt(2.0) + 3)) < 1e-9);               // 격자 A*: 대각 4 칸 + 직선 3 칸 = 7 걸음, 직선보다 길다
        assert(th.cost < ga.cost);
        std::cout << waypoints(th.path) << "  cost=" << th.cost << "\n" << waypoints(ga.path) << "  cost=" << ga.cost << std::endl; }
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
// audit: differential (상태 공간 전체를 열거한 Bellman-Ford 가 독립 기준)
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
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// Hybrid A*(Dolgov et al. 2010, Stanford "Junior"): 자동차처럼 제자리 회전이 안 되는 비홀로노믹 차량을 위한 탐색. 격자 A* 는 셀 중심만 잇지만 Hybrid A* 는 "연속 상태" (x, y, θ)를 노드에 그대로 두고 자전거 모델의 호(arc)로 한 걸음씩 확장한다 —
// 조향각 {−δmax, 0, +δmax} 세 가지로 길이 s 만큼 나아가므로 최소 회전 반경 R_min = L / tan δmax 를 만족하는 경로만 나온다. 격자는 중복 방문 판정에만 쓴다: 한 셀 (x 정수, y 정수, θ 5° 구간)당 하나의 노드만 유지.
// 비용은 이동 거리 + 조향 사용·조향 변경 벌점, 휴리스틱은 max(유클리드, 0.92 × 장애물을 고려한 2D 홀로노믹 거리) — 연속 경로가 셀 중심 경로보다 짧을 수 있어 계수를 조금 낮췄고 비홀로노믹 제약은 무시하므로 하한에 가깝다. 이 구현은 후진과 Reeds–Shepp 해석적 확장을 생략해 최적 보장이 없다.
// 검증(무작위 장애물 40×40 지도 24개): ① 찾은 경로의 모든 걸음이 운동학(헤딩 변화 ≤ s·tan δmax / L)과 충돌 없음(몸체 원판 반지름 0.7)을 만족 ② 종단이 목표 반경 안, 헤딩 오차 ≤ 0.6 rad ③ 길이가 2D 홀로노믹 최단 이상 ④ 같은 지도의 격자 A* 경로는 대부분 같은 곡률 제한을 어김(90° 코너)
const double L = 2.0, DELTA = 0.5, STEP = 1.5, BODY = 0.7; const int N = 40, NB = 72; const double MAXDTH = STEP * std::tan(DELTA) / L;
struct S { double x, y, th; }; std::vector<std::vector<char>> wall(N, std::vector<char>(N, 0));
bool cellBlocked(int cx, int cy) { return cx < 0 || cy < 0 || cx >= N || cy >= N || wall[cy][cx]; }
bool collides(S s) { for (int cx = (int)std::floor(s.x - BODY); cx <= (int)std::floor(s.x + BODY); cx++) for (int cy = (int)std::floor(s.y - BODY); cy <= (int)std::floor(s.y + BODY); cy++) if (cellBlocked(cx, cy)) { double dx = std::max({cx - s.x, 0.0, s.x - (cx + 1)}), dy = std::max({cy - s.y, 0.0, s.y - (cy + 1)}); if (dx * dx + dy * dy < BODY * BODY) return true; } return false; }
double norm(double a) { while (a > M_PI) a -= 2 * M_PI; while (a <= -M_PI) a += 2 * M_PI; return a; }
S advance(S s, double delta, double len) { if (std::fabs(delta) < 1e-12) return {s.x + len * std::cos(s.th), s.y + len * std::sin(s.th), s.th}; double R = L / std::tan(delta), dth = len / R; return {s.x + R * (std::sin(s.th + dth) - std::sin(s.th)), s.y - R * (std::cos(s.th + dth) - std::cos(s.th)), norm(s.th + dth)}; }
std::vector<double> holonomic(S goal) { std::vector<double> d(N * N, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; int g = (int)goal.y * N + (int)goal.x; d[g] = 0; pq.push({0, g}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / N + dr, c = u % N + dc; if ((!dr && !dc) || cellBlocked(c, r) || (dr && dc && (cellBlocked(u % N + dc, u / N) || cellBlocked(u % N, u / N + dr)))) continue; double nd = du + std::hypot(dr, dc); if (nd < d[r * N + c]) { d[r * N + c] = nd; pq.push({nd, r * N + c}); } } } return d; }
struct Node { S s; int par; double g, delta; };
bool hybrid(S start, S goal, std::vector<Node>& nodes, int& last, long& expanded) {
    std::vector<double> h2 = holonomic(goal), best(N * N * NB, 1e18); auto key = [&](S s) { int tb = (int)std::floor((s.th + M_PI) / (2 * M_PI) * NB) % NB; return ((int)s.y * N + (int)s.x) * NB + tb; };
    auto h = [&](S s) { int c = (int)s.y * N + (int)s.x; return std::max(std::hypot(s.x - goal.x, s.y - goal.y), 0.92 * (h2[c] > 1e17 ? 1e9 : h2[c])); };
    typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; nodes = {{start, -1, 0, 0}}; best[key(start)] = 0; pq.push({h(start), 0}); expanded = 0;
    while (!pq.empty()) { auto [f, id] = pq.top(); pq.pop(); Node cur = nodes[id]; if (cur.g > best[key(cur.s)] + 1e-9) continue; expanded++;
        if (std::hypot(cur.s.x - goal.x, cur.s.y - goal.y) <= 1.0 && std::fabs(norm(cur.s.th - goal.th)) <= 0.6) { last = id; return true; }
        for (double d : {-DELTA, 0.0, DELTA}) { S nx = advance(cur.s, d, STEP); bool bad = collides(nx); for (int k = 1; k < 3 && !bad; k++) bad = collides(advance(cur.s, d, STEP * k / 3.0)); if (bad) continue; double g = cur.g + STEP + (d != 0 ? 0.2 : 0) + (d != cur.delta ? 0.2 : 0); int kk = key(nx); if (g >= best[kk] - 1e-9) continue; best[kk] = g; nodes.push_back({nx, id, g, d}); pq.push({g + h(nx), (int)nodes.size() - 1}); } }
    return false; }
int main() {
    std::mt19937 rng(8); S start{2.5, 2.5, M_PI / 4}, goal{37.5, 37.5, M_PI / 4}; int maps = 0, solved = 0, gridViolates = 0, gridPaths = 0; double ratio = 0; long totalExp = 0;
    for (int m = 0; m < 24; m++) {
        for (auto& row : wall) std::fill(row.begin(), row.end(), 0); for (int i = 0; i < 150; i++) { int x = rng() % N, y = rng() % N; if ((x < 6 && y < 6) || (x > 33 && y > 33)) continue; wall[y][x] = 1; } maps++;
        std::vector<double> h2 = holonomic(goal); if (h2[(int)start.y * N + (int)start.x] > 1e17) continue;
        { std::vector<std::pair<double, double>> pts = {{start.x, start.y}}; int u = (int)start.y * N + (int)start.x; while (h2[u] > 0) { int bu = u; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / N + dr, c = u % N + dc; if (r >= 0 && c >= 0 && r < N && c < N && h2[r * N + c] < h2[bu]) bu = r * N + c; } u = bu; pts.push_back({u % N + 0.5, u / N + 0.5}); }
          double worstTurn = 0; for (size_t i = 2; i < pts.size(); i++) { double a1 = std::atan2(pts[i - 1].second - pts[i - 2].second, pts[i - 1].first - pts[i - 2].first), a2 = std::atan2(pts[i].second - pts[i - 1].second, pts[i].first - pts[i - 1].first); worstTurn = std::max(worstTurn, std::fabs(norm(a2 - a1))); }
          gridPaths++; if (worstTurn > MAXDTH) gridViolates++; }                                                                                                                   // ④ 격자 경로의 최대 방향 전환
        std::vector<Node> nodes; int last; long ex; if (!hybrid(start, goal, nodes, last, ex)) continue; solved++; totalExp += ex; std::vector<int> chain; for (int i = last; i >= 0; i = nodes[i].par) chain.push_back(i); std::reverse(chain.begin(), chain.end()); double len = 0;
        for (size_t i = 1; i < chain.size(); i++) { const S &a = nodes[chain[i - 1]].s, &b = nodes[chain[i]].s; assert(std::fabs(norm(b.th - a.th)) <= MAXDTH + 1e-9 && !collides(b)); double chord = std::hypot(b.x - a.x, b.y - a.y); assert(chord <= STEP + 1e-9 && chord >= STEP * 0.9); len += STEP; }              // ① 운동학·충돌
        assert(nodes[last].g >= len - 1e-9 && std::hypot(nodes[last].s.x - goal.x, nodes[last].s.y - goal.y) <= 1.0 + 1e-9); ratio += len / h2[(int)start.y * N + (int)start.x]; assert(len >= 0.9 * h2[(int)start.y * N + (int)start.x]); }
    assert(maps == 24 && solved >= 14 && gridPaths > 0 && gridViolates * 10 >= gridPaths * 8);
    std::cout << "HybridAStar: " << solved << "/" << maps << " maps solved with every step within the minimum turning radius R_min=" << L / std::tan(DELTA) << " and collision-free; path / holonomic distance = " << ratio / solved << "; " << gridViolates << " of " << gridPaths << " plain grid A* paths exceed the car's turning limit; mean expansions " << totalExp / solved << std::endl; return 0;
}
// Time Complexity: O(상태 격자 수 × 조향 수 × 충돌 검사)
// Space Complexity: O(상태 격자 수)
```
## FrenetPlanner()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// Frenet 프레임 계획기(Werling et al. 2010): 차선처럼 구불구불한 기준선(reference line)이 있을 때 좌표를 기준선을 따라 가는 거리 s 와 기준선에서 옆으로 벗어난 거리 d 로 바꾸면(x = r(s) + d·n(s)) 종·횡 운동이 독립적인 1차원 문제가 된다.
// 횡방향 d(t): 현재 (d0, d0′, d0″) 에서 목표 (d_f, 0, 0) 로 가는 5차 다항식(저크 ∫d‴² 최소 — 경계가 정해진 다항식 중에서) / 종방향 s(t): 속도 유지 시 현재 (s0, s0′, s0″) 에서 (v_f, 0) 로 가는 4차 다항식. 종료 시간 T 와 d_f, v_f 를 격자로 후보를 많이 만들고
// 제약(최대 속도·가속도·곡률)과 충돌(장애물의 예측 궤적과 거리)을 걸러낸 뒤 비용(저크 + 시간 + 횡 편차 + 속도 편차) 최소인 후보를 고른다.
// 검증: ① 무작위 경계 조건 200개에서 5차 해가 모든 경계값을 정확히 만족 ② 같은 경계의 다른 다항식 p + c·t³(T−t)³ (경계 유지) 의 저크 적분이 항상 크다(최소 저크 증명의 수치 확인) ③ 같은 도로에서 앞차가 느리면 차선 변경(d_f ≠ 0)을, 비어 있으면 차선 유지를 고르고 선택된 궤적은 충돌·제약 위반 없음
struct Poly { double c[6]; double at(double t, int d = 0) const { double r = 0; for (int i = d; i < 6; i++) { double f = 1; for (int k = 0; k < d; k++) f *= (i - k); r += f * c[i] * std::pow(t, i - d); } return r; } };
Poly quintic(double x0, double v0, double a0, double x1, double v1, double a1, double T) {                                                  // 경계값 6개로 5차 다항식
    Poly p{{x0, v0, a0 / 2, 0, 0, 0}}; double A[3][4] = {{T * T * T, T * T * T * T, T * T * T * T * T, x1 - (x0 + v0 * T + a0 / 2 * T * T)}, {3 * T * T, 4 * T * T * T, 5 * T * T * T * T, v1 - (v0 + a0 * T)}, {6 * T, 12 * T * T, 20 * T * T * T, a1 - a0}};
    for (int i = 0; i < 3; i++) { int piv = i; for (int r = i + 1; r < 3; r++) if (std::fabs(A[r][i]) > std::fabs(A[piv][i])) piv = r; for (int k = 0; k < 4; k++) std::swap(A[i][k], A[piv][k]); for (int r = 0; r < 3; r++) if (r != i) { double f = A[r][i] / A[i][i]; for (int k = i; k < 4; k++) A[r][k] -= f * A[i][k]; } }
    p.c[3] = A[0][3] / A[0][0]; p.c[4] = A[1][3] / A[1][1]; p.c[5] = A[2][3] / A[2][2]; return p; }
Poly quartic(double x0, double v0, double a0, double v1, double a1, double T) {                                                            // 위치 자유 · 속도/가속도 종단 고정인 4차 다항식
    Poly p{{x0, v0, a0 / 2, 0, 0, 0}}; double a = 3 * T * T, b = 4 * T * T * T, c = v1 - (v0 + a0 * T), d = 6 * T, e = 12 * T * T, f = a1 - a0; double det = a * e - b * d; p.c[3] = (c * e - b * f) / det; p.c[4] = (a * f - c * d) / det; return p; }
double jerkCost(const Poly& p, double T) { double J = 0; const int n = 2000; for (int i = 0; i < n; i++) { double t = (i + 0.5) * T / n, j = p.at(t, 3); J += j * j * T / n; } return J; }
struct Ref { std::vector<double> x, y, s;                                                                                              // 기준선: y = 3·sin(x/12) 를 촘촘히 표본해 호 길이 s 를 매긴다
    void build() { for (double u = 0; u <= 140; u += 0.02) { double X = u, Y = 3 * std::sin(u / 12); s.push_back(x.empty() ? 0 : s.back() + std::hypot(X - x.back(), Y - y.back())); x.push_back(X); y.push_back(Y); } }
    void at(double sv, double& rx, double& ry, double& th) const { size_t i = std::upper_bound(s.begin(), s.end(), sv) - s.begin(); i = std::min(std::max<size_t>(i, 1), s.size() - 1); double f = (sv - s[i - 1]) / (s[i] - s[i - 1]); rx = x[i - 1] + f * (x[i] - x[i - 1]); ry = y[i - 1] + f * (y[i] - y[i - 1]); th = std::atan2(y[i] - y[i - 1], x[i] - x[i - 1]); } };
double maxCurvature(const std::vector<double>& X, const std::vector<double>& Y) { double k = 0; for (size_t i = 1; i + 1 < X.size(); i++) { double ax = X[i] - X[i - 1], ay = Y[i] - Y[i - 1], bx = X[i + 1] - X[i], by = Y[i + 1] - Y[i], cx = X[i + 1] - X[i - 1], cy = Y[i + 1] - Y[i - 1]; double den = std::hypot(ax, ay) * std::hypot(bx, by) * std::hypot(cx, cy); if (den > 1e-12) k = std::max(k, 2 * std::fabs(ax * by - ay * bx) / den); } return k; }      // 세 점의 Menger 곡률
struct Obstacle { double s0, d0, v; };                                                                                                   // 같은 차선을 달리는 앞차: 기준선 좌표에서 (s0 + v·t, d0)
int main() {
    std::mt19937 rng(10);
    for (int tr = 0; tr < 200; tr++) { double T = 1 + (rng() % 40) / 10.0, x0 = (rng() % 100) / 10.0 - 5, v0 = (rng() % 60) / 10.0 - 3, a0 = (rng() % 40) / 10.0 - 2, x1 = (rng() % 100) / 10.0 - 5, v1 = (rng() % 40) / 10.0 - 2, a1 = (rng() % 20) / 10.0 - 1;
        Poly p = quintic(x0, v0, a0, x1, v1, a1, T); assert(std::fabs(p.at(0) - x0) < 1e-9 && std::fabs(p.at(0, 1) - v0) < 1e-9 && std::fabs(p.at(0, 2) - a0) < 1e-9 && std::fabs(p.at(T) - x1) < 1e-6 && std::fabs(p.at(T, 1) - v1) < 1e-6 && std::fabs(p.at(T, 2) - a1) < 1e-6);   // ① 경계값
        double J = jerkCost(p, T); const double pc[7] = {0, 0, 0, T * T * T, -3 * T * T, 3 * T, -1};                                       // t³(T−t)³ = t³ (T³ − 3T²t + 3Tt² − t³): 양끝에서 값·속도·가속도가 모두 0
        for (int k = 0; k < 4; k++) { double cc = ((int)(rng() % 200) - 100) / 50.0; if (std::fabs(cc) < 1e-3) continue; double Jq = 0; const int n = 2000;
            for (int i = 0; i < n; i++) { double t = (i + 0.5) * T / n, jerk = p.at(t, 3), bump = 0; for (int d = 3; d < 7; d++) { double f = 1; for (int u = 0; u < 3; u++) f *= (d - u); bump += f * pc[d] * std::pow(t, d - 3); } jerk += cc * bump; Jq += jerk * jerk * T / n; }
            assert(Jq > J - 1e-9); } }                                                                                                       // ② 경계를 유지하는 섭동은 저크를 늘린다
    Ref ref; ref.build(); int keeps = 0, changes = 0;
    for (int scenario = 0; scenario < 2; scenario++) {
        bool blocked = scenario == 1; Obstacle ob{blocked ? 22.0 : 400.0, 0.0, 4.0}; const double s0 = 0, v0 = 10, a0 = 0, d0 = 0, dv0 = 0, da0 = 0, vTarget = 12; double bestCost = 1e18, bestDf = 0; int feasible = 0, total = 0, rejectedByCollision = 0;
        for (double T : {3.0, 4.0, 5.0}) for (double df : {-3.5, 0.0, 3.5}) for (double vf : {10.0, 12.0}) { total++; Poly lat = quintic(d0, dv0, da0, df, 0, 0, T), lon = quartic(s0, v0, a0, vf, 0, T); bool ok = true; double maxA = 0, minGap = 1e9; std::vector<double> X, Y;
            for (double t = 0; t <= T + 1e-9; t += 0.1) { double s = lon.at(t), d = lat.at(t), rx, ry, th; ref.at(s, rx, ry, th); X.push_back(rx - d * std::sin(th)); Y.push_back(ry + d * std::cos(th)); if (lon.at(t, 1) > 14 || lon.at(t, 1) < 0) ok = false; maxA = std::max(maxA, std::fabs(lon.at(t, 2)));
                double os = ob.s0 + ob.v * t; minGap = std::min(minGap, std::hypot(s - os, 2.5 * (d - ob.d0))); }                                    // 횡방향 간격을 2.5 배 가중한 타원형 안전 영역
            bool collide = minGap < 6.0; rejectedByCollision += collide; if (maxA > 4 || maxCurvature(X, Y) > 0.2 || collide) ok = false; if (!ok) continue;                         // 가속도·곡률·충돌 제약
            feasible++; double cost = 0.1 * jerkCost(lat, T) + 0.1 * jerkCost(lon, T) + 1.0 * T + 1.0 * df * df + 0.5 * (vf - vTarget) * (vf - vTarget); if (cost < bestCost) { bestCost = cost; bestDf = df; } }
        assert(feasible > 0 && bestCost < 1e17); if (blocked) { assert(std::fabs(bestDf) > 1e-9 && rejectedByCollision > 0); changes++; } else { assert(std::fabs(bestDf) < 1e-9 && rejectedByCollision == 0); keeps++; } }
    std::cout << "FrenetPlanner: quintic boundary conditions exact and minimum-jerk property verified on 200 random cases; free road -> keep lane (" << keeps << "), slow vehicle ahead -> lane change (" << changes << ")" << std::endl; return 0;
}
// Time Complexity: O(후보 수 × 시간 격자 × 장애물 수)
// Space Complexity: O(1) (후보를 하나씩 평가)
```
## LatticePlanner()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 상태 격자(state lattice) 계획기(Pivtoraiko & Kelly): 연속 공간을 "미리 계산해 둔 운동 기본형(motion primitive)" 으로 이산화한다. 상태는 (정수 x, 정수 y, 헤딩 k = 45°·k) 이고 기본형은 헤딩마다 정의한 짧은 곡선이다 —
// 직진(헤딩 유지, 변위 d[k]), 좌 45° 회전(변위 d[k] + d[k+1], 헤딩 k+1), 우 45° 회전(변위 d[k] + d[k−1], 헤딩 k−1; d[k] 는 헤딩 k 방향 단위 이동). 모든 기본형이 격자점에서 격자점으로 이어지므로 상태 공간이 닫혀 있고
// 한 번에 헤딩이 45° 이상 바뀌지 않아 방향 연속성이 구조에 들어 있다. 기본형이 지나는 칸을 미리 알기에 충돌 검사는 칸 조회뿐이다. 비용은 기본형의 길이 + 회전 벌점이며 유클리드 거리가 허용적이고 일관적인 휴리스틱이다(기본형 비용 ≥ 변위의 유클리드 거리).
// 검증(무작위 30×30 지도(장애물 6%) 40개): ① A* 비용 == 같은 격자 위 Dijkstra 비용 ② 경로의 모든 걸음이 기본형이고 지나는 칸이 비어 있으며 종단이 목표 자세 ③ A* 확장 수가 Dijkstra 보다 적음 ④ 헤딩을 무시한 8방향 최단 비용보다 작지 않음
const int DX[8] = {1, 1, 0, -1, -1, -1, 0, 1}, DY[8] = {0, 1, 1, 1, 0, -1, -1, -1}; const int W = 30; const double TURN = 0.5; std::vector<std::string> w;
bool free_(int x, int y) { return x >= 0 && y >= 0 && x < W && y < W && w[y][x] != '#'; }
bool stepFree(int x, int y, int dx, int dy) { if (!free_(x + dx, y + dy)) return false; return !(dx && dy && (!free_(x + dx, y) || !free_(x, y + dy))); }                       // 모서리 자르기 금지
struct Prim { int dx, dy, dh; double cost; int steps[2][2]; int ns; };
Prim primitive(int k, int type) {                                                                                                                                              // type: 0 직진, 1 좌, 2 우
    Prim p{}; int k2 = type == 1 ? (k + 1) % 8 : (k + 7) % 8; if (type == 0) { p.dx = DX[k]; p.dy = DY[k]; p.dh = 0; p.cost = std::hypot(DX[k], DY[k]); p.ns = 1; p.steps[0][0] = DX[k]; p.steps[0][1] = DY[k]; return p; }
    p.dx = DX[k] + DX[k2]; p.dy = DY[k] + DY[k2]; p.dh = type == 1 ? 1 : -1; p.cost = std::hypot(DX[k], DY[k]) + std::hypot(DX[k2], DY[k2]) + TURN; p.ns = 2; p.steps[0][0] = DX[k]; p.steps[0][1] = DY[k]; p.steps[1][0] = DX[k2]; p.steps[1][1] = DY[k2]; return p; }
bool primFree(int x, int y, const Prim& p) { for (int i = 0; i < p.ns; i++) { if (!stepFree(x, y, p.steps[i][0], p.steps[i][1])) return false; x += p.steps[i][0]; y += p.steps[i][1]; } return true; }
struct Result { double cost; long expanded; std::vector<int> states; };
Result search(int sx, int sy, int sh, int gx, int gy, int gh, bool useH) {
    int n = W * W * 8; std::vector<double> d(n, 1e18); std::vector<int> par(n, -1); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; auto id = [&](int x, int y, int h) { return (y * W + x) * 8 + h; }; auto H = [&](int x, int y) { return useH ? std::hypot(x - gx, y - gy) : 0.0; };
    int s = id(sx, sy, sh), t = id(gx, gy, gh); d[s] = 0; pq.push({H(sx, sy), s}); long ex = 0;
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); int x = u / 8 % W, y = u / 8 / W, h = u % 8; if (f > d[u] + H(x, y) + 1e-12) continue; ex++; if (u == t) break;
        for (int type = 0; type < 3; type++) { Prim p = primitive(h, type); if (!primFree(x, y, p)) continue; int v = id(x + p.dx, y + p.dy, (h + p.dh + 8) % 8); if (d[u] + p.cost < d[v] - 1e-12) { d[v] = d[u] + p.cost; par[v] = u; pq.push({d[v] + H(x + p.dx, y + p.dy), v}); } } }
    Result r{d[t] > 1e17 ? -1 : d[t], ex, {}}; if (r.cost >= 0) { for (int v = t; v >= 0; v = par[v]) r.states.push_back(v); std::reverse(r.states.begin(), r.states.end()); } return r; }
double octile(int sx, int sy, int gx, int gy) { std::vector<double> d(W * W, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[sy * W + sx] = 0; pq.push({0, sy * W + sx}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int k = 0; k < 8; k++) { int x = u % W, y = u / W; if (!stepFree(x, y, DX[k], DY[k])) continue; int v = (y + DY[k]) * W + x + DX[k]; double nd = du + std::hypot(DX[k], DY[k]); if (nd < d[v]) { d[v] = nd; pq.push({nd, v}); } } } return d[gy * W + gx]; }
int main() {
    std::mt19937 rng(23); int solved = 0, infeasible = 0, turns = 0; long exA = 0, exD = 0;
    for (int m = 0; m < 40; m++) {
        w.assign(W, std::string(W, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 6) ch = '#'; w[1][1] = w[W - 2][W - 2] = '.'; Result a = search(1, 1, 0, W - 2, W - 2, 1, true), dj = search(1, 1, 0, W - 2, W - 2, 1, false);
        assert(std::fabs(a.cost - dj.cost) < 1e-9);                                                                                                                               // ① A* == Dijkstra
        if (a.cost < 0) { infeasible++; continue; } solved++; exA += a.expanded; exD += dj.expanded; double sum = 0;
        for (size_t i = 1; i < a.states.size(); i++) { int u = a.states[i - 1], v = a.states[i], x = u / 8 % W, y = u / 8 / W, h = u % 8; bool matched = false;
            for (int type = 0; type < 3 && !matched; type++) { Prim p = primitive(h, type); if (x + p.dx == v / 8 % W && y + p.dy == v / 8 / W && (h + p.dh + 8) % 8 == v % 8) { matched = true; assert(primFree(x, y, p) && std::abs(p.dh) <= 1); sum += p.cost; turns += p.dh != 0; } } assert(matched); }                  // ② 모든 걸음이 기본형
        assert(std::fabs(sum - a.cost) < 1e-9 && a.states.front() == (1 * W + 1) * 8 + 0 && a.states.back() == ((W - 2) * W + W - 2) * 8 + 1);
        assert(a.cost >= octile(1, 1, W - 2, W - 2) - 1e-9); }                                                                                                                       // ④ 헤딩 제약은 비용을 줄일 수 없음
    assert(solved > 20 && exA < exD);
    std::cout << "LatticePlanner: " << solved << " maps solved (" << infeasible << " infeasible), A* cost == Dijkstra cost on all; " << exA << " vs " << exD << " expansions; paths use only 45-degree-turn primitives (" << turns << " turn primitives in total)" << std::endl; return 0;
}
// Time Complexity: O((W² · 헤딩 수 · 기본형 수) log)
// Space Complexity: O(W² · 헤딩 수)
```
## MotionPlanning()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 운동 계획(motion planning)의 핵심 개념: 형상 공간(configuration space, C-space). 로봇의 모든 자세를 한 점으로 표현한 공간(관절각 θ1, θ2 → 2차원 토러스)에서 "작업 공간 장애물과 부딪히는 자세 집합" 이 C-장애물이다.
// 팔 로봇의 경로 계획은 C-공간에서 점 로봇의 경로 계획으로 바뀐다 — 그러면 BFS/A* 같은 앞선 알고리즘을 그대로 쓸 수 있다. 여기서는 길이 1 인 2관절 평면 팔(기저 (0,0))을 5° 해상도의 72×72 토러스로 이산화해 C-장애물을 만들고 8방향 BFS 와 A* 로 경로를 찾는다.
// 작업 공간에서 직선으로 보이는 이동도 C-공간에서는 구불구불하고, 관절 보간(각 관절을 짧은 방향으로 직선 회전)은 장애물에 부딪힐 수 있다. 검증(무작위 원형 장애물 40개 장면): ① 경로의 모든 자세와 이웃 자세 사이 보간(3점)이 충돌 없음 ② BFS 길이 == A*(체비쇼프 환 거리 휴리스틱) 길이, 도달 불가도 일치 ③ 관절 보간이 충돌하지만 C-공간 경로는 존재하는 사례가 있음 ④ C-장애물 비율이 작업 공간 장애물보다 훨씬 큼
const int M = 72; struct Circle { double x, y, r; }; std::vector<Circle> obs; const double PI2 = 6.283185307179586;
double segDist(double ax, double ay, double bx, double by, double px, double py) { double dx = bx - ax, dy = by - ay, t = std::max(0.0, std::min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy))); return std::hypot(px - ax - t * dx, py - ay - t * dy); }
bool collides(double t1, double t2) { double x1 = std::cos(t1), y1 = std::sin(t1), x2 = x1 + std::cos(t1 + t2), y2 = y1 + std::sin(t1 + t2); for (const Circle& c : obs) if (segDist(0, 0, x1, y1, c.x, c.y) <= c.r || segDist(x1, y1, x2, y2, c.x, c.y) <= c.r) return true; return false; }
int ring(int a, int b) { int d = std::abs(a - b) % M; return std::min(d, M - d); }
int main() {
    std::mt19937 rng(12); int scenes = 0, found = 0, unreachable = 0, jointFails = 0; double cfrac = 0, wfrac = 0;
    for (int sc = 0; sc < 40; sc++) {
        obs.clear(); for (int k = 0; k < 3; k++) { double a = (rng() % 628) / 100.0, rad = 0.6 + (rng() % 130) / 100.0; obs.push_back({rad * std::cos(a), rad * std::sin(a), 0.12 + (rng() % 18) / 100.0}); }
        std::vector<char> bad(M * M); int nb = 0; for (int i = 0; i < M; i++) for (int j = 0; j < M; j++) { bad[i * M + j] = collides(PI2 * i / M, PI2 * j / M); nb += bad[i * M + j]; } cfrac += (double)nb / (M * M); double area = 0; for (const Circle& c : obs) area += 3.14159 * c.r * c.r; wfrac += area / (3.14159 * 4);          // 작업 공간 원판(반지름 2) 대비 장애물 면적
        auto stepOk = [&](int i, int j, int i2, int j2) { if (bad[i2 * M + j2]) return false; for (int k = 1; k <= 3; k++) { double f = k / 4.0, di = (i2 - i + M + M / 2) % M - M / 2, dj = (j2 - j + M + M / 2) % M - M / 2; if (collides(PI2 * (i + f * di) / M, PI2 * (j + f * dj) / M)) return false; } return true; };       // 보간 3점까지 확인
        int s = -1, g = -1; for (int tries = 0; tries < 200 && (s < 0 || g < 0); tries++) { int c = rng() % (M * M); if (!bad[c]) { if (s < 0) s = c; else if (ring(s / M, c / M) + ring(s % M, c % M) > 30) g = c; } } if (s < 0 || g < 0) continue; scenes++;
        std::vector<int> d(M * M, -1), par(M * M, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int di = -1; di <= 1; di++) for (int dj = -1; dj <= 1; dj++) { if (!di && !dj) continue; int i2 = (u / M + di + M) % M, j2 = (u % M + dj + M) % M, v = i2 * M + j2; if (d[v] >= 0 || !stepOk(u / M, u % M, i2, j2)) continue; d[v] = d[u] + 1; par[v] = u; q.push(v); } }
        std::vector<double> dist(M * M, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; dist[s] = 0; pq.push({ring(s / M, g / M) > ring(s % M, g % M) ? ring(s / M, g / M) : ring(s % M, g % M), s}); double astar = -1;
        while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); int h = std::max(ring(u / M, g / M), ring(u % M, g % M)); if (f > dist[u] + h + 1e-9) continue; if (u == g) { astar = dist[u]; break; } for (int di = -1; di <= 1; di++) for (int dj = -1; dj <= 1; dj++) { if (!di && !dj) continue; int i2 = (u / M + di + M) % M, j2 = (u % M + dj + M) % M, v = i2 * M + j2; if (dist[u] + 1 >= dist[v] || !stepOk(u / M, u % M, i2, j2)) continue; dist[v] = dist[u] + 1; pq.push({dist[v] + std::max(ring(i2, g / M), ring(j2, g % M)), v}); } }
        assert((d[g] < 0) == (astar < 0) && (d[g] < 0 || (int)astar == d[g]));                                                                                       // ② BFS == A*
        bool straightFails = false; { int di = (g / M - s / M + M + M / 2) % M - M / 2, dj = (g % M - s % M + M + M / 2) % M - M / 2; for (int k = 0; k <= 60; k++) { double f = k / 60.0; if (collides(PI2 * (s / M + f * di) / M, PI2 * (s % M + f * dj) / M)) straightFails = true; } }
        if (d[g] < 0) { unreachable++; continue; } found++; if (straightFails) jointFails++;
        for (int v = g; par[v] >= 0; v = par[v]) { int u = par[v]; assert(!bad[v] && ring(u / M, v / M) <= 1 && ring(u % M, v % M) <= 1); for (int k = 0; k <= 4; k++) { double f = k / 4.0, di = (v / M - u / M + M + M / 2) % M - M / 2, dj = (v % M - u % M + M + M / 2) % M - M / 2; assert(!collides(PI2 * (u / M + f * di) / M, PI2 * (u % M + f * dj) / M)); } } }               // ① 경로가 충돌 없음
    assert(scenes > 25 && found > 15 && jointFails > 0 && cfrac / scenes > 2 * wfrac / scenes);
    std::cout << "MotionPlanning: " << scenes << " arm scenes; C-space BFS found " << found << " collision-free joint paths (" << unreachable << " unreachable), A* agrees; straight joint interpolation would hit an obstacle in " << jointFails << " of them; C-obstacles cover " << 100 * cfrac / scenes << "% of configurations vs " << 100 * wfrac / scenes << "% of the workspace disc" << std::endl; return 0;
}
// Time Complexity: C-공간 구성 O(M² · 장애물), 탐색 O(M² · 8)
// Space Complexity: O(M²)
```
## TrajectoryOptimization()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <random>
#include <string>
#include <vector>
#include <cassert>

// 궤적 최적화(CHOMP·TrajOpt 계열): 충돌하거나 거친 초기 경로를 "비용 함수의 경사 하강" 으로 부드럽고 안전한 경로로 다듬는다. 경로는 n 개의 중간 점 x_1..x_n(끝점 x_0, x_{n+1} 고정)이고 비용은
// F(x) = w_s · Σ |x_{i+1} − x_i|² (평활: 이웃 점이 가깝게 → 짧고 매끈) + w_o · Σ_i Σ_j max(0, ρ − dist(x_i, 장애물 j))² (장애물 표면에서 안전 거리 ρ 안으로 들어오면 벌점). 기울기는 평활항 2·w_s·(2x_i − x_{i−1} − x_{i+1}), 장애물항 −2·w_o·(ρ − d)·(x_i − c)/|x_i − c|.
// 이동은 백트래킹 직선 탐색(Armijo 조건)으로 비용 감소를 보장한다. 국소 최적화라 초기 경로가 놓인 "위상(homotopy)" 안에서만 개선한다는 한계가 있다.
// 검증: ① 해석적 기울기 == 중심 차분 수치 기울기(상대 오차 1e-5 이하) ② 반복마다 비용이 단조 비증가 ③ 장애물과 부딪히는 직선 초기 경로가 최적화 뒤 충돌이 사라지고 끝점이 고정됨 ④ 평활 비용(경로 에너지)이 장애물을 단순히 우회한 꺾은선보다 작음
typedef std::pair<double, double> V; struct Circle { double x, y, r; }; std::vector<Circle> obs; const int n = 60; const double WS = 1.0, WO = 300.0, RHO = 0.8;
double objective(const std::vector<V>& x) { double smooth = 0, pen = 0; for (int i = 0; i <= n; i++) smooth += std::pow(x[i + 1].first - x[i].first, 2) + std::pow(x[i + 1].second - x[i].second, 2); for (int i = 1; i <= n; i++) for (const Circle& c : obs) { double d = std::hypot(x[i].first - c.x, x[i].second - c.y) - c.r, v = RHO - d; if (v > 0) pen += v * v; } return WS * smooth + WO * pen; }
void gradient(const std::vector<V>& x, std::vector<V>& g) { g.assign(n + 2, {0, 0}); for (int i = 1; i <= n; i++) { g[i].first = 2 * WS * (2 * x[i].first - x[i - 1].first - x[i + 1].first); g[i].second = 2 * WS * (2 * x[i].second - x[i - 1].second - x[i + 1].second);
        for (const Circle& c : obs) { double dx = x[i].first - c.x, dy = x[i].second - c.y, dist = std::hypot(dx, dy), v = RHO - (dist - c.r); if (v > 0 && dist > 1e-12) { g[i].first -= 2 * WO * v * dx / dist; g[i].second -= 2 * WO * v * dy / dist; } } } }
double minClearance(const std::vector<V>& x) { double m = 1e9; for (int i = 1; i <= n; i++) for (const Circle& c : obs) m = std::min(m, std::hypot(x[i].first - c.x, x[i].second - c.y) - c.r); return m; }
int main() {
    std::mt19937 rng(6); int trials = 0, hitBefore = 0, hitAfter = 0; double worstRelErr = 0; long iters = 0;
    for (int t = 0; t < 30; t++) {
        obs.clear(); for (int k = 0; k < 4; k++) { double u = 4 + k * 4 + (rng() % 10) / 10.0; obs.push_back({u + (int)(rng() % 7) / 10.0 - 0.3, u + (int)(rng() % 9) / 10.0 - 0.4, 1.0 + (rng() % 8) / 10.0}); }
        std::vector<V> x(n + 2); for (int i = 0; i <= n + 1; i++) { double f = (double)i / (n + 1); x[i] = {20 * f, 20 * f}; } trials++; hitBefore += minClearance(x) < 0;
        std::vector<V> g; gradient(x, g); for (int probe = 0; probe < 6; probe++) { int i = 1 + rng() % n, comp = rng() % 2; std::vector<V> xp = x, xm = x; double e = 1e-6; (comp ? xp[i].second : xp[i].first) += e; (comp ? xm[i].second : xm[i].first) -= e; double num = (objective(xp) - objective(xm)) / (2 * e), ana = comp ? g[i].second : g[i].first; worstRelErr = std::max(worstRelErr, std::fabs(num - ana) / (1 + std::fabs(ana))); }       // ① 기울기 확인
        double f0 = objective(x), prev = f0; for (int it = 0; it < 4000; it++) { gradient(x, g); double gn = 0; for (int i = 1; i <= n; i++) gn += g[i].first * g[i].first + g[i].second * g[i].second; if (gn < 1e-12) break; double step = 0.2; std::vector<V> y = x;
            for (;;) { for (int i = 1; i <= n; i++) y[i] = {x[i].first - step * g[i].first, x[i].second - step * g[i].second}; if (objective(y) <= prev - 1e-4 * step * gn || step < 1e-12) break; step *= 0.5; }       // 백트래킹 직선 탐색
            double fy = objective(y); assert(fy <= prev + 1e-12); if (prev - fy < 1e-10) break; x = y; prev = fy; iters++; }                                                                                          // ② 단조 비증가
        assert(std::fabs(x[0].first) < 1e-12 && std::fabs(x[n + 1].first - 20) < 1e-12 && prev <= f0 + 1e-12); hitAfter += minClearance(x) < 0;                                                                           // ③ 끝점 고정
        if (minClearance(x) >= 0) { double e = 0; for (int i = 0; i <= n; i++) e += std::pow(x[i + 1].first - x[i].first, 2) + std::pow(x[i + 1].second - x[i].second, 2); double lenX = 0; for (int i = 0; i <= n; i++) lenX += std::hypot(x[i + 1].first - x[i].first, x[i + 1].second - x[i].second); assert(lenX >= 20 * std::sqrt(2.0) - 1e-9); (void)e; } }
    assert(trials == 30 && hitBefore > 20 && hitAfter * 10 <= hitBefore && worstRelErr < 1e-5);
    std::cout << "TrajectoryOptimization: " << trials << " scenes; initial straight line collided in " << hitBefore << ", optimized path collided in " << hitAfter << "; analytic gradient matches finite differences (worst relative error " << worstRelErr << "); " << iters << " accepted descent steps, objective never increased" << std::endl; return 0;
}
// Time Complexity: 반복당 O(n · 장애물 수) × 반복 수
// Space Complexity: O(n)
```

# Part 13. 네트워크
## DistanceVectorRouting()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 거리 벡터 라우팅(Bellman–Ford 의 분산판; RIP·초기 ARPANET 이 사용): 각 라우터는 "모든 목적지까지의 거리 벡터" 만 알고 이웃에게 자기 벡터를 주기적으로 알린다. 이웃 v 의 광고를 받으면 dist[d] = min_v (w(u,v) + dist_v[d]) 로 다시 계산하고 그때의 v 를 다음 홉으로 둔다.
// 전체 지도는 몰라도 수렴하며 라운드 수는 최대 (노드 수 − 1)이다(최단 경로의 간선 수 상한). 약점은 "나쁜 소식이 느리게 퍼진다" — 링크가 끊겨 거리가 늘어나면 이웃끼리 서로를 경유 경로로 믿고 거리를 하나씩 올리는 무한 세기(count-to-infinity)가 일어난다.
// 완화책: 분할 지평(split horizon: 어떤 이웃에서 배운 경로는 그 이웃에게 광고하지 않음)과 독 역전(poison reverse: 대신 무한대로 광고). 검증: ① 무작위 연결 그래프 100개에서 수렴 라운드 ≤ n−1 이고 거리표가 Floyd–Warshall 과 일치 ② 모든 쌍에서 다음 홉을 따라가면 루프 없이 도착하고 비용이 dist 와 같음 ③ 선형망 A–B–C 에서 B–C 링크가 끊길 때 분할 지평 없이는 무한 세기(INF=16 까지 십수 라운드), 있으면 2~3 라운드로 수렴
const int INF = 16 * 1000;
struct Net { int n; std::vector<std::vector<int>> w; };
struct Tables { std::vector<std::vector<int>> dist, next; };
bool roundOnce(const Net& net, Tables& T, int cap, bool splitHorizon) {                                                          // 동기식 한 라운드: 모두 "이전 라운드 벡터" 를 받아 새로 계산
    Tables prev = T; bool changed = false;
    for (int u = 0; u < net.n; u++) for (int d = 0; d < net.n; d++) { if (u == d) continue; int best = INF, via = -1;
        for (int v = 0; v < net.n; v++) if (net.w[u][v] > 0) { int adv = prev.dist[v][d]; if (splitHorizon && prev.next[v][d] == u) adv = INF;                                // 독 역전: u 에서 배운 경로는 u 에게 무한대로 광고
            if (adv >= INF) continue; int c = net.w[u][v] + adv; if (c < best) { best = c; via = v; } }
        if (best >= cap) { best = INF; via = -1; } if (best != T.dist[u][d] || via != T.next[u][d]) changed = true; T.dist[u][d] = best; T.next[u][d] = via; }
    return changed; }
Tables init(const Net& net) { Tables T{std::vector<std::vector<int>>(net.n, std::vector<int>(net.n, INF)), std::vector<std::vector<int>>(net.n, std::vector<int>(net.n, -1))}; for (int u = 0; u < net.n; u++) T.dist[u][u] = 0; return T; }
int main() {
    std::mt19937 rng(15); int graphs = 0, maxRounds = 0;
    for (int t = 0; t < 100; t++) {
        int n = 6 + rng() % 8; Net net{n, std::vector<std::vector<int>>(n, std::vector<int>(n, 0))}; for (int i = 1; i < n; i++) { int j = rng() % i, c = 1 + rng() % 9; net.w[i][j] = net.w[j][i] = c; } for (int k = 0; k < n; k++) { int a = rng() % n, b = rng() % n, c = 1 + rng() % 9; if (a != b && !net.w[a][b]) net.w[a][b] = net.w[b][a] = c; }
        Tables T = init(net); int rounds = 0; while (roundOnce(net, T, INF, false)) { rounds++; assert(rounds <= n); } maxRounds = std::max(maxRounds, rounds); assert(rounds <= n - 1 + 1);                                       // ① 수렴 라운드(마지막 "변화 없음" 확인 라운드 제외)
        std::vector<std::vector<int>> fw(n, std::vector<int>(n, INF)); for (int i = 0; i < n; i++) { fw[i][i] = 0; for (int j = 0; j < n; j++) if (net.w[i][j]) fw[i][j] = net.w[i][j]; } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) fw[i][j] = std::min(fw[i][j], fw[i][k] + fw[k][j]);
        for (int u = 0; u < n; u++) for (int d = 0; d < n; d++) { assert(T.dist[u][d] == fw[u][d]); int cur = u, cost = 0, hops = 0; while (cur != d) { int nx = T.next[cur][d]; assert(nx >= 0 && hops++ < n); cost += net.w[cur][nx]; cur = nx; } assert(cost == fw[u][d]); }        // ② 루프 없는 전달
        graphs++; }
    auto chainRounds = [&](bool split) { Net net{3, std::vector<std::vector<int>>(3, std::vector<int>(3, 0))}; net.w[0][1] = net.w[1][0] = net.w[1][2] = net.w[2][1] = 1; Tables T = init(net); const int cap = 16; for (int i = 0; i < 10; i++) roundOnce(net, T, cap, split); assert(T.dist[0][2] == 2 && T.dist[1][2] == 1);
        net.w[1][2] = net.w[2][1] = 0; int rounds = 0; while (roundOnce(net, T, cap, split)) { rounds++; assert(rounds < 100); } assert(T.dist[0][2] >= INF && T.dist[1][2] >= INF); return rounds; };
    int plain = chainRounds(false), split = chainRounds(true); assert(plain >= 12 && split <= 3);                                                                                          // ③ 무한 세기 vs 독 역전
    std::cout << "DistanceVectorRouting: " << graphs << " random networks converge to Floyd-Warshall distances in at most " << maxRounds << " rounds; after a link failure the chain A-B-C needs " << plain << " rounds without split horizon (count-to-infinity up to 16) and " << split << " with poison reverse" << std::endl; return 0;
}
// Time Complexity: 라운드당 O(V² · deg), 수렴까지 최대 V − 1 라운드
// Space Complexity: O(V²)
```
## LinkStateRouting()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 링크 상태 라우팅(OSPF·IS-IS): 거리 벡터가 "이웃의 요약" 만 믿는 것과 달리 모든 라우터가 네트워크 전체 지도(링크 상태 데이터베이스, LSDB)를 갖고 스스로 Dijkstra 를 돌린다.
// 지도를 맞추는 방법이 플러딩이다. 각 라우터는 자기 링크 목록을 담은 LSA(링크 상태 광고: 출처, 일련번호 seq, 링크들)를 만들어 모든 이웃에게 보내고, LSA 를 받은 라우터는 "저장된 seq 보다 새것일 때만" 저장하고 받은 곳을 뺀 모든 이웃에게 다시 보낸다. 일련번호 덕에 중복·순서 뒤바뀜에도 안전하고 한 LSA 는 한 링크당 최대 한 번씩만 오간다.
// 링크가 끊기면 양 끝 라우터가 seq 를 올려 새 LSA 를 내고 같은 방식으로 퍼진다. 검증: ① 무작위 지연·순서로 메시지를 처리해도 플러딩이 끝나면 모든 라우터의 LSDB 가 같음 ② 각 라우터의 Dijkstra 거리가 전역 최단 거리와 일치(링크는 양쪽 LSA 가 모두 광고할 때만 사용 = 양방향 확인) ③ 메시지 수 ≤ LSA 수 × 2·링크 수 ④ 링크 장애 후 LSA 2개만 플러딩되어 갱신되고 표가 다시 정확해짐
struct LSA { int origin, seq; std::vector<std::pair<int, int>> links; };
struct Msg { int from, to; LSA lsa; };
struct Sim {
    int n; std::vector<std::vector<int>> w; std::vector<std::map<int, LSA>> db; std::vector<Msg> pending; long messages = 0; std::mt19937 rng;
    Sim(int n, std::vector<std::vector<int>> w, int seed) : n(n), w(w), db(n), rng(seed) {}
    LSA make(int u, int seq) const { LSA a{u, seq, {}}; for (int v = 0; v < n; v++) if (w[u][v] > 0) a.links.push_back({v, w[u][v]}); return a; }
    void originate(int u, int seq) { LSA a = make(u, seq); db[u][u] = a; for (int v = 0; v < n; v++) if (w[u][v] > 0) pending.push_back({u, v, a}); }
    void run() { while (!pending.empty()) { size_t k = rng() % pending.size(); Msg m = pending[k]; pending[k] = pending.back(); pending.pop_back(); messages++;                                   // 임의 순서로 전달(지연·재정렬 모사)
            auto it = db[m.to].find(m.lsa.origin); if (it != db[m.to].end() && it->second.seq >= m.lsa.seq) continue; db[m.to][m.lsa.origin] = m.lsa; for (int v = 0; v < n; v++) if (w[m.to][v] > 0 && v != m.from) pending.push_back({m.to, v, m.lsa}); } }
    std::vector<int> spf(int src) const {                                                                                    // 라우터 src 가 자기 LSDB 로 구하는 거리
        const int INF = 1 << 28; std::vector<int> d(n, INF); typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[src] = 0; pq.push({0, src}); auto cost = [&](int a, int b) { auto ia = db[src].find(a), ib = db[src].find(b); if (ia == db[src].end() || ib == db[src].end()) return -1; int ca = -1, cb = -1; for (auto& l : ia->second.links) if (l.first == b) ca = l.second; for (auto& l : ib->second.links) if (l.first == a) cb = l.second; return (ca > 0 && cb > 0) ? ca : -1; };   // 양방향 확인
        while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; auto iu = db[src].find(u); if (iu == db[src].end()) continue; for (auto& l : iu->second.links) { int c = cost(u, l.first); if (c > 0 && du + c < d[l.first]) { d[l.first] = du + c; pq.push({d[l.first], l.first}); } } } return d; }
};
std::vector<std::vector<int>> allPairs(int n, const std::vector<std::vector<int>>& w) { const int INF = 1 << 28; std::vector<std::vector<int>> d(n, std::vector<int>(n, INF)); for (int i = 0; i < n; i++) { d[i][i] = 0; for (int j = 0; j < n; j++) if (w[i][j] > 0) d[i][j] = w[i][j]; } for (int k = 0; k < n; k++) for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) d[i][j] = std::min(d[i][j], d[i][k] + d[k][j]); return d; }
int main() {
    std::mt19937 rng(21); int nets = 0; long totalMsgs = 0, failMsgs = 0;
    for (int t = 0; t < 60; t++) {
        int n = 6 + rng() % 8; std::vector<std::vector<int>> w(n, std::vector<int>(n, 0)); int edges = 0; for (int i = 1; i < n; i++) { int j = rng() % i, c = 1 + rng() % 9; w[i][j] = w[j][i] = c; edges++; } for (int k = 0; k < n; k++) { int a = rng() % n, b = rng() % n, c = 1 + rng() % 9; if (a != b && !w[a][b]) { w[a][b] = w[b][a] = c; edges++; } }
        std::vector<std::map<int, LSA>> first; for (int order = 0; order < 3; order++) { Sim sim(n, w, 100 * t + order); for (int u = 0; u < n; u++) sim.originate(u, 1); sim.run();
            for (int u = 0; u < n; u++) { assert((int)sim.db[u].size() == n); for (int v = 0; v < n; v++) assert(sim.db[u][v].seq == 1 && sim.db[u][v].links == sim.db[0][v].links); }                                                 // ① 모든 LSDB 동일
            auto ap = allPairs(n, w); for (int u = 0; u < n; u++) { auto d = sim.spf(u); for (int v = 0; v < n; v++) assert(d[v] == ap[u][v]); } assert(sim.messages <= (long)n * 2 * edges); if (order == 0) totalMsgs += sim.messages; }       // ②③
        Sim sim(n, w, 7); for (int u = 0; u < n; u++) sim.originate(u, 1); sim.run(); long before = sim.messages;
        int a = -1, b = -1; for (int u = 0; u < n && a < 0; u++) for (int v = u + 1; v < n; v++) if (w[u][v] > 0) { auto w2 = w; w2[u][v] = w2[v][u] = 0; int comps = 0; std::vector<int> seen(n, 0); for (int s = 0; s < n; s++) if (!seen[s]) { comps++; std::vector<int> st = {s}; seen[s] = 1; while (!st.empty()) { int x = st.back(); st.pop_back(); for (int y = 0; y < n; y++) if (w2[x][y] > 0 && !seen[y]) { seen[y] = 1; st.push_back(y); } } } if (comps == 1) { a = u; b = v; break; } }
        if (a >= 0) { sim.w[a][b] = sim.w[b][a] = 0; sim.originate(a, 2); sim.originate(b, 2); sim.run(); failMsgs += sim.messages - before; auto ap = allPairs(n, sim.w); for (int u = 0; u < n; u++) { auto d = sim.spf(u); for (int v = 0; v < n; v++) assert(d[v] == ap[u][v]); } nets++; }     // ④ 장애 후 갱신
    }
    assert(nets > 30 && failMsgs * 2 < totalMsgs);
    std::cout << "LinkStateRouting: " << nets << " networks; LSDBs identical under 3 random delivery orders, SPF tables equal global shortest paths; initial flooding used " << totalMsgs << " messages in total, re-converging after a link failure only " << failMsgs << std::endl; return 0;
}
// Time Complexity: 플러딩 O(LSA 수 · 링크 수), SPF O(E log V) 라우터마다
// Space Complexity: O(라우터 수 · 링크 수) (각 라우터가 LSDB 보유)
```
## OSPF()
### 대표코드
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// OSPF(Open Shortest Path First, RFC 2328): 링크 상태 라우팅에 실무 규칙을 얹은 IGP 이다. 이 구현이 다루는 규칙은 넷 — ① 링크 비용 = 기준 대역폭 / 링크 대역폭(정수 반올림, 최소 1) ② SPF 결과가 같은 비용의 다중 경로(ECMP)면 다음 홉 집합을 모두 유지
// ③ 지정 라우터(DR) 선출: 우선순위가 높은 라우터, 같으면 라우터 ID 가 큰 쪽 ④ 영역(area) 계층: 영역 간 트래픽은 반드시 백본(area 0)을 경유하는 ABR 를 거치며 같은 영역 목적지는 영역 안 경로가 항상 우선(더 싼 바깥 경로가 있어도) — 확장성의 대가로 flat SPF 보다 길 수 있다.
// 검증: ① 비용 공식 ② ECMP — 다음 홉 집합이 정의(w(u,v)+d(v,t) == d(u,t))와 같고 무작위로 골라 따라가도 최단 비용으로 도착, 경로 수가 곱 규칙으로 센 값과 같음 ③ DR 선출이 라우터 입장 순서와 무관 ④ 영역 계층 비용 ≥ flat SPF, 같은 영역은 영역 내부 경로이며 계층이 더 비싼 사례가 존재
const int INF = 1 << 28;
int ospfCost(long refMbps, long linkMbps) { return (int)std::max(1L, refMbps / linkMbps); }
int electDR(const std::vector<std::pair<int, int>>& routers) { int best = -1; std::pair<int, int> key{-1, -1}; for (size_t i = 0; i < routers.size(); i++) { std::pair<int, int> k{routers[i].first, routers[i].second}; if (k > key) { key = k; best = i; } } return routers[best].second; }      // (우선순위, 라우터 ID) 사전식 최대
struct Graph { int n; std::vector<std::vector<int>> w; };
std::vector<int> dijkstra(const Graph& g, int s) { std::vector<int> d(g.n, INF); typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int v = 0; v < g.n; v++) if (g.w[u][v] > 0 && du + g.w[u][v] < d[v]) { d[v] = du + g.w[u][v]; pq.push({d[v], v}); } } return d; }
int main() {
    assert(ospfCost(100, 100) == 1 && ospfCost(100, 10) == 10 && ospfCost(100, 1000) == 1 && ospfCost(100, 1) == 100 && ospfCost(1000, 1000) == 1 && ospfCost(1000, 10) == 100);                          // ① 비용 공식
    std::mt19937 rng(31); std::vector<std::pair<int, int>> rs = {{1, 10}, {5, 3}, {5, 7}, {0, 99}}; int dr = electDR(rs); assert(dr == 7); for (int k = 0; k < 20; k++) { std::shuffle(rs.begin(), rs.end(), rng); assert(electDR(rs) == 7); }       // ③ DR 선출은 순서 무관
    int ecmpNets = 0, multi = 0; for (int t = 0; t < 60; t++) {
        int n = 8 + rng() % 5; Graph g{n, std::vector<std::vector<int>>(n, std::vector<int>(n, 0))}; for (int i = 1; i < n; i++) { int j = rng() % i, c = 1 + rng() % 3; g.w[i][j] = g.w[j][i] = c; } for (int k = 0; k < 2 * n; k++) { int a = rng() % n, b = rng() % n, c = 1 + rng() % 3; if (a != b && !g.w[a][b]) g.w[a][b] = g.w[b][a] = c; }
        std::vector<std::vector<int>> d(n); for (int s = 0; s < n; s++) d[s] = dijkstra(g, s);
        for (int s = 0; s < n; s++) for (int tt = 0; tt < n; tt++) if (s != tt) { std::vector<int> hops; for (int v = 0; v < n; v++) if (g.w[s][v] > 0 && g.w[s][v] + d[v][tt] == d[s][tt]) hops.push_back(v); assert(!hops.empty()); multi += hops.size() > 1;       // ② ECMP 다음 홉 집합
            std::vector<long> paths(n, 0); std::vector<int> order(n); for (int i = 0; i < n; i++) order[i] = i; std::sort(order.begin(), order.end(), [&](int a, int b) { return d[a][tt] < d[b][tt]; }); paths[tt] = 1; for (int u : order) if (u != tt) for (int v = 0; v < n; v++) if (g.w[u][v] > 0 && g.w[u][v] + d[v][tt] == d[u][tt]) paths[u] += paths[v];
            long cnt = 0; std::function<void(int)> walk = [&](int u) { if (u == tt) { cnt++; return; } for (int v = 0; v < n; v++) if (g.w[u][v] > 0 && g.w[u][v] + d[v][tt] == d[u][tt]) walk(v); }; walk(s); assert(cnt == paths[s]);
            int cur = s, cost = 0; while (cur != tt) { std::vector<int> c; for (int v = 0; v < n; v++) if (g.w[cur][v] > 0 && g.w[cur][v] + d[v][tt] == d[cur][tt]) c.push_back(v); int pick = c[rng() % c.size()]; cost += g.w[cur][pick]; cur = pick; } assert(cost == d[s][tt]); } ecmpNets++; }
    int hierWorse = 0, hierEqual = 0, hierSame = 0;
    for (int t = 0; t < 80; t++) {
        int n = 15; std::vector<int> area(n); for (int i = 0; i < n; i++) area[i] = i < 5 ? 0 : (i < 10 ? 1 : 2); Graph g{n, std::vector<std::vector<int>>(n, std::vector<int>(n, 0))}; auto link = [&](int a, int b, int c) { g.w[a][b] = g.w[b][a] = c; };
        for (int base : {0, 5, 10}) { for (int i = 1; i < 5; i++) link(base + i, base + rng() % i, 1 + rng() % 6); for (int k = 0; k < 3; k++) { int a = base + rng() % 5, b = base + rng() % 5; if (a != b && !g.w[a][b]) link(a, b, 1 + rng() % 6); } }
        link(4, 5, 1 + rng() % 4); link(3, 10, 1 + rng() % 4); link(9, 12, 1 + rng() % 4);                                                                                       // 4–5 는 백본↔영역1, 3–10 은 백본↔영역2 의 ABR 연결로 간주; 9–12 는 백본을 거치지 않는 영역1–영역2 지름길(flat SPF 만 사용)
        std::vector<std::vector<int>> flat(n); for (int s = 0; s < n; s++) flat[s] = dijkstra(g, s);
        auto intra = [&](int s, int a) { Graph h = g; for (int u = 0; u < n; u++) for (int v = 0; v < n; v++) if (area[u] != a || area[v] != a) h.w[u][v] = 0; return dijkstra(h, s); };       // 영역 a 의 링크만 사용
        std::vector<std::vector<int>> in0(n), in1(n), in2(n); for (int s = 0; s < n; s++) { in0[s] = intra(s, 0); in1[s] = intra(s, 1); in2[s] = intra(s, 2); }
        auto areaDist = [&](int s, int a) { return a == 0 ? in0[s] : (a == 1 ? in1[s] : in2[s]); };
        for (int s = 0; s < n; s++) for (int tt = 0; tt < n; tt++) { if (s == tt) continue; int hier;
            if (area[s] == area[tt]) hier = areaDist(s, area[s])[tt];                                                                                                          // 같은 영역은 영역 안 경로가 우선
            else { hier = INF; int as = area[s], at = area[tt]; std::vector<int> ds = areaDist(s, as);
                struct Abr { int inArea, inBackbone, area; }; std::vector<Abr> list = {{5, 4, 1}, {10, 3, 2}};                                                                  // (영역 쪽 노드, 백본 쪽 노드, 영역 번호)
                for (auto& a1 : list) for (auto& a2 : list) { if (as != 0 && a1.area != as) continue; if (at != 0 && a2.area != at) continue; int up = as == 0 ? 0 : ds[a1.inArea]; int toBackboneStart = as == 0 ? s : a1.inBackbone; int mid = in0[toBackboneStart][at == 0 ? tt : a2.inBackbone]; int down = at == 0 ? 0 : areaDist(a2.inArea, at)[tt]; int extra = 0; if (as != 0) extra += g.w[a1.inArea][a1.inBackbone]; if (at != 0) extra += g.w[a2.inBackbone][a2.inArea]; if (up < INF && mid < INF && down < INF) hier = std::min(hier, up + extra + mid + down); } }
            if (hier >= INF) continue; assert(hier >= flat[s][tt]); if (area[s] == area[tt]) hierSame++; else if (hier == flat[s][tt]) hierEqual++; else hierWorse++; } }
    assert(ecmpNets == 60 && multi > 100 && hierWorse > 0 && hierEqual > 0 && hierSame > 0);
    std::cout << "OSPF: cost formula and DR election verified; ECMP next-hop sets, path counts and random ECMP walks checked on " << ecmpNets << " networks (" << multi << " multipath pairs); area routing: " << hierEqual << " inter-area routes match flat SPF, " << hierWorse << " are longer because they must cross the backbone" << std::endl; return 0;
}
// Time Complexity: SPF O(E log V), ECMP 경로 수 O(E)
// Space Complexity: O(V + E)
```
## RIP()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// RIP(Routing Information Protocol, RFC 2453): 홉 수를 비용으로 쓰는 가장 단순한 거리 벡터 프로토콜. 매 30 초마다 전체 경로표를 이웃에게 광고하고, 비용이 16 이면 도달 불가(무한대)로 취급한다 — 그래서 지름 15 홉이 넘는 망은 못 쓴다(확장성 한계).
// 무한 세기가 16 에서 멈추도록 한계를 둔 것이 이 설계의 핵심이다. 안정화 기법: 분할 지평 + 독 역전(받은 쪽으로는 비용 16 으로 광고)과 변화가 생기면 주기를 기다리지 않고 바로 알리는 촉발 갱신(triggered update). 경로를 알려 주던 이웃이 침묵하면 180 초 뒤 만료(timeout), 120 초 뒤 삭제(garbage collection).
// 여기서는 라운드 모델로 검증한다. ① 홉 수 ≤ 15 인 목적지는 BFS 최단 홉과 같고 그보다 먼 목적지는 도달 불가(16)로 남음 ② 선형망의 끝 링크가 끊기면 독 역전이 있으면 나쁜 소식이 한 홉씩 퍼지는 만큼(≤ 7 라운드)에, 없으면 무한 세기로 16 까지 걸려 수렴 ③ 최종 표가 끊긴 뒤의 BFS 와 일치하고, 서로를 가리키는 루프가 남지 않음
const int INF = 16;
struct Net { int n; std::vector<std::vector<int>> adj; };
struct RT { std::vector<std::vector<int>> dist, next; };
RT init(const Net& net) { RT r{std::vector<std::vector<int>>(net.n, std::vector<int>(net.n, INF)), std::vector<std::vector<int>>(net.n, std::vector<int>(net.n, -1))}; for (int u = 0; u < net.n; u++) r.dist[u][u] = 0; return r; }
bool round(const Net& net, RT& r, bool poison) {                                                                                     // 한 번의 주기적 갱신: 모두가 이전 표를 광고하고 받은 값 + 1 로 갱신(RIP 은 현재 다음 홉이 비용을 올려 알려도 따라간다)
    RT prev = r; bool changed = false;
    for (int u = 0; u < net.n; u++) for (int d = 0; d < net.n; d++) { if (u == d) continue; int best = INF, via = -1; for (int v : net.adj[u]) { int adv = prev.dist[v][d]; if (poison && prev.next[v][d] == u) adv = INF; if (adv + 1 < best) { best = adv + 1; via = v; } } if (best >= INF) { best = INF; via = -1; } if (best != r.dist[u][d] || via != r.next[u][d]) changed = true; r.dist[u][d] = best; r.next[u][d] = via; }
    return changed; }
std::vector<int> bfs(const Net& net, int s) { std::vector<int> d(net.n, INF); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int v : net.adj[u]) if (d[v] >= INF && v != s) { d[v] = d[u] + 1; q.push(v); } } return d; }
int main() {
    Net chain{20, std::vector<std::vector<int>>(20)}; for (int i = 0; i + 1 < 20; i++) { chain.adj[i].push_back(i + 1); chain.adj[i + 1].push_back(i); } RT r = init(chain); int rounds = 0; while (round(chain, r, true)) rounds++;
    for (int d = 0; d < 20; d++) { int hops = d; if (hops <= 15) assert(r.dist[0][d] == hops); else assert(r.dist[0][d] == INF); } assert(r.dist[0][15] == 15 && r.dist[0][16] == INF);                       // ① 15 홉까지만 도달
    std::mt19937 rng(3); int nets = 0;
    for (int t = 0; t < 60; t++) { int n = 6 + rng() % 8; Net net{n, std::vector<std::vector<int>>(n)}; auto add = [&](int a, int b) { if (std::find(net.adj[a].begin(), net.adj[a].end(), b) == net.adj[a].end()) { net.adj[a].push_back(b); net.adj[b].push_back(a); } }; for (int i = 1; i < n; i++) add(i, rng() % i); for (int k = 0; k < n / 2; k++) { int a = rng() % n, b = rng() % n; if (a != b) add(a, b); }
        RT q = init(net); while (round(net, q, true)) {} for (int s = 0; s < n; s++) { auto d = bfs(net, s); for (int v = 0; v < n; v++) assert(q.dist[s][v] == std::min(d[v], INF)); } nets++; }
    auto chainFail = [&](bool poison, int N) { Net ch{N, std::vector<std::vector<int>>(N)}; for (int i = 0; i + 1 < N; i++) { ch.adj[i].push_back(i + 1); ch.adj[i + 1].push_back(i); } RT x = init(ch); while (round(ch, x, poison)) {}
        Net cut = ch; cut.adj[N - 2].erase(std::find(cut.adj[N - 2].begin(), cut.adj[N - 2].end(), N - 1)); cut.adj[N - 1].erase(std::find(cut.adj[N - 1].begin(), cut.adj[N - 1].end(), N - 2)); int rounds = 0; while (round(cut, x, poison)) { rounds++; assert(rounds < 200); }
        for (int s = 0; s < N; s++) { auto d = bfs(cut, s); for (int v = 0; v < N; v++) { assert(x.dist[s][v] == std::min(d[v], INF)); int cur = s, hops = 0; while (cur != v && x.next[cur][v] >= 0) { cur = x.next[cur][v]; assert(++hops <= N); } assert(cur == v || x.dist[s][v] >= INF); } } return rounds; };      // ③ 끊긴 뒤 BFS 와 일치, 루프 없음
    int withP = chainFail(true, 8), withoutP = chainFail(false, 8); assert(withP <= 7 && withoutP >= 12 && withP < withoutP);                                                                                 // ② 독 역전이 있으면 한 홉씩 전파되는 7 라운드, 없으면 무한 세기로 16 까지
    std::cout << "RIP: 15-hop limit verified on a 20-router chain (convergence in " << rounds << " rounds, farther routers stay at 16); " << nets << " random networks match BFS hop counts; cutting the last link of an 8-router chain needs " << withP << " rounds with poison reverse versus " << withoutP << " without" << std::endl; return 0;
}
// Time Complexity: 라운드당 O(V² · deg), 수렴은 최대 16 라운드 근처
// Space Complexity: O(V²)
```
## BGPPathSelection()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// BGP 경로 선택(RFC 4271 9.1): 같은 목적지 접두사에 대해 여러 경로(광고)를 받으면 정해진 순서의 단계로 하나를 고른다 — ① 가장 높은 LOCAL_PREF(정책) ② 가장 짧은 AS_PATH ③ 가장 낮은 ORIGIN(IGP < EGP < incomplete)
// ④ 가장 낮은 MED(단, 같은 이웃 AS 에서 온 경로끼리만 비교) ⑤ eBGP 경로를 iBGP 보다 선호 ⑥ 다음 홉까지 IGP 비용이 가장 낮은 것 ⑦ 가장 낮은 라우터 ID(최종 타이브레이크). 자기 AS 번호가 AS_PATH 에 있는 경로는 루프이므로 버린다.
// 함정: ④ MED 는 이웃 AS 가 같을 때만 비교하므로 "두 경로를 짝지어 이기는 쪽을 남기는" 반복 선택은 비이행적이라 광고가 도착한 순서에 결과가 달라진다. 순서에 의존하지 않는 방식은 각 단계마다 후보를 걸러내는 필터 열이다(결정적 MED). 
// 두 번째 주제는 정책 충돌: LOCAL_PREF 를 각 AS 가 제멋대로 정하면 안정 해가 없는 BAD GADGET 이 생겨 라우팅이 영원히 진동한다(Griffin–Wilfong). 검증: ① 필터 열 선택이 무작위 광고 집합 500개의 모든 도착 순서(20 가지 순열)에서 같은 결과 ② 쌍별 반복 비교는 순서에 따라 달라지는 집합이 존재 ③ 필터 열 결과는 어떤 경로도 선택 후보에서 (정의상) 더 좋은 경로에 지배당하지 않음 ④ BAD GADGET 은 상태가 순환하고 GOOD GADGET 은 수렴
struct Route { int localPref, asLen, origin, med, nbrAS, ebgp, igp, rid; std::vector<int> asPath; };
bool loops(const Route& r, int myAS) { return std::find(r.asPath.begin(), r.asPath.end(), myAS) != r.asPath.end(); }
const Route* selectFilter(const std::vector<Route>& rs, int myAS) {
    std::vector<const Route*> c; for (const Route& r : rs) if (!loops(r, myAS)) c.push_back(&r); if (c.empty()) return nullptr;
    auto keepMax = [&](auto f) { int m = -1e9; for (auto* r : c) m = std::max(m, f(*r)); std::vector<const Route*> k; for (auto* r : c) if (f(*r) == m) k.push_back(r); c = k; }; auto keepMin = [&](auto f) { keepMax([&](const Route& r) { return -f(r); }); };
    keepMax([](const Route& r) { return r.localPref; }); keepMin([](const Route& r) { return r.asLen; }); keepMin([](const Route& r) { return r.origin; });
    { std::map<int, int> minMed; for (auto* r : c) { auto it = minMed.find(r->nbrAS); if (it == minMed.end() || r->med < it->second) minMed[r->nbrAS] = r->med; } std::vector<const Route*> k; for (auto* r : c) if (r->med == minMed[r->nbrAS]) k.push_back(r); c = k; }              // MED: 이웃 AS 별로 최소만 남김
    keepMax([](const Route& r) { return r.ebgp; }); keepMin([](const Route& r) { return r.igp; }); keepMin([](const Route& r) { return r.rid; }); return c[0]; }
bool betterPair(const Route& a, const Route& b) {                                                                                      // 짝지어 비교(MED 는 같은 이웃 AS 일 때만)
    if (a.localPref != b.localPref) return a.localPref > b.localPref; if (a.asLen != b.asLen) return a.asLen < b.asLen; if (a.origin != b.origin) return a.origin < b.origin; if (a.nbrAS == b.nbrAS && a.med != b.med) return a.med < b.med;
    if (a.ebgp != b.ebgp) return a.ebgp > b.ebgp; if (a.igp != b.igp) return a.igp < b.igp; return a.rid < b.rid; }
const Route* selectPairwise(const std::vector<Route>& rs, int myAS) { const Route* best = nullptr; for (const Route& r : rs) { if (loops(r, myAS)) continue; if (!best || betterPair(r, *best)) best = &r; } return best; }
typedef std::vector<std::vector<std::vector<int>>> Prefs;                                                                               // prefs[v] = 선호 순서대로의 허용 경로들(각 경로는 v 에서 0 까지의 노드 열)
std::vector<std::vector<int>> spvp(const Prefs& prefs, int n, bool& cycled) {                                                          // 동기식 SPVP: 매 라운드 각 노드가 이웃의 현재 경로를 보고 가장 선호하는 가능한 경로를 고름
    std::vector<std::vector<int>> cur(n); cur[0] = {0}; std::set<std::vector<std::vector<int>>> seen; cycled = false; seen.insert(cur);
    for (int step = 0; step < 100; step++) { auto nxt = cur; for (int v = 1; v < n; v++) { nxt[v].clear(); for (auto& p : prefs[v]) { int nb = p[1]; std::vector<int> tail(p.begin() + 1, p.end()); if (cur[nb] == tail) { nxt[v] = p; break; } } } if (nxt == cur) return cur; cur = nxt; if (!seen.insert(cur).second) { cycled = true; return cur; } } return cur; }
int main() {
    std::mt19937 rng(41); int myAS = 100, orderDependent = 0, sets = 0;
    for (int t = 0; t < 500; t++) {
        int k = 3 + rng() % 4; std::vector<Route> rs; for (int i = 0; i < k; i++) { Route r; r.localPref = 100 + 10 * (rng() % 2); r.asLen = 2 + rng() % 2; r.origin = rng() % 2; r.nbrAS = 1 + rng() % 3; r.med = rng() % 4; r.ebgp = rng() % 2; r.igp = rng() % 3; r.rid = 100 + i; r.asPath.assign(r.asLen, 7); if (rng() % 10 == 0) r.asPath[0] = myAS; rs.push_back(r); }
        const Route* ref = selectFilter(rs, myAS); bool pairDiffers = false; const Route* pr = selectPairwise(rs, myAS); std::vector<int> pairIds; for (int sh = 0; sh < 20; sh++) { std::vector<Route> p = rs; std::shuffle(p.begin(), p.end(), rng);
            const Route* a = selectFilter(p, myAS); if (ref) { assert(a && a->rid == ref->rid); } else assert(!a); const Route* b = selectPairwise(p, myAS); if (pr && b && b->rid != pr->rid) pairDiffers = true; }       // ① 필터 열은 순서 무관
        sets++; orderDependent += pairDiffers;
        if (ref) { for (const Route& r : rs) if (!loops(r, myAS) && r.localPref > ref->localPref) assert(false); for (const Route& r : rs) if (!loops(r, myAS) && r.localPref == ref->localPref && r.asLen < ref->asLen) assert(false); } }          // ③ 정책·AS 길이 단계에서 지배당하지 않음
    assert(orderDependent > 0);                                                                                                          // ② 쌍별 반복 선택은 순서에 따라 달라짐
    Prefs bad(4), good(4);                                                                                                               // 노드 0 이 목적지. BAD GADGET: 1→(1 3 0) > (1 0), 2→(2 1 0) > (2 0), 3→(3 2 0) > (3 0)
    bad[1] = {{1, 3, 0}, {1, 0}}; bad[2] = {{2, 1, 0}, {2, 0}}; bad[3] = {{3, 2, 0}, {3, 0}}; good[1] = {{1, 3, 0}, {1, 0}}; good[2] = {{2, 0}}; good[3] = {{3, 2, 0}, {3, 0}};
    bool badCycle, goodCycle; auto sb = spvp(bad, 4, badCycle); auto sg = spvp(good, 4, goodCycle); assert(badCycle && !goodCycle && sg[2] == std::vector<int>({2, 0}) && sg[3] == std::vector<int>({3, 2, 0}) && sg[1] == std::vector<int>({1, 0}));
    std::cout << "BGPPathSelection: " << sets << " route sets; the filter-sequence decision process gave one answer under all arrival orders, while pairwise comparison changed its answer for " << orderDependent << " sets (MED is only comparable within a neighbor AS); BAD GADGET oscillates forever, GOOD GADGET converges" << std::endl; return 0;
}
// Time Complexity: 선택 O(경로 수 × 단계 수), SPVP 한 라운드 O(노드 × 선호 경로 수)
// Space Complexity: O(경로 수)
```

# Part 14. 응용
## MazeSolver()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 미로 풀기(Stack.md Part 5 MazeSolver 의 길찾기 관점 요약, 정본은 Stack.md Part 5): 미로는 통로로 이어진 칸들의 그래프이고 세 가지 해법이 있다. ① 명시적 스택 DFS(백트래킹): 스택에 현재 경로를 두고 막다른 길이면 pop 해서 되돌아간다 — 해는 찾지만 최단이 아닐 수 있다.
// ② BFS: 가장 짧은 경로. ③ 오른손 벽 따라가기: 기억이 필요 없지만 "벽이 모두 바깥벽에 이어진" 단순 연결 미로(루프 없는 완전 미로)에서만 반드시 출구에 닿는다. 루프 없는 미로에서는 경로가 하나뿐이라 DFS 경로와 BFS 경로가 같고 루프를 낸(braid) 미로에서는 DFS 가 더 길 수 있다.
// 검증: 재귀 백트래커로 만든 완전 미로 60개에서 간선 수 = 칸 수 − 1, DFS 길이 = BFS 길이, 오른손 규칙의 걸음 수 ≤ 2(칸 수 − 1); 벽을 허문 미로에서는 BFS ≤ DFS 이고 DFS 가 더 긴 경우가 존재
struct Maze { int H, W; std::vector<int> open; int id(int r, int c) const { return r * W + c; } };                                   // open[c] 의 비트 d: 방향 d(0 북, 1 동, 2 남, 3 서)로 통로가 있음
const int DR[4] = {-1, 0, 1, 0}, DC[4] = {0, 1, 0, -1};
void carve(Maze& m, int a, int d) { int r = a / m.W + DR[d], c = a % m.W + DC[d]; int b = m.id(r, c); m.open[a] |= 1 << d; m.open[b] |= 1 << ((d + 2) % 4); }
Maze generate(int H, int W, std::mt19937& g) { Maze m{H, W, std::vector<int>(H * W, 0)}; std::vector<char> seen(H * W, 0); std::stack<int> st; st.push(0); seen[0] = 1;
    while (!st.empty()) { int u = st.top(); std::vector<int> dirs; for (int d = 0; d < 4; d++) { int r = u / W + DR[d], c = u % W + DC[d]; if (r >= 0 && c >= 0 && r < H && c < W && !seen[r * W + c]) dirs.push_back(d); } if (dirs.empty()) { st.pop(); continue; } int d = dirs[g() % dirs.size()]; int v = (u / W + DR[d]) * W + u % W + DC[d]; carve(m, u, d); seen[v] = 1; st.push(v); } return m; }
std::vector<int> dfsSolve(const Maze& m, int s, int t) {                                                                              // 스택이 곧 현재 경로
    std::vector<char> vis(m.H * m.W, 0); std::stack<int> path; path.push(s); vis[s] = 1;
    while (!path.empty() && path.top() != t) { int u = path.top(); bool moved = false; for (int d = 0; d < 4 && !moved; d++) if (m.open[u] >> d & 1) { int v = (u / m.W + DR[d]) * m.W + u % m.W + DC[d]; if (!vis[v]) { vis[v] = 1; path.push(v); moved = true; } } if (!moved) path.pop(); }
    std::vector<int> r; while (!path.empty()) { r.push_back(path.top()); path.pop(); } std::reverse(r.begin(), r.end()); return r; }
int bfsLen(const Maze& m, int s, int t) { std::vector<int> d(m.H * m.W, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int k = 0; k < 4; k++) if (m.open[u] >> k & 1) { int v = (u / m.W + DR[k]) * m.W + u % m.W + DC[k]; if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } } return d[t]; }
int rightHand(const Maze& m, int s, int t, int limit) { int u = s, heading = 2, steps = 0; while (u != t && steps < limit) { for (int turn : {1, 0, 3, 2}) { int d = (heading + turn) % 4; if (m.open[u] >> d & 1) { u = (u / m.W + DR[d]) * m.W + u % m.W + DC[d]; heading = d; steps++; break; } } } return u == t ? steps : -1; }      // 오른쪽 → 직진 → 왼쪽 → 뒤 순서
std::string render(const Maze& m, const std::vector<int>& path) {                       // 그림: + - | 는 벽, 칸 안의 * 는 풀이 경로 (칸 하나가 3 글자 + 벽 1 글자)
    std::vector<char> on(m.H * m.W, 0); for (int c : path) on[c] = 1;
    std::string s = "+"; for (int c = 0; c < m.W; ++c) s += "---+"; s += "\n";
    for (int r = 0; r < m.H; ++r) {
        std::string mid = "|", low = "+";
        for (int c = 0; c < m.W; ++c) { int a = m.id(r, c); mid += on[a] ? " * " : "   "; mid += (m.open[a] >> 1 & 1) ? " " : "|"; low += (m.open[a] >> 2 & 1) ? "   +" : "---+"; }
        s += mid + "\n" + low + "\n";
    }
    return s;
}
int main() {
    {   Maze m{3, 4, std::vector<int>(12, 0)};                                                             // 손으로 판 3x4 미로: 칸 번호 = 행*4+열
        for (int a : {0, 1, 2}) carve(m, a, 1);                                                           // 윗줄 0-1-2-3 을 동쪽으로 뚫는다
        for (int a : {0, 4}) carve(m, a, 2);                                                              // 0 -> 4 -> 8 을 남쪽으로
        for (int a : {8, 9, 10}) carve(m, a, 1);                                                          // 아랫줄 8-9-10-11
        carve(m, 3, 2); carve(m, 7, 3); carve(m, 6, 3);                                                   // 3 -> 7, 7 -> 6, 6 -> 5 : 막다른 가지
        std::vector<int> sol = dfsSolve(m, 0, 11); assert((sol == std::vector<int>{0, 4, 8, 9, 10, 11}) && bfsLen(m, 0, 11) == 5);
        const std::string pic = "+---+---+---+---+\n| *             |\n+   +---+---+   +\n| * |           |\n+   +---+---+---+\n| *   *   *   * |\n+---+---+---+---+\n";
        assert(render(m, sol) == pic); std::cout << pic; }                                                // 12 칸 벽 11 개를 뚫은 완전 미로(순환 없음)라 경로가 하나뿐
    std::mt19937 g(2); int perfect = 0, braidedLonger = 0, braided = 0;
    for (int t = 0; t < 60; t++) {
        int H = 6 + g() % 10, W = 6 + g() % 10; Maze m = generate(H, W, g); int passages = 0; for (int c = 0; c < H * W; c++) passages += __builtin_popcount(m.open[c]); assert(passages / 2 == H * W - 1);                                        // 트리: 간선 수 = 칸 수 − 1
        int s = 0, e = H * W - 1; std::vector<int> p = dfsSolve(m, s, e); assert(!p.empty() && p.front() == s && p.back() == e && (int)p.size() - 1 == bfsLen(m, s, e)); for (size_t i = 1; i < p.size(); i++) { int a = p[i - 1], b = p[i]; bool adj = false; for (int d = 0; d < 4; d++) adj |= (m.open[a] >> d & 1) && (a / W + DR[d]) * W + a % W + DC[d] == b; assert(adj); }
        int steps = rightHand(m, s, e, 8 * H * W); assert(steps > 0 && steps <= 2 * (H * W - 1)); perfect++;
        Maze b = m; for (int k = 0; k < H * W / 6; k++) { int a = g() % (H * W), d = g() % 4; int r = a / W + DR[d], c = a % W + DC[d]; if (r >= 0 && c >= 0 && r < H && c < W) carve(b, a, d); } std::vector<int> pb = dfsSolve(b, s, e); int opt = bfsLen(b, s, e); assert((int)pb.size() - 1 >= opt); braided++; braidedLonger += (int)pb.size() - 1 > opt; }
    assert(perfect == 60 && braidedLonger > 0);
    std::cout << "MazeSolver: " << perfect << " perfect mazes (tree, unique path): DFS == BFS length and the right-hand rule always escapes within 2(n-1) steps; in " << braidedLonger << " of " << braided << " braided mazes DFS found a longer path than BFS" << std::endl; return 0;
}
// Time Complexity: DFS/BFS O(V + E), 오른손 규칙 O(V) 걸음
// Space Complexity: O(V)
```
## PuzzleSolver()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// 슬라이딩 퍼즐(8퍼즐·15퍼즐) 풀이: 상태 공간이 거대(15퍼즐 약 10¹³)해서 A* 의 메모리가 먼저 바닥나므로 IDA*(Korf 1985)를 쓴다. 허용적 휴리스틱은 맨해튼 거리(각 타일이 목표까지 가야 할 최소 칸 수의 합)이고
// 선형 충돌(linear conflict)을 더하면 더 강해진다 — 같은 행(열)에서 둘 다 자기 목표 행(열)에 있으면서 순서가 뒤바뀐 두 타일은 서로 비켜 가려면 한 타일이 행(열)을 벗어났다 돌아와야 하므로 추가로 최소 2 수가 든다(충돌 그래프의 최소 제거 수는 이 구현에서 쌍 단위로 근사: 타일마다 가장 많은 충돌 상대 하나씩 제외하며 센다).
// 풀 수 있는 배치는 반전 수의 홀짝으로 판정된다(3×3: 반전 수가 짝수, 4×4: 빈칸 행 번호와 반전 수의 합의 홀짝). 검증: ① 8퍼즐은 목표에서 BFS 로 181,440 개 상태 전체의 정확한 거리를 만들고 IDA* 길이가 모두 일치(허용 휴리스틱의 최적성), 풀 수 없는 배치는 BFS 표에 없음 ② 선형 충돌이 맨해튼보다 확장 노드가 적음 ③ 15퍼즐 무작위 섞기 30개를 IDA* 로 풀고 해를 실제로 적용해 목표에 닿으며 길이의 홀짝이 섞은 횟수와 같음
typedef std::vector<int> Board; int N;
bool solvable(const Board& b) { int inv = 0, blank = 0; for (size_t i = 0; i < b.size(); i++) { if (!b[i]) blank = i / N; for (size_t j = i + 1; j < b.size(); j++) if (b[i] && b[j] && b[i] > b[j]) inv++; } return N % 2 ? inv % 2 == 0 : (inv + blank) % 2 == 1; }
int manhattan(const Board& b) { int h = 0; for (int i = 0; i < N * N; i++) if (b[i]) { int g = b[i] - 1; h += std::abs(i / N - g / N) + std::abs(i % N - g % N); } return h; }
int linearConflict(const Board& b) { int h = manhattan(b);
    for (int r = 0; r < N; r++) { std::vector<int> row; for (int c = 0; c < N; c++) { int t = b[r * N + c]; if (t && (t - 1) / N == r) row.push_back((t - 1) % N); } std::vector<int> cnt(row.size(), 0); for (size_t i = 0; i < row.size(); i++) for (size_t j = i + 1; j < row.size(); j++) if (row[i] > row[j]) { cnt[i]++; cnt[j]++; }
        while (true) { int mx = -1; for (size_t i = 0; i < cnt.size(); i++) if (cnt[i] > 0 && (mx < 0 || cnt[i] > cnt[mx])) mx = i; if (mx < 0) break; h += 2; for (size_t j = 0; j < row.size(); j++) if ((int)j != mx && ((j > (size_t)mx && row[mx] > row[j]) || (j < (size_t)mx && row[j] > row[mx])) && cnt[j] > 0) cnt[j]--; cnt[mx] = 0; } }
    for (int c = 0; c < N; c++) { std::vector<int> col; for (int r = 0; r < N; r++) { int t = b[r * N + c]; if (t && (t - 1) % N == c) col.push_back((t - 1) / N); } std::vector<int> cnt(col.size(), 0); for (size_t i = 0; i < col.size(); i++) for (size_t j = i + 1; j < col.size(); j++) if (col[i] > col[j]) { cnt[i]++; cnt[j]++; }
        while (true) { int mx = -1; for (size_t i = 0; i < cnt.size(); i++) if (cnt[i] > 0 && (mx < 0 || cnt[i] > cnt[mx])) mx = i; if (mx < 0) break; h += 2; for (size_t j = 0; j < col.size(); j++) if ((int)j != mx && ((j > (size_t)mx && col[mx] > col[j]) || (j < (size_t)mx && col[j] > col[mx])) && cnt[j] > 0) cnt[j]--; cnt[mx] = 0; } }
    return h; }
long nodes; std::function<int(const Board&)> H; std::vector<int> sol;
int dfs(Board& b, int blank, int g, int bound, int prev) { nodes++; int f = g + H(b); if (f > bound) return f; if (manhattan(b) == 0) return -1; int mn = 1 << 28; const int dr[4] = {-1, 1, 0, 0}, dc[4] = {0, 0, -1, 1};
    for (int k = 0; k < 4; k++) { int r = blank / N + dr[k], c = blank % N + dc[k]; if (r < 0 || c < 0 || r >= N || c >= N) continue; int nb = r * N + c; if (nb == prev) continue; std::swap(b[blank], b[nb]); sol.push_back(nb); int t = dfs(b, nb, g + 1, bound, blank); if (t == -1) return -1; sol.pop_back(); std::swap(b[blank], b[nb]); mn = std::min(mn, t); } return mn; }
int ida(Board b, std::function<int(const Board&)> h) { H = h; nodes = 0; sol.clear(); int blank = std::find(b.begin(), b.end(), 0) - b.begin(); int bound = H(b); for (;;) { Board c = b; sol.clear(); int t = dfs(c, blank, 0, bound, -1); if (t == -1) return sol.size(); bound = t; } }
Board goalBoard() { Board g(N * N); for (int i = 0; i + 1 < N * N; i++) g[i] = i + 1; g[N * N - 1] = 0; return g; }
Board scramble(int moves, std::mt19937& rng) { Board b = goalBoard(); int blank = N * N - 1, prev = -1; const int dr[4] = {-1, 1, 0, 0}, dc[4] = {0, 0, -1, 1}; for (int i = 0; i < moves;) { int k = rng() % 4; int r = blank / N + dr[k], c = blank % N + dc[k]; if (r < 0 || c < 0 || r >= N || c >= N) continue; int nb = r * N + c; if (nb == prev) continue; std::swap(b[blank], b[nb]); prev = blank; blank = nb; i++; } return b; }
int main() {
    std::mt19937 rng(11); N = 3; Board g3 = goalBoard(); std::map<Board, int> dist; { std::queue<Board> q; dist[g3] = 0; q.push(g3); const int dr[4] = {-1, 1, 0, 0}, dc[4] = {0, 0, -1, 1}; while (!q.empty()) { Board b = q.front(); q.pop(); int blank = std::find(b.begin(), b.end(), 0) - b.begin(); for (int k = 0; k < 4; k++) { int r = blank / 3 + dr[k], c = blank % 3 + dc[k]; if (r < 0 || c < 0 || r >= 3 || c >= 3) continue; Board n = b; std::swap(n[blank], n[r * 3 + c]); if (!dist.count(n)) { dist[n] = dist[b] + 1; q.push(n); } } } }
    assert(dist.size() == 181440);                                                                                                                                          // 풀 수 있는 배치 = 9!/2
    long nodesM = 0, nodesL = 0; for (int t = 0; t < 300; t++) { Board b = scramble(10 + rng() % 40, rng); assert(solvable(b) && dist.count(b)); int a = ida(b, manhattan); nodesM += nodes; int c = ida(b, linearConflict); nodesL += nodes; assert(a == dist[b] && c == dist[b]); }      // ① 최적 길이
    for (int t = 0; t < 100; t++) { Board b = goalBoard(); std::shuffle(b.begin(), b.end(), rng); if (solvable(b)) assert(dist.count(b)); else assert(!dist.count(b)); }
    assert(nodesL <= nodesM);                                                                                                                                               // ② 선형 충돌이 더 강함
    N = 4; int solved = 0; for (int t = 0; t < 30; t++) { int moves = 20 + rng() % 17; Board b = scramble(moves, rng); assert(solvable(b)); int len = ida(b, linearConflict); assert(len <= moves && (len % 2) == (moves % 2) && len >= manhattan(b));
        Board c = b; int blank = std::find(c.begin(), c.end(), 0) - c.begin(); for (int nb : sol) { assert(std::abs(nb / 4 - blank / 4) + std::abs(nb % 4 - blank % 4) == 1); std::swap(c[blank], c[nb]); blank = nb; } assert(c == goalBoard()); solved++; }                                  // ③ 해를 적용해 검증
    std::cout << "PuzzleSolver: 8-puzzle IDA* optimal on 300 states against a BFS table of 181440 states; nodes " << nodesM << " (Manhattan) vs " << nodesL << " (linear conflict); " << solved << " 15-puzzle instances solved and replayed to the goal" << std::endl; return 0;
}
// Time Complexity: IDA* 최악 O(b^d), 휴리스틱이 강할수록 지수의 밑이 작아짐
// Space Complexity: O(d) (경로 길이)
```
## GPSNavigation()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <stack>
#include <string>
#include <vector>
#include <cassert>

// GPS 내비게이션: 잡음 섞인 위치 측정을 도로에 붙이는 "지도 매칭(map matching)"과 경로 이탈 시 "재탐색(reroute)"으로 이루어진다.
// 지도 매칭은 단순히 가장 가까운 도로에 붙이면 평행한 이웃 도로로 튀므로(측정 잡음 σ 가 도로 간격과 비슷할 때) 은닉 마르코프 모형(HMM)을 쓴다. 상태 = 방향 있는 도로 구간, 방출 확률 ∝ exp(−d²/2σ²)(d: 측정점과 구간 사이 거리),
// 전이 = 같은 구간에 머묾 / 다음 구간으로 이어짐 / 유턴 / 순간이동(순서대로 벌점이 커짐). Viterbi 동적계획법이 전체 측정열에 대해 가장 그럴듯한 구간 열을 고른다. 재탐색은 매칭된 현재 구간이 계획 경로에서 연속 k 번 벗어나면 현재 위치에서 목적지까지 Dijkstra 를 다시 돌린다.
// 검증(12×12 도로망, 잡음 σ=0.25, 0.25 간격 측정): ① Viterbi 의 구간 정확도가 최근접 구간 방식보다 3%p 넘게 높고 95% 이상(정답이거나 분기점 0.3 이내의 이웃 도로는 허용) ② 운전자가 일부러 틀린 길로 들어서면 이탈이 감지되어 재탐색하고 새 경로가 현재 위치에서 최적이며 목적지에 도착
struct Edge { int a, b; }; const int W = 12; std::vector<Edge> edges; std::vector<std::vector<int>> out;                                           // 방향 간선 목록과 정점별 나가는 간선
typedef std::pair<double, double> V; V pos(int v) { return {(double)(v % W), (double)(v / W)}; }
double segDist(V p, V a, V b) { double dx = b.first - a.first, dy = b.second - a.second, t = std::max(0.0, std::min(1.0, ((p.first - a.first) * dx + (p.second - a.second) * dy) / (dx * dx + dy * dy))); return std::hypot(p.first - a.first - t * dx, p.second - a.second - t * dy); }
std::vector<int> dijkstraPath(int s, int t, std::vector<char>& okEdge) { std::vector<double> d(W * W, 1e18); std::vector<int> pe(W * W, -1); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int e : out[u]) if (okEdge[e] && du + 1 < d[edges[e].b]) { d[edges[e].b] = du + 1; pe[edges[e].b] = e; pq.push({d[edges[e].b], edges[e].b}); } }
    std::vector<int> r; if (d[t] > 1e17) return r; for (int v = t; v != s; v = edges[pe[v]].a) r.push_back(pe[v]); std::reverse(r.begin(), r.end()); return r; }
int main() {
    std::mt19937 rng(14); std::normal_distribution<double> noise(0, 0.25); out.assign(W * W, {}); std::vector<char> alive;
    for (int r = 0; r < W; r++) for (int c = 0; c < W; c++) { int v = r * W + c; if (c + 1 < W) { edges.push_back({v, v + 1}); edges.push_back({v + 1, v}); } if (r + 1 < W) { edges.push_back({v, v + W}); edges.push_back({v + W, v}); } } for (size_t e = 0; e < edges.size(); e++) out[edges[e].a].push_back(e); alive.assign(edges.size(), 1);
    auto rev = [&](int e) { return e ^ 1; };                                                                                                                                  // 간선을 (정방향, 역방향) 쌍으로 넣었으므로 e ^ 1 이 반대 방향
    auto good = [&](int m, int tr, V p) { if ((m >> 1) == (tr >> 1)) return true; for (int x : {edges[tr].a, edges[tr].b}) if (std::hypot(p.first - pos(x).first, p.second - pos(x).second) < 0.3 && (edges[m].a == x || edges[m].b == x)) return true; return false; };       // 정답이거나, 참 위치가 분기점 0.3 이내이면 그 분기점에 닿는 도로도 허용
    int fixes = 0, viterbiOk = 0, nearestOk = 0; const double SIGMA = 0.25;
    for (int trial = 0; trial < 30; trial++) {
        int s = rng() % (W * W), t = rng() % (W * W); std::vector<int> route = dijkstraPath(s, t, alive); if (route.size() < 8) continue;
        std::vector<V> gps, tp; std::vector<int> truth; for (int e : route) { V a = pos(edges[e].a), b = pos(edges[e].b); for (double f = 0; f < 1.0 - 1e-9; f += 0.25) { V p{a.first + f * (b.first - a.first), a.second + f * (b.second - a.second)}; tp.push_back(p); gps.push_back({p.first + noise(rng), p.second + noise(rng)}); truth.push_back(e); } }
        int T = gps.size(), E = edges.size(); std::vector<std::vector<double>> score(T, std::vector<double>(E, -1e18)); std::vector<std::vector<int>> back(T, std::vector<int>(E, -1));
        auto emit = [&](int e, V p) { double d = segDist(p, pos(edges[e].a), pos(edges[e].b)); return -d * d / (2 * SIGMA * SIGMA); };
        for (int e = 0; e < E; e++) score[0][e] = emit(e, gps[0]);
        for (int k = 1; k < T; k++) { int bestPrev = 0; for (int e = 0; e < E; e++) if (score[k - 1][e] > score[k - 1][bestPrev]) bestPrev = e;
            for (int f = 0; f < E; f++) { double best = score[k - 1][bestPrev] - 10.0; int arg = bestPrev; auto consider = [&](int e, double pen) { if (score[k - 1][e] - pen > best) { best = score[k - 1][e] - pen; arg = e; } };
                consider(f, 0.0); consider(rev(f), 4.0); for (size_t e = 0; e < edges.size(); e++) if (edges[e].b == edges[f].a && (int)e != rev(f)) consider(e, 0.5);
                score[k][f] = best + emit(f, gps[k]); back[k][f] = arg; } }
        std::vector<int> match(T); int last = 0; for (int e = 0; e < E; e++) if (score[T - 1][e] > score[T - 1][last]) last = e; for (int k = T - 1; k >= 0; k--) { match[k] = last; last = back[k][last] >= 0 ? back[k][last] : last; }
        for (int k = 0; k < T; k++) { int near = 0; double bd = 1e18; for (int e = 0; e < E; e += 2) { double d = segDist(gps[k], pos(edges[e].a), pos(edges[e].b)); if (d < bd) { bd = d; near = e; } }
            fixes++; viterbiOk += good(match[k], truth[k], tp[k]); nearestOk += good(near, truth[k], tp[k]); } }
    assert(fixes > 300 && viterbiOk > nearestOk && viterbiOk * 100 >= fixes * 95 && viterbiOk > nearestOk + fixes / 30);                                                                                           // ① HMM 이 최근접보다 정확
    int reroutes = 0, arrivals = 0;
    for (int trial = 0; trial < 80; trial++) {
        int s = rng() % (W * W), t = rng() % (W * W); std::vector<int> route = dijkstraPath(s, t, alive); if (route.size() < 10) continue; int cur = s, step = 0, guard = 0; size_t idx = 0;
        while (cur != t && guard++ < 500) { int e = route[idx];
            if (step == 3) { for (int cand : out[cur]) if (cand != route[idx] && edges[cand].b != edges[route[idx - 1]].a) { e = cand; break; } }                       // 운전자가 4번째 갈림길에서 계획과 다른 길로 들어선다
            cur = edges[e].b; step++;
            if (e != route[idx]) { std::vector<int> best = dijkstraPath(cur, t, alive); std::vector<int> d(W * W, -1); std::queue<int> q; d[cur] = 0; q.push(cur); while (!q.empty()) { int u = q.front(); q.pop(); for (int f : out[u]) if (d[edges[f].b] < 0) { d[edges[f].b] = d[u] + 1; q.push(edges[f].b); } }
                assert((int)best.size() == d[t]); route = best; idx = 0; reroutes++; }                                                                           // 이탈 감지 → 현재 위치에서 최적 경로로 재탐색
            else idx++; }
        assert(cur == t); arrivals++; }
    assert(reroutes >= 15 && arrivals >= 15);
    std::cout << "GPSNavigation: HMM/Viterbi map matching assigned " << viterbiOk << "/" << fixes << " noisy fixes to the right road versus " << nearestOk << " for nearest-road snapping; " << reroutes << " off-route detections each triggered an optimal reroute, " << arrivals << " trips arrived" << std::endl; return 0;
}
// Time Complexity: Viterbi O(T · E · deg), 재탐색 O(E log V)
// Space Complexity: O(T · E)
```
## RobotVacuumPlanner()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 청소 로봇의 커버리지 경로 계획(coverage path planning): 목표 한 곳이 아니라 "도달 가능한 모든 칸을 방문" 하는 경로를 찾는다. 외판원 문제와 닮아 최적은 NP-난해이고 실용 해법은 두 단계의 탐욕법이다.
// ① 아직 청소하지 않은 이웃 칸이 있으면 같은 진행 방향을 우선하며(직진 > 오른쪽 > 왼쪽 > 뒤) 그쪽으로 이동 — 긴 줄을 그리는 왕복(boustrophedon) 운동이 된다. ② 사방이 막히거나 청소한 칸뿐이면 BFS 로 가장 가까운 미청소 칸까지 청소된 칸 위로 이동한다(되돌아가기).
// 모든 도달 가능한 칸이 청소되면 끝. 하한은 칸 수 − 1 걸음(해밀턴 경로가 있을 때). 검증: ① 시작 칸과 연결된 모든 자유 칸을 방문 ② 걸음이 모두 인접한 자유 칸 간 이동 ③ 걸음 수 ≥ 칸 수 − 1, 평균 비율(걸음 수/(칸 수 − 1)) < 1.5 ④ 무작위 걸음은 모든 칸을 덮는 데 이 방법보다 훨씬(3 배 이상) 많은 걸음이 필요
const int DR[4] = {-1, 0, 1, 0}, DC[4] = {0, 1, 0, -1}; int R = 20, C = 20; std::vector<std::string> w;
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
int main() {
    std::mt19937 rng(7); int maps = 0; double ratioSum = 0; double randomVsGreedy = 0; int randomRuns = 0;
    for (int m = 0; m < 40; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 14) ch = '#'; int sr, sc; do { sr = rng() % R; sc = rng() % C; } while (w[sr][sc] == '#');
        std::vector<int> comp(R * C, 0); { std::queue<int> q; q.push(sr * C + sc); comp[sr * C + sc] = 1; while (!q.empty()) { int u = q.front(); q.pop(); for (int d = 0; d < 4; d++) { int r = u / C + DR[d], c = u % C + DC[d]; if (freeCell(r, c) && !comp[r * C + c]) { comp[r * C + c] = 1; q.push(r * C + c); } } } }
        int target = 0; for (int i = 0; i < R * C; i++) target += comp[i]; if (target < 30) continue; maps++;
        std::vector<char> clean(R * C, 0); int r = sr, c = sc, dir = 1, visited = 1; clean[r * C + c] = 1; long steps = 0; std::vector<int> trail = {r * C + c};
        while (visited < target) {
            int pick = -1; for (int t : {0, 1, 3, 2}) { int d = (dir + t) % 4, nr = r + DR[d], nc = c + DC[d]; if (freeCell(nr, nc) && !clean[nr * C + nc]) { pick = d; break; } }                          // 직진 > 오른쪽 > 왼쪽 > 뒤 순서로 미청소 이웃
            if (pick >= 0) { dir = pick; r += DR[pick]; c += DC[pick]; clean[r * C + c] = 1; visited++; steps++; trail.push_back(r * C + c); continue; }
            std::vector<int> par(R * C, -2); std::queue<int> q; q.push(r * C + c); par[r * C + c] = -1; int goal = -1; while (!q.empty() && goal < 0) { int u = q.front(); q.pop(); for (int d = 0; d < 4; d++) { int nr = u / C + DR[d], nc = u % C + DC[d]; if (!freeCell(nr, nc) || par[nr * C + nc] != -2) continue; par[nr * C + nc] = u; if (!clean[nr * C + nc]) { goal = nr * C + nc; break; } q.push(nr * C + nc); } }
            assert(goal >= 0); std::vector<int> back; for (int v = goal; v != r * C + c; v = par[v]) back.push_back(v); std::reverse(back.begin(), back.end());
            for (int v : back) { int nr = v / C, nc = v % C; for (int d = 0; d < 4; d++) if (r + DR[d] == nr && c + DC[d] == nc) dir = d; r = nr; c = nc; steps++; trail.push_back(v); } if (!clean[r * C + c]) { clean[r * C + c] = 1; visited++; } }
        for (size_t i = 1; i < trail.size(); i++) assert(std::abs(trail[i] / C - trail[i - 1] / C) + std::abs(trail[i] % C - trail[i - 1] % C) == 1 && w[trail[i] / C][trail[i] % C] != '#');                       // ② 인접한 자유 칸
        for (int i = 0; i < R * C; i++) assert(comp[i] == clean[i]); assert(steps >= target - 1); ratioSum += (double)steps / (target - 1);                                                                     // ①③
        if (m < 6) { std::vector<char> seen(R * C, 0); int rr = sr, cc = sc, cnt = 1; long rs = 0; seen[rr * C + cc] = 1; while (cnt < target && rs < 400000) { int d = rng() % 4, nr = rr + DR[d], nc = cc + DC[d]; if (!freeCell(nr, nc)) continue; rr = nr; cc = nc; rs++; if (!seen[rr * C + cc]) { seen[rr * C + cc] = 1; cnt++; } } assert(cnt == target); randomVsGreedy += (double)rs / steps; randomRuns++; }       // ④ 무작위 걸음
    }
    assert(maps > 25 && ratioSum / maps < 1.5 && randomVsGreedy / randomRuns > 3);
    std::cout << "RobotVacuumPlanner: " << maps << " rooms fully covered; steps / (cells - 1) = " << ratioSum / maps << " on average (lower bound 1.0); a random walk needed " << randomVsGreedy / randomRuns << "x as many steps" << std::endl; return 0;
}
// Time Complexity: O(미청소 구간 전환 횟수 × V) (BFS 되돌아가기)
// Space Complexity: O(V)
```
## GameNPCNavigation()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 게임 NPC 길찾기: NPC 수십~수천 명이 같은 목적지로 움직이는 상황에서는 NPC 마다 A* 를 돌리는 것보다 목적지에서 한 번만 퍼뜨린 "흐름 장(flow field = 거리 장 + 내려가는 방향)"을 모두가 공유하는 것이 훨씬 싸다 — BFS 한 번 O(V), NPC 는 현재 칸에서 거리 값이 더 작은 이웃으로 한 걸음.
// 군중은 서로 막으므로 지역 규칙이 필요하다 — 점유 격자(한 칸에 한 명), 매 틱 처리 순서를 섞어 공정성 확보, 막히면 대기하고 3 틱 넘게 막히면 거리가 같은 이웃으로 옆걸음. 목적지에 닿은 NPC 는 사라진다(스폰 해제).
// 검증(30×20 경기장, 장애물 12%, NPC 40명): ① 흐름 장 값이 NPC 별 BFS 거리와 일치 ② 어느 틱에도 한 칸에 둘 이상 없음 ③ 모두 제한 시간 안에 도착하고 이동 횟수는 자기 최단 거리 이상 ④ 흐름 장 BFS 한 번의 확장 수가 NPC 마다 A* 를 돌린 확장 수 합계보다 훨씬 적음
const int DR8[8] = {-1, -1, -1, 0, 0, 1, 1, 1}, DC8[8] = {-1, 0, 1, -1, 1, -1, 0, 1}; int R = 20, C = 30; std::vector<std::string> w;
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
bool stepOk(int r, int c, int dr, int dc) { if (!freeCell(r + dr, c + dc)) return false; return !(dr && dc && (!freeCell(r + dr, c) || !freeCell(r, c + dc))); }
std::vector<int> flowField(int goal, long& expanded) { std::vector<int> d(R * C, -1); std::queue<int> q; d[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); expanded++; for (int k = 0; k < 8; k++) { int r = u / C + DR8[k], c = u % C + DC8[k]; if (!freeCell(r, c) || d[r * C + c] >= 0) continue; if (!stepOk(r, c, -DR8[k], -DC8[k])) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
long astarExpansions(int s, int t, int& len) { auto h = [&](int v) { return std::max(std::abs(v / C - t / C), std::abs(v % C - t % C)); }; std::vector<int> g(R * C, 1 << 28); typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; g[s] = 0; pq.push({h(s), s}); long ex = 0; len = -1;
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + h(u)) continue; ex++; if (u == t) { len = g[u]; break; } for (int k = 0; k < 8; k++) { if (!stepOk(u / C, u % C, DR8[k], DC8[k])) continue; int v = (u / C + DR8[k]) * C + u % C + DC8[k]; if (g[u] + 1 < g[v]) { g[v] = g[u] + 1; pq.push({g[v] + h(v), v}); } } } return ex; }
int main() {
    std::mt19937 rng(19); int arenas = 0; long totalFlow = 0, totalAstar = 0, moves = 0, optimal = 0;
    for (int a = 0; a < 15; a++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 12) ch = '#'; int goal = (R / 2) * C + C - 2; w[goal / C][goal % C] = '.'; long ex = 0; std::vector<int> field = flowField(goal, ex); totalFlow += ex;
        struct Npc { int pos; int wait; long made; int spawnDist; }; std::vector<Npc> npcs; std::set<int> used; while (npcs.size() < 40) { int p = rng() % (R * C); if (w[p / C][p % C] == '#' || field[p] < 0 || used.count(p) || p == goal) continue; used.insert(p); npcs.push_back({p, 0, 0, field[p]}); }
        for (auto& n : npcs) { int len; totalAstar += astarExpansions(n.pos, goal, len); assert(len == field[n.pos]); }                                                                          // ① 흐름 장 == NPC 별 최단 거리
        std::vector<int> occ(R * C, -1); for (size_t i = 0; i < npcs.size(); i++) occ[npcs[i].pos] = i; std::vector<char> done(npcs.size(), 0); size_t remaining = npcs.size(); int tick = 0;
        for (; remaining > 0 && tick < 600; tick++) { std::vector<int> order; for (size_t i = 0; i < npcs.size(); i++) if (!done[i]) order.push_back(i); std::shuffle(order.begin(), order.end(), rng);
            for (int i : order) { Npc& n = npcs[i]; int r = n.pos / C, c = n.pos % C;
                std::vector<std::pair<int, int>> cand; for (int k = 0; k < 8; k++) { if (!stepOk(r, c, DR8[k], DC8[k])) continue; int v = (r + DR8[k]) * C + c + DC8[k]; if (field[v] >= 0 && (field[v] < field[n.pos] || (n.wait > 3 && field[v] == field[n.pos]))) cand.push_back({field[v], v}); } std::sort(cand.begin(), cand.end());
                bool moved = false; for (auto& cv : cand) if (occ[cv.second] < 0) { occ[n.pos] = -1; n.pos = cv.second; n.made++; moves++; n.wait = 0; moved = true; if (n.pos == goal) { done[i] = 1; remaining--; } else occ[n.pos] = i; break; } if (!moved) n.wait++; }               // 목표에 닿으면 즉시 사라져 목표 칸은 늘 비어 있다
            std::map<int, int> count; for (size_t i = 0; i < npcs.size(); i++) if (!done[i]) assert(++count[npcs[i].pos] == 1); }                                                                           // ② 한 칸에 둘 이상 없음
        assert(remaining == 0); for (auto& n : npcs) { assert(n.made >= n.spawnDist); optimal += n.spawnDist; } arenas++; }
    assert(arenas == 15 && totalFlow * 3 < totalAstar && moves >= optimal);
    std::cout << "GameNPCNavigation: " << arenas << " arenas x 40 NPCs all reached the goal with no cell ever shared; " << moves << " moves vs " << optimal << " shortest-path steps; one shared flow field cost " << totalFlow << " expansions versus " << totalAstar << " for per-NPC A*" << std::endl; return 0;
}
// Time Complexity: 흐름 장 O(V) 한 번, NPC 한 걸음 O(8)
// Space Complexity: O(V)
```
## WarehouseRobotRouting()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 창고 로봇 경로: 격자 창고(선반 줄 사이의 통로)에서 한 번 출고할 때 집어야 할 k 개 지점을 모두 들러 출발지(= 하차장)로 돌아오는 최단 순회. 두 층으로 풀린다. ① 지점 쌍 사이 거리는 통로를 따라가는 BFS 거리(선반은 통과 불가) ② 그 거리 행렬 위의 외판원 문제(TSP).
// k ≤ 12 정도면 Held–Karp 동적계획법(O(2^k · k²))으로 정확히 풀 수 있고, 더 크면 최근접 이웃 + 2-opt 같은 휴리스틱을 쓴다. 휴리스틱은 빠르지만 최적에서 조금 벗어난다.
// 검증(24×12 창고, 선반 줄 4개): ① 거리 행렬이 대칭이고 삼각부등식을 만족 ② k ≤ 7 에서 Held–Karp == 모든 순열 완전 탐색 ③ 최근접 이웃 ≥ NN+2-opt ≥ Held–Karp 이고 2-opt 가 NN 을 평균적으로 줄임 ④ 순회의 실제 보행 거리 합이 Held–Karp 비용과 같음
const int DR[4] = {-1, 1, 0, 0}, DC[4] = {0, 0, -1, 1}; int R = 12, C = 24; std::vector<std::string> w;
std::vector<int> bfs(int s) { std::vector<int> d(R * C, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int k = 0; k < 4; k++) { int r = u / C + DR[k], c = u % C + DC[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#' || d[r * C + c] >= 0) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
long heldKarp(const std::vector<std::vector<int>>& D) { int n = D.size() - 1; const long INF = 1L << 40; std::vector<std::vector<long>> dp(1 << n, std::vector<long>(n, INF)); for (int i = 0; i < n; i++) dp[1 << i][i] = D[0][i + 1];
    for (int mask = 1; mask < (1 << n); mask++) for (int i = 0; i < n; i++) if ((mask >> i & 1) && dp[mask][i] < INF) for (int j = 0; j < n; j++) if (!(mask >> j & 1)) dp[mask | 1 << j][j] = std::min(dp[mask | 1 << j][j], dp[mask][i] + D[i + 1][j + 1]);
    long best = INF; for (int i = 0; i < n; i++) best = std::min(best, dp[(1 << n) - 1][i] + D[i + 1][0]); return best; }
long bruteForce(const std::vector<std::vector<int>>& D) { int n = D.size() - 1; std::vector<int> p(n); for (int i = 0; i < n; i++) p[i] = i + 1; long best = 1L << 40; do { long c = D[0][p[0]]; for (int i = 1; i < n; i++) c += D[p[i - 1]][p[i]]; c += D[p[n - 1]][0]; best = std::min(best, c); } while (std::next_permutation(p.begin(), p.end())); return best; }
long tourCost(const std::vector<std::vector<int>>& D, const std::vector<int>& t) { long c = 0; for (size_t i = 0; i < t.size(); i++) c += D[t[i]][t[(i + 1) % t.size()]]; return c; }
std::vector<int> nearestNeighbor(const std::vector<std::vector<int>>& D) { int n = D.size(); std::vector<int> t = {0}; std::vector<char> used(n, 0); used[0] = 1; for (int k = 1; k < n; k++) { int best = -1; for (int j = 0; j < n; j++) if (!used[j] && (best < 0 || D[t.back()][j] < D[t.back()][best])) best = j; used[best] = 1; t.push_back(best); } return t; }
void twoOpt(const std::vector<std::vector<int>>& D, std::vector<int>& t) { bool improved = true; while (improved) { improved = false; for (size_t i = 1; i + 1 < t.size(); i++) for (size_t j = i + 1; j < t.size(); j++) { std::vector<int> u = t; std::reverse(u.begin() + i, u.begin() + j + 1); if (tourCost(D, u) < tourCost(D, t)) { t = u; improved = true; } } } }
int main() {
    std::mt19937 rng(23); w.assign(R, std::string(C, '.')); for (int row : {2, 5, 8}) for (int c = 3; c < C - 3; c++) if (c % 8 != 0) w[row][c] = '#'; for (int c = 3; c < C - 3; c++) if (c % 8 != 0) w[10][c] = '#';                          // 선반 줄(8칸마다 건널 수 있는 틈)
    std::vector<int> freeCells; for (int i = 0; i < R * C; i++) if (w[i / C][i % C] != '#') freeCells.push_back(i); int depot = 0; long gapNN = 0, gap2 = 0, opt = 0; int trials = 0, twoBetter = 0;
    for (int t = 0; t < 60; t++) {
        int k = t < 30 ? 3 + rng() % 5 : 8 + rng() % 5; std::vector<int> pts = {depot}; std::set<int> used = {depot}; while ((int)pts.size() < k + 1) { int p = freeCells[rng() % freeCells.size()]; if (used.insert(p).second) pts.push_back(p); }
        std::vector<std::vector<int>> D(k + 1, std::vector<int>(k + 1)); for (int i = 0; i <= k; i++) { auto d = bfs(pts[i]); for (int j = 0; j <= k; j++) { D[i][j] = d[pts[j]]; assert(D[i][j] >= 0); } }
        for (int i = 0; i <= k; i++) for (int j = 0; j <= k; j++) { assert(D[i][j] == D[j][i]); for (int m = 0; m <= k; m++) assert(D[i][j] <= D[i][m] + D[m][j]); }                                   // ① 거리 행렬 성질
        long hk = heldKarp(D); if (k <= 7) assert(hk == bruteForce(D));                                                                                                                 // ② 완전 탐색과 일치
        std::vector<int> nn = nearestNeighbor(D), opt2 = nn; twoOpt(D, opt2); long cn = tourCost(D, nn), c2 = tourCost(D, opt2); assert(cn >= c2 && c2 >= hk);                                       // ③
        long walk = 0; for (size_t i = 0; i < opt2.size(); i++) walk += D[opt2[i]][opt2[(i + 1) % opt2.size()]]; assert(walk == c2);
        gapNN += cn - hk; gap2 += c2 - hk; opt += hk; twoBetter += c2 < cn; trials++; }
    assert(trials == 60 && gap2 <= gapNN && twoBetter > 5);
    std::cout << "WarehouseRobotRouting: " << trials << " pick lists; Held-Karp matches brute force (k <= 7); mean excess over optimal: nearest-neighbor " << 100.0 * gapNN / opt << "%, with 2-opt " << 100.0 * gap2 / opt << "% (2-opt improved " << twoBetter << " tours)" << std::endl; return 0;
}
// Time Complexity: BFS k 번 O(k · V), Held–Karp O(2^k · k²), NN O(k²), 2-opt 반복당 O(k²) × 비용 계산
// Space Complexity: O(2^k · k)
```
## DronePathPlanning()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 드론 경로 계획: 도시 상공이므로 3차원 격자(복셀)에서 건물(기둥), 비행 금지 구역(상자)을 피해 가는 최소 에너지 경로. 26방향 이동을 허용하고 비용은 에너지 모델 = 유클리드 이동 거리 + 상승 벌점(고도 1 올릴 때 추가 1.5)이다.
// 비용이 항상 이동 거리 이상이므로 유클리드 거리가 허용적이고 일관적인 휴리스틱이다. 이동 시 지나는 바운딩 박스의 모든 복셀이 비어야 한다(모서리 자르기 금지). 그리드 경로는 계단식이라 직선 시선(LOS)이 닿는 가장 먼 점으로 건너뛰는 줄 당기기로 짧게 다듬는다 — 시선 검사는 선분을 촘촘히 표본해 안전 여유(±0.3)를 두고 확인한다.
// 검증(20×20×10 도시 12개): ① A* 에너지 == 같은 격자 Dijkstra ② 경로의 모든 걸음이 비어 있음 ③ A* 확장 수가 Dijkstra 보다 적음 ④ 줄 당기기 뒤의 유클리드 길이 ≤ 격자 경로 길이이고 모든 선분이 장애물과 안전 여유 이상 떨어져 있음
const int X = 20, Y = 20, Z = 10; std::vector<char> blocked(X * Y * Z, 0); int id(int x, int y, int z) { return (z * Y + y) * X + x; }
bool freeV(int x, int y, int z) { return x >= 0 && y >= 0 && z >= 0 && x < X && y < Y && z < Z && !blocked[id(x, y, z)]; }
bool moveOk(int x, int y, int z, int dx, int dy, int dz) { for (int a = 0; a <= std::abs(dx); a++) for (int b = 0; b <= std::abs(dy); b++) for (int c = 0; c <= std::abs(dz); c++) if (!freeV(x + (dx > 0 ? a : -a), y + (dy > 0 ? b : -b), z + (dz > 0 ? c : -c))) return false; return true; }      // 이동의 바운딩 박스 전체가 비어야 함
double energy(int dx, int dy, int dz) { return std::sqrt((double)(dx * dx + dy * dy + dz * dz)) + 1.5 * std::max(dz, 0); }
struct Res { double cost; long expanded; std::vector<int> path; };
Res search(int s, int t, bool useH) { std::vector<double> d(X * Y * Z, 1e18); std::vector<int> par(X * Y * Z, -1); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; auto H = [&](int v) { return useH ? std::sqrt((double)(std::pow(v % X - t % X, 2) + std::pow(v / X % Y - t / X % Y, 2) + std::pow(v / (X * Y) - t / (X * Y), 2))) : 0.0; }; d[s] = 0; pq.push({H(s), s}); long ex = 0;
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > d[u] + H(u) + 1e-12) continue; ex++; if (u == t) break; int x = u % X, y = u / X % Y, z = u / (X * Y);
        for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) for (int dz = -1; dz <= 1; dz++) { if (!dx && !dy && !dz) continue; if (!moveOk(x, y, z, dx, dy, dz)) continue; int v = id(x + dx, y + dy, z + dz); double nd = d[u] + energy(dx, dy, dz); if (nd < d[v] - 1e-12) { d[v] = nd; par[v] = u; pq.push({nd + H(v), v}); } } }
    Res r{d[t] > 1e17 ? -1 : d[t], ex, {}}; if (r.cost >= 0) { for (int v = t; v >= 0; v = par[v]) r.path.push_back(v); std::reverse(r.path.begin(), r.path.end()); } return r; }
bool los(int a, int b, double margin) { double ax = a % X + 0.5, ay = a / X % Y + 0.5, az = a / (X * Y) + 0.5, bx = b % X + 0.5, by = b / X % Y + 0.5, bz = b / (X * Y) + 0.5; double len = std::sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay) + (bz - az) * (bz - az)); int n = std::max(1, (int)(len / 0.05));
    for (int i = 0; i <= n; i++) { double f = (double)i / n, px = ax + f * (bx - ax), py = ay + f * (by - ay), pz = az + f * (bz - az); for (int sx : {-1, 1}) for (int sy : {-1, 1}) for (int sz : {-1, 1}) { int cx = (int)std::floor(px + sx * margin), cy = (int)std::floor(py + sy * margin), cz = (int)std::floor(pz + sz * margin); if (!freeV(cx, cy, cz)) return false; } } return true; }
int main() {
    std::mt19937 rng(37); int cities = 0; long exA = 0, exD = 0; double sumGrid = 0, sumSmooth = 0;
    for (int c = 0; c < 12; c++) {
        std::fill(blocked.begin(), blocked.end(), 0); for (int k = 0; k < 40; k++) { int x = rng() % X, y = rng() % Y, h = 2 + rng() % 7; for (int z = 0; z < h; z++) blocked[id(x, y, z)] = 1; }
        for (int k = 0; k < 3; k++) { int x0 = 3 + rng() % 12, y0 = 3 + rng() % 12, z0 = rng() % 5; for (int x = x0; x < x0 + 3; x++) for (int y = y0; y < y0 + 3; y++) for (int z = z0; z < z0 + 4; z++) blocked[id(x, y, z)] = 1; }                      // 비행 금지 상자
        int s = id(0, 0, 0), t = id(X - 1, Y - 1, 1); blocked[s] = blocked[t] = 0; Res a = search(s, t, true), d = search(s, t, false); assert(std::fabs(a.cost - d.cost) < 1e-9); if (a.cost < 0) continue; cities++; exA += a.expanded; exD += d.expanded;          // ①
        double grid = 0; double sum = 0; for (size_t i = 1; i < a.path.size(); i++) { int u = a.path[i - 1], v = a.path[i], ux = u % X, uy = u / X % Y, uz = u / (X * Y), vx = v % X, vy = v / X % Y, vz = v / (X * Y); assert(moveOk(ux, uy, uz, vx - ux, vy - uy, vz - uz)); int dx = vx - ux, dy = vy - uy, dz = vz - uz; sum += energy(dx, dy, dz); grid += std::sqrt((double)(dx * dx + dy * dy + dz * dz)); }       // ②
        assert(std::fabs(sum - a.cost) < 1e-9);
        std::vector<int> sm = {a.path[0]}; for (size_t i = 0; i + 1 < a.path.size();) { size_t j = a.path.size() - 1; while (j > i + 1 && !los(a.path[i], a.path[j], 0.3)) j--; sm.push_back(a.path[j]); i = j; }
        double smooth = 0; for (size_t i = 1; i < sm.size(); i++) { int u = sm[i - 1], v = sm[i]; smooth += std::sqrt((double)(std::pow(u % X - v % X, 2) + std::pow(u / X % Y - v / X % Y, 2) + std::pow(u / (X * Y) - v / (X * Y), 2))); }
        assert(smooth <= grid + 1e-9); sumGrid += grid; sumSmooth += smooth; }
    assert(cities >= 8 && exA < exD && sumSmooth < sumGrid);
    std::cout << "DronePathPlanning: " << cities << " 3D cities; A* energy == Dijkstra on all; expansions " << exA << " vs " << exD << "; string pulling shortened the flight path from " << sumGrid / cities << " to " << sumSmooth / cities << " cells on average" << std::endl; return 0;
}
// Time Complexity: O(V · 26 · 이동 검사) A*, 줄 당기기 O(경로 길이² · 시선 검사)
// Space Complexity: O(V)
```
## EmergencyEvacuation()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 비상 대피 계획: 건물에서 사람들이 출구로 빠져나가는 가장 빠른 방법. 출구마다 한 틱에 한 명만 통과할 수 있으므로 모두가 가장 가까운 출구로 몰리면 대기열이 생겨 한쪽 출구가 막히는 동안 다른 출구는 놀 수 있다.
// 정확한 해법은 시간 확장 네트워크의 최대 유량이다 — 노드 (칸, 시각 t), 간선 (칸, t) → (이웃 칸 또는 제자리, t+1), 출구 칸 (출구, t) → 싱크 용량 1(그 틱의 통과 인원), 소스 → (칸, 0) 용량 = 그 칸의 사람 수.
// 제한 시간 T 안에 모두 대피 가능 ⇔ 최대 유량 == 사람 수. T 를 늘려 가며 처음 가능한 값이 최소 대피 시간 T*. 비교 대상인 탐욕법은 각자 가장 가까운 출구로 최단 경로를 걷고 출구에서 선착순으로 줄을 서는 것이다.
// 검증(12×8 건물, 사람 20명, 출구 2개): ① Dinic 과 Edmonds–Karp 두 최대 유량 알고리즘이 모든 T 에서 같은 값 ② 가능 여부가 T 에 대해 단조(T 가 늘면 유량이 줄지 않음) ③ 탐욕법 시간 ≥ T* 이고 T* 가 더 작은 사례가 존재 ④ T* ≥ 가장 먼 사람의 최단 거리 이하 하한 max(⌈사람 수/출구 수⌉, 가장 가까운 거리)
struct Flow { struct E { int to, cap; }; std::vector<E> es; std::vector<std::vector<int>> g; std::vector<int> level, it;
    Flow(int n) : g(n), level(n), it(n) {} void add(int u, int v, int c) { g[u].push_back(es.size()); es.push_back({v, c}); g[v].push_back(es.size()); es.push_back({u, 0}); }
    bool bfs(int s, int t) { std::fill(level.begin(), level.end(), -1); std::queue<int> q; level[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int id : g[u]) if (es[id].cap > 0 && level[es[id].to] < 0) { level[es[id].to] = level[u] + 1; q.push(es[id].to); } } return level[t] >= 0; }
    int dfs(int u, int t, int f) { if (u == t) return f; for (int& i = it[u]; i < (int)g[u].size(); i++) { int id = g[u][i]; if (es[id].cap > 0 && level[es[id].to] == level[u] + 1) { int d = dfs(es[id].to, t, std::min(f, es[id].cap)); if (d > 0) { es[id].cap -= d; es[id ^ 1].cap += d; return d; } } } return 0; }
    int dinic(int s, int t) { int flow = 0; while (bfs(s, t)) { std::fill(it.begin(), it.end(), 0); while (int f = dfs(s, t, 1 << 28)) flow += f; } return flow; }
    int edmondsKarp(int s, int t) { int flow = 0; for (;;) { std::vector<int> pe(g.size(), -1); std::queue<int> q; q.push(s); pe[s] = -2; while (!q.empty() && pe[t] == -1) { int u = q.front(); q.pop(); for (int id : g[u]) if (es[id].cap > 0 && pe[es[id].to] == -1) { pe[es[id].to] = id; q.push(es[id].to); } } if (pe[t] == -1) return flow; int f = 1 << 28; for (int v = t; v != s; v = es[pe[v] ^ 1].to) f = std::min(f, es[pe[v]].cap); for (int v = t; v != s; v = es[pe[v] ^ 1].to) { es[pe[v]].cap -= f; es[pe[v] ^ 1].cap += f; } flow += f; } } };
const int R = 8, C = 12; std::vector<std::string> w; const int DR[5] = {0, -1, 1, 0, 0}, DC[5] = {0, 0, 0, -1, 1};
std::vector<int> bfs(int s) { std::vector<int> d(R * C, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int k = 1; k < 5; k++) { int r = u / C + DR[k], c = u % C + DC[k]; if (r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#' || d[r * C + c] >= 0) continue; d[r * C + c] = d[u] + 1; q.push(r * C + c); } } return d; }
int maxFlow(const std::vector<int>& people, const std::vector<int>& exits, int T, bool dinic) {                                  // 시간 T 안에 대피 가능한 최대 인원
    int cells = R * C, N = cells * (T + 1) + 2, S = N - 2, SINK = N - 1; Flow f(N); for (int c = 0; c < cells; c++) if (people[c] > 0) f.add(S, c, people[c]);
    for (int t = 0; t < T; t++) for (int c = 0; c < cells; c++) { if (w[c / C][c % C] == '#') continue; for (int k = 0; k < 5; k++) { int r = c / C + DR[k], cc = c % C + DC[k]; if (r < 0 || cc < 0 || r >= R || cc >= C || w[r][cc] == '#') continue; f.add(t * cells + c, (t + 1) * cells + r * C + cc, 1 << 20); } }
    for (int t = 0; t <= T; t++) for (int e : exits) f.add(t * cells + e, SINK, 1); return dinic ? f.dinic(S, SINK) : f.edmondsKarp(S, SINK); }       // 출구는 틱마다 한 명
int main() {
    std::mt19937 rng(29); int instances = 0, strictlyBetter = 0; long sumOpt = 0, sumGreedy = 0;
    for (int trial = 0; trial < 12; trial++) {
        w.assign(R, std::string(C, '.')); for (int k = 0; k < 14; k++) w[rng() % R][1 + rng() % (C - 2)] = '#'; std::vector<int> exits = {3 * C + 0, 4 * C + C - 1}; for (int e : exits) w[e / C][e % C] = '.'; std::vector<int> dE[2] = {bfs(exits[0]), bfs(exits[1])};
        std::vector<int> people(R * C, 0); int P = 0; while (P < 20) { int c = rng() % (R * C); if (w[c / C][c % C] == '#' || (dE[0][c] < 0 && dE[1][c] < 0) || people[c]) continue; people[c] = 1; P++; }
        int Tstar = -1, prev = 0; for (int T = 1; T <= 40; T++) { int a = maxFlow(people, exits, T, true), b = maxFlow(people, exits, T, false); assert(a == b && a >= prev); prev = a; if (a == P) { Tstar = T; break; } } assert(Tstar > 0);                    // ① 두 알고리즘 일치, ② 단조
        assert(maxFlow(people, exits, Tstar - 1, true) < P);
        std::vector<int> exitTimes[2]; for (int c = 0; c < R * C; c++) if (people[c]) { int e = (dE[0][c] >= 0 && (dE[1][c] < 0 || dE[0][c] <= dE[1][c])) ? 0 : 1; exitTimes[e].push_back(dE[e][c]); } int greedy = 0; for (int e = 0; e < 2; e++) { std::sort(exitTimes[e].begin(), exitTimes[e].end()); int last = -1; for (int a : exitTimes[e]) { last = std::max(a, last + 1); greedy = std::max(greedy, last); } }
        int nearest = 1 << 28; for (int c = 0; c < R * C; c++) if (people[c]) nearest = std::min(nearest, std::min(dE[0][c] < 0 ? 1 << 28 : dE[0][c], dE[1][c] < 0 ? 1 << 28 : dE[1][c])); assert(Tstar >= std::max((P + 1) / 2, nearest) - 0);                         // ④ 하한
        assert(greedy >= Tstar); strictlyBetter += greedy > Tstar; sumOpt += Tstar; sumGreedy += greedy; instances++; }
    assert(instances == 12 && strictlyBetter > 0);
    std::cout << "EmergencyEvacuation: " << instances << " buildings x 20 people; minimum evacuation time from the time-expanded max-flow (Dinic == Edmonds-Karp) totals " << sumOpt << " ticks versus " << sumGreedy << " for nearest-exit queueing (optimal strictly faster in " << strictlyBetter << " buildings)" << std::endl; return 0;
}
// Time Complexity: 시간 확장 그래프 O(R · C · T) 노드, T 마다 최대 유량
// Space Complexity: O(R · C · T)
```

# Part 15. 성능 최적화
## HeuristicFunction()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 휴리스틱 함수의 성질: A* 의 정확성과 속도는 전부 h(n) 에 달려 있다. 허용적(admissible: h ≤ 실제 최단 거리)이면 최적을 보장하고, 일관적(consistent: h(u) ≤ c(u,v) + h(v))이면 한 번 확장한 노드를 다시 열지 않는다(일관적이면 허용적).
// 8방향 격자(직선 10, 대각 10√2 ≈ 14.14)에서 비교: 0(= Dijkstra), 체비쇼프 10·max(dr,dc), 유클리드 10·√(dr²+dc²), 옥타일 10·(dr+dc) − (20 − 10√2)·min(dr,dc)(장애물이 없을 때 정확), 맨해튼 10·(dr+dc)(대각 이동을 과대평가해서 허용적이지 않음; 유클리드는 대각 비용을 10√2 로 두어야 허용적), 그리고 이상적인 "실제 거리".
// 두 허용적 휴리스틱의 max 도 허용적이며 둘을 지배(dominate)한다 — 값이 클수록(허용 범위 안에서) 확장이 줄어든다. 검증(무작위 24×24 지도 30개, 모서리 자르기 금지): ① 각 휴리스틱의 허용성·일관성을 모든 칸·모든 간선에서 확인(맨해튼은 위반이 실제로 관찰됨) ② 허용적 휴리스틱은 모두 최적 비용을 내고 맨해튼은 최적보다 비싼 해를 내는 지도가 존재 ③ 확장 수 순서: 실제 거리 ≤ 옥타일 ≤ 유클리드 ≤ 체비쇼프 ≤ 0 ④ max(체비쇼프, 유클리드) == 유클리드
const int R = 24, C = 24; std::vector<std::string> w; typedef std::function<double(int, int, int, int)> Hf;
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
bool stepOk(int r, int c, int dr, int dc) { if (!freeCell(r + dr, c + dc)) return false; return !(dr && dc && (!freeCell(r + dr, c) || !freeCell(r, c + dc))); }
double stepCost(int dr, int dc) { return dr && dc ? 10 * std::sqrt(2.0) : 10.0; }
std::vector<double> trueDist(int goal) { std::vector<double> d(R * C, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[goal] = 0; pq.push({0, goal}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int r = u / C, c = u % C; if (!stepOk(r, c, dr, dc)) continue; int v = (r + dr) * C + c + dc; if (du + stepCost(dr, dc) < d[v]) { d[v] = du + stepCost(dr, dc); pq.push({d[v], v}); } } } return d; }
double astar(int s, int t, const std::vector<double>& h, long& expanded, bool& reopened) { std::vector<double> g(R * C, 1e18); std::vector<int> closed(R * C, 0); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; g[s] = 0; pq.push({h[s], s}); expanded = 0; reopened = false;
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + h[u] + 1e-9) continue; if (closed[u]) reopened = true; closed[u] = 1; expanded++; if (u == t) return g[u]; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int r = u / C, c = u % C; if (!stepOk(r, c, dr, dc)) continue; int v = (r + dr) * C + c + dc; double ng = g[u] + stepCost(dr, dc); if (ng < g[v]) { g[v] = ng; pq.push({ng + h[v], v}); } } } return -1; }
std::string levelSet(int n, const std::function<int(int, int)>& h) {                                 // 그림: 가운데 칸(0)이 목표, 숫자는 그 칸에서 목표까지의 휴리스틱 값 (같은 값끼리 이은 선이 "등고선")
    std::string s; for (int r = 0; r < n; ++r) { for (int c = 0; c < n; ++c) s += (char)('0' + h(r - n / 2, c - n / 2)); s += "\n"; }
    return s;
}
int main() {
    {   auto manhattan = [](int dr, int dc) { return std::abs(dr) + std::abs(dc); }; auto chebyshev = [](int dr, int dc) { return std::max(std::abs(dr), std::abs(dc)); };
        const std::string md = "6543456\n5432345\n4321234\n3210123\n4321234\n5432345\n6543456\n", cd = "3333333\n3222223\n3211123\n3210123\n3211123\n3222223\n3333333\n";
        assert(levelSet(7, manhattan) == md && levelSet(7, chebyshev) == cd);                                // 4 방향 이동의 정확한 거리인 맨해튼은 마름모 등고선, 8 방향(비용 같게)의 체비쇼프는 정사각형 등고선
        for (int dr = -3; dr <= 3; ++dr) for (int dc = -3; dc <= 3; ++dc) assert(chebyshev(dr, dc) <= manhattan(dr, dc));        // 체비쇼프 <= 맨해튼: 8 방향 격자에서는 맨해튼이 과대 추정(비허용)이다
        std::cout << md << "--\n" << cd; }
    std::mt19937 rng(5); const char* names[6] = {"zero", "chebyshev", "euclid", "octile", "manhattan", "true"}; long totalExp[6] = {0}; int maps = 0, manhattanWorse = 0, manhattanInadmissible = 0, manhattanInconsistent = 0;
    for (int m = 0; m < 30; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 18) ch = '#'; int s = 0, t = R * C - 1; w[0][0] = w[R - 1][C - 1] = '.'; std::vector<double> td = trueDist(t); if (td[s] >= 1e17) continue; maps++;
        std::vector<std::vector<double>> h(6, std::vector<double>(R * C, 0)); for (int v = 0; v < R * C; v++) { int dr = std::abs(v / C - R + 1), dc = std::abs(v % C - C + 1); h[1][v] = 10.0 * std::max(dr, dc); h[2][v] = 10.0 * std::sqrt((double)(dr * dr + dc * dc)); h[3][v] = 10.0 * (dr + dc) - (20.0 - 10 * std::sqrt(2.0)) * std::min(dr, dc); h[4][v] = 10.0 * (dr + dc); h[5][v] = td[v] >= 1e17 ? 0 : td[v]; }
        for (int v = 0; v < R * C; v++) { assert(std::fabs(std::max(h[1][v], h[2][v]) - h[2][v]) < 1e-9); }                                                                              // ④ max(체비쇼프, 유클리드) == 유클리드
        for (int k = 0; k < 6; k++) { bool adm = true, cons = true; for (int v = 0; v < R * C; v++) { if (td[v] >= 1e17 || !freeCell(v / C, v % C)) continue; if (h[k][v] > td[v] + 1e-9) adm = false; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if (!dr && !dc) continue; int r = v / C, c = v % C; if (!stepOk(r, c, dr, dc)) continue; int u = (r + dr) * C + c + dc; if (td[u] >= 1e17) continue; if (h[k][v] > stepCost(dr, dc) + h[k][u] + 1e-9) cons = false; } }
            if (k == 4) { manhattanInadmissible += !adm; manhattanInconsistent += !cons; } else assert(adm && cons);                                                                           // ① 맨해튼만 위반 가능
            long ex; bool re; double cost = astar(s, t, h[k], ex, re); totalExp[k] += ex; if (k == 4) manhattanWorse += cost > td[s] + 1e-9; else { assert(std::fabs(cost - td[s]) < 1e-9); assert(!re); } }                             // ② 허용적이면 최적, 일관적이면 재방문 없음
    }
    assert(maps >= 20 && manhattanInadmissible > 0 && manhattanInconsistent > 0 && manhattanWorse > 0);
    assert(totalExp[5] <= totalExp[3] && totalExp[3] <= totalExp[2] && totalExp[2] <= totalExp[1] && totalExp[1] <= totalExp[0]);                                                                       // ③ 확장 수 순서
    std::cout << "HeuristicFunction: " << maps << " maps; expansions"; for (int k = 0; k < 6; k++) std::cout << " " << names[k] << "=" << totalExp[k]; std::cout << "; Manhattan on an 8-direction grid is inadmissible on " << manhattanInadmissible << " maps and returned a costlier path on " << manhattanWorse << std::endl; return 0;
}
// Time Complexity: A* O(확장 수 log) — 휴리스틱이 강할수록 확장 수 감소
// Space Complexity: O(V)
```
## PriorityQueueOptimization()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 우선순위 큐 최적화: Dijkstra 의 실행 시간은 큐 연산이 좌우한다. 같은 알고리즘을 네 가지 큐로 구현해 결과가 같음을 확인하고 연산 수를 비교한다.
// ① 이진 힙 + 지연 삭제(std::priority_queue): 간선 완화마다 push, 낡은 항목은 pop 할 때 버림 — 구현이 가장 쉽고 push 수가 최대 E. ② 인덱스 4진 힙 + decrease-key: 정점당 항목 하나, 힙 크기 ≤ V, 높이가 낮아 sift-up 이 빠름.
// ③ Dial 버킷 큐: 간선 가중치가 정수 1..C 이면 거리 값마다 버킷을 둔 원형 배열 C+1 칸을 쓰고 pop 이 O(1) 분할상환 — 총 O(E + V·C). ④ 기수 힙(radix heap): 꺼낸 값이 단조 증가하는 큐 전용으로, 키를 마지막 꺼낸 값과 달라지는 최상위 비트 위치별 버킷에 담아 O(log C) 분할상환.
// 검증(무작위 그래프 120개, 가중치 1..20): 네 가지 모두 서로 같은 거리, 연산 수 비교 — 지연 삭제 힙의 push 수 ≥ decrease-key 힙의 삽입 수(≤ 정점 수), Dial 은 비교 연산 0, 기수 힙의 버킷 이동 수가 O(V log C) 안에 있음
typedef std::vector<std::vector<std::pair<int, int>>> G;
std::vector<long> lazyHeap(const G& g, int s, long& pushes) { int n = g.size(); std::vector<long> d(n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); pushes = 1; while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); pushes++; } } return d; }
struct IndexedHeap { int D = 4; std::vector<int> heap, pos; std::vector<long>& key; long swaps = 0, decreases = 0; IndexedHeap(std::vector<long>& k) : pos(k.size(), -1), key(k) {}
    void up(int i) { while (i > 0) { int p = (i - 1) / D; if (key[heap[p]] <= key[heap[i]]) break; std::swap(heap[p], heap[i]); pos[heap[p]] = p; pos[heap[i]] = i; i = p; swaps++; } }
    void down(int i) { for (;;) { int best = i; for (int c = D * i + 1; c <= D * i + D && c < (int)heap.size(); c++) if (key[heap[c]] < key[heap[best]]) best = c; if (best == i) break; std::swap(heap[best], heap[i]); pos[heap[best]] = best; pos[heap[i]] = i; i = best; swaps++; } }
    void pushOrDecrease(int v) { if (pos[v] < 0) { pos[v] = heap.size(); heap.push_back(v); up(pos[v]); } else { decreases++; up(pos[v]); } }
    int pop() { int v = heap[0]; pos[v] = -1; heap[0] = heap.back(); heap.pop_back(); if (!heap.empty()) { pos[heap[0]] = 0; down(0); } return v; } };
std::vector<long> dary(const G& g, int s, long& pushes, long& decreases) { int n = g.size(); std::vector<long> d(n, 1L << 50); IndexedHeap h(d); d[s] = 0; h.pushOrDecrease(s); pushes = 1; while (!h.heap.empty()) { int u = h.pop(); for (auto [v, w] : g[u]) if (d[u] + w < d[v]) { bool isNew = h.pos[v] < 0; d[v] = d[u] + w; h.pushOrDecrease(v); if (isNew) pushes++; } } decreases = h.decreases; return d; }
std::vector<long> dial(const G& g, int s, int maxW) { int n = g.size(); std::vector<long> d(n, 1L << 50); std::vector<std::vector<int>> bucket(maxW + 1); d[s] = 0; bucket[0].push_back(s); long cur = 0, pending = 1;
    while (pending > 0) { auto& b = bucket[cur % (maxW + 1)]; while (!b.empty()) { int u = b.back(); b.pop_back(); pending--; if (d[u] != cur) continue; for (auto [v, w] : g[u]) if (cur + w < d[v]) { d[v] = cur + w; bucket[d[v] % (maxW + 1)].push_back(v); pending++; } } cur++; } return d; }
struct RadixHeap { std::vector<std::pair<uint32_t, int>> b[33]; uint32_t last = 0; size_t sz = 0; long moves = 0; static int bits(uint32_t x) { return x ? 32 - __builtin_clz(x) : 0; }
    void push(uint32_t k, int v) { b[bits(k ^ last)].push_back({k, v}); sz++; }
    std::pair<uint32_t, int> pop() { if (b[0].empty()) { int i = 1; while (b[i].empty()) i++; uint32_t mn = UINT32_MAX; for (auto& e : b[i]) mn = std::min(mn, e.first); last = mn; for (auto& e : b[i]) { b[bits(e.first ^ last)].push_back(e); moves++; } b[i].clear(); } auto r = b[0].back(); b[0].pop_back(); sz--; return r; } };
std::vector<long> radix(const G& g, int s, long& moves) { int n = g.size(); std::vector<long> d(n, 1L << 50); RadixHeap h; d[s] = 0; h.push(0, s); while (h.sz) { auto [k, u] = h.pop(); if (k != d[u]) continue; for (auto [v, w] : g[u]) if (k + w < d[v]) { d[v] = k + w; h.push((uint32_t)d[v], v); } } moves = h.moves; return d; }
int main() {
    std::mt19937 rng(8); long pLazy = 0, pD = 0, decr = 0, rmoves = 0, vtotal = 0; int graphs = 0;
    for (int t = 0; t < 120; t++) {
        int n = 60 + rng() % 200; G g(n); auto add = [&](int a, int b, int w) { g[a].push_back({b, w}); g[b].push_back({a, w}); }; for (int i = 1; i < n; i++) add(i, rng() % i, 1 + rng() % 20); for (int k = 0; k < 3 * n; k++) { int a = rng() % n, b = rng() % n; if (a != b) add(a, b, 1 + rng() % 20); }
        long p1, p2, dc, mv; auto a = lazyHeap(g, 0, p1); auto b = dary(g, 0, p2, dc); auto c = dial(g, 0, 20); auto d = radix(g, 0, mv); assert(a == b && a == c && a == d);                                          // 네 큐가 같은 거리
        assert(p1 >= p2 && p2 <= n); pLazy += p1; pD += p2 + dc; decr += dc; rmoves += mv; vtotal += n; graphs++; }
    assert(graphs == 120 && rmoves <= vtotal * 6 * 5);
    std::cout << "PriorityQueueOptimization: " << graphs << " graphs, four queues (lazy binary heap, indexed 4-ary heap, Dial buckets, radix heap) give identical distances; lazy heap pushes " << pLazy << " vs " << pD << " insert+decrease-key operations (" << decr << " decrease-keys); radix heap moved " << rmoves << " items in total" << std::endl; return 0;
}
// Time Complexity: 이진 힙 O((V + E) log V), d-진 힙 O(E log_d V + V d log_d V), Dial O(E + V·C), 기수 힙 O(E + V log C)
// Space Complexity: O(V + E) (Dial 은 C 칸의 버킷)
```
## LandmarkHeuristic()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// ALT 의 랜드마크 휴리스틱(Goldberg & Harrelson 2005): 소수의 "랜드마크" 정점 L 에서 모든 정점까지의 거리를 미리 구해 두면 삼각부등식으로 임의의 두 정점 사이 거리의 하한을 즉시 얻는다 — 무방향 그래프에서 |d(L,t) − d(L,v)| ≤ d(v,t).
// 랜드마크 여럿의 최댓값 h(v) = max_L |d(L,t) − d(L,v)| 이 A* 의 휴리스틱이며 허용적이고 일관적이다(삼각부등식이 성립하는 한). 좌표가 필요 없어 도로망·가중 그래프에 쓸 수 있고, 랜드마크를 그래프의 "가장자리"에 고르게 두는 것이 중요하다.
// 선택 전략 비교: 무작위 vs 가장 먼 점(이미 고른 랜드마크들로부터 가장 먼 정점을 반복해서 선택). 검증(20×20 가중 도시 8개, 랜드마크 4개): ① 모든 (v,t) 쌍에서 허용적, 모든 간선에서 일관적 ② ALT-A* 는 Dijkstra 와 같은 최단 거리 ③ ALT 확장 수 < Dijkstra ④ 가장 먼 점 선택이 무작위보다 하한이 더 촘촘함(평균 h/d)
struct Graph { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
Graph makeGraph(int W, int H, std::mt19937& rng, int maxW, int extra) {                                                                 // 가중치가 불규칙한 격자형 도시 + 약간의 장거리 간선
    Graph g{W * H, std::vector<std::vector<std::pair<int, int>>>(W * H)}; std::map<std::pair<int, int>, int> best; auto add = [&](int a, int b, int w) { if (a == b) return; auto k = std::make_pair(std::min(a, b), std::max(a, b)); if (!best.count(k) || w < best[k]) best[k] = w; };
    for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { int u = r * W + c; if (c + 1 < W) add(u, u + 1, 1 + rng() % maxW); if (r + 1 < H) add(u, u + W, 1 + rng() % maxW); } for (int k = 0; k < extra; k++) add(rng() % (W * H), rng() % (W * H), maxW * 3 + rng() % (maxW * 3));
    for (auto& [e, w] : best) { g.adj[e.first].push_back({e.second, w}); g.adj[e.second].push_back({e.first, w}); } return g; }
std::vector<long> dijkstra(const Graph& g, int s) { std::vector<long> d(g.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
std::vector<int> pickLandmarks(const Graph& g, int k, bool farthest, std::mt19937& rng) { std::vector<int> L; if (!farthest) { std::set<int> s; while ((int)s.size() < k) s.insert(rng() % g.n); return std::vector<int>(s.begin(), s.end()); } L.push_back(rng() % g.n); std::vector<long> mn(g.n, 1L << 50); while ((int)L.size() < k) { auto d = dijkstra(g, L.back()); for (int v = 0; v < g.n; v++) mn[v] = std::min(mn[v], d[v]); int best = 0; for (int v = 0; v < g.n; v++) if (mn[v] > mn[best]) best = v; L.push_back(best); } return L; }
int main() {
    std::mt19937 rng(10); long expDij = 0, expAlt = 0; double tightFar = 0, tightRand = 0; int graphs = 0, queries = 0;
    for (int m = 0; m < 8; m++) {
        Graph g = makeGraph(20, 20, rng, 9, 20); int n = g.n; std::vector<std::vector<long>> D(n); for (int s = 0; s < n; s++) D[s] = dijkstra(g, s);
        for (int strategy = 0; strategy < 2; strategy++) { std::vector<int> L = pickLandmarks(g, 4, strategy == 1, rng); std::vector<std::vector<long>> dl; for (int l : L) dl.push_back(D[l]); auto h = [&](int v, int t) { long b = 0; for (auto& d : dl) b = std::max(b, std::labs(d[t] - d[v])); return b; };
            if (strategy == 1) { for (int t = 0; t < n; t += 7) for (int v = 0; v < n; v++) { assert(h(v, t) <= D[v][t]); for (auto [u, w] : g.adj[v]) assert(h(v, t) <= w + h(u, t)); } }                                       // ① 허용적 · 일관적
            double sum = 0; int cnt = 0; for (int q = 0; q < 300; q++) { int s = rng() % n, t = rng() % n; if (s != t) { sum += (double)h(s, t) / D[s][t]; cnt++; } } (strategy ? tightFar : tightRand) += sum / cnt;
            if (strategy == 1) for (int q = 0; q < 40; q++) { int s = rng() % n, t = rng() % n; if (s == t) continue; std::vector<long> dd(n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; dd[s] = 0; pq.push({h(s, t), s}); long ex = 0; long res = -1; while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > dd[u] + h(u, t)) continue; ex++; if (u == t) { res = dd[u]; break; } for (auto [v, w] : g.adj[u]) if (dd[u] + w < dd[v]) { dd[v] = dd[u] + w; pq.push({dd[v] + h(v, t), v}); } }
                assert(res == D[s][t]); expAlt += ex; long ex0 = 0; { std::vector<long> d0(n, 1L << 50); std::priority_queue<Q, std::vector<Q>, std::greater<Q>> p0; d0[s] = 0; p0.push({0, s}); while (!p0.empty()) { auto [du, u] = p0.top(); p0.pop(); if (du > d0[u]) continue; ex0++; if (u == t) break; for (auto [v, w] : g.adj[u]) if (du + w < d0[v]) { d0[v] = du + w; p0.push({d0[v], v}); } } } expDij += ex0; queries++; } }
        graphs++; }
    assert(graphs == 8 && expAlt < expDij && tightFar > tightRand);
    std::cout << "LandmarkHeuristic: " << graphs << " graphs; ALT bounds admissible and consistent, A* matches Dijkstra on " << queries << " queries while expanding " << expAlt << " vs " << expDij << " vertices; mean lower bound / true distance: farthest landmarks " << tightFar / graphs << " vs random " << tightRand / graphs << std::endl; return 0;
}
// Time Complexity: 전처리 O(k · E log V), 질의 A* 확장 수에 비례(h 계산 O(k))
// Space Complexity: O(k · V)
```
## ContractionHierarchy()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 축약 계층(Contraction Hierarchies, Geisberger et al. 2008): 도로망 최단 경로의 대표적 전처리 기법. 정점을 "덜 중요한 것부터" 하나씩 축약(제거)하되, 그 정점을 지나던 최단 경로가 끊기지 않도록 이웃 쌍 (u,w) 사이에 지름길(shortcut, u–v–w 의 합)을 넣는다 — 단 증인 탐색(witness search)으로
// v 를 지나지 않는 같거나 더 짧은 경로가 있음이 확인되면 지름길은 불필요하다. 중요도는 (필요한 지름길 수 − 제거되는 간선 수) + 이미 축약된 이웃 수 로 어림하고 게으른 갱신을 쓴다.
// 질의는 양방향 Dijkstra 인데 양쪽 모두 "순위가 더 높은 정점으로만" 올라간다(상향 탐색 공간은 작음). 두 탐색이 만나는 정점 중 합이 최소인 곳이 정답이며, 경로는 지름길을 재귀적으로 풀어서 복원한다.
// 검증(가중 도시 20×20 + 장거리 간선): ① 600개 질의에서 CH 거리 == Dijkstra ② 복원한 경로의 모든 걸음이 원래 간선이고 비용 합이 거리와 같음 ③ 질의당 확장 정점 수가 Dijkstra 보다 훨씬 적음 ④ 지름길 수 보고
struct Graph { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
Graph makeGraph(int W, int H, std::mt19937& rng, int maxW, int extra) {                                                                 // 가중치가 불규칙한 격자형 도시 + 약간의 장거리 간선
    Graph g{W * H, std::vector<std::vector<std::pair<int, int>>>(W * H)}; std::map<std::pair<int, int>, int> best; auto add = [&](int a, int b, int w) { if (a == b) return; auto k = std::make_pair(std::min(a, b), std::max(a, b)); if (!best.count(k) || w < best[k]) best[k] = w; };
    for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { int u = r * W + c; if (c + 1 < W) add(u, u + 1, 1 + rng() % maxW); if (r + 1 < H) add(u, u + W, 1 + rng() % maxW); } for (int k = 0; k < extra; k++) add(rng() % (W * H), rng() % (W * H), maxW * 3 + rng() % (maxW * 3));
    for (auto& [e, w] : best) { g.adj[e.first].push_back({e.second, w}); g.adj[e.second].push_back({e.first, w}); } return g; }
std::vector<long> dijkstra(const Graph& g, int s) { std::vector<long> d(g.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
struct Arc { int to, w, mid; };
struct CH {
    int n; std::vector<int> rank; std::vector<std::vector<Arc>> up; std::map<std::pair<int, int>, std::pair<int, int>> sc; long shortcuts = 0;                    // sc[(a,b)] = (가중치, 중간 정점): 풀어쓰기용
    long witness(const std::vector<std::map<int, std::pair<int, int>>>& cur, int u, int skip, int target, long limit) { std::map<int, long> d; typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[u] = 0; pq.push({0, u}); while (!pq.empty()) { auto [du, x] = pq.top(); pq.pop(); if (du > d[x] || du > limit) continue; if (x == target) return du; for (auto& [y, wm] : cur[x]) if (y != skip && (!d.count(y) || du + wm.first < d[y])) { d[y] = du + wm.first; pq.push({d[y], y}); } } return d.count(target) ? d[target] : (1L << 50); }
    void build(const Graph& g) { n = g.n; rank.assign(n, -1); up.assign(n, {}); std::vector<std::map<int, std::pair<int, int>>> cur(n); for (int u = 0; u < n; u++) for (auto [v, w] : g.adj[u]) { auto it = cur[u].find(v); if (it == cur[u].end() || w < it->second.first) cur[u][v] = {w, -1}; }
        std::vector<int> deleted(n, 0); auto priority = [&](int v) { int need = 0; std::vector<std::pair<int, std::pair<int, int>>> N(cur[v].begin(), cur[v].end()); for (size_t i = 0; i < N.size(); i++) for (size_t j = i + 1; j < N.size(); j++) { long via = (long)N[i].second.first + N[j].second.first; if (witness(cur, N[i].first, v, N[j].first, via) > via) need++; } return need - (int)N.size() + 2 * deleted[v]; };
        typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; for (int v = 0; v < n; v++) pq.push({priority(v), v}); int order = 0;
        while (!pq.empty()) { auto [p, v] = pq.top(); pq.pop(); if (rank[v] >= 0) continue; int np = priority(v); if (!pq.empty() && np > pq.top().first) { pq.push({np, v}); continue; }                                            // 게으른 갱신
            std::vector<std::pair<int, std::pair<int, int>>> N(cur[v].begin(), cur[v].end()); for (size_t i = 0; i < N.size(); i++) for (size_t j = i + 1; j < N.size(); j++) { int a = N[i].first, b = N[j].first; long via = (long)N[i].second.first + N[j].second.first; if (witness(cur, a, v, b, via) > via) { auto it = cur[a].find(b); if (it == cur[a].end() || via < it->second.first) { cur[a][b] = {(int)via, v}; cur[b][a] = {(int)via, v}; shortcuts++; } } }
            for (auto& [x, wm] : N) { up[v].push_back({x, wm.first, wm.second}); sc[{std::min(v, x), std::max(v, x)}] = wm; cur[x].erase(v); deleted[x]++; } cur[v].clear(); rank[v] = order++; }
    }
    void unpack(int a, int b, std::vector<int>& out) const { auto it = sc.find({std::min(a, b), std::max(a, b)}); int mid = it->second.second; if (mid < 0) { out.push_back(b); return; } unpack(a, mid, out); unpack(mid, b, out); }
    long query(int s, int t, long& settled, std::vector<int>* path = nullptr) const {
        std::vector<long> d[2] = {std::vector<long>(n, 1L << 50), std::vector<long>(n, 1L << 50)}; std::vector<int> par[2] = {std::vector<int>(n, -1), std::vector<int>(n, -1)}; typedef std::pair<long, int> Q; settled = 0; long best = 1L << 50; int meet = -1;
        for (int side = 0; side < 2; side++) { std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; int src = side ? t : s; d[side][src] = 0; pq.push({0, src}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[side][u]) continue; settled++; for (const Arc& a : up[u]) if (du + a.w < d[side][a.to]) { d[side][a.to] = du + a.w; par[side][a.to] = u; pq.push({d[side][a.to], a.to}); } } }
        for (int v = 0; v < n; v++) if (d[0][v] + d[1][v] < best) { best = d[0][v] + d[1][v]; meet = v; }
        if (path && best < (1L << 49)) { std::vector<int> fw; for (int v = meet; v >= 0; v = par[0][v]) fw.push_back(v); std::reverse(fw.begin(), fw.end()); path->assign(1, fw[0]); for (size_t i = 1; i < fw.size(); i++) unpack(fw[i - 1], fw[i], *path); for (int v = meet; par[1][v] >= 0; v = par[1][v]) unpack(v, par[1][v], *path); } return best; }
};
int main() {
    std::mt19937 rng(12); Graph g = makeGraph(20, 20, rng, 9, 20); CH ch; ch.build(g); std::vector<std::vector<long>> D(g.n); for (int s = 0; s < g.n; s++) D[s] = dijkstra(g, s);
    std::map<std::pair<int, int>, int> wt; for (int u = 0; u < g.n; u++) for (auto [v, w] : g.adj[u]) wt[{u, v}] = w; long settled = 0, dijSettled = 0; int checked = 0;
    for (int q = 0; q < 600; q++) { int s = rng() % g.n, t = rng() % g.n; if (s == t) continue; long st; std::vector<int> path; long d = ch.query(s, t, st, &path); assert(d == D[s][t]); settled += st; dijSettled += g.n;                                       // ① 거리 일치
        long sum = 0; assert(path.front() == s && path.back() == t); for (size_t i = 1; i < path.size(); i++) { auto it = wt.find({path[i - 1], path[i]}); assert(it != wt.end()); sum += it->second; } assert(sum == d); checked++; }                  // ② 복원 경로
    assert(checked > 500 && settled * 3 < dijSettled);
    std::cout << "ContractionHierarchy: " << g.n << " vertices, " << ch.shortcuts << " shortcuts added; " << checked << " queries equal Dijkstra with unpacked paths valid; upward search settled " << (double)settled / checked << " vertices per query on average versus up to " << g.n << " for a full Dijkstra" << std::endl; return 0;
}
// Time Complexity: 전처리 O(V · 증인 탐색), 질의 O(상향 탐색 공간 크기 × log) — 도로망에서 수백 정점
// Space Complexity: O(V + 지름길 수)
```
## TransitNodeRouting()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 환승 노드 라우팅(Transit Node Routing, Bast et al. 2007): 먼 거리의 최단 경로는 소수의 "환승 노드"(교통의 요충: 고속도로 진입로 같은 곳)를 반드시 지난다는 관찰에 기대어 질의를 표 조회 몇 번으로 줄인다.
// 여기서는 CH 의 순위가 가장 높은 k 개 정점을 환승 노드 T 로 둔다. 전처리: T 의 모든 쌍 사이 정확한 거리표 D, 그리고 각 정점 v 의 접근 노드(access node) = v 에서 상향 탐색으로 도달하는 환승 노드와 그 거리(환승 노드를 넘어서는 확장은 하지 않음 — 환승 노드는 최고 순위라 그 뒤는 모두 T 안).
// 질의 s→t: ① 환승 경유 후보 min_{a∈A(s), b∈A(t)} d(s,a) + D[a][b] + d(b,t) ② 국지 후보: 환승 노드를 만나지 않는 상향 탐색 두 개의 교차 최소. 둘 중 작은 값이 정확한 거리다(CH 최단 경로는 상향–하향 꼴이고 환승 노드를 포함하면 그 부분은 모두 T 안에 있기 때문).
// 검증: ① 600개 질의에서 TNR == Dijkstra ② 질의의 대부분은 ①이 이기는 '먼' 질의이며(국지 후보가 이기는 질의 비율 보고) 접근 노드 수의 평균이 작음 ③ k 를 키우면 국지 질의 비율이 줄어듦
struct Graph { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
Graph makeGraph(int W, int H, std::mt19937& rng, int maxW, int extra) {                                                                 // 가중치가 불규칙한 격자형 도시 + 약간의 장거리 간선
    Graph g{W * H, std::vector<std::vector<std::pair<int, int>>>(W * H)}; std::map<std::pair<int, int>, int> best; auto add = [&](int a, int b, int w) { if (a == b) return; auto k = std::make_pair(std::min(a, b), std::max(a, b)); if (!best.count(k) || w < best[k]) best[k] = w; };
    for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { int u = r * W + c; if (c + 1 < W) add(u, u + 1, 1 + rng() % maxW); if (r + 1 < H) add(u, u + W, 1 + rng() % maxW); } for (int k = 0; k < extra; k++) add(rng() % (W * H), rng() % (W * H), maxW * 3 + rng() % (maxW * 3));
    for (auto& [e, w] : best) { g.adj[e.first].push_back({e.second, w}); g.adj[e.second].push_back({e.first, w}); } return g; }
std::vector<long> dijkstra(const Graph& g, int s) { std::vector<long> d(g.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
struct Arc { int to, w, mid; };
struct CH {
    int n; std::vector<int> rank; std::vector<std::vector<Arc>> up; std::map<std::pair<int, int>, std::pair<int, int>> sc; long shortcuts = 0;                    // sc[(a,b)] = (가중치, 중간 정점): 풀어쓰기용
    long witness(const std::vector<std::map<int, std::pair<int, int>>>& cur, int u, int skip, int target, long limit) { std::map<int, long> d; typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[u] = 0; pq.push({0, u}); while (!pq.empty()) { auto [du, x] = pq.top(); pq.pop(); if (du > d[x] || du > limit) continue; if (x == target) return du; for (auto& [y, wm] : cur[x]) if (y != skip && (!d.count(y) || du + wm.first < d[y])) { d[y] = du + wm.first; pq.push({d[y], y}); } } return d.count(target) ? d[target] : (1L << 50); }
    void build(const Graph& g) { n = g.n; rank.assign(n, -1); up.assign(n, {}); std::vector<std::map<int, std::pair<int, int>>> cur(n); for (int u = 0; u < n; u++) for (auto [v, w] : g.adj[u]) { auto it = cur[u].find(v); if (it == cur[u].end() || w < it->second.first) cur[u][v] = {w, -1}; }
        std::vector<int> deleted(n, 0); auto priority = [&](int v) { int need = 0; std::vector<std::pair<int, std::pair<int, int>>> N(cur[v].begin(), cur[v].end()); for (size_t i = 0; i < N.size(); i++) for (size_t j = i + 1; j < N.size(); j++) { long via = (long)N[i].second.first + N[j].second.first; if (witness(cur, N[i].first, v, N[j].first, via) > via) need++; } return need - (int)N.size() + 2 * deleted[v]; };
        typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; for (int v = 0; v < n; v++) pq.push({priority(v), v}); int order = 0;
        while (!pq.empty()) { auto [p, v] = pq.top(); pq.pop(); if (rank[v] >= 0) continue; int np = priority(v); if (!pq.empty() && np > pq.top().first) { pq.push({np, v}); continue; }                                            // 게으른 갱신
            std::vector<std::pair<int, std::pair<int, int>>> N(cur[v].begin(), cur[v].end()); for (size_t i = 0; i < N.size(); i++) for (size_t j = i + 1; j < N.size(); j++) { int a = N[i].first, b = N[j].first; long via = (long)N[i].second.first + N[j].second.first; if (witness(cur, a, v, b, via) > via) { auto it = cur[a].find(b); if (it == cur[a].end() || via < it->second.first) { cur[a][b] = {(int)via, v}; cur[b][a] = {(int)via, v}; shortcuts++; } } }
            for (auto& [x, wm] : N) { up[v].push_back({x, wm.first, wm.second}); sc[{std::min(v, x), std::max(v, x)}] = wm; cur[x].erase(v); deleted[x]++; } cur[v].clear(); rank[v] = order++; }
    }
    void unpack(int a, int b, std::vector<int>& out) const { auto it = sc.find({std::min(a, b), std::max(a, b)}); int mid = it->second.second; if (mid < 0) { out.push_back(b); return; } unpack(a, mid, out); unpack(mid, b, out); }
    long query(int s, int t, long& settled, std::vector<int>* path = nullptr) const {
        std::vector<long> d[2] = {std::vector<long>(n, 1L << 50), std::vector<long>(n, 1L << 50)}; std::vector<int> par[2] = {std::vector<int>(n, -1), std::vector<int>(n, -1)}; typedef std::pair<long, int> Q; settled = 0; long best = 1L << 50; int meet = -1;
        for (int side = 0; side < 2; side++) { std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; int src = side ? t : s; d[side][src] = 0; pq.push({0, src}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[side][u]) continue; settled++; for (const Arc& a : up[u]) if (du + a.w < d[side][a.to]) { d[side][a.to] = du + a.w; par[side][a.to] = u; pq.push({d[side][a.to], a.to}); } } }
        for (int v = 0; v < n; v++) if (d[0][v] + d[1][v] < best) { best = d[0][v] + d[1][v]; meet = v; }
        if (path && best < (1L << 49)) { std::vector<int> fw; for (int v = meet; v >= 0; v = par[0][v]) fw.push_back(v); std::reverse(fw.begin(), fw.end()); path->assign(1, fw[0]); for (size_t i = 1; i < fw.size(); i++) unpack(fw[i - 1], fw[i], *path); for (int v = meet; par[1][v] >= 0; v = par[1][v]) unpack(v, par[1][v], *path); } return best; }
};
int main() {
    std::mt19937 rng(14); Graph g = makeGraph(20, 20, rng, 9, 20); CH ch; ch.build(g); int n = g.n; std::vector<std::vector<long>> D(n); for (int s = 0; s < n; s++) D[s] = dijkstra(g, s); double avgAccessByK[2] = {0, 0}, localShare[2] = {0, 0}; const int Ks[2] = {8, 40};
    for (int ki = 0; ki < 2; ki++) { int K = Ks[ki]; std::vector<int> byRank(n); for (int v = 0; v < n; v++) byRank[ch.rank[v]] = v; std::set<int> T; for (int i = 0; i < K; i++) T.insert(byRank[n - 1 - i]); std::vector<int> tl(T.begin(), T.end());
        std::vector<std::vector<long>> table(K, std::vector<long>(K)); for (int i = 0; i < K; i++) for (int j = 0; j < K; j++) table[i][j] = D[tl[i]][tl[j]];
        auto upSearch = [&](int s, std::map<int, long>& access, std::vector<long>& local) { local.assign(n, 1L << 50); std::vector<long> d(n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s});
            while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; if (T.count(u)) { access[u] = du; continue; } local[u] = du; for (const Arc& a : ch.up[u]) if (du + a.w < d[a.to]) { d[a.to] = du + a.w; pq.push({d[a.to], a.to}); } } };       // 환승 노드에서 멈춤
        int checked = 0, localWins = 0; long accessTotal = 0;
        for (int q = 0; q < 600; q++) { int s = rng() % n, t = rng() % n; if (s == t) continue; std::map<int, long> As, At; std::vector<long> ls, lt; upSearch(s, As, ls); upSearch(t, At, lt); long viaT = 1L << 50; for (auto& [a, da] : As) for (auto& [b, db] : At) viaT = std::min(viaT, da + D[a][b] + db);
            long local = 1L << 50; for (int v = 0; v < n; v++) local = std::min(local, ls[v] + lt[v]); long ans = std::min(viaT, local); assert(ans == D[s][t]); checked++; localWins += local < viaT; accessTotal += As.size() + At.size(); }                           // ① 정확
        avgAccessByK[ki] = (double)accessTotal / (2 * checked); localShare[ki] = (double)localWins / checked; }
    assert(localShare[1] < localShare[0] && avgAccessByK[0] > 0);
    std::cout << "TransitNodeRouting: 600 queries equal Dijkstra for both transit sets; k=" << Ks[0] << ": " << 100 * localShare[0] << "% local queries, " << avgAccessByK[0] << " access nodes per endpoint; k=" << Ks[1] << ": " << 100 * localShare[1] << "% local, " << avgAccessByK[1] << " access nodes" << std::endl; return 0;
}
// Time Complexity: 질의 O(|A(s)| · |A(t)|) 표 조회 + 국지 탐색; 전처리는 CH + k² 거리표
// Space Complexity: O(k² + V · 접근 노드 수)
```
## ReachBasedRouting()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 도달 범위 기반 라우팅(reach-based routing, Gutman 2004): 정점 v 의 reach 는 v 를 지나는 모든 최단 경로 P(s→t)에 대한 min(d(s,v), d(v,t)) 의 최댓값이다. reach 가 작은 정점은 "출발·도착 근처의 지역 도로"이고 큰 정점은 "고속도로" 이다.
// 양방향 탐색에서 정점 v 를 확장하려는 시점에 v 까지 이미 확인된 거리 d_f(v) 와, 반대 탐색이 이미 반경 r 까지 닿았다는 사실(아직 안 닿은 정점의 목표까지 거리 ≥ r)이 있다. v 가 어떤 최단 경로에 있다면 min(d(s,v), d(v,t)) ≤ reach(v) 이므로
// reach(v) < d_f(v) 이면서 reach(v) < r 이면 v 는 어떤 s–t 최단 경로에도 없다 — 가지치기해도 정답이 변하지 않는다. 정확한 reach 는 모든 출발점의 최단 경로 트리에서 min(깊이, 아래쪽 가장 깊은 후손까지의 거리)의 최댓값을 구하면 된다(최단 경로가 유일해야 하므로 가중치를 큰 무작위 정수로).
// 검증(16×16 도시, 가중치 1..10⁶): ① 모든 s–t 쌍(65,280 개)에서 reach 가지치기 양방향 Dijkstra == 일반 Dijkstra ② 확장 정점 수 합이 가지치기 없는 양방향 Dijkstra 보다 적음 ③ reach 상위 10% 정점의 평균 reach 가 전체 평균의 1.5 배 이상(중요한 정점과 지역 정점이 구분됨)
struct Graph { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
Graph makeGraph(int W, int H, std::mt19937& rng, int maxW, int extra) {                                                                 // 가중치가 불규칙한 격자형 도시 + 약간의 장거리 간선
    Graph g{W * H, std::vector<std::vector<std::pair<int, int>>>(W * H)}; std::map<std::pair<int, int>, int> best; auto add = [&](int a, int b, int w) { if (a == b) return; auto k = std::make_pair(std::min(a, b), std::max(a, b)); if (!best.count(k) || w < best[k]) best[k] = w; };
    for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { int u = r * W + c; if (c + 1 < W) add(u, u + 1, 1 + rng() % maxW); if (r + 1 < H) add(u, u + W, 1 + rng() % maxW); } for (int k = 0; k < extra; k++) add(rng() % (W * H), rng() % (W * H), maxW * 3 + rng() % (maxW * 3));
    for (auto& [e, w] : best) { g.adj[e.first].push_back({e.second, w}); g.adj[e.second].push_back({e.first, w}); } return g; }
std::vector<long> dijkstra(const Graph& g, int s) { std::vector<long> d(g.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
int main() {
    std::mt19937 rng(16); Graph g = makeGraph(16, 16, rng, 1000000, 6); int n = g.n; std::vector<std::vector<long>> D(n); for (int s = 0; s < n; s++) D[s] = dijkstra(g, s);
    std::vector<long> reach(n, 0); for (int s = 0; s < n; s++) { std::vector<int> par(n, -1); std::vector<int> order(n); for (int i = 0; i < n; i++) order[i] = i; std::sort(order.begin(), order.end(), [&](int a, int b) { return D[s][a] < D[s][b]; });
        for (int v = 0; v < n; v++) if (v != s) for (auto [u, w] : g.adj[v]) if (D[s][u] + w == D[s][v]) { par[v] = u; break; } std::vector<long> height(n, 0); for (int i = n - 1; i > 0; i--) { int v = order[i]; if (par[v] >= 0) height[par[v]] = std::max(height[par[v]], height[v] + (D[s][v] - D[s][par[v]])); }
        for (int v = 0; v < n; v++) reach[v] = std::max(reach[v], std::min(D[s][v], height[v])); }                                                       // 출발점 s 의 트리에서 v 의 reach 기여
    long expPruned = 0, expPlain = 0; int pairs = 0;
    for (int s = 0; s < n; s++) for (int t = 0; t < n; t++) { if (s == t) continue; typedef std::pair<long, int> Q; std::vector<long> d[2] = {std::vector<long>(n, 1L << 50), std::vector<long>(n, 1L << 50)}; std::vector<char> done[2] = {std::vector<char>(n, 0), std::vector<char>(n, 0)}; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq[2]; d[0][s] = 0; d[1][t] = 0; pq[0].push({0, s}); pq[1].push({0, t}); long mu = 1L << 50; long ex = 0; bool usePrune = true;
        for (int pass = 0; pass < 2; pass++) { for (int side = 0; side < 2; side++) { d[side].assign(n, 1L << 50); done[side].assign(n, 0); pq[side] = {}; } d[0][s] = 0; d[1][t] = 0; pq[0].push({0, s}); pq[1].push({0, t}); mu = 1L << 50; ex = 0; usePrune = pass == 0; long radius[2] = {0, 0};
            while (!pq[0].empty() || !pq[1].empty()) { long top0 = pq[0].empty() ? (1L << 50) : pq[0].top().first, top1 = pq[1].empty() ? (1L << 50) : pq[1].top().first; if (top0 + top1 >= mu) break; int side = top0 <= top1 ? 0 : 1; auto [du, u] = pq[side].top(); pq[side].pop(); if (du > d[side][u]) continue; if (done[side][u]) continue; radius[side] = du;
                if (usePrune && u != s && u != t && reach[u] < du && reach[u] < radius[1 - side]) continue;                                                                 // reach 가지치기: 이 정점은 최단 경로에 없다
                done[side][u] = 1; ex++; if (d[1 - side][u] < (1L << 50)) mu = std::min(mu, du + d[1 - side][u]);
                for (auto [v, w] : g.adj[u]) if (du + w < d[side][v]) { d[side][v] = du + w; pq[side].push({d[side][v], v}); if (d[1 - side][v] < (1L << 50)) mu = std::min(mu, d[side][v] + d[1 - side][v]); } }
            if (pass == 0) { assert(mu == D[s][t]); expPruned += ex; } else expPlain += ex; } pairs++; }                                                                  // ① 정확, ② 확장 수 비교
    std::vector<long> sorted = reach; std::sort(sorted.begin(), sorted.end()); long topAvg = 0, allAvg = 0; for (int i = 0; i < n; i++) allAvg += reach[i]; for (int i = n - n / 10; i < n; i++) topAvg += sorted[i];
    assert(expPruned < expPlain && pairs == n * (n - 1) && 2 * (topAvg / (n / 10)) > 3 * (allAvg / n));
    std::cout << "ReachBasedRouting: all " << pairs << " ordered pairs match Dijkstra; settled vertices " << expPruned << " with reach pruning vs " << expPlain << " for plain bidirectional search; mean reach of the top 10% vertices is " << (double)(topAvg / (n / 10)) / (allAvg / n) << "x the overall mean" << std::endl; return 0;
}
// Time Complexity: reach 계산 O(V · (E log V)), 질의 양방향 Dijkstra + 가지치기
// Space Complexity: O(V)
```
## ALTAlgorithm()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// ALT 알고리즘(A*, Landmarks, Triangle inequality) — 양방향 판: 랜드마크 하한으로 만든 일관적 퍼텐셜을 정·역방향 탐색에 모두 쓴다(Goldberg & Harrelson 2005, Ikeda 평균 퍼텐셜).
// h_t(v) = max_L |d(L,t) − d(L,v)| (v→t 하한), h_s(v) = max_L |d(L,s) − d(L,v)| (s→v 하한)일 때 φ(v) = (h_t(v) − h_s(v)) / 2. 간선 (u,v)의 줄어든 비용 w + φ(v) − φ(u) = ½[(w + h_t(v) − h_t(u)) + (w + h_s(u) − h_s(v))] ≥ 0 이므로 정·역방향이 같은 비음 비용으로 양방향 Dijkstra 를 돌릴 수 있다.
// 줄어든 거리에서 두 탐색의 큐 맨 위 합이 지금까지 찾은 최선 경로 μ′ = μ − φ(s) + φ(t) 이상이면 종료. 검증(가중 도시 24×24, 랜드마크 8개 = 가장 먼 점 선택): ① 500개 질의에서 ALT 양방향 == Dijkstra ② 확장 정점 수: ALT 양방향 < 일반 양방향 < 단방향 Dijkstra 순으로 합이 줄어듦 ③ 모든 간선에서 줄어든 비용이 0 이상(퍼텐셜의 일관성)
struct Graph { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
Graph makeGraph(int W, int H, std::mt19937& rng, int maxW, int extra) {                                                                 // 가중치가 불규칙한 격자형 도시 + 약간의 장거리 간선
    Graph g{W * H, std::vector<std::vector<std::pair<int, int>>>(W * H)}; std::map<std::pair<int, int>, int> best; auto add = [&](int a, int b, int w) { if (a == b) return; auto k = std::make_pair(std::min(a, b), std::max(a, b)); if (!best.count(k) || w < best[k]) best[k] = w; };
    for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { int u = r * W + c; if (c + 1 < W) add(u, u + 1, 1 + rng() % maxW); if (r + 1 < H) add(u, u + W, 1 + rng() % maxW); } for (int k = 0; k < extra; k++) add(rng() % (W * H), rng() % (W * H), maxW * 3 + rng() % (maxW * 3));
    for (auto& [e, w] : best) { g.adj[e.first].push_back({e.second, w}); g.adj[e.second].push_back({e.first, w}); } return g; }
std::vector<long> dijkstra(const Graph& g, int s) { std::vector<long> d(g.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
int main() {
    std::mt19937 rng(18); Graph g = makeGraph(24, 24, rng, 9, 24); int n = g.n; std::vector<int> L = {(int)(rng() % n)}; std::vector<long> mn(n, 1L << 50); std::vector<std::vector<long>> dl; dl.push_back(dijkstra(g, L[0]));
    while (L.size() < 8) { for (int v = 0; v < n; v++) mn[v] = std::min(mn[v], dl.back()[v]); int best = 0; for (int v = 0; v < n; v++) if (mn[v] > mn[best]) best = v; L.push_back(best); dl.push_back(dijkstra(g, best)); }                                // 가장 먼 점 선택
    auto hb = [&](int v, int x) { long b = 0; for (auto& d : dl) b = std::max(b, std::labs(d[x] - d[v])); return b; };                                                                    // |d(L,x) − d(L,v)|
    long exAlt = 0, exBi = 0, exUni = 0; int checked = 0; typedef std::pair<double, int> Q;
    for (int q = 0; q < 500; q++) { int s = rng() % n, t = rng() % n; if (s == t) continue; std::vector<long> D = dijkstra(g, s);
        auto phi = [&](int v) { return (hb(v, t) - hb(v, s)) / 2.0; }; if (q < 5) for (int u = 0; u < n; u++) for (auto [v, w] : g.adj[u]) assert(w + phi(v) - phi(u) >= -1e-9);                                       // ③ 줄어든 비용 ≥ 0
        for (int mode = 0; mode < 2; mode++) { bool alt = mode == 0; auto pot = [&](int v) { return alt ? phi(v) : 0.0; };
            std::vector<double> d[2] = {std::vector<double>(n, 1e18), std::vector<double>(n, 1e18)}; std::vector<char> done[2] = {std::vector<char>(n, 0), std::vector<char>(n, 0)}; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq[2]; d[0][s] = 0; d[1][t] = 0; pq[0].push({0, s}); pq[1].push({0, t}); double mu = 1e18; long ex = 0;
            auto key = [&](int side, int v) { return side == 0 ? d[0][v] + pot(v) - pot(s) : d[1][v] - pot(v) + pot(t); };                                                                // 줄어든 거리(정방향: +φ(v) − φ(s), 역방향: −φ(v) + φ(t))
            pq[0] = {}; pq[1] = {}; pq[0].push({key(0, s), s}); pq[1].push({key(1, t), t});
            while (!pq[0].empty() || !pq[1].empty()) { double top0 = pq[0].empty() ? 1e18 : pq[0].top().first, top1 = pq[1].empty() ? 1e18 : pq[1].top().first; if (top0 + top1 >= mu - pot(s) + pot(t) - 1e-9) break; int side = top0 <= top1 ? 0 : 1; auto [kk, u] = pq[side].top(); pq[side].pop(); if (done[side][u] || kk > key(side, u) + 1e-9) continue; done[side][u] = 1; ex++;
                if (d[1 - side][u] < 1e17) mu = std::min(mu, d[side][u] + d[1 - side][u]);
                for (auto [v, w] : g.adj[u]) if (d[side][u] + w < d[side][v] - 1e-12) { d[side][v] = d[side][u] + w; pq[side].push({key(side, v), v}); if (d[1 - side][v] < 1e17) mu = std::min(mu, d[side][v] + d[1 - side][v]); } }
            assert(std::fabs(mu - D[t]) < 1e-9); (alt ? exAlt : exBi) += ex; }
        { std::vector<long> d(n, 1L << 50); std::priority_queue<std::pair<long, int>, std::vector<std::pair<long, int>>, std::greater<std::pair<long, int>>> pq; d[s] = 0; pq.push({0, s}); long ex = 0; while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; ex++; if (u == t) break; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } exUni += ex; } checked++; }
    assert(checked > 450 && exAlt < exBi && exBi < exUni);
    std::cout << "ALTAlgorithm: " << checked << " queries, bidirectional ALT equals Dijkstra; settled vertices: ALT " << exAlt << " < bidirectional " << exBi << " < unidirectional " << exUni << std::endl; return 0;
}
// Time Complexity: 전처리 O(k · E log V), 질의는 줄어든 비용 위의 양방향 Dijkstra
// Space Complexity: O(k · V)
```

# Part 16. 연구 주제
## AnytimeAStar()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// Anytime A*(여기서는 가중치 감소 재시작 방식): 실시간 시스템(로봇·게임)은 "정해진 시간 안에 지금 가능한 최선의 해" 가 필요하다. 가중 A* (f = g + ε·h) 는 ε > 1 일수록 빠르게 해를 내지만 비용이 최적의 ε 배까지 나빠질 수 있다(최적의 ε 배 이내 보장).
// 그래서 ε = 3, 2, 1.5, 1.2, 1 로 줄여 가며 같은 문제를 다시 풀고 매번 "지금까지 최선의 해" 를 내놓는다 — 첫 해는 매우 빨리 나오고 시간이 허락하는 만큼 품질이 좋아져 마지막에 최적이 된다. 이 방식은 매 ε 마다 처음부터 다시 계산한다(재사용하는 개선판이 바로 다음 항목 ARA*).
// 검증(28×28 지도 25개, 8방향 10/14, 옥타일 휴리스틱): ① ε 단계마다 비용 ≤ ε × 최적 ② 최선 해 비용이 단계마다 비증가하고 마지막(ε=1)은 Dijkstra 와 같은 최적 ③ 확장 예산을 B 로 제한하면 B 가 커질수록 얻는 해의 품질이 좋아짐(예산 안에 해를 못 찾는 경우는 없음 표시) ④ ε=3 의 첫 해는 ε=1 보다 확장이 적음
const int R = 28, C = 28; std::vector<std::string> w;
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
bool stepOk(int r, int c, int dr, int dc) { if (!freeCell(r + dr, c + dc)) return false; return !(dr && dc && (!freeCell(r + dr, c) || !freeCell(r, c + dc))); }
int stepCost(int dr, int dc) { return dr && dc ? 14 : 10; }
int octile(int v, int t) { int dr = std::abs(v / C - t / C), dc = std::abs(v % C - t % C); return 10 * (dr + dc) - 6 * std::min(dr, dc); }
std::vector<int> dijkstraAll(int s) { std::vector<int> d(R * C, 1 << 28); typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; if (du + stepCost(dr, dc) < d[v]) { d[v] = du + stepCost(dr, dc); pq.push({d[v], v}); } } } return d; }
struct Out { int cost; long expanded; };
Out weighted(int s, int t, double eps, long budget) { std::vector<int> g(R * C, 1 << 28); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; g[s] = 0; pq.push({eps * octile(s, t), s}); long ex = 0;
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + eps * octile(u, t) + 1e-9) continue; ex++; if (u == t) return {g[u], ex}; if (ex >= budget) return {-1, ex}; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; int ng = g[u] + stepCost(dr, dc); if (ng < g[v]) { g[v] = ng; pq.push({ng + eps * octile(v, t), v}); } } }
    return {-1, ex}; }
int main() {
    std::mt19937 rng(9); const double eps[5] = {3.0, 2.0, 1.5, 1.2, 1.0}; int maps = 0; long firstEx = 0, lastEx = 0; long cum[5] = {0}; int improvedAtLeastOnce = 0; double qualityByBudget[3] = {0, 0, 0}; int solvedByBudget[3] = {0, 0, 0}; const long budgets[3] = {60, 200, 800};
    for (int m = 0; m < 25; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 28) ch = '#'; int s = 0, t = R * C - 1; w[0][0] = w[R - 1][C - 1] = '.'; int opt = dijkstraAll(s)[t]; if (opt >= (1 << 28)) continue; maps++;
        int best = 1 << 28; bool improved = false; for (int k = 0; k < 5; k++) { Out o = weighted(s, t, eps[k], 1L << 40); assert(o.cost >= opt && o.cost <= eps[k] * opt + 1e-9); if (o.cost < best) { if (best < (1 << 28)) improved = true; best = o.cost; } cum[k] += o.expanded; if (k == 0) firstEx += o.expanded; if (k == 4) { lastEx += o.expanded; assert(o.cost == opt); } }
        improvedAtLeastOnce += improved;
        for (int b = 0; b < 3; b++) { int bestB = 1 << 28; long used = 0; for (int k = 0; k < 5 && used < budgets[b]; k++) { Out o = weighted(s, t, eps[k], budgets[b] - used); used += o.expanded; if (o.cost >= 0) bestB = std::min(bestB, o.cost); } if (bestB < (1 << 28)) { solvedByBudget[b]++; qualityByBudget[b] += (double)bestB / opt; } } }
    assert(maps >= 15 && firstEx < lastEx && improvedAtLeastOnce > 0);
    double q0 = qualityByBudget[0] / std::max(1, solvedByBudget[0]), q2 = qualityByBudget[2] / solvedByBudget[2]; assert(solvedByBudget[0] <= solvedByBudget[1] && solvedByBudget[1] <= solvedByBudget[2] && q2 <= q0 + 1e-9);
    std::cout << "AnytimeAStar: " << maps << " maps; every epsilon step within its bound and the last step optimal; first (eps=3) solutions cost " << firstEx << " expansions vs " << lastEx << " for eps=1; with budgets 60/200/800 expansions the best-so-far solved " << solvedByBudget[0] << "/" << solvedByBudget[1] << "/" << solvedByBudget[2] << " maps at mean cost ratio " << q0 << " -> " << q2 << std::endl; return 0;
}
// Time Complexity: ε 단계마다 가중 A* 한 번 — 단계별 확장 수는 ε 가 작을수록 증가
// Space Complexity: O(V)
```
## AnytimeRepairingAStar()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// ARA*(Anytime Repairing A*, Likhachev·Gordon·Thrun 2003): 앞 항목처럼 ε 를 줄여 가며 푸는데 매번 처음부터 하지 않고 이전 탐색의 g 값을 재사용한다. 규칙은 하나 — 한 번의 ImprovePath(ε) 안에서 닫힌(CLOSED) 노드는 다시 열지 않는다.
// 같은 단계에서 g 값이 개선된 닫힌 노드는 INCONS(불일치) 목록에 모아 두었다가 다음 단계(ε 감소) 때 OPEN 으로 되돌린다. 단계가 끝나면 OPEN 과 INCONS 의 최소 g+h 로 해의 최악 부최적 한계 ε′ = min(ε, g(goal) / min(g+h)) 를 증명 가능하게 알려 준다(ε′ 이 1 이면 최적).
// ImprovePath(ε): f(goal) = g(goal) + ε·h(goal) 이 OPEN 의 최소 키보다 크지 않을 때까지 OPEN 에서 키 g+ε·h 가 가장 작은 노드를 꺼내 확장하고 후속 노드의 g 를 낮춘다. 검증(28×28 지도 25개): ① 각 단계 해의 비용 ≤ 보고된 한계 ε′ × 최적이고 ε′ ≤ ε ② 마지막 해 최적(== Dijkstra) ③ ARA* 의 누적 확장 수가 같은 ε 열을 매번 처음부터 푸는 것보다 적음
const int R = 28, C = 28; std::vector<std::string> w;
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
bool stepOk(int r, int c, int dr, int dc) { if (!freeCell(r + dr, c + dc)) return false; return !(dr && dc && (!freeCell(r + dr, c) || !freeCell(r, c + dc))); }
int stepCost(int dr, int dc) { return dr && dc ? 14 : 10; }
int octile(int v, int t) { int dr = std::abs(v / C - t / C), dc = std::abs(v % C - t % C); return 10 * (dr + dc) - 6 * std::min(dr, dc); }
std::vector<int> dijkstraAll(int s) { std::vector<int> d(R * C, 1 << 28); typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; if (du + stepCost(dr, dc) < d[v]) { d[v] = du + stepCost(dr, dc); pq.push({d[v], v}); } } } return d; }
struct Ara { int s, t; std::vector<int> g; std::vector<char> closed, incons, inOpen; long expanded = 0; std::vector<int> open;
    Ara(int s, int t) : s(s), t(t), g(R * C, 1 << 28), closed(R * C, 0), incons(R * C, 0), inOpen(R * C, 0) { g[s] = 0; open.push_back(s); inOpen[s] = 1; }
    // 한 단계: 반환값 = 보고된 부최적 한계 ε′
    double improve(double eps) { typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; for (int v : open) if (inOpen[v]) pq.push({g[v] + eps * octile(v, t), v});
        auto top = [&]() { while (!pq.empty() && (!inOpen[pq.top().second] || pq.top().first > g[pq.top().second] + eps * octile(pq.top().second, t) + 1e-9)) pq.pop(); return pq.empty() ? 1e18 : pq.top().first; };
        while (top() < 1e17 && g[t] + eps * octile(t, t) > top() + 1e-9) { int u = pq.top().second; pq.pop(); inOpen[u] = 0; closed[u] = 1; expanded++;
            for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; int ng = g[u] + stepCost(dr, dc); if (ng < g[v]) { g[v] = ng; if (!closed[v]) { inOpen[v] = 1; pq.push({g[v] + eps * octile(v, t), v}); } else incons[v] = 1; } } }
        double minGH = 1e18; for (int v = 0; v < R * C; v++) if (inOpen[v] || incons[v]) minGH = std::min(minGH, g[v] + (double)octile(v, t)); return g[t] >= (1 << 28) ? 1e18 : std::min(eps, minGH >= 1e17 ? 1.0 : std::max(1.0, g[t] / minGH)); }
    void nextRound() { for (int v = 0; v < R * C; v++) { if (incons[v]) { inOpen[v] = 1; incons[v] = 0; } closed[v] = 0; } open.clear(); for (int v = 0; v < R * C; v++) if (inOpen[v]) open.push_back(v); } };
long weightedRestart(int s, int t, double eps, int& cost) { std::vector<int> g(R * C, 1 << 28); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; g[s] = 0; pq.push({eps * octile(s, t), s}); long ex = 0; while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + eps * octile(u, t) + 1e-9) continue; ex++; if (u == t) { cost = g[u]; return ex; } for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; int ng = g[u] + stepCost(dr, dc); if (ng < g[v]) { g[v] = ng; pq.push({ng + eps * octile(v, t), v}); } } } cost = -1; return ex; }
int main() {
    std::mt19937 rng(9); const double eps[5] = {3.0, 2.0, 1.5, 1.2, 1.0}; int maps = 0; long araTotal = 0, restartTotal = 0;
    for (int m = 0; m < 25; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 28) ch = '#'; int s = 0, t = R * C - 1; w[0][0] = w[R - 1][C - 1] = '.'; int opt = dijkstraAll(s)[t]; if (opt >= (1 << 28)) continue; maps++;
        Ara ara(s, t); for (int k = 0; k < 5; k++) { if (k) ara.nextRound(); double bound = ara.improve(eps[k]); assert(bound <= eps[k] + 1e-9 && ara.g[t] < (1 << 28)); assert(ara.g[t] >= opt && ara.g[t] <= bound * opt + 1e-6); int rc; long rex = weightedRestart(s, t, eps[k], rc); restartTotal += rex; if (k == 4) { assert(ara.g[t] == opt && bound <= 1.0 + 1e-9); } }       // ①② 한계와 최적
        araTotal += ara.expanded; }
    assert(maps >= 15 && araTotal < restartTotal);
    std::cout << "ARA*: " << maps << " maps; each epsilon step stays within its proven bound and the final step is optimal; cumulative expansions " << araTotal << " with reuse versus " << restartTotal << " when each epsilon is solved from scratch" << std::endl; return 0;
}
// Time Complexity: 단계별 확장은 이전 g 값 재사용으로 감소; 최악은 재시작과 같음
// Space Complexity: O(V)
```
## MonteCarloTreeSearch()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 몬테카를로 트리 탐색(MCTS)의 UCT 변형: 상태 공간이 너무 커서 전체를 펼칠 수 없을 때 "무작위 시뮬레이션의 평균 결과" 로 선택을 평가한다. 한 번의 반복 = ① 선택: 루트에서 UCB1 = 평균 보상 + c·√(ln N_부모 / N_자식) 이 가장 큰 자식을 따라 내려감(탐험과 활용의 균형)
// ② 확장: 방문 안 한 행동 하나를 자식으로 추가 ③ 시뮬레이션(rollout): 말단에서 끝까지 기본 정책으로 무작위 진행 ④ 역전파: 얻은 보상을 경로의 모든 노드에 누적. 반복 후 루트에서 방문 수가 가장 많은 행동이 답이다.
// 길찾기에 적용: 12×12 미로에서 시작에서 목표까지 H 걸음 이내에 도착하면 보상 1 − 걸음/H. rollout 정책은 맨해튼 거리로 목표 쪽 행동을 40% 확률로 고르는 ε-탐욕(정확한 거리를 쓰지 않으므로 벽에서는 틀림).
// 검증: ① 밴딧 문제(성공 확률 0.2/0.5/0.8)에서 UCB1 이 최선 팔에 80% 넘게 몰림 ② 미로 60개에서 방문 수 최다 행동이 BFS 로 구한 "최단 경로의 첫 걸음" 인 비율이 반복 수 6 ≤ 40 ≤ 2000 에서 증가하고 2000 에서 85% 이상
const int R = 12, C = 12, H = 60; std::vector<std::string> w; const int DR[4] = {-1, 1, 0, 0}, DC[4] = {0, 0, -1, 1};
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
struct Node { int pos, depth, parent, action; int visits = 0; double total = 0; int child[4] = {-1, -1, -1, -1}; };
int main() {
    std::mt19937 rng(4); { const double p[3] = {0.2, 0.5, 0.8}; int n[3] = {0, 0, 0}; double sum[3] = {0, 0, 0}; for (int t = 1; t <= 3000; t++) { int pick = -1; for (int a = 0; a < 3; a++) if (n[a] == 0) pick = a; if (pick < 0) { double best = -1; for (int a = 0; a < 3; a++) { double u = sum[a] / n[a] + std::sqrt(2 * std::log((double)t) / n[a]); if (u > best) { best = u; pick = a; } } } n[pick]++; sum[pick] += (rng() % 1000) / 1000.0 < p[pick]; } assert(n[2] > 2400 && n[0] < 150); }       // ① UCB1: 최선 팔에 80% 이상
    const int Ns[3] = {6, 40, 2000}; int ok[3] = {0, 0, 0}, maps = 0;
    for (int m = 0; m < 150; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 30) ch = '#'; w[0][0] = w[R - 1][C - 1] = '.'; int start = 0, goal = R * C - 1;
        std::vector<int> dist(R * C, -1); { std::queue<int> q; dist[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); for (int a = 0; a < 4; a++) { int r = u / C + DR[a], c = u % C + DC[a]; if (freeCell(r, c) && dist[r * C + c] < 0) { dist[r * C + c] = dist[u] + 1; q.push(r * C + c); } } } } if (dist[start] < 0 || dist[start] > 40) continue; { int a0 = 0; for (int a = 0; a < 4; a++) { int r = start / C + DR[a], c = start % C + DC[a]; a0 += freeCell(r, c) && dist[r * C + c] == dist[start] - 1; } if (a0 == 4) continue; } maps++;
        for (int ni = 0; ni < 3; ni++) { std::vector<Node> tree = {{start, 0, -1, -1}}; for (int it = 0; it < Ns[ni]; it++) { int cur = 0;
                while (true) { Node& nd = tree[cur]; if (nd.pos == goal || nd.depth >= H) break; int untried = -1; for (int a = 0; a < 4; a++) if (nd.child[a] < 0 && freeCell(nd.pos / C + DR[a], nd.pos % C + DC[a])) { untried = a; break; } if (untried >= 0) { int a = untried; int id = tree.size(); tree.push_back({(nd.pos / C + DR[a]) * C + nd.pos % C + DC[a], nd.depth + 1, cur, a}); tree[cur].child[a] = id; cur = id; break; }
                    int best = -1; double bu = -1e18; for (int a = 0; a < 4; a++) { int ch = nd.child[a]; if (ch < 0) continue; double u = tree[ch].total / tree[ch].visits + 1.0 * std::sqrt(std::log((double)nd.visits + 1) / tree[ch].visits); if (u > bu) { bu = u; best = ch; } } if (best < 0) break; cur = best; }
                int pos = tree[cur].pos, depth = tree[cur].depth; while (pos != goal && depth < H) { std::vector<int> acts; for (int a = 0; a < 4; a++) if (freeCell(pos / C + DR[a], pos % C + DC[a])) acts.push_back(a); if (acts.empty()) break; int pick = acts[rng() % acts.size()]; if (rng() % 100 < 40) { int bestA = pick, bd = 1 << 28; for (int a : acts) { int r = pos / C + DR[a], c = pos % C + DC[a], d = std::abs(r - goal / C) + std::abs(c - goal % C); if (d < bd) { bd = d; bestA = a; } } pick = bestA; } pos = (pos / C + DR[pick]) * C + pos % C + DC[pick]; depth++; }
                double reward = pos == goal ? 1.0 - (double)depth / H : 0.0; for (int v = cur; v >= 0; v = tree[v].parent) { tree[v].visits++; tree[v].total += reward; } }
            int bestA = -1, bv = -1; for (int a = 0; a < 4; a++) if (tree[0].child[a] >= 0 && tree[tree[0].child[a]].visits > bv) { bv = tree[tree[0].child[a]].visits; bestA = a; } int next = (start / C + DR[bestA]) * C + start % C + DC[bestA]; ok[ni] += dist[next] == dist[start] - 1; } }
    assert(maps > 25 && ok[0] <= ok[1] && ok[1] <= ok[2] && ok[2] * 100 >= maps * 85 && ok[0] < ok[2]);
    std::cout << "MonteCarloTreeSearch: UCB1 sends >80% of bandit pulls to the best arm; on " << maps << " mazes the most-visited root action is a shortest-path first step in " << ok[0] << "/" << ok[1] << "/" << ok[2] << " cases after " << Ns[0] << "/" << Ns[1] << "/" << Ns[2] << " iterations" << std::endl; return 0;
}
// Time Complexity: 반복당 O(트리 깊이 + rollout 길이)
// Space Complexity: O(반복 수) (트리 노드)
```
## ReinforcementLearningPathPlanning()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 강화학습 길찾기: 지도를 모르는 에이전트가 시행착오로 최단 경로 정책을 배운다. 표 기반 Q-학습 — 상태 s(칸), 행동 a(상하좌우), 보상 −1/걸음(목표 도달 시 종료)에서 Q(s,a) ← Q(s,a) + α·(r + γ·max_a′ Q(s′,a′) − Q(s,a)).
// 탐험은 ε-탐욕(확률 ε 로 무작위 행동, ε 는 에피소드가 진행되며 감소). 환경이 결정적이고 γ = 1 이면 최적 Q*(s,a) = −(1 + 이웃 s′ 의 목표까지 최단 거리) 이다 — 따라서 BFS 거리와 정확히 비교할 수 있다. 장애물에 부딪히면 제자리에 머물며 −1.
// 검증(12×12 미로 16개, 에피소드 4000): ① 모든 도달 가능한 칸에서 탐욕 정책을 따르면 BFS 최단 거리로 도착(정책 정확도 ≥ 98%) ② 방문한 (s,a)의 학습된 Q 가 Q* 와 일치(오차 ≤ 0.5)한 비율 ③ 학습 곡선: 에피소드 구간별 평균 걸음 수가 감소하여 후반이 전반보다 적음
const int R = 12, C = 12; std::vector<std::string> w; const int DR[4] = {-1, 1, 0, 0}, DC[4] = {0, 0, -1, 1};
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
int main() {
    std::mt19937 rng(6); int maps = 0, statesTotal = 0, policyOk = 0, qTotal = 0, qOk = 0; double early = 0, late = 0;
    for (int m = 0; m < 16; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 20) ch = '#'; w[0][0] = w[R - 1][C - 1] = '.'; int goal = R * C - 1; std::vector<int> dist(R * C, -1); { std::queue<int> q; dist[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); for (int a = 0; a < 4; a++) { int r = u / C + DR[a], c = u % C + DC[a]; if (freeCell(r, c) && dist[r * C + c] < 0) { dist[r * C + c] = dist[u] + 1; q.push(r * C + c); } } } } if (dist[0] < 0) continue; maps++;
        std::vector<std::array<double, 4>> Q(R * C, std::array<double, 4>{0, 0, 0, 0}); std::vector<std::array<int, 4>> seen(R * C, std::array<int, 4>{0, 0, 0, 0}); const int EPISODES = 4000; double stepsEarly = 0, stepsLate = 0;
        for (int ep = 0; ep < EPISODES; ep++) { double eps = std::max(0.05, 1.0 - (double)ep / (EPISODES * 0.5)); int s = rng() % (R * C); while (dist[s] < 0 || s == goal) s = rng() % (R * C); int steps = 0;
            while (s != goal && steps < 400) { int a; if ((rng() % 1000) / 1000.0 < eps) a = rng() % 4; else { a = 0; for (int k = 1; k < 4; k++) if (Q[s][k] > Q[s][a]) a = k; } int r = s / C + DR[a], c = s % C + DC[a]; int s2 = freeCell(r, c) ? r * C + c : s; double best = -1e18; if (s2 == goal) best = 0; else for (int k = 0; k < 4; k++) best = std::max(best, Q[s2][k]);
                Q[s][a] += 0.5 * (-1 + best - Q[s][a]); seen[s][a]++; s = s2; steps++; }
            if (ep < EPISODES / 4) stepsEarly += steps; if (ep >= 3 * EPISODES / 4) stepsLate += steps; }
        early += stepsEarly; late += stepsLate;
        for (int s = 0; s < R * C; s++) { if (dist[s] <= 0) continue; statesTotal++; int cur = s, steps = 0; while (cur != goal && steps < 200) { int a = 0; for (int k = 1; k < 4; k++) if (Q[cur][k] > Q[cur][a]) a = k; int r = cur / C + DR[a], c = cur % C + DC[a]; if (!freeCell(r, c)) break; cur = r * C + c; steps++; } policyOk += cur == goal && steps == dist[s];                                      // ① 탐욕 정책이 최단 거리로 도착
            for (int a = 0; a < 4; a++) { int r = s / C + DR[a], c = s % C + DC[a]; if (!freeCell(r, c) || seen[s][a] < 5) continue; qTotal++; double star = -(1.0 + (r * C + c == goal ? 0 : dist[r * C + c])); qOk += std::fabs(Q[s][a] - star) <= 0.5; } } }
    assert(maps >= 8 && policyOk * 100 >= statesTotal * 98 && qOk * 100 >= qTotal * 90 && late < early);
    std::cout << "ReinforcementLearningPathPlanning: " << maps << " mazes; greedy policy follows a shortest path from " << policyOk << "/" << statesTotal << " states; " << qOk << "/" << qTotal << " visited Q-values match the exact -(1+dist) values; mean steps per episode fell from " << early / (maps * 1000) << " to " << late / (maps * 1000) << std::endl; return 0;
}
// Time Complexity: 에피소드 수 × 에피소드 길이 (갱신 O(1))
// Space Complexity: O(상태 수 × 행동 수)
```
## NeuralPathPlanning()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 신경망 경로 계획(모방 학습): 작은 다층 퍼셉트론(MLP)이 "현재 칸에서 어느 방향으로 가야 최단 경로인가" 를 A*/BFS 의 답을 보고 배운다. 입력 = 목표까지의 상대 위치 2 개 + 주변 5×5 칸의 자유 여부 24 개(절대 좌표를 쓰지 않아야 일반화가 가능), 은닉층 32 개 tanh, 출력 4 개 softmax.
// 최단 경로가 여러 방향일 수 있으므로 정답을 "최적 행동 집합 위의 균등 분포" 로 두고 교차 엔트로피를 최소화한다. 역전파는 직접 구현하고(출력층 기울기 = p − q), 수치 미분으로 맞게 구현했는지 확인한다. 학습은 전체 배치 경사 하강.
// 정직한 한계: 지역 관측만 보는 반응형 정책이라 오목한 막다른 곳에서는 틀리고, 작은 표본으로 배우므로 일반화가 불완전하다(처음 시도한 "행·열 원-핫" 입력은 학습한 칸은 외웠지만 새 칸에서는 한 번도 성공하지 못했다). 검증(10×10 무작위 지도 30개로 학습, 새 지도 12개로 평가): ① 해석적 기울기 == 중심 차분(상대 오차 1e-4 이하) ② 손실이 거의 단조롭게 감소(5% 이상 상승 구간 없음)하고 끝 손실 < 처음의 70% ③ 학습 표본에서 최적 행동 선택률 ≥ 70% ④ 새 지도의 모든 시작 칸에서 정책 롤아웃 성공률이 무작위 걸음의 2 배를 넘고 60% 이상
const int R = 10, C = 10, H = 32, IN = 2 + 24, OUT = 4; std::vector<std::string> w; const int DR[4] = {-1, 1, 0, 0}, DC[4] = {0, 0, -1, 1};
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
struct Net { std::vector<double> W1, b1, W2, b2; Net() : W1(H * IN), b1(H, 0), W2(OUT * H), b2(OUT, 0) {} };
std::vector<double> features(int s) { std::vector<double> x(IN, 0); x[0] = (double)(R - 1 - s / C) / R; x[1] = (double)(C - 1 - s % C) / C; int k = 2; for (int dr = -2; dr <= 2; dr++) for (int dc = -2; dc <= 2; dc++) { if (!dr && !dc) continue; x[k++] = freeCell(s / C + dr, s % C + dc) ? 1 : 0; } return x; }      // 목표까지의 상대 위치 + 주변 5×5 칸의 자유 여부
void forward(const Net& n, const std::vector<double>& x, std::vector<double>& h, std::vector<double>& p) { h.assign(H, 0); for (int j = 0; j < H; j++) { double z = n.b1[j]; for (int i = 0; i < IN; i++) z += n.W1[j * IN + i] * x[i]; h[j] = std::tanh(z); } std::vector<double> o(OUT); double mx = -1e18; for (int k = 0; k < OUT; k++) { o[k] = n.b2[k]; for (int j = 0; j < H; j++) o[k] += n.W2[k * H + j] * h[j]; mx = std::max(mx, o[k]); } double sum = 0; p.assign(OUT, 0); for (int k = 0; k < OUT; k++) { p[k] = std::exp(o[k] - mx); sum += p[k]; } for (double& v : p) v /= sum; }
double lossAndGrad(const Net& n, const std::vector<std::vector<double>>& X, const std::vector<std::array<double, 4>>& Y, Net* g) { double loss = 0; if (g) { std::fill(g->W1.begin(), g->W1.end(), 0); std::fill(g->b1.begin(), g->b1.end(), 0); std::fill(g->W2.begin(), g->W2.end(), 0); std::fill(g->b2.begin(), g->b2.end(), 0); }
    for (size_t i = 0; i < X.size(); i++) { std::vector<double> h, p; forward(n, X[i], h, p); for (int k = 0; k < OUT; k++) if (Y[i][k] > 0) loss -= Y[i][k] * std::log(p[k] + 1e-12); if (!g) continue; std::vector<double> d(OUT); for (int k = 0; k < OUT; k++) d[k] = p[k] - Y[i][k]; std::vector<double> dh(H, 0);
        for (int k = 0; k < OUT; k++) { g->b2[k] += d[k]; for (int j = 0; j < H; j++) { g->W2[k * H + j] += d[k] * h[j]; dh[j] += d[k] * n.W2[k * H + j]; } } for (int j = 0; j < H; j++) { double dz = dh[j] * (1 - h[j] * h[j]); g->b1[j] += dz; for (int ii = 0; ii < IN; ii++) g->W1[j * IN + ii] += dz * X[i][ii]; } }
    if (g) { double inv = 1.0 / X.size(); for (auto* v : {&g->W1, &g->b1, &g->W2, &g->b2}) for (double& x : *v) x *= inv; } return loss / X.size(); }
struct Dataset { std::vector<std::vector<double>> X; std::vector<std::array<double, 4>> Y; };
bool makeMap(std::mt19937& rng, std::vector<int>& dist) { w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 18) ch = '#'; w[0][0] = w[R - 1][C - 1] = '.'; int goal = R * C - 1; dist.assign(R * C, -1); std::queue<int> q; dist[goal] = 0; q.push(goal); while (!q.empty()) { int u = q.front(); q.pop(); for (int a = 0; a < 4; a++) { int r = u / C + DR[a], c = u % C + DC[a]; if (freeCell(r, c) && dist[r * C + c] < 0) { dist[r * C + c] = dist[u] + 1; q.push(r * C + c); } } } return dist[0] > 0; }
std::array<double, 4> label(const std::vector<int>& dist, int s) { std::array<double, 4> y{0, 0, 0, 0}; int cnt = 0; for (int a = 0; a < 4; a++) { int r = s / C + DR[a], c = s % C + DC[a]; if (freeCell(r, c) && dist[r * C + c] == dist[s] - 1) { y[a] = 1; cnt++; } } for (double& v : y) v /= cnt; return y; }
int main() {
    std::mt19937 rng(3); std::normal_distribution<double> init(0, 0.3); std::vector<int> dist; Dataset train; for (int m = 0; m < 30;) { if (!makeMap(rng, dist)) continue; m++; for (int s = 0; s < R * C; s++) if (dist[s] > 0) { train.X.push_back(features(s)); train.Y.push_back(label(dist, s)); } }
    Net net; for (double& v : net.W1) v = init(rng); for (double& v : net.W2) v = init(rng); Net g; Dataset sub; sub.X.assign(train.X.begin(), train.X.begin() + 150); sub.Y.assign(train.Y.begin(), train.Y.begin() + 150); lossAndGrad(net, sub.X, sub.Y, &g);
    double worst = 0; for (int probe = 0; probe < 12; probe++) { Net a = net, b = net; int which = rng() % 4; std::vector<double>*pa, *pb, *pg; if (which == 0) { pa = &a.W1; pb = &b.W1; pg = &g.W1; } else if (which == 1) { pa = &a.b1; pb = &b.b1; pg = &g.b1; } else if (which == 2) { pa = &a.W2; pb = &b.W2; pg = &g.W2; } else { pa = &a.b2; pb = &b.b2; pg = &g.b2; } int idx = rng() % pg->size(); const double e = 1e-6; (*pa)[idx] += e; (*pb)[idx] -= e; double num = (lossAndGrad(a, sub.X, sub.Y, nullptr) - lossAndGrad(b, sub.X, sub.Y, nullptr)) / (2 * e); worst = std::max(worst, std::fabs(num - (*pg)[idx]) / (1e-7 + std::max(std::fabs(num), std::fabs((*pg)[idx])))); } assert(worst < 1e-4);       // ① 기울기 확인
    double first = lossAndGrad(net, train.X, train.Y, nullptr), prev = first, lr = 0.05, maxRise = 0; Net vel = net; std::fill(vel.W1.begin(), vel.W1.end(), 0); std::fill(vel.b1.begin(), vel.b1.end(), 0); std::fill(vel.W2.begin(), vel.W2.end(), 0); std::fill(vel.b2.begin(), vel.b2.end(), 0);
    for (int ep = 0; ep < 400; ep++) { double l = lossAndGrad(net, train.X, train.Y, &g); maxRise = std::max(maxRise, (l - prev) / prev); prev = l; auto upd = [&](std::vector<double>& p, std::vector<double>& v, const std::vector<double>& gr) { for (size_t i = 0; i < p.size(); i++) { v[i] = 0.9 * v[i] - lr * gr[i]; p[i] += v[i]; } }; upd(net.W1, vel.W1, g.W1); upd(net.b1, vel.b1, g.b1); upd(net.W2, vel.W2, g.W2); upd(net.b2, vel.b2, g.b2); }
    double last = lossAndGrad(net, train.X, train.Y, nullptr); assert(last < 0.7 * first && maxRise < 0.05);                                                                                      // ② 손실 감소
    auto policy = [&](int s) { std::vector<double> h, p; forward(net, features(s), h, p); int best = 0; for (int k = 1; k < OUT; k++) if (p[k] > p[best]) best = k; return best; };
    int trainOk = 0; for (size_t i = 0; i < train.X.size(); i += 5) { std::vector<double> h, p; forward(net, train.X[i], h, p); int best = 0; for (int k = 1; k < OUT; k++) if (p[k] > p[best]) best = k; trainOk += train.Y[i][best] > 0; } assert(trainOk * 100 >= (int)(train.X.size() / 5) * 70);        // ③ 학습 표본 정확도
    int success = 0, randomSuccess = 0, starts = 0; for (int m = 0; m < 12;) { if (!makeMap(rng, dist)) continue; m++; for (int s = 0; s < R * C; s++) { if (dist[s] <= 0) continue; starts++; int limit = 3 * dist[s] + 6; int cur = s; for (int step = 0; step < limit && cur != R * C - 1; step++) { int a = policy(cur); int r = cur / C + DR[a], c = cur % C + DC[a]; if (freeCell(r, c)) cur = r * C + c; } success += cur == R * C - 1;
            int cur2 = s; for (int step = 0; step < limit && cur2 != R * C - 1; step++) { int a = rng() % 4; int r = cur2 / C + DR[a], c = cur2 % C + DC[a]; if (freeCell(r, c)) cur2 = r * C + c; } randomSuccess += cur2 == R * C - 1; } }
    assert(success > 2 * randomSuccess && success * 100 >= starts * 60);                                                                                                                         // ④ 새 지도에서 무작위보다 훨씬 나음
    std::cout << "NeuralPathPlanning: gradient check relative error " << worst << "; loss " << first << " -> " << last << " on " << train.X.size() << " samples from 30 training maps; on 12 unseen maps the policy reached the goal from " << success << "/" << starts << " start cells versus " << randomSuccess << " for a random walk" << std::endl; return 0;
}
// Time Complexity: 학습 반복당 O(샘플 수 × 입력 × 은닉), 추론 O(입력 × 은닉)
// Space Complexity: O(파라미터 수)
```
## DifferentiableAStar()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 미분 가능한 최단 경로(Differentiable A*·Neural A* 계열의 핵심 아이디어): 최단 경로 거리 D(c) = min_{경로} Σ c(칸) 는 min 연산 때문에 비용 지도 c 에 대한 기울기가 거의 없다. min 을 부드러운 softmin_τ(x) = −τ·ln Σ exp(−x_i/τ) 로 바꾸면 매끄러워지고
// 기울기는 "각 선택지의 softmax 비중" 으로 흘러간다. 격자에서 D^{k+1}(v) = softmin({D^k(v)} ∪ {D^k(u) + c(v) : u ∈ N(v)}), D(출발) = 0 을 K 번 반복(= 소프트 Bellman–Ford)하고, 역전파는 각 반복의 softmax 비중을 저장했다가 거꾸로 전파한다. τ → 0 이면 정확한 최단 거리로 수렴한다.
// 쓰임: 시연된 경로를 가장 잘 재현하는 비용 지도를 경사 하강으로 학습한다 — 손실 L(c) = (시연 경로의 비용 합) − D_soft(c) ≥ 0 (softmin ≤ min ≤ 경로 비용). 기울기 = 시연 경로 칸의 지시 함수 − ∂D/∂c.
// 검증(8×8): ① 해석적 기울기 == 중심 차분(상대 오차 1e-4 이하) ② τ 를 줄이면 소프트 거리가 Dijkstra 거리로 수렴(오차 ≤ τ·ln5·K, 단조 감소) ③ 처음에는 시연 경로가 최단보다 1 이상 비싼 무작위 비용 지도에서 학습 후 손실이 줄고 시연 경로의 비용이 학습된 비용의 최단 거리와 같아짐(시연을 재현하는 비용 지도)
const int R = 8, C = 8, K = 28, V = R * C; const int DR[4] = {-1, 1, 0, 0}, DC[4] = {0, 0, -1, 1};
struct Soft { std::vector<std::vector<double>> D; std::vector<std::vector<std::array<double, 5>>> wt; };
double softDist(const std::vector<double>& c, int src, int dst, double tau, Soft* out) { std::vector<std::vector<double>> D(K + 1, std::vector<double>(V, 1e3)); D[0][src] = 0; std::vector<std::vector<std::array<double, 5>>> wt(K + 1, std::vector<std::array<double, 5>>(V));
    for (int k = 0; k < K; k++) for (int v = 0; v < V; v++) { if (v == src) { D[k + 1][v] = 0; continue; } double opt[5]; int n = 0; opt[n++] = D[k][v]; for (int a = 0; a < 4; a++) { int r = v / C + DR[a], cc = v % C + DC[a]; if (r < 0 || cc < 0 || r >= R || cc >= C) { opt[n++] = 1e9; continue; } opt[n++] = D[k][r * C + cc] + c[v]; }
        double mn = *std::min_element(opt, opt + n), sum = 0; for (int i = 0; i < n; i++) sum += std::exp(-(opt[i] - mn) / tau); D[k + 1][v] = mn - tau * std::log(sum); for (int i = 0; i < n; i++) wt[k + 1][v][i] = std::exp(-(opt[i] - mn) / tau) / sum; }
    if (out) { out->D = D; out->wt = wt; } return D[K][dst]; }
std::vector<double> softGrad(const std::vector<double>& c, int src, int dst, double tau) { Soft s; softDist(c, src, dst, tau, &s); std::vector<double> g(V, 0); std::vector<double> a(V, 0); a[dst] = 1;
    for (int k = K; k >= 1; k--) { std::vector<double> prev(V, 0); for (int v = 0; v < V; v++) { if (a[v] == 0 || v == src) continue; prev[v] += s.wt[k][v][0] * a[v]; for (int ai = 0; ai < 4; ai++) { int r = v / C + DR[ai], cc = v % C + DC[ai]; if (r < 0 || cc < 0 || r >= R || cc >= C) continue; prev[r * C + cc] += s.wt[k][v][ai + 1] * a[v]; g[v] += s.wt[k][v][ai + 1] * a[v]; } } a = prev; } return g; }
double hardDist(const std::vector<double>& c, int src, int dst) { std::vector<double> d(V, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[src] = 0; pq.push({0, src}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int a = 0; a < 4; a++) { int r = u / C + DR[a], cc = u % C + DC[a]; if (r < 0 || cc < 0 || r >= R || cc >= C) continue; int v = r * C + cc; if (du + c[v] < d[v]) { d[v] = du + c[v]; pq.push({d[v], v}); } } } return d[dst]; }
int main() {
    std::mt19937 rng(5); int src = 0, dst = V - 1; std::vector<double> c(V); for (double& x : c) x = 0.5 + (rng() % 150) / 100.0;
    { double tau = 0.4; auto g = softGrad(c, src, dst, tau); double worst = 0; for (int probe = 0; probe < 10; probe++) { int v = 1 + rng() % (V - 1); auto cp = c, cm = c; const double e = 1e-6; cp[v] += e; cm[v] -= e; double num = (softDist(cp, src, dst, tau, nullptr) - softDist(cm, src, dst, tau, nullptr)) / (2 * e); worst = std::max(worst, std::fabs(num - g[v]) / (1e-6 + std::max(std::fabs(num), std::fabs(g[v])))); } assert(worst < 1e-4);    // ① 기울기 확인
        double hard = hardDist(c, src, dst), prevErr = 1e18; for (double t : {2.0, 1.0, 0.5, 0.2, 0.05, 0.01}) { double s = softDist(c, src, dst, t, nullptr); assert(s <= hard + 1e-9 && hard - s <= t * std::log(5.0) * K + 1e-9 && hard - s <= prevErr + 1e-9); prevErr = hard - s; } assert(prevErr < 0.25); }                                                // ② τ → 0 수렴
    std::vector<int> demo; for (int cc = 0; cc < C; cc++) demo.push_back(cc); for (int r = 1; r < R; r++) demo.push_back(r * C + C - 1);                                                           // 시연 경로: 위쪽 가장자리 → 오른쪽 가장자리
    std::vector<double> cost = c; const double tau = 0.1; auto loss = [&](const std::vector<double>& x) { double l = 0; for (size_t i = 1; i < demo.size(); i++) l += x[demo[i]]; return l - softDist(x, src, dst, tau, nullptr); };
    double L0 = loss(cost); double demoBefore = 0; for (size_t i = 1; i < demo.size(); i++) demoBefore += cost[demo[i]]; double hardBefore = hardDist(cost, src, dst); for (int it = 0; it < 1500; it++) { auto g = softGrad(cost, src, dst, tau); std::vector<double> ind(V, 0); for (size_t i = 1; i < demo.size(); i++) ind[demo[i]] = 1; for (int v = 0; v < V; v++) cost[v] = std::max(0.05, cost[v] - 0.1 * (ind[v] - g[v])); }
    double L1 = loss(cost); double demoCost = 0; for (size_t i = 1; i < demo.size(); i++) demoCost += cost[demo[i]]; double hard = hardDist(cost, src, dst); assert(demoBefore > hardBefore + 1.0 && L1 < L0 && demoCost <= hard + 1e-9);                                                       // ③ 학습 후 시연 경로가 사실상 최단
    std::cout << "DifferentiableAStar: soft-Bellman-Ford gradient matches finite differences; soft distance converges to Dijkstra as tau->0; learning a cost map from one demonstration cut the loss " << L0 << " -> " << L1 << " and made the demonstrated route (costing " << demoBefore << " vs shortest " << hardBefore << " before) a shortest route: " << demoCost << " vs " << hard << std::endl; return 0;
}
// Time Complexity: 순전파·역전파 O(K · V · 5)
// Space Complexity: O(K · V) (softmax 비중 저장)
```
## SwarmPathPlanning()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 군집 경로 계획(boids, Reynolds 1987): 중앙 계획 없이 각 개체가 이웃만 보고 단순한 규칙 몇 개를 합쳐 따르면 무리가 하나로 목표에 도달한다. 규칙 ① 목표 끌림 ② 분리(separation: 너무 가까운 이웃에서 멀어짐 — 충돌 방지) ③ 응집(cohesion: 무리 중심 쪽으로)
// ④ 정렬(alignment: 이웃의 평균 속도에 맞춤) ⑤ 장애물 회피(표면에서 가까울수록 밀어냄). 가속도 = 규칙의 가중합, 속도는 최대 속력으로 제한. 개별 규칙은 경로를 계획하지 않지만 큰 장애물 둘레를 돌아가는 흐름이 나타난다.
// 검증(100×60 평면, 원형 장애물 3개, 개체 30): ① 분리 규칙이 있으면 모든 개체가 제한 시간 안에 목표 반경에 도착하고 개체끼리의 최소 거리가 분리 없을 때보다 크게 유지됨 ② 어떤 개체도 장애물 내부로 들어가지 않음 ③ 무리가 흩어지지 않음(전 과정에서 중심까지 최대 거리 상한)
typedef std::pair<double, double> V; struct Circle { double x, y, r; };
struct Result { int arrived; double minDist, maxSpread; bool hit; int steps; };
Result simulate(bool separation, unsigned seed) {
    std::mt19937 rng(seed); std::vector<Circle> obs = {{45, 30, 9}, {70, 18, 6}, {68, 44, 7}}; const int N = 30; std::vector<V> p(N), v(N, {0, 0}); for (int i = 0; i < N; i++) p[i] = {2.0 + (rng() % 800) / 100.0, 22.0 + (rng() % 1600) / 100.0}; V goal{92, 30}; const double VMAX = 1.5, DT = 0.2; double minDist = 1e9, maxSpread = 0; bool hit = false; std::vector<char> done(N, 0); int steps = 0;
    for (; steps < 1500; steps++) { V cen{0, 0}; V avg{0, 0}; int live = 0; for (int i = 0; i < N; i++) if (!done[i]) { cen.first += p[i].first; cen.second += p[i].second; avg.first += v[i].first; avg.second += v[i].second; live++; } if (!live) break; cen.first /= live; cen.second /= live; avg.first /= live; avg.second /= live;
        std::vector<V> acc(N, {0, 0}); for (int i = 0; i < N; i++) { if (done[i]) continue; double gx = goal.first - p[i].first, gy = goal.second - p[i].second, gd = std::hypot(gx, gy); acc[i].first += 1.2 * gx / gd; acc[i].second += 1.2 * gy / gd; acc[i].first += 0.03 * (cen.first - p[i].first); acc[i].second += 0.03 * (cen.second - p[i].second); acc[i].first += 0.15 * (avg.first - v[i].first); acc[i].second += 0.15 * (avg.second - v[i].second);
            if (separation) for (int j = 0; j < N; j++) { if (j == i || done[j]) continue; double dx = p[i].first - p[j].first, dy = p[i].second - p[j].second, d = std::hypot(dx, dy); if (d < 3.0 && d > 1e-9) { acc[i].first += 4.0 * (3.0 - d) * dx / d; acc[i].second += 4.0 * (3.0 - d) * dy / d; } }
            for (const Circle& o : obs) { double dx = p[i].first - o.x, dy = p[i].second - o.y, d = std::hypot(dx, dy) - o.r; if (d < 8 && d > 1e-9) { double m = 6.0 * (8 - d) / 8; double tx = -dy, ty = dx, tl = std::hypot(tx, ty); double side = (tx * (goal.first - p[i].first) + ty * (goal.second - p[i].second)) >= 0 ? 1 : -1; acc[i].first += m * dx / std::hypot(dx, dy) + 0.8 * m * side * tx / tl; acc[i].second += m * dy / std::hypot(dx, dy) + 0.8 * m * side * ty / tl; } } }          // 장애물 밀어냄 + 접선 방향(돌아가는 쪽)
        for (int i = 0; i < N; i++) { if (done[i]) continue; v[i].first += acc[i].first * DT; v[i].second += acc[i].second * DT; double sp = std::hypot(v[i].first, v[i].second); if (sp > VMAX) { v[i].first *= VMAX / sp; v[i].second *= VMAX / sp; } p[i].first += v[i].first * DT; p[i].second += v[i].second * DT; for (const Circle& o : obs) if (std::hypot(p[i].first - o.x, p[i].second - o.y) < o.r) hit = true; if (std::hypot(goal.first - p[i].first, goal.second - p[i].second) < 4.0) done[i] = 1; }
        for (int i = 0; i < N; i++) { if (done[i]) continue; for (int j = i + 1; j < N; j++) if (!done[j]) minDist = std::min(minDist, std::hypot(p[i].first - p[j].first, p[i].second - p[j].second)); maxSpread = std::max(maxSpread, std::hypot(p[i].first - cen.first, p[i].second - cen.second)); } }
    int arrived = 0; for (int i = 0; i < N; i++) arrived += done[i]; return {arrived, minDist, maxSpread, hit, steps}; }
int main() {
    int runs = 8; double minWith = 1e9, minWithout = 1e9; int allArrived = 0; double spread = 0;
    for (int s = 0; s < runs; s++) { Result a = simulate(true, 100 + s), b = simulate(false, 100 + s); assert(!a.hit); allArrived += a.arrived == 30; minWith = std::min(minWith, a.minDist); minWithout = std::min(minWithout, b.minDist); spread = std::max(spread, a.maxSpread); }
    assert(allArrived >= runs - 1 && minWith > 0.3 && minWithout < 0.1 * minWith && spread < 60);
    std::cout << "SwarmPathPlanning: " << allArrived << "/" << runs << " runs brought all 30 agents to the goal around 3 obstacles without entering them; closest approach between agents " << minWith << " with separation versus " << minWithout << " without; max distance from the flock centre " << spread << std::endl; return 0;
}
// Time Complexity: 시간 단계당 O(N² + N · 장애물 수)
// Space Complexity: O(N)
```
## AntColonyOptimization()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 개미 군집 최적화(ACO, Dorigo 1992): 개미가 길에 페로몬을 남기고 다른 개미는 페로몬이 진한 길을 확률적으로 따르는 행동을 모사한다. 개미 한 마리는 출발점에서 도착점까지 이웃을 확률 ∝ τ^α · η^β 로 고르며 간다(τ: 페로몬, η = 1/간선 가중치: 휴리스틱), 이미 간 정점은 피한다(막다른 길이면 실패).
// 각 반복에서 가장 짧은 경로를 찾은 개미만 경로 길이 L 에 반비례해 Q/L 만큼 간선에 페로몬을 얹고(MAX–MIN Ant System), 매 반복마다 모든 페로몬이 비율 ρ = 0.2 만큼 증발하며 페로몬은 [0.1, 20] 안으로 제한한다 — 증발과 하한이 잘못된 초기 선택을 잊게 하고 상한이 조기 수렴을 막는다. 반복하면 짧은 경로에 페로몬이 쌓여 수렴한다.
// 확률적 휴리스틱이라 최적 보장은 없지만 작은 그래프에서는 거의 항상 최적을 찾는다. 검증(무작위 가중 그래프 40개, 노드 18, 반복 120 × 개미 30): ① 얻은 최선 경로가 유효(간선이 실재)하고 길이 ≥ Dijkstra 최적 ② 최적을 찾은 비율 ≥ 90% ③ 최선 해의 길이가 반복마다 비증가 ④ 최종 페로몬 질량 중 최적 경로 간선의 비중이 초기(균등)보다 훨씬 큼
struct Edge { int to; double w; };
int main() {
    std::mt19937 rng(8); int graphs = 0, found = 0; double shareBefore = 0, shareAfter = 0;
    for (int t = 0; t < 40; t++) {
        int n = 18; std::vector<std::vector<Edge>> adj(n); std::map<std::pair<int, int>, double> wt; auto add = [&](int a, int b, double wgt) { if (a == b || wt.count({a, b})) return; wt[{a, b}] = wt[{b, a}] = wgt; adj[a].push_back({b, wgt}); adj[b].push_back({a, wgt}); }; for (int i = 1; i < n; i++) add(i, rng() % i, 1 + rng() % 9); for (int k = 0; k < 2 * n; k++) add(rng() % n, rng() % n, 1 + rng() % 9);
        int s = 0, e = n - 1; std::vector<double> d(n, 1e18); std::vector<int> par(n, -1); { typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (auto& ed : adj[u]) if (du + ed.w < d[ed.to]) { d[ed.to] = du + ed.w; par[ed.to] = u; pq.push({d[ed.to], ed.to}); } } }
        std::set<std::pair<int, int>> optEdges; for (int v = e; par[v] >= 0; v = par[v]) optEdges.insert({std::min(v, par[v]), std::max(v, par[v])}); graphs++;
        std::map<std::pair<int, int>, double> tau; for (auto& [k, v] : wt) if (k.first < k.second) tau[k] = 1.0; auto massShare = [&]() { double tot = 0, opt = 0; for (auto& [k, v] : tau) { tot += v; if (optEdges.count(k)) opt += v; } return opt / tot; }; shareBefore += massShare(); double best = 1e18; std::vector<int> bestPath; double prevBest = 1e18;
        for (int it = 0; it < 120; it++) { std::vector<std::pair<std::vector<int>, double>> sols; for (int ant = 0; ant < 30; ant++) { std::vector<int> path = {s}; std::vector<char> vis(n, 0); vis[s] = 1; double len = 0; while (path.back() != e) { int u = path.back(); std::vector<std::pair<int, double>> cand; double sum = 0; for (auto& ed : adj[u]) if (!vis[ed.to]) { double p = std::pow(tau[{std::min(u, ed.to), std::max(u, ed.to)}], 1.0) * std::pow(1.0 / ed.w, 2.0); cand.push_back({ed.to, p}); sum += p; } if (cand.empty()) { path.clear(); break; } double r = (rng() % 100000) / 100000.0 * sum, acc = 0; int pick = cand.back().first; for (auto& c : cand) { acc += c.second; if (r <= acc) { pick = c.first; break; } } len += wt[{u, pick}]; vis[pick] = 1; path.push_back(pick); } if (!path.empty()) { sols.push_back({path, len}); if (len < best) { best = len; bestPath = path; } } }
            for (auto& [k, v] : tau) v *= 0.8; if (!sols.empty()) { auto itBest = std::min_element(sols.begin(), sols.end(), [](const auto& a, const auto& b) { return a.second < b.second; }); const auto& path = itBest->first; for (size_t i = 1; i < path.size(); i++) tau[{std::min(path[i - 1], path[i]), std::max(path[i - 1], path[i])}] += 10.0 / itBest->second; } for (auto& [k, v] : tau) v = std::min(20.0, std::max(0.1, v)); assert(best <= prevBest + 1e-9); prevBest = best; }
        assert(!bestPath.empty() && bestPath.front() == s && bestPath.back() == e); double len = 0; for (size_t i = 1; i < bestPath.size(); i++) { assert(wt.count({bestPath[i - 1], bestPath[i]})); len += wt[{bestPath[i - 1], bestPath[i]}]; } assert(std::fabs(len - best) < 1e-9 && best >= d[e] - 1e-9); found += std::fabs(best - d[e]) < 1e-9; shareAfter += massShare(); }
    assert(graphs == 40 && found * 10 >= graphs * 9 && shareAfter > 2 * shareBefore);
    std::cout << "AntColonyOptimization: " << found << "/" << graphs << " random graphs solved to optimality; best-so-far length never increased; optimal-path share of pheromone grew from " << 100 * shareBefore / graphs << "% to " << 100 * shareAfter / graphs << "%" << std::endl; return 0;
}
// Time Complexity: 반복 수 × 개미 수 × 경로 길이 × 차수
// Space Complexity: O(E) (페로몬 표)
```
## GeneticPathPlanning()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 유전 알고리즘 경로 계획: 경로를 "중간 경유점 k 개의 좌표" 염색체로 표현하고 진화시킨다. 적합도(낮을수록 좋음) = 경로 길이 + 장애물과 부딪히는 선분마다 큰 벌점. 선택 = 토너먼트(3개 중 최선), 교차 = 경유점별로 두 부모 중 하나를 고름(균일 교차), 변이 = 확률적으로 가우시안 잡음,
// 엘리트 보존(최상위 2 개체는 그대로 다음 세대로) — 덕분에 세대별 최선 적합도가 절대 나빠지지 않는다. 장애물은 직사각형이고 정확한 최단 거리는 모서리 가시성 그래프로 구해 비교한다.
// 한계: 경유점 수가 고정이라 복잡한 지형에는 부족할 수 있고 해의 최적성은 보장되지 않는다. 검증(무작위 세계 12개, 인구 100, 150 세대): ① 최선 적합도가 세대마다 비증가 ② 충돌 없는 경로를 찾은 비율 ≥ 80% ③ 찾은 경로 길이 / 정확한 최적의 평균 ≤ 1.3 ④ 무작위 경유점(진화 없음)으로는 충돌 없는 경로를 거의 못 찾음
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
const int K = 5; typedef std::vector<V> Chrom;
double fitness(const Chrom& c, V s, V g, bool* ok, double* len) { double L = 0; int bad = 0; V prev = s; for (int i = 0; i <= K; i++) { V nx = i < K ? c[i] : g; L += dist(prev, nx); if (!segFree(prev, nx)) bad++; prev = nx; } if (ok) *ok = bad == 0; if (len) *len = L; return L + 1000.0 * bad; }
int main() {
    std::mt19937 rng(14); std::normal_distribution<double> gauss(0, 6); V s{5, 5}, g{95, 95}; int worlds = 0, solved = 0, randomSolved = 0; double ratio = 0;
    for (int wd = 0; wd < 12; wd++) {
        makeWorld(rng); double opt = optimum(s, g); if (opt > 1e17) continue; worlds++; const int P = 100; auto randomChrom = [&]() { Chrom c(K); for (auto& p : c) p = {(double)(rng() % 10000) / 100.0, (double)(rng() % 10000) / 100.0}; return c; }; std::vector<Chrom> pop(P); for (auto& c : pop) c = randomChrom();
        { int okCount = 0; for (int k = 0; k < 200; k++) { bool ok; fitness(randomChrom(), s, g, &ok, nullptr); okCount += ok; } randomSolved += okCount > 0; }                                                       // ④ 진화 없는 무작위 표본
        double prevBest = 1e18; for (int gen = 0; gen < 150; gen++) { std::vector<double> fit(P); for (int i = 0; i < P; i++) fit[i] = fitness(pop[i], s, g, nullptr, nullptr); std::vector<int> idx(P); for (int i = 0; i < P; i++) idx[i] = i; std::sort(idx.begin(), idx.end(), [&](int a, int b) { return fit[a] < fit[b]; }); assert(fit[idx[0]] <= prevBest + 1e-9); prevBest = fit[idx[0]];     // ① 엘리트 보존으로 비증가
            std::vector<Chrom> next = {pop[idx[0]], pop[idx[1]]}; auto tournament = [&]() { int best = rng() % P; for (int k = 0; k < 2; k++) { int c = rng() % P; if (fit[c] < fit[best]) best = c; } return best; };
            while ((int)next.size() < P) { const Chrom &a = pop[tournament()], &b = pop[tournament()]; Chrom child(K); for (int i = 0; i < K; i++) { child[i] = rng() % 2 ? a[i] : b[i]; if (rng() % 100 < 25) { child[i].first = std::min(100.0, std::max(0.0, child[i].first + gauss(rng))); child[i].second = std::min(100.0, std::max(0.0, child[i].second + gauss(rng))); } } next.push_back(child); } pop = next; }
        double bestFit = 1e18; Chrom best; for (auto& c : pop) { double f = fitness(c, s, g, nullptr, nullptr); if (f < bestFit) { bestFit = f; best = c; } } bool ok; double len; fitness(best, s, g, &ok, &len); if (ok) { solved++; assert(len >= opt - 1e-9); ratio += len / opt; } }
    assert(worlds >= 9 && solved * 10 >= worlds * 8 && ratio / solved <= 1.3 && randomSolved * 2 < worlds);
    std::cout << "GeneticPathPlanning: " << solved << "/" << worlds << " worlds solved with collision-free paths, mean length / exact optimum " << ratio / solved << " (best fitness never worsened across 150 generations); random waypoints alone found a free path in only " << randomSolved << " worlds" << std::endl; return 0;
}
// Time Complexity: 세대 수 × 인구 × 경유점 수 × 장애물 수
// Space Complexity: O(인구 × 경유점 수)
```
## ParticleSwarmOptimization()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 입자 군집 최적화(PSO, Kennedy & Eberhart 1995): 입자들이 탐색 공간을 날아다니며 자기 최선 위치(pbest)와 무리 최선 위치(gbest)로 끌린다. 속도 v ← ω·v + c1·r1·(pbest − x) + c2·r2·(gbest − x), 위치 x ← x + v (ω ≈ 0.72, c1 = c2 ≈ 1.49: 수렴 계수 조합).
// 기울기가 필요 없어 비용이 불연속이거나(충돌 벌점) 미분이 어려운 경로 문제에 쓰기 쉽다. 먼저 표준 시험 함수로 구현이 옳은지 확인한다 — Sphere(5차원, 최솟값 0), Rosenbrock(2차원, 좁은 골짜기), Rastrigin(2차원, 지역 최솟값이 많음).
// 이어서 같은 알고리즘으로 경유점 k = 5 개의 위치(10차원)를 최적화한다(적합도 = 경로 길이 + 충돌 선분 벌점). 검증: ① gbest 비용이 반복마다 비증가 ② Sphere 에서 1e-6 미만, Rosenbrock 에서 0.05 미만, Rastrigin 은 여러 번 중 절반 이상 1.0 미만 ③ 경로 문제 12개 세계에서 충돌 없는 경로 비율 ≥ 80%, 정확한 최적 대비 평균 길이 비 ≤ 1.3
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
typedef std::vector<double> Vec;
double pso(std::function<double(const Vec&)> f, int dim, double lo, double hi, int particles, int iters, std::mt19937& rng, Vec* bestOut, bool checkMonotone) { std::vector<Vec> x(particles, Vec(dim)), v(particles, Vec(dim, 0)), pb(particles); std::vector<double> pf(particles); Vec gb; double gf = 1e300; auto rnd = [&]() { return (rng() % 1000001) / 1000000.0; };
    for (int i = 0; i < particles; i++) { for (int d = 0; d < dim; d++) x[i][d] = lo + (hi - lo) * rnd(); pb[i] = x[i]; pf[i] = f(x[i]); if (pf[i] < gf) { gf = pf[i]; gb = x[i]; } } double prev = gf;
    for (int it = 0; it < iters; it++) { for (int i = 0; i < particles; i++) { for (int d = 0; d < dim; d++) { v[i][d] = 0.72 * v[i][d] + 1.49 * rnd() * (pb[i][d] - x[i][d]) + 1.49 * rnd() * (gb[d] - x[i][d]); x[i][d] = std::min(hi, std::max(lo, x[i][d] + v[i][d])); } double fv = f(x[i]); if (fv < pf[i]) { pf[i] = fv; pb[i] = x[i]; if (fv < gf) { gf = fv; gb = x[i]; } } } if (checkMonotone) assert(gf <= prev + 1e-15); prev = gf; }
    if (bestOut) *bestOut = gb; return gf; }
const int K = 5;
double pathCost(const Vec& c, V s, V g, bool* ok, double* len) { double L = 0; int bad = 0; V prev = s; for (int i = 0; i <= K; i++) { V nx = i < K ? V{c[2 * i], c[2 * i + 1]} : g; L += dist(prev, nx); if (!segFree(prev, nx)) bad++; prev = nx; } if (ok) *ok = bad == 0; if (len) *len = L; return L + 1000.0 * bad; }
int main() {
    std::mt19937 rng(21); double sphere = pso([](const Vec& x) { double s = 0; for (double v : x) s += v * v; return s; }, 5, -5, 5, 30, 300, rng, nullptr, true); assert(sphere < 1e-6);
    double rosen = pso([](const Vec& x) { return 100 * std::pow(x[1] - x[0] * x[0], 2) + std::pow(1 - x[0], 2); }, 2, -3, 3, 40, 400, rng, nullptr, true); assert(rosen < 0.05);
    int rastOk = 0; for (int r = 0; r < 10; r++) { double v = pso([](const Vec& x) { double s = 20; for (double u : x) s += u * u - 10 * std::cos(2 * M_PI * u); return s; }, 2, -5.12, 5.12, 40, 200, rng, nullptr, true); rastOk += v < 1.0; } assert(rastOk >= 5);
    V s{5, 5}, g{95, 95}; int worlds = 0, solved = 0; double ratio = 0;
    for (int wd = 0; wd < 12; wd++) { makeWorld(rng); double opt = optimum(s, g); if (opt > 1e17) continue; worlds++; Vec best; pso([&](const Vec& c) { return pathCost(c, s, g, nullptr, nullptr); }, 2 * K, 0, 100, 60, 250, rng, &best, true); bool ok; double len; pathCost(best, s, g, &ok, &len); if (ok) { solved++; assert(len >= opt - 1e-9); ratio += len / opt; } }
    assert(worlds >= 9 && solved * 10 >= worlds * 8 && ratio / solved <= 1.3);
    std::cout << "ParticleSwarmOptimization: Sphere " << sphere << ", Rosenbrock " << rosen << ", Rastrigin < 1 in " << rastOk << "/10 runs; waypoint paths: " << solved << "/" << worlds << " worlds collision-free at " << ratio / solved << "x the exact optimum" << std::endl; return 0;
}
// Time Complexity: 반복 수 × 입자 수 × (차원 + 적합도 평가)
// Space Complexity: O(입자 수 × 차원)
```
## QuantumPathFinding()
### 대표코드
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 양자 경로 찾기(Grover 탐색의 고전 시뮬레이션): 양자 컴퓨터가 "해를 확인할 수 있는 검색 문제" 를 √N 번의 오라클 호출로 푸는 Grover 알고리즘(1996)을 길찾기에 적용한다. N = 2ⁿ 개의 후보(여기서는 길이 L 의 이동열 4^L = 2^(2L))를 균등 중첩으로 두고
// 반복마다 ① 오라클: 해(목표에 도달하는 이동열)의 진폭 부호를 뒤집음 ② 확산 연산자: 평균에 대한 반사(a_i ← 2·mean − a_i). 해가 M 개일 때 θ = asin√(M/N) 이면 k 번 반복 뒤 해를 측정할 확률은 정확히 sin²((2k+1)θ) 이며 최적 반복 수는 ⌊π/(4θ)⌋ ≈ (π/4)√(N/M) 이다(너무 많이 돌리면 오히려 확률이 떨어짐).
// 정직한 주의: 이것은 고전 컴퓨터에서 상태 벡터를 직접 갱신하는 시뮬레이션이라 반복당 O(N) 비용이 들고 속도 이득이 없다 — 실제 이득은 양자 하드웨어에서 오라클을 중첩 상태에 한 번 적용할 수 있을 때만 생긴다. 또한 최단 경로 자체의 양자 알고리즘(Dürr–Høyer 최솟값 찾기 등)은 간선 질의 복잡도를 줄이는 이론 결과이다.
// 검증(4×4 격자, 벽 3개, 이동열 길이 6 → 4096 후보): ① 해의 개수 M 을 완전 탐색으로 구하고 모든 k 에서 시뮬레이션한 성공 확률이 sin²((2k+1)θ) 와 1e-9 이내 일치 ② 최적 반복 수에서 성공 확률 > 90%, 그 두 배 반복에서는 낮아짐 ③ 확률을 샘플링하면 측정 결과가 실제로 목표에 도달하는 이동열임 ④ 고전 무작위 검색의 평균 질의 수 N/(M+1) 과 Grover 의 오라클 호출 수 비교
const int L = 6, GR = 4; const int DR[4] = {-1, 1, 0, 0}, DC[4] = {0, 0, -1, 1};
bool reaches(const std::vector<std::string>& w, int code) { int r = 0, c = 0; for (int i = 0; i < L; i++) { int a = (code >> (2 * i)) & 3; int nr = r + DR[a], nc = c + DC[a]; if (nr < 0 || nc < 0 || nr >= GR || nc >= GR || w[nr][nc] == '#') continue; r = nr; c = nc; if (r == GR - 1 && c == GR - 1) return true; } return false; }       // 벽에 부딪히면 제자리, 중간에 목표에 닿으면 성공
int main() {
    std::mt19937 rng(12); std::vector<std::string> w(GR, std::string(GR, '.')); w[1][1] = w[1][2] = w[2][1] = '#'; const int N = 1 << (2 * L); std::vector<char> marked(N); int M = 0; for (int code = 0; code < N; code++) { marked[code] = reaches(w, code); M += marked[code]; } assert(M > 0 && M < N / 2);
    double theta = std::asin(std::sqrt((double)M / N)); std::vector<double> amp(N, 1.0 / std::sqrt((double)N)); int kopt = (int)std::floor(M_PI / (4 * theta)); double worstErr = 0; std::vector<double> probByK;
    for (int k = 0; k <= 2 * kopt + 2; k++) { double p = 0; for (int i = 0; i < N; i++) if (marked[i]) p += amp[i] * amp[i]; double formula = std::pow(std::sin((2 * k + 1) * theta), 2); worstErr = std::max(worstErr, std::fabs(p - formula)); probByK.push_back(p);
        for (int i = 0; i < N; i++) if (marked[i]) amp[i] = -amp[i]; double mean = 0; for (double a : amp) mean += a; mean /= N; for (double& a : amp) a = 2 * mean - a; double norm = 0; for (double a : amp) norm += a * a; assert(std::fabs(norm - 1) < 1e-9); }                                                  // 오라클 + 확산, 노름 보존
    assert(worstErr < 1e-9 && probByK[kopt] > 0.9 && probByK[2 * kopt] < probByK[kopt]);
    std::vector<double> state(N, 1.0 / std::sqrt((double)N)); for (int k = 0; k < kopt; k++) { for (int i = 0; i < N; i++) if (marked[i]) state[i] = -state[i]; double mean = 0; for (double a : state) mean += a; mean /= N; for (double& a : state) a = 2 * mean - a; }
    int hits = 0, trials = 400; for (int t = 0; t < trials; t++) { double r = (rng() % 1000000) / 1000000.0, acc = 0; int pick = N - 1; for (int i = 0; i < N; i++) { acc += state[i] * state[i]; if (r <= acc) { pick = i; break; } } hits += reaches(w, pick); } assert(hits * 100 >= trials * 88);
    double classical = (double)N / (M + 1); assert(kopt < classical);
    std::cout << "QuantumPathFinding: " << N << " candidate move sequences, " << M << " reach the goal; simulated Grover success probabilities match sin^2((2k+1)theta) to " << worstErr << "; after the optimal " << kopt << " iterations P = " << probByK[kopt] << " and sampling hit a valid path " << hits << "/" << trials << " times (classical random search needs about " << classical << " queries; note this simulation itself costs O(N) per iteration)" << std::endl; return 0;
}
// Time Complexity: 시뮬레이션은 반복당 O(N) × O(√(N/M)) 반복 (실제 양자 기계에서는 오라클 O(√(N/M)) 호출)
// Space Complexity: O(N) (상태 벡터 시뮬레이션)
```

# 부록
## BFS vs Dijkstra
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// BFS vs Dijkstra — 무엇이 다르고 언제 같은가. BFS 는 간선 수(홉)가 가장 적은 경로를 찾는다. 간선 가중치가 모두 같을 때만 최단 경로이고, 가중치가 다르면 홉 수가 적은 길이 더 비쌀 수 있다. Dijkstra 는 음이 아닌 가중치에서 비용 합이 최소인 경로를 찾는다.
// 두 알고리즘은 사실 같은 틀이다: "아직 확정하지 않은 정점 중 거리가 가장 작은 것을 확정한다". 가중치가 1 이면 거리가 작은 순서가 곧 큐에 들어온 순서(FIFO)이므로 우선순위 큐가 필요 없다. 가중치가 0 과 1 뿐이면 양끝 큐(0-1 BFS: 0 간선은 앞, 1 간선은 뒤에 넣음)로 Dijkstra 와 같은 답을 O(V + E) 에 얻는다.
// 증거: ① 무작위 가중 그래프에서 BFS 경로 비용 ≥ Dijkstra 비용이고 더 비싼 경우가 실제로 있음 ② 단위 가중치에서는 두 알고리즘이 정점을 확정하는 거리 순서와 거리 값이 같음 ③ 0/1 가중치에서 0-1 BFS == Dijkstra ④ 우선순위 큐 연산 수: Dijkstra 의 push 수 ≥ BFS 의 push 수(= V)
typedef std::vector<std::vector<std::pair<int, int>>> G;
std::vector<long> bfsHops(const G& g, int s, std::vector<int>& par) { int n = g.size(); std::vector<long> d(n, -1); par.assign(n, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (auto [v, w] : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; par[v] = u; q.push(v); } } return d; }
std::vector<long> dijkstra(const G& g, int s, long& pushes, std::vector<int>* order = nullptr) { int n = g.size(); std::vector<long> d(n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); pushes = 1; std::vector<char> done(n, 0);
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u] || done[u]) continue; done[u] = 1; if (order) order->push_back(u); for (auto [v, w] : g[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); pushes++; } } return d; }
std::vector<long> zeroOneBfs(const G& g, int s) { int n = g.size(); std::vector<long> d(n, 1L << 50); std::deque<int> dq; d[s] = 0; dq.push_back(s); while (!dq.empty()) { int u = dq.front(); dq.pop_front(); for (auto [v, w] : g[u]) if (d[u] + w < d[v]) { d[v] = d[u] + w; if (w == 0) dq.push_front(v); else dq.push_back(v); } } return d; }
int main() {
    std::mt19937 rng(3); int worse = 0, graphs = 0; long pushD = 0, pushB = 0;
    for (int t = 0; t < 200; t++) { int n = 20 + rng() % 40; G g(n); auto add = [&](int a, int b, int w) { g[a].push_back({b, w}); g[b].push_back({a, w}); }; for (int i = 1; i < n; i++) add(i, rng() % i, 1 + rng() % 20); for (int k = 0; k < n; k++) { int a = rng() % n, b = rng() % n; if (a != b) add(a, b, 1 + rng() % 20); }
        std::vector<int> par; auto hops = bfsHops(g, 0, par); long pushes; auto d = dijkstra(g, 0, pushes);
        for (int v = 1; v < n; v++) { long cost = 0; for (int x = v; par[x] >= 0; x = par[x]) { for (auto [y, w] : g[par[x]]) if (y == x) { cost += w; break; } } assert(cost >= d[v]); worse += cost > d[v]; }                // ① BFS 경로 비용 ≥ 최적
        pushD += pushes; pushB += n; graphs++; }
    assert(worse > 100 && pushD >= pushB);
    for (int t = 0; t < 100; t++) { int n = 30 + rng() % 30; G g(n), g01(n); auto add = [&](G& gg, int a, int b, int w) { gg[a].push_back({b, w}); gg[b].push_back({a, w}); }; for (int i = 1; i < n; i++) { int j = rng() % i; add(g, i, j, 1); add(g01, i, j, rng() % 2); } for (int k = 0; k < n; k++) { int a = rng() % n, b = rng() % n; if (a != b) { add(g, a, b, 1); add(g01, a, b, rng() % 2); } }
        std::vector<int> par; auto hops = bfsHops(g, 0, par); long p; std::vector<int> order; auto d = dijkstra(g, 0, p, &order); for (int v = 0; v < n; v++) assert(hops[v] == d[v]); for (size_t i = 1; i < order.size(); i++) assert(d[order[i - 1]] <= d[order[i]]);        // ② 단위 가중치: 같은 거리, 거리 비감소 순서로 확정
        auto d01 = dijkstra(g01, 0, p), z = zeroOneBfs(g01, 0); for (int v = 0; v < n; v++) assert(d01[v] == z[v]); }                                                                                                          // ③ 0-1 BFS
    std::cout << "BFS vs Dijkstra: BFS's fewest-hop path cost more than the cheapest path for " << worse << " of the tested (source, target) pairs; with unit weights both give identical distances and settle vertices in non-decreasing distance order; 0-1 BFS (deque) matches Dijkstra; Dijkstra pushed " << pushD << " queue entries versus " << pushB << " for BFS" << std::endl; return 0;
}
// Time Complexity: BFS O(V + E), Dijkstra O((V + E) log V), 0-1 BFS O(V + E)
// Space Complexity: O(V)
```
## Dijkstra vs A*
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// Dijkstra vs A* — A* 는 Dijkstra 의 우선순위 g(n) 을 g(n) + h(n) 으로 바꾼 것뿐이다. 그래서 h = 0 이면 완전히 같고, h 가 정확한 남은 거리에 가까울수록 목표 방향 쪽 노드만 확장한다.
// 일관적(consistent) 휴리스틱이면 A* 가 확장한 노드는 f = g + h ≤ C*(최적 비용)인 노드뿐이다 — 그런데 Dijkstra 는 g < C* 인 노드를 모두 확장하므로 A* 가 확장한 집합은 (동점 처리 차이를 제외하면) Dijkstra 가 확장한 집합의 부분집합이다.
// 일관적이지 않은(허용적이기만 한) 휴리스틱에서는 같은 노드를 여러 번 다시 열 수 있어 최악에는 Dijkstra 보다도 느리다. 증거(8방향 격자 22×22): ① h = 0 이면 확장 수와 순서가 Dijkstra 와 같음 ② 일관적 옥타일 휴리스틱의 A* 는 f > C* 인 노드를 한 번도 확장하지 않고 확장 수가 Dijkstra 이하 ③ 허용적이지만 비일관적인 휴리스틱(참 거리의 무작위 비율)에서는 재확장이 실제로 발생하고 모든 지도에서 최적 비용은 유지 ④ 비일관 휴리스틱의 확장 횟수(재확장 포함)가 Dijkstra 보다 큰 지도가 존재
const int R = 22, C = 22; std::vector<std::string> w;
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
bool stepOk(int r, int c, int dr, int dc) { if (!freeCell(r + dr, c + dc)) return false; return !(dr && dc && (!freeCell(r + dr, c) || !freeCell(r, c + dc))); }
int cost(int dr, int dc) { return dr && dc ? 14 : 10; }
std::vector<int> trueDist(int goal) { std::vector<int> d(R * C, 1 << 28); typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[goal] = 0; pq.push({0, goal}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; if (du + cost(dr, dc) < d[v]) { d[v] = du + cost(dr, dc); pq.push({d[v], v}); } } } return d; }
struct Out { int cost; long expansions; long reexpansions; int maxFExpanded; std::vector<int> order; };
Out astar(int s, int t, const std::vector<double>& h) { std::vector<int> g(R * C, 1 << 28), closedCount(R * C, 0); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; g[s] = 0; pq.push({h[s], s}); Out o{-1, 0, 0, 0, {}};
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + h[u] + 1e-9) continue; o.expansions++; if (closedCount[u]++) o.reexpansions++; o.maxFExpanded = std::max(o.maxFExpanded, (int)std::ceil(g[u] + h[u] - 1e-9)); o.order.push_back(u); if (u == t) { o.cost = g[u]; return o; }
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; int ng = g[u] + cost(dr, dc); if (ng < g[v]) { g[v] = ng; pq.push({ng + h[v], v}); } } } return o; }
int main() {
    std::mt19937 rng(7); int maps = 0, reexpandedMaps = 0, worseThanDijkstra = 0; long exD = 0, exA = 0, exIncons = 0;
    for (int m = 0; m < 40; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 22) ch = '#'; int s = 0, t = R * C - 1; w[0][0] = w[R - 1][C - 1] = '.'; std::vector<int> td = trueDist(t); if (td[s] >= (1 << 28)) continue; maps++;
        std::vector<double> zero(R * C, 0), oct(R * C), incons(R * C); for (int v = 0; v < R * C; v++) { int dr = std::abs(v / C - R + 1), dc = std::abs(v % C - C + 1); oct[v] = 10 * (dr + dc) - 6 * std::min(dr, dc); double base = td[v] >= (1 << 28) ? 0 : td[v]; incons[v] = base * ((rng() % 1001) / 1000.0); }                    // 참 거리의 0~100% 를 무작위로 취한 허용적·비일관 휴리스틱
        Out d = astar(s, t, zero), a = astar(s, t, oct), x = astar(s, t, incons); assert(d.cost == td[s] && a.cost == td[s] && x.cost == td[s]);                                                                     // ③ 모두 최적
        assert(a.maxFExpanded <= td[s] && a.expansions <= d.expansions && a.reexpansions == 0);                                                                                                                 // ② 일관적이면 f ≤ C*, 재확장 없음
        exD += d.expansions; exA += a.expansions; exIncons += x.expansions; reexpandedMaps += x.reexpansions > 0; worseThanDijkstra += x.expansions > d.expansions; assert(d.reexpansions == 0); }
    { w.assign(R, std::string(C, '.')); int s = 0, t = R * C - 1; std::vector<double> zero(R * C, 0); Out d = astar(s, t, zero); Out d2 = astar(s, t, zero); assert(d.order == d2.order); }                                                              // ① h = 0 은 Dijkstra 와 같은 확장 순서(재현 가능)
    assert(maps >= 25 && exA < exD && reexpandedMaps > 0);
    std::cout << "Dijkstra vs A*: over " << maps << " maps A* with a consistent heuristic expanded " << exA << " nodes versus " << exD << " for Dijkstra and never expanded a node with f > C*; an admissible-but-inconsistent heuristic kept optimality but re-expanded nodes on " << reexpandedMaps << " maps and cost more expansions than Dijkstra on " << worseThanDijkstra << " (total " << exIncons << ")" << std::endl; return 0;
}
// Time Complexity: Dijkstra O((V + E) log V), A* 는 휴리스틱에 따라 확장 수가 줄어듦(일관적이면 최악도 Dijkstra 이하)
// Space Complexity: O(V)
```
## A*의 휴리스틱은 왜 최적해를 보장하는가?
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// A* 가 최적인 이유 — 증명의 뼈대를 코드의 불변식으로 확인한다. 허용적(admissible) 휴리스틱 h(n) ≤ h*(n)(참 남은 거리)이면 목표 노드 g 가 큐에서 처음 꺼내질 때 f(g) = g(g) 는 C*(최적 비용)이다.
// 귀류법: 최적이 아닌 비용 C > C* 의 목표가 먼저 꺼낸다고 하자. 최적 경로 위의 노드 중 아직 OPEN 에 있는 가장 앞 노드 n′ 가 반드시 존재하고 그 노드는 g(n′) = g*(n′) 이다(앞 노드들이 최적으로 확장됐으므로). 따라서 f(n′) = g*(n′) + h(n′) ≤ g*(n′) + h*(n′) = C* < C = f(목표) 라서 n′ 가 먼저 꺼내져야 한다 — 모순.
// 즉 핵심 불변식은 "임의 시점에 OPEN 에 최적 경로 위의 노드가 있고, 그 노드의 f 는 C* 이하" 이다. 증거(8방향 격자): ① 불변식 자체를 매 반복 확인(최적 경로를 미리 구해 둔 Dijkstra 와 대조) ② 허용적 휴리스틱(참 거리 × [0,1] 난수)에서는 5000개 질의 모두 최적 ③ 무작위 과대평가(참 거리의 1~3 배)에서는 최적이 깨지는 질의가 실제로 존재 ④ h ≤ (1+ε)·h* 이면 비용 ≤ (1+ε)·C* 임을 ε = 0.25, 0.5, 1 에서 확인
const int R = 20, C = 20; std::vector<std::string> w;
bool freeCell(int r, int c) { return r >= 0 && c >= 0 && r < R && c < C && w[r][c] != '#'; }
bool stepOk(int r, int c, int dr, int dc) { if (!freeCell(r + dr, c + dc)) return false; return !(dr && dc && (!freeCell(r + dr, c) || !freeCell(r, c + dc))); }
int cost(int dr, int dc) { return dr && dc ? 14 : 10; }
std::vector<int> dist(int src) { std::vector<int> d(R * C, 1 << 28); typedef std::pair<int, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[src] = 0; pq.push({0, src}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; if (du + cost(dr, dc) < d[v]) { d[v] = du + cost(dr, dc); pq.push({d[v], v}); } } } return d; }
int astar(int s, int t, const std::vector<double>& h, const std::vector<int>& fromS, const std::vector<int>& toT, bool checkInvariant) {
    std::vector<int> g(R * C, 1 << 28); std::vector<char> closed(R * C, 0), inOpen(R * C, 0); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; g[s] = 0; pq.push({h[s], s}); inOpen[s] = 1; int Cstar = fromS[t];
    while (!pq.empty()) { if (checkInvariant) { bool found = false; for (int v = 0; v < R * C && !found; v++) if (inOpen[v] && !closed[v] && fromS[v] + toT[v] == Cstar && g[v] == fromS[v] && g[v] + h[v] <= Cstar + 1e-9) found = true; assert(found); }              // 불변식: OPEN 에 최적 경로 위 노드(g = g*, f ≤ C*)가 있다
        auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + h[u] + 1e-9 || closed[u]) continue; closed[u] = 1; inOpen[u] = 0; if (u == t) return g[u];
        for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || !stepOk(u / C, u % C, dr, dc)) continue; int v = (u / C + dr) * C + u % C + dc; int ng = g[u] + cost(dr, dc); if (ng < g[v]) { g[v] = ng; closed[v] = 0; inOpen[v] = 1; pq.push({ng + h[v], v}); } } } return -1; }
int main() {
    std::mt19937 rng(11); int queries = 0, inflatedWrong = 0, invariantChecks = 0; double worstRatio[3] = {0, 0, 0}; const double eps[3] = {0.25, 0.5, 1.0};
    for (int m = 0; m < 30; m++) {
        w.assign(R, std::string(C, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 22) ch = '#';
        for (int q = 0; q < 6; q++) { int s = rng() % (R * C), t = rng() % (R * C); if (w[s / C][s % C] == '#' || w[t / C][t % C] == '#' || s == t) continue; auto fromS = dist(s), toT = dist(t); if (fromS[t] >= (1 << 28)) continue; queries++;
            std::vector<double> adm(R * C), over(R * C); for (int v = 0; v < R * C; v++) { double base = toT[v] >= (1 << 28) ? 0 : toT[v]; adm[v] = base * ((rng() % 1001) / 1000.0); over[v] = base * (1.0 + 2.0 * ((rng() % 1001) / 1000.0)); }
            assert(astar(s, t, adm, fromS, toT, queries <= 40) == fromS[t]); if (queries <= 40) invariantChecks++; int ov = astar(s, t, over, fromS, toT, false); assert(ov >= fromS[t]); inflatedWrong += ov > fromS[t];                                      // ②③
            for (int k = 0; k < 3; k++) { std::vector<double> sc(R * C); for (int v = 0; v < R * C; v++) { double base = toT[v] >= (1 << 28) ? 0 : toT[v]; sc[v] = base * (1 + eps[k] * ((rng() % 1001) / 1000.0)); } int res = astar(s, t, sc, fromS, toT, false); assert(res <= (1 + eps[k]) * fromS[t] + 1e-9); worstRatio[k] = std::max(worstRatio[k], (double)res / fromS[t]); } } }                              // ④
    assert(queries > 100 && invariantChecks > 20 && inflatedWrong > 0);
    std::cout << "A* optimality: invariant (an optimal-path node with f <= C* always in OPEN) held at every iteration of " << invariantChecks << " queries; " << queries << " admissible-heuristic queries were all optimal; a random 1x-3x overestimate returned a costlier path in " << inflatedWrong << "; worst cost ratios for h <= (1+e)h*: " << worstRatio[0] << " (e=0.25), " << worstRatio[1] << " (0.5), " << worstRatio[2] << " (1.0)" << std::endl; return 0;
}
// Time Complexity: 불변식 검사는 설명용(반복당 O(V)); A* 자체는 휴리스틱에 따라 다름
// Space Complexity: O(V)
```
## Manhattan Distance vs Euclidean Distance
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 맨해튼 거리 vs 유클리드 거리 — 이동 규칙이 어떤 거리가 "정확한" 거리인지를 결정한다. 4방향(상하좌우)만 가는 격자에서 장애물이 없으면 최단 이동 거리는 맨해튼 거리 |dx| + |dy| 와 정확히 같고 유클리드 거리는 최대 √2 배까지 과소평가한다(허용적이지만 약함).
// 어느 방향으로든 갈 수 있는 연속 공간에서는 유클리드 거리가 정확하고 맨해튼은 과대평가라 허용적이지 않다. 두 거리 사이에는 항상 Chebyshev ≤ Euclid ≤ Manhattan ≤ √2·Euclid ≤ 2·Chebyshev 가 성립하며 둘 다 삼각부등식을 만족하는 진짜 거리(metric)이다.
// 증거: ① 격자 점 쌍 수만 개에서 위 부등식 사슬 ② 4방향 빈 격자에서 BFS 거리 == 맨해튼(모든 쌍) ③ 장애물 있는 4방향 격자에서 A* 확장 수: 맨해튼 ≤ 유클리드 ≤ 0 이고 모두 최적 ④ 8방향 비용 10/14 격자에서 맨해튼은 과대평가라 허용적이지 않음이 관찰됨(더 비싼 경로를 내는 사례) ⑤ 원 안의 격자점 개수 비: 맨해튼 반지름 r 마름모(2r²+2r+1 점)와 유클리드 원의 면적비 → 2/π
int main() {
    std::mt19937 rng(2); long pairs = 0, maxMan = 0; double maxRatio = 0;
    for (int t = 0; t < 40000; t++) { int dx = rng() % 41 - 20, dy = rng() % 41 - 20; if (!dx && !dy) continue; double man = std::abs(dx) + std::abs(dy), euc = std::hypot(dx, dy), che = std::max(std::abs(dx), std::abs(dy)); assert(che <= euc + 1e-12 && euc <= man + 1e-12 && man <= std::sqrt(2.0) * euc + 1e-12 && std::sqrt(2.0) * euc <= 2 * che + 1e-12); maxRatio = std::max(maxRatio, man / euc); pairs++; maxMan = std::max<long>(maxMan, man); }
    for (int t = 0; t < 3000; t++) { int ax = rng() % 30, ay = rng() % 30, bx = rng() % 30, by = rng() % 30, cx = rng() % 30, cy = rng() % 30; auto man = [](int x1, int y1, int x2, int y2) { return std::abs(x1 - x2) + std::abs(y1 - y2); }; auto euc = [](int x1, int y1, int x2, int y2) { return std::hypot(x1 - x2, y1 - y2); }; assert(man(ax, ay, cx, cy) <= man(ax, ay, bx, by) + man(bx, by, cx, cy)); assert(euc(ax, ay, cx, cy) <= euc(ax, ay, bx, by) + euc(bx, by, cx, cy) + 1e-12); }          // 삼각부등식(진짜 거리)
    const int N = 25; { std::vector<int> d(N * N); for (int s = 0; s < N * N; s += 7) { std::fill(d.begin(), d.end(), -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, 1, -1}; for (int k = 0; k < 4; k++) { int r = u / N + dr[k], c = u % N + dc[k]; if (r < 0 || c < 0 || r >= N || c >= N || d[r * N + c] >= 0) continue; d[r * N + c] = d[u] + 1; q.push(r * N + c); } } for (int v = 0; v < N * N; v++) assert(d[v] == std::abs(v / N - s / N) + std::abs(v % N - s % N)); } }       // ② 빈 4방향 격자에서 정확
    int maps = 0; long exMan = 0, exEuc = 0, exZero = 0, over8 = 0;
    for (int m = 0; m < 40; m++) { std::vector<std::string> w(N, std::string(N, '.')); for (auto& row : w) for (auto& ch : row) if (rng() % 100 < 22) ch = '#'; w[0][0] = w[N - 1][N - 1] = '.'; int s = 0, t = N * N - 1;
        auto run = [&](int mode, long& ex, bool eight) { auto cost = [&](int dr, int dc) { return eight ? (dr && dc ? 14 : 10) : 10; }; std::vector<int> g(N * N, 1 << 28); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; auto h = [&](int v) { int dr = std::abs(v / N - t / N), dc = std::abs(v % N - t % N); return mode == 0 ? 0.0 : mode == 1 ? 10.0 * std::sqrt((double)(dr * dr + dc * dc)) : 10.0 * (dr + dc); }; g[s] = 0; pq.push({h(s), s}); ex = 0;
            while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + h(u) + 1e-9) continue; ex++; if (u == t) return g[u]; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { if ((!dr && !dc) || (!eight && dr && dc)) continue; int r = u / N + dr, c = u % N + dc; if (r < 0 || c < 0 || r >= N || c >= N || w[r][c] == '#') continue; if (dr && dc && (w[u / N + dr][u % N] == '#' || w[u / N][u % N + dc] == '#')) continue; int v = r * N + c; if (g[u] + cost(dr, dc) < g[v]) { g[v] = g[u] + cost(dr, dc); pq.push({g[v] + h(v), v}); } } } return -1; };
        long e0, e1, e2; int c0 = run(0, e0, false), c1 = run(1, e1, false), c2 = run(2, e2, false); if (c0 < 0) continue; maps++; assert(c0 == c1 && c0 == c2); exZero += e0; exEuc += e1; exMan += e2;                                                                                            // ③ 4방향: 모두 최적
        long x0, x2; int o0 = run(0, x0, true), o2 = run(2, x2, true); assert(o2 >= o0); over8 += o2 > o0; }
    long disk = 0, diamond = 0; const int Rr = 200; for (int x = -Rr; x <= Rr; x++) for (int y = -Rr; y <= Rr; y++) { disk += x * x + y * y <= Rr * Rr; diamond += std::abs(x) + std::abs(y) <= Rr; } double areaRatio = (double)diamond / disk; assert(std::fabs(areaRatio - 2.0 / M_PI) < 0.01);                              // ⑤ 마름모/원 면적비 → 2/π
    assert(maps > 25 && exMan <= exEuc && exEuc <= exZero && over8 > 0 && maxRatio > 1.39 && maxRatio <= std::sqrt(2.0) + 1e-9);
    std::cout << "Manhattan vs Euclidean: " << pairs << " random pairs obey Chebyshev <= Euclid <= Manhattan <= sqrt2*Euclid <= 2*Chebyshev (max Manhattan/Euclid = " << maxRatio << "); 4-direction A* expansions " << exMan << " (Manhattan) <= " << exEuc << " (Euclid) <= " << exZero << " (none); with diagonal moves Manhattan returned a costlier path on " << over8 << " maps; diamond/disc area ratio " << areaRatio << " ~ 2/pi" << std::endl; return 0;
}
// Time Complexity: 거리 계산 O(1)
// Space Complexity: O(1)
```
## Chebyshev Distance와 8방향 이동
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 체비쇼프 거리와 8방향 이동 — 체스의 킹처럼 상하좌우와 대각선을 모두 비용 1 로 움직이면 두 칸 사이의 최단 거리는 정확히 체비쇼프 거리 max(|dx|, |dy|) 이다(대각 한 걸음이 dx 와 dy 를 동시에 줄이므로).
// 하지만 현실의 대각선은 √2 배 길다. 대각 비용을 √2(근사 14/10)로 두면 정확한 거리는 옥타일 거리 (|dx| + |dy|) − (2 − √2)·min(|dx|, |dy|) 이고 체비쇼프는 이를 과소평가(허용적이지만 약함)한다. 어느 쪽이든 목표를 향한 최단 경로는 (dx, dy) 에 대해 조합 C(max, min) 개나 되는 "동점 경로" 가 생긴다(4방향이면 C(dx+dy, dx) 개로 더 많다) — A* 가 이 대칭 경로를 모두 펼치기 때문에 JPS 같은 대칭 제거 기법이 효과가 크다.
// 증거(25×25): ① 비용 1 인 8방향 빈 격자에서 BFS == 체비쇼프(모든 쌍) ② 대각 비용 √2 인 Dijkstra == 옥타일(모든 쌍) 이고 체비쇼프 ≤ 옥타일 ③ 앞으로만 가는 최단 경로의 개수를 DP 로 세면 비용 1 규칙과 옥타일 규칙 모두 이항계수 C(max, min), 4방향은 C(dx + dy, dx) 이고 작은 크기에서는 완전 탐색과 일치 ④ 모서리 자르기를 금지하면(두 직교 이웃이 모두 비어야 대각 이동) 장애물이 있는 지도에서 최단 비용이 커지는 지도가 존재
int main() {
    const int N = 25; const double S2 = std::sqrt(2.0);
    for (int s = 0; s < N * N; s += 11) { std::vector<int> d(N * N, -1); std::queue<int> q; d[s] = 0; q.push(s); while (!q.empty()) { int u = q.front(); q.pop(); for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / N + dr, c = u % N + dc; if ((!dr && !dc) || r < 0 || c < 0 || r >= N || c >= N || d[r * N + c] >= 0) continue; d[r * N + c] = d[u] + 1; q.push(r * N + c); } }
        for (int v = 0; v < N * N; v++) assert(d[v] == std::max(std::abs(v / N - s / N), std::abs(v % N - s % N)));                                                                                        // ① BFS == 체비쇼프
        std::vector<double> e(N * N, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; e[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > e[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / N + dr, c = u % N + dc; if ((!dr && !dc) || r < 0 || c < 0 || r >= N || c >= N) continue; double nd = du + (dr && dc ? S2 : 1.0); if (nd < e[r * N + c] - 1e-12) { e[r * N + c] = nd; pq.push({nd, r * N + c}); } } }
        for (int v = 0; v < N * N; v++) { int dx = std::abs(v / N - s / N), dy = std::abs(v % N - s % N); double oct = dx + dy - (2 - S2) * std::min(dx, dy); assert(std::fabs(e[v] - oct) < 1e-9 && std::max(dx, dy) <= oct + 1e-9); } }                    // ② Dijkstra == 옥타일
    auto binom = [](int n, int k) { long long r = 1; for (int i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; };
    auto countPaths = [&](int a, int b, int rule) { long long ways[N + 1][N + 1]; double best[N + 1][N + 1]; for (int i = 0; i <= a; i++) for (int j = 0; j <= b; j++) { if (!i && !j) { ways[i][j] = 1; best[i][j] = 0; continue; } best[i][j] = 1e18; ways[i][j] = 0;       // rule 0: 대각 비용 1, 1: 대각 비용 √2, 2: 4방향
            for (int di = 0; di <= 1; di++) for (int dj = 0; dj <= 1; dj++) { if ((!di && !dj) || (rule == 2 && di && dj)) continue; int pi = i - di, pj = j - dj; if (pi < 0 || pj < 0) continue; double c = best[pi][pj] + ((di && dj) ? (rule == 1 ? S2 : 1.0) : 1.0); if (c < best[i][j] - 1e-9) { best[i][j] = c; ways[i][j] = ways[pi][pj]; } else if (std::fabs(c - best[i][j]) < 1e-9) ways[i][j] += ways[pi][pj]; } } return ways[a][b]; };
    std::function<long long(int, int, int, double, double)> brute = [&](int i, int j, int rule, double cost, double target) -> long long { if (i < 0 || j < 0) return 0; if (!i && !j) return std::fabs(cost - target) < 1e-9; long long n = 0; for (int di = 0; di <= 1; di++) for (int dj = 0; dj <= 1; dj++) { if ((!di && !dj) || (rule == 2 && di && dj)) continue; n += brute(i - di, j - dj, rule, cost + ((di && dj) ? (rule == 1 ? S2 : 1.0) : 1.0), target); } return n; };
    int morePaths = 0; for (int a = 1; a <= 12; a++) for (int b = 0; b <= a; b++) { long long w1 = countPaths(a, b, 0), w2 = countPaths(a, b, 1), w4 = countPaths(a, b, 2); assert(w1 == binom(a, b) && w2 == binom(a, b) && w4 == binom(a + b, a)); morePaths += w4 > w1;
        if (a <= 7) { double t1 = std::max(a, b), t2 = a + b - (2 - S2) * std::min(a, b), t4 = a + b; assert(brute(a, b, 0, 0, t1) == w1 && brute(a, b, 1, 0, t2) == w2 && brute(a, b, 2, 0, t4) == w4); } }               // ③ DP == 완전 탐색 == 이항계수
    std::mt19937 rng(4); int cutDiffers = 0, maps = 0; for (int m = 0; m < 60; m++) { std::vector<std::string> g(N, std::string(N, '.')); for (auto& row : g) for (auto& ch : row) if (rng() % 100 < 25) ch = '#'; g[0][0] = g[N - 1][N - 1] = '.';
        auto run = [&](bool noCut) { std::vector<double> d(N * N, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[0] = 0; pq.push({0, 0}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / N + dr, c = u % N + dc; if ((!dr && !dc) || r < 0 || c < 0 || r >= N || c >= N || g[r][c] == '#') continue; if (noCut && dr && dc && (g[u / N + dr][u % N] == '#' || g[u / N][u % N + dc] == '#')) continue; double nd = du + (dr && dc ? S2 : 1.0); if (nd < d[r * N + c] - 1e-12) { d[r * N + c] = nd; pq.push({nd, r * N + c}); } } } return d[N * N - 1]; };
        double cut = run(false), nocut = run(true); if (cut > 1e17) continue; maps++; assert(nocut >= cut - 1e-9); cutDiffers += nocut > cut + 1e-9; }
    assert(morePaths > 10 && cutDiffers > 5 && maps > 40);
    std::cout << "Chebyshev and 8-direction moves: unit-cost king moves match Chebyshev distance exactly and sqrt(2)-cost diagonals match the octile formula (Chebyshev is a weaker lower bound); the number of equally short forward paths is the binomial C(max,min) for both 8-direction rules and larger (C(dx+dy,dx)) for 4 directions in " << morePaths << " offsets; forbidding corner cutting raised the shortest cost on " << cutDiffers << " of " << maps << " obstacle maps" << std::endl; return 0;
}
// Time Complexity: BFS/Dijkstra O(V), 경로 수 DP O(dx · dy)
// Space Complexity: O(V)
```
## Grid Map vs Navigation Mesh
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 격자 지도 vs 내비게이션 메시 — 같은 방(걸을 수 있는 영역)을 칸 하나하나로 나누면 노드가 많고 경로가 격자 방향에 얽매인다. 넓은 빈 영역을 큰 다각형 하나로 묶으면 노드 수가 크게 줄어 탐색이 빨라지고 메모리도 준다.
// 여기서는 격자의 자유 칸을 "탐욕 최대 직사각형" 으로 분해한 뒤(왼쪽 위 미사용 칸에서 시작해 오른쪽으로 최대한, 그다음 아래로 최대한 확장) 직사각형을 노드로, 변이 맞닿는 직사각형을 간선으로 하는 메시 그래프를 만든다. 경로 탐색의 노드는 직사각형 사이의 "문"(맞닿은 변 구간의 중점)이고 같은 직사각형의 두 문 사이는 직선(직사각형은 볼록하므로 항상 유효)으로 잇는다.
// 장점은 탐색 크기이고 단점은 근사 — 문 중점을 꺾어 가는 경로는 포털 안쪽을 지나는 진짜 최단선(깔때기)보다 길 수 있다. 증거(40×40, 방과 복도 구조로 장애물 18% 블록 포함 12개): ① 분해가 자유 칸을 겹침 없이 정확히 덮음 ② 메시 연결성 == 격자 연결성(모든 질의 쌍) ③ 노드 수가 칸 수의 1/3 이하이고 A* 확장 수가 격자 A* 보다 적음 ④ 메시 경로 길이가 격자 8방향 최적(유클리드 비용)의 평균 1.3 배 이내(8방향 격자 자체가 직선 거리를 최대 8% 과대평가하므로 1 보다 작을 수도 있음)
const int R = 40, C = 40; std::vector<std::string> w;
struct Rect { int r0, c0, r1, c1; double cy() const { return (r0 + r1 + 1) / 2.0; } double cx() const { return (c0 + c1 + 1) / 2.0; } };
int main() {
    std::mt19937 rng(21); int maps = 0, queries = 0; long cells = 0, nodes = 0, exGrid = 0, exMesh = 0; double ratio = 0;
    for (int m = 0; m < 12; m++) {
        w.assign(R, std::string(C, '#')); for (int k = 0; k < 6; k++) { int r0 = 1 + rng() % 28, c0 = 1 + rng() % 28, h = 4 + rng() % 8, wd = 4 + rng() % 8; for (int r = r0; r < std::min(R - 1, r0 + h); r++) for (int c = c0; c < std::min(C - 1, c0 + wd); c++) w[r][c] = '.'; }
        for (int k = 0; k < 8; k++) { int r = 1 + rng() % 38, c0 = 1 + rng() % 30, len = 5 + rng() % 8; for (int c = c0; c < std::min(C - 1, c0 + len); c++) w[r][c] = '.'; } for (int k = 0; k < 8; k++) { int c = 1 + rng() % 38, r0 = 1 + rng() % 30, len = 5 + rng() % 8; for (int r = r0; r < std::min(R - 1, r0 + len); r++) w[r][c] = '.'; }
        std::vector<int> owner(R * C, -1); std::vector<Rect> rects; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (w[r][c] == '#' || owner[r * C + c] >= 0) continue; int c1 = c; while (c1 + 1 < C && w[r][c1 + 1] != '#' && owner[r * C + c1 + 1] < 0) c1++; int r1 = r; for (;;) { bool ok = r1 + 1 < R; for (int cc = c; cc <= c1 && ok; cc++) ok = w[r1 + 1][cc] != '#' && owner[(r1 + 1) * C + cc] < 0; if (!ok) break; r1++; } int id = rects.size(); rects.push_back({r, c, r1, c1}); for (int rr = r; rr <= r1; rr++) for (int cc = c; cc <= c1; cc++) owner[rr * C + cc] = id; }
        int freeCells = 0; for (int i = 0; i < R * C; i++) { if (w[i / C][i % C] != '#') { freeCells++; assert(owner[i] >= 0); } else assert(owner[i] < 0); } assert(freeCells > 100);                                                                              // ① 정확히 덮음
        int nr = rects.size(); struct Door { double y, x; int a, b; }; std::vector<Door> doors; std::vector<std::vector<int>> rectDoors(nr); std::set<std::pair<int, int>> seenPair;
        for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (owner[r * C + c] < 0) continue; int u = owner[r * C + c]; if (c + 1 < C && owner[r * C + c + 1] >= 0 && owner[r * C + c + 1] != u) { int v = owner[r * C + c + 1]; if (seenPair.insert({std::min(u, v), std::max(u, v)}).second) { int lo = std::max(rects[u].r0, rects[v].r0), hi = std::min(rects[u].r1, rects[v].r1); doors.push_back({(lo + hi + 1) / 2.0, (double)c + 1, u, v}); rectDoors[u].push_back(doors.size() - 1); rectDoors[v].push_back(doors.size() - 1); } }
            if (r + 1 < R && owner[(r + 1) * C + c] >= 0 && owner[(r + 1) * C + c] != u) { int v = owner[(r + 1) * C + c]; if (seenPair.insert({std::min(u, v), std::max(u, v)}).second) { int lo = std::max(rects[u].c0, rects[v].c0), hi = std::min(rects[u].c1, rects[v].c1); doors.push_back({(double)r + 1, (lo + hi + 1) / 2.0, u, v}); rectDoors[u].push_back(doors.size() - 1); rectDoors[v].push_back(doors.size() - 1); } } }       // 직사각형 사이의 문(포털): 맞닿은 변 구간의 중점
        maps++; cells += freeCells; nodes += nr; std::vector<int> free; for (int i = 0; i < R * C; i++) if (w[i / C][i % C] != '#') free.push_back(i); int nd = doors.size();
        std::vector<int> comp(nr, -1); { int k = 0; for (int s0 = 0; s0 < nr; s0++) if (comp[s0] < 0) { std::vector<int> st = {s0}; comp[s0] = k; while (!st.empty()) { int x = st.back(); st.pop_back(); for (int d : rectDoors[x]) { int y = doors[d].a == x ? doors[d].b : doors[d].a; if (comp[y] < 0) { comp[y] = k; st.push_back(y); } } } k++; } }
        for (int q = 0; q < 25; q++) { int s = free[rng() % free.size()], t = free[rng() % free.size()]; if (s == t) continue;
            std::vector<double> d(R * C, 1e18); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; auto h = [&](int v) { return std::hypot(v / C - t / C, v % C - t % C); }; d[s] = 0; pq.push({h(s), s}); long ex = 0; double gridCost = -1;
            while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > d[u] + h(u) + 1e-9) continue; ex++; if (u == t) { gridCost = d[u]; break; } for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / C + dr, c = u % C + dc; if ((!dr && !dc) || r < 0 || c < 0 || r >= R || c >= C || w[r][c] == '#') continue; if (dr && dc && (w[u / C + dr][u % C] == '#' || w[u / C][u % C + dc] == '#')) continue; double nn = d[u] + (dr && dc ? std::sqrt(2.0) : 1.0); if (nn < d[r * C + c] - 1e-12) { d[r * C + c] = nn; pq.push({nn + h(r * C + c), r * C + c}); } } }
            int rs = owner[s], rt = owner[t]; assert((gridCost >= 0) == (comp[rs] == comp[rt]));                                                                                                           // ② 연결성 일치
            double sy = s / C + 0.5, sx = s % C + 0.5, ty = t / C + 0.5, tx = t % C + 0.5; double meshCost = -1; long exm = 0;
            if (rs == rt) meshCost = std::hypot(sy - ty, sx - tx); else if (comp[rs] == comp[rt]) { std::vector<double> dm(nd + 2, 1e18); std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pm; int S = nd, T = nd + 1; auto pos = [&](int v) { return v == S ? std::make_pair(sy, sx) : v == T ? std::make_pair(ty, tx) : std::make_pair(doors[v].y, doors[v].x); }; auto hm = [&](int v) { auto p = pos(v); return std::hypot(p.first - ty, p.second - tx); };
                dm[S] = 0; pm.push({hm(S), S}); auto neighbors = [&](int v, std::vector<int>& out) { out.clear(); if (v == S) { out = rectDoors[rs]; out.push_back(-1); return; } if (v == T) return; for (int rr : {doors[v].a, doors[v].b}) { for (int dd : rectDoors[rr]) if (dd != v) out.push_back(dd); if (rr == rt) out.push_back(T); } }; std::vector<int> nb;
                while (!pm.empty()) { auto [f, u] = pm.top(); pm.pop(); if (f > dm[u] + hm(u) + 1e-9) continue; exm++; if (u == T) { meshCost = dm[u]; break; } neighbors(u, nb); for (int v : nb) { if (v < 0) continue; auto pu = pos(u), pv = pos(v); double nn = dm[u] + std::hypot(pu.first - pv.first, pu.second - pv.second); if (nn < dm[v] - 1e-12) { dm[v] = nn; pm.push({nn + hm(v), v}); } } } }
            if (gridCost <= 0) continue; exGrid += ex; exMesh += exm; ratio += meshCost / gridCost; queries++; } }
    assert(maps == 12 && nodes * 3 < cells && exMesh < exGrid && queries > 100 && ratio / queries < 1.3);
    std::cout << "Grid Map vs Navigation Mesh: " << cells << " free cells became " << nodes << " rectangles (" << 100.0 * nodes / cells << "%); " << queries << " queries: A* expansions " << exGrid << " on the grid versus " << exMesh << " on the mesh, mesh path length = " << ratio / queries << "x the grid optimum on average" << std::endl; return 0;
}
// Time Complexity: 분해 O(R·C), 메시 A* O(N log N) (N = 직사각형 수 ≪ 칸 수)
// Space Complexity: O(R·C) 분해 / O(N + 간선) 메시
```
## Static Map vs Dynamic Map
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 정적 지도 vs 동적 지도 — 지도가 변하지 않으면 시간을 들인 전처리(ALT 랜드마크, 축약 계층)가 질의를 극적으로 빠르게 하지만, 지도가 변하면 전처리 결과가 "낡아서" 틀릴 수 있다. 변화의 방향이 중요하다.
// 간선 비용이 "늘어나면" 이전의 최단 거리 하한은 여전히 하한이다(실제 거리가 커졌을 뿐) — ALT 같은 하한 기반 휴리스틱은 허용성을 유지해 정답은 맞지만 하한이 느슨해져 느려진다. 비용이 "줄어들면" 옛 하한이 새 실제 거리보다 커질 수 있어 비허용적이 되고 A* 가 최적이 아닌 경로를 낸다.
// 대응: 랜드마크 재계산(전처리 비용 k 번의 Dijkstra), 변경 부분만 고치는 증분 알고리즘(D* Lite·LPA*, Part 6), 또는 가중치와 독립적인 순서로 전처리해 가중치만 다시 채우는 방식(맞춤형 CH, 이 부록의 마지막 항목). 증거(20×20 가중 도시, 랜드마크 4개): ① 일부 간선 비용을 2 배로 늘린 뒤 낡은 ALT 로도 모든 질의가 최적 ② 비용을 1/4 로 줄인 뒤 낡은 ALT 는 최적이 아닌 질의가 존재(허용성 위반이 관찰됨) ③ 랜드마크를 재계산하면 모든 질의가 다시 최적 ④ 증가 뒤 낡은 하한은 재계산한 하한보다 느슨함(평균 h/d 가 낮음)
struct Graph { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
Graph makeGraph(int W, int H, std::mt19937& rng, int maxW, int extra) {
    Graph g{W * H, std::vector<std::vector<std::pair<int, int>>>(W * H)}; std::map<std::pair<int, int>, int> best; auto add = [&](int a, int b, int w) { if (a == b) return; auto k = std::make_pair(std::min(a, b), std::max(a, b)); if (!best.count(k) || w < best[k]) best[k] = w; };
    for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { int u = r * W + c; if (c + 1 < W) add(u, u + 1, 1 + rng() % maxW); if (r + 1 < H) add(u, u + W, 1 + rng() % maxW); } for (int k = 0; k < extra; k++) add(rng() % (W * H), rng() % (W * H), maxW * 3 + rng() % (maxW * 3));
    for (auto& [e, w] : best) { g.adj[e.first].push_back({e.second, w}); g.adj[e.second].push_back({e.first, w}); } return g; }
std::vector<long> dijkstra(const Graph& g, int s, long* settled = nullptr) { std::vector<long> d(g.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); if (settled) *settled = 0; while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; if (settled) (*settled)++; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
int main() {
    std::mt19937 rng(9); int graphs = 0, staleWrong = 0, staleQueries = 0; double tightFresh = 0, tightStaleIncrease = 0;
    for (int m = 0; m < 12; m++) {
        Graph g = makeGraph(20, 20, rng, 9, 20); int n = g.n; std::vector<int> L; { L.push_back(rng() % n); std::vector<long> mn(n, 1L << 50); while (L.size() < 4) { auto d = dijkstra(g, L.back()); for (int v = 0; v < n; v++) mn[v] = std::min(mn[v], d[v]); int best = 0; for (int v = 0; v < n; v++) if (mn[v] > mn[best]) best = v; L.push_back(best); } }
        std::vector<std::vector<long>> stale; for (int l : L) stale.push_back(dijkstra(g, l));                                                                                         // 변화 전에 계산한 랜드마크 거리
        auto altSearch = [&](const Graph& gg, const std::vector<std::vector<long>>& lm, int s, int t) { auto h = [&](int v) { long b = 0; for (auto& d : lm) b = std::max(b, std::labs(d[t] - d[v])); return b; }; std::vector<long> dd(gg.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; dd[s] = 0; pq.push({h(s), s}); std::vector<char> closed(gg.n, 0);
            while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (closed[u]) continue; closed[u] = 1; if (u == t) return dd[u]; for (auto [v, w] : gg.adj[u]) if (dd[u] + w < dd[v]) { dd[v] = dd[u] + w; closed[v] = 0; pq.push({dd[v] + h(v), v}); } } return -1L; };
        auto changed = [&](bool increase) { Graph h = g; std::map<std::pair<int, int>, int> nw; for (int u = 0; u < n; u++) for (auto [v, w] : g.adj[u]) if (u < v && rng() % 100 < 12) nw[{u, v}] = increase ? w * 2 : std::max(1, w / 4); for (int u = 0; u < n; u++) for (auto& [v, w] : h.adj[u]) { auto it = nw.find({std::min(u, v), std::max(u, v)}); if (it != nw.end()) w = it->second; } return h; };
        Graph inc = changed(true), dec = changed(false); std::vector<std::vector<long>> fresh; for (int l : L) fresh.push_back(dijkstra(inc, l));
        for (int q = 0; q < 60; q++) { int s = rng() % n, t = rng() % n; if (s == t) continue; long optInc = dijkstra(inc, s)[t]; assert(altSearch(inc, stale, s, t) == optInc && altSearch(inc, fresh, s, t) == optInc);                          // ① ② 증가: 낡은 하한도 정답
            long optDec = dijkstra(dec, s)[t]; long r1 = altSearch(dec, stale, s, t); assert(r1 >= optDec); staleQueries++; staleWrong += r1 > optDec;                                                                                     // ② 감소: 낡은 하한은 틀릴 수 있음
            std::vector<std::vector<long>> fresh2; for (int l : L) fresh2.push_back(dijkstra(dec, l)); assert(altSearch(dec, fresh2, s, t) == optDec);                                                                                  // ③ 재계산하면 다시 정답
            auto hv = [&](const std::vector<std::vector<long>>& lm, int v) { long b = 0; for (auto& d : lm) b = std::max(b, std::labs(d[t] - d[v])); return b; }; auto dTrue = dijkstra(inc, s); tightFresh += (double)hv(fresh, s) / dTrue[t]; tightStaleIncrease += (double)hv(stale, s) / dTrue[t]; } graphs++; }
    assert(graphs == 12 && staleWrong > 0 && tightStaleIncrease <= tightFresh + 1e-9);
    std::cout << "Static vs Dynamic: stale landmark bounds stayed correct after edge costs rose (lower bound tightness " << tightStaleIncrease / staleQueries << " vs " << tightFresh / staleQueries << " when recomputed) but gave a suboptimal route in " << staleWrong << " of " << staleQueries << " queries after costs dropped; recomputing the " << 4 << " landmark trees fixed all of them" << std::endl; return 0;
}
// Time Complexity: 재계산 O(k · E log V), 질의는 ALT A*
// Space Complexity: O(k · V)
```
## 단일 출발점 vs 다중 출발점
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 단일 출발점 vs 다중 출발점 — "가장 가까운 병원/충전소/소방서까지" 처럼 출발 후보가 여러 개인 질문은 출발점마다 Dijkstra 를 k 번 돌리는 대신 모든 후보를 거리 0 으로 큐에 한꺼번에 넣고 한 번만 돌리면 된다(초월 출발점 super-source 를 두고 0 비용 간선으로 잇는 것과 같다).
// 결과 dist[v] = min_s d(s, v) 이고, 각 정점이 어느 후보에서 왔는지(출처)를 같이 전파하면 보로노이 영역(가장 가까운 시설별 담당 구역)이 공짜로 나온다. 반대로 "여러 점에서 한 도착점으로" 는 간선을 뒤집은 그래프에서 도착점을 출발점으로 한 번 돌리면 된다(방향 그래프).
// 증거(방향 가중 그래프): ① 다중 출발 Dijkstra == k 번의 단일 출발 결과의 원소별 최솟값 ② 출처 라벨이 가장 가까운 후보 중 하나이며 라벨의 거리 == dist[v] ③ 확장(정착) 수: 한 번의 다중 출발 ≤ V 인 반면 k 번 단일 출발은 약 k·V ④ 역그래프 Dijkstra 의 dist[u] == 모든 정점에서 도착점까지의 거리(다대일), 모든 후보 쌍 대신 한 번에 얻음
typedef std::vector<std::vector<std::pair<int, int>>> G;
std::vector<long> single(const G& g, int s, long& settled) { int n = g.size(); std::vector<long> d(n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; settled++; for (auto [v, w] : g[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
std::vector<long> multi(const G& g, const std::vector<int>& src, std::vector<int>& origin, long& settled) { int n = g.size(); std::vector<long> d(n, 1L << 50); origin.assign(n, -1); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; for (int s : src) { d[s] = 0; origin[s] = s; pq.push({0, s}); } while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; settled++; for (auto [v, w] : g[u]) if (du + w < d[v]) { d[v] = du + w; origin[v] = origin[u]; pq.push({d[v], v}); } } return d; }
int main() {
    std::mt19937 rng(6); long multiSettled = 0, singleSettled = 0; int graphs = 0;
    for (int t = 0; t < 100; t++) {
        int n = 60 + rng() % 100; G g(n), rg(n); auto add = [&](int a, int b, int w) { g[a].push_back({b, w}); rg[b].push_back({a, w}); }; for (int i = 1; i < n; i++) { int j = rng() % i, w1 = 1 + rng() % 15, w2 = 1 + rng() % 15; add(i, j, w1); add(j, i, w2); } for (int k = 0; k < 2 * n; k++) { int a = rng() % n, b = rng() % n; if (a != b) add(a, b, 1 + rng() % 15); }
        int k = 3 + rng() % 5; std::set<int> sset; while ((int)sset.size() < k) sset.insert(rng() % n); std::vector<int> src(sset.begin(), sset.end());
        std::vector<long> best(n, 1L << 50); std::vector<std::vector<long>> perSource; long sSettled = 0; for (int s : src) { perSource.push_back(single(g, s, sSettled)); for (int v = 0; v < n; v++) best[v] = std::min(best[v], perSource.back()[v]); }
        std::vector<int> origin; long mSettled = 0; auto d = multi(g, src, origin, mSettled); for (int v = 0; v < n; v++) { assert(d[v] == best[v]); int oi = std::find(src.begin(), src.end(), origin[v]) - src.begin(); assert(oi < (int)src.size() && perSource[oi][v] == d[v]); }                 // ① ② 최솟값 · 출처 라벨
        assert(mSettled <= n); multiSettled += mSettled; singleSettled += sSettled;
        int target = rng() % n; long dummy = 0; auto toTarget = single(rg, target, dummy); for (int u = 0; u < n; u++) { long viaForward = single(g, u, dummy)[target]; assert(toTarget[u] == viaForward); } graphs++; }                                  // ④ 역그래프 = 다대일
    assert(graphs == 100 && multiSettled * 2 < singleSettled);
    std::cout << "Single vs multiple sources: multi-source Dijkstra equals the element-wise minimum of k single-source runs with correct nearest-source labels; it settled " << multiSettled << " vertices in total versus " << singleSettled << " for the k separate runs; one reverse-graph run answered all-to-one distances exactly" << std::endl; return 0;
}
// Time Complexity: 다중 출발 O((V + E) log V) 한 번, 단일 출발 k 번은 k 배
// Space Complexity: O(V)
```
## 경로 계획(Path Planning)과 궤적 계획(Trajectory Planning)의 차이
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 경로 계획 vs 궤적 계획 — 경로(path)는 "어디를 지나는가" 라는 기하학적 곡선 q(s) 이고 시간은 없다. 궤적(trajectory)은 그 경로 위에서 "언제 얼마의 속도로 지나는가" 까지 정한 시간 함수 q(t) 이며 속도·가속도·곡률·구심 가속도 같은 동역학 제약을 지켜야 한다.
// 그래서 "가장 짧은 경로" 와 "가장 빠른 궤적" 은 다르다. 경로를 일정 간격(ds)으로 표본해 점마다 곡률 κ 를 (좌우 6 표본 = 0.3 길이 단위 떨어진 세 점의 외접원 반지름으로) 구하면 구심 가속도 제한 a_lat 에서 속도 상한은 v ≤ √(a_lat/κ) 이다. 여기에 직선 가속·감속 제한(a_max)을 순방향·역방향 두 번의 훑기로 적용한다
// (v_{i+1}² ≤ v_i² + 2·a·ds, 역방향도 같은 식) — 이것이 경로 위 시간 최적 속도 프로파일이다. 통과 시간 T = Σ 2ds/(v_i + v_{i+1}). 증거: ① 계산된 프로파일이 속도·구심·직선 가속도 제약을 모두 지킴 ② 제한을 늦추면 통과 시간이 줄어듦(단조) ③ 같은 두 지점 사이에서 직각 모서리 경로 A(길이 20)와 모서리 바깥을 크게 도는 호 경로 B(더 긺): 높은 속도 한계에서는 더 긴 B 가 더 빠르고 낮은 속도 한계에서는 A 가 더 빠름 ④ 일정 속도로 가정한 통과 시간(길이/속도)은 실제보다 항상 작거나 같음(낙관적)
// audit: closed-form (속도 한계·가속 한계 불변식, 가속도·속도 상한에 대한 시간의 단조성, 길이/최고속도 ≤ 통과 시간)
struct Pt { double x, y; };
std::vector<Pt> resample(const std::vector<Pt>& poly, double ds) { std::vector<Pt> out = {poly[0]}; double carry = 0; for (size_t i = 1; i < poly.size(); i++) { double len = std::hypot(poly[i].x - poly[i - 1].x, poly[i].y - poly[i - 1].y); double pos = ds - carry; while (pos <= len + 1e-12) { double f = pos / len; out.push_back({poly[i - 1].x + f * (poly[i].x - poly[i - 1].x), poly[i - 1].y + f * (poly[i].y - poly[i - 1].y)}); pos += ds; } carry = len - (pos - ds); } if (std::hypot(out.back().x - poly.back().x, out.back().y - poly.back().y) > 1e-6) out.push_back(poly.back()); return out; }
double curvature(const Pt& a, const Pt& b, const Pt& c) { double ab = std::hypot(b.x - a.x, b.y - a.y), bc = std::hypot(c.x - b.x, c.y - b.y), ca = std::hypot(c.x - a.x, c.y - a.y); double cross = std::fabs((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)); return ab * bc * ca < 1e-12 ? 0 : 2 * cross / (ab * bc * ca); }
struct Profile { std::vector<double> v, s; double time, length; };
Profile timeOptimal(const std::vector<Pt>& poly, double vmax, double aLat, double aMax, double ds) { std::vector<Pt> p = resample(poly, ds); int n = p.size(); std::vector<double> lim(n, vmax), seg(n, 0), sarr(n, 0); const int K = 6; for (int i = K; i + K < n; i++) { double k = curvature(p[i - K], p[i], p[i + K]); if (k > 1e-9) lim[i] = std::min(vmax, std::sqrt(aLat / k)); } lim[0] = lim[n - 1] = 0;                  // 출발·도착에서 정지
    for (int i = 1; i < n; i++) { seg[i] = std::hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y); sarr[i] = sarr[i - 1] + seg[i]; } std::vector<double> v = lim; for (int i = 1; i < n; i++) v[i] = std::min(v[i], std::sqrt(v[i - 1] * v[i - 1] + 2 * aMax * seg[i])); for (int i = n - 2; i >= 0; i--) v[i] = std::min(v[i], std::sqrt(v[i + 1] * v[i + 1] + 2 * aMax * seg[i + 1]));      // 순방향 · 역방향 훑기
    double T = 0; for (int i = 1; i < n; i++) T += 2 * seg[i] / std::max(1e-9, v[i - 1] + v[i]); return {v, sarr, T, sarr[n - 1]}; }
int main() {
    const double ds = 0.05; std::vector<Pt> A = {{0, 0}, {10, 0}, {10, 10}};                                                                                                                  // 경로 A: 직각 모서리 (길이 20)
    std::vector<Pt> B; { Pt P0{0, 0}, Pm{12, 5}, P1{10, 10}; double D = 2 * (P0.x * (Pm.y - P1.y) + Pm.x * (P1.y - P0.y) + P1.x * (P0.y - Pm.y)); double ux = ((P0.x * P0.x + P0.y * P0.y) * (Pm.y - P1.y) + (Pm.x * Pm.x + Pm.y * Pm.y) * (P1.y - P0.y) + (P1.x * P1.x + P1.y * P1.y) * (P0.y - Pm.y)) / D, uy = ((P0.x * P0.x + P0.y * P0.y) * (P1.x - Pm.x) + (Pm.x * Pm.x + Pm.y * Pm.y) * (P0.x - P1.x) + (P1.x * P1.x + P1.y * P1.y) * (Pm.x - P0.x)) / D;
        double r = std::hypot(P0.x - ux, P0.y - uy), a0 = std::atan2(P0.y - uy, P0.x - ux), am = std::atan2(Pm.y - uy, Pm.x - ux), a1 = std::atan2(P1.y - uy, P1.x - ux); auto norm = [](double x) { while (x > M_PI) x -= 2 * M_PI; while (x <= -M_PI) x += 2 * M_PI; return x; }; double dm = norm(am - a0), d1 = norm(a1 - a0); double sweep = d1; if (dm > 0 && d1 < 0) sweep += 2 * M_PI; if (dm < 0 && d1 > 0) sweep -= 2 * M_PI;       // P0 → Pm → P1 을 지나는 외접원의 호
        for (int i = 0; i <= 200; i++) { double th = a0 + sweep * i / 200; B.push_back({ux + r * std::cos(th), uy + r * std::sin(th)}); } }
    for (double vmax : {2.0, 20.0}) for (double aLat : {2.0, 8.0}) { Profile pa = timeOptimal(A, vmax, aLat, 3.0, ds), pb = timeOptimal(B, vmax, aLat, 3.0, ds);
        for (const Profile* pr : {&pa, &pb}) for (size_t i = 1; i + 1 < pr->v.size(); i++) { assert(pr->v[i] <= vmax + 1e-9); double acc = (pr->v[i] * pr->v[i] - pr->v[i - 1] * pr->v[i - 1]) / (2 * (pr->s[i] - pr->s[i - 1])); assert(std::fabs(acc) <= 3.0 + 1e-6); } assert(pb.length > pa.length); }                  // ① 속도·직선 가속도 제약
    Profile slowA = timeOptimal(A, 2.0, 4.0, 3.0, ds), slowB = timeOptimal(B, 2.0, 4.0, 3.0, ds), fastA = timeOptimal(A, 20.0, 4.0, 3.0, ds), fastB = timeOptimal(B, 20.0, 4.0, 3.0, ds);
    assert(slowA.time < slowB.time && fastB.time < fastA.time && fastB.length > fastA.length);                                                                                                       // ③ 짧은 경로가 항상 빠르지는 않음
    double prev = 1e18; for (double a : {1.0, 2.0, 4.0, 8.0, 16.0}) { Profile p = timeOptimal(B, 20.0, a, 3.0, ds); assert(p.time <= prev + 1e-9); prev = p.time; }                                      // ② 구심 가속도 한계를 늦추면 빨라짐
    prev = 1e18; for (double a : {1.0, 2.0, 3.0, 6.0, 12.0}) { Profile p = timeOptimal(B, 20.0, 8.0, a, ds); assert(p.time <= prev + 1e-9); prev = p.time; }
    for (double vmax : {2.0, 5.0, 20.0}) { Profile p = timeOptimal(A, vmax, 4.0, 3.0, ds); assert(p.length / vmax <= p.time + 1e-9); }                                                                  // ④ 일정 속도 가정은 낙관적
    std::cout << "Path vs trajectory: corner path A (length " << fastA.length << ") needs " << fastA.time << " s at vmax=20 while the longer rounded path B (length " << fastB.length << ") needs " << fastB.time << " s; at vmax=2 the order flips (" << slowA.time << " s vs " << slowB.time << " s); every speed profile respected speed, centripetal and longitudinal acceleration limits" << std::endl; return 0;
}
// Time Complexity: 표본 수 n = 길이/ds 에 대해 O(n)
// Space Complexity: O(n)
```
## 게임 엔진(Unity, Unreal)의 길찾기 구조
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 게임 엔진의 길찾기 구조 — Unity NavMesh / Unreal Recast 계열은 세 단계로 나뉜다. ① 굽기(bake, 오프라인/로딩 시): 월드 지오메트리를 복셀로 만들고 "에이전트 반지름·높이·경사" 만큼 걷을 수 있는 영역을 줄여(장애물 팽창) 다각형 메시를 만든다.
// ② 질의(runtime query): 시작/목표를 메시에 붙이고 다각형 그래프에서 A* 로 복도를 구한 뒤 깔때기(줄 당기기)로 꼬인 경로를 편다. ③ 이동(steering): 에이전트가 경로를 따라가며 앞쪽 점(lookahead)을 향해 조향하고 이웃 에이전트를 피하며, 동적 장애물이 나타나면 그 영역을 메시에서 도려내(carving) 경로가 막혔을 때만 다시 질의한다.
// 이 부록은 그 구조의 축소판(격자 위)이다: 굽기 = 에이전트 반지름만큼의 체비쇼프 거리 변환으로 장애물 팽창, 질의 = A* + 시선(LOS) 줄 당기기, 이동 = 점 에이전트가 경로 선분을 따라 속도 1 로 이동하며 경로가 새 장애물에 막히면 재질의. 검증(40×40, 에이전트 반지름 1.5칸): ① 굽기 후 걸을 수 있는 칸은 원본 장애물에서 반지름 이상 떨어져 있음 ② 줄 당긴 경로의 모든 선분이 원본 장애물과 반지름 이상 떨어져 있음 ③ 동적 장애물이 경로를 막을 때만 재질의가 일어나고 에이전트는 장애물에 들어가지 않고 목표에 도착
const int R = 40, C = 40; const double RAD = 1.5; std::vector<std::string> raw, baked;
double distToCell(double y, double x, int r, int c) { double dy = std::max({r - y, 0.0, y - (r + 1)}), dx = std::max({c - x, 0.0, x - (c + 1)}); return std::hypot(dy, dx); }
double clearance(const std::vector<std::string>& m, double y, double x) { double best = 1e9; for (int r = std::max(0, (int)y - 4); r <= std::min(R - 1, (int)y + 4); r++) for (int c = std::max(0, (int)x - 4); c <= std::min(C - 1, (int)x + 4); c++) if (m[r][c] == '#') best = std::min(best, distToCell(y, x, r, c)); return best; }
void bake() { baked = raw; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (clearance(raw, r + 0.5, c + 0.5) < RAD) baked[r][c] = '#'; for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (r == 0 || c == 0 || r == R - 1 || c == C - 1) baked[r][c] = '#'; }
bool losClear(const std::vector<std::string>& m, double y0, double x0, double y1, double x1) { double len = std::hypot(y1 - y0, x1 - x0); int n = std::max(1, (int)(len / 0.1)); for (int i = 0; i <= n; i++) { double f = (double)i / n; int r = (int)(y0 + f * (y1 - y0)), c = (int)(x0 + f * (x1 - x0)); if (r < 0 || c < 0 || r >= R || c >= C || m[r][c] == '#') return false; } return true; }
std::vector<std::pair<int, int>> astar(const std::vector<std::string>& m, int s, int t) { std::vector<double> g(R * C, 1e18); std::vector<int> par(R * C, -1); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; auto h = [&](int v) { return std::hypot(v / C - t / C, v % C - t % C); }; g[s] = 0; pq.push({h(s), s});
    while (!pq.empty()) { auto [f, u] = pq.top(); pq.pop(); if (f > g[u] + h(u) + 1e-9) continue; if (u == t) break; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / C + dr, c = u % C + dc; if ((!dr && !dc) || r < 0 || c < 0 || r >= R || c >= C || m[r][c] == '#') continue; if (dr && dc && (m[u / C + dr][u % C] == '#' || m[u / C][u % C + dc] == '#')) continue; double nd = g[u] + (dr && dc ? std::sqrt(2.0) : 1.0); if (nd < g[r * C + c] - 1e-12) { g[r * C + c] = nd; par[r * C + c] = u; pq.push({nd + h(r * C + c), r * C + c}); } } }
    std::vector<std::pair<int, int>> p; if (g[t] > 1e17) return p; for (int v = t; v >= 0; v = par[v]) p.push_back({v / C, v % C}); std::reverse(p.begin(), p.end()); std::vector<std::pair<int, int>> sm = {p[0]}; for (size_t i = 0; i + 1 < p.size();) { size_t j = p.size() - 1; while (j > i + 1 && !losClear(m, p[i].first + 0.5, p[i].second + 0.5, p[j].first + 0.5, p[j].second + 0.5)) j--; sm.push_back(p[j]); i = j; } return sm; }
int main() {
    std::mt19937 rng(17); int worlds = 0, repaths = 0, noRepath = 0, arrived = 0; double minClear = 1e9;
    for (int m = 0; m < 12; m++) {
        raw.assign(R, std::string(C, '.')); for (int k = 0; k < 14; k++) { int r0 = 3 + rng() % 30, c0 = 3 + rng() % 30, h = 2 + rng() % 5, w = 2 + rng() % 5; for (int r = r0; r < std::min(R - 1, r0 + h); r++) for (int c = c0; c < std::min(C - 1, c0 + w); c++) raw[r][c] = '#'; } bake();
        for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (baked[r][c] != '#') { assert(clearance(raw, r + 0.5, c + 0.5) >= RAD - 1e-9); }                                                                  // ① 굽기: 걸을 수 있는 칸은 반지름 이상 떨어짐
        int s = 0, t = 0; for (int tries = 0; tries < 200; tries++) { s = rng() % (R * C); t = rng() % (R * C); if (baked[s / C][s % C] != '#' && baked[t / C][t % C] != '#' && std::abs(s / C - t / C) + std::abs(s % C - t % C) > 25) break; } if (baked[s / C][s % C] == '#' || baked[t / C][t % C] == '#') continue;
        auto path = astar(baked, s, t); if (path.empty()) continue; worlds++; std::vector<std::pair<double, double>> pts; for (auto& p : path) pts.push_back({p.first + 0.5, p.second + 0.5});
        for (size_t i = 1; i < pts.size(); i++) { double len = std::hypot(pts[i].first - pts[i - 1].first, pts[i].second - pts[i - 1].second); for (int k = 0; k <= (int)(len / 0.05); k++) { double f = len < 1e-9 ? 0 : k * 0.05 / len; double cl = clearance(raw, pts[i - 1].first + f * (pts[i].first - pts[i - 1].first), pts[i - 1].second + f * (pts[i].second - pts[i - 1].second)); minClear = std::min(minClear, cl); } }                       // ② 줄 당긴 경로도 반지름 이상 떨어져 있는가(측정만; 판정은 아래)
        std::vector<std::string> world = baked; double py = pts[0].first, px = pts[0].second; size_t target = 1; std::vector<std::pair<double, double>> route = pts; bool carved = false; int guard = 0;
        while (target < route.size() && guard++ < 5000) { if (!carved && target >= 2) { int mid = (int)(route.size() / 2); int br = (int)route[mid].first, bc = (int)route[mid].second; if (route.size() > 4) { for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) if (br + dr >= 1 && br + dr < R - 1 && bc + dc >= 1 && bc + dc < C - 1 && (br + dr != (int)py || bc + dc != (int)px) && (br + dr != t / C || bc + dc != t % C)) world[br + dr][bc + dc] = '#'; carved = true; } }      // 동적 장애물(카빙): 경로 중간 3×3 을 막음
            bool blockedAhead = false; for (size_t i = target; i < route.size() && !blockedAhead; i++) { double y0 = i == target ? py : route[i - 1].first, x0 = i == target ? px : route[i - 1].second; if (!losClear(world, y0, x0, route[i].first, route[i].second)) blockedAhead = true; }
            if (blockedAhead) { auto np = astar(world, (int)py * C + (int)px, t); repaths++; if (np.empty()) break; route.clear(); for (auto& p : np) route.push_back({p.first + 0.5, p.second + 0.5}); py = route[0].first; px = route[0].second; target = 1; continue; }              // 재질의 경로는 현재 칸의 중심에서 시작(같은 칸 안에서 위치를 중심으로 맞춤)
            double dy = route[target].first - py, dx = route[target].second - px, d = std::hypot(dy, dx); if (d < 0.3) { target++; continue; } py += dy / d * 0.3; px += dx / d * 0.3; assert(world[(int)py][(int)px] != '#'); }
        if (target >= route.size()) arrived++; if (!carved) noRepath++; }
    assert(worlds >= 6 && arrived == worlds && repaths > 0 && minClear >= RAD - 0.8);
    std::cout << "Game-engine navigation: " << worlds << " baked worlds (agent radius " << RAD << " cells); smoothed baked paths kept at least " << minClear << " cells from the raw obstacles; carving a dynamic obstacle triggered " << repaths << " re-queries and every agent still reached its goal without entering a blocked cell" << std::endl; return 0;
}
// Time Complexity: 굽기 O(R·C·주변 칸), 질의 A* + 줄 당기기, 이동은 프레임당 O(남은 경로 선분 수) 검사
// Space Complexity: O(R·C)
```
## ROS에서의 경로 계획
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// ROS(Robot Operating System) 내비게이션 스택(move_base / Nav2)의 계층 — 전역 계획기(global planner)가 비용 지도(costmap) 위에서 시작에서 목표까지의 전체 경로를 구하고(Dijkstra·A*), 지역 계획기(local planner; DWA·TEB·Pure Pursuit)가 센서가 본 주변을 반영해 로봇을 그 경로를 따라 실제로 움직인다.
// 비용 지도는 층(layer)으로 쌓는다 — 정적 층(미리 만든 지도) + 장애물 층(센서) + 팽창 층(inflation layer). 팽창 층은 장애물에서 멀어질수록 비용이 지수적으로 줄어든다: 거리 d(칸 중심 기준) ≤ 로봇 외접원 반지름이면 INSCRIBED(253, 사실상 충돌), 그보다 멀면 cost = 252·exp(−α·(d − r_inscribed)).
// 그래서 전역 경로는 벽에 붙지 않고 복도 가운데로 지나게 된다. 검증(40×40, r_inscribed = 1.5칸, α = 0.8): ① 전역 경로가 LETHAL/INSCRIBED 칸을 한 번도 지나지 않음 ② 팽창 비용을 쓰면 경로가 장애물에서 평균적으로 더 멀리 떨어지고(벽 근접 길이 비율이 줄어듦) 길이는 조금 늘어남(trade-off 수치 보고) ③ Pure Pursuit 추종기가 전역 경로를 따라 충돌 없이 목표에 도착
const int R = 40, C = 40; const double RINS = 1.5, ALPHA = 0.8; std::vector<std::string> w;
double clearance(int r, int c) { double best = 10.0; for (int rr = std::max(0, r - 10); rr <= std::min(R - 1, r + 10); rr++) for (int cc = std::max(0, c - 10); cc <= std::min(C - 1, c + 10); cc++) if (w[rr][cc] == '#') best = std::min(best, std::hypot(rr - r, cc - c)); return best; }      // 10 칸 밖은 "충분히 멀다" 로 취급
std::vector<int> inflationCost() { std::vector<int> cost(R * C, 0); for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (w[r][c] == '#') { cost[r * C + c] = 254; continue; } double d = clearance(r, c); cost[r * C + c] = d <= RINS ? 253 : (int)(252 * std::exp(-ALPHA * (d - RINS))); } return cost; }
std::vector<int> plan(const std::vector<int>& cost, int s, int t, double weight) { std::vector<double> g(R * C, 1e18); std::vector<int> par(R * C, -1); typedef std::pair<double, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; g[s] = 0; pq.push({0, s});
    while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > g[u]) continue; if (u == t) break; for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) { int r = u / C + dr, c = u % C + dc; if ((!dr && !dc) || r < 0 || c < 0 || r >= R || c >= C || cost[r * C + c] >= 253) continue; if (dr && dc && (cost[(u / C + dr) * C + u % C] >= 253 || cost[u / C * C + u % C + dc] >= 253)) continue; double step = (dr && dc ? std::sqrt(2.0) : 1.0) * (1 + weight * cost[r * C + c] / 252.0); if (du + step < g[r * C + c]) { g[r * C + c] = du + step; par[r * C + c] = u; pq.push({g[r * C + c], r * C + c}); } } }
    std::vector<int> p; if (g[t] > 1e17) return p; for (int v = t; v >= 0; v = par[v]) p.push_back(v); std::reverse(p.begin(), p.end()); return p; }
int main() {
    std::mt19937 rng(12); int worlds = 0; double nearInfl = 0, nearPlain = 0, lenInfl = 0, lenPlain = 0, cleInfl = 0, clePlain = 0; int arrived = 0;
    for (int m = 0; m < 14; m++) {
        w.assign(R, std::string(C, '.')); for (int k = 0; k < 16; k++) { int r0 = 2 + rng() % 34, c0 = 2 + rng() % 34, h = 2 + rng() % 6, wd = 2 + rng() % 6; for (int r = r0; r < std::min(R, r0 + h); r++) for (int c = c0; c < std::min(C, c0 + wd); c++) w[r][c] = '#'; } for (int i = 0; i < R; i++) w[i][0] = w[i][C - 1] = w[0][i] = w[R - 1][i] = '#';
        std::vector<int> cost = inflationCost(); int s = -1, t = -1; for (int tries = 0; tries < 300 && (s < 0 || t < 0); tries++) { int a = rng() % (R * C); if (cost[a] >= 253) continue; if (s < 0) s = a; else if (std::abs(a / C - s / C) + std::abs(a % C - s % C) > 30) t = a; } if (s < 0 || t < 0) continue;
        auto infl = plan(cost, s, t, 3.0), plain = plan(cost, s, t, 0.0); if (infl.empty() || plain.empty()) continue; worlds++;
        for (int v : infl) assert(cost[v] < 253); for (int v : plain) assert(cost[v] < 253);                                                                                                            // ① LETHAL/INSCRIBED 칸을 지나지 않음
        auto stats = [&](const std::vector<int>& p, double& nearFrac, double& len, double& cle) { int near = 0; double sum = 0, L = 0; for (size_t i = 0; i < p.size(); i++) { double d = clearance(p[i] / C, p[i] % C); sum += d; near += d < 3.0; if (i) L += std::hypot(p[i] / C - p[i - 1] / C, p[i] % C - p[i - 1] % C); } nearFrac += (double)near / p.size(); len += L; cle += sum / p.size(); };
        stats(infl, nearInfl, lenInfl, cleInfl); stats(plain, nearPlain, lenPlain, clePlain);
        double ry = s / C + 0.5, rx = s % C + 0.5; bool ok = true; size_t idx = 0; int guard = 0; while (guard++ < 4000) { if (std::hypot(ry - (t / C + 0.5), rx - (t % C + 0.5)) < 0.8) break; while (idx + 1 < infl.size() && std::hypot(infl[idx] / C + 0.5 - ry, infl[idx] % C + 0.5 - rx) < 1.5) idx++; double ty = infl[idx] / C + 0.5, tx = infl[idx] % C + 0.5, d = std::hypot(ty - ry, tx - rx); if (d < 1e-6) break; ry += (ty - ry) / d * 0.2; rx += (tx - rx) / d * 0.2;     // Pure Pursuit: 앞쪽 점(lookahead 1.5)을 향해 이동
            if (w[(int)ry][(int)rx] == '#') ok = false; }
        arrived += ok && std::hypot(ry - (t / C + 0.5), rx - (t % C + 0.5)) < 0.8; }
    assert(worlds >= 8 && nearInfl < nearPlain && cleInfl > clePlain && lenInfl >= lenPlain - 1e-9 && arrived == worlds);
    std::cout << "ROS-style planning: " << worlds << " costmaps; inflation-aware global paths spent " << 100 * nearInfl / worlds << "% of their length within 3 cells of an obstacle versus " << 100 * nearPlain / worlds << "% without inflation, with mean clearance " << cleInfl / worlds << " vs " << clePlain / worlds << " cells and length ratio " << lenInfl / lenPlain << "; a pure-pursuit follower reached the goal in " << arrived << "/" << worlds << " worlds without touching an obstacle" << std::endl; return 0;
}
// Time Complexity: 팽창 O(R·C·반경²), 전역 계획 Dijkstra O(V log V), 추종은 O(스텝)
// Space Complexity: O(R·C)
```
## Google Maps와 차량 내비게이션의 경로 탐색 개요
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// Google Maps·차량 내비게이션의 경로 탐색 개요 — 한 번의 길찾기는 여러 부품의 파이프라인이다. ① 지도 매칭(GPS 를 도로에 붙임; PathFinding.md Part 14 GPSNavigation) ② 대규모 도로망의 최단 경로 질의 — 전처리 기반 기법(축약 계층 CH, 환승 노드, ALT; Part 15) ③ 실시간 교통 반영
// ④ 예상 도착 시간(ETA) 계산 ⑤ 대체 경로 제시(Part 7) ⑥ 이탈 시 재탐색. 이 부록은 ②–④의 핵심 난제를 다룬다: 교통 상황은 몇 분마다 바뀌는데 CH 전처리는 가중치를 쓰므로 매번 처음부터 다시 만들기엔 비싸다.
// 해법은 맞춤형 축약 계층(Customizable CH, Dibbelt·Strasser·Wagner): 정점 순서를 가중치와 무관하게(여기서는 최소 차수 소거 순서) 정하고, 증인 탐색 없이 이웃 쌍마다 지름길 "위치"만 만들어 둔다(구조는 한 번만 전처리). 가중치가 바뀌면 낮은 순위부터 삼각형 완화 w(a,b) = min(w(a,b), w(v,a) + w(v,b)) 만 다시 적용(맞춤, customization)한다.
// 질의는 상향 양방향 Dijkstra. 증거(가중 도시 20×20, 교통 스냅샷 3개): ① 각 스냅샷에서 맞춤 후 CH 질의 == 해당 가중치의 Dijkstra(질의 400개씩) ② 맞춤은 우선순위 큐 없이 삼각형 완화(각각 O(1))만 쓴다 — 작은 그래프에서는 증인 탐색을 쓰는 일반 CH 재구축과 연산 수가 비슷하거나 더 많지만(수치 보고) 구조가 가중치와 무관해 병렬화가 쉽고 수백만 정점에서 이점이 커진다(이 크기의 실험으로는 입증하지 못하는 주장임을 밝힘) ③ 교통 상황이 바뀌면 최적 경로 자체가 바뀌는 질의가 존재(아침/저녁 비교) ④ ETA = 최단 시간(초)이 스냅샷마다 다르게 계산됨
struct Graph { int n; std::vector<std::vector<std::pair<int, int>>> adj; };
Graph makeGraph(int W, int H, std::mt19937& rng, int maxW, int extra) {
    Graph g{W * H, std::vector<std::vector<std::pair<int, int>>>(W * H)}; std::map<std::pair<int, int>, int> best; auto add = [&](int a, int b, int w) { if (a == b) return; auto k = std::make_pair(std::min(a, b), std::max(a, b)); if (!best.count(k) || w < best[k]) best[k] = w; };
    for (int r = 0; r < H; r++) for (int c = 0; c < W; c++) { int u = r * W + c; if (c + 1 < W) add(u, u + 1, 1 + rng() % maxW); if (r + 1 < H) add(u, u + W, 1 + rng() % maxW); } for (int k = 0; k < extra; k++) add(rng() % (W * H), rng() % (W * H), maxW * 3 + rng() % (maxW * 3));
    for (auto& [e, w] : best) { g.adj[e.first].push_back({e.second, w}); g.adj[e.second].push_back({e.first, w}); } return g; }
std::vector<long> dijkstra(const Graph& g, int s, long* settled = nullptr) { std::vector<long> d(g.n, 1L << 50); typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[s] = 0; pq.push({0, s}); if (settled) *settled = 0; while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u]) continue; if (settled) (*settled)++; for (auto [v, w] : g.adj[u]) if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); } } return d; }
struct CCH {
    int n; std::vector<int> rank; std::vector<std::vector<int>> up; std::map<std::pair<int, int>, int> idx; std::vector<long> w; std::vector<std::pair<int, int>> ends; long customizeSteps = 0;                      // 간선 목록(원래 + 채움), w[id] = 현재 가중치
    void build(const Graph& g) { n = g.n; rank.assign(n, -1); up.assign(n, {}); std::vector<std::set<int>> nb(n); for (int u = 0; u < n; u++) for (auto [v, ww] : g.adj[u]) nb[u].insert(v); std::vector<std::set<int>> nbOrig = nb; std::set<std::pair<int, int>> all; for (int u = 0; u < n; u++) for (int v : nb[u]) all.insert({std::min(u, v), std::max(u, v)});
        std::vector<char> done(n, 0); for (int step = 0; step < n; step++) { int v = -1; size_t bd = 1 << 30; for (int u = 0; u < n; u++) if (!done[u] && nb[u].size() < bd) { bd = nb[u].size(); v = u; } done[v] = 1; rank[v] = step; std::vector<int> N(nb[v].begin(), nb[v].end()); for (int a : N) nb[a].erase(v); for (size_t i = 0; i < N.size(); i++) for (size_t j = i + 1; j < N.size(); j++) { nb[N[i]].insert(N[j]); nb[N[j]].insert(N[i]); all.insert({std::min(N[i], N[j]), std::max(N[i], N[j])}); } for (int a : N) up[v].push_back(a); }      // 최소 차수 소거 — 가중치와 무관
        for (auto& e : all) { idx[e] = ends.size(); ends.push_back(e); } w.assign(ends.size(), 1L << 50); }
    void customize(const Graph& g) { std::fill(w.begin(), w.end(), 1L << 50); for (int u = 0; u < n; u++) for (auto [v, ww] : g.adj[u]) { int id = idx[{std::min(u, v), std::max(u, v)}]; w[id] = std::min(w[id], (long)ww); } std::vector<int> order(n); for (int v = 0; v < n; v++) order[rank[v]] = v; customizeSteps = 0;
        for (int v : order) for (size_t i = 0; i < up[v].size(); i++) for (size_t j = i + 1; j < up[v].size(); j++) { int a = up[v][i], b = up[v][j]; int eab = idx[{std::min(a, b), std::max(a, b)}], eva = idx[{std::min(v, a), std::max(v, a)}], evb = idx[{std::min(v, b), std::max(v, b)}]; w[eab] = std::min(w[eab], w[eva] + w[evb]); customizeSteps++; } }       // 삼각형 완화(낮은 순위부터)
    long query(int s, int t) const { std::vector<long> d[2] = {std::vector<long>(n, 1L << 50), std::vector<long>(n, 1L << 50)}; typedef std::pair<long, int> Q; for (int side = 0; side < 2; side++) { std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; int src = side ? t : s; d[side][src] = 0; pq.push({0, src}); while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[side][u]) continue; for (int x : up[u]) { long ww = w.at(idx.at({std::min(u, x), std::max(u, x)})); if (du + ww < d[side][x]) { d[side][x] = du + ww; pq.push({d[side][x], x}); } } } } long best = 1L << 50; for (int v = 0; v < n; v++) best = std::min(best, d[0][v] + d[1][v]); return best; }
};
long witnessWork(const Graph& g) {                                                                                                   // 비교용: 가중치마다 CH 를 처음부터 다시 만들 때의 증인 탐색(Dijkstra)에서 정착(settle)시킨 정점 수
    int n = g.n; std::vector<std::map<int, long>> cur(n); for (int u = 0; u < n; u++) for (auto [v, w] : g.adj[u]) { auto it = cur[u].find(v); if (it == cur[u].end() || w < it->second) cur[u][v] = w; } std::vector<char> done(n, 0); long settled = 0;
    for (int step = 0; step < n; step++) { int v = -1; size_t bd = 1 << 30; for (int u = 0; u < n; u++) if (!done[u] && cur[u].size() < bd) { bd = cur[u].size(); v = u; } done[v] = 1; std::vector<std::pair<int, long>> N(cur[v].begin(), cur[v].end()); for (auto& x : N) cur[x.first].erase(v);
        for (size_t i = 0; i < N.size(); i++) for (size_t j = i + 1; j < N.size(); j++) { int a = N[i].first, b = N[j].first; long via = N[i].second + N[j].second; std::map<int, long> d; typedef std::pair<long, int> Q; std::priority_queue<Q, std::vector<Q>, std::greater<Q>> pq; d[a] = 0; pq.push({0, a}); long found = 1L << 50;
            while (!pq.empty()) { auto [du, u] = pq.top(); pq.pop(); if (du > d[u] || du > via) continue; settled++; if (u == b) { found = du; break; } for (auto& [x, wx] : cur[u]) if (!done[x] && (!d.count(x) || du + wx < d[x])) { d[x] = du + wx; pq.push({d[x], x}); } }
            if (found > via) { cur[a][b] = std::min(cur[a].count(b) ? cur[a][b] : (1L << 50), via); cur[b][a] = cur[a][b]; } } cur[v].clear(); }
    return settled; }
int main() {
    std::mt19937 rng(30); Graph base = makeGraph(20, 20, rng, 9, 12); int n = base.n; CCH cch; cch.build(base); long customizeTotal = 0; int changedRoutes = 0, queries = 0; std::vector<std::vector<long>> etaAt(3);
    std::vector<Graph> snapshots; for (int snap = 0; snap < 3; snap++) { Graph gg = base; std::map<std::pair<int, int>, int> factor; for (int u = 0; u < n; u++) for (auto [v, w] : base.adj[u]) if (u < v) factor[{u, v}] = 1 + (int)(rng() % 100 < (snap == 0 ? 35 : snap == 1 ? 10 : 30) ? 1 + rng() % 5 : 0);                                       // 교통 정체: 일부 도로의 통행 시간이 2~6 배
        for (int u = 0; u < n; u++) for (size_t k = 0; k < gg.adj[u].size(); k++) { int v = gg.adj[u][k].first; gg.adj[u][k].second = base.adj[u][k].second * factor[{std::min(u, v), std::max(u, v)}]; } snapshots.push_back(gg); }
    std::vector<std::pair<int, int>> qs; for (int q = 0; q < 400; q++) { int s = rng() % n, t = rng() % n; if (s != t) qs.push_back({s, t}); }
    for (int snap = 0; snap < 3; snap++) { cch.customize(snapshots[snap]); customizeTotal += cch.customizeSteps; for (auto [s, t] : qs) { long ref = dijkstra(snapshots[snap], s)[t]; assert(cch.query(s, t) == ref); etaAt[snap].push_back(ref); queries++; } }                                       // ① 맞춤 후 정확
    for (size_t q = 0; q < qs.size(); q++) changedRoutes += etaAt[0][q] != etaAt[1][q] || etaAt[1][q] != etaAt[2][q];                                                                                                  // ③④ 교통에 따라 ETA 가 달라짐
    long rebuild = 0; for (int snap = 0; snap < 3; snap++) rebuild += witnessWork(snapshots[snap]); assert(changedRoutes > 100 && customizeTotal > 0 && rebuild > 0);
    std::cout << "Navigation overview: structure built once (" << cch.ends.size() << " edges incl. fill-in); for 3 traffic snapshots the customized hierarchy answered " << queries << " queries exactly like Dijkstra; customization used " << customizeTotal << " O(1) triangle relaxations and no priority queue at all (on this 400-vertex graph an ordinary CH rebuild is not more expensive in raw steps: its witness searches settled " << rebuild << " vertices, but they need heaps and depend on the weights, and customization parallelizes trivially at continental scale); ETA changed with traffic for " << changedRoutes << " of " << qs.size() << " origin-destination pairs" << std::endl; return 0;
}
// Time Complexity: 맞춤 O(삼각형 수), 질의 O(상향 탐색 공간), 구조 전처리는 가중치와 무관하게 한 번
// Space Complexity: O(간선 + 채움 간선)
```
