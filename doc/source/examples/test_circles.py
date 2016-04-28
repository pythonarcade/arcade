import arcade


def on_draw(delta_time):
    arcade.start_render()

    # Appear in first column
    arcade.draw_circle_filled(100, 100, 50, arcade.color.YELLOW)

    # Appear in second column
    arcade.draw_small_filled_circle(300, 100, arcade.color.YELLOW)
    arcade.draw_medium_filled_circle(300, 300, arcade.color.YELLOW)
    arcade.draw_large_filled_circle(300, 500, arcade.color.YELLOW)

    # Appear in third column
    arcade.draw_standard_circle(500, 100,
                                arcade.color.YELLOW, "LARGE", "filled")
    arcade.draw_standard_circle(500, 300,
                                arcade.color.YELLOW, "m", "filled")
    arcade.draw_standard_circle(500, 500,
                                arcade.color.YELLOW, "small", "filled")

    # Appear in fourth column
    arcade.draw_circle_outline(700, 300, 50, arcade.color.YELLOW)

    arcade.draw_circle(700, 100, 50, arcade.color.YELLOW)

arcade.open_window("Test Circles", 800, 600)
arcade.set_background_color(arcade.color.RED)

arcade.schedule(on_draw, 1/80)

arcade.run()

arcade.close_window()
