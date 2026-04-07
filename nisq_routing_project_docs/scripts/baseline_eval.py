from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Dict, List

from server.nisq_routing_environment import NISQRoutingEnvironment
from server.tasks import build_task_registry
from tests.helpers import greedy_routing_action

OUTPUT_PATH = Path("baseline_results.json")
SEEDS = [7, 13, 29]


def run_task_episode(task_id: str, seed: int) -> Dict[str, float]:
    env = NISQRoutingEnvironment()
    obs = env.reset(task_id=task_id, seed=seed)

    rewards: List[float] = []
    steps = 0

    max_steps = build_task_registry()[task_id].max_steps

    while not obs.done and steps < max_steps:
        steps += 1
        action = greedy_routing_action(obs)
        obs = env.step(action)
        rewards.append(float(obs.reward or 0.0))

    return {
        "task_id": task_id,
        "seed": seed,
        "done": 1.0 if obs.done else 0.0,
        "completed": 1.0 if obs.done_reason == "completed" else 0.0,
        "steps": float(steps),
        "total_reward": float(sum(rewards)),
        "rubric_score": float(obs.rubric_reward or 0.0),
        "swap_count": float(obs.swap_count),
        "depth": float(obs.depth),
        "success_prob": float(obs.estimated_success_prob),
    }


def summarize(records: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    grouped: Dict[str, List[Dict[str, float]]] = {}
    for rec in records:
        grouped.setdefault(str(rec["task_id"]), []).append(rec)

    summary: Dict[str, Dict[str, float]] = {}
    for task_id, rows in grouped.items():
        summary[task_id] = {
            "episodes": float(len(rows)),
            "completion_rate": mean(r["completed"] for r in rows),
            "avg_steps": mean(r["steps"] for r in rows),
            "avg_total_reward": mean(r["total_reward"] for r in rows),
            "avg_rubric_score": mean(r["rubric_score"] for r in rows),
            "avg_swap_count": mean(r["swap_count"] for r in rows),
            "avg_depth": mean(r["depth"] for r in rows),
            "avg_success_prob": mean(r["success_prob"] for r in rows),
        }

    return summary


def main() -> None:
    tasks = list(build_task_registry().keys())

    records: List[Dict[str, float]] = []
    for task_id in tasks:
        for seed in SEEDS:
            records.append(run_task_episode(task_id=task_id, seed=seed))

    summary = summarize(records)

    payload = {
        "seeds": SEEDS,
        "records": records,
        "summary": summary,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Task,CompletionRate,AvgRubric,AvgReward,AvgSteps")
    for task_id in tasks:
        s = summary[task_id]
        print(
            f"{task_id},{s['completion_rate']:.2f},{s['avg_rubric_score']:.3f},"
            f"{s['avg_total_reward']:.3f},{s['avg_steps']:.1f}"
        )

    print(f"\\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
