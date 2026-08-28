# schemas

Storage Space 구성과 Cross-Space Catalog JSON 레코드의 형식 정본이다. JSON Schema Draft 2020-12를
사용한다.

- `storage-space.schema.json`: 공간 역할·보존·손실·질의·쓰기·재구성 계약
- `storage-registry.schema.json`: active space와 definition 경로의 등록부
- `catalog-entry.schema.json`: representation과 lineage를 잇는 Cross-Space Catalog 계약
- `transformation.schema.json`: 변환 방법·버전·입출력·손실·재처리 계약

스키마와 `operator:storage-spaces`의 검사가 다르면 더 엄격한 쪽을 따르고 같은 변경에서 둘을 정합시킨다.
