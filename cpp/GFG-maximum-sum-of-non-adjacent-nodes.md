# [Maximum sum of Non-adjacent nodes](https://www.geeksforgeeks.org/problems/maximum-sum-of-non-adjacent-nodes/1)

<blockquote>

## Problem Statement

Given a root of binary tree with a value associated with each node. Your task is to select a subset of nodes such that the sum of their values is maximized , with the condition that no two selected nodes are directly connected that is, if a node is included in the subset, neither its parent nor its children can be included.

Examples:

Input: root = [11, 1, 2]<br>
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/880845/Web/Other/blobid0_1732598044.png)<br>
Output: 11<br>
Explanation: The maximum sum is obtained by selecting the node 11.<br>
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/880845/Web/Other/blobid1_1732598102.png)<br>

Input: root = [1, 2, 3, 4, N, 5, 6]<br>
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/880845/Web/Other/blobid2_1732598208.png)<br>
Output: 16
Explanation: The maximum sum is obtained by selecting the nodes 1, 4, 5, and 6, which are not directly connected to each other. Their total sum is 16.<br>
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/880845/Web/Other/blobid3_1732598283.png)<br>

Constraints: 1 ≤ no. of nodes in the tree ≤ 10^4

1 ≤ Node.val ≤ 10^5

## Input Format

The tree in the input is given in the form of a string as described below.

The values in the string are in the order of level order traversal of the tree where, numbers denote node values, and a character “ N ” denotes NULL child. For example:<br>
![](https://media.geeksforgeeks.org/wp-content/uploads/20200124141533/Untitled-Diagram65.jpg)<br>
For the above tree, the string will be: 1 2 3 N N 4 6 N 5 N N 7 N

Example:

```
11 1 2
```

Sample Input:
11 1 2

## Examples

```
Input: root = [11, 1, 2]
Output: 11
Explanation: The maximum sum is obtained by selecting the node 11.

Input: root = [1, 2, 3, 4, N, 5, 6]
Output: 16
Explanation: The maximum sum is obtained by selecting the nodes 1, 4, 5, and 6, which are not directly connected to each other. Their total sum is 16.  
```

## Constraints

Constraints:

**Tags:** Tree, Data Structures

**Article / Editorial:**

- https://www.geeksforgeeks.org/maximum-sum-nodes-binary-tree-no-two-adjacent/


</blockquote>

## Solution
```cpp
/*
class Node {
public:
    int data;
    Node* left;
    Node* right;
    Node(int val) {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};
*/
class Solution {
  public:
    int getMaxSum(Node *root) {
        // auto ans = dfs(root);
        // return max(ans.first, ans.second);
        
        unordered_map<Node*, int> memo;
        return recur(root, memo);
    }
    
    // Top-Down DP
    int recur(Node *root, unordered_map<Node*, int> &memo) {
        if(!root) return 0;
        if(memo.count(root)) return memo[root];
        
        // include current node
        int incl = root->data;
        if(root->left) {
            incl += recur(root->left->left, memo)
                    + recur(root->left->right, memo);
        }
        if(root->right) {
            incl += recur(root->right->left, memo)
                    + recur(root->right->right, memo);
        }
        
        // exclude current node
        int excl = recur(root->left, memo)
                   + recur(root->right, memo);
        
        return memo[root] = max(incl, excl);
    }
    
    
    // returns pair (sumWithNode, sumWithoutNode)
    pair<int, int> dfs(Node *root) {
        if(!root) {
            return make_pair(0,0);
        }
        auto l = dfs(root->left);
        auto r = dfs(root->right);
        pair<int, int> cur;
        // include current node
        cur.first = l.second + r.second + root->data;
        // exclude current node
        cur.second = max(l.first, l.second)
                     + max(r.first, r.second);
        return cur;
    }
};
```
