import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5


def test_physics_engine(window):
    window.background_color = arcade.color.AMAZON
    window.clear()

    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(
        ":resources:images/animated_characters/female_person/femalePerson_idle.png",
        scale=CHARACTER_SCALING,
    )
    character_sprite.center_x = 250
    character_sprite.center_y = 250
    character_sprite.change_x = 5
    character_sprite.change_y = 5
    character_list.append(character_sprite)

    wall_list = arcade.SpriteList()

    sprite = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=CHARACTER_SCALING)
    sprite.position = (330, 330)
    sprite.angle = 90
    wall_list.append(sprite)

    sprite = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=CHARACTER_SCALING)
    sprite.position = (170, 170)
    sprite.angle = 45
    wall_list.append(sprite)

    physics_engine = arcade.PhysicsEngineSimple(character_sprite, wall_list)

    def on_draw():
        window.clear()
        wall_list.draw()
        character_list.draw()

    def update(delta_time):
        physics_engine.update()

    def switch():
        character_sprite.change_x = -5
        character_sprite.change_y = -5

    window.on_draw = on_draw
    window.on_update = update
    window.test(10)
    switch()
    window.test(20)
