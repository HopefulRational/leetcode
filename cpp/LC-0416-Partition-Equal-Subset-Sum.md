# [416. Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/)

**Difficulty:** Medium

**Topics:** Array, Dynamic Programming

---



<blockquote>

<p>Given an integer array <code>nums</code>, return <code>true</code> <em>if you can partition the array into two subsets such that the sum of the elements in both subsets is equal or </em><code>false</code><em> otherwise</em>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> nums = [1,5,11,5]
<strong>Output:</strong> true
<strong>Explanation:</strong> The array can be partitioned as [1, 5, 5] and [11].
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> nums = [1,2,3,5]
<strong>Output:</strong> false
<strong>Explanation:</strong> The array cannot be partitioned into equal sum subsets.
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= nums.length &lt;= 200</code></li>
	<li><code>1 &lt;= nums[i] &lt;= 100</code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int sum = accumulate(nums.begin(), nums.end(), 0);
        if(sum & 1) return false;
        int n = nums.size();

        vector<bool> prev(sum+1, false), tmp(sum+1, false);
        prev[0] = true;
        prev[nums[0]] = true;
        for(int i=1; i<n; ++i) {
            // tmp[0] = true; // we never touch target = 0 
            for(int target=1; target<=sum/2; ++target) {
                bool notTake = prev[target];
                bool take = false;
                if(target >= nums[i]) {
                    take = prev[target-nums[i]];
                }
                tmp[target] = take || notTake;
            }
            swap(tmp, prev);
        }
        return prev[sum/2];

        // vector<vector<bool>> dp(n, vector<bool>(sum+1, false));
        // for(int i=0; i<n; ++i) dp[i][0] = true;
        // dp[0][nums[0]] = true;
        // for(int i=1; i<n; ++i) {
        //     for(int target=1; target<=sum/2; ++target) {
        //         bool notTake = dp[i-1][target];
        //         bool take = false;
        //         if(target >= nums[i]) {
        //             take = dp[i-1][target-nums[i]];
        //         }
        //         dp[i][target] = take | notTake;
        //     }
        // }
        // return dp[n-1][sum/2];

        // vector<vector<int>> dp(n, vector<int>(sum+1, -1)); // sum/2 ?
        // return f(nums.size()-1, sum/2, nums, dp);
    }
    bool f(int i, int target, vector<int>& nums, vector<vector<int>> &dp) {
        if(target == 0) return true;
        if(i == 0) return nums[0] == target;
        if(dp[i][target] != -1) return dp[i][target];
        bool notTake = f(i-1, target, nums, dp);
        bool take = false;
        if(target >= nums[i]) {
            take = f(i-1, target-nums[i], nums, dp);
        }
        return dp[i][target] = take | notTake;
    }
};
```
