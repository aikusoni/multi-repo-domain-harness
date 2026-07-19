# changed

특정 주체에 직접 일을 요청하지 않지만 다른 프로젝트나 operator에 영향을 줄 수 있는 변경과 그 확인
결과를 추적한다.

## 변경 기록

당일 `status-YYYY-MM-DD.md`에 append한다.

```markdown
## [c-xxxxxxxx] HH:MM · from: <project>
- 변경: 한 줄 요약
- 위치: 문서, 브랜치 또는 커밋
- 영향: project-a, project-b, operator:operator-id 또는 전체
- 관련: request, issue, decision 링크
```

## 주체별 확인

각 프로젝트는 `looked-<project>.md`, operator는 필요할 때 `looked-operator-<id>.md` 하나만 소유한다.

```markdown
# <project> 변경 확인
<!-- cursor: BEGIN -->

- [c-xxxxxxxx] YYYY-MM-DD 확인 · 대응: 무관 — 사유
- [c-xxxxxxxx] YYYY-MM-DD 확인 · 대응: 완료 — 위치 또는 커밋
- [c-xxxxxxxx] YYYY-MM-DD 확인 · 대응: 요청 생성 — requests/...
- [c-xxxxxxxx] YYYY-MM-DD 확인 · 대응: 후속 예정 — 무엇을 언제
```

커서는 전체 변경 피드에서 마지막으로 확인한 위치를 뜻하며 관련 항목만의 위치가 아니다.
