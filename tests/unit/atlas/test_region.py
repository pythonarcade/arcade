"""Test AtlasRegion class."""

import pytest
import PIL.Image

from arcade.texture_atlas.region import AtlasRegion
from arcade.texture.texture import Texture, ImageData
from arcade.texture_atlas.atlas_default import DefaultTextureAtlas


def test_region_coordinates(ctx):
    """Test region class."""
    atlas = DefaultTextureAtlas(size=(8, 8), border=0, auto_resize=False)
    region = AtlasRegion(atlas=atlas, x=0, y=0, width=8, height=8)
    assert region.x == 0
    assert region.y == 0
    assert region.width == 8
    assert region.height == 8
    # Simulate the half pixel location
    a, b = 0.5 / 8, 1 - 0.5 / 8
    assert region.texture_coordinates == (
        a,
        a,
        b,
        a,
        a,
        b,
        b,
        b,
    )
    # Above raw values:
    # (
    #     0.0625, 0.0625,
    #     0.9375, 0.0625,
    #     0.0625, 0.9375,
    #     0.9375, 0.9375)
    # )


def test_verify_size(ctx):
    im_data = ImageData(PIL.Image.new("RGBA", (8, 8)))
    texture = Texture(im_data)
    region = AtlasRegion(atlas=ctx.default_atlas, x=0, y=0, width=8, height=8)

    region.verify_image_size(im_data)
    im_data = ImageData(PIL.Image.new("RGBA", (9, 9)))
    with pytest.raises(RuntimeError):
        region.verify_image_size(im_data)
