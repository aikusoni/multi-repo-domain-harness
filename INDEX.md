# Multi-Repo Domain Harness 운영 규칙

**규칙 버전: r0014 · 최종 갱신: 2026-08-28 05:48:09 UTC · 지연 도입 로컬 저장·기억 신뢰성 경계 추가**

여러 도메인과 코드 저장소를 하나의 작업 흐름으로 연결하기 위한 진입점이자 운영 규칙의 유일한 정본이다.

> **필수**: 모든 프로젝트와 모든 에이전트는 작업 종류와 규모에 관계없이 작업을 시작하기 전에 이 파일
> 전체를 반드시 읽고 숙지한다. 이 절차를 생략한 상태에서는 파일 조사·수정·작업 착수를 진행하지 않는다.
> 규칙 버전 스탬프가 마지막으로 확인한 값과 다르면 이 파일 전체를 다시 읽는다.

`INDEX.md`를 읽은 뒤 현재 프로젝트와 관련된 하위 문서만 선택적으로 읽는다.

## 폴더 구조

| 경로 | 역할 | 운영 방식 |
|---|---|---|
| `docs/` | 공통 계약, 용어, 결정, 저장소·도메인 지도 | 기준 문서. 변경 전 검토 권장 |
| `storage/` | 활성 저장공간 registry, definition, catalog, transformation과 파일 공간 | record·파생 표현의 위치·손실·lineage 정본 |
| `schemas/` | 저장공간 control plane의 기계 판독 계약 | JSON Schema와 operator 검사를 함께 정합 |
| `indexes/` | 등록 공간과 catalog의 재생성 가능한 검색 index | 생성 결과. 정본 아님, 직접 수정 금지 |
| `views/` | 여러 저장공간에서 조립한 사람용 파생 뷰 | 생성 조건·입력 digest·손실을 명시 |
| `research/` | 저장공간·adapter 설계에 참고한 검증된 공개 연구·구현 reference | 기본 reference-only. 채택 정본 아님 |
| `journal/` | 세션별 발견, 결정, 시행착오 | append-only. 유효성 메타데이터만 예외 |
| `INVALIDATIONS.md` | 대체·기각된 저널 판단의 누적 색인 | 원본 저널과 함께 갱신 |
| `CURATION.md` | 지식 큐레이션 시각과 주의 임계값 | 현재 상태. 규칙 정본이 아님 |
| `FEEDBACK.md` | 검증 결과 집계 설정과 주의 임계값 | 현재 상태. 성과 점수가 아님 |
| `feedback/` | 검증된 성공·실수의 UTC 날짜별 이벤트 | append-only. 지침 개선 증거 |
| `proposals/` | 기준 문서 변경 제안 | 자유롭게 작성, 승인 후 `docs/` 반영 |
| `requests/` | 다른 프로젝트·operator에 전달하는 작업 요청 | 요청자와 대상이 왕복 처리 |
| `ISSUES.md` | 활성 proposal/request의 상태 정본 | 활성 상태만 유지 |
| `issues/` | 날짜별 이슈 상태 변경 이력 | UTC 날짜의 당일 파일에 append |
| `changed/` | 교차 프로젝트 변경 피드와 확인 기록 | 변경자 기록, 영향 프로젝트 확인 |
| `tasks/` | 프로젝트·operator별 실행 작업 큐 | 폴더 위치가 상태 정본 |
| `AGENDA.md` | 사람의 결정·리뷰·합의를 기다리는 열린 안건 | 게이팅 없음. 결론 반영 시 제거 |
| `PROJECTS.md` | 프로젝트·저장소·역할 식별 등록부 | 프로젝트 프로필 한두 줄 색인 |
| `projects/` | 프로젝트 프로필 상세 | 각 프로젝트가 자기 문서만 관리 |
| `INITIATIVES.md` | 활성 공동 이니셔티브 등록부 | 공동 목표·상태·참여 주체의 현재 정본 |
| `initiatives/` | 이니셔티브 상세와 완료 기준 | lead가 갱신, 참여 주체가 실행 결과 연결 |
| `OPERATORS.md` | 실행 자동화 식별 등록부 | operator별 책임·소유권 색인 |
| `operators/` | operator 동작 계약과 작성 템플릿 | 기준 문서. 변경 전 영향 검토 |

## 세션 규칙

1. **INDEX 필독**: 어떤 프로젝트·에이전트·작업 유형이든 다른 하네스 파일을 읽거나 수정하기 전에
   `INDEX.md` 전체를 반드시 읽는다. 읽지 않은 상태에서는 작업을 시작하지 않는다. 이어서 현재 저장소의
   `git status --short`를 확인해 기존 변경과 자기 작업 범위가 겹치는지 판단한다.
   - 한 프로젝트 저장소의 같은 작업트리에는 동시에 한 에이전트만 작업하는 것을 권장한다.
   - 병렬 작업이 필요하면 별도 worktree를 우선하고, 불가능하면 서로 겹치지 않는 경로를 사전에 나눈다.
   - 기존 변경은 다른 작업의 소유물로 간주한다. 조사나 검증이 막혀도 임의 수정·삭제·stage 해제하지 않고
     사용자에게 충돌 범위와 가능한 격리 방법을 알린다.
2. **프로젝트 기반 에이전트 식별**: 에이전트의 기본 정체성은 사람·세션·모델·브랜치가 아니라 현재
   담당하는 저장소 또는 역할의 `project-id`다. 브랜치·worktree·task id·커밋은 작업 문맥과 결과 위치로
   기록하며 정체성으로 사용하지 않는다. `PROJECTS.md`에 없으면 작업 전에 등록한다. 한 세션이 여러
   저장소를 오가면 저장소마다 해당 `project-id`로 별도 확인한다.
   - `PROJECTS.md`와 `projects/<project-id>.md`의 **Project Profile(프로젝트 프로필)**은 프로젝트의
     자기소개다. “누가 협업하는가, 무엇을 소유하는가, 어떤 계약을 제공·소비하는가”를 답한다.
3. **선택적 읽기**: `INDEX.md`, 자기 프로젝트와 관련 operator의 활성 이니셔티브·이슈·변경·작업 큐,
   현재 작업과 직접 관련된 `docs/`·`initiatives/`·`operators/` 문서만 읽는다. 코드를 단순화하거나
   비직관적 동작을 바꾸기 전에는 `docs/quirks.md`를 해당 project와 symbol로 검색한다. 모든 이력과 완료
   작업을 일괄 로드하지 않는다.
4. **착수 게이트**: 자기 프로젝트와 관련된 `critical` 또는 `major` 이슈가 `open`이나
   `in-progress`이면 일반 작업보다 해당 이슈를 우선 검토한다. 관련 없는 이슈는 작업을 막지 않는다.
5. **작업 로그와 열린 논의 분리**: 결정·발견·시행착오는 UTC 날짜의
   `journal/YYYY-MM-DD-<topic>.md`에 기록하고 새 파일은 `VALIDITY: ACTIVE`로 시작한다. 기존 기록은
   고치지 않고 정정이나 후속 내용을 아래에 추가한다. 단, 판단의 현재 유효성을 나타내는 `VALIDITY`,
   `REPLACED_BY`, `REASON`은 메타데이터 예외로 갱신할 수 있다. 사람의 결정·리뷰나 프로젝트 간 합의를
   기다리는 살아 있는 안건은 journal에 묻지 않고 관련 request/proposal 본문과 `AGENDA.md`에 등재한다.
6. **기준 문서 변경**: 기본 경로는 `proposals/`에 변경안과 근거를 작성하는 것이다. 승인된 변경은
   `docs/`에 반영하고 관련 proposal을 종료한다.
7. **주체 간 요청**: 다른 프로젝트가 수행하거나 operator가 실행·수정해야 할 일은 `requests/`에 작성한다.
   요청 파일에는 배경, 구체적 요청, 수용 기준, 관련 문서, 차단 여부를 포함한다.
   - 규약·계약·소유권의 해석이 충돌하면 에이전트끼리 반복 왕복으로 확정하지 않는다. 각자의 근거를
     `저장소/파일:라인`, 확인 브랜치·커밋과 함께 요청 본문에 기록하고 `AGENDA.md`에 등재해 사용자 결정을
     기다린다.
   - operator 실패·계약 위반은 독립 이슈 파일을 만들지 않고, 수정 책임이 있는 owner 프로젝트 또는
     `operator:<id>`를 대상으로 request를 만든 뒤 그 request를 `ISSUES.md`에 등록한다.
8. **요청 왕복**: 대상은 `open → in-progress → resolved`, 요청자는 결과를 확인한 뒤 `done`으로
   닫는다. 처리 결과와 확인 내용은 원 요청 아래에 append한다.
9. **상태와 이력 분리**: 활성 상태는 `ISSUES.md`, 상태 전환 이력은 UTC 날짜 기준
   `issues/status-YYYY-MM-DD.md`에 남긴다. 종료 항목은 활성 표에서 제거한다.
   - `ISSUES.md`의 요약과 `AGENDA.md`의 기다리는 것은 현재 상태이므로 새 사실이 생기면 문장을
     다시 쓴다. 과거 경위는 요청·제안 본문과 날짜별 이벤트에 누적한다.
   - `done`·`dropped` 요청과 제안은 각각 `requests/archive/YYYY-MM/`,
     `proposals/archive/YYYY-MM/`로 옮긴다. `on-hold`는 재개 가능하므로 활성 폴더에 남긴다.
   - 아카이브는 현행이 아니며 기본 스캔에서 제외한다. 재개할 때만 원래 폴더로 되돌리고 활성 행과 이벤트를
     복원한다. 과거 이력의 기존 경로는 파일명으로 추적할 수 있으므로 일괄 수정하지 않는다. 단, 현재
     등재부·canon·목차가 이동한 파일을 가리키면 같은 변경에서 새 경로로 갱신한다.
10. **변경 알림**: 계약, 기준 문서, 공통 규칙, operator 동작처럼 다른 프로젝트나 operator에 영향을 줄
    수 있는 변경은 UTC 날짜의 당일 `changed/status-YYYY-MM-DD.md`에 기록한다. 영향받는 주체는 자기
    확인 로그에 대응을 남긴다.
11. **실행 작업**: 프로젝트 내부 작업은 `tasks/<project>/pending|in-progress|completed`, operator 자체의
    구현·유지보수 작업은 `tasks/operator-<id>/pending|in-progress|completed`에서 관리한다. 파일의 폴더
    위치만 상태로 사용하며 파일 내부에 중복 상태를 쓰지 않는다.
12. **불확실성**: 검증하지 않은 추론은 `[미검증]`으로 표시하고 근거와 확인 방법을 함께 남긴다.
13. **시간 기준과 표기**: 하네스의 모든 날짜와 시각은 UTC를 사용한다.
    - 시각은 `YYYY-MM-DD HH:MM:SS UTC` 형식으로 기록해 값에 `UTC`를 반드시 명시한다. 시간대가 없는
      로컬 시각이나 `UTC` 표기가 생략된 새 시각 기록은 허용하지 않는다.
    - UTC는 연중 고정 오프셋 `+00:00`으로 사용한다. 서머타임(DST)이나 지역별·계절별 오프셋을 하네스의
      날짜·시각·파일명·스케줄 계산에 적용하지 않는다.
    - 날짜만 사용하는 필드·표 제목·파일명·아카이브 경로의 `YYYY-MM-DD`와 `YYYY-MM`도 UTC 달력 날짜를
      기준으로 계산하며, 해당 템플릿이나 설명에 UTC 기준임을 명시한다.
    - 외부 시스템의 원문 시각은 원래 시간대와 함께 보존한다. 하네스에서 비교·정렬할 때는
      `YYYY-MM-DD HH:MM:SS UTC`로 변환한 값을 함께 기록한다.
    - r0005 이전 append-only 이력은 작성 당시 표기를 그대로 보존한다. 기존 이력을 소급 변환하지 않고
      새 행부터 이 규칙을 적용한다.
14. **INDEX 재확인과 규칙 변경 감지**: 규칙은 같은 날과 같은 세션 안에서도 여러 번 바뀔 수 있다.
    각 에이전트는 마지막으로 읽은 `INDEX.md` 상단의 규칙 버전 스탬프 전체를 기억하고 다음 경계마다
    스탬프를 다시 확인한다.
    전체 파일을 매번 읽을 필요는 없지만 스탬프 확인은 생략하지 않는다.
    - 새 세션 또는 새 작업을 시작할 때
    - 하나의 작업 단위를 마치고 다음 작업으로 넘어갈 때
    - 중단되거나 오래 실행된 작업을 재개할 때
    - 커밋 또는 사용자에게 최종 결과를 보고하기 직전
    - 숙지 버전은 활성 에이전트의 세션 문맥에서만 유지한다. 프로젝트별·에이전트별 영구 숙지 기록을
      만들거나 다른 에이전트의 숙지 상태를 승계하지 않는다.
    - 에이전트가 자신이 마지막으로 숙지한 규칙 버전을 정확히 확인할 수 없거나 문맥 유실이 의심되면
      **미숙지 상태로 간주**한다. 추측으로 버전을 정하지 말고 즉시 `INDEX.md` 전체를 다시 읽은 뒤에만
      작업을 계속한다.
    - 스탬프가 마지막으로 확인한 값과 다르면 즉시 `INDEX.md` 전체와 관련 `changed/` 엔트리를 다시
      읽은 뒤 새 규칙을 적용한다.
    - 스탬프 형식은 `규칙 버전: rNNNN · 최종 갱신: YYYY-MM-DD HH:MM:SS UTC · 변경 요약`이다.
      규칙 버전은 시간과 별개의 단조 증가 값이며 변경 순서의 정본이다. 시각은 감사와 추적을 위한 정보다.
    - `INDEX.md`를 수정한 에이전트는 같은 변경에서 규칙 버전을 정확히 1 올리고, 초 단위 UTC 시각과
      변경 요약을 갱신하며, `changed/`에 영향 `전체`인 엔트리를 남긴다. 이 항목들이 없으면 다른
      에이전트가 규칙 변경을 감지할 수 없다.
    - 동시 수정이 병합되면서 같은 버전이 충돌하면 최종 병합자는 양쪽 중 큰 버전에서 1을 더한 새 버전과
      병합 시각을 기록한다. 날짜가 바뀌어도 버전 번호를 초기화하지 않는다.
15. **커밋 전 공개 위험 정보 검토**: 이 하네스는 공개 저장소에 올라갈 수 있다고 전제한다. 에이전트는
    커밋할 전체 변경을 대상으로 공개 시 위험한 정보가 포함됐는지 반드시 검토한다. 최소한 다음을 확인한다.
    - 비밀번호, API 키, 액세스 토큰, 인증서·개인키, 세션·쿠키, `.env` 값과 기타 인증 정보
    - 개인 식별 정보, 고객 데이터, 운영 데이터와 실제 데이터 샘플
    - 비공개 저장소·문서 URL, 내부 호스트·IP·포트, 계정명, 로컬 절대 경로
    - 특정 조직의 비공개 시스템 구조, 인프라 구성, 보안 정책, 취약점과 운영 절차
    - 라이선스나 권한상 공개할 수 없는 코드·문서·이미지 및 출처 공개가 제한된 자료
    - 위험 정보가 없다고 판단되면 작업 변경을 자동으로 커밋한다.
    - 위험하거나 공개 가능 여부가 불확실한 정보가 하나라도 있으면 **stage와 commit을 중단**하고,
      발견 위치와 위험 이유를 노출하지 않는 범위에서 사용자에게 한 번 확인한다. 사용자의 명시적 결정
      전에는 해당 정보를 삭제·마스킹하거나 커밋하지 않는다.
16. **Git 경계**: 완료한 하네스 변경은 규칙 14의 INDEX 재확인과 규칙 15의 공개 위험 검토를 통과한 뒤
    커밋 메시지 규약에 따라 자동 커밋한다. 자동 push는 하지 않는다. push는 사용자가 명시적으로 요청한
    경우에만 수행한다. 사용자가 커밋하지 말라고 지시하면 그 지시를 우선한다.
    - stage와 commit은 현재 작업에서 직접 변경한 명시적 경로만 대상으로 한다. 기존 변경이 있는
      작업트리에서 `git add -A`, `git add .`, `git commit -a`처럼 범위가 넓은 명령을 사용하지 않는다.
    - 여러 작업이 같은 날짜별 피드 끝에 추가한 행을 보존하도록 `changed/status-*.md`,
      `issues/status-*.md`, `feedback/status-*.md`에만 union 병합을 사용한다. 현재 상태를 수정하는 파일과
      저널에는 적용하지 않는다.
    - 커밋 전 staged diff, 커밋 후 커밋 통계를 확인해 다른 작업의 파일이 섞이지 않았는지 검증한다.
    - 하네스 기록과 제품 코드 변경은 서로 다른 저장소의 별도 커밋으로 유지한다.
17. **operator 식별과 거버넌스**: 실행 자동화는 에이전트 정체성과 분리해 `OPERATORS.md`에
    `operator:<id>`로 등록하며 파일과 디렉터리에는 `operator-<id>`를 사용한다. operator를 실행하거나
    수정하는 에이전트의 정체성은 여전히 소유 프로젝트의 `project-id`다. operator는 프로젝트와 같은
    request·issue·changed·task 흐름을 사용하며 세부 계약은 `operators/README.md`를 따른다.
    - 개발·수정·수동 실행 요청은 `requests/`에 `target: operator:<id>`로 등록할 수 있다.
    - 실패·계약 위반·반복 장애·차단은 `ISSUES.md`와 `issues/`에서 관련 operator와 영향 프로젝트를
      함께 기록한다.
    - 동작 계약이나 영향 범위 변경은 `changed/`에 알린다.
    - operator 자체의 구현·유지보수는 `tasks/operator-<id>/`에서 관리한다.
    - 정상적인 반복 실행은 request나 issue를 만들지 않는다. 실행 증거는 operator 문서에 정한 로그 또는
      외부 실행 기록에 남기고, 사람의 판단·다른 주체의 작업·계약 수정·작업 차단이 필요할 때만 하네스
      이슈로 승격한다.
18. **타 프로젝트 저장소 경계**: 교차 저장소 계약과 영향 확인을 위해 담당 프로젝트가 아닌 저장소를
    읽고 검색하며 `git log`를 확인할 수 있다. 단 수정·stage·commit·브랜치 생성·빌드·실행은 담당
    프로젝트 저장소에서만 한다. 타 프로젝트에 필요한 변경은 규칙 7의 request로 넘긴다.
    - 타 저장소에서 얻은 사실은 로컬 브랜치가 현행과 다를 수 있으므로 `[미검증]`으로 기록한다.
    - 근거에는 저장소 식별자, 파일과 줄, 확인한 브랜치와 커밋을 포함한다.
    - 최종 확인은 해당 프로젝트의 에이전트가 맡는다. 외부 조사가 요청 왕복을 대체하지 않는다.
19. **제품 코드 주석과 하네스 이력 분리**: 제품 코드 주석에 승인 경위, 과거 명칭, 커밋 해시, 날짜별
    결정 이력 같은 하네스 provenance를 넣지 않는다. 그런 이력은 decision/ADR, changed, journal과 커밋
    메시지에서 관리한다. 코드 주석은 코드만으로 드러나지 않는 현재 계약·제약·불변식만 설명한다.
20. **공동 이니셔티브(`initiatives/`)**: 둘 이상의 프로젝트·역할·operator가 하나의 측정 가능한 결과를
    함께 달성하는 협업 단위를 **Initiative(이니셔티브)**라고 한다. “왜 함께 일하는가, 어떤 결과가 되면
    끝나는가”를 답하며 프로젝트나 에이전트의 정체성이 아니다.
    - 활성 상태와 한 줄 결과는 `INITIATIVES.md`, 상세 목표·범위·참여 주체·완료 기준·연결 작업은
      `initiatives/<id>.md`가 정본이다. 논리 식별자는 `initiative:<kebab-id>`를 사용한다.
    - 상태는 `proposed → active → completed`를 기본으로 하고 진행 중 `blocked`·`paused`, 종료 시
      `cancelled`를 사용할 수 있다. `blocked`에는 반드시 원인이 되는 `ISSUES.md` 행을 연결한다.
    - initiative는 task·request·issue의 상태를 대신하지 않는다. 프로젝트 내부 실행은 task, 주체 간
      인계는 request, 위험·차단은 issue, 사람 결정은 agenda에 기록하고 모두 initiative 문서에 연결한다.
    - `completed`·`cancelled` 시 완료 기준과 결과 또는 취소 사유를 기록한 뒤
      `initiatives/archive/YYYY-MM/`로 옮기고 활성 등록부에서 제거하며, `INITIATIVES.md` 종료 대장에
      한 줄을 남긴다. `paused`는 재개 가능하므로 활성 영역에 남긴다.
    - 한 프로젝트 안에서 독립적으로 끝나는 일은 initiative를 만들지 않고 task로 관리한다. 여러 주체의
      공동 결과·통합 완료 기준·조정이 필요할 때만 initiative를 만든다.
21. **지식 유효성과 무효화**: 저널의 과거 사건은 보존하되 그 안의 판단이 현재도 유효한지는
    `ACTIVE`, `SUPERSEDED`, `REJECTED`로 명시한다. `SUPERSEDED`에는 대체 대상과 사유,
    `REJECTED`에는 사유가 필수다. 현재 작업에서 판단을 실제로 뒤집었다면 같은 변경에서 원본 저널의
    유효성 메타데이터와 `INVALIDATIONS.md`를 갱신한다. 아카이브는 오래된 기록의 보관 위치일 뿐
    무효화를 뜻하지 않는다. 세부 형식은 `journal/README.md`를 따른다.
22. **큐레이션과 역할**: worker는 자기 프로젝트 작업과 실행 기록을 남기고, curator는 검증된 현행
    판단의 canon 승격, 무효화 색인, quirk, 아카이브와 하네스 정합을 관리한다. 역할은 책임 묶음일 뿐
    규칙 2의 project-id를 대체하지 않는다. 시작할 때 `operator:curation-status`를 실행하고
    `ATTENTION`이면 첫 사용자 응답에 알리되, 이 신호만으로 현재 작업을 막거나 자동 교정하지 않는다.
    큐레이션을 실제로 완료한 때만 `CURATION.md`의 시각을 갱신한다. 큐레이션 중에는
    `operator:harness-audit` 결과도 확인한다. 세부 책임은 `docs/roles.md`를 따른다.
23. **Quirk 등록부**: 모르고 제거·단순화하면 동작을 깨뜨리는 비직관적 현행 불변식은 검증 근거와 영향,
    검색 가능한 symbol을 `docs/quirks.md`에 기록한다. 단순 복잡성·과거 경위·추측은 등록하지 않는다.
    코드 주석은 프로젝트 규칙이 허용할 때 안정 quirk ID를 가리키는 현재 불변식 앵커만 둘 수 있고,
    승인 경위·날짜·사람·커밋 해시는 넣지 않는다.
24. **현재 상태 요약과 살아있는 canon**: 누적형 기록과 재작성형 현재 상태를 구분한다.
    - `journal/`, `changed/`, `issues/status-*`, `feedback/status-*`는 당시 사실의 누적형 기록이므로
      append한다.
    - `ISSUES.md`의 요약, `AGENDA.md`의 기다리는 것, 현재 상황을 주장하는 canon은 재작성형이다. 정정을
      뒤에 덧붙이지 않고 첫 문장이 지금 상태와 닫히기 위한 다음 행동을 말하도록 다시 쓴다.
    - 현황·인벤토리·체크리스트처럼 코드와 운영 상태에 따라 낡는 문서는 `docs/README.md`의 살아있는 문서
      등록부에 등재하고 기준 시각, 그 뒤 미반영분, 현행 정본을 머리말에 표시한다.
    - 상태 요약을 다시 써도 같은 변경의 날짜별 이벤트는 append해 이력을 보존한다.
25. **식별자 보고 가독성**: 사용자와 대화하거나 긴 문서에서 항목을 처음 가리킬 때 `i-...`, `c-...`,
    `Q-NNN`, 순번 같은 식별자만 쓰지 않고 짧은 헤드라인을 함께 붙인다. 식별자는 추적 앵커이며 사람이
    이전 문맥을 되짚지 않고도 대상을 알아볼 수 있어야 한다. 같은 문맥에서 반복할 때는 식별자만 쓸 수 있다.
26. **검증 결과 피드백**: 작업 완료, 리뷰, 검증과 변경 승격에서 지침 평가에 정보가 있는 성공·실수를
    근거와 함께 `feedback/`에 기록한다. 단순 행동 횟수, 자기 평가, 검증되지 않은 추론은 세지 않는다.
    - 성공과 실수는 서로 상쇄하는 점수로 만들지 않는다. 성공은 지침의 효과, 실수는 누락·모호성·미준수,
      실행 오류와 외부 실패의 원인을 검토하는 증거다.
    - 시작할 때 `operator:feedback-status`를 실행한다. `ATTENTION`이면 반복 pattern, major 이상 실수 또는
      스키마 오류를 첫 사용자 응답에 알리되 이 신호만으로 작업을 막거나 기준 문서를 자동 수정하지 않는다.
    - curator는 원인과 반례를 확인해 지침 문제로 검증된 경우에만 proposal을 만들고, 사람의 승인을 받은
      변경만 canon 또는 이 파일에 반영한다. 변경 후 같은 pattern의 재발 여부로 효과를 다시 확인한다.
    - 형식, 분류, 임계값과 개선 절차는 `FEEDBACK.md`, `feedback/README.md`,
      `docs/outcome-feedback.md`를 따른다.
27. **변경 승격과 리뷰 체크포인트**: 작업 변경은 별도 작업용 worktree 또는 임시 작업 브랜치에서 만들고,
    사람의 승인 없이 원격 PR·feature·release·정본이나 배포 단계로 승격하지 않는다. 승격 경로와 리뷰
    스냅샷은 서로 다른 축이다.
    - 자동화가 만드는 작업용 worktree에는 worktree와 수명이 같은 임시 작업 브랜치만 연결한다. 로컬
      `review/*`, 원격 PR, feature, 통합·릴리스·배포·정본처럼 검토하거나 이동할 참조는 작업 브랜치로
      연결하지 않고 명시적 ref 또는 detached commit으로 다룬다.
    - 로컬 `review/<topic>_YYYYMMDDTHHMMSSZ`는 clean 작업 결과에만 한 번 생기는 단계가 아니라, 작업
      결과·PR head·기능 통합 후보·릴리스 후보 등 **어느 committed checkpoint에서나** 만들 수 있는 불변
      제출 스냅샷이다. 원격에 push하거나 생성 뒤 이동·amend·reset·직접 커밋하지 않으며, checkpoint가
      달라지면 새 UTC 타임스탬프의 review를 만든다.
    - 리뷰어에게 이동 가능한 통합·검증·릴리스 참조를 검토 대상으로 주지 않는다. 정확한 review commit을
      detached 상태로 열게 해 참조 이동을 막지 않으며, PR head나 승격 후보가 바뀌면 기존 승인을
      무효화하고 새 review에서 검증·리뷰를 다시 수행한다.
    - 승인된 결과만 보호된 feature로 통합하고, release·배포 브랜치 또는 정본 승격에는 별도 통합 검증과
      승인을 요구한다. 태그 배포는 정본 브랜치에 먼저 병합한 정확한 commit만 태그한다.
    - 작업용 worktree를 제거할 때는 임시 작업 브랜치 commit이 원격 작업 브랜치·feature·정본·tag 같은
      지속 가능한 ref에서 도달 가능한지 확인한다. 로컬 review만 남은 상태는 보존 완료로 보지 않는다.
      보존 ref를 만든 뒤 worktree와 임시 로컬·원격 작업 브랜치를 정리하고 잔존 여부를 기계적으로 확인한다.
    - 저장소별 이름과 배포 방식이 달라도 임시 작업 브랜치의 수명, review 불변성·원격 push 금지,
      checkpoint 변경 시 승인 무효화 원칙은 유지한다. 전체 계약과 강제 장치는
      `docs/change-promotion.md`, 로컬 도구는 `operator:review-branch`를 따른다.
28. **살아 있는 세션 조정과 통신 예산**: 세션 등록부와 직접 메시지 기능이 있는 환경에서는 커서 전진,
    append-only가 아닌 공유 파일 수정, worktree 일괄 정리, 공유 런타임·포트 점유 직전에만 겹치는 살아
    있는 세션을 확인하고 직접 조정한다. 모든 세션 시작을 막는 게이트로 쓰지 않는다.
    - 세션의 생존 여부와 정체성 정보를 분리한다. 현재 턴 실행 여부, 최근 활동 시각, 제목, 브랜치명만으로
      대상이나 생존을 판정하지 않는다. 정규화한 작업 디렉터리의 `project-id`와 worktree를 기준으로 하고,
      같은 위치의 세션이 여럿이면 안정적인 session id와 task·소유 경로를 함께 대조한다.
    - append-only가 아닌 공유 파일과 단일 공유 자원은 응답을 먼저 받아 소유권을 확인한 세션 하나가
      변경한다. 무응답은 쓰기 허가가 아니며, 다음 세션은 해제 메시지를 받은 뒤 파일과 Git 상태를 다시
      읽고 작업한다.
    - 세션 간 메시지는 직접 질문의 답, 새 실측·상태·근거·산출물처럼 **새 값이 있을 때만** 보낸다.
      단순 확인·감사·종료 인사는 보내지 않으며 `회신 불요`를 받은 세션은 답하지 않는다.
    - 하나의 협업 판단은 `tx:<topic>-YYYYMMDDTHHMMSSZ`로 식별하고 모든 세션·양방향 메시지를 합해
      **최대 10건**으로 제한한다. fan-out은 수신자 수만큼 세고, 10번째 수신자는 답하지 않으며 11번째
      전송은 금지한다. 응답자는 받은 tx id를 계승하고 peer 메시지나 자동화 신호로 카운터를 초기화하지
      않는다. 사람이 새 프롬프트를 보내면 이전 tx를 닫고 후속 통신은 새 tx로 시작한다.
    - 각 세션은 사람이 자기 세션에 직접 보낸 마지막 프롬프트 뒤의 **세션 간 수신만** 별도로 센다.
      **5번째 수신 직후** 추가 메시지와 가변 상태 변경을 멈추고 사용자에게 진행 여부를 묻는다. 사용자가
      계속을 승인하는 새 프롬프트를 보내면 해당 세션의 수신 카운터를 초기화하고 후속 통신은 새 tx로
      시작한다.
    - 어느 제한이든 걸리면 사용자에게 카운트와 송신 주체, 지금까지의 산출물, 멈출 때 잃는 것, 다음
      행동을 함께 보고한다. 사람과 직접 대화할 수 없는 worker는 이 보고를 사람 대면 조정 세션에 반환한다.
    - 관측과 통신은 각 세션의 journal에 `**SESSION-COMM:**`으로 남긴다. 공개 기록에는 절대경로를 넣지
      않는다. 답이 계약·현재 상태·규칙·후속 작업의 근거가 되면 request·changed·decision·canon으로
      승격해 비공개 세션 합의가 정본을 우회하지 않게 한다.
    - 등록부나 직접 메시지 기능이 없거나 관측 범위가 불완전하면 다른 세션이 없다고 단정하지 않고 규칙
      1과 16의 보수적 직렬·Git 경계로 돌아간다. 정의, 카운팅과 로그 형식은
      `docs/session-coordination.md`와 `journal/README.md`를 따른다.
29. **조합 가능한 저장공간과 손실 추적**: 하네스의 기록을 하나의 데이터 모델이나 저장 기술에 강제하지
    않는다. 정보의 성격, 보존할 특성, 허용 손실, 질의 방식과 비용에 따라 `storage/registry.json`의
    active Storage Space를 선택하고 필요할 때 여러 표현을 조합한다.
    - 기존 journal·request·issue·changed·task와 현재 상태 정본은 이동하거나 일괄 변환하지 않는다.
      definition의 `locations`로 현재 record space에 연결하며, 기존 append-only 기록은 소급 수정하지 않는다.
    - 모든 공간은 `evidence`, `record`, `projection`, `index`, `cache` 중 역할과 storage kind, 보존·손실,
      query mode, 쓰기·일관성·보존 정책, provenance, rebuild, 비용·권한·공개 안전성을 선언한다.
      projection·index·cache를 정본으로 사용하지 않고, projection·index는 source에서 재생성할 수 있어야 한다.
    - 같은 관찰을 여러 공간에 표현하면 Cross-Space Catalog에 representation과 source lineage를 연결한다.
      파생 표현은 transformation의 방법·버전·입출력·보존 특성·손실과 가역성을 기록한다. Object·Relation·
      Field·시계열·의미 검색은 선택 가능한 저장 전략이지 하네스 전체의 필수 중심 모델이 아니다.
    - 새 정보는 정확한 ID·상태·시간·관계·수치·유사성·근거·잔차 중 필요한 query mode를 먼저 정하고,
      구조화 조건과 최소 공간부터 조회한다. Context는 현재 project·task와 직접 관련된 결과만 예산 안에서
      조립하고 사용 공간, 잘린 결과와 손실을 드러낸다. 중요한 판단은 record·evidence로 돌아가 재확인한다.
    - 적합한 active 공간이 없으면 임의 디렉터리나 외부 저장소를 추가하지 않는다. proposal에서 definition,
      schema, adapter, 비용, migration과 소급 여부를 승인받은 뒤 registry에 등록한다. 저장공간·catalog·
      transformation 변경 후에는 `operator:storage-spaces audit`과 결정적 index 재생성을 수행한다.
    - 원시 제품 자료와 비공개 시스템 정보를 복제하지 않는다. representation·source ref는 공개 안전한
      프로젝트 한정 식별자를 사용하며 생성 index와 view도 규칙 15의 별도 공개 위험 검토를 받는다.
      상세 계약은 `docs/storage-architecture.md`, 형식은 `schemas/`, 실행은 `operator:storage-spaces`를 따른다.
30. **저장 구현 재사용과 Adapter 이식성**: 새 저장 요구가 생기면 구현부터 만들지 않는다. 정보 형태,
    query mode, 일관성·보존, provenance·rebuild, 허용 손실, 권한·비용과 장애 시 data access를 먼저
    Storage Space Definition으로 확정하고, 관련 공개 연구·기존 구현·범용 엔진의 adapter 가능성을 평가한다.
    - 구현 선택의 `selection_policy`는 `reuse-first`다. 이는 외부 제품 우선이 아니라 직접 구현 전에 기존
      지식과 구현을 비교한다는 뜻이다. 현재 전략은 `native`, `adapter`, `hybrid`, `custom-minimal` 중 하나로
      선언하고, 적합한 구현이 없거나 하네스 고유 제어 계층일 때만 최소 범위를 직접 구현한다.
    - 검증한 공개 원문은 `research/catalog.json`에 `research:<id>`로 등록하고 기본 상태를
      `reference-only`로 둔다. reference는 채택 승인이 아니며, 실제 후보는 space definition에서
      `discovered → evaluating → optional → selected` 또는 `rejected`로 관리한다. selected에는 license와
      유지보수 상태, 실제 fixture의 capability·손실·비용 검증이 필요하다.
    - 외부 엔진·서비스는 `storage/adapters/registry.json`에 등록한 `adapter:<id>`를 통해서만 active space에
      연결한다. adapter는 `write`, `query`, `trace`, `export`, `rebuild`, `health`의 지원·저하·미지원 상태를
      숨김없이 선언한다. 연결만으로 외부 시스템이나 그 결과가 evidence·record의 정본이 되지 않는다.
    - active space는 공개 export 형식, vendor lock-in, exit plan, fallback adapter 또는 직접 접근,
      장애 시 남는 data access와 degraded query mode를 선언한다. evidence·record의 fallback은 핵심 자료
      접근이 `unavailable`이 될 수 없고, projection·index는 source에서 재생성할 수 있어야 한다.
    - adapter 채택·교체·제거는 proposal에서 migration·소급·비용·권한·공개 안전성을 승인받고 space
      definition·adapter registry·fixture·`changed/`를 같은 변경에서 갱신한다. 연구 source만 공개 HTTPS
      URL을 허용하며 비공개 문서·구현 endpoint와 원문 본문은 기록하지 않는다. 세부 계약은
      `docs/storage-adapters.md`, 형식은 `schemas/storage-adapter*.json`과
      `schemas/research-catalog.schema.json`, 검사는 `operator:storage-spaces`를 따른다.
31. **로컬 저장 실행과 기억 신뢰성의 지연 도입**: 현재의 파일·Git evidence·record를 사람이 검토 가능한
    정본으로 유지한다. 로컬 DB, 전문 index, background service, Query Planner·Context Composer와 Local
    Storage Broker는 현재 operator의 기능으로 간주하지 않으며, 반복적인 탐색·문맥·동시 쓰기·인출 실패가
    작업 시간·latency·token·중복률·정확도 측정에서 주요 병목으로 확인된 뒤 별도 proposal로 단계 도입한다.
    - 파생 database·index·cache·작업 memory는 Git에 공유하는 새 정본이 아니다. 공유 record와 event,
      transformation·adapter version에서 재생성할 수 있어야 하며 실행 계층 실패 시 파일 기반 읽기와 핵심
      record 접근으로 복귀해야 한다. 초기 확장은 embedded를 우선하고 실제 동시성·격리 요구가 있는 공간만
      local service로 분리한다. remote/shared는 별도 권한·동기화·충돌 결정을 요구한다.
    - 도입 proposal은 반복 병목의 기준 측정, 최소 space와 실행 방식, 공개 안전성, 비용·token budget,
      adapter·migration·rebuild·rollback, 성공·중단 기준을 포함한다. 명확한 증거 없이 모든 공간이나 broker를
      미리 구현하지 않고 단계별 proposal과 검증을 독립적으로 거친다.
    - future query 계약은 `found`, `not_found`, `not_searched`, `not_indexed`, `inaccessible`, `stale`,
      `ambiguous`, `partial`, `failed`를 구분한다. `not_found` 이외 상태를 자료 부재로 해석하지 않으며 조회한
      공간·제외 이유·범위·freshness·version·limit·conflict·evidence·fallback과 Query Trace를 드러낸다.
    - future Memory Fault는 필요한 정보가 문맥에 없거나 stale·모호·부분적일 때 최소 추가 조회와 source
      재검증을 요구하는 신호다. 권한 확대, 무제한 전체 검색이나 자동 확정의 근거가 아니며 비용·위험 한계나
      사용자 결정 경계에 도달하면 상태와 시도한 fallback을 보고하고 멈춘다.
    - 저장 요청 접수와 durable record, index·projection 반영을 구분한다. 중요한 record는 가능한 경우
      read-after-write로 확인하고, 파생 갱신 지연·공간 간 불일치·검색하지 않은 범위를 숨기지 않는다. 전체
      실행 로드맵은 `docs/local-storage-runtime.md`, 실패 단계·인출 상태·trace 계약은
      `docs/memory-reliability.md`를 따른다.

## 권장 시작 순서

1. `PROJECTS.md`에서 자기 프로젝트 식별자를 확인한다.
2. operator 관련 작업이면 `OPERATORS.md`에서 식별자·소유 프로젝트·계약 문서를 확인한다.
3. `./operators/curation-status.sh`를 실행하고 `ATTENTION`이면 첫 사용자 응답에 상태를 알린다.
4. `./operators/feedback-status.sh`를 실행하고 `ATTENTION`이면 첫 사용자 응답에 상태를 알린다.
5. `INITIATIVES.md`에서 자기 프로젝트·operator가 참여하는 활성 이니셔티브를 확인한다.
6. `ISSUES.md`에서 자기 프로젝트와 관련 operator의 활성 이슈를 확인한다.
7. `changed/`에서 자기 프로젝트나 operator가 아직 확인하지 않은 영향을 확인한다.
8. 해당 `tasks/<project>/` 또는 `tasks/operator-<id>/`의 미완료 작업 제목만 확인한다.
9. `AGENDA.md`에서 자기 프로젝트·operator가 참여하는 열린 논의를 확인한다.
10. 지금 수행할 작업과 직접 관련된 문서와 `docs/quirks.md`의 관련 project·symbol만 연다.
11. 작업이 여러 정보 표현의 저장·조회·문맥 조립을 바꾸면 `storage/registry.json`과 관련 definition을
    확인하고 `operator:storage-spaces audit`을 실행한다.

## 커밋 메시지 권장 형식

`<type>(<project>): <subject>`

- type: `docs`, `journal`, `proposal`, `request`, `task`, `chore`
- project: `PROJECTS.md`에 등록된 식별자. 하네스 자체 변경은 `harness`
