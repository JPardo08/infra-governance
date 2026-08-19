"""Deterministic authorization against a validated policy."""

from __future__ import annotations

from .codes import DecisionCode
from .types import AuthorizationDecision, GovernancePolicy


def authorize(
    policy: GovernancePolicy,
    *,
    agent_id: str,
    capability: str,
    resource_ref: str,
    mutation: bool = False,
) -> AuthorizationDecision:
    """Decide whether an agent may execute a capability on a resource.

    Unknown identities and missing grants return DENY with a stable code.
    This function does not raise for those semantic cases.
    """

    def deny(code: DecisionCode, message: str) -> AuthorizationDecision:
        return AuthorizationDecision(
            effect="DENY",
            code=code,
            agent_id=agent_id,
            capability=capability,
            resource_ref=resource_ref,
            mutation=mutation,
            message=message,
        )

    if agent_id not in policy.agents:
        return deny(
            DecisionCode.AGENT_UNKNOWN,
            f"unknown agent {agent_id!r}",
        )

    if capability not in policy.capability_registry:
        return deny(
            DecisionCode.CAPABILITY_UNKNOWN,
            f"unknown capability {capability!r}",
        )

    if resource_ref not in policy.resources:
        return deny(
            DecisionCode.RESOURCE_UNKNOWN,
            f"unknown resource {resource_ref!r}",
        )

    matching = [
        grant
        for grant in policy.grants
        if grant.agent_id == agent_id
        and grant.action == "execute"
        and grant.capability == capability
        and grant.resource_ref == resource_ref
    ]
    if not matching:
        return deny(
            DecisionCode.NO_GRANT,
            (
                f"agent {agent_id!r} has no execute grant for "
                f"{capability!r} on {resource_ref!r}"
            ),
        )

    if mutation:
        ceiling = policy.agent_mutations(agent_id)
        if ceiling == "deny":
            return deny(
                DecisionCode.MUTATION_DENIED,
                f"agent {agent_id!r} mutations ceiling is deny",
            )
        if ceiling == "approval-required":
            return deny(
                DecisionCode.APPROVAL_REQUIRED,
                f"agent {agent_id!r} mutations require approval",
            )
        return deny(
            DecisionCode.MALFORMED_POLICY,
            f"agent {agent_id!r} has unsupported mutations value {ceiling!r}",
        )

    return AuthorizationDecision(
        effect="ALLOW",
        code=DecisionCode.ALLOW,
        agent_id=agent_id,
        capability=capability,
        resource_ref=resource_ref,
        mutation=mutation,
        message=(
            f"agent {agent_id!r} may execute {capability!r} "
            f"on {resource_ref!r}"
        ),
    )
