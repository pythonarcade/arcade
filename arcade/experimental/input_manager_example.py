#  type: ignore

import random
from typing import List, Optional

import pyglet

import arcade
from arcade.experimental import input

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class Player(arcade.Sprite):

    def __init__(
        self,
        walls: arcade.SpriteList,
        input_manager_template: input.InputManager,
        controller: Optional[pyglet.input.Controller] = None,
    ):
        super().__init__(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        )
        self.center_x = random.randint(0, WINDOW_WIDTH)
        self.center_y = 128

        self.input_manager = input.InputManager(
            controller=controller, action_handlers=self.on_action
        )
        self.input_manager.copy_existing(input_manager_template)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self, walls=walls, gravity_constant=1
        )

    def on_update(self, delta_time: float):
        self.input_manager.update()
        self.change_x = self.input_manager.axis("Move") * 5

        self.physics_engine.update()

    def on_action(self, action: str, state: input.ActionState):
        if (
            action == "Jump"
            and state == input.ActionState.PRESSED
            and self.physics_engine.can_jump()
        ):
            self.change_y = 20


class Game(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Input Example")

        # This is an example of how to load an InputManager from a file. The parse function
        # accepts a dictionary, so anything such as toml, yaml, or json could be used to load
        # that dictionary. As long as it can handle a Python dictionary.
        #
        # with open("out.json", "r") as f:
        #     raw = json.load(f)
        # self.INPUT_TEMPLATE = arcade.InputManager.parse(raw)
        # self.INPUT_TEMPLATE.allow_keyboard = False

        self.INPUT_TEMPLATE = input.InputManager(allow_keyboard=False)
        self.INPUT_TEMPLATE.new_action("Jump")
        self.INPUT_TEMPLATE.add_action_input("Jump", input.Keys.SPACE)
        self.INPUT_TEMPLATE.add_action_input(
            "Jump", input.ControllerButtons.BOTTOM_FACE
        )

        self.INPUT_TEMPLATE.new_axis("Move")
        self.INPUT_TEMPLATE.add_axis_input("Move", input.Keys.A, -1.0)
        self.INPUT_TEMPLATE.add_axis_input("Move", input.Keys.D, 1.0)
        self.INPUT_TEMPLATE.add_axis_input("Move", input.ControllerAxes.LEFT_STICK_X)

        # This is an example of how to dump an InputManager to a file. The serialize function
        # returns a dictionary, so anything such as toml, yaml, or json could be used to save
        # that dictionary. As long as it can handle a Python dictionary.
        #
        # serialized = self.INPUT_TEMPLATE.serialize()
        # with open("out.json", "w") as f:
        #     json.dump(serialized, f)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        self.players: List[Player] = []

        self.controller_manager = pyglet.input.ControllerManager()
        self.controller_manager.set_handlers(self.on_connect, self.on_disconnect)

        controller = None
        if self.controller_manager.get_controllers():
            controller = self.controller_manager.get_controllers()[0]

        self.players.append(Player(self.wall_list, self.INPUT_TEMPLATE, controller))

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.players[0])

    def on_connect(self, controller: pyglet.input.Controller):
        player = Player(self.wall_list, self.INPUT_TEMPLATE, controller)
        self.players.append(player)
        self.player_list.append(player)

    def on_disconnect(self, controller: pyglet.input.Controller):
        to_remove = None
        for player in self.players:
            if player.input_manager.controller == controller:
                to_remove = player
                break

        if to_remove:
            to_remove.input_manager.unbind_controller()
            to_remove.kill()
            self.players.remove(to_remove)

    def on_draw(self):
        self.clear()

        self.player_list.draw()
        self.wall_list.draw()

    def on_key_press(self, key, modifiers):
        key = input.Keys(key)

        if key == input.Keys.KEY_1:
            self.players[0].input_manager.allow_keyboard = True
            for index, player in enumerate(self.players):
                if index != 0:
                    player.input_manager.allow_keyboard = False
        elif key == input.Keys.KEY_2:
            self.players[1].input_manager.allow_keyboard = True
            for index, player in enumerate(self.players):
                if index != 1:
                    player.input_manager.allow_keyboard = False

    def on_update(self, delta_time: float):
        self.player_list.on_update(delta_time)


def main():
    Game()
    arcade.run()


if __name__ == "__main__":
    main()
