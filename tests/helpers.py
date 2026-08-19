from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from pardo_governance import load

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "governance.json"

CAPABILITY = "storage.health@1.0.0"
RESOURCE = "nas-primary"


def production_policy():
    return load(POLICY_PATH)


def production_document() -> dict[str, Any]:
    return deepcopy(dict(production_policy().document))


def clone_document() -> dict[str, Any]:
    return deepcopy(production_document())
