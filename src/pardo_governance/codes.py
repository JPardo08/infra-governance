"""Stable V1 decision codes. These are the public contract."""

from __future__ import annotations

from enum import Enum


class DecisionCode(str, Enum):
    ALLOW = "ALLOW"
    OK = "OK"
    AGENT_UNKNOWN = "AGENT_UNKNOWN"
    RESOURCE_UNKNOWN = "RESOURCE_UNKNOWN"
    CAPABILITY_UNKNOWN = "CAPABILITY_UNKNOWN"
    NO_GRANT = "NO_GRANT"
    MUTATION_DENIED = "MUTATION_DENIED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    AMBIGUOUS_OWNER = "AMBIGUOUS_OWNER"
    MALFORMED_POLICY = "MALFORMED_POLICY"
