# [567. Permutation in String](https://leetcode.com/problems/permutation-in-string/)

**Difficulty:** Medium

**Topics:** Hash Table, Two Pointers, String, Sliding Window

---



<blockquote>

<p>Given two strings <code>s1</code> and <code>s2</code>, return <code>true</code> if <code>s2</code> contains a <span data-keyword="permutation-string">permutation</span> of <code>s1</code>, or <code>false</code> otherwise.</p>

<p>In other words, return <code>true</code> if one of <code>s1</code>&#39;s permutations is the substring of <code>s2</code>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>

<pre>
<strong>Input:</strong> s1 = &quot;ab&quot;, s2 = &quot;eidbaooo&quot;
<strong>Output:</strong> true
<strong>Explanation:</strong> s2 contains one permutation of s1 (&quot;ba&quot;).
</pre>

<p><strong class="example">Example 2:</strong></p>

<pre>
<strong>Input:</strong> s1 = &quot;ab&quot;, s2 = &quot;eidboaoo&quot;
<strong>Output:</strong> false
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= s1.length, s2.length &lt;= 10<sup>4</sup></code></li>
	<li><code>s1</code> and <code>s2</code> consist of lowercase English letters.</li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    bool checkInclusion(string s1, string s2) {
        if(s1.size() > s2.size()) return 0;
        int matched = 0;
        int m = s1.size(), n = s2.size();
        int c1[26] = {0}, c2[26] = {0};
        for(int i=0; i<m; ++i) {
            c1[s1[i]-'a']++;
            c2[s2[i]-'a']++;
        }
        for(int i=0; i<26; ++i) {
            matched += (c1[i] == c2[i]);
        }
        int i = 0, j = s1.size();
        while(j < n) {
            if(matched == 26) return true;
            
            // increment i
            c2[s2[i]-'a']--;
            if(c2[s2[i]-'a']+1 == c1[s2[i]-'a']) {
                matched--;
            }
            else if(c2[s2[i]-'a'] == c1[s2[i]-'a']) {
                matched++;
            }
            i++;

            // increment j
            c2[s2[j]-'a']++;
            if(c2[s2[j]-'a']-1 == c1[s2[j]-'a']) {
                matched--;
            }
            else if(c2[s2[j]-'a'] == c1[s2[j]-'a']) {
                matched++;
            }
            j++;
        }

        return matched == 26;
    }
};
```
