# Special Subarrays

**Difficulty:** Medium

**Topics:** Maths, Prefix Count

---

<blockquote>

<p>Given array of n integers, count the number of special subarrays and return the result. A special subarray is a subarray where the product of the elements has an odd number of divisors.</p>

</blockquote>

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
 
// --- Global state for primes ---
vector<int> primes;
unordered_map<int,int> primeIndex;
 
// -------- Sieve all primes up to maxVal --------
void sievePrimes(int maxVal) {
    vector<bool> sieve(maxVal+1, true);
 
    for (int i=2; i*i <= maxVal; ++i) {
        if (sieve[i]) {
            for (int j=i*i; j<=maxVal; j+=i) sieve[j] = false;
        }
    }
 
    for (int i=2; i<=maxVal; ++i) {
        if (sieve[i]) primes.push_back(i);
    }
 
    for (int i=0; i<primes.size(); ++i) {
        primeIndex[primes[i]] = i;
    }
}
 
// -------- Factorize number into parity mask --------
vector<int> factorMask(int x) {
    vector<int> mask(primes.size(), 0);
 
    for (int p : primes) {
        if (1LL * p * p > x) break;
        int cnt = 0;
        while (x % p == 0) {
            x /= p;
            cnt ^= 1; // only track odd/even exponent
        }
        if (cnt) mask[primeIndex[p]] = 1;
    }
    if (x > 1) {
        // x itself is prime, guaranteed in primes due to full sieve
        mask[primeIndex[x]] = 1;
    }
    return mask;
}
 
// -------- Count special subarrays --------
long long countSpecialSubarrays(const vector<int>& nums) {
    int maxVal = *max_element(nums.begin(), nums.end());
    sievePrimes(maxVal);
 
    unordered_map<string,long long> prefixCount;
    string current(primes.size(), '0');
    prefixCount[current] = 1; // empty prefix
 
    long long result = 0;
 
    for (int x : nums) {
        vector<int> mask = factorMask(x);
 
        for (int i=0; i<mask.size(); ++i) {
            if (mask[i]) current[i] = (current[i] == '0' ? '1' : '0');
        }
 
        result += prefixCount[current];
        prefixCount[current]++;
    }
    return result;
}
 
// -------- Main --------
int main() {
    vector<int> nums = {2, 4, 16}; // example
    cout << countSpecialSubarrays(nums) << "\n";
    return 0;
}
```
