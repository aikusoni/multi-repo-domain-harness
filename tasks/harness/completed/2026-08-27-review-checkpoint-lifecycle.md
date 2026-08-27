---
task_id: t-6e8a2f14
project: harness
operator: operator:review-branch
opened: 2026-08-27 05:57:16 UTC
initiative:
related_issue:
related_request:
---

# 리뷰 체크포인트와 작업 브랜치 수명주기 보강

## 목표

리뷰를 선형 승격 단계가 아닌 어느 체크포인트에서나 생성할 수 있는 불변 스냅샷으로 정의하고, 작업용
worktree에는 임시 작업 브랜치만 연결하도록 브랜치 수명주기와 감사 장치를 보강한다.

## 완료 기준

- [x] 승격 경로와 리뷰 스냅샷의 관계가 선형 단계로 오해되지 않게 정의된다.
- [x] 작업용 worktree에 연결할 수 있는 브랜치와 금지되는 참조가 구분된다.
- [x] 임시 작업 브랜치 삭제 전 도달 가능성 확인과 종료 정리 기준이 정의된다.
- [x] review operator가 worktree에 연결된 review ref를 탐지한다.
- [x] 관련 fixture와 하네스 정합 검사를 통과한다.
- [x] UTC 표기와 공개 위험 정보 검토를 통과한다.

## 진행 기록

- 2026-08-27 05:57:16 UTC - 최근 확정 규칙과 현재 승격 canon·operator의 차이를 검토하고 별도 작업
  브랜치에서 구현을 시작했다.
- 2026-08-27 06:01:54 UTC - 승격·리뷰·worktree 수명 규칙과 operator 계약·fixture를 갱신하고 1차
  operator 검증을 통과했다.
- 2026-08-27 06:03:05 UTC - 전체 operator fixture, 상태 검사, 하네스 정합 감사와 diff 형식 검사를
  통과해 작업을 완료했다.

## 완료 결과

- 완료 내용: review를 승격 경로와 독립된 checkpoint 스냅샷으로 재정의하고, 작업용 worktree의 임시
  브랜치 수명·지속 가능한 ref 확인·detached 리뷰 절차를 추가했다. review operator에 명시적 source ref
  생성과 연결된 worktree 탐지 `R003`을 추가했다.
- 검증: `operators/tests/review-branch.sh`, `operators/tests/feedback-status.sh`,
  `operators/curation-status.sh`, `operators/feedback-status.sh`, `operators/harness-audit.sh`,
  `bash -n`, `git diff --check`, 공개 위험 키워드 검사
- 관련 커밋: 이 task를 completed로 이동한 하네스 변경 커밋
