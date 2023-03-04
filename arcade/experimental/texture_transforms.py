from PIL import Image
import arcade

TEST_TEXTURE_PATH = ":resources:images/test_textures/xy_square.png"

class App(arcade.Window):

    def __init__(self):
        super().__init__(900, 600, "Atlas Revamp Check")
        # self.init_multi_image_test()
        self.init_hit_box_test()

    def init_single_image_test(self):
        self.atlas = arcade.TextureAtlas((128, 128))

        texture_1 = arcade.load_texture(TEST_TEXTURE_PATH)
        texture_2 = texture_1.rotate_90()
        texture_3 = texture_2.rotate_90()
        texture_4 = texture_3.rotate_90()

        # self.atlas.add(texture_1)
        # self.atlas.add(texture_2)
        # self.atlas.add(texture_3)
        # self.atlas.add(texture_4)

        self.spritelist = arcade.SpriteList(atlas=self.atlas)
        self.spritelist.append(arcade.Sprite(texture=texture_1, center_x=100, center_y=300))
        self.spritelist.append(arcade.Sprite(texture=texture_2, center_x=250, center_y=300))
        self.spritelist.append(arcade.Sprite(texture=texture_3, center_x=400, center_y=300))
        self.spritelist.append(arcade.Sprite(texture=texture_4, center_x=550, center_y=300))

        self.atlas.print_contents()

    def init_multi_image_test(self):
        self.atlas = arcade.TextureAtlas((260, 260))
        im_1 = Image.new("RGBA", (128, 128), (255, 0, 0, 255))
        im_2 = Image.new("RGBA", (128, 128), (0, 255, 0, 255))
        im_3 = Image.new("RGBA", (128, 128), (0, 0, 255, 255))
        im_4 = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
        im_5 = Image.new("RGBA", (128, 128), (255, 0, 255, 255))
        tex_1 = arcade.Texture(im_1)
        tex_2 = arcade.Texture(im_2)
        tex_3 = arcade.Texture(im_3)
        tex_4 = arcade.Texture(im_4)
        tex_5 = arcade.Texture(im_5)
        self.atlas.add(tex_1)
        self.atlas.add(tex_2)
        self.atlas.add(tex_3)
        self.atlas.add(tex_4)
        self.atlas.add(tex_5)

        self.spritelist = arcade.SpriteList(atlas=self.atlas)
        self.spritelist.extend([
            arcade.Sprite(texture=tex_1, center_x=100, center_y=300),
            arcade.Sprite(texture=tex_2, center_x=250, center_y=300),
            arcade.Sprite(texture=tex_3, center_x=400, center_y=300),
            arcade.Sprite(texture=tex_4, center_x=550, center_y=300),
            arcade.Sprite(texture=tex_5, center_x=400, center_y=100),
        ])

    def init_hit_box_test(self):
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
            self.spritelist.append(arcade.Sprite(tex, center_x=100 + 100 * i, center_y=300))

    def on_draw(self):
        self.clear()
        if hasattr(self, "spritelist"):
            self.spritelist.draw()
            self.spritelist.draw_hit_boxes(color=arcade.color.RED, line_thickness=2)

    def on_key_press(self, symbol: int, modifiers: int):
        for sprite in self.spritelist:
            # sprite.texture = sprite.texture.flip_left_to_right()
            # sprite.texture = sprite.texture.flip_top_to_bottom()
            # sprite.texture = sprite.texture.transverse()
            # sprite.texture = sprite.texture.rotate_90().transverse()
            # sprite.texture = sprite.texture.rotate_90()
            # sprite.angle += 90
            # sprite.texture = sprite.texture.rotate_180()
            # sprite.texture = sprite.texture.rotate_180()
            sprite.texture = sprite.texture.rotate_270()
            sprite._hit_box_points = None
            print("size", (sprite.width, sprite.height), "order", sprite.texture._vertex_order)


App().run()
