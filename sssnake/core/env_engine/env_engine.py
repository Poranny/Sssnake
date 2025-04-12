import math
from math import sin, cos, radians
import random

from PIL import Image


class EnvEngine:

    def __init__(self):
        self.env_data = None
        self.state = dict()
        self.observers = list()

        self.head_path = []
        self.segment_length = 1.5
        self.candy_distance = 2
        self.tail_hit_distance = 1
        self.wall_hit_distance = 1
        self.candy_wall_distance = 2
        self.obstacle_hit_distance = 1
        self.candy_obstacle_distance = 2

        self.hit_done = False

    def reset_env(self, env_params) :

        self.env_data = env_params

        self.state = {
            "head_position": (15, 15),
            "head_direction": 0,
            "segments_num" : 0,
            "segments_positions": [],
            "candy_position" : (15, 10)
        }

        self.calculate_obstacles_map()

        self.hit_done = False

        self.head_path = [self.state["head_position"]]

    def step (self, action=None):
        if self.hit_done or self.env_data is None:
            return

        new_state = self.state

        speed = self.env_data["snake_speed"]
        turnspeed = self.env_data["snake_turnspeed"]

        head_pos_x, head_pos_y = self.state["head_position"]

        if action == "left" :
            new_state["head_direction"] += turnspeed
        elif action == "right" :
            new_state["head_direction"] -= turnspeed

        head_dir_rad = radians(self.state["head_direction"])
        head_dir_x, head_dir_y = sin(head_dir_rad), cos(head_dir_rad)

        new_state["head_position"] = (head_pos_x + head_dir_x * speed, head_pos_y + head_dir_y * speed)

        new_state["head_direction"] %= 360

        self.head_path.append(new_state["head_position"])

        if self.hit_anything(new_state) :
            self.hit_done = True
            self.notify_observers("Hit")
            return

        if self.met_candy(new_state) :
            self.add_segment(new_state)
            new_state["candy_position"] = self.random_candy_pos()

        for i in range(new_state["segments_num"]):
            distance_behind_head = (i + 1) * self.segment_length
            new_state["segments_positions"][i] = self.get_position_on_path(distance_behind_head)

        self.state = new_state
        self.notify_observers(self.state)

    def hit_anything(self, state):

        hit = False

        hit = hit or self.hit_tail(state)

        if not hit :
            hit = hit or self.hit_wall(state)

        if not hit :
            hit = hit or self.hit_obstacle(state)

        return hit

    def hit_obstacle(self, state):
        obstacles_map = state.get("obstacles_map")
        safe_map_snake = state.get("safe_map_snake")
        if not obstacles_map or not safe_map_snake:
            return False

        hx, hy = state["head_position"]
        w = len(obstacles_map[0])
        h = len(obstacles_map)

        px = int(hx / self.env_data["map_size_x"] * w)
        py = int(hy / self.env_data["map_size_y"] * h)

        px = max(0, min(w - 1, px))
        py = max(0, min(h - 1, py))

        return safe_map_snake[py][px] == 0

    def hit_wall (self, state):

        hpx, hpy = state["head_position"]

        hit = any(
            abs(coord - border) < self.wall_hit_distance
            for coord, border in [
                (hpx, 0),
                (hpy, 0),
                (hpx, self.env_data["map_size_x"]),
                (hpy, self.env_data["map_size_y"]),
            ]
        )

        return hit

    def hit_tail(self, state):

        hpx, hpy = state["head_position"]

        hit = False

        for segment_pos in state["segments_positions"]:
            cpx, cpy = segment_pos
            distance = math.sqrt((hpx - cpx) ** 2 + (hpy - cpy) ** 2)

            if distance < self.tail_hit_distance :
                hit = True
                break

        return hit

    def random_candy_pos(self):

        if self._free_cells_candy:
            x_pixel, y_pixel = random.choice(self._free_cells_candy)
            w = len(self.state["obstacles_map"][0])
            h = len(self.state["obstacles_map"])
            env_x = x_pixel * (self.env_data["map_size_x"] / w)
            env_y = y_pixel * (self.env_data["map_size_y"] / h)
            return (env_x, env_y)
        else:
            return self.random_candy_pos_legacy()

    def random_candy_pos_legacy(self):

        min_dist = self.candy_wall_distance
        max_x = self.env_data["map_size_x"] - min_dist
        max_y = self.env_data["map_size_y"] - min_dist

        rand_x = random.uniform(min_dist, max_x)
        rand_y = random.uniform(min_dist, max_y)
        return (rand_x, rand_y)

    def met_candy(self, state):
        hpx, hpy = state["head_position"]
        cpx, cpy = state["candy_position"]
        distance = math.sqrt((hpx - cpx) ** 2 + (hpy - cpy) ** 2)

        return distance < self.candy_distance

    def get_position_on_path(self, distance_behind_head):

        if len(self.head_path) < 2:
            return self.head_path[0] if self.head_path else (0, 0)

        accumulated = 0.0

        for idx in range(len(self.head_path) - 1, 0, -1):
            x1, y1 = self.head_path[idx]
            x0, y0 = self.head_path[idx - 1]

            seg_len = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            if accumulated + seg_len >= distance_behind_head:
                ratio = (distance_behind_head - accumulated) / seg_len

                x = x1 + (x0 - x1) * ratio
                y = y1 + (y0 - y1) * ratio
                return (x, y)
            else:
                accumulated += seg_len

        return self.head_path[0]

    def add_segment(self, state):

        if state["segments_num"] == 0:
            last_pos_x, last_pos_y = state["head_position"]

            last_dir_rad = radians(state["head_direction"])
            last_dir_x, last_dir_y = -sin(last_dir_rad), -cos(last_dir_rad)

        else :
            last_pos_x, last_pos_y = state["segments_positions"][-1]

            if state["segments_num"] == 1 :
                head_pos_x, head_pos_y = state["head_position"]

                dx, dy = last_pos_x - head_pos_x, last_pos_y - head_pos_y
                length = (dx ** 2 + dy ** 2) ** 0.5

                if length > 0 :
                    last_dir_x, last_dir_y = (dx / length, dy / length)
                else :
                    last_dir_x, last_dir_y = 1, 0

            else :
                last2_pos_x, last2_pos_y = state["segments_positions"][-2]

                dx, dy = last_pos_x - last2_pos_x, last_pos_y - last2_pos_y
                length = (dx ** 2 + dy ** 2) ** 0.5
                if length > 0:
                    last_dir_x, last_dir_y = (dx / length, dy / length)
                else:
                    last_dir_x, last_dir_y = 1, 0


        state["segments_num"] += 1

        state["segments_positions"].append((last_pos_x + last_dir_x * self.segment_length, last_pos_y + last_dir_y * self.segment_length))

    def calculate_obstacles_map(self):

        path = self.env_data["map_bitmap_path"]
        if not path:
            self.state["obstacles_map"] = None
            self.state["safe_map_snake"] = None
            self.state["safe_map_candy"] = None
            self._free_cells_candy = []
            return

        img = Image.open(path).convert("L")
        w, h = img.size
        pixels = list(img.getdata())

        obstacles_map = [
            [1 if p > 128 else 0 for p in pixels[row_start: row_start + w]]
            for row_start in range(0, w * h, w)
        ]
        self.state["obstacles_map"] = obstacles_map

        px_margin_snake = int(self.obstacle_hit_distance * (w / self.env_data["map_size_x"]))
        px_margin_snake = max(px_margin_snake, 1)

        safe_map_snake = [[1] * w for _ in range(h)]

        for y in range(h):
            for x in range(w):
                if obstacles_map[y][x] == 1:
                    x0 = max(0, x - px_margin_snake)
                    x1 = min(w, x + px_margin_snake + 1)
                    y0 = max(0, y - px_margin_snake)
                    y1 = min(h, y + px_margin_snake + 1)
                    for yy in range(y0, y1):
                        for xx in range(x0, x1):
                            safe_map_snake[yy][xx] = 0

        px_margin_candy = int(self.candy_obstacle_distance * (w / self.env_data["map_size_x"]))
        px_margin_candy = max(px_margin_candy, 1)

        safe_map_candy = [[1] * w for _ in range(h)]

        for y in range(h):
            for x in range(w):
                if obstacles_map[y][x] == 1:
                    x0 = max(0, x - px_margin_candy)
                    x1 = min(w, x + px_margin_candy + 1)
                    y0 = max(0, y - px_margin_candy)
                    y1 = min(h, y + px_margin_candy + 1)
                    for yy in range(y0, y1):
                        for xx in range(x0, x1):
                            safe_map_candy[yy][xx] = 0

        px_margin_wall = int(self.candy_wall_distance * (w / self.env_data["map_size_x"]))
        px_margin_wall = max(px_margin_wall, 1)

        for y in range(px_margin_wall):
            for x in range(w):
                safe_map_candy[y][x] = 0
                safe_map_candy[h - 1 - y][x] = 0

        for x in range(px_margin_wall):
            for y in range(h):
                safe_map_candy[y][x] = 0
                safe_map_candy[y][w - 1 - x] = 0

        self.state["safe_map_snake"] = safe_map_snake
        self.state["safe_map_candy"] = safe_map_candy

        free_cells_candy = []
        for y in range(h):
            for x in range(w):
                if safe_map_candy[y][x] == 1:
                    free_cells_candy.append((x, y))

        self._free_cells_candy = free_cells_candy

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data=None):
        for callback in self.observers:
            callback(data)
