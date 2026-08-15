# PARDO Infra Governance

Governance policy for the PARDO Infra agent topology.

## Scope

This repository defines effective authority constraints for:

- Infra Control
- Infra Auditor
- Infra Operator

It does not contain agent behavior or deployment implementation.

## Responsibilities

Governance defines:

- approved model policy;
- sandbox requirements;
- network and elevation boundaries;
- delegation authority;
- skill visibility;
- tool restrictions;
- capability and mutation boundaries.

## Separation of concerns

AgentFactory defines what an agent is.

GovernanceFactory defines what an instantiated agent may do.

DeploymentFactory translates these policies into the target runtime and verifies
that the effective environment satisfies them.

ToolFactory provides the capabilities that Governance may allow.

## Current V0

Infra Auditor has no infrastructure capabilities and may not mutate
infrastructure.

Infra Operator has no mutating capability granted yet. Future mutations require
an approved capability and the corresponding approval policy.

Infra Control is the only orchestration root for this project.
