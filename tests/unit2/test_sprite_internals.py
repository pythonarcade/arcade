import arcade

def test_it_can_correctly_set_left_after_width_change_with_texture():
    sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_walk0.png")
    assert sprite.get_adjusted_hit_box() == [[a,b] for (a, b) in sprite._points]
    sprite.width *= 2
    sprite.height *= 2
    assert sprite.get_adjusted_hit_box() == [[a*2,b*2] for (a, b) in sprite._points]
