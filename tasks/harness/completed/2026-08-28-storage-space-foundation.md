---
task_id: t-8f31c6d2
project: harness
operator: operator:storage-spaces
opened: 2026-08-28 05:03:06 UTC
initiative:
related_issue:
related_request:
---

# 조합 가능한 저장공간 아키텍처 기반 구축

## 목표

기존 문맥·작업 기록을 유지하면서 정보 성격과 질의 목적에 맞는 여러 저장공간을 등록·조합하고, 표현 간
출처·변환·손실을 추적해 제한된 비용으로 감사·조회·문맥 조립할 수 있는 초기 메모리 아키텍처를 구축한다.

## 배경

문장 중심 기록만으로는 현재 상태, 관계, 수치, 시간, 유효기간, 관점별 충돌과 원본 근거를 찾기 위해 전체
문맥을 다시 해석해야 한다. 하나의 오브젝트 모델을 모든 정보에 강제하지 않고, 목적별 저장공간과 공통
카탈로그, 통제된 손실과 재생성 가능한 파생 계층이 필요하다.

## 완료 기준

- [x] Storage Space Definition과 Cross-Space Catalog의 JSON Schema와 운영 규약이 정의된다.
- [x] evidence·record·projection·index·cache 역할, 보존 특성, 허용 손실, 질의 방식과 재구성 계약이 정의된다.
- [x] 기존 journal·request·issue·changed·task와 선택적 object·relation·residual 공간이 registry로 연결된다.
- [x] 저장공간 감사, 결정적 catalog index 생성, 제한 조회와 작업별 문맥 조립 operator가 동작한다.
- [x] 오브젝트·그래프·필드·시계열·의미 검색은 선택 가능한 전략이며 미검증 고급 공간은 후속으로 분리된다.
- [x] 전체 fixture·하네스 정합·공개 위험 검토를 통과한다.

## 진행 기록

- 2026-08-28 05:03:06 UTC - 개선안을 현재 하네스 구조에 맞춘 초기 수직 단면으로 범위화하고 별도 작업
  브랜치에서 구현을 시작했다.
- 2026-08-28 05:09:48 UTC - 추가 개선안에 따라 Object 중심 구조를 폐기하고 Storage Space Registry와
  Cross-Space Catalog 중심의 조합 가능한 저장공간 아키텍처로 작업 범위를 갱신했다.
- 2026-08-28 05:18:07 UTC - storage control plane의 schema·registry·definition과 감사·index·query·plan·
  context operator, 정상·위험 fixture를 구현하고 1차 정합 검사를 통과했다.
- 2026-08-28 05:20:00 UTC - 전체 operator fixture, 상태 검사, 하네스 정합, JSON·diff 형식과 공개 위험
  검토를 통과해 작업을 완료했다.

## 완료 결과

- 완료 내용: 특정 데이터 모델 대신 여러 Storage Space를 registry·catalog·transformation으로 조합하는
  초기 메모리 아키텍처를 정의했다. 기존 기록을 이동 없이 연결하고 감사·결정적 index·제한 query plan·
  context operator와 공개 안전 경계를 구현했다.
- 검증: `operators/tests/storage-spaces.sh`를 포함한 전체 operator fixture, `operators/curation-status.sh`,
  `operators/feedback-status.sh`, `operators/harness-audit.sh`, `operators/storage-spaces.py audit`, JSON syntax,
  Python·Bash syntax, index 결정성, `git diff --check`, 공개 위험 키워드 검사
- 관련 커밋: 이 task를 completed로 이동한 하네스 변경 커밋
