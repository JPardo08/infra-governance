"""Load a ProjectGovernance document from a path or mapping."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Union

from .codes import DecisionCode
from .errors import GovernanceError
from .types import GovernancePolicy
from .validate import validate

Source = Union[str, Path, Mapping[str, Any]]


def load(source: Source) -> GovernancePolicy:
    """Parse and validate a policy. Raises MALFORMED_POLICY on failure."""

    if isinstance(source, Mapping):
        return validate(source)

    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GovernanceError(
            DecisionCode.MALFORMED_POLICY,
            f"unable to read policy file: {path}",
            details={"path": str(path)},
        ) from exc

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise GovernanceError(
            DecisionCode.MALFORMED_POLICY,
            "policy file is not valid JSON",
            details={"path": str(path), "error": str(exc)},
        ) from exc

    if not isinstance(payload, dict):
        raise GovernanceError(
            DecisionCode.MALFORMED_POLICY,
            "policy document must be a JSON object",
            details={"path": str(path)},
        )

    return validate(payload)
