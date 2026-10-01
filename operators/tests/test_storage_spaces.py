"""Storage control-plane fixtures, independent of a shell or Unix tools."""
import json
import shutil
import unittest
from test_operators import FixtureTest, ROOT


FIXTURES = json.loads(r'''
{
  "storage/adapters/registry.json": {
    "schema_version": 1,
    "adapters": [
      {
        "id": "adapter:fixture",
        "definition": "storage/adapters/fixture.json"
      }
    ],
    "recorded_at": "2026-08-28 00:00:00 UTC"
  },
  "storage/adapters/fixture.json": {
    "schema_version": 1,
    "id": "adapter:fixture",
    "type": "embedded",
    "status": "active",
    "implementation": "fixture:adapter-v1",
    "operations": {
      "write": {
        "support": "supported",
        "notes": "fixture write"
      },
      "query": {
        "support": "supported",
        "notes": "fixture query"
      },
      "trace": {
        "support": "supported",
        "notes": "fixture trace"
      },
      "export": {
        "support": "supported",
        "notes": "fixture export"
      },
      "rebuild": {
        "support": "degraded",
        "notes": "fixture rebuild"
      },
      "health": {
        "support": "supported",
        "notes": "fixture health"
      }
    },
    "query_modes": [
      "exact",
      "state",
      "time-range"
    ],
    "input_formats": [
      "json"
    ],
    "output_formats": [
      "jsonl"
    ],
    "consistency": "snapshot",
    "license_status": "compatible",
    "public_safety": {
      "classification": "public-metadata-only",
      "raw_content_allowed": false
    },
    "recorded_at": "2026-08-28 00:00:00 UTC"
  },
  "storage/transformations/event-to-object.json": {
    "schema_version": 1,
    "id": "transformation:event-to-object",
    "version": 1,
    "method": "fixture projection",
    "inputs": [
      {
        "space": "space:harness-events",
        "ref_pattern": "fixture:issues/*.md"
      }
    ],
    "outputs": [
      {
        "space": "space:objects",
        "ref_pattern": "fixture:objects/*.json"
      }
    ],
    "preserves": [
      "identity",
      "event time"
    ],
    "losses": [
      "unstructured detail"
    ],
    "reversible": false,
    "implementation": "fixture:manual-v1",
    "recorded_at": "2026-08-28 00:00:00 UTC"
  },
  "storage/catalog/observation.json": {
    "schema_version": 1,
    "id": "catalog:fixture-observation",
    "type": "fixture-observation",
    "recorded_at": "2026-08-28 00:00:00 UTC",
    "representations": [
      {
        "space": "space:harness-events",
        "ref": "fixture:issues/status.md",
        "role": "record",
        "valid_from": "2026-08-28 00:00:00 UTC"
      },
      {
        "space": "space:objects",
        "ref": "fixture:objects/one.json",
        "role": "record",
        "confidence": 0.8
      }
    ],
    "lineage": {
      "sources": [
        {
          "space": "space:evidence-references",
          "ref": "fixture:evidence/run-1"
        }
      ],
      "transformation": "transformation:event-to-object"
    },
    "public_safety": {
      "reviewed": true,
      "classification": "public-metadata-only"
    }
  },
  "storage/catalog/unsafe.json": {
    "schema_version": 1,
    "id": "catalog:unsafe-fixture",
    "type": "fixture-observation",
    "recorded_at": "2026-08-28 00:00:00 UTC",
    "representations": [
      {
        "space": "space:unregistered",
        "ref": "fixture:/private/content"
      },
      {
        "space": "space:objects",
        "ref": "https://example.invalid/private"
      }
    ],
    "lineage": {
      "sources": []
    },
    "public_safety": {
      "reviewed": false,
      "classification": "public-metadata-only"
    }
  }
}
''')


class StorageTests(FixtureTest):
    def test_storage_contract(self):
        for directory in (
            "storage/definitions", "storage/adapters", "storage/catalog", "storage/transformations",
            "storage/spaces/evidence", "storage/spaces/objects", "storage/spaces/relations",
            "storage/spaces/residuals", "journal", "explorations", "requests", "proposals",
            "issues", "changed", "feedback/candidates", "tasks", "indexes", "research",
        ):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        for name in ("ISSUES.md", "AGENDA.md", "INITIATIVES.md"):
            self.write(name, "")
        for source in [ROOT / "storage/registry.json", ROOT / "research/catalog.json", *sorted((ROOT / "storage/definitions").glob("*.json"))]:
            shutil.copyfile(source, self.root / source.relative_to(ROOT))
        self.write('storage/adapters/registry.json', json.dumps(FIXTURES['storage/adapters/registry.json']))
        self.write('storage/adapters/fixture.json', json.dumps(FIXTURES['storage/adapters/fixture.json']))
        self.write('storage/transformations/event-to-object.json', json.dumps(FIXTURES['storage/transformations/event-to-object.json']))
        self.write('storage/catalog/observation.json', json.dumps(FIXTURES['storage/catalog/observation.json']))
        path = self.root / "storage/definitions/objects.json"
        definition = json.loads(path.read_text(encoding="utf-8"))
        definition["implementation"]["strategy"] = "adapter"
        definition["implementation"]["adapter"] = "adapter:fixture"
        definition["implementation"]["candidates"] = [{
            "id": "candidate:fixture", "type": "embedded", "status": "selected",
            "research_refs": ["research:bigdawg-polystore"], "license_status": "compatible",
            "maintenance_status": "active", "notes": "fixture candidate",
        }]
        self.write("storage/definitions/objects.json", json.dumps(definition))
        output = self.operator("storage-spaces", "--root", self.root, "audit")
        for expected in ("OK storage-spaces:", "active_spaces=9", "adapters=1", "research_refs=8", "catalog_entries=1", "transformations=1"):
            self.assertIn(expected, output)
        self.operator("storage-spaces", "--root", self.root, "build-index")
        first = (self.root / "indexes/storage-catalog.json").read_bytes()
        self.operator("storage-spaces", "--root", self.root, "build-index")
        self.assertEqual(first, (self.root / "indexes/storage-catalog.json").read_bytes())
        query = self.operator("storage-spaces", "--root", self.root, "query", "--role", "record", "--text", "relation", "--limit", "5")
        self.assertIn('"id": "space:relations"', query)
        adapter = self.operator("storage-spaces", "--root", self.root, "query", "--id", "adapter:fixture", "--limit", "5")
        self.assertIn('"record_type": "adapter"', adapter)
        plan = self.operator("storage-spaces", "--root", self.root, "plan", "--mode", "relation", "--mode", "evidence", "--limit", "5")
        self.assertIn('"space": "space:cross-space-catalog"', plan)
        self.assertIn('"unserved_modes": []', plan)
        context = self.operator("storage-spaces", "--root", self.root, "context", "catalog:fixture-observation", "--limit", "1")
        self.assertIn('"omitted_representations": 1', context)
        self.assertIn('"id": "transformation:event-to-object"', context)
        self.write('storage/catalog/unsafe.json', json.dumps(FIXTURES['storage/catalog/unsafe.json']))
        definition["implementation"]["candidates"][0]["research_refs"].append("research:missing")
        self.write("storage/definitions/objects.json", json.dumps(definition))
        adapter_path = self.root / "storage/adapters/fixture.json"
        adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
        adapter["license_status"] = "not-reviewed"
        adapter["query_modes"].remove("time-range")
        self.write("storage/adapters/fixture.json", json.dumps(adapter))
        catalog = json.loads((self.root / "research/catalog.json").read_text(encoding="utf-8"))
        catalog["entries"][0]["source"]["url"] = "http://127.0.0.1/private"
        self.write("research/catalog.json", json.dumps(catalog))
        output = self.operator("storage-spaces", "--root", self.root, "audit")
        for code in ("ATTENTION storage-spaces:", "C008", "C009", "D111", "R008", "S123", "S143"):
            self.assertIn(code, output)
        self.operator("storage-spaces", "--root", self.root, "build-index", code=1)
        self.assertEqual(first, (self.root / "indexes/storage-catalog.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
