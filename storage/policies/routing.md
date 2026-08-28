# Storage routing policy

## 선택 질문

1. 원본 감사, 의도, 변화, 대상, 관계, 수치, 공간, 유사성, 잔차 중 무엇을 보존해야 하는가?
2. exact, state, time-range, relation, aggregate, similarity, evidence 중 어떤 조회가 필요한가?
3. 무엇을 잃어도 되고, 무엇은 반드시 원본으로 돌아갈 수 있어야 하는가?
4. registry의 active space가 목적과 손실 한계를 충족하는가?

## 기본 routing

| 정보 | 우선 공간 | 쓰기 |
|---|---|---|
| 조사·요청·결정 과정 | narrative | 기존 기록 규칙 |
| 상태 전환·영향·검증 결과 | event | append-only |
| 활성 이슈·논의·initiative·task 상태 | current-state | 현재 문장 재작성 또는 폴더 이동 |
| 원본의 공개 안전한 식별자 | evidence-reference | versioned |
| 지속 대상·관점별 상태 | object | versioned claims |
| 명시적 연결·영향 | relation | append-only |
| 설명되지 않은 충돌·희귀 정보 | residual | append-only + review_after |

하나의 관찰을 여러 공간에 기록하면 catalog와 transformation으로 lineage를 남긴다. 의미·field·time-series
공간은 active definition과 검증된 adapter가 생기기 전에는 사용하지 않는다.
