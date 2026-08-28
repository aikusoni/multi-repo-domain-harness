#!/usr/bin/env python3
"""Audit and query the harness storage-space control plane."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse


UTC_FORMAT = "%Y-%m-%d %H:%M:%S UTC"
SPACE_ID = re.compile(r"^space:[a-z0-9][a-z0-9._-]*$")
CATALOG_ID = re.compile(r"^catalog:[a-z0-9][a-z0-9._-]*$")
TRANSFORMATION_ID = re.compile(r"^transformation:[a-z0-9][a-z0-9._-]*$")
ADAPTER_ID = re.compile(r"^adapter:[a-z0-9][a-z0-9._-]*$")
RESEARCH_ID = re.compile(r"^research:[a-z0-9][a-z0-9._-]*$")
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
    adapter_registry: dict[str, Any]
    adapters: dict[str, dict[str, Any]]
    adapter_paths: dict[str, Path]
    research_catalog: dict[str, Any]
    research: dict[str, dict[str, Any]]
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


def public_https_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    host = parsed.hostname.casefold()
    if host == "localhost" or host.endswith((".local", ".internal")):
        return False
    try:
        if ipaddress.ip_address(host).is_private:
            return False
    except ValueError:
        pass
    return True


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

    adapter_registry_path = root / "storage/adapters/registry.json"
    adapter_registry = read_json(adapter_registry_path, required=True)
    source_paths.append(adapter_registry_path)
    adapters: dict[str, dict[str, Any]] = {}
    adapter_paths: dict[str, Path] = {}
    adapter_entries = adapter_registry.get("adapters")
    if adapter_registry.get("schema_version") != 1:
        add(findings, "D001", "storage/adapters/registry.json: schema_version은 1이어야 함")
    if not valid_utc(adapter_registry.get("recorded_at")):
        add(findings, "D002", "storage/adapters/registry.json: recorded_at은 명시적 UTC 시각이어야 함")
    if not isinstance(adapter_entries, list):
        add(findings, "D003", "storage/adapters/registry.json: adapters는 배열이어야 함")
        adapter_entries = []

    seen_adapter_ids: set[str] = set()
    seen_adapter_refs: set[str] = set()
    for position, entry in enumerate(adapter_entries):
        label = f"storage/adapters/registry.json:adapters[{position}]"
        if not isinstance(entry, dict):
            add(findings, "D004", f"{label}: object가 아님")
            continue
        adapter_id = entry.get("id")
        definition_ref = entry.get("definition")
        if not isinstance(adapter_id, str) or not ADAPTER_ID.fullmatch(adapter_id):
            add(findings, "D005", f"{label}: 잘못된 adapter id")
            continue
        if adapter_id in seen_adapter_ids:
            add(findings, "D006", f"{label}: 중복 adapter id {adapter_id}")
            continue
        seen_adapter_ids.add(adapter_id)
        if not safe_relative_path(definition_ref) or not str(definition_ref).startswith("storage/adapters/"):
            add(findings, "D007", f"{label}: 안전하지 않은 definition 경로")
            continue
        seen_adapter_refs.add(str(definition_ref))
        path = root / str(definition_ref)
        if not path.is_file():
            add(findings, "D008", f"{label}: definition 파일 없음 {definition_ref}")
            continue
        adapter = read_json(path)
        source_paths.append(path)
        adapters[adapter_id] = adapter
        adapter_paths[adapter_id] = path

    for path in json_files(root / "storage/adapters"):
        if path == adapter_registry_path:
            continue
        ref = relative(root, path)
        if ref not in seen_adapter_refs:
            add(findings, "D009", f"{ref}: registry에 없는 adapter definition")

    required_adapter_fields = {
        "schema_version",
        "id",
        "type",
        "status",
        "implementation",
        "operations",
        "query_modes",
        "input_formats",
        "output_formats",
        "consistency",
        "license_status",
        "public_safety",
        "recorded_at",
    }
    for adapter_id, adapter in adapters.items():
        path = relative(root, adapter_paths[adapter_id])
        require_fields(adapter, required_adapter_fields, path, findings, "D101")
        if adapter.get("schema_version") != 1:
            add(findings, "D102", f"{path}: schema_version은 1이어야 함")
        if adapter.get("id") != adapter_id:
            add(findings, "D103", f"{path}: registry id와 adapter id가 다름")
        if adapter.get("status") != "active":
            add(findings, "D104", f"{path}: registry에 등록된 adapter는 active여야 함")
        if adapter.get("type") not in {"embedded", "engine", "external-service", "delegated"}:
            add(findings, "D114", f"{path}: 알 수 없는 adapter type")
        implementation = adapter.get("implementation")
        if not safe_ref(implementation) and not safe_relative_path(implementation):
            add(findings, "D105", f"{path}: 공개 안전하지 않은 implementation")
        operations = adapter.get("operations")
        if not isinstance(operations, dict):
            add(findings, "D106", f"{path}: operations는 object여야 함")
        else:
            for operation in ("write", "query", "trace", "export", "rebuild", "health"):
                contract = operations.get(operation)
                if not isinstance(contract, dict):
                    add(findings, "D107", f"{path}: operation 누락 {operation}")
                    continue
                if contract.get("support") not in {"supported", "degraded", "unsupported"}:
                    add(findings, "D108", f"{path}: {operation}.support 값 오류")
                if not isinstance(contract.get("notes"), str) or not contract.get("notes"):
                    add(findings, "D109", f"{path}: {operation}.notes 누락")
        for field in ("input_formats", "output_formats"):
            value = adapter.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                add(findings, "D110", f"{path}: {field}는 비어 있지 않은 문자열 배열이어야 함")
        query_modes = adapter.get("query_modes")
        if not isinstance(query_modes, list) or not all(isinstance(item, str) and item for item in query_modes):
            add(findings, "D115", f"{path}: query_modes는 문자열 배열이어야 함")
        if adapter.get("consistency") not in {"strong", "eventual", "snapshot", "not-applicable"}:
            add(findings, "D116", f"{path}: 알 수 없는 consistency")
        if adapter.get("license_status") not in {"compatible", "not-applicable"}:
            add(findings, "D111", f"{path}: active adapter의 license 검토가 완료되지 않음")
        safety = adapter.get("public_safety")
        if not isinstance(safety, dict):
            add(findings, "D117", f"{path}: public_safety는 object여야 함")
        elif safety.get("classification") == "public-metadata-only":
            if safety.get("raw_content_allowed") is not False:
                add(findings, "D112", f"{path}: metadata-only adapter는 raw content를 허용할 수 없음")
        if not valid_utc(adapter.get("recorded_at")):
            add(findings, "D113", f"{path}: recorded_at은 명시적 UTC 시각이어야 함")

    research_path = root / "research/catalog.json"
    research_catalog = read_json(research_path, required=True)
    source_paths.append(research_path)
    research: dict[str, dict[str, Any]] = {}
    research_entries = research_catalog.get("entries")
    if research_catalog.get("schema_version") != 1:
        add(findings, "R001", "research/catalog.json: schema_version은 1이어야 함")
    if not valid_utc(research_catalog.get("recorded_at")):
        add(findings, "R002", "research/catalog.json: recorded_at은 명시적 UTC 시각이어야 함")
    if not isinstance(research_entries, list):
        add(findings, "R003", "research/catalog.json: entries는 배열이어야 함")
        research_entries = []
    for position, entry in enumerate(research_entries):
        label = f"research/catalog.json:entries[{position}]"
        if not isinstance(entry, dict):
            add(findings, "R004", f"{label}: object가 아님")
            continue
        research_id = entry.get("id")
        if not isinstance(research_id, str) or not RESEARCH_ID.fullmatch(research_id):
            add(findings, "R005", f"{label}: 잘못된 research id")
            continue
        if research_id in research:
            add(findings, "R006", f"{label}: 중복 research id {research_id}")
            continue
        research[research_id] = entry
        require_fields(
            entry,
            {
                "id",
                "type",
                "title",
                "source",
                "supports",
                "relevant_spaces",
                "possible_use",
                "adoption_status",
                "license_review",
            },
            label,
            findings,
            "R007",
        )
        source = entry.get("source")
        if not isinstance(source, dict) or not public_https_url(source.get("url")):
            add(findings, "R008", f"{label}: 공개 HTTPS source가 아님")
        elif not valid_utc(source.get("verified_at")):
            add(findings, "R009", f"{label}: verified_at은 명시적 UTC 시각이어야 함")
        for field in ("supports", "relevant_spaces", "possible_use"):
            value = entry.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                add(findings, "R010", f"{label}: {field}는 비어 있지 않은 문자열 배열이어야 함")
        if entry.get("type") not in {"paper", "architecture", "research-implementation", "documentation"}:
            add(findings, "R012", f"{label}: 알 수 없는 reference type")
        if entry.get("adoption_status") not in {"reference-only", "evaluating", "adopted", "rejected"}:
            add(findings, "R013", f"{label}: 알 수 없는 adoption_status")
        if entry.get("license_review") not in {
            "not-required-reference-only",
            "not-reviewed",
            "compatible",
            "incompatible",
        }:
            add(findings, "R014", f"{label}: 알 수 없는 license_review")
        if entry.get("adoption_status") == "adopted" and entry.get("license_review") != "compatible":
            add(findings, "R011", f"{label}: adopted reference의 license가 compatible이 아님")

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
        "implementation",
        "portability",
        "recorded_at",
    }
    for space_id, definition in definitions.items():
        path = relative(root, definition_paths[space_id])
        require_fields(definition, required_definition_fields, path, findings, "S101")
        if definition.get("schema_version") != 2:
            add(findings, "S102", f"{path}: schema_version은 2여야 함")
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
        implementation = definition.get("implementation")
        if not isinstance(implementation, dict):
            add(findings, "S113", f"{path}: implementation은 object여야 함")
        else:
            if implementation.get("selection_policy") != "reuse-first":
                add(findings, "S114", f"{path}: selection_policy는 reuse-first여야 함")
            strategy = implementation.get("strategy")
            if strategy not in {"native", "adapter", "hybrid", "custom-minimal"}:
                add(findings, "S115", f"{path}: 알 수 없는 implementation strategy")
            adapter_ref = implementation.get("adapter")
            if strategy in {"adapter", "hybrid"} and adapter_ref is None:
                add(findings, "S116", f"{path}: adapter/hybrid strategy는 adapter가 필요함")
            if adapter_ref is not None and adapter_ref not in adapters:
                add(findings, "S117", f"{path}: 미등록 adapter {adapter_ref}")
            candidates = implementation.get("candidates")
            if not isinstance(candidates, list):
                add(findings, "S118", f"{path}: candidates는 배열이어야 함")
            else:
                seen_candidates: set[str] = set()
                selected_candidates = 0
                for position, candidate in enumerate(candidates):
                    pointer = f"{path}:candidates[{position}]"
                    if not isinstance(candidate, dict):
                        add(findings, "S119", f"{pointer}: object가 아님")
                        continue
                    require_fields(
                        candidate,
                        {
                            "id",
                            "type",
                            "status",
                            "research_refs",
                            "license_status",
                            "maintenance_status",
                            "notes",
                        },
                        pointer,
                        findings,
                        "S134",
                    )
                    candidate_id = candidate.get("id")
                    if not isinstance(candidate_id, str) or not re.fullmatch(
                        r"candidate:[a-z0-9][a-z0-9._-]*", candidate_id
                    ):
                        add(findings, "S120", f"{pointer}: 잘못된 candidate id")
                    elif candidate_id in seen_candidates:
                        add(findings, "S121", f"{pointer}: 중복 candidate id {candidate_id}")
                    else:
                        seen_candidates.add(candidate_id)
                    refs = candidate.get("research_refs")
                    if not isinstance(refs, list):
                        add(findings, "S122", f"{pointer}: research_refs는 배열이어야 함")
                    else:
                        for research_ref in refs:
                            if research_ref not in research:
                                add(findings, "S123", f"{pointer}: research reference 없음 {research_ref}")
                    if candidate.get("type") not in {
                        "embedded",
                        "engine",
                        "external-service",
                        "research-implementation",
                    }:
                        add(findings, "S135", f"{pointer}: 알 수 없는 candidate type")
                    if candidate.get("status") not in {
                        "discovered",
                        "evaluating",
                        "optional",
                        "selected",
                        "rejected",
                    }:
                        add(findings, "S136", f"{pointer}: 알 수 없는 candidate status")
                    if candidate.get("license_status") not in {
                        "not-reviewed",
                        "compatible",
                        "incompatible",
                        "not-applicable",
                    }:
                        add(findings, "S137", f"{pointer}: 알 수 없는 candidate license_status")
                    if candidate.get("maintenance_status") not in {"unknown", "active", "inactive"}:
                        add(findings, "S138", f"{pointer}: 알 수 없는 candidate maintenance_status")
                    if not isinstance(candidate.get("notes"), str) or not candidate.get("notes"):
                        add(findings, "S139", f"{pointer}: candidate notes 누락")
                    if candidate.get("status") == "selected":
                        selected_candidates += 1
                        if candidate.get("license_status") not in {"compatible", "not-applicable"}:
                            add(findings, "S124", f"{pointer}: selected candidate의 license 검토 미완료")
                        if candidate.get("maintenance_status") != "active":
                            add(findings, "S125", f"{pointer}: selected candidate가 active 유지보수 상태가 아님")
                if strategy in {"adapter", "hybrid"} and selected_candidates != 1:
                    add(findings, "S141", f"{path}: adapter/hybrid strategy는 selected candidate 하나가 필요함")
                if strategy in {"native", "custom-minimal"} and selected_candidates:
                    add(findings, "S142", f"{path}: native/custom-minimal strategy에 selected candidate가 있음")
            if strategy == "adapter" and adapter_ref in adapters:
                adapter = adapters[adapter_ref]
                missing_modes = sorted(set(definition.get("query_modes", [])) - set(adapter.get("query_modes", [])))
                if missing_modes:
                    add(findings, "S143", f"{path}: adapter가 query mode를 지원하지 않음 {','.join(missing_modes)}")
                query_operation = adapter.get("operations", {}).get("query", {})
                if query_operation.get("support") == "unsupported":
                    add(findings, "S144", f"{path}: adapter query operation이 unsupported임")
                export_formats = set(definition.get("portability", {}).get("export_formats", []))
                if export_formats and not export_formats.intersection(adapter.get("output_formats", [])):
                    add(findings, "S145", f"{path}: adapter output과 portability export 형식이 겹치지 않음")
            fallback = implementation.get("fallback")
            if not isinstance(fallback, dict):
                add(findings, "S126", f"{path}: fallback은 object여야 함")
            else:
                fallback_adapter = fallback.get("adapter")
                if fallback_adapter is not None and fallback_adapter not in adapters:
                    add(findings, "S127", f"{path}: 미등록 fallback adapter {fallback_adapter}")
                if fallback.get("data_access") not in {"full", "read-only", "export-only", "unavailable"}:
                    add(findings, "S140", f"{path}: 알 수 없는 fallback data_access")
                if definition.get("role") in {"evidence", "record"} and fallback.get("data_access") == "unavailable":
                    add(findings, "S128", f"{path}: evidence/record fallback은 핵심 자료 접근을 유지해야 함")
                modes = fallback.get("degraded_query_modes")
                if not isinstance(modes, list):
                    add(findings, "S129", f"{path}: degraded_query_modes는 배열이어야 함")
        portability = definition.get("portability")
        if not isinstance(portability, dict):
            add(findings, "S130", f"{path}: portability는 object여야 함")
        else:
            formats = portability.get("export_formats")
            if not isinstance(formats, list) or not formats or not all(isinstance(item, str) and item for item in formats):
                add(findings, "S131", f"{path}: export_formats는 비어 있지 않은 문자열 배열이어야 함")
            if portability.get("vendor_lock_in") not in {"prohibited", "exception-approved"}:
                add(findings, "S132", f"{path}: vendor_lock_in 값 오류")
            if not isinstance(portability.get("exit_plan"), str) or not portability.get("exit_plan"):
                add(findings, "S133", f"{path}: exit_plan 누락")

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
        adapter_registry=adapter_registry,
        adapters=adapters,
        adapter_paths=adapter_paths,
        research_catalog=research_catalog,
        research=research,
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
        f"adapters={len(model.adapters)} "
        f"research_refs={len(model.research)} "
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
                "implementation": definition["implementation"],
                "portability": definition["portability"],
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
        "adapters": [
            {
                "id": adapter_id,
                "type": adapter["type"],
                "query_modes": adapter["query_modes"],
                "output_formats": adapter["output_formats"],
                "operations": adapter["operations"],
            }
            for adapter_id, adapter in sorted(model.adapters.items())
        ],
        "research_references": [
            {
                "id": research_id,
                "type": entry["type"],
                "title": entry["title"],
                "adoption_status": entry["adoption_status"],
                "possible_use": entry["possible_use"],
            }
            for research_id, entry in sorted(model.research.items())
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
    for adapter_id, adapter in sorted(model.adapters.items()):
        records.append({"record_type": "adapter", **adapter})
    for research_id, entry in sorted(model.research.items()):
        records.append({"record_type": "research", **entry})

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
                "implementation": definition["implementation"],
                "portability": definition["portability"],
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
                "implementation": model.definitions[space_id]["implementation"],
                "portability": model.definitions[space_id]["portability"],
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
