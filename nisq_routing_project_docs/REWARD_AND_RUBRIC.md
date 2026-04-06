# Reward and Rubric Design

## Reward goals

The reward should provide dense feedback for routing quality while preserving a deterministic terminal score.

## Step-level reward (dense)

At each step t:

r_t = progress_reward - swap_cost - invalid_penalty - latency_penalty

### Components

- progress_reward:
  - +0.08 for valid apply_gate that advances required gate sequence
  - +0.02 for valid mapping-preserving advance action
- swap_cost:
  - 0.03 base cost per SWAP
  - plus 0.05 * selected_edge_error_rate to discourage noisy edges
- invalid_penalty:
  - -0.20 for invalid or infeasible action
- latency_penalty:
  - -0.005 per step to encourage shorter solutions

## Terminal reward (quality)

On completion:

terminal_bonus = +0.60 * grader_score

On timeout or forced termination without completion:

terminal_bonus = -0.30

Total episodic return:

R = sum_t(r_t) + terminal_bonus

## Rubric output

The grader score is deterministic and normalized to [0.0, 1.0], using formulas in [TASK_SUITE_AND_GRADERS.md](TASK_SUITE_AND_GRADERS.md).

The environment should expose:

- raw step reward in observation.reward
- rubric score in observation.rubric_reward (optional but recommended)

## Anti-exploit constraints

- Maximum invalid action threshold before hard termination
- No-op loops receive only latency penalty and no progress reward
- terminate action before completion incurs terminal penalty

## Calibration plan

1. Run random and heuristic baselines to estimate score distribution.
2. Tune coefficients so random policy mean score remains below 0.35.
3. Ensure a deterministic greedy baseline reaches at least 0.60 on easy and medium tasks.
4. Verify reward scale consistency across task difficulty.
