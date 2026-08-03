# Quirks

코드만 읽으면 불필요하거나 잘못된 것으로 오해하기 쉽지만, 제거·단순화하면 계약이나 동작이 깨지는
비직관적 현행 불변식을 기록한다. 단순히 복잡하거나 오래된 코드는 등재 대상이 아니다.

## 사용 규칙

- 기존 코드의 단순화·리팩터링·방어 분기 제거를 제안하기 전에 해당 project와 symbol로 이 문서를 검색한다.
- 디버깅 결과 실제 원인이 비직관적 기존 동작으로 확인됐을 때 후보를 남긴다. 추측으로 만들지 않는다.
- 식별자는 전역에서 중복되지 않는 `Q-NNN`을 사용하고 재번호·재사용하지 않는다.
- `symbol`은 코드에서 그대로 검색할 수 있는 클래스·함수·필드·설정 키를 기록한다.
- `impact_if_changed`는 생략하지 않는다. 이 문서가 필요한 이유를 설명하는 핵심 필드다.
- 공개 위험 검토를 통과한 내용만 기록한다. 비공개 구조나 취약점이 필요한 경우 공유 하네스가 아니라
  해당 프로젝트의 접근 통제된 정본에 두고 여기에는 안전한 포인터만 남긴다.
- 코드 주석이 현재 프로젝트 규칙상 허용되면 안정 ID만 가리키는 한 줄 앵커를 둘 수 있다.
  결정 경위·날짜·사람·커밋 해시는 코드에 쓰지 않는다.

```text
// QUIRK Q-001: tenant-scoped cache key invariant. docs/quirks.md
```

## 상태

| status | 의미 |
|---|---|
| `ACTIVE` | 현재도 유효한 불변식 |
| `RESOLVED` | 원인이 제거되어 더 이상 적용되지 않음. 항목은 삭제하지 않고 해소 사유를 남김 |

## 엔트리 형식

```markdown
### Q-NNN · 제목
- status: ACTIVE | RESOLVED
- project: <project-id>
- symbol: `SearchableSymbol`
- location: <project-relative-path 또는 canon pointer>
- behavior: 겉보기와 실제 동작의 차이
- rationale: 확인된 배경 또는 `[미검증] 불명`
- impact_if_changed: 모르고 변경했을 때 생기는 결과
- evidence: 검증 근거
- resolved_reason: RESOLVED일 때만
```

## Entries

<!-- 확인된 항목만 추가한다. -->
