import numpy as np


def test_random_candy_in_bounds(env_candies):
    x, y = env_candies.random_candy_pos_nomap()

    assert 0 <= x < env_candies.map_size, f"x={x} out of [0, {env_candies.map_size})"
    assert 0 <= y < env_candies.map_size, f"y={y} out of [0, {env_candies.map_size})"


def test_met_candy_true(env_candies, full_state):
    full_state.head_position = (0.0, 0.0)
    full_state.candy_position = (env_candies.candy_distance / 2, 0.0)

    assert env_candies.met_candy(full_state)


def test_met_candy_false(env_candies, full_state):
    full_state.head_position = (0.0, 0.0)
    full_state.candy_position = (2 * env_candies.candy_distance, 0.0)

    assert not env_candies.met_candy(full_state)


def test_random_candy_pos_head_dist(env_candies, full_state):
    too_close = env_candies.candy_head_distance / 2
    just_right = env_candies.candy_head_distance * 2

    coords = np.array([[too_close, 0.0], [just_right, 0.0]], dtype=np.float32)
    env_candies.free_pos_candy = coords

    full_state.head_position = (0.0, 0.0)

    pos = env_candies.random_candy_pos(full_state)
    assert pos == (just_right, 0.0), f"{pos} chosen, instead of {(just_right, 0.0)}"
