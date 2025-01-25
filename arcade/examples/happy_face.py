"""
Drawing an example happy face

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.happy_face
"""

import arcade

# Set constants for the screen size
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Happy Face Example"

# Open the window. Set the window title and dimensions
arcade.open_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)

# Set the background color
arcade.set_background_color(arcade.color.WHITE)

# Clear screen and start render process
arcade.start_render()

# --- Drawing Commands Will Go Here ---

# Draw the face
x = 300
y = 300
radius = 200
arcade.draw_circle_filled(x, y, radius, arcade.color.YELLOW)

# Draw the right eye
x = 370
y = 350
radius = 20
arcade.draw_circle_filled(x, y, radius, arcade.color.BLACK)

# Draw the left eye
x = 230
y = 350
radius = 20
arcade.draw_circle_filled(x, y, radius, arcade.color.BLACK)

# Draw the smile
x = 300
y = 280
width = 240
height = 200
start_angle = 190
end_angle = 350
line_width = 20
arcade.draw_arc_outline(x, y, width, height, arcade.color.BLACK,
                        start_angle, end_angle, line_width)

# Finish drawing and display the result
arcade.finish_render()

# Keep the window open until the user hits the 'close' button
arcade.run()
