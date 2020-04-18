import arcade

def test():

    height = 2
    width = 2
    wall = arcade.SpriteSolidColor(width, height, arcade.color.RED)
    wall.position = 0, 0

    assert wall.height == height
    assert wall.width == width
    assert wall.top == height / 2
    assert wall.bottom == -height / 2
    assert wall.left == -width / 2
    assert wall.right == width / 2
    hit_box = wall.get_hit_box()
    assert hit_box[0] == (-width / 2, -height / 2)
    assert hit_box[1] == (width / 2, -height / 2)
    assert hit_box[2] == (width / 2, height / 2)
    assert hit_box[3] == (-width / 2, height / 2)

    height = 128
    width = 128
    wall = arcade.SpriteSolidColor(width, height, arcade.color.RED)
    wall.position = 0, 0

    assert wall.height == height
    assert wall.width == width
    assert wall.top == height / 2
    assert wall.bottom == -height / 2
    assert wall.left == -width / 2
    assert wall.right == width / 2
    hit_box = wall.get_hit_box()
    assert hit_box[0] == (-width / 2, -height / 2)
    assert hit_box[1] == (width / 2, -height / 2)
    assert hit_box[2] == (width / 2, height / 2)
    assert hit_box[3] == (-width / 2, height / 2)

    height = 128
    width = 128
    wall = arcade.Sprite(":resources:images/tiles/dirtCenter.png")
    wall.position = 0, 0

    assert wall.height == height
    assert wall.width == width
    assert wall.top == height / 2
    assert wall.bottom == -height / 2
    assert wall.left == -width / 2
    assert wall.right == width / 2
    hit_box = wall.get_hit_box()
    assert hit_box[0] == (-width / 2, -height / 2)
    assert hit_box[1] == (width / 2, -height / 2)
    assert hit_box[2] == (width / 2, height / 2)
    assert hit_box[3] == (-width / 2, height / 2)

    wall = arcade.Sprite(":resources:images/items/coinGold.png")
    wall.position = 0, 0

    hit_box = wall.get_hit_box()
    assert hit_box == ((-32.0, -15.0), (-15.0, -32.0), (15.0, -32.0), (32.0, -15.0), (32.0, 14.0), (14.0, 32.0), (-15.0, 32.0), (-32.0, 15.0))
