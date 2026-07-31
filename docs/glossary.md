# 용어집

| 용어 | 정의 | 소유 도메인 | 저장소별 표현 | 비고 |
|---|---|---|---|---|
| Project Profile | 프로젝트의 정체성·책임·소유 도메인·제공/소비 계약을 설명하는 자기소개 문서 | harness | `PROJECTS.md`, `projects/<project-id>.md` | 에이전트의 기본 정체성은 project-id |
| Initiative | 둘 이상의 프로젝트·역할·operator가 측정 가능한 공동 결과를 달성하기 위한 협업 단위 | harness | `initiative:<id>` | 프로젝트 정체성이나 task 상태를 대체하지 않음 |
| Initiative Outcome | initiative가 완료됐다고 판정할 수 있는 측정 가능한 공동 목표 | initiative lead | 결과, 완료 기준 | 구현 목록보다 사용자·시스템 결과 중심 |
| Task | 한 프로젝트 또는 operator owner가 직접 수행하는 실행 단위 | 해당 프로젝트 | `tasks/<project>/...` | 프로젝트 내부 상태 |
| Request | 다른 프로젝트·operator에 전달하고 결과를 왕복 확인하는 실행 요청 | 요청자·대상 | `requests/...` | 프로젝트 간 인계 |
| Issue | 계약·기준·작업 흐름의 위험이나 차단 상태 | 관련 주체 | `ISSUES.md`, `issues/...` | 활성 상태와 이력 분리 |
| Operator | 반복 가능한 실행을 자동화하는 주체 | owner 프로젝트 | `operator:<id>` | 에이전트 정체성이 아님 |
