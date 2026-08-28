---
operator_id: operator:harness-audit
owner: harness
implementation: operators/harness-audit.sh
affected_projects:
  - all
related_initiatives: []
---

# Operator: harness-audit

## 목적과 책임

현재 상태를 소유하는 하네스 문서의 파일 참조, 상태 요약과 살아있는 문서 현재성을 읽기 전용으로 검사한다.
발견 사항을 자동 수정하거나 상태를 판정하지 않는다.

## 실행 조건

- 자동 트리거: 없음
- 수동 호출: `./operators/harness-audit.sh`
- 권장 호출: 큐레이션 중, 아카이브 이동 후, 공통 규칙·canon 커밋 전
- 스케줄 시간대: UTC (`+00:00`, 서머타임 미적용)
- 중단 조건: 필수 루트 문서를 읽을 수 없음

## 입력 계약

- `ISSUES.md`의 활성 request·proposal 표
- `INDEX.md`, 루트 등재부, `docs/`, `storage/`, `schemas/`, `indexes/`, `views/`, `research/` Markdown의 로컬
  Markdown·JSON 포인터
- `requests/`, `proposals/`의 루트와 아카이브
- `docs/README.md`의 살아있는 문서 등록부와 등록 문서 머리말
- Python 3 표준 라이브러리

## 출력과 성공 판정

- 발견 사항이 없으면 `OK harness-audit` 한 줄
- 발견 사항이 있으면 `ATTENTION harness-audit`와 안정된 검사 코드·상대 경로
- 검사를 끝냈다면 발견 여부와 무관하게 exit code `0`
- 필수 입력을 읽거나 파싱할 수 없으면 설명과 함께 non-zero

검사 범위는 다음과 같다.

- 활성 행이 가리키는 request·proposal 파일의 존재와 표 열 수
- 현재 문서가 가리키는 로컬 Markdown·JSON 파일의 존재
- 활성 요약의 800자 초과 또는 UTC 시각 3개 이상 누적
- 활성 요약이 아카이브된 request·proposal을 현행 근거로 참조하는지
- 살아있는 문서 등록 파일의 존재와 `기준 시각`·`그 뒤 미반영분`·`현행 정본` 머리말

`ATTENTION`은 정합 검토 신호이며 작업 게이트가 아니다. 실제 오류인지 자리표시자·외부 정본인지 판단한 뒤
문서 또는 검사 계약을 수정한다.

## 권한과 부작용

- 읽기 범위: 위 입력 계약의 하네스 파일
- 쓰기 범위: 없음
- 외부 변경: 없음
- 사용자 승인 필요 조건: 없음

## 실행 안전성

- 멱등성: 같은 파일 상태에는 같은 결과
- 동시 실행: 안전
- 타임아웃: 로컬 문서 수가 비정상적으로 많으면 호출자가 제한
- 재시도: 입력 파일 오류를 해결한 뒤 1회

## 실패와 복구

- 실패 분류: Python 3 부재, 필수 문서 읽기 실패, 예기치 않은 표 형식
- 복구 절차: 입력 또는 계약을 정정하고 다시 실행
- issue 승격 조건: 검사 자체가 반복적으로 실패하거나 공통 상태 정합 문제로 여러 작업이 오도됨

## 실행 증거

- 로그 위치: 표준 출력
- 보존 기간: 별도 보존하지 않음
- 민감정보 제거: 상대 경로와 요약 통계만 출력하며 문서 본문은 출력하지 않음

## 검증

- 빈 활성 표와 빈 살아있는 문서 등록부에서 `OK` 확인
- 누락 파일·비대한 요약·아카이브 참조·현재성 머리말 누락 fixture에서 각각 `ATTENTION` 확인
- 저장소 위치와 로컬 시간대가 달라도 결과가 같은지 확인

## 변경 호환성

출력 접두사 `OK|ATTENTION`, 검사 코드와 살아있는 문서 머리말 세 필드는 공개 계약이다. 검사 범위나 임계값
변경 시 `changed/`에 알린다.
