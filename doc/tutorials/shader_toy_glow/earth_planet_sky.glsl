// EarthPlanetSky by MelisaHot
// https://www.shadertoy.com/view/ssjBD3

const int MAX_MARCHING_STEPS = 255;
const float MIN_DIST = 0.0;
const float MAX_DIST = 100.0;
const float PRECISION = 0.0001;


#define NUM_LAYER 6.


mat2 Rot(float angle){
    float s=sin(angle), c=cos(angle);
    return mat2(c, -s, s, c);
}


float sdSphere(vec3 p, float r )
{
  vec3 offset = vec3(0, 0, -4);
  return length(p - offset) - r;
}

float rayMarch(vec3 ro, vec3 rd, float start, float end) {
  float depth = start;

  for (int i = 0; i < MAX_MARCHING_STEPS; i++) {
    vec3 p = ro + depth * rd;
    float d = sdSphere(p, 1.);
    depth += d;
    if (d < PRECISION || depth > end) break;
  }

  return depth;
}


vec3 calcNormal(vec3 p) {
    vec2 e = vec2(1.0, -1.0) * 0.0005; // epsilon
    float r = 1.; // radius of sphere
    return normalize(
      e.xyy * sdSphere(p + e.xyy, r) +
      e.yyx * sdSphere(p + e.yyx, r) +
      e.yxy * sdSphere(p + e.yxy, r) +
      e.xxx * sdSphere(p + e.xxx, r));
}


float hash(vec2 p) {
  return fract(sin(dot(p.xy, vec2(5.34, 7.13)))*5865.273458);
}




float Hash21(vec2 p){
    p = fract(p*vec2(123.34, 456.21));
    p +=dot(p, p+45.32);
    return  fract(p.x*p.y);
}

float Star(vec2 uv, float flare){
    float d = length(uv);//center of screen is origin of uv -- length give us distance from every pixel to te center
    float m = .05/d;
    float rays = max(0., 1.-abs(uv.x*uv.y*1000.));
    m +=rays*flare;
    uv *=Rot(3.1415/4.);
    rays = max(0., 1.-abs(uv.x*uv.y*1000.));
    m +=rays*.2*flare;
    m *=smoothstep(1., .1, d);
    return m;
}

vec3 StarLayer(vec2 uv){

   vec3 col = vec3(0.);

    vec2 gv= fract(uv)-.5; //gv is grid view
    vec2 id= floor(uv);

    for(int y=-1; y<=1; y++){
        for(int x=-1; x<=1; x++){

            vec2 offset= vec2(x, y);
            float n = Hash21(id+offset);
            float size = fract(n*345.32);
            float star= Star(gv-offset-(vec2(n, fract(n*34.))-.5), smoothstep(.8, 1., size)*.6);
            vec3 color = sin(vec3(.2, .3, .4)*fract(n*2345.2)*123.2)*.5+.5;
            color = color*vec3(.7, .2, .5+size);

            star *=sin(iTime*3.+n*6.2831)*.5+.5;
            col +=star*size*color;

         }
     }
    return col;
}
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
  vec2 uv = (fragCoord-.5*iResolution.xy)/iResolution.y;
 vec3 backgroundColor = vec3(0.);

    for(float i =0.; i<1.; i += 1./NUM_LAYER){
        float depth = fract(i+iTime*.02);
        float scale= mix(10.,.5, depth);
        float fade = depth*smoothstep(1., .8, depth);
        backgroundColor += StarLayer(uv*scale+i*453.32)*fade;

}
  vec3 col = vec3(0);
  vec3 ro = vec3(0, 0, 3); // ray origin that represents camera position
  vec3 rd = normalize(vec3(uv, -1)); // ray direction

  float d = rayMarch(ro, rd, MIN_DIST, MAX_DIST); // distance to sphere

  if (d+0.5 > MAX_DIST) {
    col = backgroundColor; // ray didn't hit anything
  } else {
    vec3 p = ro + rd * d; // point on sphere we discovered from ray marching
    vec3 normal = calcNormal(p);
    vec3 lightPosition = vec3(sin(iTime*0.5)*2.0, 0.0, cos(iTime*0.5)*2.0) ;
    vec3 lightDirection = normalize(lightPosition - p);

    // Calculate diffuse reflection by taking the dot product of
    // the normal and the light direction.
    float dif = clamp(dot(normal, lightDirection), 0.3, 1.);

    // Multiply the diffuse reflection value by an orange color and add a bit
    // of the background color to the sphere to blend it more with the background.

    vec2 rg = textureLod( iChannel0, uv, .5 ).yx;
    col= dif*vec3(rg, .6);

  }


  // Output to screen
  fragColor = vec4(col, 1.0);
}
