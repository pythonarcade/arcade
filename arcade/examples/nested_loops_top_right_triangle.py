"""
Example "Arcade" library code.

Showing how to do nested loops.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.nested_loops_bottom_right_triangle
"""

# Library imports
import arcade

COLUMN_SPACING = 20
ROW_SPACING = 20
LEFT_MARGIN = 110
BOTTOM_MARGIN = 110

# Open the window and set the background
arcade.open_window(400, 400, "Complex Loops - Top Right Triangle")

arcade.set_background_color(arcade.color.WHITE)

# Start the render process. This must be done before any drawing commands.
arcade.start_render()

# Loop for each row
for row in range(10):
    # Loop for each column
    # Change the number of columns depending on the row we are in
    for column in range(9 - row, 10):
        # Calculate our location
        x = column * COLUMN_SPACING + LEFT_MARGIN
        y = row * ROW_SPACING + BOTTOM_MARGIN

        # Draw the item
        arcade.draw_circle_filled(x, y, 7, arcade.color.AO)

# Finish the render.
arcade.finish_render()

# Keep the window up until someone closes it.
arcade.run()
