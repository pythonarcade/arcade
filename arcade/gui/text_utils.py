"""
This collection contains functions to generate text, apply space around, padding and draw borders for PIL.Images.
"""
from itertools import chain
from typing import Tuple, Union, Iterable, NamedTuple, Sequence

from PIL import Image, ImageDraw, ImageOps, ImageFont

from arcade import Color, DEFAULT_FONT_NAMES
from arcade.utils import generate_uuid

TEXT_SCALE_ALIASED = 2
LEGACY_FONT_SIZE_MODE = True


class Padding(NamedTuple):
    """
    Data class to hold padding for a GUI item. Has fields for top, bottom, left, and right.
    """
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    @property
    def vertical(self):
        return self.top + self.bottom

    @property
    def horizontal(self):
        return self.left + self.right

    @staticmethod
    def resolve(pad: Union[int, Sequence[int]]) -> "Padding":
        if isinstance(pad, int):
            return Padding(pad, pad, pad, pad)
        elif len(pad) == 2:
            pad_v, pad_h = pad
            return Padding(pad_v, pad_h, pad_v, pad_h)
        elif len(pad) == 4:
            return Padding(*pad)
        else:
            raise Exception(
                f"Invalid value for padding, either int, (int, int), (int, int, int, int) allowed. ({pad})"
            )


def _find_font(font_name: Union[str, Iterable[str]], font_size: int):
    """
    Search font by name or a list of alternatives
    """
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

    # try to load preferred fonts
    for font_string_name in font_names:
        try:
            font = ImageFont.truetype(font_string_name, int(font_size))
            break
        except OSError:
            continue

    # Fallback to pyglet font
    if font is None:
        try:
            import pyglet.font

            font_config = pyglet.font.fontconfig.get_fontconfig()
            result = font_config.find_font("Arial")
            font = ImageFont.truetype(result.name, int(font_size))
        except Exception:
            # NOTE: Will catch OSError from loading font and missing fontconfig in pyglet
            pass

    # Final fallback just getting PIL's default font if possible
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            raise RuntimeError(
                "Unable to find a default font on this system. Please specify an available font."
            )

    return font


def create_raw_text_image(
    text: str,
    font_name: Union[str, Iterable[str]],
    font_size: int,
    font_color: Color,
    bg_image: Image.Image = None,
    bg_color: Color = (0, 0, 0, 0),
) -> Image:
    """
    Creates a PIL image with the given text, font, font_size, font_color, and bg_image.

    To add padding, margin, etc. use functions from :py:mod:`arcade.gui.utils`.
    """
    # Text isn't anti-aliased, so we'll draw big, and then shrink

    # Scale the font up, so it matches with the sizes of the old code back
    # when Pyglet drew the text.
    if LEGACY_FONT_SIZE_MODE:
        font_size *= 1.25

    # Text isn't anti-aliased, so we'll draw big, and then shrink
    font_size *= TEXT_SCALE_ALIASED

    font = _find_font(font_name, font_size)

    # create image with bg
    if bg_image is None:
        bg_image = Image.new("RGBA", font.getsize(text), bg_color)
    else:  # or use image, but scale it
        _w, _h = bg_image.size
        bg_image = bg_image.resize(
            (_w * TEXT_SCALE_ALIASED, _h * TEXT_SCALE_ALIASED), resample=Image.LANCZOS
        )
    draw = ImageDraw.Draw(bg_image)

    # Calculate the mid points and offset by the upper left corner of the bounding box
    draw.multiline_text(
        xy=(bg_image.width / 2, bg_image.height / 2),
        text=text,
        fill=font_color,
        align="left",
        font=font,
        anchor="mm",
    )
    bg_image = bg_image.resize(
        (
            bg_image.width // TEXT_SCALE_ALIASED,
            bg_image.height // TEXT_SCALE_ALIASED,
        ),
        resample=Image.LANCZOS,
    )
    return bg_image


def add_bg_color_to_image(
    image: Image,
    bg_color: Color,
) -> Image:
    """
    Adds background color, only usable for images with alpha and mode RGBA.
    """
    bg_image = Image.new("RGBA", image.size, bg_color)
    return Image.alpha_composite(bg_image, image)


def add_padding_to_image(image: Image, pad: Padding, color: Color):
    """
    Surrounds image with the given padding. The padding is filled with the color.
    """
    width, height = image.size
    new_width = width + pad.right + pad.left
    new_height = height + pad.top + pad.bottom
    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (pad.left, pad.top))
    return result


def add_border_to_image(
    image: Image,
    border_width: int,
    border_color: Color,
) -> Image:
    """
    Returns a new image with border. The size will be increased.
    """
    if border_width > 0 and border_color is not None:
        return ImageOps.expand(image, border=border_width, fill=border_color)
    else:
        return image


def expand_image(
    image: Image,
    size: Tuple[float, float],
    color: Color = (0, 0, 0, 0),
    v_align="top",
    h_align="left",
):
    """
    Returns a new image with space added around to fill up to the given size.
    If a dimension exceeds the requested size, no padding is applied in that dimension.

    v_align: vertical alignment (top, center, bottom)
    h_align: vertical alignment (left, center, right)
    color: fill color, default alpha
    """
    iw, ih = image.size
    w, h = size

    v_space = h - ih
    top = bottom = 0
    if v_space > 0:
        if v_align == "center":
            top = bottom = v_space // 2
        elif v_align == "bottom":
            top = v_space
        else:
            bottom = v_space

    h_space = w - iw
    left = right = 0
    if h_space > 0:
        if h_align == "center":
            left = right = h_space // 2
        elif h_align == "right":
            left = h_space
        else:
            right = h_space

    return add_padding_to_image(image, Padding(top, right, bottom, left), color)


def create_text(
    *,  # prevent positional arguments, this will ease signature changes
    # Text props
    text: str,
    font_name: Union[str, Iterable[str]],
    font_size: int,
    font_color: Color,
    bg_color: Color,
    # alignment
    min_width: float,
    min_height: float,
    v_align: str,
    h_align: str,
    # border props
    border_width: int,
    border_color: Color,
    padding: Padding = None,
) -> Tuple[Image.Image, str]:
    """
    Generates a PIL image with the given values.

    Together with the image a uuid is returned, which is generated using the given parameters
    """

    if border_color is None:
        border_width = 0

    if padding is None:
        padding = Padding()

    text_image_uuid = generate_uuid(
        # Text props
        text=text,
        font_name=font_name,
        font_size=font_size,
        font_color=font_color,
        bg_color=bg_color,
        # alignment
        min_width=min_width,
        min_height=min_height,
        v_align=v_align,
        h_align=h_align,
        # bg props
        border_width=border_width,
        border_color=border_color,
        padding=padding,
    )

    image = create_raw_text_image(
        text=text,
        font_name=font_name,
        font_size=font_size,
        font_color=font_color,
        bg_color=bg_color,
    )

    if padding.vertical > 0 or padding.horizontal > 0:
        image = add_padding_to_image(image, padding, bg_color)

    image = expand_image(
        image=image,
        size=(min_width - 2 * border_width, min_height - 2 * border_width),
        color=bg_color,
        v_align=v_align,
        h_align=h_align,
    )
    image = add_border_to_image(
        image=image,
        border_width=border_width,
        border_color=border_color,
    )

    return image, text_image_uuid

