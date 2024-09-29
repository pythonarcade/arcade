"""Test AtlasRegion class."""
import pytest   
import PIL.Image

from arcade.texture_atlas.region import AtlasRegion
from arcade.texture.texture import ImageData
from arcade.texture_atlas.atlas_default import DefaultTextureAtlas


def test_region_coordinates_simple(ctx):
    """Basic region test."""
    atlas = DefaultTextureAtlas(size=(8, 8), border=0, auto_resize=False)
    region = AtlasRegion(atlas=atlas, x=0, y=0, width=8, height=8)
    assert region.x == 0
    assert region.y == 0
    assert region.width == 8
    assert region.height == 8
    # Simulate the half pixel location
    a, b = 0, 1.0
    assert region.texture_coordinates == (
        a, a,
        b, a,
        a, b,
        b, b,
    )


def test_region_coordinates_complex(ctx):
    """A more complex region test."""
    atlas = DefaultTextureAtlas(size=(16, 16), border=0, auto_resize=False)
    region = AtlasRegion(atlas=atlas, x=1, y=2, width=8, height=6)
    assert region.x == 1
    assert region.y == 2
    assert region.width == 8
    assert region.height == 6
    assert region.texture_coordinates == (0.0625, 0.125, 0.5625, 0.125, 0.0625, 0.5, 0.5625, 0.5)


def test_verify_size(ctx):
    im_data = ImageData(PIL.Image.new("RGBA", (8, 8)))
    region = AtlasRegion(atlas=ctx.default_atlas, x=0, y=0, width=8, height=8)

    region.verify_image_size(im_data)
    im_data = ImageData(PIL.Image.new("RGBA", (9, 9)))
    with pytest.raises(RuntimeError):
        region.verify_image_size(im_data)
