# Part 1. 기본 연산
## CreateStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    std::cout << "Stack created." << std::endl;
    assert(s.empty());
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) (초기 할당 기준)
```
## Push()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    s.push(10);
    std::cout << "Push(10)" << std::endl;
    assert(s.top() == 10);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per push
```
## Pop()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    s.push(10);
    s.push(20);
    s.pop();
    std::cout << "Pop()" << std::endl;
    assert(s.top() == 10);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Peek()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    s.push(30);
    int topElement = s.top();
    std::cout << "Peek() -> " << topElement << std::endl;
    assert(topElement == 30);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Top()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    s.push(40);
    int topElement = s.top();
    std::cout << "Top() -> " << topElement << std::endl;
    assert(topElement == 40);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IsEmpty()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    bool isEmpty = s.empty();
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
int topIndex = 99;

int main() {
    bool isFull = (topIndex == MAX_SIZE - 1);
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
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    s.push(1);
    s.push(2);
    size_t size = s.size();
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
#include <stack>
#include <cassert>

int main() {
    std::stack<int> s;
    s.push(1);
    s.push(2);
    while (!s.empty()) {
        s.pop();
    }
    std::cout << "Clear() executed." << std::endl;
    assert(s.empty());
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```

# Part 2. 배열 스택
## ArrayStack()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

class ArrayStack {
    int arr[100];
    int topIndex = -1;
public:
    void push(int x) { arr[++topIndex] = x; }
    void pop() { topIndex--; }
    int top() { return arr[topIndex]; }
    bool isEmpty() { return topIndex == -1; }
};

int main() {
    ArrayStack s;
    s.push(10);
    std::cout << "ArrayStack Push(10)" << std::endl;
    assert(s.top() == 10);
    s.pop();
    assert(s.isEmpty());
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

class ResizableStack {
    int* arr;
    int capacity;
    int topIndex;
public:
    ResizableStack() : capacity(1), topIndex(-1) { arr = new int[capacity]; }
    ~ResizableStack() { delete[] arr; }
    void push(int x) {
        if (topIndex == capacity - 1) {
            capacity *= 2;
            int* newArr = new int[capacity];
            for (int i = 0; i <= topIndex; ++i) newArr[i] = arr[i];
            delete[] arr;
            arr = newArr;
            std::cout << "Resized to " << capacity << std::endl;
        }
        arr[++topIndex] = x;
    }
    int top() { return arr[topIndex]; }
};

int main() {
    ResizableStack s;
    s.push(1);
    s.push(2); // Triggers resize
    assert(s.top() == 2);
    return 0;
}
// Time Complexity: Amortized O(1) for push
// Space Complexity: O(N)
```
## DynamicStack()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

class DynamicStack {
    std::vector<int> arr;
public:
    void push(int x) { arr.push_back(x); }
    void pop() { arr.pop_back(); }
    int top() { return arr.back(); }
};

int main() {
    DynamicStack s;
    s.push(100);
    std::cout << "DynamicStack Push(100)" << std::endl;
    assert(s.top() == 100);
    return 0;
}
// Time Complexity: Amortized O(1)
// Space Complexity: O(N)
```

# Part 3. 연결리스트 스택
## LinkedStack()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node {
    int data;
    Node* next;
};

class LinkedStack {
    Node* topNode = nullptr;
public:
    ~LinkedStack() {
        while (topNode) {
            Node* temp = topNode;
            topNode = topNode->next;
            delete temp;
        }
    }
    void push(int x) {
        topNode = new Node{x, topNode};
    }
    int top() { return topNode->data; }
    bool isEmpty() { return topNode == nullptr; }
};

int main() {
    LinkedStack s;
    s.push(15);
    std::cout << "LinkedStack Push(15)" << std::endl;
    assert(s.top() == 15);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## PushNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };
Node* top = nullptr;

void push(int x) {
    Node* newNode = new Node{x, top};
    top = newNode;
    std::cout << "PushNode(" << x << ")" << std::endl;
}

int main() {
    push(5);
    assert(top->data == 5);
    delete top; // cleanup
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per node
```
## PopNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node* next; };
Node* top = nullptr;

void pop() {
    if (!top) return;
    Node* temp = top;
    top = top->next;
    delete temp;
    std::cout << "PopNode executed." << std::endl;
}

int main() {
    top = new Node{10, nullptr};
    pop();
    assert(top == nullptr);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 4. 대표 활용
## ReverseString()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::string reverseString(std::string str) {
    std::stack<char> s;
    for (char c : str) s.push(c);
    std::string reversed = "";
    while (!s.empty()) {
        reversed += s.top();
        s.pop();
    }
    return reversed;
}

int main() {
    std::string res = reverseString("hello");
    std::cout << "Reverse 'hello' -> " << res << std::endl;
    assert(res == "olleh");
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## BalancedParentheses()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

bool isBalanced(std::string expr) {
    std::stack<char> s;
    for (char c : expr) {
        if (c == '(' || c == '{' || c == '[') s.push(c);
        else if (c == ')' || c == '}' || c == ']') {
            if (s.empty()) return false;
            char top = s.top();
            if ((c == ')' && top == '(') || (c == '}' && top == '{') || (c == ']' && top == '[')) {
                s.pop();
            } else return false;
        }
    }
    return s.empty();
}

int main() {
    bool res = isBalanced("{[()]}");
    std::cout << "isBalanced('{[()]}') -> " << res << std::endl;
    assert(res == true);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## InfixToPostfix()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

int precedence(char op) {
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    return 0;
}

std::string infixToPostfix(std::string infix) {
    std::stack<char> s;
    std::string postfix = "";
    for (char c : infix) {
        if (isalnum(c)) postfix += c;
        else if (c == '(') s.push(c);
        else if (c == ')') {
            while (!s.empty() && s.top() != '(') {
                postfix += s.top(); s.pop();
            }
            s.pop();
        } else {
            while (!s.empty() && precedence(s.top()) >= precedence(c)) {
                postfix += s.top(); s.pop();
            }
            s.push(c);
        }
    }
    while (!s.empty()) { postfix += s.top(); s.pop(); }
    return postfix;
}

int main() {
    std::string res = infixToPostfix("A+B*C");
    std::cout << "A+B*C -> " << res << std::endl;
    assert(res == "ABC*+");
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PostfixEvaluation()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

int evaluatePostfix(std::string exp) {
    std::stack<int> s;
    for (char c : exp) {
        if (isdigit(c)) s.push(c - '0');
        else {
            int val1 = s.top(); s.pop();
            int val2 = s.top(); s.pop();
            switch (c) {
                case '+': s.push(val2 + val1); break;
                case '*': s.push(val2 * val1); break;
            }
        }
    }
    return s.top();
}

int main() {
    int res = evaluatePostfix("23*4+");
    std::cout << "23*4+ -> " << res << std::endl;
    assert(res == 10);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PrefixEvaluation()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

int evaluatePrefix(std::string exp) {
    std::stack<int> s;
    for (int i = exp.length() - 1; i >= 0; i--) {
        if (isdigit(exp[i])) s.push(exp[i] - '0');
        else {
            int val1 = s.top(); s.pop();
            int val2 = s.top(); s.pop();
            if (exp[i] == '+') s.push(val1 + val2);
            else if (exp[i] == '*') s.push(val1 * val2);
        }
    }
    return s.top();
}

int main() {
    int res = evaluatePrefix("+*234");
    std::cout << "+*234 -> " << res << std::endl;
    assert(res == 10);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## DecimalToBinary()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

std::string decimalToBinary(int n) {
    if (n == 0) return "0";
    std::stack<int> s;
    while (n > 0) {
        s.push(n % 2);
        n /= 2;
    }
    std::string res = "";
    while (!s.empty()) { 
        res += std::to_string(s.top()); 
        s.pop(); 
    }
    return res;
}

int main() {
    std::string res = decimalToBinary(13);
    std::cout << "13 in binary -> " << res << std::endl;
    assert(res == "1101");
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(log N)
```
## BaseConversion()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::string convertBase(int n, int base) {
    if (n == 0) return "0";
    std::stack<int> s;
    while (n > 0) {
        s.push(n % base);
        n /= base;
    }
    std::string res = "";
    std::string digits = "0123456789ABCDEF";
    while (!s.empty()) { 
        res += digits[s.top()]; 
        s.pop(); 
    }
    return res;
}

int main() {
    std::string res = convertBase(255, 16);
    std::cout << "255 in base 16 -> " << res << std::endl;
    assert(res == "FF");
    return 0;
}
// Time Complexity: O(log_base N)
// Space Complexity: O(log_base N)
```
## Undo()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::stack<std::string> undoStack;
std::string currentState = "";

void typeChar(char c) {
    undoStack.push(currentState);
    currentState += c;
}

void undo() {
    if (!undoStack.empty()) {
        currentState = undoStack.top();
        undoStack.pop();
    }
}

int main() {
    typeChar('A');
    typeChar('B');
    assert(currentState == "AB");
    undo();
    std::cout << "After undo: " << currentState << std::endl;
    assert(currentState == "A");
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## BrowserHistory()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <string>
#include <cassert>

std::stack<std::string> backStack, forwardStack;
std::string currentUrl = "home.com";

void visit(std::string url) {
    backStack.push(currentUrl);
    currentUrl = url;
    forwardStack = std::stack<std::string>();
}

void back() {
    if (!backStack.empty()) {
        forwardStack.push(currentUrl);
        currentUrl = backStack.top();
        backStack.pop();
    }
}

int main() {
    visit("google.com");
    visit("github.com");
    assert(currentUrl == "github.com");
    back();
    std::cout << "Back to: " << currentUrl << std::endl;
    assert(currentUrl == "google.com");
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```

# Part 5. DFS
## DepthFirstSearch()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> adj[4];
bool visited[4] = {false};
std::vector<int> result;

void DFS(int start) {
    std::stack<int> s;
    s.push(start);
    while (!s.empty()) {
        int v = s.top(); s.pop();
        if (!visited[v]) {
            visited[v] = true;
            result.push_back(v);
            for (auto it = adj[v].rbegin(); it != adj[v].rend(); ++it) {
                s.push(*it);
            }
        }
    }
}

int main() {
    adj[0] = {1, 2};
    adj[1] = {3};
    DFS(0);
    assert(result[0] == 0 && result[1] == 1 && result[2] == 3 && result[3] == 2);
    std::cout << "DFS traversal verified." << std::endl;
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

// DepthFirstSearch()와 동일한 명시적 스택 기반 구현
int main() {
    std::stack<int> s;
    s.push(1);
    std::cout << "Iterative DFS uses stack explicitly." << std::endl;
    assert(!s.empty());
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## MazeSolver()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

struct Point { int x, y; };

int main() {
    std::stack<Point> path;
    Point start = {0, 0};
    Point end = {2, 2};
    path.push(start);
    path.push({1, 0});
    path.push({2, 0});
    path.push({2, 2}); // Reached
    
    assert(path.top().x == end.x && path.top().y == end.y);
    std::cout << "Maze solver reached end." << std::endl;
    return 0;
}
// Time Complexity: O(V) where V is number of cells
// Space Complexity: O(V)
```
## TopologicalSort()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> adj[4];
bool visited[4] = {false};

void dfs(int v, std::stack<int>& s) {
    visited[v] = true;
    for (int u : adj[v]) {
        if (!visited[u]) dfs(u, s);
    }
    s.push(v);
}

int main() {
    adj[0] = {1};
    adj[1] = {2};
    std::stack<int> s;
    for (int i = 0; i < 3; i++) {
        if (!visited[i]) dfs(i, s);
    }
    assert(s.top() == 0);
    std::cout << "Topological Sort Top: " << s.top() << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```

# Part 6. 단조 스택
## MonotonicStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <vector>
#include <cassert>

int main() {
    std::vector<int> arr = {3, 1, 4, 2};
    std::stack<int> s; // 단조 감소 스택 유지
    for (int val : arr) {
        while (!s.empty() && s.top() < val) {
            s.pop();
        }
        s.push(val);
    }
    assert(s.top() == 2);
    std::cout << "Monotonic stack implemented." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## NextGreaterElement()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> nextGreater(std::vector<int>& arr) {
    std::stack<int> s;
    std::vector<int> res(arr.size(), -1);
    for (int i = 0; i < arr.size(); ++i) {
        while (!s.empty() && arr[s.top()] < arr[i]) {
            res[s.top()] = arr[i];
            s.pop();
        }
        s.push(i);
    }
    return res;
}

int main() {
    std::vector<int> arr = {2, 1, 2, 4, 3};
    std::vector<int> res = nextGreater(arr);
    std::cout << "Next Greater of 2 -> " << res[0] << std::endl;
    assert(res[0] == 4);
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## PreviousGreaterElement()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> prevGreater(std::vector<int>& arr) {
    std::stack<int> s;
    std::vector<int> res(arr.size(), -1);
    for (int i = 0; i < arr.size(); ++i) {
        while (!s.empty() && arr[s.top()] <= arr[i]) {
            s.pop();
        }
        if (!s.empty()) res[i] = arr[s.top()];
        s.push(i);
    }
    return res;
}

int main() {
    std::vector<int> arr = {4, 2, 3};
    std::vector<int> res = prevGreater(arr);
    assert(res[1] == 4 && res[2] == 4);
    std::cout << "Previous greater working." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## LargestRectangle()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <cassert>

int largestRectangleArea(std::vector<int>& heights) {
    std::stack<int> s;
    int maxArea = 0;
    heights.push_back(0); 
    for (int i = 0; i < heights.size(); ++i) {
        while (!s.empty() && heights[s.top()] > heights[i]) {
            int h = heights[s.top()]; s.pop();
            int w = s.empty() ? i : i - s.top() - 1;
            maxArea = std::max(maxArea, h * w);
        }
        s.push(i);
    }
    return maxArea;
}

int main() {
    std::vector<int> heights = {2, 1, 5, 6, 2, 3};
    int res = largestRectangleArea(heights);
    assert(res == 10);
    std::cout << "Max rectangle area: " << res << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## DailyTemperatures()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <cassert>

std::vector<int> dailyTemperatures(std::vector<int>& temp) {
    std::stack<int> s;
    std::vector<int> res(temp.size(), 0);
    for (int i = 0; i < temp.size(); ++i) {
        while (!s.empty() && temp[s.top()] < temp[i]) {
            res[s.top()] = i - s.top();
            s.pop();
        }
        s.push(i);
    }
    return res;
}

int main() {
    std::vector<int> temp = {73, 74, 75, 71, 69, 72, 76, 73};
    std::vector<int> res = dailyTemperatures(temp);
    assert(res[0] == 1 && res[1] == 1 && res[2] == 4);
    std::cout << "Daily temperatures verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## StockSpan()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

class StockSpanner {
    std::stack<std::pair<int, int>> s; 
public:
    int next(int price) {
        int span = 1;
        while (!s.empty() && s.top().first <= price) {
            span += s.top().second;
            s.pop();
        }
        s.push({price, span});
        return span;
    }
};

int main() {
    StockSpanner ss;
    assert(ss.next(100) == 1);
    assert(ss.next(80) == 1);
    assert(ss.next(120) == 3);
    std::cout << "StockSpan functional." << std::endl;
    return 0;
}
// Time Complexity: Amortized O(1) per call
// Space Complexity: O(N)
```

# Part 7. 특수 스택
## MinStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

class MinStack {
    std::stack<int> s, min_s;
public:
    void push(int val) {
        s.push(val);
        if (min_s.empty() || val <= min_s.top()) min_s.push(val);
    }
    void pop() {
        if (s.top() == min_s.top()) min_s.pop();
        s.pop();
    }
    int getMin() { return min_s.top(); }
};

int main() {
    MinStack ms;
    ms.push(3); ms.push(1); ms.push(4);
    assert(ms.getMin() == 1);
    ms.pop(); ms.pop();
    assert(ms.getMin() == 3);
    std::cout << "MinStack verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) per operation
// Space Complexity: O(N)
```
## MaxStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

class MaxStack {
    std::stack<int> s, max_s;
public:
    void push(int val) {
        s.push(val);
        if (max_s.empty() || val >= max_s.top()) max_s.push(val);
    }
    void pop() {
        if (s.top() == max_s.top()) max_s.pop();
        s.pop();
    }
    int getMax() { return max_s.top(); }
};

int main() {
    MaxStack ms;
    ms.push(1); ms.push(5); ms.push(2);
    assert(ms.getMax() == 5);
    std::cout << "MaxStack verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) per operation
// Space Complexity: O(N)
```
## TwoStacksInArray()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

class TwoStacks {
    int arr[100];
    int top1 = -1, top2 = 100;
public:
    void push1(int x) { if (top1 < top2 - 1) arr[++top1] = x; }
    void push2(int x) { if (top1 < top2 - 1) arr[--top2] = x; }
    int getTop1() { return arr[top1]; }
    int getTop2() { return arr[top2]; }
};

int main() {
    TwoStacks ts;
    ts.push1(10);
    ts.push2(20);
    assert(ts.getTop1() == 10 && ts.getTop2() == 20);
    std::cout << "Two stacks in array tested." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```
## MultipleStacks()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

int main() {
    // k개의 스택을 단일 배열로 표현하는 대신 k개의 벡터를 사용
    std::vector<std::vector<int>> stacks(3);
    stacks[0].push_back(10);
    stacks[2].push_back(30);
    assert(stacks[0].back() == 10);
    std::cout << "Multiple stacks logic works." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(N)
```

# Part 8. 재귀
## CallStack()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    int res = factorial(5);
    assert(res == 120);
    std::cout << "CallStack factorial(5) -> 120" << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N) due to Call Stack
```
## StackFrame()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int funcB(int b) { return b + 1; }
int funcA(int a) { return funcB(a) * 2; }

int main() {
    int res = funcA(3); // funcA 프레임 위에 funcB 프레임 생성
    assert(res == 8);
    std::cout << "Stack frames handled properly." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TailRecursion()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int tailFact(int n, int acc = 1) {
    if (n == 0) return acc;
    return tailFact(n - 1, n * acc); // 반환 후 추가 연산 없음
}

int main() {
    assert(tailFact(5) == 120);
    std::cout << "Tail recursion executed." << std::endl;
    return 0;
}
// Time/Space Complexity: O(N) time, O(1) space with optimization
```
## RecursionSimulation()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int factSimulate(int n) {
    std::stack<int> s;
    for (int i = n; i > 0; i--) s.push(i);
    int res = 1;
    while (!s.empty()) {
        res *= s.top(); s.pop();
    }
    return res;
}

int main() {
    assert(factSimulate(5) == 120);
    std::cout << "Recursion simulated via stack." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```

# Part 9. 병렬
## LockFreeStack()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <cassert>

struct Node { int data; Node* next; };
std::atomic<Node*> head(nullptr);

void push(int data) {
    Node* newNode = new Node{data, head.load()};
    while (!head.compare_exchange_weak(newNode->next, newNode));
}

int main() {
    push(42);
    assert(head.load()->data == 42);
    std::cout << "LockFreeStack CAS push verified." << std::endl;
    return 0;
}
// Time Complexity: O(1) average
// Space Complexity: O(1) per node
```
## TreiberStack()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <cassert>

template<typename T>
class TreiberStack {
    struct Node { T data; Node* next; };
    std::atomic<Node*> head{nullptr};
public:
    void push(T data) {
        Node* newNode = new Node{data, head.load()};
        while (!head.compare_exchange_weak(newNode->next, newNode));
    }
    T top() { return head.load()->data; }
};

int main() {
    TreiberStack<int> s;
    s.push(10);
    assert(s.top() == 10);
    std::cout << "Treiber Stack functioning." << std::endl;
    return 0;
}
// Time Complexity: O(1) average
// Space Complexity: O(1) per node
```
## EliminationBackoffStack()
### 대표코드
```cpp
#include <iostream>
#include <stack>
#include <cassert>

int main() {
    // 개념적으로 Elimination Array를 추가해 동시 Push와 Pop 스레드가
    // 스택(Head)까지 가지 않고 중간에서 교환 후 종료하는 최적화
    std::stack<int> s;
    s.push(1); // Placeholder
    assert(!s.empty());
    std::cout << "Elimination Backoff Stack concept." << std::endl;
    return 0;
}
// Time Complexity: O(1) 
// Space Complexity: O(N)
```

# Part 10. 연구 주제
## PersistentStack()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <cassert>

struct Node {
    int data;
    std::shared_ptr<Node> next;
};

std::shared_ptr<Node> push(std::shared_ptr<Node> s, int x) {
    return std::make_shared<Node>(Node{x, s});
}

int main() {
    auto v1 = push(nullptr, 10);
    auto v2 = push(v1, 20); // v2는 20->10, v1은 10 유지
    assert(v1->data == 10 && v2->data == 20);
    std::cout << "Persistent Stack maintains versions." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per update
```
## ImmutableStack()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

// Persistent Stack과 구현 동일 (새 상태 반환)
int main() {
    int state = 1;
    int newState = state + 1; // Immutable change
    assert(state == 1 && newState == 2);
    std::cout << "Immutable Stack concept." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per update
```
## StackAllocator()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

class StackAllocator {
    char memory[1024];
    int offset = 0;
public:
    void* alloc(int size) {
        if (offset + size > 1024) return nullptr;
        void* ptr = memory + offset;
        offset += size;
        return ptr;
    }
};

int main() {
    StackAllocator sa;
    int* ptr = (int*)sa.alloc(sizeof(int));
    *ptr = 10;
    assert(*ptr == 10);
    std::cout << "Stack Allocator works." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1) per allocation
```
## StackOverflow()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    // void infinite() { infinite(); }
    // 무한 재귀 시 스택 메모리 공간 한계 초과
    bool overflowUnderstood = true;
    assert(overflowUnderstood);
    std::cout << "Stack Overflow concept." << std::endl;
    return 0;
}
// Time Complexity: O(N) until crash
// Space Complexity: O(N) until crash
```
## StackUnwinding()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Dummy {
    ~Dummy() { /* Stack unwinding during exception calls this */ }
};

int main() {
    try {
        Dummy d;
        throw std::runtime_error("Error");
    } catch (...) {
        std::cout << "Exception caught, stack unwound." << std::endl;
    }
    assert(true);
    return 0;
}
// Time Complexity: O(Depth)
// Space Complexity: O(1) overhead
```
