#version 330

#define MAX_STEPS 100
#define MAX_DIST 100.0
#define SURF_DIST 0.01

uniform float aspect_ratio;
uniform float iTime;

out vec4 fragColor;
in vec2 v_uv;

float GetDist(vec3 p) {
    // Sphere at x=0, y=1, z=6 with radius 6
    vec4 sphere = vec4(0.0, 1.0, 6.0, 1.0);
    // Move the sphere a little bit based on time
    sphere.y = 1.25 + sin(iTime) / 6.0;

    // Distance betwwn p and the sphere.
    // Distance between p and sphere center minus sphere radius
    float sphereDist = length(p - sphere.xyz) - sphere.w;

    float planeDist = p.y;

    float d = min(sphereDist, planeDist);

    return d;
}

float RayMarch(vec3 ro, vec3 rd) {
    float d0 = 0.0;

    // Match the ray until we so close it's a hit
    // or we have reached the maximum distance
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * d0;
        float dS = GetDist(p);
        d0 += dS;
        if (d0 > MAX_DIST || dS < SURF_DIST) break;
    }
    return d0;
}

vec3 GetNormal(vec3 p) {
    float d = GetDist(p);
    vec2 e = vec2(0.01, 0.0);

    vec3 n = d - vec3(
        GetDist(p-e.xyy),
        GetDist(p-e.yxy),
        GetDist(p-e.yyx));

    return normalize(n);
}

// Get light for a point
float GetLight(vec3 p) {
    vec3 lightPos = vec3(0.0, 5.0, 6.0);
    lightPos.xz += vec2(sin(iTime), cos(iTime)) * 2.0;
    vec3 l = normalize(lightPos - p);
    vec3 n = GetNormal(p);
    float dif = clamp(dot(n, l), 0.0, 1.0);

    // Shadows: March between p and the light.
    // We need to move the point slightly or the marcher will return immediately
    float d = RayMarch(p + n * SURF_DIST * 2.0, l);
    // If the marched distance is lower than the distance
    // between the light and the point we can assume p is in shadow
    if (d < length(lightPos - p)) dif *= 0.1;

    return dif;
}

void main() {
    // Move center to the middle of the screen
    vec2 uv = v_uv - vec2(0.5);
    uv.x *= aspect_ratio;

    vec3 col = vec3(0.0);
    // Ray origin
    vec3 ro = vec3(0.0, 1.0, 0.0);
    // ray direction
    vec3 rd = normalize(vec3(uv, 1.0));

    // Final distance
    float d = RayMarch(ro, rd);

    // The point we are getting light for
    vec3 p = ro + rd * d;
    float dif = GetLight(p); // Diffuse light
    col = vec3(dif);

    // col = GetNormal(p);

    // Show ray directions
    fragColor = vec4(col, 1.0);
}
