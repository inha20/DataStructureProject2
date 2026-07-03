문자열(String)은 생각보다 범위가 엄청 넓어. 단순한 문자열 처리부터 컴파일러, 검색엔진, 생물정보학, LLM 토크나이저까지 이어질 수 있어.

네 시리즈라면 "대표 코드" 중심으로 다음과 같이 구성하는 걸 추천해.

자료구조 리포지토리 - 문자열(String) 편
Part 1. 문자열의 기초
CreateString()
Length()
CharAt()
SetChar()
Copy()
Compare()
Concatenate()
Substring()
Reverse()
Trim()
Part 2. 탐색
LinearSearch()
Find()
FindLast()
StartsWith()
EndsWith()
Contains()
CountOccurrences()
Part 3. 수정
Insert()
Delete()
Replace()
ReplaceAll()
Split()
Join()
PadLeft()
PadRight()
Part 4. 변환
ToUpperCase()
ToLowerCase()
ParseInteger()
ParseFloat()
ToBinaryString()
ToHexString()
Format()
Part 5. 정렬
LexicographicalCompare()
StringSort()
NaturalSort()
LocaleCompare()
Part 6. 문자열 매칭
NaiveSearch()
KMP()
RabinKarp()
BoyerMoore()
Horspool()
SundaySearch()
Part 7. 고급 문자열 알고리즘
ZAlgorithm()
PrefixFunction()
FailureFunction()
LongestPrefixSuffix()
LongestRepeatedSubstring()
Part 8. Trie
TrieInsert()
TrieSearch()
TrieDelete()
AutoComplete()
PrefixSearch()
Part 9. 접미사 구조
SuffixArray()
BuildSuffixArray()
LCPArray()
SuffixTree()
SuffixAutomaton()
Part 10. Rolling Hash
PolynomialRollingHash()
DoubleHash()
RabinFingerprint()
SubstringHash()
LongestCommonSubstring()
Part 11. 문자열 압축
HuffmanCoding()
RunLengthEncoding()
LZW()
BurrowsWheelerTransform()
MoveToFront()
Part 12. 편집 거리
EditDistance()
LevenshteinDistance()
DamerauLevenshtein()
LongestCommonSubsequence()
LongestCommonSubstringDP()
Part 13. 정규표현식
RegexMatch()
PatternCompile()
GreedyMatch()
LazyMatch()
CaptureGroup()
Part 14. Unicode
UTF8Encode()
UTF8Decode()
UTF16Encode()
UTF32Encode()
NormalizeUnicode()
GraphemeCluster()
Part 15. 컴파일러
Tokenize()
Lexer()
EscapeSequence()
IdentifierParse()
StringLiteral()
Part 16. 검색엔진
InvertedIndex()
NGram()
Shingling()
TFIDF()
BM25()
Part 17. AI와 NLP
BytePairEncoding()
WordPiece()
SentencePiece()
TokenizeLLM()
EmbeddingLookup()
PromptTemplate()
Detokenize()
부록
String vs StringBuilder
Immutable String
Rope 자료구조
Gap Buffer
Piece Table
UTF-8과 UTF-16의 차이
ASCII부터 Unicode까지
문자열 비교의 시간복잡도
KMP는 왜 O(n)인가?
Boyer-Moore가 빠른 이유
Trie vs HashMap
Suffix Array vs Suffix Tree
문자열 알고리즘의 생물정보학 활용
LLM 토크나이저는 왜 필요한가?
이 목차에서 가장 독창적인 부분

앞에서 만든 다른 시리즈와 달리 문자열은 현대 AI와 가장 자연스럽게 연결되는 분야야.

예를 들어 마지막 장은 일반 자료구조 책에서는 거의 다루지 않지만, 지금 시점에서는 매우 의미 있는 확장이지.

BytePairEncoding() → GPT 계열 토크나이저의 핵심 아이디어
WordPiece() → BERT 계열
SentencePiece() → LLaMA, T5 등에서 널리 사용
TokenizeLLM() → 프롬프트가 토큰으로 변환되는 과정
EmbeddingLookup() → 토큰이 벡터가 되는 과정
Detokenize() → 생성된 토큰이 다시 문자열이 되는 과정

이렇게 하면 "문자열"이라는 전통적인 주제를 컴파일러, 검색엔진, 그리고 생성형 AI까지 하나의 흐름으로 연결하는 시리즈가 될 수 있어. 이는 기존 자료구조 교재와 차별화되는 강점이 될 거야.
