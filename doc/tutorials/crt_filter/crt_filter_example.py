import arcade
from arcade.experimental.crt_filter import CRTFilter
from pyglet.math import Vec2


# Store our screen dimensions & title in a convenient place
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1100
SCREEN_TITLE = "ShaderToy Demo"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)

        # Create the crt filter
        self.crt_filter = CRTFilter(width, height,
                                    resolution_down_scale=6.0,
                                    hard_scan=-8.0,
                                    hard_pix=-3.0,
                                    display_warp=Vec2(1.0 / 32.0, 1.0 / 24.0),
                                    mask_dark=0.5,
                                    mask_light=1.5)

        self.filter_on = True

        # Create some stuff to draw on the screen
        self.sprite_list = arcade.SpriteList()

        full = arcade.Sprite("Pac-man.png")
        full.center_x = width / 2
        full.center_y = height / 2
        full.scale = width / full.width
        self.sprite_list.append(full)

        my_sprite = arcade.Sprite(
            "pac_man_sprite_sheet.png",
            scale=5, image_x=4, image_y=65, image_width=13, image_height=15)
        my_sprite.change_x = 1
        self.sprite_list.append(my_sprite)
        my_sprite.center_x = 100
        my_sprite.center_y = 300

        my_sprite = arcade.Sprite(
            "pac_man_sprite_sheet.png",
            scale=5, image_x=4, image_y=81, image_width=13, image_height=15)
        my_sprite.change_x = -1
        self.sprite_list.append(my_sprite)
        my_sprite.center_x = 800
        my_sprite.center_y = 200

        my_sprite = arcade.AnimatedTimeBasedSprite()
        texture = arcade.load_texture(
            "pac_man_sprite_sheet.png", x=4, y=1, width=13, height=15)
        frame = arcade.AnimationKeyframe(tile_id=0,
                                         duration=150,
                                         texture=texture)
        my_sprite.frames.append(frame)
        texture = arcade.load_texture(
            "pac_man_sprite_sheet.png", x=20, y=1, width=13, height=15)
        frame = arcade.AnimationKeyframe(tile_id=1,
                                         duration=150,
                                         texture=texture)
        my_sprite.frames.append(frame)

        my_sprite.change_x = 1
        self.sprite_list.append(my_sprite)
        my_sprite.center_x = 0
        my_sprite.center_y = 300
        my_sprite.texture = texture
        my_sprite.scale = 5.0

    def on_draw(self):
        if self.filter_on:
            # Draw our stuff into the CRT filter instead of on screen
            self.crt_filter.use()
            self.crt_filter.clear()
            self.sprite_list.draw()

            # Next, switch back to the screen and dump the contents of
            # the CRT filter to it.
            self.use()
            self.clear()
            self.crt_filter.draw()
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
