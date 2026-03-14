# Experiments

Experiments are the aggregation layer for trajectory data. They collect runs, validate structural correctness, and produce learning-ready datasets.

## Directory Structure

An experiment directory contains:

```
experiment/
├── evaluation_summary.json    # Aggregated run results
├── artifacts/                # Per-run trajectory data
│   ├── run-001/
│   │   ├── manifest.json
│   │   ├── trajectory.json
│   │   ├── decision.json
│   │   └── deltas.json
│   └── run-002/
│       └── ...
└── datasets/                 # Exported learning datasets (optional)
    └── trajectories.jsonl
```

## Evaluation Summary

The `evaluation_summary.json` contains aggregated results from all runs:

```json
{
  "aggregate": {
    "total_runs": 10,
    "runs_with_integrity_errors": 1,
    "runs_without_integrity_errors": 9,
    "pct_integrity_fail": 10.0,
    "avg_steps_executed": 5.2
  },
  "runs": [
    {
      "run_id": "run-001",
      "manifest_valid": true,
      "integrity_errors": [],
      "steps_executed": 7,
      "truncated_by_budget": false
    }
  ],
  "summary": {
    "total_runs": 10,
    "ok_runs": 9,
    "failed_runs": 1
  }
}
```

## Artifacts

Each run directory contains:

- **manifest.json**: Run metadata (mode, symbols, runtime version)
- **trajectory.json**: Sequence of observations and actions
- **decision.json**: Decision context
- **deltas.json**: State transitions

## Flow: Run → Evaluation → Experiment → Dataset

```
1. Run executes → produces artifacts/
2. Evaluation checks → produces evaluation_summary.json
3. Aggregation collects → creates experiment/
4. Learning exports → produces dataset (JSONL)
```

## Usage

Experiments are created by the evaluation system. To work with experiments:

```python
from services.core.learning import select_learning_runs, export_learning_dataset

# Select valid runs
runs = select_learning_runs(experiment_dir, require_valid=True)

# Export to learning dataset
export_learning_dataset(experiment_dir, output_path)
```

## Use Cases

- Compare strategy performance across runs
- Identify structurally valid trajectories for learning
- Aggregate metrics across experiments
- Generate learning datasets from validated runs
