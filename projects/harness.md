# Project Profile: harness

## 개요와 책임

여러 프로젝트·도메인·operator가 같은 작업 규칙과 상태 모델을 사용하도록 조정하는 문서 기반 하네스다.

## 소유 도메인과 주요 기능

- 규칙 버전과 세션 시작 절차
- 프로젝트·operator 식별 등록부와 프로젝트 프로필
- 공동 이니셔티브의 목표·참여 주체·완료 기준
- request·issue·changed·task 상태 모델
- 기준 문서·제안·저널·아젠다의 생명주기

## 제공 계약

- `INDEX.md`
- `ISSUES.md`, `PROJECTS.md`, `INITIATIVES.md`, `OPERATORS.md`, `AGENDA.md`
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

## 현재 제약과 후속 작업

- 운영 절차의 일부는 아직 문서 기반이며 자동 검사·커서 도구는 operator 구현으로 확장할 수 있다.
