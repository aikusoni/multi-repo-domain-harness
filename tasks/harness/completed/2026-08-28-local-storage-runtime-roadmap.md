---
task_id: t-6c9b82e0
project: harness
operator: operator:storage-spaces
opened: 2026-08-28 05:48:09 UTC
initiative:
related_issue:
related_request:
---

# 로컬 저장 실행·기억 신뢰성 장기 로드맵 정의

## 목표

현재 파일 기반 정본을 유지하면서, 실제 병목이 확인된 뒤에만 도입할 로컬 다중 저장공간 실행 계층과 기억
신뢰성·인출 보장 계층의 책임, 단계, 도입 조건과 fallback을 범용 canon으로 정의한다.

## 완료 기준

- [x] Local Storage API·Broker·전문 공간과 embedded 우선 실행 방식의 경계가 정의된다.
- [x] Git record와 로컬 재생성 상태, 도입 조건·비목표·단계·rollback이 정의된다.
- [x] 기억 실패 단계, Retrieval Status, 저장 상태, Query Trace와 fallback이 정의된다.
- [x] Memory Fault가 future signal이며 권한 확대·무제한 검색 근거가 아님을 명시한다.
- [x] 기존 storage canon·INDEX·용어·결정·changed 기록과 정합하다.
- [x] 전체 audit·syntax·링크·공개 위험 검토를 통과한다.

## 진행 기록

- 2026-08-28 05:48:09 UTC - 장기 후보와 현재 active 기능의 경계를 정하고 두 기준 문서와 연결 문서를
  작성했다.
- 2026-08-28 05:54:27 UTC - operator fixture, storage·harness audit, JSON·Python·Bash syntax, 결정적 index,
  링크·diff와 공개 위험 검토를 통과했다.

## 완료 결과

- 완료 내용: Local Storage API·Broker와 전문 공간을 파일 정본 위의 재생성 가능한 future runtime으로
  정의했다. embedded 우선·병목 측정·단계별 proposal·rollback을 도입 게이트로 두고, Retrieval Status,
  저장 상태, Query Trace, 위험 기반 fallback과 future Memory Fault의 책임을 별도 신뢰성 계약으로 정리했다.
- 현재 경계: 로컬 DB·broker·자동 Memory Fault는 구현하지 않았으며 active adapter는 0개다.
- 검증: 전체 operator fixture, `operator:storage-spaces` audit·build·query·plan,
  `operator:harness-audit`, curation·feedback 상태, JSON·Python·Bash syntax, 생성 index URL 비복제,
  `git diff --check`, 공개 위험 검사
- 관련 커밋: 이 task를 completed로 이동한 하네스 변경 커밋
