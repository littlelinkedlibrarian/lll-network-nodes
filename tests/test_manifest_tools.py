from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import validate_manifests  # noqa: E402
import verify_live_node  # noqa: E402


class ManifestToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas/node-manifest.schema.json").read_text(encoding="utf-8"))
        cls.example = yaml.safe_load((ROOT / "examples/node-manifest.yaml").read_text(encoding="utf-8"))

    def write_manifest(self, document: dict, filename: str = "lll-garden-gate.yaml") -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        path = directory / filename
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        return path

    def test_checked_in_example_is_valid(self) -> None:
        result = validate_manifests.validate_one(
            ROOT / "examples/node-manifest.yaml",
            self.schema,
            example=True,
        )
        self.assertEqual(result["id"], "lll-garden-gate")
        self.assertEqual(result["environment"], "production")

    def test_credential_field_is_rejected(self) -> None:
        document = copy.deepcopy(self.example)
        document["spec"]["operator"]["apiKey"] = "not-a-real-key"
        with self.assertRaisesRegex(ValueError, "forbidden credential field"):
            validate_manifests.validate_one(self.write_manifest(document), self.schema)

    def test_split_origin_is_rejected_for_current_central_contract(self) -> None:
        document = copy.deepcopy(self.example)
        document["spec"]["operator"]["centralUserId"] = "central-user-123"
        document["spec"]["connectivity"]["uiUrl"] = "https://different.example.com"
        with self.assertRaisesRegex(ValueError, "must currently share one origin"):
            validate_manifests.validate_one(self.write_manifest(document), self.schema)

    def test_live_checker_rejects_private_address(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "private or non-global"):
            verify_live_node.require_public_host("127.0.0.1")


if __name__ == "__main__":
    unittest.main()
