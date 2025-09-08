# [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)

**Difficulty:** Medium

**Topics:** Hash Table, String, Sliding Window

---



<blockquote>

<p>Given a string <code>s</code>, find the length of the <strong>longest</strong> <span data-keyword="substring-nonempty"><strong>substring</strong></span> without duplicate characters.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> s = &quot;abcabcbb&quot;
<strong>Output:</strong> 3
<strong>Explanation:</strong> The answer is &quot;abc&quot;, with the length of 3.
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> s = &quot;bbbbb&quot;
<strong>Output:</strong> 1
<strong>Explanation:</strong> The answer is &quot;b&quot;, with the length of 1.
</pre>

<p><strong class="example">Example 3:</strong></p>

<pre>
<strong>Input:</strong> s = &quot;pwwkew&quot;
<strong>Output:</strong> 3
<strong>Explanation:</strong> The answer is &quot;wke&quot;, with the length of 3.
Notice that the answer must be a substring, &quot;pwke&quot; is a subsequence and not a substring.
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>0 &lt;= s.length &lt;= 5 * 10<sup>4</sup></code></li>
	<li><code>s</code> consists of English letters, digits, symbols and spaces.</li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    int lengthOfLongestSubstringSetBased(string s) {
        int ans = 0;
        unordered_set<char> us;
        int i=0, j=0, n=s.size();
        while(j < n) {
            while(us.count(s[j])) {
                us.erase(s[i++]);
            }
            us.insert(s[j]);
            ans = max(ans, (int)us.size());
            ++j;
        }

        return ans;
    }

    int lengthOfLongestSubstringArrayBased(string s) {
        int ans = 0;
        int cnt[256] = {0};
        int i=0, j=0, n=s.size();
        while(j < n) {
            while(cnt[s[j]]) {
                cnt[s[i]]--;
                i++;
            }
            cnt[s[j]]++;
            ans = max(ans, j-i+1);
            ++j;
        }

        return ans;
    }
};
```
