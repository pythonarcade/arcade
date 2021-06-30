"""
Render into a sub-section of a texture atlas
"""
import math
import arcade
import PIL


class AtlasRenderDemo(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Atlas Render Demo")
        self.ctx.atlas_size = (600, 600)

        # Empty dummy image to reseve space in the atlas
        dummy_image = PIL.Image.new("RGBA", (256, 256), (255, 0, 0, 255))
        self.texture_1 = arcade.Texture("render_area_1", image=dummy_image, hit_box_algorithm=None)
        self.texture_2 = arcade.Texture("render_area_2", image=dummy_image, hit_box_algorithm=None)
        self.sprite_1 = arcade.Sprite(center_x=200, center_y=300)
        self.sprite_2 = arcade.Sprite(center_x=600, center_y=300)
        self.sprite_1.texture = self.texture_1
        self.sprite_2.texture = self.texture_2

        self.spritelist = arcade.SpriteList()
        self.spritelist.append(self.sprite_1)
        self.spritelist.append(self.sprite_2)

        self.elapsed_time = 0
        self.frame = 0

    def on_draw(self):
        self.clear()
        self.render_into_sprite_texture()
        self.spritelist.draw()

    def render_into_sprite_texture(self):
        # Render shape into texture atlas in the first sprite texture's space
        with self.spritelist.atlas.render_into(self.texture_1) as fbo:
            proj_old = self.ctx.projection_2d
            target_size = self.texture_1.image.size
            self.ctx.projection_2d = 0, target_size[0], 0, target_size[1]
            fbo.clear((255, 0, 0, 255))
            arcade.draw_rectangle_filled(128, 128, 160, 160, arcade.color.WHITE, self.elapsed_time * 100)
            self.ctx.projection_2d = proj_old

        # Render a shape into the second texture in the atlas
        with self.spritelist.atlas.render_into(self.texture_2) as fbo:
            proj_old = self.ctx.projection_2d
            target_size = self.texture_2.image.size
            self.ctx.projection_2d = 0, target_size[0], 0, target_size[1]
            fbo.clear((0, 255, 0, 255))
            arcade.draw_circle_filled(
                128,
                128,
                80 + math.sin(self.elapsed_time) * 30,
                arcade.color.BLUE,
            )
            self.ctx.projection_2d = proj_old

        self.sprite_1.angle = self.elapsed_time * 66
        self.sprite_2.angle = self.elapsed_time * 56

        self.frame += 1

    def on_update(self, delta_time: float):
        self.elapsed_time += delta_time


window = AtlasRenderDemo()
arcade.run()
