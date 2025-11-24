# [Flood fill Algorithm](https://www.geeksforgeeks.org/problems/flood-fill-algorithm1856/1)

<blockquote>

## Problem Statement

You are given a 2D grid image[][] , where each image[i][j] represents the color of a pixel in the image. Also provided a coordinate (sr, sc) representing the starting pixel (row and column) and a new color value newColor .

Your task is to perform a flood fill starting from the pixel (sr, sc) , changing its color to newColor and the color of all the connected pixels that have the same original color . Two pixels are considered connected if they are adjacent horizontally or vertically (not diagonally) and have the same original color.

Examples:

Input: image[][] = [[1, 1, 1, 0], [0, 1, 1, 1], [1, 0, 1, 1]], sr = 1, sc = 2, newColor = 2![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/705720/Web/Other/blobid0_1744378665.jpg)Output: [[2, 2, 2, 0], [0, 2, 2, 2], [1, 0, 2, 2]]![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/705720/Web/Other/blobid1_1744378699.jpg)Explanation: Starting from pixel (1, 2) with value 1, flood fill updates all connected pixels (up, down, left, right) with value 1 to 2, resulting in [[2, 2, 2, 0], [0, 2, 2, 2], [1, 0, 2, 2]].

```
Input: image[][] = [[0, 1, 0], [0, 1, 0]], sr = 0, sc = 1, newColor = 0
Output: [[0, 0, 0], [0, 0, 0]]
Explanation: Starting from pixel (0, 1) with value 1, flood fill changes all 4-directionally connected pixels with value 1 to 0, resulting in [[0, 0, 0], [0, 0, 0]]
```

Constraints: 1 ≤ n ≤ m ≤ 500 0 ≤ image[i][j] ≤ 10

0 ≤ newColor ≤ 10

0 ≤ sr ≤ (n-1)

0 ≤ sc ≤ (m-1)

## Input Format

Custom input should contain n+2 lines. The first line should contain n and m. Each of the next n lines should contain m elements. The next lines should contain sr, sc, and newColor.

Example:

```
3 3
1 1 1
1 1 0
1 0 1
1 1 2
```

Sample Input:
3&!//!&4&!//!&1 1 1 0
0 1 1 1
1 0 1 1&!//!&1&!//!&2&!//!&2

## Examples

```
Input: image[][] = [[1, 1, 1, 0], [0, 1, 1, 1], [1, 0, 1, 1]], sr = 1, sc = 2, newColor = 2Output: [[2, 2, 2, 0], [0, 2, 2, 2], [1, 0, 2, 2]]Explanation: Starting from pixel (1, 2) with value 1, flood fill updates all connected pixels (up, down, left, right) with value 1 to 2, resulting in [[2, 2, 2, 0], [0, 2, 2, 2], [1, 0, 2, 2]].

Input: image[][] = [[0, 1, 0], [0, 1, 0]], sr = 0, sc = 1, newColor = 0
Output: [[0, 0, 0], [0, 0, 0]]
Explanation: Starting from pixel (0, 1) with value 1, flood fill changes all 4-directionally connected pixels with value 1 to 0, resulting in [[0, 0, 0], [0, 0, 0]]
```

## Constraints

Constraints:

**Tags:** Recursion, DFS, Matrix, Graph, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/flood-fill-algorithm-implement-fill-paint/

- https://www.geeksforgeeks.org/flood-fill-algorithm/


</blockquote>

## Solution
```cpp
class Solution {
    const int d[5] = {1,0,-1,0,1};
  void dfs(int r, int c, int m, int n, vector<vector<int>> &image, 
            vector<vector<int>> &ans, int origColor, int newColor) {
      ans[r][c] = newColor;
      
      for(int del=0; del<4; ++del) {
        int nr = r + d[del];
        int nc = c + d[del+1];
        
        if(nr >=0 && nr < m && nc >= 0 && nc < n
            && image[nr][nc] == origColor && ans[nr][nc] != newColor) {
            dfs(nr, nc, m, n, image, ans, origColor, newColor);
        }
      }
  }
  public:
    vector<vector<int>> floodFill(vector<vector<int>>& image, int sr, int sc,
                                  int newColor) {
        // code here
        int origColor = image[sr][sc];
        vector<vector<int>> ans = image;
        int m = image.size();
        int n = image[0].size();
        dfs(sr, sc, m, n, image, ans, origColor, newColor);
        return ans;
    }
};
```
