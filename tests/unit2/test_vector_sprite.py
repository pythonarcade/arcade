import os
import arcade


file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)


def test_vector_sprite():
    class MyTestWindow(arcade.Window):
        def __init__(self):
            super().__init__(width=640, height=480, title="Test window")
            arcade.set_background_color(arcade.color.WHITE)
            self.all_sprites = arcade.SpriteList()

            self.vsprite = arcade.VectorSprite("../../arcade/examples/images/coin_01.png")
            self.vsprite.position = [50, 70]             # set as list or tuple or...
            self.vsprite.velocity = arcade.Vector(1, 3)  # set as arcade.Vector

            assert type(self.vsprite.position) is arcade.Vector
            assert self.vsprite.center_x == 50
            assert self.vsprite.center_y == 70

            assert type(self.vsprite.velocity) is arcade.Vector
            assert self.vsprite.change_x == 1
            assert self.vsprite.change_y == 3

            self.all_sprites.append(self.vsprite)

        def update(self, deltatime):
            self.all_sprites.update()

        def on_draw(self):
            arcade.start_render()
            self.all_sprites.draw()

    window = MyTestWindow()
    window.test(frames=20)
    window.close()


def test_vector_sprite_unit_tests():
    # can create vector sprite object
    vs = arcade.VectorSprite()

    # Confirm new pos/vel types
    assert isinstance(vs.position, arcade.Vector)
    assert isinstance(vs.velocity, arcade.Vector)

    # can set position
    vs.position.x += 5
    assert vs.position.x == 5

    vs.position = arcade.Vector(17, 19)
    assert vs.position.x == 17
    assert vs.position.y == 19

    vs.position = 1, 3
    vs.position += 5, 7
    assert vs.position.x == 6
    assert vs.position.y == 10

    # test update position
    player = arcade.VectorSprite()
    player.position = 100, 100
    player.velocity = 5, 1
    player.update()
    assert player.position == (105, 101)
