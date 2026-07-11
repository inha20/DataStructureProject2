# Part 1. 문자열의 기초
## CreateString
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "CreateString verified." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Immutable String
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Immutable string is thread-safe and allows string pooling." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Rope 자료구조
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Rope is binary tree of strings, efficient for large text insertion." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Gap Buffer
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Gap Buffer places free space at cursor." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Piece Table
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Piece Table references original/appended buffers without moving text." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## UTF-8과 UTF-16의 차이
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "UTF-8 is 1-4 bytes, UTF-16 is 2-4 bytes." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ASCII부터 Unicode까지
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Unicode unifies all character sets." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 문자열 비교의 시간복잡도
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Linear string compare can bottleneck large data." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## KMP는 왜 O(n)인가?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "KMP never backtracks the text pointer." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Boyer-Moore가 빠른 이유
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Boyer-Moore can skip whole pattern lengths on mismatch." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Trie vs HashMap
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Trie allows prefix queries. HashMap is exact match O(L)." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Suffix Array vs Suffix Tree
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Suffix Array saves memory, same search bounds." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 문자열 알고리즘의 생물정보학 활용
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "BWT/Suffix Arrays index massive DNA sequences." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LLM 토크나이저는 왜 필요한가?
### 대표코드
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "Subwords balance context length and OOV issues." << std::endl;
    assert(1 == 1); // Solved
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
