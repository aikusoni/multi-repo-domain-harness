# 2026-10-01 Python 실행 도구 전환

**VALIDITY:** ACTIVE

## 2026-10-01 03:54:40 UTC · 착수

- 목표: 운영 도구·회귀 검사를 Python 표준 라이브러리로 전환하고 Bash 및 Unix 유틸리티 의존 제거.
- 범위: 현재 harness 저장소의 운영 도구 5개, 기존 Python 도구의 호출 안내, 테스트와 현행 문서.
- 예상: 기존 출력 접두사·검사 코드·종료 코드, UTC 계산, review 차단 및 primary 판정은 유지된다.
- 주요 실패 지점: Git 환경변수 오염, 공백·비ASCII 경로, stdin hook 입력과 fixture 누락.
- 반증: 임시 Git 저장소와 문서 fixture에서 기존 수용 기준이 실패하거나 Bash 없이 실행할 수 없으면 전환 미완료.
- 검증: Python unittest, 기존 도구와 출력 비교, 실제 harness 감사. Windows 실제 실행은 별도 확인 대상.
- 배포 권한: 사용자는 배포 요청을 정정해 완료 후 Git push만 요청했다.

**SESSION-COMM:** 2026-10-01 03:54:40 UTC · observe · peer: harness@prior-python-request · reason: 공유 파일·Git 상태 수정 전 동일 checkout 채팅 확인; 원본 turn은 INDEX 읽기 후 interrupted이며 파일 변경 없음 · ref:operators/

## 2026-10-01 03:58:42 UTC · 구현·검증

- 상태 도구는 셸 내 embedded Python을 직접 실행 파일과 main 함수로 옮겼다. root는 스크립트 위치 기준이고
  fixture용 `--root`를 제공한다. Git 도구는 subprocess argument list로 호출하며 shell을 사용하지 않는다.
- 기존 상태 도구 3개의 stdout·stderr·종료 코드를 직접 비교해 일치를 확인했다.
- Python unittest 11개 PASS. 기존 셸 fixture 수용 기준을 보존하고 curation·오류 입력·시간대·경로 검증을 추가했다.
- 처음 guard fixture의 non-Git 디렉터리를 Git 저장소 내부에 만들어 실패했다. Git은 상위 저장소를 찾으므로
  별도의 임시 형제 디렉터리로 수정한 뒤 검사 통과. 구현의 primary 판정은 문제 없었다.
- 실제 harness-audit와 storage audit는 OK. guard는 primary 허용, 기존 linked 1개 잔존을 ATTENTION으로 보고한다.
- 예측 대조: 맞음 — 기존 계약과 실행 결과는 보존됐다. Windows 실제 실행은 NOT_RUN이며 이식성은 실기 미검증.
- `.sh` 파일 10개 제거, `.py`와 unittest 진입점으로 전환. append-only 과거 이력의 실행 경로는 소급 수정하지 않았다.
- 공개 위험 검토: 인증정보·실제 데이터·내부 endpoint·사용자 절대경로를 새 변경에 포함하지 않음.
- 사용자가 허용한 작업 브랜치 push만 수행하며 merge·배포는 하지 않는다.
