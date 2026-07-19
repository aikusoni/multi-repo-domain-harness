# 활성 이슈 레지스트리

`open`, `in-progress`, `resolved` 상태인 proposal과 request의 현재 상태 정본이다. 종료 상태인
`done`, `on-hold`, `dropped`는 표에서 제거하고 `issues/status-YYYY-MM-DD.md`에 보존한다.

## 게이팅

- `critical` 또는 `major`이면서 `open` 또는 `in-progress`인 관련 이슈는 착수 게이트다.
- `resolved`, 종료 상태, `minor` 이슈는 일반 작업을 막지 않는다.
- 게이트는 `target`, `from`, `관련 주체`에 현재 프로젝트 또는 관련 operator가 포함될 때만 적용한다.

## 상태

| status | 의미 |
|---|---|
| `open` | 미착수 |
| `in-progress` | 처리 중 |
| `resolved` | 대상 처리 완료, 요청자 확인 대기 |
| `done` | 확인·반영 완료 |
| `on-hold` | 보류 |
| `dropped` | 폐기 |

## Requests

| level | status | 파일 | target | from | 요약 |
|---|---|---|---|---|---|

## Proposals

| level | status | 파일 | 관련 프로젝트·operator·문서 | 요약 |
|---|---|---|---|---|

## 갱신 규칙

- 생성 또는 상태·레벨 변경 시 이 표와 당일 이슈 이벤트를 같은 변경에서 갱신한다.
- 종료 시 표의 행을 제거하고 최종 상태 이벤트를 남긴다.
- request/proposal 파일 자체에는 status나 level을 중복 기록하지 않는다.
