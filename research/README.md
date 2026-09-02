# research references

Storage Space와 adapter 설계·선정에 참고한 공개 연구와 구현체를 검증 가능한 reference로 관리한다.
reference 등록은 도입 승인이 아니다.

- 정본: `research/catalog.json`
- 형식: `schemas/research-catalog.schema.json`
- 기본 채택 상태: `reference-only`
- 허용 source: 공개 원문을 가리키는 HTTPS URL

## 주제

필요할 때 dataspaces, polystores, blackboard systems, cognitive memory, agent memory, provenance,
information compression, forecasting, planning 같은 주제로 찾는다. 별도 해설이 필요해질 때만 하위 문서를
만들고 catalog entry에서 연결한다.

에이전트 지침 개선에는 online harness learning, execution reflection, skill compilation, feedback
grounding과 bounded context selection 연구도 참고할 수 있다.

## 운영 경계

- 제목·지원 개념·가능한 용도는 공개 원문에서 확인한 범위만 기록한다.
- 원문 본문, 코드와 데이터를 복사하지 않는다.
- 후보를 실제 평가할 때는 license, 유지보수 상태, 데이터 형식, query, lineage, export, 비용과 fallback을
  다시 검증한다.
- `reference-only` 항목을 active adapter나 저장공간의 정본으로 취급하지 않는다.
- 채택·기각 결정은 candidate 상태, 근거와 필요하면 decision/ADR에 남긴다.
