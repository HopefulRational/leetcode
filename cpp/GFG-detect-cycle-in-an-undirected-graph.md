# [Undirected Graph Cycle](https://www.geeksforgeeks.org/problems/detect-cycle-in-an-undirected-graph/1)

<blockquote>

## Problem Statement

Given an undirected graph with V vertices and E edges, represented as a 2D vector edges[][] , where each entry edges[i] = [u, v] denotes an edge between vertices u and v , determine whether the graph contains a cycle or not.

Note: The graph can have multiple component. ![](C:\Users\Mukul kumar\Desktop\GFG_PIC.JPG)

Examples:

Input: V = 4, E = 4, edges[][] = [[0, 1], [0, 2], [1, 2], [2, 3]]
Output: true
Explanation: 
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/891735/Web/Other/blobid1_1743510240.jpg) 1 -> 2 -> 0 -> 1 is a cycle.

Input: V = 4, E = 3, edges[][] = [[0, 1], [1, 2], [2, 3]]
Output: false
Explanation: 
![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/891735/Web/Other/blobid2_1743510254.jpg) No cycle in the graph.

Constraints: 1 ≤ V, E ≤ 10 5 0 ≤ edges[i][0], edges[i][1] < V

## Input Format

V = &!//!&E = &!//!&edges[][] =

Sample Input:
4&!//!&4&!//!&0 1
0 2
1 2
2 3

## Examples

```
Input: V = 4, E = 4, edges[][] = [[0, 1], [0, 2], [1, 2], [2, 3]]
Output: true
Explanation: 
 1 -> 2 -> 0 -> 1 is a cycle.


Input: V = 4, E = 3, edges[][] = [[0, 1], [1, 2], [2, 3]]
Output: false
Explanation: 
 No cycle in the graph.

```

## Constraints

Constraints:

**Tags:** DFS, Graph, union-find, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/detect-cycle-in-an-undirected-graph-using-bfs/

- https://www.geeksforgeeks.org/detect-cycle-undirected-graph/


</blockquote>

## Solution
```cpp
class Solution {
private:
    bool bfs(int node, vector<vector<int>> &adj, vector<int> &vis) {
        int parent = -1;
        vis[node] = 1;
        queue<pair<int, int>> q;
        q.push({node, parent});
        while(!q.empty()) {
            auto [u, par] = q.front();
            q.pop();
            
            for(auto &v : adj[u]) {
                if(!vis[v]) {
                    vis[v] = 1;
                    q.push({v, u});
                }
                else if(par != v) {
                    return true;
                }
            }
        }
        
        return false;
    }
    bool dfs(int node, int parent, vector<vector<int>> &adj, vector<int> &vis) {
        vis[node] = 1;
        
        for(auto it : adj[node]) {
            if(!vis[it]) {
                if(dfs(it, node, adj, vis)) return true;
            }
            else if(it != parent) {
                return true;
            }
        }
        
        return false;
    }
  public:
    bool isCycle(int V, vector<vector<int>>& edges) {
        // Code here
        vector<int> vis(V, 0);
        vector<vector<int>> adj(V);
        
        for(auto &e : edges) {
            int u = e[0];
            int v = e[1];
            adj[u].push_back(v);
            adj[v].push_back(u);
        }
        
        for(int i=0; i<V; ++i) {
            if(!vis[i]) {
                // if(bfs(i, adj, vis)) return true;
                if(dfs(i, -1, adj, vis)) return true;
            }
        }
        
        return false;
    }
};
```
