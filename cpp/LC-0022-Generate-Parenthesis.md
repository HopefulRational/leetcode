# [22. Generate Parentheses](https://leetcode.com/problems/generate-parentheses/)

**Difficulty:** Medium

**Topics:** String, Dynamic Programming, Backtracking

---



<blockquote>

<p>Given <code>n</code> pairs of parentheses, write a function to <em>generate all combinations of well-formed parentheses</em>.</p>

<p>&nbsp;</p>
<p><strong class="example">Example 1:</strong></p>
<pre><strong>Input:</strong> n = 3
<strong>Output:</strong> ["((()))","(()())","(())()","()(())","()()()"]
</pre><p><strong class="example">Example 2:</strong></p>
<pre><strong>Input:</strong> n = 1
<strong>Output:</strong> ["()"]
</pre>
<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>

<ul>
	<li><code>1 &lt;= n &lt;= 8</code></li>
</ul>


</blockquote>

## Solution
```cpp
class Solution {
public:
    vector<string> generateParenthesisV2(int n) {
        // res[k] has all valid combinations containing k open brackets
        vector<vector<string>> res(n + 1);
        res[0] = {""};

        // Each valid pair can be uniquely written as: 
        //      S = '(' + A + ')' + B,  where A,B are valid
        // k tracks the open bracket count. 0..n
        // For making k, picking i, k-i-1, 1 open-close brackets
        for (int k = 0; k <= n; ++k) {
            for (int i = 0; i < k; ++i) {
                for (const string& left : res[i]) { // picking i valid 
                    for (const string& right : res[k - i - 1]) { // picking (k-i)-1 valid
                        res[k].push_back("(" + left + ")" + right); // adding 1 more valid uniquely
                    }
                }
            }
        }

        return res[n];
    }

    vector<string> generateParenthesisV1(int n) {
        vector<string> ans;
        function<void(int,int, string&)> backtrack = [&](int open, int closed, string &s) {
            if(closed == n) {
                ans.push_back(s);
                return;
            }
            // use open if not exhausted
            if(open < n) {
                s.push_back('(');
                backtrack(open+1, closed, s);
                s.pop_back();
            }
            // use closed if possible to close
            if(closed < open) {
                s.push_back(')');
                backtrack(open, closed+1, s);
                s.pop_back();
            }
        };

        string s;
        backtrack(0, 0, s);

        return ans;
    }
};
```
