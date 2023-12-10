from array import array

import arcade
import arcade.gl as gl

# TODO: comment for days

win = arcade.Window()
win.set_exclusive_mouse()
geo = gl.geometry.cube((0.5, 0.5, 0.5))
prog = win.ctx.program(
    vertex_shader="\n".join((
        "#version 330",
        "uniform WindowBlock {",
        "    mat4 projection;",
        "    mat4 view;",
        "} window;",
        "in vec3 in_position;",
        "in vec3 in_normal;",
        "in vec2 in_uv;",
        "",
        "out vec3 vs_normal;",
        "out vec2 vs_uv;",
        "void main() {",
        "gl_Position = window.projection * window.view * vec4(in_position, 1.0);",
        "vs_normal = in_normal;",
        "vs_uv = in_uv;",
        "}"
    )),
    fragment_shader="\n".join((
        "#version 330",
        "in vec3 vs_normal;",
        "in vec2 vs_uv;",
        "out vec4 fs_colour;",
        "",
        "void main() {",
        "vec3 uv_colour = vec3(vs_uv, 0.2);",
        "float light_intensity = 0.2 + max(0.0, dot(vs_normal, vec3(pow(3, -0.5), pow(3, -0.5), pow(3, -0.5))));",
        "fs_colour = vec4(light_intensity * uv_colour, 1.0);",
        "}"
    ))
)

cam = arcade.camera.PerspectiveProjector()
cam.view.position = (0.0, 0.0, 1.0)

forward = 0
strafe = 0


def on_mouse_motion(x, y, dx, dy):
    _l = (dx**2 + dy**2)**0.5

    arcade.camera.controllers.rotate_around_up(cam.view, 2.0 * dx/_l)
    _f = cam.view.forward
    arcade.camera.controllers.rotate_around_right(cam.view, 2.0 * -dy/_l, up=False)
    if abs(cam.view.forward[0]*cam.view.up[0]+cam.view.forward[1]*cam.view.up[1]+cam.view.forward[2]*cam.view.up[2]) > 0.90:
        cam.view.forward = _f
win.on_mouse_motion = on_mouse_motion


def on_key_press(symbol, modifier):
    global forward, strafe
    if symbol == arcade.key.ESCAPE:
        win.close()

    if symbol == arcade.key.W:
        forward += 1
    elif symbol == arcade.key.S:
        forward -= 1
    elif symbol == arcade.key.D:
        strafe += 1
    elif symbol == arcade.key.A:
        strafe -= 1
win.on_key_press = on_key_press


def on_key_release(symbol, modifier):
    global forward, strafe
    if symbol == arcade.key.W:
        forward -= 1
    elif symbol == arcade.key.S:
        forward += 1
    elif symbol == arcade.key.D:
        strafe -= 1
    elif symbol == arcade.key.A:
        strafe += 1
win.on_key_release = on_key_release


def on_update(delta_time):
    win.set_mouse_position(0, 0)
    arcade.camera.controllers.strafe(cam.view, (strafe * delta_time * 1.0, 0.0))

    _pos = cam.view.position
    _for = cam.view.forward

    cam.view.position = (
        _pos[0] + _for[0] * forward * delta_time * 1.0,
        _pos[1] + _for[1] * forward * delta_time * 1.0,
        _pos[2] + _for[2] * forward * delta_time * 1.0,
    )

win.on_update = on_update


def on_draw():
    win.ctx.enable(win.ctx.DEPTH_TEST)
    win.clear()
    cam.use()
    geo.render(prog)
win.on_draw = on_draw

win.run()

