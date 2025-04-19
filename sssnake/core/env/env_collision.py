import math

class EnvCollision :
    def __init__(self):
        self.obstacles_map = []

        self.tail_hit_distance = 1
        self.wall_hit_distance = 1
        self.obstacle_hit_distance = 1

    def hit_anything(self, state):
        return (
            self.hit_tail(state) or
            self.hit_wall(state) or
            self.hit_obstacle(state)
        )

    def hit_obstacle(self, state):
        if not state["safe_map_snake"]:
            return False

        hx, hy = state["head_position"]
        w, h = len(state["safe_map_snake"][0]), len(state["safe_map_snake"])

        px = int(hx / state["map_size"][0] * w)
        py = int(hy / state["map_size"][1]  * h)

        px = max(0, min(w - 1, px))
        py = max(0, min(h - 1, py))

        return state["safe_map_snake"][py][px] == 0

    def hit_wall (self, state):
        hpx, hpy = state["head_position"]

        hit = any(
            abs(coord - border) < self.wall_hit_distance
            for coord, border in [
                (hpx, 0),
                (hpy, 0),
                (hpx, state["map_size"][0]),
                (hpy, state["map_size"][1]),
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