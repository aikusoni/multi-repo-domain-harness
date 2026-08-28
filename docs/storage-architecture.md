# 조합 가능한 저장공간 아키텍처

## 목적

이 하네스는 하나의 데이터 모델이나 데이터베이스를 모든 정보에 강제하지 않는다. 정보의 성격, 사용 목적,
질의 방식, 비용과 허용 가능한 손실에 따라 여러 저장공간을 등록하고 조합하는 메모리 아키텍처다.

```text
원본과 기존 기록
  → 관찰·수집
  → Storage Policy와 Router
  → 목적별 Storage Space
  → Cross-Space Catalog
  → Query Planner
  → 제한된 Context
```

제품 저장소와 외부 시스템이 실제 원본을 소유한다. 하네스는 원본을 완전히 복제하지 않으며, 무엇을
보존·압축했고 무엇을 잃었는지 추적해 원본 또는 이전 표현으로 돌아갈 수 있게 한다.

## 손실 모델

정보는 관찰, 구조화, 검색, 문맥 조립의 각 단계에서 손실된다.

```text
제품 세계
  → 관찰 손실
원본 자료와 실행 결과
  → 구조화 손실
저장공간별 표현
  → 검색 손실
선택된 결과
  → 문맥 압축
작업 문맥
```

목표는 손실을 없애는 것이 아니라 입력·출력·방법·버전·보존 특성·제거 특성·재처리 가능성을 선언해
통제하는 것이다. 중요한 결론은 압축 표현에서 끝내지 않고 원본 근거를 다시 확인한다.

## 저장공간 역할

모든 Storage Space는 다음 역할 중 하나를 선언한다.

| role | 의미 | 재생성 기대 |
|---|---|---|
| `evidence` | 원본 또는 안전한 원본 참조 | 원본이므로 필수 아님 |
| `record` | 관찰·요청·결정 등 하네스가 직접 보존하는 기록 | 보통 재생성 불가 |
| `projection` | evidence·record에서 계산한 상태나 표현 | 가능해야 함 |
| `index` | 검색을 위해 생성한 파생 자료 | 반드시 가능 |
| `cache` | 현재 작업을 위한 임시 고해상도 정보 | 언제든 폐기 가능 |

projection·index·cache를 Source of Truth로 사용하지 않는다. 삭제 후 복구가 불가능한 공간은 `rebuild`에
그 사실과 보존 책임을 명시한다.

## 저장공간 유형

| kind | 주요 목적 | 보존 특성 | 대표 손실 |
|---|---|---|---|
| `evidence-space` | 감사와 재검증 | 원본 위치·무결성·관찰 방법 | 검색 편의와 해석 |
| `narrative-space` | 의도와 과정 | 요청·결정 경위·원문 | 구조화된 현재 상태 |
| `event-space` | 변화 추적 | 시각·순서·변경 | 현재 상태의 직접 조회 |
| `object-space` | 대상·상태·수명주기 | 안정 ID·관점별 주장 | 원문의 세부 맥락 |
| `relation-space` | 연결과 영향 탐색 | source·target·관계 근거 | 연속성·밀도 |
| `field-space` | 분포·근접·중첩 | 좌표·영역·해상도 | 명시적 의미 |
| `table-space` | 정확한 구조와 계산 | 값·제약·정규화 | 비정형 문맥 |
| `time-series-space` | 수치의 시간 변화 | 순서·간격·추세 | 원인과 의미 |
| `semantic-space` | 유사 자료 발견 | 의미적 근접성 | 정확한 사실·관계 |
| `residual-space` | 미분류 정보 보존 | 예외·충돌·희귀 패턴 | 즉시 활용성과 정리 |
| `working-space` | 현재 작업 수행 | 선택된 고해상도 정보 | 장기 보존과 전체성 |

모든 프로젝트가 모든 종류를 만들 필요는 없다. `storage/registry.json`에 등록된 active 공간만 현재 하네스의
구성으로 취급한다. Object·Relation·Field는 선택 가능한 저장 전략이며 하네스 전체의 필수 중심 모델이
아니다.

## Storage Space Definition

각 공간은 `storage/definitions/*.json`에서 다음을 선언한다.

- `role`, `kind`, `status`, 목적과 실제 `locations`
- 수용 레코드와 보존할 특성
- 허용 손실과 지원 질의 방식
- 쓰기·일관성·보존 정책
- provenance 의무와 재구성 가능성
- 비용 등급, 공개 안전성, 읽기·쓰기 책임

정의가 없는 디렉터리나 외부 저장소를 하네스의 활성 공간으로 간주하지 않는다. 정의와 실제 구현이
갈리면 `operator:storage-spaces audit`이 알리고, 정의 또는 adapter를 같은 변경에서 정합시킨다.

## 여러 표현과 Cross-Space Catalog

같은 관찰은 목적에 따라 여러 표현을 가질 수 있다. 예를 들어 원본 실행 결과의 안전한 참조는 evidence,
변화는 event, 반복 수치는 time-series, 지속 대상의 상태는 object, 설명되지 않는 부분은 residual에
투영할 수 있다.

`storage/catalog/*.json`은 실제 데이터를 복사하는 공간이 아니라 다음을 연결하는 제어 계층이다.

- 안정적인 정보·관찰 식별자
- 저장공간별 representation 위치
- evidence와 파생 표현의 lineage
- 변환 방법·버전
- 관찰·생성 시각과 유효기간
- 무결성·공개 안전성 메타데이터

각 representation은 등록된 space를 가리켜야 한다. 하나의 표현이 사라져도 lineage가 가리키는 source와
transformation을 통해 복구 가능 여부를 판단할 수 있어야 한다.

## 기존 하네스 기록의 위치

기존 구조는 이동하거나 세계 모델 형식으로 일괄 변환하지 않는다.

| 기존 영역 | 등록 공간 | 성격 |
|---|---|---|
| `journal/`, `requests/`, `proposals/` | narrative | 조사·의도·결정 과정의 record |
| `issues/`, `changed/`, `feedback/` | event | UTC 시간순 append-only record |
| `ISSUES.md`, `AGENDA.md`, `INITIATIVES.md`, `tasks/` | current-state table | 재작성형 상태와 폴더 상태 record |
| `storage/spaces/evidence/` | evidence reference | 공개 안전한 원본 식별자 |
| `storage/spaces/objects/` | object | 선택적 안정 ID·관점별 주장 |
| `storage/spaces/relations/` | relation | 선택적 관계·영향 표현 |
| `storage/spaces/residuals/` | residual | 미분류·충돌·희귀 정보 |

기존 기록을 catalog와 연결할 필요가 있을 때 representation `ref`로 상대경로만 가리킨다. 기존 append-only
기록을 소급 수정하지 않으며 새 연결부터 적용한다.

## Storage Policy와 Router

새 정보를 기록하기 전에 다음을 판단한다.

1. 원본 검증이 목적인가, 의도·변화·대상·관계·수치·유사성·미분류 신호 중 무엇이 중요한가?
2. 어떤 특성을 반드시 보존하고 어떤 손실을 허용할 수 있는가?
3. 현재 registry에 목적과 query mode가 맞는 active 공간이 있는가?
4. 기존 공간 하나로 충분한가, 같은 관찰을 여러 표현으로 투영해야 하는가?
5. 파생 표현이면 transformation과 rebuild source가 있는가?
6. 공개 저장소에 안전한 메타데이터만 남는가?

적합한 active 공간이 없으면 임의 디렉터리를 만들지 않는다. proposal에서 정의·schema·adapter·비용과
마이그레이션·소급 여부를 승인받은 뒤 registry에 추가한다.

## Query Planner

문장 유사도 하나로 모든 공간을 조회하지 않는다.

| 질문 | 우선 query mode·공간 |
|---|---|
| 정확한 식별자·현재 상태 | exact·state, table/object |
| 변화 과정 | time-range, event/narrative |
| 의존·영향 | relation, relation-space |
| 수치와 추세 | aggregate·time-range, table/time-series |
| 근접·중첩 | region·proximity, field |
| 비슷한 사례 | similarity, semantic |
| 원인 검증 | evidence, evidence-space |
| 설명되지 않은 신호 | residual, residual-space |

Query Planner는 정확한 ID와 구조화 조건을 먼저 적용하고, 필요한 공간만 고른 뒤 catalog로 결과를 연결한다.
시간·출처·신뢰도·유효성을 비교하며 충돌과 residual을 숨기지 않는다. 중요한 판단은 evidence로 돌아간다.

## Context Composer

Context Composer는 모든 저장공간을 프롬프트에 넣지 않는다. 현재 프로젝트·task, 질문 유형, 관련 ID,
직접 관계, 최근 중요 event, 충돌, residual과 필요한 evidence만 선택한다. `--limit`과 관계 깊이로 예산을
제한하고, 잘린 결과와 사용한 공간·손실을 출력에 표시한다.

신뢰도가 낮거나 변경이 되돌리기 어렵다면 압축된 projection보다 원본 record와 evidence를 우선한다.

## 관점과 독립성

Object·Relation 같은 공간을 사용할 때 `structure`, `runtime`, `domain`, `temporal`, `user`, `security`,
`challenge`, `residual` 관점을 구분할 수 있다. 여러 관찰자가 같은 결론을 냈다는 이유만으로 확정하지 않고
근거 독립성, 방법 다양성, 시각, 반증 가능성과 실제 결과를 우선한다.

독립 관찰 자동화와 다중 에이전트 실행은 초기 구현 범위가 아니다. 실제 필요가 생기면 세션 통신 예산과
사용자 승인 경계를 유지하는 별도 proposal로 도입한다.

## 공개·권한 경계

- 제품 코드, 원시 로그·메트릭, 문서·이미지 원본, 고객·운영 데이터와 비공개 시스템 구조를 복사하지 않는다.
- source·representation ref는 `<project-id>:<relative-path-or-opaque-id>` 형식의 공개 안전한 식별자를 쓴다.
- 로컬 절대경로, URL, 인증정보, 계정과 원본 본문을 catalog·index·view에 넣지 않는다.
- permissions는 책임 경계를 설명할 뿐 외부 시스템 권한을 부여하지 않는다.
- 보안 관점의 상세가 공개 위험을 만들면 레코드를 생성하지 않고 안전한 원본 시스템에만 둔다.

## 단계적 확장

초기 단계는 registry, 정의, catalog schema, 기존 기록 연결, 결정적 index, query planning과 제한된 context
조립까지만 구현한다.

후속 단계는 실제 질의와 비용 증거가 있을 때 별도 proposal로 진행한다.

1. evidence·object·relation·residual 파일 adapter와 유형별 record schema 확장
2. transformation 실행과 lineage 무결성·재구성 검증
3. time-series·semantic adapter와 exact/time/relation 혼합 검색
4. 다중 관점 독립 관찰과 충돌·누락 분석
5. field 좌표계·해상도·영역 검색 실험
6. 토큰 예산과 중요도에 따른 다중 해상도 context composer

그래프 DB, 벡터 DB, 시계열 DB와 field 엔진은 실제 필요성이 확인된 뒤 교체 가능한 adapter로 도입한다.
