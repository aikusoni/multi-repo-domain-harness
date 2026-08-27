# 리뷰 체크포인트와 작업 브랜치 수명주기

**VALIDITY:** ACTIVE

## 2026-08-27 05:57:16 UTC · 공유 규칙 수정 경계 확인

**SESSION-COMM:** 2026-08-27 05:57:16 UTC · observe · peer: none-in-observable-scope · reason: INDEX와 승격 canon 수정 전 소유 확인

현재 실행 문맥의 세션 등록부에는 이 세션만 보였다. 관측 범위가 다른 작업·환경·사람의 수동 편집까지
포괄하지 않으므로 다른 세션이 없다는 근거로 사용하지 않았고, clean Git 상태와 명시적 stage 경계를 함께
적용했다.

## 2026-08-27 05:58:29 UTC · 결정과 발견

- 승격은 임시 작업, 선택적 PR, feature, release·정본과 배포로 이동하는 경로다.
- review는 이 경로에서 한 번 통과하는 단계가 아니라, 사람의 판단이 필요한 어느 committed
  checkpoint에서나 별도로 생성하는 로컬 불변 스냅샷이다.
- 이동 가능한 통합·검증·release ref를 리뷰 대상으로 checkout하면 ref가 worktree에 잠길 수 있다.
  리뷰어는 정확한 review commit을 detached 상태로 열고, checkpoint가 바뀌면 새 review를 사용한다.
- 임시 작업 브랜치는 worktree와 수명을 같이하되, 삭제 전 결과 commit이 지속 가능한 ref에서 도달
  가능한지 확인한다. 로컬 review만 남은 상태는 장기 보존으로 간주하지 않는다.
- `operator:review-branch`는 명시한 source ref를 checkout 없이 스냅샷하고, review ref의 worktree 연결을
  `R003`으로 탐지한다.

## 2026-08-27 06:01:54 UTC · 검증

- 기본 clean HEAD와 명시한 과거 checkpoint에서 review 생성 성공
- 잘못된 source ref, dirty HEAD, review 직접 commit·push 거부 확인
- 잘못된 이름, 원격 추적 review와 worktree 연결 review의 `R001`, `R002`, `R003` 탐지 확인

## 2026-08-27 06:01:54 UTC · 미해결

없음.
