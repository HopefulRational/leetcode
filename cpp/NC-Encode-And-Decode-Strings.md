# [Encode and Decode Strings (Medium) - NeetCode](https://neetcode.io/problems/string-encode-and-decode)

<blockquote>

Design an algorithm to encode a list of strings to a single string. The encoded string is then decoded back to the original list of strings.

Please implement `encode` and `decode`

**Example 1:**

```
Input: ["neet","code","love","you"]

Output:["neet","code","love","you"]
```

Copy

**Example 2:**

```
Input: ["we","say",":","yes"]

Output: ["we","say",":","yes"]
```

Copy

**Constraints:**

* `0 <= strs.length < 100`
* `0 <= strs[i].length < 200`
* `strs[i]` contains only UTF-8 characters.

</blockquote>

## Solution
```cpp
class Solution {
public:

    string encode(vector<string>& strs) {
        string res;
        for (auto &s : strs) {
            res += to_string(s.size()) + '#' + s;
        }
        return res;
    }

    vector<string> decode(string s) {
        vector<string> res;
        int i=0;
        while(i < s.size()) {
            int j = i;
            while(s[++j] != '#');
            int sz = stoi(s.substr(i,j-i));
            j += 1;
            res.push_back(s.substr(j,sz));
            i = j+sz;
        }
        return res;
    }
};
```
