from __future__ import annotations

from models import NISQRoutingAction
from server.nisq_routing_environment import NISQRoutingEnvironment
from tests.helpers import greedy_routing_action


def test_reset_returns_expected_initial_observation() -> None:
    env = NISQRoutingEnvironment()
    obs = env.reset(task_id="easy_line_routing", seed=11)

    assert obs.task_id == "easy_line_routing"
    assert obs.depth == 0
    assert obs.swap_count == 0
    assert obs.done is False
    assert len(obs.logical_to_physical) == 8


def test_invalid_action_limit_terminates_episode() -> None:
    env = NISQRoutingEnvironment()
    env.reset(task_id="easy_line_routing")

    done = False
    last_obs = None
    for _ in range(6):
        last_obs = env.step(NISQRoutingAction(action_type="insert_swap"))
        done = last_obs.done
        if done:
            break

    assert done is True
    assert last_obs.done_reason == "invalid_action_limit"


def test_easy_task_completes_with_greedy_policy() -> None:
    env = NISQRoutingEnvironment()
    obs = env.reset(task_id="easy_line_routing", seed=7)

    steps = 0
    while not obs.done and steps < 120:
        steps += 1
        action = greedy_routing_action(obs)
        obs = env.step(action)

    assert obs.done is True
    assert obs.done_reason == "completed"
    assert obs.rubric_reward is not None
    assert obs.rubric_reward >= 0.0


def test_deterministic_replay_for_same_seed_and_actions() -> None:
    actions = [
        NISQRoutingAction(action_type="advance"),
        NISQRoutingAction(action_type="insert_swap", edge_u=0, edge_v=1),
        NISQRoutingAction(action_type="advance"),
        NISQRoutingAction(action_type="apply_gate", gate_index=0),
    ]

    env_a = NISQRoutingEnvironment()
    env_b = NISQRoutingEnvironment()

    obs_a = env_a.reset(task_id="easy_line_routing", seed=13)
    obs_b = env_b.reset(task_id="easy_line_routing", seed=13)

    for action in actions:
        obs_a = env_a.step(action)
        obs_b = env_b.step(action)

    assert obs_a.depth == obs_b.depth
    assert obs_a.swap_count == obs_b.swap_count
    assert obs_a.estimated_success_prob == obs_b.estimated_success_prob
    assert obs_a.done_reason == obs_b.done_reason
