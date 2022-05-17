import arcade

# Derive an application window from Arcade's parent Window class
class MyGame(arcade.Window):

    def __init__(self):
        # Call the parent constructor
        super().__init__(width=1920, height=1080)

    def on_draw(self):
        # Clear the screen
        self.clear()

if __name__ == "__main__":
    MyGame()
    arcade.run()
