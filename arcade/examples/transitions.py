"""
Example showing how to do transitions between views.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.transitions
"""
import arcade

WIDTH = 1280
HEIGHT = 720
FADE_RATE = 5


class FadingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.fade_out = None
        self.fade_in = 255

    def update_fade(self, next_view=None):
        if self.fade_out is not None:
            self.fade_out += FADE_RATE
            if self.fade_out is not None and self.fade_out > 255 and next_view is not None:
                game_view = next_view()
                game_view.setup()
                self.window.show_view(game_view)

        if self.fade_in is not None:
            self.fade_in -= FADE_RATE
            if self.fade_in <= 0:
                self.fade_in = None

    def draw_fading(self):
        if self.fade_out is not None:
            arcade.draw_rect_filled(
                arcade.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height,
                ),
                color=(0, 0, 0, self.fade_out),
            )

        if self.fade_in is not None:
            arcade.draw_rect_filled(
                arcade.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height,
                ),
                color=(0, 0, 0, self.fade_in),
            )


class MenuView(FadingView):
    """ Class that manages the 'menu' view. """

    def on_update(self, dt):
        self.update_fade(next_view=GameView)

    def on_show_view(self):
        """ Called when switching to this view"""
        self.window.background_color = arcade.color.WHITE

    def on_draw(self):
        """ Draw the menu """
        self.clear()
        arcade.draw_text("Menu Screen - press space to advance", WIDTH / 2, HEIGHT / 2,
                         arcade.color.BLACK, font_size=30, anchor_x="center")
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        """ Handle key presses. In this case, we'll just count a 'space' as
        game over and advance to the game over view. """
        if self.fade_out is None and key == arcade.key.SPACE:
            self.fade_out = 0

    def setup(self):
        """ This should set up your game and get it ready to play """
        # Replace 'pass' with the code to set up your game
        pass


class GameView(FadingView):
    """ Manage the 'game' view for our program. """

    def setup(self):
        """ This should set up your game and get it ready to play """
        # Replace 'pass' with the code to set up your game
        pass

    def on_update(self, dt):
        self.update_fade(next_view=GameOverView)

    def on_show_view(self):
        """ Called when switching to this view"""
        self.window.background_color = arcade.color.ORANGE_PEEL

    def on_draw(self):
        """ Draw everything for the game. """
        self.clear()
        arcade.draw_text("Game - press SPACE to advance", WIDTH / 2, HEIGHT / 2,
                         arcade.color.BLACK, font_size=30, anchor_x="center")
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        """ Handle key presses. In this case, we'll just count a 'space' as
        game over and advance to the game overview. """
        if key == arcade.key.SPACE:
            self.fade_out = 0


class GameOverView(FadingView):
    """ Class to manage the game overview """
    def on_update(self, dt):
        self.update_fade(next_view=MenuView)

    def on_show_view(self):
        """ Called when switching to this view"""
        self.background_color = arcade.color.BLACK

    def on_draw(self):
        """ Draw the game overview """
        self.clear()
        arcade.draw_text("Game Over - press SPACE to advance", WIDTH / 2, HEIGHT / 2,
                         arcade.color.WHITE, 30, anchor_x="center")
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        """ If user hits escape, go back to the main menu view """
        if key == arcade.key.SPACE:
            self.fade_out = 0

    def setup(self):
        """ This should set up your game and get it ready to play """
        # Replace 'pass' with the code to set up your game
        pass


def main():
    """ Startup """
    window = arcade.Window(WIDTH, HEIGHT, "Different Views Minimal Example")
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
