#  type: ignore
import random
from typing import Sequence

import pyglet
from pyglet.input import Controller

import arcade
from arcade.future.input import ActionState, ControllerAxes, ControllerButtons, InputManager, Keys

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FLOAT_HEIGHT = 80


# Default per-player textures
DEFAULT_TEXTURES = (
    ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
    ":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png",
    ":resources:images/animated_characters/robot/robot_idle.png",
    ":resources:images/animated_characters/zombie/zombie_idle.png",
)


class Player(arcade.Sprite):
    def __init__(
        self,
        texture,
        walls: arcade.SpriteList,
        input_manager_template: InputManager,
        controller: pyglet.input.Controller | None = None,
        center_x: float = 0.0,
        center_y: float = 0.0,
        x_max_speed: float = 300.0,
        y_jump_speed: float = 20.0,
    ):
        super().__init__(texture, center_x=center_x, center_y=center_y)
        self.x_max_velocity = x_max_speed
        self.y_jump_speed = y_jump_speed

        self.input_manager = InputManager(controller=controller, action_handlers=self.on_action)
        self.input_manager.copy_existing(input_manager_template)

        #
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, walls=walls, gravity_constant=1)

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.input_manager.update()
        self.change_x = self.input_manager.axis("Move") * self.x_max_velocity * delta_time
        self.physics_engine.update()

    def on_action(self, action: str, state: ActionState):
        if action == "Jump" and state == ActionState.PRESSED and self.physics_engine.can_jump():
            self.change_y = self.y_jump_speed


class Game(arcade.Window):
    def __init__(
        self,
        player_textures: Sequence[str] = DEFAULT_TEXTURES,
        max_players: int = 4,
        randomize_textures: bool = True,
    ):
        if not (1 < max_players <= 4):
            raise ValueError("max_players must between 1 and 4 (the maximum supported by XInput)")

        super().__init__(title="Input Example")

        self.player_textures = [t for t in player_textures]
        if randomize_textures:
            random.shuffle(self.player_textures)

        self._max_players = max_players
        self.key_to_player_index: dict[Keys, int] = {
            getattr(Keys, f"KEY_{i + 1}"): i for i in range(0, max_players)
        }

        self.players: list[Player | None] = []
        self.player_list = arcade.SpriteList()
        self.device_labels_batch = pyglet.graphics.Batch()
        self.player_device_labels: list[arcade.Text | None] = []

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        for x in range(0, self.width + 64, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        # This is an example of how to load an InputManager from a file. The parse function
        # accepts a dictionary, so anything such as toml, yaml, or json could be used to load
        # that dictionary. As long as it can handle a Python dictionary.
        #
        # with open("out.json", "r") as f:
        #     raw = json.load(f)
        # self.INPUT_TEMPLATE = arcade.InputManager.parse(raw)
        # self.INPUT_TEMPLATE.allow_keyboard = False

        self.INPUT_TEMPLATE = InputManager(allow_keyboard=False)
        self.INPUT_TEMPLATE.new_action("Jump")
        self.INPUT_TEMPLATE.add_action_input("Jump", Keys.SPACE)
        self.INPUT_TEMPLATE.add_action_input("Jump", ControllerButtons.BOTTOM_FACE)

        self.INPUT_TEMPLATE.new_axis("Move")
        self.INPUT_TEMPLATE.add_axis_input("Move", Keys.A, -1.0)
        self.INPUT_TEMPLATE.add_axis_input("Move", Keys.D, 1.0)
        self.INPUT_TEMPLATE.add_axis_input("Move", ControllerAxes.LEFT_STICK_X)

        # This is an example of how to dump an InputManager to a file. The serialize function
        # returns a dictionary, so anything such as toml, yaml, or json could be used to save
        # that dictionary. As long as it can handle a Python dictionary.
        #
        # serialized = self.INPUT_TEMPLATE.serialize()
        # with open("out.json", "w") as f:
        #     json.dump(serialized, f)

        self.controller_manager = pyglet.input.ControllerManager()
        self.controller_manager.set_handlers(self.on_connect, self.on_disconnect)

        for index, controller in enumerate(self.controller_manager.get_controllers()):
            self.add_player_for_controller(controller)

    def _get_first_player_slot_free(self) -> int | None:
        for i, player in self.players:
            if player is None:
                return i

        if len(self.players) < self._max_players:
            return len(self.players)

        return None

    def add_player_for_controller(self, controller: Controller) -> None:
        slot = self._get_first_player_slot_free()
        texture = self.player_textures[slot]
        print(f"got {slot=}, {texture=}")

        # Put the player in a random location
        player = Player(
            texture,
            center_x=random.randrange(0, self.width),
            center_y=128,
            walls=self.wall_list,
            input_manager_template=self.INPUT_TEMPLATE,
            controller=controller,
        )

        label_text = f"Player {slot + 1}\n({controller.device.name})"
        label = arcade.Text(
            label_text,
            player.center_x,
            player.center_y + FLOAT_HEIGHT,
            multiline=True,
            width=400,
            align="center",
            anchor_x="center",
            batch=self.device_labels_batch,
        )

        if slot == len(self.players):
            self.players.append(player)
            self.player_device_labels.append(label)
        else:
            self.players[slot] = player
            self.player_device_labels[slot] = label

        self.player_list.append(player)

    def on_connect(self, controller: pyglet.input.Controller):
        self.add_player_for_controller(controller)

    def on_disconnect(self, controller: pyglet.input.Controller):
        to_remove = None
        to_remove_index = -1

        for index, player in enumerate(self.players):
            if player.input_manager.controller == controller:
                to_remove = player
                to_remove_index = index
                break

        if to_remove is None:
            return

        to_remove.input_manager.unbind_controller()
        to_remove.kill()
        self.players[to_remove_index] = None
        # self.device_labels_batch.remove()
        self.player_device_labels[to_remove_index] = None

    def on_draw(self):
        self.clear()

        self.player_list.draw()
        self.wall_list.draw()
        self.device_labels_batch.draw()

    def on_key_press(self, key, modifiers):
        player_index = self.key_to_player_index.get(Keys(key), None)
        if player_index is None or player_index >= len(self.players):
            return

        # Give keyboard focus to player # N
        self.players[player_index].input_manager.allow_keyboard = True
        for index, player in enumerate(self.players):
            if index != player_index:
                player.input_manager.allow_keyboard = False

    def on_update(self, delta_time: float):
        self.player_list.update(delta_time)
        for label, player in zip(self.player_device_labels, self.players):
            position_x, position_y = player.position
            position_y += FLOAT_HEIGHT
            label.position = position_x, position_y


def main():
    Game()
    arcade.run()


if __name__ == "__main__":
    main()
