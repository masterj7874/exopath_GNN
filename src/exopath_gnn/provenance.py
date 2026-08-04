"""Minimal provenance capture for protocol artifacts."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_provenance(
    path: str | Path,
    seed: int,
    frozen_files: Iterable[str | Path],
    command: str,
) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "synthetic_contract_test_only",
        "seed": int(seed),
        "command": command,
        "python": sys.version,
        "platform": platform.platform(),
        "frozen_files": {str(Path(item)): sha256_file(item) for item in frozen_files},
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

