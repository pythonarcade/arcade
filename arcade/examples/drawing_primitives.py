"""
Example "Arcade" library code.

This example shows the drawing primitives and how they are used.
It does not assume the programmer knows how to define functions or classes
yet.

API documentation for the draw commands can be found here:
https://api.arcade.academy/en/latest/quick_index.html

A video explaining this example can be found here:
https://vimeo.com/167158158

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.drawing_primitives
"""

# Import the Arcade library. If this fails, then try following the instructions
# for how to install arcade:
# https://api.arcade.academy/en/latest/install/index.html
import arcade

# Open the window. Set the window title and dimensions (width and height)
arcade.open_window(600, 600, "Drawing Primitives Example")

# Set the background color to white
# For a list of named colors see
# https://api.arcade.academy/en/latest/arcade.color.html
# Colors can also be specified in (red, green, blue) format and
# (red, green, blue, alpha) format.
arcade.set_background_color(arcade.color.WHITE)

# Start the render process. This must be done before any drawing commands.
arcade.start_render()

# Draw a grid
# Draw vertical lines every 120 pixels
for x in range(0, 601, 120):
    arcade.draw_line(x, 0, x, 600, arcade.color.BLACK, 2)

# Draw horizontal lines every 200 pixels
for y in range(0, 601, 200):
    arcade.draw_line(0, y, 800, y, arcade.color.BLACK, 2)

# Draw a point
arcade.draw_text("draw_point", 3, 405, arcade.color.BLACK, 12)
arcade.draw_point(60, 495, arcade.color.RED, 10)

# Draw a set of points
arcade.draw_text("draw_points", 123, 405, arcade.color.BLACK, 12)
point_list = ((165, 495),
              (165, 480),
              (165, 465),
              (195, 495),
              (195, 480),
              (195, 465))
arcade.draw_points(point_list, arcade.color.ZAFFRE, 10)

# Draw a line
arcade.draw_text("draw_line", 243, 405, arcade.color.BLACK, 12)
arcade.draw_line(270, 495, 300, 450, arcade.color.WOOD_BROWN, 3)

# Draw a set of lines
arcade.draw_text("draw_lines", 363, 405, arcade.color.BLACK, 12)
point_list = ((390, 450),
              (450, 450),
              (390, 480),
              (450, 480),
              (390, 510),
              (450, 510)
              )
arcade.draw_lines(point_list, arcade.color.BLUE, 3)

# Draw a line strip
arcade.draw_text("draw_line_strip", 483, 405, arcade.color.BLACK, 12)
point_list = ((510, 450),
              (570, 450),
              (510, 480),
              (570, 480),
              (510, 510),
              (570, 510)
              )
arcade.draw_line_strip(point_list, arcade.color.TROPICAL_RAIN_FOREST, 3)

# Draw a polygon
arcade.draw_text("draw_polygon_outline", 3, 207, arcade.color.BLACK, 9)
point_list = ((30, 240),
              (45, 240),
              (60, 255),
              (60, 285),
              (45, 300),
              (30, 300))
arcade.draw_polygon_outline(point_list, arcade.color.SPANISH_VIOLET, 3)

# Draw a filled in polygon
arcade.draw_text("draw_polygon_filled", 123, 207, arcade.color.BLACK, 9)
point_list = ((150, 240),
              (165, 240),
              (180, 255),
              (180, 285),
              (165, 300),
              (150, 300))
arcade.draw_polygon_filled(point_list, arcade.color.SPANISH_VIOLET)

# Draw an outline of a circle
arcade.draw_text("draw_circle_outline", 243, 207, arcade.color.BLACK, 10)
arcade.draw_circle_outline(300, 285, 18, arcade.color.WISTERIA, 3)

# Draw a filled in circle
arcade.draw_text("draw_circle_filled", 363, 207, arcade.color.BLACK, 10)
arcade.draw_circle_filled(420, 285, 18, arcade.color.GREEN)

# Draw an ellipse outline, and another one rotated
arcade.draw_text("draw_ellipse_outline", 483, 207, arcade.color.BLACK, 10)
arcade.draw_ellipse_outline(540, 273, 15, 36, arcade.color.AMBER, 3)
arcade.draw_ellipse_outline(540, 336, 15, 36,
                            arcade.color.BLACK_BEAN, 3, 45)

# Draw a filled ellipse, and another one rotated
arcade.draw_text("draw_ellipse_filled", 3, 3, arcade.color.BLACK, 10)
arcade.draw_ellipse_filled(60, 81, 15, 36, arcade.color.AMBER)
arcade.draw_ellipse_filled(60, 144, 15, 36,
                           arcade.color.BLACK_BEAN, 45)

# Draw an arc, and another one rotated
arcade.draw_text("draw_arc/filled_arc", 123, 3, arcade.color.BLACK, 10)
arcade.draw_arc_outline(150, 81, 15, 36,
                        arcade.color.BRIGHT_MAROON, 90, 360)
arcade.draw_arc_filled(150, 144, 15, 36,
                       arcade.color.BOTTLE_GREEN, 90, 360, 45)

# Draw an rectangle outline
arcade.draw_text("draw_rect", 243, 3, arcade.color.BLACK, 10)
arcade.draw_rectangle_outline(295, 100, 45, 65,
                              arcade.color.BRITISH_RACING_GREEN)
arcade.draw_rectangle_outline(295, 160, 20, 45,
                              arcade.color.BRITISH_RACING_GREEN, 3, 45)

# Draw a filled in rectangle
arcade.draw_text("draw_filled_rect", 363, 3, arcade.color.BLACK, 10)
arcade.draw_rectangle_filled(420, 100, 45, 65, arcade.color.BLUSH)
arcade.draw_rectangle_filled(420, 160, 20, 40, arcade.color.BLUSH, 45)

# Load and draw an image to the screen
# Image from kenney.nl asset pack #1
arcade.draw_text("draw_bitmap", 483, 3, arcade.color.BLACK, 12)
texture = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")
scale = .6
arcade.draw_scaled_texture_rectangle(540, 120, texture, scale, 0)
arcade.draw_scaled_texture_rectangle(540, 60, texture, scale, 45)

# Finish the render.
# Nothing will be drawn without this.
# Must happen after all draw commands
arcade.finish_render()

# Keep the window up until someone closes it.
arcade.run()
