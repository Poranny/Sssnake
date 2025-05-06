from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Mapping, Any, Optional, Tuple, Sequence, Iterator


@dataclass(frozen=True, slots=True)
class EnvSpec:
    candy_collect_distance: float
    candy_pos_wall_distance: float
    candy_pos_obstacle_distance: float
    candy_head_distance: float

    hit_tail_distance: float
    hit_wall_distance: float
    hit_obstacle_distance:float

    tail_segment_length: float
    tail_max_segment: int

    collision_map_resolution: int

    max_num_steps: float
    seed: Optional[int] = None

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> EnvSpec:
        return EnvSpec(**d)

@dataclass(slots=True)
class ResetOptions:
    start_pos_coords: tuple[float, float]
    
    snake_speed: float
    snake_turnspeed: float

    map_size: float

    map_bitmap_path: str = ""
    start_dir: float = 1.0

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> ResetOptions:
        return ResetOptions(
            start_pos_coords=tuple(d["start_pos_coords"]),
            **{k: v for k, v in d.items() if k != "start_pos_coords"}
        )

    def iter(self) -> Iterator[Tuple[str, type, Any]]:
        for f in fields(self):
            yield f.name, f.type, getattr(self, f.name)

@dataclass(frozen=True, slots=True)
class RenderConfig:
    map_bitmap_path: str

    @classmethod
    def from_reset(cls, opts: "ResetOptions") -> RenderConfig:

        return cls(
            map_bitmap_path=opts.map_bitmap_path
        )


@dataclass(slots=True)
class RenderState:
    head_position: Tuple[float, float]
    head_direction: float
    segments_positions: Sequence[Tuple[float, float]]
    segments_num: float
    map_size: float
    candy_position: float


    @staticmethod
    def from_env_state(s: Mapping[str, Any]) -> RenderState:
        return RenderState(**{k: s[k]
            for k in RenderState.__annotations__
        })