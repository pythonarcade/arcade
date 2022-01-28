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
import os
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Particle System Examples"
QUIET_BETWEEN_SPAWNS = 0.25  # time between spawning another particle system
EMITTER_TIMEOUT = 10 * 60
CENTER_POS = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
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
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_0.__doc__, e


def emitter_1():
    """Burst, emit from center, particle lifetime 1.0 seconds"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=1.0,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_1.__doc__, e


def emitter_2():
    """Burst, emit from center, particle lifetime random in range"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=random.uniform(DEFAULT_PARTICLE_LIFETIME - 1.0, DEFAULT_PARTICLE_LIFETIME),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_2.__doc__, e


def emitter_3():
    """Burst, emit in circle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_in_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_3.__doc__, e


def emitter_4():
    """Burst, emit on circle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_on_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_4.__doc__, e


def emitter_5():
    """Burst, emit in rectangle"""
    width, height = 200, 100
    centering_offset = (-width / 2, -height / 2)
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_in_rect(centering_offset, width, height),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_5.__doc__, e


def emitter_6():
    """Burst, emit on line"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_on_line((0.0, 0.0), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_6.__doc__, e


def emitter_7():
    """Burst, emit from center, velocity fixed speed around 360 degrees"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_on_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_7.__doc__, e


def emitter_8():
    """Burst, emit from center, velocity in rectangle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_rect((-2.0, -2.0), 4.0, 4.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_8.__doc__, e


def emitter_9():
    """Burst, emit from center, velocity in fixed angle and random speed"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_vec_magnitude(45, 1.0, 4.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_9.__doc__, e


def emitter_10():
    """Burst, emit from center, velocity from angle with spread"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_vec_spread_deg(90, 45, 2.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_10.__doc__, e


def emitter_11():
    """Burst, emit from center, velocity along a line"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT // 4),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_on_line((-2, 1), (2, 1)),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_11.__doc__, e


def emitter_12():
    """Infinite emitting w/ eternal particle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitInterval(0.02),
        particle_factory=lambda emitter: arcade.EternalParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_12.__doc__, e


def emitter_13():
    """Interval, emit particle every 0.01 seconds for one second"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_13.__doc__, e


def emitter_14():
    """Interval, emit from center, particle lifetime 1.0 seconds"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=1.0,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_14.__doc__, e


def emitter_15():
    """Interval, emit from center, particle lifetime random in range"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=random.uniform(DEFAULT_PARTICLE_LIFETIME - 1.0, DEFAULT_PARTICLE_LIFETIME),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_15.__doc__, e


def emitter_16():
    """Interval, emit in circle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_in_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_16.__doc__, e


def emitter_17():
    """Interval, emit on circle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_on_circle((0.0, 0.0), 100),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_17.__doc__, e


def emitter_18():
    """Interval, emit in rectangle"""
    width, height = 200, 100
    centering_offset = (-width / 2, -height / 2)
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_in_rect(centering_offset, width, height),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_18.__doc__, e


def emitter_19():
    """Interval, emit on line"""
    e = arcade.Emitter(
        center_xy=(0.0, 0.0),
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_SLOW),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            center_xy=arcade.rand_on_line((0.0, 0.0), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_19.__doc__, e


def emitter_20():
    """Interval, emit from center, velocity fixed speed around 360 degrees"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_on_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_20.__doc__, e


def emitter_21():
    """Interval, emit from center, velocity in rectangle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_rect((-2.0, -2.0), 4.0, 4.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_21.__doc__, e


def emitter_22():
    """Interval, emit from center, velocity in fixed angle and speed"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(0.2, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
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
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL * 8, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_vec_magnitude(45, 1.0, 4.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_23.__doc__, e


def emitter_24():
    """Interval, emit from center, velocity from angle with spread"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_vec_spread_deg(90, 45, 2.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_24.__doc__, e


def emitter_25():
    """Interval, emit from center, velocity along a line"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_on_line((-2, 1), (2, 1)),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_25.__doc__, e


def emitter_26():
    """Interval, emit particles every 0.4 seconds and stop after emitting 5"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithCount(0.4, 5),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=0.6,
            alpha=128
        )
    )
    return emitter_26.__doc__, e


def emitter_27():
    """Maintain a steady count of particles"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitMaintainCount(3),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_on_circle((0.0, 0.0), 2.0),
            lifetime=random.uniform(1.0, 3.0),
        )
    )
    return emitter_27.__doc__, e


def emitter_28():
    """random particle textures"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL * 5, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=random.choice((TEXTURE, TEXTURE2, TEXTURE3)),
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_28.__doc__, e


def emitter_29():
    """random particle scale"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL * 5, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=random.uniform(0.1, 0.8),
            alpha=DEFAULT_ALPHA
        )
    )
    return emitter_29.__doc__, e


def emitter_30():
    """random particle alpha"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL * 5, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=int(random.uniform(32, 128))
        )
    )
    return emitter_30.__doc__, e


def emitter_31():
    """Constant particle angle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL * 5, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE2,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            angle=45,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_31.__doc__, e


def emitter_32():
    """animate particle angle"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL * 5, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE2,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            change_angle=2,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_32.__doc__, e


def emitter_33():
    """Particles that fade over time"""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_33.__doc__, e


def emitter_34():
    """Dynamically generated textures, burst emitting, fading particles"""
    textures = [arcade.make_soft_circle_texture(48, p) for p in (arcade.color.GREEN, arcade.color.BLUE_GREEN)]
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitBurst(BURST_PARTICLE_COUNT),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=random.choice(textures),
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE
        )
    )
    return emitter_34.__doc__, e


def emitter_35():
    """Use most features"""
    soft_circle = arcade.make_soft_circle_texture(80, (255, 64, 64))
    textures = (TEXTURE, TEXTURE2, TEXTURE3, TEXTURE4, TEXTURE5, TEXTURE6, TEXTURE7, soft_circle)
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(0.01, 1.0),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=random.choice(textures),
            change_xy=arcade.rand_in_circle((0.0, 0.0), PARTICLE_SPEED_FAST * 2),
            lifetime=random.uniform(1.0, 3.5),
            angle=random.uniform(0, 360),
            change_angle=random.uniform(-3, 3),
            scale=random.uniform(0.1, 0.8)
        )
    )
    return emitter_35.__doc__, e


def emitter_36():
    """Moving emitter. Particles spawn relative to emitter."""

    class MovingEmitter(arcade.Emitter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.elapsed = 0.0

        def update(self):
            super().update()
            self.elapsed += 1 / 60
            self.center_x = sine_wave(self.elapsed, 0, SCREEN_WIDTH, SCREEN_WIDTH / 100)
            self.center_y = sine_wave(self.elapsed, 0, SCREEN_HEIGHT, SCREEN_HEIGHT / 100)

    e = MovingEmitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitInterval(0.005),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), 0.1),
            lifetime=random.uniform(1.5, 5.5),
            scale=random.uniform(0.05, 0.2)
        )
    )
    return emitter_36.__doc__, e


def emitter_37():
    """Rotating emitter. Particles initial velocity is relative to emitter's angle."""
    e = arcade.Emitter(
        center_xy=CENTER_POS,
        emit_controller=arcade.EmitterIntervalWithTime(DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
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
    e = arcade.make_burst_emitter(
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
    e = arcade.make_interval_emitter(
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


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.BLACK)

        # collect particle factory functions
        self.factories = [v for k, v in globals().items() if k.startswith("emitter_")]

        self.emitter_factory_id = -1
        self.label = None
        self.emitter = None
        self.emitter_timeout = 0
        self.obj = arcade.Sprite(":resources:images/pinball/bumper.png", 0.2, center_x=0, center_y=15)
        self.obj.change_x = 3
        pyglet.clock.schedule_once(self.next_emitter, QUIET_BETWEEN_SPAWNS)

    def next_emitter(self, _time_delta):
        self.emitter_factory_id = (self.emitter_factory_id + 1) % len(self.factories)
        print("Changing emitter to {}".format(self.emitter_factory_id))
        self.emitter_timeout = 0
        self.label, self.emitter = self.factories[self.emitter_factory_id]()

    def update(self, delta_time):
        if self.emitter:
            self.emitter_timeout += 1
            self.emitter.update()
            if self.emitter.can_reap() or self.emitter_timeout > EMITTER_TIMEOUT:
                pyglet.clock.schedule_once(self.next_emitter, QUIET_BETWEEN_SPAWNS)
                self.emitter = None
        self.obj.update()
        if self.obj.center_x > SCREEN_WIDTH:
            self.obj.center_x = 0

    def on_draw(self):
        self.clear()
        self.obj.draw()
        if self.label:
            arcade.draw_text("#{} {}".format(self.emitter_factory_id, self.label),
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20,
                             arcade.color.PALE_GOLD, 20, width=SCREEN_WIDTH, align="center",
                             anchor_x="center", anchor_y="center")
        if self.emitter:
            self.emitter.draw()
            arcade.draw_text("Particles: " + str(self.emitter.get_count()), 10, 30, arcade.color.PALE_GOLD, 12)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()


if __name__ == "__main__":
    game = MyGame()
    arcade.run()
