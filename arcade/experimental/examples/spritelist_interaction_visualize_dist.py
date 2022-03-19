"""
Shows how we can use shaders using existing spritelist data.

This examples renders a line between the player position
and nearby sprites when they are within a certain distance.
"""
import random
import arcade

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
NUM_COINS = 1000
INTERACTION_RADIUS = 250


class SpriteListInteraction(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "SpriteList Interaction")

        # Genreate some random coins
        self.coins = arcade.SpriteList()
        for _ in range(NUM_COINS):
            self.coins.append(
                arcade.Sprite(
                    ":resources:images/items/coinGold.png",
                    center_x=random.randint(0, WINDOW_WIDTH),
                    center_y=random.randint(0, WINDOW_HEIGHT),
                    scale=0.25,
                )
            )

        # Player
        self.player = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=0.5,            
        )

        # This program draws lines from the player/origin
        # to sprites that are within a certain distance.
        # The main action here happens in the geometry shader.
        # It creates lines when a sprite is within the maxDistance.
        self.program_visualize_dist = self.ctx.program(
            vertex_shader="""
            #version 330

            // Sprite positions from SpriteList
            in vec2 in_pos;

            // Output to geometry shader
            out vec2 v_position;

            void main() {
                // This shader just forwards info to geo shader
                v_position = in_pos;
            }
            """,
            geometry_shader="""
            #version 330

            // This is how we access Arcade's global projection matrix
            uniform Projection {
                uniform mat4 matrix;
            } proj;

            // The position we measure distance from
            uniform vec2 origin;
            // The maximum distance
            uniform float maxDistance;

            // These configure the geometry shader to process a points
            // and allows it to emit lines. It runs for every sprite
            // in the spritelist.
            layout (points) in;
            layout (line_strip, max_vertices = 2) out;

            // The position input from vertex shader.
            // It's an array because geo shader can take more than one input
            in vec2 v_position[];

            void main() {
                // ONLY emit a line between the sprite and origin when within the distance
                if (distance(v_position[0], origin) < maxDistance) {
                    // First line segment position (origin)
                    gl_Position = proj.matrix * vec4(origin, 0.0, 1.0);
                    EmitVertex();
                    // Second line segment position (sprite position)
                    gl_Position = proj.matrix * vec4(v_position[0], 0.0, 1.0);
                    EmitVertex();
                }
            }
            """,
            fragment_shader="""
            #version 330
            // The fragment shader just runs for every pixel of the line segment.

            // Reference to the pixel we are writing to in the framebuffer
            out vec4 fragColor;

            void main() {
                // All the pixels in the line should just be white
                fragColor = vec4(1.0, 1.0, 1.0, 1.0);
            }
            """
        )
        # Configure program with maximum distance
        self.program_visualize_dist["maxDistance"] = INTERACTION_RADIUS

    def on_draw(self):
        self.clear()
        self.coins.draw()
        # We already have a geometry instance in the spritelist we can
        # use to run our shader/gpu program. It only requires that we
        # use correctly named input name(s). in_pos in this example
        # what will automatically map in the position buffer to the vertex shader.
        self.coins.geometry.render(self.program_visualize_dist, vertices=len(self.coins))
        self.player.draw()

        # Visualize the interaction radius
        arcade.draw_circle_filled(self.player.center_x, self.player.center_y, INTERACTION_RADIUS, (255, 255, 255, 64))

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        # Move the sprite to mouse position
        self.player.position = x, y
        # Update the program with a new origin
        self.program_visualize_dist["origin"] = x, y


SpriteListInteraction().run()
