"""
Particle - Object produced by an Emitter.  Often used in large quantity to produce visual effects effects
"""

from arcade.sprite import Sprite
from arcade.draw_commands import Texture
import arcade.utils
from pymunk import Vec2d


class Particle(Sprite):
    """Sprite that is emitted from an Emitter"""
    def __init__(
        self,
        filename_or_texture: str,
        vel: Vec2d,
        pos: Vec2d = None,
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        alpha: int = 255,
        mutation_callback = None
    ):
        if pos is None:
            pos = Vec2d.zero()

        if isinstance(filename_or_texture, Texture):
            super().__init__(None, scale=scale)
            self.append_texture(filename_or_texture)
            self.set_texture(0)
        else:
            super().__init__(filename_or_texture, scale=scale)

        self.center_x = pos.x
        self.center_y = pos.y
        self.change_x = vel.x
        self.change_y = vel.y
        self.angle = angle
        self.change_angle = change_angle
        self.alpha = alpha
        self.mutation_callback = mutation_callback

    def update(self):
        """Advance the Particle's simulation"""
        super().update()
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
        filename_or_texture: str,
        vel: Vec2d,
        pos: Vec2d = None,
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        alpha: int = 255,
        mutation_callback=None
    ):
        super().__init__(filename_or_texture, vel, pos, angle, change_angle, scale, alpha, mutation_callback)

    def can_reap(self):
        """Determine if Particle can be deleted"""
        return False


class LifetimeParticle(Particle):
    """Particle that lives for a given amount of time and is then deleted"""
    def __init__(
        self,
        filename_or_texture: str,
        vel: Vec2d,
        lifetime: float,
        pos: Vec2d = None,
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        alpha: int = 255,
        mutation_callback = None
    ):
        super().__init__(filename_or_texture, vel, pos, angle, change_angle, scale, alpha, mutation_callback)
        self.lifetime_original = lifetime
        self.lifetime_elapsed = 0.0

    def update(self):
        """Advance the Particle's simulation"""
        super().update()
        self.lifetime_elapsed += 1/60

    def can_reap(self):
        """Determine if Particle can be deleted"""
        return self.lifetime_elapsed >= self.lifetime_original


class FadeParticle(LifetimeParticle):
    """Particle that animates its alpha between two values during its lifetime"""
    def __init__(
        self,
        filename_or_texture: str,
        vel: Vec2d,
        lifetime: float,
        pos: Vec2d = None,
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        start_alpha: int = 255,
        end_alpha: int = 0,
        mutation_callback=None
    ):
        super().__init__(filename_or_texture, vel, lifetime, pos, angle, change_angle, scale, start_alpha, mutation_callback)
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha

    def update(self):
        """Advance the Particle's simulation"""
        super().update()
        self.alpha = arcade.utils.lerp(self.start_alpha, self.end_alpha, self.lifetime_elapsed / self.lifetime_original)
