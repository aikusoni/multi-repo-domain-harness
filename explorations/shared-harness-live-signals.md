# 공유 하네스 실시간 작업 신호

**상태:** OPEN
**시작:** 2026-09-02 08:34:21 UTC
**최종 갱신:** 2026-09-02 08:48:57 UTC
**정본 여부:** 비정본 exploration

## 질문

하네스의 여러 세션이 primary working directory를 공유하면서도 직접 메시지의 휘발성과 통신 예산,
공식 record의 상대적으로 무거운 기록 비용 사이에서 작업 소유·checkpoint·발견·handoff를 빠르고 안전하게
공유하려면 별도의 append 작업 신호 계층이 필요한가?

## 현재 종합

- 현행 정본은 하네스 가변 작업을 primary checkout에 직렬화한다. 이는 linked worktree 사이에서 최신
  파일과 미커밋 기록이 보이지 않는 문제를 먼저 제거하는 단순한 기본값이다.
- primary checkout을 함께 봐도 이미 구성된 세션 문맥은 자동 갱신되지 않으므로 각 세션은 판단 전에
  관련 파일과 Git 상태를 다시 읽어야 한다.
- 직접 세션 메시지는 소유·충돌 조정에 적합하지만 비정본·휘발성이고 tx 총 10건과 프롬프트 후 수신 5건
  제한이 있다.
- request·changed·task·journal은 세션 이후에도 남아야 하는 정보를 보존하지만 모든 진행 상황을 실시간으로
  싣는 stream은 아니다.
- 현재 active `space:harness-events`는 issue·changed·feedback의 durable history다. 실시간 작업 신호,
  watcher와 소비자 cursor는 구현돼 있지 않다.

따라서 실시간 신호 계층은 현재 기능으로 간주하지 않는다. 공유 누락·중복 분석·소유권 대기·상태 재탐색이
반복 측정될 때만 최소 범위 proposal로 승격한다.

## 서로 다른 관점

### Primary checkout과 직접 통신 유지

구성 요소가 가장 적고 모든 세션이 같은 파일을 본다. 비append 파일은 한 writer가 소유하고 짧은 handoff는
직접 메시지로 해결한다. 동시 작업량이 작다면 별도 event stream보다 이해·감사·복구가 쉽다.

### 세션별 append 작업 신호 추가

의미 있는 상태 전환을 세션별 stream에 append하면 polling 메시지와 중복 조사를 줄일 수 있다. 단일 공유
파일에 여러 writer가 쓰지 않고, 소비자별 cursor를 event 본문과 분리해야 한다. 신호는 정본이 아니므로
중요한 결과는 기존 durable record로 승격해야 한다.

### Linked worktree와 중앙 broker 허용

중앙 event log만 공유해도 각 worktree의 실제 파일·index·미커밋 변경은 동기화되지 않는다. linked 작업을
허용하려면 모든 하네스 쓰기를 중앙 broker가 primary record에 반영하고 충돌·read-after-write·실패 복구를
보장해야 한다. 현재 필요에 비해 복잡하며 primary-only 정책을 대체하지 않는다.

## 후보 event 계약 [미검증]

실제 proposal에서는 최소한 다음을 검증할 수 있다.

- event 종류: `ownership-acquired`, `checkpoint`, `finding`, `blocked`, `handoff`, `ownership-released`
- 필수 필드: 안정 event id, UTC 시각, project·task 또는 operator, 공개 안전한 session alias, event kind,
  상대 경로·commit·record 같은 산출물 포인터. 행동 유발 signal은 기존 tx id와 tx·수신 카운터도 포함
- 선택 필드: 기대 종료 조건, 선행 event, 대체·정정 대상, 만료 조건
- 쓰기: 물리 stream 하나에는 세션별 단일 writer만 쓰거나 broker가 모든 쓰기를 직렬화한다. operator는
  한 event를 원자적으로 추가하고 read-after-write로 확인
- 읽기: 소비자·stream generation별 단조 sequence cursor로 새 event만 읽는다. event 처리가 성공한 뒤
  cursor를 원자적으로 전진하고, crash 뒤 replay와 안정 event id 기반 중복 제거를 지원하며 공유 event나
  다른 소비자의 ack를 수정하지 않음
- 정정: 과거 event를 고치지 않고 새 correction·superseding event를 append
- 승격: 계약·현재 상태·후속 작업에 영향을 주면 request·changed·task·journal·decision 중 맞는 정본에 반영
- 보존: 일시적 소유·progress 신호는 만료·압축할 수 있지만 승격 포인터와 실패 증거는 추적 가능하게 유지

모든 도구 호출, 토큰 단위 진행, chain-of-thought나 비공개 원문을 기록하지 않는다. 새 값이 없는 heartbeat와
단순 수신 확인도 event로 부풀리지 않는다.

`ownership-acquired`는 소유권을 부여하는 명령이 아니다. 기존 단일-writer 조정 절차가 성공했거나 broker가
만료·fencing token을 가진 lease를 부여한 뒤 그 사실을 기록하는 event다. event append만 성공하고 실제
조정·lease가 실패했다면 소유권이 없다.

특정 세션을 대상으로 하거나 다른 세션의 새 가변 행동을 유발하는 signal은 파일·watcher·broker 중 어떤
방식으로 전달해도 세션 간 메시지다. 기존 tx를 계승해 송·수신 예산에 포함하고 자동 signal은 tx나 카운터를
초기화하지 않는다. 수신자를 알 수 없는 broadcast는 예산을 계산할 수 없으므로 행동 유발 신호로 쓰지 않는다.

## 저장 위치 후보 [미검증]

아직 위치를 정하거나 새 디렉터리를 만들지 않는다.

- Git-ignored local runtime: 같은 머신·primary checkout에서는 빠르지만 clone 간 공유와 장기 복구가 안 됨
- Git tracked append record: 이식성과 감사가 쉽지만 작업 트리·commit noise와 동시 쓰기 비용이 큼
- Local broker와 event store: 원자 쓰기·watcher·cursor에 유리하지만 프로세스 수명·복구·schema 운영 필요
- Remote/shared service: 머신 간 공유가 가능하지만 권한·비용·offline·동기화 계약이 먼저 필요

채택 전 proposal에서 Storage Space 역할, 실제 위치, schema, retention, 권한, 공개 안전성, adapter,
rebuild·fallback과 기존 record로의 승격 방식을 승인한다. 임의의 루트 폴더나 새 정본을 만들지 않는다.

## 도입 조건

- 같은 파일이나 상태를 여러 세션이 반복해서 재탐색함
- 직접 메시지가 progress polling 때문에 통신 예산에 반복해서 접근함
- primary checkout 소유권 대기가 작업 시간의 주요 부분이 됨
- handoff 누락·중복 분석·stale 문맥 사용이 반복 검증됨
- 현재 durable record에 모든 중간 진행을 넣어 기록 noise가 증가함

도입 후에는 새 정보 발견 지연, 중복 작업, 직접 메시지 수, 소유권 대기 시간, event 누락·중복과 durable
승격 성공률을 기준선과 비교한다. 효과가 없거나 운영 복잡성이 더 크면 제거하고 현재 파일·메시지 방식으로
복귀한다.

## 열린 질문

- live signal은 같은 primary checkout에만 공유할지, 여러 clone·machine까지 확장할지
- session alias와 수명 종료를 어떤 runtime evidence로 판정할지
- atomic append와 cursor 갱신을 파일만으로 보장할지 local broker가 필요한지
- stream generation·sequence, crash replay·중복 제거와 lease fencing을 어떤 fixture로 검증할지
- 어떤 event를 durable record로 자동 제안하고 어떤 판단은 사람에게 남길지
- 보존 기간과 compaction 뒤 provenance를 어떻게 유지할지

## 하네스에 미칠 수 있는 영향

- 직접 메시지를 상태 polling이 아니라 충돌·질문 중심으로 줄일 수 있다.
- 각 세션이 마지막으로 본 checkpoint를 구분해 stale 문맥을 더 빨리 발견할 수 있다.
- 잘못 설계하면 progress log가 새 Source of Truth가 되거나 통신 예산을 우회하고 공개 위험 정보를
  대량 축적할 수 있다.
- linked worktree를 다시 허용하는 근거로 사용하면 실제 파일 비가시성 문제가 남는다.

## 승격된 결과

- 공유 가시성을 primary checkout 전용 정책의 직접 목적으로 명시: `INDEX.md` 규칙 35
- primary checkout과 정본 branch의 개념 분리: `docs/change-promotion.md`, D-010
- 실시간 append 작업 신호 구현: 없음
