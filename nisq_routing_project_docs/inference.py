#!/usr/bin/env python3
"""Baseline inference for NISQ routing with required submission logging format."""

from __future__ import annotations

import json
import os
from typing import List, Optional

from openai import OpenAI

try:
    from .client import NISQRoutingEnv
    from .models import NISQRoutingAction, NISQRoutingObservation
except ImportError:
    from client import NISQRoutingEnv
    from models import NISQRoutingAction, NISQRoutingObservation

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
TASKS = [
    item.strip()
    for item in os.getenv(
        "TASKS",
        "easy_line_routing,medium_heavyhex_routing,hard_drift_aware_routing",
    ).split(",")
    if item.strip()
]
MAX_STEPS = int(os.getenv("MAX_STEPS", "220"))

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")


def _format_error(value: Optional[str]) -> str:
    if value is None or value == "":
        return "null"
    return value.replace("\n", " ").strip()


def _emit_start(task: str, model: str) -> None:
    print(f"[START] task={task} env=nisq_routing_env model={model}")


def _emit_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={_format_error(error)}"
    )


def _emit_end(success: bool, steps: int, rewards: List[float]) -> None:
    reward_str = ",".join(f"{value:.2f}" for value in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={reward_str}")


def _find_json_object(text: str) -> Optional[dict]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _heuristic_action(obs: NISQRoutingObservation) -> NISQRoutingAction:
    if obs.action_mask.get("apply_gate", False):
        return NISQRoutingAction(action_type="apply_gate", gate_index=0)
    if obs.action_mask.get("insert_swap", False) and obs.coupling_edges:
        u, v = obs.coupling_edges[0]
        return NISQRoutingAction(action_type="insert_swap", edge_u=u, edge_v=v)
    return NISQRoutingAction(action_type="advance")


def _llm_action(client: OpenAI, obs: NISQRoutingObservation) -> NISQRoutingAction:
    prompt = (
        "Return exactly one JSON object with keys: action_type, edge_u, edge_v, gate_index. "
        "Valid action_type values are insert_swap, apply_gate, advance, terminate. "
        "Use null for unused fields.\n"
        f"task_id={obs.task_id}\n"
        f"depth={obs.depth} swap_count={obs.swap_count} remaining_gates={len(obs.pending_two_qubit_gates)}\n"
        f"action_mask={obs.action_mask}\n"
        f"first_pending_gates={obs.pending_two_qubit_gates[:3]}\n"
        f"sample_edges={obs.coupling_edges[:8]}\n"
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are an RL routing policy assistant. Return valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=120,
    )

    content = response.choices[0].message.content or ""
    parsed = _find_json_object(content)
    if not parsed:
        return _heuristic_action(obs)

    action_type = parsed.get("action_type", "advance")
    try:
        return NISQRoutingAction(
            action_type=action_type,
            edge_u=parsed.get("edge_u"),
            edge_v=parsed.get("edge_v"),
            gate_index=parsed.get("gate_index", 0),
        )
    except Exception:
        return _heuristic_action(obs)


def _run_task(client: OpenAI, task_name: str) -> None:
    rewards: List[float] = []
    success = False
    steps = 0

    _emit_start(task=task_name, model=MODEL_NAME)

    try:
        with NISQRoutingEnv(base_url=ENV_BASE_URL).sync() as env:
            result = env.reset(task_id=task_name)

            for step in range(1, MAX_STEPS + 1):
                steps = step
                action = _llm_action(client, result.observation)
                result = env.step(action)

                reward = float(result.reward or 0.0)
                rewards.append(reward)

                action_text = action.action_type
                if action.action_type == "insert_swap":
                    action_text = f"insert_swap({action.edge_u},{action.edge_v})"
                elif action.action_type == "apply_gate":
                    action_text = f"apply_gate({action.gate_index or 0})"

                error = getattr(result.observation, "last_action_error", None)
                _emit_step(
                    step=step,
                    action=action_text,
                    reward=reward,
                    done=bool(result.done),
                    error=error,
                )

                if result.done:
                    success = getattr(result.observation, "done_reason", "") == "completed"
                    break

    except Exception as exc:
        if steps == 0:
            steps = 1
            rewards = [0.0]
        _emit_step(
            step=steps,
            action="exception",
            reward=rewards[-1],
            done=True,
            error=str(exc),
        )
        success = False

    finally:
        _emit_end(success=success, steps=steps, rewards=rewards)


def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    for task_name in TASKS:
        _run_task(client, task_name)


if __name__ == "__main__":
    main()
