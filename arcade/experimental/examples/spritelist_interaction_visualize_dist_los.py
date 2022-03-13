"""
Shows how we can use shaders using existing spritelist data.

This examples renders a line between the player position
and nearby sprites when they are within a certain distance.

This builds on a previous example adding line of sight (LoS)
checks by using texture lookups. We our walls into a
texture and read the pixels in a line between the 
player and the target sprite to check if the path is
colliding with something.
"""
import random
import arcade
from arcade.gl import BufferDescription

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
NUM_SPRITES = 100


class SpriteListInteraction(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "SpriteList Interaction - LoS")

        # Player
        self.player = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=0.25,            
        )

        # Wall sprites we are checking collission against
        self.walls = arcade.SpriteList()
        for _ in range(NUM_SPRITES):
            self.walls.append(
                arcade.Sprite(
                    ":resources:images/tiles/boxCrate_double.png",
                    center_x=random.randint(0, WINDOW_WIDTH),
                    center_y=random.randint(0, WINDOW_HEIGHT),
                    scale=0.25,
                )
            )

        # Genreate some random coins.
        # We make sure they are not placed inside a wall.
        # We give each coin 4 chances to spawn at the right position.
        self.coins = arcade.SpriteList()
        count = 0
        for _ in range(NUM_SPRITES * 4):
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                center_x=random.randint(0, WINDOW_WIDTH),
                center_y=random.randint(0, WINDOW_HEIGHT),
                scale=0.25,
            )
            if arcade.check_for_collision_with_list(coin, self.walls):
                continue

            self.coins.append(coin)
            count += 1
            if count == NUM_SPRITES:
                break



        # This program draws lines from the player/origin
        # to sprites that are within a certain distance.
        # The main action here happens in the geometry shader.
        # It creates lines when a sprite is within the maxDistance.
        self.program_visualize_dist = self.ctx.program(
            vertex_shader="""
            #version 330

            // Sprite positions from SpriteList
            in vec2 in_position;

            // Output to geometry shader
            out vec2 v_position;

            void main() {
                // This shader just forwards info to geo shader
                v_position = in_position;
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
            // Sampler for reading wall data
            uniform sampler2D walls;

            // These configure the geometry shader to process a points
            // and allows it to emit lines. It runs for every sprite
            // in the spritelist.
            layout (points) in;
            layout (line_strip, max_vertices = 2) out;

            // The position input from vertex shader.
            // It's an array because geo shader can take more than one input
            in vec2 v_position[];

            // Helper function converting screen coordinates to texture coordinates.
            // Texture coordinates are normalized (0.0 -> 1.0) were 0,0 is in the
            vec2 screen2texcoord(vec2 pos) {
                return vec2(pos / textureSize(walls, 0).xy);
            }

            void main() {
                // ONLY emit a line between the sprite and origin when within the distance
                if (distance(v_position[0], origin) > maxDistance) return;

                // Read samples from the wall texture in a line looking for obstacles
                // We simply make a vector between the origina and the sprite location
                // and trace pixels in this path with a reasonable step.
                int steps = int(maxDistance / 2);
                vec2 dir = v_position[0] - origin;
                for (int i = 0; i < steps; i++) {
                    // Read pixels along the vector
                    vec2 pos = origin + dir * (float(i) / float(steps));
                    vec4 color = texture(walls, screen2texcoord(pos));
                    // If we find non-zero pixel data we have obstacles in our path!
                    if (color != vec4(0.0)) return;
                }

                // First line segment position (origin)
                gl_Position = proj.matrix * vec4(origin, 0.0, 1.0);
                EmitVertex();
                // Second line segment position (sprite position)
                gl_Position = proj.matrix * vec4(v_position[0], 0.0, 1.0);
                EmitVertex();
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
        self.program_visualize_dist["maxDistance"] = 300
        # Create a geometry instance with the spritelist's position buffer.
        # This configures the inputs for the vertex shader
        self.geometry = self.ctx.geometry(
            [BufferDescription(self.coins._sprite_pos_buf, "2f", ["in_position"])]
        )

        # Lookup texture/framebuffer for walls so we can trace pixels in the shader.
        # It contains a texture attachment with the same size as the window.
        # We draw only the walls into this one as a line of sight lookup
        self.walls_fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((WINDOW_WIDTH, WINDOW_HEIGHT))]
        )
        # Draw the walls into the framebuffer
        with self.walls_fbo.activate() as fbo:
            fbo.clear()
            self.walls.draw()

    def on_draw(self):
        self.clear()

        self.walls.draw()
        self.coins.draw()
        # Bind the wall texture to texture channel 0 so we can read it in the shader
        self.walls_fbo.color_attachments[0].use(0)
        # We can run our program with this geometry since
        # the inputs are compatible (it has an "in_position" configured)
        self.geometry.render(self.program_visualize_dist)
        self.player.draw()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        # Move the sprite to mouse position
        self.player.position = x, y
        # Update the program with a new origin
        self.program_visualize_dist["origin"] = x, y


SpriteListInteraction().run()
