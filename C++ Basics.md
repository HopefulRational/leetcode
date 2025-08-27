# C/C++ Basics

**Q1. Who calls `main()`?**  
Ans. `__libc_start_main()` (added to executable by C runtime)  

---
**Q2. `const int *ptr` variations**  
Ans. Read if from back(right to left) \[eg. `const int *ptr` is pointer to integer constant]

---
**Q3. How to have heterogeneous container in c++?**  
Ans. Use `std::variant`(type-fixed) and `std::any`(type-erased) -
```cpp
// using std::variant

#include <iostream>
#include <vector>
#include <variant>
#include <string>

int main() {
    std::vector<std::variant<int, std::string>> container;
    container.push_back(42);
    container.push_back("hello");

    for (const auto& item : container) {
        std::visit([](const auto& val) {
            std::cout << val << "\n";
        }, item);
    }
}
```
```cpp
// using std::any

#include <iostream>
#include <vector>
#include <any>
#include <string>

int main() {
    std::vector<std::any> container;
    container.push_back(42);
    container.push_back(std::string("hello"));

    for (const auto& item : container) {
        if (item.type() == typeid(int)) {
            std::cout << "int: " << std::any_cast<int>(item) << "\n";
        } else if (item.type() == typeid(std::string)) {
            std::cout << "string: " << std::any_cast<std::string>(item) << "\n";
        }
    }
}
```

---
**Q4. `std::advance(it)` vs `it += 3`?**
Ans. `it += 3` does not work with `std::list`, `std::set`.

---
**Q5. Find min and max using XOR**  
```cpp
min = a ^ ((a ^ b) & -(a > b));
max = b ^ ((a ^ b) & -(a > b));
```

---
**Q6. Overload `operator<<` for a class**  
Ans. Possible answers :
(i) `std::ostream` is from STL but we cant modify its class definition. So `operator<<`
```cpp
#include <iostream>
#include <string>
using namespace std;

class MyData {
    int number;
    string text;
    
public:
    MyData(int n , string &t) : number(n), text(t) {}
    
    // friend function to allow private member access
    firend ostream& operator<<(ostream &os, const MyData &obj);
};

ostream& operator<<(ostream &os, MyData &data) {
    os << "Number: " << obj.
};
os << "Number: " << obj.number << ", string: " << "\n";
```
The main reasons for friendship are:<br />
(a) Friendship lets `operator<<` access private membersdirectly for printing.<br />
(b) Since `std::ostream` is left operand, `operator<<` must be a non-member—friendship allows it work seamlessly.<br />

(ii) Since C++23, `std::formatter` can be speicialized for printing custom objects.
```cpp
#include <print>
#include <string>

class MyData {
    int id;
    std::string name;
public:
    MyData(int i, std::string n) : id(i), name(std::move(n)) {}
    
    friend struct std::formatter<MyData>;
};

// Specialize std::formatter without converting types
template <>
struct std::formatter<MyData> {
    constexpr auto parse(auto& ctx) { return ctx.begin(); }
    
    auto format(const MyData& obj, auto& ctx) {
        return std::format_to(ctx.out(), "MyData{{id: {}, name: \"{}\"}}", obj.id, obj.name);
    }
};

int main() {
    MyData obj(42, "hopeful");
    std::println("Object: {}", obj);
}
```

---
**Q7. What are different ways to overload a function/method?**  
Ans. Ways to overload a function or method:  
(a) Number of parameters  
(b) Type of parameters  
(c) Parameter order  
(d) `const` qualification (for member functions)  
(e) Reference vs pointer vs value  
```cpp
#include <bits/stdc++.h>
using namespace std;

int f(int&& x) { return 0; }       // for rvalues
int f(const int& x) { return 1; }  // for lvalues
int f(int* x) { return 2; }        // for pointer

int main() {
    int x = 10;
    cout << f(5) << "\n";    // 0
    cout << f(x) << "\n";    // 1
    cout << f(&x) << "\n";   // 2
    return 0;
}
```
(f) Lvalue/Rvalue reference  
(g) Default arguments (not technically overloading but simulates it)  
(h) Template specialization
```cpp
template<typename T>
void print(T);

template<>
void print(int);
```
(i) Return type (only with other differences)  
(j) Operator overloading (kind of overloading)  
(k) `const` vs non-`const` reference
```cpp
void show(const std::string& s); // read-only
void show(std::string& s);       // modifiable
```
(l) Reference qualifiers on member functions
```cpp
class MyClass {
public:
    std::string get() &;  // called for lvalue object
    std::string get() &&; // called for rvalue object
};
```

---
**Q8. Alignment of members in struct**  
Ans. Members are aligned based on the largest primitive type. Best way is to order from largest to smallest - this has all the data at the beginning and all/most of the padding at the end.<br />
Further, `#pragma pack(push, x)` and `#pragma pack(pop, x)` can be used for specific alignment.<br />

---
**Q9. IEEE 754 format**  
Ans.
|      Component      | Bits(Single Precision) | Bits(Double Precision) | Description                     |
|---------------------|------------------------|------------------------|---------------------------------|
| Sign                |      1                 |      1                 | 0 = +ve, 1 = -ve                |
| Exponent            |      8                 |      11                | Biased exponent                 |
| Fraction(Mantissa)  |      23                |      52                | Precision bits                  |
| Bias                |      127               |      1023              | to be subtracted from exponent  |

| Value Type             | Sign     |     Exponent | Fraction     | Meaning                              |
|------------------------|----------|--------------|--------------|--------------------------------------|
| Zero                   | 0 or 1   | All 0s       | All 0s       | +0 or -0                             |
| Subnormal              | 0 or 1   | All 0s       | ≠ 0          | Very small numbers close to zero     |
| Normal                 | 0 or 1   | 1 to 254     | Any          | Regular floating-point numbers       |
| Infinity               | 0 or 1   | All 1s       | All 0s       | +∞ or -∞                             |
| NaN (Quiet)            | 0 or 1   | All 1s       | ≠ 0 (MSB=1)  | Not a Number (e.g., 0/0)             |
| NaN (Signaling)        | 0 or 1   | All 1s       | ≠ 0 (MSB=0)  | Triggers exceptions in strict mode   |

---
**Q10. Overflow/underflow conditions for addition, subtraction etc. of `int`s.**  
Ans.
```cpp
bool will_add_overflow(int a, int b) {
    if(b > 0 && a > INT_MAX - b) return true; // overflow
    if(b < 0 && a < INT_MIN - b) return true; // underflow
}

bool will_sub_overflow(int a, int b) {
    if(b < 0 && a > INT_MAX + b) return true; // overflow
    if(b > 0 && a < INT_MIN + b) return true; // underflow
}

bool will_mul_overflow(int a, int b) {
    if(a == 0 || b == 0) return false;
    if(a == -1 && b == INT_MIN) return true;
    if(b == -1 && a == INT_MIN) return true;
    int result = a * b;
    return result / b != a;
}

bool will_div_overflow(int a, int b) {
    if(b == 0) return true;
    if(a == INT_MIN && b == -1) return true;
    return false;
}
```

---
**Q11. Difference between `fun(int arr[2])` and `fun(int* ptr)`**  
Ans. They are same because array parameters decay to pointers when passed to a function.<br />

---
**Q12. `fun(int& arr[2])` vs `fun(int&* ptr)`**  
Ans. Both are illegal<br />
| Syntax | Valid | Meaning |
|----------|----------|----------|
| int (&arr)\[2\] | Yes | Reference to array of 2 ints  |
| int& arr\[2\] | No | Array of two references (illegal) |
| int&* ptr | No | Pointer to reference (illegal) |

---
**Q13. How is `void*` different from pointer to fixed types?**  
Ans. `void*` can point to any type but no arithmetic is allowed. Dereferencing `void*` requires explicit casting.<br />

---
**Q14. Type-casting in c++.**  
Ans.
| Casting Method       | Purpose (What it Does) | Valid Uses (Examples) | Invalid Uses (Examples) | Key Notes |
|----------------------|-----------------------|----------------------|-------------------------|-----------|
| **`static_cast`**    | Compile-time safe conversions (e.g., numeric, base-to-derived). | ```int i = 10; double d = static_cast<double>(i); ``` | ```cpp char* p = static_cast<char*>(&i); // Invalid: unrelated pointers ``` | - No runtime checks. <br> - Avoids narrowing conversions. |
| **`dynamic_cast`**   | Runtime-safe downcasting (polymorphic types). | ```Base* b = new Derived(); Derived* d = dynamic_cast<Derived*>(b); ``` | ```cpp int* p = dynamic_cast<int*>(b); // Invalid: non-polymorphic type ``` | - Requires RTTI. <br> - Returns `nullptr` on failure. |
| **`const_cast`**     | Adds/removes `const` or `volatile`. | ```cpp const int x = 10; int* p = const_cast<int*>(&x); ``` | ```cpp const int x = 10; float* p = const_cast<float*>(&x); // Invalid: type mismatch ``` | - UB if modifying originally `const` data. |
| **`reinterpret_cast`** | Low-level bit reinterpretation (e.g., pointer-to-int). | ```cpp int i = 42; int* p = &i; uintptr_t addr = reinterpret_cast<uintptr_t>(p); ``` | ```cpp float f = 3.14f; int i = reinterpret_cast<int>(f); // Invalid: direct type punning ``` | - Unsafe, implementation-dependent. |
| **C-style cast `(T)expr`** | Forces conversion (uses `static_cast`/`const_cast`/`reinterpret_cast`). | ```cpp int i = (int)3.14; ``` | ```cpp const int x = 10; int* p = (int*)&x; // Dangerous: removes const ``` | - Avoid in C++. |
| **`std::bit_cast` (C++20)** | Type punning with defined behavior. | ```cpp float f = 3.14f; int i = std::bit_cast<int>(f); ``` | ```cpp int i = 10; float f = std::bit_cast<float>(i); // Invalid: sizes must match ``` | - Safe alternative to `reinterpret_cast`. |

---
**Q15. Creating a string `"abc"`**  
Ans. 
| Method | Allocation |
|--------|------------|
|`const char* str = "abc";`|text segment(.rodata)|
|`char str[] = "abc";`|Function stack|
|`string str = "abc";`|Heap|

---
    
    
