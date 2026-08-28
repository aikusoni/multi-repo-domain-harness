# Public safety policy

이 하네스는 공개 저장소에 올라갈 수 있다. Storage Space를 추가하거나 catalog·index·view를 생성해도
`INDEX.md`의 공개 위험 정보 검토를 우회하지 않는다.

- 제품 코드, 원시 로그·메트릭, 문서·이미지 원본, 실제 데이터 샘플을 복사하지 않는다.
- 로컬 절대경로, URL, 계정, 인증정보, 내부 호스트·IP·포트와 비공개 시스템 구조를 기록하지 않는다.
- `research/catalog.json`만 검증한 공개 원문의 HTTPS URL을 허용한다. 사설 주소·인증정보·구현 endpoint는
  허용하지 않으며 생성 index에는 URL을 복제하지 않는다.
- source와 representation은 `<project-id>:<relative-path-or-opaque-id>` 형식의 안전한 식별자를 사용한다.
- 공개 가능 여부가 불확실한 정보는 space에 넣지 않고 사용자 확인을 먼저 받는다.
- index와 view도 새 공개 표면이다. 생성 결과를 커밋하기 전에 정본 레코드와 별도로 다시 검사한다.
