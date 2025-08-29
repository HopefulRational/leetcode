# [78. Subsets](https://leetcode.com/problems/subsets/)

**Difficulty:** Medium

**Topics:** Array, Backtracking, Bit Manipulation

---



<blockquote>

<p>Given an integer array <code>nums</code> of <strong>unique</strong> elements, return <em>all possible</em> <span data-keyword="subset"><em>subsets</em></span> <em>(the power set)</em>.</p>

<p>The solution set <strong>must not</strong> contain duplicate subsets. Return the solution in <strong>any order</strong>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> nums = [1,2,3]
<strong>Output:</strong> [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> nums = [0]
<strong>Output:</strong> [[],[0]]
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= nums.length &lt;= 10</code></li>
	<li><code>-10 &lt;= nums[i] &lt;= 10</code></li>
	<li>All the numbers of&nbsp;<code>nums</code> are <strong>unique</strong>.</li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        int n = nums.size();
        vector<int> cur;
        vector<vector<int>> ans;
        cur.reserve(n);
        ans.reserve(1 << n);
        
        function<void(int,int)> helper = [&](int inums, int jcur) {
            if(inums == n) {
                ans.push_back(cur);
                return;
            }
            cur.push_back(nums[inums]);
            helper(inums+1, jcur+1);
            cur.pop_back();
            helper(inums+1, jcur);
        };

        helper(0,0);

        return ans;
    }
};
```
