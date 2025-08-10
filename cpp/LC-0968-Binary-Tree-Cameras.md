# [968. Binary Tree Cameras](https://leetcode.com/problems/binary-tree-cameras/)

**Difficulty:** Hard

**Topics:** Dynamic Programming, Tree, Depth-First Search, Binary Tree

---



<blockquote>

<p>You are given the <code>root</code> of a binary tree. We install cameras on the tree nodes where each camera at a node can monitor its parent, itself, and its immediate children.</p>

<p>Return <em>the minimum number of cameras needed to monitor all nodes of the tree</em>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>
<img alt="" src="https://assets.leetcode.com/uploads/2018/12/29/bst_cameras_01.png" style="width: 138px; height: 163px;" />
<pre>
<strong>Input:</strong> root = [0,0,null,0,0]
<strong>Output:</strong> 1
<strong>Explanation:</strong> One camera is enough to monitor all nodes if placed as shown.
</pre>

<p><strong class="example">Example 2:</strong></p>
<img alt="" src="https://assets.leetcode.com/uploads/2018/12/29/bst_cameras_02.png" style="width: 139px; height: 312px;" />
<pre>
<strong>Input:</strong> root = [0,0,null,0,null,0,null,null,0]
<strong>Output:</strong> 2
<strong>Explanation:</strong> At least two cameras are needed to monitor all nodes of the tree. The above image shows one of the valid configurations of camera placement.
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li>The number of nodes in the tree is in the range <code>[1, 1000]</code>.</li>
	<li><code>Node.val == 0</code></li>
</ul>


</blockquote>

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
// Idea: Not covering leaves. Better to cover their parents
enum STATUS {
    UNCOVERED,
    COVERED_BY_CHILD,
    COVERED_BY_ITSELF
};
class Solution {
public:
    int res;
    STATUS dfs(TreeNode *root) {
        // nullptr - COVERED_BY_CHILD bcoz COVERED_BY_ITSELF means leaf is coverd by camera at nullptr
        if(!root) return COVERED_BY_CHILD;
        STATUS left = dfs(root->left), right = dfs(root->right);
        if(left == UNCOVERED || right == UNCOVERED) {
            // cover root to cover the uncovered leaf
            ++res;
            return COVERED_BY_ITSELF;
        }

        return left == COVERED_BY_ITSELF || right == COVERED_BY_ITSELF ? COVERED_BY_CHILD : UNCOVERED;
    }
    int minCameraCover(TreeNode* root) {
        res = 0;
        return (dfs(root) == UNCOVERED ? 1 : 0) + res;
    }
};
```
