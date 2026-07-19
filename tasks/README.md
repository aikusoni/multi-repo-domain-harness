# tasks

프로젝트 내부 실행 작업을 관리한다.

```text
tasks/<project>/
├── pending/
├── in-progress/
└── completed/
```

- 폴더 위치가 유일한 상태 정본이다.
- 파일 내부에 status를 쓰지 않는다.
- 파일명은 `YYYY-MM-DD-<short-topic>.md`다.
- 상태가 바뀌어도 `task_id`와 파일명은 유지하고 파일만 이동한다.
- 다른 프로젝트에 일을 넘길 때는 task를 대신 만들지 않고 `requests/`를 사용한다.
- 시작 시 `pending`과 `in-progress`의 제목만 보고 필요한 파일만 연다.
- `completed`는 이력 확인이 필요할 때만 읽는다.
