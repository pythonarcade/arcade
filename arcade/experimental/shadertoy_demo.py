import arcade
from arcade.experimental.shadertoy import ShaderToy

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ShaderToy Demo"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.time = 0
        self.shadertoy = ShaderToy("""
            // Star Nest by Pablo Roman Andrioli
            // This content is under the MIT License.
            // Source : https://www.shadertoy.com/view/XlfGRj

            #define iterations 17
            #define formuparam 0.53

            #define volsteps 20
            #define stepsize 0.1

            #define zoom   0.800
            #define tile   0.850
            #define speed  0.010 

            #define brightness 0.0015
            #define darkmatter 0.300
            #define distfading 0.730
            #define saturation 0.850

            void mainImage( out vec4 fragColor, in vec2 fragCoord )
            {
                //get coords and direction
                vec2 uv=fragCoord.xy/iResolution.xy-.5;
                uv.y*=iResolution.y/iResolution.x;
                vec3 dir=vec3(uv*zoom,1.);
                float time=iTime*speed+.25;

                //mouse rotation
                float a1=.5+iMouse.x/iResolution.x*2.;
                float a2=.8+iMouse.y/iResolution.y*2.;
                mat2 rot1=mat2(cos(a1),sin(a1),-sin(a1),cos(a1));
                mat2 rot2=mat2(cos(a2),sin(a2),-sin(a2),cos(a2));
                dir.xz*=rot1;
                dir.xy*=rot2;
                vec3 from=vec3(1.,.5,0.5);
                from+=vec3(time*2.,time,-2.);
                from.xz*=rot1;
                from.xy*=rot2;
                
                //volumetric rendering
                float s=0.1,fade=1.;
                vec3 v=vec3(0.);
                for (int r=0; r<volsteps; r++) {
                    vec3 p=from+s*dir*.5;
                    p = abs(vec3(tile)-mod(p,vec3(tile*2.))); // tiling fold
                    float pa,a=pa=0.;
                    for (int i=0; i<iterations; i++) { 
                        p=abs(p)/dot(p,p)-formuparam; // the magic formula
                        a+=abs(length(p)-pa); // absolute sum of average change
                        pa=length(p);
                    }
                    float dm=max(0.,darkmatter-a*a*.001); //dark matter
                    a*=a*a; // add contrast
                    if (r>6) fade*=1.-dm; // dark matter, don't render near
                    //v+=vec3(dm,dm*.5,0.);
                    v+=fade;
                    v+=vec3(s,s*s,s*s*s*s)*a*brightness*fade; // coloring based on distance
                    fade*=distfading; // distance fading
                    s+=stepsize;
                }
                v=mix(vec3(length(v)),v,saturation); //color adjust
                fragColor = vec4(v*.01,1.);	                
            }                    
        """)

    def on_draw(self):
        arcade.start_render()
        self.shadertoy.draw(time=self.time)

    def on_update(self, dt):
        # Keep track of elapsed time
        self.time += dt

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.shadertoy.mouse_pos = x, y


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
