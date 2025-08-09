# [257. Binary Tree Paths](https://leetcode.com/problems/binary-tree-paths/)

**Difficulty**: Easy  
**Topics**: String, Backtracking, Tree, Depth-First Search, Binary Tree

## Problem Statement

Given the `root` of a binary tree, return all root-to-leaf paths in any order .

A leaf is a node with no children.

## Examples

### Example 1:

**Input**: `root = [1,2,3,null,5]`  
**Output**: `["1->2->5","1->3"] `



### Example 2:

**Input**: `root = [1]`  
**Output**: `["1"] ` 



## Constraints

- The number of nodes in the tree is in the range `[1, 100]` .
- `-100 <= Node.val <= 100`

## Solution
```cpp
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
    inline void getString(vector<int>& tmp, string& s) {
        for(int i=0; i<tmp.size(); ++i) {
            s.append(to_string(tmp[i]));
            if(i != tmp.size()-1) s.append("->");
        }
    }
    void preorder(TreeNode* root, vector<int>& tmp, vector<string>& ans) {
        if(!root) return;
        if(!root->left && !root->right) {
            tmp.push_back(root->val);
            string s;
            getString(tmp, s);
            ans.push_back(s);
            tmp.pop_back();
            return;
        }
        tmp.push_back(root->val);
        preorder(root->left, tmp, ans);
        preorder(root->right, tmp, ans);
        tmp.pop_back();
    }
    vector<string> binaryTreePaths(TreeNode* root) {
        vector<string> ans;
        vector<int> tmp;
        preorder(root, tmp, ans);
        return ans;
    }
};
```
