import arcade
from arcade.experimental.crt_filter import CRTFilter
from arcade.types.rect import LBWH
from pyglet.math import Vec2


# Store our screen dimensions & title in a convenient place
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1100
SCREEN_TITLE = "ShaderToy Demo"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=False)

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

        # Load the pac-man map image and scale it up to the window size
        map = arcade.Sprite("Pac-man.png", center_x=width / 2, center_y=height / 2)
        map.scale = width / map.width
        self.sprite_list.append(map)

        # Slice out some textures from the sprite sheet
        spritesheet = arcade.load_spritesheet("pac_man_sprite_sheet.png")
        ghost_red = spritesheet.get_texture(LBWH(4, 65, 13, 15))
        pink_ghost = spritesheet.get_texture(LBWH(4, 81, 13, 15))
        pacman_1 = spritesheet.get_texture(LBWH(4, 1, 13, 15))
        pacman_2 = spritesheet.get_texture(LBWH(20, 1, 13, 15))
        pacman_3 = spritesheet.get_texture(LBWH(36, 1, 13, 15))

        # Create sprite for the red ghost with some movement and add it to the sprite list
        sprite = arcade.Sprite(ghost_red, center_x=100, center_y=300, scale=5.0)
        sprite.change_x = 1
        self.sprite_list.append(sprite)

        # Create sprite for the pink ghost with some movement and add it to the sprite list
        sprite = arcade.Sprite(pink_ghost, center_x=800, center_y=200, scale=5.0)
        sprite.change_x = -1
        self.sprite_list.append(sprite)

        # Create an animated pacman sprite and add it to the sprite list
        keyframes = [
            arcade.TextureKeyframe(pacman_1, duration=100),
            arcade.TextureKeyframe(pacman_2, duration=100),
            arcade.TextureKeyframe(pacman_3, duration=100),
        ]
        sprite = arcade.TextureAnimationSprite(
            center_x=0,
            center_y=300,
            scale=5.0,
            animation=arcade.TextureAnimation(keyframes)
        )
        sprite.change_x = 1
        self.sprite_list.append(sprite)

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
