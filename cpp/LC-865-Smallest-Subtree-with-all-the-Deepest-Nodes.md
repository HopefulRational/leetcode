# [865. Smallest Subtree with all the Deepest Nodes](https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/)

**Difficulty**: Medium  
**Topics**: Tree, Depth-First Search, Breadth-First Search, Binary Tree

## Problem Statement

Given the `root` of a binary tree, the **smallest subtree** that contains all the deepest nodes is called the *subtree with all the deepest nodes*.

Return the root of that subtree.

A node is called the *deepest* if it has the largest depth possible among any node in the entire tree.

The subtree of a node is a tree consisting of that node, plus all its descendants.

The answer is guaranteed to be unique.

## Examples

### Example 1:
**Input**: `root = [3,5,1,6,2,0,8,null,null,7,4]`  
**Output**: `[2,7,4]`  
**Explanation**:  
The deepest nodes are 7 and 4. The smallest subtree containing both is rooted at node 2.

### Example 2:
**Input**: `root = [1]`  
**Output**: `[1]`  
**Explanation**:  
The deepest node is the root itself.

### Example 3:
**Input**: `root = [0,1,3,null,2]`  
**Output**: `[2]`  
**Explanation**:  
The deepest node is 2 itself.

## Constraints
- The number of nodes in the tree is in the range `[1, 500]`.
- `0 <= Node.val <= 500`

## Solution
```cpp
// https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/solutions/146808/c-java-python-one-pass

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    pair<int, TreeNode*> deep(TreeNode* root) {
        if(!root) return {0, nullptr};
        auto l = deep(root->left);
        auto r = deep(root->right);
        int ld = l.first, rd = r.first;
        return {max(ld, rd) + 1, ld == rd ? root : (ld > rd ? l.second : r.second)};
    }
    TreeNode* subtreeWithAllDeepest(TreeNode* root) {
        return deep(root).second;
    }
};
```
