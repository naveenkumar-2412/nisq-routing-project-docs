from __future__ import annotations

from server.graders import compute_task_score
from server.tasks import build_task_registry


def test_grader_outputs_are_clamped() -> None:
    tasks = build_task_registry()

    for task in tasks.values():
        score = compute_task_score(
            task,
            {
                "swap_count": 10_000,
                "depth": 10_000,
                "invalid_actions": 10_000,
                "error_exposure": 10.0,
                "completed": 0.0,
            },
        )
        assert 0.0 <= score <= 1.0


def test_completed_episode_scores_higher_than_timeout_for_easy() -> None:
    task = build_task_registry()["easy_line_routing"]

    completed = compute_task_score(
        task,
        {
            "swap_count": 4,
            "depth": 12,
            "invalid_actions": 0,
            "error_exposure": 0.08,
            "completed": 1.0,
        },
    )

    timeout = compute_task_score(
        task,
        {
            "swap_count": 20,
            "depth": 45,
            "invalid_actions": 8,
            "error_exposure": 0.35,
            "completed": 0.0,
        },
    )

    assert completed > timeout
