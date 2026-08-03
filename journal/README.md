# journal

세션별 작업 로그를 append-only로 기록한다.

- 파일명: UTC 날짜 기준 `YYYY-MM-DD-<short-topic>.md`
- 날짜와 시각: `YYYY-MM-DD HH:MM:SS UTC` 형식으로 UTC를 반드시 명시
- 기존 내용을 고치지 않고 후속 섹션이나 정정을 추가한다. 단, 아래 유효성 메타데이터는 예외다.
- 파일 최상단 제목 바로 아래에 `**VALIDITY:** ACTIVE`를 기록한다.
- 검증하지 않은 내용은 `[미검증]` 표시
- 사람의 결정·리뷰나 프로젝트 간 합의를 기다리는 안건은 journal이 아니라 request/proposal 본문과
  `AGENDA.md`에 기록
- 오래되어 현행 판단에 필요하지 않은 기록은 `journal/archive/YYYY-MM/`로 이동하며 기본 스캔에서 제외

## 지식 유효성

저널의 실행 경위는 과거 사실로 보존하되, 그 안의 판단이 지금도 유효한지는 명시된 값으로 관리한다.
폐기된 판단을 단순히 다시 언급하지 않는 방식으로 표현하면 검색 결과에서 현행 판단과 구별할 수 없다.

| VALIDITY | 의미 | 필수 메타데이터 |
|---|---|---|
| `ACTIVE` | 현재도 유효하거나 아직 대체·기각되지 않음 | 없음 |
| `SUPERSEDED` | 더 나은 판단이나 canon으로 대체됨 | `REPLACED_BY`, `REASON` |
| `REJECTED` | 검토·시도했으나 채택하지 않음 | `REASON` |

```markdown
# YYYY-MM-DD topic

**VALIDITY:** SUPERSEDED
**REPLACED_BY:** docs/... 또는 journal/...#anchor
**REASON:** 대체된 이유 한 줄
```

- `SUPERSEDED`는 대체 문서나 섹션을 반드시 가리킨다. 대체 대상이 없으면 `REJECTED`를 사용한다.
- `SUPERSEDED`·`REJECTED`는 판단 근거가 드러나는 사유 한 줄이 필수다.
- `VALIDITY`, `REPLACED_BY`, `REASON`만 append-only의 메타데이터 예외로 사후 수정할 수 있다.
  본문·과거 시각·당시 관찰을 고치거나 삭제하지 않는다. 본문 정정은 하단에 새 섹션으로 append한다.
- 작업 중 과거 판단을 뒤집었다면 같은 작업에서 과거 저널의 유효성 메타데이터를 갱신한다.
- 무효화된 항목은 `INVALIDATIONS.md`에 한 줄로 등재한다. 색인은 원문을 대체하지 않는다.
- 기존 저널을 일괄 소급 수정하지 않는다. 새 저널과 현재 작업에서 실제로 재판정한 기록부터 적용한다.
- 아카이브 여부와 유효성은 별개다. 오래되어 이동한 `ACTIVE` 기록이 자동으로 무효가 되지 않는다.

```markdown
# YYYY-MM-DD topic

**VALIDITY:** ACTIVE

## YYYY-MM-DD HH:MM:SS UTC · 컨텍스트

## YYYY-MM-DD HH:MM:SS UTC · 결정과 발견

## YYYY-MM-DD HH:MM:SS UTC · 미해결
```
