from __future__ import annotations

import math
from copy import deepcopy
from importlib.resources import files
from math import cos, radians, sin
from typing import Any, Dict, List, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.utils import seeding

from sssnake.env.core.candies import EnvCandies
from sssnake.env.core.collision import EnvCollision
from sssnake.env.core.renderer import state_to_array
from sssnake.env.utils.config_def import EnvSpec, ResetOptions
from sssnake.env.utils.env_helpers import generate_safe_map, load_config, load_obstacles_map
from sssnake.env.utils.schema import DEFAULT_OBS_KEYS, build_observation_space
from sssnake.env.utils.snake_action import SnakeAction
from sssnake.env.utils.state_def import (
    FullState,
    InfoDict,
    ObservationDict,
    RenderState,
)


class EnvEngine(gym.Env):
    """
    Base gym env class.
    """

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(self, env_spec_in: EnvSpec | None = None, render_mode: str | None = None) -> None:
        super().__init__()
        self.last_reset_options: ResetOptions | None = None

        default_json = files("sssnake.env.utils").joinpath("default_params.json")
        env_spec_loaded, self.last_reset_options = load_config(jsonpath=str(default_json))

        if env_spec_in is None:
            env_spec = env_spec_loaded
        else:
            env_spec = env_spec_in

        if render_mode not in {None, "rgb_array"}:
            raise ValueError(f"Rendermode '{render_mode}' not supported.")

        self.num_steps: int = 0
        self.render_mode = render_mode
        self.np_random: np.random.Generator

        self.obs_keys = DEFAULT_OBS_KEYS

        self.action_space = spaces.Discrete(len(SnakeAction))
        self.observation_space = build_observation_space(env_spec, self.obs_keys)

        self.env_spec = env_spec
        self.state: FullState = FullState.initial(self.env_spec, self.last_reset_options)

        self.head_path: List[Tuple[float, float]] = []
        self.segment_length = self.env_spec.tail_segment_length

        self.env_collision = EnvCollision(env_spec)
        self.env_candies = EnvCandies(env_spec)

    def reset(
        self, *, seed: int | None = None, options: Dict[str, Any] | ResetOptions | None = None
    ):
        self.np_random, seed = seeding.np_random(seed)

        if options is not None:
            if isinstance(options, dict):
                self.last_reset_options = ResetOptions.from_dict(options)
            else:
                self.last_reset_options = options

        super().reset(seed=seed)

        if self.last_reset_options is None:
            raise RuntimeError("ResetOptions not initialized.")

        reset_opts = self.last_reset_options

        self.state = FullState.initial(self.env_spec, reset_opts)

        self.num_steps = 0

        self.place_head(reset_opts.start_pos_coords)

        self.env_candies.set_map_size(self.state.map_size)
        self.prepare_collision_map(reset_opts)
        self.init_candies()

        info: InfoDict = {}
        obs: ObservationDict = self.state.to_obs(self.obs_keys)
        return obs, info

    def step(self, action_int: int):
        assert self.state is not None, "Environment not reset!"

        current_reward = 0
        terminated = truncated = False
        info: InfoDict = {}

        action = SnakeAction(action_int)

        self.apply_turn(action)

        self.move_head()

        if self.env_collision.hit_anything(self.state):
            terminated = True
            obs: ObservationDict = self.state.to_obs(self.obs_keys)
            current_reward = -1
            return obs, current_reward, terminated, truncated, info

        if self.env_candies.met_candy(self.state):
            if self.env_spec.tail_max_segment > self.state.segments_num:
                self.add_segment()
            current_reward = 1
            self.state.candy_position = self.env_candies.random_candy_pos(self.state)

        self.update_body_segments()
        self.num_steps += 1

        truncated = self.num_steps >= self.env_spec.max_num_steps

        observation: ObservationDict = self.state.to_obs(self.obs_keys)

        return observation, current_reward, terminated, truncated, info

    def place_head(self, start_coords: Tuple[float, float]):
        """
        Initially sets the head's position.
        """

        self.state.head_position = (
            start_coords[0] * self.state.map_size,
            start_coords[1] * self.state.map_size,
        )

        self.head_path = [self.state.head_position]

    def move_head(self):
        """
        Moves the head in accordance with its direction and speed.
        """

        ang = radians(self.state.head_direction)
        dx, dy = sin(ang) * self.state.speed, cos(ang) * self.state.speed
        x, y = self.state.head_position

        self.state.head_position = (x + dx, y + dy)
        self.head_path.append(self.state.head_position)

    def apply_turn(self, action):
        """
        Apply the current turn's action.
        """

        if action is SnakeAction.LEFT:
            self.state.head_direction += self.state.turnspeed
        elif action is SnakeAction.RIGHT:
            self.state.head_direction -= self.state.turnspeed
        elif action is SnakeAction.NONE:
            pass

        self.state.head_direction %= 360.0

    def update_body_segments(self):
        """
        Updates the positions of snake's body segments.
        """

        for i in range(self.state.segments_num):
            distance_behind_head = (i + 1) * self.segment_length
            self.state.segments_positions[i] = self.get_position_on_path(distance_behind_head)

    def get_position_on_path(self, distance_behind_head):
        """
        Calculates the position on snake's path for a certain distance behind head.
        """

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

    def add_segment(self):
        """
        Adds a segment to the snake's body on a certain position behind the last segment/head.
        """

        if self.state.segments_num == 0:
            last_pos_x, last_pos_y = self.state.head_position

            last_dir_rad = radians(self.state.head_direction)
            last_dir_x, last_dir_y = -sin(last_dir_rad), -cos(last_dir_rad)

        else:

            def normalized_direction(from_pos, to_pos):
                dx, dy = from_pos[0] - to_pos[0], from_pos[1] - to_pos[1]
                length = (dx**2 + dy**2) ** 0.5
                if length > 0:
                    return dx / length, dy / length
                else:
                    return 1, 0

            last_pos_x, last_pos_y = self.state.segments_positions[-1]

            if self.state.segments_num == 1:
                last_dir_x, last_dir_y = normalized_direction(
                    self.state.head_position, self.state.segments_positions[-1]
                )

            else:
                last_dir_x, last_dir_y = normalized_direction(
                    self.state.segments_positions[-1], self.state.segments_positions[-2]
                )

        self.state.segments_positions[self.state.segments_num] = (
            last_pos_x + last_dir_x * self.segment_length,
            last_pos_y + last_dir_y * self.segment_length,
        )
        self.state.segments_num += 1

    def prepare_collision_map(self, reset_options: ResetOptions):
        """
        Loads and sets up the obstacles map for snake's collision and EnvCandies candies generation.
        """
        map_size = reset_options.map_size
        obstacles_map = load_obstacles_map(
            reset_options.map_bitmap_path, self.env_spec.collision_map_resolution
        )

        assert self.state is not None
        self.state.safe_map_snake = generate_safe_map(
            self.env_collision.obstacle_hit_distance, map_size, obstacles_map
        )

        self.env_candies.generate_free_cells_candy(obstacles_map)

    def init_candies(self):
        """
        Initialize the rng in env_candies and set up the initial candy's position.
        """

        self.env_candies.set_rng(self.np_random)

        self.state.candy_position = self.env_candies.random_candy_pos(self.state)

    def render(self):
        if self.render_mode is None:
            return None
        elif self.render_mode == "rgb_array":
            return state_to_array(
                RenderState.from_full_state(self.state),
                self.last_reset_options.map_bitmap_path,
            )
        else:
            raise NotImplementedError(f"Render mode '{self.render_mode}' is not supported.")

    def get_state(self) -> FullState | None:
        return deepcopy(self.state)
