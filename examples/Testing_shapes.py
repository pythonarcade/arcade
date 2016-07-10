import arcade


def on_draw(delta_time):
    """ Use this function to draw everything to the screen. """

    # Start the render. This must happen before any drawing
    # commands. We do NOT need an stop render command.
    arcade.start_render()

    # Draw shapes
    on_draw.rectangle.draw()
    on_draw.oval.draw()
    on_draw.ellipse.draw()
    on_draw.circle.draw()
    on_draw.square.draw()
    arcade.draw_all(shapes)

    # update shape positions
    on_draw.rectangle.update()
    on_draw.oval.update()
    on_draw.ellipse.update()
    on_draw.circle.update()
    on_draw.square.update()
    arcade.update_all(shapes)

arcade.open_window("Drawing Example", 800, 600)
arcade.set_background_color(arcade.color.WHITE)

on_draw.rectangle = arcade.Rectangle(400, 100, 35, 50, arcade.color.PURPLE)
on_draw.rectangle.change_x = 3
on_draw.rectangle.change_y = 2

on_draw.oval = arcade.Oval(250, 250, 50, 25, arcade.color.ORANGE)
on_draw.oval.change_x = 1
on_draw.oval.change_y = -1

on_draw.ellipse = arcade.Ellipse(500, 0, 25, 50, arcade.color.COCONUT)
on_draw.ellipse.change_y = 2
on_draw.ellipse.change_angle = 15

on_draw.circle = arcade.Circle(350, 250, 15, arcade.color.BLUE)
on_draw.circle.change_x = 1

on_draw.square = arcade.Square(350, 150, 20, arcade.color.GREEN, 12, 12)
on_draw.square.change_angle = 20

on_draw.m_circle = arcade.Circle(700, 550, 18, arcade.color.CORNFLOWER_BLUE)
on_draw.m_circle.change_x = -2

on_draw.m_rectangle = arcade.Rectangle(400, 300, 27, 18,
                                       arcade.color.KOMBU_GREEN)
on_draw.m_rectangle.change_x = 3
on_draw.m_rectangle.change_y = -3

on_draw.m_square = arcade.Square(50, 50, 27,
                                 arcade.color.LANGUID_LAVENDER, 6, 45)
on_draw.m_square.change_y = 5

shapes = [on_draw.m_square, on_draw.m_rectangle, on_draw.m_circle]

on_draw.point = arcade.Point(90, 90, 25, arcade.color.FOREST_GREEN)
on_draw.point.change_y = .5
shapes.append(on_draw.point)

on_draw.text = arcade.Text("Hello!!", 250, 300, 100, arcade.color.CHESTNUT)
shapes.append(on_draw.text)

on_draw.triangle = arcade.Triangle(40, 99, 100, 50, 55, 150,
                                   arcade.color.MAROON)
on_draw.triangle.change_x = 2
on_draw.triangle.change_y = 4
shapes.append(on_draw.triangle)

points = ([19, 24], [33, 107], [15, 66], [100, 75], [100, 90])
on_draw.polygon = arcade.Polygon(points, arcade.color.CYAN)
on_draw.polygon.change_x = 6
on_draw.polygon.change_y = 2
shapes.append(on_draw.polygon)

on_draw.parabola = arcade.Parabola(300, 450, 390, 50, arcade.color.INDIGO, 14)
on_draw.parabola.change_y = -2
on_draw.parabola.change_angle = 8
shapes.append(on_draw.parabola)

on_draw.line = arcade.Line(0, 0, 800, 800, arcade.color.AMAZON, 3)
on_draw.line.change_y = -2
shapes.append(on_draw.line)

on_draw.Arc = arcade.Arc(250, 250, 75, 100,
                         arcade.color.BRICK_RED, 0, 180, 0, 0)
on_draw.Arc.change_x = 0.5
on_draw.Arc.change_y = 0.5
on_draw.Arc.change_start_angle = .2
on_draw.Arc.change_end_angle = -.1
on_draw.Arc.change_tilt_angle = 3
shapes.append(on_draw.Arc)

arcade.schedule(on_draw, 1 / 80)

arcade.run()

# unnecssary if drawing with on_draw
# arcade.finish_render()
