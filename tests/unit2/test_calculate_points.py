import arcade

def test_calculate_points():
    texture = arcade.load_texture(":resources:images/items/coinGold.png")
    result = arcade.calculate_points(texture.image)
    print(result)

    texture = arcade.load_texture(":resources:images/animated_characters/female_person/character_femalePerson_idle.png")
    result = arcade.calculate_points(texture.image)
    print(result)
