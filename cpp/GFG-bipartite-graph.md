# [Bipartite Graph](https://www.geeksforgeeks.org/problems/bipartite-graph/1)

<blockquote>

## Problem Statement

Given a Graph with V vertices (Numbered from 0 to V-1 ) and E edges. Check whether the graph is bipartite or not.

A bipartite graph can be colored with two colors such that no two adjacent vertices share the same color . This means we can divide the graph’s vertices into two distinct sets where:

All edges connect vertices from one set to vertices in the other set. No edges exist between vertices within the same set.

Examples:

Input: V = 3, edges[][] = [[0, 1], [1,2]]
![Bipartite-Graph](https://media.geeksforgeeks.org/wp-content/uploads/20240926114602/Bipartite-Graph.webp)
Output: true
Explanation: The given graph can be colored in two colors so, it is a bipartite graph.

Input: V = 4, edges[][] = [[0, 3], [1, 2], [3, 2], [0, 2]]![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/700410/Web/Other/blobid0_1735020917.webp)Output: false Explanation: The given graph cannot be colored in two colors such that color of adjacent vertices differs.

Constraints: 1 ≤ V ≤ 2 * 10 5 1 ≤ edges.size() ≤ 10 5 1 ≤ edges[i][j] ≤ 10 5

## Input Format

First line should contain V and E. Each of next E lines should contain two space separated integers. Example:

```
3 2
0 1
1 2
```

Sample Input:
3&!//!&2&!//!&0 1
1 2

## Examples

```
Input: V = 3, edges[][] = [[0, 1], [1,2]]

Output: true
Explanation: The given graph can be colored in two colors so, it is a bipartite graph.


Input: V = 4, edges[][] = [[0, 3], [1, 2], [3, 2], [0, 2]]Output: false Explanation: The given graph cannot be colored in two colors such that color of adjacent vertices differs. 
```

## Constraints

Constraints:

**Tags:** DFS, Graph, BFS, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/bipartite-graph/


</blockquote>

## Solution
```cpp
class Solution {
private:
    // 1 = red, 2 = blue
    // x = 3-x flips b/w 1 and 2
    // BUT using 0 = red, 1 = blue
    bool dfs(int node, int nodeColor, vector<vector<int>> &adj, vector<int> &color) {
        color[node] = nodeColor;
        for(auto &it : adj[node]) {
            if(color[it] == -1) {
                if(!dfs(it, !color[node], adj, color)) return false;
            }
            else if(color[it] == nodeColor) {
                return false;
            }
        }
        return true;
    } 
    bool bfs(int node, vector<vector<int>> &adj, vector<int> &color) {
        queue<int> q;
        color[node] = 0;
        q.push(node);
        while(!q.empty()) {
            auto vert = q.front();
            q.pop();
            
            for(auto it : adj[vert]) {
                if(color[it] == -1) {
                    color[it] = !color[vert];
                    q.push(it);
                }
                else if(color[it] == color[vert]) {
                    return false;
                }
            }
        }
        return true;
    }
public:
    bool isBipartite(int V, vector<vector<int>> &edges) {
        
        vector<vector<int>> adj(V);
        for(auto &e : edges) {
            int u = e[0];
            int v = e[1];
            adj[u].push_back(v);
            adj[v].push_back(u);
        }
        
        vector<int> color(V, -1);
        
        for(int i=0; i<V; ++i) {
            if(color[i] == -1) {
                // if(!dfs(i, 0, adj, color)) return false;
                if(!bfs(i, adj, color)) return false;
            }
        }
        
        return true;
    }
};
```
