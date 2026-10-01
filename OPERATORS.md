# Operator 식별 등록부

하네스에서 실행 가능한 자동화를 등록한다. operator는 프로젝트를 대체하지 않으며, 에이전트의 정체성도
아니다. operator를 실행하거나 수정하는 에이전트는 현재 담당 저장소의 `project-id`로 식별한다.

## 식별 규칙

- 논리 식별자: `operator:<id>`
- `<id>`: 소문자 영문·숫자와 하이픈으로 구성한 kebab-case
- 파일·디렉터리 식별자: `operator-<id>`
- 상세 계약: `operators/<id>.md`
- 유지보수 작업 큐: `tasks/operator-<id>/`

## 등록 형식

```markdown
### operator:<id>
- **목적**: 자동화가 제공하는 결과
- **owner**: PROJECTS.md에 등록된 소유 프로젝트
- **구현**: 실행 파일, 패키지 또는 외부 실행 위치
- **계약**: operators/<id>.md
- **영향**: 관련 프로젝트 또는 전체
```

## 등록된 operator

### operator:curation-status
- **목적**: 루트·아카이브의 미큐레이션 저널 수, 마지막 큐레이션 경과와 유효성 메타데이터 누락을 보고한다.
- **owner**: harness
- **구현**: `operators/curation-status.py`
- **계약**: `operators/curation-status.md`
- **영향**: 전체

### operator:harness-audit
- **목적**: 활성 항목 파일, 현재 참조, 상태 요약과 살아있는 문서의 정합을 읽기 전용으로 검사한다.
- **owner**: harness
- **구현**: `operators/harness-audit.py`
- **계약**: `operators/harness-audit.md`
- **영향**: 전체

### operator:harness-worktree-guard
- **목적**: 하네스의 현재 checkout이 primary인지 판정해 linked worktree의 가변 작업을 차단하고, 잔존
  linked worktree 수를 경로 없이 감사한다.
- **owner**: harness
- **구현**: `operators/harness-worktree-guard.py`
- **계약**: `operators/harness-worktree-guard.md`
- **영향**: harness

### operator:feedback-status
- **목적**: 최근 검증 결과의 성공·실수 수, major 이상 실수, 반복 pattern과 이벤트 스키마 오류를 보고한다.
- **owner**: harness
- **구현**: `operators/feedback-status.py`
- **계약**: `operators/feedback-status.md`
- **영향**: 전체

### operator:review-branch
- **목적**: 어느 committed checkpoint에서나 로컬 review 스냅샷을 생성하고 이름·원격 유출·worktree
  연결을 감사하며 hook에서 직접 커밋과 원격 push를 차단한다.
- **owner**: harness
- **구현**: `operators/review-branch.py`
- **계약**: `operators/review-branch.md`
- **영향**: 전체

### operator:storage-spaces
- **목적**: 등록 저장공간·adapter·research·catalog·transformation lineage와 이식성·fallback을 감사하고
  결정적 index, 제한 조회, query plan과 catalog 단위 context를 제공한다.
- **owner**: harness
- **구현**: `operators/storage-spaces.py`
- **계약**: `operators/storage-spaces.md`
- **영향**: 전체
