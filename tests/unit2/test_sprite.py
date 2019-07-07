import os
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


def test_scale_by_width_and_height():
    """Should show texture very wide and very short."""
    class SpecificTestWindow(GeneralTestWindow):
        def setup(self):
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


def test_scale_by_width_and_height_then_scale_property():
    """Should show texture very wide and very short.
    just scaled down by half."""
    class SpecificTestWindow(GeneralTestWindow):
        def setup(self):
            sprite = arcade.Sprite(
                image="../../arcade/examples/images/character.png",
                width=300,
                height=50)
            sprite.scale = 0.5  # scale down
            sprite.change_x = 3
            sprite.change_y = 3
            self.character_list.append(sprite)
    window = SpecificTestWindow()
    window.test(frames=FRAMES)
    window.close()

    assert window.character_list[0].width == 300 * 0.5
    assert window.character_list[0].height == 50 * 0.5


def test_give_width_and_height_and_scale():
    """Should set width and height, then size up/down according to scale
    Should show very tall and very thin, yet, scaled up significantly."""
    class SpecificTestWindow(GeneralTestWindow):
        def setup(self):
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
