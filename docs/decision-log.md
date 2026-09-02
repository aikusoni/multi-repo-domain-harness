# 결정 로그

확정된 횡단 결정의 현재 색인이다. 검토·시도했지만 채택하지 않은 판단은 `INVALIDATIONS.md`에 두고 이
파일에 섞지 않는다.

## 전제와 재검토 트리거

- 판단형 결정은 결정이 유효한 `전제`와 다시 검토해야 하는 관측 가능한 `재검토 트리거`를 기록한다.
- 트리거는 날짜가 아니라 사건으로 쓴다. 예: 첫 운영 배포, 계약 소유권 변경, 측정값이 합의한 한계 초과.
- 전제가 없는 사실형 결정은 전제에 `해당 없음(사실)`, 트리거에 `해당 없음(사실 확정)`을 명시한다.
- 빈칸은 “해당 없음”이 아니라 미검토로 간주한다.

| ID | 상태 | 결정 시각(UTC) | 결정 | 전제 | 재검토 트리거 | 관련 프로젝트 | 상세 문서 |
|---|---|---|---|---|---|---|---|
| D-001 | accepted | 2026-08-20 01:33:17 UTC | 성공·실수는 상쇄되는 성과 점수가 아니라 검증 증거와 반복 pattern으로 지침 개선에 사용한다. | 구조화된 evidence와 도입·발견 단계가 원시 카운트보다 지침 원인을 더 잘 구분한다. | 이벤트 부풀리기, 유의미한 문제 미탐지 또는 임계값으로 인한 반복 오판이 확인됨 | harness, 전체 | `docs/outcome-feedback.md` |
| D-002 | superseded | 2026-08-20 01:33:17 UTC | 작업본은 로컬 불변 review, 공동 원격 PR, feature, release·정본 순으로 승인·검증해 승격한다. D-003이 review를 선형 단계에서 독립 checkpoint 스냅샷으로 재정의했다. | 참여 저장소가 로컬 branch와 원격 보호·CI를 구분해 운영할 수 있다. | review가 승격 경로의 한 단계가 아니거나 승격 뒤 checkpoint도 다시 검토해야 함 | harness, 전체 | `docs/change-promotion.md#승격-경로와-리뷰-체크포인트` |
| D-003 | accepted | 2026-08-27 05:58:29 UTC | 승격은 작업·PR·feature·release·정본 경로로 관리하고, review는 어느 committed checkpoint에서나 별도로 생성하는 로컬 불변 스냅샷으로 관리한다. 작업용 worktree에는 임시 작업 브랜치만 연결한다. | 저장소가 임시 작업 ref와 지속 가능한 ref를 구분하고 commit을 detached 상태로 검토할 수 있다. | 호스팅 도구가 detached commit 검토를 지원하지 않거나 브랜치 잠금 없이 동일한 불변성·도달 가능성을 보장하는 방식이 필요함 | harness, 전체 | `docs/change-promotion.md#승격-경로와-리뷰-체크포인트` |
| D-004 | accepted | 2026-08-28 05:16:27 UTC | 하네스 메모리는 하나의 중심 데이터 모델이 아니라 공통 registry·catalog·query/context 계약 아래 조합하는 여러 Storage Space로 구성한다. Object·Relation·Field는 선택 가능한 저장 전략으로 둔다. | 정보마다 보존 특성·질의·비용·허용 손실이 달라 단일 표현이 원문과 모든 구조적 조회를 함께 최적화할 수 없다. | 서로 다른 space의 lineage 비용이 효용을 반복해서 초과하거나 하나의 검증된 표현이 모든 활성 query mode와 보존 요구를 더 단순하게 충족함 | harness, 전체 | `docs/storage-architecture.md` |
| D-005 | accepted | 2026-08-28 05:36:34 UTC | 새 저장 구현은 capability 정의와 기존 연구·구현 평가를 먼저 수행하고, 적합한 구현은 표준 adapter로 연결한다. 직접 구현은 하네스 고유 제어 계층과 최소 fallback에 한정한다. | 공개 export, lineage, license와 장애 fallback을 계약으로 강제하면 외부 구현을 재사용하면서도 교체 가능성과 정본 경계를 유지할 수 있다. | adapter 계층의 운영·교체 비용이 검증된 직접 구현보다 반복해서 높거나 기존 구현 조사로 보안·정확성·가용성 요구를 충족할 수 없음 | harness, 전체 | `docs/storage-adapters.md` |
| D-006 | accepted | 2026-08-28 05:48:09 UTC | 파일·Git record를 사람이 검토 가능한 정본으로 유지하고, 로컬 DB·전문 index·broker와 기억 신뢰성 기능은 반복 병목이 측정된 뒤 재생성 가능한 실행 계층으로 단계 도입한다. | 파일 정본과 파생 실행 상태를 분리하고 retrieval status·trace·fallback을 계약화하면 검색을 가속하면서도 누락·stale 결과와 새로운 정본 생성을 막을 수 있다. | 파일 기반 탐색·문맥 비용 또는 기억 실패가 반복 측정되거나, 반대로 제안 계층의 비용·복잡성이 검증 효용을 초과함 | harness, 전체 | `docs/local-storage-runtime.md`, `docs/memory-reliability.md` |
| D-007 | accepted | 2026-08-28 09:10:02 UTC | 하네스 정책·설계·용어의 열린 사유는 일반 시작 읽기와 작업 게이트에서 제외한 `explorations/` 비정본 narrative로 보존하고, 실행·판단·규칙은 기존 정식 경로로만 명시적으로 승격한다. | 작업 journal·proposal·agenda·canon과 분리하면 결론을 서두르지 않고 사고 과정을 보존하면서 현행 지침으로 오인하는 위험을 줄일 수 있다. | exploration이 실행 정본으로 반복 오인되거나, 사용되지 않는 토론 노트의 탐색·관리 비용이 보존 가치보다 커짐 | harness, 전체 | `explorations/README.md` |
| D-008 | accepted | 2026-09-01 07:44:45 UTC | 에이전트의 요청 수용, 비정본 입력, 위임·독립 리뷰, 중단·재개, 긴 작업의 외부 상태와 완료 증거를 도구 중립 실행 계약으로 관리한다. | 모델·도구·하위 에이전트의 결과와 사용자 권한을 분리하고 현재 판단·진행·경험 및 직접 관측한 완료 단계를 구분해야 자동화가 권한·상태를 추측하지 않는다. | 계약이 일반 작업을 반복해서 불필요하게 막거나, 새로운 실행 형태가 현행 권한·증거 상태로 표현되지 않음 | harness, 전체 | `docs/agent-execution.md` |
| D-009 | accepted | 2026-09-01 07:44:45 UTC | 검증된 실행 결과는 lesson·trigger·evidence·scope_hint를 가진 Guidance Candidate record로 만든 뒤 기존 지침과 비교해 추가·병합·수정·기각하고, 승인된 범위별 지침만 선택적으로 적용한다. | 원시 경험을 직접 규칙에 붙이면 작업 특이 노이즈와 지침 팽창이 생기므로 evidence, 후보 생명주기, scope, feedback과 회귀 검증을 분리해야 한다. | candidate 큐레이션 비용이 효과보다 크거나, 범위별 지침과 선택 예산이 실제 성능·안전성을 반복해서 악화함 | harness, 전체 | `docs/harness-evolution.md`, `feedback/candidates/README.md` |
| D-010 | accepted | 2026-09-02 06:16:57 UTC | 하네스 저장소의 가변 작업은 Git dir와 common dir가 같은 primary checkout에서만 수행하고 linked worktree에서는 차단한다. 참여 프로젝트의 worktree 정책은 유지한다. | append가 많은 공유 운영 기록을 하나의 checkout으로 직렬화하면 동시 분기·누락 위험을 줄일 수 있고, 하네스 병렬성보다 상태 일관성이 중요하다. | primary 직렬화가 반복적으로 병목이 되거나 linked 격리가 더 낮은 위험으로 동일한 정합성을 보장한다는 검증 근거가 축적됨 | harness | `docs/change-promotion.md#하네스-저장소-예외-primary-checkout-전용` |

상태는 `accepted`, `superseded`, `deprecated`를 사용한다. `superseded`는 대체 결정이나 ADR 링크가
필수다. 중요한 결정은 별도 ADR 문서를 만들고 여기에는 한 줄 요약과 링크만 둔다.
