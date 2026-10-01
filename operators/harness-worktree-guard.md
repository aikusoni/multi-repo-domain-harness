---
operator_id: operator:harness-worktree-guard
owner: harness
implementation: operators/harness-worktree-guard.py
affected_projects:
  - harness
related_initiatives: []
---

# Operator: harness-worktree-guard

## 목적과 책임

하네스 저장소의 현재 checkout이 Git metadata 기준 primary인지 판정하고, linked worktree에서 가변 작업을
non-zero로 차단한다. 등록된 linked worktree는 경로를 노출하지 않고 잔존 수만 감사한다. worktree 생성·
삭제·정리, 파일 변경, branch 이동, commit과 원격 작업은 수행하지 않는다.

primary 전용 정책은 여러 하네스 세션이 하나의 working directory에서 request·changed·task·journal과
미커밋 변경을 다시 읽게 하는 공유 가시성 경계다. primary 판정은 물리적 checkout을 뜻하며 `main` 같은
정본 branch에서 직접 작업하라는 뜻이 아니다.

이 operator는 `project-id: harness` 전용이다. 참여 프로젝트와 제품 저장소의 worktree 정책을 검사하거나
바꾸지 않는다. 스크립트는 fixture와 진단을 위해 임의 repository 경로를 받을 수 있지만, 대상이 harness가
아니면 결과에 정책 효력이 없으며 그 프로젝트의 worktree 규칙을 우선한다.

## 실행 조건

- 자동 트리거: 하네스 작업 시작·재개와 stage·commit·push 직전의 `check`
- 수동 호출:
  - 위치 게이트: `python3 operators/harness-worktree-guard.py check [repository]`
  - 잔존 상태 감사: `python3 operators/harness-worktree-guard.py audit [repository]`
- Git hook 연계: 사용자가 별도 설치한 하네스 pre-commit·pre-push hook은 다른 검사보다 먼저 `check`를
  호출할 수 있다. 이 저장소는 hook 설치나 `core.hooksPath` 설정을 자동 수행하지 않는다.
- 스케줄 시간대: 해당 없음. 시각 기반 상태를 만들지 않음
- 중단 조건: 대상이 Git worktree가 아니거나 Git dir·common dir·worktree registry를 읽을 수 없음

## 입력 계약

- 명령: `check` 또는 `audit`
- 선택적 저장소 경로: 기본값은 현재 디렉터리
- Git CLI가 제공하는 absolute Git dir, absolute common dir와 worktree registry

경로 이름, 현재 branch 이름이나 디렉터리 관례로 primary 여부를 추측하지 않는다. absolute Git dir와
absolute common dir가 같으면 primary, 다르면 linked로 판정한다. 호출 환경의 `GIT_DIR`, `GIT_WORK_TREE`,
`GIT_COMMON_DIR`는 위치 판정을 바꿀 수 없도록 제거한 뒤 metadata를 조회하고,
`--is-inside-work-tree`의 값이 정확히 `true`인 대상만 허용한다.

## 출력과 성공 판정

### check

- 현재 primary이고 등록 linked worktree가 없으면 `OK harness-worktree-guard`, exit code `0`
- 현재 primary이고 cutover 이전 것을 포함한 linked worktree가 남아 있으면 경로 없이
  `ATTENTION harness-worktree-guard`와 `linked_registered=<count>`, exit code `0`
- 현재 linked이면 `BLOCKED harness-worktree-guard`, exit code `1`
- 입력·Git metadata 오류는 `ERROR harness-worktree-guard`와 `H400`, exit code `2`

`ATTENTION`은 현재 checkout의 가변 작업 위치 게이트는 통과했지만 별도 안전 정리가 남았다는 뜻이다.
linked worktree 존재를 새 작업에 사용해도 된다는 뜻이 아니다.

### audit

- 현재 checkout이 linked이면 `H401`
- 하나 이상의 registered linked worktree가 있으면 경로 없이 수만 포함한 `H402`
- finding이 없으면 `OK`, 있으면 `ATTENTION`; audit 자체를 완료하면 모두 exit code `0`
- Git metadata 오류는 `H400`과 exit code `2`

## 권한과 부작용

- 읽기 범위: 대상 저장소의 Git dir, common dir와 worktree registry
- 쓰기 범위: 없음
- 외부 변경과 네트워크: 없음
- 출력 금지: checkout·Git dir·common dir의 절대경로, remote URL, 파일 내용
- 사용자 승인 필요 조건: 없음. 단, 발견한 worktree의 제거·clean·reset·prune은 이 operator 범위가 아니며
  소유·보존 상태를 확인한 별도 명시적 사용자 결정이 필요함

## 실행 안전성

- 멱등성: 같은 Git metadata와 registry에서 같은 판정
- 동시 실행: 읽기 전용이라 병렬 호출 가능. 결과 직후 registry가 바뀔 수 있으므로 가변 경계마다 재실행
- 타임아웃: 로컬 Git metadata 조회가 비정상적으로 오래 걸리면 호출자가 제한
- 재시도: metadata 오류 원인을 확인한 뒤 1회. linked 판정을 재시도로 우회하지 않음

## 실패와 복구

- `H400`: 대상 또는 Git metadata 오류. 올바른 하네스 checkout에서 다시 확인
- `H401`: 현재 위치가 linked. 변경하지 말고 primary checkout의 동일 task로 전환한 뒤 `INDEX.md`와
  동적 상태를 다시 읽음
- `H402`: registered linked worktree 잔존. 새 작업에 사용하지 않고, dirty·미보존 commit·소유자를
  확인한 별도 정리 작업에서만 제거
- issue 승격 조건: linked checkout에서 가변 작업이 반복되거나 guard가 Git metadata를 잘못 분류함

## 실행 증거

- 로그 위치: 표준 출력과 호출 task·journal의 검증 결과
- 보존 기간: 장기 실행 로그 없음. 정책 변경·복구 판단만 하네스 기록에 보존
- 민감정보 제거: 위치는 `primary|linked`, 잔존 상태는 count로만 출력

## 검증

- 임시 Git 저장소의 primary checkout에서 `check`가 exit code `0`인지 확인
- fixture linked worktree에서 `check`가 `BLOCKED`와 exit code `1`인지 확인
- primary에 linked worktree가 남아 있을 때 `check`가 `ATTENTION`이지만 exit code `0`인지 확인
- linked 상태의 환경변수 오염이 판정을 우회하지 못하고, non-Git·`.git` 디렉터리가 `H400`인지 확인
- `audit`가 `H401|H402`와 count만 출력하고 fixture 절대경로를 노출하지 않으며 dirty 상태를 바꾸지
  않는지 확인
- fixture linked worktree 제거 뒤 primary `audit`가 `OK`인지 확인

fixture가 만드는 linked worktree는 임시 일회용 Git 저장소 안에서 판정기를 검증하기 위한 테스트 대상이며,
하네스 저장소에 linked worktree를 만드는 운영 예외가 아니다.

## 적용 한계

- 저장소 안의 guard는 데스크톱 앱이나 자동화가 작업 환경을 만들기 **전**에는 실행될 수 없다. Git에는
  worktree 생성 직전 전용 hook이 없으므로 task 생성 단계에서 하네스를 local/direct primary checkout으로
  선택해야 한다. 잘못 생성된 linked 환경에서는 bootstrap의 절차상 `check`가 작업 중단을 요구하며,
  사용자가 hook을 별도 설치·연결한 경우에만 pre-commit·pre-push에서도 기술적으로 차단한다.
- 별도 `git clone`은 자기 Git dir와 common dir가 같으므로 이 operator에서 primary로 판정된다. 그러나
  working directory를 공유하지 않아 primary-only 정책의 가시성 목적을 충족하지 않는다. 모든 로컬 세션을
  동일한 configured primary 경로로 연결하는 것은 bootstrap 설정 계약이며 이 operator만으로 강제되지 않는다.

## 변경 호환성

primary 판정식, `check|audit`, 출력 접두사 `OK|ATTENTION|BLOCKED|ERROR`, 검사 코드 `H400|H401|H402`와
exit code는 공개 계약이다. 판정·차단 범위를 바꾸면 `INDEX.md`, `docs/change-promotion.md`, fixture와
`changed/`를 같은 변경에서 갱신한다.
