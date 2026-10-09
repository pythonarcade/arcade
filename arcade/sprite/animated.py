import bisect
import logging

from arcade import Texture

from .sprite import Sprite

logger = logging.getLogger("arcade")


class TextureKeyframe:
    """
    Keyframe for texture animations.

    Args:
        texture:
            Texture to display for this keyframe.
        duration:
            Duration in milliseconds to display this keyframe.
        tile_id:
            Tile ID for this keyframe (only used for tiled maps).
            This can be ignored when not using tiled maps.
    """

    __slots__ = ("texture", "duration", "tile_id")

    def __init__(self, texture: Texture, duration: int = 100, tile_id: int | None = 0, **kwargs):
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

    Args:
        keyframes:
            List of keyframes for the animation.
    """

    __slots__ = ("_keyframes", "_duration_ms", "_timeline")

    def __init__(self, keyframes: list[TextureKeyframe]):
        self._keyframes = keyframes
        self._duration_ms = 0
        self._timeline: list[int] = self._create_timeline(self._keyframes)

    @property
    def keyframes(self) -> tuple[TextureKeyframe, ...]:
        """
        A tuple of keyframes in the animation.
        Keyframes should not be modified directly.
        """
        return tuple(self._keyframes)

    @property
    def duration_seconds(self) -> float:
        """Total duration of the animation in seconds."""
        return self._duration_ms / 1000

    @property
    def duration_ms(self) -> int:
        """Total duration of the animation in milliseconds."""
        return self._duration_ms

    @property
    def num_frames(self) -> int:
        """Number of frames in the animation."""
        return len(self._keyframes)

    def _create_timeline(self, keyframes: list[TextureKeyframe]) -> list[int]:
        """
        Create a timeline of the animation.

        This is a list of timestamps for each frame in seconds.
        """
        timeline: list[int] = []
        current_time_ms = 0
        for frame in keyframes:
            timeline.append(current_time_ms)
            current_time_ms += frame.duration

        self._duration_ms = current_time_ms
        return timeline

    def get_keyframe(self, time: float, loop: bool = True) -> tuple[int, TextureKeyframe]:
        """
        Get the frame at a given time.

        Args:
            time:
                Time in seconds.
            loop:
                If the animation should loop.
        Returns:
            Tuple of frame index and keyframe.
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

    Primarily used internally by tilemaps to animate tiles.

    Args:
        path_or_texture:
            Path to the image file, or a Texture object.
        center_x:
            Initial x position of the sprite.
        center_y:
            Initial y position of the sprite.
        scale:
            Initial scale of the sprite.
        **kwargs:
            Passed to :py:class:`~arcade.Sprite`, such as ``angle``, ``scale`` or ``visible``.
    """

    def __init__(
        self,
        center_x: float = 0.0,
        center_y: float = 0.0,
        scale: float = 1.0,
        animation: TextureAnimation | None = None,
        **kwargs,
    ):
        super().__init__(
            scale=scale,
            center_x=center_x,
            center_y=center_y,
            **kwargs,
        )
        self._time = 0.0
        self._animation: TextureAnimation | None = None
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

        Args:
            value: Animation to set.
        """
        self._animation = value
        # TODO: Forcing the first frame here might not be the best idea.
        self.texture = value._keyframes[0].texture
        self.sync_hit_box_to_texture()

    def update_animation(self, delta_time: float = 1 / 60, **kwargs) -> None:
        """
        Logic for updating the animation.

        Args:
            delta_time: Time since last update.
        """
        if self._animation is None:
            raise RuntimeError("No animation set for this sprite.")

        self.time += delta_time
        index, keyframe = self._animation.get_keyframe(self.time)
        if index != self._current_keyframe_index:
            self._current_keyframe_index = index
            self.texture = keyframe.texture
