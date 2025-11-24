# [Number of Provinces](https://www.geeksforgeeks.org/problems/number-of-provinces/1)

<blockquote>

## Problem Statement

Given an undirected graph with V vertices. We say two vertices u and v belong to a single province if there is a path from u to v or v to u. Your task is to find the number of provinces. Note: A province is a group of directly or indirectly connected cities and no other cities outside of the group.

Example 1:

Input:[[1, 0, 1],[0, 1, 0],[1, 0, 1]]
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/706298/Web/Other/blobid0_1744377052.jpg) Output:
2
Explanation:
The graph clearly has 2 Provinces [1,3] and [2]. As city 1 and city 3 has a path between them they belong to a single province. City 2 has no path to city 1 or city 3 hence it belongs to another province.

Example 2:

Input:[[1, 1],[1, 1]] ![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/706298/Web/Other/blobid1_1744378525.jpg) Output :
1

Your Task: You don't need to read input or print anything. Your task is to complete the function numProvinces() which takes an integer V and an adjacency matrix adj(as a 2d vector) as input and returns the number of provinces. adj[i][j] = 1, if nodes i and j are connected and adj[i][j] = 0, if not connected.

Expected Time Complexity: O(V 2 ) Expected Auxiliary Space: O(V)

Constraints: 1 ≤ V ≤ 500

## Input Format

Custom test case should contain V+1 lines. First line contains an integer V. Next V lines contains a list of V integers.

Example:

```
3
1 0 1
0 1 0
1 0 1
```

Sample Input:
3

1 0 1

0 1 0

1 0 1

## Examples

```
Input:[[1, 0, 1],[0, 1, 0],[1, 0, 1]]
 Output:
2
Explanation:
The graph clearly has 2 Provinces [1,3] and [2]. As city 1 and city 3 has a path between them they belong to a single province. City 2 has no path to city 1 or city 3 hence it belongs to another province.


Input:[[1, 1],[1, 1]]  Output :
1

```

## Constraints

Constraints:

**Tags:** DFS, Graph, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/connected-components-in-an-undirected-graph/


</blockquote>

## Solution
```cpp
class Solution {
  private:
    void dfs(int node, vector<vector<int>> &adj, vector<int> &vis) {
        vis[node] = 1;
        
        for(auto &it : adj[node]) {
            if(!vis[it]) {
                dfs(it, adj, vis);
            }
        }
    }
  public:
    int numProvinces(vector<vector<int>> adjMat, int V) {
        // code here
        vector<int> vis(V, 0);
        int ans = 0;
        vector<vector<int>> adj(V);
        
        for(int i=0; i<V; ++i) {
            for(int j=i+1; j<V; ++j) {
                if(adjMat[i][j]) {
                    adj[i].push_back(j);
                    adj[j].push_back(i);   
                }
            }
        }
        
        for(int i=0; i<V; ++i) {
            if(!vis[i]) {
                dfs(i, adj, vis);
                ++ans;
            }
        }
        
        return ans;
    }
};
```
