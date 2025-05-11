import numpy as np
import pytest
from PIL import Image

from sssnake.env.core.renderer import get_cached_sprite, state_to_array
from sssnake.env.utils.state_def import RenderState


def test_get_cached_sprite(simple_render_state):
    base = Image.new("RGBA", (4, 4), "black")
    size = 8

    sprite1 = get_cached_sprite(base, size)
    assert isinstance(sprite1, Image.Image)
    assert sprite1.size == (size, size)

    sprite2 = get_cached_sprite(base, size)
    assert sprite1 is sprite2


def test_state_to_array(simple_render_state, tmp_path):
    arr = state_to_array(simple_render_state, collision_bitmap_path="", out_size=16)

    assert isinstance(arr, np.ndarray)
    assert arr.shape == (16, 16, 4), f"Wrong shape: {arr.shape}"
    assert arr.dtype == np.uint8

    bg = Image.new("L", (4, 4), color=128)
    bg_path = tmp_path / "bg.png"
    bg.save(bg_path)

    arr2 = state_to_array(
        simple_render_state, collision_bitmap_path=str(bg_path), out_size=8
    )
    assert arr2.shape == (8, 8, 4)

    assert arr2.mean() > 0, "Some pixels should be white"
