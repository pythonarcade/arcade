"""
Particle - Object produced by an Emitter.
Often used in large quantity to produce visual effects effects
"""

from typing import Literal

from arcade.math import clamp, lerp
from arcade.sprite import Sprite
from arcade.types import PathOrTexture, Point, Velocity


class Particle(Sprite):
    """Sprite that is emitted from an Emitter"""

    def __init__(
        self,
        path_or_texture: PathOrTexture | None,
        change_xy: tuple[float, float],
        center_xy: Point = (0.0, 0.0),
        angle: float = 0.0,
        change_angle: float = 0.0,
        scale: float = 1.0,
        alpha: int = 255,
        mutation_callback=None,
    ):
        super().__init__(path_or_texture, scale=scale)
        self.center_x = center_xy[0]
        self.center_y = center_xy[1]
        self.change_x = change_xy[0]
        self.change_y = change_xy[1]
        self.angle = angle
        self.change_angle = change_angle
        self.alpha = alpha
        self.mutation_callback = mutation_callback

    def update(self, delta_time: float = 1 / 60):
        """Advance the Particle's simulation"""
        super().update(delta_time)
        if self.mutation_callback:
            self.mutation_callback(self)

    # def draw(self):
    #     raise NotImplementedError("Particle.draw needs to be implemented")

    def can_reap(self):
        """Determine if Particle can be deleted"""
        raise NotImplementedError("Particle.can_reap needs to be implemented")


class EternalParticle(Particle):
    """Particle that has no end to its life"""

    def __init__(
        self,
        filename_or_texture: PathOrTexture,
        change_xy: Velocity,
        center_xy: Point = (0.0, 0.0),
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        alpha: int = 255,
        mutation_callback=None,
    ):
        super().__init__(
            filename_or_texture,
            change_xy,
            center_xy,
            angle,
            change_angle,
            scale,
            alpha,
            mutation_callback,
        )

    def can_reap(self) -> Literal[False]:
        """Determine if Particle can be deleted"""
        return False


class LifetimeParticle(Particle):
    """Particle that lives for a given amount of time and is then deleted"""

    def __init__(
        self,
        filename_or_texture: PathOrTexture | None,
        change_xy: Velocity,
        lifetime: float,
        center_xy: Point = (0.0, 0.0),
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        alpha: int = 255,
        mutation_callback=None,
    ):
        super().__init__(
            filename_or_texture,
            change_xy,
            center_xy,
            angle,
            change_angle,
            scale,
            alpha,
            mutation_callback,
        )
        self.lifetime_original = lifetime
        self.lifetime_elapsed = 0.0

    def update(self, delta_time: float = 1 / 60):
        """Advance the Particle's simulation"""
        super().update(delta_time)
        self.lifetime_elapsed += delta_time

    def can_reap(self) -> bool:
        """Determine if Particle can be deleted"""
        return self.lifetime_elapsed >= self.lifetime_original


class FadeParticle(LifetimeParticle):
    """Particle that animates its alpha between two values during its lifetime"""

    def __init__(
        self,
        filename_or_texture: PathOrTexture,
        change_xy: Velocity,
        lifetime: float,
        center_xy: Point = (0.0, 0.0),
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        start_alpha: int = 255,
        end_alpha: int = 0,
        mutation_callback=None,
    ):
        super().__init__(
            filename_or_texture,
            change_xy,
            lifetime,
            center_xy,
            angle,
            change_angle,
            scale,
            start_alpha,
            mutation_callback,
        )
        self.start_alpha = start_alpha
        self.alpha = start_alpha
        self.end_alpha = end_alpha

    def update(self, delta_time: float = 1 / 60):
        """Advance the Particle's simulation"""
        super().update(delta_time)
        a = lerp(self.start_alpha, self.end_alpha, self.lifetime_elapsed / self.lifetime_original)
        self.alpha = int(clamp(a, 0, 255))
