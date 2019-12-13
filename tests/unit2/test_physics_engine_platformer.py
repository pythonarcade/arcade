import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5
GRAVITY = 0.5


class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.AMAZON)

        self.character_list = arcade.SpriteList()
        self.character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
        self.character_sprite.center_x = 150
        self.character_sprite.center_y = 110
        self.character_list.append(self.character_sprite)

        self.wall_list = arcade.SpriteList()
        for x in range(0, 1200, 64):
            sprite = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", CHARACTER_SCALING)
            sprite.center_x = x
            sprite.center_y = 32
            self.wall_list.append(sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.character_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.character_list.draw()

    def update(self, delta_time):
        self.physics_engine.update()


def multi_jump(window):
    window.physics_engine.enable_multi_jump(2)
    window.physics_engine.jumps_since_ground = 0
    assert window.physics_engine.can_jump() is True
    window.character_sprite.change_y = 15
    window.physics_engine.increment_jump_counter()
    window.test()
    assert window.physics_engine.can_jump() is True
    window.character_sprite.change_y = 15
    window.physics_engine.increment_jump_counter()
    window.test()
    assert window.physics_engine.can_jump() is False
    window.physics_engine.disable_multi_jump()


def test_main():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Text")
    window.test()
    multi_jump(window)
    window.close()
