# Project Profile: harness

## 개요와 책임

여러 프로젝트·도메인·operator가 같은 작업 규칙과 상태 모델을 사용하도록 조정하는 문서 기반 하네스다.

## 소유 도메인과 주요 기능

- 규칙 버전과 세션 시작 절차
- 프로젝트·operator 식별 등록부와 프로젝트 프로필
- 공동 이니셔티브의 목표·참여 주체·완료 기준
- request·issue·changed·task 상태 모델
- 기준 문서·제안·저널·아젠다의 생명주기
- 저널 판단의 유효성·무효화 색인과 큐레이션 상태
- worker·reviewer·curator 역할, 에이전트 실행 계약과 비직관적 현행 불변식 등록부
- 현재 상태 요약·살아있는 문서의 현재성·로컬 참조 정합 감사
- 검증된 성공·실수의 집계와 지침 개선 피드백
- 실행 결과에서 Guidance Candidate와 범위 있는 지침을 만드는 증거 기반 하네스 진화
- 로컬 review·원격 PR·feature·release·정본의 변경 승격 계약
- 하네스 primary checkout 전용 변경 경계와 linked worktree 판정·차단
- 여러 세션이 최신 하네스 기록을 다시 읽는 공유 working-directory 가시성과 통신 계층 경계

## 제공 계약

- `INDEX.md`
- `ISSUES.md`, `PROJECTS.md`, `INITIATIVES.md`, `OPERATORS.md`, `AGENDA.md`
- `INVALIDATIONS.md`, `CURATION.md`
- `FEEDBACK.md`, `feedback/README.md`
- `operators/curation-status.md`, `operators/harness-audit.md`, `operators/feedback-status.md`,
  `operators/harness-worktree-guard.md`, `operators/review-branch.md`
- 각 운영 폴더의 `README.md`와 템플릿

## 소비 계약

- 참여 프로젝트 저장소의 식별자와 소스 오브 트루스 포인터

## 다른 프로젝트와의 접점

참여 프로젝트는 자기 식별자로 요청·변경·작업을 관리하며, 타 프로젝트 수정은 request를 통해 전달한다.

## 소스 오브 트루스

- 운영 규칙: `INDEX.md`
- 프로젝트 식별: `PROJECTS.md`
- 활성 공동 이니셔티브: `INITIATIVES.md`
- 실행 자동화 식별: `OPERATORS.md`
- 지식 무효화: `INVALIDATIONS.md`
- 큐레이션 현재 상태: `CURATION.md`
- 검증 결과 집계 설정: `FEEDBACK.md`
- 변경 승격: `docs/change-promotion.md`
- 하네스 checkout 경계: `operators/harness-worktree-guard.md`
- 에이전트 실행: `docs/agent-execution.md`
- 하네스 진화: `docs/harness-evolution.md`

## 현재 제약과 후속 작업

- 운영 절차의 일부는 아직 문서 기반이며 자동 검사·커서 도구는 operator 구현으로 확장할 수 있다.
