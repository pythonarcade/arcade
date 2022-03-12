"""
An example drawing a huge map to offscreen
then view that map form different actor viewpoints.

This example is using the lower level rendering API
in arcade.
"""
import random
from typing import Tuple

import arcade
from arcade.gl import geometry


class ActorMap(arcade.Window):

    def __init__(self):
        super().__init__(512, 512, "Actor Map")
        self.shaders = Shaders(self.ctx)
        self.map = Map(self.ctx, size=(4096, 4096))
        self.map.draw()
        self.actor = Actor(self.map, self.shaders)
        self.time = 0

    def on_draw(self):
        self.clear()
        self.ctx.projection_2d = 0, self.width, 0, self.height
        self.actor.draw(self.time)

    def on_update(self, delta_time: float):
        self.time += delta_time


class Actor:
    """
    An actor located somewhere in the map.
    We can render this actor's view to the screen.
    It should support translation and rotations
    and possibly zoom.
    """
    def __init__(
        self,
        map,
        shaders,
        *,
        position: Tuple[float, float] = (0, 0),
        rotation: float = 0.0,
        area: Tuple[float, float] = (256, 256),
        view_distance: float = 120.0,
    ):
        self.ctx = map.ctx
        self.map = map
        self.shaders = shaders
        self._position = position
        self._rotation = rotation
        self._area = area
        self._view_distance = view_distance
        # Geometry for drawing the actor view
        self.geometry = geometry.quad_2d_fs()

    @property
    def position(self) -> Tuple[float, float]:
        """Get or set the position"""
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def rotation(self) -> float:
        """Get or set the rotation"""
        return self._rotation

    @rotation.setter
    def rotation(self, value: float):
        self._rotation = value

    def draw(self, time: float):
        self.map.texture.use()
        program = self.shaders.actor_view
        program["mapSize"] = self.map.size
        program["area"] = self._area
        program["pos"] = time / 10, time / 10
        program["rot"] = time * 10
        self.geometry.render(self.shaders.actor_view)


class Map:
    """
    Sprites for out map to keep things less messy
    """

    def __init__(self, ctx, *, size: Tuple[int, int]):
        self.ctx = ctx
        self.size = size

        # Create a framebuffer for the map.
        # This is an RGBA texture wrapped in a framebuffer
        # so we can draw into it
        self.fbo = self.ctx.framebuffer(
            color_attachments=[
                self.ctx.texture(
                    (self.size),
                    components=4,
                    wrap_x=self.ctx.CLAMP_TO_EDGE,
                    wrap_y=self.ctx.CLAMP_TO_EDGE,
                ),
            ]
        )

        # Let's make some sprites for the map itself
        self.sprites = arcade.SpriteList()
        # Some random 128x128 tile images
        texture_paths = [
            ":resources:images/tiles/boxCrate_double.png",
            ":resources:images/tiles/boxCrate_single.png",
            ":resources:images/tiles/boxCrate.png",
            ":resources:images/tiles/brickBrown.png",
            ":resources:images/tiles/brickGrey.png",
            ":resources:images/tiles/brickTextureWhite.png",
            ":resources:images/tiles/dirt.png",
            ":resources:images/tiles/dirtCenter_rounded.png",
            ":resources:images/tiles/dirtCenter.png",
        ]

        tex_size = 128
        step_x = self.size[1] // tex_size * 4
        step_y = self.size[0] // tex_size * 4

        # Generate random sprites covering the entire map
        for y in range(step_y):
            for x in range(step_x):
                self.sprites.append(
                    arcade.Sprite(
                        random.choice(texture_paths),
                        center_x=16 + x * 32,
                        center_y=16 + y * 32,
                        scale=0.25,
                    )
                )

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def texture(self):
        """The OpenGL texture containing the map pixel data"""
        return self.fbo.color_attachments[0]

    def draw(self):
        """Draw the map contents"""

        with self.fbo.activate() as fbo:
            fbo.clear()
            # Change projection to match the contents
            self.ctx.projection_2d = 0, self.width, 0, self.height
            self.sprites.draw()


class Shaders:
    """
    Quick and dirty contains for all the shaders we're using.
    We don't want to compile a program/shader multiple times.
    """
    def __init__(self, ctx):
        self.ctx = ctx
        self.actor_view = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform vec2 mapSize;
            uniform vec2 pos;
            uniform vec2 area;
            uniform float rot;

            in vec2 in_vert;
            in vec2 in_uv;
            out vec3 uv;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);

                mat3 trans = mat3(
                    1.0, 0.0, 0.0,
                    0.0, 1.0, 0.0,
                    pos.x, pos.y, 1.0
                );
                float s = 1.0 / mapSize.x * area.x;
                mat3 scale = mat3(
                    s, 0.0, 0.0,
                    0.0, s, 0.0,
                    0.0, 0.0, s
                );
                float angle = radians(rot);
                mat3 rot = mat3(
                    cos(angle), -sin(angle), 0.0,
                    sin(angle),  cos(angle), 0.0,
                    0.0, 0.0, 1.0
                );

                uv = trans * rot * scale * vec3(in_uv - vec2(0.5), 1.0) + vec3(0.5);
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D map;
            in vec3 uv;
            out vec4 fragColor;

            void main() {
                fragColor = texture(map, uv.xy);
            }
            """,
        )


ActorMap().run()
