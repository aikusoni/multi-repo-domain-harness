# schemas

Storage Space 구성과 Cross-Space Catalog JSON 레코드의 형식 정본이다. JSON Schema Draft 2020-12를
사용한다.

- `storage-space.schema.json`: 공간 역할·보존·손실·질의·구현 전략·fallback·이식성 계약
- `storage-registry.schema.json`: active space와 definition 경로의 등록부
- `storage-adapter-registry.schema.json`: 등록 adapter와 definition 경로의 정본
- `storage-adapter.schema.json`: 공통 write·query·trace·export·rebuild·health adapter 계약
- `catalog-entry.schema.json`: representation과 lineage를 잇는 Cross-Space Catalog 계약
- `transformation.schema.json`: 변환 방법·버전·입출력·손실·재처리 계약
- `research-catalog.schema.json`: 검증한 공개 연구·구현 reference와 채택 상태 계약

스키마와 `operator:storage-spaces`의 검사가 다르면 더 엄격한 쪽을 따르고 같은 변경에서 둘을 정합시킨다.

Storage Space Definition v2는 v1에 `implementation`과 `portability`를 필수로 추가했다. active definition은
모두 v2여야 하며 v1을 읽을 때 암묵적 기본값을 추정하지 않는다.
