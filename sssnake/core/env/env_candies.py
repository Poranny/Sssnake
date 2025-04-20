import math
import random

from sssnake.core.env.env_helpers import generate_safe_map
from sssnake.utils.env_config import EnvConfig


class EnvCandies :
    def __init__(self, env_config: EnvConfig):
        self.candy_distance = env_config.get("candy_collect_distance")
        self.candy_wall_distance = env_config.get("candy_pos_wall_distance")
        self.candy_obstacle_distance = env_config.get("candy_pos_obstacle_distance")
        self.candy_head_distance = env_config.get("candy_head_distance")

        self.map_size = 0, 0

        self.free_pos_candy = None

    def set_map_size(self, map_size):
        self.map_size = map_size

    def random_candy_pos(self, state):
        max_search = 20

        while True:
            max_search -= 1
            if self.free_pos_candy:
                x_pos, y_pos = random.choice(self.free_pos_candy)
            else:
                x_pos, y_pos = self.random_candy_pos_nomap()

            dist_to_head = math.sqrt((x_pos - state["head_position"][0]) ** 2 + (y_pos - state["head_position"][1]) ** 2)
            if dist_to_head > self.candy_head_distance or max_search == 0:
                return x_pos, y_pos

    def random_candy_pos_nomap(self):
        min_dist = self.candy_wall_distance
        max_x = self.map_size[0] - min_dist
        max_y = self.map_size[1] - min_dist

        rand_x = random.uniform(min_dist, max_x)
        rand_y = random.uniform(min_dist, max_y)
        return rand_x, rand_y

    def met_candy(self, state):
        hpx, hpy = state["head_position"]
        cpx, cpy = state["candy_position"]
        distance = math.sqrt((hpx - cpx) ** 2 + (hpy - cpy) ** 2)

        return distance < self.candy_distance

    def generate_free_cells_candy(self, obstacles_map):
        obstacles_w, obstacles_h = len(obstacles_map[0]), len(obstacles_map)

        candy_margin_wall_x = max(int(self.candy_wall_distance * (obstacles_w / self.map_size[0])), 1)
        candy_margin_wall_y = max(int(self.candy_wall_distance * (obstacles_h / self.map_size[1])), 1)

        safe_map_candy = generate_safe_map(self.candy_obstacle_distance, self.map_size, obstacles_map)

        for x in range(obstacles_w):
            for y in range(candy_margin_wall_y):
                safe_map_candy[y][x] = 0
                safe_map_candy[obstacles_h - 1 - y][x] = 0

        for y in range(obstacles_h):
            for x in range(candy_margin_wall_x):
                safe_map_candy[y][x] = 0
                safe_map_candy[y][obstacles_w - 1 - x] = 0

        free_cells_candy = []
        for y in range(obstacles_h):
            for x in range(obstacles_w):
                if safe_map_candy[y][x] == 1:
                    free_cells_candy.append((x, y))


        self.free_pos_candy = [
            (x * (self.map_size[0] / obstacles_w),
             y * (self.map_size[1] / obstacles_h))
            for (x, y) in free_cells_candy
        ]