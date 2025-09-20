# [213. House Robber II](https://leetcode.com/problems/house-robber-ii/)

**Difficulty:** Medium

**Topics:** Array, Dynamic Programming

---



<blockquote>

<p>You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. All houses at this place are <strong>arranged in a circle.</strong> That means the first house is the neighbor of the last one. Meanwhile, adjacent houses have a security system connected, and&nbsp;<b>it will automatically contact the police if two adjacent houses were broken into on the same night</b>.</p>

<p>Given an integer array <code>nums</code> representing the amount of money of each house, return <em>the maximum amount of money you can rob tonight <strong>without alerting the police</strong></em>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> nums = [2,3,2]
<strong>Output:</strong> 3
<strong>Explanation:</strong> You cannot rob house 1 (money = 2) and then rob house 3 (money = 2), because they are adjacent houses.
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> nums = [1,2,3,1]
<strong>Output:</strong> 4
<strong>Explanation:</strong> Rob house 1 (money = 1) and then rob house 3 (money = 3).
Total amount you can rob = 1 + 3 = 4.
</pre>

<p><strong class="example">Example 3:</strong></p>

<pre>
<strong>Input:</strong> nums = [1,2,3]
<strong>Output:</strong> 3
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= nums.length &lt;= 100</code></li>
	<li><code>0 &lt;= nums[i] &lt;= 1000</code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    int f(int start, int end, vector<int> &nums) {
        int prev1 = nums[start], prev2 = 0;
        for(int i=start+1; i<=end; ++i) {
            int pick = nums[i] + prev2;
            int notPick = 0 + prev1;
            int curi = max(pick, notPick);
            prev2 = prev1;
            prev1 = curi;
        }
        return prev1;
    }
    int rob(vector<int>& nums) {
        int n = nums.size();
        if(nums.size() == 1) return nums[0];
        return max(f(0, n-2, nums), f(1, n-1, nums));
    }
    // int f(int idx, int startIdx, vector<int> &arr, vector<int> &dp) {
    //     if(idx == startIdx) return arr[idx];
    //     if(idx < startIdx) return 0;
    //     if(dp[idx] != -1) dp[idx];
    //     int pick = arr[idx] + f(idx-2, startIdx, arr, dp);
    //     int notPick = 0 + f(idx-1, startIdx, arr, dp);
    //     return dp[idx] = max(pick, notPick);
    // }
    // int rob(vector<int>& nums) {
    //     int n = nums.size();
    //     if(nums.size() < 3) return *max_element(nums.begin(), nums.end());
    //     vector<int> dp(n, -1);
    //     int val1 = f(n-2, 0, nums, dp);
    //     fill(dp.begin(), dp.end(), -1);
    //     int val2 = f(n-1, 1, nums, dp);
    //     return max(val1, val2);
    // }
};
```
