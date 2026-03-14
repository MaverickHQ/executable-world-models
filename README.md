# Executable World Models

Executable World Models (EWM) is a research framework for building deterministic experimental systems around intelligent agents.

The goal of the project is NOT trading performance and NOT agent automation.

The goal is architectural:

to make intelligent behavior reproducible, inspectable, and experimentally verifiable.

Most agent systems generate outputs.

EWM generates trajectories.

A trajectory is the sequence of observations, decisions, and state transitions that occur while an agent interacts with an environment.

Once trajectories exist, they can be validated, aggregated into experiments, and used as inputs to learning systems.

------------------------------------------------------------

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

------------------------------------------------------------

# Core Idea: Trajectories, Not Outputs

Traditional agent frameworks return responses.

EWM records trajectories.

Responses answer questions.

Trajectories explain behavior.

Trajectories allow systems to:

- replay decisions
- compare strategies across experiments
- generate structured learning datasets
- study how agents interact with environments

This architectural shift is the foundation of the project.

------------------------------------------------------------

# System Architecture

The system is organized as a layered experimental architecture:

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

Each layer contributes a specific capability:

Layer | Role
Agents | Execute decision logic
Constraints | Enforce runtime safety limits
Artifacts | Record decision trajectories
Evaluation | Verify structural correctness
Experiments | Aggregate trajectories
Environments | Provide world interaction
Learning | Consume trajectories as datasets

------------------------------------------------------------

# Learning Loop (v0.8.4)

Version v0.8.4 introduces a minimal learning-loop scaffold.

Validated trajectories can now be exported as learning-ready datasets and consumed by a learning layer.

The architectural loop becomes:

environment → trajectories → artifacts → evaluation → experiments → dataset → learner

The learner included in this release is intentionally minimal.

It demonstrates how learning systems can consume trajectory datasets without introducing reinforcement learning or policy training.

------------------------------------------------------------

# Trading Environment Example

The reference environment used in this repository is a deterministic market-path replay.

The environment provides agents with sequential market observations and records the resulting actions.

This domain is useful because it produces structured decision sequences that resemble real-world planning problems.

Example demo:

python3 scripts/demo_learning_loop.py

Example output:

STEP 1: Select Learning Runs
Selected 2 runs

STEP 2: Export Learning Dataset
Rows exported: 8

STEP 3: Run Stub Learner
Total runs: 2
Total steps: 8

------------------------------------------------------------

# Local Development

Setup:

make setup
make lint
pytest

Run demo:

python3 scripts/demo_learning_loop.py

------------------------------------------------------------

# AWS Deployment

Deploy the runtime:

make deploy-agentcore-loop

Verify health:

/health

Run integration tests:

pytest tests/integration

------------------------------------------------------------

# Repository Structure

services/core/environment/   world environments
services/core/eval/          structural evaluation
services/core/learning/      learning scaffold
services/cli/                operational CLI

scripts/                     demos and tools
tests/                       unit and integration tests
docs/                        architecture documentation

------------------------------------------------------------

# Essay Series

This repository accompanies the research essay series:

1. Agents Can Plan
2. Evaluation is a Primitive, Not a Report
3. Agents Need Worlds
4. The Architecture of Intelligent Systems
5. Closing the Learning Loop

Essays are published on Substack.

------------------------------------------------------------

# Project Status

Current milestone:

v0.8.4 — Learning-ready experimental architecture

The system now supports:

- deterministic agent execution
- trajectory artifacts
- structural evaluation
- experiment aggregation
- environment interaction
- learning-ready dataset export

Future work may explore:

- world model learning
- policy optimization
- experiment-driven agent improvement
