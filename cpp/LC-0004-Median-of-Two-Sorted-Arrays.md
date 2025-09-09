# [4. Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/)

**Difficulty:** Hard

**Topics:** Array, Binary Search, Divide and Conquer

---



<blockquote>

<p>Given two sorted arrays <code>nums1</code> and <code>nums2</code> of size <code>m</code> and <code>n</code> respectively, return <strong>the median</strong> of the two sorted arrays.</p>

<p>The overall run time complexity should be <code>O(log (m+n))</code>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> nums1 = [1,3], nums2 = [2]
<strong>Output:</strong> 2.00000
<strong>Explanation:</strong> merged array = [1,2,3] and median is 2.
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> nums1 = [1,2], nums2 = [3,4]
<strong>Output:</strong> 2.50000
<strong>Explanation:</strong> merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>nums1.length == m</code></li>
	<li><code>nums2.length == n</code></li>
	<li><code>0 &lt;= m &lt;= 1000</code></li>
	<li><code>0 &lt;= n &lt;= 1000</code></li>
	<li><code>1 &lt;= m + n &lt;= 2000</code></li>
	<li><code>-10<sup>6</sup> &lt;= nums1[i], nums2[i] &lt;= 10<sup>6</sup></code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    double findMedianSortedArrays(vector<int>& X, vector<int>& Y) {
        if(X.size() > Y.size()) swap(X, Y);
        // K is required for getting partitionY from partitionX(=((L+R)/2))
        int M = X.size(), N = Y.size(), K = (M + N + 1) / 2, L = 0, R = M;
        
        while(L <= R) {
            // partitionX = # elements on left
            int partitionX = (L + R) / 2;
            int partitionY = K - partitionX;
            
            int maxLeftX = partitionX == 0 ? INT_MIN : X[partitionX-1];
            int minRightX = partitionX == M ? INT_MAX : X[partitionX];
            
            int maxLeftY = partitionY == 0 ? INT_MIN : Y[partitionY-1];
            int minRightY = partitionY == N ? INT_MAX : Y[partitionY];
            
            if(maxLeftX <= minRightY && maxLeftY <= minRightX) {
                if((M + N) & 1) return max(maxLeftX, maxLeftY);
                else return (max(maxLeftX, maxLeftY) + min(minRightX, minRightY)) / 2.;
            }
            else if(maxLeftX > minRightY) R = partitionX - 1;
            else L = partitionX + 1;
        }
        
        return -1;
    }
};
```
