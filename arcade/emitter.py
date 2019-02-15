"""
Emitter - Invisible object that determines when Particles are emitted, actually emits them, and manages them over their lifetime
"""

import arcade
from arcade.particle import Particle
from pymunk import Vec2d
from typing import Callable


##########
class EmitController:
    """Base class for how a client configure the rate at which an Emitter emits Particles

    Subclasses allow the client to control the rate and duration of emitting"""
    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        raise NotImplemented("EmitterRate.how_many must be implemented")

    def is_complete(self) -> bool:
        raise NotImplemented("EmitterRate.is_complete must be implemented")


class EmitBurst(EmitController):
    """Used to configure an Emitter to emit particles in one burst"""
    def __init__(self, count: int):
        self._is_complete = False
        self._count = count

    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        if not self._is_complete:
            self._is_complete = True
            return self._count
        return 0

    def is_complete(self) -> bool:
        return True


class EmitMaintainCount(EmitController):
    """Used to configure an Emitter so it emits particles so that the given count is always maintained"""
    def __init__(self, particle_count: int):
        self._target_count = particle_count

    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        return self._target_count - current_particle_count

    def is_complete(self) -> bool:
        return False


class EmitInterval(EmitController):
    """Base class used by subclasses that are used to configure an Emitter to have a constant rate of emitting. Will emit indefinitely."""
    def __init__(self, emit_interval: float):
        self._emit_interval = emit_interval
        self._carryover_time = 0.0

    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        self._carryover_time += delta_time
        emit_count = 0
        while self._carryover_time >= self._emit_interval:
            self._carryover_time -= self._emit_interval
            emit_count += 1
        return emit_count

    def is_complete(self) -> bool:
        return False


class EmitterIntervalWithCount(EmitInterval):
    """Used to configure an Emitter so it emits particles at the given interval, ending after emitting a given number of particles"""
    def __init__(self, emit_interval: float, particle_count: int):
        super().__init__(emit_interval)
        self._count_remaining = particle_count

    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        proposed_count = super().how_many(delta_time, current_particle_count)
        actual_count = min(proposed_count, self._count_remaining)
        self._count_remaining -= actual_count
        return actual_count

    def is_complete(self) -> bool:
        return self._count_remaining <= 0


class EmitterIntervalWithTime(EmitInterval):
    """Useed to configure an Emitter so it emits particles at the given interval, ending after given number of seconds"""
    def __init__(self, emit_interval: float, lifetime: float):
        super().__init__(emit_interval)
        self._lifetime = lifetime

    def how_many(self, delta_time: float, current_particle_count: int) -> int:
        if self._lifetime <= 0.0:
            return 0
        self._lifetime -= delta_time
        return super().how_many(delta_time, current_particle_count)

    def is_complete(self) -> bool:
        return self._lifetime <= 0



########## Emitter
class Emitter:
    """Emits and manages Particles over their lifetime.  The foundational class in a particle system."""
    def __init__(
        self,
        pos: Vec2d,
        emit_controller: EmitController,
        particle_factory: Callable[["Emitter"], Particle],
        vel: Vec2d = None,
        emit_done_cb: Callable[["Emitter"], None] = None,
        reap_cb: Callable[[], None] = None
    ):
        # Note Self-reference with type annotations: https://www.python.org/dev/peps/pep-0484/#the-problem-of-forward-declarations
        if vel is None:
            self.change_x = 0.0
            self.change_y = 0.0
        else:
            self.change_x = vel.x
            self.change_y = vel.y

        self.center_x = pos.x
        self.center_y = pos.y
        self.angle = 0.0
        self.change_angle = 0.0
        self.rate_factory = emit_controller
        self.particle_factory = particle_factory
        self._emit_done_cb = emit_done_cb
        self._reap_cb = reap_cb
        self._particles = arcade.SpriteList(use_spatial_hash=False)

    def _emit(self):
        """Emit one particle. A particle's position is treated relative to the position of the emitter"""
        p = self.particle_factory(self)
        p.center_x = self.center_x + p.center_x
        p.center_y = self.center_y + p.center_y
        vel = Vec2d(p.change_x, p.change_y).rotated_degrees(self.angle)
        p.change_x = vel.x
        p.change_y = vel.y
        self._particles.append(p)

    def get_count(self):
        return len(self._particles)

    def get_pos(self) -> Vec2d:
        """Get position of emitter as a Vec2d"""
        # TODO: should this be a property so a method call isn't needed?
        return Vec2d(self.center_x, self.center_y)

    def update(self):
        # update emitter
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.angle += self.change_angle

        # update particles
        emit_count = self.rate_factory.how_many(1 / 60, len(self._particles))
        for _ in range(emit_count):
            self._emit()
        self._particles.update()
        particles_to_reap = [p for p in self._particles if p.can_reap()]
        for dead_particle in particles_to_reap:
            dead_particle.kill()

    def draw(self):
        self._particles.draw()

    def can_reap(self):
        """Determine if Emitter can be deleted"""
        is_emit_complete = self.rate_factory.is_complete()
        can_reap = is_emit_complete and len(self._particles) <= 0
        if is_emit_complete and self._emit_done_cb:
            self._emit_done_cb(self)
            self._emit_done_cb = None
        if can_reap and self._reap_cb:
            self._reap_cb()
            self._reap_cb = None
        return can_reap
