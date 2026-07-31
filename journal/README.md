# journal

세션별 작업 로그를 append-only로 기록한다.

- 파일명: UTC 날짜 기준 `YYYY-MM-DD-<short-topic>.md`
- 날짜와 시각: `YYYY-MM-DD HH:MM:SS UTC` 형식으로 UTC를 반드시 명시
- 기존 내용을 고치지 않고 후속 섹션이나 정정을 추가
- 검증하지 않은 내용은 `[미검증]` 표시
- 사람의 결정·리뷰나 프로젝트 간 합의를 기다리는 안건은 journal이 아니라 request/proposal 본문과
  `AGENDA.md`에 기록
- 오래되어 현행 판단에 필요하지 않은 기록은 `journal/archive/YYYY-MM/`로 이동하며 기본 스캔에서 제외

```markdown
# YYYY-MM-DD topic

## YYYY-MM-DD HH:MM:SS UTC · 컨텍스트

## YYYY-MM-DD HH:MM:SS UTC · 결정과 발견

## YYYY-MM-DD HH:MM:SS UTC · 미해결
```
