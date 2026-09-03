# 변경 승격과 브랜치 전략

## 목적

작업 중인 변경이 사람의 검토 없이 원격 통합 또는 배포 환경에 반영되지 않도록 작업본, 공동 PR,
feature 통합, release·정본을 분리하고, 각 지점의 검토 대상을 로컬 리뷰 스냅샷으로 동결한다. 브랜치는
에이전트 정체성이 아니라 변경 상태와 검증 증거다.

## 공통 불변식

- 참여 프로젝트가 변경을 만드는 작업용 worktree를 사용할 때는 그 worktree와 수명이 같은 임시 작업
  브랜치만 연결한다. 하네스 저장소는 아래 primary checkout 전용 예외를 따른다. 작업 브랜치는 배포
  트리거가 될 수 없다.
- 로컬 `review/*`는 어느 committed checkpoint든 가리킬 수 있는 제출 스냅샷이다. 승격 경로의 단계가
  아니며, 원격에 push하지 않고 생성 뒤 이동, amend, reset, 직접 커밋하지 않는다.
- 승인 뒤 검토한 commit 또는 tree가 바뀌면 기존 승인은 무효다. 바뀐 checkpoint에서 새 로컬 리뷰
  스냅샷을 만들고 다시 검토한다.
- 원격 PR 브랜치는 공동 리뷰와 CI를 위한 임시 통합 공간이며 배포 소스가 아니다.
- 원격 feature 브랜치에는 승인된 개인 리뷰 또는 PR 결과만 들어간다.
- release·배포 브랜치 또는 정본 브랜치로의 병합은 별도의 통합 검증과 승인 뒤 수행한다.
- 에이전트 reviewer의 결과는 검증 증거이지 사람 승인이나 보호 ref 승격 권한이 아니다. 승인 주체와
  reviewer를 구분하고, 자동 리뷰 통과만으로 다음 승격 단계를 실행하지 않는다.
- 태그 방식 배포는 승인된 결과를 정본 브랜치에 먼저 병합한 뒤 그 정확한 정본 commit에 태그한다.
- 임시 작업 브랜치를 삭제하기 전에 결과 commit이 지속 가능한 ref에서 도달 가능한지 확인한다. 로컬
  review 하나만 남은 상태는 장기 보존으로 보지 않는다.
- 어떤 단계도 앞 단계의 승인·검증을 자동으로 추정하거나 우회하지 않는다.

## 브랜치 역할과 명명

| 역할 | 권장 형식 | 위치 | 변경 가능성 | 원격 push | 배포 |
|---|---|---|---|---|---|
| 임시 작업 | `<tool>/work/<topic>` 또는 프로젝트 규약 | 참여 프로젝트의 작업용 worktree 또는 하네스 primary checkout | 가능 | 프로젝트 정책 | 금지 |
| 로컬 리뷰 스냅샷 | `review/<topic>_YYYYMMDDTHHMMSSZ` | 로컬 ref | 불변 | 금지 | 금지 |
| 공동 PR | `<tool>/pr/<topic>` 또는 프로젝트 규약 | 원격 | PR 수명 동안 가능 | 허용 | 금지 |
| 기능 통합 | `feature/<topic>` | 원격 | 승인된 결과만 | 허용 | 직접 배포 금지 |
| 릴리스 | `release/<version>` 또는 배포 브랜치 | 원격 | 보호 | 허용 | 정책에 따라 허용 |
| 정본 | `main` 등 프로젝트 정본 | 원격 | 보호 | 승인 병합만 | 태그 기준 |

`<topic>`은 도구 호환성을 위해 소문자 영문·숫자와 하이픈을 권장한다. 리뷰 타임스탬프는 UTC
`YYYYMMDDTHHMMSSZ`를 사용한다. 저장소가 `codex/` 같은 필수 namespace를 정하면 작업·PR 브랜치에
적용하되, 로컬 리뷰 브랜치는 검색과 push 차단을 위해 `review/`를 최상위 prefix로 유지한다. 임시 작업
브랜치 prefix는 프로젝트가 명시하고 종료 검사에도 같은 값을 사용한다.

## 하네스 저장소 예외: primary checkout 전용

`project-id: harness`는 Git dir와 common dir가 같은 **Primary Checkout** 하나에서만 조사·편집·생성형
검사·build·stage·commit·merge·push를 수행한다. Git dir와 common dir가 다른 **Linked Worktree**는
읽기 전용 상태 확인 외의 작업 장소로 사용하지 않는다. 경로명, branch명이나 앱이 표시하는 환경 이름이
아니라 `operator:harness-worktree-guard`의 Git metadata 판정을 사용한다.

이 제한은 여러 세션이 하나의 working directory를 함께 읽어 request·changed·task·journal과 아직
commit되지 않은 최신 기록까지 바로 관찰하게 하는 공유 가시성 계약이다. linked worktree는 working tree와
index를 격리하므로 한 세션의 기록이 commit·merge되기 전 다른 세션에서 누락되고, 오래된 상태로 판단할 수
있다. primary checkout을 공유해도 이미 열린 세션의 문맥이 자동 갱신되는 것은 아니므로 판단·수정 직전에
대상 파일과 Git 상태를 다시 읽는다.

Primary Checkout은 물리적 작업 위치이고 `main` 같은 정본 branch는 승인된 Git 이력의 역할이다. 하네스는
primary 안의 임시 작업 branch에서 변경한 뒤 정상 승격 절차를 따를 수 있으며, 이 예외는 `main`에 직접
commit하라는 뜻이 아니다. 같은 하네스의 로컬 세션은 모두 동일한 primary 절대경로를 사용한다. 별도 clone은
자기 Git metadata에서 primary로 보이더라도 working directory를 공유하지 않으므로 대체 작업 위치로 쓰지
않는다.

- 하네스에 `git worktree add`를 실행하지 않는다. 데스크톱 앱과 자동화도 하네스 task를 linked worktree로
  만들거나 handoff하지 않고 기존 primary checkout에서 직접 실행한다.
- 작업 시작·재개와 stage·commit·push 직전에
  `./operators/harness-worktree-guard.sh check .`를 실행한다. `BLOCKED` 또는 non-zero면 가변 행동을
  시작하지 않는다.
- primary에서 cutover 이전 linked worktree가 발견되면 `ATTENTION`을 보고하되 primary 작업은 계속할 수
  있다. 발견한 linked worktree는 새 작업에 재사용하지 않는다.
- 기존 linked worktree에는 dirty 변경이나 미보존 commit이 있을 수 있다. 자동 remove·clean·reset·prune
  하지 않고, 소유자·미커밋 상태·지속 가능한 보존 ref를 확인한 별도 명시적 정리 작업에서만 제거한다.
- 병렬 하네스 작업은 linked worktree로 격리하지 않는다. primary checkout의 소유권을 세션 조정 계약으로
  직렬화한다. working tree·Git index·현재 branch·refs를 바꾸는 stage·commit·switch·checkout·merge·
  rebase·amend·reset·stash는 응답을 받은 단일 writer만 수행하고, 상태와 현재 branch를 확인한 뒤 다음
  작업으로 전환한다. 이 목록은 별도 승인이나 권한이 필요한 행동을 허가하지 않는다.

이 예외는 하네스 운영 기록이 여러 checkout에서 동시에 분기·수정되거나 세션마다 다르게 보이는 위험을
줄이기 위한 저장소 한정 정책이다. 참여 프로젝트와 제품 저장소는 각 프로젝트의 worktree·격리 정책을
계속 적용한다.

## 승격 경로와 리뷰 체크포인트

review는 아래 경로를 따라 한 번 통과하는 단계가 아니다. 변경이 사람의 판단을 받아야 하는 어느
checkpoint에서나 현재 commit 옆에 새 불변 스냅샷을 만든다.

```text
승격:  임시 작업 ─────→ PR(선택) ─────→ feature ─────→ release·정본 ─────→ 배포
검토:      └ review A       └ review B      └ review C
```

review A·B·C는 필요할 때만 만든다. 최초 작업 결과, PR 수정 뒤 head, 기능 통합 결과, release 후보처럼
검토 범위와 위험이 달라지는 checkpoint는 각각 새 review가 될 수 있다. 뒤 단계 review가 앞 단계의
승인을 자동 계승하지 않으며, 앞 review를 이동해 재사용하지 않는다.

검토할 변경은 모두 커밋돼 있어야 한다. review 브랜치는 파일을 복사하지 않고 선택한 commit과 같은 SHA를
가리킨다. 반려되거나 checkpoint가 바뀌면 임시 작업 브랜치 또는 해당 통합 절차에서 수정하고 새 UTC
타임스탬프의 review를 만든다. 이전 review는 보존 기간이 끝날 때까지 이동하지 않는다.

## 개인 작업 흐름

작업 결과를 review로 동결해 승인받은 뒤 feature에 등록한다. feature 통합이나 release 후보를 사람이 다시
판단해야 하면 그 checkpoint에서 별도 review를 만든다. 리뷰어에게 이동 가능한 feature·release·검증
참조를 직접 열게 하지 않는다.

## 공동 작업 흐름

```text
승격:  임시 작업 ─────→ 원격 PR·CI ─────→ 보호된 feature ─────→ release·정본 ─────→ 배포
검토:      └ 제출 review       └ 변경 review          └ 통합 review
```

로컬 review는 제출 단위를 동결하고, 원격 PR은 여러 사람이 의견과 커밋을 모으는 변경 가능한 검토
공간이다. PR 수정은 임시 작업 브랜치에서 수행하고 변경된 PR head를 승인받아야 할 때 새 로컬 review를
만든다. PR head가 바뀌면 기존 승인을 무효화하고 필수 CI와 공동 리뷰를 다시 수행한다. feature 통합 뒤
다시 확인해야 하는 결과도 기존 review를 옮기지 않고 새 checkpoint review로 동결한다.

## 참여 프로젝트의 작업용 worktree와 임시 브랜치 수명

참여 프로젝트의 자동화가 생성하는 편집용 worktree에는 `<tool>/work/*`처럼 프로젝트가 임시 작업용으로
선언한 브랜치만 연결한다. 로컬 `review/*`, 원격 PR, feature, 통합·검증·release·배포·정본 ref는 작업용 worktree의
브랜치로 연결하지 않는다. 연결된 브랜치는 다른 worktree에서 checkout하거나 안전하게 이동할 수 없기
때문이다.

review는 브랜치 자체를 checkout하지 않고 `git switch --detach review/<name>` 또는
`git worktree add --detach <path> review/<name>`처럼 정확한 commit을 detached 상태로 연다. 통합 후보도
검토만 할 때는 같은 방식으로 열며, 프로젝트 절차상 통합 ref를 checkout해야 한다면 그 ref를 강제로
이동하기 전에 연결된 worktree와 소유자를 확인한다.

위 detached worktree 예시는 참여 프로젝트에만 적용한다. 하네스 review는 linked worktree로 열지 않고
primary checkout에서 `git show`, `git diff`, `git log`와 commit을 직접 지정하는 read-only 검사로 검토한다.
하네스의 기존 linked worktree는 이 절의 일반 종료 순서로 자동 정리하지 않고 위 예외의 보존 확인을 먼저
거친다.

작업 종료 시 다음 순서를 지킨다.

1. 임시 작업 브랜치의 tip SHA를 기록한다.
2. `git for-each-ref --points-at <sha>`와 `git branch --contains <sha>`로 보존 ref를 찾고, 필요하면
   `git merge-base --is-ancestor <sha> <durable-ref>`로 도달 가능성을 확인한다.
3. 로컬 review만 tip을 가리키거나 지속 가능한 ref에서 도달할 수 없으면 원격 작업 브랜치, feature,
   정본 또는 프로젝트가 정한 장기 ref에 먼저 보존한다.
4. worktree를 제거한 뒤 임시 로컬·원격 작업 브랜치를 프로젝트 정책에 따라 삭제한다.
5. 프로젝트가 선언한 임시 prefix로 local·remote ref를 검색해 종료한 작업의 잔존 브랜치가 없는지
   기계적으로 확인한다.

review는 로컬 전용이고 정리될 수 있으므로 지속 가능한 보존 ref가 아니다. 반대로 오래 유지되는 feature,
release·정본 ref는 작업용 worktree의 수명에 묶지 않는다.

## 승인 증거

task, request 또는 프로젝트의 PR 시스템에 다음을 남긴다.

- 기준 브랜치와 임시 작업 브랜치
- 로컬 리뷰 브랜치명, 검토한 checkpoint 역할과 commit SHA
- 원격 PR 링크 또는 식별자(공동 작업일 때)
- 검증 명령과 결과
- 승인 주체와 UTC 승인 시각
- feature·release·정본으로 승격된 commit 또는 tree

로컬 review 브랜치는 장기 감사 정본이 아니다. 삭제 전에 승인된 SHA와 결과를 공유 기록 또는 PR에
남긴다. 비밀·개인정보·내부 URL은 기록하지 않는다.

## 강제 장치

- 하네스에서는 호출자가 `operator:harness-worktree-guard check`를 작업 시작과 stage·commit·push 직전에
  실행하는 절차상 게이트로 사용한다. 현재 checkout이 linked이면 non-zero를 반환하고, `audit`는 등록 linked
  worktree 잔존을 경로 없이 보고한다. hook에 연결하지 않은 저장소에서 Git 자체를 가로채지는 않는다.
- pre-push 검사로 `refs/heads/review/*`의 source 또는 destination push를 거부한다.
- 감사 검사로 `review/*`가 worktree 브랜치로 연결된 상태를 경고하고 detached 검토로 전환하게 한다.
- 자동 push는 `git push <remote> <명시한-브랜치>`처럼 ref를 명시하고 `--all`, `--mirror`를 금지한다.
- PR·feature·release·정본에는 직접 push와 force push를 금지하고 필수 승인·CI를 보호 규칙으로 강제한다.
- 새 커밋이 추가되면 승인을 해제하도록 PR 시스템을 설정한다.
- 작업·review·PR·feature 단계에는 배포 자격증명과 자동 배포 트리거를 연결하지 않는다.

저장소가 호스팅 서비스나 배포 방식 때문에 다른 브랜치 이름을 사용해도 임시 작업 ref와 지속 가능한 ref의
수명 분리, 로컬 review의 원격 push 금지, checkpoint 변경 시 승인 무효화와 정본 태그 원칙은 유지한다.

## 예외와 복구

긴급 hotfix도 별도 작업본, 사람 승인, 검증을 거친다. 단축된 경로가 필요하면 프로젝트의 사전 승인된
hotfix 계약에 우회 단계, 승인자, 사후 정본 병합과 회고 조건을 명시한다. 운영에서 발견된 결함은
`feedback/`에 도입·발견 단계를 기록하고, 관련 issue·request·rollback 절차와 연결한다.
