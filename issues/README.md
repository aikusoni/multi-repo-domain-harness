# issues

`ISSUES.md`가 활성 상태의 현재 스냅샷이라면 이 폴더는 상태 전환의 날짜별 이력이다. 이벤트는 UTC 날짜의
당일 `status-YYYY-MM-DD.md`에만 append하며 과거 날짜 파일에 뒤늦게 추가하지 않는다.

활성 표의 `요약`은 재작성형 현재 상태이고 아래 이벤트의 `요약`은 누적형 당시 사실이다. 상태가 바뀌면
활성 표 문장을 다시 쓰되 같은 변경에서 새 이벤트를 append한다. 활성 표에 정정을 계속 덧붙이면 낡은
문장이 먼저 읽히므로 왕복 이력은 이벤트와 요청·제안 본문에 둔다.

```markdown
## [i-xxxxxxxx] YYYY-MM-DD HH:MM:SS UTC · from: <project>
- 이슈: requests/... 또는 proposals/...
- 상태: <before 또는 created> -> <after>
- 레벨: critical | major | minor
- 관련 주체: project-a, project-b, operator:operator-id 또는 전체
- 관련 initiative: initiative:initiative-id (있으면)
- 요약: 이 전환 시점의 변화와 남은 일
- 위치: 관련 파일 또는 커밋
```

ID는 이 하네스 안에서 중복되지 않는 `i-` 접두사의 8자리 식별자를 사용한다.
