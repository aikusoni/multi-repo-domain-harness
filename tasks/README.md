# tasks

프로젝트 내부 실행 작업과 operator 자체의 구현·유지보수 작업을 관리한다.

```text
tasks/<project>/
├── pending/
├── in-progress/
└── completed/
```

operator 작업은 `tasks/operator-<id>/`에 같은 구조를 사용한다.

- 폴더 위치가 유일한 상태 정본이다.
- 파일 내부에 status를 쓰지 않는다.
- 파일명은 UTC 날짜 기준 `YYYY-MM-DD-<short-topic>.md`다.
- 상태가 바뀌어도 `task_id`와 파일명은 유지하고 파일만 이동한다.
- operator 작업 파일의 `project`에는 owner 프로젝트, `operator`에는 `operator:<id>`를 기록한다.
- 공동 이니셔티브에서 파생된 작업은 `initiative: initiative:<id>`로 연결한다.
- 다른 프로젝트에 일을 넘길 때는 task를 대신 만들지 않고 `requests/`를 사용한다.
- operator의 정상 반복 실행은 task로 만들지 않는다. 구현·수정·복구처럼 완료 기준이 있는 작업만 관리한다.
- 시작 시 `pending`과 `in-progress`의 제목만 보고 필요한 파일만 연다.
- `completed`는 이력 확인이 필요할 때만 읽는다.
- 요청을 받아 구현하는 작업은 `related_request`로 연결한다. 완료 시 task 결과와 request 처리 결과를
  같은 변경에서 갱신하되, 두 상태를 하나로 간주하지 않는다.
- `in-progress` 이동 시 진행 기록에 `YYYY-MM-DD HH:MM:SS UTC` 형식의 착수 시각과 이유,
  `completed` 이동 전에는 완료 내용·검증·관련 커밋을 반드시 기록한다.
- 완료 기준이 남아 있거나 최신 관련 변경 뒤 검증이 `FAIL`, `PARTIAL`, `NOT_RUN`이면 `completed`로 옮기지
  않는다. 실행할 수 없었던 검증은 이유·남은 위험과 함께 기록하되 완료로 과장하지 않는다.
- 중단·취소·대체 시에는 부분 변경, 확인된 사실, 실행한·실행하지 못한 검증과 안전한 재개·rollback 지점을
  남긴다. 취소된 결론 때문에 별도로 검증된 관찰까지 일괄 폐기하지 않는다.
