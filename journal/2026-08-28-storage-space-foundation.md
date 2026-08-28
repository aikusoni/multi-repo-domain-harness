# 조합 가능한 저장공간 아키텍처 기반

**VALIDITY:** ACTIVE

## 2026-08-28 05:03:06 UTC · 공유 규칙 수정 경계 확인

**SESSION-COMM:** 2026-08-28 05:03:06 UTC · observe · peer: none-in-observable-scope · reason: INDEX와 저장공간 canon 수정 전 소유 확인

현재 실행 문맥의 세션 관측 범위에는 이 세션만 보였다. 다른 실행 환경·수동 편집까지 포괄하는 관측은
아니므로 다른 세션이 없다고 단정하지 않았고, 별도 작업 브랜치와 명시적 stage 경계를 적용했다.

## 2026-08-28 05:16:27 UTC · 결정과 발견

- 하네스 메모리의 중심을 특정 데이터 모델이나 저장 기술로 고정하면 정보마다 다른 보존 특성·질의·비용과
  허용 손실을 제대로 표현할 수 없다.
- Storage Space Registry를 활성 구성의 정본으로 두고, Cross-Space Catalog가 같은 정보의 여러 표현과
  lineage를 잇도록 했다.
- evidence·record는 직접 보존 계층, projection·index·cache는 파생·임시 계층으로 구분했다. Object,
  Relation, Field, 시계열과 의미 검색은 필요에 따라 선택하는 storage kind로 두었다.
- transformation은 입력·출력·방법·버전·보존 특성·손실·가역성을 선언한다. Query Planner와 Context
  Composer는 질문에 필요한 최소 공간만 골라 사용 공간, 빠진 mode와 잘린 결과를 드러낸다.
- 기존 journal·request·issue·changed·task는 이동하거나 일괄 변환하지 않고 active space definition의
  location으로 연결했다.

## 2026-08-28 05:18:07 UTC · 구현

- registry, 9개 active definition, catalog·transformation JSON Schema와 공개 안전 정책을 추가했다.
- `operator:storage-spaces`에 registry/catalog/lineage 감사, 결정적 index, 제한 query·plan·context 명령을
  구현했다.
- 정상 다중 표현과 transformation, 미등록 space와 위험 ref, index 결정성을 fixture로 검증했다.
- 기존 하네스 감사의 살아 있는 Markdown·JSON 참조 범위를 storage·schemas·indexes·views로 넓혔다.

## 2026-08-28 05:20:00 UTC · 최종 검증

- 전체 operator fixture와 Python·Bash·JSON 형식 검사를 통과했다.
- storage audit, 결정적 index 재생성, curation·feedback 상태 검사와 harness audit를 통과했다.
- 공개 위험 검사 결과 실제 비밀·개인정보·내부 경로·비공개 시스템 정보는 발견되지 않았다. 공개 JSON
  Schema 표준 식별자와 위험 ref 거부를 검증하는 예약 예시만 URL 검색에 잡혔다.
- `git diff --check`를 통과했다.

## 미해결

고급 field·시계열·semantic adapter와 실제 transformation 실행은 사용 사례와 비용 근거가 생길 때 별도
proposal로 검토한다.
