import arcade


class Test():
    def __init__(self):
        # setup
        my_sprite = arcade.Sprite()
        hit_box = [-10, -10], [-10, 10], [10, 10], [10, -10]
        my_sprite.set_hit_box(hit_box)
        my_sprite.scale = 1.0
        my_sprite.angle = 0
        my_sprite.center_x = 100
        my_sprite.center_y = 100

        print()
        hitbox = my_sprite.get_adjusted_hit_box()
        print(f'Hitbox: {my_sprite.scale} -> {my_sprite._points} -> {hitbox}')
        assert hitbox == [[90, 90], [90, 110], [110, 110], [110, 90]]

        my_sprite.scale = 0.5
        hitbox = my_sprite.get_adjusted_hit_box()
        print(f'Hitbox: {my_sprite.scale} -> {my_sprite._points} -> {hitbox}')
        assert hitbox == [[95, 95], [95, 105], [105, 105], [105, 95]]

        my_sprite.scale = 1
        hitbox = my_sprite.get_adjusted_hit_box()
        print(f'Hitbox: {my_sprite.scale} -> {my_sprite._points} -> {hitbox}')
        assert hitbox == [[90, 90], [90, 110], [110, 110], [110, 90]]

        my_sprite.scale = 2.0
        hitbox = my_sprite.get_adjusted_hit_box()
        print(f'Hitbox: {my_sprite.scale} -> {my_sprite._points} -> {hitbox}')
        assert hitbox == [[80, 80], [80, 120], [120, 120], [120, 80]]

        my_sprite.scale = 2.0
        hitbox = my_sprite.get_adjusted_hit_box()
        print(f'Hitbox: {my_sprite.scale} -> {my_sprite._points} -> {hitbox}')
        assert hitbox == [[80, 80], [80, 120], [120, 120], [120, 80]]


def test_sprite():
    Test()