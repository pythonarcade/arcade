import arcade
from arcade import TextureAtlas


def test_calculate_minimum_size(ctx, common):
    """Calculate the min size for an atlas"""
    texture_paths = [
        ":resources:images/topdown_tanks/tankBlue_barrel1.png",
        ":resources:images/topdown_tanks/tankBlue_barrel1_outline.png",
        ":resources:images/topdown_tanks/tankBlue_barrel2.png",
        ":resources:images/topdown_tanks/tankBlue_barrel2_outline.png",
        ":resources:images/topdown_tanks/tankBlue_barrel3.png",
        ":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
        ":resources:images/topdown_tanks/tankBody_bigRed.png",
        ":resources:images/topdown_tanks/tankBody_bigRed_outline.png",
        ":resources:images/topdown_tanks/tankBody_blue.png",
        ":resources:images/topdown_tanks/tankBody_blue_outline.png",
        ":resources:images/topdown_tanks/tankBody_dark.png",
        ":resources:images/topdown_tanks/tankBody_darkLarge.png",
        ":resources:images/topdown_tanks/tankBody_darkLarge_outline.png",
        ":resources:images/topdown_tanks/tankBody_dark_outline.png",
        ":resources:images/topdown_tanks/tankBody_green.png",
        ":resources:images/topdown_tanks/tankBody_green_outline.png",
        ":resources:images/topdown_tanks/tankBody_huge.png",
        ":resources:images/topdown_tanks/tankBody_huge_outline.png",
        ":resources:images/topdown_tanks/tankBody_red.png",
        ":resources:images/topdown_tanks/tankSand_barrel3_outline.png",
        ":resources:images/topdown_tanks/tankGreen_barrel1_outline.png",
        ":resources:images/topdown_tanks/tankRed_barrel2_outline.png",
        ":resources:images/topdown_tanks/tank_sand.png",
        ":resources:images/topdown_tanks/tank_green.png",
        ":resources:images/topdown_tanks/tank_green.png",
        ":resources:images/topdown_tanks/tank_green.png",
    ]
    textures = []
    for path in texture_paths:
        textures.append(arcade.load_texture(path))

    size = TextureAtlas.calculate_minimum_size(textures)
    atlas = TextureAtlas(size, textures=textures)
    # We have two duplicate textures in the list
    count = len(textures) - 2
    common.check_internals(atlas, num_images=count, num_textures=count)
    assert size == (320, 320)

    textures = textures[:len(textures) // 2]
    size = TextureAtlas.calculate_minimum_size(textures)
    atlas = TextureAtlas(size, textures=textures)
    common.check_internals(atlas, num_textures=len(textures), num_images=len(textures))
    assert size == (192, 192)

    textures = textures[:len(textures) // 2]
    size = TextureAtlas.calculate_minimum_size(textures)
    atlas = TextureAtlas(size, textures=textures)
    common.check_internals(atlas, num_images=len(textures), num_textures=len(textures))
    assert size == (64, 64)

    # Empty list should at least create the minimum atlas
    size = TextureAtlas.calculate_minimum_size([])
    assert size == (128, 128)
