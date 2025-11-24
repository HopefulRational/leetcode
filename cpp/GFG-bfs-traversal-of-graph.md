# [BFS of graph](https://www.geeksforgeeks.org/problems/bfs-traversal-of-graph/1)

<blockquote>

## Problem Statement

Given a connected undirected graph containing V vertices, represented by a 2-d adjacency list adj[][] , where each adj[i] represents the list of vertices connected to vertex i . Perform a Breadth First Search (BFS) traversal starting from vertex 0 , visiting vertices from left to right according to the given adjacency list, and return a list containing the BFS traversal of the graph.

Note: Do traverse in the same order as they are in the given adjacency list .

Examples:

Input: adj[][] = [[2, 3, 1], [0], [0, 4], [0], [2]]![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/700217/Web/Other/blobid0_1728648582.jpg)Output: [0, 2, 3, 1, 4]Explanation: Starting from 0, the BFS traversal will follow these steps: Visit 0 → Output: 0 Visit 2 (first neighbor of 0) → Output: 0, 2 Visit 3 (next neighbor of 0) → Output: 0, 2, 3 Visit 1 (next neighbor of 0) → Output: 0, 2, 3, 1Visit 4 (neighbor of 2) → Final Output: 0, 2, 3, 1, 4

Input: adj[][] = [[1, 2], [0, 2], [0, 1, 3, 4], [2], [2]]![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/700217/Web/Other/blobid1_1728648604.jpg)Output: [0, 1, 2, 3, 4]Explanation: Starting from 0, the BFS traversal proceeds as follows: Visit 0 → Output: 0 Visit 1 (the first neighbor of 0) → Output: 0, 1 Visit 2 (the next neighbor of 0) → Output: 0, 1, 2 Visit 3 (the first neighbor of 2 that hasn't been visited yet) → Output: 0, 1, 2, 3 Visit 4 (the next neighbor of 2) → Final Output: 0, 1, 2, 3, 4

Constraints: 1 ≤ V = adj.size() ≤ 10 4 0 ≤ adj[i][j] ≤ 10 4

## Input Format

V represent as the no. of vertices. adj[][] represent as the 2-d adjacency list where each adj[i] represents the list of vertices connected to vertex i.

Sample Input:
5&!//!&2 3 1
0 
0 4 
0 
2

## Examples

```
Input: adj[][] = [[2, 3, 1], [0], [0, 4], [0], [2]]Output: [0, 2, 3, 1, 4]Explanation: Starting from 0, the BFS traversal will follow these steps: Visit 0 → Output: 0 Visit 2 (first neighbor of 0) → Output: 0, 2 Visit 3 (next neighbor of 0) → Output: 0, 2, 3 Visit 1 (next neighbor of 0) → Output: 0, 2, 3, 1Visit 4 (neighbor of 2) → Final Output: 0, 2, 3, 1, 4

Input: adj[][] = [[1, 2], [0, 2], [0, 1, 3, 4], [2], [2]]Output: [0, 1, 2, 3, 4]Explanation: Starting from 0, the BFS traversal proceeds as follows: Visit 0 → Output: 0 Visit 1 (the first neighbor of 0) → Output: 0, 1 Visit 2 (the next neighbor of 0) → Output: 0, 1, 2 Visit 3 (the first neighbor of 2 that hasn't been visited yet) → Output: 0, 1, 2, 3 Visit 4 (the next neighbor of 2) → Final Output: 0, 1, 2, 3, 4
```

## Constraints

Constraints:

**Tags:** Graph, BFS, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/


</blockquote>

## Solution
```cpp
class Solution {
  public:
    vector<int> bfs(vector<vector<int>> &adj) {
        // code here
        vector<int> ans;
        int m = adj.size();
        
        // vis, q, push
        vector<int> vis(m, 0);
        vis[0] = 1;
        queue<int> q;
        q.push(0);
        
        while(!q.empty()) {
            int node = q.front();
            q.pop();
            ans.push_back(node);
            
            for(auto &v : adj[node]) {
                if(!vis[v]) {
                    vis[v] = true;
                    q.push(v);
                }
            }
        }
        
        return ans;
    }
};
```
