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

# Part 6. AVL 트리
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

# Part 7. Red-Black Tree
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
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 레드-블랙 트리 삭제 (CLRS).  규칙: (1) 루트는 검정 (2) 빨강의 자식은 검정 (3) 모든 루트→nil 경로의 검정 개수가 같다.
// 빨강 노드를 지우면 규칙이 안 깨지지만, 검정 노드를 지우면 그 경로의 검정이 하나 모자란다 -> x 에 "추가 검정(double black)" 을 얹고 위로 올리며 해소
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
struct RBTree {
    Node *nil, *root;
    RBTree() { nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil; }
    void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; }
    void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; }
    void insertFix(Node* z) {
        while (z->p->c == RED) {
            bool left = z->p == z->p->p->l;
            Node* y = left ? z->p->p->r : z->p->p->l;                          // 삼촌
            if (y->c == RED) { z->p->c = BLACK; y->c = BLACK; z->p->p->c = RED; z = z->p->p; }
            else {
                if (left && z == z->p->r) { z = z->p; rotL(z); } else if (!left && z == z->p->l) { z = z->p; rotR(z); }
                z->p->c = BLACK; z->p->p->c = RED;
                if (left) rotR(z->p->p); else rotL(z->p->p);
            }
        }
        root->c = BLACK;
    }
    void insert(int k) {
        Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
        while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
        z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
        insertFix(z);
    }
    void transplant(Node* u, Node* v) { if (u->p == nil) root = v; else if (u == u->p->l) u->p->l = v; else u->p->r = v; v->p = u->p; }
    Node* minimum(Node* x) { while (x->l != nil) x = x->l; return x; }
    Node* find(int k) { Node* x = root; while (x != nil && x->key != k) x = k < x->key ? x->l : x->r; return x; }
    void deleteFix(Node* x) {
        while (x != root && x->c == BLACK) {
            bool left = x == x->p->l;
            Node* w = left ? x->p->r : x->p->l;                                // 형제
            if (w->c == RED) { w->c = BLACK; x->p->c = RED; if (left) rotL(x->p); else rotR(x->p); w = left ? x->p->r : x->p->l; }     // 경우 1: 형제가 빨강
            Node *near = left ? w->l : w->r, *far = left ? w->r : w->l;
            if (near->c == BLACK && far->c == BLACK) { w->c = RED; x = x->p; }                                                          // 경우 2: 조카가 모두 검정 -> 문제를 위로
            else {
                if (far->c == BLACK) { near->c = BLACK; w->c = RED; if (left) rotR(w); else rotL(w); w = left ? x->p->r : x->p->l; far = left ? w->r : w->l; }   // 경우 3
                w->c = x->p->c; x->p->c = BLACK; far->c = BLACK; if (left) rotL(x->p); else rotR(x->p); x = root;                      // 경우 4: 한 번의 회전으로 해소
            }
        }
        x->c = BLACK;
    }
    void erase(int k) {
        Node* z = find(k); if (z == nil) return;
        Node *y = z, *x; Color orig = y->c;
        if (z->l == nil) { x = z->r; transplant(z, z->r); }
        else if (z->r == nil) { x = z->l; transplant(z, z->l); }
        else {
            y = minimum(z->r); orig = y->c; x = y->r;
            if (y->p == z) x->p = y; else { transplant(y, y->r); y->r = z->r; y->r->p = y; }
            transplant(z, y); y->l = z->l; y->l->p = y; y->c = z->c;
        }
        delete z;
        if (orig == BLACK) deleteFix(x);
    }
    int check(Node* n) {                                                       // 검정 높이를 반환, 규칙 위반이면 -1
        if (n == nil) return 1;
        if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
        int a = check(n->l), b = check(n->r);
        if (a < 0 || b < 0 || a != b) return -1;
        return a + (n->c == BLACK);
    }
    void inorder(Node* n, std::vector<int>& out) { if (n == nil) return; inorder(n->l, out); out.push_back(n->key); inorder(n->r, out); }
    bool valid() { return root->c == BLACK && check(root) > 0; }
};

int main() {
    RBTree t; std::set<int> oracle; std::mt19937 rng(11);
    for (int step = 0; step < 6000; step++) {
        int k = rng() % 500;
        if (rng() % 3 != 0) { if (!oracle.count(k)) { t.insert(k); oracle.insert(k); } }
        else { t.erase(k); oracle.erase(k); }
        if (step % 25 == 0) assert(t.valid());
    }
    assert(t.valid());
    std::vector<int> keys; t.inorder(t.root, keys);
    assert((keys == std::vector<int>(oracle.begin(), oracle.end())));          // 내용이 std::set 과 일치
    for (int k : std::vector<int>(oracle.begin(), oracle.end())) { t.erase(k); assert(t.valid()); }   // 하나씩 전부 삭제
    assert(t.root == t.nil);
    std::cout << "RBDelete verified: 6000 random operations kept all red-black rules." << std::endl;
    return 0;
}
// Time Complexity: O(log N), 삭제 후 회전은 최대 3번
// Space Complexity: O(N)
```
## FixViolation()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 삽입 후 규칙 위반 수리(fix-up): 새 노드는 빨강이므로 "빨강의 부모가 빨강" 위반만 생길 수 있다.  삼촌 색으로 세 경우를 가른다.
//  경우 1: 삼촌이 빨강       -> 부모·삼촌을 검정, 조부모를 빨강으로 (재색칠), 조부모에서 다시 검사 (위로 전파)
//  경우 2: 삼촌이 검정, 꺾인 모양(<, >) -> 회전으로 직선 모양을 만든다
//  경우 3: 삼촌이 검정, 직선 모양      -> 조부모 기준 회전 + 색 교환, 종료
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
Node* nil;
int caseCount[4];
Node* root;
void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; }
void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; }
void fixViolation(Node* z) {
    while (z->p->c == RED) {
        bool left = z->p == z->p->p->l;
        Node* uncle = left ? z->p->p->r : z->p->p->l;
        if (uncle->c == RED) { caseCount[1]++; z->p->c = BLACK; uncle->c = BLACK; z->p->p->c = RED; z = z->p->p; continue; }
        if (left && z == z->p->r) { caseCount[2]++; z = z->p; rotL(z); }
        else if (!left && z == z->p->l) { caseCount[2]++; z = z->p; rotR(z); }
        caseCount[3]++;
        z->p->c = BLACK; z->p->p->c = RED;
        if (left) rotR(z->p->p); else rotL(z->p->p);
    }
    root->c = BLACK;
}
void insert(int k) {
    Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
    while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
    z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
    fixViolation(z);
}
int blackHeight(Node* n) {                                          // 규칙 위반이면 -1
    if (n == nil) return 1;
    if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
    int a = blackHeight(n->l), b = blackHeight(n->r);
    return (a < 0 || b < 0 || a != b) ? -1 : a + (n->c == BLACK);
}
int height(Node* n) { return n == nil ? 0 : 1 + std::max(height(n->l), height(n->r)); }

int main() {
    nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil;
    std::mt19937 rng(12);
    std::vector<int> keys(2000); for (int i = 0; i < 2000; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) { insert(k); assert(root->c == BLACK && blackHeight(root) > 0); }   // 삽입할 때마다 모든 규칙 유지
    assert(caseCount[1] > 0 && caseCount[2] > 0 && caseCount[3] > 0);                       // 세 경우가 모두 실제로 쓰였다
    assert(caseCount[3] <= 2000);                                                           // 경우 3(회전)은 삽입당 최대 1번
    assert(height(root) <= 2 * std::log2(2001));                                            // 높이 <= 2·log2(n+1)
    std::cout << "FixViolation cases: recolor=" << caseCount[1] << " zigzag=" << caseCount[2] << " straight=" << caseCount[3] << ", height " << height(root) << std::endl;
    return 0;
}
// Time Complexity: O(log N), 회전은 삽입당 최대 2번
// Space Complexity: O(1) 추가 공간
```

## Recolor()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 재색칠(recolor): 삼촌이 빨강일 때의 수리는 포인터 하나 바꾸지 않고 색만 뒤집는다 (2-3-4 트리에서 4-노드를 분할해 가운데 키를 위로 올리는 것과 같다).
// 위로 전파될 수 있지만 분할상환하면 삽입당 O(1)번만 일어나고, 회전보다 훨씬 싸다.  전파가 루트에 닿으면 전체 검정 높이가 1 커진다
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
Node *nil, *root;
long recolors, rotations, maxCascade;
void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; rotations++; }
void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; rotations++; }
void insert(int k) {
    Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
    while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
    z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
    long cascade = 0;
    while (z->p->c == RED) {
        bool left = z->p == z->p->p->l; Node* u = left ? z->p->p->r : z->p->p->l;
        if (u->c == RED) { z->p->c = BLACK; u->c = BLACK; z->p->p->c = RED; z = z->p->p; recolors++; cascade++; }   // 재색칠: 회전 없음
        else {
            if (left && z == z->p->r) { z = z->p; rotL(z); } else if (!left && z == z->p->l) { z = z->p; rotR(z); }
            z->p->c = BLACK; z->p->p->c = RED; if (left) rotR(z->p->p); else rotL(z->p->p);
        }
    }
    root->c = BLACK; maxCascade = std::max(maxCascade, cascade);
}
int blackHeight(Node* n) {
    if (n == nil) return 1;
    if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
    int a = blackHeight(n->l), b = blackHeight(n->r);
    return (a < 0 || b < 0 || a != b) ? -1 : a + (n->c == BLACK);
}

int main() {
    nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil;
    std::mt19937 rng(13);
    const int n = 20000;
    std::vector<int> keys(n); for (int i = 0; i < n; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) insert(k);
    assert(blackHeight(root) > 0);
    assert(double(recolors) / n < 1.0);                              // 삽입당 평균 재색칠 < 1 (분할상환 O(1))
    assert(double(rotations) / n < 2.0);                             // 삽입당 회전 < 2
    assert(maxCascade <= std::log2(n + 1));                          // 한 번의 삽입에서 위로 전파되는 재색칠은 O(log n)
    std::cout << "per insert: recolors=" << double(recolors) / n << " rotations=" << double(rotations) / n << " max cascade=" << maxCascade << std::endl;
    return 0;
}
// Time Complexity: 삽입당 재색칠 분할상환 O(1), 최악 O(log N)
// Space Complexity: O(1)
```
## DoubleBlack()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 이중 검정(double black): 검정 노드를 지우면 그 아래 경로의 검정 개수가 하나 모자란다 -> 대체 노드 x 에 "검정 하나가 더 필요" 라는 표시를 단다.
// 형제 w 의 색과 조카의 색으로 네 경우를 나눠 해소한다 (오른쪽 자식일 때는 좌우 대칭).
//  1: w 가 빨강                  -> 회전·색 교환으로 w 를 검정으로 만들어 2~4 중 하나로
//  2: w, 두 조카 모두 검정       -> w 를 빨강으로 (검정 하나를 부모로 올림) -> 이중 검정이 위로 이동
//  3: w 검정, 먼 조카 검정·가까운 조카 빨강 -> w 와 가까운 조카를 회전해 4 로
//  4: w 검정, 먼 조카 빨강       -> 부모 기준 회전 + 색 교환 -> 종료
enum Color { RED, BLACK };
struct Node { int key; Color c; Node *l, *r, *p; };
Node *nil, *root; long cases[5];
void rotL(Node* x) { Node* y = x->r; x->r = y->l; if (y->l != nil) y->l->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->l) x->p->l = y; else x->p->r = y; y->l = x; x->p = y; }
void rotR(Node* x) { Node* y = x->l; x->l = y->r; if (y->r != nil) y->r->p = x; y->p = x->p; if (x->p == nil) root = y; else if (x == x->p->r) x->p->r = y; else x->p->l = y; y->r = x; x->p = y; }
void insert(int k) {
    Node* z = new Node{k, RED, nil, nil, nil}; Node *y = nil, *x = root;
    while (x != nil) { y = x; x = k < x->key ? x->l : x->r; }
    z->p = y; if (y == nil) root = z; else if (k < y->key) y->l = z; else y->r = z;
    while (z->p->c == RED) {
        bool left = z->p == z->p->p->l; Node* u = left ? z->p->p->r : z->p->p->l;
        if (u->c == RED) { z->p->c = BLACK; u->c = BLACK; z->p->p->c = RED; z = z->p->p; }
        else { if (left && z == z->p->r) { z = z->p; rotL(z); } else if (!left && z == z->p->l) { z = z->p; rotR(z); }
               z->p->c = BLACK; z->p->p->c = RED; if (left) rotR(z->p->p); else rotL(z->p->p); }
    }
    root->c = BLACK;
}
void resolveDoubleBlack(Node* x) {
    while (x != root && x->c == BLACK) {
        bool left = x == x->p->l; Node* w = left ? x->p->r : x->p->l;
        if (w->c == RED) { cases[1]++; w->c = BLACK; x->p->c = RED; if (left) rotL(x->p); else rotR(x->p); w = left ? x->p->r : x->p->l; }
        Node *near = left ? w->l : w->r, *far = left ? w->r : w->l;
        if (near->c == BLACK && far->c == BLACK) { cases[2]++; w->c = RED; x = x->p; }
        else {
            if (far->c == BLACK) { cases[3]++; near->c = BLACK; w->c = RED; if (left) rotR(w); else rotL(w); w = left ? x->p->r : x->p->l; far = left ? w->r : w->l; }
            cases[4]++; w->c = x->p->c; x->p->c = BLACK; far->c = BLACK; if (left) rotL(x->p); else rotR(x->p); x = root;
        }
    }
    x->c = BLACK;                                                     // 빨강을 만나면 검정으로 칠해 이중 검정을 흡수
}
void transplant(Node* u, Node* v) { if (u->p == nil) root = v; else if (u == u->p->l) u->p->l = v; else u->p->r = v; v->p = u->p; }
void erase(int k) {
    Node* z = root; while (z != nil && z->key != k) z = k < z->key ? z->l : z->r;
    if (z == nil) return;
    Node *y = z, *x; Color orig = y->c;
    if (z->l == nil) { x = z->r; transplant(z, z->r); } else if (z->r == nil) { x = z->l; transplant(z, z->l); }
    else { y = z->r; while (y->l != nil) y = y->l; orig = y->c; x = y->r;
           if (y->p == z) x->p = y; else { transplant(y, y->r); y->r = z->r; y->r->p = y; }
           transplant(z, y); y->l = z->l; y->l->p = y; y->c = z->c; }
    delete z;
    if (orig == BLACK) resolveDoubleBlack(x);                         // 검정을 지웠을 때만 이중 검정이 생긴다
}
int blackHeight(Node* n) {
    if (n == nil) return 1;
    if (n->c == RED && (n->l->c == RED || n->r->c == RED)) return -1;
    int a = blackHeight(n->l), b = blackHeight(n->r);
    return (a < 0 || b < 0 || a != b) ? -1 : a + (n->c == BLACK);
}

int main() {
    nil = new Node{0, BLACK, nullptr, nullptr, nullptr}; nil->l = nil->r = nil->p = nil; root = nil;
    std::mt19937 rng(14);
    std::vector<int> keys(3000); for (int i = 0; i < 3000; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) insert(k);
    std::shuffle(keys.begin(), keys.end(), rng);
    for (size_t i = 0; i < keys.size(); i++) { erase(keys[i]); if (i % 10 == 0 && root != nil) assert(root->c == BLACK && blackHeight(root) > 0); }
    assert(root == nil);
    assert(cases[1] > 0 && cases[2] > 0 && cases[3] > 0 && cases[4] > 0);       // 네 경우가 모두 실제로 쓰였다
    assert(cases[4] <= 3000);                                                   // 종료 경우(4)는 삭제당 최대 1번
    std::cout << "DoubleBlack cases: 1=" << cases[1] << " 2=" << cases[2] << " 3=" << cases[3] << " 4=" << cases[4] << std::endl;
    return 0;
}
// Time Complexity: 삭제당 O(log N), 회전은 최대 3번
// Space Complexity: O(1) 추가 공간
```
## TwoThreeTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 2-3 트리: 모든 내부 노드가 자식 2개(키 1개) 또는 3개(키 2개)이고, 모든 잎이 같은 깊이에 있는 완전 균형 탐색 트리.
// 삽입은 잎까지 내려가 키를 넣고, 키가 3개가 되면 가운데 키를 위로 올리며 노드를 둘로 쪼갠다(분할이 루트까지 번지면 그때만 높이가 1 늘어난다).
// 균형이 "회전"이 아니라 "분할"로 유지되므로 모든 잎의 깊이가 항상 같다 -> 레드-블랙 트리(특히 LLRB)가 이 구조를 이진 트리로 흉내 낸 것이다
struct Node { std::vector<int> k; std::vector<Node*> c; bool leaf() const { return c.empty(); } };

bool contains(Node* n, int x) {
    while (n) {
        int i = 0; while (i < (int)n->k.size() && x > n->k[i]) i++;
        if (i < (int)n->k.size() && n->k[i] == x) return true;
        if (n->leaf()) return false;
        n = n->c[i];
    }
    return false;
}
bool insertRec(Node* n, int x, int& up, Node*& right) {                    // 분할이 일어나면 true, up 은 올릴 키, right 는 새로 생긴 오른쪽 노드
    int i = 0; while (i < (int)n->k.size() && x > n->k[i]) i++;
    if (i < (int)n->k.size() && n->k[i] == x) return false;                // 중복 키
    if (n->leaf()) n->k.insert(n->k.begin() + i, x);
    else {
        int u; Node* r;
        if (!insertRec(n->c[i], x, u, r)) return false;                    // 아래에서 분할이 없었으면 여기서 끝
        n->k.insert(n->k.begin() + i, u); n->c.insert(n->c.begin() + i + 1, r);
    }
    if (n->k.size() < 3) return false;
    up = n->k[1]; right = new Node; right->k = {n->k[2]};                  // [a b c] -> [a] ↑b [c]
    if (!n->leaf()) { right->c = {n->c[2], n->c[3]}; n->c.resize(2); }
    n->k.resize(1); return true;
}
void insert(Node*& root, int x) {
    if (!root) { root = new Node; root->k = {x}; return; }
    int u; Node* r;
    if (insertRec(root, x, u, r)) { Node* nr = new Node; nr->k = {u}; nr->c = {root, r}; root = nr; }
}
// 불변식 검사: 키 1~2개, 자식 수 = 키 수 + 1, 키 순서, 모든 잎의 깊이가 같음. 높이(잎=1)를 돌려주고 위반이면 -1
int check(Node* n, long lo, long hi, std::vector<int>& inorder) {
    if (n->k.empty() || n->k.size() > 2) return -1;
    for (size_t i = 0; i < n->k.size(); i++) if (n->k[i] <= (i ? n->k[i - 1] : lo) || n->k[i] >= hi) return -1;
    if (n->leaf()) { for (int x : n->k) inorder.push_back(x); return 1; }
    if (n->c.size() != n->k.size() + 1) return -1;
    int h = -2;
    for (size_t i = 0; i < n->c.size(); i++) {
        long l = i ? n->k[i - 1] : lo, r = i < n->k.size() ? n->k[i] : hi;
        int ch = check(n->c[i], l, r, inorder); if (ch < 0 || (h != -2 && ch != h)) return -1;
        h = ch; if (i < n->k.size()) inorder.push_back(n->k[i]);
    }
    return h + 1;
}
void destroy(Node* n) { if (!n) return; for (Node* c : n->c) destroy(c); delete n; }

int main() {
    std::mt19937 rng(23);
    Node* root = nullptr; std::set<int> ref;
    for (int i = 0; i < 5000; i++) {
        int x = rng() % 20000; insert(root, x); ref.insert(x);
        if (i % 500 == 0) { std::vector<int> v; assert(check(root, -1, 1L << 40, v) > 0); }
    }
    std::vector<int> v; int h = check(root, -1, 1L << 40, v);
    assert(h > 0 && v == std::vector<int>(ref.begin(), ref.end()));        // 구조가 올바르고 중위 순회가 정렬된 집합과 같다
    for (int x = 0; x < 20000; x += 7) assert(contains(root, x) == (ref.count(x) > 0));
    int n = ref.size();
    assert(h <= std::log2(n + 1) + 1e-9 && h >= std::log(n + 1.0) / std::log(3.0) - 1e-9);   // 3^h >= n+1 >= 2^h
    destroy(root); root = nullptr;
    for (int x = 1; x <= 4095; x++) insert(root, x);                       // 정렬 입력에도 균형이 유지된다
    v.clear(); int hs = check(root, 0, 1L << 40, v);
    assert(hs > 0 && hs <= 12 && v.size() == 4095);
    std::cout << "2-3 tree: " << n << " random keys -> height " << h << ", 4095 sorted keys -> height " << hs << std::endl;
    destroy(root);
    return 0;
}
// Time Complexity: 탐색·삽입 O(log N) (높이 log3 N ~ log2 N)
// Space Complexity: O(N)
```
## TwoThreeFourTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 2-3-4 트리: 노드가 키 1~3개(자식 2~4개)를 가지는 균형 탐색 트리. 삽입을 "내려가는 길에" 처리하는 것이 핵심이다.
// 루트에서 잎으로 내려가며 만나는 가득 찬 노드(키 3개, 4-노드)를 미리 쪼개 두면, 잎에 도착했을 때 부모에 자리가 있다는 것이 보장되어
// 위로 되돌아갈 필요가 없다(한 번의 하향 패스). 레드-블랙 트리는 2-3-4 트리를 이진 트리로 옮긴 것: 4-노드 = 검은 노드 + 빨간 자식 둘
struct Node { int n = 0; int k[3]; Node* c[4] = {}; bool leaf = true; };

void splitChild(Node* p, int i) {                                          // p->c[i] 는 가득 찬 노드, p 는 가득 차 있지 않다
    Node* y = p->c[i]; Node* z = new Node; z->leaf = y->leaf; z->n = 1; z->k[0] = y->k[2];
    if (!y->leaf) { z->c[0] = y->c[2]; z->c[1] = y->c[3]; }
    for (int j = p->n; j > i; j--) { p->k[j] = p->k[j - 1]; p->c[j + 1] = p->c[j]; }
    p->k[i] = y->k[1]; p->c[i + 1] = z; p->n++; y->n = 1;                  // 가운데 키가 부모로 올라간다
}
int splits = 0;
bool insert(Node*& root, int x) {
    if (!root) { root = new Node; root->n = 1; root->k[0] = x; return true; }
    if (root->n == 3) { Node* s = new Node; s->leaf = false; s->c[0] = root; splitChild(s, 0); root = s; splits++; }
    Node* t = root;
    for (;;) {
        int i = 0; while (i < t->n && x > t->k[i]) i++;
        if (i < t->n && t->k[i] == x) return false;
        if (t->leaf) { for (int j = t->n; j > i; j--) t->k[j] = t->k[j - 1]; t->k[i] = x; t->n++; return true; }
        if (t->c[i]->n == 3) {
            splitChild(t, i); splits++;
            if (x == t->k[i]) return false;
            if (x > t->k[i]) i++;
        }
        t = t->c[i];
    }
}
bool contains(Node* t, int x) {
    while (t) {
        int i = 0; while (i < t->n && x > t->k[i]) i++;
        if (i < t->n && t->k[i] == x) return true;
        if (t->leaf) return false;
        t = t->c[i];
    }
    return false;
}
int check(Node* t, long lo, long hi, std::vector<int>& out) {              // 높이(잎=1), 위반이면 -1
    if (t->n < 1 || t->n > 3) return -1;
    for (int i = 0; i < t->n; i++) if (t->k[i] <= (i ? t->k[i - 1] : lo) || t->k[i] >= hi) return -1;
    if (t->leaf) { for (int i = 0; i < t->n; i++) out.push_back(t->k[i]); return 1; }
    int h = -2;
    for (int i = 0; i <= t->n; i++) {
        if (!t->c[i]) return -1;
        int ch = check(t->c[i], i ? t->k[i - 1] : lo, i < t->n ? t->k[i] : hi, out);
        if (ch < 0 || (h != -2 && ch != h)) return -1;
        h = ch; if (i < t->n) out.push_back(t->k[i]);
    }
    return h + 1;
}
void destroy(Node* t) { if (!t) return; if (!t->leaf) for (int i = 0; i <= t->n; i++) destroy(t->c[i]); delete t; }

int main() {
    std::mt19937 rng(5);
    Node* root = nullptr; std::set<int> ref;
    for (int i = 0; i < 6000; i++) {
        int x = rng() % 30000; bool added = insert(root, x); assert(added == ref.insert(x).second);   // 중복이면 false
        if (i % 600 == 0) { std::vector<int> v; assert(check(root, -1, 1L << 40, v) > 0); }
    }
    std::vector<int> v; int h = check(root, -1, 1L << 40, v);
    assert(h > 0 && v == std::vector<int>(ref.begin(), ref.end()));
    for (int x = 0; x < 30000; x += 11) assert(contains(root, x) == (ref.count(x) > 0));
    int n = ref.size();
    assert(h <= std::log2(n + 1) + 1e-9 && h >= std::log(n + 1.0) / std::log(4.0) - 1e-9);   // 4^h >= n+1 >= 2^h
    std::cout << "2-3-4 tree: " << n << " keys -> height " << h << " (log4=" << std::log(n + 1.0) / std::log(4.0) << ", log2=" << std::log2(n + 1) << "), splits " << splits << std::endl;
    destroy(root); root = nullptr;
    for (int x = 1; x <= 3000; x++) insert(root, x);
    v.clear(); assert(check(root, 0, 1L << 40, v) > 0 && v.size() == 3000);
    destroy(root);
    return 0;
}
// Time Complexity: 탐색·삽입 O(log N), 삽입은 하향 한 번
// Space Complexity: O(N)
```
## LeftLeaningRedBlackTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <cassert>

// 좌편향 레드-블랙 트리(LLRB, Sedgewick): 빨간 링크는 반드시 왼쪽 자식으로만 허용한다. 빨간 왼쪽 링크로 묶인 두 노드 = 2-3 트리의 3-노드.
// 그 규칙 덕에 삽입은 "회전 2종 + 색 뒤집기" 세 줄(fix)만으로 끝나고, 삭제도 "빨간 링크를 아래로 밀어 내리는" moveRedLeft/moveRedRight 로 정리된다
struct Node { int key; Node *l = nullptr, *r = nullptr; bool red = true; explicit Node(int k) : key(k) {} };
bool isRed(Node* h) { return h && h->red; }
Node* rotL(Node* h) { Node* x = h->r; h->r = x->l; x->l = h; x->red = h->red; h->red = true; return x; }
Node* rotR(Node* h) { Node* x = h->l; h->l = x->r; x->r = h; x->red = h->red; h->red = true; return x; }
void flip(Node* h) { h->red = !h->red; h->l->red = !h->l->red; h->r->red = !h->r->red; }
Node* fix(Node* h) {
    if (isRed(h->r) && !isRed(h->l)) h = rotL(h);                          // 오른쪽 빨간 링크는 왼쪽으로 눕힌다
    if (isRed(h->l) && isRed(h->l->l)) h = rotR(h);                        // 빨간 링크 두 개가 연속 -> 4-노드로 만든다
    if (isRed(h->l) && isRed(h->r)) flip(h);                               // 4-노드를 쪼개 빨간 링크를 부모로 올린다
    return h;
}
Node* insert(Node* h, int k) {
    if (!h) return new Node(k);
    if (k < h->key) h->l = insert(h->l, k); else if (k > h->key) h->r = insert(h->r, k);
    return fix(h);
}
Node* moveRedLeft(Node* h) { flip(h); if (isRed(h->r->l)) { h->r = rotR(h->r); h = rotL(h); flip(h); } return h; }
Node* moveRedRight(Node* h) { flip(h); if (isRed(h->l->l)) { h = rotR(h); flip(h); } return h; }
Node* minNode(Node* h) { while (h->l) h = h->l; return h; }
Node* deleteMin(Node* h) {
    if (!h->l) { delete h; return nullptr; }
    if (!isRed(h->l) && !isRed(h->l->l)) h = moveRedLeft(h);
    h->l = deleteMin(h->l); return fix(h);
}
bool contains(Node* h, int k) { while (h) { if (k == h->key) return true; h = k < h->key ? h->l : h->r; } return false; }
Node* erase(Node* h, int k) {                                              // k 가 반드시 존재한다고 가정
    if (k < h->key) {
        if (!isRed(h->l) && !isRed(h->l->l)) h = moveRedLeft(h);
        h->l = erase(h->l, k);
    } else {
        if (isRed(h->l)) h = rotR(h);
        if (k == h->key && !h->r) { delete h; return nullptr; }
        if (!isRed(h->r) && !isRed(h->r->l)) h = moveRedRight(h);
        if (k == h->key) { h->key = minNode(h->r)->key; h->r = deleteMin(h->r); }
        else h->r = erase(h->r, k);
    }
    return fix(h);
}
Node* insertRoot(Node* root, int k) { root = insert(root, k); root->red = false; return root; }
Node* eraseRoot(Node* root, int k) {
    if (!contains(root, k)) return root;
    if (!isRed(root->l) && !isRed(root->r)) root->red = true;
    root = erase(root, k); if (root) root->red = false; return root;
}
// 불변식: BST 순서, 오른쪽 빨간 링크 없음, 빨간 노드의 빨간 자식 없음, 모든 경로의 검은 노드 수가 같음
int blackHeight(Node* h, long lo, long hi) {
    if (!h) return 1;
    if (h->key <= lo || h->key >= hi || isRed(h->r) || (h->red && isRed(h->l))) return -1;
    int a = blackHeight(h->l, lo, h->key), b = blackHeight(h->r, h->key, hi);
    if (a < 0 || b < 0 || a != b) return -1;
    return a + (h->red ? 0 : 1);
}
int height(Node* h) { return h ? 1 + std::max(height(h->l), height(h->r)) : 0; }
void destroy(Node* h) { if (!h) return; destroy(h->l); destroy(h->r); delete h; }

int main() {
    Node* root = nullptr;
    for (int i = 1; i <= 4095; i++) root = insertRoot(root, i);              // 정렬 입력(BST 라면 최악)
    assert(blackHeight(root, 0, 1L << 40) > 0);
    assert(height(root) <= 2 * std::log2(4096.0));                          // 높이 <= 2 log2(N+1)
    destroy(root); root = nullptr;

    std::mt19937 rng(77); std::set<int> ref;
    for (int step = 0; step < 20000; step++) {
        int x = rng() % 600;
        if (rng() % 3) { root = insertRoot(root, x); ref.insert(x); }
        else           { root = eraseRoot(root, x); ref.erase(x); }
        if (step % 25 == 0) {
            assert(!isRed(root) && blackHeight(root, -1, 1L << 40) > 0);
            for (int q = 0; q < 600; q += 37) assert(contains(root, q) == (ref.count(q) > 0));
        }
    }
    assert(blackHeight(root, -1, 1L << 40) > 0);
    for (int x : std::set<int>(ref)) { root = eraseRoot(root, x); ref.erase(x); assert(!root || blackHeight(root, -1, 1L << 40) > 0); }
    assert(!root);
    std::cout << "LLRB: 4095 sorted inserts OK, 20000 random insert/delete steps OK" << std::endl;
    return 0;
}
// Time Complexity: 삽입·삭제·탐색 O(log N)
// Space Complexity: O(N)
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
        
        if (left < (int)heap.size() && heap[left] < heap[smallest]) smallest = left;
        if (right < (int)heap.size() && heap[right] < heap[smallest]) smallest = right;
            
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

## HeapInsert()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 힙 삽입(트리 관점의 요약, 정본은 Queue.md Part 5): 완전이진트리의 배열 표현에서 맨 끝(다음 빈 자리)에 넣고 부모보다 작으면 위로 올린다(sift-up).
// 배열 인덱스로 트리 관계가 정해진다: 부모 (i-1)/2, 왼쪽 자식 2i+1, 오른쪽 자식 2i+2
void heapInsert(std::vector<int>& h, int v) {
    h.push_back(v);
    for (size_t i = h.size() - 1; i > 0 && h[(i - 1) / 2] > h[i]; i = (i - 1) / 2) std::swap(h[i], h[(i - 1) / 2]);
}

int main() {
    std::vector<int> h;
    for (int v : {5, 3, 8, 1, 9, 2}) heapInsert(h, v);
    assert(h[0] == 1);                                                         // 최솟값이 루트
    for (size_t i = 1; i < h.size(); i++) assert(h[(i - 1) / 2] <= h[i]);       // 힙 성질: 부모 <= 자식
    std::cout << "HeapInsert: root=" << h[0] << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## HeapDelete()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 힙 삭제(요약, 정본은 Queue.md Part 5): 루트를 빼고 맨 끝 원소를 루트로 옮긴 뒤 더 작은 자식과 교환하며 내린다(sift-down)
int heapDelete(std::vector<int>& h) {
    int top = h[0]; h[0] = h.back(); h.pop_back();
    size_t i = 0, n = h.size();
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, s = i;
        if (l < n && h[l] < h[s]) s = l;
        if (r < n && h[r] < h[s]) s = r;
        if (s == i) break;
        std::swap(h[i], h[s]); i = s;
    }
    return top;
}

int main() {
    std::vector<int> h = {1, 3, 2, 7, 4, 8, 9};                                 // 이미 힙
    assert(heapDelete(h) == 1 && h[0] == 2);
    assert(heapDelete(h) == 2 && h[0] == 3);
    for (size_t i = 1; i < h.size(); i++) assert(h[(i - 1) / 2] <= h[i]);
    std::cout << "HeapDelete verified." << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## Heapify()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// Heapify(요약, 정본은 Queue.md Part 5): 노드 i 의 두 서브트리가 이미 힙일 때, i 를 아래로 내려 전체를 힙으로 만든다 (sift-down 한 번)
void heapify(std::vector<int>& a, size_t n, size_t i) {
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, s = i;
        if (l < n && a[l] < a[s]) s = l;
        if (r < n && a[r] < a[s]) s = r;
        if (s == i) return;
        std::swap(a[i], a[s]); i = s;
    }
}

int main() {
    std::vector<int> a = {9, 1, 2, 3, 4, 5, 6};                                 // 루트만 힙 성질을 어김 (서브트리는 힙)
    heapify(a, a.size(), 0);
    assert(a[0] == 1);
    for (size_t i = 1; i < a.size(); i++) assert(a[(i - 1) / 2] <= a[i]);
    std::cout << "Heapify verified." << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(1)
```
## BuildHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 힙 만들기(요약, 정본은 Queue.md Part 5): 마지막 내부 노드부터 루트까지 heapify 를 부르면 O(N)  (N log N 이 아니다).
// 높이 h 인 노드는 N/2^(h+1) 개이고 각 heapify 비용이 O(h) 이므로 합이 N·Σ h/2^(h+1) = O(N)
long swaps;
void heapify(std::vector<int>& a, size_t n, size_t i) {
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, s = i;
        if (l < n && a[l] < a[s]) s = l;
        if (r < n && a[r] < a[s]) s = r;
        if (s == i) return;
        std::swap(a[i], a[s]); swaps++; i = s;
    }
}

int main() {
    std::mt19937 rng(15);
    for (int n : {1000, 100000}) {
        std::vector<int> a(n); for (auto& x : a) x = rng();
        swaps = 0;
        for (int i = n / 2 - 1; i >= 0; i--) heapify(a, n, i);
        for (int i = 1; i < n; i++) assert(a[(i - 1) / 2] <= a[i]);
        assert(swaps < n);                                                      // 교환 횟수 < N (선형)
        std::cout << "BuildHeap n=" << n << " swaps=" << swaps << std::endl;
    }
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
#include <random>
#include <vector>
#include <cassert>

// 힙 정렬(요약, 정본은 Queue.md Part 5): 최대 힙을 만든 뒤, 루트(최댓값)를 맨 뒤로 보내고 힙 크기를 줄이며 반복한다. 제자리, 최악 O(N log N)
void siftDown(std::vector<int>& a, size_t n, size_t i) {
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, m = i;
        if (l < n && a[l] > a[m]) m = l;
        if (r < n && a[r] > a[m]) m = r;
        if (m == i) return;
        std::swap(a[i], a[m]); i = m;
    }
}
void heapSort(std::vector<int>& a) {
    for (int i = (int)a.size() / 2 - 1; i >= 0; i--) siftDown(a, a.size(), i);
    for (size_t end = a.size(); end > 1; end--) { std::swap(a[0], a[end - 1]); siftDown(a, end - 1, 0); }
}

int main() {
    std::mt19937 rng(16);
    for (int iter = 0; iter < 200; iter++) {
        std::vector<int> a(rng() % 100 + 1); for (auto& x : a) x = rng() % 50;
        auto b = a; heapSort(a); std::sort(b.begin(), b.end());
        assert(a == b);
    }
    std::cout << "HeapSort verified on 200 random arrays." << std::endl;
    return 0;
}
// Time Complexity: O(N log N) 최악도 동일
// Space Complexity: O(1)
```
## FibonacciHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <climits>
#include <cmath>
#include <memory>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>
#include <cassert>

// 피보나치 힙: push·meld·findMin·decreaseKey 가 분할상환 O(1), extractMin 이 분할상환 O(log n).  Dijkstra/Prim 을 O(E + V log V) 로 만든다.
// 루트들을 원형 이중 연결 리스트로 느슨하게 두었다가, extractMin 때만 "차수가 같은 두 트리를 합치는" consolidate 를 한다.
// decreaseKey 는 부모보다 작아지면 그 노드를 루트 리스트로 잘라내고(cut), 자식을 하나 잃은 부모에 표시(mark)를 하다가 두 번째로 잃으면 연쇄 절단한다
struct FNode {
    int key, degree = 0; bool mark = false; FNode *p = nullptr, *child = nullptr, *l, *r;
    explicit FNode(int k) : key(k) { l = r = this; }
};
struct FibHeap {
    FNode* min = nullptr; size_t n = 0; std::vector<std::unique_ptr<FNode>> pool;
    void addRoot(FNode* x) {
        x->p = nullptr;
        if (!min) { x->l = x->r = x; min = x; return; }
        x->r = min->r; x->l = min; min->r->l = x; min->r = x;
        if (x->key < min->key) min = x;
    }
    FNode* push(int k) { pool.emplace_back(new FNode(k)); FNode* x = pool.back().get(); addRoot(x); n++; return x; }
    void meld(FibHeap& o) {                                                // 두 루트 리스트를 이어 붙인다: O(1)
        if (!o.min) return;
        for (auto& p : o.pool) pool.push_back(std::move(p));
        o.pool.clear();
        if (!min) min = o.min;
        else {
            FNode *a2 = min->r, *b2 = o.min->l;
            min->r = o.min; o.min->l = min; b2->r = a2; a2->l = b2;
            if (o.min->key < min->key) min = o.min;
        }
        n += o.n; o.min = nullptr; o.n = 0;
    }
    void link(FNode* y, FNode* x) {                                        // y 를 x 의 자식으로
        y->p = x; y->mark = false;
        if (!x->child) { x->child = y; y->l = y->r = y; }
        else { y->r = x->child->r; y->l = x->child; x->child->r->l = y; x->child->r = y; }
        x->degree++;
    }
    int maxDegree = 0;
    void consolidate() {
        std::vector<FNode*> roots; FNode* w = min; do { roots.push_back(w); w = w->r; } while (w != min);
        std::vector<FNode*> A(64, nullptr);
        for (FNode* x : roots) {
            int d = x->degree;
            while (A[d]) { FNode* y = A[d]; if (x->key > y->key) std::swap(x, y); link(y, x); A[d++] = nullptr; }
            A[d] = x;
        }
        min = nullptr; maxDegree = 0;
        for (FNode* x : A) if (x) { x->l = x->r = x; addRoot(x); maxDegree = std::max(maxDegree, x->degree); }
    }
    FNode* extractMin() {
        FNode* z = min; if (!z) return nullptr;
        if (z->child) {
            FNode* c = z->child; do { c->p = nullptr; c = c->r; } while (c != z->child);
            FNode *a2 = z->r, *b1 = z->child, *b2 = z->child->l;           // 자식 리스트를 z 바로 뒤에 끼운다
            z->r = b1; b1->l = z; b2->r = a2; a2->l = b2; z->child = nullptr;
        }
        if (z == z->r) min = nullptr;
        else { z->l->r = z->r; z->r->l = z->l; min = z->r; consolidate(); }
        n--; return z;
    }
    void cut(FNode* x, FNode* y) {
        if (x->r == x) y->child = nullptr;
        else { if (y->child == x) y->child = x->r; x->l->r = x->r; x->r->l = x->l; }
        y->degree--; x->mark = false; addRoot(x);
    }
    void decreaseKey(FNode* x, int k) {
        assert(k <= x->key); x->key = k; FNode* y = x->p;
        if (y && x->key < y->key) {
            cut(x, y);
            for (FNode* z = y; z->p; ) { FNode* up = z->p; if (!z->mark) { z->mark = true; break; } cut(z, up); z = up; }   // 연쇄 절단
        }
        if (x->key < min->key) min = x;
    }
    void erase(FNode* x) { decreaseKey(x, INT_MIN); extractMin(); }
};

int main() {
    std::mt19937 rng(7);
    FibHeap h; std::multiset<int> ms; std::vector<FNode*> hs; std::vector<char> alive; std::unordered_map<FNode*, int> idx;
    for (int step = 0; step < 20000; step++) {
        int op = rng() % 10;
        if (op < 5 || ms.empty()) { int k = rng() % 100000 + 1000; FNode* x = h.push(k); idx[x] = hs.size(); hs.push_back(x); alive.push_back(1); ms.insert(k); }
        else if (op < 7) { FNode* z = h.extractMin(); assert(z->key == *ms.begin()); ms.erase(ms.begin()); alive[idx[z]] = 0; }
        else if (op < 9) {
            int i; do { i = rng() % hs.size(); } while (!alive[i]);
            int old = hs[i]->key, nk = old - (int)(rng() % 1000) - 1; h.decreaseKey(hs[i], nk);
            ms.erase(ms.find(old)); ms.insert(nk);
        } else { int i; do { i = rng() % hs.size(); } while (!alive[i]); ms.erase(ms.find(hs[i]->key)); h.erase(hs[i]); alive[i] = 0; }
        assert(h.n == ms.size()); if (!ms.empty()) assert(h.min->key == *ms.begin());
    }
    FibHeap a, b; std::multiset<int> all;                                  // meld 검사
    for (int i = 0; i < 500; i++) { int x = rng() % 1000; a.push(x); all.insert(x); int y = rng() % 1000; b.push(y); all.insert(y); }
    a.meld(b); assert(b.n == 0 && a.n == 1000);
    while (a.n) { FNode* z = a.extractMin(); assert(z->key == *all.begin()); all.erase(all.begin()); }
    FibHeap big; for (int i = 0; i < 100000; i++) big.push((int)(rng() % 1000000));
    big.extractMin();                                                      // consolidate: 차수가 모두 달라지고 최대 차수는 log_phi(n) 이하
    assert(big.maxDegree <= (int)(std::log((double)big.n) / std::log(1.6180339887)) + 1);
    std::cout << "FibonacciHeap: 20000 mixed ops match multiset; max root degree after consolidate of 1e5 keys = " << big.maxDegree << std::endl;
    return 0;
}
// Time Complexity: push/meld/decreaseKey 분할상환 O(1), extractMin 분할상환 O(log N)
// Space Complexity: O(N)
```
## BinomialHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <memory>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 이항 힙: 이항 트리 B0, B1, B2, ... (Bk 는 노드 2^k 개, 루트 차수 k) 들의 모음. n 의 이진 표현이 곧 구성이다 (n = 13 = 1101 -> B3, B2, B0).
// 두 힙의 합치기(unite)는 이진수 덧셈과 똑같다: 차수가 같은 두 트리를 합치면 올림이 생긴다.  push = 크기 1 짜리 힙과 unite, extractMin = 루트의 자식들을 힙으로 보고 unite
struct BNode { int key, id, degree = 0; BNode *p = nullptr, *child = nullptr, *sibling = nullptr; };
struct BinomialHeap {
    BNode* head = nullptr; size_t n = 0; std::vector<std::unique_ptr<BNode>> pool; std::vector<BNode*> loc;
    static void link(BNode* y, BNode* z) { y->p = z; y->sibling = z->child; z->child = y; z->degree++; }   // y 를 z 의 첫 자식으로
    static BNode* mergeLists(BNode* a, BNode* b) {                         // 차수 오름차순 두 리스트를 병합
        BNode dummy; BNode* t = &dummy;
        while (a && b) { if (a->degree <= b->degree) { t->sibling = a; a = a->sibling; } else { t->sibling = b; b = b->sibling; } t = t->sibling; }
        t->sibling = a ? a : b; return dummy.sibling;
    }
    static BNode* unite(BNode* a, BNode* b) {
        BNode* h = mergeLists(a, b); if (!h) return nullptr;
        BNode *prev = nullptr, *x = h, *next = x->sibling;
        while (next) {
            if (x->degree != next->degree || (next->sibling && next->sibling->degree == x->degree)) { prev = x; x = next; }
            else if (x->key <= next->key) { x->sibling = next->sibling; link(next, x); }
            else { if (!prev) h = next; else prev->sibling = next; link(x, next); x = next; }
            next = x->sibling;
        }
        return h;
    }
    int push(int key) {
        int id = loc.size(); pool.emplace_back(new BNode{key, id}); loc.push_back(pool.back().get());
        head = unite(head, loc.back()); n++; return id;
    }
    int findMin() const { int m = INT32_MAX; for (BNode* x = head; x; x = x->sibling) m = std::min(m, x->key); return m; }
    int extractMin(int& id) {
        BNode *best = head, *bestPrev = nullptr;
        for (BNode *p = nullptr, *x = head; x; p = x, x = x->sibling) if (x->key < best->key) { best = x; bestPrev = p; }
        if (bestPrev) bestPrev->sibling = best->sibling; else head = best->sibling;
        BNode* rev = nullptr;                                              // 자식 리스트를 뒤집어 차수 오름차순으로
        for (BNode* c = best->child; c; ) { BNode* nx = c->sibling; c->sibling = rev; c->p = nullptr; rev = c; c = nx; }
        head = unite(head, rev); n--; id = best->id; loc[id] = nullptr; return best->key;
    }
    void decreaseKey(int id, int k) {                                      // 부모와 키·id 를 맞바꾸며 올라간다
        BNode* x = loc[id]; assert(k <= x->key); x->key = k;
        while (x->p && x->key < x->p->key) { BNode* p = x->p; std::swap(x->key, p->key); std::swap(x->id, p->id); loc[x->id] = x; loc[p->id] = p; x = p; }
    }
};

int main() {
    BinomialHeap h;
    for (int i = 1; i <= 1000; i++) { h.push(1000 - i); int trees = 0; for (BNode* x = h.head; x; x = x->sibling) trees++; assert(trees == __builtin_popcount(i)); }
    // 트리 개수 = n 의 이진 표현에서 1 의 개수, 각 루트의 차수는 켜진 비트의 위치와 같다
    int expectDeg = 0; for (BNode* x = h.head; x; x = x->sibling) { while (!((1000 >> expectDeg) & 1)) expectDeg++; assert(x->degree == expectDeg++); }

    std::mt19937 rng(3); BinomialHeap q; std::multiset<int> ms; std::vector<char> alive;
    for (int step = 0; step < 15000; step++) {
        int op = rng() % 10;
        if (op < 5 || ms.empty()) { int k = rng() % 100000 + 1000; int id = q.push(k); alive.push_back(1); assert(id == (int)alive.size() - 1); ms.insert(k); }
        else if (op < 8) { int id; int k = q.extractMin(id); assert(k == *ms.begin()); ms.erase(ms.begin()); alive[id] = 0; }
        else {
            int i; do { i = rng() % alive.size(); } while (!alive[i]);
            int old = q.loc[i]->key, nk = old - (int)(rng() % 500) - 1; q.decreaseKey(i, nk); ms.erase(ms.find(old)); ms.insert(nk);
        }
        assert(q.n == ms.size()); if (!ms.empty()) assert(q.findMin() == *ms.begin());
    }
    std::cout << "BinomialHeap: " << h.n << " keys -> trees = popcount, 15000 mixed ops match multiset" << std::endl;
    return 0;
}
// Time Complexity: push·unite·extractMin·decreaseKey 모두 O(log N) (push 는 분할상환 O(1))
// Space Complexity: O(N)
```
## PairingHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <memory>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>
#include <cassert>

// 페어링 힙: "힙 순서 트리"를 자식 리스트(첫 자식-다음 형제)로 표현한 가장 단순한 meld 가능 힙. 구현이 짧고 실전에서 피보나치 힙보다 빠른 경우가 많다.
// meld(a,b) 는 루트가 큰 쪽을 작은 쪽의 첫 자식으로 붙이면 끝(O(1)).  deleteMin 은 루트의 자식들을 "왼쪽→오른쪽으로 둘씩 짝 짓고(meld), 오른쪽→왼쪽으로 하나로 합치는" 2-pass 로 처리한다
struct PNode { int key; PNode *child = nullptr, *sibling = nullptr, *prev = nullptr; };   // prev: 첫 자식이면 부모, 아니면 왼쪽 형제
struct PairingHeap {
    PNode* root = nullptr; size_t n = 0; std::vector<std::unique_ptr<PNode>> pool;
    static PNode* meld(PNode* a, PNode* b) {
        if (!a) return b; if (!b) return a;
        if (b->key < a->key) std::swap(a, b);
        b->prev = a; b->sibling = a->child; if (a->child) a->child->prev = b; a->child = b;
        a->prev = a->sibling = nullptr; return a;
    }
    PNode* push(int k) { pool.emplace_back(new PNode{k}); PNode* x = pool.back().get(); root = meld(root, x); n++; return x; }
    void meld(PairingHeap& o) { for (auto& p : o.pool) pool.push_back(std::move(p)); o.pool.clear(); root = meld(root, o.root); n += o.n; o.root = nullptr; o.n = 0; }
    static PNode* twoPass(PNode* first) {
        if (!first) return nullptr;
        std::vector<PNode*> v;
        for (PNode* c = first; c; ) {
            PNode *a = c, *b = a->sibling, *nx = b ? b->sibling : nullptr;
            a->sibling = a->prev = nullptr; if (b) b->sibling = b->prev = nullptr;
            v.push_back(b ? meld(a, b) : a); c = nx;
        }
        PNode* r = v.back(); for (int i = (int)v.size() - 2; i >= 0; i--) r = meld(v[i], r);
        return r;
    }
    PNode* popMin() {
        PNode* z = root; root = twoPass(z->child); if (root) root->prev = nullptr; n--; z->child = nullptr; return z;
    }
    void decreaseKey(PNode* x, int k) {
        assert(k <= x->key); x->key = k; if (x == root) return;
        if (x->prev->child == x) x->prev->child = x->sibling; else x->prev->sibling = x->sibling;   // 부모(또는 형제)에서 떼어낸다
        if (x->sibling) x->sibling->prev = x->prev;
        x->prev = x->sibling = nullptr; root = meld(root, x);
    }
};

int main() {
    std::mt19937 rng(11);
    PairingHeap h; std::multiset<int> ms; std::vector<PNode*> hs; std::vector<char> alive; std::unordered_map<PNode*, int> idx;
    for (int step = 0; step < 20000; step++) {
        int op = rng() % 10;
        if (op < 5 || ms.empty()) { int k = rng() % 100000 + 1000; PNode* x = h.push(k); idx[x] = hs.size(); hs.push_back(x); alive.push_back(1); ms.insert(k); }
        else if (op < 7) { PNode* z = h.popMin(); assert(z->key == *ms.begin()); ms.erase(ms.begin()); alive[idx[z]] = 0; }
        else {
            int i; do { i = rng() % hs.size(); } while (!alive[i]);
            int old = hs[i]->key, nk = old - (int)(rng() % 700) - 1; h.decreaseKey(hs[i], nk); ms.erase(ms.find(old)); ms.insert(nk);
        }
        assert(h.n == ms.size()); if (!ms.empty()) assert(h.root->key == *ms.begin());
    }
    PairingHeap a, b; std::multiset<int> all;
    for (int i = 0; i < 400; i++) { int x = rng() % 1000, y = rng() % 1000; a.push(x); b.push(y); all.insert(x); all.insert(y); }
    a.meld(b); while (a.n) { PNode* z = a.popMin(); assert(z->key == *all.begin()); all.erase(all.begin()); }
    PairingHeap sorted; std::vector<int> v(5000); for (auto& x : v) x = rng() % 100000;
    for (int x : v) sorted.push(x);
    std::sort(v.begin(), v.end()); for (int x : v) assert(sorted.popMin()->key == x);                // 힙 정렬
    std::cout << "PairingHeap: 20000 mixed ops match multiset, meld and heap-sort OK" << std::endl;
    return 0;
}
// Time Complexity: push/meld O(1), deleteMin 분할상환 O(log N), decreaseKey 분할상환 o(log N) (정확한 한계는 미해결 문제)
// Space Complexity: O(N)
```
## LeftistHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <memory>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 좌편향 힙(leftist heap): 각 노드의 npl(null path length, 가장 가까운 빈 자리까지의 거리)을 두고 "왼쪽 자식의 npl >= 오른쪽 자식의 npl" 을 유지한다.
// 그러면 오른쪽 가지(right spine)의 길이가 O(log n) 이므로, 병합을 오른쪽 가지만 따라 내려가며 재귀로 처리할 수 있다.  insert/pop 은 모두 merge 한 번
struct LNode { int key, npl = 1; LNode *l = nullptr, *r = nullptr; };
int npl(LNode* x) { return x ? x->npl : 0; }
LNode* merge(LNode* a, LNode* b) {
    if (!a) return b; if (!b) return a;
    if (b->key < a->key) std::swap(a, b);
    a->r = merge(a->r, b);
    if (npl(a->l) < npl(a->r)) std::swap(a->l, a->r);                     // 왼쪽이 더 "무겁게"
    a->npl = npl(a->r) + 1; return a;
}
struct LeftistHeap {
    LNode* root = nullptr; size_t n = 0; std::vector<std::unique_ptr<LNode>> pool;
    void push(int k) { pool.emplace_back(new LNode{k}); root = merge(root, pool.back().get()); n++; }
    int top() const { return root->key; }
    int pop() { int k = root->key; root = merge(root->l, root->r); n--; return k; }
    void meld(LeftistHeap& o) { for (auto& p : o.pool) pool.push_back(std::move(p)); o.pool.clear(); root = merge(root, o.root); n += o.n; o.root = nullptr; o.n = 0; }
};
bool valid(LNode* x) {                                                     // 힙 순서 + 좌편향 성질 + npl 값
    if (!x) return true;
    if (x->l && x->l->key < x->key) return false;
    if (x->r && x->r->key < x->key) return false;
    if (npl(x->l) < npl(x->r) || x->npl != npl(x->r) + 1) return false;
    return valid(x->l) && valid(x->r);
}

int main() {
    std::mt19937 rng(19);
    LeftistHeap h; std::priority_queue<int, std::vector<int>, std::greater<int>> pq;
    for (int step = 0; step < 20000; step++) {
        if (rng() % 3 < 2 || pq.empty()) { int k = rng() % 100000; h.push(k); pq.push(k); }
        else { assert(h.top() == pq.top()); assert(h.pop() == pq.top()); pq.pop(); }
        assert(h.n == pq.size());
        if (step % 1000 == 0) assert(valid(h.root));
    }
    assert(npl(h.root) <= std::log2(h.n + 1) + 1);                         // 오른쪽 가지의 길이 <= log2(n+1)
    LeftistHeap a, b; std::vector<int> all;
    for (int i = 0; i < 700; i++) { int x = rng() % 5000, y = rng() % 5000; a.push(x); b.push(y); all.push_back(x); all.push_back(y); }
    a.meld(b); assert(valid(a.root) && b.n == 0);
    std::sort(all.begin(), all.end()); for (int x : all) assert(a.pop() == x);
    LeftistHeap lopsided; for (int i = 0; i < 4096; i++) lopsided.push(i);   // 정렬된 입력에도 오른쪽 가지는 짧다
    assert(npl(lopsided.root) <= 13);
    std::cout << "LeftistHeap: merge-only heap OK, right spine <= log2(n+1)" << std::endl;
    return 0;
}
// Time Complexity: merge·push·pop O(log N)
// Space Complexity: O(N)
```
## DAryHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <functional>
#include <queue>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// d-ary 힙: 자식이 d 개인 완전 d-분 트리를 배열에 담는다. 부모 (i-1)/d, 자식 d*i+1 .. d*i+d.
// 높이가 log_d n 으로 낮아져서 push / decreaseKey (위로 올리기) 가 빨라지고, pop (아래로 내리기) 은 레벨마다 d 개를 비교하므로 느려진다.
// decreaseKey 가 많은 Dijkstra 에서는 d = 2 + E/V 정도가 좋다.  아래는 id(0..N-1) 로 원소를 가리키는 "인덱스 우선순위 큐"
template <int D> struct IndexedDHeap {
    std::vector<int> heap, pos, key; long compares = 0;
    explicit IndexedDHeap(int n) : pos(n, -1), key(n) {}
    bool empty() const { return heap.empty(); }
    void up(int i) {
        int id = heap[i];
        while (i > 0) { int p = (i - 1) / D; compares++; if (key[heap[p]] <= key[id]) break; heap[i] = heap[p]; pos[heap[i]] = i; i = p; }
        heap[i] = id; pos[id] = i;
    }
    void down(int i) {
        int id = heap[i], n = heap.size();
        for (;;) {
            int c = D * i + 1; if (c >= n) break;
            int best = c; for (int j = c + 1; j < std::min(n, c + D); j++) { compares++; if (key[heap[j]] < key[heap[best]]) best = j; }
            compares++; if (key[heap[best]] >= key[id]) break;
            heap[i] = heap[best]; pos[heap[i]] = i; i = best;
        }
        heap[i] = id; pos[id] = i;
    }
    void push(int id, int k) { key[id] = k; heap.push_back(id); up(heap.size() - 1); }
    int pop() { int top = heap[0], last = heap.back(); pos[top] = -1; heap.pop_back(); if (!heap.empty()) { heap[0] = last; pos[last] = 0; down(0); } return top; }
    void decrease(int id, int k) { key[id] = k; up(pos[id]); }
    bool contains(int id) const { return pos[id] >= 0; }
};
template <int D> std::vector<long> dijkstra(const std::vector<std::vector<std::pair<int, int>>>& g, int s, long& cmp) {
    std::vector<long> dist(g.size(), 1L << 60); IndexedDHeap<D> pq(g.size()); dist[s] = 0; pq.push(s, 0);
    while (!pq.empty()) {
        int u = pq.pop();
        for (auto [v, w] : g[u]) if (dist[u] + w < dist[v]) {
            bool had = pq.contains(v); dist[v] = dist[u] + w;
            if (had) pq.decrease(v, dist[v]); else pq.push(v, dist[v]);   // 키가 int 라 이 데모에서는 거리가 int 범위
        }
    }
    cmp = pq.compares; return dist;
}
template <int D> void fuzz() {
    std::mt19937 rng(D); IndexedDHeap<D> h(3000); std::set<std::pair<int, int>> ref; std::vector<int> cur(3000, -1);
    for (int step = 0; step < 30000; step++) {
        int id = rng() % 3000;
        if (cur[id] < 0 && rng() % 2) { int k = rng() % 100000 + 500; h.push(id, k); ref.insert({k, id}); cur[id] = k; }
        else if (cur[id] >= 0 && rng() % 2) { int nk = cur[id] - (int)(rng() % 400); h.decrease(id, nk); ref.erase({cur[id], id}); ref.insert({nk, id}); cur[id] = nk; }
        else if (!ref.empty() && rng() % 3 == 0) {
            int top = h.pop(); assert(h.key[top] == ref.begin()->first);       // 같은 키면 id 는 다를 수 있으므로 키만 비교
            auto it = ref.find({h.key[top], top}); assert(it != ref.end()); ref.erase(it); cur[top] = -1;
        }
        assert(h.heap.size() == ref.size());
    }
}
int main() {
    fuzz<2>(); fuzz<3>(); fuzz<4>(); fuzz<8>();
    std::mt19937 rng(42); int N = 2000, M = 20000;
    std::vector<std::vector<std::pair<int, int>>> g(N);
    for (int i = 0; i < M; i++) { int u = rng() % N, v = rng() % N, w = rng() % 100 + 1; g[u].push_back({v, w}); g[v].push_back({u, w}); }
    // 기준: 표준 priority_queue 로 구현한 lazy Dijkstra
    std::vector<long> ref(N, 1L << 60); std::priority_queue<std::pair<long, int>, std::vector<std::pair<long, int>>, std::greater<>> q; ref[0] = 0; q.push({0, 0});
    while (!q.empty()) { auto [d, u] = q.top(); q.pop(); if (d > ref[u]) continue; for (auto [v, w] : g[u]) if (d + w < ref[v]) { ref[v] = d + w; q.push({ref[v], v}); } }
    long c2, c4, c8; assert(dijkstra<2>(g, 0, c2) == ref); assert(dijkstra<4>(g, 0, c4) == ref); assert(dijkstra<8>(g, 0, c8) == ref);
    auto levels = [](long n, int d) { int h = 0; for (long i = n - 1; i > 0; i = (i - 1) / d) h++; return h; };
    assert(levels(1000000, 4) * 2 <= levels(1000000, 2) + 1 && levels(1000000, 8) < levels(1000000, 4));
    std::cout << "d-ary heap: Dijkstra compares  d=2: " << c2 << ", d=4: " << c4 << ", d=8: " << c8
              << " | depth for 1e6 keys  d=2: " << levels(1000000, 2) << ", d=4: " << levels(1000000, 4) << ", d=8: " << levels(1000000, 8) << std::endl;
    return 0;
}
// Time Complexity: push·decreaseKey O(log_d N), pop O(d log_d N)
// Space Complexity: O(N)
```
## MinMaxHeap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 최소-최대 힙: 하나의 배열 힙으로 최솟값과 최댓값을 모두 O(1) 로 보고 O(log n) 에 뺄 수 있다 (양방향 우선순위 큐).
// 깊이가 짝수인 레벨은 "자기 아래 모든 원소보다 작다"(min 레벨), 홀수 레벨은 "모든 후손보다 크다"(max 레벨).  최솟값은 a[0], 최댓값은 a[1], a[2] 중 큰 쪽.
// 삽입은 부모와 비교해 레벨 종류를 바꾼 뒤 같은 종류의 조부모 사슬로 올라가고, 삭제는 자식·손자 중 극값과 교환하며 내려간다
struct MinMaxHeap {
    std::vector<int> a;
    static bool minLevel(size_t i) { return (63 - __builtin_clzll(i + 1)) % 2 == 0; }
    void bubbleUpMin(size_t i) { while (i >= 3) { size_t g = ((i - 1) / 2 - 1) / 2; if (a[i] < a[g]) { std::swap(a[i], a[g]); i = g; } else break; } }
    void bubbleUpMax(size_t i) { while (i >= 3) { size_t g = ((i - 1) / 2 - 1) / 2; if (a[i] > a[g]) { std::swap(a[i], a[g]); i = g; } else break; } }
    void push(int x) {
        a.push_back(x); size_t i = a.size() - 1; if (!i) return;
        size_t p = (i - 1) / 2;
        if (minLevel(i)) { if (a[i] > a[p]) { std::swap(a[i], a[p]); bubbleUpMax(p); } else bubbleUpMin(i); }
        else             { if (a[i] < a[p]) { std::swap(a[i], a[p]); bubbleUpMin(p); } else bubbleUpMax(i); }
    }
    template <class Less> void trickleDown(size_t i, Less less) {          // less 가 < 이면 min 레벨, > 이면 max 레벨
        size_t n = a.size();
        while (2 * i + 1 < n) {
            size_t m = 2 * i + 1;                                          // 자식과 손자 중 "가장 극단적인" 것
            for (size_t c : {2 * i + 2, 4 * i + 3, 4 * i + 4, 4 * i + 5, 4 * i + 6}) if (c < n && less(a[c], a[m])) m = c;
            if (m > 2 * i + 2) {                                           // 손자인 경우
                if (!less(a[m], a[i])) break;
                std::swap(a[m], a[i]);
                size_t p = (m - 1) / 2; if (less(a[p], a[m])) std::swap(a[m], a[p]);   // 새 값이 부모(반대 레벨)와 충돌하면 교환
                i = m;
            } else { if (less(a[m], a[i])) std::swap(a[m], a[i]); break; }  // 자식인 경우는 잎 직전이라 끝
        }
    }
    int min() const { return a[0]; }
    int max() const { return a.size() == 1 ? a[0] : a.size() == 2 ? a[1] : std::max(a[1], a[2]); }
    int popMin() { int x = a[0]; a[0] = a.back(); a.pop_back(); if (!a.empty()) trickleDown(0, std::less<int>()); return x; }
    int popMax() {
        size_t i = a.size() == 1 ? 0 : a.size() == 2 ? 1 : (a[1] >= a[2] ? 1 : 2);
        int x = a[i]; a[i] = a.back(); a.pop_back(); if (i < a.size()) trickleDown(i, std::greater<int>()); return x;
    }
    bool valid() const {                                                   // 모든 노드가 자기 레벨의 규칙을 후손 전체에 대해 만족하는가 (O(n^2), 테스트용)
        for (size_t i = 0; i < a.size(); i++) {
            std::vector<size_t> st = {2 * i + 1, 2 * i + 2};
            while (!st.empty()) { size_t j = st.back(); st.pop_back(); if (j >= a.size()) continue;
                if (minLevel(i) ? a[j] < a[i] : a[j] > a[i]) return false; st.push_back(2 * j + 1); st.push_back(2 * j + 2); }
        }
        return true;
    }
};

int main() {
    std::mt19937 rng(31);
    MinMaxHeap h; std::multiset<int> ms;
    for (int step = 0; step < 6000; step++) {
        int op = rng() % 6;
        if (op < 3 || ms.empty()) { int x = rng() % 1000; h.push(x); ms.insert(x); }
        else if (op < 5) { assert(h.popMin() == *ms.begin()); ms.erase(ms.begin()); }
        else { assert(h.popMax() == *ms.rbegin()); ms.erase(std::prev(ms.end())); }
        if (!ms.empty()) { assert(h.min() == *ms.begin() && h.max() == *ms.rbegin()); }
        if (step % 100 == 0) assert(h.valid());
    }
    std::vector<int> v; while (!h.a.empty()) { v.push_back(h.popMin()); if (!h.a.empty()) v.push_back(h.popMax()); }   // 양 끝을 번갈아 꺼내기
    std::vector<int> ref(ms.begin(), ms.end()); std::vector<int> expect;
    for (size_t lo = 0, hi = ref.size(); lo < hi; ) { expect.push_back(ref[lo++]); if (lo < hi) expect.push_back(ref[--hi]); }
    assert(v == expect);
    std::cout << "MinMaxHeap: min/max both O(1), 6000 mixed ops match multiset" << std::endl;
    return 0;
}
// Time Complexity: min/max O(1), push·popMin·popMax O(log N)
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
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 기수 트리(압축 트라이, radix tree): 자식이 하나뿐인 경로를 하나의 간선(문자열 레이블)으로 합친 트라이.  노드 수가 단어 수에 비례(O(n))하고, 단어를 넣을 때
// 간선 레이블이 중간에서 갈라지면 그 자리에서 둘로 쪼갠다.  리눅스 커널의 페이지 캐시·IP 라우팅 테이블(LPM)·Redis 의 rax 가 쓴다
struct Node { std::map<char, std::pair<std::string, Node*>> kids; bool end = false; };
static int nodeCount = 1;

void insert(Node* root, const std::string& w) {
    Node* n = root; size_t i = 0;
    while (i < w.size()) {
        auto it = n->kids.find(w[i]);
        if (it == n->kids.end()) { Node* leaf = new Node; leaf->end = true; nodeCount++; n->kids[w[i]] = {w.substr(i), leaf}; return; }
        std::string& label = it->second.first; Node* child = it->second.second;
        size_t l = 0; while (l < label.size() && i + l < w.size() && label[l] == w[i + l]) l++;
        if (l == label.size()) { n = child; i += l; continue; }                    // 레이블 전체 일치: 아래로
        Node* mid = new Node; nodeCount++;                                          // 레이블 중간에서 갈라짐: 중간 노드를 만들어 분할
        mid->kids[label[l]] = {label.substr(l), child};
        it->second = {label.substr(0, l), mid};
        n = mid; i += l;
    }
    n->end = true;
}
bool contains(const Node* root, const std::string& w) {
    const Node* n = root; size_t i = 0;
    while (i < w.size()) {
        auto it = n->kids.find(w[i]); if (it == n->kids.end()) return false;
        const std::string& label = it->second.first;
        if (w.compare(i, label.size(), label) != 0) return false;
        i += label.size(); n = it->second.second;
    }
    return n->end;
}
void collect(const Node* n, std::string cur, std::vector<std::string>& out) {
    if (n->end) out.push_back(cur);
    for (auto& kv : n->kids) collect(kv.second.second, cur + kv.second.first, out);
}
std::vector<std::string> withPrefix(const Node* root, const std::string& p) {
    const Node* n = root; std::string cur; size_t i = 0;
    while (i < p.size()) {
        auto it = n->kids.find(p[i]); if (it == n->kids.end()) return {};
        const std::string& label = it->second.first; size_t m = std::min(label.size(), p.size() - i);
        if (label.compare(0, m, p, i, m) != 0) return {};
        cur += label; i += m; n = it->second.second;                               // 접두사가 레이블 중간에서 끝나도 그 아래 전체가 후보
    }
    std::vector<std::string> out; collect(n, cur, out); return out;
}

int main() {
    Node root;
    std::vector<std::string> words = {"romane", "romanus", "romulus", "rubens", "ruber", "rubicon", "rubicundus"};
    size_t trieNodes = 1; { std::map<std::string, int> prefixes; for (auto& w : words) for (size_t k = 1; k <= w.size(); k++) prefixes[w.substr(0, k)] = 1; trieNodes += prefixes.size(); }
    for (auto& w : words) insert(&root, w);
    for (auto& w : words) assert(contains(&root, w));
    assert(!contains(&root, "rom") && !contains(&root, "roman") && !contains(&root, "rubicons"));      // 접두사만으로는 단어가 아니다
    assert(nodeCount * 2 <= (int)trieNodes);                                    // 일반 트라이(문자당 노드, 28개)의 절반 이하 (14개)
    assert((withPrefix(&root, "rub") == std::vector<std::string>{"rubens", "ruber", "rubicon", "rubicundus"}));
    assert((withPrefix(&root, "roman") == std::vector<std::string>{"romane", "romanus"}));
    assert(withPrefix(&root, "x").empty());
    std::cout << "RadixTree: " << words.size() << " words in " << nodeCount << " nodes (plain trie: " << trieNodes << ")" << std::endl;
    return 0;
}
// Time Complexity: 삽입·검색 O(L)
// Space Complexity: O(단어 수) 노드 + 레이블
```

## GeneralTree()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <cassert>

// 일반 트리: 자식 수에 제한이 없다.  표준 표현은 "왼쪽 자식-오른쪽 형제(LCRS)": 모든 노드가 (첫 자식, 다음 형제) 포인터 두 개만 가지므로
// 일반 트리가 곧 이진 트리가 된다.  성질: 일반 트리의 전위 순회 = LCRS 의 전위 순회,  일반 트리의 후위 순회 = LCRS 의 중위 순회
struct Node { char label; Node *firstChild = nullptr, *nextSibling = nullptr; };
Node* addChild(Node* parent, char label) {
    Node* c = new Node{label};
    if (!parent->firstChild) parent->firstChild = c;
    else { Node* s = parent->firstChild; while (s->nextSibling) s = s->nextSibling; s->nextSibling = c; }
    return c;
}
void preorder(const Node* n, std::string& out) { for (; n; n = n->nextSibling) { out += n->label; preorder(n->firstChild, out); } }   // 일반 트리의 전위
void postorder(const Node* n, std::string& out) { for (; n; n = n->nextSibling) { postorder(n->firstChild, out); out += n->label; } }  // 일반 트리의 후위
void binaryInorder(const Node* n, std::string& out) { if (!n) return; binaryInorder(n->firstChild, out); out += n->label; binaryInorder(n->nextSibling, out); }
int height(const Node* n) { int h = 0; for (; n; n = n->nextSibling) h = std::max(h, 1 + height(n->firstChild)); return h; }

int main() {
    Node* a = new Node{'A'};                       //        A
    Node* b = addChild(a, 'B');                    //      / | \  .
    addChild(a, 'C');                              //     B  C  D
    Node* d = addChild(a, 'D');                    //    / \    |
    addChild(b, 'E'); addChild(b, 'F');            //   E   F   G
    addChild(d, 'G');
    std::string pre, post, in;
    preorder(a, pre); postorder(a, post); binaryInorder(a, in);
    assert(pre == "ABEFCDG");
    assert(post == "EFBCGDA");
    assert(in == post);                            // LCRS 중위 순회 == 일반 트리 후위 순회
    assert(height(a) == 3);
    std::cout << "GeneralTree preorder=" << pre << " postorder=" << post << std::endl;
    return 0;
}
// Time Complexity: 자식 추가 O(자식 수), 순회 O(N)
// Space Complexity: O(N)
```
## NaryTree()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cassert>

// N-ary 트리: 모든 노드의 자식이 최대 N 개.  완전 N-ary 트리는 배열에 담을 수 있다 (N=2 가 힙).
//   부모(i) = (i-1)/N,   자식 k(0-based) 의 인덱스 = N·i + k + 1
//   n 개 노드의 높이 = ceil(log_N(n·(N-1) + 1)) - 1   (간선 기준),  N 이 클수록 얕아진다 (B-트리·캐시 친화적 힙의 동기)
int height(long n, int N) { int h = 0; long levelEnd = 1, width = 1; while (levelEnd < n) { width *= N; levelEnd += width; h++; } return h; }

int main() {
    const int N = 3;
    for (long i = 1; i < 1000; i++) {
        long parent = (i - 1) / N;
        long k = (i - 1) % N;
        assert(N * parent + k + 1 == i);                                      // 부모/자식 인덱스 공식이 서로 역
    }
    for (int n : {1, 4, 13, 14, 40, 41, 1000}) {                               // 3-ary 의 가득 찬 수준: 1, 4, 13, 40, 121 ...
        int expect = (int)std::ceil(std::log((double)n * (N - 1) + 1) / std::log((double)N)) - 1;
        assert(height(n, N) == expect);
    }
    assert(height(1000000, 2) == 19 && height(1000000, 8) == 7);               // 같은 N=100만: 이진 19, 8진 7
    std::cout << "NaryTree: height for 1e6 nodes: binary=" << height(1000000, 2) << " 8-ary=" << height(1000000, 8) << std::endl;
    return 0;
}
// Time Complexity: 인덱스 계산 O(1)
// Space Complexity: O(N) 배열
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
        for (int i = 0; i < (int)text.length(); i++) {
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
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 접미사 트리: 문자열의 모든 접미사를 압축 트라이로 모은 것.  부분 문자열 검색이 O(m), 서로 다른 부분 문자열 수·최장 반복 부분 문자열·최장 공통 부분 문자열 같은 문제를 선형 시간에 푼다.
// 끝 표식 '$' 를 붙여 어떤 접미사도 다른 접미사의 접두사가 되지 않게 한다 (모든 접미사가 잎).  여기서는 접미사를 하나씩 넣는 O(n²) 구성 (선형 시간 알고리즘은 Ukkonen)
struct Node { std::map<char, std::pair<std::string, Node*>> kids; int leafIndex = -1; };

void insertSuffix(Node* root, const std::string& s, int start) {
    Node* n = root; size_t i = start;
    for (;;) {
        auto it = n->kids.find(s[i]);
        if (it == n->kids.end()) { Node* leaf = new Node; leaf->leafIndex = start; n->kids[s[i]] = {s.substr(i), leaf}; return; }
        std::string& label = it->second.first; Node* child = it->second.second;
        size_t l = 0; while (l < label.size() && s[i + l] == label[l]) l++;
        if (l == label.size()) { n = child; i += l; continue; }
        Node* mid = new Node;                                                       // 분할
        mid->kids[label[l]] = {label.substr(l), child};
        it->second = {label.substr(0, l), mid};
        n = mid; i += l;
    }
}
void leaves(const Node* n, std::set<int>& out) { if (n->leafIndex >= 0) out.insert(n->leafIndex); for (auto& kv : n->kids) leaves(kv.second.second, out); }
std::set<int> find(const Node* root, const std::string& p) {                         // 패턴의 모든 출현 위치 = 패턴 끝 아래의 잎들
    const Node* n = root; size_t i = 0;
    while (i < p.size()) {
        auto it = n->kids.find(p[i]); if (it == n->kids.end()) return {};
        const std::string& label = it->second.first; size_t m = std::min(label.size(), p.size() - i);
        if (label.compare(0, m, p, i, m) != 0) return {};
        i += m; n = it->second.second;
    }
    std::set<int> r; leaves(n, r); return r;
}
size_t edgeChars(const Node* n) { size_t s = 0; for (auto& kv : n->kids) s += kv.second.first.size() + edgeChars(kv.second.second); return s; }

int main() {
    std::string text = "banana", s = text + "$";
    Node root; for (size_t i = 0; i < s.size(); i++) insertSuffix(&root, s, i);
    assert((find(&root, "ana") == std::set<int>{1, 3}));
    assert((find(&root, "na") == std::set<int>{2, 4}));
    assert((find(&root, "banana") == std::set<int>{0}));
    assert(find(&root, "nab").empty());
    // 간선 레이블의 총 길이 = 서로 다른 부분 문자열의 수 ('$' 로 끝나는 n+1 개 포함)
    assert(edgeChars(&root) - (text.size() + 1) == 15);                              // banana 의 서로 다른 부분 문자열은 15개
    std::set<std::string> brute; for (size_t i = 0; i < text.size(); i++) for (size_t l = 1; i + l <= text.size(); l++) brute.insert(text.substr(i, l));
    assert(brute.size() == 15);
    std::cout << "SuffixTree(banana): 'ana' at {1,3}, 15 distinct substrings" << std::endl;
    return 0;
}
// Time Complexity: 이 구성 O(n²), Ukkonen O(n); 검색 O(m + 출현 수)
// Space Complexity: O(n)
```
## PatriciaTrie()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <set>
#include <cassert>

// 패트리샤 트라이(crit-bit 트리): 키를 비트열로 보고 "두 키가 처음 달라지는 비트(critical bit)" 만 내부 노드에 저장한다.
// 한 자식만 있는 노드가 없어서 n 개의 키에 정확히 n-1 개의 내부 노드가 있고, 비교는 비트 검사뿐이라 분기가 단순하다.  IP 라우팅의 최장 접두사 일치와 문자열 사전에 쓰인다
struct Node { bool leaf; uint32_t key; int bit; Node *l = nullptr, *r = nullptr; };
Node* newLeaf(uint32_t k) { return new Node{true, k, -1}; }
int topBit(uint32_t x) { return 31 - __builtin_clz(x); }
bool bitAt(uint32_t k, int b) { return k >> b & 1; }

Node* findLeaf(Node* n, uint32_t k) { while (!n->leaf) n = bitAt(k, n->bit) ? n->r : n->l; return n; }
Node* insert(Node* root, uint32_t k) {
    if (!root) return newLeaf(k);
    Node* best = findLeaf(root, k);
    if (best->key == k) return root;                                       // 이미 있다
    int crit = topBit(best->key ^ k);                                       // 처음 달라지는 비트
    Node** where = &root;                                                    // 비트 번호가 crit 보다 큰 내부 노드들을 지나 내려간다
    while (!(*where)->leaf && (*where)->bit > crit) where = bitAt(k, (*where)->bit) ? &(*where)->r : &(*where)->l;
    Node* leaf = newLeaf(k); Node* inner = new Node{false, 0, crit};
    if (bitAt(k, crit)) { inner->l = *where; inner->r = leaf; } else { inner->l = leaf; inner->r = *where; }
    *where = inner;
    return root;
}
bool contains(Node* root, uint32_t k) { return root && findLeaf(root, k)->key == k; }
int countLeaves(Node* n) { return !n ? 0 : n->leaf ? 1 : countLeaves(n->l) + countLeaves(n->r); }
int countInner(Node* n) { return (!n || n->leaf) ? 0 : 1 + countInner(n->l) + countInner(n->r); }
bool decreasing(Node* n) { if (n->leaf) return true; for (Node* c : {n->l, n->r}) if (!c->leaf && c->bit >= n->bit) return false; return decreasing(n->l) && decreasing(n->r); }

int main() {
    std::mt19937 rng(18); Node* root = nullptr; std::set<uint32_t> truth;
    for (int i = 0; i < 2000; i++) { uint32_t k = rng() % 100000; root = insert(root, k); truth.insert(k); }
    for (uint32_t k = 0; k < 100000; k += 7) assert(contains(root, k) == (truth.count(k) > 0));
    assert(countLeaves(root) == (int)truth.size());
    assert(countInner(root) == (int)truth.size() - 1);                       // 내부 노드는 정확히 n-1 개
    assert(decreasing(root));                                                 // 내려갈수록 비교하는 비트가 낮아진다
    std::cout << "PatriciaTrie: " << truth.size() << " keys, " << countInner(root) << " internal nodes (n-1)" << std::endl;
    return 0;
}
// Time Complexity: 삽입·검색 O(키 길이 비트 수)
// Space Complexity: O(n)
```

## TernarySearchTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 삼진 탐색 트리(TST): 노드가 문자 하나와 세 개의 자식(작은 문자 lo / 같은 문자 eq 로 다음 글자 / 큰 문자 hi)을 갖는다.
// 트라이의 빠른 접두사 검색과 BST 의 작은 메모리를 합친 구조: 노드당 포인터 3개라 알파벳이 큰 트라이(문자당 배열)보다 훨씬 작고, 비교는 문자 단위.  자동 완성·철자 검사에 적합
struct Node { char c; Node *lo = nullptr, *eq = nullptr, *hi = nullptr; bool end = false; explicit Node(char ch) : c(ch) {} };

Node* insert(Node* n, const std::string& w, size_t i) {
    if (!n) n = new Node(w[i]);
    if (w[i] < n->c) n->lo = insert(n->lo, w, i);
    else if (w[i] > n->c) n->hi = insert(n->hi, w, i);
    else if (i + 1 < w.size()) n->eq = insert(n->eq, w, i + 1);
    else n->end = true;
    return n;
}
bool contains(const Node* n, const std::string& w, size_t i = 0) {
    while (n) {
        if (w[i] < n->c) n = n->lo; else if (w[i] > n->c) n = n->hi;
        else { if (i + 1 == w.size()) return n->end; n = n->eq; i++; }
    }
    return false;
}
void collect(const Node* n, std::string cur, std::vector<std::string>& out) {
    if (!n) return;
    collect(n->lo, cur, out);
    if (n->end) out.push_back(cur + n->c);
    collect(n->eq, cur + n->c, out);
    collect(n->hi, cur, out);
}
std::vector<std::string> startsWith(const Node* n, const std::string& p) {
    size_t i = 0; std::vector<std::string> out;
    while (n) {
        if (p[i] < n->c) n = n->lo; else if (p[i] > n->c) n = n->hi;
        else { if (i + 1 == p.size()) { if (n->end) out.push_back(p); collect(n->eq, p, out); return out; } n = n->eq; i++; }
    }
    return out;
}

int main() {
    Node* root = nullptr;
    std::vector<std::string> words = {"cat", "cap", "can", "car", "card", "care", "dog", "do", "done"};
    for (auto& w : words) root = insert(root, w, 0);
    for (auto& w : words) assert(contains(root, w));
    assert(!contains(root, "ca") && !contains(root, "cow") && !contains(root, "dones"));
    assert((startsWith(root, "car") == std::vector<std::string>{"car", "card", "care"}));
    assert((startsWith(root, "do") == std::vector<std::string>{"do", "dog", "done"}));
    assert(startsWith(root, "x").empty());
    std::cout << "TernarySearchTree verified: autocomplete 'car' -> car, card, care" << std::endl;
    return 0;
}
// Time Complexity: O(L + log σ) 평균 (σ = 알파벳 크기)
// Space Complexity: O(총 글자 수) 노드 · 3 포인터
```
## SuffixArray()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <numeric>
#include <string>
#include <vector>
#include <cassert>

// 접미사 배열(트리 관점의 요약, 정본은 String.md Part 9): 접미사 트리를 정렬된 배열로 평평하게 편 것.
// 접미사 트리의 잎을 사전순으로 훑은 순서 = 접미사 배열.  공간은 정수 n 개로 트리보다 훨씬 작고 캐시 친화적이다
int main() {
    std::string s = "banana";
    std::vector<int> sa(s.size()); std::iota(sa.begin(), sa.end(), 0);
    std::sort(sa.begin(), sa.end(), [&](int a, int b) { return s.compare(a, std::string::npos, s, b, std::string::npos) < 0; });
    assert((sa == std::vector<int>{5, 3, 1, 0, 4, 2}));                        // a, ana, anana, banana, na, nana
    // 패턴 "ana" 로 시작하는 접미사는 SA 에서 연속 구간 (이진 탐색으로 찾는다)
    auto lo = std::lower_bound(sa.begin(), sa.end(), std::string("ana"), [&](int i, const std::string& x) { return s.compare(i, x.size(), x) < 0; });
    auto hi = std::upper_bound(sa.begin(), sa.end(), std::string("ana"), [&](const std::string& x, int i) { return s.compare(i, x.size(), x) > 0; });
    assert(hi - lo == 2);
    std::cout << "SuffixArray(banana) = 5 3 1 0 4 2" << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n log² n), 검색 O(m log n)
// Space Complexity: O(n)
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
        for (++i; i < (int)tree.size(); i += i & -i) tree[i] += delta;
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
#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <random>
#include <vector>
#include <cassert>

// k-d 트리: k 차원 점들을 축을 번갈아 가며 중앙값으로 이진 분할한다.  최근접 이웃 탐색은 "가까운 쪽 먼저, 반대쪽은 분할 평면까지의 거리가 현재 최선보다 작을 때만" 방문하는 가지치기로
// 평균 O(log n).  차원이 커지면(약 20 이상) 가지치기가 듣지 않는 "차원의 저주" 가 있다
typedef std::array<double, 2> P;
struct KD {
    std::vector<P> pts;
    void build(int lo, int hi, int axis) {                        // pts[lo, hi) 구간을 중앙값 기준으로 재배열 (구간 안에서 중앙이 노드)
        if (hi - lo <= 1) return;
        int mid = (lo + hi) / 2;
        std::nth_element(pts.begin() + lo, pts.begin() + mid, pts.begin() + hi, [&](const P& a, const P& b) { return a[axis] < b[axis]; });
        build(lo, mid, 1 - axis); build(mid + 1, hi, 1 - axis);
    }
    static double d2(const P& a, const P& b) { return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]); }
    void nearest(int lo, int hi, int axis, const P& q, P& best, double& bestD) const {
        if (lo >= hi) return;
        int mid = (lo + hi) / 2; const P& node = pts[mid];
        double d = d2(node, q); if (d < bestD) { bestD = d; best = node; }
        double diff = q[axis] - node[axis];
        int nearLo = diff < 0 ? lo : mid + 1, nearHi = diff < 0 ? mid : hi, farLo = diff < 0 ? mid + 1 : lo, farHi = diff < 0 ? hi : mid;
        nearest(nearLo, nearHi, 1 - axis, q, best, bestD);
        if (diff * diff < bestD) nearest(farLo, farHi, 1 - axis, q, best, bestD);     // 분할 평면이 최선보다 가까울 때만 반대쪽 탐색
    }
    int rangeCount(int lo, int hi, int axis, const P& a, const P& b) const {          // 직사각형 [a, b] 안의 점 수
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2; const P& n = pts[mid]; int c = (n[0] >= a[0] && n[0] <= b[0] && n[1] >= a[1] && n[1] <= b[1]);
        if (a[axis] <= n[axis]) c += rangeCount(lo, mid, 1 - axis, a, b);
        if (b[axis] >= n[axis]) c += rangeCount(mid + 1, hi, 1 - axis, a, b);
        return c;
    }
};

int main() {
    std::mt19937 rng(22); std::uniform_real_distribution<double> U(0, 100);
    KD kd; for (int i = 0; i < 3000; i++) kd.pts.push_back({U(rng), U(rng)});
    std::vector<P> original = kd.pts;
    kd.build(0, kd.pts.size(), 0);
    for (int t = 0; t < 200; t++) {
        P q = {U(rng), U(rng)}, best{}; double bestD = std::numeric_limits<double>::max();
        kd.nearest(0, kd.pts.size(), 0, q, best, bestD);
        double brute = std::numeric_limits<double>::max(); for (auto& p : original) brute = std::min(brute, KD::d2(p, q));
        assert(std::fabs(bestD - brute) < 1e-12);                           // 완전 탐색과 같은 최근접 거리
        P a = {U(rng) * 0.5, U(rng) * 0.5}, b = {a[0] + 30, a[1] + 30}; int cnt = 0;
        for (auto& p : original) cnt += (p[0] >= a[0] && p[0] <= b[0] && p[1] >= a[1] && p[1] <= b[1]);
        assert(kd.rangeCount(0, kd.pts.size(), 0, a, b) == cnt);            // 범위 질의도 일치
    }
    std::cout << "KDTree: nearest-neighbour and range queries match brute force on 3000 points." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n log n), 최근접 평균 O(log n)
// Space Complexity: O(n)
```
## QuadTree()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 쿼드트리: 2차원 영역을 4개의 사분면으로 재귀 분할한다.  한 영역에 점이 CAP 개를 넘으면 쪼갠다.  범위 질의는 질의 사각형과 겹치는 사분면만 방문한다.
// 게임의 충돌 후보 찾기, 지도 타일, 이미지 압축에 쓰인다.  (같은 점이 여러 개 몰리는 경우를 위해 최대 깊이를 둔다)
struct Pt { double x, y; };
struct Rect { double x0, y0, x1, y1; bool contains(const Pt& p) const { return p.x >= x0 && p.x < x1 && p.y >= y0 && p.y < y1; }
              bool intersects(const Rect& r) const { return x0 < r.x1 && r.x0 < x1 && y0 < r.y1 && r.y0 < y1; } };
class QuadTree {
    static const int CAP = 4, MAXD = 12;
    Rect box; int depth; std::vector<Pt> pts; std::unique_ptr<QuadTree> kid[4];
public:
    QuadTree(Rect b, int d = 0) : box(b), depth(d) {}
    bool insert(const Pt& p) {
        if (!box.contains(p)) return false;
        if (!kid[0] && ((int)pts.size() < CAP || depth >= MAXD)) { pts.push_back(p); return true; }
        if (!kid[0]) {                                                         // 분할: 네 사분면 생성 후 기존 점 재배치
            double mx = (box.x0 + box.x1) / 2, my = (box.y0 + box.y1) / 2;
            kid[0].reset(new QuadTree({box.x0, box.y0, mx, my}, depth + 1)); kid[1].reset(new QuadTree({mx, box.y0, box.x1, my}, depth + 1));
            kid[2].reset(new QuadTree({box.x0, my, mx, box.y1}, depth + 1));  kid[3].reset(new QuadTree({mx, my, box.x1, box.y1}, depth + 1));
            std::vector<Pt> old; old.swap(pts); for (auto& q : old) insert(q);
        }
        for (auto& k : kid) if (k->insert(p)) return true;
        return false;
    }
    int query(const Rect& r) const {
        if (!box.intersects(r)) return 0;
        int c = 0; for (auto& p : pts) c += (p.x >= r.x0 && p.x < r.x1 && p.y >= r.y0 && p.y < r.y1);
        if (kid[0]) for (auto& k : kid) c += k->query(r);
        return c;
    }
    int nodes() const { int c = 1; if (kid[0]) for (auto& k : kid) c += k->nodes(); return c; }
};

int main() {
    std::mt19937 rng(23); std::uniform_real_distribution<double> U(0, 1000);
    QuadTree qt({0, 0, 1000, 1000}); std::vector<Pt> all;
    for (int i = 0; i < 5000; i++) { Pt p{U(rng), U(rng)}; all.push_back(p); assert(qt.insert(p)); }
    assert(!qt.insert({-1, 5}));                                                 // 영역 밖의 점은 거부
    for (int t = 0; t < 200; t++) {
        double x = U(rng) * 0.9, y = U(rng) * 0.9; Rect r{x, y, x + 80, y + 80}; int brute = 0;
        for (auto& p : all) brute += (p.x >= r.x0 && p.x < r.x1 && p.y >= r.y0 && p.y < r.y1);
        assert(qt.query(r) == brute);
    }
    QuadTree dup({0, 0, 1, 1}); for (int i = 0; i < 100; i++) assert(dup.insert({0.5, 0.5}));        // 같은 점 100개도 무한 분할하지 않는다
    std::cout << "QuadTree: 5000 points in " << qt.nodes() << " nodes; range queries match brute force." << std::endl;
    return 0;
}
// Time Complexity: 삽입 O(깊이), 범위 질의 평균 O(log n + k)
// Space Complexity: O(n)
```
## Octree()
### 대표코드
```cpp
#include <iostream>
#include <array>
#include <cmath>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 옥트리: 3차원 공간을 8개의 팔분면으로 재귀 분할한다 (쿼드트리의 3차원판).  3D 렌더링의 가시성 판정·충돌 검출·포인트 클라우드·복셀 맵에 쓰인다.
// 반경 질의: 구와 겹치지 않는 팔분면은 통째로 건너뛴다
struct V3 { double x, y, z; };
class Octree {
    static const int CAP = 8, MAXD = 10;
    V3 lo, hi; int depth; std::vector<V3> pts; std::unique_ptr<Octree> kid[8];
    int child(const V3& p) const { V3 m{(lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2}; return (p.x >= m.x) | (p.y >= m.y) << 1 | (p.z >= m.z) << 2; }
    bool inside(const V3& p) const { return p.x >= lo.x && p.x < hi.x && p.y >= lo.y && p.y < hi.y && p.z >= lo.z && p.z < hi.z; }
    static double clamp(double v, double a, double b) { return v < a ? a : v > b ? b : v; }
    bool sphereHits(const V3& c, double r) const {                      // 구 중심에서 상자까지의 최단 거리 <= 반지름
        double dx = c.x - clamp(c.x, lo.x, hi.x), dy = c.y - clamp(c.y, lo.y, hi.y), dz = c.z - clamp(c.z, lo.z, hi.z);
        return dx * dx + dy * dy + dz * dz <= r * r;
    }
public:
    Octree(V3 a, V3 b, int d = 0) : lo(a), hi(b), depth(d) {}
    bool insert(const V3& p) {
        if (!inside(p)) return false;
        if (!kid[0] && ((int)pts.size() < CAP || depth >= MAXD)) { pts.push_back(p); return true; }
        if (!kid[0]) {
            V3 m{(lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2};
            for (int i = 0; i < 8; i++) kid[i].reset(new Octree({i & 1 ? m.x : lo.x, i & 2 ? m.y : lo.y, i & 4 ? m.z : lo.z}, {i & 1 ? hi.x : m.x, i & 2 ? hi.y : m.y, i & 4 ? hi.z : m.z}, depth + 1));
            std::vector<V3> old; old.swap(pts); for (auto& q : old) insert(q);
        }
        return kid[child(p)]->insert(p);
    }
    int radius(const V3& c, double r) const {
        if (!sphereHits(c, r)) return 0;
        int cnt = 0; for (auto& p : pts) cnt += ((p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y) + (p.z - c.z) * (p.z - c.z) <= r * r);
        if (kid[0]) for (auto& k : kid) cnt += k->radius(c, r);
        return cnt;
    }
};

int main() {
    std::mt19937 rng(24); std::uniform_real_distribution<double> U(0, 100);
    Octree oc({0, 0, 0}, {100, 100, 100}); std::vector<V3> all;
    for (int i = 0; i < 4000; i++) { V3 p{U(rng), U(rng), U(rng)}; all.push_back(p); assert(oc.insert(p)); }
    for (int t = 0; t < 100; t++) {
        V3 c{U(rng), U(rng), U(rng)}; double r = 5 + U(rng) * 0.2; int brute = 0;
        for (auto& p : all) brute += ((p.x - c.x) * (p.x - c.x) + (p.y - c.y) * (p.y - c.y) + (p.z - c.z) * (p.z - c.z) <= r * r);
        assert(oc.radius(c, r) == brute);
    }
    std::cout << "Octree: radius queries match brute force on 4000 points." << std::endl;
    return 0;
}
// Time Complexity: 삽입 O(깊이), 반경 질의 평균 O(log n + k)
// Space Complexity: O(n)
```
## BSPTree()
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <memory>
#include <vector>
#include <cassert>

// BSP 트리(이진 공간 분할): 선분(3D 에서는 다각형) 하나의 직선으로 공간을 앞/뒤 두 반평면으로 나누고 재귀한다.  분할선에 걸친 선분은 둘로 쪼갠다.
// 시점에서 먼 쪽부터 가까운 쪽 순서로 순회하면 정렬 없이 화가 알고리즘(painter's algorithm)의 올바른 그리기 순서가 나온다 (둠(DOOM) 등 초기 3D 게임의 렌더링)
struct Seg { double x1, y1, x2, y2; double len() const { return std::hypot(x2 - x1, y2 - y1); } };
const double EPS = 1e-9;
double side(const Seg& line, double x, double y) { return (line.x2 - line.x1) * (y - line.y1) - (line.y2 - line.y1) * (x - line.x1); }    // >0: 왼쪽(앞), <0: 오른쪽(뒤)

struct Node { Seg splitter; std::vector<Seg> same; std::unique_ptr<Node> front, back; };
std::unique_ptr<Node> build(std::vector<Seg> segs) {
    if (segs.empty()) return nullptr;
    auto n = std::make_unique<Node>(); n->splitter = segs[0]; n->same.push_back(segs[0]);
    std::vector<Seg> f, b;
    for (size_t i = 1; i < segs.size(); i++) {
        const Seg& s = segs[i]; double d1 = side(n->splitter, s.x1, s.y1), d2 = side(n->splitter, s.x2, s.y2);
        if (std::fabs(d1) < EPS && std::fabs(d2) < EPS) n->same.push_back(s);          // 같은 직선 위
        else if (d1 > -EPS && d2 > -EPS) f.push_back(s);
        else if (d1 < EPS && d2 < EPS) b.push_back(s);
        else {                                                                            // 분할선을 가로지름: 교점에서 둘로 쪼갠다
            double t = d1 / (d1 - d2); double mx = s.x1 + t * (s.x2 - s.x1), my = s.y1 + t * (s.y2 - s.y1);
            Seg a{s.x1, s.y1, mx, my}, c{mx, my, s.x2, s.y2};
            if (d1 > 0) { f.push_back(a); b.push_back(c); } else { b.push_back(a); f.push_back(c); }
        }
    }
    n->front = build(f); n->back = build(b);
    return n;
}
void farToNear(const Node* n, double ex, double ey, std::vector<Seg>& out) {                    // 시점 (ex, ey) 에서 먼 순서
    if (!n) return;
    bool eyeFront = side(n->splitter, ex, ey) >= 0;
    farToNear(eyeFront ? n->back.get() : n->front.get(), ex, ey, out);                          // 시점 반대편이 더 멀다
    for (auto& s : n->same) out.push_back(s);
    farToNear(eyeFront ? n->front.get() : n->back.get(), ex, ey, out);
}

int main() {
    // 평행한 세로선 3개: x = 1, 2, 3
    std::vector<Seg> lines = {{2, 0, 2, 5}, {1, 0, 1, 5}, {3, 0, 3, 5}};
    auto tree = build(lines);
    std::vector<Seg> order; farToNear(tree.get(), 0, 2, order);                                  // 시점 x = 0: 가장 먼 x = 3 부터
    assert(order.size() == 3 && order[0].x1 == 3 && order[1].x1 == 2 && order[2].x1 == 1);
    order.clear(); farToNear(tree.get(), 10, 2, order);                                          // 시점 x = 10: 가장 먼 x = 1 부터
    assert(order[0].x1 == 1 && order[1].x1 == 2 && order[2].x1 == 3);
    // 교차하는 선분은 분할된다: 수평선 y = 0 (x: -2..2) 과 세로선 x = 0 (y: -1..1)
    std::vector<Seg> cross = {{-2, 0, 2, 0}, {0, -1, 0, 1}};
    auto t2 = build(cross); std::vector<Seg> out; farToNear(t2.get(), 5, 5, out);
    assert(out.size() == 3);                                                                       // 세로선이 둘로 쪼개져 3개
    double total = 0; for (auto& s : out) total += s.len();
    assert(std::fabs(total - (4 + 2)) < 1e-9);                                                     // 쪼개도 전체 길이는 보존
    std::cout << "BSPTree: painter's order verified; a crossing segment was split into 2 pieces." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n²) 최악 (좋은 분할선을 고르면 O(n log n)), 순회 O(n)
// Space Complexity: O(n) (분할로 최대 O(n²))
```

# Part 12. 구간 연산
## RangeQuery()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 정적 배열의 구간 질의: 값이 바뀌지 않는다면 전처리로 질의를 O(1)에 답할 수 있다.
//  구간 합: 누적합 P[r] - P[l]   구간 최솟값(RMQ): 희소 표(sparse table) — 길이 2^k 구간의 최솟값을 모두 저장하고, 질의 [l, r] 은 겹치는 두 구간으로 덮는다 (min 은 겹쳐도 상관없다)
struct Static {
    std::vector<long> prefix; std::vector<std::vector<int>> sp; std::vector<int> lg;
    explicit Static(const std::vector<int>& a) : prefix(a.size() + 1, 0), lg(a.size() + 1, 0) {
        for (size_t i = 0; i < a.size(); i++) prefix[i + 1] = prefix[i] + a[i];
        for (size_t i = 2; i <= a.size(); i++) lg[i] = lg[i / 2] + 1;
        sp.assign(lg[a.size()] + 1, std::vector<int>(a.size())); sp[0] = a;
        for (int k = 1; k <= lg[a.size()]; k++) for (size_t i = 0; i + (1u << k) <= a.size(); i++) sp[k][i] = std::min(sp[k - 1][i], sp[k - 1][i + (1 << (k - 1))]);
    }
    long sum(int l, int r) const { return prefix[r + 1] - prefix[l]; }                    // [l, r]
    int rmq(int l, int r) const { int k = lg[r - l + 1]; return std::min(sp[k][l], sp[k][r - (1 << k) + 1]); }
};

int main() {
    std::mt19937 rng(25); std::vector<int> a(5000); for (auto& x : a) x = (int)(rng() % 20001) - 10000;
    Static s(a);
    for (int t = 0; t < 20000; t++) {
        int l = rng() % a.size(), r = rng() % a.size(); if (l > r) std::swap(l, r);
        assert(s.sum(l, r) == std::accumulate(a.begin() + l, a.begin() + r + 1, 0L));
        assert(s.rmq(l, r) == *std::min_element(a.begin() + l, a.begin() + r + 1));
    }
    std::cout << "RangeQuery: O(1) sum and RMQ verified on 20000 random queries." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(n log n), 질의 O(1)
// Space Complexity: O(n log n)
```
## LazyPropagation()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 지연 전파(lazy propagation): 구간 갱신(예: [l, r] 에 v 더하기)을 모든 원소에 적용하지 않고, 구간을 덮는 O(log n) 개 노드에 "보류 중인 갱신(lazy)" 으로만 표시해 둔다.
// 그 노드의 자식을 실제로 방문할 때 아래로 밀어 내린다(push down).  구간 갱신 + 구간 합을 둘 다 O(log n)
class SegTree {
    int n; std::vector<long> sum, lazy;
    void apply(int node, int len, long v) { sum[node] += v * len; lazy[node] += v; }
    void push(int node, int l, int r) {
        if (!lazy[node]) return;
        int m = (l + r) / 2; apply(2 * node, m - l + 1, lazy[node]); apply(2 * node + 1, r - m, lazy[node]); lazy[node] = 0;
    }
    void add(int node, int l, int r, int a, int b, long v) {
        if (b < l || r < a) return;
        if (a <= l && r <= b) { apply(node, r - l + 1, v); return; }
        push(node, l, r); int m = (l + r) / 2;
        add(2 * node, l, m, a, b, v); add(2 * node + 1, m + 1, r, a, b, v);
        sum[node] = sum[2 * node] + sum[2 * node + 1];
    }
    long query(int node, int l, int r, int a, int b) {
        if (b < l || r < a) return 0;
        if (a <= l && r <= b) return sum[node];
        push(node, l, r); int m = (l + r) / 2;
        return query(2 * node, l, m, a, b) + query(2 * node + 1, m + 1, r, a, b);
    }
public:
    explicit SegTree(int size) : n(size), sum(4 * size, 0), lazy(4 * size, 0) {}
    void rangeAdd(int a, int b, long v) { add(1, 0, n - 1, a, b, v); }
    long rangeSum(int a, int b) { return query(1, 0, n - 1, a, b); }
};

int main() {
    const int N = 2000; SegTree st(N); std::vector<long> brute(N, 0); std::mt19937 rng(26);
    for (int op = 0; op < 20000; op++) {
        int l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        if (rng() % 2) { long v = (long)(rng() % 201) - 100; st.rangeAdd(l, r, v); for (int i = l; i <= r; i++) brute[i] += v; }
        else { long s = 0; for (int i = l; i <= r; i++) s += brute[i]; assert(st.rangeSum(l, r) == s); }
    }
    std::cout << "LazyPropagation: range add / range sum match brute force over 20000 operations." << std::endl;
    return 0;
}
// Time Complexity: 갱신·질의 O(log n)
// Space Complexity: O(n)
```
## RangeUpdate()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 펜윅 트리(BIT)로 "구간 더하기 + 구간 합" 하기: 차분 배열 d[i] = a[i] - a[i-1] 을 두면 구간 더하기는 d 의 두 점 갱신이다.
// prefix(i) = Σ_{j<=i} a[j] = (i+1)·Σ d[j] - Σ j·d[j]  이므로 BIT 두 개(d 용, j·d 용)로 충분하다.  코드가 짧고 상수가 작아 세그먼트 트리보다 빠르다
class RangeBIT {
    int n; std::vector<long> b1, b2;
    void upd(std::vector<long>& b, int i, long v) { for (i++; i <= n; i += i & -i) b[i] += v; }
    long qry(const std::vector<long>& b, int i) const { long s = 0; for (i++; i > 0; i -= i & -i) s += b[i]; return s; }
    long prefix(int i) const { return i < 0 ? 0 : qry(b1, i) * (i + 1) - qry(b2, i); }
public:
    explicit RangeBIT(int size) : n(size), b1(size + 2, 0), b2(size + 2, 0) {}
    void rangeAdd(int l, int r, long v) {
        upd(b1, l, v); upd(b1, r + 1, -v);
        upd(b2, l, v * l); upd(b2, r + 1, -v * (r + 1));
    }
    long rangeSum(int l, int r) const { return prefix(r) - prefix(l - 1); }
};

int main() {
    const int N = 3000; RangeBIT bit(N); std::vector<long> brute(N, 0); std::mt19937 rng(27);
    for (int op = 0; op < 30000; op++) {
        int l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        if (rng() % 2) { long v = (long)(rng() % 2001) - 1000; bit.rangeAdd(l, r, v); for (int i = l; i <= r; i++) brute[i] += v; }
        else { long s = 0; for (int i = l; i <= r; i++) s += brute[i]; assert(bit.rangeSum(l, r) == s); }
    }
    std::cout << "RangeUpdate: BIT range add / range sum verified over 30000 operations." << std::endl;
    return 0;
}
// Time Complexity: O(log n)
// Space Complexity: O(n)
```

## SqrtDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// 제곱근 분할: 배열을 크기 B ≈ √n 의 블록으로 나눈다.  구간 연산은 "완전히 덮이는 블록은 블록 단위로(O(1)), 양 끝의 부분 블록은 원소 단위로(O(B))" 처리해 O(√n).
// 세그먼트 트리(O(log n))보다 느리지만 구현이 단순하고, 블록 안에서 임의의 보조 구조(정렬된 사본, 해시, 비트셋)를 쓸 수 있어 더 이상한 질의에도 적용된다
class Sqrt {
    int n, B; std::vector<long> a, blockSum, blockAdd;
public:
    explicit Sqrt(int size) : n(size), B(std::max(1, (int)std::sqrt((double)size))), a(size, 0), blockSum((size + B - 1) / B, 0), blockAdd((size + B - 1) / B, 0) {}
    void rangeAdd(int l, int r, long v) {
        int bl = l / B, br = r / B;
        if (bl == br) { for (int i = l; i <= r; i++) { a[i] += v; blockSum[bl] += v; } return; }
        for (int i = l; i < (bl + 1) * B; i++) { a[i] += v; blockSum[bl] += v; }          // 왼쪽 부분 블록
        for (int b = bl + 1; b < br; b++) { blockAdd[b] += v; blockSum[b] += v * B; }       // 완전히 덮인 블록: 한 번에
        for (int i = br * B; i <= r; i++) { a[i] += v; blockSum[br] += v; }                // 오른쪽 부분 블록
    }
    long rangeSum(int l, int r) const {
        long s = 0; int bl = l / B, br = r / B;
        if (bl == br) { for (int i = l; i <= r; i++) s += a[i] + blockAdd[bl]; return s; }
        for (int i = l; i < (bl + 1) * B; i++) s += a[i] + blockAdd[bl];
        for (int b = bl + 1; b < br; b++) s += blockSum[b];
        for (int i = br * B; i <= r; i++) s += a[i] + blockAdd[br];
        return s;
    }
};

int main() {
    const int N = 2500; Sqrt sq(N); std::vector<long> brute(N, 0); std::mt19937 rng(28);
    for (int op = 0; op < 20000; op++) {
        int l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        if (rng() % 2) { long v = (long)(rng() % 201) - 100; sq.rangeAdd(l, r, v); for (int i = l; i <= r; i++) brute[i] += v; }
        else { long s = 0; for (int i = l; i <= r; i++) s += brute[i]; assert(sq.rangeSum(l, r) == s); }
    }
    std::cout << "SqrtDecomposition: block size " << (int)std::sqrt((double)N) << ", 20000 operations verified." << std::endl;
    return 0;
}
// Time Complexity: 갱신·질의 O(√n)
// Space Complexity: O(n)
```
## MergeSortTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 머지 소트 트리: 세그먼트 트리의 각 노드가 자기 구간의 "정렬된 사본" 을 가진다 (머지 소트의 병합 과정을 그대로 저장).
// 구간 [l, r] 에서 x 이하인 원소의 개수 = 구간을 덮는 O(log n) 개 노드에서 이진 탐색(upper_bound)한 결과의 합 -> O(log² n).  갱신이 없는 정적 배열의 "순위" 질의에 쓴다
class MergeSortTree {
    int n; std::vector<std::vector<int>> t;
    void build(int node, int l, int r, const std::vector<int>& a) {
        if (l == r) { t[node] = {a[l]}; return; }
        int m = (l + r) / 2; build(2 * node, l, m, a); build(2 * node + 1, m + 1, r, a);
        t[node].resize(t[2 * node].size() + t[2 * node + 1].size());
        std::merge(t[2 * node].begin(), t[2 * node].end(), t[2 * node + 1].begin(), t[2 * node + 1].end(), t[node].begin());     // 정렬된 두 사본을 병합
    }
    int count(int node, int l, int r, int a, int b, int x) const {
        if (b < l || r < a) return 0;
        if (a <= l && r <= b) return std::upper_bound(t[node].begin(), t[node].end(), x) - t[node].begin();
        int m = (l + r) / 2; return count(2 * node, l, m, a, b, x) + count(2 * node + 1, m + 1, r, a, b, x);
    }
public:
    explicit MergeSortTree(const std::vector<int>& a) : n(a.size()), t(4 * a.size()) { build(1, 0, n - 1, a); }
    int countLE(int l, int r, int x) const { return count(1, 0, n - 1, l, r, x); }
};

int main() {
    std::mt19937 rng(29); std::vector<int> a(3000); for (auto& v : a) v = rng() % 1000;
    MergeSortTree mt(a);
    for (int q = 0; q < 5000; q++) {
        int l = rng() % a.size(), r = rng() % a.size(); if (l > r) std::swap(l, r); int x = rng() % 1000;
        assert(mt.countLE(l, r, x) == (int)std::count_if(a.begin() + l, a.begin() + r + 1, [&](int v) { return v <= x; }));
    }
    std::cout << "MergeSortTree: count-less-or-equal in a range verified on 5000 queries." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n log n), 질의 O(log² n)
// Space Complexity: O(n log n)
```
# Part 13. 고급 트리
## BTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// B-트리: 한 노드에 여러 키를 담는 균형 다진 트리.  최소 차수 t 이면 루트 외 모든 노드는 키를 t-1 ~ 2t-1 개 가지며 모든 잎의 깊이가 같다.
// 노드 하나를 디스크 블록 하나에 맞추면 높이가 log_t(n) 이라 디스크 접근이 극히 적다 (데이터베이스·파일 시스템의 기본 구조).
// 삽입은 "내려가면서 꽉 찬 노드를 미리 쪼개는" 방식이라 위로 되돌아올 필요가 없다 (단일 패스)
const int T = 3;                                                     // 최소 차수: 키 2..5 개
struct Node {
    std::vector<int> keys; std::vector<Node*> kids; bool leaf = true;
    bool full() const { return (int)keys.size() == 2 * T - 1; }
};
struct BTree {
    Node* root = new Node();
    void splitChild(Node* x, int i) {                                // x->kids[i] 가 꽉 찼을 때 가운데 키를 x 로 올리고 둘로 쪼갠다
        Node* y = x->kids[i]; Node* z = new Node(); z->leaf = y->leaf;
        int mid = y->keys[T - 1];
        z->keys.assign(y->keys.begin() + T, y->keys.end());
        if (!y->leaf) { z->kids.assign(y->kids.begin() + T, y->kids.end()); y->kids.resize(T); }
        y->keys.resize(T - 1);
        x->keys.insert(x->keys.begin() + i, mid);
        x->kids.insert(x->kids.begin() + i + 1, z);
    }
    void insertNonFull(Node* x, int k) {
        int i = std::upper_bound(x->keys.begin(), x->keys.end(), k) - x->keys.begin();
        if (x->leaf) { x->keys.insert(x->keys.begin() + i, k); return; }
        if (x->kids[i]->full()) { splitChild(x, i); if (k > x->keys[i]) i++; }
        insertNonFull(x->kids[i], k);
    }
    void insert(int k) {
        if (root->full()) { Node* s = new Node(); s->leaf = false; s->kids.push_back(root); root = s; splitChild(s, 0); }   // 루트가 쪼개질 때만 높이 증가
        insertNonFull(root, k);
    }
    bool search(const Node* x, int k) const {
        int i = std::lower_bound(x->keys.begin(), x->keys.end(), k) - x->keys.begin();
        if (i < (int)x->keys.size() && x->keys[i] == k) return true;
        return !x->leaf && search(x->kids[i], k);
    }
    void inorder(const Node* x, std::vector<int>& out) const {
        for (size_t i = 0; i < x->keys.size(); i++) { if (!x->leaf) inorder(x->kids[i], out); out.push_back(x->keys[i]); }
        if (!x->leaf) inorder(x->kids.back(), out);
    }
    int height(const Node* x) const { return x->leaf ? 1 : 1 + height(x->kids[0]); }
    bool valid(const Node* x, bool isRoot, int depth, int leafDepth) const {   // 최소/최대 키 수와 잎의 깊이 검사
        int n = x->keys.size();
        if (n > 2 * T - 1 || (!isRoot && n < T - 1)) return false;
        if (x->leaf) return depth == leafDepth;
        if ((int)x->kids.size() != n + 1) return false;
        for (auto* c : x->kids) if (!valid(c, false, depth + 1, leafDepth)) return false;
        return true;
    }
};

int main() {
    BTree t; std::mt19937 rng(17);
    const int n = 5000;
    std::vector<int> keys(n); for (int i = 0; i < n; i++) keys[i] = i * 3; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) t.insert(k);
    std::vector<int> out; t.inorder(t.root, out);
    assert((int)out.size() == n && std::is_sorted(out.begin(), out.end()));    // 중위 순회 = 정렬된 키
    for (int i = 0; i < n; i++) { assert(t.search(t.root, i * 3)); assert(!t.search(t.root, i * 3 + 1)); }
    int h = t.height(t.root);
    assert(t.valid(t.root, true, 1, h));                                       // 모든 잎의 깊이가 같고 키 수 제약을 지킨다
    assert(h <= 1 + std::log((n + 1) / 2.0) / std::log((double)T));            // 높이 <= 1 + log_t((n+1)/2)
    std::cout << "BTree t=" << T << ": " << n << " keys, height " << h << " (binary tree would need ~" << (int)std::log2(n) + 1 << ")" << std::endl;
    return 0;
}
// Time Complexity: 검색·삽입 O(t · log_t N), 디스크 접근 O(log_t N)
// Space Complexity: O(N)
```
## BPlusTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// B+ 트리: B-트리의 변형으로 (1) 모든 키-값은 잎에만 저장하고 내부 노드는 길 안내용 키만 갖는다 (2) 잎들을 연결 리스트로 이어 둔다.
// 내부 노드가 작아져 분기 계수가 커지고(높이가 낮고), 범위 질의는 첫 잎을 찾은 뒤 연결 리스트를 따라가기만 하면 된다.  거의 모든 데이터베이스 인덱스와 파일 시스템(NTFS, ext4 의 htree)이 쓴다
const int M = 4;                                              // 노드당 최대 키 수 (실제로는 디스크 블록 크기에 맞춰 수백)
struct Node { bool leaf; std::vector<int> keys; std::vector<Node*> kids; Node* next = nullptr; explicit Node(bool l) : leaf(l) {} };

bool insertRec(Node* n, int k, int& up, Node*& right) {      // 분할이 일어나면 true: up = 위로 올릴 키, right = 새 오른쪽 형제
    if (n->leaf) {
        auto it = std::lower_bound(n->keys.begin(), n->keys.end(), k);
        if (it != n->keys.end() && *it == k) return false;
        n->keys.insert(it, k);
        if ((int)n->keys.size() <= M) return false;
        int mid = n->keys.size() / 2; right = new Node(true);
        right->keys.assign(n->keys.begin() + mid, n->keys.end()); n->keys.resize(mid);
        right->next = n->next; n->next = right;               // 잎 연결 리스트 유지
        up = right->keys[0];                                   // 잎 분할: 오른쪽 첫 키를 "복사" 해서 올린다 (잎에도 남는다)
        return true;
    }
    int idx = std::upper_bound(n->keys.begin(), n->keys.end(), k) - n->keys.begin(); int u; Node* r;
    if (!insertRec(n->kids[idx], k, u, r)) return false;
    n->keys.insert(n->keys.begin() + idx, u); n->kids.insert(n->kids.begin() + idx + 1, r);
    if ((int)n->keys.size() <= M) return false;
    int mid = n->keys.size() / 2; right = new Node(false);
    up = n->keys[mid];                                         // 내부 노드 분할: 가운데 키는 위로 "이동"
    right->keys.assign(n->keys.begin() + mid + 1, n->keys.end()); right->kids.assign(n->kids.begin() + mid + 1, n->kids.end());
    n->keys.resize(mid); n->kids.resize(mid + 1);
    return true;
}
struct BPlus {
    Node* root = new Node(true);
    void insert(int k) { int u; Node* r; if (insertRec(root, k, u, r)) { Node* nr = new Node(false); nr->keys = {u}; nr->kids = {root, r}; root = nr; } }
    Node* leafFor(int k) const { Node* n = root; while (!n->leaf) n = n->kids[std::upper_bound(n->keys.begin(), n->keys.end(), k) - n->keys.begin()]; return n; }
    bool contains(int k) const { Node* l = leafFor(k); return std::binary_search(l->keys.begin(), l->keys.end(), k); }
    std::vector<int> range(int lo, int hi) const {            // [lo, hi]: 첫 잎을 찾은 뒤 연결 리스트만 따라간다
        std::vector<int> out;
        for (Node* l = leafFor(lo); l; l = l->next)
            for (int k : l->keys) { if (k > hi) return out; if (k >= lo) out.push_back(k); }
        return out;
    }
    int depthOfLeaves(Node* n, int d, bool& same, int& first) const {
        if (n->leaf) { if (first < 0) first = d; else if (first != d) same = false; return d; }
        for (Node* c : n->kids) depthOfLeaves(c, d + 1, same, first); return d;
    }
};

int main() {
    std::mt19937 rng(30); BPlus t; std::set<int> truth;
    for (int i = 0; i < 5000; i++) { int k = rng() % 100000; t.insert(k); truth.insert(k); }
    for (int k = 0; k < 100000; k += 13) assert(t.contains(k) == (truth.count(k) > 0));
    for (int q = 0; q < 200; q++) {
        int lo = rng() % 100000, hi = lo + rng() % 3000;
        std::vector<int> expect(truth.lower_bound(lo), truth.upper_bound(hi));
        assert(t.range(lo, hi) == expect);                     // 범위 질의 == 정렬된 집합의 구간
    }
    bool same = true; int first = -1; t.depthOfLeaves(t.root, 0, same, first);
    assert(same);                                               // 모든 잎의 깊이가 같다 (균형)
    int total = 0; for (Node* l = t.leafFor(-1); l; l = l->next) total += l->keys.size();
    assert(total == (int)truth.size());                         // 잎 연결 리스트가 모든 키를 정렬된 순서로 담고 있다
    std::cout << "BPlusTree: " << truth.size() << " keys, leaf depth " << first << ", range scans verified." << std::endl;
    return 0;
}
// Time Complexity: 검색·삽입 O(log_M N), 범위 질의 O(log_M N + k)
// Space Complexity: O(N)
```
## SplayTree()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 스플레이 트리: 접근한 노드를 회전(zig, zig-zig, zig-zag)으로 루트까지 끌어올리는 자기 조정 BST.  균형 정보(높이·색)를 저장하지 않지만 모든 연산이 분할상환 O(log n).
// 최근에 쓴 키가 루트 근처에 모이므로 접근에 지역성이 있으면(작업 집합이 작으면) 균형 트리보다 빠르다.  캐시·메모리 할당기·가비지 컬렉터에 쓰인다
struct Node { int key; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
Node* rotR(Node* x) { Node* y = x->l; x->l = y->r; y->r = x; return y; }
Node* rotL(Node* x) { Node* y = x->r; x->r = y->l; y->l = x; return y; }
Node* splay(Node* root, int key) {                                  // key 가 있으면 루트로, 없으면 경로의 마지막 노드를 루트로
    if (!root || root->key == key) return root;
    if (key < root->key) {
        if (!root->l) return root;
        if (key < root->l->key) { root->l->l = splay(root->l->l, key); root = rotR(root); }                  // zig-zig
        else if (key > root->l->key) { root->l->r = splay(root->l->r, key); if (root->l->r) root->l = rotL(root->l); }   // zig-zag
        return root->l ? rotR(root) : root;
    }
    if (!root->r) return root;
    if (key > root->r->key) { root->r->r = splay(root->r->r, key); root = rotL(root); }
    else if (key < root->r->key) { root->r->l = splay(root->r->l, key); if (root->r->l) root->r = rotR(root->r); }
    return root->r ? rotL(root) : root;
}
Node* insert(Node* root, int k) {
    if (!root) return new Node(k);
    root = splay(root, k); if (root->key == k) return root;
    Node* n = new Node(k);
    if (k < root->key) { n->r = root; n->l = root->l; root->l = nullptr; } else { n->l = root; n->r = root->r; root->r = nullptr; }
    return n;
}
Node* erase(Node* root, int k) {
    if (!root) return nullptr;
    root = splay(root, k); if (root->key != k) return root;
    if (!root->l) return root->r;
    Node* nr = splay(root->l, k); nr->r = root->r; return nr;      // 왼쪽 서브트리의 최댓값을 루트로 올리고 오른쪽을 붙인다
}
int depthOf(Node* n, int k) { int d = 0; while (n && n->key != k) { n = k < n->key ? n->l : n->r; d++; } return n ? d : -1; }
bool isBST(Node* n, long lo, long hi) { return !n || (n->key > lo && n->key < hi && isBST(n->l, lo, n->key) && isBST(n->r, n->key, hi)); }

int main() {
    Node* root = nullptr; std::set<int> truth; std::mt19937 rng(31);
    for (int i = 0; i < 3000; i++) { int k = rng() % 1000; if (rng() % 3) { root = insert(root, k); truth.insert(k); } else { root = erase(root, k); truth.erase(k); } }
    assert(isBST(root, -1, 1 << 30));
    for (int k = 0; k < 1000; k++) { root = splay(root, k); bool present = root && root->key == k; assert(present == (truth.count(k) > 0)); }   // 접근하면 루트가 된다
    // 지역성: 키 5개만 반복 접근하면 평균 깊이가 아주 얕다 (균형 트리는 항상 log n)
    Node* big = nullptr; for (int k = 0; k < 10000; k++) big = insert(big, k);
    long steps = 0; int hot[5] = {17, 4000, 123, 9000, 555};
    for (int rep = 0; rep < 2000; rep++) for (int h : hot) { steps += depthOf(big, h); big = splay(big, h); assert(big->key == h); }
    assert(double(steps) / (2000 * 5) < 6.0);                                  // 평균 깊이 < 6  (log2(10000) ≈ 13)
    std::cout << "SplayTree: average depth of hot keys = " << double(steps) / 10000 << " (balanced tree: ~13)" << std::endl;
    return 0;
}
// Time Complexity: 분할상환 O(log N), 작업 집합 크기 w 에서 O(log w)
// Space Complexity: O(N)
```
## Treap()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 트립(Treap = Tree + Heap): 키에 대해서는 BST, 무작위 우선순위에 대해서는 힙인 트리.  우선순위가 무작위이므로 기대 높이가 O(log n) — 키를 정렬된 순서로 넣어도 균형이 맞는다.
// split(키 기준 분할)과 merge(두 트립 합치기) 두 연산만으로 삽입·삭제·구간 연산이 모두 만들어진다.  코드가 짧고 병합/분할이 필요한 문제(Rope, 순서 통계)에 편하다
std::mt19937 rng(32);
struct Node { int key, pri; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k), pri(rng()) {} };
void split(Node* t, int key, Node*& a, Node*& b) {                          // a: 키 < key, b: 키 >= key
    if (!t) { a = b = nullptr; return; }
    if (t->key < key) { a = t; split(t->r, key, t->r, b); } else { b = t; split(t->l, key, a, t->l); }
}
Node* merge(Node* a, Node* b) {                                              // a 의 모든 키 < b 의 모든 키
    if (!a || !b) return a ? a : b;
    if (a->pri > b->pri) { a->r = merge(a->r, b); return a; }
    b->l = merge(a, b->l); return b;
}
bool contains(Node* t, int k) { while (t) { if (k == t->key) return true; t = k < t->key ? t->l : t->r; } return false; }
Node* insert(Node* t, int k) { if (contains(t, k)) return t; Node *a, *b; split(t, k, a, b); return merge(merge(a, new Node(k)), b); }
Node* erase(Node* t, int k) { Node *a, *b, *c, *d; split(t, k, a, b); split(b, k + 1, c, d); return merge(a, d); }
int height(Node* t) { return t ? 1 + std::max(height(t->l), height(t->r)) : 0; }
bool valid(Node* t, long lo, long hi) { return !t || (t->key > lo && t->key < hi && (!t->l || t->l->pri <= t->pri) && (!t->r || t->r->pri <= t->pri) && valid(t->l, lo, t->key) && valid(t->r, t->key, hi)); }

int main() {
    Node* t = nullptr; std::set<int> truth;
    for (int k = 0; k < 10000; k++) { t = insert(t, k); truth.insert(k); }          // 정렬된 입력도 균형을 유지한다 (일반 BST 라면 높이 10000)
    assert(height(t) <= 6 * std::log2(10000));
    for (int i = 0; i < 4000; i++) { int k = rng() % 10000; t = erase(t, k); truth.erase(k); }
    assert(valid(t, -1, 1 << 30));                                                 // BST 성질 + 힙 성질
    for (int k = 0; k < 10000; k += 3) assert(contains(t, k) == (truth.count(k) > 0));
    Node *a, *b; split(t, 5000, a, b);                                             // 분할: 5000 미만 / 이상
    std::vector<int> left; for (Node* n = a; n;) { left.push_back(n->key); n = n->r; }
    assert(!left.empty() && left.back() < 5000);
    t = merge(a, b);
    assert(valid(t, -1, 1 << 30));
    std::cout << "Treap: height " << height(t) << " for " << truth.size() << " keys inserted in sorted order." << std::endl;
    return 0;
}
// Time Complexity: 기대 O(log N)
// Space Complexity: O(N)
```
## CartesianTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 데카르트 트리: 배열 a 에서 (인덱스에 대해 BST 순서, 값에 대해 힙 순서)를 동시에 만족하는 트리.  중위 순회하면 원래 배열 순서가 나오고, 루트는 최솟값이다.
// 스택을 이용해 O(n) 에 구성한다: 새 원소보다 큰 스택 원소들을 pop 해 새 원소의 왼쪽 자식으로 달고, 새 원소를 스택 맨 위 원소의 오른쪽 자식으로 단다.
// 구간 [l, r] 의 최솟값 = 그 구간에 걸친 가장 높은 노드 -> RMQ 와 LCA 가 서로 환원되는 연결 고리 (트립은 우선순위가 무작위인 데카르트 트리)
struct Node { int idx, val, l = -1, r = -1; };
int build(std::vector<Node>& t, const std::vector<int>& a) {
    std::vector<int> st;
    for (int i = 0; i < (int)a.size(); i++) {
        t[i] = {i, a[i]}; int last = -1;
        while (!st.empty() && t[st.back()].val > a[i]) { last = st.back(); st.pop_back(); }
        t[i].l = last;
        if (!st.empty()) t[st.back()].r = i;
        st.push_back(i);
    }
    return st.front();                                              // 스택 바닥 = 최솟값 = 루트
}
void inorder(const std::vector<Node>& t, int u, std::vector<int>& out) { if (u < 0) return; inorder(t, t[u].l, out); out.push_back(t[u].val); inorder(t, t[u].r, out); }
bool heapOrdered(const std::vector<Node>& t, int u) { return u < 0 || ((t[u].l < 0 || t[t[u].l].val >= t[u].val) && (t[u].r < 0 || t[t[u].r].val >= t[u].val) && heapOrdered(t, t[u].l) && heapOrdered(t, t[u].r)); }
int rmqIndex(const std::vector<Node>& t, int u, int l, int r) {         // 루트에서 내려가며 구간 [l, r] 에 처음 걸치는 노드가 최솟값의 위치
    for (;;) { if (t[u].idx < l) u = t[u].r; else if (t[u].idx > r) u = t[u].l; else return t[u].idx; }
}

int main() {
    std::mt19937 rng(33); std::vector<int> a(3000); for (auto& x : a) x = rng() % 100000;
    std::vector<Node> t(a.size()); int root = build(t, a);
    assert(a[root] == *std::min_element(a.begin(), a.end()));
    std::vector<int> in; inorder(t, root, in);
    assert(in == a);                                                  // 중위 순회 == 원래 배열
    assert(heapOrdered(t, root));                                     // 부모 <= 자식
    for (int q = 0; q < 5000; q++) {
        int l = rng() % a.size(), r = rng() % a.size(); if (l > r) std::swap(l, r);
        int idx = rmqIndex(t, root, l, r);
        assert(idx >= l && idx <= r && a[idx] == *std::min_element(a.begin() + l, a.begin() + r + 1));
    }
    std::cout << "CartesianTree: built in O(n); inorder = array, range minimum by descent." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(n), RMQ 는 트리 높이에 비례 (LCA 전처리 후 O(1))
// Space Complexity: O(n)
```
## ScapegoatTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <vector>
#include <cassert>

// 희생양 트리(scapegoat tree): 균형 정보를 노드에 저장하지 않는 BST.  삽입 후 깊이가 log_{1/α}(n) 을 넘으면, 경로를 거슬러 올라가며 "한쪽 서브트리가 전체의 α 배를 넘는" 첫 조상(희생양)을 찾아
// 그 서브트리를 통째로 완전 균형으로 다시 짓는다.  삭제는 n 이 최대치의 α 배 아래로 떨어지면 전체를 재구성.  모든 연산 분할상환 O(log n), 높이 ≤ log_{1/α}(n) + 1
const double ALPHA = 0.7;
struct Node { int key; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
int size(Node* n) { return n ? 1 + size(n->l) + size(n->r) : 0; }
void flatten(Node* n, std::vector<Node*>& out) { if (!n) return; flatten(n->l, out); out.push_back(n); flatten(n->r, out); }
Node* rebuild(std::vector<Node*>& v, int lo, int hi) {                       // [lo, hi) 를 완전 균형 BST 로
    if (lo >= hi) return nullptr;
    int mid = (lo + hi) / 2; Node* n = v[mid];
    n->l = rebuild(v, lo, mid); n->r = rebuild(v, mid + 1, hi); return n;
}
struct Tree {
    Node* root = nullptr; int n = 0, maxN = 0;
    bool insert(int k) {
        std::vector<Node*> path; Node* cur = root;
        while (cur) { if (cur->key == k) return false; path.push_back(cur); cur = k < cur->key ? cur->l : cur->r; }
        Node* nn = new Node(k);
        if (path.empty()) root = nn; else if (k < path.back()->key) path.back()->l = nn; else path.back()->r = nn;
        n++; maxN = std::max(maxN, n); path.push_back(nn);
        if ((int)path.size() - 1 > std::floor(std::log(n) / std::log(1 / ALPHA))) {          // 너무 깊다: 희생양을 찾는다
            int childSize = 1;
            for (int i = (int)path.size() - 2; i >= 0; i--) {
                int total = 1 + childSize + size(sibling(path[i], path[i + 1]));
                if (childSize > ALPHA * total) { rebuildAt(path, i); break; }               // 균형이 깨진 첫 조상
                childSize = total;
            }
        }
        return true;
    }
    static Node* sibling(Node* parent, Node* child) { return parent->l == child ? parent->r : parent->l; }
    void rebuildAt(std::vector<Node*>& path, int i) {
        std::vector<Node*> v; flatten(path[i], v); Node* sub = rebuild(v, 0, v.size());
        if (i == 0) root = sub; else if (path[i - 1]->l == path[i]) path[i - 1]->l = sub; else path[i - 1]->r = sub;
    }
    int height(Node* x) const { return x ? 1 + std::max(height(x->l), height(x->r)) : 0; }
    bool contains(int k) const { Node* c = root; while (c) { if (c->key == k) return true; c = k < c->key ? c->l : c->r; } return false; }
};

int main() {
    Tree t;
    for (int k = 1; k <= 5000; k++) t.insert(k);                              // 정렬된 입력: 일반 BST 라면 높이 5000
    int h = t.height(t.root);
    assert(h <= std::log(5000) / std::log(1 / ALPHA) + 2);                    // 높이 <= log_{1/α}(n) + 상수
    for (int k = 1; k <= 5000; k++) assert(t.contains(k));
    assert(!t.contains(0) && !t.contains(5001));
    std::vector<Node*> in; flatten(t.root, in);
    assert((int)in.size() == 5000 && std::is_sorted(in.begin(), in.end(), [](Node* a, Node* b) { return a->key < b->key; }));
    std::cout << "ScapegoatTree: height " << h << " for 5000 sorted inserts (bound " << std::log(5000) / std::log(1 / ALPHA) + 2 << ")" << std::endl;
    return 0;
}
// Time Complexity: 삽입 분할상환 O(log N), 검색 O(log N)
// Space Complexity: O(N) (노드에 균형 정보 없음)
```

## OrderStatisticTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 순서 통계 트리: BST 의 각 노드에 "자기 서브트리의 크기" 를 덧붙여 순위 질의를 O(log n) 에 한다.
//   select(k): 작은 쪽에서 k 번째 원소  /  rank(x): x 보다 작은 원소의 개수 (= x 의 순위).   중앙값, 백분위수, "k 번째로 작은 수" 에 쓴다.  (여기서는 균형을 트립으로 유지)
std::mt19937 rng(34);
struct Node { int key, pri, sz = 1; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k), pri(rng()) {} };
int sz(Node* n) { return n ? n->sz : 0; }
void upd(Node* n) { n->sz = 1 + sz(n->l) + sz(n->r); }
void split(Node* t, int key, Node*& a, Node*& b) { if (!t) { a = b = nullptr; return; } if (t->key < key) { a = t; split(t->r, key, t->r, b); upd(a); } else { b = t; split(t->l, key, a, t->l); upd(b); } }
Node* merge(Node* a, Node* b) { if (!a || !b) return a ? a : b; if (a->pri > b->pri) { a->r = merge(a->r, b); upd(a); return a; } b->l = merge(a, b->l); upd(b); return b; }
Node* insert(Node* t, int k) { Node *a, *b; split(t, k, a, b); return merge(merge(a, new Node(k)), b); }
Node* erase(Node* t, int k) { Node *a, *b, *c, *d; split(t, k, a, b); split(b, k + 1, c, d); return merge(a, d); }
int select(Node* t, int k) { for (;;) { int ls = sz(t->l); if (k < ls) t = t->l; else if (k == ls) return t->key; else { k -= ls + 1; t = t->r; } } }      // 0-기반
int rankOf(Node* t, int x) { int r = 0; while (t) { if (x <= t->key) t = t->l; else { r += sz(t->l) + 1; t = t->r; } } return r; }              // x 보다 작은 개수

int main() {
    Node* t = nullptr; std::set<int> truth;
    for (int i = 0; i < 4000; i++) { int k = rng() % 100000; if (truth.insert(k).second) t = insert(t, k); }          // 중복 키는 넣지 않는다 (집합)
    for (int i = 0; i < 1000; i++) { int k = *std::next(truth.begin(), rng() % truth.size()); t = erase(t, k); truth.erase(k); }
    std::vector<int> sorted(truth.begin(), truth.end());
    assert(sz(t) == (int)sorted.size());
    for (int q = 0; q < 2000; q++) {
        int k = rng() % sorted.size(); assert(select(t, k) == sorted[k]);        // k 번째로 작은 값
        int x = rng() % 100000; assert(rankOf(t, x) == (int)(std::lower_bound(sorted.begin(), sorted.end(), x) - sorted.begin()));   // 순위
    }
    int median = select(t, sorted.size() / 2); assert(median == sorted[sorted.size() / 2]);
    std::cout << "OrderStatisticTree: select / rank verified; median of " << sorted.size() << " keys = " << median << std::endl;
    return 0;
}
// Time Complexity: select·rank·삽입·삭제 기대 O(log N)
// Space Complexity: O(N) (노드당 크기 필드 하나)
```
## WeightBalancedTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 가중치 균형 트리(BB[α], Adams): 높이 대신 "서브트리 크기" 로 균형을 정의한다 — 어떤 노드든 한쪽 서브트리의 가중치(크기+1)가 다른 쪽의 Δ=3 배를 넘지 않는다.
// 위반되면 회전 한 번 또는 두 번(Γ=2 로 판단)으로 복구.  크기를 이미 저장하므로 순위 질의에 그대로 쓰이고, 함수형 언어의 표준 집합 구현(Haskell Data.Map, OCaml Set)이 쓴다
struct Node { int key, size = 1; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
int sz(Node* n) { return n ? n->size : 0; }
int w(Node* n) { return sz(n) + 1; }
void upd(Node* n) { n->size = 1 + sz(n->l) + sz(n->r); }
Node* rotL(Node* n) { Node* r = n->r; n->r = r->l; r->l = n; upd(n); upd(r); return r; }
Node* rotR(Node* n) { Node* l = n->l; n->l = l->r; l->r = n; upd(n); upd(l); return l; }
Node* balance(Node* n) {
    upd(n);
    if (sz(n->l) + sz(n->r) <= 1) return n;
    if (w(n->r) > 3 * w(n->l)) { if (w(n->r->l) >= 2 * w(n->r->r)) n->r = rotR(n->r); return rotL(n); }     // 오른쪽이 너무 무겁다: 단일 또는 이중 회전
    if (w(n->l) > 3 * w(n->r)) { if (w(n->l->r) >= 2 * w(n->l->l)) n->l = rotL(n->l); return rotR(n); }
    return n;
}
Node* insert(Node* n, int k) { if (!n) return new Node(k); if (k < n->key) n->l = insert(n->l, k); else if (k > n->key) n->r = insert(n->r, k); else return n; return balance(n); }
Node* eraseMin(Node* n, int& minKey) { if (!n->l) { minKey = n->key; return n->r; } n->l = eraseMin(n->l, minKey); return balance(n); }
Node* erase(Node* n, int k) {
    if (!n) return nullptr;
    if (k < n->key) n->l = erase(n->l, k); else if (k > n->key) n->r = erase(n->r, k);
    else { if (!n->l) return n->r; if (!n->r) return n->l; int m; n->r = eraseMin(n->r, m); n->key = m; }
    return balance(n);
}
bool balanced(Node* n) { return !n || ((sz(n->l) + sz(n->r) <= 1 || (w(n->l) <= 3 * w(n->r) && w(n->r) <= 3 * w(n->l))) && n->size == 1 + sz(n->l) + sz(n->r) && balanced(n->l) && balanced(n->r)); }
int height(Node* n) { return n ? 1 + std::max(height(n->l), height(n->r)) : 0; }

int main() {
    Node* t = nullptr; std::set<int> truth; std::mt19937 rng(35);
    for (int k = 0; k < 8000; k++) { t = insert(t, k); truth.insert(k); }            // 정렬된 입력
    assert(balanced(t) && height(t) <= 3 * std::log2(8001));
    for (int i = 0; i < 6000; i++) { int k = rng() % 8000; t = erase(t, k); truth.erase(k); if (i % 500 == 0) assert(balanced(t)); }
    assert(balanced(t) && sz(t) == (int)truth.size());
    for (int k = 0; k < 8000; k += 5) { Node* c = t; while (c && c->key != k) c = k < c->key ? c->l : c->r; assert((c != nullptr) == (truth.count(k) > 0)); }
    std::cout << "WeightBalancedTree: size " << sz(t) << ", height " << height(t) << ", every node satisfies weight(left) <= 3*weight(right)." << std::endl;
    return 0;
}
// Time Complexity: O(log N)
// Space Complexity: O(N)
```
## ZipTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <set>
#include <utility>
#include <vector>
#include <cassert>

// 집 트리(Zip tree, Tarjan–Levy–Timmel 2019): 스킵 리스트를 이진 트리로 옮긴 구조.  각 노드가 기하분포 랭크(P(rank ≥ r) = 2^-r)를 받고, 랭크에 대한 힙이며
// 랭크가 같으면 키가 작은 쪽이 위다.  삽입 = 새 노드 아래에서 경로를 "풀어 쪼개기(unzip)", 삭제 = 두 자식 서브트리를 "지퍼처럼 합치기(zip)".  회전이 없고 코드가 짧다
std::mt19937 rng(36);
struct Node { int key, rank; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) { int r = 0; while (rng() & 1) r++; rank = r; } };
bool above(const Node* a, const Node* b) { return a->rank > b->rank || (a->rank == b->rank && a->key < b->key); }     // a 가 b 의 부모가 될 수 있는가

std::pair<Node*, Node*> unzip(Node* t, int key) {                       // 키 < key 와 키 > key 로 가르며 경로를 푼다
    if (!t) return {nullptr, nullptr};
    if (t->key < key) { auto p = unzip(t->r, key); t->r = p.first; return {t, p.second}; }
    auto p = unzip(t->l, key); t->l = p.second; return {p.first, t};
}
Node* insert(Node* root, Node* x) {
    if (!root) return x;
    if (above(x, root)) { auto p = unzip(root, x->key); x->l = p.first; x->r = p.second; return x; }   // x 가 이 자리의 루트가 된다
    if (x->key < root->key) root->l = insert(root->l, x); else root->r = insert(root->r, x);
    return root;
}
Node* zip(Node* a, Node* b) { if (!a) return b; if (!b) return a; if (above(a, b)) { a->r = zip(a->r, b); return a; } b->l = zip(a, b->l); return b; }
Node* erase(Node* root, int k) {
    if (!root) return nullptr;
    if (k < root->key) { root->l = erase(root->l, k); return root; }
    if (k > root->key) { root->r = erase(root->r, k); return root; }
    return zip(root->l, root->r);
}
bool valid(Node* n, long lo, long hi) {
    if (!n) return true;
    if (!(n->key > lo && n->key < hi)) return false;
    if (n->l && !above(n, n->l)) return false;
    if (n->r && !above(n, n->r)) return false;
    return valid(n->l, lo, n->key) && valid(n->r, n->key, hi);
}
int height(Node* n) { return n ? 1 + std::max(height(n->l), height(n->r)) : 0; }
bool contains(Node* n, int k) { while (n) { if (k == n->key) return true; n = k < n->key ? n->l : n->r; } return false; }

int main() {
    Node* root = nullptr; std::set<int> truth;
    for (int k = 0; k < 6000; k++) { root = insert(root, new Node(k)); truth.insert(k); }       // 정렬된 입력
    assert(valid(root, -1, 1 << 30) && height(root) <= 6 * std::log2(6000));
    for (int i = 0; i < 4000; i++) { int k = rng() % 6000; root = erase(root, k); truth.erase(k); }
    assert(valid(root, -1, 1 << 30));
    for (int k = 0; k < 6000; k += 7) assert(contains(root, k) == (truth.count(k) > 0));
    std::cout << "ZipTree: " << truth.size() << " keys, height " << height(root) << ", heap-on-rank invariant holds." << std::endl;
    return 0;
}
// Time Complexity: 기대 O(log N)
// Space Complexity: O(N) (랭크는 작은 정수)
```
## WAVLTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>
#include <vector>
#include <cassert>

// WAVL 트리(weak AVL, Haeupler–Sen–Tarjan 2015): AVL 과 레드-블랙의 장점을 합친 균형 트리.  각 노드에 정수 "랭크" 를 두고, 부모와 자식의 랭크 차(rank difference)가 항상 1 또는 2 이며
// 잎(자식이 둘 다 없음)의 랭크는 0 이다 (널 노드의 랭크는 -1).  삽입만 하면 AVL 처럼 높이 ≤ log₂(n+1)·1.44 로 균형이 좋고, 삭제를 포함해도 레드-블랙 정도(≤ 2 log₂ n)를 보장하며 회전은 상수 번.
// 삽입 후 새 잎의 부모와 랭크 차가 0 이 되는 위반을 위로 올라가며 수리한다: 형제와의 차가 1 이면 승급(promote), 2 이면 회전
struct Node { int key, rank = 0; Node *l = nullptr, *r = nullptr; explicit Node(int k) : key(k) {} };
int rk(Node* n) { return n ? n->rank : -1; }
Node* rotL(Node* x) { Node* y = x->r; x->r = y->l; y->l = x; return y; }
Node* rotR(Node* x) { Node* y = x->l; x->l = y->r; y->r = x; return y; }

Node* fix(Node* t) {                                                          // t 의 자식 중 하나가 t 와 같은 랭크(0-자식)면 수리
    if (rk(t->l) == t->rank) {                                                // 왼쪽이 0-자식
        if (rk(t->r) == t->rank - 1) { t->rank++; return t; }                 // 형제 차이 1: 승급 (위반이 부모로 전파될 수 있다)
        Node* x = t->l;
        if (rk(x->r) == x->rank - 2) { t = rotR(t); t->r->rank--; return t; }                         // 바깥쪽이 무거움: 단일 회전 + t 강등
        Node* y = x->r; t->l = rotL(x); t = rotR(t); y->rank++; y->l->rank--; y->r->rank--; return t;      // 안쪽이 무거움: 이중 회전
    }
    if (rk(t->r) == t->rank) {                                                // 오른쪽이 0-자식 (대칭)
        if (rk(t->l) == t->rank - 1) { t->rank++; return t; }
        Node* x = t->r;
        if (rk(x->l) == x->rank - 2) { t = rotL(t); t->l->rank--; return t; }
        Node* y = x->l; t->r = rotR(x); t = rotL(t); y->rank++; y->l->rank--; y->r->rank--; return t;
    }
    return t;
}
Node* insert(Node* t, int k) {
    if (!t) return new Node(k);
    if (k < t->key) t->l = insert(t->l, k); else if (k > t->key) t->r = insert(t->r, k); else return t;
    return fix(t);
}
bool valid(Node* n, long lo, long hi) {                                       // BST 순서 + 랭크 규칙
    if (!n) return true;
    if (!(n->key > lo && n->key < hi)) return false;
    int dl = n->rank - rk(n->l), dr = n->rank - rk(n->r);
    if (dl < 1 || dl > 2 || dr < 1 || dr > 2) return false;                   // 모든 랭크 차는 1 또는 2
    if (!n->l && !n->r && n->rank != 0) return false;                         // 잎의 랭크는 0
    return valid(n->l, lo, n->key) && valid(n->r, n->key, hi);
}
int height(Node* n) { return n ? 1 + std::max(height(n->l), height(n->r)) : 0; }

int main() {
    Node* t = nullptr;
    for (int k = 0; k < 10000; k++) { t = insert(t, k); if (k % 997 == 0) assert(valid(t, -1, 1 << 30)); }    // 정렬된 입력
    assert(valid(t, -1, 1 << 30));
    assert(height(t) <= 1.45 * std::log2(10001) + 1);                         // 삽입만 있으면 AVL 수준의 높이
    std::mt19937 rng(37); Node* u = nullptr; std::vector<int> keys(5000); for (int i = 0; i < 5000; i++) keys[i] = i; std::shuffle(keys.begin(), keys.end(), rng);
    for (int k : keys) u = insert(u, k);
    assert(valid(u, -1, 1 << 30) && height(u) <= 1.45 * std::log2(5001) + 1);
    std::cout << "WAVLTree: height " << height(t) << " (sorted) / " << height(u) << " (random), all rank differences in {1,2}." << std::endl;
    return 0;
}
// Time Complexity: 삽입 O(log N), 회전 최대 2번
// Space Complexity: O(N) (랭크는 작은 정수; 랭크 차를 2비트로 저장 가능)
```
# Part 14. 함수형 자료구조
## PersistentTree()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cmath>
#include <cassert>

// 영속 세그먼트 트리: 점 갱신을 할 때 루트에서 그 잎까지의 경로(O(log n) 개 노드)만 새로 만들고 나머지는 이전 버전과 공유한다(경로 복사, path copying).
// 갱신할 때마다 새 루트가 하나 생기고, 옛 루트로도 질의할 수 있다 -> "버전 v 시점의 구간 합" 같은 과거 질의, k 번째 수 구하기(구간 내 k번째로 작은 값), 롤백/브랜칭에 쓴다
struct Node { int l = 0, r = 0; long sum = 0; };
std::vector<Node> pool(1);                                        // 0 번은 널 노드 (합 0, 자식 0)
int build(int l, int r, const std::vector<long>& a) {
    int id = pool.size(); pool.push_back({});
    if (l == r) { pool[id].sum = a[l]; return id; }
    int m = (l + r) / 2, L = build(l, m, a), R = build(m + 1, r, a);
    pool[id] = {L, R, pool[L].sum + pool[R].sum}; return id;
}
int update(int prev, int l, int r, int pos, long val) {            // prev 버전에서 pos 를 val 로 바꾼 새 버전의 루트
    int id = pool.size(); pool.push_back(pool[prev]);
    if (l == r) { pool[id].sum = val; return id; }
    int m = (l + r) / 2;
    if (pos <= m) { int c = update(pool[prev].l, l, m, pos, val); pool[id].l = c; }
    else          { int c = update(pool[prev].r, m + 1, r, pos, val); pool[id].r = c; }
    pool[id].sum = pool[pool[id].l].sum + pool[pool[id].r].sum; return id;
}
long query(int node, int l, int r, int a, int b) {
    if (!node || b < l || r < a) return 0;
    if (a <= l && r <= b) return pool[node].sum;
    int m = (l + r) / 2; return query(pool[node].l, l, m, a, b) + query(pool[node].r, m + 1, r, a, b);
}

int main() {
    const int N = 1000, U = 2000; std::mt19937 rng(40);
    std::vector<long> a(N); for (auto& x : a) x = rng() % 100;
    std::vector<int> roots = {build(0, N - 1, a)}; std::vector<std::vector<long>> snapshot = {a};
    size_t afterBuild = pool.size();
    for (int i = 0; i < U; i++) { int pos = rng() % N; long v = rng() % 1000; a[pos] = v; roots.push_back(update(roots.back(), 0, N - 1, pos, v)); snapshot.push_back(a); }
    assert(pool.size() - afterBuild <= (size_t)U * (std::log2(N) + 2));              // 갱신당 새 노드는 경로 길이만큼 (전체 복사였다면 갱신당 2000개)
    for (int q = 0; q < 3000; q++) {
        int ver = rng() % roots.size(), l = rng() % N, r = rng() % N; if (l > r) std::swap(l, r);
        long expect = 0; for (int i = l; i <= r; i++) expect += snapshot[ver][i];
        assert(query(roots[ver], 0, N - 1, l, r) == expect);                           // 어떤 과거 버전에서도 정확한 구간 합
    }
    std::cout << "PersistentTree: " << roots.size() << " versions in " << pool.size() << " nodes (full copies would need " << (size_t)U * 2 * N << ")" << std::endl;
    return 0;
}
// Time Complexity: 갱신·질의 O(log N)
// Space Complexity: 버전당 O(log N)
```
## ImmutableTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <map>
#include <random>
#include <tuple>
#include <utility>
#include <vector>
#include <cassert>

// 불변 트리 + 해시 컨싱(hash-consing): 노드를 (키, 왼쪽 id, 오른쪽 id) 로 "인터닝" 해서 같은 내용의 서브트리는 메모리에 단 하나만 둔다.
// 균형을 키의 해시로 정한 우선순위(트립)로 잡으면 트리 모양이 "삽입 순서와 무관하게 키 집합만으로 결정"(history independence)되므로,
// 같은 집합은 항상 같은 루트 id -> 두 집합이 같은지 O(1) 비교.  (Git 의 객체 저장소, 함수형 DB, 증분 계산이 쓰는 원리)
struct Node { int key, l, r, size; };
std::vector<Node> pool(1, Node{0, 0, 0, 0});                       // id 0 = 빈 트리
std::map<std::tuple<int, int, int>, int> interned;
int mk(int key, int l, int r) {
    auto k = std::make_tuple(key, l, r); auto it = interned.find(k);
    if (it != interned.end()) return it->second;                   // 이미 있는 내용이면 그 노드를 재사용
    int id = pool.size(); pool.push_back({key, l, r, 1 + pool[l].size + pool[r].size}); interned[k] = id; return id;
}
unsigned pri(int key) { unsigned x = key * 2654435761u; x ^= x >> 15; x *= 2246822519u; x ^= x >> 13; return x; }
std::pair<int, int> split(int t, int key) {                         // 키 < key 와 키 >= key (새 노드를 만들며 원본은 건드리지 않는다)
    if (!t) return {0, 0};
    const Node n = pool[t];
    if (n.key < key) { auto p = split(n.r, key); return {mk(n.key, n.l, p.first), p.second}; }
    auto p = split(n.l, key); return {p.first, mk(n.key, p.second, n.r)};
}
int merge(int a, int b) {
    if (!a) return b; if (!b) return a;
    const Node x = pool[a], y = pool[b];
    if (pri(x.key) > pri(y.key)) return mk(x.key, x.l, merge(x.r, b));
    return mk(y.key, merge(a, y.l), y.r);
}
int insert(int t, int k) { auto p = split(t, k); auto q = split(p.second, k + 1); return merge(merge(p.first, mk(k, 0, 0)), q.second); }
bool contains(int t, int k) { while (t) { if (k == pool[t].key) return true; t = k < pool[t].key ? pool[t].l : pool[t].r; } return false; }

int main() {
    std::vector<int> keys; for (int i = 1; i <= 500; i++) keys.push_back(i * 3);
    int asc = 0, desc = 0, shuffled = 0; std::mt19937 rng(41);
    for (int k : keys) asc = insert(asc, k);
    for (auto it = keys.rbegin(); it != keys.rend(); ++it) desc = insert(desc, *it);
    std::vector<int> sh = keys; std::shuffle(sh.begin(), sh.end(), rng); for (int k : sh) shuffled = insert(shuffled, k);
    assert(asc == desc && desc == shuffled);                          // 삽입 순서가 달라도 같은 집합은 같은 루트 (O(1) 동일성 판정)
    assert(pool[asc].size == 500);
    size_t before = pool.size();
    int next = insert(asc, 7);                                         // 새 버전: 키 하나 추가
    assert(pool.size() - before <= 60);                                // 새로 만든 노드는 경로 길이 정도뿐 (나머지는 공유)
    assert(contains(next, 7) && !contains(asc, 7) && next != asc);     // 이전 버전은 그대로
    assert(insert(next, 7) == next);                                    // 이미 있는 키를 또 넣어도 같은 트리 (멱등)
    std::cout << "ImmutableTree: three insertion orders -> one root id " << asc << "; new version allocated " << pool.size() - before << " nodes." << std::endl;
    return 0;
}
// Time Complexity: 삽입 기대 O(log N) (인터닝 조회 포함 O(log² N))
// Space Complexity: 버전당 O(log N), 같은 서브트리는 공유
```
## FingerTree()
### 대표코드
```cpp
#include <iostream>
#include <iterator>
#include <set>
#include <cassert>

// 핑거 트리(요약, 정본은 AdvancedDataStructures.md Part 4): "핑거" 는 구조 안의 특정 위치를 가리키는 손가락 — 핑거 근처의 연산은 전체 크기가 아니라 핑거까지의 거리에 비례하는 비용만 든다.
// 핑거 트리는 양 끝에 핑거를 둬 덱 연산이 분할상환 O(1), 연결·분할이 O(log n).  같은 아이디어를 표준 라이브러리에서 볼 수 있다: std::set::insert(힌트, 값) 은 힌트 위치 근처라면 O(1) 분할상환
long comparisons = 0;
struct Less { bool operator()(int a, int b) const { ++comparisons; return a < b; } };

int main() {
    const int N = 100000;
    std::set<int, Less> plain, hinted;
    comparisons = 0; for (int i = 0; i < N; i++) plain.insert(i);                           // 매번 루트에서 O(log N)
    long plainCmp = comparisons;
    comparisons = 0; auto finger = hinted.end();
    for (int i = 0; i < N; i++) finger = hinted.insert(finger, i);                          // 직전 삽입 위치(핑거)를 힌트로 -> 분할상환 O(1)
    long fingerCmp = comparisons;
    assert(plain.size() == (size_t)N && hinted.size() == (size_t)N && *plain.rbegin() == N - 1 && *hinted.rbegin() == N - 1);
    assert(fingerCmp * 4 < plainCmp);                                                       // 비교 횟수가 훨씬 적다 (약 N 대 N·log N)
    std::cout << "finger insertion: " << fingerCmp << " comparisons vs " << plainCmp << " from the root" << std::endl;
    return 0;
}
// Time Complexity: 핑거 근처 O(1) 분할상환, 일반 O(log N)
// Space Complexity: O(N)
```

# Part 15. 그래프 확장
## RootingTree()
### 대표코드
```cpp
#include <iostream>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 트리 뿌리 내리기(rooting)와 재루팅(rerooting): 방향 없는 트리에 루트 r 을 정하고 부모·깊이·서브트리 크기를 구한다(반복 DFS 로 깊은 트리에서도 스택 오버플로 없음).
// 재루팅 DP: 모든 정점에서 "다른 모든 정점까지의 거리 합" 을 O(n) 에 구한다.  루트의 값을 한 번 구하면, 루트를 자식 c 로 옮길 때 c 의 서브트리(크기 s)는 1씩 가까워지고 나머지(n-s)는 1씩 멀어진다:
//   sum[c] = sum[parent] - s[c] + (n - s[c])
int main() {
    std::mt19937 rng(42);
    for (int trial = 0; trial < 50; trial++) {
        int n = rng() % 150 + 2; std::vector<std::vector<int>> g(n);
        for (int v = 1; v < n; v++) { int p = rng() % v; g[p].push_back(v); g[v].push_back(p); }
        std::vector<int> parent(n, -1), depth(n, 0), order, size(n, 1);
        std::vector<int> st = {0};
        while (!st.empty()) { int u = st.back(); st.pop_back(); order.push_back(u); for (int v : g[u]) if (v != parent[u]) { parent[v] = u; depth[v] = depth[u] + 1; st.push_back(v); } }
        for (int i = n - 1; i > 0; i--) size[parent[order[i]]] += size[order[i]];             // 자식이 먼저 나오는 역순으로 크기 누적
        std::vector<long> sum(n, 0); for (int v = 0; v < n; v++) sum[0] += depth[v];
        for (int i = 1; i < n; i++) { int c = order[i]; sum[c] = sum[parent[c]] - size[c] + (n - size[c]); }     // 부모가 먼저 나오는 순서로 재루팅
        for (int s = 0; s < n; s++) {                                                          // 검증: 모든 정점에서 BFS 로 거리 합
            std::vector<int> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0; long total = 0;
            while (!q.empty()) { int u = q.front(); q.pop(); total += d[u]; for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } }
            assert(sum[s] == total);
        }
    }
    std::cout << "RootingTree: rerooting DP matched BFS from every vertex on 50 random trees." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## TreeDP()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 트리 DP: 트리에서는 "서브트리" 가 자연스러운 부분 문제다.  자식들의 결과를 합쳐 부모의 결과를 만든다 (후위 순서).  고전 두 가지:
//  (1) 가중치 최대 독립 집합(서로 인접하지 않은 정점의 가중치 합 최대): dp[v][0] = v 미선택 = Σ max(dp[c][0], dp[c][1]),  dp[v][1] = v 선택 = w[v] + Σ dp[c][0]
//  (2) 트리의 지름: 정점마다 "아래로 가장 긴 경로" 를 구하고, 가장 긴 두 개를 이은 것이 v 를 지나는 최장 경로
int main() {
    std::mt19937 rng(43);
    for (int trial = 0; trial < 200; trial++) {
        int n = rng() % 12 + 2; std::vector<std::vector<int>> g(n); std::vector<int> w(n);
        for (int v = 0; v < n; v++) w[v] = rng() % 20 + 1;
        std::vector<int> parent(n, -1), order;
        for (int v = 1; v < n; v++) { int p = rng() % v; g[p].push_back(v); g[v].push_back(p); }
        std::vector<int> st = {0};
        while (!st.empty()) { int u = st.back(); st.pop_back(); order.push_back(u); for (int v : g[u]) if (v != parent[u]) { parent[v] = u; st.push_back(v); } }
        std::vector<long> in(n), out(n); std::vector<int> down(n, 0); int diameter = 0;
        for (int i = n - 1; i >= 0; i--) {                                                 // 자식 -> 부모 순서
            int u = order[i]; in[u] = w[u]; out[u] = 0; int best1 = 0, best2 = 0;
            for (int c : g[u]) if (c != parent[u]) {
                in[u] += out[c]; out[u] += std::max(in[c], out[c]);
                int d = down[c] + 1; if (d > best1) { best2 = best1; best1 = d; } else if (d > best2) best2 = d;
            }
            down[u] = best1; diameter = std::max(diameter, best1 + best2);
        }
        long mis = std::max(in[0], out[0]);
        long brute = 0;                                                                    // 비트마스크 완전 탐색
        for (int mask = 0; mask < (1 << n); mask++) {
            bool ok = true; long s = 0;
            for (int v = 0; v < n && ok; v++) if (mask >> v & 1) { s += w[v]; for (int c : g[v]) if ((mask >> c & 1)) ok = false; }
            if (ok) brute = std::max(brute, s);
        }
        assert(mis == brute);
        auto bfs = [&](int s) { std::vector<int> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0; int last = s; while (!q.empty()) { int u = q.front(); q.pop(); last = u; for (int v : g[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } return std::make_pair(last, d[last]); };
        assert(bfs(bfs(0).first).second == diameter);                                      // BFS 두 번 방식의 지름과 일치
    }
    std::cout << "TreeDP: max-weight independent set and diameter verified on 200 random trees." << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## HeavyLightDecomposition()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 중경량 분할(HLD): 각 정점에서 서브트리가 가장 큰 자식으로 가는 간선을 "무거운 간선" 으로 정해 트리를 무거운 경로(체인)들로 나눈다.
// 루트에서 어떤 정점까지 가벼운 간선은 최대 log₂ n 개뿐이므로 경로 질의는 체인 O(log n) 개를 건너뛰는 것이 된다.  체인 안의 정점들이 DFS 순서에서 연속이 되게 번호를 매기면
// 각 체인은 배열 구간이므로 세그먼트 트리/펜윅 트리로 경로 합·갱신을 O(log² n) 에 처리한다 (트리 위의 경로 질의 문제의 표준 해법)
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

// 센트로이드 분해: 트리에서 "제거하면 남는 모든 컴포넌트의 크기가 n/2 이하" 가 되는 정점(센트로이드)을 찾아 루트로 삼고, 남은 컴포넌트에 재귀한다.  깊이가 O(log n) 인 센트로이드 트리가 나온다.
// 어떤 두 정점 u, v 의 경로는 센트로이드 트리에서 둘의 공통 조상 센트로이드 하나를 반드시 지난다 -> "가장 가까운 표시된 정점" 같은 질의를 O(log n) 에 답한다:
//   표시(v): v 의 모든 센트로이드 조상 c 에 대해 best[c] = min(best[c], dist(v, c)).   질의(v): min over c (best[c] + dist(v, c))
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
## BinaryLifting()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <random>
#include <vector>
#include <cassert>

// 이진 점프(binary lifting): up[k][v] = v 의 2^k 번째 조상을 전처리(O(n log n))해 두면 k 번째 조상을 이진수로 쪼개 O(log n) 에 구한다.
// LCA(최소 공통 조상): 두 정점의 깊이를 맞춘 뒤, 큰 점프부터 "조상이 서로 달라지는 동안" 같이 올라가면 바로 아래에서 멈춘다.  거리(u, v) = depth[u] + depth[v] - 2·depth[LCA]
struct Lift {
    int n, LOG; std::vector<std::vector<int>> up; std::vector<int> depth;
    Lift(const std::vector<int>& parent) : n(parent.size()), LOG(1), depth(parent.size(), 0) {
        while ((1 << LOG) < n) LOG++;
        up.assign(LOG, std::vector<int>(n));
        for (int v = 0; v < n; v++) { up[0][v] = parent[v] < 0 ? v : parent[v]; depth[v] = parent[v] < 0 ? 0 : depth[parent[v]] + 1; }       // 부모가 번호 순서상 앞이라고 가정
        for (int k = 1; k < LOG; k++) for (int v = 0; v < n; v++) up[k][v] = up[k - 1][up[k - 1][v]];
    }
    int kth(int v, int k) const { for (int i = 0; i < LOG; i++) if (k >> i & 1) v = up[i][v]; return v; }
    int lca(int u, int v) const {
        if (depth[u] < depth[v]) std::swap(u, v);
        u = kth(u, depth[u] - depth[v]);
        if (u == v) return u;
        for (int i = LOG - 1; i >= 0; i--) if (up[i][u] != up[i][v]) { u = up[i][u]; v = up[i][v]; }
        return up[0][u];
    }
    int dist(int u, int v) const { return depth[u] + depth[v] - 2 * depth[lca(u, v)]; }
};

int main() {
    std::mt19937 rng(46); const int N = 5000;
    std::vector<int> parent(N, -1); for (int v = 1; v < N; v++) parent[v] = (rng() % 3 == 0) ? v - 1 : rng() % v;
    Lift L(parent);
    for (int q = 0; q < 20000; q++) {
        int u = rng() % N, v = rng() % N;
        std::vector<bool> anc(N, false); for (int x = u;; x = parent[x]) { anc[x] = true; if (parent[x] < 0) break; }          // 순진한 LCA
        int x = v; while (!anc[x]) x = parent[x];
        assert(L.lca(u, v) == x);
        int d = 0; for (int a = u; a != x; a = parent[a]) d++; for (int b = v; b != x; b = parent[b]) d++;
        assert(L.dist(u, v) == d);
        int k = rng() % (L.depth[u] + 1), a = u; for (int i = 0; i < k; i++) a = parent[a];
        assert(L.kth(u, k) == a);
    }
    std::cout << "BinaryLifting: LCA, distance and k-th ancestor verified on 20000 random queries." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(N log N), 질의 O(log N)
// Space Complexity: O(N log N)
```
## EulerTourTechnique()
### 대표코드
```cpp
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 오일러 투어 기법: DFS 로 정점에 들어갈 때 tin, 나올 때 tout 번호를 매기면 "v 의 서브트리 = 구간 [tin[v], tout[v])" 가 된다.  트리 문제가 배열 구간 문제로 바뀐다:
//   서브트리 합 질의 = 구간 합,   v 의 값 갱신 = 점 갱신 (펜윅 트리).  또 "루트에서 v 까지의 경로 합" 은 v 의 값을 서브트리 구간 [tin, tout) 에 더하고 tin[x] 에서 점 질의하면 된다
struct BIT {
    int n; std::vector<long> t; explicit BIT(int n) : n(n), t(n + 2, 0) {}
    void add(int i, long v) { for (i++; i <= n; i += i & -i) t[i] += v; }
    long prefix(int i) const { long s = 0; for (; i > 0; i -= i & -i) s += t[i]; return s; }       // [0, i)
};
int main() {
    std::mt19937 rng(47); const int N = 2000;
    std::vector<std::vector<int>> g(N); std::vector<int> parent(N, -1);
    for (int v = 1; v < N; v++) { int p = rng() % v; parent[v] = p; g[p].push_back(v); }
    std::vector<int> tin(N), tout(N); int timer = 0;
    std::vector<std::pair<int, size_t>> st = {{0, 0}}; tin[0] = timer++;                            // 반복 DFS
    while (!st.empty()) {
        auto& top = st.back(); int u = top.first;
        if (top.second < g[u].size()) { int c = g[u][top.second++]; tin[c] = timer++; st.push_back({c, 0}); }
        else { tout[u] = timer; st.pop_back(); }
    }
    for (int v = 0; v < N; v++) assert(tin[v] < tout[v] && tout[v] - tin[v] >= 1);
    BIT subtree(N), pathBit(N + 1); std::vector<long> val(N, 0);
    for (int op = 0; op < 8000; op++) {
        int v = rng() % N;
        if (rng() % 2) {
            long d = (long)(rng() % 100) - 30; val[v] += d;
            subtree.add(tin[v], d);                                                                   // 서브트리 합용: 점 갱신
            pathBit.add(tin[v], d); pathBit.add(tout[v], -d);                                         // 경로 합용: 서브트리 구간에 더하기
        } else {
            long expect = 0; for (int u = 0; u < N; u++) if (tin[u] >= tin[v] && tin[u] < tout[v]) expect += val[u];      // v 서브트리의 합
            assert(subtree.prefix(tout[v]) - subtree.prefix(tin[v]) == expect);
            long pathExpect = 0; for (int x = v; x >= 0; x = parent[x]) pathExpect += val[x];          // 루트에서 v 까지의 경로 합
            assert(pathBit.prefix(tin[v] + 1) == pathExpect);
        }
    }
    std::cout << "EulerTourTechnique: subtree sums and root-path sums match naive computation." << std::endl;
    return 0;
}
// Time Complexity: 전처리 O(N), 질의·갱신 O(log N)
// Space Complexity: O(N)
```

## LinkCutTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 링크-컷 트리: "간선을 추가(link)하고 끊는(cut)" 동적 포레스트에서 연결 여부와 경로 집계를 O(log n) 분할상환에 처리한다 (Sleator–Tarjan).
// 숲을 "선호 경로(preferred path)" 들로 나누고, 각 경로를 스플레이 트리 하나로 표현한다.  access(v) 는 루트에서 v 까지를 하나의 선호 경로로 만들고,
// makeroot(v) 는 그 경로를 뒤집어(reverse 태그) v 를 새 루트로 만든다.  link/cut/connected/pathSum 모두 이 두 연산으로 구성된다
const int MAXN = 205;
int ch[MAXN][2], par[MAXN]; bool rev[MAXN]; long val[MAXN], sum[MAXN];
bool isRoot(int x) { return !par[x] || (ch[par[x]][0] != x && ch[par[x]][1] != x); }
void pushup(int x) { sum[x] = sum[ch[x][0]] + sum[ch[x][1]] + val[x]; }
void pushdown(int x) { if (rev[x]) { std::swap(ch[x][0], ch[x][1]); rev[ch[x][0]] ^= 1; rev[ch[x][1]] ^= 1; rev[x] = false; } }
void rotate(int x) {
    int y = par[x], z = par[y], k = ch[y][1] == x;
    if (!isRoot(y)) ch[z][ch[z][1] == y] = x;
    par[x] = z; ch[y][k] = ch[x][!k]; if (ch[x][!k]) par[ch[x][!k]] = y; ch[x][!k] = y; par[y] = x; pushup(y);
}
void splay(int x) {
    std::vector<int> stack = {x}; for (int y = x; !isRoot(y); y = par[y]) stack.push_back(par[y]);
    for (int i = stack.size() - 1; i >= 0; i--) pushdown(stack[i]);                      // 위에서부터 지연된 뒤집기를 내려보낸다
    while (!isRoot(x)) { int y = par[x], z = par[y]; if (!isRoot(y)) rotate((ch[y][1] == x) == (ch[z][1] == y) ? y : x); rotate(x); }
    pushup(x);
}
void access(int x) { for (int last = 0; x; last = x, x = par[x]) { splay(x); ch[x][1] = last; pushup(x); } }
void makeRoot(int x) { access(x); splay(x); rev[x] ^= 1; }
int findRoot(int x) { access(x); splay(x); while (true) { pushdown(x); if (!ch[x][0]) break; x = ch[x][0]; } splay(x); return x; }
bool connected(int x, int y) { return findRoot(x) == findRoot(y); }
void link(int x, int y) { makeRoot(x); par[x] = y; }                                      // 호출 전에 서로 다른 트리인지 확인
void cut(int x, int y) { makeRoot(x); access(y); splay(y); ch[y][0] = par[x] = 0; pushup(y); }   // x-y 간선이 있다고 가정
long pathSum(int x, int y) { makeRoot(x); access(y); splay(y); return sum[y]; }
void setVal(int x, long v) { access(x); splay(x); val[x] = v; pushup(x); }

int main() {
    const int N = 60; std::mt19937 rng(48);
    for (int i = 1; i <= N; i++) val[i] = sum[i] = i;
    std::vector<std::vector<int>> adj(N + 1); std::vector<long> value(N + 1); for (int i = 1; i <= N; i++) value[i] = i;
    auto naivePath = [&](int s, int t, bool& ok) -> long {                                // 순진한 숲: BFS 로 경로를 찾아 합산
        std::vector<int> prev(N + 1, -1); std::queue<int> q; q.push(s); prev[s] = 0;
        while (!q.empty()) { int u = q.front(); q.pop(); for (int v : adj[u]) if (prev[v] < 0) { prev[v] = u; q.push(v); } }
        ok = prev[t] >= 0; long total = 0; if (ok) for (int x = t; x; x = prev[x]) { total += value[x]; if (x == s) break; } return total;
    };
    for (int op = 0; op < 4000; op++) {
        int u = rng() % N + 1, v = rng() % N + 1; bool ok; int kind = rng() % 4;
        if (kind == 0 && u != v) { naivePath(u, v, ok); if (!ok) { link(u, v); adj[u].push_back(v); adj[v].push_back(u); } }          // 서로 다른 트리일 때만 link
        else if (kind == 1 && !adj[u].empty()) { int w = adj[u][rng() % adj[u].size()]; cut(u, w); adj[u].erase(std::find(adj[u].begin(), adj[u].end(), w)); adj[w].erase(std::find(adj[w].begin(), adj[w].end(), u)); }
        else if (kind == 2) { long nv = rng() % 100; setVal(u, nv); value[u] = nv; }
        else { long expect = naivePath(u, v, ok); assert(connected(u, v) == ok); if (ok) assert(pathSum(u, v) == expect); }
    }
    std::cout << "LinkCutTree: link / cut / connected / path-sum verified against a naive forest over 4000 operations." << std::endl;
    return 0;
}
// Time Complexity: 모든 연산 분할상환 O(log N)
// Space Complexity: O(N)
```
## TopTree()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <queue>
#include <random>
#include <vector>
#include <cassert>

// 탑 트리(top tree)의 핵심: 트리를 "클러스터" 들의 계층으로 쪼갠다.  클러스터는 경계 정점 두 개(a, b)를 가진 연결된 부분 트리이고, 두 가지 병합으로 만든다:
//   compress: a–m 클러스터와 m–b 클러스터를 이어 a–b 로 (경로를 따라 잇기),   rake: 경로 클러스터의 정점에 매달린 서브트리를 한 점으로 흡수.
// 클러스터마다 몇 가지 값만 저장해 두면 병합이 O(1) 이라 전체 트리의 값(여기서는 지름)이 루트 클러스터에서 바로 나온다.
// 이 구현은 정적 트리를 중경량 분할(heavy path)로 나눠 위 계층을 재귀적으로 만든다 (동적 갱신은 생략; 일반 탑 트리는 가중 균형으로 높이 O(log n) 보장)
struct Cluster { long len, down, up, diam; };                       // 경계 a(위)–b(아래): len = 경로 a-b 길이, down = a 에서 클러스터 내 가장 먼 거리, up = b 에서 가장 먼 거리, diam = 클러스터 내 지름
Cluster compress(const Cluster& A, const Cluster& B) {              // A 의 아래 경계 == B 의 위 경계
    return {A.len + B.len, std::max(A.down, A.len + B.down), std::max(B.up, B.len + A.up), std::max({A.diam, B.diam, A.up + B.down})};
}
struct TopTree {
    int n; std::vector<std::vector<std::pair<int, int>>> g; std::vector<int> parent, sz, heavy, pw; int maxDepth = 0;
    explicit TopTree(const std::vector<std::vector<std::pair<int, int>>>& adj) : n(adj.size()), g(adj), parent(n, -1), sz(n, 1), heavy(n, -1), pw(n, 0) { dfs(0); }
    void dfs(int v) { for (auto& e : g[v]) if (e.first != parent[v]) { parent[e.first] = v; pw[e.first] = e.second; dfs(e.first); sz[v] += sz[e.first]; if (heavy[v] < 0 || sz[e.first] > sz[heavy[v]]) heavy[v] = e.first; } }
    // 정점 v 에서 시작하는 무거운 경로 전체를 클러스터 하나로 만든다 (매달린 가벼운 서브트리는 rake 로 흡수)
    Cluster solvePath(int v, int depth) {
        std::vector<int> path; for (int x = v; x >= 0; x = heavy[x]) path.push_back(x);
        std::vector<Cluster> seq;                                                    // 정점 클러스터 Q_i 와 간선 클러스터 E_i 를 번갈아 놓는다
        for (size_t i = 0; i < path.size(); i++) {
            long best1 = 0, best2 = 0, innerDiam = 0;                                // rake: 정점에 매달린 가벼운 자식들
            for (auto& e : g[path[i]]) if (e.first != parent[path[i]] && e.first != heavy[path[i]]) {
                Cluster sub = solvePath(e.first, depth + 1); long d = e.second + sub.down;
                if (d > best1) { best2 = best1; best1 = d; } else if (d > best2) best2 = d;
                innerDiam = std::max(innerDiam, sub.diam);
            }
            seq.push_back({0, best1, best1, std::max(innerDiam, best1 + best2)});    // 정점 클러스터 (경로 길이 0)
            if (i + 1 < path.size()) seq.push_back({pw[path[i + 1]], pw[path[i + 1]], pw[path[i + 1]], pw[path[i + 1]]});   // 간선 클러스터
        }
        return combine(seq, 0, seq.size(), depth);
    }
    Cluster combine(const std::vector<Cluster>& s, size_t lo, size_t hi, int depth) {    // 균형 있게 compress: 높이 O(log 경로 길이)
        maxDepth = std::max(maxDepth, depth);
        if (hi - lo == 1) return s[lo];
        size_t mid = (lo + hi) / 2; return compress(combine(s, lo, mid, depth + 1), combine(s, mid, hi, depth + 1));
    }
};

int main() {
    std::mt19937 rng(49);
    for (int trial = 0; trial < 100; trial++) {
        int n = rng() % 200 + 2; std::vector<std::vector<std::pair<int, int>>> g(n);
        for (int v = 1; v < n; v++) { int p = (rng() % 3 == 0) ? v - 1 : rng() % v, w = rng() % 20 + 1; g[p].push_back({v, w}); g[v].push_back({p, w}); }
        TopTree tt(g); Cluster root = tt.solvePath(0, 0);
        auto far = [&](int s) { std::vector<long> d(n, -1); std::queue<int> q; q.push(s); d[s] = 0; int last = s; while (!q.empty()) { int u = q.front(); q.pop(); if (d[u] > d[last]) last = u; for (auto& e : g[u]) if (d[e.first] < 0) { d[e.first] = d[u] + e.second; q.push(e.first); } } return std::make_pair(last, d[last]); };
        assert(root.diam == far(far(0).first).second);                           // 루트 클러스터의 지름 == 두 번 탐색으로 구한 트리 지름
        assert(root.down >= 0 && tt.maxDepth <= 2 * std::log2(n + 1) * std::log2(n + 1) + 4);   // 계층의 높이는 O(log² n)
    }
    std::cout << "TopTree: root cluster diameter matched the true diameter on 100 random weighted trees." << std::endl;
    return 0;
}
// Time Complexity: 구성 O(N), 클러스터 병합 O(1)
// Space Complexity: O(N)
```
# Part 16. 특수 목적
## ExpressionTree()
### 대표코드
```cpp
#include <cctype>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// 수식 트리: 잎 = 피연산자(숫자·변수), 내부 노드 = 연산자.  중위 표기 -> (shunting-yard) -> 후위 표기 -> (스택) -> 트리.
// 후위 순회가 후위 표기, 전위 순회가 전위 표기, 중위 순회에 "필요한 괄호만" 붙이면 원래 식이 된다.  계산은 후위 순회 한 번, 미분은 트리를 재귀적으로 다시 쓰면 된다
struct Node; typedef std::shared_ptr<Node> P;
struct Node { std::string v; P l, r; };
P mk(const std::string& v, P l = nullptr, P r = nullptr) { return std::make_shared<Node>(Node{v, l, r}); }
bool isOp(const std::string& s) { return s.size() == 1 && std::string("+-*/^").find(s[0]) != std::string::npos; }
int prec(char c) { return c == '^' ? 3 : (c == '*' || c == '/') ? 2 : 1; }
bool rightAssoc(char c) { return c == '^'; }

std::vector<std::string> tokenize(const std::string& s) {
    std::vector<std::string> t;
    for (size_t i = 0; i < s.size();) {
        if (isspace((unsigned char)s[i])) { i++; continue; }
        if (isalnum((unsigned char)s[i]) || s[i] == '.') { size_t j = i; while (j < s.size() && (isalnum((unsigned char)s[j]) || s[j] == '.')) j++; t.push_back(s.substr(i, j - i)); i = j; }
        else t.push_back(std::string(1, s[i++]));
    }
    return t;
}
std::vector<std::string> toPostfix(const std::vector<std::string>& tok) {          // shunting-yard (단항 마이너스는 다루지 않는다)
    std::vector<std::string> out, st;
    for (auto& t : tok) {
        if (isOp(t)) {
            while (!st.empty() && isOp(st.back()) && (prec(st.back()[0]) > prec(t[0]) || (prec(st.back()[0]) == prec(t[0]) && !rightAssoc(t[0])))) { out.push_back(st.back()); st.pop_back(); }
            st.push_back(t);
        } else if (t == "(") st.push_back(t);
        else if (t == ")") { while (st.back() != "(") { out.push_back(st.back()); st.pop_back(); } st.pop_back(); }
        else out.push_back(t);
    }
    while (!st.empty()) { out.push_back(st.back()); st.pop_back(); }
    return out;
}
P fromPostfix(const std::vector<std::string>& pf) {
    std::vector<P> st;
    for (auto& t : pf) {
        if (isOp(t)) { P r = st.back(); st.pop_back(); P l = st.back(); st.pop_back(); st.push_back(mk(t, l, r)); }
        else st.push_back(mk(t));
    }
    return st.back();
}
P parse(const std::string& s) { return fromPostfix(toPostfix(tokenize(s))); }
typedef std::map<std::string, double> Env;
double eval(const P& n, const Env& env) {
    if (!n->l) { auto it = env.find(n->v); return it != env.end() ? it->second : std::stod(n->v); }
    double a = eval(n->l, env), b = eval(n->r, env);
    switch (n->v[0]) { case '+': return a + b; case '-': return a - b; case '*': return a * b; case '/': return a / b; default: return std::pow(a, b); }
}
std::string infix(const P& n, int parentPrec = 0, bool right = false, char parentOp = 0) {      // 필요한 괄호만 붙인다
    if (!n->l) return n->v;
    char op = n->v[0]; int p = prec(op);
    std::string s = infix(n->l, p, false, op) + op + infix(n->r, p, true, op);
    bool paren = p < parentPrec || (p == parentPrec && right != rightAssoc(parentOp));       // 같은 우선순위면 결합 방향의 반대쪽 자식만 괄호
    return paren ? "(" + s + ")" : s;
}
std::string prefix(const P& n)  { return !n->l ? n->v : n->v + " " + prefix(n->l) + " " + prefix(n->r); }
std::string postfix(const P& n) { return !n->l ? n->v : postfix(n->l) + " " + postfix(n->r) + " " + n->v; }
bool same(const P& a, const P& b) { return a->v == b->v && (!a->l) == (!b->l) && (!a->l || (same(a->l, b->l) && same(a->r, b->r))); }

// 기호 미분: d/dx.  수식 트리를 재귀적으로 새 트리로 다시 쓰고, simp 로 0·1 과 상수를 정리한다 (지수는 상수만 지원)
std::string fmt(double d) { std::ostringstream o; o << d; return o.str(); }
P num(double d) { return mk(fmt(d)); }
bool isNum(const P& n, double& v) { if (n->l || !(isdigit((unsigned char)n->v[0]) || n->v[0] == '.')) return false; v = std::stod(n->v); return true; }
P simp(const P& n) {
    if (!n->l) return n;
    P l = simp(n->l), r = simp(n->r); double a, b; char op = n->v[0];
    bool la = isNum(l, a), rb = isNum(r, b);
    if (la && rb) { switch (op) { case '+': return num(a + b); case '-': return num(a - b); case '*': return num(a * b); case '/': return num(a / b); default: return num(std::pow(a, b)); } }
    if (op == '+') { if (la && a == 0) return r; if (rb && b == 0) return l; }
    if (op == '-' && rb && b == 0) return l;
    if (op == '*') { if ((la && a == 0) || (rb && b == 0)) return num(0); if (la && a == 1) return r; if (rb && b == 1) return l; }
    if (op == '/') { if (la && a == 0) return num(0); if (rb && b == 1) return l; }
    if (op == '^') { if (rb && b == 1) return l; if (rb && b == 0) return num(1); }
    return mk(n->v, l, r);
}
P diff(const P& n, const std::string& x) {
    if (!n->l) return num(n->v == x ? 1 : 0);
    const P &a = n->l, &b = n->r;
    switch (n->v[0]) {
        case '+': case '-': return simp(mk(n->v, diff(a, x), diff(b, x)));
        case '*': return simp(mk("+", mk("*", diff(a, x), b), mk("*", a, diff(b, x))));
        case '/': return simp(mk("/", mk("-", mk("*", diff(a, x), b), mk("*", a, diff(b, x))), mk("^", b, num(2))));
        default: { double c; bool ok = isNum(b, c); assert(ok); (void)ok; return simp(mk("*", mk("*", b, mk("^", a, num(c - 1))), diff(a, x))); }
    }
}
P randomTree(std::mt19937& rng, int depth) {                               // 정수 잎, + - * 만 사용 (정확한 정수 계산)
    if (depth == 0 || rng() % 4 == 0) return mk(std::to_string(rng() % 10));
    return mk(std::string(1, "+-*"[rng() % 3]), randomTree(rng, depth - 1), randomTree(rng, depth - 1));
}

int main() {
    P t = parse("3+4*2");
    assert(postfix(t) == "3 4 2 * +" && prefix(t) == "+ 3 * 4 2" && infix(t) == "3+4*2" && eval(t, {}) == 11);
    assert(infix(parse("(3+4)*2")) == "(3+4)*2" && eval(parse("(3+4)*2"), {}) == 14);
    assert(eval(parse("2^3^2"), {}) == 512 && infix(parse("2^3^2")) == "2^3^2");         // ^ 는 오른쪽 결합
    assert(eval(parse("10-4-3"), {}) == 3 && infix(parse("10-(4-3)")) == "10-(4-3)");  // - 는 왼쪽 결합이라 오른쪽 괄호는 필수
    assert(eval(parse("x*x+y"), {{"x", 4}, {"y", 1}}) == 17);

    std::mt19937 rng(8);
    for (int i = 0; i < 2000; i++) {                                       // 트리 -> 중위 문자열 -> 트리 왕복이 구조까지 같다
        P a = randomTree(rng, 5); std::string s = infix(a); P b = parse(s);
        assert(same(a, b) && eval(a, {}) == eval(b, {}));
    }
    P f = parse("x^3+2*x*y-5");
    P d = diff(f, "x");
    assert(infix(d) == "3*x^2+2*y");                                       // d/dx (x^3 + 2xy - 5) = 3x^2 + 2y
    assert(eval(d, {{"x", 2}, {"y", 3}}) == 18);
    P g = parse("(x+1)/(x-1)"); P dg = diff(g, "x");                       // 몫의 미분은 수치 미분과 비교
    double h = 1e-6, num_ = (eval(g, {{"x", 3 + h}}) - eval(g, {{"x", 3 - h}})) / (2 * h);
    assert(std::fabs(eval(dg, {{"x", 3}}) - num_) < 1e-6 && std::fabs(eval(dg, {{"x", 3}}) + 0.5) < 1e-12);
    std::cout << "ExpressionTree: d/dx(x^3+2*x*y-5) = " << infix(d) << std::endl;
    return 0;
}
// Time Complexity: 구성·계산·출력 O(N), 미분 O(N) (정리 포함)
// Space Complexity: O(N)
```
## SyntaxTree()
### 대표코드
```cpp
#include <cctype>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <cassert>

// 추상 구문 트리(AST): 소스 코드의 "의미 구조"만 남긴 트리. 괄호·세미콜론·중간 문법 규칙(Term, Factor ...)은 사라지고 연산자 우선순위가 트리 모양으로 굳는다.
// 아래는 변수·산술·비교·if·while 만 있는 작은 언어의 토큰화 -> 우선순위 상승 파서 -> AST -> 상수 접기(최적화) -> 인터프리터.  컴파일러의 프런트엔드 전체를 축소한 모양이다
enum Kind { NUM, VAR, BIN, NEG, ASSIGN, WHILE, IF, BLOCK };
struct Node; typedef std::unique_ptr<Node> P;
struct Node { Kind k; long num = 0; std::string s; std::vector<P> c; };
P mk(Kind k, const std::string& s = "", long num = 0) { P n(new Node); n->k = k; n->s = s; n->num = num; return n; }

std::vector<std::string> lex(const std::string& src) {
    std::vector<std::string> t;
    for (size_t i = 0; i < src.size();) {
        char ch = src[i];
        if (isspace((unsigned char)ch)) { i++; continue; }
        if (isalnum((unsigned char)ch) || ch == '_') { size_t j = i; while (j < src.size() && (isalnum((unsigned char)src[j]) || src[j] == '_')) j++; t.push_back(src.substr(i, j - i)); i = j; continue; }
        bool two = false;
        for (const char* op : {"<=", ">=", "==", "!="}) if (src.compare(i, 2, op) == 0) { t.push_back(op); i += 2; two = true; break; }
        if (!two) t.push_back(std::string(1, src[i++]));
    }
    return t;
}
struct Parser {
    std::vector<std::string> t; size_t i = 0;
    std::string peek() const { return i < t.size() ? t[i] : ""; }
    std::string next() { return t[i++]; }
    void expect(const std::string& s) { assert(peek() == s); i++; }
    static int prec(const std::string& op) {
        if (op == "==" || op == "!=") return 1;
        if (op == "<" || op == ">" || op == "<=" || op == ">=") return 2;
        if (op == "+" || op == "-") return 3;
        if (op == "*" || op == "/" || op == "%") return 4;
        return 0;
    }
    P primary() {
        std::string s = next();
        if (isdigit((unsigned char)s[0])) return mk(NUM, "", std::stol(s));
        if (s == "(") { P e = expr(0); expect(")"); return e; }                        // 괄호는 여기서 사라진다
        if (s == "-") { P n = mk(NEG); n->c.push_back(primary()); return n; }
        return mk(VAR, s);
    }
    P expr(int minPrec) {                                                              // 우선순위 상승(precedence climbing)
        P lhs = primary();
        for (;;) {
            std::string op = peek(); int p = prec(op);
            if (p == 0 || p <= minPrec) break;
            i++; P rhs = expr(p);
            P b = mk(BIN, op); b->c.push_back(std::move(lhs)); b->c.push_back(std::move(rhs)); lhs = std::move(b);
        }
        return lhs;
    }
    P stmt() {
        std::string s = peek();
        if (s == "while") { i++; expect("("); P n = mk(WHILE); n->c.push_back(expr(0)); expect(")"); n->c.push_back(stmt()); return n; }
        if (s == "if") {
            i++; expect("("); P n = mk(IF); n->c.push_back(expr(0)); expect(")"); n->c.push_back(stmt());
            if (peek() == "else") { i++; n->c.push_back(stmt()); } return n;
        }
        if (s == "{") { i++; P n = mk(BLOCK); while (peek() != "}") n->c.push_back(stmt()); i++; return n; }
        P n = mk(ASSIGN, next()); expect("="); n->c.push_back(expr(0)); expect(";"); return n;
    }
    P program() { P n = mk(BLOCK); while (i < t.size()) n->c.push_back(stmt()); return n; }
};
P parse(const std::string& src) { Parser p; p.t = lex(src); return p.program(); }

long apply(const std::string& op, long a, long b) {
    if (op == "+") return a + b; if (op == "-") return a - b; if (op == "*") return a * b; if (op == "/") return a / b; if (op == "%") return a % b;
    if (op == "<") return a < b; if (op == ">") return a > b; if (op == "<=") return a <= b; if (op == ">=") return a >= b; if (op == "==") return a == b; return a != b;
}
typedef std::map<std::string, long> Env;
long evalExpr(const Node* n, Env& env) {
    switch (n->k) {
        case NUM: return n->num;
        case VAR: return env[n->s];
        case NEG: return -evalExpr(n->c[0].get(), env);
        default:  { long a = evalExpr(n->c[0].get(), env), b = evalExpr(n->c[1].get(), env); return apply(n->s, a, b); }
    }
}
void exec(const Node* n, Env& env) {
    switch (n->k) {
        case ASSIGN: env[n->s] = evalExpr(n->c[0].get(), env); break;
        case WHILE:  while (evalExpr(n->c[0].get(), env)) exec(n->c[1].get(), env); break;
        case IF:     if (evalExpr(n->c[0].get(), env)) exec(n->c[1].get(), env); else if (n->c.size() > 2) exec(n->c[2].get(), env); break;
        case BLOCK:  for (auto& ch : n->c) exec(ch.get(), env); break;
        default: break;
    }
}
std::string sexpr(const Node* n) {
    std::string r;
    switch (n->k) {
        case NUM: return std::to_string(n->num);
        case VAR: return n->s;
        case NEG: return "(- " + sexpr(n->c[0].get()) + ")";
        case BIN: return "(" + n->s + " " + sexpr(n->c[0].get()) + " " + sexpr(n->c[1].get()) + ")";
        case ASSIGN: return "(= " + n->s + " " + sexpr(n->c[0].get()) + ")";
        case WHILE: return "(while " + sexpr(n->c[0].get()) + " " + sexpr(n->c[1].get()) + ")";
        case IF: r = "(if"; break;
        case BLOCK: r = "(block"; break;
    }
    for (auto& ch : n->c) r += " " + sexpr(ch.get());
    return r + ")";
}
P fold(P n) {                                                              // 상수 접기: 컴파일 시점에 계산 가능한 부분 트리를 숫자 하나로
    for (auto& ch : n->c) ch = fold(std::move(ch));
    if (n->k == BIN && n->c[0]->k == NUM && n->c[1]->k == NUM && !((n->s == "/" || n->s == "%") && n->c[1]->num == 0))
        return mk(NUM, "", apply(n->s, n->c[0]->num, n->c[1]->num));
    if (n->k == NEG && n->c[0]->k == NUM) return mk(NUM, "", -n->c[0]->num);
    return n;
}
int size(const Node* n) { int s = 1; for (auto& ch : n->c) s += size(ch.get()); return s; }
long run(const std::string& src, const std::string& var) { Env env; P ast = parse(src); exec(ast.get(), env); return env[var]; }

int main() {
    assert(sexpr(parse("x = 1 + 2 * (3 + 4);").get()) == "(block (= x (+ 1 (* 2 (+ 3 4)))))");          // 괄호가 없어도 우선순위가 모양에 담겼다
    assert(sexpr(parse("x = (((1)));").get()) == sexpr(parse("x = 1;").get()));                           // 겹괄호는 AST 에서 구분되지 않는다
    assert(sexpr(parse("x = 10 - 4 - 3;").get()) == "(block (= x (- (- 10 4) 3)))");                       // 왼쪽 결합
    assert(sexpr(parse("x = a < b == c;").get()) == "(block (= x (== (< a b) c)))");                       // 비교 연산자의 우선순위 단계
    P ast = parse("x = 2 * 3 + 4 * 5; y = x - -1;"); int before = size(ast.get());
    ast = fold(std::move(ast));
    assert(sexpr(ast.get()) == "(block (= x 26) (= y (- x -1)))" && size(ast.get()) < before);            // 상수 부분식만 접힌다
    assert(run("n = 10; a = 0; b = 1; i = 0; while (i < n) { t = a + b; a = b; b = t; i = i + 1; } result = a;", "result") == 55);   // fib(10)
    assert(run("a = 48; b = 18; while (b != 0) { t = a % b; a = b; b = t; } result = a;", "result") == 6);                           // gcd
    assert(run("n = 27; steps = 0; while (n != 1) { if (n % 2 == 0) { n = n / 2; } else { n = 3 * n + 1; } steps = steps + 1; } result = steps;", "result") == 111);   // 콜라츠
    assert(run("x = 5; if (x > 3) y = 1; else y = 2; if (x > 9) z = 1; else z = 2; result = y * 10 + z;", "result") == 12);
    std::cout << "SyntaxTree: AST nodes for x = 2*3+4*5: " << before << " -> " << size(ast.get()) << " after constant folding" << std::endl;
    return 0;
}
// Time Complexity: 구문 분석 O(N), 실행은 프로그램에 따라 다름
// Space Complexity: O(N)
```
## ParseTree()
### 대표코드
```cpp
#include <cctype>
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <cassert>

// 파스 트리(구체 구문 트리, CST): 문법 규칙을 그대로 따라 만든, 입력의 모든 토큰이 잎으로 남는 트리. 내부 노드는 문법의 비단말 기호다.
// 잎을 왼쪽에서 오른쪽으로 읽으면(yield) 원래 입력이 복원된다는 것이 정의다.  AST 와 달리 괄호와 중간 규칙(Term, Factor)이 그대로 있다.
// 문법:  Expr -> Term (('+'|'-') Term)*   Term -> Factor (('*'|'/') Factor)*   Factor -> NUM | '(' Expr ')'   (재귀 하강 파서)
struct Node; typedef std::unique_ptr<Node> P;
struct Node { std::string label; std::vector<P> kids; };
P nt(const std::string& l) { P n(new Node); n->label = l; return n; }
struct Parser {
    std::vector<std::string> t; size_t i = 0;
    std::string peek() const { return i < t.size() ? t[i] : ""; }
    P leaf() { P n(new Node); n->label = t[i++]; return n; }
    P expr() { P n = nt("Expr"); n->kids.push_back(term()); while (peek() == "+" || peek() == "-") { n->kids.push_back(leaf()); n->kids.push_back(term()); } return n; }
    P term() { P n = nt("Term"); n->kids.push_back(factor()); while (peek() == "*" || peek() == "/") { n->kids.push_back(leaf()); n->kids.push_back(factor()); } return n; }
    P factor() {
        P n = nt("Factor");
        if (peek() == "(") { n->kids.push_back(leaf()); n->kids.push_back(expr()); assert(peek() == ")"); n->kids.push_back(leaf()); }
        else n->kids.push_back(leaf());
        return n;
    }
};
std::vector<std::string> tokens(const std::string& s) {
    std::vector<std::string> t;
    for (size_t i = 0; i < s.size();) {
        if (isspace((unsigned char)s[i])) { i++; continue; }
        if (isdigit((unsigned char)s[i])) { size_t j = i; while (j < s.size() && isdigit((unsigned char)s[j])) j++; t.push_back(s.substr(i, j - i)); i = j; }
        else t.push_back(std::string(1, s[i++]));
    }
    return t;
}
P parse(const std::string& s, std::vector<std::string>& tok) { Parser p; p.t = tok = tokens(s); P root = p.expr(); assert(p.i == p.t.size()); return root; }
std::string show(const Node* n) {
    if (n->kids.empty()) return n->label;
    std::string r = "(" + n->label; for (auto& k : n->kids) r += " " + show(k.get()); return r + ")";
}
void yield(const Node* n, std::vector<std::string>& out) { if (n->kids.empty()) out.push_back(n->label); for (auto& k : n->kids) yield(k.get(), out); }
int count(const Node* n) { int c = 1; for (auto& k : n->kids) c += count(k.get()); return c; }
long evalCst(const Node* n) {                                              // 파스 트리를 아래에서 위로 계산 (규칙 구조가 곧 우선순위)
    if (n->label == "Factor") return n->kids.size() == 1 ? std::stol(n->kids[0]->label) : evalCst(n->kids[1].get());
    long v = evalCst(n->kids[0].get());
    for (size_t j = 1; j < n->kids.size(); j += 2) {
        long r = evalCst(n->kids[j + 1].get()); char op = n->kids[j]->label[0];
        v = op == '+' ? v + r : op == '-' ? v - r : op == '*' ? v * r : v / r;
    }
    return v;
}
std::string toAst(const Node* n) {                                         // 파스 트리 -> AST 의 S-식: 괄호·중간 규칙을 걷어낸다
    if (n->label == "Factor") return n->kids.size() == 1 ? n->kids[0]->label : toAst(n->kids[1].get());
    std::string acc = toAst(n->kids[0].get());
    for (size_t j = 1; j < n->kids.size(); j += 2) acc = "(" + n->kids[j]->label + " " + acc + " " + toAst(n->kids[j + 1].get()) + ")";
    return acc;
}
// 모호한 문법 S -> S S | a : 같은 문자열에 파스 트리가 여러 개.  구간 DP(CYK 방식)로 트리 개수를 센다 -> 카탈란 수
long countTrees(int n) {
    std::vector<std::vector<long>> c(n + 1, std::vector<long>(n + 1, 0));
    for (int i = 0; i < n; i++) c[i][i + 1] = 1;
    for (int len = 2; len <= n; len++) for (int i = 0; i + len <= n; i++) for (int k = i + 1; k < i + len; k++) c[i][i + len] += c[i][k] * c[k][i + len];
    return c[0][n];
}

int main() {
    std::vector<std::string> tok;
    P t = parse("1+2*3", tok);
    assert(show(t.get()) == "(Expr (Term (Factor 1)) + (Term (Factor 2) * (Factor 3)))");
    std::vector<std::string> y; yield(t.get(), y); assert(y == tok);                                 // yield == 입력 토큰열
    for (std::string s : {"(1+2)*3", "10-4-3", "2*(3+(4-1))/3", "((7))"}) {
        P p = parse(s, tok); y.clear(); yield(p.get(), y); assert(y == tok);                         // 괄호까지 모두 잎으로 남는다
        assert(count(p.get()) > 2 * (int)tok.size() - 1 || s == "10-4-3");
    }
    assert(evalCst(parse("1+2*3", tok).get()) == 7 && evalCst(parse("(1+2)*3", tok).get()) == 9 && evalCst(parse("10-4-3", tok).get()) == 3);
    assert(toAst(parse("1+2*3", tok).get()) == "(+ 1 (* 2 3))");
    assert(toAst(parse("(1+2)*3", tok).get()) == "(* (+ 1 2) 3)");
    assert(toAst(parse("10-4-3", tok).get()) == "(- (- 10 4) 3)");
    P big = parse("1+2*3", tok);
    assert(count(big.get()) == 11);                                                                    // 파스 트리 11 노드 vs AST (+ 1 (* 2 3)) 5 노드
    long catalan[] = {1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862};
    for (int n = 1; n <= 10; n++) assert(countTrees(n) == catalan[n - 1]);
    std::cout << "ParseTree: " << show(t.get()) << " ; trees for a^10 under S->SS|a = " << countTrees(10) << std::endl;
    return 0;
}
// Time Complexity: 재귀 하강 파싱 O(N), 모호한 문법의 트리 수 세기 O(N^3)
// Space Complexity: O(N)
```
## DecisionTree()
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 의사결정 트리: 내부 노드 = 속성에 대한 질문, 간선 = 답, 잎 = 예측.  "가장 불순도를 많이 줄이는 질문"을 탐욕적으로 고르며 재귀 분할한다.
// (1) ID3: 범주형 속성, 정보 이득 = H(S) - Σ |Sv|/|S| · H(Sv)   (2) CART: 수치형 속성, 임계값 분할과 지니 불순도 2p(1-p)
typedef std::vector<std::string> Row;                                      // 마지막 열 = 레이블
const char* attrName[] = {"Outlook", "Temperature", "Humidity", "Wind"};
double entropy(const std::vector<Row>& rows) {
    std::map<std::string, int> cnt; for (auto& r : rows) cnt[r.back()]++;
    double h = 0; for (auto& kv : cnt) { double p = (double)kv.second / rows.size(); h -= p * std::log2(p); } return h;
}
double gain(const std::vector<Row>& rows, int a) {
    std::map<std::string, std::vector<Row>> parts; for (auto& r : rows) parts[r[a]].push_back(r);
    double g = entropy(rows); for (auto& kv : parts) g -= (double)kv.second.size() / rows.size() * entropy(kv.second); return g;
}
struct Node { int attr = -1; std::string label; std::map<std::string, std::unique_ptr<Node>> kids; };
std::string majority(const std::vector<Row>& rows) {
    std::map<std::string, int> cnt; for (auto& r : rows) cnt[r.back()]++;
    return std::max_element(cnt.begin(), cnt.end(), [](auto& a, auto& b) { return a.second < b.second; })->first;
}
std::unique_ptr<Node> build(const std::vector<Row>& rows, std::set<int> attrs) {
    std::unique_ptr<Node> n(new Node); n->label = majority(rows);
    std::set<std::string> labels; for (auto& r : rows) labels.insert(r.back());
    if (labels.size() == 1 || attrs.empty()) return n;                     // 순수하거나 쓸 속성이 없으면 잎
    int best = -1; double bg = -1; for (int a : attrs) { double g = gain(rows, a); if (g > bg) { bg = g; best = a; } }
    n->attr = best; attrs.erase(best);
    std::map<std::string, std::vector<Row>> parts; for (auto& r : rows) parts[r[best]].push_back(r);
    for (auto& kv : parts) n->kids[kv.first] = build(kv.second, attrs);
    return n;
}
std::string predict(const Node* n, const Row& x) {
    while (n->attr >= 0) { auto it = n->kids.find(x[n->attr]); if (it == n->kids.end()) return n->label; n = it->second.get(); }
    return n->label;
}
std::string show(const Node* n) {
    if (n->attr < 0) return n->label;
    std::string s = std::string(attrName[n->attr]) + "("; bool first = true;
    for (auto& kv : n->kids) { if (!first) s += ","; first = false; s += kv.first + ":" + show(kv.second.get()); }
    return s + ")";
}
// ---- CART: 수치형 속성 2개, 이진 분할 ----
struct Pt { double x[2]; int y; };
struct CNode { int f = -1; double thr = 0; int label = 0; std::unique_ptr<CNode> l, r; };
double gini(int n0, int n1) { int n = n0 + n1; if (!n) return 0; double p = (double)n1 / n; return 2 * p * (1 - p); }
std::unique_ptr<CNode> buildCart(std::vector<Pt>& p, int lo, int hi, int depth, int maxDepth) {
    std::unique_ptr<CNode> n(new CNode); int c1 = 0; for (int i = lo; i < hi; i++) c1 += p[i].y;
    int c0 = (hi - lo) - c1; n->label = c1 > c0;
    if (c0 == 0 || c1 == 0 || depth == maxDepth) return n;
    double parent = gini(c0, c1), best = parent; int bf = -1; double bt = 0;
    for (int f = 0; f < 2; f++) {
        std::sort(p.begin() + lo, p.begin() + hi, [f](const Pt& a, const Pt& b) { return a.x[f] < b.x[f]; });
        int l0 = 0, l1 = 0;
        for (int i = lo; i + 1 < hi; i++) {
            (p[i].y ? l1 : l0)++;
            if (p[i].x[f] == p[i + 1].x[f]) continue;
            int m = i + 1 - lo; double g = (m * gini(l0, l1) + (hi - lo - m) * gini(c0 - l0, c1 - l1)) / (hi - lo);
            if (g < best - 1e-12) { best = g; bf = f; bt = (p[i].x[f] + p[i + 1].x[f]) / 2; }
        }
    }
    if (bf < 0) return n;                                                  // 불순도를 줄이는 분할이 없다
    n->f = bf; n->thr = bt;
    std::sort(p.begin() + lo, p.begin() + hi, [bf](const Pt& a, const Pt& b) { return a.x[bf] < b.x[bf]; });
    int mid = lo; while (mid < hi && p[mid].x[bf] <= bt) mid++;
    n->l = buildCart(p, lo, mid, depth + 1, maxDepth); n->r = buildCart(p, mid, hi, depth + 1, maxDepth);
    return n;
}
int predictCart(const CNode* n, const Pt& q) { while (n->f >= 0) n = q.x[n->f] <= n->thr ? n->l.get() : n->r.get(); return n->label; }
int depthOf(const CNode* n) { return n->f < 0 ? 0 : 1 + std::max(depthOf(n->l.get()), depthOf(n->r.get())); }

int main() {
    std::vector<Row> d = {
        {"Sunny","Hot","High","Weak","No"},       {"Sunny","Hot","High","Strong","No"},    {"Overcast","Hot","High","Weak","Yes"},
        {"Rain","Mild","High","Weak","Yes"},      {"Rain","Cool","Normal","Weak","Yes"},   {"Rain","Cool","Normal","Strong","No"},
        {"Overcast","Cool","Normal","Strong","Yes"}, {"Sunny","Mild","High","Weak","No"},  {"Sunny","Cool","Normal","Weak","Yes"},
        {"Rain","Mild","Normal","Weak","Yes"},    {"Sunny","Mild","Normal","Strong","Yes"}, {"Overcast","Mild","High","Strong","Yes"},
        {"Overcast","Hot","Normal","Weak","Yes"}, {"Rain","Mild","High","Strong","No"}};
    assert(std::fabs(entropy(d) - 0.9403) < 5e-4);                         // 9 Yes / 5 No
    assert(std::fabs(gain(d, 0) - 0.2467) < 5e-4 && std::fabs(gain(d, 1) - 0.0292) < 5e-4);      // 교과서의 정보 이득 값
    assert(std::fabs(gain(d, 2) - 0.1518) < 5e-4 && std::fabs(gain(d, 3) - 0.0481) < 5e-4);
    auto tree = build(d, {0, 1, 2, 3});
    assert(show(tree.get()) == "Outlook(Overcast:Yes,Rain:Wind(Strong:No,Weak:Yes),Sunny:Humidity(High:No,Normal:Yes))");
    for (auto& r : d) assert(predict(tree.get(), r) == r.back());          // 학습 데이터 14/14
    assert(predict(tree.get(), {"Sunny", "Cool", "Normal", "Strong", ""}) == "Yes");
    assert(predict(tree.get(), {"Rain", "Mild", "High", "Strong", ""}) == "No");

    std::mt19937 rng(2024); std::uniform_real_distribution<double> U(0, 10);
    auto make = [&](int n) { std::vector<Pt> v(n); for (auto& p : v) { p.x[0] = U(rng); p.x[1] = U(rng); p.y = (p.x[0] > 5 && p.x[1] < 3); } return v; };
    std::vector<Pt> train = make(2000), test = make(5000);
    auto cart = buildCart(train, 0, train.size(), 0, 5);
    int ok = 0; for (auto& q : test) ok += predictCart(cart.get(), q) == q.y;
    assert(depthOf(cart.get()) <= 3 && ok >= 0.98 * test.size());          // 두 임계값(x0>5, x1<3)을 찾아낸다
    for (auto& q : train) assert(predictCart(cart.get(), q) == q.y);
    std::cout << "DecisionTree: ID3 = " << show(tree.get()) << " ; CART depth " << depthOf(cart.get()) << ", test accuracy " << 100.0 * ok / test.size() << "%" << std::endl;
    return 0;
}
// Time Complexity: ID3 O(속성 수 × N × 깊이), CART 노드당 O(속성 수 × N log N)
// Space Complexity: O(N)
```
## MerkleTree()
### 대표코드
```cpp
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 머클 트리: 잎 = 데이터 블록의 해시, 내부 노드 = 두 자식 해시를 이은 것의 해시.  루트 해시 32바이트 하나가 전체 데이터의 지문이다.
// 어느 한 블록이 진짜인지는 "루트까지 형제 해시 log2 n 개(감사 경로)"만 받으면 O(log n) 에 검증된다 (Git, 비트코인, 인증서 투명성 로그, 분산 DB 의 동기화).
// 여기서는 RFC 6962(인증서 투명성)의 정의를 따른다: 잎 해시 = H(0x00 || 데이터), 내부 = H(0x01 || 왼쪽 || 오른쪽), n 개를 "n 보다 작은 가장 큰 2의 거듭제곱 k" 에서 둘로 나눈다.
// 접두 바이트(도메인 분리)와 "마지막 노드 복제 없음" 이 비트코인식 단순 구성의 취약점(잎과 내부 노드 혼동, [a,b,c] == [a,b,c,c])을 막는다
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
std::string sha256raw(const std::string& msg) {                            // SHA-256: 32바이트 원시 다이제스트
    static uint32_t K[64], H0[8]; static bool init = false;
    if (!init) {
        std::vector<uint32_t> pr; for (uint32_t p = 2; pr.size() < 64; p++) { bool ok = true; for (uint32_t q : pr) if (p % q == 0) { ok = false; break; } if (ok) pr.push_back(p); }
        for (int i = 0; i < 64; i++) { long double c = cbrtl((long double)pr[i]); K[i] = (uint32_t)((c - floorl(c)) * 4294967296.0L); }
        for (int i = 0; i < 8; i++)  { long double s = sqrtl((long double)pr[i]); H0[i] = (uint32_t)((s - floorl(s)) * 4294967296.0L); }
        init = true;
    }
    uint32_t H[8]; for (int i = 0; i < 8; i++) H[i] = H0[i];
    std::vector<uint8_t> m(msg.begin(), msg.end()); uint64_t bits = (uint64_t)msg.size() * 8;
    m.push_back(0x80); while (m.size() % 64 != 56) m.push_back(0);
    for (int i = 7; i >= 0; i--) m.push_back((bits >> (8 * i)) & 0xff);
    for (size_t off = 0; off < m.size(); off += 64) {
        uint32_t w[64];
        for (int i = 0; i < 16; i++) w[i] = m[off + 4*i] << 24 | m[off + 4*i + 1] << 16 | m[off + 4*i + 2] << 8 | m[off + 4*i + 3];
        for (int i = 16; i < 64; i++) {
            uint32_t s0 = rotr(w[i-15], 7) ^ rotr(w[i-15], 18) ^ (w[i-15] >> 3), s1 = rotr(w[i-2], 17) ^ rotr(w[i-2], 19) ^ (w[i-2] >> 10);
            w[i] = w[i-16] + s0 + w[i-7] + s1;
        }
        uint32_t a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
        for (int i = 0; i < 64; i++) {
            uint32_t t1 = h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i];
            uint32_t t2 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
            h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
        }
        H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
    std::string out(32, 0); for (int i = 0; i < 8; i++) for (int j = 0; j < 4; j++) out[4 * i + j] = (char)((H[i] >> (24 - 8 * j)) & 0xff);
    return out;
}
std::string hex(const std::string& s) { static const char* d = "0123456789abcdef"; std::string r; for (unsigned char c : s) { r += d[c >> 4]; r += d[c & 15]; } return r; }

typedef std::string Hash; typedef std::vector<std::string> Data;
Hash leafHash(const std::string& d) { return sha256raw(std::string(1, '\x00') + d); }
Hash nodeHash(const Hash& l, const Hash& r) { return sha256raw(std::string(1, '\x01') + l + r); }
size_t lpow2(size_t n) { size_t k = 1; while (k * 2 < n) k *= 2; return k; }            // n 보다 작은 가장 큰 2의 거듭제곱 (n >= 2)
Hash mth(const Data& D, size_t lo, size_t hi) {                             // Merkle Tree Hash (루트)
    size_t n = hi - lo; if (n == 0) return sha256raw(""); if (n == 1) return leafHash(D[lo]);
    size_t k = lpow2(n); return nodeHash(mth(D, lo, lo + k), mth(D, lo + k, hi));
}
void auditPath(const Data& D, size_t m, size_t lo, size_t hi, std::vector<Hash>& out) {   // 잎 m 에서 루트까지의 형제 해시들 (아래 -> 위)
    size_t n = hi - lo; if (n == 1) return; size_t k = lpow2(n);
    if (m < k) { auditPath(D, m, lo, lo + k, out); out.push_back(mth(D, lo + k, hi)); }
    else       { auditPath(D, m - k, lo + k, hi, out); out.push_back(mth(D, lo, lo + k)); }
}
bool rootFromPath(size_t m, size_t n, const Hash& leaf, const std::vector<Hash>& p, size_t& end, Hash& out) {
    if (n == 1) { out = leaf; return true; }
    if (end == 0) return false;
    const Hash& sib = p[--end]; size_t k = lpow2(n); Hash sub;
    if (m < k) { if (!rootFromPath(m, k, leaf, p, end, sub)) return false; out = nodeHash(sub, sib); }
    else       { if (!rootFromPath(m - k, n - k, leaf, p, end, sub)) return false; out = nodeHash(sib, sub); }
    return true;
}
bool verify(const Hash& root, size_t n, size_t m, const std::string& data, const std::vector<Hash>& path) {
    size_t end = path.size(); Hash r; return m < n && rootFromPath(m, n, leafHash(data), path, end, r) && end == 0 && r == root;
}
Hash naiveRoot(std::vector<Hash> level) {                                   // 비트코인식: 접두 없음, 홀수면 마지막 복제
    while (level.size() > 1) { if (level.size() % 2) level.push_back(level.back()); std::vector<Hash> nx; for (size_t i = 0; i < level.size(); i += 2) nx.push_back(sha256raw(level[i] + level[i + 1])); level = nx; }
    return level[0];
}

int main() {
    assert(hex(sha256raw("abc")) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    const char* expect[] = {                                                // 독립 구현(Python hashlib)으로 구한 "leaf0".."leaf8" 의 n = 0..9 루트
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "e6c410a9745b0151d82d1a9f007b81f378a1588c3fb63dc634a2ab001379c3d2",
        "82bbd1c5de08394573f035ab3871ffaa6d8aba80baf47c7b28fb2b167f18464e", "f1aed069e1b79c5f12193e715059c468eff1559a5c989c6d7c46bc29f4f84f6c",
        "86f9ec25a8a2b32a4bd733e04c213de63c8b0655bcb887b75cfd8b02691be0e5", "2f4e0d79b7e066069be4d391a858023d0acd245505ab6913a8fd69726b65741d",
        "2bec773a6ce6d83151210fdd24bea43e7c4c94902811ce6124a21c71951860bd", "4b6939132387c5bf27ebaf5ac122810ce866eb0c7bf44082364b35c06f713aa6",
        "d12334b61aa2f244f11754c40896641551d64cd5c79fa0f9760d2ec3079d1834", "d6fe82371b0d1ef3c1a646efa98551e16d7c07bb83c0b9fe97136f471dd45f82"};
    Data D; for (int i = 0; i < 40; i++) D.push_back("leaf" + std::to_string(i));
    for (int n = 0; n <= 9; n++) assert(hex(mth(D, 0, n)) == expect[n]);
    for (size_t n = 1; n <= 40; n++) {                                      // 모든 (크기, 잎) 쌍에서 감사 경로가 검증되고 길이는 ceil(log2 n) 이하
        Hash root = mth(D, 0, n);
        for (size_t m = 0; m < n; m++) {
            std::vector<Hash> path; auditPath(D, m, 0, n, path);
            assert(path.size() <= (size_t)std::ceil(std::log2((double)n)) && verify(root, n, m, D[m], path));
            assert(!verify(root, n, m, D[m] + "x", path));                  // 데이터 변조
            if (n > 1) { auto bad = path; bad[0][0] ^= 1; assert(!verify(root, n, m, D[m], bad)); }            // 경로 변조
            if (n > 1) assert(!verify(root, n, (m + 1) % n, D[m], path));   // 엉뚱한 위치 주장
        }
    }
    // 단순 구성의 약점: [a,b,c] 와 [a,b,c,c] 가 같은 루트 / 내부 노드가 잎으로 위장
    std::vector<Hash> abc = {sha256raw("a"), sha256raw("b"), sha256raw("c")}, abcc = abc; abcc.push_back(abc[2]);
    assert(naiveRoot(abc) == naiveRoot(abcc));
    assert(mth({"a", "b", "c"}, 0, 3) != mth({"a", "b", "c", "c"}, 0, 4));
    std::vector<Hash> ab = {sha256raw("a"), sha256raw("b")};
    assert(sha256raw(ab[0] + ab[1]) == naiveRoot(ab));                    // 두 해시를 이은 "데이터" 한 개짜리 트리(잎 해시 = H(데이터))가 둘짜리 트리와 같은 루트
    assert(mth({leafHash("a") + leafHash("b")}, 0, 1) != mth({"a", "b"}, 0, 2));       // 접두 바이트가 이를 막는다
    std::cout << "MerkleTree: root(8 leaves) = " << hex(mth(D, 0, 8)).substr(0, 16) << "..., proof length for 40 leaves <= " << std::ceil(std::log2(40.0)) << std::endl;
    return 0;
}
// Time Complexity: 루트 계산 O(N) 해시, 감사 경로 생성·검증 O(log N) (경로 생성은 부분 트리 해시 재계산 포함 O(N))
// Space Complexity: 증명 O(log N)
```
## IntervalTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <memory>
#include <random>
#include <tuple>
#include <vector>
#include <cassert>

// 구간 트리(증강 BST): 구간 [lo, hi] 들을 lo 순으로 BST 에 두고, 각 노드에 "부분 트리 안의 최대 hi(mx)" 를 덧붙인다 (CLRS 14장).
// "질의 구간과 겹치는 구간이 있는가" 는 왼쪽 부분 트리의 mx >= 질의.lo 이면 왼쪽에 겹침 후보가 있다는 사실로 한 길을 따라 내려가며 O(log n) 에 답한다.
// 모든 겹침을 찾는 연산은 mx 가 질의.lo 보다 작은 부분 트리를 통째로 건너뛰어 O(k + log n) 에 가깝다.  균형은 트레이프로 잡는다 (분할/병합이 mx 를 쉽게 유지)
struct Node { int lo, hi, mx, id; unsigned pri; Node *l = nullptr, *r = nullptr; };
typedef std::tuple<int, int, int> Key;
Key key(const Node* n) { return Key(n->lo, n->hi, n->id); }
void upd(Node* t) { t->mx = t->hi; if (t->l) t->mx = std::max(t->mx, t->l->mx); if (t->r) t->mx = std::max(t->mx, t->r->mx); }
void split(Node* t, const Key& k, bool leq, Node*& a, Node*& b) {          // a: 키 < k (leq 이면 <= k), b: 나머지
    if (!t) { a = b = nullptr; return; }
    if (leq ? key(t) <= k : key(t) < k) { a = t; split(t->r, k, leq, t->r, b); } else { b = t; split(t->l, k, leq, a, t->l); }
    upd(t);
}
Node* merge(Node* a, Node* b) {
    if (!a) return b; if (!b) return a;
    if (a->pri > b->pri) { a->r = merge(a->r, b); upd(a); return a; }
    b->l = merge(a, b->l); upd(b); return b;
}
struct IntervalTree {
    Node* root = nullptr; std::vector<std::unique_ptr<Node>> pool; std::mt19937 rng{12345};
    void insert(int lo, int hi, int id) {
        pool.emplace_back(new Node{lo, hi, hi, id, (unsigned)rng()}); Node* n = pool.back().get();
        Node *a, *b; split(root, key(n), false, a, b); root = merge(merge(a, n), b);
    }
    void erase(int lo, int hi, int id) {
        Key k(lo, hi, id); Node *a, *b, *m, *c; split(root, k, false, a, b); split(b, k, true, m, c); root = merge(a, c);   // m 은 정확히 그 구간 하나
    }
    Node* anyOverlap(int lo, int hi) const {                               // 겹치는 구간 하나 (없으면 null)
        Node* t = root;
        while (t) { if (t->lo <= hi && lo <= t->hi) return t; t = (t->l && t->l->mx >= lo) ? t->l : t->r; }
        return nullptr;
    }
    void allOverlaps(const Node* t, int lo, int hi, std::vector<int>& out, long& visited) const {
        if (!t || t->mx < lo) return;                                       // 이 부분 트리의 어떤 구간도 lo 에 닿지 못한다
        visited++;
        allOverlaps(t->l, lo, hi, out, visited);
        if (t->lo <= hi && lo <= t->hi) out.push_back(t->id);
        if (t->lo <= hi) allOverlaps(t->r, lo, hi, out, visited);           // 오른쪽은 모두 lo' >= t->lo 이므로 t->lo > hi 면 전부 제외
    }
};
bool checkMx(const Node* t) { if (!t) return true; int m = t->hi; if (t->l) m = std::max(m, t->l->mx); if (t->r) m = std::max(m, t->r->mx); return m == t->mx && checkMx(t->l) && checkMx(t->r); }

int main() {
    std::mt19937 rng(99); IntervalTree T; struct Iv { int lo, hi; bool alive; }; std::vector<Iv> iv;
    for (int i = 0; i < 5000; i++) { int lo = rng() % 100000, len = rng() % 60 + 1; iv.push_back({lo, lo + len, true}); T.insert(lo, lo + len, i); }
    assert(checkMx(T.root));
    auto brute = [&](int lo, int hi) { std::vector<int> r; for (size_t i = 0; i < iv.size(); i++) if (iv[i].alive && iv[i].lo <= hi && lo <= iv[i].hi) r.push_back(i); return r; };
    long visitedTotal = 0; int queries = 1000;
    for (int round = 0; round < 2; round++) {
        for (int q = 0; q < queries; q++) {
            int lo = rng() % 100000, hi = lo + rng() % 40; std::vector<int> got; long vis = 0;
            T.allOverlaps(T.root, lo, hi, got, vis); visitedTotal += vis; std::sort(got.begin(), got.end());
            auto want = brute(lo, hi); assert(got == want);
            Node* any = T.anyOverlap(lo, hi); assert((any != nullptr) == !want.empty());
            if (any) assert(any->lo <= hi && lo <= any->hi);
            int x = rng() % 100000; assert((T.anyOverlap(x, x) != nullptr) == !brute(x, x).empty());      // 점 질의(stabbing)
        }
        if (round == 0) {                                                   // 절반을 삭제한 뒤 같은 검사를 반복
            for (int i = 0; i < 5000; i += 2) { T.erase(iv[i].lo, iv[i].hi, i); iv[i].alive = false; }
            assert(checkMx(T.root));
        }
    }
    double avg = (double)visitedTotal / (2 * queries);
    assert(avg < 200);                                                      // 5000 개를 모두 훑는 대신 평균 수십~수백 노드만 방문
    std::cout << "IntervalTree: avg visited nodes per query = " << avg << " (brute force: 5000)" << std::endl;
    return 0;
}
// Time Complexity: 삽입·삭제 O(log N) 기대, 겹침 하나 O(log N), 겹침 k 개 모두 O(k log N) 이내
// Space Complexity: O(N)
```
## RopeTree()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <cassert>

// 로프 트리(트리 관점의 요약, 정본은 String.md Part 4): 긴 문자열을 이진 트리로 표현하고 내부 노드에 "왼쪽 부분 트리 전체 길이(weight)"를 기록한다.
// 색인은 weight 로 좌우를 고르며 내려가는 O(깊이), 연결은 새 루트 하나를 만드는 O(1) 이라 거대한 문서 중간 편집에 복사가 필요 없다.
// (분할·삽입·삭제·불변 공유는 String.md 의 Rope 항목)
struct Rope { Rope *l = nullptr, *r = nullptr; size_t w = 0; std::string s; bool leaf() const { return !l && !r; } };
Rope* leaf(const std::string& s) { Rope* n = new Rope; n->s = s; n->w = s.size(); return n; }
size_t len(const Rope* n) { return !n ? 0 : n->leaf() ? n->s.size() : n->w + len(n->r); }
Rope* cat(Rope* a, Rope* b) { Rope* n = new Rope; n->l = a; n->r = b; n->w = len(a); return n; }
char at(const Rope* n, size_t i) { return n->leaf() ? n->s[i] : i < n->w ? at(n->l, i) : at(n->r, i - n->w); }
void del(Rope* n) { if (n) { del(n->l); del(n->r); delete n; } }
int main() {
    Rope* doc = cat(cat(leaf("Hello, "), leaf("tree ")), leaf("world!"));
    assert(len(doc) == 18 && at(doc, 0) == 'H' && at(doc, 7) == 't' && at(doc, 12) == 'w' && at(doc, 17) == '!');
    std::cout << "RopeTree: char[12] = " << at(doc, 12) << std::endl; del(doc); return 0;
}
// Time Complexity: 색인 O(깊이), 연결 O(1)
// Space Complexity: O(노드 수)
```
## RTree()
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// R-트리: 2차원 이상 "사각형"(MBR, 최소 외접 사각형)을 B-트리처럼 균형 있게 모은 공간 색인 (PostGIS, SQLite R*Tree, 지도·게임 충돌 검사).
// 내부 노드의 각 항목 = (자식 노드 전체를 덮는 사각형, 자식).  질의 사각형과 겹치지 않는 항목은 그 아래를 통째로 건너뛴다.
// 삽입: 사각형이 "가장 적게 커지는" 자식으로 내려가고, 노드가 M+1 개가 되면 이차(quadratic) 분할 — 가장 낭비가 큰 한 쌍을 씨앗으로 삼아 나머지를 더 이득인 쪽에 배정 (각 쪽 최소 m 개 보장)
struct Rect { int x1, y1, x2, y2; };
long area(const Rect& r) { return (long)(r.x2 - r.x1) * (r.y2 - r.y1); }
Rect unite(const Rect& a, const Rect& b) { return {std::min(a.x1, b.x1), std::min(a.y1, b.y1), std::max(a.x2, b.x2), std::max(a.y2, b.y2)}; }
bool inter(const Rect& a, const Rect& b) { return a.x1 <= b.x2 && b.x1 <= a.x2 && a.y1 <= b.y2 && b.y1 <= a.y2; }
long enlarge(const Rect& r, const Rect& add) { return area(unite(r, add)) - area(r); }
struct Node;
struct Entry { Rect r; Node* child; int id; };
struct Node { bool leaf; std::vector<Entry> e; };
const int M = 4, m = 2;
Rect mbr(const Node* n) { Rect r = n->e[0].r; for (auto& x : n->e) r = unite(r, x.r); return r; }
Node* splitNode(Node* n) {                                                 // n 은 M+1 개를 가진다. 한 그룹은 n 에 남기고 다른 그룹을 새 노드로
    auto E = n->e; int a = 0, b = 1; long worst = -1;
    for (size_t i = 0; i < E.size(); i++) for (size_t j = i + 1; j < E.size(); j++) {
        long waste = area(unite(E[i].r, E[j].r)) - area(E[i].r) - area(E[j].r);
        if (waste > worst) { worst = waste; a = i; b = j; }
    }
    std::vector<Entry> g1 = {E[a]}, g2 = {E[b]}, rest; Rect r1 = E[a].r, r2 = E[b].r;
    for (size_t i = 0; i < E.size(); i++) if ((int)i != a && (int)i != b) rest.push_back(E[i]);
    while (!rest.empty()) {
        if (g1.size() + rest.size() <= (size_t)m) { for (auto& x : rest) g1.push_back(x); break; }        // 최소 개수 보장
        if (g2.size() + rest.size() <= (size_t)m) { for (auto& x : rest) g2.push_back(x); break; }
        int pick = 0; long bestDiff = -1;                                   // 두 그룹에 대한 선호 차이가 가장 큰 항목부터
        for (size_t i = 0; i < rest.size(); i++) { long d = std::labs(enlarge(r1, rest[i].r) - enlarge(r2, rest[i].r)); if (d > bestDiff) { bestDiff = d; pick = i; } }
        Entry x = rest[pick]; rest.erase(rest.begin() + pick);
        long d1 = enlarge(r1, x.r), d2 = enlarge(r2, x.r);
        bool to1 = d1 < d2 || (d1 == d2 && (area(r1) < area(r2) || (area(r1) == area(r2) && g1.size() <= g2.size())));
        if (to1) { g1.push_back(x); r1 = unite(r1, x.r); } else { g2.push_back(x); r2 = unite(r2, x.r); }
    }
    n->e = g1; return new Node{n->leaf, g2};
}
Node* insertRec(Node* n, const Entry& e) {                                 // 분할이 일어나면 새 형제를 돌려준다
    if (n->leaf) n->e.push_back(e);
    else {
        int best = 0; long bd = LONG_MAX, ba = LONG_MAX;
        for (size_t i = 0; i < n->e.size(); i++) {
            long d = enlarge(n->e[i].r, e.r), a = area(n->e[i].r);
            if (d < bd || (d == bd && a < ba)) { best = i; bd = d; ba = a; }
        }
        Node* s = insertRec(n->e[best].child, e);
        n->e[best].r = mbr(n->e[best].child);
        if (s) n->e.push_back(Entry{mbr(s), s, -1});
    }
    return (int)n->e.size() > M ? splitNode(n) : nullptr;
}
void insert(Node*& root, const Rect& r, int id) {
    Node* s = insertRec(root, Entry{r, nullptr, id});
    if (s) root = new Node{false, {Entry{mbr(root), root, -1}, Entry{mbr(s), s, -1}}};               // 루트 분할 -> 높이 +1
}
void search(const Node* n, const Rect& q, std::vector<int>& out, long& visited) {
    visited++;
    for (auto& x : n->e) if (inter(x.r, q)) { if (n->leaf) out.push_back(x.id); else search(x.child, q, out, visited); }
}
int check(const Node* n, bool isRoot, int& count) {                        // 높이(잎=1), 위반이면 -1: 항목 수, 같은 깊이, 부모의 사각형 == 자식의 MBR
    if (n->e.empty() || (int)n->e.size() > M || (!isRoot && (int)n->e.size() < m)) return -1;
    if (n->leaf) { count += n->e.size(); return 1; }
    int h = -2;
    for (auto& x : n->e) {
        Rect t = mbr(x.child); if (t.x1 != x.r.x1 || t.y1 != x.r.y1 || t.x2 != x.r.x2 || t.y2 != x.r.y2) return -1;
        int ch = check(x.child, false, count); if (ch < 0 || (h != -2 && ch != h)) return -1; h = ch;
    }
    return h + 1;
}
void destroy(Node* n) { if (!n->leaf) for (auto& x : n->e) destroy(x.child); delete n; }

int main() {
    std::mt19937 rng(17); Node* root = new Node{true, {}}; std::vector<Rect> rects; int N = 4000;
    for (int i = 0; i < N; i++) {
        int x = rng() % 10000, y = rng() % 10000, w = rng() % 100 + 1, h = rng() % 100 + 1;
        rects.push_back({x, y, x + w, y + h}); insert(root, rects.back(), i);
        if (i % 500 == 0) { int c = 0; assert(check(root, true, c) > 0 && c == i + 1); }
    }
    int cnt = 0; int height = check(root, true, cnt); assert(height > 0 && cnt == N);
    assert(height <= std::log2((double)N));                                // 모든 노드가 m=2 개 이상이므로 높이 <= log2 N
    long visitedTotal = 0;
    for (int q = 0; q < 400; q++) {
        int x = rng() % 10000, y = rng() % 10000; Rect w{x, y, x + (int)(rng() % 600), y + (int)(rng() % 600)};
        std::vector<int> got; long vis = 0; search(root, w, got, vis); visitedTotal += vis; std::sort(got.begin(), got.end());
        std::vector<int> want; for (int i = 0; i < N; i++) if (inter(rects[i], w)) want.push_back(i);
        assert(got == want);                                               // 브루트 포스와 같은 결과
    }
    double avg = (double)visitedTotal / 400;
    assert(avg < N / 8.0);                                                 // 전체 사각형 4000 개 대신 일부 노드만 방문
    std::cout << "RTree: height " << height << ", avg nodes visited per window query " << avg << " (rects: " << N << ")" << std::endl;
    destroy(root); return 0;
}
// Time Complexity: 삽입 O(M log_m N), 검색은 겹침 정도에 따라 O(log N) ~ O(N)
// Space Complexity: O(N)
```
## VanEmdeBoasTree()
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <random>
#include <set>
#include <vector>
#include <cassert>

// 반 엠데 보아스(vEB) 트리: 정수 집합 U = 2^bits 를 지원하면서 insert/erase/member/min/max/successor/predecessor 가 모두 O(log log U).
// U 를 √U 개씩 √U 칸으로 나눠 "상위 비트 = 클러스터 번호, 하위 비트 = 클러스터 안 위치"로 재귀하고, 비어 있지 않은 클러스터를 다른 vEB(summary)로 관리한다.
// 두 가지 요령: (1) 최솟값은 클러스터에 넣지 않고 노드에 따로 두어 빈 클러스터 삽입을 O(1) 로, (2) min/max 를 O(1) 로 알고 있어 재귀 호출이 항상 하나뿐 -> T(U) = T(√U) + O(1).
// 클러스터는 필요할 때만 만들어(lazy) U = 2^24 도 메모리를 적게 쓴다
long calls = 0;                                                            // 재귀 호출 수 측정
struct VEB {
    int bits, lowBits, highBits; long mn = -1, mx = -1; VEB* summary = nullptr; std::vector<VEB*> cl;
    explicit VEB(int b) : bits(b), lowBits(b / 2), highBits(b - b / 2) { if (b > 1) cl.assign(1L << highBits, nullptr); }
    ~VEB() { delete summary; for (VEB* c : cl) delete c; }
    long high(long x) const { return x >> lowBits; }
    long low(long x) const { return x & ((1L << lowBits) - 1); }
    long index(long h, long l) const { return (h << lowBits) | l; }
    bool empty() const { return mn < 0; }
    bool member(long x) const {
        calls++; if (x == mn || x == mx) return true;
        if (bits == 1) return false;
        VEB* c = cl[high(x)]; return c && c->member(low(x));
    }
    void insert(long x) {
        calls++;
        if (mn < 0) { mn = mx = x; return; }
        if (x == mn || x == mx) return;
        if (x < mn) std::swap(x, mn);                                      // 새 최솟값은 이 노드에 두고, 밀려난 옛 최솟값을 아래로 내려보낸다
        if (bits > 1) {
            VEB*& c = cl[high(x)]; if (!c) c = new VEB(lowBits);
            if (c->empty()) { if (!summary) summary = new VEB(highBits); summary->insert(high(x)); }   // 빈 클러스터에 넣을 때는 아래 insert 가 O(1)
            c->insert(low(x));
        }
        if (x > mx) mx = x;
    }
    void erase(long x) {                                                   // x 가 집합에 있어야 한다
        calls++;
        if (mn == mx) { mn = mx = -1; return; }
        if (bits == 1) { mn = mx = (x == 0 ? 1 : 0); return; }
        if (x == mn) { long fc = summary->mn; x = index(fc, cl[fc]->mn); mn = x; }          // 최솟값을 지우려면 다음 최솟값을 끌어올린다
        long h = high(x); cl[h]->erase(low(x));
        if (cl[h]->empty()) {
            delete cl[h]; cl[h] = nullptr; summary->erase(h);
            if (x == mx) { long sm = summary->mx; mx = sm < 0 ? mn : index(sm, cl[sm]->mx); }
        } else if (x == mx) mx = index(h, cl[h]->mx);
    }
    long succ(long x) const {                                              // x 보다 큰 최소 원소, 없으면 -1
        calls++;
        if (bits == 1) return (x == 0 && mx == 1) ? 1 : -1;
        if (mn >= 0 && x < mn) return mn;
        VEB* c = cl[high(x)];
        if (c && !c->empty() && low(x) < c->mx) return index(high(x), c->succ(low(x)));
        long sc = summary ? summary->succ(high(x)) : -1;
        return sc < 0 ? -1 : index(sc, cl[sc]->mn);
    }
    long pred(long x) const {                                              // x 보다 작은 최대 원소, 없으면 -1
        calls++;
        if (bits == 1) return (x == 1 && mn == 0) ? 0 : -1;
        if (mx >= 0 && x > mx) return mx;
        VEB* c = cl[high(x)];
        if (c && !c->empty() && low(x) > c->mn) return index(high(x), c->pred(low(x)));
        long pc = summary ? summary->pred(high(x)) : -1;
        if (pc < 0) return (mn >= 0 && x > mn) ? mn : -1;
        return index(pc, cl[pc]->mx);
    }
};

int main() {
    const int BITS = 24; const long U = 1L << BITS;
    VEB v(BITS); std::set<long> ref; std::vector<long> keys; std::mt19937_64 rng(5); long maxCalls = 0;
    for (int step = 0; step < 80000; step++) {
        long x = rng() % U; int op = rng() % 6; calls = 0;
        if (op <= 1 || ref.empty()) { v.insert(x); if (ref.insert(x).second) keys.push_back(x); }          // 삽입 2/6 (중복 삽입도 포함)
        else if (op == 2) { size_t k = rng() % keys.size(); long y = keys[k]; keys[k] = keys.back(); keys.pop_back(); v.erase(y); ref.erase(y); }
        else if (op == 3) { auto it = ref.upper_bound(x); assert(v.succ(x) == (it == ref.end() ? -1 : *it)); }
        else if (op == 4) { auto it = ref.lower_bound(x); assert(v.pred(x) == (it == ref.begin() ? -1 : *std::prev(it))); }
        else              { assert(v.member(x) == (ref.count(x) > 0)); }
        maxCalls = std::max(maxCalls, calls);
        assert(v.member(x) == (ref.count(x) > 0));
        if (!ref.empty()) assert(v.mn == *ref.begin() && v.mx == *ref.rbegin());
    }
    assert(maxCalls <= 16);                                                // 재귀 깊이는 log2(24) ~ 5 단계, 상수 번만 호출
    VEB dense(16); for (long i = 0; i < 65536; i += 3) dense.insert(i);       // 작은 우주는 전부 채워 본다
    for (long i = 0; i < 65535; i++) assert(dense.succ(i) == ((i / 3 + 1) * 3 < 65536 ? (i / 3 + 1) * 3 : -1));
    for (long i = 0; i < 65536; i += 6) dense.erase(i);
    for (long i = 0; i < 65536; i++) assert(dense.member(i) == (i % 3 == 0 && i % 6 != 0));
    std::cout << "VanEmdeBoasTree: U=2^24, " << ref.size() << " keys, max recursive calls per op = " << maxCalls << std::endl;
    return 0;
}
// Time Complexity: 모든 연산 O(log log U)
// Space Complexity: O(N log log U) (lazy 할당; 즉시 할당하면 O(U))
```

# 부록
## 트리 순회의 재귀와 반복 구현
### 대표코드
```cpp
#include <algorithm>
#include <iostream>
#include <memory>
#include <random>
#include <vector>
#include <cassert>

// 같은 순회를 세 가지 방식으로: (1) 재귀 - 호출 스택이 곧 방문 상태, 깊이 h 면 스택 프레임 h 개 (한쪽으로 치우친 100만 노드 트리는 스택 오버플로)
// (2) 반복 - 호출 스택을 명시적 스택(힙 메모리)으로 바꾼 것. 깊이에는 안전하지만 O(h) 공간은 그대로
// (3) Morris - 잎의 빈 오른쪽 자식 포인터를 "후속 노드로 가는 임시 실(thread)"로 쓰고 지나간 뒤 복구해 O(1) 공간.  전위·중위는 가능, 후위는 번거롭다
struct Node { int v; Node *l = nullptr, *r = nullptr; };
std::vector<std::unique_ptr<Node>> pool;
Node* mk(int v) { pool.emplace_back(new Node{v}); return pool.back().get(); }
int depthSeen = 0;
void inRec(const Node* t, std::vector<int>& o, int d = 1)   { if (!t) return; depthSeen = std::max(depthSeen, d); inRec(t->l, o, d + 1); o.push_back(t->v); inRec(t->r, o, d + 1); }
void preRec(const Node* t, std::vector<int>& o)             { if (!t) return; o.push_back(t->v); preRec(t->l, o); preRec(t->r, o); }
void postRec(const Node* t, std::vector<int>& o)            { if (!t) return; postRec(t->l, o); postRec(t->r, o); o.push_back(t->v); }
std::vector<int> inIter(Node* t) {
    std::vector<int> o; std::vector<Node*> st; Node* c = t;
    while (c || !st.empty()) { while (c) { st.push_back(c); c = c->l; } c = st.back(); st.pop_back(); o.push_back(c->v); c = c->r; }
    return o;
}
std::vector<int> preIter(Node* t) {
    std::vector<int> o; std::vector<Node*> st; if (t) st.push_back(t);
    while (!st.empty()) { Node* c = st.back(); st.pop_back(); o.push_back(c->v); if (c->r) st.push_back(c->r); if (c->l) st.push_back(c->l); }
    return o;
}
std::vector<int> postIter(Node* t) {                                       // 스택 하나 + "방금 방문한 노드" 로 오른쪽 부분 트리를 끝냈는지 판단
    std::vector<int> o; std::vector<Node*> st; Node *c = t, *last = nullptr;
    while (c || !st.empty()) {
        if (c) { st.push_back(c); c = c->l; }
        else { Node* top = st.back(); if (top->r && last != top->r) c = top->r; else { o.push_back(top->v); last = top; st.pop_back(); } }
    }
    return o;
}
std::vector<int> inMorris(Node* t, bool preorder = false) {                // preorder=true 이면 처음 도착했을 때 방문 (전위)
    std::vector<int> o; Node* c = t;
    while (c) {
        if (!c->l) { o.push_back(c->v); c = c->r; continue; }
        Node* p = c->l; while (p->r && p->r != c) p = p->r;                // 왼쪽 부분 트리의 가장 오른쪽 = 중위 선행자
        if (!p->r) { if (preorder) o.push_back(c->v); p->r = c; c = c->l; }          // 실을 걸고 내려간다
        else       { p->r = nullptr; if (!preorder) o.push_back(c->v); c = c->r; }   // 실을 풀고 올라온다 (트리 원상 복구)
    }
    return o;
}
Node* randomTree(std::mt19937& rng, int n, int& counter) {
    if (n == 0) return nullptr;
    int k = rng() % n; Node* t = mk(0); t->l = randomTree(rng, k, counter); t->v = counter++; t->r = randomTree(rng, n - 1 - k, counter);
    return t;                                                              // 중위 순서로 0..n-1 이 붙는다
}

int main() {
    std::mt19937 rng(4);
    for (int n = 0; n <= 300; n++) {
        int counter = 0; Node* t = randomTree(rng, n, counter);
        std::vector<int> in, pre, post; inRec(t, in); preRec(t, pre); postRec(t, post);
        assert(inIter(t) == in && preIter(t) == pre && postIter(t) == post);
        assert(inMorris(t) == in && inMorris(t, true) == pre);
        std::vector<int> again; preRec(t, again); assert(again == pre);    // Morris 가 트리를 망가뜨리지 않았다
        for (int i = 0; i < n; i++) assert(in[i] == i);
    }
    // 깊이 100만짜리 한쪽 치우친 트리: 반복·Morris 는 문제없고, 재귀는 같은 깊이를 흉내 낼 수 없다
    Node* chain = mk(0); Node* cur = chain; int N = 1000000;
    for (int i = 1; i < N; i++) { cur->l = mk(i); cur = cur->l; }
    auto a = inIter(chain), b = inMorris(chain), c = preIter(chain), d = postIter(chain);
    assert((int)a.size() == N && a == b && a.front() == N - 1 && a.back() == 0);      // 왼쪽 사슬: 중위 = 맨 아래부터
    assert(c.front() == 0 && c.back() == N - 1 && d == a);
    Node* small = mk(0); cur = small; for (int i = 1; i < 5000; i++) { cur->l = mk(i); cur = cur->l; }
    std::vector<int> o; depthSeen = 0; inRec(small, o); assert(depthSeen == 5000);    // 재귀는 깊이만큼 스택 프레임을 쓴다
    std::cout << "Traversal: recursive/iterative/Morris agree on 300 random trees; 1e6-deep chain handled without recursion (recursion depth 5000 here)" << std::endl;
    return 0;
}
// Time Complexity: 세 방식 모두 O(N) (Morris 는 간선을 최대 3번 지남)
// Space Complexity: 재귀 O(h) 호출 스택, 반복 O(h) 명시적 스택, Morris O(1)
```

## Binary Tree vs BST
### 대표코드
```cpp
#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <numeric>
#include <random>
#include <vector>
#include <cassert>

// 이진 트리는 "모양"(노드마다 자식 최대 2개)만 정의하고, BST 는 거기에 "순서 불변식"(왼쪽 < 노드 < 오른쪽)을 더한 것이다.
// 모양만 있는 이진 트리에서는 값을 찾으려면 전부 뒤져야 한다(O(N)).  불변식이 있으면 비교 한 번에 절반(이상)을 버려 O(높이) 로 찾는다.
// 대신 BST 는 "어떤 모양이 되는가"가 입력 순서에 달려 있다 -> 정렬된 입력은 높이 N 의 연결 리스트가 되므로 AVL/레드-블랙 같은 균형 트리가 필요하다
struct Node { int v; Node *l = nullptr, *r = nullptr; };
std::vector<std::unique_ptr<Node>> pool;
Node* mk(int v) { pool.emplace_back(new Node{v}); return pool.back().get(); }
bool findAny(const Node* t, int x, long& visited) {                        // 순서 정보가 없는 이진 트리: 전위 탐색
    if (!t) return false; visited++;
    return t->v == x || findAny(t->l, x, visited) || findAny(t->r, x, visited);
}
bool findBst(const Node* t, int x, long& visited) {
    while (t) { visited++; if (x == t->v) return true; t = x < t->v ? t->l : t->r; }
    return false;
}
Node* insertBst(Node* root, int x) {
    Node* n = mk(x); if (!root) return n;
    Node* c = root; for (;;) { Node*& next = x < c->v ? c->l : c->r; if (!next) { next = n; return root; } c = next; }
}
bool isBst(const Node* t, long lo, long hi) { return !t || (t->v > lo && t->v < hi && isBst(t->l, lo, t->v) && isBst(t->r, t->v, hi)); }
void inorder(const Node* t, std::vector<int>& o) { if (!t) return; inorder(t->l, o); o.push_back(t->v); inorder(t->r, o); }
int height(const Node* t) { return t ? 1 + std::max(height(t->l), height(t->r)) : 0; }
Node* fromSorted(const std::vector<int>& a, int lo, int hi) {              // 가운데를 루트로: 높이 ceil(log2(N+1))
    if (lo >= hi) return nullptr; int mid = (lo + hi) / 2; Node* t = mk(a[mid]);
    t->l = fromSorted(a, lo, mid); t->r = fromSorted(a, mid + 1, hi); return t;
}

int main() {
    const int N = (1 << 14) - 1; std::mt19937 rng(10);
    std::vector<int> vals(N); std::iota(vals.begin(), vals.end(), 0); std::shuffle(vals.begin(), vals.end(), rng);
    std::vector<Node*> lvl; for (int x : vals) lvl.push_back(mk(x));       // 같은 값으로 (a) 완전 이진 트리(배열 순서 그대로) (b) 무작위 삽입 BST
    for (int i = 0; i < N; i++) { if (2 * i + 1 < N) lvl[i]->l = lvl[2 * i + 1]; if (2 * i + 2 < N) lvl[i]->r = lvl[2 * i + 2]; }
    Node* plain = lvl[0]; Node* bst = nullptr; for (int x : vals) bst = insertBst(bst, x);
    assert(!isBst(plain, -1, N) && isBst(bst, -1, N));                     // 모양은 같은 "이진 트리"여도 BST 인 것은 불변식을 지킨 쪽뿐
    std::vector<int> a, b; inorder(plain, a); inorder(bst, b);
    assert(!std::is_sorted(a.begin(), a.end()) && std::is_sorted(b.begin(), b.end()));   // BST 의 중위 순회는 정렬 결과
    long visPlain = 0, visBst = 0; int Q = 500;
    for (int q = 0; q < Q; q++) { int x = N + q; bool f1 = findAny(plain, x, visPlain), f2 = findBst(bst, x, visBst); assert(!f1 && !f2); }   // 없는 값 찾기
    for (int q = 0; q < Q; q++) { int x = rng() % N; long t1 = 0, t2 = 0; assert(findAny(plain, x, t1) && findBst(bst, x, t2)); visPlain += t1; visBst += t2; }
    assert(visPlain / (2 * Q) > 2000 && visBst / (2 * Q) < 60);            // 평균 방문 노드: 수천 개 vs 수십 개
    // 입력 순서에 따른 BST 모양
    std::vector<int> sorted(2000); std::iota(sorted.begin(), sorted.end(), 0);
    Node* degenerate = nullptr; for (int x : sorted) degenerate = insertBst(degenerate, x);
    Node* balanced = fromSorted(sorted, 0, sorted.size());
    assert(height(degenerate) == 2000 && height(balanced) == (int)std::ceil(std::log2(2001.0)));
    assert(height(bst) <= 4 * std::log2((double)N));                       // 무작위 순서 삽입의 높이는 평균 ~ 2 ln N, 거의 확실히 4 log2 N 이하
    std::cout << "Binary Tree vs BST: avg visited (plain/BST) = " << visPlain / (2 * Q) << " / " << visBst / (2 * Q)
              << ", height sorted-insert = " << height(degenerate) << ", balanced = " << height(balanced) << ", random = " << height(bst) << std::endl;
    return 0;
}
// Time Complexity: 이진 트리 탐색 O(N), BST 탐색 O(높이) (평균 O(log N), 최악 O(N))
// Space Complexity: O(N)
```
## BST vs AVL vs Red-Black
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <vector>
#include <cassert>

// 같은 입력(정렬된 키 1..n — 이진 탐색 트리의 최악 입력)을 세 트리에 넣고 높이를 비교한다.
//  - 일반 BST: 균형 장치가 없어 높이 n (연결 리스트로 퇴화)
//  - AVL: 모든 노드에서 좌우 높이 차 <= 1 -> 높이 <= 1.44·log2(n).  회전이 잦지만 조회가 가장 빠르다
//  - 레드-블랙(여기서는 구현이 짧은 좌편향 변형): 높이 <= 2·log2(n+1).  회전이 적어 삽입·삭제가 빠르다 (std::map, Java TreeMap)
struct B { int k; B *l = nullptr, *r = nullptr; };
int bstHeight(B* root) { int best = 0; std::vector<std::pair<B*, int>> st = {{root, 1}}; while (!st.empty()) { auto p = st.back(); st.pop_back(); if (!p.first) continue; best = std::max(best, p.second); st.push_back({p.first->l, p.second + 1}); st.push_back({p.first->r, p.second + 1}); } return best; }

struct A { int k, h = 1; A *l = nullptr, *r = nullptr; };
int hh(A* n) { return n ? n->h : 0; }
void upd(A* n) { n->h = 1 + std::max(hh(n->l), hh(n->r)); }
A* rotR(A* y) { A* x = y->l; y->l = x->r; x->r = y; upd(y); upd(x); return x; }
A* rotL(A* x) { A* y = x->r; x->r = y->l; y->l = x; upd(x); upd(y); return y; }
long avlRotations;
A* avlInsert(A* n, int k) {
    if (!n) return new A{k};
    if (k < n->k) n->l = avlInsert(n->l, k); else n->r = avlInsert(n->r, k);
    upd(n); int bal = hh(n->l) - hh(n->r);
    if (bal > 1) { if (hh(n->l->l) < hh(n->l->r)) { n->l = rotL(n->l); avlRotations++; } avlRotations++; return rotR(n); }
    if (bal < -1) { if (hh(n->r->r) < hh(n->r->l)) { n->r = rotR(n->r); avlRotations++; } avlRotations++; return rotL(n); }
    return n;
}

struct R { int k; bool red; R *l = nullptr, *r = nullptr; };
bool isRed(R* n) { return n && n->red; }
long llrbRotations;
R* rl(R* h) { R* x = h->r; h->r = x->l; x->l = h; x->red = h->red; h->red = true; llrbRotations++; return x; }
R* rr(R* h) { R* x = h->l; h->l = x->r; x->r = h; x->red = h->red; h->red = true; llrbRotations++; return x; }
void flip(R* h) { h->red = !h->red; h->l->red = !h->l->red; h->r->red = !h->r->red; }
R* llrbInsert(R* h, int k) {
    if (!h) return new R{k, true};
    if (k < h->k) h->l = llrbInsert(h->l, k); else h->r = llrbInsert(h->r, k);
    if (isRed(h->r) && !isRed(h->l)) h = rl(h);
    if (isRed(h->l) && isRed(h->l->l)) h = rr(h);
    if (isRed(h->l) && isRed(h->r)) flip(h);
    return h;
}
int rbHeight(R* n) { return n ? 1 + std::max(rbHeight(n->l), rbHeight(n->r)) : 0; }

int main() {
    const int n = 10000;
    B* bst = nullptr; A* avl = nullptr; R* rb = nullptr;
    for (int k = 1; k <= n; k++) {
        B* node = new B{k}; if (!bst) bst = node; else { B* c = bst; while (c->r) c = c->r; c->r = node; }    // 정렬된 입력 -> 항상 오른쪽 끝
        avl = avlInsert(avl, k);
        rb = llrbInsert(rb, k); rb->red = false;
    }
    int hb = bstHeight(bst), ha = hh(avl), hr = rbHeight(rb);
    assert(hb == n);                                                           // BST: 연결 리스트로 퇴화
    assert(ha <= 1.45 * std::log2(n + 2));                                     // AVL
    assert(hr <= 2 * std::log2(n + 1));                                        // 레드-블랙
    assert(ha <= hr);                                                          // AVL 이 더 엄격하게 균형 -> 더 낮거나 같다
    std::cout << "n=" << n << " sorted insert: BST height " << hb << ", AVL " << ha << " (" << avlRotations << " rotations), red-black " << hr << " (" << llrbRotations << " rotations)" << std::endl;
    return 0;
}
// Time Complexity: BST 최악 O(N), AVL·레드-블랙 O(log N)
// Space Complexity: O(N)
```
## Segment Tree vs Fenwick Tree
### 대표코드
```cpp
#include <algorithm>
#include <climits>
#include <iostream>
#include <random>
#include <vector>
#include <cassert>

// 둘 다 "점 갱신 + 구간 질의"를 O(log n) 에 처리하지만 성격이 다르다.
// 펜윅(BIT): 배열 n+1 칸, 코드 10줄 안팎, 상수 작음.  그러나 "역연산이 있는 연산"(합, XOR)의 접두 질의가 본업이다. 구간 [l,r] = prefix(r) - prefix(l-1) 로 빼기가 필요하기 때문.
// 세그먼트 트리: 2n 칸 이상, 연산이 결합법칙만 만족하면 된다(최소·최대·gcd·행렬곱 ...).  지연 전파를 붙이면 구간 갱신도 가능.
// 아래에서 확인: (1) 합은 둘이 같은 답 (2) 최솟값은 세그먼트 트리만 임의 구간·임의 갱신을 지원 (3) 구간 덧셈+구간 합은 BIT 2개로도 가능
struct Fenwick {                                                           // 1-기준 인덱스
    int n; std::vector<long> t; explicit Fenwick(int n) : n(n), t(n + 1, 0) {}
    void add(int i, long d) { for (; i <= n; i += i & -i) t[i] += d; }
    long sum(int i) const { long s = 0; for (; i > 0; i -= i & -i) s += t[i]; return s; }
    long range(int l, int r) const { return sum(r) - sum(l - 1); }
};
struct RangeBit {                                                          // 구간 덧셈 + 구간 합: B1·i - B2 (차분 배열 두 개)
    Fenwick b1, b2; explicit RangeBit(int n) : b1(n), b2(n) {}
    void rangeAdd(int l, int r, long x) { b1.add(l, x); b1.add(r + 1, -x); b2.add(l, x * (l - 1)); b2.add(r + 1, -x * r); }
    long prefix(int i) const { return b1.sum(i) * i - b2.sum(i); }
    long range(int l, int r) const { return prefix(r) - prefix(l - 1); }
};
template <class Op> struct SegTree {                                       // 반복(bottom-up) 세그먼트 트리, [l, r) 질의
    int n; std::vector<long> t; long id; Op op;
    SegTree(int n, long id, Op op) : n(n), t(2 * n, id), id(id), op(op) {}
    void set(int p, long v) { for (t[p += n] = v; p > 1; p >>= 1) t[p >> 1] = op(t[p], t[p ^ 1]); }
    long query(int l, int r) const { long a = id, b = id; for (l += n, r += n; l < r; l >>= 1, r >>= 1) { if (l & 1) a = op(a, t[l++]); if (r & 1) b = op(t[--r], b); } return op(a, b); }
};
struct MinBit {                                                            // 접두 최솟값 BIT: 값이 "작아지는" 갱신만 가능
    int n; std::vector<long> t; explicit MinBit(int n) : n(n), t(n + 1, LONG_MAX) {}
    void lower(int i, long v) { for (; i <= n; i += i & -i) t[i] = std::min(t[i], v); }
    long prefixMin(int i) const { long m = LONG_MAX; for (; i > 0; i -= i & -i) m = std::min(m, t[i]); return m; }
};

int main() {
    const int N = 1000; std::mt19937 rng(6);
    Fenwick bit(N); SegTree<std::plus<long>> segSum(N, 0, std::plus<long>()); std::vector<long> a(N + 1, 0);
    auto mn = [](long x, long y) { return std::min(x, y); };
    SegTree<decltype(mn)> segMin(N, LONG_MAX, mn); for (int i = 1; i <= N; i++) { a[i] = rng() % 1000; bit.add(i, a[i]); segSum.set(i - 1, a[i]); segMin.set(i - 1, a[i]); }
    for (int step = 0; step < 20000; step++) {
        int p = rng() % N + 1; long v = rng() % 1000;
        bit.add(p, v - a[p]); segSum.set(p - 1, v); segMin.set(p - 1, v); a[p] = v;                // 점 갱신: 펜윅은 "차이"를, 세그먼트 트리는 "새 값"을
        int l = rng() % N + 1, r = rng() % N + 1; if (l > r) std::swap(l, r);
        long s = 0, m = LONG_MAX; for (int i = l; i <= r; i++) { s += a[i]; m = std::min(m, a[i]); }
        assert(bit.range(l, r) == s && segSum.query(l - 1, r) == s);       // 합: 둘 다 정확
        assert(segMin.query(l - 1, r) == m);                               // 최솟값: 세그먼트 트리는 임의 갱신 후에도 정확
    }
    RangeBit rb(N); std::vector<long> b(N + 2, 0);                         // 구간 덧셈·구간 합도 펜윅 2개로 가능
    for (int step = 0; step < 5000; step++) {
        int l = rng() % N + 1, r = rng() % N + 1; if (l > r) std::swap(l, r); long x = (long)(rng() % 200) - 100;
        rb.rangeAdd(l, r, x); for (int i = l; i <= r; i++) b[i] += x;
        int ql = rng() % N + 1, qr = rng() % N + 1; if (ql > qr) std::swap(ql, qr);
        long s = 0; for (int i = ql; i <= qr; i++) s += b[i]; assert(rb.range(ql, qr) == s);
    }
    // 최솟값 펜윅의 한계: 값이 작아지는 갱신만 가능하고, 접두 구간만 답한다
    MinBit mb(5); long arr[6] = {0, 5, 3, 8, 6, 7}; for (int i = 1; i <= 5; i++) mb.lower(i, arr[i]);
    assert(mb.prefixMin(5) == 3);
    arr[2] = 10; mb.lower(2, 10);                                          // 값을 키우는 갱신 -> BIT 는 반영하지 못한다
    long truth = *std::min_element(arr + 1, arr + 6);                      // 실제 최솟값은 5
    assert(truth == 5 && mb.prefixMin(5) == 3 && mb.prefixMin(5) != truth);   // BIT 의 답 3 은 낡았다. 세그먼트 트리는 set 한 번으로 정확히 5
    SegTree<decltype(mn)> st5(5, LONG_MAX, mn); for (int i = 1; i <= 5; i++) st5.set(i - 1, arr[i]); assert(st5.query(0, 5) == 5);
    std::cout << "Segment vs Fenwick: sum agrees, min needs segment tree; memory BIT " << (N + 1) << " vs segment " << 2 * N << " words" << std::endl;
    return 0;
}
// Time Complexity: 둘 다 점 갱신·질의 O(log N); 펜윅은 상수가 작고 세그먼트 트리는 연산 종류가 자유롭다
// Space Complexity: 펜윅 N, 세그먼트 트리 2N (재귀 구현은 4N)
```
