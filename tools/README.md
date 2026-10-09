# tools

책(`*.md`)을 고치고 검증하는 도구 모음입니다. 모두 표준 라이브러리만 쓰는 Python 3 이고 `python3 -I`(격리 모드)로 실행합니다.

| 도구 | 하는 일 |
|------|---------|
| `check_all.py` | **커밋 전에 돌리는 빠른 관문**(몇 초, 컴파일 없음): 자체 테스트, 구조·자리표시·얕은 항목 0, 링크, 복잡도 표기, 생성 문서 최신성 |
| `audit.py` | 구조 점검과 **컴파일·실행 검증**. 모드: `--strict`(-Wall -Wextra, 경고도 실패) `--san`(ASan+UBSan+LSan) `--tsan`(ThreadSanitizer) `--portable`(clang++, g++ -std=c++20 -pedantic) `--repeat N`(스레드 블록 반복) `--time`(3초 넘는 블록). 결과는 블록 해시로 `~/.cache/ds-audit.json` 에 저장되어 바뀐 블록만 다시 돌린다 |
| `mdedit.py` | 책 파일 일괄 편집 DSL(`@@ CODE File.md :: ## 표제`). CRLF/LF·BOM 을 보존한다. 문법은 파일 머리말 참고 |
| `where.py` | 항목이 어느 책 몇 Part 에 있는지 조회 |
| `linkcheck.py` | `File.md Part N` 언급과 `정본은 …` 링크 주석의 대상 존재, 동명 항목의 분류(`canonical.json`) 검사 |
| `drift.py` | 링크형 요약이 정본과 다른 복잡도를 말하는지 비교(검토한 차이는 `canonical.json` 의 `drift_ok`) |
| `complexity_lint.py` | 모든 항목에 Time/Space 주석이 있는지(필수), 코드 구조와 어긋나 보이는 표기(`--advisory`) |
| `gen_index.py` | `INDEX.md`(목차·이식성 표), `COMPLEXITY.md`, README 의 현황 블록 생성. `--check` 는 최신 여부만 확인 |
| `test_tools.py` | 위 도구들의 자체 테스트(`python3 -I tools/test_tools.py`) |
| `canonical.json` | 동명 항목 분류표(generic / homonym / variant / link)와 검토 기록 |

## 작업 순서

```
python3 -I tools/mdedit.py batch.txt          # 또는 책을 직접 고친다
python3 -I tools/audit.py Tree --strict        # 고친 책만 컴파일·실행 검증
python3 -I tools/gen_index.py                  # 목차·복잡도 모음 갱신
python3 -I tools/check_all.py                  # 빠른 관문
```

릴리스 전에는 `python3 -I tools/audit.py --strict --san --tsan --portable --stamp` 를 돌립니다. 모든 책이 통과하면 `tools/last_audit.json` 에 날짜가 기록되고 `gen_index.py` 가 README 현황에 반영합니다.

## 코드 블록 표지

코드 주석에 `// audit: <표지>` 를 두면 해당 검사를 건너뜁니다.

| 표지 | 의미 |
|------|------|
| `no-sanitize` | 일부러 메모리 위반·프로세스 분기·한도 초과를 일으키는 항목이라 새니타이저/TSan 에서 제외 |
| `allow-warn` | 설명용으로 경고가 나는 코드를 일부러 보여 주는 항목 |
| `gcc-only` | `-pedantic` C++20 검사에서 제외(GCC 확장 사용) |
| `stl-demo` | STL 사용법을 보이는 것이 목적인 항목(얇은 항목 목록에서 제외) |
| `exhaustive` | 입력 공간 전체를 열거하므로 무작위 검사가 없어도 얕은 항목이 아님 |
| `known-answer` | 공개된 시험 벡터(해시·암호·부호화 표준 값)로 검증하는 항목 — `--list-weak` 에서 제외 |
| `closed-form` | 단언이 유도한 공식(예: 측정한 프레임 간격 차이 = 지역 배열 크기 차이)을 검사하는 항목 — `--list-weak` 에서 제외 |
| `differential` | 이름에는 드러나지 않지만 같은 함수를 독립적으로 쓴 두 번째 구현(예: 재귀 대 명시적 스택)과 출력을 비교하는 항목 — `--list-weak` 에서 제외 |
| `stress` | 보존 법칙(모든 값이 정확히 한 번 전달, 생산자별 순서, 풀 전부 반환)을 오라클로 삼는 동시성 스트레스 시험 — `--list-weak` 에서 제외 |

## 비결정성 규칙

난수는 고정 시드(`std::mt19937 rng(상수)`)만 쓰고, 단언은 시간이 아니라 횟수·불변식·정답과의 일치로 합니다. 새니타이저·clang 에서도 도는 코드라야 하므로 `assert` 안에 부작용을 넣지 않고(`bool ok = f(); assert(ok);`), `new` 로 만든 것은 모두 해제합니다.
