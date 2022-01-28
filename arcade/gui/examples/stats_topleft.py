import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIAnchorWidget, UIBoxLayout, UILabel


class UINumberLabel(UILabel):
    _value: float = 0

    def __init__(self, value=0, format="{value:.0f}", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = format
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.text = self.format.format(value=value)
        self.fit_content()


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)

        # Init UIManager
        self.manager = UIManager()
        self.manager.enable()

        # Set background
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create value labels
        self.timer = UINumberLabel()
        wood = UINumberLabel(10)
        stone = UINumberLabel(20)
        food = UINumberLabel(30)

        # Create a vertical BoxGroup to align labels
        self.columns = UIBoxLayout(
            vertical=False,
            children=[
                # Create one vertical UIBoxLayout per column and add the labels
                UIBoxLayout(vertical=True, children=[
                    UILabel(text="Time:", width=50),
                    UILabel(text="Wood:", width=50),
                    UILabel(text="Stone:", width=50),
                    UILabel(text="Food:", width=50),
                ]),
                # Create one vertical UIBoxLayout per column and add the labels
                UIBoxLayout(vertical=True, children=[
                    self.timer,
                    wood,
                    stone,
                    food
                ]),
            ])

        # Use a UIAnchorWidget to place the UILabels in the top left corner
        self.manager.add(UIAnchorWidget(
            align_x=10,
            anchor_x="left",
            align_y=-10,
            anchor_y="top",
            child=self.columns
        ))

    def on_update(self, delta_time: float):
        self.timer.value += delta_time

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = UIMockup()
arcade.run()
