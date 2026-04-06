# Implementation Plan

## Milestone 1: Scaffolding and contracts

Deliverables:

- models.py with typed Action, Observation, State
- openenv.yaml manifest
- package metadata and basic README

Exit criteria:

- Static import checks pass
- Model schema fields reviewed

## Milestone 2: Task registry and graders

Deliverables:

- server/tasks.py with fixed fixtures for easy, medium, hard
- server/graders.py with deterministic scoring formulas

Exit criteria:

- Reproducibility checks over multiple seeds
- Grader outputs always in [0.0, 1.0]

## Milestone 3: Core environment dynamics

Deliverables:

- server/nisq_routing_environment.py implementing reset, step, state
- Action validation and state transitions
- Reward integration from [REWARD_AND_RUBRIC.md](REWARD_AND_RUBRIC.md)

Exit criteria:

- Episodes terminate correctly for completion and timeout
- Invalid actions penalized as specified

## Milestone 4: Server wiring and local run

Deliverables:

- server/app.py with create_fastapi_app
- Dockerfile for container execution

Exit criteria:

- docker build and docker run succeed
- health endpoint responds

## Milestone 5: Client and baseline

Deliverables:

- client.py for EnvClient integration
- inference.py using OpenAI client and required output format

Exit criteria:

- Baseline run executes all tasks and logs START/STEP/END lines

## Milestone 6: Validation and submission

Deliverables:

- openenv validate pass
- Hugging Face Space deployment and running status
- Final baseline score report in README

Exit criteria:

- Submission checklist in [SUBMISSION_RUNBOOK.md](SUBMISSION_RUNBOOK.md) fully complete

## Risk register

1. Overly expensive simulation: keep state updates lightweight and graph-based.
2. Reward hacking: enforce action masks and anti-loop penalties.
3. Submission failure due to formatting: use strict logging helpers in inference.py.
4. Credential mismatch across docs: support both HF_TOKEN and OPENAI_API_KEY aliases.
