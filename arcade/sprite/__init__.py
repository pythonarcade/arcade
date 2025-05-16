from pathlib import Path

import PIL.Image

from arcade.texture import Texture
from arcade.resources import resolve
from .base import BasicSprite, SpriteType, SpriteType_co
from .sprite import Sprite
from .mixins import PymunkMixin, PyMunk
from .animated import (
    TextureAnimationSprite,
    TextureAnimation,
    TextureKeyframe,
    AnimatedWalkingSprite,
)
from .colored import SpriteSolidColor, SpriteCircle
from .enums import (
    FACE_LEFT,
    FACE_RIGHT,
    FACE_UP,
    FACE_DOWN,
)


def load_animated_gif(resource_name: str | Path) -> TextureAnimationSprite:
    """
    Attempt to load an animated GIF as a :class:`TextureAnimationSprite`.

    .. note::

        Many older GIFs will load with incorrect transparency for every
        frame but the first. Until the Pillow library handles the quirks of
        the format better, loading animated GIFs will be pretty buggy. A
        good workaround is loading GIFs in another program and exporting them
        as PNGs, either as sprite sheets or a frame per file.

    Args:
        resource_name: A path to a GIF as either a :py:class:`pathlib.Path`
            or a :py:class:`str` which may include a
            :ref:`resource handle <resource_handles>`.

    """

    file_name = resolve(resource_name)
    image_object = PIL.Image.open(file_name)

    # Pillow doc recommends testing for the is_animated attribute as of 10.0.0
    # https://pillow.readthedocs.io/en/stable/deprecations.html#categories
    if not getattr(image_object, "is_animated", False) or not (
        n_frames := getattr(image_object, "n_frames", 0)
    ):
        raise TypeError(f"The file {resource_name} is not an animated gif.")

    sprite = TextureAnimationSprite()
    keyframes = []
    for frame in range(n_frames):
        image_object.seek(frame)
        frame_duration = image_object.info["duration"]
        image = image_object.convert("RGBA")
        texture = Texture(image)
        texture.file_path = file_name
        # sprite.textures.append(texture)
        keyframes.append(TextureKeyframe(texture, frame_duration))

    animation = TextureAnimation(keyframes=keyframes)
    sprite.animation = animation
    return sprite


__all__ = [
    "SpriteType",
    "SpriteType_co",
    "BasicSprite",
    "Sprite",
    "PyMunk",
    "TextureAnimationSprite",
    "TextureAnimation",
    "TextureKeyframe",
    "AnimatedWalkingSprite",
    "load_animated_gif",
    "SpriteSolidColor",
    "SpriteCircle",
    "FACE_LEFT",
    "FACE_RIGHT",
    "FACE_UP",
    "FACE_DOWN",
    "PymunkMixin",
]
