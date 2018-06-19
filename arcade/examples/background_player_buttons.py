import arcade
import typing

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 300


class Text:
    def __init__(self, text: str, x: int, y: int, font_size: int = 18,
                 font_color: str = arcade.color.BLACK,
                 font_width: int = 2000,
                 font_face: str = "Arial",
                 font_alignment: str = "left",
                 bold: bool = False,
                 italic: bool = False,
                 anchor_x: str = "left",
                 anchor_y: str = "top",
                 rotation: int = 0):
        self.text = text
        self.properties = {
            'start_x': x, 'start_y': y,
            'color': font_color,
            'font_size': font_size,
            'width': font_width,
            'align': font_alignment,
            'font_name': font_face,
            'bold': bold,
            'italic': italic,
            'anchor_x': anchor_x,
            'anchor_y': anchor_y,
            'rotation': rotation
        }

    def draw(self):
        arcade.draw_text(text=self.text, **self.properties)


class TextButton:
    """ Text-based button """

    def __init__(self,
                 center_x, center_y,
                 width, height,
                 text,
                 font_size=18,
                 font_face="Arial",
                 face_color=arcade.color.LIGHT_GRAY,
                 highlight_color=arcade.color.WHITE,
                 shadow_color=arcade.color.GRAY,
                 button_height=2):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.font_face = font_face
        self.pressed = False
        self.face_color = face_color
        self.highlight_color = highlight_color
        self.shadow_color = shadow_color
        self.button_height = button_height

    def draw(self) -> typing.NoReturn:
        """ Draw the button """
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width,
                                     self.height, self.face_color)

        if not self.pressed:
            color = self.shadow_color
        else:
            color = self.highlight_color

        # Bottom horizontal
        arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
                         self.center_x + self.width / 2, self.center_y - self.height / 2,
                         color, self.button_height)

        # Right vertical
        arcade.draw_line(self.center_x + self.width / 2, self.center_y - self.height / 2,
                         self.center_x + self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        if not self.pressed:
            color = self.highlight_color
        else:
            color = self.shadow_color

        # Top horizontal
        arcade.draw_line(self.center_x - self.width / 2, self.center_y + self.height / 2,
                         self.center_x + self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        # Left vertical
        arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
                         self.center_x - self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        x = self.center_x
        y = self.center_y
        if not self.pressed:
            x -= self.button_height
            y += self.button_height

        arcade.draw_text(self.text, x, y,
                         arcade.color.BLACK, font_size=self.font_size,
                         width=self.width, align="center",
                         anchor_x="center", anchor_y="center")

    def on_press(self) -> typing.NoReturn:
        self.pressed = True

    def on_release(self) -> typing.NoReturn:
        self.pressed = False

    @property
    def bounding_box(self) -> typing.Tuple[int, int, int, int]:
        return self.center_x - self.width / 2, \
               self.center_y - self.height / 2, \
               self.center_x + self.width / 2, \
               self.center_y + self.height / 2

    def contains(self, x: int, y: int) -> bool:
        box = self.bounding_box
        return box[0] < x < box[2] and box[3] > y > box[1]


class ActionButton(TextButton):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, func: typing.Callable,
                 font_size: int = 18,
                 font_face: str = "Arial",
                 face_color: arcade.color = arcade.color.LIGHT_GRAY,
                 highlight_color: arcade.color = arcade.color.WHITE,
                 shadow_color: arcade.color = arcade.color.GRAY,
                 button_height: int = 2, optional=None):
        super().__init__(x, y, width, height, text,
                         font_size=font_size,
                         font_face=font_face,
                         face_color=face_color,
                         highlight_color=highlight_color,
                         shadow_color=shadow_color,
                         button_height=button_height)
        self.opt = optional
        self._func = func

    def on_release(self, *args, **kwargs) -> typing.NoReturn:
        super().on_release()
        self._func(args, kwargs)


class MediaPlayer(arcade.Window):
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Media Player Example",
                 fullscreen=False, resizable=False):
        super(MediaPlayer, self).__init__(width, height, title, fullscreen=fullscreen, resizable=resizable)

        self.window_size = width, height

        self.__player = arcade.Player()
        self.__player.looping(True)

        self.drawables = {
            "static": arcade.ShapeElementList(),
            "dynamic": arcade.ShapeElementList(),
            "text": list(),
            "buttons": list()
        }

    def load_music(self, directory):
        self.__player.load_dir(directory)

    def play(self, *args, **kwargs):
        if len(args) == 1:
            self.__player.play(args[0])
        else:
            if "track" in kwargs.keys():
                self.__player.play(kwargs["track"])

    def on_draw(self) -> typing.NoReturn:
        self.clear()
        arcade.start_render()
        for key in self.drawables.keys():
            if type(self.drawables[key]) is arcade.ShapeElementList:
                self.drawables[key].draw()
            else:
                for item in self.drawables[key]:
                    item.draw()

    def update(self, delta_time: float) -> typing.NoReturn:
        for sprite in self.drawables["dynamic"]:
            sprite.update()

    def on_key_press(self, symbol: int, modifiers: int) -> typing.NoReturn:
        pass

    def on_key_release(self, symbol: int, modifiers: int) -> typing.NoReturn:
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> typing.NoReturn:
        pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int) -> typing.NoReturn:
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> typing.NoReturn:
        for button in self.drawables["buttons"]:
            if button.contains(x, y):
                button.on_press()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> typing.NoReturn:
        for button in self.drawables["buttons"]:
            if button.contains(x, y):
                button.on_release(button.opt)

    def main(self) -> typing.NoReturn:
        """
        Creates the environment to display the main menu after the game loads.
        """
        import os
        path = "c:\\" + os.path.join(*arcade.__file__.split("\\")[1:-1], "examples", "sounds")
        self.load_music(path)
        for index, track in enumerate(self.__player.music):
            y = int(self.window_size[1] - index * 65 - 50)
            self.drawables['buttons'].append(
                ActionButton(65, y, 100, 50, "{}".format(track), lambda args, kwargs: self.play(*args, **kwargs))
            )
            self.drawables['buttons'][-1].opt = track

        self.drawables['buttons'].append(
            ActionButton(300, 65, 100, 50, "Loop", lambda args, kwargs: self.__player.looping(not self.__player.loop))
        )


if __name__ == "__main__":
    mp = MediaPlayer()
    mp.main()
    arcade.run()
