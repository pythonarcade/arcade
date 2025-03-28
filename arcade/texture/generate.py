import PIL.Image
import PIL.ImageDraw
import PIL.ImageOps

from arcade import cache
from arcade.color import TRANSPARENT_BLACK
from arcade.hitbox import HitBoxAlgorithm
from arcade.math import lerp
from arcade.types import RGBA255

from .texture import ImageData, Texture


def make_circle_texture(
    diameter: int,
    color: RGBA255,
    name: str | None = None,
    hit_box_algorithm: HitBoxAlgorithm | None = None,
) -> Texture:
    """
    Creates a :class:`Texture` of a circle with the given diameter and color.

    Args:
        diameter:
            Diameter of the circle and dimensions of the square :class:`Texture` returned.
        color:
            Color of the circle as a :py:class:`~arcade.types.Color` instance a 3 or 4 tuple.
        name:
            A unique name for the texture. If not provided, a name will be generated.
            This is used for caching and unique identifier for texture atlases.
        hit_box_algorithm:
            The hit box algorithm to use for this texture. If not provided, the default
            hit box algorithm will be used.
    """
    name = name or cache.crate_str_from_values(
        "circle_texture", diameter, color[0], color[1], color[2]
    )
    bg_color = TRANSPARENT_BLACK  # fully transparent
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=color)
    return Texture(ImageData(img, hash=name), hit_box_algorithm=hit_box_algorithm)


def make_soft_circle_texture(
    diameter: int,
    color: RGBA255,
    center_alpha: int = 255,
    outer_alpha: int = 0,
    name: str | None = None,
    hit_box_algorithm: HitBoxAlgorithm | None = None,
) -> Texture:
    """
    Creates a :class:`Texture` of a circle with the given diameter and color,
    fading out at its edges.

    Args:
        diameter:
            Diameter of the circle and dimensions of the square :class:`Texture` returned.
        color:
            Color of the circle as a 4-length tuple or :py:class:`~arcade.types.Color` instance.
        center_alpha:
            Alpha value of the circle at its center.
        outer_alpha:
            Alpha value of the circle at its edges.
        name:
            A unique name for the texture. If not provided, a name will be generated.
            This is used for caching and unique identifier for texture atlases.
        hit_box_algorithm:
            The hit box algorithm to use for this texture. If not provided, the default
            hit box algorithm will be used.
    """
    # Name must be unique for caching
    name = cache.crate_str_from_values(
        "soft_circle_texture",
        diameter,
        color[0],
        color[1],
        color[2],
        center_alpha,
        outer_alpha,
    )

    bg_color = TRANSPARENT_BLACK
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    max_radius = int(diameter // 2)
    center = max_radius

    for radius in range(max_radius, 0, -1):
        alpha = int(lerp(center_alpha, outer_alpha, radius / max_radius))
        clr = (color[0], color[1], color[2], alpha)
        draw.ellipse(
            (
                center - radius,
                center - radius,
                center + radius - 1,
                center + radius - 1,
            ),
            fill=clr,
        )

    return Texture(ImageData(img, name), hit_box_algorithm=hit_box_algorithm)


def make_soft_square_texture(
    size: int,
    color: RGBA255,
    center_alpha: int = 255,
    outer_alpha: int = 0,
    name: str | None = None,
) -> Texture:
    """
    Creates a :class:`Texture` of a square with the given diameter and color,
    fading out at its edges.

    Args:
        size:
            Diameter of the square and dimensions of the square Texture returned.
        color:
            Color of the square.
        center_alpha:
            Alpha value of the square at its center.
        outer_alpha:
            Alpha value of the square at its edges.
        name:
            A unique name for the texture. If not provided, a name will be generated.
            This is used for caching and unique identifier for texture atlases.
    """
    # Build name used for caching
    name = name or cache.crate_str_from_values(
        "gradient-square", size, color, center_alpha, outer_alpha
    )

    # Generate the soft square image
    bg_color = TRANSPARENT_BLACK
    img = PIL.Image.new("RGBA", (size, size), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    half_size = int(size // 2)

    for cur_size in range(0, half_size):
        alpha = int(lerp(outer_alpha, center_alpha, cur_size / half_size))
        clr = (color[0], color[1], color[2], alpha)
        draw.rectangle((cur_size, cur_size, size - cur_size, size - cur_size), clr, None)

    return Texture(img, name=name)
