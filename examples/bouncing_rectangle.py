""" This simple animation example shows how to bounce a rectangle
on the screen. """

import arcade

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50


def draw(dt):
    """ Use this function to draw everything to the screen. """

    # Start the render. This must happen before any drawing
    # commands. We do NOT need an stop render command.
    arcade.start_render()

    # Draw our rectangle
    arcade.draw_rect_filled(draw.x, draw.y,
                            RECT_WIDTH, RECT_HEIGHT,
                            arcade.color.BLACK)

    # Modify rectangles position based on the delta
    # vector. (Delta means change. You can also think
    # of this as our speed and direction.)
    draw.x += draw.delta_x
    draw.y += draw.delta_y

    # Figure out if we hit the edge and need to reverse.
    if draw.x < 0 or draw.x > SCREEN_WIDTH - RECT_WIDTH:
        draw.delta_x *= -1
    if draw.y < RECT_HEIGHT or draw.y > SCREEN_HEIGHT:
        draw.delta_y *= -1

# These are function-specific variables. Before we
# use them in our function, we need to give them initial
# values.
draw.x = 0
draw.y = RECT_HEIGHT
draw.delta_x = 3
draw.delta_y = 2

# Open up our window
arcade.open_window("Drawing Example", SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.set_background_color(arcade.color.WHITE)

# Tell the computer to call the draw command at the specified interval.
arcade.schedule(draw, 1 / 80)

# Run the program
arcade.run()

# When done running the program, close the window.
arcade.close_window()
