# Compliance Matrix

This matrix maps extracted hackathon requirements to concrete artifacts in this project folder.

## Functional requirements from problem statement PDF

| Requirement | Source | Planned evidence |
|---|---|---|
| Real-world task simulation (no toy/game) | Problem Statement PDF | [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md), [README.md](README.md) |
| OpenEnv interface with typed models and reset/step/state | Problem Statement PDF | [DESIGN_SPEC.md](DESIGN_SPEC.md), [models.py](models.py) |
| openenv.yaml metadata present | Problem Statement PDF | [openenv.yaml](openenv.yaml) |
| Minimum 3 tasks with easy/medium/hard progression | Problem Statement PDF | [TASK_SUITE_AND_GRADERS.md](TASK_SUITE_AND_GRADERS.md) |
| Programmatic deterministic grader in [0,1] | Problem Statement PDF | [TASK_SUITE_AND_GRADERS.md](TASK_SUITE_AND_GRADERS.md) |
| Meaningful incremental reward and penalties | Problem Statement PDF | [REWARD_AND_RUBRIC.md](REWARD_AND_RUBRIC.md) |
| Baseline inference script with OpenAI client | Problem Statement PDF | [inference.py](inference.py), [SUBMISSION_RUNBOOK.md](SUBMISSION_RUNBOOK.md) |
| Deployable containerized environment | Problem Statement PDF | [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) (Milestone 4) |
| README includes overview, action/observation, tasks, setup, baseline | Problem Statement PDF | [README.md](README.md) |

## Additional submission constraints from guidelines PDF

| Requirement | Source | Planned evidence |
|---|---|---|
| inference.py at project root | Guidelines PDF | [inference.py](inference.py) |
| API_BASE_URL must have default | Guidelines PDF | [inference.py](inference.py) |
| MODEL_NAME must have default | Guidelines PDF | [inference.py](inference.py) |
| HF_TOKEN required | Guidelines PDF | [inference.py](inference.py) |
| Required START/STEP/END stdout line format | Guidelines PDF | [inference.py](inference.py), [SUBMISSION_RUNBOOK.md](SUBMISSION_RUNBOOK.md) |
| Space must be in Running state at submit time | Guidelines PDF | [SUBMISSION_RUNBOOK.md](SUBMISSION_RUNBOOK.md) |
| Runtime must fit 2 vCPU and 8 GB RAM | Guidelines PDF | [DESIGN_SPEC.md](DESIGN_SPEC.md), [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) |

## Credential naming note

The two PDFs mention different credential names in different places. To reduce integration risk, [inference.py](inference.py) supports both:

- HF_TOKEN (primary)
- OPENAI_API_KEY (fallback alias)
