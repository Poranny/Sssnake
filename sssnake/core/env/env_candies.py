import math
import random

import numpy as np

from sssnake.core.env.env_helpers import generate_safe_map
from sssnake.utils.env_config import EnvSpec


class EnvCandies :
    def __init__(self, env_spec: EnvSpec):
        self.candy_distance = env_spec.candy_collect_distance
        self.candy_wall_distance = env_spec.candy_pos_wall_distance
        self.candy_obstacle_distance = env_spec.candy_pos_obstacle_distance
        self.candy_head_distance = env_spec.candy_head_distance

        self.map_size = 0

        self.free_pos_candy = None

    def set_rng(self, rng: np.random.Generator):
        self.rng = rng

    def set_map_size(self, map_size):
        self.map_size = map_size

    def random_candy_pos(self, state):
        assert self.rng is not None, "RNG not set – call set_rng() from EnvEngine.reset()"

        head = state.head_position

        available = [
            pos for pos in self.free_pos_candy
            if np.linalg.norm(np.subtract(pos, head)) >= self.candy_head_distance
        ]

        if available:
            idx = self.rng.integers(len(available))
            return available[idx]

        return self.random_candy_pos_nomap()

    def random_candy_pos_nomap(self):
        assert self.rng is not None, "RNG not set – call set_rng() from EnvEngine.reset()"

        min_dist = self.candy_wall_distance
        max_pos = self.map_size - min_dist

        rand_x = self.rng.uniform(min_dist, max_pos)
        rand_y = self.rng.uniform(min_dist, max_pos)
        return rand_x, rand_y

    def met_candy(self, state):
        hpx, hpy = state.head_position
        cpx, cpy = state.candy_position
        distance = math.sqrt((hpx - cpx)**2 + (hpy - cpy)**2)

        return distance < self.candy_distance

    def generate_free_cells_candy(self, obstacles_map):
        obstacles_size = len(obstacles_map)

        candy_margin_wall = max(int(self.candy_wall_distance * (obstacles_size / self.map_size)), 1)

        safe_map_candy = generate_safe_map(self.candy_obstacle_distance, self.map_size, obstacles_map)

        for x in range(obstacles_size):
            for y in range(candy_margin_wall):
                safe_map_candy[y][x] = 0
                safe_map_candy[obstacles_size - 1 - y][x] = 0

        for y in range(obstacles_size):
            for x in range(candy_margin_wall):
                safe_map_candy[y][x] = 0
                safe_map_candy[y][obstacles_size - 1 - x] = 0

        free_cells_candy = []
        for y in range(obstacles_size):
            for x in range(obstacles_size):
                if safe_map_candy[y][x] == 1:
                    free_cells_candy.append((x, y))

        ratio = self.map_size / obstacles_size
        self.free_pos_candy = [
            (x * ratio,
             y * ratio)
            for (x, y) in free_cells_candy
        ]