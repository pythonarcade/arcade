import arcade
from arcade.experimental import camera_new

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Camera Testing"

class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.camera = camera_new.OrthographicCamera(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        self.camera_speed = 5
        self.camera_change_x = 0
        self.camera_change_y = 0

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            self.camera.zoom(-0.04)
        else:
            self.camera.zoom(0.04)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.camera_change_y = -1
        elif key == arcade.key.DOWN:
            self.camera_change_y = 1
        elif key == arcade.key.LEFT:
            self.camera_change_x = 1
        elif key == arcade.key.RIGHT:
            self.camera_change_x = -1

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.camera_change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.camera_change_x = 0

    def on_draw(self):
        self.camera.scroll(self.camera_change_x * self.camera_speed, self.camera_change_y * self.camera_speed)
        self.camera.use()

        print(self.camera.scale)

        arcade.start_render()
        arcade.draw_rectangle_filled(400, 300, 100, 100, [255, 0, 0], 0)


def main():
    window = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
