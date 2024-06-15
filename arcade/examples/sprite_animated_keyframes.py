"""
Example using the TextureAnimationSprite class to animate a sprite using keyframes.
This sprite type is primarily used internally by tilemaps, but can be used for other purposes as well.

If Python and arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_animated_keyframes
"""
import arcade


class Animated(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Time based animated sprite")

        # Load the 8 frames for the walking animation
        keyframes = [
            arcade.TextureKeyframe(
                texture=arcade.load_texture(
                    f":assets:/images/animated_characters/female_adventurer/femaleAdventurer_walk{i}.png"
                ),
                duration=100,
            )
            for i in range(8)
        ]
        anim = arcade.TextureAnimation(keyframes=keyframes)
        self.sprite = arcade.TextureAnimationSprite(
            animation=anim,
            scale=1.0,
            center_x=400,
            center_y=300
        )

    def on_draw(self):
        self.clear()
        self.sprite.draw(pixelated=True)

    def on_update(self, delta_time: float):
        self.sprite.update_animation(delta_time)


def main():
    Animated().run()


if __name__ == "__main__":
    main()

