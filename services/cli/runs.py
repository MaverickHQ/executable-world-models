from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from services.cli.check import _detect_repo_root


def _repo_root(cwd: Path | None = None) -> Path | None:
    return _detect_repo_root(cwd or Path.cwd())


def _candidate_paths(root: Path) -> list[Path]:
    return [
        root / "tmp" / "demo_local_loop" / "runs.json",
        root / "tmp" / "demo_local_loop" / "state.json",
    ]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_runs(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [item for item in obj if isinstance(item, dict)]
    if isinstance(obj, dict):
        if isinstance(obj.get("runs"), list):
            return [item for item in obj["runs"] if isinstance(item, dict)]
        return [obj]
    return []


def _find_latest_runs_source(root: Path) -> tuple[list[dict[str, Any]], Path | None]:
    for path in _candidate_paths(root):
        if path.exists():
            runs = _extract_runs(_read_json(path))
            if runs:
                return runs, path

    artifacts = root / "tmp" / "demo_local_loop" / "artifacts"
    if artifacts.exists():
        executions = sorted(artifacts.rglob("executions.json"))
        if executions:
            latest = executions[-1]
            rows = _extract_runs(_read_json(latest))
            if rows:
                return rows, latest

    return [], None


def _plan_summary(plan: Any) -> str:
    if not isinstance(plan, dict):
        return "plan: none"
    meta = plan.get("meta") or plan.get("metadata") or {}
    steps = plan.get("steps") or []
    lines = [f"plan.meta: {meta}"]
    for idx, step in enumerate(steps[:3], start=1):
        tool = step.get("tool") if isinstance(step, dict) else str(step)
        lines.append(f"plan.step[{idx}]: {tool}")
    return "\n".join(lines)


def runs_latest(cwd: Path | None = None) -> int:
    root = _repo_root(cwd)
    if root is None:
        print("No local runs found. Run scripts/demo_local_loop.py first.")
        return 0

    runs, source = _find_latest_runs_source(root)
    if not runs:
        print("No local runs found. Run scripts/demo_local_loop.py first.")
        return 0

    latest = runs[-1]
    print(f"source: {source}")
    print(json.dumps(latest, indent=2, sort_keys=True, default=str))
    print(_plan_summary(latest.get("plan")))
    return 0


def runs_tail(n: int, cwd: Path | None = None) -> int:
    root = _repo_root(cwd)
    if root is None:
        print("No local runs found. Run scripts/demo_local_loop.py first.")
        return 0

    runs, source = _find_latest_runs_source(root)
    if not runs:
        print("No local runs found. Run scripts/demo_local_loop.py first.")
        return 0

    tail = runs[-max(1, n) :]
    print(f"source: {source}")
    print(json.dumps(tail, indent=2, sort_keys=True, default=str))
    return 0
