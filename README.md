Executable World Models

Executable World Models (EWM) is a research framework for building deterministic, stateful planning systems that run locally or on AWS under strict cost and safety constraints.

This project is not about trading performance.
It is about verifiable state transitions under explicit control.

The core question is simple:

Can we build agent systems that are reproducible, inspectable, and cost-bounded — without hidden loops or runaway behavior?

⸻

Why This Exists

Many modern agent systems obscure state transitions, blur reasoning and execution, and make cost behavior unpredictable.

EWM takes the opposite approach.

Every transition is deterministic.
Every action is logged.
Every execution is budget-constrained.
Nothing runs implicitly.

This repository demonstrates how to construct such systems from first principles.

⸻

EWM treats agent systems as experiments rather than demonstrations. Each execution produces a structured artifact record, which can be evaluated deterministically and aggregated across runs. This enables reproducible experimentation under explicit cost and safety constraints.

⸻

Design Principles

Determinism
The market path is fixed. Strategies operate on a known sequence. Given the same seed and inputs, results are reproducible.

Explicit State
All actions produce a trade tape, execution ledger, and final state snapshot. Nothing is hidden inside the runtime.

Hard Budget Boundaries
Every execution is constrained by explicit budget dimensions such as steps, tool calls, model calls, and memory operations. When a budget is exceeded, execution stops immediately.

No Implicit Scaling
There are no background loops, recursive invocations, or automatic retries. AWS Lambda reserved concurrency is set deliberately to prevent uncontrolled parallelism.

⸻

Architecture

EWM can run entirely locally or via AWS AgentCore.

Local Runtime

The local runtime includes:
	•	Deterministic market simulator
	•	JSON strategy specification (BUY / SELL / HOLD)
	•	State transition engine
	•	Tape and execution logs
	•	Replay tooling

This provides full transparency and reproducibility.

AWS Runtime (AgentCore)

The AWS deployment layers the same deterministic logic behind:
	•	Lambda handlers (Base, Tools, Memory, Loop)
	•	HTTP API Gateway
	•	S3 artifact storage
	•	Optional DynamoDB state persistence
	•	Strict budget enforcement

The goal is not scale.
The goal is control.

The architecture follows a layered approach: tokens → models → agents → constraints → artifacts → evaluation → experiments → environments. The upper layers generate intelligent behavior, while the lower layers ensure that behavior is reproducible, inspectable, and experimentally valid. See docs/architecture.md for the full diagram.

⸻

Cost & Safety Guardrails

Every invocation must provide explicit budgets, for example:
```
{
  "max_steps": 1,
  "max_tool_calls": 0,
  "max_model_calls": 0,
  "max_memory_ops": 0,
  "max_memory_bytes": 0
}
```
If any budget is exceeded:

Execution halts immediately.
The response returns ok=false.
No additional work is performed.

This system is designed to fail safely, not continue optimistically.

If you encounter budget_exceeded, inspect which limiter triggered and adjust only that specific dimension. Do not weaken unrelated guardrails.

⸻

Local Development

Install dependencies and run tests:
```
make setup
make lint
make test
```

Install dependencies and run tests:
```
make demo-local-loop
```

Replay the trade tape:
```
python3 scripts/replay_tape.py --tape tmp/demo_local_loop/tape.json
```

Replay executions:
```
python3 scripts/replay_executions.py --executions tmp/demo_local_loop/executions.json
```

AWS Deployment

Deploy AgentCore Base:
```
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make deploy-agentcore-base
```

Deploy AgentCore Tools:
```
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make deploy-agentcore-tools
```

Deploy AgentCore Memory (optional, cost-safe):
```
export ENABLE_AGENTCORE_MEMORY=1
export MEMORY_MAX_OPS=1
export MEMORY_MAX_BYTES=512
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make deploy-agentcore-memory
```

If your machine encounters TLS issues during smoke tests, set:
```
export REQUESTS_CA_BUNDLE="$(python3 -c 'import certifi; print(certifi.where())')"
```
CLI (ewm)

The ewm CLI provides operational control over runtime, cost guardrails, and run inspection.

Install in editable mode:
```
pip install -e .
```

Check configuration health:
```
ewm check
```

Show current runtime target:
```
ewm target show
```

Set runtime target:
```
ewm target set local
ewm target set aws
ewm target set both
```

Show or modify cost guardrails:
```
ewm cost show
ewm cost set --profile integration
ewm cost apply
```

Inspect recent runs:
```
ewm runs latest
ewm runs tail --n 10
```

Production safety requirements:
	•	The prod profile requires explicit confirmation (--yes)
	•	AWS targets require AWS_PROFILE and AWS_REGION
	•	Budgets must be non-negative integers

The CLI is designed to control execution, not bypass safeguards.

⸻

## API Endpoints

### Health Check
The `/health` endpoint provides a deterministic health status:
```json
{
  "status": "ok",
  "version": "0.8.0"
}
```

### Error Response Format
All API errors follow a standardized format per OpenSpec:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "request_id": "string"
  }
}
```

## Configuration

### Strategy Path
The loop strategy path is configurable via the `strategy_path` field in requests:
```json
{
  "strategy_path": "examples/strategies/threshold_demo.json"
}
```
Defaults to `examples/strategies/threshold_demo.json` if not specified.

## Testing

Run all tests:
```bash
pytest tests/ -q
```

Run contract tests:
```bash
pytest tests/contract/ -q
```

Run smoke test:
```bash
python3 scripts/smoke_health.py
```

---

## MarketPathEnvironment Layer (Experimental)

The MarketPathEnvironment layer provides a **stateful world interface for replaying market paths**. This environment is not a market simulator. It replays deterministic market paths to provide a stateful world interface for agents, bridging experiments to future environment-based work.

### What It Is

- **Deterministic replay-based environment**: Agents step through a fixed sequence of market observations
- **Stateful world interface**: Maintains positions, cash balance, and action history across steps
- **Lightweight**: Returns plain dicts, no external library types
- **Bridge toward future work**: Foundation for Essay 8 ("Agents Need Worlds")

### What It Is NOT

- **NOT a market simulator**: No order matching, no trade execution
- **NOT a broker**: No slippage modeling, no PnL computation
- **NOT RL training**: No reward optimization
- **NOT a world model**: No predictive modeling

Actions may be recorded/echoed but are **NOT financially executed**. No PnL is computed, no orders are matched, no rewards are calculated.

### Components

- **BaseEnvironment**: Abstract interface defining `reset()`, `state()`, and `step()` methods
- **MarketPathEnvironment**: Primary implementation (preferred name)
- **TradingEnvironment**: Alias for MarketPathEnvironment (backwards compatible)

### Design Principles

- **Deterministic**: Same inputs always produce same outputs
- **Replay-based**: Agents step through a fixed sequence of market observations
- **Inspectable**: All state transitions are visible and logged
- **Optional**: Does not affect existing runtime/evaluation stack

### Example Usage

```python
from services.core.environment import MarketPathEnvironment

# Define a simple market path
market_path = [
    {"AAPL": 100.0, "MSFT": 200.0},
    {"AAPL": 101.0, "MSFT": 201.0},
    {"AAPL": 102.0, "MSFT": 202.0},
]

# Create environment
env = MarketPathEnvironment(market_path=market_path, initial_cash=10_000.0)

# Reset to initial state
state = env.reset()

# Step through the environment
result = env.step({"type": "hold"})
result = env.step({"type": "buy", "symbol": "AAPL", "qty": 10})
```

Or run the demo script:

```bash
python3 scripts/demo_trading_environment.py
```

This layer provides foundational support for future environment-based experiments, planning with environmental feedback, and multi-step agent interactions.

---

Versioning

v0.7.0-base → AgentCore baseline (no model calls)
v0.7.1-tools → Tool calling + budget enforcement
v0.7.2-memory → Optional memory path
v0.7.6-planner → Local planner integration
v0.7.7-cli → Operational CLI controls
v0.8.0 → Health endpoint, contract tests, config strategy, structured logging
v0.8.1 → Evaluation infrastructure
v0.8.2 → AWS runtime validation
v0.8.3 → Structural evaluation + experiment aggregation

