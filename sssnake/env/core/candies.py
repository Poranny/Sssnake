from __future__ import annotations

import math

import numpy as np

from sssnake.env.utils.config_def import EnvSpec
from sssnake.env.utils.env_helpers import generate_safe_map


class EnvCandies:
    """
    Class responsible for managing the candies' generation, placement, and their collection.
    """

    def __init__(self, env_spec: EnvSpec):
        self.rng: np.random.Generator | None = None

        self.candy_distance = env_spec.candy_collect_distance
        self.candy_wall_distance = env_spec.candy_pos_wall_distance
        self.candy_obstacle_distance = env_spec.candy_pos_obstacle_distance
        self.candy_head_distance = env_spec.candy_head_distance

        self.map_size = 0

        self.free_pos_candy: np.ndarray | None = None

    def set_rng(self, rng: np.random.Generator):
        self.rng = rng

    def set_map_size(self, map_size):
        self.map_size = map_size

    def random_candy_pos(self, state):
        """
        Randomly chooses a candy position basing on the safe map.
        """

        assert self.rng is not None

        head = state.head_position
        dists = np.linalg.norm(self.free_pos_candy - head, axis=1)

        available = self.free_pos_candy[dists >= self.candy_head_distance]

        if available.size:
            idx = self.rng.integers(available.shape[0])
            return tuple(available[idx])

        return self.random_candy_pos_nomap()  # Run when there are no available candy positions

    def random_candy_pos_nomap(self):
        """
        Randomly chooses a candy position within the map's size.
        """

        assert self.rng is not None, "RNG not set – call set_rng() from EnvEngine.reset()"

        min_dist = self.candy_wall_distance
        max_pos = self.map_size - min_dist

        rand_x = self.rng.uniform(min_dist, max_pos)
        rand_y = self.rng.uniform(min_dist, max_pos)
        return rand_x, rand_y

    def met_candy(self, state):
        hpx, hpy = state.head_position
        cpx, cpy = state.candy_position
        return math.hypot(hpx - cpx, hpy - cpy) < self.candy_distance

    def generate_free_cells_candy(self, obstacles_map):
        """
        Generates free cells for candy placement based on the obstacles map.
        """

        n = obstacles_map.shape[0]

        candy_margin_wall = max(int(self.candy_wall_distance * (n / self.map_size)), 1)

        safe_map_candy = generate_safe_map(
            self.candy_obstacle_distance,
            self.map_size,
            obstacles_map,
        )

        safe_map_candy[:candy_margin_wall, :] = 0
        safe_map_candy[-candy_margin_wall:, :] = 0
        safe_map_candy[:, :candy_margin_wall] = 0
        safe_map_candy[:, -candy_margin_wall:] = 0

        ys, xs = np.nonzero(safe_map_candy)

        coords = np.stack((xs, ys), axis=1).astype(np.float32)
        ratio = self.map_size / n

        self.free_pos_candy = coords * ratio
