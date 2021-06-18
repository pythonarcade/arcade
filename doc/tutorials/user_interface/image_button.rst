Image Buttons
=============

.. code-block:: python

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
            size_hint=(20, 20)
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.start_button.on_click = self.start_button_clicked

        # Add in our element.
        self.ui_manager.add_ui_element(self.start_button)