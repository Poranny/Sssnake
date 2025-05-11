from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Tuple, List, Dict, Any, Sequence

import numpy as np

from sssnake.env.utils.config_def import ResetOptions, EnvSpec


@dataclass
class FullState:
    head_position: Tuple[float, float]
    head_direction: float
    segments_num: int
    segments_positions: List[Tuple[float, float]]
    speed: float
    turnspeed: float
    map_size: float
    candy_position: Tuple[float, float]
    safe_map_snake: np.ndarray

    @staticmethod
    def initial(spec: EnvSpec, opts: ResetOptions) -> "FullState":
        return FullState(
            head_position=(0.0, 0.0),
            head_direction=opts.start_dir,
            segments_num=0,
            segments_positions=[(0.0, 0.0)] * spec.tail_max_segment,
            speed=opts.snake_speed,
            turnspeed=opts.snake_turnspeed,
            map_size=opts.map_size,
            candy_position=(10.0, 10.0),
            safe_map_snake=np.ones(
                (spec.collision_map_resolution, spec.collision_map_resolution),
                dtype=np.int8,
            ),
        )

    def to_obs(self, keys: Sequence[str] | None = None) -> "ObservationDict":
        raw: Dict[str, Any] = asdict(self)
        if keys is None:
            return raw
        return {k: raw[k] for k in keys}


ObservationDict = Dict[str, Any]
InfoDict = Dict[str, Any]


@dataclass(slots=True)
class RenderState:
    head_position: Tuple[float, float]
    head_direction: float
    segments_positions: Sequence[Tuple[float, float]]
    segments_num: float
    map_size: float
    candy_position: Tuple[float, float]

    @classmethod
    def from_full_state(cls, s: "FullState") -> RenderState:
        return cls(
            head_position=s.head_position,
            head_direction=s.head_direction,
            segments_positions=s.segments_positions.copy(),
            candy_position=s.candy_position,
            segments_num=s.segments_num,
            map_size=s.map_size,
        )
