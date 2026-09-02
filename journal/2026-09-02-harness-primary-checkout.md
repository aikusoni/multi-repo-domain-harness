# 하네스 primary checkout 전용 정책 검토

**VALIDITY:** ACTIVE

## 2026-09-02 06:15:21 UTC · 착수

**SESSION-COMM:** 2026-09-02 06:15:21 UTC · observe · peer: none-in-observable-scope · reason: INDEX·승격 canon 수정 전 소유 확인

- 현재 하네스 checkout은 Git dir와 common dir가 같은 primary checkout이다.
- 별도 linked worktree 하나에는 미커밋 변경이 남아 있다. 사용자 소유 상태로 보존하고 읽기 전용으로만
  구조를 확인했으며 수정·stage·commit·정리하지 않는다.
- 과거 미커밋안은 agent 변경을 linked worktree에만 허용하는 반대 방향이었다. 현행 정본이 아니므로
  복제하지 않고, 이번 사용자 요청대로 하네스에만 primary checkout 전용 예외를 설계한다.

## 착수 예측

- primary 판정은 `git-dir == git-common-dir`, linked 판정은 두 경로가 다름으로 안정적으로 구분될 것이다.
- 신규 사용 금지와 기존 dirty worktree 자동 삭제 금지를 분리하면 현재 정책 도입을 막지 않으면서 보존
  위험을 피할 수 있다.
- fixture에서 primary 허용·linked 차단·잔존 linked 감지가 갈리지 않으면 판정 계약을 재설계한다.

## 2026-09-02 06:32:54 UTC · 구현과 검증

**SESSION-COMM:** tx:harness-primary-checkout-20260902T061657Z · outbound 3, inbound 3, total 6/10 ·
peer: read-only operator reviewer, read-only canon reviewer · purpose: 판정 우회와 기존 문서 충돌을 독립 점검 ·
adopted: Git 환경변수 제거, `.git` 디렉터리 거부, 하네스 예외의 문서 범위, cleanup agenda 보류 ·
final_review: PASS

- `operator:harness-worktree-guard`는 absolute Git dir와 common dir를 비교해 현재 위치를 판정한다.
  `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR` 오염은 제거하고 `--is-inside-work-tree`가 정확히 `true`인
  대상만 허용한다.
- fixture에서 primary와 하위 디렉터리는 통과했고, linked 위치는 exit code 1로 차단됐다. primary에 linked
  worktree가 남은 상태는 `ATTENTION`과 exit code 0, linked audit는 `H401`·`H402`로 구분됐다.
- non-Git·`.git` 디렉터리는 exit code 2로 거부됐고, 환경변수 주입으로 linked 판정을 우회하지 못했다.
  audit 전후 dirty fixture 상태가 같고 출력에 fixture 절대경로가 없음을 확인했다.
- 현재 하네스는 예측대로 primary를 통과했고 registered linked worktree 1개를 경로 없이 경고했다. 기존
  linked worktree의 branch tip과 dirty 상태는 보존됐으며 수정·stage·commit·정리하지 않았다.
- `operator:harness-audit`, `operator:review-branch`, `operator:storage-spaces`와 모든 관련 fixture가
  성공했다.

## 예측 대조

- primary 허용·fixture linked 차단·현재 잔존 수 1 경고는 예측과 일치했다.
- 단순 Git metadata 비교만으로 충분하다는 예측에는 반례가 있었다. `.git` 디렉터리의 false/exit 0과
  Git 환경변수 오염이 우회점이어서 명시적 값 검사와 환경 정규화를 추가했다.
- 기존 linked 존재를 primary 작업 차단으로 오해하지 않도록 `ATTENTION`과 `BLOCKED`의 exit code를
  분리한 계약은 유지됐다.
