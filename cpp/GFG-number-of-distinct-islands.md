# [Number of Distinct Islands](https://www.geeksforgeeks.org/problems/number-of-distinct-islands/1)

<blockquote>

## Problem Statement

Given a boolean 2D matrix grid of size n * m . You have to find the number of distinct islands where a group of connected 1s (horizontally or vertically) forms an island. Two islands are considered to be distinct if and only if one island is not equal to another (not rotated or reflected).

Example 1:

```
Input:
grid[][] = [[1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1]]
Output: 1
Explanation:
grid[][] = [[1, 1, 0, 0, 0], 
            [1, 1, 0, 0, 0], 
            [0, 0, 0, 1, 1], 
            [0, 0, 0, 1, 1]]
Same colored islands are equal. We have 2 equal islands, so we have only 1 distinct island.
```

Example 2:

```
Input:
grid[][] = [[1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1]]
Output: 3
Explanation:
grid[][] = [[1, 1, 0, 1, 1], 
            [1, 0, 0, 0, 0], 
            [0, 0, 0, 0, 1], 
            [1, 1, 0, 1, 1]]
Same colored islands are equal.
We have 4 islands, but 2 of them
are equal, So we have 3 distinct islands.
```

Your Task: You don't need to read or print anything. Your task is to complete the function countDistinctIslands() which takes the grid as an input parameter and returns the total number of distinct islands.

Constraints: 1 ≤ n, m ≤ 500 grid[i][j] == 0 or grid[i][j] == 1

## Input Format

First line should contain n and m .

Following n lines should contain m space-separated integers(either 1 or 0), denoting the 2D array elements.

Sample Input:
4&!//!&5&!//!&1 1 0 0 0 
1 1 0 0 0
0 0 0 1 1
0 0 0 1 1

## Examples

```
Input:
grid[][] = [[1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1]]
Output: 1
Explanation:
grid[][] = [[1, 1, 0, 0, 0], 
            [1, 1, 0, 0, 0], 
            [0, 0, 0, 1, 1], 
            [0, 0, 0, 1, 1]]
Same colored islands are equal. We have 2 equal islands, so we have only 1 distinct island.



Input:
grid[][] = [[1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1]]
Output: 3
Explanation:
grid[][] = [[1, 1, 0, 1, 1], 
            [1, 0, 0, 0, 0], 
            [0, 0, 0, 0, 1], 
            [1, 1, 0, 1, 1]]
Same colored islands are equal.
We have 4 islands, but 2 of them
are equal, So we have 3 distinct islands.


```

## Constraints

Constraints:

**Tags:** DFS, Graph, BFS, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/find-the-number-of-distinct-islands-in-a-2d-matrix/


</blockquote>


## Solution
```cpp
class Solution {
  private:
    void dfs(int r, int c, vector<vector<int>> &grid, vector<vector<int>> &vis, 
                vector<pair<int,int>> &nodes, int initRow, int initCol) {
        vis[r][c] = 1;
        nodes.push_back({r-initRow, c-initCol});
        int delRow[4] = {-1, 0, 1, 0};
        int delCol[4] = {0, 1, 0, -1};
        int m = grid.size(), n = grid[0].size();
        for(int i=0; i<4; ++i) {
            int row = r + delRow[i];
            int col = c + delCol[i];
            if(row >= 0 && row < m && col >= 0 && col < n
                    && grid[row][col] && !vis[row][col]) {
                dfs(row, col, grid, vis, nodes, initRow, initCol);
            }
        }
    }
  public:
    int countDistinctIslands(vector<vector<int>>& grid) {
        int m = grid.size();
        int n = grid[0].size();
        vector<vector<int>> vis(m, vector<int>(n,0));
        set<vector<pair<int,int>>> s;
        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                if(!vis[i][j] && grid[i][j]) {
                    vector<pair<int,int>> nodes;
                    dfs(i, j, grid, vis, nodes, i, j);
                    s.insert(nodes);
                }
            }
        }
        
        return s.size();
    }
};
```
