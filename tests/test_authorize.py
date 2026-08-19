from __future__ import annotations

import unittest

from pardo_governance import DecisionCode, authorize, validate

from helpers import CAPABILITY, RESOURCE, clone_document, production_policy


class AuthorizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = production_policy()

    def test_auditor_execute_storage_health_is_allowed(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="infra-auditor",
            capability=CAPABILITY,
            resource_ref=RESOURCE,
            mutation=False,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.effect, "ALLOW")
        self.assertEqual(decision.code, DecisionCode.ALLOW)

    def test_control_has_no_execute_grant(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="infra-control",
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, DecisionCode.NO_GRANT)

    def test_operator_has_no_execute_grant(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="infra-operator",
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, DecisionCode.NO_GRANT)

    def test_unknown_agent(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="unknown-agent",
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        self.assertEqual(decision.code, DecisionCode.AGENT_UNKNOWN)

    def test_unknown_resource(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="infra-auditor",
            capability=CAPABILITY,
            resource_ref="unknown-nas",
        )
        self.assertEqual(decision.code, DecisionCode.RESOURCE_UNKNOWN)

    def test_unknown_capability(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="infra-auditor",
            capability="storage.health@9.9.9",
            resource_ref=RESOURCE,
        )
        self.assertEqual(decision.code, DecisionCode.CAPABILITY_UNKNOWN)

    def test_auditor_mutation_is_denied(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="infra-auditor",
            capability=CAPABILITY,
            resource_ref=RESOURCE,
            mutation=True,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, DecisionCode.MUTATION_DENIED)

    def test_operator_mutation_requires_approval_when_granted(self) -> None:
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
        decision = authorize(
            policy,
            agent_id="infra-operator",
            capability=CAPABILITY,
            resource_ref=RESOURCE,
            mutation=True,
        )
        self.assertEqual(decision.code, DecisionCode.APPROVAL_REQUIRED)

    def test_decision_is_structured(self) -> None:
        decision = authorize(
            self.policy,
            agent_id="infra-control",
            capability=CAPABILITY,
            resource_ref=RESOURCE,
        )
        payload = decision.to_dict()
        self.assertEqual(payload["effect"], "DENY")
        self.assertEqual(payload["code"], "NO_GRANT")
        self.assertEqual(payload["agentId"], "infra-control")


if __name__ == "__main__":
    unittest.main()
