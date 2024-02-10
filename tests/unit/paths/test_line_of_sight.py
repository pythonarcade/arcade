import arcade


def test_line_of_sight(window):
    player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png")
    player.center_x = 0
    player.center_y = 350

    enemy = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png")
    enemy.center_x = 250
    enemy.center_y = 350

    wall_list = arcade.SpriteList(use_spatial_hash=True)

    result = arcade.has_line_of_sight(player.position, enemy.position, wall_list)
    assert result

    result = arcade.has_line_of_sight(player.position, enemy.position, wall_list, 2000)
    assert result

    result = arcade.has_line_of_sight(player.position, enemy.position, wall_list, 20)
    assert not result

    result = arcade.has_line_of_sight(enemy.position, enemy.position, wall_list)
    assert result

    wall = arcade.Sprite(":resources:images/tiles/grassCenter.png")
    wall.center_x = 0
    wall.center_y = 0
    wall_list.append(wall)

    result = arcade.has_line_of_sight(player.position, enemy.position, wall_list)
    assert result

    wall.center_x = 100
    wall.center_y = 350

    result = arcade.has_line_of_sight(player.position, enemy.position, wall_list)
    assert not result

    wall.center_x = 100
    wall.center_y = 450

    result = arcade.has_line_of_sight(player.position, enemy.position, wall_list)
    assert result
