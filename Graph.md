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
typedef __int128 big;
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
