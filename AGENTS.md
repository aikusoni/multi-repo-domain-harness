# Agent Instructions

<!-- harness-bootstrap: read-index-first -->

## Bootstrap

이 저장소에서 작업하는 모든 에이전트는 작업 종류와 규모에 관계없이 다른 파일을 읽거나 수정하기 전에
루트 `INDEX.md` 전체를 읽고 상단 규칙 버전 스탬프를 기억한다. `INDEX.md`는 저장소 내부 운영 규칙의
유일한 정본이다. 이 파일은 진입 포인터이며 세부 규칙을 복제하지 않는다.

플랫폼·시스템·사용자·보안 지침처럼 더 높은 우선순위의 지침은 `INDEX.md`보다 우선한다. 새 작업·작업 단위
전환·중단 후 재개·commit·최종 보고 직전에는 스탬프를 다시 확인한다. 값이 달라졌거나 마지막 숙지 버전을
확인할 수 없으면 `INDEX.md` 전체를 다시 읽기 전까지 작업을 계속하지 않는다.

## Entry

1. `INDEX.md` 전체를 읽는다.
2. `git status --short`로 기존 변경과 현재 범위가 겹치는지 확인한다.
3. `PROJECTS.md`에서 현재 `project-id`를, 자동화 작업이면 `OPERATORS.md`에서 operator와 owner를 확인한다.
4. `INDEX.md`의 권장 시작 순서에 따라 현재 작업과 직접 관련된 상태·문서만 읽는다.
5. 실행·위임·리뷰·중단·완료 판단은 `docs/agent-execution.md`를 따른다.
