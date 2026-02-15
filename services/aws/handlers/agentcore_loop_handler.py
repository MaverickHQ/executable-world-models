from __future__ import annotations

import json
from typing import Any

from services.core.agentcore_loop.run import run_agentcore_loop
from services.core.agentcore_loop.types import LoopBudgets, LoopRequest


def _parse(event: dict[str, Any]) -> LoopRequest:
    body_raw = event.get("body") or "{}"
    if isinstance(body_raw, str):
        body = json.loads(body_raw or "{}")
    else:
        body = body_raw

    budgets = body.get("budgets") or {}
    return LoopRequest(
        budgets=LoopBudgets(
            max_steps=int(budgets.get("max_steps", 5)),
            max_tool_calls=int(budgets.get("max_tool_calls", 10)),
            max_model_calls=int(budgets.get("max_model_calls", 0)),
            max_memory_ops=int(budgets.get("max_memory_ops", 0)),
            max_memory_bytes=int(budgets.get("max_memory_bytes", 0)),
        ),
        seed=int(body.get("seed", 7)),
        symbols=tuple(body.get("symbols", ["AAPL", "MSFT"])),
        starting_cash=float(body.get("starting_cash", 1000.0)),
        steps=int(body.get("steps", 5)),
        write_artifacts=bool(body.get("write_artifacts", True)),
        mode=str(body.get("mode", "agentcore-loop")),
    )


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    req = _parse(event)
    result = run_agentcore_loop(req)

    status = 200 if result.get("ok") else 400
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(result),
    }
