---
task_id: t-7c9d2a41
project: harness
operator:
opened: 2026-08-21 09:08:56 UTC
initiative:
related_issue:
related_request:
---

# 세션 간 협업과 통신 예산 규칙 추가

## 목표

동시에 살아 있는 세션을 안전하게 식별·호출하고, 사람의 통제권을 잃지 않도록 세션 간 통신의 기록,
트랜잭션 총량과 사람 프롬프트 이후 수신량의 중단 기준을 범용 규칙으로 정의한다.

## 완료 기준

- [x] 충돌 위험 경계에서만 살아 있는 세션을 관측하고 직접 조정하는 절차가 정의된다.
- [x] 세션 간 통신 트랜잭션의 식별자·경계·총 10건 상한이 정의된다.
- [x] 한 세션에서 사람의 마지막 프롬프트 이후 수신 5건째에 확인을 요청하는 규칙이 정의된다.
- [x] 무가치한 핑퐁과 종료 메시지 재응답을 막는 중단 조건이 정의된다.
- [x] 저널에 관측·통신과 카운터를 남기는 범용 형식이 추가된다.
- [x] UTC 표기, 공개 위험 검토와 하네스 정합 검사가 통과한다.

## 진행 기록

- 2026-08-21 09:08:56 UTC - 별도 작업 브랜치에서 기존 규칙과 새 세션 협업 지침의 차이를 검토했다.
- 2026-08-21 09:14:07 UTC - 규칙·canon·저널 형식을 반영하고 fixture, 상태 operator, 정합 검사를 통과했다.

## 완료 결과

- 완료 내용: 위험 경계 관측과 공유 쓰기 선후, 새 값·종료 신호, tx 전체 10건 상한, 세션별 사람
  프롬프트 이후 수신 5건 게이트, 사용자 중단 보고와 `SESSION-COMM` 기록 형식을 추가했다.
- 검증: `operators/tests/feedback-status.sh`, `operators/tests/review-branch.sh`,
  `operators/curation-status.sh`, `operators/feedback-status.sh`, `operators/harness-audit.sh`,
  `git diff --check`, 공개 위험 키워드 검사
- 관련 커밋: 이 task를 completed로 이동한 하네스 변경 커밋
