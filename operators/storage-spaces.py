#!/usr/bin/env python3
"""Audit and query the harness storage-space control plane."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


UTC_FORMAT = "%Y-%m-%d %H:%M:%S UTC"
SPACE_ID = re.compile(r"^space:[a-z0-9][a-z0-9._-]*$")
CATALOG_ID = re.compile(r"^catalog:[a-z0-9][a-z0-9._-]*$")
TRANSFORMATION_ID = re.compile(r"^transformation:[a-z0-9][a-z0-9._-]*$")
ROLES = {"evidence", "record", "projection", "index", "cache"}
KINDS = {
    "evidence-space",
    "narrative-space",
    "event-space",
    "object-space",
    "relation-space",
    "field-space",
    "table-space",
    "time-series-space",
    "semantic-space",
    "residual-space",
    "working-space",
}


class FatalInputError(RuntimeError):
    pass


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


@dataclass
class Model:
    root: Path
    registry: dict[str, Any]
    definitions: dict[str, dict[str, Any]]
    definition_paths: dict[str, Path]
    catalog: dict[str, dict[str, Any]]
    catalog_paths: dict[str, Path]
    transformations: dict[str, dict[str, Any]]
    transformation_paths: dict[str, Path]
    source_paths: list[Path]
    findings: list[Finding]


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def read_json(path: Path, *, required: bool = False) -> dict[str, Any]:
    if not path.is_file():
        if required:
            raise FatalInputError(f"필수 JSON 파일 없음: {path}")
        raise FileNotFoundError(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FatalInputError(f"JSON을 읽을 수 없음: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FatalInputError(f"JSON 최상위 값은 object여야 함: {path}")
    return value


def json_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def valid_utc(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, UTC_FORMAT)
    except ValueError:
        return False
    return True


def safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or value.startswith(("/", "~")):
        return False
    if "://" in value or "\\" in value or re.match(r"^[A-Za-z]:", value):
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and ".." not in parts and "." not in parts


def safe_ref(value: Any) -> bool:
    if not isinstance(value, str) or ":" not in value or "://" in value or "\\" in value:
        return False
    project, payload = value.split(":", 1)
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", project):
        return False
    if not payload or payload.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", payload):
        return False
    return ".." not in PurePosixPath(payload).parts


def add(findings: list[Finding], code: str, message: str) -> None:
    findings.append(Finding(code, message))


def require_fields(
    record: dict[str, Any], fields: Iterable[str], path: str, findings: list[Finding], code: str
) -> None:
    missing = sorted(field for field in fields if field not in record)
    if missing:
        add(findings, code, f"{path}: 필수 필드 누락 {','.join(missing)}")


def load_model(root: Path) -> Model:
    root = root.resolve()
    registry_path = root / "storage/registry.json"
    registry = read_json(registry_path, required=True)
    findings: list[Finding] = []
    source_paths = [registry_path]
    definitions: dict[str, dict[str, Any]] = {}
    definition_paths: dict[str, Path] = {}
    active_entries = registry.get("active_spaces")

    if registry.get("schema_version") != 1:
        add(findings, "S001", "storage/registry.json: schema_version은 1이어야 함")
    if not valid_utc(registry.get("recorded_at")):
        add(findings, "S002", "storage/registry.json: recorded_at은 명시적 UTC 시각이어야 함")
    if not isinstance(active_entries, list):
        add(findings, "S003", "storage/registry.json: active_spaces는 배열이어야 함")
        active_entries = []

    seen_registry_ids: set[str] = set()
    seen_definition_refs: set[str] = set()
    for position, entry in enumerate(active_entries):
        label = f"storage/registry.json:active_spaces[{position}]"
        if not isinstance(entry, dict):
            add(findings, "S004", f"{label}: object가 아님")
            continue
        space_id = entry.get("id")
        definition_ref = entry.get("definition")
        if not isinstance(space_id, str) or not SPACE_ID.fullmatch(space_id):
            add(findings, "S005", f"{label}: 잘못된 space id")
            continue
        if space_id in seen_registry_ids:
            add(findings, "S006", f"{label}: 중복 space id {space_id}")
            continue
        seen_registry_ids.add(space_id)
        if not safe_relative_path(definition_ref) or not str(definition_ref).startswith("storage/definitions/"):
            add(findings, "S007", f"{label}: 안전하지 않은 definition 경로")
            continue
        seen_definition_refs.add(str(definition_ref))
        path = root / str(definition_ref)
        if not path.is_file():
            add(findings, "S008", f"{label}: definition 파일 없음 {definition_ref}")
            continue
        definition = read_json(path)
        source_paths.append(path)
        definitions[space_id] = definition
        definition_paths[space_id] = path

    for path in json_files(root / "storage/definitions"):
        ref = relative(root, path)
        if ref not in seen_definition_refs:
            add(findings, "S009", f"{ref}: registry에 없는 definition")

    required_definition_fields = {
        "schema_version",
        "id",
        "role",
        "kind",
        "status",
        "purpose",
        "locations",
        "accepts",
        "preserves",
        "losses",
        "query_modes",
        "write_policy",
        "consistency",
        "retention",
        "provenance",
        "rebuild",
        "cost",
        "public_safety",
        "permissions",
        "recorded_at",
    }
    for space_id, definition in definitions.items():
        path = relative(root, definition_paths[space_id])
        require_fields(definition, required_definition_fields, path, findings, "S101")
        if definition.get("schema_version") != 1:
            add(findings, "S102", f"{path}: schema_version은 1이어야 함")
        if definition.get("id") != space_id:
            add(findings, "S103", f"{path}: registry id와 definition id가 다름")
        if definition.get("status") != "active":
            add(findings, "S104", f"{path}: registry에 등록된 공간은 active여야 함")
        if definition.get("role") not in ROLES:
            add(findings, "S105", f"{path}: 알 수 없는 role {definition.get('role')}")
        if definition.get("kind") not in KINDS:
            add(findings, "S106", f"{path}: 알 수 없는 kind {definition.get('kind')}")
        for field in ("purpose", "locations", "accepts", "preserves", "losses", "query_modes"):
            value = definition.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                add(findings, "S107", f"{path}: {field}는 비어 있지 않은 문자열 배열이어야 함")
        locations = definition.get("locations", [])
        for location in locations if isinstance(locations, list) else []:
            if not safe_relative_path(location):
                add(findings, "S108", f"{path}: 안전하지 않은 location {location}")
                continue
            generated = definition.get("role") == "index" and definition.get("rebuild", {}).get("rebuildable") is True
            if not generated and not (root / location).exists():
                add(findings, "S109", f"{path}: location 없음 {location}")
        if definition.get("role") in {"projection", "index"}:
            rebuild = definition.get("rebuild")
            if not isinstance(rebuild, dict) or rebuild.get("rebuildable") is not True or not rebuild.get("sources"):
                add(findings, "S110", f"{path}: projection/index는 rebuild source를 선언해야 함")
        safety = definition.get("public_safety")
        if isinstance(safety, dict) and safety.get("classification") == "public-metadata-only":
            if safety.get("raw_content_allowed") is not False:
                add(findings, "S111", f"{path}: metadata-only 공간은 raw content를 허용할 수 없음")
        if not valid_utc(definition.get("recorded_at")):
            add(findings, "S112", f"{path}: recorded_at은 명시적 UTC 시각이어야 함")

    catalog: dict[str, dict[str, Any]] = {}
    catalog_paths: dict[str, Path] = {}
    for path in json_files(root / "storage/catalog"):
        entry = read_json(path)
        source_paths.append(path)
        label = relative(root, path)
        entry_id = entry.get("id")
        require_fields(
            entry,
            {"schema_version", "id", "type", "recorded_at", "representations", "lineage", "public_safety"},
            label,
            findings,
            "C001",
        )
        if not isinstance(entry_id, str) or not CATALOG_ID.fullmatch(entry_id):
            add(findings, "C002", f"{label}: 잘못된 catalog id")
            continue
        if entry_id in catalog:
            add(findings, "C003", f"{label}: 중복 catalog id {entry_id}")
            continue
        catalog[entry_id] = entry
        catalog_paths[entry_id] = path
        if entry.get("schema_version") != 1:
            add(findings, "C004", f"{label}: schema_version은 1이어야 함")
        if not valid_utc(entry.get("recorded_at")):
            add(findings, "C005", f"{label}: recorded_at은 명시적 UTC 시각이어야 함")
        representations = entry.get("representations")
        if not isinstance(representations, list) or not representations:
            add(findings, "C006", f"{label}: representations는 비어 있지 않아야 함")
            representations = []
        for position, representation in enumerate(representations):
            pointer = f"{label}:representations[{position}]"
            if not isinstance(representation, dict):
                add(findings, "C007", f"{pointer}: object가 아님")
                continue
            if representation.get("space") not in definitions:
                add(findings, "C008", f"{pointer}: 미등록 space {representation.get('space')}")
            elif representation.get("role") is not None:
                expected_role = definitions[representation["space"]].get("role")
                if representation.get("role") != expected_role:
                    add(findings, "C018", f"{pointer}: definition과 role이 다름")
            if not safe_ref(representation.get("ref")):
                add(findings, "C009", f"{pointer}: 공개 안전하지 않은 ref")
            start = representation.get("valid_from")
            end = representation.get("valid_until")
            if start is not None and not valid_utc(start):
                add(findings, "C010", f"{pointer}: valid_from UTC 형식 오류")
            if end is not None and not valid_utc(end):
                add(findings, "C011", f"{pointer}: valid_until UTC 형식 오류")
            if valid_utc(start) and valid_utc(end):
                if datetime.strptime(end, UTC_FORMAT) < datetime.strptime(start, UTC_FORMAT):
                    add(findings, "C012", f"{pointer}: valid_until이 valid_from보다 이름")
        lineage = entry.get("lineage")
        if not isinstance(lineage, dict) or not isinstance(lineage.get("sources"), list):
            add(findings, "C013", f"{label}: lineage.sources는 배열이어야 함")
        else:
            for position, source in enumerate(lineage["sources"]):
                pointer = f"{label}:lineage.sources[{position}]"
                if not isinstance(source, dict):
                    add(findings, "C014", f"{pointer}: object가 아님")
                    continue
                if source.get("space") not in definitions:
                    add(findings, "C015", f"{pointer}: 미등록 space {source.get('space')}")
                if not safe_ref(source.get("ref")):
                    add(findings, "C016", f"{pointer}: 공개 안전하지 않은 ref")
        safety = entry.get("public_safety")
        if not isinstance(safety, dict) or safety.get("reviewed") is not True:
            add(findings, "C019", f"{label}: public_safety.reviewed가 true가 아님")

    transformations: dict[str, dict[str, Any]] = {}
    transformation_paths: dict[str, Path] = {}
    for path in json_files(root / "storage/transformations"):
        transformation = read_json(path)
        source_paths.append(path)
        label = relative(root, path)
        transformation_id = transformation.get("id")
        require_fields(
            transformation,
            {
                "schema_version",
                "id",
                "version",
                "method",
                "inputs",
                "outputs",
                "preserves",
                "losses",
                "reversible",
                "implementation",
                "recorded_at",
            },
            label,
            findings,
            "T001",
        )
        if not isinstance(transformation_id, str) or not TRANSFORMATION_ID.fullmatch(transformation_id):
            add(findings, "T002", f"{label}: 잘못된 transformation id")
            continue
        if transformation_id in transformations:
            add(findings, "T003", f"{label}: 중복 transformation id {transformation_id}")
            continue
        transformations[transformation_id] = transformation
        transformation_paths[transformation_id] = path
        if transformation.get("schema_version") != 1:
            add(findings, "T004", f"{label}: schema_version은 1이어야 함")
        if not isinstance(transformation.get("version"), int) or transformation["version"] < 1:
            add(findings, "T005", f"{label}: version은 1 이상의 정수여야 함")
        if not valid_utc(transformation.get("recorded_at")):
            add(findings, "T006", f"{label}: recorded_at은 명시적 UTC 시각이어야 함")
        implementation = transformation.get("implementation")
        if not safe_ref(implementation) and not safe_relative_path(implementation):
            add(findings, "T011", f"{label}: 공개 안전하지 않은 implementation")
        for field in ("inputs", "outputs"):
            endpoints = transformation.get(field)
            if not isinstance(endpoints, list) or not endpoints:
                add(findings, "T007", f"{label}: {field}는 비어 있지 않아야 함")
                continue
            for position, endpoint in enumerate(endpoints):
                pointer = f"{label}:{field}[{position}]"
                if not isinstance(endpoint, dict):
                    add(findings, "T008", f"{pointer}: object가 아님")
                    continue
                if endpoint.get("space") not in definitions:
                    add(findings, "T009", f"{pointer}: 미등록 space {endpoint.get('space')}")
                if not safe_ref(endpoint.get("ref_pattern")):
                    add(findings, "T010", f"{pointer}: 공개 안전하지 않은 ref_pattern")

    for entry_id, entry in catalog.items():
        transformation_id = entry.get("lineage", {}).get("transformation")
        if transformation_id is not None and transformation_id not in transformations:
            add(
                findings,
                "C017",
                f"{relative(root, catalog_paths[entry_id])}: transformation 없음 {transformation_id}",
            )

    return Model(
        root=root,
        registry=registry,
        definitions=definitions,
        definition_paths=definition_paths,
        catalog=catalog,
        catalog_paths=catalog_paths,
        transformations=transformations,
        transformation_paths=transformation_paths,
        source_paths=sorted(set(source_paths)),
        findings=sorted(findings, key=lambda item: (item.code, item.message)),
    )


def print_audit(model: Model) -> None:
    if model.findings:
        print(f"ATTENTION storage-spaces: findings={len(model.findings)}")
        for finding in model.findings:
            print(f"{finding.code} {finding.message}")
        return
    print(
        "OK storage-spaces: "
        f"active_spaces={len(model.definitions)} "
        f"catalog_entries={len(model.catalog)} "
        f"transformations={len(model.transformations)}"
    )


def source_digest(model: Model) -> str:
    digest = hashlib.sha256()
    for path in model.source_paths:
        digest.update(relative(model.root, path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_index(model: Model) -> int:
    if model.findings:
        print_audit(model)
        print("REFUSED storage-index: 감사 발견 사항을 먼저 해결해야 함", file=sys.stderr)
        return 1
    output = {
        "schema_version": 1,
        "source_digest": f"sha256:{source_digest(model)}",
        "spaces": [
            {
                "id": space_id,
                "role": definition["role"],
                "kind": definition["kind"],
                "purpose": definition["purpose"],
                "locations": definition["locations"],
                "query_modes": definition["query_modes"],
                "losses": definition["losses"],
                "rebuildable": definition["rebuild"]["rebuildable"],
            }
            for space_id, definition in sorted(model.definitions.items())
        ],
        "catalog_entries": [
            {
                "id": entry_id,
                "type": entry["type"],
                "recorded_at": entry["recorded_at"],
                "spaces": sorted({item["space"] for item in entry["representations"]}),
                "transformation": entry["lineage"].get("transformation"),
            }
            for entry_id, entry in sorted(model.catalog.items())
        ],
        "transformations": [
            {
                "id": transformation_id,
                "version": transformation["version"],
                "input_spaces": sorted({item["space"] for item in transformation["inputs"]}),
                "output_spaces": sorted({item["space"] for item in transformation["outputs"]}),
                "losses": transformation["losses"],
                "reversible": transformation["reversible"],
            }
            for transformation_id, transformation in sorted(model.transformations.items())
        ],
    }
    path = model.root / "indexes/storage-catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    print(
        "BUILT storage-index: "
        f"path={relative(model.root, path)} "
        f"spaces={len(model.definitions)} catalog_entries={len(model.catalog)}"
    )
    return 0


def assert_clean(model: Model) -> bool:
    if not model.findings:
        return True
    print_audit(model)
    return False


def query(model: Model, args: argparse.Namespace) -> int:
    if not assert_clean(model):
        return 1
    records: list[dict[str, Any]] = []
    for space_id, definition in sorted(model.definitions.items()):
        records.append({"record_type": "space", **definition})
    for entry_id, entry in sorted(model.catalog.items()):
        records.append({"record_type": "catalog", **entry})
    for transformation_id, transformation in sorted(model.transformations.items()):
        records.append({"record_type": "transformation", **transformation})

    def matches(record: dict[str, Any]) -> bool:
        if args.id and record.get("id") != args.id:
            return False
        if args.role and record.get("role") != args.role:
            return False
        if args.kind and record.get("kind") != args.kind:
            return False
        if args.space:
            spaces = {record.get("id")} if record.get("record_type") == "space" else set()
            for key in ("representations", "inputs", "outputs"):
                for item in record.get(key, []):
                    if isinstance(item, dict):
                        spaces.add(item.get("space"))
            for item in record.get("lineage", {}).get("sources", []):
                if isinstance(item, dict):
                    spaces.add(item.get("space"))
            if args.space not in spaces:
                return False
        if args.text and args.text.casefold() not in json.dumps(record, ensure_ascii=False, sort_keys=True).casefold():
            return False
        return True

    selected = [record for record in records if matches(record)][: args.limit]
    print(json.dumps({"count": len(selected), "results": selected}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def plan(model: Model, args: argparse.Namespace) -> int:
    if not assert_clean(model):
        return 1
    requested = list(dict.fromkeys(args.mode))
    candidates: list[dict[str, Any]] = []
    for space_id, definition in model.definitions.items():
        supported = set(definition["query_modes"])
        matched = [mode for mode in requested if mode in supported]
        if not matched:
            continue
        candidates.append(
            {
                "space": space_id,
                "role": definition["role"],
                "kind": definition["kind"],
                "matched_modes": matched,
                "missing_modes": [mode for mode in requested if mode not in supported],
                "locations": definition["locations"],
                "losses": definition["losses"],
            }
        )
    candidates.sort(key=lambda item: (-len(item["matched_modes"]), item["space"]))
    output = {
        "requested_modes": requested,
        "candidate_count": min(len(candidates), args.limit),
        "candidates": candidates[: args.limit],
        "unserved_modes": [
            mode for mode in requested if not any(mode in candidate["matched_modes"] for candidate in candidates)
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def context(model: Model, args: argparse.Namespace) -> int:
    if not assert_clean(model):
        return 1
    entry = model.catalog.get(args.catalog_entry_id)
    if entry is None:
        print(f"catalog entry 없음: {args.catalog_entry_id}", file=sys.stderr)
        return 1
    representations = entry["representations"]
    selected = representations[: args.limit]
    lineage_sources = entry["lineage"].get("sources", [])
    selected_sources = lineage_sources[: args.limit]
    used_space_ids = sorted(
        {item["space"] for item in selected}
        | {item["space"] for item in selected_sources}
    )
    transformation_id = entry["lineage"].get("transformation")
    output = {
        "catalog_entry": entry["id"],
        "type": entry["type"],
        "recorded_at": entry["recorded_at"],
        "representations": selected,
        "lineage": {
            "sources": selected_sources,
            "transformation": transformation_id,
        },
        "spaces": [
            {
                "id": space_id,
                "role": model.definitions[space_id]["role"],
                "kind": model.definitions[space_id]["kind"],
                "losses": model.definitions[space_id]["losses"],
            }
            for space_id in used_space_ids
        ],
        "transformation": model.transformations.get(transformation_id) if transformation_id else None,
        "truncated": len(representations) > len(selected),
        "omitted_representations": len(representations) - len(selected),
        "omitted_lineage_sources": len(lineage_sources) - len(selected_sources),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="하네스 루트. 기본값은 이 operator가 속한 저장소다.",
    )
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("audit", help="registry, definition, catalog와 transformation을 감사한다.")
    commands.add_parser("build-index", help="감사 후 결정적 검색 index를 생성한다.")

    query_parser = commands.add_parser("query", help="control-plane 레코드를 제한 조회한다.")
    query_parser.add_argument("--id")
    query_parser.add_argument("--space")
    query_parser.add_argument("--role", choices=sorted(ROLES))
    query_parser.add_argument("--kind", choices=sorted(KINDS))
    query_parser.add_argument("--text")
    query_parser.add_argument("--limit", type=int, default=20)

    plan_parser = commands.add_parser("plan", help="query mode에 맞는 active space를 계획한다.")
    plan_parser.add_argument("--mode", action="append", required=True)
    plan_parser.add_argument("--limit", type=int, default=20)

    context_parser = commands.add_parser("context", help="한 catalog entry의 제한 문맥을 조립한다.")
    context_parser.add_argument("catalog_entry_id")
    context_parser.add_argument("--limit", type=int, default=20)
    return result


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "limit", 1) < 1:
        print("--limit은 1 이상이어야 함", file=sys.stderr)
        return 2
    try:
        model = load_model(args.root)
    except FatalInputError as exc:
        print(f"ERROR storage-spaces: {exc}", file=sys.stderr)
        return 2
    if args.command == "audit":
        print_audit(model)
        return 0
    if args.command == "build-index":
        return build_index(model)
    if args.command == "query":
        return query(model, args)
    if args.command == "plan":
        return plan(model, args)
    if args.command == "context":
        return context(model, args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
