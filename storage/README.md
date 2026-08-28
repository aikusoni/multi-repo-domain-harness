# storage

정보 성격과 질의 목적에 맞는 Storage Space를 등록하고, 여러 표현의 출처·변환·손실을 연결한다.

```text
storage/
├── registry.json       # active 공간과 definition 경로의 정본
├── definitions/        # 공간별 역할·보존·손실·query·rebuild 계약
├── adapters/           # 외부 구현의 공통 API definition과 active registry
├── policies/           # routing과 공개 안전 경계
├── transformations/    # 표현 변환 방법·버전·입출력·손실
├── catalog/            # 여러 공간의 representation과 lineage 연결
└── spaces/             # 이 저장소가 직접 소유하는 선택적 파일 기반 공간
```

기존 `journal/`, `explorations/`, `requests/`, `issues/`, `changed/`, `tasks/`는 이동하지 않는다.
definition의 `locations`가 그 위치를 기존 record space로 등록한다. `explorations/`는 narrative record에
포함되지만 비정본이며 일반 작업 시작 시 읽거나 실행 근거로 사용하지 않는다.

## 운영 순서

1. 질문과 정보에서 보존할 특성, 허용 손실과 필요한 query mode를 정한다.
2. `registry.json`의 active space 중 목적에 맞는 곳을 고른다.
3. 새 구현이 필요하면 `research/catalog.json`과 후보를 평가하고 native·adapter·hybrid·custom-minimal 중
   최소 전략을 고른다.
4. 외부 구현을 쓰면 등록 adapter, 공개 export와 장애 fallback을 space definition에 연결한다.
5. 같은 관찰을 여러 공간에 투영하면 catalog entry로 representation과 lineage를 연결한다.
6. 파생 표현은 transformation과 rebuild source를 기록한다.
7. `operator:storage-spaces`로 감사하고 index를 다시 만든다.
8. query plan과 context 결과가 가리키는 원본 record·evidence를 중요한 판단 전에 재확인한다.

적합한 공간이 없으면 임의 폴더나 엔진을 만들지 않는다. capability, 연구·구현 후보, definition·schema·
adapter·비용·portability·fallback·소급 여부를 proposal에서 승인받은 뒤 registry에 추가한다.

## 명령

```bash
./operators/storage-spaces.py audit
./operators/storage-spaces.py build-index
./operators/storage-spaces.py query --role record --text event
./operators/storage-spaces.py plan --mode relation --mode evidence
./operators/storage-spaces.py context <catalog-entry-id> --limit 20
```

상세 설계는 `docs/storage-architecture.md`, 구현 선택은 `docs/storage-adapters.md`, 형식 정본은
`schemas/*.schema.json`, 현재 실행 계약은 `operators/storage-spaces.md`를 따른다. 장기 로컬 DB·broker·
context 실행 계층은 `docs/local-storage-runtime.md`, 인출 상태·trace·Memory Fault 후보는
`docs/memory-reliability.md`에 분리하며 현재 active 기능으로 간주하지 않는다.
