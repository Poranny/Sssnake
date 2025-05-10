import math
import random
import numpy as np
from PIL import Image
from sssnake.env.utils.state_def import RenderState
from importlib.resources import files

texture_path = files("sssnake.env.textures")

_HEAD_BASE    = Image.open(texture_path.joinpath("head.png")).convert("RGBA")
_SEGMENT_BASE = Image.open(texture_path.joinpath("segment.png")).convert("RGBA")
_CANDY_BASE   = Image.open(texture_path.joinpath("candy.png")).convert("RGBA")

_sprite_cache = {}
_candy_angles = {}

def get_sprite(base: Image.Image, size: int) -> Image.Image:
    key = (id(base), size)
    if key not in _sprite_cache:
        sz = max(1, size)
        _sprite_cache[key] = base.resize((sz, sz), Image.LANCZOS)
    return _sprite_cache[key]

def state_to_array(
    render_state: RenderState,
    collision_bitmap_path: str = "",
    out_size: int = 400
) -> np.ndarray:
      # 0) Bg
    if collision_bitmap_path:
        off = (
            Image.open(collision_bitmap_path)
                 .convert("L")
                 .resize((out_size, out_size), Image.LANCZOS)
                 .convert("RGBA")
        )
    else:
        off = Image.new("RGBA", (out_size, out_size), "black")

    map_size = render_state.map_size

    # 1) Candy
    cx, cy = render_state.candy_position
    candy_r = 1.45
    candy_px = max(1, int(2 * candy_r * out_size / map_size))
    candy_sprite = get_sprite(_CANDY_BASE, candy_px)
    key = (int(cx), int(cy))
    if key not in _candy_angles:
        _candy_angles[key] = random.uniform(140, 220)
    candy_sprite = candy_sprite.rotate(_candy_angles[key], expand=True, resample=Image.BICUBIC)
    cw, ch = candy_sprite.size
    off.paste(
        candy_sprite,
        (int(cx * out_size / map_size - cw/2), int(cy * out_size / map_size - ch/2)),
        candy_sprite
    )

      # 2) Segments
    seg_r = 1.3
    seg_px = max(1, int(2 * seg_r * out_size / map_size))
    seg_base = get_sprite(_SEGMENT_BASE, seg_px)

      # Wyciągamy tylko tyle segmentów, ile faktycznie używamy
    positions = render_state.segments_positions[:render_state.segments_num]
      # Tworzymy listę "poprzednich" pozycji: głowa + wszystkie segmenty oprócz ostatniego
    prev_positions = [render_state.head_position] + positions[:-1]

      # Iterujemy od ostatniego segmentu do pierwszego
    for (sx, sy), (tx, ty) in zip(reversed(positions), reversed(prev_positions)):
          # dx, dy ze „względu” na poprzedni segment (czy głowę, jeśli to segment #0)
        dx, dy = tx - sx, ty - sy
        angle = math.degrees(math.atan2(-dy, dx)) + 90

          # obracamy sprite i wycinamy jego rozmiar
        seg_sprite = seg_base.rotate(angle, expand=True, resample=Image.BICUBIC)
        sw, sh = seg_sprite.size

          # wklejamy na obrazek, centrując
        off.paste(
           seg_sprite,
         (int(sx * out_size / map_size - sw / 2),
               int(sy * out_size / map_size - sh / 2)),
           seg_sprite
        )

    # 3) Head
    head_r = 1.5
    head_px = max(1, int(2 * head_r * out_size / map_size))
    head_sprite = get_sprite(_HEAD_BASE, head_px)
    head_angle = render_state.head_direction + 180
    head_sprite = head_sprite.rotate(head_angle, expand=True, resample=Image.BICUBIC)
    hw, hh = head_sprite.size
    hx, hy = render_state.head_position
    off.paste(
        head_sprite,
        (int(hx * out_size / map_size - hw/2), int(hy * out_size / map_size - hh/2)),
        head_sprite
    )

    return np.array(off, dtype=np.uint8)
