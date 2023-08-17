import arcade, pyglet

def _attempt_font_name_resolution(font_name):
    """
    Attempt to resolve a tuple of font names.

    Preserves the original logic of this section, even though it
    doesn't seem to make sense entirely. Comments are an attempt
    to make sense of the original code.

    If it can't resolve a definite path, it will return the original
    argument for pyglet to attempt to resolve. This is consistent with
    the original behavior of this code before it was encapsulated.

    :param Union[str, Tuple[str, ...]] font_name:
    :return: Either a resolved path or the original tuple
    """
    if font_name:

        # ensure
        if isinstance(font_name, str):
            font_list: Tuple[str, ...] = (font_name,)
        elif isinstance(font_name, tuple):
            font_list = font_name
        else:
            raise TypeError("font_name parameter must be a string, or a tuple of strings that specify a font name.")

        for font in font_list:
            try:
                path = resolve(font)
                # print(f"Font path: {path=}")

                # found a font successfully!
                return path.name

            except FileNotFoundError:
                pass

    # failed to find it ourselves, hope pyglet can make sense of it
    return font_name


class UsageAttempt(arcade.Window):

    def __init__(self, width: int = 320, height: int = 240):
        super().__init__(width=width, height=height)

        self.sprites = arcade.SpriteList()
        text_sprite = arcade.create_text_sprite(
            "First line\nsecond line",
            multiline=True,
            width=100,
        )
        text_sprite.position = self.width // 2, self.height // 2
        self.sprites.append(text_sprite)

        self._label = pyglet.text.Label(
            text="First line\nsecond line\nTHIRD Line",
            x = 200,
            y = 200,
            font_name="Arial",
            font_size=12,
            anchor_x="left",
            width=100,
            align="baseline",
            bold=True,
            italic=True,
            multiline=True,
        )

    def on_draw(self):
        self.clear()
        self.sprites.draw()

        window = arcade.get_window()
        with window.ctx.pyglet_rendering():
            self._label.draw()




if __name__ == "__main__":
    w = UsageAttempt()
    arcade.run()