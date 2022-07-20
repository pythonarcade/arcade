#version 330

uniform vec4 patch_data;

uniform Projection {
    mat4 matrix;
} proj;

in vec2 in_uv;

out vec2 pos_uv;

void main() {
    // Position the vertices and pass the uv to the fragment shader.
    gl_Position = proj.matrix * vec4(patch_data.x + in_uv.x*patch_data.z, patch_data.y + in_uv.y*patch_data.w, 0, 1);
    pos_uv = in_uv;
}
