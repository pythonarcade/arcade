from __future__ import annotations

import dataclasses
import math
from typing import List

from .sprite import Sprite
from arcade import Texture
from arcade.types import PathOrTexture
from .enums import (
    FACE_LEFT,
    FACE_RIGHT,
    FACE_UP,
    FACE_DOWN,
)


@dataclasses.dataclass
class AnimationKeyframe:
    """
    Keyframe for texture animations.
    """
    tile_id: int
    duration: int
    texture: Texture


class AnimatedTimeBasedSprite(Sprite):
    """
    Sprite for platformer games that supports animations. These can
    be automatically created by the Tiled Map Editor.

    :param path_or_texture: Path to the image file, or a Texture object.
    :param center_x: Initial x position of the sprite.
    :param center_y: Initial y position of the sprite.
    :param scale: Initial scale of the sprite.
    """
    def __init__(
        self,
        path_or_texture: PathOrTexture = None,
        center_x: float = 0.0,
        center_y: float = 0.0,
        scale: float = 1.0,
        **kwargs,
    ):
        super().__init__(
            path_or_texture,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )
        self.cur_frame_idx = 0
        self.frames: List[AnimationKeyframe] = []
        self.time_counter = 0.0

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        """
        Logic for updating the animation.

        :param float delta_time: Time since last update.
        """
        self.time_counter += delta_time
        while self.time_counter > self.frames[self.cur_frame_idx].duration / 1000.0:
            self.time_counter -= self.frames[self.cur_frame_idx].duration / 1000.0
            self.cur_frame_idx += 1
            if self.cur_frame_idx >= len(self.frames):
                self.cur_frame_idx = 0
            # source = self.frames[self.cur_frame].texture.image.source
            cur_frame = self.frames[self.cur_frame_idx]
            # print(f"Advance to frame {self.cur_frame_idx}: {cur_frame.texture.name}")
            self.texture = cur_frame.texture


class AnimatedWalkingSprite(Sprite):
    """
    Deprecated Sprite for platformer games that supports walking animations.
    Make sure to call update_animation after loading the animations so the
    initial texture can be set. Or manually set it.

    It is highly recommended you create your own version of this class rather than
    try to use this pre-packaged one.

    For an example, see this section of the platformer tutorial:
    :ref:`platformer_part_twelve`.

    :param scale: Initial scale of the sprite.
    :param center_x: Initial x position of the sprite.
    :param center_y: Initial y position of the sprite.
    """
    def __init__(
        self,
        scale: float = 1.0,
        center_x: float = 0.0,
        center_y: float = 0.0,
        **kwargs,
    ):
        super().__init__(
            None,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )
        self.state = FACE_RIGHT
        self.stand_right_textures: List[Texture] = []
        self.stand_left_textures: List[Texture] = []
        self.walk_left_textures: List[Texture] = []
        self.walk_right_textures: List[Texture] = []
        self.walk_up_textures: List[Texture] = []
        self.walk_down_textures: List[Texture] = []
        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.last_texture_change_center_x: float = 0.0
        self.last_texture_change_center_y: float = 0.0

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        """
        Logic for texture animation.

        :param float delta_time: Time since last update.
        """
        x1 = self.center_x
        x2 = self.last_texture_change_center_x
        y1 = self.center_y
        y2 = self.last_texture_change_center_y
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        texture_list: List[Texture] = []

        change_direction = False
        if (
            self.change_x > 0
            and self.change_y == 0
            and self.state != FACE_RIGHT
            and len(self.walk_right_textures) > 0
        ):
            self.state = FACE_RIGHT
            change_direction = True
        elif (
            self.change_x < 0
            and self.change_y == 0
            and self.state != FACE_LEFT
            and len(self.walk_left_textures) > 0
        ):
            self.state = FACE_LEFT
            change_direction = True
        elif (
            self.change_y < 0
            and self.change_x == 0
            and self.state != FACE_DOWN
            and len(self.walk_down_textures) > 0
        ):
            self.state = FACE_DOWN
            change_direction = True
        elif (
            self.change_y > 0
            and self.change_x == 0
            and self.state != FACE_UP
            and len(self.walk_up_textures) > 0
        ):
            self.state = FACE_UP
            change_direction = True

        if self.change_x == 0 and self.change_y == 0:
            if self.state == FACE_LEFT:
                self.texture = self.stand_left_textures[0]
            elif self.state == FACE_RIGHT:
                self.texture = self.stand_right_textures[0]
            elif self.state == FACE_UP:
                self.texture = self.walk_up_textures[0]
            elif self.state == FACE_DOWN:
                self.texture = self.walk_down_textures[0]

        elif change_direction or distance >= self.texture_change_distance:
            self.last_texture_change_center_x = self.center_x
            self.last_texture_change_center_y = self.center_y

            if self.state == FACE_LEFT:
                texture_list = self.walk_left_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a "
                        "list of walk left textures."
                    )
            elif self.state == FACE_RIGHT:
                texture_list = self.walk_right_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of "
                        "walk right textures."
                    )
            elif self.state == FACE_UP:
                texture_list = self.walk_up_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of "
                        "walk up textures."
                    )
            elif self.state == FACE_DOWN:
                texture_list = self.walk_down_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of walk down textures."
                    )

            self.cur_texture_index += 1
            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0

            self.texture = texture_list[self.cur_texture_index]

        if self._texture is None:
            print("Error, no texture set")
        else:
            self.width = self._texture.width * self.scale
            self.height = self._texture.height * self.scale
