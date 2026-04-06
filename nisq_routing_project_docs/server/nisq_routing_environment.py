from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Tuple

from openenv.core.env_server import Environment

try:
    from ..models import NISQRoutingAction, NISQRoutingObservation, NISQRoutingState
    from .graders import compute_task_score
    from .tasks import NISQTask, build_task_registry, canonical_edge
except ImportError:
    from models import NISQRoutingAction, NISQRoutingObservation, NISQRoutingState
    from server.graders import compute_task_score
    from server.tasks import NISQTask, build_task_registry, canonical_edge

Edge = Tuple[int, int]


class NISQRoutingEnvironment(
    Environment[NISQRoutingAction, NISQRoutingObservation, NISQRoutingState]
):
    """Deterministic NISQ routing environment with dense reward and rubric scoring."""

    def __init__(self, default_task_id: str = "easy_line_routing", seed: int = 7):
        super().__init__()
        self._registry = build_task_registry()
        self._default_task_id = (
            default_task_id if default_task_id in self._registry else "easy_line_routing"
        )
        self._default_seed = seed

        self._task: Optional[NISQTask] = None
        self._state: Optional[NISQRoutingState] = None
        self._executed_edge_errors: List[float] = []

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs,
    ) -> NISQRoutingObservation:
        selected_task_id = task_id or kwargs.get("task_name") or self._default_task_id
        self._task = self._registry.get(selected_task_id, self._registry[self._default_task_id])

        run_seed = self._default_seed if seed is None else int(seed)

        self._executed_edge_errors = []
        self._state = NISQRoutingState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=self._task.task_id,
            seed=run_seed,
            remaining_gates=len(self._task.gate_sequence),
            depth=0,
            swap_count=0,
            invalid_action_count=0,
            cumulative_reward=0.0,
            termination_status="running",
            estimated_success_prob=1.0,
            logical_to_physical=self._task.initial_mapping[:],
            pending_gate_sequence=[[a, b] for a, b in self._task.gate_sequence],
            current_edge_errors=self._edge_error_snapshot(step=0),
        )

        return self._make_observation(
            reward=0.0,
            done=False,
            done_reason="",
            error=None,
            rubric_reward=None,
        )

    def step(self, action: NISQRoutingAction, **kwargs) -> NISQRoutingObservation:
        _ = kwargs

        if self._state is None or self._task is None:
            return self.reset()

        if self._state.termination_status != "running":
            return self._make_observation(
                reward=0.0,
                done=True,
                done_reason=self._state.termination_status,
                error="episode_already_terminated",
                rubric_reward=None,
            )

        st = self._state
        task = self._task

        st.step_count += 1
        reward = -0.005
        error: Optional[str] = None
        done = False
        done_reason = ""
        rubric_reward: Optional[float] = None

        if action.action_type == "insert_swap":
            delta, error = self._handle_insert_swap(action)
            reward += delta
        elif action.action_type == "apply_gate":
            delta, error = self._handle_apply_gate(action)
            reward += delta
        elif action.action_type == "advance":
            delta, error = self._handle_advance()
            reward += delta
        elif action.action_type == "terminate":
            done = True
            done_reason = "terminated_by_agent"
            reward -= 0.30
        else:
            reward -= 0.20
            error = "unsupported_action_type"
            st.invalid_action_count += 1

        if error:
            st.invalid_action_count += 1

        if not done and st.remaining_gates == 0:
            done = True
            done_reason = "completed"

        if not done and st.invalid_action_count >= 5:
            done = True
            done_reason = "invalid_action_limit"
            reward -= 0.30

        if not done and st.step_count >= task.max_steps:
            done = True
            done_reason = "timeout"
            reward -= 0.30

        if done:
            rubric_reward = self._compute_rubric_score(completed=done_reason == "completed")
            if done_reason == "completed":
                reward += 0.60 * rubric_reward

        st.cumulative_reward += reward
        st.current_edge_errors = self._edge_error_snapshot(step=st.step_count)
        st.termination_status = done_reason if done else "running"

        return self._make_observation(
            reward=reward,
            done=done,
            done_reason=done_reason,
            error=error,
            rubric_reward=rubric_reward,
        )

    @property
    def state(self) -> NISQRoutingState:
        if self._state is None:
            return NISQRoutingState()
        return self._state

    def _handle_insert_swap(self, action: NISQRoutingAction) -> Tuple[float, Optional[str]]:
        st = self._state
        task = self._task

        if action.edge_u is None or action.edge_v is None:
            return -0.20, "swap_requires_edge_u_and_edge_v"

        u, v = int(action.edge_u), int(action.edge_v)
        if u == v:
            return -0.20, "swap_edge_endpoints_must_differ"

        edge = canonical_edge(u, v)
        if edge not in task.coupling_edges:
            return -0.20, "edge_not_in_coupling_graph"

        self._swap_physical_positions(u, v)
        st.swap_count += 1
        st.depth += 3

        edge_error = task.edge_error_at(st.step_count, edge)
        self._executed_edge_errors.append(edge_error)

        # Cost for swap plus a noise-aware penalty.
        return -(0.03 + 0.05 * edge_error), None

    def _handle_apply_gate(self, action: NISQRoutingAction) -> Tuple[float, Optional[str]]:
        st = self._state
        task = self._task

        if not st.pending_gate_sequence:
            return -0.20, "no_pending_gates"

        gate_index = int(action.gate_index or 0)
        if gate_index != 0:
            return -0.20, "only_front_gate_is_executable"

        logical_a, logical_b = st.pending_gate_sequence[0]
        physical_a = st.logical_to_physical[logical_a]
        physical_b = st.logical_to_physical[logical_b]
        edge = canonical_edge(physical_a, physical_b)

        if edge not in task.coupling_edges:
            return -0.20, "gate_qubits_not_adjacent"

        edge_error = task.edge_error_at(st.step_count, edge)
        self._executed_edge_errors.append(edge_error)

        st.pending_gate_sequence.pop(0)
        st.remaining_gates -= 1
        st.depth += 1
        st.estimated_success_prob = max(
            0.0, min(1.0, st.estimated_success_prob * (1.0 - edge_error))
        )

        # Progress reward minus noise-aware penalty.
        return 0.08 - (0.05 * edge_error), None

    def _handle_advance(self) -> Tuple[float, Optional[str]]:
        if self._is_front_gate_executable():
            return 0.02, None
        return -0.01, None

    def _swap_physical_positions(self, u: int, v: int) -> None:
        st = self._state

        idx_u = st.logical_to_physical.index(u)
        idx_v = st.logical_to_physical.index(v)
        st.logical_to_physical[idx_u], st.logical_to_physical[idx_v] = (
            st.logical_to_physical[idx_v],
            st.logical_to_physical[idx_u],
        )

    def _is_front_gate_executable(self) -> bool:
        st = self._state
        task = self._task

        if not st.pending_gate_sequence:
            return False

        logical_a, logical_b = st.pending_gate_sequence[0]
        physical_a = st.logical_to_physical[logical_a]
        physical_b = st.logical_to_physical[logical_b]
        return canonical_edge(physical_a, physical_b) in task.coupling_edges

    def _edge_error_snapshot(self, step: int) -> List[float]:
        task = self._task
        return [task.edge_error_at(step, edge) for edge in task.coupling_edges]

    def _compute_rubric_score(self, completed: bool) -> float:
        st = self._state
        task = self._task

        normalization = max(1, len(task.gate_sequence) + task.swap_budget)
        error_exposure = min(1.0, sum(self._executed_edge_errors) / normalization)

        metrics: Dict[str, float] = {
            "swap_count": float(st.swap_count),
            "depth": float(st.depth),
            "invalid_actions": float(st.invalid_action_count),
            "error_exposure": float(error_exposure),
            "completed": 1.0 if completed else 0.0,
        }
        return compute_task_score(task, metrics)

    def _make_observation(
        self,
        reward: float,
        done: bool,
        done_reason: str,
        error: Optional[str],
        rubric_reward: Optional[float],
    ) -> NISQRoutingObservation:
        st = self._state
        task = self._task

        pending_window = st.pending_gate_sequence[:5]
        action_mask = {
            "insert_swap": True,
            "apply_gate": self._is_front_gate_executable(),
            "advance": True,
            "terminate": True,
        }

        return NISQRoutingObservation(
            task_id=st.task_id,
            logical_to_physical=st.logical_to_physical[:],
            pending_two_qubit_gates=[gate[:] for gate in pending_window],
            coupling_edges=[list(edge) for edge in task.coupling_edges],
            edge_error_rates=st.current_edge_errors[:],
            depth=st.depth,
            swap_count=st.swap_count,
            estimated_success_prob=st.estimated_success_prob,
            action_mask=action_mask,
            done_reason=done_reason,
            last_action_error=error,
            rubric_reward=rubric_reward,
            reward=reward,
            done=done,
        )
