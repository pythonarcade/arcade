from copy import deepcopy
from typing import Optional, List

import arcade
from arcade.gui.events import UIOnChangeEvent, UIOnClickEvent
from arcade.gui.widgets import UILayout, UIWidget
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout


class UIDropdown(UILayout):
    """
    A dropdown layout. When clicked displays a list of options provided.

    Triggers an event when an option is clicked, the event can be read by

    .. code:: py

        dropdown = Dropdown()

        @dropdown.event()
        def on_change(event: UIOnChangeEvent):
            print(event.old_value, event.new_value)
    
    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float width: Width of each of the option.
    :param float height: Height of each of the option.
    :param str default: The default value shown.
    :param list[str] options: The options displayed when the layout is clicked. 
    :param style: Used to style the dropdown.
    """
    DIVIDER = None

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        default: Optional[str] = None,
        options: Optional[List[str]] = None,
        style=None, **kwargs
    ):
        if style is None:
            style = {}

        # TODO handle if default value not in options or options empty
        if options is None:
            options = []
        self._options = options
        self._value = default

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            style=style,
            **kwargs)

        # Setup button showing value
        self._default_button = UIFlatButton(
            text=self._value, width=self.width, height=self.height
        )

        self._default_button.on_click = self._on_button_click  # type: ignore

        self._layout = UIBoxLayout()
        self._layout.visible = False
        self._update_options()

        # add children after super class setup
        self.add(self._default_button)
        self.add(self._layout)

        self.register_event_type("on_change")

        self.with_border(color=arcade.color.RED)

    @property
    def value(self):
        """Current selected option."""
        return self._value

    @value.setter
    def value(self, value):
        """Change the current selected option to a new option."""
        old_value = self._value
        self._value = value
        self._default_button.text = self._value

        self._update_options()
        self.dispatch_event("on_change", UIOnChangeEvent(self, old_value, value))
        self.trigger_render()

    def _update_options(self):
        # generate options
        self._layout.clear()

        # is there another way then deepcopy, does it matter? ("premature optimization is the root of all evil")
        active_style = deepcopy(UIFlatButton.DEFAULT_STYLE)
        active_style["normal"]["bg"] = (55, 66, 81)

        for option in self._options:
            if option == self.DIVIDER:
                self._layout.add(
                    UIWidget(width=self.width, height=2).with_background(
                        color=arcade.color.GRAY
                    )
                )
                continue

            button = self._layout.add(
                UIFlatButton(
                    text=option,
                    width=self.width,
                    height=self.height,
                    style=active_style
                    if self.value == option
                    else UIFlatButton.DEFAULT_STYLE,
                )
            )
            button.on_click = self._on_option_click

    def _on_button_click(self, event: UIOnClickEvent):
        self._layout.visible = not self._layout.visible
        if self.parent:
            print(self.parent)
            self.parent._update_size_hints()
            self.parent.do_layout()
            self.parent.trigger_render()


    def _on_option_click(self, event: UIOnClickEvent):
        source: UIFlatButton = event.source
        self.value = source.text
        self._layout.visible = False

    def do_layout(self):
        self._default_button.rect = self.rect

        # resize layout to contain widgets
        self._layout.rect = self._layout.rect \
            .resize(*self._layout.size_hint_min) \
            .align_top(self.bottom - 2) \
            .align_left(self._default_button.left)

    def on_change(self, event: UIOnChangeEvent):
        """To be implemented by the user, triggered when the current selected value is changed to a different option."""
        pass
