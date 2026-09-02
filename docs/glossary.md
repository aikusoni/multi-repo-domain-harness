# 용어집

| 용어 | 정의 | 소유 도메인 | 저장소별 표현 | 비고 |
|---|---|---|---|---|
| Project Profile | 프로젝트의 정체성·책임·소유 도메인·제공/소비 계약을 설명하는 자기소개 문서 | harness | `PROJECTS.md`, `projects/<project-id>.md` | 에이전트의 기본 정체성은 project-id |
| Initiative | 둘 이상의 프로젝트·역할·operator가 측정 가능한 공동 결과를 달성하기 위한 협업 단위 | harness | `initiative:<id>` | 프로젝트 정체성이나 task 상태를 대체하지 않음 |
| Initiative Outcome | initiative가 완료됐다고 판정할 수 있는 측정 가능한 공동 목표 | initiative lead | 결과, 완료 기준 | 구현 목록보다 사용자·시스템 결과 중심 |
| Outcome Feedback | 검증된 성공·실수가 지침의 효과와 개선 필요성에 제공하는 증거 | worker, curator | `feedback/`, `FEEDBACK.md` | 개인·에이전트 성과 점수가 아님 |
| Agent Execution Contract | 요청 권한·비정본 입력·위임·재개·검증과 완료 주장을 에이전트 공통 행동으로 정한 계약 | harness | `docs/agent-execution.md` | 모델·세션·도구가 권한을 넓히지 않음 |
| Guidance Candidate | 검증된 결과에서 추출한 lesson·trigger·evidence·scope_hint를 가진 비정본 지침 후보 | curator | `feedback/candidates/gc-xxxxxxxx.md` | 승인 전 canon이나 작업 지시가 아님 |
| Harness Evolution | candidate를 현행 지침과 비교해 추가·병합·수정·기각하고 범위·효과·회귀를 검증하는 절차 | harness | `docs/harness-evolution.md` | 자동 자기수정이나 원시 경험 append가 아님 |
| Review Snapshot | 사람이 검토할 어느 committed checkpoint든 가리킬 수 있는 로컬 전용 불변 브랜치 | 작업 project | `review/<topic>_<UTC timestamp>` | 승격 경로의 단계가 아니며 원격 push와 생성 뒤 변경 금지 |
| Promotion | 승인·검증된 변경을 PR, feature, release·정본의 다음 통합 단계로 이동하는 행위 | 작업 project와 승인자 | `docs/change-promotion.md` | review 생성이나 브랜치 생성만으로 승인된 것이 아님 |
| Primary Checkout | absolute Git dir와 absolute common dir가 같고 하네스의 가변 작업을 허용하는 기본 checkout | harness | `operator:harness-worktree-guard`의 `current=primary` | 단순 경로명이나 branch명으로 판정하지 않음 |
| Linked Worktree | absolute Git dir와 absolute common dir가 다른 추가 checkout | harness | `operator:harness-worktree-guard`의 `current=linked` | 하네스에서는 읽기 전용 상태 확인만 허용, 참여 프로젝트 정책은 별도 |
| Task | 한 프로젝트 또는 operator owner가 직접 수행하는 실행 단위 | 해당 프로젝트 | `tasks/<project>/...` | 프로젝트 내부 상태 |
| Request | 다른 프로젝트·operator에 전달하고 결과를 왕복 확인하는 실행 요청 | 요청자·대상 | `requests/...` | 프로젝트 간 인계 |
| Issue | 계약·기준·작업 흐름의 위험이나 차단 상태 | 관련 주체 | `ISSUES.md`, `issues/...` | 활성 상태와 이력 분리 |
| Operator | 반복 가능한 실행을 자동화하는 주체 | owner 프로젝트 | `operator:<id>` | 에이전트 정체성이 아님 |
| Storage Space | 특정 정보 특성·질의·비용을 위해 역할·보존·손실·rebuild 계약으로 등록한 저장 위치 | harness | `space:<id>`, `storage/definitions/` | object·graph·field는 선택 가능한 kind |
| Storage Role | 공간이 원본 근거, 직접 기록, 파생 표현, 검색 index, 임시 cache 중 맡는 책임 | harness | `evidence`, `record`, `projection`, `index`, `cache` | projection·index·cache는 정본이 아님 |
| Cross-Space Catalog | 같은 정보의 여러 representation과 source lineage·transformation을 연결하는 제어 계층 | harness | `catalog:<id>`, `storage/catalog/` | 실제 자료 본문을 복제하는 공간이 아님 |
| Transformation | 한 표현에서 다른 표현을 만들 때 방법·버전·입출력·보존·손실·가역성을 선언한 계약 | 변환 owner | `transformation:<id>` | 파생 표현 재구성 근거 |
| Residual | 현재 active model이나 분류에 맞지 않는 충돌·예외·희귀 신호 | 관찰 project | `space:residuals` | 억지 분류하지 않고 review 시각과 근거 보존 |
| Query Plan | 질문의 query mode와 예산에 맞춰 필요한 active space·순서·손실을 선택한 조회 계획 | harness | `operator:storage-spaces plan` | 정확한 구조 조건을 우선하고 중요한 결론은 evidence 재확인 |
| Storage Adapter | 외부 엔진·서비스의 고유 API를 write·query·trace·export·rebuild·health 공통 계약으로 격리하는 연결 계층 | adapter owner | `adapter:<id>`, `storage/adapters/` | 외부 시스템을 정본으로 자동 승격하지 않음 |
| Implementation Candidate | Storage Space requirement를 충족할 가능성이 있어 근거·license·유지보수·손실을 평가하는 구현 후보 | space owner | `candidate:<id>` | research reference나 발견만으로 selected가 되지 않음 |
| Reuse-first | 직접 구현 전에 capability를 정의하고 기존 연구·구현과 adapter 가능성을 비교하는 선택 원칙 | harness | `implementation.selection_policy` | 무조건 외부 구현을 채택한다는 뜻이 아님 |
| Portability Contract | 구현 중단·교체 시 export 형식, lock-in 허용 여부, exit plan과 fallback data access를 보장하는 계약 | space owner | `portability`, `implementation.fallback` | evidence·record의 핵심 접근은 unavailable 금지 |
| Research Reference | 구현·질의·lineage 설계를 검토하기 위해 공개 원문에서 확인한 참고 항목 | harness | `research:<id>`, `research/catalog.json` | 기본 `reference-only`, 도입 승인이 아님 |
| Local Storage Runtime | 파일·Git 정본 위에서 DB·전문 index·context 조립을 재생성 가능한 projection으로 실행하는 장기 계층 | harness | `docs/local-storage-runtime.md` | 현재 미구현, 측정된 병목과 proposal 승인 뒤 도입 |
| Local Storage Broker | 다중 에이전트의 로컬 저장 접근을 중개해 정책·schema·ID·쓰기·파생 갱신을 조정하는 future component | harness | future runtime process | record owner나 Source of Truth가 아님 |
| Retrieval Status | 조회 범위와 결과 의미를 found·not_found·not_searched·stale·partial 등으로 구분하는 계약 | query owner | query result metadata | not_found 이외 상태를 부재로 해석 금지 |
| Query Trace | 질문 해석부터 space 선택·질의·fallback·선별·압축·최종 전달까지 잇는 재현 가능한 인출 provenance | query owner | `query:<id>` | 비공개 query 본문 대신 안전한 ref 사용 |
| Memory Fault | 필요한 정보가 현재 문맥에 없거나 신뢰할 수 없을 때 추가 조회·재검증을 요구하는 future runtime signal | harness runtime | `memory-failure:<id>` | 권한 확대나 무제한 전체 검색의 근거가 아님 |
| Exploration | 정책·설계·용어와 장기 방향을 결정·실행 전에 여러 관점과 열린 질문으로 보존하는 비정본 토론 노트 | harness | `explorations/<topic>.md` | 일반 시작 읽기·작업 게이트 아님, 결과는 명시적으로 승격 |
| Invalidation | 과거 저널 판단이 대체되거나 기각됐음을 명시하는 지식 유효성 기록 | harness | `INVALIDATIONS.md` | 실행 항목의 dropped/cancelled와 구분 |
| Quirk | 코드만 읽으면 오해하기 쉬우며 모르고 변경하면 동작을 깨뜨리는 현행 불변식 | 해당 프로젝트 | `Q-NNN` | 단순 복잡성이나 과거 경위는 제외 |
| Worker | 프로젝트 작업과 그 실행 기록을 남기는 기본 역할 | 해당 프로젝트 | `docs/roles.md` | project-id를 대체하지 않음 |
| Reviewer | 고정된 checkpoint를 기본 read-only로 검토해 근거 있는 finding을 반환하는 역할 | 검토 project | `docs/roles.md` | 사람 승인·승격 권한을 대신하지 않음 |
| Curator | 하네스의 승격·무효화·아카이브·정합을 관리하는 역할 | harness | `docs/roles.md`, `CURATION.md` | project-id를 대체하지 않음 |
