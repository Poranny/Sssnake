import tkinter as tk
from PIL import Image, ImageTk
import aggdraw

from sssnake.core.rendering.canvas_corners_masking import add_corners

class Renderer:
    def __init__(self, width, height):
        self.parent = None
        self.width = width
        self.height = height

        self.offscreen = Image.new("RGBA", (self.width, self.height), "black")
        self.draw = aggdraw.Draw(self.offscreen)
        self.pen = aggdraw.Pen("white", 1)
        self.brush = aggdraw.Brush("white")

        self.canvas_id = None
        self.canvas = None
        self.frame_buffer = None
        self.parent_bg_col = None

        self.base_bg = None
        self.obstacles_texture = None

        self.obstacles_map = {}

    def _load_background_texture(self, img_path: str) -> Image.Image:
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
                self.offscreen.paste(
                    self.obstacles_texture, (0, 0), self.obstacles_texture
                )

    def set_parent(self, mainview):
        self.parent = mainview.get_render_frame()
        self.parent_bg_col = self.parent.cget("fg_color")

        self.canvas = tk.Canvas(
            self.parent,
            width=self.width,
            height=self.height,
            bg=self.parent_bg_col[1],
            highlightthickness=0
        )

        self.canvas.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        base = Image.new("RGBA", (self.width, self.height), "black")
        self.base_bg = add_corners(base, rad=5, fill_color=self.parent_bg_col[1])
        self.offscreen.paste(self.base_bg, (0, 0))

        self.frame_buffer = ImageTk.PhotoImage(self.offscreen)  # tylko raz
        self.canvas_id = self.canvas.create_image(0, 0, anchor="nw",
                                                  image=self.frame_buffer)
        self.clear()

    def clear(self):
        if self.base_bg is not None:
            self.offscreen.paste(self.base_bg, (0, 0))
        else:
            self.offscreen.paste(
                "black",
                (0, 0, self.width, self.height)
            )
        if self.obstacles_texture is not None:
            self.offscreen.paste(self.obstacles_texture, (0, 0), self.obstacles_texture)

    def compute_render(self, state: dict) -> Image.Image:
        self.clear()
        self.draw = aggdraw.Draw(self.offscreen)

        head_r = 1.25
        seg_r = 1
        candy_r = 1

        def draw_circle(x, y, r):
            bbox = (
                (x - r) * (self.width / state['map_size'][0]),
                (y - r) * (self.height / state['map_size'][1]),
                (x + r) * (self.width / state['map_size'][0]),
                (y + r) * (self.height / state['map_size'][1]),
            )
            self.draw.ellipse(bbox, self.brush)

        hx, hy = state['head_position']
        draw_circle(hx, hy, head_r)

        cx, cy = state['candy_position']
        draw_circle(cx, cy, candy_r)

        for sx, sy in state['segments_positions']:
            draw_circle(sx, sy, seg_r)

        self.draw.flush()

        return self.offscreen

    def update_canvas(self, final_img: Image.Image):
        self.frame_buffer.paste(final_img)

    def async_render(self, state: dict):
        final = self.compute_render(state)
        self.canvas.after(0, lambda: self.update_canvas(final))
