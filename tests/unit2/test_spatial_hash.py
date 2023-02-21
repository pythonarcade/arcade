import arcade
from arcade.sprite_list.spatial_hash import SpatialHash


def test_create():
    sh = SpatialHash(cell_size=10)
    assert sh.cell_size == 10
    assert sh.contents == {}
    assert sh.buckets_for_sprite == {}
    assert sh.count == 0


def test_reset():
    sh = SpatialHash(cell_size=10)
    sh.insert_object_for_box(
        arcade.SpriteSolidColor(10, 10, color=arcade.color.RED),
    )
    assert sh.count == 1
    sh.reset()
    assert sh.count == 0


def test_add():
    sh = SpatialHash(cell_size=10)
    sh.insert_object_for_box(
        arcade.SpriteSolidColor(10, 10, color=arcade.color.RED),
    )
    print(sh.contents)
    print(sh.buckets_for_sprite)

    # assert False


# Around for running debugger on the module directly
if __name__ == "__main__":
    test_clear()
