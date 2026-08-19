"""Typed policy failure used by load/validate."""

from __future__ import annotations

from typing import Any, Mapping

from .codes import DecisionCode


class GovernanceError(Exception):
    """Fail-closed error for documents that cannot be evaluated.

    Semantic authorization denials are returned as decisions, not raised.
    ``load`` / ``validate`` raise this with ``code=MALFORMED_POLICY``.
    """

    def __init__(
        self,
        code: DecisionCode,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "details": self.details,
        }
