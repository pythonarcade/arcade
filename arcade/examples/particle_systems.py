"""
Particle Systems

Demonstrate how to use the Emitter and Particle classes to create particle systems.

Demonstrate the different effects possible with Emitter's and Particle's by showing
a number of different emitters in sequence, with each example often varying just one
setting from the previous example.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.particle_systems
"""
import arcade
import pyglet
import random
import math
from arcade.math import (
    rand_in_circle,
    rand_on_circle,
    rand_in_rect,
    rand_on_line,
    rand_vec_magnitude,
    rand_vec_spread_deg,
)
from arcade import particles, LBWH

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Particle System Examples"
QUIET_BETWEEN_SPAWNS = 0.25  # time between spawning another particle system
EMITTER_TIMEOUT = 10 * 60
CENTER_POS = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
BURST_PARTICLE_COUNT = 500
TEXTURE = ":resources:images/pinball/pool_cue_ball.png"
TEXTURE2 = ":resources:images/space_shooter/playerShip3_orange.png"
TEXTURE3 = ":resources:images/pinball/bumper.png"
TEXTURE4 = ":resources:images/enemies/wormGreen.png"
TEXTURE5 = ":resources:images/space_shooter/meteorGrey_med1.png"
TEXTURE6 = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
TEXTURE7 = ":resources:images/tiles/boxCrate_double.png"
DEFAULT_SCALE = 0.3
DEFAULT_ALPHA = 32
DEFAULT_PARTICLE_LIFETIME = 3.0
PARTICLE_SPEED_FAST = 1.0
PARTICLE_SPEED_SLOW = 0.3
DEFAULT_EMIT_INTERVAL = 0.003
DEFAULT_EMIT_DURATION = 1.5


# Utils
def sine_wave(t, min_x, max_x, wavelength):
    spread = max_x - min_x
    mid = (max_x + min_x) / 2
    return (spread / 2) * math.sin(2 * math.pi * t / wavelength) + mid


# Example emitters
def emitter_0():
    """Burst, emit from center, particle with lifetime"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_0.__doc__, e


def emitter_1():
    """Burst, emit from center, particle lifetime 1.0 seconds"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=1.0,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_1.__doc__, e


def emitter_2():
    """Burst, emit from center, particle lifetime random in range"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=random.uniform(DEFAULT_PARTICLE_LIFETIME - 1.0, DEFAULT_PARTICLE_LIFETIME),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_2.__doc__, e


def emitter_3():
    """Burst, emit in circle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_in_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_3.__doc__, e


def emitter_4():
    """Burst, emit on circle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_on_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_4.__doc__, e


def emitter_5():
    """Burst, emit in rectangle"""
    width, height = 200, 100
    centering_offset = (-width / 2, -height / 2)
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_in_rect(LBWH(*centering_offset, width, height)),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_5.__doc__, e


def emitter_6():
    """Burst, emit on line"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_on_line((0.0, 0.0), (WINDOW_WIDTH, WINDOW_HEIGHT)),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_6.__doc__, e


def emitter_7():
    """Burst, emit from center, velocity fixed speed around 360 degrees"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_on_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_7.__doc__, e


def emitter_8():
    """Burst, emit from center, velocity in rectangle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_rect(LBWH(-2.0, -2.0, 4.0, 4.0)),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_8.__doc__, e


def emitter_9():
    """Burst, emit from center, velocity in fixed angle and random speed"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_vec_magnitude(45, 1.0, 4.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_9.__doc__, e


def emitter_10():
    """Burst, emit from center, velocity from angle with spread"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_vec_spread_deg(90, 45, 2.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_10.__doc__, e


def emitter_11():
    """Burst, emit from center, velocity along a line"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_on_line((-2, 1), (2, 1)),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_11.__doc__, e


def emitter_12():
    """Infinite emitting w/ eternal particle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitInterval(0.02),
        particle_factory=lambda emitter: particles.EternalParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_12.__doc__, e


def emitter_13():
    """Interval, emit particle every 0.01 seconds for one second"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_13.__doc__, e


def emitter_14():
    """Interval, emit from center, particle lifetime 1.0 seconds"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=1.0,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_14.__doc__, e


def emitter_15():
    """Interval, emit from center, particle lifetime random in range"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=random.uniform(DEFAULT_PARTICLE_LIFETIME - 1.0, DEFAULT_PARTICLE_LIFETIME),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_15.__doc__, e


def emitter_16():
    """Interval, emit in circle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_in_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_16.__doc__, e


def emitter_17():
    """Interval, emit on circle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_on_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_17.__doc__, e


def emitter_18():
    """Interval, emit in rectangle"""
    width, height = 200, 100
    centering_offset = (-width / 2, -height / 2)
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_in_rect(LBWH(*centering_offset, width, height)),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_18.__doc__, e


def emitter_19():
    """Interval, emit on line"""
    e = particles.Emitter(
        center_xy=(0.0, 0.0),
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=rand_on_line((0.0, 0.0), (WINDOW_WIDTH, WINDOW_HEIGHT)),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA,
        )
    )
    return emitter_19.__doc__, e


def emitter_20():
    """Interval, emit from center, velocity fixed speed around 360 degrees"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_on_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA,
        )
    )
    return emitter_20.__doc__, e


def emitter_21():
    """Interval, emit from center, velocity in rectangle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_rect(LBWH(-2.0, -2.0, 4.0, 4.0)),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_21.__doc__, e


def emitter_22():
    """Interval, emit from center, velocity in fixed angle and speed"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(0.2, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=(1.0, 1.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=128
        )
    )
    return emitter_22.__doc__, e


def emitter_23():
    """Interval, emit from center, velocity in fixed angle and random speed"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL * 8,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_vec_magnitude(45, 1.0, 4.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_23.__doc__, e


def emitter_24():
    """Interval, emit from center, velocity from angle with spread"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_vec_spread_deg(90, 45, 2.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_24.__doc__, e


def emitter_25():
    """Interval, emit from center, velocity along a line"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_on_line((-2, 1), (2, 1)),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_25.__doc__, e


def emitter_26():
    """Interval, emit particles every 0.4 seconds and stop after emitting 5"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithCount(0.4, 5),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=0.6,
            alpha=128
        )
    )
    return emitter_26.__doc__, e


def emitter_27():
    """Maintain a steady count of particles"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitMaintainCount(3),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_on_circle((0.0, 0.0), 2.0),
            lifetime=random.uniform(1.0, 3.0),
        )
    )
    return emitter_27.__doc__, e


def emitter_28():
    """random particle textures"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL * 5,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=random.choice((TEXTURE, TEXTURE2, TEXTURE3)),
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_28.__doc__, e


def emitter_29():
    """random particle scale"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL * 5,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=random.uniform(0.1, 0.8),
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_29.__doc__, e


def emitter_30():
    """random particle alpha"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL * 5,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=int(random.uniform(32, 128))
        )
    )
    return emitter_30.__doc__, e


def emitter_31():
    """Constant particle angle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL * 5,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE2,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            angle=45,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_31.__doc__, e


def emitter_32():
    """animate particle angle"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL * 5,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE2,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            change_angle=2,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_32.__doc__, e


def emitter_33():
    """Particles that fade over time"""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.FadeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_33.__doc__, e


def emitter_34():
    """Dynamically generated textures, burst emitting, fading particles"""
    textures = [
        arcade.make_soft_circle_texture(48, p)
        for p in (arcade.color.GREEN, arcade.color.BLUE_GREEN)
    ]
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: particles.FadeParticle(
            filename_or_texture=random.choice(textures),
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_34.__doc__, e


def emitter_35():
    """Use most features"""
    soft_circle = arcade.make_soft_circle_texture(80, (255, 64, 64))
    textures = (
        TEXTURE,
        TEXTURE2,
        TEXTURE3,
        TEXTURE4,
        TEXTURE5,
        TEXTURE6,
        TEXTURE7,
        soft_circle,
    )
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(0.01, 1.0),
        particle_factory=lambda emitter: particles.FadeParticle(
            filename_or_texture=random.choice(textures),
            change_xy=rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST * 2),
            lifetime=random.uniform(1.0, 3.5),
            angle=random.uniform(0, 360),
            change_angle=random.uniform(-3, 3),
            scale=random.uniform(0.1, 0.8)
        )
    )
    return emitter_35.__doc__, e


def emitter_36():
    """Moving emitter. Particles spawn relative to emitter."""

    class MovingEmitter(particles.Emitter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.elapsed = 0.0

        def update(self, delta_time: float = 1 / 60):
            super().update(delta_time)
            self.elapsed += delta_time
            self.center_x = sine_wave(self.elapsed, 0, WINDOW_WIDTH, WINDOW_WIDTH / 100)
            self.center_y = sine_wave(self.elapsed, 0, WINDOW_HEIGHT, WINDOW_HEIGHT / 100)

    e = MovingEmitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitInterval(0.005),
        particle_factory=lambda emitter: particles.FadeParticle(
            filename_or_texture=TEXTURE,
            change_xy=rand_in_circle((0.0, 0.0), 0.1),
            lifetime=random.uniform(1.5, 5.5),
            scale=random.uniform(0.05, 0.2)
        )
    )
    return emitter_36.__doc__, e


def emitter_37():
    """Rotating emitter. Particles initial velocity is relative to emitter's angle."""
    e = particles.Emitter(
        center_xy=CENTER_POS,
        emit_controller=particles.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL,
            DEFAULT_EMIT_DURATION,
        ),
        particle_factory=lambda emitter: particles.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=(0.0, 2.0),
            lifetime=2.0,
            scale=DEFAULT_SCALE
        )
    )
    e.change_angle = 10.0
    return emitter_37.__doc__, e


def emitter_38():
    """Use simple emitter interface to create a burst emitter"""
    e = particles.make_burst_emitter(
        center_xy=CENTER_POS,
        filenames_and_textures=(TEXTURE, TEXTURE3, TEXTURE4),
        particle_count=50,
        particle_speed=2.5,
        particle_lifetime_min=1.0,
        particle_lifetime_max=2.5,
        particle_scale=0.3,
        fade_particles=True
    )
    return emitter_38.__doc__, e


def emitter_39():
    """Use simple emitter interface to create an interval emitter"""
    e = particles.make_interval_emitter(
        center_xy=CENTER_POS,
        filenames_and_textures=(TEXTURE, TEXTURE3, TEXTURE4),
        emit_interval=0.01,
        emit_duration=2.0,
        particle_speed=1.5,
        particle_lifetime_min=1.0,
        particle_lifetime_max=3.0,
        particle_scale=0.2,
        fade_particles=True
    )
    return emitter_39.__doc__, e


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK

        # collect particle factory functions
        self.factories = [v for k, v in globals().items() if k.startswith("emitter_")]

        self.emitter_factory_id = -1
        self.label = None
        self.emitter = None
        self.emitter_timeout = 0
        self.obj = arcade.Sprite(
            ":resources:images/pinball/bumper.png",
            scale=0.2,
            center_x=0,
            center_y=15,
        )
        self.obj.change_x = 3
        pyglet.clock.schedule_once(self.next_emitter, QUIET_BETWEEN_SPAWNS)

    def next_emitter(self, _time_delta):
        self.emitter_factory_id = (self.emitter_factory_id + 1) % len(self.factories)
        print(f"Changing emitter to {self.emitter_factory_id}")
        self.emitter_timeout = 0
        self.label, self.emitter = self.factories[self.emitter_factory_id]()

    def on_update(self, delta_time):
        if self.emitter:
            self.emitter_timeout += 1
            self.emitter.update(delta_time)
            if self.emitter.can_reap() or self.emitter_timeout > EMITTER_TIMEOUT:
                pyglet.clock.schedule_once(self.next_emitter, QUIET_BETWEEN_SPAWNS)
                self.emitter = None
        self.obj.update(delta_time)
        if self.obj.center_x > WINDOW_WIDTH:
            self.obj.center_x = 0

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.obj)
        if self.label:
            arcade.draw_text(f"#{self.emitter_factory_id} {self.label}",
                             WINDOW_WIDTH / 2, WINDOW_HEIGHT - 25,
                             arcade.color.PALE_GOLD, 20, width=WINDOW_WIDTH,
                             anchor_x="center")
        if self.emitter:
            self.emitter.draw()
            arcade.draw_text(
                "Particles: " + str(self.emitter.get_count()),
                x=10,
                y=30,
                color=arcade.color.PALE_GOLD,
                font_size=12,
            )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
