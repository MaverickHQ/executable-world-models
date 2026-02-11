from __future__ import annotations

import json
from pathlib import Path
from typing import List

from services.core.loop.types import ExecutionRow


def write_execution_ledger(path: Path, rows: List[ExecutionRow]) -> None:
    path.write_text(json.dumps([row.to_dict() for row in rows], indent=2))