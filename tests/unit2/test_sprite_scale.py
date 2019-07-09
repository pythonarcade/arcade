import os
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5

FRAMES = 50


file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)


class GeneralTestWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Window")
        arcade.set_background_color(arcade.color.AMAZON)
        self.character_list = arcade.SpriteList()

    def update(self, delta_time):
        self.character_list.update()

    def on_draw(self):
        arcade.start_render()
        self.character_list.draw()


def test_sprite_grows_when_increasing_scale():
    """Should show character image in lower left, growing in size."""
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            self.character_sprite = arcade.Sprite(
                image="../../arcade/examples/images/character.png",
                scale=CHARACTER_SCALING)
            self.character_sprite.center_x = 150
            self.character_sprite.center_y = 150
            self.character_list.append(self.character_sprite)

        def update(self, delta_time):
            super().update(delta_time)
            self.character_sprite.scale += 0.1

    window = SpecificTestWindow()
    window.test()
    window.close()


def test_sprite_without_image_grows_when_increasing_scale():
    """Should show a black square texture growing in the bottom left."""
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            self.character_sprite = arcade.Sprite(width=20,
                                                  height=20,
                                                  color=(0, 0, 0))
            self.character_sprite.center_x = 150
            self.character_sprite.center_y = 150
            self.character_list.append(self.character_sprite)

        def update(self, delta_time):
            super().update(delta_time)
            self.character_sprite.scale += 0.1

    window = SpecificTestWindow()
    window.test()
    window.close()


def test_setting_width_will_reset_scale_to_1():
    """Should show red square growing in scale.
    When it gets to be 100 px, the width will be reset to 50
    and continue to grow again to 100px"""
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            self.character_sprite = arcade.Sprite(width=50,
                                                  height=50,
                                                  color=(255, 0, 0))
            self.character_sprite.center_x = 150
            self.character_sprite.center_y = 150
            self.character_list.append(self.character_sprite)

        def update(self, delta_time):
            super().update(delta_time)
            self.character_sprite.scale += 0.1
            if self.character_sprite.width > 100:
                self.character_sprite.width = 50
                self.character_sprite.height = 50

    window = SpecificTestWindow()
    window.test(frames=FRAMES)
    window.close()


def test_scale_by_width_and_height():
    """Should show texture very wide and very short.
    Moving up and to the right"""
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            sprite = arcade.Sprite(
                "../../arcade/examples/images/character.png",
                width=300,
                height=50)
            sprite.change_x = 3
            sprite.change_y = 3
            self.character_list.append(sprite)

    window = SpecificTestWindow()
    window.test(frames=FRAMES)
    window.close()


def test_set_width_then_scale_maintains_ratio():
    sprite = arcade.Sprite(width=100, height=50)
    sprite.scale = 0.5
    assert sprite.width == 50
    assert sprite.height == 25


def test_give_width_and_height_and_scale():
    """Should set width and height, then size up/down according to scale
    Should show very tall and very thin, yet, scaled up significantly."""
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            sprite = arcade.Sprite(
                image="../../arcade/examples/images/character.png",
                width=10,
                height=100,
                scale=5)
            sprite.change_x = 3
            sprite.change_y = 3
            self.character_list.append(sprite)
    window = SpecificTestWindow()
    window.test(frames=FRAMES)
    window.close()
