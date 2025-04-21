import math
import random
import tkinter as tk
from PIL import Image, ImageTk

from sssnake.core.rendering.canvas_corners_masking import add_corners

class Renderer:

    def __init__(self, width: int, height: int):
        self.parent = None
        self.width = width
        self.height = height

        self.offscreen = Image.new("RGBA", (self.width, self.height), "black")

        self.canvas = None
        self.frame_buffer = None
        self.parent_bg_col = None

        self.base_bg = None
        self.obstacles_texture = None
        self._head_sprite_base = Image.open("data/textures/head.png").convert("RGBA")
        self._segment_sprite_base = Image.open("data/textures/segment.png").convert("RGBA")
        self._candy_sprite_base = Image.open("data/textures/candy.png").convert("RGBA")

        self._sprite_cache: dict[tuple[int, int], Image.Image] = {}
        self._candy_angles: dict[tuple[int, int], float] = {}

    def _get_sprite(self, base: Image.Image, size: int) -> Image.Image:
        key = (id(base), size)
        try:
            return self._sprite_cache[key]
        except KeyError:
            size = max(1, size)
            sprite = base.resize((size, size), Image.LANCZOS)
            self._sprite_cache[key] = sprite
            return sprite

    def _load_background_texture(self, img_path: str):
        if not img_path:
            return None
        tex = (
            Image.open(img_path)
            .convert("L")
            .resize((self.width, self.height), Image.LANCZOS)
            .convert("RGBA")
        )
        return add_corners(tex, rad=5, fill_color=self.parent_bg_col[1])

    def set_render_config(self, render_config):
        self.obstacles_texture = None
        bg_path = render_config.get("map_bitmap_path")

        if bg_path and self.parent:
            self.obstacles_texture = self._load_background_texture(bg_path)
            if self.obstacles_texture:
                self.offscreen.paste(self.obstacles_texture, (0, 0), self.obstacles_texture)

    def set_parent(self, mainview):
        self.parent = mainview.get_render_frame()
        self.parent_bg_col = self.parent.cget("fg_color")

        self.canvas = tk.Canvas(
            self.parent,
            width=self.width,
            height=self.height,
            bg=self.parent_bg_col[1],
            highlightthickness=0,
        )
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        base = Image.new("RGBA", (self.width, self.height), "black")
        self.base_bg = add_corners(base, rad=5, fill_color=self.parent_bg_col[1])
        self.offscreen.paste(self.base_bg, (0, 0))

        self.frame_buffer = ImageTk.PhotoImage(self.offscreen)
        self.canvas_id = self.canvas.create_image(0, 0, anchor="nw", image=self.frame_buffer)

        self.clear()

    def clear(self):
        if self.base_bg is not None:
            self.offscreen.paste(self.base_bg, (0, 0))
        else:
            self.offscreen.paste("black", (0, 0, self.width, self.height))

        if self.obstacles_texture is not None:
            self.offscreen.paste(self.obstacles_texture, (0, 0), self.obstacles_texture)

    def compute_render(self, state: dict):
        self.clear()

        map_w, map_h = state["map_size"]

        head_r, seg_r, candy_r = 1.5, 1.3, 1.45

        cx, cy = state["candy_position"]
        candy_px = max(1, int(2 * candy_r * self.width / map_w))
        base_candy_sprite = self._get_sprite(self._candy_sprite_base, candy_px)

        pos_key = (int(cx), int(cy))
        if pos_key not in self._candy_angles:
            self._candy_angles[pos_key] = random.uniform(140, 220)
        candy_angle = self._candy_angles[pos_key]

        candy_sprite = base_candy_sprite.rotate(
            candy_angle, expand=True, resample=Image.BICUBIC
        )
        cw, ch = candy_sprite.size

        self.offscreen.paste(
            candy_sprite,
            (
                int(cx * self.width / map_w - cw / 2),
                int(cy * self.height / map_h - ch / 2),
            ),
            candy_sprite,
        )

        seg_px = max(1, int(2 * seg_r * self.width / map_w))
        base_seg_sprite = self._get_sprite(self._segment_sprite_base, seg_px)

        for idx, (sx, sy) in enumerate(state["segments_positions"]):
            tx, ty = (state["head_position"] if idx == 0 else state["segments_positions"][idx - 1])
            dx, dy = tx - sx, ty - sy
            angle = math.degrees(math.atan2(-dy, dx)) + 90

            seg_sprite = base_seg_sprite.rotate(angle, expand=True, resample=Image.BICUBIC)
            sw, sh = seg_sprite.size

            self.offscreen.paste(
                seg_sprite,
                (
                    int(sx * self.width / map_w - sw / 2),
                    int(sy * self.height / map_h - sh / 2),
                ),
                seg_sprite,
            )

        hx, hy = state["head_position"]
        head_angle = state["head_direction"] + 180
        head_px = max(1, int(2 * head_r * self.width / map_w))

        head_sprite = self._get_sprite(self._head_sprite_base, head_px)
        head_sprite = head_sprite.rotate(head_angle, expand=True, resample=Image.BICUBIC)
        hw, hh = head_sprite.size

        self.offscreen.paste(
            head_sprite,
            (
                int(hx * self.width / map_w - hw / 2),
                int(hy * self.height / map_h - hh / 2),
            ),
            head_sprite,
        )

        return self.offscreen

    def _update_canvas(self, final_img):
        self.frame_buffer.paste(final_img)

    def async_render(self, state: dict):
        final = self.compute_render(state)
        self.canvas.after(0, lambda img=final: self._update_canvas(img))