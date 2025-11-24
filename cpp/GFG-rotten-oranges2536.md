# [Rotten Oranges](https://www.geeksforgeeks.org/problems/rotten-oranges2536/1)

<blockquote>

## Problem Statement

Given a matrix mat[][] , where each cell in the matrix can have values 0, 1 or 2 which has the following meaning: 0 : Empty cell 1 : Cell have fresh oranges 2 : Cell have rotten oranges

Your task is to determine t he minimum time required so that all the oranges become rotten. A rotten orange at index (i, j) can rot other fresh orange at indexes (i-1, j), (i+1, j), (i, j-1), (i, j+1) ( up , down , left and right ) in a unit time.

Note : If it is impossible to rot every orange then simply return -1.

Examples:

```
Input: mat[][] = [[2, 1, 0, 2, 1], [1, 0, 1, 2, 1], [1, 0, 0, 2, 1]]
Output: 2
Explanation: Oranges at positions (0,0), (0,3), (1,3), and (2,3) will rot adjacent fresh oranges in successive time frames.All fresh oranges become rotten after 2 units of time.
```

```
Input: mat[][] = [[2, 1, 0, 2, 1], [0, 0, 1, 2, 1], [1, 0, 0, 2, 1]]
Output: -1
Explanation: Oranges at positions (0,0), (0,3), (1,3), and (2,3) rot some fresh oranges,but the fresh orange at (2,0) can never be reached, so not all oranges can rot.
```

Constraints: 1 ≤ mat.size() ≤ 500 1 ≤ mat[0].size() ≤ 500 mat[i][j] = {0, 1, 2}

## Input Format

First line of the input should contain n and m separated by space. Each of next n lines should contain m space separated integers, Example:

```
33
0 1 2 
0 1 2 
2 1 1
```

Sample Input:
3&!//!&3&!//!&0 1 2 
0 1 2 
2 1 1

## Examples

```
Input: mat[][] = [[2, 1, 0, 2, 1], [1, 0, 1, 2, 1], [1, 0, 0, 2, 1]]
Output: 2
Explanation: Oranges at positions (0,0), (0,3), (1,3), and (2,3) will rot adjacent fresh oranges in successive time frames.All fresh oranges become rotten after 2 units of time.

Input: mat[][] = [[2, 1, 0, 2, 1], [0, 0, 1, 2, 1], [1, 0, 0, 2, 1]]
Output: -1
Explanation: Oranges at positions (0,0), (0,3), (1,3), and (2,3) rot some fresh oranges,but the fresh orange at (2,0) can never be reached, so not all oranges can rot.

```

## Constraints

Constraints:

**Tags:** Matrix, Graph, Data Structures, Queue

**Article / Editorial:**

- https://www.geeksforgeeks.org/minimum-time-required-so-that-all-oranges-become-rotten/


</blockquote>

## Solution
```cpp
class Solution {
  public:
    int orangesRot(vector<vector<int>>& mat) {
        // code here
        int m = mat.size();
        int n = mat[0].size();
        int fresh=0;
        
        vector<vector<int>> vis(m, vector<int>(n));
        queue<tuple<int, int, int>> q; 
        
        for(int i=0; i<m; ++i) {
            for(int j=0; j<n; ++j) {
                if(mat[i][j] == 2) {
                    vis[i][j] = 2;
                    q.push({i,j,0});
                }
                else if(mat[i][j] == 1) {
                    vis[i][j] = 0;
                    ++fresh;
                }
            }
        }
        
        int dr[] = {-1, 0, 1, 0};
        int dc[] = {0, 1, 0, -1};
        int tm = 0;
        while(!q.empty()) {
            auto [r, c, t] = q.front();
            q.pop();
            tm = max(tm, t);
            
            for(int i=0; i<4; ++i) {
                int nr = r + dr[i];
                int nc = c + dc[i];
                
                if(nr >=0 && nr < m && nc >= 0 && nc < n
                    && vis[nr][nc] != 2 && mat[nr][nc] == 1) {
                    vis[nr][nc] = 2;
                    q.push({nr, nc, t+1});
                    --fresh;
                }
            }
            
        }
        return fresh == 0 ? tm : -1;
    }
};
```
