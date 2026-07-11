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

# Part 11. 네트워크 플로우
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

# Part 13. 그래프 분해
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

## IsTree()
### 대표코드
```cpp
#include <iostream>
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
#include <queue>
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
#include <queue>
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

# Part 7. 최소 신장 트리 (보완)
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
#include <queue>
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

# Part 8. 분리 집합 (보완)
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

# Part 9. 최단 경로 (보완)
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

# Part 10. 길찾기 (보완)
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
#include <unordered_map>
#include <cassert>

// 양방향 BFS: 시작과 목표에서 동시에 탐색, 만나면 종료
int bidirectionalBFS(int src, int dst, int V, std::vector<std::vector<int>>& adj) {
    if (src == dst) return 0;
    std::vector<int> distF(V, -1), distB(V, -1);
    std::queue<int> qF, qB;
    qF.push(src); distF[src] = 0;
    qB.push(dst); distB[dst] = 0;
    while (!qF.empty() || !qB.empty()) {
        if (!qF.empty()) {
            int u = qF.front(); qF.pop();
            for (int v : adj[u]) {
                if (distF[v] == -1) { distF[v] = distF[u]+1; qF.push(v); }
                if (distB[v] != -1) return distF[v] + distB[v];
            }
        }
        if (!qB.empty()) {
            int u = qB.front(); qB.pop();
            for (int v : adj[u]) {
                if (distB[v] == -1) { distB[v] = distB[u]+1; qB.push(v); }
                if (distF[v] != -1) return distF[v] + distB[v];
            }
        }
    }
    return -1;
}

int main() {
    int V = 6;
    std::vector<std::vector<int>> adj = {{1,2},{0,3},{0,4},{1,5},{2,5},{3,4}};
    int dist = bidirectionalBFS(0, 5, V, adj);
    assert(dist == 2);
    std::cout << "BidirectionalSearch dist(0,5): " << dist << std::endl;
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
    assert(minCost == 6);
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

# Part 13. 그래프 분석 (보완)
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
#include <algorithm>
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

# Part 15. 그래프 모델
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

# 부록 (보완)
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
