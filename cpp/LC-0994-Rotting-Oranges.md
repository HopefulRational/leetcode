# [994. Rotting Oranges](https://leetcode.com/problems/rotting-oranges/)

**Difficulty:** Medium

**Topics:** Array, Breadth-First Search, Matrix

---



<blockquote>

<p>You are given an <code>m x n</code> <code>grid</code> where each cell can have one of three values:</p>

<ul>
	<li><code>0</code> representing an empty cell,</li>
	<li><code>1</code> representing a fresh orange, or</li>
	<li><code>2</code> representing a rotten orange.</li>
</ul>

<p>Every minute, any fresh orange that is <strong>4-directionally adjacent</strong> to a rotten orange becomes rotten.</p>

<p>Return <em>the minimum number of minutes that must elapse until no cell has a fresh orange</em>. If <em>this is impossible, return</em> <code>-1</code>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>
<img alt="" src="https://assets.leetcode.com/uploads/2019/02/16/oranges.png" style="width: 650px; height: 137px;" />
<pre>
<strong>Input:</strong> grid = [[2,1,1],[1,1,0],[0,1,1]]
<strong>Output:</strong> 4
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> grid = [[2,1,1],[0,1,1],[1,0,1]]
<strong>Output:</strong> -1
<strong>Explanation:</strong> The orange in the bottom left corner (row 2, column 0) is never rotten, because rotting only happens 4-directionally.
</pre>

<p><strong class="example">Example 3:</strong></p>

<pre>
<strong>Input:</strong> grid = [[0,2]]
<strong>Output:</strong> 0
<strong>Explanation:</strong> Since there are already no fresh oranges at minute 0, the answer is just 0.
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>m == grid.length</code></li>
	<li><code>n == grid[i].length</code></li>
	<li><code>1 &lt;= m, n &lt;= 10</code></li>
	<li><code>grid[i][j]</code> is <code>0</code>, <code>1</code>, or <code>2</code>.</li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    int orangesRotting(vector<vector<int>>& grid) {
        int m = grid.size(), n = grid[0].size(), fresh = 0;
        queue<pair<int,int>> q;
        
        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                if(grid[i][j] == 1) ++fresh;
                else if(grid[i][j] == 2) q.emplace(i,j);
            }
        }

        if(!fresh) return 0;

        int dirs[] = {1,0,-1,0,1};
        int ans = 0;

        while(fresh && q.size()) {
            for(int cnt = q.size(); cnt--;) {
                auto [x,y] = q.front(); q.pop();
                for(int i=0; i<4; ++i) {
                    int nx = x + dirs[i], ny = y + dirs[i+1];
                    if(nx >= 0 && nx < m && ny >= 0 && ny < n && grid[nx][ny] == 1)
                        --fresh, grid[nx][ny] = 2, q.emplace(nx, ny);
                }
            }
            ++ans;
        }

        return fresh == 0 ? ans : -1;
    }
};
```
