import math
from math import sin, cos, radians

from sssnake.core.env.env_candies import EnvCandies
from sssnake.core.env.env_collision import EnvCollision
from sssnake.utils.env_config import EnvConfig
from sssnake.core.env.env_helpers import load_obstacles_map, generate_safe_map

class EnvEngine:
    def __init__(self, env_config: EnvConfig):
        self.config = env_config
        self.state = dict()
        self.observers = list()

        self.head_path = []
        self.segment_length = env_config.get("tail_segment_length")

        self.env_collision = EnvCollision(env_config)
        self.env_candies = EnvCandies(env_config)

        self.current_reward = 0

    def reset_env(self, config: EnvConfig = None) :
        if config is not None:
            self.config = config

        self.state = {
            "head_position": (0, 0),
            "head_direction": self.config.get("start_dir"),
            "segments_num": 0,
            "segments_positions": [(0, 0) for _ in range(self.config.get("tail_max_segment"))],
            "speed": self.config.get("snake_speed"),
            "turnspeed": self.config.get("snake_turnspeed"),
            "map_size": self.config.get("map_size"),
            "candy_position": (10.0, 10.0),
            "safe_map_snake": [[0 for _ in range(self.config.get("collision_map_resolution"))] for _ in range(self.config.get("collision_map_resolution"))]
        }

        self.env_candies.set_map_size(self.state["map_size"])
        self.calculate_obstacles_map(self.config)

        start_coords = self.config.get("start_pos_coords")
        self.state["head_position"] = tuple(coord * self.state["map_size"] for coord in start_coords)

        self.head_path = [self.state["head_position"]]

        self.state["candy_position"] = self.env_candies.random_candy_pos(self.state)

        self.current_reward = 0
        self.num_steps = 0

    def step (self, action):
        terminated, truncated = False, False

        new_state = self.state

        speed = self.state["speed"]
        turnspeed = self.state["turnspeed"]

        head_pos_x, head_pos_y = self.state["head_position"]

        if action == "left" :
            new_state["head_direction"] += turnspeed
        elif action == "right" :
            new_state["head_direction"] -= turnspeed
        elif action == "none" :
            pass

        head_dir_rad = radians(self.state["head_direction"])
        head_dir_x, head_dir_y = sin(head_dir_rad), cos(head_dir_rad)

        new_state["head_position"] = (head_pos_x + head_dir_x * speed, head_pos_y + head_dir_y * speed)
        new_state["head_direction"] %= 360

        self.head_path.append(new_state["head_position"])

        if self.env_collision.hit_anything(new_state) :
            self.state = new_state
            self.hit_done()
            terminated = True
            return

        if self.env_candies.met_candy(new_state) :
            if self.config.get("tail_max_segment") > self.state["segments_num"] :
                self.add_segment(new_state)
            self.current_reward += 1
            new_state["candy_position"] = self.env_candies.random_candy_pos(self.state)


        for i in range(new_state["segments_num"]):
            distance_behind_head = (i + 1) * self.segment_length
            new_state["segments_positions"][i] = self.get_position_on_path(distance_behind_head)

        self.num_steps += 1

        self.state = new_state

        if self.num_steps >= self.config.get("max_num_steps") and not terminated:
            truncated = True

        self.notify_observers(self.state)

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
            def normalized_direction(from_pos, to_pos):
                dx, dy = from_pos[0] - to_pos[0], from_pos[1] - to_pos[1]
                length = (dx ** 2 + dy ** 2) ** 0.5
                if length > 0:
                    return dx / length, dy / length
                else:
                    return 1, 0

            last_pos_x, last_pos_y = state["segments_positions"][-1]

            if state["segments_num"] == 1 :
                last_dir_x, last_dir_y = normalized_direction(state["head_position"], state["segments_positions"][-1])

            else :
                last_dir_x, last_dir_y = normalized_direction(state["segments_positions"][-1], state["segments_positions"][-2])

        state["segments_positions"] [state["segments_num"]] = (last_pos_x + last_dir_x * self.segment_length,
                                                               last_pos_y + last_dir_y * self.segment_length)
        state["segments_num"] += 1

    def calculate_obstacles_map(self, env_config):
        map_size = env_config.get("map_size")

        obstacles_map = load_obstacles_map(env_config.get("map_bitmap_path"), env_config.get("collision_map_resolution"))

        self.state["safe_map_snake"] = generate_safe_map(self.env_collision.obstacle_hit_distance, map_size, obstacles_map)

        self.env_candies.generate_free_cells_candy(obstacles_map)

    def hit_done(self):
        self.notify_observers("Hit")

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data=None):
        for callback in self.observers:
            callback(data)