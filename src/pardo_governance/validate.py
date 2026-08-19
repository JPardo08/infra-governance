"""Schema plus semantic validation. Fail closed as MALFORMED_POLICY."""

from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from importlib.resources import files
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaError

from .codes import DecisionCode
from .errors import GovernanceError
from .types import GovernancePolicy, Grant

_SCHEMA = json.loads(
    files("pardo_governance")
    .joinpath("project_governance.schema.json")
    .read_text(encoding="utf-8")
)
_VALIDATOR = Draft202012Validator(_SCHEMA)

_MUTATION_FIELDS = frozenset({"mutations", "mutation", "allowMutations"})


def validate(document: Mapping[str, Any]) -> GovernancePolicy:
    """Validate structure and references. Returns an immutable policy."""

    if not isinstance(document, Mapping):
        raise GovernanceError(
            DecisionCode.MALFORMED_POLICY,
            "policy document must be a JSON object",
        )

    payload = json.loads(json.dumps(document))
    errors: list[str] = []

    schema_errors = sorted(
        _VALIDATOR.iter_errors(payload),
        key=lambda err: list(err.path),
    )
    for err in schema_errors:
        errors.append(_format_schema_error(err))

    if not errors:
        errors.extend(_semantic_errors(payload))

    if errors:
        raise GovernanceError(
            DecisionCode.MALFORMED_POLICY,
            "policy document is malformed",
            details={"errors": errors},
        )

    grants = tuple(
        Grant(
            id=item["id"],
            agent_id=item["agentId"],
            action=item["action"],
            capability=item["capability"],
            resource_ref=item["resourceRef"],
        )
        for item in payload["spec"]["grants"]
    )
    return GovernancePolicy(document=deepcopy(payload), grants=grants)


def _format_schema_error(err: JsonSchemaError) -> str:
    location = ".".join(str(part) for part in err.absolute_path) or "$"
    return f"{location}: {err.message}"


def _semantic_errors(payload: Mapping[str, Any]) -> list[str]:
    spec = payload["spec"]
    agents = spec["agents"]
    resources = spec["resources"]
    registry = spec["capabilityRegistry"]
    grants = spec["grants"]
    errors: list[str] = []

    allow = spec["defaults"]["capabilities"]["allow"]
    if allow != []:
        errors.append(
            "spec.defaults.capabilities.allow must remain empty; "
            "authority is expressed only via spec.grants"
        )

    for key, record in registry.items():
        expected = f"{record['id']}@{record['version']}"
        if key != expected:
            errors.append(
                f"spec.capabilityRegistry[{key!r}] key must equal {expected!r}"
            )

    for agent_id, agent in agents.items():
        for target in agent["delegation"]["allow"]:
            if target not in agents:
                errors.append(
                    f"spec.agents.{agent_id}.delegation.allow "
                    f"references unknown agent {target!r}"
                )
            if target == agent_id:
                errors.append(
                    f"spec.agents.{agent_id}.delegation.allow "
                    f"cannot include the agent itself"
                )

    grant_ids: list[str] = []
    identities: list[tuple[str, str, str, str]] = []
    for index, grant in enumerate(grants):
        prefix = f"spec.grants[{index}]"
        extra = _MUTATION_FIELDS.intersection(grant)
        if extra:
            errors.append(
                f"{prefix} cannot declare {sorted(extra)}; "
                "agent mutations is the mutation ceiling"
            )

        agent_id = grant["agentId"]
        capability = grant["capability"]
        resource_ref = grant["resourceRef"]

        if agent_id not in agents:
            errors.append(f"{prefix}.agentId references unknown agent {agent_id!r}")
        if capability not in registry:
            errors.append(
                f"{prefix}.capability references unknown capability {capability!r}"
            )
        if resource_ref not in resources:
            errors.append(
                f"{prefix}.resourceRef references unknown resource {resource_ref!r}"
            )

        grant_ids.append(grant["id"])
        identities.append(
            (agent_id, grant["action"], capability, resource_ref)
        )

    for grant_id, count in Counter(grant_ids).items():
        if count > 1:
            errors.append(f"duplicate grant id {grant_id!r}")

    for identity, count in Counter(identities).items():
        if count > 1:
            agent_id, action, capability, resource_ref = identity
            errors.append(
                "duplicate grant identity "
                f"(agentId={agent_id!r}, action={action!r}, "
                f"capability={capability!r}, resourceRef={resource_ref!r})"
            )

    return errors
