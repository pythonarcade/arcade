"""
Example code showing how to create some of the different UIWidgets.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_widgets
"""
import arcade
import arcade.gui
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout
import arcade.gui.widgets.text


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "GUI Widgets Example", resizable=True)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.widgets.layout.UIBoxLayout(space_between=20)

        # Create a text label
        ui_text_label = arcade.gui.widgets.text.UITextArea(
            text="This is a Text Widget",
            width=450,
            height=40,
            font_size=24,
            font_name="Kenney Future",
        )
        self.v_box.add(ui_text_label)

        text = (
            "The real danger is not that computers will begin to think like people, "
            "but that people will begin "
            "to think like computers. - Sydney Harris (Journalist)"
        )
        ui_text_label = arcade.gui.widgets.text.UITextArea(
            text=text, width=450, height=60, font_size=12, font_name="Arial"
        )
        self.v_box.add(ui_text_label)

        # Create a UIFlatButton
        ui_flatbutton = arcade.gui.widgets.buttons.UIFlatButton(
            text="Flat Button", width=200
        )
        self.v_box.add(ui_flatbutton)

        # Handle Clicks
        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            print("UIFlatButton pressed", event)

        # Create a UITextureButton
        texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/play.png")
        ui_texture_button = arcade.gui.widgets.buttons.UITextureButton(texture=texture)

        # Handle Clicks
        @ui_texture_button.event("on_click")
        def on_click_texture_button(event):
            print("UITextureButton pressed", event)

        self.v_box.add(ui_texture_button)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.widgets.layout.UIAnchorLayout(children=[self.v_box])
        )

    def on_click_start(self, event):
        print("Start:", event)

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = MyWindow()
arcade.run()
