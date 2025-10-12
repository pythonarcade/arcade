# Arcade Input Manager

This is an overview of how to use the new Arcade `InputManager` class.

## Key Concepts

- Enums are used heavily. There are new enums in the global Arcade namespace. Namely:
    
    - arcade.Keys - Keyboard Mappings. Same as original `arcade.keys` module, but now an enum.
    - arcade.MouseAxes - Mouse Axis. Contains two values of just `X` and `Y`.
    - arcade.MouseButtons - Mappings to the Pyglet mouse button values
    - arcade.ControllerButtons - Mappings to pyglet controller button names
    - arcade.ControllerAxes - Mappings to pyglet analog controller names
    - There are some more enums added within the `input.inputs` module, but they are largely internal

- `arcade.InputManager` is the primary user-facing class. Almost all interaction between a user and Arcade will happen through this class.

- Actions - A named action that can be taken, and have inputs mapped to it. For example, an action named "Jump" with the spacebar and the bottom controller face button mapped to it. Users can listen to a new special event for this, or subscribe callbacks to them.

- Axes - A named axis which can be used for more "constant" input that is intended to be polled instead of event-driven. Generally this feature is derived from analog inputs such as thumbsticks or triggers. These will be explained more below.

## A simple example

This example creates an InputManager that is modeled to support a basic platformer game. Supporting side-to-side movement and jumping.

```py
input_manager = arcade.InputManager()

input_manager.new_action("Jump")
input_manager.add_action_input("Jump", arcade.Keys.SPACE)
input_manager.add_action_input("Jump", arcade.ControllerButtons.BOTTOM_FACE)

input_manager.new_axis("Move")
input_manager.add_axis_input("Move", arcade.Keys.LEFT, scale=-1.0)
input_manager.add_axis_input("Move", arcade.Keys.RIGHT, scale=1.0)
input_manager.add_axis_input("Move", arcade.ControllerAxes.LEFT_STICK_X, scale=1.0)
```

The jump action here is fairly straightforward, so let's talk about the Move axis we've created here.

First we register two keyboard keys, LEFT and RIGHT, to it, each with a different scale. When you register a keyboard key to an axis input, the scale value that you set with it will be set literally when it is triggered.

So in this case, when we press the LEFT keyboard key, the value of our "Move" axis will be -1.0 literally, and for RIGHT it would be 1.0. This functionality is the same keyboard keys, controller buttons, and mouse buttons.

Conversely, when you register a `ControllerAxes` input to it, in our case the X axis of the left thumbstick. The analog value of that input is polled, and the scale value is multipled to it. So for example, if the value of the input is 0.5, and we had a scale value of 0.5, then the actual value of our "Move" axis will be 0.25.

## Using the example

In order to make use of the input manager we setup above, we need to do things, update/poll the axis, and receive an event for the jump action.

### Actions

For receiving the jump action we have a few options. One is that there is a global `on_action` function which can be put onto any `arcade.Window`, `arcade.View`, or `arcade.Section`:

```py
def on_action(self, action: str, state: arcade.ActionState):
    # Do something based on action name and state
```

The `arcade.ActionState` is an enum which has the values `PRESSED` and `RELEASED`. 

In addition to the global event, you can also add the `on_action` callback explicitly. This means it doesn't need to be on one of the above classes to be handled, as it doesn't go through Pyglet's event system.

```py
def on_action(self, action: str, state: arcade.ActionState):
    # Do something based on action name and state

# Set it during the constructor. Can pass a single callable here or a list of them
input_manager = arcade.InputManager(action_handlers=self.on_action)

# Set it after creation. Can also take a single callable or a list here
input_manager.register_action_handler(self.on_action)
```

### Axes

For handling the axis, we first need to make sure we tick the input manager. In the `on_update` function(or via something else that is called every update). The below should be run:

```py
input_manager.update()
```

Assuming the input manager has been ticked, it will have update to values for the various axis input values, and they can be polled by simply doing the below. You can for example poll the value(which in our case is between -1.0 and 1.0) and multiply it by a speed value to get the amount that a character should move.:

```py
# This returns a float
player.change_x = input_manager.axis("Move") * PLAYER_MOVEMENT_SPEED
```

A question you may ask yourself, is if I've registered inputs on the "Move" axis for both the keyboard and the controller, and the user has both devices active, which one will be used? This depends on a few factors:

If no controller is bound to the InputManager, then the keyboard will be used. However if the `allow_keyboard` option on the InputManager is set to False, then the keyboard/mouse will never be used, even if there is no controller. The value will simply return 0.

HOWEVER, the InputManager is fairly intelligent, and if it has both keyboard enabled, and has a controller bound, then the one which takes precedent is the last one which has been used, so for example, if the controller is the active device, and the user presses a key on the keyboard, the active device will be swapped to the keyboard. Then if the player presses a button on the controller or uses any of the inputs, the active device will be automatically swapped to the controller(analog inputs will only trigger if they are above the configured deadzone which defaults to 0.1).

## Handling Controllers and Multiple Players

One thing we haven't covered, is how the InputManager actually gets a controller bound to it. Currently, the InputManager does not do this on it's own, it is up to the user to provide an instance of `pyglet.input.Controller` to it.

This means the user can setup a `ControllerManager`, and listen for `on_connect` and `on_disconnect` events for controllers. The controller can be bound during the constructor of the InputManager, or later bound/removed with the `bind_controller` and `unbind_controller` functions.

The general idea for multiple players, is that each player would own it's own InputManager instance, but it is largely up to the user how to handle this.