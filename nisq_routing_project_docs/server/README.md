# Server Implementation Notes

This folder is reserved for the OpenEnv server implementation.

Planned files:

- app.py: FastAPI app wiring using create_fastapi_app
- nisq_routing_environment.py: core environment dynamics
- tasks.py: deterministic task fixtures
- graders.py: deterministic scoring functions in [0,1]
- Dockerfile: deployable runtime image for Hugging Face Spaces

Key implementation constraints:

1. Keep runtime compatible with 2 vCPU and 8 GB RAM.
2. Preserve deterministic behavior for same seed and action sequence.
3. Expose action masks to prevent invalid routing operations.
4. Keep step logic lightweight and graph-based.
