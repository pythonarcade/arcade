#version 330
// Shader for drawing a texutre into the atlas with extruded borders
uniform sampler2D image;
uniform vec2 image_size;
uniform float border;

in vec2 uv;
out vec4 fragColor;

void main()
{
    vec2 tex_size = textureSize(image, 0);
    vec2 content_ratio = image_size / tex_size;

    // Size of the area we are drawing into (including border)
    vec2 target_size = image_size + 2.0 * border;
    vec2 px = 1.0 / target_size;

    // Offset the uvs by the border size
    vec2 offset = px * border;
    // Scale up the uvs to create extrusion in borders
    vec2 scale = target_size / image_size;

    // Adjust the uvs to the content area
    vec2 adjusted_uv = (uv - offset) * (scale * content_ratio);
    // Clamp the uvs to the content area
    adjusted_uv = clamp(adjusted_uv, vec2(0.0), content_ratio - 2.0 / tex_size);

    fragColor = texture(image, adjusted_uv);
}
