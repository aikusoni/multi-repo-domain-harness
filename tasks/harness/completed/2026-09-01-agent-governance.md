---
task_id: t-dd455a31
project: harness
operator:
opened: 2026-09-01 07:35:10 UTC
initiative:
related_issue:
related_request:
---

# 에이전트 거버넌스와 증거 기반 하네스 진화 보강

## 목표

기존 하네스와 공개 연구의 재사용 가능한 원칙을 범용화해 에이전트의 권한·위임·중단·검증·완료 계약과
실행 결과에서 지침을 안전하게 진화시키는 절차를 닫는다.

## 완료 기준

- [x] 두 참조 하네스의 신규·기존 지침과 현재 하네스의 공백을 읽기 전용으로 비교한다.
- [x] 공개 EvoHarness 연구에서 이식 가능한 구조와 연구 전용 요소를 구분한다.
- [x] 요청 수용, 비정본 입력, 위임·Reviewer, 중단·재개와 완료 증거 계약을 정의한다.
- [x] feedback에서 Guidance Candidate를 만들고 범위별 지침으로 승격하는 절차를 정의한다.
- [x] INDEX·역할·request·task·operator·세션·승격·bootstrap 문서를 정합하게 연결한다.
- [x] research catalog·storage index·감사·fixture와 공개 위험 검토를 통과한다.

## 진행 기록

- 2026-09-01 07:35:10 UTC - 참조 하네스 두 곳과 현재 에이전트 거버넌스 공백을 병렬 읽기 전용으로 검토했다.
- 2026-09-01 07:44:45 UTC - agent execution과 evidence-based harness evolution canon 초안을 반영했다.
- 2026-09-01 08:04:39 UTC - 독립 read-only 리뷰의 finding을 재현하고 우선순위·candidate 생명주기·cutover·
  원자 경계·bootstrap 감사 정합을 보정했다.
- 2026-09-02 01:34:58 UTC - EvoHarness-RL의 외부 상태 구분·선택적 접근 원칙을 추가 검토해 범용 경계로
  반영했다.
- 2026-09-02 01:40:10 UTC - 전체 fixture·감사·JSON·shell·Python 검사와 공개 위험 검토를 완료했다.

## 결과

- 에이전트 요청 권한, 비정본 입력, 현재 판단·진행·경험, 위임·Reviewer, 중단·재개와 완료 단계를
  `docs/agent-execution.md`로 정본화했다.
- Guidance Candidate의 `ADD|MERGE|REVISE|SKIP`, 범위·회귀·cutover와 안정 ID·상태·종결 생명주기를
  `docs/harness-evolution.md`와 `feedback/candidates/README.md`에 정본화했다.
- `instruction-ineffective` cutover, bootstrap marker, storage/research index를 operator와 fixture로 검증했다.
- 공개 위험 검토 결과 로컬 절대경로·조직 내부 정보·인증정보·개인정보·비공개 URL은 없었고, 추가 URL은
  공개 arXiv 원문 두 건뿐이었다.

## 검증

- `git diff --check`: PASS
- `bash -n operators/*.sh operators/tests/*.sh`: PASS
- 전체 JSON `jq empty`: PASS
- `operators/tests/feedback-status.sh`: PASS
- `operators/tests/harness-audit.sh`: PASS
- `operators/tests/storage-spaces.sh`: PASS
- `operators/tests/review-branch.sh`: PASS
- `operator:storage-spaces audit`: PASS (`active_spaces=9`, `research_refs=8`)
- `operator:harness-audit`: PASS (`checked_current_documents=39`)
- `operator:feedback-status`: PASS (`invalid_events=0`)
- 관련 커밋: 이 task를 완료로 이동하는 동일 커밋
