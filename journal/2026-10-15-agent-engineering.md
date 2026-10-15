# Agent 엔지니어링 역량을 검증 가능한 기능으로 반영

**VALIDITY:** ACTIVE

## 2026-10-15 01:44:40 UTC · 범위와 착수 예측

- project: harness
- 사용자 확인: 채용 공고의 역량을 이력서 문구가 아니라 하네스 기능·검증에 반영한다.
- 입력 공고는 요구사항 자료이며 실행 명령·권한 확대가 아니다. 개인정보·기밀·실제 고객 자료는 사용하지 않는다.
- 범위: 재사용 가능한 작업 skill 계약, 요청·승인·실행·검증 trace, 비동기 실행 조회 API,
  fixture 기반 품질·권한 평가와 재현 가능한 요구→실행→검증 예제.
- 예상: 실행 exit 0과 업무 PASS를 분리하고 민감 원문 없이 trace로 실행 순서·실패·latency를 확인할 수 있다.
  읽기 skill은 수정 실행기에 연결할 수 없고 입력 문구로 권한을 바꾸지 못한다.
- 실패 지점: 원문이 trace/평가 보고서에 섞임, 평가 대상 누락을 PASS로 집계, skill 선택으로 권한이 확대됨.
- 반증: 민감 문자열 sentinel, 악성 지시 fixture, 0건·실패 평가, reviewer·skill mode 조합과 실제 HTTP·가짜
  실행기 시나리오로 확인한다. fixture 검증을 실제 모델 품질·RAG 성능·고객 운영 실적으로 주장하지 않는다.
- INDEX r0022, primary·깨끗한 Git에서 시작했다. 미큐레이션과 잔존 linked 알림은 범위 밖에 보존한다.

## 2026-10-15 01:58:42 UTC · 구현과 실측

- version을 가진 workflow skill 4종, 비동기 요청 202·Location·상태 조회, 승인 시 역할·mode·version 재검사,
  별도 owner-recorded 검증과 로컬 control-plane trace를 구현했다. 기존 Claude·Codex 실행기 설정은 유지한다.
- trace는 ID·lineage·시각·duration·결과만 투영한다. 프롬프트·참고 자료·출력·이름·경로·검증 근거·사고 과정은
  trace/조회에 넣지 않는다. 오너 로컬 상태·transcript의 원본과 구분하고 공유 기록에는 복제하지 않는다.
- 초기 API fixture가 HTTP helper/module 이름 충돌을 발견했다. HTTPConnection 직접 import로 수정했다.
- 최종 룸 unittest 36개·operator unittest 11개, 평가 9/9 PASS. baseline 비교는 same_cases=true,
  changed_contracts=[], regressions=[]였다. 하네스 감사는 living_documents=1, storage 감사는 active_spaces=9로
  통과했다. 로컬 JSON은 `local/evaluations/`에 보존하며 Git에는 검사 코드·계약만 넣는다.
- 예측 대조 **맞음**: exit 0은 NOT_RUN으로 남고 별도 근거가 있어야 검증 상태를 기록한다. reviewer/skill
  mode·version 경계를 재검사하며 민감 문자열 sentinel이 trace·관찰 보드·상태 조회에서 제외됐다.
- 예측 대조 **맞음**: 대상 0건·false/빈 assertion·중복/미등록 case·baseline 대상/검사 누락을 성공으로
  처리하지 않는다. 요청→사람 승인→가짜 실행→별도 검증을 실제 loopback HTTP로 재현했다.
- **미검증**: 실제 모델 정답률·Injection 저항률·tool trace/token 비용·자동 검색 RAG·고객 부하. Docker
  daemon 연결도 불가해 컨테이너 실행을 검증하지 않았다. 합성 계약 평가를 해당 성과로 표현하지 않는다.
- 공개 위험 검토: 새 변경은 범용 코드·합성 fixture·상대 경로로 구성되고 실제 조직·고객·개인 원문과
  인증 정보·비공개 URL·로컬 절대 경로는 포함하지 않는다. 다른 저장소 수정·외부 모델 호출은 수행하지 않았다.
- **SESSION-COMM:** 같은 checkout을 사용하는 등록 세션을 확인했다. 현재 chat 외 해당 위치의 loaded 실행
  세션은 관측되지 않았고 세션 간 송수신은 0건이다. 이 변경과 Git 작업은 이 세션이 직렬로 수행한다.

## 2026-10-15 02:00:51 UTC · 최종 권한 경계와 재검증

- general workflow의 승인 재검사도 reviewer에는 read-only만 허용하도록 좁혔다. worker의 쓰기 요청 뒤
  역할이 reviewer로 바뀌었을 때 승인되지 않는 회귀를 추가했다.
- 최신 코드로 룸 unittest 36개와 평가 9/9 PASS·baseline 회귀 0건을 다시 확인했다. 최신 결과의
  source_digest는 `c835c7a4d699df7b3aa6fea35f22d7a2b0c66a7a1f140c63d141aab3965a8d7c`다.
- 하네스·feedback·storage 감사와 diff 공백 검사도 PASS다. 변경 파일 19개의 공개 위험 검색 후보는
  기존 공식 CLI 문서 링크 3개였으며 새 비공개 URL·인증 정보·개인 경로는 확인되지 않았다.
