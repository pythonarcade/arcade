import arcade
import arcade.gui


class MyView(arcade.View):
    def __init__(self, my_window: arcade.Window):
        super().__init__(my_window)

        self.paused = False
        self.sprite_list = arcade.SpriteList()
        sprite = arcade.Sprite(":resources:images/enemies/fishGreen.png")
        self.sprite_list.append(sprite)

        # This creates a "manager" for all our UI elements
        self.ui_manager = arcade.gui.UIManager(self.window)

        # --- Start button
        press_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/start.png")
        normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_light/start.png")
        hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_light/start.png")

        # Create our button
        self.start_button = arcade.gui.UIImageButton(
            normal_texture=normal_texture,
            hover_texture=hover_texture,
            press_texture=press_texture,
            center_x=self.window.width / 2,
            center_y=self.window.height / 2,
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.start_button.on_click = self.start_button_clicked

        # Add in our element.
        self.ui_manager.add_ui_element(self.start_button)

        # --- Pause Button
        press_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/pause.png")
        normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_light/pause.png")
        hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_light/pause.png")

        # Create our button
        self.start_button = arcade.gui.UIImageButton(
            normal_texture=normal_texture,
            hover_texture=hover_texture,
            press_texture=press_texture,
            center_x=self.window.width / 2,
            center_y=self.window.height / 2 - normal_texture.height * 2,
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.start_button.on_click = self.pause_button_clicked

        # Add in our element.
        self.ui_manager.add_ui_element(self.start_button)

    def start_button_clicked(self):
        print("Start button has been clicked!")
        self.paused = False

    def pause_button_clicked(self):
        print("Pause button has been clicked!")
        self.paused = True

    def on_draw(self):
        arcade.start_render()

        self.sprite_list.draw()

        # This draws our elements
        self.ui_manager.on_draw()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ALMOND)

        # Registers handlers for GUI button clicks, etc.
        # We don't really use them in this example.
        self.ui_manager.enable()

    def on_hide_view(self):
        # This unregisters the manager's UI handlers,
        # Handlers respond to GUI button clicks, etc.
        self.ui_manager.disable()

    def on_update(self, delta_time: float):
        for sprite in self.sprite_list:
            sprite.center_x += 1


if __name__ == "__main__":
    window = arcade.Window(title="Arcade GUI Tutorial")
    window.show_view(MyView(window))
    arcade.run()
