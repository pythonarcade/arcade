import arcade
from arcade.experimental import BloomFilter
import random
from arcade.color import RED, YELLOW, ORANGE, GREEN, BLUEBERRY, AMETHYST


# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ShaderToy Demo"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)

        # Create the crt filter
        self.bloom_filter = BloomFilter(width + 20, height,
                                        intensity=24.0)

        self.filter_on = True

        # Create some stuff to draw on the screen
        self.sprite_list = arcade.SpriteList()

        for y in range(10, self.height, 50):
            color = random.choice(
                [RED, YELLOW, ORANGE, GREEN, BLUEBERRY, AMETHYST])
            my_sprite = arcade.SpriteCircle(random.randrange(1, 40), color)
            self.sprite_list.append(my_sprite)
            my_sprite.change_x = random.random() * 5
            my_sprite.center_y = y

    def on_draw(self):
        if self.filter_on:
            # Draw our stuff into the CRT filter
            self.bloom_filter.use()
            self.bloom_filter.clear()
            self.sprite_list.draw()
            # arcade.draw_lrbt_rectangle_outline(
            # 0, self.width - 25, 0, self.height - 5, arcade.color.WHITE, 5)

            # Switch back to our window and draw the CRT filter do
            # draw its stuff to the screen
            self.use()
            self.clear()

            self.bloom_filter.draw()

        else:
            # Draw our stuff into the screen
            self.use()
            self.clear()
            self.sprite_list.draw()

    def on_update(self, dt):
        # Keep track of elapsed time
        self.sprite_list.update()
        self.sprite_list.update_animation(dt)
        for sprite in self.sprite_list:
            if sprite.left > self.width and sprite.change_x > 0:
                sprite.right = 0
            if sprite.right < 0 and sprite.change_x < 0:
                sprite.left = self.width

    def on_key_press(self, key, mod):
        if key == arcade.key.SPACE:
            self.filter_on = not self.filter_on


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
