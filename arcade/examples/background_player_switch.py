import arcade


if __name__ == "__main__":
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    sqaure_width = 2.99
    square_height = 2.99
    sqaure_spacing = 3

    sqaure_color = arcade.color.DARK_CYAN
    background = arcade.color.ASH_GREY


    @arcade.decorator.setup
    def setup(window):
        arcade.set_background_color(background)
        window.player = arcade.Player()
        import os
        path = "c:\\" + os.path.join(*arcade.__file__.split("\\")[1:-1], "examples", "sounds")
        window.player.load_dir(path)
        window.player.play(window.player.music[0])


    @arcade.decorator.update
    def update(window, dt):
        pass


    @arcade.decorator.draw
    def draw(window):
        pass


    arcade.decorator.run(SCREEN_WIDTH, SCREEN_HEIGHT, title="Background Example")
