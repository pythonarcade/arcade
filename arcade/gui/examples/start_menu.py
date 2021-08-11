import arcade
from arcade.gui import UIManager
from arcade.gui.events import UIOnClickEvent
from arcade.gui.widgets import UIAnchorWidget, UIBoxGroup, UIFlatButton


class QuitButton(UIFlatButton):
    def on_click(self, event: UIOnClickEvent):
        arcade.exit()


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        # Init UIManager
        self.manager = UIManager()
        self.manager.enable()

        # Set background
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = UIBoxGroup()

        # create StartButton, assign self.on_click_start as callback
        start_button = UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))
        start_button.on_click = self.on_click_start

        # create SettingsButton, assign a inline function as callback
        settings_button = UIFlatButton(text="Settings", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        @settings_button.event("on_click")
        def on_click_settings(event):
            print("Settings:", event)

        # create QuitButton, use overwritten class method as callback
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        self.manager.add(
            UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_click_start(self, event):
        print("Start:", event)

    def on_draw(self):
        arcade.start_render()
        self.manager.draw()


window = UIMockup()
arcade.run()
