""" This simple animation example shows how to bounce a rectangle
on the screen. """

import arcade

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50


def on_draw(delta_time):
    """ Use this function to draw everything to the screen. """

    # Start the render. This must happen before any drawing
    # commands. We do NOT need an stop render command.
    arcade.start_render()

    # Draw our rectangle
    arcade.draw_rect_filled(on_draw.x, on_draw.y,
                            RECT_WIDTH, RECT_HEIGHT,
                            arcade.color.BLACK)

    # Modify rectangles position based on the delta
    # vector. (Delta means change. You can also think
    # of this as our speed and direction.)
    on_draw.x += on_draw.delta_x
    on_draw.y += on_draw.delta_y

    # Figure out if we hit the edge and need to reverse.
    if on_draw.x < RECT_WIDTH // 2 or on_draw.x > SCREEN_WIDTH - RECT_WIDTH // 2:
        on_draw.delta_x *= -1
    if on_draw.y < RECT_HEIGHT // 2 or on_draw.y > SCREEN_HEIGHT - RECT_HEIGHT // 2:
        on_draw.delta_y *= -1

# These are function-specific variables. Before we
# use them in our function, we need to give them initial
# values.
on_draw.x = 100
on_draw.y = 50
on_draw.delta_x = 3
on_draw.delta_y = 2

# Open up our window
arcade.open_window("Drawing Example", SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.set_background_color(arcade.color.WHITE)

# Tell the computer to call the draw command at the specified interval.
arcade.schedule(on_draw, 1 / 80)

# Run the program
arcade.run()

# When done running the program, close the window.
arcade.close_window()
