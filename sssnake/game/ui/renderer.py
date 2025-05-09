from __future__ import annotations
import tkinter as tk
from PIL import Image, ImageTk

from sssnake.env.utils.state_def import RenderState
from sssnake.env.utils.config_def import RenderConfig
from sssnake.env.core.renderer import state_to_array

class Renderer:
    def __init__(self, width: int, height: int):
        self.parent = None
        self.width = width
        self.height = height

        self.canvas = None
        self.frame_buffer = None
        self.canvas_id = None

        self.render_config: RenderConfig | None = None

    def set_parent(self, mainview):
        self.parent = mainview.get_render_frame()
        bg_col = self.parent.cget("fg_color")[1]

        self.canvas = tk.Canvas(
            self.parent, width=self.width, height=self.height,
            bg=bg_col, highlightthickness=0
        )
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        blank = Image.new("RGBA", (self.width, self.height), "black")
        self.frame_buffer = ImageTk.PhotoImage(blank)
        self.canvas_id = self.canvas.create_image(0, 0, anchor="nw", image=self.frame_buffer)

    def set_render_config(self, render_config: RenderConfig):
        self.render_config = render_config

    def compute_render(self, render_state: RenderState) -> Image.Image:
        bmp = ""
        if self.render_config:
            bmp = self.render_config.map_bitmap_path

        arr = state_to_array(
            render_state,
            collision_bitmap_path=bmp,
            out_size=self.width
        )

        return Image.fromarray(arr, mode="RGBA")

    def async_render(self, render_state: RenderState):
        img = self.compute_render(render_state)
        self.frame_buffer.paste(img)