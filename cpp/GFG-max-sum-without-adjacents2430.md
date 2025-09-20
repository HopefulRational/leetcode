# [Max Sum without Adjacents](https://www.geeksforgeeks.org/problems/max-sum-without-adjacents2430/1)

<blockquote>

## Problem Statement

Given an array arr containing positive integers. Find the maximum sum of elements of any possible subsequence such that no two numbers in the subsequence should be adjacent in array arr[] .

Examples:

```
Input: arr[] = [5, 5, 10, 100, 10, 5]
Output: 110
Explanation: If you take indices 0, 3 and 5, then = 5+100+5 = 110.
```

```
Input: arr[] = [3, 2, 7, 10]
Output: 13
Explanation: 3 and 10 forms a non continuous subsequence with maximum sum.
```

```
Input: arr[] = [9, 1, 6, 10]
Output: 19
Explanation: 9 and 10 forms a non continuous subsequence with maximum sum.
```

Constraints: 1 ≤ arr.size() ≤ 10 5 1 ≤ arr i ≤ 10 5

## Input Format

The custom test case should contain 2 lines. The first line should contain single integer N denoting the size of array. Then next line contains N space seperated integers denoting array Arr.

Example :

```
6
5 5 10 100 10 5
```

Sample Input:
5 5 10 100 10 5

## Examples

```
Input: arr[] = [5, 5, 10, 100, 10, 5]
Output: 110
Explanation: If you take indices 0, 3 and 5, then = 5+100+5 = 110.

Input: arr[] = [3, 2, 7, 10]
Output: 13
Explanation: 3 and 10 forms a non continuous subsequence with maximum sum.

Input: arr[] = [9, 1, 6, 10]
Output: 19
Explanation: 9 and 10 forms a non continuous subsequence with maximum sum.
```

## Constraints

Constraints:

**Tags:** Arrays, Dynamic Programming, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/maximum-sum-such-that-no-two-elements-are-adjacent/


</blockquote>

## Solution
```cpp
class Solution {
  public:
    int f(vector<int> &arr, int idx, vector<int> &dp) {
        if(idx == 0) return arr[idx];
        if(idx < 0)  return 0;
        if(dp[idx] != -1) return dp[idx];
        int pick = arr[idx] + f(arr, idx-2, dp);
        int notPick = 0 + f(arr, idx-1, dp);
        return dp[idx] = max(pick, notPick);
    }
    int findMaxSum(vector<int>& arr) {
        int n = arr.size();
        vector<int> dp(n, -1);
        // return f(arr, n-1, dp);
        
        // dp[0] = arr[0];
        // for(int i=1; i<=n-1; ++i) {
        //     int pick = arr[i] + dp[i-2];
        //     int notPick = 0 + dp[i-1];
        //     dp[i] = max(pick, notPick);
        // }
        // return dp[n-1];
        
        int prev1 = arr[0], prev2 = 0;
        for(int i=1; i<=n-1; ++i) {
            int pick = arr[i] + prev2;
            int notPick = 0 + prev1;
            int curi = max(pick, notPick);
            prev2 = prev1;
            prev1 = curi;
        }
        return prev1;
    }
};
```
