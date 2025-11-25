# [Directed Graph Cycle](https://www.geeksforgeeks.org/problems/detect-cycle-in-a-directed-graph/1)

<blockquote>

## Problem Statement

Given a Directed Graph with V vertices (Numbered from 0 to V-1 ) and E edges, check whether it contains any cycle or not. The graph is represented as a 2D vector edges[][] , where each entry edges[i] = [u, v] denotes an edge from verticex u to v.

Examples:

Input: V = 4, edges[][] = [[0, 1], [1, 2], [2, 0], [2, 3]]

![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/700218/Web/Other/blobid0_1761112751.jpg)

Output: true
Explanation: The diagram clearly shows a cycle 0 → 1 → 2 → 0

Input: V = 4, edges[][] = [[0, 1], [0, 2], [1, 2], [2, 3]]
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/700218/Web/Other/blobid1_1761112778.jpg)Output: false
Explanation: no cycle in the graph

Constraints: 1 ≤ V ≤ 10 5 0 ≤ E ≤ 10 5 0 ≤ edges[i][0], edges[i][1] < V

## Input Format

V = &!//!&E = &!//!&edges[][]

Sample Input:
4&!//!&4&!//!&0 1
1 2
2 0
2 3

## Examples

```
Input: V = 4, edges[][] = [[0, 1], [1, 2], [2, 0], [2, 3]]



Output: true
Explanation: The diagram clearly shows a cycle 0 → 1 → 2 → 0

Input: V = 4, edges[][] = [[0, 1], [0, 2], [1, 2], [2, 3]]
Output: false
Explanation: no cycle in the graph
```

## Constraints

Constraints:

**Tags:** Graph, Data Structures

**Article / Editorial:**

- https://www.geeksforgeeks.org/detect-cycle-in-a-graph/


</blockquote>

## Solution
```cpp
class Solution {
private:
    bool dfs(int node, vector<vector<int>> &adj, vector<int> &vis, vector<int> &pathVis) {
        vis[node] = 1;
        pathVis[node] = 1;
        
        for(auto it : adj[node]) {
            if(!vis[it]) {
                if(dfs(it, adj, vis, pathVis)) return true;
            }
            else if(pathVis[it]) {
                return true;
            }
        }
        
        pathVis[node] = 0;
        return false;
    }
public:
    bool isCyclic(int V, vector<vector<int>> &edges) {
        vector<vector<int>> adj(V);
        for(auto &e : edges) {
            int u = e[0];
            int v = e[1];
            adj[u].push_back(v);
        }
        
        vector<int> vis(V, 0);
        vector<int> pathVis(V, 0);
        
        for(int i=0; i<V; ++i) {
            if(!vis[i]) {
                if(dfs(i, adj, vis, pathVis)) return true;
            }
        }
        
        return false;
    }
};
```
