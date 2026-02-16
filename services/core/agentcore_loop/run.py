from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from services.core.agentcore_loop.types import LoopRequest
from services.core.loop import run_loop
from services.core.market.generator import generate_market_path
from services.core.planner import LocalPlanner
from services.core.strategy import load_strategy

STRATEGY_PATH = "examples/strategies/threshold_demo.json"


def _get_max_model_calls(req: LoopRequest) -> int:
    """
    Budgets can be a typed dataclass (LoopBudgets) in unit tests,
    or a dict in live JSON->pydantic/dataclass decoding. Support both.
    """
    budgets = req.budgets
    if isinstance(budgets, dict):
        return int(budgets.get("max_model_calls", 0))
    return int(getattr(budgets, "max_model_calls", 0))


def _validate_budgets(req: LoopRequest) -> None:
    if _get_max_model_calls(req) != 0:
        raise ValueError("max_model_calls must be 0 for loop-no-llm")


def _planner_enabled() -> bool:
    return os.environ.get("ENABLE_LOCAL_PLANNER", "0") == "1"


def _budget_dict(req: LoopRequest) -> dict[str, int]:
    budgets = req.budgets
    if isinstance(budgets, dict):
        return {
            "max_steps": int(budgets.get("max_steps", 5)),
            "max_tool_calls": int(budgets.get("max_tool_calls", 10)),
            "max_model_calls": int(budgets.get("max_model_calls", 0)),
            "max_memory_ops": int(budgets.get("max_memory_ops", 0)),
            "max_memory_bytes": int(budgets.get("max_memory_bytes", 0)),
        }
    return {
        "max_steps": int(getattr(budgets, "max_steps", 5)),
        "max_tool_calls": int(getattr(budgets, "max_tool_calls", 10)),
        "max_model_calls": int(getattr(budgets, "max_model_calls", 0)),
        "max_memory_ops": int(getattr(budgets, "max_memory_ops", 0)),
        "max_memory_bytes": int(getattr(budgets, "max_memory_bytes", 0)),
    }


def run_agentcore_loop(req: LoopRequest) -> Dict[str, Any]:
    run_id = str(uuid4())

    if req.mode != "agentcore-loop":
        return {
            "ok": False,
            "run_id": run_id,
            "mode": req.mode,
            "plan": None,
            "error": {"code": "invalid_mode", "message": "mode must be 'agentcore-loop'"},
        }

    try:
        _validate_budgets(req)
    except ValueError as e:
        return {
            "ok": False,
            "run_id": run_id,
            "mode": req.mode,
            "plan": None,
            "error": {"code": "invalid_budget", "message": str(e)},
        }

    market_path = generate_market_path(
        tickers=list(req.symbols),
        n_steps=req.steps,
        seed=req.seed,
    )

    strategy = load_strategy(STRATEGY_PATH)
    steps = min(req.steps, len(market_path.steps))

    planner = LocalPlanner(enabled=_planner_enabled())
    plan = planner.make_plan(
        symbols=list(req.symbols),
        steps=req.steps,
        seed=req.seed,
        write_artifacts=req.write_artifacts,
        budgets=_budget_dict(req),
    )

    data_dir = Path(tempfile.mkdtemp(prefix="agentcore-loop-"))

    result = run_loop(
        market_path=market_path,
        strategy=strategy,
        steps=steps,
        data_dir=data_dir,
    )

    out: Dict[str, Any] = {
        "ok": True,
        "mode": req.mode,
        "run_id": run_id,
        "plan": LocalPlanner.to_dict(plan) if plan else None,
        "steps": steps,
        "tape_length": len(result.tape_rows),
        "execution_count": len(result.execution_rows),
        "final_state": {
            "cash_balance": result.final_state.cash_balance,
            "positions": result.final_state.positions,
        },
    }

    if req.write_artifacts:
        out["artifact_dir"] = str(data_dir)

    return out