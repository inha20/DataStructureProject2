# COMPLEXITY

> 각 항목 코드 끝의 `// Time Complexity:` / `// Space Complexity:` 주석을 모았다. `python3 -I tools/gen_index.py` 가 만든다.

## AdvancedDataStructures

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `PersistentArray` | 1 | 읽기·갱신 O(log N) | 버전당 O(log N) |
| `PersistentList` | 1 | cons·tail O(1), setAt·at O(i), concat O(\|a\|) | 변경마다 새 노드 O(i) 만 추가 |
| `PersistentStack` | 1 | push·pop·top O(1), 공유 접미사 O(길이) | 버전당 O(1), push 마다 셀 하나 |
| `PersistentQueue` | 1 | snoc·tail·head 최악 O(1) (영속 사용에서도) | O(N) |
| `PersistentSegmentTree` | 1 | 구성 O(N log N), 질의 O(log N) | O(N log N) |
| `PersistentTrie` | 1 | 구성 O(N·B), 질의 O(B)  (B = 비트 수) | O(N·B) |
| `HAMT` | 1 | 조회·삽입·삭제 O(log32 N) — 해시 64 비트라서 최대 13 층(= 사실상 O(1)), 삽입 한 번이 만드는 노드는 경로 길이만큼 | O(N) (노드마다 실제 자식 수만큼의 배열 + 비트맵), 버전 하나를 더 두는 비용은 O(log32 N) |
| `RRBVector` | 1 | get·set O(M log_M N), concat·slice O(M log_M N) (이음매 한 줄만 다시 만든다), pushBack O(M log_M N) | O(N), 새 버전 하나는 경로만큼(O(M log_M N))의 새 노드 |
| `BitVector` | 2 | get·set O(1), count O(N/64) | N 비트 |
| `Rank` | 2 | rank O(1) (최대 8 워드 popcount 상수 번) | N + 0.0625 N 비트 |
| `Select` | 2 | select O(log (표본 사이의 워드 수)) + O(1) | N + 표본 O(N/1024) |
| `WaveletTree` | 2 | 구성 O(N log σ), 질의 O(log σ) | N log σ 비트 (+ 랭크 디렉터리) |
| `FMIndex` | 2 | count O(\|P\|·B) (Occ 체크포인트 간격 B), locate 는 행마다 O(s·log) 걸음, 구성 O(n log n) | BWT n 바이트 + Occ 체크포인트 n/B·σ 정수 + SA 표본 n/s 개 |
| `SuccinctTrie` | 2 | 이동 O(1) (rank/select 가 O(1) 일 때), 단어 조회 O(\|w\|·σ) | 구조 2N+1 논리 비트 + 라벨 N 문자 (이 데모의 int 로 저장한 B 와 rank/select 표는 O(N) 워드; 간결 구현은 N 비트 + o(N) 디렉터리) |
| `BitmapIndex` | 2 | 동치·AND·OR·NOT O(N/64), 범위 질의·합 O(B·N/64) (B: 값의 비트 수), 압축 AND O(두 압축열 길이의 합) | 동치 부호화 O(C·N/8) 바이트(C: 서로 다른 값 수), 비트 슬라이스 O(B·N/8) |
| `BloomFilter` | 3 | 삽입·조회 O(k) | 약 1.44 n log2(1/p) 비트 |
| `CountingBloomFilter` | 3 | 삽입·삭제·조회 O(k) | 카운터당 4비트 → 블룸 필터의 4배 |
| `CuckooFilter` | 3 | 조회·삭제 O(1) (버킷 2개), 삽입 분할상환 O(1) | 키당 f / 부하율 비트 (f=12, 부하 95% -> 약 12.6 비트) |
| `QuotientFilter` | 3 | 조회·삽입 O(클러스터 길이) = 기대 O(1) (부하율이 낮을 때) | 원소당 r + 3 비트 |
| `XORFilter` | 3 | 조회 O(1) (메모리 접근 3번), 구성 O(N) 기대 | 약 1.23 N 바이트 (지문 8비트) |
| `CountMinSketch` | 3 | 갱신·질의 O(d) = O(log 1/δ) | O((1/ε) log (1/δ)) 카운터 |
| `HyperLogLog` | 3 | 삽입 O(1), 추정 O(m) | m 레지스터 (p=14 이면 6비트씩 약 12 KB) |
| `TDigest` | 3 | 추가 분할상환 O(log δ), 분위수 질의 O(δ) | O(δ) 중심점 |
| `MisraGries` | 3 | add 분할상환 O(1)~O(k) (전체 -1 은 k 개 카운터를 훑지만 그 전에 최소 k 번 +1 이 필요), merge O(k) | O(k) |
| `SpaceSaving` | 3 | add O(log k) (힙 내리기·올리기), 조회 O(1) | O(k) |
| `CountSketch` | 3 | update·estimate O(d), 표 합치기 O(d·w) | O(d·w) |
| `ReservoirSampling` | 3 | 알고리즘 R O(n), 알고리즘 L 기대 O(k (1 + log(n/k)))  (건너뛴 항목은 읽지 않아도 된다) | O(k) |
| `Rope` | 4 | 색인·분할·삽입·삭제·구간 뒤집기·이동 기대 O(log N) | O(N) (글자당 노드 하나) |
| `PieceTable` | 4 | 삽입·삭제 O(조각 수), 텍스트 조립 O(길이), undo·redo O(1) (스냅샷 버퍼 교체, 복사 없음; 삽입·삭제가 조각 목록을 스냅샷으로 복사하므로 O(조각 수)) | 원본 + 추가 버퍼 + 조각 목록 (+ undo 스냅샷마다 조각 목록 한 벌) |
| `GapBuffer` | 4 | 커서 위치 삽입·삭제 분할상환 O(1), 커서 이동 O(거리) | O(N + 틈) |
| `FingerTree` | 4 | 양 끝 push/pop 분할상환 O(1), concat O(log N), split/index O(log N) | O(N), 버전 사이에 구조 공유 |
| `SuffixAutomaton` | 4 | 구성 O(n·σ) (복제 시 전이 배열 복사), 출현 횟수 집계 countEndpos 는 std::sort 때문에 O(n log n) (계수 정렬이면 O(n)), 부분 문자열 판정 O(m) | O(n·σ) |
| `PatriciaTrie` | 4 | 삽입·삭제·조회 O(\|key\|) | O(키 수) 노드 (노드 수 < 2 · 키 수) |
| `KDTree` | 5 | 구성 O(N log N), 최근접 질의 평균 O(log N) | O(N) |
| `QuadTree` | 5 | 삽입 O(깊이), 범위 질의 O(깊이 + k) | O(N) |
| `Octree` | 5 | 삽입 O(깊이), 범위 질의 O(깊이 + k) | O(N) |
| `RTree` | 5 | 벌크 로드 O(N log N), 질의 O(log N + k) (겹침이 적을 때) | O(N) |
| `BallTree` | 5 | 구성 O(N log N), kNN 평균 O(log N) ~ O(N^(1-1/d)) | O(N) |
| `BVHTree` | 5 | 구성 O(N log N), 레이 질의 평균 O(log N) | O(N) |
| `BKTree` | 5 | 검색 평균 O(N^α) (α < 1, 반경이 작을수록 가지치기가 잘 됨) | O(N) |
| `VPTree` | 5 | 구성 O(N log N), kNN 평균 O(log N) (차원이 낮거나 군집이 있을 때) | O(N) |
| `CoverTree` | 5 | 삽입 O(c^6 log N), NN 질의 O(c^12 log N) (c: 팽창 상수) | O(N) |
| `DCEL` | 5 | 만들기 O(E log E) (점마다 각도 정렬), 면·점 둘레 훑기 O(둘레 길이), splitFace O(1) (+ 면 번호 다시 매기기 O(E)) | O(V + E) |
| `QuadEdge` | 5 | MakeEdge·Splice·Connect·DeleteEdge 모두 O(1), 점·면 훑기는 둘레 길이에 비례 | 변 하나당 4 칸 (Onext) + 시작점 — O(E) |
| `SegmentTree` | 6 | build O(N), 구간 갱신·구간 합 O(log N) | O(N) (4N 칸) |
| `LazyPropagation` | 6 | 갱신·질의 O(log N) | O(N) |
| `FenwickTree` | 6 | 점 갱신·접두 합 O(log R · log C), 직사각형 합 4 번의 접두 합 | O(R · C) |
| `SparseTable` | 6 | 구성 O(N log N), 멱등 연산 질의 O(1) | O(N log N) |
| `IntervalTree` | 6 | 질의 O(log N + k) | O(N) |
| `RangeTree` | 6 | 구성 O(N log N), 개수 질의 O(log² N) | O(N log N) |
| `DisjointSparseTable` | 6 | 전처리 O(N log N), 질의 O(1) (연산 ⊕ 두 번) | O(N log N) |
| `SqrtTree` | 6 | 전처리 O(N log log N), 질의 O(1) | O(N log log N) |
| `AVLTree` | 7 | join O(\|높이 차\|), split O(log N), 합집합·교집합·차집합 O(m log(n/m + 1)) | O(N) (함수형 — 연산마다 O(log N) 새 노드) |
| `RedBlackTree` | 7 | 삽입·삭제·조회 O(log N) | O(N) |
| `AA Tree` | 7 | 삽입·삭제·탐색 O(log N) | O(N) |
| `Treap` | 7 | 삽입·삭제·탐색 기대 O(log N) | O(N) |
| `SplayTree` | 7 | 분할상환 O(log N), 작업 집합 크기 w 에서 O(log w) | O(N) |
| `ScapegoatTree` | 7 | 삽입·삭제 분할상환 O(log N), 검색 O(log N) | O(N) (노드마다 부분 트리 크기) |
| `TangoTree` | 7 | 접근열 X 에 대해 기대 O((k + 1)(1 + log log N)) (k = 선호 자식이 바뀐(join 한) 횟수 <= interleave 하한 + N + \|X\|; 보조 트리가 트립이므로 l | O(N) |
| `BTree` | 8 | 검색·삽입·삭제 O(t · log_t N), 디스크 접근 O(log_t N) | O(N) |
| `BPlusTree` | 8 | 검색·삽입·삭제 O(log_M N), 범위 질의 O(log_M N + k) | O(N) |
| `BStarTree` | 8 | 삽입·탐색 O(log N) 노드 접근 | O(N), 노드 이용률 >= 2/3 |
| `FractalTree` | 8 | 삽입 분할상환 O(log_B N / B^(1-ε)) 노드 접근, 조회 O(log_B N) | O(N) |
| `LSMTree` | 8 | 쓰기 분할상환 O(쓰기 증폭), 읽기 O(레벨 수 × 파일당 이분 탐색) (블룸 필터로 대부분 생략) | O(N) + 공간 증폭 (툼스톤·중복) |
| `BufferTree` | 8 | 연산당 분할상환 I/O O((1/B) log_{M/B} (N/B)) | O(N) |
| `CSBPlusTree` | 8 | 검색 O(log_{K+1} N) 노드 (노드 안 이분 탐색), 삽입은 그룹 안 이동 O(K) 이 층마다 더해져 O(K log_{K+1} N) | O(N), 내부 노드에 자식 포인터가 하나뿐이라 같은 크기 노드에 키가 약 2.6 배 |
| `BwTree` | 8 | 조회 O(체인 길이 + log 페이지 크기) — 체인은 CONSOLIDATE_AT 이하, 갱신 O(1) CAS (+ 통합 O(페이지 크기)) | O(N + 델타·휴지통) — 휴지통은 통합마다 늘어 (실제로는 에포크 회수로 비운다) |
| `Masstree` | 8 | 키 길이 L 바이트에 대해 O(L/8) 층 x 층당 O(log N) 정수 비교 (원래 구현은 B+-트리, 여기서는 std::map) | O(N·L) 최악, 접미사 달기로 층은 키 둘 이상이 8 바이트 조각을 공유할 때만 생긴다 |
| `LockFreeQueue` | 9 | enqueue·dequeue 락프리 (경쟁 없을 때 O(1)) | O(N) 노드 풀 (재활용 없음) |
| `LockFreeStack` | 9 | push·pop 락프리 (경쟁 없을 때 O(1)) | O(N) 고정 풀 (노드 재활용, 태그로 ABA 방지) |
| `ConcurrentHashMap` | 9 | 평균 O(1) (조각 잠금 구간), size·snapshot 은 O(S + N) | O(N + S) |
| `SkipListSet` | 9 | 탐색·삽입 기대 O(log N) | 기대 O(N) (노드당 평균 2 개의 포인터) |
| `CompareAndSwap` | 9 | 경쟁 없을 때 연산당 O(1), 경쟁이 있으면 재시도 (락프리: 시스템 전체로는 진행) | O(1) |
| `HazardPointer` | 9 | 읽기 O(1) 공시 + 재검증, 회수 분할상환 O(스레드 수) per 노드 | 미회수 노드 수 <= 스레드 수 × (임계값 + 스레드 수) |
| `ChaseLevDeque` | 9 | push·pop 상수(소유자, 대개 원자 연산 없음), steal 상수(CAS 한 번), 증가는 분할상환 O(1) | O(최대 원소 수) (옛 배열 합쳐 최대 2배) |
| `Disruptor` | 9 | publish·consume 상수(원자 연산 몇 번 + 대기), 대기는 가장 느린 소비자에 좌우 | O(링 크기) 고정, 이벤트 할당 없음 |
| `RCU` | 9 | 읽기 O(1) (락 없음), synchronize O(독자 칸 수 + 가장 긴 읽기 구간) | O(독자 수) 칸 + 객체 (유예 기간 동안 옛 버전 하나가 더 산다) |
| `Seqlock` | 9 | 읽기 O(N) 복사 + 재시도(쓰기와 겹칠 때), 쓰기 O(N) | O(N) + 카운터 하나 |
| `EpochBasedReclamation` | 9 | enter·leave O(1), retire 분할상환 O(스레드 수) (시대 전진 검사 32 번에 한 번) | O(스레드 수 + 폐기 대기 노드) — 멈춘 스레드가 있으면 대기 노드가 무한히 쌓일 수 있다 |
| `ConsistentHashing` | 10 | 조회 O(log (N·V)) (이분 탐색), 서버 추가·삭제 O(V log (N·V)) | O(N · V) |
| `DistributedHashTable` | 10 | 라우팅 O(log N) 홉, put/get O(log N + R) | 노드당 finger 24 개 + 맡은 키 |
| `Chord` | 10 | 조회 O(log N) 홉 | 노드당 O(log N) 손가락 |
| `Kademlia` | 10 | 조회 O(log N) 라운드 | 노드당 O(k log N) 연락처 |
| `MerkleTree` | 10 | 구축 O(N), 감사 경로 생성·검증 O(log N), 차이 찾기 O(k log N) | O(N) |
| `MerklePatriciaTrie` | 10 | 조회·삽입·삭제·증명 생성 O(키 길이(니블)), 검증 O(증명 길이) 번의 SHA-256 | O(N·키 길이) 노드 + 갱신 한 번당 경로 길이만큼의 새 노드(영속) |
| `CRDT` | 10 | 연산 O(1)~O(원소 태그 수), 병합 O(상태 크기) | O(복제본 수 + 태그 수) |
| `GPUBVH` | 11 | 구성 O(N log N) (정렬) + 노드별 O(log N), GPU 병렬이면 정렬 이후 O(log N) 단계 | O(N) |
| `CUDASparseMatrix` | 11 | SpMV O(nnz) (ELL 은 O(K·rows)) | CSR O(nnz + rows), ELL O(K·rows) |
| `ParallelPrefixSum` | 11 | 작업 O(N), 깊이 O(log N) (Blelloch) | O(N) |
| `ParallelHashTable` | 11 | 삽입·조회 기대 O(1) (부하율이 낮을 때) | 고정 용량 (키 8 B + 값 4 B) × 슬롯 |
| `WarpQueue` | 11 | 워프당 원자 연산 1회 (푸시당 O(1/레인 수)) | 큐 용량 |
| `VectorIndex` | 12 | 질의 O(N·D + N log k) | O(N·D) |
| `HNSW` | 12 | 질의·삽입 평균 거리 계산이 N 에 대해 부선형 (저차원에서는 대략 O(log N) 으로 보고, 이 16 차원 군집 데이터는 N 이 5 배일 때 약 2.3 배로 관측 — 경험적, 보장 아님) | O(N·(D + M)) |
| `IVFIndex` | 12 | 질의 O(nlist·D + (N/nlist)·nprobe·D) | O(N·D + nlist·D) |
| `ProductQuantization` | 12 | 학습 O(m·ksub·N·dsub·반복), 질의 표 만들기 O(ksub·D) + 벡터당 O(m) | 벡터당 m 바이트 + 코드북 m·ksub·dsub |
| `KDTreeKNN` | 12 | 질의 평균 O(log N + k) (저차원) | O(N) |
| `BallTreeKNN` | 12 | 질의 평균 O(√N) (한 층 판), 계층 볼 트리는 O(log N) | O(N) |
| `AnnoyIndex` | 12 | 구성 O(트리 수 · N log N), 질의 O(search_k + 후보 정확 거리) | O(트리 수 · N) |
| `FAISSIndex` | 12 | 질의 O(nlist·D + nprobe·(ksub·D + 목록 길이·m) + R·D) | 벡터당 m 바이트 + id, 코드북·중심 O(nlist·D + m·ksub·dsub) |
| `SkipList` | 13 | 탐색·삽입 기대 O(log N) | 기대 O(N) |
| `MemTable` | 13 | 쓰기·읽기 기대 O(log N), flush 순회 O(N) | O(쓰기 수) — 갱신도 새 항목이라 한도에 이를 때까지 커진다 |
| `SSTable` | 13 | 조회 O(log (블록 수) + 블록 안 레코드 수), 블록 읽기 1 회 | 파일 O(N), 메모리에는 인덱스·필터만 |
| `WriteAheadLog` | 13 | append O(레코드), 재생 O(로그 길이) | 로그 크기 (체크포인트 후 앞부분 삭제) |
| `BTreeIndex` | 13 | 조회 O(log_F N) 페이지 읽기 (페이지 안 탐색은 메모리) | 데이터 N 키 + 인덱스 단계들 (전체의 1/P 정도) |
| `HashIndex` | 13 | 등치 조회 평균 O(1) 페이지, 범위 조건은 O(전체 페이지) | O(N / cap + B) 페이지 |
| `BuddyAllocator` | 14 | 할당·해제 O(log (전체 페이지 수)) | 차수별 빈 목록 + 할당 표 |
| `SlabAllocator` | 14 | 할당·해제 O(1) (집합 연산은 슬랩 수에 로그; 실제 구현은 이중 연결 리스트로 O(1)) | 슬랩 페이지 + 칸당 1 바이트 표 |
| `RadixTree` | 14 | 조회·삽입·삭제 O(키 비트 / 4), 후속자 O(깊이 · 16) | 쓰인 경로 비례 (조밀하면 키 수 / 15 근처) |
| `XArray` | 14 | 조회·저장·삭제 O(높이 = ⌈log64 (최대 인덱스)⌉), 다음 항목 찾기 O(높이 + 건너뛴 칸을 비트로) | 쓰인 인덱스 구간 비례, 노드 64 칸 |
| `PageTable` | 14 | 변환 O(레벨 수) = 메모리 접근 4 번 (큰 페이지 3 번, TLB 적중 0 번) | 사용한 영역 비례 (영역마다 테이블 쪽 3 개 + 공유 루트) |
| `LearnedIndex` | 15 | 조회 O(1) 모델 계산 + O(log (오차 구간)), 구성 O(N) | O(모델 수) (키 배열 제외) |
| `LearnedHash` | 15 | 해시 계산 O(log (표본점 수)) 이분 탐색 | O(표본점 수) |
| `AdaptiveRadixTree` | 15 | 조회·삽입·삭제 O(키 길이) (키 수와 무관) | 노드 형식 적응으로 키당 평균 약 8.1 바이트 오버헤드 (논문 보고, 이 코드는 구조만 검증) |
| `CacheObliviousBTree` | 15 | 탐색 O(log_B N) 블록 전송 (모든 B 에 대해 동시에) | O(N) |
| `FusionTree` | 15 | predecessor O(log_{k+1} N) 노드 방문 × 노드당 O(1) 워드 연산 (스케치 추출 제외) | O(N) |
| `vanEmdeBoasTree` | 15 | successor O(1) 클러스터 2 번 + 요약 1 번 (이 2 단 판), 완전 재귀판은 O(log log U) | O(U) 비트 |
| `XFastTrie` | 15 | pred/succ O(log w), 삽입·삭제 O(w) | O(n w) |
| `YFastTrie` | 15 | pred/succ/삽입/삭제 O(log w) (삽입·삭제는 분할상환) | O(n) |
| `EliasFano` | 15 | access O(1) (select 표본 간격 상수), nextGEQ 기대 O(1 + 버킷 크기) | n(2 + ⌈log2(u/n)⌉) 비트 |
| `CompressedSuffixArray` | 15 | 검색 O(m log n) 번 Ψ 계산, locate O(S) 번 Ψ 계산 (S = 표본 간격) | 글자당 약 H0 + O(1) 비트 + SA 표본 n/S 개 |
| `DynamicWaveletTree` | 15 | 연산당 O(log n · log σ) | O(n log σ) 노드 (비트 하나가 트립 노드 하나) |
| `PackedMemoryArray` | 15 | 삽입·삭제 분할상환 O(log² n) 이동, 범위 스캔 O(k) (순차 메모리) | O(n) (밀도 0.1 ~ 0.5 유지) |
| `CacheAwareBTree` | 15 | 탐색 O(log_F N) 캐시 라인 (F = 라인 크기 / 키 크기) | 정렬 배열 + N/(F-1) 개 표본 |
| `LearnedBloomFilter` | 15 | 조회 O(특징 수 + k) (모델 한 번 + 필요 시 백업 필터) | 모델 + 놓친 키 수 × O(log 1/p) 비트 |
| `Cache-Aware vs Cache-Oblivious` | 0 | 전치 O(N²) 연산, 캐시 미스는 인지형·무관형 모두 O(N²/L) (곱셈은 O(N³ / (L·√M))) | O(N²) |
| `Immutable vs Persistent` | 0 | 전체 복사 갱신 O(N), 영속 갱신 O(log N) | 영속 버전당 O(log N) |
| `Lock-Free vs Wait-Free` | 0 | CAS 루프: 경쟁 시 한 스레드의 재시도에 상한이 없다(락프리), fetch_add: O(1) 웨이트프리 | O(1) |
| `Online vs Offline 자료구조` | 0 | 온라인 질의당 O(log N), 오프라인 전체 O((N + Q) α(N)) | 온라인 O(N log N), 오프라인 O(N + Q) |
| `Static vs Dynamic 자료구조` | 0 | 정적 질의 O(1)·갱신 시 재구성 O(N log N), 동적 질의·갱신 O(log N) | 정적 O(N log N), 동적 O(N) |
| `Internal Memory vs External Memory` | 0 | 외부 병합 정렬 I/O O((N/B) log_{M/B}(N/B)), 힙 정렬 I/O O(N log (N/M)) | O(N) 디스크 + O(M) 메모리 |
| `Exact vs Approximate 자료구조` | 0 | 근사 구조 연산은 모두 O(1)~O(d) | 근사 구조는 원소 수와 무관한 고정 크기(ε, δ, p 로 결정), 정확 구조는 O(N) |
| `CPU 자료구조 vs GPU 자료구조` | 0 | 이 시뮬레이션은 O(N) | O(N) |
| `LSM Tree가 SSD에 적합한 이유` | 0 | 시뮬레이션 O(쓰기 수 × 블록 수) | O(물리 페이지 수) |
| `벡터 데이터베이스는 왜 HNSW를 사용하는가?` | 0 | 그래프 질의는 경험적으로 부선형 (이 데모에서 N 이 8 배일 때 약 2.5 배; 저차원 가정 하에서 O(log N) 으로 보고됨, 보장 아님), IVF 는 이상적으로 O(√N)(여기서 약 3.8  | 그래프 O(N·(D + M)), IVF·KD 트리 O(N·D) |
| `현대 데이터베이스가 B+Tree와 LSMTree를 함께 사용하는 이유` | 0 | 시뮬레이션 O(연산 수 · log N) | O(N) |
| `생성형 AI 시대의 자료구조` | 0 | 블록 할당·해제 O(1), 논리 위치 -> 물리 블록 변환 O(1) (블록 테이블 조회) | 요청당 O(길이/블록) 테이블 + 사용한 블록 |

## Graph

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateGraph` | 1 | O(V + E) (중복 검사가 선형이면 O(E · 차수)) | O(V + E) |
| `AddVertex` | 1 | 인접 리스트 분할상환 O(1), 행렬 O(V) ~ O(V²) | O(V + E) (행렬은 O(V²)) |
| `RemoveVertex` | 1 | 표시 O(deg), 마지막 옮기기 O(deg · 이웃 차수), 압축 O(V + E) | O(1) 추가 (압축은 O(V + E)) |
| `AddEdge` | 1 | 해시 검사 기대 O(1), 선형 검사 O(deg) | O(1) 추가 |
| `RemoveEdge` | 1 | 탐색 O(deg), 위치 맵 기대 O(1) | O(1) 추가 (위치 맵은 O(E)) |
| `VertexCount` | 1 | O(1) (카운터), 재계산 O(용량) | O(1) |
| `EdgeCount` | 1 | O(1) (카운터), 재계산 O(V + E) | O(1) |
| `Degree` | 1 | deg(v) O(1) (카운터) 또는 O(deg), 하벨–하키미 O(n² log n) | O(V) |
| `InDegree` | 1 | 질의 O(1) (역방향 리스트·카운터), 훑기 O(V + E) | O(V + E) |
| `OutDegree` | 1 | 질의 O(1), 전체 O(V) | O(V) |
| `AdjacencyMatrix` | 2 | 간선 질의 O(1), 이웃 훑기 O(V/64 + deg), 폐쇄 O(V³/64) | O(V²/8) 바이트 |
| `AdjacencyList` | 2 | 이웃 훑기 O(deg), 간선 질의 O(deg) (정렬 시 O(log deg)), 전치 O(V + E) | O(V + E) |
| `EdgeList` | 2 | 이웃 질의 O(E) (정렬 시 O(log E + deg)), 계수 정렬 변환 O(V + E), 정렬 변환 O(E log E) | O(E) |
| `IncidenceMatrix` | 2 | 구성 O(V · E), 행렬 곱 O(V² E) | O(V · E) |
| `CompressedSparseRow` | 2 | 구성 O(V + E) (기수 정렬 — 비교 정렬 없음), 이웃 훑기 O(deg), 행렬-벡터 곱 O(E) | O(V + E) |
| `CompressedSparseColumn` | 2 | 열 훑기 O(indeg), 전치 O(V + E), 곱셈 O(E) | O(V + E) |
| `BreadthFirstSearch` | 3 | O(V + E) | O(V) |
| `DepthFirstSearch` | 3 | O(V + E) | O(V) (재귀 깊이 포함) |
| `IterativeDFS` | 3 | O(V + E) | O(V) (단순형은 최악 O(E)) |
| `RecursiveDFS` | 3 | O(V + E) | O(V) (호출 스택 최대 깊이 = DFS 트리 높이) |
| `GraphTraversal` | 3 | 큐·스택 O(V + E), 우선순위 큐 O(E log V) | O(V + E) (프런티어 포함) |
| `ConnectedComponents` | 4 | O(V + E) (서로소 집합 O(E α(V)), 라벨 전파 O(지름 · E)) | O(V) |
| `StronglyConnectedComponents` | 4 | O(V + E) | O(V) |
| `WeaklyConnectedComponents` | 4 | O(E α(V)) | O(V) |
| `IsConnected` | 4 | O(V + E) | O(V + E) |
| `ArticulationPoint` | 4 | O(V + E) | O(V) |
| `Bridge` | 4 | O(V + E) | O(V + E) |
| `DetectCycle` | 5 | O(V + E) | O(V + E) |
| `DetectCycleDFS` | 5 | O(V + E) | O(V + E) (간선 목록에서 만든 인접 리스트) |
| `DetectCycleBFS` | 5 | O(V + E)  (girth 는 모든 루트에서 BFS 하므로 O(V · (V + E))) | O(V + E) |
| `DetectCycleUnionFind` | 5 | O(E α(V)) | O(V) |
| `IsTree` | 5 | 판정 (a)~(c) 는 O(V + E), (d) 는 O(E·(V + E)), (e) 는 최악 지수 시간 — (d)·(e) 는 교차 검증용 오라클일 뿐이다 | O(V + E) |
| `IsForest` | 5 | O(V + E α(V)) | O(V) |
| `IsBiconnected` | 5 | O(V + E) | O(V) |
| `KahnAlgorithm` | 6 | O(V + E)  (최소 힙 변형은 O((V + E) log V)) | O(V + E) |
| `DFSBasedTopologicalSort` | 6 | O(V + E) | O(V) |
| `LongestPathInDAG` | 6 | O(V + E) | O(V + E) |
| `Kruskal` | 7 | O(E log E)  (정렬이 지배, 서로소 집합은 E α(V)) | O(V + E) |
| `Prim` | 7 | O(E log V)  (밀집 구현은 O(V²)) | O(V + E) |
| `Boruvka` | 7 | O(E log V) | O(V + E) |
| `ReverseDelete` | 7 | O(E (V + E)) | O(V + E) |
| `MinimumSpanningTree` | 7 | Kruskal O(E log E), Prim O(E log V), Borůvka O(E log V) | O(V + E) |
| `MakeSet` | 8 | O(1) 평균 (키 사전 조회), 일괄 초기화 O(n) | O(n) |
| `FindSet` | 8 | 압축 없음 O(경로 길이), 압축/반감/분할은 분할상환 O(log n) (랭크 합치기와 함께면 O(α(n))) | O(1) 추가 공간 (반복 구현) |
| `UnionSet` | 8 | 분할상환 O(α(n)) | O(n) |
| `UnionByRank` | 8 | find O(log n) (압축 없을 때), 합치기 O(log n) | O(n) |
| `PathCompression` | 8 | 분할상환 O(α(n)) (랭크 합치기와 함께), 압축만으로는 O(log n) | O(n) |
| `Dijkstra` | 9 | O(E log V) | O(V + E) |
| `BellmanFord` | 9 | O(V · E) | O(V + E) |
| `FloydWarshall` | 9 | O(V³) | O(V²) |
| `Johnson` | 9 | O(V·E + V·E log V) = O(V·E log V) | O(V²) (결과 행렬) |
| `SPFA` | 9 | O(k·E) 평균, O(V·E) 최악 | O(V + E) |
| `DialAlgorithm` | 9 | O(E + V·C) — 간선 한 번씩 + 버킷 훑기(최대 거리 <= V·C) | O(V + E + C) |
| `AStar` | 10 | O((V + E) log V) 이하 (좋은 휴리스틱에서 확장 수가 크게 줄어듦) | O(V) |
| `JumpPointSearch` | 10 | 최악 O(V) 이지만 열린 공간에서 A* 의 수분의 1~수십분의 1 확장 (점프마다 직선 스캔) | O(점프 포인트 수) |
| `GreedyBestFirstSearch` | 10 | O(V log V) (닫힌 집합으로 정점마다 한 번만 확장; 닫힌 집합이 없는 트리 탐색이라면 최악 O(b^m)), 좋은 휴리스틱에서는 훨씬 적게 확장 | O(V) |
| `BidirectionalSearch` | 10 | O(b^(d/2)) vs O(b^d) for unidirectional | O(b^(d/2)) |
| `IDDFS` | 10 | O(b^d) | O(d) |
| `IDAStar` | 10 | O(b^d) (휴리스틱이 좋을수록 지수의 밑이 작아진다) | O(d) |
| `ThetaStar` | 10 | A* 와 같고 이웃마다 시선 검사 O(경로 길이) | O(V) |
| `FordFulkerson` | 11 | O(E · f) (f = 최대 유량, 정수 용량), 경로 선택 규칙이 정해지지 않으면 유사 다항 시간 | O(V + E) |
| `EdmondsKarp` | 11 | O(V E²) (증가 O(VE) 번 × BFS O(E)) | O(V + E) |
| `Dinic` | 11 | O(V² E), 단위 용량 이분 그래프 O(E √V) | O(V + E) |
| `PushRelabel` | 11 | FIFO 선택 O(V³), 최고 높이 우선 선택 O(V² √E) | O(V + E) |
| `MinCostMaxFlow` | 11 | O(F · SPFA) 또는 O(F · E log V) (F = 총 유량) | O(V + E) |
| `BipartiteMatching` | 12 | O(V · E) | O(V + E) |
| `HungarianAlgorithm` | 12 | O(n² m) | O(n m) (입력 표 포함, 알고리즘 자체는 O(n + m)) |
| `HopcroftKarp` | 12 | O(E √V) | O(V + E) |
| `BlossomAlgorithm` | 12 | O(V³) (최대 V/2 번의 증가 경로 탐색, 각각 O(V²) 이하) — 고급 구현은 O(√V · E) | O(V + E) |
| `Tarjan` | 13 | O(V + E) | O(V) |
| `Kosaraju` | 13 | O(V + E) | O(V + E) |
| `Gabow` | 13 | O(V + E) | O(V) (스택 S, B, 호출 스택) |
| `EulerTour` | 13 | O(V + E) | O(V + E) |
| `HeavyLightDecomposition` | 13 | 전처리 O(N), 경로 질의·갱신 O(log² N) | O(N) |
| `CentroidDecomposition` | 13 | 구성 O(N log N), 표시·질의 O(log N) | O(N log N) |
| `BipartiteGraph` | 14 | O(V + E)  (서로소 집합 판정은 O(E α(V))) | O(V + E) |
| `DirectedGraph` | 14 | 간선 추가 O(1), 뒤집기 O(V + E), 행렬 곱 O(n³) | O(V + E) |
| `UndirectedGraph` | 14 | 간선 추가 O(1), 연결 요소 O(V + E) | O(V + E) |
| `WeightedGraph` | 14 | Dijkstra O(E log V), Bellman-Ford O(V·E), Floyd–Warshall O(V³) | O(V + E) |
| `UnweightedGraph` | 14 | BFS O(V + E) | O(V) |
| `CompleteGraph` | 14 | 신장 트리 개수 O(n³) (행렬식), 열거는 지수 | O(n²) |
| `SparseGraph` | 14 | 인접 리스트 순회 O(V + E), 인접 행렬 순회 O(V²) | 인접 리스트 O(V + E), 인접 행렬 O(V²) |
| `DenseGraph` | 14 | 삼각형 O(V²·V/64), 전이적 폐쇄 O(V³/64) | O(V²/64) 워드 |
| `PlanarGraph` | 14 | 필요조건 검사 O(1), 완전한 평면성 판정 O(V) | O(1) |
| `Multigraph` | 14 | 판정 O(V + E), 오일러 경로 O(V + E) | O(V + E) |
| `Hypergraph` | 14 | 2-section 변환 O(Σ\|e\|²) | O(V·E) 연관 행렬 |
| `RandomGraph` | 15 | 생성 O(n²) | O(n) |
| `GridGraph` | 15 | BFS O(R·C) | O(R·C) |
| `TreeGraph` | 15 | 프뤼퍼 복호화 O(n log n) | O(n) |
| `HypercubeGraph` | 15 | BFS O(d·2^d) | O(2^d) |
| `ScaleFreeGraph` | 15 | 기대 O(n·m²) (뽑을 때마다 중복 대상 검사 O(m), 기대 O(m) 번 뽑음) | O(n·m) |
| `SmallWorldGraph` | 15 | 평균 경로 O(n·(n + E)) | O(n·k) |
| `DependencyGraph` | 16 | 순서·단계·증분 O(V + E), 축약 O(E · V / 64) | O(V + E) (축약은 O(V²/64) 비트) |
| `KnowledgeGraph` | 16 | 색인 질의 O(결과), 닫힘 O(V·\|facts\|), 규칙 고정점 O(반복 횟수 · \|facts\|) | O(\|facts\|) (색인 두 벌) |
| `SocialNetworkGraph` | 16 | 추천 O(Σ 친구의 차수 · log V), 경로 O((V + E) log V), 삼각형 O(d² · log V) — 이름이 길이 L 인 문자열이면 비교마다 O(L) 이 더 붙는다 (map/set<s | O(V + E) |
| `CallGraph` | 16 | O(V + E) | O(V + E) |
| `StateTransitionGraph` | 16 | 도달성·교착 O(S + T), Moore 최소화 O(k · n² )(최악), Hopcroft 는 O(k · n log n) | O(S + T) |
| `ControlFlowGraph` | 16 | 블록 구성 O(명령 수), 반복 지배자 O(블록 수² · 반복) — Lengauer-Tarjan 은 O(E α) | O(블록 수) |
| `DataFlowGraph` | 16 | 고정점까지 O(블록 수 · 변수 수 · 반복 횟수)  (비트마스크로 집합 연산 O(1)) | O(블록 수 · 변수 수) |
| `BayesianNetwork` | 16 | 열거 O(2^n), 변수 제거 O(n · 2^w) (w = 제거 순서가 만든 최대 범위 크기) | O(2^w) |
| `NeuralGraph` | 16 | 순전파·역전파 모두 O(연산 수) — 입력이 n 개인 스칼라 출력의 전체 기울기가 순방향 모드는 O(n · 연산 수), 역방향 모드는 O(연산 수) 한 번 | O(연산 수) |
| `PageRank` | 16 | O(iter · (V + E)), iter ≈ log ε / log d | O(V + E) |
| `BFS vs DFS` | 0 | BFS, DFS 모두 O(V + E) | BFS O(가장 넓은 층), DFS O(가장 깊은 경로) |
| `DAG가 중요한 이유` | 0 | 위상 정렬 O(V + E), DAG 위의 DP O(V + E), 비트셋 폐쇄 O(V·E/64) | O(V + E) |
| `Prim vs Kruskal` | 0 | Kruskal O(E log E), Prim 이진 힙 O(E log V), Prim 배열 O(V²) | O(V + E) |
| `Dijkstra vs A*` | 0 | Dijkstra O(E log V), A* 는 휴리스틱에 따라 훨씬 적은 확장 (일관적이면 Dijkstra 이하) | O(V) |
| `Union-Find 시간복잡도` | 0 | m 번의 연산에 O(m · α(n)) (랭크 + 경로 압축), 압축만: O(m log n), 랭크만: find 당 O(log n) | O(n) |

## Hash

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateHashTable` | 1 | O(m)  (버킷 m개 초기화, 소수 찾기 O(√m) 반복) | O(m) |
| `Insert` | 1 | 평균 O(1 + α), 최악 O(n) | O(n + m)  (항목 n 개 + 미리 잡아 둔 버킷 m 개) |
| `Search` | 1 | 평균 O(1 + α), 최악 O(n) | O(1) |
| `Delete` | 1 | 평균 O(1 + α), 최악 O(n) | O(1) |
| `Resize` | 1 | 삽입 분할상환 O(1), 확장 1회는 O(n) | O(n) |
| `Rehash` | 1 | 한꺼번에 O(n), 점진적이면 연산당 O(최대 사슬 길이) | O(n) (점진적일 때 재해시 중에는 두 테이블) |
| `LoadFactor` | 1 | 평균 탐색 O(1) 은 α 가 상수일 때만 — 선형 탐사의 실패 탐색은 ½(1 + 1/(1−α)²) 라 α → 1 이면 폭발하고 최악은 O(n); 이 시뮬레이션은 α 마다 O(m + 시도 수 · 평 | O(m) (시뮬레이션 표; 이론식 자체는 O(1)) |
| `DivisionMethod` | 2 | O(1) | O(1) |
| `MultiplicationMethod` | 2 | O(1) | O(1) |
| `UniversalHashing` | 2 | O(1) | O(1) |
| `FNV` | 2 | O(len) | O(1) |
| `MurmurHash` | 2 | O(len) | O(1) |
| `xxHash` | 2 | O(len) | O(1)  (스트리밍 상태 48 바이트) |
| `SipHash` | 2 | O(len) | O(1) |
| `Chaining` | 3 | 평균 O(1 + α), 최악 O(n) | O(n + m) |
| `OpenAddressing` | 3 | 평균 탐사 수 선형 ½(1+1/(1-α)) 성공 / ½(1+1/(1-α)²) 실패, 이차·이중 해싱은 실패 ≈ 1/(1-α); 최악 O(m) | O(m) |
| `LinearProbing` | 3 | 성공 탐색 ≈ ½(1 + 1/(1−α)), 실패 탐색 ≈ ½(1 + 1/(1−α)²), 최악 O(n) (키가 한 클러스터에 몰릴 때) | O(m) |
| `QuadraticProbing` | 3 | 평균 O(1/(1−α)), 군집은 선형 탐사보다 완화 | O(m) |
| `DoubleHashing` | 3 | 평균 O(1/(1−α)) (1차·2차 군집 없음) | O(m) |
| `RobinHoodHashing` | 3 | 평균 O(1), 탐색 실패 시 조기 종료 | O(m) |
| `CuckooHashing` | 3 | 탐색 O(1) 최악, 삽입 분할상환 O(1) | O(n)  (적재율 약 50% 이하에서 안정) |
| `HopscotchHashing` | 3 | 탐색 O(H), 삽입 평균 O(1) | O(m) |
| `CoalescedHashing` | 3 | 평균 O(1), 병합된 체인 길이에 비례 | O(m) |
| `PerfectHash` | 4 | 탐색 O(1) 최악, 구성 기대 O(n) | O(n) |
| `MinimalPerfectHash` | 4 | 탐색 O(len), 구성 기대 O(n) | O(n)  (키당 약 수 비트의 변위 배열) |
| `PolynomialRollingHash` | 5 | 전처리 O(n), 부분 문자열 해시 O(1) | O(n) |
| `RabinFingerprint` | 5 | 슬라이드 1회 O(1) | O(256) |
| `LongestCommonSubstringHash` | 5 | O((n + m) log min(n, m)) | O(n + m) |
| `HashMap` | 6 | 평균 O(1), 확장은 분할상환 | O(n) |
| `LinkedHashMap` | 6 | put/get/erase 평균 O(1) | O(n) |
| `Multimap` | 6 | insert 분할상환 O(1), erase(key) O(값 개수) | O(n) |
| `BiMap` | 6 | put·forcePut·조회·삭제 기대 O(1) (선형 탐사, 적재율 <= 1/2) | O(n) — 해시 표 두 개 (항목당 키·값을 두 번 저장) |
| `ConsistentHashing` | 7 | 조회 O(log N) | O(N) |
| `VirtualNode` | 7 | 조회 O(log(N·V)), 노드 추가·제거 O(V log(N·V)) | O(N·V) |
| `RendezvousHash` | 7 | 조회 O(N) | O(N) |
| `Chord` | 7 | 조회 O(log N) 홉 | 노드당 O(log N) finger |
| `Kademlia` | 7 | 조회 O(log N) 라운드 | 노드당 O(K log N) |
| `Consistent Hashing이 분산 시스템에서 중요한 이유` | 7 | 링 조회 O(log(N·V)), 랑데부 O(N), 모듈로 O(1) | O(N·V) |
| `MD5` | 8 | O(len) | O(1)  (스트리밍 상태 64 바이트 버퍼) |
| `SHA256` | 8 | O(len) | O(1)  (스트리밍 상태 64 바이트 버퍼) |
| `HMAC` | 8 | O(len) | O(len) |
| `MerkleDamgard` | 8 | O(len) | O(len) |
| `암호학적 해시와 일반 해시의 차이` | 8 | SHA-256 O(n), 충돌 탐색 O(2^(b/2)), 원상 탐색 O(2^b) (b = 자른 비트 수) | O(2^(b/2)) (충돌 탐색의 표) |
| `HashIndex` | 9 | 등치 조회 기대 O(1) 페이지, 범위 조회 O(전체 페이지) (정렬 인덱스는 O(log n + 결과/페이지)) | O(n / PAGE) 페이지 |
| `HashJoin` | 9 | O(n + m + 결과) (Grace: 디스크 I/O 약 3(n + m), 한 키가 M 보다 많으면 블록 중첩 루프로 O(n·m/M)) | O(작은 쪽 테이블) (Grace 는 O(M) 튜플) |
| `ExtendibleHashing` | 9 | 조회 O(1) (디렉터리 1회 + 버킷 1회) | O(n + 2^전역깊이) |
| `LinearHashing` | 9 | 조회 O(1) 평균, 분할 1회 O(버킷 크기) | O(n) |
| `왜 Java HashMap은 TreeBin으로 바뀌는가?` | 10 | 리스트 bin O(n), 트리 bin O(log n) | O(n) |
| `Python dict의 구현 원리` | 10 | 평균 O(1) | O(n)  (indices 는 int 배열이라 entries 대비 작다) |
| `C++ unordered_map의 구조` | 10 | 평균 O(1) | O(n)  (요소마다 노드 할당) |
| `Redis Dictionary 구조` | 10 | 연산당 O(1) + 재해시 1버킷 분할상환 | 재해시 중 최대 두 테이블 |
| `LRUCache` | 10 | get/put/erase O(1) 기대, 스택 거리 오라클은 O(n log n) | O(capacity) |
| `LFUCache` | 10 | get/put O(1) | O(capacity) |
| `HashDoS` | 11 | 공격 시 삽입 n 개 O(n²), 키 있는 해시 O(n) 기대, 트리화 O(n log n) | O(n) |
| `Salting` | 11 | O(반복 횟수)  (비용을 의도적으로 키움) | O(1) |
| `ConcurrentHashMap` | 12 | 평균 O(1) (서로 다른 구역은 병렬, 같은 구역의 읽기도 병렬), snapshot 은 O(n) 에 전 구역 잠금 | O(n) |
| `LockFreeHashTable` | 12 | 평균 O(1), 락 없이 진행 보장(lock-free) | O(고정 용량) |
| `BloomFilter` | 13 | add / mayContain O(k), 합집합 O(m/64) | O(m) 비트 |
| `CountMinSketch` | 13 | add / estimate O(d), 합치기 O(d·w) | O(d·w) = O((1/ε)·ln(1/δ)) |
| `Bloom Filter는 왜 오탐(False Positive)만 발생하는가?` | 13 | add / has / remove O(k), 열거 검증 O(3^U · U) | O(m) |
| `LocalitySensitiveHashing` | 14 | 서명 O(\|문서\|·H), 후보 탐색 평균 O(n) | O(n·H) |
| `SimHash` | 14 | 지문 O(단어 수 · 64), 색인 질의 기대 O(k · log N + 후보 수) | O(N · (k + 1)) (색인), 지문은 문서당 8 바이트 |
| `MinHash` | 14 | 서명 O(\|S\|·K), 비교 O(K), bottom-k 는 O(\|S\| log k) | O(K) (b-비트 MinHash 는 K·b 비트) |
| `SemanticHashing` | 14 | 인코딩 O(B·D), 비교 O(B/64) (비트 연산) | O(B·D) 초평면 |
| `SwissTable` | 15 | 평균 O(1), 그룹 단위 병렬 비교 | O(n)  (슬롯당 제어 바이트 1개) |
| `LearnedHash` | 15 | 조회 O(log S) (S = 표본 수, 균등 분할 표를 쓰면 O(1)), 학습 O(n) | O(n / step) |
| `CollisionVisualization` | 16 | DP O(n·m), 분포 측정 O(n) | O(m) |
| `BucketDistribution` | 16 | O(n + m) | O(m) |
| `ProbeSequence` | 16 | 탐사열 생성 O(m), 평균 탐사 수 선형 ½(1+1/(1−α)²) / 이중 1/(1−α) | O(m) |
| `ResizeAnimation` | 16 | 확장 1회 O(n), 삽입당 분할상환 O(1) (×2 정책) | O(n) |
| `ChainGrowth` | 16 | O(n) | O(m) |
| `ClusterFormation` | 16 | O(n · 평균 탐사) | O(m) |
| `AvalancheEffect` | 16 | O(표본 · 32 · 32) | O(1) (격자 32×32) |
| `HashQualityEvaluation` | 16 | O(패턴 수 · n + 표본 · 32 · 32) | O(2^16) |
| `CacheLocality` | 16 | O(n · 평균 탐사) | O(m) |
| `MemoryLayout` | 16 | O(1) | O(1) |

## List

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateList` | 1 | 배열 생성 O(N), 연결 리스트 꼬리 포인터 O(N) (끝까지 걷기는 O(N²)) | O(N) |
| `Traverse` | 1 | O(N) | 전방 O(1), 재귀·스택 후방 O(N) |
| `Search` | 1 | O(N) (평균 (N+1)/2 번 비교) | O(1) |
| `Insert` | 1 | 배열 O(N) (이동), 연결 리스트 O(pos) (걷기) + O(1) (연결) | O(1) |
| `Delete` | 1 | 위치 삭제 배열 O(N)·연결 리스트 O(pos), 값 전부 삭제 O(N) | O(1) |
| `Update` | 1 | 배열 O(1), 연결 리스트 O(pos), 일괄 갱신 O(N) | O(1) |
| `Reverse` | 1 | O(N) | 배열·반복 O(1), 재귀 O(N) |
| `Copy` | 1 | 얕은 복사 O(1), 깊은 복사 O(N) | 깊은 복사 O(N) (임의 포인터 복사는 대응표 방식 추가 O(N), 끼워 넣기 방식 추가 O(1)) |
| `Swap` | 1 | 배열 O(1), 연결 리스트 O(max(i, j)) (걷기), 리스트 전체 교환 O(1) | O(1) |
| `Clear` | 1 | O(N) (소멸자·해제 각 한 번) | O(1) |
| `DynamicArray` | 2 | 접근 O(1), push_back 분할상환 O(1) (최악 O(N)), pop_back O(1) | O(N) (용량은 길이의 2 배 이내) |
| `Resize` | 2 | resize 줄이기 O(줄인 수), 늘리기 O(N) (재할당 포함, 분할상환 O(추가 수)), reserve O(N) | O(용량) |
| `ShiftLeft` | 2 | O(N) | 논리 이동·저글링·뒤집기 O(1), 임시 버퍼 O(k) |
| `ShiftRight` | 2 | O(N) | O(1) |
| `InsertAt` | 2 | 단일 O(N−pos), 범위 삽입 O(N−pos+m), 순서 무관 삽입 O(1) | O(1) (범위 삽입은 임시 O(m)) |
| `DeleteAt` | 2 | 단일 O(N−pos), 구간 O(N−last), 순서 무관 O(1), 조건 삭제 O(N) | O(1) |
| `BinarySearch` | 2 | O(log N) | 반복 O(1), 재귀 O(log N) |
| `LowerBound` | 2 | O(log N) | O(1) |
| `UpperBound` | 2 | O(log N) | O(1) |
| `PushFront` | 3 | O(1) | O(1) (노드 하나) |
| `PushBack` | 3 | 꼬리 포인터 O(1), 꼬리 없음 O(N) | O(1) |
| `PopFront` | 3 | O(1) | O(1) |
| `PopBack` | 3 | 단방향 O(N), 양방향 O(1) | O(1) |
| `InsertAfter` | 3 | O(1) (노드를 이미 가지고 있을 때) | O(1) |
| `InsertBefore` | 3 | 단방향 걷기 O(N), 값 바꿔치기 O(1), 양방향 O(1) | O(1) |
| `RemoveNode` | 3 | 단방향 걷기 O(N), 다음 노드 복사 트릭 O(1), 양방향 O(1) | O(1) |
| `FindMiddle` | 3 | O(N) (한 번의 순회) | O(1) |
| `DetectCycle` | 3 | O(μ + λ) = O(N) | O(1) (해시 집합 방식은 O(N)) |
| `MergeLists` | 3 | 두 리스트 O(M+N), k 개 O(N log k) | 반복 O(1), 재귀 O(M+N), k 개 힙 O(k) |
| `SplitList` | 3 | 나누기 O(N) (걷기), 병합 정렬 O(N log N) | O(1) (병합 정렬은 재귀 O(log N)) |
| `BubbleSort` | 4 | 최악·평균 O(N²), 최선(조기 종료) O(N) | O(1) |
| `SelectionSort` | 4 | 비교 항상 O(N²), 교환 O(N) | O(1) |
| `InsertionSort` | 4 | 최악·평균 O(N²), 최선 O(N), 일반적으로 O(N + 역순쌍 수) | O(1) |
| `MergeSort` | 4 | O(N log N) (최선·평균·최악) | O(N) |
| `QuickSort` | 4 | 평균 O(N log N), 최악 O(N²) (인트로 정렬은 O(N log N) 보장) | O(log N) (작은 쪽 먼저 재귀) |
| `StablePartition` | 4 | 버퍼 방식 O(N), 제자리 방식 O(N log N), 호어(불안정) O(N) | 버퍼 O(N), 제자리 O(log N), 호어 O(1) |
| `TwoPointers` | 5 | O(N) (3Sum 은 O(N²)) | O(1) |
| `SlidingWindow` | 5 | O(N) (고정 윈도우는 O(N), 가변 윈도우는 포인터 이동 합 ≤ 2N) | O(1) ~ O(윈도우 안 서로 다른 값의 수) |
| `PrefixSum` | 5 | 구축 O(N), 질의 O(1), K 개수 세기 O(N) | O(N) |
| `DifferenceArray` | 5 | 갱신 O(1), 복원 O(N) | O(N) |
| `DummyNode` | 6 | O(N) (더미 노드는 O(1) 추가) | O(1) |
| `SentinelNode` | 6 | 삽입·삭제 O(1) (분기 없음), 센티넬 탐색 O(N) (비교 횟수 절반) | 센티넬 노드 1 개 추가 |
| `CircularList` | 6 | 삽입·삭제·회전·이어붙이기 O(1), 조제푸스 시뮬레이션 O(N·K) | O(1) |
| `DoublyLinkedList` | 6 | 핸들 기반 삽입·삭제·이동 O(1), 뒤집기 O(N) | 노드당 포인터 2 개 + 센티넬 1 개 |
| `XORLinkedList` | 6 | 순회 O(1)/단계, 위치 삽입·삭제 O(1) (커서가 있을 때), 뒤집기 O(1) | 노드당 포인터 크기 1 개 |
| `Iterator` | 7 | 증감·역참조 O(1), std::distance 는 양방향에서 O(N) | O(1) 반복자 |
| `Begin` | 7 | begin()·before_begin()·end() O(1), insert_after·erase_after O(1) (위치 반복자를 이미 가진 경우) | O(1) 반복자 |
| `End` | 7 | end() O(1), 검사 포함 증감·역참조 O(1) | O(1) 반복자 (센티넬 노드 1 개) |
| `Next` | 7 | 순방향·양방향 O(n), 임의 접근 O(1) | O(1) |
| `Prev` | 7 | 이중 연결 O(1), 단방향 O(N) | O(1) |
| `ShallowCopy` | 8 | 얕은 복사 O(1), 깊은 복사 O(N) | 얕은 복사 O(1), 깊은 복사 O(N) |
| `DeepCopy` | 8 | O(노드 수 + 간선 수) | O(노드 수) (대응표) |
| `Move` | 8 | 이동 O(1), 복사 O(N) | O(1) |
| `Alloc` | 8 | 할당·해제 O(1), 덩어리 확보 분할상환 O(1) | O(노드 수) (덩어리 단위) |
| `Free` | 8 | alloc·free 모두 O(1) | O(블록 수), 블록당 세대 번호·플래그 오버헤드 |
| `GarbageCollection` | 8 | 참조 계수 갱신 O(1), mark–sweep O(전체 객체 + 참조) | 참조 계수 O(1) 추가, mark–sweep O(표시 비트 + DFS 스택) |
| `Map` | 9 | O(N) (게으른 뷰는 읽는 만큼) | 즉시 맵 O(N) 새 셀, 게으른 뷰 O(1) |
| `Filter` | 9 | O(N) | 새 셀 O(통과한 앞부분), 공유 꼬리 O(1) |
| `Reduce` | 9 | O(N) | O(1) (쌍대 합은 재귀 O(log N)) |
| `Zip` | 9 | O(min(N, M)) (zipLongest 는 O(max(N, M))) | 즉시 zip O(min(N, M)), 게으른 zip O(1) |
| `Flatten` | 9 | O(전체 원소 수) | 한 단계 O(N), 반복 중첩 평탄화 O(깊이), 다층 연결 리스트 O(깊이) |
| `SkipList` | 10 | 탐색·삽입·삭제·순위·k 번째 기대 O(log N) | O(N) (노드당 평균 포인터 2 개) |
| `Rope` | 10 | 연결 O(1), 분할 O(깊이) | O(노드 수), 편집 후에도 원본 공유 |
| `UnrolledLinkedList` | 10 | 접근·삽입·삭제 O(N/B + B) | O(N), 노드 오버헤드 ≤ 2N/B 개 포인터 |
| `GapBuffer` | 10 | 커서 위치 삽입·삭제 O(1), 이동 O(거리) | O(N + 틈) |
| `PieceTable` | 10 | 삽입·삭제 O(조각 수), 텍스트 조립 O(길이) | 원본 + 추가 버퍼 + 조각 목록 |
| `FingerTree` | 10 | 양 끝 push/pop 분할상환 O(1) (concat·split 은 정본 참고) | O(N), 버전 사이에 구조 공유 |
| `PersistentList` | 10 | cons·tail O(1), setAt·at O(i), concat O(\|a\|) | 변경마다 새 노드 O(i) 만 추가 |
| `ImmutableList` | 10 | 접근·set·끝 추가·끝 삭제 O(log_W N) (W=32 에서 실질적 상수) | 수정당 새 노드 O(log_W N), 나머지는 이전 버전과 공유 |
| `ArrayList vs LinkedList` | 0 | 위치를 아는 삽입 — 배열 O(N), 연결 O(1) / 인덱스로 찾는 삽입 — 둘 다 O(N) / 임의 접근 — 배열 O(1), 연결 O(N) | 배열 O(N) (원소 크기), 연결 O(N) (원소 + 포인터 2 개) |
| `Cache Locality` | 0 | 시뮬레이션은 접근당 O(ways); 실제 순회의 점근 복잡도는 같아도 미스 수가 수십 배 차이 | O(캐시 크기) |
| `Amortized Analysis` | 0 | push_back 분할상환 O(1) (최악 한 번은 O(N)), 이진 카운터 증가 분할상환 O(1) | O(N) (용량은 크기의 최대 2 배) |
| `Iterator Invalidation` | 0 | 검사 반복자 역참조 O(1) (버전 비교 한 번) | 반복자당 추가 정수 하나 |
| `Memory Fragmentation` | 0 | 첫 적합 할당 O(빈 조각 수), 해제 O(log N), 압축 O(살아 있는 블록 수) (빈 조각은 살아 있는 블록 사이에만 있어 L+1 개 이하) | O(블록 수) 메타데이터 |
| `False Sharing` | 0 | 해당 없음 (캐시 일관성 비용 모델) | 변수당 캐시 라인 하나 (64 B) — 메모리를 써서 시간을 산다 |
| `Lock-Free Linked List` | 0 | 검색·삽입·삭제 O(N) (CAS 재시도는 경쟁에 비례) | O(고정 풀 크기) |
| `Concurrent List` | 0 | 조대 O(N) 직렬, 손잡이 교대 O(N) (노드마다 잠금), 게으른 O(N) 탐색 + 잠금 2 개 | O(N) (+ 폐기 목록) |
| `Copy-on-Write List` | 0 | 읽기(스냅샷) O(1), 쓰기 O(N) (전체 복사), 일괄 수정 O(N) / 변경 묶음 | O(N) × (동시에 살아 있는 스냅샷 수) |

## Memory

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateMemory` | 1 | 접근 O(n 바이트) | O(size) |
| `Alignment` | 1 | O(1) | O(1) |
| `Padding` | 1 | layout O(멤버 수), 최소 크기 탐색 O(멤버 수!) (검증용), 정렬 배치 O(m log m) | O(멤버 수) |
| `MemoryDump` | 1 | O(n) | O(n) |
| `TextSegment` | 2 | O(매핑 수) | O(매핑 수) |
| `DataSegment` | 2 | O(1) | bss 는 실행 파일 크기에 영향 없음 |
| `EnvironmentVariable` | 2 | getenv O(환경 변수 수) | O(환경 크기) |
| `CommandLineArgument` | 2 | O(인자 수) | O(인자 수) |
| `PushFrame` | 3 | O(1) | O(프레임 크기) |
| `PopFrame` | 3 | push/pop O(1), 백트레이스 O(깊이) | O(스택 크기) |
| `CallFunction` | 3 | 호출 하나당 상수 개의 명령, 전체는 호출 트리의 크기 | 4 · 재귀 깊이 칸 |
| `ReturnFunction` | 3 | O(1) (큰 구조체는 O(크기)) | O(1) |
| `LocalVariable` | 3 | O(1) 할당/해제 | O(스코프 깊이) |
| `StackFrame` | 3 | O(깊이) | O(깊이) 스택 |
| `StackOverflow` | 3 | O(깊이) | O(깊이) 스택 |
| `TailCallOptimization` | 3 | O(n) | 트램펄린 O(1), 일반 재귀 O(n) |
| `malloc` | 4 | 할당 O(블록 수) (first-fit), 해제 O(블록 수) (병합 포함) | 블록당 헤더 16B |
| `new` | 4 | 할당기에 따라 다름 (평균 O(1)) | O(n) |
| `PlacementNew` | 4 | 아레나 할당 O(1), 생성자 비용 별도 | O(1) 추가 할당 없음 (고정 버퍼) |
| `Pointer` | 5 | O(1) | O(1) |
| `Reference` | 5 | O(1) | O(1) |
| `SmartPointer` | 5 | unique_ptr O(1), shared_ptr 복사 O(1) (원자적 카운터) | shared_ptr 은 제어 블록 추가 |
| `Aliasing` | 5 | 비트 캐스트 O(1) (memcpy 가 한 명령으로 바뀐다), 기수 정렬 O(n), memmove O(n) | O(1) |
| `MemoryPool` | 6 | 할당 O(1) (덩어리가 필요하면 덩어리 크기), 해제 O(덩어리 수) (owns 검증 포함 — 검증을 빼면 O(1)) | O(블록 크기 · 개수) |
| `ObjectPool` | 6 | acquire O(1) 평균(덩어리 증설 시 O(덩어리 크기)), release O(덩어리 수) (소유 확인 포함) | O(최대 동시 객체 수) |
| `FreeList` | 6 | 벡터 구현 할당 O(구멍 수)·해제 O(구멍 수), 인덱스 구현 best/worst-fit 할당 O(log 구멍 수)·해제 O(log 구멍 수) (first-fit 은 선형) | O(구멍 수) |
| `SlabAllocator` | 6 | 할당·해제 O(1) (슬랩 머리말은 주소 마스크로 찾고, 리스트 이동은 이중 연결 리스트) | O(슬랩 수 · 4096) |
| `BuddyAllocator` | 6 | 할당·해제 O(차수) = O(log N) (집합 연산 포함 O(log N · log 블록 수)) | O(블록 수) |
| `ArenaAllocator` | 6 | 할당 O(1) (덩어리 증설 시 O(덩어리 크기)), rollback/reset O(되돌릴 객체 수 + 덩어리 수) | O(용량) |
| `MarkSweep` | 7 | 마크 O(살아있는 객체와 참조), 스윕 O(힙 전체), 할당 O(자유 블록 수) | O(깊이) 마크 스택 (포인터 역전 표시는 O(1)) |
| `MarkCompact` | 7 | O(힙 크기) · 4 패스 (표시 + 주소 계산 + 갱신 + 이동), 두 손가락은 표시 뒤 O(셀 수) 한 번 | O(1) 추가 (forwarding 주소는 객체 헤더에 저장) + 표시 스택 최악 O(살아 있는 객체 수) (푸시할 때 표시하므로 한 객체는 한 번만 들어간다) |
| `CopyingGC` | 7 | O(살아있는 객체) (쓰레기는 방문하지 않는다; 디버그용 poison 채우기만 O(힙)), 할당 O(1) | O(힙) · 2 (두 공간), 큐/스택 없이 scan 포인터 하나로 BFS |
| `GenerationalGC` | 7 | minor GC 는 살아있는 young + 기억 집합(또는 더러운 카드)에 비례, major GC 는 살아있는 전체 | O(기억 집합) 또는 O(카드 수) |
| `ReferenceCountingGC` | 7 | decref 연쇄 해제 O(해제되는 객체), 순환 수집 O(객체 + 참조) | 객체당 카운터 하나 |
| `IncrementalGC` | 7 | 조각당 O(예산), 한 사이클 O(힙), 장벽 O(1) | O(회색 작업 목록) |
| `ConcurrentGC` | 7 | O(스냅샷 크기 + 장벽 기록 수) | O(SATB 큐) |
| `CacheLine` | 8 | O(1) 주소 분해 | O(1) |
| `CacheHit` | 8 | 접근 O(ways) | O(캐시 라인 수) |
| `CacheMiss` | 8 | 시뮬레이션 O(접근 수 · 방향 수), 스택 거리 O(n log n) (Fenwick) | O(캐시 라인 수) |
| `CacheFriendlyTraversal` | 8 | O(N²) 접근, 미스 수가 다르다 | O(1) |
| `CacheBlocking` | 8 | O(N³) 연산은 동일, 캐시 미스는 O(N³/ (B·L)) 로 감소 | O(1) |
| `FalseSharing` | 8 | O(iters) | 패딩으로 캐시 라인 하나씩 낭비 |
| `VirtualAddress` | 9 | O(1) | O(1) |
| `PhysicalAddress` | 9 | alloc O(프레임 수 / 64) (비트맵 워드 단위 건너뛰기), 연속 할당 O(프레임 수 · 크기), 해제 O(1) | O(프레임 수) |
| `AddressTranslation` | 9 | TLB 적중 O(방향 수), 미스 O(1) (한 단계 테이블) | O(페이지 수 + TLB 항목 수) |
| `Paging` | 9 | 시뮬레이션 O(트레이스 길이 · 프레임 수) (LRU 리스트 구현은 O(1)/접근) | O(프레임 수) |
| `PageTable` | 9 | map/unmap/walk 모두 O(4) = O(1) (레벨 수), 메모리 접근은 레벨 수만큼 | O(사용 중인 구간에 필요한 테이블 수) — 희소한 주소 공간에서 한 장짜리 배열(512GB)보다 훨씬 작다 |
| `PageFault` | 9 | FIFO/LRU O(n · 프레임), OPT O(n² · 프레임) (비교용) | O(프레임) |
| `TLBLookup` | 9 | 조회 O(1) | O(TLB 항목 수) |
| `MemoryMapping` | 9 | 매핑 O(1), 쪽 접근은 처음 만질 때 폴트 한 번 | 만진 쪽 수만큼 물리 메모리 |
| `ReadOnlyMemory` | 10 | O(1) | O(1) |
| `ExecuteOnlyMemory` | 10 | 코드 생성 O(길이), 호출 O(1) | O(페이지) |
| `MemoryProtection` | 10 | O(1) | 가드 페이지 1개 (4KB) |
| `StackCanary` | 10 | O(1) 검사 | 프레임당 8바이트 |
| `ASLR` | 10 | O(1) (모형의 한 번 뽑기) | O(1) |
| `DEP` | 10 | O(1) | O(1) |
| `AtomicOperation` | 11 | O(1) 연산 (경합 시 캐시 라인 이동 비용) | O(1) |
| `CompareAndSwap` | 11 | 루프당 O(1), 경합 시 재시도 | O(N) 노드 풀 + O(1) 카운터 |
| `MemoryBarrier` | 11 | 모형 열거는 상태 수에 비례 (작은 리트머스 테스트), 실제 실행 O(N) | O(N + 상태 수) |
| `AcquireRelease` | 11 | 모형 열거는 상태 수에 비례, 실제 실행 O(N) | O(N) |
| `SequentialConsistency` | 11 | 모형 열거는 상태 수에 비례, 실제 실행 O(N) | O(N) |
| `MemoryLeak` | 12 | O(1) 추적 (목록 보고는 O(할당 수)) | O(1) 카운터, 상세 추적은 O(할당 수) |
| `DanglingPointer` | 12 | 접근 O(1) + 세대 검사 | 슬롯당 세대 카운터 |
| `WildPointer` | 12 | 검사 O(log N) | O(할당 수) |
| `DoubleFree` | 12 | O(log 블록 수) | O(블록 수) |
| `UseAfterFree` | 12 | 할당·해제·접근 O(1) | O(힙 크기 + Q) |
| `BufferOverflow` | 12 | 접근 검사 O(접근 크기), 할당·해제 O(1) (격리 큐 제외) | 힙 크기 / 8 (그림자) + 할당당 2 · 레드존 |
| `HeapCorruption` | 12 | 할당 O(1), 검증 O(블록 수) | 블록당 헤더 12B + 푸터 4B (16B 정렬) |
| `MemoryMappedFile` | 13 | 접근 시 페이지 폴트 O(1) (캐시에 있으면 복사 없음), 증설은 재매핑 O(1) + 새 페이지만 폴트 | 페이지 캐시 공유 |
| `SharedMemory` | 13 | 접근 O(1), 동기화는 프로세스 수에 비례한 경쟁 | 공유 영역 1벌 (프로세스 수와 무관) |
| `CopyOnWrite` | 13 | 복사 O(1), 첫 쓰기 O(크기) | 쓰기가 일어나기 전까지 공유 |
| `ZeroCopy` | 13 | O(n) 이동, 사용자 공간 복사 0 | O(1) 사용자 버퍼 |
| `ProcessMemory` | 14 | O(영역 수) | O(영역 수) |
| `ThreadLocalStorage` | 14 | 접근 O(1) (세그먼트 레지스터 기준 오프셋; 동적 키는 벡터 색인) | 스레드 수 · 변수 크기 |
| `KernelMemory` | 14 | O(1) 주소 검증 | O(1) |
| `UserMemory` | 14 | 매핑·해제 O(1), 만진 페이지는 페이지당 O(1) 결함 | 예약은 무료, 만진 페이지(RSS)만 비용 |
| `NUMAMemory` | 14 | O(접근 기록 + 페이지 × 노드²) | O(페이지 × 노드) |
| `GPUMemory` | 15 | O(32) (워프 한 번) | O(1) |
| `UnifiedMemory` | 15 | 접근당 O(1) (검증 오라클은 O(n²)) | O(페이지 수) |
| `PersistentMemory` | 15 | 검증 O(단계 · 2^dirty) | O(1) 로그 |
| `HugePage` | 15 | TLB 적중 O(log 항목) (시뮬레이션), 압축 O(프레임 수) | O(항목 수), 페이지 테이블 O(매핑 크기 / 4KB · 8B) |
| `RDMA` | 15 | 연산당 O(1) 검사 (NIC 가 처리), 시뮬레이션은 사건 수 · log | 등록한 영역 크기 |
| `MemoryCompression` | 15 | 압축 O(n · 창 크기), 복원 O(n) | O(n) |
| `GarbageFirstGC` | 16 | 수집 O(CSet 생존 객체 + 기억 집합 항목), 선택 O(R log R) | O(영역 수 + 기억 집합) |
| `ZGC` | 16 | 로드 장벽 빠른 경로 O(1) 비교, 느린 경로 O(1) 조회(+재배치 시 객체 복사), 정지 시간은 루트 수에 비례 | 포인터 상위 비트 + 페이지별 전달 표 (다음 표시가 끝나면 해제) |
| `ShenandoahGC` | 16 | 접근마다 포인터 한 번 더 (간접 참조 비용), 쓰기는 수집 집합 객체에 처음 쓸 때 복사 O(객체 크기) | 객체당 포인터 하나 (+ 이동 중에는 옛 사본과 새 사본) |
| `RegionBasedMemory` | 16 | 할당 O(1), 닫기 O(등록된 소멸자 + 덩어리 수) | O(요청 합 + 덩어리 내부 조각) |
| `EscapeAnalysis` | 16 | 고정점 반복 O(반복 · 문장 수 · site 수) | O(변수 · site 수) |
| `OwnershipTypeSystem` | 16 | O(1) 런타임 검사, 정적 검사기 O(문장 수² · 참조 수) (설명용) | O(1) / O(변수 수) |
| `PersistentHeap` | 16 | 삽입·삭제·조회 기대 O(log N) 시간과 O(log N) 새 노드 | 버전마다 O(log N) 추가 (공유) |
| `TransactionalMemory` | 16 | 읽기 O(1) (+ 쓰기 집합 조회), 커밋 O(쓰기 집합 · log + 읽기 집합) | 트랜잭션당 O(읽기 집합 + 쓰기 집합), 변수당 한 워드(버전 + 잠금 비트) |
| `CapabilityPointer` | 16 | O(1) 검사 (하드웨어) | 포인터당 base·length·perms 추가 (CHERI 는 128비트 포인터 + 태그 1비트) |
| `CHERIArchitecture` | 16 | 저장·읽기 O(1), 회수 훑기 O(메모리 / 16) | 16바이트당 태그 1비트 (약 0.8%) |
| `MemoryTagging` | 16 | O(1) 검사 (걸친 칸 수) | 16바이트당 4비트 (3%) |
| `HardwareMemorySafety` | 16 | O(1) 판정 | O(1) |
| `Stack vs Heap` | 0 | 스택 할당·해제 O(1), 힙 first-fit 은 블록 수에 비례 | 스택은 제한적(MB), 힙은 큼 |
| `Pointer vs Reference` | 0 | O(1) 접근, 포인터 산술 O(1) | 포인터 8B, 참조는 구현 의존(보통 포인터 하나) |
| `malloc vs new` | 0 | 할당기에 따라 다름 | O(n) |
| `free vs delete` | 0 | delete 는 소멸자 비용 포함 | O(1) |
| `Shared Pointer의 순환 참조` | 0 | O(1) | 누수 시 영구 점유 |
| `왜 캐시 미스가 성능을 떨어뜨리는가?` | 0 | O(1) 공식, 시뮬레이션 O(접근 수 · 방향 수) | O(캐시 라인 수) |
| `페이지 교체 알고리즘(LRU, Clock)` | 0 | LRU 접근당 O(1) (리스트 + 해시), Clock 은 분할상환 O(1) 이고 적중 때 순서 변경이 없다 | O(프레임 수) |
| `Virtual Memory가 필요한 이유` | 0 | 접근 O(1) (적중), 폴트 O(프레임 수) (Clock) | O(프로세스 수 · 가상 페이지 수 + 스왑 크기) |
| `메모리 단편화(Fragmentation)` | 0 | 압축 O(N), 할당 O(구멍 수) | O(N) |
| `False Sharing이란?` | 0 | 분석 O(이벤트 수 × 라인당 조각 수) | 패딩만큼 증가 |
| `NUMA 구조 이해하기` | 0 | BFS O(n(n+간선)), 분배 전수 O(5^n) | O(n²) |
| `C, C++, Java, Python의 메모리 관리 비교` | 0 | O(V + E) | O(V) |
| `JVM 메모리 구조` | 0 | minor GC 는 Young 크기에 비례 | O(힙) |
| `CPython 객체 모델` | 0 | append 분할상환 O(1), 참조 횟수 갱신 O(1), 순환 수집 O(컨테이너 수 + 참조 수) | 용량이 길이보다 약 12.5% 크다, 객체당 머리말 16바이트 |
| `Rust Ownership와 Borrow Checker` | 0 | 데이터 흐름 O(노드 수 · 변수 수), 경로 열거는 O(2^분기 수 · 문장 수) | O(노드 수 · 변수 수) |
| `CUDA 메모리 계층` | 0 | 시뮬레이션 O(사이클 × 워프) | O(워프 수 + 타일) |
| `현대 CPU 캐시 계층(L1/L2/L3)` | 0 | O(접근 수 · 단계 수 · ways) | O(캐시 크기) |

## PathFinding

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateMap` | 1 | O(행 × 열) | O(행 × 열) |
| `CreateGrid` | 1 | 이웃 생성 O(1) | O(1) (격자 자체 O(행 × 열)) |
| `CreateNode` | 1 | 노드 생성·비교 O(1) | O(1) 노드당 |
| `CreateEdge` | 1 | 간선 추가 O(1), 중복 제거 O(E log E), CSR 변환 O(V + E) | O(V + E) |
| `BuildGraph` | 1 | O(행 × 열 × 이웃 수) | O(V + E) |
| `InitializeSearch` | 1 | 초기화 O(1), 질의는 방문한 칸 수 비례 | O(V) |
| `IsReachable` | 1 | BFS 질의 O(V+E), 요소 전처리 후 질의 O(α(V)) | O(V) |
| `ReconstructPath` | 1 | O(경로 길이) | O(경로 길이) |
| `BreadthFirstSearch` | 2 | O(V + E) | O(V) |
| `DepthFirstSearch` | 2 | O(V + E) | O(V) |
| `IterativeDeepeningDFS` | 2 | O(b^d) (b/(b-1) 배의 중복 포함) | O(d) |
| `BidirectionalSearch` | 2 | O(b^(d/2)) × 2 | O(b^(d/2)) |
| `MultiSourceBFS` | 2 | O(V + E) | O(V) |
| `Dijkstra` | 3 | O(E log V) | O(V) |
| `BellmanFord` | 3 | O(V · E) | O(V) |
| `SPFA` | 3 | 평균 O(k·E), 최악 O(V·E) | O(V) |
| `FloydWarshall` | 3 | O(V³) | O(V²) |
| `Johnson` | 3 | O(V·E log V) | O(V²) (결과 행렬) |
| `GreedyBestFirstSearch` | 4 | O(V log V) (닫힌 집합으로 칸마다 한 번만 확장; 닫힌 집합이 없는 트리 탐색이라면 최악 O(b^m)), 좋은 휴리스틱에서는 훨씬 적게 확장 | O(V) |
| `AStar` | 4 | 최악 O(b^d), 좋은 휴리스틱에서는 O(경로 주변) | O(탐색한 노드 수) |
| `WeightedAStar` | 4 | w 가 클수록 빠름, 최악 O(b^d) | O(탐색한 노드 수) |
| `IDAStar` | 4 | O(b^d) (휴리스틱이 좋을수록 지수의 밑이 작아진다) | O(d) |
| `BeamSearch` | 4 | O(깊이 × k × b log (k b)) | O(k × 깊이) (방문 표를 쓰면 O(V)) |
| `JumpPointSearch` | 5 | 최악 O(V) 이지만 열린 공간에서 A* 의 수분의 1~수십분의 1 확장 (점프마다 직선 스캔) | O(점프 포인트 수) |
| `ThetaStar` | 5 | A* 와 같고 이웃마다 시선 검사 O(경로 길이) | O(V) |
| `LazyThetaStar` | 5 | 시선 검사 횟수 = 확장한 노드 수 (세타* 는 생성한 노드 수) | O(V) |
| `AnyAngleSearch` | 5 | 평활화 O(경로² × 시선 비용), 가시성 그래프 구성 O(정점² × 장애물) | O(정점) |
| `HierarchicalPathFinding` | 5 | 전처리 O(클러스터 수 × 입구² × K²), 질의 O(추상 그래프 탐색 + 구간별 정밀화) | O(입구 수²) 추상 간선 |
| `DStar` | 6 | O(영향받은 부분 트리 × log) 갱신 / 전체 재계산 O(V log V) | O(V) |
| `DStarLite` | 6 | 첫 계획 O(V log V), 이후 갱신은 변한 간선의 영향 범위에 비례 | O(V) |
| `LifelongPlanningAStar` | 6 | 첫 탐색 O(V log V), 이후 변화는 영향받은 칸 수에 비례 | O(V) |
| `DynamicReplanning` | 6 | 재계획 1회당 O(V log V) × 재계획 횟수 | O(V) |
| `KShortestPaths` | 7 | O(K · m log(K · m)) | O(K · m) |
| `YenAlgorithm` | 7 | O(K · V · (E + V log V)) | O(K · V) |
| `EppsteinAlgorithm` | 7 | O(E + V log V + K log K) | O(E + K) |
| `AlternativeRoute` | 7 | O(반복 횟수 × E log V) | O(V + E) |
| `UniformCostSearch` | 8 | O((b^(C*/ε)) log) — 최적 비용 C* 안쪽 상태를 모두 확장 (암시적 그래프) | O(확장 상태 수) |
| `MinCostPath` | 8 | DP O(RC), Dijkstra O(RC log RC) | O(RC) |
| `ResourceConstrainedPath` | 8 | O(T · E) 층 DP (의사 다항), 라벨 설정은 최악 지수 | O(T · V) |
| `TimeDependentShortestPath` | 8 | O((V + E) log V) (FIFO) — 시간 확장 그래프는 O(T · (V + E)) | O(V + E · H) |
| `CooperativeAStar` | 9 | O(에이전트 수 × (V · T) log) — 에이전트마다 시공간 A* | O(V · T) |
| `ConflictBasedSearch` | 9 | 최악 지수(제약 트리), 실전에서는 충돌 수에 따라 증가 | O(제약 트리 노드 × 에이전트 × 경로 길이) |
| `MultiAgentPathFinding` | 9 | 우선순위 계획 O(A · V · T), 결합 정확 탐색 O((V · 5)^A) — 에이전트 수에 지수 | O(V · T) / 결합 상태 O(V^A) |
| `ReservationTable` | 9 | 예약/조회 O(1) 평균(해시), 안전 구간 생성 O(T), SIPP O(안전 구간 수 × log) | O(예약 수) |
| `NavigationMesh` | 10 | 삼각형 그래프 탐색 O(T log T) + 깔때기 O(포털 수 × 꺾임 수) — 꺾을 때마다 그 꼭짓점 다음 포털부터 다시 훑으므로 최악 O(포털 수²), 보통은 거의 선형 | O(T) |
| `WaypointGraph` | 10 | 전처리 O(웨이포인트² × 시선 검사), 질의 O(W log W + W × 시선 검사) | O(W + 간선) |
| `VisibilityGraph` | 10 | 순진한 구성 O(n³), 회전 스위프 O(n² log n); Dijkstra O(E log V) | O(n²) |
| `VoronoiDiagram` | 10 | O(RC) 거리장·스켈레톤, 질의 O(RC) BFS | O(RC) |
| `RoadNetwork` | 10 | CSR 순회 O(deg), 간선 기반 탐색 O(E · deg · log E), 색인 질의 O(주변 칸 × 간선) | O(V + E) |
| `RapidlyExploringRandomTree` | 11 | 반복당 O(노드 수) 최근접 탐색(k-d 트리로 O(log n)) + 충돌 검사 | O(노드 수) |
| `RRTStar` | 11 | 반복당 O(n) (k-d 트리 + 반경 질의로 O(log n)), 총 O(n log n) | O(n) |
| `ProbabilisticRoadMap` | 11 | 전처리 O(N² + N·k·충돌 검사), 질의 O(N log N) | O(N·k) |
| `PotentialField` | 11 | APF 한 걸음 O(장애물 수), NF1 O(격자 칸 수) | O(1) / O(격자 칸 수) |
| `DynamicWindowApproach` | 11 | 제어 주기당 O(속도 샘플 수 × 예측 길이 × 장애물 수) | O(1) |
| `HybridAStar` | 12 | O(상태 격자 수 × 조향 수 × 충돌 검사) | O(상태 격자 수) |
| `FrenetPlanner` | 12 | O(후보 수 × 시간 격자 × 장애물 수) | O(1) (후보를 하나씩 평가) |
| `LatticePlanner` | 12 | O((W² · 헤딩 수 · 기본형 수) log) | O(W² · 헤딩 수) |
| `MotionPlanning` | 12 | C-공간 구성 O(M² · 장애물), 탐색 O(M² · 8) | O(M²) |
| `TrajectoryOptimization` | 12 | 반복당 O(n · 장애물 수) × 반복 수 | O(n) |
| `DistanceVectorRouting` | 13 | 라운드당 O(V² · deg), 수렴까지 최대 V − 1 라운드 | O(V²) |
| `LinkStateRouting` | 13 | 플러딩 O(LSA 수 · 링크 수), SPF O(E log V) 라우터마다 | O(라우터 수 · 링크 수) (각 라우터가 LSDB 보유) |
| `OSPF` | 13 | SPF O(E log V), ECMP 경로 수 O(E) | O(V + E) |
| `RIP` | 13 | 라운드당 O(V² · deg), 수렴은 최대 16 라운드 근처 | O(V²) |
| `BGPPathSelection` | 13 | 선택 O(경로 수 × 단계 수), SPVP 한 라운드 O(노드 × 선호 경로 수) | O(경로 수) |
| `MazeSolver` | 14 | DFS/BFS O(V + E), 오른손 규칙 O(V) 걸음 | O(V) |
| `PuzzleSolver` | 14 | IDA* 최악 O(b^d), 휴리스틱이 강할수록 지수의 밑이 작아짐 | O(d) (경로 길이) |
| `GPSNavigation` | 14 | Viterbi O(T · E · deg), 재탐색 O(E log V) | O(T · E) |
| `RobotVacuumPlanner` | 14 | O(미청소 구간 전환 횟수 × V) (BFS 되돌아가기) | O(V) |
| `GameNPCNavigation` | 14 | 흐름 장 O(V) 한 번, NPC 한 걸음 O(8) | O(V) |
| `WarehouseRobotRouting` | 14 | BFS k 번 O(k · V), Held–Karp O(2^k · k²), NN O(k²), 2-opt 반복당 O(k²) × 비용 계산 | O(2^k · k) |
| `DronePathPlanning` | 14 | O(V · 26 · 이동 검사) A*, 줄 당기기 O(경로 길이² · 시선 검사) | O(V) |
| `EmergencyEvacuation` | 14 | 시간 확장 그래프 O(R · C · T) 노드, T 마다 최대 유량 | O(R · C · T) |
| `HeuristicFunction` | 15 | A* O(확장 수 log) — 휴리스틱이 강할수록 확장 수 감소 | O(V) |
| `PriorityQueueOptimization` | 15 | 이진 힙 O((V + E) log V), d-진 힙 O(E log_d V + V d log_d V), Dial O(E + V·C), 기수 힙 O(E + V log C) | O(V + E) (Dial 은 C 칸의 버킷) |
| `LandmarkHeuristic` | 15 | 전처리 O(k · E log V), 질의 A* 확장 수에 비례(h 계산 O(k)) | O(k · V) |
| `ContractionHierarchy` | 15 | 전처리 O(V · 증인 탐색), 질의 O(상향 탐색 공간 크기 × log) — 도로망에서 수백 정점 | O(V + 지름길 수) |
| `TransitNodeRouting` | 15 | 질의 O(\|A(s)\| · \|A(t)\|) 표 조회 + 국지 탐색; 전처리는 CH + k² 거리표 | O(k² + V · 접근 노드 수) |
| `ReachBasedRouting` | 15 | reach 계산 O(V · (E log V)), 질의 양방향 Dijkstra + 가지치기 | O(V) |
| `ALTAlgorithm` | 15 | 전처리 O(k · E log V), 질의는 줄어든 비용 위의 양방향 Dijkstra | O(k · V) |
| `AnytimeAStar` | 16 | ε 단계마다 가중 A* 한 번 — 단계별 확장 수는 ε 가 작을수록 증가 | O(V) |
| `AnytimeRepairingAStar` | 16 | 단계별 확장은 이전 g 값 재사용으로 감소; 최악은 재시작과 같음 | O(V) |
| `MonteCarloTreeSearch` | 16 | 반복당 O(트리 깊이 + rollout 길이) | O(반복 수) (트리 노드) |
| `ReinforcementLearningPathPlanning` | 16 | 에피소드 수 × 에피소드 길이 (갱신 O(1)) | O(상태 수 × 행동 수) |
| `NeuralPathPlanning` | 16 | 학습 반복당 O(샘플 수 × 입력 × 은닉), 추론 O(입력 × 은닉) | O(파라미터 수) |
| `DifferentiableAStar` | 16 | 순전파·역전파 O(K · V · 5) | O(K · V) (softmax 비중 저장) |
| `SwarmPathPlanning` | 16 | 시간 단계당 O(N² + N · 장애물 수) | O(N) |
| `AntColonyOptimization` | 16 | 반복 수 × 개미 수 × 경로 길이 × 차수 | O(E) (페로몬 표) |
| `GeneticPathPlanning` | 16 | 세대 수 × 인구 × 경유점 수 × 장애물 수 | O(인구 × 경유점 수) |
| `ParticleSwarmOptimization` | 16 | 반복 수 × 입자 수 × (차원 + 적합도 평가) | O(입자 수 × 차원) |
| `QuantumPathFinding` | 16 | 시뮬레이션은 반복당 O(N) × O(√(N/M)) 반복 (실제 양자 기계에서는 오라클 O(√(N/M)) 호출) | O(N) (상태 벡터 시뮬레이션) |
| `BFS vs Dijkstra` | 0 | BFS O(V + E), Dijkstra O((V + E) log V), 0-1 BFS O(V + E) | O(V) |
| `Dijkstra vs A*` | 0 | Dijkstra O((V + E) log V), A* 는 휴리스틱에 따라 확장 수가 줄어듦(일관적이면 최악도 Dijkstra 이하) | O(V) |
| `A*의 휴리스틱은 왜 최적해를 보장하는가?` | 0 | 불변식 검사는 설명용(반복당 O(V)); A* 자체는 휴리스틱에 따라 다름 | O(V) |
| `Manhattan Distance vs Euclidean Distance` | 0 | 거리 계산 O(1) | O(1) |
| `Chebyshev Distance와 8방향 이동` | 0 | BFS/Dijkstra O(V), 경로 수 DP O(dx · dy) | O(V) |
| `Grid Map vs Navigation Mesh` | 0 | 분해 O(R·C), 메시 A* O(N log N) (N = 직사각형 수 ≪ 칸 수) | O(R·C) 분해 / O(N + 간선) 메시 |
| `Static Map vs Dynamic Map` | 0 | 재계산 O(k · E log V), 질의는 ALT A* | O(k · V) |
| `단일 출발점 vs 다중 출발점` | 0 | 다중 출발 O((V + E) log V) 한 번, 단일 출발 k 번은 k 배 | O(V) |
| `경로 계획(Path Planning)과 궤적 계획(Trajectory Planning)의 차이` | 0 | 표본 수 n = 길이/ds 에 대해 O(n) | O(n) |
| `게임 엔진(Unity, Unreal)의 길찾기 구조` | 0 | 굽기 O(R·C·주변 칸), 질의 A* + 줄 당기기, 이동은 프레임당 O(남은 경로 선분 수) 검사 | O(R·C) |
| `ROS에서의 경로 계획` | 0 | 팽창 O(R·C·반경²), 전역 계획 Dijkstra O(V log V), 추종은 O(스텝) | O(R·C) |
| `Google Maps와 차량 내비게이션의 경로 탐색 개요` | 0 | 맞춤 O(삼각형 수), 질의 O(상향 탐색 공간), 구조 전처리는 가중치와 무관하게 한 번 | O(간선 + 채움 간선) |

## Queue

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateQueue` | 1 | 연결 큐 O(1), 배열 큐 할당 1 회 | 배열 O(용량), 연결 O(1) (원소 수에 비례해 증가) |
| `Enqueue` | 1 | 고정 O(1), 동적 분할상환 O(1) (최악 O(N)), 연결 O(1) | O(N) (동적은 용량이 크기의 최대 2 배) |
| `Dequeue` | 1 | O(1) | O(1) |
| `Front` | 1 | O(1) | O(1) |
| `Rear` | 1 | O(1) (연결 큐는 rear 포인터가 있을 때) | O(1) |
| `Peek` | 1 | O(1) | O(1) |
| `IsEmpty` | 1 | O(1) | O(1) |
| `IsFull` | 1 | O(1) | O(1) |
| `Size` | 1 | O(1) | O(1) |
| `Clear` | 1 | 원소 소멸자 호출 O(N) (trivially destructible 이면 O(1)) | O(1) |
| `LinearQueue` | 2 | enqueue·dequeue O(1), 당기기 방식은 최악 O(N) | O(N) |
| `CircularQueue` | 2 | enqueue·dequeue O(1) | O(N) |
| `Resize` | 2 | resize O(크기), enqueue·dequeue 분할상환 O(1) | O(용량) |
| `Rotate` | 2 | 큐로 회전 O(k), 가득 찬 원형 배열에서는 O(1) | O(1) 추가 |
| `LinkedQueue` | 3 | enqueue·dequeue·front·back O(1), splice O(1), 복사·소멸 O(N) | O(N) (노드당 포인터 하나 추가) |
| `EnqueueNode` | 3 | O(1) | O(1) per node |
| `DequeueNode` | 3 | O(1) | O(1) |
| `Deque` | 4 | 양 끝 연산·임의 접근 O(1) (분할상환) | O(N) |
| `PushFront` | 4 | 분할상환 O(1) | O(N) |
| `PushBack` | 4 | 분할상환 O(1) | O(N) |
| `PopFront` | 4 | 분할상환 O(1) | O(N), 용량은 크기의 4 배 이하 |
| `PopBack` | 4 | O(1) | O(1) |
| `PriorityQueue` | 5 | push·pop O(log N), top O(1) | O(N) |
| `PushHeap` | 5 | O(log N) 최악, 무작위 입력에서만 평균 O(1) 비교 (오름차순 입력은 매번 O(log N)) | O(1) 추가 |
| `PopHeap` | 5 | O(log N) (클래식 최대 2 log N 비교, bottom-up 평균 ≈ log N) | O(1) 추가 |
| `Heapify` | 5 | O(log N) (노드의 높이에 비례) | O(1) |
| `BuildHeap` | 5 | Floyd O(N), 반복 push O(N log N) | O(1) 추가 |
| `HeapSort` | 5 | O(N log N) (최악 포함), top-k 는 O(N log k) | O(1) 추가 (제자리) |
| `CalendarQueue` | 5 | 평균 O(1) (사건이 칸에 고르게 퍼질 때), 최악 O(n) (한 칸에 몰릴 때), 칸 수 조정은 분할상환 O(1) | O(n + 칸 수) |
| `RadixHeap` | 5 | push O(1), pop 분할상환 O(log C) (원소 하나는 버킷을 아래로만 옮겨 최대 65 번), 다익스트라 O(E + V log C) | O(n + 65) |
| `BreadthFirstSearch` | 6 | O(V + E) | O(V) |
| `LevelOrderTraversal` | 6 | O(N) | O(최대 너비) |
| `ShortestPath` | 6 | BFS O(V + E), 0-1 BFS O(V + E) | O(V) |
| `FloodFill` | 6 | O(R·C) | O(R·C) (큐 최대 크기는 영역의 둘레) |
| `MultiSourceBFS` | 6 | O(R·C) (출발점 개수와 무관) | O(R·C) |
| `SlidingWindowMaximum` | 7 | 덱 O(N), 블록 분할 O(N), 멀티셋 O(N log k) | O(k) (블록 분할은 O(N)) |
| `MonotonicQueue` | 7 | push·pop·max 분할상환 O(1) | O(N) |
| `WindowMinimum` | 7 | O(N) | O(k) 또는 O(N) |
| `JobQueue` | 8 | submit·next·cancel 모두 O(1) | O(대기 작업 수) |
| `ReadyQueue` | 8 | FCFS·RR 선택 O(1), SJF·우선순위 선택 O(log N) | O(N) |
| `WaitingQueue` | 8 | P·V O(1) | O(대기 프로세스 수) |
| `TimingWheel` | 8 | 등록·취소 O(1), 틱 하나 O(만료되거나 cascade 되는 타이머 수) — 타이머당 많아야 층 수만큼 이동 | O(활성 타이머 + 칸 수 256 + 취소됐지만 아직 칸에 남은 항목) |
| `MessageQueue` | 8 | send·receive O(log P) (P = 서로 다른 우선순위 수) | O(메시지 수) |
| `PacketQueue` | 9 | 슬롯당 O(1) | O(K) |
| `ProducerConsumer` | 9 | put·take 각 O(1) (대기 제외), 모델 검사 O(상태 수 × 프로세스 수) | O(용량) (모델 검사는 O(상태 수)) |
| `RingBuffer` | 9 | write·read O(n) 바이트 복사 (memcpy 최대 2 번), 카운터 연산 O(1) | O(용량) |
| `CircularBuffer` | 9 | push·pop_front·접근 O(1), linearize O(N) | O(용량) |
| `LockFreeQueue` | 10 | push·pop 분할상환 O(1) (경쟁이 없을 때 CAS 1 번) | O(용량) |
| `MichaelScottQueue` | 10 | enqueue·dequeue 분할상환 O(1) (락프리: 경쟁에서 재시도 가능) | O(풀 크기) |
| `WorkStealingQueue` | 10 | push·pop O(1) (성장은 분할상환 O(1)), steal O(1) (CAS 재시도 가능) | O(N) (옛 배열 보관분 합계도 O(N)) |
| `ConcurrentQueue` | 10 | push·pop O(1) (뮤텍스 경쟁 시 대기) | O(용량) |
| `PersistentQueue` | 11 | snoc·tail·head 최악 O(1) (영속 사용에서도) | O(N) |
| `ImmutableQueue` | 11 | push O(1), head O(1), pop 분할상환 O(1) (이어 쓸 때만; 같은 버전 반복 사용은 최악 O(N)) | O(N), 새 버전은 O(1) 노드를 만들고 나머지는 공유 |
| `QueueingTheory` | 11 | 시뮬레이션 사건당 O(log c), 이론식 O(c) 또는 O(K) | O(c + 대기열 길이) |
| `FairQueue` | 11 | 양자 ≥ 최대 패킷 크기이면 enqueue·dequeue 패킷당 O(1) | O(흐름 수 + 대기 패킷 수) |
| `PriorityScheduling` | 11 | 일당 O(log N) (에이징 키가 불변이라 재정렬 없음) | O(N) |

## Set

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateSet` | 1 | O(N) (N 개 원소, 기대) | O(N) |
| `Add` | 1 | 분할상환 O(1) (최악 O(N)) | O(N) |
| `Remove` | 1 | O(1) 기대 (되밀기는 군집 길이만큼) | O(1) |
| `Contains` | 1 | 기대 O(1) (부하율 ≤ 1/2), 최악 O(N) | O(1) |
| `Clear` | 1 | 채우기 O(용량), 세대 번호 O(1) | O(용량) |
| `Size` | 1 | 크기 조회 O(1) (순회로 세면 O(N)) | O(1) |
| `IsEmpty` | 1 | O(1) (비트 집합은 최악 O(워드 수)) | O(1) |
| `Copy` | 1 | 표 복제 O(용량), 재삽입 O(N), 쓰기 시 복사 O(1) (쓰기 때 O(용량)) | O(N) |
| `Union` | 2 | 병합 O(\|A\| + \|B\|), 해시 기대 O(\|A\| + \|B\|) (테스트용 출력 정렬은 제외), 비트 O(U/64), k 개 O(N log k) | O(\|A\| + \|B\|) |
| `union() (Python Style)` | 2 | - | - |
| `Intersection` | 0 | 병합 O(\|A\| + \|B\|), 해시 O(min) 기대, 지수 탐색 O(\|A\| log(\|B\|/\|A\|)) | O(min(\|A\|, \|B\|)) |
| `Difference` | 0 | 병합 O(\|A\| + \|B\|), 해시 기대 O(\|A\| + \|B\|), 비트 O(U/64) | O(\|A\| + \|B\|) |
| `SymmetricDifference` | 0 | 병합 O(\|A\| + \|B\|), 비트 O(U/64) | O(\|A\| + \|B\|) |
| `Complement` | 0 | 비트 O(U/64), 정렬 배열 O(\|U\|) | O(U/64) |
| `CartesianProduct` | 0 | 생성 O(\|A\|·\|B\|), 번호로 접근 O(1) | 저장하면 O(\|A\|·\|B\|), 게으른 접근 O(1) |
| `PowerSet` | 0 | O(2ⁿ · n) | 열거 O(n) (모두 저장하면 O(2ⁿ · n)) |
| `IsSubset` | 3 | 병합 O(\|A\| + \|B\|), 해시 기대 O(\|A\| + \|B\|) (B 의 해시가 이미 있으면 O(\|A\|)), 비트 O(U/64) | O(1) (해시 방식은 O(\|B\|)) |
| `IsProperSubset` | 3 | 부분집합 검사 + O(1) 크기 비교 | O(1) |
| `IsSuperset` | 3 | 병합식 O(\|A\| + \|B\|), 해시식 O(\|B\|) 기대 | O(1) 추가 공간 |
| `IsDisjoint` | 3 | 병합 O(\|A\| + \|B\|) (조기 종료), 해시 기대 O(\|A\| + \|B\|) (큰 쪽의 해시가 이미 있으면 O(min)), 비트 O(U/64) | O(1) (해시 방식은 O(\|큰 쪽\|)) |
| `Equals` | 3 | 정렬 비교 O(N), 해시 O(N) 기대, 지문 비교 O(1) (지문 계산은 O(N)) | O(1) (해시 방식은 O(N)) |
| `Iterator` | 4 | begin 과 ++ 한 번은 최악 O(용량) (해시: 빈 슬롯을 건너뜀), 전체 순회 O(용량) (해시) 또는 O(N) (트리) | O(1) 반복자 |
| `ForEach` | 4 | O(용량) (해시) / O(N) (트리) | O(1) |
| `Find` | 4 | 해시 기대 O(1), 트리 O(log N), 정렬 배열 O(log N), find_if O(N) | O(1) |
| `Filter` | 4 | 필터링 O(N) (해시: O(용량)) | O(N) (새 집합) / O(걸러낼 원소 수) (모았다 지우기) |
| `Map` | 4 | 변환 O(N) (결과 삽입 포함), 정렬이면 O(N log N) | O(N) |
| `Reduce` | 4 | 접기 O(N), 점증 유지 갱신당 O(1) | O(1) |
| `ArraySet` | 5 | 조회 O(log N), 삽입·삭제 O(N), 순위·select O(log N)/O(1), 집합 연산 O(N + M) | O(N) 연속 |
| `LinkedSet` | 5 | 조회/삽입/삭제 O(n), 집합 연산 O(n + m) | O(n) (노드당 포인터 1개) |
| `HashSet` | 5 | 기대 O(1) (부하율 ≤ 1), 최악 O(N) | O(N + 버킷 수) |
| `TreeSet` | 5 | 조회·삽입·삭제·순위·select 모두 O(log N) | O(N) |
| `Multiset` | 5 | insert·erase·count·rank·kth·bounds O(log d) (d: 서로 다른 값의 수, 기대), 다중집합 연산 O(d log d) | O(d) — 같은 값은 노드 하나에 개수로 저장 |
| `BitSet` | 5 | 원소 접근 O(1), 집합 연산·count O(N/64), 순회 O(N/64 + 원소 수) | N/8 바이트 |
| `ImmutableSet` | 5 | 조회·삽입·삭제 기대 O(log N) | 갱신당 새 노드 O(log N), 나머지는 이전 버전과 공유 |
| `SetBit` | 6 | O(1) | O(1) |
| `ClearBit` | 6 | O(1) (켜진 비트 순회는 O(popcount)) | O(1) |
| `ToggleBit` | 6 | O(1) | O(1) |
| `TestBit` | 6 | O(1) | O(1) |
| `CountBits` | 6 | 커니핸 O(popcount), 표 조회·SWAR·하드웨어 O(1) | O(1) (표 방식 256 칸) |
| `EnumerateSubsets` | 6 | 부분마스크 열거 O(2^popcount), 모든 마스크에 대해 O(3ⁿ), 고스퍼 O(C(n, k)) | O(1) (열거 중) |
| `MakeSet` | 7 | O(1) (원소당) | O(N) |
| `FindSet` | 7 | 분할상환 O(α(N)) (경로 압축 + 크기 기준 합치기) | O(N) |
| `UnionSet` | 7 | 분할상환 O(α(N)) | O(N) |
| `UnionByRank` | 7 | find O(log n) (압축 없을 때), 합치기 O(log n) | O(n) |
| `PathCompression` | 7 | 단독 사용 시 분할상환 O(log n), 랭크와 함께면 O(α(n)) | O(n) |
| `ConnectedComponents` | 7 | O((n + m) α(n)) | O(n) |
| `Combination` | 8 | 열거 분할상환 O(1)/조합 (k ≤ n/2), C(n,k) 계산 O(min(k, n−k)), rank/unrank O(n) | O(k) |
| `Permutation` | 8 | 열거 O(n·n!), 순위/역순위 O(n²) | O(n) |
| `CombinationWithReplacement` | 8 | 다음 조합 구하기 O(k), 전체 O(C(n+k-1, k) · k) | O(k) |
| `NextPermutation` | 8 | 호출당 O(n) (평균 O(1)), 전체 순열 열거 O(n!) | O(1) |
| `GrayCode` | 8 | g(i) 계산 O(1), 역변환 O(log n) 또는 O(n) | O(1) |
| `Backtracking` | 9 | 최악 O(2ⁿ), 가지치기로 실제 방문은 크게 줄어듦 | O(n) (재귀 깊이) |
| `BitMaskEnumeration` | 9 | 전체 O(2ⁿ), 부분마스크 전체 O(3ⁿ), k-부분집합 O(C(n,k)) | O(1) |
| `MeetInTheMiddle` | 9 | O(2^(n/2) · n) | O(2^(n/2)) |
| `SubsetSum` | 9 | O(n · T / 64) 가능성, O(n · T) 개수 세기 | O(T) |
| `KnapsackSubset` | 9 | O(n · W) (DP), 복원 O(n), 비트 집합 DP O(n · W / 64) | O(n · W) (복원 포함), 값만 구하면 O(W) |
| `DancingLinks` | 9 | 최악 지수, 열 선택 휴리스틱(S 최소)으로 실전에서 매우 빠름 | O(1 의 개수) (노드 수) |
| `BinaryRelation` | 10 | 합성/추이 닫힘 O(n³), 성질 검사 O(n²)~O(n³) | O(n²) |
| `EquivalenceRelation` | 10 | 동치 판정 O(n³), 서로소 집합으로 닫힘 O(m α(n)) | O(n²) 행렬 / O(n) 서로소 집합 |
| `Partition` | 10 | 열거 O(B(n) · n) | O(n) (재귀) / 결과 저장 시 O(B(n) · n) |
| `EquivalenceClass` | 10 | O((n + m) α(n)) 로 모든 동치류 계산 | O(n) |
| `QuotientSet` | 10 | 몫집합 구성 O(n α(n)), 잘 정의됨 검사 O(n²) (또는 류별 O(n)) | O(n) |
| `Distinct` | 11 | 해시 O(n) 기대, 정렬/트리 O(n log n) | O(고유 행 수) |
| `Projection` | 11 | 사영 O(n), 중복 제거 포함 O(n) 기대(해시) 또는 O(n log n) | O(결과 크기) |
| `Selection` | 11 | 스캔 O(n), 정렬 인덱스 범위 O(log n + k) | O(결과 크기) |
| `Join` | 11 | 중첩 루프 O(\|R\|\|S\|), 해시 조인 O(\|R\| + \|S\| + 출력) 기대, 병합 조인 O(n log n + 출력) | 해시 조인 O(\|S\|), 병합 조인 정렬 복사본 O(\|R\| + \|S\|) |
| `GroupBy` | 11 | 해시 집계 기대 O(n) (이 코드는 결과를 키 순서 std::map 으로 옮겨 O(g log g) 가 더해짐, g = 그룹 수), 정렬 집계 O(n log n) | O(그룹 수) |
| `DuplicateElimination` | 11 | 해시 O(n), 정렬 O(n log n), 블룸 앞단 + 정확 집합 O(n) 기대 | O(고유 수) (정확 집합), 블룸 앞단은 고정 비트 수 |
| `InvertedIndex` | 12 | 질의 O(포스팅 길이의 합) (정렬 병합) | O(총 단어 출현 수) |
| `PostingList` | 12 | 교집합 O(m log(n/m)) (갤로핑), 인코딩/디코딩 O(n) | O(n) (압축 시 항목당 ~1~2 바이트) |
| `JaccardSimilarity` | 12 | 정렬된 집합 O(\|A\| + \|B\|), 해시 O(min(\|A\|,\|B\|)) 기대, 표본 추정 O(k) | O(1) 추가 |
| `MinHash` | 12 | 서명 O(\|S\| · k), 비교 O(k) | O(k) 서명 |
| `LocalitySensitiveHashing` | 12 | 서명 O(N · \|S\| · k), 밴딩 O(N · b), 후보 비교는 버킷 크기에 비례 | O(N · k) |
| `LabelSet` | 13 | 샘플당 O(1) 비트 연산(레이블 ≤ 64), 마이크로/매크로 집계 O(n · L) | O(n) (샘플당 64비트) |
| `FeatureSet` | 13 | 탐욕 O(k · n · 평가), 느린 탐욕은 평가 횟수가 크게 줄어듦 | O(n) |
| `VocabularySet` | 13 | 어휘 구성 O(N log N), 인코딩 O(토큰 수) 해시 조회 | O(V) |
| `CandidateSet` | 13 | 합집합 O(Σ\|Cᵢ\|) (해시) 또는 O(Σ\|Cᵢ\| log), 필터 O(\|C\|), 랭킹 O(N · 모델 비용) | O(\|C\|) |
| `ConstraintSet` | 13 | AC-3 O(e · d³), 탐색은 최악 지수 | O(n · d) |
| `BloomFilter` | 14 | 삽입·조회 O(k) | O(m) 비트 (원소당 약 10~15 비트로 ε ≈ 1% 이하) |
| `CountingBloomFilter` | 14 | 삽입·삭제·조회 O(k) | O(m · 카운터 비트 수) |
| `CuckooFilter` | 14 | 조회·삭제 O(1) (버킷 2개), 삽입 분할상환 O(1) | 키당 f / 적재율 비트 |
| `QuotientFilter` | 14 | 삽입·조회 O(log 런 길이) (이 개념 모델), 실제 몫 필터는 클러스터 길이에 비례하는 O(1) 기대 | 원소당 r 비트 + 메타데이터(실제 구현은 r + 3 비트), 이 모델은 벡터 오버헤드가 추가 |
| `ConcurrentSet` | 15 | 연산 O(log n) + 잠금 대기 | O(n) |
| `LockFreeSet` | 15 | 연산 O(n) (연결 리스트 탐색), 경합 시 CAS 재시도 | O(n) + 폐기 목록(소멸 시까지 유지) |
| `SkipListSet` | 15 | 탐색·삽입·삭제 기대 O(log n), 최악 O(n) | O(n) (노드당 평균 포인터 2개) |
| `ConcurrentHashSet` | 15 | 연산 기대 O(1) + 스트라이프 잠금, resize 는 O(n) (전체 잠금) | O(n) |
| `PersistentSet` | 16 | 조회·삽입·삭제 기대 O(log n) | 버전당 기대 O(log n) 새 노드 |
| `ImmutableBitSet` | 16 | test O(1), rank O(1), select O(log(U/64)), 변경·집합 연산 O(U/64) | O(U/8) 바이트 (+ 접두사 합) |
| `CompressedBitSet` | 16 | 연산 O(두 압축열의 런 수) (채움 대 리터럴은 워드 단위로 진행하지만 리터럴 런이 한 워드씩이라 이 합을 넘지 않음), 압축 O(워드 수) | O(런 수) |
| `RoaringBitmap` | 16 | contains O(log 청크 수 + log 4096), 합·교집합 O(공통 청크 수 · 컨테이너 연산) | 청크당 min(2·원소 수, 8192) 바이트 |
| `SuccinctSet` | 16 | access O(1) 분할상환(표본 + 워드 훑기), 조회 O(log n) | n(2 + log₂(U/n)) 비트 + select 표본 |
| `LearnedSetIndex` | 16 | 조회 O(1) 예측 + O(log ε) 구간 이분 탐색 | O(세그먼트 수) 모델 (키 배열 제외) |
| `DynamicConnectivity` | 16 | O(m log T log n) (m: 간선 구간 수) | O(m log T) (시간 트리에 걸린 간선) + O(n) 서로소 집합 |
| `Set vs List` | 0 | 리스트 조회 O(n), 정렬 리스트 O(log n), 해시 집합 O(1) 기대, 트리 집합 O(log n) | 모두 O(n) (집합은 노드/버킷 오버헤드가 큼) |
| `Set vs Multiset` | 0 | 연산 O(서로 다른 원소 수 log) (map 기반) | O(서로 다른 원소 수) |
| `HashSet vs TreeSet` | 0 | 해시 O(1) 기대 / O(n) 최악, 트리 O(log n) 보장 | O(n) |
| `BitSet은 언제 사용하는가?` | 0 | 합·교·차 O(U/64), 원소 수 O(U/64) (popcount), 단일 비트 접근 O(1) | U/8 바이트 |
| `Union-Find가 거의 O(1)인 이유` | 0 | m 번 연산 O(m α(n)) (분할상환) | O(n) |
| `집합과 그래프의 연결` | 0 | Warshall O(n³), 정점마다 BFS O(n(n + e)) | O(n²) |
| `집합과 관계(Relation)` | 0 | O(2^(n²) · n²) 완전 열거 | O(n) |
| `집합과 함수(Function)` | 0 | 함수 전수 열거 O(m^n · n) | O(n) |
| `SQL은 왜 집합 이론 위에서 동작하는가?` | 0 | 관계 대수 연산 자체는 설명용 (질의 최적화기는 비용 기반 탐색) | O(릴레이션 크기) |
| `AI에서 Label Set과 Vocabulary Set의 의미` | 0 | BPE 학습 O(병합 수 × 코퍼스 크기), 인코딩 O(병합 수 × 단어 길이) | O(어휘 크기 · 임베딩 차원) |
| `비트마스크와 집합의 대응 관계` | 0 | 집합 연산 O(1) (n ≤ 64), 전수 검증 O(4ⁿ) | O(1) |
| `부분집합 열거 최적화` | 0 | 순진 O(n·2ⁿ), Gray/최하위 비트 DP O(2ⁿ), 부분집합 열거 O(3ⁿ), SOS DP O(n·2ⁿ) | O(2ⁿ) |

## Stack

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateStack` | 1 | 연결 스택 생성 O(1), 배열 스택 생성 O(1) 할당 (값 초기화를 하면 O(용량)) | 배열 O(용량), 연결 O(1) (원소 수에 비례해 증가) |
| `Push` | 1 | 고정 배열 O(1), 동적 배열 분할상환 O(1) (최악 O(N)), 연결 O(1) | O(N) (동적 배열은 용량이 크기의 최대 2 배) |
| `Pop` | 1 | O(1) | O(1) |
| `Peek` | 1 | O(1) | O(1) |
| `Top` | 1 | O(1) | O(1) |
| `IsEmpty` | 1 | O(1) (카운터 없는 연결 스택의 size 는 O(N)) | O(1) |
| `IsFull` | 1 | O(1) | O(1) |
| `Size` | 1 | 카운터 방식 O(1), 세는 방식 O(N) | 카운터 방식 O(1) 추가 |
| `Clear` | 1 | 배열 O(N) (trivially destructible 이면 O(1)), 연결 O(N) | 반복 해제 O(1), 재귀 해제 O(N) 호출 스택 |
| `ArrayStack` | 2 | push·pop·peek·at O(1), 복사 O(N) | O(용량) |
| `Resize` | 2 | resize O(크기), 나머지 O(1) | O(용량) |
| `DynamicStack` | 2 | push·pop 분할상환 O(1) (최악 O(N)) | O(N), 용량은 크기의 4 배 이하 |
| `LinkedStack` | 3 | push·pop·peek O(1), 복사·뒤집기·소멸 O(N) | O(N) (노드당 포인터 하나 추가) |
| `PushNode` | 3 | O(1) | O(1) per node |
| `PopNode` | 3 | O(1) | O(1) |
| `ReverseString` | 4 | O(N) | O(N) |
| `BalancedParentheses` | 4 | O(N) | O(N) (한 종류 괄호는 O(1)) |
| `InfixToPostfix` | 4 | O(N) | O(N) |
| `PostfixEvaluation` | 4 | O(N) | O(N) |
| `PrefixEvaluation` | 4 | O(N) | O(N) |
| `DecimalToBinary` | 4 | O(log N) | O(log N) |
| `BaseConversion` | 4 | O(log_base N) | O(log_base N) |
| `Undo` | 4 | undo·redo·편집 O(편집 크기) | O(총 편집 크기) (스냅샷 방식은 O(문서 크기 × 편집 수)) |
| `BrowserHistory` | 4 | visit O(1) (forward 비우기는 O(forward 크기)), back·forward O(이동한 칸 수) | O(방문한 페이지 수) |
| `DepthFirstSearch` | 5 | O(V + E) | O(V) |
| `IterativeDFS` | 5 | O(V + E) | A 형 O(V) (경로 길이), B 형 O(E) |
| `MazeSolver` | 5 | O(R·C) | O(R·C) |
| `TopologicalSort` | 5 | O(V + E) | O(V) |
| `MonotonicStack` | 6 | O(N) (각 원소가 한 번 push, 한 번 pop) | O(N) |
| `NextGreaterElement` | 6 | O(N) | O(N) |
| `PreviousGreaterElement` | 6 | O(N) | O(N) |
| `LargestRectangle` | 6 | O(N), 행렬 버전 O(R·C) | O(N) |
| `DailyTemperatures` | 6 | O(N) | O(N) |
| `StockSpan` | 6 | next() 분할상환 O(1) | O(N) |
| `MinStack` | 7 | push·pop·top·getMin 모두 O(1) | 보조 스택 방식 O(N), 차이 부호화 O(1) 추가 |
| `MaxStack` | 7 | 보조 스택 방식 push·pop·top·peekMax O(1), popMax O(N) / 리스트+맵 방식 popMax 포함 O(log N) | O(N) |
| `TwoStacksInArray` | 7 | push·pop·peek O(1) | O(N) — 두 스택이 공간을 공유하므로 낭비 없음 |
| `MultipleStacks` | 7 | push·pop·peek O(1) | O(전체 칸 수) (스택 수와 무관) |
| `CallStack` | 8 | fib 호출 수 O(φ^n), 호출 스택 깊이 O(n) | O(n) 프레임 |
| `StackFrame` | 8 | O(깊이) | O(깊이 × 프레임 크기) |
| `TailRecursion` | 8 | O(n) | 비꼬리·(제거 없는) 꼬리 재귀 O(n), 반복문·트램펄린·TCO 적용 시 O(1) |
| `RecursionSimulation` | 8 | 재귀와 같다 (하노이 O(2ⁿ), 중위 순회 O(N)) | 명시적 스택 O(최대 재귀 깊이) — 호출 스택이 아니라 힙을 쓴다 |
| `LockFreeStack` | 9 | push·pop 분할상환 O(1) (락프리: 경쟁에서 재시도) | O(풀 크기) |
| `TreiberStack` | 9 | push·pop 분할상환 O(1) (락프리) | O(N + 지금까지의 pop 수) — 폐기 노드는 소멸 때까지 보관 |
| `EliminationBackoffStack` | 9 | 경쟁이 없으면 O(1); 경쟁이 있으면 교환 성공 시 중앙 스택을 거치지 않음 | O(풀 크기 + 슬롯 수) |
| `PersistentStack` | 10 | push·pop·top O(1) (모든 버전에서), 순회 O(N) | 연산당 새 노드 O(1), 이전 버전과 구조 공유 |
| `ImmutableStack` | 10 | push·pop·top·size O(1), 동등 비교 O(서로 다른 접두사 길이) | 변경당 O(1), 나머지는 공유 |
| `StackAllocator` | 10 | 할당·되감기 O(1) | 미리 확보한 용량 (할당당 헤더 없음, 정렬 패딩만) |
| `StackOverflow` | 10 | O(깊이) | 호출 스택 O(깊이 × 프레임), 명시적 스택 O(깊이) 힙 |
| `StackUnwinding` | 10 | 되감기 O(풀리는 프레임 수 + 소멸시킬 객체 수) — 예외가 던져질 때만 비용 발생 | O(1) 추가 |

## String

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateString` | 1 | append 분할상환 O(1), insert/erase O(n), 길이 O(1) | O(n) (15 바이트 이하는 객체 안) |
| `Length` | 1 | 바이트 길이 O(1) (저장), 코드 포인트·글자 수 O(n) | O(1) |
| `Concat` | 1 | 분할상환 O(1)/문자(곱셈 성장), 왼쪽 결합 O(k²L), join O(kL) | O(n) |
| `Substring` | 1 | substr 복사 O(len), 뷰 O(1) | substr 복사 O(len), 뷰 O(1) (포인터 + 길이) |
| `Compare` | 1 | O(min(\|a\|, \|b\|)) | O(1) |
| `문자열 비교의 시간복잡도` | 1 | 비교 O(LCP), 비교 기반 정렬 O(n log n · LCP), 멀티키 퀵정렬 기대 O(n log n + D) (무작위 피벗) | O(n) (포인터 배열), 재귀 깊이 O(log n + 최대 길이) |
| `Reverse` | 1 | O(n) | 바이트·코드 포인트 뒤집기 O(1), 글자 뒤집기 O(n) |
| `Split` | 1 | O(n) (string_view 토큰, 복사 없음) | O(토큰 수) |
| `Immutable String` | 1 | 복사 O(1), 연결 O(n+m), 인터닝 평균 O(len), 해시 O(1) (전체 문자열은 캐시, slice 는 O(len)) | O(n) (slice 는 원본 버퍼를 공유) |
| `Palindrome` | 2 | 판별 O(n), 가장 긴 회문 부분 문자열·개수 O(n²), 최소 삽입 O(n²), 최단 회문 O(n) | 판별 O(1), 최소 삽입 O(n²), 최단 회문 O(n) |
| `Anagram` | 2 | 판별 O(n), 윈도 탐색 O(\|text\| + \|pattern\|), 그룹핑 O(총 길이) (서명·해시) / O(총 길이 · log 길이) (정렬) | O(알파벳) (판별), O(총 길이) (그룹핑) |
| `RunLengthEncoding` | 2 | O(n) | O(n) |
| `ASCII부터 Unicode까지` | 3 | 부호화·복호화 O(1)/코드 포인트 | O(1) |
| `UTF-8과 UTF-16의 차이` | 3 | O(1) (글자당) | O(1) |
| `UTF8Validate` | 3 | O(n) | O(1) |
| `Rope` | 4 | 색인·분할·삽입·삭제·붙이기 O(log n) | O(n), 편집마다 O(log n) 새 노드 (나머지는 공유) |
| `GapBuffer` | 4 | 커서 근처 삽입/삭제 O(1), 이동 O(거리) | O(n + gap) |
| `PieceTable` | 4 | 편집 O(조각 수), 균형 트리로 O(log 조각 수) 개선 가능 | O(편집 횟수), 원본은 복사하지 않음 |
| `NaiveSearch` | 5 | 평균 O(n) (무작위 텍스트), 최악 O(n·m) | O(1) |
| `KMP` | 5 | O(n + m) (글자당 최악 O(log m) 이지만 총합은 O(n)) | O(m) |
| `RabinKarp` | 6 | 평균 O(n + m), 가짜 일치가 많으면 최악 O(n·m) | O(1) (2 차원은 O(R·C)) |
| `BoyerMoore` | 6 | 평균 O(n/m), 최악 O(n·m) (좋은 접미사 규칙과 Galil 규칙을 쓰면 O(n)) | O(m + σ) |
| `Horspool` | 6 | 평균 O(n/m), 최악 O(n·m) | O(σ) |
| `SundaySearch` | 6 | 평균 O(n/m), 최악 O(n·m) | O(σ) |
| `ZAlgorithm` | 7 | O(n + m) | O(n + m) (확장 Z 는 O(m)) |
| `LongestRepeatedSubstring` | 7 | 해시 이분 탐색 O(n log n), 접미사 배열 + LCP O(n log² n) | O(n) |
| `Manacher` | 7 | O(n) | O(n) |
| `Trie` | 8 | 삽입/검색/삭제/접두사 개수 O(L), 자동 완성 O(L + 결과 크기) | O(노드 수 · σ) |
| `AhoCorasick` | 8 | O(n + Σ\|패턴\| + z)  (z = 출현 횟수) | O(Σ\|패턴\| · σ) |
| `SuffixArray` | 9 | 구성 O(n log² n) (배가법) / O(n² log n) 최악 (순진), LCP O(n), 검색 O(m log n) | O(n) |
| `BuildSuffixArray` | 9 | O(n log² n)  (기수 정렬을 쓰면 O(n log n), SA-IS 는 O(n)) | O(n) |
| `LCPArray` | 9 | Kasai 단계 O(n) (이 코드의 접미사 배열 정렬은 O(n² log n)) | O(n) |
| `SuffixAutomaton` | 9 | 구성 O(n log σ), 질의 O(m log σ) | O(n) |
| `FMIndex` | 9 | count O(\|P\|·Occ 비용), locate O(s·Occ 비용), 구성 O(n log n) (이 구현의 정렬 기반) | BWT n 문자 + Occ 체크포인트 + SA 표본 n/s 개 (BWT 를 압축하면 n H_k 비트) |
| `PalindromicTree` | 9 | O(n log σ) | O(n) |
| `PolynomialRollingHash` | 10 | 전처리 O(n), 부분 문자열 해시 O(1), 해시 LCP O(log n) | O(n) |
| `RabinFingerprint` | 10 | 윈도 이동 O(1) (표 조회 2 번), 처음부터 계산 O(w) | O(1) (표 2 × 256 개) |
| `SubstringHash` | 10 | 전처리 O(n), 비교 O(1), 최장 공통 부분 문자열 O((n + m) log min(n, m)) | O(n) |
| `LongestCommonSubstring` | 10 | O(\|a\| log σ + \|b\| log σ) | O(\|a\|) |
| `LZW` | 11 | O(n log D) | O(D)  (사전 크기) |
| `BurrowsWheelerTransform` | 11 | 정의대로 O(n² log n), 접미사 배열(배증) O(n log² n), SA-IS 로 O(n) | O(n) |
| `MoveToFront` | 11 | O(n·σ) (σ ≤ 256) | O(σ) |
| `Huffman` | 11 | O(n + σ log σ) | O(σ) |
| `Levenshtein` | 12 | O(n·m), 띠 O(n·k), 비트 병렬 O(n·⌈m/64⌉) | O(n·m) (연산열 필요 시), 거리만 O(min(n, m)) |
| `DamerauLevenshtein` | 12 | O(n·m) | O(n·m) |
| `LongestCommonSubstringDP` | 12 | O(n·m) | O(m) |
| `LongestCommonSubsequence` | 12 | O(n·m) (Hirschberg 도 O(n·m)), 비트 병렬 O(n·⌈m/64⌉) | 표 O(n·m), Hirschberg·거리만 O(n + m) |
| `FiniteAutomaton` | 13 | 구성 O(m·σ), 검색 O(n) | O(m·σ) |
| `RegexNFA` | 13 | 매칭 O(n·m) (n = 텍스트, m = 정규식 크기) | O(m) |
| `Lexer` | 14 | O(n) (문자마다 상수 번 앞을 본다) | O(토큰 수) |
| `RecursiveDescentParser` | 14 | O(n) | O(중첩 깊이) |
| `InvertedIndex` | 15 | 색인 O(총 토큰 수 log V), AND 질의 O(\|짧은 목록\| · log(\|긴 목록\| / \|짧은 목록\|)) | O(총 토큰 수) |
| `NGramIndex` | 15 | 질의 O(\|q\| · 평균 포스팅 길이) | O(총 n-gram 수) |
| `TFIDF` | 15 | 색인 O(총 토큰), 질의 O(질의 단어의 색인 목록 길이 합) | O(고유 (단어, 문서) 쌍) |
| `문자열 알고리즘의 생물정보학 활용` | 16 | O(n) (k-mer 세기 O(n·k), 롤링은 O(n)) | O(고유 k-mer 수) |
| `NeedlemanWunsch` | 16 | O(n·m) | O(n·m) (점수만 O(min(n, m)), Hirschberg 로 정렬도 O(n + m)) |
| `SmithWaterman` | 16 | O(n·m) | O(n·m) |
| `BytePairEncoding` | 17 | 학습 O(병합 수 · 코퍼스 크기), 추론 O(병합 수 · 단어 길이) | O(어휘) |
| `WordPiece` | 17 | 추론 O(L²) (L = 단어 길이), 학습 O(병합 수 · 코퍼스) | O(어휘) |
| `SentencePiece` | 17 | Viterbi O(n · 최대 조각 길이), k-최선 O(n · L · k log k), EM 한 번은 O(코퍼스 · L) | O(n) |
| `TokenizeLLM` | 17 | O(병합 수 · 단어 길이) (실제 구현은 우선순위 큐로 O(n log n)) | O(어휘 + n) |
| `EmbeddingLookup` | 17 | 조회 O(d), 원-핫 행렬곱 O(V·d) | O(V·d) |
| `Detokenize` | 17 | O(총 길이) | O(총 길이) |
| `LLM 토크나이저는 왜 필요한가?` | 17 | O(병합 수 · 코퍼스) | O(어휘) |
| `KMP는 왜 O(n)인가?` | 0 | O(n + m) | O(m) |
| `Boyer-Moore가 빠른 이유` | 0 | 평균 O(n/m) | O(σ) |
| `Trie vs HashMap` | 0 | 트라이 접두사 질의 O(L + 결과 크기), 해시맵 O(N·L) | 트라이 O(노드 수 · σ), 해시맵 O(총 글자 수) |
| `Suffix Array vs Suffix Tree` | 0 | 접미사 배열 검색 O(m log n), 자동자 검색 O(m) | 트라이 O(n²), 자동자 O(n), 배열 O(n) |

## Tree

| 항목 | Part | 시간 | 공간 |
|------|-----:|------|------|
| `CreateTree` | 1 | 노드 추가 O(1), 변환 O(n) | O(n) (노드당 포인터 2 개 + 부모) |
| `Root` | 1 | 루트 찾기 O(n), 중심 O(n), reroot O(경로 길이) | O(n) |
| `Parent` | 1 | 추가·삭제 O(차수), 이동 O(깊이) (사이클 검사), k 번째 조상 O(log n) | O(n) (이진 승 O(n log n)) |
| `Child` | 1 | k 번째 자식·위치 삽입·삭제 O(k), 맨 뒤 삽입 O(1) | O(n) |
| `Sibling` | 1 | 이전 형제·삭제 단방향 O(k) / 양방향 O(1), 삽입 O(1) | O(n) (양방향은 노드당 포인터 하나 더) |
| `Degree` | 1 | 차수 계산 O(n), 카탈랑 열거 O(C(n−1)·n) | O(n) |
| `Depth` | 1 | 순진 O(n·h), BFS·메모이제이션 O(n) | O(n) |
| `Height` | 1 | O(n) | O(n) (반복문; 재귀는 O(h) 호출 스택) |
| `Level` | 1 | O(n) | O(n) (BFS 큐 = 가장 넓은 층) |
| `Size` | 1 | O(n) (구간 성질 검사는 O(n²)) | O(n) |
| `IsLeaf` | 1 | 판정 O(1), 전체 리프 O(n), 증분 갱신 O(log n) | O(n) |
| `IsRoot` | 1 | 판별 O(1) (트리 표현) / 분리 집합은 find 기준 거의 O(1) 분할상환 | O(n) |
| `CreateBinaryTree` | 2 | 직렬화·복원 O(n) (순회열 복원은 값→위치 맵으로 O(n log n)), 모양 열거 O(C(n)·n) | O(n) |
| `InsertLeft` | 2 | O(1) (노드를 이미 알 때), 값으로 찾으면 O(n) | O(1) 추가 (노드 하나) |
| `InsertRight` | 2 | O(1) (노드를 알 때) | O(1) 추가 |
| `DeleteNode` | 2 | O(n) (BFS 로 대상과 마지막 노드를 찾는다) | O(n) (BFS 큐) |
| `CopyTree` | 2 | 깊은 복사 O(n), 경로 복사 O(깊이) | O(n) 새 노드 (경로 복사는 O(깊이)), 명시적 스택 O(h) |
| `MirrorTree` | 2 | O(n) | 풀을 훑으면 O(1) 추가, BFS 는 O(너비) |
| `MergeTree` | 2 | O(min(n, m)) (겹치는 위치만 순회, 파괴적) / 함수형은 O(n + m) | O(h) 명시적 스택 |
| `Preorder` | 3 | O(n) | O(h) (명시적 스택) |
| `Inorder` | 3 | O(n) | O(h) (스택) — 왼쪽 사슬이면 O(n); Morris 순회는 O(1) |
| `Postorder` | 3 | O(n) | O(h) |
| `LevelOrder` | 3 | O(n) | O(가장 넓은 층) (완전 이진 트리에서는 약 n/2) |
| `MorrisTraversal` | 3 | O(n) (각 간선 최대 3 번) | O(1) 추가 (임시 스레드는 트리 안의 빈 포인터를 재사용) |
| `EulerTour` | 3 | 투어 O(n), RMQ 전처리 O(n log n) 질의 O(1) | O(n) |
| `TreeSearch` | 4 | O(n) (IDDFS 는 완전 이진 트리에서 O(n), 사슬에서는 O(n²)) | DFS·IDDFS O(h), BFS O(너비) |
| `FindNode` | 4 | 값 찾기 O(n), 경로 O(경로 길이), k 번째 노드 O(h) (크기 배열 전처리 O(n)) | O(n) |
| `FindParent` | 4 | 질의마다 탐색 O(n), 부모 배열 전처리 O(n) 후 질의 O(1) | O(n) |
| `LowestCommonAncestor` | 4 | 올라가기 O(h), 이진 승 O(log n) (전처리 O(n log n)), 오일러 투어 + RMQ O(1) (전처리 O(n log n)) | O(n log n) |
| `PathToNode` | 4 | 재귀 O(n), 부모 배열 O(경로 길이) (전처리 O(n)), 두 노드 사이 O(경로 길이) | O(경로 길이) (재귀 O(h) 호출 스택) |
| `DistanceBetweenNodes` | 4 | 거리 O(h) (LCA 방법에 따라 O(1)), 지름 O(n), 총합 O(n) | O(n) |
| `InsertBST` | 5 | 평균 O(log n), 최악 O(n) (정렬된 입력) | O(1) 추가 (반복문), 재귀는 O(h) 호출 스택 |
| `SearchBST` | 5 | 탐색·ceil·floor O(h), 구간 O(h + 결과 수) | O(1) (반복문) |
| `DeleteBST` | 5 | O(h) | O(1) 추가 (반복문, 노드 풀 재사용) |
| `FindMin` | 5 | BST O(h), 정렬 안 된 트리 O(n) | O(1) |
| `FindMax` | 5 | O(h), k 번째로 큰 수 O(h + k) | O(1) (k 번째 큰 수는 O(h) 스택) |
| `Successor` | 5 | 한 번 O(h), n 번 반복하면 총 O(n) | O(1) |
| `Predecessor` | 5 | 한 번 O(h), n 번 반복하면 총 O(n) | O(1) |
| `ValidateBST` | 5 | 한계 방식·중위 방식 O(n), 브루트포스 O(n·h) | O(h) |
| `AVLInsert` | 6 | O(log N) | O(N) (재귀 깊이 O(log N)) |
| `AVLDelete` | 6 | O(log N) (재균형은 최대 O(log N) 번) | O(N) (재귀 깊이 O(log N)) |
| `BalanceFactor` | 6 | O(1) per node (저장된 높이 사용); 전체 재계산은 O(N) | O(N) |
| `RotateLeft` | 6 | O(1) (포인터 몇 개) | O(1) |
| `RotateRight` | 6 | O(1) | O(1) |
| `RotateLeftRight` | 6 | O(1) | O(1) |
| `RotateRightLeft` | 6 | O(1) | O(1) |
| `RBInsert` | 7 | 삽입 O(log n) (회전 ≤ 2, 색 바꾸기는 분할상환 O(1)) | O(n) |
| `RBDelete` | 7 | O(log N), 삭제 후 회전은 최대 3번 | O(N) |
| `FixViolation` | 7 | O(log N), 회전은 삽입당 최대 2번 | O(1) 추가 공간 |
| `Recolor` | 7 | 삽입당 재색칠 분할상환 O(1), 최악 O(log N) | O(1) |
| `DoubleBlack` | 7 | 삭제당 O(log N), 회전은 최대 3번 | O(1) 추가 공간 |
| `TwoThreeTree` | 7 | 탐색·삽입 O(log N) (높이 log3 N ~ log2 N) | O(N) |
| `TwoThreeFourTree` | 7 | 탐색·삽입 O(log N), 삽입은 하향 한 번 | O(N) |
| `LeftLeaningRedBlackTree` | 7 | 삽입·삭제·탐색 O(log N) | O(N) |
| `BinaryHeap` | 8 | push·pop O(log n), top O(1), build O(n) | O(n) |
| `HeapInsert` | 8 | O(log N) (평균 O(1)) | O(1) |
| `HeapDelete` | 8 | O(log N) | O(1) |
| `Heapify` | 8 | heapify O(log N), build-heap O(N) | O(1) |
| `BuildHeap` | 8 | O(N) | O(1) |
| `HeapSort` | 8 | O(N log N) 최악도 동일 | O(1) |
| `FibonacciHeap` | 8 | push/meld/decreaseKey 분할상환 O(1), extractMin 분할상환 O(log N) | O(N) |
| `BinomialHeap` | 8 | push·unite·extractMin·decreaseKey 모두 O(log N) (push 는 분할상환 O(1)) | O(N) |
| `PairingHeap` | 8 | push/meld O(1), deleteMin 분할상환 O(log N), decreaseKey 분할상환 o(log N) (정확한 한계는 미해결 문제) | O(N) |
| `LeftistHeap` | 8 | merge·push·pop O(log N) | O(N) |
| `DAryHeap` | 8 | push·decreaseKey O(log_d N), pop O(d log_d N) | O(N) |
| `MinMaxHeap` | 8 | min/max O(1), push·popMin·popMax O(log N) | O(N) |
| `SkewHeap` | 8 | push·pop·meld 분할상환 O(log n) (한 번의 연산은 O(n) 일 수 있다) | O(n), 노드마다 키 + 포인터 둘 (균형 정보 없음) |
| `IntervalHeap` | 8 | push·popMin·popMax O(log n), min·max O(1) | O(n) — 포인터 없는 배열 |
| `LoserTree` | 8 | 병합 원소당 정확히 ceil(log2 k) 번 비교, 만들기 O(k) | O(k) (내부 노드 k-1 개의 패자 번호 + 머리 키) |
| `TrieInsert() & TrieSearch` | 9 | O(L) | O(총 문자 수 · 알파벳) — 노드당 26 개의 간선 슬롯 |
| `TrieDelete` | 9 | O(L) | O(L) (경로 저장) |
| `RadixTree` | 9 | 삽입·검색·삭제 O(L · σ) (σ = 한 노드의 자식 수 탐색, std::map 이면 L log σ) | O(단어 수) 노드 + 레이블 (노드 ≤ 2n + 1) |
| `GeneralTree` | 9 | 자식 추가 O(1) (마지막 자식 포인터), 순회 O(N) | O(N) |
| `NaryTree` | 9 | 인덱스 계산 O(1), N-ary 힙 삽입 O(log_N n), 삭제 O(N log_N n) | O(N) 배열 |
| `SuffixTrie` | 10 | 구성 O(N²), 검색 O(M) | O(N²) 노드 (서로 다른 부분 문자열 수에 비례) |
| `SuffixTree` | 10 | 이 구성 O(n²), Ukkonen O(n); 검색 O(m + 출현 수) | O(n) 노드 (레이블은 부분 문자열 복사; 인덱스 쌍으로 두면 O(n)) |
| `PatriciaTrie` | 10 | 삽입·검색 O(키 길이 비트 수) | O(n) |
| `TernarySearchTree` | 10 | 삽입·검색 O(L + log σ) 평균 (σ = 알파벳 크기), 와일드카드 O(노드 수) 최악 | O(총 글자 수) 노드 · 3 포인터 |
| `SuffixArray` | 10 | 구성 O(n log n), LCP O(n), 패턴 검색 O(m log n) | O(n) |
| `SegmentTree` | 11 | build O(N), update/query/maxRight O(log N) | O(N) |
| `FenwickTree` | 11 | build O(N), add/prefix O(log N) | O(N) |
| `KDTree` | 11 | 구성 O(n log n), 최근접 평균 O(log n) | O(n) |
| `QuadTree` | 11 | 삽입 O(깊이), 범위 질의 평균 O(log n + k) | O(n) |
| `Octree` | 11 | 삽입 O(깊이), 반경 질의 평균 O(log n + k) | O(n) |
| `BSPTree` | 11 | 구성 — 첫 선분을 고르면 노드마다 O(m) 분류라 균형이면 O(n log n), 최악 O(n²) (분할로 조각이 늘면 그 이상);  여기 쓴 최소 절단 선택기는 노드마다 O(m²) 라 루트에서만  | O(조각 수) (분할로 최대 O(n²)) |
| `RangeQuery` | 12 | 전처리 O(n log n), 질의 O(1) | O(n log n) |
| `LazyPropagation` | 12 | 갱신·질의 O(log n) | O(n) |
| `RangeUpdate` | 12 | O(log n) | O(n) |
| `SqrtDecomposition` | 12 | 갱신·질의 O(√n) | O(n) |
| `MergeSortTree` | 12 | 구성 O(n log n), 질의 O(log² n) | O(n log n) |
| `BTree` | 13 | 검색·삽입 O(t · log_t N), 디스크 접근 O(log_t N) | O(N) |
| `BPlusTree` | 13 | 검색·삽입 O(log_M N), 범위 질의 O(log_M N + k) | O(N) |
| `SplayTree` | 13 | 분할상환 O(log N), 작업 집합 크기 w 에서 O(log w) | O(N) |
| `Treap` | 13 | 기대 O(log N) | O(N) |
| `CartesianTree` | 13 | 구성 O(n), RMQ 는 트리 높이에 비례 (LCA 전처리 후 O(1)) | O(n) |
| `ScapegoatTree` | 13 | 삽입·삭제 분할상환 O(log N), 검색 O(log N) | O(N) (노드에 균형 정보 없음) |
| `OrderStatisticTree` | 13 | select·rank·삽입·삭제 기대 O(log N) | O(N) (노드당 크기 필드 하나) |
| `WeightBalancedTree` | 13 | O(log N) | O(N) |
| `ZipTree` | 13 | 기대 O(log N) | O(N) (랭크는 작은 정수) |
| `WAVLTree` | 13 | 삽입·삭제 O(log N) (승급·강등이 위로 전파되어도 경로 길이만큼), 연산당 회전 최대 2번 | O(N) (랭크는 작은 정수; 랭크 차를 2비트로 저장 가능), 재귀 깊이 O(log N) |
| `PersistentTree` | 14 | 갱신·질의 O(log N) | 버전당 O(log N) |
| `ImmutableTree` | 14 | 삽입 기대 O(log N) (인터닝 조회 포함 O(log² N)) | 버전당 O(log N), 같은 서브트리는 공유 |
| `FingerTree` | 14 | 양 끝 push/pop 분할상환 O(1), at(i) O(log min(i, N − i)) | O(N), 영속 버전은 구조 공유 |
| `RootingTree` | 15 | O(N) | O(N) |
| `TreeDP` | 15 | O(N) | O(N) |
| `HeavyLightDecomposition` | 15 | 전처리 O(N), 경로 질의·갱신 O(log² N) | O(N) |
| `CentroidDecomposition` | 15 | 구성 O(N log N), 표시·질의 O(log N) | O(N log N) |
| `BinaryLifting` | 15 | 전처리 O(N log N), 질의 O(log N) | O(N log N) |
| `EulerTourTechnique` | 15 | 전처리 O(N), 질의·갱신 O(log N) | O(N) |
| `LinkCutTree` | 15 | 모든 연산 분할상환 O(log N) | O(N) |
| `TopTree` | 15 | 구성 O(N), 클러스터 병합 O(1) | O(N) |
| `EulerTourTree` | 15 | link·cut·connected·treeSize 기대 O(log n) (트립의 split/merge 몇 번 + 부모 포인터 올라가기) | O(n) — 정점 노드 n 개 + 간선당 호 노드 2 개 |
| `ExpressionTree` | 16 | 구성·계산·출력 O(N), 미분 O(N) (정리 포함) | O(N) |
| `SyntaxTree` | 16 | 구문 분석 O(N), 실행은 프로그램에 따라 다름 | O(N) |
| `ParseTree` | 16 | 재귀 하강 파싱 O(N), 모호한 문법의 트리 수 세기 O(N^3) | O(N) |
| `DecisionTree` | 16 | ID3 O(속성 수 × N × 깊이), CART 노드당 O(속성 수 × N log N) | O(N) |
| `MerkleTree` | 16 | 루트 계산 O(N) 해시, 검증 O(log N) 해시, 감사 경로 *생성* O(N) 해시 (형제 부분 트리의 해시를 매번 다시 계산한다; 노드 해시를 저장해 두면 O(log N)) | 증명 O(log N) |
| `IntervalTree` | 16 | 삽입·삭제 O(log N) 기대, 겹침 하나 O(log N), 겹침 k 개 모두 O(k log N) 이내 | O(N) |
| `RopeTree` | 16 | 색인·분할·삽입·삭제·붙이기 O(log N) | O(N), 편집마다 O(log N) 새 노드 |
| `RTree` | 16 | 삽입 O(M log_m N), 검색은 겹침 정도에 따라 O(log N) ~ O(N) | O(N) |
| `VanEmdeBoasTree` | 16 | 모든 연산 O(log log U) | O(N log log U) (lazy 할당; 즉시 할당하면 O(U)) |
| `트리 순회의 재귀와 반복 구현` | 0 | 세 방식 모두 O(N) (Morris 는 간선을 최대 3번 지남) | 재귀 O(h) 호출 스택, 반복 O(h) 명시적 스택, Morris O(1) |
| `Binary Tree vs BST` | 0 | 이진 트리 탐색 O(N), BST 탐색 O(높이) (평균 O(log N), 최악 O(N)) | O(N) |
| `BST vs AVL vs Red-Black` | 0 | BST 최악 O(N), AVL·LLRB O(log N) | O(N) |
| `Segment Tree vs Fenwick Tree` | 0 | 둘 다 점 갱신·질의 O(log N); 펜윅은 상수가 작고 세그먼트 트리는 연산 종류가 자유롭다 | 펜윅 N, 세그먼트 트리 2N (재귀 구현은 4N) |
