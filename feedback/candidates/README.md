# Guidance Candidates

검증된 feedback·test·review·journal evidence에서 컴파일한 비정본 지침 후보를 보존한다. 후보는 승인된 canon,
작업 지시나 사용자 승인이 아니며 `docs/harness-evolution.md`의 범위·회귀·cutover 계약을 따른다.

## 식별과 위치

- ID는 하네스 전체에서 중복되지 않는 `gc-` 접두사의 8자리 소문자 영숫자다.
- 활성 후보는 `feedback/candidates/gc-xxxxxxxx.md`에 둔다.
- `accepted`, `skipped`, `superseded` 후보는 결정 기록을 마친 뒤
  `feedback/candidates/archive/YYYY-MM/`로 옮긴다. 월은 종결 시각의 UTC 달력 월이다.
- 파일을 병합하거나 종결해도 삭제하지 않는다. 현재 proposal·canon은 새 경로를 가리키고 과거 evidence의
  기존 경로는 소급 수정하지 않는다.

## 현재 상태와 전이

상태는 `draft → proposed → accepted`를 기본으로 하며 `draft|proposed → skipped`, 어느 비종결 상태에서든
`superseded`로 전이할 수 있다.

- `draft`: 근거·범위·회귀 조건을 검토 중
- `proposed`: `proposals/`의 활성 변경안과 연결됨
- `accepted`: 사용자 승인과 검증 뒤 canon에 반영됨
- `skipped`: 중복·근거 부족·과적합·권한 충돌·비용 때문에 채택하지 않음
- `superseded`: 다른 후보로 병합되거나 새 근거가 대체함

현재 상태 필드와 현재 연결 포인터는 재작성할 수 있다. 아래 `## 결정 기록`은 UTC 시각순 append-only다.
`MERGE`는 살아남는 후보와 `supersedes`를 양방향으로 연결하며 원본을 삭제하지 않는다. 같은 evidence·trigger·
target 조합을 새 후보로 중복 생성하지 않고 기존 후보에 근거를 추가한다.

## 파일 형식

```markdown
---
candidate_id: gc-xxxxxxxx
status: draft | proposed | accepted | skipped | superseded
created: YYYY-MM-DD HH:MM:SS UTC
updated: YYYY-MM-DD HH:MM:SS UTC
scope_hint: cross-task | project:<id> | operator:<id> | task-type:<topic>
operation: ADD | MERGE | REVISE | SKIP
target: <기존 지침 또는 신규 위치>
proposal: proposals/... | none
canon: docs/... | INDEX.md 규칙 N | none
supersedes: gc-xxxxxxxx | none
superseded_by: gc-xxxxxxxx | none
---

# <후보 헤드라인>

## Lesson
## Trigger
## Evidence
## Expected effect
## Regression check
## Cutover
## Revisit trigger
## 결정 기록
- YYYY-MM-DD HH:MM:SS UTC - <결정·근거·다음 상태>
```

`Evidence`는 원본 feedback ID, 검사, 리뷰와 상대 경로를 포함한다. `SKIP`은 `proposal: none`일 수 있지만
기각 이유와 다시 검토할 관측 가능한 trigger가 필수다. `accepted`는 proposal과 최종 canon 포인터가 모두
필수이며, 명시적인 사용자 요청으로 바로 승인된 경우 그 요청 범위와 검증 증거를 결정 기록에 남긴다.

## 도입 경계

이 저장소는 2026-09-02 01:38:20 UTC 이후 생성하는 Guidance Candidate부터 이 형식을 적용한다. 그 이전
feedback·journal을 일괄 후보화하거나 소급 수정하지 않는다.
