from __future__ import annotations

import unittest

from pardo_governance import load

from helpers import POLICY_PATH, production_policy


class V0InvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = production_policy()

    def test_defaults_capabilities_allow_is_empty(self) -> None:
        allow = self.policy.spec["defaults"]["capabilities"]["allow"]
        self.assertEqual(allow, [])

    def test_infra_control_is_root_coordinator(self) -> None:
        agent = self.policy.agents["infra-control"]
        self.assertEqual(agent["role"], "coordinator")
        self.assertEqual(agent["orchestration"], "root")
        self.assertEqual(agent["mutations"], "deny")
        self.assertEqual(
            agent["delegation"]["allow"],
            ["infra-auditor", "infra-operator"],
        )
        self.assertTrue(agent["delegation"]["requireExplicitTarget"])

    def test_auditor_and_operator_are_leaves(self) -> None:
        auditor = self.policy.agents["infra-auditor"]
        operator = self.policy.agents["infra-operator"]
        self.assertEqual(auditor["orchestration"], "leaf")
        self.assertEqual(operator["orchestration"], "leaf")
        self.assertEqual(auditor["delegation"]["allow"], [])
        self.assertEqual(operator["delegation"]["allow"], [])
        self.assertEqual(auditor["mutations"], "deny")
        self.assertEqual(operator["mutations"], "approval-required")

    def test_v0_agent_set_preserved(self) -> None:
        self.assertEqual(
            set(self.policy.agents),
            {"infra-control", "infra-auditor", "infra-operator"},
        )

    def test_production_document_loads(self) -> None:
        loaded = load(POLICY_PATH)
        self.assertEqual(loaded.document["metadata"]["version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
