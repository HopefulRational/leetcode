# [Maximum path sum in matrix](https://www.geeksforgeeks.org/problems/path-in-matrix3805/1)

<blockquote>

## Problem Statement

You are given a matrix mat[][] of size n x m where each element is a positive integer. Starting from any cell in the first row, you are allowed to move to the next row, but with specific movement constraints. From any cell (r, c) in the current row, you can move to any of the three possible positions :

(r+1, c-1) — move diagonally to the left. (r+1, c) — move directly down. (r+1, c+1) — move diagonally to the right.

Find the maximum sum of any path starting from any column in the first row and ending at any column in the last row, following the above movement constraints.

Examples :

```
Input: mat[][] = [[3, 6, 1], [2, 3, 4], [5, 5, 1]]
Output: 15
Explaination: The best path is (0, 1) -> (1, 2) -> (2, 1). It gives the maximum sum as 15.
```

```
Input: mat[][] = [[2, 1, 1], [1, 2, 2]]
Output: 4
Explaination: The best path is (0, 0) -> (1, 1). It gives the maximum sum as 4.
```

```
Input: mat[][] = [[25]]
Output: 25
Explaination: (0, 0) is the only cell in mat[][], so maximum path sum will be 25.
```

Constraints: 1 ≤ mat.size() ≤ 500 1 ≤ mat[i].size() ≤ 500 1 ≤ mat[i][j] ≤ 1000

## Input Format

The custom input should contain two lines.

The first line contains the value of n.

The second line contains the matrix elements in row major order.

Example:

```
2
348 391 618 193
```

Sample Input:
3&!//!&3&!//!&3 6 1
2 3 4
5 5 1

## Examples

```
Input: mat[][] = [[3, 6, 1], [2, 3, 4], [5, 5, 1]]
Output: 15
Explaination: The best path is (0, 1) -> (1, 2) -> (2, 1). It gives the maximum sum as 15.

Input: mat[][] = [[2, 1, 1], [1, 2, 2]]
Output: 4
Explaination: The best path is (0, 0) -> (1, 1). It gives the maximum sum as 4.

Input: mat[][] = [[25]]
Output: 25
Explaination: (0, 0) is the only cell in mat[][], so maximum path sum will be 25.
```

## Constraints

You are given a matrix mat[][] of size n x m where each element is a positive integer. Starting from any cell in the first row, you are allowed to move to the next row, but with specific movement constraints. From any cell (r, c) in the current row, you can move to any of the three possible positions :

Find the maximum sum of any path starting from any column in the first row and ending at any column in the last row, following the above movement constraints.

Constraints:

**Tags:** Dynamic Programming, Matrix, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/find-the-longest-path-in-a-matrix-with-given-constraints/

- https://www.geeksforgeeks.org/maximum-path-sum-matrix/


</blockquote>

## Solution
```cpp
class Solution {
  public:
    int maximumPath(vector<vector<int>>& mat) {
        int m = mat.size(), n = mat[0].size();
        
        vector<int> prev(n, 0);
        for(int i=0; i<=m-1; ++i) {
            vector<int> tmp(n, 0);
            for(int j=0; j<=n-1; ++j) {
                if(i == 0) tmp[j] = mat[i][j];
                else {
                    int up = mat[i][j], upLeft = mat[i][j], upRight = mat[i][j];
                    up += prev[j];
                    if(j>0) upLeft = mat[i][j] + prev[j-1];
                    if(j<n-1) upRight = mat[i][j] + prev[j+1];
                    tmp[j] = max(up, max(upLeft, upRight));
                }
            }
            swap(prev, tmp);
        }
        int maxi = prev[0];
        for(auto &x : prev) maxi = max(maxi, x);
        return maxi;
        
        // vector<vector<int>> dp(m, vector<int>(n, 0));
        // for(int i=0; i<=m-1; ++i) {
        //     for(int j=0; j<=n-1; ++j) {
        //         if(i == 0) dp[i][j] = mat[i][j];
        //         else {
        //             int up = mat[i][j], upLeft = mat[i][j], upRight = mat[i][j];
        //             up += dp[i-1][j];
        //             if(j>0) upLeft = mat[i][j] + dp[i-1][j-1];
        //             if(j<n-1) upRight = mat[i][j] + dp[i-1][j+1];
        //             dp[i][j] = max(up, max(upLeft, upRight));
        //         }
        //     }
        // }
        // int maxi = dp[m-1][0];
        // for(auto &x : dp[m-1]) maxi = max(maxi, x);
        // return maxi;
        
        // int ans = -1;
        // vector<vector<int>> dp(m, vector<int>(n, -1));
        // for(int j=0; j<n; ++j) {
        //     ans = max(ans, f(m-1, j, mat, n, dp));
        // }
        // return ans;
    }
    
    int f(int i, int j, vector<vector<int>>& mat, int n, vector<vector<int>>& dp) {
        if(j < 0 || j > n-1) return -1e6;
        if(i == 0) return mat[i][j];
        if(dp[i][j] != -1) return dp[i][j];
        int up = mat[i][j] + f(i-1, j, mat, n, dp);
        int upLeft = mat[i][j] + f(i-1, j-1, mat, n, dp);
        int upRight = mat[i][j] + f(i-1, j+1, mat, n, dp);
        return dp[i][j] = max(up, max(upLeft, upRight));
    }
};
```
