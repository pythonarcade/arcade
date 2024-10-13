"""
Example using the TextureAnimationSprite class to animate a sprite using keyframes.
This sprite type is primarily used internally by tilemaps, but can be used for other
purposes as well.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_animated_keyframes
"""
import arcade


class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        # Load the 8 frames for the walking animation
        path = ":assets:/images/animated_characters/female_adventurer/"
        keyframes = [
            arcade.TextureKeyframe(
                texture=arcade.load_texture(
                    path + f"femaleAdventurer_walk{i}.png"
                ),
                duration=100,
            )
            for i in range(8)
        ]
        anim = arcade.TextureAnimation(keyframes=keyframes)
        self.sprite = arcade.TextureAnimationSprite(
            animation=anim,
            scale=5.0,
            center_x=self.width // 2,
            center_y=self.height // 2,
        )

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.sprite, pixelated=True)

    def on_update(self, delta_time: float):
        self.sprite.update_animation(delta_time)


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(1280, 720, "Time based animated sprite")

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()

