# Multi-Repo Domain Harness

## 문서 안내

- **처음 설치하는 사람**: [macOS 데스크톱 앱에 하네스 적용하기](#처음-적용하기-macos-데스크톱-앱)를
  따라 Codex 또는 Claude Code에 하네스를 연결한다.
- **작업을 시작하는 에이전트**: [에이전트 작업 시작](#에이전트-작업-시작)에 따라
  [`INDEX.md`](INDEX.md)를 먼저 읽는다.
- **운영 방식을 이해하려는 사람**: [설계 원칙](#설계-원칙)과 [핵심 용어](#핵심-용어)를 읽는다.

여러 도메인과 여러 코드 저장소를 하나의 작업 맥락으로 연결하는 문서 기반 하네스다.

이 저장소는 제품 코드를 소유하지 않는다. 대신 저장소별 책임, 공통 계약, 교차 저장소 요청,
영향 있는 변경, 활성 이슈와 실행 작업을 한곳에서 추적한다. AI 코딩 세션과 사람이 같은 운영
규칙을 사용해 작업을 이어받을 수 있도록 현재 상태와 이력을 분리한다.

## 처음 적용하기: macOS 데스크톱 앱

이 절은 Mac에 하네스를 내려받고 Codex 데스크톱 앱의 로컬 프로젝트 또는 Claude Desktop의
**Code > Local** 세션에서 사용하는 경우를 다룬다. 일반 Claude Chat 탭이나 클라우드·SSH 세션은 로컬
파일 경로를 같은 방식으로 읽는다고 가정하지 않는다.

macOS에서 `~`는 현재 사용자의 홈 디렉터리다. 하네스는 `~/.codex/config.toml`이나
`~/.claude/settings.json`에 임의의 설정 키로 등록하지 않는다. 이 파일들은 도구·권한 같은 실행 설정에
사용하고, 하네스 진입 규칙은 Codex의 `AGENTS.md`와 Claude Code의 `CLAUDE.md`에 선언한다.

### 1. 하네스 절대경로 확인

하네스 저장소에서 `pwd`를 실행해 절대경로를 확인한다. 아래 예시의
`/absolute/path/to/multi-repo-domain-harness`는 이 값으로 바꾼다. 실제 사용자명이나 로컬 절대경로가
들어간 설정 파일은 공개 저장소에 커밋하지 않는다.

### 2. Codex에 전역 하네스 선언

Codex는 기본적으로 `~/.codex/AGENTS.md`를 사용자 전역 지침으로 읽는다. 디렉터리가 없다면
`mkdir -p ~/.codex`로 만든 뒤, 기존 내용을 보존하면서 다음 진입 규칙을 추가한다.

```md
# Shared multi-repo harness

모든 저장소 작업에서 다음 절차를 따른다.

1. 다른 프로젝트 파일을 읽거나 수정하기 전에
   `/absolute/path/to/multi-repo-domain-harness/INDEX.md` 전체를 읽는다.
2. 현재 Git 저장소 이름을 `project-id`로 사용한다.
3. `INDEX.md`의 시작 절차, 읽기 범위, 기록 위치와 Git 경계를 따른다.
4. 작업 단위 전환, 중단 후 재개, 커밋과 최종 보고 전에는 규칙 버전 스탬프를 다시 확인한다.
5. 스탬프가 바뀌었거나 마지막 숙지 버전을 확신할 수 없으면 `INDEX.md` 전체를 다시 읽는다.
```

저장소 루트의 `AGENTS.md`에는 그 저장소에만 필요한 규칙을 둔다. Codex는 사용자 전역 지침과 저장소
지침을 함께 읽으므로 하네스 전체를 각 저장소에 복사할 필요가 없다. 단,
`~/.codex/AGENTS.override.md`가 있으면 같은 위치의 `AGENTS.md`보다 먼저 선택되므로, 위 규칙을 override
파일에 합치거나 해당 override를 사용하지 않는 상태인지 확인한다.

### 3. Claude Code에 전역 하네스 선언

Claude Desktop에서는 일반 Chat 탭이 아니라 **Code** 탭에서 **Local** 환경과 작업할 저장소 폴더를
선택한다. `~/.claude/CLAUDE.md`가 없다면 `mkdir -p ~/.claude`로 디렉터리를 만든 뒤 파일을 생성하고,
기존 파일이 있다면 다음 내용을 병합한다.

```md
@/absolute/path/to/multi-repo-domain-harness/INDEX.md

# Shared multi-repo harness

- 위에서 불러온 `INDEX.md`를 운영 규칙의 정본으로 사용한다.
- 현재 Git 저장소 이름을 `project-id`로 사용한다.
- 작업 단위 전환, 중단 후 재개, 커밋과 최종 보고 전에는 원본 `INDEX.md`의 규칙 버전 스탬프를
  다시 확인한다.
- 스탬프가 바뀌었거나 마지막 숙지 버전을 확신할 수 없으면 원본 `INDEX.md` 전체를 다시 읽는다.
```

Claude Code의 `@절대경로` 표기는 해당 파일을 세션 시작 문맥으로 불러온다. 팀과 공유할 프로젝트 규칙은
저장소 루트의 `CLAUDE.md` 또는 `.claude/CLAUDE.md`에 둔다. 이미 `AGENTS.md` 하나로 프로젝트 규칙을
관리한다면 루트 `CLAUDE.md`에 `@AGENTS.md`를 적어 같은 규칙을 재사용할 수 있다. 개인별 경로나 설정은
커밋 대상 파일 대신 `~/.claude/CLAUDE.md` 또는 gitignore된 `CLAUDE.local.md`에 둔다.

이 하네스 저장소에 포함된 루트 `AGENTS.md`와 `CLAUDE.md`는 세부 규칙을 복제하지 않고 `INDEX.md`와
에이전트 실행 계약으로 연결하는 최소 bootstrap만 제공한다.

하네스 저장소 자체를 Codex·Claude의 작업 대상으로 열 때는 linked worktree가 아닌 기존 primary checkout을
직접 사용한다. 앱이나 자동화가 별도 worktree를 만들었다면 그 세션에서는 하네스를 변경하지 말고 primary
checkout에서 같은 작업을 다시 시작한다. 이 제한은 하네스 자체에만 적용되며 참여 제품 저장소의 격리
worktree 정책은 그대로 유지된다.

그 이유는 여러 하네스 세션이 같은 working directory를 읽어 request·changed·task·journal과 아직 commit되지
않은 기록까지 즉시 공유해야 하기 때문이다. primary checkout은 물리적 위치이고 `main`은 승인된 Git 이력의
정본 branch이므로 서로 같은 개념이 아니다. primary 안에서 임시 작업 branch를 사용해도 되며 `main`에 직접
commit할 필요는 없다.

같은 하네스의 모든 로컬 세션은 전역 지침에서 **동일한 하나의 절대경로**를 가리켜야 한다. 별도 clone은
기술적으로 자기 primary checkout이어서 guard를 통과할 수 있지만 working directory를 공유하지 않으므로
이 목적을 충족하지 않는다.

### 4. 적용 확인

설정 파일을 바꾼 뒤에는 이미 열려 있던 대화를 재사용하지 말고 새 작업 또는 새 세션을 시작한다.

- Codex: 저장소를 프로젝트로 연 뒤 “적용된 하네스의 `INDEX.md` 규칙 버전 스탬프와 현재
  `project-id`를 말해 달라”고 요청한다.
- Claude Code: `/context`에서 `CLAUDE.md`가 Memory files에 포함됐는지 확인한 뒤 같은 질문을 한다.
- 두 앱 모두 응답한 `project-id`가 현재 저장소 이름과 같고, 스탬프가 실제 `INDEX.md` 상단과 같아야
  적용된 상태다.

하네스가 선택한 프로젝트 폴더 밖에 있어 읽기 승인이 나타나면 해당 하네스 디렉터리에 대한 읽기만
허용한다. 쓰기는 제품 저장소와 하네스 저장소의 경계를 유지해 각각 별도 변경과 별도 커밋으로 처리한다.

## 에이전트 작업 시작

에이전트는 이 README를 운영 절차의 정본으로 사용하지 않는다. 새 작업을 시작하면 다른 하네스 파일을
읽거나 수정하기 전에 [`INDEX.md`](INDEX.md) 전체를 읽고, 그 안의 시작 절차와 현재 작업에 필요한 문서
선택 규칙을 따른다. 세부 절차는 `INDEX.md`에서만 관리하며 README에 중복하지 않는다.

## 설계 원칙

- 현재 상태의 정본과 시간순 이력을 분리한다.
- 현재 상태 요약은 다시 쓰고, 당시 사실을 보존하는 이벤트와 journal은 append한다.
- 하나의 데이터 모델을 강제하지 않고 보존 특성·허용 손실·질의 목적이 다른 저장공간을 공통 registry와
  catalog로 조합한다. 오브젝트·관계·필드·시계열·의미 검색은 필요할 때 선택하는 저장 전략이다.
- 파생 projection·index·cache를 정본으로 사용하지 않고 source lineage와 transformation을 통해 무엇을
  보존·압축·손실했는지 추적한다.
- 새 저장 구현은 capability를 먼저 정의하고 공개 연구·기존 구현을 평가한 뒤 native·adapter·hybrid·
  custom-minimal 중 최소 전략을 택한다. 외부 구현에는 공개 export, 교체와 장애 fallback을 요구한다.
- 현재 파일·Git record를 사람 검토 가능한 정본으로 유지한다. 로컬 DB·전문 index·broker는 반복 병목이
  측정된 뒤에만 재생성 가능한 실행 계층으로 단계 도입하며, 실패하면 파일 기반 경로로 복귀한다.
- 저장됐다는 사실과 작업에서 인출됐다는 사실을 구분한다. 미래 인출 계층은 조회 범위·freshness·상태와
  Query Trace를 드러내고 `not_found`를 `not_searched`·`stale`·`partial`과 혼동하지 않아야 한다.
- 하네스 정책·설계·용어의 열린 사유는 `explorations/`에 비정본으로 보존한다. 일반 작업 시작에는 읽지
  않으며 구체적인 변경·판단·실행이 생길 때만 proposal·agenda·task·canon으로 명시적으로 승격한다.
- 변경에 따라 낡을 수 있는 문서는 기준 시각·미반영분·현행 정본을 스스로 밝힌다.
- 세션·사람·도구가 아니라 프로젝트 식별자를 작업 주체로 사용한다.
- 요청의 목표와 권한을 분리한다. 조사·리뷰·수정·외부 반영은 서로 다른 허가이며, 위임과 지속 요구도
  원래 권한을 넓히지 않는다.
- 하위 에이전트·도구 결과와 exit code를 완료 증거로 자동 해석하지 않는다. 최신 변경 뒤 실제 대상과
  범위를 검증하고 작성·검증·commit·push·merge·배포 상태를 구분한다.
- 긴 작업의 현재 판단·진행·재사용 경험을 구분하고, 과거 경험은 현재 환경의 정답이 아니라 재검증할 prior로
  취급한다. 현재 결정에 필요한 외부 상태만 선택적으로 읽고 갱신한다.
- 실행 자동화는 `operator:<id>`로 등록하되 이를 에이전트 정체성과 혼동하지 않는다.
- 공동 목표는 `initiative:<id>`로 등록하되 프로젝트·task·request의 정체성과 상태를 대체하지 않는다.
- 과거 기록과 그 안의 판단이 지금도 유효한지는 분리하고, 대체·기각된 판단을 검색 가능한 색인에 남긴다.
- 검증된 성공·실수는 성과 점수가 아니라 지침의 효과와 개선 필요성을 판단하는 증거로 사용한다.
- 작업본, 공동 PR, feature 통합과 release·정본 승격을 분리하고, 리뷰는 어느 committed checkpoint에서나
  별도로 생성하는 로컬 불변 스냅샷으로 다룬다.
- 참여 프로젝트가 자동화 작업용 worktree를 사용할 때는 수명이 같은 임시 작업 브랜치만 연결하고, 삭제 전
  결과가 지속 가능한 ref에 보존됐는지 확인한다. 하네스 저장소 자체의 변경은 primary checkout에서만 한다.
- 살아 있는 세션은 위험 경계에서만 직접 조정하고, 세션 간 통신에는 트랜잭션 총량과 사람 프롬프트 이후
  수신량이라는 독립된 예산을 적용한다.
- 하네스 세션은 primary working directory로 최신 파일을 공유하고, 짧은 소유·충돌 조정은 직접 메시지,
  오래 남아야 할 결과는 request·changed·task·journal에 기록한다. 실시간 append progress stream은 아직
  active 기능이 아니다.
- worker·reviewer·curator는 책임 역할이며 프로젝트 정체성을 대체하지 않는다.
- 검증된 실행 결과는 곧바로 규칙에 붙이지 않고 trigger·evidence·scope가 있는 Guidance Candidate로
  컴파일해 `feedback/candidates/`에 생명주기를 보존한다. 기존 지침과 비교해 추가·병합·수정·기각하고
  승인된 최소 지침만 선택적으로 읽는다.
- 비직관적 현행 불변식은 검증 근거·영향·검색 가능한 symbol과 함께 quirk로 관리한다.
- 식별자와 순번은 처음 언급할 때 짧은 헤드라인을 함께 붙여 사람이 문맥을 되짚지 않게 한다.
- 전체 문서를 매번 읽지 않고 현재 작업에 관련된 문서만 선택한다.
- 모든 날짜와 시각은 UTC 고정 오프셋 `+00:00`을 사용하고 시각 값에 `UTC`를 반드시 명시한다.
  서머타임(DST)이나 지역별·계절별 오프셋은 적용하지 않는다.
- 검증되지 않은 판단은 `[미검증]`으로 표시한다.
- 기준 문서는 보호하고 변경 제안과 작업 로그를 별도로 남긴다.
- 특정 조직이나 시스템의 구조를 전제하지 않는다.

완료한 변경은 공개 위험 정보 검토를 통과한 뒤 자동 커밋한다. 위험하거나 공개 가능 여부가 불확실한
정보가 발견되면 커밋하지 않고 사용자 확인을 먼저 받는다. 원격 저장소로 자동 push하지 않는다.

## 핵심 용어

| 용어 | 답하는 질문 | 예시 |
|---|---|---|
| Project Profile | 누가 참여하며 무엇을 소유하는가? | 재고 API 프로젝트의 책임과 제공 계약 |
| Initiative | 왜 여러 주체가 함께 일하며 어떤 결과를 달성하는가? | 재고 복구 서비스 완성과 통합 검증 |
| Task | 한 프로젝트가 직접 수행할 일은 무엇인가? | 복구 worker 구현 |
| Request | 다른 주체에 무엇을 요청하고 어떻게 확인하는가? | API에 복구 endpoint 요청 |
| Issue | 무엇이 위험하거나 작업을 막는가? | 이벤트 계약 불일치 |
| Operator | 어떤 반복 실행을 자동화하는가? | 복구 시나리오 검증 실행기 |
| Outcome Feedback | 어떤 검증 결과가 지침의 효과나 개선 필요성을 보여 주는가? | 리뷰에서 반복 발견된 누락 |
| Agent Execution Contract | 에이전트가 어떤 권한으로 무엇을 검증하고 어느 단계까지 완료했다고 말할 수 있는가? | read-only 리뷰와 push 권한의 분리 |
| Guidance Candidate | 실행 결과에서 어떤 lesson을 언제·어디에 적용할 후보로 만들었는가? | 특정 task 유형의 검증 누락 방지 후보 |
| Harness Evolution | 후보를 기존 지침과 비교해 어떻게 추가·병합·수정·기각하고 효과를 재검증하는가? | topic 지침을 cross-task canon으로 승격 |
| Review Snapshot | 사람이 검토할 정확한 checkpoint는 무엇인가? | 로컬 `review/<topic>_<UTC timestamp>` |
| Promotion | 승인된 변경이 어느 통합·배포 단계로 이동할 수 있는가? | PR에서 feature로 승인 승격 |
| Primary Checkout | 여러 하네스 세션이 최신 working directory 상태를 공유할 물리적 위치는 어디인가? | Git dir와 common dir가 같은 checkout |
| Linked Worktree | 하네스에서 가변 작업이 금지되는 추가 checkout은 무엇인가? | Git dir와 common dir가 다른 checkout |
| Canonical Branch | 승인된 Git 이력의 정본 branch는 무엇인가? | `main` 등 프로젝트가 정한 branch |
| Coordination Transaction | 어떤 충돌 위험·협업 판단을 위해 세션들이 주고받은 메시지 묶음인가? | 계약 파일 소유 확인을 위한 tx |
| Storage Space | 어떤 정보 특성·질의·비용을 위해 어디에 어떤 계약으로 저장하는가? | event record 또는 relation projection 공간 |
| Storage Role | 이 공간이 원본 근거, 직접 기록, 파생 표현, index, cache 중 무엇인가? | `evidence`, `record`, `projection`, `index`, `cache` |
| Cross-Space Catalog | 같은 정보의 여러 표현과 출처·변환을 어떻게 잇는가? | event와 object 표현의 lineage 연결 |
| Transformation | 표현을 만들며 무엇을 보존하고 잃었는가? | narrative에서 state projection 생성 |
| Query Plan | 질문에 필요한 최소 공간과 조회 방식을 어떻게 고르는가? | exact 조회 뒤 relation과 evidence 확인 |
| Storage Adapter | 외부 저장·검색 구현을 어떤 공통 동작과 경계로 연결하는가? | query·trace·export·health adapter |
| Implementation Candidate | 기존 구현을 어떤 근거와 상태로 평가 중인가? | 발견됨, 평가 중, 선택 또는 기각 후보 |
| Portability Contract | 구현이 중단·교체돼도 무엇을 어떻게 회수하는가? | JSONL export와 read-only fallback |
| Local Storage Runtime | 파일 정본을 바꾸지 않고 어떤 파생 저장·검색 계층을 로컬에서 실행하는가? | embedded catalog와 선택적 전문 index |
| Local Storage Broker | 여러 에이전트의 로컬 저장 접근을 누가 직렬화하고 검증하는가? | 정책·schema·쓰기 조정과 context 조립 |
| Retrieval Status | 검색 결과 없음과 미실행·오래됨·부분 조회를 어떻게 구분하는가? | `not_found`, `not_searched`, `stale`, `partial` |
| Memory Fault | 필요한 정보가 문맥에 없거나 신뢰할 수 없을 때 어떤 추가 조회가 필요한가? | stale 상태의 source 재검증 |
| Exploration | 아직 결정·구현하지 않아도 보존할 가치가 있는 어떤 정책·설계 질문을 탐색하는가? | 기억과 작업 문맥의 관계에 대한 열린 토론 |
| Invalidation | 어떤 과거 판단이 대체되거나 기각됐는가? | 이전 재시도 전략의 대체 기록 |
| Quirk | 어떤 비직관적 불변식을 모르고 바꾸면 동작이 깨지는가? | 호환성을 위한 특수 분기 |

저장공간 구성과 확장 경계는 [`docs/storage-architecture.md`](docs/storage-architecture.md), 구현 선택과
교체 계약은 [`docs/storage-adapters.md`](docs/storage-adapters.md), 장기 로컬 실행 계층은
[`docs/local-storage-runtime.md`](docs/local-storage-runtime.md), 미래 인출 신뢰성 계약은
[`docs/memory-reliability.md`](docs/memory-reliability.md), 활성 구성은
[`storage/registry.json`](storage/registry.json), 실행 명령은
[`operators/storage-spaces.md`](operators/storage-spaces.md)를 따른다.

에이전트의 권한·위임·검증·완료 계약은 [`docs/agent-execution.md`](docs/agent-execution.md), 검증 결과를
하네스 지침으로 승격하는 절차는 [`docs/harness-evolution.md`](docs/harness-evolution.md)를 따른다.
하네스의 primary checkout 전용 경계와 판정 명령은
[`docs/change-promotion.md`](docs/change-promotion.md)와
[`operators/harness-worktree-guard.md`](operators/harness-worktree-guard.md)를 따른다.

## 운영 도구 실행

Python 3.10 이상으로 운영 도구와 테스트를 직접 실행한다. Git 관련 도구에는 Git CLI가 필요하다.

```text
python3 operators/harness-worktree-guard.py check .
python3 operators/curation-status.py
python3 operators/feedback-status.py
python3 -B -m unittest discover -s operators/tests -v
```

Windows에서는 `python3` 대신 `py -3` 또는 `python`을 사용한다. 기존 `.sh` 호출과 별도 설치한 hook은
Python 호출로 바꾼다. 전체 명령과 전환 안내는 [`operators/README.md`](operators/README.md)를 따른다.
