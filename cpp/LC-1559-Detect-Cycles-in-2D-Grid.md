# [1559. Detect Cycles in 2D Grid](https://leetcode.com/problems/detect-cycles-in-2d-grid/)

**Difficulty:** Medium

**Topics:** Array, Depth-First Search, Breadth-First Search, Union Find, Matrix

---



<blockquote>

<p>Given a 2D array of characters <code>grid</code> of size <code>m x n</code>, you need to find if there exists any cycle consisting of the <strong>same value</strong> in <code>grid</code>.</p>

<p>A cycle is a path of <strong>length 4 or more</strong> in the grid that starts and ends at the same cell. From a given cell, you can move to one of the cells adjacent to it - in one of the four directions (up, down, left, or right), if it has the <strong>same value</strong> of the current cell.</p>

<p>Also, you cannot move to the cell that you visited in your last move. For example, the cycle <code>(1, 1) -&gt; (1, 2) -&gt; (1, 1)</code> is invalid because from <code>(1, 2)</code> we visited <code>(1, 1)</code> which was the last visited cell.</p>

<p>Return <code>true</code> if any cycle of the same value exists in <code>grid</code>, otherwise, return <code>false</code>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<p><strong><img alt="" src="https://assets.leetcode.com/uploads/2020/07/15/1.png" style="width: 231px; height: 152px;" /></strong></p>

<pre>
<strong>Input:</strong> grid = [[&quot;a&quot;,&quot;a&quot;,&quot;a&quot;,&quot;a&quot;],[&quot;a&quot;,&quot;b&quot;,&quot;b&quot;,&quot;a&quot;],[&quot;a&quot;,&quot;b&quot;,&quot;b&quot;,&quot;a&quot;],[&quot;a&quot;,&quot;a&quot;,&quot;a&quot;,&quot;a&quot;]]
<strong>Output:</strong> true
<strong>Explanation: </strong>There are two valid cycles shown in different colors in the image below:
<img alt="" src="https://assets.leetcode.com/uploads/2020/07/15/11.png" style="width: 225px; height: 163px;" />
</pre>

<p><strong class="example">Example 2:</strong></p>

<p><strong><img alt="" src="https://assets.leetcode.com/uploads/2020/07/15/22.png" style="width: 236px; height: 154px;" /></strong></p>

<pre>
<strong>Input:</strong> grid = [[&quot;c&quot;,&quot;c&quot;,&quot;c&quot;,&quot;a&quot;],[&quot;c&quot;,&quot;d&quot;,&quot;c&quot;,&quot;c&quot;],[&quot;c&quot;,&quot;c&quot;,&quot;e&quot;,&quot;c&quot;],[&quot;f&quot;,&quot;c&quot;,&quot;c&quot;,&quot;c&quot;]]
<strong>Output:</strong> true
<strong>Explanation: </strong>There is only one valid cycle highlighted in the image below:
<img alt="" src="https://assets.leetcode.com/uploads/2020/07/15/2.png" style="width: 229px; height: 157px;" />
</pre>

<p><strong class="example">Example 3:</strong></p>

<p><strong><img alt="" src="https://assets.leetcode.com/uploads/2020/07/15/3.png" style="width: 183px; height: 120px;" /></strong></p>

<pre>
<strong>Input:</strong> grid = [[&quot;a&quot;,&quot;b&quot;,&quot;b&quot;],[&quot;b&quot;,&quot;z&quot;,&quot;b&quot;],[&quot;b&quot;,&quot;b&quot;,&quot;a&quot;]]
<strong>Output:</strong> false
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>m == grid.length</code></li>
	<li><code>n == grid[i].length</code></li>
	<li><code>1 &lt;= m, n &lt;= 500</code></li>
	<li><code>grid</code> consists only of lowercase English letters.</li>
</ul>

## Solution
```cpp
class DSU {
public:
    vector<int> id, sz;
    DSU(int n) : id(n), sz(n,1) {
        iota(id.begin(), id.end(), 0);
    }

    int find(int x) {
        return id[x] == x ? x : id[x] = find(id[x]);
    }

    // returns false if already connected
    bool join(int x, int y) {
        int a = find(x), b = find(y);
        if(a == b) return false;
        if(sz[a] < sz[b]) swap(a, b);
        id[b] = a;
        sz[a] += sz[b];
        return true; 
    }
};
class Solution {
public:
    bool containsCycle(vector<vector<char>>& grid) {
        int m = grid.size(), n = grid[0].size();
        DSU dsu(m*n);
        
        int dirs[2][2] = {{1,0}, {0,1}}; // only down and right

        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                int id = i * n + j;
                for(auto &d : dirs) {
                    int ni = i + d[0], nj = j + d[1];
                    if(ni < m && nj < n && grid[ni][nj] == grid[i][j]) {
                        int nid = ni * n + nj;
                        if(dsu.find(nid) == dsu.find(id)) return true;
                        dsu.join(id, nid);
                    }
                }
            }
        }

        return false;
    }
    bool containsCycleDFS(vector<vector<char>>& grid) {
        int m = grid.size(), n = grid[0].size();
        vector<vector<bool>> visited(m, vector<bool>(n, false));
        int dirs[] = {1, 0, -1, 0, 1};
        function<bool(int, int, int, int)> dfs = [&](int x, int y, int px, int py){
            visited[x][y] = true;
            for(int i=0; i<4; ++i) {
                int nx = x + dirs[i], ny = y + dirs[i+1];
                if(nx < 0 || nx >= m || ny < 0 || ny >= n) continue;    // going beyond grid
                if(grid[nx][ny] != grid[x][y]) continue;                // cant move forward coz its different char
                if(nx == px && ny == py) continue;                      // don't go back to parent
                if(visited[nx][ny]) return true;
                if(dfs(nx, ny, x, y)) return true;
            }
            return false;
        };

        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                if(!visited[i][j] && dfs(i,j,-1,-1)) return true;
            }
        }

        return false;
    }
};
```
