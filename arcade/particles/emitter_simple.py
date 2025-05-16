"""
Convenience functions that provide a much simpler interface to Emitters and Particles.

These trade away some flexibility in favor of simplicity to allow beginners
to start using particle systems.
"""

import random
from collections.abc import Sequence

from arcade.math import rand_in_circle, rand_on_circle
from arcade.types import PathOrTexture, Point

from .emitter import EmitBurst, Emitter, EmitterIntervalWithTime
from .particle import FadeParticle, LifetimeParticle


def make_burst_emitter(
    center_xy: Point,
    filenames_and_textures: Sequence[PathOrTexture],
    particle_count: int,
    particle_speed: float,
    particle_lifetime_min: float,
    particle_lifetime_max: float,
    particle_scale: float = 1.0,
    fade_particles: bool = True,
) -> Emitter:
    """Returns an emitter that emits all of its particles at once"""
    particle_factory: type[LifetimeParticle] = LifetimeParticle
    if fade_particles:
        particle_factory = FadeParticle
    return Emitter(
        center_xy=center_xy,
        emit_controller=EmitBurst(particle_count),
        particle_factory=lambda emitter: particle_factory(
            filename_or_texture=random.choice(filenames_and_textures),
            change_xy=rand_in_circle((0.0, 0.0), particle_speed),
            lifetime=random.uniform(particle_lifetime_min, particle_lifetime_max),
            scale=particle_scale,
        ),
    )


def make_interval_emitter(
    center_xy: Point,
    filenames_and_textures: Sequence[PathOrTexture],
    emit_interval: float,
    emit_duration: float,
    particle_speed: float,
    particle_lifetime_min: float,
    particle_lifetime_max: float,
    particle_scale: float = 1.0,
    fade_particles: bool = True,
) -> Emitter:
    """Returns an emitter that emits its particles at a constant rate for a given amount of time"""
    particle_factory: type[LifetimeParticle] = LifetimeParticle
    if fade_particles:
        particle_factory = FadeParticle
    return Emitter(
        center_xy=center_xy,
        emit_controller=EmitterIntervalWithTime(emit_interval, emit_duration),
        particle_factory=lambda emitter: particle_factory(
            filename_or_texture=random.choice(filenames_and_textures),
            change_xy=rand_on_circle((0.0, 0.0), particle_speed),
            lifetime=random.uniform(particle_lifetime_min, particle_lifetime_max),
            scale=particle_scale,
        ),
    )
