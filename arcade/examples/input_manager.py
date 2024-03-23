import pyglet

import arcade


class Game(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Input Example")

        controller_manager = pyglet.input.ControllerManager()
        controller = None
        if controller_manager.get_controllers():
            controller = controller_manager.get_controllers()[0]

        self.input_manager = arcade.InputManager(controller)

        self.input_manager.new_action("Jump")
        self.input_manager.add_action_input("Jump", arcade.Keys.SPACE)
        self.input_manager.add_action_input(
            "Jump", arcade.ControllerButtons.BOTTOM_FACE
        )

        self.input_manager.new_axis("Move")
        self.input_manager.add_axis_input("Move", arcade.Keys.A, -1.0)
        self.input_manager.add_axis_input("Move", arcade.Keys.D, 1.0)
        self.input_manager.add_axis_input(
            "Move", arcade.ControllerButtons.DPAD_LEFT, -1.0
        )
        self.input_manager.add_axis_input(
            "Move", arcade.ControllerButtons.DPAD_RIGHT, 1.0
        )
        self.input_manager.add_axis_input("Move", arcade.ControllerAxes.LEFT_STICK_X)

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        )
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.wall_list, gravity_constant=1
        )

    def on_draw(self):
        self.clear()

        self.player_list.draw()
        self.wall_list.draw()

    def on_update(self, delta_time):
        self.input_manager.update()
        self.player_sprite.change_x = self.input_manager.axis("Move") * 5

        self.physics_engine.update()

    def on_action(self, action: str, state: arcade.ActionState):
        if action == "Jump" and state:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = 20


def main():
    game = Game()
    arcade.run()


if __name__ == "__main__":
    main()
