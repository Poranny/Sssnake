from __future__ import annotations

import math
import random
from importlib.resources import files
from typing import Dict, Tuple

import numpy as np
from PIL import Image
from PIL.Image import Resampling

from sssnake.env.utils.state_def import RenderState

texture_path = files("sssnake.env.textures")

_HEAD_BASE = Image.open(str(texture_path / "head.png")).convert("RGBA")
_SEGMENT_BASE = Image.open(str(texture_path / "segment.png")).convert("RGBA")
_CANDY_BASE = Image.open(str(texture_path / "candy.png")).convert("RGBA")

_sprite_cache: Dict[Tuple[int, int], Image.Image] = {}
_candy_angles: Dict[Tuple[int, int], float] = {}


def get_cached_sprite(base: Image.Image, size: int) -> Image.Image:
    key = (id(base), size)
    if key not in _sprite_cache:
        sz = max(1, size)
        _sprite_cache[key] = base.resize((sz, sz), Resampling.LANCZOS)
    return _sprite_cache[key]


def state_to_array(
    render_state: RenderState, collision_bitmap_path: str = "", out_size: int = 400
) -> np.ndarray:
    if collision_bitmap_path:
        off = (
            Image.open(collision_bitmap_path)
            .convert("L")
            .resize((out_size, out_size), Resampling.LANCZOS)
            .convert("RGBA")
        )
    else:
        off = Image.new("RGBA", (out_size, out_size), "black")

    map_size = render_state.map_size

    # candy
    cx, cy = render_state.candy_position
    candy_px = max(1, int(2 * 1.45 * out_size / map_size))
    candy_sprite = get_cached_sprite(_CANDY_BASE, candy_px)
    key = (int(cx), int(cy))
    if key not in _candy_angles:
        _candy_angles[key] = random.uniform(140, 220)
    candy_sprite = candy_sprite.rotate(_candy_angles[key], expand=True, resample=Resampling.BICUBIC)
    cw, ch = candy_sprite.size
    off.paste(
        candy_sprite,
        (int(cx * out_size / map_size - cw / 2), int(cy * out_size / map_size - ch / 2)),
        candy_sprite,
    )

    # segments
    seg_px = max(1, int(2 * 1.3 * out_size / map_size))
    seg_base = get_cached_sprite(_SEGMENT_BASE, seg_px)

    positions = render_state.segments_positions[: int(render_state.segments_num)]
    prev_positions = [render_state.head_position] + list(positions[:-1])

    for (sx, sy), (tx, ty) in zip(reversed(positions), reversed(prev_positions), strict=False):
        dx, dy = tx - sx, ty - sy
        angle = math.degrees(math.atan2(-dy, dx)) + 90
        seg_sprite = seg_base.rotate(angle, expand=True, resample=Resampling.BICUBIC)
        sw, sh = seg_sprite.size
        off.paste(
            seg_sprite,
            (int(sx * out_size / map_size - sw / 2), int(sy * out_size / map_size - sh / 2)),
            seg_sprite,
        )

    # head
    head_px = max(1, int(2 * 1.5 * out_size / map_size))
    head_sprite = get_cached_sprite(_HEAD_BASE, head_px)
    head_sprite = head_sprite.rotate(
        render_state.head_direction + 180,
        expand=True,
        resample=Resampling.BICUBIC,
    )
    hw, hh = head_sprite.size
    hx, hy = render_state.head_position
    off.paste(
        head_sprite,
        (int(hx * out_size / map_size - hw / 2), int(hy * out_size / map_size - hh / 2)),
        head_sprite,
    )

    return np.array(off, dtype=np.uint8)
