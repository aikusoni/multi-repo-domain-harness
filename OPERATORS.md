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

<!-- 아래에 operator를 추가한다. -->
