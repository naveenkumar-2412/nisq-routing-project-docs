from __future__ import annotations

from typing import Dict, List, Literal, Optional

from openenv.core.env_server import Action, Observation, State
from pydantic import Field

ActionType = Literal["insert_swap", "apply_gate", "advance", "terminate"]


class NISQRoutingAction(Action):
    """Action model for NISQ adaptive qubit routing."""

    action_type: ActionType = "advance"
    edge_u: Optional[int] = None
    edge_v: Optional[int] = None
    gate_index: Optional[int] = 0


class NISQRoutingObservation(Observation):
    """Observation model for NISQ adaptive qubit routing."""

    task_id: str = ""
    logical_to_physical: List[int] = Field(default_factory=list)
    pending_two_qubit_gates: List[List[int]] = Field(default_factory=list)
    coupling_edges: List[List[int]] = Field(default_factory=list)
    edge_error_rates: List[float] = Field(default_factory=list)
    depth: int = 0
    swap_count: int = 0
    estimated_success_prob: float = 1.0
    action_mask: Dict[str, bool] = Field(default_factory=dict)
    done_reason: str = ""
    last_action_error: Optional[str] = None
    rubric_reward: Optional[float] = None


class NISQRoutingState(State):
    """State model for NISQ adaptive qubit routing."""

    task_id: str = ""
    seed: int = 0
    remaining_gates: int = 0
    depth: int = 0
    swap_count: int = 0
    invalid_action_count: int = 0
    cumulative_reward: float = 0.0
    termination_status: str = "running"
    estimated_success_prob: float = 1.0
    logical_to_physical: List[int] = Field(default_factory=list)
    pending_gate_sequence: List[List[int]] = Field(default_factory=list)
    current_edge_errors: List[float] = Field(default_factory=list)
