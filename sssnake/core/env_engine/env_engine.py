from math import sin, cos, radians
from collections import defaultdict

class EnvEngine:

    def __init__(self):
        self.env_data = None
        self.state = dict()
        self.observers = list()

    def reset_env(self, env_params) :

        self.env_data = env_params

        self.state = {
            "head_position": (50, 50),
            "head_direction": 45,
        }

    def step (self, action=None):
        speed = self.env_data["snake_speed"]
        turnspeed = self.env_data["snake_turnspeed"]

        head_pos_x, head_pos_y = self.state["head_position"]



        if action == "left" :
            self.state["head_direction"] += turnspeed
        elif action == "right" :
            self.state["head_direction"] -= turnspeed


        head_dir_rad = radians(self.state["head_direction"])


        head_dir_x, head_dir_y = sin(head_dir_rad), cos(head_dir_rad)



        self.state["head_position"] = (head_pos_x + head_dir_x * speed, head_pos_y + head_dir_y * speed)

        self.notify_observers(self.state)

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data=None):
        for callback in self.observers:
            callback(data)