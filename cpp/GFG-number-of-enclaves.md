# [Number Of Enclaves](https://www.geeksforgeeks.org/problems/number-of-enclaves/1)

<blockquote>

## Problem Statement

You are given an n x m binary matrix grid , where 0 represents a sea cell and 1 represents a land cell.

A move consists of walking from one land cell to another adjacent (4-directionally) land cell or walking off the boundary of the grid.

Find the number of land cells in grid for which we cannot walk off the boundary of the grid in any number of moves.

Example 1:

```
Input:
grid[][] = {{0, 0, 0, 0},
            {1, 0, 1, 0},
            {0, 1, 1, 0},
            {0, 0, 0, 0}}
Output:
3
Explanation:
0 0 0 0
1 0 1 0
0 1 1 0
0 0 0 0
The highlighted cells represents the land cells.
```

Example 2:

```
Input:
grid[][] = {{0, 0, 0, 1},
            {0, 1, 1, 0},
            {0, 1, 1, 0},
            {0, 0, 0, 1},
            {0, 1, 1, 0}}
Output:
4
Explanation:
0 0 0 1
0 1 1 0
0 1 1 0
0 0 0 1
0 1 1 0
The highlighted cells represents the land cells.
```

Your Task:

You don't need to print or input anything. Complete the function numberOfEnclaves() which takes a 2D integer matrix grid as the input parameter and returns an integer, denoting the number of land cells.

Expected Time Complexity: O(n * m)

Expected Space Complexity: O(n * m)

Constraints:

1 <= n, m <= 500 grid[i][j] == 0 or 1

## Input Format

The first line should contain two space-separated integers, denoting the values of n and m , respectively.

The following n lines should contain m space-separated integers(either 0 or 1), denoting the array elements.

Example:

```
4 4
0 0 0 0
1 0 1 0
0 1 1 0
0 0 0 0
```

Sample Input:
4 4

0 0 0 0

1 0 1 0

0 1 1 0

0 0 0 0

## Examples

```
Input:
grid[][] = {{0, 0, 0, 0},
            {1, 0, 1, 0},
            {0, 1, 1, 0},
            {0, 0, 0, 0}}
Output:
3
Explanation:
0 0 0 0
1 0 1 0
0 1 1 0
0 0 0 0
The highlighted cells represents the land cells.


Input:
grid[][] = {{0, 0, 0, 1},
            {0, 1, 1, 0},
            {0, 1, 1, 0},
            {0, 0, 0, 1},
            {0, 1, 1, 0}}
Output:
4
Explanation:
0 0 0 1
0 1 1 0
0 1 1 0
0 0 0 1
0 1 1 0
The highlighted cells represents the land cells.
```

## Constraints

Constraints:

**Tags:** DFS, Matrix, Graph, BFS, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/number-of-land-cells-for-which-we-cannot-walk-off-the-boundary-of-grid/


</blockquote>

## Solution
```cpp
class Solution {
  int dr[4] = {-1, 0, 1, 0};
  int dc[4] = {0, 1, 0, -1};
  void dfs(int r, int c, vector<vector<int>> &vis,
            vector<vector<int>> &grid) {
            vis[r][c] = 1;
            int m = grid.size(), n = grid[0].size();
            for(int i=0; i<4; ++i) {
                int nr = r + dr[i];
                int nc = c + dc[i];
                if(nr >= 0 && nr < m && nc >= 0 && nc < n
                    && !vis[nr][nc] && grid[nr][nc] == 1) {
                    dfs(nr, nc, vis, grid);
                }
            }
        }
  public:
    int numberOfEnclaves(vector<vector<int>> &grid) {
        // Code here
        int m = grid.size(); 
        int n = grid[0].size();
        vector<vector<int>> vis(m, vector<int>(n, 0));
        
        for(int i=0; i<m; ++i) {
            if(!vis[i][0] && grid[i][0] == 1)
                dfs(i, 0, vis, grid);
            if(!vis[i][n-1] && grid[i][n-1] == 1)
                dfs(i, n-1, vis, grid);
        }
        
        for(int j=0; j<n; ++j) {
            if(!vis[0][j] && grid[0][j] == 1)
                dfs(0, j, vis, grid);
            if(!vis[m-1][j] && grid[m-1][j] == 1)
                dfs(m-1, j, vis, grid);
        }
        
        int ans = 0;
        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                ans += (!vis[i][j] && grid[i][j]);
            }
        }
        return ans;
    }
};
```
