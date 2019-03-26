"""
Particle Fireworks

Use a fireworks display to demonstrate "real-world" uses of Emitters and Particles

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_list_particle_fireworks
"""
import arcade
import os
import random
import pyglet
from pymunk import Vec2d

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Particle based fireworks"
LAUNCH_INTERVAL_MIN = 1.5
LAUNCH_INTERVAL_MAX = 2.5
TEXTURE = "images/pool_cue_ball.png"
RAINBOW_COLORS = (
    arcade.color.ELECTRIC_CRIMSON,
    arcade.color.FLUORESCENT_ORANGE,
    arcade.color.ELECTRIC_YELLOW,
    arcade.color.ELECTRIC_GREEN,
    arcade.color.ELECTRIC_CYAN,
    arcade.color.MEDIUM_ELECTRIC_BLUE,
    arcade.color.ELECTRIC_INDIGO,
    arcade.color.ELECTRIC_PURPLE,
)
SPARK_TEXTURES = [arcade.make_circle_texture(15, clr) for clr in RAINBOW_COLORS]
SPARK_PAIRS = [
    [SPARK_TEXTURES[0], SPARK_TEXTURES[3]],
    [SPARK_TEXTURES[1], SPARK_TEXTURES[5]],
    [SPARK_TEXTURES[7], SPARK_TEXTURES[2]],
]
ROCKET_SMOKE_TEXTURE = arcade.make_soft_circle_texture(15, arcade.color.GRAY)
PUFF_TEXTURE = arcade.make_soft_circle_texture(80, (40, 40, 40))
FLASH_TEXTURE = arcade.make_soft_circle_texture(70, (128, 128, 90))
CLOUD_TEXTURES = [
    arcade.make_soft_circle_texture(50, arcade.color.WHITE),
    arcade.make_soft_circle_texture(50, arcade.color.LIGHT_GRAY),
    arcade.make_soft_circle_texture(50, arcade.color.LIGHT_BLUE),
]
STAR_TEXTURES = [
    arcade.make_soft_circle_texture(6, arcade.color.WHITE),
    arcade.make_soft_circle_texture(6, arcade.color.PASTEL_YELLOW),
]
SPINNER_HEIGHT=75


def make_spinner():
    spinner = arcade.Emitter(
        pos=Vec2d(SCREEN_WIDTH / 2, SPINNER_HEIGHT - 5),
        emit_controller=arcade.EmitterIntervalWithTime(0.025, 2.0),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=random.choice(STAR_TEXTURES),
            vel=Vec2d(0, 6.0),
            lifetime=0.2
        )
    )
    spinner.change_angle = 16.28
    return spinner

def make_rocket(emit_done_cb):
    """Emitter that displays the smoke trail as the firework shell climbs into the sky"""
    rocket = RocketEmitter(
        pos=Vec2d(random.uniform(100, SCREEN_WIDTH - 100), 25),
        emit_controller=arcade.EmitterIntervalWithTime(0.04, 2.0),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=ROCKET_SMOKE_TEXTURE,
            vel=arcade.rand_in_circle(Vec2d.zero(), 0.08),
            scale=0.5,
            lifetime=random.uniform(1.0, 1.5),
            start_alpha=100,
            end_alpha=0,
            mutation_callback=rocket_smoke_mutator
        ),
        emit_done_cb=emit_done_cb
    )
    rocket.change_x = random.uniform(-1.0, 1.0)
    rocket.change_y = random.uniform(5.0, 7.25)
    return rocket

def make_flash(prev_emitter):
    """Return emitter that displays the brief flash when a firework shell explodes"""
    return arcade.Emitter(
        pos=prev_emitter.get_pos(),
        emit_controller=arcade.EmitBurst(3),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=FLASH_TEXTURE,
            vel=arcade.rand_in_circle(Vec2d.zero(), 3.5),
            lifetime=0.15
        )
    )

def make_puff(prev_emitter):
    """Return emitter that generates the subtle smoke cloud left after a firework shell explodes"""
    return arcade.Emitter(
        pos=prev_emitter.get_pos(),
        emit_controller=arcade.EmitBurst(4),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=PUFF_TEXTURE,
            vel=arcade.rand_in_circle(Vec2d.zero(), 0.4) + Vec2d(0.3, 0.0),
            lifetime=4.0
        )
    )


class AnimatedAlphaParticle(arcade.LifetimeParticle):
    """A custom particle that animates between three different alpha levels"""
    def __init__(
        self,
        filename_or_texture: str,
        vel: Vec2d,
        start_alpha: int = 0,
        duration1: float = 1.0,
        mid_alpha: int = 255,
        duration2: float = 1.0,
        end_alpha: int = 0,
        pos: Vec2d = None,
        angle: float = 0,
        change_angle: float = 0,
        scale: float = 1.0,
        mutation_callback=None,
    ):
        super().__init__(filename_or_texture, vel, duration1 + duration2, pos, angle, change_angle, scale, start_alpha, mutation_callback)
        self.start_alpha = start_alpha
        self.in_duration = duration1
        self.mid_alpha = mid_alpha
        self.out_duration = duration2
        self.end_alpha = end_alpha

    def update(self):
        super().update()
        if self.lifetime_elapsed <= self.in_duration:
            u = self.lifetime_elapsed / self.in_duration
            self.alpha = arcade.utils.lerp(self.start_alpha, self.mid_alpha, u)
        else:
            u = (self.lifetime_elapsed - self.in_duration) / self.out_duration
            self.alpha = arcade.utils.lerp(self.mid_alpha, self.end_alpha, u)


class RocketEmitter(arcade.Emitter):
    """Custom emitter class to add gravity to the emitter to represent gravity on the firework shell"""
    def update(self):
        super().update()
        # gravity
        self.change_y += -0.05


class FireworksApp(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.BLACK)
        self.emitters = []
        self.frametime_plotter = arcade.FrametimePlotter()

        self.launch_firework(0)
        arcade.schedule(self.launch_spinner, 4.0)

        stars = arcade.Emitter(
            pos=Vec2d.zero(),
            emit_controller=arcade.EmitMaintainCount(20),
            particle_factory=lambda emitter: AnimatedAlphaParticle(
                filename_or_texture=random.choice(STAR_TEXTURES),
                vel=Vec2d.zero(),
                start_alpha=0,
                duration1=random.uniform(2.0, 6.0),
                mid_alpha=128,
                duration2=random.uniform(2.0, 6.0),
                end_alpha=0,
                pos=arcade.rand_in_rect(Vec2d.zero(), SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        )
        self.emitters.append(stars)

        self.cloud = arcade.Emitter(
            pos=Vec2d(50, 500),
            vel=Vec2d(0.15, 0),
            emit_controller=arcade.EmitMaintainCount(60),
            particle_factory=lambda emitter: AnimatedAlphaParticle(
                filename_or_texture=random.choice(CLOUD_TEXTURES),
                vel=arcade.rand_in_circle(Vec2d.zero(), 0.04) + Vec2d(0.1, 0),
                start_alpha=0,
                duration1=random.uniform(5.0, 10.0),
                mid_alpha=255,
                duration2=random.uniform(5.0, 10.0),
                end_alpha=0,
                pos=arcade.rand_in_circle(Vec2d.zero(), 50)
            )
        )
        self.emitters.append(self.cloud)

    def launch_firework(self, delta_time):
        self.frametime_plotter.add_event("launch")
        launchers = (
            self.launch_random_firework,
            self.launch_ringed_firework,
            self.launch_sparkle_firework,
        )
        random.choice(launchers)(delta_time)
        pyglet.clock.schedule_once(self.launch_firework, random.uniform(LAUNCH_INTERVAL_MIN, LAUNCH_INTERVAL_MAX))

    def launch_random_firework(self, delta_time):
        """Simple firework that explodes in a random color"""
        rocket = make_rocket(self.explode_firework)
        self.emitters.append(rocket)

    def launch_ringed_firework(self, delta_time):
        """"Firework that has a basic explosion and a ring of sparks of a different color"""
        rocket = make_rocket(self.explode_ringed_firework)
        self.emitters.append(rocket)

    def launch_sparkle_firework(self, delta_time):
        """Firework which has sparks that sparkle"""
        rocket = make_rocket(self.explode_sparkle_firework)
        self.emitters.append(rocket)

    def launch_spinner(self, delta_time):
        """Start the spinner that throws sparks"""
        spinner1 = make_spinner()
        spinner2 = make_spinner()
        spinner2.angle = 180
        self.emitters.append(spinner1)
        self.emitters.append(spinner2)

    def explode_firework(self, prev_emitter):
        """Actions that happen when a firework shell explodes, resulting in a typical firework"""
        self.emitters.append(make_puff(prev_emitter))
        self.emitters.append(make_flash(prev_emitter))

        spark_texture = random.choice(SPARK_TEXTURES)
        sparks = arcade.Emitter(
            pos=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(random.randint(30, 40)),
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=spark_texture,
                vel=arcade.rand_in_circle(Vec2d.zero(), 9.0),
                lifetime=random.uniform(0.5, 1.2),
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(sparks)

    def explode_ringed_firework(self, prev_emitter):
        """Actions that happen when a firework shell explodes, resulting in a ringed firework"""
        self.emitters.append(make_puff(prev_emitter))
        self.emitters.append(make_flash(prev_emitter))

        spark_texture, ring_texture = random.choice(SPARK_PAIRS)
        sparks = arcade.Emitter(
            pos=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(25),
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=spark_texture,
                vel=arcade.rand_in_circle(Vec2d.zero(), 8.0),
                lifetime=random.uniform(0.55, 0.8),
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(sparks)

        ring = arcade.Emitter(
            pos=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(20),
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=ring_texture,
                vel=arcade.rand_on_circle(Vec2d.zero(), 5.0) + arcade.rand_in_circle(Vec2d.zero(), 0.25),
                lifetime=random.uniform(1.0, 1.6),
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(ring)

    def explode_sparkle_firework(self, prev_emitter):
        """Actions that happen when a firework shell explodes, resulting in a sparkling firework"""
        self.emitters.append(make_puff(prev_emitter))
        self.emitters.append(make_flash(prev_emitter))

        spark_texture = random.choice(SPARK_TEXTURES)
        sparks = arcade.Emitter(
            pos=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(random.randint(30, 40)),
            particle_factory=lambda emitter: AnimatedAlphaParticle(
                filename_or_texture=spark_texture,
                vel=arcade.rand_in_circle(Vec2d.zero(), 9.0),
                start_alpha=255,
                duration1=random.uniform(0.6, 1.0),
                mid_alpha=0,
                duration2=random.uniform(0.1, 0.2),
                end_alpha=255,
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(sparks)

    def update(self, delta_time):
        # prevent list from being mutated (often by callbacks) while iterating over it
        emitters_to_update = self.emitters.copy()
        # update cloud
        if self.cloud.center_x > SCREEN_WIDTH:
            self.cloud.center_x = 0
        # update
        for e in emitters_to_update:
            e.update()
        # remove emitters that can be reaped
        to_del = [e for e in emitters_to_update if e.can_reap()]
        for e in to_del:
            self.emitters.remove(e)
        self.frametime_plotter.end_frame(delta_time)

    def on_draw(self):
        arcade.start_render()
        for e in self.emitters:
            e.draw()
        arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, 25, 0, arcade.color.DARK_GREEN)
        mid = SCREEN_WIDTH / 2
        arcade.draw_lrtb_rectangle_filled(mid-2, mid+2, SPINNER_HEIGHT, 10, arcade.color.DARK_BROWN)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()


def firework_spark_mutator(emitter: arcade.Emitter):
    """mutation_callback shared by all fireworks sparks"""
    # gravity
    emitter.change_y += -0.03
    # drag
    emitter.change_x *= 0.92
    emitter.change_y *= 0.92

def rocket_smoke_mutator(emitter: arcade.Emitter):
    emitter.scale = arcade.lerp(0.5, 3.0, emitter.lifetime_elapsed/emitter.lifetime_original)
    # A Sprite's scale doesn't affect generated textures (ex: make_soft_circle_texture) or scale being animated over time.
    # The fix below is copied from Sprite.update_animation().
    # Bug may have been recorded here: https://github.com/pvcraven/arcade/issues/331
    emitter.width = emitter._texture.width * emitter.scale
    emitter.height = emitter._texture.height * emitter.scale


if __name__ == "__main__":
    app = FireworksApp()
    arcade.run()
    app.frametime_plotter.show()
