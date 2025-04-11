from math import sin, cos, radians

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
        if self.env_data is None:
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

        self.state = new_state

        self.notify_observers(self.state)

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data=None):
        for callback in self.observers:
            callback(data)