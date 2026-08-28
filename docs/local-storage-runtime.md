# 로컬 다중 저장공간 실행 계층

> **상태:** 장기 개선 후보
> **현재 구현:** 파일·Git record와 재생성 가능한 파일 index만 사용하며 Local Storage Broker는 없다.
> **도입 게이트:** 실제 저장·검색·문맥 처리 병목의 반복 측정과 별도 proposal 승인이 필요하다.

## 목적

현재의 파일 기반 하네스는 사람이 읽고 검토하며 Git으로 변경을 추적하기 쉬운 안정적인 정본이다. 데이터
규모, 에이전트 수와 질의 종류가 늘어나 파일 탐색·구조 해석·문맥 조립 비용이 주요 병목이 되면, 여러 저장
소프트웨어를 공통 인터페이스로 조합하는 로컬 실행 계층을 추가할 수 있다.

이 계층은 정본을 대체하지 않는다. SQL·graph·time-series·semantic index와 작업 뷰는 공유 record에서
재생성할 수 있는 projection·index·cache이며, 실패하면 파일 기반 조회로 복귀한다.

```text
Agents and users
  → Harness Storage API
  → Local Storage Broker
      ├─ policy·permission
      ├─ schema·common ID
      ├─ write coordination
      ├─ Query Planner
      ├─ provenance
      └─ Context Composer
  → Local Storage Spaces
      ├─ table·relation·field
      ├─ event·time-series·semantic
      ├─ prediction·plan·residual
      └─ source file
```

## 현재 경계와 장기 목표

현재 단계에서 `operator:storage-spaces`는 control-plane 파일의 정합, 결정적 index와 제한된 조회 계획만
제공한다. daemon, background watcher, database process, 동시 쓰기 broker 또는 자동 context injection을
실행하지 않는다.

장기 실행 계층의 목표는 다음과 같다.

- 반복적인 전체 파일 읽기와 자연어 재구조화 비용 감소
- 변경된 record만 반영하는 증분 index
- 여러 작업에서 검증된 분석 결과와 lineage 재사용
- 질문 유형에 맞는 Storage Space 선택과 제한된 context 조립
- 민감한 source를 로컬에 유지하면서 파생 결과만 안전하게 사용
- 저장 제품 교체, 공개 export, rebuild와 파일 기반 fallback 보장

## 구성 요소 책임

### Harness Storage API

호출자가 특정 제품 API에 결합되지 않도록 `observe`, `write`, `query`, `trace`, `compose_context`,
`snapshot`, `rebuild`, `validate`, `health` 같은 상위 동작을 제공할 수 있다. 실제 adapter 동작과 지원 수준은
`docs/storage-adapters.md`의 계약을 따른다.

### Local Storage Broker

여러 에이전트가 같은 로컬 DB와 파생 파일을 직접 동시에 수정하지 않도록 단일 로컬 중개 계층을 둘 수
있다. broker의 책임 후보는 쓰기 직렬화, 정책·권한 검사, schema 검증, 공통 ID와 provenance 기록, 파생
공간 갱신, query planning과 context composition이다.

broker는 record의 owner나 새 Source of Truth가 아니다. broker 상태가 사라져도 공유 record와 transformation
metadata로 필요한 projection을 다시 만들 수 있어야 한다.

### Local Storage Spaces

공간은 요구에 따라 선택한다. 모든 유형을 함께 실행하지 않는다.

| 공간 후보 | 적합한 질의 | 정본 경계 |
|---|---|---|
| table/SQL | 정확한 상태·속성·수치·제약·집계 | record 또는 projection 여부를 definition에 명시 |
| relation/graph | 의존성·영향·경로 | source relation과 transformation으로 재구성 |
| field/canvas | 미확정 관계·영역·중첩·작업 가설 | 작업 projection이며 승인 사실이 아님 |
| event | 관찰·변경·결정의 순서 | append-only record 또는 source event projection |
| time-series | 수치·추세·시간 범위 | source와 sampling·aggregation loss를 추적 |
| semantic/vector | 식별자를 모를 때 유사 자료 발견 | 보조 index이며 사실 판정에 단독 사용 금지 |
| prediction/plan | 조건부 예측·계획·결과·평가 | 표준 record와 evidence lineage 유지 |
| residual | 미분류·충돌·예상 밖 신호 | 억지 분류 없이 보존하고 재검토 |
| source file | 사람 검토 가능한 원본 record | Git과 파일 소유권이 정본 |

## 실행 방식 선택

Storage Space Definition은 필요가 검증됐을 때 다음 실행 방식 중 하나를 선택할 수 있다.

| 방식 | 사용 조건 | 기본 경계 |
|---|---|---|
| embedded | 단일 로컬 프로세스와 작은 규모로 충분 | 초기 확장의 우선 방식 |
| local-service | 동시성·격리·수명 관리가 실제로 필요 | broker를 통한 접근과 health 필요 |
| remote-shared | 머신 간 공유가 이점과 위험을 상회 | 별도 권한·동기화·오프라인·충돌 승인 필요 |

초기 확장은 embedded를 우선하고, 측정된 규모·동시성 요구가 있는 공간만 local service로 분리한다.
remote/shared는 로컬 계층과 별개의 보안·운영 결정이며 자동 승격하지 않는다.

## Git record와 로컬 상태 분리

Git으로 공유할 정본은 다음과 같다.

- Storage Space Definition, 정책, schema와 adapter 계약
- 사람이 검토 가능한 원본 record와 중요한 event
- transformation·migration·rebuild metadata
- 공개 안전한 provenance와 portable export 규칙

로컬에서 재생성할 수 있는 상태는 다음과 같다.

- SQL 상태 projection, graph·semantic index와 time-series projection
- cache, 작업 memory, field/canvas 파생 뷰
- query 통계와 재생성 가능한 검색 자료

파생 database 파일 자체를 Git으로 공유하지 않는다. 공유 record와 event를 내려받은 각 머신이 등록된
transformation과 adapter version으로 필요한 projection을 재생성하는 방식을 우선한다.

## 도입 조건과 증거

다음 문제가 반복되고 작업 시간·latency·token·중복률 같은 측정값으로 주요 비용임이 확인될 때 proposal을
검토한다.

- 같은 파일·record의 반복 전체 읽기가 지속됨
- 검색과 context 조립이 작업 시간 또는 입력 token의 주요 부분을 차지함
- 전체 scan 비용과 index 최신성 지연이 합의한 한계를 넘음
- 여러 에이전트가 같은 분석을 반복하며 재사용할 lineage가 필요함
- relation·time-series·field 질의를 text search로 신뢰성 있게 처리하기 어려움
- 파일 기반 동시 쓰기나 파생 표현 일관성 문제가 반복됨
- prediction·plan·outcome·evaluation을 장기간 비교할 필요가 생김

proposal에는 기준 측정, 목표, 최소 공간, 실행 방식, adapter 후보, 공개 안전성, migration, rollback,
운영·교체 비용과 성공 판정을 포함한다. 명확한 병목 없이 편의나 가능성만으로 daemon·DB·broker를 만들지
않는다.

## 단계적 검토 순서

1. **Local catalog:** 공통 ID·provenance, 파일 index, 증분 변경 감지와 embedded table 실험
2. **Query Planner·Context Composer:** 질문 유형별 공간 선택, 구조화 결과와 token 예산
3. **전문 adapter:** graph·time-series·semantic·field·prediction 중 실측 병목이 있는 공간
4. **Local Storage Broker:** 다중 에이전트 동시 접근, 정책·권한, 쓰기 조정과 파생 일관성
5. **선택적 공유:** 머신 간 event 동기화, 오프라인 병합, 충돌 처리와 팀 권한

각 단계는 독립 proposal과 검증을 거친다. 뒤 단계의 가능성이 앞 단계 전체 구현의 근거가 되지 않는다.

## 비목표와 복구 기준

- 처음부터 분산 데이터 플랫폼을 구축하지 않는다.
- 모든 공간을 하나의 데이터 모델로 통합하지 않는다.
- 전문 엔진 기능을 하네스에서 다시 구현하지 않는다.
- projection·index·cache를 새로운 Source of Truth로 만들지 않는다.
- 성능·품질 측정 없이 파일 기반 구조를 제거하지 않는다.
- 특정 상용 제품이나 독점 형식을 필수 요소로 두지 않는다.

채택된 계층은 전체 파일 읽기, 검색·context latency, 입력 token과 중복 분석을 의미 있게 줄이고, 관련 정보
검색 정확도와 lineage 추적을 유지해야 한다. adapter 또는 broker 실패 시 중요한 record는 파일 기반 경로로
읽을 수 있어야 하며 모든 파생 결과는 rebuild 또는 안전한 폐기가 가능해야 한다.
