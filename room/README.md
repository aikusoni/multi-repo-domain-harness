# 룸 서버와 웹 화면

공유 하네스의 파일 정본 위에 작업별 방을 제공하는 선택적 로컬 도구다. Python 3.10 이상과 Git만 필요하다.
패키지 설치, 데스크톱 설정 변경, 고정 모델이나 외부 계정 연동 없이 실행한다.

```text
python3 -B room/server.py
```

출력된 `127.0.0.1` 주소를 브라우저에서 연다. 주소의 로컬 토큰은 브라우저 세션에 보관하며 주소창에서는
제거한다. 다른 사람·에이전트에게 토큰을 전달하지 않는다. 이 화면은 한 사람이 자기 머신에서 쓰는
**오너 콘솔**이다. 발신자 선택은 기록의 귀속 표시이며 멤버별 로그인·권한 인증이 아니다.

기본 데이터는 gitignore된 `local/room/`의 `state.json`이다. 다른 로컬 위치는 `--data-dir`로 지정한다.
포트 변경은 `--port 9000`. 서버는 loopback에만 바인딩하고 Host·Origin·토큰을 검사한다.
인터넷·LAN 공개나 다중 사용자 운영은 지원하지 않는다.

## 방에서 하는 일

오너 화면 상단의 **익명 관찰 보드**는 별도 읽기 전용 화면이다. 전체 방과 실행·승인·재개 판단 수,
방마다의 상태·멤버 수·전달 예산만 보인다. 이름·제목·레포·대화·노트·실행 출력은 API 응답에 포함하지
않으며 방은 `Room 01` 같은 별칭으로 표시한다. 보드의 **익명 현황 저장**은 이 제한된 projection만
내려받는다. 원래 **기록 내보내기**는 전체 로컬 transcript이므로 내용 검토 없이 공유하지 않는다.
관찰 토큰은 오너 API·실행 승인에 사용할 수 없다. 로컬 작업 통계도 운영 정보이므로 공개 서버로 쓰지 않는다.

1. 목표와 완료 조건으로 방을 만들고 필요하면 `initiative:<id>`를 연결한다.
2. 조정·작업·리뷰·관찰 역할의 멤버를 연결한다. 표시 이름과 별개로 안정된 멤버 ID를 사용한다.
3. 대화의 수신자를 명시한다. 선택하지 않으면 화면에만 기록한다. 이름에서 멘션을 추측하지 않는다.
4. 긴 근거와 인수인계는 노트로 남긴다. 퇴장에는 요약이 필수다.
5. 설정한 실행기에 요청을 등록하고 사람이 정확한 명령·작업 위치·프롬프트·시간 제한을 확인해 승인한다.
6. 방을 마치면 기록을 Markdown으로 내려받고, 공개 위험 검토를 거친 필요한 결과만 기존 하네스 기록에
   옮긴다. 다운로드 자체는 공유 저장·커밋·작업 완료가 아니다.

대화는 자동으로 에이전트를 깨우지 않는다. `실행 요청 → 사람 승인 → 실행`은 별도 단계다. 성공 exit code는
`호출 종료`로 표시하며 업무 검증이나 task 완료로 취급하지 않는다. 방 종료도 task 완료와 별개다.

## Claude용·Codex용 설정

서버와 화면은 공통으로 쓰고 실행기만 분리한다. [config.example.json](config.example.json)을
gitignore된 `local/room-config.json`에 복사하고 실제 project-id와 제품 작업 위치를 채운다.
`claude-read`, `claude-edit`, `codex-read`, `codex-edit`가 독립된 실행기로 나타난다. 한 방에서 섞어 쓸 수 있다.
한 도구만 쓰려면 다른 도구의 항목을 제거한다. 실제 설정 파일은 커밋하지 않는다.

| 설정 | Claude | Codex |
|---|---|---|
| `type` | `claude` | `codex` |
| 읽기 프로필 | restricted, Read·Glob·Grep만, dontAsk | exec, read-only sandbox |
| 수정 프로필 | restricted, 위 도구에 Edit·Write 추가, acceptEdits | exec, workspace-write sandbox |
| 결과 | JSON result를 공통 결과로 변환 | JSONL agent_message를 공통 결과로 변환 |
| 모델·effort | 로컬 `model`, `effort` 선택 | 로컬 `model`, `effort` 선택 |
| CLI 위치 | 기본 `claude`, 로컬 `cli`로 변경 가능 | 기본 `codex`, 로컬 `cli`로 변경 가능 |

Codex 프로필은 sandbox를 유지하면서 비대화형 실행을 사용한다.
([공식 CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli),
[비대화형 실행](https://learn.chatgpt.com/docs/non-interactive-mode))
Claude 프로필은 restricted에서 도구 집합을 제한하고 MCP·slash command·브라우저 연동을 사용하지 않는다.
수정 프로필에도 Bash는 포함하지 않으므로 빌드·테스트는 별도 검증 실행기로 수행한다.
([공식 Claude CLI reference](https://code.claude.com/docs/en/cli-reference))

두 도구의 권한 의미는 같지 않다. read-only reviewer는 읽기 프로필만 사용한다. 프로필에 정의한 작업
위치 밖의 파일·공유 하네스를 쓰기 허용에 추가하지 않는다. INDEX 전체는 서버가 현재 원본을 프롬프트에
포함한다. Claude restricted는 사용자·프로젝트 설정을 읽지 않으므로 제품의 추가 지침도 사람이 프롬프트에
포함하고 결과를 확인한다. 설정·관리 정책·MCP·hook이 있는 로컬 환경은 각 도구의 실제 권한을 별도로 검토한다.

CLI 설치와 로그인은 각각 로컬에서 준비한다. 모델 호출 없이 지원 옵션만 확인할 수 있다:

```text
python3 -B room/drivers.py --provider claude --check
python3 -B room/drivers.py --provider codex --check
```

이 검사는 인증·모델 접근·실제 추론의 성공을 확인하지 않는다. 필요한 옵션이 없거나 CLI가 손상되면
우회 모드로 내려가지 않고 명시적으로 실패한다. 실제 호출은 룸의 사람이 승인한 실행에서만 수행한다.

## 사용자 정의 실행기 연결

gitignore된 `local/room-config.json`을 직접 작성한다. 아래 값은 예시 자리표시자다. 실제 프로젝트 이름은
`PROJECTS.md`의 `project-id`와 맞춘다. 실제 경로·명령·인증 값은 공유 문서에 복사하지 않는다.

```json
{
  "projects": {"project-a": "/absolute/path/to/project-a"},
  "drivers": {
    "local-agent": {
      "argv": ["/absolute/path/to/agent-wrapper"],
      "timeout": 120
    }
  }
}
```

```text
python3 -B room/server.py --config local/room-config.json
```

실행기 계약은 **stdin으로 UTF-8 작업 지시 수신, stdout/stderr로 결과 반환, 종료 코드로 호출 상태 표시**다.
shell을 통하지 않고 `argv` 그대로 실행하며 프롬프트를 명령 인자로 보간하지 않는다. 실행기는 사용하는
모델 CLI·SDK의 래퍼가 될 수 있다. 인증·모델·사용량·sandbox 설정은 그 래퍼의 로컬 계약으로 둔다.
명령 설정을 수정하면 서버를 다시 시작한다. 사용자 정의 실행기는 `type: command`를 생략할 수 있다.

**이 서버는 실행기 프로세스를 OS sandbox로 격리하지 않는다.** cwd 설정은 파일 접근 통제가 아니다.
쓰기·읽기 전용·리뷰 권한은 실행기 자체의 sandbox와 프로젝트 지침에서 강제해야 한다. 서버가 부여한
승인은 프롬프트 한 건의 실행 승인이다. push·merge·배포·외부 연락은 해당 사용자 권한을 별도로 확인한다.
상속 환경에 인증 정보가 있을 수 있으므로 신뢰하는 실행기만 등록하고 필요한 환경만 전달하는 래퍼를 쓴다.

실행 프로젝트로 하네스 자체·하위 디렉터리·상위 디렉터리는 등록할 수 없다. 서로 다른 방에서도 같은
프로젝트의 서버 관리 실행은 하나씩만 허용한다. 외부 IDE·터미널의 동시 작업까지 탐지하지는 않으므로
공유 파일·Git 소유권은 기존 세션 조정 계약으로 확인한다. 서버는 Git 브랜치·worktree를 생성하거나
stage·commit·push·merge하지 않는다.

## 중단과 복구

- `중지`·timeout은 실행 프로세스 그룹을 중지한다(POSIX). Windows는 직접 자식 프로세스만 중지한다.
  쓰인 파일이나 외부 부작용을 되돌리지 않으므로 결과를 확인하고 새 요청을 만든다.
- 재시작 시 `running` 작업은 `interrupted`가 된다. 승인된 호출을 자동 재실행하지 않는다.
- 중단·시간 초과 실행의 **재개 판단**에서 부분 부작용 확인 체크를 한 뒤 새 요청 준비 또는 재실행하지
  않음을 선택한다. 새 요청 준비는 자동 실행이 아니며 별도 승인 카드가 생긴다. 이전 결과는 보존한다.
- 데이터 디렉터리의 `server.lock`으로 서버 중복을 차단한다. 비정상 종료 후 lock이 남으면 기존 PID의
  프로세스와 부분 실행을 확인한 뒤 해당 lock만 수동 제거한다. 상태 파일을 지우지 않는다.
- 실행 출력은 최대 64,000 bytes만 보관한다. 긴 출력은 원본 실행기의 로컬 기록에서 확인한다.
- 실행 중인 작업은 방 종료·멤버 퇴장 전에 중지해야 한다. 대기 승인은 종료·퇴장 시 거절한다.
- INDEX 스탬프가 바뀌면 기존 방의 실행 승인을 거부한다. 규칙 전체와 동적 상태를 다시 읽고 새 방에서
  필요한 맥락만 이어받는다. 과거 승인에 새 규칙을 소급 적용해 실행하지 않는다.

## 화면 업데이트와 입력 보존

서버는 시작한 시점의 HTML·CSS·JavaScript를 고정한다. 파일을 고친 뒤 서버를 재시작하면 새 화면 버전이
된다. 열린 탭에는 안내를 표시하며 자동으로 새로고침하지 않는다. 메시지와 일반 폼 초안은 이 탭의
sessionStorage에만 보관해 새로고침 후 복원한다. 승인 체크는 복원하지 않는다. 서버 재시작 후에는
출력된 새 오너 주소를 같은 탭에서 열고, 관찰 보드도 오너 화면의 새 링크로 다시 연다.
초안·오너 화면·전체 transcript에는 개인 정보가 있을 수 있으며 보드의 제외 정책이 그것까지 지우지는 않는다.

## 인용 답글·코드 비교·테마

메시지의 **↪ 답글**로 원문을 인용하고 인용을 누르면 원문으로 이동한다. 검색 중이면 검색을 해제한다.
답글 취소도 가능하다. 입력·원문 ID·발신자·수신자는 방별로 탭 초안에 보관한다. 메시지는 원문 ID만
연결하고 원문 본문을 복제하지 않는다. 같은 방의 메시지만 허용하며 기존 tx 10건·멤버 수신 5건을 따른다.
API에서 targets를 생략하면 활성 원문 작성자를 대상으로 삼고, 명시한 targets(빈 배열 포함)가 우선한다.
메시지는 자동 실행을 유발하지 않는다. Ctrl/Cmd+Enter로 전송하고 Enter는 줄바꿈이다.

**코드 비교** 버튼 또는 `/비교 <project-id>`(`/diff`도 가능)로 연다. `/비교 <project-id> HEAD~1...HEAD`는
공통 조상부터 대상까지 비교한다. 입력 명령은 대화나 에이전트에 보내지 않는다.

- 해당 방에 멤버가 연결된 등록 프로젝트만 선택한다. 기본은 HEAD → 현재 작업 파일이며 staged·unstaged를
  함께 비교하고 untracked는 제외한다. 기준 → 대상 commit과 공통 조상 → 대상 commit도 선택할 수 있다.
- 파일 목록의 추가·수정·삭제와 +/−, 전후 줄 번호·나란히 코드·변경 글자를 보여준다. rename은 삭제/추가다.
  바뀐 줄 필터·줄바꿈·파일/변경 이동을 지원한다. 코드 칸에서 J/K는 변경, N/P는 파일, W는 줄바꿈,
  방향키·PageUp/Down·Space·Home/End는 스크롤이다. Esc는 선택 해제 후 비교창을 닫는다.
- ref는 로컬 commit으로 고정하고 fetch·checkout·stage·commit·merge를 하지 않는다. 외부 diff·textconv·
  fsmonitor는 사용하지 않고 clean/process filter가 설정된 저장소의 작업 파일 비교는 거부한다(commit
  비교는 가능). symlink·submodule 내용은 제공하지 않는다. 경로 이탈·Git 옵션/ref 조작도 거부한다.
- 인증·환경 경로는 목록과 내용에서 제외한다. 일반 파일 하나 512,000 bytes, 전후 합계 6,000줄,
  변경 1,000파일, Git 호출별 8초·출력 상한을 적용한다. 이진·비UTF-8·한도 초과는 정상 텍스트로 표시하지
  않는다. 코드의 임의 개인정보·기밀을 자동 판별·정화하는 기능은 아니다.

비교창의 줄 클릭·Shift+클릭으로 질문 범위를 고른다. 선택하지 않으면 바뀐 줄을 쓴다. **질문 요청 준비**는
화면의 파일 지문을 재확인하고 최대 약 10,000자 자료를 담은 investigate 요청을 pending으로 만든다.
질문 담당과 프로젝트가 같고 실행기는 read-only여야 한다. 오너가 명령·전달 자료를 확인해 건별 승인해야
실행한다. Claude·Codex의 기존 개별 프로필과 오너 로컬 모델 선택을 사용하며 모델을 기본 호출하지 않는다.
응답은 비교창과 기존 실행 이력에 표시한다. 원본 코드·질문·응답은 로컬 비정본 job에 남고 관찰 보드·trace에
전달하지 않는다. 이전 파일 지문에 대한 답은 표시로 구분한다. 프로세스 성공은 업무 PASS가 아니다.

헤더 **테마**에서 밝게·어둡게·시스템 연동과 숲·바다·모래 색상을 조합한다. 같은 서버 origin의 오너 화면과
관찰 보드가 브라우저 localStorage 설정을 공유하며 탭 간 변경도 반영한다. 설정에는 mode·palette만 저장하고
룸 내용·인증 정보를 넣지 않는다. 서버나 다른 사용자의 설정·권한은 바꾸지 않는다. 시스템 모드는 각 탭의
prefers-color-scheme을 따른다. 브라우저 저장소가 차단되면 기본값으로 동작한다.

## Skills·비동기 API·Trace·평가

investigate·review-change·implement-change는 version·역할·mode·산출물을 가진 룸 workflow다. 기존 호출은
general로 유지한다. mode 없는 custom 실행기는 제한 skill에 연결할 수 없다. 오너 GET /api/skills로
계약을 조회한다. 개인 Codex/Claude plugin skill을 설치하는 기능은 아니다.

오너 POST /api/runs는 room_id·member_id·driver·prompt와 선택적 skill·references를 받아 202·job_id·
trace_id·Location을 반환한다. GET /api/runs/<job-id>?room_id=<room-id>에서 조회하며 pending은 승인
대기다. 실행은 별도 approve가 필요하다. 관찰 token에는 접근 권한이 없다. references는 사람이 제공한
비정본 자료이며 자동 검색 RAG는 아니다.

조회 trace는 요청·승인·실행·검증·복구 span과 duration·exit·출력 잘림만 담는다. 프롬프트·참고 자료·출력·
경로·이름·검증 근거 본문과 모델 사고 과정은 포함하지 않는다. 모델 tool call·token은 미수집이다.
exit 0이어도 검증은 NOT_RUN이며 실제 검사 후 오너 action record_verification으로 job_id·status·evidence를
기록한다. source=owner-recorded로 자동 평가와 구분한다.

```text
python3 -B -m room.evaluate --output local/evaluations/current.json
python3 -B -m room.evaluate --case api-async-run
```

이 데모·평가는 합성 fixture와 가짜 실행기다. 0건·실패·입력 오류를 성공으로 처리하지 않으며 실제 모델
품질·운영 실적으로 표현하지 않는다. [구현·검증 범위](../docs/agent-engineering.md)와
[평가 operator](../operators/room-evaluate.md)에 전체 계약·추가 검증 기준이 있다.

## 범위와 제한

방·멤버·실행·승인·대화 검색·노트·내보내기와 기존 하네스 통신 예산을 제공한다. 모델 자동 선택,
자동 멤버 생성, 자율 대화 라우팅, 기존 데스크톱 세션 초대, 외부 이슈·메신저 연동, 예약 실행,
제품 worktree 자동 통합은 내장하지 않는다. 이들 기능에는 각각 실행기·소유권·권한 계약이 필요하다.
로컬 상태는 기억 검색 DB나 새 공유 정본이 아니며, 파일 기반 하네스는 서버 없이 계속 사용할 수 있다.

검증:

```text
python3 -B -m unittest discover -s room/tests -v
```

LLM·외부 서비스 호출 없이 임시 저장소와 가짜 실행기로 예산·경계·승인 경쟁·실패·복구·HTTP를 검증한다.
운영 계약은 [룸 협업 계약](../docs/room-harness.md), 실행 계약은
[room-server operator](../operators/room-server.md)를 따른다.
