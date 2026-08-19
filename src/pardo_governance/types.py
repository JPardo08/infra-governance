"""Immutable policy and decision types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from .codes import DecisionCode


@dataclass(frozen=True)
class Grant:
    id: str
    agent_id: str
    action: str
    capability: str
    resource_ref: str

    @property
    def identity(self) -> tuple[str, str, str, str]:
        return (self.agent_id, self.action, self.capability, self.resource_ref)


@dataclass(frozen=True)
class GovernancePolicy:
    document: Mapping[str, Any]
    grants: tuple[Grant, ...]

    @property
    def spec(self) -> Mapping[str, Any]:
        return self.document["spec"]

    @property
    def agents(self) -> Mapping[str, Any]:
        return self.spec["agents"]

    @property
    def resources(self) -> Mapping[str, Any]:
        return self.spec["resources"]

    @property
    def capability_registry(self) -> Mapping[str, Any]:
        return self.spec["capabilityRegistry"]

    def agent_mutations(self, agent_id: str) -> str:
        return self.agents[agent_id]["mutations"]


@dataclass(frozen=True)
class AuthorizationDecision:
    effect: Literal["ALLOW", "DENY"]
    code: DecisionCode
    agent_id: str
    capability: str
    resource_ref: str
    mutation: bool
    message: str

    @property
    def allowed(self) -> bool:
        return self.effect == "ALLOW"

    def to_dict(self) -> dict[str, Any]:
        return {
            "effect": self.effect,
            "code": self.code.value,
            "agentId": self.agent_id,
            "capability": self.capability,
            "resourceRef": self.resource_ref,
            "mutation": self.mutation,
            "message": self.message,
        }


@dataclass(frozen=True)
class OwnerResolution:
    resolved: bool
    code: DecisionCode
    capability: str
    resource_ref: str
    agent_id: str | None
    matching_agent_ids: tuple[str, ...]
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "resolved": self.resolved,
            "code": self.code.value,
            "capability": self.capability,
            "resourceRef": self.resource_ref,
            "agentId": self.agent_id,
            "matchingAgentIds": list(self.matching_agent_ids),
            "message": self.message,
        }
