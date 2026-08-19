from __future__ import annotations

import unittest

from pardo_governance import DecisionCode, resolve_owner, validate

from helpers import CAPABILITY, RESOURCE, clone_document, production_policy


class ResolveOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = production_policy()

    def test_storage_health_owner_is_auditor(self) -> None:
        result = resolve_owner(
            self.policy,
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        self.assertTrue(result.resolved)
        self.assertEqual(result.code, DecisionCode.OK)
        self.assertEqual(result.agent_id, "infra-auditor")
        self.assertEqual(result.matching_agent_ids, ("infra-auditor",))

    def test_two_distinct_agents_are_ambiguous(self) -> None:
        document = clone_document()
        document["spec"]["grants"].append(
            {
                "id": "infra-operator-storage-health-nas-primary",
                "agentId": "infra-operator",
                "action": "execute",
                "capability": CAPABILITY,
                "resourceRef": RESOURCE,
            }
        )
        policy = validate(document)
        result = resolve_owner(
            policy,
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        self.assertFalse(result.resolved)
        self.assertEqual(result.code, DecisionCode.AMBIGUOUS_OWNER)
        self.assertIsNone(result.agent_id)
        self.assertEqual(
            set(result.matching_agent_ids),
            {"infra-auditor", "infra-operator"},
        )

    def test_zero_owners_is_no_grant(self) -> None:
        document = clone_document()
        document["spec"]["grants"] = []
        policy = validate(document)
        result = resolve_owner(
            policy,
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        self.assertEqual(result.code, DecisionCode.NO_GRANT)
        self.assertFalse(result.resolved)

    def test_unknown_capability(self) -> None:
        result = resolve_owner(
            self.policy,
            capability="other.cap@1.0.0",
            resource_ref=RESOURCE,
        )
        self.assertEqual(result.code, DecisionCode.CAPABILITY_UNKNOWN)

    def test_unknown_resource(self) -> None:
        result = resolve_owner(
            self.policy,
            capability=CAPABILITY,
            resource_ref="missing-resource",
        )
        self.assertEqual(result.code, DecisionCode.RESOURCE_UNKNOWN)

    def test_never_returns_first_match_on_ambiguity(self) -> None:
        document = clone_document()
        document["spec"]["grants"].insert(
            0,
            {
                "id": "infra-control-storage-health-nas-primary",
                "agentId": "infra-control",
                "action": "execute",
                "capability": CAPABILITY,
                "resourceRef": RESOURCE,
            },
        )
        policy = validate(document)
        result = resolve_owner(
            policy,
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        self.assertEqual(result.code, DecisionCode.AMBIGUOUS_OWNER)
        self.assertNotEqual(result.agent_id, "infra-control")


if __name__ == "__main__":
    unittest.main()
