---
task_id: t-7607163b
project: harness
operator:
opened: 2026-10-15 01:44:40 UTC
initiative:
related_issue:
related_request:
---

# Agent 엔지니어링 요구를 기능·검증에 반영

## 목표

개인정보·기밀·제품 도메인 자료를 제외하고 공고의 Agent 설계·품질·보안·관측·검증 역량을
기존 룸 서버의 실행 계약과 재현 가능한 검사에 연결한다.

## 완료 기준

- [x] workflow skill의 역할·mode·version을 요청·승인 시 검증한다.
- [x] 승인 대기 비동기 요청·상태 조회와 업무 검증을 분리한다.
- [x] 원문·이름·경로·사고 과정 없이 실행 trace·duration을 제공한다.
- [x] 합성 fixture·가짜 실행기로 권한·품질·복구·API를 재현한다.
- [x] 0건·실패·baseline 계약 변경을 성공으로 집계하지 않는다.
- [x] 전체 회귀·감사·공개 위험 검토와 실제 모델·RAG·컨테이너의 미검증 범위를 기록한다.

## 진행 기록

- 2026-10-15 01:44:40 UTC - 사용자 선택에 따라 이력서 문구 대신 기능·검증 구현을 시작하고
  예상·실패 지점·반증 방법을 `journal/2026-10-15-agent-engineering.md`에 기록했다.
- 2026-10-15 01:58:42 UTC - 룸 unittest 36개, operator unittest 11개, 9개 평가 case와 같은 baseline
  비교를 통과했다. 하네스·storage 감사도 통과했다.
- 2026-10-15 02:00:51 UTC - general workflow도 reviewer의 읽기 전용 제한을 승인 시 재검사하도록
  보강한 뒤 룸 36개·평가 9개와 baseline 비교를 다시 통과했다. 최신 문서·기록의 하네스·feedback·storage
  감사와 공개 위험 검토도 통과했다.

## 완료 결과

- `room/skills.py`, `room/tracing.py`, `room/server.py`가 workflow·비동기 API·trace·별도 검증을 제공한다.
- `operator:room-evaluate`와 `room/evals/cases.json`이 합성 계약을 검사한다. 원본 JSON은 로컬 비정본이다.
- `docs/agent-engineering.md`가 요구별 구현·증거·한계를 설명하고 r0023은 완료 과장을 방지한다.
- 실제 모델 정답률·모델 Injection 저항률·자동 검색 RAG·컨테이너 실행은 이번 수용 범위가 아니며,
  구현·운영 실적으로 주장하지 않는다. 코드·문서·이 task를 같은 로컬 변경 커밋으로 보존한다.
