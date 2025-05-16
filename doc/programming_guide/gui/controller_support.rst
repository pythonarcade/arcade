.. _gui_controller_support:

GUI Controller Support
----------------------

The `arcade.gui` module now includes **experimental controller support**, allowing you to navigate through GUI elements using a game controller. This feature introduces the `ControllerWindow` and `ControllerView` classes, which provide controller-specific functionality.

Below is a guide on how to set up and use this feature effectively.

Basic Setup
~~~~~~~~~~~

To use controller support, you need to use the `ControllerWindow` and `ControllerView` classes.
These classes provide the necessary hooks for handling controller input and managing focus within the GUI.

The following code makes use of the `UIView` class, which simplifies the process of setting up a view with a `UIManager`.

Setting Up Controller Support
`````````````````````````````

The `ControllerWindow` is an instance of `arcade.Window` that integrates controller input handling. The `ControllerView` class provides controller-specific callbacks,
which are used by the `UIManager` to handle controller events.

Below is an example of how to set up a controller-enabled application:

.. code-block:: python

    import arcade
    from arcade.gui import UIView
    from arcade.experimental.controller_window import ControllerWindow, ControllerView


    class MyControllerView(ControllerView, UIView):
        def __init__(self):
            super().__init__()

            # Initialize your GUI elements here

        # react to controller events for your game
        def on_connect(self, controller):
            print(f"Controller connected: {controller}")

        def on_disconnect(self, controller):
            print(f"Controller disconnected: {controller}")

        def on_stick_motion(self, controller, stick, value):
            print(f"Stick {stick} moved to {value} on controller {controller}")

        def on_trigger_motion(self, controller, trigger, value):
            print(f"Trigger {trigger} moved to {value} on controller {controller}")

        def on_button_press(self, controller, button):
            print(f"Button {button} pressed on controller {controller}")

        def on_button_release(self, controller, button):
            print(f"Button {button} released on controller {controller}")

        def on_dpad_motion(self, controller, value):
            print(f"D-Pad moved to {value} on controller {controller}")


    if __name__ == "__main__":
        window = ControllerWindow(title="Controller Support Example")
        view = MyControllerView()
        window.show_view(view)
        arcade.run()


Managing Focus with `FocusGroups`
`````````````````````````````````

To enable controller navigation, you must group your interactive GUI elements into a `UIFocusGroup`.
A `UIFocusGroup` allows the controller to cycle through the elements and ensures that only one element is focused at a time.

A single `UIFocusGroup` can be added to the `UIManager` as a root widget acting as a `UIAnchorLayout`.

.. code-block:: python

    from arcade.experimental.controller_window import ControllerView, ControllerWindow
    from arcade.gui import UIFlatButton, UIBoxLayout, UIView
    from arcade.gui.experimental.focus import UIFocusGroup


    class MyControllerView(ControllerView, UIView):
        def __init__(self):
            super().__init__()

            # Create buttons and add them to the focus group
            fg = UIFocusGroup()
            self.ui.add(fg)

            box = UIBoxLayout()
            fg.add(box)

            button1 = UIFlatButton(text="Button 1", width=200)
            button2 = UIFlatButton(text="Button 2", width=200)

            box.add(button1)
            box.add(button2)

            # initialize the focus group, detect focusable widgets and set the initial focus
            fg.detect_focusable_widgets()
            fg.set_focus()


    if __name__ == "__main__":
        window = ControllerWindow(title="Controller Support Example")
        view = MyControllerView()
        window.show_view(view)
        window.run()


Setting Initial Focus
`````````````````````

It is essential to set the initial focus for the `UIFocusGroup`. Without this, the controller will not know which element to start with.

.. code-block:: python

            # Set the initial focus
            self.focus_group.set_focus()

Summary
```````
To use the experimental controller support in `arcade.gui`:

1. Use `ControllerWindow` as your main application window.
2. Use `ControllerView` to provide controller-specific callbacks for the `UIManager`.
3. Group interactive elements into a `UIFocusGroup` for navigation.
4. Set the initial focus for the `UIFocusGroup` to enable proper navigation.

This setup allows you to create a fully functional GUI that can be navigated using a game controller. Note that this feature is experimental and may be subject to changes in future releases.


Advanced Usage
~~~~~~~~~~~~~~

Nested `UIFocusGroups`
``````````````````````

When using nested `UIFocusGroups`, only one `UIFocusGroup` will be navigated at a time.
This is particularly useful for scenarios like modals or overlays, where you want to temporarily restrict navigation to
a specific set of elements. For example, the `UIDropdown` widget uses this feature to handle focus within its dropdown
menu while isolating it from the rest of the interface.


Advanced focus direction
````````````````````````

To provide a more advanced focus direction, you can use the `UIFocusable` class.

The `UIFocusable` class allows you to define directional neighbors (`neighbor_up`, `neighbor_down`, `neighbor_left`, `neighbor_right`) for a widget.
These neighbors determine how focus moves between widgets when navigating with a controller or keyboard.

Here is an example of how to use the `UIFocusable` class:

.. code-block:: python

    from arcade.gui import UIFlatButton, UIGridLayout
    from arcade.gui.experimental.focus import UIFocusGroup, UIFocusable

    class MyButton(UIFlatButton, UIFocusable):
        def __init__(self, text, width):
            super().__init__(text=text, width=width)


    # Create focusable buttons
    button1 = MyButton(text="Button 1", width=200)
    button2 = MyButton(text="Button 2", width=200)
    button3 = MyButton(text="Button 3", width=200)
    button4 = MyButton(text="Button 4", width=200)

    # Set directional neighbors
    button1.neighbor_right = button2
    button1.neighbor_down = button3
    button2.neighbor_left = button1
    button2.neighbor_down = button4
    button3.neighbor_up = button1
    button3.neighbor_right = button4
    button4.neighbor_up = button2
    button4.neighbor_left = button3

    # Add buttons to a focus group
    fg = UIFocusGroup()

    grid_layout = UIGridLayout(column_count=2, row_count=2, vertical_spacing=10)
    grid_layout.add(button1, col_num=0, row_num=0)
    grid_layout.add(button2, col_num=1, row_num=0)
    grid_layout.add(button3, col_num=0, row_num=1)
    grid_layout.add(button4, col_num=1, row_num=1)

    fg.add(grid_layout)

    # Detect focusable widgets and set the initial focus
    fg.detect_focusable_widgets()
    fg.set_focus(button1)

This setup allows you to define custom navigation paths between widgets, enabling more complex focus behavior.
