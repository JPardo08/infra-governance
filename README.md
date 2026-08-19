# PARDO Infra Governance

Governance policy for the PARDO Infra agent topology.

V1 answers a single question:

**WHO may perform WHICH capability ON WHICH resource.**

| Agent | Capability | Resource | Execute | Mutate |
| --- | --- | --- | --- | --- |
| `infra-auditor` | `storage.health@1.0.0` | `nas-primary` | allow | deny |
| `infra-control` | `storage.health@1.0.0` | `nas-primary` | deny | deny |
| `infra-operator` | `storage.health@1.0.0` | `nas-primary` | deny | approval-required (no grant) |

Deny by default. `spec.defaults.capabilities.allow` remains `[]`.
Authority exists only as an explicit grant.

`infra-control` remains the orchestration root and may delegate to
`infra-auditor` and `infra-operator`. Delegation is not an execute grant.

## Boundaries

| Layer | Owns |
| --- | --- |
| Governance | `agentId` ↔ `capability` ↔ `resourceRef` |
| ToolFactory | capability implementation |
| DeploymentFactory | runtime / materialization |
| Backend | credentials, DSM roles, network identity |

Governance does not contain `synology-primary`, Tailscale, DSM, MCP, or
hostnames.

## Evaluator

`pardo_governance` loads `governance.json` and exposes `authorize` and
`resolve_owner`. It does not talk to OpenClaw, MCP, or DeploymentFactory.
