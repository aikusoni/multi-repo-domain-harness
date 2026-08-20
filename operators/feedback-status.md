---
operator_id: operator:feedback-status
owner: harness
implementation: operators/feedback-status.sh
affected_projects:
  - all
related_initiatives: []
---

# Operator: feedback-status

## 목적과 책임

`FEEDBACK.md` 설정과 `feedback/`의 구조화된 결과 이벤트를 읽어 최근 성공·실수 수, major 이상 실수,
반복 실수 패턴과 스키마 오류를 보고한다. 지침을 자동 수정하거나 행위자의 성과 점수를 만들지 않는다.

## 실행 조건

- 자동 트리거: 에이전트 시작 절차와 curator의 피드백 검토
- 수동 호출: `./operators/feedback-status.sh`
- 스케줄 시간대: UTC (`+00:00`, 서머타임 미적용)
- 중단 조건: `FEEDBACK.md`가 없거나 필수 설정 형식이 잘못됨

## 입력 계약

- 하네스 루트 `FEEDBACK.md`
- `feedback/status-YYYY-MM-DD.md`
- Python 3 표준 라이브러리

## 출력과 성공 판정

- `OK` 또는 `ATTENTION` 요약 한 줄
- 관찰 기간, 검증된 success·mistake 수, major·critical 수와 임계값
- 반복 실수 pattern 수와 임계값, 잘못된 이벤트 수
- 반복 pattern은 `repeat <pattern>=<count>`로 추가 출력
- 잘못된 이벤트는 안정 검사 코드, 상대 경로와 event ID로 추가 출력
- 설정과 파일을 정상적으로 읽어 계산을 마치면 주의 여부와 무관하게 exit code `0`

다음 중 하나면 `ATTENTION`이다.

- 관찰 기간의 major·critical 실수가 설정 임계값 이상
- 같은 mistake `pattern`이 반복 임계값 이상
- 중복 ID, 누락·알 수 없는 필드, 잘못된 분류 등 스키마 오류 존재

`ATTENTION`은 지침 검토 신호이며 작업 게이트가 아니다. curator가 원인과 근거를 확인한 뒤 필요한 경우에만
proposal을 만든다.

## 권한과 부작용

- 읽기 범위: `FEEDBACK.md`, `feedback/status-*.md`
- 쓰기 범위: 없음
- 외부 변경: 없음
- 사용자 승인 필요 조건: 없음

## 실행 안전성

- 멱등성: 같은 파일 상태와 같은 UTC 날짜에는 같은 판정
- 동시 실행: 안전
- 타임아웃: 로컬 이벤트 수가 비정상적으로 많으면 호출자가 제한
- 재시도: 설정 또는 입력 파일 오류를 해결한 뒤 1회

## 실패와 복구

- 실패 분류: Python 3 부재, 필수 설정 누락·형식 오류, 파일 읽기 실패
- 복구 절차: 계약에 맞게 설정이나 이벤트를 정정하되 과거 이벤트 본문은 고치지 않고 정정 이벤트를 append
- issue 승격 조건: 시작 절차를 반복적으로 막거나 서로 다른 환경에서 같은 입력의 판정이 달라짐

## 실행 증거

- 로그 위치: 표준 출력
- 보존 기간: 별도 보존하지 않음
- 민감정보 제거: pattern, 상대 경로, event ID와 요약 통계만 출력하고 evidence·summary 본문은 출력하지 않음

## 검증

- 빈 이벤트에서 `OK`와 0 집계 확인
- 같은 mistake pattern이 임계값에 도달한 fixture에서 `ATTENTION` 확인
- major mistake 하나가 임계값에 도달한 fixture에서 `ATTENTION` 확인
- 중복 ID, 누락 필드와 잘못된 outcome/category fixture에서 안정 검사 코드 확인
- 로컬 시간대 변경과 관계없이 UTC 관찰 기간이 같은지 확인

## 변경 호환성

`FEEDBACK.md`의 네 설정 키, 출력 접두사 `OK|ATTENTION`, 검사 코드 `F001`–`F013`과
`feedback/README.md`의 필수 필드는
공개 계약이다. 형식·임계값·분류를 바꾸면 `changed/`에 영향 `전체`로 알린다.
