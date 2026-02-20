from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict

import boto3

from services.core.artifacts.writer import serialize_simulation_result
from services.core.simulator import SimulationResult


@dataclass
class S3ArtifactWriter:
    bucket_name: str

    def __post_init__(self) -> None:
        self._client = boto3.client("s3")

    def write(self, result: SimulationResult) -> Dict[str, str]:
        prefix = f"artifacts/{result.run_id}"
        trajectory_key = f"{prefix}/trajectory.json"
        decision_key = f"{prefix}/decision.json"
        deltas_key = f"{prefix}/deltas.json"

        # Use shared serialization function
        payloads = serialize_simulation_result(result)

        self._client.put_object(
            Bucket=self.bucket_name,
            Key=trajectory_key,
            Body=json.dumps(payloads["trajectory"], indent=2).encode("utf-8"),
        )
        self._client.put_object(
            Bucket=self.bucket_name,
            Key=decision_key,
            Body=json.dumps(payloads["decision"], indent=2).encode("utf-8"),
        )
        self._client.put_object(
            Bucket=self.bucket_name,
            Key=deltas_key,
            Body=json.dumps(payloads["deltas"], indent=2).encode("utf-8"),
        )

        return {
            "artifact_prefix": prefix,
            "trajectory_key": trajectory_key,
            "decision_key": decision_key,
            "deltas_key": deltas_key,
        }
