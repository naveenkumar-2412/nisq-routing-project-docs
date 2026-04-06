from __future__ import annotations

import os

from openenv.core.env_server import create_app

try:
    from ..models import NISQRoutingAction, NISQRoutingObservation
    from .nisq_routing_environment import NISQRoutingEnvironment
except ImportError:
    from models import NISQRoutingAction, NISQRoutingObservation
    from server.nisq_routing_environment import NISQRoutingEnvironment


def create_nisq_environment() -> NISQRoutingEnvironment:
    task_id = os.getenv("NISQ_DEFAULT_TASK", "easy_line_routing")
    seed = int(os.getenv("NISQ_SEED", "7"))
    return NISQRoutingEnvironment(default_task_id=task_id, seed=seed)


app = create_app(
    create_nisq_environment,
    NISQRoutingAction,
    NISQRoutingObservation,
    env_name="nisq_routing_env",
)


def main() -> None:
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
