# Technical Design Specification

## 1. OpenEnv interface contract

The environment will implement:

- reset(seed=None, episode_id=None, task_id=None) -> NISQRoutingObservation
- step(action: NISQRoutingAction) -> NISQRoutingObservation
- state -> NISQRoutingState

Reward and done are returned as part of OpenEnv Observation semantics.

## 2. Core models

Canonical model definitions live in [models.py](models.py).

### 2.1 Action model

NISQRoutingAction fields:

- action_type: one of insert_swap, apply_gate, advance, terminate
- edge_u, edge_v: physical qubit ids for SWAP actions
- gate_index: index into pending gate window for apply_gate

### 2.2 Observation model

NISQRoutingObservation fields:

- task_id: active benchmark task
- logical_to_physical: current mapping vector
- pending_two_qubit_gates: next gate window as logical qubit pairs
- coupling_edges: hardware edges
- edge_error_rates: per-edge error estimate
- depth: compiled depth so far
- swap_count: number of inserted SWAPs
- estimated_success_prob: cumulative modeled success estimate
- action_mask: boolean validity mask per action type
- done_reason: empty until terminal

### 2.3 State model

NISQRoutingState fields:

- episode_id, step_count
- task_id, seed
- remaining_gates
- depth, swap_count
- invalid_action_count
- cumulative_reward
- termination_status

## 3. Environment dynamics

1. reset() loads a deterministic circuit/topology pair from task registry.
2. step() validates action against current state.
3. Valid SWAP updates mapping and depth.
4. Valid apply_gate consumes next logical interaction when physically adjacent.
5. Invalid actions receive penalties and may end episode after threshold.
6. Episode ends on completion, step budget exhaustion, or terminate.

## 4. Determinism and reproducibility

- Task definitions are static fixtures.
- Seed controls any stochastic noise perturbation.
- Grader uses deterministic arithmetic only.
- No external API calls inside environment step logic.

## 5. System boundaries

In scope:

- Routing-level optimization with modeled edge errors
- Task registry and deterministic graders
- Runtime bounded for 2 vCPU and 8 GB RAM constraints

Out of scope:

- Pulse-level calibration loops
- Full quantum statevector simulation for large circuits

## 6. Runtime profile target

- Mean step latency target: less than 50 ms on reference container
- Memory target: less than 1.5 GB for default task sizes

## 7. Planned server components

- server/app.py: create_fastapi_app wiring
- server/nisq_routing_environment.py: main environment implementation
- server/graders.py: deterministic scorers
- server/tasks.py: fixed task fixtures
