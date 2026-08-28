# 로컬 저장 실행·기억 신뢰성 장기 로드맵

**VALIDITY:** ACTIVE

## 2026-08-28 05:48:09 UTC · 범위 결정

- 현재 파일·Git record와 결정적 JSON index를 안정 기반으로 유지한다.
- Local Storage Broker, embedded·service DB, 자동 context injection과 Memory Fault는 구현 완료 기능이 아니라
  측정된 병목과 별도 proposal 승인이 필요한 장기 후보로 분리한다.
- 실행 계층은 projection·index·cache만 가속하며 새 정본이 되지 않는다. 실패 시 파일 기반 선택적 읽기와
  source record로 복귀하고, 파생 상태는 rebuild 또는 안전하게 폐기할 수 있어야 한다.
- 기억 신뢰성은 존재·검색 가능·검색됨·문맥 포함·실제 사용을 구분한다. 특히 `not_found`를
  `not_searched`, `not_indexed`, `stale`, `partial`, `failed`와 혼동하지 않는 계약을 둔다.

## 2026-08-28 05:48:09 UTC · 설계 반영

- 실행 API·broker 책임, 공간 후보, embedded 우선 실행 방식, Git record와 로컬 파생 상태의 분리, 측정 기반
  도입 조건과 5단계 로드맵을 `docs/local-storage-runtime.md`에 정의했다.
- 관찰·저장·색인·routing·retrieval·selection·compression·attention 실패 단계, Retrieval Status, future
  Memory Fault, 저장 상태, Query Trace, fallback과 신뢰성 fixture를 `docs/memory-reliability.md`에 정의했다.
- 현재 operator가 daemon·broker·자동 인출을 이미 제공한다고 오해하지 않도록 architecture·adapter·role·
  README와 용어 경계를 갱신했다.

## 미해결

실제 runtime schema, broker process, 증분 index와 Memory Fault 구현은 도입 조건에 맞는 반복 측정이 생길 때
별도 proposal과 task로 시작한다.

## 2026-08-28 05:54:27 UTC · 최종 검증

- 전체 Bash syntax와 operator fixture, 임시 cache를 사용한 Python compile을 통과했다.
- storage audit·결정적 index 재생성·query plan, curation·feedback 상태와 harness audit를 통과했다.
- 전체 JSON parse, 생성 index의 source URL 비복제와 `git diff --check`를 확인했다.
- 공개 위험 검사에서 실제 비밀·개인정보·조직별 시스템 정보·내부 경로는 발견되지 않았다. 검증된 공개
  연구 원문·JSON Schema URL, private URL을 거부하는 코드와 fixture만 검색됐다.
