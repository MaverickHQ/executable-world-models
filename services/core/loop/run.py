from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

from services.core.actions import PlaceBuy
from services.core.artifacts import ArtifactWriter
from services.core.deltas.compute import compute_state_delta
from services.core.execution import execute_run
from services.core.loop.types import ExecutionRow, LoopResult
from services.core.market import MarketPath
from services.core.observability import TapeRow
from services.core.persistence import PolicyStore, RunStore, StateStore
from services.core.simulator import simulate_plan
from services.core.state import RiskLimits, State
from services.core.strategy import evaluate_signals_with_rationale, signals_to_actions


def _format_signals(signals: Dict[str, object]) -> Dict[str, str]:
    return {symbol: signal.value for symbol, signal in signals.items()}


def _actions_with_prices(actions: List[object], prices: Dict[str, float]) -> List[object]:
    priced_actions = []
    for action in actions:
        price = prices.get(action.symbol, action.price)
        priced_actions.append(replace(action, price=price))
    return priced_actions


def _positions_slice(state: State, symbols: List[str]) -> Dict[str, float]:
    return {symbol: state.positions.get(symbol, 0.0) for symbol in symbols}


def _execution_rows_for_actions(
    step_index: int,
    run_id: str,
    decision: str,
    actions: List[object],
    prices: Dict[str, float],
    prior_state: State,
    next_state: State,
    reason: str,
    verification: str,
) -> List[ExecutionRow]:
    if decision != "APPROVED":
        return []

    execution_rows: List[ExecutionRow] = []
    cash_before = prior_state.cash_balance
    cash_after = next_state.cash_balance

    for action in actions:
        side = "BUY" if isinstance(action, PlaceBuy) else "SELL"
        symbol = action.symbol
        qty = action.quantity
        price = prices.get(symbol, action.price)
        positions_before = _positions_slice(prior_state, [symbol])
        positions_after = _positions_slice(next_state, [symbol])
        execution_rows.append(
            ExecutionRow(
                step_index=step_index,
                run_id=run_id,
                decision=decision,
                symbol=symbol,
                side=side,
                quantity=qty,
                price=price,
                cash_before=cash_before,
                cash_after=cash_after,
                positions_before=positions_before,
                positions_after=positions_after,
                reason=reason,
                verification=verification,
            )
        )
    return execution_rows


def run_loop(
    *,
    market_path: MarketPath,
    strategy: object,
    steps: int,
    data_dir: object,
) -> LoopResult:
    data_dir = data_dir
    artifact_dir = data_dir / "artifacts"

    state_store = StateStore(data_dir / "state.json")
    run_store = RunStore(data_dir / "runs.json")
    policy_store = PolicyStore(data_dir / "policies.json")
    artifact_writer = ArtifactWriter(artifact_dir)

    policy = {
        "policy_id": "default",
        "risk_limits": {
            "max_leverage": 2.0,
            "max_position_pct": 0.8,
            "max_position_value": 5_000.0,
        },
    }
    policy_store.save_policy(policy)

    state = State(
        cash_balance=1_000.0,
        positions={},
        exposure=0.0,
        risk_limits=RiskLimits(2.0, 0.8, 5_000.0),
    )
    state_store.init_state(state)

    tape_rows: List[TapeRow] = []
    execution_rows: List[ExecutionRow] = []

    for step_index in range(steps):
        prices = market_path.price_context(step_index)
        evaluation = evaluate_signals_with_rationale(
            strategy=strategy,
            state=state,
            price_ctx=prices,
            step_index=step_index,
            market_path=market_path,
        )
        signals = _format_signals(evaluation.signals)
        rationales = evaluation.rationales

        actions = signals_to_actions(strategy, state, prices, evaluation.signals)
        action_payloads = [action.to_dict() for action in actions]

        if not actions:
            delta = compute_state_delta(state, state, prices)
            tape_rows.append(
                TapeRow(
                    step_index=step_index,
                    prices=prices,
                    signals=signals,
                    rationales=rationales,
                    actions=action_payloads,
                    decision="HOLD",
                    why="strategy HOLD",
                    explanation="",
                    state_delta=delta,
                    verifier_errors=[],
                    run_id="-",
                    artifact_dir=str(artifact_dir),
                )
            )
            continue

        priced_actions = _actions_with_prices(actions, prices)
        simulation = simulate_plan(
            state,
            priced_actions,
            market_path,
            policy_id=policy["policy_id"],
            policy_version=policy.get("policy_version"),
            policy_hash=policy.get("policy_hash"),
        )
        run_store.save_run(simulation)
        artifacts = artifact_writer.write(simulation)

        decision = "APPROVED" if simulation.approved else "REJECTED"
        explanation = simulation.steps[-1].explanation if simulation.steps else ""
        verifier_errors = [
            {"code": error.code, "message": error.message}
            for error in (simulation.steps[-1].errors if simulation.steps else [])
        ]
        if simulation.approved and simulation.trajectory:
            final_state = simulation.trajectory[-1]
            delta = compute_state_delta(state, final_state, prices)
        else:
            final_state = state
            delta = compute_state_delta(state, state, prices)

        why_parts = [
            f"{symbol}: {rationale}"
            for symbol, rationale in rationales.items()
            if signals.get(symbol) != "HOLD"
        ]
        reason = "; ".join(why_parts) if why_parts else "strategy HOLD"
        verification = "verified OK" if simulation.approved else "verification failed"
        why = f"{reason} | {verification}"

        tape_rows.append(
            TapeRow(
                step_index=step_index,
                prices=prices,
                signals=signals,
                rationales=rationales,
                actions=action_payloads,
                decision=decision,
                why=why,
                explanation=explanation,
                state_delta=delta,
                verifier_errors=verifier_errors,
                run_id=simulation.run_id,
                artifact_dir=str(artifacts["decision"]).rsplit("/", 1)[0],
            )
        )

        execution_rows.extend(
            _execution_rows_for_actions(
                step_index=step_index,
                run_id=simulation.run_id,
                decision=decision,
                actions=priced_actions,
                prices=prices,
                prior_state=state,
                next_state=final_state,
                reason=reason,
                verification=verification,
            )
        )

        if simulation.approved:
            execution = execute_run(run_store, state_store, simulation.run_id)
            if execution.state is not None:
                state = execution.state

    return LoopResult(tape_rows=tape_rows, execution_rows=execution_rows, final_state=state)