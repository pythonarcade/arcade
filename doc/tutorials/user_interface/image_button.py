import arcade
import arcade.gui


class MyView(arcade.View):
    def __init__(self, my_window: arcade.Window):
        super().__init__(my_window)

        # Def sound status
        self.sound_on = False

        # This creates a "manager" for all our UI elements
        self.ui_manager = arcade.gui.UIManager(self.window, attach_callbacks=False)

        # Load textures for the image buttons. For normal, mouse-over, and click.
        press_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_off.png")
        normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/sound_off.png")
        hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_off.png")

        # Create our button
        self.start_button = arcade.gui.UIImageButton(
            normal_texture=normal_texture,
            hover_texture=hover_texture,
            press_texture=press_texture,
            center_x=self.window.width / 2,
            center_y=self.window.height / 2,
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.start_button.on_click = self.on_button_click

        # You can scale the button with the scale attribute
        self.start_button.scale = 1.25

        # Add in our element.
        self.ui_manager.add_ui_element(self.start_button)

    def on_button_click(self):
        print("Button has been clicked!")
        if self.sound_on:
            self.start_button.press_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_off.png")
            self.start_button.normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/sound_off.png")
            self.start_button.hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_off.png")
            self.sound_on = False
        else:
            self.start_button.press_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_on.png")
            self.start_button.normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/sound_on.png")
            self.start_button.hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_on.png")
            self.sound_on = True

    def on_draw(self):
        arcade.start_render()

        # This draws our elements
        self.ui_manager.on_draw()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        # Registers handlers for GUI button clicks, etc.
        # We don't really use them in this example.
        self.ui_manager.enable()

    def on_hide_view(self):
        # This unregisters the manager's UI handlers,
        # Handlers respond to GUI button clicks, etc.
        self.ui_manager.disable()


if __name__ == "__main__":
    window = arcade.Window(title="Arcade GUI Tutorial")
    window.show_view(MyView(window))
    arcade.run()
