from collections import defaultdict
import arcade


WIDTH = 640
HEIGHT = 480
SPRITE_SPEED = 5
SPRITE_SCALE = 0.5
keys_pressed = defaultdict(bool)


player = arcade.Sprite(filename="images/character_sprites/character0.png",
                       center_x=WIDTH//2,
                       center_y=HEIGHT//2,
                       scale=SPRITE_SCALE)

sprite1 = arcade.Sprite(filename="images/character_sprites/character2.png",
                        center_x=1*WIDTH//4,
                        center_y=HEIGHT//2,
                        scale=SPRITE_SCALE)

sprite2 = arcade.Sprite(filename="images/character_sprites/character3.png",
                        center_x=1*WIDTH//3,
                        center_y=HEIGHT//2,
                        scale=SPRITE_SCALE)

sprite3 = arcade.Sprite(filename="images/character_sprites/character4.png",
                        center_x=2*WIDTH//3,
                        center_y=HEIGHT//2,
                        scale=SPRITE_SCALE)

sprite4 = arcade.Sprite(filename="images/character_sprites/character5.png",
                        center_x=3*WIDTH//4,
                        center_y=HEIGHT//2,
                        scale=SPRITE_SCALE)


sprites = arcade.SpriteList()
sprites.append(player)
sprites.append(sprite1)
sprites.append(sprite2)
sprites.append(sprite3)
sprites.append(sprite4)


def setup():
    arcade.open_window(WIDTH, HEIGHT, "My Arcade Game")
    arcade.set_background_color(arcade.color.SKY_BLUE)
    arcade.schedule(update, 1/80)

    # Override arcade window methods
    window = arcade.get_window()
    window.on_draw = draw
    window.on_key_press = on_key_press
    window.on_key_release = on_key_release

    arcade.run()


def update(delta_time):

    if keys_pressed[arcade.key.A]:  # left
        player.position.x += -SPRITE_SPEED
        sprite1.position += -SPRITE_SPEED, 0
        sprite2.position[0] = 0
        sprite3.velocity.x = -1
        sprite4.center_x += -SPRITE_SPEED
    elif keys_pressed[arcade.key.D]:  # right
        player.position.x += SPRITE_SPEED
        sprite1.position += SPRITE_SPEED, 0
        sprite2.position[0] = WIDTH
        sprite3.velocity.x = 1
        sprite4.center_x += SPRITE_SPEED

    if keys_pressed[arcade.key.W]:  # up
        player.position.y += SPRITE_SPEED
        sprite1.position += 0, SPRITE_SPEED
        sprite2.position[1] = HEIGHT
        sprite3.velocity.y = 1
        sprite4.center_y += SPRITE_SPEED
    elif keys_pressed[arcade.key.S]:  # down
        player.position.y += -SPRITE_SPEED
        sprite1.position += 0, -SPRITE_SPEED
        sprite2.position[1] = 0
        sprite3.velocity.y = -1
        sprite4.center_y += -SPRITE_SPEED

    sprites.update()


def draw():
    arcade.start_render()
    sprites.draw()


def on_key_press(key, modifiers):
    keys_pressed[key] = True


def on_key_release(key, modifiers):
    keys_pressed[key] = False


def on_mouse_press(x, y, button, modifiers):
    pass


if __name__ == '__main__':
    setup()
