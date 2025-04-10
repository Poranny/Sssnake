import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

from sssnake.core.rendering.canvas_corners_masking import add_corners

class GameRenderer:
    def __init__(self, width, height, supersample_factor=2):
        self.supersample_factor = supersample_factor
        self.width = width
        self.height = height

        self.high_res_width = width * self.supersample_factor
        self.high_res_height = height * self.supersample_factor

        self.canvas_id = None
        self.canvas = None
        self.frame_buffer  = None
        self.parent_bg_col = None
        self.base_bg = None

        self.envinfo = {}
        self.pos_mult_x = 1
        self.pos_mult_y = 1

        self.offscreen = Image.new("RGBA", (self.high_res_width, self.high_res_height), "black")
        self.draw = ImageDraw.Draw(self.offscreen)

    def set_envinfo(self, envinfo):
        self.envinfo = envinfo

        self.pos_mult_x = self.high_res_width / envinfo["map_size"][0]
        self.pos_mult_y = self.high_res_height / envinfo["map_size"][1]

    def set_parent(self, parent):
        self.parent_bg_col = parent.cget("fg_color")
        self.canvas = tk.Canvas(parent, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        base = Image.new("RGBA", (self.high_res_width, self.high_res_height), "black")

        self.base_bg = add_corners(base, rad=5 * self.supersample_factor, fill_color=self.parent_bg_col[1])
        self.offscreen.paste(self.base_bg, (0, 0))
        self.frame_buffer = ImageTk.PhotoImage(self.back_original_size())

        self.canvas_id = self.canvas.create_image(0, 0, anchor="nw", image=self.frame_buffer)

    def clear(self):
        if self.base_bg is not None:
            self.offscreen.paste(self.base_bg, (0, 0))
        self.offscreen_render()

    def render(self, state: dict):
        self.clear()
        head_x, head_y = state["head_position"]
        radius = 5 * self.supersample_factor

        self.draw.ellipse(
            (
                (head_x * self.supersample_factor - radius) * self.pos_mult_x / self.supersample_factor,
                (head_y * self.supersample_factor - radius) * self.pos_mult_y / self.supersample_factor,
                (head_x * self.supersample_factor + radius) * self.pos_mult_x / self.supersample_factor,
                (head_y * self.supersample_factor + radius) * self.pos_mult_y / self.supersample_factor,
            ),
            fill="white"
        )

        self.offscreen_render()

    def back_original_size(self):
        return self.offscreen.resize((self.width, self.height), resample=Image.LANCZOS)

    def offscreen_render(self):
        final_img = self.back_original_size() if self.supersample_factor > 1 else self.offscreen

        self.frame_buffer = ImageTk.PhotoImage(final_img)
        if self.canvas_id is not None:
            self.canvas.itemconfig(self.canvas_id, image=self.frame_buffer)