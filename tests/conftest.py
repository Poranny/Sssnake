from pathlib import Path

import numpy as np
import pytest

from sssnake.env.core.candies import EnvCandies
from sssnake.env.core.collision import EnvCollision
from sssnake.env.core.env_engine import EnvEngine
from sssnake.env.utils.env_helpers import (
    generate_safe_map,
    load_config,
    load_obstacles_map,
)
from sssnake.env.utils.state_def import FullState, RenderState


@pytest.fixture(params=["default_params.json", "params_map.json"])
def config_path(request):
    return Path(__file__).parent / "input_data" / request.param


@pytest.fixture
def spec_and_opts(config_path):
    return load_config(config_path)


@pytest.fixture
def rng():
    return np.random.default_rng(42)


@pytest.fixture
def env_candies(spec_and_opts, rng):
    spec, opts = spec_and_opts
    candy = EnvCandies(spec)
    candy.set_map_size(opts.map_size)
    candy.set_rng(rng)
    return candy


@pytest.fixture
def collision_checker(spec_and_opts):
    spec, _ = spec_and_opts
    return EnvCollision(spec)


@pytest.fixture
def full_state(spec_and_opts):
    spec, opts = spec_and_opts
    return FullState.initial(spec, opts)


@pytest.fixture
def obstacle_map(spec_and_opts):
    spec, opts = spec_and_opts
    return load_obstacles_map(opts.map_bitmap_path, spec.collision_map_resolution)


@pytest.fixture
def safe_map(obstacle_map, spec_and_opts):
    spec, opts = spec_and_opts
    return generate_safe_map(spec.hit_obstacle_distance, opts.map_size, obstacle_map)


@pytest.fixture
def env_engine(spec_and_opts):
    spec, opts = spec_and_opts
    env = EnvEngine(spec)
    env.reset(options=opts)
    return env


@pytest.fixture
def simple_render_state():
    return RenderState(
        head_position=(5.0, 5.0),
        head_direction=0.0,
        segments_positions=[(5.0, 5.0)],
        segments_num=0,
        map_size=10.0,
        candy_position=(5.0, 5.0),
    )
