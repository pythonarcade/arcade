#version 330

// The base uv defines the start and end UV co-oridnates before any resizing has occured.
uniform vec4 base_uv;

// The var uv defines the start and end UV co-ordincates after the resizing.
uniform vec4 var_uv;

// Because the nine_patch relies on a texture atlas, we need the texture id to retrieve the data
// from the uv_texture, and use that to get the correct placement in the sprite_texture.
uniform float texture_id;

uniform sampler2D uv_texture;
uniform sampler2D sprite_texture;

// The interpolated fragment specific uv.
in vec2 pos_uv;

// The final output frag colour.
out vec4 f_color;

void main() {
    vec2 tex_uv;

    if (pos_uv.x <= var_uv.x){
        // If the frag uv is below the start edge uv threshold we want to normalise the uv,
        // and then convert to the range 0.0 - base uv.

        tex_uv.x = pos_uv.x / var_uv.x * base_uv.x;
    }
    else if (pos_uv.x >= var_uv.z){
        // If the frag uv is above the end edge uv threshold we want to normalse the uv.
        // and then convert to the base uv. However, for the right edge we must first
        // make the frag uv range from 0.0 - (1.0 - varying end uv), this will allow us to easily normalise
        // the co-ordinates to the range end uv - 1.0.
        tex_uv.x = base_uv.z + (pos_uv.x - var_uv.z) / (1 - var_uv.z) * (1 - base_uv.z);
    }
    else{
        // If the frag uv is inbetween the start and end uv we want to normalise the uv,
        // and then convert to the range start uv - end uv. Again we must first convert the
        // the frag uv for easy normilisation, by minusing the varying start uv.
        tex_uv.x = base_uv.x + (pos_uv.x - var_uv.x) / (var_uv.z - var_uv.x) * (base_uv.z - base_uv.x);
    }

    // The same logic holds for the y-axis.
    if (pos_uv.y <= var_uv.y){
        tex_uv.y = pos_uv.y / var_uv.y * base_uv.y;
    }
    else if (pos_uv.y >= var_uv.w){
        tex_uv.y = base_uv.w + ((pos_uv.y - var_uv.w) / (1 - var_uv.w)) * (1 - base_uv.w);
    }
    else{
        tex_uv.y = base_uv.y + (pos_uv.y - var_uv.y) / (var_uv.w - var_uv.y) * (base_uv.w - base_uv.y);
    }

    // Retrieve the texture data from the atlas and multiply by the calculated adjust uv.
    // The uv is calcualted with the y-axis 0.0 at the bottom. so a invesrion must be done.
    vec4 uv_data = texelFetch(uv_texture, ivec2(texture_id, 0), 0);
    f_color = texture(sprite_texture, vec2(uv_data.x, 1 - uv_data.y) + vec2(uv_data.z, -uv_data.w)*tex_uv);

}