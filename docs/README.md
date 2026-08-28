# docs

여러 저장소가 공유해야 하는 기준 문서를 둔다.

- `project-map.md`: 저장소와 역할, 의존 관계, 계약 소유권
- `domain-map.md`: 도메인 경계와 각 도메인의 책임
- `glossary.md`: 저장소 사이에서 의미가 달라질 수 있는 용어
- `decision-log.md`: 확정된 횡단 결정과 대체된 결정
- `roles.md`: worker·curator 책임과 프로젝트 정체성의 경계
- `quirks.md`: 모르고 단순화하면 동작을 깨뜨리는 비직관적 현행 불변식
- `outcome-feedback.md`: 검증된 성공·실수를 지침 개선으로 연결하는 절차
- `change-promotion.md`: 로컬 review, 원격 PR, feature, release·정본의 승격 계약
- `session-coordination.md`: 살아 있는 세션 식별, 위험 경계 조정, tx 총 10건과 프롬프트 후 수신 5건 제한
- `storage-architecture.md`: 목적별 저장공간, 여러 표현의 lineage, query planning과 제한 context 조립
- `storage-adapters.md`: 재사용 우선 구현 평가, 공통 adapter API, 이식성·fallback과 채택 게이트
- `local-storage-runtime.md`: 파일 정본 위의 장기 로컬 실행 계층, broker와 단계적 도입 게이트
- `memory-reliability.md`: 저장·인출 실패 단계, retrieval status, Query Trace와 Memory Fault 장기 계약
- `contracts/`: API, 이벤트, 데이터 스키마 등 저장소 간 계약

기준 문서에는 확인된 사실과 확정된 결정만 기록한다. 검토가 필요한 변경은 먼저 `proposals/`에 둔다.

## 살아있는 문서의 현재성

계약·결정처럼 확정 사실을 소유하는 문서와 달리 현황·인벤토리·체크리스트는 관련 코드나 운영 상태가
바뀌면 낡을 수 있다. 이런 문서는 아래 등록부에 등재하고 제목 다음 머리말에 세 필드를 둔다.

```markdown
> **기준 시각:** YYYY-MM-DD HH:MM:SS UTC
> **그 뒤 미반영분:** 없음(기준 시각 이후 변경 확인) 또는 미반영 내용과 근거
> **현행 정본:** 현재 상태를 실제로 소유하는 문서·코드·등재부 포인터
```

- 빈 `그 뒤 미반영분`은 확인하지 않은 상태로 간주한다. 확인했다면 `없음`과 확인 범위를 명시한다.
- 열린 항목이 task·request·issue를 가리키면 그 항목의 종료 시 닫힌 영역으로 옮기거나 현재 상태를
  재판정한다.
- 기준 시각과 미반영분을 갱신하지 않은 채 과거 판정을 현행처럼 단정하지 않는다.

### 살아있는 문서 등록부

| 문서 | 현재 상태의 범위 | 현행 정본 |
|---|---|---|
