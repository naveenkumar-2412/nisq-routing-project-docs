from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

Edge = Tuple[int, int]
Gate = Tuple[int, int]


def canonical_edge(u: int, v: int) -> Edge:
    return (u, v) if u <= v else (v, u)


@dataclass(frozen=True)
class NISQTask:
    task_id: str
    difficulty: str
    num_qubits: int
    coupling_edges: List[Edge]
    base_edge_errors: Dict[Edge, float]
    initial_mapping: List[int]
    gate_sequence: List[Gate]
    max_steps: int
    swap_budget: int
    target_depth: int
    drift_schedule: Tuple[Tuple[int, float], ...] = ((0, 1.0),)

    def edge_error_at(self, step: int, edge: Edge) -> float:
        base = self.base_edge_errors.get(canonical_edge(*edge), 0.05)
        multiplier = 1.0
        for stage_start, stage_mult in self.drift_schedule:
            if step >= stage_start:
                multiplier = stage_mult
            else:
                break
        value = base * multiplier
        return min(0.35, max(0.0005, value))


def _build_line_edges(num_qubits: int) -> List[Edge]:
    return [canonical_edge(i, i + 1) for i in range(num_qubits - 1)]


def _build_heavy_hex_style_edges() -> List[Edge]:
    edges: set[Edge] = set()

    # 3 rows x 9 columns = 27 qubits
    rows, cols = 3, 9
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            if c < cols - 1:
                edges.add(canonical_edge(idx, idx + 1))
            if r < rows - 1 and c % 2 == 0:
                edges.add(canonical_edge(idx, idx + cols))

    # Add sparse diagonals for richer routing structure.
    for c in range(0, cols - 2, 3):
        edges.add(canonical_edge(c, c + cols + 1))
        edges.add(canonical_edge(cols + c, 2 * cols + c + 1))

    return sorted(edges)


def _build_edge_errors(edges: List[Edge], base: float, spread: float) -> Dict[Edge, float]:
    error_map: Dict[Edge, float] = {}
    for u, v in edges:
        hash_bucket = ((u * 17) + (v * 13)) % 11
        error_map[(u, v)] = base + (hash_bucket / 10.0) * spread
    return error_map


def build_task_registry() -> Dict[str, NISQTask]:
    easy_edges = _build_line_edges(8)
    easy = NISQTask(
        task_id="easy_line_routing",
        difficulty="easy",
        num_qubits=8,
        coupling_edges=easy_edges,
        base_edge_errors=_build_edge_errors(easy_edges, base=0.006, spread=0.004),
        initial_mapping=list(range(8)),
        gate_sequence=[(0, 1), (2, 3), (4, 5), (1, 2), (3, 4), (5, 6), (6, 7)],
        max_steps=80,
        swap_budget=12,
        target_depth=20,
    )

    medium_edges = _build_heavy_hex_style_edges()
    medium = NISQTask(
        task_id="medium_heavyhex_routing",
        difficulty="medium",
        num_qubits=27,
        coupling_edges=medium_edges,
        base_edge_errors=_build_edge_errors(medium_edges, base=0.012, spread=0.010),
        initial_mapping=list(range(27)),
        gate_sequence=[
            (0, 10),
            (2, 14),
            (4, 12),
            (6, 18),
            (8, 20),
            (1, 9),
            (3, 15),
            (5, 17),
            (7, 25),
            (11, 23),
            (13, 24),
            (16, 26),
        ],
        max_steps=160,
        swap_budget=30,
        target_depth=55,
    )

    hard = NISQTask(
        task_id="hard_drift_aware_routing",
        difficulty="hard",
        num_qubits=27,
        coupling_edges=medium_edges,
        base_edge_errors=_build_edge_errors(medium_edges, base=0.014, spread=0.012),
        initial_mapping=list(range(27)),
        gate_sequence=[
            (0, 18),
            (1, 19),
            (2, 20),
            (3, 21),
            (4, 22),
            (5, 23),
            (6, 24),
            (7, 25),
            (8, 26),
            (9, 17),
            (10, 16),
            (11, 15),
            (12, 14),
            (13, 21),
            (2, 24),
            (6, 16),
            (7, 12),
            (11, 20),
        ],
        max_steps=220,
        swap_budget=45,
        target_depth=85,
        drift_schedule=((0, 1.0), (70, 1.25), (150, 0.9)),
    )

    return {
        easy.task_id: easy,
        medium.task_id: medium,
        hard.task_id: hard,
    }
