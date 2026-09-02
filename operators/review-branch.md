---
operator_id: operator:review-branch
owner: harness
implementation: operators/review-branch.sh
affected_projects:
  - all
related_initiatives: []
---

# Operator: review-branch

## 목적과 책임

clean 작업 HEAD 또는 명시한 committed checkpoint에서 UTC 타임스탬프가 있는 로컬 `review/*`
스냅샷을 만들고, 이름·원격 추적·worktree 연결 상태를 감사하며, Git hook에서 review 브랜치의 직접
커밋과 원격 push를 차단한다. PR 생성, 승인, merge 또는 배포는 수행하지 않는다.

## 실행 조건

- 자동 트리거: 없음
- 수동 호출:
  - 현재 clean HEAD에서 생성: `./operators/review-branch.sh create <topic> [repository]`
  - 명시한 checkpoint에서 생성: `./operators/review-branch.sh create <topic> <repository> <source-ref>`
  - 감사: `./operators/review-branch.sh audit [repository]`
  - pre-commit hook: `./operators/review-branch.sh pre-commit [repository]`
  - pre-push hook: `./operators/review-branch.sh pre-push`
- 스케줄 시간대: UTC (`+00:00`, 서머타임 미적용)
- 중단 조건: 대상이 Git worktree가 아니거나, 기본 HEAD 생성 시 worktree가 clean하지 않거나, topic이
  규약과 다르거나 source ref가 committed checkpoint로 해석되지 않음

## 입력 계약

- `create`: 소문자 영문·숫자·하이픈 topic, 선택적 저장소 경로와 source ref. source ref를 생략하면
  clean `HEAD`를 사용하고, 명시하면 그 commit만 스냅샷하며 현재 worktree의 미커밋 변경은 포함하지 않음
- `audit`, `pre-commit`: 선택적 저장소 경로, 기본값은 현재 디렉터리
- `pre-push`: Git pre-push hook이 표준 입력으로 제공하는
  `<local-ref> <local-sha> <remote-ref> <remote-sha>` 행
- Git CLI와 UTC `date`

## 출력과 성공 판정

### create

- `review/<topic>_YYYYMMDDTHHMMSSZ` 로컬 브랜치를 clean HEAD 또는 명시한 source commit에 생성
- `CREATED review-snapshot`과 브랜치명·commit SHA 출력
- checkout, worktree 연결, 파일 복사, 원격 push는 하지 않음

### audit

- 모든 로컬 review 이름이 규약에 맞고 remote-tracking review ref와 worktree에 연결된 review가 없으면
  `OK review-branch`
- 이름 오류는 `R001`, 원격 추적 흔적은 `R002`, worktree 연결은 `R003`과
  `ATTENTION review-branch`
- 발견 여부와 무관하게 검사를 마치면 exit code `0`

### hook 모드

- `pre-commit`은 현재 브랜치가 `review/*`이면 non-zero로 차단
- `pre-push`는 source 또는 destination이 `refs/heads/review/*`이면 non-zero로 차단
- 실수로 생긴 원격 review ref를 복구할 수 있도록 삭제 push는 허용

## 권한과 부작용

- 읽기 범위: 대상 저장소의 worktree 상태와 Git refs
- 쓰기 범위: `create`에서 대상 저장소의 `refs/heads/review/*` 하나. source ref와 worktree는 바꾸지 않음
- 외부 변경: 없음. 원격 네트워크를 호출하지 않음
- 사용자 승인 필요 조건: `create`를 사용자가 직접 요청하거나 프로젝트 작업 절차가 생성하도록 정한 경우

## 실행 안전성

- 멱등성: `audit`과 hook 모드는 같은 ref·입력에 같은 판정. `create`는 매 UTC 초마다 새 이름을 생성
- 동시 실행: 같은 topic을 같은 초에 생성하면 하나만 성공하며 기존 ref를 이동하지 않음
- 타임아웃: Git 상태·ref 조회가 비정상적으로 오래 걸리면 호출자가 제한
- 재시도: clean 상태와 topic을 확인한 뒤 새 UTC 초에 1회

## 실패와 복구

- 실패 분류: Git 저장소 아님, 기본 HEAD 생성 시 dirty worktree, 잘못된 topic·source ref, 동일 브랜치
  존재, Git ref 쓰기 실패
- 복구 절차: 작업 변경을 커밋·정리하거나 topic·source ref를 수정한 뒤 다시 생성. `R002`는 원격 존재를
  별도 확인하고 삭제 권한과 보존 정책에 따라 복구한다. `R003`은 해당 worktree를 detached commit으로
  전환하거나 제거한 뒤 다시 감사한다. 단, `project-id: harness`에서는 새 detached worktree를 만들지 않고
  primary checkout에서 commit을 직접 검토하며, 기존 linked worktree는 소유·미커밋·보존 상태를 확인한
  별도 명시적 정리 작업 전에는 전환·제거하지 않는다.
- issue 승격 조건: hook 우회로 review ref가 반복 push되거나 승인되지 않은 결과가 다음 단계로 승격됨

## 실행 증거

- 로그 위치: 표준 출력과 생성된 로컬 ref. 승인 결과의 장기 증거는 task·request·PR 시스템이 소유
- 보존 기간: 프로젝트의 `docs/change-promotion.md` 적용 정책에 따름
- 민감정보 제거: 브랜치명과 commit SHA만 출력하며 diff·remote URL을 출력하지 않음

## 검증

- clean 저장소에서 규약에 맞는 로컬 review 브랜치가 HEAD와 같은 SHA로 생성되는지 확인
- 명시한 과거·승격 checkpoint에서 현재 HEAD를 checkout하지 않고 같은 SHA의 review가 생성되는지 확인
- dirty 저장소와 잘못된 topic에서 생성이 거부되는지 확인
- 잘못된 이름, remote-tracking review ref와 worktree에 연결된 review에서 `R001`, `R002`, `R003` 확인
- hook fixture에서 review commit·push는 거부하고 PR 브랜치 push와 원격 review 삭제는 허용하는지 확인

## 변경 호환성

`review/<topic>_YYYYMMDDTHHMMSSZ`, 출력 접두사 `CREATED|OK|ATTENTION`, 검사 코드
`R001|R002|R003`와 hook 차단 동작은 공개 계약이다. 명명·차단 범위를 바꾸면
`docs/change-promotion.md`와 `changed/`를 함께 갱신한다.
