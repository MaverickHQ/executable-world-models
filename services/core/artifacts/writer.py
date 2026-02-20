from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from services.core.simulator import SimulationResult


def serialize_simulation_result(result: SimulationResult) -> Dict[str, dict]:
    """
    Serialize a SimulationResult into artifact payloads.
    
    Returns dictionaries ready for JSON serialization.
    Shared by both local and S3 artifact writers.
    """
    trajectory_payload = {
        "run_id": result.run_id,
        "trajectory": [state.to_dict() for state in result.trajectory],
        "steps": [
            {
                "step_index": step.step_index,
                "action": {
                    "type": step.action.__class__.__name__,
                    "symbol": step.action.symbol,
                    "quantity": step.action.quantity,
                    "price": step.action.price,
                },
                "price_context": step.price_context,
                "accepted": step.accepted,
                "errors": [
                    {"code": error.code, "message": error.message}
                    for error in step.errors
                ],
                "explanation": step.explanation,
                "state_delta": step.state_delta,
            }
            for step in result.steps
        ],
    }

    decision_payload = {
        "run_id": result.run_id,
        "approved": result.approved,
        "rejected_step_index": result.rejected_step_index,
        "errors": [
            {
                "step_index": step.step_index,
                "errors": [
                    {"code": error.code, "message": error.message}
                    for error in step.errors
                ],
            }
            for step in result.steps
            if step.errors
        ],
        "planner": {
            "planner_name": result.planner_name,
            "planner_metadata": result.planner_metadata,
        },
        "policy": {
            "policy_id": result.policy_id,
            "policy_version": result.policy_version,
            "policy_hash": result.policy_hash,
        },
    }

    deltas_payload = {
        "run_id": result.run_id,
        "deltas": [step.state_delta for step in result.steps],
    }
    
    return {
        "trajectory": trajectory_payload,
        "decision": decision_payload,
        "deltas": deltas_payload,
    }


@dataclass
class ArtifactWriter:
    output_dir: Path

    def write(self, result: SimulationResult) -> Dict[str, Path]:
        run_dir = self.output_dir / result.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        payloads = serialize_simulation_result(result)
        
        trajectory_path = run_dir / "trajectory.json"
        decision_path = run_dir / "decision.json"
        deltas_path = run_dir / "deltas.json"

        trajectory_path.write_text(json.dumps(payloads["trajectory"], indent=2))
        decision_path.write_text(json.dumps(payloads["decision"], indent=2))
        deltas_path.write_text(json.dumps(payloads["deltas"], indent=2))

        return {
            "trajectory": trajectory_path,
            "decision": decision_path,
            "deltas": deltas_path,
        }
