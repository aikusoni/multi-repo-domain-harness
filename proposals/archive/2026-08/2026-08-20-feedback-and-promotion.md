# 제안: 검증 결과 피드백과 변경 승격 보호

- 대상: `INDEX.md`, `FEEDBACK.md`, `feedback/`, `docs/outcome-feedback.md`,
  `docs/change-promotion.md`, `operators/`
- 관련 프로젝트: harness
- 관련 initiative: 없음

## 변경 내용

1. 검증된 성공·실수를 구조화된 append-only 이벤트로 기록하고 최근 수치, major 이상 실수와 반복 원인을
   읽기 전용 operator로 집계한다.
2. 카운트를 행위자 점수나 자동 규칙 수정에 사용하지 않고, curator의 원인 검토와 사람 승인 proposal을
   거쳐 지침 개선으로 연결한다.
3. 작업본, 로컬 전용 불변 review 스냅샷, 공동 작업용 원격 PR, feature, release·정본을 분리한다.
4. 로컬 review 브랜치 생성·감사와 commit·push 차단에 사용할 operator를 제공한다.

## 근거

사용자는 실수와 잘된 결과를 세어 지침을 개선하는 기능, 작업 변경이 배포 환경에 바로 반영되지 않는
브랜치 전략, `review/<작업주제>_<timestamp>` 로컬 스냅샷과 공동 작업용 원격 PR 브랜치의 분리를 요청하고
이 방향의 하네스 반영을 승인했다.

원시 카운트만 사용하면 일상 성공을 부풀리거나 심각한 실수를 다수의 성공으로 상쇄할 수 있다. 결과를
검증 증거, 원인 pattern, 도입·발견 단계와 함께 기록하고 변경 전후 재발을 비교해야 지침 개선에 사용할 수
있다. 브랜치 이름만으로는 승인을 강제할 수 없으므로 불변 스냅샷, SHA·tree 증거, 승인 무효화와 push
차단을 함께 계약해야 한다.

## 영향

- 모든 참여 프로젝트는 시작할 때 feedback 상태를 확인하고 정보 가치가 있는 검증 결과를 기록한다.
- 작업 저장소는 자기 브랜치·배포 규약에 공통 승격 불변식을 적용한다.
- `operator:feedback-status`와 `operator:review-branch`가 새 공개 계약이 된다.
- 정상 작업마다 의무적으로 성공 이벤트를 만드는 규칙은 추가하지 않는다.

## 수용 기준

- 피드백 이벤트 형식과 분류, 집계 임계값, proposal 기반 개선 절차가 문서와 자동 검사에서 일치한다.
- 개인·공동 작업 흐름에서 로컬 review와 원격 PR의 책임이 구분된다.
- review 브랜치 이름·불변성·원격 push 금지와 승인 뒤 변경 시 재검토가 명시된다.
- fixture, feedback 상태, 큐레이션과 하네스 정합 검사가 통과한다.
- 공개 위험 정보가 없고 변경이 별도 브랜치에 커밋되어 원격 PR 브랜치로 push된다.

## 승인과 반영

- 2026-08-20 01:26:53 UTC - 사용자가 충분한 검토 뒤 하네스를 개선하고 원격에 push하도록 승인했다.
- 2026-08-20 01:37:26 UTC - 기준 문서, 두 operator와 fixture를 구현하고 로컬 검증을 통과했다.
- 반영 위치: `INDEX.md` 규칙 26·27, `docs/outcome-feedback.md`, `docs/change-promotion.md`,
  `operator:feedback-status`, `operator:review-branch`
