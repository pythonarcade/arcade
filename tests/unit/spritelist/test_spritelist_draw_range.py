import pytest

import arcade
from arcade.resources import resolve
from arcade.sprite_list import sprite_list as sprite_list_module


@pytest.fixture(params=["buffer", "texture"])
def storage_backend(request, monkeypatch):
    if request.param == "texture":
        monkeypatch.setattr(
            sprite_list_module, "SpriteListBufferData", sprite_list_module.SpriteListTextureData
        )


COLORS = [arcade.color.RED, arcade.color.GREEN, arcade.color.BLUE, arcade.color.YELLOW]


def make_sprites(*, lazy=False):
    sprites = arcade.SpriteList(lazy=lazy)
    for i, color in enumerate(COLORS):
        sprites.append(
            arcade.SpriteSolidColor(4, 4, center_x=10 + 10 * i, center_y=10, color=color)
        )
    return sprites


def test_render_control(offscreen, storage_backend):
    sprites = make_sprites()
    sprites.draw()
    for i, color in enumerate(COLORS):
        assert offscreen.read_pixel(10 + 10 * i, 10) == color[:3]


@pytest.mark.parametrize(
    "start, stop, expected",
    [
        (1, 3, [1, 2]),
        (0, None, [0, 1, 2, 3]),
        (-3, -1, [1, 2]),
        (-20, 2, [0, 1]),
        (2, 20, [2, 3]),
        (3, 1, []),
        (10, None, []),
    ],
)
def test_slice_bounds(offscreen, storage_backend, start, stop, expected):
    sprites = make_sprites(lazy=True)
    sprites.draw_range(start, stop)
    for i, color in enumerate(COLORS):
        assert offscreen.read_pixel(10 + 10 * i, 10) == (color[:3] if i in expected else (0, 0, 0))


def test_logical_order_after_slot_reuse(offscreen, storage_backend):
    sprites = make_sprites()
    removed = sprites[1]
    sprites.remove(removed)
    sprites.reverse()
    sprites.append(removed)
    assert [sprites.sprite_slot[sprite] for sprite in sprites] != list(range(len(sprites)))
    sprites.draw_range(1, 3)
    for sprite in sprites:
        expected = sprite.color[:3] if sprite in sprites[1:3] else (0, 0, 0)
        assert offscreen.read_pixel(int(sprite.center_x), 10) == expected


def test_range_preserves_painter_order(offscreen, storage_backend):
    sprites = make_sprites()
    for sprite in sprites:
        sprite.center_x = 10
    sprites.reverse()
    sprites.draw_range(1, 3)
    assert offscreen.read_pixel(10, 10) == sprites[2].color[:3]


def test_offset_does_not_leak_to_whole_draw(offscreen, storage_backend):
    sprites = make_sprites()
    other = make_sprites()
    for current in (sprites, other, sprites):
        offscreen.clear()
        sprites.draw_range(2, 3)
        assert offscreen.read_pixel(10, 10) == (0, 0, 0)
        offscreen.clear()
        current.draw()
        for i, color in enumerate(COLORS):
            assert offscreen.read_pixel(10 + 10 * i, 10) == color[:3]


def test_crosses_texture_row_boundary(offscreen, storage_backend):
    sprites = arcade.SpriteList(capacity=1000)
    for i in range(300):
        sprites.append(arcade.SpriteSolidColor(1, 1, center_x=i + 0.5, center_y=0.5))
    sprites.draw_range(254, 258)
    for i in range(300):
        assert offscreen.read_pixel(i, 0) == ((255, 255, 255) if 254 <= i < 258 else (0, 0, 0))


@pytest.mark.parametrize("state", ["empty", "range", "invisible", "transparent"])
def test_noop_keeps_lazy_list_uninitialized(ctx, state):
    sprites = make_sprites(lazy=True)
    if state == "empty":
        sprites.clear()
    elif state == "invisible":
        sprites.visible = False
    elif state == "transparent":
        sprites.alpha = 0
    sprites.draw_range(2, 2 if state == "range" else 3)
    assert not sprites._initialized


def test_render_options(offscreen, storage_backend):
    sprites = make_sprites()
    sprites.color = (128, 255, 255)
    offscreen.fbo.clear(color=(0, 0, 64))
    sprites.draw_range(0, 1, filter=arcade.gl.NEAREST, blend_function=offscreen.ctx.BLEND_ADDITIVE)
    assert offscreen.read_pixel(10, 10) == (128, 0, 64)
    assert offscreen.read_pixel(20, 10) == (0, 0, 64)
    assert sprites.atlas.texture.filter == (arcade.gl.NEAREST, arcade.gl.NEAREST)


def test_window_view_draw(window, storage_backend):
    sprites = make_sprites()

    class RangeView(arcade.View):
        def on_draw(self):
            self.clear()
            sprites.draw_range(1, 3)
            assert arcade.get_pixel(10, 10) == (0, 0, 0)
            assert arcade.get_pixel(20, 10) == COLORS[1][:3]
            assert arcade.get_pixel(30, 10) == COLORS[2][:3]
            assert arcade.get_pixel(40, 10) == (0, 0, 0)

    window.background_color = arcade.color.BLACK
    window.show_view(RangeView())
    window.test(2)


def test_legacy_texture_shader(offscreen, monkeypatch, tmp_path):
    monkeypatch.setattr(
        sprite_list_module, "SpriteListBufferData", sprite_list_module.SpriteListTextureData
    )
    sprites = make_sprites()
    source = resolve(":system:shaders/sprites/sprite_list_simple_vs.glsl").read_text()
    source = source.replace("uniform int sprite_start;", "").replace(
        "gl_InstanceID + sprite_start", "gl_InstanceID"
    )
    shader = tmp_path / "legacy_vertex.glsl"
    shader.write_text(source)
    program = offscreen.ctx.load_program(
        vertex_shader=shader, fragment_shader=":system:shaders/sprites/sprite_list_simple_fs.glsl"
    )
    for unit, name in enumerate(
        [
            "sprite_texture",
            "uv_texture",
            "pos_data",
            "size_data",
            "color_data",
            "texture_id_data",
            "index_data",
        ]
    ):
        program[name] = unit
    sprites.data.program = program
    sprites.draw_range(0, 1)
    assert offscreen.read_pixel(10, 10) == COLORS[0][:3]
    offscreen.clear()
    previous_blend = offscreen.ctx.blend_func
    with pytest.raises(ValueError, match="sprite_start"):
        sprites.draw_range(1, 3, blend_function=offscreen.ctx.BLEND_ADDITIVE)
    assert offscreen.ctx.blend_func == previous_blend
    sprites.draw()
    for i, color in enumerate(COLORS):
        assert offscreen.read_pixel(10 + 10 * i, 10) == color[:3]


def test_texture_offset_restored_after_render_error(offscreen, monkeypatch):
    monkeypatch.setattr(
        sprite_list_module, "SpriteListBufferData", sprite_list_module.SpriteListTextureData
    )
    sprites = make_sprites()

    def fail_render(*args, **kwargs):
        assert sprites.data.program["sprite_start"] == 2
        raise RuntimeError("Injected rendering failure")

    monkeypatch.setattr(arcade.gl.Geometry, "render", fail_render)
    with pytest.raises(RuntimeError, match="Injected"):
        sprites.draw_range(2, 3)
    assert sprites.data.program["sprite_start"] == 0
