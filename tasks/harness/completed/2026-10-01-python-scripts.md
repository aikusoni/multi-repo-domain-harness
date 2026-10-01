# 하네스 실행 도구 Python 전환

- task_id: t-21b537de
- project: harness
- owner: harness
- created_at: 2026-10-01 03:58:42 UTC
- 요청: 셸·배치의 환경 영향을 줄이기 위해 Python으로 전환; 완료 후 push (배포 아님)

## 수용 기준과 완료 결과

- 운영 도구 5개와 기존 셸 테스트 5개를 Python으로 교체했다.
- Python 3.10 이상 표준 라이브러리와 Git CLI만 필요하며 Bash·Unix 유틸리티 의존을 제거했다.
- `INDEX.md` r0020, bootstrap·operator 계약·실행 안내와 외부 호출 전환 안내를 갱신했다.
- 출력 접두사·코드·UTC 계산·primary/review 차단을 유지했다.

## 검증

- PASS: 상태 도구 3개의 변경 전후 stdout·stderr·종료 코드 동일.
- PASS: `python3 -B -m unittest discover -s operators/tests -v`, 11개 테스트에서 모든 운영 도구 검사.
- PASS: 임시 Git primary·linked, 오염된 환경변수, 공백·한글 경로, dirty 보존, review ref/hook 차단.
- PASS: UTC 시간대 독립, 문서·이벤트의 오류 fixture, storage 정상·오류와 index byte 결정성.
- PASS: 실제 harness-audit와 storage-spaces audit; guard는 primary 허용과 기존 linked 잔존 ATTENTION.
- NOT_RUN: Windows 실제 환경 실행. 이식 가능한 fixture·문법을 사용했지만 실기 검증은 별도 필요.
- 관련 커밋: 이 task·journal과 실행 도구를 함께 포함한 `chore(harness): migrate operators and tests to Python`.
- push 대상: `codex/python-harness-scripts`; merge·배포는 범위 밖.

## 진행 기록

- 2026-10-01 03:58:42 UTC: 구현·검증 완료. 기존 linked worktree는 정리 권한이 없어 보존.
