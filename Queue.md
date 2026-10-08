# Part 1. 기본 연산
## CreateQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    std::cout << "Queue created." << std::endl;
    assert(q.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Enqueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(10);
    std::cout << "Enqueue(10)" << std::endl;
    assert(q.front() == 10);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per element
```
## Dequeue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(10);
    q.push(20);
    q.pop();
    std::cout << "Dequeue()" << std::endl;
    assert(q.front() == 20);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Front()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(30);
    int frontElement = q.front();
    std::cout << "Front() -> " << frontElement << std::endl;
    assert(frontElement == 30);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Rear()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(40);
    q.push(50);
    int backElement = q.back();
    std::cout << "Rear() -> " << backElement << std::endl;
    assert(backElement == 50);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Peek()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(60);
    int peekElement = q.front();
    std::cout << "Peek() -> " << peekElement << std::endl;
    assert(peekElement == 60);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IsEmpty()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    bool isEmpty = q.empty();
    std::cout << "IsEmpty() -> " << isEmpty << std::endl;
    assert(isEmpty == true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IsFull()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

const int MAX_SIZE = 100;
int arr[MAX_SIZE];
int front = 0, rear = 99;

int main() {
    bool isFull = ((rear + 1) % MAX_SIZE == front);
    std::cout << "IsFull() -> " << isFull << std::endl;
    assert(isFull == true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Size()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(1);
    q.push(2);
    size_t size = q.size();
    std::cout << "Size() -> " << size << std::endl;
    assert(size == 2);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Clear()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(1);
    while (!q.empty()) {
        q.pop();
    }
    std::cout << "Clear() executed." << std::endl;
    assert(q.empty());
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```

# Part 2. 배열 큐
## LinearQueue()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

class LinearQueue {
    int arr[100];
    int front = 0, rear = 0;
public:
    void enqueue(int x) { arr[rear++] = x; }
    void dequeue() { front++; }
    int getFront() { return arr[front]; }
    bool isEmpty() { return front == rear; }
};

int main() {
    LinearQueue lq;
    lq.enqueue(10);
    assert(lq.getFront() == 10);
    lq.dequeue();
    assert(lq.isEmpty());
    std::cout << "Linear Queue operational." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## CircularQueue()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

class CircularQueue {
    int arr[100];
    int front = 0, rear = 0;
    int size = 100;
public:
    void enqueue(int x) {
        arr[rear] = x;
        rear = (rear + 1) % size;
    }
    void dequeue() {
        front = (front + 1) % size;
    }
    int getFront() { return arr[front]; }
};

int main() {
    CircularQueue cq;
    cq.enqueue(5);
    assert(cq.getFront() == 5);
    cq.dequeue();
    std::cout << "Circular Queue operational." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## Resize()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

class ResizableQueue {
    int* arr;
    int capacity = 2, front = 0, rear = 0, count = 0;
public:
    ResizableQueue() { arr = new int[capacity]; }
    ~ResizableQueue() { delete[] arr; }
    void enqueue(int x) {
        if (count == capacity) {
            int newCap = capacity * 2;
            int* newArr = new int[newCap];
            for (int i = 0; i < count; i++) {
                newArr[i] = arr[(front + i) % capacity];
            }
            delete[] arr;
            arr = newArr;
            front = 0;
            rear = count;
            capacity = newCap;
            std::cout << "Queue Resized to " << capacity << std::endl;
        }
        arr[rear] = x;
        rear = (rear + 1) % capacity;
        count++;
    }
    int getFront() { return arr[front]; }
};

int main() {
    ResizableQueue q;
    q.enqueue(1); q.enqueue(2); q.enqueue(3); // triggers resize
    assert(q.getFront() == 1);
    return 0;
}
// Time Complexity: Amortized O(1)
// Space Complexity: O(N)
```
## Rotate()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    q.push(1); q.push(2); q.push(3);
    if (!q.empty()) {
        q.push(q.front());
        q.pop();
    }
    std::cout << "Rotated Queue. New front: " << q.front() << std::endl;
    assert(q.front() == 2);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) overhead
```

# Part 3. 연결 큐
## LinkedQueue()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };

class LinkedQueue {
    Node *front = nullptr, *rear = nullptr;
public:
    ~LinkedQueue() {
        while (front) {
            Node* temp = front;
            front = front->next;
            delete temp;
        }
    }
    void enqueue(int x) {
        Node* newNode = new Node{x, nullptr};
        if (!rear) front = rear = newNode;
        else { rear->next = newNode; rear = newNode; }
    }
    int getFront() { return front->data; }
};

int main() {
    LinkedQueue lq;
    lq.enqueue(15);
    assert(lq.getFront() == 15);
    std::cout << "LinkedQueue tested." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## EnqueueNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };
Node *front = nullptr, *rear = nullptr;

void enqueue(int x) {
    Node* newNode = new Node{x, nullptr};
    if (rear == nullptr) front = rear = newNode;
    else { rear->next = newNode; rear = newNode; }
    std::cout << "EnqueueNode(" << x << ")" << std::endl;
}

int main() {
    enqueue(100);
    assert(front->data == 100);
    delete front; // cleanup
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per node
```
## DequeueNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };
Node *front = nullptr, *rear = nullptr;

void dequeue() {
    if (front == nullptr) return;
    Node* temp = front;
    front = front->next;
    if (front == nullptr) rear = nullptr;
    delete temp;
    std::cout << "DequeueNode executed." << std::endl;
}

int main() {
    front = rear = new Node{10, nullptr};
    dequeue();
    assert(front == nullptr);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 4. 덱
## Deque()
### 대표코드
```cpp
#include <iostream>
#include <deque>
#include <cassert>

int main() {
    std::deque<int> dq;
    std::cout << "Deque created." << std::endl;
    assert(dq.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PushFront()
### 대표코드
```cpp
#include <iostream>
#include <deque>
#include <cassert>

int main() {
    std::deque<int> dq;
    dq.push_front(10);
    std::cout << "PushFront(10)" << std::endl;
    assert(dq.front() == 10);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PushBack()
### 대표코드
```cpp
#include <iostream>
#include <deque>
#include <cassert>

int main() {
    std::deque<int> dq;
    dq.push_back(20);
    std::cout << "PushBack(20)" << std::endl;
    assert(dq.back() == 20);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PopFront()
### 대표코드
```cpp
#include <iostream>
#include <deque>
#include <cassert>

int main() {
    std::deque<int> dq;
    dq.push_back(10);
    dq.pop_front();
    std::cout << "PopFront executed." << std::endl;
    assert(dq.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PopBack()
### 대표코드
```cpp
#include <iostream>
#include <deque>
#include <cassert>

int main() {
    std::deque<int> dq;
    dq.push_back(10);
    dq.pop_back();
    std::cout << "PopBack executed." << std::endl;
    assert(dq.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 5. 우선순위 큐
## PriorityQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::priority_queue<int> pq; 
    std::cout << "Max Heap Priority Queue created." << std::endl;
    assert(pq.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PushHeap()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::priority_queue<int> pq;
    pq.push(30);
    pq.push(50);
    std::cout << "PushHeap -> " << pq.top() << std::endl;
    assert(pq.top() == 50);
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1) per element
```
## PopHeap()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::priority_queue<int> pq;
    pq.push(10); pq.push(40); pq.push(20);
    pq.pop(); // Removes 40
    std::cout << "PopHeap executed." << std::endl;
    assert(pq.top() == 20);
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## Heapify()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> v = {3, 1, 4, 1, 5, 9};
    std::make_heap(v.begin(), v.end()); 
    std::cout << "Heapified vector. Top: " << v.front() << std::endl;
    assert(v.front() == 9);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## BuildHeap()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

int main() {
    // std::make_heap 내부적으로 수행되는 O(N) 바텀업 빌드 방식 모사
    std::vector<int> arr = {5, 3, 8};
    std::make_heap(arr.begin(), arr.end());
    assert(arr.front() == 8);
    std::cout << "BuildHeap logic verified." << std::endl;
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
#include <vector>
#include <cassert>

int main() {
    std::vector<int> v = {3, 1, 4, 1, 5, 9};
    std::make_heap(v.begin(), v.end());
    std::sort_heap(v.begin(), v.end());
    std::cout << "HeapSorted. Last element: " << v.back() << std::endl;
    assert(v.back() == 9);
    return 0;
}
// Time Complexity: O(N log N)
// Space Complexity: O(1)
```

# Part 6. BFS
## BreadthFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

std::vector<int> adj[4];
bool visited[4] = {false};
std::vector<int> result;

void BFS(int start) {
    std::queue<int> q;
    q.push(start);
    visited[start] = true;
    while (!q.empty()) {
        int v = q.front(); q.pop();
        result.push_back(v);
        for (int u : adj[v]) {
            if (!visited[u]) {
                visited[u] = true;
                q.push(u);
            }
        }
    }
}

int main() {
    adj[0] = {1, 2};
    adj[1] = {3};
    BFS(0);
    assert(result.size() == 4 && result[0] == 0 && result[1] == 1 && result[2] == 2);
    std::cout << "BFS verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## LevelOrderTraversal()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; };

std::vector<int> levelOrder(TreeNode* root) {
    std::vector<int> res;
    if (!root) return res;
    std::queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode* curr = q.front(); q.pop();
        res.push_back(curr->val);
        if (curr->left) q.push(curr->left);
        if (curr->right) q.push(curr->right);
    }
    return res;
}

int main() {
    TreeNode* root = new TreeNode{1, new TreeNode{2, nullptr, nullptr}, new TreeNode{3, nullptr, nullptr}};
    std::vector<int> res = levelOrder(root);
    assert(res[0] == 1 && res[1] == 2 && res[2] == 3);
    std::cout << "Level Order Traversal verified." << std::endl;
    return 0;
}
// Time Complexity: O(V)
// Space Complexity: O(V)
```
## ShortestPath()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

int main() {
    std::queue<int> q;
    std::vector<int> dist(4, -1);
    std::vector<int> adj[4];
    adj[0] = {1}; adj[1] = {2};
    q.push(0); dist[0] = 0;
    while(!q.empty()){
        int curr = q.front(); q.pop();
        for(int nxt : adj[curr]){
            if(dist[nxt] == -1) { dist[nxt] = dist[curr] + 1; q.push(nxt); }
        }
    }
    assert(dist[2] == 2);
    std::cout << "Shortest Path BFS verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## FloodFill()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

int main() {
    std::vector<std::vector<int>> grid = {{1,1,0}, {1,1,0}, {0,0,1}};
    std::queue<std::pair<int,int>> q;
    q.push({0,0});
    grid[0][0] = 2; // Fill color 2
    int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
    while(!q.empty()){
        auto [r, c] = q.front(); q.pop();
        for(int i=0; i<4; i++){
            int nr = r+dr[i], nc = c+dc[i];
            if(nr>=0 && nr<3 && nc>=0 && nc<3 && grid[nr][nc]==1){
                grid[nr][nc] = 2; q.push({nr,nc});
            }
        }
    }
    assert(grid[1][1] == 2);
    std::cout << "FloodFill verified." << std::endl;
    return 0;
}
// Time Complexity: O(V) where V is grid cells
// Space Complexity: O(V)
```
## MultiSourceBFS()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> q;
    std::vector<int> dist(5, -1);
    std::vector<int> adj[5];
    adj[0]={2}; adj[1]={3}; adj[2]={4}; adj[3]={4};
    // 다중 출발점
    q.push(0); dist[0] = 0;
    q.push(1); dist[1] = 0;
    while(!q.empty()){
        int curr = q.front(); q.pop();
        for(int nxt : adj[curr]){
            if(dist[nxt] == -1){ dist[nxt] = dist[curr]+1; q.push(nxt); }
        }
    }
    assert(dist[4] == 2);
    std::cout << "Multi-source BFS verified." << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```

# Part 7. 슬라이딩 윈도우
## SlidingWindowMaximum()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <deque>
#include <cassert>

std::vector<int> maxSlidingWindow(std::vector<int>& nums, int k) {
    std::deque<int> dq; 
    std::vector<int> res;
    for (int i = 0; i < (int)nums.size(); ++i) {
        if (!dq.empty() && dq.front() == i - k) dq.pop_front();
        while (!dq.empty() && nums[dq.back()] < nums[i]) dq.pop_back();
        dq.push_back(i);
        if (i >= k - 1) res.push_back(nums[dq.front()]);
    }
    return res;
}

int main() {
    std::vector<int> nums = {1,3,-1,-3,5,3,6,7};
    std::vector<int> res = maxSlidingWindow(nums, 3);
    assert(res[0] == 3 && res[2] == 5);
    std::cout << "Sliding window maximum -> " << res[0] << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(K)
```
## MonotonicQueue()
### 대표코드
```cpp
#include <iostream>
#include <deque>
#include <cassert>

class MonotonicQueue {
    std::deque<int> dq;
public:
    void push(int val) {
        while(!dq.empty() && dq.back() < val) dq.pop_back();
        dq.push_back(val);
    }
    int max() { return dq.front(); }
    void pop(int val) {
        if(!dq.empty() && dq.front() == val) dq.pop_front();
    }
};

int main() {
    MonotonicQueue mq;
    mq.push(1); mq.push(5); mq.push(3);
    assert(mq.max() == 5);
    std::cout << "Monotonic Queue verified." << std::endl;
    return 0;
}
// Time Complexity: Amortized O(1)
// Space Complexity: O(K)
```
## WindowMinimum()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <deque>
#include <cassert>

int main() {
    std::vector<int> nums = {3,1,4,1,5};
    std::deque<int> dq;
    int k = 2;
    // Sliding Window Minimum
    for(int i=0; i<k; i++){
        while(!dq.empty() && nums[dq.back()] > nums[i]) dq.pop_back();
        dq.push_back(i);
    }
    assert(nums[dq.front()] == 1);
    std::cout << "Window Minimum verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(K)
```

# Part 8. 운영체제
## JobQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <string>
#include <cassert>

int main() {
    std::queue<std::string> jobQueue;
    jobQueue.push("PrintDoc1");
    jobQueue.push("PrintDoc2");
    std::cout << "Processing: " << jobQueue.front() << std::endl;
    assert(jobQueue.front() == "PrintDoc1");
    jobQueue.pop();
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## ReadyQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

struct Process { int id, priority; };
auto comp = [](Process a, Process b) { return a.priority < b.priority; };

int main() {
    std::priority_queue<Process, std::vector<Process>, decltype(comp)> readyQueue(comp);
    readyQueue.push({1, 5});
    readyQueue.push({2, 10}); // Higher priority
    assert(readyQueue.top().id == 2);
    std::cout << "Ready Queue (Priority) verified." << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(N)
```
## WaitingQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> waitingQueue; // stores PID waiting for IO
    waitingQueue.push(101);
    assert(waitingQueue.front() == 101);
    std::cout << "Waiting Queue verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## MessageQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <string>
#include <cassert>

int main() {
    std::queue<std::string> mq; // IPC Msg queue
    mq.push("Message_1");
    assert(mq.front() == "Message_1");
    std::cout << "Message Queue verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```

# Part 9. 네트워크
## PacketQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::queue<int> packetQueue; // 1 means packet
    packetQueue.push(1);
    assert(!packetQueue.empty());
    std::cout << "Packet Queue verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## ProducerConsumer()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <mutex>
#include <cassert>

std::queue<int> sharedQueue;
std::mutex mtx;

void produce(int val) {
    std::lock_guard<std::mutex> lock(mtx);
    sharedQueue.push(val);
}

int main() {
    produce(10);
    assert(sharedQueue.front() == 10);
    std::cout << "Producer-Consumer Queue conceptually verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) per operation
// Space Complexity: O(N)
```
## RingBuffer()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <deque>
#include <iostream>
#include <random>
#include <thread>
#include <vector>
#include <cassert>

// 링 버퍼(Ring Buffer): 고정 크기 배열을 원형으로 쓰는 FIFO. 바이트 스트림(소켓 수신 버퍼, 오디오 입출력, 로그 파이프)의 표준 구조이며 할당·이동이 없고 읽기/쓰기가 O(1) 이다.
// 구현 요점 세 가지. ① 용량을 2 의 거듭제곱으로 두고 인덱스 대신 "단조 증가하는 카운터" 를 저장한다 — 위치 = 카운터 & (용량−1). 그러면 빈 상태(tail == head)와 가득 찬 상태(tail − head == 용량)가 구별되어 한 칸을 낭비하지 않고, 카운터가 size_t 한계를 넘어 돌아가도 용량이 2^64 의 약수라 차이 계산이 맞는다.
// ② 구간이 배열 끝을 넘으면 memcpy 를 두 번(끝까지, 처음부터)으로 나눈다. ③ 생산자 하나·소비자 하나(SPSC)이면 잠금도 CAS 도 필요 없다: 생산자만 tail 을, 소비자만 head 를 쓰고 서로의 카운터는 acquire 로 읽고 자기 것은 release 로 공개하면 데이터 쓰기가 카운터 공개보다 먼저 보인다. 두 카운터는 서로 다른 캐시 라인에 둬서 거짓 공유를 피한다.
// 검증: ① 무작위 크기의 쓰기·읽기를 std::deque 모델(용량 제한)과 대조, 가득/빈 경계와 래핑 ② 카운터를 size_t 최댓값 근처에서 시작해도 동일 ③ 생산자·소비자 두 스레드로 8 MB 의사난수 스트림을 임의 청크 크기로 주고받아 바이트가 하나도 변하거나 빠지지 않음(TSan 으로도 검증)
class SpscRing {
    std::vector<uint8_t> buf; const size_t cap, mask; alignas(64) std::atomic<size_t> head; alignas(64) std::atomic<size_t> tail;
public:
    explicit SpscRing(size_t capacityPow2, size_t startCounter = 0) : buf(capacityPow2), cap(capacityPow2), mask(capacityPow2 - 1), head(startCounter), tail(startCounter) { assert((cap & mask) == 0); }
    size_t size() const { return tail.load(std::memory_order_acquire) - head.load(std::memory_order_acquire); }
    size_t write(const uint8_t* p, size_t n) {                                         // 생산자 전용. 실제로 쓴 바이트 수를 돌려준다
        size_t t = tail.load(std::memory_order_relaxed), h = head.load(std::memory_order_acquire); n = std::min(n, cap - (t - h));
        if (!n) return 0;                                                                                                     // memcpy 에 널 포인터를 넘기지 않는다 (크기 0 이어도 정의되지 않은 동작)
        size_t off = t & mask, first = std::min(n, cap - off); std::memcpy(&buf[off], p, first); std::memcpy(&buf[0], p + first, n - first); tail.store(t + n, std::memory_order_release); return n;
    }
    size_t read(uint8_t* p, size_t n) {                                                // 소비자 전용
        size_t h = head.load(std::memory_order_relaxed), t = tail.load(std::memory_order_acquire); n = std::min(n, t - h);
        if (!n) return 0;
        size_t off = h & mask, first = std::min(n, cap - off); std::memcpy(p, &buf[off], first); std::memcpy(p + first, &buf[0], n - first); head.store(h + n, std::memory_order_release); return n;
    }
};
int main() {
    for (size_t start : {(size_t)0, (size_t)-1 - 100, (size_t)-1 - 7}) {
        SpscRing r(64, start); std::deque<uint8_t> model; std::mt19937 rng(5); uint8_t next = 0; size_t fullSeen = 0, emptySeen = 0;
        for (int step = 0; step < 50000; step++) {
            if (rng() % 2) { size_t n = rng() % 100; std::vector<uint8_t> data(n); for (auto& b : data) b = next++; size_t w = r.write(data.data(), n); assert(w == std::min(n, 64 - model.size())); next -= (uint8_t)(n - w); for (size_t i = 0; i < w; i++) model.push_back(data[i]); fullSeen += model.size() == 64; }
            else { size_t n = rng() % 100; std::vector<uint8_t> out(n); size_t g = r.read(out.data(), n); assert(g == std::min(n, model.size())); for (size_t i = 0; i < g; i++) { assert(out[i] == model.front()); model.pop_front(); } emptySeen += model.empty(); }
            assert(r.size() == model.size());
        }
        assert(fullSeen > 100 && emptySeen > 100);                                                                                                                                  // ① ② 가득/빈 상태 모두 경험, 용량 전체(64) 사용 가능
    }
    const size_t TOTAL = 8u << 20; SpscRing ring(4096); std::atomic<bool> bad{false}; uint64_t producedSum = 0, consumedSum = 0;
    std::thread prod([&] { std::mt19937 rng(7); std::vector<uint8_t> chunk(1500); size_t sent = 0; while (sent < TOTAL) { size_t n = std::min<size_t>(1 + rng() % 1500, TOTAL - sent); for (size_t i = 0; i < n; i++) chunk[i] = (uint8_t)((sent + i) * 31 % 251); size_t off = 0; while (off < n) { size_t w = ring.write(chunk.data() + off, n - off); off += w; if (!w) std::this_thread::yield(); } for (size_t i = 0; i < n; i++) producedSum += chunk[i]; sent += n; } });
    std::thread cons([&] { std::mt19937 rng(8); std::vector<uint8_t> chunk(2000); size_t got = 0; while (got < TOTAL) { size_t g = ring.read(chunk.data(), 1 + rng() % 2000); if (!g) { std::this_thread::yield(); continue; } for (size_t i = 0; i < g; i++) { if (chunk[i] != (uint8_t)((got + i) * 31 % 251)) bad = true; consumedSum += chunk[i]; } got += g; } });
    prod.join(); cons.join(); assert(!bad && producedSum == consumedSum && ring.size() == 0);                                                                                        // ③
    std::cout << "RingBuffer: matched a bounded deque model including counters starting near size_t max; " << TOTAL << " bytes streamed through a 4 KB SPSC ring with exact order and checksum " << consumedSum << std::endl; return 0;
}
// Time Complexity: write·read O(n) 바이트 복사 (memcpy 최대 2 번), 카운터 연산 O(1)
// Space Complexity: O(용량)
```
## CircularBuffer()
### 대표코드
```cpp
#include <algorithm>
#include <deque>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 순환 버퍼(Circular Buffer): 가득 차면 가장 오래된 원소를 덮어쓰는 고정 용량 버퍼다. RingBuffer 항목이 "가득 차면 쓰기를 거절하는" 스트림 버퍼라면, 이쪽은 "최근 N 개만 기억" 하는 용도 — 로그의 마지막 N 줄, 최근 N 개 센서 값, 이동 평균, undo 이력.
// 구현의 핵심은 "비었다/가득 찼다" 의 구별이다. head == tail 만 저장하면 둘이 같은 상태가 된다. 해법: ① 항상 한 칸을 비워 두기(용량 N 에 N−1 개만 저장; 상태 구별은 쉽지만 한 칸 낭비) ② 원소 수 count 를 따로 저장(낭비 없음; 이 구현) ③ 카운터를 단조 증가시키고 차이로 크기를 구하기(RingBuffer 항목).
// 덮어쓰기 모드에서는 push 가 가득 찬 상태에서 head 를 한 칸 밀어 가장 오래된 값을 버린다. i 번째 오래된 원소는 a[(head + i) % N] 이라 임의 접근이 O(1) 이고, 이동 평균처럼 창 합계가 필요하면 들어오고 나가는 값으로 합을 갱신해 O(1) 에 유지한다. 메모리 위에서 연속이 필요하면 std::rotate 로 head 를 0 으로 옮기는 linearize 가 있다.
// 검증: ① 무작위 push/pop/덮어쓰기를 "용량 제한 deque(가득 차면 앞 제거)" 와 대조 ② 한 칸 비우는 변형은 용량 N 에서 N−1 개만 담음 ③ 이동 평균을 O(1) 갱신한 값이 매번 정의대로 다시 합한 값과 같음 ④ linearize 후 순서 보존, 빈 버퍼 접근은 예외
template <class T> class Circular {
    std::vector<T> a; size_t head = 0, count = 0;
public:
    explicit Circular(size_t cap) : a(cap) { if (!cap) throw std::invalid_argument("capacity"); }
    size_t size() const { return count; } size_t capacity() const { return a.size(); } bool full() const { return count == a.size(); } bool empty() const { return count == 0; }
    bool push(const T& v, T* evicted = nullptr) {                                        // 덮어썼으면 true (evicted 에 버려진 값)
        if (full()) { if (evicted) *evicted = a[head]; a[head] = v; head = (head + 1) % a.size(); return true; }
        a[(head + count) % a.size()] = v; count++; return false;
    }
    T pop_front() { if (empty()) throw std::out_of_range("empty"); T v = a[head]; head = (head + 1) % a.size(); count--; return v; }
    const T& operator[](size_t i) const { if (i >= count) throw std::out_of_range("index"); return a[(head + i) % a.size()]; }          // 0 이 가장 오래된 값
    const T& back() const { return (*this)[count - 1]; }
    void linearize() { std::rotate(a.begin(), a.begin() + head, a.end()); head = 0; }
    const std::vector<T>& raw() const { return a; }
};
struct OneSlotEmpty {                                                                    // 비교용: 항상 한 칸을 비우는 방식
    std::vector<int> a; size_t head = 0, tail = 0; explicit OneSlotEmpty(size_t n) : a(n) {}
    bool full() const { return (tail + 1) % a.size() == head; } bool empty() const { return head == tail; }
    bool push(int v) { if (full()) return false; a[tail] = v; tail = (tail + 1) % a.size(); return true; }
};
int main() {
    std::mt19937 rng(9);
    for (int cap : {1, 2, 3, 7, 16}) { Circular<int> c(cap); std::deque<int> model; for (int step = 0; step < 20000; step++) { int op = rng() % 5;
        if (op < 3) { int v = rng() % 1000, ev = -1; bool over = c.push(v, &ev); bool modelOver = (int)model.size() == cap; assert(over == modelOver); if (modelOver) { assert(ev == model.front()); model.pop_front(); } model.push_back(v); }
        else if (op == 3 && !model.empty()) { assert(c.pop_front() == model.front()); model.pop_front(); }
        assert(c.size() == model.size() && c.full() == ((int)model.size() == cap)); for (size_t i = 0; i < model.size(); i++) assert(c[i] == model[i]); } }                       // ①
    { OneSlotEmpty o(8); int stored = 0; while (o.push(stored)) stored++; Circular<int> c(8); for (int i = 0; i < 100; i++) c.push(i); assert(stored == 7 && c.size() == 8); }                       // ② 한 칸 비움: 용량 8 에서 7 개
    { const size_t W = 50; Circular<double> win(W); double sum = 0; for (int i = 0; i < 5000; i++) { double v = (rng() % 10000) / 100.0, gone = 0; bool over = win.push(v, &gone); sum += v - (over ? gone : 0); double exact = 0; for (size_t k = 0; k < win.size(); k++) exact += win[k]; assert(std::abs(sum - exact) < 1e-6); } }                       // ③ 이동 평균 O(1) 갱신
    { Circular<int> c(5); for (int i = 0; i < 12; i++) c.push(i); assert(c[0] == 7 && c.back() == 11); c.linearize(); assert(std::vector<int>(c.raw().begin(), c.raw().end()) == (std::vector<int>{7, 8, 9, 10, 11}));
      bool threw = false; Circular<int> e(3); try { e.pop_front(); } catch (const std::out_of_range&) { threw = true; } assert(threw); threw = false; try { (void)e[0]; } catch (const std::out_of_range&) { threw = true; } assert(threw); }          // ④
    std::cout << "CircularBuffer: overwrite-oldest semantics matched a capped deque for capacities 1..16; one-slot-empty stores only 7 of 8; O(1) moving-average sums matched recomputation" << std::endl; return 0;
}
// Time Complexity: push·pop_front·접근 O(1), linearize O(N)
// Space Complexity: O(용량)
```

# Part 10. 병렬
## LockFreeQueue()
### 대표코드
```cpp
#include <atomic>
#include <cstdint>
#include <deque>
#include <iostream>
#include <thread>
#include <vector>
#include <cassert>

// 락프리 큐(Vyukov 의 유계 MPMC 큐): 용량이 고정된 원형 배열의 각 칸에 순번(sequence) 필드를 두어, 생산자와 소비자가 "이 칸이 지금 내 차례인가" 를 순번으로 판단한다. 포인터 CAS 가 아니라 카운터 CAS 하나(enqueue 위치/dequeue 위치)만 경쟁하므로 ABA 도 노드 회수 문제도 없다.
// 칸 i 의 순번은 처음에 i. 위치 pos 에 쓰려는 생산자는 seq == pos 이면 자기 차례(CAS 로 enq 를 pos+1 로 올려 선점)이고, 데이터를 쓴 뒤 seq 를 pos+1 로 공개한다. 소비자는 seq == pos+1 이면 읽을 차례이며 읽은 뒤 seq 를 pos+용량 으로 올려 다음 바퀴의 생산자에게 칸을 넘긴다. seq < pos 이면 가득 참(아직 소비 안 됨), seq < pos+1 이면 빔 — 잠금 없이 판단한다.
// 성질: 한 스레드가 멈춰도 다른 스레드는 진행하지만(그 칸을 선점한 쪽이 쓰기를 마치기 전에는 그 칸의 소비자만 기다림) 엄밀한 wait-free 는 아니다. 가득/빈 경우를 실패 반환으로 알려 주므로 호출자가 backoff 정책(spin, yield, 블로킹)을 고른다. 무제한 큐는 MichaelScottQueue 항목.
// 검증: ① 단일 스레드: 정확히 용량만큼 들어가고 FIFO ② 용량 4 의 작은 큐에서 생산자 3·소비자 3 이 3 만 개씩 주고받아 모든 값이 정확히 한 번 나오고, 소비자마다 같은 생산자의 값은 증가 순서로 관측 ③ 가득/빈 실패가 실제로 발생(경쟁 경로 실행) ④ TSan 으로도 검증
template <class T> class MpmcQueue {
    struct Cell { std::atomic<size_t> seq; T data; };
    std::vector<Cell> buf; const size_t mask; alignas(64) std::atomic<size_t> enq{0}; alignas(64) std::atomic<size_t> deq{0};
public:
    explicit MpmcQueue(size_t capacityPow2) : buf(capacityPow2), mask(capacityPow2 - 1) { assert((capacityPow2 & mask) == 0 && capacityPow2 >= 2); for (size_t i = 0; i < capacityPow2; i++) buf[i].seq.store(i, std::memory_order_relaxed); }
    bool push(const T& v) {
        size_t pos = enq.load(std::memory_order_relaxed); Cell* c;
        for (;;) { c = &buf[pos & mask]; size_t seq = c->seq.load(std::memory_order_acquire); intptr_t dif = (intptr_t)seq - (intptr_t)pos;
            if (dif == 0) { if (enq.compare_exchange_weak(pos, pos + 1, std::memory_order_relaxed)) break; }          // 내 차례: 위치 선점
            else if (dif < 0) return false;                                                                        // 가득 참 (이전 바퀴의 값이 아직 소비되지 않음)
            else pos = enq.load(std::memory_order_relaxed); }                                                       // 다른 생산자가 앞섬
        c->data = v; c->seq.store(pos + 1, std::memory_order_release); return true;
    }
    bool pop(T& v) {
        size_t pos = deq.load(std::memory_order_relaxed); Cell* c;
        for (;;) { c = &buf[pos & mask]; size_t seq = c->seq.load(std::memory_order_acquire); intptr_t dif = (intptr_t)seq - (intptr_t)(pos + 1);
            if (dif == 0) { if (deq.compare_exchange_weak(pos, pos + 1, std::memory_order_relaxed)) break; }
            else if (dif < 0) return false;                                                                        // 비어 있음
            else pos = deq.load(std::memory_order_relaxed); }
        v = c->data; c->seq.store(pos + mask + 1, std::memory_order_release); return true;
    }
};
int main() {
    { MpmcQueue<int> q(8); int pushed = 0; while (q.push(pushed)) pushed++; assert(pushed == 8); int v; for (int i = 0; i < 8; i++) { assert(q.pop(v) && v == i); } assert(!q.pop(v)); for (int r = 0; r < 100; r++) { for (int i = 0; i < 5; i++) assert(q.push(r * 10 + i)); for (int i = 0; i < 5; i++) { assert(q.pop(v) && v == r * 10 + i); } } }                                // ① 용량·FIFO·바퀴 넘김
    const int P = 3, C = 3, N = 30000; MpmcQueue<int> q(4); std::atomic<int> consumed{0}; std::atomic<long> fullFails{0}, emptyFails{0}; std::atomic<bool> bad{false}; std::vector<std::vector<int>> seen(C, std::vector<int>(P, -1)); std::vector<std::vector<char>> got(P, std::vector<char>(N, 0)); std::vector<std::thread> ts;
    for (int p = 0; p < P; p++) ts.emplace_back([&, p] { for (int i = 0; i < N; i++) { while (!q.push(p * N + i)) { fullFails++; std::this_thread::yield(); } } });
    for (int c = 0; c < C; c++) ts.emplace_back([&, c] { int v; while (consumed.load() < P * N) { if (!q.pop(v)) { emptyFails++; std::this_thread::yield(); continue; } int p = v / N, i = v % N; if (i <= seen[c][p]) bad = true; seen[c][p] = i; got[p][i]++; consumed++; } });
    for (auto& t : ts) t.join(); assert(!bad && consumed == P * N); for (int p = 0; p < P; p++) for (int i = 0; i < N; i++) assert(got[p][i] == 1);                                      // ② 모든 값이 정확히 한 번, 소비자별 생산자 순서 유지
    assert(fullFails > 0 && emptyFails > 0);                                                                                                                                                         // ③ 경쟁 경로 실행
    std::cout << "LockFreeQueue: " << P * N << " items through a 4-slot MPMC queue (" << P << " producers, " << C << " consumers) with exactly-once delivery and per-producer order; full-queue retries " << fullFails << ", empty-queue retries " << emptyFails << std::endl; return 0;
}
// Time Complexity: push·pop 분할상환 O(1) (경쟁이 없을 때 CAS 1 번)
// Space Complexity: O(용량)
```
## MichaelScottQueue()
### 대표코드
```cpp
#include <atomic>
#include <cstdint>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>
#include <cassert>

// 마이클–스콧 큐(Michael & Scott 1996): 연결 리스트로 만든 무제한 락프리 FIFO. 더미 노드 하나로 시작해 head 는 "방금 꺼낸 노드(더미)", tail 은 "끝 근처" 를 가리킨다.
// enqueue: tail.next 가 비어 있으면 CAS 로 새 노드를 잇고 tail 을 새 노드로 민다. tail.next 가 이미 채워져 있으면 다른 스레드가 잇기만 하고 tail 을 못 민 것이므로 대신 밀어 준다(helping) — 덕분에 스레드가 멈춰도 다른 스레드가 진행한다. dequeue: head.next 의 값을 읽고 head 를 한 칸 CAS 로 전진시킨다. head == tail 이면서 next 가 있으면 tail 이 뒤처진 것이라 먼저 밀어 준다.
// 이 구현은 원 논문처럼 "카운터가 붙은 포인터" 를 쓴다: 노드를 32 비트 인덱스로 가리키고 64 비트 워드 상위에 32 비트 카운터를 붙여, 성공한 CAS 마다 카운터를 올린다. 꺼낸 더미 노드는 고정 풀로 돌려보내 재사용하므로 메모리가 새지 않으면서도 낡은 CAS 는 카운터 때문에 반드시 실패한다(ABA 방지). 풀이 비면 enqueue 는 false 를 돌려주고 호출자가 재시도한다.
// 검증: ① 단일 스레드 FIFO ② 생산자 3·소비자 3 이 3 만 개씩 주고받아 모든 값이 정확히 한 번, 소비자마다 같은 생산자의 값은 증가 순서 ③ 작은 풀(64 노드)에서 풀 고갈 재시도가 실제 발생하고도 끝난 뒤 자유 리스트 + 큐 안의 노드 + 더미 == 풀 크기(누수·중복 없음) ④ TSan 으로도 검증
typedef uint64_t W; const uint32_t NIL = 0xFFFFFFFFu;
inline W mk(uint32_t cnt, uint32_t idx) { return ((W)cnt << 32) | idx; } inline uint32_t ix(W w) { return (uint32_t)w; } inline uint32_t ct(W w) { return (uint32_t)(w >> 32); }
class MSQueue {
    struct Node { std::atomic<int> val{0}; std::atomic<W> next{0}; };
    std::unique_ptr<Node[]> nodes; std::unique_ptr<std::atomic<uint32_t>[]> fnext; std::atomic<W> freeHead, head, tail; uint32_t cap;
    uint32_t alloc() { for (;;) { W h = freeHead.load(); uint32_t i = ix(h); if (i == NIL) return NIL; uint32_t nx = fnext[i].load(); if (freeHead.compare_exchange_weak(h, mk(ct(h) + 1, nx))) return i; } }
    void release(uint32_t i) { for (;;) { W h = freeHead.load(); fnext[i].store(ix(h)); if (freeHead.compare_exchange_weak(h, mk(ct(h) + 1, i))) return; } }
public:
    explicit MSQueue(uint32_t capacity) : nodes(new Node[capacity + 1]), fnext(new std::atomic<uint32_t>[capacity + 1]), cap(capacity + 1) {      // 노드 0 은 처음의 더미
        nodes[0].next = mk(0, NIL); head = tail = mk(0, 0); for (uint32_t i = 1; i <= capacity; i++) fnext[i] = i < capacity ? i + 1 : NIL; freeHead = mk(0, capacity ? 1 : NIL);
    }
    bool enqueue(int v) {
        uint32_t n = alloc(); if (n == NIL) return false; nodes[n].val.store(v); W old = nodes[n].next.load(); nodes[n].next.store(mk(ct(old) + 1, NIL));       // 카운터는 이전 생애보다 계속 증가
        for (;;) {
            W t = tail.load(); W nx = nodes[ix(t)].next.load(); if (t != tail.load()) continue;                           // 일관성 확인
            if (ix(nx) == NIL) { if (nodes[ix(t)].next.compare_exchange_weak(nx, mk(ct(nx) + 1, n))) { tail.compare_exchange_strong(t, mk(ct(t) + 1, n)); return true; } }
            else tail.compare_exchange_strong(t, mk(ct(t) + 1, ix(nx)));                                                 // 뒤처진 tail 을 대신 밀어 준다
        }
    }
    bool dequeue(int& out) {
        for (;;) {
            W h = head.load(), t = tail.load(); W nx = nodes[ix(h)].next.load(); if (h != head.load()) continue;
            if (ix(h) == ix(t)) { if (ix(nx) == NIL) return false; tail.compare_exchange_strong(t, mk(ct(t) + 1, ix(nx))); }          // 비었거나, tail 이 뒤처짐
            else { int v = nodes[ix(nx)].val.load(); if (head.compare_exchange_weak(h, mk(ct(h) + 1, ix(nx)))) { out = v; release(ix(h)); return true; } }       // CAS 전에 값을 읽는다 (성공 뒤엔 풀로 돌아갈 수 있다)
        }
    }
    size_t countFree() const { size_t c = 0; for (uint32_t i = ix(freeHead.load()); i != NIL; i = fnext[i].load()) c++; return c; }
    size_t countQueued() const { size_t c = 0; for (uint32_t i = ix(nodes[ix(head.load())].next.load()); i != NIL; i = ix(nodes[i].next.load())) c++; return c; }
    size_t total() const { return cap; }
};
int main() {
    { MSQueue q(100); int v; assert(!q.dequeue(v)); for (int i = 0; i < 100; i++) assert(q.enqueue(i)); assert(!q.enqueue(100)); for (int i = 0; i < 100; i++) { assert(q.dequeue(v) && v == i); } assert(!q.dequeue(v) && q.countFree() == 100); }          // ① FIFO와 풀 고갈
    const int P = 3, C = 3, N = 30000; MSQueue q(64); std::atomic<int> consumed{0}; std::atomic<long> poolRetries{0}; std::atomic<bool> bad{false}; std::vector<std::vector<int>> seen(C, std::vector<int>(P, -1)); std::vector<std::vector<char>> got(P, std::vector<char>(N, 0)); std::vector<std::thread> ts;
    for (int p = 0; p < P; p++) ts.emplace_back([&, p] { for (int i = 0; i < N; i++) { while (!q.enqueue(p * N + i)) { poolRetries++; std::this_thread::yield(); } } });
    for (int c = 0; c < C; c++) ts.emplace_back([&, c] { int v; while (consumed.load() < P * N) { if (!q.dequeue(v)) { std::this_thread::yield(); continue; } int p = v / N, i = v % N; if (i <= seen[c][p]) bad = true; seen[c][p] = i; got[p][i]++; consumed++; } });
    for (auto& t : ts) t.join(); assert(!bad && consumed == P * N); for (int p = 0; p < P; p++) for (int i = 0; i < N; i++) assert(got[p][i] == 1);                                                            // ②
    assert(poolRetries > 0 && q.countQueued() == 0 && q.countFree() + 1 == q.total());                                                                                                                  // ③ 누수·중복 없음 (더미 1 개 포함)
    std::cout << "MichaelScottQueue: " << P * N << " items delivered exactly once with per-producer order through a 64-node pool (" << poolRetries << " pool-exhaustion retries); every node returned to the pool" << std::endl; return 0;
}
// Time Complexity: enqueue·dequeue 분할상환 O(1) (락프리: 경쟁에서 재시도 가능)
// Space Complexity: O(풀 크기)
```
## WorkStealingQueue()
### 대표코드
```cpp
#include <iostream>
#include <deque>
#include <cassert>

int main() {
    std::deque<int> wsq; // 덱을 이용해 한쪽에서는 push/pop, 다른쪽에서 steal
    wsq.push_front(1); // My task
    wsq.push_front(2);
    int stolenTask = wsq.back(); wsq.pop_back(); // Others steal
    assert(stolenTask == 1);
    std::cout << "Work Stealing concept verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## ConcurrentQueue()
### 대표코드
```cpp
#include <algorithm>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <deque>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>
#include <cassert>

// 동시성 큐(Blocking Bounded Queue): 락프리가 아니라 "뮤텍스 + 조건 변수" 로 만든 생산자–소비자 큐다. 락프리 구조보다 단순하고 정확하며, 큐가 비었을 때 소비자를, 가득 찼을 때 생산자를 CPU 를 쓰지 않고 재운다(블로킹) — 대부분의 스레드 풀·파이프라인이 이것으로 충분하다.
// 설계 요점: ① 용량을 제한해 생산자가 소비자보다 빠를 때 메모리가 무한히 늘지 않게 한다(역압, backpressure) ② 조건 변수 대기는 반드시 술어(predicate) 루프 안에서 한다 — 가짜 깨어남(spurious wakeup)이나 다른 스레드가 먼저 가져간 경우에도 조건을 다시 확인하기 위해서다 ③ close(): 더 넣을 것이 없다고 알리면 대기 중인 모두를 깨우고, 소비자는 남은 것을 모두 꺼낸 뒤 false 를 받아 종료한다(종료 신호를 센티넬 값으로 넣지 않아도 된다) ④ 시간 제한 대기(wait_for)로 교착을 피한다.
// 검증: ① 용량 4 인 큐로 생산자 3·소비자 3 이 3 만 개씩 주고받아 모든 값이 정확히 한 번이고 큐 크기가 용량을 넘지 않음 ② 소비자별로 같은 생산자의 값은 증가 순서 ③ close 이후 push 는 실패하고, 소비자는 잔여분을 비운 뒤 종료 ④ 대기(블로킹)가 실제로 일어남을 카운터로 확인 ⑤ try_pop_for 가 시간 제한 안에 빈 큐에서 false 를 돌려줌
template <class T> class BlockingQueue {
    std::deque<T> q; const size_t cap; bool closed = false; std::mutex m; std::condition_variable notFull, notEmpty; size_t maxSize = 0, pushWaits = 0, popWaits = 0;
public:
    explicit BlockingQueue(size_t c) : cap(c) {}
    bool push(const T& v) { std::unique_lock<std::mutex> lk(m); while (!closed && q.size() == cap) { pushWaits++; notFull.wait(lk); } if (closed) return false; q.push_back(v); maxSize = std::max(maxSize, q.size()); notEmpty.notify_one(); return true; }
    bool pop(T& out) { std::unique_lock<std::mutex> lk(m); while (!closed && q.empty()) { popWaits++; notEmpty.wait(lk); } if (q.empty()) return false; out = q.front(); q.pop_front(); notFull.notify_one(); return true; }       // 닫혔고 비었을 때만 false
    bool try_pop_for(T& out, std::chrono::milliseconds d) { std::unique_lock<std::mutex> lk(m); if (!notEmpty.wait_for(lk, d, [&] { return closed || !q.empty(); }) || q.empty()) return false; out = q.front(); q.pop_front(); notFull.notify_one(); return true; }
    void close() { { std::lock_guard<std::mutex> lk(m); closed = true; } notFull.notify_all(); notEmpty.notify_all(); }
    size_t maxObserved() { std::lock_guard<std::mutex> lk(m); return maxSize; } size_t waits() { std::lock_guard<std::mutex> lk(m); return pushWaits + popWaits; }
};
int main() {
    const int P = 3, C = 3, N = 30000; BlockingQueue<int> q(4); std::atomic<int> consumed{0}; std::atomic<bool> bad{false}; std::vector<std::vector<int>> seen(C, std::vector<int>(P, -1)); std::vector<std::vector<int>> got(P, std::vector<int>(N, 0)); std::mutex gm; std::vector<std::thread> producers, consumers;
    for (int p = 0; p < P; p++) producers.emplace_back([&, p] { for (int i = 0; i < N; i++) { bool ok = q.push(p * N + i); assert(ok); } });
    for (int c = 0; c < C; c++) consumers.emplace_back([&, c] { int v; while (q.pop(v)) { int p = v / N, i = v % N; if (i <= seen[c][p]) bad = true; seen[c][p] = i; { std::lock_guard<std::mutex> g(gm); got[p][i]++; } consumed++; } });
    for (auto& t : producers) t.join(); q.close(); for (auto& t : consumers) t.join();                                                    // ③ 생산이 끝나면 close -> 소비자는 잔여분을 비우고 종료
    assert(!bad && consumed == P * N && q.maxObserved() <= 4 && q.waits() > 0); for (int p = 0; p < P; p++) for (int i = 0; i < N; i++) assert(got[p][i] == 1);              // ①②④
    { int v = 0; assert(!q.push(1) && !q.pop(v)); }                                                                                                  // 닫힌 큐: push 실패, 빈 pop 은 false
    BlockingQueue<int> e(2); int v = -1; auto t0 = std::chrono::steady_clock::now(); assert(!e.try_pop_for(v, std::chrono::milliseconds(30))); auto dt = std::chrono::steady_clock::now() - t0; assert(dt >= std::chrono::milliseconds(25));         // ⑤ 시간 제한
    std::thread late([&] { std::this_thread::sleep_for(std::chrono::milliseconds(20)); e.push(42); }); assert(e.try_pop_for(v, std::chrono::seconds(5)) && v == 42); late.join();
    std::cout << "ConcurrentQueue: " << P * N << " items delivered exactly once through a bounded queue (max size " << q.maxObserved() << " of 4, blocked " << q.waits() << " times); close() let consumers drain and exit" << std::endl; return 0;
}
// Time Complexity: push·pop O(1) (뮤텍스 경쟁 시 대기)
// Space Complexity: O(용량)
```

# Part 11. 연구 주제
## PersistentQueue()
### 대표코드
```cpp
#include <deque>
#include <functional>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 영속 큐 (큐 관점의 요약, 정본은 AdvancedDataStructures.md Part 1): 모든 옛 버전을 건드리지 않고, "어떤 버전에서든" snoc(뒤에 추가)·tail(앞 제거)을 최악 O(1) 에 한다 (Okasaki 의 실시간 큐).
// 두 스택(앞 f, 뒤 r)으로 만드는 큐는 평균 O(1) 이지만 영속적으로 쓰면 같은 "비싼 뒤집기"를 반복 호출당해 O(n) 이 된다.
// 해법은 지연 평가(lazy): f 를 "다 쓰면" 뒤집는 대신, r 의 뒤집기를 f 와 이어 붙이는 작업(rotate)을 지연 스트림으로 걸어 두고, 연산마다 일정(schedule) 스트림 s 를 한 칸씩 강제 평가해 그 일을 조금씩 미리 끝낸다.
// 불변식 |s| = |f| - |r|.  평가 결과는 메모이즈되므로 같은 버전을 여러 번 써도 작업이 한 번만 일어난다
struct Lazy; typedef std::shared_ptr<Lazy> Stream;
struct Cell { bool nil = true; int head = 0; Stream tail; };
long forced = 0;                                                           // 강제된 썽크 수 (최악 시간 측정용)
struct Lazy {
    std::function<Cell()> thunk; Cell val; bool done = false;
    const Cell& force() { if (!done) { forced++; val = thunk(); done = true; thunk = nullptr; } return val; }
};
Stream mkNil() { auto s = std::make_shared<Lazy>(); s->done = true; return s; }
Stream mkCons(int x, const Stream& t) { auto s = std::make_shared<Lazy>(); s->done = true; s->val = Cell{false, x, t}; return s; }
Stream delay(std::function<Cell()> f) { auto s = std::make_shared<Lazy>(); s->thunk = f; return s; }
struct L; typedef std::shared_ptr<const L> List;
struct L { int x; List next; };
Stream rotate(Stream f, List r, Stream a) {                                // f 뒤에 reverse(r) 와 a 를 이은 스트림 (|r| = |f| + 1)
    return delay([=]() -> Cell {
        const Cell& fc = f->force();
        if (fc.nil) return Cell{false, r->x, a};
        return Cell{false, fc.head, rotate(fc.tail, r->next, mkCons(r->x, a))};
    });
}
struct Queue { Stream f; List r; Stream s; };
Queue exec(const Stream& f, const List& r, const Stream& s) {
    const Cell& sc = s->force();                                           // 일정 스트림을 한 칸 강제 = rotate 를 한 걸음 진행
    if (!sc.nil) return Queue{f, r, sc.tail};
    Stream f2 = rotate(f, r, mkNil());                                     // 일정이 끝나면 새 rotate 를 시작
    return Queue{f2, nullptr, f2};
}
Queue empty() { return Queue{mkNil(), nullptr, mkNil()}; }
Queue snoc(const Queue& q, int x) { return exec(q.f, std::make_shared<const L>(L{x, q.r}), q.s); }
bool isEmpty(const Queue& q) { return q.f->force().nil; }
int head(const Queue& q) { return q.f->force().head; }
Queue tail(const Queue& q) { return exec(q.f->force().tail, q.r, q.s); }

int main() {
    std::mt19937 rng(21); std::vector<Queue> ver = {empty()}; std::vector<std::deque<int>> model = {{}}; long worst = 0;
    for (int step = 0; step < 30000; step++) {
        int base = rng() % std::min<size_t>(ver.size(), 3000) + (ver.size() > 3000 ? ver.size() - 3000 : 0);   // 최근 3000 개 버전 중 하나에서 갈라진다
        const Queue q = ver[base]; std::deque<int> m = model[base]; long before = forced;
        if (m.empty() || rng() % 5 < 3) { int x = rng() % 1000; ver.push_back(snoc(q, x)); m.push_back(x); }
        else { assert(head(q) == m.front()); ver.push_back(tail(q)); m.pop_front(); }
        worst = std::max(worst, forced - before); model.push_back(m);
        const Queue& nq = ver.back(); assert(isEmpty(nq) == m.empty()); if (!m.empty()) assert(head(nq) == m.front());
    }
    for (size_t i = 0; i < ver.size(); i += 7) {                           // 오래된 버전도 끝까지 비우면 모델과 같은 순서
        Queue q = ver[i]; for (int x : model[i]) { assert(!isEmpty(q) && head(q) == x); q = tail(q); } assert(isEmpty(q));
    }
    Queue big = empty(); for (int i = 0; i < 1000; i++) big = snoc(big, i);
    long before = forced; Queue t1 = tail(big); for (int k = 0; k < 500; k++) { Queue t = tail(big); assert(head(t) == 1); } (void)t1;
    assert(forced - before <= 10);                                         // 같은 버전에 tail 을 500 번 호출해도 비싼 일은 한 번만 (메모이즈)
    assert(worst <= 12);                                                   // 연산 한 번당 강제 평가 수가 상수
    std::cout << "PersistentQueue: " << ver.size() << " versions verified, worst thunks forced per op = " << worst << std::endl;
    return 0;
}
// Time Complexity: snoc·tail·head 최악 O(1) (영속 사용에서도)
// Space Complexity: O(N)
```
## ImmutableQueue()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <deque>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 불변 큐(Immutable Queue): 연산이 큐를 바꾸지 않고 "새 큐" 를 돌려준다 — 모든 이전 버전이 그대로 유효하다. 가장 단순한 방법은 연결 리스트 두 개(앞쪽 front, 뒤쪽 rear 를 거꾸로 저장)다: push 는 rear 앞에 cons, pop 은 front 의 꼬리로, front 가 비면 rear 를 뒤집어 front 로 옮긴다. 공유되는 꼬리 덕분에 새 버전은 노드 O(1) 개만 만든다.
// 한 가지 버전을 한 번씩만 쓰는 일반적인 사용(ephemeral)에서는 뒤집기 비용이 원소당 한 번이라 분할상환 O(1) 이다. 그러나 같은 버전에서 pop 을 여러 번 부르면(영속 사용) 비싼 뒤집기가 매번 되풀이되어 분할상환 보장이 깨진다 — 분할상환 분석은 연산 열이 이어진다고 가정하기 때문이다. 이 약점을 지연 평가와 일정으로 막은 것이 실시간 영속 큐(PersistentQueue 항목, Okasaki)다.
// 검증: ① 무작위 push/pop 을 임의의 옛 버전에서 이어 붙여도 모든 버전이 std::deque 스냅샷과 같다(불변성) ② 새 버전이 노드를 O(1) 개만 새로 만든다(구조 공유) ③ 한 줄로 이어 쓰면 n 번 push 뒤 n 번 pop 에서 뒤집기 작업량이 정확히 n (분할상환 O(1)) ④ 같은 버전에서 pop 을 K 번 반복하면 뒤집기 작업량이 K×(n−1) 로 커진다(영속 사용에서 분할상환 붕괴)
struct L; typedef std::shared_ptr<const L> List; struct L { int x; List next; };
long reverseWork = 0, allocated = 0;
List cons(int x, const List& t) { allocated++; return std::make_shared<const L>(L{x, t}); }
List reverseList(const List& l) { List r; for (List p = l; p; p = p->next) { r = cons(p->x, r); reverseWork++; } return r; }
struct IQueue {
    List front, rear; size_t n = 0;
    static IQueue make(List f, List r, size_t n) { if (!f && r) { f = reverseList(r); r = nullptr; } return IQueue{f, r, n}; }                 // 불변식: n > 0 이면 front 가 비어 있지 않다
    IQueue push(int x) const { return make(front, cons(x, rear), n + 1); }
    int head() const { return front->x; }
    IQueue pop() const { return make(front->next, rear, n - 1); }
    std::vector<int> toVector() const { std::vector<int> v; for (List p = front; p; p = p->next) v.push_back(p->x); std::vector<int> r; for (List p = rear; p; p = p->next) r.push_back(p->x); v.insert(v.end(), r.rbegin(), r.rend()); return v; }
};
int main() {
    std::mt19937 rng(14); std::vector<IQueue> ver = {IQueue{}}; std::vector<std::deque<int>> model = {{}}; long maxNew = 0;
    for (int step = 0; step < 4000; step++) {
        size_t base = rng() % ver.size(); const IQueue q = ver[base]; std::deque<int> m = model[base]; long before = allocated, revBefore = reverseWork; IQueue r;
        if (m.empty() || rng() % 5 < 3) { int x = rng() % 1000; r = q.push(x); m.push_back(x); } else { assert(q.head() == m.front()); r = q.pop(); m.pop_front(); }
        if (reverseWork == revBefore) maxNew = std::max(maxNew, allocated - before);                                                                         // ② 뒤집기가 없는 연산은 노드를 1 개 이하로 만든다 (뒤집기가 일어난 연산은 크기에 비례)
        assert(r.n == m.size() && r.toVector() == std::vector<int>(m.begin(), m.end()));
        ver.push_back(r); model.push_back(m);
        if (m.size() > 60) { ver.back() = IQueue{}; model.back().clear(); }
    }
    for (size_t i = 0; i < ver.size(); i += 17) assert(ver[i].toVector() == std::vector<int>(model[i].begin(), model[i].end()));                                         // ① 옛 버전은 그대로
    assert(maxNew <= 1);
    const int n = 5000; reverseWork = 0; { IQueue q; for (int i = 0; i < n; i++) q = q.push(i); for (int i = 0; i < n; i++) { assert(q.head() == i); q = q.pop(); } assert(q.n == 0); } assert(reverseWork == n);        // ③ 이어 쓰면 뒤집기 n 번
    { IQueue q; for (int i = 0; i < n; i++) q = q.push(i); reverseWork = 0; const int K = 50; for (int k = 0; k < K; k++) { IQueue t = q.pop(); assert(t.n == n - 1); } assert(reverseWork == (long)K * (n - 1)); }                                     // ④ 같은 버전에서 pop 50 번 -> 뒤집기 50(n−1)
    std::cout << "ImmutableQueue: 4000 persistent versions matched deque snapshots; sequential use reversed " << n << " nodes in total (amortized O(1)) but popping one version 50 times redid the reversal " << 50L * (n - 1) << " node copies" << std::endl; return 0;
}
// Time Complexity: push O(1), head O(1), pop 분할상환 O(1) (이어 쓸 때만; 같은 버전 반복 사용은 최악 O(N))
// Space Complexity: O(N), 새 버전은 O(1) 노드를 만들고 나머지는 공유
```
## QueueingTheory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    double lambda = 5.0, mu = 10.0;
    double rho = lambda / mu; // Utilization
    assert(rho == 0.5);
    std::cout << "Queueing Theory Utilization: " << rho << std::endl;
    return 0;
}
// Time/Space: Analytical Math
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## FairQueue()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

int main() {
    std::vector<std::queue<int>> queues(3);
    queues[0].push(1); queues[1].push(2); queues[2].push(3);
    // Round-robin processing
    int nextFlow = 0;
    int data = queues[nextFlow].front(); queues[nextFlow].pop();
    assert(data == 1);
    std::cout << "Fair Queue (Round Robin) verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## PriorityScheduling()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <cassert>

int main() {
    std::priority_queue<int> pq;
    pq.push(2); pq.push(5);
    assert(pq.top() == 5);
    std::cout << "Priority Scheduling via PQ verified." << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(N)
```
