# [120. Triangle](https://leetcode.com/problems/triangle/)

**Difficulty:** Medium

**Topics:** Array, Dynamic Programming

---



<blockquote>

<p>Given a <code>triangle</code> array, return <em>the minimum path sum from top to bottom</em>.</p>

<p>For each step, you may move to an adjacent number of the row below. More formally, if you are on index <code>i</code> on the current row, you may move to either index <code>i</code> or index <code>i + 1</code> on the next row.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]
<strong>Output:</strong> 11
<strong>Explanation:</strong> The triangle looks like:
   <u>2</u>
  <u>3</u> 4
 6 <u>5</u> 7
4 <u>1</u> 8 3
The minimum path sum from top to bottom is 2 + 3 + 5 + 1 = 11 (underlined above).
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> triangle = [[-10]]
<strong>Output:</strong> -10
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= triangle.length &lt;= 200</code></li>
	<li><code>triangle[0].length == 1</code></li>
	<li><code>triangle[i].length == triangle[i - 1].length + 1</code></li>
	<li><code>-10<sup>4</sup> &lt;= triangle[i][j] &lt;= 10<sup>4</sup></code></li>
</ul>

<p>&nbsp;</p>
<strong>Follow up:</strong> Could you&nbsp;do this using only <code>O(n)</code> extra space, where <code>n</code> is the total number of rows in the triangle?

</blockquote>

## Solution
```cpp
class Solution {
public:
    int minimumTotal(vector<vector<int>>& triangle) {
        int m = triangle.size();
        
        vector<int> prev(m, 0);
        for(int i = m-1; i>=0; --i) {
            vector<int> tmp(m, 0);
            for(int j = i; j >= 0; --j) {
                if(i == m-1) tmp[j] = triangle[i][j];
                else {
                    int up = triangle[i][j] + prev[j];
                    int diag = triangle[i][j] + prev[j+1];
                    tmp[j] = min(up, diag);
                }
            }
            swap(tmp, prev);
        }
        return prev[0];
        
        // vector<vector<int>> dp(m, vector<int>(m, 0));
        // for(int i = m-1; i>=0; --i) {
        //     for(int j = i; j >= 0; --j) {
        //         if(i == m-1) dp[i][j] = triangle[i][j];
        //         else {
        //             int up = triangle[i][j] + dp[i+1][j];
        //             int diag = triangle[i][j] + dp[i+1][j+1];
        //             dp[i][j] = min(up, diag);
        //         }
        //     }
        // }
        // return dp[0][0];

        // vector<vector<int>> dp(m, vector<int>(m, -1));
        // return f(0, 0, triangle, m, dp);

    }

    int f(int i, int j, vector<vector<int>>& triangle, int m, vector<vector<int>>& dp) {
        if(i == m-1) return triangle[i][j];
        if(dp[i][j] != -1) return dp[i][j];
        int down = triangle[i][j] + f(i+1, j, triangle, m, dp);
        int diag = triangle[i][j] + f(i+1, j+1, triangle, m, dp);
        return dp[i][j] = min(down, diag);
    }
};
```
