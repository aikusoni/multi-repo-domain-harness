---
task_id: t-a6515819
project: harness
operator:
opened: 2026-09-02 08:34:21 UTC
initiative:
related_issue:
related_request:
---

# 공유 하네스 가시성과 실시간 작업 신호

## 목표

하네스 primary checkout 전용 정책의 직접 목적을 여러 세션이 같은 미커밋·커밋 상태를 즉시 읽는 공유
가시성으로 명시하고, primary checkout과 정본 branch를 구분한다. 실시간 append 작업 신호는 현재 기능으로
도입하지 않고 기존 통신·durable record와의 경계 및 도입 조건을 exploration으로 보존한다.

## 완료 기준

- [x] INDEX 규칙과 변경 승격 계약에 공유 working directory가 필요한 이유를 명시한다.
- [x] primary checkout과 `main` 같은 정본 branch가 서로 다른 개념임을 명시한다.
- [x] 직접 세션 통신과 request·changed·task·journal의 역할을 구분한다.
- [x] 실시간 append 작업 신호의 최소 event·동시 쓰기·cursor·승격·비목표를 exploration에 기록한다.
- [x] 현재 active event space나 operator가 실시간 계층을 제공한다고 과장하지 않는다.
- [x] 감사와 공개 위험 검토를 통과한다.

## 착수 예측

- 예상 관측: 현행 primary-only 정책은 공유 visibility를 결과적으로 제공하지만 목적과 primary/main 구분은
  명시적이지 않다. 현재 `space:harness-events`는 issue·changed·feedback의 durable event만 소유하며
  실시간 세션 progress stream은 제공하지 않는다.
- 가장 가능성 높은 실패 지점: exploration의 미래 설계를 활성 기능처럼 표현하거나, 모든 세션 진행을
  영구 기록해 통신 예산과 하네스 기록을 팽창시키는 것.
- 반증과 확인: registry·session coordination·exploration 계약을 대조하고, 새 문서가 비정본·도입 조건·
  승격 경계를 명시하는지 감사한다.

## 진행 기록

- 2026-09-02 08:34:21 UTC - 현행 primary-only, session communication, event space와 exploration 계약을
  확인하고 작업을 시작했다.
- 2026-09-02 08:48:57 UTC - 동일 configured path와 별도 clone 경계, 공유 Git 상태 단일 writer, 선택적
  hook의 실제 보장 범위를 규칙 r0019에 반영했다.
- 2026-09-02 23:56:18 UTC - 독립 읽기 전용 리뷰 finding을 모두 반영하고 r0018·r0019 변경 기록을 각각
  보존한 뒤 전체 감사·fixture·형식·공개 위험 검토를 통과했다.

## 완료 결과

- 하네스의 모든 로컬 세션은 동일한 primary absolute path에서 최신 파일과 미커밋 변경을 다시 읽고,
  primary의 working tree·Git index·branch·refs 변경은 한 writer가 맡도록 정본화했다.
- primary checkout은 물리적 공유 위치이고 `main`은 정본 이력의 논리적 역할이므로, primary 안의 작업
  branch를 사용할 수 있다. linked worktree와 별도 clone은 하네스 대체 작업 위치로 사용하지 않는다.
- 직접 메시지와 durable record의 역할을 분리했고, append 실시간 신호는 구현 없이 도입 조건과 안전
  계약만 `explorations/`에 남겼다.

## 검증

- `operator:harness-worktree-guard check`: PASS (`current=primary`, 기존 linked 1개는 ATTENTION)
- `operator:harness-audit`: PASS (`checked_current_documents=40`)
- `operator:storage-spaces audit`: PASS (`active_spaces=9`, `research_refs=8`)
- `operator:review-branch audit`: PASS
- harness-worktree-guard·harness-audit·storage-spaces·review-branch·feedback-status fixture: PASS
- `git diff --check`: PASS
- 공개 위험 키워드 검사: PASS
- 독립 read-only 리뷰: finding 반영 완료, guard·공개 위험 최종 리뷰 PASS
