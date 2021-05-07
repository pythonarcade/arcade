import arcade

CHARACTER_SCALING = 0.5

def test_sprite_scale(window):
    arcade.set_background_color(arcade.color.AMAZON)

    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    character_sprite.center_x = 150
    character_sprite.center_y = 150
    character_list.append(character_sprite)

    def on_draw():
        arcade.start_render()
        character_list.draw()

    def update(delta_time):
        character_sprite.scale += 0.1

    window.on_draw = on_draw
    window.update = update
    window.test()
    arcade.cleanup_texture_cache()
