# Product Requirements Document (PRD)

## Product

NISQ Adaptive Qubit Routing Environment

## Version and Date

- Version: 1.0
- Date: 2026-04-06
- Owner: Project Team

## 1. Executive Summary

This product is an OpenEnv-compatible reinforcement learning environment for adaptive qubit routing on noisy intermediate-scale quantum (NISQ) hardware. The environment simulates real compiler-level decisions where an agent must choose SWAP placement and gate execution strategies under sparse coupling constraints and non-uniform error rates.

The product goal is to provide a reproducible benchmark and training surface for routing policies that improve compiled circuit quality, measured through deterministic graders and dense trajectory rewards.

## 2. Problem Statement

Modern NISQ devices cannot execute many logical two-qubit interactions directly because hardware qubits are only partially connected and gate error rates differ per edge. Compilers must insert additional SWAPs and remap qubits, increasing depth and error exposure.

Poor routing causes:

- Higher circuit depth and runtime
- Lower success probability due to noisy edges
- More invalid or inefficient compilation trajectories

The environment must model this as a realistic sequential decision problem suitable for RL and agentic evaluation.

## 3. Goals

1. Create a real-world, non-toy OpenEnv environment for quantum routing.
2. Provide at least three deterministic tasks with easy, medium, and hard difficulty.
3. Implement deterministic programmatic graders producing scores in [0.0, 1.0].
4. Provide dense reward feedback throughout trajectories.
5. Deliver reproducible baseline inference and submission-ready outputs.

## 4. Non-Goals

- Pulse-level hardware calibration
- Fault-tolerant quantum error correction workflows
- Full large-scale statevector simulation
- Hardware claims beyond modeled estimates

## 5. Target Users and Stakeholders

- Quantum compiler researchers
- Hardware-aware transpilation engineers
- RL researchers in constrained combinatorial planning
- OpenEnv benchmark maintainers and hackathon evaluators

## 6. User Stories

1. As a compiler researcher, I want deterministic routing tasks so I can compare policies fairly.
2. As an RL engineer, I want dense rewards and action masks so training is stable and debuggable.
3. As a benchmark maintainer, I want reproducible graders so scores are verifiable and auditable.
4. As a submission owner, I want a compliant inference script and logs so validation passes reliably.

## 7. Scope

### 7.1 In Scope

- OpenEnv server implementing reset, step, and state
- Typed models for Action, Observation, and State
- Task registry with three fixed difficulty tiers
- Deterministic grading formulas
- Dense reward design with terminal quality bonus
- Baseline inference script and submission runbook

### 7.2 Out of Scope

- Dynamic hardware API integration
- Proprietary backend coupling-map ingestion
- Distributed multi-agent routing

## 8. Functional Requirements

FR-1 OpenEnv Interface

- The environment must implement:
  - reset(seed=None, episode_id=None, task_id=None)
  - step(action)
  - state

FR-2 Typed Contracts

- Action, Observation, and State must be typed with Pydantic-compatible models.

FR-3 Task Suite

- The environment must expose exactly three baseline tasks:
  - easy_line_routing
  - medium_heavyhex_routing
  - hard_drift_aware_routing

FR-4 Deterministic Graders

- Each task must have a deterministic grader returning score in [0.0, 1.0].

FR-5 Reward Shaping

- Step-level rewards must include:
  - progress reward
  - SWAP and noise costs
  - invalid action penalty
  - per-step latency penalty
- Terminal bonus or penalty must be applied based on completion quality.

FR-6 Episode Lifecycle

- Episodes end on completion, step-budget exhaustion, or explicit terminate action.

FR-7 Action Validation

- Invalid actions must be rejected, penalized, and counted.

FR-8 Reproducibility

- Given task_id, seed, and action sequence, resulting state and score must be deterministic.

FR-9 Baseline Inference

- Provide inference.py with OpenAI client usage and environment-variable configuration.

FR-10 Submission Logging

- inference.py must emit START, STEP, END lines in required format.

## 9. Non-Functional Requirements

NFR-1 Runtime Limits

- Must run within 2 vCPU and 8 GB RAM constraints.

NFR-2 Performance

- Target mean step latency below 50 ms for default tasks.

NFR-3 Determinism

- No nondeterministic external calls in step logic.

NFR-4 Deployment

- Must be containerized and runnable via docker build and docker run.

NFR-5 Maintainability

- Task fixtures, graders, and server logic must be modular and testable.

## 10. Product Workflow

1. reset() loads topology, circuit fixture, mapping, and noise profile.
2. Agent selects action from action mask.
3. step() validates and applies transition.
4. Observation updates depth, SWAP count, pending gates, and estimated success.
5. Dense reward emitted each step.
6. Terminal condition triggers final bonus and grader score.

## 11. Data and Model Contracts

Action fields:

- action_type: insert_swap | apply_gate | advance | terminate
- edge_u, edge_v for SWAP
- gate_index for apply_gate

Observation fields:

- task_id
- logical_to_physical
- pending_two_qubit_gates
- coupling_edges
- edge_error_rates
- depth
- swap_count
- estimated_success_prob
- action_mask
- done_reason

State fields:

- episode_id
- step_count
- task_id
- seed
- remaining_gates
- depth
- swap_count
- invalid_action_count
- cumulative_reward
- termination_status

## 12. Task Definitions and Acceptance Bands

Task A: easy_line_routing

- 8-qubit line topology
- Sparse interactions, low-noise edges
- Step budget: 80

Task B: medium_heavyhex_routing

- 27-qubit heavy-hex style subset
- Mixed local/non-local interactions
- Step budget: 160

Task C: hard_drift_aware_routing

- 27-qubit heavy-hex style subset
- Dense interactions with deterministic staged drift
- Step budget: 220

Suggested qualitative score bands:

- >= 0.80: strong
- 0.60 to < 0.80: acceptable baseline
- < 0.60: needs improvement

## 13. Grading and Reward Requirements

Grader formulas must be deterministic and use fixed normalization constants.

Dense reward must include:

- Positive signal for valid progress
- Cost for SWAP usage and noisy-edge exposure
- Penalty for invalid actions
- Per-step penalty to discourage loops
- Terminal quality adjustment

## 14. Compliance Requirements

The product must satisfy both the OpenEnv and submission guideline constraints:

1. Environment manifest present (openenv.yaml)
2. Deterministic tasks and graders
3. Baseline inference script using OpenAI client
4. Required environment variables in inference:
   - API_BASE_URL with default
   - MODEL_NAME with default
   - HF_TOKEN required
5. Logging format:
   - [START] task=... env=... model=...
   - [STEP] step=... action=... reward=... done=... error=...
   - [END] success=... steps=... rewards=...

## 15. Metrics and KPIs

Primary product KPIs:

- Mean normalized score per task
- Completion rate by task
- Mean SWAP count ratio
- Mean compiled depth ratio
- Invalid action rate
- Mean error exposure metric

Operational KPIs:

- Mean step latency
- Memory usage under reference load
- Deterministic replay pass rate

## 16. Milestones

M1 Scaffolding

- Models, manifest, package metadata, PRD and spec docs

M2 Core Logic

- Task fixtures, graders, routing transitions, rewards

M3 Server and Packaging

- app wiring, Dockerfile, local run checks

M4 Baseline and Validation

- inference.py execution, format verification, openenv validate

M5 Submission

- HF Space deployment, running-state verification, final score report

## 17. Risks and Mitigations

Risk: Reward exploitation via loops

- Mitigation: per-step penalty, invalid-action threshold, terminate penalties

Risk: Runtime over budget

- Mitigation: graph-based transitions only, no heavy simulation in step loop

Risk: Submission format failure

- Mitigation: strict logging helpers and automated output parser tests

Risk: Ambiguous credential naming

- Mitigation: support HF_TOKEN and OPENAI_API_KEY alias in script

## 18. Open Questions

1. Should hard task drift be stage-based or edge-specific per time index?
2. What baseline policy should be considered minimum acceptable for launch?
3. Should rubric_reward be mandatory in observation for all tasks?
4. What reproducibility seed set should be used for leaderboard reporting?

## 19. Launch Acceptance Criteria

The product is launch-ready when all are true:

1. All three tasks run end-to-end with deterministic outputs.
2. Graders always return values in [0.0, 1.0].
3. Dense rewards are emitted each step.
4. inference.py emits required START/STEP/END line formats.
5. Docker build and run succeed.
6. openenv validate passes.
7. Baseline score table is published in README.

## 20. Related Documents

- [README.md](README.md)
- [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md)
- [DESIGN_SPEC.md](DESIGN_SPEC.md)
- [TASK_SUITE_AND_GRADERS.md](TASK_SUITE_AND_GRADERS.md)
- [REWARD_AND_RUBRIC.md](REWARD_AND_RUBRIC.md)
- [COMPLIANCE_MATRIX.md](COMPLIANCE_MATRIX.md)
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- [SUBMISSION_RUNBOOK.md](SUBMISSION_RUNBOOK.md)
