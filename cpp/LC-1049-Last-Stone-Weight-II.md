# [1049. Last Stone Weight II](https://leetcode.com/problems/last-stone-weight-ii/)

**Difficulty:** Medium

**Topics:** Array, Dynamic Programming

**Note:** Same as `Partition a set into two subsets with minimum absolute sum difference`

---



<blockquote>

<p>You are given an array of integers <code>stones</code> where <code>stones[i]</code> is the weight of the <code>i<sup>th</sup></code> stone.</p>

<p>We are playing a game with the stones. On each turn, we choose any two stones and smash them together. Suppose the stones have weights <code>x</code> and <code>y</code> with <code>x &lt;= y</code>. The result of this smash is:</p>

<ul>
	<li>If <code>x == y</code>, both stones are destroyed, and</li>
	<li>If <code>x != y</code>, the stone of weight <code>x</code> is destroyed, and the stone of weight <code>y</code> has new weight <code>y - x</code>.</li>
</ul>

<p>At the end of the game, there is <strong>at most one</strong> stone left.</p>

<p>Return <em>the smallest possible weight of the left stone</em>. If there are no stones left, return <code>0</code>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> stones = [2,7,4,1,8,1]
<strong>Output:</strong> 1
<strong>Explanation:</strong>
We can combine 2 and 4 to get 2, so the array converts to [2,7,1,8,1] then,
we can combine 7 and 8 to get 1, so the array converts to [2,1,1,1] then,
we can combine 2 and 1 to get 1, so the array converts to [1,1,1] then,
we can combine 1 and 1 to get 0, so the array converts to [1], then that&#39;s the optimal value.
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> stones = [31,26,33,21,40]
<strong>Output:</strong> 5
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= stones.length &lt;= 30</code></li>
	<li><code>1 &lt;= stones[i] &lt;= 100</code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:

    int lastStoneWeightII(vector<int>& stones) {
        int n = stones.size();
        int sum = accumulate(stones.begin(), stones.end(), 0);

        vector<bool> prev(sum+1, false), cur(sum+1, false);
        prev[0] = true;
        cur[0] = true; // making sure prev[0] is always true, even after swap
        prev[stones[0]] = true;
        for(int i=1; i<n; ++i) {
            for(int target=1; target<=sum; ++target) {
                bool notTake = prev[target];
                bool take = false;
                if(stones[i] <= target) {
                    take = prev[target-stones[i]];
                }
                cur[target] = take | notTake;
            }
            swap(prev, cur);
        }

        // int mini = 1e6;
        // for(int s1=0; s1<=sum/2; ++s1) {
        //     if(prev[s1]) {
        //         mini = min(mini, abs(sum-s1 - s1));
        //     }
        // }
        // return mini;

        for(int s1=sum/2; s1>=0; --s1)
            if(prev[s1]) return abs(sum-s1 - s1);
        
        return 0;
    }
};
```
