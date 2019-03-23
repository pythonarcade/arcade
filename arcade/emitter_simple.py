"""
Convenience functions that provide a much simpler interface to Emitters and Particles.

These trade away some flexibility in favor of simplicity to allow beginners to start using particle systems.
"""

import arcade
import random
from typing import List
from pymunk import Vec2d

def make_burst_emitter(
        pos: Vec2d,
        filenames_and_textures: List[str],  # Also supports Texture objects in the List
        particle_count: int,
        particle_speed: float,
        particle_lifetime_min: float,
        particle_lifetime_max: float,
        particle_scale: float = 1.0,
        fade_particles: bool = True
    ):
    """Returns an emitter that emits all of its particles at once"""
    particle_factory = arcade.LifetimeParticle
    if fade_particles:
        particle_factory = arcade.FadeParticle
    return arcade.Emitter(
        pos=pos,
        emit_controller=arcade.EmitBurst(particle_count),
        particle_factory=lambda emitter: particle_factory(
            filename_or_texture=random.choice(filenames_and_textures),
            vel=arcade.rand_in_circle(Vec2d.zero(), particle_speed),
            lifetime=random.uniform(particle_lifetime_min, particle_lifetime_max),
            scale=particle_scale
        )
    )

def make_interval_emitter(
        pos: Vec2d,
        filenames_and_textures: List[str], # Also supports Texture objects in the List
        emit_interval: float,
        emit_duration: float,
        particle_speed: float,
        particle_lifetime_min: float,
        particle_lifetime_max: float,
        particle_scale: float = 1.0,
        fade_particles: bool = True
    ):
    """Returns an emitter that emits its particles at a constant rate for a given amount of time"""
    particle_factory = arcade.LifetimeParticle
    if fade_particles:
        particle_factory = arcade.FadeParticle
    return arcade.Emitter(
        pos=pos,
        emit_controller=arcade.EmitterIntervalWithTime(emit_interval, emit_duration),
        particle_factory=lambda emitter: particle_factory(
            filename_or_texture=random.choice(filenames_and_textures),
            vel=arcade.rand_on_circle(Vec2d.zero(), particle_speed),
            lifetime=random.uniform(particle_lifetime_min, particle_lifetime_max),
            scale=particle_scale
        )
    )