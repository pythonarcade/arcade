# --- BEGIN TEXT FUNCTIONS # # #

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from arcade.sprite import Sprite
from arcade.arcade_types import Color


class Text:
    def __init__(self):
        self.size = (0, 0)
        self.text_sprite_list = None


def draw_text(text: str,
              start_x: float, start_y: float,
              color: Color,
              font_size: float=12,
              width: int=0,
              align="left",
              font_name=('Calibri', 'Arial'),
              bold: bool=False,
              italic: bool=False,
              anchor_x="left",
              anchor_y="baseline",
              rotation: float=0
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

    scale_up = 10
    scale_down = 8

    # If the cache gets too large, dump it and start over.
    if len(draw_text.cache) > 5000:
        draw_text.cache = {}

    font_size *= scale_up

    key = f"{text}{color}{font_size}{width}{align}{font_name}{bold}{italic}{rotation}"
    if key in draw_text.cache:
        label = draw_text.cache[key]
        text_sprite = label.text_sprite_list[0]
        text_sprite.center_x = start_x + text_sprite.width / 2
        text_sprite.center_y = start_y + text_sprite.height / 2
        label.text_sprite_list.update_positions()
    else:

        label = Text()
        # font = PIL.ImageFont.truetype(font_name + ".ttf", font_size)

        font = None
        if isinstance(font_name, str):
            try:
                font = PIL.ImageFont.truetype(font_name, int(font_size))
            except:
                pass

            if font is None:
                try:
                    font = PIL.ImageFont.truetype(font_name + ".ttf", int(font_size))
                except:
                    pass

        if font is not None:
            for font_string_name in font_name:
                try:
                    font = PIL.ImageFont.truetype(font_name, int(font_size))
                except:
                    pass

                if font is None:
                    try:
                        font = PIL.ImageFont.truetype(font_name + ".ttf", int(font_size))
                    except:
                        pass

                if font is not None:
                    break

        if font is None:
            font_name = "arial.ttf"
            font = PIL.ImageFont.truetype(font_name, int(font_size))

        image_size = font.getsize(text)
        height = image_size[1]
        start_x = 0
        width = image_size[0]

        # if width != 0:
        #     if align == "center":
        #         start_x = (width - image_size[0]) // 2
        #     else:
        #         start_x = 0
        #
        #     width *= scale_up

        image = PIL.Image.new("RGBA", image_size)
        draw = PIL.ImageDraw.Draw(image)
        draw.text((start_x, 0), text, color, font=font)
        image = image.resize((width // scale_down, height // scale_down), resample=PIL.Image.LANCZOS)

        text_sprite = Sprite()
        text_sprite.image = image
        text_sprite.texture_name = key
        text_sprite.width = image.width
        text_sprite.height = image.height
        text_sprite.center_x = start_x + text_sprite.width / 2
        text_sprite.center_y = start_y + text_sprite.height / 2

        from arcade.sprite_list import SpriteList
        label.text_sprite_list = SpriteList()
        label.text_sprite_list.append(text_sprite)

        draw_text.cache[key] = label

    label.text_sprite_list.draw()


draw_text.cache = {}