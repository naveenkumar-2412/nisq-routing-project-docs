from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

from models import NISQRoutingAction, NISQRoutingObservation


def _build_adj(edges: List[List[int]]) -> Dict[int, List[int]]:
    adj: Dict[int, List[int]] = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    return adj


def _shortest_path(src: int, dst: int, edges: List[List[int]]) -> Optional[List[int]]:
    if src == dst:
        return [src]

    adj = _build_adj(edges)
    queue = deque([src])
    parent: Dict[int, Optional[int]] = {src: None}

    while queue:
        cur = queue.popleft()
        for nxt in adj.get(cur, []):
            if nxt in parent:
                continue
            parent[nxt] = cur
            if nxt == dst:
                path = [dst]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                path.reverse()
                return path
            queue.append(nxt)

    return None


def greedy_routing_action(obs: NISQRoutingObservation) -> NISQRoutingAction:
    if obs.action_mask.get("apply_gate", False):
        return NISQRoutingAction(action_type="apply_gate", gate_index=0)

    if not obs.pending_two_qubit_gates:
        return NISQRoutingAction(action_type="terminate")

    gate = obs.pending_two_qubit_gates[0]
    if len(gate) != 2:
        return NISQRoutingAction(action_type="advance")

    logical_a, logical_b = int(gate[0]), int(gate[1])
    if logical_a >= len(obs.logical_to_physical) or logical_b >= len(obs.logical_to_physical):
        return NISQRoutingAction(action_type="advance")

    physical_a = obs.logical_to_physical[logical_a]
    physical_b = obs.logical_to_physical[logical_b]

    if obs.action_mask.get("insert_swap", False):
        path = _shortest_path(physical_a, physical_b, obs.coupling_edges)
        if path and len(path) > 1:
            return NISQRoutingAction(
                action_type="insert_swap",
                edge_u=path[0],
                edge_v=path[1],
            )

    return NISQRoutingAction(action_type="advance")
