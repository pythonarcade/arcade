"""
Separate textures can share an image and atlas name, such as every
SpriteSolidColor size. The atlas has to keep track of all of them.
"""

import gc

import PIL.Image

from arcade import DefaultTextureAtlas, Texture
from arcade.texture import ImageData


def _shared_textures(count):
    data = ImageData(PIL.Image.new("RGBA", (8, 8), (255, 255, 255, 255)))
    textures = [Texture(data) for _ in range(count)]
    assert len({texture.atlas_name for texture in textures}) == 1
    return textures


def test_resize_after_first_shared_texture_dies(ctx):
    # Used to raise "Empty set in unique textures"
    first, second = _shared_textures(2)
    atlas = DefaultTextureAtlas((32, 32))
    atlas.add(first)
    atlas.add(second)
    name = second.atlas_name
    del first
    gc.collect()

    atlas.resize((64, 64))

    # The surviving texture's coordinates follow its image to the new position
    texture_region = atlas.get_texture_region_info(name)
    image_region = atlas.get_image_region_info(second.image_data.hash)
    assert texture_region.texture_coordinates == image_region.texture_coordinates


def test_name_removed_when_last_shared_texture_dies(ctx):
    textures = _shared_textures(3)
    atlas = DefaultTextureAtlas((32, 32))
    for texture in textures:
        atlas.add(texture)
    del texture
    name = textures[0].atlas_name

    textures.pop(0)
    gc.collect()
    assert atlas.has_unique_texture(textures[0])
    textures.clear()
    gc.collect()
    assert name not in atlas._unique_textures


def test_name_removed_even_if_set_still_holds_texture(ctx):
    # A finalizer can run before the set's own weak reference callback removes
    # the dying texture. Simulate that with a texture the atlas doesn't count.
    (texture,) = _shared_textures(1)
    (not_counted,) = _shared_textures(1)
    atlas = DefaultTextureAtlas((32, 32))
    atlas.add(texture)
    name = texture.atlas_name
    atlas._unique_textures[name].add(not_counted)

    del texture
    gc.collect()
    assert name not in atlas._unique_textures

    # Used to raise "Texture '...' not found in UVData"
    (later,) = _shared_textures(1)
    atlas.add(later)
    assert atlas.get_texture_id(later) is not None


def test_add_while_last_shared_texture_is_collected(ctx, monkeypatch):
    # Python 3.14's garbage collector exposed this in CI: a texture added while
    # the last other texture with its name was being collected found the name
    # gone, and raised KeyError
    data = ImageData(PIL.Image.new("RGBA", (8, 8), (255, 255, 255, 255)))
    atlas = DefaultTextureAtlas((32, 32))
    dying = Texture(data)
    atlas.add(dying)
    name = dying.atlas_name

    # Garbage that only the cycle collector frees, like a texture held by a
    # sprite and sprite list that point at each other
    cycle: list = [dying]
    cycle.append(cycle)
    del dying, cycle

    # Collect it at the moment the new texture's reference is being added
    add_texture_ref = atlas._add_texture_ref

    def collect_then_add(texture, create_finalizer=True):
        gc.collect()
        add_texture_ref(texture, create_finalizer=create_finalizer)

    monkeypatch.setattr(atlas, "_add_texture_ref", collect_then_add)

    texture = Texture(data)
    assert texture.atlas_name == name
    slot, region = atlas.add(texture)
    assert atlas.has_unique_texture(texture)
    assert region == atlas.get_texture_region_info(name)
    assert atlas.get_image_region_info(data.hash) is not None
