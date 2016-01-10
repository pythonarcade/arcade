"""
Example "Arcade" library code.

This example shows the drawing primitives and
how they are used.
"""

# Library imports
import math
import arcade

# Open the window and set the background
arcade.open_window("Drawing Example", 800, 600)
arcade.set_background_color(arcade.color.WHITE)

# Start the render process. This must be done before any drawing commands.
arcade.start_render()

# Draw a grid
x = -0.6
while x < 1:
    arcade.draw_line(x, -1, x, 1, arcade.color.BLACK, 2)
    x += 0.4

y = -0.33
while y < 1:
    arcade.draw_line(-1, y, 1, y, arcade.color.BLACK, 2)
    y += 0.66

# Draw a point
arcade.draw_text("draw_point", -0.99, 0.35, arcade.color.BLACK)
arcade.draw_point(-0.8, 0.65, arcade.color.RED, 10)

# Draw a set of points
arcade.draw_text("draw_points", -0.59, 0.35, arcade.color.BLACK)
point_list = ((-0.45, 0.65),
              (-0.45, 0.60),
              (-0.45, 0.55),
              (-0.35, 0.65),
              (-0.35, 0.60),
              (-0.35, 0.55))
arcade.draw_points(point_list, arcade.color.ZAFFRE, 10)

# Draw a line
arcade.draw_text("draw_line", -0.19, 0.35, arcade.color.BLACK)
arcade.draw_line(-0.1, 0.65, 0, 0.5, arcade.color.WOOD_BROWN, 3)

# Draw a set of lines
arcade.draw_text("draw_lines", 0.21, 0.35, arcade.color.BLACK)
point_list = ((0.3, 0.5),
              (0.5, 0.5),
              (0.3, 0.6),
              (0.5, 0.6),
              (0.3, 0.7),
              (0.5, 0.7)
              )
arcade.draw_lines(point_list, arcade.color.BLUE, 3)

# Draw a line strip
arcade.draw_text("draw_line_strip", 0.61, 0.35, arcade.color.BLACK)
point_list = ((0.7, 0.5),
              (0.9, 0.5),
              (0.7, 0.6),
              (0.9, 0.6),
              (0.7, 0.7),
              (0.9, 0.7)
              )
arcade.draw_line_strip(point_list, arcade.color.TROPICAL_RAIN_FOREST, 3)

# Draw a polygon
arcade.draw_text("draw_polygon_outline", -0.99, -0.31, arcade.color.BLACK)
point_list = ((-0.9, -0.2),
              (-0.85, -0.2),
              (-0.8, -0.15),
              (-0.8, -0.05),
              (-0.85, 0),
              (-0.9, 0))
arcade.draw_polygon_outline(point_list, arcade.color.SPANISH_VIOLET, 3)

# Draw a filled in polygon
arcade.draw_text("draw_polygon_filled", -0.59, -0.31, arcade.color.BLACK)
point_list = ((-0.5, -0.2),
              (-0.45, -0.2),
              (-0.4, -0.15),
              (-0.4, -0.05),
              (-0.45, 0),
              (-0.5, 0))
arcade.draw_polygon_filled(point_list, arcade.color.SPANISH_VIOLET)

# Draw an outline of a circle
arcade.draw_text("draw_circle_outline", -0.19, -0.31, arcade.color.BLACK)
arcade.draw_circle_outline(0, -0.05, 0.06, arcade.color.WISTERIA, 3)

# Draw a filled in circle
arcade.draw_text("draw_circle_filled", 0.21, -0.31, arcade.color.BLACK)
arcade.draw_circle_filled(0.4, -0.05, 0.06, arcade.color.GREEN, 3)

# Draw an ellipse outline, and another one rotated
arcade.draw_text("draw_ellipse_outline", 0.61, -0.31, arcade.color.BLACK)
arcade.draw_ellipse_outline(0.8, -0.09, 0.05, 0.12, arcade.color.AMBER, 3)
arcade.draw_ellipse_outline(0.8, 0.12, 0.05, 0.12,
                            arcade.color.BLACK_BEAN, 3, 45)

# Draw a filled ellipse, and another one rotated
arcade.draw_text("draw_ellipse_filled", -0.99, -0.99, arcade.color.BLACK)
arcade.draw_ellipse_filled(-0.8, -0.73, 0.05, 0.12, arcade.color.AMBER)
arcade.draw_ellipse_filled(-0.8, -0.52, 0.05, 0.12,
                           arcade.color.BLACK_BEAN, 45)

# Draw an arc, and another one rotated
arcade.draw_text("draw_arc/filled_arc", -0.59, -0.99, arcade.color.BLACK)
arcade.draw_arc_outline(-0.5, -0.73, 0.05, 0.12,
                        arcade.color.BRIGHT_MAROON, 90, 360)
arcade.draw_arc_filled(-0.5, -0.52, 0.05, 0.12,
                       arcade.color.BOTTLE_GREEN, 90, 360, 45)

# Draw an rectangle outline
arcade.draw_text("draw_rect", -0.19, -0.99, arcade.color.BLACK)
arcade.draw_rect_outline(-0.075, -0.5, .15, .35,
                         arcade.color.BRITISH_RACING_GREEN, 2)

# Draw a filled in rectangle
arcade.draw_text("draw_filled_rect", 0.21, -0.99, arcade.color.BLACK)
arcade.draw_rect_filled(0.3, -0.5, .15, .35, arcade.color.BLUSH)

# Load and draw an image to the screen
arcade.draw_text("draw_bitmap", 0.61, -0.99, arcade.color.BLACK)
texture = arcade.load_texture("images/playerShip1_orange.png")
scale = 0.002
arcade.draw_texture_rect(0.8, -0.6, scale * texture.width, scale * texture.height, texture, 0)
arcade.draw_texture_rect(0.8, -0.8, scale * texture.width, scale * texture.height, texture, 90)

# Finish the render.
# Nothing will be drawn without this.
# Must happen after all draw commands
arcade.finish_render()

# Keep the window up until someone closes it.
arcade.run()
