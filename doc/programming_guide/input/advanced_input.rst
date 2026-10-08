.. _pg_advanced_input:

Advanced Input
==============

Advanced Input in Arcade is handled through the use of an :class:`arcade.InputManager`

Key Concepts
------------

Actions
^^^^^^^

Actions are essentially named actions which can have inputs mapped to them. For example, you might have a ``Jump`` action
with the Spacebar and the bottom controller face button mapped to it. You can then subscribe a callback to this action, which
will be hit whenever the action is triggered, regardless of the underlying input source.

Axis Inputs
^^^^^^^^^^^

Axis Inputs are named inputs similar to actions, but are used for generally analog inputs or more "constant" inputs. These are
intended to be polled for their state, rather than being notified via a callback. Generally these inputs would be used to map onto
analog devices such as thumbsticks, or triggers on controllers, however as we will demonstrate later you can also use buttons or keyboard
input to control these. These inputs generally make it simple to handle something like movement with either keyboard input or a controller.

A Small Example
---------------

Create an InputManager
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    input_manager = arcade.InputManager()

    input_manager.new_action("Jump")
    input_manager.add_action_input("Jump", arcade.Keys.SPACE)
    input_manager.add_action_input("Jump", arcade.ControllerButtons.BOTTOM_FACE)

    input_manager.new_axis("Move")
    input_manager.add_axis_input("Move", arcade.Keys.LEFT, scale=-1.0)
    input_manager.add_axis_input("Move", arcade.Keys.RIGHT, scale=1.0)
    input_manager.add_axis_input("Move", arcade.ControllerAxes.LEFT_STICK_X, scale=1.0)

The above block of code demonstrates how you would create an :class:`arcade.InputManager` and create an action for jumping, and
an axis for moving. You'll notice for the movement axis, we assign the left and right keyboard keys with a different scale, but for the
controller input, we only define a positive scale value. This is because a controller feeds us analog input that might range anywhere from
-1.0 to 1.0. When the input is a controller axis, Arcade will multiply the input against the specified scale value, so in this example
using a scale of 1.0 means we get the exact value from the controller.

However when we assign keyboard keys, or buttons of any kind to an axis, all we know from the underlying input is wether that key/button is
pressed or not, but there is no value to multiply against a scale. In the case of a key/button being added to an axis input, Arcade will
use the scale specified as the value for the axis.

Handling the Jump Action
^^^^^^^^^^^^^^^^^^^^^^^^

For handling actions from our InputManager, we have two options:

- The global :meth:`arcade.Window.on_action` method which can be added to any :class:`arcade.Window`, :class:`arcade.View`, or :class:`arcade.Section` and will receive notification of all actions.
- A callback function registered to our ``Jump`` action.

The global :meth:`arcade.Window.on_action` approach:

.. code-block:: python

    def on_action(self, action: str, state: arcade.ActionState):
        if (action == "Jump"):
            do_player_jump()

.. note::

    If you want to have the ``on_action`` function be on a class other than the Window, View, or Section. You can use :meth:`arcade.InputManager.register_action_handler` to
    explicitly register the function to the InputManager. However if the function is on the Window, View, or Section it will receive the actions automatically.

The callback function approach:

.. code-block:: python

    def handle_jump(state: arcade.ActionState):
        do_player_jump()

    input_manager.subscribe_to_action("Jump", handle_jump)

Handling the Move Axis
^^^^^^^^^^^^^^^^^^^^^^

For handling axis inputs, it is important that we make sure the input manager is being updated. You will need to manually do this as part of your :meth:`arcade.Window.on_update`
function, or via somewhere else that is called every update.

.. code-block:: python

    input_manager.update()

When the InputManager is updated, it will update the values of every Axis input within it. You can then poll it simply by using the :meth:`arcade.InputManager.axis` function.
Below is an example of getting the axis value and one way you might use it to move a player.

.. code-block::

    player.change_x = input_manager.axis("Move") * PLAYER_MOVEMENT_SPEED

Active Device Switching
-----------------------

One question you might have had, is that if we are handling inputs on the "Move" axis for both the keyboard and a controller, which devices input will be used?
The answer depends on a couple different factors.

It is possible to have never bound a controller to the InputManager, in which case the controller inputs will be ignored. If there is no controller bound, and the ``allow_keyboard`` option
of the InputManager has been set to false, then all Axis values will just return 0, and no actions will ever be triggered.

However in the scenario that ``allow_keyboard`` is true, and we have a controller bound, the InputManager has somewhat intelligent active device switching which will prioritize the last device that was used.
For example if the controller is currently active, and the user pressed a key on their keyboard, Arcade will switch the active device to the keyboard, so the controller input will be ignored for axis inputs.
If the player then presses a button on their controller, or moves a stick out of the deadzone, then it will switch back to the controller as the active device and ignore keyboard inputs.

Controller Binding and Multiple Players
---------------------------------------

One thing we haven't covered yet, is how the InputManager actually gets a controller bound to it. To keep the InputManager flexible, it does not do this automatically on it's own, and it is up to you to provide
a :class:`pyglet.input.Controller` object to it. See the full examples below for more code on how to create a new Controller.

Once you have a controller object, you can either bind it to an InputManager during creation by passing it to the ``controller`` argument. Or you can use the :meth:`arcade.InputManager.bind_controller` function after
the InputManager has been created. If you want to unbind the controller, you can use :meth:`arcade.InputManager.unbind_controller`.

If your game is intended to support multiple players via multiple controllers. The general idea is that you would have one InputManager per controller/player. A common approach to this would be to construct one InputManager
with all of your desired actions/axis inputs, and then create a new one using the :meth:`arcade.InputManager.from_existing` function, as shown below. This function will copy all of the actions/axis from the specified
InputManager into the new one, but ignore the controller binding, allowing you to bind a different controller to the newly created manager.

.. code-block:: python

    # Not real code, see Pyglet input docs for more on Controller management
    controller_one = Controller()
    controller_two = Controller()

    input_manager_one = arcade.InputManager(controller_one)
    input_manager_one.new_action("Jump")
    input_manager_one.add_action_input("Jump", arcade.Keys.SPACE)

    input_manager_two = arcade.InputManager.from_existing(input_manager_one, controller_two)