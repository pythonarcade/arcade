from __future__ import annotations

import bisect
import math
from typing import List, Optional, Tuple

from .sprite import Sprite
from arcade import Texture
from .enums import (
    FACE_LEFT,
    FACE_RIGHT,
    FACE_UP,
    FACE_DOWN,
)


class TextureKeyframe:
    """
    Keyframe for texture animations.

    :param texture: Texture to display for this keyframe.
    :param duration: Duration in milliseconds to display this keyframe.
    :param tile_id: Tile ID for this keyframe (only used for tiled maps)
    """
    __slots__ = ("texture", "duration", "tile_id")
    def __init__(
        self,
        texture: Texture,
        duration: int = 100,
        tile_id: Optional[int] = 0,
        **kwargs
    ):
        #: The texture to display for this keyframe.
        self.texture = texture
        #: Duration in milliseconds to display this keyframe.
        self.duration = duration
        #: Tile ID for this keyframe (only used for tiled maps)
        self.tile_id = tile_id


class TextureAnimation:
    """
    Animation class that holds a list of keyframes.
    The animation should not store any state related to the current time
    so it can be shared between multiple sprites.

    :param keyframes: List of keyframes for the animation.
    :param loop: If the animation should loop.
    """
    __slots__ = ("_keyframes", "_duration_ms", "_timeline")

    def __init__(self, keyframes: List[TextureKeyframe]):
        self._keyframes = keyframes
        self._duration_ms = 0
        self._timeline: List[int] = self._create_timeline(self._keyframes)

    @property
    def keyframes(self) -> Tuple[TextureKeyframe, ...]:
        """
        A tuple of keyframes in the animation.
        Keyframes should not be modified directly.
        """
        return tuple(self._keyframes)

    @property
    def duration_seconds(self) -> float:
        """
        Total duration of the animation in seconds.
        """
        return self._duration_ms / 1000

    @property
    def duration_ms(self) -> int:
        """
        Total duration of the animation in milliseconds.
        """
        return self._duration_ms

    @property
    def num_frames(self) -> int:
        """
        Number of frames in the animation.
        """
        return len(self._keyframes)

    def _create_timeline(self, keyframes: List[TextureKeyframe]) -> List[int]:
        """
        Create a timeline of the animation.
        This is a list of timestamps for each frame in seconds.
        """
        timeline: List[int] = []
        current_time_ms = 0
        for frame in keyframes:
            timeline.append(current_time_ms)
            current_time_ms += frame.duration

        self._duration_ms = current_time_ms
        return timeline

    def get_keyframe(self, time: float, loop: bool = True) -> Tuple[int, TextureKeyframe]:
        """
        Get the frame at a given time.

        :param time: Time in seconds.
        :param loop: If the animation should loop.
        :return: Tuple of frame index and keyframe.
        """
        if loop:
            time_ms = int(time * 1000) % self._duration_ms
        else:
            time_ms = int(time * 1000)

        # Find the right insertion point for the time: O(log n)
        index = bisect.bisect_right(self._timeline, time_ms) - 1
        index = max(0, min(index, len(self._keyframes) - 1))
        return index, self._keyframes[index]

    def __len__(self) -> int:
        return len(self._keyframes)


# Old name: AnimatedTimeBasedSprite
class TextureAnimationSprite(Sprite):
    """
    Animated sprite based on keyframes.
    Primarily used internally by tilemaps.

    :param path_or_texture: Path to the image file, or a Texture object.
    :param center_x: Initial x position of the sprite.
    :param center_y: Initial y position of the sprite.
    :param scale: Initial scale of the sprite.
    """
    def __init__(
        self,
        center_x: float = 0.0,
        center_y: float = 0.0,
        scale: float = 1.0,
        animation: Optional[TextureAnimation] = None,
        **kwargs,
    ):
        super().__init__(
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )
        self._time = 0.0
        self._animation: Optional[TextureAnimation] = None
        if animation:
            self.animation = animation
        self._current_keyframe_index = 0

    @property
    def time(self) -> float:
        """
        Get or set the current time of the animation in seconds.
        """
        return self._time

    @time.setter
    def time(self, value: float) -> None:
        self._time = value

    @property
    def animation(self) -> TextureAnimation:
        """
        Animation object for this sprite.
        """
        if self._animation is None:
            raise RuntimeError("No animation set for this sprite.")
        return self._animation

    @animation.setter
    def animation(self, value: TextureAnimation) -> None:
        """
        Set the animation for this sprite.

        :param value: Animation to set.
        """
        self._animation = value
        # TODO: Forcing the first frame here might not be the best idea.
        self.texture = value._keyframes[0].texture
        self.sync_hit_box_to_texture()

    def update_animation(self, delta_time: float = 1 / 60, **kwargs) -> None:
        """
        Logic for updating the animation.

        :param delta_time: Time since last update.
        """
        if self._animation is None:
            raise RuntimeError("No animation set for this sprite.")

        self.time += delta_time
        index, keyframe = self._animation.get_keyframe(self.time)
        if index != self._current_keyframe_index:
            self._current_keyframe_index = index
            self.texture = keyframe.texture


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

        :param delta_time: Time since last update.
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
