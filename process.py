import os

workspace = r'C:\Users\cjh3c\OneDrive\바탕 화면\DataStructureProject2-main'

files = [
    'AdvancedDataStructures.md',
    'Graph.md',
    'Hash.md',
    'List.md',
    'Memory.md',
    'PathFinding.md',
    'Queue.md',
    'Set.md',
    'Stack.md',
    'String.md',
    'Tree.md'
]

traits = []

def is_chapter(line):
    return line.startswith('Part ') or line.startswith('부록') or line.startswith('마지막 부록')

for file in files:
    filepath = os.path.join(workspace, file)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    
    new_lines = []
    
    for line in lines:
        if not line.strip():
            continue
            
        # Characteristic text to match
        skip = False
        for text in [
            '문자열(String)은 생각보다 범위가',
            '네 시리즈라면 "대표 코드" 중심으로',
            '자료구조 리포지토리 -',
            '이 목차에서 가장 독창적인 부분',
            '앞에서 만든 다른 시리즈와 달리',
            '예를 들어 마지막 장은 일반 자료구조',
            'BytePairEncoding() → GPT 계열',
            'WordPiece() → BERT 계열',
            'SentencePiece() → LLaMA',
            'TokenizeLLM() → 프롬프트가',
            'EmbeddingLookup() → 토큰이',
            'Detokenize() → 생성된',
            '이렇게 하면 "문자열"이라는 전통적인',
            '해시는 학부에서는 보통',
            '개인적으로 추가하고 싶은 장',
            '네 리포지토리는 "구조를 시각적으로',
            '이런 장은 일반 자료구조 책에서는',
            '이 책에서 특히 강조하면 좋은 주제',
            '이 시리즈는 단순히 자료구조를',
            '예를 들어 하나의 Union() 함수도',
            '수학: 합집합',
            'C++ STL: std::set_union',
            'Python: set.union()',
            '데이터베이스: UNION',
            '그래프: Union-Find',
            '비트마스크: OR 연산',
            'AI: 후보(Label) 집합 병합',
            '이처럼 하나의 연산을 여러 분야의',
            '이 책의 차별점',
            '이 책은 단순히 메모리 API를',
            '예를 들어 malloc() 하나의 장도',
            '함수 호출 전 힙 상태',
            '할당 가능한 블록 탐색',
            '메타데이터(Header) 생성',
            '사용자 포인터 반환',
            '할당 후 메모리 레이아웃',
            'free() 호출 시 Free List 변화',
            '단편화가 누적되는 과정',
            'Memory Pool과의 비교',
            '이런 식으로 메모리 상태의 변화를',
            '개인적으로는 지금까지 이야기한 리스트',
            '이 책의 역할',
            '이 책은 학부 교재의 연장선이라기보다',
            '예를 들어 마지막 장에 있는 항목들은',
            'HNSW → 벡터 검색',
            'FAISSIndex → 대규모 유사도',
            'LSMTree → RocksDB',
            'AdaptiveRadixTree → 메인 메모리',
            'LearnedIndex → 머신러닝을 이용한',
            'CacheObliviousBTree → 메모리 계층',
            '이렇게 구성하면 시리즈 전체가 입문부터'
        ]:
            if line.startswith(text):
                traits.append(f'[{file}] ' + line)
                skip = True
                break
                
        if skip:
            continue
            
        if is_chapter(line):
            new_lines.append(f'# {line}')
        else:
            new_lines.append(f'## {line}')
            new_lines.append('### 대표코드\n```cpp\n\n```')
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')

readme_path = os.path.join(workspace, 'README.md')
with open(readme_path, 'r', encoding='utf-8') as f:
    readme_content = f.read()

start_marker = '-----------------------------------문서의 특색 및 리포지토리의 특색-----------------------'
end_marker = '-----------------------------------끝--------------------------------------'

start_idx = readme_content.find(start_marker)
end_idx = readme_content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_readme = readme_content[:start_idx + len(start_marker)] + '\n\n' + '\n\n'.join(traits) + '\n\n' + readme_content[end_idx:]
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_readme)

print('Done!')
