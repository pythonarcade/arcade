"""
Simple normal mapping example.

We load a diffuse and normal map and render them using a simple shader.
The normal texture stores a direction vector in the RGB channels
pointing up from the surface.

For simplicity we use the texture coordinates to determine the
screen position but this can be done in other ways.

Controls:
    Mouse: Move light source
    Mouse wheel: Move light source in and out

Run this example from the command line with:
python -m arcade.examples.gl.normal_mapping_simple
"""

import arcade
from arcade.gl import geometry


class NormalMapping(arcade.Window):
    def __init__(self):
        super().__init__(512, 512, "Normal Mapping")

        # Load the color (diffuse) and normal texture
        # These should ideally be the same size
        self.texture_diffuse = self.ctx.load_texture(
            ":resources:images/test_textures/normal_mapping/diffuse.jpg"
        )
        self.texture_normal = self.ctx.load_texture(
            ":resources:images/test_textures/normal_mapping/normal.jpg"
        )

        # Shader program doing basic normal mapping
        self.program = self.ctx.program(
            vertex_shader="""
                #version 330

                // Inputs from the quad_fs geometry
                in vec2 in_vert;
                in vec2 in_uv;

                // Output to the fragment shader
                out vec2 uv;

                void main() {
                    uv = in_uv;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }

            """,
            fragment_shader="""
                #version 330

                // Samplers for reading from textures
                uniform sampler2D texture_diffuse;
                uniform sampler2D texture_normal;
                // Global light position we can set from python
                uniform vec3 light_pos;

                // Input from vertex shader
                in vec2 uv;

                // Output to the framebuffer
                out vec4 f_color;

                void main() {
                    // Read RGBA color from the diffuse texture
                    vec4 diffuse = texture(texture_diffuse, uv);
                    // Read normal from RGB channels and convert to a direction vector.
                    // These vectors are like a needle per pixel pointing up from the surface.
                    // Since RGB is 0-1 we need to convert to -1 to 1.
                    vec3 normal = normalize(texture(texture_normal, uv).rgb * 2.0 - 1.0);

                    // Calculate the light direction.
                    // This is the direction between the light position and the pixel position.
                    vec3 light_dir = normalize(light_pos - vec3(uv, 0.0));

                    // Calculate the diffuse factor.
                    // This is the dot product between the light direction and the normal.
                    // It's basically calculating the angle between the two vectors.
                    // The result is a value between 0 and 1.
                    float diffuse_factor = max(dot(normal, light_dir), 0.0);

                    // Write the final color to the framebuffer.
                    // We multiply the diffuse color with the diffuse factor.
                    f_color = vec4(diffuse.rgb * diffuse_factor, 1.0);
                }
            """,
        )
        # Configure what texture channel the samplers should read from
        self.program["texture_diffuse"] = 0
        self.program["texture_normal"] = 1

        # Shortcut for a full screen quad
        # It has two buffers with positions and texture coordinates
        # named "in_vert" and "in_uv" so we need to use that in the vertex shader
        self.quad_fs = geometry.quad_2d_fs()

        # Keep track of mouse coordinates for light position
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.mouse_z = 0.25

        self.text = arcade.Text("0, 0, 0", 20, 20, arcade.color.WHITE)

    def on_draw(self):
        self.clear()

        # Bind the textures to the channels we configured in the shader
        self.texture_diffuse.use(0)
        self.texture_normal.use(1)

        # Update the light position uniform variable
        self.program["light_pos"] = self.mouse_x, self.mouse_y, self.mouse_z

        # Run the normal mapping shader (fills a full screen quad)
        self.quad_fs.render(self.program)

        # Draw the mouse coordinates
        self.text.text = f"{self.mouse_x:.2f}, {self.mouse_y:.2f}, {self.mouse_z:.2f}"
        self.text.draw()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Move the light source with the mouse."""
        # Convert to normalized coordinates
        # (0.0, 0.0) is bottom left, (1.0, 1.0) is top right
        self.mouse_x, self.mouse_y = x / self.width, y / self.height

    def on_mouse_scroll(self, x: int, y: int, scroll_x: float, scroll_y: float):
        """Zoom in/out with the mouse wheel."""
        self.mouse_z += scroll_y * 0.05


NormalMapping().run()
