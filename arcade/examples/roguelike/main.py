"""
Starting Template Simple

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template_simple
"""
import arcade
import pyglet.gl as gl

from PIL import Image
from game_map import GameMap

SCREEN_TITLE = "RogueLike"
SCALE = 1
SPRITE_WIDTH = 9
SPRITE_HEIGHT = 16
ROWS = 60
COLUMNS = 150
SCREEN_WIDTH = SPRITE_WIDTH * COLUMNS
SCREEN_HEIGHT = SPRITE_HEIGHT * ROWS
WALL_CHAR = 219

colors = {
    'dark_wall': (0, 0, 100),
    'dark_ground': (50, 50, 150)
}

textures = arcade.load_spritesheet(":resources:images/spritesheets/codepage_437.png",
                                   sprite_width=SPRITE_WIDTH,
                                   sprite_height=SPRITE_HEIGHT,
                                   columns=32,
                                   count=8 * 32)

def recolor(original_image, new_color):
    """
    Recolors a letter.
    This function takes an image and color, then creates a new image
    with that color, minus the transparent parts of the original.
    """
    # Open original image and extract the alpha channel
    alpha = original_image.getchannel('A')

    # Create red image the same size and copy alpha channel across
    new_image = Image.new('RGBA', original_image.size, color=new_color)
    new_image.putalpha(alpha)
    return new_image

class Item(arcade.Sprite):
    """ Character Sprite on Screen """
    def __init__(self, letter, color):
        super().__init__(scale=SCALE)
        self._x = 0
        self._y = 0
        self._color = color
        self._char = letter
        self._set_char()

    @property
    def char(self):
        """ Character of the item """
        return self._char

    @char.setter
    def char(self, value):
        self._char = value
        self._set_char()

    @property
    def color(self):
        """ Color of the item """
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._set_char()

    def _set_char(self):
        """
        Gets a texture for a certain letter in the specified color.
        """
        texture = textures[self._char]
        original_image = texture.image
        new_image = recolor(original_image, self._color)
        new_texture = arcade.Texture(name=self._char, image=new_image)
        self.texture = new_texture

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.center_x = self._x * SPRITE_WIDTH * SCALE + SPRITE_WIDTH / 2 * SCALE

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.center_y = self._y * SPRITE_HEIGHT * SCALE + SPRITE_HEIGHT / 2 * SCALE


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=False)

        arcade.set_background_color(arcade.color.BLACK)
        self.player = None
        self.characters = None
        self.game_map = None
        self.dungeon_sprites = None

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        self.characters = arcade.SpriteList()
        self.player = Item(ord("@"), arcade.csscolor.WHITE)
        self.player.x = 0
        self.player.y = 0
        self.characters.append(self.player)

        # Size of the map
        map_width = COLUMNS
        map_height = ROWS

        # Some variables for the rooms in the map
        room_max_size = 10
        room_min_size = 6
        max_rooms = 30

        self.game_map = GameMap(map_width, map_height)
        self.game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, self.player)
        print(self.player.x, self.player.y)
        self.dungeon_sprites = arcade.SpriteList()

        # Draw all the tiles in the game map
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                wall = self.game_map.tiles[x][y].block_sight

                if wall:
                    sprite = Item(WALL_CHAR, colors.get('dark_wall'))
                else:
                    sprite = Item(WALL_CHAR, colors.get('dark_ground'))

                sprite.x = x
                sprite.y = y

                self.dungeon_sprites.append(sprite)


    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()

        self.dungeon_sprites.draw(filter=gl.GL_NEAREST)
        self.characters.draw(filter=gl.GL_NEAREST)

    def on_key_press(self, symbol: int, modifiers: int):
        """ Manage keyboard input """
        if symbol == arcade.key.UP:
            self.player.y += 1
        elif symbol == arcade.key.DOWN:
            self.player.y -= 1
        elif symbol == arcade.key.LEFT:
            self.player.x -= 1
        elif symbol == arcade.key.RIGHT:
            self.player.x += 1

def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
