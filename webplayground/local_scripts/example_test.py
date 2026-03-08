"""
Example local test script for the Arcade webplayground.

Place this file (or your own scripts) in the webplayground/local_scripts/ directory
to test them in the browser without restarting the server.

Your script should use the standard Python pattern with if __name__ == "__main__":
"""

import arcade


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Local Test Script")
        self.background_color = arcade.color.AMAZON

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Hello from local script!",
            self.width // 2,
            self.height // 2,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            anchor_y="center"
        )
        arcade.draw_text(
            "Edit this file and refresh to see changes",
            self.width // 2,
            self.height // 2 - 50,
            arcade.color.WHITE,
            font_size=16,
            anchor_x="center",
            anchor_y="center"
        )


if __name__ == "__main__":
    window = MyWindow()
    arcade.run()

