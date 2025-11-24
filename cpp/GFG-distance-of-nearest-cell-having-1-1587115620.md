# [Distance of nearest cell having 1](https://www.geeksforgeeks.org/problems/distance-of-nearest-cell-having-1-1587115620/1)

<blockquote>

## Problem Statement

Given a binary grid[][], where each cell contains either 0 or 1, find the distance of the nearest 1 for every cell in the grid. The distance between two cells (i 1 , j 1 )  and (i 2 , j 2 ) is calculated as |i 1 - i 2 | + |j 1 - j 2 | . You need to return a matrix of the same size, where each cell (i, j) contains the minimum distance from grid[i][j] to the nearest cell having value 1.

Note: It is guaranteed that there is at least one cell with value 1 in the grid.

Examples

Input: grid[][] = [[0, 1, 1, 0],                 [1, 1, 0, 0],                 [0, 0, 1, 1]]
Output: [[1, 0, 0, 1],         [0, 0, 1, 1],         [1, 1, 0, 0]]
Explanation: The grid is -![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/913655/Web/Other/blobid0_1761546366.webp)
- 0's at (0,0), (0,3), (1,2), (1,3), (2,0) and (2,1) are at a distance of 1 from 1's at (0,1), (0,2), (0,2), (2,3), (1,0) and (1,1) respectively.
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/701275/Web/Other/blobid0_1745302650.jpg)

Input: grid[][] = [[1, 0, 1],                 [1, 1, 0],                 [1, 0, 0]]
Output: [[0, 1, 0],         [0, 0, 1],         [0, 1, 2]]
Explanation: The grid is -![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/913655/Web/Other/blobid1_1761546409.webp)
- 0's at (0,1), (1,2), (2,1) and (2,2) are at a  distance of 1, 1, 1 and 2 from 1's at (0,0), (0,2), (2,0) and (1,1) respectively.
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/701275/Web/Other/blobid1_1745302675.jpg)

Constraints: 1 ≤ grid.size() ≤ 200 1 ≤ grid[0].size() ≤ 200

## Input Format

First line should contain n and m separated by space. Each of next n lines should contain m integers.(either 0 or 1). Example:

```
3 4 
0 1 1 0 
1 1 0 0 
0 0 1 1
```

Sample Input:
3&!//!&4&!//!&0 1 1 0
1 1 0 0
0 0 1 1

## Examples

```
Input: grid[][] = [[0, 1, 1, 0],                 [1, 1, 0, 0],                 [0, 0, 1, 1]]
Output: [[1, 0, 0, 1],         [0, 0, 1, 1],         [1, 1, 0, 0]]
Explanation: The grid is -
- 0's at (0,0), (0,3), (1,2), (1,3), (2,0) and (2,1) are at a distance of 1 from 1's at (0,1), (0,2), (0,2), (2,3), (1,0) and (1,1) respectively.


Input: grid[][] = [[1, 0, 1],                 [1, 1, 0],                 [1, 0, 0]]
Output: [[0, 1, 0],         [0, 0, 1],         [0, 1, 2]]
Explanation: The grid is -
- 0's at (0,1), (1,2), (2,1) and (2,2) are at a  distance of 1, 1, 1 and 2 from 1's at (0,0), (0,2), (2,0) and (1,1) respectively.

```

## Constraints

Constraints:

**Tags:** Matrix, Graph, BFS, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/distance-nearest-cell-1-binary-matrix/


</blockquote>

## Solution
```cpp
class Solution {
  public:
    vector<vector<int>> nearest(vector<vector<int>>& grid) {
        // code here
        int m = grid.size();
        int n = grid[0].size();
        vector<vector<int>> ans(m, vector<int>(n, INT_MAX));
        vector<vector<int>> vis(m, vector<int>(n, 0));
        queue<tuple<int,int,int>> q;
        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                if(grid[i][j] == 1) {
                    vis[i][j] = 1;
                    // ans[i][j] = 0;
                    q.push({i, j, 0});
                }
            }
        }
        
        int dx[] = {-1, 0, 1, 0};
        int dy[] = {0, 1, 0, -1};
        while(!q.empty()) {
            auto [r, c, d] = q.front();
            q.pop();
            // ans[r][c] = min(ans[r][c], d);
			ans[r][c] = d;
            
            for(int i=0; i<4; ++i) {
                int nr = r + dx[i];
                int nc = c + dy[i];
                if(nr >= 0 && nr < m && nc >= 0 && nc < n
                    && !vis[nr][nc]) {
                    vis[nr][nc] = 1;
                    q.push({nr, nc, d+1});
                }
            }
        }
        
        return ans;
    }
};
```
