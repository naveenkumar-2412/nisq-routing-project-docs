from __future__ import annotations

from server.tasks import build_task_registry


def test_task_registry_has_expected_entries() -> None:
    tasks = build_task_registry()
    assert set(tasks.keys()) == {
        "easy_line_routing",
        "medium_heavyhex_routing",
        "hard_drift_aware_routing",
    }


def test_task_shapes_and_budgets() -> None:
    tasks = build_task_registry()

    easy = tasks["easy_line_routing"]
    medium = tasks["medium_heavyhex_routing"]
    hard = tasks["hard_drift_aware_routing"]

    assert easy.num_qubits == 8
    assert medium.num_qubits == 27
    assert hard.num_qubits == 27

    assert easy.max_steps < medium.max_steps < hard.max_steps
    assert easy.swap_budget < medium.swap_budget < hard.swap_budget


def test_hard_task_has_drift_profile() -> None:
    hard = build_task_registry()["hard_drift_aware_routing"]
    sample_edge = hard.coupling_edges[0]

    early = hard.edge_error_at(0, sample_edge)
    mid = hard.edge_error_at(80, sample_edge)
    late = hard.edge_error_at(180, sample_edge)

    assert early != mid
    assert late != mid
