import arcade


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__()


def main():
    app = MyGame()
    app.run()


if __name__ == '__main__':
    main()