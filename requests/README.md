# requests

다른 프로젝트 또는 operator에 전달하는 작업 요청을 파일 하나당 하나씩 관리한다. 요청 주체는 세션이나
사람이 아니라 `PROJECTS.md`의 프로젝트 또는 `OPERATORS.md`의 operator 식별자다.

## 생애주기

`open → in-progress → resolved → done` 또는 `dropped`

- 대상 프로젝트는 착수 시 `in-progress`, 처리 후 `resolved`로 바꾸고 `## 처리 결과`를 append한다.
- 요청 프로젝트는 결과를 검토한 뒤 `done`으로 닫고 `## 확인 (요청자)`를 append한다.
- 상태 변경은 `ISSUES.md`와 당일 이슈 이벤트에 함께 반영한다.
- operator 대상 요청은 `target: operator:<id>`를 사용한다. 파일명에서는 `operator-<id>`로 쓴다.
- operator 실행을 담당한 에이전트는 처리 결과에 자기 `project-id`와 실행 증거를 함께 남긴다.

## 파일 형식

파일명: `YYYY-MM-DD-<target>-<short-topic>.md`

```markdown
---
target: project-b
from: project-a
opened: YYYY-MM-DD
blocking: false
---

# 요청 제목

## 배경

## 구체적 요청

## 수용 기준

- [ ] 검증 가능한 조건

## 관련 문서

## 처리 결과

## 확인 (요청자)
```

요청 파일에는 status와 level을 쓰지 않는다.
