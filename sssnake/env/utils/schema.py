from typing import Callable, Dict, Sequence

from gymnasium import spaces

from sssnake.env.utils.config_def import EnvSpec

SpaceFactory = Callable[[EnvSpec], spaces.Space]

OBS_SPACE_FACTORIES: Dict[str, SpaceFactory] = {
    "head_position": lambda spec: spaces.Box(
        low=0.0, high=spec.max_map_size, shape=(2,), dtype=float
    ),
    "head_direction": lambda _spec: spaces.Box(low=0.0, high=360.0, shape=(), dtype=float),
    "candy_position": lambda spec: spaces.Box(
        low=0.0, high=spec.max_map_size, shape=(2,), dtype=float
    ),
    "segments_num": lambda spec: spaces.Box(
        low=0,
        high=spec.tail_max_segment,
        shape=(),
        dtype=int,
    ),
    "speed": lambda spec: spaces.Box(
        low=spec.min_speed, high=spec.max_speed, shape=(), dtype=float
    ),
    "turnspeed": lambda spec: spaces.Box(
        low=spec.min_turnspeed, high=spec.max_turnspeed, shape=(), dtype=float
    ),
    "map_size": lambda spec: spaces.Box(
        low=spec.min_map_size, high=spec.max_map_size, shape=(), dtype=float
    ),
    "segments_positions": lambda spec: spaces.Box(
        low=0.0,
        high=spec.max_map_size,
        shape=(spec.tail_max_segment, 2),
        dtype=float,
    ),
    "safe_map_snake": lambda spec: spaces.Box(
        low=0,
        high=1,
        shape=(spec.collision_map_resolution, spec.collision_map_resolution),
        dtype=int,
    ),
}


def build_observation_space(spec: EnvSpec, obs_keys: Sequence[str] | None = None) -> spaces.Dict:
    keys = list(obs_keys) if obs_keys is not None else DEFAULT_OBS_KEYS
    return spaces.Dict({k: OBS_SPACE_FACTORIES[k](spec) for k in keys})


DEFAULT_OBS_KEYS = list(OBS_SPACE_FACTORIES)
