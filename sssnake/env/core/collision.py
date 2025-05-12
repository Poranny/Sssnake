import math
from typing import Any, List

from sssnake.env.utils.config_def import EnvSpec
from sssnake.env.utils.state_def import FullState


class EnvCollision:
    def __init__(self, env_spec: EnvSpec) -> None:
        self.obstacles_map: List[Any] = []
        self.tail_hit_distance = env_spec.hit_tail_distance
        self.wall_hit_distance = env_spec.hit_wall_distance
        self.obstacle_hit_distance = env_spec.hit_obstacle_distance

    def hit_anything(self, state: FullState) -> bool:
        return self.hit_tail(state) or self.hit_wall(state) or self.hit_obstacle(state)

    def hit_obstacle(self, state: FullState) -> bool:
        if state.safe_map_snake is None or state.safe_map_snake.size == 0:
            return False

        hx, hy = state.head_position
        h, w = state.safe_map_snake.shape

        px = int(hx / state.map_size * w)
        py = int(hy / state.map_size * h)

        px = max(0, min(w - 1, px))
        py = max(0, min(h - 1, py))

        return state.safe_map_snake[py][px] == 0

    def hit_wall(self, state: FullState) -> bool:
        hpx, hpy = state.head_position

        return any(
            abs(coord - border) < self.wall_hit_distance
            for coord, border in [
                (hpx, 0),
                (hpy, 0),
                (hpx, state.map_size),
                (hpy, state.map_size),
            ]
        )

    def hit_tail(self, state: FullState) -> bool:
        hpx, hpy = state.head_position

        for cpx, cpy in state.segments_positions:
            if math.hypot(hpx - cpx, hpy - cpy) < self.tail_hit_distance:
                return True

        return False
