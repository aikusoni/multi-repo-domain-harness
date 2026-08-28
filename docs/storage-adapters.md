# 저장 구현 재사용과 Adapter 계약

## 목적

하네스는 새로운 저장 요구가 생겼다는 이유만으로 저장 엔진·검색기·시뮬레이터를 직접 구현하지 않는다.
먼저 필요한 capability를 정의하고 공개 연구와 구현 후보를 조사한 뒤, 적합한 구현은 표준 Storage Adapter로
연결한다. 직접 구현은 하네스 고유 제어 계층과 최소 fallback에 한정한다.

```text
Storage Space Definition
  → Capability Requirements
  → Implementation Discovery
  → Evaluation Gate
  → Native | Adapter | Hybrid | Custom-minimal
  → Cross-Space Catalog와 운영 상태
```

reference, candidate, adapter, active space는 서로 다른 상태다. 연구 reference를 등록하거나 구현체를
발견해도 채택된 것이 아니며, active adapter도 그 외부 시스템을 evidence·record의 정본으로 자동
승격하지 않는다.

## Capability Requirements

구현을 조사하기 전에 Storage Space Definition으로 다음을 확정한다.

| 질문 | definition 필드 |
|---|---|
| 어떤 자료를 수용하는가? | `accepts`, `kind` |
| 무엇을 조회해야 하는가? | `query_modes` |
| 무엇을 보존하고 잃을 수 있는가? | `preserves`, `losses` |
| 어떤 일관성과 보존 기간이 필요한가? | `consistency`, `retention` |
| 출처·재구성 책임은 무엇인가? | `provenance`, `rebuild` |
| 비용·권한·공개 경계는 무엇인가? | `cost`, `permissions`, `public_safety` |
| 장애·교체 뒤 무엇이 남아야 하는가? | `implementation.fallback`, `portability` |

특정 제품 기능을 전제로 requirement를 역산하지 않는다. 실제 query, 규모, 성능과 운영 제약이 확인되지
않았으면 `[미검증]`으로 표시하고 후보 평가를 보류한다.

## 발견과 후보 상태

관련 연구·공개 구현·범용 엔진·도메인 전용 시스템을 조사하고, 검증한 공개 reference는
`research/catalog.json`에 등록한다. reference의 기본 상태는 `reference-only`다.

도입 가능성을 실제로 비교할 때만 space definition의 `implementation.candidates`에 후보를 만든다.

```text
discovered → evaluating → optional → selected
                    └────→ rejected
```

- `discovered`: 존재와 기본 capability만 확인
- `evaluating`: fixture로 요구사항·손실·비용·권한을 검증 중
- `optional`: 일부 상황에서 사용할 수 있으나 현재 구현은 아님
- `selected`: license·유지보수·fallback까지 통과해 현재 adapter가 사용
- `rejected`: 근거와 함께 채택하지 않기로 결정

후보 상태는 연구의 권위나 기능 목록만으로 올리지 않는다. 채택·기각이 여러 프로젝트의 계약이나 장기
데이터 접근에 영향을 주면 decision/ADR과 migration 방침을 함께 남긴다.

## 평가 게이트

후보는 다음 질문을 모두 평가한다.

1. 필요한 데이터 형태와 query mode를 안정적으로 표현하는가?
2. source·transformation·result lineage를 추적할 수 있는가?
3. 압축·샘플링·정규화 등 알려진 손실과 해상도를 드러내는가?
4. 공개 형식으로 export하고 projection·index를 재생성할 수 있는가?
5. 프로젝트별 쓰기 경계, 최소 권한과 공개 안전 정책을 적용할 수 있는가?
6. 필요한 경우 오프라인·로컬 환경이나 최소 fallback으로 핵심 record에 접근할 수 있는가?
7. license가 사용·배포 목적에 맞고 유지보수 중단 뒤에도 migration할 수 있는가?
8. 도입·운영·교체 비용이 최소 직접 구현보다 합리적인가?

기능이 많다는 이유만으로 복잡한 시스템을 도입하지 않는다. 후보가 일부 capability만 충족하면 기존 구현과
부족한 projection·index만 조합한다. 종속 위험이 크면 reference로만 남기고 공개 export를 사용하는 대체
계층을 유지한다.

## 구현 전략

| strategy | 사용 조건 |
|---|---|
| `native` | repository의 공개 형식과 기존 하네스 규칙만으로 요구사항 충족 |
| `adapter` | 하나의 등록 adapter가 요구사항과 fallback을 충족 |
| `hybrid` | 외부 구현과 하네스의 최소 projection·index를 조합 |
| `custom-minimal` | 적합한 구현이 없거나 하네스 고유 제어 계층만 직접 구현 |

모든 전략의 `selection_policy`는 `reuse-first`다. 이는 외부 구현을 우선 채택한다는 뜻이 아니라, 직접 구현
전에 기존 지식과 구현을 조사하고 비교 근거를 남긴다는 뜻이다.

## Storage Adapter API

adapter는 외부 시스템의 고유 API를 하네스 canon에 노출하지 않고 다음 공통 동작의 지원 수준을 선언한다.

| 동작 | 계약 |
|---|---|
| `write` | 표준 record를 대상 표현으로 기록하고 source identity 반환 |
| `query` | 지원 query mode, 잘린 결과·손실·비용을 함께 반환 |
| `trace` | 결과에서 source와 transformation lineage로 복귀 |
| `export` | 공개·이식 가능한 형식으로 반출 |
| `rebuild` | source에서 projection·index 재생성 |
| `health` | 가용성·버전·성능 저하와 마지막 성공 확인 |

각 동작은 `supported`, `degraded`, `unsupported` 중 하나와 제한을 선언한다. `unsupported`를 공통 계층에서
성공처럼 보이게 만들지 않는다. 형식 정본은 `schemas/storage-adapter.schema.json`, active 등록부는
`storage/adapters/registry.json`이다.

## 실행 위치와 broker 경계

adapter는 미래에 `embedded`, `local-service`, `remote-shared` 중 하나로 실행할 수 있지만 실행 위치가
정본 역할을 바꾸지 않는다. 현재 registry는 실행 프로세스를 시작하거나 관리하지 않으며 active adapter도
없다. 실행 계층을 도입할 때는 embedded를 우선하고 실제 동시성·격리 요구가 있는 공간만 local service로
분리한다.

여러 에이전트의 동시 쓰기 조정이 필요하면 각 agent가 adapter와 DB 파일을 직접 수정하지 않고 Local
Storage Broker를 통하게 할 수 있다. broker는 policy·schema·common ID·provenance와 파생 갱신을 조정하지만
adapter의 export·rebuild·health 책임이나 파일 기반 fallback을 대신하지 않는다. 단계와 도입 조건은
`docs/local-storage-runtime.md`를 따른다.

## 외부 결과와 lineage

외부 시스템의 결과는 adapter를 거쳐도 원본이 되지 않는다.

```text
External system
  → adapter query
  → 표준 representation
  → source·query·version·transformation·loss
  → Cross-Space Catalog
```

외부 결과에는 최소한 시스템의 공개 안전한 ID와 version, 조회·생성 UTC 시각, 실행 query의 안전한 식별자,
결과 ref, 변환, 알려진 손실, 재조회 방법을 남긴다. 원시 query나 결과 본문이 비공개 정보를 포함하면
catalog에 복사하지 않고 안전한 opaque ID만 사용한다.

## Portability와 장애

active space는 `export_formats`, `vendor_lock_in`, `exit_plan`을 선언한다. 원칙적으로 vendor lock-in은
금지하며 예외는 사용자 승인과 migration·복구 증거가 있을 때만 `exception-approved`로 기록한다.

외부 adapter가 중단됐을 때 fallback은 다음을 명시한다.

- 사용할 대체 adapter 또는 공개 형식 직접 접근
- `full`, `read-only`, `export-only`, `unavailable` 중 남는 data access
- 사용할 수 없거나 느려지는 query mode
- 손실·정확도·성능 저하

evidence·record space는 fallback에서 핵심 자료 접근이 `unavailable`이 되면 안 된다. 외부 index와
projection은 삭제 후 source에서 다시 만들 수 있어야 한다.

## 예측·계획·평가의 조합

Prediction, Plan, Outcome, Evaluation은 처음부터 별도 저장 엔진 종류로 고정하지 않고 목적별 space를
조합하는 record pattern으로 다룬다.

- Prediction: 대상, 생성 시각, 목표 시각·범위, 확률·예상 범위, 가정, 모델·버전, evidence lineage
- Plan: 목표, 제약, 선택 행동, 예상 효과, 책임 주체, 승인·실행 상태
- Outcome: 실제 결과, 관찰 시각, plan 개입 여부, evidence
- Evaluation: prediction·plan과 outcome 연결, 오차·성과, 평가 방법·version, 보정 판단

통계 모델·시계열 시스템·시뮬레이터·workflow engine·constraint solver는 이 표준 record와 adapter 계약을
충족할 때 연결할 수 있다. 구현을 교체해도 과거 prediction·plan·outcome·evaluation record와 lineage는
유지한다. 실제 사용 사례가 생기기 전에는 새 active kind나 외부 시스템을 등록하지 않는다.

## 채택 절차

1. space requirement와 미충족 query를 기록한다.
2. `research/` reference와 새 후보를 조사한다.
3. 실제 규모의 공개 안전 fixture로 capability·손실·비용·license·health를 평가한다.
4. adapter definition과 export·fallback·migration을 구현한다.
5. proposal 승인 뒤 adapter registry와 space definition을 같은 변경에서 갱신한다.
6. `operator:storage-spaces audit`, adapter fixture, 장애·복구와 재생성 검증을 통과한다.
7. `changed/`에 영향 프로젝트와 degraded query mode를 알린다.

직접 구현을 선택해도 후보 조사와 기각 근거를 생략하지 않는다. 단, 보안상 조사 자체가 위험하거나 요구가
하네스의 작은 제어 기능에만 한정되면 그 이유와 최소 범위를 기록한다.
