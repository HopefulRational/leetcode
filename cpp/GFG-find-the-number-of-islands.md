# [Find the number of islands](https://www.geeksforgeeks.org/problems/find-the-number-of-islands/1)

<blockquote>

## Problem Statement

Given a grid of size n*m (n is the number of rows and m is the number of columns in the grid) consisting of 'W' s (Water) and 'L' s (Land). Find the number of islands . Note: An island is either surrounded by water or the boundary of a grid and is formed by connecting adjacent lands horizontally or vertically or diagonally i.e., in all 8 directions.

Examples:

Input: grid[][] = [['L', 'L', 'W', 'W', 'W'],                 ['W', 'L', 'W', 'W', 'L'],                 ['L', 'W', 'W', 'L', 'L'],                 ['W', 'W', 'W', 'W', 'W'],                 ['L', 'W', 'L', 'L', 'W']]
Output: 4
Explanation:
The image below shows all the 4 islands in the grid.![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/891756/Web/Other/blobid1_1743509451.jpg)

Input: grid[][] = [['W', 'L', 'L', 'L', 'W', 'W', 'W'],                 ['W', 'W', 'L', 'L', 'W', 'L', 'W']]
Output: 2
Expanation:
The image below shows 2 islands in the grid.![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/891756/Web/Other/blobid2_1743509488.jpg)

Constraints: 1 ≤ n, m ≤ 500 grid[i][j] = {'L' , 'W'}

## Input Format

The first two line should contain n and m. Each of the next n lines should contain m space-separated integers(either 1 or 0).

Example:

```
4 2
W L
L W
L L
L W
```

Sample Input:
4&!//!&2&!//!&W L
L W
L L
L W

## Examples

```
Input: grid[][] = [['L', 'L', 'W', 'W', 'W'],                 ['W', 'L', 'W', 'W', 'L'],                 ['L', 'W', 'W', 'L', 'L'],                 ['W', 'W', 'W', 'W', 'W'],                 ['L', 'W', 'L', 'L', 'W']]
Output: 4
Explanation:
The image below shows all the 4 islands in the grid. 

Input: grid[][] = [['W', 'L', 'L', 'L', 'W', 'W', 'W'],                 ['W', 'W', 'L', 'L', 'W', 'L', 'W']]
Output: 2
Expanation:
The image below shows 2 islands in the grid. 
```

## Constraints

Constraints:

**Tags:** DFS, Graph, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/find-the-number-of-islands-using-dfs/


</blockquote>

## Solution
```cpp
class Solution {
  private:
    void dfs(int r, int c, vector<vector<char>> &grid, 
                vector<vector<int>> &vis) {
        vis[r][c] = 1;
        int m = grid.size();
        int n = grid[0].size();
        
        for(int dr=-1; dr<=1; ++dr) {
            for(int dc=-1; dc <=1; ++dc) {
                int nr = r + dr;
                int nc = c + dc;
                if(nr >=0 && nr < m && nc >= 0 && nc < n
                    && grid[nr][nc] == 'L' && !vis[nr][nc]) {
                    dfs(nr, nc, grid, vis);
                }
            }
        }
    }
    void bfs(int r, int c, vector<vector<char>> &grid, 
            vector<vector<int>> &vis) {
        queue<pair<int,int>> q;
        vis[r][c] = 1;
        int m = grid.size();
        int n = grid[0].size();
        q.push({r,c});
        while(!q.empty()) {
            int row = q.front().first;
            int col = q.front().second;
            q.pop();
            
            for(int dr=-1; dr<=1; ++dr) {
                for(int dc=-1; dc<=1; ++dc) {
                    int nrow = row + dr;
                    int ncol = col + dc;
                    if(nrow >=0 && nrow < m && ncol >= 0 && ncol < n
                        && grid[nrow][ncol] == 'L' && !vis[nrow][ncol]) {
                            vis[nrow][ncol] = 1;
                            q.push({nrow, ncol});
                    }
                }
            }
        }
    }
  public:
    int countIslands(vector<vector<char>>& grid) {
        // Code here
        int m = grid.size();
        int n = grid[0].size();
        
        vector<vector<int>> vis(m, vector<int>(n, 0));
        int ans = 0;
        
        for(int row=0; row<m; ++row) {
            for(int col=0; col<n; ++col) {
                if(!vis[row][col] && grid[row][col] == 'L') {
                    // dfs(row, col, grid, vis);
                    bfs(row, col, grid, vis);
                    ++ans;
                }
            }
        }
        
        return ans;
    }
};
```
