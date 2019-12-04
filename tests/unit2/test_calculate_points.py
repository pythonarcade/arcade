import arcade
def test_calculate_points():
    texture = arcade.load_texture(":resources:images/items/coinGold.png")
    arcade.calculate_points(texture.image)
