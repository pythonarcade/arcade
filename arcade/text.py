# --- BEGIN TEXT FUNCTIONS # # #

from itertools import chain
from typing import Dict, Tuple, Union, cast

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import pyglet

from arcade.arcade_types import RGBA, Color
from arcade.draw_commands import Texture, get_four_byte_color
from arcade.sprite import Sprite

DEFAULT_FONT_NAMES = (
    "arial.ttf",
    "Arial.ttf",
    "NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    "/System/Library/Fonts/SFNSDisplay.ttf",
    "/Library/Fonts/Arial.ttf"
)

draw_text_cache: Dict[str, 'Text'] = dict()


class Text:
    """ Class used for managing text. """

    def __init__(self):
        self.size = (0, 0)
        self.text_sprite_list = None


class CreateText:
    """ Class used for managing text """

    def __init__(self,
                 text: str,
                 color: Color,
                 font_size: float = 12,
                 width: int = 20,
                 align="left",
                 font_name=('Calibri', 'Arial'),
                 bold: bool = False,
                 italic: bool = False,
                 anchor_x="left",
                 anchor_y="baseline",
                 rotation=0):
        self.text = text
        self.color = color
        self.font_size = font_size
        self.width = width
        self.align = align
        self.font_name = font_name
        self.bold = bold
        self.italic = italic
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.rotation = rotation


def create_text(text: str,
                color: Color,
                font_size: float = 12,
                width: int = 0,
                align="left",
                font_name=('Calibri', 'Arial'),
                bold: bool = False,
                italic: bool = False,
                anchor_x: str = "left",
                anchor_y: str = "baseline",
                rotation=0):
    """ Deprecated. Two step text drawing for backwards compatibility. """

    import warnings
    warnings.warn("create_text has been deprecated, please use draw_text instead.", DeprecationWarning)
    my_text = CreateText(text, color, font_size, width, align, font_name, bold, italic, anchor_x, anchor_y, rotation)
    return my_text


def render_text(text: CreateText, start_x: float, start_y: float):
    """ Deprecated. Two step text drawing for backwards compatibility. """

    import warnings
    warnings.warn("render_text has been deprecated, please use draw_text instead.", DeprecationWarning)

    draw_text(text.text,
              start_x,
              start_y,
              color=text.color,
              font_size=text.font_size,
              width=text.width,
              align=text.align,
              font_name=text.font_name,
              bold=text.bold,
              italic=text.italic,
              anchor_x=text.anchor_x,
              anchor_y=text.anchor_y,
              rotation=text.rotation)


def draw_text(text: str,
              start_x: float,
              start_y: float,
              color: Color,
              font_size: float = 12,
              width: int = 0,
              align: str = "left",
              font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial'),
              bold: bool = False,
              italic: bool = False,
              anchor_x: str = "left",
              anchor_y: str = "baseline",
              rotation: float = 0
              ) -> Sprite:
    """

    :param str text: Text to draw
    :param float start_x: x coordinate of the lower-left point to start drawing text
    :param float start_y: y coordinate of the lower-left point to start drawing text
    :param Color color: Color of the text
    :param float font_size: Size of the text
    :param float width: Width of the text-box for the text to go into. Used with alignment.
    :param str align: Align left, right, center
    :param Union[str, Tuple[str, ...]] font_name: Font name, or list of font names in order of preference
    :param bool bold: Bold the font
    :param bool italic: Italicize the font
    :param str anchor_x: Anchor the font location, defaults to 'left'
    :param str anchor_y: Anchor the font location, defaults to 'baseline'
    :param float rotation: Rotate the text
    """
    global draw_text_cache

    # Scale the font up, so it matches with the sizes of the old code back
    # when Pyglet drew the text.
    font_size *= 1.25

    # Text isn't anti-aliased, so we'll draw big, and then shrink
    scale_up = 2
    scale_down = 2

    font_size *= scale_up

    # If the cache gets too large, dump it and start over.
    if len(draw_text_cache) > 5000:
        draw_text_cache = {}

    r, g, b, alpha = get_four_byte_color(color)
    cache_color = f"{r}{g}{b}"

    key = f"{text}{cache_color}{font_size}{width}{align}{font_name}{bold}{italic}"
    try:
        label = draw_text_cache[key]
    except KeyError:  # doesn't exist, create it
        label = Text()

        # Figure out the font to use
        font = None

        # Font was specified with a string
        if isinstance(font_name, str):
            font_name = font_name,

        font_names = chain(*[
            [font_string_name, f"{font_string_name}.ttf"]
            for font_string_name in font_name
        ], DEFAULT_FONT_NAMES)

        font_found = False
        for font_string_name in font_names:
            try:
                font = PIL.ImageFont.truetype(font_string_name, int(font_size))
            except OSError:
                continue
            else:
                font_found = True
                break

        if not font_found:
            raise RuntimeError("Unable to find a default font on this system. Please specify an available font.")

        # This is stupid. We have to have an image to figure out what size
        # the text will be when we draw it. Of course, we don't know how big
        # to make the image. Catch-22. So we just make a small image we'll trash
        text_image_size = (10, 10)
        image = PIL.Image.new("RGBA", text_image_size)
        draw = PIL.ImageDraw.Draw(image)

        # Get size the text will be
        text_image_size = draw.multiline_textsize(text, font=font)
        # Add some extra pixels at the bottom to account for letters that drop below the baseline.
        text_image_size = text_image_size[0], text_image_size[1] + int(font_size * 0.25)

        # Create image of proper size
        text_height = text_image_size[1]
        text_width = text_image_size[0]

        image_start_x = 0
        if width == 0:
            width = text_image_size[0]
        else:
            # Wait! We were given a field width.
            if align == "center":
                # Center text on given field width
                field_width = width * scale_up
                text_image_size = field_width, text_height
                image_start_x = (field_width - text_width) // 2
                width = field_width
            else:
                image_start_x = 0

        # Find y of top-left corner
        image_start_y = 0

        # Create image
        image = PIL.Image.new("RGBA", text_image_size)
        draw = PIL.ImageDraw.Draw(image)

        # Convert to tuple if needed, because the multiline_text does not take a
        # list for a color
        if isinstance(color, list):
            color = cast(RGBA, tuple(color))
        draw.multiline_text((image_start_x, image_start_y), text, color, align=align, font=font)
        image = image.resize((max(1, width // scale_down), text_height // scale_down), resample=PIL.Image.LANCZOS)

        text_sprite = Sprite()
        text_sprite._texture = Texture(key)
        text_sprite.texture.image = image

        text_sprite.width = image.width
        text_sprite.height = image.height

        from arcade.sprite_list import SpriteList
        label.text_sprite_list = SpriteList()
        label.text_sprite_list.append(text_sprite)

        draw_text_cache[key] = label

    text_sprite = label.text_sprite_list[0]

    if anchor_x == "left":
        text_sprite.center_x = start_x + text_sprite.width / 2
    elif anchor_x == "center":
        text_sprite.center_x = start_x
    elif anchor_x == "right":
        text_sprite.right = start_x
    else:
        raise ValueError(f"anchor_x should be 'left', 'center', or 'right'. Not '{anchor_x}'")

    if anchor_y == "top":
        text_sprite.center_y = start_y - text_sprite.height / 2
    elif anchor_y == "center":
        text_sprite.center_y = start_y
    elif anchor_y == "bottom" or anchor_y == "baseline":
        text_sprite.bottom = start_y
    else:
        raise ValueError(f"anchor_y should be 'top', 'center', 'bottom', or 'baseline'. Not '{anchor_y}'")

    text_sprite.angle = rotation
    text_sprite.alpha = alpha

    label.text_sprite_list.draw()
    return text_sprite


def draw_text_2(text: str,
                start_x: float, start_y: float,
                color: Color,
                font_size: float = 12,
                width: int = 0,
                align: str = "left",
                font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial'),
                bold: bool = False,
                italic: bool = False,
                anchor_x: str = "left",
                anchor_y: str = "baseline",
                rotation: float = 0
                ):
    """

    :param str text: Text to draw
    :param float start_x:
    :param float start_y:
    :param Color color: Color of the text
    :param float font_size: Size of the text
    :param float width:
    :param str align:
    :param Union[str, Tuple[str, ...]] font_name:
    :param bool bold:
    :param bool italic:
    :param str anchor_x:
    :param str anchor_y:
    :param float rotation:
    """

    color = get_four_byte_color(color)
    label = pyglet.text.Label(text,
                              font_name=font_name,
                              font_size=font_size,
                              x=start_x, y=start_y,
                              anchor_x=anchor_x, anchor_y=anchor_y,
                              color=color,
                              align=align,
                              bold=bold,
                              italic=italic,
                              width=width)

    label.draw()
