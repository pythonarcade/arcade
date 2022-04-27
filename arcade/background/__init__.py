from PIL import Image

import arcade.gl as gl
from arcade import get_window
from arcade.resources import resolve_resource_path
from arcade.color import WHITE

from arcade.background.background_texture import BackgroundTexture
from arcade.background.background import Background
from arcade.background.groups import BackgroundGroup, ParallaxGroup


def texture_from_file(tex_src: str,
                      offset: tuple[float, float] = (0.0, 0.0),
                      scale: float = 1.0,
                      angle: float = 0.0,
                      filters=(gl.NEAREST, gl.NEAREST)) -> BackgroundTexture:
    _context = get_window().ctx

    with Image.open(resolve_resource_path(tex_src)).convert("RGBA") as img:
        texture = _context.texture(img.size, data=img.transpose(Image.FLIP_TOP_BOTTOM).tobytes(),
                                   filter=filters)

    return BackgroundTexture(texture, offset, scale, angle)


def background_from_file(tex_src: str,
                         pos: tuple[float, float] = (0.0, 0.0),
                         size: tuple[int, int] = None,
                         offset: tuple[float, float] = (0.0, 0.0),
                         scale: float = 1.0,
                         angle: float = 0.0,
                         *,
                         filters=(gl.NEAREST, gl.NEAREST),
                         color=WHITE,
                         shader: gl.Program = None,
                         geometry: gl.Geometry = None) -> Background:

    texture = BackgroundTexture.from_file(tex_src, offset, scale, angle, filters)
    if size is None:
        size = texture.texture.size

    return Background(texture, pos, size, color, shader, geometry)
