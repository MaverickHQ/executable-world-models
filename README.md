# Executable World Models

Executable World Models (EWM) is a research framework for building deterministic experimental systems around intelligent agents.

The goal of the project is NOT trading performance and NOT agent automation.

The goal is architectural:

> to make intelligent behavior reproducible, inspectable, and experimentally verifiable.

Most agent systems generate outputs.

EWM generates trajectories.

A trajectory is the sequence of observations, decisions, and state transitions that occur while an agent interacts with an environment.

Once trajectories exist, they can be validated, aggregated into experiments, and used as inputs to learning systems.

---

# Why This Architecture Exists

Modern agent systems are powerful but opaque.

Agents can call tools, execute code, retrieve data, and orchestrate workflows. However, most systems still lack the structure required to study behavior.

Typical problems include:

- Non-reproducible executions
- Logs without structural guarantees
- Experiments that cannot be compared reliably
- Learning systems that lack clean trajectory data

Executable World Models addresses this by enforcing:

- deterministic execution
- explicit artifact generation
- structural evaluation
- experiment aggregation
- environment interaction
- learning-ready trajectory export

Together these layers form the architecture required to study intelligent systems.

---

# Core Idea: Trajectories, Not Outputs

Traditional agent frameworks return responses.

EWM records trajectories.

**Responses answer questions.**
**Trajectories explain behavior.**

Trajectories allow systems to:

- replay decisions
- compare strategies across experiments
- generate structured learning datasets
- study how agents interact with environments

This architectural shift is the foundation of the project.

---

# System Architecture

The system is organized as a layered experimental architecture:

```
tokens
↓
models
↓
agents
↓
constraints
↓
artifacts
↓
evaluation
↓
experiments
↓
environments
↓
learning
```

Each layer contributes a specific capability:

| Layer | Role |
|-------|------|
| Agents | Execute decision logic |
| Constraints | Enforce runtime safety limits |
| Artifacts | Record decision trajectories |
| Evaluation | Verify structural correctness |
| Experiments | Aggregate trajectories |
| Environments | Provide world interaction |
| Learning | Consume trajectories as datasets |

---

# Evidence Policy Feedback (v0.8.5)

Version v0.8.5 completes the learning loop with deterministic policy feedback.

The architectural loop is now:

```
environment → trajectories → artifacts → evaluation → experiments → evidence dataset → policy update → better decisions
```

Key concepts:

- **experiments** produce evidence (validated trajectories)
- **evidence** is analyzed by the learner stub to produce a learning report
- **policy** is built from the report, capturing action preferences by symbol and step
- **decisions** can consult the evidence policy to influence future actions

This is NOT reinforcement learning:

- No model weights are learned
- No gradient descent occurs
- No exploration/exploitation tradeoff
- Simply: past experiment evidence influences future decisions

Commands:

```bash
# Export learning dataset
python3 scripts/export_learning_dataset.py

# Run learner stub
python3 scripts/run_learning_stub.py

# Build evidence policy
python3 scripts/build_evidence_policy.py \
  --learning-report outputs/learning/demo_learning_report.json \
  --output outputs/learning/evidence_policy.json

# Run policy feedback demo
python3 scripts/demo_policy_feedback_loop.py
```

The evidence policy file is a simple JSON structure containing:

- `default_action`: The most common action across experiments
- `action_preferences_by_symbol`: Most common action for each trading symbol
- `action_preferences_by_step`: Most common action at each step position

Example demo:

```bash
python3 scripts/demo_policy_feedback_loop.py
```

---

# Policy-Guided Agent Demo (v0.8.5.1)

Version v0.8.5.1 adds a policy-guided trading agent that actually uses the evidence policy to make trading decisions.

The complete loop now reaches **future decisions**, not just policy creation:

```
environment → trajectories → artifacts → evaluation → experiments 
    → evidence dataset → learning report → evidence policy 
    → policy-guided agent → decisions
```

### What the Agent Does

- Loads an evidence policy (JSON file with action preferences)
- Consults the policy for each trading decision
- Uses symbol preferences first, then step preferences
- Falls back to default action when no evidence exists
- Provides explanations for each decision

This is NOT RL training - it's deterministic policy-guided decision making.

### Commands

```bash
# Run policy-guided agent demo
python3 scripts/demo_policy_guided_trading_agent.py

# Run end-to-end learning loop demo
python3 scripts/demo_end_to_end_learning_loop.py
```

### Example Output

```
--- Step 0 ---
  Observation: {'symbol': 'AAPL', 'step': 0, 'price': 150.0}
  Explanation: Decision for AAPL at step 0: hold (policy preference for symbol)
  Action: {'type': 'hold', 'symbol': 'AAPL', 'qty': 0, 'source': 'symbol', 'policy_used': True}
```

### What This Proves

1. Evidence policy can be loaded and consumed
2. Agent makes deterministic decisions based on policy
3. Policy preferences take precedence over defaults
4. Complete loop from experiments to decisions works end-to-end

---

# Trading Environment Example

The reference environment used in this repository is a deterministic market-path replay.

The environment provides agents with sequential market observations and records the resulting actions.

This domain is useful because it produces structured decision sequences that resemble real-world planning problems.

Example demo:

```bash
python3 scripts/demo_learning_loop.py
```

Example output:

```
STEP 1: Select Learning Runs
Selected 2 runs

STEP 2: Export Learning Dataset
Rows exported: 8

STEP 3: Run Stub Learner
Total runs: 2
Total steps: 8
```

---

# Local Development

Setup:

```bash
make setup
make lint
pytest
```

Run demo:

```bash
python3 scripts/demo_learning_loop.py
```

---

# AWS Deployment

Deploy the runtime:

```bash
make deploy-agentcore-loop
```

Verify health:

```
/health
```

Run integration tests:

```bash
pytest tests/integration
```

---

# Repository Structure

```
services/core/environment/   world environments
services/core/eval/          structural evaluation
services/core/learning/      learning scaffold
services/cli/                operational CLI

scripts/                     demos and tools
tests/                       unit and integration tests
docs/                        architecture documentation
```

---

# Essay Series

This repository accompanies the research essay series:

1. Agents Can Plan
2. Evaluation is a Primitive, Not a Report
3. Agents Need Worlds
4. The Architecture of Intelligent Systems
5. Closing the Learning Loop

Essays are published on Substack.

---

# Project Status

Current milestone:

**v0.8.5 — Evidence Policy Feedback Loop**

The system now supports:

- deterministic agent execution
- trajectory artifacts
- structural evaluation
- experiment aggregation
- environment interaction
- learning-ready dataset export
- deterministic policy feedback from experiment evidence

The learning loop is now complete: experiments produce evidence, evidence influences future decisions.

This is NOT reinforcement learning - it's a deterministic policy-feedback scaffold.
