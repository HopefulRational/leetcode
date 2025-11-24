# [Replace O's with X's](https://www.geeksforgeeks.org/problems/replace-os-with-xs0052/1)

<blockquote>

## Problem Statement

You are given a grid[][] of size n*m, where every element is either 'O' or 'X'. You have to replace all 'O' or a group of 'O' with 'X' that are surrounded by 'X'.

A 'O' (or a set of 'O') is considered to be surrounded by 'X' if there are 'X' at locations just below, just above, just left and just right of it.

Examples:

```
Input: grid[][] = [['X', 'X', 'X', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'O', 'O', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'X', 'O', 'O']]
Output: [['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'O', 'O']]
Explanation: We only changed those 'O' that are surrounded by 'X'
```

```
Input: grid[][] = [['X', 'O', 'X', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'O', 'O', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'X', 'O', 'O']]
Output: [['X', 'O', 'X', 'X'], ['X', 'O', 'X', 'X'], ['X', 'O', 'O', 'X'], ['X', 'O', 'X', 'X'], ['X', 'X', 'O', 'O']]
Explanation: There's no 'O' that's surround by 'X'.
```

```
Input: grid[][] = [['X', 'X', 'X'],           ['X', 'O', 'X'],           ['X', 'X', 'X']]
Output: [['X', 'X', 'X'], ['X', 'X', 'X'], ['X', 'X', 'X']]
Explanation: There's only one 'O' that's surround by 'X'.
```

Constraints: 1 ≤ grid.size() ≤ 100 1 ≤ grid[0].size() ≤ 100

## Input Format

The custom input should contain N+1 lines. The first line contains N and M. Next N lines contains M space separated characters each.

Example:

```
4 5
X X X X X
O X X X O
O X X O X
X X X O O
```

Sample Input:
5&!//!&4&!//!&X X X X
X O X X
X O O X
X O X X
X X O O

## Examples

```
Input: grid[][] = [['X', 'X', 'X', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'O', 'O', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'X', 'O', 'O']]
Output: [['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'O', 'O']]
Explanation: We only changed those 'O' that are surrounded by 'X'


Input: grid[][] = [['X', 'O', 'X', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'O', 'O', 'X'],           ['X', 'O', 'X', 'X'],           ['X', 'X', 'O', 'O']]
Output: [['X', 'O', 'X', 'X'], ['X', 'O', 'X', 'X'], ['X', 'O', 'O', 'X'], ['X', 'O', 'X', 'X'], ['X', 'X', 'O', 'O']]
Explanation: There's no 'O' that's surround by 'X'.

Input: grid[][] = [['X', 'X', 'X'],           ['X', 'O', 'X'],           ['X', 'X', 'X']]
Output: [['X', 'X', 'X'], ['X', 'X', 'X'], ['X', 'X', 'X']]
Explanation: There's only one 'O' that's surround by 'X'.
```

## Constraints

Constraints:

**Tags:** Recursion, Matrix, Graph, Data Structures, Algorithms, BFS

**Article / Editorial:**

- https://www.geeksforgeeks.org/given-matrix-o-x-replace-o-x-surrounded-x/


</blockquote>

## Solution
```cpp
class Solution {
  private:
    int dx[4] = {-1, 0, 1, 0};
    int dy[4] = {0, 1, 0, -1};
    void dfs(int r, int c, vector<vector<char>> &grid, char orig, char target) {
        grid[r][c] = target;
        int m = grid.size(), n = grid[0].size();
        for(int i=0; i<4; ++i) {
            int nr = r + dx[i];
            int nc = c + dy[i];
            if(nr >=0 && nr < m && nc >= 0 && nc < n
                && grid[nr][nc] == orig) {
                dfs(nr, nc, grid, orig, target);
            }
        }
    }
  public:
    void fill(vector<vector<char>>& grid) {
        // Code here
        /*
            1. change boundary O to T
            2. change remaining O to X
            3. change T to O
        */
        
        int m = grid.size(), n = grid[0].size();
        for(int i=0; i<m; ++i) {
            if(grid[i][0] == 'O') {
                dfs(i, 0, grid, 'O', 'T');
            }
            if(grid[i][n-1] == 'O') {
                dfs(i, n-1, grid, 'O', 'T');
            }
        }
        
        for(int j=0; j<n; ++j) {
            if(grid[0][j] == 'O') {
                dfs(0, j, grid, 'O', 'T');
            }
            if(grid[m-1][j] == 'O') {
                dfs(m-1, j, grid, 'O', 'T');
            }
        }
        
        for(int i=1; i<m-1; ++i) {
            for(int j=1; j<n-1; ++j) {
                if(grid[i][j] == 'O') {
                    dfs(i, j, grid, 'O', 'X');
                }
            }
        }
        
        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                if(grid[i][j] == 'T')
                    grid[i][j] = 'O';
            }
        }
    }
};
```
