---
task_id: t-a40d2e91
project: harness
operator: operator:storage-spaces
opened: 2026-08-28 05:24:02 UTC
initiative:
related_issue:
related_request:
---

# 저장 구현 재사용·어댑터 거버넌스 구축

## 목표

새 저장 요구를 직접 구현하기 전에 필요한 capability와 허용 손실을 정의하고, 검증된 연구·공개 구현·범용
엔진을 평가해 표준 adapter로 연결하며, 이식성·fallback·lineage를 유지하는 재사용 우선 거버넌스를
저장공간 아키텍처에 추가한다.

## 배경

저장공간을 조합할 수 있어도 구현 선택과 교체 계약이 없으면 하네스가 모든 엔진을 직접 만들거나 특정
제품에 종속될 수 있다. 후보 발견, 채택 판단, 실행 adapter와 정본 승격을 분리해야 한다.

## 완료 기준

- [x] capability 정의 → 구현 발견 → 평가 → adapter 연결 → fallback의 흐름이 canon에 정의된다.
- [x] Storage Space Definition v2가 reuse-first 구현 전략, 후보, portability와 fallback을 표현한다.
- [x] adapter registry·definition과 연구 reference catalog의 JSON Schema가 정의된다.
- [x] storage audit가 adapter·research 정합, 후보 근거, 공개 source와 fallback을 검사한다.
- [x] 기존 active space가 v2로 무손실 migration되고 결정적 index에 구현·이식성 정보가 반영된다.
- [x] 전체 fixture·하네스 정합·공개 위험 검토를 통과한다.

## 진행 기록

- 2026-08-28 05:24:02 UTC - 현재 r0012 저장공간 계약과 요청 범위의 차이를 확인하고 별도 작업
  브랜치에서 구현을 시작했다.
- 2026-08-28 05:27:55 UTC - 공개 원문 6건의 관련 capability를 확인하고 모두 reference-only로 등록했다.
- 2026-08-28 05:39:09 UTC - Storage Space Definition v2, adapter·research schema와 registry, audit·index·
  query 연계, 정상·위험 fixture를 구현하고 1차 정합 검사를 통과했다.
- 2026-08-28 05:41:19 UTC - 전체 operator fixture, storage·harness audit, 상태·JSON·syntax·index 안전성,
  diff와 공개 위험 검토를 통과해 작업을 완료했다.

## 완료 결과

- 완료 내용: 새 저장 구현을 capability 정의와 공개 연구·기존 구현 평가부터 시작하는 reuse-first 흐름으로
  정립했다. adapter 공통 API·registry, 후보·license·유지보수, portability·fallback을 기계 계약과 감사에
  연결하고 기존 9개 active space를 v2 native 전략으로 migration했다.
- 검증: `operators/tests/storage-spaces.sh`를 포함한 전체 operator fixture,
  `operators/storage-spaces.py audit`, 결정적 index와 URL 비복제, `operators/harness-audit.sh`,
  curation·feedback 상태 검사, Python·Bash·JSON syntax, `git diff --check`, 공개 위험 키워드 검사
- 관련 커밋: 이 task를 completed로 이동한 하네스 변경 커밋
