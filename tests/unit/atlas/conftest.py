import pytest
import arcade


@pytest.fixture
def common():
    return Common


class Common:

    @staticmethod
    def check_internals(
        atlas: arcade.DefaultTextureAtlas,
        *,
        textures=0,
        images=0,
        unique_textures=0,
        textures_added=-1,
        textures_removed=-1,
    ):
        # Images
        assert len(atlas._images) == images
        assert len(atlas._image_uvs) == images  # potentially also test free slots
        assert len(atlas._image_regions) == images
        assert len(atlas._image_ref_count) == images

        # Textures
        assert len(atlas._textures) == textures

        # Unique textures
        assert len(atlas._unique_textures) == unique_textures
        assert len(atlas._texture_uvs) == unique_textures    # potentially also test free slots
        assert len(atlas._texture_regions) == unique_textures
        assert len(atlas._unique_texture_ref_count) == unique_textures

        # Misc
        if textures_added >= 0:
            assert atlas._finalizers_created == textures_added
        if textures_removed >= 0:
            assert atlas._textures_removed == textures_removed
