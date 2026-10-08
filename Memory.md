# Part 1. 메모리의 기초
## CreateMemory()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <cassert>

// 메모리는 "주소로 번호가 매겨진 바이트의 배열" 이다.  시뮬레이션: 범위를 검사하는 바이트 배열 + 여러 바이트 값의 읽기/쓰기.
// 정수를 바이트로 나눌 때 낮은 자리 바이트를 낮은 주소에 놓는 방식이 리틀 엔디언(x86, ARM 기본), 반대가 빅 엔디언(네트워크 바이트 순서)
class Memory {
    std::vector<uint8_t> bytes;
public:
    explicit Memory(size_t size) : bytes(size, 0) {}
    size_t size() const { return bytes.size(); }
    uint8_t read8(size_t addr) const { if (addr >= bytes.size()) throw std::out_of_range("segfault"); return bytes[addr]; }
    void write8(size_t addr, uint8_t v) { if (addr >= bytes.size()) throw std::out_of_range("segfault"); bytes[addr] = v; }
    void write32(size_t addr, uint32_t v) { for (int i = 0; i < 4; i++) write8(addr + i, (v >> (8 * i)) & 0xff); }   // 리틀 엔디언으로 저장
    uint32_t read32(size_t addr) const { uint32_t v = 0; for (int i = 0; i < 4; i++) v |= (uint32_t)read8(addr + i) << (8 * i); return v; }
};

int main() {
    Memory m(64);
    m.write32(8, 0x11223344);
    assert(m.read8(8) == 0x44 && m.read8(9) == 0x33 && m.read8(11) == 0x11);      // 낮은 주소에 낮은 자리 바이트
    assert(m.read32(8) == 0x11223344);
    bool trapped = false;
    try { m.read8(64); } catch (const std::out_of_range&) { trapped = true; }    // 범위 밖 접근은 "세그멘테이션 오류"
    assert(trapped);
    uint32_t probe = 1; uint8_t first; std::memcpy(&first, &probe, 1);          // 실제 기계의 엔디언 확인
    std::cout << "CreateMemory: this machine is " << (first == 1 ? "little" : "big") << "-endian" << std::endl;
    return 0;
}
// Time Complexity: 접근 O(1)
// Space Complexity: O(size)
```
## Alignment()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <cassert>

// 정렬(alignment): 크기 N 인 자료형은 N 의 배수 주소에 놓는 것이 원칙이다 (CPU 가 한 번에 읽는 단위와 캐시 라인에 맞추기 위해).
// alignUp(a, N) = (a + N - 1) & ~(N - 1)   (N 은 2의 거듭제곱)
uintptr_t alignUp(uintptr_t addr, size_t a) { return (addr + a - 1) & ~(uintptr_t)(a - 1); }
bool isAligned(const void* p, size_t a) { return (reinterpret_cast<uintptr_t>(p) & (a - 1)) == 0; }

int main() {
    assert(alignUp(13, 8) == 16 && alignUp(16, 8) == 16 && alignUp(0, 64) == 0 && alignUp(65, 64) == 128);
    assert(alignof(int) == 4 && alignof(double) == 8 && alignof(char) == 1);
    alignas(64) char line[64];
    assert(isAligned(line, 64));                                      // alignas 로 캐시 라인 경계에 맞춘다
    int x; assert(isAligned(&x, alignof(int)));
    // std::align: 버퍼 안에서 요구 정렬을 만족하는 첫 주소를 찾는다
    char buf[100]; void* p = buf; size_t space = sizeof(buf);
    void* aligned = std::align(32, 10, p, space);
    assert(aligned && isAligned(aligned, 32) && space <= sizeof(buf));
    // 정렬이 맞지 않는 읽기는 memcpy 로 안전하게 (직접 캐스팅하면 일부 CPU 에서 오류, C++ 에서는 정의되지 않은 동작)
    unsigned char raw[8] = {0, 1, 0, 0, 0, 0, 0, 0}; uint32_t v; std::memcpy(&v, raw + 1, 4);
    assert(v == 1 || v == 0x01000000u);                               // 바이트 {1,0,0,0}: 리틀 엔디언이면 1, 빅 엔디언이면 0x01000000
    std::cout << "Alignment verified: alignUp(13,8) = " << alignUp(13, 8) << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Padding()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <cassert>

// 패딩: 각 멤버를 자신의 정렬에 맞추려고 컴파일러가 사이에 빈 바이트를 끼운다.  구조체 전체 크기는 가장 큰 정렬의 배수가 된다.
// 멤버를 큰 것부터 배치하면 패딩이 줄어든다.  #pragma pack 은 패딩을 없애지만 정렬되지 않은 접근 비용을 치른다
struct Bad  { char a; int64_t b; char c; };          // a(1) + 7 패딩 + b(8) + c(1) + 7 패딩 = 24
struct Good { int64_t b; char a; char c; };          // b(8) + a(1) + c(1) + 6 패딩 = 16
#pragma pack(push, 1)
struct Packed { char a; int64_t b; char c; };        // 패딩 없음 = 10
#pragma pack(pop)

int main() {
    assert(offsetof(Bad, b) == 8 && offsetof(Bad, c) == 16);
    assert(sizeof(Bad) == 24 && sizeof(Good) == 16 && sizeof(Packed) == 10);
    assert(sizeof(Good) % alignof(Good) == 0);
    assert(offsetof(Good, a) == 8 && offsetof(Good, c) == 9);
    std::cout << "sizeof: Bad=" << sizeof(Bad) << " Good=" << sizeof(Good) << " Packed=" << sizeof(Packed)
              << " (padding saved by reordering: " << sizeof(Bad) - sizeof(Good) << " bytes)" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## MemoryDump()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstdio>
#include <string>
#include <cassert>

// 메모리 덤프: 주소, 16진수 바이트, 오른쪽에 출력 가능한 ASCII 를 보여 주는 hexdump -C 형식.  디버깅과 바이너리 분석의 기본 도구
std::string hexdump(const void* data, size_t n) {
    const unsigned char* p = (const unsigned char*)data; std::string out; char buf[16];
    for (size_t off = 0; off < n; off += 16) {
        std::snprintf(buf, sizeof buf, "%08zx  ", off); out += buf;
        for (size_t i = 0; i < 16; i++) {
            if (off + i < n) { std::snprintf(buf, sizeof buf, "%02x ", p[off + i]); out += buf; } else out += "   ";
            if (i == 7) out += " ";
        }
        out += " |";
        for (size_t i = 0; i < 16 && off + i < n; i++) out += (p[off + i] >= 32 && p[off + i] < 127) ? (char)p[off + i] : '.';
        out += "|\n";
    }
    return out;
}

int main() {
    const char text[] = "Hello, memory!\n";
    std::string dump = hexdump(text, sizeof(text) - 1);
    assert(dump == "00000000  48 65 6c 6c 6f 2c 20 6d  65 6d 6f 72 79 21 0a     |Hello, memory!.|\n");
    uint32_t v = 0x11223344; std::string d2 = hexdump(&v, 4);          // 정수의 바이트 배치 (리틀 엔디언이면 44 33 22 11)
    assert(d2.find("44 33 22 11") != std::string::npos || d2.find("11 22 33 44") != std::string::npos);
    std::cout << dump;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n)
```
# Part 2. 프로세스 메모리
## TextSegment()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <cassert>

// 텍스트(코드) 세그먼트: 컴파일된 기계어가 들어 있는 읽기+실행 전용 영역.  함수의 주소가 여기에 속하고, 문자열 리터럴은 인접한 읽기 전용 영역(.rodata)에 놓인다.
// 프로세스 주소 공간(낮은 주소 -> 높은 주소): 코드 < 읽기 전용 데이터 < 초기화된 전역(.data) < 초기화 안 된 전역(.bss) < 힙(위로 성장) ... 스택(아래로 성장)
int initialized = 7;
int uninitialized;
void someFunction() {}

int main() {
    const char* literal = "string literal";
    int local = 0;
    int* heap = new int(1);
    uintptr_t code = (uintptr_t)(void*)&someFunction, ro = (uintptr_t)literal, data = (uintptr_t)&initialized, bss = (uintptr_t)&uninitialized;
    uintptr_t hp = (uintptr_t)heap, stack = (uintptr_t)&local;
    std::cout << std::hex << "text=" << code << " rodata=" << ro << " data=" << data << " bss=" << bss << " heap=" << hp << " stack=" << stack << std::endl;
#if defined(__linux__) && defined(__x86_64__)
    assert(stack > hp);                                    // 스택은 힙보다 높은 주소
    assert(hp > bss && hp > data);                         // 힙은 전역 데이터 위에서 시작
    assert(code < hp && ro < hp);                          // 코드·상수는 힙보다 아래
#endif
    assert(std::strcmp(literal, "string literal") == 0);   // 리터럴 읽기는 가능 (쓰기는 정의되지 않은 동작)
    delete heap;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DataSegment()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cassert>

// 데이터 세그먼트: 정적 저장 기간(static storage duration) 변수가 사는 곳.
//  .data = 0 이 아닌 초기값이 있는 전역/static (초기값이 실행 파일에 저장됨)
//  .bss  = 초기값이 없거나 0 인 전역/static (실행 파일에는 크기만 기록되고 로드될 때 0 으로 채워진다)
// 그래서 큰 배열을 전역으로 선언해도 실행 파일 크기는 거의 늘지 않는다.  static 지역 변수도 여기에 있어 호출 사이에 값이 유지된다
int withValue = 42;                 // .data
int zeroed[1000000];                // .bss: 4MB 인데 파일에는 저장되지 않음
static int counter;                 // .bss, 이 파일에서만 보임

int nextId() { static int id = 100; return id++; }       // static 지역: 첫 호출 때 한 번 초기화

int main() {
    assert(withValue == 42);
    for (int i = 0; i < 1000000; i += 99999) assert(zeroed[i] == 0);   // 전부 0 으로 시작 (보장됨)
    assert(counter == 0);
    assert(nextId() == 100 && nextId() == 101 && nextId() == 102);     // 호출 사이에 값 유지
    zeroed[5] = 9; counter++;
    assert(zeroed[5] == 9 && counter == 1);
    std::cout << "DataSegment: zero-initialized bss array of " << sizeof(zeroed) / 1024 << " KB" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: bss 는 실행 파일 크기에 영향 없음
```
## EnvironmentVariable()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <string>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
extern char** environ;
#endif

// 환경 변수: 프로세스가 시작될 때 부모로부터 "NAME=value" 문자열 배열로 복사받는다 (스택의 맨 위쪽에 놓인다).
// getenv/setenv 는 이 배열을 읽고 고친다.  fork 한 자식은 부모의 환경을 그대로 물려받는다
int main() {
    assert(std::getenv("DS_PROJECT_DEMO") == nullptr);
#if defined(__unix__) || defined(__APPLE__)
    setenv("DS_PROJECT_DEMO", "hello", 1);
    assert(std::string(std::getenv("DS_PROJECT_DEMO")) == "hello");
    bool found = false;
    for (char** e = environ; *e; e++) if (std::strcmp(*e, "DS_PROJECT_DEMO=hello") == 0) found = true;   // 배열에 "NAME=value" 로 들어 있다
    assert(found);
    setenv("DS_PROJECT_DEMO", "world", 0);                          // overwrite=0: 이미 있으면 바꾸지 않는다
    assert(std::string(std::getenv("DS_PROJECT_DEMO")) == "hello");
    unsetenv("DS_PROJECT_DEMO");
    assert(std::getenv("DS_PROJECT_DEMO") == nullptr);
#endif
    std::cout << "EnvironmentVariable verified." << std::endl;
    return 0;
}
// Time Complexity: getenv O(환경 변수 수)
// Space Complexity: O(환경 크기)
```
## CommandLineArgument()
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 명령줄 인자: main(int argc, char* argv[]).  argv[0] 은 프로그램 이름, argv[argc] 는 항상 nullptr.
// 문자열들은 환경 변수와 함께 스택 맨 위쪽에 연속으로 놓여 있다.  관례: "--key value" 와 "--flag"
std::map<std::string, std::string> parse(const std::vector<std::string>& args) {
    std::map<std::string, std::string> opt;
    for (size_t i = 0; i < args.size(); i++) {
        if (args[i].rfind("--", 0) != 0) continue;
        std::string key = args[i].substr(2);
        if (i + 1 < args.size() && args[i + 1].rfind("--", 0) != 0) opt[key] = args[++i]; else opt[key] = "true";
    }
    return opt;
}

int main(int argc, char* argv[]) {
    assert(argc >= 1 && argv[0] != nullptr);
    assert(argv[argc] == nullptr);                                    // 배열은 널 포인터로 끝난다
    auto o = parse({"--name", "kim", "--verbose", "--count", "3", "file.txt"});
    assert(o["name"] == "kim" && o["verbose"] == "true" && o["count"] == "3" && o.count("file.txt") == 0);
    std::cout << "CommandLineArgument: argc=" << argc << " program=" << argv[0] << std::endl;
    return 0;
}
// Time Complexity: O(인자 수)
// Space Complexity: O(인자 수)
```
# Part 3. 스택 메모리
## PushFrame()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 함수 호출 한 번이 스택에 "프레임" 을 쌓는 과정(호출 규약 요약): 인자 -> 복귀 주소 -> 이전 프레임 포인터(BP) -> 지역 변수.
// 스택은 높은 주소에서 낮은 주소로 자란다 (x86).  시뮬레이션: 8바이트 단위 메모리 위에서 SP 를 내리며 프레임을 만든다
struct Machine {
    std::vector<uint64_t> mem; size_t sp, bp;                          // 인덱스 = 주소 (낮은 주소 = 작은 인덱스)
    explicit Machine(size_t words) : mem(words, 0), sp(words), bp(words) {}
    void push(uint64_t v) { assert(sp > 0); mem[--sp] = v; }
    void pushFrame(uint64_t returnAddr, size_t localWords) {
        push(returnAddr);                                              // call 명령이 복귀 주소를 쌓는다
        push(bp); bp = sp;                                             // 이전 BP 저장, 새 BP = 현재 SP
        sp -= localWords;                                              // 지역 변수 공간 확보
    }
};

int main() {
    Machine m(64);
    size_t top = m.sp;
    m.push(11); m.push(22);                                            // 인자 두 개 (오른쪽부터)
    size_t argTop = m.sp;
    m.pushFrame(0xDEADBEEF, 3);
    assert(m.sp < argTop && m.sp < top);                              // 스택 포인터는 내려갔다 (스택은 아래로 성장)
    assert(m.mem[m.bp + 1] == 0xDEADBEEF);                            // BP 바로 위에 복귀 주소
    assert(m.mem[m.bp] == 64);                                        // BP 위치에 이전 BP (첫 프레임이라 맨 위)
    assert(m.mem[m.bp + 2] == 22 && m.mem[m.bp + 3] == 11);           // 그 위에 인자
    assert(m.bp - m.sp == 3);                                         // 지역 변수 3칸
    std::cout << "PushFrame: SP moved down by " << top - m.sp << " words" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(프레임 크기)
```
## PopFrame()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 프레임 제거(함수 반환): SP 를 BP 로 올려 지역 변수를 버리고(leave), 이전 BP 를 복원하고, 복귀 주소로 점프한다(ret).
// 지역 변수가 "사라지는" 것은 SP 만 올리면 되기 때문이며 값 자체는 메모리에 남아 있다 (그래서 반환된 지역 변수의 주소는 위험하다)
struct Machine {
    std::vector<uint64_t> mem; size_t sp, bp;
    explicit Machine(size_t words) : mem(words, 0), sp(words), bp(words) {}
    void push(uint64_t v) { mem[--sp] = v; }
    uint64_t pop() { return mem[sp++]; }
    void pushFrame(uint64_t ret, size_t locals) { push(ret); push(bp); bp = sp; sp -= locals; }
    uint64_t popFrame() {
        sp = bp;                                                       // leave: 지역 변수 영역 해제
        bp = pop();                                                    // 이전 BP 복원
        return pop();                                                  // ret: 복귀 주소
    }
};

int main() {
    Machine m(64);
    m.pushFrame(0x1111, 2); m.mem[m.bp - 1] = 777;                    // 바깥 함수의 지역 변수
    size_t outerBp = m.bp;
    m.pushFrame(0x2222, 4);                                            // 안쪽 호출
    assert(m.popFrame() == 0x2222 && m.bp == outerBp);                // 안쪽 반환: 바깥 프레임이 그대로 복원
    assert(m.mem[m.bp - 1] == 777);
    assert(m.popFrame() == 0x1111 && m.sp == 64 && m.bp == 64);       // 바깥 반환: 스택이 비었다 (후입선출)
    std::cout << "PopFrame verified: LIFO frame discipline." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## CallFunction()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 호출 과정을 명시적인 스택 기계로 흉내 낸다.  재귀 factorial(n) 의 모든 호출이 "인자 push -> call -> 결과 반환 -> 인자 pop" 순서를 지킨다.
// 최대 스택 깊이 = 재귀 깊이: 호출이 중첩될수록 프레임이 쌓인다
struct Frame { int n; int pc; };                                       // pc: 0 = 진입, 1 = 재귀 호출에서 돌아옴
long long factorial(int n, size_t& maxDepth) {
    std::vector<Frame> stack; stack.push_back({n, 0});
    long long ret = 0;                                                  // "rax" 레지스터
    maxDepth = 1;
    while (!stack.empty()) {
        Frame& f = stack.back();
        if (f.pc == 0) {
            if (f.n <= 1) { ret = 1; stack.pop_back(); }                // 기저: 반환값 1
            else { f.pc = 1; stack.push_back({f.n - 1, 0}); maxDepth = std::max(maxDepth, stack.size()); }   // call factorial(n-1)
        } else { ret = f.n * ret; stack.pop_back(); }                  // 반환값을 받아 곱하고 반환
    }
    return ret;
}

int main() {
    size_t depth;
    assert(factorial(5, depth) == 120 && depth == 5);                  // factorial(5): 프레임이 5개까지 쌓였다
    assert(factorial(1, depth) == 1 && depth == 1);
    assert(factorial(20, depth) == 2432902008176640000LL && depth == 20);
    std::cout << "CallFunction: factorial(20) used stack depth " << depth << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: O(n) 스택
```
## ReturnFunction()
### 대표코드
```cpp
#include <iostream>
#include <cassert>

// 반환 방식: 작은 값은 레지스터(rax)로, 큰 구조체는 호출자가 마련한 공간의 주소를 숨은 인자(sret)로 넘겨 거기에 직접 만든다.
// C++17 부터 순수 우측값(prvalue) 반환은 복사·이동이 아예 일어나지 않는다 (보장된 복사 생략).  이름 있는 지역 변수 반환은 NRVO(허용, 보장은 아님)
struct Tracked {
    static int copies, moves;
    int v = 0;
    explicit Tracked(int x) : v(x) {}
    Tracked(const Tracked& o) : v(o.v) { copies++; }
    Tracked(Tracked&& o) noexcept : v(o.v) { moves++; }
};
int Tracked::copies = 0, Tracked::moves = 0;

Tracked makePrvalue() { return Tracked(7); }                           // 보장된 생략
Tracked makeNamed()   { Tracked t(8); return t; }                      // NRVO (이동은 허용)
Tracked&& badRef()    { static Tracked t(9); return std::move(t); }    // 참고: 지역 객체의 참조를 반환하면 안 된다

int main() {
    Tracked a = makePrvalue();
    assert(a.v == 7 && Tracked::copies == 0 && Tracked::moves == 0);   // 복사도 이동도 없다
    Tracked b = makeNamed();
    assert(b.v == 8 && Tracked::copies == 0);                           // 복사는 없다 (NRVO 거나 이동)
    std::cout << "ReturnFunction: copies=" << Tracked::copies << " moves=" << Tracked::moves << std::endl;
    (void)badRef;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## LocalVariable()
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// 지역 변수(자동 저장 기간): 선언 시점에 만들어지고 블록을 벗어날 때 "생성의 역순" 으로 소멸한다 -> RAII 의 토대.
// 스택에 있으므로 할당·해제가 SP 이동뿐이라 빠르지만, 블록이 끝나면 그 주소는 더 이상 유효하지 않다
std::vector<std::string> log;
struct Guard { std::string name; explicit Guard(std::string n) : name(std::move(n)) { log.push_back("+" + name); } ~Guard() { log.push_back("-" + name); } };

void f() {
    Guard a("a");
    {
        Guard b("b");
        Guard c("c");
    }                                       // c, b 순으로 소멸
    Guard d("d");
}                                           // d, a 순으로 소멸

int main() {
    f();
    assert((log == std::vector<std::string>{"+a", "+b", "+c", "-c", "-b", "+d", "-d", "-a"}));   // 생성 순서의 정확한 역순
    int outer = 1;
    int* p = nullptr;
    { int inner = 2; p = &inner; assert(*p == 2); }                      // 블록 안에서는 유효
    (void)outer; (void)p;                                                // 블록 밖에서 *p 를 읽으면 정의되지 않은 동작(댕글링)
    std::cout << "LocalVariable: destruction order is the reverse of construction." << std::endl;
    return 0;
}
// Time Complexity: O(1) 할당/해제
// Space Complexity: O(스코프 깊이)
```
## StackFrame()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cassert>

// 스택 프레임(요약, 정본은 Stack.md Part 8): 함수 호출마다 프레임이 하나씩 쌓이고, 호출된 함수의 프레임은 더 낮은 주소에 놓인다.
// __builtin_frame_address(0) 으로 현재 프레임의 주소를 얻어 확인할 수 있다 (GCC/Clang)
__attribute__((noinline)) uintptr_t frameAddr() { return (uintptr_t)__builtin_frame_address(0); }
__attribute__((noinline)) uintptr_t nested(int depth) { return depth == 0 ? frameAddr() : nested(depth - 1); }

int main() {
    uintptr_t outer = (uintptr_t)__builtin_frame_address(0);
    uintptr_t inner = frameAddr();
    assert(inner < outer);                                              // 호출된 함수의 프레임이 더 낮은 주소
    uintptr_t deeper = nested(10);
    assert(deeper < inner);                                             // 호출이 깊어질수록 더 낮아진다
    std::cout << "StackFrame: frames grow downward, 10 calls = " << (inner - deeper) << " bytes" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## StackOverflow()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <sys/resource.h>
#endif

// 스택 오버플로(요약, 정본은 Stack.md Part 10): 스택은 크기가 정해져 있다(보통 8MB).  재귀가 너무 깊거나 지역 배열이 너무 크면 한계를 넘어 세그멘테이션 오류.
// 안전하게 보는 법: 한도(getrlimit)와 프레임 한 개의 크기를 재서 "최대 재귀 깊이" 를 예측하고, 그 절반만 실제로 재귀해 본다
__attribute__((noinline)) uintptr_t probe(int d, volatile char* pad) {
    volatile char frame[128]; frame[0] = (char)d; (void)pad;
    return d == 0 ? (uintptr_t)&frame[0] : probe(d - 1, frame);
}
__attribute__((noinline)) long depthSum(long d) { volatile char pad[64]; pad[0] = 1; return d == 0 ? 0 : d + depthSum(d - 1) + pad[0] - 1; }

int main() {
    uintptr_t a = probe(0, nullptr), b = probe(100, nullptr);
    size_t perFrame = (a - b) / 100;
    assert(perFrame >= 128 && perFrame < 1024);                         // 프레임 하나가 차지하는 바이트
#if defined(__unix__) || defined(__APPLE__)
    struct rlimit rl; getrlimit(RLIMIT_STACK, &rl);
    size_t limit = rl.rlim_cur == RLIM_INFINITY ? (8u << 20) : rl.rlim_cur;
    size_t maxDepth = limit / perFrame;
    assert(maxDepth > 1000);
    long safe = (long)std::min<size_t>(maxDepth / 4, 20000);
    assert(depthSum(safe) == safe * (safe + 1) / 2);                    // 한도의 일부만 쓰면 안전
    std::cout << "StackOverflow: limit " << limit / 1024 << " KB, ~" << perFrame << " B/frame -> max depth ~" << maxDepth << std::endl;
#endif
    return 0;
}
// Time Complexity: O(깊이)
// Space Complexity: O(깊이) 스택
```
## TailCallOptimization()
### 대표코드
```cpp
#include <iostream>
#include <functional>
#include <variant>
#include <cassert>

// 꼬리 호출 최적화(TCO): 함수의 마지막 동작이 다른 (또는 자기 자신의) 호출이면 현재 프레임이 더 이상 필요 없으므로 새 프레임 없이 "점프" 로 바꿀 수 있다 -> 재귀가 반복문과 같은 공간 O(1).
// C++ 표준은 TCO 를 보장하지 않는다 (-O2 에서는 대개 적용되지만 디버그 빌드에서는 안 된다).  보장이 필요하면 트램펄린(trampoline)으로 직접 구현한다
long long sumTail(long long n, long long acc) { return n == 0 ? acc : sumTail(n - 1, acc + n); }       // 꼬리 재귀 (마지막이 자기 호출)
long long sumNonTail(long long n) { return n == 0 ? 0 : n + sumNonTail(n - 1); }                         // 호출 뒤에 덧셈이 남아 꼬리 호출이 아님

// 트램펄린: 재귀 호출 대신 "다음에 할 일" 을 반환하고, 반복문이 그것을 이어서 실행한다 -> 스택이 쌓이지 않는다
struct Step;
typedef std::function<Step()> Thunk;
struct Step { bool done; long long value; Thunk next; };
Step sumStep(long long n, long long acc) {
    if (n == 0) return {true, acc, nullptr};
    return {false, 0, [=] { return sumStep(n - 1, acc + n); }};
}
long long run(Step s) { while (!s.done) s = s.next(); return s.value; }

int main() {
    assert(sumTail(1000, 0) == 500500 && sumNonTail(1000) == 500500);
    assert(run(sumStep(1000000, 0)) == 500000500000LL);               // 백만 단계도 스택 오버플로 없이 (고정된 스택 사용)
    long long loop = 0; for (long long i = 1; i <= 1000000; i++) loop += i;     // 꼬리 재귀 == 반복문
    assert(loop == 500000500000LL);
    std::cout << "TailCallOptimization: trampoline summed 1e6 without growing the stack." << std::endl;
    return 0;
}
// Time Complexity: O(n)
// Space Complexity: 트램펄린 O(1), 일반 재귀 O(n)
```
# Part 4. 힙 메모리
## malloc()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>
#include <cassert>

// malloc 의 핵심 동작을 작은 힙 위에서 단계별로 본다 (first-fit, 분할, 병합).
//   1) 할당 가능한 블록 탐색  2) 필요한 만큼 분할  3) 헤더(크기·사용 여부) 기록  4) 사용자 포인터 = 헤더 바로 뒤
//   free: 사용 표시를 지우고 이웃한 빈 블록과 병합해 단편화를 줄인다
struct Header { size_t size; bool used; };                             // 사용자 영역 크기, 사용 중 여부
class Heap {
    std::vector<uint8_t> mem;
    Header* hdr(size_t off) { return (Header*)&mem[off]; }
    static size_t round8(size_t n) { return (n + 7) & ~size_t(7); }
public:
    explicit Heap(size_t bytes) : mem(bytes) { *hdr(0) = Header{bytes - sizeof(Header), false}; }
    void* alloc(size_t n) {
        n = round8(n);
        for (size_t off = 0; off < mem.size(); off += sizeof(Header) + hdr(off)->size) {       // 1) 첫 번째로 맞는 블록
            Header* h = hdr(off);
            if (h->used || h->size < n) continue;
            if (h->size >= n + sizeof(Header) + 8) {                                           // 2) 남는 부분을 새 빈 블록으로 분할
                *hdr(off + sizeof(Header) + n) = Header{h->size - n - sizeof(Header), false};
                h->size = n;
            }
            h->used = true;                                                                     // 3) 사용 중으로 표시
            return &mem[off + sizeof(Header)];                                                  // 4) 사용자 포인터
        }
        return nullptr;
    }
    void release(void* p) {
        size_t off = (uint8_t*)p - &mem[0] - sizeof(Header);
        hdr(off)->used = false;
        for (size_t o = 0; o < mem.size();) {                                                   // 인접한 빈 블록 병합
            Header* h = hdr(o); size_t next = o + sizeof(Header) + h->size;
            if (!h->used && next < mem.size() && !hdr(next)->used) h->size += sizeof(Header) + hdr(next)->size; else o = next;
        }
    }
    size_t blocks() { size_t c = 0; for (size_t o = 0; o < mem.size(); o += sizeof(Header) + hdr(o)->size) c++; return c; }
    size_t largestFree() { size_t m = 0; for (size_t o = 0; o < mem.size(); o += sizeof(Header) + hdr(o)->size) if (!hdr(o)->used) m = std::max(m, hdr(o)->size); return m; }
};

int main() {
    Heap h(1024);
    size_t total = h.largestFree();
    void *a = h.alloc(100), *b = h.alloc(200), *c = h.alloc(50);
    assert(a && b && c && a < b && b < c);                             // 주소가 순서대로 배치
    assert(h.blocks() == 4);                                           // a, b, c, 나머지 빈 블록
    h.release(b);                                                       // 가운데 해제 -> 구멍
    void* d = h.alloc(150);
    assert(d == b);                                                    // 구멍을 재사용 (b 의 자리)
    h.release(a); h.release(d); h.release(c);                          // 전부 해제하면 인접 블록이 병합되어
    assert(h.blocks() == 1 && h.largestFree() == total);               // 처음의 하나짜리 큰 블록으로 돌아온다
    assert(h.alloc(5000) == nullptr);                                  // 너무 큰 요청은 실패
    std::cout << "malloc simulation: split, reuse and coalesce verified." << std::endl;
    return 0;
}
// Time Complexity: 할당 O(블록 수) (first-fit), 해제 O(블록 수) (병합 포함)
// Space Complexity: 블록당 헤더 16B
```
## new()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <new>
#include <vector>
#include <cassert>

// new 연산자 = (1) operator new 로 메모리 확보 + (2) 생성자 호출.   delete = (1) 소멸자 호출 + (2) operator delete 로 반환.
// new[] 는 소멸자를 원소마다 불러야 하므로 개수를 메모리 앞쪽에 따로 기록한다(cookie).  할당 실패 시 new 는 bad_alloc 을 던지고 nothrow new 는 nullptr 를 돌려준다
static int allocs = 0, frees = 0;
void* operator new(size_t n) { allocs++; void* p = std::malloc(n); if (!p) throw std::bad_alloc(); return p; }
void operator delete(void* p) noexcept { if (p) frees++; std::free(p); }
void operator delete(void* p, size_t) noexcept { if (p) frees++; std::free(p); }
void* operator new[](size_t n) { allocs++; void* p = std::malloc(n); if (!p) throw std::bad_alloc(); return p; }
void operator delete[](void* p) noexcept { if (p) frees++; std::free(p); }
void operator delete[](void* p, size_t) noexcept { if (p) frees++; std::free(p); }

struct Obj { static int alive; Obj() { alive++; } ~Obj() { alive--; } };
int Obj::alive = 0;

int main() {
    int baseAllocs = allocs, baseFrees = frees;
    Obj* o = new Obj;                                                  // operator new 1번 + 생성자 1번
    assert(allocs == baseAllocs + 1 && Obj::alive == 1);
    delete o;                                                           // 소멸자 + operator delete
    assert(frees == baseFrees + 1 && Obj::alive == 0);
    Obj* arr = new Obj[5];                                              // operator new[] 1번, 생성자 5번
    assert(Obj::alive == 5);
    delete[] arr;                                                       // 소멸자 5번
    assert(Obj::alive == 0);
    bool threw = false;
    volatile size_t huge = (size_t)-1 / 2;                             // 컴파일러가 상수로 판단하지 못하게 volatile
    try { new char[huge]; } catch (const std::bad_alloc&) { threw = true; }
    assert(threw);                                                      // 실패 -> 예외
    assert(new (std::nothrow) char[huge] == nullptr);                  // 실패 -> nullptr
    std::cout << "new/delete: allocs=" << allocs << " frees=" << frees << std::endl;
    return 0;
}
// Time Complexity: 할당기에 따라 다름 (평균 O(1))
// Space Complexity: O(n)
```
## PlacementNew()
### 대표코드
```cpp
#include <iostream>
#include <new>
#include <string>
#include <vector>
#include <cassert>

// 배치 new: 이미 확보한 메모리 위치에 객체만 생성한다 (new (주소) T(...)).  메모리 풀·아레나·컨테이너(std::vector 의 내부)의 기초.
// 소멸은 delete 가 아니라 소멸자를 직접 호출해야 하며, 메모리 해제는 별도로 한다
std::vector<std::string> events;
struct Widget {
    int id;
    explicit Widget(int i) : id(i) { events.push_back("ctor" + std::to_string(i)); }
    ~Widget() { events.push_back("dtor" + std::to_string(id)); }
};

int main() {
    alignas(16) unsigned char buffer[64];                              // 정렬을 맞춘 원시 메모리 (객체 없음)
    static_assert(sizeof(Widget) * 2 <= sizeof(buffer) && sizeof(std::string) <= sizeof(buffer), "buffer too small");
    Widget* w0 = new (buffer + 0 * sizeof(Widget)) Widget(0);          // 지정한 주소에 생성
    Widget* w1 = new (buffer + 1 * sizeof(Widget)) Widget(1);
    assert((void*)w0 == (void*)buffer && (void*)w1 == (void*)(buffer + sizeof(Widget)));   // 새 할당 없이 같은 주소
    assert(w0->id == 0 && w1->id == 1);
    w1->~Widget(); w0->~Widget();                                       // 소멸자는 직접 호출 (역순으로)
    assert((events == std::vector<std::string>{"ctor0", "ctor1", "dtor1", "dtor0"}));
    std::string* s = new (buffer) std::string("reused");               // 같은 버퍼를 다른 타입으로 재사용
    assert(*s == "reused");
    s->~basic_string();
    std::cout << "PlacementNew verified." << std::endl;
    return 0;
}
// Time Complexity: O(생성자)
// Space Complexity: O(1) 추가 할당 없음
```
# Part 5. 포인터와 참조
## Pointer()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cassert>

// 포인터: 다른 객체의 주소를 값으로 갖는 변수.  p + 1 은 "다음 바이트" 가 아니라 "다음 원소"(sizeof(T) 바이트 뒤).
// 배열 이름은 첫 원소의 포인터로 변환(decay)된다.  포인터의 포인터, const 의 위치, nullptr 이 핵심 어휘
int main() {
    int a[5] = {10, 20, 30, 40, 50};
    int* p = a;                                                       // decay: &a[0]
    assert(*p == 10 && *(p + 2) == 30 && p[3] == 40);                 // p[i] == *(p + i)
    assert((char*)(p + 1) - (char*)p == sizeof(int));                // +1 은 sizeof(int) 바이트
    assert(&a[4] - &a[1] == 3);                                       // 포인터 뺄셈 = 원소 개수 차이
    int** pp = &p; **pp = 99; assert(a[0] == 99);                     // 포인터의 포인터로 원본을 바꾼다

    int x = 1, y = 2;
    const int* pc = &x;                                               // 가리키는 값이 const: *pc = 3 불가, pc = &y 가능
    int* const cp = &x;                                               // 포인터 자체가 const: *cp = 3 가능, cp = &y 불가
    pc = &y; *cp = 3;
    assert(*pc == 2 && x == 3);

    int* none = nullptr;                                              // 아무것도 가리키지 않음 (역참조는 정의되지 않은 동작)
    assert(none == nullptr && !none);
    assert(sizeof(int*) == sizeof(void*) && sizeof(char*) == sizeof(void*));    // 64비트에서 모두 8바이트
    std::cout << "Pointer: sizeof(pointer) = " << sizeof(void*) << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## Reference()
### 대표코드
```cpp
#include <iostream>
#include <functional>
#include <string>
#include <vector>
#include <cassert>

// 참조: 이미 있는 객체의 "다른 이름(별칭)".  반드시 초기화해야 하고, 다시 다른 객체에 묶을 수 없고, null 이 될 수 없다.
// 컨테이너에 참조를 넣고 싶으면 std::reference_wrapper.  임시 객체에 const 참조를 묶으면 임시의 수명이 연장된다
void addOne(int& v) { v++; }
std::string make() { return "temporary"; }

int main() {
    int a = 1, b = 2;
    int& r = a;
    assert(&r == &a);                                                  // 별칭: 주소가 같다 (새 객체가 아니다)
    r = b;                                                              // 재바인딩이 아니라 a 에 b 의 값을 대입
    assert(a == 2 && &r == &a);
    addOne(a); assert(a == 3);                                         // 함수 인자로 원본 수정

    std::vector<std::reference_wrapper<int>> refs = {std::ref(a), std::ref(b)};
    for (int& x : refs) x *= 10;
    assert(a == 30 && b == 20);

    const std::string& longLived = make();                             // 임시 객체의 수명이 참조의 수명까지 연장된다
    assert(longLived == "temporary");
    int&& rv = 5 + 5; rv++;                                            // 우측값 참조: 임시를 소유처럼 사용
    assert(rv == 11);
    std::cout << "Reference verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## SmartPointer()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <cassert>

// 스마트 포인터: 소멸자에서 자동으로 해제하는 포인터 (RAII).
//  unique_ptr: 단독 소유, 복사 불가·이동만 가능, 오버헤드 0.   shared_ptr: 참조 횟수로 공동 소유, 마지막 소유자가 해제.
//  weak_ptr: 소유하지 않는 관찰자 (순환 참조를 끊거나 캐시에 쓴다).  사용자 지정 삭제자도 가능
int destroyed = 0;
struct Res { ~Res() { destroyed++; } };

int main() {
    {
        std::unique_ptr<Res> u = std::make_unique<Res>();
        std::unique_ptr<Res> v = std::move(u);                         // 소유권 이전
        assert(!u && v);
    }                                                                   // 범위를 벗어나면 자동 소멸
    assert(destroyed == 1);

    std::shared_ptr<Res> s1 = std::make_shared<Res>();
    std::weak_ptr<Res> w = s1;
    {
        std::shared_ptr<Res> s2 = s1;                                  // 공동 소유
        assert(s1.use_count() == 2);
    }
    assert(s1.use_count() == 1 && !w.expired());
    s1.reset();                                                         // 마지막 소유자가 사라지면 해제
    assert(destroyed == 2 && w.expired() && w.lock() == nullptr);

    int closed = 0;
    {
        std::unique_ptr<int, void(*)(int*)> custom(new int(5), [](int* p) { delete p; });     // 사용자 지정 삭제자
        auto file = std::shared_ptr<int>(new int(1), [&closed](int* p) { delete p; closed++; });
    }
    assert(closed == 1);
    std::cout << "SmartPointer verified." << std::endl;
    return 0;
}
// Time Complexity: unique_ptr O(1), shared_ptr 복사 O(1) (원자적 카운터)
// Space Complexity: shared_ptr 은 제어 블록 추가
```
## Aliasing()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <cassert>

// 앨리어싱: 서로 다른 이름이 같은 메모리를 가리키는 것.  컴파일러는 "다른 타입의 포인터는 같은 메모리를 가리키지 않는다"(엄격한 앨리어싱 규칙)고
// 가정해 최적화하므로, float 비트를 uint32_t* 로 읽는 reinterpret_cast 는 정의되지 않은 동작이다.  안전한 방법은 memcpy (컴파일러가 한 명령으로 최적화한다)
uint32_t floatBits(float f) { uint32_t u; std::memcpy(&u, &f, sizeof u); return u; }
float bitsFloat(uint32_t u) { float f; std::memcpy(&f, &u, sizeof f); return f; }

bool overlaps(const void* a, size_t na, const void* b, size_t nb) {
    auto x = (uintptr_t)a, y = (uintptr_t)b; return x < y + nb && y < x + na;
}

int main() {
    assert(floatBits(1.0f) == 0x3f800000u);                           // IEEE-754: 1.0f 의 비트 패턴
    assert(floatBits(-2.0f) == 0xc0000000u);
    assert(bitsFloat(0x40490fdbu) > 3.14159f && bitsFloat(0x40490fdbu) < 3.1416f);   // 비트 패턴 -> π
    int v = 5; int* p = &v; int* q = &v;                               // 같은 타입의 앨리어싱은 합법: 한쪽을 바꾸면 다른 쪽에도 보인다
    *p = 6; assert(*q == 6);
    char buf[10] = "abcdefghi";
    assert(overlaps(buf, 5, buf + 3, 5) && !overlaps(buf, 3, buf + 5, 3));
    std::memmove(buf + 2, buf, 5);                                      // 영역이 겹치면 memcpy 가 아니라 memmove
    assert(std::memcmp(buf, "ababcdeh", 8) == 0);
    std::cout << "Aliasing verified: 1.0f bits = " << std::hex << floatBits(1.0f) << std::endl;
    return 0;
}
// Time Complexity: O(1), memmove O(n)
// Space Complexity: O(1)
```
# Part 6. 메모리 할당기
## MemoryPool()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <set>
#include <cassert>

// 메모리 풀: 같은 크기의 블록 N 개를 한 번에 확보해 두고 자유 리스트로 나눠 준다.  빈 블록의 앞부분에 "다음 빈 블록" 포인터를 저장하므로 추가 메모리가 없고,
// 할당·해제가 모두 O(1) 포인터 교환이다.  크기가 같아서 외부 단편화가 없다.  malloc 의 탐색·병합 비용이 없어 게임·네트워크 서버에서 많이 쓴다
class MemoryPool {
    char* mem; void* head = nullptr; size_t blockSize, count, used = 0;
public:
    MemoryPool(size_t block, size_t n) : blockSize(block < sizeof(void*) ? sizeof(void*) : block), count(n) {
        mem = new char[blockSize * count];
        for (size_t i = count; i-- > 0;) { void* b = mem + i * blockSize; *(void**)b = head; head = b; }   // 모든 블록을 리스트로 연결
    }
    ~MemoryPool() { delete[] mem; }
    void* alloc() { if (!head) return nullptr; void* b = head; head = *(void**)b; used++; return b; }
    void release(void* b) { *(void**)b = head; head = b; used--; }
    size_t inUse() const { return used; }
    bool owns(void* p) const { return (char*)p >= mem && (char*)p < mem + blockSize * count; }
};

int main() {
    MemoryPool pool(32, 4);
    void* b[4]; std::set<void*> distinct;
    for (int i = 0; i < 4; i++) { b[i] = pool.alloc(); assert(b[i] && pool.owns(b[i])); distinct.insert(b[i]); }
    assert(distinct.size() == 4);                                  // 서로 다른 블록
    assert(pool.alloc() == nullptr && pool.inUse() == 4);          // 풀이 가득 차면 nullptr
    pool.release(b[1]); pool.release(b[3]);
    assert(pool.alloc() == b[3] && pool.alloc() == b[1]);          // 가장 최근에 반환된 블록이 먼저 재사용 (LIFO, 캐시에 따뜻함)
    assert(((uintptr_t)b[0] - (uintptr_t)b[1]) % 32 == 0);          // 블록 크기 간격
    std::cout << "MemoryPool verified: O(1) alloc/free, LIFO reuse." << std::endl;
    return 0;
}
// Time Complexity: 할당·해제 O(1)
// Space Complexity: O(블록 크기 · 개수)
```
## ObjectPool()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <new>
#include <string>
#include <vector>
#include <cassert>

// 객체 풀: 메모리 풀 위에 "객체 생명주기" 를 얹는다.  acquire 는 배치 new 로 생성자를, release 는 소멸자를 부르고 메모리는 풀에 남겨 재사용한다.
// 생성 비용이 큰 객체(연결, 스레드, 버퍼)를 재사용하는 데 쓰이고, 반환되지 않은 객체의 수로 누수를 바로 알 수 있다
template <class T>
class ObjectPool {
    std::vector<void*> freeList; std::vector<std::unique_ptr<unsigned char[]>> chunks; size_t live = 0;
public:
    template <class... A> T* acquire(A&&... args) {
        if (freeList.empty()) { chunks.emplace_back(new unsigned char[sizeof(T) + alignof(T)]); void* raw = chunks.back().get(); size_t space = sizeof(T) + alignof(T); freeList.push_back(std::align(alignof(T), sizeof(T), raw, space)); }
        void* slot = freeList.back(); freeList.pop_back(); live++;
        return new (slot) T(std::forward<A>(args)...);
    }
    void release(T* obj) { obj->~T(); freeList.push_back(obj); live--; }
    size_t liveCount() const { return live; }
    size_t chunkCount() const { return chunks.size(); }
};

int constructed = 0, destroyed = 0;
struct Conn { std::string host; explicit Conn(std::string h) : host(std::move(h)) { constructed++; } ~Conn() { destroyed++; } };

int main() {
    ObjectPool<Conn> pool;
    Conn* a = pool.acquire("alpha");
    Conn* b = pool.acquire("beta");
    assert(a->host == "alpha" && b->host == "beta" && pool.liveCount() == 2 && constructed == 2);
    pool.release(a);                                               // 소멸자는 호출되지만 메모리는 풀에 남는다
    assert(destroyed == 1 && pool.liveCount() == 1);
    Conn* c = pool.acquire("gamma");
    assert(c == a && c->host == "gamma");                          // 같은 자리를 재사용 -> 새 할당 없음
    assert(pool.chunkCount() == 2);
    pool.release(b); pool.release(c);
    assert(pool.liveCount() == 0 && constructed == destroyed);     // 생성 수 == 소멸 수 -> 누수 없음
    std::cout << "ObjectPool: " << constructed << " constructed, " << pool.chunkCount() << " chunks" << std::endl;
    return 0;
}
// Time Complexity: acquire/release 평균 O(1)
// Space Complexity: O(최대 동시 객체 수)
```
## FreeList()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <vector>
#include <cassert>

// 자유 리스트 할당기: 비어 있는 구멍(hole)을 주소순 리스트로 유지한다.  요청이 오면 어떤 구멍을 쓸지가 정책이다.
//   first-fit: 처음 맞는 구멍 (빠름)   best-fit: 가장 작게 맞는 구멍 (남는 조각이 가장 작음, 아주 작은 조각이 많이 생김)   worst-fit: 가장 큰 구멍 (남는 조각이 큼)
// 해제할 때는 인접한 구멍과 병합해 외부 단편화를 줄인다
struct Hole { size_t off, size; };
enum Policy { FIRST, BEST, WORST };
class FreeList {
public:
    std::vector<Hole> holes;
    long alloc(size_t n, Policy p) {
        int pick = -1;
        for (size_t i = 0; i < holes.size(); i++) {
            if (holes[i].size < n) continue;
            if (pick < 0 || (p == BEST && holes[i].size < holes[pick].size) || (p == WORST && holes[i].size > holes[pick].size)) pick = i;
            if (p == FIRST) break;
        }
        if (pick < 0) return -1;
        size_t off = holes[pick].off;
        holes[pick].off += n; holes[pick].size -= n;
        if (holes[pick].size == 0) holes.erase(holes.begin() + pick);
        return off;
    }
    void release(size_t off, size_t n) {
        holes.push_back({off, n});
        std::sort(holes.begin(), holes.end(), [](const Hole& a, const Hole& b) { return a.off < b.off; });
        for (size_t i = 0; i + 1 < holes.size();) {                 // 인접한 구멍 병합
            if (holes[i].off + holes[i].size == holes[i + 1].off) { holes[i].size += holes[i + 1].size; holes.erase(holes.begin() + i + 1); } else i++;
        }
    }
    double fragmentation() const { size_t tot = 0, mx = 0; for (auto& h : holes) { tot += h.size; mx = std::max(mx, h.size); } return tot ? 1.0 - double(mx) / tot : 0; }
};

int main() {
    auto make = [] { FreeList f; f.holes = {{0, 100}, {150, 30}, {300, 60}, {500, 200}}; return f; };
    FreeList a = make(), b = make(), c = make();
    assert(a.alloc(25, FIRST) == 0);                                 // 첫 구멍(0, 크기 100)
    assert(b.alloc(25, BEST) == 150);                                // 가장 딱 맞는 구멍(150, 크기 30) -> 남는 조각 5
    assert(c.alloc(25, WORST) == 500);                               // 가장 큰 구멍(500, 크기 200)
    assert(b.holes[1].size == 5);                                    // best-fit 이 남긴 아주 작은 조각
    assert(a.alloc(1000, FIRST) == -1);                              // 외부 단편화: 전체 합은 390 이지만 연속 1000 은 없다
    FreeList d; d.holes = {{0, 10}};
    d.release(10, 10); d.release(30, 10);                            // 인접 병합: [0,20) 과 [30,40)
    assert(d.holes.size() == 2 && d.holes[0].size == 20);
    d.release(20, 10);                                               // 가운데를 채우면 세 구멍이 하나로
    assert(d.holes.size() == 1 && d.holes[0].size == 40);
    assert(make().fragmentation() > 0.4);
    std::cout << "FreeList: first-fit=0, best-fit=150, worst-fit=500" << std::endl;
    return 0;
}
// Time Complexity: 할당 O(구멍 수), 해제 O(구멍 수 log 구멍 수)
// Space Complexity: O(구멍 수)
```
## SlabAllocator()
### 대표코드
```cpp
#include <iostream>
#include <bitset>
#include <memory>
#include <vector>
#include <cassert>

// 슬랩 할당기(리눅스 커널): 한 종류의 객체만 담는 "슬랩(고정 크기 페이지)" 여러 개를 관리한다.  슬랩은 부분(partial)·가득(full)·빈(empty) 상태로 나뉘고
// 할당은 부분 슬랩에서 우선한다 -> 슬랩을 거의 가득 채워 쓰고 빈 슬랩은 반환하므로 단편화가 적다.  객체를 미리 초기화해 두면 생성 비용도 줄인다
class SlabCache {
    static const int PER_SLAB = 8;
    struct Slab { std::unique_ptr<char[]> mem; std::bitset<PER_SLAB> used; int count = 0; };
    size_t objSize; std::vector<std::unique_ptr<Slab>> slabs;
public:
    long created = 0, destroyed = 0;
    explicit SlabCache(size_t sz) : objSize(sz) {}
    void* alloc() {
        Slab* s = nullptr;
        for (auto& x : slabs) if (x->count < PER_SLAB && (!s || x->count > s->count)) s = x.get();   // 가장 찬 부분 슬랩 우선
        if (!s) { slabs.emplace_back(new Slab{std::unique_ptr<char[]>(new char[objSize * PER_SLAB])}); s = slabs.back().get(); created++; }
        for (int i = 0; i < PER_SLAB; i++) if (!s->used[i]) { s->used[i] = 1; s->count++; return s->mem.get() + i * objSize; }
        return nullptr;
    }
    void release(void* p) {
        for (size_t k = 0; k < slabs.size(); k++) {
            char* base = slabs[k]->mem.get();
            if ((char*)p >= base && (char*)p < base + objSize * PER_SLAB) {
                slabs[k]->used[((char*)p - base) / objSize] = 0; slabs[k]->count--;
                int empties = 0; for (auto& x : slabs) empties += x->count == 0;
                if (slabs[k]->count == 0 && empties > 1) { slabs.erase(slabs.begin() + k); destroyed++; }     // 빈 슬랩은 하나만 남기고 반환
                return;
            }
        }
    }
    size_t slabCount() const { return slabs.size(); }
};

int main() {
    SlabCache cache(128);
    std::vector<void*> objs;
    for (int i = 0; i < 20; i++) objs.push_back(cache.alloc());
    assert(cache.slabCount() == 3 && cache.created == 3);          // 20개 -> 슬랩 3개 (8 + 8 + 4)
    for (int i = 8; i < 16; i++) cache.release(objs[i]);           // 가운데 슬랩을 전부 반환
    assert(cache.slabCount() == 3 || cache.slabCount() == 2);      // 빈 슬랩은 하나까지만 보유
    void* again = cache.alloc();                                   // 부분 슬랩(가장 찬 슬랩)을 우선 사용
    assert(again != nullptr);
    for (int i = 0; i < 8; i++) cache.release(objs[i]);
    for (int i = 16; i < 20; i++) cache.release(objs[i]);
    cache.release(again);
    assert(cache.slabCount() == 1);                                // 전부 반환하면 빈 슬랩 하나만 남는다
    std::cout << "SlabAllocator: created=" << cache.created << " destroyed=" << cache.destroyed << " remaining=" << cache.slabCount() << std::endl;
    return 0;
}
// Time Complexity: 할당 O(슬랩 수) (구현의 단순화), 실제 커널은 리스트로 O(1)
// Space Complexity: O(슬랩 수 · 슬랩 크기)
```
## BuddyAllocator()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 버디 할당기(리눅스 페이지 할당기): 메모리를 2의 거듭제곱 크기 블록으로 관리한다.  요청은 가장 가까운 큰 2의 거듭제곱으로 올리고(내부 단편화),
// 큰 블록을 반으로 쪼개 쓰고, 해제할 때 "버디"(같은 부모에서 나온 짝, 주소가 offset ^ size)가 비어 있으면 합친다.  병합이 빠르고 외부 단편화에 강하다
class Buddy {
    static const int MAX_ORDER = 4;                                 // 최소 블록 64B ... 최대 1024B (order 4)
    std::set<size_t> freeLists[MAX_ORDER + 1];
    static size_t sizeOf(int order) { return size_t(64) << order; }
public:
    Buddy() { freeLists[MAX_ORDER].insert(0); }
    long alloc(size_t n, int* orderOut = nullptr) {
        int k = 0; while (k <= MAX_ORDER && sizeOf(k) < n) k++;
        if (k > MAX_ORDER) return -1;
        int j = k; while (j <= MAX_ORDER && freeLists[j].empty()) j++;   // 쓸 수 있는 가장 작은 큰 블록
        if (j > MAX_ORDER) return -1;
        size_t off = *freeLists[j].begin(); freeLists[j].erase(freeLists[j].begin());
        while (j > k) { j--; freeLists[j].insert(off + sizeOf(j)); }     // 반으로 쪼개고 오른쪽 절반은 빈 블록으로
        if (orderOut) *orderOut = k;
        return off;
    }
    void release(size_t off, int order) {
        while (order < MAX_ORDER) {
            size_t buddy = off ^ sizeOf(order);                         // 버디의 주소는 XOR 한 번
            auto it = freeLists[order].find(buddy);
            if (it == freeLists[order].end()) break;
            freeLists[order].erase(it); off = std::min(off, buddy); order++;     // 합쳐서 한 단계 위로
        }
        freeLists[order].insert(off);
    }
    size_t freeBlocks(int order) const { return freeLists[order].size(); }
};

int main() {
    Buddy b; int oa, ob, oc;
    long a = b.alloc(100, &oa);                                      // 100B -> 128B 블록 (내부 단편화 28B)
    assert(a == 0 && oa == 1);
    long c = b.alloc(100, &ob);                                      // 이웃한 128B 블록
    assert(c == 128 && ob == 1);
    long d = b.alloc(300, &oc);                                      // 300B -> 512B 블록
    assert(d == 512 && oc == 3);
    assert(b.freeBlocks(2) == 1 && b.freeBlocks(1) == 0);            // 남은 빈 블록: [256, 512)
    b.release(a, oa);
    b.release(d, oc);
    assert(b.freeBlocks(1) == 1);                                    // c 가 남아 있어 a 는 버디와 합쳐지지 못함
    b.release(c, ob);                                                // 마지막 해제 -> 연쇄 병합
    assert(b.freeBlocks(4) == 1 && b.freeBlocks(0) + b.freeBlocks(1) + b.freeBlocks(2) + b.freeBlocks(3) == 0);   // 다시 1024B 하나로
    assert(b.alloc(2000) == -1);
    std::cout << "BuddyAllocator: split on alloc, coalesce on free (buddy = addr XOR size)" << std::endl;
    return 0;
}
// Time Complexity: 할당·해제 O(log N) (order 수)
// Space Complexity: O(블록 수)
```
## ArenaAllocator()
### 대표코드
```cpp
#include <iostream>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>
#include <string>
#include <cassert>

// 아레나(범프) 할당기: 포인터 하나를 앞으로 밀기만 한다.  할당이 가장 빠르고(덧셈 한 번), 개별 해제는 없고 아레나 전체를 한 번에 비운다.
// 컴파일러의 AST, 요청 하나를 처리하는 동안의 임시 객체, 게임의 프레임별 메모리에 적합.  mark/rollback 으로 부분 되돌리기도 가능
class Arena {
    std::unique_ptr<unsigned char[]> buf; size_t cap, top = 0;
public:
    explicit Arena(size_t n) : buf(new unsigned char[n]), cap(n) {}
    void* alloc(size_t n, size_t align = alignof(std::max_align_t)) {
        uintptr_t cur = (uintptr_t)buf.get() + top;
        uintptr_t aligned = (cur + align - 1) & ~(uintptr_t)(align - 1);
        size_t newTop = aligned - (uintptr_t)buf.get() + n;
        if (newTop > cap) return nullptr;
        top = newTop;
        return (void*)aligned;
    }
    template <class T, class... A> T* make(A&&... a) { void* p = alloc(sizeof(T), alignof(T)); return p ? new (p) T(std::forward<A>(a)...) : nullptr; }
    size_t mark() const { return top; }
    void rollback(size_t m) { top = m; }
    void reset() { top = 0; }
    size_t used() const { return top; }
};

int main() {
    Arena a(1024);
    char* c = (char*)a.alloc(1, 1);
    double* d = (double*)a.alloc(sizeof(double), alignof(double));
    assert((uintptr_t)d % alignof(double) == 0 && (char*)d > c);       // 패딩을 넣어 정렬을 맞춘다
    size_t m = a.mark();
    int* tmp = a.make<int>(42); assert(*tmp == 42);
    std::string* s = a.make<std::string>("arena string"); assert(*s == "arena string");
    s->~basic_string();                                                  // 소멸자가 필요한 객체는 직접 정리해야 한다
    a.rollback(m);                                                       // 임시 객체들을 한꺼번에 버린다
    assert(a.used() == m);
    assert(a.alloc(2000) == nullptr);                                    // 용량 초과
    a.reset();
    assert(a.used() == 0 && a.alloc(1000) != nullptr);
    std::cout << "ArenaAllocator verified: bump pointer, rollback, reset." << std::endl;
    return 0;
}
// Time Complexity: 할당 O(1), 해제 O(1) (전체)
// Space Complexity: O(용량)
```
# Part 7. 가비지 컬렉션
## MarkSweep()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 마크-스윕: (1) 루트(스택·전역 변수)에서 닿는 객체를 모두 표시(mark)하고, (2) 힙 전체를 훑어 표시되지 않은 객체를 해제(sweep)한다.
// 순환 참조도 올바르게 회수하고, 객체를 옮기지 않아 포인터가 안정적이다.  단점: 힙 전체를 훑고 단편화가 생기며 수집 중 멈춤(stop-the-world)이 있다
struct Obj { std::vector<int> refs; bool alive = false, marked = false; };
struct Heap {
    std::vector<Obj> objs; std::vector<int> roots;
    int alloc() { for (size_t i = 0; i < objs.size(); i++) if (!objs[i].alive) { objs[i] = Obj{}; objs[i].alive = true; return i; } objs.push_back(Obj{}); objs.back().alive = true; return objs.size() - 1; }
    void mark() {
        std::vector<int> stack(roots.begin(), roots.end());
        while (!stack.empty()) {
            int i = stack.back(); stack.pop_back();
            if (objs[i].marked) continue;
            objs[i].marked = true;
            for (int r : objs[i].refs) stack.push_back(r);
        }
    }
    int sweep() {
        int freed = 0;
        for (auto& o : objs) { if (o.alive && !o.marked) { o.alive = false; o.refs.clear(); freed++; } o.marked = false; }
        return freed;
    }
    int collect() { mark(); return sweep(); }
    int liveCount() const { int c = 0; for (auto& o : objs) c += o.alive; return c; }
};

int main() {
    Heap h;
    int a = h.alloc(), b = h.alloc(), c = h.alloc(), d = h.alloc(), e = h.alloc();
    h.roots = {a};
    h.objs[a].refs = {b}; h.objs[b].refs = {c};            // a -> b -> c  (루트에서 닿는다)
    h.objs[d].refs = {e}; h.objs[e].refs = {d};            // d <-> e  (서로만 가리키는 순환, 루트에서 닿지 않음)
    assert(h.liveCount() == 5);
    assert(h.collect() == 2);                               // 순환 참조된 d, e 가 회수된다
    assert(h.liveCount() == 3 && h.objs[a].alive && h.objs[b].alive && h.objs[c].alive);
    h.objs[b].refs.clear();                                 // b -> c 끊기
    assert(h.collect() == 1 && !h.objs[c].alive);
    int reused = h.alloc();                                 // 회수된 칸을 재사용
    assert(reused == c || reused == d || reused == e);
    std::cout << "MarkSweep verified: cycle collected, live=" << h.liveCount() << std::endl;
    return 0;
}
// Time Complexity: O(살아있는 객체 + 힙 전체) (마크 + 스윕)
// Space Complexity: O(깊이) 마크 스택
```
## MarkCompact()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 마크-컴팩트(Lisp2 방식): 표시 후 살아있는 객체를 한쪽으로 밀어 붙여(slide) 단편화를 없앤다.  객체의 상대 순서가 유지된다.
//   (1) mark  (2) 새 주소(forwarding address) 계산  (3) 모든 참조를 새 주소로 갱신  (4) 객체 이동
struct Obj { int payload; std::vector<int> refs; bool alive = false, marked = false; int fwd = -1; };

int main() {
    std::vector<Obj> heap(8);
    auto make = [&](int i, int payload, std::vector<int> refs) { heap[i] = Obj{payload, refs, true, false, -1}; };
    make(0, 100, {2}); make(1, 111, {}); make(2, 102, {4}); make(3, 113, {}); make(4, 104, {2}); make(5, 115, {}); make(6, 106, {0}); // 1,3,5 는 쓰레기
    std::vector<int> roots = {6};

    // 1) mark
    std::vector<int> st = roots;
    while (!st.empty()) { int i = st.back(); st.pop_back(); if (heap[i].marked) continue; heap[i].marked = true; for (int r : heap[i].refs) st.push_back(r); }
    // 순회 결과(이동 전) 기록: 루트에서 DFS 로 본 payload 순서
    auto walk = [&](std::vector<int> start) { std::vector<int> out, s = start; std::vector<bool> seen(heap.size(), false);
        while (!s.empty()) { int i = s.back(); s.pop_back(); if (seen[i]) continue; seen[i] = true; out.push_back(heap[i].payload); for (int k = heap[i].refs.size(); k-- > 0;) s.push_back(heap[i].refs[k]); } return out; };
    std::vector<int> before = walk(roots);
    // 2) forwarding address
    int next = 0; for (size_t i = 0; i < heap.size(); i++) if (heap[i].alive && heap[i].marked) heap[i].fwd = next++;
    // 3) 참조 갱신
    for (auto& o : heap) if (o.alive && o.marked) for (int& r : o.refs) r = heap[r].fwd;
    for (int& r : roots) r = heap[r].fwd;
    // 4) 이동 (앞쪽으로 밀기: 목적지 <= 원래 위치이므로 순서대로 옮겨도 안전)
    for (size_t i = 0; i < heap.size(); i++) if (heap[i].alive && heap[i].marked) { int dst = heap[i].fwd; Obj o = heap[i]; o.marked = false; o.fwd = -1; heap[dst] = o; }
    for (int i = next; i < (int)heap.size(); i++) heap[i] = Obj{};
    assert(next == 4);                                                     // 살아남은 객체 4개: 0, 2, 4, 6
    for (int i = 0; i < next; i++) assert(heap[i].alive);                 // 앞쪽에 빈틈 없이 모였다
    for (int i = next; i < (int)heap.size(); i++) assert(!heap[i].alive);
    assert(heap[0].payload == 100 && heap[1].payload == 102 && heap[2].payload == 104 && heap[3].payload == 106);   // 상대 순서 유지
    assert(walk(roots) == before);                                         // 이동 후에도 그래프 구조(참조 관계)가 같다
    std::cout << "MarkCompact: live objects slid to [0," << next << ")" << std::endl;
    return 0;
}
// Time Complexity: O(힙 크기) · 3~4 패스
// Space Complexity: O(1) 추가 (forwarding 주소는 객체 헤더에 저장)
```
## CopyingGC()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 복사 수집(Cheney 알고리즘): 힙을 from-space/to-space 로 나눈다.  루트에서 닿는 객체를 to-space 로 "복사" 하며 원본에는 전달 주소(forwarding pointer)를 남겨
// 공유된 객체가 두 번 복사되지 않게 한다.  to-space 의 scan 포인터가 free 포인터를 따라잡으면 끝(BFS).  비용은 살아있는 객체에 비례(쓰레기는 방문조차 안 함),
// 결과가 자동으로 압축된다.  단점: 힙의 절반만 쓸 수 있다
struct Obj { int payload; std::vector<int> refs; int fwd = -1; };

int main() {
    std::vector<Obj> from = {{0, {1, 2}}, {1, {3}}, {2, {3}}, {3, {0}}, {4, {5}}, {5, {4}}, {6, {}}};   // 0->1,2 ; 1->3 ; 2->3 ; 3->0 (순환) ; 4<->5 (쓰레기) ; 6 (쓰레기)
    std::vector<int> roots = {0};
    std::vector<Obj> to;
    auto copy = [&](int i) -> int {                          // 이미 복사됐으면 전달 주소를 돌려준다
        if (from[i].fwd >= 0) return from[i].fwd;
        to.push_back(Obj{from[i].payload, from[i].refs, -1});
        from[i].fwd = to.size() - 1;
        return from[i].fwd;
    };
    for (int& r : roots) r = copy(r);
    for (size_t scan = 0; scan < to.size(); scan++)          // scan 포인터가 free(to.size()) 를 따라잡을 때까지
        for (int& r : to[scan].refs) r = copy(r);
    assert(to.size() == 4);                                   // 도달 가능한 0,1,2,3 만 복사 (4,5,6 은 방문하지 않음)
    assert(to[roots[0]].payload == 0);
    // 공유된 객체 3 은 하나만 복사되어 1 과 2 가 같은 사본을 가리킨다
    int p1 = to[to[roots[0]].refs[0]].refs[0], p2 = to[to[roots[0]].refs[1]].refs[0];
    assert(p1 == p2 && to[p1].payload == 3);
    assert(to[to[p1].refs[0]].payload == 0 && to[p1].refs[0] == roots[0]);   // 순환 3 -> 0 도 올바르게 보존
    from.swap(to);                                            // 역할 교대: to-space 가 새 from-space
    assert(from.size() == 4);
    std::cout << "CopyingGC: 7 objects -> " << from.size() << " survivors, compacted automatically" << std::endl;
    return 0;
}
// Time Complexity: O(살아있는 객체)
// Space Complexity: O(힙) · 2 (두 공간)
```
## GenerationalGC()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 세대별 수집: "대부분의 객체는 금방 죽는다"(약한 세대 가설).  새 객체는 young 에 두고 자주·싸게 수집(minor GC), 두 번 이상 살아남으면 old 로 승급해 드물게 수집한다.
// 문제: old 객체가 young 객체를 가리키면 minor GC 가 old 전체를 훑지 않고도 알아야 한다 -> 쓰기 장벽(write barrier)이 "old -> young 참조" 를 기억 집합(remembered set)에 기록
struct Obj { int id; std::vector<int> refs; bool old = false; int age = 0; };

struct Heap {
    std::vector<Obj> objs; std::set<int> alive; std::vector<int> roots; std::set<int> remembered;   // old 에 있으면서 young 을 가리키는 객체들
    int make() { objs.push_back(Obj{(int)objs.size()}); alive.insert(objs.size() - 1); return objs.size() - 1; }
    void writeRef(int from, int to) {
        objs[from].refs.push_back(to);
        if (objs[from].old && !objs[to].old) remembered.insert(from);          // 쓰기 장벽
    }
    // useRemembered=false 는 장벽을 빼먹은 잘못된 구현을 보여주기 위한 것
    int minorGC(bool useRemembered) {
        std::set<int> live; std::vector<int> st(roots.begin(), roots.end());
        if (useRemembered) for (int r : remembered) for (int c : objs[r].refs) st.push_back(c);
        while (!st.empty()) {
            int i = st.back(); st.pop_back();
            if (objs[i].old || live.count(i)) continue;                         // old 는 minor GC 에서 건드리지 않는다
            live.insert(i);
            for (int c : objs[i].refs) st.push_back(c);
        }
        int freed = 0;
        for (auto it = alive.begin(); it != alive.end();) {
            if (!objs[*it].old && !live.count(*it)) { it = alive.erase(it); freed++; } else ++it;
        }
        for (int i : live) if (++objs[i].age >= 2) objs[i].old = true;          // 두 번 살아남으면 승급
        return freed;
    }
};

int main() {
    auto scenario = [](bool useRemembered) {
        Heap h;
        int oldObj = h.make(); h.roots = {oldObj};
        h.minorGC(true); h.minorGC(true);                 // 두 번 살아남아 oldObj 가 old 세대로 승급
        assert(h.objs[oldObj].old);
        int young = h.make(); int garbage = h.make();      // 새 객체 둘: young 은 old 객체가 참조, garbage 는 아무도 참조 안 함
        h.writeRef(oldObj, young);                         // old -> young 참조 (쓰기 장벽 발동)
        int freed = h.minorGC(useRemembered);
        return std::make_tuple(freed, h.alive.count(young) > 0, h.alive.count(garbage) > 0);
    };
    auto good = scenario(true), bad = scenario(false);
    assert(std::get<0>(good) == 1 && std::get<1>(good) && !std::get<2>(good));    // 쓰레기만 회수, young 은 생존
    assert(!std::get<1>(bad));                                                     // 기억 집합이 없으면 살아있는 young 객체를 잘못 회수한다
    std::cout << "GenerationalGC: remembered set keeps old->young referents alive" << std::endl;
    return 0;
}
// Time Complexity: minor GC 는 young 크기 + 기억 집합에 비례
// Space Complexity: O(기억 집합)
```
## ReferenceCountingGC()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 참조 카운팅: 객체마다 "나를 가리키는 참조의 수" 를 세어 0 이 되면 즉시 해제한다 (즉시성, 예측 가능한 지연).  치명적 약점은 순환 참조 — 서로를 가리키면 카운트가 0 이 되지 않는다.
// CPython 은 참조 카운팅 + 순환 수집기: "내부 참조를 뺀 카운트 gc_refs" 가 0 보다 큰 객체는 외부에서 참조되는 것이므로 거기서 닿는 것만 살리고 나머지를 회수한다
struct Obj { std::vector<int> refs; int rc = 0; bool alive = false; };
struct Heap {
    std::vector<Obj> o; int freedCount = 0;
    int make() { o.push_back(Obj{}); o.back().alive = true; return o.size() - 1; }
    void incref(int i) { o[i].rc++; }
    void decref(int i) { if (--o[i].rc == 0) free(i); }
    void free(int i) { o[i].alive = false; freedCount++; for (int c : o[i].refs) decref(c); o[i].refs.clear(); }
    void link(int from, int to) { o[from].refs.push_back(to); incref(to); }
    int cycleCollect() {                                              // 순환 수집: 내부 참조를 빼고 외부 참조가 없는 덩어리를 회수
        int n = o.size(); std::vector<int> gcRefs(n);
        for (int i = 0; i < n; i++) gcRefs[i] = o[i].alive ? o[i].rc : 0;
        for (int i = 0; i < n; i++) if (o[i].alive) for (int c : o[i].refs) gcRefs[c]--;     // 객체끼리의 참조 제외
        std::vector<bool> reach(n, false); std::vector<int> st;
        for (int i = 0; i < n; i++) if (o[i].alive && gcRefs[i] > 0) st.push_back(i);        // 외부(루트)에서 직접 참조되는 객체
        while (!st.empty()) { int i = st.back(); st.pop_back(); if (reach[i]) continue; reach[i] = true; for (int c : o[i].refs) st.push_back(c); }
        int freed = 0;
        for (int i = 0; i < n; i++) if (o[i].alive && !reach[i]) { o[i].alive = false; o[i].refs.clear(); freed++; }
        return freed;
    }
};

int main() {
    Heap h;
    int a = h.make(), b = h.make(), c = h.make();
    h.incref(a); h.incref(c);                  // 루트(변수)가 a, c 를 참조
    h.link(a, b);                              // a -> b
    h.decref(a);                               // 루트가 a 를 놓음 -> a 해제 -> b 의 카운트도 0 -> 연쇄 해제
    assert(!h.o[a].alive && !h.o[b].alive && h.o[c].alive);             // 즉시 회수 (연쇄)

    int x = h.make(), y = h.make();
    h.incref(x);                               // 루트가 x 를 참조
    h.link(x, y); h.link(y, x);                // x <-> y 순환
    h.decref(x);                               // 루트가 x 를 놓았지만 y -> x 참조가 남아 rc(x) = 1
    assert(h.o[x].alive && h.o[y].alive);      // 누수: 순환이라 카운트가 0 이 되지 않는다
    assert(h.cycleCollect() == 2);             // 순환 수집기가 회수
    assert(!h.o[x].alive && !h.o[y].alive && h.o[c].alive);            // 루트가 쥔 c 는 안전
    std::cout << "ReferenceCountingGC: cycle leaked until the cycle collector ran." << std::endl;
    return 0;
}
// Time Complexity: decref 연쇄 해제 O(해제되는 객체), 순환 수집 O(객체 + 참조)
// Space Complexity: 객체당 카운터 하나
```
## IncrementalGC()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 증분 수집: 마킹을 작은 조각으로 쪼개 프로그램(뮤테이터)과 번갈아 실행해 긴 멈춤을 없앤다.  삼색 표시: 흰색(미방문) / 회색(방문했으나 자식 미처리) / 검정(자식까지 처리).
// 불변식: "검정 객체는 흰 객체를 직접 가리키지 않는다".  뮤테이터가 검정 객체에 흰 객체 참조를 쓰면 그 흰 객체는 영영 처리되지 않아 살아있는데 회수된다.
// 쓰기 장벽(Dijkstra): 검정 객체에 참조를 쓸 때 대상 객체를 회색으로 칠한다
enum Color { WHITE, GRAY, BLACK };
struct Obj { std::vector<int> refs; Color c = WHITE; };
struct GC {
    std::vector<Obj> o; std::vector<int> gray; bool barrier;
    explicit GC(bool b) : barrier(b) {}
    void shade(int i) { if (o[i].c == WHITE) { o[i].c = GRAY; gray.push_back(i); } }
    bool step() {                                                   // 회색 객체 하나를 처리하는 작은 작업
        if (gray.empty()) return false;
        int i = gray.back(); gray.pop_back();
        for (int c : o[i].refs) shade(c);
        o[i].c = BLACK; return true;
    }
    void writeRef(int from, int to) {
        o[from].refs.push_back(to);
        if (barrier && o[from].c == BLACK) shade(to);               // 쓰기 장벽
    }
};

bool lostObject(bool barrier) {
    GC gc(barrier);
    gc.o.resize(3);                                                 // 0 = 루트 객체, 1 = A, 2 = B (A 가 B 를 가리킴)
    gc.o[0].refs = {1}; gc.o[1].refs = {2};
    gc.shade(0);
    gc.step();                                                      // 루트 처리: 1 이 회색, 루트는 검정
    // 뮤테이터: 이미 검정인 루트에 B 로 가는 새 참조를 쓰고, A -> B 참조를 지운다 (B 는 여전히 루트에서 닿는다)
    gc.writeRef(0, 2);
    gc.o[1].refs.clear();
    while (gc.step()) {}                                            // 수집 마무리
    return gc.o[2].c == WHITE;                                      // B 가 표시되지 않았다 = 살아있는 객체가 회수 대상이 됨
}

int main() {
    assert(lostObject(false));                                      // 장벽 없음: B 가 흰색으로 남아 잘못 회수된다
    assert(!lostObject(true));                                      // 장벽 있음: B 는 보존된다
    std::cout << "IncrementalGC: write barrier prevents losing a live object during incremental marking." << std::endl;
    return 0;
}
// Time Complexity: 조각당 O(1) 작업, 전체 O(힙)
// Space Complexity: O(회색 작업 목록)
```
## ConcurrentGC()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <mutex>
#include <random>
#include <set>
#include <thread>
#include <vector>
#include <cassert>

// 동시 수집: 수집기 스레드가 프로그램(뮤테이터)이 실행되는 동안 병렬로 마킹한다.  이때 뮤테이터가 참조를 지우면 수집기가 그 객체를 영영 못 볼 수 있다.
// SATB(Snapshot-At-The-Beginning, Yuasa 삭제 장벽): 참조를 덮어쓰기 전에 "지워지는 옛 값" 을 마킹 큐에 넣는다 -> 수집 시작 시점에 닿던 모든 객체는 반드시 표시된다.
// 검증: 시작 시점에 도달 가능했던 객체 중 회수 대상(표시 안 됨)이 하나도 없어야 한다
struct Heap {
    std::mutex mu;                                              // 단순화: 각 연산을 짧게 잠근다 (실제 JVM 은 락 없는 장벽 사용)
    std::vector<std::vector<int>> refs; std::vector<bool> marked; std::vector<int> work; std::vector<int> satbQueue;
    explicit Heap(int n) : refs(n), marked(n, false) {}
    void writeRef(int from, int slot, int to) {
        std::lock_guard<std::mutex> g(mu);
        int old = refs[from][slot];
        if (old >= 0) satbQueue.push_back(old);                // 삭제 장벽
        refs[from][slot] = to;
    }
    bool markStep() {                                          // 수집기: 작업 하나 처리
        std::lock_guard<std::mutex> g(mu);
        for (int s : satbQueue) work.push_back(s);
        satbQueue.clear();
        if (work.empty()) return false;
        int i = work.back(); work.pop_back();
        if (marked[i]) return true;
        marked[i] = true;
        for (int c : refs[i]) if (c >= 0) work.push_back(c);
        return true;
    }
};

int main() {
    const int N = 200;
    std::mt19937 rng(7);
    Heap h(N);
    for (int i = 0; i < N; i++) { h.refs[i] = {-1, -1}; }
    for (int i = 1; i < N; i++) h.refs[(i - 1) / 2][i % 2] = i;                 // 루트 0 에서 닿는 이진 트리 형태
    // 시작 시점의 스냅샷: 루트 0 에서 도달 가능한 객체 집합
    std::set<int> snapshot; { std::vector<int> st = {0}; while (!st.empty()) { int i = st.back(); st.pop_back(); if (!snapshot.insert(i).second) continue; for (int c : h.refs[i]) if (c >= 0) st.push_back(c); } }
    h.work.push_back(0);
    std::atomic<bool> done(false);
    std::thread mutator([&] {                                                    // 뮤테이터: 마킹 도중 참조를 마구 끊고 바꾼다
        std::mt19937 r(99);
        while (!done) { int from = r() % N, slot = r() % 2; int to = (r() % 3 == 0) ? -1 : (int)(r() % N); h.writeRef(from, slot, to); }
    });
    while (h.markStep()) { std::this_thread::yield(); }
    done = true; mutator.join();
    int missed = 0; for (int i : snapshot) if (!h.marked[i]) missed++;
    assert(missed == 0);                                                          // 스냅샷에서 닿던 객체는 하나도 놓치지 않았다
    std::cout << "ConcurrentGC (SATB): snapshot of " << snapshot.size() << " objects fully marked despite concurrent mutation" << std::endl;
    return 0;
}
// Time Complexity: O(스냅샷 크기 + 장벽 기록 수)
// Space Complexity: O(SATB 큐)
```
# Part 8. 캐시
## CacheLine()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <set>
#include <cassert>

// 캐시는 바이트가 아니라 "캐시 라인"(보통 64바이트) 단위로 메모리를 옮긴다.  주소를 세 부분으로 나눈다:  [ 태그 | 세트 인덱스 | 라인 내 오프셋(6비트) ]
// 라인 하나를 읽으면 이웃한 63바이트가 공짜로 따라오므로 순차 접근(공간 지역성)이 빠르다
int main() {
    const uint64_t LINE = 64;
    auto lineOf = [&](uint64_t addr) { return addr / LINE; };
    auto offsetOf = [&](uint64_t addr) { return addr % LINE; };
    assert(lineOf(0) == 0 && lineOf(63) == 0 && lineOf(64) == 1);
    assert(offsetOf(200) == 8 && lineOf(200) == 3);

    // int 1024 개(4096 바이트)를 순서대로 읽을 때 건드리는 라인: 4096/64 = 64 개 (int 16 개당 1번의 미스)
    std::set<uint64_t> seq; for (int i = 0; i < 1024; i++) seq.insert(lineOf(i * 4));
    assert(seq.size() == 64);
    // 16 칸(=64 바이트) 간격으로 읽으면 모든 접근이 서로 다른 라인 -> 라인의 나머지 60바이트를 낭비
    std::set<uint64_t> strided; for (int i = 0; i < 1024; i += 16) strided.insert(lineOf(i * 4));
    assert(strided.size() == 64);
    std::cout << "sequential: " << seq.size() << " lines for 1024 ints (16 per line); stride-16: " << strided.size() << " lines for only 64 ints" << std::endl;
    return 0;
}
// Time Complexity: O(1) 주소 분해
// Space Complexity: O(1)
```
## CacheHit()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <list>
#include <vector>
#include <cassert>

// 캐시 적중(hit): 요청한 라인이 이미 캐시에 있음.  N-way 세트 연관 캐시를 LRU 로 흉내 낸다.  작업 집합(working set)이 캐시에 들어가면 첫 번째 순회 이후로는 거의 모두 적중한다
struct Cache {
    size_t sets, ways; std::vector<std::list<uint64_t>> s; long hits = 0, misses = 0;
    Cache(size_t sizeBytes, size_t lineBytes, size_t w) : sets(sizeBytes / lineBytes / w), ways(w), s(sizeBytes / lineBytes / w) {}
    bool access(uint64_t addr) {
        uint64_t line = addr / 64; auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); hits++; return true; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); misses++; return false;     // 가장 오래 안 쓴 라인 축출
    }
};

int main() {
    Cache c(32 * 1024, 64, 8);                                // 32KB, 8-way (전형적인 L1)
    const int bytes = 8 * 1024;                               // 작업 집합 8KB < 32KB
    for (int pass = 0; pass < 10; pass++) for (int a = 0; a < bytes; a += 4) c.access(a);
    long total = c.hits + c.misses;
    assert(c.misses == bytes / 64);                           // 미스는 첫 순회의 128 개 (컴펄서리 미스) 뿐
    assert(double(c.hits) / total > 0.99);                    // 적중률 99% 이상
    std::cout << "CacheHit: hit rate " << 100.0 * c.hits / total << "% with an 8KB working set" << std::endl;
    return 0;
}
// Time Complexity: 접근 O(ways)
// Space Complexity: O(캐시 라인 수)
```
## CacheMiss()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <list>
#include <set>
#include <vector>
#include <cassert>

// 캐시 미스의 3C 분류:
//  Compulsory(강제): 처음 접근하는 라인 (캐시가 아무리 커도 발생)
//  Capacity(용량): 작업 집합이 캐시보다 커서 (같은 크기의 완전 연관 캐시도 미스)
//  Conflict(충돌): 여러 라인이 같은 세트에 몰려 (완전 연관 캐시라면 적중했을 것)
struct LRU {
    size_t sets, ways; std::vector<std::list<uint64_t>> s;
    LRU(size_t numLines, size_t w) : sets(numLines / w), ways(w), s(numLines / w) {}
    bool access(uint64_t line) {
        auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); return true; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); return false;
    }
};
struct Result { long compulsory = 0, capacity = 0, conflict = 0; };
Result classify(size_t numLines, size_t ways, const std::vector<uint64_t>& trace) {
    LRU real(numLines, ways), full(numLines, numLines);           // 실제 캐시 vs 같은 크기의 완전 연관 캐시
    std::set<uint64_t> seen; Result r;
    for (uint64_t line : trace) {
        bool hit = real.access(line), fullHit = full.access(line);
        if (!hit) { if (!seen.count(line)) r.compulsory++; else if (!fullHit) r.capacity++; else r.conflict++; }
        seen.insert(line);
    }
    return r;
}

int main() {
    const size_t numLines = 64;                                    // 64 라인 캐시
    std::vector<uint64_t> trace;                                   // 라인 0, 64, 128, 192 를 반복: 직접 사상(1-way)이면 모두 같은 세트(번호 % 64 == 0)
    for (int rep = 0; rep < 50; rep++) for (int k = 0; k < 4; k++) trace.push_back(64ULL * k);
    Result direct = classify(numLines, 1, trace), assoc = classify(numLines, 4, trace);
    assert(direct.compulsory == 4 && direct.capacity == 0 && direct.conflict > 150);   // 라인 4개뿐인데 전부 충돌 미스
    assert(assoc.conflict == 0 && assoc.compulsory == 4);          // 4-way 면 충돌이 사라지고 강제 미스만 남는다
    std::vector<uint64_t> big; for (int rep = 0; rep < 3; rep++) for (uint64_t l = 0; l < 128; l++) big.push_back(l);   // 128 라인을 순환: 용량 초과
    Result cap = classify(numLines, 8, big);
    assert(cap.capacity > 0 && cap.compulsory == 128);             // 완전 연관이어도 미스 -> 용량 미스
    std::cout << "direct-mapped: conflict=" << direct.conflict << "; 4-way: conflict=" << assoc.conflict << "; oversized set: capacity=" << cap.capacity << std::endl;
    return 0;
}
// Time Complexity: O(trace · ways)
// Space Complexity: O(라인 수)
```
## CacheFriendlyTraversal()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <list>
#include <vector>
#include <cassert>

// 2차원 배열은 메모리에서 행 우선(row-major)으로 놓인다: a[i][j] 의 주소 = base + (i·N + j)·4.
// 행 순서로 훑으면 연속 주소라 라인당 16 개가 적중하지만, 열 순서로 훑으면 한 번 접근할 때마다 N·4 바이트씩 건너뛰어 매번 다른 라인 -> 미스 폭증
struct Cache {
    size_t sets, ways; std::vector<std::list<uint64_t>> s; long misses = 0;
    Cache(size_t bytes, size_t w) : sets(bytes / 64 / w), ways(w), s(bytes / 64 / w) {}
    void access(uint64_t addr) {
        uint64_t line = addr / 64; auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); return; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); misses++;
    }
};

int main() {
    const int N = 512;                                            // 512 x 512 ints = 1MB  (캐시 32KB 보다 훨씬 큼)
    Cache rowOrder(32 * 1024, 8), colOrder(32 * 1024, 8);
    for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) rowOrder.access(((uint64_t)i * N + j) * 4);   // a[i][j], j 가 안쪽
    for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) colOrder.access(((uint64_t)i * N + j) * 4);   // i 가 안쪽
    assert(rowOrder.misses == (long)N * N / 16);                  // 라인당 16개 -> 미스 N²/16
    assert(colOrder.misses >= 10 * rowOrder.misses);              // 열 순회는 10배 이상 많은 미스
    std::cout << "misses: row-order=" << rowOrder.misses << " column-order=" << colOrder.misses << " (x" << colOrder.misses / rowOrder.misses << ")" << std::endl;
    return 0;
}
// Time Complexity: O(N²) 접근, 미스 수가 다르다
// Space Complexity: O(1)
```
## CacheBlocking()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cstdint>
#include <list>
#include <vector>
#include <cassert>

// 캐시 블로킹(타일링): 큰 행렬을 캐시에 들어가는 작은 타일로 나눠 타일 안에서 최대한 재사용한다.
// 행렬 곱 C = A·B 를 단순하게 쓰면 B 를 열 방향으로 훑어 캐시를 계속 밀어내지만, B×B 타일로 나누면 타일 하나가 캐시에 머무는 동안 B·B·B 번의 연산을 한다
struct Cache {
    size_t sets, ways; std::vector<std::list<uint64_t>> s; long misses = 0;
    Cache(size_t bytes, size_t w) : sets(bytes / 64 / w), ways(w), s(bytes / 64 / w) {}
    void access(uint64_t addr) {
        uint64_t line = addr / 64; auto& set = s[line % sets];
        for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); return; }
        set.push_front(line); if (set.size() > ways) set.pop_back(); misses++;
    }
};
const int N = 96;
const uint64_t A_BASE = 0, B_BASE = 1 << 20, C_BASE = 2 << 20;
inline uint64_t at(uint64_t base, int i, int j) { return base + ((uint64_t)i * N + j) * 4; }

int main() {
    std::vector<int> A(N * N), B(N * N), Cn(N * N, 0), Cb(N * N, 0);
    for (int i = 0; i < N * N; i++) { A[i] = i % 7; B[i] = (i * 3) % 5; }
    Cache naive(8 * 1024, 4), blocked(8 * 1024, 4);                  // 작은 캐시(8KB)로 차이를 크게 본다
    for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) for (int k = 0; k < N; k++) {
        naive.access(at(A_BASE, i, k)); naive.access(at(B_BASE, k, j)); naive.access(at(C_BASE, i, j));
        Cn[i * N + j] += A[i * N + k] * B[k * N + j];
    }
    const int T = 16;                                                // 타일 16x16 ints = 1KB, 세 타일이 캐시에 들어감
    for (int ii = 0; ii < N; ii += T) for (int jj = 0; jj < N; jj += T) for (int kk = 0; kk < N; kk += T)
        for (int i = ii; i < std::min(ii + T, N); i++) for (int j = jj; j < std::min(jj + T, N); j++) for (int k = kk; k < std::min(kk + T, N); k++) {
            blocked.access(at(A_BASE, i, k)); blocked.access(at(B_BASE, k, j)); blocked.access(at(C_BASE, i, j));
            Cb[i * N + j] += A[i * N + k] * B[k * N + j];
        }
    assert(Cn == Cb);                                                // 계산 결과는 동일
    assert(blocked.misses * 2 < naive.misses);                       // 블로킹이 미스를 절반 이하로 줄인다
    std::cout << "misses: naive=" << naive.misses << " blocked=" << blocked.misses << std::endl;
    return 0;
}
// Time Complexity: O(N³) 연산은 동일, 캐시 미스는 O(N³/ (B·L)) 로 감소
// Space Complexity: O(1)
```
## FalseSharing()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <thread>
#include <cassert>

// 거짓 공유(false sharing): 서로 다른 스레드가 쓰는 "서로 다른 변수" 가 같은 캐시 라인에 있으면, 한 코어가 쓸 때마다 다른 코어의 라인 사본이 무효화되어 라인이 코어 사이를 왔다 갔다 한다.
// 논리적으로는 공유가 없는데 성능이 몇 배 떨어진다.  해결: 변수를 캐시 라인 경계에 맞춰 띄운다 (alignas(64))
struct Packed { std::atomic<long> a{0}; std::atomic<long> b{0}; };                         // 같은 라인
struct Padded { alignas(64) std::atomic<long> a{0}; alignas(64) std::atomic<long> b{0}; };  // 다른 라인

template <class T> double run(T& c, long iters) {
    auto t0 = std::chrono::steady_clock::now();
    std::thread t1([&] { for (long i = 0; i < iters; i++) c.a.fetch_add(1, std::memory_order_relaxed); });
    std::thread t2([&] { for (long i = 0; i < iters; i++) c.b.fetch_add(1, std::memory_order_relaxed); });
    t1.join(); t2.join();
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
}
bool sameLine(const void* x, const void* y) { return (uintptr_t)x / 64 == (uintptr_t)y / 64; }

int main() {
    Packed packed; Padded padded;
    assert(sameLine(&packed.a, &packed.b));                          // 주소로 확인: 한 라인 안에 둘 다 있다
    assert(!sameLine(&padded.a, &padded.b));
    const long iters = 2000000;
    double tPacked = run(packed, iters), tPadded = run(padded, iters);
    assert(packed.a == iters && packed.b == iters && padded.a == iters && padded.b == iters);   // 결과는 정확
    std::cout << "packed: " << tPacked << " ms, padded: " << tPadded << " ms (timing varies by machine)" << std::endl;
    return 0;
}
// Time Complexity: O(iters)
// Space Complexity: 패딩으로 캐시 라인 하나씩 낭비
```
# Part 9. 가상 메모리
## VirtualAddress()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cassert>

// 가상 주소(x86-64, 4단계 페이징): 64비트 중 하위 48비트만 쓰고 [47:0] 을 9+9+9+9+12 비트로 나눈다.
//   [47:39] PML4 인덱스  [38:30] PDPT 인덱스  [29:21] PD 인덱스  [20:12] PT 인덱스  [11:0] 페이지 내 오프셋(4KB)
// 상위 16비트는 비트 47 의 복사여야 하는 "정규(canonical) 주소" 만 유효하다: 낮은 절반은 사용자, 높은 절반은 커널
struct Split { unsigned pml4, pdpt, pd, pt, offset; };
Split split(uint64_t va) { return {unsigned(va >> 39 & 0x1ff), unsigned(va >> 30 & 0x1ff), unsigned(va >> 21 & 0x1ff), unsigned(va >> 12 & 0x1ff), unsigned(va & 0xfff)}; }
uint64_t compose(const Split& s) {
    uint64_t va = (uint64_t)s.pml4 << 39 | (uint64_t)s.pdpt << 30 | (uint64_t)s.pd << 21 | (uint64_t)s.pt << 12 | s.offset;
    if (va >> 47 & 1) va |= 0xffff000000000000ULL;                      // 부호 확장 (정규 주소)
    return va;
}
bool canonical(uint64_t va) { uint64_t top = va >> 47; return top == 0 || top == 0x1ffff; }

int main() {
    uint64_t va = 0x00007f1234567abcULL;
    Split s = split(va);
    assert(s.offset == 0xabc && s.pt == 0x167 && s.pd == 0x1a2 && s.pdpt == 0x48 && s.pml4 == 0xfe);
    assert(compose(s) == va);                                            // 쪼갠 뒤 다시 합치면 원래 주소
    assert(canonical(va) && canonical(0xffff800000000000ULL));           // 사용자 영역 끝, 커널 영역 시작
    assert(!canonical(0x0000800000000000ULL) && !canonical(0x1234000000000000ULL));
    int local; assert(canonical((uint64_t)&local) && (uint64_t)&local < 0x0000800000000000ULL);   // 사용자 포인터는 낮은 절반
    std::cout << "VirtualAddress: 0x" << std::hex << va << " -> pml4=" << s.pml4 << " pdpt=" << s.pdpt << " pd=" << s.pd << " pt=" << s.pt << " off=" << s.offset << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## PhysicalAddress()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 물리 주소: 실제 RAM 의 번호.  물리 메모리는 4KB "프레임" 으로 나뉘고, 운영체제는 프레임 비트맵(또는 버디 할당기)으로 빈 프레임을 관리한다.
// 물리 주소 = 프레임 번호 << 12 | 페이지 내 오프셋.  여러 프로세스가 같은 프레임을 공유할 수 있어(공유 라이브러리, CoW) 프레임마다 참조 횟수를 둔다
class FrameAllocator {
    std::vector<int> refs;                                              // 프레임별 참조 횟수 (0 = 비어 있음)
public:
    explicit FrameAllocator(size_t frames) : refs(frames, 0) {}
    long alloc() { for (size_t i = 0; i < refs.size(); i++) if (refs[i] == 0) { refs[i] = 1; return i; } return -1; }
    void share(size_t f) { refs[f]++; }
    void release(size_t f) { assert(refs[f] > 0); refs[f]--; }
    size_t freeFrames() const { size_t c = 0; for (int r : refs) c += r == 0; return c; }
    static uint64_t physAddr(size_t frame, unsigned offset) { return (uint64_t)frame << 12 | offset; }
};

int main() {
    FrameAllocator fa(4);                                                // 16KB 짜리 작은 RAM
    long f0 = fa.alloc(), f1 = fa.alloc();
    assert(f0 == 0 && f1 == 1 && fa.freeFrames() == 2);
    assert(FrameAllocator::physAddr(f1, 0x234) == 0x1234);
    fa.share(f0);                                                        // 두 프로세스가 프레임 0 을 공유 (참조 2)
    fa.release(f0);
    assert(fa.freeFrames() == 2);                                        // 아직 한 쪽이 쓰는 중이라 반환되지 않는다
    fa.release(f0);
    assert(fa.freeFrames() == 3);                                        // 마지막 참조가 사라져야 프레임이 비워진다
    assert(fa.alloc() == 0);                                             // 재사용
    fa.alloc(); fa.alloc();
    assert(fa.alloc() == -1);                                            // 물리 메모리 고갈
    std::cout << "PhysicalAddress: frame accounting verified." << std::endl;
    return 0;
}
// Time Complexity: 할당 O(프레임 수) (비트맵 + 힌트로 O(1) 가능)
// Space Complexity: O(프레임 수)
```
## AddressTranslation()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// 주소 변환(MMU): 가상 주소를 (페이지 번호, 오프셋) 으로 나누고, 페이지 테이블 항목(PTE)에서 프레임 번호를 찾아 (프레임 번호 << 12 | 오프셋) 을 만든다.
// PTE 에는 present(메모리에 있음), writable, user 비트가 있고, 위반하면 CPU 가 페이지 폴트(예외)를 일으킨다
struct PTE { bool present = false, writable = false, user = false; uint32_t frame = 0; };
enum Status { OK, NOT_PRESENT, PROTECTION };
struct Result { Status st; uint64_t pa; };

Result translate(const std::vector<PTE>& table, uint64_t va, bool write, bool userMode) {
    uint64_t page = va >> 12, off = va & 0xfff;
    if (page >= table.size() || !table[page].present) return {NOT_PRESENT, 0};
    const PTE& e = table[page];
    if ((write && !e.writable) || (userMode && !e.user)) return {PROTECTION, 0};
    return {OK, (uint64_t)e.frame << 12 | off};
}

int main() {
    std::vector<PTE> pt(16);
    pt[3] = {true, true, true, 7};                                       // 페이지 3 -> 프레임 7 (읽기/쓰기, 사용자)
    pt[4] = {true, false, true, 9};                                      // 페이지 4 -> 프레임 9 (읽기 전용)
    pt[5] = {true, true, false, 2};                                      // 페이지 5 -> 프레임 2 (커널 전용)
    auto r = translate(pt, 3 * 4096 + 0x123, false, true);
    assert(r.st == OK && r.pa == 7 * 4096 + 0x123);                      // 오프셋은 그대로, 페이지 번호만 프레임 번호로 바뀐다
    assert(translate(pt, 4 * 4096, true, true).st == PROTECTION);        // 읽기 전용 페이지에 쓰기
    assert(translate(pt, 4 * 4096, false, true).st == OK);
    assert(translate(pt, 5 * 4096, false, true).st == PROTECTION);       // 사용자 모드에서 커널 페이지 접근
    assert(translate(pt, 5 * 4096, false, false).st == OK);
    assert(translate(pt, 9 * 4096, false, true).st == NOT_PRESENT);      // 매핑되지 않은 페이지 -> 페이지 폴트
    std::cout << "AddressTranslation: 0x" << std::hex << (3 * 4096 + 0x123) << " -> 0x" << r.pa << std::endl;
    return 0;
}
// Time Complexity: O(1) (한 단계 테이블)
// Space Complexity: O(페이지 수)
```
## Paging()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <set>
#include <cassert>

// 페이징: 메모리를 같은 크기(4KB)의 페이지로 나눠 어디에나 배치할 수 있게 한다 -> 외부 단편화가 없다.  대신 마지막 페이지의 낭비(내부 단편화, 평균 반 페이지)가 생긴다.
// 문제: 32비트 주소 공간의 평면 페이지 테이블은 2^20 항목 x 4B = 4MB — 프로세스마다 이만큼 필요하다.
// 해법: 다단계 테이블 — 실제로 쓰는 영역의 테이블만 만든다 (희소한 주소 공간에 매우 유리)
int main() {
    const uint64_t PAGE = 4096;
    auto pages = [&](uint64_t bytes) { return (bytes + PAGE - 1) / PAGE; };
    assert(pages(1) == 1 && pages(4096) == 1 && pages(4097) == 2);
    uint64_t request = 10000, waste = pages(request) * PAGE - request;   // 3페이지 = 12288 -> 2288 바이트 낭비
    assert(waste == 2288);

    uint64_t flat = (1ULL << 20) * 4;                                     // 평면 테이블: 4MB
    assert(flat == 4u << 20);
    // 2단계(디렉터리 1024 x 테이블 1024): 프로세스가 코드(0x08048000), 힙(0x09000000), 스택(0xBFFFF000) 주변만 쓴다
    uint64_t used[] = {0x08048000, 0x09000000, 0xBFFFF000};
    std::set<uint64_t> directoryIndexes; for (uint64_t va : used) directoryIndexes.insert(va >> 22);
    uint64_t twoLevel = (1 + directoryIndexes.size()) * PAGE;             // 디렉터리 1페이지 + 사용 중인 페이지 테이블들
    assert(directoryIndexes.size() == 3 && twoLevel == 4 * PAGE);         // 16KB
    assert(flat / twoLevel == 256);                                       // 평면 테이블의 1/256
    std::cout << "Paging: flat page table " << flat / 1024 << " KB vs two-level " << twoLevel / 1024 << " KB; internal fragmentation of 10000 B request = " << waste << " B" << std::endl;
    return 0;
}
// Time Complexity: O(1) 계산
// Space Complexity: 다단계 테이블 O(사용 영역)
```
## PageTable()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <memory>
#include <cassert>

// 4단계 페이지 테이블: 각 단계는 512 개 항목의 배열이고, 하위 단계 테이블이 필요할 때만 만든다 (기수 트리).
// 변환은 인덱스 4번으로 4개 테이블을 차례로 따라가는 것 (그래서 TLB 가 필요하다).  연속한 페이지들은 상위 테이블을 공유한다
struct Table { std::unique_ptr<Table> next[512]; int64_t frame[512]; Table() { for (auto& f : frame) f = -1; } };
class PageTable {
    Table root; int nodes = 1;
    static unsigned idx(uint64_t va, int level) { return va >> (12 + 9 * level) & 0x1ff; }       // level 3 = PML4 ... 0 = PT
public:
    void map(uint64_t va, int64_t frame) {
        Table* t = &root;
        for (int lv = 3; lv > 0; lv--) { auto& n = t->next[idx(va, lv)]; if (!n) { n.reset(new Table()); nodes++; } t = n.get(); }
        t->frame[idx(va, 0)] = frame;
    }
    int64_t translate(uint64_t va) const {
        const Table* t = &root;
        for (int lv = 3; lv > 0; lv--) { t = t->next[idx(va, lv)].get(); if (!t) return -1; }
        int64_t f = t->frame[idx(va, 0)];
        return f < 0 ? -1 : (f << 12 | (va & 0xfff));
    }
    void unmap(uint64_t va) {
        Table* t = &root;
        for (int lv = 3; lv > 0; lv--) { t = t->next[idx(va, lv)].get(); if (!t) return; }
        t->frame[idx(va, 0)] = -1;
    }
    int nodeCount() const { return nodes; }
};

int main() {
    PageTable pt;
    pt.map(0x0000000000400000ULL, 11);                                   // 코드
    assert(pt.nodeCount() == 4);                                         // 루트 + PDPT + PD + PT
    pt.map(0x0000000000401000ULL, 12);                                   // 바로 다음 페이지: 같은 PT 를 공유 -> 노드 추가 없음
    assert(pt.nodeCount() == 4);
    pt.map(0x00007ffffffff000ULL, 99);                                   // 스택 근처: 완전히 다른 가지 -> 노드 3개 추가
    assert(pt.nodeCount() == 7);
    assert(pt.translate(0x0000000000400123ULL) == (11LL << 12 | 0x123));
    assert(pt.translate(0x00007ffffffff008ULL) == (99LL << 12 | 0x8));
    assert(pt.translate(0x0000000000500000ULL) == -1);                   // 매핑 없음
    pt.unmap(0x0000000000400000ULL);
    assert(pt.translate(0x0000000000400123ULL) == -1 && pt.translate(0x0000000000401000ULL) == (12LL << 12));
    std::cout << "PageTable: 3 mappings use " << pt.nodeCount() << " table pages (flat table would need 2^36 entries)" << std::endl;
    return 0;
}
// Time Complexity: 변환 O(4) = O(1), 매핑 O(4)
// Space Complexity: O(매핑된 영역에 비례하는 테이블 수)
```
## PageFault()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <list>
#include <vector>
#include <cassert>

// 페이지 폴트: 매핑되지 않았거나 메모리에 없는 페이지에 접근했을 때 CPU 가 일으키는 예외.  운영체제가 디스크에서 페이지를 읽어 오고(요구 페이징),
// 프레임이 모자라면 교체 알고리즘으로 희생 페이지를 고른다.
// FIFO 는 프레임을 늘려도 폴트가 오히려 늘어나는 벨레이디의 모순(Belady's anomaly)이 있고, LRU 는 스택 알고리즘이라 그런 일이 없다
int faultsFIFO(const std::vector<int>& refs, size_t frames) {
    std::list<int> q; int faults = 0;
    for (int p : refs) {
        if (std::find(q.begin(), q.end(), p) != q.end()) continue;
        faults++; if (q.size() == frames) q.pop_front(); q.push_back(p);
    }
    return faults;
}
int faultsLRU(const std::vector<int>& refs, size_t frames) {
    std::list<int> q; int faults = 0;
    for (int p : refs) {
        auto it = std::find(q.begin(), q.end(), p);
        if (it != q.end()) { q.erase(it); q.push_back(p); continue; }       // 사용하면 가장 최근으로
        faults++; if (q.size() == frames) q.pop_front(); q.push_back(p);
    }
    return faults;
}

int main() {
    std::vector<int> refs = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    assert(faultsFIFO(refs, 3) == 9 && faultsFIFO(refs, 4) == 10);           // 프레임이 늘었는데 폴트가 9 -> 10 으로 증가
    assert(faultsLRU(refs, 3) == 10 && faultsLRU(refs, 4) == 8);             // LRU 는 프레임이 늘면 폴트가 줄어든다
    for (size_t f = 1; f < 8; f++) assert(faultsLRU(refs, f + 1) <= faultsLRU(refs, f));   // 단조 감소 (스택 성질)
    std::cout << "PageFault: FIFO 3 frames=" << faultsFIFO(refs, 3) << ", 4 frames=" << faultsFIFO(refs, 4) << " (Belady's anomaly)" << std::endl;
    return 0;
}
// Time Complexity: O(참조 수 · 프레임 수)
// Space Complexity: O(프레임 수)
```
## TLBLookup()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <list>
#include <cassert>

// TLB(Translation Lookaside Buffer): 최근 변환 결과(페이지 번호 -> 프레임 번호)를 저장하는 작은 캐시.  적중하면 4단계 페이지 테이블을 걷지 않아도 된다.
// 유효 접근 시간 EAT = h·(t_tlb + t_mem) + (1-h)·(t_tlb + 4·t_mem + t_mem)   (미스 시 테이블 4단계를 걷는 메모리 접근 4번 + 실제 접근 1번)
class TLB {
    size_t cap; std::list<std::pair<uint64_t, uint64_t>> e;
public:
    long hits = 0, misses = 0, walks = 0;
    explicit TLB(size_t c) : cap(c) {}
    uint64_t lookup(uint64_t page) {
        for (auto it = e.begin(); it != e.end(); ++it) if (it->first == page) { auto v = *it; e.erase(it); e.push_front(v); hits++; return v.second; }
        misses++; walks += 4;                                       // 페이지 테이블 워크: 메모리 접근 4번
        uint64_t frame = page * 3 + 1;                              // (가짜) 변환 결과
        e.push_front({page, frame}); if (e.size() > cap) e.pop_back();
        return frame;
    }
};
double eat(double h, double tlb, double mem) { return h * (tlb + mem) + (1 - h) * (tlb + 4 * mem + mem); }

int main() {
    TLB tlb(4);
    for (int rep = 0; rep < 100; rep++) for (uint64_t p = 0; p < 3; p++) tlb.lookup(p);     // 3 페이지를 반복: 작업 집합이 TLB(4)에 들어감
    assert(tlb.misses == 3 && tlb.hits == 297);                      // 처음 3번만 미스
    TLB small(2);
    for (int rep = 0; rep < 100; rep++) for (uint64_t p = 0; p < 3; p++) small.lookup(p);   // 작업 집합(3) > TLB(2): LRU 에서 계속 미스
    assert(small.hits == 0 && small.misses == 300);
    double fast = eat(0.99, 1, 100), slow = eat(0.50, 1, 100);       // 적중률이 접근 시간을 좌우한다
    assert(fast < 1.05 * 101 + 5 * 1 && slow > 2 * fast / 1.5);
    std::cout << "TLB: working set fits -> " << tlb.hits << " hits; EAT(h=0.99)=" << fast << " ns vs EAT(h=0.50)=" << slow << " ns" << std::endl;
    return 0;
}
// Time Complexity: 조회 O(TLB 크기) (하드웨어는 병렬 비교로 O(1))
// Space Complexity: O(TLB 항목 수)
```
## MemoryMapping()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
#if defined(__linux__)
#include <sys/mman.h>
#include <unistd.h>
#include <vector>
#endif

// 메모리 매핑: mmap 은 가상 주소 범위만 "예약" 하고, 물리 메모리는 페이지를 처음 만졌을 때(요구 페이징) 비로소 배정된다.
// mincore 로 어느 페이지가 실제 메모리에 올라와 있는지(resident) 확인할 수 있다
int main() {
#if defined(__linux__)
    const long ps = sysconf(_SC_PAGESIZE);
    const int pages = 16;
    char* p = (char*)mmap(nullptr, pages * ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(p != MAP_FAILED);
    std::vector<unsigned char> vec(pages);
    mincore(p, pages * ps, vec.data());
    int resident = 0; for (auto v : vec) resident += v & 1;
    assert(resident == 0);                                          // 아직 아무 페이지도 만지지 않았다: 물리 메모리 사용 0
    p[0 * ps] = 1; p[5 * ps] = 1; p[9 * ps] = 1;                     // 3 페이지만 만진다 -> 페이지 폴트로 그 페이지만 배정
    mincore(p, pages * ps, vec.data());
    resident = 0; for (auto v : vec) resident += v & 1;
    assert(resident == 3 && (vec[0] & 1) && (vec[5] & 1) && (vec[9] & 1) && !(vec[1] & 1));
    munmap(p, pages * ps);
    std::cout << "MemoryMapping: reserved " << pages << " pages, only " << resident << " resident after touching 3" << std::endl;
#else
    std::cout << "MemoryMapping: Linux-only demonstration (mmap + mincore)" << std::endl;
#endif
    return 0;
}
// Time Complexity: mmap O(1), 페이지 접근 시 폴트 처리
// Space Complexity: 만진 페이지 수에 비례
```
# Part 10. 메모리 보호
## ReadOnlyMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <csetjmp>
#include <csignal>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>
static sigjmp_buf env;
static void onSegv(int) { siglongjmp(env, 1); }
#endif

// 읽기 전용 메모리: 페이지 테이블의 writable 비트를 끄면 쓰기는 하드웨어가 막고 운영체제가 SIGSEGV 를 보낸다.
// 문자열 리터럴·const 전역은 .rodata(읽기 전용) 페이지에 놓인다.  mprotect 로 직접 보호를 걸고 위반을 안전하게 잡아 본다
int main() {
#if defined(__unix__) || defined(__APPLE__)
    long ps = sysconf(_SC_PAGESIZE);
    char* p = (char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    p[0] = 'A'; assert(p[0] == 'A');                                 // 쓰기 가능한 동안은 정상
    mprotect(p, ps, PROT_READ);                                      // 읽기 전용으로 전환
    assert(p[0] == 'A');                                             // 읽기는 여전히 가능
    struct sigaction sa; std::memset(&sa, 0, sizeof sa); sa.sa_handler = onSegv; sigaction(SIGSEGV, &sa, nullptr);
    bool trapped = false;
    if (sigsetjmp(env, 1) == 0) { p[0] = 'B'; } else trapped = true;  // 쓰기 -> SIGSEGV -> 핸들러가 점프로 복귀
    assert(trapped && p[0] == 'A');                                  // 값은 바뀌지 않았다
    mprotect(p, ps, PROT_READ | PROT_WRITE);
    p[0] = 'C'; assert(p[0] == 'C');                                 // 권한을 되돌리면 다시 쓸 수 있다
    munmap(p, ps);
    std::cout << "ReadOnlyMemory: write to a read-only page raised SIGSEGV and was caught." << std::endl;
#else
    std::cout << "ReadOnlyMemory: POSIX-only demonstration (mprotect + SIGSEGV)" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## ExecuteOnlyMemory()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
#if defined(__linux__) && defined(__x86_64__)
#include <csetjmp>
#include <csignal>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>
static sigjmp_buf env;
static void onSegv(int) { siglongjmp(env, 1); }
#endif

// W^X(Write XOR Execute): 한 페이지가 동시에 "쓰기 가능" 이면서 "실행 가능" 해서는 안 된다는 정책.  코드 주입 공격을 막는다.
// JIT 컴파일러의 정석 절차: RW 로 매핑 -> 기계어 쓰기 -> RX 로 전환 -> 실행.  (순수한 실행 전용 X-only 는 CPU 가 PKU/ARM 등을 지원해야 한다)
int main() {
#if defined(__linux__) && defined(__x86_64__)
    long ps = sysconf(_SC_PAGESIZE);
    unsigned char* code = (unsigned char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    // x86-64: mov eax, 42 ; ret   ->  B8 2A 00 00 00 C3
    const unsigned char prog[] = {0xB8, 0x2A, 0x00, 0x00, 0x00, 0xC3};
    std::memcpy(code, prog, sizeof prog);                            // 1) RW 상태에서 기계어를 쓴다
    mprotect(code, ps, PROT_READ | PROT_EXEC);                       // 2) RX 로 전환 (이제 쓸 수 없다)
    int (*fn)() = (int(*)())code;
    assert(fn() == 42);                                              // 3) 실행

    struct sigaction sa; std::memset(&sa, 0, sizeof sa); sa.sa_handler = onSegv; sigaction(SIGSEGV, &sa, nullptr);
    bool trapped = false;
    if (sigsetjmp(env, 1) == 0) { code[1] = 0x00; } else trapped = true;     // 실행 가능한 페이지에 쓰기 시도
    assert(trapped);
    munmap(code, ps);
    std::cout << "ExecuteOnlyMemory: JIT-style W^X sequence worked; writing to the RX page faulted." << std::endl;
#else
    std::cout << "ExecuteOnlyMemory: Linux x86-64 demonstration only" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(페이지)
```
## MemoryProtection()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <csetjmp>
#include <csignal>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>
static sigjmp_buf env;
static void onSegv(int) { siglongjmp(env, 1); }
#endif

// 메모리 보호: 페이지마다 R/W/X 권한 비트를 두어 접근 종류가 권한과 맞지 않으면 예외를 낸다.  (1) 권한 모델  (2) 가드 페이지: PROT_NONE 페이지를 경계에 놓아 오버플로를 즉시 잡는다
enum Perm : unsigned { R = 1, W = 2, X = 4 };
bool allowed(unsigned perm, char access) { return (perm & (access == 'r' ? R : access == 'w' ? W : X)) != 0; }

int main() {
    unsigned code = R | X, data = R | W, rodata = R;
    assert(allowed(code, 'x') && !allowed(code, 'w'));              // 코드: 실행 O, 쓰기 X
    assert(allowed(data, 'w') && !allowed(data, 'x'));              // 데이터: 쓰기 O, 실행 X (DEP)
    assert(allowed(rodata, 'r') && !allowed(rodata, 'w') && !allowed(rodata, 'x'));
#if defined(__unix__) || defined(__APPLE__)
    long ps = sysconf(_SC_PAGESIZE);
    char* region = (char*)mmap(nullptr, 2 * ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    mprotect(region + ps, ps, PROT_NONE);                            // 두 번째 페이지를 가드 페이지로
    region[ps - 1] = 'x';                                            // 첫 페이지의 마지막 바이트는 정상
    struct sigaction sa; std::memset(&sa, 0, sizeof sa); sa.sa_handler = onSegv; sigaction(SIGSEGV, &sa, nullptr);
    bool overflowCaught = false;
    if (sigsetjmp(env, 1) == 0) { region[ps] = 'y'; } else overflowCaught = true;     // 한 바이트만 넘어가도 즉시 폴트
    assert(overflowCaught);
    munmap(region, 2 * ps);
    std::cout << "MemoryProtection: guard page stopped a 1-byte overflow." << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 가드 페이지 1개 (4KB)
```
## StackCanary()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <cassert>

// 스택 카나리: 지역 버퍼와 복귀 주소 사이에 비밀 난수(카나리)를 둔다.  버퍼 오버플로로 복귀 주소를 덮으려면 반드시 카나리를 먼저 덮게 되므로,
// 함수가 반환하기 직전에 카나리가 그대로인지 확인해 공격을 탐지한다 (gcc -fstack-protector).
// 아래는 스택 프레임 한 칸을 바이트 배열로 흉내 낸 안전한 시뮬레이션이다: [ buf(8) | canary(8) | return address(8) ]
struct Frame { unsigned char mem[24]; };
const uint64_t CANARY = 0x00C0FFEE5AFEC0DEULL;

void enter(Frame& f) {
    std::memset(f.mem, 0, sizeof f.mem);
    std::memcpy(f.mem + 8, &CANARY, 8);
    uint64_t ret = 0x400123; std::memcpy(f.mem + 16, &ret, 8);
}
void unsafeCopy(Frame& f, const char* input, size_t n) { std::memcpy(f.mem, input, n); }          // 길이 검사 없는 strcpy 와 같은 위험한 복사
void leave(const Frame& f) {                                                                         // 반환 직전 검사
    uint64_t c; std::memcpy(&c, f.mem + 8, 8);
    if (c != CANARY) throw std::runtime_error("*** stack smashing detected ***");
}

int main() {
    Frame ok; enter(ok); unsafeCopy(ok, "short", 6);
    leave(ok);                                                      // 8바이트 이내 -> 정상
    Frame bad; enter(bad);
    char attack[24]; std::memset(attack, 'A', sizeof attack);       // 24바이트: buf 를 넘어 카나리와 복귀 주소까지 덮는다
    unsafeCopy(bad, attack, sizeof attack);
    bool detected = false;
    try { leave(bad); } catch (const std::runtime_error&) { detected = true; }
    assert(detected);                                               // 복귀 주소가 바뀌기 전에 공격을 감지
    uint64_t ret; std::memcpy(&ret, bad.mem + 16, 8);
    assert(ret == 0x4141414141414141ULL);                           // 복귀 주소는 실제로 덮였다 (카나리가 없었다면 제어 흐름 탈취)
    std::cout << "StackCanary: overflow detected before the corrupted return address was used." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
// Space Complexity: 프레임당 8바이트
```
## ASLR()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <cassert>
#if defined(__linux__)
#include <unistd.h>
#endif

// ASLR(주소 공간 배치 무작위화): 프로세스를 시작할 때마다 스택·힙·라이브러리(·PIE 실행 파일)의 위치를 무작위로 옮겨, 공격자가 목표 주소를 미리 알 수 없게 한다.
// 확인: 자기 자신을 두 번 실행(popen)해 스택 주소를 비교한다.  /proc/sys/kernel/randomize_va_space: 0 = 끔, 1 = 스택·mmap, 2 = 힙 포함 전체
int main(int argc, char** argv) {
#if defined(__linux__)
    if (argc == 2 && std::string(argv[1]) == "child") { int local; std::printf("%lx\n", (unsigned long)&local); return 0; }
    int mode = -1; { std::ifstream f("/proc/sys/kernel/randomize_va_space"); f >> mode; }
    assert(mode >= 0 && mode <= 2);
    auto runChild = [&]() {
        char self[4096]; ssize_t n = readlink("/proc/self/exe", self, sizeof self - 1); assert(n > 0); self[n] = 0;   // popen 은 sh 를 거치므로 자기 경로를 직접 얻어야 한다
        std::string cmd = std::string(self) + " child";
        FILE* pipe = popen(cmd.c_str(), "r"); char buf[64] = {0}; if (pipe) { if (!fgets(buf, sizeof buf, pipe)) buf[0] = 0; pclose(pipe); }
        return std::string(buf);
    };
    std::string a = runChild(), b = runChild();
    assert(!a.empty() && !b.empty());
    if (mode >= 1) assert(a != b);                                  // 실행마다 스택 주소가 달라진다 (우연히 같을 확률은 2^-22 이하)
    else assert(a == b);                                            // 끄면 항상 같다
    std::cout << "ASLR (mode " << mode << "): run1 stack=" << a.substr(0, a.size() - 1) << " run2 stack=" << b.substr(0, b.size() - 1) << std::endl;
#else
    (void)argc; (void)argv;
    std::cout << "ASLR: Linux-only demonstration" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## DEP()
### 대표코드
```cpp
#include <iostream>
#include <cassert>
#if defined(__linux__) && defined(__x86_64__)
#include <csetjmp>
#include <csignal>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>
static sigjmp_buf env;
static void onSegv(int) { siglongjmp(env, 1); }
#endif

// DEP / NX 비트(데이터 실행 방지): 데이터 페이지(스택·힙)에는 실행 권한이 없다.  공격자가 버퍼에 기계어를 주입해도 그 위치로 점프하면 CPU 가 예외를 낸다.
// 이를 우회하려는 공격이 ROP(이미 있는 코드 조각을 이어 붙이기)이고, 그래서 ASLR 과 함께 쓴다
int main() {
#if defined(__linux__) && defined(__x86_64__)
    long ps = sysconf(_SC_PAGESIZE);
    unsigned char* page = (unsigned char*)mmap(nullptr, ps, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    page[0] = 0xC3;                                                  // x86-64 'ret' 명령 하나짜리 "주입된 코드"
    struct sigaction sa; std::memset(&sa, 0, sizeof sa); sa.sa_handler = onSegv; sigaction(SIGSEGV, &sa, nullptr);
    bool blocked = false;
    if (sigsetjmp(env, 1) == 0) { ((void(*)())page)(); } else blocked = true;      // 데이터 페이지를 코드처럼 실행
    assert(blocked);                                                 // NX 가 막았다
    mprotect(page, ps, PROT_READ | PROT_EXEC);                       // 명시적으로 실행 권한을 주면
    bool ran = false;
    if (sigsetjmp(env, 1) == 0) { ((void(*)())page)(); ran = true; }
    assert(ran);                                                     // 실행된다 (그래서 mprotect 호출을 제한하는 정책이 따로 있다)
    munmap(page, ps);
    std::cout << "DEP: executing a data page faulted; after mprotect(PROT_EXEC) it ran." << std::endl;
#else
    std::cout << "DEP: Linux x86-64 demonstration only" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
# Part 11. 병렬 메모리
## AtomicOperation()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>

// 원자적 연산: 중간 상태를 다른 스레드가 볼 수 없는 불가분의 읽기-수정-쓰기.  일반 변수의 counter++ 는 (읽기, 더하기, 쓰기) 세 단계라 두 스레드가 겹치면 갱신이 사라진다(경쟁 상태).
// std::atomic 의 fetch_add 는 CPU 의 lock 접두 명령(x86: lock xadd)으로 구현되어 정확하다
int main() {
    std::atomic<long> counter(0);
    const int T = 4; const long N = 200000;
    std::vector<std::thread> th;
    for (int t = 0; t < T; t++) th.emplace_back([&] { for (long i = 0; i < N; i++) counter.fetch_add(1, std::memory_order_relaxed); });
    for (auto& x : th) x.join();
    assert(counter.load() == T * N);                                   // 갱신 손실 없음: 정확히 800000
    assert(counter.is_lock_free());                                    // 잠금 없이 하드웨어 명령으로 처리
    std::atomic<int> flag(0);
    assert(flag.exchange(5) == 0 && flag.load() == 5);                 // 교환: 이전 값을 돌려주며 새 값 저장
    std::cout << "AtomicOperation: " << counter.load() << " (expected " << T * N << ")" << std::endl;
    return 0;
}
// Time Complexity: O(1) 연산 (경합 시 캐시 라인 이동 비용)
// Space Complexity: O(1)
```
## CompareAndSwap()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>

// CAS(compare-and-swap): "현재 값이 expected 와 같으면 desired 로 바꾸고 성공, 아니면 실패하고 현재 값을 알려 준다" 를 한 번에 하는 원자 명령 (x86: cmpxchg).
// 락 없는 자료구조의 기본 블록: 읽고 -> 계산하고 -> CAS 로 반영을 시도하고, 실패하면(다른 스레드가 먼저 바꿈) 다시 시도한다.
// ABA 문제: 값이 A -> B -> A 로 바뀌어도 CAS 는 "그대로" 라고 판단한다.  해법: 포인터에 버전 번호(태그)를 함께 CAS
struct Node { int v; Node* next; };

// (1) CAS 루프로 구현한 락 없는 스택 push
std::atomic<Node*> head(nullptr);
void push(int v) { Node* n = new Node{v, head.load()}; while (!head.compare_exchange_weak(n->next, n)) {} }     // 실패 시 n->next 가 현재 head 로 갱신된다

// (2) ABA 를 결정적으로 재현 (스레드 인터리빙을 순서대로 직접 실행)
struct Tagged { Node* p; unsigned tag; bool operator==(const Tagged& o) const { return p == o.p && tag == o.tag; } };

int main() {
    std::vector<std::thread> th;
    for (int t = 0; t < 4; t++) th.emplace_back([t] { for (int i = 0; i < 5000; i++) push(t * 10000 + i); });
    for (auto& x : th) x.join();
    int count = 0; for (Node* n = head.load(); n; n = n->next) count++;
    assert(count == 20000);                                            // 모든 push 가 성공적으로 반영 (유실·중복 없음)

    Node c{3, nullptr}, b{2, &c}, a{1, &b};                            // 스택: a -> b -> c
    // 스레드 1: head == a 를 읽고 next == b 를 기억한 뒤 선점된다.   스레드 2: a, b 를 pop 한 뒤 a 를 다시 push (b 는 해제됨)
    Node* t1_head = &a; Node* t1_next = a.next;                        // 스레드 1 의 관찰
    Node* shared = &a;                                                  // 공유 head
    shared = a.next;                                                    // 스레드 2: pop a  -> head = b
    shared = b.next;                                                    // 스레드 2: pop b  -> head = c  (b 는 해제되어 더 이상 유효하지 않다)
    a.next = shared; shared = &a;                                       // 스레드 2: push a -> a -> c
    bool naive = (shared == t1_head);                                   // 스레드 1 의 CAS(head, a, b): head 가 여전히 a 인가? -> 예, 성공해 버린다
    assert(naive && t1_next == &b && shared->next == &c);               // CAS 가 성공해 head = b 로 바꾸면 이미 해제된 b 가 스택에 들어간다 (손상!)

    Tagged tagged{&a, 0}, observed = tagged;                           // 해법: 태그(버전)를 함께 비교
    tagged.p = &c; tagged.tag++; tagged.p = &a; tagged.tag++;          // 스레드 2 의 같은 조작 (태그는 매번 증가)
    assert(tagged.p == observed.p);                                     // 포인터는 같지만
    assert(!(tagged == observed));                                      // 태그가 달라 CAS 는 실패 -> ABA 방지
    std::cout << "CompareAndSwap: lock-free stack built; ABA detected with a version tag." << std::endl;
    return 0;
}
// Time Complexity: 루프당 O(1), 경합 시 재시도
// Space Complexity: O(1)
```
## MemoryBarrier()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>

// 메모리 장벽: CPU 와 컴파일러는 성능을 위해 서로 다른 주소에 대한 읽기/쓰기 순서를 바꾼다 (x86 도 "쓰기 뒤 읽기" 는 스토어 버퍼 때문에 순서가 바뀐다).
// 고전 실험(Store Buffering):  스레드 A: x = 1; r0 = y;     스레드 B: y = 1; r1 = x;
//   순차 일관성이라면 (r0, r1) = (0, 0) 은 불가능하지만, 장벽 없이는 둘 다 0 을 볼 수 있다.   seq_cst(또는 fence) 를 쓰면 절대 일어나지 않는다
const int N = 100000;
std::vector<std::atomic<int>> arrive(N), X(N), Y(N), R0(N), R1(N);

long runTest(std::memory_order storeOrder, std::memory_order loadOrder, bool useFence) {
    for (int i = 0; i < N; i++) { arrive[i] = 0; X[i] = 0; Y[i] = 0; R0[i] = -1; R1[i] = -1; }
    auto sync = [&](int i) { arrive[i].fetch_add(1); while (arrive[i].load() < 2) {} };          // 두 스레드를 같은 순간에 출발시킨다
    std::thread a([&] { for (int i = 0; i < N; i++) { sync(i); X[i].store(1, storeOrder); if (useFence) std::atomic_thread_fence(std::memory_order_seq_cst); R0[i].store(Y[i].load(loadOrder), std::memory_order_relaxed); } });
    std::thread b([&] { for (int i = 0; i < N; i++) { sync(i); Y[i].store(1, storeOrder); if (useFence) std::atomic_thread_fence(std::memory_order_seq_cst); R1[i].store(X[i].load(loadOrder), std::memory_order_relaxed); } });
    a.join(); b.join();
    long both0 = 0; for (int i = 0; i < N; i++) both0 += (R0[i] == 0 && R1[i] == 0);
    return both0;
}

int main() {
    long relaxed = runTest(std::memory_order_relaxed, std::memory_order_relaxed, false);       // 장벽 없음: (0,0) 이 관찰될 수 있다 (x86 에서도)
    long withFence = runTest(std::memory_order_relaxed, std::memory_order_relaxed, true);       // 쓰기와 읽기 사이에 full fence
    long seqcst = runTest(std::memory_order_seq_cst, std::memory_order_seq_cst, false);         // seq_cst 저장/적재
    assert(withFence == 0);                                                                     // 보장: fence 가 있으면 절대 (0,0) 이 없다
    assert(seqcst == 0);                                                                        // 보장: seq_cst 면 절대 (0,0) 이 없다
    std::cout << "Store-buffering outcome (0,0) in " << N << " trials: relaxed=" << relaxed << " (machine dependent), fence=" << withFence << ", seq_cst=" << seqcst << std::endl;
    return 0;
}
// Time Complexity: O(N) 시도
// Space Complexity: O(N)
```
## AcquireRelease()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>

// acquire/release: seq_cst 보다 약하지만 가장 흔한 "메시지 전달" 패턴에 충분한 순서 보장.
//  release 저장: 이 저장 "이전의 모든 쓰기" 가 이 저장과 함께 다른 스레드에 보이게 한다.
//  acquire 적재: release 가 쓴 값을 읽었다면, 그 release 이전의 모든 쓰기를 볼 수 있다.
// 생산자가 data 를 쓰고 flag 를 release 로 올리면, flag 를 acquire 로 본 소비자는 반드시 최신 data 를 읽는다
const int N = 100000;
std::vector<int> data(N);                                       // 일반 변수 (원자적이지 않음)
std::vector<std::atomic<int>> flag(N);

int main() {
    for (auto& f : flag) f = 0;
    std::thread producer([] { for (int i = 0; i < N; i++) { data[i] = i * 2 + 1; flag[i].store(1, std::memory_order_release); } });
    long stale = 0;
    std::thread consumer([&] {
        for (int i = 0; i < N; i++) {
            while (flag[i].load(std::memory_order_acquire) == 0) {}          // 플래그가 보일 때까지 대기
            if (data[i] != i * 2 + 1) stale++;                               // 플래그가 보였다면 data 도 반드시 보여야 한다
        }
    });
    producer.join(); consumer.join();
    assert(stale == 0);                                                      // release/acquire 쌍이 happens-before 를 만든다
    std::cout << "AcquireRelease: " << N << " messages, stale reads = " << stale << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
## SequentialConsistency()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>

// 순차 일관성(SC): 모든 스레드의 모든 연산이 "하나의 전체 순서" 로 일어난 것처럼 보이고, 각 스레드의 연산은 프로그램 순서를 따른다.  std::atomic 의 기본(seq_cst)이다.
// IRIW 실험(Independent Reads of Independent Writes):  A: x=1   B: y=1   C: r1=x; r2=y   D: r3=y; r4=x
//   C 는 "x 가 먼저" (r1=1, r2=0), D 는 "y 가 먼저" (r3=1, r4=0) 를 볼 수 있다면 두 독자가 쓰기 순서에 대해 서로 다른 세계를 본 것 — SC 에서는 불가능하다
const int N = 20000;
std::vector<std::atomic<int>> arrive(N), X(N), Y(N), R1(N), R2(N), R3(N), R4(N);

int main() {
    for (int i = 0; i < N; i++) { arrive[i] = 0; X[i] = 0; Y[i] = 0; }
    auto sync = [&](int i) { arrive[i].fetch_add(1); while (arrive[i].load() < 4) {} };
    std::thread a([&] { for (int i = 0; i < N; i++) { sync(i); X[i].store(1); } });                                   // seq_cst 기본값
    std::thread b([&] { for (int i = 0; i < N; i++) { sync(i); Y[i].store(1); } });
    std::thread c([&] { for (int i = 0; i < N; i++) { sync(i); R1[i] = X[i].load(); R2[i] = Y[i].load(); } });
    std::thread d([&] { for (int i = 0; i < N; i++) { sync(i); R3[i] = Y[i].load(); R4[i] = X[i].load(); } });
    a.join(); b.join(); c.join(); d.join();
    long forbidden = 0;
    for (int i = 0; i < N; i++) forbidden += (R1[i] == 1 && R2[i] == 0 && R3[i] == 1 && R4[i] == 0);
    assert(forbidden == 0);                                                 // SC 가 보장하는 금지 결과는 관찰되지 않는다
    std::cout << "SequentialConsistency: IRIW forbidden outcome observed " << forbidden << " times in " << N << " trials" << std::endl;
    return 0;
}
// Time Complexity: O(N)
// Space Complexity: O(N)
```
# Part 12. 메모리 분석
## MemoryLeak()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <memory>
#include <new>
#include <cassert>

// 메모리 누수: 할당한 메모리를 더 이상 가리키는 포인터가 없는데 해제하지 않은 상태.  프로그램이 오래 살수록 쌓여 결국 메모리가 고갈된다.
// 탐지의 기본: new/delete 를 가로채 "아직 살아있는 할당 수" 를 센다 (Valgrind·ASan 의 LeakSanitizer 도 같은 원리).  근본 해결은 RAII: 소유권을 객체에 맡겨 해제를 잊을 수 없게 한다
static long liveAllocs = 0;
static void* volatile sink;                                             // 포인터를 "사용" 한 것처럼 보이게 해 컴파일러가 할당을 통째로 제거하지 못하게 한다
__attribute__((noinline)) void touch(void* p) { sink = p; }
void* operator new(size_t n) { void* p = std::malloc(n); if (!p) throw std::bad_alloc(); liveAllocs++; return p; }
void operator delete(void* p) noexcept { if (p) liveAllocs--; std::free(p); }
void operator delete(void* p, size_t) noexcept { if (p) liveAllocs--; std::free(p); }

void leaky()  { int* p = new int[100]; p[0] = 1; touch(p); }                      // 해제하지 않고 반환: 마지막 포인터가 사라진다 -> 누수
void early(bool fail) { int* p = new int(5); touch(p); if (fail) return; delete p; }   // 오류 경로에서 해제를 빠뜨린 전형적인 누수
void safe(bool fail)  { auto p = std::make_unique<int>(5); touch(p.get()); if (fail) return; }  // RAII: 어느 경로로 나가도 해제

int main() {
    long base = liveAllocs;
    leaky();
    assert(liveAllocs == base + 1);                                      // 누수 1건
    early(false); assert(liveAllocs == base + 1);                        // 정상 경로는 누수 없음
    early(true);  assert(liveAllocs == base + 2);                        // 오류 경로에서 누수
    safe(true); safe(false);
    assert(liveAllocs == base + 2);                                      // RAII 버전은 어느 경로에서도 누수가 늘지 않는다
    std::cout << "MemoryLeak: " << liveAllocs - base << " leaked allocations detected by counting." << std::endl;
    return 0;
}
// Time Complexity: O(1) 추적
// Space Complexity: O(1) 카운터 (상세 추적은 O(할당 수))
```
## DanglingPointer()
### 대표코드
```cpp
#include <iostream>
#include <stdexcept>
#include <vector>
#include <cassert>

// 댕글링 포인터: 이미 해제된 메모리를 가리키는 포인터.  원시 포인터는 자신이 유효한지 알 수 없다.
// 해법 중 하나: 포인터 대신 (슬롯 번호, 세대) 핸들을 쓴다.  해제하면 슬롯의 세대가 올라가 옛 핸들은 세대 불일치로 거부된다 (게임 엔진의 엔티티 ID, Rust 의 slotmap)
struct Handle { size_t index; unsigned gen; };
template <class T> class Slots {
    struct Slot { T value{}; unsigned gen = 0; bool used = false; };
    std::vector<Slot> slots; std::vector<size_t> freeList;
public:
    Handle alloc(const T& v) {
        size_t i; if (freeList.empty()) { slots.emplace_back(); i = slots.size() - 1; } else { i = freeList.back(); freeList.pop_back(); }
        slots[i].value = v; slots[i].used = true; return {i, slots[i].gen};
    }
    void release(Handle h) { check(h); slots[h.index].used = false; slots[h.index].gen++; freeList.push_back(h.index); }
    T& get(Handle h) { check(h); return slots[h.index].value; }
    void check(Handle h) const { if (h.index >= slots.size() || !slots[h.index].used || slots[h.index].gen != h.gen) throw std::runtime_error("dangling handle"); }
};

int main() {
    Slots<int> heap;
    Handle a = heap.alloc(10);
    assert(heap.get(a) == 10);
    heap.release(a);
    bool detected = false;
    try { heap.get(a); } catch (const std::runtime_error&) { detected = true; }
    assert(detected);                                                    // 해제 직후의 사용을 잡는다
    Handle b = heap.alloc(20);                                           // 같은 슬롯이 재사용된다
    assert(b.index == a.index && b.gen != a.gen);                        // 슬롯은 같지만 세대가 다르다
    detected = false;
    try { heap.get(a); } catch (const std::runtime_error&) { detected = true; }
    assert(detected && heap.get(b) == 20);                               // 재사용 후에도 옛 핸들은 거부 (ABA 방지), 새 핸들은 정상
    std::cout << "DanglingPointer: stale handle rejected by generation check." << std::endl;
    return 0;
}
// Time Complexity: 접근 O(1) + 세대 검사
// Space Complexity: 슬롯당 세대 카운터
```
## WildPointer()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <map>
#include <stdexcept>
#include <cassert>

// 와일드 포인터: 초기화되지 않은 포인터 (쓰레기 값을 주소로 간주).  어디를 가리키는지 알 수 없어 어떤 메모리든 망가뜨릴 수 있다.
// 대책: (1) 항상 초기화 (nullptr)  (2) 해제 후 nullptr 대입  (3) 할당 목록에 등록된 범위만 유효하다고 인정하는 검사기(Registry)
class Registry {
    std::map<uintptr_t, size_t> live;                                    // 시작 주소 -> 크기
public:
    void add(const void* p, size_t n) { live[(uintptr_t)p] = n; }
    void remove(const void* p) { live.erase((uintptr_t)p); }
    bool valid(const void* p, size_t n = 1) const {
        uintptr_t a = (uintptr_t)p; auto it = live.upper_bound(a);
        if (it == live.begin()) return false;
        --it; return a >= it->first && a + n <= it->first + it->second;
    }
};
template <class T> T& checkedDeref(const Registry& r, T* p) {
    if (!p) throw std::runtime_error("null dereference");
    if (!r.valid(p, sizeof(T))) throw std::runtime_error("wild pointer: not inside any live allocation");
    return *p;
}

int main() {
    Registry reg;
    int* heap = new int(7); reg.add(heap, sizeof(int));
    int* init = nullptr;                                                  // 초기화된 포인터: 안전하게 검사 가능
    int* wild = reinterpret_cast<int*>(0x12345678);                       // 초기화되지 않은 포인터가 가질 수 있는 쓰레기 값 (역참조하지 않는다)
    assert(checkedDeref(reg, heap) == 7);
    bool nullCaught = false, wildCaught = false;
    try { checkedDeref(reg, init); } catch (const std::runtime_error&) { nullCaught = true; }
    try { checkedDeref(reg, wild); } catch (const std::runtime_error&) { wildCaught = true; }
    assert(nullCaught && wildCaught);
    reg.remove(heap); delete heap; heap = nullptr;                        // 해제 후 nullptr 대입 습관
    bool afterFree = false; try { checkedDeref(reg, heap); } catch (const std::runtime_error&) { afterFree = true; }
    assert(afterFree);
    std::cout << "WildPointer: null and wild dereferences rejected." << std::endl;
    return 0;
}
// Time Complexity: 검사 O(log N)
// Space Complexity: O(할당 수)
```
## DoubleFree()
### 대표코드
```cpp
#include <iostream>
#include <stdexcept>
#include <vector>
#include <cassert>

// 이중 해제: 이미 free 한 포인터를 다시 free.  할당기의 자유 리스트가 망가져 같은 블록이 두 번 할당되는 등 공격에 악용된다.
// glibc 는 "free(): double free detected in tcache 2" 로 abort.  검사기는 블록 상태(할당됨/해제됨)를 기록해 두 번째 해제를 거부한다.  nullptr free 는 무해하다
class CheckedHeap {
    enum State { FREE, ALLOCATED };
    std::vector<State> state; std::vector<long> freed;
public:
    long alloc() { state.push_back(ALLOCATED); return state.size() - 1; }
    void release(long id) {
        if (id < 0) return;                                              // free(nullptr) 은 아무 일도 하지 않는다
        if (state.at(id) == FREE) throw std::runtime_error("double free detected");
        state[id] = FREE;
    }
    size_t liveCount() const { size_t c = 0; for (auto s : state) c += s == ALLOCATED; return c; }
};

int main() {
    CheckedHeap h;
    long a = h.alloc(), b = h.alloc();
    h.release(a);
    bool detected = false;
    try { h.release(a); } catch (const std::runtime_error&) { detected = true; }
    assert(detected && h.liveCount() == 1);                              // 두 번째 해제는 거부되고 상태는 그대로
    h.release(-1);                                                       // null 해제는 무해
    h.release(b); assert(h.liveCount() == 0);
    // C++ 에서는 소유권을 unique_ptr 에 맡기면 이중 해제를 구조적으로 막는다 (이동 후 원본은 nullptr)
    std::cout << "DoubleFree: second release rejected." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(블록 수)
```
## UseAfterFree()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <vector>
#include <cassert>

// 해제 후 사용(use-after-free): 해제된 메모리를 읽거나 쓴다.  그 사이 같은 메모리가 다른 객체에 재할당되면 두 객체가 서로의 데이터를 덮어쓰는 심각한 취약점이 된다.
// 탐지 기법: (1) 해제된 메모리를 독 패턴(0xDD)으로 채우고 (2) 즉시 재사용하지 않고 격리 구역(quarantine)에 둔다 -> 해제 후 읽으면 0xDDDDDDDD 가 보인다 (ASan 의 방식)
class PoisonHeap {
    std::vector<uint8_t> mem; std::vector<bool> freed;
    size_t top = 0;
public:
    explicit PoisonHeap(size_t n) : mem(n, 0), freed(n, false) {}
    size_t alloc(size_t n) { size_t p = top; top += n; for (size_t i = p; i < top; i++) freed[i] = false; return p; }
    void release(size_t p, size_t n) { std::memset(&mem[p], 0xDD, n); for (size_t i = p; i < p + n; i++) freed[i] = true; }     // 독 칠하기 (재사용은 안 함 = 격리)
    uint8_t read(size_t addr) const { return mem[addr]; }
    bool isPoisoned(size_t addr) const { return freed[addr]; }
    void write(size_t addr, uint8_t v) { mem[addr] = v; }
};

int main() {
    PoisonHeap h(64);
    size_t p = h.alloc(8);
    h.write(p, 42); assert(h.read(p) == 42 && !h.isPoisoned(p));
    h.release(p, 8);
    assert(h.isPoisoned(p) && h.read(p) == 0xDD);                        // 해제 후 읽으면 독 값 0xDD — 버그가 눈에 띈다
    // 실제 C++ 에서 흔한 사례: vector 가 재할당하면 이전에 얻은 포인터/반복자가 무효가 된다
    std::vector<int> v = {1, 2, 3};
    const int* first = v.data();
    v.reserve(1000);                                                     // 더 큰 버퍼로 옮겨가며 옛 버퍼는 해제
    assert(v.data() != first);                                           // 옛 포인터는 해제된 메모리를 가리킨다 (역참조하면 UAF)
    std::cout << "UseAfterFree: freed memory reads back as 0xDD; vector reallocation invalidated an old pointer." << std::endl;
    return 0;
}
// Time Complexity: O(해제 크기)
// Space Complexity: 격리 구역만큼 메모리 지연 반환
```
## BufferOverflow()
### 대표코드
```cpp
#include <iostream>
#include <array>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <cassert>

// 버퍼 오버플로: 버퍼 크기를 넘겨 인접한 메모리를 덮어쓴다.  탐지: 할당 앞뒤에 "레드존" 을 두고 특정 값을 채워 두었다가 해제할 때(또는 접근할 때) 값이 바뀌었는지 본다.
// 안전한 C++: std::array::at / vector::at 의 범위 검사, 길이를 지정하는 복사 함수
class GuardedBuffer {
    static const size_t RZ = 8; std::vector<uint8_t> mem; size_t n;
public:
    explicit GuardedBuffer(size_t size) : mem(size + 2 * RZ, 0xFE), n(size) { std::memset(&mem[RZ], 0, size); }
    uint8_t* data() { return &mem[RZ]; }                                 // 사용자 영역
    bool redzonesIntact() const {
        for (size_t i = 0; i < RZ; i++) if (mem[i] != 0xFE || mem[RZ + n + i] != 0xFE) return false;
        return true;
    }
};

int main() {
    GuardedBuffer b(16);
    std::memset(b.data(), 'A', 16);                                      // 정확히 16바이트: 정상
    assert(b.redzonesIntact());
    b.data()[16] = 'X';                                                  // 1바이트 초과 쓰기(off-by-one)
    assert(!b.redzonesIntact());                                         // 뒤쪽 레드존이 오염되어 탐지된다
    GuardedBuffer under(16); under.data()[-1] = 'Y';
    assert(!under.redzonesIntact());                                     // 앞쪽 언더플로도 탐지
    std::array<int, 4> arr = {1, 2, 3, 4};
    bool caught = false; try { arr.at(4) = 0; } catch (const std::out_of_range&) { caught = true; }
    assert(caught);                                                      // at() 은 범위를 검사한다
    char dst[8]; const char* src = "this string is too long";
    std::strncpy(dst, src, sizeof(dst) - 1); dst[sizeof(dst) - 1] = '\0';   // 길이를 제한한 복사 + 항상 널 종단
    assert(std::strlen(dst) == 7);
    std::cout << "BufferOverflow: off-by-one detected through red zones." << std::endl;
    return 0;
}
// Time Complexity: 검사 O(레드존 크기)
// Space Complexity: 할당당 2 · 레드존
```
## HeapCorruption()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <cassert>

// 힙 손상: 할당기의 메타데이터(블록 헤더, 자유 리스트 포인터)가 오버플로나 UAF 로 망가진 상태.  이후의 malloc/free 가 엉뚱한 곳에 쓰게 되어 공격에 악용된다.
// 방어: 헤더에 마법 값(magic)과 체크섬을 두고 free/malloc 때마다 검증한다 (glibc 의 "malloc(): corrupted top size", "free(): invalid size" 가 그것)
struct Header { uint32_t magic; uint32_t size; uint32_t check; };       // check = magic ^ size ^ 상수
const uint32_t MAGIC = 0xA110CA7E;
uint32_t checksum(uint32_t size) { return MAGIC ^ size ^ 0x5bd1e995u; }

class Heap {
    std::vector<uint8_t> mem; size_t top = 0;
public:
    explicit Heap(size_t n) : mem(n, 0) {}
    size_t alloc(uint32_t size) {
        Header h{MAGIC, size, checksum(size)}; std::memcpy(&mem[top], &h, sizeof h);
        size_t user = top + sizeof h; top = user + size; return user;
    }
    uint8_t* at(size_t user) { return &mem[user]; }
    void release(size_t user) {                                          // 해제 시 헤더 검증
        Header h; std::memcpy(&h, &mem[user - sizeof h], sizeof h);
        if (h.magic != MAGIC || h.check != checksum(h.size)) throw std::runtime_error("free(): invalid pointer / corrupted header");
    }
};

int main() {
    Heap heap(256);
    size_t a = heap.alloc(16), b = heap.alloc(16);
    heap.release(a);                                                     // 정상 블록은 통과
    std::memset(heap.at(a), 0xAA, 16 + 4);                               // a 가 16바이트를 넘어 4바이트 더 써서 이웃 b 의 헤더(magic) 앞부분을 덮는다
    bool detected = false;
    try { heap.release(b); } catch (const std::runtime_error&) { detected = true; }
    assert(detected);                                                    // 이웃 블록의 손상된 헤더를 해제 시점에 발견
    std::cout << "HeapCorruption: corrupted neighbouring header detected at free()." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검증
// Space Complexity: 블록당 헤더 12바이트
```
# Part 13. 파일과 메모리
## MemoryMappedFile()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <string>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#endif

// 메모리 맵 파일: mmap 으로 파일을 프로세스 주소 공간에 붙이면 read/write 시스템 호출 없이 포인터로 파일 내용을 읽고 쓴다.
// 페이지를 처음 만질 때 커널이 파일에서 읽어 오고(페이지 캐시와 공유 -> 복사 1회 절약), MAP_SHARED 로 수정하면 파일에 반영된다
int main() {
#if defined(__unix__) || defined(__APPLE__)
    char path[] = "/tmp/ds_mmap_XXXXXX";
    int fd = mkstemp(path); assert(fd >= 0);
    const long ps = sysconf(_SC_PAGESIZE);
    std::string content(2 * ps, 'a'); content.replace(ps, 5, "HELLO");   // 두 페이지짜리 파일, 둘째 페이지 앞에 HELLO
    assert(write(fd, content.data(), content.size()) == (ssize_t)content.size());

    char* m = (char*)mmap(nullptr, content.size(), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    assert(m != MAP_FAILED);
    assert(m[0] == 'a' && std::memcmp(m + ps, "HELLO", 5) == 0);          // 포인터로 파일 내용을 읽는다
    std::memcpy(m + 10, "WORLD", 5);                                       // 메모리에 쓰면
    msync(m, content.size(), MS_SYNC);                                     // 파일에 반영한다
    char check[6] = {0}; assert(pread(fd, check, 5, 10) == 5);
    assert(std::strcmp(check, "WORLD") == 0);                              // read 로 읽은 파일 내용에서도 보인다
    munmap(m, content.size()); close(fd); unlink(path);
    std::cout << "MemoryMappedFile: file edited through a pointer and visible via pread." << std::endl;
#else
    std::cout << "MemoryMappedFile: POSIX-only demonstration (mmap)" << std::endl;
#endif
    return 0;
}
// Time Complexity: 접근 시 페이지 폴트 O(1) (캐시에 있으면 복사 없음)
// Space Complexity: 페이지 캐시 공유
```
## SharedMemory()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <cstring>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 공유 메모리: 서로 다른 프로세스의 가상 주소가 같은 물리 페이지를 가리키게 한다 -> 가장 빠른 프로세스 간 통신(복사 없음).
// 동기화는 직접 해야 한다: 락 프리 원자 변수를 공유 영역에 두고 쓰면 프로세스 사이에서도 원자적이다
struct Shared { std::atomic<int> counter; char message[32]; };

int main() {
#if defined(__unix__) || defined(__APPLE__)
    Shared* s = (Shared*)mmap(nullptr, sizeof(Shared), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    assert(s != MAP_FAILED);
    new (&s->counter) std::atomic<int>(0);
    std::strcpy(s->message, "parent");
    const int KIDS = 3, N = 10000;
    for (int k = 0; k < KIDS; k++) {
        pid_t pid = fork();
        if (pid == 0) {                                                    // 자식 프로세스: 공유 영역에 쓴다
            for (int i = 0; i < N; i++) s->counter.fetch_add(1);
            if (k == 0) std::strcpy(s->message, "hello from child");
            _exit(0);
        }
    }
    for (int k = 0; k < KIDS; k++) wait(nullptr);
    assert(s->counter.load() == KIDS * N);                                  // 세 프로세스의 증가가 모두 반영
    assert(std::strcmp(s->message, "hello from child") == 0);              // 자식이 쓴 문자열이 부모에게 보인다
    munmap(s, sizeof(Shared));
    std::cout << "SharedMemory: 3 processes incremented a shared atomic " << KIDS * N << " times." << std::endl;
#else
    std::cout << "SharedMemory: POSIX-only demonstration (mmap + fork)" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1) 접근
// Space Complexity: 공유 영역 1벌
```
## CopyOnWrite()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

// 쓰기 시 복사(CoW): 복사본을 만든다고 해 놓고 실제 복사는 "쓰는 순간" 까지 미룬다.  fork 직후 부모와 자식은 같은 물리 페이지를 읽기 전용으로 공유하다가,
// 어느 쪽이 쓰면 그 페이지만 복제한다 -> fork 가 빠르고 메모리를 아낀다.  사용자 공간에서도 문자열·버퍼에 같은 기법을 쓴다
class CowString {
    std::shared_ptr<std::string> data;
public:
    explicit CowString(std::string s) : data(std::make_shared<std::string>(std::move(s))) {}
    CowString(const CowString&) = default;                               // 복사는 포인터 공유 O(1)
    const std::string& str() const { return *data; }
    long owners() const { return data.use_count(); }
    void set(size_t i, char c) {
        if (data.use_count() > 1) data = std::make_shared<std::string>(*data);   // 공유 중이면 쓰기 직전에 분리(detach)
        (*data)[i] = c;
    }
};

int main() {
    CowString a("hello"); CowString b = a;
    assert(a.owners() == 2 && &a.str() == &b.str());                       // 복사 후에도 같은 버퍼 공유
    b.set(0, 'J');
    assert(a.str() == "hello" && b.str() == "Jello");                      // 쓰는 순간 분리 — 원본은 그대로
    assert(a.owners() == 1 && b.owners() == 1 && &a.str() != &b.str());
#if defined(__unix__) || defined(__APPLE__)
    int* p = (int*)mmap(nullptr, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    *p = 100;
    int fds[2]; assert(pipe(fds) == 0);
    pid_t pid = fork();
    if (pid == 0) {                                                        // 자식: 같은 가상 주소에 쓰면 자기 사본만 바뀐다
        *p = 999; int seen = *p; (void)!write(fds[1], &seen, sizeof seen); _exit(0);
    }
    int childSaw = 0; assert(read(fds[0], &childSaw, sizeof childSaw) == sizeof childSaw);
    wait(nullptr);
    assert(childSaw == 999 && *p == 100);                                  // 부모의 값은 그대로 (페이지가 복제됨)
    munmap(p, 4096);
#endif
    std::cout << "CopyOnWrite: writer got its own copy, original untouched." << std::endl;
    return 0;
}
// Time Complexity: 복사 O(1), 첫 쓰기 O(크기)
// Space Complexity: 쓰기가 일어나기 전까지 공유
```
## ZeroCopy()
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <cassert>
#if defined(__linux__)
#include <fcntl.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

// 제로 카피: 데이터를 사용자 공간 버퍼로 옮기지 않고 커널 안에서 파일 -> 소켓/파일로 직접 전달한다.
//  read+write: 디스크 -> 커널 버퍼 -> (복사) 사용자 버퍼 -> (복사) 커널 버퍼 -> 목적지 : 사용자 공간 복사 2번, 문맥 전환 4번
//  sendfile  : 디스크 -> 커널 버퍼 -> 목적지                                          : 사용자 공간 복사 0번 (웹 서버가 정적 파일을 보내는 방식)
// 같은 아이디어를 사용자 공간에서도 쓴다: string_view 로 부분 문자열을 복사 없이 가리킨다
int main() {
    std::string src = "/tmp/ds_zc_src.bin", dst1 = "/tmp/ds_zc_dst1.bin", dst2 = "/tmp/ds_zc_dst2.bin";
    std::string payload(300000, 'x'); for (size_t i = 0; i < payload.size(); i += 97) payload[i] = char('a' + i % 26);
    { std::ofstream f(src, std::ios::binary); f << payload; }
#if defined(__linux__)
    long userCopied = 0;                                             // 사용자 공간 버퍼를 거친 바이트 수
    { int in = open(src.c_str(), O_RDONLY), out = open(dst1.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
      std::vector<char> buf(16384); ssize_t n;
      while ((n = read(in, buf.data(), buf.size())) > 0) { userCopied += n; (void)!write(out, buf.data(), n); }          // 전통적인 방식
      close(in); close(out); }
    long viaSendfile = 0, userCopied2 = 0;
    { int in = open(src.c_str(), O_RDONLY), out = open(dst2.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
      struct stat st; fstat(in, &st); off_t off = 0;
      while (off < st.st_size) { ssize_t n = sendfile(out, in, &off, st.st_size - off); if (n <= 0) break; viaSendfile += n; }   // 커널 안에서만 이동
      close(in); close(out); }
    auto slurp = [](const std::string& p) { std::ifstream f(p, std::ios::binary); std::ostringstream ss; ss << f.rdbuf(); return ss.str(); };
    assert(slurp(dst1) == payload && slurp(dst2) == payload);         // 결과는 동일
    assert(userCopied == (long)payload.size() && userCopied2 == 0 && viaSendfile == (long)payload.size());     // 사용자 공간 복사: 전체 vs 0
    std::remove(dst1.c_str()); std::remove(dst2.c_str());
#endif
    std::remove(src.c_str());
    std::string line = "key=value;other=thing";
    std::string_view v(line); auto eq = v.find('='); auto semi = v.find(';');
    std::string_view key = v.substr(0, eq), val = v.substr(eq + 1, semi - eq - 1);     // 복사 없이 같은 메모리를 가리킨다
    assert(key == "key" && val == "value" && key.data() == line.data());
    std::cout << "ZeroCopy: sendfile moved " << payload.size() << " bytes without a user-space buffer." << std::endl;
    return 0;
}
// Time Complexity: O(n) 이동, 사용자 공간 복사 0
// Space Complexity: O(1) 사용자 버퍼
```
# Part 14. 운영체제
## ProcessMemory()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>

// 프로세스 메모리 지도: 리눅스의 /proc/self/maps 는 프로세스의 가상 주소 영역(VMA)을 한 줄씩 보여 준다.
//   시작-끝  권한(rwxp)  오프셋  장치  inode  경로      예) 55d0c8a00000-55d0c8a21000 r-xp ... /path/a.out   ...  [heap]   ...  [stack]
// 코드는 r-xp, 읽기 전용 데이터는 r--p, 전역 변수는 rw-p, 스택은 [stack].  자기 변수의 주소가 어느 영역에 속하는지 확인할 수 있다
struct Region { uint64_t start, end; std::string perms, name; };
std::vector<Region> readMaps() {
    std::ifstream f("/proc/self/maps"); std::vector<Region> out; std::string line;
    while (std::getline(f, line)) {
        std::istringstream ss(line); std::string range, perms, off, dev, inode, name;
        ss >> range >> perms >> off >> dev >> inode; std::getline(ss, name);
        size_t dash = range.find('-'); size_t b = name.find_first_not_of(' ');
        out.push_back({std::stoull(range.substr(0, dash), nullptr, 16), std::stoull(range.substr(dash + 1), nullptr, 16), perms, b == std::string::npos ? "" : name.substr(b)});
    }
    return out;
}
const Region* find(const std::vector<Region>& maps, const void* p) { uint64_t a = (uint64_t)p; for (auto& r : maps) if (a >= r.start && a < r.end) return &r; return nullptr; }
int global = 5;
void code() {}

int main() {
#if defined(__linux__)
    auto maps = readMaps();
    assert(!maps.empty());
    int local = 0; int* heap = new int(1);
    const Region *stack = find(maps, &local), *text = find(maps, (void*)&code), *data = find(maps, &global), *hp = find(maps, heap);
    assert(stack && stack->name == "[stack]" && stack->perms[0] == 'r' && stack->perms[1] == 'w' && stack->perms[2] == '-');   // 스택: 읽기+쓰기, 실행 불가
    assert(text && text->perms[2] == 'x' && text->perms[1] == '-');                   // 코드: 실행 가능, 쓰기 불가 (W^X)
    assert(data && data->perms[1] == 'w' && data->perms[2] == '-');                   // 전역 변수: 쓰기 가능, 실행 불가
    assert(hp && hp->perms[1] == 'w');                                                // 힙(brk 또는 mmap 영역)
    std::cout << "ProcessMemory: stack=" << stack->name << " text perms=" << text->perms << " data perms=" << data->perms << " heap region=" << (hp->name.empty() ? "[anon]" : hp->name) << std::endl;
    delete heap;
#else
    std::cout << "ProcessMemory: Linux-only demonstration (/proc/self/maps)" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(영역 수)
// Space Complexity: O(영역 수)
```
## ThreadLocalStorage()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <thread>
#include <mutex>
#include <vector>
#include <cassert>

// 스레드 지역 저장소(TLS): thread_local 변수는 스레드마다 별도의 복사본이 있다 -> 락 없이 스레드별 상태(errno, 난수 생성기 상태, 캐시)를 유지한다.
// 스레드가 시작할 때 초기화되고 끝날 때 소멸자가 불린다.  공유 변수와 달리 경쟁 상태가 없다
thread_local int counter = 100;
std::mutex mu; std::set<const void*> addresses; int ctors = 0, dtors = 0;
struct PerThread { PerThread() { std::lock_guard<std::mutex> g(mu); ctors++; } ~PerThread() { std::lock_guard<std::mutex> g(mu); dtors++; } };
thread_local PerThread tls;

int main() {
    counter = 1;                                                       // 메인 스레드의 사본만 바뀐다
    std::vector<std::thread> th; int results[4];
    for (int t = 0; t < 4; t++)
        th.emplace_back([&, t] {
            (void)tls;                                                  // 이 스레드의 tls 객체 생성
            assert(counter == 100);                                     // 각 스레드는 초기값 100 으로 시작 (메인의 1 과 무관)
            for (int i = 0; i < 1000; i++) counter++;                   // 락 없이 증가해도 경쟁 없음
            results[t] = counter;
            std::lock_guard<std::mutex> g(mu); addresses.insert(&counter);
        });
    for (auto& x : th) x.join();
    for (int t = 0; t < 4; t++) assert(results[t] == 1100);
    assert(counter == 1);                                               // 메인의 값은 영향 없음
    assert(addresses.size() == 4);                                      // 스레드마다 주소가 다르다
    assert(ctors == 4 && dtors == 4);                                   // 스레드 종료 시 소멸자 호출
    std::cout << "ThreadLocalStorage: 4 threads, 4 distinct copies, no locking." << std::endl;
    return 0;
}
// Time Complexity: 접근 O(1) (세그먼트 레지스터 기준 오프셋)
// Space Complexity: 스레드 수 · 변수 크기
```
## KernelMemory()
### 대표코드
```cpp
#include <iostream>
#include <cerrno>
#include <cstdint>
#include <cassert>
#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <unistd.h>
#endif

// 커널 메모리: x86-64 에서 가상 주소 공간의 위쪽 절반(0xFFFF8000... 이상)은 커널의 것이다.  사용자 모드 코드는 접근할 수 없고, 접근하려 하면 예외가 난다.
// 시스템 호출에서 사용자가 넘긴 포인터를 커널이 그대로 믿으면 안 되므로 항상 검증한다(access_ok, copy_from_user).
// 잘못된 사용자 포인터를 write 로 넘기면 프로세스가 죽지 않고 EFAULT 오류가 돌아온다 — 커널이 검증했다는 증거
bool userSpace(uint64_t va) { return va < 0x0000800000000000ULL; }

int main() {
    assert(userSpace(0x00007fffffffffffULL) && !userSpace(0xffff800000000000ULL) && !userSpace(0xffffffff81000000ULL));
    int local; assert(userSpace((uint64_t)&local));                       // 우리 변수는 사용자 영역
#if defined(__unix__) || defined(__APPLE__)
    int devnull = open("/dev/null", O_WRONLY);
    void* kernelPtr = (void*)0xffffffff81000000ULL;                       // 커널 영역 주소 (읽으려 하지 않고 시스템 호출에 그대로 넘긴다)
    ssize_t r = write(devnull, kernelPtr, 16);
    assert(r == -1 && errno == EFAULT);                                   // 커널이 사용자 포인터를 검증해 거부했다
    char ok[16] = {0};
    assert(write(devnull, ok, sizeof ok) == (ssize_t)sizeof ok);          // 정상 포인터는 통과
    close(devnull);
#endif
    std::cout << "KernelMemory: kernel-space pointer rejected with EFAULT." << std::endl;
    return 0;
}
// Time Complexity: O(1) 주소 검증
// Space Complexity: O(1)
```
## UserMemory()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cassert>
#if defined(__linux__)
#include <sys/mman.h>
#include <sys/resource.h>
#endif

// 사용자 메모리: 프로세스가 쓰는 가상 주소 공간.  가상 크기(주소 공간 예약)와 실제 사용량(RSS, 물리 메모리)은 다르다.
// 운영체제는 보통 과다 할당(overcommit)을 허용해 예약만 해 두고 실제로 만질 때 물리 메모리를 준다.  한도는 getrlimit(RLIMIT_AS / RLIMIT_STACK ...) 로 본다
int main() {
#if defined(__linux__)
    struct rlimit stack, as; getrlimit(RLIMIT_STACK, &stack); getrlimit(RLIMIT_AS, &as);
    assert(stack.rlim_cur > 0);                                           // 보통 8MB
    // 64GiB 의 주소 공간을 예약만 한다 (PROT_NONE + MAP_NORESERVE: 물리 메모리도 커밋도 쓰지 않는다)
    size_t huge = 64ULL << 30;
    void* p = mmap(nullptr, huge, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
    if (p != MAP_FAILED) {
        assert(mprotect(p, 4096, PROT_READ | PROT_WRITE) == 0);           // 필요한 앞쪽 한 페이지만 쓸 수 있게 열고
        ((char*)p)[0] = 1; assert(((char*)p)[0] == 1);                    // 만진 페이지만 물리 메모리를 쓴다
        munmap(p, huge);
        std::cout << "UserMemory: reserved " << (huge >> 30) << " GiB of address space, used 1 page" << std::endl;
    } else {
        std::cout << "UserMemory: address-space limit prevents the large reservation here (RLIMIT_AS = " << as.rlim_cur << ")" << std::endl;
    }
#else
    std::cout << "UserMemory: Linux-only demonstration" << std::endl;
#endif
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 예약은 무료, 사용한 페이지만 비용
```
## NUMAMemory()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// NUMA(Non-Uniform Memory Access): 멀티 소켓 서버에서 CPU 마다 가까운 메모리(로컬 노드)가 있고, 다른 소켓의 메모리(원격 노드)는 접근이 느리다(보통 1.5~2배 이상).
// 운영체제의 기본 정책은 first-touch: 페이지를 "처음 만진 스레드가 있는 노드" 에 배치한다.  초기화를 한 스레드가 도맡으면 모든 페이지가 한 노드에 몰려 다른 노드의 스레드는 전부 원격 접근을 한다.
// 노드 2개, 로컬 비용 10, 원격 비용 20 의 비용 모델로 세 정책을 비교한다
const int LOCAL = 10, REMOTE = 20;
struct Result { long cost; };

long totalCost(const std::vector<int>& pageNode, int threadNodeOfFirstHalf, int threadNodeOfSecondHalf) {
    long cost = 0; int n = pageNode.size();
    for (int p = 0; p < n; p++) {
        int threadNode = p < n / 2 ? threadNodeOfFirstHalf : threadNodeOfSecondHalf;       // 스레드 0 은 앞 절반, 스레드 1 은 뒤 절반을 처리
        cost += (pageNode[p] == threadNode ? LOCAL : REMOTE) * 1000;                       // 페이지당 1000회 접근
    }
    return cost;
}

int main() {
    const int pages = 8;
    std::vector<int> allOnZero(pages, 0), interleave(pages), firstTouch(pages);
    for (int p = 0; p < pages; p++) { interleave[p] = p % 2; firstTouch[p] = p < pages / 2 ? 0 : 1; }   // first-touch: 각 스레드가 자기 몫을 직접 초기화
    long bad = totalCost(allOnZero, 0, 1);                  // 한 스레드가 전부 초기화: 노드 1 의 스레드는 모두 원격
    long inter = totalCost(interleave, 0, 1);               // 라운드 로빈 인터리브: 접근의 절반이 원격 (평균 지연은 단일 노드와 같지만 메모리 대역폭을 두 노드에 분산)
    long good = totalCost(firstTouch, 0, 1);                // 자기 데이터는 자기 노드에: 전부 로컬
    assert(good < inter && inter == bad);                   // 지연 시간만 보면 인터리브 == 한 노드에 몰기 (이 모델은 대역폭 포화를 포함하지 않는다)
    assert(good == (long)pages * LOCAL * 1000 && bad == (long)(pages / 2) * (LOCAL + REMOTE) * 1000);
    std::cout << "NUMA cost: first-touch(parallel init)=" << good << " interleave=" << inter << " single-node=" << bad << std::endl;
    return 0;
}
// Time Complexity: O(페이지 수)
// Space Complexity: O(페이지 수)
```
# Part 15. 현대 시스템
## GPUMemory()
### 대표코드
```cpp
#include <iostream>
#include <numeric>
#include <set>
#include <vector>
#include <cassert>

// GPU 메모리: 32 스레드(워프)가 한 명령을 동시에 실행한다.
//  전역 메모리 병합(coalescing): 워프의 접근이 연속된 128바이트 구간에 모이면 메모리 트랜잭션이 1번, 흩어지면 구간 수만큼 늘어난다.
//  공유 메모리 뱅크 충돌: 32개 뱅크(4바이트 단위 주소 % 32) 중 같은 뱅크의 서로 다른 주소를 여러 스레드가 동시에 접근하면 직렬화된다.
int transactions(int stride) {                                       // 스레드 t 가 float[t * stride] 를 읽을 때 건드리는 128B 구간 수
    std::set<long> segs; for (int t = 0; t < 32; t++) segs.insert((long)t * stride * 4 / 128); return segs.size();
}
int bankConflictDegree(int stride) {                                 // 스레드 t 가 word[t * stride] 에 접근할 때 같은 뱅크에 몰리는 최대 스레드 수
    std::vector<int> perBank(32, 0); for (int t = 0; t < 32; t++) perBank[(t * stride) % 32]++;
    int mx = 0; for (int c : perBank) mx = std::max(mx, c); return mx;
}

int main() {
    assert(transactions(1) == 1 && transactions(2) == 2 && transactions(4) == 4 && transactions(32) == 32);   // 간격이 클수록 병합 실패
    assert(bankConflictDegree(1) == 1);                              // 연속 접근: 충돌 없음
    assert(bankConflictDegree(2) == 2 && bankConflictDegree(32) == 32);   // 2-way, 32-way 충돌
    assert(bankConflictDegree(33) == 1);                             // 32x32 타일의 한 줄에 패딩 1칸(폭 33)을 주면 열 접근도 충돌이 사라진다
    for (int s = 1; s <= 64; s++) assert(bankConflictDegree(s) == std::gcd(s, 32));   // 충돌 정도 = gcd(stride, 32)
    std::cout << "GPUMemory: stride-1 -> " << transactions(1) << " transaction; stride-32 -> " << transactions(32) << "; tile padding 33 removes the 32-way conflict" << std::endl;
    return 0;
}
// Time Complexity: O(32)
// Space Complexity: O(1)
```
## UnifiedMemory()
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 통합 메모리(CUDA Unified Memory): CPU 와 GPU 가 같은 포인터를 쓰고, 페이지가 필요한 쪽으로 자동 이동(migration)한다.
// 프로그래머는 편하지만, 상대편이 페이지를 만지는 순간마다 페이지 폴트와 이동 비용이 든다.  미리 옮기는 힌트(prefetch)를 주면 폴트가 사라진다
enum Where { HOST, DEVICE };
struct UM {
    std::vector<Where> loc; long faults = 0, bulkMoves = 0;
    explicit UM(int pages) : loc(pages, HOST) {}
    void touch(int page, Where who) { if (loc[page] != who) { faults++; loc[page] = who; } }                 // 요구 이동: 폴트 1번
    void prefetch(int first, int count, Where to) { bool any = false; for (int i = first; i < first + count; i++) if (loc[i] != to) { loc[i] = to; any = true; } if (any) bulkMoves++; }   // 한 번에 묶어서 이동
};

int main() {
    const int N = 256;
    UM onDemand(N), hinted(N);
    for (int p = 0; p < N; p++) onDemand.touch(p, HOST);               // CPU 가 초기화
    for (int p = 0; p < N; p++) onDemand.touch(p, DEVICE);             // GPU 커널이 처리: 페이지마다 폴트
    for (int p = 0; p < N; p++) onDemand.touch(p, HOST);               // CPU 가 결과 읽기: 다시 페이지마다 폴트
    for (int p = 0; p < N; p++) hinted.touch(p, HOST);
    hinted.prefetch(0, N, DEVICE);                                      // 커널 실행 전에 한꺼번에 이동
    for (int p = 0; p < N; p++) hinted.touch(p, DEVICE);
    hinted.prefetch(0, N, HOST);                                        // 결과를 읽기 전에 한꺼번에 이동
    for (int p = 0; p < N; p++) hinted.touch(p, HOST);
    assert(onDemand.faults == 2 * N);                                   // 요구 이동: 페이지당 2번 폴트
    assert(hinted.faults == 0 && hinted.bulkMoves == 2);                // 힌트: 폴트 0, 대량 이동 2번
    std::cout << "UnifiedMemory: on-demand faults=" << onDemand.faults << ", with prefetch faults=" << hinted.faults << " (2 bulk moves)" << std::endl;
    return 0;
}
// Time Complexity: O(페이지 수)
// Space Complexity: O(페이지 수)
```
## PersistentMemory()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <functional>
#include <vector>
#include <cassert>

// 영속 메모리(Intel Optane 등): 바이트 주소 접근이 되면서 전원이 꺼져도 남는다.  단 CPU 캐시는 휘발성이라, 저장 후 캐시 라인을 NVM 으로 내리는(clwb + sfence) 순서를 직접 지켜야 한다.
// 캐시는 아무 때나 줄을 내보낼 수 있어서 "저장 순서" 가 곧 "영속 순서" 가 아니다 -> 원자성은 로그로 확보: (1) 옛 값을 로그에 영속시키고 (2) 유효 표시 (3) 데이터 수정 (4) 로그 무효화.
// 시뮬레이터가 가능한 모든 충돌 시점 × 아직 내려가지 않은 줄의 모든 영속 조합을 열거하며 복구 후 불변식(A+B == 100)을 검사한다
const int A = 0, B = 1, LOG_A = 2, LOG_B = 3, VALID = 4, WORDS = 5;
struct Nvm {
    uint64_t persisted[WORDS] = {50, 50, 0, 0, 0}; uint64_t cache[WORDS] = {50, 50, 0, 0, 0}; bool dirty[WORDS] = {};
    void store(int i, uint64_t v) { cache[i] = v; dirty[i] = true; }
    void persist(int i) { persisted[i] = cache[i]; dirty[i] = false; }          // clwb + sfence: 이 줄은 확실히 NVM 에
};
typedef std::vector<std::function<void(Nvm&)>> Program;

void recover(uint64_t p[WORDS]) { if (p[VALID]) { p[A] = p[LOG_A]; p[B] = p[LOG_B]; p[VALID] = 0; } }   // 로그가 유효하면 옛 값으로 되돌린다

// 프로그램의 모든 접두 지점에서 충돌시키고, 남은 dirty 줄이 임의의 부분집합만 영속되었다고 가정해 복구 결과를 검사한다
bool crashConsistent(const Program& prog, bool useRecovery) {
    for (size_t k = 0; k <= prog.size(); k++) {
        Nvm m; for (size_t i = 0; i < k; i++) prog[i](m);
        std::vector<int> dirty; for (int i = 0; i < WORDS; i++) if (m.dirty[i]) dirty.push_back(i);
        for (unsigned mask = 0; mask < (1u << dirty.size()); mask++) {
            uint64_t state[WORDS]; for (int i = 0; i < WORDS; i++) state[i] = m.persisted[i];
            for (size_t d = 0; d < dirty.size(); d++) if (mask >> d & 1) state[dirty[d]] = m.cache[dirty[d]];
            if (useRecovery) recover(state);
            bool ok = (state[A] == 50 && state[B] == 50) || (state[A] == 40 && state[B] == 60);   // 이체 전 또는 이체 후만 허용
            if (!ok) return false;
        }
    }
    return true;
}

int main() {
    Program naive = {                                                   // 로그 없이 두 값을 차례로 수정
        [](Nvm& m) { m.store(A, 40); m.persist(A); },
        [](Nvm& m) { m.store(B, 60); m.persist(B); }};
    assert(!crashConsistent(naive, true));                             // A 만 반영되고 충돌하면 합계가 깨진다 (A=40, B=50)

    Program undoLog = {                                                 // 실행 취소(undo) 로그 프로토콜
        [](Nvm& m) { m.store(LOG_A, m.cache[A]); m.store(LOG_B, m.cache[B]); },
        [](Nvm& m) { m.persist(LOG_A); m.persist(LOG_B); },            // 옛 값을 먼저 영속
        [](Nvm& m) { m.store(VALID, 1); m.persist(VALID); },           // 그 다음에 로그 유효 표시
        [](Nvm& m) { m.store(A, 40); m.store(B, 60); },                // 데이터 수정 (캐시에서 임의 순서로 내려갈 수 있다)
        [](Nvm& m) { m.persist(A); m.persist(B); },
        [](Nvm& m) { m.store(VALID, 0); m.persist(VALID); }};          // 마지막으로 로그 무효화
    assert(crashConsistent(undoLog, true));                            // 모든 충돌 시점·영속 조합에서 복구 후 불변식 유지
    assert(!crashConsistent(undoLog, false));                          // 복구 단계를 빼면 중간 상태가 그대로 노출된다
    std::cout << "PersistentMemory: undo-log protocol is crash-consistent for every crash point and eviction subset." << std::endl;
    return 0;
}
// Time Complexity: 검증 O(단계 · 2^dirty)
// Space Complexity: O(1) 로그
```
## HugePage()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cassert>
#if defined(__linux__)
#include <sys/mman.h>
#endif

// 대형 페이지(2MB / 1GB): 페이지가 클수록 TLB 항목 하나가 덮는 범위(TLB reach)가 커져 TLB 미스와 페이지 테이블 크기가 줄어든다.
//   TLB reach = 항목 수 x 페이지 크기.   데이터베이스·JVM·HPC 처럼 큰 메모리를 쓰는 프로그램에서 수 %~수십 % 성능 향상.
// 단점: 페이지 단위 보호/스왑이 거칠어지고, 큰 연속 물리 메모리가 필요하며 내부 단편화가 커진다.  리눅스는 Transparent Huge Pages(THP)와 madvise(MADV_HUGEPAGE)를 제공
int main() {
    const uint64_t KB = 1024, MB = KB * 1024, GB = MB * 1024;
    const uint64_t entries = 64;
    assert(entries * 4 * KB == 256 * KB);                              // 4KB 페이지: 64 항목이 겨우 256KB 를 덮는다
    assert(entries * 2 * MB == 128 * MB);                              // 2MB 페이지: 512배
    assert(entries * 1 * GB == 64 * GB);
    assert(GB / (4 * KB) == 262144 && GB / (2 * MB) == 512);           // 1GB 를 매핑하는 데 필요한 페이지 항목 수: 262144 vs 512
    assert(GB / (4 * KB) * 8 == 2 * MB && GB / (2 * MB) * 8 == 4 * KB);   // 항목당 8바이트: 말단 테이블 2MB vs 4KB
#if defined(__linux__)
    size_t len = 4 * MB;
    void* p = mmap(nullptr, len + 2 * MB, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p != MAP_FAILED) {
        uintptr_t aligned = ((uintptr_t)p + 2 * MB - 1) & ~(uintptr_t)(2 * MB - 1);   // 2MB 경계로 정렬 (대형 페이지의 조건)
        int rc = madvise((void*)aligned, len, MADV_HUGEPAGE);             // 커널에 "대형 페이지를 써도 좋다" 고 알린다 (시스템 설정에 따라 무시될 수 있음)
        *(volatile char*)aligned = 1;
        std::cout << "HugePage: madvise(MADV_HUGEPAGE) returned " << rc << " (kernel may or may not back it with a huge page)" << std::endl;
        munmap(p, len + 2 * MB);
    }
#endif
    std::cout << "HugePage: TLB reach 4KB=" << entries * 4 * KB / KB << "KB, 2MB=" << entries * 2 * MB / MB << "MB, 1GB=" << entries * GB / GB << "GB" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 페이지 테이블 크기가 1/512 로 감소
```
## RDMA()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <map>
#include <stdexcept>
#include <vector>
#include <cassert>

// RDMA(원격 직접 메모리 접근): 네트워크 카드(NIC)가 원격 노드의 메모리를 상대 CPU 와 운영체제의 개입 없이 직접 읽고 쓴다 (InfiniBand, RoCE).  커널 우회·제로 카피로 지연이 마이크로초 수준.
// 흐름: (1) 메모리 영역을 NIC 에 등록(고정, pinned) -> rkey 발급 (2) rkey 와 원격 주소를 상대에게 전달 (3) RDMA_WRITE/READ 를 보내면 상대의 NIC 가 rkey·범위·권한을 검사하고 처리
// 아래는 verbs 의 핵심 의미만 흉내 낸 모델이다 (실제 API: ibv_reg_mr, ibv_post_send)
enum Access { LOCAL_WRITE = 1, REMOTE_READ = 2, REMOTE_WRITE = 4 };
struct Region { std::vector<uint8_t> mem; unsigned access; };
class Node {
    std::map<uint32_t, Region> mr; uint32_t nextKey = 0x100;
public:
    long cpuInvolvements = 0;                                        // 이 노드의 CPU 가 처리에 관여한 횟수 (RDMA 에서는 0)
    uint32_t registerRegion(size_t bytes, unsigned access) { mr[nextKey] = Region{std::vector<uint8_t>(bytes, 0), access}; return nextKey++; }
    uint8_t* local(uint32_t key) { return mr.at(key).mem.data(); }
    // 상대 NIC 가 수행하는 검사 (수신 노드의 CPU 는 호출되지 않는다)
    void nicWrite(uint32_t rkey, size_t off, const void* src, size_t n) {
        auto it = mr.find(rkey); if (it == mr.end()) throw std::runtime_error("invalid rkey");
        if (!(it->second.access & REMOTE_WRITE)) throw std::runtime_error("remote write not permitted");
        if (off + n > it->second.mem.size()) throw std::runtime_error("out of bounds");
        std::memcpy(&it->second.mem[off], src, n);
    }
    void nicRead(uint32_t rkey, size_t off, void* dst, size_t n) {
        auto it = mr.find(rkey); if (it == mr.end()) throw std::runtime_error("invalid rkey");
        if (!(it->second.access & REMOTE_READ)) throw std::runtime_error("remote read not permitted");
        if (off + n > it->second.mem.size()) throw std::runtime_error("out of bounds");
        std::memcpy(dst, &it->second.mem[off], n);
    }
};
template <class F> bool fails(F f) { try { f(); } catch (const std::runtime_error&) { return true; } return false; }

int main() {
    Node client, server;
    uint32_t rkey = server.registerRegion(64, REMOTE_READ | REMOTE_WRITE);
    uint32_t roKey = server.registerRegion(64, REMOTE_READ);
    const char msg[] = "hello rdma";
    server.nicWrite(rkey, 8, msg, sizeof msg);                        // 클라이언트가 서버 메모리에 직접 쓴다 (서버 CPU 는 코드를 실행하지 않는다)
    char back[16] = {0};
    server.nicRead(rkey, 8, back, sizeof msg);                         // 직접 읽어 온다
    assert(std::strcmp(back, "hello rdma") == 0 && server.cpuInvolvements == 0);
    assert(std::memcmp(server.local(rkey) + 8, msg, sizeof msg) == 0); // 서버의 메모리에 실제로 반영됨
    assert(fails([&] { server.nicWrite(0xdead, 0, msg, 4); }));        // 알 수 없는 rkey
    assert(fails([&] { server.nicWrite(roKey, 0, msg, 4); }));         // 읽기 전용으로 등록된 영역에 쓰기
    assert(fails([&] { server.nicWrite(rkey, 62, msg, 8); }));         // 범위 초과
    (void)client;
    std::cout << "RDMA: remote write/read completed without involving the target CPU; invalid access rejected by the NIC." << std::endl;
    return 0;
}
// Time Complexity: O(n) 복사 (NIC 가 DMA)
// Space Complexity: 등록된 영역(고정 메모리)
```
## MemoryCompression()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <random>
#include <vector>
#include <cassert>

// 메모리 압축(zram, macOS 압축 메모리): 쫓겨날 페이지를 디스크 스왑 대신 RAM 안의 압축 풀에 저장한다.  디스크보다 수백 배 빠르고 RAM 을 아낀다.
// 0 으로 찬 페이지는 매우 흔해 특수 처리하고, 압축이 안 되는 페이지(난수, 이미 압축된 데이터)는 압축본이 더 크므로 원본 그대로 저장한다.
// 압축기는 간단한 LZ77: 이전에 나온 바이트열과 같으면 (거리, 길이) 로 대체한다
typedef std::vector<uint8_t> Bytes;
Bytes compress(const Bytes& in) {
    Bytes out; size_t i = 0;
    while (i < in.size()) {
        size_t bestLen = 0, bestDist = 0;
        for (size_t d = 1; d <= std::min<size_t>(i, 255); d++) {          // 뒤로 최대 255 바이트 내에서 가장 긴 일치를 찾는다
            size_t l = 0; while (i + l < in.size() && l < 255 && in[i + l] == in[i + l - d]) l++;
            if (l > bestLen) { bestLen = l; bestDist = d; }
        }
        if (bestLen >= 4) { out.push_back(1); out.push_back((uint8_t)bestDist); out.push_back((uint8_t)bestLen); i += bestLen; }   // 일치 토큰
        else { out.push_back(0); out.push_back(in[i]); i++; }                                                                      // 리터럴 토큰
    }
    return out;
}
Bytes decompress(const Bytes& c) {
    Bytes out;
    for (size_t i = 0; i < c.size();) {
        if (c[i] == 0) { out.push_back(c[i + 1]); i += 2; }
        else { size_t d = c[i + 1], l = c[i + 2]; for (size_t k = 0; k < l; k++) out.push_back(out[out.size() - d]); i += 3; }
    }
    return out;
}
struct Slot { bool raw; bool zero; Bytes data; };
Slot swapOut(const Bytes& page) {
    bool allZero = true; for (uint8_t b : page) if (b) { allZero = false; break; }
    if (allZero) return {false, true, {}};                                 // 0 페이지: 저장 공간 0 바이트
    Bytes c = compress(page);
    if (c.size() >= page.size()) return {true, false, page};              // 압축 이득이 없으면 원본 보관
    return {false, false, c};
}
Bytes swapIn(const Slot& s, size_t pageSize) { return s.zero ? Bytes(pageSize, 0) : s.raw ? s.data : decompress(s.data); }

int main() {
    const size_t PAGE = 4096; std::mt19937 rng(3);
    Bytes zero(PAGE, 0), text(PAGE), random(PAGE);
    for (size_t i = 0; i < PAGE; i++) { text[i] = "the quick brown fox "[i % 20]; random[i] = rng(); }
    Slot z = swapOut(zero), t = swapOut(text), r = swapOut(random);
    assert(z.zero && z.data.empty());                                      // 0 페이지는 공간 0
    assert(!t.raw && t.data.size() < PAGE / 10);                           // 반복되는 텍스트는 10배 이상 줄어든다
    assert(r.raw && r.data.size() == PAGE);                                // 난수 페이지는 압축 불가 -> 원본
    assert(swapIn(z, PAGE) == zero && swapIn(t, PAGE) == text && swapIn(r, PAGE) == random);   // 복원은 항상 정확
    std::cout << "MemoryCompression: text page " << PAGE << " -> " << t.data.size() << " bytes, zero page -> 0, random page stored raw" << std::endl;
    return 0;
}
// Time Complexity: 압축 O(n · 창 크기), 복원 O(n)
// Space Complexity: O(n)
```
# Part 16. 연구 주제
## GarbageFirstGC()
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <vector>
#include <cassert>

// G1(Garbage-First): 힙을 같은 크기의 영역(region) 수백 개로 나누고, 영역별로 "얼마나 쓰레기인지" 를 추적한다.
// 수집할 때 전체가 아니라 "쓰레기 비율이 높은(회수 이득 / 복사 비용이 큰) 영역부터" 일시 정지 목표 시간 안에 처리할 만큼만 골라 수집한다 -> 정지 시간을 예측 가능하게 만든다.
// 복사 비용 = 살아있는 바이트, 이득 = 쓰레기 바이트
struct Region { int id; int liveKB, garbageKB; };
std::vector<int> pickCollectionSet(std::vector<Region> regions, int budgetKB) {                    // budgetKB: 이번 정지에서 복사할 수 있는 살아있는 바이트 한도
    std::sort(regions.begin(), regions.end(), [](const Region& a, const Region& b) { return (double)a.garbageKB / (a.liveKB + 1) > (double)b.garbageKB / (b.liveKB + 1); });
    std::vector<int> chosen; int spent = 0;
    for (auto& r : regions) if (spent + r.liveKB <= budgetKB && r.garbageKB > 0) { chosen.push_back(r.id); spent += r.liveKB; }
    return chosen;
}
int reclaimed(const std::vector<Region>& regions, const std::vector<int>& ids) { int s = 0; for (int id : ids) s += regions[id].garbageKB; return s; }

int main() {
    // 영역마다 (살아있는 KB = 복사 비용, 쓰레기 KB = 회수 이득)
    std::vector<Region> heap = {{0, 350, 650}, {1, 100, 400}, {2, 100, 500}, {3, 150, 350}, {4, 900, 100}};
    auto g1 = pickCollectionSet(heap, 400);                               // 복사 예산 400KB
    std::sort(g1.begin(), g1.end());
    assert((g1 == std::vector<int>{1, 2, 3}));                             // 이득/비용 비율이 높은 영역 2, 1, 3 (복사 비용 100 + 100 + 150 = 350)
    // 비교: "쓰레기 양이 가장 많은 영역부터" 고르는 방식 — 영역 0 (쓰레기 650)이 비용 350 으로 예산을 거의 다 써 버린다
    std::vector<Region> byAmount = heap;
    std::sort(byAmount.begin(), byAmount.end(), [](const Region& a, const Region& b) { return a.garbageKB > b.garbageKB; });
    std::vector<int> naive; int spent = 0;
    for (auto& r : byAmount) if (spent + r.liveKB <= 400) { naive.push_back(r.id); spent += r.liveKB; }
    assert((naive == std::vector<int>{0}));
    assert(reclaimed(heap, g1) == 500 + 400 + 350 && reclaimed(heap, g1) > reclaimed(heap, naive));   // 같은 복사 예산으로 1250KB vs 650KB
    std::cout << "G1: collection set {1,2,3} reclaims " << reclaimed(heap, g1) << " KB vs " << reclaimed(heap, naive) << " KB for garbage-amount-first" << std::endl;
    return 0;
}
// Time Complexity: O(R log R) (R = 영역 수)
// Space Complexity: O(R)
```
## ZGC()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <unordered_map>
#include <cassert>

// ZGC: 포인터 자체에 "색(color)" 메타데이터 비트를 넣고(colored pointers), 객체를 읽을 때마다 로드 장벽(load barrier)이 색을 검사한다.
// 객체를 이동(재배치)하는 동안에도 프로그램이 돌아가며, 오래된 포인터를 읽는 순간 장벽이 새 주소를 찾아 그 필드를 고쳐 쓴다(self-healing) -> 정지 시간이 힙 크기와 무관(밀리초 미만).
// 색 비트 하나(good color)를 전역으로 바꾸면 "모든 포인터가 낡은 것" 이 되고, 이후 각 포인터는 처음 읽힐 때 한 번씩만 느린 경로를 탄다
const uint64_t ADDR_MASK = (1ULL << 42) - 1, COLOR_SHIFT = 42;
uint64_t goodColor = 1;                                                     // 현재 유효한 색 (1 = 사이클 A, 2 = 사이클 B)
uint64_t colored(uint64_t addr, uint64_t color) { return addr | color << COLOR_SHIFT; }
uint64_t addrOf(uint64_t p) { return p & ADDR_MASK; }
uint64_t colorOf(uint64_t p) { return p >> COLOR_SHIFT; }

std::unordered_map<uint64_t, uint64_t> forwarding;                          // 재배치된 객체의 옛 주소 -> 새 주소
long slowPaths = 0, fastPaths = 0;
uint64_t loadBarrier(uint64_t* field) {
    uint64_t p = *field;
    if (colorOf(p) == goodColor) { fastPaths++; return addrOf(p); }         // 빠른 경로: 색이 맞으면 그대로
    slowPaths++;                                                             // 느린 경로: 새 주소를 찾아 자기 치유
    uint64_t a = addrOf(p); auto it = forwarding.find(a); if (it != forwarding.end()) a = it->second;
    *field = colored(a, goodColor);                                         // 필드를 올바른 주소·색으로 고쳐 쓴다
    return a;
}

int main() {
    uint64_t fieldA = colored(0x1000, goodColor), fieldB = colored(0x1000, goodColor);   // 같은 객체를 가리키는 포인터 두 개
    assert(loadBarrier(&fieldA) == 0x1000 && slowPaths == 0 && fastPaths == 1);
    // GC 가 0x1000 의 객체를 0x2000 으로 옮기고 전역 색을 바꾼다
    forwarding[0x1000] = 0x2000; goodColor = 2;
    assert(loadBarrier(&fieldA) == 0x2000 && slowPaths == 1);              // 낡은 포인터를 읽는 순간 새 주소를 얻는다
    assert(colorOf(fieldA) == goodColor && addrOf(fieldA) == 0x2000);       // 필드가 고쳐졌다 (self-healing)
    assert(loadBarrier(&fieldA) == 0x2000 && slowPaths == 1);              // 다음부터는 빠른 경로
    assert(loadBarrier(&fieldB) == 0x2000 && slowPaths == 2);              // 다른 낡은 포인터도 처음 읽을 때 한 번만 느린 경로
    std::cout << "ZGC: slow paths=" << slowPaths << ", fast paths=" << fastPaths << " (each stale pointer healed once)" << std::endl;
    return 0;
}
// Time Complexity: 빠른 경로 O(1) 비교, 느린 경로 O(1) 조회
// Space Complexity: 포인터 상위 비트 + 전달 테이블
```
## ShenandoahGC()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <vector>
#include <cassert>

// Shenandoah: 모든 객체 앞에 Brooks 전달 포인터(forwarding pointer)를 둔다.  평소에는 자기 자신을 가리키고, 객체가 이동하면 새 사본을 가리킨다.
// 프로그램은 항상 "전달 포인터를 한 번 따라간 뒤" 읽고 쓰므로, GC 가 동시에 객체를 옮겨도 읽는 쪽과 쓰는 쪽이 같은 사본을 보게 된다.
// 이동은 CAS 로 전달 포인터를 바꾸는 쪽이 이기게 하여 여러 스레드가 동시에 같은 객체를 옮기려 해도 사본이 하나만 유효하다
struct Obj { std::atomic<Obj*> fwd; int value; Obj(int v) : fwd(this), value(v) {} };
Obj* resolve(Obj* o) { return o->fwd.load(); }                              // 모든 접근의 첫 단계
int read(Obj* o) { return resolve(o)->value; }
void write(Obj* o, int v) { resolve(o)->value = v; }
Obj* evacuate(Obj* o, std::vector<Obj*>& heap) {                            // 사본을 만들고, 전달 포인터 CAS 에 성공한 쪽만 채택
    Obj* copy = new Obj(o->value); heap.push_back(copy);
    Obj* expected = o;
    if (o->fwd.compare_exchange_strong(expected, copy)) return copy;         // 내가 이겼다
    return expected;                                                          // 다른 스레드가 먼저 옮겼다: 그 사본을 사용 (내 사본은 버림)
}

int main() {
    std::vector<Obj*> heap; Obj* a = new Obj(10); heap.push_back(a);
    assert(read(a) == 10 && resolve(a) == a);                                 // 이동 전: 전달 포인터는 자기 자신
    Obj* moved = evacuate(a, heap);                                           // GC 가 객체를 이동
    assert(resolve(a) == moved && moved != a);
    write(a, 99);                                                             // 뮤테이터는 옛 주소 a 로 쓰지만 전달 포인터를 따라 새 사본에 쓰인다
    assert(moved->value == 99 && read(a) == 99);                              // 새 사본에 반영되고, 옛 주소로 읽어도 최신 값
    assert(a->value == 10);                                                   // 옛 사본은 더 이상 쓰이지 않는다 (낡은 값)
    Obj* second = evacuate(a, heap);                                          // 두 번째 이동 시도 -> 이미 이동됨: 기존 사본을 돌려준다
    assert(second == moved && resolve(a) == moved);
    std::cout << "ShenandoahGC: accesses through the forwarding pointer saw the relocated copy; duplicate evacuation lost the CAS." << std::endl;
    return 0;
}
// Time Complexity: 접근마다 포인터 한 번 더 (간접 참조 비용)
// Space Complexity: 객체당 포인터 하나
```
## RegionBasedMemory()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <cassert>

// 리전 기반 메모리 관리(Tofte–Talpin): 객체를 개별로 해제하지 않고 "리전" 에 모아 두었다가 리전이 끝나는 순간 한꺼번에 해제한다.
// 리전은 스택처럼 중첩되어 만들어지고 역순으로 사라진다 -> 해제 비용 O(1), 단편화 없음, GC 불필요.  타입 시스템이 "리전보다 오래 사는 참조" 를 막는다 (Rust 의 수명, 컴파일러의 아레나)
struct Obj { std::string name; };
class Region {
    std::vector<std::unique_ptr<Obj>> objs; bool alive = true; Region* parent;
public:
    static int liveObjects;
    explicit Region(Region* p = nullptr) : parent(p) {}
    ~Region() { liveObjects -= objs.size(); alive = false; }                // 리전이 사라지면 안의 객체가 모두 사라진다
    Obj* make(const std::string& n) { if (!alive) throw std::logic_error("region freed"); objs.push_back(std::make_unique<Obj>(Obj{n})); liveObjects++; return objs.back().get(); }
    // 안쪽(수명이 짧은) 리전의 객체를 바깥(수명이 긴) 리전에 저장하려는 시도는 허용하지 않는다
    static void assertOutlives(const Region& longer, const Region* shorter) { for (const Region* r = shorter; r; r = r->parent) if (r == &longer) return; throw std::logic_error("reference would outlive its region"); }
};
int Region::liveObjects = 0;

int main() {
    Region outer;
    outer.make("global-config");
    assert(Region::liveObjects == 1);
    {
        Region request(&outer);                                             // 요청 하나를 처리하는 동안만 사는 리전
        for (int i = 0; i < 1000; i++) request.make("tmp" + std::to_string(i));
        assert(Region::liveObjects == 1001);
        Region::assertOutlives(outer, &request);                            // 안쪽 리전은 바깥 리전의 하위: 수명 관계 확인 가능
        bool rejected = false;
        try { Region::assertOutlives(request, &outer); } catch (const std::logic_error&) { rejected = true; }
        assert(rejected);                                                    // 바깥 -> 안쪽 참조는 안쪽이 먼저 죽으므로 거부
    }                                                                        // 리전 종료: 객체 1000개가 한꺼번에 해제 (개별 delete 없음)
    assert(Region::liveObjects == 1);
    std::cout << "RegionBasedMemory: 1000 temporary objects freed with one region exit." << std::endl;
    return 0;
}
// Time Complexity: 리전 해제 O(1) (구현의 편의상 O(객체 수))
// Space Complexity: O(객체 수)
```
## EscapeAnalysis()
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// 탈출 분석(escape analysis): 객체가 만들어진 함수 밖으로 "빠져나가는가" 를 컴파일 시점에 분석한다.  빠져나가지 않으면 힙 대신 스택에 두거나(스택 할당),
// 필드를 지역 변수로 쪼개 객체 자체를 없앨 수 있다(스칼라 치환) -> GC 부담 제거.  JVM(HotSpot), Go, V8 이 사용
// 단순화한 중간 표현에서 분석을 직접 구현한다.  탈출 조건: (1) 반환됨 (2) 전역/미지의 함수에 전달됨 (3) 이미 탈출하는 객체의 필드에 저장됨
enum Op { NEW, MOVE, STORE, RETURN, PASS };
struct Stmt { Op op; std::string a, b; };     // NEW a: a = new / MOVE a, b: a = b / STORE a, b: a.f = b / RETURN a / PASS a: 미지의 함수에 인자로 전달

std::set<std::string> escaped(const std::vector<Stmt>& prog) {
    std::set<std::string> esc;
    for (auto& s : prog) if (s.op == RETURN || s.op == PASS) esc.insert(s.a);
    for (bool changed = true; changed;) {                                    // 고정점 반복: 탈출이 별칭·필드를 통해 전파된다
        changed = false;
        for (auto& s : prog) {
            if (s.op == MOVE && esc.count(s.a) && esc.insert(s.b).second) changed = true;      // a = b 에서 a 가 탈출하면 b 도 탈출
            if (s.op == MOVE && esc.count(s.b) && esc.insert(s.a).second) changed = true;      // 별칭이므로 양방향
            if (s.op == STORE && esc.count(s.a) && esc.insert(s.b).second) changed = true;      // 탈출하는 객체의 필드에 저장된 값도 탈출
        }
    }
    return esc;
}

int main() {
    using V = std::vector<Stmt>;
    // 1) p 는 함수 안에서만 쓰인다 -> 탈출 없음 -> 스택/스칼라 치환 가능
    assert(escaped(V{{NEW, "p", ""}, {STORE, "p", "p"}}).empty());
    // 2) 반환되는 객체는 탈출
    assert((escaped(V{{NEW, "p", ""}, {RETURN, "p", ""}}) == std::set<std::string>{"p"}));
    // 3) q 를 탈출하는 p 의 필드에 저장 -> q 도 탈출
    assert((escaped(V{{NEW, "q", ""}, {NEW, "p", ""}, {STORE, "p", "q"}, {RETURN, "p", ""}}) == std::set<std::string>{"p", "q"}));
    // 4) 둘 다 지역에서만 연결되면 탈출 없음
    assert(escaped(V{{NEW, "q", ""}, {NEW, "p", ""}, {STORE, "p", "q"}}).empty());
    // 5) 별칭을 통한 탈출: r = p; return r;
    assert((escaped(V{{NEW, "p", ""}, {MOVE, "r", "p"}, {RETURN, "r", ""}}) == std::set<std::string>{"p", "r"}));
    // 6) 미지의 함수에 전달하면 탈출
    assert((escaped(V{{NEW, "p", ""}, {PASS, "p", ""}}) == std::set<std::string>{"p"}));
    std::cout << "EscapeAnalysis: classified 6 programs; non-escaping objects can live on the stack." << std::endl;
    return 0;
}
// Time Complexity: O(문장 수 · 반복)
// Space Complexity: O(변수 수)
```
## OwnershipTypeSystem()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <cassert>

// 소유권 타입 시스템(Rust): (1) 값의 소유자는 하나  (2) 소유권이 이동(move)하면 원래 변수는 사용 불가  (3) 빌림(borrow) 규칙: 읽기 참조는 여러 개 OR 쓰기 참조는 정확히 한 개 (동시에는 불가)
// -> 데이터 경쟁과 댕글링 참조를 컴파일 시점에 막는다.  Rust 는 컴파일러가 하지만, 여기서는 같은 규칙을 런타임 검사로 흉내 내 규칙의 의미를 확인한다 (RefCell 과 비슷)
template <class T> class Owned {
    std::unique_ptr<T> v; int shared = 0; bool mut = false;
public:
    explicit Owned(T x) : v(new T(std::move(x))) {}
    Owned(Owned&& o) noexcept : v(std::move(o.v)) {}                       // 이동: 원본은 비워진다
    bool moved() const { return !v; }
    struct Ref { Owned& o; bool isMut; Ref(Owned& x, bool m) : o(x), isMut(m) {} ~Ref() { if (isMut) o.mut = false; else o.shared--; } const T& get() const { return *o.v; } T& getMut() { return *o.v; } };
    Ref borrow() { if (!v) throw std::logic_error("use after move"); if (mut) throw std::logic_error("cannot borrow as immutable: mutably borrowed"); shared++; return Ref(*this, false); }
    Ref borrowMut() { if (!v) throw std::logic_error("use after move"); if (mut || shared) throw std::logic_error("cannot borrow as mutable: already borrowed"); mut = true; return Ref(*this, true); }
};
template <class F> bool throws(F f) { try { f(); } catch (const std::logic_error&) { return true; } return false; }

int main() {
    Owned<std::string> a(std::string("data"));
    { auto r1 = a.borrow(); auto r2 = a.borrow(); assert(r1.get() == "data" && r2.get() == "data"); }     // 읽기 참조는 여러 개 가능
    { auto w = a.borrowMut(); w.getMut() += "!"; }                                                            // 쓰기 참조는 하나
    assert(a.borrow().get() == "data!");
    { auto r = a.borrow(); assert(throws([&] { a.borrowMut(); })); }                                         // 읽는 중에 쓰기 참조 -> 위반
    { auto w = a.borrowMut(); assert(throws([&] { a.borrow(); })); assert(throws([&] { a.borrowMut(); })); } // 쓰는 중에는 어떤 참조도 불가
    assert(!throws([&] { a.borrowMut(); }));                                                                  // 참조가 끝나면 다시 가능
    Owned<std::string> b = std::move(a);                                                                      // 소유권 이동
    assert(a.moved() && !b.moved() && throws([&] { a.borrow(); }));                                           // 이동 후 원본 사용은 오류
    std::cout << "OwnershipTypeSystem: aliasing XOR mutation enforced; use after move rejected." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
// Space Complexity: O(1)
```
## PersistentHeap()
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <cassert>

// 영속 자료구조(persistent): 수정해도 이전 버전이 그대로 남는다.  비결은 "구조 공유(structural sharing)" — 바뀌는 경로(루트 -> 변경 지점)의 노드만 복사하고 나머지는 이전 버전과 공유한다.
// 이진 탐색 트리에 삽입하면 새 노드는 O(log n) 개뿐이다.  불변성 덕분에 락 없이 여러 스레드가 안전하게 읽고, 스냅샷·되돌리기(undo)가 공짜다 (Clojure, Git 의 객체 저장소, 영속 메모리 힙)
struct Node; typedef std::shared_ptr<const Node> P;
struct Node { int key; P l, r; static long created; Node(int k, P a, P b) : key(k), l(a), r(b) { created++; } };
long Node::created = 0;

P insert(const P& t, int k) {
    if (!t) return std::make_shared<const Node>(k, nullptr, nullptr);
    if (k < t->key) return std::make_shared<const Node>(t->key, insert(t->l, k), t->r);       // 경로의 노드만 새로 만들고 반대쪽 서브트리는 공유
    if (k > t->key) return std::make_shared<const Node>(t->key, t->l, insert(t->r, k));
    return t;
}
bool contains(const P& t, int k) { while (t) { if (k == t->key) return true; return contains(k < t->key ? t->l : t->r, k); } return false; }
int height(const P& t) { return t ? 1 + std::max(height(t->l), height(t->r)) : 0; }

int main() {
    std::vector<P> versions = {nullptr};
    int order[] = {50, 30, 70, 20, 40, 60, 80, 35, 45, 65};
    for (int k : order) versions.push_back(insert(versions.back(), k));
    long createdBefore = Node::created;
    P v11 = insert(versions.back(), 42);                                       // 새 버전: 키 42 추가
    long newNodes = Node::created - createdBefore;
    assert(newNodes <= height(v11));                                           // 새 노드는 변경 경로의 길이만큼만 (나머지는 공유)
    assert(contains(v11, 42) && !contains(versions.back(), 42));               // 이전 버전은 변하지 않았다
    for (size_t i = 0; i < versions.size(); i++) {                             // 모든 과거 버전이 그대로 조회된다
        int present = 0; for (int k : order) present += contains(versions[i], k);
        assert(present == (int)i);                                             // 버전 i 에는 정확히 i 개의 키가 있다
    }
    assert(v11->r == versions.back()->r);                                      // 변경되지 않은 오른쪽 서브트리는 같은 객체를 공유
    std::cout << "PersistentHeap: inserting into a 10-key tree allocated only " << newNodes << " new nodes; all 11 versions remain readable." << std::endl;
    return 0;
}
// Time Complexity: 삽입 O(log N) 시간·공간
// Space Complexity: 버전마다 O(log N) 추가
```
## TransactionalMemory()
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <unordered_map>
#include <vector>
#include <cassert>

// 소프트웨어 트랜잭셔널 메모리(STM, TL2 방식): 락 대신 트랜잭션으로 공유 변수를 다룬다.  읽기는 낙관적으로(락 없이) 하고 쓰기는 버퍼에 모았다가,
// 커밋할 때 "내가 읽은 변수들이 시작 이후 바뀌지 않았는가"(버전 검증)를 확인한다.  충돌했으면 버리고 처음부터 재시도 — 교착 상태가 없고 조합이 쉽다
struct TVar { int value = 0; std::atomic<long> version{0}; };
std::atomic<long> globalClock(0); std::mutex commitLock;

struct Tx {
    long start = globalClock.load();
    std::unordered_map<TVar*, long> readSet;                         // 읽은 변수 -> 읽은 시점의 버전
    std::unordered_map<TVar*, int> writeBuf;
    int read(TVar& v) {
        auto w = writeBuf.find(&v); if (w != writeBuf.end()) return w->second;     // 자기 쓰기 우선
        long ver = v.version.load(); int val = v.value;
        if (v.version.load() != ver || ver > start) throw std::runtime_error("conflict");   // 읽는 도중이거나 시작 후에 바뀐 값
        readSet[&v] = ver; return val;
    }
    void write(TVar& v, int x) { writeBuf[&v] = x; }
    void commit() {
        std::lock_guard<std::mutex> g(commitLock);
        for (auto& r : readSet) if (r.first->version.load() != r.second) throw std::runtime_error("conflict");   // 읽기 집합 검증
        long wv = globalClock.fetch_add(1) + 1;
        for (auto& w : writeBuf) { w.first->value = w.second; w.first->version.store(wv); }                    // 쓰기 반영
    }
};
template <class F> void atomically(F f) { for (;;) { Tx tx; try { f(tx); tx.commit(); return; } catch (const std::runtime_error&) {} } }

int main() {
    // 결정적 충돌: tx1 이 x 를 읽은 뒤 tx2 가 x 를 바꿔 커밋하면 tx1 의 커밋은 실패해야 한다
    TVar x; x.value = 5;
    Tx tx1; int seen = tx1.read(x);
    atomically([&](Tx& t) { t.write(x, t.read(x) + 1); });
    tx1.write(x, seen + 100);
    bool conflicted = false; try { tx1.commit(); } catch (const std::runtime_error&) { conflicted = true; }
    assert(conflicted && x.value == 6);                              // tx1 의 쓰기는 반영되지 않았다 (낡은 읽기에 기반한 갱신 차단)

    // 여러 스레드가 두 계좌 사이에서 동시에 이체: 락 없이도 합계가 보존된다
    TVar a, b; a.value = 1000; b.value = 1000;
    std::vector<std::thread> th;
    for (int t = 0; t < 4; t++) th.emplace_back([&, t] { for (int i = 0; i < 2000; i++) atomically([&](Tx& tx) { int amount = 1 + (i + t) % 5; tx.write(a, tx.read(a) - amount); tx.write(b, tx.read(b) + amount); }); });
    for (auto& s : th) s.join();
    assert(a.value + b.value == 2000);                               // 불변식 유지
    assert(a.value != 1000);                                         // 이체가 실제로 일어났다
    std::cout << "TransactionalMemory: stale transaction aborted; 8000 concurrent transfers kept the total at " << a.value + b.value << std::endl;
    return 0;
}
// Time Complexity: 트랜잭션당 O(읽기 + 쓰기 집합), 충돌 시 재시도
// Space Complexity: O(읽기·쓰기 집합)
```
## CapabilityPointer()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <stdexcept>
#include <vector>
#include <cassert>

// 케이퍼빌리티 포인터(CHERI): 포인터를 "주소" 만이 아니라 (기준 주소 base, 길이 length, 권한 perms) 를 함께 담은 불변 토큰으로 만든다.
// 접근할 때 하드웨어가 범위와 권한을 검사한다.  케이퍼빌리티는 "축소만" 가능하다(단조성): 더 좁은 범위·더 적은 권한은 만들 수 있지만 넓히거나 권한을 추가할 수는 없다 -> 최소 권한 원칙을 하드웨어가 강제
enum Perm : unsigned { LOAD = 1, STORE = 2 };
struct Cap {
    uint64_t base, length, addr; unsigned perms;
    Cap derive(uint64_t newBase, uint64_t newLen, unsigned newPerms) const {
        if (newBase < base || newBase + newLen > base + length) throw std::runtime_error("monotonicity: range would widen");
        if (newPerms & ~perms) throw std::runtime_error("monotonicity: permissions would increase");
        return {newBase, newLen, newBase, newPerms};
    }
};
class Memory {
    std::vector<uint8_t> bytes;
public:
    explicit Memory(size_t n) : bytes(n, 0) {}
    uint8_t load(const Cap& c, uint64_t off) const { check(c, off, LOAD); return bytes[c.base + off]; }
    void store(const Cap& c, uint64_t off, uint8_t v) { check(c, off, STORE); bytes[c.base + off] = v; }
private:
    static void check(const Cap& c, uint64_t off, unsigned need) {
        if (off >= c.length) throw std::runtime_error("bounds violation");
        if (!(c.perms & need)) throw std::runtime_error("permission violation");
    }
};
template <class F> bool traps(F f) { try { f(); } catch (const std::runtime_error&) { return true; } return false; }

int main() {
    Memory mem(1024);
    Cap whole{0, 1024, 0, LOAD | STORE};
    Cap buf = whole.derive(100, 16, LOAD | STORE);                    // 16바이트 버퍼에 대한 케이퍼빌리티
    mem.store(buf, 15, 7); assert(mem.load(buf, 15) == 7);             // 범위 안: 정상
    assert(traps([&] { mem.store(buf, 16, 1); }));                     // 버퍼 오버플로: 1바이트만 넘어도 하드웨어가 거부
    Cap readOnly = buf.derive(100, 8, LOAD);                           // 더 좁고 더 약한 케이퍼빌리티는 만들 수 있다
    assert(mem.load(readOnly, 0) == 0 && traps([&] { mem.store(readOnly, 0, 1); }));   // 읽기 전용: 쓰기 거부
    assert(traps([&] { readOnly.derive(100, 8, LOAD | STORE); }));     // 권한을 되살릴 수 없다
    assert(traps([&] { buf.derive(100, 32, LOAD); }));                 // 범위를 넓힐 수 없다
    assert(traps([&] { buf.derive(90, 8, LOAD); }));                   // 범위 밖으로 이동할 수 없다
    std::cout << "CapabilityPointer: bounds and permissions enforced; derivation can only shrink." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
// Space Complexity: 포인터당 base·length·perms 추가 (CHERI 는 128비트 포인터)
```
## CHERIArchitecture()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <cassert>

// CHERI 의 핵심 아이디어 두 가지: (1) 케이퍼빌리티는 16바이트로 정렬된 메모리에 저장되고, 메모리 16바이트마다 숨은 "태그 비트" 가 붙는다.
// (2) 케이퍼빌리티를 저장하면 태그가 1 이 되지만, 같은 16바이트에 일반 데이터를 쓰면 태그가 자동으로 0 이 된다 -> 바이트를 조작해 케이퍼빌리티를 위조할 수 없다.
// 태그가 꺼진 케이퍼빌리티는 사용하려 하면 예외.  이 두 가지로 "포인터 위조 불가" 가 하드웨어 수준에서 성립한다
const size_t GRANULE = 16;
struct Cap { uint64_t base, length; bool tag; };
class TaggedMemory {
    std::vector<uint8_t> bytes; std::vector<bool> tags; std::vector<Cap> capStore;       // 케이퍼빌리티 값은 별도 저장 (16B 칸마다 하나)
public:
    explicit TaggedMemory(size_t n) : bytes(n, 0), tags(n / GRANULE, false), capStore(n / GRANULE) {}
    void storeCap(size_t addr, const Cap& c) { assert(addr % GRANULE == 0); capStore[addr / GRANULE] = c; tags[addr / GRANULE] = true; }
    Cap loadCap(size_t addr) const { Cap c = capStore[addr / GRANULE]; c.tag = tags[addr / GRANULE]; return c; }
    void storeByte(size_t addr, uint8_t v) { bytes[addr] = v; tags[addr / GRANULE] = false; }      // 일반 저장은 해당 칸의 태그를 지운다
    bool tagAt(size_t addr) const { return tags[addr / GRANULE]; }
};
uint8_t use(const Cap& c) { if (!c.tag) throw std::runtime_error("tag violation: invalid capability"); return 1; }

int main() {
    TaggedMemory mem(256);
    mem.storeCap(32, Cap{100, 16, true});                           // 정상적인 케이퍼빌리티 저장
    assert(mem.tagAt(32) && use(mem.loadCap(32)) == 1);             // 태그가 켜져 있어 사용 가능
    mem.storeByte(40, 0xFF);                                        // 공격자가 같은 16바이트 칸의 일부 바이트를 덮어써 케이퍼빌리티를 변조하려 한다
    assert(!mem.tagAt(32));                                         // 태그가 자동으로 꺼졌다
    bool trapped = false; try { use(mem.loadCap(32)); } catch (const std::runtime_error&) { trapped = true; }
    assert(trapped);                                                // 변조된 케이퍼빌리티는 쓸 수 없다
    // 위조 시도: 일반 데이터로 "그럴듯한 케이퍼빌리티 비트 패턴" 을 써도 태그가 없으므로 무효
    for (size_t i = 64; i < 80; i++) mem.storeByte(i, 0x41);
    assert(!mem.tagAt(64) && !mem.loadCap(64).tag);
    std::cout << "CHERIArchitecture: writing data over a capability cleared its tag; forged capabilities are unusable." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 16바이트당 태그 1비트 (약 0.8%)
```
## MemoryTagging()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <stdexcept>
#include <vector>
#include <cassert>

// 메모리 태깅(ARM MTE): 메모리를 16바이트 단위(granule)로 나눠 각각에 4비트 "태그" 를 붙이고, 포인터의 상위 비트에도 같은 4비트 태그를 넣는다.
// 접근할 때 하드웨어가 포인터 태그 == 메모리 태그 인지 검사한다.  할당할 때 임의 태그를 붙이고, 해제하면 다른 태그로 바꾸면 해제 후 사용(UAF)이 대부분(15/16) 잡히고,
// 이웃한 할당끼리 태그를 달리하면 오버플로도 잡힌다.  CHERI 와 달리 포인터 크기가 그대로이고 확률적 보호
struct TaggedPtr { uint64_t addr; unsigned tag; };
class TaggedHeap {
    std::vector<uint8_t> mem, tags; uint64_t top = 0; unsigned nextTag = 1;
public:
    explicit TaggedHeap(size_t n) : mem(n, 0), tags(n / 16, 0) {}
    TaggedPtr alloc(size_t n) {
        size_t g = (n + 15) / 16; unsigned t = nextTag; nextTag = nextTag % 15 + 1;          // 이웃에 다른 태그가 가도록 순환
        TaggedPtr p{top, t}; for (size_t i = 0; i < g; i++) tags[top / 16 + i] = t; top += g * 16; return p;
    }
    void release(TaggedPtr p, size_t n) { unsigned nt = p.tag % 15 + 1; for (size_t i = 0; i < (n + 15) / 16; i++) tags[p.addr / 16 + i] = nt; }   // 해제: 메모리 태그를 다른 값으로 바꿔 둔다 (옛 포인터의 태그와 달라진다)
    uint8_t read(TaggedPtr p, size_t off) const { if (tags[(p.addr + off) / 16] != p.tag) throw std::runtime_error("tag mismatch"); return mem[p.addr + off]; }
    void write(TaggedPtr p, size_t off, uint8_t v) { if (tags[(p.addr + off) / 16] != p.tag) throw std::runtime_error("tag mismatch"); mem[p.addr + off] = v; }
};
template <class F> bool traps(F f) { try { f(); } catch (const std::runtime_error&) { return true; } return false; }

int main() {
    TaggedHeap h(1024);
    TaggedPtr a = h.alloc(32), b = h.alloc(32);                          // 서로 다른 태그를 가진 이웃 할당
    assert(a.tag != b.tag);
    h.write(a, 31, 9); assert(h.read(a, 31) == 9);                        // 범위 안: 정상
    assert(traps([&] { h.write(a, 32, 1); }));                            // 오버플로: a 의 끝을 넘어 b 의 영역(다른 태그)에 쓰기 -> 탐지
    h.release(a, 32);
    assert(traps([&] { h.read(a, 0); }));                                 // 해제 후 사용: 메모리 태그가 바뀌어 탐지
    TaggedPtr c = h.alloc(32);                                            // 같은 번호의 새 할당 (다른 태그)
    assert(traps([&] { h.read(a, 0); }) || c.tag != a.tag);               // 재할당 후에도 옛 포인터는 (태그가 다르면) 거부
    std::cout << "MemoryTagging: overflow into a neighbour and use-after-free both caught by tag mismatch." << std::endl;
    return 0;
}
// Time Complexity: O(1) 검사
// Space Complexity: 16바이트당 4비트 (3%)
```
## HardwareMemorySafety()
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <map>
#include <string>
#include <vector>
#include <cassert>

// 하드웨어/런타임 메모리 안전 기법을 같은 버그 4가지에 적용해 무엇을 잡는지 비교한다.  하나의 기법이 모든 버그를 잡지는 못한다.
//  버그 A: 바로 옆으로 넘치는 오버플로          버그 B: 멀리(다른 객체 한가운데로) 건너뛰는 오버플로
//  버그 C: 해제 직후 사용                        버그 D: 해제 후 같은 메모리가 새 객체에 재할당된 뒤의 사용
// 기법: 레드존+격리(ASan 식), 태그(MTE 식), 케이퍼빌리티(CHERI, 해제 회수 없음)
struct Obj { int start, size; unsigned tag; bool live; };
struct World {
    std::vector<Obj> objs;      // 할당 목록 (주소순). 객체 사이에는 16바이트 레드존
    World() {                   // 객체 0: [16,48)  객체 1: [64,96)  객체 2: [112,144)
        objs.push_back({16, 32, 1, true}); objs.push_back({64, 32, 2, true}); objs.push_back({112, 32, 3, true});
    }
    int ownerOf(int addr) const { for (size_t i = 0; i < objs.size(); i++) if (objs[i].live && addr >= objs[i].start && addr < objs[i].start + objs[i].size) return i; return -1; }
    bool inRedzone(int addr) const { return ownerOf(addr) < 0; }
};

// 접근 (포인터는 객체 id 의 것, addr 에 접근) 에 대해 각 기법이 탐지하는지
bool redzoneDetects(const World& w, int ptrObj, int addr, bool freedQuarantined) {
    if (freedQuarantined) return true;                        // 격리 중인 해제 메모리는 독 처리되어 접근 시 탐지
    return w.inRedzone(addr) && addr >= 0;                    // 유효 객체 밖(레드존)에 닿으면 탐지. 다른 객체 한가운데면 탐지 못 함
}
bool tagDetects(const World& w, const Obj& ptrObjSnapshot, int addr, unsigned memTagAtAddr) { (void)w; (void)addr; return memTagAtAddr != ptrObjSnapshot.tag; }
bool capDetects(const Obj& cap, int addr, bool revoked) { if (revoked) return true; return addr < cap.start || addr >= cap.start + cap.size; }

int main() {
    World w;
    const Obj o0 = w.objs[0];                                  // 객체 0 의 포인터를 들고 있다
    // 버그 A: 객체 0 의 끝(48)에 쓰기 -> 레드존
    assert(redzoneDetects(w, 0, 48, false) && tagDetects(w, o0, 48, 0) && capDetects(o0, 48, false));
    // 버그 B: 객체 0 의 포인터로 객체 1 한가운데(80)에 쓰기
    assert(!redzoneDetects(w, 0, 80, false));                 // 레드존은 놓친다 (다른 객체의 유효한 메모리)
    assert(tagDetects(w, o0, 80, w.objs[1].tag) && capDetects(o0, 80, false));    // 태그·케이퍼빌리티는 잡는다
    // 버그 C: 객체 0 을 해제하고 곧바로 옛 포인터로 읽기 (재할당 전)
    w.objs[0].live = false;
    assert(redzoneDetects(w, 0, 20, true) && tagDetects(w, o0, 20, 9));             // 격리 + 해제 시 태그 변경으로 탐지
    assert(!capDetects(o0, 20, false));                       // 회수(revocation) 없는 케이퍼빌리티는 범위가 여전히 유효해 놓친다
    // 버그 D: 같은 주소에 새 객체(태그 4)가 할당된 뒤 옛 포인터로 접근
    w.objs[0] = {16, 32, 4, true};
    assert(!redzoneDetects(w, 0, 20, false));                 // 새 객체의 유효한 메모리라 놓친다
    assert(tagDetects(w, o0, 20, 4));                         // 태그가 달라(1 != 4) 잡는다
    assert(!capDetects(o0, 20, false) && capDetects(o0, 20, true));      // 회수를 하면 잡는다 (CHERI 의 revocation sweep)
    // 요약 행렬 (O = 탐지, X = 놓침)
    std::map<std::string, std::string> matrix = {{"redzone+quarantine", "OXOX"}, {"memory tagging", "OOOO"}, {"capability (no revocation)", "OOXX"}, {"capability + revocation", "OOOO"}};
    for (auto& kv : matrix) std::cout << kv.first << ": A..D = " << kv.second << "\n";
    assert(matrix["memory tagging"] == "OOOO" && matrix["redzone+quarantine"] == "OXOX");
    return 0;
}
// Time Complexity: O(1) 판정
// Space Complexity: O(1)
```
# 부록
## Stack vs Heap
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <new>
#include <cassert>

// 스택: 함수 호출과 함께 자동으로 생기고 사라지는 LIFO 영역 (할당 = SP 이동).  힙: 프로그래머가 수명을 정하는 영역 (할당기가 빈 블록을 찾아야 하므로 느리고 단편화가 생긴다).
// 스택 변수는 할당기를 부르지 않는다는 것을 operator new 호출 횟수로 확인한다
static long newCalls = 0;
void* operator new(size_t n) { newCalls++; void* p = std::malloc(n); if (!p) throw std::bad_alloc(); return p; }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, size_t) noexcept { std::free(p); }
struct Point { int x, y; };

int main() {
    long before = newCalls;
    for (int i = 0; i < 1000; i++) { volatile Point p{i, i}; (void)p.x; }      // 스택에 만들고 매 반복 자동 소멸
    assert(newCalls == before);                                                // 할당기 호출 0번
    for (int i = 0; i < 1000; i++) { Point* p = new Point{i, i}; delete p; }
    assert(newCalls == before + 1000);                                         // 힙은 호출마다 할당기를 거친다
    int onStack = 0; Point* onHeap = new Point{1, 2};
    assert((uintptr_t)&onStack > (uintptr_t)onHeap || true);                   // 일반적으로 스택은 높은 주소 (플랫폼 의존)
    Point* escaped = new Point{3, 4};                                           // 힙 객체는 함수가 끝나도 살아남을 수 있다 (수명은 우리가 결정)
    assert(escaped->y == 4);
    delete onHeap; delete escaped;
    std::cout << "Stack vs Heap: 1000 stack objects used 0 allocator calls; 1000 heap objects used 1000." << std::endl;
    return 0;
}
// Time Complexity: 스택 O(1), 힙 할당기에 따라 다름
// Space Complexity: 스택 제한적(MB), 힙 큼
```
## Pointer vs Reference
### 대표코드
```cpp
#include <iostream>
#include <cassert>

// 포인터: 주소를 담는 변수 — null 가능, 다른 대상으로 재지정 가능, 산술 연산 가능, 별도 크기(8B).   참조: 기존 객체의 별칭 — 반드시 초기화, 재바인딩 불가, null 불가, 항상 유효한 객체를 가리켜야 한다.
// 참조는 보통 컴파일러가 포인터로 구현하지만 언어 규칙이 안전한 사용법을 강제한다
int main() {
    int a = 1, b = 2;
    int* p = &a; int& r = a;
    assert(*p == r && &r == p);                      // 둘 다 a 를 가리킨다
    p = &b;                                           // 포인터는 다른 대상으로 옮길 수 있다
    r = b;                                            // 참조에 대입은 재바인딩이 아니라 a 의 값을 바꾼다
    assert(*p == 2 && a == 2 && &r == &a);
    p = nullptr;                                      // 포인터는 "없음" 을 표현할 수 있다 (참조는 불가)
    assert(p == nullptr);
    int arr[3] = {10, 20, 30}; int* q = arr; q += 2;  // 포인터 산술
    assert(*q == 30);
    assert(sizeof(r) == sizeof(int) && sizeof(p) == sizeof(void*));    // sizeof(참조) 는 대상의 크기, sizeof(포인터) 는 주소 크기
    std::cout << "Pointer vs Reference verified." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 포인터 8B, 참조는 구현 의존
```
## malloc vs new
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <new>
#include <cassert>

// malloc: C 함수, 크기(바이트)를 받아 void* 반환, 초기화 없음(생성자 호출 X), 실패 시 NULL.   new: C++ 연산자, 타입을 받아 해당 타입 포인터 반환, 생성자 호출, 실패 시 bad_alloc 예외.
// new 로 만든 것은 delete, malloc 으로 만든 것은 free 로 해제해야 한다 (섞어 쓰면 정의되지 않은 동작)
struct Widget { static int ctors, dtors; int v = 7; Widget() { ctors++; } ~Widget() { dtors++; } };
int Widget::ctors = 0, Widget::dtors = 0;

int main() {
    Widget* viaMalloc = (Widget*)std::malloc(sizeof(Widget));        // 메모리만 확보, 객체는 아직 없다
    assert(Widget::ctors == 0);                                       // 생성자 호출 없음 (v 는 쓰레기 값)
    Widget* viaNew = new Widget;
    assert(Widget::ctors == 1 && viaNew->v == 7);                     // 생성자가 호출되고 멤버가 초기화됨
    new (viaMalloc) Widget;                                           // malloc 메모리에 객체를 만들려면 배치 new 가 필요
    assert(Widget::ctors == 2 && viaMalloc->v == 7);
    viaMalloc->~Widget(); std::free(viaMalloc);                       // malloc 짝은 소멸자 직접 호출 + free
    delete viaNew;                                                    // new 짝은 delete
    assert(Widget::dtors == 2);
    int* arr = (int*)std::malloc(10 * sizeof(int));                   // 크기를 직접 계산해야 한다 (new int[10] 은 타입이 계산)
    assert(arr); std::free(arr);
    std::cout << "malloc vs new: constructors run only with new (or placement new)." << std::endl;
    return 0;
}
// Time Complexity: 할당기에 따라 다름
// Space Complexity: O(n)
```
## free vs delete
### 대표코드
```cpp
#include <iostream>
#include <cstdlib>
#include <new>
#include <cassert>

// free: 메모리만 반환한다 — 소멸자를 부르지 않는다.   delete: 소멸자를 먼저 호출(자원 해제)한 뒤 메모리를 반환한다.
// 소멸자가 파일을 닫거나 락을 푸는 객체에 free 를 쓰면 그 자원이 새어 나간다.   delete[] 는 배열의 모든 원소에 소멸자를 호출한다
struct Resource { static int open; Resource() { open++; } ~Resource() { open--; } };
int Resource::open = 0;

int main() {
    Resource* a = new Resource; assert(Resource::open == 1);
    delete a; assert(Resource::open == 0);                             // delete: 소멸자 호출 -> 자원 닫힘

    void* raw = std::malloc(sizeof(Resource));
    Resource* b = new (raw) Resource; assert(Resource::open == 1);
    std::free(b);                                                      // free 만 호출: 메모리는 돌려주지만 소멸자는 호출되지 않는다
    assert(Resource::open == 1);                                       // 자원이 닫히지 않은 채 남았다 (누수)
    Resource::open = 0;

    Resource* arr = new Resource[3]; assert(Resource::open == 3);
    delete[] arr; assert(Resource::open == 0);                         // 배열은 delete[] 로: 소멸자 3번
    std::cout << "free vs delete: free skipped the destructor; delete[] destroyed all elements." << std::endl;
    return 0;
}
// Time Complexity: delete 는 소멸자 비용 포함
// Space Complexity: O(1)
```
## Shared Pointer의 순환 참조
### 대표코드
```cpp
#include <iostream>
#include <memory>
#include <cassert>

// shared_ptr 은 참조 카운트가 0 이 되어야 해제한다.  두 객체가 서로를 shared_ptr 로 가리키면 카운트가 영원히 1 이상이라 둘 다 해제되지 않는다(누수).
// 해법: 한쪽(보통 자식 -> 부모, 관찰자 방향)을 weak_ptr 로 바꿔 카운트에 포함시키지 않는다
int destroyed = 0;
struct Node { std::shared_ptr<Node> next; ~Node() { destroyed++; } };
struct Parent; struct Child;
struct Parent { std::shared_ptr<Child> child; ~Parent() { destroyed++; } };
struct Child { std::weak_ptr<Parent> parent; ~Child() { destroyed++; } };     // 역방향은 weak

int main() {
    {
        auto a = std::make_shared<Node>(), b = std::make_shared<Node>();
        a->next = b; b->next = a;                                            // 순환
        assert(a.use_count() == 2 && b.use_count() == 2);
    }                                                                        // 지역 변수가 사라져도 서로가 붙들고 있어 해제되지 않는다
    assert(destroyed == 0);                                                  // 누수!

    {
        auto p = std::make_shared<Parent>(); auto c = std::make_shared<Child>();
        p->child = c; c->parent = p;                                         // 부모 -> 자식은 shared, 자식 -> 부모는 weak
        assert(p.use_count() == 1 && c.use_count() == 2);                    // 부모의 카운트가 올라가지 않았다
        assert(c->parent.lock() == p);                                       // 필요하면 lock() 으로 잠시 소유권을 얻는다
    }
    assert(destroyed == 2);                                                  // 정상적으로 둘 다 해제
    std::cout << "Cycle of shared_ptr leaked (destroyed=0); weak_ptr back-reference freed both." << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: 누수 시 영구 점유
```
## 왜 캐시 미스가 성능을 떨어뜨리는가?
### 대표코드
```cpp
#include <iostream>
#include <cmath>
#include <cassert>

// 평균 메모리 접근 시간 AMAT = 적중 시간 + 미스율 × 미스 비용.  L1 적중은 약 4사이클이지만 DRAM 접근은 약 200사이클로 50배 느리다.
// 그래서 미스율이 작아 보여도 평균이 크게 나빠진다: 미스율 5% 만 돼도 AMAT 이 3.5 배가 된다.  캐시 지역성이 곧 성능이다
double amat(double hit, double missRate, double penalty) { return hit + missRate * penalty; }
double amat3(double l1, double l2, double l3, double mem, double m1, double m2, double m3) {      // 3단계 + DRAM
    return l1 + m1 * (l2 + m2 * (l3 + m3 * mem));
}

int main() {
    const double L1 = 4, DRAM = 200;
    assert(amat(L1, 0.00, DRAM) == 4);                                   // 모두 적중
    assert(amat(L1, 0.01, DRAM) == 6);                                   // 1% 미스: 평균 50% 증가
    assert(std::fabs(amat(L1, 0.05, DRAM) - 14) < 1e-9);                 // 5% 미스: 3.5 배
    assert(amat(L1, 0.20, DRAM) / amat(L1, 0.0, DRAM) == 11);            // 20% 미스: 11 배
    // 다단계 캐시는 미스 비용을 단계별로 완화한다: L1 미스 10%, 그중 L2 미스 20%, 그중 L3 미스 30%
    double hierarchical = amat3(4, 12, 40, 200, 0.10, 0.20, 0.30);
    double flat = amat(4, 0.10 * 0.20 * 0.30, 200) ;                      // 참고: 중간 단계를 무시한 값
    assert(hierarchical < amat(4, 0.10, 200));                            // 같은 L1 미스율이라도 L2/L3 가 있으면 훨씬 낫다
    std::cout << "AMAT: 0% miss=4, 1%=6, 5%=14 cycles; 3-level hierarchy (10%/20%/30% misses) = " << hierarchical << " cycles (flat estimate " << flat << ")" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 페이지 교체 알고리즘(LRU, Clock)
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <list>
#include <vector>
#include <cassert>

// 프레임이 가득 찼을 때 어느 페이지를 내보낼까?  OPT(앞으로 가장 늦게 쓸 페이지, 미래를 알아야 하므로 이론적 하한)  /  LRU(가장 오래 안 쓴 페이지, 정확하지만 매 접근마다 갱신이 필요해 비싸다)
// Clock(Second Chance): LRU 를 싸게 근사한다 — 프레임을 원형으로 놓고 참조 비트를 보며 시계바늘이 돈다.  비트가 1 이면 0 으로 내리고 한 번 더 기회를 주고, 0 이면 쫓아낸다.  FIFO 는 구현이 가장 단순하지만 성능이 나쁘다
int fifo(const std::vector<int>& r, int F) { std::list<int> q; int f = 0; for (int p : r) { if (std::find(q.begin(), q.end(), p) != q.end()) continue; f++; if ((int)q.size() == F) q.pop_front(); q.push_back(p); } return f; }
int lru(const std::vector<int>& r, int F) { std::list<int> q; int f = 0; for (int p : r) { auto it = std::find(q.begin(), q.end(), p); if (it != q.end()) { q.erase(it); q.push_back(p); continue; } f++; if ((int)q.size() == F) q.pop_front(); q.push_back(p); } return f; }
int opt(const std::vector<int>& r, int F) {
    std::vector<int> mem; int f = 0;
    for (size_t i = 0; i < r.size(); i++) {
        if (std::find(mem.begin(), mem.end(), r[i]) != mem.end()) continue;
        f++; if ((int)mem.size() < F) { mem.push_back(r[i]); continue; }
        size_t victim = 0; long farthest = -1;
        for (size_t k = 0; k < mem.size(); k++) { long next = 1e9; for (size_t j = i + 1; j < r.size(); j++) if (r[j] == mem[k]) { next = j; break; } if (next > farthest) { farthest = next; victim = k; } }
        mem[victim] = r[i];
    }
    return f;
}
int clockAlg(const std::vector<int>& r, int F) {
    std::vector<int> page(F, -1); std::vector<bool> ref(F, false); int hand = 0, f = 0;
    for (int p : r) {
        auto it = std::find(page.begin(), page.end(), p);
        if (it != page.end()) { ref[it - page.begin()] = true; continue; }       // 적중: 참조 비트만 켠다 (싸다)
        f++;
        while (page[hand] != -1 && ref[hand]) { ref[hand] = false; hand = (hand + 1) % F; }   // 기회를 한 번 주고 넘어감
        page[hand] = p; ref[hand] = true; hand = (hand + 1) % F;
    }
    return f;
}

int main() {
    std::vector<int> refs = {7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1};      // 운영체제 교과서의 표준 참조열 (프레임 3개)
    assert(fifo(refs, 3) == 15 && lru(refs, 3) == 12 && opt(refs, 3) == 9);
    int c = clockAlg(refs, 3);
    assert(c >= opt(refs, 3) && c <= fifo(refs, 3));                   // Clock 은 OPT 보다 나쁘고 FIFO 보다 나쁘지 않다 (LRU 에 가깝다)
    std::cout << "page faults (3 frames): OPT=" << opt(refs, 3) << " LRU=" << lru(refs, 3) << " Clock=" << c << " FIFO=" << fifo(refs, 3) << std::endl;
    return 0;
}
// Time Complexity: LRU 접근당 O(프레임) (리스트), Clock 은 분할상환 O(1)
// Space Complexity: O(프레임 수)
```
## Virtual Memory가 필요한 이유
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <vector>
#include <cassert>

// 가상 메모리가 주는 것: (1) 격리 — 프로세스마다 독립된 주소 공간이라 서로의 메모리를 볼 수 없다  (2) 단순한 프로그래밍 모델 — 모든 프로세스가 같은 가상 주소(예: 0x1000)를 쓸 수 있다
// (3) 공유 — 읽기 전용 라이브러리 페이지를 한 프레임에 매핑해 여러 프로세스가 함께 쓴다  (4) 물리 메모리보다 큰 주소 공간(요구 페이징·스왑)  (5) 보호 — 페이지별 권한
struct Process { std::map<int, int> pageTable; };            // 가상 페이지 -> 물리 프레임
std::vector<int> physical(8, 0);                              // 물리 메모리 8프레임 (각 프레임의 내용을 정수 하나로 단순화)
int load(const Process& p, int vpage) { auto it = p.pageTable.find(vpage); if (it == p.pageTable.end()) return -1; return physical[it->second]; }

int main() {
    Process a, b;
    a.pageTable[1] = 3; b.pageTable[1] = 5;                    // 같은 가상 페이지 1 이 서로 다른 프레임으로
    physical[3] = 111; physical[5] = 222;
    assert(load(a, 1) == 111 && load(b, 1) == 222);            // 같은 주소를 읽어도 각자 자기 데이터 (격리)
    assert(load(a, 2) == -1);                                  // 매핑이 없으면 접근 불가 (b 의 프레임 5 에 닿을 방법이 없다)
    a.pageTable[7] = 0; b.pageTable[9] = 0; physical[0] = 42;  // 라이브러리 프레임 0 을 두 프로세스가 서로 다른 가상 주소로 공유
    assert(load(a, 7) == 42 && load(b, 9) == 42);
    physical[0] = 43; assert(load(a, 7) == 43 && load(b, 9) == 43);   // 한 프레임이므로 물리 메모리는 한 벌만 쓴다
    // 가상 주소 공간은 물리 메모리보다 크다: 프로세스 2개가 각각 1000 페이지를 "예약" 했지만 실제 프레임은 8개뿐 (쓸 때 배정)
    Process big1, big2; for (int v = 0; v < 1000; v++) { big1.pageTable[v] = -1; big2.pageTable[v] = -1; }
    assert(big1.pageTable.size() + big2.pageTable.size() > physical.size());
    std::cout << "Virtual memory: isolation, sharing and over-reservation demonstrated with page tables." << std::endl;
    return 0;
}
// Time Complexity: O(log 매핑 수)
// Space Complexity: O(매핑 수)
```
## 메모리 단편화(Fragmentation)
### 대표코드
```cpp
#include <iostream>
#include <vector>
#include <cassert>

// 내부 단편화: 블록 안에서 요청보다 크게 줘서 낭비 (크기 클래스 올림, 페이지 올림).   외부 단편화: 빈 공간의 합은 충분하지만 연속된 큰 조각이 없어 할당 실패.
// 해결: 외부 -> 압축(compaction, 이동), 페이징(연속일 필요 없음), 버디/슬랩;  내부 -> 크기 클래스 세분화
int sizeClass(int n) { int c = 16; while (c < n) c *= 2; return c; }       // 16, 32, 64, 128 ...

int main() {
    // 내부 단편화
    assert(sizeClass(17) == 32 && sizeClass(17) - 17 == 15);               // 17 바이트 요청에 32 바이트 -> 15 바이트 낭비
    assert(sizeClass(64) == 64);                                            // 딱 맞으면 낭비 없음
    // 외부 단편화: 6400 바이트 힙에 64 바이트 블록 100개
    const int B = 64, N = 100;
    std::vector<bool> used(N, true);
    for (int i = 0; i < N; i += 2) used[i] = false;                         // 짝수 번째 블록을 해제 -> 3200 바이트가 비었지만 모두 흩어져 있다
    auto largestFree = [&]() { int best = 0, run = 0; for (bool u : used) { run = u ? 0 : run + 1; best = std::max(best, run); } return best * B; };
    int totalFree = 0; for (bool u : used) totalFree += u ? 0 : B;
    assert(totalFree == 3200 && largestFree() == 64);                       // 합은 3200 인데 연속 최대는 64
    assert(largestFree() < 128);                                            // 128 바이트짜리 요청은 실패 (공간은 충분한데도)
    double fragmentation = 1.0 - double(largestFree()) / totalFree;          // 외부 단편화 지수
    assert(fragmentation > 0.97);
    // 압축: 사용 중인 블록을 앞쪽으로 모으면 빈 공간이 하나로 합쳐진다
    int w = 0; std::vector<bool> compacted(N, false);
    for (int i = 0; i < N; i++) if (used[i]) compacted[w++] = true;
    used = compacted;
    assert(largestFree() == 3200);                                          // 이제 3200 바이트 연속 공간
    std::cout << "Fragmentation index before compaction: " << fragmentation << ", after: 0" << std::endl;
    return 0;
}
// Time Complexity: 압축 O(N)
// Space Complexity: O(N)
```
## False Sharing이란?
### 대표코드
```cpp
#include <iostream>
#include <atomic>
#include <cstdint>
#include <thread>
#include <cassert>

// 서로 다른 코어가 서로 다른 변수를 쓰는데도, 두 변수가 같은 캐시 라인(64B)에 있으면 한 코어가 쓸 때마다 다른 코어의 라인 사본이 무효화되어 라인이 코어 사이를 오간다.
// 데이터는 공유하지 않는데 캐시 일관성 프로토콜(MESI) 때문에 성능이 떨어지므로 "거짓" 공유라 부른다.  해결: alignas(64) 패딩 (또는 std::hardware_destructive_interference_size)
struct Bad  { std::atomic<long> x, y; };                                    // 16바이트: 같은 라인
struct Good { alignas(64) std::atomic<long> x; alignas(64) std::atomic<long> y; };    // 128바이트: 라인 하나씩
bool sameLine(const void* a, const void* b) { return (uintptr_t)a / 64 == (uintptr_t)b / 64; }

int main() {
    Bad bad; Good good;
    assert(sizeof(Bad) == 16 && sizeof(Good) == 128);
    assert(sameLine(&bad.x, &bad.y) && !sameLine(&good.x, &good.y));         // 레이아웃으로 확인
    auto work = [](std::atomic<long>& v) { for (int i = 0; i < 100000; i++) v.fetch_add(1, std::memory_order_relaxed); };
    std::thread a(work, std::ref(bad.x)), b(work, std::ref(bad.y)); a.join(); b.join();
    std::thread c(work, std::ref(good.x)), d(work, std::ref(good.y)); c.join(); d.join();
    assert(bad.x == 100000 && bad.y == 100000 && good.x == 100000 && good.y == 100000);   // 결과는 같다 — 차이는 속도뿐
    std::cout << "False sharing: Bad shares one cache line (16 B), Good pads to two (128 B); results identical." << std::endl;
    return 0;
}
// Time Complexity: O(작업량)
// Space Complexity: 패딩만큼 증가
```
## NUMA 구조 이해하기
### 대표코드
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cassert>
#if defined(__linux__)
#include <dirent.h>
#endif

// NUMA 서버의 노드 간 상대 거리(numactl --hardware 의 distance 표): 자기 노드 10, 이웃 노드 21, 먼 노드 31 처럼 거리가 다르다.
// 접근 비용은 (스레드가 있는 노드, 메모리가 있는 노드) 쌍의 거리에 비례한다.  메모리를 어디에 둘지가 정책이다:
//  local(first-touch): 항상 가까운 곳   interleave: 노드에 균등 분산(평균 비용, 대신 대역폭 분산)   remote: 최악
int main() {
    std::vector<std::vector<int>> dist = {{10, 21, 21, 31}, {21, 10, 31, 21}, {21, 31, 10, 21}, {31, 21, 21, 10}};   // 4소켓 예
    int n = dist.size();
    double local = 0, interleave = 0, worst = 0;
    for (int t = 0; t < n; t++) {
        local += dist[t][t];
        double sum = 0; int mx = 0; for (int m = 0; m < n; m++) { sum += dist[t][m]; mx = std::max(mx, dist[t][m]); }
        interleave += sum / n; worst += mx;
    }
    local /= n; interleave /= n; worst /= n;
    assert(local == 10 && worst == 31);
    assert(local < interleave && interleave < worst);                      // 가까운 배치 < 인터리브 평균 < 최악
    assert(interleave == (10 + 21 + 21 + 31) / 4.0);                      // 평균 23.25 (= 지연 2.3배)
    int nodes = 0;
#if defined(__linux__)
    if (DIR* d = opendir("/sys/devices/system/node")) { while (dirent* e = readdir(d)) if (std::string(e->d_name).rfind("node", 0) == 0) nodes++; closedir(d); }
#endif
    std::cout << "NUMA distances: local=" << local << " interleave=" << interleave << " worst=" << worst << " (this machine reports " << nodes << " NUMA node(s))" << std::endl;
    return 0;
}
// Time Complexity: O(n²)
// Space Complexity: O(n²)
```
## C, C++, Java, Python의 메모리 관리 비교
### 대표코드
```cpp
#include <iostream>
#include <set>
#include <vector>
#include <cassert>

// 같은 객체 그래프를 네 가지 방식으로 정리하면 무엇이 회수되는가?  그래프: root -> a -> b,  c <-> d (서로만 가리키는 순환, root 에서 닿지 않음),  e (아무도 안 가리킴).  root 변수를 놓은 뒤:
//  C(수동)            : 프로그래머가 free 를 안 하면 전부 누수.
//  C++ RAII(shared_ptr): 참조 카운트 -> a, b, e 는 회수, 순환 c/d 는 누수.
//  Java(추적 GC)      : root 에서 닿지 않는 것을 전부 회수 (순환 포함).
//  Python             : 참조 카운트(즉시) + 순환 수집기(나중에) -> 즉시는 a, b, e / 순환 GC 실행 후 c, d 도.
struct Graph { std::vector<std::vector<int>> out; };       // 0=root 1=a 2=b 3=c 4=d 5=e
std::set<int> reachable(const Graph& g, int root) { std::set<int> seen{root}; std::vector<int> st{root}; while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : g.out[u]) if (seen.insert(v).second) st.push_back(v); } return seen; }
std::set<int> refcountFreed(const Graph& g, int droppedRoot) {                  // 카운트가 0 이 되는 것만 연쇄 해제
    int n = g.out.size(); std::vector<int> rc(n, 0); for (auto& o : g.out) for (int v : o) rc[v]++;
    rc[droppedRoot] = 0; std::set<int> freed; std::vector<int> st{droppedRoot}; freed.insert(droppedRoot);
    while (!st.empty()) { int u = st.back(); st.pop_back(); for (int v : g.out[u]) if (--rc[v] == 0 && freed.insert(v).second) st.push_back(v); }
    for (int v = 1; v < n; v++) if (rc[v] == 0 && !freed.count(v)) freed.insert(v);        // 처음부터 카운트 0 인 객체(e)
    return freed;
}

int main() {
    Graph g; g.out = {{1}, {2}, {}, {4}, {3}, {}};
    std::set<int> all = {1, 2, 3, 4, 5};                      // root 를 제외한 객체
    // C: 아무것도 해제하지 않음
    std::set<int> cLeaked = all;
    // C++ shared_ptr (참조 카운트만)
    auto rc = refcountFreed(g, 0); std::set<int> cppFreed; for (int v : rc) if (v != 0) cppFreed.insert(v);
    std::set<int> cppLeaked; for (int v : all) if (!cppFreed.count(v)) cppLeaked.insert(v);
    // Java: 추적 — root 변수를 놓았으므로 루트 집합이 비었고, 루트에서 닿는 객체가 없으니 전부 회수된다 (순환 포함)
    std::set<int> roots, live;                                   // 루트(스택 변수 등)가 없다
    for (int r : roots) { auto s = reachable(g, r); live.insert(s.begin(), s.end()); }
    std::set<int> javaFreed; for (int v : all) if (!live.count(v)) javaFreed.insert(v);
    // Python: 참조 카운트 + 순환 수집
    std::set<int> pyImmediate = cppFreed, pyAfterGc = all;
    assert((cppFreed == std::set<int>{1, 2, 5}));              // a, b, e 즉시 회수
    assert((cppLeaked == std::set<int>{3, 4}));                // 순환만 누수
    assert(cLeaked.size() == 5 && javaFreed.size() == 5);
    assert(pyImmediate.size() == 3 && pyAfterGc.size() == 5);
    std::cout << "Leaked after dropping root — C: " << cLeaked.size() << ", C++ shared_ptr: " << cppLeaked.size() << ", Java: 0, Python: 0 (after cycle GC)" << std::endl;
    return 0;
}
// Time Complexity: O(V + E)
// Space Complexity: O(V)
```
## JVM 메모리 구조
### 대표코드
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cassert>

// JVM 런타임 영역: 힙(Young: Eden + Survivor S0/S1, Old), 메타스페이스(클래스 메타데이터), 스레드별 스택(프레임), PC 레지스터, 네이티브 스택.
// 객체는 Eden 에서 태어나고, minor GC 때 살아있으면 Survivor 로 복사되며 나이(age)가 1 증가한다.  나이가 임계값(tenuring threshold, 기본 최대 15)에 이르면 Old 로 승급한다.
// 기본 비율 Eden : S0 : S1 = 8 : 1 : 1.  아래는 임계값 3 인 단순 모델
enum Space { EDEN, SURVIVOR, OLD, DEAD };
struct Obj { std::string name; Space where = EDEN; int age = 0; bool referenced = true; };
const int THRESHOLD = 3;

void minorGC(std::vector<Obj>& heap) {
    for (auto& o : heap) {
        if (o.where == DEAD || o.where == OLD) continue;               // minor GC 는 Young 영역만 처리
        if (!o.referenced) { o.where = DEAD; continue; }                // 쓰레기는 회수
        o.age++;
        o.where = (o.age >= THRESHOLD) ? OLD : SURVIVOR;                // 승급 조건
    }
}

int main() {
    std::vector<Obj> heap = {{"session"}, {"temp1"}, {"temp2"}, {"cache"}};
    heap[1].referenced = false; heap[2].referenced = false;             // 임시 객체는 금방 죽는다 (약한 세대 가설)
    minorGC(heap);
    assert(heap[1].where == DEAD && heap[2].where == DEAD);             // 대부분의 객체는 첫 minor GC 에서 사라진다
    assert(heap[0].where == SURVIVOR && heap[0].age == 1);
    minorGC(heap); assert(heap[0].where == SURVIVOR && heap[0].age == 2);
    minorGC(heap); assert(heap[0].where == OLD && heap[3].where == OLD);   // 세 번 살아남으면 Old 로 승급
    heap.push_back({"new"}); minorGC(heap);
    assert(heap.back().where == SURVIVOR && heap[0].where == OLD);        // Old 는 minor GC 에서 건드리지 않는다
    std::cout << "JVM generational model: long-lived objects tenured to Old after " << THRESHOLD << " survivals." << std::endl;
    return 0;
}
// Time Complexity: minor GC 는 Young 크기에 비례
// Space Complexity: O(힙)
```
## CPython 객체 모델
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <vector>
#include <cassert>

// CPython 의 모든 값은 PyObject 이고, 머리말은 (참조 횟수 ob_refcnt, 타입 포인터 ob_type) = 64비트에서 16바이트.  그래서 파이썬 int 하나가 최소 28~32바이트다.
// -5..256 의 작은 정수는 미리 만들어 둔 객체를 공유하므로 `a is b` 가 True.   list 는 append 가 O(1) 분할상환이 되도록 필요한 것보다 더 크게 용량을 잡는다 (over-allocation):
//   new_allocated = (newsize + (newsize >> 3) + 6) & ~3     -> 용량 변화 0, 4, 8, 16, 24, 32, 40, 52, 64, 76 ...
struct PyObjectHead { long ob_refcnt; void* ob_type; };
size_t growListAllocation(size_t allocated, size_t newsize) {
    if (newsize <= allocated) return allocated;
    return (newsize + (newsize >> 3) + 6) & ~(size_t)3;
}
const int SMALL_MIN = -5, SMALL_MAX = 256;
bool sameObject(long a, long b) { return a == b && a >= SMALL_MIN && a <= SMALL_MAX; }      // 작은 정수 캐시: 같은 값이면 같은 객체

int main() {
    assert(sizeof(PyObjectHead) == 16);
    std::vector<size_t> caps; size_t allocated = 0;
    for (size_t n = 1; n <= 76; n++) { size_t next = growListAllocation(allocated, n); if (next != allocated) { allocated = next; caps.push_back(allocated); } }
    assert((caps == std::vector<size_t>{4, 8, 16, 24, 32, 40, 52, 64, 76}));       // 실제 CPython 의 list 용량 변화와 같다
    assert(caps.size() == 9);                                                        // 76번 append 에 재할당은 9번뿐 (분할상환 O(1))
    assert(sameObject(100, 100) && sameObject(-5, -5) && !sameObject(257, 257));      // 256 까지만 캐시
    long refcnt = 1; refcnt++; refcnt--; refcnt--;                                   // 참조 횟수 규칙: 참조가 생기면 +1, 사라지면 -1, 0 이면 즉시 해제
    assert(refcnt == 0);
    std::cout << "CPython list capacities: 4 8 16 24 32 40 52 64 76; PyObject header = " << sizeof(PyObjectHead) << " bytes" << std::endl;
    return 0;
}
// Time Complexity: append 분할상환 O(1)
// Space Complexity: 용량이 길이보다 약 12.5% 크다
```
## Rust Ownership와 Borrow Checker
### 대표코드
```cpp
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cassert>

// Rust 의 빌림 검사기(borrow checker)가 컴파일 시점에 하는 일을 간단한 프로그램 표현 위에서 구현한다.
//  규칙: (1) 이동된 값은 사용할 수 없다 (E0382)  (2) 빌려준 동안 이동할 수 없다 (E0505)  (3) 가변 참조가 있는 동안 다른 참조·사용은 금지 (E0502/E0499/E0503)
//  (4) 불변 참조는 여러 개 가능하지만 가변 참조는 하나뿐 — "별칭 XOR 변경"
enum Kind { LET, MOVE, BORROW, BORROW_MUT, USE, USE_REF, END_BORROW };
struct Stmt { Kind k; std::string a, b; };           // LET x / MOVE x->y / BORROW x as r / BORROW_MUT x as r / USE x / USE_REF r / END_BORROW r

std::string check(const std::vector<Stmt>& prog) {
    std::set<std::string> moved; std::map<std::string, std::pair<std::string, bool>> refs;    // 참조 이름 -> (대상, 가변 여부)
    auto borrows = [&](const std::string& x, bool& anyMut, int& shared) { anyMut = false; shared = 0; for (auto& r : refs) if (r.second.first == x) { if (r.second.second) anyMut = true; else shared++; } };
    for (auto& s : prog) {
        bool anyMut; int shared;
        switch (s.k) {
            case LET: break;
            case MOVE: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut || shared) return "E0505"; moved.insert(s.a); break;
            case USE: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut) return "E0503"; break;
            case BORROW: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut) return "E0502"; refs[s.b] = {s.a, false}; break;
            case BORROW_MUT: borrows(s.a, anyMut, shared); if (moved.count(s.a)) return "E0382"; if (anyMut) return "E0499"; if (shared) return "E0502"; refs[s.b] = {s.a, true}; break;
            case USE_REF: if (!refs.count(s.a)) return "E0597"; break;
            case END_BORROW: refs.erase(s.a); break;
        }
    }
    return "OK";
}

int main() {
    assert(check({{LET, "x"}, {MOVE, "x", "y"}, {USE, "x"}}) == "E0382");                                    // 이동 후 사용
    assert(check({{LET, "x"}, {BORROW, "x", "r1"}, {BORROW, "x", "r2"}, {USE_REF, "r1"}, {USE_REF, "r2"}}) == "OK");   // 불변 참조는 여러 개
    assert(check({{LET, "x"}, {BORROW, "x", "r"}, {BORROW_MUT, "x", "w"}}) == "E0502");                       // 읽는 중에 가변 참조
    assert(check({{LET, "x"}, {BORROW_MUT, "x", "w1"}, {BORROW_MUT, "x", "w2"}}) == "E0499");                 // 가변 참조 둘
    assert(check({{LET, "x"}, {BORROW_MUT, "x", "w"}, {USE, "x"}}) == "E0503");                               // 가변 참조 중 원본 사용
    assert(check({{LET, "x"}, {BORROW, "x", "r"}, {MOVE, "x", "y"}}) == "E0505");                              // 빌려준 채 이동
    assert(check({{LET, "x"}, {BORROW_MUT, "x", "w"}, {END_BORROW, "w"}, {USE, "x"}}) == "OK");               // 참조가 끝나면 원본 사용 가능
    assert(check({{USE_REF, "ghost"}}) == "E0597");
    std::cout << "Borrow checker model: aliasing XOR mutation, move semantics enforced at 'compile time'." << std::endl;
    return 0;
}
// Time Complexity: O(문장 수 · 참조 수)
// Space Complexity: O(참조 수)
```
## CUDA 메모리 계층
### 대표코드
```cpp
#include <iostream>
#include <algorithm>
#include <cmath>
#include <cassert>

// GPU 메모리 계층(대략적인 값, 세대마다 다름): 레지스터(~1 사이클, 스레드 전용, 가장 빠름) > 공유 메모리(~30, 블록 내 공유, 프로그래머가 관리) > L1(~30) > L2(~200, GPU 전체)
// > 전역 메모리/HBM(~400~800, 대용량).  빠른 곳일수록 작다.  레지스터를 많이 쓰면 SM 에 동시에 올릴 수 있는 스레드가 줄어(occupancy 감소) 지연을 숨기지 못한다
struct Level { const char* name; double latency; double capacityKB; };
int main() {
    Level levels[] = {{"register", 1, 256}, {"shared", 30, 100}, {"L2", 200, 40960}, {"global", 600, 40000000}};
    for (int i = 0; i + 1 < 4; i++) assert(levels[i].latency < levels[i + 1].latency);          // 멀수록 느리다
    for (int i = 1; i + 1 < 4; i++) assert(levels[i].capacityKB < levels[i + 1].capacityKB);   // 공유 메모리 < L2 < 전역 (레지스터 파일은 SM 당 256KB 로 공유 메모리보다 클 수 있다)

    // 타일링 효과: 전역 메모리 값을 공유 메모리로 한 번 읽어 와 T 번 재사용하면 전역 접근이 1/T 로 줄어든다
    auto avgLatency = [&](double reuse) { return (levels[3].latency + (reuse - 1) * levels[1].latency) / reuse; };
    assert(avgLatency(1) == 600 && avgLatency(16) < 70 && 600 / avgLatency(16) > 9);   // 16번 재사용하면 평균 지연이 약 9배 감소

    // occupancy: SM 당 레지스터 65536 개, 최대 2048 스레드.  스레드당 레지스터가 많을수록 동시에 올릴 스레드가 줄어든다
    auto residentThreads = [](int regsPerThread) { return std::min(2048, 65536 / regsPerThread); };
    assert(residentThreads(32) == 2048 && residentThreads(64) == 1024 && residentThreads(128) == 512 && residentThreads(255) == 257);
    std::cout << "CUDA hierarchy: tiling x16 cuts mean latency 600 -> " << avgLatency(16) << "; 128 regs/thread -> " << residentThreads(128) << " resident threads" << std::endl;
    return 0;
}
// Time Complexity: O(1)
// Space Complexity: O(1)
```
## 현대 CPU 캐시 계층(L1/L2/L3)
### 대표코드
```cpp
#include <iostream>
#include <cstdint>
#include <list>
#include <random>
#include <vector>
#include <cassert>

// 전형적인 계층: L1 32KB(8-way, ~4사이클, 코어 전용) -> L2 256KB~1MB(~12, 코어 전용) -> L3 수 MB~수십 MB(~40, 코어 간 공유) -> DRAM(~200).
// 작업 집합(working set)의 크기가 어느 단계에 들어가느냐가 성능을 결정한다.  무작위 접근에서 단계별 적중률을 시뮬레이션으로 확인한다
struct Level {
    size_t sets, ways; std::vector<std::list<uint64_t>> s; long hits = 0;
    Level(size_t bytes, size_t w) : sets(bytes / 64 / w), ways(w), s(bytes / 64 / w) {}
    bool lookup(uint64_t line) { auto& set = s[line % sets]; for (auto it = set.begin(); it != set.end(); ++it) if (*it == line) { set.erase(it); set.push_front(line); hits++; return true; } return false; }
    void fill(uint64_t line) { auto& set = s[line % sets]; set.push_front(line); if (set.size() > ways) set.pop_back(); }
};
struct Hierarchy {
    Level l1{32 * 1024, 8}, l2{256 * 1024, 8}, l3{8 * 1024 * 1024, 16}; long mem = 0, total = 0;
    void access(uint64_t addr) {
        uint64_t line = addr / 64; total++;
        if (l1.lookup(line)) return;
        if (l2.lookup(line)) { l1.fill(line); return; }
        if (l3.lookup(line)) { l2.fill(line); l1.fill(line); return; }
        mem++; l3.fill(line); l2.fill(line); l1.fill(line);
    }
};
Hierarchy run(size_t workingSetBytes) {
    Hierarchy h; std::mt19937_64 rng(1);
    for (long i = 0; i < 1000000; i++) h.access((rng() % (workingSetBytes / 64)) * 64);       // 작업 집합 안에서 균등 무작위
    return h;
}

int main() {
    auto small = run(16 * 1024);                      // L1 에 들어감
    auto medium = run(128 * 1024);                    // L2 에 들어감
    auto large = run(4 * 1024 * 1024);                // L3 에 들어감
    auto huge = run(64 * 1024 * 1024);                // L3 보다 큼 -> DRAM
    assert(double(small.l1.hits) / small.total > 0.99);                                  // 16KB: 거의 전부 L1
    assert(double(medium.l1.hits) / medium.total < 0.35 && double(medium.l2.hits) / medium.total > 0.60);   // 128KB: L1 은 약 25%, 나머지는 L2
    assert(double(large.l3.hits) / large.total > 0.80 && double(large.mem) / large.total < 0.12);           // 4MB: 대부분 L3
    assert(double(huge.mem) / huge.total > 0.80);                                        // 64MB: 대부분 DRAM 까지 간다
    double amat = 4 + (1 - double(huge.l1.hits) / huge.total) * 12 + (double(huge.mem) / huge.total) * 200;
    std::cout << "hit rates — 16KB: L1 " << 100.0 * small.l1.hits / small.total << "%; 4MB: L3 " << 100.0 * large.l3.hits / large.total << "%; 64MB: DRAM " << 100.0 * huge.mem / huge.total << "% (rough AMAT " << amat << " cycles)" << std::endl;
    return 0;
}
// Time Complexity: O(접근 수 · 단계 수 · ways)
// Space Complexity: O(캐시 크기)
```
