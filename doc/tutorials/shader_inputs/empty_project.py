import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Basic Arcade Template"


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.center_window()
        self.background_color = arcade.color.ALMOND

    def on_draw(self):
        # Draw a simple circle to the screen
        self.clear()
        arcade.draw_circle_filled(
            SCREEN_WIDTH / 2, 
            SCREEN_HEIGHT / 2,
            100,
            arcade.color.AFRICAN_VIOLET
        )


app = MyWindow()
arcade.run()
