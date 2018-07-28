# --- BEGIN TEXT FUNCTIONS # # #

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from arcade.sprite import Sprite
from arcade.arcade_types import Color
from arcade.sprite_list import SpriteList2


class Text:
    def __init__(self):
        size = (0, 0)
        text_sprite_list = None


def draw_text(text: str,
              start_x: float, start_y: float,
              color: Color,
              font_size: float=12,
              width: int=2000,
              align="left",
              font_name=('Calibri', 'Arial'),
              bold: bool=False,
              italic: bool=False,
              anchor_x="left",
              anchor_y="baseline",
              rotation=0
              ):
    """

    Args:
        :text: Text to display.
        :start_x: x coordinate of top left text point.
        :start_y: y coordinate of top left text point.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.

    Example:

    >>> import arcade
    >>> arcade.open_window(800, 600, "Drawing Example")
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_text("Text Example", 250, 300, arcade.color.BLACK, 10)
    >>> arcade.draw_text("Text Example", 250, 300, (0, 0, 0, 100), 10)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    scale_up = 5
    scale_down = 4

    # If the cache gets too large, dump it and start over.
    if len(draw_text.cache) > 5000:
        draw_text.cache = {}

    font_size *= scale_up

    key = f"{text}{color}{font_size}{width}{align}{font_name}{bold}{italic}"
    if key in draw_text.cache:
        label = draw_text.cache[key]
        text_sprite = label.text_sprite_list[0]
        text_sprite.center_x = start_x + text_sprite.width / 2
        text_sprite.center_y = start_y
        label.text_sprite_list.update_positions()
    else:

        label = Text()
        # font = PIL.ImageFont.truetype(font_name + ".ttf", font_size)

        font_name = "calibri.ttf"

        font = PIL.ImageFont.truetype(font_name, int(font_size))

        image_size = font.getsize(text)

        image = PIL.Image.new("RGBA", image_size)
        draw = PIL.ImageDraw.Draw(image)
        draw.text((0, 0), text, font=font)
        image = image.resize((image_size[0] // scale_down, image_size[1] // scale_down), PIL.Image.ANTIALIAS)

        text_sprite = Sprite()
        text_sprite.image = image
        text_sprite.texture_name = key
        text_sprite.width = image.width
        text_sprite.height = image.height
        text_sprite.center_x = start_x + text_sprite.width / 2
        text_sprite.center_y = start_y
        label.text_sprite_list = SpriteList2()
        label.text_sprite_list.append(text_sprite)

        draw_text.cache[key] = label

    label.text_sprite_list.draw()


draw_text.cache = {}