"""
An experiment trying to bug out the geometry shader sprite culling.
If the culling algorithm is wrong sprites can disappear before they
leave the screen.

Simply run the program and move draw the sprites around using the mouse.
"""

from arcade.sprite import Sprite
import PIL
import arcade


class GeoCullingTest(arcade.Window):

    def __init__(self):
        super().__init__(800, 400, "Cull test", resizable=True)
        self.proj = self.ctx.projection_2d
        self.texture = arcade.Texture("weird_texture", image=PIL.Image.new("RGBA", (2048, 2), (255, 255, 255, 255)))

        self.spritelist = arcade.SpriteList()
        self.spritelist.append(Sprite(
            ":resources:images/tiles/boxCrate_double.png",
            center_x=400, center_y=300, scale=6)
        )
        for i in range(0, 360, 36):
            self.spritelist.append(
                arcade.Sprite(texture=self.texture, center_x=400, center_y=300, angle=i)
            )

        self.spritelist.append(Sprite(":resources:images/items/gold_1.png", center_x=400, center_y=300))

    def on_draw(self):
        self.clear()
        self.ctx.projection_2d = self.proj
        self.spritelist.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.proj = self.ctx.projection_2d

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        self.proj = (
            self.proj[0] - dx,
            self.proj[1] - dx,
            self.proj[2] - dy,
            self.proj[3] - dy,
        )


window = GeoCullingTest()
arcade.run()
