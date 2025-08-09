# [808. Soup Servings](https://leetcode.com/problems/soup-servings/)

**Difficulty**: Medium  
**Topics**: Dynamic Programming, Probability and Statistics

## Problem Statement

There are two types of soup: **type A** and **type B**. Initially, we have `n` ml of each type of soup. There are four kinds of operations:

1. Serve **100 ml** of soup A and **0 ml** of soup B,
2. Serve **75 ml** of soup A and **25 ml** of soup B,
3. Serve **50 ml** of soup A and **50 ml** of soup B,
4. Serve **25 ml** of soup A and **75 ml** of soup B.

When we serve some volume of soup, we give it to someone, and we no longer have it. Each turn, we will choose from the four operations with equal probability **0.25**. We stop once we no longer have some quantity of both types of soup.

Return the probability that soup A will be empty first, plus half the probability that A and B become empty at the same time. Answers within **10<sup>-5</sup>** of the true value will be accepted.

## Examples

### Example 1:
**Input**: `n = 50`  
**Output**: `0.62500`  
**Explanation**:  
- If we choose the first two operations, A will become empty first.
- For the third operation, A and B will become empty at the same time.
- For the fourth operation, B will become empty first.
  
The final probability is:  
`(0.25 * 1 + 0.25 * 1 + 0.25 * 0.5 + 0.25 * 0) = 0.625`.

### Example 2:
**Input**: `n = 100`  
**Output**: `0.71875`

## Constraints
- `0 <= n <= 10^9`

## Solution
```cpp
class Solution {
public:
    double memo[200][200];
    double soupServings(int n) {
        // When N = 4800, the result = 0.999994994426
        // When N = 4801, the result = 0.999995382315
        // So if N>= 4800, just return 1 and it will be enough.

        return n > 4800 ? 1 : f((n+24)/25, (n+24)/25);
    }
    double f(int a, int b) {
        if(a <= 0 && b <= 0) return 0.5;
        if(a <= 0) return 1;
        if(b <= 0) return 0;
        if(memo[a][b] > 0) return memo[a][b];
        return 0.25 * (f(a-4 ,b) + f(a-3, b-1) + f(a-2 ,b-2) + f(a-1, b-3));
    }
};
```
