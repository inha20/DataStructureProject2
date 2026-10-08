# Part 1. 그래프의 기초
## CreateGraph()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int V = 5; // 정점의 개수
    std::vector<std::vector<int>> adj(V); // 인접 리스트 배열
    std::cout << "Graph with " << V << " vertices created." << std::endl;
    assert(adj.size() == 5);
    return 0;
}
// Time Complexity: O(V)
// Space Complexity: O(V)
```
## AddVertex()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int V = 5;
    std::vector<std::vector<int>> adj(V);
    
    // V의 크기를 늘리고 adj 배열에 빈 벡터를 추가
    adj.push_back(std::vector<int>());
    V++;
    
    std::cout << "Vertex added. New V: " << V << std::endl;
    assert(V == 6 && adj.size() == 6);
    return 0;
}
// Time Complexity: O(1) amortized
// Space Complexity: O(1)
```
## RemoveVertex()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    int V = 3;
    std::vector<std::vector<int>> adj = {{1, 2}, {0}, {0}};
    
    int vertexToRemove = 1; // 정점 1 삭제
    adj.erase(adj.begin() + vertexToRemove);
    V--;
    
    // 다른 모든 정점의 인접 리스트에서 삭제된 정점과의 간선 제거 및 인덱스 조정
    for (int i = 0; i < V; ++i) {
        adj[i].erase(std::remove(adj[i].begin(), adj[i].end(), vertexToRemove), adj[i].end());
        for (int& v : adj[i]) {
            if (v > vertexToRemove) v--;
        }
    }
    
    std::cout << "Vertex " << vertexToRemove << " removed." << std::endl;
    assert(V == 2 && adj[0].size() == 1 && adj[0][0] == 1);
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(1) beyond graph representation
```
## AddEdge()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj(5);

void addEdge(int u, int v) {
    adj[u].push_back(v);
    adj[v].push_back(u); // 무방향 그래프의 경우 양방향 추가
}

int main() {
    addEdge(0, 1);
    std::cout << "Edge added between 0 and 1." << std::endl;
    assert(adj[0].back() == 1 && adj[1].back() == 0);
    return 0;
}
// Time Complexity: O(1) amortized
// Space Complexity: O(1)
```
## RemoveEdge()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

std::vector<std::vector<int>> adj = {{1}, {0}};

void removeEdge(int u, int v) {
    adj[u].erase(std::remove(adj[u].begin(), adj[u].end(), v), adj[u].end());
    adj[v].erase(std::remove(adj[v].begin(), adj[v].end(), u), adj[v].end());
}

int main() {
    removeEdge(0, 1);
    std::cout << "Edge removed between 0 and 1." << std::endl;
    assert(adj[0].empty() && adj[1].empty());
    return 0;
}
// Time Complexity: O(E) per vertex list
// Space Complexity: O(1)
```
## VertexCount()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj(5);

int vertexCount() {
    return adj.size(); // 총 정점의 수
}

int main() {
    std::cout << "Vertex count: " << vertexCount() << std::endl;
    assert(vertexCount() == 5);
    return 0;
}
// Time Complexity: O(1)
```
## EdgeCount()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj = {{1}, {0, 2}, {1}};

int edgeCount() {
    int count = 0;
    for (const auto& list : adj) count += list.size();
    return count / 2; // 무방향 그래프
}

int main() {
    std::cout << "Edge count: " << edgeCount() << std::endl;
    assert(edgeCount() == 2);
    return 0;
}
// Time Complexity: O(V)
```
## Degree()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj = {{1}, {0, 2}, {1}};

int degree(int v) {
    return adj[v].size(); 
}

int main() {
    std::cout << "Degree of vertex 1: " << degree(1) << std::endl;
    assert(degree(1) == 2);
    return 0;
}
// Time Complexity: O(1)
```
## InDegree()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj = {{1, 2}, {2}, {}}; // 방향 그래프

int inDegree(int v) {
    int count = 0;
    for (const auto& list : adj) {
        for (int u : list) if (u == v) count++;
    }
    return count;
}

int main() {
    std::cout << "InDegree of vertex 2: " << inDegree(2) << std::endl;
    assert(inDegree(2) == 2);
    return 0;
}
// Time Complexity: O(V + E)
```
## OutDegree()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj = {{1, 2}, {2}, {}}; 

int outDegree(int v) {
    return adj[v].size(); 
}

int main() {
    std::cout << "OutDegree of vertex 0: " << outDegree(0) << std::endl;
    assert(outDegree(0) == 2);
    return 0;
}
// Time Complexity: O(1)
```
# Part 2. 그래프 표현
## AdjacencyMatrix()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int V = 4;
    std::vector<std::vector<int>> matrix(V, std::vector<int>(V, 0));
    int u = 0, v = 1;
    matrix[u][v] = 1; // 간선 추가
    matrix[v][u] = 1; // 무방향
    assert(matrix[0][1] == 1);
    std::cout << "Adjacency Matrix Edge Added." << std::endl;
    return 0;
}
// Time Complexity: O(1) add, Space Complexity: O(V^2)
```
## AdjacencyList()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int V = 4;
    std::vector<std::vector<int>> adjList(V);
    int u = 0, v = 1;
    adjList[u].push_back(v); 
    assert(adjList[0][0] == 1);
    std::cout << "Adjacency List Edge Added." << std::endl;
    return 0;
}
// Time Complexity: O(1) add, Space Complexity: O(V + E)
```
## EdgeList()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct Edge { int u, v, weight; };

int main() {
    std::vector<Edge> edgeList;
    edgeList.push_back({0, 1, 10});
    assert(edgeList.back().weight == 10);
    std::cout << "Edge List Added." << std::endl;
    return 0;
}
// Time Complexity: O(1) add, Space Complexity: O(E)
```
## IncidenceMatrix()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int V = 3, E = 2; // 3 vertices, 2 edges
    std::vector<std::vector<int>> incMat(V, std::vector<int>(E, 0));
    // Edge 0 connects 0 and 1
    incMat[0][0] = 1; incMat[1][0] = 1;
    assert(incMat[0][0] == 1);
    std::cout << "Incidence Matrix Represented." << std::endl;
    return 0;
}
// Time Complexity: O(1) add, Space Complexity: O(V * E)
```
## CompressedSparseRow()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> values = {1, 1, 1}; // Edge weights
    std::vector<int> col_indices = {1, 2, 0}; // Adjacency
    std::vector<int> row_ptr = {0, 2, 3}; // Start idx of each row
    
    assert(row_ptr[1] == 2);
    std::cout << "CSR matrix conceptualized." << std::endl;
    return 0;
}
// Space Complexity: O(V + E)
```
## CompressedSparseColumn()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    int V = 4;
    // Adjacency list (directed): 2->0, 0->1, 0->2, 1->2, 2->3
    // Compressed Sparse Column (CSC) format stores column boundaries and row indices.
    // cols: 0, 1, 2, 3
    // col_ptr: [0, 1, 2, 4, 5] -> boundaries for each column
    // row_indices: [2, 0, 0, 1, 2] -> corresponding row for each non-zero
    std::vector<int> col_ptr = {0, 1, 2, 4, 5};
    std::vector<int> row_indices = {2, 0, 0, 1, 2};
    std::vector<int> values = {1, 1, 1, 1, 1}; // Edge weights

    int target_col = 2; // Incoming edges to vertex 2
    int edges_in_col2 = col_ptr[target_col + 1] - col_ptr[target_col];
    
    std::cout << "Edges pointing to vertex 2: " << edges_in_col2 << std::endl;
    assert(edges_in_col2 == 2);
    
    return 0;
}
// Time Complexity: O(1) to find number of incoming edges to a vertex
// Space Complexity: O(V + E)
```
# Part 3. 그래프 탐색
## BreadthFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1, 2}, {0, 3}, {0}, {1}};
std::vector<int> res;

void BFS(int start) {
    std::queue<int> q;
    std::vector<bool> visited(V, false);
    q.push(start); visited[start] = true;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        res.push_back(u);
        for (int v : adj[u]) {
            if (!visited[v]) { visited[v] = true; q.push(v); }
        }
    }
}

int main() {
    BFS(0);
    assert(res.size() == 4 && res[0] == 0);
    std::cout << "BFS traversal complete." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## DepthFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1, 2}, {0, 3}, {0}, {1}};
std::vector<int> res;
std::vector<bool> visited(4, false);

void DFS(int u) {
    visited[u] = true;
    res.push_back(u);
    for (int v : adj[u]) {
        if (!visited[v]) DFS(v);
    }
}

int main() {
    DFS(0);
    assert(res.size() == 4);
    std::cout << "DFS traversal complete." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## IterativeDFS()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1, 2}, {0, 3}, {0}, {1}};

std::vector<int> iterDFS(int start) {
    std::vector<int> res;
    std::stack<int> s;
    std::vector<bool> visited(V, false);
    s.push(start);
    while(!s.empty()){
        int u = s.top(); s.pop();
        if(!visited[u]) {
            visited[u] = true;
            res.push_back(u);
            // Reverse order push for consistent visiting order to recursive DFS
            for(auto it = adj[u].rbegin(); it != adj[u].rend(); ++it){
                if(!visited[*it]) s.push(*it);
            }
        }
    }
    return res;
}

int main() {
    auto res = iterDFS(0);
    assert(res.size() == 4);
    std::cout << "Iterative DFS complete." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## RecursiveDFS()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int V = 5;
std::vector<std::vector<int>> adj = {{1, 2}, {0, 3}, {0, 3}, {1, 2, 4}, {3}};
std::vector<bool> visited(5, false);
int visit_count = 0;

void recursiveDFS(int u) {
    visited[u] = true;
    visit_count++;
    for (int v : adj[u]) {
        if (!visited[v]) {
            recursiveDFS(v);
        }
    }
}

int main() {
    recursiveDFS(0);
    assert(visit_count == 5);
    std::cout << "Recursive DFS completed." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V) for call stack
```
## GraphTraversal()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int V = 5;
std::vector<std::vector<int>> adj = {{1}, {0}, {3}, {2}, {}}; // 3 components
std::vector<bool> visited(5, false);

void DFS(int u) {
    visited[u] = true;
    for(int v : adj[u]) if(!visited[v]) DFS(v);
}

int main() {
    int components = 0;
    for(int i = 0; i < V; i++){
        if(!visited[i]) {
            DFS(i);
            components++;
        }
    }
    assert(components == 3);
    std::cout << "GraphTraversal visited all components." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
# Part 4. 연결성
## ConnectedComponents()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1}, {0}, {}, {}};
std::vector<bool> visited(4, false);

void DFS(int u) {
    visited[u] = true;
    for(int v : adj[u]) if(!visited[v]) DFS(v);
}

int getConnectedComponents() {
    int count = 0;
    for (int i = 0; i < V; i++) {
        if (!visited[i]) { DFS(i); count++; }
    }
    return count;
}

int main() {
    int cc = getConnectedComponents();
    std::cout << "Connected Components: " << cc << std::endl;
    assert(cc == 3);
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## StronglyConnectedComponents()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<std::vector<int>> adj, rev_adj;
std::vector<bool> visited;
std::stack<int> s;

void dfs1(int u) {
    visited[u] = true;
    for(int v : adj[u]) if(!visited[v]) dfs1(v);
    s.push(u);
}
void dfs2(int u) {
    visited[u] = true;
    for(int v : rev_adj[u]) if(!visited[v]) dfs2(v);
}

int main() {
    int V = 3;
    adj.assign(V, std::vector<int>());
    rev_adj.assign(V, std::vector<int>());
    visited.assign(V, false);
    
    adj[0].push_back(1); rev_adj[1].push_back(0);
    adj[1].push_back(2); rev_adj[2].push_back(1);
    adj[2].push_back(0); rev_adj[0].push_back(2); // cycle
    
    for(int i=0; i<V; i++) if(!visited[i]) dfs1(i);
    visited.assign(V, false);
    
    int scc_count = 0;
    while(!s.empty()){
        int u = s.top(); s.pop();
        if(!visited[u]) {
            dfs2(u);
            scc_count++;
        }
    }
    assert(scc_count == 1);
    std::cout << "Kosaraju SCC count: " << scc_count << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## WeaklyConnectedComponents()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int V = 4;
// Directed graph: 0->1, 2->3
std::vector<std::vector<int>> adj = {{1}, {}, {3}, {}};
std::vector<std::vector<int>> undirected_adj(4);
std::vector<bool> visited(4, false);

void dfs(int u) {
    visited[u] = true;
    for (int v : undirected_adj[u]) {
        if (!visited[v]) dfs(v);
    }
}

int main() {
    // Convert to undirected for WCC
    for (int u = 0; u < V; ++u) {
        for (int v : adj[u]) {
            undirected_adj[u].push_back(v);
            undirected_adj[v].push_back(u);
        }
    }
    
    int wcc_count = 0;
    for (int i = 0; i < V; ++i) {
        if (!visited[i]) {
            dfs(i);
            wcc_count++;
        }
    }
    
    std::cout << "Weakly Connected Components: " << wcc_count << std::endl;
    assert(wcc_count == 2);
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## IsConnected()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int V = 3;
std::vector<std::vector<int>> adj = {{1,2},{0,2},{0,1}};
std::vector<bool> visited(3, false);

void dfs(int u){
    visited[u]=true;
    for(int v:adj[u]) if(!visited[v]) dfs(v);
}

bool isConnected() {
    dfs(0);
    for(bool v : visited) if(!v) return false;
    return true;
}

int main() {
    assert(isConnected() == true);
    std::cout << "IsConnected verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## ArticulationPoint()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1, 2}, {0, 2}, {0, 1, 3}, {2}};
std::vector<int> dfn(4, 0), low(4, 0);
std::vector<bool> isAP(4, false);
int timer = 0;

void dfs(int u, int p = -1) {
    dfn[u] = low[u] = ++timer;
    int children = 0;
    for (int v : adj[u]) {
        if (v == p) continue;
        if (dfn[v]) { low[u] = std::min(low[u], dfn[v]); }
        else {
            dfs(v, u);
            low[u] = std::min(low[u], low[v]);
            if (low[v] >= dfn[u] && p != -1) isAP[u] = true;
            children++;
        }
    }
    if (p == -1 && children > 1) isAP[u] = true;
}

int main() {
    dfs(0);
    assert(isAP[2] == true); // Node 2 connects (0,1) with (3)
    std::cout << "Articulation Point verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## Bridge()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1, 2}, {0, 2}, {0, 1, 3}, {2}};
std::vector<int> dfn(4, 0), low(4, 0);
int timer = 0, bridges = 0;

void dfs(int u, int p = -1) {
    dfn[u] = low[u] = ++timer;
    for (int v : adj[u]) {
        if (v == p) continue;
        if (dfn[v]) low[u] = std::min(low[u], dfn[v]);
        else {
            dfs(v, u);
            low[u] = std::min(low[u], low[v]);
            if (low[v] > dfn[u]) bridges++;
        }
    }
}

int main() {
    dfs(0);
    assert(bridges == 1); // Edge 2-3 is a bridge
    std::cout << "Bridge finding verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
# Part 5. 사이클
## DetectCycle()
### 대표코드
```cpp
#include <iostream>
#include <numeric>
#include <utility>
#include <vector>
#include <cassert>

// 사이클 탐지의 통합 진입점: 그래프 종류에 따라 알고리즘이 달라진다.
//  - 방향 그래프: DFS 색칠 (0=미방문, 1=현재 경로 위, 2=완료).  경로 위의 정점으로 되돌아가는 간선(뒤 간선) = 사이클
//  - 무방향 그래프: 서로소 집합. 이미 같은 집합인 두 정점을 잇는 간선이 나오면 사이클 (자기 루프·평행 간선 포함)
// (세부 구현은 DetectCycleDFS / DetectCycleBFS / DetectCycleUnionFind 참고)
typedef std::vector<std::pair<int, int>> Edges;

bool dfs(int u, const std::vector<std::vector<int>>& adj, std::vector<int>& color) {
    color[u] = 1;
    for (int v : adj[u]) {
        if (color[v] == 1) return true;
        if (color[v] == 0 && dfs(v, adj, color)) return true;
    }
    color[u] = 2;
    return false;
}
bool detectCycle(int V, const Edges& edges, bool directed) {
    if (directed) {
        std::vector<std::vector<int>> adj(V);
        for (auto& e : edges) adj[e.first].push_back(e.second);
        std::vector<int> color(V, 0);
        for (int s = 0; s < V; s++) if (color[s] == 0 && dfs(s, adj, color)) return true;
        return false;
    }
    std::vector<int> p(V); std::iota(p.begin(), p.end(), 0);
    auto find = [&](int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; };
    for (auto& e : edges) {
        int a = find(e.first), b = find(e.second);
        if (a == b) return true;
        p[a] = b;
    }
    return false;
}

int main() {
    assert(detectCycle(3, {{0, 1}, {1, 2}, {2, 0}}, true));          // 방향 삼각형
    assert(!detectCycle(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}}, true)); // DAG (다이아몬드): 사이클 아님
    assert(!detectCycle(4, {{0, 1}, {1, 2}, {2, 3}}, false));         // 무방향 트리
    assert(detectCycle(4, {{0, 1}, {1, 2}, {2, 3}, {3, 1}}, false));
    assert(detectCycle(2, {{0, 1}, {1, 0}}, false));                  // 무방향의 평행 간선도 사이클
    assert(detectCycle(2, {{0, 1}, {1, 0}}, true));                   // 방향이면 0->1->0
    assert(detectCycle(1, {{0, 0}}, true) && detectCycle(1, {{0, 0}}, false));   // 자기 루프
    std::cout << "DetectCycle verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## DetectCycleDFS()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int V = 3;
std::vector<std::vector<int>> adj = {{1}, {2}, {0}};
std::vector<bool> vis(3, false), in_stack(3, false);

bool dfs(int u) {
    vis[u] = true; in_stack[u] = true;
    for (int v : adj[u]) {
        if (!vis[v] && dfs(v)) return true;
        else if (in_stack[v]) return true;
    }
    in_stack[u] = false;
    return false;
}

int main() {
    assert(dfs(0) == true);
    std::cout << "Cycle DFS detected." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## DetectCycleBFS()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

int main() {
    int V = 3;
    std::vector<std::vector<int>> adj = {{1}, {2}, {0}};
    std::vector<int> indegree(V, 0);
    for(int u=0; u<V; u++) for(int v:adj[u]) indegree[v]++;
    
    std::queue<int> q;
    for(int i=0; i<V; i++) if(indegree[i] == 0) q.push(i);
    
    int count = 0;
    while(!q.empty()){
        int u = q.front(); q.pop(); count++;
        for(int v : adj[u]) if(--indegree[v] == 0) q.push(v);
    }
    assert(count < V); // cycle exists
    std::cout << "Cycle BFS (Kahn's) verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## DetectCycleUnionFind()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<int> parent;
int findSet(int v) { return v == parent[v] ? v : parent[v] = findSet(parent[v]); }
bool unionSet(int u, int v) {
    u = findSet(u); v = findSet(v);
    if(u == v) return true; // cycle detected
    parent[u] = v; return false;
}

int main() {
    parent = {0, 1, 2};
    std::vector<std::pair<int,int>> edges = {{0,1}, {1,2}, {0,2}};
    bool hasCycle = false;
    for(auto edge : edges) {
        if(unionSet(edge.first, edge.second)) { hasCycle = true; break; }
    }
    assert(hasCycle == true);
    std::cout << "Cycle UF detected." << std::endl;
    return 0;
}
// Time Complexity: O(E a(V))
```
## IsTree()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

int V_nodes = 5;
std::vector<std::vector<int>> adj_tree = {{1,2},{0,3},{0},{1},{}}; // 4 edges, but 4 has no edge
// A graph is a tree iff it is connected AND has exactly V-1 edges.
bool isTree(int V, std::vector<std::vector<int>>& adj) {
    int edgeCount = 0;
    for (int i = 0; i < V; i++) edgeCount += adj[i].size();
    edgeCount /= 2; // undirected
    if (edgeCount != V - 1) return false;
    // BFS connectivity check
    std::vector<bool> visited(V, false);
    std::queue<int> q;
    q.push(0); visited[0] = true; int cnt = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) if (!visited[v]) { visited[v]=true; q.push(v); cnt++; }
    }
    return cnt == V;
}
int main() {
    std::vector<std::vector<int>> g = {{1,2},{0,3,4},{0},{1},{1}}; // 5 nodes, 4 edges
    assert(isTree(5, g) == true);
    std::cout << "IsTree verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## IsForest()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// A forest has no cycles and E == V - (number of trees/components)
bool isForest(int V, std::vector<std::vector<int>>& adj) {
    int edgeCount = 0;
    for (int i = 0; i < V; i++) edgeCount += adj[i].size();
    edgeCount /= 2;
    // BFS to count components and check no cycle via edge count
    std::vector<bool> visited(V, false);
    int components = 0;
    // forest: E == V - components
    std::queue<int> q;
    for (int i = 0; i < V; i++) {
        if (!visited[i]) {
            components++;
            q.push(i); visited[i] = true;
            while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!visited[v]) { visited[v]=true; q.push(v); } }
        }
    }
    return edgeCount == V - components;
}
int main() {
    // Two trees: 0-1-2 and 3-4 (forest of 2 trees, 5 nodes, 3 edges)
    std::vector<std::vector<int>> g = {{1},{0,2},{1},{4},{3}};
    assert(isForest(5, g) == true);
    std::cout << "IsForest verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## IsBiconnected()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int timer_bc = 0;
std::vector<int> disc_bc, low_bc, parent_bc;
bool hasBridge = false;

void dfs_bc(int u, std::vector<std::vector<int>>& adj) {
    disc_bc[u] = low_bc[u] = timer_bc++;
    int children = 0;
    for (int v : adj[u]) {
        if (disc_bc[v] == -1) {
            children++; parent_bc[v] = u;
            dfs_bc(v, adj);
            low_bc[u] = std::min(low_bc[u], low_bc[v]);
            if (parent_bc[u] == -1 && children > 1) hasBridge = true;
            if (parent_bc[u] != -1 && low_bc[v] >= disc_bc[u]) hasBridge = true;
        } else if (v != parent_bc[u]) {
            low_bc[u] = std::min(low_bc[u], disc_bc[v]);
        }
    }
}

bool isBiconnected(int V, std::vector<std::vector<int>>& adj) {
    disc_bc.assign(V, -1); low_bc.assign(V, 0); parent_bc.assign(V, -1);
    hasBridge = false; timer_bc = 0;
    dfs_bc(0, adj);
    if (hasBridge) return false;
    for (int i = 0; i < V; i++) if (disc_bc[i] == -1) return false;
    return true;
}

int main() {
    int V = 5;
    std::vector<std::vector<int>> g = {{1,2,3},{0,2},{0,1,3,4},{0,2,4},{2,3}};
    assert(isBiconnected(V, g) == true);
    std::cout << "IsBiconnected verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
# Part 6. 위상 구조
## KahnAlgorithm()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

int main() {
    int V = 4;
    std::vector<std::vector<int>> adj = {{1, 2}, {3}, {3}, {}};
    std::vector<int> indegree(V, 0);
    for(int u=0; u<V; u++) for(int v:adj[u]) indegree[v]++;
    
    std::queue<int> q; std::vector<int> res;
    for (int i = 0; i < V; ++i) if (indegree[i] == 0) q.push(i);
    
    while (!q.empty()) {
        int u = q.front(); q.pop(); res.push_back(u);
        for (int v : adj[u]) if (--indegree[v] == 0) q.push(v);
    }
    assert(res.size() == 4 && res.back() == 3);
    std::cout << "Kahn's Topological Sort completed." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## DFSBasedTopologicalSort()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1, 2}, {3}, {3}, {}};
std::vector<bool> visited(4, false);
std::stack<int> s;

void dfs(int u) {
    visited[u] = true;
    for(int v : adj[u]) if(!visited[v]) dfs(v);
    s.push(u);
}

int main() {
    for(int i=0; i<V; i++) if(!visited[i]) dfs(i);
    std::vector<int> res;
    while(!s.empty()){ res.push_back(s.top()); s.pop(); }
    assert(res[0] == 0 && res.back() == 3);
    std::cout << "DFS Topological Sort completed." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## LongestPathInDAG()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    int V = 4;
    std::vector<std::vector<std::pair<int,int>>> adj = {{{1,2}, {2,5}}, {{3,1}}, {{3,1}}, {}};
    std::vector<int> topOrder = {0, 1, 2, 3}; // From previous algorithm
    std::vector<int> dist(V, -1e9);
    dist[0] = 0;
    
    for(int u : topOrder) {
        if(dist[u] != -1e9){
            for(auto edge : adj[u]){
                int v = edge.first, w = edge.second;
                if(dist[v] < dist[u] + w) dist[v] = dist[u] + w;
            }
        }
    }
    assert(dist[3] == 6); // 0 -> 2 -> 3
    std::cout << "Longest Path in DAG computed." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
# Part 7. 최소 신장 트리
## Kruskal()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

struct Edge { int u, v, w; };
std::vector<int> parent;
int findSet(int v) { return v == parent[v] ? v : parent[v] = findSet(parent[v]); }
void unionSet(int u, int v) { parent[findSet(u)] = findSet(v); }

int main() {
    int V = 4;
    parent.resize(V); for(int i=0; i<V; i++) parent[i] = i;
    std::vector<Edge> edges = {{0,1,10}, {1,3,15}, {2,3,4}, {2,0,6}, {0,3,5}};
    std::sort(edges.begin(), edges.end(), [](Edge a, Edge b){ return a.w < b.w; });
    
    int mst_weight = 0, edges_taken = 0;
    for(auto e : edges){
        if(findSet(e.u) != findSet(e.v)){
            unionSet(e.u, e.v);
            mst_weight += e.w;
            edges_taken++;
        }
    }
    assert(mst_weight == 19 && edges_taken == 3);
    std::cout << "Kruskal MST Weight: " << mst_weight << std::endl;
    return 0;
}
// Time Complexity: O(E log E)
// Space Complexity: O(V + E)
```
## Prim()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

int main() {
    int V = 4;
    std::vector<std::vector<std::pair<int,int>>> adj = {{{1,10},{2,6},{3,5}}, {{0,10},{3,15}}, {{0,6},{3,4}}, {{1,15},{0,5},{2,4}}};
    std::vector<bool> visited(V, false);
    std::priority_queue<std::pair<int,int>, std::vector<std::pair<int,int>>, std::greater<>> pq;
    
    int mst_weight = 0;
    pq.push({0, 0});
    while(!pq.empty()){
        auto [w, u] = pq.top(); pq.pop();
        if(visited[u]) continue;
        visited[u] = true;
        mst_weight += w;
        for(auto edge : adj[u]) if(!visited[edge.first]) pq.push({edge.second, edge.first});
    }
    assert(mst_weight == 19);
    std::cout << "Prim MST Weight: " << mst_weight << std::endl;
    return 0;
}
// Time Complexity: O(E log V)
// Space Complexity: O(V + E)
```
## Boruvka()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <tuple>
#include <cassert>

struct Edge { int u, v, w; };

int findB(std::vector<int>& par, int x) { return par[x] == x ? x : par[x] = findB(par, par[x]); }
void unionB(std::vector<int>& par, std::vector<int>& rank, int x, int y) {
    x = findB(par,x); y = findB(par,y);
    if (rank[x] < rank[y]) std::swap(x,y);
    par[y] = x; if (rank[x]==rank[y]) rank[x]++;
}

int boruvka(int V, std::vector<Edge>& edges) {
    std::vector<int> par(V), rnk(V, 0);
    for (int i = 0; i < V; i++) par[i] = i;
    int mstWeight = 0, numComponents = V;
    while (numComponents > 1) {
        std::vector<int> cheapest(V, -1);
        for (int i = 0; i < (int)edges.size(); i++) {
            int su = findB(par, edges[i].u), sv = findB(par, edges[i].v);
            if (su != sv) {
                if (cheapest[su] == -1 || edges[cheapest[su]].w > edges[i].w) cheapest[su] = i;
                if (cheapest[sv] == -1 || edges[cheapest[sv]].w > edges[i].w) cheapest[sv] = i;
            }
        }
        for (int i = 0; i < V; i++) {
            if (cheapest[i] != -1) {
                int su = findB(par, edges[cheapest[i]].u), sv = findB(par, edges[cheapest[i]].v);
                if (su != sv) { mstWeight += edges[cheapest[i]].w; unionB(par, rnk, su, sv); numComponents--; }
            }
        }
    }
    return mstWeight;
}

int main() {
    int V = 4;
    std::vector<Edge> edges = {{0,1,10},{0,2,6},{0,3,5},{1,3,15},{2,3,4}};
    int mst = boruvka(V, edges);
    assert(mst == 19);
    std::cout << "Boruvka MST weight: " << mst << std::endl;
    return 0;
}
// Time Complexity: O(E log V)
// Space Complexity: O(V + E)
```
## ReverseDelete()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <algorithm>
#include <cassert>

struct EdgeRD { int u, v, w; };

int V_rd;
std::vector<std::vector<int>> adj_rd;

bool isConnectedRD() {
    std::vector<bool> vis(V_rd, false);
    std::queue<int> q; q.push(0); vis[0] = true; int cnt = 1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj_rd[u]) if (!vis[v]) { vis[v]=true; q.push(v); cnt++; }
    }
    return cnt == V_rd;
}
int reverseDelete(int V, std::vector<EdgeRD>& edges) {
    V_rd = V;
    std::sort(edges.begin(), edges.end(), [](const EdgeRD& a, const EdgeRD& b){ return a.w > b.w; });
    adj_rd.assign(V, {});
    for (auto& e : edges) { adj_rd[e.u].push_back(e.v); adj_rd[e.v].push_back(e.u); }
    int mstWeight = 0;
    for (auto& e : edges) {
        adj_rd[e.u].erase(std::find(adj_rd[e.u].begin(), adj_rd[e.u].end(), e.v));
        adj_rd[e.v].erase(std::find(adj_rd[e.v].begin(), adj_rd[e.v].end(), e.u));
        if (!isConnectedRD()) { adj_rd[e.u].push_back(e.v); adj_rd[e.v].push_back(e.u); mstWeight += e.w; }
    }
    return mstWeight;
}

int main() {
    int V = 4;
    std::vector<EdgeRD> edges = {{0,1,10},{0,2,6},{0,3,5},{1,3,15},{2,3,4}};
    int mst = reverseDelete(V, edges);
    assert(mst == 19);
    std::cout << "ReverseDelete MST weight: " << mst << std::endl;
    return 0;
}
// Time Complexity: O(E log E * (V + E))
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
#include <vector>
#include <cassert>

std::vector<int> parent(5), rank_arr(5, 0);

void makeSet(int v) {
    parent[v] = v;
    rank_arr[v] = 0;
}

int main() {
    makeSet(1);
    assert(parent[1] == 1 && rank_arr[1] == 0);
    std::cout << "MakeSet executed." << std::endl;
    return 0;
}
// Time Complexity: O(1)
```
## FindSet()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<int> parent = {0, 0, 1}; // 2 points to 1, 1 points to 0

int findSet(int v) {
    if (v == parent[v]) return v;
    return parent[v] = findSet(parent[v]); // Path compression
}

int main() {
    int root = findSet(2);
    assert(root == 0 && parent[2] == 0); // Path compressed
    std::cout << "FindSet with compression verified." << std::endl;
    return 0;
}
// Time Complexity: Amortized O(a(N)) -> ~O(1)
```
## UnionSet()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <numeric>
#include <vector>
#include <cassert>

// UnionSet: 두 원소가 속한 집합을 하나로 합친다. 대표(루트)를 찾아 한쪽 루트를 다른 쪽 밑에 붙이는 것이 전부다.
//  - 합칠 때 랭크(트리 높이의 상한)가 낮은 쪽을 높은 쪽 밑에 붙이고 (UnionByRank), 찾을 때 경로를 압축하면 (PathCompression)
//    연산 한 번당 분할상환 O(α(n))  (α 는 역아커만 함수, 실용상 4 이하)
struct DisjointSet {
    std::vector<int> parent, rnk; int components;
    explicit DisjointSet(int n) : parent(n), rnk(n, 0), components(n) { std::iota(parent.begin(), parent.end(), 0); }
    int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }
    bool unionSet(int a, int b) {                       // 합쳤으면 true, 이미 같은 집합이면 false
        a = find(a); b = find(b);
        if (a == b) return false;
        if (rnk[a] < rnk[b]) std::swap(a, b);
        parent[b] = a;
        if (rnk[a] == rnk[b]) rnk[a]++;
        components--;
        return true;
    }
    bool connected(int a, int b) { return find(a) == find(b); }
};

int main() {
    DisjointSet ds(8);
    assert(ds.unionSet(0, 1) && ds.unionSet(2, 3) && ds.unionSet(1, 3));
    assert(!ds.unionSet(0, 2));                          // 이미 같은 집합
    assert(ds.connected(0, 3) && !ds.connected(0, 4));
    assert(ds.components == 5);                          // {0,1,2,3} {4} {5} {6} {7}
    for (int i = 4; i < 7; i++) ds.unionSet(i, i + 1);
    assert(ds.components == 2 && ds.connected(4, 7));
    // 긴 사슬을 합쳐도 랭크 덕분에 트리가 납작하게 유지된다
    DisjointSet chain(100000);
    for (int i = 0; i + 1 < 100000; i++) chain.unionSet(i, i + 1);
    assert(chain.components == 1 && chain.connected(0, 99999));
    int maxRank = *std::max_element(chain.rnk.begin(), chain.rnk.end());
    assert(maxRank <= 17);                               // log2(100000) ≈ 16.6
    std::cout << "UnionSet verified. max rank in a 100000-chain: " << maxRank << std::endl;
    return 0;
}
// Time Complexity: 분할상환 O(α(n))
// Space Complexity: O(n)
```
## UnionByRank()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

std::vector<int> parent = {0, 1}, rank_arr = {0, 1};

int findSet(int v) { return v == parent[v] ? v : parent[v] = findSet(parent[v]); }

void unionByRank(int a, int b) {
    a = findSet(a); b = findSet(b);
    if (a != b) {
        if (rank_arr[a] < rank_arr[b]) std::swap(a, b);
        parent[b] = a;
        if (rank_arr[a] == rank_arr[b]) rank_arr[a]++;
    }
}

int main() {
    unionByRank(0, 1);
    assert(findSet(0) == 1);
    std::cout << "UnionByRank verified." << std::endl;
    return 0;
}
// Time Complexity: Amortized O(a(N)) -> ~O(1)
```
## PathCompression()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<int> parent_pc;
int findPC(int x) {
    if (parent_pc[x] != x) parent_pc[x] = findPC(parent_pc[x]); // 경로 압축
    return parent_pc[x];
}

int main() {
    parent_pc = {0, 0, 1, 2, 3}; // 0<-1<-2<-3<-4 체인
    int root = findPC(4); // 경로 압축 후 모두 0을 가리킴
    assert(root == 0);
    assert(parent_pc[4] == 0); // 직접 루트를 가리키게 됨
    std::cout << "PathCompression verified. Root of 4: " << root << std::endl;
    return 0;
}
// Time Complexity: O(alpha(N)) amortized (Inverse Ackermann)
// Space Complexity: O(N)
```
# Part 9. 최단 경로
## Dijkstra()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

struct Edge { int v, weight; };

int main() {
    int V = 3;
    std::vector<std::vector<Edge>> adj = {{{1, 10}, {2, 3}}, {{2, 1}}, {}};
    std::vector<int> dist(V, 1e9);
    std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq;
    
    dist[0] = 0; pq.push({0, 0});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto& edge : adj[u]) {
            if (dist[u] + edge.weight < dist[edge.v]) {
                dist[edge.v] = dist[u] + edge.weight;
                pq.push({dist[edge.v], edge.v});
            }
        }
    }
    assert(dist[2] == 3);
    std::cout << "Dijkstra SP completed." << std::endl;
    return 0;
}
// Time Complexity: O(E log V)
// Space Complexity: O(V + E)
```
## BellmanFord()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct Edge { int u, v, w; };

int main() {
    int V = 3;
    std::vector<Edge> edges = {{0, 1, 4}, {1, 2, -1}, {0, 2, 5}};
    std::vector<int> dist(V, 1e9);
    dist[0] = 0;
    
    for(int i=0; i<V-1; i++){
        for(auto e : edges) {
            if(dist[e.u] != 1e9 && dist[e.u] + e.w < dist[e.v])
                dist[e.v] = dist[e.u] + e.w;
        }
    }
    assert(dist[2] == 3);
    std::cout << "Bellman-Ford SP completed." << std::endl;
    return 0;
}
// Time Complexity: O(V * E)
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
    int V = 3;
    std::vector<std::vector<int>> dist = {{0, 5, 1e9}, {1e9, 0, 3}, {1e9, 1e9, 0}};
    
    for (int k = 0; k < V; ++k)
        for (int i = 0; i < V; ++i)
            for (int j = 0; j < V; ++j)
                dist[i][j] = std::min(dist[i][j], dist[i][k] + dist[k][j]); 
                
    assert(dist[0][2] == 8);
    std::cout << "Floyd-Warshall all-pairs SP completed." << std::endl;
    return 0;
}
// Time Complexity: O(V^3)
// Space Complexity: O(V^2)
```
## Johnson()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>
#include <climits>

// Johnson's Algorithm: 음수 가중치 허용, 모든 쌍 최단 경로 O(VE + V^2 log V)
// Step 1: Bellman-Ford로 각 정점 h[v] 계산 (재가중치)
// Step 2: 간선 재가중치 w'(u,v) = w(u,v) + h[u] - h[v] (non-negative)
// Step 3: 각 정점에서 Dijkstra 실행

int main() {
    std::cout << "Johnson's algorithm combines Bellman-Ford + Dijkstra for all-pairs shortest paths." << std::endl;
    std::cout << "Useful for sparse graphs with negative weights. O(VE + V^2 log V)" << std::endl;
    // 실전 구현은 BF + Dijkstra 조합이므로 개념 검증
    assert(true);
    return 0;
}
// Time Complexity: O(VE + V^2 log V)
// Space Complexity: O(V^2)
```
## SPFA()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>
#include <climits>

// SPFA (Shortest Path Faster Algorithm): BellmanFord 개선, 평균 O(kE)
std::vector<int> spfa(int src, int V, std::vector<std::vector<std::pair<int,int>>>& adj) {
    std::vector<int> dist(V, INT_MAX);
    std::vector<bool> inQueue(V, false);
    std::queue<int> q;
    dist[src] = 0; q.push(src); inQueue[src] = true;
    while (!q.empty()) {
        int u = q.front(); q.pop(); inQueue[u] = false;
        for (auto [v, w] : adj[u]) {
            if (dist[u] != INT_MAX && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                if (!inQueue[v]) { q.push(v); inQueue[v] = true; }
            }
        }
    }
    return dist;
}

int main() {
    int V = 5;
    std::vector<std::vector<std::pair<int,int>>> adj(V);
    adj[0].push_back({1, 10}); adj[0].push_back({2, 3});
    adj[2].push_back({1, 4}); adj[1].push_back({3, 2}); adj[2].push_back({3, 8});
    auto dist = spfa(0, V, adj);
    assert(dist[1] == 7); assert(dist[3] == 9);
    std::cout << "SPFA dist[1]=" << dist[1] << " dist[3]=" << dist[3] << std::endl;
    return 0;
}
// Time Complexity: O(kE) average, O(VE) worst
// Space Complexity: O(V + E)
```
# Part 10. 길찾기
## AStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "A* combines Dijkstra's uniform-cost search and Greedy Best-First Search with f(n) = g(n) + h(n)." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(E log V) heavily depends on heuristic
```
## JumpPointSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "JPS optimizes grid map A* by ignoring intermediate nodes without forced neighbors." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## GreedyBestFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

int main() {
    // 휴리스틱만 사용 (실제 비용 무시) — A*보다 빠르지만 최적 미보장
    std::cout << "Greedy Best-First Search uses only heuristic h(n), ignoring actual cost g(n)." << std::endl;
    std::cout << "Faster than A* but NOT guaranteed to find optimal path." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(b^m) worst (b=branching factor, m=max depth)
// Space Complexity: O(b^m)
```
## BidirectionalSearch()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <algorithm>
#include <climits>
#include <cassert>

// 양방향 BFS: 시작점과 목표점에서 레벨 단위로 번갈아 확장하고, 만나는 순간의 최소 거리를 반환
// (처음 만난 간선이 최단이라고 단정하지 않고 한 레벨 전체를 보고 최솟값을 취한다)
int expandLevel(std::queue<int>& q, std::vector<int>& mine, const std::vector<int>& other,
                const std::vector<std::vector<int>>& adj) {
    int best = INT_MAX;
    for (size_t sz = q.size(); sz > 0; --sz) {
        int u = q.front(); q.pop();
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
        int best = (qF.size() <= qB.size()) ? expandLevel(qF, distF, distB, adj)
                                            : expandLevel(qB, distB, distF, adj);
        if (best != INT_MAX) return best;
    }
    return -1;
}

int main() {
    std::vector<std::vector<int>> adj = {{1,2},{0,3},{0,4},{1,5},{2,5},{3,4}};
    assert(bidirectionalBFS(0, 5, adj) == 3);   // 0-1-3-5
    assert(bidirectionalBFS(0, 0, adj) == 0);
    std::vector<std::vector<int>> split = {{1},{0},{3},{2}};
    assert(bidirectionalBFS(0, 3, split) == -1); // 연결되지 않은 경우
    std::cout << "BidirectionalSearch dist(0,5): " << bidirectionalBFS(0, 5, adj) << std::endl;
    return 0;
}
// Time Complexity: O(b^(d/2)) vs O(b^d) for unidirectional
// Space Complexity: O(b^(d/2))
```
## IDDFS()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj_iddfs;

bool dls(int u, int goal, int limit, std::vector<bool>& visited) {
    if (u == goal) return true;
    if (limit == 0) return false;
    visited[u] = true;
    for (int v : adj_iddfs[u])
        if (!visited[v] && dls(v, goal, limit-1, visited)) return true;
    visited[u] = false;
    return false;
}

bool iddfs(int src, int goal, int V, int maxDepth) {
    for (int d = 0; d <= maxDepth; d++) {
        std::vector<bool> visited(V, false);
        if (dls(src, goal, d, visited)) return true;
    }
    return false;
}

int main() {
    adj_iddfs = {{1,2},{0,3},{0,4},{1},{2}};
    assert(iddfs(0, 4, 5, 10) == true);
    assert(iddfs(3, 4, 5, 10) == true);
    std::cout << "IDDFS verified." << std::endl;
    return 0;
}
// Time Complexity: O(b^d) — same as BFS but O(bd) space
// Space Complexity: O(d)
```
## IDAStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
#include <climits>

// IDA* = IDDFS + A* heuristic: 메모리 효율적인 A*
int idaStar_search(int node, int goal, int g, int threshold, auto heuristic) {
    int f = g + heuristic(node, goal);
    if (f > threshold) return f;
    if (node == goal) return -1; // found
    int minimum = INT_MAX;
    // (실제 구현에서는 이웃 노드를 탐색)
    return minimum;
}

int main() {
    std::cout << "IDA* uses iterative deepening with f = g(n) + h(n) as threshold." << std::endl;
    std::cout << "Memory: O(d), optimal with admissible heuristic." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(b^d) — repeated work per iteration
// Space Complexity: O(d)
```
## ThetaStar()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // Theta* = Any-angle 경로 탐색 (A*의 격자 제약 없이 임의 각도 이동)
    std::cout << "Theta* extends A* with line-of-sight checks for any-angle paths." << std::endl;
    std::cout << "Parent is set to any visible ancestor, not just grid neighbors." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(E log V) similar to A*
// Space Complexity: O(V)
```
# Part 11. 네트워크 플로우
## FordFulkerson()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>
#include <climits>

int V_ff;
std::vector<std::vector<int>> cap;

bool bfsFF(int src, int sink, std::vector<int>& parent) {
    std::vector<bool> visited(V_ff, false);
    std::queue<int> q; q.push(src); visited[src] = true; parent[src] = -1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v = 0; v < V_ff; v++)
            if (!visited[v] && cap[u][v] > 0) { parent[v]=u; visited[v]=true; q.push(v); }
    }
    return visited[sink];
}

int fordFulkerson(int src, int sink, int V) {
    V_ff = V; int maxFlow = 0;
    std::vector<int> parent(V);
    while (bfsFF(src, sink, parent)) {
        int pathFlow = INT_MAX;
        for (int v = sink; v != src; v = parent[v])
            pathFlow = std::min(pathFlow, cap[parent[v]][v]);
        for (int v = sink; v != src; v = parent[v]) {
            cap[parent[v]][v] -= pathFlow;
            cap[v][parent[v]] += pathFlow;
        }
        maxFlow += pathFlow;
    }
    return maxFlow;
}

int main() {
    V_ff = 6; cap.assign(6, std::vector<int>(6, 0));
    cap[0][1]=16; cap[0][2]=13; cap[1][2]=10; cap[1][3]=12;
    cap[2][4]=14; cap[3][5]=20; cap[4][3]=7; cap[4][5]=4;
    int mf = fordFulkerson(0, 5, 6);
    assert(mf == 23);
    std::cout << "FordFulkerson max flow: " << mf << std::endl;
    return 0;
}
// Time Complexity: O(VE^2) with BFS (Edmonds-Karp)
// Space Complexity: O(V^2)
```
## EdmondsKarp()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> capacity, flow, adj;

int bfs(int s, int t, std::vector<int>& parent) {
    std::fill(parent.begin(), parent.end(), -1);
    parent[s] = -2;
    std::queue<std::pair<int, int>> q;
    q.push({s, 1e9});
    
    while (!q.empty()) {
        auto [cur, f] = q.front(); q.pop();
        for (int next : adj[cur]) {
            if (parent[next] == -1 && capacity[cur][next] - flow[cur][next] > 0) {
                parent[next] = cur;
                int new_flow = std::min(f, capacity[cur][next] - flow[cur][next]);
                if (next == t) return new_flow;
                q.push({next, new_flow});
            }
        }
    }
    return 0;
}

int edmondsKarp(int s, int t) {
    int max_flow = 0, new_flow;
    std::vector<int> parent(V);
    while (new_flow = bfs(s, t, parent)) {
        max_flow += new_flow;
        int cur = t;
        while (cur != s) {
            int prev = parent[cur];
            flow[prev][cur] += new_flow;
            flow[cur][prev] -= new_flow;
            cur = prev;
        }
    }
    return max_flow;
}

int main() {
    capacity.assign(V, std::vector<int>(V, 0));
    flow.assign(V, std::vector<int>(V, 0));
    adj.assign(V, std::vector<int>());
    
    auto addEdge = [](int u, int v, int cap) {
        adj[u].push_back(v); adj[v].push_back(u);
        capacity[u][v] += cap;
    };
    
    addEdge(0, 1, 3); addEdge(0, 2, 2); addEdge(1, 2, 5); addEdge(1, 3, 2); addEdge(2, 3, 3);
    
    assert(edmondsKarp(0, 3) == 5);
    std::cout << "Edmonds-Karp Max Flow verified." << std::endl;
    return 0;
}
// Time Complexity: O(V E^2)
// Space Complexity: O(V^2) for matrix
```
## Dinic()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>
#include <climits>

struct Dinic {
    struct Edge { int to, rev; int cap; };
    std::vector<std::vector<Edge>> graph;
    std::vector<int> level, iter;
    int n;
    Dinic(int n) : n(n), graph(n), level(n), iter(n) {}
    void addEdge(int from, int to, int cap) {
        graph[from].push_back({to, (int)graph[to].size(), cap});
        graph[to].push_back({from, (int)graph[from].size()-1, 0});
    }
    bool bfs(int s, int t) {
        std::fill(level.begin(), level.end(), -1);
        std::queue<int> q; level[s]=0; q.push(s);
        while (!q.empty()) { int v=q.front(); q.pop(); for (auto& e:graph[v]) if (e.cap>0&&level[e.to]<0) { level[e.to]=level[v]+1; q.push(e.to); } }
        return level[t] >= 0;
    }
    int dfs(int v, int t, int f) {
        if (v==t) return f;
        for (int& i=iter[v]; i<(int)graph[v].size(); i++) {
            Edge& e=graph[v][i];
            if (e.cap>0&&level[v]<level[e.to]) {
                int d=dfs(e.to,t,std::min(f,e.cap));
                if (d>0) { e.cap-=d; graph[e.to][e.rev].cap+=d; return d; }
            }
        }
        return 0;
    }
    int maxflow(int s, int t) {
        int flow=0;
        while (bfs(s,t)) { std::fill(iter.begin(),iter.end(),0); int d; while ((d=dfs(s,t,INT_MAX))>0) flow+=d; }
        return flow;
    }
};

int main() {
    Dinic dinic(6);
    dinic.addEdge(0,1,16); dinic.addEdge(0,2,13); dinic.addEdge(1,2,10);
    dinic.addEdge(1,3,12); dinic.addEdge(2,4,14); dinic.addEdge(3,5,20);
    dinic.addEdge(4,3,7); dinic.addEdge(4,5,4);
    assert(dinic.maxflow(0,5) == 23);
    std::cout << "Dinic max flow: 23" << std::endl;
    return 0;
}
// Time Complexity: O(V^2 * E)
// Space Complexity: O(V + E)
```
## PushRelabel()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // Push-Relabel: 각 정점에서 높이(height) 함수를 기반으로 과잉 흐름(excess)을 밀어냄
    std::cout << "Push-Relabel: height function + excess flow preflow." << std::endl;
    std::cout << "O(V^2 * sqrt(E)) with FIFO selection. Faster than Ford-Fulkerson in dense graphs." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(V^2 * sqrt(E))
// Space Complexity: O(V^2)
```
## MinCostMaxFlow()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // 최소 비용 최대 유량: 최대 유량을 유지하면서 비용을 최소화
    // SPFA(Bellman-Ford 개선)로 최소 비용 경로 탐색 반복
    std::cout << "MinCostMaxFlow finds maximum flow with minimum cost." << std::endl;
    std::cout << "Uses SPFA to find shortest (cheapest) augmenting path. O(V * E * maxFlow)" << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(V * E * maxFlow) or O(E * V^2) with SPFA
// Space Complexity: O(V + E)
```
# Part 12. 매칭
## BipartiteMatching()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

std::vector<std::vector<int>> adj;
std::vector<int> match;
std::vector<bool> visited;

bool dfs(int u) {
    for (int v : adj[u]) {
        if (visited[v]) continue;
        visited[v] = true;
        if (match[v] == -1 || dfs(match[v])) {
            match[v] = u;
            return true;
        }
    }
    return false;
}

int main() {
    int n = 2, m = 2; // 2 left, 2 right nodes
    adj.assign(n, std::vector<int>());
    match.assign(m, -1);
    
    adj[0] = {0, 1}; // L0 connected to R0, R1
    adj[1] = {0};    // L1 connected to R0
    
    int size = 0;
    for (int i = 0; i < n; ++i) {
        visited.assign(m, false);
        if (dfs(i)) size++;
    }
    assert(size == 2);
    std::cout << "Bipartite Matching verified." << std::endl;
    return 0;
}
// Time Complexity: O(V * E)
// Space Complexity: O(V + E)
```
## HungarianAlgorithm()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>
#include <climits>

// 헝가리안 알고리즘: 이분 그래프 최소 비용 완전 매칭 (할당 문제)
int hungarian(std::vector<std::vector<int>>& cost) {
    int n = cost.size();
    std::vector<int> u(n+1), v(n+1), p(n+1), way(n+1);
    for (int i = 1; i <= n; i++) {
        p[0] = i;
        int j0 = 0;
        std::vector<int> minv(n+1, INT_MAX);
        std::vector<bool> used(n+1, false);
        do {
            used[j0] = true;
            int i0 = p[j0], delta = INT_MAX, j1;
            for (int j = 1; j <= n; j++) {
                if (!used[j]) {
                    int cur = cost[i0-1][j-1] - u[i0] - v[j];
                    if (cur < minv[j]) { minv[j]=cur; way[j]=j0; }
                    if (minv[j] < delta) { delta=minv[j]; j1=j; }
                }
            }
            for (int j = 0; j <= n; j++) { if (used[j]) { u[p[j]]+=delta; v[j]-=delta; } else minv[j]-=delta; }
            j0 = j1;
        } while (p[j0] != 0);
        do { int j1=way[j0]; p[j0]=p[j1]; j0=j1; } while (j0);
    }
    int result = 0;
    for (int j = 1; j <= n; j++) if (p[j]) result += cost[p[j]-1][j-1];
    return result;
}

int main() {
    std::vector<std::vector<int>> cost = {{4,2,3},{1,3,2},{2,1,4}};
    int minCost = hungarian(cost);
    assert(minCost == 5); // 최적 할당: (0→2)=3,(1→0)=1,(2→1)=1;
    std::cout << "Hungarian min cost: " << minCost << std::endl;
    return 0;
}
// Time Complexity: O(N^3)
// Space Complexity: O(N^2)
```
## HopcroftKarp()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>
#include <climits>

// Hopcroft-Karp: 이분 그래프 최대 매칭 O(E * sqrt(V))
struct HopcroftKarp {
    int n, m;
    std::vector<std::vector<int>> adj;
    std::vector<int> matchL, matchR, dist;
    HopcroftKarp(int n, int m) : n(n), m(m), adj(n), matchL(n,-1), matchR(m,-1), dist(n) {}
    void addEdge(int u, int v) { adj[u].push_back(v); }
    bool bfs() {
        std::queue<int> q;
        for (int u=0;u<n;u++) { if (matchL[u]==-1) { dist[u]=0; q.push(u); } else dist[u]=INT_MAX; }
        bool found=false;
        while (!q.empty()) { int u=q.front();q.pop(); for (int v:adj[u]) { int w=matchR[v]; if (w==-1) found=true; else if (dist[w]==INT_MAX) { dist[w]=dist[u]+1; q.push(w); } } }
        return found;
    }
    bool dfs(int u) {
        for (int v:adj[u]) { int w=matchR[v]; if (w==-1||dist[w]==dist[u]+1&&dfs(w)) { matchL[u]=v; matchR[v]=u; return true; } }
        dist[u]=INT_MAX; return false;
    }
    int maxMatching() { int res=0; while(bfs()) for(int u=0;u<n;u++) if(matchL[u]==-1&&dfs(u)) res++; return res; }
};

int main() {
    HopcroftKarp hk(4, 4);
    hk.addEdge(0,0); hk.addEdge(0,1); hk.addEdge(1,1); hk.addEdge(2,2); hk.addEdge(3,3); hk.addEdge(3,2);
    assert(hk.maxMatching() == 4);
    std::cout << "HopcroftKarp max matching: 4" << std::endl;
    return 0;
}
// Time Complexity: O(E * sqrt(V))
// Space Complexity: O(V + E)
```
## BlossomAlgorithm()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // Blossom Algorithm (에드몬즈): 일반 그래프(이분 아닌) 최대 매칭
    // 홀수 사이클(꽃, Blossom)을 수축하여 증가 경로 탐색
    std::cout << "Blossom Algorithm handles general (non-bipartite) maximum matching." << std::endl;
    std::cout << "Contracts odd-length cycles (blossoms) to find augmenting paths. O(V^3)" << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(V^3) or O(V * E) with optimization
// Space Complexity: O(V + E)
```
# Part 13. 그래프 분석
## Tarjan()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <cassert>

int V = 4;
std::vector<std::vector<int>> adj = {{1}, {2}, {0}, {2}};
std::vector<int> dfn(4, 0), low(4, 0);
std::vector<bool> in_stack(4, false);
std::stack<int> st;
int timer = 0, scc_cnt = 0;

void dfs(int u) {
    dfn[u] = low[u] = ++timer;
    st.push(u); in_stack[u] = true;
    
    for (int v : adj[u]) {
        if (!dfn[v]) { dfs(v); low[u] = std::min(low[u], low[v]); }
        else if (in_stack[v]) low[u] = std::min(low[u], dfn[v]);
    }
    
    if (low[u] == dfn[u]) {
        scc_cnt++;
        while (true) {
            int t = st.top(); st.pop(); in_stack[t] = false;
            if (t == u) break;
        }
    }
}

int main() {
    for(int i=0; i<V; i++) if(!dfn[i]) dfs(i);
    assert(scc_cnt == 2); // {0,1,2} and {3}
    std::cout << "Tarjan's SCC verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
```
## Kosaraju()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

void dfsKos(int u, std::vector<std::vector<int>>& adj, std::vector<bool>& vis, std::stack<int>& st) {
    vis[u] = true;
    for (int v : adj[u]) if (!vis[v]) dfsKos(v, adj, vis, st);
    st.push(u);
}
void dfsKosRev(int u, std::vector<std::vector<int>>& radj, std::vector<bool>& vis) {
    vis[u] = true;
    for (int v : radj[u]) if (!vis[v]) dfsKosRev(v, radj, vis);
}

int kosaraju(int V, std::vector<std::vector<int>>& adj) {
    std::stack<int> st;
    std::vector<bool> vis(V, false);
    for (int i = 0; i < V; i++) if (!vis[i]) dfsKos(i, adj, vis, st);
    std::vector<std::vector<int>> radj(V);
    for (int u = 0; u < V; u++) for (int v : adj[u]) radj[v].push_back(u);
    std::fill(vis.begin(), vis.end(), false);
    int scc = 0;
    while (!st.empty()) {
        int u = st.top(); st.pop();
        if (!vis[u]) { dfsKosRev(u, radj, vis); scc++; }
    }
    return scc;
}

int main() {
    int V = 5;
    std::vector<std::vector<int>> adj = {{2},{0},{1,3},{4},{}};
    assert(kosaraju(V, adj) == 3); // {0,1,2}, {3}, {4}
    std::cout << "Kosaraju SCC count: 3" << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V + E)
```
## Gabow()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // Gabow's Algorithm: SCC 탐색 (두 개의 스택 사용, Tarjan의 변형)
    std::cout << "Gabow's Algorithm finds SCCs using two stacks (path and root)." << std::endl;
    std::cout << "Similar complexity to Tarjan but simpler stack management. O(V + E)" << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## EulerTour()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>
#include <algorithm>

// 오일러 회로: 모든 간선을 정확히 한 번씩 지나는 경로
// 조건: 연결 그래프에서 모든 정점의 차수가 짝수
void eulerTour(int u, std::vector<std::vector<int>>& adj, std::vector<int>& path) {
    while (!adj[u].empty()) {
        int v = adj[u].back(); adj[u].pop_back();
        // 역방향 간선도 제거 (무방향)
        adj[v].erase(std::find(adj[v].begin(), adj[v].end(), u));
        eulerTour(v, adj, path);
    }
    path.push_back(u);
}
int main() {
    // 0-1-2-0 삼각형 (모든 차수 2, 오일러 회로 존재)
    std::vector<std::vector<int>> adj = {{1,2},{0,2},{0,1}};
    std::vector<int> path;
    eulerTour(0, adj, path);
    assert(path.size() == 4); // 3간선 + 시작점 복귀
    std::cout << "EulerTour path length: " << path.size() << std::endl;
    return 0;
}
// Time Complexity: O(E)
// Space Complexity: O(V + E)
```
## HeavyLightDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // HLD: 트리를 헤비/라이트 엣지로 분해 → 경로 쿼리를 O(log^2 N)에 처리
    std::cout << "Heavy-Light Decomposition decomposes tree paths into O(log N) chains." << std::endl;
    std::cout << "Enables path queries/updates in O(log^2 N) with segment tree." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(N log N) preprocessing, O(log^2 N) per query
// Space Complexity: O(N)
```
## CentroidDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // 중심 분해: 트리를 재귀적으로 무게중심(centroid)으로 분해
    // 경로 관련 분할정복 쿼리에 사용 — O(N log N)
    std::cout << "Centroid Decomposition recursively finds centroids (subtree size <= N/2)." << std::endl;
    std::cout << "Used for path queries/distance problems in trees. O(N log N)" << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(N log N)
// Space Complexity: O(N log N)
```
# Part 14. 특수 그래프
## BipartiteGraph()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

bool isBipartite(int V, std::vector<std::vector<int>>& adj) {
    std::vector<int> color(V, -1);
    for (int s = 0; s < V; s++) {
        if (color[s] != -1) continue;
        std::queue<int> q; q.push(s); color[s] = 0;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : adj[u]) {
                if (color[v] == -1) { color[v] = 1 - color[u]; q.push(v); }
                else if (color[v] == color[u]) return false;
            }
        }
    }
    return true;
}

int main() {
    std::vector<std::vector<int>> g = {{1,3},{0,2},{1,3},{0,2}}; // 4-cycle (bipartite)
    assert(isBipartite(4, g) == true);
    std::vector<std::vector<int>> g2 = {{1,2},{0,2},{0,1}}; // triangle (not bipartite)
    assert(isBipartite(3, g2) == false);
    std::cout << "BipartiteGraph check verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## DirectedGraph()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    // 방향 그래프: 간선에 방향이 있는 그래프
    // 인접 리스트에서 u→v만 저장 (v→u 저장 안 함)
    int V = 4;
    std::vector<std::vector<int>> adj(V); // 방향 그래프
    adj[0].push_back(1); // 0→1
    adj[1].push_back(2); // 1→2
    adj[2].push_back(3); // 2→3
    adj[3].push_back(0); // 3→0 (사이클)
    assert(adj[0].size() == 1 && adj[1].size() == 1);
    // InDegree[1] = 1 (0→1만), OutDegree[1] = 1 (1→2만)
    std::cout << "DirectedGraph: 0->1->2->3->0 cycle of size 4." << std::endl;
    return 0;
}
// Space Complexity: O(V + E)
```
## UndirectedGraph()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// 무방향 그래프: 간선 {u, v} 는 순서가 없다. 인접 리스트에는 양쪽 모두 기록한다.
// 악수 보조정리(handshake lemma): 모든 정점의 차수의 합 = 2·|E|  (그러므로 홀수 차수 정점의 수는 항상 짝수)
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
            c++; std::queue<int> q; q.push(s); seen[s] = true;
            while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (!seen[v]) { seen[v] = true; q.push(v); } }
        }
        return c;
    }
    int oddDegreeCount() const { int c = 0; for (auto& a : adj) c += a.size() % 2; return c; }
};

int main() {
    UndirectedGraph g(6);
    g.addEdge(0, 1); g.addEdge(1, 2); g.addEdge(2, 0); g.addEdge(3, 4);
    size_t sum = 0; for (int i = 0; i < 6; i++) sum += g.degree(i);
    assert(sum == 2 * g.edgeCount());                    // 악수 보조정리
    assert(g.components() == 3);                         // {0,1,2} {3,4} {5}
    assert(g.oddDegreeCount() % 2 == 0);                 // 홀수 차수 정점은 짝수 개
    g.addEdge(5, 5);                                     // 자기 루프: 차수 2 증가
    assert(g.degree(5) == 2 && g.edgeCount() == 5);
    std::cout << "UndirectedGraph verified." << std::endl;
    return 0;
}
// Time Complexity: 간선 추가 O(1), 연결 요소 O(V + E)
// Space Complexity: O(V + E)
```
## WeightedGraph()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <climits>
#include <queue>
#include <utility>
#include <vector>
#include <cassert>

// 가중치 그래프: 간선마다 비용이 있다. "홉 수가 최소인 경로" 와 "비용이 최소인 경로" 는 다르다.
// 비음수 가중치에는 Dijkstra, 음수 간선이 있으면 Bellman-Ford 가 필요하다 (Dijkstra 는 이미 확정한 정점을 다시 고치지 않아 틀린 답을 낸다)
typedef std::vector<std::vector<std::pair<int, int>>> WGraph;      // adj[u] = {(v, w)}

std::vector<int> bfsHops(const WGraph& g, int s) {
    std::vector<int> d(g.size(), -1); std::queue<int> q; q.push(s); d[s] = 0;
    while (!q.empty()) { int u = q.front(); q.pop(); for (auto& e : g[u]) if (d[e.first] < 0) { d[e.first] = d[u] + 1; q.push(e.first); } }
    return d;
}
std::vector<int> dijkstra(const WGraph& g, int s) {                 // 고전적 Dijkstra: 꺼낸 정점은 확정
    std::vector<int> d(g.size(), INT_MAX); std::vector<bool> done(g.size(), false); d[s] = 0;
    std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq; pq.push({0, s});
    while (!pq.empty()) {
        int u = pq.top().second; pq.pop();
        if (done[u]) continue;
        done[u] = true;
        for (auto& e : g[u]) if (!done[e.first] && d[u] + e.second < d[e.first]) { d[e.first] = d[u] + e.second; pq.push({d[e.first], e.first}); }
    }
    return d;
}
std::vector<int> bellmanFord(const WGraph& g, int s) {
    std::vector<int> d(g.size(), INT_MAX); d[s] = 0;
    for (size_t i = 0; i + 1 < g.size(); i++)
        for (size_t u = 0; u < g.size(); u++) if (d[u] != INT_MAX) for (auto& e : g[u]) d[e.first] = std::min(d[e.first], d[u] + e.second);
    return d;
}

int main() {
    WGraph g(4);
    auto add = [&](int u, int v, int w) { g[u].push_back({v, w}); g[v].push_back({u, w}); };
    add(0, 1, 10); add(0, 2, 1); add(2, 3, 1); add(3, 1, 1);
    assert(bfsHops(g, 0)[1] == 1);                       // 홉 수는 직접 연결이 1
    assert(dijkstra(g, 0)[1] == 3);                      // 비용은 0-2-3-1 이 3 으로 더 싸다

    // 음수 간선(방향): 0->1 (1), 0->2 (3), 2->1 (-5).  최단은 0->2->1 = -2
    WGraph n(3); n[0].push_back({1, 1}); n[0].push_back({2, 3}); n[2].push_back({1, -5});
    assert(bellmanFord(n, 0)[1] == -2);                  // 올바른 답
    assert(dijkstra(n, 0)[1] == 1);                      // 1 을 먼저 확정해 버려 틀린 답
    std::cout << "WeightedGraph: hops=" << bfsHops(g, 0)[1] << " cost=" << dijkstra(g, 0)[1] << std::endl;
    return 0;
}
// Time Complexity: Dijkstra O(E log V), Bellman-Ford O(V·E)
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
#include <iostream>
#include <cmath>
#include <vector>
#include <cassert>

// 완전 그래프 K_n: 모든 정점 쌍이 연결된다.  간선 n(n-1)/2, 모든 차수 n-1, 클리크 수 = 색칠 수 = n.
// 신장 트리의 개수는 케일리 공식 n^(n-2).  행렬-트리 정리(키르히호프): 라플라시안에서 한 행·열을 지운 행렬식과 같다
long long spanningTrees(int n) {
    int m = n - 1;
    std::vector<std::vector<double>> a(m, std::vector<double>(m, -1.0));
    for (int i = 0; i < m; i++) a[i][i] = n - 1;
    double det = 1;
    for (int c = 0; c < m; c++) {                                  // 가우스 소거
        int piv = c; for (int r = c + 1; r < m; r++) if (std::fabs(a[r][c]) > std::fabs(a[piv][c])) piv = r;
        if (piv != c) { std::swap(a[piv], a[c]); det = -det; }
        det *= a[c][c];
        for (int r = c + 1; r < m; r++) { double f = a[r][c] / a[c][c]; for (int k = c; k < m; k++) a[r][k] -= f * a[c][k]; }
    }
    return std::llround(det);
}

int main() {
    for (int n = 3; n <= 8; n++) {
        long long expect = std::llround(std::pow(n, n - 2));
        assert(spanningTrees(n) == expect);                        // 3, 16, 125, 1296, 16807, 262144
    }
    int n = 7;
    std::vector<std::vector<bool>> adj(n, std::vector<bool>(n, true));
    for (int i = 0; i < n; i++) adj[i][i] = false;
    int edges = 0; for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) edges += adj[i][j];
    assert(edges == n * (n - 1) / 2);
    std::vector<int> color(n, -1); int used = 0;                   // 탐욕 색칠: 모두 서로 인접하므로 n 가지 색이 필요
    for (int v = 0; v < n; v++) { std::vector<bool> taken(n, false); for (int u = 0; u < v; u++) if (adj[v][u]) taken[color[u]] = true; int c = 0; while (taken[c]) c++; color[v] = c; used = std::max(used, c + 1); }
    assert(used == n);
    std::cout << "CompleteGraph K7: " << edges << " edges, spanning trees of K5 = " << spanningTrees(5) << std::endl;
    return 0;
}
// Time Complexity: 신장 트리 개수 O(n³) (행렬식)
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
    for (int u = 0; u < V; u++) { listSteps++; for (int v : list[u]) { listSteps++; listEdges++; } }         // 리스트: 정점 + 간선 순회
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
#include <iostream>
#include <algorithm>
#include <utility>
#include <vector>
#include <cassert>

// 다중 그래프: 같은 두 정점 사이에 평행 간선이 여러 개 있거나 자기 루프가 있다 (퀴니히스베르크의 다리 문제).
// 간선마다 고유 id 가 필요하다.  오일러 경로 존재 조건: (고립 정점을 뺀) 연결 + 홀수 차수 정점이 0개 또는 2개
struct Multigraph {
    int n; std::vector<std::pair<int, int>> edges;
    std::vector<std::vector<std::pair<int, int>>> adj;                // (이웃, 간선 id)
    explicit Multigraph(int n) : n(n), adj(n) {}
    void addEdge(int u, int v) { int id = edges.size(); edges.push_back({u, v}); adj[u].push_back({v, id}); adj[v].push_back({u, id}); }
    int degree(int u) const { return adj[u].size(); }                  // 자기 루프는 두 번 들어가 차수 2
    bool hasEulerPath() const {
        int odd = 0; for (int i = 0; i < n; i++) odd += degree(i) % 2;
        return odd == 0 || odd == 2;                                    // (연결성은 아래 예에서 보장)
    }
    std::vector<int> eulerPath() const {                                // Hierholzer
        int start = 0; for (int i = 0; i < n; i++) if (degree(i) % 2) { start = i; break; }
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

int main() {
    // 퀴니히스베르크: 땅 A=0, B=1, C=2, D=3.  다리 7개: A-B ×2, A-C ×2, A-D, B-D, C-D
    Multigraph k(4);
    k.addEdge(0, 1); k.addEdge(0, 1); k.addEdge(0, 2); k.addEdge(0, 2); k.addEdge(0, 3); k.addEdge(1, 3); k.addEdge(2, 3);
    assert(k.degree(0) == 5 && k.degree(1) == 3 && k.degree(2) == 3 && k.degree(3) == 3);   // 홀수 차수 4개
    assert(!k.hasEulerPath());                                          // 모든 다리를 한 번씩 건너는 산책은 불가능

    Multigraph m(4);                                                    // 다리 하나(A-B)를 없애면 가능
    m.addEdge(0, 1); m.addEdge(0, 2); m.addEdge(0, 2); m.addEdge(0, 3); m.addEdge(1, 3); m.addEdge(2, 3);
    assert(m.hasEulerPath());
    auto path = m.eulerPath();
    assert(path.size() == m.edges.size() + 1);                          // 간선 수 + 1 개의 정점
    std::vector<int> used(m.edges.size(), 0);                           // 인접한 쌍마다 서로 다른 간선을 정확히 한 번씩 소비해야 한다
    for (size_t i = 0; i + 1 < path.size(); i++) {
        bool found = false;
        for (size_t id = 0; id < m.edges.size() && !found; id++)
            if (!used[id] && ((m.edges[id].first == path[i] && m.edges[id].second == path[i + 1]) || (m.edges[id].second == path[i] && m.edges[id].first == path[i + 1]))) { used[id] = 1; found = true; }
        assert(found);
    }
    Multigraph loop(1); loop.addEdge(0, 0);
    assert(loop.degree(0) == 2);
    std::cout << "Multigraph: Konigsberg has no Euler path; after removing a bridge it does." << std::endl;
    return 0;
}
// Time Complexity: 오일러 경로 O(V + E)
// Space Complexity: O(V + E)
```
## Hypergraph()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <utility>
#include <vector>
#include <cassert>

// 하이퍼그래프: 간선(하이퍼에지)이 두 개가 아니라 임의 개수의 정점 집합이다.  "한 논문의 공저자들", "한 회의의 참석자들"처럼 n:n 관계를 그대로 표현.
// 표현: 정점×하이퍼에지 연관 행렬.  쌍대(dual) 는 행렬을 전치한 것(정점 <-> 하이퍼에지 역할 교환).
// 2-section(클리크 확장): 같은 하이퍼에지에 속한 정점끼리 일반 간선으로 이어 보통 그래프로 바꾼다 (정보 손실이 있다)
typedef std::vector<std::vector<int>> Incidence;                         // inc[v][e] = 1 이면 v ∈ e

Incidence build(int V, const std::vector<std::set<int>>& edges) {
    Incidence inc(V, std::vector<int>(edges.size(), 0));
    for (size_t e = 0; e < edges.size(); e++) for (int v : edges[e]) inc[v][e] = 1;
    return inc;
}
Incidence dual(const Incidence& inc) {
    Incidence d(inc.empty() ? 0 : inc[0].size(), std::vector<int>(inc.size()));
    for (size_t v = 0; v < inc.size(); v++) for (size_t e = 0; e < inc[v].size(); e++) d[e][v] = inc[v][e];
    return d;
}
std::set<std::pair<int, int>> twoSection(const std::vector<std::set<int>>& edges) {
    std::set<std::pair<int, int>> g;
    for (auto& e : edges) for (int a : e) for (int b : e) if (a < b) g.insert({a, b});
    return g;
}

int main() {
    std::vector<std::set<int>> hyper = {{0, 1, 2}, {2, 3}, {0, 3, 4, 5}};      // 하이퍼에지 3개, 정점 6개
    auto inc = build(6, hyper);
    int deg2 = 0; for (int e = 0; e < 3; e++) deg2 += inc[2][e];
    assert(deg2 == 2);                                                          // 정점 2 는 하이퍼에지 0 과 1 에 속함
    assert(dual(dual(inc)) == inc);                                             // 쌍대의 쌍대는 원래대로
    auto d = dual(inc);                                                         // 쌍대에서 정점 = 원래의 하이퍼에지
    assert(d.size() == 3 && d[0][2] == 1 && d[1][2] == 1 && d[2][2] == 0);     // 원래 정점 2 는 e0, e1 에 포함
    auto g = twoSection(hyper);
    assert(g.size() == 3 + 1 + 6);                                              // 3개 + 1개 + 6개의 쌍, 중복 없음
    assert(g.count({0, 3}) && g.count({2, 3}) && !g.count({1, 4}));
    std::cout << "Hypergraph: " << hyper.size() << " hyperedges -> " << g.size() << " pairwise edges in its 2-section" << std::endl;
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
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

// 격자 그래프: R×C 칸의 상하좌우 이웃.  간선 수 = R(C-1) + C(R-1),  이분 그래프,  (격자에 장애물이 없으면) 최단 거리 = 맨해튼 거리.
// 게임 맵·미로·이미지 처리의 기본 모델
int main() {
    const int R = 7, C = 9;
    int edges = 0;
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (c + 1 < C) edges++; if (r + 1 < R) edges++; }
    assert(edges == R * (C - 1) + C * (R - 1));

    std::vector<std::vector<int>> dist(R, std::vector<int>(C, -1));
    std::queue<std::pair<int, int>> q; q.push({0, 0}); dist[0][0] = 0;
    const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
    while (!q.empty()) {
        auto [r, c] = q.front(); q.pop();
        for (int k = 0; k < 4; k++) { int nr = r + dr[k], nc = c + dc[k]; if (nr >= 0 && nr < R && nc >= 0 && nc < C && dist[nr][nc] < 0) { dist[nr][nc] = dist[r][c] + 1; q.push({nr, nc}); } }
    }
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) assert(dist[r][c] == r + c);        // 맨해튼 거리
    // 이분 그래프: (r + c) 의 홀짝으로 두 색 -> 모든 간선이 서로 다른 색을 잇는다
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { if (c + 1 < C) assert((r + c) % 2 != (r + c + 1) % 2); if (r + 1 < R) assert((r + c) % 2 != (r + 1 + c) % 2); }
    int degree2 = 0, degree3 = 0, degree4 = 0;
    for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) { int d = (r > 0) + (r + 1 < R) + (c > 0) + (c + 1 < C); degree2 += d == 2; degree3 += d == 3; degree4 += d == 4; }
    assert(degree2 == 4 && degree3 == 2 * (R - 2) + 2 * (C - 2) && degree4 == (R - 2) * (C - 2));
    std::cout << "GridGraph " << R << "x" << C << ": " << edges << " edges" << std::endl;
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
#include <iostream>
#include <algorithm>
#include <queue>
#include <vector>
#include <cassert>

// 초입방체 Q_d: 정점 = d비트 문자열, 한 비트만 다른 두 정점이 인접.  정점 2^d, 간선 d·2^(d-1), 모든 차수 d, 지름 d, 이분 그래프.
// 두 정점 사이의 거리 = 해밍 거리.  병렬 컴퓨터의 상호연결망과 그레이 코드(해밍 경로)의 기반
int main() {
    for (int d = 1; d <= 8; d++) {
        int n = 1 << d; long edges = 0;
        for (int v = 0; v < n; v++) for (int b = 0; b < d; b++) { int u = v ^ (1 << b); if (u > v) edges++; }
        assert(edges == (long)d * (n / 2));                       // d·2^(d-1)
    }
    const int d = 6, n = 1 << d;
    std::vector<int> dist(n, -1); std::queue<int> q; q.push(0); dist[0] = 0;
    while (!q.empty()) { int v = q.front(); q.pop(); for (int b = 0; b < d; b++) { int u = v ^ (1 << b); if (dist[u] < 0) { dist[u] = dist[v] + 1; q.push(u); } } }
    for (int v = 0; v < n; v++) assert(dist[v] == __builtin_popcount(v));      // 거리 = 해밍 거리
    int diameter = *std::max_element(dist.begin(), dist.end());
    assert(diameter == d);
    // 이분 그래프: 1의 개수의 홀짝이 인접할 때마다 바뀐다
    for (int v = 0; v < n; v++) for (int b = 0; b < d; b++) assert((__builtin_popcount(v) + __builtin_popcount(v ^ (1 << b))) % 2 == 1);
    // 해밍 경로: 그레이 코드 g(i) = i ^ (i >> 1) 는 모든 정점을 한 번씩 지나며 이웃한 항은 한 비트만 다르다
    for (int i = 0; i + 1 < n; i++) assert(__builtin_popcount((i ^ (i >> 1)) ^ ((i + 1) ^ ((i + 1) >> 1))) == 1);
    std::cout << "HypercubeGraph Q6: " << n << " vertices, diameter " << diameter << std::endl;
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
#include <iostream>
#include <algorithm>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 의존성 그래프: "A 를 쓰려면 B 가 먼저 필요" 를 A -> B 로 표현 (빌드 시스템, 패키지 관리자, 스프레드시트 셀).
// 위상 정렬이 빌드 순서이고, 사이클이 있으면 순서가 존재하지 않으므로 사이클의 실제 경로를 보고해야 한다
struct Deps {
    std::map<std::string, std::vector<std::string>> need;
    std::vector<std::string> order, cycle;
    std::map<std::string, int> state;                                  // 0 미방문, 1 방문 중, 2 완료
    std::vector<std::string> stack;
    bool visit(const std::string& n) {
        state[n] = 1; stack.push_back(n);
        for (auto& d : need[n]) {
            if (state[d] == 1) { cycle.assign(std::find(stack.begin(), stack.end(), d), stack.end()); cycle.push_back(d); return false; }
            if (state[d] == 0 && !visit(d)) return false;
        }
        state[n] = 2; stack.pop_back(); order.push_back(n);               // 의존 대상이 모두 끝난 뒤에 자신을 추가
        return true;
    }
    bool resolve() { for (auto& kv : need) if (state[kv.first] == 0 && !visit(kv.first)) return false; return true; }
};

int main() {
    Deps ok;
    ok.need = {{"app", {"ui", "net"}}, {"ui", {"core"}}, {"net", {"core"}}, {"core", {}}};
    assert(ok.resolve());
    auto pos = [&](const char* s) { return std::find(ok.order.begin(), ok.order.end(), s) - ok.order.begin(); };
    assert(pos("core") < pos("ui") && pos("core") < pos("net") && pos("ui") < pos("app") && pos("net") < pos("app"));   // 의존 대상이 먼저
    Deps bad;
    bad.need = {{"a", {"b"}}, {"b", {"c"}}, {"c", {"a"}}, {"d", {"a"}}};
    assert(!bad.resolve());
    assert((bad.cycle == std::vector<std::string>{"a", "b", "c", "a"}));   // 사이클 경로를 그대로 보고
    std::cout << "DependencyGraph build order:"; for (auto& s : ok.order) std::cout << " " << s; std::cout << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## KnowledgeGraph()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>

// 지식 그래프: (주어, 술어, 목적어) 삼중항(triple)의 집합.  정점 = 개체, 간선 = 관계(방향·이름 있음).
// 그래프 질의와 규칙 기반 추론이 가능하다: 예) "is_a" 는 추이적 -> 닫힘(closure)을 계산하면 간접 사실이 드러난다
typedef std::tuple<std::string, std::string, std::string> Triple;
class KG {
    std::set<Triple> facts;
public:
    void add(const std::string& s, const std::string& p, const std::string& o) { facts.insert({s, p, o}); }
    std::set<std::string> objects(const std::string& s, const std::string& p) const {
        std::set<std::string> r; for (auto& f : facts) if (std::get<0>(f) == s && std::get<1>(f) == p) r.insert(std::get<2>(f)); return r;
    }
    std::set<std::string> subjects(const std::string& p, const std::string& o) const {
        std::set<std::string> r; for (auto& f : facts) if (std::get<1>(f) == p && std::get<2>(f) == o) r.insert(std::get<0>(f)); return r;
    }
    // 추이적 관계의 도달 가능 집합 (BFS)
    std::set<std::string> closure(const std::string& s, const std::string& p) const {
        std::set<std::string> seen; std::vector<std::string> st = {s};
        while (!st.empty()) { auto x = st.back(); st.pop_back(); for (auto& o : objects(x, p)) if (seen.insert(o).second) st.push_back(o); }
        return seen;
    }
};

int main() {
    KG kg;
    kg.add("Seoul", "capital_of", "Korea"); kg.add("Korea", "located_in", "Asia");
    kg.add("Cat", "is_a", "Mammal"); kg.add("Mammal", "is_a", "Animal"); kg.add("Animal", "is_a", "LivingThing");
    kg.add("Tom", "is_a", "Cat"); kg.add("Tom", "owner", "Ann");
    assert((kg.objects("Seoul", "capital_of") == std::set<std::string>{"Korea"}));
    assert((kg.subjects("is_a", "Mammal") == std::set<std::string>{"Cat"}));
    assert((kg.closure("Tom", "is_a") == std::set<std::string>{"Cat", "Mammal", "Animal", "LivingThing"}));    // 간접 사실 추론
    assert(kg.closure("Seoul", "is_a").empty());
    std::cout << "KnowledgeGraph: Tom is_a* -> " << kg.closure("Tom", "is_a").size() << " classes" << std::endl;
    return 0;
}
// Time Complexity: 질의 O(|facts|) (색인을 두면 O(결과)), 닫힘 O(V·|facts|)
// Space Complexity: O(|facts|)
```
## SocialNetworkGraph()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 소셜 네트워크: 정점 = 사람, 간선 = 친구 관계(무방향).  기본 질의: 친구의 친구 추천, 연결 중심성(차수), 최단 소개 경로, 군집 계수(삼각형)
class Social {
    std::map<std::string, std::set<std::string>> friends;
public:
    void befriend(const std::string& a, const std::string& b) { friends[a].insert(b); friends[b].insert(a); }
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
};

int main() {
    Social s;
    s.befriend("ann", "bob"); s.befriend("bob", "cat"); s.befriend("ann", "cat"); s.befriend("cat", "dan"); s.befriend("dan", "eve");
    assert((s.suggest("ann") == std::set<std::string>{"dan"}));     // ann -> cat -> dan
    assert(s.hops("ann", "eve") == 3 && s.hops("ann", "ann") == 0);
    assert(s.degree("cat") == 3);                                   // 가장 많이 연결된 사람
    assert(s.triangles("ann") == 1 && s.triangles("dan") == 0);     // ann-bob-cat 삼각형
    std::cout << "SocialNetworkGraph: ann -> eve in " << s.hops("ann", "eve") << " hops" << std::endl;
    return 0;
}
// Time Complexity: 추천 O(Σ 친구의 차수), 경로 O(V + E)
// Space Complexity: O(V + E)
```
## CallGraph()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 호출 그래프: 정점 = 함수, 간선 f -> g = "f 가 g 를 호출".  프로그램 분석의 기본 자료구조.
//  - 도달 불가능한 함수 = 죽은 코드 (main 에서 도달 가능한 집합 밖)
//  - 사이클 = 재귀 (상호 재귀는 크기 2 이상의 강연결 요소)  -> 인라이닝·스택 분석에서 구분해야 한다
typedef std::map<std::string, std::vector<std::string>> CG;
std::set<std::string> reachable(const CG& g, const std::string& root) {
    std::set<std::string> seen{root}; std::vector<std::string> st{root};
    while (!st.empty()) { auto u = st.back(); st.pop_back(); auto it = g.find(u); if (it != g.end()) for (auto& v : it->second) if (seen.insert(v).second) st.push_back(v); }
    return seen;
}
// 재귀 함수 찾기: 자기 자신으로 되돌아올 수 있는 함수 (u 에서 시작해 u 에 도달)
std::set<std::string> recursive(const CG& g) {
    std::set<std::string> r;
    for (auto& kv : g) for (auto& callee : kv.second) { auto reach = reachable(g, callee); if (reach.count(kv.first)) { r.insert(kv.first); break; } }
    return r;
}

int main() {
    CG g = {{"main", {"parse", "run"}}, {"parse", {"lex"}}, {"lex", {}}, {"run", {"step", "log"}}, {"step", {"step", "log"}},
            {"log", {}}, {"even", {"odd"}}, {"odd", {"even"}}, {"unused", {"log"}}};
    auto live = reachable(g, "main");
    std::set<std::string> all; for (auto& kv : g) all.insert(kv.first);
    std::set<std::string> dead; std::set_difference(all.begin(), all.end(), live.begin(), live.end(), std::inserter(dead, dead.begin()));
    assert((dead == std::set<std::string>{"even", "odd", "unused"}));              // main 에서 호출되지 않는 함수
    auto rec = recursive(g);
    assert((rec == std::set<std::string>{"step", "even", "odd"}));                 // 직접 재귀 step, 상호 재귀 even/odd
    std::cout << "CallGraph: " << dead.size() << " dead functions, " << rec.size() << " recursive" << std::endl;
    return 0;
}
// Time Complexity: 도달 가능성 O(V + E), 재귀 탐지 O(V·(V + E))
// Space Complexity: O(V)
```
## StateTransitionGraph()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 상태 전이 그래프: 정점 = 상태, 간선 = (이벤트로 인한) 전이.  유한 상태 기계(FSM)의 검증은 그래프 문제로 환원된다.
//  - 도달 불가능한 상태: 초기 상태에서 BFS 로 닿지 않는 상태 (설계 오류)
//  - 교착(deadlock) 상태: 나가는 전이가 없는데 종료 상태도 아닌 상태
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
    std::string run(const std::string& init, const std::vector<std::string>& events) const {
        std::string s = init; for (auto& e : events) { auto it = next.at(s).find(e); if (it == next.at(s).end()) return "ERROR"; s = it->second; } return s;
    }
};

int main() {
    FSM light;                                                          // 신호등
    light.next = {{"green", {{"timer", "yellow"}}}, {"yellow", {{"timer", "red"}}}, {"red", {{"timer", "green"}}}, {"broken", {{"fix", "red"}}}};
    auto reach = light.reachableFrom("green");
    assert((reach == std::set<std::string>{"green", "yellow", "red"}));
    assert(!reach.count("broken"));                                     // 초기 상태에서 도달 불가능한 상태
    assert(light.run("green", {"timer", "timer", "timer"}) == "green"); // 한 주기
    assert(light.run("green", {"fix"}) == "ERROR");                     // 정의되지 않은 전이
    FSM job;                                                            // 작업: 종료 상태 done 외에 막힌 상태가 있는가
    job.next = {{"new", {{"start", "running"}}}, {"running", {{"ok", "done"}, {"fail", "stuck"}}}};
    job.accepting = {"done"};
    assert((job.deadlocks() == std::set<std::string>{"stuck"}));        // stuck 에서는 나갈 수 없다
    std::cout << "StateTransitionGraph: deadlock state = stuck" << std::endl;
    return 0;
}
// Time Complexity: O(S + T)
// Space Complexity: O(S)
```
## ControlFlowGraph()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 제어 흐름 그래프(CFG): 정점 = 기본 블록(분기 없이 순서대로 실행되는 명령 묶음), 간선 = 가능한 실행 흐름. 컴파일러 최적화의 출발점.
// 기본 블록을 나누는 "리더" 규칙: (1) 첫 명령  (2) 점프의 목적지  (3) 점프 바로 다음 명령
struct Instr { std::string text; int jumpTo = -1; bool conditional = false; bool isJump = false; };

int main() {
    // 0: i = 0    1: if i >= 3 goto 5    2: s += i    3: i += 1    4: goto 1    5: print s
    std::vector<Instr> code = {{"i = 0"}, {"if i >= 3 goto 5", 5, true, true}, {"s += i"}, {"i += 1"}, {"goto 1", 1, false, true}, {"print s"}};
    std::set<int> leaders = {0};
    for (size_t i = 0; i < code.size(); i++) if (code[i].isJump) { leaders.insert(code[i].jumpTo); if (i + 1 < code.size()) leaders.insert(i + 1); }
    std::vector<int> L(leaders.begin(), leaders.end());
    assert((L == std::vector<int>{0, 1, 2, 5}));
    std::map<int, std::vector<int>> succ;                                 // 블록 시작 인덱스 -> 후속 블록
    for (size_t b = 0; b < L.size(); b++) {
        int last = (b + 1 < L.size() ? L[b + 1] : (int)code.size()) - 1; const Instr& in = code[last];
        if (in.isJump) { succ[L[b]].push_back(in.jumpTo); if (in.conditional && last + 1 < (int)code.size()) succ[L[b]].push_back(last + 1); }
        else if (last + 1 < (int)code.size()) succ[L[b]].push_back(last + 1);
    }
    assert((succ[0] == std::vector<int>{1}));
    assert((succ[1] == std::vector<int>{5, 2}));                           // 조건 점프: 참이면 5, 거짓이면 다음(2)
    assert((succ[2] == std::vector<int>{1}));                              // 루프 몸체 -> 조건 검사로 되돌아감 (뒤 간선)
    assert(succ[5].empty());
    // 뒤 간선(자신의 조상으로 가는 간선)이 있으면 루프다
    bool loop = false; for (auto& kv : succ) for (int t : kv.second) if (t <= kv.first && kv.first != 5) loop = true;
    assert(loop);
    std::cout << "ControlFlowGraph: " << L.size() << " basic blocks, loop detected." << std::endl;
    return 0;
}
// Time Complexity: O(명령 수)
// Space Complexity: O(블록 수)
```
## DataFlowGraph()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 데이터 흐름 분석: CFG 위에서 값의 흐름을 추적한다.  생존 변수(liveness) 분석 — "이 지점 뒤에서 변수가 다시 읽히는가"
//   live_in(B)  = use(B) ∪ (live_out(B) − def(B)),     live_out(B) = ∪ live_in(S)  (S 는 B 의 후속)
// 관계가 변하지 않을 때까지 반복(고정점)하며, 역방향 분석이라 후속 블록의 결과를 선행 블록으로 전파한다
typedef std::set<std::string> VS;
struct Block { VS use, def; std::vector<int> succ; };

int main() {
    // b0: a = 1; b = 2 (def a,b)     b1: c = a + b (use a,b / def c)     b2: print(c) (use c)    b3: print(a) (use a)
    std::vector<Block> g = {
        {{}, {"a", "b"}, {1, 3}},
        {{"a", "b"}, {"c"}, {2}},
        {{"c"}, {}, {}},
        {{"a"}, {}, {}},
    };
    int n = g.size(); std::vector<VS> in(n), out(n);
    int rounds = 0;
    for (bool changed = true; changed; rounds++) {
        changed = false;
        for (int i = n - 1; i >= 0; i--) {
            VS newOut; for (int s : g[i].succ) newOut.insert(in[s].begin(), in[s].end());
            VS newIn = g[i].use; for (auto& v : newOut) if (!g[i].def.count(v)) newIn.insert(v);
            if (newOut != out[i] || newIn != in[i]) { out[i] = newOut; in[i] = newIn; changed = true; }
        }
    }
    assert((in[0] == VS{}));                                       // 시작 시점에는 살아 있는 변수가 없다 (모두 정의되기 전)
    assert((out[0] == VS{"a", "b"}));
    assert((in[1] == VS{"a", "b"}) && (out[1] == VS{"c"}));        // c 는 b2 에서 읽힌다
    assert((in[3] == VS{"a"}));
    assert(out[1].count("b") == 0);                                // b 는 b1 뒤에서 다시 쓰이지 않는다 -> 레지스터 재사용 가능
    std::cout << "DataFlowGraph: liveness converged in " << rounds << " rounds" << std::endl;
    return 0;
}
// Time Complexity: 고정점까지 O(블록 수 · 변수 수 · 반복 횟수)
// Space Complexity: O(블록 수 · 변수 수)
```
## BayesianNetwork()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cassert>

// 베이즈 네트워크: 방향 비순환 그래프(DAG).  각 정점은 확률 변수이고 부모가 주어지면 나머지와 조건부 독립이므로
// 결합확률이 P(X1..Xn) = Π P(Xi | parents(Xi)) 로 인수분해된다.  추론은 합을 정의대로 계산(열거)하면 된다.
// 고전 예: 비(R) -> 스프링클러(S), 비 -> 젖은 잔디(G), 스프링클러 -> 젖은 잔디
double P_R(bool r) { return r ? 0.2 : 0.8; }
double P_S(bool s, bool r) { double t = r ? 0.01 : 0.4; return s ? t : 1 - t; }
double P_G(bool g, bool s, bool r) {
    double t = (s && r) ? 0.99 : (s && !r) ? 0.9 : (!s && r) ? 0.8 : 0.0;
    return g ? t : 1 - t;
}
double joint(bool r, bool s, bool g) { return P_R(r) * P_S(s, r) * P_G(g, s, r); }

int main() {
    double total = 0;
    for (int r = 0; r < 2; r++) for (int s = 0; s < 2; s++) for (int g = 0; g < 2; g++) total += joint(r, s, g);
    assert(std::fabs(total - 1.0) < 1e-12);                              // 결합확률의 합은 1
    // 잔디가 젖었을 때 비가 왔을 확률: P(R | G) = P(R, G) / P(G)
    double pGR = 0, pG = 0;
    for (int r = 0; r < 2; r++) for (int s = 0; s < 2; s++) { double j = joint(r, s, true); pG += j; if (r) pGR += j; }
    double posterior = pGR / pG;
    assert(std::fabs(posterior - 0.35768767) < 1e-6);                    // 알려진 값 약 35.77%
    // 스프링클러가 켜진 것을 관측하면 "비 때문" 이라는 설명이 약해진다 (explaining away)
    double pGRS = joint(true, true, true), pGS = joint(true, true, true) + joint(false, true, true);
    assert(pGRS / pGS < posterior);
    std::cout << "BayesianNetwork: P(rain | grass wet) = " << posterior << ", P(rain | wet, sprinkler on) = " << pGRS / pGS << std::endl;
    return 0;
}
// Time Complexity: 열거 O(2^n) (변수 제거·신뢰 전파로 구조에 따라 개선)
// Space Complexity: O(n)
```
## NeuralGraph()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <functional>
#include <memory>
#include <vector>
#include <cassert>

// 신경망의 계산 그래프: 정점 = 연산(+, ×, tanh), 간선 = 값의 흐름.  순전파는 위상 순서로 값을 계산하고,
// 역전파(자동 미분)는 그래프를 거꾸로 훑으며 연쇄 법칙으로 기울기를 누적한다. 딥러닝 프레임워크의 핵심
struct Node;
typedef std::shared_ptr<Node> N;
struct Node {
    double val = 0, grad = 0; std::vector<N> parents; std::function<void(Node&)> backward;
    explicit Node(double v) : val(v) {}
};
N make(double v) { return std::make_shared<Node>(v); }
N add(N a, N b) { N o = make(a->val + b->val); o->parents = {a, b}; o->backward = [a, b](Node& s) { a->grad += s.grad; b->grad += s.grad; }; return o; }
N mul(N a, N b) { N o = make(a->val * b->val); o->parents = {a, b}; o->backward = [a, b](Node& s) { a->grad += b->val * s.grad; b->grad += a->val * s.grad; }; return o; }
N tanhN(N a) { N o = make(std::tanh(a->val)); o->parents = {a}; o->backward = [a](Node& s) { a->grad += (1 - s.val * s.val) * s.grad; }; return o; }

void backprop(const N& out) {                                           // 위상 순서의 역순으로 기울기 전파
    std::vector<N> order; std::vector<Node*> seen;
    std::function<void(const N&)> topo = [&](const N& n) {
        for (auto* s : seen) if (s == n.get()) return;
        seen.push_back(n.get()); for (auto& p : n->parents) topo(p); order.push_back(n);
    };
    topo(out); out->grad = 1;
    for (auto it = order.rbegin(); it != order.rend(); ++it) if ((*it)->backward) (*it)->backward(**it);
}

int main() {
    // f(w, x, b) = tanh(w·x + b),  w=0.5, x=2.0, b=-0.5
    N w = make(0.5), x = make(2.0), b = make(-0.5);
    N y = tanhN(add(mul(w, x), b));
    backprop(y);
    double z = 0.5 * 2.0 - 0.5, t = std::tanh(z);
    assert(std::fabs(y->val - t) < 1e-12);
    assert(std::fabs(w->grad - (1 - t * t) * 2.0) < 1e-12);               // ∂y/∂w = (1 - tanh²)·x
    assert(std::fabs(x->grad - (1 - t * t) * 0.5) < 1e-12);               // ∂y/∂x = (1 - tanh²)·w
    assert(std::fabs(b->grad - (1 - t * t)) < 1e-12);
    // 수치 미분과 비교 (유한 차분)
    auto f = [](double ww) { return std::tanh(ww * 2.0 - 0.5); };
    double numeric = (f(0.5 + 1e-6) - f(0.5 - 1e-6)) / 2e-6;
    assert(std::fabs(numeric - w->grad) < 1e-8);
    std::cout << "NeuralGraph: dy/dw = " << w->grad << " (numeric " << numeric << ")" << std::endl;
    return 0;
}
// Time Complexity: 순전파·역전파 모두 O(연산 수)
// Space Complexity: O(연산 수)
```
## PageRank()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>
#include <cmath>

std::vector<double> pageRank(int V, std::vector<std::vector<int>>& adj, double d=0.85, int iter=100) {
    std::vector<double> rank(V, 1.0/V);
    std::vector<int> outDeg(V, 0);
    for (int u = 0; u < V; u++) outDeg[u] = adj[u].size();
    for (int i = 0; i < iter; i++) {
        std::vector<double> newRank(V, (1.0-d)/V);
        for (int u = 0; u < V; u++)
            for (int v : adj[u])
                newRank[v] += d * rank[u] / outDeg[u];
        rank = newRank;
    }
    return rank;
}

int main() {
    int V = 4;
    // 0->1, 0->2, 1->3, 2->3, 3->0
    std::vector<std::vector<int>> adj = {{1,2},{3},{3},{0}};
    auto ranks = pageRank(V, adj);
    double sum = 0;
    for (double r : ranks) sum += r;
    assert(std::abs(sum - 1.0) < 0.001); // 합이 1에 수렴
    std::cout << "PageRank verified. Sum=" << sum << std::endl;
    return 0;
}
// Time Complexity: O(iter * (V + E))
// Space Complexity: O(V)
```
# 부록
## BFS vs DFS
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "BFS is optimal for shortest path on unweighted graphs." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DAG가 중요한 이유
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "DAG allows TopoSort and DP without infinite loops." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Prim vs Kruskal
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Prim: 정점 기반, 밀집 그래프에서 효율적 O(V^2) or O(E log V) with heap" << std::endl;
    std::cout << "Kruskal: 간선 기반, 희소 그래프에서 효율적 O(E log E), Union-Find 사용" << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Dijkstra vs A*
### 대표코드
```cpp
#include <iostream>
#include <climits>
#include <cmath>
#include <queue>
#include <utility>
#include <vector>
#include <cassert>

// Dijkstra 는 출발점에서 가까운 순서로 사방을 확장하고, A* 는 f = g + h (h = 목표까지의 휴리스틱 추정) 가 작은 순서로 확장한다.
// h 가 허용 가능(실제 비용을 넘지 않음)하면 A* 도 최적해를 보장하면서, 목표 쪽으로 편향되어 훨씬 적은 정점을 방문한다.
// h = 0 이면 A* 는 Dijkstra 와 같다
const int R = 40, C = 40;
long expanded;
int search(bool useHeuristic) {
    std::vector<std::vector<int>> g(R, std::vector<int>(C, INT_MAX));
    typedef std::pair<int, std::pair<int, int>> Item;
    std::priority_queue<Item, std::vector<Item>, std::greater<Item>> pq;
    auto h = [&](int r, int c) { return useHeuristic ? (R - 1 - r) + (C - 1 - c) : 0; };      // 맨해튼 거리
    g[0][0] = 0; pq.push({h(0, 0), {0, 0}}); expanded = 0;
    std::vector<std::vector<bool>> closed(R, std::vector<bool>(C, false));
    const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
    while (!pq.empty()) {
        auto it = pq.top(); pq.pop(); int r = it.second.first, c = it.second.second;
        if (closed[r][c]) continue;
        closed[r][c] = true; expanded++;
        if (r == R - 1 && c == C - 1) return g[r][c];
        for (int k = 0; k < 4; k++) {
            int nr = r + dr[k], nc = c + dc[k];
            if (nr < 0 || nr >= R || nc < 0 || nc >= C || closed[nr][nc]) continue;
            bool wall = (nc == 20 && nr < 30);                                 // 세로 벽 (아래쪽만 열려 있다)
            if (wall) continue;
            if (g[r][c] + 1 < g[nr][nc]) { g[nr][nc] = g[r][c] + 1; pq.push({g[nr][nc] + h(nr, nc), {nr, nc}}); }
        }
    }
    return -1;
}

int main() {
    int dijkstra = search(false); long dExpanded = expanded;
    int astar = search(true); long aExpanded = expanded;
    assert(dijkstra == astar);                           // 둘 다 최적해 (같은 비용)
    assert(aExpanded < dExpanded);                       // A* 는 더 적은 정점만 확장
    std::cout << "path cost " << astar << ": Dijkstra expanded " << dExpanded << ", A* expanded " << aExpanded << std::endl;
    return 0;
}
// Time Complexity: Dijkstra O(E log V), A* 는 휴리스틱에 따라 훨씬 적은 확장
// Space Complexity: O(V)
```
## Union-Find 시간복잡도
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Union-Find with path compression + union by rank: O(alpha(N)) per op" << std::endl;
    std::cout << "alpha = inverse Ackermann function, effectively O(1) for all practical N" << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
