# Submission Runbook

Use this checklist before final hackathon submission.

## 1. Root file layout

Required in project root:

- inference.py
- openenv.yaml
- README.md
- server/Dockerfile

This folder is prepared so it can be used directly as a standalone project root.

## 2. Baseline inference requirements

inference.py must:

1. Use OpenAI client for LLM calls.
2. Read API_BASE_URL with a default value.
3. Read MODEL_NAME with a default value.
4. Read HF_TOKEN as required token.
5. Optionally accept OPENAI_API_KEY as fallback for compatibility.

## 3. Mandatory stdout format

The script must emit exactly these line types in order:

1. [START] task=<task_name> env=<benchmark> model=<model_name>
2. [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
3. [END] success=<true|false> steps=<n> rewards=<r1,r2,...,rn>

Rules:

- Emit one START line per episode.
- Emit one STEP line after every env.step() call.
- Always emit END line, including exceptions.
- reward and rewards use 2 decimal places.
- done and success are lowercase true or false.

## 4. Local verification steps

1. Run unit tests for environment dynamics and graders.
2. Run openenv validate.
3. Execute inference.py on all tasks.
4. Confirm output format with a line parser.
5. Build and run Docker image locally.

## 5. Hugging Face deployment checks

1. Push environment to Hugging Face Space.
2. Ensure Space status is Running before submission.
3. Keep only required spaces active to avoid startup delays.
4. Re-submit after fixes if validation fails.

## 6. Performance and resource guardrails

Target runtime limits from guidelines:

- 2 vCPU
- 8 GB RAM

Actions:

- Use lightweight graph updates in step() logic.
- Avoid heavy quantum simulation in online episode loop.
- Keep dependencies minimal and pinned.

## 7. Final pre-submit checklist

- [x] README complete with baseline score table
- [x] Three tasks configured and reproducible
- [x] Deterministic graders output [0,1]
- [x] Reward shaping enabled and tested
- [x] inference.py logs START/STEP/END exactly
- [ ] Docker build and run verified
- [ ] Space is Running

## 8. Current status snapshot

- Tests: 9 passed with pytest.
- Validation: openenv validate returned OK.
- Baseline: generated in baseline_results.json.
- Docker verification attempt: Docker CLI present, but daemon was not running in this session.
- Remaining external actions: start Docker daemon, verify container runtime, and confirm Hugging Face Space is Running.
