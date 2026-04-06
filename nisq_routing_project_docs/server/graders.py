from __future__ import annotations

from typing import Dict

from .tasks import NISQTask


def _clip_01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def compute_task_score(task: NISQTask, metrics: Dict[str, float]) -> float:
    swap_count = float(metrics.get("swap_count", 0.0))
    depth = float(metrics.get("depth", 0.0))
    invalid_actions = float(metrics.get("invalid_actions", 0.0))
    error_exposure = float(metrics.get("error_exposure", 0.0))
    completed = bool(metrics.get("completed", False))

    swap_ratio = swap_count / max(1.0, float(task.swap_budget))
    depth_ratio = depth / max(1.0, float(task.target_depth))
    invalid_ratio = invalid_actions / max(1.0, float(task.max_steps))
    timeout_penalty = 0.0 if completed else 1.0

    if task.task_id == "easy_line_routing":
        score = 1.0 - (0.45 * swap_ratio + 0.35 * depth_ratio + 0.20 * invalid_ratio)
    elif task.task_id == "medium_heavyhex_routing":
        score = 1.0 - (
            0.35 * swap_ratio
            + 0.30 * depth_ratio
            + 0.25 * error_exposure
            + 0.10 * invalid_ratio
        )
    elif task.task_id == "hard_drift_aware_routing":
        score = 1.0 - (
            0.30 * swap_ratio
            + 0.25 * depth_ratio
            + 0.30 * error_exposure
            + 0.15 * timeout_penalty
        )
    else:
        score = 1.0 - (0.4 * swap_ratio + 0.4 * depth_ratio + 0.2 * invalid_ratio)

    return _clip_01(score)
