# 활성 이슈 레지스트리

request의 `open`, `in-progress`, `resolved`와 proposal의 `open`, `in-progress` 상태에 대한 현재 정본이다.
종료 상태인 `done`, `on-hold`, `dropped`는 표에서 제거하고 `issues/status-YYYY-MM-DD.md`에 보존한다.

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

request는 `open → in-progress → resolved → done`, proposal은 `open → in-progress → done` 흐름을
사용한다. proposal에는 요청자 확인 단계인 `resolved`를 사용하지 않는다.

## 레벨

- `critical`: 계약·보안·데이터 무결성·운영 흐름을 즉시 파손하거나 광범위한 작업을 막음
- `major`: 주요 계약·기준 문서 불일치 또는 중요한 기능·자동화의 실패
- `minor`: 참고, 개선, 국소적 문제. 착수 게이트로 사용하지 않음

request의 `blocking`은 요청자의 현재 작업이 실제로 막혔는지 나타내는 설명 필드다. 전체 착수 게이트의
정본은 이 파일의 `level`, `status`, 관련 주체 조합이며 둘이 충돌하면 이 파일을 따른다.

## Requests

| level | status | 파일 | target | from | 관련 initiative | 요약 |
|---|---|---|---|---|---|---|

## Proposals

| level | status | 파일 | 관련 프로젝트·operator·문서 | 관련 initiative | 요약 |
|---|---|---|---|---|---|

## 갱신 규칙

- 생성 또는 상태·레벨 변경 시 이 표와 UTC 날짜의 당일 이슈 이벤트를 같은 변경에서 갱신한다.
- 종료 시 표의 행을 제거하고 최종 상태 이벤트를 남긴다.
- request/proposal 파일 자체에는 status나 level을 중복 기록하지 않는다.
- initiative와 무관한 행의 `관련 initiative`는 `-`로 기록한다.
- operator 실패는 수정 책임 프로젝트 또는 operator를 대상으로 한 request를 먼저 만들고 그 행을 등록한다.
