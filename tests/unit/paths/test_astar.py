"""
Test for A-Star path routing
"""
import arcade

SPRITE_IMAGE_SIZE = 128
SPRITE_SCALING = 0.25
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING)


def test_astar(window):
    grid_size = SPRITE_SIZE

    # Sprite lists
    player_list = arcade.SpriteList()
    wall_list = arcade.SpriteList(use_spatial_hash=True, spatial_hash_cell_size=128)
    enemy_list = arcade.SpriteList()

    # Set up the player
    player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                           scale=SPRITE_SCALING)
    player.center_x = SPRITE_SIZE * 1
    player.center_y = SPRITE_SIZE * 1
    player_list.append(player)

    # Set enemies
    enemy = arcade.Sprite(":resources:images/animated_characters/zombie/zombie_idle.png", scale=SPRITE_SCALING)
    enemy.center_x = SPRITE_SIZE * 5
    enemy.center_y = SPRITE_SIZE * 5
    enemy_list.append(enemy)

    # Calculate the playing field size. We can't generate paths outside of
    # this.
    playing_field_left_boundary = -SPRITE_SIZE * 2
    playing_field_right_boundary = SPRITE_SIZE * 35
    playing_field_top_boundary = SPRITE_SIZE * 17
    playing_field_bottom_boundary = -SPRITE_SIZE * 2

    # This calculates a list of barriers. By calculating it here in the
    # init, we are assuming this list does not change. In this example,
    # our walls don't move, so that is ok. If we want moving barriers (such as
    # moving platforms or enemies) we need to recalculate. This can be an
    # time-intensive process depending on the playing field size and grid
    # resolution.

    # Note: If the enemy sprites are the same size, we only need to calculate
    # one of these. We do NOT need a different one for each enemy. The sprite
    # is just used for a size calculation.
    barrier_list = arcade.AStarBarrierList(enemy,
                                           wall_list,
                                           grid_size,
                                           playing_field_left_boundary,
                                           playing_field_right_boundary,
                                           playing_field_bottom_boundary,
                                           playing_field_top_boundary)

    # print()
    path = arcade.astar_calculate_path(enemy.position,
                                       player.position,
                                       barrier_list,
                                       diagonal_movement=False)

    # barrier_list.recalculate()
    # print(f"barrier_list: {barrier_list.barrier_list}")

    # print("Path 1", path)
    assert path == [(160, 160), (128, 160), (128, 128), (96, 128), (96, 96), (64, 96), (64, 64), (32, 64), (32, 32)]

    path = arcade.astar_calculate_path(enemy.position,
                                       player.position,
                                       barrier_list,
                                       diagonal_movement=True)
    assert path == [(160, 160), (128, 128), (96, 96), (64, 64), (32, 32)]
    # print("Path 2", path)

    sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", scale=SPRITE_SCALING)
    sprite.center_x = SPRITE_SIZE * 3
    sprite.center_y = SPRITE_SIZE * 1
    wall_list.append(sprite)

    sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", scale=SPRITE_SCALING)
    sprite.center_x = SPRITE_SIZE * 3
    sprite.center_y = SPRITE_SIZE * 2
    wall_list.append(sprite)

    sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", scale=SPRITE_SCALING)
    sprite.center_x = SPRITE_SIZE * 3
    sprite.center_y = SPRITE_SIZE * 3
    wall_list.append(sprite)

    sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", scale=SPRITE_SCALING)
    sprite.center_x = SPRITE_SIZE * 3
    sprite.center_y = SPRITE_SIZE * 4
    wall_list.append(sprite)

    sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", scale=SPRITE_SCALING)
    sprite.center_x = SPRITE_SIZE * 3
    sprite.center_y = SPRITE_SIZE * 5
    wall_list.append(sprite)

    barrier_list.recalculate()

    path = arcade.astar_calculate_path(enemy.position,
                                       player.position,
                                       barrier_list,
                                       diagonal_movement=True)

    assert path == [(160, 160), (128, 160), (96, 192), (64, 160), (64, 128), (64, 96), (64, 64), (32, 32)]
