# [Safe States](https://www.geeksforgeeks.org/problems/eventual-safe-states/1)

<blockquote>

## Problem Statement

Given a directed graph with V vertices numbered from 0 to V-1 and E directed edges, represented as a 2D array edges[][] , where each element edges[i] = [u, v] represents a directed edge from vertex u to vertex v . Return all Safe Nodes of the graph. A vertex with no outgoing edges is called a terminal node . A vertex is considered safe if every path starting from it eventually reaches a terminal node.

Examples:

Input: V = 5, E = 6, edges[][] = [[1, 0], [1, 2], [1, 3], [1, 4], [2, 3], [3, 4]]![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/913663/Web/Other/blobid0_1761648473.webp)Output: [0, 1, 2, 3, 4]
Explanation: 4 and 0 is the terminal node, and all the paths from 1, 2, 3 lead to terminal node, i.e., 4.

Input: V = 4, E = 3, edges[][] = [[1, 2], [2, 3], [3, 2]]![](https://media.geeksforgeeks.org/img-practice/prod/addEditProblem/913663/Web/Other/blobid1_1761648488.webp)Output: [0]
Explanation: 0 is the terminal node, and no other node than 0 leads to 0.

Constraints: 1 ≤ V ≤ 10 5 0 ≤ E ≤ 10 5 0 ≤ edges[i][0], edges[i][1] < V

## Input Format

First line should contain two space separated integers, denoting V and E ,  respectively.

Each of next E lines should contain two space separated integers, u and v respectively, denoting a directed edge from node u to node v .

Example:

```
7 7 
0 1
0 2
1 2
1 3
3 0
4 5
2 5
```

Sample Input:
5&!//!&6&!//!&1 0
1 2
1 3
1 4
2 3
3 4

## Examples

```
Input: V = 5, E = 6, edges[][] = [[1, 0], [1, 2], [1, 3], [1, 4], [2, 3], [3, 4]]Output: [0, 1, 2, 3, 4]
Explanation: 4 and 0 is the terminal node, and all the paths from 1, 2, 3 lead to terminal node, i.e., 4.

Input: V = 4, E = 3, edges[][] = [[1, 2], [2, 3], [3, 2]]Output: [0]
Explanation: 0 is the terminal node, and no other node than 0 leads to 0.
```

## Constraints

Constraints:

**Tags:** DFS, Graph, BFS, Data Structures, Algorithms

**Article / Editorial:**

- https://www.geeksforgeeks.org/eventual-safe-states/


</blockquote>

## Solution
```cpp
class Solution {
private:
    bool dfsCheck(int node, vector<vector<int>> &adj, vector<int> &vis, vector<int> &pathVis, vector<int> &check) {
        vis[node] = 1;
        pathVis[node] = 1;
        check[node] = 0;
        
        for(auto it : adj[node]) {
            if(!vis[it]) {
                if(dfsCheck(it, adj, vis, pathVis, check)) {
                    check[node] = 0;
                    return true;
                }
            }
            else if(pathVis[it]) {
                check[node] = 0;
                return true;
            }
        }
        
        pathVis[node] = 0;
        check[node] = 1;
        return false;
    }
public:
    vector<int> safeNodes(int V, vector<vector<int>>& edges) {
        vector<vector<int>> adj(V);
        for(auto &e : edges) {
            int u = e[0];
            int v = e[1];
            adj[u].push_back(v);
        }
        
        vector<int> vis(V, 0);
        vector<int> pathVis(V, 0);
        vector<int> check(V, 0);
        
        for(int i=0; i<V; ++i) {
            if(!vis[i]) {
                dfsCheck(i, adj, vis, pathVis, check);
            }
        }
        
        vector<int> safeNodes;
        for(int i=0; i<V; ++i) {
            if(check[i]) {
                safeNodes.push_back(i);
            }
        }
        
        return safeNodes;
        
    }
};
```
```cpp
class Solution {
private:
    // states:
    // 0=notVisited, 1=visiting, 2=visitedAndDone
    bool dfsCheck(int node, vector<vector<int>> &adj, vector<int> &states) {
        if(states[node] == 1) return false; // cycle
        if(states[node] == 2) return true;  // node finished
        
        states[node] = 1;
        
        for(auto it : adj[node]) {
            if(!dfsCheck(it, adj, states)) {
                return false; // child leads to cycle
            }
        }
        
        states[node] = 2;
        return true;
    }
public:
    vector<int> safeNodes(int V, vector<vector<int>>& edges) {
        vector<vector<int>> adj(V);
        for(auto &e : edges) {
            int u = e[0];
            int v = e[1];
            adj[u].push_back(v);
        }
        
        vector<int> states(V, 0);
        
        for(int i=0; i<V; ++i) {
            if(!states[i]) {
                dfsCheck(i, adj, states);
            }
        }
        
        vector<int> safeNodes;
        for(int i=0; i<V; ++i) {
            if(states[i] == 2) {
                safeNodes.push_back(i);
            }
        }
        
        return safeNodes;
        
    }
};
```
