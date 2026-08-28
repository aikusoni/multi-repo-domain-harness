# 기억 신뢰성 및 인출 보장 계층

> **상태:** 장기 개선 후보
> **현재 구현:** INDEX 필독, 선택적 읽기, provenance·loss와 audit를 사용하며 자동 Memory Fault 계층은 없다.
> **도입 게이트:** 로컬 저장 실행 계층이 도입되거나 저장·검색 누락이 반복 문제로 검증돼야 한다.

## 목적

정보가 저장되어 있다는 사실은 필요한 작업에서 검색·선택·전달·사용된다는 뜻이 아니다.

```text
존재함 ≠ 검색 가능함 ≠ 검색됨 ≠ 문맥에 포함됨 ≠ 판단에 사용됨
```

장기적으로 하네스는 관찰부터 모델 사용까지의 경로를 단계별로 추적하고, 검색 결과 없음과 검색 미실행,
오래된 index와 권한 차단을 구분해야 한다. 이 계층은 저장 용량 확대가 아니라 인출 가능성·최신성·범위와
사용 여부의 신뢰성을 다룬다.

## 실패 단계

| 단계 | failure stage | 의미 |
|---|---|---|
| 관찰 | `observation` | 실제 source가 있지만 관찰하지 못함 |
| 저장 | `persistence` | 관찰했지만 durable record로 남기지 못함 |
| 색인 | `indexing` | source는 있지만 검색 index에 반영되지 않음 |
| 대상 해석 | `resolution` | ID·별칭·범위를 잘못 해석함 |
| 질의 계획 | `routing` | 부적합한 space나 query mode를 선택함 |
| 검색 | `retrieval` | 질의와 저장 표현이 맞지 않아 찾지 못함 |
| 선별 | `selection` | 찾았지만 순위·limit·threshold로 제외됨 |
| 문맥 조립 | `compression` | 중요한 정보가 요약·압축 중 제거됨 |
| 모델 사용 | `attention` | 전달된 정보를 판단에 사용하지 않음 |

`attention`은 모델 내부 상태를 추측해 단정하지 않는다. 최종 판단이 전달된 evidence를 사용했는지 관찰
가능한 trace와 결과 검증으로만 분류한다.

## Retrieval Status

검색 도구는 최소한 다음 상태를 구분해야 한다.

| status | 의미 |
|---|---|
| `found` | 조건에 맞는 결과를 찾음 |
| `not_found` | 명시한 범위를 실제 조회했지만 결과가 없음 |
| `not_searched` | 해당 공간 또는 범위를 조회하지 않음 |
| `not_indexed` | source는 있으나 index 반영을 확인하지 못함 |
| `inaccessible` | 권한·정책 때문에 조회할 수 없음 |
| `stale` | 최신성 한계를 넘음 |
| `ambiguous` | 대상이나 의도를 하나로 해석할 수 없음 |
| `partial` | 일부 공간·범위·시간만 조회함 |
| `failed` | 저장소·adapter·도구 실행이 실패함 |

`not_found` 이외 상태를 정보가 존재하지 않는다는 뜻으로 사용하지 않는다. 여러 공간의 상태가 다르면
전체 status는 숨기지 않고 `partial`, `stale` 또는 `failed`로 축약하고 공간별 상태를 함께 반환한다.

## 기억 동작의 다중 안전장치

저장과 인출을 모델의 자율적인 도구 호출 하나에 의존하지 않는다.

- **정책 기반 기록:** 중요한 사용자 결정, 작업 상태 변화, 실행 실패, 권한·정책 변경과 검증된 결과를
  현재 하네스 record 규칙에 따라 기록한다.
- **정책 기반 인출:** 루트·프로젝트 지침, 쓰기 경계, 현재 project·task, 선행 조건, 미해결 충돌과
  freshness 경고는 실행 계층이 도입되면 작업 유형에 맞게 자동 조립할 수 있다.
- **모델 주도 탐색:** 관련 object·relation, 과거 event·결정, 유사 사례, source evidence,
  prediction·plan·outcome·residual은 필요한 범위에서 능동 조회한다.

현재는 `INDEX.md`의 필독·재확인과 시작 절차가 정책 기반 인출의 사람 검토 가능한 최소 장치다. 미래
자동화가 생겨도 이 정본과 Git 경계를 우회하지 않는다.

## Memory Fault

Memory Fault는 현재 문맥에 필요한 정보가 없거나 신뢰할 수 없다는 **future runtime signal**이다. 일반적인
확신 부족을 모두 fault로 만들지 않으며 다음처럼 검증 가능한 조건과 필요한 정보 종류를 연결한다.

- 알려지지 않은 object ID 또는 모호한 별칭 참조
- freshness 한계를 넘은 상태를 현재 상태로 사용
- 쓰기·실행 전 필요한 권한과 정책이 문맥에 없음
- unresolved conflict나 선행 decision이 조회되지 않음
- prediction을 참조하는 plan에 해당 prediction·evidence가 없음
- source 확인이 필요한 판단에 projection·요약만 있음

fault가 발생하면 위험과 비용에 맞는 최소 범위를 추가 조회한다. 검색·rebuild·권한 확인으로 해결되지
않거나 사용자 결정이 필요한 경우 작업을 멈추고 상태·누락 범위·실행한 fallback을 보고한다. 전체 검색을
항상 실행하거나 fault를 근거로 권한을 확대하지 않는다.

## 검색 결과 계약

미래 query API는 결과 본문만이 아니라 다음 metadata를 반환해야 한다.

- 전체 status와 공간별 status
- searched space, not searched space와 이유
- project·ID·시간 범위와 query 해석
- source·index의 freshness와 version
- 결과, conflict·uncertainty와 evidence lineage
- limit·threshold·ranking과 잘린 결과
- 추정 coverage와 적용한 fallback

```yaml
query_id: query:current-impact
status: partial
as_of: 2026-08-28 05:48:09 UTC
searched_spaces: [objects, relations, events]
not_searched:
  - space: runtime
    reason: unavailable
freshness:
  objects: 2026-08-28 05:45:00 UTC
  relations: 2026-08-27 18:00:00 UTC
coverage:
  estimated: 0.72
warnings: [runtime-space-unavailable, relation-index-stale]
evidence: [evidence:issue-record]
```

coverage는 측정 방법이 없으면 숫자를 꾸며내지 않고 `unknown`으로 반환한다.

## 단계적 fallback 검색

한 번의 빠른 검색이 실패했다고 즉시 `not_found`로 끝내지 않는다.

```text
exact ID
  → structured property
  → relation·time
  → specialized index
  → semantic discovery
  → source file
  → incremental rebuild
  → bounded rescan
  → user confirmation
```

낮은 위험의 탐색은 앞 단계에서 끝낼 수 있다. 중요한 코드 변경은 관련 정책·relation·source evidence까지,
삭제·권한·승격 같은 되돌리기 어려운 작업은 최신 상태와 필요한 명시적 승인까지 확인한다. fallback은
query trace에 남기며 비용·시간·token budget을 넘으면 자동으로 확대하지 않는다.

## 저장 신뢰성 계약

저장 요청 접수와 durable 기록, index 반영을 구분한다.

| status | 의미 |
|---|---|
| `accepted` | 요청을 접수했으나 영구 기록은 미확인 |
| `persisted` | 기본 record space에 기록됨 |
| `durable` | 내구성 있는 기록과 read-after-write를 확인함 |
| `indexed` | 검색 index 반영을 확인함 |
| `projected` | 요구된 파생 공간까지 갱신됨 |
| `partial` | 일부 공간만 갱신됐거나 검증되지 않음 |
| `failed` | 기록 또는 검증 실패 |

중요한 record는 가능한 경우 read-after-write로 ID·source·version을 확인한다. projection 갱신 실패를 record
저장 성공과 혼동하지 않고 pending·stale 상태로 노출한다.

## Query Trace와 공간 간 일관성

Query Trace는 원 질문, 해석된 의도와 ID, 선택·제외한 공간, 실행 query, 상태, ranking·threshold, 제외
이유, fallback, 선택한 evidence, context compression과 최종 전달 표현을 재현 가능하게 연결한다. 비공개
query 본문은 기록하지 않고 안전한 opaque ID와 실행 위치의 source ref만 남긴다.

같은 정보의 여러 representation은 기준 source version, 마지막 갱신 UTC 시각, transformation·adapter
version, 처리 상태, rebuild 가능 여부와 알려진 지연을 갖는다. 일시적 불일치는 허용할 수 있으나
Cross-Space Catalog와 query 결과에서 숨기지 않는다.

## 평가와 실패 기록

도입 proposal은 정답을 아는 공개 안전 fixture로 다음을 검증한다.

- 중요한 record의 durable 저장, read-after-write와 실패 오보고 방지
- 필수 정책·현재 task의 자동 인출과 freshness 경고
- 여러 space를 잇는 relation 조회와 conflict 동시 반환
- `not_found`·`not_searched`·`stale`·`partial` 구분
- semantic 실패 뒤 source fallback과 Query Trace 재현
- context 압축 뒤 필수 정책·evidence 보존
- 모델이 인용한 정보가 실제 전달 결과에 존재하는지 확인

중요한 실패는 `memory-failure:<id>`로 failure stage, expected·actual, source와 query trace, recovery,
prevention을 기록할 수 있다. 반복 failure만 정책·planner·fallback·freshness·context composer 개선 근거로
사용하고, 성공률을 높이기 위해 query 범위나 비용을 숨기지 않는다.

## 단계적 도입과 성공 기준

1. **검색 상태·freshness:** `not_found`와 `not_searched` 구분, 공간별 범위와 최신성
2. **저장 확인·Query Trace:** durable 상태, read-after-write, 실행 query와 선택·제외 근거
3. **정책 기반 인출:** 지침·권한·task·conflict의 필수 context
4. **Memory Fault·fallback:** 누락·stale 탐지, 위험 기반 검색 깊이와 source 재검증
5. **신뢰성 평가:** 저장·인출·context fixture, 실패 단계 분류와 개선 효과 측정

채택 기준은 검색 미실행과 결과 없음의 구분, durable·indexed 상태 확인, 오래되거나 partial한 결과의 경고,
재현 가능한 실패 단계, 중요한 정보의 context 보존과 합리적인 latency·token 비용이다. 자동 계층 실패 시
현재의 INDEX·파일 기반 선택적 읽기로 복귀할 수 있어야 한다.
