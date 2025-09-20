# [62. Unique Paths](https://leetcode.com/problems/unique-paths/)

**Difficulty:** Medium

**Topics:** Math, Dynamic Programming, Combinatorics

---



<blockquote>

<p>There is a robot on an <code>m x n</code> grid. The robot is initially located at the <strong>top-left corner</strong> (i.e., <code>grid[0][0]</code>). The robot tries to move to the <strong>bottom-right corner</strong> (i.e., <code>grid[m - 1][n - 1]</code>). The robot can only move either down or right at any point in time.</p>

<p>Given the two integers <code>m</code> and <code>n</code>, return <em>the number of possible unique paths that the robot can take to reach the bottom-right corner</em>.</p>

<p>The test cases are generated so that the answer will be less than or equal to <code>2 * 10<sup>9</sup></code>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>
<img src="https://assets.leetcode.com/uploads/2018/10/22/robot_maze.png" style="width: 400px; height: 183px;" />
<pre>
<strong>Input:</strong> m = 3, n = 7
<strong>Output:</strong> 28
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> m = 3, n = 2
<strong>Output:</strong> 3
<strong>Explanation:</strong> From the top-left corner, there are a total of 3 ways to reach the bottom-right corner:
1. Right -&gt; Down -&gt; Down
2. Down -&gt; Down -&gt; Right
3. Down -&gt; Right -&gt; Down
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= m, n &lt;= 100</code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    int uniquePaths(int m, int n) {
        /*
            To reach from [0,0] to [m-1, n-1], there should be
            (m-1) down and (n-1) right steps.
            Now, total num of steps:
                (m-1) + (n-1) = (m + n - 2)
            So the answer is num of ways 
            to have m-1 down steps from (m + n - 2), i.e.,
            (m+n-2)C(m-1) = (m+n-2)! / ((m-1)! * ((m+n-2)-(m-1))!)
            [nCr = n! / (r! * (n-r)!)]
        */

        int N = m+n-2;
        int r = m-1;
        double res = 1;

        for(int i=1; i<=r; ++i) {
            res = res * (N - r + i) / i;
        }

        return int(res);

        // vector<int> prev(n, 0);
        // for(int i=0; i<=m-1; ++i) {
        //     vector<int> tmp(n, 0);
        //     for(int j=0; j<=n-1; ++j) {
        //         if(i == 0 && j == 0) tmp[j] = 1;
        //         else {
        //             int up = 0, left = 0;
        //             if(i>0) up = prev[j];
        //             if(j>0) left = tmp[j-1];
        //             tmp[j] = up + left;
        //         }
        //     }
        //     swap(tmp, prev);
        // }
        // return prev[n-1];

        // vector<vector<int>> dp(m, vector<int>(n, 0));
        // dp[0][0] = 1;
        // for(int i=0; i<=m-1; ++i) {
        //     for(int j=0; j<=n-1; ++j) {
        //         if(i == 0 && j == 0) dp[0][0] = 1;
        //         else {
        //             int up = 0, left = 0;
        //             if(i>0) up = dp[i-1][j];
        //             if(j>0) left = dp[i][j-1];
        //             dp[i][j] = up + left;
        //         }
        //     }
        // }
        // return dp[m-1][n-1];
        
        // vector<vector<int>> dp(m, vector<int>(n, -1));
        // return f(m-1, n-1, dp);

    }
    int f(int i, int j, vector<vector<int>> &dp) {
        if(i == 0 && j == 0) return 1;
        if(i < 0 || j < 0) return 0;
        if(dp[i][j] != -1) return dp[i][j];
        int up = f(i-1, j, dp);
        int left = f(i, j-1, dp);
        return dp[i][j] = up + left;
    }
};
```
