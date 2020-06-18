import os
from itertools import chain
from pathlib import Path
from typing import Union, cast, Tuple, Optional, Any
from warnings import warn

import PIL
from PIL import Image, ImageDraw
from PIL.Image import Image
from PIL.ImageColor import getrgb

import arcade
from arcade import RGBA, Color, DEFAULT_FONT_NAMES


def parse_value(value: Any):
    """
    Parses the input string returning rgb int-tuple.

    Supported formats:

    * RGB ('r,g,b', 'r, g, b')
    * HEX ('00ff00')
    * Arcade colors ('BLUE', 'DARK_BLUE')

    """
    import arcade

    if value in (None, '', 'None'):
        return None

    if type(value) in (int, float, list):
        return value

    # if a string, then try parsing
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            pass

        # arcade color
        if isinstance(value, str) and hasattr(arcade.color, value.upper()):
            return getattr(arcade.color, value)

        # hex
        if len(value) in (3, 6) and ',' not in value:
            try:
                return getrgb(f'#{value}')
            except ValueError:
                pass

        # rgb
        try:
            return getrgb(f'rgb({value})')
        except ValueError:
            pass

        # last chance some Path
        if os.path.exists(value):
            return Path(value)

    warn(f'Could not parse style value: {value}')
    return value


def add_margin(pil_img, top, right, bottom, left, color=None):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def get_image_with_text(text: str,
                        font_color: Color,
                        background_image: Image,
                        font_size: float = 12,
                        align: str = "left",
                        valign: str = "top",
                        font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial'),
                        indent=0
                        ) -> Image:
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
        try:
            import pyglet.font
            font_config = pyglet.font.fontconfig.get_fontconfig()
            result = font_config.find_font('Arial')
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
        raise RuntimeError("Unable to find a default font on this system. Please specify an available font.")

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

    # Wait! We have a image width to match.
    width = background_image.width
    if align == "center":
        # Center text on given field width
        field_width = width * scale_up
        image_start_x = (field_width // 2) - (text_width // 2)
    else:
        image_start_x = indent

    # Find y of top-left corner
    image_start_y = 0
    height = background_image.height
    if valign == "middle":
        field_height = height * scale_up
        image_start_y = (field_height // 2) - (text_height // 2)

    text_image_size[1] = height * scale_up
    text_image_size[0] = width * scale_up

    # Create image
    image = background_image.resize(text_image_size, resample=PIL.Image.LANCZOS)
    draw = PIL.ImageDraw.Draw(image)

    # Convert to tuple if needed, because the multiline_text does not take a
    # list for a color
    if isinstance(font_color, list):
        color = cast(RGBA, tuple(font_color))
    draw.multiline_text((image_start_x, image_start_y), text, font_color, align=align, font=font)
    image = image.resize((max(1, text_image_size[0] // scale_down), text_image_size[1] // scale_down),
                         resample=PIL.Image.LANCZOS)
    return image


# taken from arcade 2.4 alpha
# TODO remove this!
def get_text_image(text: str,
                   font_color: Color,
                   font_size: float = 12,
                   width: int = 0,
                   align: str = "left",
                   valign: str = "top",
                   font_name: Union[str, Tuple[str, ...]] = ('calibri', 'arial'),
                   background_color: Color = None,
                   height: int = 0,
                   indent=0
                   ) -> Image:
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
        try:
            import pyglet.font
            font_config = pyglet.font.fontconfig.get_fontconfig()
            result = font_config.find_font('Arial')
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
        raise RuntimeError("Unable to find a default font on this system. Please specify an available font.")

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
            image_start_x = indent

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
    if isinstance(font_color, list):
        color = cast(RGBA, tuple(font_color))
    draw.multiline_text((image_start_x, image_start_y), text, font_color, align=align, font=font)
    image = image.resize((max(1, text_image_size[0] // scale_down), text_image_size[1] // scale_down),
                         resample=PIL.Image.LANCZOS)
    return image


def render_text_image(
        text: str,

        font_size=22,
        font_name=('Calibri', 'Arial'),
        font_color: Color = arcade.color.WHITE,

        border_width: int = 2,
        border_color: Optional[Color] = arcade.color.WHITE,

        align: str = "left",
        valign: str = "top",

        bg_color: Optional[Color] = None,
        bg_image: Optional[Image] = None,

        width: int = 0,
        height: int = 0,
        indent: int = 0
):
    if bg_image:

        if width:
            if not height:
                height = bg_image.height
            bg_image.resize((width, height), resample=PIL.Image.LANCZOS)

        image = get_image_with_text(
            text,
            font_name=font_name,
            font_color=font_color,
            font_size=font_size,

            background_image=bg_image,
            align=align,
            valign=valign,
            indent=indent
        )
    else:
        image = get_text_image(
            text,
            font_name=font_name,
            font_color=font_color,
            font_size=font_size,

            background_color=bg_color,
            align=align,
            valign=valign,
            indent=indent,

            width=width,
            height=height
        )

    # draw outline
    if border_width is None:
        border_width = 0
    rect = [0,
            0,
            image.width - border_width / 2,
            image.height - border_width / 2]

    if border_color and border_width:
        d = ImageDraw.Draw(image)
        d.rectangle(rect, fill=None, outline=border_color, width=border_width)

    return image
