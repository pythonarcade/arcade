import PIL.Image

from arcade.texture import Texture
from arcade.resources import resolve
from .base import BasicSprite, SpriteType
from .sprite import Sprite
from .mixins import PymunkMixin, PyMunk
from .animated import (
    AnimatedTimeBasedSprite,
    AnimationKeyframe,
    AnimatedWalkingSprite,
)
from .colored import SpriteSolidColor, SpriteCircle
from .enums import (
    FACE_LEFT,
    FACE_RIGHT,
    FACE_UP,
    FACE_DOWN,
)


def load_animated_gif(resource_name) -> AnimatedTimeBasedSprite:
    """
    Attempt to load an animated GIF as an :class:`AnimatedTimeBasedSprite`.

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

    sprite = AnimatedTimeBasedSprite()
    for frame in range(image_object.n_frames):
        image_object.seek(frame)
        frame_duration = image_object.info['duration']
        image = image_object.convert("RGBA")
        texture = Texture(image)
        texture.file_path = file_name
        sprite.textures.append(texture)
        sprite.frames.append(AnimationKeyframe(0, frame_duration, texture))

    sprite.texture = sprite.textures[0]
    return sprite


__all__ = [
    "SpriteType",
    "BasicSprite",
    "Sprite",
    "PyMunk",
    "AnimatedTimeBasedSprite",
    "AnimationKeyframe",
    "AnimatedWalkingSprite",
    "load_animated_gif",
    "SpriteSolidColor",
    "SpriteCircle",
    "FACE_LEFT",
    "FACE_RIGHT",
    "FACE_UP",
    "FACE_DOWN",
    "PymunkMixin"
]
