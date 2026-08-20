---
task_id: t-f309781e
project: harness
operator:
opened: 2026-08-20 01:26:53 UTC
initiative:
related_issue: i-8914738a
related_request:
---

# 검증 결과 피드백과 변경 승격 체계 추가

## 목표

검증된 성공·실수를 집계해 지침 개선 후보를 찾고, 작업 결과가 사람의 승인 없이 원격 통합·배포 단계로
건너가지 않도록 로컬 리뷰 스냅샷과 원격 PR을 구분한 변경 승격 계약을 추가한다.

## 배경

사용자는 실수와 잘된 결과를 근거로 지침을 개선하는 기능, 작업본을 바로 배포 환경에 반영하지 않는 브랜치
전략, 로컬 전용 리뷰 브랜치와 공동 작업용 원격 PR 브랜치의 분리를 요청했다.

## 완료 기준

- [x] 검증된 결과 이벤트의 기록·집계·개선 임계값이 기준 문서와 operator로 제공된다.
- [x] 개인·공동 작업의 브랜치 승격 단계와 각 단계의 금지 사항이 기준 문서에 명시된다.
- [x] 로컬 `review/*` 스냅샷과 원격 PR 브랜치의 책임·명명·재검토 조건이 구분된다.
- [x] 자동 검사와 fixture 검증이 통과한다.
- [x] 공개 위험 검토 후 변경만 별도 커밋하고 원격 PR 브랜치로 push할 수 있게 준비한다.

## 진행 기록

- 2026-08-20 01:26:53 UTC - 사용자 승인에 따라 작업 브랜치를 만들고 설계·구현을 시작했다.
- 2026-08-20 01:37:26 UTC - feedback 집계와 review 브랜치 fixture, 큐레이션·정합 검사를 통과했다.

## 완료 결과

- 완료 내용: 검증 결과 이벤트·임계값·지침 개선 canon과 로컬 review·원격 PR·feature·release·정본 승격
  canon을 추가하고, 읽기 전용 집계와 로컬 리뷰 스냅샷·hook guard operator를 구현했다.
- 검증: `operators/tests/feedback-status.sh`, `operators/tests/review-branch.sh`,
  `operators/feedback-status.sh`, `operators/curation-status.sh`, `operators/harness-audit.sh`, `git diff --check`
- 관련 커밋: 이 task를 completed로 이동한 하네스 변경 커밋
