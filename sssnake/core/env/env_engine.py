import math
from math import sin, cos, radians

import gym
from gym import spaces

from sssnake.core.env.env_candies import EnvCandies
from sssnake.core.env.env_collision import EnvCollision
from sssnake.utils.env_config import EnvSpec, ResetOptions
from sssnake.core.env.env_helpers import load_obstacles_map, generate_safe_map
from sssnake.utils.snake_action import SnakeAction


class EnvEngine (gym.Env):

    def __init__(self, env_spec: EnvSpec):
        super().__init__()
        self.num_steps = None

        n_actions = len(SnakeAction)

        self.action_space = spaces.Discrete(n_actions)

        self.env_spec = env_spec
        self.state = dict()
        self.observers = list()

        self.head_path = []
        self.segment_length = self.env_spec.tail_segment_length

        self.env_collision = EnvCollision(env_spec)
        self.env_candies = EnvCandies(env_spec)

        self.current_reward = 0

    def reset(self, seed=None, options: ResetOptions = None) :
        self.state = {
            "head_position": (0, 0),
            "head_direction": options.start_dir,
            "segments_num": 0,
            "segments_positions": [(0, 0) for _ in range(self.env_spec.tail_max_segment)],
            "speed": options.snake_speed,
            "turnspeed": options.snake_turnspeed,
            "map_size": options.map_size,
            "candy_position": (10.0, 10.0),
            "safe_map_snake": [[0 for _ in range(self.env_spec.collision_map_resolution)] for _ in range(self.env_spec.collision_map_resolution)]
        }

        self.env_candies.set_map_size(self.state["map_size"])
        self.calculate_obstacles_map(options)

        start_coords = options.start_pos_coords
        self.state["head_position"] = tuple(coord * self.state["map_size"] for coord in start_coords)

        self.head_path = [self.state["head_position"]]

        self.state["candy_position"] = self.env_candies.random_candy_pos(self.state)

        self.current_reward = 0
        self.num_steps = 0

        info = []

        return self.state, info

    def step (self, _action: int) -> tuple[dict, int, bool, bool, dict]:
        action = SnakeAction(_action)

        terminated, truncated = False, False
        info = {}

        new_state = self.state.copy()

        speed = self.state["speed"]
        turnspeed = self.state["turnspeed"]

        head_pos_x, head_pos_y = self.state["head_position"]

        if action is SnakeAction.LEFT :
            new_state["head_direction"] += turnspeed
        elif action is SnakeAction.RIGHT :
            new_state["head_direction"] -= turnspeed
        elif action is SnakeAction.NONE :
            pass

        head_dir_rad = radians(self.state["head_direction"])
        head_dir_x, head_dir_y = sin(head_dir_rad), cos(head_dir_rad)

        new_state["head_position"] = (head_pos_x + head_dir_x * speed, head_pos_y + head_dir_y * speed)
        new_state["head_direction"] %= 360

        self.head_path.append(new_state["head_position"])


        if self.env_collision.hit_anything(new_state) :
            self.state = new_state
            terminated=True
            return self.state, self.current_reward, truncated, terminated, info

        if self.env_candies.met_candy(new_state) :
            if self.env_spec.tail_max_segment > self.state["segments_num"] :
                self.add_segment(new_state)
            self.current_reward += 1
            new_state["candy_position"] = self.env_candies.random_candy_pos(self.state)

        for i in range(new_state["segments_num"]):
            distance_behind_head = (i + 1) * self.segment_length
            new_state["segments_positions"][i] = self.get_position_on_path(distance_behind_head)

        self.num_steps += 1

        self.state = new_state

        if self.num_steps >= self.env_spec.max_num_steps and not terminated:
            truncated = True

        return self.state, self.current_reward, truncated, terminated, info

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
                return x, y
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

    def calculate_obstacles_map(self, reset_options : ResetOptions):
        map_size = reset_options.map_size

        obstacles_map = load_obstacles_map(reset_options.map_bitmap_path, self.env_spec.collision_map_resolution)

        self.state["safe_map_snake"] = generate_safe_map(self.env_collision.obstacle_hit_distance, map_size, obstacles_map)

        self.env_candies.generate_free_cells_candy(obstacles_map)

    def render(self):
        pass