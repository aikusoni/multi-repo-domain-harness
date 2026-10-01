# Claude Agent Instructions

<!-- harness-bootstrap: read-index-first -->

이 저장소에서 어떤 작업을 시작하든 다른 파일을 읽거나 수정하기 전에 루트 `INDEX.md` 전체를 먼저 읽고
규칙 버전 스탬프를 기억한다. `INDEX.md`가 저장소 내부 운영 규칙의 유일한 정본이며 이 파일은 세부 규칙을
복제하지 않는 bootstrap 포인터다.

새 작업·작업 단위 전환·중단 후 재개·commit·최종 보고 직전에는 `INDEX.md` 스탬프를 다시 확인한다. 값이
달라졌거나 숙지 상태를 확신할 수 없으면 전체를 다시 읽는다. 이후 `INDEX.md`의 권장 시작 순서와
`docs/agent-execution.md`의 실행·위임·검증 계약을 따른다.

`INDEX.md`를 읽은 직후 `python3 operators/harness-worktree-guard.py check .`를 실행한다. 이 하네스 저장소가
linked worktree로 판정되면 읽기 전용 상태 확인 외의 작업을 시작하지 않고 primary checkout으로 전환한다.
