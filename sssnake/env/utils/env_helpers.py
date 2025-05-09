from __future__ import annotations

import json
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image

from sssnake.env.utils.config_def import EnvSpec, ResetOptions


def load_obstacles_map(path: Union[str, Path], col_res: int) -> np.ndarray:
    if not path or str(path) == "":
        return np.zeros((col_res, col_res), dtype=np.int8)

    img = Image.open(path).convert("L").resize((col_res, col_res), Image.LANCZOS)

    arr = np.asarray(img, dtype=np.uint8)
    obstacles = (arr > 128).astype(np.int8)

    return obstacles


def generate_safe_map(
    margin_units: float,
    map_size: float,
    obstacles_map: np.ndarray,
) -> np.ndarray:

    obst = np.asarray(obstacles_map, dtype=np.int8)
    n = obst.shape[0]
    margin = max(int(margin_units * (n / map_size)), 1)

    if obst.max() == 0:
        return np.ones_like(obst, dtype=np.int8)

    dilated = np.zeros_like(obst, dtype=np.int8)

    for dy in range(-margin, margin + 1):
        y_src = slice(max(0, -dy), min(n, n - dy))
        y_dst = slice(max(0,  dy), min(n, n + dy))
        for dx in range(-margin, margin + 1):
            x_src = slice(max(0, -dx), min(n, n - dx))
            x_dst = slice(max(0,  dx), min(n, n + dx))

            dilated[y_dst, x_dst] = np.maximum(
                dilated[y_dst, x_dst],
                obst[y_src, x_src]
            )

    safe_map = 1 - dilated
    return safe_map.astype(np.int8)



def load_config(jsonpath: str):
    with open(jsonpath, "r", encoding="utf-8") as f:
        raw = json.load(f)
    spec = EnvSpec.from_dict(raw["env_spec"])
    opts = ResetOptions.from_dict(raw["reset_options"])
    return spec, opts