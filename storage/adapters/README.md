# storage adapters

외부 엔진·서비스와 하네스 Storage Space 사이의 교체 가능한 경계를 둔다. `registry.json`에 등록된 adapter만
active space definition이 사용할 수 있다.

현재 등록 adapter는 없다. 기존 repository 파일 공간은 `strategy: native`이며 외부 시스템 연결로
간주하지 않는다. 실제 질의·규모·성능 요구가 확인되기 전에는 adapter를 미리 만들지 않는다.

## 공통 동작

모든 adapter definition은 다음 동작의 지원 수준과 제한을 선언한다.

- `write`: 표준 record를 저장공간 표현으로 기록
- `query`: 선언한 query mode 수행
- `trace`: 결과에서 source·transformation lineage로 복귀
- `export`: 공개·이식 가능한 형식으로 반출
- `rebuild`: source에서 projection·index 재생성
- `health`: 가용성, 버전과 성능 저하 상태 확인

`unsupported` 동작은 숨기지 않는다. active space의 필수 query mode를 제공하지 못하면 다른 adapter와
조합하거나 definition의 fallback·degraded query mode에 명시한다.

## 등록 절차

1. `docs/storage-adapters.md`의 capability와 채택 게이트를 평가한다.
2. `schemas/storage-adapter.schema.json`에 맞는 definition을 이 디렉터리에 둔다.
3. license, public safety, export와 장애 시 data access를 확인한다.
4. `registry.json`에 등록하고 사용하는 space definition의 implementation·fallback을 연결한다.
5. `operator:storage-spaces audit`과 adapter별 fixture를 통과시킨다.

adapter 등록은 외부 시스템을 evidence나 record의 정본으로 자동 승격하지 않는다. source ownership과
lineage는 해당 Storage Space와 Cross-Space Catalog 계약이 계속 소유한다.
