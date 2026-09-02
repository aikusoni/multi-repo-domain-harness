---
task_id: t-6e034557
project: harness
operator:
opened: 2026-09-02 06:15:21 UTC
initiative:
related_issue:
related_request:
---

# 하네스 primary checkout 전용 정책

## 목표

하네스 저장소의 가변 작업은 primary checkout에서만 허용하고 linked Git worktree의 생성·사용·커밋·push를
강한 규칙과 기계 판정으로 차단한다. 다른 프로젝트의 worktree 정책은 바꾸지 않는다.

## 완료 기준

- [x] primary checkout과 linked worktree를 Git metadata로 구분하는 계약을 정의한다.
- [x] 하네스 linked worktree에서 파일 변경·생성·build·stage·commit·push·merge를 금지한다.
- [x] 기존 linked worktree를 자동 삭제하지 않고 cutover와 안전한 정리 경계를 정의한다.
- [x] INDEX·bootstrap·변경 승격·operator·프로젝트 프로필을 정합하게 연결한다.
- [x] primary 통과, linked 차단과 잔존 linked audit fixture를 검증한다.
- [x] 전체 감사와 공개 위험 검토를 통과한다.

## 착수 예측

- 예상 관측: 현재 checkout은 Git dir와 common dir가 같아 guard를 통과하고, fixture의 linked worktree는
  non-zero로 차단된다. 현재 저장소 audit은 기존 linked worktree 1개를 경고하되 경로를 출력하지 않는다.
- 가장 가능성 높은 실패 지점: Git 버전별 path 정규화 차이, 기존 linked worktree 존재를 현재 작업 자체의
  차단으로 잘못 해석하는 계약.
- 반증과 확인: primary·linked fixture의 exit code와 출력, 현재 `git worktree list --porcelain` 기반 count,
  기존 작업트리·브랜치의 불변 상태를 비교한다.

## 진행 기록

- 2026-09-02 06:15:21 UTC - 현행 승격 계약과 현재 Git 구조를 확인하고 작업을 시작했다.
- 2026-09-02 06:32:54 UTC - primary·linked·잔존 linked·하위 디렉터리·non-Git·`.git`·환경변수 오염·
  dirty 상태 보존·경로 비노출 fixture를 통과했다.
- 2026-09-02 06:32:54 UTC - 하네스·review·storage audit와 관련 전체 fixture, diff 검사, 공개 위험 검색을
  통과했고 독립 read-only 최종 리뷰가 PASS를 반환했다.

## 완료 결과

- 규칙 r0017과 D-010이 하네스만 primary checkout 전용으로 만들고 참여 프로젝트의 worktree 계약은
  유지한다.
- `operator:harness-worktree-guard check`는 linked 현재 위치를 non-zero로 차단하고, primary에 남은
  cutover 이전 linked worktree는 경로 없이 `ATTENTION`으로 보고한다.
- 기존 linked worktree는 새 작업에 사용하지 않으며 소유·미커밋·보존 상태를 확인한 명시적 정리 전에는
  자동으로 제거하지 않는다.
