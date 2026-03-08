"""
Ensure internal buffers are sized correctly.
Incorrectly sized buffers can lead to segfaults.
"""

import struct
import arcade


def check_buff_sizes(sp: arcade.SpriteList):
    # Buffers
    capacity = sp._buf_capacity
    assert len(sp.data.storage_positions_angle.read()) == 16 * capacity  # 3 floats
    assert len(sp.data.storage_color.read()) == 4 * capacity  # 4 floats
    assert len(sp.data.storage_size.read()) == 8 * capacity  # 2 floats
    assert len(sp.data.storage_texture_id.read()) == 4 * capacity  # 1 int
    # Arrays
    assert len(sp._sprite_pos_angle_data) == 4 * capacity  # 3 floats
    assert len(sp._sprite_color_data) == 4 * capacity  # 1 float
    assert len(sp._sprite_size_data) == 2 * capacity  # 2 floats
    assert len(sp._sprite_texture_data) == 1 * capacity  # 1 int
    # Index buffer
    assert len(sp.data.storage_index.read()) == 4 * sp._idx_capacity  # 1 int
    assert len(sp._sprite_index_data) == 1 * sp._idx_capacity  # 1 int
    # Slots
    assert len(sp.sprite_slot) == len(sp)
    # Free slots should be empty unless we removed sprites
    assert len(sp._sprite_buffer_free_slots) == 0
    # Slots should be the same size as the sprite list
    assert sp._sprite_buffer_slots == len(sp)
    assert sp._sprite_index_slots == len(sp)


def test_buffer_sizes(ctx: arcade.ArcadeContext):
    colors = (
        arcade.color.WHITE,
        arcade.color.RED,
        arcade.color.GREEN,
        arcade.color.BLUE,
    )
    positions_angle = (
        (0, 1, 2, 0),
        (10, 11, 12, 1),
        (20, 21, 22, 2),
        (30, 31, 32, 3),
    )
    sizes = (
        (10, 20),
        (30, 40),
        (50, 60),
        (70, 80),
    )

    sprites = []
    for color, size, pos_angle in zip(colors, sizes, positions_angle):
        sprite = arcade.SpriteSolidColor(
            *size,
            center_x=pos_angle[0],
            center_y=pos_angle[1],
            color=color,
            angle=pos_angle[3],
        )
        sprite.depth = pos_angle[2]
        sprites.append(sprite)

    sp: arcade.SpriteList = arcade.SpriteList(capacity=1)

    # Initial capacity
    assert sp._buf_capacity == 256
    assert sp._idx_capacity == 256
    check_buff_sizes(sp)

    # After adding a sprite filling the capacity (1)
    sp.append(sprites[0])
    assert sp._buf_capacity == 256
    assert sp._idx_capacity == 256
    check_buff_sizes(sp)

    # Adding one more sprite should double the capacity (2)
    sp.append(sprites[1])
    assert sp._buf_capacity == 256
    assert sp._idx_capacity == 256
    check_buff_sizes(sp)

    # Adding 1 more sprites to pass max capacity (3)
    sp.append(sprites[2])
    assert sp._buf_capacity == 256
    assert sp._idx_capacity == 256
    check_buff_sizes(sp)

    # Adding 1 more sprites to pass max capacity (4)
    sp.append(sprites[3])
    assert sp._buf_capacity == 256
    assert sp._idx_capacity == 256
    check_buff_sizes(sp)

    sp.write_sprite_buffers_to_gpu()

    # Test the contents of the arrays and buffers.
    # Prepare expected data
    expected_pos_data = struct.pack("16f", *[v for p in positions_angle for v in p])
    expected_color_data = struct.pack("16B", *[v for c in colors for v in c])
    expected_size_data = struct.pack("8f", *[v for s in sizes for v in s])
    expected_texture_data = struct.pack(
        "4f",
        *[ctx.default_atlas.get_texture_id(sprite.texture) for sprite in sprites],
    )

    # Check the buffers
    assert sp.data.storage_positions_angle.read().startswith(expected_pos_data)
    assert sp.data.storage_color.read().startswith(expected_color_data)
    assert sp.data.storage_size.read().startswith(expected_size_data)
    assert sp.data.storage_texture_id.read().startswith(expected_texture_data)

    # Check arrays
    assert sp._sprite_pos_angle_data.tobytes().startswith(expected_pos_data)
    assert sp._sprite_color_data.tobytes().startswith(expected_color_data)
    assert sp._sprite_size_data.tobytes().startswith(expected_size_data)
    assert sp._sprite_texture_data.tobytes().startswith(expected_texture_data)

    # Index buffer
    assert sp.data.storage_index.read().startswith(struct.pack("4i", 0, 1, 2, 3))
