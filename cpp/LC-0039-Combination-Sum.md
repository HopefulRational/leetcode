# [39. Combination Sum](https://leetcode.com/problems/combination-sum/)

**Difficulty:** Medium

**Topics:** Array, Backtracking

---



<blockquote>

<p>Given an array of <strong>distinct</strong> integers <code>candidates</code> and a target integer <code>target</code>, return <em>a list of all <strong>unique combinations</strong> of </em><code>candidates</code><em> where the chosen numbers sum to </em><code>target</code><em>.</em> You may return the combinations in <strong>any order</strong>.</p>

<p>The <strong>same</strong> number may be chosen from <code>candidates</code> an <strong>unlimited number of times</strong>. Two combinations are unique if the <span data-keyword="frequency-array">frequency</span> of at least one of the chosen numbers is different.</p>

<p>The test cases are generated such that the number of unique combinations that sum up to <code>target</code> is less than <code>150</code> combinations for the given input.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> candidates = [2,3,6,7], target = 7
<strong>Output:</strong> [[2,2,3],[7]]
<strong>Explanation:</strong>
2 and 3 are candidates, and 2 + 2 + 3 = 7. Note that 2 can be used multiple times.
7 is a candidate, and 7 = 7.
These are the only two combinations.
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> candidates = [2,3,5], target = 8
<strong>Output:</strong> [[2,2,2,2],[2,3,3],[3,5]]
</pre>

<p><strong class="example">Example 3:</strong></p>

<pre>
<strong>Input:</strong> candidates = [2], target = 1
<strong>Output:</strong> []
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= candidates.length &lt;= 30</code></li>
	<li><code>2 &lt;= candidates[i] &lt;= 40</code></li>
	<li>All elements of <code>candidates</code> are <strong>distinct</strong>.</li>
	<li><code>1 &lt;= target &lt;= 40</code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        // commented region is basically for using sorting
        // ranges::sort(candidates);
        int n = candidates.size();
        vector<vector<int>> ans;
        vector<int> cur;
        cur.reserve(20);
        
        function<void(int, int)> dfs = [&](int idx, int rem) {
            if(rem == 0) {
                ans.push_back(cur);
                return;
            }
            // if(idx >= n) return;
            // if(candidates[idx] <= rem) {
            //     cur.push_back(candidates[idx]);
            //     dfs(idx, rem-candidates[idx]);
            //     cur.pop_back();
            //     dfs(idx+1, rem);
            // }
            if(rem < 0 || idx >= n) return;
            cur.push_back(candidates[idx]);
            dfs(idx, rem-candidates[idx]);
            cur.pop_back();
            dfs(idx+1, rem);
        };

        dfs(0, target);

        return ans;
    }
};
```
