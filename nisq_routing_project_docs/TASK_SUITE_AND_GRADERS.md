# Task Suite and Deterministic Graders

## Task design principles

- Real compiler-style routing decisions only
- Difficulty scales by topology complexity, gate density, and noise variability
- Deterministic seeds and fixtures for reproducibility

## Task 1: easy_line_routing

### Setup

- Topology: 8-qubit line graph
- Circuit: sparse two-qubit gate chain with short interaction distance
- Error profile: near-uniform low error rates
- Step budget: 80

### Objective

Complete all logical two-qubit gates with minimal SWAP overhead.

### Grader

score_easy = clip(1 - (0.45 * swap_ratio + 0.35 * depth_ratio + 0.20 * invalid_ratio), 0, 1)

Where:

- swap_ratio = swap_count / swap_budget_easy
- depth_ratio = compiled_depth / target_depth_easy
- invalid_ratio = invalid_actions / step_budget

## Task 2: medium_heavyhex_routing

### Setup

- Topology: 27-qubit heavy-hex style graph subset
- Circuit: mixed local and non-local two-qubit gates
- Error profile: heterogeneous edges with low and medium quality links
- Step budget: 160

### Objective

Trade off route length and edge quality while finishing within budget.

### Grader

score_medium = clip(1 - (0.35 * swap_ratio + 0.30 * depth_ratio + 0.25 * error_exposure + 0.10 * invalid_ratio), 0, 1)

Where:

- error_exposure = normalized sum of edge error for executed two-qubit gates

## Task 3: hard_drift_aware_routing

### Setup

- Topology: 27-qubit heavy-hex style graph subset
- Circuit: dense two-qubit interaction program
- Error profile: deterministic time-varying edge quality by stage
- Step budget: 220

### Objective

Adapt routing policy to staged drift while preserving completion and quality.

### Grader

score_hard = clip(1 - (0.30 * swap_ratio + 0.25 * depth_ratio + 0.30 * error_exposure + 0.15 * timeout_penalty), 0, 1)

Where:

- timeout_penalty = 1.0 if not completed else 0.0

## Shared deterministic grader properties

1. All formulas are deterministic and closed-form.
2. All normalization constants are fixed in task fixtures.
3. Each score is clamped to [0.0, 1.0].
4. Scores are reproducible for a given seed and action trajectory.

## Pass/fail interpretation for reporting

- score >= 0.80: strong routing quality
- 0.60 <= score < 0.80: acceptable baseline quality
- score < 0.60: needs policy improvement

## Evaluation output schema

Per episode evaluator output:

- task_id
- seed
- completed (bool)
- score (float in [0,1])
- swap_count
- compiled_depth
- invalid_actions
- error_exposure
