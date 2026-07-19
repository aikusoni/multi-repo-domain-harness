# issues

`ISSUES.md`가 활성 상태의 현재 스냅샷이라면 이 폴더는 상태 전환의 날짜별 이력이다. 이벤트는 KST 기준
당일 `status-YYYY-MM-DD.md`에만 append하며 과거 날짜 파일에 뒤늦게 추가하지 않는다.

```markdown
## [i-xxxxxxxx] HH:MM · from: <project>
- 이슈: requests/... 또는 proposals/...
- 상태: <before 또는 created> -> <after>
- 레벨: critical | major | minor
- 관련 프로젝트: project-a, project-b 또는 전체
- 요약: 현재 남은 일
- 위치: 관련 파일 또는 커밋
```

ID는 이 하네스 안에서 중복되지 않는 `i-` 접두사의 8자리 식별자를 사용한다.
