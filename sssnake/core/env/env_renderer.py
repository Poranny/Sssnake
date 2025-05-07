import numpy as np
from sssnake.core.env.env_types import FullState

class SnakeRenderer:

    @staticmethod
    def rgb_array(state: FullState, out_size: int = 200) -> np.ndarray:
        H = W = out_size
        img = np.zeros((H, W, 3), dtype=np.uint8)

        safe = state.safe_map_snake
        if safe.ndim == 2:
            k = H // safe.shape[0]
            obst = np.kron(1 - safe, np.ones((k, k), dtype=np.uint8))
            img[:obst.shape[0], :obst.shape[1]][obst == 1] = (255, 255, 255)

        def to_px(xy):
            x, y = xy
            return int(x / state.map_size * W), int(y / state.map_size * H)

        cx, cy = to_px(state.candy_position)
        img[cy-2:cy+3, cx-2:cx+3] = (220, 30, 30)

        for sx, sy in state.segments_positions[: state.segments_num]:
            px, py = to_px((sx, sy))
            img[py-2:py+3, px-2:px+3] = (60, 200, 60)

        hx, hy = to_px(state.head_position)
        img[hy-3:hy+4, hx-3:hx+4] = (0, 255, 0)

        return img