"""
This simple animation example shows how to bounce a rectangle
on the screen.

It assumes a programmer knows how to create functions already.

It does not assume a programmer knows how to create classes. If you do know
how to create classes, see the starting template for a better example:

http://arcade.academy/examples/starting_template.html

Or look through the examples showing how to use Sprites.

A video walk-through of this example is available at:
https://vimeo.com/168063840

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.bouncing_rectangle

"""

import arcade

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Bouncing Rectangle Example"

# Size of the rectangle
RECT_WIDTH = 50
RECT_HEIGHT = 50


def on_draw(delta_time):
    """
    Use this function to draw everything to the screen.
    """

    # Start the render. This must happen before any drawing
    # commands. We do NOT need a stop render command.
    arcade.start_render()

    # Draw a rectangle.
    # For a full list of colors see:
    # http://arcade.academy/arcade.color.html
    arcade.draw_rectangle_filled(on_draw.center_x, on_draw.center_y,
                                 RECT_WIDTH, RECT_HEIGHT,
                                 arcade.color.ALIZARIN_CRIMSON)

    # Modify rectangles position based on the delta
    # vector. (Delta means change. You can also think
    # of this as our speed and direction.)
    on_draw.center_x += on_draw.delta_x * delta_time
    on_draw.center_y += on_draw.delta_y * delta_time

    # Figure out if we hit the edge and need to reverse.
    if on_draw.center_x < RECT_WIDTH // 2 \
            or on_draw.center_x > SCREEN_WIDTH - RECT_WIDTH // 2:
        on_draw.delta_x *= -1
    if on_draw.center_y < RECT_HEIGHT // 2 \
            or on_draw.center_y > SCREEN_HEIGHT - RECT_HEIGHT // 2:
        on_draw.delta_y *= -1

# Below are function-specific variables. Before we use them
# in our function, we need to give them initial values. Then
# the values will persist between function calls.
#
# In other languages, we'd declare the variables as 'static' inside the
# function to get that same functionality.
#
# Later on, we'll use 'classes' to track position and velocity for multiple
# objects.
on_draw.center_x = 100      # Initial x position
on_draw.center_y = 50       # Initial y position
on_draw.delta_x = 115  # Initial change in x
on_draw.delta_y = 130  # Initial change in y


def main():
    # Open up our window
    arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.set_background_color(arcade.color.WHITE)

    # Tell the computer to call the draw command at the specified interval.
    arcade.schedule(on_draw, 1 / 80)

    # Run the program
    arcade.run()


if __name__ == "__main__":
    main()
