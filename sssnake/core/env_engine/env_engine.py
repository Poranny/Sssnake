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

        self.hit_done = False

    def reset_env(self, env_params) :

        self.env_data = env_params

        self.calculate_obstacles_map()

        self.state = {
            "head_position": (15, 15),
            "head_direction": 0,
            "segments_num" : 0,
            "segments_positions": [],
            "candy_position" : (10, 10)
        }

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

        return hit



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
        min_dist = self.wall_hit_distance * 2
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
        if path == "" :
            return

        img = Image.open(path).convert("L")
        pixels = img.getdata()
        binary = [1 if p > 128 else 0 for p in pixels]
        self.obstacles_map = [binary[i * img.width:(i + 1) * img.width] for i in range(img.height)]


    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data=None):
        for callback in self.observers:
            callback(data)
