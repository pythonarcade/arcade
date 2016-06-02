"""
Example "Arcade" library code.

Showing how to do nested loops.
"""

# Library imports
import arcade

COLUMN_SPACING = 60
ROW_SPACING = 40

TEXT_SIZE = 12

# Open the window and set the background
arcade.open_window("Complex Loops - Top Left Triangle", 600, 400)

arcade.set_background_color(arcade.color.WHITE)

# Start the render process. This must be done before any drawing commands.
arcade.start_render()

# Loop for each row
for row in range(10):
    # Loop for each column
    # Change the number of columns depending on the row we are in
    for column in range(row):
        # Calculate our location
        x = column * COLUMN_SPACING
        y = row * ROW_SPACING

        # Draw the item
        arcade.draw_text("({}, {})".format(column, row),
                         x, y,
                         arcade.color.BLACK, TEXT_SIZE)

# Finish the render.
arcade.finish_render()

# Keep the window up until someone closes it.
arcade.run()
