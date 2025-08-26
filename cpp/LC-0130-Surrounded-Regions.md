# [130. Surrounded Regions](https://leetcode.com/problems/surrounded-regions/)

**Difficulty:** Medium

**Topics:** Array, Depth-First Search, Breadth-First Search, Union Find, Matrix

---



<blockquote>

<p>You are given an <code>m x n</code> matrix <code>board</code> containing <strong>letters</strong> <code>&#39;X&#39;</code> and <code>&#39;O&#39;</code>, <strong>capture regions</strong> that are <strong>surrounded</strong>:</p>

<ul>
	<li><strong>Connect</strong>: A cell is connected to adjacent cells horizontally or vertically.</li>
	<li><strong>Region</strong>: To form a region <strong>connect every</strong> <code>&#39;O&#39;</code> cell.</li>
	<li><strong>Surround</strong>: The region is surrounded with <code>&#39;X&#39;</code> cells if you can <strong>connect the region </strong>with <code>&#39;X&#39;</code> cells and none of the region cells are on the edge of the <code>board</code>.</li>
</ul>

<p>To capture a <strong>surrounded region</strong>, replace all <code>&#39;O&#39;</code>s with <code>&#39;X&#39;</code>s <strong>in-place</strong> within the original board. You do not need to return anything.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<div class="example-block">
<p><strong>Input:</strong> <span class="example-io">board = [[&quot;X&quot;,&quot;X&quot;,&quot;X&quot;,&quot;X&quot;],[&quot;X&quot;,&quot;O&quot;,&quot;O&quot;,&quot;X&quot;],[&quot;X&quot;,&quot;X&quot;,&quot;O&quot;,&quot;X&quot;],[&quot;X&quot;,&quot;O&quot;,&quot;X&quot;,&quot;X&quot;]]</span></p>

<p><strong>Output:</strong> <span class="example-io">[[&quot;X&quot;,&quot;X&quot;,&quot;X&quot;,&quot;X&quot;],[&quot;X&quot;,&quot;X&quot;,&quot;X&quot;,&quot;X&quot;],[&quot;X&quot;,&quot;X&quot;,&quot;X&quot;,&quot;X&quot;],[&quot;X&quot;,&quot;O&quot;,&quot;X&quot;,&quot;X&quot;]]</span></p>

<p><strong>Explanation:</strong></p>
<img alt="" src="https://assets.leetcode.com/uploads/2021/02/19/xogrid.jpg" style="width: 367px; height: 158px;" />
<p>In the above diagram, the bottom region is not captured because it is on the edge of the board and cannot be surrounded.</p>
</div>

<p><strong class="example">Example 2:</strong></p>

<div class="example-block">
<p><strong>Input:</strong> <span class="example-io">board = [[&quot;X&quot;]]</span></p>

<p><strong>Output:</strong> <span class="example-io">[[&quot;X&quot;]]</span></p>
</div>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>m == board.length</code></li>
	<li><code>n == board[i].length</code></li>
	<li><code>1 &lt;= m, n &lt;= 200</code></li>
	<li><code>board[i][j]</code> is <code>&#39;X&#39;</code> or <code>&#39;O&#39;</code>.</li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    void solve(vector<vector<char>>& board) {
        int m = board.size(), n = board[0].size();
        function<void(int, int)> dfs = [&](int x, int y) {
            if(x < 0 || x >= m || y < 0 || y >= n || board[x][y] != 'O')
                return;
            board[x][y] = 'T';
            dfs(x-1,y);
            dfs(x+1,y);
            dfs(x,y-1);
            dfs(x,y+1);
        };

        for(int i=0; i<m; ++i) {
            if(board[i][0] == 'O') dfs(i,0);
            if(board[i][n-1] == 'O') dfs(i,n-1);
        }
        
        for(int j=0; j<n; ++j) {
            if(board[0][j] == 'O') dfs(0, j);
            if(board[m-1][j] == 'O') dfs(m-1, j);
        }
        
        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                if(board[i][j] == 'O')      board[i][j] = 'X';
                else if(board[i][j] == 'T') board[i][j] = 'O';
            }
        }
        
    }
};
```


