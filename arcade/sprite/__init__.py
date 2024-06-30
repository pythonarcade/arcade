from __future__ import annotations

import PIL.Image

from arcade.texture import Texture
from arcade.resources import resolve
from .base import BasicSprite, SpriteType
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


def load_animated_gif(resource_name) -> TextureAnimationSprite:
    """
    Attempt to load an animated GIF as an :class:`TextureAnimationSprite`.

    Many older GIFs will load with incorrect transparency for every
    frame but the first. Until the Pillow library handles the quirks of
    the format better, loading animated GIFs will be pretty buggy. A
    good workaround is loading GIFs in another program and exporting them
    as PNGs, either as sprite sheets or a frame per file.
    """

    file_name = resolve(resource_name)
    image_object = PIL.Image.open(file_name)
    if not image_object.is_animated:
        raise TypeError(f"The file {resource_name} is not an animated gif.")

    sprite = TextureAnimationSprite()
    keyframes = []
    for frame in range(image_object.n_frames):
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
