import os
import random
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5

FRAMES = 10


class GeneralTestWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Window")

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.AMAZON)

        self.character_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        self.setup()

    def setup(self):
        """To be overridden by specific test windows"""
        pass

    def on_draw(self):
        arcade.start_render()
        self.coin_list.draw()
        self.character_list.draw()

    def update(self, delta_time):
        self.coin_list.update()
        self.character_list.update()


def test_sprite():
    class SpecificTestWindow(GeneralTestWindow):
        def setup(self):
            self.character_sprite = arcade.Sprite(
                image="../../arcade/examples/images/character.png",
                scale=CHARACTER_SCALING)
            self.character_sprite.center_x = 50
            self.character_sprite.center_y = 50
            self.character_sprite.change_x = 5
            self.character_sprite.change_y = 5
            self.character_list.append(self.character_sprite)

            sprite = arcade.Sprite(
                image="../../arcade/examples/images/coin_01.png",
                scale=CHARACTER_SCALING)
            sprite.position = (130, 130)
            sprite.set_position(130, 130)
            sprite.angle = 90
            self.coin_list.append(sprite)

        def update(self, deltatime):
            super().update(deltatime)
            coin_hit_list = arcade.check_for_collision_with_list(
                sprite=self.character_sprite,
                sprite_list=self.coin_list)
            for coin in coin_hit_list:
                coin.kill()

    window = SpecificTestWindow()
    window.test(frames=FRAMES)
    window.close()


def test_sprite_image_crop():
    """Should show small cutout of character's face as the texture."""
    class SpecificTestWindow(GeneralTestWindow):
        def setup(self):
            cropped_texture = arcade.load_texture(
                file_name="../../arcade/examples/images/character.png",
                x=30,
                y=28,
                width=30,
                height=30)
            sprite = arcade.Sprite(
                image=cropped_texture,
                center_x=200,
                center_y=200)
            self.character_list.append(sprite)
    window = SpecificTestWindow()
    window.test(frames=FRAMES)
    window.close()


def test_adding_image_after_creation_should_not_leave_a_tint():
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            self.frame_count = 0
            self.character_sprite = arcade.Sprite(width=50,
                                                  height=50,
                                                  color=(0, 0, 0))
            self.character_sprite.center_x = 150
            self.character_sprite.center_y = 150
            self.character_list.append(self.character_sprite)

        def update(self, delta_time):
            super().update(delta_time)
            self.frame_count += 1

            if self.frame_count == 10:
                self.character_sprite.texture = arcade.load_texture(
                    "../../arcade/examples/images/character.png")

    window = SpecificTestWindow()
    window.test(frames=20)
    window.close()


def test_debug_mode_with_image():
    """Should show a bunch of sprites flying around in debug mode."""
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            self.frame_count = 0
            self.character_sprite = arcade.Sprite(
                image="../../arcade/examples/images/character.png",
                scale=1)
            self.character_sprite.center_x = 150
            self.character_sprite.center_y = 150
            self.character_sprite.change_x = 3
            self.character_sprite.change_y = 3
            self.character_list.append(self.character_sprite)
            assert self.character_sprite.debug is False

            for _ in range(100):
                coin = arcade.Sprite(
                    image="../../arcade/examples/images/coin_01.png",
                    scale=CHARACTER_SCALING)
                coin.center_x = random.randrange(0, SCREEN_WIDTH)
                coin.center_y = random.randrange(0, SCREEN_HEIGHT)
                while coin.change_x == 0 and coin.change_y == 0:
                    coin.change_x = random.randrange(-5, 5)
                    coin.change_y = random.randrange(-5, 5)
                coin.debug = True
                self.coin_list.append(coin)

        def update(self, delta_time):
            super().update(delta_time)
            self.frame_count += 1

            if self.frame_count == 10:
                self.character_sprite.debug = True

    window = SpecificTestWindow()
    window.test(frames=20)
    window.close()


def test_switch_debug_mode_with_image():
    """Should show character moving to the right switching on and off
    between debug mode."""
    class SpecificTestWindow(GeneralTestWindow):
        def __init__(self):
            super().__init__()
            self.frame_count = 0
            self.character_sprite = arcade.Sprite(
                image="../../arcade/examples/images/character.png",
                scale=0.5)
            self.character_sprite.center_x = 150
            self.character_sprite.center_y = 150
            self.character_sprite.change_x = 3
            self.character_list.append(self.character_sprite)

        def update(self, delta_time):
            super().update(delta_time)
            self.frame_count += 1

            if self.frame_count == 30:
                self.character_sprite.debug = True
            elif self.frame_count == 60:
                self.character_sprite.debug = False
            elif self.frame_count == 90:
                self.character_sprite.debug = True

    window = SpecificTestWindow()
    window.test(frames=120)
    window.close()
