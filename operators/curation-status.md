---
operator_id: operator:curation-status
owner: harness
implementation: operators/curation-status.py
affected_projects:
  - all
related_initiatives: []
---

# Operator: curation-status

## 목적과 책임

`CURATION.md`의 임계값과 `journal/` 루트·아카이브 상태를 읽어 큐레이션 주의 신호를 한 줄로 보고한다.
규칙을 바꾸거나 저널을 자동 승격·무효화·보관하지 않는다.

## 실행 조건

- 자동 트리거: 에이전트 시작 절차
- 수동 호출: `python3 operators/curation-status.py`
- 스케줄 시간대: UTC (`+00:00`, 서머타임 미적용)
- 중단 조건: `CURATION.md`가 없거나 필수 설정 형식이 잘못됨

## 입력 계약

- 하네스 루트 `CURATION.md`
- `journal/YYYY-MM-DD-*.md`와 `journal/archive/YYYY-MM/YYYY-MM-DD-*.md`
- Python 3.10 이상 표준 라이브러리
- 선택 인자 `--root <path>`: 생략하면 스크립트가 속한 하네스 루트; fixture·진단용

## 출력과 성공 판정

- `OK` 또는 `ATTENTION` 한 줄
- 마지막 큐레이션 뒤 UTC 활동이 있는 미큐레이션 저널 수와 임계값
- 미큐레이션 저널 중 아카이브에 있는 수
- 마지막 큐레이션 UTC 시각과 경과 일수
- `validity_required_since` 이후 생성된 저널의 `VALIDITY` 누락 수
- 설정을 정상적으로 읽고 상태를 계산하면 주의 여부와 무관하게 exit code `0`

`ATTENTION`은 작업 게이트가 아니다. 에이전트는 첫 사용자 응답에서 상태를 알리고, 사용자가 다른 작업을
지시하면 그 작업을 계속할 수 있다.

## 권한과 부작용

- 읽기 범위: `CURATION.md`, `journal/` 루트와 아카이브 Markdown 파일
- 쓰기 범위: 없음
- 외부 변경: 없음
- 사용자 승인 필요 조건: 없음

## 실행 안전성

- 멱등성: 같은 파일 상태와 같은 UTC 날짜에는 같은 판정
- 동시 실행: 안전
- 타임아웃: 로컬 파일 수가 비정상적으로 많으면 호출자가 제한
- 재시도: 설정 또는 파일 읽기 실패를 해결한 뒤 1회

## 실패와 복구

- 실패 분류: Python 3 부재, 필수 설정 누락·형식 오류, 파일 읽기 실패
- 복구 절차: 계약에 맞게 `CURATION.md`를 정정한 뒤 다시 실행
- issue 승격 조건: 시작 절차를 반복적으로 막거나 서로 다른 환경에서 판정이 달라짐

## 실행 증거

- 로그 위치: 표준 출력
- 보존 기간: 별도 보존하지 않음
- 민감정보 제거: 파일명만 출력하며 본문을 출력하지 않음

## 검증

- 정상 설정에서 exit code `0`과 `OK|ATTENTION` 출력 확인
- 마지막 큐레이션 이후 UTC 활동 시각이 있는 루트·아카이브 저널이 같은 방식으로 집계되는지 확인
- 임계값 초과와 `VALIDITY` 누락 fixture에서 `ATTENTION` 확인
- 로컬 시간대 변경과 관계없이 UTC 경과 일수가 같은지 확인

## 변경 호환성

`CURATION.md`의 네 설정 키와 출력 접두사 `OK|ATTENTION`은 공개 계약이다. 저널의 UTC 활동 시각은 본문에
있는 `YYYY-MM-DD HH:MM:SS UTC` 중 가장 늦은 값으로 판정하고, 값이 없으면 파일명 UTC 날짜의 끝으로
보수적으로 판정한다. 변경 시 `changed/`에 알린다.
