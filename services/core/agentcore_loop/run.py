from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict

from services.core.agentcore_loop.types import LoopRequest
from services.core.loop import run_loop
from services.core.market.generator import generate_market_path
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


def run_agentcore_loop(req: LoopRequest) -> Dict[str, Any]:
    if req.mode != "agentcore-loop":
        return {
            "ok": False,
            "mode": req.mode,
            "error": {"code": "invalid_mode", "message": "mode must be 'agentcore-loop'"},
        }

    try:
        _validate_budgets(req)
    except ValueError as e:
        return {
            "ok": False,
            "mode": req.mode,
            "error": {"code": "invalid_budget", "message": str(e)},
        }

    market_path = generate_market_path(
        tickers=list(req.symbols),
        n_steps=req.steps,
        seed=req.seed,
    )

    strategy = load_strategy(STRATEGY_PATH)
    steps = min(req.steps, len(market_path.steps))
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