# 공유 하네스 가시성과 실시간 작업 신호

**VALIDITY:** ACTIVE

## 2026-09-02 08:34:21 UTC · 착수

**SESSION-COMM:** 2026-09-02 08:34:21 UTC · observe · peer: none-in-observable-scope · reason: INDEX와 공유 상태 canon 수정 전 소유 확인

- 하네스의 primary checkout 전용 정책은 여러 세션이 동일한 working directory의 미커밋 변경까지 즉시
  관찰하도록 만드는 공유 가시성 계약으로 해석해야 한다.
- primary checkout은 물리적 checkout 위치이고 `main` 같은 정본 branch는 승인된 Git 이력의 역할이다.
  두 개념을 같게 만들거나 하네스 변경을 `main`에 직접 commit하도록 요구하지 않는다.
- 세션 간 직접 메시지는 빠르지만 비정본·휘발성이고 통신 예산이 있다. request·changed·task·journal은
  durable record지만 실시간 progress stream은 아니다.
- 현재 `space:harness-events`의 위치는 issue·changed·feedback이며 실시간 작업 신호 계층이나 cursor를
  제공하지 않는다. append 작업 신호는 실제 병목과 누락이 관찰되기 전까지 exploration으로만 다룬다.

## 착수 예측

- 현재 정책의 방향은 유지하고 목적·용어·채널 역할만 보강하면 worktree를 다시 허용하지 않고도 사용자가
  설명한 공유 문제를 정확히 표현할 수 있다.
- 실시간 신호는 세션별 append stream과 로컬 cursor로 분리해야 단일 공유 파일 덮어쓰기와 ack 경쟁을
  피할 수 있다.

## 2026-09-02 23:56:18 UTC · 검토와 완료

**SESSION-COMM:** 2026-09-02 08:34:21 UTC · outbound · peer: harness@worktree-docs-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:1/10 · prompt-in:- · 공유 가시성 canon 정합 읽기 전용 리뷰 요청 · ref:docs/change-promotion.md

**SESSION-COMM:** 2026-09-02 08:34:21 UTC · outbound · peer: harness@worktree-guard-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:2/10 · prompt-in:- · append 신호 동시성·예산 경계 읽기 전용 리뷰 요청 · ref:explorations/shared-harness-live-signals.md

**SESSION-COMM:** 2026-09-02 08:48:57 UTC · inbound · peer: harness@worktree-guard-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:3/10 · prompt-in:1/5 · 행동 유발 신호의 통신 예산 계승과 lease·cursor 동시성 보강 제안 채택 · ref:explorations/shared-harness-live-signals.md

**SESSION-COMM:** 2026-09-02 08:48:57 UTC · inbound · peer: harness@worktree-docs-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:4/10 · prompt-in:2/5 · 동일 configured path·공유 Git 상태 단일 writer·선택적 hook 경계 제안 채택 · ref:INDEX.md

**SESSION-COMM:** 2026-09-02 08:54:01 UTC · outbound · peer: harness@worktree-docs-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:5/10 · prompt-in:- · 보강된 전체 diff 최종 읽기 전용 리뷰 요청 · ref:docs/session-coordination.md

**SESSION-COMM:** 2026-09-02 08:54:01 UTC · outbound · peer: harness@worktree-guard-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:6/10 · prompt-in:- · 공개 위험·guard 보장 범위 최종 읽기 전용 리뷰 요청 · ref:operators/harness-worktree-guard.md

**SESSION-COMM:** 2026-09-02 23:56:18 UTC · inbound · peer: harness@worktree-guard-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:7/10 · prompt-in:3/5 · 최종 공개 위험·guard 계약 리뷰 PASS · ref:operators/harness-worktree-guard.md

**SESSION-COMM:** 2026-09-02 23:56:18 UTC · inbound · peer: harness@worktree-docs-review · tx:shared-harness-visibility-20260902T083421Z · tx-count:8/10 · prompt-in:4/5 · r0018 changed 기록 복원·r0019 별도 append와 bootstrap 표현 보정 제안 채택, 회신 불요 · ref:changed/status-2026-09-02.md

- 착수 예측과 같이 primary-only 방향은 유지하면서 공유 가시성 목적, primary checkout과 정본 branch의
  구분, 통신 계층만 보강했다. 별도 clone도 동일 경로 공유를 충족하지 않는다는 추가 경계가 확인됐다.
- 실시간 작업 신호는 active 기능으로 만들지 않았다. 후보 계약에는 행동 유발 신호의 기존 통신 예산 계승,
  단일 writer 또는 broker 직렬화, 원자 cursor, replay·dedup과 lease fencing 필요성을 기록했다.
- 같은 날 규칙이 r0018과 r0019로 연속 갱신됐으므로 `changed/`에서 기존 r0018 항목을 유지하고 r0019를 새
  ID로 append했다. 공개 위험 검색에서는 로컬 절대경로·조직 내부 정보·인증정보·개인정보가 발견되지 않았다.
