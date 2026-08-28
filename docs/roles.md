# 하네스 역할

역할은 에이전트가 현재 수행하는 책임 묶음이며 프로젝트 정체성을 대체하지 않는다. worker나 curator 역할을
맡아도 에이전트의 기본 정체성은 계속 현재 저장소 또는 역할의 `project-id`다.

## Worker

제품·문서 작업을 수행하고 관련 기록을 하네스에 남기는 기본 역할이다.

- 새 저널을 `VALIDITY: ACTIVE`로 시작한다.
- 현재 작업에서 과거 판단을 뒤집으면 원본 저널의 유효성 메타데이터와 `INVALIDATIONS.md`를 갱신한다.
- 기존 코드의 비직관적 동작 때문에 실제 문제를 조사했다면 `docs/quirks.md` 후보를 남긴다.
- 작업 완료·리뷰·검증·승격에서 지침 평가에 정보가 있는 검증 결과를 `feedback/`에 기록한다.
- 작업 변경은 `docs/change-promotion.md`의 worktree·review·PR·feature 승격 경계를 지킨다.
- 정보를 새 표현으로 저장할 때 active Storage Space를 선택하고 evidence·lineage, 허용 손실과 public-safe
  ref를 보존한다. 적합한 공간이 없으면 임의 저장소를 만들지 않고 proposal로 제안한다.
- 다른 프로젝트의 작업은 request로 넘기고 자기 프로젝트의 task·changed 기록만 관리한다.

## Curator

하네스의 지식 정합성과 검색 품질을 관리하는 역할이다. 하네스 규칙 변경 작업이나 사용자가 명시한
큐레이션 작업에서 활성화한다.

1. `operator:curation-status` 결과와 `CURATION.md`를 확인한다.
2. `operator:harness-audit`로 깨진 참조, 상태 요약 비대, 종료 문서의 현행 참조와 살아있는 문서의
   현재성 헤더를 확인한다.
3. `operator:feedback-status`의 major 이상 실수와 반복 pattern을 근거·반례·현행 지침에 대조한다.
4. 저널의 `VALIDITY` 누락과 대체·기각됐지만 아직 `ACTIVE`인 판단을 점검한다.
5. `SUPERSEDED`·`REJECTED` 항목을 `INVALIDATIONS.md`에 등재한다.
6. 반복해서 재발견되는 현행 불변식을 `docs/quirks.md`에 승격한다.
7. 검증된 현행 판단만 canon과 `docs/decision-log.md`로 승격한다. 판단형 결정에는 전제와 사건 기반
   재검토 트리거를 기록한다.
8. `ISSUES.md`·`AGENDA.md`의 현재 문장을 근거와 대조해 다시 쓰고, 살아있는 문서의 현재성 머리말과
   종료 항목 반영 여부를 점검한다.
9. 현행 참조가 없는 오래된 저널·요청·제안을 각 archive로 옮기고 현재 등재부·canon·목차의 포인터를
   새 경로로 갱신한다.
10. `operator:storage-spaces audit`으로 registry-definition 정합, 여러 표현의 lineage, 위험 ref와 파생
    index 재구성 가능성을 확인한다. 저장 기술 하나를 기본 정답으로 승격하지 않는다.
11. 완료 후 `CURATION.md`의 `last_curated_at`을 실제 완료 시각의 UTC 값으로 갱신한다.

Curator도 분쟁을 임의 확정하지 않는다. 해석·소유권·정책 결정이 필요하면 근거를 `AGENDA.md`에 올리고
사용자 결정을 기다린다. 자동 교정이나 과거 본문 재작성은 하지 않는다.
