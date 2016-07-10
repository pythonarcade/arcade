.. _quick-index:

Quick API Index
===============

Window Module
-------------

Functions
^^^^^^^^^
- close_window()
- finish_render()
- get_window()
- open_window(window_title, width, height)
- pause(seconds)
- quick_run(time_to_pause)
- run()
- schedule(function_pointer, interval)
- set_background_color(color)
- set_viewport(left, right, bottom, top)
- set_window(window)
- start_render()


Drawing Module
--------------

Classes
^^^^^^^
- Texture()
    - __init__(id, width, height)
- VertexBuffer()
    - __init__(vbo_id, size, width, height, color)

Functions
^^^^^^^^^
- create_ellipse(width, height, color)
- create_rectangle(width, height, color)
- draw_arc_filled(center_x, center_y, width, height, color, start_angle, end_angle, tilt_angle=0)
- draw_arc_outline(center_x, center_y, width, height, color, start_angle, end_angle, border_width=1, tilt_angle=0)
- draw_circle_filled(center_x, center_y, radius, color)
- draw_circle_outline(center_x, center_y, radius, color, border_width=1)
- draw_ellipse_filled(center_x, center_y, width, height, color, tilt_angle=0)
- draw_ellipse_outline(center_x, center_y, width, height, color, border_width=1, tilt_angle=0)
- draw_line(start_x, start_y, end_x, end_y, color, border_width=1)
- draw_line_strip(point_list, color, border_width=1)
- draw_lines(point_list, color, border_width=1)
- draw_parabola_filled(start_x, start_y, end_x, height, color, tilt_angle=0)
- draw_parabola_outline(start_x, start_y, end_x, height, color, border_width=1, tilt_angle=0)
- draw_point(x, y, color, size)
- draw_points(point_list, color, size)
- draw_polygon_filled(point_list, color)
- draw_polygon_outline(point_list, color, border_width=1)
- draw_rectangle(center_x, center_y, width, height, color, border_width=0, tilt_angle=0)
- draw_rectangle_filled(x, y, width, height, color, tilt_angle=0)
- draw_rectangle_outline(x, y, width, height, color, border_width=1, tilt_angle=0)
- draw_text(text, start_x, start_y, color, size)
- draw_texture_rectangle(center_x, center_y, width, height, texture, angle=0, alpha=1, transparent=True)
- draw_triangle_filled(x1, y1, x2, y2, x3, y3, color)
- draw_triangle_outline(x1, y1, x2, y2, x3, y3, color, border_width=1)
- load_texture(file_name, x=0, y=0, width=0, height=0, scale=1)
- load_textures(file_name, image_location_list, mirrored=False, flipped=False)
- render_ellipse_filled(shape, center_x, center_y, color, angle=0)
- render_rectangle_filled(shape, center_x, center_y, color, tilt_angle=0)
- trim_image(image)

Shape Objects Module
--------------------

Classes
^^^^^^^
- Shape()
    - __init__(center_x, center_y, color=arcade.color.GREEN,

    - draw()
    - update()
- Rectangle(Shape)
    - __init__(center_x, center_y, width, height,

    - draw()
- Square(Rectangle)
    - __init__(center_x, center_y, width_and_height,

    - draw()
- Oval(Shape)
    - __init__(center_x, center_y, width, height,

    - draw()
- Ellipse(Oval)
    - __init__(center_x, center_y, width, height,

    - draw()
- Circle(Shape)
    - __init__(center_x, center_y, radius,

    - draw()
- Point(Shape)
    - __init__(center_x, center_y, size, color=arcade.color.GREEN)
    - draw()
- Text(Shape)
    - __init__(text, center_x, center_y, size,

    - draw()
- Triangle()
    - __init__(first_x, first_y, second_x, second_y, third_x, third_y,

    - draw()
    - update()
- Polygon()
    - __init__(point_list, color=arcade.color.GREEN, border_width=0)
    - draw()
    - update()
- Parabola()
    - __init__(start_x, start_y, end_x, height,

    - draw()
    - update()
- Line()
    - __init__(start_x, start_y, end_x, end_y,

    - draw()
    - update()
- Arc()
    - __init__(center_x, center_y, width, height,

    - draw()
    - update()

Functions
^^^^^^^^^
- draw_all(list)
- master_draw(object)
- update_all(list)

Geometry Module
---------------

Functions
^^^^^^^^^
- are_polygons_intersecting(poly_a, poly_b)
- check_for_collision(sprite1, sprite2)
- check_for_collision_with_list(sprite1, sprite_list)
- rotate(x, y, cx, cy, angle)

Sprite Module
-------------

Classes
^^^^^^^
- SpriteList()
    - __init__()
    - append(item)
    - remove(item)
    - update()
    - update_animation()
    - draw(fast=True)
    - pop()
- Sprite()
    - __init__(filename=None, scale=1, x=0, y=0, width=0, height=0)
    - append_texture(texture)
    - set_texture(texture_no)
    - get_texture()
    - set_position(center_x, center_y)
    - set_points(points)
    - get_points()
    - draw()
    - update()
    - update_animation()
    - kill()
- AnimatedTimeSprite(Sprite)
    - __init__(scale=1, x=0, y=0)
    - update_animation()
- AnimatedWalkingSprite(Sprite)
    - __init__(scale=1, x=0, y=0)
    - update_animation()

Physics Engines Module
----------------------

Classes
^^^^^^^
- PhysicsEngineSimple()
    - __init__(player_sprite, walls)
    - update()
- PhysicsEnginePlatformer()
    - __init__(player_sprite, platforms, gravity_constant=0.5)
    - can_jump()
    - update()

Application Module
------------------

Classes
^^^^^^^
- Window(pyglet.window.Window)
    - __init__(width, height, title='Arcade Window')
    - animate(dt)
    - set_update_rate(rate)
    - on_mouse_motion(x, y, dx, dy)
    - on_mouse_press(x, y, button, modifiers)
    - on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    - on_mouse_release(x, y, button, modifiers)
    - on_key_press(symbol, modifiers)
    - on_key_release(symbol, modifiers)

