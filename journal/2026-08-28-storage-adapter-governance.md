# 저장 구현 재사용·어댑터 거버넌스

**VALIDITY:** ACTIVE

## 2026-08-28 05:24:02 UTC · 공유 규칙 수정 경계 확인

**SESSION-COMM:** 2026-08-28 05:24:02 UTC · observe · peer: none-in-observable-scope · reason: INDEX와 저장공간 canon 수정 전 소유 확인

현재 실행 문맥의 세션 관측 범위에는 이 세션만 보였다. 다른 실행 환경과 수동 편집까지 포괄하지 않으므로
다른 세션이 없다고 단정하지 않았고, 별도 작업 브랜치와 명시적 stage 경계를 적용했다.

## 2026-08-28 05:27:55 UTC · 조사와 결정

- 이질적인 자료의 점진적 통합, 여러 엔진의 공통 질의 계층, 목적별 기억 표현, 제한 context 관리와 파생
  결과 provenance를 다루는 공개 원문 6건을 확인했다.
- 모든 항목은 설계 근거인 `reference-only`로 등록했다. 특정 구현의 license·유지보수·비용·실제 적합성은
  채택 후보가 생길 때 별도로 검증하며, 현재 active adapter는 만들지 않았다.
- 구현 선택은 capability를 먼저 정의한 뒤 native·adapter·hybrid·custom-minimal 중 최소 전략을 고르는
  `reuse-first`로 확정했다. 외부 구현 우선이 아니라 불필요한 재구현과 종속을 함께 피하는 기준이다.

## 2026-08-28 05:39:09 UTC · 구현

- Storage Space Definition을 v2로 올려 selection policy, 전략·adapter·후보, fallback data access·degraded
  query mode, export format·vendor lock-in·exit plan을 필수화했다.
- adapter registry와 write·query·trace·export·rebuild·health 공통 definition schema를 추가했다.
- research catalog, 후보 근거·license·유지보수 상태와 공개 HTTPS source 검사를 추가했다.
- storage audit와 결정적 index가 adapter·research·implementation·portability를 검사·요약하도록 확장했다.
- Prediction·Plan·Outcome·Evaluation은 새 중심 엔진이 아니라 목적별 space를 조합하는 record pattern으로
  정의했다.

## 2026-08-28 05:41:19 UTC · 최종 검증

- 전체 operator fixture와 Python·Bash·JSON syntax 검사를 통과했다.
- storage audit, 결정적 index 재생성, curation·feedback 상태 검사와 harness audit를 통과했다.
- 생성 index에 research source URL이 복제되지 않음을 확인했다.
- 공개 위험 검사 결과 실제 비밀·개인정보·내부 경로·비공개 시스템 정보는 발견되지 않았다. 검증한 공개
  원문, JSON Schema 표준 식별자와 위험 URL 거부 fixture만 URL 검색에 잡혔다.
- `git diff --check`를 통과했다.

## 미해결

실제 외부 adapter와 고급 예측·계획 record schema는 확인된 query·규모·비용 요구가 생길 때 proposal로
도입한다.
