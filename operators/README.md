# operators

실행 자동화의 동작 계약을 관리한다. operator마다 `operators/<id>.md`를 만들고 `OPERATORS.md`에 한 줄
색인을 등록한다.

## 프로젝트와 operator의 경계

- 프로젝트는 도메인 결과와 코드 저장소의 책임을 소유한다.
- operator는 반복 가능한 자동화 동작과 그 입출력 계약을 소유한다.
- operator를 실행·수정하는 에이전트의 정체성은 operator가 아니라 `owner` 프로젝트다.
- 브랜치, worktree, task id와 커밋은 정체성이 아니라 작업 문맥과 결과 증거다.

## 필수 계약

각 operator 문서는 다음을 정의한다.

- 목적, owner, 영향을 받는 프로젝트
- 구현 위치와 호출 방법
- 자동·수동 실행 조건과 UTC `+00:00` 기준 스케줄(서머타임 미적용)
- 입력, 출력과 성공 판정
- 읽기·쓰기 권한과 외부 부작용
- 멱등성, 동시 실행, 타임아웃과 재시도
- 실패 분류, 중단 조건과 복구 절차
- 로그·실행 증거의 위치와 보존 정책
- 비밀·개인정보·내부 정보 취급 방식
- 검증 방법과 변경 호환성

operator의 process exit code와 업무 판정은 별도 계약이다. wrapper·집계 operator는 하위 명령 실패를
전파하고 결과를 `PASS`, `FAIL`, `PARTIAL`, `NOT_RUN`으로 구분한다. 기대 대상 수, 실제 관측 단위, 제외
경로와 대상 0건을 함께 보고하며, 비게이팅 `ATTENTION`을 실행 오류와 혼동하지 않는다. 외부 상태를 바꾸는
operator는 timeout·재시도 전에 부분 실행과 멱등성을 확인하고 완료 뒤 대상 상태를 가능한 범위에서 다시
읽는다.

## 공통 거버넌스

operator도 기존 하네스 흐름을 사용한다.

| 상황 | 기록 위치 |
|---|---|
| 여러 프로젝트·operator가 공유하는 결과 | `INITIATIVES.md` + `initiatives/` |
| 신규 개발, 수정, 수동 실행 요청 | `requests/` |
| 실패, 계약 위반, 반복 장애, 작업 차단 | `ISSUES.md` + `issues/` |
| 동작 계약·권한·영향 범위 변경 | `changed/` |
| 구현·유지보수 작업 | `tasks/operator-<id>/` |
| 설계 변경 제안 | `proposals/` |
| 조사·시행착오 | `journal/` |
| 검증된 성공·실수와 지침 효과 | `feedback/` |

정상적인 반복 실행은 request나 issue를 만들지 않는다. operator 문서에 정의한 로그 또는 외부 실행 기록에
증거를 남기고, 사람의 판단·다른 주체의 작업·계약 변경·차단 처리가 필요할 때만 이슈로 승격한다.

## 요청과 이슈의 주체 표기

- operator 대상: `target: operator:<id>`
- operator가 감지해 생성한 요청: `from: operator:<id>`와 실제 실행 owner를 본문에 기록
- 관련 이슈: operator 식별자와 영향을 받는 프로젝트를 모두 기록
- 관련 initiative: operator 상세 문서의 `related_initiatives`와 initiative 상세 문서를 서로 연결
- 파일명과 디렉터리에서는 콜론 대신 `operator-<id>` 사용

operator가 자동으로 하네스 파일을 수정할 때도 `INDEX.md`의 공개 위험 정보 검토와 Git 규칙을 동일하게
적용한다. 특히 `project-id: harness`의 가변 operator 실행은 primary checkout에서만 허용하며 시작·재개와
stage·commit·push 직전에 `operator:harness-worktree-guard check`를 통과한다. 참여 프로젝트를 대상으로
실행하는 operator의 worktree 정책은 해당 프로젝트 계약을 따른다.

## Python 실행 환경과 전환

모든 운영 도구와 회귀 검사는 Python 3.10 이상 표준 라이브러리로 실행한다. 별도 pip 패키지, Bash,
배치 파일, `awk`, `sed`, `date`, `mktemp`가 필요하지 않다. Git 관련 도구와 해당 테스트에는 PATH에서
실행 가능한 Git CLI가 필요하다. 출력 인코딩은 UTF-8이고 날짜 계산은 UTC다.

macOS·Linux에서는 `python3`, Windows에서는 `py -3` 또는 Python 3.10 이상을 가리키는 `python`을
사용한다. 실행 권한이나 shebang에 의존하지 않고 인터프리터로 직접 실행한다.

```text
python3 operators/harness-worktree-guard.py check .
python3 operators/curation-status.py
python3 operators/feedback-status.py
python3 operators/harness-audit.py
python3 operators/review-branch.py audit .
python3 operators/storage-spaces.py audit
python3 -B -m unittest discover -s operators/tests -v
```

기존 `.sh` 진입점과 셸 테스트는 Python 구현·unittest로 교체했다. 기존 외부 bootstrap, 자동화와 사용자가
별도 설치한 Git hook의 호출 경로도 `.py`와 Python 인터프리터로 변경해야 한다. 이 저장소 밖의 설정이나
hook은 자동 수정하지 않는다. 출력 접두사·검사 코드·정상 종료 코드와 primary/review 차단 계약은 유지한다.
`review-branch pre-push`는 Git의 remote 인자를 허용하고 stdin을 그대로 검사하며, 형식 오류는 exit code
`2`로 거부한다. Git 조회 실패를 정상 상태로 삼키지 않는다.

`curation-status`, `feedback-status`, `harness-audit`의 `--root <path>`는 fixture·진단용 선택 인자다.
생략하면 현재 작업 디렉터리가 아닌 스크립트가 속한 하네스 루트를 사용한다. Git 도구의 repository 인자는
기존처럼 생략 시 현재 디렉터리를 사용한다. 공백이 있는 경로는 터미널에서 따옴표로 감싼다.

Windows 명령 예시:

```text
py -3 operators/harness-worktree-guard.py check .
py -3 operators/curation-status.py
py -3 -B -m unittest discover -s operators/tests -v
```
