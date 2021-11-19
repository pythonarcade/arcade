"""
PIL based text functions
"""

from itertools import chain
from typing import Tuple, Union, cast

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from arcade.arcade_types import RGBA, Color
from arcade.draw_commands import Texture, get_four_byte_color
from arcade.sprite import Sprite

DEFAULT_FONT_NAMES = (
    "arial.ttf",
    "Arial.ttf",
    "NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    "/System/Library/Fonts/SFNSDisplay.ttf",
    "/Library/Fonts/Arial.ttf",
)


def create_text_image(
    text: str,
    text_color: Color,
    font_size: float = 12,
    width: int = 0,
    align: str = "left",
    valign: str = "top",
    font_name: Union[str, Tuple[str, ...]] = ("calibri", "arial"),
    background_color: Color = None,
    height: int = 0,
) -> PIL.Image.Image:
    """
    Create a PIL.Image containing text.

    .. warning::
        This method can be fairly slow. We recommend creating
        images on initialization or infrequently later on.

    :param str text: The text to render to the image
    :param Color text_color: Color of the text
    :param float font_size: Size of the font
    :param int width: The width of the image in pixels
    :param str align: "left" or "right" aligned
    :param str valign: "top" or "bottom" aligned
    :param str font_name: The font to use
    :param Color background_color: The background color of the image
    :param int height: the height of the image in pixels
    """

    # Scale the font up, so it matches with the sizes of the old code back
    # when Pyglet drew the text.
    font_size *= 1.25

    # Text isn't anti-aliased, so we'll draw big, and then shrink
    scale_up = 2
    scale_down = 2

    font_size *= scale_up

    # Figure out the font to use
    font = None

    # Font was specified with a string
    if isinstance(font_name, str):
        font_name = (font_name,)

    font_names = chain(
        *[
            [font_string_name, f"{font_string_name}.ttf"]
            for font_string_name in font_name
        ],
        DEFAULT_FONT_NAMES,
    )

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
        try:
            import pyglet.font

            font_config = pyglet.font.fontconfig.get_fontconfig()
            result = font_config.find_font("Arial")
            font = PIL.ImageFont.truetype(result.name, int(font_size))
        except Exception:
            # NOTE: Will catch OSError from loading font and missing fontconfig in pyglet
            pass
        else:
            font_found = True

    # Final fallback just getting PIL's default font if possible
    if not font_found:
        try:
            font = PIL.ImageFont.load_default()
            font_found = True
        except Exception:
            pass

    if not font_found:
        raise RuntimeError(
            "Unable to find a default font on this system. Please specify an available font."
        )

    # This is stupid. We have to have an image to figure out what size
    # the text will be when we draw it. Of course, we don't know how big
    # to make the image. Catch-22. So we just make a small image we'll trash
    text_image_size = [10, 10]
    image = PIL.Image.new("RGBA", text_image_size)
    draw = PIL.ImageDraw.Draw(image)

    # Get size the text will be
    text_image_size = draw.multiline_textsize(text, font=font)
    # Add some extra pixels at the bottom to account for letters that drop below the baseline.
    text_image_size = [text_image_size[0], text_image_size[1] + int(font_size * 0.25)]

    # Create image of proper size
    text_height = text_image_size[1]
    text_width = text_image_size[0]

    image_start_x = 0
    specified_width = width
    if specified_width == 0:
        width = text_image_size[0]
    else:
        # Wait! We were given a field width.
        if align == "center":
            # Center text on given field width
            field_width = width * scale_up
            image_start_x = (field_width // 2) - (text_width // 2)
        else:
            image_start_x = 0

    # Find y of top-left corner
    image_start_y = 0

    if height and valign == "middle":
        field_height = height * scale_up
        image_start_y = (field_height // 2) - (text_height // 2)

    if height:
        text_image_size[1] = height * scale_up

    if specified_width:
        text_image_size[0] = width * scale_up

    # Create image
    image = PIL.Image.new("RGBA", text_image_size, background_color)
    draw = PIL.ImageDraw.Draw(image)

    # Convert to tuple if needed, because the multiline_text does not take a
    # list for a color
    if isinstance(text_color, list):
        text_color = cast(RGBA, tuple(text_color))

    draw.multiline_text(
        (image_start_x, image_start_y), text, text_color, align=align, font=font
    )
    image = image.resize(
        (max(1, text_image_size[0] // scale_down), text_image_size[1] // scale_down),
        resample=PIL.Image.LANCZOS,
    )
    return image


def create_text_sprite(
    text: str,
    start_x: float,
    start_y: float,
    color: Color,
    font_size: float = 12,
    width: int = 0,
    align: str = "left",
    font_name: Union[str, Tuple[str, ...]] = ("calibri", "arial"),
    bold: bool = False,
    italic: bool = False,
    anchor_x: str = "left",
    anchor_y: str = "baseline",
    rotation: float = 0,
) -> Sprite:
    """
    Creates a sprite with a text texture using :py:func:`~arcade.create_text_image`.

    Internally this works by creating an image, and using the Pillow library to
    draw the text to it. Then use that image to create a sprite. We cache the sprite
    (so we don't have to recreate over and over, which is slow) and use it to
    draw text to the screen.

    This implementation does not support bold/italic like the older Pyglet-based
    implementation of draw_text. However if you specify the 'italic' or 'bold'
    version of the font via the font name, you will get that font. Just the booleans
    do not work.

    :param str text: Text to draw
    :param float start_x: x coordinate of the lower-left point to start drawing text
    :param float start_y: y coordinate of the lower-left point to start drawing text
    :param Color color: Color of the text
    :param float font_size: Size of the text
    :param float width: Width of the text-box for the text to go into. Used with alignment.
    :param str align: Align left, right, center
    :param Union[str, Tuple[str, ...]] font_name: Font name, or list of font names in order of preference
    :param bool bold: Bold the font (currently unsupported)
    :param bool italic: Italicize the font (currently unsupported)
    :param str anchor_x: Anchor the font location, defaults to 'left'
    :param str anchor_y: Anchor the font location, defaults to 'baseline'
    :param float rotation: Rotate the text
    """
    r, g, b, alpha = get_four_byte_color(color)
    cache_color = f"{r}{g}{b}"
    key = f"{text}{cache_color}{font_size}{width}{align}{font_name}{bold}{italic}"
    image = create_text_image(
        text=text,
        text_color=color,
        font_size=font_size,
        width=width,
        align=align,
        font_name=font_name,
    )
    text_sprite = Sprite()
    text_sprite._texture = Texture(key)
    text_sprite.texture.image = image
    text_sprite.width = image.width
    text_sprite.height = image.height

    if anchor_x == "left":
        text_sprite.center_x = start_x + text_sprite.width / 2
    elif anchor_x == "center":
        text_sprite.center_x = start_x
    elif anchor_x == "right":
        text_sprite.right = start_x
    else:
        raise ValueError(
            f"anchor_x should be 'left', 'center', or 'right'. Not '{anchor_x}'"
        )

    if anchor_y == "top":
        text_sprite.center_y = start_y - text_sprite.height / 2
    elif anchor_y == "center":
        text_sprite.center_y = start_y
    elif anchor_y == "bottom" or anchor_y == "baseline":
        text_sprite.center_y = start_y + text_sprite.height / 2
    else:
        raise ValueError(
            f"anchor_y should be 'top', 'center', 'bottom', or 'baseline'. Not '{anchor_y}'"
        )

    text_sprite.angle = rotation
    text_sprite.alpha = alpha

    return text_sprite
