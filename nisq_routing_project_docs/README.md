---
title: NISQ Routing Environment Server
emoji: q
colorFrom: gray
colorTo: blue
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - reinforcement-learning
  - quantum-computing
  - nisq
---

# NISQ Adaptive Qubit Routing Environment

An OpenEnv environment for training and evaluating agents that perform adaptive qubit routing on noisy intermediate-scale quantum (NISQ) hardware topologies.

## Why this project

Real quantum hardware has sparse qubit connectivity and non-uniform gate errors. Compilers must decide when to insert SWAP gates and where to place logical qubits to reduce depth and error accumulation. This environment turns that real system-design problem into an RL task with deterministic grading.

## Problem scope

The agent observes a target circuit prefix, current logical-to-physical mapping, hardware coupling graph, and per-edge error rates. At each step it chooses routing and gate execution actions to finish compilation while maximizing estimated execution quality.

## OpenEnv alignment

This project follows OpenEnv patterns used across existing environments:

- Typed models: Action, Observation, State
- Server contract: reset(), step(action), state
- Metadata manifest: openenv.yaml
- Task suite with deterministic programmatic graders in [0.0, 1.0]
- Baseline inference script using OpenAI client

## Task suite

The environment defines three benchmark tasks with increasing difficulty:

1. Easy: Line topology routing with low noise heterogeneity
2. Medium: Heavy-hex style topology with mixed two-qubit gate density
3. Hard: Time-varying edge error profiles with constrained step budget

Detailed task definitions and graders are in [TASK_SUITE_AND_GRADERS.md](TASK_SUITE_AND_GRADERS.md).

## Action and observation spaces

Action and observation contracts are specified in [DESIGN_SPEC.md](DESIGN_SPEC.md) and reflected in [models.py](models.py).

## Reward strategy

The reward is trajectory-aware and includes:

- Positive reward for valid gate execution and progress
- Penalty for invalid actions, excessive SWAP insertion, and depth growth
- Terminal quality bonus tied to deterministic grader score

See [REWARD_AND_RUBRIC.md](REWARD_AND_RUBRIC.md).

## Quick start plan

1. Install package in editable mode.
2. Implement server runtime in server/.
3. Run local validation with openenv validate.
4. Run baseline inference with inference.py.
5. Package and deploy to Hugging Face Space.

## Required documents index

- Problem statement: [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md)
- Technical design: [DESIGN_SPEC.md](DESIGN_SPEC.md)
- Task and grader spec: [TASK_SUITE_AND_GRADERS.md](TASK_SUITE_AND_GRADERS.md)
- Reward and rubric: [REWARD_AND_RUBRIC.md](REWARD_AND_RUBRIC.md)
- Compliance matrix: [COMPLIANCE_MATRIX.md](COMPLIANCE_MATRIX.md)
- Implementation plan: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- Submission runbook: [SUBMISSION_RUNBOOK.md](SUBMISSION_RUNBOOK.md)

## Baseline benchmark results

Baseline was measured using the deterministic greedy routing policy in scripts/baseline_eval.py with seeds 7, 13, and 29.

| Task | Completion Rate | Avg Rubric Score | Avg Total Reward | Avg Steps |
|---|---|---:|---:|---:|
| easy_line_routing | 1.00 | 0.878 | 1.049 | 7.0 |
| medium_heavyhex_routing | 1.00 | 0.089 | -0.131 | 42.0 |
| hard_drift_aware_routing | 1.00 | 0.275 | -0.050 | 61.0 |

Detailed run artifacts are stored in baseline_results.json.

## Verification status

- Unit and integration tests: 9 passed (pytest)
- OpenEnv validation: [OK] Ready for multi-mode deployment

## Reproducibility commands

Use the project virtual environment from the workspace root.

1. c:\kaggle\meta\.venv\Scripts\python.exe -m pip install -e .[dev]
2. c:\kaggle\meta\.venv\Scripts\python.exe -m pytest -q
3. c:\kaggle\meta\.venv\Scripts\python.exe scripts\baseline_eval.py
4. c:\kaggle\meta\.venv\Scripts\openenv.exe validate .

## Related project docs

- [PRD.md](PRD.md)
- [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md)
- [DESIGN_SPEC.md](DESIGN_SPEC.md)
- [TASK_SUITE_AND_GRADERS.md](TASK_SUITE_AND_GRADERS.md)
- [REWARD_AND_RUBRIC.md](REWARD_AND_RUBRIC.md)
- [COMPLIANCE_MATRIX.md](COMPLIANCE_MATRIX.md)
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- [SUBMISSION_RUNBOOK.md](SUBMISSION_RUNBOOK.md)
