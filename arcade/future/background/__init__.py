from PIL import Image

import arcade.gl as gl
from arcade import get_window
from arcade.resources import resolve

from arcade.future.background.background_texture import BackgroundTexture
from arcade.future.background.background import Background
from arcade.future.background.groups import BackgroundGroup, ParallaxGroup

__all__ = [
    "Background",
    "BackgroundGroup",
    "BackgroundTexture",
    "ParallaxGroup",
    "texture_from_file",
    "background_from_file",
]


def texture_from_file(
    tex_src: str,
    offset: tuple[float, float] = (0.0, 0.0),
    scale: float = 1.0,
    angle: float = 0.0,
    filters=(gl.NEAREST, gl.NEAREST),
) -> BackgroundTexture:
    _context = get_window().ctx

    with Image.open(resolve(tex_src)).convert("RGBA") as img:
        texture = _context.texture(
            img.size,
            data=img.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes(),
            filter=filters,
        )

    return BackgroundTexture(texture, offset, scale, angle)


def background_from_file(
    tex_src: str,
    pos: tuple[float, float] = (0.0, 0.0),
    size: tuple[int, int] | None = None,
    offset: tuple[float, float] = (0.0, 0.0),
    scale: float = 1.0,
    angle: float = 0.0,
    *,
    filters=(gl.NEAREST, gl.NEAREST),
    color: tuple[int, int, int] | None = None,
    color_norm: tuple[float, float, float] | None = None,
    shader: gl.Program | None = None,
    geometry: gl.Geometry | None = None,
) -> Background:
    texture = BackgroundTexture.from_file(tex_src, offset, scale, angle, filters)
    if size is None:
        size = texture.texture.size

    if color_norm:
        _color = color_norm
    elif color:
        _color = color[0] / 255, color[1] / 255, color[2] / 255
    else:
        _color = (1.0, 1.0, 1.0)

    return Background(texture, pos, size, _color, shader, geometry)
