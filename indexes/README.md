# indexes

등록된 Storage Space 정의와 Cross-Space Catalog에서 재생성 가능한 검색 index를 둔다. index는 정본이
아니며 직접 수정하지 않는다.

초기 index는 `./operators/storage-spaces.py build-index`가 만드는 `storage-catalog.json` 하나다. 공간
정의, adapter, research reference, catalog entry와 transformation의 검색용 요약만 담고 원본 근거 본문은
복제하지 않는다. research source URL은 index에 복제하지 않는다.
