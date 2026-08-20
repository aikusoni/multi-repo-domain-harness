# 검증 결과 피드백 상태

이 파일은 성공·실수 피드백 집계의 현재 설정 정본이다. 기록 형식은 `feedback/README.md`, 지침 개선 절차는
`docs/outcome-feedback.md`, 상태 확인 방법은 `operators/feedback-status.md`가 소유한다.

- observation_window_days: 30
- repeated_mistake_warning: 3
- major_mistake_warning: 1
- schema_required_since: 2026-08-20 UTC

임계값은 지침 검토가 필요한지 알리는 신호이며 작업 게이트나 개인·에이전트의 성과 점수가 아니다. 같은
`pattern`의 검증된 실수가 관찰 기간 안에 `repeated_mistake_warning` 이상이거나, `major`·`critical`
실수가 `major_mistake_warning` 이상이면 `operator:feedback-status`가 `ATTENTION`을 보고한다.

`ATTENTION`만으로 기준 문서를 자동 수정하지 않는다. 원인과 반례를 검토해 지침 문제로 확인된 경우에만
proposal을 만들고, 승인된 변경의 효과는 이후 피드백에서 재발 여부로 확인한다.
