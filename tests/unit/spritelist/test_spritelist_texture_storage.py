"""
On WebGL, a SpriteList keeps its sprite data in textures instead of buffers.
These tests use that storage on desktop OpenGL, so they run in CI.

The shader reads the textures as rows of 256 sprites. They used to be
created as a single row as wide as the capacity, so a list whose storage
was created with a capacity over 256 only drew its first 256 sprites.
"""

import pytest

import arcade
from arcade.sprite_list import sprite_list as sprite_list_module


@pytest.fixture
def texture_storage(monkeypatch):
    """New SpriteLists use the WebGL storage, in textures"""
    monkeypatch.setattr(
        sprite_list_module, "SpriteListBufferData", sprite_list_module.SpriteListTextureData
    )


def _add_pixels(sprites, count):
    for i in range(count):
        x, y = (i % 30) * 3 + 1.5, (i // 30) * 3 + 1.5
        sprites.append(arcade.SpriteSolidColor(1, 1, center_x=x, center_y=y))


def _drawn(ctx, sprites):
    """How many pixels the sprites cover, one per sprite"""
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((100, 100), components=4)])
    with fbo.activate():
        fbo.clear()
        sprites.draw()
    data = fbo.read(components=4)
    return sum(1 for i in range(3, len(data), 4) if data[i] > 0)


@pytest.mark.parametrize("capacity", [100, 256, 1000, 1024, 3000])
def test_created_with_capacity(ctx, texture_storage, capacity):
    sprites = arcade.SpriteList(capacity=capacity)
    assert isinstance(sprites._data, sprite_list_module.SpriteListTextureData)
    _add_pixels(sprites, 600)
    assert _drawn(ctx, sprites) == 600


def test_clear_after_growing(ctx, texture_storage):
    """clear() keeps the grown capacity and creates the storage again"""
    sprites = arcade.SpriteList()
    _add_pixels(sprites, 300)
    sprites.clear()
    _add_pixels(sprites, 400)
    assert _drawn(ctx, sprites) == 400


def test_lazy_list_grown_before_first_draw(ctx, texture_storage):
    """A lazy list creates its storage at the capacity it has grown to"""
    sprites = arcade.SpriteList(lazy=True)
    _add_pixels(sprites, 400)
    assert _drawn(ctx, sprites) == 400


def test_storage_is_rows_of_256(ctx, texture_storage):
    sprites = arcade.SpriteList(capacity=1024)
    data = sprites._data
    for texture in (
        data._storage_pos_angle,
        data._storage_size,
        data._storage_color,
        data._storage_texture_id,
        data._storage_index,
    ):
        assert texture.size == (256, 4)
