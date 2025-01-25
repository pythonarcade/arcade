"""
Shows how we can use shaders using existing spritelist data.

This example builds on previous examples visualizing selection
of nearby sprites taking line of sight into consideration.

This version on the other hand does not visualize. We want
return useful data from the shader to resolve the actual
selected sprite objects so we can use it in our game logic.

For this to happen we need to change our shader into a
transform shader. These shaders do not draw to the screen.
They write data into a buffer we can read back on the
python side. This simply involves removing the fragment
shader and instead defining some values to output.
We also need to do a transform() instead of render()
and supply a buffer for our results. In addition we
use a Query to count how many results the shader gave us.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.spritelist_interaction_visualize_dist_los_trans
"""

import random
import struct
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
NUM_COINS = 500
NUM_WALLS = 100
INTERACTION_RADIUS = 200


class SpriteListInteraction(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "SpriteList Interaction - LoS")

        # Player
        self.player = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=0.25,
        )

        # Wall sprites we are checking collision against
        self.walls = arcade.SpriteList()
        for _ in range(NUM_WALLS):
            self.walls.append(
                arcade.Sprite(
                    ":resources:images/tiles/boxCrate_double.png",
                    center_x=random.randint(0, WINDOW_WIDTH),
                    center_y=random.randint(0, WINDOW_HEIGHT),
                    scale=0.25,
                )
            )

        # Generate some random coins.
        # We make sure they are not placed inside a wall.
        # We give each coin 1 chance to spawn at the right position.
        self.coins = arcade.SpriteList()
        for _ in range(NUM_COINS):
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                center_x=random.randint(0, WINDOW_WIDTH),
                center_y=random.randint(0, WINDOW_HEIGHT),
                scale=0.25,
            )
            if arcade.check_for_collision_with_list(coin, self.walls):
                continue

            self.coins.append(coin)

        # This program finds sprites within a certain distance
        # not blocked by line of sight. We use a texture containing
        # the walls to trace a ray between the player and coin.
        # If any non-zero pixels are detected we skip the sprite.
        self.program_select_sprites = self.ctx.program(
            vertex_shader="""
            #version 330

            // Sprite positions from SpriteList
            in vec3 in_pos;

            // Output to geometry shader
            out vec3 v_position;

            void main() {
                // This shader just forwards info to geo shader
                v_position = in_pos;
            }
            """,
            geometry_shader="""
            #version 330

            // The position we measure distance from
            uniform vec2 origin;
            // The maximum distance
            uniform float maxDistance;
            // Sampler for reading wall data
            uniform sampler2D walls;

            // These configure the geometry shader to process a points
            // and also emit single points of data
            // in the spritelist.
            layout (points) in;
            layout (points, max_vertices = 1) out;

            // The position input from vertex shader.
            // It's an array because geo shader can take more than one input
            in vec3 v_position[];
            // This shader outputs all the sprite indices it selected.
            // NOTE: We use floats here for compatibility since integers are always working
            out float spriteIndex;

            // Helper function converting screen coordinates to texture coordinates.
            // Texture coordinates are normalized (0.0 -> 1.0) were 0,0 is in the
            vec2 screen2texcoord(vec2 pos) {
                return vec2(pos / vec2(textureSize(walls, 0).xy));
            }

            void main() {
                // ONLY emit a line between the sprite and origin when within the distance
                if (distance(v_position[0].xy, origin) > maxDistance) return;

                // Read samples from the wall texture in a line looking for obstacles
                // We simply make a vector between the original and the sprite location
                // and trace pixels in this path with a reasonable step.
                int numSteps = int(maxDistance / 2.0);
                vec2 dir = v_position[0].xy - origin;
                for (int i = 0; i < numSteps; i++) {
                    // Read pixels along the vector
                    vec2 pos = origin + dir * (float(i) / float(numSteps));
                    vec4 color = texture(walls, screen2texcoord(pos));
                    // If we find non-zero pixel data we have obstacles in our path!
                    if (color != vec4(0.0)) return;
                }
                // We simply return the primitive index.
                // This is a built in counter in geometry shaders
                // started at 0 incrementing by 1 for every invocation.
                // It should always match the spritelist index.
                spriteIndex = float(gl_PrimitiveIDIn);
                EmitVertex();
                EndPrimitive();
            }
            """,
        )
        # Configure program with maximum distance
        self.program_select_sprites["maxDistance"] = INTERACTION_RADIUS

        # NOTE: Before we do this we need to ensure the internal sprite buffers are complete!
        self.coins.write_sprite_buffers_to_gpu()
        # We need a buffer that can capture the output from our transform shader.
        # We need to make room for len(coins) 32 bit floats (4 bytes each. size specified in bytes)
        self.result_buffer = self.ctx.buffer(reserve=len(self.coins) * 4)
        # We need a query to count how many sprites the shader gave us.
        # We do this by making a sampler that counts the number of primitives
        # (points in this instance) it emitted into the result buffer.
        self.query = self.ctx.query()

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

        # As long as we have coins...
        if len(self.coins) > 0:
            # Ensure the internal sprite buffers are up to date
            self.coins.write_sprite_buffers_to_gpu()
            # Bind the wall texture to texture channel 0 so we can read it in the shader
            self.walls_fbo.color_attachments[0].use(0)
            with self.query:
                # We already have a geometry instance in the spritelist we can
                # use to run our shader/gpu program. It only requires that we
                # use correctly named input name(s). in_pos in this example
                # what will automatically map in the position buffer to the vertex shader.
                self.coins.geometry.transform(
                    self.program_select_sprites,
                    self.result_buffer,
                    vertices=len(self.coins),
                )

            # Store the number of primitives/sprites found
            num_sprites_found = self.query.primitives_generated
            if num_sprites_found > 0:
                print(f"We found {num_sprites_found} sprite(s)")
                # Transfer the the data from the vram into python and decode the
                # values into python objects. We read num_sprites_found float
                # values from the result buffer and convert those into python floats
                sprite_indices = struct.unpack(
                    f"{num_sprites_found}f",
                    self.result_buffer.read(size=num_sprites_found * 4),
                )
                print("Indices found:", sprite_indices)
                print(
                    (
                        f"max(sprite_indices) = {max(sprite_indices)} | "
                        f"len(self.coins) = {len(self.coins)} | "
                        f"sprite_indices = {len(sprite_indices)}"
                    )
                )
                # Resolve the list of selected sprites and remove them
                sprites = [self.coins[int(i)] for i in sprite_indices]
                for coin in sprites:
                    coin.remove_from_sprite_lists()

        self.walls.draw()
        self.coins.draw()
        arcade.draw_sprite(self.player)

        # Visualize the interaction radius
        arcade.draw_circle_filled(
            center_x=self.player.center_x,
            center_y=self.player.center_y,
            radius=INTERACTION_RADIUS,
            color=(255, 255, 255, 64)
        )

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        # Move the sprite to mouse position
        self.player.position = x, y
        # Update the program with a new origin
        self.program_select_sprites["origin"] = x, y


SpriteListInteraction().run()
