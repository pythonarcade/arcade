import arcade
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
TITLE = 'Arcade cx_Freeze Sample'
BACKGROUND_COLOR = arcade.color.WHITE


def resource_path(file):
    path = 'resources/' + file
    # are we in a frozen environment (e.g. pyInstaller)?
    if getattr(sys, 'frozen', False):
        # noinspection PyProtectedMember,PyUnresolvedReferences
        path = sys._MEIPASS.replace('\\', '/') + '/' + path
    return path


def main():
    arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    arcade.set_background_color(BACKGROUND_COLOR)
    arcade.start_render()
    arcade.draw_circle_filled(400, 250, 100, arcade.color.BLACK)
    # load image
    image = arcade.load_texture(resource_path('character.png'))
    arcade.draw_texture_rectangle(200, 250, image.width, image.height, image)
    # load sound
    sound = arcade.sound.load_sound(resource_path('cat-meow.wav'))
    arcade.sound.play_sound(sound)
    arcade.finish_render()
    arcade.run()
    return


main()
