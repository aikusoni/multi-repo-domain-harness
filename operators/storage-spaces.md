---
operator_id: operator:storage-spaces
owner: harness
implementation: operators/storage-spaces.py
affected_projects:
  - all
related_initiatives: []
---

# Operator: storage-spaces

## 목적과 책임

등록된 저장공간·adapter·research reference, 여러 표현의 catalog와 transformation lineage를 감사하고 결정적
index, 제한 조회, query plan과 catalog 단위 context를 제공한다. 실제 제품 자료를 수집하거나 외부
저장소를 수정하지 않는다.

## 실행 조건

- 자동 트리거: 없음
- 수동 호출: `./operators/storage-spaces.py <command>`
- 권장 호출: 저장공간 정의·adapter·research catalog·catalog·transformation 변경 후, 공통 규칙 커밋 전
- 스케줄 시간대: UTC (`+00:00`, 서머타임 미적용)
- 중단 조건: `storage/registry.json` 부재·파싱 실패 또는 잘못된 인자

## 명령 계약

```bash
./operators/storage-spaces.py audit
./operators/storage-spaces.py build-index
./operators/storage-spaces.py query --role record --text event --limit 20
./operators/storage-spaces.py plan --mode relation --mode evidence --limit 20
./operators/storage-spaces.py context <catalog-entry-id> --limit 20
```

- `audit`: registry와 definition 일치, v2 구현·portability·fallback, adapter 동작·license, 공개 research
  source, location, UTC, public-safe ref, 등록 space와 lineage를 검사한다.
- `build-index`: audit가 깨끗할 때만 `indexes/storage-catalog.json`을 원자적으로 다시 만든다.
- `query`: control plane의 space·adapter·research·catalog·transformation 레코드만 필터링한다.
- `plan`: 요청 query mode와 일치하는 active space, 빠지는 mode와 각 공간의 손실을 반환한다.
- `context`: catalog entry 하나의 representation·lineage·space 손실·transformation을 `--limit` 안에서 조립한다.

`--root <path>`는 fixture 검증용이다. 실제 운영에서는 생략한다.

## 입력 계약

- `storage/registry.json`과 등록된 `storage/definitions/*.json`
- `storage/adapters/registry.json`과 등록된 adapter definition
- `research/catalog.json`
- `storage/catalog/*.json`, `storage/transformations/*.json`
- 해당 JSON의 `schemas/*.schema.json` 계약
- Python 3 표준 라이브러리

## 출력과 성공 판정

- audit 발견 없음: `OK storage-spaces` 한 줄, exit code `0`
- audit 발견 있음: `ATTENTION storage-spaces`와 안정된 코드·상대 경로, exit code `0`
- index 생성: `BUILT storage-index`, exit code `0`
- 발견 사항이 있는 build/query/plan/context: `ATTENTION` 뒤 거절, non-zero
- query/plan/context 성공: JSON 한 개
- 필수 입력·인자 오류: `ERROR` 또는 설명, non-zero

audit의 주요 코드 범위는 `S`(registry·space), `D`(adapter), `R`(research), `C`(catalog),
`T`(transformation)다. `ATTENTION`은 자동 수정 근거가 아니라 정의·구현·자료 중 무엇이 잘못됐는지
검토하라는 신호다.

## 권한과 부작용

- 읽기 범위: 입력 계약과 등록 location의 존재 여부
- 쓰기 범위: `build-index`의 `indexes/storage-catalog.json`만
- 외부 변경: 없음
- 사용자 승인 필요 조건: 없음

## 실행 안전성

- 멱등성: 입력이 같으면 audit·query·plan·context와 생성 index byte가 같다.
- 동시 실행: 읽기 명령은 안전하다. build는 임시 파일 교체를 쓰지만 같은 root에서 동시 실행하지 않는다.
- 재시도: 입력을 고친 뒤 1회
- query 예산은 결과 기본 20개, context 예산은 representation·lineage source 목록별 기본 20개이며
  `--limit`은 1 이상

index에는 생성 시각 대신 입력 파일명과 byte의 `sha256` digest를 넣는다. 연구 source URL은 index에
복제하지 않는다. 따라서 단순 재실행은 diff를 만들지 않고, 모든 생성 결과는 커밋 전 별도 공개 위험
검토를 받는다.

## 실패와 복구

- 실패 분류: JSON 파싱, registry-definition 불일치, 미등록 space·adapter·research, license·fallback·
  portability 미검토, 위험 ref·source, lineage 단절, index 쓰기 실패
- 복구 절차: S/D/R/C/T 코드가 가리키는 정본을 고치고 audit 후 build를 다시 실행한다.
- issue 승격 조건: 복구할 source가 없거나 여러 프로젝트의 활성 representation이 오도될 수 있음

## 실행 증거

- 로그 위치: 표준 출력·표준 오류
- 보존 기간: 별도 보존하지 않음. 필요한 결과만 task 검증란에 요약한다.
- 민감정보 제거: 본문을 출력하지 않고 control-plane 메타데이터와 public-safe ref만 다룬다.

## 검증

- 정상 registry, 두 representation, transformation fixture의 audit·build·query·plan·context 성공
- 등록 adapter와 근거 research를 연결하고 required query·export capability를 충족한 space의
  audit·query·index 성공
- 미등록 space·research, 미검토 license, 사설 research URL과 위험 ref fixture의 `ATTENTION`과 build 거절
- 같은 입력에서 index byte와 digest가 동일함

## 변경 호환성

`OK|ATTENTION|ERROR|BUILT` 접두사, S/D/R/C/T 코드 범위, registry·definition·adapter·research·catalog·
transformation schema와 index의 결정성은 공개 계약이다. 호환되지 않는 변경은 schema version,
`changed/`와 migration 방침을 함께 갱신한다.
