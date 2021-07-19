import random
import arcade
from arcade.experimental import Shadertoy

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ShaderToy Demo"

SPRITE_SCALING = 0.25


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.time = 0
        file_name = "example.glsl"
        file = open(file_name)
        shader_sourcecode = file.read()
        size = width, height
        self.mouse_pos = 0, 0

        self.shadertoy = Shadertoy(size, shader_sourcecode)
        self.channel0 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture((width, height), components=4)]
        )
        self.shadertoy.channel_0 = self.channel0.color_attachments[0]

        self.channel1 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture((width, height), components=4)]
        )
        self.shadertoy.channel_1 = self.channel1.color_attachments[0]

        self.wall_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()

        # -- Set up several columns of walls
        for x in range(0, 1650, int(128 * SPRITE_SCALING * 3)):
            for y in range(0, 1600, int(128 * SPRITE_SCALING)):
                # Randomly skip a box so the player can find a way through
                if random.randrange(5) > 0:
                    sprite = arcade.Sprite(":resources:images/tiles/boxCrate_single.png", 0.25)
                    sprite.center_x = x
                    sprite.center_y = y
                    self.wall_list.append(sprite)

        for x in range(0, 1650, int(128 * SPRITE_SCALING)):
            for y in range(0, 1600, int(128 * SPRITE_SCALING)):
                sprite = arcade.Sprite(":resources:images/tiles/dirtCenter.png", 0.25)
                sprite.center_x = x
                sprite.center_y = y
                self.floor_list.append(sprite)

    def on_draw(self):
        self.channel0.use()
        self.wall_list.draw()

        self.channel1.use()
        self.floor_list.draw()

        self.use()
        self.shadertoy.render(time=self.time, mouse_position=self.mouse_pos)
        self.wall_list.draw()

    def on_update(self, dt):
        # Keep track of elapsed time
        self.time += dt

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_pos = x, y


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
