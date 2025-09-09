# [84. Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/)

**Difficulty:** Hard

**Topics:** Array, Stack, Monotonic Stack

---



<blockquote>

<p>Given an array of integers <code>heights</code> representing the histogram&#39;s bar height where the width of each bar is <code>1</code>, return <em>the area of the largest rectangle in the histogram</em>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>
<img alt="" src="https://assets.leetcode.com/uploads/2021/01/04/histogram.jpg" style="width: 522px; height: 242px;" />
<pre>
<strong>Input:</strong> heights = [2,1,5,6,2,3]
<strong>Output:</strong> 10
<strong>Explanation:</strong> The above is a histogram where width of each bar is 1.
The largest rectangle is shown in the red area, which has an area = 10 units.
</pre>

<p><strong class="example">Example 2:</strong></p>
<img alt="" src="https://assets.leetcode.com/uploads/2021/01/04/histogram-1.jpg" style="width: 202px; height: 362px;" />
<pre>
<strong>Input:</strong> heights = [2,4]
<strong>Output:</strong> 4
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= heights.length &lt;= 10<sup>5</sup></code></li>
	<li><code>0 &lt;= heights[i] &lt;= 10<sup>4</sup></code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    int largestRectangleArea(vector<int>& h) {
        stack<int> stk;
        int ans = 0;
        
        // to make sure flusing happens 
        // and we dont have to do it explicitly 
        // post the below for loop
        h.push_back(0); 
        
        for(int i=0,n=h.size(); i<n; ++i) {
            while(stk.size() && h[i] < h[stk.top()]) {
                int ht = h[stk.top()]; stk.pop();
                int j = stk.size() ? stk.top() : -1;
                ans = max(ans, ht * (i-1-j));
            }
            stk.push(i);
        }
        
        return ans;
    }
};
```
