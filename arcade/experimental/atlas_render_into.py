"""
Render into a sub-section of a texture atlas
"""

import math

import arcade


class AtlasRenderDemo(arcade.Window):
    def __init__(self):
        super().__init__(1280, 720, "Atlas Render Demo")
        self.atlas = arcade.DefaultTextureAtlas((600, 600))

        self.texture_1 = arcade.Texture.create_empty("render_area_1", size=(256, 256))
        self.texture_2 = arcade.Texture.create_empty("render_area_2", size=(256, 256))
        self.sprite_1 = arcade.Sprite(self.texture_1, center_x=400, center_y=360)
        self.sprite_2 = arcade.Sprite(self.texture_2, center_x=850, center_y=360)

        self.spritelist = arcade.SpriteList(atlas=self.atlas)
        self.spritelist.extend([self.sprite_1, self.sprite_2])

        self.elapsed_time = 0
        self.frame = 0

    def on_draw(self):
        self.clear()
        self.render_into_sprite_texture()
        self.spritelist.draw()

    def render_into_sprite_texture(self):
        # Render shape into texture atlas in the first sprite texture's space
        with self.spritelist.atlas.render_into(self.texture_1) as fbo:
            fbo.clear(color=(255, 0, 0, 255))
            arcade.draw_rect_filled(
                arcade.rect.XYWH(128, 128, 160, 160),
                arcade.color.WHITE,
                self.elapsed_time * 100,
            )

        # Render a shape into the second texture in the atlas
        with self.spritelist.atlas.render_into(self.texture_2) as fbo:
            fbo.clear(color=(0, 255, 0, 255))
            arcade.draw_circle_filled(
                128,
                128,
                80 + math.sin(self.elapsed_time) * 30,
                arcade.color.BLUE,
            )

        self.sprite_1.angle = self.elapsed_time * 66
        self.sprite_2.angle = self.elapsed_time * 56

        self.frame += 1

    def on_update(self, delta_time: float):
        self.elapsed_time += delta_time


window = AtlasRenderDemo()
arcade.run()
