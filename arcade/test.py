import arcade
import PIL

arcade.open_window(600, 600, "Drawing Example")

arcade.set_background_color(arcade.color.WHITE)

arcade.start_render()

image = PIL.Image.new("RGBA", (10, 10))
text_sprite = arcade.Sprite()
text_sprite.texture = arcade.Texture("test")
text_sprite.texture.image = image

text_sprite.draw()

arcade.finish_render()

# Keep the window up until someone closes it.
arcade.run()
