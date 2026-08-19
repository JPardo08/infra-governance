"""Deterministic owner resolution. Never first-match."""

from __future__ import annotations

from .codes import DecisionCode
from .types import GovernancePolicy, OwnerResolution


def resolve_owner(
    policy: GovernancePolicy,
    *,
    capability: str,
    resource_ref: str,
) -> OwnerResolution:
    """Return the unique execute owner for a capability on a resource.

    Zero matching agents → NO_GRANT.
    One matching agent → OK.
    Two or more distinct agents → AMBIGUOUS_OWNER.
    """

    def deny(
        code: DecisionCode,
        message: str,
        matching: tuple[str, ...] = (),
    ) -> OwnerResolution:
        return OwnerResolution(
            resolved=False,
            code=code,
            capability=capability,
            resource_ref=resource_ref,
            agent_id=None,
            matching_agent_ids=matching,
            message=message,
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

    matching_agents = tuple(
        dict.fromkeys(
            grant.agent_id
            for grant in policy.grants
            if grant.action == "execute"
            and grant.capability == capability
            and grant.resource_ref == resource_ref
        )
    )

    if not matching_agents:
        return deny(
            DecisionCode.NO_GRANT,
            (
                f"no execute owner for {capability!r} "
                f"on {resource_ref!r}"
            ),
        )

    if len(matching_agents) > 1:
        return deny(
            DecisionCode.AMBIGUOUS_OWNER,
            (
                f"multiple execute owners for {capability!r} "
                f"on {resource_ref!r}: {list(matching_agents)}"
            ),
            matching_agents,
        )

    owner = matching_agents[0]
    return OwnerResolution(
        resolved=True,
        code=DecisionCode.OK,
        capability=capability,
        resource_ref=resource_ref,
        agent_id=owner,
        matching_agent_ids=matching_agents,
        message=(
            f"owner of {capability!r} on {resource_ref!r} is {owner!r}"
        ),
    )
