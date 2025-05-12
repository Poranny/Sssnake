from __future__ import annotations

from typing import Callable, Dict, Sequence

import numpy as np
from gymnasium import spaces

from sssnake.env.utils.config_def import EnvSpec

SpaceFactory = Callable[[EnvSpec], spaces.Space]

OBS_SPACE_FACTORIES: Dict[str, SpaceFactory] = {
    "head_position": lambda spec: spaces.Box(
        low=0.0, high=spec.max_map_size, shape=(2,), dtype=np.float32
    ),
    "head_direction": lambda _spec: spaces.Box(low=0.0, high=360.0, shape=(), dtype=np.float32),
    "candy_position": lambda spec: spaces.Box(
        low=0.0, high=spec.max_map_size, shape=(2,), dtype=np.float32
    ),
    "segments_num": lambda spec: spaces.Box(
        low=0,
        high=spec.tail_max_segment,
        shape=(),
        dtype=np.int64,
    ),
    "speed": lambda spec: spaces.Box(
        low=spec.min_speed, high=spec.max_speed, shape=(), dtype=np.float32
    ),
    "turnspeed": lambda spec: spaces.Box(
        low=spec.min_turnspeed, high=spec.max_turnspeed, shape=(), dtype=np.float32
    ),
    "map_size": lambda spec: spaces.Box(
        low=spec.min_map_size, high=spec.max_map_size, shape=(), dtype=np.float32
    ),
    "segments_positions": lambda spec: spaces.Box(
        low=0.0,
        high=spec.max_map_size,
        shape=(spec.tail_max_segment, 2),
        dtype=np.float32,
    ),
    "safe_map_snake": lambda spec: spaces.Box(
        low=0,
        high=1,
        shape=(spec.collision_map_resolution, spec.collision_map_resolution),
        dtype=np.int64,
    ),
}


def build_observation_space(spec: EnvSpec, obs_keys: Sequence[str] | None = None) -> spaces.Dict:
    keys = list(obs_keys) if obs_keys is not None else DEFAULT_OBS_KEYS
    return spaces.Dict({k: OBS_SPACE_FACTORIES[k](spec) for k in keys})


DEFAULT_OBS_KEYS = list(OBS_SPACE_FACTORIES)
