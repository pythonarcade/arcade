import PIL.Image

import arcade
from arcade.texture import Texture
from arcade.resources import resolve_resource_path
from .base import Sprite, PyMunk
from .animated import (
    AnimatedTimeBasedSprite,
    AnimationKeyframe,
    AnimatedWalkingSprite,
)
from .simple import SpriteSolidColor, SpriteCircle
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

    file_name = resolve_resource_path(resource_name)
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


def get_distance_between_sprites(sprite1: Sprite, sprite2: Sprite) -> float:
    """
    Returns the distance between the center of two given sprites

    :param Sprite sprite1: Sprite one
    :param Sprite sprite2: Sprite two
    :return: Distance
    :rtype: float
    """
    return arcade.get_distance(*sprite1._position, *sprite2._position)


__all__ = [
    "Sprite",
    "PyMunk",
    "AnimatedTimeBasedSprite",
    "AnimationKeyframe",
    "AnimatedWalkingSprite",
    "load_animated_gif",
    "get_distance_between_sprites",
    "SpriteSolidColor",
    "SpriteCircle",
    "FACE_LEFT",
    "FACE_RIGHT",
    "FACE_UP",
    "FACE_DOWN",
]
