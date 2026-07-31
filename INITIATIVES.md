# 활성 공동 이니셔티브 등록부

둘 이상의 프로젝트·역할·operator가 함께 달성할 측정 가능한 결과를 **Initiative(이니셔티브)**로 등록한다.
이 파일은 활성 initiative의 상태와 한 줄 결과에 대한 현재 정본이다. `initiatives/<id>.md`는 목표·범위·
참여 주체·완료 기준·연결 실행의 상세 정본이며 상태를 중복 기록하지 않는다.

## 상태

| status | 의미 |
|---|---|
| `proposed` | 공동 목표와 참여 범위 검토 중 |
| `active` | 승인되어 실행 중 |
| `blocked` | 연결된 활성 issue 때문에 진행 불가 |
| `paused` | 사용자 결정으로 일시 정지 |
| `completed` | 완료 기준 충족 및 결과 확인 완료 |
| `cancelled` | 목표를 더 이상 추진하지 않기로 결정 |

`completed`·`cancelled` initiative는 상세 문서를 `initiatives/archive/YYYY-MM/`로 옮기고 활성 표에서
제거한다. `blocked`에는 반드시 `ISSUES.md`의 원인 행을 연결하며, `paused`는 활성 표에 남긴다.

## 활성 initiatives

| ID | status | 공동 결과 | lead | 참여 프로젝트·operator | 상세 |
|---|---|---|---|---|---|

등록 예시로, 여러 프로젝트가 재고 상태를 재구성하고 재처리하며 운영 화면에서 결과를 확인해야 한다면,
`initiative:inventory-recovery-service` 하나 아래 각 프로젝트의 task·request와 통합 완료 기준을 연결한다.
