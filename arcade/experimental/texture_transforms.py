import random

import arcade
from arcade.texture import transforms

TEST_TEXTURE_PATH = ":resources:images/test_textures/xy_square.png"
TRANSFORMS = [
    transforms.Rotate90Transform,
    transforms.Rotate180Transform,
    transforms.Rotate270Transform,
    transforms.FlipLeftRightTransform,
    transforms.FlipTopBottomTransform,
    transforms.TransposeTransform,
    transforms.TransverseTransform,
]


class App(arcade.Window):
    def __init__(self):
        super().__init__(1200, 600, "Atlas Revamp Check")
        paths = [
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk1.png",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk2.png",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk3.png",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk4.png",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk5.png",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk6.png",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk7.png",
        ]
        self.textures = [arcade.load_texture(path) for path in paths]
        self.spritelist = arcade.SpriteList()
        for i, tex in enumerate(self.textures):
            self.spritelist.append(arcade.Sprite(tex, center_x=100 + 130 * i, center_y=300))

        for i in range(len(TRANSFORMS)):
            sprite = self.spritelist[i]
            sprite.texture = sprite.texture.transform(TRANSFORMS[i])
            sprite.sync_hit_box_to_texture()

    def on_draw(self):
        self.clear()
        self.spritelist.draw()
        self.spritelist.draw_hit_boxes(color=arcade.color.RED, line_thickness=2)

    def on_key_press(self, symbol: int, modifiers: int):
        for sprite in self.spritelist:
            sprite.texture = sprite.texture.transform(random.choice(TRANSFORMS))
            sprite.sync_hit_box_to_texture()


App().run()
