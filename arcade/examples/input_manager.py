import random
from typing import List, Optional

import pyglet

import arcade

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class Player(arcade.Sprite):

    def __init__(
        self,
        walls: arcade.SpriteList,
        input_manager_template: arcade.InputManager,
        controller: Optional[pyglet.input.Controller] = None,
    ):
        super().__init__(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        )
        self.center_x = random.randint(0, WINDOW_WIDTH)
        self.center_y = 128

        self.input_manager = arcade.InputManager(
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

    def on_action(self, action: str, state: arcade.ActionState):
        if action == "Jump" and self.physics_engine.can_jump():
            self.change_y = 20


class Game(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Input Example")

        self.INPUT_TEMPLATE = arcade.InputManager(allow_keyboard=False)
        self.INPUT_TEMPLATE.new_action("Jump")
        self.INPUT_TEMPLATE.add_action_input("Jump", arcade.Keys.SPACE)
        self.INPUT_TEMPLATE.add_action_input(
            "Jump", arcade.ControllerButtons.BOTTOM_FACE
        )

        self.INPUT_TEMPLATE.new_axis("Move")
        self.INPUT_TEMPLATE.add_axis_input("Move", arcade.Keys.A, -1.0)
        self.INPUT_TEMPLATE.add_axis_input("Move", arcade.Keys.D, 1.0)
        self.INPUT_TEMPLATE.add_axis_input("Move", arcade.ControllerAxes.LEFT_STICK_X)

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
        key = arcade.Keys(key)

        if key == arcade.Keys.KEY_1:
            self.players[0].input_manager.allow_keyboard = True
            for index, player in enumerate(self.players):
                if index != 0:
                    player.input_manager.allow_keyboard = False
        elif key == arcade.Keys.KEY_2:
            self.players[1].input_manager.allow_keyboard = True
            for index, player in enumerate(self.players):
                if index != 1:
                    player.input_manager.allow_keyboard = False

    def on_update(self, delta_time: float):
        self.player_list.on_update(delta_time)


def main():
    game = Game()
    arcade.run()


if __name__ == "__main__":
    main()
