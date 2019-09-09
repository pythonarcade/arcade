import arcade
# from abc import ABC, abstractmethod


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
        self.active = True

    def draw(self):
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
    
    def on_press(self):
        pass

    def on_release(self):
        pass

    def check_mouse_press(self, x, y):
        if x > self.center_x + self.width / 2:
            return
        if x < self.center_x - self.width / 2:
            return
        if y > self.center_y + self.height / 2:
            return
        if y < self.center_y - self.height / 2:
            return
        self.on_press()

    def check_mouse_release(self, x, y):
        if self.pressed:
            self.on_release()


class DialogueBox:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.active = False
        self.button_list = []
        self.text_list = []

    def on_draw(self):
        try:
            if self.active:
                arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, self.color)
                for button in self.button_list:
                    button.draw()
                for text in self.text_list:
                    text.draw()
        except:
            pass

    def on_mouse_press(self, x, y, button, modifiers):
        try:
            for button in self.button_list:
                button.check_mouse_press(x, y)
        except:
            pass
    
    def on_mouse_release(self, x, y, button, modifiers):
        try:
            for button in self.button_list:
                button.check_mouse_release(x, y)
        except:
            pass
        

class Text:
    def __init__(self, text, x, y, color=arcade.color.BLACK, font_size=22, anchor_x="center",
                 anchor_y="center", width: int = 0,
                 align="center",
                 font_name=('Calibri', 'Arial'),
                 bold: bool = False,
                 italic: bool = False, rotation=0):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font_size = font_size
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.width = width
        self.align = align
        self.font_name = font_name
        self.bold = bold
        self.italic = italic
        self.rotation = rotation
        self.active = True

    def draw(self):
        arcade.draw_text(self.text, self.x, self.y, self.color, font_size=self.font_size,
        anchor_x=self.anchor_x,
        anchor_y=self.anchor_y,
        width=self.width, align=self.align,
        font_name=self.font_name, bold=self.bold,
        italic=self.italic, rotation=self.rotation)
