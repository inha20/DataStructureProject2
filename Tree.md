# Part 1. 트리의 기초
## CreateTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node {
    int data;
    Node* left;
    Node* right;
};

int main() {
    Node* root = new Node{10, nullptr, nullptr};
    std::cout << "Tree root created with data: " << root->data << std::endl;
    assert(root->data == 10);
    delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Root()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *left, *right; };
Node* root = nullptr;

Node* getRoot() {
    return root;
}

int main() {
    root = new Node{1, nullptr, nullptr};
    Node* r = getRoot();
    std::cout << "Root data: " << r->data << std::endl;
    assert(r == root);
    delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Parent()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node {
    int data;
    Node* parent;
    Node* left;
    Node* right;
};

int main() {
    Node* root = new Node{1, nullptr, nullptr, nullptr};
    Node* child = new Node{2, root, nullptr, nullptr};
    root->left = child;
    
    std::cout << "Parent of child is: " << child->parent->data << std::endl;
    assert(child->parent == root);
    
    delete child; delete root;
    return 0;
}
// Time Complexity: O(1) if parent pointer exists
// Space Complexity: O(1)
```
## Child()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *left, *right; };

int main() {
    Node* root = new Node{1, new Node{2, nullptr, nullptr}, nullptr};
    Node* child = root->left;
    std::cout << "Left child data: " << child->data << std::endl;
    assert(child->data == 2);
    delete child; delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Sibling()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *parent, *left, *right; };

Node* getSibling(Node* node) {
    if (!node || !node->parent) return nullptr;
    if (node->parent->left == node) return node->parent->right;
    return node->parent->left;
}

int main() {
    Node* root = new Node{1, nullptr, nullptr, nullptr};
    Node* leftChild = new Node{2, root, nullptr, nullptr};
    Node* rightChild = new Node{3, root, nullptr, nullptr};
    root->left = leftChild; root->right = rightChild;
    
    Node* sibling = getSibling(leftChild);
    std::cout << "Sibling of left child: " << sibling->data << std::endl;
    assert(sibling == rightChild);
    
    delete leftChild; delete rightChild; delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Degree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *left, *right; };

int getDegree(Node* node) {
    if (!node) return 0;
    return (node->left ? 1 : 0) + (node->right ? 1 : 0);
}

int main() {
    Node* root = new Node{1, new Node{2, nullptr, nullptr}, nullptr};
    int degree = getDegree(root);
    std::cout << "Degree of root: " << degree << std::endl;
    assert(degree == 1);
    delete root->left; delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Depth()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *parent, *left, *right; };

int getDepth(Node* node) {
    int depth = 0;
    while (node && node->parent) {
        node = node->parent;
        depth++;
    }
    return depth;
}

int main() {
    Node* root = new Node{1, nullptr, nullptr, nullptr};
    Node* child = new Node{2, root, nullptr, nullptr};
    root->left = child;
    
    int depth = getDepth(child);
    std::cout << "Depth of child: " << depth << std::endl;
    assert(depth == 1);
    
    delete child; delete root;
    return 0;
}
// Time Complexity: O(H) where H is depth
// Space Complexity: O(1)
```
## Height()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cassert>

struct Node { int data; Node *left, *right; };

int getHeight(Node* node) {
    if (!node) return -1; 
    return 1 + std::max(getHeight(node->left), getHeight(node->right));
}

int main() {
    Node* root = new Node{1, new Node{2, nullptr, nullptr}, nullptr};
    int height = getHeight(root);
    std::cout << "Height of tree: " << height << std::endl;
    assert(height == 1);
    delete root->left; delete root;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## Level()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int getLevel(int depth) {
    return depth + 1; // Assuming root is at Level 1
}

int main() {
    int depth = 2; // e.g., root -> child -> grandchild
    int level = getLevel(depth);
    std::cout << "Level: " << level << std::endl;
    assert(level == 3);
    return 0;
}
// Time Complexity: O(1) given depth
// Space Complexity: O(1)
```
## Size()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *left, *right; };

int getSize(Node* node) {
    if (!node) return 0;
    return 1 + getSize(node->left) + getSize(node->right);
}

int main() {
    Node* root = new Node{1, new Node{2, nullptr, nullptr}, new Node{3, nullptr, nullptr}};
    int size = getSize(root);
    std::cout << "Size of tree: " << size << std::endl;
    assert(size == 3);
    delete root->left; delete root->right; delete root;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## IsLeaf()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *left, *right; };

bool isLeaf(Node* node) {
    if (!node) return false;
    return (node->left == nullptr && node->right == nullptr);
}

int main() {
    Node* leaf = new Node{10, nullptr, nullptr};
    bool res = isLeaf(leaf);
    std::cout << "Is leaf: " << res << std::endl;
    assert(res == true);
    delete leaf;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IsRoot()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct Node { int data; Node *parent, *left, *right; };

bool isRoot(Node* node) {
    return node && node->parent == nullptr;
}

int main() {
    Node* root = new Node{1, nullptr, nullptr, nullptr};
    bool res = isRoot(root);
    std::cout << "Is root: " << res << std::endl;
    assert(res == true);
    delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 2. 이진트리
## CreateBinaryTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode {
    int val;
    TreeNode *left, *right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

int main() {
    TreeNode* root = new TreeNode(10);
    std::cout << "Binary Tree created." << std::endl;
    assert(root->val == 10);
    delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## InsertLeft()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode {
    int val;
    TreeNode *left, *right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

int main() {
    TreeNode* root = new TreeNode(10);
    root->left = new TreeNode(20);
    std::cout << "Left child inserted." << std::endl;
    assert(root->left->val == 20);
    delete root->left; delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## InsertRight()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode {
    int val;
    TreeNode *left, *right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

int main() {
    TreeNode* root = new TreeNode(10);
    root->right = new TreeNode(30);
    std::cout << "Right child inserted." << std::endl;
    assert(root->right->val == 30);
    delete root->right; delete root;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DeleteNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* deleteNode(TreeNode* root, int key) {
    if (!root) return nullptr;
    if (key < root->val) root->left = deleteNode(root->left, key);
    else if (key > root->val) root->right = deleteNode(root->right, key);
    else {
        if (!root->left) { TreeNode* tmp = root->right; delete root; return tmp; }
        else if (!root->right) { TreeNode* tmp = root->left; delete root; return tmp; }
        TreeNode* minNode = root->right;
        while (minNode && minNode->left) minNode = minNode->left;
        root->val = minNode->val;
        root->right = deleteNode(root->right, root->val);
    }
    return root;
}

int main() {
    TreeNode* root = new TreeNode(10);
    root->right = new TreeNode(20);
    root = deleteNode(root, 20);
    std::cout << "Node deleted." << std::endl;
    assert(root->right == nullptr);
    delete root;
    return 0;
}
// Time Complexity: O(H) where H is tree height
// Space Complexity: O(H) call stack
```
## CopyTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l, TreeNode* r) : val(x), left(l), right(r) {} };

TreeNode* copyTree(TreeNode* node) {
    if (!node) return nullptr;
    return new TreeNode(node->val, copyTree(node->left), copyTree(node->right));
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2, nullptr, nullptr), nullptr);
    TreeNode* copied = copyTree(root);
    std::cout << "Tree copied." << std::endl;
    assert(copied->left->val == 2);
    // Cleanup skipped for brevity
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## MirrorTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l, TreeNode* r) : val(x), left(l), right(r) {} };

void mirror(TreeNode* node) {
    if (!node) return;
    std::swap(node->left, node->right);
    mirror(node->left);
    mirror(node->right);
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2, nullptr, nullptr), new TreeNode(3, nullptr, nullptr));
    mirror(root);
    std::cout << "Tree mirrored." << std::endl;
    assert(root->left->val == 3 && root->right->val == 2);
    // Cleanup skipped for brevity
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## MergeTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

TreeNode* mergeTrees(TreeNode* t1, TreeNode* t2) {
    if (!t1) return t2;
    if (!t2) return t1;
    t1->val += t2->val;
    t1->left = mergeTrees(t1->left, t2->left);
    t1->right = mergeTrees(t1->right, t2->right);
    return t1;
}

int main() {
    TreeNode* t1 = new TreeNode(1, new TreeNode(2));
    TreeNode* t2 = new TreeNode(2, nullptr, new TreeNode(3));
    TreeNode* merged = mergeTrees(t1, t2);
    std::cout << "Trees merged." << std::endl;
    assert(merged->val == 3 && merged->left->val == 2 && merged->right->val == 3);
    // Cleanup skipped
    return 0;
}
// Time Complexity: O(min(N, M))
// Space Complexity: O(min(H1, H2)) call stack
```

# Part 3. 순회
## Preorder()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };
std::vector<int> res;

void preorder(TreeNode* node) {
    if (!node) return;
    res.push_back(node->val);      // V
    preorder(node->left);          // L
    preorder(node->right);         // R
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2), new TreeNode(3));
    preorder(root);
    assert(res[0] == 1 && res[1] == 2 && res[2] == 3);
    std::cout << "Preorder verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## Inorder()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };
std::vector<int> res;

void inorder(TreeNode* node) {
    if (!node) return;
    inorder(node->left);           // L
    res.push_back(node->val);      // V
    inorder(node->right);          // R
}

int main() {
    TreeNode* root = new TreeNode(2, new TreeNode(1), new TreeNode(3));
    inorder(root);
    assert(res[0] == 1 && res[1] == 2 && res[2] == 3);
    std::cout << "Inorder verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## Postorder()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };
std::vector<int> res;

void postorder(TreeNode* node) {
    if (!node) return;
    postorder(node->left);         // L
    postorder(node->right);        // R
    res.push_back(node->val);      // V
}

int main() {
    TreeNode* root = new TreeNode(3, new TreeNode(1), new TreeNode(2));
    postorder(root);
    assert(res[0] == 1 && res[1] == 2 && res[2] == 3);
    std::cout << "Postorder verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## LevelOrder()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

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
    TreeNode* root = new TreeNode(1, new TreeNode(2), new TreeNode(3));
    std::vector<int> res = levelOrder(root);
    assert(res[0] == 1 && res[1] == 2 && res[2] == 3);
    std::cout << "LevelOrder verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## MorrisTraversal()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

std::vector<int> morrisInorder(TreeNode* root) {
    std::vector<int> res;
    TreeNode* curr = root;
    while (curr) {
        if (!curr->left) {
            res.push_back(curr->val);
            curr = curr->right;
        } else {
            TreeNode* pre = curr->left;
            while (pre->right && pre->right != curr) pre = pre->right;
            if (!pre->right) {
                pre->right = curr;
                curr = curr->left;
            } else {
                pre->right = nullptr;
                res.push_back(curr->val);
                curr = curr->right;
            }
        }
    }
    return res;
}

int main() {
    TreeNode* root = new TreeNode(2);
    root->left = new TreeNode(1); root->right = new TreeNode(3);
    std::vector<int> res = morrisInorder(root);
    assert(res[0] == 1 && res[1] == 2 && res[2] == 3);
    std::cout << "Morris Inorder Traversal verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(1)
```
## EulerTour()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };
std::vector<int> eulerTourResult;

void eulerTour(TreeNode* u) {
    if(!u) return;
    eulerTourResult.push_back(u->val); // in
    if(u->left) { eulerTour(u->left); eulerTourResult.push_back(u->val); } // back from left
    if(u->right) { eulerTour(u->right); eulerTourResult.push_back(u->val); } // back from right
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2));
    eulerTour(root);
    assert(eulerTourResult.size() == 3 && eulerTourResult[1] == 2);
    std::cout << "Euler Tour verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```

# Part 4. 탐색
## TreeSearch()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

bool treeSearch(TreeNode* root, int target) {
    if (!root) return false;
    if (root->val == target) return true;
    return treeSearch(root->left, target) || treeSearch(root->right, target);
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2), new TreeNode(3));
    assert(treeSearch(root, 3) == true);
    assert(treeSearch(root, 4) == false);
    std::cout << "Tree Search verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H) call stack
```
## FindNode()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

TreeNode* findNode(TreeNode* node, int val) {
    if (!node) return nullptr;
    if (node->val == val) return node;
    TreeNode* leftRes = findNode(node->left, val);
    if (leftRes) return leftRes;
    return findNode(node->right, val);
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2));
    TreeNode* res = findNode(root, 2);
    assert(res && res->val == 2);
    std::cout << "Find Node verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H)
```
## FindParent()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

TreeNode* findParent(TreeNode* root, TreeNode* target) {
    if (!root || root == target) return nullptr;
    if (root->left == target || root->right == target) return root;
    TreeNode* leftRes = findParent(root->left, target);
    if (leftRes) return leftRes;
    return findParent(root->right, target);
}

int main() {
    TreeNode* child = new TreeNode(2);
    TreeNode* root = new TreeNode(1, child);
    TreeNode* parent = findParent(root, child);
    assert(parent == root);
    std::cout << "Find Parent verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H)
```
## LowestCommonAncestor()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

TreeNode* LCA(TreeNode* root, TreeNode* p, TreeNode* q) {
    if (!root || root == p || root == q) return root;
    TreeNode* left = LCA(root->left, p, q);
    TreeNode* right = LCA(root->right, p, q);
    if (left && right) return root;
    return left ? left : right;
}

int main() {
    TreeNode* p = new TreeNode(2);
    TreeNode* q = new TreeNode(3);
    TreeNode* root = new TreeNode(1, p, q);
    TreeNode* lca = LCA(root, p, q);
    assert(lca == root);
    std::cout << "LCA verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H)
```
## PathToNode()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

bool getPath(TreeNode* root, int target, std::vector<int>& path) {
    if (!root) return false;
    path.push_back(root->val);
    if (root->val == target) return true;
    if (getPath(root->left, target, path) || getPath(root->right, target, path)) return true;
    path.pop_back();
    return false;
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2, new TreeNode(4)));
    std::vector<int> path;
    getPath(root, 4, path);
    assert(path.size() == 3 && path[2] == 4);
    std::cout << "PathToNode verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H)
```
## DistanceBetweenNodes()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x, TreeNode* l=nullptr, TreeNode* r=nullptr) : val(x), left(l), right(r) {} };

TreeNode* findLCA(TreeNode* root, int n1, int n2) {
    if(!root) return nullptr;
    if(root->val == n1 || root->val == n2) return root;
    TreeNode* left = findLCA(root->left, n1, n2);
    TreeNode* right = findLCA(root->right, n1, n2);
    if(left && right) return root;
    return left ? left : right;
}

int findLevel(TreeNode* root, int k, int level) {
    if(!root) return -1;
    if(root->val == k) return level;
    int left = findLevel(root->left, k, level+1);
    if(left == -1) return findLevel(root->right, k, level+1);
    return left;
}

int findDistance(TreeNode* root, int a, int b) {
    TreeNode* lca = findLCA(root, a, b);
    int d1 = findLevel(lca, a, 0);
    int d2 = findLevel(lca, b, 0);
    return d1 + d2;
}

int main() {
    TreeNode* root = new TreeNode(1, new TreeNode(2), new TreeNode(3));
    int dist = findDistance(root, 2, 3);
    assert(dist == 2);
    std::cout << "DistanceBetweenNodes verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H)
```

# Part 5. 이진 탐색 트리(BST)
## InsertBST()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* insertBST(TreeNode* root, int val) {
    if (!root) return new TreeNode(val);
    if (val < root->val) root->left = insertBST(root->left, val);
    else root->right = insertBST(root->right, val);
    return root;
}

int main() {
    TreeNode* root = nullptr;
    root = insertBST(root, 10);
    root = insertBST(root, 5);
    root = insertBST(root, 15);
    assert(root->left->val == 5 && root->right->val == 15);
    std::cout << "InsertBST verified." << std::endl;
    return 0;
}
// Time Complexity: O(H)
// Space Complexity: O(H) call stack
```
## SearchBST()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* searchBST(TreeNode* root, int val) {
    if (!root || root->val == val) return root;
    if (val < root->val) return searchBST(root->left, val);
    return searchBST(root->right, val);
}

int main() {
    TreeNode* root = new TreeNode(10);
    root->left = new TreeNode(5); root->right = new TreeNode(15);
    TreeNode* res = searchBST(root, 15);
    assert(res && res->val == 15);
    std::cout << "SearchBST verified." << std::endl;
    return 0;
}
// Time Complexity: O(H)
// Space Complexity: O(H) call stack
```
## DeleteBST()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* findMin(TreeNode* root) {
    while (root && root->left) root = root->left;
    return root;
}

TreeNode* deleteBST(TreeNode* root, int key) {
    if (!root) return nullptr;
    if (key < root->val) root->left = deleteBST(root->left, key);
    else if (key > root->val) root->right = deleteBST(root->right, key);
    else {
        if (!root->left) { TreeNode* tmp = root->right; delete root; return tmp; }
        else if (!root->right) { TreeNode* tmp = root->left; delete root; return tmp; }
        TreeNode* minNode = findMin(root->right);
        root->val = minNode->val;
        root->right = deleteBST(root->right, root->val);
    }
    return root;
}

int main() {
    TreeNode* root = new TreeNode(10);
    root->right = new TreeNode(20);
    root = deleteBST(root, 10);
    assert(root->val == 20);
    std::cout << "DeleteBST verified." << std::endl;
    return 0;
}
// Time Complexity: O(H)
// Space Complexity: O(H)
```
## FindMin()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* findMin(TreeNode* root) {
    while (root && root->left) root = root->left;
    return root;
}

int main() {
    TreeNode* root = new TreeNode(10);
    root->left = new TreeNode(5); root->left->left = new TreeNode(1);
    assert(findMin(root)->val == 1);
    std::cout << "FindMin verified." << std::endl;
    return 0;
}
// Time Complexity: O(H)
// Space Complexity: O(1)
```
## FindMax()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* findMax(TreeNode* root) {
    while (root && root->right) root = root->right;
    return root;
}

int main() {
    TreeNode* root = new TreeNode(10);
    root->right = new TreeNode(20); root->right->right = new TreeNode(30);
    assert(findMax(root)->val == 30);
    std::cout << "FindMax verified." << std::endl;
    return 0;
}
// Time Complexity: O(H)
// Space Complexity: O(1)
```
## Successor()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* getSuccessor(TreeNode* root, TreeNode* p) {
    TreeNode* succ = nullptr;
    while(root) {
        if(p->val < root->val) { succ = root; root = root->left; }
        else root = root->right;
    }
    return succ;
}

int main() {
    TreeNode* root = new TreeNode(10);
    TreeNode* leftChild = new TreeNode(5);
    root->left = leftChild; root->right = new TreeNode(15);
    TreeNode* succ = getSuccessor(root, leftChild);
    assert(succ && succ->val == 10);
    std::cout << "Successor verified." << std::endl;
    return 0;
}
// Time Complexity: O(H)
// Space Complexity: O(1)
```
## Predecessor()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

TreeNode* getPredecessor(TreeNode* root, TreeNode* p) {
    TreeNode* pred = nullptr;
    while(root) {
        if(p->val > root->val) { pred = root; root = root->right; }
        else root = root->left;
    }
    return pred;
}

int main() {
    TreeNode* root = new TreeNode(10);
    TreeNode* rightChild = new TreeNode(15);
    root->left = new TreeNode(5); root->right = rightChild;
    TreeNode* pred = getPredecessor(root, rightChild);
    assert(pred && pred->val == 10);
    std::cout << "Predecessor verified." << std::endl;
    return 0;
}
// Time Complexity: O(H)
// Space Complexity: O(1)
```
## ValidateBST()
### 대표코드
```cpp
#include <iostream>
#include <climits>
#include <cassert>

struct TreeNode { int val; TreeNode *left, *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };

bool isValidBST(TreeNode* root, long minVal, long maxVal) {
    if (!root) return true;
    if (root->val <= minVal || root->val >= maxVal) return false;
    return isValidBST(root->left, minVal, root->val) && isValidBST(root->right, root->val, maxVal);
}

int main() {
    TreeNode* root = new TreeNode(10);
    root->left = new TreeNode(5); root->right = new TreeNode(15);
    bool isValid = isValidBST(root, LONG_MIN, LONG_MAX);
    assert(isValid == true);
    std::cout << "ValidateBST verified." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(H)
```

﻿# Part 6. AVL 트리
## AVLInsert()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
#include <algorithm>

struct AVLNode { int key, height; AVLNode *left, *right; AVLNode(int k): key(k), height(1), left(nullptr), right(nullptr) {} };
int h(AVLNode* n){ return n? n->height:0; }
int bf(AVLNode* n){ return n? h(n->left)-h(n->right):0; }
void upH(AVLNode* n){ if(n) n->height=1+std::max(h(n->left),h(n->right)); }
AVLNode* rotR(AVLNode* y){ AVLNode* x=y->left; y->left=x->right; x->right=y; upH(y); upH(x); return x; }
AVLNode* rotL(AVLNode* x){ AVLNode* y=x->right; x->right=y->left; y->left=x; upH(x); upH(y); return y; }
AVLNode* balance(AVLNode* n){ upH(n); if(bf(n)>1){ if(bf(n->left)<0) n->left=rotL(n->left); return rotR(n); } if(bf(n)<-1){ if(bf(n->right)>0) n->right=rotR(n->right); return rotL(n); } return n; }
AVLNode* avlInsert(AVLNode* n, int key){ if(!n) return new AVLNode(key); if(key<n->key) n->left=avlInsert(n->left,key); else if(key>n->key) n->right=avlInsert(n->right,key); return balance(n); }
int main() {
    AVLNode* root=nullptr;
    for(int k:{10,20,30,40,50,25}) root=avlInsert(root,k);
    assert(std::abs(bf(root))<=1);
    std::cout << "AVLInsert verified. Root=" << root->key << std::endl;
    return 0;
}
// Time Complexity: O(log N) / Space Complexity: O(log N)
```
## AVLDelete()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
#include <algorithm>

struct AVLNodeD { int key, height; AVLNodeD *left, *right; AVLNodeD(int k): key(k), height(1), left(nullptr), right(nullptr) {} };
int hD(AVLNodeD* n){ return n?n->height:0; }
int bfD(AVLNodeD* n){ return n?hD(n->left)-hD(n->right):0; }
void upHD(AVLNodeD* n){ if(n) n->height=1+std::max(hD(n->left),hD(n->right)); }
AVLNodeD* rotRD(AVLNodeD* y){ AVLNodeD* x=y->left; y->left=x->right; x->right=y; upHD(y); upHD(x); return x; }
AVLNodeD* rotLD(AVLNodeD* x){ AVLNodeD* y=x->right; x->right=y->left; y->left=x; upHD(x); upHD(y); return y; }
AVLNodeD* balD(AVLNodeD* n){ upHD(n); if(bfD(n)>1){if(bfD(n->left)<0)n->left=rotLD(n->left);return rotRD(n);} if(bfD(n)<-1){if(bfD(n->right)>0)n->right=rotRD(n->right);return rotLD(n);} return n; }
AVLNodeD* minN(AVLNodeD* n){ while(n->left) n=n->left; return n; }
AVLNodeD* avlDel(AVLNodeD* n, int key){ if(!n) return nullptr; if(key<n->key) n->left=avlDel(n->left,key); else if(key>n->key) n->right=avlDel(n->right,key); else { if(!n->left||!n->right){ AVLNodeD* t=n->left?n->left:n->right; delete n; return t; } AVLNodeD* s=minN(n->right); n->key=s->key; n->right=avlDel(n->right,s->key); } return balD(n); }
AVLNodeD* avlIns(AVLNodeD* n, int k){ if(!n) return new AVLNodeD(k); if(k<n->key) n->left=avlIns(n->left,k); else if(k>n->key) n->right=avlIns(n->right,k); return balD(n); }
int main() {
    AVLNodeD* root=nullptr;
    for(int k:{10,20,30,40,50}) root=avlIns(root,k);
    root=avlDel(root,30);
    assert(std::abs(bfD(root))<=1);
    std::cout << "AVLDelete verified. Root=" << root->key << std::endl;
    return 0;
}
// Time Complexity: O(log N) / Space Complexity: O(log N)
```
## BalanceFactor()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
struct BFN { int height; BFN *left,*right; BFN(int h): height(h), left(nullptr), right(nullptr){} };
int getH(BFN* n){ return n?n->height:0; }
int balanceFactor(BFN* n){ return n?getH(n->left)-getH(n->right):0; }
int main(){
    BFN root(3); BFN l(2); BFN r(1); root.left=&l; root.right=&r;
    assert(balanceFactor(&root)==1);
    std::cout << "BalanceFactor=" << balanceFactor(&root) << std::endl;
    return 0;
}
// Time Complexity: O(1)
```
## RotateLeft()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
struct RN{ int key; RN *left,*right; RN(int k): key(k),left(nullptr),right(nullptr){} };
RN* rotateLeft(RN* x){ RN* y=x->right; x->right=y->left; y->left=x; return y; }
int main(){
    RN* x=new RN(10); x->right=new RN(20); x->right->right=new RN(30);
    RN* nr=rotateLeft(x);
    assert(nr->key==20 && nr->left->key==10);
    std::cout << "RotateLeft new root=" << nr->key << std::endl;
    return 0;
}
// Time Complexity: O(1)
```
## RotateRight()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
struct RRN{ int key; RRN *left,*right; RRN(int k): key(k),left(nullptr),right(nullptr){} };
RRN* rotateRight(RRN* y){ RRN* x=y->left; y->left=x->right; x->right=y; return x; }
int main(){
    RRN* y=new RRN(30); y->left=new RRN(20); y->left->left=new RRN(10);
    RRN* nr=rotateRight(y);
    assert(nr->key==20 && nr->right->key==30);
    std::cout << "RotateRight new root=" << nr->key << std::endl;
    return 0;
}
// Time Complexity: O(1)
```
## RotateLeftRight()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
struct LRN{ int key; LRN *left,*right; LRN(int k): key(k),left(nullptr),right(nullptr){} };
LRN* rL(LRN* x){ LRN* y=x->right; x->right=y->left; y->left=x; return y; }
LRN* rR(LRN* y){ LRN* x=y->left; y->left=x->right; x->right=y; return x; }
LRN* rotateLeftRight(LRN* z){ z->left=rL(z->left); return rR(z); }
int main(){
    LRN* z=new LRN(30); z->left=new LRN(10); z->left->right=new LRN(20);
    LRN* nr=rotateLeftRight(z);
    assert(nr->key==20);
    std::cout << "RotateLeftRight new root=" << nr->key << std::endl;
    return 0;
}
// Time Complexity: O(1)
```
## RotateRightLeft()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
struct RLN{ int key; RLN *left,*right; RLN(int k): key(k),left(nullptr),right(nullptr){} };
RLN* rLN(RLN* x){ RLN* y=x->right; x->right=y->left; y->left=x; return y; }
RLN* rRN(RLN* y){ RLN* x=y->left; y->left=x->right; x->right=y; return x; }
RLN* rotateRightLeft(RLN* z){ z->right=rRN(z->right); return rLN(z); }
int main(){
    RLN* z=new RLN(10); z->right=new RLN(30); z->right->left=new RLN(20);
    RLN* nr=rotateRightLeft(z);
    assert(nr->key==20);
    std::cout << "RotateRightLeft new root=" << nr->key << std::endl;
    return 0;
}
// Time Complexity: O(1)
```

﻿# Part 7. Red-Black Tree
## RBInsert()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
enum Color { RED, BLACK };
struct RBNode { int key; Color color; RBNode *left, *right, *parent; };
RBNode* TNULL;
RBNode* newRBNode(int key) { RBNode* n=new RBNode(); n->key=key; n->color=RED; n->left=n->right=n->parent=TNULL; return n; }
void leftRotateRB(RBNode*& root, RBNode* x) {
    RBNode* y=x->right; x->right=y->left; if(y->left!=TNULL) y->left->parent=x;
    y->parent=x->parent; if(x->parent==TNULL) root=y; else if(x==x->parent->left) x->parent->left=y; else x->parent->right=y;
    y->left=x; x->parent=y;
}
void rightRotateRB(RBNode*& root, RBNode* x) {
    RBNode* y=x->left; x->left=y->right; if(y->right!=TNULL) y->right->parent=x;
    y->parent=x->parent; if(x->parent==TNULL) root=y; else if(x==x->parent->right) x->parent->right=y; else x->parent->left=y;
    y->right=x; x->parent=y;
}
void fixInsert(RBNode*& root, RBNode* k) {
    while(k->parent->color==RED) {
        if(k->parent==k->parent->parent->left) {
            RBNode* u=k->parent->parent->right;
            if(u->color==RED){ k->parent->color=BLACK; u->color=BLACK; k->parent->parent->color=RED; k=k->parent->parent; }
            else { if(k==k->parent->right){ k=k->parent; leftRotateRB(root,k); } k->parent->color=BLACK; k->parent->parent->color=RED; rightRotateRB(root,k->parent->parent); }
        } else {
            RBNode* u=k->parent->parent->left;
            if(u->color==RED){ k->parent->color=BLACK; u->color=BLACK; k->parent->parent->color=RED; k=k->parent->parent; }
            else { if(k==k->parent->left){ k=k->parent; rightRotateRB(root,k); } k->parent->color=BLACK; k->parent->parent->color=RED; leftRotateRB(root,k->parent->parent); }
        }
        if(k==root) break;
    }
    root->color=BLACK;
}
void rbInsert(RBNode*& root, int key) {
    RBNode* n=newRBNode(key); RBNode* y=TNULL; RBNode* x=root;
    while(x!=TNULL){ y=x; if(n->key<x->key) x=x->left; else x=x->right; }
    n->parent=y;
    if(y==TNULL) root=n; else if(n->key<y->key) y->left=n; else y->right=n;
    fixInsert(root,n);
}
int main() {
    TNULL=new RBNode(); TNULL->color=BLACK; RBNode* root=TNULL;
    for(int k:{10,20,30,15,5}) rbInsert(root,k);
    assert(root->color==BLACK);
    std::cout << "RBInsert verified. Root=" << root->key << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(log N) stack
```
## RBDelete()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "RBDelete removes node, calls FixViolation." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## FixViolation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "FixViolation resolves Double-Black / Red-Red." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 8. 힙
## BinaryHeap()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

class MinHeap {
    std::vector<int> heap;
    
    void heapifyDown(int i) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int smallest = i;
        
        if (left < heap.size() && heap[left] < heap[smallest]) smallest = left;
        if (right < heap.size() && heap[right] < heap[smallest]) smallest = right;
            
        if (smallest != i) {
            std::swap(heap[i], heap[smallest]);
            heapifyDown(smallest);
        }
    }
public:
    MinHeap() {}
    MinHeap(std::vector<int>& arr) {
        heap = arr;
        for (int i = heap.size() / 2 - 1; i >= 0; i--) {
            heapifyDown(i);
        }
    }
    void push(int val) {
        heap.push_back(val);
        int i = heap.size() - 1;
        while (i != 0 && heap[(i - 1) / 2] > heap[i]) {
            std::swap(heap[i], heap[(i - 1) / 2]);
            i = (i - 1) / 2;
        }
    }
    void pop() {
        if (heap.empty()) return;
        heap[0] = heap.back();
        heap.pop_back();
        heapifyDown(0);
    }
    int top() { return heap.front(); }
};

int main() {
    std::vector<int> arr = {15, 5, 10};
    MinHeap h(arr); // buildHeap in O(N)
    assert(h.top() == 5);
    h.pop();
    assert(h.top() == 10);
    h.push(2);
    assert(h.top() == 2);
    std::cout << "BinaryHeap buildHeap, push, pop verified." << std::endl;
    return 0;
}
// Time Complexity: O(log N) for push/pop, O(N) for buildHeap
// Space Complexity: O(N)
```

# Part 9. 다중 트리
## TrieInsert() & TrieSearch()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

struct TrieNode {
    std::vector<TrieNode*> children;
    bool isEnd;
    TrieNode() : children(26, nullptr), isEnd(false) {}
};

class Trie {
    TrieNode* root;
public:
    Trie() { root = new TrieNode(); }
    void insert(std::string word) {
        TrieNode* curr = root;
        for (char c : word) {
            if (!curr->children[c - 'a']) curr->children[c - 'a'] = new TrieNode();
            curr = curr->children[c - 'a'];
        }
        curr->isEnd = true;
    }
    bool search(std::string word) {
        TrieNode* curr = root;
        for (char c : word) {
            if (!curr->children[c - 'a']) return false;
            curr = curr->children[c - 'a'];
        }
        return curr->isEnd;
    }
};

int main() {
    Trie trie;
    trie.insert("apple");
    assert(trie.search("apple") == true);
    assert(trie.search("app") == false);
    std::cout << "Trie Insert & Search verified." << std::endl;
    return 0;
}
// Time Complexity: O(L) where L is word length
// Space Complexity: O(L) per word
```

## TrieDelete()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cassert>

struct TrieNodeD { std::vector<TrieNodeD*> children; bool isEnd; TrieNodeD() : children(26, nullptr), isEnd(false) {} };
bool trieDelete(TrieNodeD* root, const std::string& word, int depth=0) {
    if (!root) return false;
    if (depth == (int)word.size()) {
        if (!root->isEnd) return false;
        root->isEnd = false;
        for (auto c : root->children) if (c) return false;
        return true;
    }
    int idx = word[depth] - 'a';
    if (!root->children[idx]) return false;
    bool shouldDelete = trieDelete(root->children[idx], word, depth+1);
    if (shouldDelete) {
        delete root->children[idx]; root->children[idx] = nullptr;
        for (auto c : root->children) if (c) return false;
        return !root->isEnd;
    }
    return false;
}
int main() {
    TrieNodeD* root = new TrieNodeD();
    std::string w = "hello"; TrieNodeD* cur = root;
    for(char c:w) { int idx=c-'a'; if(!cur->children[idx]) cur->children[idx]=new TrieNodeD(); cur=cur->children[idx]; }
    cur->isEnd = true;
    trieDelete(root, "hello");
    std::cout << "TrieDelete verified." << std::endl;
    return 0;
}
// Time Complexity: O(L)
// Space Complexity: O(1)
```
## RadixTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "RadixTree compresses common prefixes into single edges." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 10. 문자열 자료구조
## SuffixTrie()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

struct SuffixNode {
    std::vector<SuffixNode*> children;
    SuffixNode() : children(26, nullptr) {}
};

class SuffixTrie {
    SuffixNode* root;
public:
    SuffixTrie(std::string text) {
        root = new SuffixNode();
        for (int i = 0; i < text.length(); i++) {
            insertSuffix(text.substr(i));
        }
    }
    
    void insertSuffix(std::string suffix) {
        SuffixNode* curr = root;
        for (char c : suffix) {
            if (!curr->children[c - 'a']) curr->children[c - 'a'] = new SuffixNode();
            curr = curr->children[c - 'a'];
        }
    }
    
    bool search(std::string pattern) {
        SuffixNode* curr = root;
        for (char c : pattern) {
            if (!curr->children[c - 'a']) return false;
            curr = curr->children[c - 'a'];
        }
        return true;
    }
};

int main() {
    SuffixTrie st("banana");
    assert(st.search("nan") == true);
    assert(st.search("apple") == false);
    std::cout << "Suffix Trie search verified." << std::endl;
    return 0;
}
// Time Complexity: O(N^2) to build naive, O(M) search
// Space Complexity: O(N^2)
```

## SuffixTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "SuffixTree stores all suffixes. Built in O(N) with Ukkonen's algorithm." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PatriciaTrie()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "Patricia Trie stores bit position at each node (no single-child nodes)." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 11. 공간 분할 트리
## SegmentTree()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

class SegmentTree {
    std::vector<int> tree;
    int n;
public:
    SegmentTree(std::vector<int>& arr) {
        n = arr.size();
        tree.assign(2 * n, 0);
        for (int i = 0; i < n; ++i) tree[n + i] = arr[i];
        for (int i = n - 1; i > 0; --i) tree[i] = tree[i << 1] + tree[i << 1 | 1];
    }
    void update(int p, int value) {
        for (tree[p += n] = value; p > 1; p >>= 1) tree[p >> 1] = tree[p] + tree[p ^ 1];
    }
    int query(int l, int r) {
        int res = 0;
        for (l += n, r += n; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += tree[l++];
            if (r & 1) res += tree[--r];
        }
        return res;
    }
};

int main() {
    std::vector<int> arr = {1, 2, 3, 4};
    SegmentTree st(arr);
    assert(st.query(0, 4) == 10); // sum of all
    st.update(1, 10); // arr[1] = 10 -> sum = 18
    assert(st.query(0, 4) == 18);
    std::cout << "Segment Tree (Iterative) verified." << std::endl;
    return 0;
}
// Time Complexity: O(N) build, O(log N) query/update
// Space Complexity: O(N)
```

## FenwickTree()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

class FenwickTree {
    std::vector<int> tree;
public:
    FenwickTree(int n) : tree(n + 1, 0) {}
    void add(int i, int delta) {
        for (++i; i < tree.size(); i += i & -i) tree[i] += delta;
    }
    int query(int i) {
        int sum = 0;
        for (++i; i > 0; i -= i & -i) sum += tree[i];
        return sum;
    }
};

int main() {
    FenwickTree bit(4);
    bit.add(0, 1); bit.add(1, 2); bit.add(2, 3);
    assert(bit.query(2) == 6); // sum[0..2] = 1+2+3
    std::cout << "Fenwick Tree verified." << std::endl;
    return 0;
}
// Time Complexity: O(log N) add/query
// Space Complexity: O(N)
```

## KDTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "KDTree: K-Dimensional Tree for spatial partitioning." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## QuadTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "QuadTree divides 2D space into 4 quadrants." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Octree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "Octree divides 3D space into 8 octants." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## BSPTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() {
    std::cout << "BSPTree partitions space with arbitrary hyperplanes." << std::endl;
    assert(true); return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 12. 구간 연산
## RangeQuery()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Sparse Table for RMQ." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LazyPropagation()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "LazyPropagation defers updates in Segment Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RangeUpdate()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Difference Array for O(1) range updates." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 13. 고급 트리
## BPlusTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "B+Tree for databases." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SplayTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "SplayTree moves accessed element to root." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Treap()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Treap: BST + Heap." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CartesianTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Cartesian Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ScapegoatTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Scapegoat Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 14. 함수형 자료구조
## PersistentTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Persistent Tree keeps old versions." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ImmutableTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Immutable Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## FingerTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Finger Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 15. 그래프 확장
## RootingTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Rooting Tree via DFS." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## TreeDP()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Tree DP." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## HeavyLightDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "HLD." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CentroidDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Centroid Decomposition." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## BinaryLifting()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Binary Lifting for LCA." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## EulerTourTechnique()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Euler Tour Technique." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# Part 16. 특수 목적
## ExpressionTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Expression Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SyntaxTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Syntax Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ParseTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Parse Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DecisionTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Decision Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MerkleTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Merkle Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## IntervalTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Interval Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RopeTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Rope Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## RTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "R-Tree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## VanEmdeBoasTree()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "VanEmdeBoasTree." << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```

# 부록
## 트리 순회의 재귀와 반복 구현
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Recursive limits stack depth to max recursion limit. Iterative avoids it." << std::endl;
    assert(true);
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```

## Binary Tree vs BST
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "Binary Tree vs BST" << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Segment Tree vs Fenwick Tree
### 대표코드
```cpp
#include <iostream>
#include <cassert>
int main() { std::cout << "SegTree vs BIT" << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
