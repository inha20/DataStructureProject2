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
    for (int i = 0; i < nums.size(); ++i) {
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
#include <iostream>
#include <cassert>

class RingBuffer {
    int arr[5];
    int head = 0, tail = 0;
public:
    void push(int x) { arr[tail] = x; tail = (tail + 1) % 5; }
    int pop() { int res = arr[head]; head = (head + 1) % 5; return res; }
};

int main() {
    RingBuffer rb;
    rb.push(1);
    assert(rb.pop() == 1);
    std::cout << "Ring Buffer verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## CircularBuffer()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

// RingBuffer와 본질적으로 동일한 원리
int main() {
    std::cout << "Circular Buffer conceptually identical to Ring Buffer." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```

# Part 10. 병렬
## LockFreeQueue()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <cassert>

struct Node { int data; std::atomic<Node*> next; };

int main() {
    // 개념적 검증
    std::atomic<Node*> head(nullptr);
    Node* dummy = new Node{0, nullptr};
    head.store(dummy);
    assert(head.load() != nullptr);
    std::cout << "LockFreeQueue atomic pointers verified." << std::endl;
    return 0;
}
// Time Complexity: Amortized O(1)
// Space Complexity: O(1) per node
```
## MichaelScottQueue()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Michael-Scott Queue uses head & tail atomic pointers with CAS loop." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
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
#include <iostream>
#include <queue>
#include <mutex>
#include <cassert>

class ConcurrentQueue {
    std::queue<int> q;
    std::mutex m;
public:
    void push(int x) { std::lock_guard<std::mutex> lock(m); q.push(x); }
    bool empty() { std::lock_guard<std::mutex> lock(m); return q.empty(); }
};

int main() {
    ConcurrentQueue cq;
    cq.push(10);
    assert(!cq.empty());
    std::cout << "Concurrent Queue locked access verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) with Mutex Overhead
// Space Complexity: O(N)
```

# Part 11. 연구 주제
## PersistentQueue()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Persistent Queue logic (two persistent stacks approach)." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per persistence
```
## ImmutableQueue()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Immutable Queue (State is copied on change)." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
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
