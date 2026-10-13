---
operator_id: operator:room-server
owner: harness
implementation: room/server.py
affected_projects:
  - all
related_initiatives: []
---

# Operator: room-server

## 목적과 입력

선택적 로컬 룸 조정 서버·웹 화면. Python 3.10+, Git, primary 하네스 checkout, `INDEX.md` 스탬프와
오너가 선택한 로컬 데이터·실행기 설정을 사용한다. 자동 스케줄·외부 메시지·모델 기본값은 없다.

Claude와 Codex용 CLI 실행기는 `room/drivers.py`에서 각각 명령·읽기/수정 프로필·결과 변환을 관리한다.
설정 type은 `claude`, `codex`, `command`; 모델을 고정하지 않으며 옵션 검사 실패 시 우회하지 않는다.

```text
python3 -B room/server.py
python3 -B room/server.py --config local/room-config.json
```

시각과 방 ID의 날짜는 UTC 고정 오프셋이다. 서버는 127.0.0.1에만 바인딩하며 Host·Origin과 로컬 토큰을
검사한다. 토큰은 시작마다 새로 생성한다. 명령 로그에 사용자 본문·설정 값·전체 URL을 남기지 않는다.

## 권한과 부작용

- 하네스 읽기: primary 판정과 INDEX 스탬프. 공유 canon·task·Git의 자동 쓰기 없음.
- 로컬 쓰기: state.json과 server.lock. 데이터·실제 경로·실행기 설정은 공유·커밋 대상이 아님.
- 실행기: 명시한 프로젝트 cwd에서 argv 직접 실행. 프롬프트는 stdin. 사람의 건별 승인 필요.
- 이 도구는 실행기의 OS sandbox가 아니다. 제품 권한·외부 부작용은 실행기와 기존 하네스 계약이 강제한다.
- transcript 내보내기: HTTP 다운로드만 제공. 정본 기록·commit·push 자동화 없음.

## 성공·실패와 복구

HTTP 상태 조회·명령 승인을 통해 실제 방·대상·결과를 확인한다. 종료 코드 0은 호출 종료일 뿐 업무
`PASS`가 아니다. 거절·실패·timeout·중단 상태는 구분하며 승인 중복 소비와 자동 재실행을 금지한다.
동일 프로젝트 실행은 방을 가로질러 직렬화한다. 외부 프로세스·IDE의 소유권은 별도 확인해야 한다.

데이터 lock 중복·linked checkout·설정 오류는 시작 실패다. lock이 남으면 실제 PID·부분 실행을 확인한 뒤
lock만 제거한다. JSON 상태 파일 오류는 보존한 채 원인을 확인하며 자동 초기화하지 않는다.
Ctrl+C는 관리 실행을 중지한다. POSIX는 프로세스 그룹, Windows는 직접 자식만 중지한다.
재시작은 running을 interrupted로 복구하며 재실행 전에 외부 부작용을 확인한다.

## 검증과 호환성

```text
python3 -B -m unittest discover -s room/tests -v
```

가짜 실행기·임시 Git·실제 localhost HTTP로 예산·fan-out·승인 경쟁·동시 프로젝트·INDEX 변경·실패·timeout·
복구·출력 제한·접근 거부를 검사한다. 데이터 스키마 version 1; 미지원 버전은 시작을 거부한다.
상태 변경은 원자 파일 교체이며 디렉터리당 서버 하나만 실행한다. 포트·연결 실패는 원인을 고친 뒤 재시도한다.
동작·상태 계약 변경은 changed에 알린다. 자세한 사용과 제한은 [room/README.md](../room/README.md),
협업 계약은 [docs/room-harness.md](../docs/room-harness.md)를 따른다.
