# feedback

검증된 성공과 실수를 UTC 날짜별 append-only 이벤트로 기록한다. 파일명은
`status-YYYY-MM-DD.md`이며 날짜는 UTC 달력 날짜를 사용한다.

## 기록 단위

- 이벤트 하나는 검증으로 확인된 하나의 결과를 나타낸다. 단순 행동 횟수나 자기 평가는 기록하지 않는다.
- `success`는 테스트 통과, 리뷰에서의 결함 차단, 승인된 승격처럼 근거가 있는 결과만 기록한다.
- `mistake`는 기대 계약과 실제 결과의 차이가 근거로 확인됐을 때 기록한다.
- 한 작업에서 성공과 실수가 모두 확인되면 각각 별도 이벤트로 기록할 수 있다. 둘을 상쇄한 총점은 만들지
  않는다.
- 검증되지 않은 추론은 feedback에 넣지 않고 journal에 `[미검증]`으로 기록한다.
- 과거 이벤트는 고치거나 삭제하지 않는다. 분류가 잘못됐다면 새 정정 이벤트를 append하고 원본을
  `supersedes`로 가리킨다.

## 이벤트 형식

```markdown
## [f-xxxxxxxx] YYYY-MM-DD HH:MM:SS UTC · project: <project-id>
- outcome: success | mistake
- category: <허용 category>
- severity: none | minor | major | critical
- pattern: <안정된 kebab-case 패턴 키>
- introduced_at: work | local-review | pull-request | feature | release | canonical | production | not-applicable
- detected_at: work | local-review | pull-request | feature | release | canonical | production | not-applicable
- instruction: `INDEX.md` 규칙, canon 경로#anchor 또는 none
- task: `tasks/...` 또는 none
- evidence: 검증 명령, 리뷰 결과, 상대 경로 또는 커밋
- supersedes: f-xxxxxxxx 또는 none
- summary: 결과와 지침에 주는 의미 한 줄
```

허용 category는 다음과 같다.

| outcome | category | 의미 |
|---|---|---|
| `success` | `instruction-helped` | 지침이 올바른 행동이나 결정을 직접 이끔 |
| `success` | `review-caught` | 다음 단계로 넘어가기 전에 결함을 발견·차단함 |
| `success` | `validation-passed` | 합의된 검증이 기대 결과를 확인함 |
| `success` | `safe-promotion` | 승인된 작업본만 다음 승격 단계로 이동함 |
| `mistake` | `instruction-missed` | 명확한 현행 지침을 따르지 않음 |
| `mistake` | `instruction-ambiguous` | 지침의 복수 해석 때문에 잘못된 결과가 발생함 |
| `mistake` | `instruction-missing` | 필요한 지침이 없어 잘못된 결과가 발생함 |
| `mistake` | `instruction-ineffective` | 지침을 준수했지만 의도한 예방·효과가 나타나지 않음 |
| `mistake` | `execution-error` | 지침과 무관한 구현·명령·판단 오류가 발생함 |
| `mistake` | `external-failure` | 외부 시스템이나 환경 실패가 결과를 깨뜨림 |

## 필드 규칙

- ID는 하네스 전체에서 중복되지 않는 `f-` 접두사의 8자리 소문자 영숫자 식별자다.
- `success`의 severity는 `none`, `mistake`는 `minor`, `major`, `critical` 중 하나다.
- `pattern`은 반복 여부를 비교하는 안정 키다. 같은 근본 원인은 같은 키를 재사용하고, 단순히 같은 작업이라는
  이유로 묶지 않는다.
- `introduced_at`은 원인이 들어간 가장 이른 단계, `detected_at`은 검증으로 확인된 단계다. 원인 주입 개념이
  없는 성공은 둘 다 검증 단계로 기록할 수 있다.
- `instruction`은 결과와 직접 관련된 현행 지침을 가리킨다. 지침 누락이나 무관한 외부 실패는 `none`이다.
- `instruction-ineffective`는 준수 증거와 의도한 효과가 실패했다는 검증을 모두 요구한다. 단순 미준수나
  적용 trigger가 아니었던 사례를 이 category로 분류하지 않는다.
- `instruction-ineffective`는 2026-09-02 01:38:20 UTC 이후 새 event부터 사용할 수 있다. 기존 event를
  소급 분류하지 않으며 `operator:feedback-status`는 이 cutover 이전 분류를 오류로 보고한다.
- `evidence`는 다른 사람이 결과를 확인할 수 있어야 하며 비밀·개인정보·내부 경로를 포함하지 않는다.
- 정정 이벤트는 원본과 반대 outcome을 자동으로 의미하지 않는다. 현재 확인된 결과를 새로 기록하고
  `supersedes`만 연결한다.

## 집계와 개선

`operator:feedback-status`는 `FEEDBACK.md`의 관찰 기간 안에서 검증된 이벤트를 집계하고, 잘못된 스키마,
중복 ID, major 이상 실수와 반복 실수 패턴을 보고한다. 자세한 개선 판단은 `docs/outcome-feedback.md`를
따른다.

검증된 event에서 지침 후보를 만들면 `feedback/candidates/README.md`의 안정 ID·상태·결정 생명주기를
사용한다. event는 evidence이고 candidate는 비정본 파생 record이므로 서로를 대신하지 않는다.
