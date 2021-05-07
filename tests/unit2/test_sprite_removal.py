import arcade

CHARACTER_SCALING = 0.5
frame = 0


def test_sprite_removal(window):
    global frame
    frame = 0
    arcade.set_background_color(arcade.color.AMAZON)

    character_list = arcade.SpriteList()

    sprite_1 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    sprite_1.center_x = 150
    sprite_1.center_y = 150
    character_list.append(sprite_1)

    sprite_2 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    sprite_2.center_x = 250
    sprite_2.center_y = 250
    character_list.append(sprite_2)

    sprite_3 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
    sprite_3.center_x = 250
    sprite_3.center_y = 250
    character_list.append(sprite_3)


    def on_draw():
        arcade.start_render()
        character_list.draw()

    def update(delta_time):
        global frame
        frame += 1

        if frame == 3:
            sprite_2.remove_from_sprite_lists()

        if frame == 5:
            character_list.remove(sprite_3)

        if frame == 7:
            sprite_2.center_x += 5

        if frame == 9:
            sprite_3.center_x += 5

    window.on_draw = on_draw
    window.update = update
    window.test()
    arcade.cleanup_texture_cache()
