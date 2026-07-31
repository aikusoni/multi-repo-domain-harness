# requests

다른 프로젝트 또는 operator에 전달하는 작업 요청을 파일 하나당 하나씩 관리한다. 요청 주체는 세션이나
사람이 아니라 `PROJECTS.md`의 프로젝트 또는 `OPERATORS.md`의 operator 식별자다.

## 생애주기

`open → in-progress → resolved → done` 또는 `dropped`

- 대상 프로젝트는 착수 시 `in-progress`, 처리 후 `resolved`로 바꾸고 `## 처리 결과`를 append한다.
- 요청 프로젝트는 결과를 검토한 뒤 `done`으로 닫고 `## 확인 (요청자)`를 append한다.
- 상태 변경은 `ISSUES.md`와 UTC 날짜의 당일 이슈 이벤트에 함께 반영한다.
- operator 대상 요청은 `target: operator:<id>`를 사용한다. 파일명에서는 `operator-<id>`로 쓴다.
- operator 실행을 담당한 에이전트는 처리 결과에 자기 `project-id`와 실행 증거를 함께 남긴다.

## 파일 형식

파일명: UTC 날짜 기준 `YYYY-MM-DD-<target>-<short-topic>.md`

```markdown
---
target: project-b
from: project-a
opened: YYYY-MM-DD HH:MM:SS UTC
blocking: false
initiative:
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

공동 이니셔티브에서 파생된 요청이면 `initiative: initiative:<id>`를 기록한다. initiative는 요청의
`target`·`from`과 상태를 대체하지 않는다.

`blocking`은 요청자의 현재 작업이 직접 막혔는지를 설명할 뿐 전체 게이트를 결정하지 않는다. 전체 게이트는
`ISSUES.md`의 level·status·관련 주체 조합이 정본이다.

## 분쟁과 사람 결정

프로젝트 간 규약·계약·소유권 해석이 충돌하면 에이전트끼리 결론을 확정하지 않는다. 각자의 근거
(`저장소/파일:라인`, 확인 브랜치·커밋)를 요청 본문에 append하고 `AGENDA.md`에 등재한다. 사용자의 결정을
반영한 뒤 결정 문서와 요청 결과를 함께 갱신한다.

## 아카이브

- `done`·`dropped` 요청은 `requests/archive/<파일명 앞 YYYY-MM>/<기존 파일명>`으로 이동한다.
- `on-hold`는 재개 가능하므로 루트에 남긴다.
- 아카이브는 현행이 아니며 기본 스캔에서 제외하고 수정하지 않는다.
- 요청이 재개되면 루트로 되돌리고 활성 행 복원과 재개 이벤트를 같은 변경에서 남긴다.
- 과거 문서의 기존 링크는 파일명으로 새 위치를 찾을 수 있으므로 일괄 수정하지 않는다.
