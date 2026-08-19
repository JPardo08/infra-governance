from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pardo_governance import DecisionCode, GovernanceError, load, validate

from helpers import CAPABILITY, RESOURCE, clone_document, production_document


class ValidateTests(unittest.TestCase):
    def test_production_policy_is_valid(self) -> None:
        policy = validate(production_document())
        self.assertEqual(len(policy.grants), 1)
        self.assertEqual(policy.grants[0].agent_id, "infra-auditor")

    def test_duplicate_grant_id_is_malformed(self) -> None:
        document = clone_document()
        document["spec"]["grants"].append(
            {
                "id": "infra-auditor-storage-health-nas-primary",
                "agentId": "infra-control",
                "action": "execute",
                "capability": CAPABILITY,
                "resourceRef": RESOURCE,
            }
        )
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_duplicate_grant_identity_is_malformed(self) -> None:
        document = clone_document()
        document["spec"]["grants"].append(
            {
                "id": "auditor-storage-health-duplicate",
                "agentId": "infra-auditor",
                "action": "execute",
                "capability": CAPABILITY,
                "resourceRef": RESOURCE,
            }
        )
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)
        self.assertTrue(
            any("duplicate grant identity" in item for item in ctx.exception.details["errors"])
        )

    def test_dangling_agent_ref_is_malformed(self) -> None:
        document = clone_document()
        document["spec"]["grants"][0]["agentId"] = "ghost-agent"
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_dangling_resource_ref_is_malformed(self) -> None:
        document = clone_document()
        document["spec"]["grants"][0]["resourceRef"] = "missing-nas"
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_dangling_capability_ref_is_malformed(self) -> None:
        document = clone_document()
        document["spec"]["grants"][0]["capability"] = "storage.health@9.9.9"
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_registry_key_mismatch_is_malformed(self) -> None:
        document = clone_document()
        record = document["spec"]["capabilityRegistry"].pop(CAPABILITY)
        document["spec"]["capabilityRegistry"]["storage.health@9.9.9"] = record
        document["spec"]["grants"][0]["capability"] = "storage.health@9.9.9"
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_non_empty_default_capabilities_is_malformed(self) -> None:
        document = clone_document()
        document["spec"]["defaults"]["capabilities"]["allow"] = [CAPABILITY]
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_grant_cannot_declare_mutations(self) -> None:
        document = clone_document()
        document["spec"]["grants"][0]["mutations"] = "allow"
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_malformed_json_is_malformed_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(GovernanceError) as ctx:
                load(path)
            self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_missing_required_field_is_malformed(self) -> None:
        document = clone_document()
        del document["spec"]["resources"]
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_unsupported_action_is_malformed(self) -> None:
        document = clone_document()
        document["spec"]["grants"][0]["action"] = "admin"
        with self.assertRaises(GovernanceError) as ctx:
            validate(document)
        self.assertEqual(ctx.exception.code, DecisionCode.MALFORMED_POLICY)

    def test_error_payload_is_structured(self) -> None:
        with self.assertRaises(GovernanceError) as ctx:
            validate({"kind": "Nope"})
        payload = ctx.exception.to_dict()
        self.assertEqual(payload["code"], "MALFORMED_POLICY")
        self.assertIn("errors", payload["details"])


if __name__ == "__main__":
    unittest.main()
