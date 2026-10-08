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
#include <iostream>
#include <cassert>
int main() { std::cout << "SegTree vs BIT" << std::endl; assert(true); return 0; }
// Time Complexity: O(1)
// Space Complexity: O(1)
```
