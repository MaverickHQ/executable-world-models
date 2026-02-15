from services.core.agentcore_loop.run import run_agentcore_loop
from services.core.agentcore_loop.types import LoopBudgets, LoopRequest


def test_loop_rejects_nonzero_model_budget() -> None:
    req = LoopRequest(budgets=LoopBudgets(max_model_calls=1))
    out = run_agentcore_loop(req)
    assert out["ok"] is False
    assert out["error"]["code"] == "invalid_budget"
