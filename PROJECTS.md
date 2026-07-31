# 프로젝트 식별 등록부와 Project Profile 색인

하네스에 참여하는 저장소와 횡단 역할을 등록한다. 각 항목은 프로젝트의 짧은 자기소개인
**Project Profile(프로젝트 프로필)** 색인이다. 상세 프로필은 `projects/<project-id>.md`, 프로젝트 간
관계는 `docs/project-map.md`에서 관리한다.

## 작성 형식

```markdown
### <project-id>
- **종류**: repository | role
- **책임**: 이 프로젝트가 소유하는 도메인 또는 기능
- **소스 오브 트루스**: 저장소 내부 문서나 경로
- **관련 도메인**: domain-a, domain-b
- **상세**: projects/<project-id>.md
```

프로젝트 식별자는 프로젝트가 요청의 `target`/`from`이나 변경 피드의 `영향`에 등장할 때 동일하게
사용한다. 영문·숫자·점·밑줄·하이픈만 사용하는 것을 권장한다.

실행 자동화는 프로젝트로 중복 등록하지 않고 `OPERATORS.md`에 등록한다. operator를 실행하거나 수정하는
에이전트는 해당 operator의 `owner` 프로젝트를 자기 정체성으로 사용한다.

여러 프로젝트가 함께 달성할 목표는 프로젝트 프로필에 섞지 않고 `INITIATIVES.md`와 `initiatives/`에
등록한다. 프로젝트 프로필은 “누구인가”, initiative는 “왜 함께 일하는가”의 정본이다.

## 등록 프로젝트

### harness
- **종류**: role
- **책임**: 여러 프로젝트·도메인·operator의 공통 작업 규칙과 교차 프로젝트 상태를 관리한다.
- **소스 오브 트루스**: `INDEX.md`
- **관련 도메인**: 전체
- **상세**: `projects/harness.md`
