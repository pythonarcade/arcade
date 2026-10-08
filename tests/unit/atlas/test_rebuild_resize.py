import PIL.Image
import pytest
from pyglet.graphics.atlas import AllocatorException

import arcade
from arcade import DefaultTextureAtlas, load_texture


def test_rebuild(ctx, common):
    """Build and atlas and rebuild it"""
    # 36 x 36 : 6a9c1abbf2719dc59b9ebe2b7c2a6d662432dfe9e3d77f202ee042f98caf3616
    tex_small = load_texture(":resources:images/topdown_tanks/treeGreen_small.png")
    # 64 x 64 : b883bf9ece9ab2dc738b24dc6bf664b056bea59503040eac15e7374e4a806b1b
    tex_big = load_texture(":resources:images/topdown_tanks/treeGreen_large.png")

    atlas = DefaultTextureAtlas((104, 104), border=1)
    slot_a, region_a = atlas.add(tex_big)
    slot_b, region_b = atlas.add(tex_small)
    region_a = atlas.get_texture_region_info(tex_big.atlas_name)
    region_b = atlas.get_texture_region_info(tex_small.atlas_name)
    common.check_internals(
        atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0
    )

    # Re-build and check states
    atlas.rebuild()
    assert slot_a == atlas.get_texture_id(tex_big)
    assert slot_b == atlas.get_texture_id(tex_small)
    region_aa = atlas.get_texture_region_info(tex_big.atlas_name)
    region_bb = atlas.get_texture_region_info(tex_small.atlas_name)
    common.check_internals(
        atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0
    )

    # The textures have switched places in the atlas and should
    # have the same left position
    assert region_a.texture_coordinates[0] == region_bb.texture_coordinates[0]
    # check that textures moved at the very least
    assert region_b.texture_coordinates[0] != region_bb.texture_coordinates[0]
    assert region_a.texture_coordinates[0] != region_aa.texture_coordinates[0]

    common.check_internals(
        atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0
    )


def test_resize(ctx, common):
    """Attempt to resize the atlas"""
    atlas = DefaultTextureAtlas((50, 100), border=1, auto_resize=False)
    # sha256 0118296e6c16a0113a31e71a64cac301152e44d9623ca2db92bbbfb166dd22fa
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (255, 0, 0, 255)))
    # sha256 81776589b8a141ac4ac01cce9cf16ee239fb82564c8ec026473aa185c1d6786e
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (0, 255, 0, 255)))

    atlas.add(t1)
    atlas.add(t2)
    common.check_internals(
        atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0
    )
    atlas.resize((50, 100))
    common.check_internals(
        atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0
    )

    assert atlas._textures_added == 2
    assert atlas._finalizers_created == 2
    assert atlas._textures_removed == 0

    # Make atlas so small the current textures won't fit
    with pytest.raises(AllocatorException):
        atlas.resize((50, 99))

    # Resize past max size
    atlas = DefaultTextureAtlas((50, 50), border=0)
    atlas._max_size = 60, 60
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (255, 0, 0, 255)))
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (0, 255, 0, 255)))
    atlas.add(t1)
    common.check_internals(
        atlas, images=1, textures=1, unique_textures=1, textures_added=1, textures_removed=0
    )

    with pytest.raises(AllocatorException):
        atlas.add(t2)


@pytest.mark.parametrize("atlas_size", [(32, 32), (256, 256)])
def test_render_into_auto_resize(ctx, atlas_size):
    atlas = DefaultTextureAtlas(atlas_size, border=0)
    target = arcade.Texture(PIL.Image.new("RGBA", (32, 32), (0, 255, 0, 255)))
    source = arcade.Texture(PIL.Image.new("RGBA", (64, 64), (255, 0, 0, 255)))
    atlas.add(target)
    previous_fbo = ctx.active_framebuffer
    previous_camera = ctx.current_camera

    with atlas.render_into(target):
        arcade.draw_texture_rect(source, arcade.LBWH(8, 8, 16, 16), atlas=atlas)

    image = atlas.read_texture_image_from_atlas(target)
    assert image.getpixel((16, 16)) == (255, 0, 0, 255)
    assert image.getpixel((0, 0)) == (0, 255, 0, 255)
    assert ctx.active_framebuffer is previous_fbo
    assert ctx.current_camera is previous_camera


@pytest.mark.parametrize("same_atlas", [True, False])
def test_render_into_nested_resize(ctx, same_atlas):
    outer_atlas = DefaultTextureAtlas((64, 64), border=0)
    inner_atlas = outer_atlas if same_atlas else DefaultTextureAtlas((32, 32), border=0)
    outer = arcade.Texture(PIL.Image.new("RGBA", (32, 32), (0, 255, 0, 255)))
    inner = arcade.Texture(PIL.Image.new("RGBA", (16, 16), (0, 0, 0, 255)))
    outer_atlas.add(outer)
    inner_atlas.add(inner)
    previous_fbo = ctx.active_framebuffer
    previous_camera = ctx.current_camera
    old_region = outer_atlas.get_texture_region_info(outer.atlas_name)
    old_position = old_region.x, old_region.y

    with outer_atlas.render_into(outer) as outer_fbo:
        outer_camera = ctx.current_camera
        arcade.draw_rect_filled(arcade.LBWH(0, 0, 8, 8), (0, 0, 255, 255))
        with inner_atlas.render_into(inner) as inner_fbo:
            outer_atlas.resize((128, 128))
            if not same_atlas:
                inner_atlas.resize((64, 64))
            assert ctx.active_framebuffer is inner_fbo
            inner_fbo.clear(color=(255, 0, 0, 255))
        assert ctx.active_framebuffer is outer_fbo
        assert ctx.current_camera is outer_camera
        arcade.draw_rect_filled(arcade.LBWH(8, 8, 8, 8), (255, 255, 0, 255))

    if same_atlas:
        region = outer_atlas.get_texture_region_info(outer.atlas_name)
        assert (region.x, region.y) != old_position
    image = outer_atlas.read_texture_image_from_atlas(outer).transpose(
        PIL.Image.Transpose.FLIP_TOP_BOTTOM
    )
    assert image.getpixel((4, 4)) == (0, 0, 255, 255)
    assert image.getpixel((12, 12)) == (255, 255, 0, 255)
    assert image.getpixel((24, 24)) == (0, 255, 0, 255)
    assert inner_atlas.read_texture_image_from_atlas(inner).getpixel((8, 8)) == (255, 0, 0, 255)
    assert ctx.active_framebuffer is previous_fbo
    assert ctx.current_camera is previous_camera


@pytest.mark.parametrize("raise_error", [False, True])
def test_render_into_resize_restores_state(ctx, raise_error):
    atlas = DefaultTextureAtlas((32, 32), border=0)
    target = arcade.Texture(PIL.Image.new("RGBA", (32, 32), (0, 255, 0, 255)))
    atlas.add(target)
    offscreen = ctx.framebuffer(color_attachments=[ctx.texture((64, 64), components=4)])
    offscreen.viewport = 4, 5, 40, 42
    previous_camera = ctx.current_camera

    with offscreen.activate():
        offscreen.scissor = 6, 7, 8, 9
        previous_projection = ctx.projection_matrix
        previous_view = ctx.view_matrix

        def render():
            with atlas.render_into(target) as fbo:
                atlas.resize((64, 64))
                atlas.resize((128, 128))
                fbo.clear(color=(255, 0, 0, 255))
                if raise_error:
                    raise RuntimeError("drawing failed")

        if raise_error:
            with pytest.raises(RuntimeError, match="drawing failed"):
                render()
        else:
            render()
        assert ctx.active_framebuffer is offscreen
        assert offscreen.viewport == (4, 5, 40, 42)
        assert offscreen.scissor == (6, 7, 8, 9)
        assert ctx.current_camera is previous_camera
        assert ctx.projection_matrix == previous_projection
        assert ctx.view_matrix == previous_view
    assert atlas.read_texture_image_from_atlas(target).getpixel((16, 16)) == (255, 0, 0, 255)


@pytest.mark.parametrize("atlas_size", [(32, 32), (512, 512)])
def test_render_into_repeated_growth_projection(ctx, atlas_size):
    atlas = DefaultTextureAtlas(atlas_size, border=0)
    target = arcade.Texture(PIL.Image.new("RGBA", (32, 32), (0, 255, 0, 255)))
    red = arcade.Texture(PIL.Image.new("RGBA", (64, 64), (255, 0, 0, 255)))
    blue = arcade.Texture(PIL.Image.new("RGBA", (128, 128), (0, 0, 255, 255)))
    atlas.add(target)

    with atlas.render_into(target, projection=(0, 64, 0, 64)):
        arcade.draw_texture_rect(red, arcade.LBWH(0, 0, 16, 16), atlas=atlas)
        arcade.draw_texture_rect(blue, arcade.LBWH(32, 32, 16, 16), atlas=atlas)

    image = atlas.read_texture_image_from_atlas(target).transpose(
        PIL.Image.Transpose.FLIP_TOP_BOTTOM
    )
    assert image.getpixel((4, 4)) == (255, 0, 0, 255)
    assert image.getpixel((20, 20)) == (0, 0, 255, 255)
    assert image.getpixel((28, 28)) == (0, 255, 0, 255)


def test_render_into_resize_with_scissor(ctx):
    atlas = DefaultTextureAtlas((64, 64), border=0)
    target = arcade.Texture(PIL.Image.new("RGBA", (32, 32), (0, 255, 0, 255)))
    atlas.add(target)
    with atlas.render_into(target) as fbo:
        fbo.clear(color=(255, 0, 0, 255))
        fbo.scissor = 0, 0, 4, 4
        atlas.resize((128, 128))
        assert fbo.scissor == (0, 0, 4, 4)
        fbo.scissor = None
    image = atlas.read_texture_image_from_atlas(target)
    assert image.tobytes() == PIL.Image.new("RGBA", (32, 32), (255, 0, 0, 255)).tobytes()


def _red(color):
    return color[0] > 200 and color[1] < 60 and color[2] < 60


def _full_atlas_with_freed_space(can_grow):
    """
    An atlas that's full, with some textures freed, so adding another one
    has to rebuild or grow it. Returns the atlas, the texture to render
    into, and the textures still in it.
    """
    import gc

    atlas = DefaultTextureAtlas((128, 128), border=0)
    max_size = atlas._max_size
    # Fill it without letting it grow
    atlas._max_size = (128, 128)
    target = arcade.Texture(PIL.Image.new("RGBA", (32, 32), (0, 255, 0, 255)))
    atlas.add(target)
    kept = []
    fillers = []
    while True:
        filler = arcade.Texture(PIL.Image.new("RGBA", (24, 24), (0, 0, 255 - len(fillers), 255)))
        if len(fillers) > 40:
            break
        try:
            atlas.add(filler)
        except AllocatorException:
            break
        fillers.append(filler)
    # Free every other filler
    kept = fillers[1::2]
    del fillers, filler
    gc.collect()
    if can_grow:
        atlas._max_size = max_size
    return atlas, target, kept


def _draw_inside(atlas, target):
    """Draw a corner before adding a new texture, then the new texture"""
    big = arcade.Texture(PIL.Image.new("RGBA", (40, 40), (255, 0, 0, 255)))
    with atlas.render_into(target):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, 8, 8), (255, 255, 0, 255))
        arcade.draw_texture_rect(big, arcade.LBWH(16, 16, 16, 16), atlas=atlas)
    return atlas.read_texture_image_from_atlas(target).transpose(
        PIL.Image.Transpose.FLIP_TOP_BOTTOM
    )


def _check_drawing(atlas, target, kept):
    image = _draw_inside(atlas, target)
    # Drawn before and after making room, in the right place
    assert image.getpixel((4, 4)) == (255, 255, 0, 255)
    assert _red(image.getpixel((24, 24)))
    assert image.getpixel((12, 12)) == (0, 255, 0, 255)
    # The other textures weren't drawn on
    for texture in kept:
        data = atlas.read_texture_image_from_atlas(texture).tobytes()
        assert not any(_red(data[i : i + 3]) for i in range(0, len(data), 4))


def test_render_into_rebuild(ctx):
    """
    An atlas that can't grow rebuilds to make room, even while being
    rendered into. The rebuild used to move the texture being drawn into,
    so the drawing went to other textures, and what was drawn before it
    was lost.
    """
    atlas, target, kept = _full_atlas_with_freed_space(can_grow=False)
    rebuilds = []
    rebuild = atlas.rebuild
    atlas.rebuild = lambda: (rebuilds.append(1), rebuild())
    _check_drawing(atlas, target, kept)
    assert rebuilds
    assert atlas.size == (128, 128)


def test_render_into_grows_instead_of_rebuilding(ctx):
    """While rendering into an atlas that can grow, it grows instead of rebuilding"""
    atlas, target, kept = _full_atlas_with_freed_space(can_grow=True)
    rebuilds = []
    rebuild = atlas.rebuild
    atlas.rebuild = lambda: (rebuilds.append(1), rebuild())
    _check_drawing(atlas, target, kept)
    assert not rebuilds
    assert atlas.size != (128, 128)


def test_rebuild_outside_render_into_unchanged(ctx):
    """Outside render_into, freed space is still reused by rebuilding"""
    atlas, target, kept = _full_atlas_with_freed_space(can_grow=True)
    rebuilds = []
    rebuild = atlas.rebuild
    atlas.rebuild = lambda: (rebuilds.append(1), rebuild())
    atlas.add(arcade.Texture(PIL.Image.new("RGBA", (40, 40), (255, 0, 0, 255))))
    assert rebuilds
    assert atlas.size == (128, 128)


def test_manual_rebuild_inside_render_into(ctx):
    atlas = DefaultTextureAtlas((128, 128), border=0)
    other = arcade.Texture(PIL.Image.new("RGBA", (64, 64), (0, 0, 255, 255)))
    target = arcade.Texture(PIL.Image.new("RGBA", (32, 32), (0, 255, 0, 255)))
    atlas.add(other)
    atlas.add(target)
    with atlas.render_into(target):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, 8, 8), (255, 255, 0, 255))
        atlas.rebuild()
        arcade.draw_rect_filled(arcade.LBWH(16, 16, 8, 8), (255, 0, 0, 255))
    image = atlas.read_texture_image_from_atlas(target).transpose(
        PIL.Image.Transpose.FLIP_TOP_BOTTOM
    )
    assert image.getpixel((4, 4)) == (255, 255, 0, 255)
    assert image.getpixel((20, 20)) == (255, 0, 0, 255)
    assert atlas.read_texture_image_from_atlas(other).getpixel((32, 32)) == (0, 0, 255, 255)
