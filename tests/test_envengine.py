import pytest
from sssnake.env.utils.snake_action import SnakeAction

def test_reset_state(env_engine):
    assert env_engine.num_steps == 0
    assert env_engine.state.segments_num == 0
    assert env_engine.state.head_position == env_engine.head_path[0]

def test_step_progress(env_engine):
    start_pos = env_engine.state.head_position
    _, reward, terminated, truncated, _ = env_engine.step(SnakeAction.NONE.value)
    assert env_engine.num_steps == 1
    assert reward == 0
    assert not terminated
    assert not truncated
    assert env_engine.state.head_position != start_pos

def test_candy_reward(env_engine):
    env_engine.state.speed = 0.0
    env_engine.state.candy_position = env_engine.state.head_position
    _, reward, terminated, _, _ = env_engine.step(SnakeAction.NONE.value)
    assert reward == 1
    assert not terminated






