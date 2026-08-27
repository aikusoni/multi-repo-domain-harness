# 용어집

| 용어 | 정의 | 소유 도메인 | 저장소별 표현 | 비고 |
|---|---|---|---|---|
| Project Profile | 프로젝트의 정체성·책임·소유 도메인·제공/소비 계약을 설명하는 자기소개 문서 | harness | `PROJECTS.md`, `projects/<project-id>.md` | 에이전트의 기본 정체성은 project-id |
| Initiative | 둘 이상의 프로젝트·역할·operator가 측정 가능한 공동 결과를 달성하기 위한 협업 단위 | harness | `initiative:<id>` | 프로젝트 정체성이나 task 상태를 대체하지 않음 |
| Initiative Outcome | initiative가 완료됐다고 판정할 수 있는 측정 가능한 공동 목표 | initiative lead | 결과, 완료 기준 | 구현 목록보다 사용자·시스템 결과 중심 |
| Outcome Feedback | 검증된 성공·실수가 지침의 효과와 개선 필요성에 제공하는 증거 | worker, curator | `feedback/`, `FEEDBACK.md` | 개인·에이전트 성과 점수가 아님 |
| Review Snapshot | 사람이 검토할 어느 committed checkpoint든 가리킬 수 있는 로컬 전용 불변 브랜치 | 작업 project | `review/<topic>_<UTC timestamp>` | 승격 경로의 단계가 아니며 원격 push와 생성 뒤 변경 금지 |
| Promotion | 승인·검증된 변경을 PR, feature, release·정본의 다음 통합 단계로 이동하는 행위 | 작업 project와 승인자 | `docs/change-promotion.md` | review 생성이나 브랜치 생성만으로 승인된 것이 아님 |
| Task | 한 프로젝트 또는 operator owner가 직접 수행하는 실행 단위 | 해당 프로젝트 | `tasks/<project>/...` | 프로젝트 내부 상태 |
| Request | 다른 프로젝트·operator에 전달하고 결과를 왕복 확인하는 실행 요청 | 요청자·대상 | `requests/...` | 프로젝트 간 인계 |
| Issue | 계약·기준·작업 흐름의 위험이나 차단 상태 | 관련 주체 | `ISSUES.md`, `issues/...` | 활성 상태와 이력 분리 |
| Operator | 반복 가능한 실행을 자동화하는 주체 | owner 프로젝트 | `operator:<id>` | 에이전트 정체성이 아님 |
| Invalidation | 과거 저널 판단이 대체되거나 기각됐음을 명시하는 지식 유효성 기록 | harness | `INVALIDATIONS.md` | 실행 항목의 dropped/cancelled와 구분 |
| Quirk | 코드만 읽으면 오해하기 쉬우며 모르고 변경하면 동작을 깨뜨리는 현행 불변식 | 해당 프로젝트 | `Q-NNN` | 단순 복잡성이나 과거 경위는 제외 |
| Worker | 프로젝트 작업과 그 실행 기록을 남기는 기본 역할 | 해당 프로젝트 | `docs/roles.md` | project-id를 대체하지 않음 |
| Curator | 하네스의 승격·무효화·아카이브·정합을 관리하는 역할 | harness | `docs/roles.md`, `CURATION.md` | project-id를 대체하지 않음 |
