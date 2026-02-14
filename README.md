# Executable World Models

This repository demonstrates stateful planning systems implemented locally and on AWS using:

- Deterministic world models
- Trade tape + execution ledger
- Budget enforcement (steps, tools, model calls, memory)
- AWS Bedrock AgentCore (Base + Tools)

The goal is not trading performance.
The goal is verifiable state transitions under explicit constraints.

---

## Architecture Overview

Local:
- Deterministic market path
- JSON strategy spec (BUY / SELL / HOLD)
- State transition engine
- Trade tape
- Execution ledger
- Exposure tracking

AWS (AgentCore):
- Lambda handler (AgentCore Base)
- Lambda handler (AgentCore Tools)
- Lambda handler (AgentCore Memory)
- HTTP API Gateway
- S3 artifact storage
- Budget enforcement circuit breakers
- Reserved concurrency guardrail

---

## COST CONTROLS (IMPORTANT)

Every AgentCore invocation includes explicit budget fields:

{
  "max_steps": 1,
  "max_tool_calls": 0,
  "max_model_calls": 0,
  "max_memory_ops": 0,
  "max_memory_bytes": 0
}

If any budget is exceeded:
- Execution stops immediately
- Response returns ok=false
- No further model/tool/memory calls occur

Additional safeguards:
- Lambda reserved concurrency = 1
- No recursive invocation
- No background loops
- No automatic retries

If you hit a threshold:
1) Increase the specific budget parameter
2) Redeploy
3) Re-test

If you receive a `budget_exceeded` response:
- Inspect `error.limiter` to identify the exact breaker that tripped.
- Inspect `error.budgets.budget` vs `error.budgets.budget_state`.
- Increase only the required budget dimension; keep other breakers strict.

Do NOT remove guardrails.

---

## Local Development

make setup
make lint
make test

Run local loop:
make demo-local-loop

Replay tape:
python3 scripts/replay_tape.py --tape tmp/demo_local_loop/tape.json

Replay executions:
python3 scripts/replay_executions.py --executions tmp/demo_local_loop/executions.json

---

## AWS Deployment (AgentCore Base)

AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make deploy-agentcore-base

Smoke test:
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make smoke-agentcore-base

---

## AWS Deployment (AgentCore Tools)

AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make deploy-agentcore-tools

Smoke test:
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make smoke-agentcore-tools

Run demo:
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make demo-agentcore-tools

---

## AgentCore Memory (optional, cost-safe)

Enable memory explicitly before smoke/demo runs:

ENABLE_AGENTCORE_MEMORY=1
MEMORY_MAX_OPS=1
MEMORY_MAX_BYTES=512

Deploy:
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make deploy-agentcore-memory

Smoke test:
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make smoke-agentcore-memory

Run demo:
AWS_PROFILE=beyond-tokens-dev AWS_REGION=us-east-1 make demo-agentcore-memory

Budgets:

| Budget | Meaning |
| --- | --- |
| max_memory_ops | Maximum memory put/get operations |
| max_memory_bytes | Maximum serialized bytes across memory ops |

If you hit a threshold:
1) Increase the specific memory budget (MEMORY_MAX_OPS / MEMORY_MAX_BYTES) only as needed.
2) Re-deploy and re-run the smoke test.
3) Confirm no runaway calls by keeping max_steps=1 and max_tool_calls=0.

### HTTPS CA bundle troubleshooting

Memory smoke/demo scripts always verify TLS.
They use `REQUESTS_CA_BUNDLE` when provided, otherwise they use `certifi`.

If your machine has certificate issues, export:

```bash
export REQUESTS_CA_BUNDLE="$(python3 -c 'import certifi; print(certifi.where())')"
```

Then re-run smoke/demo.

To clean up artifacts if needed, remove the run prefix from the artifacts bucket.

---

## Versioning

v0.7.0-base  → AgentCore baseline (no model calls)
v0.7.1-tools → Tool calling + budget enforcement + README rewrite
v0.7.2-memory → Optional memory path (budgeted, no model calls)
