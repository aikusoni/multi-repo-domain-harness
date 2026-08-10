# proposals

기준 문서 변경을 제안한다. 파일명은 UTC 날짜 기준 `YYYY-MM-DD-<short-topic>.md`다.

```markdown
# 제안: 제목

- 대상: docs/... 또는 신규
- 관련 프로젝트: project-a, project-b
- 관련 initiative: initiative:initiative-id (있으면)

## 변경 내용

## 근거

## 영향

## 수용 기준
```

현재 status와 level은 파일에 쓰지 않고 `ISSUES.md`와 UTC 날짜의 당일 `issues/` 이벤트에서 관리한다.

proposal은 `open → in-progress → done` 또는 `on-hold`·`dropped` 흐름을 사용하며 `resolved`를 사용하지
않는다. `done`·`dropped` 제안은 `proposals/archive/YYYY-MM/`로 옮긴다. `on-hold`와 활성 문서가 직접
참조하는 제안은 루트에 남긴다. 아카이브 파일은 현행이 아니며 재개 전에는 수정하지 않는다. 이동할 때
현재 등재부·canon·목차의 포인터는 새 경로로 갱신하고 과거 이벤트와 종결 문서의 경로는 보존한다.
