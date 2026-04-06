from __future__ import annotations

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

try:
    from .models import NISQRoutingAction, NISQRoutingObservation, NISQRoutingState
except ImportError:
    from models import NISQRoutingAction, NISQRoutingObservation, NISQRoutingState


class NISQRoutingEnv(EnvClient[NISQRoutingAction, NISQRoutingObservation, NISQRoutingState]):
    """Client for the NISQ adaptive qubit routing environment."""

    def _step_payload(self, action: NISQRoutingAction) -> dict:
        return action.model_dump(exclude_none=True)

    def _parse_result(self, payload: dict) -> StepResult[NISQRoutingObservation]:
        obs = NISQRoutingObservation(**payload["observation"])
        return StepResult(
            observation=obs,
            reward=payload.get("reward"),
            done=payload.get("done", False),
            info=payload.get("info", {}),
        )

    def _parse_state(self, payload: dict) -> NISQRoutingState:
        return NISQRoutingState(**payload)
