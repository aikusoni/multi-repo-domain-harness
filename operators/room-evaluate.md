---
operator_id: operator:room-evaluate
owner: harness
implementation: room/evaluate.py
affected_projects:
  - all
related_initiatives: []
---

# Operator: room-evaluate

룸의 API·skill·품질 판정·trace·권한·복구를 fixture로 평가한다. Python 3.10+, Git, loopback socket
권한이 필요하다. 자동 스케줄·모델·계정·외부 서비스 호출·Git 변경은 없다.

```text
python3 -B -m room.evaluate
python3 -B -m room.evaluate --case api-async-run
python3 -B -m room.evaluate --output local/evaluations/current.json
python3 -B -m room.evaluate --baseline local/evaluations/current.json
```

입력은 room/evals/cases.json의 schema_version 1 manifest다. --cases로 대체 파일, 반복 --case로 정확한
ID를 선택한다. 등록된 scenario만 허용하며 임의 명령·모델 선택은 없다. 중복·미등록 case·schema 오류는
실패다. 시나리오는 독립 임시 Git·프로세스·HTTP 서버를 사용하고 정리한다. 하네스 linked worktree를
생성하지 않는다. --output은 지정한 JSON을 작성하므로 기본적으로 gitignore된 local/를 사용한다.

출력: 실제 assertion·PASS/FAIL·duration·오류 class·측정 건수·코드/선택 manifest digest와 범위 fixture-contract.
프롬프트·출력·개인 경로·token을 보고서에 넣지 않는다. 예외는 FAIL로 전파한다. 전부 성공 exit 0,
case 실패 1, 0건·입력 오류 2. baseline의 PASS 회귀·대상 누락·scenario/검사 항목 변경은 nonzero다.
깨진 baseline·중복 ID·근거 없는 baseline PASS도 거부한다. 보고서는 비정본 검증
artifact이며 공유 전 공개 위험 검토가 필요하다. 검증 실패를 자동 수정하거나 사람 승인을 대행하지 않는다.

같은 입력·코드에서 같은 assertion 결과를 기대하되 시각·duration은 달라진다. 병렬 실행은 독립 임시
경로·포트를 쓰며 같은 output 파일에 동시 쓰지 않는다. fixture timeout과 5초 상태 대기가 실행 제한이다.
권한·Git·port 실패를 정상 결과로 숨기지 않는다. 변경 후 room/tests/test_engineering.py와 전체 룸
unittest로 검증하며 계약 변경은 changed에 알린다.

실제 LLM 정답률·Injection 저항률·token 비용·고객 운영 benchmark가 아니다.
[Agent 엔지니어링](../docs/agent-engineering.md)에 전체 검증 범위와 추가 기술 채택 기준이 있다.
