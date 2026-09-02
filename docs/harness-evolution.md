# 증거 기반 하네스 진화

## 목적

작업 결과에서 재사용 가능한 교훈을 얻되, 한 번의 실행·자기평가·특정 작업의 우연을 곧바로 공통 규칙으로
만들지 않는다. 하네스 진화는 원시 경험을 쌓는 일이 아니라 검증된 결과를 범위와 trigger가 있는 실행
지침으로 컴파일하고, 기존 지침과 비교하며, 효과와 회귀를 다시 검증하는 과정이다.

현재 하네스는 자동 자기수정 시스템이 아니다. 에이전트나 operator가 후보를 만들 수 있지만, 공통 canon과
`INDEX.md`의 변경은 proposal·검증·사용자 승인과 Git 경계를 그대로 따른다.

## 정보 계층

```text
실행 context와 결과
        ↓ 검증
feedback event·journal evidence
        ↓ reflection
Guidance Candidate
        ↓ curator가 기존 harness와 비교
ADD · MERGE · REVISE · SKIP
        ↓ proposal·승인·검증
project/topic guidance 또는 cross-task canon
        ↓ 선택적 읽기·적용
후속 결과와 회귀 관찰
```

- 실행 trajectory와 도구 출력은 원시 자료다.
- feedback은 검증된 결과의 append-only evidence이며 지침 자체가 아니다.
- Guidance Candidate는 가능한 교훈이고, `feedback/candidates/`의 안정된 record로 보존한다.
- 승인된 canon만 후속 에이전트 행동을 구속한다.

## Candidate 형식

Guidance Candidate는 최소한 다음을 답한다.

```yaml
lesson: 에이전트가 앞으로 다르게 수행할 구체적 행동
trigger: 이 행동을 적용해야 하는 관측 가능한 조건
evidence: 검증된 feedback·test·review·상대 경로
scope_hint: cross-task | project:<id> | operator:<id> | task-type:<topic>
operation: ADD | MERGE | REVISE | SKIP
target: 기존 지침 또는 신규 위치
expected_effect: 관측 가능한 개선
regression_check: 관련·인접 작업에서 확인할 반례와 비용
cutover: backfill 또는 적용 시작 UTC 경계
```

실패나 부정적 feedback은 잘못된 가정, 누락된 제약, 약한 검증과 복구 실패를 드러내므로 후보 생성을 우선
검토한다. 검증된 성공은 효과 있는 기존 지침의 유지·간소화 근거와 실패 후보의 반례로 사용한다. 자기평가,
단순 성공 횟수와 검증되지 않은 회고만으로 candidate를 만들지 않는다.

후보 ID는 `gc-xxxxxxxx`이고 현재 상태는 `draft`, `proposed`, `accepted`, `skipped`, `superseded` 중 하나다.
활성 후보는 `feedback/candidates/`, 종결 후보는 그 아래 `archive/YYYY-MM/`에 보존한다. 원본 evidence,
operation, target, proposal·canon 포인터, 병합 관계, 결정과 재검토 trigger의 전체 형식은
`feedback/candidates/README.md`를 따른다.

## 범위 결정

- 한 프로젝트·operator·도구·작업 형식에서만 확인된 교훈은 먼저 topic guidance로 제한한다.
- 서로 다른 작업이나 프로젝트에서 공통 trigger와 효과가 확인돼야 cross-task 규칙으로 승격한다.
- 넓은 규칙이 탐색·실험·창의적 작업을 방해하거나 특정 solver만 따를 수 있으면 범위를 줄이거나 `SKIP`한다.
- 모델·런타임별 adapter 설명은 공통 행동 계약과 분리한다. 공통 canon은 숨은 추론이나 특정 도구 이름보다
  관측 가능한 입력·행동·증거를 기술한다.

## Curator 연산

candidate를 현행 규칙과 함께 읽고 다음 중 하나를 선택한다.

| 연산 | 조건 |
|---|---|
| `ADD` | 기존 지침으로 다룰 수 없는 반복 가능 행동 경계가 검증됨 |
| `MERGE` | 같은 trigger·결과의 후보가 여러 표현으로 중복됨 |
| `REVISE` | 현행 지침이 모호하거나 준수해도 의도한 효과가 없다는 근거가 있음 |
| `SKIP` | 근거 부족, 과적합, 중복, 권한 충돌 또는 비용이 예상 효과보다 큼 |

`SKIP`도 교훈을 삭제한다는 뜻이 아니다. `feedback/candidates/`의 후보를 `skipped`로 종결해 기각 이유와
재검토 trigger를 검색할 수 있게 한다. candidate를 append-only 방식으로 INDEX 끝에 그대로 붙이지 않는다.

## 규칙 작성 계약

새 규칙이나 개정 규칙은 다음 요소를 갖는다.

1. 적용 trigger와 범위
2. 필요한 행동과 금지 행동
3. 완료·준수 여부를 확인할 증거
4. 예외·권한·사용자 승격 경계
5. 근거와 예상 효과
6. 재검토·rollback 조건

`INDEX.md`에는 필수 조항과 짧은 이유·상세 계약 포인터를 두고, 긴 사례·실행 기록·반례는 관련 docs,
journal 또는 exploration에 둔다. 같은 규칙을 bootstrap 파일에 복제하지 않는다. 숫자 조항을 폐지하면
번호를 재사용하지 않고 대체 조항을 가리키는 tombstone을 남긴다.

사용자가 특정 canon 변경을 직접 요청하면 서술된 범위는 승인으로 본다. 작업 중 새로 발견한 범위 밖 canon
변경, 새 외부 부작용이나 공개 판단은 그 승인에 포함하지 않고 proposal 또는 추가 확인으로 분리한다.

새 marker·field·schema·index·검사를 도입할 때 기존 자산을 backfill할지 같은 변경에서 결정한다. 소급하지
않으면 적용 시작 UTC 경계와 그 이전 자료가 비어 있거나 미검사인 이유를 명시한다. append-only 기록은
소급 개작하지 않고 migration event나 cutover 설명을 사용한다.

## 선택과 Context 예산

승인된 지침도 매 작업에 전부 읽히지 않는다. 에이전트는 현재 project·task와 trigger에 맞는 최소 지침만
선택하고, 적용한 지침과 제외·잘린 범위를 중요한 판단의 검증 근거에 남긴다.

- topic guidance를 맞지 않는 작업에 주입하지 않는다.
- cross-task 지침도 상위 지침·현재 사용자 요청·권한을 덮어쓰지 않는다.
- context가 커지면 중복 지침을 병합하고 상세 evidence는 필요할 때 drill-down한다.
- 선택 예산은 고정 숫자를 모든 환경에 강제하지 않고 모델·작업 비용과 검색 정확도를 측정해 정한다.

## 효과 검증

규칙 변경 proposal은 관련 작업의 기준 결과, 기대 변화와 인접 범위의 회귀 검사를 포함한다. 가능하면 변경
전후 같은 verifier를 사용하고, 표본·solver·task category와 `PASS`, `FAIL`, `PARTIAL`, `NOT_RUN`을 구분한다.

- aggregate 개선만으로 특정 규칙의 인과를 단정하지 않는다.
- detailed feedback가 특정 실패에 과적합할 수 있고 sparse feedback가 원인을 놓칠 수 있으므로 작업 유형에
  맞는 feedback granularity를 선택한다.
- 다른 모델이나 프로젝트로 이전할 때는 지침을 이해·수행할 수 있는지 별도 검증한다.
- 지침을 지켰지만 의도한 예방·효과가 없으면 `instruction-ineffective`로 기록하고 `REVISE`·범위 축소·
  철회를 우선 검토한다.
- 회귀나 비용 증가가 예상 효과를 반복해서 초과하면 결정 로그의 재검토 trigger에 따라 supersede한다.
- 회상·적용 기록이 0건이라는 사실만으로 지침이 무가치하다고 단정하지 않는다. trigger가 실제로 발생했는지,
  검색·선택 계층이 후보를 노출했는지와 적용 결과를 함께 확인한다.

## 연구 참조와 적용 경계

`research:evo-harness`는 one-shot 실행 context를 `lesson`, `trigger`, `evidence`, `scope_hint` 후보로 만들고,
기존 harness에 `ADD`, `MERGE`, `REVISE`, `SKIP`으로 컴파일하는 구조, general·topic guidance 분리와 제한된
selection budget의 공개 연구 근거다. `research:evoharness-rl`은 긴 작업의 외부 상태를 현재 판단·진행·경험의
기능으로 구분하고, 접근·갱신·통합 비용을 고려해 선택적으로 사용한다는 참고 근거다.

이 하네스는 두 연구의 자동 evolver·강화학습 정책·자동 망각, 모델 선택이나 대규모 benchmark 설정을 채택하지
않는다. 현재 판단은 검증된 사실이 아니고 과거 경험은 현재 환경의 oracle이 아니다. 공개 reference에서
확인한 원칙만 현재의 사람 승인, feedback, curator, proposal과 정본 경계에 맞게 적용한다.
