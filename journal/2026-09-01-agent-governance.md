# 에이전트 거버넌스와 하네스 진화 검토

**VALIDITY:** ACTIVE

## 2026-09-01 07:35:10 UTC · 경계와 병렬 검토

**SESSION-COMM:** 2026-09-01 07:35:10 UTC · observe · peer: none-in-observable-scope · reason: 공통 canon 수정 전 소유 확인

**SESSION-COMM:** 2026-09-01 07:35:10 UTC · outbound · peer: harness@review-reference-a · tx:harness-guideline-review-20260901T073510Z · tx-count:1/10 · prompt-in:- · 참조 하네스의 범용 에이전트 규칙 읽기 전용 비교 · ref:docs/agent-execution.md

**SESSION-COMM:** 2026-09-01 07:35:10 UTC · outbound · peer: harness@review-reference-b · tx:harness-guideline-review-20260901T073510Z · tx-count:2/10 · prompt-in:- · 참조 하네스의 범용 에이전트 규칙 읽기 전용 비교 · ref:docs/agent-execution.md

**SESSION-COMM:** 2026-09-01 07:35:10 UTC · outbound · peer: harness@agent-governance-audit · tx:harness-guideline-review-20260901T073510Z · tx-count:3/10 · prompt-in:- · 현행 권한·위임·완료 계약 gap 분석 · ref:docs/agent-execution.md

**SESSION-COMM:** 2026-09-01 07:44:45 UTC · inbound · peer: harness@agent-governance-audit · tx:harness-guideline-review-20260901T073510Z · tx-count:4/10 · prompt-in:1/5 · 권한·비정본 입력·위임·재개·완료 증거 공백과 최소 구조 반환 · ref:docs/agent-execution.md

**SESSION-COMM:** 2026-09-01 07:44:45 UTC · inbound · peer: harness@review-reference-a · tx:harness-guideline-review-20260901T073510Z · tx-count:5/10 · prompt-in:2/5 · 독립 리뷰·사전 예측·검증 진실성·중단 인계 후보 반환 · ref:docs/agent-execution.md

**SESSION-COMM:** 2026-09-01 07:44:45 UTC · inbound · peer: harness@review-reference-b · tx:harness-guideline-review-20260901T073510Z · tx-count:6/10 · prompt-in:3/5 · 소급 경계·규칙 작성·위임 계약 후보 반환, 회신 불요 · ref:docs/harness-evolution.md

중앙 조정자 기준 tx 총량은 6/10, 이 세션의 사용자 프롬프트 이후 수신은 3/5다. worker 결과를 정본으로
직접 사용하지 않고 현행 문서와 공개 연구 원문을 대조했다.

## 2026-09-01 07:44:45 UTC · 공개 연구 확인

`research:evo-harness`에서 다음 공개 근거를 확인했다.

- 실행 결과를 바로 지침으로 쓰지 않고 lesson·trigger·evidence·scope_hint 후보로 만든다.
- 후보를 기존 harness와 비교해 add·merge·revise·skip한다.
- cross-task와 topic guidance를 분리하고 현재 task에 제한된 수만 선택한다.
- procedural task에는 도움이 컸지만 noise·과도한 구체화·solver 불일치가 성능을 떨어뜨릴 수 있다.
- self-generated feedback만으로는 충분하지 않았고 feedback granularity의 효과가 task마다 달랐다.

자동 evolver, 특정 모델 구성, 고정 skill 수와 대규모 benchmark 실행은 현재 운영 기본값으로 채택하지 않았다.

## 2026-09-01 07:44:45 UTC · 채택한 계약

- 요청 목표와 수정·외부 반영 권한을 분리하고 terminal persistence가 권한을 넓히지 않게 했다.
- 자료 안 지시문, 도구 출력과 하위 에이전트 결과를 정본·완료 증거로 자동 해석하지 않게 했다.
- 위임 계약과 read-only Reviewer를 정의하고 최종 검증·통합 책임을 상위 worker에 남겼다.
- 조사형·고위험 작업에만 사전 예측과 종료 대조를 적용해 작은 작업의 형식 부담을 피했다.
- timeout·문맥 유실 뒤 부분 부작용과 멱등성을 확인하고 완료 단계를 분리했다.
- feedback에 `instruction-ineffective`를 추가하고 Guidance Candidate 큐레이션·범위·회귀·cutover를 정의했다.
- bootstrap 파일은 INDEX 포인터만 유지하고 세부 규칙 복제로 인한 drift를 줄였다.

transcript 수집, 런타임별 강제 설정, 자동 canon 수정, 특정 worker 수와 세션별 중복 journal은 범용 기본
규칙으로 채택하지 않았다.

## 2026-09-01 08:04:39 UTC · 독립 구현 리뷰

**SESSION-COMM:** 2026-09-01 07:57:11 UTC · outbound · peer: harness@review-agent-governance-diff · tx:agent-governance-review-20260901T075711Z · tx-count:1/10 · prompt-in:- · 현재 미커밋 diff의 권한·위임·cutover·공개 안전성 읽기 전용 검토 · ref:docs/agent-execution.md

**SESSION-COMM:** 2026-09-01 08:04:39 UTC · inbound · peer: harness@review-agent-governance-diff · tx:agent-governance-review-20260901T075711Z · tx-count:2/10 · prompt-in:4/5 · 우선순위 모순·candidate 생명주기·cutover 검사·원자 경계·bootstrap 감사·changed 정합 finding 반환, 회신 불요 · ref:docs/harness-evolution.md

리뷰 결과를 직접 재현해 다음을 채택했다.

- 명확한 상위 지침 적용, 모호하거나 새 권한이 필요한 경우의 질문, 안전상 금지의 거절을 분리했다.
- Guidance Candidate의 안정 ID·위치·상태·병합·종결·재검토 생명주기를 `feedback/candidates/`에 정의했다.
- `instruction-ineffective` cutover를 operator와 음성 fixture로 강제했다.
- 5번째 세션 수신 뒤 원자 단위를 이미 실행 중인 분리 불가능한 호출 하나로 제한했다.
- bootstrap marker의 정상·누락·부정형을 감사 fixture로 구분했다.

## 2026-09-02 01:34:58 UTC · EvoHarness-RL 추가 검토

`research:evoharness-rl`에서 긴 작업의 외부 상태를 현재 판단·진행·재사용 경험의 기능으로 구분하고, 접근과
갱신이 실행 예산을 소비하므로 필요한 때 선택적으로 사용한다는 공개 연구 근거를 확인했다. 현재 하네스의
journal·task/request/issue·feedback/candidate/canon 경계를 이 기능 렌즈로 점검하되 새 통합 스키마로
옮기지 않았다. 강화학습 정책, 자동 망각·퇴출과 빈번한 회상만을 가치 판정으로 쓰는 방식은 채택하지 않았다.

## 2026-09-02 01:40:10 UTC · 최종 검증

- 독립 리뷰 finding 6건을 직접 재현하고 모두 보정했다.
- shell syntax, 전체 JSON, feedback·harness audit·storage·review branch fixture가 PASS였다.
- storage index를 재생성했고 audit은 active space 9개, 공개 research reference 8개, 오류 0건을 확인했다.
- harness audit은 현재 문서 39개와 bootstrap marker를 확인했고 feedback event 오류는 0건이었다.
- 큐레이션 상태는 미승격 journal 7/7로 `ATTENTION`이지만 비게이팅 신호이며 이번 작업으로 자동 큐레이션하지
  않았다.
- 추가된 줄과 신규 파일의 공개 위험 검토에서 로컬 절대경로·조직 내부 정보·인증정보·개인정보·비공개 URL을
  발견하지 않았다. 공개 URL은 등록한 arXiv 원문 두 건뿐이었다.
