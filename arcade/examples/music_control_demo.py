import arcade
import arcade.gui


class MyView(arcade.View):
    def __init__(self, my_window: arcade.Window):
        super().__init__(my_window)

        self.media_player = None
        self.paused = True
        self.songs = [":resources:music/funkyrobot.mp3",
                      ":resources:music/1918.mp3"]
        self.cur_song_index = 0

        self.my_music = arcade.load_sound(self.songs[self.cur_song_index])

        # This creates a "manager" for all our UI elements
        self.ui_manager = arcade.gui.UIManager(self.window)

        box = arcade.gui.UIBoxLayout(vertical=False)

        # --- Start button
        normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/"
                                             "sound_off.png")
        hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/"
                                            "sound_off.png")
        press_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/"
                                            "sound_off.png")

        # Create our button
        self.start_button = arcade.gui.UITextureButton(
            texture=normal_texture,
            texture_hovered=hover_texture,
            texture_pressed=press_texture,
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.start_button.on_click = self.start_button_clicked  # type: ignore

        # Add in our element.
        box.add(self.start_button)

        # --- Down button
        press_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/down.png")
        normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/down.png")
        hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/down.png")

        # Create our button
        self.down_button = arcade.gui.UITextureButton(
            texture=normal_texture,
            texture_hovered=hover_texture,
            texture_pressed=press_texture,
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.down_button.on_click = self.volume_down  # type: ignore
        self.down_button.scale(0.5)

        # Add in our element.
        box.add(self.down_button)

        # --- Up button
        press_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/up.png")
        normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/up.png")
        hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/up.png")

        # Create our button
        self.up_button = arcade.gui.UITextureButton(
            texture=normal_texture,
            texture_hovered=hover_texture,
            texture_pressed=press_texture,
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.up_button.on_click = self.volume_up  # type: ignore
        self.up_button.scale(0.5)

        # Add in our element.
        box.add(self.up_button)

        # --- Right button
        press_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/right.png")
        normal_texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/right.png")
        hover_texture = arcade.load_texture(":resources:onscreen_controls/shaded_dark/right.png")

        # Create our button
        self.right_button = arcade.gui.UITextureButton(
            texture=normal_texture,
            texture_hovered=hover_texture,
            texture_pressed=press_texture,
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.right_button.on_click = self.forward  # type: ignore
        self.right_button.scale(0.5)

        # Add in our element.
        box.add(self.right_button)

        # Place buttons in the center of the screen using an UIAnchorWidget with default values
        self.ui_manager.add(arcade.gui.UIAnchorWidget(child=box))

    def music_over(self):
        self.media_player.pop_handlers()
        self.media_player = None
        self.sound_button_off()
        self.cur_song_index += 1
        if self.cur_song_index >= len(self.songs):
            self.cur_song_index = 0
        self.my_music = arcade.load_sound(self.songs[self.cur_song_index])
        self.media_player = self.my_music.play()
        self.media_player.push_handlers(on_eos=self.music_over)

    def volume_down(self, *_):
        if self.media_player and self.media_player.volume > 0.2:
            self.media_player.volume -= 0.2

    def volume_up(self, *_):
        if self.media_player and self.media_player.volume < 1.0:
            self.media_player.volume += 0.2

    def forward(self, *_):
        skip_time = 10

        if self.media_player and self.media_player.time < self.my_music.get_length() - skip_time:
            self.media_player.seek(self.media_player.time + 10)

    def sound_button_on(self):
        self.start_button.texture_pressed = \
            arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_on.png")
        self.start_button.texture = \
            arcade.load_texture(":resources:onscreen_controls/flat_dark/sound_on.png")
        self.start_button.texture_hovered = \
            arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_on.png")

    def sound_button_off(self):
        self.start_button.texture_pressed = \
            arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_off.png")
        self.start_button.texture = \
            arcade.load_texture(":resources:onscreen_controls/flat_dark/sound_off.png")
        self.start_button.texture_hovered = \
            arcade.load_texture(":resources:onscreen_controls/shaded_dark/sound_off.png")

    def start_button_clicked(self, *_):
        self.paused = False
        if not self.media_player:
            # Play button has been hit, and we need to start playing from the beginning.
            self.media_player = self.my_music.play()
            self.media_player.push_handlers(on_eos=self.music_over)
            self.sound_button_on()
        elif not self.media_player.playing:
            # Play button hit, and we need to un-pause our playing.
            self.media_player.play()
            self.sound_button_on()
        elif self.media_player.playing:
            # We are playing music, so pause.
            self.media_player.pause()
            self.sound_button_off()

    def on_draw(self):
        self.clear()

        # This draws our UI elements
        self.ui_manager.draw()
        arcade.draw_text("Music Demo",
                         start_x=0, start_y=self.window.height - 55,
                         width=self.window.width,
                         font_size=40,
                         align="center",
                         color=arcade.color.BLACK)

        if self.media_player:
            seconds = self.media_player.time
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            arcade.draw_text(f"Time: {minutes}:{seconds:02}",
                             start_x=10, start_y=10, color=arcade.color.BLACK, font_size=24)
            volume = self.media_player.volume
            arcade.draw_text(f"Volume: {volume:3.1f}",
                             start_x=10, start_y=50, color=arcade.color.BLACK, font_size=24)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ALMOND)

        # Registers handlers for GUI button clicks, etc.
        # We don't really use them in this example.
        self.ui_manager.enable()

    def on_hide_view(self):
        # This unregisters the manager's UI handlers,
        # Handlers respond to GUI button clicks, etc.
        self.ui_manager.disable()


if __name__ == "__main__":
    window = arcade.Window(title="Arcade Music Control Demo")
    window.show_view(MyView(window))
    arcade.run()
