# journal

세션별 작업 로그를 append-only로 기록한다.

- 파일명: UTC 날짜 기준 `YYYY-MM-DD-<short-topic>.md`
- 날짜와 시각: `YYYY-MM-DD HH:MM:SS UTC` 형식으로 UTC를 반드시 명시
- 기존 내용을 고치지 않고 후속 섹션이나 정정을 추가한다. 단, 아래 유효성 메타데이터는 예외다.
- 파일 최상단 제목 바로 아래에 `**VALIDITY:** ACTIVE`를 기록한다.
- 검증하지 않은 내용은 `[미검증]` 표시
- 사람의 결정·리뷰나 프로젝트 간 합의를 기다리는 안건은 journal이 아니라 request/proposal 본문과
  `AGENDA.md`에 기록
- 살아 있는 세션을 관측하거나 세션 간 메시지를 주고받으면 아래 `SESSION-COMM` 형식으로 기록
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

## 세션 관측·통신 로그

`INDEX.md` 규칙 28과 `docs/session-coordination.md`에 따라 위험 경계에서 다른 세션을 관측하거나
메시지를 주고받았으면 해당 섹션에 한 줄을 append한다.

```markdown
**SESSION-COMM:** 2026-08-21 09:20:00 UTC · observe · peer: project-a@worktree-a · reason: INDEX 수정 전 소유 확인
**SESSION-COMM:** 2026-08-21 09:21:00 UTC · outbound · peer: project-a@worktree-a · tx:contract-check-20260821T092100Z · tx-count:1/10 · prompt-in:- · API 계약 파일 수정 여부 질문 · ref:docs/contracts/api.md
**SESSION-COMM:** 2026-08-21 09:22:00 UTC · inbound · peer: project-a@worktree-a · tx:contract-check-20260821T092100Z · tx-count:2/10 · prompt-in:1/5 · 수정 없음 확인 → requests/... · value:none(direct-answer)
```

- `observe`, `outbound`, `inbound`, `no-response` 중 하나를 사용한다. 관측만 한 줄에는 tx 카운터가 없다.
- `peer`는 실제 작업 디렉터리로 확인하되 공개 기록에는 절대경로 대신
  `<project-id>@<worktree-or-task>`를 쓴다. 제목이나 브랜치명만으로 상대를 기록하지 않는다.
- 메시지 줄에는 tx id와 전체 메시지 번호 `tx-count:<n>/10`을 반드시 기록한다.
- `prompt-in`은 해당 세션이 사람의 마지막 직접 프롬프트 뒤 받은 메시지 수다. outbound에는 `-`,
  inbound에는 `<n>/5`를 기록한다.
- 끝에는 파일·커밋·수치 같은 산출물 포인터를 붙인다. 없으면 `value:none`, 직접 질문에 대한 답이면
  `value:none(direct-answer)`로 적는다.
- 무응답과 `회신 불요` 수신도 기록하되 그것을 이유로 새 메시지를 보내지 않는다.
- 통신 결과가 결론의 근거가 되면 request, changed, decision 또는 canon 포인터를 같은 줄에 붙인다.
- 이 형식은 도입 뒤 새 로그부터 적용하며 기존 journal은 소급 수정하지 않는다.

## 항목 템플릿

```markdown
# YYYY-MM-DD topic

**VALIDITY:** ACTIVE

## YYYY-MM-DD HH:MM:SS UTC · 컨텍스트

## YYYY-MM-DD HH:MM:SS UTC · 결정과 발견

## YYYY-MM-DD HH:MM:SS UTC · 미해결
```
