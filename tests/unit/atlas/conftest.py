import pytest
import arcade


@pytest.fixture
def common():
    return Common


class Common:

    @staticmethod
    def check_internals(atlas: arcade.TextureAtlas, *, num_textures = 0, num_images = 0):
        # Images
        # assert len(atlas._images) == num_images
        # assert len(atlas._image_uv_slots) == num_images
        # assert len(atlas._image_uv_slots_free) == atlas._num_image_slots - num_images
        # assert len(atlas._image_regions) == num_images

        # Textures
        # assert len(atlas._textures) == num_textures
        # assert len(atlas._texture_uv_slots) == num_textures
        # assert len(atlas._texture_uv_slots_free) == atlas._num_texture_slots - num_textures    
        # assert len(atlas._texture_regions) == num_textures

        # Misc
        # assert len(atlas._image_ref_count) == num_images
        # the number of image refs should be the same as the number of textures
        # assert atlas._image_ref_count.count_all_refs() == num_textures
        # TODO: Check the size of these when when texture row allocation is fixed
        # atlas._image_uv_data
        # atlas._texture_uv_data
        pass
